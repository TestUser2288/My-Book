import sys, time, warnings, unicodedata; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch
import outils_ch02 as O
from transformers import AutoTokenizer, AutoModelForCausalLM
rep="HuggingFaceTB/SmolLM2-135M-Instruct"; tok=AutoTokenizer.from_pretrained(rep); m=AutoModelForCausalLM.from_pretrained(rep,dtype=torch.float32).eval()
fr=["La livraison a été très rapide et le colis était bien emballé.","Je recommande ce produit à tous mes amis.","Le service client a répondu en quelques minutes.","Le prix est raisonnable pour une qualité aussi soignée.","Nous sommes très satisfaits de notre commande."]
en=["Delivery was very fast and the parcel was well packed.","I recommend this product to all my friends.","The customer service answered within minutes.","The price is reasonable for such careful quality.","We are very satisfied with our order."]
nf=[len(tok(s).input_ids) for s in fr]; ne=[len(tok(s).input_ids) for s in en]; wf=[len(s.split()) for s in fr]; we=[len(s.split()) for s in en]
print("tokens fr",nf,"en",ne,"par mot fr %.2f en %.2f"%(sum(nf)/sum(wf),sum(ne)/sum(we)), "ratio", round(sum(nf)/sum(ne),2))
print(tok.convert_ids_to_tokens(tok("La livraison a été très rapide.").input_ids))
print(tok.convert_ids_to_tokens(tok("Anticonstitutionnellement").input_ids))
print("vocab",tok.vocab_size)
# prochain jeton
ids=tok("La livraison a été très",return_tensors="pt").input_ids
with torch.no_grad(): lg=m(ids).logits[0,-1]
p=torch.softmax(lg,-1); top=torch.topk(p,8); print([(tok.decode(i),round(float(v),3)) for v,i in zip(top.values,top.indices)], "H(bits)=",round(O.entropie(p.numpy()),2))
pl=lg.numpy()
for T in (0.2,0.7,1.0,1.5,2.5):
    q=O.decoder_probas(pl,temperature=T); print("T",T,"H",round(O.entropie(q),2),"p_max",round(q.max(),3),"nb(p>1%)",int((q>0.01).sum()))
for k in (1,5,50): q=O.decoder_probas(pl,top_k=k); print("top_k",k,"support",int((q>0).sum()))
for pp in (0.5,0.9,0.99): q=O.decoder_probas(pl,top_p=pp); print("top_p",pp,"support",int((q>0).sum()))
# génération sous contraintes, gloutonne
msgs=[{"role":"user","content":"Écris une phrase pour remercier un client qui a laissé un avis positif."}]
enc=tok.apply_chat_template(msgs,add_generation_prompt=True,return_tensors="pt",return_dict=True)
print(repr(tok.apply_chat_template(msgs,add_generation_prompt=True,tokenize=False)))
with torch.no_grad(): out=m.generate(**enc,max_new_tokens=40,do_sample=False)
print("GREEDY:",repr(tok.decode(out[0,enc.input_ids.shape[1]:],skip_special_tokens=True)))
msgs=[{"role":"user","content":"Quel est le prix du produit A dans notre boutique ?"}]
enc=tok.apply_chat_template(msgs,add_generation_prompt=True,return_tensors="pt",return_dict=True)
with torch.no_grad(): out=m.generate(**enc,max_new_tokens=50,do_sample=False)
print("HALLU:",repr(tok.decode(out[0,enc.input_ids.shape[1]:],skip_special_tokens=True)))
# Arabe
ar_mots={"livre":"كتاب","le livre":"الكتاب","et leurs livres":"وكتبهم"}
for k,v in ar_mots.items(): print(k,"len",len(v),"jetons SmolLM",len(tok(v).input_ids),[hex(ord(c)) for c in v][:3])
phr="التوصيل كان سريعا"
print("phrase ar: caractères",len(phr),"mots",len(phr.split()),"jetons",len(tok(phr).input_ids))
dia="كَتَبَ"; print("diacritiques",len(dia), len("".join(c for c in dia if not unicodedata.category(c)=="Mn")), [unicodedata.name(c) for c in dia][:3])
# LoRA
cfg=m.config; print("hidden",cfg.hidden_size,"couches",cfg.num_hidden_layers,"inter",cfg.intermediate_size,"tetes",cfg.num_attention_heads,"kv",cfg.num_key_value_heads,"vocab",cfg.vocab_size)
tot=sum(p.numel() for p in m.parameters()); print("params",tot)
d=cfg.hidden_size; r=8; print("LoRA par matrice d x d: ",2*d*r,"contre",d*d,"ratio",round(2*d*r/(d*d),4))
# BPE
mots={"rapide":5,"rapides":2,"rapidement":3,"lent":4,"lente":2,"lentement":3}
f,c=O.fusions_bpe(mots,6); print(f); print(c)
