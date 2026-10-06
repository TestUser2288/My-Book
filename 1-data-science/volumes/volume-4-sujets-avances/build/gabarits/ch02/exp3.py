import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch
import outils_ch02 as O
a=O.charger_avis()
t=time.time(); voc,E,pertes=O.entrainer_word2vec(a.texte.tolist(),dim=32,epoques=5); print("w2v",round(time.time()-t,1),"s",len(voc),[round(x,3) for x in pertes])
for w in ["livraison","rapide","lente","prix","déçu","cher","excellent","emballage"]:
    if w in voc.stoi: print(w,[(x,round(s,2)) for x,s in O.voisins(voc,E,w,5)])
for p in [("rapide","lente"),("rapide","rapidement"),("cher","raisonnable"),("livraison","colis")]:
    if all(x in voc.stoi for x in p): print(p, round(O.cosinus(voc,E,*p),2))
En=E/np.linalg.norm(E,axis=1,keepdims=True)
# analogie
def ana(a_,b_,c_,k=3):
    v=En[voc.stoi[b_]]-En[voc.stoi[a_]]+En[voc.stoi[c_]]; s=En@v; s[:4]=-9
    for w in (a_,b_,c_): s[voc.stoi[w]]=-9
    return [voc.itos[i] for i in np.argsort(-s)[:k]]
print("analogie", ana("rapide","lente","bon") if "lente" in voc.stoi else "-")
# LM
voc2=O.Vocabulaire(a.texte.tolist(),min_freq=2); print("vocab LM",len(voc2))
t=time.time(); lm,pl=O.entrainer_langage(a.texte.tolist(),voc2,epoques=8); print("LM train",round(time.time()-t,1),"s",[round(x,2) for x in pl], "ppl",round(np.exp(pl[-1]),1), "params",sum(p.numel() for p in lm.parameters()))
for T in (0.3,1.0,1.5):
    print("T",T,"|",O.generer(lm,voc2,"la livraison",n=18,temperature=T,graine=1))
print("topk3",O.generer(lm,voc2,"le produit",n=18,temperature=1.0,top_k=3,graine=2))
