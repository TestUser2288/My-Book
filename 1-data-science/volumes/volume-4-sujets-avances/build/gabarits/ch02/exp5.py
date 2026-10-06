import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch
import outils_ch02 as O
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.cluster import KMeans
from sklearn.metrics import adjusted_rand_score
f,c=O.fusions_bpe({"rapide":5,"rapides":2,"rapidement":3,"lent":4,"lente":2},6); print(f); print(c)
a=O.charger_avis(); a=a[a.texte.str.split().str.len()>3].reset_index(drop=True)
sub=a.sample(1500,random_state=0).reset_index(drop=True)
tf=TfidfVectorizer(min_df=3); X=tf.fit_transform(sub.texte); nmf=NMF(5,random_state=0,init="nndsvd",max_iter=400).fit(X); mots=np.array(tf.get_feature_names_out())
for k,comp in enumerate(nmf.components_): print("NMF",k,list(mots[np.argsort(-comp)[:6]]))
W=nmf.transform(X); lab=W.argmax(1); print("ARI NMF vs sujet",round(adjusted_rand_score(sub.sujet,lab),3))
print(pd.crosstab(lab,sub.sujet).values.tolist())
cv=CountVectorizer(min_df=3); Xc=cv.fit_transform(sub.texte); lda=LatentDirichletAllocation(5,random_state=0,max_iter=15).fit(Xc); mc=np.array(cv.get_feature_names_out())
for k,comp in enumerate(lda.components_): print("LDA",k,list(mc[np.argsort(-comp)[:6]]))
print("ARI LDA",round(adjusted_rand_score(sub.sujet,lda.transform(Xc).argmax(1)),3))
from sentence_transformers import SentenceTransformer
st=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
t=time.time(); E=st.encode(sub.texte.tolist(),batch_size=128,normalize_embeddings=True); print("encode 1500",round(time.time()-t,1))
km=KMeans(5,n_init=10,random_state=0).fit(E); print("ARI kmeans embeddings vs sujet",round(adjusted_rand_score(sub.sujet,km.labels_),3))
q=["Le colis est arrivé très en retard","Le produit est cassé","C'est trop cher","Le service client ne répond pas"]
Q=st.encode(q,normalize_embeddings=True)
for i,qq in enumerate(q):
    s=E@Q[i]; top=np.argsort(-s)[:3]; print(qq,"->",[(sub.sujet[j],sub.note[j],sub.texte[j][:60]) for j in top])
# évaluation de la recherche : requêtes = 5 sujets x négatif ; pertinents = même sujet & note<=2
req={"livraison":"Le colis est arrivé en retard","qualite":"Le produit est abîmé et de mauvaise qualité","prix":"C'est beaucoup trop cher","service":"Le service client ne répond jamais","emballage":"L'emballage était déchiré"}
Qe=st.encode(list(req.values()),normalize_embeddings=True)
for nom,scoref in [("minilm",lambda i:E@Qe[i]),("tfidf",lambda i:(tf.transform([list(req.values())[i]])@X.T).toarray()[0])]:
    ps=[]
    for i,(sj,_) in enumerate(req.items()):
        pert=set(np.where((sub.sujet==sj)&(sub.note<=2))[0]); cl=np.argsort(-scoref(i)); ps.append(O.precision_au_rang(cl,pert,5))
    print(nom,"precision@5 par sujet",[round(x,2) for x in ps],"moy",round(np.mean(ps),3))
# RAG
from transformers import AutoTokenizer, AutoModelForCausalLM
rep="HuggingFaceTB/SmolLM2-135M-Instruct"; tok=AutoTokenizer.from_pretrained(rep); m=AutoModelForCausalLM.from_pretrained(rep,dtype=torch.float32).eval()
question="Quels problèmes les clients rencontrent-ils avec la livraison ?"
qe=st.encode([question],normalize_embeddings=True)[0]; top=np.argsort(-(E@qe))[:3]; ctx=[sub.texte[j] for j in top]; print("CTX",ctx)
prompt="Réponds en français à la question en t'appuyant uniquement sur les avis suivants.\n\nAvis :\n"+"\n".join("- "+c for c in ctx)+f"\n\nQuestion : {question}"
enc=tok.apply_chat_template([{"role":"user","content":prompt}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
with torch.no_grad(): out=m.generate(**enc,max_new_tokens=80,do_sample=False,repetition_penalty=1.2)
print("RAG:",repr(tok.decode(out[0,enc.input_ids.shape[1]:],skip_special_tokens=True)))
for pr in ["What is the price of product A in our shop?","Donne le prix du produit A.\nRéponse :"]:
    enc=tok.apply_chat_template([{"role":"user","content":pr}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
    torch.manual_seed(0)
    with torch.no_grad(): out=m.generate(**enc,max_new_tokens=40,do_sample=True,temperature=0.7,top_p=0.9)
    print("HAL:",repr(tok.decode(out[0,enc.input_ids.shape[1]:],skip_special_tokens=True)))
