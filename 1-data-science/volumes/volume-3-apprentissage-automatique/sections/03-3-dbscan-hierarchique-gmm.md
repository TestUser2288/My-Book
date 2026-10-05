## 3.3 ➕ Pour aller plus loin : DBSCAN, classification hiérarchique, mélanges gaussiens

> 🧭 **Section optionnelle.** Elle prolonge 3.1 avec trois méthodes qui lèvent chacune une hypothèse de k-means : que les groupes soient des **boules** (DBSCAN et les liens hiérarchiques), qu'ils soient **bien tranchés** (les mélanges gaussiens donnent des appartenances « floues »). On peut la sauter sans perdre le fil du chapitre.

k-means suppose, sans le dire, que chaque groupe est une région **convexe** et à peu près **sphérique** autour de son centre : il découpe l'espace en cellules de Voronoï. Quand les groupes ont une forme allongée, courbe ou imbriquée, cette hypothèse trahit les données. Le cas d'école est celui des **deux lunes** : deux croissants entrelacés. Un humain y voit tout de suite deux groupes ; k-means, qui doit couper l'espace par une droite, les mélange.

### 3.3.1 DBSCAN : les groupes comme régions denses

**DBSCAN** (Ester et coll., 1996) définit un groupe comme une **région dense** séparée d'autres régions denses par des zones vides. Il n'a pas besoin de connaître le nombre de groupes, accepte des formes quelconques, et surtout il a une réponse naturelle pour les points qui n'appartiennent à aucun groupe : ce sont du **bruit**.

Deux paramètres seulement : un rayon $\varepsilon$ et un effectif minimal $m$ (`min_samples`). Pour un point $\mathbf x$, son **voisinage** est l'ensemble des points à distance au plus $\varepsilon$ de lui (lui-même compris). Les points se classent alors en trois types :

- un point **cœur** a au moins $m$ points dans son voisinage ;
- un point **de bordure** n'est pas un cœur, mais se trouve dans le voisinage d'un cœur ;
- un point **de bruit** n'est ni l'un ni l'autre.

Un groupe est l'ensemble des points obtenus en partant d'un cœur et en **suivant de proche en proche les cœurs voisins** (deux cœurs sont connectés s'ils sont à distance $\le\varepsilon$), auxquels on ajoute leurs points de bordure.

**Un exemple à la main, en dimension 1.** Neuf valeurs : $1;\ 1{,}2;\ 1{,}4;\ 1{,}85;\ 2{,}5;\ 5;\ 5{,}1;\ 5{,}3;\ 9$, avec $\varepsilon=0{,}5$ et $m=3$.

- Le voisinage de $1$ est $\{1;\ 1{,}2;\ 1{,}4\}$ : trois points, c'est un **cœur**. De même pour $1{,}2$ (voisinage $\{1;\ 1{,}2;\ 1{,}4\}$) et pour $1{,}4$ (voisinage $\{1;\ 1{,}2;\ 1{,}4;\ 1{,}85\}$).
- Le point $1{,}85$ n'a que deux points dans son voisinage ($1{,}4$ et lui-même) : ce n'est pas un cœur ; mais il est à $0{,}45$ du cœur $1{,}4$, c'est un point **de bordure** : il rejoint le premier groupe.
- Le point $2{,}5$ est à $0{,}65$ du point le plus proche : ni cœur, ni voisin d'un cœur, c'est du **bruit**.
- $5$, $5{,}1$ et $5{,}3$ forment un second groupe, chacun étant un cœur. Enfin $9$ est du bruit.

```python hide
from sklearn.cluster import DBSCAN, AgglomerativeClustering
x1 = np.array([1, 1.2, 1.4, 1.85, 2.5, 5, 5.1, 5.3, 9]).reshape(-1, 1)
db = DBSCAN(eps=0.5, min_samples=3).fit(x1)
type_pt = ["cœur" if i in db.core_sample_indices_ else ("bruit" if db.labels_[i] == -1 else "bordure") for i in range(len(x1))]
print(pd.DataFrame({"valeur": x1.ravel(), "type": type_pt, "groupe": db.labels_}).to_string(index=False))
```
<!--sortie-->
```text
 valeur    type  groupe
   1.00    cœur       0
   1.20    cœur       0
   1.40    cœur       0
   1.85 bordure       0
   2.50   bruit      -1
   5.00    cœur       1
   5.10    cœur       1
   5.30    cœur       1
   9.00   bruit      -1
```

```python hide-code
print(pd.DataFrame({"valeur": x1.ravel(), "type": type_pt, "groupe": db.labels_}).to_string(index=False))
```
<!--sortie-->
```text
 valeur    type  groupe
   1.00    cœur       0
   1.20    cœur       0
   1.40    cœur       0
   1.85 bordure       0
   2.50   bruit      -1
   5.00    cœur       1
   5.10    cœur       1
   5.30    cœur       1
   9.00   bruit      -1
```

Le tableau de la bibliothèque confirme le raisonnement : deux groupes (étiquettes $0$ et $1$), six cœurs, un point de bordure et deux points de bruit (étiquette $-1$).

**Choisir $\varepsilon$ et $m$.** L'effectif minimal $m$ se prend en général égal à $2p$ ($p$ étant la dimension), ou plus quand les données sont bruitées. Le rayon $\varepsilon$ se lit sur le **graphique des $k$-distances** : pour chaque point, on calcule la distance à son $m$-ième plus proche voisin, on trie ces distances, et on cherche le « coude » de la courbe, au-delà duquel les distances grimpent brusquement (les points isolés). Sur les deux lunes, avec $m=5$, la distance au 5e voisin est de $0{,}057$ pour la moitié des points et de $0{,}128$ pour $99\ \%$ d'entre eux.

```python hide
from sklearn.datasets import make_moons
from sklearn.neighbors import NearestNeighbors
Xm, ym = make_moons(600, noise=0.07, random_state=0)
nn = NearestNeighbors(n_neighbors=5).fit(Xm)
kd = np.sort(nn.kneighbors(Xm)[0][:, -1])
print("distance au 5e voisin, quantiles 50 / 90 / 95 / 99 % :", np.quantile(kd, [.5, .9, .95, .99]).round(3))
lignes = []
for eps in (0.05, 0.1, 0.15, 0.2, 0.3):
    lab = DBSCAN(eps=eps, min_samples=5).fit_predict(Xm)
    lignes.append({"epsilon": eps, "groupes": len(set(lab)) - (1 if -1 in lab else 0), "points de bruit": int((lab == -1).sum()), "ARI": round(adjusted_rand_score(ym, lab), 3)})
tab_eps = pd.DataFrame(lignes); print(tab_eps.to_string(index=False))
lab_km = KMeans(2, n_init=10, random_state=0).fit_predict(Xm)
lab_db = DBSCAN(eps=0.15, min_samples=5).fit_predict(Xm)
liens = {}
for lien in ("single", "complete", "average", "ward"):
    liens[lien] = AgglomerativeClustering(2, linkage=lien).fit_predict(Xm)
fr_lien = {"single": "simple", "complete": "complet", "average": "moyen", "ward": "de Ward"}
tab_lien = pd.DataFrame([{"méthode": "k-means (k=2)", "ARI": round(adjusted_rand_score(ym, lab_km), 3)}, {"méthode": "DBSCAN (epsilon=0,15)", "ARI": round(adjusted_rand_score(ym, lab_db), 3)}] +
                        [{"méthode": f"hiérarchique, lien {fr_lien[l]}", "ARI": round(adjusted_rand_score(ym, liens[l]), 3)} for l in liens])
print(tab_lien.to_string(index=False))
fig, ax = plt.subplots(1, 4, figsize=(11, 2.9))
for a, lab, titre in zip(ax, (lab_km, lab_db, liens["single"], liens["ward"]), ("k-means ($k=2$)", "DBSCAN ($\\varepsilon=0{,}15$)", "Hiérarchique, lien simple", "Hiérarchique, lien de Ward")):
    cl = np.where(lab == -1, 2, lab); couleurs = [BLEU, ORANGE, MUET]
    a.scatter(Xm[:, 0], Xm[:, 1], c=[couleurs[v] for v in cl], s=7); a.set_title(titre, fontsize=9); a.grid(False); a.set_xticks([]); a.set_yticks([])
plt.tight_layout(); save(fig, "ch03-lunes.png")
fig, ax = plt.subplots(figsize=(4.8, 3.0))
ax.plot(np.arange(len(kd)), kd, color=BLEU, lw=1.8)
for e, col in ((0.05, ROUGE), (0.15, AQUA)): ax.axhline(e, color=col, ls="--", lw=1); ax.text(10, e + 0.004, f"$\\varepsilon={e}$".replace(".", "{,}"), fontsize=8, color=col)
ax.set_xlabel("points triés"); ax.set_ylabel("distance au 5e plus proche voisin"); ax.set_title("Graphique des $k$-distances (deux lunes)", fontsize=9)
plt.tight_layout(); save(fig, "ch03-kdistances.png")
```
<!--sortie-->
```text
distance au 5e voisin, quantiles 50 / 90 / 95 / 99 % : [0.057 0.091 0.107 0.128]
 epsilon  groupes  points de bruit   ARI
    0.05       35              266 0.021
    0.10        2                4 0.987
    0.15        2                0 1.000
    0.20        2                0 1.000
    0.30        1                0 0.000
                   méthode   ARI
             k-means (k=2) 0.252
     DBSCAN (epsilon=0,15) 1.000
 hiérarchique, lien simple 1.000
hiérarchique, lien complet 0.426
  hiérarchique, lien moyen 0.557
hiérarchique, lien de Ward 0.557
figure : ch03-lunes.png
figure : ch03-kdistances.png
```

```python hide-code
print(tab_eps.to_string(index=False))
```
<!--sortie-->
```text
 epsilon  groupes  points de bruit   ARI
    0.05       35              266 0.021
    0.10        2                4 0.987
    0.15        2                0 1.000
    0.20        2                0 1.000
    0.30        1                0 0.000
```

![Deux lunes entrelacées : k-means, DBSCAN avec $\varepsilon=0{,}15$, classification hiérarchique à lien simple et à lien de Ward. Les points gris seraient du bruit.](figures/ch03-lunes.png)

![Graphique des $k$-distances des deux lunes (distance au 5e voisin, triée) avec deux valeurs de $\varepsilon$ testées.](figures/ch03-kdistances.png)

La sensibilité à $\varepsilon$ est nette. Trop petit ($0{,}05$), il **fragmente** les lunes en 35 groupes minuscules et déclare 266 points « bruit » (ARI $0{,}021$). Dans l'intervalle $0{,}1$ à $0{,}2$, il retrouve les deux lunes (ARI $0{,}987$ à $1{,}0$). Trop grand ($0{,}3$), les deux lunes **fusionnent** en un seul groupe (ARI nul). C'est la limite principale de DBSCAN : un seul rayon pour toute la population, donc une **densité unique**. Quand les groupes ont des densités très différentes, aucun $\varepsilon$ ne convient.

> ⚠️ **DBSCAN ne marche pas partout.** Sur les clients de la boutique, il échoue : les distributions sont asymétriques et le nuage forme un **continuum** de densités variables. Avec $m=14$ ($=2p$), $\varepsilon=0{,}8$ donne 3 groupes mais **16,5 %** de bruit et un ARI de $0{,}214$ avec la vérité (contre $0{,}487$ pour k-means) ; $\varepsilon=0{,}5$ déclare 86 % de bruit ; $\varepsilon=1{,}2$ fusionne tout. La méthode excelle sur des formes géométriques bien séparées, pas sur des profils de comportement à frontières floues.

```python hide
nn14 = NearestNeighbors(n_neighbors=14).fit(Z)
d14 = nn14.kneighbors(Z)[0][:, -1]
lignes = []
for eps in (0.5, 0.8, 1.2):
    lab = DBSCAN(eps=eps, min_samples=14).fit_predict(Z)
    lignes.append({"epsilon": eps, "groupes": len(set(lab)) - (1 if -1 in lab else 0), "part de bruit": round((lab == -1).mean(), 3), "ARI": round(adjusted_rand_score(c["segment_vrai"], lab), 3)})
tab_db_shop = pd.DataFrame(lignes); print(tab_db_shop.to_string(index=False))
```
<!--sortie-->
```text
 epsilon  groupes  part de bruit    ARI
     0.5        7          0.860 -0.016
     0.8        3          0.165  0.214
     1.2        2          0.008 -0.002
```

```python hide-code
print(tab_db_shop.to_string(index=False))
```
<!--sortie-->
```text
 epsilon  groupes  part de bruit    ARI
     0.5        7          0.860 -0.016
     0.8        3          0.165  0.214
     1.2        2          0.008 -0.002
```

### 3.3.2 La classification hiérarchique, revue par les liens

Le volume II (section 3.3.4) a présenté la classification ascendante hiérarchique : on part de $n$ groupes d'un point et on fusionne à chaque étape les deux groupes les plus proches, ce qui produit un **dendrogramme** que l'on coupe à la hauteur voulue. Reste à définir la distance entre **deux groupes** : c'est le **lien** (*linkage*).

- **Lien simple** : distance minimale entre un point de chaque groupe. Il suit les « chaînes » de points proches, et retrouve donc les formes allongées, mais il est sensible au **chaînage** (un pont de quelques points fusionne deux groupes distincts).
- **Lien complet** : distance maximale. Il produit des groupes compacts de diamètre limité.
- **Lien moyen** : distance moyenne entre toutes les paires.
- **Lien de Ward** : on fusionne les deux groupes dont la fusion fait **le moins augmenter la variance intra** $W$ ; c'est l'analogue hiérarchique de k-means, qui donne des groupes en boules.

Sur les deux lunes, l'effet du lien est spectaculaire (voir le tableau : le lien simple retrouve parfaitement les croissants, l'ARI du lien de Ward est modeste).

```python hide-code
print(tab_lien.to_string(index=False))
```
<!--sortie-->
```text
                   méthode   ARI
             k-means (k=2) 0.252
     DBSCAN (epsilon=0,15) 1.000
 hiérarchique, lien simple 1.000
hiérarchique, lien complet 0.426
  hiérarchique, lien moyen 0.557
hiérarchique, lien de Ward 0.557
```

Le lien simple atteint un ARI de $1{,}0$ ; le lien moyen et celui de Ward, $0{,}557$ ; le lien complet, $0{,}426$ ; k-means, $0{,}252$. **Aucun lien n'est « le bon »** : chacun encode une idée de la forme d'un groupe. Une limite pratique commune : la classification hiérarchique doit stocker les distances entre toutes les paires, soit un coût en mémoire de l'ordre de $n^2$ : acceptable pour quelques milliers de points, impossible pour nos 12 000 clients.

### 3.3.3 Les mélanges gaussiens : des appartenances « floues »

k-means affecte chaque client à **un** groupe, de façon tranchée. Or un client à mi-chemin entre fidèle et occasionnel n'appartient pas vraiment à l'un ou à l'autre. Les **mélanges gaussiens** (*Gaussian mixture models*, GMM) modélisent cela en supposant que les données sont tirées d'un **mélange de lois normales** :

$$p(\mathbf x)=\sum_{k=1}^K\pi_k\,\mathcal N(\mathbf x\mid\boldsymbol\mu_k,\Sigma_k),\qquad \pi_k\ge0,\ \sum_k\pi_k=1.$$

Chaque groupe $k$ a son centre $\boldsymbol\mu_k$, sa **forme** (la matrice de covariance $\Sigma_k$ : boule, ellipse, ellipse inclinée) et son **poids** $\pi_k$. La grande différence : pour un client $\mathbf x_i$, le modèle ne dit pas « groupe 2 », il donne les **probabilités d'appartenance** (ou *responsabilités*)

$$\gamma_{ik}=\frac{\pi_k\,\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)}{\sum_{l=1}^K\pi_l\,\mathcal N(\mathbf x_i\mid\boldsymbol\mu_l,\Sigma_l)}.$$

Les paramètres se choisissent en maximisant la vraisemblance, mais la somme dans le logarithme rend le calcul direct impossible. On le contourne par l'algorithme **EM** (*Expectation–Maximization*, Dempster, Laird et Rubin, 1977), qui alterne deux étapes simples :

- **étape E** (espérance) : avec les paramètres actuels, calculer les responsabilités $\gamma_{ik}$ ;
- **étape M** (maximisation) : remettre à jour les paramètres en traitant les $\gamma_{ik}$ comme des poids :
$$N_k=\sum_i\gamma_{ik},\qquad \boldsymbol\mu_k=\frac1{N_k}\sum_i\gamma_{ik}\,\mathbf x_i,\qquad \Sigma_k=\frac1{N_k}\sum_i\gamma_{ik}(\mathbf x_i-\boldsymbol\mu_k)(\mathbf x_i-\boldsymbol\mu_k)^\top,\qquad \pi_k=\frac{N_k}n.$$

> 📐 **D'où viennent ces formules ?** Dérivons la mise à jour de $\boldsymbol\mu_k$. La log-vraisemblance est $\ell=\sum_i\ln\sum_k\pi_k\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)$. Comme $\partial_{\boldsymbol\mu_k}\mathcal N(\mathbf x\mid\boldsymbol\mu_k,\Sigma_k)=\mathcal N\,\Sigma_k^{-1}(\mathbf x-\boldsymbol\mu_k)$, on obtient
> $$\frac{\partial\ell}{\partial\boldsymbol\mu_k}=\sum_i\underbrace{\frac{\pi_k\mathcal N(\mathbf x_i\mid\boldsymbol\mu_k,\Sigma_k)}{\sum_l\pi_l\mathcal N(\mathbf x_i\mid\boldsymbol\mu_l,\Sigma_l)}}_{\gamma_{ik}}\Sigma_k^{-1}(\mathbf x_i-\boldsymbol\mu_k).$$
> Annuler ce gradient donne $\sum_i\gamma_{ik}(\mathbf x_i-\boldsymbol\mu_k)=0$, soit $\boldsymbol\mu_k=\sum_i\gamma_{ik}\mathbf x_i/N_k$ : **une moyenne pondérée par les responsabilités**. Les autres formules se démontrent de même (avec un multiplicateur de Lagrange pour la contrainte $\sum_k\pi_k=1$). On montre ensuite (par l'inégalité de Jensen, qui fournit une minoration de $\ell$ que l'étape E rend exacte au point courant) que **chaque tour EM ne peut pas faire baisser la vraisemblance** ; l'algorithme converge donc vers un maximum **local**, ce qui impose, comme pour k-means, de relancer plusieurs fois.

> 💡 **k-means est un cas limite d'EM.** Si tous les groupes sont des boules de même variance $\sigma^2$ et de même poids, et que l'on fait tendre $\sigma\to0$, les responsabilités deviennent des $0$ ou des $1$ (le groupe le plus proche l'emporte) : l'étape E devient l'affectation de Lloyd, l'étape M devient le recalcul des centres. Un mélange gaussien est un k-means « avec des nuances ».

**Un tour d'EM à la main.** Quatre valeurs, $0;\ 1;\ 4;\ 6$, deux groupes. Pour que le calcul reste faisable à la main, on simplifie : les deux groupes ont la même variance $\sigma^2=1$ et le même poids $1/2$, et **seules les moyennes** sont à estimer ; on part de $\mu_1=0$ et $\mu_2=3$. La responsabilité du groupe 1 pour une valeur $x$ s'écrit $\gamma_1(x)=1/\big(1+e^{-[(x-\mu_2)^2-(x-\mu_1)^2]/2}\big)$.

- $x=0$ : $(9-0)/2=4{,}5$, donc $\gamma_1=1/(1+e^{-4{,}5})\approx0{,}989$.
- $x=1$ : $(4-1)/2=1{,}5$, donc $\gamma_1\approx0{,}818$.
- $x=4$ : $(1-16)/2=-7{,}5$, donc $\gamma_1\approx0{,}0006$ ; $x=6$ : $\gamma_1\approx0$.

Étape M : $\mu_1=\dfrac{0\times0{,}989+1\times0{,}818+4\times0{,}0006}{0{,}989+0{,}818+0{,}0006}\approx0{,}454$ et, avec $\gamma_2=1-\gamma_1$, $\mu_2=\dfrac{1\times0{,}182+4\times0{,}9994+6\times1}{0{,}011+0{,}182+0{,}9994+1}\approx4{,}642$. Les deux centres se sont rapprochés de leurs vraies valeurs ; deux ou trois tours suffisent.

```python hide
from scipy.stats import norm
xe = np.array([0.0, 1.0, 4.0, 6.0]); mu = np.array([0.0, 3.0]); histo = [mu.copy()]
g1 = None
for it in range(4):
    g = 1 / (1 + np.exp(-((xe - mu[1]) ** 2 - (xe - mu[0]) ** 2) / 2)); G = np.column_stack([g, 1 - g])
    if it == 0: g1 = g.copy()
    mu = (G * xe[:, None]).sum(0) / G.sum(0); histo.append(mu.copy())
print("responsabilités du groupe 1 au tour 1 :", g1.round(4))
for it, m in enumerate(histo): print("tour", it, ": mu =", m.round(3))
# EM complet (moyennes, variances, poids) sur 6 valeurs, pour la figure
xs = np.array([1.0, 1.5, 2.0, 5.0, 6.0, 6.5]); m_ = np.array([2.0, 4.0]); s_ = np.array([1.0, 1.0]); p_ = np.array([0.5, 0.5]); traj = [(m_.copy(), s_.copy(), p_.copy())]
for it in range(6):
    r = p_ * norm.pdf(xs[:, None], m_, s_); r /= r.sum(1, keepdims=True); N = r.sum(0)
    m_ = (r * xs[:, None]).sum(0) / N; s_ = np.sqrt((r * (xs[:, None] - m_) ** 2).sum(0) / N); p_ = N / len(xs); traj.append((m_.copy(), s_.copy(), p_.copy()))
ll = lambda m, s, p: np.log((p * norm.pdf(xs[:, None], m, s)).sum(1)).sum()
print("log-vraisemblance aux tours 0, 1, 2, 6 :", [round(ll(*traj[i]), 3) for i in (0, 1, 2, 6)])
print("paramètres finaux : moyennes", m_.round(3), "écarts-types", s_.round(3), "poids", p_.round(3))
grille = np.linspace(-1, 9, 400)
fig, ax = plt.subplots(1, 3, figsize=(10, 2.7), sharey=True)
for a, i in zip(ax, (0, 1, 6)):
    m, s, p = traj[i]
    a.plot(grille, (p * norm.pdf(grille[:, None], m, s)).sum(1), color=BLEU, lw=2)
    for k, col in enumerate((ORANGE, AQUA)): a.plot(grille, p[k] * norm.pdf(grille, m[k], s[k]), color=col, lw=1.2, ls="--")
    a.plot(xs, np.zeros_like(xs) - 0.01, "|", color=ENCRE2, ms=14); a.set_title(f"tour {i} : $\\ell = {ll(m, s, p):.2f}$".replace(".", "{,}"), fontsize=9)
ax[0].set_ylabel("densité du mélange")
plt.tight_layout(); save(fig, "ch03-em.png")
```
<!--sortie-->
```text
responsabilités du groupe 1 au tour 1 : [9.890e-01 8.176e-01 6.000e-04 0.000e+00]
tour 0 : mu = [0. 3.]
tour 1 : mu = [0.454 4.642]
tour 2 : mu = [0.504 4.998]
tour 3 : mu = [0.506 5.001]
tour 4 : mu = [0.506 5.001]
log-vraisemblance aux tours 0, 1, 2, 6 : [np.float64(-15.707), np.float64(-9.521), np.float64(-8.572), np.float64(-8.568)]
paramètres finaux : moyennes [1.5   5.833] écarts-types [0.408 0.624] poids [0.5 0.5]
figure : ch03-em.png
```

```python hide-code
print("responsabilités du groupe 1 au tour 1 :", g1.round(4))
for it, m in enumerate(histo[:4]): print("tour", it, ": mu =", m.round(3))
```
<!--sortie-->
```text
responsabilités du groupe 1 au tour 1 : [9.890e-01 8.176e-01 6.000e-04 0.000e+00]
tour 0 : mu = [0. 3.]
tour 1 : mu = [0.454 4.642]
tour 2 : mu = [0.504 4.998]
tour 3 : mu = [0.506 5.001]
```

![Trois étapes de l'algorithme EM sur six valeurs : le mélange (bleu) et ses deux composantes (pointillés) au départ, après un tour, puis à la convergence ; la log-vraisemblance $\ell$ augmente.](figures/ch03-em.png)

La bibliothèque confirme les nombres de la main : après un tour, $\mu=(0{,}454;\ 4{,}642)$. Le graphique montre un EM **complet** (moyennes, écarts-types et poids) sur six valeurs : la vraisemblance augmente à chaque tour, ce que garantit la théorie.

**Choisir le nombre de composantes : le critère BIC.** Contrairement à k-means, un GMM possède une **vraisemblance**, donc un critère de sélection de modèle : le **BIC** (*Bayesian Information Criterion*), $\mathrm{BIC}=-2\ln\hat L+q\ln n$, où $q$ est le nombre de paramètres libres. Il récompense l'ajustement et pénalise la complexité (à minimiser). Sur les clients, avec $p=7$ variables et une covariance complète, chaque composante coûte $7+28=35$ paramètres (plus un poids).

```python hide
from sklearn.mixture import GaussianMixture
lignes = []
for k in range(1, 9):
    g = GaussianMixture(k, covariance_type="full", n_init=3, random_state=0).fit(Z)
    lignes.append({"k": k, "BIC": round(g.bic(Z)), "ARI avec la vérité": round(adjusted_rand_score(c["segment_vrai"], g.predict(Z)), 3)})
tab_bic = pd.DataFrame(lignes); print(tab_bic.to_string(index=False))
lignes = []
for ct in ("full", "diag", "spherical", "tied"):
    g = GaussianMixture(4, covariance_type=ct, n_init=3, random_state=0).fit(Z)
    lignes.append({"covariance": ct, "BIC": round(g.bic(Z)), "ARI avec la vérité": round(adjusted_rand_score(c["segment_vrai"], g.predict(Z)), 3)})
tab_cov = pd.DataFrame(lignes); print(tab_cov.to_string(index=False))
g4 = GaussianMixture(4, covariance_type="full", n_init=3, random_state=0).fit(Z)
pmax = g4.predict_proba(Z).max(axis=1)
print("part des clients dont la plus forte probabilité d'appartenance est < 0,7 :", round((pmax < 0.7).mean(), 3), "| < 0,9 :", round((pmax < 0.9).mean(), 3))
fig, ax = plt.subplots(1, 2, figsize=(8.6, 2.9))
ax[0].plot(tab_bic["k"], tab_bic["BIC"] / 1000, "o-", color=BLEU, lw=1.8); ax[0].set_xlabel("nombre de composantes $k$"); ax[0].set_ylabel("BIC (milliers)"); ax[0].set_title("BIC : la chute se calme après $k=4$", fontsize=9)
ax[1].plot(tab_bic["k"], tab_bic["ARI avec la vérité"], "o-", color=ORANGE, lw=1.8); ax[1].set_xlabel("nombre de composantes $k$"); ax[1].set_ylabel("ARI avec la vérité cachée"); ax[1].set_title("Fidélité à la vérité (laboratoire seulement)", fontsize=9)
plt.tight_layout(); save(fig, "ch03-bic.png")
```
<!--sortie-->
```text
 k    BIC  ARI avec la vérité
 1 207243               0.000
 2 180819               0.336
 3 117562               0.276
 4 106300               0.503
 5 104420               0.469
 6 102459               0.407
 7 101505               0.358
 8 101462               0.358
covariance    BIC  ARI avec la vérité
      full 106300               0.503
      diag 114379               0.477
 spherical 197934               0.497
      tied 181073               0.506
part des clients dont la plus forte probabilité d'appartenance est < 0,7 : 0.07 | < 0,9 : 0.168
figure : ch03-bic.png
```

```python hide-code
print(tab_bic.to_string(index=False))
print(tab_cov.to_string(index=False))
print("part de clients avec probabilité maximale < 0,7 :", round((pmax < 0.7).mean(), 3))
```
<!--sortie-->
```text
 k    BIC  ARI avec la vérité
 1 207243               0.000
 2 180819               0.336
 3 117562               0.276
 4 106300               0.503
 5 104420               0.469
 6 102459               0.407
 7 101505               0.358
 8 101462               0.358
covariance    BIC  ARI avec la vérité
      full 106300               0.503
      diag 114379               0.477
 spherical 197934               0.497
      tied 181073               0.506
part de clients avec probabilité maximale < 0,7 : 0.07
```

![BIC d'un mélange gaussien à covariance complète selon le nombre de composantes (à gauche) et ARI avec la vérité cachée (à droite).](figures/ch03-bic.png)

Le BIC chute violemment jusqu'à $k=4$ (de $117\,562$ à $106\,300$ entre $k=3$ et $k=4$), puis ne gagne plus que de petits montants ($104\,420$ à $k=5$, $102\,459$ à $k=6$, et à peine $43$ de $k=7$ à $k=8$) : le coude est à $4$. Le BIC continue pourtant de décroître lentement, parce que les variables (comptages, montants) ne sont **pas exactement gaussiennes** : de petites composantes supplémentaires servent à épouser les asymétries. À $k=4$, le mélange à covariance complète atteint un ARI de $0{,}503$, un peu mieux que k-means ($0{,}487$).

Le tableau des types de covariance est une mise en garde. La covariance **sphérique** (des boules, comme k-means) a un BIC très mauvais ($197\,934$) mais un ARI quasi identique ($0{,}497$) ; la covariance **complète** a le meilleur BIC ($106\,300$). Le BIC juge **la qualité de l'ajustement de la densité**, l'ARI juge **la qualité de la partition** : ce sont deux objectifs différents, qui ne se classent pas toujours de la même façon.

Enfin, l'intérêt propre du mélange : **$7{,}0\ \%$** des clients ont une probabilité maximale d'appartenance inférieure à $0{,}7$ (et $16{,}8\ \%$ sous $0{,}9$), c'est-à-dire qu'ils sont réellement « entre deux groupes ». Cette incertitude, qu'un k-means tranché cache, est une information utile : on peut réserver les messages très ciblés aux clients dont l'appartenance est sûre.

> ✅ **À retenir (méthodes au-delà de k-means).**
> - **DBSCAN** : groupes = régions denses, forme libre, bruit explicite ; mais un seul rayon $\varepsilon$ (une seule densité), et inadapté à des données en continuum.
> - **Classification hiérarchique** : le **lien** (simple, complet, moyen, Ward) définit la forme des groupes ; coût mémoire en $n^2$.
> - **Mélanges gaussiens** : appartenances **probabilistes**, formes elliptiques, estimation par **EM** (la vraisemblance ne baisse jamais, optimum local) ; le **BIC** guide le choix de $K$.
> - Aucune méthode n'est supérieure en soi : on choisit selon la forme probable des groupes, puis on **valide** avec les épreuves de 3.1.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.5 et 3.6, exercices 3.9 à 3.11.
