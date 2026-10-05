### 1.1.3 Valeurs propres et vecteurs propres : les directions privilégiées

> 💡 **Intuition.** Une matrice carrée agit sur le plan comme une machine à déformer : elle étire, elle fait pivoter, elle cisaille. Si vous lui donnez un vecteur, elle en renvoie un autre, en général dans une **autre direction**.
>
> Mais il existe parfois des vecteurs « têtus » : la machine les **étire (ou les écrase) sans les faire tourner**. Ce sont les **vecteurs propres**. Le facteur d'étirement est la **valeur propre**.

Formellement, un vecteur $\mathbf{v} \neq \mathbf{0}$ est un **vecteur propre** de la matrice carrée $\mathbf{A}$ s'il existe un nombre $\lambda$ (la **valeur propre**) tel que

$$\mathbf{A}\mathbf{v} = \lambda\,\mathbf{v}.$$

#### Un exemple que l'on vérifie à la main

Prenons $\mathbf{A} = \begin{pmatrix}2&1\\1&2\end{pmatrix}$ et essayons trois vecteurs.

> 🧪 **Test 1.** $\mathbf{v} = (1, 1)$ : $\mathbf{A}\mathbf{v} = (2\cdot 1 + 1\cdot 1,\; 1\cdot 1 + 2\cdot 1) = (3, 3) = 3\,\mathbf{v}$. ✔ La direction est conservée, le vecteur est triplé : **vecteur propre, valeur propre 3**.
>
> **Test 2.** $\mathbf{w} = (1, -1)$ : $\mathbf{A}\mathbf{w} = (2 - 1,\; 1 - 2) = (1, -1) = 1\cdot\mathbf{w}$. ✔ **Vecteur propre, valeur propre 1.**
>
> **Test 3.** $\mathbf{u} = (1, 0)$ : $\mathbf{A}\mathbf{u} = (2, 1)$. Ce n'est pas un multiple de $(1, 0)$ : la direction a changé. ✘ **Pas un vecteur propre.**

La figure ci-dessous montre ce que fait $\mathbf{A}$ sur tous les vecteurs de longueur 1 (le cercle unité) : elle le transforme en une **ellipse**, allongée d'un facteur 3 dans la direction $(1,1)$ et conservée (facteur 1) dans la direction $(1,-1)$. Les axes de l'ellipse sont exactement les vecteurs propres.

![Action de la matrice A sur le cercle unité : l'ellipse est étirée d'un facteur 3 le long de (1,1) et inchangée le long de (1,−1).](figures/ch01-ellipse-propre.png)

#### Comment trouver les valeurs propres ?

On cherche les $\lambda$ pour lesquels l'équation $\mathbf{A}\mathbf{v} = \lambda\mathbf{v}$ admet une solution non nulle. On la réécrit $(\mathbf{A} - \lambda\mathbf{I})\mathbf{v} = \mathbf{0}$. Un système homogène a une solution non nulle exactement lorsque sa matrice est **singulière**, c'est-à-dire lorsque son déterminant est nul :

$$\det(\mathbf{A} - \lambda\mathbf{I}) = 0.$$

C'est l'**équation caractéristique**. Pour notre matrice :

$$\det\begin{pmatrix}2-\lambda & 1\\ 1 & 2-\lambda\end{pmatrix} = (2-\lambda)^2 - 1 = \lambda^2 - 4\lambda + 3 = (\lambda - 1)(\lambda - 3).$$

Les valeurs propres sont donc $\lambda_1 = 3$ et $\lambda_2 = 1$. On trouve ensuite les vecteurs propres en résolvant $(\mathbf{A} - \lambda\mathbf{I})\mathbf{v} = \mathbf{0}$ :

- pour $\lambda = 3$ : $\begin{pmatrix}-1&1\\1&-1\end{pmatrix}\mathbf{v} = \mathbf{0}$ donne $v_1 = v_2$, soit $\mathbf{v} = (1, 1)$ (à un multiple près) ;
- pour $\lambda = 1$ : $\begin{pmatrix}1&1\\1&1\end{pmatrix}\mathbf{v} = \mathbf{0}$ donne $v_2 = -v_1$, soit $\mathbf{w} = (1, -1)$.

> ✅ **Deux contrôles rapides.** La **somme** des valeurs propres vaut la **trace** de la matrice (somme de la diagonale) : $3 + 1 = 4 = 2 + 2$. Le **produit** des valeurs propres vaut le **déterminant** : $3 \times 1 = 3 = 2\cdot 2 - 1\cdot 1$. Utile pour détecter une erreur de calcul.

```python
import numpy as np

A = np.array([[2, 1], [1, 2]])
valeurs, vecteurs = np.linalg.eigh(A)     # eigh : pour les matrices symétriques
print("valeurs propres :", valeurs)
print("vecteurs propres (en colonnes) :\n", vecteurs.round(4))
```
<!--sortie-->
```text
valeurs propres : [1. 3.]
vecteurs propres (en colonnes) :
 [[-0.7071  0.7071]
 [ 0.7071  0.7071]]
```

```python hide
print("trace =", np.trace(A), " somme des valeurs propres =", valeurs.sum())
print("det   =", round(np.linalg.det(A), 4), " produit des valeurs propres =", valeurs.prod())
```
<!--sortie-->
```text
trace = 4  somme des valeurs propres = 4.0
det   = 3.0  produit des valeurs propres = 3.0
```

NumPy range les valeurs propres par ordre croissant et renvoie des vecteurs **de longueur 1** (le signe est arbitraire : si $\mathbf{v}$ est propre, $-\mathbf{v}$ l'est aussi).

#### Le cas des matrices symétriques

Une matrice est **symétrique** si $\mathbf{A}^\top = \mathbf{A}$ (la matrice de similarité de la section précédente en est une, et la matrice de covariance, que nous rencontrerons dans un instant, aussi). Ces matrices ont une propriété exceptionnelle :

> **Théorème spectral.** Une matrice symétrique réelle de taille $p\times p$ a $p$ valeurs propres **réelles** et on peut choisir pour elle $p$ vecteurs propres **orthogonaux** deux à deux (et de longueur 1). Si $\mathbf{V}$ est la matrice qui les contient en colonnes et $\boldsymbol{\Lambda}$ la matrice diagonale des valeurs propres, alors
>
> $$\mathbf{A} = \mathbf{V}\boldsymbol{\Lambda}\mathbf{V}^\top.$$

Nous admettons l'existence (la preuve complète se trouve dans tout cours d'algèbre linéaire), mais voici pourquoi les vecteurs propres associés à des valeurs propres différentes sont orthogonaux :

> 📐 **Démonstration : orthogonalité.** Soient $\mathbf{A}\mathbf{v}_1 = \lambda_1\mathbf{v}_1$ et $\mathbf{A}\mathbf{v}_2 = \lambda_2\mathbf{v}_2$ avec $\lambda_1 \neq \lambda_2$ et $\mathbf{A}$ symétrique. Calculons de deux façons le nombre $(\mathbf{A}\mathbf{v}_1)\cdot\mathbf{v}_2$ :
>
> - directement : $(\mathbf{A}\mathbf{v}_1)\cdot\mathbf{v}_2 = \lambda_1\,(\mathbf{v}_1\cdot\mathbf{v}_2)$ ;
> - en déplaçant $\mathbf{A}$ : comme $\mathbf{A}$ est symétrique, $(\mathbf{A}\mathbf{v}_1)\cdot\mathbf{v}_2 = \mathbf{v}_1^\top\mathbf{A}^\top\mathbf{v}_2 = \mathbf{v}_1^\top\mathbf{A}\mathbf{v}_2 = \mathbf{v}_1\cdot(\mathbf{A}\mathbf{v}_2) = \lambda_2\,(\mathbf{v}_1\cdot\mathbf{v}_2)$.
>
> En soustrayant : $(\lambda_1 - \lambda_2)\,(\mathbf{v}_1\cdot\mathbf{v}_2) = 0$. Comme $\lambda_1 \neq \lambda_2$, on a $\mathbf{v}_1\cdot\mathbf{v}_2 = 0$ : les vecteurs sont orthogonaux. $\blacksquare$
>
> Dans notre exemple : $(1,1)\cdot(1,-1) = 1 - 1 = 0$. ✔

Une conséquence pratique de $\mathbf{A} = \mathbf{V}\boldsymbol{\Lambda}\mathbf{V}^\top$ est que les **puissances** deviennent triviales : $\mathbf{A}^k = \mathbf{V}\boldsymbol{\Lambda}^k\mathbf{V}^\top$, et élever une matrice diagonale à la puissance $k$, c'est simplement élever ses éléments. (Nous nous en servirons pour les chaînes de Markov dans la section ➕ du chapitre 2.)

```python hide
k = 5
via_diagonalisation = vecteurs @ np.diag(valeurs**k) @ vecteurs.T
directement = np.linalg.matrix_power(A, k)
print("A^5 par diagonalisation :\n", via_diagonalisation.round(6))
print("A^5 directement :\n", directement)
```
<!--sortie-->
```text
A^5 par diagonalisation :
 [[122. 121.]
 [121. 122.]]
A^5 directement :
 [[122 121]
 [121 122]]
```

#### Un nuage de clients : la direction principale

La gérante mesure, pour 200 clients, le nombre de visites mensuelles sur son site et leur dépense mensuelle. Elle soupçonne que les deux sont liées. On **standardise** chaque variable (on retranche la moyenne et on divise par l'écart-type, pour qu'elles aient la même échelle, comme promis dans la section sur les vecteurs), puis on calcule la **matrice de covariance** des deux variables standardisées :

$$\mathbf{C} = \begin{pmatrix} 1 & r \\ r & 1 \end{pmatrix},$$

où $r$ est la corrélation entre les deux variables. C'est une matrice symétrique : le théorème spectral s'applique, et le calcul se fait **à la main** pour n'importe quel $r > 0$.

> 🧪 **À la main.** L'équation caractéristique est $\det(\mathbf{C} - \lambda\mathbf{I}) = (1-\lambda)^2 - r^2 = 0$, donc $\lambda = 1 \pm r$.
>
> - Pour $\lambda_1 = 1 + r$ : $\begin{pmatrix}-r & r\\ r & -r\end{pmatrix}\mathbf{v} = \mathbf{0}$ donne $v_1 = v_2$, soit la direction $\frac{1}{\sqrt2}(1, 1)$ : la **diagonale**.
> - Pour $\lambda_2 = 1 - r$ : on trouve $\frac{1}{\sqrt2}(1, -1)$ : l'autre diagonale, perpendiculaire à la première.
>
> Quelle que soit la corrélation, les axes principaux de deux variables standardisées sont donc les deux diagonales, et la part de variance portée par le premier axe vaut $\dfrac{1+r}{2}$. Pour $r = 0{,}9$, cela fait $95\ \%$.

```python hide
rng = np.random.default_rng(42)
n = 200
visites = rng.normal(6, 2, n)                        # visites par mois
depense = 15 * visites + rng.normal(0, 12, n)        # dépense en €, liée aux visites

def standardise(x):
    return (x - x.mean()) / x.std(ddof=1)

Z = np.column_stack([standardise(visites), standardise(depense)])
C = np.cov(Z.T)                                      # matrice de covariance 2 x 2
print("Matrice de covariance :\n", C.round(3))

valeurs, vecteurs = np.linalg.eigh(C)
print("Valeurs propres :", valeurs.round(3))
print("Part de la variance expliquée :", (valeurs / valeurs.sum()).round(3))
print("Direction principale :", np.abs(vecteurs[:, -1]).round(3))
```
<!--sortie-->
```text
Matrice de covariance :
 [[1.    0.903]
 [0.903 1.   ]]
Valeurs propres : [0.097 1.903]
Part de la variance expliquée : [0.049 0.951]
Direction principale : [0.707 0.707]
```

![Nuage des 200 clients (variables standardisées) et son axe principal : le long de la diagonale, le nuage est étiré ; perpendiculairement, il est mince.](figures/ch01-nuage-clients.png)

**Sur les données simulées.** La corrélation mesurée vaut environ 0,90 : la plus grande valeur propre (environ 1,90) correspond à la direction $(0{,}71;\; 0{,}71)$, la diagonale : c'est l'axe le long duquel le nuage de clients est le plus étiré, l'axe « client actif et dépensier ». Elle capte environ **95 %** de toute la variabilité. La seconde (0,10) correspond à la direction perpendiculaire, qui ne représente que les écarts « dépense inhabituelle pour ce nombre de visites ».

Autrement dit, on peut résumer ces deux variables par **une seule** (la position le long de l'axe principal), en ne perdant que 5 % de l'information. C'est le principe de l'**analyse en composantes principales** (ACP), que nous étudierons en détail au volume II : *trouver les directions de plus grande variance, ce sont les vecteurs propres de la matrice de covariance*.

> ✅ **À retenir (valeurs propres).**
>
> - $\mathbf{A}\mathbf{v} = \lambda\mathbf{v}$ : un vecteur propre garde sa direction, la valeur propre dit de combien il est étiré.
> - On les trouve avec $\det(\mathbf{A} - \lambda\mathbf{I}) = 0$. Somme des valeurs propres = trace ; produit = déterminant.
> - Une matrice symétrique a des valeurs propres réelles et des vecteurs propres orthogonaux ; $\mathbf{A} = \mathbf{V}\boldsymbol{\Lambda}\mathbf{V}^\top$.
> - Les vecteurs propres de la matrice de covariance sont les axes principaux d'un nuage de données.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.3, exercice 1.3.

### 1.1.4 La décomposition en valeurs singulières (SVD)

Les valeurs propres ne sont définies que pour des matrices **carrées**. Or un jeu de données est rarement carré : $n$ individus, $p$ variables, avec $n \neq p$. La **décomposition en valeurs singulières**, ou **SVD** (*Singular Value Decomposition*), étend la même idée à **n'importe quelle matrice**. C'est l'un des outils les plus puissants de toute la data science.

> 💡 **Intuition.** Toute matrice, même rectangulaire, agit en trois temps : **une rotation, un étirement le long des axes, puis une autre rotation**. On écrit :
>
> $$\mathbf{A} = \mathbf{U}\,\boldsymbol{\Sigma}\,\mathbf{V}^\top.$$
>
> Les matrices $\mathbf{U}$ et $\mathbf{V}$ sont des rotations (leurs colonnes sont des vecteurs de longueur 1, orthogonaux entre eux) ; $\boldsymbol{\Sigma}$ est « diagonale » et contient les facteurs d'étirement $\sigma_1 \ge \sigma_2 \ge \dots \ge 0$, appelés **valeurs singulières**.

On peut aussi lire la SVD comme une **somme de couches simples** (« de rang 1 »), classées de la plus importante à la moins importante :

$$\mathbf{A} = \sigma_1\,\mathbf{u}_1\mathbf{v}_1^\top + \sigma_2\,\mathbf{u}_2\mathbf{v}_2^\top + \dots + \sigma_r\,\mathbf{u}_r\mathbf{v}_r^\top.$$

Chaque couche $\mathbf{u}_i\mathbf{v}_i^\top$ est un tableau « produit » : (profil des lignes) × (profil des colonnes). La première couche, celle de plus grande valeur singulière, capture la structure dominante des données ; les suivantes en sont les raffinements.

#### Un exemple minuscule

> 🧪 **Exemple à la main.** Prenons $\mathbf{A} = \begin{pmatrix}1&1\\1&1\end{pmatrix}$ (rang 1 : les deux lignes sont identiques). Calculons $\mathbf{A}^\top\mathbf{A} = \begin{pmatrix}2&2\\2&2\end{pmatrix}$. Ses valeurs propres sont 4 et 0 (trace 4, déterminant 0). La plus grande valeur singulière est donc $\sigma_1 = \sqrt{4} = 2$ et la seconde est $\sigma_2 = 0$. Le vecteur propre associé à 4 est $\mathbf{v}_1 = \frac{1}{\sqrt2}(1, 1)$, et $\mathbf{u}_1 = \mathbf{A}\mathbf{v}_1/\sigma_1 = \frac{1}{\sqrt2}(1,1)$. On vérifie :
>
> $$\sigma_1\mathbf{u}_1\mathbf{v}_1^\top = 2\cdot\tfrac12\begin{pmatrix}1&1\\1&1\end{pmatrix} = \begin{pmatrix}1&1\\1&1\end{pmatrix} = \mathbf{A}. \;\checkmark$$
>
> Une seule valeur singulière non nulle : la matrice n'a qu'**une** couche. Plus généralement, **le nombre de valeurs singulières non nulles est le rang** de la matrice.

> 📐 **Démonstration : d'où viennent les valeurs singulières ?** (l'idée de la construction)
>
> Soit $\mathbf{A} \in \mathbb{R}^{n\times p}$. La matrice $\mathbf{A}^\top\mathbf{A}$ est carrée ($p\times p$), **symétrique**, et **positive** : pour tout vecteur $\mathbf{x}$, $\mathbf{x}^\top\mathbf{A}^\top\mathbf{A}\mathbf{x} = \|\mathbf{A}\mathbf{x}\|^2 \ge 0$. Le théorème spectral nous donne donc des vecteurs propres orthonormés $\mathbf{v}_1, \dots, \mathbf{v}_p$ associés à des valeurs propres $\lambda_i \ge 0$ (elles sont positives car $\lambda_i = \mathbf{v}_i^\top\mathbf{A}^\top\mathbf{A}\mathbf{v}_i = \|\mathbf{A}\mathbf{v}_i\|^2$).
>
> On pose $\sigma_i = \sqrt{\lambda_i}$ et, pour $\sigma_i > 0$, $\mathbf{u}_i = \mathbf{A}\mathbf{v}_i/\sigma_i$. Ces vecteurs $\mathbf{u}_i$ sont **orthonormés** :
>
> $$\mathbf{u}_i\cdot\mathbf{u}_j = \frac{(\mathbf{A}\mathbf{v}_i)^\top(\mathbf{A}\mathbf{v}_j)}{\sigma_i\sigma_j} = \frac{\mathbf{v}_i^\top\mathbf{A}^\top\mathbf{A}\mathbf{v}_j}{\sigma_i\sigma_j} = \frac{\lambda_j\,\mathbf{v}_i\cdot\mathbf{v}_j}{\sigma_i\sigma_j} = \begin{cases}1 & i = j\\ 0 & i\neq j.\end{cases}$$
>
> Enfin, par construction $\mathbf{A}\mathbf{v}_i = \sigma_i\mathbf{u}_i$ : c'est exactement l'égalité $\mathbf{A}\mathbf{V} = \mathbf{U}\boldsymbol{\Sigma}$, qui donne $\mathbf{A} = \mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^\top$. $\blacksquare$

Autrement dit : **les valeurs singulières de $\mathbf{A}$ sont les racines carrées des valeurs propres de $\mathbf{A}^\top\mathbf{A}$**. Le lien avec la section précédente est direct.

#### Approximer une matrice par un nombre réduit de couches

Voici la propriété qui rend la SVD si utile en pratique.

> **Théorème (Eckart-Young).** Parmi toutes les matrices de rang $k$, la meilleure approximation de $\mathbf{A}$ (au sens de la somme des carrés des erreurs) est obtenue en **ne gardant que les $k$ premières couches** de la SVD :
> $$\mathbf{A}_k = \sigma_1\mathbf{u}_1\mathbf{v}_1^\top + \dots + \sigma_k\mathbf{u}_k\mathbf{v}_k^\top.$$
> L'erreur vaut alors $\|\mathbf{A} - \mathbf{A}_k\|_F = \sqrt{\sigma_{k+1}^2 + \dots + \sigma_r^2}$, où $\|\cdot\|_F$ est la racine de la somme des carrés de tous les éléments.

Autrement dit : si les premières valeurs singulières sont grandes et les suivantes minuscules, on peut **jeter** les dernières couches sans presque rien perdre. C'est de la **compression**.

#### Un tableau de ventes : combien de couches faut-il ?

La gérante a les ventes hebdomadaires de 6 produits sur 8 semaines (un tableau de 48 nombres). Les données sont simulées selon une règle simple : *ventes = popularité du produit × effet de la semaine + un peu de bruit*. Une telle structure « produit × saison » doit se retrouver dans la première couche de la SVD : c'est la matrice la plus simple possible, un produit extérieur $\mathbf{u}\mathbf{v}^\top$ (comme dans l'exemple à la main ci-dessus, mais bruitée).

```python hide
rng = np.random.default_rng(7)
popularite = np.array([50, 30, 20, 12, 8, 5.0])                    # un niveau par produit
saison = np.array([1.0, 1.1, 0.9, 1.2, 1.5, 1.4, 1.0, 0.8])       # un effet par semaine
M = (np.outer(popularite, saison) + rng.normal(0, 1.0, (6, 8))).round(0)

print("Tableau des ventes (6 produits x 8 semaines) :")
print(M.astype(int))
```
<!--sortie-->
```text
Tableau des ventes (6 produits x 8 semaines) :
[[50 55 45 59 75 69 50 41]
 [30 32 27 36 45 41 30 25]
 [19 22 16 23 28 28 19 16]
 [12 13  8 14 18 17 10  9]
 [ 7  8  8  9 12 12  7  6]
 [ 5  6  3  6  9  5  6  4]]
```

```python hide
U, s, Vt = np.linalg.svd(M)
print("valeurs singulières :", s.round(2))
part = 100 * s**2 / (s**2).sum()
print("part de l'énergie par couche (%) :", " ".join(f"{x:.2f}" for x in part))

M1 = s[0] * np.outer(U[:, 0], Vt[0])          # approximation avec UNE seule couche
erreur_relative = np.linalg.norm(M - M1) / np.linalg.norm(M)
print("erreur relative de l'approximation de rang 1 :", round(erreur_relative, 4))
print("nombres à stocker : 48 (tableau) contre", 6 + 8 + 1, "(couche 1)")
```
<!--sortie-->
```text
valeurs singulières : [202.05   3.53   3.51   1.81   1.18   0.75]
part de l'énergie par couche (%) : 99.93 0.03 0.03 0.01 0.00 0.00
erreur relative de l'approximation de rang 1 : 0.0271
nombres à stocker : 48 (tableau) contre 15 (couche 1)
```

![Ventes observées (à gauche), approximation par une seule couche (au centre) et ce qui reste (à droite). L'échelle de couleur est la même pour les deux premiers panneaux.](figures/ch01-svd-ventes.png)

**Résultat.** La SVD du tableau donne une première valeur singulière (environ 202) près de soixante fois plus grande que la deuxième (environ 3,5) : **99,9 %** de l'« énergie » du tableau est dans une seule couche. Une approximation de rang 1, qui ne stocke que 15 nombres au lieu de 48, reproduit le tableau avec une erreur relative d'environ 2,7 %. Le reste (les couches 2 à 6) est du bruit.

La SVD a donc **retrouvé toute seule** la structure « popularité × saison » que nous avions mise dans les données, sans qu'on lui dise de la chercher. Vous venez de voir le principe de la **réduction de dimension** et celui des **systèmes de recommandation** par factorisation de matrices, deux sujets que nous développerons aux volumes suivants.

> ✅ **À retenir (SVD).**
>
> - Toute matrice se décompose en $\mathbf{A} = \mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^\top$ : rotation, étirement, rotation.
> - Les valeurs singulières mesurent l'importance de chaque couche ; leur nombre non nul est le rang.
> - Garder les $k$ premières couches donne la meilleure approximation de rang $k$ (Eckart-Young) : c'est la base de la compression, du débruitage et de l'ACP.
> - L'ACP n'est rien d'autre que la SVD des données centrées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.4.
