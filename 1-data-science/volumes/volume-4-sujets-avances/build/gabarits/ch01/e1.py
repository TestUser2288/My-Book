import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, torch, torch.nn as nn
from outils_ch01 import *
graine(0)
# --- exemple à la main : réseau 2-2-1, sigmoïdes, entropie croisée
x=np.array([1.0,2.0]); W1=np.array([[0.1,0.3],[0.2,-0.1]]); b1=np.array([0.0,0.1]); W2=np.array([0.4,-0.2]); b2=0.05; y=1.0
sig=lambda z:1/(1+np.exp(-z))
z1=W1@x+b1; a1=sig(z1); z2=W2@a1+b2; a2=sig(z2); L=-(y*np.log(a2)+(1-y)*np.log(1-a2))
d2=a2-y; gW2=d2*a1; gb2=d2; d1=(W2*d2)*a1*(1-a1); gW1=np.outer(d1,x); gb1=d1
print("z1",z1,"a1",a1,"z2",z2,"a2",a2,"L",L); print("d2",d2,"gW2",gW2,"d1",d1,"gW1",gW1)
eta=0.5; print("W2'",W2-eta*gW2,"W1'",W1-eta*gW1, "b2'", b2-eta*gb2, "b1'", b1-eta*gb1)
z1n=(W1-eta*gW1)@x+(b1-eta*gb1); a1n=sig(z1n); a2n=sig((W2-eta*gW2)@a1n+b2-eta*gb2); print("nouvelle sortie",a2n,"nouvelle perte",-np.log(a2n))
# --- MLP MNIST
xtr,ytr,xte,yte=charger_mnist(plat=True)
xv,yv=xtr[8000:],ytr[8000:]; xt,yt=xtr[:8000],ytr[:8000]
t=time.time()
m=nn.Sequential(nn.Linear(784,128),nn.ReLU(),nn.Linear(128,64),nn.ReLU(),nn.Linear(64,10)); h=entrainer(m,xt,yt,xv,yv,epoques=8)
print("MLP params",nb_parametres(m),"acc val",h["acc_val"][-1],"test",exactitude(m,xte,yte),round(time.time()-t,1),"s"); print([round(a,3) for a in h["acc_val"]])
# baselines
from sklearn.linear_model import LogisticRegression
t=time.time(); lr=LogisticRegression(max_iter=300).fit(xt.numpy(),yt.numpy()); print("logit test",round(lr.score(xte.numpy(),yte.numpy()),4),round(time.time()-t,1),"s")
import lightgbm as lgb
t=time.time(); g=lgb.LGBMClassifier(n_estimators=100,num_leaves=31,n_jobs=2,verbose=-1,random_state=0).fit(xt.numpy(),yt.numpy()); print("lgbm test",round(g.score(xte.numpy(),yte.numpy()),4),round(time.time()-t,1),"s")
