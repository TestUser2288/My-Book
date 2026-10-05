# Chapitre 1 : Mathématiques pour la data science — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 1 du livre. On y manipule vecteurs, matrices, dérivées, gradients et optimisation sur les petits exemples de la boutique. Aucune donnée externe : tout est défini dans le texte. Prérequis : le chapitre 1 du livre. Le code est écrit en Python avec NumPy et SciPy ; chaque application avance par petites étapes, avec le résultat sous chaque bloc.

## Préparation

Une seule fois, au début de la séance :

```python
import math
import numpy as np
```

## Applications

### Application 1.1 — Des colonnes redondantes : le rang d'une table

*Section 1.1.2 du livre.*

**Contexte.** Un fichier de produits contient le prix hors taxes (HT) *et* le prix toutes taxes comprises (TTC), égal à 1,19 fois le HT. Une des deux colonnes est-elle utile ?

**Étape 1 : construire la table et mesurer son rang.** Le rang est le nombre de colonnes réellement indépendantes.

```python
ht = np.array([40.0, 25.0, 60.0, 15.0])
table = np.column_stack([ht, 1.19 * ht])        # deux colonnes : HT et TTC
print("colonnes :", table.shape[1], "  rang :", np.linalg.matrix_rank(table))
```
<!--sortie-->
```text
colonnes : 2   rang : 1
```

Le rang vaut 1 : la colonne TTC ne dit rien de plus que la colonne HT.

**Étape 2 : ajouter une vraie information.** Ajoutons le poids de chaque produit (en kg), qui n'a aucun lien avec le prix.

```python
poids = np.array([1.2, 0.4, 2.5, 0.3])
table3 = np.column_stack([ht, 1.19 * ht, poids])
print("colonnes :", table3.shape[1], "  rang :", np.linalg.matrix_rank(table3))
```
<!--sortie-->
```text
colonnes : 3   rang : 2
```

Trois colonnes, mais le rang ne monte qu'à 2 : la redondance HT/TTC est toujours là.

**Étape 3 : voir la conséquence.** Une régression résout un système avec la matrice $\mathbf{X}^\top\mathbf{X}$. Pour une table de rang insuffisant, elle est singulière :

```python
G = table.T @ table
print("déterminant de X^T X :", round(np.linalg.det(G), 6))
print("valeurs propres      :", np.linalg.eigvalsh(G).round(4))
```
<!--sortie-->
```text
déterminant de X^T X : 0.0
valeurs propres      : [   -0.    14617.405]
```

Le déterminant est (numériquement) nul et une valeur propre est nulle : le système n'a pas de solution unique, on ne peut pas départager les rôles du HT et du TTC. C'est la **multicolinéarité**.

> **Pour aller plus loin.** Retirez la colonne TTC et recalculez le déterminant de $\mathbf{X}^\top\mathbf{X}$ pour la table (HT, poids). Que constatez-vous ?

### Application 1.2 — La matrice des similarités entre clients

*Section 1.1.2 du livre.*

**Contexte.** Cinq clients sont décrits par leurs achats dans trois catégories (poteries, textiles, bijoux). On veut comparer **tous** les clients deux à deux d'un seul coup.

**Étape 1 : la matrice des profils.** Une ligne par client.

```python
clients = {"Alix": [3, 1, 0], "Basile": [6, 2, 0], "Camille": [0, 1, 4],
           "Dominique": [1, 0, 5], "Eden": [2, 2, 2]}
noms = list(clients)
X = np.array(list(clients.values()), dtype=float)
print(X)
```
<!--sortie-->
```text
[[3. 1. 0.]
 [6. 2. 0.]
 [0. 1. 4.]
 [1. 0. 5.]
 [2. 2. 2.]]
```

**Étape 2 : normaliser les lignes.** Chaque ligne est divisée par sa norme, pour que sa longueur vaille 1.

```python
U = X / np.linalg.norm(X, axis=1, keepdims=True)
print("normes des lignes de U :", np.linalg.norm(U, axis=1).round(3))
```
<!--sortie-->
```text
normes des lignes de U : [1. 1. 1. 1. 1.]
```

**Étape 3 : toutes les similarités d'un coup.** Le produit $\mathbf{U}\mathbf{U}^\top$ rassemble les cosinus.

```python
S = U @ U.T
print(" " * 10 + "".join(f"{n:>10}" for n in noms))
for i, n in enumerate(noms):
    print(f"{n:<10}" + "".join(f"{S[i, j]:10.2f}" for j in range(len(noms))))
```
<!--sortie-->
```text
                Alix    Basile   Camille Dominique      Eden
Alix            1.00      1.00      0.08      0.19      0.73
Basile          1.00      1.00      0.08      0.19      0.73
Camille         0.08      0.08      1.00      0.95      0.70
Dominique       0.19      0.19      0.95      1.00      0.68
Eden            0.73      0.73      0.70      0.68      1.00
```

**Lecture.** La diagonale vaut 1 (chacun ressemble parfaitement à lui-même) et la matrice est symétrique. Alix et Basile valent 1,00 : même profil, simplement plus de volume. Camille et Dominique, tous deux amateurs de bijoux, sont très proches. Eden, qui achète un peu de tout, est moyennement proche de chacun (entre 0,68 et 0,73) sans avoir de « jumeau ».

**Étape 4 : le plus proche voisin de chacun.** Pour recommander des produits, on regarde ce qu'achète le client le plus semblable. On ignore la diagonale (la ressemblance à soi-même) avant de chercher le maximum.

```python
S2 = S.copy()
np.fill_diagonal(S2, -1)
for i, n in enumerate(noms):
    j = S2[i].argmax()
    print(f"voisin le plus proche de {n:<9} : {noms[j]:<9} (similarité {S2[i, j]:.2f})")
```
<!--sortie-->
```text
voisin le plus proche de Alix      : Basile    (similarité 1.00)
voisin le plus proche de Basile    : Alix      (similarité 1.00)
voisin le plus proche de Camille   : Dominique (similarité 0.95)
voisin le plus proche de Dominique : Camille   (similarité 0.95)
voisin le plus proche de Eden      : Alix      (similarité 0.73)
```

Avec cinq mille clients, ce serait exactement le même code.

> **Pour aller plus loin.** Remplacez la similarité cosinus par la distance euclidienne : les voisins les plus proches changent-ils ? Pourquoi (relisez la section 1.1.1 sur cosinus et distance) ?

### Application 1.3 — La direction principale d'un nuage de clients

*Section 1.1.3 du livre.*

**Contexte.** Pour 200 clients, on mesure le nombre de visites mensuelles sur le site et la dépense mensuelle. Les deux semblent liées. Quel axe résume le mieux le nuage ?

**Étape 1 : simuler les données** (graine fixée pour retrouver les mêmes nombres).

```python
rng = np.random.default_rng(42)
n = 200
visites = rng.normal(6, 2, n)                        # visites par mois
depense = 15 * visites + rng.normal(0, 12, n)        # dépense en euros, liée aux visites
```

**Étape 2 : standardiser** (moyenne 0, écart-type 1), pour que les deux variables aient la même échelle.

```python
def standardise(x):
    return (x - x.mean()) / x.std(ddof=1)

Z = np.column_stack([standardise(visites), standardise(depense)])
C = np.cov(Z.T)                                      # matrice de covariance 2 x 2
print("Matrice de covariance :\n", C.round(3))
```
<!--sortie-->
```text
Matrice de covariance :
 [[1.    0.903]
 [0.903 1.   ]]
```

C'est la matrice $\begin{pmatrix}1&r\\r&1\end{pmatrix}$ du livre, avec $r \approx 0{,}90$.

**Étape 3 : valeurs propres et vecteurs propres.**

```python
valeurs, vecteurs = np.linalg.eigh(C)
print("Valeurs propres :", valeurs.round(3))
print("Part de la variance expliquée :", (valeurs / valeurs.sum()).round(3))
print("Direction principale :", np.abs(vecteurs[:, -1]).round(3))
```
<!--sortie-->
```text
Valeurs propres : [0.097 1.903]
Part de la variance expliquée : [0.049 0.951]
Direction principale : [0.707 0.707]
```

![Nuage des 200 clients (variables standardisées) et son axe principal : le long de la diagonale, le nuage est étiré ; perpendiculairement, il est mince.](figures/ch01-nuage-clients.png)

**Lecture.** La plus grande valeur propre (environ 1,90) correspond à la direction $(0{,}71 ; 0{,}71)$, la diagonale : l'axe « client actif et dépensier ». Elle capte environ **95 %** de la variabilité, ce que prédit la formule $(1+r)/2$ du livre. La seconde (0,10) correspond à la direction perpendiculaire : « dépense inhabituelle pour ce nombre de visites ». On peut donc résumer les deux variables par une seule en ne perdant que 5 % de l'information : c'est le principe de l'analyse en composantes principales (volume II).

> **Pour aller plus loin.** Recommencez avec un bruit plus fort (par exemple `rng.normal(0, 40, n)` pour la dépense). Comment évoluent la corrélation et la part de variance de l'axe principal ? Comparez avec $(1+r)/2$.

### Application 1.4 — Résumer un tableau de ventes par la SVD

*Section 1.1.4 du livre.*

**Contexte.** Ventes hebdomadaires de 6 produits sur 8 semaines. Les données sont simulées selon une règle simple : *ventes = popularité du produit × effet de la semaine + bruit*.

**Étape 1 : construire le tableau.**

```python
rng = np.random.default_rng(7)
popularite = np.array([50, 30, 20, 12, 8, 5.0])                    # un niveau par produit
saison = np.array([1.0, 1.1, 0.9, 1.2, 1.5, 1.4, 1.0, 0.8])       # un effet par semaine
M = (np.outer(popularite, saison) + rng.normal(0, 1.0, (6, 8))).round(0)
print(M.astype(int))
```
<!--sortie-->
```text
[[50 55 45 59 75 69 50 41]
 [30 32 27 36 45 41 30 25]
 [19 22 16 23 28 28 19 16]
 [12 13  8 14 18 17 10  9]
 [ 7  8  8  9 12 12  7  6]
 [ 5  6  3  6  9  5  6  4]]
```

**Étape 2 : la décomposition en valeurs singulières.**

```python
U, s, Vt = np.linalg.svd(M)
part = 100 * s**2 / (s**2).sum()
print("valeurs singulières :", s.round(2))
print("part de l'énergie par couche (%) :", " ".join(f"{x:.2f}" for x in part))
```
<!--sortie-->
```text
valeurs singulières : [202.05   3.53   3.51   1.81   1.18   0.75]
part de l'énergie par couche (%) : 99.93 0.03 0.03 0.01 0.00 0.00
```

**Étape 3 : approximation par une seule couche.**

```python
M1 = s[0] * np.outer(U[:, 0], Vt[0])
erreur = np.linalg.norm(M - M1) / np.linalg.norm(M)
print("erreur relative du rang 1 :", round(erreur, 4))
print("nombres à stocker : 48 (tableau) contre", 6 + 8 + 1, "(couche 1)")
```
<!--sortie-->
```text
erreur relative du rang 1 : 0.0271
nombres à stocker : 48 (tableau) contre 15 (couche 1)
```

![Ventes observées (à gauche), approximation par une seule couche (au centre) et ce qui reste (à droite). L'échelle de couleur est la même pour les deux premiers panneaux.](figures/ch01-svd-ventes.png)

**Lecture.** La première valeur singulière (environ 202) est près de soixante fois plus grande que la deuxième (environ 3,5) : 99,9 % de l'« énergie » est dans une seule couche. Une approximation de rang 1, qui ne stocke que 15 nombres au lieu de 48, reproduit le tableau avec une erreur relative d'environ 2,7 %. La SVD a retrouvé la structure « popularité × saison » sans qu'on la lui indique.

> **Pour aller plus loin.** Augmentez le bruit (écart-type 5 au lieu de 1) et regardez comment la part d'énergie de la première couche diminue. À partir de quel niveau de bruit la deuxième couche devient-elle utile ?

### Application 1.5 — À quel niveau de ventes le bénéfice est-il maximal ?

*Section 1.2.1 du livre.*

**Contexte.** Le bénéfice hebdomadaire d'une poterie en fonction du nombre $q$ de pièces vendues est $P(q) = -2q^2 + 80q - 300$.

**Étape 1 : observer la fonction.**

```python
def benefice(q):
    return -2 * q**2 + 80 * q - 300

for q in [10, 15, 20, 25, 30]:
    print(f"q = {q:>2}   bénéfice = {benefice(q):>4} €")
```
<!--sortie-->
```text
q = 10   bénéfice =  300 €
q = 15   bénéfice =  450 €
q = 20   bénéfice =  500 €
q = 25   bénéfice =  450 €
q = 30   bénéfice =  300 €
```

**Étape 2 : la dérivée et le bénéfice marginal.** $P'(q) = -4q + 80$ s'annule en $q = 20$. Comparons la pente en $q = 10$ au gain réel de la pièce suivante.

```python
print("gain réel de la 11e pièce : P(11) - P(10) =", benefice(11) - benefice(10), "€")
print("pente en q = 10           : P'(10) = -4*10 + 80 =", -4 * 10 + 80, "€")
```
<!--sortie-->
```text
gain réel de la 11e pièce : P(11) - P(10) = 38 €
pente en q = 10           : P'(10) = -4*10 + 80 = 40 €
```

**Étape 3 : confirmer sans la dérivée**, par une recherche numérique du maximum (on minimise $-P$).

```python
from scipy.optimize import minimize_scalar

res = minimize_scalar(lambda q: -benefice(q), bounds=(0, 40), method="bounded")
print(f"optimum numérique : q = {res.x:.3f}, bénéfice = {-res.fun:.2f} €")
```
<!--sortie-->
```text
optimum numérique : q = 20.000, bénéfice = 500.00 €
```

![Bénéfice hebdomadaire en fonction du nombre de pièces vendues. En q = 10 la tangente monte avec une pente de 40 ; en q = 20 elle est horizontale : c'est le sommet.](figures/ch01-benefice-tangentes.png)

**Lecture.** Le sommet est en $q = 20$ pour un bénéfice de 500 €. La pente en $q=10$ (40 €) approche le gain réel de la pièce suivante (38 €) : la dérivée est exacte pour une variation infiniment petite, approchée pour une pièce.

> **Pour aller plus loin.** Les frais fixes passent de 300 € à 500 €. Que devient le niveau optimal ? Et le bénéfice maximal ? (Expliquez pourquoi sans recalculer.)

### Application 1.6 — Le gradient de l'erreur d'une droite

*Section 1.2.2 du livre.*

**Contexte.** On ajuste $y = ax + b$ à trois mesures $(1, 2)$, $(2, 3)$, $(3, 5)$ ; la perte est $L(a, b) = \sum_i (y_i - (ax_i + b))^2$.

**Étape 1 : la perte et son gradient**, écrits à partir des formules du livre.

```python
x = np.array([1.0, 2.0, 3.0])
y = np.array([2.0, 3.0, 5.0])

def perte(a, b):
    return np.sum((y - (a * x + b))**2)

def grad_perte(a, b):
    r = y - (a * x + b)
    return np.array([-2 * np.sum(x * r), -2 * np.sum(r)])

print("perte en (0, 0)    :", perte(0, 0))
print("gradient en (0, 0) :", grad_perte(0, 0))
```
<!--sortie-->
```text
perte en (0, 0)    : 38.0
gradient en (0, 0) : [-46. -20.]
```

On retrouve le calcul à la main du livre : $L = 38$ et un gradient $(-46, -20)$.

**Étape 2 : vérifier le gradient par de petites différences.** Si la formule est juste, la pente mesurée par un petit déplacement doit coïncider.

```python
h = 1e-6
num_a = (perte(0 + h, 0) - perte(0 - h, 0)) / (2 * h)
num_b = (perte(0, 0 + h) - perte(0, 0 - h)) / (2 * h)
print("gradient numérique :", round(num_a, 4), round(num_b, 4))
```
<!--sortie-->
```text
gradient numérique : -46.0 -20.0
```

**Étape 3 : le fond du bol.** Au point $(1{,}5 ; 1/3)$ le gradient doit être nul.

```python
print("perte en (1,5 ; 1/3)    :", round(perte(1.5, 1 / 3), 4))
print("gradient en (1,5 ; 1/3) :", grad_perte(1.5, 1 / 3).round(10) + 0)
```
<!--sortie-->
```text
perte en (1,5 ; 1/3)    : 0.1667
gradient en (1,5 ; 1/3) : [0. 0.]
```

> **Pour aller plus loin.** Choisissez deux autres points $(a, b)$ et vérifiez que $-\nabla L$ pointe bien dans la direction où la perte diminue, en comparant `perte(a, b)` à `perte` après un petit pas de $-0{,}01\,\nabla L$.

### Application 1.7 — Une commande dans les trois prochaines minutes ?

*Section 1.2.3 du livre.*

**Contexte.** En heure de pointe, une commande arrive en moyenne toutes les 2 minutes. Le temps d'attente $T$ (en minutes) suit une loi exponentielle de densité $f(t) = 0{,}5\,e^{-0{,}5\,t}$. Quelle est la probabilité que $T \le 3$ ?

**Étape 1 : intégrer avec des rectangles de Riemann.**

```python
def riemann(f, a, b, n):
    largeur = (b - a) / n
    xs = a + largeur * np.arange(1, n + 1)
    return np.sum(f(xs)) * largeur

densite = lambda t: 0.5 * np.exp(-0.5 * t)
for n in [3, 30, 300, 3000]:
    print(f"n = {n:>4} rectangles : P(T <= 3) ≈ {riemann(densite, 0, 3, n):.5f}")
```
<!--sortie-->
```text
n =    3 rectangles : P(T <= 3) ≈ 0.59877
n =   30 rectangles : P(T <= 3) ≈ 0.75761
n =  300 rectangles : P(T <= 3) ≈ 0.77493
n = 3000 rectangles : P(T <= 3) ≈ 0.77668
```

**Étape 2 : comparer à l'intégration numérique et à la formule.**

```python
from scipy.integrate import quad

p_quad, _ = quad(densite, 0, 3)
print("intégration numérique (quad) :", round(p_quad, 5))
print("formule 1 - exp(-1,5)        :", round(1 - np.exp(-1.5), 5))
```
<!--sortie-->
```text
intégration numérique (quad) : 0.77687
formule 1 - exp(-1,5)        : 0.77687
```

**Étape 3 : l'aire totale doit valoir 1** (c'est la condition pour qu'une densité soit une densité).

```python
total, _ = quad(densite, 0, np.inf)
print("aire totale sous la courbe :", round(total, 5))
```
<!--sortie-->
```text
aire totale sous la courbe : 1.0
```

![Densité du temps d'attente avant la prochaine commande. L'aire grisée entre 0 et 3 minutes vaut 0,777 : il y a environ 78 % de chances qu'une commande arrive dans les trois prochaines minutes.](figures/ch01-attente-densite.png)

**Lecture.** Les rectangles convergent vers la valeur exacte $1 - e^{-1{,}5} \approx 0{,}777$ : environ 77,7 % de chances qu'une commande arrive dans les 3 minutes.

> **Pour aller plus loin.** Calculez, par la formule, la probabilité d'attendre **plus de 5 minutes**, puis vérifiez avec `quad(densite, 5, np.inf)`.

### Application 1.8 — La descente de gradient pour ajuster une droite

*Section 1.3.3 du livre.*

**Contexte.** On reprend les trois points $(1,2)$, $(2,3)$, $(3,5)$. On sait que la droite optimale est $y = 1{,}5\,x + 1/3$ ; voyons comment la descente de gradient la trouve, et comment le pas $\eta$ et le centrage de $x$ changent tout.

**Étape 1 : l'algorithme, écrit une fois pour toutes.**

```python
def descente_de_gradient(grad, theta0, eta, n_iter=1000, tol=1e-8):
    """Renvoie le point final et le chemin parcouru."""
    theta = np.array(theta0, dtype=float)
    chemin = [theta.copy()]
    for _ in range(n_iter):
        g = grad(theta)
        if np.linalg.norm(g) < tol:          # presque à plat : on s'arrête
            break
        theta = theta - eta * g
        chemin.append(theta.copy())
    return theta, np.array(chemin)
```

**Étape 2 : la perte des moindres carrés et son gradient.**

```python
x = np.array([1.0, 2.0, 3.0])
y = np.array([2.0, 3.0, 5.0])
X = np.column_stack([x, np.ones_like(x)])             # colonnes : x et 1  ->  theta = (a, b)

grad_L = lambda theta, X, y: -2 * X.T @ (y - X @ theta)
perte_L = lambda theta, X, y: np.sum((y - X @ theta)**2)

H = 2 * X.T @ X
print("valeurs propres de la hessienne :", np.linalg.eigvalsh(H).round(2))
```
<!--sortie-->
```text
valeurs propres de la hessienne : [ 0.72 33.28]
```

Le pas doit rester inférieur à $2/\lambda_{\max} = 2/33{,}28 \approx 0{,}060$.

**Étape 3 : un pas acceptable, puis un pas trop grand.**

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

Avec $\eta = 0{,}05$, la descente converge vers $(1{,}5 ; 0{,}3333)$ mais il lui faut **335 itérations**. Avec $\eta = 0{,}07$, la perte explose.

**Étape 4 : centrer la variable $x$.** On remplace $x = (1,2,3)$ par $x - \bar x = (-1,0,1)$, puis on revient à l'ordonnée d'origine par $b = b' - a\,\bar x$.

```python
xc = x - x.mean()
Xc = np.column_stack([xc, np.ones_like(xc)])
print("valeurs propres (variable centrée) :", np.linalg.eigvalsh(2 * Xc.T @ Xc).round(3))

theta_c, chemin_c = descente_de_gradient(lambda t: grad_L(t, Xc, y), [0, 0], eta=0.15, n_iter=5000, tol=1e-6)
a, b_centre = theta_c
print("itérations =", len(chemin_c) - 1, "  retour : a =", round(a, 4), " b =", round(b_centre - a * x.mean(), 4))
```
<!--sortie-->
```text
valeurs propres (variable centrée) : [4. 6.]
itérations = 18   retour : a = 1.5  b = 0.3333
```

**18 itérations au lieu de 335**, pour le même résultat. C'est pourquoi on centre et on standardise presque toujours les variables.

**Étape 5 : comparer avec la solution exacte** des équations normales.

```python
print("équations normales :", np.linalg.solve(X.T @ X, X.T @ y).round(4))
```
<!--sortie-->
```text
équations normales : [1.5    0.3333]
```

![Chemin de la descente de gradient sur les courbes de niveau de la perte, avec la variable brute (à gauche) et la variable centrée (à droite). Le bol allongé force à zigzaguer ; le bol presque rond permet d'aller droit au but.](figures/ch01-descente-2d.png)

> **Pour aller plus loin.** Avec la variable centrée, essayez $\eta = 0{,}3$ (limite théorique : $2/6 \approx 0{,}33$) puis $\eta = 0{,}4$. Combien d'itérations faut-il, et que se passe-t-il à 0,4 ?

### Application 1.9 — Le prix qui maximise les recettes

*Section 1.3.4 du livre.*

**Contexte.** On a testé huit prix pour un bol en céramique, chacun pendant une semaine.

| Prix $p$ (€) | 25 | 28 | 31 | 34 | 37 | 40 | 43 | 46 |
|-------------------|---|---|---|---|---|---|---|---|
| Ventes $q$ (pièces) | 93 | 82 | 82 | 69 | 67 | 56 | 56 | 47 |

**Étape 1 : modéliser la demande** par $q = \alpha + \beta p$, ajustée par descente de gradient sur le prix **standardisé** (les variables n'ont pas la même échelle).

```python
prix = np.array([25, 28, 31, 34, 37, 40, 43, 46], dtype=float)
ventes = np.array([93, 82, 82, 69, 67, 56, 56, 47], dtype=float)

z = (prix - prix.mean()) / prix.std()
Z = np.column_stack([z, np.ones_like(z)])
theta = np.zeros(2)
for _ in range(2000):                                  # descente de gradient, pas 0,05
    theta = theta + 0.05 * 2 * Z.T @ (ventes - Z @ theta)
    if np.linalg.norm(Z.T @ (ventes - Z @ theta)) < 1e-6:
        break

beta = theta[0] / prix.std()
alpha = theta[1] - theta[0] * prix.mean() / prix.std()
print(f"alpha = {alpha:.3f}   beta = {beta:.3f}")
print("contrôle avec np.polyfit :", np.polyfit(prix, ventes, 1).round(3)[::-1])
```
<!--sortie-->
```text
alpha = 143.944   beta = -2.111
contrôle avec np.polyfit : [143.944  -2.111]
```

Chaque euro de hausse fait perdre environ 2,1 ventes par semaine.

**Étape 2 : les recettes et leur maximum.** $R(p) = p\,(\alpha + \beta p)$, maximale en $p^\star = -\alpha/(2\beta)$ puisque $\beta < 0$.

```python
p_opt = -alpha / (2 * beta)
R = lambda p: p * (alpha + beta * p)
print(f"prix optimal p* = {p_opt:.2f} €")
for p in (p_opt, 40, 46):
    print(f"recettes prévues à {p:5.2f} € : {R(p):7.1f} € par semaine")
```
<!--sortie-->
```text
prix optimal p* = 34.09 €
recettes prévues à 34.09 € :  2453.7 € par semaine
recettes prévues à 40.00 € :  2380.0 € par semaine
recettes prévues à 46.00 € :  2154.3 € par semaine
```

![À gauche : les huit mesures et la droite de demande ajustée. À droite : les recettes prévues selon le prix, avec leur maximum vers 34 €.](figures/ch01-demande-recettes.png)

**Lecture.** Le prix qui maximise les recettes est d'environ 34 €, pour 2 454 € par semaine. Au prix actuel de 40 €, elles seraient de 2 380 € : baisser le prix de 6 € rapporterait un peu plus de 70 € par semaine, soit environ 3 %.

> ⚠️ **Prudence.** Huit points et un modèle très simple : aucune idée de l'incertitude de $p^\star$, aucune prise en compte des coûts (on maximise des *recettes*), aucune garantie hors de la plage de prix testée. Ces questions relèvent du chapitre 3 et du volume II.

> **Pour aller plus loin.** Chaque bol coûte 15 € à produire. Maximisez le **bénéfice** $(p - 15)\,q(p)$ au lieu des recettes : le prix optimal est-il plus haut ou plus bas ? Pourquoi ?

### Application 1.10 — Répartir un budget publicitaire (multiplicateurs de Lagrange)

*Section 1.3.5 du livre.*

**Contexte.** On dispose de 1 000 € à répartir entre deux canaux de publicité, $x$ euros sur le canal A et $y$ euros sur le canal B, avec des recettes $R(x, y) = 80\sqrt{x} + 120\sqrt{y}$ sous la contrainte $x + y = 1000$.

**Étape 1 : la solution par la formule de Lagrange**, établie à la main dans le livre : $x = 1000/3{,}25$ et $y = 2{,}25\,x$.

```python
R2 = lambda v: 80 * np.sqrt(v[0]) + 120 * np.sqrt(v[1])
x_th = 1000 / 3.25
print("formule : x = %.1f, y = %.1f, recettes = %.2f" % (x_th, 1000 - x_th, R2([x_th, 1000 - x_th])))
```
<!--sortie-->
```text
formule : x = 307.7, y = 692.3, recettes = 4560.70
```

**Étape 2 : deux vérifications indépendantes.** Un solveur numérique sous contrainte, puis une recherche exhaustive le long de la contrainte.

```python
from scipy.optimize import minimize

res = minimize(lambda v: -R2(v), x0=[500, 500], method="SLSQP", bounds=[(1e-6, None), (1e-6, None)],
               constraints=[{"type": "eq", "fun": lambda v: v[0] + v[1] - 1000}])
print("solveur SLSQP        : x = %.1f, y = %.1f, recettes = %.2f" % (res.x[0], res.x[1], -res.fun))

grille = np.linspace(1, 999, 9981)
valeurs = [R2([g, 1000 - g]) for g in grille]
i = int(np.argmax(valeurs))
print("recherche exhaustive : x = %.1f, y = %.1f, recettes = %.2f" % (grille[i], 1000 - grille[i], valeurs[i]))
```
<!--sortie-->
```text
solveur SLSQP        : x = 307.7, y = 692.3, recettes = 4560.70
recherche exhaustive : x = 307.7, y = 692.3, recettes = 4560.70
```

**Étape 3 : le prix de l'ombre.** Le multiplicateur $\lambda = 40/\sqrt{x}$ doit valoir le gain obtenu avec 1 € de budget en plus.

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

**Lecture.** Chaque euro de budget supplémentaire rapporte environ 2,28 € de recettes ; il n'est donc rentable d'augmenter le budget que si la marge brute dépasse $1/2{,}28 \approx 44\ \%$.

> **Pour aller plus loin.** Remplacez les coefficients (80, 120) par (80, 80). Quelle répartition obtenez-vous, et pourquoi est-elle plus simple à prévoir ?

### Application 1.11 — Le graphe des produits achetés ensemble

*Sections 1.6.1 à 1.6.4 du livre.*

**Contexte.** Cinq produits ; deux produits sont reliés si au moins un client les a pris dans le même panier. On veut mesurer la ressemblance de paniers, compter des chemins, et trouver le plus court chemin de recommandation.

**Étape 1 : ensembles et similarité de Jaccard.**

```python
panier_a = {"bol", "tapis", "lampe"}
panier_b = {"bol", "plateau"}
print("union :", sorted(panier_a | panier_b), "  intersection :", sorted(panier_a & panier_b))
print("Jaccard(A, B) =", len(panier_a & panier_b) / len(panier_a | panier_b))
```
<!--sortie-->
```text
union : ['bol', 'lampe', 'plateau', 'tapis']   intersection : ['bol']
Jaccard(A, B) = 0.25
```

**Étape 2 : le graphe en liste d'adjacence.**

```python
produits = ["bol", "tapis", "lampe", "plateau", "coussin"]
aretes = [("bol", "plateau"), ("bol", "tapis"), ("tapis", "lampe"),
          ("tapis", "coussin"), ("lampe", "coussin")]
voisins = {p: [] for p in produits}
for a, b in aretes:
    voisins[a].append(b)
    voisins[b].append(a)
print({p: len(v) for p, v in voisins.items()})        # le degré de chaque produit
```
<!--sortie-->
```text
{'bol': 2, 'tapis': 3, 'lampe': 2, 'plateau': 1, 'coussin': 2}
```

**Étape 3 : la matrice d'adjacence et le comptage des chemins.**

```python
idx = {p: i for i, p in enumerate(produits)}
A = np.zeros((5, 5), dtype=int)
for a, b in aretes:
    A[idx[a], idx[b]] = A[idx[b], idx[a]] = 1

A2 = A @ A
print("chemins de longueur 2, bol -> lampe :", A2[idx["bol"], idx["lampe"]])
print("triangles :", np.trace(np.linalg.matrix_power(A, 3)) // 6)
```
<!--sortie-->
```text
chemins de longueur 2, bol -> lampe : 1
triangles : 1
```

**Étape 4 : la recherche en largeur.**

```python
from collections import deque

def distances_depuis(depart, voisins):
    dist = {depart: 0}
    file = deque([depart])
    while file:
        courant = file.popleft()
        for v in voisins[courant]:
            if v not in dist:
                dist[v] = dist[courant] + 1
                file.append(v)
    return dist

print(distances_depuis("plateau", voisins))
```
<!--sortie-->
```text
{'plateau': 0, 'bol': 1, 'tapis': 2, 'lampe': 3, 'coussin': 3}
```

**Lecture.** Les deux paniers n'ont qu'un produit en commun sur quatre au total ($J = 0{,}25$). Le tapis (degré 3) est le produit le plus connecté. Il y a un seul chemin en deux pas entre le bol et la lampe (bol → tapis → lampe), et un seul triangle (tapis, lampe, coussin). Depuis le plateau, la chaîne de recommandation la plus courte vers une lampe passe par le bol puis le tapis (distance 3).

> **Pour aller plus loin.** Ajoutez un sixième produit « bougie » relié seulement au coussin. Quelles distances depuis le plateau changent ? Combien de triangles y a-t-il maintenant ?

## Exercices

*Essayez chaque exercice sur papier ou dans un notebook **avant** de lire le corrigé. Difficulté croissante : ⭐ application directe, ⭐⭐ demande un raisonnement, ⭐⭐⭐ synthèse.*

### Exercice 1.1 ⭐ — Similarité cosinus (section 1.1.1)

Deux clientes sont décrites par leurs achats (bols, tapis, lampes) : $\mathbf{u}=(1,2,2)$ et $\mathbf{v}=(2,0,1)$. Calculez leur similarité cosinus. Sont-elles plutôt semblables ?

### Exercice 1.2 ⭐ — Produit matriciel et système (section 1.1.2)

Soit $\mathbf{A}=\begin{pmatrix}2&1\\1&3\end{pmatrix}$ et $\mathbf{b}=\begin{pmatrix}5\\10\end{pmatrix}$. (a) Calculez $\mathbf{A}^2$. (b) Résolvez $\mathbf{A}\mathbf{x}=\mathbf{b}$ à la main (par substitution), puis vérifiez avec NumPy.

### Exercice 1.3 ⭐⭐ — Valeurs propres (section 1.1.3)

Trouvez les valeurs propres et des vecteurs propres de $\mathbf{M}=\begin{pmatrix}4&1\\2&3\end{pmatrix}$. Vérifiez que la trace est la somme et le déterminant le produit des valeurs propres.

### Exercice 1.4 ⭐ — Dérivées (section 1.2.1)

Pour $f(x)=x^3-6x^2+9x$, calculez $f'$, trouvez les points où la pente est nulle, et déterminez s'il s'agit de minima ou de maxima grâce à $f''$.

### Exercice 1.5 ⭐⭐ — Gradient (section 1.2.2)

Pour $f(x,y)=x^2+3y^2$, calculez le gradient en $(1,1)$ puis effectuez **un pas** de descente de gradient avec $\eta=0{,}1$. La valeur de $f$ a-t-elle diminué ?

### Exercice 1.6 ⭐⭐ — Pas d'apprentissage (section 1.3.3)

Soit $f(x)=2(x-1)^2$. (a) Écrivez la récurrence de la descente de gradient. (b) Pour quelles valeurs de $\eta$ converge-t-elle ? (c) Quelle valeur de $\eta$ converge en un seul pas ?

### Exercice 1.7 ⭐⭐ — Lagrange (section 1.3.5)

La gérante dispose de 10 mètres de ruban pour entourer un rectangle de tissu. Quel rectangle d'aire maximale peut-on former ? Utilisez un multiplicateur de Lagrange, c'est-à-dire maximisez $xy$ sous la contrainte $x+y=5$ (demi-périmètre), et interprétez $\lambda$.

### Exercice 1.8 ⭐⭐⭐ — Régression à la main (sections 1.3.3 et 1.3.4)

Les ventes de bougies en fonction de la température sont : $x=(10,15,20,25)$ et $y=(40,35,28,22)$. (a) Ajustez la droite $y=ax+b$ avec les équations normales. (b) Retrouvez le résultat par descente de gradient sur la variable **centrée**. (c) Prédisez les ventes à 18 °C.

### Exercice 1.9 ⭐⭐ — Analyse numérique (section 1.5)

Expliquez pourquoi `0.1 * 3 == 0.3` est faux en Python et écrivez le test correct. Puis donnez le nombre de chiffres perdus pour un conditionnement $\kappa=10^6$.

### Exercice 1.10 ⭐⭐ — Graphes (section 1.6)

Dans le graphe de co-achat de l'application 1.11, calculez avec $\mathbf{A}^2$ le nombre de chemins de longueur 2 entre « plateau » et « tapis », puis entre « bol » et « coussin ». Vérifiez en les énumérant à la main.

## Corrigés

### Corrigé 1.1

$\mathbf{u}\cdot\mathbf{v}=1\cdot2+2\cdot0+2\cdot1=4$. $\lVert\mathbf{u}\rVert=\sqrt{1+4+4}=3$, $\lVert\mathbf{v}\rVert=\sqrt{4+0+1}=\sqrt5$. Donc $\cos\theta=\dfrac{4}{3\sqrt5}\approx0{,}596$.

```python
u = np.array([1, 2, 2]); v = np.array([2, 0, 1])
cos = u @ v / (np.linalg.norm(u) * np.linalg.norm(v))
print("cosinus =", round(cos, 3), "  angle =", round(np.degrees(np.arccos(cos)), 1), "degrés")
```
<!--sortie-->
```text
cosinus = 0.596   angle = 53.4 degrés
```

Un cosinus de 0,6 correspond à un angle d'environ 53° : **moyennement semblables** (1 = identiques, 0 = rien en commun). Elles aiment toutes deux les bols mais diffèrent sur les tapis.

### Corrigé 1.2

(a) $\mathbf{A}^2=\begin{pmatrix}2\cdot2+1\cdot1&2\cdot1+1\cdot3\\1\cdot2+3\cdot1&1\cdot1+3\cdot3\end{pmatrix}=\begin{pmatrix}5&5\\5&10\end{pmatrix}$. (b) Les équations sont $2x+y=5$ et $x+3y=10$. De la première : $y=5-2x$. En remplaçant : $x+15-6x=10$, donc $-5x=-5$, $x=1$ et $y=3$.

```python
A = np.array([[2, 1], [1, 3]]); b = np.array([5, 10])
print(A @ A)
print("solution :", np.linalg.solve(A, b))
```
<!--sortie-->
```text
[[ 5  5]
 [ 5 10]]
solution : [1. 3.]
```

### Corrigé 1.3

Le polynôme caractéristique est $\det(\mathbf{M}-\lambda\mathbf{I})=(4-\lambda)(3-\lambda)-2=\lambda^2-7\lambda+10=(\lambda-5)(\lambda-2)$. Les valeurs propres sont $5$ et $2$. Pour $\lambda=5$ : $(\mathbf{M}-5\mathbf{I})\mathbf{v}=\begin{pmatrix}-1&1\\2&-2\end{pmatrix}\mathbf{v}=\mathbf{0}$ donne $\mathbf{v}=(1,1)$. Pour $\lambda=2$ : $\begin{pmatrix}2&1\\2&1\end{pmatrix}\mathbf{v}=\mathbf{0}$ donne $\mathbf{v}=(1,-2)$. Trace : $4+3=7=5+2$ ✓. Déterminant : $4\cdot3-1\cdot2=10=5\times2$ ✓.

```python
M = np.array([[4, 1], [2, 3]])
valeurs, vecteurs = np.linalg.eig(M)
print("valeurs propres :", np.sort(valeurs.real))
print("trace =", np.trace(M), "  det =", round(np.linalg.det(M), 6))
print("M @ (1,1) =", M @ np.array([1, 1]), " = 5 * (1,1)")
```
<!--sortie-->
```text
valeurs propres : [2. 5.]
trace = 7   det = 10.0
M @ (1,1) = [5 5]  = 5 * (1,1)
```

### Corrigé 1.4

$f'(x)=3x^2-12x+9=3(x-1)(x-3)$, nulle en $x=1$ et $x=3$. $f''(x)=6x-12$. En $x=1$ : $f''=-6<0$, c'est un **maximum local** ($f(1)=4$). En $x=3$ : $f''=6>0$, c'est un **minimum local** ($f(3)=0$).

```python
f = lambda x: x**3 - 6*x**2 + 9*x
print("f(1) =", f(1), " f(3) =", f(3))
```
<!--sortie-->
```text
f(1) = 4  f(3) = 0
```

### Corrigé 1.5

$\nabla f=(2x,\,6y)$, donc $\nabla f(1,1)=(2,6)$. Le pas : $(1,1)-0{,}1\,(2,6)=(0{,}8;\,0{,}4)$. Avant : $f(1,1)=1+3=4$. Après : $f(0{,}8;0{,}4)=0{,}64+3\cdot0{,}16=1{,}12$. La valeur a bien diminué (de 4 à 1,12).

```python
grad = lambda p: np.array([2 * p[0], 6 * p[1]])
f2 = lambda p: p[0]**2 + 3 * p[1]**2
p = np.array([1.0, 1.0])
p_nouveau = p - 0.1 * grad(p)
print(p_nouveau, f2(p), round(f2(p_nouveau), 2))
```
<!--sortie-->
```text
[0.8 0.4] 4.0 1.12
```

### Corrigé 1.6

(a) $f'(x)=4(x-1)$, donc $x_{k+1}=x_k-4\eta(x_k-1)$, soit $x_{k+1}-1=(1-4\eta)(x_k-1)$. (b) L'écart à 1 est multiplié par $(1-4\eta)$ à chaque pas ; il tend vers 0 si $|1-4\eta|<1$, c'est-à-dire $0<\eta<\tfrac12$. (On retrouve $\eta<2/\lambda_{\max}$ avec $f''=4$.) (c) Le facteur est nul si $\eta=\tfrac14$ : on tombe sur le minimum en un seul pas.

```python
for eta in (0.1, 0.25, 0.45, 0.5, 0.55):
    x = 5.0
    for _ in range(20):
        x = x - eta * 4 * (x - 1)
    print(f"eta = {eta:<5} -> x après 20 pas = {x:.6g}")
```
<!--sortie-->
```text
eta = 0.1   -> x après 20 pas = 1.00015
eta = 0.25  -> x après 20 pas = 1
eta = 0.45  -> x après 20 pas = 1.04612
eta = 0.5   -> x après 20 pas = 5
eta = 0.55  -> x après 20 pas = 154.35
```

### Corrigé 1.7

On maximise $g(x,y)=xy$ sous $x+y=5$. Lagrangien : $\mathcal{L}=xy-\lambda(x+y-5)$. Les conditions $\partial_x\mathcal{L}=y-\lambda=0$ et $\partial_y\mathcal{L}=x-\lambda=0$ donnent $x=y=\lambda$. La contrainte donne $2\lambda=5$, donc $x=y=2{,}5$ m : le **carré** de 2,5 m de côté, d'aire $6{,}25\ \text{m}^2$. Le multiplicateur $\lambda=2{,}5$ s'interprète comme le prix de l'ombre : un mètre de demi-périmètre en plus rapporte environ 2,5 m² d'aire en plus (l'aire optimale est $(c/2)^2$ et sa dérivée par rapport à $c$ est $c/2=2{,}5$).

```python
from scipy.optimize import minimize
res = minimize(lambda v: -v[0] * v[1], x0=[1, 1],
               constraints={"type": "eq", "fun": lambda v: v[0] + v[1] - 5})
print(res.x.round(3), "aire =", round(-res.fun, 3))
```
<!--sortie-->
```text
[2.5 2.5] aire = 6.25
```

### Corrigé 1.8

(a) On construit $\mathbf{X}$ avec une colonne $x$ et une colonne de 1, puis on résout $\mathbf{X}^\top\mathbf{X}\boldsymbol\theta=\mathbf{X}^\top\mathbf{y}$. (b) On centre $x$ (moyenne 17,5), on descend le gradient, puis on revient à l'ordonnée d'origine par $b=b'-a\bar{x}$. (c) On évalue la droite en 18. Attention au pas : la hessienne vaut ici $2\mathbf{X}_c^\top\mathbf{X}_c=\operatorname{diag}(250,\,8)$, donc il faut $\eta<2/250=0{,}008$ ; nous prendrons $\eta=0{,}003$.

```python
x = np.array([10, 15, 20, 25.0]); y = np.array([40, 35, 28, 22.0])
X = np.column_stack([x, np.ones_like(x)])
a, b = np.linalg.solve(X.T @ X, X.T @ y)
print(f"(a) a = {a:.3f}  b = {b:.3f}")

xc = x - x.mean()
Xc = np.column_stack([xc, np.ones_like(xc)])
theta = np.zeros(2)
for _ in range(500):
    theta = theta - 0.003 * (-2 * Xc.T @ (y - Xc @ theta))
a2, b2 = theta[0], theta[1] - theta[0] * x.mean()
print(f"(b) a = {a2:.3f}  b = {b2:.3f}")
print("(c) ventes à 18 °C :", round(a * 18 + b, 1))
```
<!--sortie-->
```text
(a) a = -1.220  b = 52.600
(b) a = -1.220  b = 52.600
(c) ventes à 18 °C : 30.6
```

Lecture : chaque degré de plus fait perdre environ 1,2 ventes de bougies ; à 18 °C on prévoit environ 31 bougies.

### Corrigé 1.9

Le nombre $0{,}1$ n'a pas d'écriture finie en base 2 ; `0.1 * 3` vaut `0.30000000000000004`, un flottant différent de celui de `0.3`. Le bon test est `math.isclose(0.1 * 3, 0.3)`. Pour $\kappa=10^6$ on perd environ $\log_{10}\kappa=6$ chiffres significatifs sur les 16 disponibles : il en reste environ 10.

```python
print(0.1 * 3, 0.1 * 3 == 0.3, math.isclose(0.1 * 3, 0.3))
```
<!--sortie-->
```text
0.30000000000000004 False True
```

### Corrigé 1.10

Avec l'ordre des produits `["bol","tapis","lampe","plateau","coussin"]` (indices 0 à 4), on lit $(\mathbf{A}^2)_{\text{plateau},\text{tapis}}$ et $(\mathbf{A}^2)_{\text{bol},\text{coussin}}$. À la main : plateau—bol—tapis est le seul chemin en deux pas du plateau au tapis (le plateau n'a qu'un voisin, le bol), donc 1. Bol—tapis—coussin est le seul chemin en deux pas du bol au coussin (les voisins du bol sont plateau et tapis ; seul le tapis touche le coussin), donc 1.

```python
produits = ["bol", "tapis", "lampe", "plateau", "coussin"]
aretes = [("bol", "plateau"), ("bol", "tapis"), ("tapis", "lampe"),
          ("tapis", "coussin"), ("lampe", "coussin")]
idx = {p: i for i, p in enumerate(produits)}
A = np.zeros((5, 5), dtype=int)
for a_, b_ in aretes:
    A[idx[a_], idx[b_]] = A[idx[b_], idx[a_]] = 1
A2 = A @ A
print("plateau-tapis :", A2[idx["plateau"], idx["tapis"]])
print("bol-coussin   :", A2[idx["bol"], idx["coussin"]])
```
<!--sortie-->
```text
plateau-tapis : 1
bol-coussin   : 1
```
