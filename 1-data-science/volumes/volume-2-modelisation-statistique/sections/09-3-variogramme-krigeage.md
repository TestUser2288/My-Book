## 9.3 Variogramme et krigeage

> 💡 **Intuition.** Yasmine veut promettre un délai à une cliente de Zaghouan, où personne n'a encore été livré. Que peut-on dire ? Les livraisons **proches** de cette adresse sont informatives, celles qui sont loin le sont moins, et deux livraisons voisines l'une de l'autre se répètent (elles apportent à peu près la même information). Le **variogramme** mesure à quelle vitesse la ressemblance entre deux mesures s'estompe quand la distance augmente. Le **krigeage** s'en sert pour fabriquer, en tout point, la **meilleure moyenne pondérée** des mesures voisines, avec une **marge d'erreur**.

### 9.3.1 De la corrélation entre voisines à une fonction de la distance

Au 9.2, la ressemblance entre voisines était résumée par un seul nombre (Moran) pour une définition de voisinage fixée. En géostatistique, on décrit toute la courbe : *comment la ressemblance dépend de la distance $h$ qui sépare deux points*.

Le modèle de base écrit la mesure en un point $s$ du plan comme la somme d'un niveau moyen, d'un champ qui varie régulièrement et d'un bruit de mesure :

$$Z(s)=\mu+S(s)+\varepsilon(s).$$

On suppose que le champ est **stationnaire** : sa moyenne $\mu$ est la même partout et la dépendance entre deux points ne dépend que du **vecteur** qui les sépare, pas de l'endroit où ils sont. (L'hypothèse minimale, dite *intrinsèque*, ne demande que la stationnarité des **différences** $Z(s+h)-Z(s)$.) On définit alors le **semi-variogramme**

$$\gamma(h)=\tfrac12\,\mathbb E\big[(Z(s+h)-Z(s))^2\big],$$

la moitié de l'écart quadratique moyen entre deux mesures séparées par $h$. Il est nul à l'origine ($\gamma(0)=0$) et croît d'ordinaire avec $h$ : plus deux points sont éloignés, moins ils se ressemblent. Trois nombres décrivent la courbe :

- la **pépite** (*nugget*) $c_0$ : la valeur de $\gamma$ juste après 0. Elle regroupe le bruit de mesure et les variations à une échelle plus petite que la distance minimale entre points. Même deux mesures très proches ne se ressemblent pas parfaitement ;
- le **palier** (*sill*) : la valeur de $\gamma$ quand la courbe se stabilise. C'est la variance totale du processus ($c_0+c$) ;
- la **portée** (*range*) $a$ : la distance au-delà de laquelle deux points ne se ressemblent plus davantage qu'au hasard : deux points plus éloignés que la portée sont (presque) indépendants.

> 📐 **Lien avec la covariance.** Si le processus est de variance finie $C(0)$ et de covariance $C(h)=\operatorname{Cov}(Z(s),Z(s+h))$, alors
> $$\gamma(h)=\tfrac12\operatorname{Var}\big(Z(s+h)-Z(s)\big)=\tfrac12\big[C(0)+C(0)-2C(h)\big]=C(0)-C(h).$$
> Le variogramme est donc la covariance « retournée » : $\gamma$ monte quand $C$ descend, et le palier vaut $C(0)$. Le variogramme est plus général (il existe aussi quand la variance est infinie) et il se **déduit directement des données**, ce qui explique qu'il soit l'outil standard.

**Un calcul à la main.** Quatre mesures alignées aux abscisses 0, 1, 2 et 3 km, de valeurs 2, 3, 5 et 4. À la distance 1 km, il y a trois paires (0-1, 1-2, 2-3) dont les écarts au carré valent $(3-2)^2=1$, $(5-3)^2=4$ et $(4-5)^2=1$ : $\hat\gamma(1)=\frac{1+4+1}{2\times3}=1{,}0$. À 2 km, deux paires (0-2, 1-3) : $\frac{(5-2)^2+(4-3)^2}{2\times2}=\frac{9+1}{4}=2{,}5$. À 3 km, une seule paire : $\hat\gamma(3)=\frac{(4-2)^2}{2}=2{,}0$. Le diviseur est **deux fois le nombre de paires**, d'où le « semi » dans le mot.

### 9.3.2 Le variogramme empirique

Avec $n$ points, l'estimateur classique de la semi-variance à la distance $h$ est

$$\hat\gamma(h)=\frac{1}{2N(h)}\sum_{(i,j)\in N(h)}(z_i-z_j)^2,$$

où $N(h)$ est l'ensemble des paires dont la distance est « à peu près » $h$ (on découpe les distances en **classes** de largeur fixe) et $N(h)$ leur nombre. Le code suivant fabrique cet estimateur. Nous le validons d'abord sur les quatre points ci-dessus.

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

Les trois lignes redonnent nos calculs à la main : 1,0 ; 2,5 ; 2,0. Passons aux 200 livraisons. Voici d'abord le code qui les a fabriquées, c'est-à-dire la **vérité** que nous allons chercher à retrouver (nous ne la regarderons qu'après l'analyse). C'est un champ aléatoire gaussien stationnaire de covariance exponentielle, observé avec un bruit de mesure.

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

Calculons le variogramme empirique de ces données, avec des classes de 5 km jusqu'à 50 km (la moitié de la taille du domaine : au-delà, les paires deviennent rares et dépendent de la forme du domaine, c'est la règle de pouce usuelle).

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

Le tableau montre un variogramme qui **monte puis se stabilise** : le comportement attendu d'un processus stationnaire. Remarquons aussi que le nombre de paires croît avec la distance (il y a bien plus de paires éloignées que de paires proches), si bien que les premières classes, justement les plus importantes pour estimer la pépite, sont aussi les moins fiables.

> ⚠️ **Le variogramme empirique est bruité.** Chaque point $\hat\gamma(h)$ est une moyenne de carrés d'écarts, un estimateur sensible aux valeurs extrêmes et fortement **corrélé** d'une classe à l'autre (les mêmes points participent à beaucoup de paires). Le choix de la largeur des classes est un compromis : des classes étroites donnent une courbe précise mais bruitée, des classes larges lissent la forme près de l'origine. Il existe des estimateurs robustes (Cressie-Hawkins, qui utilise la racine des écarts absolus), mais l'estimateur classique reste la référence pour des données à peu près gaussiennes.

### 9.3.3 Modèles de variogramme et ajustement

Une courbe en escalier de 10 points ne peut pas servir directement : il faut une **fonction** $\gamma(h)$ pour toute distance $h$, et pas n'importe laquelle : elle doit garantir qu'une variance calculée avec elle n'est jamais négative (on dit que $-\gamma$ doit être *conditionnellement définie positive*). On ne choisit donc pas une courbe au hasard : on utilise une famille de modèles **valides**. Trois sont standard, avec $c_0$ la pépite, $c$ le palier partiel (palier total $c_0+c$) et $a$ le paramètre de portée :

| Modèle | $\gamma(h)$ pour $h>0$ | Portée pratique | Allure près de l'origine |
|---|---|---|---|
| **Sphérique** | $c_0+c\left(\frac{3h}{2a}-\frac{h^3}{2a^3}\right)$ si $h<a$, sinon $c_0+c$ | $a$ (atteinte exactement) | linéaire |
| **Exponentiel** | $c_0+c\,(1-e^{-h/a})$ | $3a$ (95 % du palier) | linéaire |
| **Gaussien** | $c_0+c\,(1-e^{-(h/a)^2})$ | $\sqrt3\,a$ | **parabolique** (très lisse) |

La **portée pratique** est la distance où le variogramme atteint 95 % de son palier. Elle vaut $a$ pour le modèle sphérique, $3a$ pour l'exponentiel (qui n'atteint jamais exactement son palier) et $\sqrt 3\,a$ pour le gaussien. Le comportement près de l'origine traduit la régularité du phénomène : un variogramme linéaire correspond à un champ continu mais rugueux, un variogramme parabolique à un champ très lisse.

Pour ajuster un modèle, on cherche $(c_0,c,a)$ qui rapprochent le modèle des points empiriques par **moindres carrés pondérés**. Les classes contenant beaucoup de paires sont plus fiables et celles où $\gamma$ est petit ont une variance plus faible, d'où les poids (de Cressie) $N(h)/\gamma_{\text{modèle}}(h)^2$ : on minimise $\sum_k N_k\big(\hat\gamma_k/\gamma_k(\theta)-1\big)^2$.

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

Les trois modèles proposent un **palier total** voisin (entre 1,28 et 1,32), mais des décompositions différentes entre pépite et portée : le modèle exponentiel trouve presque une pépite nulle et une portée pratique d'environ 24 km, le gaussien une pépite de 0,39 et une portée de 18 km. Leurs **critères** d'ajustement sont très proches (47,2 pour l'exponentiel, 48,1 et 48,4 pour les deux autres) : l'exponentiel est légèrement meilleur, mais **les données ne permettent pas de trancher** entre les formes. Regardons-les sur la figure.

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

![Variogramme empirique (points, taille proportionnelle au nombre de paires) et trois modèles ajustés. La ligne pointillée est la variance empirique des données, voisine du palier.](figures/ch09-variogramme.png)

> 🧪 **La vérité terrain.** Les données sont simulées : nous connaissons la bonne réponse. C'est un champ de covariance exponentielle $C(h)=1{,}0\,e^{-h/12}$, soit un palier partiel $c=1{,}0$ et un paramètre $a=12$ (portée pratique 36 km), observé avec une **pépite** de $0{,}4$ (palier total $1{,}4$). Comparons avec la ligne « exponentiel » du tableau : le **palier total** est bien retrouvé (1,32 contre 1,4), mais la **pépite** est très sous-estimée (0,04 contre 0,4) et la **portée pratique** aussi (24 km contre 36 km). Ce qui est facile à estimer, c'est la variance totale ; ce qui est difficile, c'est sa répartition entre bruit de mesure et dépendance spatiale. La suite montre que ce n'est pas une particularité de notre tirage.

**Cet ajustement est-il typique ?** Une seule série de 200 mesures est un seul tirage ; il est légitime de se demander ce qui se passerait avec d'autres tirages du même processus. Faisons l'expérience : nous répétons la simulation avec 30 graines différentes, nous réajustons à chaque fois le modèle exponentiel et nous regardons la dispersion des paramètres estimés.

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

> ⚠️ **Ce qu'il faut retenir de cette expérience.** Sur 30 tirages, le palier total est estimé avec une assez bonne précision (médiane 1,38 pour une vérité de 1,4), mais la pépite varie de 0,10 à 0,54 (entre le 10e et le 90e percentile) et la portée pratique de 16 à 52 km, pour des vérités de 0,4 et 36 km. La **médiane** de la portée pratique (29 km) est elle-même inférieure à la vérité : l'ajustement a tendance à la sous-estimer. Notre tirage (pépite 0,04, portée 24 km) est dans la queue basse de la distribution, sans être aberrant. Même avec 200 points, les paramètres du variogramme sont donc **peu précis** : la pépite et la portée sont particulièrement difficiles à identifier, parce que l'une et l'autre se jouent dans les toutes premières classes de distance, qui contiennent peu de paires. Ce n'est pas un défaut de notre code, c'est la nature du problème. Deux conséquences pratiques : (1) ne jamais donner un variogramme ajusté comme un fait certain, (2) comme nous le verrons, le **krigeage** est heureusement assez peu sensible aux petites erreurs de variogramme.

### 9.3.4 Le krigeage : la meilleure moyenne pondérée

Nous voulons prédire $Z(s_0)$ en un point $s_0$ où nous n'avons pas mesuré. Cherchons un prédicteur de la forme d'une **moyenne pondérée** des $n$ mesures :

$$\hat Z(s_0)=\sum_{i=1}^n\lambda_i\,Z(s_i),\qquad \sum_i\lambda_i=1.$$

La contrainte $\sum\lambda_i=1$ garantit que le prédicteur est **sans biais** quand la moyenne $\mu$ est constante *mais inconnue* (c'est le **krigeage ordinaire**) : $\mathbb E[\hat Z]=\mu\sum\lambda_i=\mu$. Parmi tous les poids possibles, nous voulons ceux qui **minimisent l'erreur quadratique moyenne** $\mathbb E[(\hat Z(s_0)-Z(s_0))^2]$.

> 📐 **Dérivation.** Grâce à la contrainte, l'erreur se réécrit $Z(s_0)-\hat Z(s_0)=\sum_i\lambda_i\big(Z(s_0)-Z(s_i)\big)$ : c'est une combinaison d'**accroissements**, dont on connaît les moments grâce au variogramme. Pour deux accroissements $a=Z(s_0)-Z(s_i)$ et $b=Z(s_0)-Z(s_j)$, on a $ab=\tfrac12\big[a^2+b^2-(a-b)^2\big]$ et $a-b=Z(s_j)-Z(s_i)$, donc $\mathbb E[ab]=\gamma_{i0}+\gamma_{j0}-\gamma_{ij}$, en notant $\gamma_{ij}=\gamma(\|s_i-s_j\|)$. On en déduit, en utilisant $\sum\lambda=1$ :
>
> $$\sigma_K^2(\lambda)=\sum_i\sum_j\lambda_i\lambda_j(\gamma_{i0}+\gamma_{j0}-\gamma_{ij})=2\sum_i\lambda_i\gamma_{i0}-\sum_i\sum_j\lambda_i\lambda_j\gamma_{ij}=2\lambda^\top\gamma_0-\lambda^\top\Gamma\lambda,$$
>
> où $\Gamma=(\gamma_{ij})$ et $\gamma_0=(\gamma_{i0})_i$. On minimise sous la contrainte $\mathbf 1^\top\lambda=1$ avec un **multiplicateur de Lagrange** $m$ (comme au volume I, section 1.3.5) : $\mathcal L=2\lambda^\top\gamma_0-\lambda^\top\Gamma\lambda-2m(\mathbf 1^\top\lambda-1)$. En annulant le gradient en $\lambda$ : $\gamma_0-\Gamma\lambda-m\mathbf 1=0$. Le système à résoudre est donc
>
> $$\begin{pmatrix}\Gamma&\mathbf 1\\\mathbf 1^\top&0\end{pmatrix}\begin{pmatrix}\lambda\\m\end{pmatrix}=\begin{pmatrix}\gamma_0\\1\end{pmatrix},\qquad\boxed{\hat Z(s_0)=\lambda^\top Z},\qquad\boxed{\sigma_K^2=\lambda^\top\gamma_0+m}.$$
>
> (Pour la variance : $\Gamma\lambda=\gamma_0-m\mathbf 1$ donne $\lambda^\top\Gamma\lambda=\lambda^\top\gamma_0-m$, donc $\sigma_K^2=2\lambda^\top\gamma_0-(\lambda^\top\gamma_0-m)=\lambda^\top\gamma_0+m$.)

Trois choses à remarquer dans ce système. (1) Les poids dépendent **des distances entre les points de mesure** (la matrice $\Gamma$, qui sait que deux points voisins sont redondants) *et* de la distance de chaque point à la cible ($\gamma_0$) : on n'est pas une simple pondération par l'inverse de la distance. (2) La variance de krigeage $\sigma_K^2$ ne dépend **que de la géométrie et du variogramme**, pas des valeurs mesurées. (3) Le système est linéaire de taille $(n+1)$ : un seul appel à `numpy.linalg.solve`.

**Un exemple à la main.** Prenons le cas le plus simple : une dimension, un variogramme **linéaire** $\gamma(h)=h$, deux points de mesure à $x=0$ (valeur 10) et $x=3$ (valeur 16), et une cible à $x=1$. Alors $\Gamma=\begin{pmatrix}0&3\\3&0\end{pmatrix}$ et $\gamma_0=(1,2)^\top$. Le système s'écrit $3\lambda_2+m=1$, $3\lambda_1+m=2$, $\lambda_1+\lambda_2=1$. En soustrayant les deux premières équations, $3(\lambda_1-\lambda_2)=1$, donc $\lambda_1=\tfrac23$, $\lambda_2=\tfrac13$ et $m=0$. La prédiction vaut $\tfrac23\times10+\tfrac13\times16=12$ et la variance $\lambda^\top\gamma_0+m=\tfrac23+\tfrac23+0=\tfrac43$. Ce résultat porte un enseignement : **dans ce cas particulier, le krigeage est l'interpolation linéaire** (de 10 à 16 en trois km, soit 12 à 1 km). Vérifions avec une fonction générale.

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

Nous retrouvons les poids $\frac23,\frac13$, la prédiction 12 et la variance $\frac43$ du calcul à la main. Revenons aux livraisons, avec le modèle **exponentiel** ajusté. Prédisons d'abord en un point précis, par exemple l'adresse $(40,\,60)$, et examinons les poids.

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

Les poids les plus forts reviennent aux livraisons **les plus proches** de la cible (le plus grand, 0,53, est pour celle qui est à 2,7 km), leur somme vaut 1, et 29 des 200 poids sont **négatifs** (mais très petits, comme l'indique le plus petit d'entre eux) : ce n'est pas une anomalie. Quand un point en cache d'autres derrière lui (*effet d'écran*), le krigeage peut donner un poids légèrement négatif au point masqué. Une moyenne ordinaire ne le ferait jamais.

> 💡 **Le krigeage est un interpolateur exact.** Si la cible est l'un des points de mesure, le système donne le poids 1 à ce point et 0 aux autres : la prédiction redonne la mesure et la variance est nulle. C'est vrai ici même avec une pépite, parce que nous la traitons comme une propriété de la mesure (le point mesuré est connu). Si au contraire la pépite représente un bruit que l'on veut *filtrer*, on utilise une variante qui lisse au lieu d'interpoler (non traitée ici).

### 9.3.5 Une carte de prédiction et une carte d'incertitude

Prédisons maintenant en chacun des 625 points d'une grille régulière (le jeu `verite` contient aussi le **vrai** champ en ces points, grâce à la simulation) et comparons à trois alternatives : la **moyenne globale**, la méthode de l'**inverse de la distance au carré** (IDW, une moyenne pondérée sans variogramme) et le krigeage.

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

Dessinons le vrai champ, la prédiction par krigeage et l'écart-type de krigeage.

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

![De gauche à droite : le vrai champ de délais (connu car simulé), la prédiction par krigeage ordinaire à partir des 200 mesures, et l'écart-type d'erreur de krigeage (les points noirs sont les 200 livraisons mesurées). L'incertitude est faible près des mesures et monte dans les zones qui en sont éloignées.](figures/ch09-krigeage.png)

Contre le vrai champ, le krigeage obtient une erreur quadratique de 0,645 jour, contre 0,916 pour la moyenne globale (30 % de moins) et 0,671 pour l'inverse de la distance : l'IDW fait presque aussi bien (4 % d'écart), ce qui rappelle qu'une moyenne pondérée bien choisie est déjà un bon prédicteur. L'avantage décisif du krigeage n'est pas là, mais dans la carte de droite. La carte du centre reproduit les grandes structures du vrai champ, en plus lisse (le krigeage est une moyenne : il **lisse** et sous-estime donc les extrêmes). La carte de droite est une originalité du krigeage : elle dit **où la prédiction est fiable**, avant même d'avoir livré. Dans la pratique, c'est la carte qui guide le choix des **prochains points de mesure** : on va mesurer là où l'incertitude est la plus grande.

De quoi dépend cette incertitude ? Mesurons-le : pour chaque point de la grille, la distance au point de mesure le plus proche, et la façon dont l'écart-type de krigeage évolue avec elle, puis une comparaison entre les points proches d'un bord du domaine et les autres.

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

L'écart-type de krigeage est presque une fonction croissante de la distance à la mesure la plus proche (corrélation de 0,92) : de 0,59 jour à moins de 2 km d'une mesure à 0,97 jour entre 6 et 10 km. Aucun **effet de bord** n'apparaît ici (0,78 jour près des bords contre 0,77 à l'intérieur) : avec 200 points répartis uniformément sur le carré, les bords sont aussi bien couverts que le centre. Il se manifesterait avec un échantillonnage plus clairsemé ou concentré au centre, où les points du bord n'auraient de voisins que d'un seul côté.



### 9.3.6 Évaluer honnêtement : la validation croisée

Comparer au vrai champ n'est possible que sur données simulées. Dans une vraie étude, on évalue par **validation croisée** : on retire une partie des mesures, on les prédit avec le reste, et on compare. Notre fichier contient une colonne `pli` (cinq plis de 40 points). Pour être honnête, il faut **réajuster le variogramme à chaque pli, uniquement sur les données d'entraînement** : sinon, le variogramme aurait « vu » les points à prédire.

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

Trois lectures. **(1)** Les trois méthodes sont comparées sur **les mêmes** 200 prédictions : le krigeage a la plus petite erreur (0,969 jour), devant l'IDW (0,994), elle-même meilleure que la moyenne globale (1,097). L'avantage du krigeage sur l'IDW est mince (2,5 %) : sur ce jeu, la qualité de la prédiction ponctuelle ne départage pas nettement les deux. **(2)** Le krigeage fournit en plus un **écart-type d'erreur** : on le contrôle avec les résidus *standardisés* $(z-\hat z)/\sigma_K$, qui devraient avoir une moyenne proche de 0 et une variance proche de 1 si les barres d'erreur sont bien calibrées, et avec la **couverture** des intervalles $\hat z\pm1{,}96\,\sigma_K$. La moyenne des résidus standardisés est bien proche de 0 (−0,02), mais leur **variance est de 1,71** et la couverture n'est que de 89,5 % au lieu de 95 %. **(3)** Les barres d'erreur sont donc **trop optimistes** : trop étroites d'un facteur $\sqrt{1{,}71}\approx1{,}3$. La cause est celle que nous avons vue à l'ajustement : un variogramme estimé avec une pépite trop faible (0,04 au lieu de 0,4) annonce une prédiction plus précise qu'elle ne l'est. Le krigeage donne de **bonnes prédictions** même avec un variogramme approximatif, mais ses **barres d'erreur**, elles, héritent de toute l'incertitude du variogramme.

> 💡 **Remarque sur la mesure d'erreur.** Notre cible, dans cette validation, est la **mesure bruitée** $Z$ (ce que l'on observerait), qui contient la pépite. Une partie de l'erreur est donc irréductible, quelle que soit la qualité du modèle : même un krigeage parfait ne peut pas prédire le bruit de mesure. C'est pour cela que le RMSE de la validation croisée est supérieur à celui calculé plus haut contre le champ sans bruit.

**Une alternative sans variogramme : un lissage par spline.** On peut aussi prédire le délai comme une fonction lisse $f(x,y)$ des coordonnées, par une **spline de plaque mince**, comme le fait `mgcv` en R (le modèle additif généralisé de la section 2.5 de ce volume). Voici le même protocole de validation croisée, avec les mêmes plis :

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

La spline obtient une erreur de 0,974 jour, quasiment identique à celle du krigeage (0,969), ce qui n'a rien de surprenant : les deux sont des **lisseurs linéaires** du même type, et le krigeage avec variogramme exponentiel a une interprétation proche. Les avantages propres du krigeage sont (1) un **modèle explicite de la dépendance** (pépite, portée, que l'on peut interpréter), (2) des **variances de prédiction** natives (la spline en fournit aussi, par ses erreurs-types, avec d'autres hypothèses).

### 9.3.7 Les limites : tendance, anisotropie, extrapolation

**Si la moyenne n'est pas constante.** Le variogramme présuppose un processus stationnaire. Si la moyenne varie dans l'espace (une **tendance** : par exemple, les délais augmentent avec l'éloignement du dépôt), le variogramme empirique **monte sans jamais se stabiliser**, parce que les paires éloignées diffèrent aussi par leur niveau moyen. Illustrons-le en ajoutant aux délais une tendance linéaire de $0{,}04$ jour par km vers l'est, puis en l'ôtant par régression avant de calculer le variogramme.

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

**Si le phénomène dépend de la direction** (*anisotropie*) : un délai peut varier plus vite le long d'un axe routier que perpendiculairement. On le détecte en calculant des variogrammes **directionnels** (en ne gardant que les paires orientées dans une direction, à une tolérance d'angle près). S'ils diffèrent, un variogramme unique est inadapté.

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

![À gauche : variogramme des délais sans tendance (vert), avec une tendance linéaire ajoutée (rouge, qui ne se stabilise pas), et après retrait de la tendance par régression (bleu). À droite : variogrammes directionnels est-ouest et nord-sud, comparés au variogramme toutes directions confondues.](figures/ch09-limites-variogramme.png)

À gauche, la tendance non retirée fait monter le variogramme bien au-delà du palier (de 0,84 à 3,29 entre 8 et 67 km), alors que le retrait de la tendance par régression redonne une courbe presque identique à celle sans tendance. La régression retrouve d'ailleurs la tendance ajoutée : une pente de 0,042 jour par km vers l'est pour 0,04 en vérité, et une pente nulle (−0,003) vers le nord. À droite, les deux directions **ne sont pas superposées** : la courbe nord-sud est au-dessus de la courbe est-ouest à toutes les distances. Faut-il y voir de l'**anisotropie** ? Avec des données réelles, on ne peut pas le savoir d'emblée : des variogrammes directionnels sont calculés sur des secteurs d'angle étroits, donc sur **moins de paires**, et sont bruités. La bonne démarche est de **calibrer** ce que le hasard seul produit. Résumons l'écart par un rapport moyen $\gamma_{\text{N-S}}/\gamma_{\text{E-O}}$ sur les classes de distance, puis calculons le même rapport sur 60 jeux simulés **isotropes** (le même processus, 60 autres graines).

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

Le rapport observé (1,24) est dans la queue haute de ce que le hasard produit sous isotropie (médiane 1,02 ; 80 % des jeux entre 0,91 et 1,17) : environ 5 % des jeux isotropes l'atteignent ou le dépassent. C'est donc un cas **limite** : trop marqué pour être banal, pas assez pour conclure. Nous *savons* ici, par construction, que le champ est isotrope : l'écart observé est un accident de ce tirage. Avec des données réelles, on aurait hésité, et la réponse prudente serait de comparer des modèles avec et sans anisotropie (par exemple par validation croisée) plutôt que de se fier à un graphique.

> ⚠️ **Quatre mises en garde.**
> 1. **Stationnarité.** Avec une tendance, il faut la modéliser (krigeage universel : tendance par régression et résidu krigé) ou la retirer. Retirer une tendance par régression ordinaire peut sous-estimer légèrement la semi-variance aux grandes distances (ici, la courbe des résidus est presque confondue avec celle du processus sans tendance).
> 2. **Anisotropie.** Vérifiez-la sur des variogrammes directionnels avant de supposer qu'une seule portée convient.
> 3. **Extrapolation.** Le krigeage est un **interpolateur** : loin de toute mesure, ou hors de l'enveloppe des points mesurés, la prédiction revient vers la moyenne et la variance monte vers le palier (nous venons de voir l'écart-type croître avec la distance à la mesure la plus proche). Ne promettez pas un délai dans une zone qu'aucune mesure n'entoure.
> 4. **Variogramme estimé, non connu.** La variance de krigeage suppose le variogramme **connu**. Comme nous l'avons vu à l'expérience des 30 graines, il est en réalité estimé avec une grande incertitude : l'écart-type de krigeage est donc plutôt optimiste, ce que la validation croisée du 9.3.6 a confirmé (variance des résidus standardisés de 1,71 au lieu de 1).

> ✅ **À retenir.**
> - Le **semi-variogramme** $\gamma(h)=\frac12\mathbb E[(Z(s+h)-Z(s))^2]$ décrit comment la ressemblance s'estompe avec la distance ; pour un processus de variance finie, $\gamma(h)=C(0)-C(h)$. Ses paramètres : **pépite** (bruit et micro-variations), **palier** (variance totale), **portée** (distance de décorrélation).
> - On estime $\gamma$ par classes de distance (**variogramme empirique**, avec le nombre de paires), puis on **ajuste un modèle valide** (sphérique, exponentiel, gaussien) par moindres carrés pondérés. Pépite et portée sont peu précises, même avec 200 points.
> - Le **krigeage ordinaire** est le meilleur prédicteur linéaire sans biais : on résout $\begin{pmatrix}\Gamma&\mathbf 1\\\mathbf 1^\top&0\end{pmatrix}\binom{\lambda}{m}=\binom{\gamma_0}{1}$, la prédiction est $\lambda^\top z$ et la variance $\lambda^\top\gamma_0+m$.
> - On le **valide** par validation croisée *avec réajustement du variogramme à chaque pli*, et on contrôle les barres d'erreur par les résidus standardisés et la couverture.
> - Limites : **stationnarité** (tendance), **anisotropie**, **extrapolation**, et un variogramme qui est une estimation, pas une vérité.
