import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd
import outils_ch02 as O
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
a=O.etiqueter_tranches(O.charger_avis()); print(a.columns.tolist(), a.index[:3])
st=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
E=st.encode(a.texte.tolist(),batch_size=128,normalize_embeddings=True); np.save("/home/ubuntu/.claude/jobs/5b7143f8/tmp/v4c2/Eall.npy",E)
tf=TfidfVectorizer(min_df=2); X=tf.fit_transform(a.texte)
res=[]
for sj,qs in O.REQUETES.items():
    pert=set(np.where((a.sujet==sj)&(a.note<=2))[0])
    for q in qs:
        qe=st.encode([q],normalize_embeddings=True)[0]
        c1=np.argsort(-(E@qe)); c2=np.argsort(-(X@tf.transform([q]).T).toarray()[:,0])
        res.append((sj,q,len(pert),O.precision_au_rang(c2,pert,5),O.precision_au_rang(c1,pert,5)))
r=pd.DataFrame(res,columns=["sujet","q","npert","tfidf","minilm"]); print(r.to_string()); print(r[["tfidf","minilm"]].mean())
print(a.sujet.value_counts().to_dict(), (a.note<=2).mean())
