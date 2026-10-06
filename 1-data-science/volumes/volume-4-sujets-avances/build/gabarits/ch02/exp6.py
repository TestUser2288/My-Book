import sys, time, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, pandas as pd, torch
import outils_ch02 as O
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.decomposition import NMF, LatentDirichletAllocation
from sklearn.metrics import adjusted_rand_score
STOP=["le","la","les","l'","un","une","des","de","du","d'","et","en","est","a","à","au","aux","je","ne","pas","que","qu'","ce","c'est","il","ça","sur","pour","par","très","vraiment","franchement","honnêtement","dans","l'ensemble","plus","se","qui","y","mon","ma","mes","si","sans","avec","été","était","tout","tous","on","m'a","j'ai","n'a","n'est","n'était","ni","aucun","rien","bon","bien"]
a=O.charger_avis(); a=a[a.texte.str.split().str.len()>3].reset_index(drop=True); sub=a.sample(3000,random_state=0).reset_index(drop=True)
tf=TfidfVectorizer(min_df=5,max_df=0.3,stop_words=STOP,token_pattern=r"[a-zàâçéèêëîïôûùüÿœ]{3,}"); X=tf.fit_transform(sub.texte); mots=np.array(tf.get_feature_names_out())
for k in (5,):
    nmf=NMF(k,random_state=0,init="nndsvd",max_iter=500).fit(X)
    for i,comp in enumerate(nmf.components_): print("NMF",i,list(mots[np.argsort(-comp)[:7]]))
    lab=nmf.transform(X).argmax(1); print("ARI",round(adjusted_rand_score(sub.sujet,lab),3)); print(pd.crosstab(lab,sub.sujet).to_string())
cv=CountVectorizer(min_df=5,max_df=0.3,stop_words=STOP,token_pattern=r"[a-zàâçéèêëîïôûùüÿœ]{3,}"); Xc=cv.fit_transform(sub.texte); lda=LatentDirichletAllocation(5,random_state=0,max_iter=20,learning_method="batch").fit(Xc); mc=np.array(cv.get_feature_names_out())
for i,comp in enumerate(lda.components_): print("LDA",i,list(mc[np.argsort(-comp)[:7]]))
print("ARI LDA",round(adjusted_rand_score(sub.sujet,lda.transform(Xc).argmax(1)),3))
# complétions
from transformers import AutoTokenizer, AutoModelForCausalLM
rep="HuggingFaceTB/SmolLM2-135M-Instruct"; tok=AutoTokenizer.from_pretrained(rep); m=AutoModelForCausalLM.from_pretrained(rep,dtype=torch.float32).eval()
for amorce in ["La boutique a été fondée en","Le produit A coûte exactement"]:
    ids=tok(amorce,return_tensors="pt").input_ids; sorties=[]
    for g in range(5):
        torch.manual_seed(g)
        with torch.no_grad(): out=m.generate(ids,max_new_tokens=8,do_sample=True,temperature=1.0,top_k=50,pad_token_id=tok.eos_token_id)
        sorties.append(tok.decode(out[0,ids.shape[1]:],skip_special_tokens=True).replace("\n"," "))
    print(amorce,sorties)
