import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, torch, torch.nn as nn
from outils_ch01 import *
xi,yi,xti,yti=charger_mnist(); xv,yv=xi[8000:],yi[8000:]; xt,yt=xi[:8000],yi[:8000]
cnn=lambda: nn.Sequential(nn.Conv2d(1,8,3),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(8,16,3),nn.ReLU(),nn.MaxPool2d(2),nn.Flatten(),nn.Linear(16*5*5,10))
graine(0); m=cnn(); t=time.time(); h=entrainer(m,xt,yt,xv,yv,epoques=6,lr=3e-3); print("CNN params",nb_parametres(m),"val",[round(a,3) for a in h["acc_val"]],"test",round(exactitude(m,xti,yti),4),round(time.time()-t,1),"s")
mlp=lambda: nn.Sequential(nn.Flatten(),nn.Linear(784,128),nn.ReLU(),nn.Linear(128,64),nn.ReLU(),nn.Linear(64,10))
graine(0); mm=mlp(); h2=entrainer(mm,xt,yt,xv,yv,epoques=25,lr=3e-3); print("MLP params",nb_parametres(mm),"test",round(exactitude(mm,xti,yti),4))
# décalages
def shift(x,dx):
    return torch.roll(x,shifts=dx,dims=3)
for dx in [0,1,2,3,4]:
    print("décalage",dx,"CNN",round(exactitude(m,shift(xti,dx),yti),4),"MLP",round(exactitude(mm,shift(xti,dx),yti),4))
# augmentation : décalages aléatoires dans [-3,3]
def aug(x):
    out=x.clone()
    for i in range(len(x)):
        out[i]=torch.roll(x[i],shifts=(int(torch.randint(-3,4,(1,))),int(torch.randint(-3,4,(1,)))),dims=(1,2))
    return out
torch.manual_seed(1); xa=torch.cat([xt,aug(xt),aug(xt)]); ya=torch.cat([yt,yt,yt])
graine(0); ma=mlp(); entrainer(ma,xa,ya,xv,yv,epoques=15,lr=3e-3); print("MLP augmenté: test",round(exactitude(ma,xti,yti),4),"décalé 3:",round(exactitude(ma,shift(xti,3),yti),4))
graine(0); mca=cnn(); entrainer(mca,xa,ya,xv,yv,epoques=6,lr=3e-3); print("CNN augmenté: test",round(exactitude(mca,xti,yti),4),"décalé 3:",round(exactitude(mca,shift(xti,3),yti),4))
# formes
x=xti[:1]; 
for l in m: x=l(x); print(type(l).__name__,tuple(x.shape),sum(p.numel() for p in l.parameters()))
print("filtres", m[0].weight.shape)
