import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np, torch
from sklearn.feature_extraction.text import TfidfVectorizer
from sentence_transformers import SentenceTransformer
from transformers import AutoTokenizer, AutoModelForCausalLM
KB=["Les retours sont acceptés pendant 14 jours après la réception, avec le produit dans son emballage d'origine.",
"Les frais de port sont offerts à partir de 60 € d'achat ; en dessous, ils s'élèvent à 5,90 €.",
"Le service client répond du lundi au vendredi, de 9 h à 17 h, par courriel ou par téléphone.",
"Le remboursement est effectué sous 7 jours ouvrés après réception du retour, sur le moyen de paiement d'origine.",
"La livraison standard prend 3 à 5 jours ouvrés ; la livraison express prend 24 heures pour un supplément de 9 €.",
"Un produit endommagé à la réception est remplacé gratuitement si la réclamation est faite sous 48 heures avec une photo.",
"Les cartes cadeaux sont valables un an et ne sont pas remboursables.",
"Le produit A est garanti deux ans contre les défauts de fabrication."]
Q=["Combien de temps ai-je pour renvoyer un article ?","À partir de quel montant la livraison est-elle gratuite ?","Quand puis-je joindre quelqu'un au téléphone ?","Au bout de combien de temps serai-je remboursé ?","Peut-on recevoir sa commande le lendemain ?","Mon colis est arrivé cassé, que faire ?","Combien de temps dure la garantie du produit A ?","Puis-je me faire rembourser une carte cadeau ?","Quel est le prix du produit A ?"]
GOLD=[0,1,2,3,4,5,7,6,None]
st=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
E=st.encode(KB,normalize_embeddings=True); QE=st.encode(Q,normalize_embeddings=True)
tf=TfidfVectorizer().fit(KB+Q); Xk=tf.transform(KB)
for i,q in enumerate(Q):
    s=E@QE[i]; s2=(Xk@tf.transform([q]).T).toarray()[:,0]
    print(i,GOLD[i],"minilm",int(s.argmax()),round(float(s.max()),2),"| tfidf",int(s2.argmax()),round(float(s2.max()),2))
tok=AutoTokenizer.from_pretrained("HuggingFaceTB/SmolLM2-135M-Instruct"); m=AutoModelForCausalLM.from_pretrained("HuggingFaceTB/SmolLM2-135M-Instruct",dtype=torch.float32).eval()
for i in (0,5,8):
    top=int((E@QE[i]).argmax()); prompt=f"Réponds en français, en une phrase, uniquement à partir du document ci-dessous. Si la réponse n'y est pas, réponds « Je ne sais pas ».\n\nDocument : {KB[top]}\n\nQuestion : {Q[i]}"
    enc=tok.apply_chat_template([{"role":"user","content":prompt}],add_generation_prompt=True,return_tensors="pt",return_dict=True)
    with torch.no_grad(): o=m.generate(**enc,max_new_tokens=60,do_sample=False)
    print(i,repr(tok.decode(o[0,enc.input_ids.shape[1]:],skip_special_tokens=True)))
