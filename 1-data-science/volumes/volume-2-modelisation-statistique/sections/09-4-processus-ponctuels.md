## 9.4 Processus ponctuels

> 💡 **Intuition.** Jusqu'ici, les lieux étaient donnés (les 144 zones, les adresses de livraison choisies par les clients) et c'était la **valeur** qui était aléatoire. Maintenant, ce sont les **positions** elles-mêmes qui sont le phénomène : où habitent les clients de la boutique ? Sont-ils éparpillés au hasard, **regroupés** en quartiers (une publicité, un bouche-à-oreille) ou étonnamment **bien espacés** (chacun choisit une adresse à distance des autres) ? Pour répondre, on compare ce que l'on observe à ce que produirait le **hasard complet**.

### 9.4.1 Le hasard complet : le processus de Poisson spatial

Pour reconnaître un écart au hasard, il faut d'abord définir le hasard. Un semis de points est de **hasard spatial complet** (en anglais *complete spatial randomness*, CSR) quand il est un **processus de Poisson homogène** d'intensité $\lambda$ (nombre moyen de points par km²) :

1. le nombre de points dans une région $B$ suit une loi de Poisson de moyenne $\lambda\,|B|$, où $|B|$ est l'aire de la région ;
2. les nombres de points dans des régions **disjointes** sont indépendants ;
3. conditionnellement au nombre total de points $n$ dans la fenêtre, les points sont **indépendants et uniformes** sur la fenêtre.

La propriété 3 est la plus utile en pratique : fabriquer un semis aléatoire sur une fenêtre, c'est tirer $n$ points uniformes. Le CSR est notre **hypothèse nulle** : aucune attraction, aucune répulsion entre points, et la même densité partout. Les deux écarts typiques sont l'**agrégat** (points groupés en paquets) et la **régularité** (points qui se repoussent, avec une distance minimale entre eux).

Fabriquons trois semis de la même fenêtre de $10\times10$ km (100 km²) autour de la boutique, de 75 à 100 adresses de clients chacun (le nombre de points de l'agrégé est lui-même aléatoire) :

- un semis **aléatoire** (CSR) de 100 points uniformes ;
- un semis **agrégé**, par un processus de **Thomas** : des « centres » (des quartiers, des abonnés d'un même influenceur) tombent au hasard, puis chaque centre engendre un nombre de clients de loi de Poisson, répartis autour de lui selon une loi normale ;
- un semis **régulier**, par **inhibition séquentielle** : on tire des points uniformes l'un après l'autre en refusant ceux qui tomberaient à moins de $0{,}7$ km d'un point déjà accepté.

```python hide
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

COTE = 10.0                                  # fenêtre carrée de 10 km de côté
AIRE = COTE ** 2                             # 100 km²

def distances(P, Q=None):
    Q = P if Q is None else Q
    return np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(axis=2))

def semis_poisson(n, rng):
    """CSR conditionnel à n : n points indépendants et uniformes."""
    return rng.uniform(0, COTE, size=(n, 2))

def semis_inhibition(n, rmin, rng):
    """Inhibition séquentielle simple : points uniformes refusés s'ils sont à moins de rmin d'un point accepté."""
    pts = []
    while len(pts) < n:
        p = rng.uniform(0, COTE, size=2)
        if not pts or (np.hypot(*(np.array(pts) - p).T) >= rmin).all():
            pts.append(p)
    return np.array(pts)
```

Le générateur du processus de Thomas montre bien le mécanisme d'agrégation ; les deux autres, plus simples, sont reconstruits dans le cahier (application 9.6).

```python
def semis_thomas(kappa, mu, sigma, rng):
    """Agrégat de Thomas : centres de Poisson (densité kappa), mu descendants en moyenne, étalement sigma."""
    marge = 3 * sigma                                            # on génère aussi des centres hors fenêtre
    n_centres = rng.poisson(kappa * (COTE + 2 * marge) ** 2)
    centres = rng.uniform(-marge, COTE + marge, size=(n_centres, 2))
    nb = rng.poisson(mu, size=n_centres)
    pts = np.repeat(centres, nb, axis=0) + rng.normal(0, sigma, size=(nb.sum(), 2))
    return pts[((pts >= 0) & (pts <= COTE)).all(axis=1)]         # on ne garde que ce qui tombe dans la fenêtre
```

On tire alors les trois semis (graine fixe) et on les dessine :

```python hide-code
rng = np.random.default_rng(2025)
semis = {
    "aléatoire (CSR)": semis_poisson(100, rng),
    "agrégé (Thomas)": semis_thomas(kappa=0.08, mu=12, sigma=0.4, rng=rng),
    "régulier (inhibition)": semis_inhibition(100, 0.7, rng),
}
for nom, pts in semis.items():
    print(f"{nom:24s} n = {len(pts):3d} points  (intensité estimée {len(pts) / AIRE:.2f} par km²)")

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
aléatoire (CSR)          n = 100 points  (intensité estimée 1.00 par km²)
agrégé (Thomas)          n =  75 points  (intensité estimée 0.75 par km²)
régulier (inhibition)    n = 100 points  (intensité estimée 1.00 par km²)
figure enregistrée
```

![Trois semis de points dans une fenêtre de 10 km × 10 km : hasard complet (gauche), agrégat de Thomas (centre), régulier par inhibition (droite).](figures/ch09-semis.png)

Les différences se voient à l'œil : des paquets et des vides au centre, un espacement très uniforme à droite, et au hasard complet à gauche un mélange de petits groupes et de vides qui surprend : **le hasard n'est pas régulier**. C'est un piège classique : nous avons tendance à voir de l'agrégation dans un semis tout à fait aléatoire, parce que des points qui tombent par hasard près les uns des autres nous sautent aux yeux. D'où le besoin de tests.

### 9.4.2 Le test des quadrats

La méthode la plus simple : quadriller la fenêtre en $m$ cases égales et **compter** les points dans chaque case. Sous le CSR, conditionnellement au nombre $n$ de points, les comptages suivent une loi multinomiale de probabilités égales : chaque case a la même moyenne $\bar c=n/m$, et l'on s'attend à une variance voisine de la moyenne (propriété de la loi de Poisson). On forme la statistique de Pearson

$$\chi^2=\sum_{k=1}^m\frac{(c_k-\bar c)^2}{\bar c},\qquad\text{approximativement }\chi^2_{m-1}\text{ sous le CSR}$$

(une approximation raisonnable quand $\bar c\ge5$ environ). Rappelons qu'elle vaut $(m-1)$ fois l'**indice de dispersion** $\text{VMR}=s^2/\bar c$ (variance divisée par moyenne). Une valeur **grande** de $\chi^2$ indique de l'**agrégation** (certaines cases beaucoup plus peuplées que d'autres), une valeur **petite** de la **régularité** (comptages trop uniformes).

> 💡 **Un exemple à la main.** Quatre cases contenant 1, 1, 1 et 9 points : $\bar c=3$, donc $\chi^2=\frac{(-2)^2+(-2)^2+(-2)^2+6^2}{3}=\frac{12+36}{3}=16$ avec 3 degrés de liberté : bien au-delà de ce que le hasard produit (la valeur critique à 5 % est 7,81). Quatre cases à 3 points chacune : $\chi^2=0$, une régularité parfaite. La statistique mesure donc l'inégalité des comptages.

```python hide-code
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

Le test distingue bien les trois cas : le semis **agrégé** a une statistique très élevée (VMR bien supérieur à 1, p-valeur d'agrégation minuscule), le semis **régulier** une statistique très faible (VMR très inférieur à 1, p-valeur de régularité minuscule) et le semis **aléatoire** une valeur banale.

> ⚠️ **Les limites du test des quadrats.** (1) Le résultat dépend de la **taille des cases** : un agrégat de 1 km de diamètre passe inaperçu avec des cases de 5 km. Le test est un test **à une échelle**. (2) Il ne retient que les comptages et jette l'information de **position** à l'intérieur de chaque case. (3) La loi du $\chi^2$ n'est qu'une approximation quand les comptages sont petits. Les méthodes à base de **distances**, qui suivent, n'ont pas ces défauts.

### 9.4.3 Le plus proche voisin : l'indice de Clark-Evans

Pour chaque point, notons $d_i$ la distance à son **plus proche voisin**. Sous le CSR d'intensité $\lambda$, la probabilité que le plus proche voisin d'un point soit **au-delà** de la distance $r$ est celle de ne trouver **aucun** point dans un disque d'aire $\pi r^2$, soit (loi de Poisson de moyenne $\lambda\pi r^2$, valeur en 0) :

$$\mathbb P(d>r)=e^{-\lambda\pi r^2}\quad\Longrightarrow\quad G(r)=\mathbb P(d\le r)=1-e^{-\lambda\pi r^2}.$$

On en déduit la distance moyenne au plus proche voisin, $\mathbb E[d]=\int_0^\infty e^{-\lambda\pi r^2}\,dr=\dfrac{1}{2\sqrt\lambda}$, et sa variance, $\operatorname{Var}(d)=\dfrac{4-\pi}{4\pi\lambda}$. L'**indice de Clark-Evans** compare la distance moyenne observée à celle du hasard :

$$R=\frac{\bar d_{\text{obs}}}{1/(2\sqrt{\hat\lambda})},\qquad \hat\lambda=\frac nA,$$

avec $R=1$ pour le hasard, $R<1$ pour de l'agrégation (les voisins sont plus proches que prévu), $R>1$ pour de la régularité. Comme $\bar d$ est une moyenne de $n$ distances (supposées à peu près indépendantes), on obtient un test $z=(\bar d-\mathbb E[d])/\sqrt{\operatorname{Var}(d)/n}$ approximativement normal.

> ⚠️ **L'effet de bord.** Cette formule suppose un plan infini. Dans une **fenêtre finie**, un point près du bord a moins de voisins possibles (il n'y a rien au-delà), donc son plus proche voisin est en moyenne plus loin : $\bar d$ est **surestimé** et $R$ est biaisé vers le haut, ce qui peut faire conclure à tort à une régularité. Donnelly (1978) a proposé une correction pour une fenêtre de périmètre $P$ : $\mathbb E[\bar d]=0{,}5\sqrt{A/n}+(0{,}0514+0{,}041/\sqrt n)\,P/n$ et $\operatorname{Var}(\bar d)=0{,}070\,A/n^2+0{,}037\,P\sqrt{A/n^5}$. Au lieu de la croire sur parole, **vérifions-la par simulation** : nous simulons 4 000 semis CSR de 100 points dans notre fenêtre et nous comparons la moyenne et l'écart-type de $\bar d$ aux deux formules.

```python hide-code
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

La formule naïve sous-estime la moyenne (0,500 contre 0,523 simulé : près de 5 % d'écart) et l'écart-type ; celle de Donnelly colle à la simulation. Appliquons l'indice de Clark-Evans aux trois semis avec les deux versions, et ajoutons une troisième voie, qui évite toute formule : une **p-valeur de Monte-Carlo**. On simule $B=999$ semis CSR de même taille dans la **même fenêtre** et l'on regarde où tombe notre $\bar d$ : l'effet de bord est automatiquement pris en compte, puisque les semis simulés le subissent aussi.

```python hide-code
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

Les trois voies s'accordent pour le semis agrégé (R très inférieur à 1) et pour le semis régulier (R supérieur à 1). Pour le semis aléatoire, le R naïf vaut un peu plus de 1 et pourrait faire croire à une légère régularité : c'est le biais de bord. Avec la correction de Donnelly, il est ramené près de 1.

**La fonction $G$ entière.** L'indice de Clark-Evans résume toutes les distances par leur moyenne. On peut regarder la **fonction de répartition empirique** de $d_i$, $\hat G(r)=\frac1n\#\{i:d_i\le r\}$, et la comparer à la courbe théorique $1-e^{-\lambda\pi r^2}$, avec une **enveloppe de Monte-Carlo** : un bandeau qui contient 95 % des courbes obtenues sur des semis CSR simulés. Si notre courbe sort du bandeau, le hasard complet est mis en défaut. Une courbe $\hat G$ qui **monte plus vite** que le hasard indique des voisins plus proches que prévu (agrégat) ; une courbe qui monte **plus lentement** indique de la répulsion.

```python hide-code
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

![Fonction G (part des points dont le plus proche voisin est à moins de r) pour les trois semis, avec l'enveloppe de Monte-Carlo (bandeau gris, 499 semis CSR de même taille) et la courbe théorique du plan infini (pointillés).](figures/ch09-fonction-G.png)

Le semis aléatoire reste dans le bandeau ; l'agrégé monte beaucoup plus vite (ses voisins sont proches) ; le régulier est **nul** jusqu'à la distance d'inhibition (0,7 km) puis monte brusquement. Remarquons que le bandeau est un peu décalé par rapport à la courbe théorique : il intègre l'effet de bord. C'est lui, et non la courbe en pointillés, qu'il faut regarder.

### 9.4.4 La fonction $K$ de Ripley

La fonction $G$ ne regarde que le **premier** voisin, donc l'échelle la plus petite. Pour étudier plusieurs échelles à la fois, Ripley a proposé la fonction $K$ : $K(r)$ est le **nombre moyen de points supplémentaires** que l'on trouve à moins de la distance $r$ d'un point typique, **divisé par l'intensité** $\lambda$ :

$$K(r)=\frac1\lambda\;\mathbb E\big[\#\{\text{autres points à distance}\le r\text{ d'un point typique}\}\big].$$

Sous le CSR, les autres points sont distribués comme un processus de Poisson indépendamment du point typique (propriété de Slivnyak) : le nombre moyen d'autres points dans un disque d'aire $\pi r^2$ vaut $\lambda\pi r^2$, donc

$$K_{\text{CSR}}(r)=\pi r^2.$$

Pour un agrégat, un point typique a **plus** de voisins que prévu à toutes les petites distances : $K(r)>\pi r^2$. Pour un semis régulier, il en a **moins** : $K(r)<\pi r^2$. On préfère tracer la version « stabilisée » $\;L(r)-r=\sqrt{K(r)/\pi}-r$, qui vaut 0 sous le CSR et dont la variance est à peu près constante en $r$. L'estimateur naïf est $\hat K(r)=\dfrac{A}{n(n-1)}\sum_{i\ne j}\mathbf 1\{d_{ij}\le r\}$.

> 💡 **Un exemple à la main.** Quatre adresses dans la fenêtre unité ($A=1$) : $(0{,}1;0{,}1)$, $(0{,}2;0{,}1)$, $(0{,}8;0{,}8)$, $(0{,}85;0{,}9)$. Les deux premières sont à $0{,}1$ l'une de l'autre, les deux dernières à $\sqrt{0{,}05^2+0{,}1^2}\approx0{,}112$, les autres paires à plus de $1$. Pour $r=0{,}2$, il y a 2 paires proches, donc 4 couples ordonnés $(i,j)$ avec $i\ne j$ : $\hat K(0{,}2)=\frac{1}{4\times3}\times4=0{,}333$, alors que $\pi r^2=0{,}126$ : le semis est nettement agrégé à cette échelle.

> ⚠️ **L'effet de bord, encore.** Un point proche du bord a une partie de son disque hors de la fenêtre : on y voit mécaniquement moins de voisins, et l'estimateur naïf **sous-estime** $K$ aux grandes distances. La correction la plus simple est la **méthode du bord** (*reduced-sample*) : pour une distance $r$, on ne compte que les points situés à plus de $r$ du bord (leurs disques sont entiers dans la fenêtre), soit $n_r$ points :
> $$\hat K(r)=\frac{A}{(n-1)\,n_r}\sum_{i:\,b_i\ge r}\#\{j\ne i:\ d_{ij}\le r\},$$
> où $b_i$ est la distance de $i$ au bord. Elle est sans biais, au prix d'une perte de données quand $r$ grandit : on limite donc $r$ au quart du côté de la fenêtre environ.

```python hide-code
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

Sans correction, l'estimateur sous-estime nettement $K$ à 2 km : 10,4 en moyenne au lieu de $\pi r^2=12{,}6$, soit 17 % de trop peu. Avec la méthode du bord, on obtient 12,3 : un écart de 2 %, très inférieur. Passons à l'application : on compare la courbe $\hat L(r)-r$ de chaque semis à une enveloppe obtenue sur 499 semis CSR de même taille. Pour un **test global** (et non « point par point »), on utilise la statistique $T=\max_r|\hat L(r)-r|$, comparée à sa distribution sous CSR.

```python hide-code
def L_centre(pts, rs):
    return np.sqrt(ripley_K(pts, rs) / np.pi) - rs

rng = np.random.default_rng(21)
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.9), sharey=True)
lignes = []
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

![Fonction L(r) − r de Ripley pour les trois semis, avec l'enveloppe de Monte-Carlo (bandeau gris) obtenue sur 499 semis aléatoires de même taille. Au-dessus de 0 : agrégat ; en dessous : régularité.](figures/ch09-ripley.png)

La lecture est la suivante. Le semis **aléatoire** reste dans le bandeau à toutes les distances et sa p-valeur globale est banale. Le semis **agrégé** est très au-dessus du bandeau sur toute la plage, avec une forme caractéristique : l'écart se creuse jusqu'à un **maximum vers 1 km**, une échelle de quelques fois l'étalement $\sigma=0{,}4$ km des paquets, puis décroît quand le disque de rayon $r$ commence à englober plusieurs paquets, dont les voisins ne sont plus « en excès ». Le semis **régulier** est sous le bandeau aux petites distances, avec un **minimum exactement à la distance d'inhibition** (0,7 km). Ce n'est pas un hasard : tant que $r<0{,}7$ km, aucune paire de points n'est à moins de $r$, donc $\hat K(r)=0$ et $L(r)-r=-r$ (la droite descendante de la figure) ; au-delà de 0,7 km, les voisins apparaissent et la courbe remonte vers le bandeau.

> ⚠️ **Enveloppe point par point ≠ test global.** Un bandeau à 95 % *en chaque $r$* est dépassé quelque part avec une probabilité bien supérieure à 5 % si l'on regarde de nombreuses distances (c'est le même problème que les tests multiples). Pour **conclure**, utilisez la p-valeur **globale** de la statistique $T$ ; le bandeau sert à **voir** à quelles échelles l'écart se produit.

### 9.4.5 Attention : agrégat ou densité variable ?

Tout ce qui précède suppose que l'**intensité est homogène**. C'est le piège principal des processus ponctuels. Imaginez que les clients habitent plutôt près de la boutique, au centre de la fenêtre, parce que la densité d'habitation y est plus forte. Même si chacun a choisi son adresse **sans tenir compte des autres** (aucune interaction), le semis paraîtra agrégé : beaucoup de points au centre, peu en périphérie. La fonction $K$ ne distingue pas un **agrégat** (les points s'attirent) d'une **intensité qui varie** (les points s'accumulent là où la densité est forte).

```python hide-code
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

![À gauche : 100 adresses indépendantes les unes des autres, mais avec une densité qui décroît du centre vers les bords. À droite : la fonction L(r) − r sort de l'enveloppe du hasard complet, alors qu'il n'y a aucune interaction entre les points.](figures/ch09-inhomogene.png)

Le test rejette le hasard complet alors qu'**aucun point n'attire les autres**. L'agrégat apparent est entièrement dû à la variation de la densité. Le remède est de comparer non pas à un CSR homogène mais à un **processus de Poisson inhomogène** d'intensité estimée $\hat\lambda(s)$ (par un lissage à noyau, par exemple), et d'utiliser la fonction **$K$ inhomogène** de Baddeley, Møller et Waagepetersen. Elle ne figure pas dans ce chapitre (nous ne l'avons pas implémentée) ; retenez le principe : **on ne peut parler d'agrégation entre les points qu'après avoir tenu compte de la densité qui varie**. Cette distinction entre *effet du premier ordre* (l'intensité) et *effet du second ordre* (l'interaction) est le cœur de la modélisation des semis de points.

> 💡 **Retour à la question de la gérante.** Pour savoir si ses clients du quartier sont **vraiment** regroupés autour de la boutique, elle ne peut pas se contenter d'un test de $K$ : elle doit d'abord se demander si la densité de population varie, c'est-à-dire si les habitants eux-mêmes sont plus nombreux près de la boutique. Un semis de clients qui reproduit simplement la répartition de la **population** ne dit rien sur son comportement. La comparaison utile est avec les habitants **non clients** (un semis de « contrôle ») ou avec une carte de densité de population.

> ✅ **À retenir.**
> - Un **semis de points** est un phénomène dont les **positions** sont aléatoires. La référence est le **hasard spatial complet** : un processus de Poisson homogène (comptages de Poisson, indépendance entre régions disjointes, points uniformes conditionnellement à leur nombre).
> - **Quadrats** : $\chi^2=\sum(c_k-\bar c)^2/\bar c$ (approximativement $\chi^2_{m-1}$) ; simple, mais dépend de la taille des cases.
> - **Plus proche voisin** : $G(r)=1-e^{-\lambda\pi r^2}$ sous le CSR, $\mathbb E[d]=1/(2\sqrt\lambda)$ ; indice de Clark-Evans $R<1$ pour un agrégat, $R>1$ pour de la régularité. Une fenêtre finie biaise $R$ (**effet de bord**) : corrigez (Donnelly) ou, mieux, utilisez une **p-valeur de Monte-Carlo** dans la même fenêtre.
> - **Fonction $K$ de Ripley** : $K_{\text{CSR}}(r)=\pi r^2$ ; $L(r)-r$ au-dessus de 0 pour l'agrégat, en dessous pour la régularité ; **correction de bord** indispensable ; utilisez un test **global** et non un bandeau point par point.
> - **Une intensité variable imite un agrégat** : avant de conclure à une interaction, tenez compte de la densité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.6 et 9.7, exercices 9.10 et 9.12.
