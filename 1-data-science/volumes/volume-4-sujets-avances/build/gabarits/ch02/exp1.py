import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd
import outils_ch02 as O
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
a=O.etiqueter_tranches(O.charger_avis()); d=O.polarite(a)
print(len(a),len(d), d.y.mean().round(3))
print({c:int(d[c].sum()) for c in ["niee","anglais","mixte","court","inedite"]})
tr,te=train_test_split(d,test_size=0.25,random_state=0,stratify=d.y)
def ev(nom,ngr,tr,te):
    v=TfidfVectorizer(ngram_range=ngr,min_df=2); m=LogisticRegression(max_iter=3000,C=3).fit(v.fit_transform(tr.texte),tr.y)
    p=m.predict_proba(v.transform(te.texte))[:,1]; ok=pd.Series((p>0.5)==te.y.values,index=te.index)
    r={"global":ok.mean()}
    for c in ["niee","anglais","mixte","court","inedite"]: r[c]=(ok[te[c]].mean(), int(te[c].sum()))
    print(nom, {k:(round(v_,3) if not isinstance(v_,tuple) else (round(v_[0],3),v_[1])) for k,v_ in r.items()})
ev("tfidf 1-gram",(1,1),tr,te); ev("tfidf 1-2gram",(1,2),tr,te)
# généralisation : entraîner sans les phrases réservées, tester dessus
d2=d.copy(); trg=d2[~d2.inedite]; teg=d2[d2.inedite]; print("train sans inédites",len(trg),"test inédites",len(teg))
for ng in [(1,1),(1,2)]:
    v=TfidfVectorizer(ngram_range=ng,min_df=2); m=LogisticRegression(max_iter=3000,C=3).fit(v.fit_transform(trg.texte),trg.y)
    print("inédites",ng,round(m.score(v.transform(teg.texte),teg.y),3), "| sur le reste (échantillon):", round(m.score(v.transform(trg.texte.iloc[:1500]),trg.y.iloc[:1500]),3))
