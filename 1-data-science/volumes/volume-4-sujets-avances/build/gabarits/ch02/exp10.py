import sys, time, warnings, math; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch, torch.nn as nn, torch.nn.functional as F
import outils_ch02 as O
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
torch.set_num_threads(2)
a=O.etiqueter_tranches(O.charger_avis()); d=O.polarite(a); tr,te=train_test_split(d,test_size=0.25,random_state=0,stratify=d["y"])
st=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
tk=st.tokenizer; enc=st[0].auto_model
class LoRA(nn.Module):
    def __init__(s, base, r=8, alpha=16):
        super().__init__(); s.base=base; s.A=nn.Parameter(torch.randn(r, base.in_features)*0.01); s.B=nn.Parameter(torch.zeros(base.out_features, r)); s.scale=alpha/r
    def forward(s,x): return s.base(x)+(x@s.A.T@s.B.T)*s.scale
torch.manual_seed(0)
for p in enc.parameters(): p.requires_grad=False
for layer in enc.encoder.layer:
    layer.attention.self.query=LoRA(layer.attention.self.query); layer.attention.self.value=LoRA(layer.attention.self.value)
head=nn.Linear(384,2)
def embed(texts):
    b=tk(texts,padding=True,truncation=True,max_length=64,return_tensors="pt"); h=enc(**b).last_hidden_state; m=b["attention_mask"].unsqueeze(-1).float(); return (h*m).sum(1)/m.sum(1)
params=[p for p in enc.parameters() if p.requires_grad]+list(head.parameters()); print("trainable",sum(p.numel() for p in params),"total",sum(p.numel() for p in enc.parameters()))
sub=tr.sample(1000,random_state=0); opt=torch.optim.AdamW(params,lr=1e-3)
t0=time.time()
for ep in range(2):
    perm=np.random.default_rng(ep).permutation(len(sub))
    for k in range(0,len(sub),32):
        ix=perm[k:k+32]; loss=F.cross_entropy(head(embed(sub.texte.iloc[ix].tolist())),torch.tensor(sub.y.iloc[ix].values)); opt.zero_grad(); loss.backward(); opt.step()
    print(ep,loss.item(),round(time.time()-t0))
def pred(texts):
    out=[]
    with torch.no_grad():
        for k in range(0,len(texts),128): out.append(head(embed(texts[k:k+128])).argmax(-1).numpy())
    return np.concatenate(out)
t0=time.time(); pt=pred(te.texte.tolist()); ps=pred(O.SONDES); print("test",(pt==te.y.values).mean(),"probes",(ps==O.Y_SONDES).mean(),round(time.time()-t0))
