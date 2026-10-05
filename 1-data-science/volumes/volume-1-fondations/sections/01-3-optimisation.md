## 1.3 Optimisation : trouver le meilleur choix

Presque tout problème de data science se ramène à la même question : **parmi toutes les valeurs possibles des paramètres de mon modèle, laquelle est la meilleure ?** Et « meilleure » veut dire : celle qui **minimise une erreur** (ou maximise un gain). C'est la troisième phrase de notre épigraphe : *apprendre, c'est minimiser une erreur*. Tout ce que nous avons vu dans ce chapitre (vecteurs, matrices, dérivées, gradients) converge ici.

### 1.3.1 Le problème d'optimisation

Un **problème d'optimisation** consiste à trouver les paramètres $\boldsymbol{\theta}$ qui minimisent une **fonction objectif** $f(\boldsymbol{\theta})$ (on dit aussi *fonction de coût* ou *fonction de perte*) :

$$\boldsymbol{\theta}^\star = \underset{\boldsymbol{\theta}}{\arg\min}\; f(\boldsymbol{\theta}).$$

La notation $\arg\min$ se lit « l'argument qui minimise » : on cherche **où** le minimum est atteint, pas seulement sa valeur. Maximiser $f$ revient à minimiser $-f$ : on peut donc toujours se ramener à une minimisation.

Nous avons déjà rencontré deux problèmes de ce type :

- le bénéfice $P(q)$ de la section 1.2 (une variable, maximisation) ;
- la perte $L(a, b)$ d'une droite ajustée à des points (deux variables, minimisation).

> 💡 **Rappel utile.** Aux points qui annulent le gradient ($\nabla f = \mathbf{0}$), la fonction est « à plat ». Ces points sont des **candidats** : minimum local, maximum local, ou col. La question est de savoir lequel, et surtout de savoir si c'est le **meilleur de tous** (minimum *global*) ou seulement le meilleur dans son voisinage (minimum *local*).

### 1.3.2 La convexité : quand il n'y a qu'une vallée

> 💡 **Intuition.** Imaginez un bol : où que vous posiez une bille, elle roule vers l'unique point le plus bas. Maintenant imaginez un paysage de montagnes avec plusieurs vallées : la bille peut se retrouver coincée dans une petite vallée alors qu'une plus profonde existe ailleurs. Une fonction **convexe** est un bol : **pas de piège possible**.

Formellement, $f$ est **convexe** si, pour deux points quelconques $\mathbf{x}$ et $\mathbf{y}$ et pour tout $t \in [0, 1]$,

$$f\bigl(t\,\mathbf{x} + (1-t)\,\mathbf{y}\bigr) \;\le\; t\,f(\mathbf{x}) + (1-t)\,f(\mathbf{y}).$$

Graphiquement : **la corde qui relie deux points de la courbe est toujours au-dessus de la courbe**. Pour une fonction d'une variable deux fois dérivable, c'est équivalent à $f''(x) \ge 0$ partout.

| Fonction | $f''$ | Convexe ? |
|---|---|---|
| $x^2$ | $2$ | oui |
| $\lvert x\rvert$ | (pas dérivable en 0, mais la corde est au-dessus) | oui |
| $e^x$ | $e^x > 0$ | oui |
| $x^3$ | $6x$ (change de signe) | **non** |
| $\sin x$ | $-\sin x$ (change de signe) | **non** |

La propriété qui rend la convexité précieuse :

> **Théorème.** Si $f$ est convexe, **tout minimum local est un minimum global**.

> 📐 **Démonstration.** Raisonnons par l'absurde. Soit $\mathbf{x}^\star$ un minimum local de $f$, et supposons qu'il existe un point $\mathbf{y}$ avec $f(\mathbf{y}) < f(\mathbf{x}^\star)$. Pour $t \in (0, 1)$, considérons le point $\mathbf{z}_t = (1-t)\,\mathbf{x}^\star + t\,\mathbf{y}$, sur le segment qui joint $\mathbf{x}^\star$ à $\mathbf{y}$. Par convexité,
>
> $$f(\mathbf{z}_t) \le (1-t)\,f(\mathbf{x}^\star) + t\,f(\mathbf{y}) < (1-t)\,f(\mathbf{x}^\star) + t\,f(\mathbf{x}^\star) = f(\mathbf{x}^\star).$$
>
> Or, quand $t \to 0$, le point $\mathbf{z}_t$ se rapproche de $\mathbf{x}^\star$ tout en gardant $f(\mathbf{z}_t) < f(\mathbf{x}^\star)$ : il existe donc des points arbitrairement proches de $\mathbf{x}^\star$ où $f$ est plus petite. Cela contredit le fait que $\mathbf{x}^\star$ est un minimum local. $\blacksquare$

#### La perte des moindres carrés est convexe

Voici le résultat qui justifie pourquoi la régression linéaire est « facile » à optimiser. Pour un modèle linéaire, la perte s'écrit avec une matrice de données $\mathbf{X}$ (une ligne par individu), un vecteur de paramètres $\boldsymbol{\theta}$ et un vecteur de cibles $\mathbf{y}$ :

$$L(\boldsymbol{\theta}) = \|\mathbf{y} - \mathbf{X}\boldsymbol{\theta}\|^2.$$

Son gradient est $\nabla L(\boldsymbol{\theta}) = -2\,\mathbf{X}^\top(\mathbf{y} - \mathbf{X}\boldsymbol{\theta})$ (c'est la forme matricielle de ce que nous avions calculé à la main en 1.2.2), et sa dérivée seconde, la **matrice hessienne**, est $\mathbf{H} = 2\,\mathbf{X}^\top\mathbf{X}$.

> 📐 **Démonstration : la hessienne est « positive », donc $L$ est convexe.** Pour tout vecteur $\mathbf{v}$,
>
> $$\mathbf{v}^\top\mathbf{H}\,\mathbf{v} = 2\,\mathbf{v}^\top\mathbf{X}^\top\mathbf{X}\,\mathbf{v} = 2\,\|\mathbf{X}\mathbf{v}\|^2 \;\ge\; 0.$$
>
> Une hessienne dont toutes les valeurs propres sont positives ou nulles correspond à une fonction convexe (c'est l'analogue en plusieurs variables de $f'' \ge 0$). $\blacksquare$
>
> De plus, si les colonnes de $\mathbf{X}$ sont **indépendantes** (rang plein), alors $\mathbf{X}\mathbf{v} = \mathbf{0}$ n'est possible que pour $\mathbf{v} = \mathbf{0}$ : la hessienne est strictement positive, le bol a un **unique** fond.

On retrouve ici le rang de la section 1.1. Reprenons nos colonnes redondantes (prix HT et prix TTC) : si $\mathbf{X}$ contient les deux, alors $\boldsymbol{\theta} = (1, 0)$ (« on utilise le HT ») et $\boldsymbol{\theta} = (0, 1/1{,}19)$ (« on utilise le TTC divisé par 1,19 ») produisent **exactement les mêmes prédictions** et donc la même perte : le fond du bol est une *rigole*, pas un point. Le minimum existe mais n'est pas unique.

```python
import numpy as np

ht = np.array([40.0, 25.0, 60.0, 15.0])
X_redondant = np.column_stack([ht, 1.19 * ht])
for theta in [(1.0, 0.0), (0.0, 1 / 1.19)]:
    print("theta =", np.round(theta, 4), "-> prédictions :", np.round(X_redondant @ np.array(theta), 4))
```
<!--sortie-->
```text
theta = [1. 0.] -> prédictions : [40. 25. 60. 15.]
theta = [0.     0.8403] -> prédictions : [40. 25. 60. 15.]
```

Pour notre petit exemple de trois points, la hessienne est $2\mathbf{X}^\top\mathbf{X}$ avec $\mathbf{X}$ constituée de la colonne $x = (1,2,3)$ et d'une colonne de 1 :

```python
x = np.array([1.0, 2.0, 3.0])
y = np.array([2.0, 3.0, 5.0])
X = np.column_stack([x, np.ones_like(x)])          # colonnes : x et 1  ->  theta = (a, b)

H = 2 * X.T @ X
print("Hessienne :\n", H)
print("valeurs propres :", np.linalg.eigvalsh(H).round(3))
```
<!--sortie-->
```text
Hessienne :
 [[28. 12.]
 [12.  6.]]
valeurs propres : [ 0.721 33.279]
```

Les deux valeurs propres (0,72 et 33,28) sont positives : $L$ est convexe, avec un unique minimum. Remarquez toutefois qu'elles sont **très inégales** (un rapport de 46). Cela signifie que le bol est très allongé : raide dans une direction, presque plat dans l'autre. Nous allons voir que cela a des conséquences concrètes.

### 1.3.3 La descente de gradient

> 💡 **Intuition.** Vous êtes un randonneur dans le brouillard ; vous ne voyez pas la vallée, mais vous sentez la pente sous vos pieds. La stratégie : **faire un pas dans la direction où le sol descend le plus, puis recommencer**. Nous savons déjà que cette direction est $-\nabla f$.

#### L'algorithme

On part d'un point initial $\boldsymbol{\theta}_0$ et on répète :

$$\boxed{\;\boldsymbol{\theta}_{k+1} = \boldsymbol{\theta}_k - \eta\,\nabla f(\boldsymbol{\theta}_k)\;}$$

Le nombre $\eta > 0$ est le **pas d'apprentissage** (*learning rate*) : la taille de nos enjambées. On s'arrête quand le gradient est presque nul, ou après un nombre fixé d'itérations.

#### Un exemple à une variable, calculé à la main

Minimisons $f(x) = (x - 3)^2$. Sa dérivée est $f'(x) = 2(x - 3)$ et son minimum est évidemment en $x = 3$. Partons de $x_0 = 0$ avec $\eta = 0{,}1$.

> 🧪 **Pas à pas.**
>
> - $x_1 = 0 - 0{,}1 \times 2(0 - 3) = 0 + 0{,}6 = 0{,}6$
> - $x_2 = 0{,}6 - 0{,}1 \times 2(0{,}6 - 3) = 0{,}6 + 0{,}48 = 1{,}08$
> - $x_3 = 1{,}08 - 0{,}1 \times 2(1{,}08 - 3) = 1{,}08 + 0{,}384 = 1{,}464$
>
> On avance vers 3, avec des pas qui raccourcissent (la pente s'adoucit à mesure qu'on approche du fond).

Peut-on prévoir ce comportement ? Oui, et c'est instructif :

> 📐 **Démonstration : quand la descente converge-t-elle ?** Écrivons l'itération : $x_{k+1} = x_k - 2\eta(x_k - 3)$. Soustrayons 3 des deux côtés :
>
> $$x_{k+1} - 3 = (x_k - 3) - 2\eta(x_k - 3) = (1 - 2\eta)\,(x_k - 3).$$
>
> L'écart au minimum est donc **multiplié à chaque pas par le même facteur** $(1 - 2\eta)$. Par récurrence, $x_k - 3 = (1 - 2\eta)^k\,(x_0 - 3)$. Cet écart tend vers zéro si et seulement si $|1 - 2\eta| < 1$, c'est-à-dire
>
> $$0 < \eta < 1.$$
>
> Avec $\eta = 0{,}1$, le facteur vaut $0{,}8$ : on réduit l'erreur de 20 % à chaque pas ($x_1 - 3 = 0{,}8 \times (-3) = -2{,}4$, soit $x_1 = 0{,}6$ ✔). Le cas $\eta = 0{,}5$ donne un facteur 0 : convergence **en un seul pas** (c'est le pas idéal, égal à l'inverse de la courbure $f'' = 2$). Pour $\eta > 1$, le facteur dépasse 1 en valeur absolue : l'erreur **grandit** à chaque pas. $\blacksquare$

Observons les cinq comportements possibles :

```python
grad_1d = lambda x: 2 * (x - 3)

for eta in [0.1, 0.5, 0.9, 1.0, 1.1]:
    x_k = 0.0
    suite = [x_k]
    for _ in range(6):
        x_k = x_k - eta * grad_1d(x_k)
        suite.append(round(x_k, 3))
    print(f"eta = {eta:<4}", suite)
```
<!--sortie-->
```text
eta = 0.1  [0.0, 0.6, 1.08, 1.464, 1.771, 2.017, 2.214]
eta = 0.5  [0.0, 3.0, 3.0, 3.0, 3.0, 3.0, 3.0]
eta = 0.9  [0.0, 5.4, 1.08, 4.536, 1.771, 3.983, 2.214]
eta = 1.0  [0.0, 6.0, 0.0, 6.0, 0.0, 6.0, 0.0]
eta = 1.1  [0.0, 6.6, -1.32, 8.184, -3.221, 10.465, -5.958]
```

On y voit : $\eta = 0{,}1$ converge doucement ; $\eta = 0{,}5$ tombe sur 3 dès le premier pas ; $\eta = 0{,}9$ converge **en oscillant** de part et d'autre du minimum ; $\eta = 1$ oscille éternellement entre 0 et 6 sans jamais converger ; $\eta = 1{,}1$ **diverge** (les valeurs s'éloignent de plus en plus).

![Descente de gradient sur f(x) = (x−3)² pour trois pas d'apprentissage : prudent (lent), bien choisi (rapide), trop grand (divergence).](figures/ch01-descente-1d.png)

> ⚠️ **Piège : le choix du pas.** Un pas trop petit donne un calcul lent ; un pas trop grand fait diverger l'algorithme. En pratique, le pas se règle à l'essai, ou avec des méthodes adaptatives (que nous verrons au volume III).

#### Descente de gradient en deux dimensions : ajuster une droite

Passons au problème de la droite ajustée aux points $(1,2)$, $(2,3)$, $(3,5)$. Écrivons l'algorithme une fois pour toutes sous une forme réutilisable :

```python
def descente_de_gradient(grad, theta0, eta, n_iter=1000, tol=1e-8):
    """Descente de gradient : renvoie le point final et le chemin parcouru."""
    theta = np.array(theta0, dtype=float)
    chemin = [theta.copy()]
    for _ in range(n_iter):
        g = grad(theta)
        if np.linalg.norm(g) < tol:          # presque à plat : on s'arrête
            break
        theta = theta - eta * g
        chemin.append(theta.copy())
    return theta, np.array(chemin)

def grad_L(theta, X, y):
    return -2 * X.T @ (y - X @ theta)

def perte_L(theta, X, y):
    return np.sum((y - X @ theta)**2)
```

On a vu que la hessienne a pour valeurs propres 0,72 et 33,28. Pour que la descente converge, le pas doit être inférieur à $2/\lambda_{\max} = 2/33{,}28 \approx 0{,}060$ (même raisonnement que $0 < \eta < 1$ en une dimension, où la courbure était 2). Essayons un pas de $0{,}05$ (acceptable), puis de $0{,}07$ (trop grand) :

```python
theta, chemin = descente_de_gradient(lambda t: grad_L(t, X, y), [0, 0], eta=0.05, n_iter=5000, tol=1e-6)
print("eta = 0,05 : itérations =", len(chemin) - 1, "   theta =", theta.round(4))

_, chemin = descente_de_gradient(lambda t: grad_L(t, X, y), [0, 0], eta=0.07, n_iter=15, tol=1e-6)
print("eta = 0,07 : pertes aux étapes 0, 5, 10, 15 :", [float(round(perte_L(chemin[k], X, y), 1)) for k in (0, 5, 10, 15)])
```
<!--sortie-->
```text
eta = 0,05 : itérations = 335    theta = [1.5    0.3333]
eta = 0,07 : pertes aux étapes 0, 5, 10, 15 : [38.0, 652.5, 11256.2, 194234.4]
```

Avec $\eta = 0{,}05$, l'algorithme converge vers $(1{,}5\;;\;0{,}3333)$, la droite $y = 1{,}5x + 1/3$, mais il lui faut **335 itérations** pour un problème à trois points. Avec $\eta = 0{,}07$ (juste au-dessus de la limite 0,060), la perte **explose**.

Pourquoi tant d'itérations ? À cause du bol allongé : le pas est limité par la direction raide (valeur propre 33), mais la progression dans la direction presque plate (valeur propre 0,72) est minuscule. Il existe un remède classique et très simple : **centrer** la variable. Au lieu de $x = (1, 2, 3)$, on utilise $x - \bar{x} = (-1, 0, 1)$.

> 🧪 **Pourquoi ça aide ?** Avec la colonne centrée, le produit $\mathbf{X}^\top\mathbf{X}$ devient **diagonal** : $\begin{pmatrix}2&0\\0&3\end{pmatrix}$. Les deux directions deviennent indépendantes et de courbures comparables (4 et 6 pour la hessienne). Le bol est presque rond.

```python
xc = x - x.mean()
Xc = np.column_stack([xc, np.ones_like(xc)])
print("valeurs propres (variable centrée) :", np.linalg.eigvalsh(2 * Xc.T @ Xc).round(3))

theta_c, chemin_c = descente_de_gradient(lambda t: grad_L(t, Xc, y), [0, 0], eta=0.15, n_iter=5000, tol=1e-6)
a, b_centre = theta_c
print("variable centrée : itérations =", len(chemin_c) - 1, "   (a, b') =", theta_c.round(4))
print("retour à la droite d'origine : a =", round(a, 4), "  b =", round(b_centre - a * x.mean(), 4))
```
<!--sortie-->
```text
valeurs propres (variable centrée) : [4. 6.]
variable centrée : itérations = 18    (a, b') = [1.5    3.3333]
retour à la droite d'origine : a = 1.5   b = 0.3333
```

**18 itérations au lieu de 335**, pour exactement le même résultat. (On retrouve la droite d'origine par $b = b' - a\,\bar{x}$.) C'est la raison pour laquelle on **centre et standardise** presque toujours les variables avant d'entraîner un modèle par descente de gradient.

Enfin, pour ce problème précis, une solution **exacte** existe, sans itérer. Le gradient s'annule quand $-2\mathbf{X}^\top(\mathbf{y} - \mathbf{X}\boldsymbol{\theta}) = \mathbf{0}$, c'est-à-dire pour

$$\mathbf{X}^\top\mathbf{X}\,\boldsymbol{\theta} = \mathbf{X}^\top\mathbf{y},$$

un système linéaire (les « équations normales ») que l'on sait résoudre avec ce que nous avons vu en 1.1.2 :

```python
theta_exact = np.linalg.solve(X.T @ X, X.T @ y)
print("équations normales :", theta_exact.round(4))
```
<!--sortie-->
```text
équations normales : [1.5    0.3333]
```

Pourquoi alors se servir de la descente de gradient ? Parce que **la plupart des modèles n'ont pas de solution exacte** : réseaux de neurones, régression logistique, etc. La descente de gradient fonctionne partout où l'on sait calculer un gradient. La régression linéaire est notre terrain d'entraînement, car on connaît la bonne réponse.

![Chemin de la descente de gradient sur les courbes de niveau de la perte, avec la variable brute (à gauche) et la variable centrée (à droite). Le bol allongé force à zigzaguer ; le bol presque rond permet d'aller droit au but.](figures/ch01-descente-2d.png)

### 1.3.4 🛠️ Application : le prix qui maximise les recettes

Voici un vrai petit problème de décision, qui combine tout le chapitre. La gérante a testé huit prix pour un même bol en céramique, chacun pendant une semaine :

| Prix $p$ (€) | 25 | 28 | 31 | 34 | 37 | 40 | 43 | 46 |
|---|---|---|---|---|---|---|---|---|
| Ventes $q$ (pièces) | 93 | 82 | 82 | 69 | 67 | 56 | 56 | 47 |

**Étape 1 : modéliser la demande.** On suppose une relation linéaire $q = \alpha + \beta\,p$ et on cherche $\alpha$ et $\beta$ par descente de gradient. Ici les prix valent environ 35 et les ventes environ 70 : les variables n'ont pas la même échelle. Nous appliquons donc ce que nous venons d'apprendre : **standardiser le prix** avant de descendre.

```python
prix = np.array([25, 28, 31, 34, 37, 40, 43, 46], dtype=float)
ventes = np.array([93, 82, 82, 69, 67, 56, 56, 47], dtype=float)

z = (prix - prix.mean()) / prix.std()                 # prix standardisé
Z = np.column_stack([z, np.ones_like(z)])

theta, chemin = descente_de_gradient(lambda t: grad_L(t, Z, ventes), [0, 0], eta=0.05, n_iter=1000, tol=1e-6)
print("itérations :", len(chemin) - 1)

# retour aux unités d'origine : q = alpha + beta * p
beta = theta[0] / prix.std()
alpha = theta[1] - theta[0] * prix.mean() / prix.std()
print(f"alpha = {alpha:.3f}   beta = {beta:.3f}")
print("contrôle avec np.polyfit :", np.polyfit(prix, ventes, 1).round(3)[::-1])
```
<!--sortie-->
```text
itérations : 13
alpha = 143.944   beta = -2.111
contrôle avec np.polyfit : [143.944  -2.111]
```

Treize itérations seulement. Le modèle trouvé est $q \approx 143{,}9 - 2{,}11\,p$ : **chaque euro de hausse fait perdre environ 2,1 ventes par semaine**. (La ligne `polyfit` vérifie notre résultat avec la fonction toute faite de NumPy.)

**Étape 2 : exprimer les recettes.** Les recettes sont le prix multiplié par les quantités vendues :

$$R(p) = p \cdot q(p) = p\,(\alpha + \beta\,p) = \alpha\,p + \beta\,p^2.$$

**Étape 3 : maximiser.** On dérive et on annule : $R'(p) = \alpha + 2\beta\,p = 0$, d'où

$$p^\star = -\frac{\alpha}{2\beta}.$$

Comme $\beta < 0$, on a $R'' = 2\beta < 0$ : c'est bien un maximum.

```python
p_opt = -alpha / (2 * beta)
R = lambda p: p * (alpha + beta * p)
print(f"prix optimal p* = {p_opt:.2f} €")
print(f"recettes prévues à p* : {R(p_opt):8.1f} € par semaine")
print(f"recettes prévues à 40 € : {R(40):8.1f} € par semaine")
print(f"recettes prévues à 46 € : {R(46):8.1f} € par semaine")
```
<!--sortie-->
```text
prix optimal p* = 34.09 €
recettes prévues à p* :   2453.7 € par semaine
recettes prévues à 40 € :   2380.0 € par semaine
recettes prévues à 46 € :   2154.3 € par semaine
```

![À gauche : les huit mesures et la droite de demande ajustée. À droite : les recettes prévues selon le prix, avec leur maximum vers 34 €.](figures/ch01-demande-recettes.png)

**Résultat.** Le prix qui maximise les recettes est d'environ **34 €**, avec 2 454 € de recettes hebdomadaires prévues. Au prix actuel de 40 €, elles seraient de 2 380 € : baisser le prix de 6 euros rapporterait un peu plus de **70 € par semaine**, soit environ 3 % de mieux.

> ⚠️ **Prudence.** Ce résultat est obtenu avec **huit** points et un modèle très simple. Il ne dit rien de l'incertitude (de combien $p^\star$ pourrait-il se tromper ?), ni du bénéfice (ici nous avons maximisé les *recettes*, sans tenir compte des coûts), ni de l'extrapolation hors de la plage de prix testée. Ces questions sont l'objet du chapitre 3 (statistique) et du volume II (régression). Retenez la démarche : **modéliser, écrire la fonction objectif, la dériver, l'annuler.**

### 1.3.5 Optimisation sous contraintes : les multiplicateurs de Lagrange

Dans la vraie vie, on n'optimise presque jamais librement : on a un **budget**, une capacité, un poids maximal. On cherche alors le meilleur choix **parmi ceux qui respectent une contrainte**.

> 💡 **Intuition.** Vous voulez atteindre le point le plus haut d'une colline, mais vous devez rester sur un sentier. Au meilleur point du sentier, vous ne pouvez plus monter en suivant le sentier : celui-ci est **tangent à une courbe de niveau** de la colline. À cet endroit, la direction de plus forte montée de la colline (le gradient de $f$) est **perpendiculaire au sentier**, donc **parallèle au gradient de la contrainte** (qui, lui aussi, est perpendiculaire au sentier).

#### Un exemple concret

La gérante dispose de 1 000 € de budget publicitaire à répartir entre Facebook ($x$ euros) et Réseaux ($y$ euros). Elle estime les recettes générées par :

$$R(x, y) = 80\sqrt{x} + 120\sqrt{y}.$$

(La racine carrée traduit des **rendements décroissants** : les premiers euros investis rapportent plus que les derniers.) Elle veut maximiser $R$ sous la contrainte $x + y = 1000$.

**La méthode de Lagrange.** On introduit un nombre $\lambda$ (le *multiplicateur*) et on forme le **lagrangien** :

$$\mathcal{L}(x, y, \lambda) = 80\sqrt{x} + 120\sqrt{y} - \lambda\,(x + y - 1000).$$

On annule toutes ses dérivées partielles :

- $\dfrac{\partial\mathcal{L}}{\partial x} = \dfrac{40}{\sqrt{x}} - \lambda = 0$
- $\dfrac{\partial\mathcal{L}}{\partial y} = \dfrac{60}{\sqrt{y}} - \lambda = 0$
- $\dfrac{\partial\mathcal{L}}{\partial \lambda} = -(x + y - 1000) = 0$ (qui redonne la contrainte).

> 🧪 **Résolution à la main.** Les deux premières équations donnent $\dfrac{40}{\sqrt{x}} = \dfrac{60}{\sqrt{y}}$, donc $\sqrt{y} = 1{,}5\sqrt{x}$, soit $y = 2{,}25\,x$. En reportant dans la contrainte : $x + 2{,}25\,x = 1000$, donc
>
> $$x = \frac{1000}{3{,}25} \approx 307{,}7\ \text{€}, \qquad y = 2{,}25\,x \approx 692{,}3\ \text{€}.$$
>
> Recettes : $80\sqrt{307{,}7} + 120\sqrt{692{,}3} \approx 1\,403{,}3 + 3\,157{,}4 = 4\,560{,}7$ €.

> 📐 **Pourquoi cette méthode marche.** Le long de la contrainte, on peut paramétrer $y = 1000 - x$ et regarder $R$ comme fonction d'une seule variable. Au maximum, sa dérivée s'annule, ce qui s'écrit $\nabla R \cdot \mathbf{t} = 0$ où $\mathbf{t}$ est la direction du sentier : $\nabla R$ est perpendiculaire au sentier. Or le gradient de $g(x,y) = x + y - 1000$ l'est aussi. Deux vecteurs perpendiculaires à la même direction (en dimension 2) sont parallèles : $\nabla R = \lambda\,\nabla g$. C'est exactement ce que disent les équations $\partial\mathcal{L}/\partial x = \partial\mathcal{L}/\partial y = 0$. $\blacksquare$

Vérifions par trois chemins différents : un solveur numérique, une recherche exhaustive le long de la contrainte, et la formule.

```python
from scipy.optimize import minimize

R2 = lambda v: 80 * np.sqrt(v[0]) + 120 * np.sqrt(v[1])

res = minimize(lambda v: -R2(v), x0=[500, 500], method="SLSQP",
               bounds=[(1e-6, None), (1e-6, None)],
               constraints=[{"type": "eq", "fun": lambda v: v[0] + v[1] - 1000}])
print("solveur SLSQP        : x = %.1f, y = %.1f, recettes = %.2f" % (res.x[0], res.x[1], -res.fun))

grille = np.linspace(1, 999, 9981)
valeurs = [R2([g, 1000 - g]) for g in grille]
i = int(np.argmax(valeurs))
print("recherche exhaustive : x = %.1f, y = %.1f, recettes = %.2f" % (grille[i], 1000 - grille[i], valeurs[i]))

x_th = 1000 / 3.25
print("formule              : x = %.1f, y = %.1f, recettes = %.2f" % (x_th, 1000 - x_th, R2([x_th, 1000 - x_th])))
```
<!--sortie-->
```text
solveur SLSQP        : x = 307.7, y = 692.3, recettes = 4560.70
recherche exhaustive : x = 307.7, y = 692.3, recettes = 4560.70
formule              : x = 307.7, y = 692.3, recettes = 4560.70
```

**Le multiplicateur $\lambda$ a une signification concrète.** Au point optimal, $\lambda = 40/\sqrt{x} \approx 40/17{,}54 \approx 2{,}28$. C'est le **prix de l'ombre** (*shadow price*) de la contrainte : **un euro de budget supplémentaire rapporterait environ 2,28 € de recettes en plus**, si l'on réoptimise la répartition. Vérifions :

```python
meilleur = lambda B: R2([B / 3.25, B - B / 3.25])       # répartition optimale pour un budget B
print("gain réel avec 1 € de plus :", round(meilleur(1001) - meilleur(1000), 4))
print("multiplicateur lambda       :", round(40 / np.sqrt(x_th), 4))
```
<!--sortie-->
```text
gain réel avec 1 € de plus : 2.2798
multiplicateur lambda       : 2.2804
```

C'est une information précieuse pour fixer un budget : 1 € de publicité en plus rapporte environ 2,28 € de recettes. Il n'est donc rentable d'augmenter le budget que si la marge brute de la gérante dépasse $1/2{,}28 \approx 44\,\%$ (sinon la dépense supplémentaire coûte plus qu'elle ne rapporte).

> ✅ **À retenir (optimisation).**
>
> - Apprendre = minimiser une fonction de perte. $\arg\min$ désigne le point où le minimum est atteint.
> - Si la fonction est **convexe**, tout minimum local est global. La perte des moindres carrés est convexe (hessienne $2\mathbf{X}^\top\mathbf{X}$ positive) ; elle a un fond unique si les colonnes de $\mathbf{X}$ sont indépendantes.
> - Descente de gradient : $\boldsymbol{\theta}_{k+1} = \boldsymbol{\theta}_k - \eta\,\nabla f(\boldsymbol{\theta}_k)$. Le pas $\eta$ ne doit être ni trop petit (lent) ni trop grand (divergence : $\eta < 2/\lambda_{\max}$ pour une fonction quadratique).
> - **Centrer et standardiser** les variables arrondit le bol et accélère considérablement la descente.
> - Sous contrainte, on annule les dérivées du lagrangien ; $\lambda$ mesure la valeur marginale de la contrainte.
