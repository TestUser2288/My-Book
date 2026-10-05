## 1.4 La fiche de notations

> 💡 **À quoi sert cette fiche ?** Les livres de data science sont pleins de symboles. Le but n'est pas de les apprendre par cœur, mais de **savoir où regarder** quand l'un d'eux vous bloque. Gardez cette page ouverte pendant la lecture de tous les volumes.

### 1.4.1 Conventions typographiques

| Ce que vous voyez | Ce que cela désigne | Exemple |
|---|---|---|
| Lettre minuscule italique : $x$, $a$, $\eta$ | un **nombre** (scalaire) | $x = 3{,}5$ |
| Minuscule grasse : $\mathbf{x}$, $\mathbf{y}$, $\boldsymbol{\theta}$ | un **vecteur** (colonne par défaut) | $\mathbf{x} = (1, 2, 3)^\top$ |
| Majuscule grasse : $\mathbf{A}$, $\mathbf{X}$ | une **matrice** | $\mathbf{X} \in \mathbb{R}^{n\times p}$ |
| Majuscule italique : $X$, $Y$ | (au chapitre 2) une **variable aléatoire** | $X$ = montant d'un panier |
| Chapeau : $\hat{y}$, $\hat{\theta}$ | une valeur **estimée** ou **prédite** | $\hat{y}_i$ = prédiction pour $i$ |
| Barre : $\bar{x}$ | la **moyenne** | $\bar{x} = \frac1n\sum x_i$ |
| Étoile : $p^\star$, $\theta^\star$ | la valeur **optimale** | $p^\star = 34{,}09$ |
| Exposant $\top$ : $\mathbf{A}^\top$ | la **transposée** (lignes ↔ colonnes) | |
| Exposant $-1$ : $\mathbf{A}^{-1}$ | l'**inverse** d'une matrice | $\mathbf{A}\mathbf{A}^{-1} = \mathbf{I}$ |

> ⚠️ **Attention aux indices.** $x_i$ est le $i$-ème **élément** d'un vecteur, ou la $i$-ème **observation**. $x_{ij}$ est l'élément de la ligne $i$, colonne $j$ d'une matrice. Mathématiquement on compte à partir de **1** ; en Python, à partir de **0** : $x_1$ s'écrit `x[0]`. C'est la source d'erreur n°1 quand on traduit une formule en code.

### 1.4.2 Ensembles et logique

| Symbole | Se lit | Exemple et sens |
|---|---|---|
| $\mathbb{N}, \mathbb{Z}, \mathbb{Q}, \mathbb{R}$ | entiers naturels, relatifs, rationnels, réels | $\mathbb{R}$ = tous les nombres de la droite |
| $\mathbb{R}^n$ | vecteurs de $n$ nombres réels | $\mathbb{R}^3$ : l'espace usuel |
| $\mathbb{R}^{n\times p}$ | matrices à $n$ lignes et $p$ colonnes | un tableau de données |
| $\in$ | « appartient à » | $3 \in \mathbb{N}$ |
| $\subset$ | « est inclus dans » | $\mathbb{N} \subset \mathbb{R}$ |
| $\cup$, $\cap$ | union, intersection | $A \cup B$ : dans $A$ **ou** $B$ |
| $\emptyset$ | ensemble vide | |
| $\forall$ | « pour tout » | $\forall x \in \mathbb{R},\; x^2 \ge 0$ |
| $\exists$ | « il existe » | $\exists x,\; x^2 = 2$ |
| $\Rightarrow$ | « implique » | $x > 2 \Rightarrow x > 1$ |
| $\Leftrightarrow$ | « si et seulement si » | |
| $:=$ | « est défini comme » | $f(x) := x^2$ |
| $\approx$, $\propto$ | environ égal ; proportionnel à | |

### 1.4.3 Sommes, produits, fonctions

| Symbole | Sens | Équivalent NumPy |
|---|---|---|
| $\sum_{i=1}^n x_i$ | $x_1 + x_2 + \dots + x_n$ | `x.sum()` |
| $\prod_{i=1}^n x_i$ | $x_1 \times x_2 \times \dots \times x_n$ | `x.prod()` |
| $\bar{x} = \frac1n\sum x_i$ | moyenne | `x.mean()` |
| $\max$, $\min$ | plus grande, plus petite valeur | `x.max()`, `x.min()` |
| $\arg\min_\theta f(\theta)$ | **l'argument** $\theta$ qui rend $f$ minimale | `np.argmin(f_values)` |
| $\arg\max$ | idem pour le maximum | `np.argmax` |
| $\lvert x\rvert$ | valeur absolue | `np.abs(x)` |
| $\lfloor x\rfloor$, $\lceil x\rceil$ | partie entière inférieure, supérieure | `np.floor`, `np.ceil` |
| $\exp(x) = e^x$, $\ln x$ | exponentielle, log népérien | `np.exp`, `np.log` |
| $\mathbb{1}[\text{cond}]$ | vaut 1 si la condition est vraie, 0 sinon | `(cond).astype(int)` |
| $f: A\to B$ | $f$ prend ses valeurs de $A$ vers $B$ | |
| $f\circ g$ | composition : $(f\circ g)(x) = f(g(x))$ | |
| $\lim_{x\to a} f(x)$ | limite | |
| $\binom{n}{k}$ | « $k$ parmi $n$ » | `math.comb(n, k)` |
| $n!$ | factorielle | `math.factorial(n)` |

### 1.4.4 Algèbre linéaire et analyse

| Symbole | Sens | Équivalent NumPy |
|---|---|---|
| $\mathbf{u}\cdot\mathbf{v} = \mathbf{u}^\top\mathbf{v}$ | produit scalaire | `u @ v` |
| $\lVert\mathbf{v}\rVert$ ou $\lVert\mathbf{v}\rVert_2$ | norme euclidienne $\sqrt{\sum v_i^2}$ | `np.linalg.norm(v)` |
| $\lVert\mathbf{v}\rVert_1$ | norme 1 : $\sum\lvert v_i\rvert$ | `np.linalg.norm(v, 1)` |
| $\mathbf{A}\mathbf{B}$ | produit matriciel | `A @ B` |
| $\mathbf{A}^\top$ | transposée | `A.T` |
| $\mathbf{A}^{-1}$ | inverse | `np.linalg.inv(A)` (ou mieux : `solve`) |
| $\mathbf{I}$ | matrice identité | `np.eye(n)` |
| $\det\mathbf{A}$ | déterminant | `np.linalg.det(A)` |
| $\operatorname{rang}\mathbf{A}$ | nombre de colonnes indépendantes | `np.linalg.matrix_rank(A)` |
| $\operatorname{tr}\mathbf{A}$ | trace (somme de la diagonale) | `np.trace(A)` |
| $\lambda$, $\mathbf{v}$ | valeur propre, vecteur propre : $\mathbf{A}\mathbf{v} = \lambda\mathbf{v}$ | `np.linalg.eig(A)` |
| $\mathbf{A} = \mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^\top$ | décomposition en valeurs singulières | `np.linalg.svd(A)` |
| $f'(x)$ ou $\dfrac{df}{dx}$ | dérivée | |
| $\dfrac{\partial f}{\partial x_j}$ | dérivée partielle | |
| $\nabla f$ | gradient (vecteur des dérivées partielles) | |
| $\nabla^2 f$ ou $\mathbf{H}$ | hessienne (matrice des dérivées secondes) | |
| $\int_a^b f(x)\,dx$ | intégrale (aire sous la courbe) | `scipy.integrate.quad` |

### 1.4.5 L'alphabet grec en data science

Les lettres grecques reviennent partout. Voici celles que vous rencontrerez, avec leur usage **habituel** (pas une règle absolue).

| Lettre | Nom | Usage courant |
|---|---|---|
| $\alpha$ | alpha | niveau de risque d'un test ; ordonnée à l'origine ; paramètre de régularisation |
| $\beta$ | bêta | coefficients d'une régression |
| $\gamma$ | gamma | pas d'apprentissage (parfois) ; fonction Gamma |
| $\delta$, $\Delta$ | delta | une petite variation ; $\Delta x$ = écart |
| $\varepsilon$ | epsilon | une très petite quantité ; l'**erreur** (bruit) d'un modèle |
| $\eta$ | êta | **pas d'apprentissage** (learning rate) |
| $\theta$ | thêta | **paramètres** d'un modèle (ce que l'on apprend) |
| $\lambda$ | lambda | valeur propre ; multiplicateur de Lagrange ; taux d'une loi exponentielle ; force de la régularisation |
| $\mu$ | mu | **moyenne** d'une loi (théorique) |
| $\nu$ | nu | degrés de liberté |
| $\pi$ | pi | 3,14159… ; ou une probabilité |
| $\rho$ | rhô | coefficient de **corrélation** |
| $\sigma$, $\Sigma$ | sigma | **écart-type** ($\sigma$) ; matrice de covariance ($\boldsymbol\Sigma$) ; ⚠️ $\sum$ est la somme, pas la même lettre |
| $\tau$ | tau | un seuil |
| $\phi$, $\varphi$ | phi | densité de la loi normale ($\varphi$) ; une fonction de transformation |
| $\Phi$ | Phi majuscule | fonction de répartition de la loi normale |
| $\chi^2$ | khi-deux | loi et test du khi-deux |
| $\omega$, $\Omega$ | oméga | l'ensemble des issues possibles ($\Omega$) |

> 🧪 **Astuce pour lire une formule inconnue.** (1) Repérez d'abord ce qui est un nombre, un vecteur, une matrice (grâce à la typographie). (2) Cherchez ce qui est *sommé* ou *minimisé*. (3) Remplacez les symboles par un exemple chiffré minuscule ($n = 3$). Une formule devient presque toujours claire sur un exemple à trois éléments.

### 1.4.6 Exemple : lire une formule du début à la fin

Voici la fonction de perte des moindres carrés, que vous connaissez maintenant :

$$\hat{\boldsymbol\theta} = \arg\min_{\boldsymbol\theta}\; \sum_{i=1}^{n}\bigl(y_i - \mathbf{x}_i^\top\boldsymbol\theta\bigr)^2 .$$

Lecture mot à mot : « le vecteur de paramètres estimé $\hat{\boldsymbol\theta}$ est **l'argument $\boldsymbol\theta$ qui minimise** la somme, sur les $n$ observations, du **carré de l'écart** entre la valeur observée $y_i$ et la prédiction $\mathbf{x}_i^\top\boldsymbol\theta$ ». Et en Python :

```python
import numpy as np
x = np.array([1.0, 2.0, 3.0]); y = np.array([2.0, 3.0, 5.0])
X = np.column_stack([x, np.ones_like(x)])
theta_chapeau = np.linalg.solve(X.T @ X, X.T @ y)
print("theta chapeau =", theta_chapeau.round(4))
print("somme des carrés =", round(((y - X @ theta_chapeau) ** 2).sum(), 4))
```
<!--sortie-->
```text
theta chapeau = [1.5    0.3333]
somme des carrés = 0.1667
```

Une formule, une phrase, trois lignes de code : c'est cette triple lecture qui vous rendra autonome.
