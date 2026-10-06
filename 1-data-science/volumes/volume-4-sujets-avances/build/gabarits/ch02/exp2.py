import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch
import outils_ch02 as O
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sentence_transformers import SentenceTransformer
a=O.etiqueter_tranches(O.charger_avis()); d=O.polarite(a)
tr,te=train_test_split(d,test_size=0.25,random_state=0,stratify=d.y)
res={}
v=TfidfVectorizer(ngram_range=(1,2),min_df=2); m=LogisticRegression(max_iter=3000,C=3).fit(v.fit_transform(tr.texte),tr.y)
res["tfidf"]=(m.score(v.transform(te.texte),te.y), ((m.predict_proba(v.transform(O.SONDES))[:,1]>0.5)==O.Y_SONDES).mean())
st=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
t=time.time(); Etr=st.encode(tr.texte.tolist(),batch_size=128,normalize_embeddings=True); Ete=st.encode(te.texte.tolist(),batch_size=128,normalize_embeddings=True); Es=st.encode(O.SONDES,normalize_embeddings=True); print("encode",round(time.time()-t,1),"s")
lr=LogisticRegression(max_iter=3000,C=10).fit(Etr,tr.y); res["minilm+logit"]=(lr.score(Ete,te.y), ((lr.predict_proba(Es)[:,1]>0.5)==O.Y_SONDES).mean())
voc=O.Vocabulaire(tr.texte.tolist(),min_freq=2); print("vocab",len(voc))
t=time.time(); mt=O.entrainer_classifieur(tr.texte.tolist(),tr.y.values,voc,epoques=8); print("transformer train",round(time.time()-t,1),"s", sum(p.numel() for p in mt.parameters()))
pt=O.predire_classe(mt,voc,te.texte.tolist()); ps=O.predire_classe(mt,voc,O.SONDES); res["transformer"]=(((pt>0.5)==te.y.values).mean(), ((ps>0.5)==O.Y_SONDES).mean())
print({k:(round(a_,3),round(b_,3)) for k,(a_,b_) in res.items()})
# par tranche sonde: erreurs
for nom,p in [("tfidf",m.predict_proba(v.transform(O.SONDES))[:,1]),("minilm",lr.predict_proba(Es)[:,1]),("transf",ps)]:
    err=[O.SONDES[i] for i in range(len(O.SONDES)) if (p[i]>0.5)!=O.Y_SONDES[i]]; print(nom,len(err),"erreurs sur 48 ;",err[:4])
np.save("/home/ubuntu/.claude/jobs/5b7143f8/tmp/v4c2/E_tr.npy",Etr)
