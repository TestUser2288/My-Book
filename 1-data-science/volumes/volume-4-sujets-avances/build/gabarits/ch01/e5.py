import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch, torch.nn as nn, torchvision
from outils_ch01 import *
from sklearn.linear_model import LogisticRegression
# --- transfert : ResNet-18 ImageNet, chiffres MNIST agrandis
xi,yi,xti,yti=charger_mnist()
net=torchvision.models.resnet18(weights=torchvision.models.ResNet18_Weights.IMAGENET1K_V1).eval(); net.fc=nn.Identity()
mean=torch.tensor([0.485,0.456,0.406]).view(1,3,1,1); std=torch.tensor([0.229,0.224,0.225]).view(1,3,1,1)
def feats(x,lot=250):
    out=[]
    with torch.no_grad():
        for i in range(0,len(x),lot):
            b=nn.functional.interpolate(x[i:i+lot],size=64,mode="bilinear").repeat(1,3,1,1); out.append(net((b-mean)/std))
    return torch.cat(out).numpy()
t=time.time(); Fte=feats(xti[:1000]); print("features test",Fte.shape,round(time.time()-t,1),"s")
t=time.time(); Ftr=feats(xi[:2000]); print("features train 2000",round(time.time()-t,1),"s")
for n in [50,200,1000,2000]:
    pix=LogisticRegression(max_iter=500).fit(xi[:n].reshape(n,-1).numpy(),yi[:n].numpy()).score(xti[:1000].reshape(1000,-1).numpy(),yti[:1000].numpy())
    from sklearn.preprocessing import StandardScaler
    sc=StandardScaler().fit(Ftr[:n]); tl=LogisticRegression(max_iter=1000,C=0.1).fit(sc.transform(Ftr[:n]),yi[:n].numpy()).score(sc.transform(Fte),yti[:1000].numpy())
    cn=nn.Sequential(nn.Conv2d(1,8,3),nn.ReLU(),nn.MaxPool2d(2),nn.Conv2d(8,16,3),nn.ReLU(),nn.MaxPool2d(2),nn.Flatten(),nn.Linear(400,10)); graine(0); entrainer(cn,xi[:n],yi[:n],xti[1000:1500],yti[1000:1500],epoques=40,lr=3e-3); sc_=exactitude(cn,xti[:1000],yti[:1000])
    print(f"n={n}: pixels+logit {pix:.3f} | CNN from scratch {sc_:.3f} | ResNet18 features+logit {tl:.3f}")
# --- OCR
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import pytesseract
from rapidfuzz.distance import Levenshtein
font=ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",22)
rng=np.random.default_rng(0)
def facture(i):
    lignes=[f"FACTURE N° 2025-{i:04d}", f"Date : {int(rng.integers(1,28)):02d}/{int(rng.integers(1,13)):02d}/2025", f"Client : Ville {chr(65+int(rng.integers(0,8)))}", f"Article {rng.choice(['A','B','C','D'])}{int(rng.integers(1,9))} x{int(rng.integers(1,4))}   {rng.uniform(5,120):.2f} €", f"TOTAL TTC : {rng.uniform(20,400):.2f} €"]
    im=Image.new("L",(620,200),255); dr=ImageDraw.Draw(im)
    for k,l in enumerate(lignes): dr.text((15,10+36*k),l,font=font,fill=0)
    return im,"\n".join(lignes)
def cer(a,b): return Levenshtein.distance(a,b)/max(1,len(b))
conds={}
def degrade(im,mode):
    if mode=="propre": return im
    if mode=="bruit": a=np.array(im).astype(float)+rng.normal(0,45,(200,620)); return Image.fromarray(np.clip(a,0,255).astype(np.uint8))
    if mode=="rotation": return im.rotate(4,fillcolor=255)
    if mode=="basse résolution": return im.resize((155,50)).resize((620,200))
    if mode=="flou": return im.filter(ImageFilter.GaussianBlur(2.2))
def prep(im): 
    a=np.array(im.filter(ImageFilter.MedianFilter(3))); s=(a>a.mean()*0.8)*255; return Image.fromarray(s.astype(np.uint8)).resize((1240,400))
data=[facture(i) for i in range(1,21)]
for mode in ["propre","bruit","rotation","basse résolution","flou"]:
    r1=[];r2=[]
    for im,txt in data:
        d_=degrade(im,mode)
        r1.append(cer(pytesseract.image_to_string(d_,lang="fra").strip(),txt)); r2.append(cer(pytesseract.image_to_string(prep(d_),lang="fra").strip(),txt))
    print(f"{mode:18s} CER brut {np.mean(r1):.3f} | CER prétraité {np.mean(r2):.3f}")
