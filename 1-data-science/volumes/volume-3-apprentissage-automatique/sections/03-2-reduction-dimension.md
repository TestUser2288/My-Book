## 3.2 Réduction de dimension

> 💡 **Intuition.** Une photographie de $64$ pixels n'a pas besoin de $64$ nombres indépendants pour être reconnue : les pixels voisins se ressemblent, les traits se répètent. La réduction de dimension cherche **la description courte** que cachent les données longues : moins de variables, presque la même information. Elle sert à **comprendre** (peut-on dessiner les données ?), à **compresser**, à **débruiter** et à **accélérer** les modèles qui suivent.

Le volume II a présenté la plus célèbre de ces méthodes, l'ACP (section 3.1). Cette section commence par expliquer *pourquoi* réduire est souvent indispensable (la « malédiction de la dimension »), rappelle l'ACP en une page pour mesurer ce qu'elle garde, puis présente les méthodes qui prolongent l'ACP quand ses hypothèses ne tiennent pas : données non linéaires, données positives à interpréter par « parties », données si nombreuses qu'on ne peut plus les centrer, ou si larges qu'on préfère une projection au hasard.

### 3.2.1 Pourquoi réduire : la malédiction de la dimension

Quand on ajoute des variables, on s'attend à *mieux* décrire les clients. La géométrie dit le contraire dès qu'on raisonne en **distances**, base de nombreuses méthodes (k plus proches voisins, k-means, noyaux). Prenons des points tirés uniformément dans un cube de dimension $d$, et regardons les distances entre paires de points.

Pour deux points $\mathbf x$ et $\mathbf y$ dont les coordonnées sont indépendantes et de même loi, le carré de la distance $\|\mathbf x-\mathbf y\|^2=\sum_{j=1}^d(x_j-y_j)^2$ est une somme de $d$ termes indépendants : son espérance croît comme $d$ et son écart-type comme $\sqrt d$. La **dispersion relative** des distances décroît donc comme $1/\sqrt d$ : quand $d$ grandit, **toutes les distances deviennent presque égales**, et la notion de « plus proche voisin » perd son sens.

```python hide
from sklearn.metrics import pairwise_distances
rg = np.random.default_rng(1)
lignes = []
for dim in (2, 5, 10, 50, 200, 1000):
    A = rg.uniform(size=(500, dim))
    D = pairwise_distances(A)[np.triu_indices(500, 1)]
    lignes.append({"dimension": dim, "rapport max/min": round(D.max() / D.min(), 2), "écart-type / moyenne": round(D.std() / D.mean(), 3)})
conc = pd.DataFrame(lignes)
print(conc.to_string(index=False))
fig, ax = plt.subplots(1, 2, figsize=(8.6, 2.9))
ax[0].plot(conc["dimension"], conc["rapport max/min"], "o-", color=BLEU, lw=1.8); ax[0].set_xscale("log"); ax[0].set_yscale("log")
ax[0].set_xlabel("dimension $d$"); ax[0].set_ylabel("plus grande / plus petite distance"); ax[0].set_title("Les distances se resserrent", fontsize=9)
ax[1].plot(conc["dimension"], conc["écart-type / moyenne"], "o-", color=ORANGE, lw=1.8)
ax[1].plot(conc["dimension"], conc["écart-type / moyenne"].iloc[0] * np.sqrt(2 / conc["dimension"]), "--", color=MUET, label="décroissance en $1/\\sqrt{d}$ (repère)")
ax[1].set_xscale("log"); ax[1].set_xlabel("dimension $d$"); ax[1].set_ylabel("dispersion relative des distances"); ax[1].legend(frameon=False, fontsize=8)
ax[1].set_title("Dispersion relative des distances", fontsize=9)
plt.tight_layout(); save(fig, "ch03-malediction.png")
```
<!--sortie-->
```text
 dimension  rapport max/min  écart-type / moyenne
         2          1429.48                 0.475
         5            32.82                 0.283
        10             7.32                 0.193
        50             2.11                 0.086
       200             1.42                 0.042
      1000             1.18                 0.018
figure : ch03-malediction.png
```

```python hide-code
print(conc.to_string(index=False))
```
<!--sortie-->
```text
 dimension  rapport max/min  écart-type / moyenne
         2          1429.48                 0.475
         5            32.82                 0.283
        10             7.32                 0.193
        50             2.11                 0.086
       200             1.42                 0.042
      1000             1.18                 0.018
```

![Distances entre 500 points tirés uniformément dans un cube de dimension $d$ : le rapport entre la plus grande et la plus petite distance et la dispersion relative des distances décroissent avec $d$.](figures/ch03-malediction.png)

En dimension 2, la plus grande distance est environ $1\,400$ fois la plus petite ; en dimension 50, ce rapport tombe à $2{,}1$ ; en dimension 1 000, à $1{,}18$ : tous les points sont à peu près à la même distance de tous les autres. Un k-means ou un plus proche voisin qui s'appuie sur ces distances ne sait plus distinguer proche et lointain.

> ⚠️ **Nuance importante.** La malédiction est la plus sévère quand les variables sont **indépendantes** et **toutes pertinentes**. Les données réelles ont presque toujours une structure bien plus pauvre que leur nombre de colonnes : les chiffres manuscrits ont 64 pixels mais occupent une portion très réduite de l'espace des images possibles. C'est ce qui rend la réduction de dimension **possible** : on ne comprime pas l'espace entier, seulement la petite région où vivent les données.

### 3.2.2 L'ACP en une page, et ce qu'elle garde

Rappelons l'essentiel (volume II, sections 3.1.3 et 3.1.4). Pour des données centrées $\mathbf X$ de $n$ lignes et $p$ colonnes, l'ACP cherche les directions orthogonales de variance maximale ; ce sont les vecteurs propres de la matrice de covariance, et la variance portée par la $j$-ième direction est la valeur propre $\lambda_j$. Garder les $m$ premières composantes revient à projeter chaque observation sur le sous-espace de dimension $m$ le plus proche des données.

Ce que l'on **perd** s'exprime exactement. D'après le théorème d'**Eckart–Young**, la meilleure approximation de rang $m$ de $\mathbf X$ (au sens de la somme des carrés des erreurs) est obtenue par la SVD tronquée, et l'erreur quadratique de reconstruction vaut la somme des valeurs propres **écartées** :

$$\sum_{i}\|\mathbf x_i-\hat{\mathbf x}_i\|^2=(n-1)\sum_{j>m}\lambda_j,\qquad\text{soit en proportion : }\ 1-\frac{\lambda_1+\dots+\lambda_m}{\lambda_1+\dots+\lambda_p}.$$

L'erreur *relative* de reconstruction est donc exactement **un moins la part de variance expliquée** : c'est ce qui rend le tableau de bord de l'ACP (le graphique cumulé des valeurs propres) aussi utile. Appliquons-le aux 1 797 chiffres manuscrits ($p=64$).

```python hide
from sklearn.decomposition import PCA
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import cross_val_score
Xd = chiffres.data / 16.0
yd = chiffres.target
pca_d = PCA().fit(Xd)
cum = np.cumsum(pca_d.explained_variance_ratio_)
print("variance des 5 premières composantes :", pca_d.explained_variance_ratio_[:5].round(3))
print("dimensions pour 80 / 90 / 95 / 99 % :", [int(np.searchsorted(cum, t) + 1) for t in (0.8, 0.9, 0.95, 0.99)])
lignes = []
for m in (2, 5, 10, 20, 30, 40):
    pm = PCA(m).fit(Xd)
    R = pm.inverse_transform(pm.transform(Xd))
    err = ((Xd - R) ** 2).sum() / ((Xd - Xd.mean(0)) ** 2).sum()
    acc = cross_val_score(KNeighborsClassifier(5), pm.transform(Xd), yd, cv=5).mean()
    lignes.append({"composantes": m, "variance gardée": round(cum[m - 1], 3), "erreur relative": round(err, 3), "précision 5-ppv": round(acc, 3)})
tab_pca = pd.DataFrame(lignes)
acc_brut = cross_val_score(KNeighborsClassifier(5), Xd, yd, cv=5).mean()
print(tab_pca.to_string(index=False)); print("précision 5-ppv sur les 64 pixels bruts :", round(acc_brut, 3))
fig, ax = plt.subplots(1, 2, figsize=(10, 3.0))
ax[0].plot(range(1, 65), cum, color=BLEU, lw=1.8)
for t, m in zip((0.8, 0.9, 0.95, 0.99), (13, 21, 29, 41)):
    ax[0].plot([m], [t], "o", color=ORANGE, ms=5); ax[0].text(m + 1.5, t - 0.045, f"{int(t * 100)} % : {m}", fontsize=8, color=ENCRE2)
ax[0].set_xlabel("nombre de composantes"); ax[0].set_ylabel("variance cumulée"); ax[0].set_title("Chiffres manuscrits : variance gardée", fontsize=9)
ax[1].plot(tab_pca["composantes"], tab_pca["précision 5-ppv"], "o-", color=AQUA, lw=1.8, label="précision 5-ppv (validation croisée)")
ax[1].axhline(acc_brut, color=MUET, ls="--", lw=1, label="64 pixels bruts")
ax[1].set_xlabel("nombre de composantes"); ax[1].set_ylabel("précision"); ax[1].legend(frameon=False, fontsize=8, loc="lower right"); ax[1].set_title("Reconnaître un chiffre avec peu de dimensions", fontsize=9)
plt.tight_layout(); save(fig, "ch03-chiffres-pca.png")
fig, ax = plt.subplots(4, 6, figsize=(7.4, 5.0))
indices = [3, 8, 20, 29, 45, 77]
for col, i in enumerate(indices):
    ax[0, col].imshow(Xd[i].reshape(8, 8), cmap="gray_r"); ax[0, col].set_title(f"chiffre {yd[i]}", fontsize=8)
    for ligne, m in enumerate((2, 10, 30), start=1):
        pm = PCA(m).fit(Xd); r = pm.inverse_transform(pm.transform(Xd[i:i + 1]))[0]
        ax[ligne, col].imshow(r.reshape(8, 8), cmap="gray_r")
        if col == 0: ax[ligne, col].set_ylabel(f"{m} composantes", fontsize=8)
for a in ax.ravel(): a.set_xticks([]); a.set_yticks([]); a.grid(False)
ax[0, 0].set_ylabel("original", fontsize=8)
plt.tight_layout(); save(fig, "ch03-chiffres-reconstruction.png")
```
<!--sortie-->
```text
variance des 5 premières composantes : [0.149 0.136 0.118 0.084 0.058]
dimensions pour 80 / 90 / 95 / 99 % : [13, 21, 29, 41]
 composantes  variance gardée  erreur relative  précision 5-ppv
           2            0.285            0.715            0.603
           5            0.545            0.455            0.888
          10            0.738            0.262            0.937
          20            0.894            0.106            0.959
          30            0.959            0.041            0.962
          40            0.988            0.012            0.961
précision 5-ppv sur les 64 pixels bruts : 0.963
figure : ch03-chiffres-pca.png
figure : ch03-chiffres-reconstruction.png
```

```python hide-code
print(tab_pca.to_string(index=False))
print("précision 5-ppv sur les 64 pixels bruts :", round(acc_brut, 3))
```
<!--sortie-->
```text
 composantes  variance gardée  erreur relative  précision 5-ppv
           2            0.285            0.715            0.603
           5            0.545            0.455            0.888
          10            0.738            0.262            0.937
          20            0.894            0.106            0.959
          30            0.959            0.041            0.962
          40            0.988            0.012            0.961
précision 5-ppv sur les 64 pixels bruts : 0.963
```

![Gauche : variance cumulée des composantes principales des chiffres manuscrits et nombre de composantes nécessaires pour 80, 90, 95 et 99 %. Droite : précision d'un classifieur des 5 plus proches voisins selon le nombre de composantes gardées, comparée aux 64 pixels bruts.](figures/ch03-chiffres-pca.png)

![Quatre lignes : six chiffres originaux, puis leur reconstruction avec 2, 10 et 30 composantes principales.](figures/ch03-chiffres-reconstruction.png)

Trois lectures. **(i)** Il faut $13$ composantes pour garder $80\ \%$ de la variance, $21$ pour $90\ \%$, $29$ pour $95\ \%$ et $41$ pour $99\ \%$ : une compression par trois sans perte visible. **(ii)** L'erreur relative de reconstruction coïncide bien avec « un moins la variance gardée » (à $10$ composantes : $0{,}738$ de variance gardée et $0{,}262$ d'erreur, ce que dit Eckart–Young). **(iii)** Surtout, **l'information utile pour reconnaître un chiffre survit à la compression** : avec $20$ composantes, la précision d'un classifieur des 5 plus proches voisins est de $0{,}959$ contre $0{,}963$ sur les $64$ pixels bruts, alors qu'avec $2$ composantes elle tombe à $0{,}603$. Le graphique des reconstructions le montre : à $2$ composantes on devine à peine la forme, à $10$ on lit le chiffre, à $30$ on ne voit plus la différence.

### 3.2.3 Quand la structure n'est pas linéaire : l'ACP à noyau

L'ACP ne trouve que des directions **linéaires**. Sur deux cercles concentriques, aucune droite ne sépare le cercle intérieur du cercle extérieur : la première composante principale, qui est une direction, les mélange.

L'**ACP à noyau** (*kernel PCA*, Schölkopf et coll., 1998) contourne cette limite par une idée remarquable : au lieu de projeter les données elles-mêmes, on les envoie d'abord dans un espace de très grande dimension où elles deviennent séparables, puis on y fait une ACP, **sans jamais calculer explicitement** cet espace. Il suffit de connaître les **produits scalaires** entre points dans cet espace, que fournit une fonction appelée **noyau**, par exemple le noyau gaussien :

$$k(\mathbf x,\mathbf y)=\exp\!\big(-\gamma\,\|\mathbf x-\mathbf y\|^2\big).$$

La méthode a quatre étapes : (1) calculer la matrice de Gram $K_{ij}=k(\mathbf x_i,\mathbf x_j)$ ; (2) la **centrer** dans l'espace transformé, $\tilde K=K-\mathbf 1K-K\mathbf 1+\mathbf 1K\mathbf 1$ où $\mathbf 1$ est la matrice $n\times n$ dont toutes les entrées valent $1/n$ ; (3) calculer ses valeurs propres $\lambda_j$ et vecteurs propres $\mathbf v_j$ ; (4) les coordonnées du point $i$ sur la $j$-ième composante sont $\sqrt{\lambda_j}\,v_{j,i}$.

```python hide
from sklearn.datasets import make_circles
from sklearn.decomposition import KernelPCA
from sklearn.linear_model import LogisticRegression
Xc, yc = make_circles(600, factor=0.3, noise=0.05, random_state=0)
acp = PCA(2).fit_transform(Xc)
kpca = KernelPCA(2, kernel="rbf", gamma=2).fit_transform(Xc)
sep = {nom: round(LogisticRegression().fit(Zc[:, :1], yc).score(Zc[:, :1], yc), 3) for nom, Zc in [("ACP", acp), ("ACP à noyau", kpca)]}
print("précision d'une séparation par seuil sur la 1re composante :", sep)
fig, ax = plt.subplots(1, 3, figsize=(10, 3.0))
for a, M, titre in zip(ax, (Xc, acp, kpca), ("Données : deux cercles", "ACP : la 1re composante mélange tout", "ACP à noyau (gaussien, $\\gamma=2$)")):
    a.scatter(M[:, 0], M[:, 1], c=np.where(yc == 0, ORANGE, BLEU), s=8, alpha=0.8); a.set_title(titre, fontsize=9); a.grid(False)
plt.tight_layout(); save(fig, "ch03-kpca.png")
```
<!--sortie-->
```text
précision d'une séparation par seuil sur la 1re composante : {'ACP': 0.498, 'ACP à noyau': 1.0}
figure : ch03-kpca.png
```

```python hide-code
print("précision d'une séparation par seuil sur la 1re composante :", sep)
```
<!--sortie-->
```text
précision d'une séparation par seuil sur la 1re composante : {'ACP': 0.498, 'ACP à noyau': 1.0}
```

![Deux cercles concentriques : les données, leur projection par ACP linéaire, puis par ACP à noyau gaussien, qui sépare les deux cercles le long de la première composante.](figures/ch03-kpca.png)

Une séparation par un simple seuil sur la première composante a une précision de $0{,}498$ avec l'ACP (le hasard) et de $1{,}0$ avec l'ACP à noyau. Deux mises en garde : le paramètre $\gamma$ du noyau **décide** de ce que la méthode voit (trop grand, chaque point est isolé ; trop petit, le noyau devient presque linéaire) et il se règle par validation, comme n'importe quel hyperparamètre (section 1.5) ; et, contrairement à l'ACP, la **reconstruction** n'est pas directe (retrouver un point de l'espace d'origine à partir d'une position dans l'espace transformé est un problème d'« image réciproque » approchée).

### 3.2.4 SVD tronquée : quand on ne peut pas centrer

L'ACP exige de **centrer** les données, ce qui détruit la **parcimonie** : une matrice de $100\,000$ documents et de $50\,000$ mots, presque toute faite de zéros, devient dense une fois centrée, donc impossible à stocker. La **SVD tronquée** (`TruncatedSVD`) applique la même décomposition en valeurs singulières **sans centrer** ; elle conserve la parcimonie et reste calculable. Quand les colonnes sont déjà centrées, elle coïncide avec l'ACP. Appliquée à des tableaux de comptages de mots, elle porte le nom d'**analyse sémantique latente** (LSA).

```python hide
from sklearn.decomposition import TruncatedSVD, NMF
sv = TruncatedSVD(10, random_state=0).fit(Xd)
print("variance expliquée par 10 composantes : SVD tronquée", round(sv.explained_variance_ratio_.sum(), 3), "| ACP", round(PCA(10).fit(Xd).explained_variance_ratio_.sum(), 3))
```
<!--sortie-->
```text
variance expliquée par 10 composantes : SVD tronquée 0.732 | ACP 0.738
```

```python hide-code
print("variance expliquée par 10 composantes : SVD tronquée", round(sv.explained_variance_ratio_.sum(), 3), "| ACP", round(PCA(10).fit(Xd).explained_variance_ratio_.sum(), 3))
```
<!--sortie-->
```text
variance expliquée par 10 composantes : SVD tronquée 0.732 | ACP 0.738
```

Sur les chiffres, dont les pixels ne sont pas centrés, les deux méthodes donnent presque la même part de variance expliquée par $10$ composantes ($0{,}732$ contre $0{,}738$) : l'écart, minime, tient à l'absence de centrage.

### 3.2.5 La factorisation non négative : décrire par parties

Les composantes principales ont des coefficients positifs et négatifs : une image se décrit comme un mélange où certaines directions *retranchent* de l'information, ce qui rend les composantes difficiles à lire (« moitié d'un chiffre, moins un autre »). Quand les données sont **positives** (pixels, comptages, montants), on peut exiger une description **purement additive**.

La **factorisation non négative** (NMF, Lee et Seung, 1999) approche la matrice des données $V\ (n\times p)$ par un produit de deux matrices à entrées positives ou nulles :

$$V\approx WH,\qquad W\ge0\ (n\times m),\quad H\ge0\ (m\times p),$$

en minimisant $\|V-WH\|_F^2$. Chaque ligne de $H$ est une « partie » (un motif de base) ; chaque observation est une **somme** de parties pondérées par sa ligne de $W$. Les mises à jour multiplicatives de Lee et Seung, $H\leftarrow H\circ\dfrac{W^\top V}{W^\top WH}$ et $W\leftarrow W\circ\dfrac{VH^\top}{WHH^\top}$ (produit et quotient *terme à terme*), préservent la positivité et diminuent l'erreur à chaque pas.

```python hide
nmf = NMF(10, init="nndsvda", random_state=0, max_iter=400).fit(Xd)
acc_nmf = cross_val_score(KNeighborsClassifier(5), nmf.transform(Xd), yd, cv=5).mean()
acc_pca10 = cross_val_score(KNeighborsClassifier(5), PCA(10).fit_transform(Xd), yd, cv=5).mean()
print("NMF 10 composantes : erreur de reconstruction", round(nmf.reconstruction_err_, 2), "| précision 5-ppv", round(acc_nmf, 3), "| ACP 10 composantes", round(acc_pca10, 3))
fig, ax = plt.subplots(2, 5, figsize=(7.4, 3.2))
for a, comp, k in zip(ax.ravel(), nmf.components_, range(10)):
    a.imshow(comp.reshape(8, 8), cmap="gray_r"); a.set_title(f"partie {k + 1}", fontsize=8); a.set_xticks([]); a.set_yticks([]); a.grid(False)
plt.tight_layout(); save(fig, "ch03-nmf.png")
```
<!--sortie-->
```text
NMF 10 composantes : erreur de reconstruction 53.96 | précision 5-ppv 0.84 | ACP 10 composantes 0.937
figure : ch03-nmf.png
```

```python hide-code
print("NMF, 10 composantes : précision 5-ppv", round(acc_nmf, 3), "| ACP, 10 composantes :", round(acc_pca10, 3))
```
<!--sortie-->
```text
NMF, 10 composantes : précision 5-ppv 0.84 | ACP, 10 composantes : 0.937
```

![Les dix « parties » apprises par la factorisation non négative sur les chiffres manuscrits : chacune est un motif de traits que l'on additionne.](figures/ch03-nmf.png)

Les dix parties sont des **motifs de traits** que l'on peut additionner pour composer un chiffre : c'est la lisibilité qu'on cherche. Elle a un prix : avec $10$ composantes, un classifieur des 5 plus proches voisins atteint $0{,}840$ sur la NMF contre $0{,}937$ sur l'ACP. La NMF n'est donc **pas** une compression meilleure ; c'est une **représentation plus lisible**. Elle sert quand on veut interpréter (thèmes d'un corpus, profils d'achat, spectres).

### 3.2.6 Les projections aléatoires et le lemme de Johnson–Lindenstrauss

Dernière idée, qui surprend : pour réduire la dimension, **on peut projeter au hasard**. Choisissons une matrice $R$ de $k$ lignes et $p$ colonnes dont les entrées sont des tirages indépendants d'une loi $\mathcal N(0,1/k)$, et remplaçons chaque observation $\mathbf x$ par $R\mathbf x$. Cela paraît absurde (aucune information sur les données n'a servi à construire $R$), et pourtant :

> 📐 **Lemme de Johnson–Lindenstrauss (1984).** Pour tout $0<\varepsilon<1$ et tout ensemble de $n$ points de $\mathbb R^p$, il existe une application linéaire vers $\mathbb R^k$ avec
> $$k\ \ge\ \frac{4\ln n}{\varepsilon^2/2-\varepsilon^3/3}$$
> qui préserve toutes les distances à un facteur près : $(1-\varepsilon)\|\mathbf x-\mathbf y\|^2\le\|f(\mathbf x)-f(\mathbf y)\|^2\le(1+\varepsilon)\|\mathbf x-\mathbf y\|^2$ pour tous les couples. De plus, une projection gaussienne aléatoire convient avec une probabilité élevée.

*Idée de la démonstration.* Pour un vecteur fixe $\mathbf u$ et $R$ gaussienne, $\|R\mathbf u\|^2/\|\mathbf u\|^2$ suit la loi $\chi^2_k/k$, d'espérance $1$ et de variance $2/k$ : elle se **concentre** autour de $1$ quand $k$ grandit, avec une queue exponentielle. On applique ensuite une **borne de l'union** sur les $n(n-1)/2$ différences $\mathbf x_i-\mathbf x_j$ : si la probabilité d'erreur de chacune est de l'ordre de $n^{-2}$, la probabilité qu'une seule échoue reste faible, ce qui impose $k$ de l'ordre de $\ln n/\varepsilon^2$.

Deux remarques déroutantes. Le résultat est **indépendant de $p$** : seul le nombre de points $n$ compte (de façon logarithmique). Et la borne est **pessimiste** : elle garantit *toutes* les paires. Mesurons ce qui se passe réellement sur nos 1 797 chiffres ($p=64$).

```python hide
from sklearn.random_projection import GaussianRandomProjection, johnson_lindenstrauss_min_dim
D0 = pairwise_distances(Xd); iu = np.triu_indices(len(Xd), 1); d0 = D0[iu]
lignes = []; ratios = {}
for k in (5, 10, 20, 40, 64, 100, 200):
    gr = GaussianRandomProjection(k, random_state=0).fit(Xd)
    r = pairwise_distances(gr.transform(Xd))[iu] / d0
    ratios[k] = r
    lignes.append({"k": k, "ratio moyen": round(r.mean(), 3), "écart-type": round(r.std(), 3), "5 % - 95 %": f"{np.quantile(r, .05):.2f} - {np.quantile(r, .95):.2f}", "paires à ±20 %": f"{np.mean(np.abs(r - 1) < 0.2):.1%}"})
tab_jl = pd.DataFrame(lignes)
print(tab_jl.to_string(index=False))
print("bornes de la bibliothèque (n = 1797) : epsilon 0,5 ->", johnson_lindenstrauss_min_dim(1797, eps=0.5), "| epsilon 0,2 ->", johnson_lindenstrauss_min_dim(1797, eps=0.2))
fig, ax = plt.subplots(figsize=(6.0, 3.1))
ax.boxplot([ratios[k] for k in ratios], positions=range(len(ratios)), widths=0.6, showfliers=False, boxprops=dict(color=BLEU), medianprops=dict(color=ORANGE), whiskerprops=dict(color=MUET), capprops=dict(color=MUET))
ax.axhline(1, color=ROUGE, lw=0.9, ls="--"); ax.set_xticks(range(len(ratios))); ax.set_xticklabels(list(ratios))
ax.set_xlabel("dimension $k$ de la projection aléatoire"); ax.set_ylabel("distance après / avant"); ax.set_title("Chiffres manuscrits : conservation des distances", fontsize=9)
plt.tight_layout(); save(fig, "ch03-jl.png")
```
<!--sortie-->
```text
  k  ratio moyen  écart-type  5 % - 95 % paires à ±20 %
  5        0.944       0.286 0.49 - 1.43          48.9%
 10        0.978       0.202 0.65 - 1.32          66.7%
 20        0.978       0.148 0.74 - 1.23          81.7%
 40        0.963       0.096 0.81 - 1.12          95.0%
 64        0.968       0.075 0.85 - 1.09          98.7%
100        0.970       0.062 0.87 - 1.07          99.7%
200        0.965       0.046 0.89 - 1.04         100.0%
bornes de la bibliothèque (n = 1797) : epsilon 0,5 -> 359 | epsilon 0,2 -> 1729
figure : ch03-jl.png
```

```python hide-code
print(tab_jl.to_string(index=False))
print("bornes de la bibliothèque (n = 1797) : epsilon 0,5 ->", johnson_lindenstrauss_min_dim(1797, eps=0.5), "| epsilon 0,2 ->", johnson_lindenstrauss_min_dim(1797, eps=0.2))
```
<!--sortie-->
```text
  k  ratio moyen  écart-type  5 % - 95 % paires à ±20 %
  5        0.944       0.286 0.49 - 1.43          48.9%
 10        0.978       0.202 0.65 - 1.32          66.7%
 20        0.978       0.148 0.74 - 1.23          81.7%
 40        0.963       0.096 0.81 - 1.12          95.0%
 64        0.968       0.075 0.85 - 1.09          98.7%
100        0.970       0.062 0.87 - 1.07          99.7%
200        0.965       0.046 0.89 - 1.04         100.0%
bornes de la bibliothèque (n = 1797) : epsilon 0,5 -> 359 | epsilon 0,2 -> 1729
```

![Rapport entre la distance après et avant projection aléatoire, pour 1 797 chiffres et des projections de dimension $k$ de 5 à 200 : les boîtes se resserrent autour de 1 quand $k$ augmente.](figures/ch03-jl.png)

La borne théorique exige $k\ge359$ pour $\varepsilon=0{,}5$ et $k\ge1\,729$ pour $\varepsilon=0{,}2$, c'est-à-dire **plus que les 64 pixels d'origine** : elle n'est utile qu'en très grande dimension. Dans la pratique, la conservation est bien meilleure : avec $k=40$, $95{,}0\ \%$ des distances sont conservées à $\pm20\ \%$, avec $k=64$ $98{,}7\ \%$, et avec $k=200$ toutes. La moyenne des rapports est légèrement inférieure à $1$ (entre $0{,}94$ et $0{,}98$ selon $k$) : c'est la distance, et non son carré, qui est mesurée, et l'inégalité de Jensen fait $\mathbb E\sqrt X\le\sqrt{\mathbb EX}$.

> 💡 **Quand les projections aléatoires servent-elles ?** Quand $p$ est énorme (dizaines de milliers de colonnes), parce qu'elles sont **instantanées**, ne dépendent d'aucune donnée (on peut projeter un nouveau point sans ré-ajuster), et conservent les distances nécessaires aux méthodes de voisinage. Pour comprendre des données de dimension modérée, l'ACP reste préférable : elle choisit les directions **qui comptent**.

### 3.2.7 Combien de dimensions garder ? Et l'idée de variété

Il n'existe pas de règle universelle ; on combine trois indices.

1. **La variance gardée** : un seuil (80 %, 90 %, 95 %) ou un coude sur le graphique cumulé. Rapide, mais le seuil est arbitraire.
2. **La reconstruction** : l'erreur relative de reconstruction vaut un moins la variance gardée (Eckart–Young) ; on la compare à ce qu'on tolère.
3. **L'utilité en aval** : on mesure la performance de la tâche finale (la précision d'un classifieur, la qualité d'un regroupement) en fonction du nombre de dimensions, **par validation croisée** (section 1.2), et on s'arrête quand elle plafonne. Sur les chiffres, la précision plafonne vers $20$ composantes : c'est le critère qui compte, parce qu'il mesure ce qu'on veut en faire.

Le volume II (section 3.1.6) mentionne aussi l'analyse parallèle, qui compare les valeurs propres à celles de données sans structure : c'est la même logique de « référence sans structure » que celle de 3.1.3.

**L'hypothèse de variété.** Pourquoi une compression est-elle possible ? Parce que les données réelles vivent souvent au voisinage d'une **variété** de faible dimension : une surface (courbe, repliée) plongée dans un espace de grande dimension. Le célèbre « rouleau suisse » en est l'illustration : des points sur une feuille enroulée, dans un espace à 3 dimensions, alors que la feuille est de dimension 2. L'ACP, qui ne sait projeter que sur un plan, **écrase les couches du rouleau les unes sur les autres** ; une méthode qui respecte les **distances le long de la surface** (Isomap, qui déroule la variété à partir du graphe des plus proches voisins) le déplie. Les méthodes t-SNE et UMAP (section 3.4) reposent sur cette même hypothèse.

```python hide
from sklearn.datasets import make_swiss_roll
from sklearn.manifold import Isomap
S, tt = make_swiss_roll(1000, noise=0.05, random_state=0)
p2 = PCA(2).fit_transform(S); iso = Isomap(n_neighbors=10).fit_transform(S)
fig = plt.figure(figsize=(10, 3.2))
a3 = fig.add_subplot(1, 3, 1, projection="3d"); a3.scatter(S[:, 0], S[:, 1], S[:, 2], c=tt, cmap="viridis", s=5); a3.set_title("Rouleau suisse (3 dimensions)", fontsize=9)
a3.view_init(elev=10, azim=-70)
for k, (M, titre) in enumerate(((p2, "ACP : couches écrasées"), (iso, "Isomap : variété dépliée")), start=2):
    a = fig.add_subplot(1, 3, k); a.scatter(M[:, 0], M[:, 1], c=tt, cmap="viridis", s=5); a.set_title(titre, fontsize=9); a.grid(False)
plt.tight_layout(); save(fig, "ch03-rouleau.png")
```
<!--sortie-->
```text
figure : ch03-rouleau.png
```

![Le rouleau suisse en 3 dimensions, sa projection par ACP (les couches se recouvrent) et son dépliage par Isomap (la couleur, qui repère la position le long du rouleau, varie régulièrement).](figures/ch03-rouleau.png)

### 3.2.8 Réduire avant de classer : sur les clients de la boutique

Revenons aux 12 000 clients. Une pratique répandue consiste à **réduire** les sept variables par ACP avant de lancer k-means. Est-ce neutre ?

```python hide
p7 = PCA().fit(Z)
print("variance par composante :", p7.explained_variance_ratio_.round(3))
load = pd.DataFrame(p7.components_[:3].T, index=["âge", "commandes", "montant (log)", "récence", "part promo", "ouverture e-mail", "promos reçues"], columns=["CP1", "CP2", "CP3"]).round(2)
print(load.to_string())
lignes = []
for m in (2, 3, 4, 5, 7):
    A = p7.transform(Z)[:, :m]
    lignes.append({"composantes gardées": m, "variance gardée": round(p7.explained_variance_ratio_[:m].sum(), 3), "ARI avec la vérité (k=4)": round(adjusted_rand_score(c["segment_vrai"], KMeans(4, n_init=10, random_state=0).fit_predict(A)), 3)})
tab_cl = pd.DataFrame(lignes)
print(tab_cl.to_string(index=False))
fig, ax = plt.subplots(figsize=(4.6, 4.2))
for j in range(7):
    ax.arrow(0, 0, p7.components_[0, j] * 2.2, p7.components_[1, j] * 2.2, color=BLEU, head_width=0.05, length_includes_head=True, lw=1.2)
    dec = {"part promo": (0.28, 0.02), "promos reçues": (-0.30, 0.0), "commandes": (0.05, 0.16), "montant (log)": (0.12, -0.14)}.get(load.index[j], (0.0, 0.0))
    ax.text(p7.components_[0, j] * 2.45 + dec[0], p7.components_[1, j] * 2.45 + dec[1], load.index[j], fontsize=8, ha="center", va="center", color=ENCRE2)
ax.set_xlim(-1.6, 1.6); ax.set_ylim(-1.6, 1.6); ax.set_xlabel(f"CP1 ({p7.explained_variance_ratio_[0]:.0%})"); ax.set_ylabel(f"CP2 ({p7.explained_variance_ratio_[1]:.0%})")
ax.set_title("Clients : directions des variables dans le plan CP1-CP2", fontsize=9); ax.set_aspect("equal")
plt.tight_layout(); save(fig, "ch03-acp-boutique.png")
```
<!--sortie-->
```text
variance par composante : [0.373 0.268 0.121 0.096 0.075 0.045 0.023]
                   CP1   CP2   CP3
âge               0.04 -0.43  0.80
commandes         0.47 -0.20 -0.10
montant (log)     0.52 -0.27 -0.22
récence          -0.50  0.15  0.22
part promo        0.25  0.58  0.13
ouverture e-mail  0.39  0.16  0.46
promos reçues     0.21  0.57  0.14
 composantes gardées  variance gardée  ARI avec la vérité (k=4)
                   2            0.641                     0.480
                   3            0.762                     0.489
                   4            0.857                     0.502
                   5            0.932                     0.479
                   7            1.000                     0.487
figure : ch03-acp-boutique.png
```

```python hide-code
print(tab_cl.to_string(index=False))
print(load.to_string())
```
<!--sortie-->
```text
 composantes gardées  variance gardée  ARI avec la vérité (k=4)
                   2            0.641                     0.480
                   3            0.762                     0.489
                   4            0.857                     0.502
                   5            0.932                     0.479
                   7            1.000                     0.487
                   CP1   CP2   CP3
âge               0.04 -0.43  0.80
commandes         0.47 -0.20 -0.10
montant (log)     0.52 -0.27 -0.22
récence          -0.50  0.15  0.22
part promo        0.25  0.58  0.13
ouverture e-mail  0.39  0.16  0.46
promos reçues     0.21  0.57  0.14
```

![Cercle des corrélations de l'ACP sur les sept variables de comportement : la première composante oppose récence et activité, la deuxième regroupe les variables liées aux promotions.](figures/ch03-acp-boutique.png)

La première composante ($37\ \%$ de la variance) oppose la **récence** à l'**activité** (nombre de commandes, montant, ouverture des e-mails) : c'est un axe « client actif contre client endormi ». La deuxième ($27\ \%$) regroupe `part_achats_promo` et `nb_promos_recues_12m` : un axe « sensibilité aux promotions ». Garder $4$ composantes ($85{,}7\ \%$ de la variance) donne un ARI de $0{,}502$ avec la vérité cachée, contre $0{,}487$ avec les $7$ variables : la réduction **ne détruit pas** la structure et la débruite même un peu. Avec seulement $2$ composantes, on retombe à $0{,}480$. La leçon : la réduction n'est pas neutre, et son effet se **mesure** avec les mêmes épreuves que la classification (3.1), au lieu de se supposer.

> ✅ **À retenir (réduction de dimension).**
> - En grande dimension, les distances se resserrent (dispersion relative en $1/\sqrt d$) : les méthodes de voisinage souffrent, d'où l'intérêt de réduire.
> - L'ACP garde la variance, et l'erreur relative de reconstruction vaut **un moins la variance gardée** (Eckart–Young) ; le bon nombre de composantes se choisit par **l'utilité en aval**, validée par validation croisée.
> - L'**ACP à noyau** capte des structures non linéaires ; la **SVD tronquée** évite de centrer (données parcimonieuses) ; la **NMF** donne des composantes **additives et lisibles** ; les **projections aléatoires** conservent les distances (Johnson–Lindenstrauss) à moindre coût quand $p$ est énorme.
> - Les données réelles vivent souvent près d'une **variété** de faible dimension : c'est ce qui rend la réduction possible, et ce que t-SNE et UMAP cherchent à déplier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.4 et 3.8, exercices 3.6 à 3.8.
