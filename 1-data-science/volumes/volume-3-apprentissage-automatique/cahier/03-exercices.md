# Chapitre 3 : Apprentissage non supervisé et réduction de dimension — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 3 du livre. Les **applications** reprennent, pas à pas et avec le code, les études du livre (segmenter, valider, réduire, dessiner) ; les **exercices** se travaillent d'abord à la main, puis se vérifient par le calcul. Données : les 12 000 clients simulés de la boutique (`donnees/clients_ml.csv`) et les chiffres manuscrits de `scikit-learn` (jeu **réel** embarqué). Prérequis : le chapitre 3 du livre ; Python avec NumPy, pandas, scikit-learn.

## Applications

### Préparation commune

À exécuter une fois : elle charge les clients, prépare les sept variables de comportement (le montant en logarithme, puis centrage-réduction) et importe les outils. Les applications 3.1 à 3.3 et 3.5 à 3.8 la réutilisent.

```python
import warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import KMeans
from sklearn.metrics import (silhouette_score, calinski_harabasz_score, davies_bouldin_score,
                             adjusted_rand_score, normalized_mutual_info_score)

c = pd.read_csv("donnees/clients_ml.csv")
cols = ["age", "nb_commandes_12m", "montant_12m", "recence_jours",
        "part_achats_promo", "taux_ouverture_email", "nb_promos_recues_12m"]
X = c[cols].copy()
X["montant_12m"] = np.log1p(X["montant_12m"])          # montant très asymétrique : logarithme
Z = StandardScaler().fit_transform(X)
print(Z.shape, "| moyennes ~ 0 :", Z.mean(0).round(2).max(), "| écarts-types = 1 :", Z.std(0).round(2).min())
```
<!--sortie-->
```text
(12000, 7) | moyennes ~ 0 : -0.0 | écarts-types = 1 : 1.0
```

### Application 3.1 — Segmenter la clientèle de bout en bout (sections 3.1.1 à 3.1.7)

**Contexte.** La gérante veut des groupes de clients pour adapter ses envois. **Objectif.** Passer de la table brute à une segmentation justifiée : choix de $k$ par plusieurs critères, stabilité, profils, utilité.

**Étape 1 — Balayer $k$ avec trois critères internes.** Pour chaque $k$ de 2 à 8, on ajuste k-means et on calcule silhouette (sur 4 000 clients), Calinski–Harabasz et Davies–Bouldin.

```python
lignes, modeles = [], {}
for k in range(2, 9):
    km = KMeans(k, n_init=10, random_state=0).fit(Z)
    modeles[k] = km
    lignes.append({"k": k, "silhouette": round(silhouette_score(Z, km.labels_, sample_size=4000, random_state=0), 3),
                   "CH": round(calinski_harabasz_score(Z, km.labels_)), "DB": round(davies_bouldin_score(Z, km.labels_), 3)})
critere = pd.DataFrame(lignes)
print(critere.to_string(index=False))
```
<!--sortie-->
```text
 k  silhouette   CH    DB
 2       0.304 4041 1.193
 3       0.331 5040 1.118
 4       0.284 5135 1.271
 5       0.261 4678 1.311
 6       0.244 4241 1.321
 7       0.231 3825 1.428
 8       0.226 3520 1.334
```

**Lecture.** La silhouette et Davies–Bouldin préfèrent $k=3$ ($0{,}331$ et $1{,}118$) ; Calinski–Harabasz culmine à $k=4$ ($5\,135$). Aucun critère ne tranche seul : retenez une plage ($3$ à $5$) et départagez avec la stabilité et l'utilité.

**Étape 2 — Stabilité.** On tire 15 sous-échantillons de 80 %, on réajuste, et on compare au modèle de référence avec l'ARI.

```python
def stabilite(A, k, B=15):
    r = np.random.default_rng(0)
    ref = KMeans(k, n_init=10, random_state=0).fit(A)
    sc = []
    for b in range(B):
        idx = r.choice(len(A), int(0.8 * len(A)), replace=False)
        km = KMeans(k, n_init=5, random_state=b).fit(A[idx])
        sc.append(adjusted_rand_score(ref.predict(A[idx]), km.labels_))
    return round(float(np.mean(sc)), 3), round(float(np.std(sc)), 3)
print({k: stabilite(Z, k) for k in (3, 4, 5, 6)})
```
<!--sortie-->
```text
{3: (0.996, 0.004), 4: (0.986, 0.007), 5: (0.981, 0.016), 6: (0.964, 0.029)}
```

**Étape 3 — Profils et utilité.** On retient $k=4$ et on regarde, pour chaque groupe, sa taille, deux variables de comportement et le départ à 90 jours (que la segmentation n'a pas vu).

```python
c["groupe"] = modeles[4].labels_
profil = c.groupby("groupe").agg(part=("age", lambda s: len(s) / len(c)), commandes=("nb_commandes_12m", "mean"),
                                 recence=("recence_jours", "mean"), part_promo=("part_achats_promo", "mean"),
                                 depart=("churn_90j", "mean"), depense_6m=("depense_6m", "mean")).round(3)
print(profil.to_string())
```
<!--sortie-->
```text
         part  commandes  recence  part_promo  depart  depense_6m
groupe                                                           
0       0.186      4.283   62.151       0.746   0.198      52.372
1       0.296      7.305   39.021       0.191   0.010     168.239
2       0.145      0.108  363.855       0.187   0.413      22.161
3       0.374      2.276   91.661       0.158   0.110      57.801
```

**Lecture.** Quatre profils nets. Le groupe 1 (30 % des clients) réunit les fidèles : $7{,}3$ commandes, récence de $39$ jours, départ à $1{,}0\ \%$, dépense à 6 mois de $168$ €. Le groupe 2 (14,5 %) réunit les dormants : $0{,}11$ commande, récence de $364$ jours, départ à $41{,}3\ \%$. Le groupe 0 est celui des chasseurs de promotions ($74{,}6\ \%$ des achats en promotion) et le groupe 3, le plus nombreux ($37{,}4\ \%$), celui des occasionnels réguliers. Stabilité (étape 2) : l'ARI moyen vaut $0{,}996$, $0{,}986$, $0{,}981$ et $0{,}964$ pour $k=3,\dots,6$ : tous ces découpages sont reproductibles, donc la stabilité ne départage pas $3$, $4$, $5$ et $6$.

**Pour aller plus loin.** Reprenez l'étape 1 avec `random_state=1` : les critères et le $k$ retenu changent-ils ? Recommencez avec seulement `age`, `recence_jours` et `nb_commandes_12m` : que deviennent les profils ?

### Application 3.2 — Valider contre la vérité cachée : initialisation, échelle, transformation (sections 3.1.5 et 3.1.6)

**Objectif.** Mesurer, avec `segment_vrai`, ce qui change l'ARI : le hasard de l'initialisation, l'échelle, la transformation du montant.

**Étape 1 — Le hasard de l'initialisation.** Vingt graines, avec une seule initialisation par ajustement (`n_init=1`), puis avec dix.

```python
def ari_graines(A, n_init, graines=range(20)):
    out = [adjusted_rand_score(c["segment_vrai"], KMeans(4, n_init=n_init, random_state=s).fit_predict(A)) for s in graines]
    return round(float(np.mean(out)), 3), round(float(np.min(out)), 3), round(float(np.max(out)), 3)
print("n_init=1  (moyenne, min, max) :", ari_graines(Z, 1))
print("n_init=10 (moyenne, min, max) :", ari_graines(Z, 10, range(5)))
```
<!--sortie-->
```text
n_init=1  (moyenne, min, max) : (0.486, 0.482, 0.489)
n_init=10 (moyenne, min, max) : (0.487, 0.486, 0.489)
```

**Lecture.** Surprise : sur ces données bien structurées, l'initialisation compte **très peu** : avec une seule initialisation, l'ARI moyen est $0{,}486$ (de $0{,}482$ à $0{,}489$ sur 20 graines) ; avec dix, $0{,}487$. Ne généralisez pas : sur des données moins nettes, `n_init=1` donne des résultats bien plus dispersés. Gardez `n_init=10` (c'est le coût d'une assurance bon marché).

**Étape 2 — Échelle et transformation.** On compare quatre préparations des mêmes variables.

```python
from sklearn.preprocessing import RobustScaler, MinMaxScaler
brut = c[cols].to_numpy(dtype=float)
prepas = {"standardisation (log du montant)": Z,
          "min-max (log du montant)": MinMaxScaler().fit_transform(X),
          "robuste (log du montant)": RobustScaler().fit_transform(X),
          "standardisation, montant brut": StandardScaler().fit_transform(brut)}
for nom, A in prepas.items():
    lab = KMeans(4, n_init=10, random_state=0).fit_predict(A)
    print(f"{nom:36s} ARI = {adjusted_rand_score(c['segment_vrai'], lab):.3f}   NMI = {normalized_mutual_info_score(c['segment_vrai'], lab):.3f}")
```
<!--sortie-->
```text
standardisation (log du montant)     ARI = 0.487   NMI = 0.535
min-max (log du montant)             ARI = 0.502   NMI = 0.545
robuste (log du montant)             ARI = 0.397   NMI = 0.498
standardisation, montant brut        ARI = 0.354   NMI = 0.490
```

**Lecture.** L'échelle pèse beaucoup plus que l'initialisation : l'ARI va de $0{,}354$ (montant brut) à $0{,}502$ (min-max). La standardisation ($0{,}487$) n'est pas la meilleure ici : le min-max fait légèrement mieux ($0{,}502$) et l'échelle **robuste** nettement moins bien ($0{,}397$), parce qu'elle ne réduit pas les valeurs extrêmes de `nb_promos_recues_12m` et de `recence_jours`. Il n'existe pas d'échelle universelle : **testez plusieurs préparations** et jugez-les avec les épreuves de 3.1.

### Application 3.3 — La statistique de l'écart, écrite à la main (section 3.1.3)

**Objectif.** Programmer la statistique de l'écart et comparer deux références. Pour limiter le temps de calcul, on travaille sur 3 000 clients tirés au hasard.

**Étape 1 — La fonction.** Pour chaque $k$ de 1 à 8, on calcule $\log W_k$ sur les données, puis sur $B$ jeux de référence ; l'écart est la différence des moyennes, et la règle de Tibshirani choisit le plus petit $k$ tel que $\mathrm{Gap}(k)\ge\mathrm{Gap}(k+1)-s_{k+1}$.

```python
def log_w(A, k):
    return np.log(KMeans(k, n_init=3, random_state=0).fit(A).inertia_)

def ecart(A, reference, ks=range(1, 9), B=10, graine=0):
    r = np.random.default_rng(graine)
    lw = np.array([log_w(A, k) for k in ks])
    ref = np.array([[log_w(reference(A, r), k) for k in ks] for _ in range(B)])
    gap, s = ref.mean(0) - lw, ref.std(0) * np.sqrt(1 + 1 / B)
    ks = list(ks)
    choix = next((k for i, k in enumerate(ks[:-1]) if gap[i] >= gap[i + 1] - s[i + 1]), ks[-1])
    return gap.round(3), choix
```

**Étape 2 — Deux références.** La permutation des colonnes garde les distributions marginales ; la boîte uniforme ne les garde pas.

```python
sous = Z[np.random.default_rng(0).choice(len(Z), 3000, replace=False)]
perm = lambda A, r: np.column_stack([r.permutation(A[:, j]) for j in range(A.shape[1])])
unif = lambda A, r: r.uniform(A.min(0), A.max(0), A.shape)
for nom, ref in (("permutation", perm), ("boîte uniforme", unif)):
    gap, choix = ecart(sous, ref)
    print(f"{nom:15s} gap = {gap}  -> k retenu : {choix}")
```
<!--sortie-->
```text
permutation     gap = [0.    0.17  0.374 0.486 0.503 0.484 0.447 0.44 ]  -> k retenu : 5
boîte uniforme  gap = [0.838 0.806 1.011 1.122 1.177 1.207 1.2   1.217]  -> k retenu : 1
```

**Lecture.** Avec la permutation, l'écart augmente puis s'aplatit : il culmine à $k=5$ ($0{,}503$) et la règle retient $5$. Avec la boîte uniforme, l'écart est déjà de $0{,}838$ pour **un seul groupe** et ne présente pas de maximum net ; ici la règle s'arrête à $k=1$ (dans le livre, avec d'autres tirages de référence, elle s'arrête à $k=6$ : le choix **n'est pas stable**). C'est la preuve que cette référence est inadaptée à des variables asymétriques et corrélées.

**Pour aller plus loin.** Écrivez une troisième référence : tirer des points uniformes dans la boîte englobante des données **après rotation par ACP** (variante de Tibshirani), puis tourner en sens inverse. Change-t-elle le $k$ retenu ?

### Application 3.4 — Réduire les chiffres manuscrits : ACP, noyau, NMF, projection aléatoire (sections 3.2.2 à 3.2.6)

**Objectif.** Comparer cinq réductions à nombre de dimensions égal, par la précision d'un classifieur (5 plus proches voisins) en validation croisée. **Précaution** : la réduction fait partie du modèle ; on l'insère donc **dans** un `Pipeline`, pour qu'elle soit réajustée sur chaque pli d'entraînement.

```python
from sklearn.datasets import load_digits
from sklearn.decomposition import PCA, KernelPCA, NMF, TruncatedSVD
from sklearn.random_projection import GaussianRandomProjection
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import make_pipeline
from sklearn.model_selection import cross_val_score
d = load_digits(); Xd, yd = d.data / 16.0, d.target
reductions = {"ACP": lambda m: PCA(m), "SVD tronquée": lambda m: TruncatedSVD(m, random_state=0),
              "ACP à noyau (rbf, gamma=0,02)": lambda m: KernelPCA(m, kernel="rbf", gamma=0.02),
              "NMF": lambda m: NMF(m, init="nndsvda", random_state=0, max_iter=400),
              "projection aléatoire": lambda m: GaussianRandomProjection(m, random_state=0)}
lignes = []
for nom, f in reductions.items():
    ligne = {"méthode": nom}
    for m in (5, 10, 20, 40):
        ligne[f"m={m}"] = round(cross_val_score(make_pipeline(f(m), KNeighborsClassifier(5)), Xd, yd, cv=5).mean(), 3)
    lignes.append(ligne)
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
                      méthode   m=5  m=10  m=20  m=40
                          ACP 0.884 0.940 0.958 0.962
                 SVD tronquée 0.844 0.935 0.959 0.962
ACP à noyau (rbf, gamma=0,02) 0.883 0.943 0.957 0.962
                          NMF 0.795 0.824 0.843 0.851
         projection aléatoire 0.586 0.757 0.905 0.934
```

**Lecture.** À $m=40$, l'ACP, la SVD tronquée et l'ACP à noyau atteignent la même précision ($0{,}962$) ; pour $m=5$, l'ACP ($0{,}884$) et l'ACP à noyau ($0{,}883$) devancent la SVD tronquée ($0{,}844$), qui gaspille une direction sur la moyenne. La **NMF** plafonne à $0{,}851$ : sa contrainte de positivité rend les composantes lisibles, au prix d'une information moins bien conservée. La **projection aléatoire** est la plus faible en petite dimension ($0{,}586$ à $m=5$) mais rattrape son retard avec $m$ ($0{,}934$ à $40$) : conforme à Johnson–Lindenstrauss, qui demande beaucoup de dimensions.

**Pour aller plus loin.** Faites varier `gamma` de l'ACP à noyau ($0{,}002$, $0{,}02$, $0{,}2$) : à partir de quelle valeur la méthode se dégrade-t-elle, et pourquoi ?

### Application 3.5 — Quand les groupes ne sont pas des boules : DBSCAN et liens (sections 3.3.1 et 3.3.2)

**Objectif.** Explorer la grille $(\varepsilon, m)$ de DBSCAN sur deux formes classiques, et comparer avec les liens hiérarchiques.

```python
from sklearn.datasets import make_moons, make_circles
from sklearn.cluster import DBSCAN, AgglomerativeClustering
jeux = {"lunes": make_moons(600, noise=0.07, random_state=0), "cercles": make_circles(600, factor=0.4, noise=0.05, random_state=0)}
for nom, (A, y) in jeux.items():
    print(nom, "| k-means :", round(adjusted_rand_score(y, KMeans(2, n_init=10, random_state=0).fit_predict(A)), 3))
    for eps in (0.08, 0.12, 0.18, 0.25):
        ligne = [round(adjusted_rand_score(y, DBSCAN(eps=eps, min_samples=m).fit_predict(A)), 2) for m in (3, 5, 10, 20)]
        print(f"   epsilon = {eps:4.2f}  ARI pour min_samples = 3, 5, 10, 20 :", ligne)
```
<!--sortie-->
```text
lunes | k-means : 0.252
   epsilon = 0.08  ARI pour min_samples = 3, 5, 10, 20 : [0.73, 0.54, 0.07, 0.0]
   epsilon = 0.12  ARI pour min_samples = 3, 5, 10, 20 : [1.0, 1.0, 0.97, 0.08]
   epsilon = 0.18  ARI pour min_samples = 3, 5, 10, 20 : [1.0, 1.0, 1.0, 0.99]
   epsilon = 0.25  ARI pour min_samples = 3, 5, 10, 20 : [1.0, 1.0, 1.0, 1.0]
cercles | k-means : -0.001
   epsilon = 0.08  ARI pour min_samples = 3, 5, 10, 20 : [0.55, 0.52, 0.97, 0.01]
   epsilon = 0.12  ARI pour min_samples = 3, 5, 10, 20 : [0.99, 0.99, 0.54, 1.0]
   epsilon = 0.18  ARI pour min_samples = 3, 5, 10, 20 : [1.0, 1.0, 1.0, 0.88]
   epsilon = 0.25  ARI pour min_samples = 3, 5, 10, 20 : [1.0, 1.0, 1.0, 1.0]
```

**Lecture.** Sur les lunes comme sur les cercles, k-means échoue ($0{,}252$ et $-0{,}001$). DBSCAN réussit (ARI $\approx1$) dès que $\varepsilon$ est assez grand, mais la bonne valeur dépend de `min_samples` : sur les lunes, $\varepsilon=0{,}12$ convient pour $m\le10$ mais s'effondre à $m=20$ ($0{,}08$) ; sur les cercles, $\varepsilon=0{,}08$ avec $m=10$ donne $0{,}97$ alors que $m=20$ donne $0{,}01$. Un voisinage trop exigeant fait disparaître les points de bordure : plus $m$ est grand, plus il faut agrandir $\varepsilon$.

```python
for nom, (A, y) in jeux.items():
    res = {l: round(adjusted_rand_score(y, AgglomerativeClustering(2, linkage=l).fit_predict(A)), 3) for l in ("single", "complete", "average", "ward")}
    print(nom, res)
```
<!--sortie-->
```text
lunes {'single': 1.0, 'complete': 0.426, 'average': 0.557, 'ward': 0.557}
cercles {'single': 1.0, 'complete': 0.236, 'average': 0.115, 'ward': 0.001}
```

**Lecture.** Le lien **simple** retrouve parfaitement les deux formes ($1{,}0$ dans les deux cas), les autres échouent, surtout sur les cercles où le lien de Ward donne $0{,}001$. Le lien simple suit des chaînes de points proches ; il serait détruit par un peu de bruit reliant les deux formes (testez en ajoutant 20 points au hasard).

### Application 3.6 — L'algorithme EM, de la main à la bibliothèque (section 3.3.3)

**Objectif.** Écrire EM pour un mélange de deux lois normales en dimension 1, vérifier que la vraisemblance ne baisse jamais, puis comparer à `GaussianMixture`.

**Étape 1 — Données et algorithme.** Cent valeurs tirées de $\mathcal N(0;1)$ (40 %) et $\mathcal N(4;1{,}5^2)$ (60 %).

```python
from scipy.stats import norm
r = np.random.default_rng(1)
x = np.concatenate([r.normal(0, 1, 40), r.normal(4, 1.5, 60)])
def em(x, mu, sd, pi, tours=40):
    ll = []
    for _ in range(tours):
        dens = pi * norm.pdf(x[:, None], mu, sd)                       # étape E
        ll.append(np.log(dens.sum(1)).sum()); g = dens / dens.sum(1, keepdims=True)
        N = g.sum(0); mu = (g * x[:, None]).sum(0) / N                  # étape M
        sd = np.sqrt((g * (x[:, None] - mu) ** 2).sum(0) / N); pi = N / len(x)
    return mu, sd, pi, np.array(ll)
mu, sd, pi, ll = em(x, np.array([1.0, 3.0]), np.array([1.0, 1.0]), np.array([0.5, 0.5]))
print("mu =", mu.round(3), "sd =", sd.round(3), "pi =", pi.round(3), "| la vraisemblance ne baisse jamais :", bool(np.all(np.diff(ll) >= -1e-9)))
```
<!--sortie-->
```text
mu = [0.358 4.135] sd = [1.166 0.933] pi = [0.489 0.511] | la vraisemblance ne baisse jamais : True
```

**Étape 2 — Comparaison avec la bibliothèque.**

```python
from sklearn.mixture import GaussianMixture
g = GaussianMixture(2, n_init=5, random_state=0).fit(x.reshape(-1, 1))
o = np.argsort(g.means_.ravel())
print("sklearn (tol=1e-3 par défaut, %d tours) : mu =" % g.n_iter_, g.means_.ravel()[o].round(3), "sd =", np.sqrt(g.covariances_.ravel())[o].round(3), "pi =", g.weights_[o].round(3))
g = GaussianMixture(2, n_init=5, random_state=0, tol=1e-9, max_iter=2000).fit(x.reshape(-1, 1)); o = np.argsort(g.means_.ravel())
print("sklearn (tol=1e-9, %d tours)           : mu =" % g.n_iter_, g.means_.ravel()[o].round(3), "sd =", np.sqrt(g.covariances_.ravel())[o].round(3), "pi =", g.weights_[o].round(3))
print("EM écrit à la main, 2 000 tours         : mu =", em(x, np.array([1.0, 3.0]), np.array([1.0, 1.0]), np.array([0.5, 0.5]), 2000)[0].round(3))
```
<!--sortie-->
```text
sklearn (tol=1e-3 par défaut, 3 tours) : mu = [0.331 4.115] sd = [1.147 0.947] pi = [0.483 0.517]
sklearn (tol=1e-9, 132 tours)           : mu = [0.386 4.157] sd = [1.186 0.917] pi = [0.495 0.505]
EM écrit à la main, 2 000 tours         : mu = [0.387 4.157]
```

**Lecture.** À 40 tours, le EM écrit à la main donne $\mu=(0{,}358\,;\,4{,}135)$ et la vraisemblance ne baisse jamais, comme la théorie le garantit. La bibliothèque donne $(0{,}331\,;\,4{,}115)$ avec sa tolérance par défaut (elle s'arrête après trois tours, dès que l'amélioration passe sous $10^{-3}$) ; avec `tol=1e-9`, elle converge vers $\mu=(0{,}386\,;\,4{,}157)$, **exactement ce que donne notre EM après 2 000 tours** $(0{,}387\,;\,4{,}157)$. Les vraies valeurs étaient $0$ et $4$ : l'estimation est correcte, avec l'erreur d'un échantillon de 100 points. Pour le BIC sur les clients (étape 3), la chute est forte de $k=3$ à $k=4$ ($31\,244\to28\,484$), puis lente ; le minimum est atteint à $k=7$ ($27\,577$) sur ce sous-échantillon de 3 000 clients : le BIC ne désigne pas le même nombre que les critères de 3.1, ce qui illustre à nouveau qu'**un critère n'est pas une vérité**.

**Étape 3 — BIC sur les clients.** On ajuste des mélanges à covariance complète, de 1 à 8 composantes, sur les 3 000 clients de l'application 3.3.

```python
for k in range(1, 9):
    gm = GaussianMixture(k, n_init=3, random_state=0).fit(sous)
    print(k, round(gm.bic(sous)))
```
<!--sortie-->
```text
1 52124
2 45583
3 31244
4 28484
5 28113
6 27944
7 27577
8 27620
```

### Application 3.7 — t-SNE et UMAP : perplexité, voisins, fiabilité (sections 3.4.1 à 3.4.4)

**Objectif.** Mesurer l'effet des hyperparamètres sur la fiabilité et sur la précision d'un classifieur entraîné sur les coordonnées du dessin. On travaille sur 600 chiffres pour que le calcul reste court.

```python
from sklearn.manifold import TSNE, trustworthiness
import umap
idx = np.random.default_rng(0).choice(len(Xd), 600, replace=False)
Xs, ys = Xd[idx], yd[idx]
def bilan(E):
    return round(trustworthiness(Xs, E, n_neighbors=10), 3), round(cross_val_score(KNeighborsClassifier(5), E, ys, cv=5).mean(), 3)
lignes = []
for perp in (5, 30, 60):
    lignes.append({"méthode": f"t-SNE, perplexité {perp}", "fiabilité, précision": bilan(TSNE(2, perplexity=perp, random_state=0, init="pca").fit_transform(Xs))})
for nv in (5, 15, 40):
    lignes.append({"méthode": f"UMAP, {nv} voisins", "fiabilité, précision": bilan(umap.UMAP(n_neighbors=nv, random_state=0).fit_transform(Xs))})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
             méthode fiabilité, précision
 t-SNE, perplexité 5       (0.984, 0.985)
t-SNE, perplexité 30        (0.985, 0.97)
t-SNE, perplexité 60       (0.984, 0.975)
     UMAP, 5 voisins       (0.982, 0.982)
    UMAP, 15 voisins       (0.983, 0.968)
    UMAP, 40 voisins       (0.983, 0.962)
```

**Lecture.** La fiabilité est quasi identique partout ($0{,}982$ à $0{,}985$) : tous les réglages conservent bien les voisinages. La précision, elle, est la plus haute pour les plus petits voisinages ($0{,}985$ pour t-SNE à perplexité $5$ contre $0{,}970$ à $30$ et $0{,}975$ à $60$ ; $0{,}982$ pour UMAP à $5$ voisins, puis $0{,}968$ et $0{,}962$ à $15$ et $40$) : un petit voisinage sépare mieux les classes **sur le dessin** même si la structure globale est moins bien rendue. Rappel : ces précisions sont optimistes (plongement transductif).

**Mise en garde.** La précision d'un classifieur sur les coordonnées d'un dessin est **optimiste** : le plongement a vu **toutes** les données, y compris celles du pli de test (c'est un plongement *transductif*). Pour une mesure honnête, ajustez UMAP sur le pli d'entraînement seulement et projetez le pli de test avec `transform`.

### Application 3.8 — Réduire avant de classer : un pipeline sur les clients (section 3.2.8)

**Objectif.** Mesurer l'effet du nombre de composantes gardées sur la segmentation, avec trois épreuves : la silhouette dans l'espace réduit, l'ARI avec la vérité cachée et la **séparation du départ** entre groupes (utilité).

```python
from sklearn.pipeline import make_pipeline
lignes = []
for m in (2, 3, 4, 5, 7):
    pipe = make_pipeline(PCA(m), KMeans(4, n_init=10, random_state=0)).fit(Z)
    lab = pipe.predict(Z); R = pipe[0].transform(Z)
    depart = c.groupby(lab)["churn_90j"].mean()
    lignes.append({"composantes": m, "variance gardée": round(pipe[0].explained_variance_ratio_.sum(), 3),
                   "silhouette": round(silhouette_score(R, lab, sample_size=4000, random_state=0), 3),
                   "ARI": round(adjusted_rand_score(c["segment_vrai"], lab), 3),
                   "départ min - max": f"{depart.min():.3f} - {depart.max():.3f}"})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 composantes  variance gardée  silhouette   ARI départ min - max
           2            0.641       0.467 0.480    0.009 - 0.418
           3            0.762       0.381 0.489    0.013 - 0.409
           4            0.857       0.342 0.502    0.012 - 0.414
           5            0.932       0.312 0.479    0.010 - 0.412
           7            1.000       0.284 0.487    0.010 - 0.413
```

**Lecture.** Garder $4$ composantes ($85{,}7\ \%$ de la variance) donne le meilleur ARI ($0{,}502$) ; $2$ composantes suffisent presque ($0{,}480$). La séparation du départ entre groupes reste **stable** quel que soit $m$ (de $1\ \%$ environ à $41\ \%$) : pour la décision, la réduction ne coûte rien. Attention à la colonne `silhouette` : elle **décroît** avec $m$ ($0{,}467\to0{,}284$), non parce que les groupes se dégradent, mais parce que les distances se resserrent en dimension plus grande (3.2.1) : on ne compare pas des silhouettes calculées dans des espaces de dimensions différentes.

## Exercices

### Exercice 3.1 ⭐ — Silhouette à la main (section 3.1.2)

Cinq points sur une droite : $1,\ 3,\ 7,\ 9,\ 11$, partagés en $A=\{1,3\}$ et $B=\{7,9,11\}$. Calculez la silhouette de chaque point et la silhouette moyenne.

### Exercice 3.2 ⭐⭐ — Calinski–Harabasz et Davies–Bouldin à la main (section 3.1.2)

Pour la même partition que l'exercice 3.1, calculez la dispersion intra $W$, la dispersion inter $B$, l'indice de Calinski–Harabasz et l'indice de Davies–Bouldin (avec la distance moyenne au centre comme $s_j$).

### Exercice 3.3 ⭐⭐ — L'indice de Rand ajusté à partir d'un tableau croisé (section 3.1.5)

Un algorithme classe 70 clients en trois groupes, alors que la vérité compte trois classes. Le tableau croisé (lignes : groupes trouvés ; colonnes : vraies classes) est

$$\begin{pmatrix}20&5&0\\3&15&2\\0&4&21\end{pmatrix}.$$

Calculez l'ARI et la pureté.

### Exercice 3.4 ⭐⭐ — L'inertie ne peut que décroître (section 3.1.1)

Montrez que l'inertie minimale $W_k^*$ de k-means vérifie $W_{k+1}^*\le W_k^*$, puis expliquez pourquoi cette monotonie interdit de choisir $k$ en minimisant l'inertie. Vérifiez numériquement sur les clients.

### Exercice 3.5 ⭐⭐ — Appliquer la règle de Tibshirani (section 3.1.3)

Une statistique de l'écart a donné, pour $k=1,\dots,6$ :
$\mathrm{Gap}=(0\,;\,0{,}30\,;\,0{,}62\,;\,0{,}75\,;\,0{,}77\,;\,0{,}74)$ et $s=(0{,}01\,;\,0{,}01\,;\,0{,}01\,;\,0{,}02\,;\,0{,}04\,;\,0{,}02)$.
Quel $k$ retient la règle « plus petit $k$ tel que $\mathrm{Gap}(k)\ge\mathrm{Gap}(k+1)-s_{k+1}$ » ? Quel est l'argmax de l'écart ? Pourquoi les deux diffèrent-ils ?

### Exercice 3.6 ⭐ — Part de variance et erreur de reconstruction (section 3.2.2)

Les valeurs propres de la matrice de corrélation de six variables sont $4{,}2\,;\,2{,}1\,;\,0{,}9\,;\,0{,}5\,;\,0{,}2\,;\,0{,}1$. Quelle part de variance gardent $1$, $2$, $3$ composantes ? Combien de composantes pour garder au moins $90\ \%$ ? Quelle est l'erreur relative de reconstruction avec $2$ composantes ?

### Exercice 3.7 ⭐⭐ — Le lemme de Johnson–Lindenstrauss en chiffres (section 3.2.6)

On a $n=10\,000$ observations décrites par $p=50\,000$ variables. Quelle dimension $k$ garantit, d'après la borne du livre, une conservation des distances à $\pm\varepsilon$ pour $\varepsilon=0{,}25$ puis $\varepsilon=0{,}1$ ? Commentez le résultat par rapport à $p$ et à $n$.

### Exercice 3.8 ⭐⭐⭐ — La concentration des distances, démontrée (section 3.2.1)

Soient $\mathbf X,\mathbf Y$ deux points indépendants, uniformes dans $[0,1]^d$. (a) Calculez l'espérance et la variance de $D^2=\|\mathbf X-\mathbf Y\|^2$. (b) Montrez que $\sqrt{\operatorname{Var}(D^2)}/\mathbb E[D^2]=\sqrt{1{,}4/d}$. (c) En déduire, par la méthode delta, la dispersion relative de $D$, et la comparer à celle du livre en dimension 50 et 1 000.

### Exercice 3.9 ⭐⭐ — DBSCAN à la main en dimension 2 (section 3.3.1)

Neuf points : $P_1(0;0)$, $P_2(1;0)$, $P_3(0;1)$, $P_4(1;1)$, $P_5(2;1{,}5)$, $P_6(5;5)$, $P_7(5{,}5;5)$, $P_8(5;5{,}5)$, $P_9(10;0)$. Avec $\varepsilon=1{,}2$ et $m=3$ (le point compte dans son voisinage), classez chaque point (cœur, bordure, bruit) et donnez les groupes.

### Exercice 3.10 ⭐⭐ — Un tour d'EM (section 3.3.3)

Quatre valeurs $0\,;\,2\,;\,3\,;\,6$, un mélange de deux lois normales de même écart-type $1$ et de poids égaux, de moyennes initiales $\mu_1=0$ et $\mu_2=6$. Calculez les responsabilités, puis les nouvelles moyennes et poids après un tour.

### Exercice 3.11 ⭐⭐ — Compter les paramètres, calculer un BIC (section 3.3.3)

(a) Combien de paramètres libres a un mélange gaussien à covariances complètes de $K$ composantes en dimension $p$ ? Évaluez pour $p=7$, $K=4$ puis $K=5$. (b) Avec $n=12\,000$, $\ln\hat L_4=-52\,500$ et $\ln\hat L_5=-51\,300$, quel $K$ minimise le BIC ? (c) De combien devrait au moins augmenter la log-vraisemblance quand on passe de $K=4$ à $K=5$ pour que le BIC préfère $K=5$ ?

### Exercice 3.12 ⭐⭐ — La perplexité de t-SNE (section 3.4.1)

La probabilité de choisir comme voisin chacun des quatre voisins d'un point est $(0{,}5\,;\,0{,}25\,;\,0{,}125\,;\,0{,}125)$. (a) Calculez son entropie en bits puis sa perplexité. (b) Quelle est la perplexité d'une loi uniforme sur $m$ voisins ? (c) Interprétez : que signifie « choisir la perplexité $30$ » ?

## Corrigés

### Corrigé 3.1

- Point $1$ : $a=|1-3|=2$ ; $b=(6+8+10)/3=8$ ; $s=1-2/8=0{,}75$.
- Point $3$ : $a=2$ ; $b=(4+6+8)/3=6$ ; $s=1-2/6\approx0{,}667$.
- Point $7$ : $a=(|7-9|+|7-11|)/2=(2+4)/2=3$ ; $b=(|7-1|+|7-3|)/2=(6+4)/2=5$ ; $s=1-3/5=0{,}4$.
- Point $9$ : $a=(2+2)/2=2$ ; $b=(8+6)/2=7$ ; $s=1-2/7\approx0{,}714$.
- Point $11$ : $a=(4+2)/2=3$ ; $b=(10+8)/2=9$ ; $s=1-3/9\approx0{,}667$.

Silhouette moyenne : $(0{,}75+0{,}667+0{,}4+0{,}714+0{,}667)/5\approx0{,}640$. Vérification :

```python
from sklearn.metrics import silhouette_samples
pts = np.array([[1.], [3.], [7.], [9.], [11.]]); lab = np.array([0, 0, 1, 1, 1])
print(silhouette_samples(pts, lab).round(3), silhouette_samples(pts, lab).mean().round(3))
```
<!--sortie-->
```text
[0.75  0.667 0.4   0.714 0.667] 0.64
```

### Corrigé 3.2

Les moyennes sont $2$ (groupe $A$) et $9$ (groupe $B$) ; la moyenne générale est $31/5=6{,}2$.
$W=(1+1)+(4+0+4)=10$ ; $B=2(2-6{,}2)^2+3(9-6{,}2)^2=35{,}28+23{,}52=58{,}8$ (on vérifie $W+B=68{,}8=\sum(x_i-6{,}2)^2$).
$\mathrm{CH}=\dfrac{58{,}8/(2-1)}{10/(5-2)}=17{,}64$. Distances moyennes au centre : $s_A=1$, $s_B=(2+0+2)/3\approx1{,}333$ ; distance entre centres : $7$ ; $\mathrm{DB}=(1+1{,}333)/7\approx0{,}333$.

```python
print(round(calinski_harabasz_score(pts, lab), 2), round(davies_bouldin_score(pts, lab), 3))
```
<!--sortie-->
```text
17.64 0.333
```

### Corrigé 3.3

$\sum_{ij}\binom{n_{ij}}2=\binom{20}2+\binom52+\binom32+\binom{15}2+\binom22+\binom42+\binom{21}2=190+10+3+105+1+6+210=525$.
Totaux des lignes $25,20,25$ : $\sum_i\binom{a_i}2=300+190+300=790$. Totaux des colonnes $23,24,23$ : $\sum_j\binom{b_j}2=253+276+253=782$. $\binom{70}2=2\,415$.
Espérance au hasard : $790\times782/2\,415\approx255{,}8$ ; maximum : $(790+782)/2=786$.
$\mathrm{ARI}=\dfrac{525-255{,}8}{786-255{,}8}\approx0{,}508$. Pureté : $(20+15+21)/70=0{,}8$ : la pureté (80 %) paraît bien meilleure que l'ARI, qui retire la part due au hasard.

```python
M = np.array([[20, 5, 0], [3, 15, 2], [0, 4, 21]])
lig, col = np.indices((3, 3))
trouve, vrai = np.repeat(lig.ravel(), M.ravel()), np.repeat(col.ravel(), M.ravel())   # une ligne par client
print(round(adjusted_rand_score(vrai, trouve), 3), M.max(axis=1).sum() / M.sum())
```
<!--sortie-->
```text
0.508 0.8
```

(Attention : la pureté prend le maximum de chaque **ligne** ; ici $20,15,21$.)

### Corrigé 3.4

*Preuve.* Soit $(C_1,\dots,C_k;\boldsymbol\mu_1,\dots,\boldsymbol\mu_k)$ une solution optimale à $k$ groupes, d'inertie $W_k^*$. Si un groupe contient au moins deux points distincts, on en retire un point $\mathbf x$ du groupe $j$ pour en faire un groupe à lui seul, de centre $\mathbf x$ : l'inertie de ce point devient $0$, et celle du groupe $j$, recalculée avec sa nouvelle moyenne, ne peut pas augmenter (la moyenne minimise la somme des carrés). On obtient une partition à $k+1$ groupes d'inertie $\le W_k^*$, donc $W_{k+1}^*\le W_k^*$. Au maximum ($k=n$), l'inertie est nulle. *Conséquence* : minimiser l'inertie sur $k$ conduirait toujours à prendre $k$ le plus grand possible ; elle ne peut servir qu'à repérer un **coude**, ou doit être remplacée par un critère qui pénalise $k$.

```python
print([round(KMeans(k, n_init=5, random_state=0).fit(Z).inertia_) for k in range(1, 9)])
```
<!--sortie-->
```text
[84000, 62970, 45645, 36775, 32812, 30349, 28889, 27542]
```

### Corrigé 3.5

Règle : $k=1$ : $0\ge0{,}30-0{,}01$ ? non. $k=2$ : $0{,}30\ge0{,}62-0{,}01$ ? non. $k=3$ : $0{,}62\ge0{,}75-0{,}02=0{,}73$ ? non. $k=4$ : $0{,}75\ge0{,}77-0{,}04=0{,}73$ ? **oui** : la règle retient $k=4$. L'argmax est $k=5$ ($0{,}77$). Les deux diffèrent parce que la règle accepte un $k$ plus petit dès que le gain suivant ($0{,}02$) est inférieur à l'incertitude de l'estimation ($s_5=0{,}04$) : elle préfère le modèle le plus simple à gain statistiquement indiscernable.

### Corrigé 3.6

Somme des valeurs propres : $8$ (six variables standardisées). Part de variance : $1$ composante : $4{,}2/8=52{,}5\ \%$ ; $2$ : $6{,}3/8=78{,}75\ \%$ ; $3$ : $7{,}2/8=90\ \%$. Il faut donc **3** composantes pour au moins $90\ \%$. Erreur relative de reconstruction avec $2$ composantes : $1-0{,}7875=0{,}2125$, soit $21{,}25\ \%$ (théorème d'Eckart–Young).

```python
vp = np.array([4.2, 2.1, 0.9, 0.5, 0.2, 0.1]); print(np.cumsum(vp) / vp.sum())
```
<!--sortie-->
```text
[0.525  0.7875 0.9    0.9625 0.9875 1.    ]
```

### Corrigé 3.7

$k\ge4\ln n/(\varepsilon^2/2-\varepsilon^3/3)$ avec $\ln10\,000\approx9{,}21$. Pour $\varepsilon=0{,}25$ : dénominateur $0{,}03125-0{,}00521=0{,}02604$, donc $k\ge1\,415$ (la bibliothèque donne $1\,414$, par arrondi). Pour $\varepsilon=0{,}1$ : $0{,}005-0{,}00033=0{,}00467$, donc $k\ge7\,894$. On passe de $50\,000$ variables à environ $1\,400$ (réduction par 35) pour $\pm25\ \%$ sur les distances, mais à $7\,900$ (réduction par 6) pour $\pm10\ \%$. La borne ne dépend pas de $p$, et seulement logarithmiquement de $n$ : elle est précieuse quand $p$ est énorme, mais elle devient **moins que triviale** quand $\varepsilon$ est petit.

```python
from sklearn.random_projection import johnson_lindenstrauss_min_dim
print(johnson_lindenstrauss_min_dim(10_000, eps=0.25), johnson_lindenstrauss_min_dim(10_000, eps=0.1))
```
<!--sortie-->
```text
1414 7894
```

### Corrigé 3.8

(a) Pour une coordonnée, $U=X_j-Y_j$ est triangulaire sur $[-1,1]$ : $\mathbb E[U^2]=\mathbb E[X^2]-2\mathbb E[X]\mathbb E[Y]+\mathbb E[Y^2]=\tfrac13-\tfrac12+\tfrac13=\tfrac16$ et $\mathbb E[U^4]=\tfrac1{15}$ (intégrale de la densité triangulaire). Donc $\operatorname{Var}(U^2)=\tfrac1{15}-\tfrac1{36}=\tfrac7{180}$. Par indépendance des coordonnées, $\mathbb E[D^2]=d/6$ et $\operatorname{Var}(D^2)=7d/180$.
(b) $\dfrac{\sqrt{7d/180}}{d/6}=\sqrt{\dfrac{7\times36}{180\,d}}=\sqrt{\dfrac{1{,}4}{d}}$.
(c) Par la méthode delta, $D=\sqrt{D^2}$ a une dispersion relative moitié moindre : $\approx0{,}5\sqrt{1{,}4/d}\approx0{,}5916/\sqrt d$. Pour $d=50$ : $0{,}0837$ ; pour $d=1\,000$ : $0{,}0187$. Le livre mesure $0{,}086$ et $0{,}018$ (tableau de 3.2.1) : l'accord est bon.

```python
for d in (50, 1000): print(d, round(0.5 * np.sqrt(1.4 / d), 4))
```
<!--sortie-->
```text
50 0.0837
1000 0.0187
```

### Corrigé 3.9

Distances utiles : $P_1P_2=P_1P_3=P_2P_4=P_3P_4=1$ ; $P_2P_3=P_1P_4=\sqrt2\approx1{,}414>1{,}2$ ; $P_4P_5=\sqrt{1+0{,}25}\approx1{,}118\le1{,}2$ ; $P_6P_7=P_6P_8=0{,}5$ ; $P_7P_8\approx0{,}707$.
Voisinages (avec le point lui-même) : $P_1:\{P_1,P_2,P_3\}$ (3, **cœur**) ; $P_2:\{P_2,P_1,P_4\}$ (3, cœur) ; $P_3:\{P_3,P_1,P_4\}$ (3, cœur) ; $P_4:\{P_4,P_2,P_3,P_5\}$ (4, cœur) ; $P_5:\{P_5,P_4\}$ (2, pas un cœur, mais voisin du cœur $P_4$ : **bordure**) ; $P_6,P_7,P_8$ : chacun a 3 points : **cœurs** ; $P_9$ : seul, **bruit**. Groupes : $\{P_1,\dots,P_5\}$ et $\{P_6,P_7,P_8\}$ ; bruit : $P_9$.

```python
P = np.array([[0, 0], [1, 0], [0, 1], [1, 1], [2, 1.5], [5, 5], [5.5, 5], [5, 5.5], [10, 0]])
db = DBSCAN(eps=1.2, min_samples=3).fit(P); print(db.labels_, [int(i) + 1 for i in sorted(db.core_sample_indices_)])
```
<!--sortie-->
```text
[ 0  0  0  0  0  1  1  1 -1] [1, 2, 3, 4, 6, 7, 8]
```

### Corrigé 3.10

Responsabilité du groupe 1 : $\gamma_1(x)=1/\big(1+e^{-[(x-6)^2-x^2]/2}\big)$. $x=0$ : $(36-0)/2=18$, $\gamma_1\approx1$ ; $x=2$ : $(16-4)/2=6$, $\gamma_1=1/(1+e^{-6})\approx0{,}9975$ ; $x=3$ : $(9-9)/2=0$, $\gamma_1=0{,}5$ ; $x=6$ : $(0-36)/2=-18$, $\gamma_1\approx0$.
Nouvelles moyennes : $\mu_1=\dfrac{0\times1+2\times0{,}9975+3\times0{,}5}{1+0{,}9975+0{,}5}\approx1{,}399$ ; avec $\gamma_2=1-\gamma_1$ : $\mu_2=\dfrac{2\times0{,}0025+3\times0{,}5+6\times1}{0+0{,}0025+0{,}5+1}\approx4{,}995$. Poids : $\pi_1=2{,}4975/4\approx0{,}624$ et $\pi_2\approx0{,}376$.

```python
xx = np.array([0.0, 2.0, 3.0, 6.0]); g = 1 / (1 + np.exp(-((xx - 6) ** 2 - xx ** 2) / 2)); G = np.column_stack([g, 1 - g])
print(g.round(4), (G * xx[:, None]).sum(0) / G.sum(0), G.sum(0) / 4)
```
<!--sortie-->
```text
[1.     0.9975 0.5    0.    ] [1.39940602 4.99506283] [0.62438184 0.37561816]
```

### Corrigé 3.11

(a) $q=Kp+K\dfrac{p(p+1)}2+(K-1)$ : $p=7$ donne $K\times(7+28)+(K-1)=35K+K-1=36K-1$ : $q=143$ pour $K=4$, $q=179$ pour $K=5$. (b) $\ln n=\ln12\,000\approx9{,}393$. $\mathrm{BIC}_4=105\,000+143\times9{,}393\approx106\,343$ ; $\mathrm{BIC}_5=102\,600+179\times9{,}393\approx104\,281$ : le BIC retient $K=5$. (c) Il faut $-2\Delta\ln\hat L>(179-143)\ln n$, soit $\Delta\ln\hat L>36\times9{,}393/2\approx169$ : le passage à $K=5$ doit gagner **au moins 169 unités** de log-vraisemblance. Ici, le gain est de $1\,200$ : très au-delà du seuil.

```python
n = 12000
print(round(105000 + 143 * np.log(n)), round(102600 + 179 * np.log(n)), round(36 * np.log(n) / 2, 1))
```
<!--sortie-->
```text
106343 104281 169.1
```

### Corrigé 3.12

(a) $H=-\sum p\log_2p=0{,}5\times1+0{,}25\times2+2\times0{,}125\times3=0{,}5+0{,}5+0{,}75=1{,}75$ bits ; perplexité $2^{1{,}75}\approx3{,}36$. (b) Pour la loi uniforme sur $m$ voisins, $H=\log_2m$, donc la perplexité vaut exactement $m$. (c) Choisir la perplexité $30$ revient à régler, pour **chaque** point, la largeur $\sigma_i$ de sorte que sa distribution de voisinage ait une entropie équivalente à celle d'une loi uniforme sur environ $30$ voisins : c'est un nombre **effectif** de voisins, qui s'adapte à la densité locale.

```python
p = np.array([0.5, 0.25, 0.125, 0.125]); print(2 ** (-(p * np.log2(p)).sum()))
```
<!--sortie-->
```text
3.363585661014858
```
