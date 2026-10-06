import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch
import outils_ch02 as O
f,c=O.fusions_bpe({"rapide":5,"rapides":2,"rapidement":3,"lent":4,"lente":2},9); print(f)
from transformers import AutoTokenizer, AutoModelForCausalLM
rep="HuggingFaceTB/SmolLM2-135M-Instruct"; tok=AutoTokenizer.from_pretrained(rep); m=AutoModelForCausalLM.from_pretrained(rep,dtype=torch.float32).eval()
def logp(prompt, suite):
    ids=tok(prompt+suite,return_tensors="pt").input_ids; n0=len(tok(prompt).input_ids)
    with torch.no_grad(): lg=torch.log_softmax(m(ids).logits[0],-1)
    return float(sum(lg[i-1,ids[0,i]] for i in range(n0,ids.shape[1])))
def zero(t): return f"Avis : {t}\nSentiment (positif ou négatif) :"
ex=[("Livraison très rapide, produit parfait.","positif"),("Colis abîmé, service client absent.","négatif"),("Super qualité, je recommande.","positif"),("Je ne rachèterai jamais, très déçu.","négatif")]
def few(t): return "".join(f"Avis : {a}\nSentiment : {b}\n\n" for a,b in ex)+f"Avis : {t}\nSentiment :"
for nom,fp in [("zero",lambda t:zero(t)),("few",few)]:
    t0=time.time(); pred=[]
    for t in O.SONDES:
        pr=fp(t); pred.append(int(logp(pr," positif")>logp(pr," négatif")))
    pred=np.array(pred); print(nom,"acc",round((pred==O.Y_SONDES).mean(),3),"part positif",round(pred.mean(),2),round(time.time()-t0,1),"s")
