import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, torch, torch.nn as nn
from outils_ch01 import *
xtr,ytr,xte,yte=charger_mnist(plat=True); xv,yv=xtr[8000:],ytr[8000:]; xt,yt=xtr[:8000],ytr[:8000]
mk=lambda: nn.Sequential(nn.Linear(784,128),nn.ReLU(),nn.Linear(128,64),nn.ReLU(),nn.Linear(64,10))
for ep,lr in [(25,1e-3),(25,3e-3)]:
    graine(0); m=mk(); t=time.time(); h=entrainer(m,xt,yt,xv,yv,epoques=ep,lr=lr); print("MLP",ep,lr,"val",round(h["acc_val"][-1],4),"max val",round(max(h["acc_val"]),4),"train",round(h["acc_train"][-1],4),"test",round(exactitude(m,xte,yte),4),round(time.time()-t,1),"s")
# optimiseurs
res={}
for nom,f in [("SGD",lambda p:torch.optim.SGD(p,lr=0.05)),("SGD+moment",lambda p:torch.optim.SGD(p,lr=0.05,momentum=0.9)),("Adam",lambda p:torch.optim.Adam(p,lr=1e-3))]:
    graine(0); m=mk(); h=entrainer(m,xt,yt,xv,yv,epoques=10,optimiseur=f); res[nom]=h; print(nom,[round(a,3) for a in h["perte"][:10:3]],"val",round(h["acc_val"][-1],4))
# surapprentissage : 1000 images
x1,y1=xtr[:1000],ytr[:1000]; xv2,yv2=xtr[2000:8000],ytr[2000:8000]
big=lambda p=0.0: nn.Sequential(nn.Linear(784,512),nn.ReLU(),nn.Dropout(p),nn.Linear(512,512),nn.ReLU(),nn.Dropout(p),nn.Linear(512,10))
for nom,kw,p in [("sans régul.",{},0.0),("weight decay 1e-2",{"wd":1e-2},0.0),("dropout 0.5",{},0.5),("arrêt précoce",{"patience":5},0.0)]:
    graine(0); m=big(p); h=entrainer(m,x1,y1,xv2,yv2,epoques=60,lr=1e-3,**kw); print(nom,"train",round(h["acc_train"][-1],3),"val",round(h["acc_val"][-1],4),"max val",round(max(h["acc_val"]),4),"ep",len(h["acc_val"]),h.get("meilleure_epoque"))
# gradients qui disparaissent
def profil(act,L=10,w=128,seed=0):
    torch.manual_seed(seed); layers=[]
    for i in range(L): layers+= [nn.Linear(w if i else 20,w), act()]
    m=nn.Sequential(*layers,nn.Linear(w,1)); x=torch.randn(64,20); m(x).pow(2).mean().backward()
    return [m[2*i].weight.grad.norm().item() for i in range(L)]
for nom,a in [("sigmoid",nn.Sigmoid),("tanh",nn.Tanh),("relu",nn.ReLU)]:
    g=profil(a); print(nom,[f"{v:.1e}" for v in g[::3]],"rapport couche1/couche10",f"{g[0]/g[-1]:.1e}")
