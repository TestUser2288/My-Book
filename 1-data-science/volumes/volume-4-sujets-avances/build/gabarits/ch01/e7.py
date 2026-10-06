import sys; sys.path.insert(0,"build")
import numpy as np, torch, torch.nn as nn
from outils_ch01 import *
T=60
def profil(couche, graine_):
    graine(graine_); x=torch.randn(1,T,1,requires_grad=True)
    o,_=couche(x); o[0,-1].sum().backward(); return x.grad[0,:,0].abs().numpy()[::-1]   # indice 0 = dernier pas
for nom,mk in [("rnn",lambda:nn.RNN(1,16,batch_first=True)),("lstm",lambda:nn.LSTM(1,16,batch_first=True)),("gru",lambda:nn.GRU(1,16,batch_first=True))]:
    P=[]
    for s in range(10):
        graine(s); c=mk(); P.append(profil(c,100+s))
    P=np.array(P); m=np.exp(np.log(P+1e-30).mean(0)); print(nom, [f"{m[k]:.1e}" for k in (0,5,10,20,40,59)])
# lstm biais oubli = 1
P=[]
for s in range(10):
    graine(s); c=nn.LSTM(1,16,batch_first=True)
    with torch.no_grad(): c.bias_hh_l0[16:32]+=1.0; c.bias_ih_l0[16:32]+=0
    P.append(profil(c,100+s))
P=np.array(P); m=np.exp(np.log(P+1e-30).mean(0)); print("lstm f=1", [f"{m[k]:.1e}" for k in (0,5,10,20,40,59)])
# pas LSTM à la main
w=dict(i=(0.5,0.3,0.1),f=(0.4,0.2,0.5),g=(0.9,-0.4,0.0),o=(0.7,0.6,-0.1))
x,h0,c0=1.0,0.5,0.2
sg=lambda z:1/(1+np.exp(-z))
i=sg(w['i'][0]*x+w['i'][1]*h0+w['i'][2]); f=sg(w['f'][0]*x+w['f'][1]*h0+w['f'][2]); g=np.tanh(w['g'][0]*x+w['g'][1]*h0+w['g'][2]); o=sg(w['o'][0]*x+w['o'][1]*h0+w['o'][2])
c1=f*c0+i*g; h1=o*np.tanh(c1); print(i,f,g,o,c1,h1)
cell=nn.LSTMCell(1,1)
with torch.no_grad():
    cell.weight_ih[:,0]=torch.tensor([w[k][0] for k in "ifgo"]); cell.weight_hh[:,0]=torch.tensor([w[k][1] for k in "ifgo"]); cell.bias_ih[:]=torch.tensor([w[k][2] for k in "ifgo"]); cell.bias_hh[:]=0
h,c=cell(torch.tensor([[x]]),(torch.tensor([[h0]]),torch.tensor([[c0]]))); print(h.item(),c.item())
