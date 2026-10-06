import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch, torch.nn as nn
from outils_ch01 import *
d=pd.read_csv("donnees/ventes_quotidiennes.csv",parse_dates=["date"]); d["ly"]=np.log(d.ventes)
tr=d[d.date<"2025-01-01"].index; te=d[d.date>="2025-01-01"].index
print(len(tr),len(te))
mae=lambda a,b: float(np.mean(np.abs(a-b))); mape=lambda a,b: float(np.mean(np.abs(a-b)/a)*100)
y=d.ventes.values
# repères
sn7=d.ventes.shift(7).values[te]; print("naïf saisonnier 7j: MAE",round(mae(y[te],sn7),2),"MAPE",round(mape(y[te],sn7),2))
sn364=d.ventes.shift(364).values[te]; print("naïf 364j",round(mae(y[te],sn364),2))
# LGBM lags
import lightgbm as lgb
F=pd.DataFrame({f"lag{k}":d.ly.shift(k) for k in list(range(1,15))+[21,28,364]}); F["dow"]=d.jour_semaine; F["promo"]=d.promo; F["mois"]=d.mois; F["doy"]=d.date.dt.dayofyear
ok=F.notna().all(axis=1); itr=[i for i in tr if ok[i]]
g=lgb.LGBMRegressor(n_estimators=300,learning_rate=0.05,num_leaves=15,n_jobs=2,verbose=-1,random_state=0).fit(F.loc[itr],d.ly[itr]); p=np.exp(g.predict(F.loc[te])); print("LGBM lags: MAE",round(mae(y[te],p),2),"MAPE",round(mape(y[te],p),2))
from sklearn.linear_model import Ridge
r=Ridge(1.0).fit(pd.get_dummies(F.loc[itr],columns=["dow","mois"]).astype(float),d.ly[itr]); pr=np.exp(r.predict(pd.get_dummies(F.loc[te],columns=["dow","mois"]).astype(float).reindex(columns=pd.get_dummies(F.loc[itr],columns=["dow","mois"]).columns,fill_value=0))); print("Ridge lags: MAE",round(mae(y[te],pr),2),"MAPE",round(mape(y[te],pr),2))
# LSTM : fenêtre 28 jours (log ventes standardisé + promo), cible jour suivant ; features calendrier du jour cible
mu,sd=d.ly[tr].mean(),d.ly[tr].std(); z=((d.ly-mu)/sd).values; promo=d.promo.values.astype(float); dow=np.eye(7)[d.jour_semaine.values]
W=28
def fen(idx):
    X=np.stack([np.column_stack([z[i-W:i],promo[i-W:i]]) for i in idx]); C=np.column_stack([promo[idx],dow[idx],np.sin(2*np.pi*d.date.dt.dayofyear.values[idx]/365),np.cos(2*np.pi*d.date.dt.dayofyear.values[idx]/365)]); return torch.tensor(X,dtype=torch.float32),torch.tensor(C,dtype=torch.float32),torch.tensor(z[idx],dtype=torch.float32)
itr2=[i for i in tr if i>=W]; Xtr,Ctr,ytr=fen(itr2); Xte,Cte,yte=fen(list(te))
class Net(nn.Module):
    def __init__(s,h=16):
        super().__init__(); s.l=nn.LSTM(2,h,batch_first=True); s.f=nn.Sequential(nn.Linear(h+10,16),nn.ReLU(),nn.Linear(16,1))
    def forward(s,x,c): o,_=s.l(x); return s.f(torch.cat([o[:,-1],c],1)).squeeze(1)
res=[]
for seed in range(3):
    graine(seed); net=Net(); opt=torch.optim.Adam(net.parameters(),2e-3); t=time.time()
    for e in range(40):
        net.train(); perm=torch.randperm(len(Xtr))
        for i in range(0,len(Xtr),64):
            idx=perm[i:i+64]; opt.zero_grad(); l=nn.functional.mse_loss(net(Xtr[idx],Ctr[idx]),ytr[idx]); l.backward(); opt.step()
    net.eval(); 
    with torch.no_grad(): pl=np.exp(net(Xte,Cte).numpy()*sd+mu)
    res.append((mae(y[te],pl),mape(y[te],pl))); print("LSTM seed",seed,"MAE",round(res[-1][0],2),"MAPE",round(res[-1][1],2),round(time.time()-t,1),"s")
print("LSTM moyenne MAE",round(np.mean([r[0] for r in res]),2),"sd",round(np.std([r[0] for r in res]),2))
print("niveau moyen des ventes test",round(y[te].mean(),1))
