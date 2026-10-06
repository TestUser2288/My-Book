import sys, warnings; warnings.filterwarnings("ignore"); sys.path.insert(0,"build")
import numpy as np
import outils_ch02 as O
from sentence_transformers import SentenceTransformer
a=O.charger_avis(); E=np.load("/home/ubuntu/.claude/jobs/5b7143f8/tmp/v4c2/Eall.npy")
st=SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",device="cpu")
for q in ["Article cassé dès la réception","Le colis n'était pas bien emballé","Mon colis a mis des semaines à arriver"]:
    qe=st.encode([q],normalize_embeddings=True)[0]; s=E@qe
    for j in np.argsort(-s)[:5]: print(q[:25],"|",a.sujet[j],a.note[j],round(float(s[j]),2),a.texte[j][:80])
    print(len(set(a.texte[np.argsort(-s)[:5]])))
