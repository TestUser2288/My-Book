# Chapitre 7 : ➕ Systèmes de recommandation — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 7 du livre. Les **applications** reprennent, pas à pas et avec le code, ce que le livre a seulement résumé : la matrice d'interactions, les voisins, l'ALS écrit à la main, la factorisation sur les notes, les métriques, le démarrage à froid, le découpage temporel, la boucle de rétroaction et les compromis de diversité. Les **exercices** se travaillent d'abord à la main, puis se vérifient par le calcul. Données : `interactions.csv` et `produits_ml.csv` (boutique simulée). Prérequis : le chapitre 7 du livre et la section 1.1 sur la séparation des données.

## Préparation

Une seule cellule charge les bibliothèques et les fichiers ; les applications qui suivent s'en servent. Le **protocole d'évaluation** (découpage des achats en entraînement, validation et test, calcul des métriques) et les simulateurs sont fournis par le script `build/outils_ch07.py`, comme dans le livre.

| Fonction | Rôle |
|---|---|
| `charger()` | lit les fichiers et retourne les interactions, les produits et la matrice binaire clients × produits |
| `decouper(R, seed)` | retire ~25 % des achats de chaque client (test), puis ~20 % du reste (validation) |
| `evaluer(S, R_connu, cible, users, k)` | calcule précision, rappel, AP, NDCG et succès @k pour chaque client |
| `resume(df)`, `ic_bootstrap(v)` | moyennes, intervalle de confiance par bootstrap |
| `scores_*` | méthodes du livre (popularité, contenu, voisins, SVD, ALS), pour comparaison |
| `monde_en_derive()`, `boucle_retroaction()` | simulateurs des sections 7.4.3 et 7.4.6 |

```python
import sys
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
import scipy.sparse as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from outils_ch07 import *

inter, prod, R = charger()                      # R : matrice binaire clients x produits (creuse)
d = decouper(R, seed=7)                         # mêmes jeux qu'au livre
Rt, Rv, users = d["R_train"], d["val"], d["users"]
print(R.shape, int(R.nnz), "| clients évalués :", len(users), "| achats entraînement/validation/test :", Rt.nnz, int(Rv.nnz), int(d["test"].nnz))

def ndcg_moyen(S):                              # raccourci : NDCG@10 moyen sur la validation
    return evaluer(S, Rt, Rv, users)["ndcg"].mean()
```
<!--sortie-->
```text
(3000, 150) 27687 | clients évalués : 2365 | achats entraînement/validation/test : 17177 3987 6523
```

## Applications

### Application 7.1 — La matrice d'interactions, la popularité et le contenu à la main

*Sections du livre : 7.1.3 à 7.1.6.* **Objectif** : construire la matrice à partir du fichier d'achats, mesurer la longue traîne, écrire soi-même la popularité et le filtrage par contenu, et voir ce qui arrive quand on oublie de mettre le prix à la même échelle que les catégories.

**Étape 1 — De la table « un achat par ligne » à la matrice.**

```python
M = inter.groupby(["id_client", "id_produit"]).size().unstack(fill_value=0)
M = M.reindex(index=range(1, 3001), columns=range(1, 151), fill_value=0)       # clients sans achat inclus
print("identique à la matrice creuse :", np.array_equal((M.values > 0).astype(float), R.toarray()))
print("cases remplies :", int(R.nnz), "sur", R.shape[0] * R.shape[1], "| densité :", round(R.nnz / (R.shape[0] * R.shape[1]), 4))
par_produit = np.sort(np.asarray(R.sum(axis=0)).ravel())[::-1]
print("part des 10 produits les plus achetés :", round(par_produit[:10].sum() / R.nnz, 3), "| des 50 premiers :", round(par_produit[:50].sum() / R.nnz, 3))
```
<!--sortie-->
```text
identique à la matrice creuse : True
cases remplies : 27687 sur 450000 | densité : 0.0615
part des 10 produits les plus achetés : 0.211 | des 50 premiers : 0.629
```

**Lecture.** La table « un achat par ligne » et la matrice creuse contiennent exactement la même information. Les 10 produits les plus achetés concentrent 21,1 % des achats et les 50 premiers 62,9 % : c'est la longue traîne du livre, vue par un autre bout.

**Étape 2 — La popularité écrite à la main.** Un simple comptage des achats d'entraînement.

```python
achats = np.asarray(Rt.sum(axis=0)).ravel()
top = np.argsort(-achats)[:10]
print("10 produits les plus achetés (id) :", top + 1, "| acheteurs :", achats[top].astype(int))
print("catégories :", "".join(prod.categorie.values[top]))
r_pop = evaluer(scores_popularite(Rt), Rt, Rv, users)
print("rappel@10 :", round(r_pop.rappel.mean(), 4), "| NDCG@10 :", round(r_pop.ndcg.mean(), 4))
print("liste du client", users[0] + 1, ":", np.array(r_pop.recommandes.iloc[0]) + 1)
```
<!--sortie-->
```text
10 produits les plus achetés (id) : [ 29  48 121  69 116  50  15 137  11  44] | acheteurs : [652 509 396 390 339 312 290 287 277 271]
catégories : CBDCABADAC
rappel@10 : 0.2409 | NDCG@10 : 0.1431
liste du client 1 : [121  69 116  15 137  11  44  10  23  60]
```

**Lecture.** Les dix produits les plus achetés comptent de 271 à 652 acheteurs et couvrent les quatre catégories. La liste du premier client évalué ne contient pas les produits 29, 48 et 50 : il les a déjà achetés, et l'on ne recommande que ce qu'il ne connaît pas encore. Le rappel@10 (24,1 %) et le NDCG@10 (0,143) sont ceux du livre.

**Étape 3 — Le contenu, avec et sans mise à l'échelle du prix.**

```python
def contenu(R_, prix_mis_a_l_echelle=True, avec_prix=True):
    F = pd.get_dummies(prod.categorie, dtype=float).to_numpy()
    if avec_prix:
        p = np.log(prod.prix.to_numpy()) if prix_mis_a_l_echelle else prod.prix.to_numpy()       # sinon : prix brut en euros
        p = (p - p.mean()) / p.std() if prix_mis_a_l_echelle else p
        F = np.hstack([F, p[:, None]])
    n = np.asarray(R_.sum(axis=1)).ravel(); n[n == 0] = 1
    P = (R_ @ F) / n[:, None]                                          # profil : moyenne des produits achetés
    P = P / np.maximum(np.linalg.norm(P, axis=1, keepdims=True), 1e-12)
    return P @ (F / np.linalg.norm(F, axis=1, keepdims=True)).T         # cosinus profil / produit

print("même scores que le livre :", np.allclose(contenu(Rt), scores_contenu(Rt, prod)))
print("prix moyen du catalogue :", round(prod.prix.mean(), 2), "€ | corrélation prix-popularité :", round(np.corrcoef(prod.prix, achats)[0, 1], 3))
for nom, S in (("catégorie seule", contenu(Rt, avec_prix=False)), ("catégorie + prix standardisé", contenu(Rt)), ("catégorie + prix brut (en euros)", contenu(Rt, prix_mis_a_l_echelle=False))):
    r = evaluer(S, Rt, Rv, users)
    print(f"{nom:34s} NDCG@10 = {r.ndcg.mean():.4f} | prix moyen des produits recommandés : {prod.prix.values[np.vstack(r.recommandes.values)].mean():.1f} €")
```
<!--sortie-->
```text
même scores que le livre : True
prix moyen du catalogue : 30.44 € | corrélation prix-popularité : 0.085
catégorie seule                    NDCG@10 = 0.0538 | prix moyen des produits recommandés : 29.3 €
catégorie + prix standardisé       NDCG@10 = 0.0588 | prix moyen des produits recommandés : 31.4 €
catégorie + prix brut (en euros)   NDCG@10 = 0.0658 | prix moyen des produits recommandés : 52.8 €
```

**Lecture.** Les trois variantes ont des NDCG proches (0,054 ; 0,059 ; 0,066), très loin de la popularité (0,143). Le résultat surprenant est que la variante « mal mise à l'échelle », avec le prix brut en euros, obtient le **meilleur** score. L'explication se lit dans la dernière colonne : dominé par le prix, le cosinus recommande surtout des produits **chers** (52,8 € en moyenne, contre 30,4 € pour le catalogue), et comme les produits chers sont un tout petit peu plus achetés que les autres (corrélation prix-popularité de 0,085), le score en profite. Il ne s'agit donc pas d'une meilleure compréhension des goûts mais d'un **effet de popularité indirect**. Deux leçons : on ne juge jamais un modèle de contenu à son seul score, on regarde aussi **ce qu'il recommande** ; et ces écarts de l'ordre d'un à deux centièmes, donnés sans intervalle de confiance, se lisent avec prudence.

**Pour aller plus loin.** Remplacez la moyenne des vecteurs produits par une moyenne pondérée par `nb_achats` (colonne de `interactions.csv`) : le profil change-t-il beaucoup ?

### Application 7.2 — Les voisins de produits et de clients écrits à la main

*Sections du livre : 7.2.2 à 7.2.5.* **Objectif** : retrouver la similarité cosinus à partir des co-achats, écrire le score de voisinage avec rétrécissement, et explorer une variante de la similarité.

**Étape 1 — Co-achats et cosinus.**

```python
co = (Rt.T @ Rt).toarray()                     # co[i, j] : nombre de clients ayant acheté i et j
n = np.diag(co).copy()
S = co / np.sqrt(np.outer(n, n)); np.fill_diagonal(S, 0)
from sklearn.metrics.pairwise import cosine_similarity
S2 = cosine_similarity(Rt.T); np.fill_diagonal(S2, 0)
i, j = np.unravel_index(S.argmax(), S.shape)
print("identique à scikit-learn :", np.allclose(S, S2), "| paire la plus proche :", i + 1, j + 1, "cosinus", round(S.max(), 3), "co-achats", int(co[i, j]))
iu = np.triu_indices(150, 1)
print("co-achats par paire : médiane", int(np.median(co[iu])), "| maximum", int(co[iu].max()), "| paires à moins de 5 co-achats :", round((co[iu] < 5).mean(), 3))
```
<!--sortie-->
```text
identique à scikit-learn : True | paire la plus proche : 29 48 cosinus 0.231 co-achats 133
co-achats par paire : médiane 3 | maximum 133 | paires à moins de 5 co-achats : 0.646
```

**Lecture.** Notre cosinus est identique à celui de scikit-learn. La paire de produits la plus proche est (29, 48), les deux produits les plus achetés (133 co-achats), pour un cosinus de seulement 0,231. Les co-achats sont rares : médiane de 3 par paire, et 64,6 % des paires en ont moins de 5. C'est ce qui rend les similarités individuellement bruitées, et justifie le rétrécissement.

**Étape 2 — Le score de voisinage avec rétrécissement.**

```python
def voisins_produits(R_, k=149, lam=0.0):
    co = (R_.T @ R_).toarray(); n = np.diag(co)
    S = co / np.sqrt(np.outer(n, n))
    if lam > 0:
        S = S * co / (co + lam)                                 # rétrécissement n_ij / (n_ij + lambda)
    np.fill_diagonal(S, 0)
    if k < 149:
        seuil = -np.sort(-S, axis=1)[:, k - 1][:, None]; S = np.where(S >= seuil, S, 0)
    return np.asarray(R_ @ S)

print("même scores que le livre :", np.allclose(voisins_produits(Rt, 20, 10), scores_voisins_articles(Rt, 20, 10)))
grille = pd.DataFrame({f"k = {k}": {f"λ = {lam}": ndcg_moyen(voisins_produits(Rt, k, lam)) for lam in (0, 5, 20, 100)} for k in (5, 10, 50, 149)})
print(grille.round(4).to_string())
```
<!--sortie-->
```text
même scores que le livre : True
          k = 5  k = 10  k = 50  k = 149
λ = 0    0.1406  0.1526  0.1564   0.1584
λ = 5    0.1478  0.1534  0.1560   0.1576
λ = 20   0.1478  0.1534  0.1567   0.1570
λ = 100  0.1477  0.1508  0.1547   0.1547
```

**Lecture.** Avec 5 voisins, un rétrécissement de $\lambda=5$ fait passer le NDCG de 0,141 à 0,148 ; avec tous les voisins, il n'apporte rien (0,158 sans rétrécissement, 0,157 avec $\lambda=5$), et un rétrécissement fort ($\lambda=100$) fait même perdre un peu (0,155). Un $\lambda$ de 5 à 20 est donc une assurance peu coûteuse : elle aide quand le voisinage est étroit et ne coûte presque rien quand il est large.

**Étape 3 — Une variante : le cosinus asymétrique.** On remplace $\sqrt{n_in_j}$ par $n_i^\alpha n_j^{1-\alpha}$ ; $\alpha=0{,}5$ redonne le cosinus.

```python
def voisins_alpha(R_, alpha):
    co = (R_.T @ R_).toarray(); n = np.diag(co)
    S = co / np.outer(n ** alpha, n ** (1 - alpha)); np.fill_diagonal(S, 0)
    return np.asarray(R_ @ S)

print({a: round(float(ndcg_moyen(voisins_alpha(Rt, a))), 4) for a in (0.0, 0.25, 0.5, 0.75, 1.0)})
print("voisins de clients, k = 30, 100, 300, 1000 :", [round(float(ndcg_moyen(scores_voisins_clients(Rt, k))), 4) for k in (30, 100, 300, 1000)])
```
<!--sortie-->
```text
{0.0: 0.0333, 0.25: 0.115, 0.5: 0.1584, 0.75: 0.1604, 1.0: 0.1579}
voisins de clients, k = 30, 100, 300, 1000 : [0.1337, 0.1587, 0.1646, 0.1567]
```

**Lecture.** Le cosinus asymétrique avec $\alpha=0{,}75$ obtient 0,160 contre 0,158 pour le cosinus ($\alpha=0{,}5$) : un écart que la validation ne permet pas de distinguer du bruit. En revanche, les valeurs extrêmes sont catastrophiques ($\alpha=0$ : 0,033), car on ne normalise plus par la popularité des produits. Pour les voisins de clients, on retrouve les valeurs du livre : 0,134 ($k=30$), 0,159 (100), **0,165** (300) et 0,157 (1 000).

### Application 7.3 — L'ALS implicite écrit à la main

*Sections du livre : 7.3.3 à 7.3.7.* **Objectif** : programmer les moindres carrés alternés avec confiance, vérifier que l'objectif ne fait que baisser, puis explorer l'effet de la confiance $\alpha$, du nombre d'itérations et regarder les facteurs appris.

**Étape 1 — L'étape de mise à jour, puis la boucle.**

```python
def pas_als(A, F, lam=100.0, alpha=8.0):
    """Facteurs des lignes de A (creuse, binaire), les facteurs F de l'autre côté étant fixés."""
    k = F.shape[1]; FtF = F.T @ F + lam * np.eye(k)
    X = np.zeros((A.shape[0], k))
    for i in range(A.shape[0]):
        idx = A.indices[A.indptr[i]:A.indptr[i + 1]]                  # produits achetés par la ligne i
        if len(idx):
            Fi = F[idx]
            X[i] = np.linalg.solve(FtF + alpha * Fi.T @ Fi, (1 + alpha) * Fi.sum(axis=0))
    return X

def objectif(U, V, A, lam=100.0, alpha=8.0):
    X = A.toarray(); C = 1 + alpha * X
    return (C * (X - U @ V.T) ** 2).sum() + lam * ((U ** 2).sum() + (V ** 2).sum())
```

```python
rng = np.random.default_rng(0); k = 6
U = 0.1 * rng.standard_normal((Rt.shape[0], k)); V = 0.1 * rng.standard_normal((Rt.shape[1], k))
Rtt = Rt.T.tocsr(); suivi = []
for it in range(10):
    U = pas_als(Rt, V); V = pas_als(Rtt, U)
    suivi.append(objectif(U, V, Rt))
print("objectif après chaque itération :", np.round(suivi, 0))
print("il ne fait que baisser :", bool(np.all(np.diff(suivi) <= 1e-6)))
print("mêmes scores que le livre :", np.allclose(U @ V.T, scores_als(Rt, k=6, lam=100.0, alpha=8.0, n_iter=10, seed=0)))
```
<!--sortie-->
```text
objectif après chaque itération : [153830. 130128. 124731. 124472. 124308. 124212. 124156. 124122. 124102.
 124092.]
il ne fait que baisser : True
mêmes scores que le livre : True
```

**Lecture.** L'objectif passe de 153 830 à 124 092 en dix itérations et ne fait **que baisser**, comme le garantit la méthode ; les trois premières itérations font l'essentiel du travail (124 731 à la troisième). Nos scores sont identiques à ceux du livre.

**Étape 2 — La confiance $\alpha$ et le nombre d'itérations.**

```python
print("confiance α  :", {a: round(float(ndcg_moyen(scores_als(Rt, k=6, lam=100.0, alpha=a, n_iter=10))), 4) for a in (1, 4, 8, 16, 32)})
print("itérations   :", {t: round(float(ndcg_moyen(scores_als(Rt, k=6, lam=100.0, alpha=8.0, n_iter=t))), 4) for t in (1, 2, 3, 5, 10, 20)})
```
<!--sortie-->
```text
confiance α  : {1: 0.1397, 4: 0.1402, 8: 0.1681, 16: 0.1636, 32: 0.1529}
itérations   : {1: 0.0991, 2: 0.1431, 3: 0.1494, 5: 0.1575, 10: 0.1681, 20: 0.1685}
```

**Lecture.** La confiance $\alpha$ interagit avec la régularisation. Avec $\lambda=100$ fixé, $\alpha=8$ est le meilleur (0,168) ; avec $\alpha=1$ ou 4 la régularisation écrase les facteurs et le NDCG retombe au niveau de la popularité (0,140) ; avec $\alpha=32$, le modèle accorde trop de poids aux achats et surapprend (0,153). Côté itérations, une seule ne suffit pas (0,099), deux donnent 0,143, cinq 0,158, dix 0,168, et vingt n'apportent presque plus rien (0,1685) : la convergence est atteinte vers dix.

**Étape 3 — Les voisins d'un produit dans l'espace des facteurs.**

```python
Vf = V / np.linalg.norm(V, axis=1, keepdims=True)
sim_lat = Vf @ Vf.T; np.fill_diagonal(sim_lat, -1)
voisins = np.argsort(-sim_lat[0])[:5]
print("produit 1, catégorie", prod.categorie[0], "| ses 5 voisins :", voisins + 1, "catégories", "".join(prod.categorie.values[voisins]))
meme = np.mean([(prod.categorie.values[np.argsort(-sim_lat[i])[:5]] == prod.categorie[i]).mean() for i in range(150)])
print("part des 5 plus proches voisins de la même catégorie, en moyenne :", round(meme, 3), "| attendu au hasard :", round(((prod.categorie.value_counts() / 150) ** 2).sum(), 3))
```
<!--sortie-->
```text
produit 1, catégorie A | ses 5 voisins : [  5 103  31  43  21] catégories ABBBB
part des 5 plus proches voisins de la même catégorie, en moyenne : 0.86 | attendu au hasard : 0.258
```

**Lecture.** Dans l'espace complet des six facteurs, en moyenne **86 %** des cinq plus proches voisins d'un produit sont de sa catégorie, contre 26 % attendus au hasard : les facteurs ont retrouvé l'organisation du catalogue sans qu'on la leur donne. Le produit 1 est une exception instructive (un seul de ses cinq voisins est de la catégorie A) : les facteurs reflètent les **achats**, pas les étiquettes, et un produit peut très bien être acheté par le même public que ceux d'une autre catégorie.

**Pour aller plus loin.** Le livre a traité les achats comme un signal binaire. Remplacez la confiance $1+\alpha R_{ui}$ par $1+\alpha\ln(1+n_{ui})$, où $n_{ui}$ est la colonne `nb_achats` du fichier `interactions.csv` (un tiers des achats concernent plusieurs exemplaires) : la quantité achetée améliore-t-elle le NDCG ? Il faut pour cela construire une matrice de confiance creuse et adapter `pas_als`.

### Application 7.4 — La factorisation sur les notes explicites, par SGD

*Sections du livre : 7.3.2 et 7.3.3.* **Objectif** : prédire les **notes** (un quart des achats en a une) avec un modèle à biais et facteurs, appris par descente de gradient stochastique, et le comparer à des références. Ici l'objectif n'est plus un classement mais une erreur de prédiction (RMSE).

**Étape 1 — Jeu d'apprentissage, jeu de test, références.**

```python
notes = inter.dropna(subset=["note"])[["id_client", "id_produit", "note"]].reset_index(drop=True)
masque = np.random.default_rng(4).random(len(notes)) < 0.8
tr, te = notes[masque], notes[~masque]
mu = tr.note.mean()
rmse = lambda pred: float(np.sqrt(np.mean((te.note.values - pred) ** 2)))
bi = tr.assign(e=tr.note - mu).groupby("id_produit").e.agg(lambda s: s.sum() / (len(s) + 10))          # biais produit rétréci
bu = tr.assign(e=tr.note - mu - tr.id_produit.map(bi)).groupby("id_client").e.agg(lambda s: s.sum() / (len(s) + 10))
pred_biais = mu + te.id_produit.map(bi).fillna(0).values + te.id_client.map(bu).fillna(0).values
print(len(notes), "notes dont", len(te), "en test | moyenne", round(mu, 3))
print("RMSE moyenne globale :", round(rmse(mu), 3), "| modèle à biais :", round(rmse(pred_biais), 3))
```
<!--sortie-->
```text
6883 notes dont 1384 en test | moyenne 3.996
RMSE moyenne globale : 1.023 | modèle à biais : 0.97
```

**Lecture.** On dispose de 6 883 notes, dont 1 384 gardées pour le test. Prédire la moyenne globale (3,996) donne une RMSE de 1,023 ; le simple modèle à biais (produit et client, rétrécis) la ramène à 0,970, soit 5 % de moins.

**Étape 2 — SGD avec biais et facteurs.**

```python
def sgd_mf(k=8, lam=0.05, gamma=0.01, epochs=30, seed=0):
    rng = np.random.default_rng(seed)
    P = 0.1 * rng.standard_normal((3001, k)); Q = 0.1 * rng.standard_normal((151, k)); bu_ = np.zeros(3001); bi_ = np.zeros(151)
    u, i, r = tr.id_client.values, tr.id_produit.values, tr.note.values
    historique = []
    for ep in range(epochs):
        for t in rng.permutation(len(r)):
            a, b = u[t], i[t]
            e = r[t] - (mu + bu_[a] + bi_[b] + P[a] @ Q[b])
            bu_[a] += gamma * (e - lam * bu_[a]); bi_[b] += gamma * (e - lam * bi_[b])
            P[a], Q[b] = P[a] + gamma * (e * Q[b] - lam * P[a]), Q[b] + gamma * (e * P[a] - lam * Q[b])
        pred = np.clip(mu + bu_[te.id_client.values] + bi_[te.id_produit.values] + (P[te.id_client.values] * Q[te.id_produit.values]).sum(axis=1), 1, 5)
        historique.append(rmse(pred))
    return historique

h = sgd_mf()
print("RMSE de test après 1, 5, 10, 20, 30 époques :", [round(h[e - 1], 3) for e in (1, 5, 10, 20, 30)])
```
<!--sortie-->
```text
RMSE de test après 1, 5, 10, 20, 30 époques : [0.998, 0.977, 0.971, 0.972, 0.982]
```

**Lecture.** La RMSE de test descend de 0,998 (une époque) à 0,971 (dix époques), puis **remonte** (0,972 à vingt, 0,982 à trente) : le modèle commence à apprendre le bruit des notes d'entraînement. C'est le surapprentissage, visible sur une courbe, et la raison pour laquelle on arrête l'apprentissage sur la validation (arrêt précoce).

**Étape 3 — Régularisation.**

```python
for lam in (0.0, 0.05, 0.2, 0.5):
    h = sgd_mf(lam=lam, epochs=25)
    print(f"λ = {lam:4}: meilleure RMSE de test {min(h):.3f} (époque {int(np.argmin(h)) + 1}) | à l'époque 25 : {h[-1]:.3f}")
```
<!--sortie-->
```text
λ =  0.0: meilleure RMSE de test 0.971 (époque 12) | à l'époque 25 : 0.984
λ = 0.05: meilleure RMSE de test 0.970 (époque 13) | à l'époque 25 : 0.976
λ =  0.2: meilleure RMSE de test 0.968 (époque 16) | à l'époque 25 : 0.971
λ =  0.5: meilleure RMSE de test 0.970 (époque 16) | à l'époque 25 : 0.971
```

**Lecture.** Sans régularisation, la meilleure RMSE est de 0,971 (époque 12) mais elle se dégrade ensuite (0,984 à l'époque 25) ; avec $\lambda=0{,}2$, elle atteint 0,968 et **reste** à 0,971. La régularisation stabilise l'apprentissage. Mais le résultat principal est **négatif** : la meilleure factorisation (0,968) est à égalité avec le modèle à biais seul (0,970). Avec environ 5 500 notes d'entraînement pour 3 000 clients, les facteurs n'apportent rien de mesurable sur les biais. Ce n'est pas un échec de la méthode : sur les **achats**, où l'on dispose de 27 687 observations contre 6 883 notes (plus de quatre fois plus), les facteurs aident nettement.

### Application 7.5 — Les métriques et leurs intervalles de confiance, écrits à la main

*Sections du livre : 7.4.1 et 7.4.2.* **Objectif** : écrire les métriques de classement pour une liste, vérifier le résultat sur l'exemple du livre, puis comparer deux méthodes sur le **jeu de test** avec un intervalle de confiance apparié.

**Étape 1 — Les métriques pour une liste.**

```python
def metriques_liste(recommandes, pertinents, k=10):
    hits = np.isin(recommandes[:k], list(pertinents)).astype(float)
    rangs = np.arange(1, k + 1)
    n_rel = len(pertinents)
    ap = (hits * np.cumsum(hits) / rangs).sum() / min(n_rel, k)
    dcg = (hits / np.log2(rangs + 1)).sum()
    idcg = (1 / np.log2(np.arange(1, min(n_rel, k) + 1) + 1)).sum()
    return hits.sum() / k, hits.sum() / n_rel, ap, dcg / idcg

print("exemple du livre (précision, rappel, AP, NDCG) :", np.round(metriques_liste(np.array([7, 3, 9, 1, 4]), {3, 1, 12}, k=5), 4))
r = evaluer(scores_popularite(Rt), Rt, Rv, users)
cibles = [set(Rv.indices[Rv.indptr[u]:Rv.indptr[u + 1]]) for u in users[:200]]
mm = np.mean([metriques_liste(np.array(l), c) for l, c in zip(r.recommandes.iloc[:200], cibles)], axis=0)
print("moyenne de nos fonctions sur 200 clients :", mm.round(4))
print("moyenne de evaluer() sur les mêmes     :", r.iloc[:200][["precision", "rappel", "ap", "ndcg"]].mean().values.round(4))
```
<!--sortie-->
```text
exemple du livre (précision, rappel, AP, NDCG) : [0.4    0.6667 0.3333 0.4982]
moyenne de nos fonctions sur 200 clients : [0.0395 0.2492 0.0934 0.1434]
moyenne de evaluer() sur les mêmes     : [0.0395 0.2492 0.0934 0.1434]
```

**Lecture.** Nos fonctions redonnent l'exemple du livre (précision 0,4 ; rappel 0,667 ; AP 0,333 ; NDCG 0,498) et la même moyenne que `evaluer()` sur 200 clients (précision 0,0395, rappel 0,2492, AP 0,0934, NDCG 0,1434).

**Étape 2 — Comparaison sur le jeu de test avec un intervalle de confiance apparié.** Les modèles sont réentraînés sur l'entraînement **et** la validation, avec les hyperparamètres choisis en validation.

```python
Rtv, T = d["R_trainval"], d["test"]
res_als = evaluer(scores_als(Rtv, k=6, lam=100.0, alpha=8.0, n_iter=10), Rtv, T, users)
res_cli = evaluer(scores_voisins_clients(Rtv, 300), Rtv, T, users)
res_pop = evaluer(scores_popularite(Rtv), Rtv, T, users)
def ic_apparie(a, b, col="ndcg"):
    delta = a[col].values - b[col].values
    return round(delta.mean(), 4), np.round(ic_bootstrap(delta), 4)
print("ALS − voisins de clients :", [round(float(v), 4) for v in (ic_apparie(res_als, res_cli)[0], *ic_apparie(res_als, res_cli)[1])], "(écart, borne basse, borne haute)")
print("ALS − popularité         :", [round(float(v), 4) for v in (ic_apparie(res_als, res_pop)[0], *ic_apparie(res_als, res_pop)[1])])
print("rappel@10 : ALS", round(res_als.rappel.mean(), 3), "| voisins de clients", round(res_cli.rappel.mean(), 3), "| popularité", round(res_pop.rappel.mean(), 3))
```
<!--sortie-->
```text
ALS − voisins de clients : [0.0068, 0.0022, 0.011] (écart, borne basse, borne haute)
ALS − popularité         : [0.042, 0.0357, 0.0481]
rappel@10 : ALS 0.295 | voisins de clients 0.288 | popularité 0.244
```

**Lecture.** Sur le jeu de test, l'ALS dépasse la popularité de 0,042 de NDCG (intervalle [0,036 ; 0,048]) et les voisins de clients de 0,0068 (intervalle [0,002 ; 0,011], qui exclut zéro de justesse), comme dans le livre.

**Étape 3 — Le choix de $k$ pour l'évaluation.**

```python
S_als, S_pop = scores_als(Rtv, k=6, lam=100.0, alpha=8.0, n_iter=10), scores_popularite(Rtv)
for k_eval in (1, 3, 5, 10, 20):
    a = resume(evaluer(S_als, Rtv, T, users, k=k_eval)); p = resume(evaluer(S_pop, Rtv, T, users, k=k_eval))
    print(f"@{k_eval:<3d} rappel ALS {a.rappel:.3f} vs popularité {p.rappel:.3f} | NDCG ALS {a.ndcg:.3f} vs popularité {p.ndcg:.3f}")
```
<!--sortie-->
```text
@1   rappel ALS 0.060 vs popularité 0.047 | NDCG ALS 0.176 vs popularité 0.142
@3   rappel ALS 0.132 vs popularité 0.109 | NDCG ALS 0.155 vs popularité 0.124
@5   rappel ALS 0.186 vs popularité 0.153 | NDCG ALS 0.171 vs popularité 0.137
@10  rappel ALS 0.295 vs popularité 0.244 | NDCG ALS 0.216 vs popularité 0.174
@20  rappel ALS 0.437 vs popularité 0.394 | NDCG ALS 0.265 vs popularité 0.225
```

**Lecture.** L'avantage **relatif** de l'ALS sur la popularité fond quand la liste s'allonge : le rapport des rappels vaut 1,28 pour $k=1$ (0,060 contre 0,047), 1,21 pour $k=10$ et 1,11 pour $k=20$ (0,437 contre 0,394). Avec une longue liste, tout le monde finit par retrouver les produits populaires. Le $k$ de l'évaluation doit donc refléter l'usage réel (une bannière, une vitrine de cinq, un défilement).

### Application 7.6 — Le démarrage à froid

*Section du livre : 7.4.5.* **Objectif** : refaire l'expérience du nouveau client avec un « fold-in », la compléter par un hybride qui mélange popularité et personnalisation tant que l'on connaît peu d'achats, puis explorer les variantes du contenu pour un nouveau produit.

**Étape 1 — Mise en place : clients « froids » et modèles entraînés sans eux.**

```python
rng = np.random.default_rng(21)
Rc = R.tocsr(); nb = np.asarray(Rc.sum(axis=1)).ravel()
eligibles = np.where(nb >= 11)[0]
froids = np.sort(rng.choice(eligibles, len(eligibles) // 4, replace=False))
R_tr = Rc.tolil(); R_tr[froids, :] = 0; R_tr = R_tr.tocsr(); R_tr.eliminate_zeros()
S_it = cosinus_colonnes(R_tr)                                          # similarités entre produits
U_f, V_f = als_implicite(R_tr, k=6, lam=100.0, alpha=8.0, n_iter=10, seed=0)
pop_tr = scores_popularite(R_tr)[0]
print(len(eligibles), "clients à 11 achats ou plus ;", len(froids), "simulés comme nouveaux")
```
<!--sortie-->
```text
1000 clients à 11 achats ou plus ; 250 simulés comme nouveaux
```

**Étape 2 — La courbe, avec un hybride.** On mélange les scores normalisés : $(1-w)\,\text{popularité}+w\,\text{personnalisé}$, avec $w=m/(m+c)$ qui croît avec le nombre $m$ d'achats connus ($c=3$).

```python
def normalise(S):
    return S / np.maximum(S.max(axis=1, keepdims=True), 1e-12)

def courbe(m, rng_loc):
    L_r, C_r, L_c, C_c = [], [], [], []
    S_p, S_i, S_a, S_h = (np.zeros((3000, 150)) for _ in range(4))
    for u in froids:
        items = rng_loc.permutation(Rc.indices[Rc.indptr[u]:Rc.indptr[u + 1]])
        vus, cibles = items[:m], items[m:]
        L_r += [u] * len(vus); C_r += list(vus); L_c += [u] * len(cibles); C_c += list(cibles)
        S_p[u] = pop_tr
        S_i[u] = S_it[vus].sum(axis=0) if m else pop_tr
        S_a[u] = vecteur_client(V_f, vus, lam=100.0, alpha=8.0) @ V_f.T if m else pop_tr
        w = m / (m + 3)
        S_h[u] = (1 - w) * normalise(pop_tr[None, :])[0] + w * normalise(S_a[u][None, :])[0]
    A = sp.csr_matrix((np.ones(len(C_r)), (L_r, C_r)), shape=(3000, 150)); B = sp.csr_matrix((np.ones(len(C_c)), (L_c, C_c)), shape=(3000, 150))
    return [evaluer(S, A, B, froids)["rappel"].mean() for S in (S_p, S_i, S_a, S_h)]

res = pd.DataFrame({m: courbe(m, np.random.default_rng(100 + m)) for m in (0, 1, 2, 3, 5, 8)}, index=["popularité", "voisins de produits", "ALS (fold-in)", "hybride"]).T
print(res.round(3).to_string())
```
<!--sortie-->
```text
   popularité  voisins de produits  ALS (fold-in)  hybride
0       0.198                0.198          0.198    0.198
1       0.203                0.204          0.212    0.221
2       0.203                0.226          0.232    0.227
3       0.213                0.259          0.259    0.248
5       0.214                0.259          0.268    0.254
8       0.223                0.290          0.285    0.269
```

**Lecture.** Sans achat connu, les quatre méthodes sont à égalité (19,8 %). Avec **un** achat, l'hybride (22,1 %) devance l'ALS (21,2 %) et la popularité (20,3 %) ; dès **deux** achats, l'ALS repasse devant (23,2 % contre 22,7 %) et à huit achats elle est nettement meilleure que l'hybride (28,5 % contre 26,9 %). Le poids $w=m/(m+3)$ est trop prudent : il ne sert qu'au tout début. Ces chiffres diffèrent un peu de ceux du livre (par exemple 23,2 % au lieu de 24,0 % pour l'ALS à deux achats) parce que les achats révélés sont tirés avec d'autres graines : avec 250 clients, des écarts d'un point sont dans le bruit.

**Étape 3 — Un nouveau produit : quel contenu ?** Les 26 produits récents sont retirés ; on les classe pour chaque client qui en a acheté, à partir de ses autres achats.

```python
nouv = np.where(prod.nouveaute.values == 1)[0]; anciens = np.where(prod.nouveaute.values == 0)[0]
cat = pd.get_dummies(prod.categorie, dtype=float).to_numpy()
lp = np.log(prod.prix.values); prix_z = ((lp - lp.mean()) / lp.std())[:, None]
Rn = Rc[:, nouv].toarray() > 0; Ra = Rc[:, anciens]
cibles_u = np.where(Rn.sum(axis=1) >= 1)[0]; Y = Rn[cibles_u]

def scores_nouveaux(F):
    n = np.asarray(Ra.sum(axis=1)).ravel(); n[n == 0] = 1
    P = (Ra @ F[anciens]) / n[:, None]
    P = P / np.maximum(np.linalg.norm(P, axis=1, keepdims=True), 1e-12)
    Fn = F[nouv] / np.maximum(np.linalg.norm(F[nouv], axis=1, keepdims=True), 1e-12)
    return (P @ Fn.T)[cibles_u]
```

On mesure ensuite, pour chaque client, le **rappel@5** parmi les 26 produits récents et l'**AUC** (probabilité qu'un produit réellement acheté soit classé devant un produit non acheté), puis on compare quatre jeux de caractéristiques.

```python
def rappel_auc(S, Y, k=5):
    rec, auc = [], []
    for s, y in zip(S, Y):
        rec.append(y[np.argsort(-s, kind="stable")[:k]].sum() / y.sum())
        pos, neg = s[y], s[~y]
        auc.append((pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean() if len(neg) else np.nan)
    return round(np.mean(rec), 3), round(np.nanmean(auc), 3)

variantes = {"catégorie seule": cat, "prix seul": prix_z, "catégorie + prix": np.hstack([cat, prix_z]), "catégorie × 2 + prix": np.hstack([2 * cat, prix_z])}
for nom, F in variantes.items():
    rec_, auc_ = rappel_auc(scores_nouveaux(F), Y)
    print(f"{nom:22s} rappel@5 = {float(rec_):.3f} | AUC = {float(auc_):.3f}")
print("hasard : rappel@5 =", round(5 / 26, 3), "| AUC = 0,5")
```
<!--sortie-->
```text
catégorie seule        rappel@5 = 0.296 | AUC = 0.617
prix seul              rappel@5 = 0.150 | AUC = 0.493
catégorie + prix       rappel@5 = 0.290 | AUC = 0.592
catégorie × 2 + prix   rappel@5 = 0.307 | AUC = 0.613
hasard : rappel@5 = 0.192 | AUC = 0,5
```

**Lecture.** La catégorie seule retrouve 29,6 % des achats (AUC de 0,617) contre 19,2 % pour le hasard. Le **prix seul** ne vaut rien : 15,0 % (AUC de 0,493), en dessous du hasard, ce qui est cohérent avec des données où le prix n'est lié à aucun goût. Donner plus de poids à la catégorie (30,7 %) améliore légèrement, d'un point que nous ne saurions distinguer du bruit.

### Application 7.7 — Découpage aléatoire contre découpage temporel

*Section du livre : 7.4.3.* **Objectif** : refaire la simulation du livre en faisant varier **le nombre de produits dont la popularité change** entre les deux périodes, et mesurer l'inflation des résultats par le découpage aléatoire.

```python
def inflation(n_bouge, seed=11):
    R1, R2 = monde_en_derive(n_bouge=n_bouge, seed=seed)
    Rall = ((R1 + R2) > 0).astype(float).tocsr()
    ds = decouper(Rall, seed=3, part_test=0.25, part_val=0.0001)
    T2 = (R2 - R2.multiply(R1)).tocsr(); T2.eliminate_zeros()
    us2 = np.where(np.asarray(T2.sum(axis=1)).ravel() >= 1)[0]
    out = {}
    for nom, f in (("popularité", scores_popularite), ("ALS", lambda X: scores_als(X, k=4, lam=30.0, alpha=8.0, n_iter=8))):
        alea = resume(evaluer(f(ds["R_trainval"]), ds["R_trainval"], ds["test"], ds["users"])).rappel
        temps = resume(evaluer(f(R1.tocsr()), R1.tocsr(), T2, us2)).rappel
        out[nom] = (alea, temps, alea / temps)
    return out

lignes = []
for nb_ in (0, 10, 30, 60):
    o = inflation(nb_)
    lignes.append({"produits qui changent": nb_, **{f"{nom} {c}": v for nom, t in o.items() for c, v in zip(("aléatoire", "temporel", "rapport"), t)}})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
 produits qui changent  popularité aléatoire  popularité temporel  popularité rapport  ALS aléatoire  ALS temporel  ALS rapport
                     0                 0.288                0.263               1.097          0.355         0.301        1.182
                    10                 0.306                0.216               1.417          0.371         0.281        1.318
                    30                 0.328                0.221               1.483          0.398         0.260        1.531
                    60                 0.353                0.248               1.425          0.412         0.251        1.644
```

**Lecture.** Même **sans aucun changement** de popularité, le découpage aléatoire donne des résultats supérieurs de 10 % (popularité, 0,288 contre 0,263) à 18 % (ALS, 0,355 contre 0,301) : cet écart ne vient pas de la dérive mais de la définition même des deux protocoles (voir le corrigé 7.12). Quand la popularité change, l'écart grimpe à 1,3 à 1,6 fois : 1,42, 1,48 et 1,43 pour la popularité avec 10, 30 et 60 produits qui changent, 1,32, 1,53 et 1,64 pour l'ALS, plus sensible. Le rapport de la popularité n'est pas monotone : c'est une simulation unique, à lire comme un ordre de grandeur.

**Pour aller plus loin.** Le rapport « aléatoire / temporel » reste supérieur à 1 même sans changement de popularité : pourquoi ? (Indice : dans le découpage temporel, on ne teste que sur des produits **nouveaux pour le client** ; dans le découpage aléatoire, un client peut avoir, dans l'entraînement, des achats de la seconde période.)

### Application 7.8 — La boucle de rétroaction

*Section du livre : 7.4.6.* **Objectif** : explorer le simulateur : quelle quantité d'exploration, quelle taille de vitrine, quelle règle de classement ?

**Étape 1 — Exploration et règle de classement.**

```python
def final(eps, taux, vitrine=5, graines=range(4)):
    moy = np.mean([boucle_retroaction(eps, taux, vitrine=vitrine, seed=s).iloc[-1][["part_top5", "produits_achetes", "correlation_vrai", "bons_en_vitrine"]].astype(float).values for s in graines], axis=0)
    return moy

lignes = []
for taux in (False, True):
    for eps in (0.0, 0.05, 0.1, 0.2, 0.5):
        m = final(eps, taux)
        lignes.append({"classement": "taux d'achat" if taux else "ventes", "exploration": eps, "part top 5": m[0], "produits achetés": m[1], "corrélation": m[2], "bons en vitrine": m[3]})
print(pd.DataFrame(lignes).round(2).to_string(index=False))
```
<!--sortie-->
```text
  classement  exploration  part top 5  produits achetés  corrélation  bons en vitrine
      ventes         0.00        0.96             48.00         0.78             0.25
      ventes         0.05        0.91             55.75         0.80             0.25
      ventes         0.10        0.87             59.25         0.80             0.25
      ventes         0.20        0.78             60.00         0.81             0.25
      ventes         0.50        0.53             60.00         0.84             0.50
taux d'achat         0.00        0.79             46.25         0.99             5.00
taux d'achat         0.05        0.83             55.75         0.97             4.75
taux d'achat         0.10        0.85             59.25         0.94             5.00
taux d'achat         0.20        0.82             60.00         0.95             4.50
taux d'achat         0.50        0.66             60.00         0.98             5.00
```

**Lecture.** Avec le classement par **ventes**, la vitrine ne contient presque jamais les bons produits (0,25 des 5 meilleurs, 0,5 avec 50 % d'exploration) et la corrélation avec l'attrait réel reste entre 0,78 et 0,84 ; l'exploration, elle, répartit les achats (48 produits achetés sans exploration, 60 avec 20 %) et fait chuter la concentration (de 96 % à 53 % des achats sur cinq produits). Avec le classement par **taux d'achat**, la vitrine contient de 4,5 à 5 des 5 meilleurs produits et la corrélation est de 0,94 à 0,99 quelle que soit l'exploration. L'exploration répartit les ventes ; c'est la **règle de classement** qui rétablit la lecture des goûts.

**Étape 2 — La taille de la vitrine.**

```python
for v in (3, 5, 10):
    for nom, (e, t) in {"ventes seules": (0.0, False), "taux d'achat + 20 % de hasard": (0.2, True)}.items():
        m = final(e, t, vitrine=v)
        print(f"vitrine de {v:2d} produits, {nom:30s}: corrélation {float(m[2]):.2f} | bons produits parmi les 5 premiers du classement {float(m[3]):.2f}")
```
<!--sortie-->
```text
vitrine de  3 produits, ventes seules                 : corrélation 0.88 | bons produits parmi les 5 premiers du classement 2.25
vitrine de  3 produits, taux d'achat + 20 % de hasard : corrélation 0.96 | bons produits parmi les 5 premiers du classement 4.00
vitrine de  5 produits, ventes seules                 : corrélation 0.78 | bons produits parmi les 5 premiers du classement 0.25
vitrine de  5 produits, taux d'achat + 20 % de hasard : corrélation 0.95 | bons produits parmi les 5 premiers du classement 4.50
vitrine de 10 produits, ventes seules                 : corrélation 0.65 | bons produits parmi les 5 premiers du classement 0.75
vitrine de 10 produits, taux d'achat + 20 % de hasard : corrélation 0.96 | bons produits parmi les 5 premiers du classement 5.00
```

**Lecture.** Plus la vitrine est grande, plus la lecture des ventes est biaisée : la corrélation avec l'attrait réel passe de 0,88 (3 produits) à 0,78 (5) puis 0,65 (10), parce que davantage de produits profitent de l'exposition. Le classement par taux d'achat, lui, reste à 0,95 ou 0,96 et trouve les cinq meilleurs produits avec une vitrine de dix.

### Application 7.9 — Mélanger les méthodes, et diversifier

*Sections du livre : 7.4.4.* **Objectif** : mélanger la popularité et l'ALS, puis réordonner les listes pour augmenter la diversité des catégories, et mesurer ce que l'on gagne et ce que l'on perd.

**Étape 1 — Un mélange des scores.**

```python
def couverture(df):
    return len(np.unique(np.vstack(df["recommandes"].values))) / 150

S_pop, S_als = normalise(scores_popularite(Rt)), normalise(scores_als(Rt, k=6, lam=100.0, alpha=8.0, n_iter=10))
lignes = []
for w in (0.0, 0.25, 0.5, 0.75, 1.0):
    r = evaluer((1 - w) * S_pop + w * S_als, Rt, Rv, users)
    lignes.append({"poids de l'ALS": w, "NDCG@10": r.ndcg.mean(), "rappel@10": r.rappel.mean(), "couverture": couverture(r)})
print(pd.DataFrame(lignes).round(4).to_string(index=False))
```
<!--sortie-->
```text
 poids de l'ALS  NDCG@10  rappel@10  couverture
           0.00   0.1431     0.2409      0.1400
           0.25   0.1508     0.2551      0.1467
           0.50   0.1571     0.2658      0.2000
           0.75   0.1645     0.2732      0.2533
           1.00   0.1681     0.2761      0.2800
```

**Lecture.** Le NDCG augmente régulièrement avec le poids de l'ALS (de 0,143 pour la popularité à 0,168 pour l'ALS seul), et la couverture aussi (de 14 % à 28 %). Sur ce jeu, **aucun mélange ne fait mieux que l'ALS seul** : l'hybride n'apporte rien. Il serait utile si le modèle personnalisé était instable, par exemple avec très peu de données.

**Étape 2 — Réordonner pour la diversité.** On construit chaque liste de façon gloutonne parmi les 30 meilleurs candidats : à chaque pas, on retire $\mu$ au score d'un candidat pour chaque produit **déjà choisi de la même catégorie**.

```python
cat_ = prod.categorie.values
def diversifier(S, mu):
    S2 = np.full_like(S, -1.0)
    for u in users:
        cand = list(np.argsort(-np.where(np.asarray(Rt[u].todense()).ravel() > 0, -np.inf, S[u]))[:30])
        choisis = []
        for rang in range(10):
            pen = [S[u, c] - mu * sum(cat_[c] == cat_[x] for x in choisis) for c in cand]
            c = cand.pop(int(np.argmax(pen))); choisis.append(c); S2[u, c] = 100 - rang
    return S2

S_base = 0.5 * S_pop + 0.5 * S_als
lignes = []
for mu in (0.0, 0.05, 0.1, 0.2):
    r = evaluer(diversifier(S_base, mu), Rt, Rv, users)
    L = np.vstack(r.recommandes.values)
    div = np.mean([np.mean([cat_[a] != cat_[b] for ia, a in enumerate(row) for b in row[ia + 1:]]) for row in L])
    lignes.append({"pénalité μ": mu, "NDCG@10": r.ndcg.mean(), "rappel@10": r.rappel.mean(), "diversité": div, "couverture": couverture(r)})
print(pd.DataFrame(lignes).round(4).to_string(index=False))
```
<!--sortie-->
```text
 pénalité μ  NDCG@10  rappel@10  diversité  couverture
       0.00   0.1571     0.2658     0.7879      0.2000
       0.05   0.1556     0.2641     0.8166      0.1933
       0.10   0.1551     0.2627     0.8208      0.2000
       0.20   0.1543     0.2625     0.8221      0.2000
```

**Lecture.** Pénaliser les doublons de catégorie fait passer la diversité de 0,788 à 0,822 (+0,034) pour une perte de 0,003 de NDCG (0,157 à 0,154) et de 0,003 de rappel : un coût faible pour un gain modeste. La couverture ne bouge pas (0,20), car on ne réordonne que les 30 meilleurs candidats : pour couvrir plus de produits, il faut élargir l'ensemble de candidats.

## Exercices

### Exercice 7.1 ⭐ — Cosinus et Jaccard à la main (section 7.1.4)

On reprend la matrice de 5 clients et 6 produits du livre (U1 : P1, P2, P4 ; U2 : P1, P3, P4 ; U3 : P2, P3, P4, P5 ; U4 : P1, P2, P6 ; U5 : P1, P3, P4, P5). (a) Calculez le cosinus et l'indice de Jaccard des produits P1 et P2. (b) Parmi les produits P1 à P5, quelle paire a le cosinus le plus élevé ? (c) Pourquoi le cosinus de P5 et P6 vaut-il 0, et que vaudrait celui de la corrélation de Pearson ?

### Exercice 7.2 ⭐ — Popularité et contenu pour un petit client (sections 7.1.5 et 7.1.6)

(a) Dans la même matrice, quels produits la popularité recommande-t-elle au client U4, dans quel ordre ? (b) Quatre produits ont pour caractéristiques $(\text{cat. A},\text{cat. B},\text{prix en dizaines d'euros})$ : P1 $=(1,0,2)$, P2 $=(1,0,3)$, P3 $=(0,1,2{,}5)$, P4 $=(1,0,2{,}5)$. Un client a acheté P1 et P2. Mettez le prix à l'échelle (centré, réduit sur ces quatre produits) et recalculez les cosinus avec P3 et P4. Que constatez-vous par rapport au livre ?

### Exercice 7.3 ⭐⭐ — Pourquoi stocker en format creux (section 7.1.3)

La matrice de la boutique a 3 000 lignes, 150 colonnes et 27 687 cases remplies. (a) Quelle mémoire occupe-t-elle en tableau dense de flottants de 8 octets, et en format creux CSR (8 octets par valeur, 4 par indice de colonne, 4 par pointeur de ligne) ? (b) Même question pour un site de 1 million de clients et 10 000 produits, à 10 achats par client en moyenne.

### Exercice 7.4 ⭐ — Voisins de produits pour U4 (section 7.2.3)

Toujours sur la même matrice : calculez à la main le score de voisinage $\hat s_{uj}=\sum_{i\in I_u}\cos(i,j)$ du client U4 (qui a acheté P1, P2 et P6) pour les candidats P3, P4 et P5. Quel classement obtenez-vous ? Est-il identique à celui de la popularité ?

### Exercice 7.5 ⭐⭐ — Le rétrécissement renverse un classement (section 7.2.4)

Trois paires de produits ont pour (cosinus ; co-achats) : $a=(0{,}9\ ;\ 3)$, $b=(0{,}5\ ;\ 30)$, $c=(0{,}7\ ;\ 12)$. (a) Classez-les avant rétrécissement. (b) Appliquez $\operatorname{sim}'=\operatorname{sim}\times n_{ij}/(n_{ij}+\lambda)$ avec $\lambda=10$ et reclassez. (c) Pour quelle valeur de $\lambda$ les paires $b$ et $c$ échangent-elles leur rang ?

### Exercice 7.6 ⭐⭐ — Prédire une note avec les voisins (section 7.2.2)

Avec le tableau de notes du livre (clients $u_1$ à $u_4$, produits A à D), prédisez la note de $u_1$ pour D en ne gardant que les voisins de **similarité positive**. Comparez avec la prédiction obtenue avec les trois voisins (4,43).

### Exercice 7.7 ⭐⭐ — Une étape d'ALS à la main (section 7.3.4)

Dans l'exemple $4\times4$ de la section 7.3.4, on a trouvé après l'étape des produits $q\approx(1{,}652\ ;\ 0{,}715\ ;\ 1{,}724\ ;\ 1{,}249)$. Avec $\lambda=1$, recalculez à la main le facteur du client 2 (qui a noté P1 $=4$ et P4 $=1$), puis le facteur du client 1 (P1 $=5$, P2 $=3$, P4 $=1$).

### Exercice 7.8 ⭐⭐⭐ — L'astuce de calcul de l'ALS implicite (section 7.3.5)

Soit $C_u$ la matrice diagonale de confiance du client $u$, de coefficients $c_{ui}=1+\alpha R_{ui}$. (a) Montrez que $Q^\top C_uQ=Q^\top Q+\alpha\,Q_u^\top Q_u$, où $Q_u$ regroupe les lignes de $Q$ des produits achetés par $u$. (b) Comparez le nombre d'opérations pour le calcul direct et pour l'astuce, en fonction du nombre de produits $m$, du nombre $d_u$ d'achats du client et du nombre de facteurs $k$.

### Exercice 7.9 ⭐⭐ — Un pas de gradient stochastique (section 7.3.3)

On a $p_u=(0{,}5\ ;\ 0{,}2)$, $q_i=(0{,}4\ ;\ 0{,}6)$, une note $r_{ui}=4$, un pas $\gamma=0{,}1$ et $\lambda=0{,}02$. Calculez l'erreur, puis les nouvelles valeurs de $p_u$ et $q_i$ (en utilisant les anciennes valeurs pour les deux mises à jour), et la nouvelle prédiction. L'erreur a-t-elle diminué ?

### Exercice 7.10 ⭐ — Les cinq métriques pour une liste de dix (section 7.4.1)

Une liste de $k=10$ produits a la pertinence $(1,0,0,1,0,0,0,1,0,0)$ ; le client avait en tout 4 produits pertinents dans le jeu de test. Calculez précision@10, rappel@10, succès@10, AP@10 et NDCG@10.

### Exercice 7.11 ⭐⭐ — Quand les métriques ne s'accordent pas (section 7.4.1)

Un client a 3 produits pertinents. La liste A de 5 produits a la pertinence $(1,0,0,0,0)$ ; la liste B a $(0,0,1,1,1)$. Calculez pour chacune précision@5, rappel@5, AP@5 et NDCG@5, ainsi que « le premier produit est-il pertinent ? ». Quelle liste est la meilleure ? Dans quel usage choisiriez-vous l'autre ?

### Exercice 7.12 ⭐⭐⭐ — Sans dérive, le découpage aléatoire est-il innocent ? (sections 7.4.3 et 7.4.6)

(a) Avec `monde_en_derive(n_bouge=0)`, comparez le rappel@10 de la popularité en découpage aléatoire et en découpage temporel. Le rapport vaut-il 1 ? (b) Expliquez en deux phrases le mécanisme qui reste. (c) Dans la boucle de rétroaction, pourquoi « ventes + 20 % d'exploration » ne change-t-il pas le nombre de bons produits en vitrine ?

## Corrigés

### Corrigé 7.1

(a) P1 est acheté par U1, U2, U4, U5 ($n_1=4$) ; P2 par U1, U3, U4 ($n_2=3$) ; les deux par U1 et U4 ($n_{12}=2$). Cosinus : $2/\sqrt{4\times3}=2/\sqrt{12}\approx0{,}577$ ; Jaccard : $2/(4+3-2)=0{,}4$. (b) On calcule tous les cosinus par $n_{ij}/\sqrt{n_in_j}$ ; le plus élevé est celui de **P3 et P4** ($n_3=3$, $n_4=4$, $n_{34}=3$ : $3/\sqrt{12}\approx0{,}866$). (c) P5 et P6 n'ont aucun acheteur commun, donc le produit scalaire est nul. La corrélation de Pearson, qui centre les vecteurs sur leur moyenne, vaut au contraire $-0{,}41$ : elle lit l'absence d'achat commun comme une **opposition** (les deux produits ne sont jamais achetés ensemble, alors que chacun l'est par d'autres clients). Le cosinus dit « aucun lien », la corrélation dit « lien négatif » ; pour recommander, « aucun lien » est la lecture utile.

```python
M = np.array([[1, 1, 0, 1, 0, 0], [1, 0, 1, 1, 0, 0], [0, 1, 1, 1, 1, 0], [1, 1, 0, 0, 0, 1], [1, 0, 1, 1, 1, 0]], float)
n = M.sum(axis=0); cos = (M.T @ M) / np.sqrt(np.outer(n, n)); np.fill_diagonal(cos, 0)
print("cos(P1,P2) =", cos[0, 1].round(3), "| Jaccard =", (M[:, 0] @ M[:, 1]) / (n[0] + n[1] - M[:, 0] @ M[:, 1]))
i, j = np.unravel_index(cos[:5, :5].argmax(), (5, 5)); print("paire la plus proche parmi P1..P5 :", i + 1, j + 1, cos[i, j].round(3))
print("corrélation de Pearson P5-P6 :", np.corrcoef(M[:, 4], M[:, 5])[0, 1].round(3))
```
<!--sortie-->
```text
cos(P1,P2) = 0.577 | Jaccard = 0.4
paire la plus proche parmi P1..P5 : 3 4 0.866
corrélation de Pearson P5-P6 : -0.408
```

### Corrigé 7.2

(a) U4 a acheté P1, P2, P6 ; il reste P3 (3 acheteurs), P4 (4) et P5 (2). La popularité recommande donc **P4, puis P3, puis P5**. (b) Prix en dizaines d'euros : $(2;\,3;\,2{,}5;\,2{,}5)$, moyenne $2{,}5$, variance $(0{,}25+0{,}25+0+0)/4=0{,}125$ et écart-type $\sqrt{0{,}125}\approx0{,}354$ ; prix centrés réduits : $(-1{,}414;\ +1{,}414;\ 0;\ 0)$. Les vecteurs deviennent P1 $=(1,0,-1{,}414)$, P2 $=(1,0,+1{,}414)$, P3 $=(0,1,0)$, P4 $=(1,0,0)$. Profil du client : $(1,0,0)$. Cosinus avec P4 : $1$ ; avec P3 : $0$. **La mise à l'échelle a rétabli la hiérarchie** : sans elle, P3 obtenait 0,862 (le prix dominait) ; avec elle, un produit d'une autre catégorie n'a plus aucune ressemblance avec le profil.

```python
prix = np.array([2, 3, 2.5, 2.5]); z = (prix - prix.mean()) / prix.std()
F = np.array([[1, 0, z[0]], [1, 0, z[1]], [0, 1, z[2]], [1, 0, z[3]]]); profil = F[:2].mean(axis=0)
c = lambda a, b: a @ b / (np.linalg.norm(a) * np.linalg.norm(b))
print("prix centrés réduits :", z.round(3), "| profil :", profil.round(3), "| cos P3 =", round(c(profil, F[2]), 3), "| cos P4 =", round(c(profil, F[3]), 3))
```
<!--sortie-->
```text
prix centrés réduits : [-1.414  1.414  0.     0.   ] | profil : [1. 0. 0.] | cos P3 = 0.0 | cos P4 = 1.0
```

### Corrigé 7.3

(a) Dense : $3\,000\times150\times8=3{,}6$ Mo. CSR : $27\,687\times(8+4)+3\,001\times4\approx344$ ko, soit environ **10 fois moins**. (b) Dense : $10^6\times10^4\times8=80$ Go (impossible à garder en mémoire). Creux : $10^7$ achats $\times12$ octets $\approx124$ Mo (avec les pointeurs de ligne), soit un rapport de **plus de 600**. Le gain croît avec la **dilution** de la matrice : à 0,1 % de cases remplies, on ne stocke que ce qui existe.

```python
dense = 3000 * 150 * 8; creux = 27687 * 12 + 3001 * 4
print("boutique : dense", dense / 1e6, "Mo | creux", round(creux / 1e3), "ko | rapport", round(dense / creux, 1))
dense2 = 1e6 * 1e4 * 8; creux2 = 1e6 * 10 * 12 + (1e6 + 1) * 4
print("grand site : dense", dense2 / 1e9, "Go | creux", round(creux2 / 1e6), "Mo | rapport", round(dense2 / creux2))
```
<!--sortie-->
```text
boutique : dense 3.6 Mo | creux 344 ko | rapport 10.5
grand site : dense 80.0 Go | creux 124 Mo | rapport 645
```

### Corrigé 7.4

U4 a acheté P1, P2, P6. Avec les cosinus du livre : pour **P3**, $\cos(\text{P3},\text{P1})=2/\sqrt{12}=0{,}577$, $\cos(\text{P3},\text{P2})=1/\sqrt9=0{,}333$, $\cos(\text{P3},\text{P6})=0$ : score $0{,}911$. Pour **P4** : $\cos(\text{P4},\text{P1})=3/\sqrt{16}=0{,}75$, $\cos(\text{P4},\text{P2})=2/\sqrt{12}=0{,}577$, $\cos(\text{P4},\text{P6})=0$ : score $1{,}327$. Pour **P5** : $1/\sqrt8=0{,}354$, $1/\sqrt6=0{,}408$, $0$ : score $0{,}762$. Le classement est **P4, P3, P5**, identique à celui de la popularité sur ce petit tableau (la personnalisation ne se voit que sur des historiques plus variés).

```python
S = (M.T @ M) / np.sqrt(np.outer(M.sum(axis=0), M.sum(axis=0))); np.fill_diagonal(S, 0)
sc = M[3] @ S
print("scores de U4 pour P3, P4, P5 :", sc[[2, 3, 4]].round(3))
```
<!--sortie-->
```text
scores de U4 pour P3, P4, P5 : [0.911 1.327 0.762]
```

### Corrigé 7.5

(a) Avant rétrécissement : $a\,(0{,}9)>c\,(0{,}7)>b\,(0{,}5)$. (b) Avec $\lambda=10$ : $a'=0{,}9\times\frac3{13}\approx0{,}208$ ; $b'=0{,}5\times\frac{30}{40}=0{,}375$ ; $c'=0{,}7\times\frac{12}{22}\approx0{,}382$. Nouveau classement : $c>b>a$ : la paire $a$, fondée sur 3 co-achats, passe **de la première à la dernière** place. (c) $b$ et $c$ échangent leur rang quand $0{,}5\,\frac{30}{30+\lambda}=0{,}7\,\frac{12}{12+\lambda}$, soit $15(12+\lambda)=8{,}4(30+\lambda)$, donc $6{,}6\,\lambda=72$ et $\lambda\approx10{,}9$ : pour $\lambda<10{,}9$ c'est $c$ qui est devant, au-delà c'est $b$ (le plus fiable).

```python
paires = {"a": (0.9, 3), "b": (0.5, 30), "c": (0.7, 12)}
for lam in (0, 10, 10.909, 20):
    print(f"λ = {lam:6}:", {k: round(s * n / (n + lam), 3) for k, (s, n) in paires.items()})
```
<!--sortie-->
```text
λ =      0: {'a': 0.9, 'b': 0.5, 'c': 0.7}
λ =     10: {'a': 0.208, 'b': 0.375, 'c': 0.382}
λ = 10.909: {'a': 0.194, 'b': 0.367, 'c': 0.367}
λ =     20: {'a': 0.117, 'b': 0.3, 'c': 0.262}
```

### Corrigé 7.6

Les voisins de similarité positive sont $u_2$ ($0{,}653$, écart $+0{,}25$) et $u_4$ ($0{,}816$, écart $+0{,}5$). Prédiction : $4+\dfrac{0{,}653\times0{,}25+0{,}816\times0{,}5}{0{,}653+0{,}816}=4+\dfrac{0{,}571}{1{,}469}\approx4{,}39$, contre 4,43 avec le voisin de similarité négative. La différence est faible ici, mais le raisonnement est plus sûr : on n'utilise pas l'hypothèse fragile « il n'aime pas ce que j'aime, donc ce qu'il déteste me plaira ».

```python
notes = np.array([[5, 3, 4, np.nan], [4, 2, 5, 4], [2, 5, 1, 2], [5, 4, 4, 5]]); moy = np.nanmean(notes, axis=1); cent = notes - moy[:, None]
sims = np.array([cent[0, :3] @ cent[v, :3] / (np.linalg.norm(cent[0, :3]) * np.linalg.norm(cent[v, :3])) for v in (1, 2, 3)])
ec = cent[1:, 3]; pos = sims > 0
print("similarités :", sims.round(3), "| prédiction (3 voisins) :", round(moy[0] + (sims * ec).sum() / np.abs(sims).sum(), 3), "| (voisins positifs) :", round(moy[0] + (sims[pos] * ec[pos]).sum() / sims[pos].sum(), 3))
```
<!--sortie-->
```text
similarités : [ 0.653 -0.717  0.816] | prédiction (3 voisins) : 4.425 | (voisins positifs) : 4.389
```

### Corrigé 7.7

Client 2 : $p_2=\dfrac{4\times1{,}652+1\times1{,}249}{1{,}652^2+1{,}249^2+1}=\dfrac{7{,}857}{5{,}289}\approx1{,}486$. Client 1 : $p_1=\dfrac{5\times1{,}652+3\times0{,}715+1\times1{,}249}{1{,}652^2+0{,}715^2+1{,}249^2+1}=\dfrac{11{,}654}{5{,}800}\approx2{,}009$. On retrouve exactement les valeurs de la seconde passe du livre.

```python
q = np.array([1.652, 0.715, 1.724, 1.249])
print("client 2 :", round((4 * q[0] + 1 * q[3]) / (q[0] ** 2 + q[3] ** 2 + 1), 3), "| client 1 :", round((5 * q[0] + 3 * q[1] + 1 * q[3]) / (q[0] ** 2 + q[1] ** 2 + q[3] ** 2 + 1), 3))
```
<!--sortie-->
```text
client 2 : 1.486 | client 1 : 2.009
```

### Corrigé 7.8

(a) $C_u=I+\alpha\,\operatorname{diag}(R_u)$, où $\operatorname{diag}(R_u)$ est la matrice diagonale des achats du client. Donc $Q^\top C_uQ=Q^\top Q+\alpha\,Q^\top\operatorname{diag}(R_u)\,Q$. Or $\operatorname{diag}(R_u)$ ne conserve que les lignes de $Q$ correspondant aux produits achetés : $Q^\top\operatorname{diag}(R_u)Q=Q_u^\top Q_u$. D'où le résultat. (b) Le calcul direct de $Q^\top C_uQ$ coûte $O(mk^2)$ pour chaque client. L'astuce calcule $Q^\top Q$ **une fois pour tous** les clients ($O(mk^2)$ au total) et ajoute $\alpha Q_u^\top Q_u$, qui coûte $O(d_uk^2)$ ; il reste à résoudre un système $k\times k$ ($O(k^3)$). Le coût par client passe de $O(mk^2)$ à $O(d_uk^2+k^3)$ : avec $m=150$, $d_u\approx9$ et $k=6$, c'est un facteur d'environ 15 sur ce terme, et bien plus avec un grand catalogue.

```python
rng = np.random.default_rng(0); Q = rng.standard_normal((150, 6)); achat = rng.random(150) < 0.06; alpha = 8.0
direct = Q.T @ np.diag(1 + alpha * achat) @ Q
astuce = Q.T @ Q + alpha * Q[achat].T @ Q[achat]
print("identiques :", np.allclose(direct, astuce), "| produits achetés :", int(achat.sum()))
```
<!--sortie-->
```text
identiques : True | produits achetés : 8
```

### Corrigé 7.9

Prédiction : $\hat r=0{,}5\times0{,}4+0{,}2\times0{,}6=0{,}32$ ; erreur $e=4-0{,}32=3{,}68$. Mises à jour (avec les anciennes valeurs) : $p_1=0{,}5+0{,}1\,(3{,}68\times0{,}4-0{,}02\times0{,}5)=0{,}6462$ ; $p_2=0{,}2+0{,}1\,(3{,}68\times0{,}6-0{,}02\times0{,}2)=0{,}4204$ ; $q_1=0{,}4+0{,}1\,(3{,}68\times0{,}5-0{,}02\times0{,}4)=0{,}5832$ ; $q_2=0{,}6+0{,}1\,(3{,}68\times0{,}2-0{,}02\times0{,}6)=0{,}6724$. Nouvelle prédiction : $0{,}6462\times0{,}5832+0{,}4204\times0{,}6724\approx0{,}660$, soit une erreur de $3{,}34$ : **elle a diminué** (de 3,68 à 3,34), comme le veut la descente de gradient.

```python
p = np.array([0.5, 0.2]); q = np.array([0.4, 0.6]); r, g, lam = 4.0, 0.1, 0.02
e = r - p @ q; p2 = p + g * (e * q - lam * p); q2 = q + g * (e * p - lam * q)
print("erreur", round(e, 3), "| p", p2.round(4), "| q", q2.round(4), "| nouvelle prédiction", round(p2 @ q2, 4), "| nouvelle erreur", round(r - p2 @ q2, 3))
```
<!--sortie-->
```text
erreur 3.68 | p [0.6462 0.4204] | q [0.5832 0.6724] | nouvelle prédiction 0.6595 | nouvelle erreur 3.34
```

### Corrigé 7.10

Positions des succès : rangs 1, 4 et 8. Précision@10 $=3/10=0{,}3$ ; rappel@10 $=3/4=0{,}75$ ; succès@10 $=1$. AP@10 $=\dfrac{1/1+2/4+3/8}{\min(4,10)}=\dfrac{1{,}875}{4}\approx0{,}469$. DCG $=1+\dfrac1{\log_25}+\dfrac1{\log_29}=1+0{,}431+0{,}315=1{,}746$ ; IDCG (4 produits pertinents aux rangs 1 à 4) $=1+0{,}631+0{,}5+0{,}431=2{,}562$ ; NDCG $\approx0{,}682$.

```python
print(np.round(metriques_liste(np.array([0, 1, 2, 3, 4, 5, 6, 7, 8, 9]), {0, 3, 7, 100}, k=10), 4))
```
<!--sortie-->
```text
[0.3    0.75   0.4688 0.6817]
```

### Corrigé 7.11

| | Précision@5 | Rappel@5 | AP@5 | NDCG@5 | 1ᵉʳ produit pertinent ? |
|---|---|---|---|---|---|
| Liste A $(1,0,0,0,0)$ | 0,2 | 0,333 | 0,333 | 0,469 | **oui** |
| Liste B $(0,0,1,1,1)$ | 0,6 | 1 | 0,478 | 0,618 | non |

La liste B est meilleure pour les quatre métriques « de liste » : elle retrouve tout ce que le client voulait. La liste A n'est meilleure que sur « le premier produit est-il pertinent ? ». Si l'on ne montre qu'**un seul** produit (une bannière), A est préférable ; si l'on affiche une vitrine de cinq, B vaut mieux. Le choix de la métrique doit donc suivre l'usage.

```python
rg = np.arange(1, 6); idcg = (1 / np.log2(np.arange(1, 4) + 1)).sum()
for nom, rel in (("A", [1, 0, 0, 0, 0]), ("B", [0, 0, 1, 1, 1])):
    hits = np.array(rel, float)
    ap = (hits * np.cumsum(hits) / rg).sum() / 3; ndcg = (hits / np.log2(rg + 1)).sum() / idcg
    print(nom, "précision", hits.sum() / 5, "| rappel", round(hits.sum() / 3, 3), "| AP", round(ap, 3), "| NDCG", round(ndcg, 3))
```
<!--sortie-->
```text
A précision 0.2 | rappel 0.333 | AP 0.333 | NDCG 0.469
B précision 0.6 | rappel 1.0 | AP 0.478 | NDCG 0.618
```

### Corrigé 7.12

(a) **Non** : sans changement de popularité, le rapport vaut environ **1,10** pour la popularité (0,288 contre 0,263) et **1,18** pour l'ALS (0,355 contre 0,301). (b) Les deux protocoles ne posent pas la même question. Dans le découpage temporel, on ne teste que sur des produits **que le client n'avait pas achetés** en première période : c'est une tâche plus dure. Dans le découpage aléatoire, le client garde dans son entraînement des achats de la même période que ceux qu'on cache, et un produit acheté aux deux périodes peut être « retrouvé ». La dérive s'ajoute à cet écart de définition et le fait passer de 1,1 à 1,5 environ. (c) Ajouter de l'exploration (20 % de produits tirés au hasard) fait découvrir plus de produits (60 produits achetés au lieu de 48), mais le nombre de bons produits en vitrine reste à 0,25 sur 5 : le classement par **ventes** continue de confondre « acheté » et « montré » : les produits qui, par hasard, ont été exposés davantage gardent un avantage. Seul un classement qui divise par les **expositions** (le taux d'achat) corrige la lecture.

```python
o = inflation(0)
for nom, t in o.items():
    print(f"{nom:11s} aléatoire {float(t[0]):.3f} | temporel {float(t[1]):.3f} | rapport {float(t[2]):.2f}")
```
<!--sortie-->
```text
popularité  aléatoire 0.288 | temporel 0.263 | rapport 1.10
ALS         aléatoire 0.355 | temporel 0.301 | rapport 1.18
```
