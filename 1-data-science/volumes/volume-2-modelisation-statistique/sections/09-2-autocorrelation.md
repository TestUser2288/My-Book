## 9.2 Autocorrélation spatiale

> 💡 **Intuition.** La carte des ventes par délégation (9.1) semble faite d'îlots. Pour savoir si cette impression est réelle, on pose une question simple : **la valeur d'une zone ressemble-t-elle à la moyenne de ses voisines ?** Si oui, les valeurs sont *positivement autocorrélées dans l'espace*. Si les zones voisines s'opposent (une forte entourée de faibles), l'autocorrélation est *négative*. Si le voisinage n'apprend rien sur la valeur, il n'y en a pas. L'indice de Moran transforme cette question en un nombre, et un test de permutation dit si ce nombre est plus grand que ce que le hasard produirait.

### 9.2.1 Définir « voisin » : la matrice de poids

Il n'existe pas de notion de voisinage « naturelle » : c'est à nous de la **choisir**, et ce choix s'écrit sous la forme d'une matrice $W$ de taille $n\times n$, la **matrice de poids** (ou de voisinage). Son coefficient $w_{ij}\ge0$ dit à quel point la zone $j$ compte comme voisine de la zone $i$, avec $w_{ii}=0$ (une zone n'est pas sa propre voisine). Les définitions usuelles :

- **Contiguïté « tour »** (*rook*) : $w_{ij}=1$ si les zones partagent une frontière (côté) ; **contiguïté « reine »** (*queen*) : si elles partagent une frontière *ou* un coin (sur une grille : 4 contre 8 voisins).
- **$k$ plus proches voisins** : $w_{ij}=1$ si $j$ est l'un des $k$ points les plus proches de $i$. Pratique pour des points (adresses), mais $W$ n'est plus symétrique.
- **Bande de distance** : $w_{ij}=1$ si la distance entre $i$ et $j$ ne dépasse pas un seuil $d$.
- **Inverse de la distance** : $w_{ij}=1/d_{ij}^{\alpha}$, où les points proches pèsent plus.

On **standardise** presque toujours par ligne : on divise chaque ligne par sa somme, de sorte que $\sum_j w_{ij}=1$. Alors $(Wz)_i$ est la **moyenne** des valeurs des voisins de $i$, ce qui rend les formules lisibles. Notons $S_0=\sum_{i,j}w_{ij}$ la somme de tous les poids (égale à $n$ après standardisation par ligne).

Un exemple minuscule que nous garderons pour les calculs à la main : une grille $3\times3$ de neuf zones numérotées de 0 à 8 ligne par ligne, avec la contiguïté « tour ».

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

Les coins ont 2 voisines, les bords 3, le centre 4 : au total $S_0=24$ liens orientés, soit 12 frontières communes comptées dans les deux sens. Pour obtenir la version standardisée par ligne, il suffit de diviser chaque ligne par sa somme.

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

### 9.2.2 L'indice de Moran

Soit $y_1,\dots,y_n$ les valeurs observées, $\bar y$ leur moyenne et $z_i=y_i-\bar y$ les valeurs **centrées**. L'**indice de Moran** est

$$I=\frac{n}{S_0}\;\frac{\sum_{i}\sum_{j}w_{ij}\,z_i\,z_j}{\sum_i z_i^2}.$$

Lisons-le morceau par morceau. Le numérateur $\sum_{ij}w_{ij}z_iz_j$ additionne, pour chaque paire de voisines, le **produit** de leurs écarts à la moyenne : il est positif quand les deux voisines sont du même côté de la moyenne (toutes deux hautes ou toutes deux basses) et négatif quand elles s'opposent. Le dénominateur $\sum z_i^2$ est la variance totale (à un facteur près), qui joue le rôle de **normalisation** : $I$ ressemble à un coefficient de corrélation entre une zone et ses voisines. Le facteur $n/S_0$ compense le nombre de liens.

> 💡 **Une lecture géométrique.** Avec une matrice standardisée par ligne ($S_0=n$), $I=\dfrac{z^\top Wz}{z^\top z}$. Mais $Wz$ est le vecteur des **moyennes des valeurs voisines**. Donc $I$ est exactement la **pente de la droite de régression** de « la moyenne de mes voisines » en fonction de « ma valeur » : le *diagramme de Moran* (nuage de $Wz$ contre $z$) montre ce que mesure l'indice. Une pente de 0,6 signifie : quand une zone est supérieure à la moyenne de 10, ses voisines le sont, en moyenne, de 6.

**Calcul à la main.** Sur la grille $3\times3$ avec des poids binaires ($S_0=24$), prenons les valeurs de 1 à 9 rangées ligne par ligne : une progression régulière, donc des voisines qui se ressemblent.

$$\begin{pmatrix}1&2&3\\4&5&6\\7&8&9\end{pmatrix},\qquad \bar y=5,\qquad z=\begin{pmatrix}-4&-3&-2\\-1&0&1\\2&3&4\end{pmatrix},\qquad \sum z_i^2=60.$$

La somme $\sum_{ij}w_{ij}z_iz_j$ compte chaque frontière deux fois, une fois dans chaque sens. Calculons les 12 produits sur les frontières, en les rangeant selon leur orientation.

- **Frontières horizontales** : $(-4)(-3)=12$ ; $(-3)(-2)=6$ ; $(-1)(0)=0$ ; $(0)(1)=0$ ; $(2)(3)=6$ ; $(3)(4)=12$ : total 36.
- **Frontières verticales** : $(-4)(-1)=4$ ; $(-1)(2)=-2$ ; $(-3)(0)=0$ ; $(0)(3)=0$ ; $(-2)(1)=-2$ ; $(1)(4)=4$ : total 4.

La somme sur les frontières vaut 40, donc $\sum_{ij}w_{ij}z_iz_j=2\times40=80$ et

$$I=\frac{9}{24}\times\frac{80}{60}=0{,}5 .$$

Dans l'autre sens, rangeons en **damier** : des 1 et des 9 qui alternent, de sorte que chaque zone n'ait que des voisines très différentes. Ici $\bar y=41/9$, les zones à 1 ont $z=-32/9$, celles à 9 ont $z=+40/9$, chaque frontière relie un 1 à un 9 (produit $-1280/81$), il y a 12 frontières donc $\sum_{ij}w_{ij}z_iz_j=-2\times12\times1280/81$, et $\sum z^2=11520/81$. Tous calculs faits, $I=\frac{9}{24}\times\frac{-30720}{11520}=-1$ : l'autocorrélation négative maximale. Vérifions les deux calculs, puis la version standardisée par ligne.

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

Les valeurs 0,5 et −1 retrouvent nos calculs à la main. La version standardisée donne un nombre un peu différent : le **choix de $W$ fait partie du modèle** et il doit être indiqué avec le résultat.

> 📐 **Que vaut $I$ en l'absence d'autocorrélation ?** Sous l'hypothèse nulle « les valeurs sont échangeables » (aucune relation avec la position), toute permutation des $y_i$ sur les zones est aussi plausible qu'une autre. Pour $i\ne j$, $\mathbb E[z_iz_j]=\frac{1}{n(n-1)}\sum_{a\ne b}z_az_b=\frac{(\sum_a z_a)^2-\sum_a z_a^2}{n(n-1)}=-\frac{\sum_a z_a^2}{n(n-1)}$, car $\sum_a z_a=0$. Comme $w_{ii}=0$, il vient
>
> $$\mathbb E[I]=\frac{n}{S_0}\,\frac{\sum_{i\ne j}w_{ij}\,\mathbb E[z_iz_j]}{\sum z_i^2}=\frac{n}{S_0}\cdot S_0\cdot\frac{-1}{n(n-1)}=-\frac{1}{n-1}.$$
>
> Ce n'est pas exactement 0 (la contrainte « la moyenne des $z$ est nulle » induit une très légère corrélation négative), mais pour $n=144$ zones, $-1/143\approx-0{,}007$ : négligeable. Pour $n=9$, l'espérance vaut $-0{,}125$, ce qui est loin d'être négligeable : on **ne compare pas** un petit Moran à zéro mais à $-1/(n-1)$.

**Donner un sens à la valeur observée : deux voies.** Quelle valeur de $I$ est « grande » ? Il faut connaître la loi de $I$ sous l'hypothèse nulle.

1. **Approximation normale.** Sous une hypothèse de normalité des $y_i$, on connaît la variance de $I$ :
$$\operatorname{Var}(I)=\frac{n^2S_1-nS_2+3S_0^2}{(n^2-1)S_0^2}-\mathbb E[I]^2,$$
avec $S_1=\frac12\sum_{ij}(w_{ij}+w_{ji})^2$ et $S_2=\sum_i\big(\sum_j w_{ij}+\sum_j w_{ji}\big)^2$. On forme alors $z_I=(I-\mathbb E[I])/\sqrt{\operatorname{Var}(I)}$ et on le compare à une loi normale centrée réduite.
2. **Permutations.** Plus simple et sans hypothèse de loi : on **mélange** les valeurs sur les zones $B$ fois, on recalcule $I$ à chaque fois, et on regarde où tombe la valeur observée parmi ces $B$ valeurs. C'est le *test de permutation* du volume I (section 3.7.4), appliqué à l'espace. La p-valeur unilatérale pour une autocorrélation positive est $\dfrac{1+\#\{I^*\ge I_{\text{obs}}\}}{B+1}$.

Appliquons-les à nos 144 délégations, avec la contiguïté « reine » (8 voisins). Voici d'abord le code qui a fabriqué les ventes (la même fonction est dans `build/donnees_ch09.py`). On part de bruits indépendants $e_i$ et on les propage dans l'espace par $z=(I-\rho W)^{-1}e$ : un **modèle autorégressif spatial** (SAR), où chaque zone est un reflet de ses voisines, avec une force $\rho=0{,}9$.

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

def delegations(seed=9, n_lig=12, n_col=12, rho=0.9):
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

deleg = delegations()
fichier = pd.read_csv("donnees/ch09-delegations.csv")
print("identique au fichier fourni :", np.allclose(deleg[["ventes_hab", "ventes_bruit"]], fichier[["ventes_hab", "ventes_bruit"]]))
print(deleg[["ventes_hab", "ventes_bruit"]].describe().round(2).to_string())
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

Nous disposons de deux variables : `ventes_hab` (structurée dans l'espace) et `ventes_bruit` (du bruit indépendant, **sans** structure spatiale ; sa moyenne et son écart-type sont proches de ceux de l'autre variable, sans être identiques). Cette deuxième variable est notre *témoin* : un bon indice doit y voir du hasard.

```python
W = std_lignes(contiguite_reine(12, 12))
n = len(deleg)

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

def moran_permutations(y, W, B=9999, seed=1):
    """B valeurs de I obtenues en mélangeant y sur les zones."""
    rng = np.random.default_rng(seed)
    z = np.asarray(y, dtype=float) - np.mean(y)
    idx = np.argsort(rng.random((B, len(z))), axis=1)          # B permutations de 0..n-1
    Z = z[idx]                                                  # chaque ligne est un mélange de z
    return len(z) / W.sum() * (((Z @ W) * Z).sum(axis=1)) / (z @ z)

lignes = []
for nom in ["ventes_hab", "ventes_bruit"]:
    y = deleg[nom].to_numpy()
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

La variable structurée a un indice de Moran nettement positif et une p-valeur proche de la plus petite que l'on puisse obtenir avec $B=9999$ permutations (jamais 0 : le $+1$ au numérateur représente la valeur observée elle-même). Le témoin, lui, est proche de $-1/(n-1)$ et sa p-valeur est élevée. Remarquons aussi que l'écart-type obtenu par permutations est voisin de celui de la formule normale : deux voies, une même conclusion.

> ⚠️ **L'indice ne vaut pas $\rho$.** Nous avons fabriqué les données avec $\rho=0{,}9$, mais $I\ne0{,}9$. Le paramètre $\rho$ d'un modèle SAR et l'indice de Moran mesurent la dépendance **sur des échelles différentes** : $\rho$ gouverne la façon dont un choc se propage de proche en proche, alors que $I$ résume la ressemblance moyenne entre voisines **directes**. Une forte propagation ($\rho$ proche de 1) produit de grandes plages, mais la ressemblance entre deux voisines immédiates reste partielle. Ne comparez jamais $I$ à une probabilité ou à un coefficient du modèle.

On voit mieux ce que mesure $I$ avec le **diagramme de Moran** (le nuage de la moyenne des voisines contre la valeur de la zone) et l'histogramme de la distribution nulle :

```python
BLEU, ORANGE, AQUA, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
y = deleg["ventes_hab"].to_numpy()
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

![À gauche : diagramme de Moran des ventes par habitant ; la pente de la droite est l'indice de Moran. À droite : distribution de I quand on mélange les valeurs au hasard sur les zones (hypothèse nulle) et valeur observée.](figures/ch09-moran.png)

La pente du diagramme est **égale** à l'indice de Moran, comme annoncé. L'histogramme de droite montre la loi de $I$ quand les valeurs sont distribuées au hasard : centrée sur un nombre proche de zéro, avec un étalement de l'ordre de 0,05. La valeur observée est loin à droite de cette loi : le hasard ne produit pas un tel alignement.

**La sensibilité au choix de $W$.** Le résultat dépend-il de notre définition du voisinage ? Recalculons $I$ avec cinq définitions, construites à partir des **distances** entre les centres des zones, ce qui est la façon de faire pour des points dans l'espace quelconques.

```python
xy = deleg[["x", "y"]].to_numpy()
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
                   "I_temoin": moran(deleg["ventes_bruit"].to_numpy(), Ws),
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

Tous les choix donnent un indice nettement positif et une p-valeur minimale, et le témoin reste proche de zéro. Mais **la valeur de $I$ change** : plus on élargit le voisinage, plus on mélange des zones qui se ressemblent peu, et plus l'indice diminue. Retenons-en une règle : une conclusion du type « il y a de l'autocorrélation » ne devrait pas dépendre du choix de $W$ ; la **valeur** de $I$, elle, n'a de sens que pour un $W$ donné. On indique donc toujours la définition choisie.

### 9.2.3 L'indice de Geary

L'indice de Moran compare chaque zone **à la moyenne** (par les écarts $z_i$). Celui de Geary compare directement les zones voisines **entre elles** :

$$C=\frac{n-1}{2S_0}\;\frac{\sum_{i}\sum_{j}w_{ij}\,(y_i-y_j)^2}{\sum_i z_i^2}.$$

Le numérateur est la somme des carrés des **différences** entre voisines, qui sera petite si les voisines se ressemblent. Sans autocorrélation, $\mathbb E[C]=1$. Une valeur **inférieure à 1** indique une autocorrélation positive ; supérieure à 1, une autocorrélation négative. L'échelle est donc inversée par rapport à Moran. Geary est plus sensible aux **différences locales** (à l'échelle d'une paire de voisines) alors que Moran, qui passe par la moyenne globale, est plus sensible à la structure d'ensemble.

> 📐 **Le lien avec le variogramme (9.3).** Le terme $\frac12(y_i-y_j)^2$ est exactement la *semi-variance* d'une paire, la brique du variogramme. L'indice de Geary est donc, à une normalisation près, une moyenne de semi-variances **sur les paires voisines** divisée par la variance totale. C'est une première approximation du variogramme à une seule distance.

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
    yy = deleg[nom].to_numpy()
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

Les deux indices racontent la même histoire : la variable structurée a un $C$ bien inférieur à 1, le témoin est proche de 1.

### 9.2.4 Où sont les îlots ? Les indices locaux (LISA)

Un seul nombre pour toute la carte ne dit pas **où** se trouvent les îlots. Les **indicateurs locaux d'association spatiale** (LISA) décomposent l'indice de Moran en une contribution par zone :

$$I_i=\frac{z_i}{m_2}\sum_j w_{ij}\,z_j,\qquad m_2=\frac1n\sum_k z_k^2 .$$

Avec une matrice standardisée par ligne, la somme des $I_i$ vaut exactement $n\,I$. Chaque $I_i$ est positif quand la zone $i$ et ses voisines sont du même côté de la moyenne. Le signe de $z_i$ et celui de la moyenne voisine $Wz_i$ donnent les **quatre quadrants** du diagramme de Moran :

- **HH** : zone haute entourée de zones hautes (un **îlot de fortes valeurs**) ;
- **LL** : zone basse entourée de zones basses (un îlot de faibles valeurs) ;
- **HL / LH** : une zone haute entourée de basses (ou l'inverse), des **valeurs atypiques** locales.

Pour savoir si un $I_i$ est significatif, on utilise une **permutation conditionnelle** : on garde la valeur de la zone $i$ fixe, on mélange les autres valeurs sur les autres zones, et on recalcule $I_i$. Mais attention : nous faisons **144 tests à la fois**. Comme au volume I (section 3.5.5), sans correction nous attendrions environ 7 faux positifs (5 % de 144) même sur des données sans structure ; nous utiliserons la procédure de **Benjamini-Hochberg**.

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

lignes = []
resultats = {}
for nom in ["ventes_hab", "ventes_bruit"]:
    Ii, quad, pv = lisa(deleg[nom].to_numpy(), W)
    rej = benjamini_hochberg(pv)
    resultats[nom] = (Ii, quad, pv, rej)
    comptes = pd.Series(np.where(rej, quad, "non significatif")).value_counts()
    lignes.append({"variable": nom, "somme_Ii/n": Ii.sum() / len(Ii), "I_global": moran(deleg[nom].to_numpy(), W),
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

La première colonne vérifie la propriété annoncée : la moyenne des $I_i$ est bien l'indice de Moran global. Sur le témoin, 5 zones sur 144 (3 %, soit à peu près les 5 % attendus du hasard) sortent avec la p-valeur brute : c'est le prix des tests multiples. La correction de Benjamini-Hochberg les écarte **toutes** (0 zone significative). Sur la variable structurée, 49 zones sont significatives avant correction et 35 après : 11 îlots de fortes valeurs (HH), 22 de faibles valeurs (LL) et 2 valeurs atypiques (LH). Regardons la carte des zones significatives.

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

![Carte des indicateurs locaux de Moran significatifs (Benjamini-Hochberg à 5 %). À gauche, les ventes par habitant : des îlots de fortes (rouge) et de faibles (bleu) valeurs. À droite, le témoin sans structure spatiale : presque rien n'est significatif.](figures/ch09-lisa.png)

La carte de gauche **localise** les îlots : l'indice global disait *qu'il y en a*, les indices locaux disent *où*. À droite, le témoin est quasiment vide.

> ⚠️ **Deux précautions.** (1) Les indices locaux ne sont **pas indépendants** (zones voisines partagent des voisines), donc le taux de faux positifs effectif est mal maîtrisé même avec la correction de Benjamini-Hochberg : on considère les zones signalées comme des **pistes à examiner**, pas comme des découvertes. (2) Les zones **en bordure** de la carte ont moins de voisines : leurs indices sont plus bruités (nous y reviendrons à la section 9.5).

### 9.2.5 Pourquoi cela compte : la régression qui voit des relations qui n'existent pas

Revenons à l'avertissement de 9.1.1 : l'autocorrélation rend les erreurs-types usuelles **trop petites**. Mesurons-le. Nous simulons **deux variables sans aucun lien** (deux champs spatiaux SAR indépendants, avec la même force $\rho=0{,}9$ que plus haut), nous régressons l'une sur l'autre par moindres carrés ordinaires et nous testons la pente à 5 %. Si la méthode est honnête, nous devrions rejeter à tort dans environ **5 %** des cas. Nous recommençons 1 000 fois.

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

# Nombre « efficace » d'observations indépendantes pour estimer une moyenne
var_y = Y.var()                                                # variance d'une zone
var_moy = Y.mean(axis=0).var()                                 # variance de la moyenne des 144 zones
print("variance d'une zone :", round(var_y, 2), "| variance de la moyenne de 144 zones :", round(var_moy, 3),
      "| si indépendantes, ce serait", round(var_y / n, 3))
print("nombre efficace d'observations indépendantes :", round(var_y / var_moy, 1), "sur", n)
```
<!--sortie-->
```text
MCO : proportion de rejets à 5 % alors qu'il n'y a AUCUN lien : 0.459
variance d'une zone : 3.9 | variance de la moyenne de 144 zones : 0.706 | si indépendantes, ce serait 0.027
nombre efficace d'observations indépendantes : 5.5 sur 144
```

Le résultat est sans appel : au lieu des 5 % promis, le test usuel rejette à tort dans **46 %** des cas, presque une fois sur deux. Et pour estimer une moyenne, nos 144 zones valent environ **5,5 observations indépendantes** : la variance de la moyenne est de 0,71, contre 0,027 si les zones étaient indépendantes. Le test usuel suppose des erreurs indépendantes ; ici elles ne le sont pas, et l'erreur-type de la pente est sous-estimée d'un facteur important.

> 💡 **Le remède, dans son principe.** Il faut tenir compte de la dépendance dans le calcul. Si l'on **connaissait** la structure de covariance $\Sigma$ des erreurs, on appliquerait les **moindres carrés généralisés** (MCG), c'est-à-dire des moindres carrés sur des données *blanchies*. Pour notre modèle SAR, le blanchiment est explicite : multiplier le vecteur $y$ par $(I-\rho W)$ « défait » la propagation. Vérifions que cela rétablit le niveau du test, en supposant ici $\rho$ connu (c'est le cas idéal ; en pratique on l'estime).

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
MCG avec rho connu : proportion de rejets à 5 % : 0.053
Moran des résidus MCO (première paire) : 0.425 | p-valeur par permutation : 0.001
```

Avec les moindres carrés généralisés, le niveau du test retombe à 5,3 %, tout près des 5 % annoncés. Et, comme le montre la dernière ligne, il existe un **signal d'alarme** simple pour une analyse réelle : calculer l'indice de Moran des **résidus** du modèle. S'il est significatif, les erreurs ne sont pas indépendantes et les erreurs-types usuelles sont à écarter.

> 🛠️ **En pratique.** On ne connaît pas $\rho$ : on l'estime avec un **modèle autorégressif spatial** (le *spatial lag* ou le *spatial error model*, estimés par maximum de vraisemblance), ou l'on modélise la covariance par un variogramme (section 9.3, krigeage universel), ou l'on utilise des **erreurs-types robustes par blocs spatiaux**. Les outils exacts sortent du cadre de ce chapitre, mais le message est général : *si vos observations sont proches dans l'espace, testez l'autocorrélation des résidus avant de lire vos p-valeurs.*

> ✅ **À retenir.**
> - Pour parler d'autocorrélation, il faut **définir le voisinage** : une matrice de poids $W$ (contiguïté, $k$ voisins, bande de distance), presque toujours standardisée par ligne. Ce choix fait partie du résultat.
> - **Indice de Moran** : $I=\frac{n}{S_0}\frac{\sum w_{ij}z_iz_j}{\sum z_i^2}$. Avec $W$ standardisée, c'est la pente de « moyenne des voisines » contre « valeur de la zone ». Sous l'hypothèse nulle, $\mathbb E[I]=-1/(n-1)$ ; on le teste par **permutations**.
> - **Geary** ($\mathbb E[C]=1$, $C<1$ pour une autocorrélation positive) est plus sensible aux différences locales.
> - Les **indices locaux** (LISA) disent *où* sont les îlots (HH, LL) et les valeurs atypiques (HL, LH) ; avec 144 tests, il faut **corriger** (Benjamini-Hochberg).
> - Ignorer l'autocorrélation fait **rejeter à tort** bien plus souvent que 5 % : testez l'indice de Moran des résidus avant de croire une p-valeur.
