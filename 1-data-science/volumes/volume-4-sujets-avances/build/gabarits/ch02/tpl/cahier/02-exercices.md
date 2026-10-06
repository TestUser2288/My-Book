# Chapitre 2 : NLP et modèles de langage — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 2 du livre. Les **applications** refont pas à pas, sur les avis de la boutique, les calculs que le livre n'a fait que résumer (TF-IDF, attention, décodage, BPE, recherche sémantique, RAG) ; les **exercices** se travaillent d'abord à la main, et leurs **corrigés** viennent à la fin. Chaque exercice indique la section du livre qu'il met en pratique. Tous les modèles s'exécutent hors ligne sur un ordinateur ordinaire.

## Préparation

Une seule cellule charge les bibliothèques et les 8 000 avis (simulés, générés par des gabarits de phrases : voir le livre, introduction du chapitre), répartit les avis nets (positifs : note ≥ 4, négatifs : note ≤ 2) en entraînement (75 %) et test (25 %), et ajuste la **référence** de la section 2.1.4 : TF-IDF (mots et paires de mots) + régression logistique. Les applications suivantes en réutilisent les noms : `avis` (tous les avis), `tr`, `te` (entraînement, test), `vec` et `modele` (la référence), et `O.SONDES` (48 phrases écrites à la main, hors gabarits, avec leurs étiquettes `O.Y_SONDES`). Le module `outils_ch02`, dans le dossier `build/`, contient les outils du chapitre (tokenisation, mini-transformer, décodage) ; ses fonctions sont lisibles.

```python
import sys, warnings, math, os
import numpy as np, pandas as pd, torch
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch02 as O
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split

torch.set_num_threads(2)
avis = O.etiqueter_tranches(O.charger_avis())
d = O.polarite(avis)
tr, te = train_test_split(d, test_size=0.25, random_state=0, stratify=d["y"])
vec = TfidfVectorizer(ngram_range=(1, 2), min_df=2)
modele = LogisticRegression(max_iter=3000, C=3).fit(vec.fit_transform(tr["texte"]), tr["y"])
acc_te = modele.score(vec.transform(te["texte"]), te["y"])
acc_so = ((modele.predict(vec.transform(O.SONDES))) == O.Y_SONDES).mean()
print(len(avis), len(tr), len(te), "| exactitude test :", round(acc_te, 3), "| sur les 48 phrases hors gabarit :", round(acc_so, 3))
```

Le test du corpus donne environ 94 %, et les phrases écrites à la main environ 62 % : c'est l'écart que le livre explique en section 2.1.5.

## Applications

### Application 2.1 — Du texte au TF-IDF, sans bibliothèque

*Sections du livre : 2.1.1 à 2.1.3.* **Objectif** : refaire le TF-IDF **de zéro** (jetons, comptages, idf, poids, cosinus), puis vérifier que la variante de `scikit-learn` donne la même idée avec des valeurs différentes, et que notre version de zéro classe aussi bien.

**Étape 1 — Jetons et vocabulaire.** On découpe chaque avis en jetons avec `O.tokeniser` (minuscules, apostrophe conservée), puis on construit le vocabulaire des mots présents au moins deux fois.

```python
from collections import Counter
jetons_tr = [O.tokeniser(t) for t in tr["texte"]]
df_mots = Counter(w for j in jetons_tr for w in set(j))                     # nombre de documents contenant chaque mot
vocab = sorted(w for w, n in df_mots.items() if n >= 2)
indice = {w: i for i, w in enumerate(vocab)}
print(len(vocab), "mots ; exemple de découpage :", jetons_tr[0][:8])
```

**Étape 2 — La matrice TF-IDF.** Pour chaque document, $\text{tf}=n_{t,d}/|d|$ ; pour chaque mot, $\text{idf}=\ln(N/\text{df})$ ; le poids est leur produit.

```python
N = len(jetons_tr)
idf = np.array([math.log(N / df_mots[w]) for w in vocab])
def tfidf(jetons):
    x = np.zeros(len(vocab))
    for w, n in Counter(jetons).items():
        if w in indice:
            x[indice[w]] = n / len(jetons) * idf[indice[w]]
    return x
X_tr = np.array([tfidf(j) for j in jetons_tr])
X_te = np.array([tfidf(O.tokeniser(t)) for t in te["texte"]])
top = np.argsort(-idf)[:3]; bas = np.argsort(idf)[:3]
print("mots les plus rares :", [vocab[i] for i in top], "| les plus fréquents :", [vocab[i] for i in bas])
```

**Étape 3 — Classer avec notre TF-IDF.**

```python
m0 = LogisticRegression(max_iter=3000, C=30).fit(X_tr, tr["y"])
print("exactitude (TF-IDF de zéro, mots seuls) :", round(m0.score(X_te, te["y"]), 3))
```

**Étape 4 — Le cosinus entre deux avis.** Les deux avis les plus proches d'un avis donné, parmi les 500 premiers du jeu d'entraînement.

```python
def cos(a, b):
    return float(a @ b / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-12))
q = 0
sims = [cos(X_tr[q], X_tr[i]) for i in range(1, 500)]
voisin = 1 + int(np.argmax(sims))
print("avis :", tr["texte"].iloc[q][:70], "\nvoisin :", tr["texte"].iloc[voisin][:70], "| cosinus", round(max(sims), 3))
```

Les mots les plus rares ne sont pas les plus utiles pour classer : ce sont des **fautes de frappe** (le plus petit df). Un `min_df` de 2 les élimine en grande partie. Notre TF-IDF de zéro, avec les mots seuls, atteint à peu près l'exactitude de la référence (mots et paires de mots) : sur ce corpus, **les paires de mots n'apportent presque rien**.

*Pour aller plus loin.* Ajoutez les paires de mots (bigrammes) à votre vocabulaire et vérifiez que l'exactitude monte d'au plus quelques dixièmes de point. Puis remplacez `ln(N/df)` par la variante de `scikit-learn`, $\ln\frac{1+N}{1+\text{df}}+1$, et comparez.

### Application 2.2 — La référence et les phrases hors gabarit

*Sections du livre : 2.1.4 et 2.1.5.* **Objectif** : voir **où** la référence se trompe sur les phrases écrites à la main, mesurer la part de mots inconnus, et écrire vos propres phrases de test.

**Étape 1 — Les erreurs sur les 48 phrases.**

```python
p = modele.predict_proba(vec.transform(O.SONDES))[:, 1]
faux = [i for i in range(len(O.SONDES)) if (p[i] > 0.5) != O.Y_SONDES[i]]
print(len(faux), "erreurs sur", len(O.SONDES))
for i in faux[:6]:
    print(f"   p(positif)={p[i]:.2f}  attendu={O.Y_SONDES[i]}  {O.SONDES[i]}")
```

**Étape 2 — La part de mots inconnus.** Pour chaque phrase, la proportion de ses mots absents du vocabulaire appris ; on compare les phrases bien et mal classées (l'hypothèse naturelle : les erreurs viennent des mots inconnus).

```python
connus = set(vec.vocabulary_)
def part_inconnue(s):
    j = O.tokeniser(s)
    return np.mean([w not in connus for w in j]) if j else 0.0
inc = np.array([part_inconnue(s) for s in O.SONDES])
ok = np.ones(len(O.SONDES), bool); ok[faux] = False
print("part moyenne de mots inconnus : phrases justes", round(inc[ok].mean(), 3), "| phrases fausses", round(inc[~ok].mean(), 3))
```

**Étape 3 — Vos propres phrases.** Écrivez six phrases (3 positives, 3 négatives) qui n'emploient **aucun** gabarit du corpus, et testez la référence dessus.

```python
mes_phrases = ["Colis reçu avec une semaine d'avance, bravo.", "Aucun souci, tout est conforme à la description.", "Un achat que je ne regrette pas.",
               "Décevant : la couleur n'a rien à voir avec la photo.", "Le vendeur n'a jamais répondu à mes relances.", "Article arrivé fendu, c'est inadmissible."]
mes_y = np.array([1, 1, 1, 0, 0, 0])
pm = modele.predict_proba(vec.transform(mes_phrases))[:, 1]
for s, pp, yy in zip(mes_phrases, pm, mes_y):
    print(f"p(positif)={pp:.2f}  attendu={yy}  {s}")
```

La part de mots inconnus est **élevée partout** (environ 40 % des mots, que la phrase soit bien ou mal classée) : elle ne suffit donc pas à expliquer les erreurs. Ce qui compte est le **signe** porté par les quelques mots connus, souvent ambigus (« rien », « colis », « pas »). Sur les six phrases que nous avons écrites, la référence se trompe dans la moitié des cas : elle n'a mémorisé que le vocabulaire et les tournures du corpus.

*Pour aller plus loin.* Étendez votre jeu à 30 phrases et calculez l'incertitude de l'exactitude : l'écart-type d'une proportion est $\sqrt{p(1-p)/n}$.

### Application 2.3 — L'attention de zéro

*Sections du livre : 2.2.2 à 2.2.6.* **Objectif** : écrire l'attention multi-têtes avec seulement `numpy`, la comparer à PyTorch, et visualiser l'effet du masque causal.

**Étape 1 — Une tête, avec des projections quelconques.** Quatre jetons de dimension 4, des projections $W_Q,W_K,W_V$ tirées au hasard.

```python
rng = np.random.default_rng(0)
n, d = 4, 4
X = rng.standard_normal((n, d))
Wq, Wk, Wv = (rng.standard_normal((d, d)) for _ in range(3))
def softmax_lignes(S):
    e = np.exp(S - S.max(axis=1, keepdims=True))
    return e / e.sum(axis=1, keepdims=True)
Q, K, V = X @ Wq, X @ Wk, X @ Wv
A = softmax_lignes(Q @ K.T / np.sqrt(d))
sortie = A @ V
print(A.round(2)); print("somme des lignes :", A.sum(axis=1))
```

**Étape 2 — Comparaison avec PyTorch.**

```python
import torch.nn.functional as F
ref = F.scaled_dot_product_attention(*(torch.tensor(M, dtype=torch.float64)[None] for M in (Q, K, V)))[0].numpy()
print("écart maximal avec PyTorch :", float(np.abs(ref - sortie).max()))
```

**Étape 3 — Le masque causal.** On remplace par $-\infty$ les scores de la partie triangulaire supérieure avant le softmax.

```python
S = Q @ K.T / np.sqrt(d)
S_masque = np.where(np.triu(np.ones((n, n), bool), 1), -np.inf, S)
A_c = softmax_lignes(S_masque)
print(A_c.round(2))
```

**Étape 4 — Plusieurs têtes.** On découpe les dimensions en 2 têtes de dimension 2, on calcule chaque attention, on concatène.

```python
def tete(X, Wq, Wk, Wv):
    q, k, v = X @ Wq, X @ Wk, X @ Wv
    return softmax_lignes(q @ k.T / np.sqrt(q.shape[1])) @ v
h = 2
sorties = [tete(X, Wq[:, i * 2:(i + 1) * 2], Wk[:, i * 2:(i + 1) * 2], Wv[:, i * 2:(i + 1) * 2]) for i in range(h)]
multi = np.concatenate(sorties, axis=1)
print(multi.shape, "| différence avec la tête unique :", float(np.abs(multi - sortie).max()))
```

La somme des lignes vaut 1, l'écart avec PyTorch est de l'ordre de $10^{-16}$, et le masque causal rend la matrice triangulaire inférieure : la première ligne ne regarde que le premier jeton. Les deux têtes de dimension 2 ne redonnent **pas** la tête unique de dimension 4 : une attention multi-têtes **n'est pas** la même fonction qu'une tête large, elle calcule plusieurs attentions indépendantes qu'une dernière projection remélange.

*Pour aller plus loin.* Ajoutez la projection de sortie $W_O$ et vérifiez que le nombre de paramètres de l'ensemble $(W_Q,W_K,W_V,W_O)$ vaut $4d^2$.

### Application 2.4 — Entraîner un mini-transformer, et l'interroger

*Sections du livre : 2.2.5 à 2.2.8.* **Objectif** : entraîner le mini-transformer sur un sous-échantillon, le comparer à la référence, et mesurer sa **sensibilité à l'ordre** des mots, que TF-IDF (sans paires de mots) ne peut pas avoir.

**Étape 1 — Entraînement sur 2 000 avis.**

```python
petit = tr.sample(2000, random_state=0)
voc = O.Vocabulaire(petit["texte"].tolist(), min_freq=2)
mini = O.entrainer_classifieur(petit["texte"].tolist(), petit["y"].to_numpy(), voc, epoques=4)
p_te = O.predire_classe(mini, voc, te["texte"].tolist())
print("paramètres :", sum(p.numel() for p in mini.parameters()), "| exactitude test :", round(((p_te > 0.5) == te["y"].to_numpy()).mean(), 3))
```

**Étape 2 — Sur les phrases hors gabarit.**

```python
ps = O.predire_classe(mini, voc, O.SONDES)
print("exactitude sur les 48 phrases :", round(((ps > 0.5) == O.Y_SONDES).mean(), 3))
```

**Étape 3 — Sensibilité à l'ordre.** On mélange l'ordre des mots de 300 avis du test et l'on mesure la variation moyenne de la probabilité prédite, pour le mini-transformer et pour un TF-IDF de mots seuls.

```python
rng = np.random.default_rng(0)
echant = te["texte"].iloc[:300].tolist()
melange = [" ".join(rng.permutation(t.split())) for t in echant]
vec1 = TfidfVectorizer(min_df=2).fit(tr["texte"]); lr1 = LogisticRegression(max_iter=3000, C=3).fit(vec1.transform(tr["texte"]), tr["y"])
ecart_mini = np.abs(O.predire_classe(mini, voc, echant) - O.predire_classe(mini, voc, melange)).mean()
ecart_tfidf = np.abs(lr1.predict_proba(vec1.transform(echant))[:, 1] - lr1.predict_proba(vec1.transform(melange))[:, 1]).mean()
print("variation moyenne de la probabilité : mini-transformer", round(ecart_mini, 3), "| TF-IDF de mots", round(ecart_tfidf, 6))
```

Le TF-IDF de mots seuls est **parfaitement insensible** à l'ordre (variation nulle : même sac de mots). Le mini-transformer l'est **presque** aussi (variation de l'ordre du millième) : malgré l'encodage positionnel, il a appris, sur ce corpus où l'ordre apporte peu, à se comporter surtout comme un sac de mots. Sur les phrases hors gabarit, il ne fait pas mieux que la référence : l'attention ne remplace pas le pré-entraînement (section 2.2.7). Un modèle capable d'être sensible à l'ordre ne l'est que si **les données l'exigent**.

*Pour aller plus loin.* Entraînez avec `couches=1` puis `couches=3` et comparez exactitude et nombre de paramètres ; mesurez la variation due à la graine (`graine=0, 1, 2`).

### Application 2.5 — Le décodage de zéro

*Sections du livre : 2.3.3 et 2.3.4.* **Objectif** : implémenter température, top-k et top-p sur un petit vocabulaire, et vérifier empiriquement par simulation que les fréquences tirées suivent les probabilités.

**Étape 1 — La température.** Cinq jetons, des scores arbitraires.

```python
mots = ["rapide", "lent", "correct", "cher", "parfait"]
z = np.array([2.0, 0.5, 1.2, -0.3, 1.8])
def probas(z, T=1.0):
    e = np.exp((z - z.max()) / T)
    return e / e.sum()
tab = pd.DataFrame({f"T={T}": probas(z, T) for T in (0.3, 1.0, 3.0)}, index=mots).round(3)
tab.loc["entropie (bits)"] = [round(O.entropie(probas(z, T)), 2) for T in (0.3, 1.0, 3.0)]
print(tab.to_string())
```

**Étape 2 — Top-k et top-p.**

```python
def top_k(p, k):
    q = np.where(p >= np.sort(p)[-k], p, 0.0)
    return q / q.sum()
def top_p(p, seuil):
    ordre = np.argsort(-p); cum = np.cumsum(p[ordre])
    garde = ordre[: np.searchsorted(cum, seuil) + 1]
    q = np.zeros_like(p); q[garde] = p[garde]
    return q / q.sum()
p1 = probas(z)
print("top-2 :", top_k(p1, 2).round(3), "| top-p 0,8 :", top_p(p1, 0.8).round(3))
```

**Étape 3 — Vérification par simulation.** On tire 100 000 jetons à $T=1$ et l'on compare les fréquences aux probabilités.

```python
rng = np.random.default_rng(0)
tirages = rng.choice(len(mots), size=100000, p=p1)
freq = np.bincount(tirages, minlength=len(mots)) / len(tirages)
print(pd.DataFrame({"théorique": p1, "observé": freq}, index=mots).round(3).to_string())
print("écart maximal :", round(float(np.abs(p1 - freq).max()), 4))
```

À $T=0{,}3$ la masse se concentre sur les deux meilleurs jetons (« rapide » 0,63 et « parfait » 0,32 ; entropie faible) ; à $T=3$, la distribution est proche de l'uniforme (entropie proche du maximum $\log_2 5\approx2{,}32$ bits). Le top-p 0,8 retient les jetons les plus probables jusqu'à atteindre 80 % de masse : ici trois jetons, et leur proportion relative est conservée.

*Pour aller plus loin.* Vérifiez que, pour $T\to0$, la sortie tend vers le décodage glouton (un seul jeton à probabilité 1), et que top-p = 1 ne change rien.

### Application 2.6 — Le BPE à la main

*Section du livre : 2.3.2.* **Objectif** : entraîner un BPE sur le vocabulaire des avis, puis voir comment il découpe un mot qu'il n'a jamais vu et une faute de frappe.

**Étape 1 — L'algorithme.** Un mot est une suite de symboles terminée par la marque `·` ; à chaque étape, on fusionne la paire voisine la plus fréquente (pondérée par la fréquence des mots).

```python
def apprendre_bpe(freq_mots, n_fusions):
    corpus = {tuple(m) + ("·",): f for m, f in freq_mots.items()}
    regles = []
    for _ in range(n_fusions):
        paires = Counter()
        for mot, f in corpus.items():
            for a, b in zip(mot, mot[1:]):
                paires[(a, b)] += f
        if not paires:
            break
        a, b = max(paires, key=paires.get)
        regles.append((a, b))
        corpus = {fusionner(mot, a, b): f for mot, f in corpus.items()}
    return regles

def fusionner(mot, a, b):
    sortie, i = [], 0
    while i < len(mot):
        if i < len(mot) - 1 and mot[i] == a and mot[i + 1] == b:
            sortie.append(a + b); i += 2
        else:
            sortie.append(mot[i]); i += 1
    return tuple(sortie)
```

**Étape 2 — Entraînement sur les avis.** 200 fusions sur les mots des avis d'entraînement.

```python
freq_mots = Counter(w for j in jetons_tr for w in j)
regles = apprendre_bpe(freq_mots, 200)
print(regles[:8], "...", regles[-3:])
```

**Étape 3 — Découper un mot quelconque.** On applique les règles dans l'ordre où elles ont été apprises.

```python
def decouper(mot, regles):
    s = tuple(mot) + ("·",)
    for a, b in regles:
        s = fusionner(s, a, b)
    return s
for mot in ["livraison", "interminable", "livriason", "emballage"]:
    print(f"{mot:13s} ->", " ".join(decouper(mot, regles)))
```

Les mots fréquents (« livraison », « emballage ») sont réduits à un ou deux symboles ; un mot **jamais vu** comme « interminable » est découpé en **morceaux plus petits** que le BPE connaît, sans jamais être « inconnu » ; la **faute de frappe** « livriason » est découpée en cinq morceaux courts (« li v ri a son »). C'est la grande différence avec un vocabulaire de mots entiers.

*Pour aller plus loin.* Faites varier le nombre de fusions (50, 200, 800) et tracez la longueur moyenne de la segmentation d'un mot en fonction de ce nombre.

### Application 2.7 — Recherche sémantique avec MiniLM

*Sections du livre : 2.4.2 et 2.2.7.* **Objectif** : construire un petit moteur de recherche sur 2 000 avis avec des plongements de phrases, et le comparer à TF-IDF.

**Étape 1 — Encoder les avis.** Le modèle `paraphrase-multilingual-MiniLM-L12-v2` (118 M de paramètres) transforme chaque avis en un vecteur de 384 nombres ; les vecteurs sont normalisés, donc le produit scalaire est le cosinus.

```python
from sentence_transformers import SentenceTransformer
st = SentenceTransformer("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", device="cpu")
corpus = avis.sample(2000, random_state=1).reset_index(drop=True)
E = st.encode(corpus["texte"].tolist(), batch_size=128, normalize_embeddings=True)
print(E.shape)
```

**Étape 2 — Deux moteurs.**

```python
tf = TfidfVectorizer(min_df=2).fit(corpus["texte"]); X_c = tf.transform(corpus["texte"])
def chercher(requete, methode, k=5):
    if methode == "tfidf":
        s = (X_c @ tf.transform([requete]).T).toarray()[:, 0]
    else:
        s = E @ st.encode([requete], normalize_embeddings=True)[0]
    return np.argsort(-s)[:k]
for q in ["Mon colis est arrivé très en retard", "Je trouve ça trop cher"]:
    print("Requête :", q)
    for m in ("tfidf", "minilm"):
        print(f"   {m:7s}", [corpus['sujet'][j] + "/" + str(corpus['note'][j]) for j in chercher(q, m)])
```

**Étape 3 — Précision au rang 5 sur les 15 requêtes du livre.** Un résultat est **pertinent** s'il a pour sujet principal celui de la requête et une note ≤ 2.

```python
res = []
for sj, qs in O.REQUETES.items():
    pert = set(np.where((corpus["sujet"] == sj) & (corpus["note"] <= 2))[0])
    for q in qs:
        res.append([O.precision_au_rang(chercher(q, m, 5), pert, 5) for m in ("tfidf", "minilm")])
res = np.array(res)
print("précision moyenne au rang 5 : TF-IDF", res[:, 0].mean().round(3), "| MiniLM", res[:, 1].mean().round(3), "| requêtes :", len(res))
```

Sur ce sous-corpus, TF-IDF est **devant** (environ 0,60 contre 0,49), alors que sur les 8 000 avis du livre l'écart est plus faible (0,77 contre 0,69) : les chiffres varient beaucoup avec le corpus, preuve du bruit de la mesure. MiniLM retrouve des avis de même **thème** même sans mot commun, mais ignore souvent le **ton** (il renvoie parfois des avis positifs sur le même thème), et la mesure dépend de l'étiquette « sujet principal », imparfaite pour des avis qui mêlent plusieurs sujets.

*Pour aller plus loin.* Combinez les deux scores (par exemple la somme des rangs inversés) : une recherche **hybride** fait-elle mieux que chacune ?

### Application 2.8 — Un RAG minimal

*Section du livre : 2.5.3.* **Objectif** : construire la chaîne *indexer → retrouver → construire le prompt*, et l'évaluer à chaque maillon. Aucun modèle de génération n'est utilisé ici : on s'intéresse à ce qu'on envoie au modèle.

**Étape 1 — Base de connaissances et questions.** Huit passages (inventés) et neuf questions, dont une sans réponse dans la base.

```python
BASE = ["Les retours sont acceptés pendant 14 jours après la réception, avec le produit dans son emballage d'origine.",
        "Les frais de port sont offerts à partir de 60 € d'achat ; en dessous, ils s'élèvent à 5,90 €.",
        "Le service client répond du lundi au vendredi, de 9 h à 17 h, par courriel ou par téléphone.",
        "Le remboursement est effectué sous 7 jours ouvrés après réception du retour, sur le moyen de paiement d'origine.",
        "La livraison standard prend 3 à 5 jours ouvrés ; la livraison express prend 24 heures pour un supplément de 9 €.",
        "Un produit endommagé à la réception est remplacé gratuitement si la réclamation est faite sous 48 heures avec une photo.",
        "Les cartes cadeaux sont valables un an et ne sont pas remboursables.",
        "Le produit A est garanti deux ans contre les défauts de fabrication."]
QUESTIONS = ["Combien de temps ai-je pour renvoyer un article ?", "À partir de quel montant la livraison est-elle gratuite ?",
             "Quand puis-je joindre quelqu'un au téléphone ?", "Au bout de combien de temps serai-je remboursé ?",
             "Peut-on recevoir sa commande le lendemain ?", "Mon colis est arrivé cassé, que faire ?",
             "Combien de temps dure la garantie du produit A ?", "Puis-je me faire rembourser une carte cadeau ?", "Quel est le prix du produit A ?"]
ATTENDU = [0, 1, 2, 3, 4, 5, 7, 6, None]
E_base = st.encode(BASE, normalize_embeddings=True); E_q = st.encode(QUESTIONS, normalize_embeddings=True)
scores = E_q @ E_base.T
rang = np.argsort(-scores, axis=1)
repondables = [i for i, a in enumerate(ATTENDU) if a is not None]
for k in (1, 3):
    print(f"succès au rang {k} :", sum(ATTENDU[i] in rang[i, :k] for i in repondables), "sur", len(repondables))
```

**Étape 2 — Construire le prompt.** On insère les trois meilleurs passages, numérotés pour que le modèle puisse **citer**, et la consigne de refuser s'il ne sait pas.

```python
def construire_prompt(question, k=3):
    passages = "\n".join(f"[{n + 1}] {BASE[j]}" for n, j in enumerate(rang[QUESTIONS.index(question), :k]))
    return ("Réponds en français à la question à partir des passages ci-dessous et cite le numéro du passage utilisé. "
            f"Si la réponse n'y figure pas, réponds « Je ne sais pas ».\n\nPassages :\n{passages}\n\nQuestion : {question}")
print(construire_prompt(QUESTIONS[5]))
```

**Étape 3 — Peut-on refuser avec un seuil ?** Le meilleur score de la question hors base, comparé à celui des questions avec réponse.

```python
meilleur = scores.max(axis=1)
print("scores des questions avec réponse :", meilleur[repondables].round(2))
print("score de la question hors base    :", meilleur[8].round(2))
```

Le passage attendu est en première position pour 6 questions sur 8 et dans les trois premiers pour les 8 : fournir **trois** passages plutôt qu'un rattrape les erreurs de recherche. La question hors base a un score **dans la plage des questions avec réponse** (0,38, entre 0,05 et 0,69) : aucun seuil ne sépare proprement les deux cas, et un modèle de génération à qui l'on fournirait ce passage pourrait **inventer** une réponse. D'où les citations et les tests de refus du livre (section 2.5.3).

*Pour aller plus loin.* Branchez un modèle de génération (SmolLM2, voir le livre) sur `construire_prompt`, et évaluez, sur les neuf questions, la part de réponses correctes **et** la part de refus justifiés.

## Exercices

### Exercice 2.1 ⭐ — Mots vides et négation (section 2.1.1)

1. Sur nos avis d'entraînement, quelle est la proportion d'avis négatifs qui contiennent le jeton « pas », et quelle est celle des avis positifs ?
2. Retirez « pas » du texte (remplacez-le par une chaîne vide) avant de vectoriser, et comparez l'exactitude de la référence (TF-IDF de mots seuls, régression logistique) avec et sans ce retrait.
3. Pourquoi retirer « pas » comme mot vide est-il dangereux pour l'analyse de sentiments ?

### Exercice 2.2 ⭐ — Racinisation à la hache (section 2.1.1)

Écrivez une fonction qui retire les terminaisons « -s », « -es », « -ement » et « -ions » d'un mot (si le mot restant fait au moins quatre lettres). Appliquez-la à « livraisons », « livraison », « rapidement », « rapide », « chères », « cher ». Quels mots sont regroupés à raison ? Lesquels à tort ou pas du tout ?

### Exercice 2.3 ⭐⭐ — L'idf de `scikit-learn` (section 2.1.3)

Soit trois documents « alpha beta », « alpha gamma » et « alpha delta ». Calculez à la main $\text{idf}(\text{alpha})$ et $\text{idf}(\text{beta})$ avec $\ln(N/\text{df})$, puis avec la formule lissée de `scikit-learn`, $\ln\frac{1+N}{1+\text{df}}+1$. Vérifiez avec `TfidfVectorizer`. Quelle est la propriété de la formule lissée pour un mot présent dans tous les documents ?

### Exercice 2.4 ⭐⭐ — Les mots inconnus (section 2.1.5)

Parmi les 48 phrases hors gabarit, quelle proportion de **mots** (jetons) est absente du vocabulaire de la référence ? Cette proportion est-elle plus élevée pour les phrases mal classées que pour les phrases bien classées ? Que concluez-vous sur l'explication « les erreurs viennent des mots inconnus » ?

### Exercice 2.5 ⭐⭐ — Une attention à deux jetons (section 2.2.2)

Deux jetons $x_1=(1,0)$, $x_2=(0,1)$ ; $W_Q=\begin{pmatrix}2&0\\0&1\end{pmatrix}$, $W_K=W_V=I$. Calculez à la main la matrice des poids d'attention $A$ et la sortie, avec $d_k=2$, et vérifiez numériquement.

### Exercice 2.6 ⭐⭐⭐ — La variance des scores et l'équivariance (sections 2.2.3 et 2.2.4)

1. Démontrez que si les composantes de $q$ et $k$ sont indépendantes, centrées, de variance 1, alors $\mathrm{Var}(q\cdot k)=d_k$.
2. Démontrez que l'attention sans positions est équivariante par permutation : si $P$ est une matrice de permutation, $\text{Att}(PX)=P\,\text{Att}(X)$.
3. Vérifiez la première propriété par simulation pour $d_k=16$.

### Exercice 2.7 ⭐⭐ — Compter les paramètres (section 2.2.5)

Un transformer a 12 blocs de dimension $d=768$ (réseau par jeton de largeur $4d$), un vocabulaire de 30 000 jetons. Estimez le nombre de paramètres des blocs (formule $12d^2+13d$ par bloc) et des plongements d'entrée. Quelle part du total représentent les plongements ?

### Exercice 2.8 ⭐⭐ — Le prix de la longueur (section 2.2.6)

Un modèle a 32 têtes et 40 couches. Si l'on stockait la matrice d'attention **complète** en flottants de 16 bits (2 octets) pour un texte de $n$ jetons, quelle mémoire faut-il pour $n=2\,048$ et pour $n=32\,768$ ? Par quel facteur la mémoire est-elle multipliée quand $n$ est multiplié par 16 ? Pourquoi les implémentations modernes évitent-elles de stocker cette matrice ?

### Exercice 2.9 ⭐ — La température (section 2.3.4)

Des scores $z=(2,\,1,\,0)$. Calculez les probabilités du softmax pour $T=1$, $T=0{,}5$ et $T=2$. Que valent les limites $T\to0$ et $T\to\infty$ ? Que devient l'entropie ?

### Exercice 2.10 ⭐⭐ — Top-k contre top-p (section 2.3.4)

Deux distributions sur dix jetons : (a) $(0{,}91,\,0{,}02,\,0{,}01,\dots)$ où la masse restante est répartie sur les neuf autres ; (b) quasi uniforme (0,1 chacun). Pour chacune, combien de jetons retiennent le top-k avec $k=5$ et le top-p avec $p=0{,}85$ ? Quel est le défaut du top-k que cela illustre ?

### Exercice 2.11 ⭐⭐ — Le BPE à la main (section 2.3.2)

Corpus (mot : fréquence) : « bas » 5, « basse » 2, « passe » 6, « passage » 3. En partant des caractères avec marque de fin de mot, effectuez à la main les **trois premières** fusions du BPE (en cas d'égalité, retenez la première paire rencontrée dans l'ordre du corpus) et donnez le découpage de « passe ». Vérifiez avec le code de l'application 2.6.

### Exercice 2.12 ⭐⭐ — Évaluer une recherche (section 2.4.2)

Une requête a 4 documents pertinents (parmi 1 000). Le moteur renvoie, dans l'ordre, des documents dont la pertinence est : 1, 0, 1, 0, 0, 1, 0, 0, 0, 1. Calculez la précision au rang 3, au rang 5, au rang 10, le rappel au rang 5, et le **rang réciproque** (inverse du rang du premier pertinent). Quelles limites a une moyenne de la précision au rang 5 sur quinze requêtes ?

### Exercice 2.13 ⭐⭐ — Le vocabulaire qui explose (section 2.4.4)

Mesurez, sur les avis, la **croissance du vocabulaire** : le nombre de mots distincts en fonction du nombre d'avis lus (100, 500, 2 000, 8 000), avec les formes de surface, puis après passage en minuscules et après une racinisation à la hache. Que constatez-vous sur ce corpus ? Pourquoi une langue qui accole des articles et des pronoms aux mots verrait-elle sa courbe monter plus vite ?

### Exercice 2.14 ⭐⭐ — Évaluer un RAG (section 2.5.3)

Un RAG répond à 100 questions : la recherche place le bon passage au rang 1 pour 70 questions et au rang 2 ou 3 pour 15 ; il ne figure pas dans les trois premiers pour 15. Quand le bon passage est dans le prompt, le modèle répond juste dans 90 % des cas ; quand il ne l'est pas, dans 10 % des cas (par chance ou connaissance générale). Quelle est la part de réponses justes si l'on fournit **un** passage (rang 1) ? Si l'on en fournit **trois** ? Donnez deux raisons de ne pas fournir tous les passages disponibles.

## Corrigés

### Corrigé 2.1

1. « pas » apparaît dans environ 54 % des avis négatifs contre 34 % des positifs (voir le calcul ci-dessous).
2. Le retrait de « pas » ne change **pas** l'exactitude sur ce corpus (0,944 dans les deux cas) : d'autres indices subsistent dans chaque avis. Cela ne rend pas le retrait anodin ailleurs.
3. « Pas » inverse le sens des mots voisins : sans lui, « pas satisfait » et « satisfait » deviennent identiques.

```python
neg = tr[tr["y"] == 0]["texte"].apply(lambda s: "pas" in O.tokeniser(s)).mean()
pos = tr[tr["y"] == 1]["texte"].apply(lambda s: "pas" in O.tokeniser(s)).mean()
def exactitude(retirer):
    f = (lambda s: " ".join(w for w in O.tokeniser(s) if w != "pas")) if retirer else (lambda s: s)
    v = TfidfVectorizer(min_df=2).fit(tr["texte"].map(f))
    m = LogisticRegression(max_iter=3000, C=3).fit(v.transform(tr["texte"].map(f)), tr["y"])
    return m.score(v.transform(te["texte"].map(f)), te["y"])
print(f"« pas » dans {neg:.1%} des avis négatifs et {pos:.1%} des positifs | exactitude avec : {exactitude(False):.3f}, sans : {exactitude(True):.3f}")
```

### Corrigé 2.2

« livraisons » et « livraison » sont regroupés (« livraison »), « rapidement » devient « rapid » et « rapide » reste « rapide » : à **tort** non regroupés ; « chères » devient « chèr » et « cher » reste « cher » : non regroupés non plus. La racinisation à la hache est **simple et imparfaite** : elle regroupe bien le pluriel et rate des variantes (« -e », accents).

```python
def racine(mot):
    for suf in ("ement", "ions", "es", "s"):
        if mot.endswith(suf) and len(mot) - len(suf) >= 4:
            return mot[: -len(suf)]
    return mot
for m in ["livraisons", "livraison", "rapidement", "rapide", "chères", "cher"]:
    print(f"{m:11s} -> {racine(m)}")
```

### Corrigé 2.3

Avec $N=3$ : « alpha » est dans les 3 documents, « beta » dans un seul. Version de cours : $\text{idf}(\text{alpha})=\ln1=0$, $\text{idf}(\text{beta})=\ln3\approx1{,}099$. Version lissée : $\text{idf}(\text{alpha})=\ln\frac44+1=1$, $\text{idf}(\text{beta})=\ln\frac42+1\approx1{,}693$. La formule lissée garantit qu'un mot présent partout garde un **poids strictement positif** (1), au lieu d'être effacé (0).

```python
tv = TfidfVectorizer(norm=None).fit(["alpha beta", "alpha gamma", "alpha delta"])
print(dict(zip(tv.get_feature_names_out(), tv.idf_.round(3))), "| à la main :", round(math.log(4 / 2) + 1, 3), round(math.log(3), 3))
```

### Corrigé 2.4

La part de mots inconnus est **voisine** pour les phrases bien et mal classées (environ 40 % dans les deux cas, un peu moins pour les phrases fausses). L'hypothèse « les erreurs viennent des mots inconnus » ne tient donc pas telle quelle : *toutes* les phrases hors gabarit contiennent beaucoup de mots inconnus ; la phrase est bien classée quand les quelques mots connus portent le bon signe, et mal classée quand ils sont ambigus. Une hypothèse se **teste**, elle ne se suppose pas.

```python
connus = set(vec.vocabulary_)
p = modele.predict_proba(vec.transform(O.SONDES))[:, 1]
juste = (p > 0.5) == O.Y_SONDES
inc = np.array([np.mean([w not in connus for w in O.tokeniser(s)]) for s in O.SONDES])
print("part de mots inconnus : phrases justes", inc[juste].mean().round(3), "| phrases fausses", inc[~juste].mean().round(3))
```

### Corrigé 2.5

Les scores bruts $Q K^\top$ : $q_1=(2,0)$, $q_2=(0,1)$, $k_1=(1,0)$, $k_2=(0,1)$ donnent $\begin{pmatrix}2&0\\0&1\end{pmatrix}$ ; divisés par $\sqrt2$ : $\begin{pmatrix}1{,}414&0\\0&0{,}707\end{pmatrix}$. Le softmax ligne à ligne donne $A_{1\cdot}=(0{,}804,\;0{,}196)$ et $A_{2\cdot}=(0{,}330,\;0{,}670)$ ; la sortie (avec $V=X$) est donc $\begin{pmatrix}0{,}804&0{,}196\\0{,}330&0{,}670\end{pmatrix}$ (la matrice $A$ elle-même, car $V=I$).

```python
X = np.array([[1., 0.], [0., 1.]]); Wq = np.diag([2., 1.])
S = (X @ Wq) @ X.T / np.sqrt(2)
A = np.exp(S) / np.exp(S).sum(axis=1, keepdims=True)
print(A.round(3)); print((A @ X).round(3))
```

### Corrigé 2.6

1. $q\cdot k=\sum_mq_mk_m$. Les termes $q_mk_m$ sont indépendants, de moyenne $E[q_m]E[k_m]=0$ et de variance $E[q_m^2k_m^2]=E[q_m^2]E[k_m^2]=1$ (indépendance de $q_m$ et $k_m$). La variance d'une somme de termes indépendants est la somme des variances : $\mathrm{Var}(q\cdot k)=d_k$.
2. Pour $X'=PX$ : $Q'=PXW_Q=PQ$, de même $K'=PK$, $V'=PV$. Alors $Q'K'^\top=PQK^\top P^\top$. Le softmax ligne à ligne commute avec la permutation des lignes **et** des colonnes (il normalise chaque ligne, sur un ensemble de colonnes que $P^\top$ ne fait que réordonner) : $\text{softmax}(PSP^\top)=P\,\text{softmax}(S)P^\top$. Donc $A'V'=PAP^\top\,PV=PAV$ car $P^\top P=I$ : la sortie est permutée comme l'entrée.
3. Voir le code.

```python
rng = np.random.default_rng(0)
q = rng.standard_normal((200000, 16)); k = rng.standard_normal((200000, 16))
print("variance de q·k :", round(float((q * k).sum(axis=1).var()), 2), "(théorie : 16)")
```

### Corrigé 2.7

Par bloc : $12\times768^2+13\times768=7\,077\,888+9\,984=7\,087\,872$ ; pour 12 blocs : environ 85,1 M. Les plongements d'entrée : $30\,000\times768=23{,}04$ M. Total ≈ 108 M, dont les plongements font environ **21 %**.

```python
d, L, V = 768, 12, 30000
blocs = L * (12 * d**2 + 13 * d); emb = V * d
print(f"blocs : {blocs / 1e6:.1f} M | plongements : {emb / 1e6:.2f} M | part des plongements : {emb / (blocs + emb):.1%}")
```

### Corrigé 2.8

La matrice complète coûte $n^2\times2$ octets, par tête et par couche, donc $n^2\times2\times32\times40$ octets. Pour $n=2\,048$ : environ 10,7 Go ; pour $n=32\,768$ : environ **2,7 To**. La mémoire est multipliée par $16^2=256$. Les implémentations modernes calculent l'attention **par blocs**, sans jamais écrire la matrice complète en mémoire rapide (et recalculent ce qu'il faut pour la rétropropagation).

```python
for n in (2048, 32768):
    print(f"n = {n:6d} : {n * n * 2 * 32 * 40 / 1e9:10.1f} Go")
```

### Corrigé 2.9

Le softmax de $(2,1,0)$ : $e^2=7{,}389$, $e^1=2{,}718$, $e^0=1$, somme 11,107 : $T=1$ donne $(0{,}665,\;0{,}245,\;0{,}090)$. À $T=0{,}5$ ($z/T=(4,2,0)$) : $(0{,}867,\;0{,}117,\;0{,}016)$ ; à $T=2$ ($(1,0{,}5,0)$) : $(0{,}506,\;0{,}307,\;0{,}186)$. Limites : $T\to0$ donne la distribution (1, 0, 0) (décodage glouton, entropie 0) ; $T\to\infty$ donne $(\frac13,\frac13,\frac13)$ (entropie maximale $\log_23\approx1{,}585$ bits).

```python
z = np.array([2., 1., 0.])
for T in (0.01, 0.5, 1, 2, 100):
    pT = O.softmax(z / T)
    print(f"T={T:<5} p={pT.round(3)}  entropie={O.entropie(pT):.3f} bits")
```

### Corrigé 2.10

(a) Une distribution concentrée : le top-p 0,85 ne retient **qu'un jeton** (0,91 ≥ 0,85), alors que le top-k avec $k=5$ en retient 5, dont quatre quasi nuls. (b) Une distribution plate : le top-p 0,85 retient **9 jetons** (9 × 0,1 = 0,9 ≥ 0,85), le top-k avec $k=5$ n'en retient que 5 et **élimine arbitrairement** des jetons aussi probables que ceux qu'il garde. Le top-k ignore la **forme** de la distribution ; le top-p s'y adapte.

```python
pa = np.array([0.91] + [0.09 / 9] * 9); pb = np.full(10, 0.1)
for nom, p_ in (("(a) concentrée", pa), ("(b) plate", pb)):
    print(nom, "| top-k=5 :", int((O.decoder_probas(np.log(p_), top_k=5) > 0).sum()), "jetons | top-p=0,85 :", int((O.decoder_probas(np.log(p_), top_p=0.85) > 0).sum()), "jetons")
```

### Corrigé 2.11

Mots (avec fin) : b a s · (5), b a s s e · (2), p a s s e · (6), p a s s a g e · (3). Paires : (a,s) = 5+2+6+3 = 16, (s,s) = 2+6+3 = 11, (e,·) = 2+6+3 = 11, (p,a) = 9, (s,e) = 8, (b,a) = 7. **Fusion 1** : (a, s), la plus fréquente (16), donne « as ». Après cette fusion : (as, s) = 11, (e, ·) = 11, (p, as) = 9, (s, e) = 8. Il y a égalité entre (as, s) et (e, ·) ; (as, s) est rencontrée en premier (dans « basse »), d'où la **fusion 2** : « ass ». Après elle : (e, ·) = 11 reste la plus fréquente (devant (p, ass) = 9 et (ass, e) = 8) : **fusion 3** : « e· ». Découpage de « passe » : « p », « ass », « e· ».

```python
f = apprendre_bpe({"bas": 5, "basse": 2, "passe": 6, "passage": 3}, 3)
print(f, "| passe ->", decouper("passe", f))
```

### Corrigé 2.12

Pertinence : 1, 0, 1, 0, 0, 1, 0, 0, 0, 1. Précision au rang 3 = 2/3 ≈ 0,667 ; au rang 5 = 2/5 = 0,4 ; au rang 10 = 4/10 = 0,4. Rappel au rang 5 = 2/4 = 0,5. Rang réciproque = 1/1 = 1. Une moyenne de précision au rang 5 sur 15 requêtes est **très bruitée** (un seul résultat déplace 0,2 par requête, soit 0,013 de la moyenne), dépend de la qualité des jugements de pertinence, ignore l'ordre dans les cinq premiers et ne dit rien du rappel.

```python
pert = np.array([1, 0, 1, 0, 0, 1, 0, 0, 0, 1])
print({k: round(pert[:k].mean(), 3) for k in (3, 5, 10)}, "| rappel@5 :", pert[:5].sum() / 4, "| rang réciproque :", 1 / (1 + int(np.argmax(pert))))
```

### Corrigé 2.13

Le vocabulaire grandit **moins vite** que le nombre d'avis (200 formes à 100 avis, 659 à 8 000 : loi de Heaps). Sur ce corpus de gabarits, déjà normalisé, les minuscules et la racinisation ne le réduisent presque pas (659 → 655) ; sur un vrai corpus, l'écart serait bien plus grand. Dans une langue qui accole articles, conjonctions et pronoms aux mots, chaque mot de base apparaît sous de nombreuses formes de surface rares : la **courbe monte plus vite et ne se stabilise pas**, d'où un vocabulaire plus grand, davantage de mots inconnus, et la nécessité de normaliser ou de passer à des sous-mots.

```python
rng = np.random.default_rng(0)
ordre = rng.permutation(len(avis))
def croissance(f):
    sortie = {}
    for n in (100, 500, 2000, 8000):
        sortie[n] = len({f(w) for i in ordre[:n] for w in O.tokeniser(avis["texte"].iloc[i])})
    return sortie
print(pd.DataFrame({"formes de surface": croissance(lambda w: w), "minuscules": croissance(lambda w: w.lower()), "racinisation": croissance(racine)}).to_string())
```

### Corrigé 2.14

Avec **un** passage : $0{,}70\times0{,}9+0{,}30\times0{,}1=0{,}63+0{,}03=0{,}66$. Avec **trois** : le bon passage est dans le prompt dans $70+15=85$ cas : $0{,}85\times0{,}9+0{,}15\times0{,}1=0{,}765+0{,}015=0{,}78$. Fournir trop de passages est mauvais pour deux raisons : le **coût et la latence** augmentent avec la longueur du prompt (la fenêtre de contexte est limitée), et des passages non pertinents **distraient** le modèle et augmentent le risque de réponse fausse (hypothèse que l'on teste en mesurant la part de réponses justes en fonction de $k$).

```python
p1 = 0.70 * 0.9 + 0.30 * 0.1; p3 = 0.85 * 0.9 + 0.15 * 0.1
print("un passage :", round(p1, 3), "| trois passages :", round(p3, 3))
```
