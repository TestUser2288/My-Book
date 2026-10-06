import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch, torch.nn as nn
from outils_ch01 import *
from sklearn.model_selection import RepeatedStratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import StandardScaler
c=pd.read_csv("donnees/clients_ml.csv"); y=c.churn_90j.values
cats=["ville","canal_acquisition","appareil","categorie_preferee"]; nums=[k for k in c.columns if k not in cats+["id_client","churn_90j","depense_6m","segment_vrai","commandes_apres_cible"]]
codes={k:pd.Categorical(c[k].fillna("manquant")).codes for k in cats}; nbmod={k:len(pd.Categorical(c[k].fillna("manquant")).categories) for k in cats}
N=c[nums].copy(); manq=N.isna().astype(float).loc[:,N.isna().any()].add_suffix("_manq")
class Tab(nn.Module):
    def __init__(s,nb_num):
        super().__init__(); s.emb=nn.ModuleList([nn.Embedding(nbmod[k],min(8,nbmod[k])) for k in cats]); d=sum(min(8,nbmod[k]) for k in cats)+nb_num
        s.f=nn.Sequential(nn.Linear(d,64),nn.ReLU(),nn.Dropout(0.2),nn.Linear(64,32),nn.ReLU(),nn.Linear(32,1))
    def forward(s,xn,xc): return s.f(torch.cat([e(xc[:,i]) for i,e in enumerate(s.emb)]+[xn],1)).squeeze(1)
def prep(tr,te):
    med=N.iloc[tr].median(); A=N.fillna(med); sc=StandardScaler().fit(A.iloc[tr]); Z=np.column_stack([sc.transform(A),manq.values]).astype(np.float32)
    C=np.column_stack([codes[k] for k in cats]).astype(np.int64); return Z,C
cv=RepeatedStratifiedKFold(n_splits=5,n_repeats=2,random_state=0); res=[]
t0=time.time()
for k,(tr,te) in enumerate(cv.split(c,y)):
    Z,C=prep(tr,te); graine(k); m=Tab(Z.shape[1]); opt=torch.optim.Adam(m.parameters(),2e-3,weight_decay=1e-4)
    Zt,Ct,yt=torch.tensor(Z[tr]),torch.tensor(C[tr]),torch.tensor(y[tr],dtype=torch.float32)
    for e in range(25):
        m.train(); perm=torch.randperm(len(tr))
        for i in range(0,len(tr),256):
            idx=perm[i:i+256]; opt.zero_grad(); nn.functional.binary_cross_entropy_with_logits(m(Zt[idx],Ct[idx]),yt[idx]).backward(); opt.step()
    m.eval()
    with torch.no_grad(): pm=torch.sigmoid(m(torch.tensor(Z[te]),torch.tensor(C[te]))).numpy()
    X=pd.concat([N,manq],axis=1).assign(**{kk:codes[kk] for kk in cats})
    hg=HistGradientBoostingClassifier(random_state=0,categorical_features=[X.columns.get_loc(kk) for kk in cats]).fit(X.iloc[tr],y[tr]); ph=hg.predict_proba(X.iloc[te])[:,1]
    D=pd.get_dummies(c[cats].fillna("manquant"),dtype=float); XL=np.column_stack([StandardScaler().fit(N.fillna(N.iloc[tr].median()).iloc[tr]).transform(N.fillna(N.iloc[tr].median())),manq.values,D.values])
    pl=LogisticRegression(max_iter=2000).fit(XL[tr],y[tr]).predict_proba(XL[te])[:,1]
    res.append((roc_auc_score(y[te],pl),roc_auc_score(y[te],pm),roc_auc_score(y[te],ph)))
print("temps",round(time.time()-t0,1),"s")
r=np.array(res); print("AUC logit/MLP/HGB moyennes",r.mean(0).round(4),"sd",r.std(0,ddof=1).round(4))
def diff(a,b,ratio=0.25):
    d=a-b; k=len(d); t=d.mean()/np.sqrt((1/k+ratio)*d.var(ddof=1)); from scipy import stats; return d.mean(),2*stats.t.sf(abs(t),k-1)
print("HGB-MLP",diff(r[:,2],r[:,1]),"HGB-logit",diff(r[:,2],r[:,0]),"MLP-logit",diff(r[:,1],r[:,0]))
