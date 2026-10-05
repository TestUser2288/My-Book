# Chapitre 9 : ➕ Statistique spatiale — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 9 du livre. Il contient le **code complet** que le livre exécute « en coulisses » (sept applications guidées, qui reconstruisent pas à pas les distances, les indices de Moran et de Geary, le variogramme, le krigeage et les processus ponctuels) puis **douze exercices corrigés**. Aucune bibliothèque de cartographie : NumPy, SciPy, matplotlib (et `mgcv` en R pour un point de comparaison). Les données sont **simulées** et le décor est une **région fictive** (villes, zones et coordonnées inventées) ; les fichiers sont dans `donnees/` (`ch09-zones.csv`, `ch09-livraisons.csv`, `clients.csv`) et leurs générateurs dans `build/donnees_ch09.py`.
>
> Le fichier est exécuté **d'un seul tenant, de haut en bas** : les fonctions définies dans une application servent dans les suivantes et dans les corrigés. Si vous travaillez dans un notebook, exécutez les cellules dans l'ordre.

## Applications

### Application 9.1 — Distances et cartes (section 9.1)

**Objectif.** Repérer des villes par leurs coordonnées, calculer des distances sur la sphère (haversine), mesurer l'erreur de deux raccourcis, et dessiner des cartes sans fond de carte.

**Étape 1 : les villes et la formule de haversine.** Dix villes fictives ; la fonction accepte des tableaux grâce à la diffusion de NumPy.

```python
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

villes = pd.DataFrame({
    "ville": ["Ville A", "Ville B", "Ville C", "Ville D", "Ville E", "Ville F", "Ville G", "Ville H", "Ville I", "Ville J"],
    "lat":   [47.30, 46.90, 46.40, 45.80, 45.30, 44.70, 47.00, 46.00, 45.20, 44.30],
    "lon":   [ 3.20,  4.60,  3.60,  4.90,  3.40,  5.30,  6.40,  6.70,  6.60,  3.70],
})
```

```python
R = 6371.0   # rayon moyen de la Terre, en km

def haversine(lat1, lon1, lat2, lon2):
    """Distance de grand cercle en km (arguments en degrés ; NumPy diffuse sur les tableaux)."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

print("1 degré de latitude          :", round(float(haversine(46.0, 4.0, 47.0, 4.0)), 1), "km")
print("1 degré de longitude à 45° N :", round(float(haversine(45.0, 4.0, 45.0, 5.0)), 1), "km")
print("Ville A - Ville B            :", round(float(haversine(47.30, 3.20, 46.90, 4.60)), 1), "km  (calcul à la main : 114,9)")
```
<!--sortie-->
```text
1 degré de latitude          : 111.2 km
1 degré de longitude à 45° N : 78.6 km
Ville A - Ville B            : 114.9 km  (calcul à la main : 114,9)
```

**Étape 2 : la matrice des distances.** Transformer les vecteurs en colonnes et en lignes calcule les $10\times10$ paires d'un coup. La matrice est symétrique, de diagonale nulle ; la plus grande distance est entre G et J (366 km), la plus petite entre H et I (89 km).

```python
lat, lon = villes["lat"].to_numpy(), villes["lon"].to_numpy()
D = haversine(lat[:, None], lon[:, None], lat[None, :], lon[None, :])     # (10, 10)
lettres = [v[-1] for v in villes["ville"]]
print(pd.DataFrame(D.round(0).astype(int), index=lettres, columns=lettres).to_string())
print("matrice symétrique :", np.allclose(D, D.T), "| diagonale nulle :", np.allclose(np.diag(D), 0))
```
<!--sortie-->
```text
     A    B    C    D    E    F    G    H    I    J
A    0  115  105  211  223  331  244  304  350  336
B  115    0   94  124  201  251  137  189  244  297
C  105   94    0  120  123  231  224  243  268  234
D  211  124  120    0  129  126  176  141  148  192
E  223  201  123  129    0  164  299  268  251  114
F  331  251  231  126  164    0  270  181  116  134
G  244  137  224  176  299  270    0  114  201  366
H  304  189  243  141  268  181  114    0   89  302
I  350  244  268  148  251  116  201   89    0  250
J  336  297  234  192  114  134  366  302  250    0
matrice symétrique : True | diagonale nulle : True
```

**Étape 3 : l'erreur des raccourcis.** (a) traiter les degrés comme des unités égales ; (b) la projection équirectangulaire centrée sur la latitude moyenne $\varphi_0$. Le raccourci (a) se trompe de 1 % à 46 % selon la direction du trajet, le raccourci (b) de moins de 2,5 %.

```python
def naif(lat1, lon1, lat2, lon2):
    return 111.19 * np.hypot(lat2 - lat1, lon2 - lon1)

def equirect(lat1, lon1, lat2, lon2, lat0):
    c = np.cos(np.radians(lat0))
    return R * np.radians(1) * np.hypot(lat2 - lat1, (lon2 - lon1) * c)

lat0 = villes["lat"].mean()
paires = [("Ville A", "Ville B"), ("Ville A", "Ville J"), ("Ville A", "Ville G"), ("Ville G", "Ville J"), ("Ville C", "Ville H")]
lignes = []
for a, b in paires:
    ra, rb = villes.set_index("ville").loc[a], villes.set_index("ville").loc[b]
    vrai = float(haversine(ra.lat, ra.lon, rb.lat, rb.lon))
    n = float(naif(ra.lat, ra.lon, rb.lat, rb.lon))
    e = float(equirect(ra.lat, ra.lon, rb.lat, rb.lon, lat0))
    lignes.append({"paire": f"{a[-1]}-{b[-1]}", "haversine_km": vrai, "degres_bruts_km": n, "erreur_%": 100 * (n / vrai - 1),
                   "equirect_km": e, "erreur_eq_%": 100 * (e / vrai - 1)})
print(pd.DataFrame(lignes).round(1).to_string(index=False))
```
<!--sortie-->
```text
paire  haversine_km  degres_bruts_km  erreur_%  equirect_km  erreur_eq_%
  A-B         114.9            161.9      40.9        117.1          1.9
  A-J         335.8            338.2       0.7        335.8         -0.0
  A-G         244.3            357.4      46.3        249.9          2.3
  G-J         366.3            424.6      15.9        365.8         -0.1
  C-H         242.7            347.5      43.2        244.0          0.6
```

**Étape 4 : une carte à symboles proportionnels.** La surface des disques est proportionnelle au nombre de clients (villes A à E du fichier `clients.csv`). À gauche, les degrés sont dessinés comme des unités égales ; à droite, le rapport d'aspect $1/\cos\varphi_0$ rétablit les proportions.

```python
clients = pd.read_csv("donnees/clients.csv")
par_ville = clients.groupby("ville").agg(clients=("id_client", "size"), depense=("depense_annuelle", "mean")).round(1)
print(par_ville.to_string())

carte = villes.merge(par_ville, left_on="ville", right_index=True, how="left")   # F à J : pas de clients dans ce fichier
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
```
<!--sortie-->
```text
         clients  depense
ville                    
Autre        301    274.0
Ville A      208    217.9
Ville B      252    243.6
Ville C      282    245.6
Ville D      337    247.0
Ville E      620    245.5
```

```python
fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.2))
for ax, titre, corrige in zip(axes, ["Degrés traités comme des unités égales", "Aspect corrigé (1 / cos de la latitude)"], [False, True]):
    ax.scatter(carte["lon"], carte["lat"], s=18, color=ORANGE, zorder=3)
    ax.scatter(carte["lon"], carte["lat"], s=carte["clients"].fillna(0) * 1.5, color=BLEU, alpha=0.35, zorder=2)
    for _, r in carte.iterrows():
        ax.annotate(r["ville"][-1], (r["lon"], r["lat"]), xytext=(6, 5), ha="left", textcoords="offset points", fontsize=9)
    ax.set_title(titre, fontsize=10)
    ax.set_xlabel("longitude (°E)")
    ax.set_xlim(2.4, 7.6)
    ax.set_ylim(43.8, 47.8)
    ax.set_aspect(1 / np.cos(np.radians(lat0)) if corrige else 1.0)
axes[0].set_ylabel("latitude (°N)")
plt.tight_layout()
plt.savefig("figures/ch09-carte-villes.png", dpi=200, bbox_inches="tight")
```

**Étape 5 : les deux jeux du chapitre, côte à côte.** Une carte choroplèthe pour les zones (surfacique) et un nuage de points colorés pour les livraisons (géostatistique).

```python
zones = pd.read_csv("donnees/ch09-zones.csv")
liv = pd.read_csv("donnees/ch09-livraisons.csv")
print("zones :", zones.shape, "| livraisons :", liv.shape)
print(liv["delai_jours"].describe().round(2).to_string())
```
<!--sortie-->
```text
zones : (144, 8) | livraisons : (200, 4)
count    200.00
mean       4.27
std        1.10
min        1.59
25%        3.62
50%        4.26
75%        5.07
max        7.53
```

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))
grille = zones["ventes_hab"].to_numpy().reshape(12, 12)                   # une case = 5 km x 5 km
im = ax1.imshow(grille, origin="lower", extent=(0, 60, 0, 60), cmap="Blues")
ax1.set_title("Ventes par habitant (€) par zone")
ax1.set_xlabel("x (km)"); ax1.set_ylabel("y (km)")
fig.colorbar(im, ax=ax1, shrink=0.8, label="€ par habitant")

sc = ax2.scatter(liv["x"], liv["y"], c=liv["delai_jours"], cmap="Oranges", s=46, edgecolor="#555555", linewidth=0.3)
ax2.set_title("Délai de livraison (jours) à 200 adresses")
ax2.set_xlabel("x (km)"); ax2.set_ylabel("y (km)")
ax2.set_aspect("equal")
fig.colorbar(sc, ax=ax2, shrink=0.8, label="jours")
plt.tight_layout()
plt.savefig("figures/ch09-donnees-chapitre.png", dpi=200, bbox_inches="tight")
```

**Pour aller plus loin.** Remplacez la distance à vol d'oiseau par une matrice de temps de trajet inventée (non symétrique) et recalculez la carte : quelles propriétés des distances sont indispensables aux outils du chapitre ?

### Application 9.2 — Les ventes par zone : Moran, Geary et indices locaux (section 9.2)

**Objectif.** Construire les matrices de voisinage, programmer l'indice de Moran (hand-check sur une grille $3\times3$), le tester par approximation normale et par permutations, mesurer sa sensibilité au choix de $W$, puis l'indice de Geary et les indices locaux (LISA) corrigés par Benjamini-Hochberg.

**Étape 1 : la grille $3\times3$ et la standardisation par ligne.** Les coins ont 2 voisines, les bords 3, le centre 4 : $S_0=24$.

```python
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

def contiguite_tour(n_lig, n_col):
    """Matrice binaire des voisins par un côté (haut, bas, gauche, droite)."""
    n = n_lig * n_col
    W = np.zeros((n, n))
    for i in range(n_lig):
        for j in range(n_col):
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if 0 <= i + di < n_lig and 0 <= j + dj < n_col:
                    W[i * n_col + j, (i + di) * n_col + (j + dj)] = 1
    return W

W3 = contiguite_tour(3, 3)
print(W3.astype(int))
print("nombre de voisins par zone :", W3.sum(axis=1).astype(int))
print("S0 (somme de tous les poids) :", int(W3.sum()))
```
<!--sortie-->
```text
[[0 1 0 1 0 0 0 0 0]
 [1 0 1 0 1 0 0 0 0]
 [0 1 0 0 0 1 0 0 0]
 [1 0 0 0 1 0 1 0 0]
 [0 1 0 1 0 1 0 1 0]
 [0 0 1 0 1 0 0 0 1]
 [0 0 0 1 0 0 0 1 0]
 [0 0 0 0 1 0 1 0 1]
 [0 0 0 0 0 1 0 1 0]]
nombre de voisins par zone : [2 3 2 3 4 3 2 3 2]
S0 (somme de tous les poids) : 24
```

```python
def std_lignes(W):
    """Standardise par ligne : chaque ligne somme à 1 (les lignes de zéros sont laissées intactes)."""
    s = W.sum(axis=1, keepdims=True)
    return np.divide(W, s, out=np.zeros_like(W), where=s > 0)

W3s = std_lignes(W3)
print(np.round(W3s[4], 2), "<- ligne du centre : 1/4 pour chacun de ses 4 voisins")
print("somme de chaque ligne :", W3s.sum(axis=1))
```
<!--sortie-->
```text
[0.   0.25 0.   0.25 0.   0.25 0.   0.25 0.  ] <- ligne du centre : 1/4 pour chacun de ses 4 voisins
somme de chaque ligne : [1. 1. 1. 1. 1. 1. 1. 1. 1.]
```

**Étape 2 : l'indice de Moran.** Sur la progression 1..9 on retrouve $I=0{,}5$ à la main, sur le damier $-1$ ; avec les poids standardisés, $0{,}556$ ; l'espérance sous le hasard est $-1/(n-1)=-0{,}125$.

```python
def moran(y, W):
    """Indice de Moran de y pour la matrice de poids W (standardisée ou non)."""
    z = np.asarray(y, dtype=float) - np.mean(y)
    return len(z) / W.sum() * (z @ W @ z) / (z @ z)

progression = np.arange(1, 10)
damier = np.array([1, 9, 1, 9, 1, 9, 1, 9, 1], dtype=float)
print("progression 1..9, poids binaires     :", round(moran(progression, W3), 4))
print("damier,           poids binaires     :", round(moran(damier, W3), 4))
print("progression 1..9, poids standardisés :", round(moran(progression, W3s), 4))
print("E[I] sans autocorrélation, n = 9     :", round(-1 / (9 - 1), 4))
```
<!--sortie-->
```text
progression 1..9, poids binaires     : 0.5
damier,           poids binaires     : -1.0
progression 1..9, poids standardisés : 0.5556
E[I] sans autocorrélation, n = 9     : -0.125
```

**Étape 3 : le générateur des ventes (modèle autorégressif spatial).** On propage des bruits indépendants par $z=(I-\rho W)^{-1}e$ avec $\rho=0{,}9$ ; le résultat est identique au fichier fourni. La variable `ventes_bruit` n'a aucune structure spatiale : c'est le témoin.

```python
def contiguite_reine(n_lig, n_col):
    """Voisins par un côté ou un coin (8 directions)."""
    n = n_lig * n_col
    W = np.zeros((n, n))
    for i in range(n_lig):
        for j in range(n_col):
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di, dj) != (0, 0) and 0 <= i + di < n_lig and 0 <= j + dj < n_col:
                        W[i * n_col + j, (i + di) * n_col + (j + dj)] = 1
    return W
```

*Le générateur proprement dit :*

```python
def grille_zones(seed=9, n_lig=12, n_col=12, rho=0.9):
    rng = np.random.default_rng(seed)
    W = std_lignes(contiguite_reine(n_lig, n_col))
    n = n_lig * n_col
    e = rng.normal(size=n)
    z = np.linalg.solve(np.eye(n) - rho * W, e)               # z = (I - rho W)^-1 e
    pop = np.round(rng.lognormal(8.5, 0.5, n)).astype(int)
    lig, col = np.divmod(np.arange(n), n_col)
    return pd.DataFrame({"id": np.arange(n), "lig": lig, "col": col, "x": col * 5.0 + 2.5, "y": lig * 5.0 + 2.5,
                         "population": pop, "ventes_hab": np.round(50 + 8 * z, 2),
                         "ventes_bruit": np.round(rng.normal(50, 8, n), 2)})

zones = grille_zones()
fichier = pd.read_csv("donnees/ch09-zones.csv")
print("identique au fichier fourni :", np.allclose(zones[["ventes_hab", "ventes_bruit"]], fichier[["ventes_hab", "ventes_bruit"]]))
print(zones[["ventes_hab", "ventes_bruit"]].describe().round(2).to_string())
```
<!--sortie-->
```text
identique au fichier fourni : True
       ventes_hab  ventes_bruit
count      144.00        144.00
mean        52.89         50.22
std         13.51          8.15
min         19.29         29.97
25%         44.29         43.90
50%         53.43         50.36
75%         62.67         56.50
max         81.49         71.64
```

**Étape 4 : test de Moran, par la formule normale et par permutations.** Pour `ventes_hab` : $I=0{,}621$, $z=14{,}2$, p-valeur par permutations $10^{-4}$ (le minimum avec 9 999 permutations) ; pour le témoin : $I=-0{,}021$, p-valeur $0{,}61$.

```python
W = std_lignes(contiguite_reine(12, 12))
n = len(zones)

def stats_poids(W):
    S0 = W.sum()
    S1 = 0.5 * ((W + W.T) ** 2).sum()
    S2 = ((W.sum(axis=1) + W.sum(axis=0)) ** 2).sum()
    return S0, S1, S2

def moran_normal(y, W):
    """I, E[I], écart-type sous normalité et z_I."""
    n = len(y)
    S0, S1, S2 = stats_poids(W)
    E = -1 / (n - 1)
    var = (n**2 * S1 - n * S2 + 3 * S0**2) / ((n**2 - 1) * S0**2) - E**2
    I = moran(y, W)
    return I, E, np.sqrt(var), (I - E) / np.sqrt(var)
```

*Les fonctions de test, puis leur application aux deux variables :*

```python
def moran_permutations(y, W, B=9999, seed=1):
    """B valeurs de I obtenues en mélangeant y sur les zones."""
    rng = np.random.default_rng(seed)
    z = np.asarray(y, dtype=float) - np.mean(y)
    idx = np.argsort(rng.random((B, len(z))), axis=1)          # B permutations de 0..n-1
    Z = z[idx]                                                  # chaque ligne est un mélange de z
    return len(z) / W.sum() * (((Z @ W) * Z).sum(axis=1)) / (z @ z)

lignes = []
for nom in ["ventes_hab", "ventes_bruit"]:
    y = zones[nom].to_numpy()
    I, E, sd, zI = moran_normal(y, W)
    sim = moran_permutations(y, W)
    p_perm = (1 + (sim >= I).sum()) / (len(sim) + 1)
    lignes.append({"variable": nom, "I": I, "E[I]": E, "ecart_type": sd, "z": zI, "p_normale": stats.norm.sf(zI),
                   "p_permutation": p_perm, "sd_perm": sim.std()})
res = pd.DataFrame(lignes)
with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 150):
    print(res.to_string(index=False))
```
<!--sortie-->
```text
    variable       I      E[I]  ecart_type       z  p_normale  p_permutation  sd_perm
  ventes_hab  0.6207 -0.006993     0.04429   14.17  6.802e-46         0.0001  0.04468
ventes_bruit -0.0214 -0.006993     0.04429 -0.3253     0.6275         0.6132  0.04445
```

**Étape 5 : le diagramme de Moran** (nuage de $Wz$ contre $z$ ; la pente est $I$) et la loi de $I$ obtenue en mélangeant les valeurs.

```python
BLEU, ORANGE, AQUA, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
y = zones["ventes_hab"].to_numpy()
zc = y - y.mean()
lag = W @ zc
I_obs = moran(y, W)
sim = moran_permutations(y, W)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
ax1.scatter(zc, lag, s=16, color=BLEU, alpha=0.7)
pente, ordonnee = np.polyfit(zc, lag, 1)
xs = np.array([zc.min(), zc.max()])
ax1.plot(xs, pente * xs + ordonnee, color=ORANGE, lw=2)
ax1.axhline(0, color="#999999", lw=0.8); ax1.axvline(0, color="#999999", lw=0.8)
ax1.set_xlabel("écart à la moyenne de la zone  z"); ax1.set_ylabel("moyenne des écarts des voisines  W z")
ax1.set_title(f"Diagramme de Moran (pente = I = {pente:.3f})")
```

*La loi de $I$ par permutations :*

```python
ax2.hist(sim, bins=50, color="#b9d0f0", edgecolor="white")
ax2.axvline(I_obs, color=ORANGE, lw=2)
ax2.annotate(f"I observé = {I_obs:.3f}", (I_obs, 400), xytext=(-8, 0), textcoords="offset points", ha="right", color=ORANGE)
ax2.set_xlabel("I après mélange des valeurs (9999 permutations)"); ax2.set_ylabel("effectif")
ax2.set_title("Ce que produirait le hasard")
plt.tight_layout()
plt.savefig("figures/ch09-moran.png", dpi=200, bbox_inches="tight")
print("pente du diagramme :", round(pente, 4), "| I :", round(I_obs, 4), "| identiques :", np.isclose(pente, I_obs))
```
<!--sortie-->
```text
pente du diagramme : 0.6207 | I : 0.6207 | identiques : True
```

**Étape 6 : sensibilité au choix de $W$.** Cinq définitions du voisinage : $I$ varie de 0,57 à 0,63, la conclusion ne change pas, le témoin reste proche de zéro.

```python
xy = zones[["x", "y"]].to_numpy()
Dd = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(axis=2))      # distances euclidiennes (km)

def poids_bande(D, d):
    W = ((D > 0) & (D <= d)).astype(float)
    return W

def poids_knn(D, k):
    W = np.zeros_like(D)
    for i in range(len(D)):
        voisins = np.argsort(D[i])[1:k + 1]                         # on saute la distance nulle (soi-même)
        W[i, voisins] = 1
    return W
```

*Les cinq matrices et le calcul de $I$ :*

```python
variantes = {
    "tour (distance <= 5 km)": poids_bande(Dd, 5.0),
    "reine (distance <= 7,1 km)": poids_bande(Dd, 7.1),
    "bande de 10 km": poids_bande(Dd, 10.0),
    "4 plus proches voisins": poids_knn(Dd, 4),
    "8 plus proches voisins": poids_knn(Dd, 8),
}
lignes = []
for nom, Wv in variantes.items():
    Ws = std_lignes(Wv)
    sim_v = moran_permutations(y, Ws, B=999, seed=3)
    I_v = moran(y, Ws)
    lignes.append({"definition": nom, "voisins_moyens": Wv.sum(axis=1).mean(), "I": I_v,
                   "I_temoin": moran(zones["ventes_bruit"].to_numpy(), Ws),
                   "p_permutation": (1 + (sim_v >= I_v).sum()) / 1000})
with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 150):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
                definition  voisins_moyens     I  I_temoin  p_permutation
   tour (distance <= 5 km)           3.667 0.627    -0.034          0.001
reine (distance <= 7,1 km)           7.028 0.621    -0.021          0.001
            bande de 10 km          10.361 0.572     0.009          0.001
    4 plus proches voisins           4.000 0.618    -0.013          0.001
    8 plus proches voisins           8.000 0.607     0.011          0.001
```

**Étape 7 : l'indice de Geary.** $C=0{,}395$ pour `ventes_hab` (nettement inférieur à 1), $0{,}991$ pour le témoin.

```python
def geary(y, W):
    y = np.asarray(y, dtype=float)
    z = y - y.mean()
    diff2 = (y[:, None] - y[None, :]) ** 2
    return (len(y) - 1) * (W * diff2).sum() / (2 * W.sum() * (z @ z))

def geary_permutations(y, W, B=999, seed=4):
    rng = np.random.default_rng(seed)
    return np.array([geary(rng.permutation(y), W) for _ in range(B)])

lignes = []
for nom in ["ventes_hab", "ventes_bruit"]:
    yy = zones[nom].to_numpy()
    C = geary(yy, W)
    sim_c = geary_permutations(yy, W)
    lignes.append({"variable": nom, "C": C, "moyenne_perm": sim_c.mean(), "p_perm (C petit)": (1 + (sim_c <= C).sum()) / (len(sim_c) + 1)})
with pd.option_context("display.float_format", "{:.4f}".format, "display.width", 150):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
    variable      C  moyenne_perm  p_perm (C petit)
  ventes_hab 0.3950        1.0033            0.0010
ventes_bruit 0.9909        0.9997            0.4030
```

**Étape 8 : les indices locaux (LISA).** Permutation conditionnelle pour chaque zone, puis correction de Benjamini-Hochberg : 35 zones significatives pour `ventes_hab` (11 HH, 22 LL, 2 LH), aucune pour le témoin (5 zones à $p<0{,}05$ sans correction).

```python
def lisa(y, W, B=999, seed=2):
    """Moran local, quadrant, et p-valeur bilatérale par permutation conditionnelle."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y, dtype=float)
    n = len(y)
    z = y - y.mean()
    m2 = (z @ z) / n
    lag = W @ z
    Ii = z * lag / m2
    pv = np.empty(n)
    for i in range(n):
        voisins = np.flatnonzero(W[i])
        poids = W[i, voisins]
        r = rng.random((B, n))
        r[:, i] = 2.0                                           # exclut la zone i du tirage
        tire = np.argsort(r, axis=1)[:, :len(voisins)]          # valeurs tirées pour les voisins
        sim = z[i] * (z[tire] * poids).sum(axis=1) / m2
        p_haut = (1 + (sim >= Ii[i]).sum()) / (B + 1)
        p_bas = (1 + (sim <= Ii[i]).sum()) / (B + 1)
        pv[i] = min(1.0, 2 * min(p_haut, p_bas))
    quadrant = np.where(z > 0, np.where(lag > 0, "HH", "HL"), np.where(lag > 0, "LH", "LL"))
    return Ii, quadrant, pv
```

*La correction de Benjamini-Hochberg :*

```python
def benjamini_hochberg(p, alpha=0.05):
    """Renvoie un tableau booléen des hypothèses rejetées (FDR contrôlé à alpha)."""
    p = np.asarray(p)
    m = len(p)
    ordre = np.argsort(p)
    ok = p[ordre] <= (np.arange(1, m + 1) / m) * alpha
    rejet = np.zeros(m, dtype=bool)
    if ok.any():
        rejet[ordre[: np.max(np.flatnonzero(ok)) + 1]] = True
    return rejet
```

*Application aux deux variables :*

```python
lignes = []
resultats = {}
for nom in ["ventes_hab", "ventes_bruit"]:
    Ii, quad, pv = lisa(zones[nom].to_numpy(), W)
    rej = benjamini_hochberg(pv)
    resultats[nom] = (Ii, quad, pv, rej)
    comptes = pd.Series(np.where(rej, quad, "non significatif")).value_counts()
    lignes.append({"variable": nom, "somme_Ii/n": Ii.sum() / len(Ii), "I_global": moran(zones[nom].to_numpy(), W),
                   "p<0.05 brut": int((pv < 0.05).sum()), "significatifs (BH)": int(rej.sum()),
                   "HH": int(comptes.get("HH", 0)), "LL": int(comptes.get("LL", 0)),
                   "HL": int(comptes.get("HL", 0)), "LH": int(comptes.get("LH", 0))})
with pd.option_context("display.float_format", "{:.4f}".format, "display.width", 170):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
    variable  somme_Ii/n  I_global  p<0.05 brut  significatifs (BH)  HH  LL  HL  LH
  ventes_hab      0.6207    0.6207           49                  35  11  22   0   2
ventes_bruit     -0.0214   -0.0214            5                   0   0   0   0   0
```

**Étape 9 : la carte des zones significatives.**

```python
couleurs = {"HH": ROUGE, "LL": BLEU, "HL": ORANGE, "LH": AQUA, "ns": "#e8e6df"}
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
for ax, nom in zip(axes, ["ventes_hab", "ventes_bruit"]):
    Ii, quad, pv, rej = resultats[nom]
    cat = np.where(rej, quad, "ns").reshape(12, 12)
    for i in range(12):
        for j in range(12):
            ax.add_patch(plt.Rectangle((j * 5, i * 5), 5, 5, facecolor=couleurs[cat[i, j]], edgecolor="white", linewidth=0.8))
    ax.set_xlim(0, 60); ax.set_ylim(0, 60); ax.set_aspect("equal")
    ax.set_title("ventes par habitant (structurées)" if nom == "ventes_hab" else "témoin (bruit sans structure)", fontsize=10)
    ax.set_xlabel("x (km)")
axes[0].set_ylabel("y (km)")
poignees = [plt.Rectangle((0, 0), 1, 1, facecolor=couleurs[k]) for k in ["HH", "LL", "HL", "LH", "ns"]]
fig.legend(poignees, ["HH : haut entouré de haut", "LL : bas entouré de bas", "HL : haut entouré de bas", "LH : bas entouré de haut", "non significatif"],
           loc="lower center", ncol=5, frameon=False, fontsize=8)
plt.tight_layout(rect=(0, 0.07, 1, 1))
plt.savefig("figures/ch09-lisa.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

**Pour aller plus loin.** Recommencez avec $\rho=0{,}5$ puis $\rho=0{,}95$ : comment évoluent $I$, le nombre de zones significatives et l'écart entre $z$ normal et p-valeur par permutations ?

### Application 9.3 — Quand l'espace trompe la régression (section 9.2.5)

**Objectif.** Mesurer à quel point ignorer l'autocorrélation fausse un test, puis rétablir le niveau avec les moindres carrés généralisés (le modèle SAR rend le blanchiment explicite). On réutilise `W`, `n`, `moran` et `moran_permutations` de l'application 9.2.

**Étape 1 : deux champs sans aucun lien.** 1 000 paires de champs SAR indépendants ($\rho=0{,}9$) ; on régresse l'un sur l'autre par moindres carrés ordinaires et on teste la pente à 5 %. Résultat : **46 %** de rejets au lieu de 5 %, et 5,5 observations indépendantes « efficaces » sur 144.

```python
from scipy import stats

A = np.linalg.inv(np.eye(n) - 0.9 * W)                         # (I - rho W)^-1, rho = 0,9
rng = np.random.default_rng(5)
reps = 1000
Y = A @ rng.normal(size=(n, reps))                             # 1000 champs « y », indépendants entre eux
X = A @ rng.normal(size=(n, reps))                             # 1000 champs « x », indépendants de y

# MCO vectorisée : pente et test de Student sur la pente, pour chacune des 1000 paires
xc, yc = X - X.mean(axis=0), Y - Y.mean(axis=0)
b = (xc * yc).sum(axis=0) / (xc ** 2).sum(axis=0)
res = yc - b * xc
s2 = (res ** 2).sum(axis=0) / (n - 2)
t = b / np.sqrt(s2 / (xc ** 2).sum(axis=0))
p_mco = 2 * stats.t.sf(np.abs(t), n - 2)
print("MCO : proportion de rejets à 5 % alors qu'il n'y a AUCUN lien :", round((p_mco < 0.05).mean(), 3))
```
<!--sortie-->
```text
MCO : proportion de rejets à 5 % alors qu'il n'y a AUCUN lien : 0.459
```

*(suite du code)*

```python
# Nombre « efficace » d'observations indépendantes pour estimer une moyenne
var_y = Y.var()                                                # variance d'une zone
var_moy = Y.mean(axis=0).var()                                 # variance de la moyenne des 144 zones
print("variance d'une zone :", round(var_y, 2), "| variance de la moyenne de 144 zones :", round(var_moy, 3),
      "| si indépendantes, ce serait", round(var_y / n, 3))
print("nombre efficace d'observations indépendantes :", round(var_y / var_moy, 1), "sur", n)
```
<!--sortie-->
```text
variance d'une zone : 3.9 | variance de la moyenne de 144 zones : 0.706 | si indépendantes, ce serait 0.027
nombre efficace d'observations indépendantes : 5.5 sur 144
```

**Étape 2 : le remède.** Les moindres carrés généralisés, avec $\rho$ connu, ramènent le niveau à 5,3 % ; l'indice de Moran des résidus de la régression ordinaire (0,425, $p=0{,}001$) est le signal d'alarme à calculer dans une vraie analyse.

```python
T = np.eye(n) - 0.9 * W                                        # opérateur de blanchiment (rho connu)
un = np.ones(n)
rejets = 0
for r in range(reps):
    ys = T @ Y[:, r]
    Xs = np.column_stack([T @ un, T @ X[:, r]])               # constante et x, blanchis
    coef, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
    resid = ys - Xs @ coef
    s2 = resid @ resid / (n - 2)
    cov = s2 * np.linalg.inv(Xs.T @ Xs)
    tt = coef[1] / np.sqrt(cov[1, 1])
    rejets += 2 * stats.t.sf(abs(tt), n - 2) < 0.05
print("MCG avec rho connu : proportion de rejets à 5 % :", rejets / reps)
```
<!--sortie-->
```text
MCG avec rho connu : proportion de rejets à 5 % : 0.053
```

*(suite du code)*

```python
# Et dans une seule paire (la première) : les résidus des MCO révèlent le problème
Xd = np.column_stack([np.ones(n), X[:, 0]])
beta = np.linalg.lstsq(Xd, Y[:, 0], rcond=None)[0]
residus = Y[:, 0] - Xd @ beta
sim_r = moran_permutations(residus, W, B=999, seed=6)
print("Moran des résidus MCO (première paire) :", round(moran(residus, W), 3),
      "| p-valeur par permutation :", round((1 + (sim_r >= moran(residus, W)).sum()) / 1000, 3))
```
<!--sortie-->
```text
Moran des résidus MCO (première paire) : 0.425 | p-valeur par permutation : 0.001
```

**Pour aller plus loin.** Estimez $\rho$ au lieu de le supposer connu (maximum de vraisemblance sur une grille de valeurs) et vérifiez que le niveau du test reste proche de 5 %.

### Application 9.4 — Du variogramme au krigeage : les délais de livraison (section 9.3)

**Objectif.** Estimer le variogramme empirique, ajuster trois modèles, mesurer l'incertitude de l'ajustement, prédire par krigeage ordinaire avec sa variance, comparer à d'autres méthodes et valider par validation croisée.

**Étape 1 : le variogramme empirique**, validé sur quatre points alignés ($\hat\gamma=1{,}0\ ;\ 2{,}5\ ;\ 2{,}0$ à la main).

```python
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats, optimize

def distances(P, Q=None):
    Q = P if Q is None else Q
    return np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(axis=2))
```

*L'estimateur par classes de distance, puis sa validation sur les quatre points :*

```python
def variogramme_empirique(coords, z, largeur=5.0, hmax=50.0, angle=None, tol=22.5):
    """Semi-variogramme empirique par classes de distance. Si `angle` (en degrés, 0 = est, 90 = nord)
    est donné, on ne garde que les paires orientées dans cette direction (à +/- tol degrés près)."""
    n = len(z)
    i, j = np.triu_indices(n, 1)
    h = distances(coords)[i, j]
    g = 0.5 * (z[i] - z[j]) ** 2
    garde = np.ones(len(h), dtype=bool)
    if angle is not None:
        theta = np.degrees(np.arctan2(coords[j, 1] - coords[i, 1], coords[j, 0] - coords[i, 0])) % 180
        ecart = np.abs(theta - angle)
        garde = np.minimum(ecart, 180 - ecart) <= tol
    classes = np.arange(0, hmax + largeur, largeur)
    lignes = []
    for a, b in zip(classes[:-1], classes[1:]):
        m = garde & (h > a) & (h <= b)
        if m.any():
            lignes.append({"h": h[m].mean(), "gamma": g[m].mean(), "paires": int(m.sum())})
    return pd.DataFrame(lignes)

# Validation sur les quatre points de l'exemple à la main (classes de 1 km)
P4 = np.array([[0.0, 0], [1, 0], [2, 0], [3, 0]])
z4 = np.array([2.0, 3, 5, 4])
print(variogramme_empirique(P4, z4, largeur=1.0, hmax=3.0).to_string(index=False))
```
<!--sortie-->
```text
  h  gamma  paires
1.0    1.0       3
2.0    2.5       2
3.0    2.0       1
```

**Étape 2 : les 200 livraisons** et leur générateur (champ gaussien de covariance exponentielle, pépite 0,4). Le résultat est identique au fichier fourni (moyenne 4,27 jours, variance 1,21).

```python
def livraisons(seed=27, n=200, cote=100.0, sill=1.0, a=12.0, pepite=0.4, moyenne=4.0):
    rng = np.random.default_rng(seed)
    g = np.linspace(2, cote - 2, 25)                          # grille de prédiction 25 x 25
    gx, gy = np.meshgrid(g, g)
    grille = np.column_stack([gx.ravel(), gy.ravel()])
    obs = rng.uniform(0, cote, size=(n, 2))
    pts = np.vstack([obs, grille])
    C = sill * np.exp(-distances(pts) / a)                     # covariance exponentielle C(h) = sill * exp(-h/a)
    champ = moyenne + np.linalg.cholesky(C + 1e-8 * np.eye(len(pts))) @ rng.normal(size=len(pts))
    z = champ[:n] + rng.normal(0, np.sqrt(pepite), n)         # champ + bruit de mesure (la pépite)
    df = pd.DataFrame({"x": np.round(obs[:, 0], 2), "y": np.round(obs[:, 1], 2), "delai_jours": np.round(z, 3)})
    df["pli"] = rng.permutation(np.arange(n) % 5)             # 5 plis pour la validation croisée
    verite = pd.DataFrame({"x": grille[:, 0], "y": grille[:, 1], "champ": champ[n:]})
    return df, verite
```

*(suite du code)*

```python
liv, verite = livraisons()
fichier = pd.read_csv("donnees/ch09-livraisons.csv")
print("identique au fichier fourni :", np.allclose(liv[["x", "y", "delai_jours"]], fichier[["x", "y", "delai_jours"]]))
coords = liv[["x", "y"]].to_numpy()
z = liv["delai_jours"].to_numpy()
print(f"n = {len(z)} | moyenne = {z.mean():.2f} jours | variance = {z.var(ddof=1):.2f}")
```
<!--sortie-->
```text
identique au fichier fourni : True
n = 200 | moyenne = 4.27 jours | variance = 1.21
```

**Étape 3 : le variogramme empirique des livraisons** (classes de 5 km jusqu'à 50 km).

```python
emp = variogramme_empirique(coords, z, largeur=5.0, hmax=50.0)
print(emp.round(3).to_string(index=False))
```
<!--sortie-->
```text
     h  gamma  paires
 3.328  0.473     139
 7.817  0.784     384
12.655  1.057     683
17.572  1.265     849
22.550  1.250     992
27.537  1.190    1193
32.569  1.150    1278
37.539  1.211    1237
42.466  1.373    1332
47.408  1.426    1343
```

**Étape 4 : trois modèles ajustés** par moindres carrés pondérés (poids de Cressie). Les trois donnent un palier total voisin (1,28 à 1,32), mais des décompositions différentes entre pépite et portée.

```python
def gamma_sph(h, c0, c, a):
    h = np.asarray(h, dtype=float)
    g = np.where(h < a, c0 + c * (1.5 * h / a - 0.5 * (h / a) ** 3), c0 + c)
    return np.where(h > 0, g, 0.0)

def gamma_exp(h, c0, c, a):
    h = np.asarray(h, dtype=float)
    return np.where(h > 0, c0 + c * (1 - np.exp(-h / a)), 0.0)

def gamma_gau(h, c0, c, a):
    h = np.asarray(h, dtype=float)
    return np.where(h > 0, c0 + c * (1 - np.exp(-(h / a) ** 2)), 0.0)
```

*Les moyens d'ajuster :*

```python
MODELES = {"sphérique": gamma_sph, "exponentiel": gamma_exp, "gaussien": gamma_gau}
PORTEE_PRATIQUE = {"sphérique": lambda a: a, "exponentiel": lambda a: 3 * a, "gaussien": lambda a: np.sqrt(3) * a}

def ajuster(emp, modele, v0=None):
    """Ajuste (c0, c, a) par moindres carrés pondérés (poids de Cressie) ; renvoie les paramètres et le critère."""
    h, g, N = emp["h"].to_numpy(), emp["gamma"].to_numpy(), emp["paires"].to_numpy()
    v = g.max() if v0 is None else v0
    def residus(p):
        return np.sqrt(N) * (g / np.maximum(modele(h, *p), 1e-9) - 1)
    meilleur = None
    for a0 in (h.max() / 6, h.max() / 3, h.max() / 1.5):          # plusieurs départs : le critère n'est pas convexe
        r = optimize.least_squares(residus, x0=[0.1 * v, v, a0], bounds=([0, 1e-6, 1e-3], [10 * v, 10 * v, 10 * h.max()]))
        if meilleur is None or r.cost < meilleur.cost:
            meilleur = r
    return meilleur.x, 2 * meilleur.cost
```

*L'ajustement des trois modèles :*

```python
lignes, ajustements = [], {}
for nom, f in MODELES.items():
    p, crit = ajuster(emp, f)
    ajustements[nom] = p
    lignes.append({"modele": nom, "pepite": p[0], "palier_partiel": p[1], "palier_total": p[0] + p[1],
                   "param_a": p[2], "portee_pratique_km": PORTEE_PRATIQUE[nom](p[2]), "critere": crit})
with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 150):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
     modele  pepite  palier_partiel  palier_total  param_a  portee_pratique_km  critere
  sphérique   0.215           1.065         1.280   20.792              20.792   48.096
exponentiel   0.038           1.277         1.315    8.136              24.407   47.196
   gaussien   0.390           0.893         1.283   10.436              18.075   48.425
```

**Étape 5 : la figure.**

```python
BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
hh = np.linspace(0.01, 50, 300)
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.scatter(emp["h"], emp["gamma"], s=np.sqrt(emp["paires"]) * 3, color="#444444", zorder=3, label="empirique (taille = nb de paires)")
for (nom, f), couleur in zip(MODELES.items(), [AQUA, ORANGE, VIOLET]):
    ax.plot(hh, f(hh, *ajustements[nom]), color=couleur, lw=2, label=nom)
ax.axhline(z.var(ddof=1), color="#999999", lw=0.8, ls="--")
ax.annotate("variance empirique des données", (50, z.var(ddof=1)), xytext=(-4, 4), textcoords="offset points", ha="right", fontsize=8, color="#666666")
ax.set_xlabel("distance h (km)"); ax.set_ylabel("semi-variance  γ(h)  (jours²)")
ax.set_title("Variogramme empirique des délais de livraison et trois modèles ajustés")
ax.set_xlim(0, 52); ax.set_ylim(0, None)
ax.legend(frameon=False, loc="lower right", fontsize=8)
plt.tight_layout()
plt.savefig("figures/ch09-variogramme.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

**Étape 6 : cet ajustement est-il typique ?** Trente autres graines : la pépite varie de 0,10 à 0,54 et la portée pratique de 16 à 52 km (vérités : 0,4 et 36 km).

```python
rangs = []
for s in range(100, 130):
    d_s, _ = livraisons(seed=s)
    e_s = variogramme_empirique(d_s[["x", "y"]].to_numpy(), d_s["delai_jours"].to_numpy())
    p, _ = ajuster(e_s, gamma_exp)
    rangs.append({"pepite": p[0], "palier_partiel": p[1], "param_a": p[2], "portee_pratique": 3 * p[2], "palier_total": p[0] + p[1]})
rangs = pd.DataFrame(rangs)
verite_p = {"pepite": 0.4, "palier_partiel": 1.0, "param_a": 12.0, "portee_pratique": 36.0, "palier_total": 1.4}
resume = pd.DataFrame({"vérité": pd.Series(verite_p), "médiane": rangs.median(), "10e perc.": rangs.quantile(0.10), "90e perc.": rangs.quantile(0.90)})
print(resume.round(2).to_string())
```
<!--sortie-->
```text
                 vérité  médiane  10e perc.  90e perc.
pepite              0.4     0.35       0.10       0.54
palier_partiel      1.0     1.04       0.78       1.38
param_a            12.0     9.64       5.29      17.33
portee_pratique    36.0    28.92      15.88      52.00
palier_total        1.4     1.38       1.05       1.63
```

**Étape 7 : le krigeage ordinaire.** La fonction résout le système bordé $\begin{pmatrix}\Gamma&\mathbf 1\\\mathbf 1^\top&0\end{pmatrix}$ ; elle est testée sur l'exemple à la main (poids $\tfrac23,\tfrac13$, prédiction 12, variance $\tfrac43$).

```python
def krigeage_ordinaire(coords, z, cibles, modele, params):
    """Krigeage ordinaire : renvoie prédictions, variances de krigeage et poids (une colonne par cible)."""
    n = len(z)
    G = modele(distances(coords), *params)                       # Gamma (diagonale nulle)
    A = np.zeros((n + 1, n + 1))
    A[:n, :n] = G
    A[:n, n] = 1.0
    A[n, :n] = 1.0
    g0 = modele(distances(coords, cibles), *params)              # gamma_0, une colonne par cible
    B = np.vstack([g0, np.ones((1, cibles.shape[0]))])
    sol = np.linalg.solve(A, B)
    lam, m = sol[:n], sol[n]
    pred = lam.T @ z
    var = (lam * g0).sum(axis=0) + m
    return pred, var, lam

lineaire = lambda h, pente: np.where(np.asarray(h) > 0, pente * np.asarray(h), 0.0)
pred, var, lam = krigeage_ordinaire(np.array([[0.0, 0], [3, 0]]), np.array([10.0, 16.0]), np.array([[1.0, 0]]), lineaire, (1.0,))
print("poids :", lam.ravel().round(4), "| prédiction :", pred.round(4), "| variance :", var.round(4))
```
<!--sortie-->
```text
poids : [0.6667 0.3333] | prédiction : [12.] | variance : [1.3333]
```

**Étape 8 : une prédiction au point $(40,\,60)$** : 4,75 jours, écart-type de krigeage 0,77 ; 29 poids négatifs sur 200 (effet d'écran).

```python
mod, par = gamma_exp, ajustements["exponentiel"]
cible = np.array([[40.0, 60.0]])
pred, var, lam = krigeage_ordinaire(coords, z, cible, mod, par)
lam = lam.ravel()
dist = distances(coords, cible).ravel()
ordre = np.argsort(-np.abs(lam))[:6]
print(f"prédiction en (40, 60) : {pred[0]:.2f} jours | écart-type de krigeage : {np.sqrt(var[0]):.2f} jour")
print("somme des poids :", round(lam.sum(), 6), "| poids négatifs :", int((lam < 0).sum()), "sur", len(lam),
      f"| plus petit : {lam.min():.3f} | plus grand : {lam.max():.3f}")
print(pd.DataFrame({"distance_km": dist[ordre], "poids": lam[ordre], "delai": z[ordre]}).round(3).to_string(index=False))
```
<!--sortie-->
```text
prédiction en (40, 60) : 4.75 jours | écart-type de krigeage : 0.77 jour
somme des poids : 1.0 | poids négatifs : 29 sur 200 | plus petit : -0.026 | plus grand : 0.532
 distance_km  poids  delai
       2.724  0.532  4.753
       4.740  0.158  4.849
       6.420  0.105  3.997
       8.405  0.102  5.156
      11.762  0.054  5.439
      11.745  0.032  3.196
```

**Étape 9 : cartes de prédiction et d'incertitude.** RMSE par rapport au vrai champ : moyenne 0,916 ; inverse de la distance 0,671 ; krigeage 0,645.

```python
grille = verite[["x", "y"]].to_numpy()
pred_k, var_k, _ = krigeage_ordinaire(coords, z, grille, mod, par)

def idw(coords, z, cibles, puissance=2.0):
    d = np.maximum(distances(cibles, coords), 1e-9)
    w = 1.0 / d ** puissance
    return (w * z).sum(axis=1) / w.sum(axis=1)

pred_i = idw(coords, z, grille)
vrai = verite["champ"].to_numpy()
rmse = lambda a, b: float(np.sqrt(np.mean((a - b) ** 2)))
print("RMSE par rapport au VRAI champ sur les 625 points de la grille :")
print(f"  moyenne globale          : {rmse(np.full_like(vrai, z.mean()), vrai):.3f}")
print(f"  inverse de la distance^2 : {rmse(pred_i, vrai):.3f}")
print(f"  krigeage ordinaire       : {rmse(pred_k, vrai):.3f}")
print(f"écart-type de krigeage : de {np.sqrt(var_k.min()):.2f} à {np.sqrt(var_k.max()):.2f} jour (moyenne {np.sqrt(var_k).mean():.2f})")
```
<!--sortie-->
```text
RMSE par rapport au VRAI champ sur les 625 points de la grille :
  moyenne globale          : 0.916
  inverse de la distance^2 : 0.671
  krigeage ordinaire       : 0.645
écart-type de krigeage : de 0.35 à 1.08 jour (moyenne 0.77)
```

```python
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))
vmin, vmax = min(vrai.min(), pred_k.min()), max(vrai.max(), pred_k.max())
cartes = [(vrai, "Vrai champ (connu par simulation)", "Oranges", dict(vmin=vmin, vmax=vmax)),
          (pred_k, "Krigeage : prédiction", "Oranges", dict(vmin=vmin, vmax=vmax)),
          (np.sqrt(var_k), "Krigeage : écart-type d'erreur", "Purples", {})]
for ax, (champ, titre, cmap, kw) in zip(axes, cartes):
    im = ax.imshow(champ.reshape(25, 25), origin="lower", extent=(0, 100, 0, 100), cmap=cmap, **kw)
    ax.set_title(titre, fontsize=10)
    ax.set_xlabel("x (km)")
    fig.colorbar(im, ax=ax, shrink=0.78)
    if "écart-type" in titre:
        ax.scatter(coords[:, 0], coords[:, 1], s=5, color="#222222", alpha=0.6)
axes[0].set_ylabel("y (km)")
plt.tight_layout()
plt.savefig("figures/ch09-krigeage.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

**Étape 10 : de quoi dépend l'incertitude ?** L'écart-type de krigeage croît avec la distance à la mesure la plus proche (corrélation 0,92).

```python
dmin = distances(grille, coords).min(axis=1)                     # distance au point mesuré le plus proche
sd_k = np.sqrt(var_k)
bord = np.minimum.reduce([grille[:, 0], 100 - grille[:, 0], grille[:, 1], 100 - grille[:, 1]])
print("corrélation entre l'écart-type de krigeage et la distance au point le plus proche :", round(np.corrcoef(sd_k, dmin)[0, 1], 3))
for a_, b_ in [(0, 2), (2, 4), (4, 6), (6, 10)]:
    m = (dmin >= a_) & (dmin < b_)
    print(f"  points de grille à {a_}-{b_} km d'une mesure : {int(m.sum()):3d} points, écart-type moyen {sd_k[m].mean():.2f} jour")
print(f"écart-type moyen à moins de 8 km d'un bord : {sd_k[bord < 8].mean():.3f} | à l'intérieur : {sd_k[bord >= 8].mean():.3f}")
```
<!--sortie-->
```text
corrélation entre l'écart-type de krigeage et la distance au point le plus proche : 0.924
  points de grille à 0-2 km d'une mesure : 145 points, écart-type moyen 0.59 jour
  points de grille à 2-4 km d'une mesure : 252 points, écart-type moyen 0.77 jour
  points de grille à 4-6 km d'une mesure : 173 points, écart-type moyen 0.87 jour
  points de grille à 6-10 km d'une mesure :  54 points, écart-type moyen 0.97 jour
écart-type moyen à moins de 8 km d'un bord : 0.779 | à l'intérieur : 0.770
```

**Étape 11 : validation croisée honnête** (variogramme réajusté à chaque pli) : RMSE 1,097 ; 0,994 ; 0,969 ; variance des résidus standardisés 1,71 ; couverture 89,5 % au lieu de 95 %.

```python
plis = liv["pli"].to_numpy()
pred_cv = {"moyenne": np.empty(len(z)), "IDW": np.empty(len(z)), "krigeage": np.empty(len(z))}
sig_cv = np.empty(len(z))
for k in range(5):
    tr, te = plis != k, plis == k
    emp_k = variogramme_empirique(coords[tr], z[tr])
    p_k, _ = ajuster(emp_k, gamma_exp)                            # variogramme réajusté sur l'entraînement
    pk, vk, _ = krigeage_ordinaire(coords[tr], z[tr], coords[te], gamma_exp, p_k)
    pred_cv["krigeage"][te] = pk
    sig_cv[te] = np.sqrt(vk)
    pred_cv["IDW"][te] = idw(coords[tr], z[tr], coords[te])
    pred_cv["moyenne"][te] = z[tr].mean()
```

*Les trois méthodes, pli par pli :*

```python
tab = pd.DataFrame({nom: {"RMSE (jours)": rmse(p, z), "biais moyen": float(np.mean(p - z))} for nom, p in pred_cv.items()}).T
print(tab.round(3).to_string())
std_res = (z - pred_cv["krigeage"]) / sig_cv
couvert = np.mean(np.abs(z - pred_cv["krigeage"]) <= 1.96 * sig_cv)
print(f"\nrésidus standardisés du krigeage : moyenne = {std_res.mean():.3f}, variance = {std_res.var(ddof=1):.3f}  (visé : 0 et 1)")
print(f"couverture des intervalles de krigeage à 95 % : {couvert:.3f}")
```
<!--sortie-->
```text
          RMSE (jours)  biais moyen
moyenne          1.097        0.000
IDW              0.994        0.040
krigeage         0.969        0.023

résidus standardisés du krigeage : moyenne = -0.021, variance = 1.710  (visé : 0 et 1)
couverture des intervalles de krigeage à 95 % : 0.895
```

**Étape 12 : une alternative sans variogramme, la spline de plaque mince** (R, `mgcv`) : RMSE 0,974, quasi identique au krigeage.

```r
library(mgcv)
d <- read.csv("donnees/ch09-livraisons.csv")
pred <- numeric(nrow(d))
for (k in 0:4) {
  tr <- d[d$pli != k, ]
  te <- d[d$pli == k, ]
  g <- gam(delai_jours ~ s(x, y, k = 60), data = tr, method = "REML")
  pred[d$pli == k] <- predict(g, newdata = te)
}
cat("RMSE par validation croisée (spline de plaque mince, mgcv) :", round(sqrt(mean((d$delai_jours - pred)^2)), 3), "\n")
cat("biais moyen :", round(mean(pred - d$delai_jours), 3), "\n")
```
<!--sortie-->
```text
Loading required package: nlme
This is mgcv 1.9-1. For overview type 'help("mgcv-package")'.
RMSE par validation croisée (spline de plaque mince, mgcv) : 0.974 
biais moyen : 0.009 
```

**Pour aller plus loin.** Remplacez le modèle exponentiel par le sphérique dans la validation croisée : l'erreur change-t-elle ? Et la couverture des intervalles ?

### Application 9.5 — Les limites du variogramme : tendance et anisotropie (section 9.3.7)

**Objectif.** Voir une tendance faire « monter » le variogramme, la retirer par régression, puis calibrer par simulation un écart apparent entre deux directions.

**Étape 1 : une tendance de $0{,}04$ jour/km vers l'est.** La régression retrouve une pente de 0,042 (vérité 0,04) ; une fois retirée, la courbe redevient celle du processus sans tendance.

```python
z_tend = z + 0.04 * coords[:, 0]                                  # tendance ajoutée : +0,04 jour/km vers l'est
X = np.column_stack([np.ones(len(z)), coords])
beta = np.linalg.lstsq(X, z_tend, rcond=None)[0]
z_res = z_tend - X @ beta                                         # résidus de la régression sur (x, y)
e_tend = variogramme_empirique(coords, z_tend, largeur=5.0, hmax=70.0)
e_res = variogramme_empirique(coords, z_res, largeur=5.0, hmax=70.0)
e_ref = variogramme_empirique(coords, z, largeur=5.0, hmax=70.0)
print("tendance estimée par régression : ", beta.round(3), "(constante, pente en x, pente en y)")
print(pd.DataFrame({"h": e_ref["h"].round(1), "sans_tendance": e_ref["gamma"], "avec_tendance": e_tend["gamma"],
                    "tendance_retiree": e_res["gamma"]}).round(2).iloc[[1, 3, 5, 7, 9, 11, 13]].to_string(index=False))
```
<!--sortie-->
```text
tendance estimée par régression :  [ 4.325e+00  4.200e-02 -3.000e-03] (constante, pente en x, pente en y)
   h  sans_tendance  avec_tendance  tendance_retiree
 7.8           0.78           0.84              0.78
17.6           1.27           1.41              1.27
27.5           1.19           1.50              1.19
37.5           1.21           1.79              1.22
47.4           1.43           2.36              1.42
57.4           1.35           2.64              1.35
67.4           1.21           3.29              1.19
```

**Étape 2 : la figure** (tendance, puis variogrammes directionnels est-ouest et nord-sud).

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.plot(e_ref["h"], e_ref["gamma"], "o-", color=AQUA, label="sans tendance")
ax1.plot(e_tend["h"], e_tend["gamma"], "o-", color=ROUGE, label="avec une tendance linéaire non retirée")
ax1.plot(e_res["h"], e_res["gamma"], "o-", color=BLEU, label="tendance retirée par régression")
ax1.set_xlabel("distance h (km)"); ax1.set_ylabel("semi-variance (jours²)"); ax1.set_title("Une tendance fait « monter » le variogramme")
ax1.legend(frameon=False, fontsize=8, loc="upper left")
for angle, couleur, nom in [(0, ORANGE, "est-ouest (0°)"), (90, VIOLET, "nord-sud (90°)")]:
    e_dir = variogramme_empirique(coords, z, largeur=7.5, hmax=45.0, angle=angle, tol=22.5)
    ax2.plot(e_dir["h"], e_dir["gamma"], "o-", color=couleur, label=nom)
e_om = variogramme_empirique(coords, z, largeur=7.5, hmax=45.0)
ax2.plot(e_om["h"], e_om["gamma"], "--", color="#444444", label="toutes directions")
ax2.set_xlabel("distance h (km)"); ax2.set_ylabel("semi-variance (jours²)"); ax2.set_title("Variogrammes directionnels")
ax2.legend(frameon=False, fontsize=8, loc="lower right")
plt.tight_layout()
plt.savefig("figures/ch09-limites-variogramme.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

**Étape 3 : calibrer l'écart apparent.** Le rapport $\gamma_{\text{N-S}}/\gamma_{\text{E-O}}$ observé (1,24) est comparé à celui de 60 jeux simulés isotropes : environ 5 % l'atteignent. Cas limite, qu'on ne tranche pas sur un graphique.

```python
def rapport_ns_eo(c, zz):
    ns_ = variogramme_empirique(c, zz, largeur=7.5, hmax=45.0, angle=90, tol=22.5)["gamma"].to_numpy()
    eo_ = variogramme_empirique(c, zz, largeur=7.5, hmax=45.0, angle=0, tol=22.5)["gamma"].to_numpy()
    m_ = min(len(ns_), len(eo_))
    return float(np.mean(ns_[:m_] / eo_[:m_]))

r_obs = rapport_ns_eo(coords, z)
r_sim = []
for s_ in range(100, 160):
    d_s, _ = livraisons(seed=s_)
    r_sim.append(rapport_ns_eo(d_s[["x", "y"]].to_numpy(), d_s["delai_jours"].to_numpy()))
r_sim = np.array(r_sim)
print(f"rapport N-S / E-O observé : {r_obs:.3f}")
print(f"rapport sur 60 jeux isotropes : médiane {np.median(r_sim):.3f}, 10e-90e percentiles {np.percentile(r_sim, 10):.3f} - {np.percentile(r_sim, 90):.3f}")
print(f"part des jeux isotropes dont le rapport est au moins aussi grand : {np.mean(r_sim >= r_obs):.3f}")
```
<!--sortie-->
```text
rapport N-S / E-O observé : 1.243
rapport sur 60 jeux isotropes : médiane 1.020, 10e-90e percentiles 0.908 - 1.167
part des jeux isotropes dont le rapport est au moins aussi grand : 0.050
```

**Pour aller plus loin.** Doublez le nombre de graines (120 jeux) et suivez la part de jeux isotropes au moins aussi extrêmes : se stabilise-t-elle ?

### Application 9.6 — Trois semis de points : quadrats, plus proche voisin, fonction K (section 9.4)

**Objectif.** Fabriquer trois semis (hasard complet, agrégat de Thomas, régulier), les distinguer par le test des quadrats, l'indice de Clark-Evans (avec correction de bord de Donnelly et p-valeur de Monte-Carlo), la fonction $G$ et la fonction $K$ de Ripley avec enveloppes.

**Étape 1 : les trois semis** (fenêtre de 10 km de côté ; 100, 75 et 100 points).

```python
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

COTE = 10.0                                  # fenêtre carrée de 10 km de côté
AIRE = COTE ** 2                             # 100 km²
```

*Les trois générateurs :*

```python
def distances(P, Q=None):
    Q = P if Q is None else Q
    return np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(axis=2))

def semis_poisson(n, rng):
    """CSR conditionnel à n : n points indépendants et uniformes."""
    return rng.uniform(0, COTE, size=(n, 2))

def semis_thomas(kappa, mu, sigma, rng):
    """Agrégat de Thomas : centres de Poisson (densité kappa), mu descendants en moyenne, étalement sigma."""
    marge = 3 * sigma                                            # on génère aussi des centres hors fenêtre
    n_centres = rng.poisson(kappa * (COTE + 2 * marge) ** 2)
    centres = rng.uniform(-marge, COTE + marge, size=(n_centres, 2))
    nb = rng.poisson(mu, size=n_centres)
    pts = np.repeat(centres, nb, axis=0) + rng.normal(0, sigma, size=(nb.sum(), 2))
    return pts[((pts >= 0) & (pts <= COTE)).all(axis=1)]         # on ne garde que ce qui tombe dans la fenêtre
```

*Le tirage et la figure :*

```python
def semis_inhibition(n, rmin, rng):
    """Inhibition séquentielle simple : points uniformes refusés s'ils sont à moins de rmin d'un point accepté."""
    pts = []
    while len(pts) < n:
        p = rng.uniform(0, COTE, size=2)
        if not pts or (np.hypot(*(np.array(pts) - p).T) >= rmin).all():
            pts.append(p)
    return np.array(pts)

rng = np.random.default_rng(2025)
semis = {
    "aléatoire (CSR)": semis_poisson(100, rng),
    "agrégé (Thomas)": semis_thomas(kappa=0.08, mu=12, sigma=0.4, rng=rng),
    "régulier (inhibition)": semis_inhibition(100, 0.7, rng),
}
for nom, pts in semis.items():
    print(f"{nom:24s} n = {len(pts):3d} points  (intensité estimée {len(pts) / AIRE:.2f} par km²)")
```
<!--sortie-->
```text
aléatoire (CSR)          n = 100 points  (intensité estimée 1.00 par km²)
agrégé (Thomas)          n =  75 points  (intensité estimée 0.75 par km²)
régulier (inhibition)    n = 100 points  (intensité estimée 1.00 par km²)
```

*(suite de la figure)*

```python
BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.3))
for ax, (nom, pts), couleur in zip(axes, semis.items(), [BLEU, ORANGE, AQUA]):
    ax.scatter(pts[:, 0], pts[:, 1], s=16, color=couleur, edgecolor="white", linewidth=0.4)
    ax.set_xlim(0, COTE); ax.set_ylim(0, COTE); ax.set_aspect("equal")
    ax.set_title(f"{nom} : {len(pts)} adresses", fontsize=10)
    ax.set_xlabel("x (km)")
axes[0].set_ylabel("y (km)")
plt.tight_layout()
plt.savefig("figures/ch09-semis.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

**Étape 2 : le test des quadrats.** $\chi^2=8{,}8$ (hasard), $143{,}7$ (agrégé), $4{,}0$ (régulier) pour 15 degrés de liberté.

```python
def comptages(pts, m=4):
    """Comptages par case d'un quadrillage m x m de la fenêtre."""
    bornes = np.linspace(0, COTE, m + 1)
    H, _, _ = np.histogram2d(pts[:, 0], pts[:, 1], bins=[bornes, bornes])
    return H.ravel()

def test_quadrats(pts, m=4):
    c = comptages(pts, m)
    chi2 = ((c - c.mean()) ** 2).sum() / c.mean()
    ddl = len(c) - 1
    return {"chi2": chi2, "ddl": ddl, "VMR": c.var(ddof=1) / c.mean(),
            "p_agregat (chi2 grand)": stats.chi2.sf(chi2, ddl), "p_regulier (chi2 petit)": stats.chi2.cdf(chi2, ddl)}
```

*(suite du code)*

```python
# l'exemple à la main
print("exemple (1, 1, 1, 9) :", round(((np.array([1, 1, 1, 9]) - 3) ** 2).sum() / 3, 2), "| valeur critique chi2(3) à 5 % :", round(stats.chi2.ppf(0.95, 3), 2))
res = pd.DataFrame({nom: test_quadrats(pts) for nom, pts in semis.items()}).T
with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 160):
    print(res.to_string())
print("\ncomptages par case du semis agrégé (4 x 4) :")
print(comptages(semis["agrégé (Thomas)"]).reshape(4, 4).astype(int))
```
<!--sortie-->
```text
exemple (1, 1, 1, 9) : 16.0 | valeur critique chi2(3) à 5 % : 7.81
                       chi2  ddl    VMR  p_agregat (chi2 grand)  p_regulier (chi2 petit)
aléatoire (CSR)         8.8   15 0.5867                  0.8877                   0.1123
agrégé (Thomas)       143.7   15  9.578               4.342e-23                        1
régulier (inhibition)     4   15 0.2667                  0.9977                 0.002263

comptages par case du semis agrégé (4 x 4) :
[[ 1  0  1 11]
 [19  0  0  0]
 [12  2 14  1]
 [ 0  0  0 14]]
```

**Étape 3 : l'effet de bord sur le plus proche voisin.** La formule naïve sous-estime la moyenne (0,500 contre 0,523 simulé) ; celle de Donnelly colle à la simulation.

```python
def plus_proches(pts):
    D = distances(pts)
    np.fill_diagonal(D, np.inf)
    return D.min(axis=1)

rng = np.random.default_rng(1)
n0 = 100
dbar = np.array([plus_proches(semis_poisson(n0, rng)).mean() for _ in range(4000)])
P = 4 * COTE
naif = 0.5 * np.sqrt(AIRE / n0)
don = 0.5 * np.sqrt(AIRE / n0) + (0.0514 + 0.041 / np.sqrt(n0)) * P / n0
sd_naif = np.sqrt((4 - np.pi) / (4 * np.pi * n0 * (n0 / AIRE)))
sd_don = np.sqrt(0.070 * AIRE / n0 ** 2 + 0.037 * P * np.sqrt(AIRE / n0 ** 5))
print(f"{'':28s}{'moyenne de d':>14s}{'écart-type de d':>18s}")
print(f"{'simulation (4000 semis CSR)':28s}{dbar.mean():14.4f}{dbar.std():18.4f}")
print(f"{'formule naïve (plan infini)':28s}{naif:14.4f}{sd_naif:18.4f}")
print(f"{'formule de Donnelly':28s}{don:14.4f}{sd_don:18.4f}")
```
<!--sortie-->
```text
                              moyenne de d   écart-type de d
simulation (4000 semis CSR)         0.5224            0.0288
formule naïve (plan infini)         0.5000            0.0261
formule de Donnelly                 0.5222            0.0291
```

**Étape 4 : l'indice de Clark-Evans**, avec trois voies : $R$ naïf, $R$ corrigé et p-valeur de Monte-Carlo.

```python
def clark_evans(pts, B=999, seed=7):
    n = len(pts)
    d = plus_proches(pts).mean()
    R_naif = d / (0.5 * np.sqrt(AIRE / n))
    E_don = 0.5 * np.sqrt(AIRE / n) + (0.0514 + 0.041 / np.sqrt(n)) * P / n
    s_don = np.sqrt(0.070 * AIRE / n ** 2 + 0.037 * P * np.sqrt(AIRE / n ** 5))
    z_don = (d - E_don) / s_don
    rng = np.random.default_rng(seed)
    sim = np.array([plus_proches(semis_poisson(n, rng)).mean() for _ in range(B)])
    p_mc = 2 * (1 + min((sim <= d).sum(), (sim >= d).sum())) / (B + 1)      # bilatérale
    return {"n": n, "d_moyen": d, "R (naïf)": R_naif, "R (Donnelly)": d / E_don, "z (Donnelly)": z_don,
            "p (Donnelly)": 2 * stats.norm.sf(abs(z_don)), "p (Monte-Carlo)": min(1.0, p_mc)}

res = pd.DataFrame({nom: clark_evans(pts) for nom, pts in semis.items()}).T
with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 170):
    print(res.to_string())
```
<!--sortie-->
```text
                        n  d_moyen  R (naïf)  R (Donnelly)  z (Donnelly)  p (Donnelly)  p (Monte-Carlo)
aléatoire (CSR)       100   0.5353     1.071         1.025        0.4506        0.6523            0.628
agrégé (Thomas)        75   0.2026    0.3509        0.3336        -10.28     8.252e-25            0.002
régulier (inhibition) 100    0.829     1.658         1.587         10.53     6.024e-26            0.002
```

**Étape 5 : la fonction $G$ et son enveloppe de Monte-Carlo** (499 semis aléatoires de même taille).

```python
def G_emp(pts, rs):
    d = plus_proches(pts)
    return np.array([(d <= r).mean() for r in rs])

rs_G = np.linspace(0, 1.6, 81)
rng = np.random.default_rng(11)
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.9), sharey=True)
lignes = []
for ax, (nom, pts), couleur in zip(axes, semis.items(), [BLEU, ORANGE, AQUA]):
    n = len(pts)
    sims = np.array([G_emp(semis_poisson(n, rng), rs_G) for _ in range(499)])
    bas, haut = np.percentile(sims, [2.5, 97.5], axis=0)
    theorique = 1 - np.exp(-(n / AIRE) * np.pi * rs_G ** 2)
    ax.fill_between(rs_G, bas, haut, color="#cfcfc8", alpha=0.8, label="enveloppe CSR (95 %)")
    ax.plot(rs_G, theorique, color="#555555", lw=1, ls="--", label="théorie (plan infini)")
    ax.plot(rs_G, G_emp(pts, rs_G), color=couleur, lw=2.2, label="observé")
    ax.set_title(nom, fontsize=10); ax.set_xlabel("distance r (km)")
    sortie = (G_emp(pts, rs_G) < bas) | (G_emp(pts, rs_G) > haut)
    lignes.append({"semis": nom, "part des r hors enveloppe": sortie.mean()})
axes[0].set_ylabel("G(r)")
axes[0].legend(frameon=False, fontsize=8, loc="lower right")
plt.tight_layout()
plt.savefig("figures/ch09-fonction-G.png", dpi=200, bbox_inches="tight")
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
                semis  part des r hors enveloppe
      aléatoire (CSR)                      0.000
      agrégé (Thomas)                      0.741
régulier (inhibition)                      0.531
```

**Étape 6 : la fonction $K$ de Ripley** : estimateur avec correction de bord (méthode du bord), contrôle sur l'exemple à la main ($0{,}333$), puis mesure du biais de bord (10,4 sans correction, 12,3 avec, 12,6 en théorie à $r=2$ km).

```python
def ripley_K(pts, rs, bord=True):
    """Estimateur de K, avec ou sans correction de bord (méthode du bord)."""
    n = len(pts)
    D = distances(pts)
    np.fill_diagonal(D, np.inf)
    b = np.minimum.reduce([pts[:, 0], COTE - pts[:, 0], pts[:, 1], COTE - pts[:, 1]])
    K = np.full(len(rs), np.nan)
    for k, r in enumerate(rs):
        garde = (b >= r) if bord else np.ones(n, dtype=bool)
        nr = garde.sum()
        if nr > 0:
            K[k] = AIRE * (D[garde] <= r).sum() / ((n - 1) * nr)
    return K
```

*(suite du code)*

```python
# Contrôle sur l'exemple à la main (fenêtre unité) : on neutralise le bord pour retrouver 0,333
P4 = np.array([[0.1, 0.1], [0.2, 0.1], [0.8, 0.8], [0.85, 0.9]])
D4 = distances(P4); np.fill_diagonal(D4, np.inf)
print("K(0,2) de l'exemple à la main :", round(1.0 * (D4 <= 0.2).sum() / (4 * 3), 4), "| pi r^2 =", round(np.pi * 0.2 ** 2, 4))

# L'effet de bord, mesuré : moyenne de K sur 300 semis CSR, avec et sans correction, à r = 2 km
rs = np.linspace(0.1, 2.0, 20)
rng = np.random.default_rng(3)
Kn, Kc = [], []
for _ in range(300):
    pts_sim = semis_poisson(100, rng)                           # le même semis sert aux deux estimateurs
    Kn.append(ripley_K(pts_sim, rs, bord=False))
    Kc.append(ripley_K(pts_sim, rs, bord=True))
Kn, Kc = np.array(Kn), np.array(Kc)
print(f"à r = 2 km  ->  pi r^2 = {np.pi * 4:.2f} | moyenne sans correction : {Kn[:, -1].mean():.2f} | moyenne avec correction : {np.nanmean(Kc[:, -1]):.2f}")
```
<!--sortie-->
```text
K(0,2) de l'exemple à la main : 0.3333 | pi r^2 = 0.1257
à r = 2 km  ->  pi r^2 = 12.57 | moyenne sans correction : 10.42 | moyenne avec correction : 12.30
```

**Étape 7 : $L(r)-r$, enveloppes et test global** ($T=\max_r|\hat L(r)-r|$).

```python
def L_centre(pts, rs):
    return np.sqrt(ripley_K(pts, rs) / np.pi) - rs

rng = np.random.default_rng(21)
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.9), sharey=True)
lignes = []
```

*La boucle : une enveloppe, une statistique $T$ et une courbe par semis :*

```python
for ax, (nom, pts), couleur in zip(axes, semis.items(), [BLEU, ORANGE, AQUA]):
    n = len(pts)
    sims = np.array([L_centre(semis_poisson(n, rng), rs) for _ in range(499)])
    bas, haut = np.nanpercentile(sims, [2.5, 97.5], axis=0)
    obs = L_centre(pts, rs)
    T_obs = np.nanmax(np.abs(obs))
    T_sim = np.nanmax(np.abs(sims), axis=1)
    lignes.append({"semis": nom, "T observé": T_obs, "T sim. (médiane)": np.median(T_sim),
                   "p global (Monte-Carlo)": (1 + (T_sim >= T_obs).sum()) / (len(T_sim) + 1),
                   "L-r moyen": np.nanmean(obs)})
    ax.fill_between(rs, bas, haut, color="#cfcfc8", alpha=0.8, label="enveloppe CSR (95 %, point par point)")
    ax.axhline(0, color="#555555", lw=1, ls="--")
    ax.plot(rs, obs, color=couleur, lw=2.2, label="observé")
    ax.set_title(nom, fontsize=10); ax.set_xlabel("distance r (km)")
```

*Les légendes, puis le résumé :*

```python
axes[0].set_ylabel("L(r) - r  (0 = hasard complet)")
axes[0].legend(frameon=False, fontsize=8, loc="lower left")
plt.tight_layout()
plt.savefig("figures/ch09-ripley.png", dpi=200, bbox_inches="tight")
with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 170):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
                semis  T observé  T sim. (médiane)  p global (Monte-Carlo)  L-r moyen
      aléatoire (CSR)      0.092            0.1002                   0.672   -0.03473
      agrégé (Thomas)      1.095             0.133                   0.002     0.7666
régulier (inhibition)        0.7            0.1023                   0.002    -0.2289
```

**Pour aller plus loin.** Variez l'étalement $\sigma$ de l'agrégat (0,2 ; 0,4 ; 0,8 km) et relevez l'échelle $r$ où $L(r)-r$ est maximal : suit-elle $\sigma$ ?

### Application 9.7 — Agrégat ou densité variable ? (section 9.4.5)

**Objectif.** Montrer qu'une densité qui varie, sans aucune interaction entre les points, fait rejeter le hasard complet. On réutilise les fonctions de l'application 9.6.

**Étape 1 : cent adresses indépendantes, avec une densité forte au centre.** Le test global rejette le hasard complet ($T=0{,}687$, $p=0{,}002$) alors qu'aucun point n'attire les autres.

```python
def semis_inhomogene(n, rng, etalement=2.5):
    """100 points indépendants, mais avec une densité qui décroît du centre vers les bords."""
    pts = []
    while len(pts) < n:
        p = rng.uniform(0, COTE, size=2)
        if rng.random() < np.exp(-((p - COTE / 2) ** 2).sum() / (2 * etalement ** 2)):
            pts.append(p)
    return np.array(pts)

rng = np.random.default_rng(31)
inho = semis_inhomogene(100, rng)
obs = L_centre(inho, rs)
sims = np.array([L_centre(semis_poisson(100, rng), rs) for _ in range(499)])
T_obs, T_sim = np.nanmax(np.abs(obs)), np.nanmax(np.abs(sims), axis=1)
print(f"semis à densité variable, SANS interaction : T = {T_obs:.3f} | p global CSR = {(1 + (T_sim >= T_obs).sum()) / 500:.3f}")
q = comptages(inho, 4).reshape(4, 4)
print("comptages par case (4 x 4) :")
print(q.astype(int))
```
<!--sortie-->
```text
semis à densité variable, SANS interaction : T = 0.687 | p global CSR = 0.002
comptages par case (4 x 4) :
[[ 3  8  2  1]
 [ 4 13 15  7]
 [ 5 10 11  6]
 [ 1  8  5  1]]
```

*Le test et le dessin :*

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
ax1.scatter(inho[:, 0], inho[:, 1], s=16, color=VIOLET, edgecolor="white", linewidth=0.4)
ax1.set_xlim(0, COTE); ax1.set_ylim(0, COTE); ax1.set_aspect("equal")
ax1.set_title("100 adresses indépendantes, densité forte au centre", fontsize=10); ax1.set_xlabel("x (km)"); ax1.set_ylabel("y (km)")
bas, haut = np.nanpercentile(sims, [2.5, 97.5], axis=0)
ax2.fill_between(rs, bas, haut, color="#cfcfc8", alpha=0.8, label="enveloppe CSR (95 %)")
ax2.axhline(0, color="#555555", lw=1, ls="--")
ax2.plot(rs, obs, color=VIOLET, lw=2.2, label="observé")
ax2.set_xlabel("distance r (km)"); ax2.set_ylabel("L(r) - r"); ax2.set_title("La fonction K voit un « agrégat » qui n'en est pas un", fontsize=10)
ax2.legend(frameon=False, fontsize=8, loc="upper left")
plt.tight_layout()
plt.savefig("figures/ch09-inhomogene.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

**Pour aller plus loin.** Divisez la fenêtre en deux moitiés de densités différentes mais homogènes : le test de $K$ sur chaque moitié rejette-t-il encore le hasard ? Que concluez-vous sur l'échelle d'analyse ?

## Exercices

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les corrigés réutilisent les fonctions définies dans les applications 9.1 à 9.7 ci-dessus (`haversine`, `moran`, `variogramme_empirique`, `krigeage_ordinaire`, `semis_thomas`, `ripley_K`…).

### Exercice 9.1 ⭐ — quel type de données ? (section 9.1.2 du livre)

Pour chaque situation, dites s'il s'agit de données **géostatistiques**, **surfaciques** ou d'un **semis de points**, et nommez l'outil de ce chapitre qui répond à la question. (a) la gérante relève la **température** à l'intérieur de 40 entrepôts de stockage répartis dans la région et veut estimer la température dans un entrepôt qu'elle n'a pas visité. (b) Elle dispose du **taux de retour de colis** de chacun des 24 départements de la région et se demande si les départements voisins ont des taux semblables. (c) Elle a les **adresses** de tous ses clients d'un même quartier et se demande si elles se regroupent. (d) Un transporteur mesure le **délai de livraison** à 300 adresses et veut cartographier le délai moyen attendu sur toute la zone.


### Exercice 9.2 ⭐ — haversine à la main (section 9.1.3 du livre)

Calculez à la main la distance entre la Ville C $(46{,}40^\circ\text{N};\,3{,}60^\circ\text{E})$ et la Ville D $(45{,}80^\circ\text{N};\,4{,}90^\circ\text{E})$ de la région fictive, en utilisant la latitude moyenne pour le facteur $\cos\varphi$. Comparez au résultat de la formule de haversine.
### Exercice 9.3 ⭐⭐ — Moran sur quatre zones (section 9.2.2 du livre)

Quatre zones alignées A–B–C–D (chacune voisine de la précédente et de la suivante) ont pour valeurs $1,\,2,\,3,\,4$. (a) Calculez à la main l'indice de Moran avec les poids binaires, puis avec les poids standardisés par ligne. (b) Quelle est son espérance sous l'hypothèse nulle ? (c) Il n'y a que $4!=24$ façons de ranger ces valeurs sur les zones : calculez la distribution **exacte** de $I$ et la p-valeur de l'alignement observé.


### Exercice 9.4 ⭐⭐ — lire un indice local (section 9.2.4 du livre)

Dans une carte, la zone $i$ a un écart à la moyenne $z_i=+12$ et la moyenne des écarts de ses voisines vaut $(Wz)_i=-8$. La variance empirique est $m_2=100$. (a) Dans quel quadrant se trouve la zone ? (b) Que vaut son indice local $I_i$ ? (c) Peut-on conclure que c'est une valeur atypique significative ? Que faudrait-il faire ?


### Exercice 9.5 ⭐⭐ — variogramme à la main (section 9.3.2 du livre)

Cinq mesures alignées aux abscisses 0, 1, 2, 3 et 4 km ont pour valeurs $3,\,5,\,4,\,8,\,7$. Calculez le variogramme empirique aux distances 1, 2, 3 et 4 km. Que pouvez-vous dire de la forme de la courbe et de la fiabilité de ces estimations ?


### Exercice 9.6 ⭐⭐ — krigeage à la main (section 9.3.4 du livre)

En dimension 1, avec le variogramme linéaire $\gamma(h)=0{,}5\,h$, on a mesuré 20 en $x=0$ et 30 en $x=4$. (a) Écrivez et résolvez le système de krigeage ordinaire pour prédire en $x=1$ ; donnez la prédiction et la variance. (b) Si les valeurs mesurées étaient 0 et 100 au lieu de 20 et 30, la variance de krigeage changerait-elle ? Pourquoi ?


### Exercice 9.7 ⭐⭐ — le problème de l'unité spatiale modifiable (section 9.1.4 du livre)

On construit une variable $x$ corrélée aux `ventes_hab` des 144 zones (la graine est donnée dans le corrigé). On **agrège** ensuite les zones en blocs de $2\times2$, $3\times3$, $4\times4$ et $6\times6$ cases (moyenne par bloc). Comment évoluent la corrélation entre $x$ et les ventes, l'écart-type des ventes et l'indice de Moran ? Qu'en conclure pour l'interprétation d'une corrélation calculée sur des zones ?


### Exercice 9.8 ⭐⭐ — l'effet de bord sur les indices locaux (section 9.2.4 du livre)

Sur la grille $12\times12$ avec voisinage « reine », les cases ont 3 voisines (coins), 5 (bords) ou 8 (intérieur). Sans autocorrélation, la variance de l'indice local $I_i$ devrait varier comme $1/k$ où $k$ est le nombre de voisines. Vérifiez-le par simulation et expliquez pourquoi les zones de bord sont plus souvent « significatives » avec une p-valeur naïve.


### Exercice 9.9 ⭐⭐ — nombre efficace d'observations (section 9.2.5 du livre)

Pour un modèle SAR sur la grille $12\times12$ avec $\rho\in\{0{,}3;\,0{,}5;\,0{,}7;\,0{,}9;\,0{,}95\}$, estimez par simulation le **nombre efficace d'observations indépendantes** pour estimer une moyenne, défini par $n_{\text{eff}}=\operatorname{Var}(y_i)/\operatorname{Var}(\bar y)$. Commentez.


### Exercice 9.10 ⭐⭐ — cases vides (section 9.4.2 du livre)

On répartit 100 points au hasard (CSR) dans une fenêtre de $10\times10$ km, divisée en $4\times4$ cases. (a) Quelle est, à la main, la probabilité qu'une case donnée soit vide, et le nombre moyen de cases vides ? (b) Vérifiez par simulation, puis comparez au nombre de cases vides du semis agrégé de la section 9.4. Que cela dit-il ?


### Exercice 9.11 ⭐⭐⭐ — l'estimateur du variogramme est-il sans biais ? (section 9.3.2 du livre)

Le variogramme empirique est une moyenne de $\frac12(z_i-z_j)^2$. Montrez que $\mathbb E\big[\tfrac12(Z(s+h)-Z(s))^2\big]=\gamma(h)$ pour un processus stationnaire de moyenne $\mu$, puis vérifiez par simulation, en moyennant le variogramme empirique de 60 jeux de livraisons indépendants (même processus que 9.3) et en le comparant au variogramme **vrai** $\gamma(h)=0{,}4+1{,}0\,(1-e^{-h/12})$.


### Exercice 9.12 ⭐⭐⭐ — la fonction $K$ d'un processus de Thomas (section 9.4.4 du livre)

Pour un processus de Thomas de densité de centres $\kappa$ et d'étalement $\sigma$ (par coordonnée), on admet que la fonction de corrélation de paires est $g(r)=1+\dfrac{1}{4\pi\kappa\sigma^2}e^{-r^2/(4\sigma^2)}$. (a) Montrez que $K(r)=\pi r^2+\dfrac1\kappa\big(1-e^{-r^2/(4\sigma^2)}\big)$. (b) Vérifiez par simulation pour $\kappa=0{,}5$, $\mu=2$, $\sigma=0{,}4$, puis pour $\kappa=0{,}08$, $\mu=12$, $\sigma=0{,}4$. Que constatez-vous ?

## Corrigés

### Corrigé 9.1

(a) **Géostatistique** : la température existe en tout point de la région et on la mesure en 40 lieux ; on veut prédire ailleurs : variogramme et **krigeage**. (b) **Surfacique** : une valeur par zone, la question est la ressemblance entre zones voisines : matrice de poids et **indice de Moran** (avec 24 zones seulement, on teste par permutations et on indique la définition du voisinage). (c) **Semis de points** : ce sont les positions qui sont le phénomène ; on les compare au hasard complet avec les quadrats, le plus proche voisin et la fonction **$K$ de Ripley**, en pensant à la densité de population qui peut varier (9.4.5). (d) **Géostatistique** : un délai défini en tout point mesuré en 300 adresses ; **variogramme et krigeage** donnent la carte du délai attendu et une carte d'incertitude.

### Corrigé 9.2

$\Delta\varphi=0{,}60^\circ$ donne $0{,}60\times111{,}2\approx66{,}7$ km vers le sud. $\Delta\lambda=1{,}30^\circ$ : avec $\cos(46{,}1^\circ)\approx0{,}693$, $1{,}30\times111{,}2\times0{,}693\approx100{,}2$ km vers l'est. La distance est $\sqrt{66{,}7^2+100{,}2^2}\approx120{,}4$ km.

```python
print("haversine C - D      :", round(float(haversine(46.40, 3.60, 45.80, 4.90)), 1), "km")
print("estimation à la main :", round(float(np.hypot(0.60 * 111.2, 1.30 * 111.2 * np.cos(np.radians(46.1)))), 1), "km")
```
<!--sortie-->
```text
haversine C - D      : 120.4 km
estimation à la main : 120.4 km
```

### Corrigé 9.3

(a) Les écarts à la moyenne $\bar y=2{,}5$ sont $z=(-1{,}5;-0{,}5;0{,}5;1{,}5)$ et $\sum z^2=5$. Les frontières sont A–B, B–C et C–D : produits $(-1{,}5)(-0{,}5)=0{,}75$, $(-0{,}5)(0{,}5)=-0{,}25$, $(0{,}5)(1{,}5)=0{,}75$, de somme $1{,}25$. **Poids binaires** ($S_0=6$ liens orientés) : $\sum_{ij}w_{ij}z_iz_j=2\times1{,}25=2{,}5$ et $I=\frac46\times\frac{2{,}5}{5}=\frac13$. **Poids standardisés** ($S_0=4$) : A et D n'ont qu'une voisine (poids 1), B et C deux (poids $\frac12$ chacune), donc $z^\top Wz=z_Az_B+\tfrac12z_B(z_A+z_C)+\tfrac12z_C(z_B+z_D)+z_Dz_C=0{,}75+0{,}25+0{,}25+0{,}75=2$ et $I=\frac{2}{5}=0{,}4$. (b) $\mathbb E[I]=-1/(n-1)=-\frac13$ : avec $n=4$ zones seulement, l'espérance sous le hasard est loin de zéro. (c) On énumère les 24 permutations.

```python
from itertools import permutations

W4 = std_lignes(np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], dtype=float))
W4b = np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], dtype=float)
vals = np.array([1.0, 2, 3, 4])
print("I (poids binaires)      :", round(moran(vals, W4b), 4), "| I (poids standardisés) :", round(moran(vals, W4), 4))
toutes = np.array([moran(np.array(p), W4) for p in permutations(vals)])
print("nombre de permutations :", len(toutes), "| valeurs distinctes de I :", np.unique(toutes.round(4)).tolist())
print("moyenne de I sur les 24 permutations :", round(toutes.mean(), 4), "(= -1/(n-1) =", round(-1 / 3, 4), ")")
print("p-valeur exacte (I >= observé) :", round(float((toutes >= moran(vals, W4) - 1e-12).mean()), 4))
```
<!--sortie-->
```text
I (poids binaires)      : 0.3333 | I (poids standardisés) : 0.4
nombre de permutations : 24 | valeurs distinctes de I : [-0.9, -0.6, -0.5, -0.3, 0.0, 0.3, 0.4]
moyenne de I sur les 24 permutations : -0.3333 (= -1/(n-1) = -0.3333 )
p-valeur exacte (I >= observé) : 0.0833
```

L'espérance exacte sur les permutations est bien $-\frac13$. L'alignement observé (1, 2, 3, 4) et son image inversée (4, 3, 2, 1) sont les deux seuls arrangements qui atteignent cette valeur maximale : la p-valeur exacte est $2/24\approx0{,}083$, **supérieure à 5 %**. Avec quatre zones, aucune autocorrélation, même parfaite, ne peut être significative : c'est le prix du petit nombre de permutations.

### Corrigé 9.4

(a) $z_i>0$ (zone haute) et $(Wz)_i<0$ (voisines basses) : quadrant **HL** (haute entourée de basses). (b) $I_i=\dfrac{z_i\,(Wz)_i}{m_2}=\dfrac{12\times(-8)}{100}=-0{,}96$ : négatif, car la zone s'oppose à ses voisines. (c) Non : un indice local négatif ne dit rien de sa significativité. Il faut une **permutation conditionnelle** (fixer $z_i$, mélanger les autres valeurs) pour obtenir une p-valeur, puis **corriger** pour les tests multiples (Benjamini-Hochberg), comme au 9.2.4.

### Corrigé 9.5

Distance 1 : paires (3,5), (5,4), (4,8), (8,7) ; carrés des écarts 4, 1, 16, 1, total 22 ; $\hat\gamma(1)=\frac{22}{2\times4}=2{,}75$. Distance 2 : (3,4), (5,8), (4,7) ; carrés 1, 9, 9, total 19 ; $\hat\gamma(2)=\frac{19}{2\times3}\approx3{,}17$. Distance 3 : (3,8), (5,7) ; carrés 25, 4 ; $\hat\gamma(3)=\frac{29}{2\times2}=7{,}25$. Distance 4 : (3,7) ; $\hat\gamma(4)=\frac{16}{2}=8$.

```python
P5 = np.array([[0.0, 0], [1, 0], [2, 0], [3, 0], [4, 0]])
z5 = np.array([3.0, 5, 4, 8, 7])
print(variogramme_empirique(P5, z5, largeur=1.0, hmax=4.0).round(3).to_string(index=False))
```
<!--sortie-->
```text
  h  gamma  paires
1.0  2.750       4
2.0  3.167       3
3.0  7.250       2
4.0  8.000       1
```

La courbe est **croissante** (2,75 ; 3,17 ; 7,25 ; 8) et ne montre aucun palier : on ne peut pas estimer de portée. Deux raisons : il y a très peu de données, et ces valeurs montrent une **tendance** (elles augmentent avec l'abscisse), qui fait monter le variogramme (9.3.7). Surtout, le nombre de paires **diminue** avec la distance (4, 3, 2, 1) : l'estimation à 4 km repose sur **une seule paire** et n'a quasiment aucune fiabilité. C'est l'inverse de ce qui se passe en deux dimensions, où les paires lointaines sont nombreuses, mais cela rappelle qu'un variogramme se lit en regardant les effectifs.

### Corrigé 9.6

(a) $\Gamma=\begin{pmatrix}0&2\\2&0\end{pmatrix}$ (car $\gamma(4)=2$) et $\gamma_0=(\gamma(1),\gamma(3))^\top=(0{,}5;\,1{,}5)^\top$. Les équations sont $2\lambda_2+m=0{,}5$, $2\lambda_1+m=1{,}5$ et $\lambda_1+\lambda_2=1$. En soustrayant, $2(\lambda_1-\lambda_2)=1$, donc $\lambda_1=0{,}75$, $\lambda_2=0{,}25$ et $m=0$. Prédiction : $0{,}75\times20+0{,}25\times30=22{,}5$, variance $\lambda^\top\gamma_0+m=0{,}75\times0{,}5+0{,}25\times1{,}5=0{,}75$. C'est l'interpolation linéaire (de 20 à 30 sur 4 km, soit 22,5 à 1 km). (b) **Non** : la variance de krigeage $\lambda^\top\gamma_0+m$ ne dépend que de la **géométrie** (les distances) et du variogramme, jamais des valeurs mesurées. Les poids sont identiques, donc la prédiction vaudrait $0{,}75\times0+0{,}25\times100=25$ et la variance resterait $0{,}75$. Le krigeage dit à quel point le *plan d'échantillonnage* est informatif, pas si les données observées sont « surprenantes ».

```python
for valeurs in ([20.0, 30.0], [0.0, 100.0]):
    pred, var, lam = krigeage_ordinaire(np.array([[0.0, 0], [4, 0]]), np.array(valeurs), np.array([[1.0, 0]]), lineaire, (0.5,))
    print("valeurs", valeurs, "-> poids", lam.ravel().round(3), "| prédiction", pred.round(3), "| variance", var.round(3))
```
<!--sortie-->
```text
valeurs [20.0, 30.0] -> poids [0.75 0.25] | prédiction [22.5] | variance [0.75]
valeurs [0.0, 100.0] -> poids [0.75 0.25] | prédiction [25.] | variance [0.75]
```

### Corrigé 9.7

Nous construisons $x$ comme un mélange de `ventes_hab` standardisées et d'un autre champ SAR indépendant, puis nous agrégeons.

```python
Wr = std_lignes(contiguite_reine(12, 12))
rng7 = np.random.default_rng(5)
A7 = np.linalg.inv(np.eye(144) - 0.9 * Wr)
y7 = zones["ventes_hab"].to_numpy()
champ = A7 @ rng7.normal(size=144)
x7 = 0.5 * (y7 - y7.mean()) / y7.std() + 0.87 * champ / champ.std()

def agrege(v, k):
    m = 12 // k
    return v.reshape(12, 12).reshape(m, k, m, k).mean(axis=(1, 3)).ravel()

lignes = []
for k in (1, 2, 3, 4, 6):
    m = 12 // k
    ya, xa = agrege(y7, k), agrege(x7, k)
    I_k = moran(ya, std_lignes(contiguite_reine(m, m))) if m >= 3 else np.nan
    lignes.append({"bloc": f"{k} x {k}", "zones": m * m, "corr(x, ventes)": np.corrcoef(xa, ya)[0, 1],
                   "ecart_type_ventes": ya.std(), "Moran_ventes": I_k, "E[I]": -1 / (m * m - 1) if m >= 3 else np.nan})
with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 150):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 bloc  zones  corr(x, ventes)  ecart_type_ventes  Moran_ventes   E[I]
1 x 1    144            0.597             13.468         0.621 -0.007
2 x 2     36            0.619             11.142         0.570 -0.029
3 x 3     16            0.646             10.010         0.291 -0.067
4 x 4      9            0.774              9.350        -0.054 -0.125
6 x 6      4            0.869              8.431           NaN    NaN
```

La **corrélation augmente** avec l'agrégation (de 0,60 sur les 144 zones à 0,87 sur les 4 blocs de $6\times6$), l'**écart-type** des ventes diminue (de 13,5 à 8,4 : les moyennes de blocs lissent les fluctuations) et l'**indice de Moran** chute : de 0,62 à 0,57 (blocs de $2\times2$), à 0,29 ($3\times3$, soit 16 zones) puis à $-0{,}05$ ($4\times4$, soit 9 zones), à comparer à $-0{,}125$ sous le hasard pour 9 zones : à cette échelle, l'autocorrélation a pratiquement disparu (et avec 9 zones, un test aurait de toute façon très peu de puissance). Les mêmes personnes, les mêmes ventes, trois « résultats » différents selon le découpage : c'est le **problème de l'unité spatiale modifiable** (MAUP). Une corrélation calculée sur des zones n'est vraie que pour **ce découpage** : on ne peut pas la transposer à l'échelle des individus (sophisme écologique), ni à un autre découpage, sans précaution.

### Corrigé 9.8

On simule le hasard en mélangeant les valeurs de `ventes_bruit` et on calcule, pour chaque case, l'indice local $I_i=z_i(Wz)_i/m_2$.

```python
rng8 = np.random.default_rng(8)
zb = zones["ventes_bruit"].to_numpy() - zones["ventes_bruit"].mean()
m2 = zb @ zb / 144
perms = np.argsort(rng8.random((3000, 144)), axis=1)
Zs = zb[perms]
Ii_sim = Zs * (Zs @ Wr.T) / m2                                   # (3000, 144) : indices locaux sous H0
k_vois = contiguite_reine(12, 12).sum(axis=1)
lignes = []
for kk in (3, 5, 8):
    cols = k_vois == kk
    lignes.append({"voisines": kk, "cases": int(cols.sum()), "variance de I_i": Ii_sim[:, cols].var(), "variance x k": Ii_sim[:, cols].var() * kk})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
 voisines  cases  variance de I_i  variance x k
        3      4            0.333         1.000
        5     40            0.191         0.957
        8    100            0.117         0.936
```

La variance de $I_i$ est environ **2,8 fois plus grande** pour un coin (3 voisines) que pour une case intérieure (8 voisines), à comparer au rapport théorique $8/3\approx2{,}67$ ; la colonne « variance × $k$ » est à peu près constante, ce qui confirme la loi en $1/k$ : la moyenne des voisines est plus bruitée quand il y a moins de voisines. Une zone de bord ressemble donc plus facilement à une valeur extrême par hasard, et une p-valeur calculée avec la **même** loi pour toutes les zones la déclarerait trop souvent significative. Les **permutations conditionnelles** du 9.2.4 évitent ce piège, car elles tirent exactement le bon nombre de voisines pour chaque zone. Par prudence, on examine séparément les zones de bord.

### Corrigé 9.9

Pour chaque $\rho$, on simule 4 000 champs SAR et on compare la variance d'une zone à celle de la moyenne des 144 zones.

```python
rng9 = np.random.default_rng(9)
lignes = []
for rho in (0.3, 0.5, 0.7, 0.9, 0.95):
    Y9 = np.linalg.inv(np.eye(144) - rho * Wr) @ rng9.normal(size=(144, 4000))
    lignes.append({"rho": rho, "variance d'une zone": Y9.var(), "variance de la moyenne": Y9.mean(axis=0).var(), "n_eff": Y9.var() / Y9.mean(axis=0).var()})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
 rho  variance d'une zone  variance de la moyenne  n_eff
0.30                1.052                   0.014 75.715
0.50                1.179                   0.028 42.577
0.70                1.555                   0.077 20.203
0.90                3.917                   0.708  5.532
0.95                8.383                   2.805  2.989
```

Le nombre efficace d'observations **s'effondre** quand $\rho$ augmente : d'environ 76 pour $\rho=0{,}3$, il tombe à 43 pour $\rho=0{,}5$, à 20 pour $\rho=0{,}7$, à 5,5 pour $\rho=0{,}9$ (la valeur de la section 9.2.5) et à 3 pour $\rho=0{,}95$. Même pour une dépendance modérée ($\rho=0{,}5$), les 144 zones n'apportent l'information que d'environ 43 observations indépendantes. C'est la raison de la surconfiance des tests usuels.

### Corrigé 9.10

(a) Les cases ont une aire de $2{,}5\times2{,}5=6{,}25$ km² et l'intensité vaut $\lambda=1$ par km² : le nombre de points d'une case suit approximativement une loi de Poisson de moyenne $6{,}25$, donc $\mathbb P(\text{vide})=e^{-6{,}25}\approx0{,}0019$. Plus exactement, conditionnellement à $n=100$ points, chaque point tombe hors d'une case donnée avec la probabilité $\frac{15}{16}$ : $\mathbb P(\text{vide})=(15/16)^{100}\approx0{,}0016$. Pour 16 cases, le nombre moyen de cases vides est $16\times0{,}0016\approx0{,}025$ : sous le hasard complet, on s'attend à **ne presque jamais** voir de case vide.

```python
print("e^-6,25 =", round(float(np.exp(-6.25)), 5), "| (15/16)^100 =", round((15 / 16) ** 100, 5), "| 16 x (15/16)^100 =", round(16 * (15 / 16) ** 100, 4))
rng10 = np.random.default_rng(10)
vides = [(comptages(semis_poisson(100, rng10)) == 0).sum() for _ in range(5000)]
print("nombre moyen de cases vides sur 5000 semis CSR :", round(float(np.mean(vides)), 4), "| part des semis avec au moins une case vide :", round(float(np.mean(np.array(vides) > 0)), 4))
print("cases vides dans le semis agrégé :", int((comptages(semis["agrégé (Thomas)"]) == 0).sum()), "sur 16")
```
<!--sortie-->
```text
e^-6,25 = 0.00193 | (15/16)^100 = 0.00157 | 16 x (15/16)^100 = 0.0252
nombre moyen de cases vides sur 5000 semis CSR : 0.0226 | part des semis avec au moins une case vide : 0.0224
cases vides dans le semis agrégé : 7 sur 16
```

(b) La simulation confirme le calcul (environ 0,025 case vide en moyenne). Le semis agrégé de 9.4 a **7 cases vides sur 16** : un événement quasi impossible sous le hasard, qui est un autre visage de l'agrégation. (Attention : ce semis compte 75 points et non 100, ce qui rend les cases vides un peu plus plausibles, sans changer la conclusion.)

### Corrigé 9.11

Notons $\delta=Z(s+h)-Z(s)$. Par stationnarité, $\mathbb E[Z(s+h)]=\mathbb E[Z(s)]=\mu$, donc $\mathbb E[\delta]=0$, et $\mathbb E[\delta^2]=\operatorname{Var}(\delta)$. Par définition du semi-variogramme, $\gamma(h)=\frac12\mathbb E[\delta^2]$. L'estimateur $\hat\gamma(h)$ est une moyenne de $\frac12\delta^2$ sur des paires **dont la distance est $h$** : son espérance est donc $\gamma(h)$ ; il est sans biais **à $\mu$ inconnue** (ce qui le distingue de la covariance empirique, qui exige d'estimer la moyenne). Le seul biais vient du regroupement par classes (nous comparons à $\gamma$ à la distance moyenne de la classe) et d'éventuelles tendances. Vérifions par simulation.

```python
accumule = []
for graine in range(300, 360):
    d_sim, _ = livraisons(seed=graine)
    accumule.append(variogramme_empirique(d_sim[["x", "y"]].to_numpy(), d_sim["delai_jours"].to_numpy()))
h_moy = np.mean([e["h"].to_numpy() for e in accumule], axis=0)
g_moy = np.mean([e["gamma"].to_numpy() for e in accumule], axis=0)
g_sd = np.std([e["gamma"].to_numpy() for e in accumule], axis=0, ddof=1) / np.sqrt(len(accumule))
vrai_g = gamma_exp(h_moy, 0.4, 1.0, 12.0)
print(pd.DataFrame({"h": h_moy, "gamma_moyen": g_moy, "erreur_type_moyenne": g_sd, "gamma_vrai": vrai_g, "ecart_%": 100 * (g_moy / vrai_g - 1)}).round(3).to_string(index=False))
```
<!--sortie-->
```text
     h  gamma_moyen  erreur_type_moyenne  gamma_vrai  ecart_%
 3.324        0.632                0.011       0.642   -1.592
 7.745        0.867                0.014       0.876   -0.956
12.636        1.033                0.019       1.051   -1.751
17.593        1.164                0.022       1.169   -0.416
22.548        1.242                0.027       1.247   -0.389
27.549        1.303                0.030       1.299    0.277
32.529        1.329                0.032       1.334   -0.326
37.509        1.367                0.037       1.356    0.809
42.512        1.404                0.036       1.371    2.385
47.503        1.405                0.037       1.381    1.719
```

La moyenne sur 60 jeux colle au variogramme vrai à toutes les distances, à moins de 2,5 % près, et les écarts restent de l'ordre de l'erreur-type de la moyenne (colonne suivante) : rien ne montre de biais. Mais regardons la colonne des erreurs-types : elle **augmente avec la distance**. C'est la signature d'une corrélation forte entre classes de distance voisines et de grandes fluctuations d'un jeu à l'autre aux distances élevées : une moyenne de 60 jeux est précise, mais **un seul jeu** de données réelles est un tirage unique, d'où la dispersion observée en 9.3.3 sur les paramètres ajustés.

### Corrigé 9.12

(a) Par définition, $K(r)=\int_0^r 2\pi s\,g(s)\,ds$ (le nombre moyen d'autres points à moins de $r$, divisé par $\lambda$, est l'intégrale de la fonction de corrélation de paires sur le disque). Donc $K(r)=\pi r^2+\dfrac{2\pi}{4\pi\kappa\sigma^2}\int_0^r s\,e^{-s^2/(4\sigma^2)}\,ds$. Or $\int_0^r s\,e^{-s^2/(4\sigma^2)}ds=2\sigma^2\big(1-e^{-r^2/(4\sigma^2)}\big)$, d'où $K(r)=\pi r^2+\dfrac{1}{2\kappa\sigma^2}\cdot2\sigma^2\big(1-e^{-r^2/(4\sigma^2)}\big)=\pi r^2+\dfrac1\kappa\big(1-e^{-r^2/(4\sigma^2)}\big)$. Remarquons que $K$ ne dépend ni de $\mu$ ni de l'intensité totale : l'excès par rapport au hasard est $\frac1\kappa(1-e^{-r^2/4\sigma^2})$, et il tend vers $1/\kappa$ (le nombre moyen de centres par km² est $\kappa$, donc $1/\kappa$ est l'aire d'« un agrégat »). (b) Simulons.

```python
def K_thomas_theorique(r, kappa, sigma):
    return np.pi * r ** 2 + (1 / kappa) * (1 - np.exp(-r ** 2 / (4 * sigma ** 2)))

rs12 = np.array([0.25, 0.5, 1.0, 1.5, 2.0])
for kappa, mu, sigma, B in [(0.5, 2, 0.4, 500), (0.08, 12, 0.4, 300)]:
    rng12 = np.random.default_rng(12)
    Ks, effectifs = [], []
    while len(Ks) < B:
        pts12 = semis_thomas(kappa, mu, sigma, rng12)
        if len(pts12) > 10:
            Ks.append(ripley_K(pts12, rs12))
            effectifs.append(len(pts12))
    Ks = np.array(Ks)
    theo = K_thomas_theorique(rs12, kappa, sigma)
    tab = pd.DataFrame({"r": rs12, "pi r^2 (hasard)": np.pi * rs12 ** 2, "K théorique": theo, "K simulé (moyenne)": np.nanmean(Ks, axis=0)})
    tab["écart_%"] = 100 * (tab["K simulé (moyenne)"] / tab["K théorique"] - 1)
    print(f"kappa = {kappa}, mu = {mu}, sigma = {sigma}  ({B} semis) | nombre de points : moyenne {np.mean(effectifs):.0f}, "
          f"écart-type {np.std(effectifs):.0f}, coefficient de variation {np.std(effectifs) / np.mean(effectifs):.0%}")
    print(tab.round(2).to_string(index=False))
    print()
```
<!--sortie-->
```text
kappa = 0.5, mu = 2, sigma = 0.4  (500 semis) | nombre de points : moyenne 101, écart-type 17, coefficient de variation 16%
   r  pi r^2 (hasard)  K théorique  K simulé (moyenne)  écart_%
0.25             0.20         0.38                0.38    -0.15
0.50             0.79         1.43                1.43    -0.19
1.00             3.14         4.72                4.68    -0.82
1.50             7.07         9.01                8.81    -2.25
2.00            12.57        14.56               13.96    -4.13

kappa = 0.08, mu = 12, sigma = 0.4  (300 semis) | nombre de points : moyenne 97, écart-type 31, coefficient de variation 32%
   r  pi r^2 (hasard)  K théorique  K simulé (moyenne)  écart_%
0.25             0.20         1.36                1.46     7.63
0.50             0.79         4.83                5.16     6.94
1.00             3.14        13.02               13.67     4.95
1.50             7.07        19.20               19.05    -0.77
2.00            12.57        25.04               23.21    -7.34
```

Pour le premier réglage (agrégats faibles et nombreux : en moyenne 2 descendants par centre), la simulation retrouve la théorie à moins de 1 % jusqu'à $r=1$ km, puis s'en écarte de $-2{,}3\,\%$ à 1,5 km et de $-4{,}1\,\%$ à 2 km. Pour le second (agrégats forts : 12 descendants par centre), les écarts sont nettement plus importants et de **signe variable** : $+7{,}6\,\%$ à 0,25 km, $+5\,\%$ à 1 km, $-7{,}3\,\%$ à 2 km. **Cela ne signifie pas que la formule est fausse**, mais que l'**estimateur** $\hat K$ est biaisé quand le nombre total de points varie beaucoup d'un semis à l'autre : le coefficient de variation de $n$ est de 16 % pour le premier réglage et de 32 % pour le second (voir la ligne imprimée au-dessus de chaque tableau). Une cause probable est que l'estimateur divise par un nombre de points aléatoire, lui-même corrélé aux comptages de voisins : l'espérance d'un rapport n'est pas le rapport des espérances. Ajoutons que, pour les grandes distances, la méthode du bord n'utilise qu'une petite fraction des points (à 2 km, seuls ceux situés à plus de 2 km du bord, soit 36 %). Morale : **ne pas surinterpréter $\hat K$ pour des semis très agrégés ni aux grandes distances**, ce que résume la règle de ne pas dépasser le quart du côté de la fenêtre.
