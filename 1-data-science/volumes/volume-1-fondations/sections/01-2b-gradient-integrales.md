### 1.2.2 Dérivées partielles et gradient : plusieurs variables à la fois

Un modèle de data science a rarement un seul paramètre : il en a deux, dix, ou un milliard. Il nous faut donc dériver des fonctions de **plusieurs variables**.

> 💡 **Intuition.** Imaginez que vous êtes debout sur le flanc d'une colline brumeuse et que vous voulez monter le plus vite possible. À vos pieds, le sol penche plus dans une direction que dans les autres. Le **gradient** est la flèche qui indique **la direction de la plus forte montée**, et sa longueur dit à quel point c'est raide. Pour descendre, on marche dans la direction opposée.

#### Dérivée partielle

Pour une fonction $f(x, y)$, la **dérivée partielle par rapport à $x$**, notée $\dfrac{\partial f}{\partial x}$, s'obtient en dérivant par rapport à $x$ **en traitant $y$ comme une constante**. De même pour $y$.

> 🧪 **Exemple.** Soit $f(x, y) = x^2 + 3y^2$ (un « bol » plus raide dans la direction $y$).
>
> $$\frac{\partial f}{\partial x} = 2x, \qquad \frac{\partial f}{\partial y} = 6y.$$
>
> (Pour $\partial f/\partial x$, le terme $3y^2$ est une constante : sa dérivée est 0.)

Le **gradient** est le vecteur qui rassemble toutes les dérivées partielles :

$$\nabla f(x, y) = \begin{pmatrix} \partial f/\partial x \\ \partial f/\partial y \end{pmatrix} = \begin{pmatrix} 2x \\ 6y \end{pmatrix}.$$

En $(1, 1)$, on obtient $\nabla f(1,1) = (2, 6)$ : la pente est 3 fois plus forte dans la direction $y$ que dans la direction $x$.

#### Pourquoi le gradient indique-t-il la plus forte montée ?

Dans une direction donnée par un vecteur $\mathbf{u}$ de longueur 1, la pente de $f$ (la **dérivée directionnelle**) vaut

$$D_{\mathbf{u}} f = \nabla f \cdot \mathbf{u}.$$

Et ce produit scalaire, nous savons le majorer.

> 📐 **Démonstration.** Par la formule du produit scalaire vue en 1.1.1,
>
> $$D_{\mathbf{u}} f = \nabla f \cdot \mathbf{u} = \|\nabla f\|\,\|\mathbf{u}\|\cos\theta = \|\nabla f\|\cos\theta,$$
>
> où $\theta$ est l'angle entre $\mathbf{u}$ et le gradient. Cette quantité est maximale quand $\cos\theta = 1$, c'est-à-dire quand $\mathbf{u}$ pointe **dans la même direction que le gradient**, et alors la pente vaut $\|\nabla f\|$. Elle est minimale (la descente la plus forte, de pente $-\|\nabla f\|$) quand $\theta = 180^\circ$, c'est-à-dire dans la direction $-\nabla f$. $\blacksquare$
>
> (Au passage : on retrouve la même inégalité de Cauchy-Schwarz que dans la section 1.1.1.)

Vérifions en $(1, 1)$, où $\nabla f = (2, 6)$ et $\|\nabla f\| = \sqrt{40} \approx 6{,}325$, en calculant la pente de $f$ dans quatre directions $\mathbf{u}$ (de longueur 1), par $\nabla f\cdot\mathbf{u}$ :

| Direction | $(1, 0)$ | $(0, 1)$ | celle du gradient | opposée au gradient |
|---|---|---|---|---|
| Pente | $2$ | $6$ | $+6{,}325$ | $-6{,}325$ |

(Un calcul numérique de la pente par de petits déplacements, mené en parallèle, donne les mêmes valeurs.)

```python hide
def f2(x, y):
    return x**2 + 3 * y**2

def gradient_f2(x, y):
    return np.array([2 * x, 6 * y])

g = gradient_f2(1, 1)
print("gradient en (1, 1) :", g, "   norme =", round(np.linalg.norm(g), 4))

h = 1e-6
directions = [("direction (1, 0)",        np.array([1.0, 0.0])),
              ("direction (0, 1)",        np.array([0.0, 1.0])),
              ("direction du gradient",   g / np.linalg.norm(g)),
              ("opposée au gradient",     -g / np.linalg.norm(g))]
for nom, u in directions:
    pente = (f2(1 + h * u[0], 1 + h * u[1]) - f2(1, 1)) / h
    print(f"{nom:<24} pente mesurée = {pente:8.3f}")
```
<!--sortie-->
```text
gradient en (1, 1) : [2 6]    norme = 6.3246
direction (1, 0)         pente mesurée =    2.000
direction (0, 1)         pente mesurée =    6.000
direction du gradient    pente mesurée =    6.325
opposée au gradient      pente mesurée =   -6.325
```

La pente est maximale ($\|\nabla f\| = \sqrt{40}$) dans la direction du gradient, et minimale ($-\sqrt{40}$) dans la direction opposée. Aucune autre direction ne fait mieux.

![Courbes de niveau de f(x,y) = x² + 3y² (chaque ellipse est une « altitude » constante) et, en chaque point, la direction de la plus forte descente (−gradient). Les flèches sont perpendiculaires aux courbes de niveau et pointent vers le fond du bol.](figures/ch01-gradient-contours.png)

Deux faits à retenir sur cette figure : le gradient est **perpendiculaire aux courbes de niveau**, et **−gradient pointe vers le bas**. C'est exactement ce que nous utiliserons en 1.3 pour descendre vers le minimum.

#### Un exemple : le gradient de l'erreur d'une droite

La gérante veut ajuster une droite $y = ax + b$ à trois mesures $(x_i, y_i)$ : $(1, 2)$, $(2, 3)$ et $(3, 5)$. Pour mesurer la qualité d'une droite candidate, on utilise la **somme des carrés des erreurs** :

$$L(a, b) = \sum_{i=1}^{3}\bigl(y_i - (a x_i + b)\bigr)^2.$$

C'est une fonction de **deux** variables, $a$ et $b$. Notons $r_i = y_i - (ax_i + b)$ l'erreur du point $i$. Par la règle de la composée :

$$\frac{\partial L}{\partial a} = -2\sum_i x_i\, r_i, \qquad \frac{\partial L}{\partial b} = -2\sum_i r_i.$$

> 🧪 **Calcul à la main en $(a, b) = (0, 0)$** (la droite $y = 0$). Les erreurs sont $r = (2, 3, 5)$.
>
> - $L(0,0) = 4 + 9 + 25 = 38$.
> - $\partial L/\partial a = -2\,(1\cdot 2 + 2\cdot 3 + 3\cdot 5) = -2 \times 23 = -46$.
> - $\partial L/\partial b = -2\,(2 + 3 + 5) = -20$.
>
> Le gradient $(-46, -20)$ est très négatif : en augmentant $a$ et $b$, l'erreur diminue fortement.

```python hide
x = np.array([1.0, 2.0, 3.0])
y = np.array([2.0, 3.0, 5.0])

def perte(a, b):
    return np.sum((y - (a * x + b))**2)

def grad_perte(a, b):
    r = y - (a * x + b)
    return np.array([-2 * np.sum(x * r), -2 * np.sum(r)])

print("perte en (0, 0)     :", perte(0, 0))
print("gradient en (0, 0)  :", grad_perte(0, 0))

# la droite des moindres carrés (calculée en 1.3) : a = 1,5 et b = 1/3
a_opt, b_opt = 1.5, 1 / 3
print("perte en (1,5 ; 1/3) :", round(perte(a_opt, b_opt), 4))
print("gradient en (1,5 ; 1/3) :", (grad_perte(a_opt, b_opt).round(10) + 0))
```
<!--sortie-->
```text
perte en (0, 0)     : 38.0
gradient en (0, 0)  : [-46. -20.]
perte en (1,5 ; 1/3) : 0.1667
gradient en (1,5 ; 1/3) : [0. 0.]
```

Au point $(a, b) = (1{,}5\;;\;1/3)$, le gradient est **nul** : on est au fond du bol. À la main : les erreurs valent alors $r = (2 - \tfrac{11}{6},\; 3 - \tfrac{10}{3},\; 5 - \tfrac{29}{6}) = (\tfrac16,\,-\tfrac13,\,\tfrac16)$, donc $\sum r_i = 0$ et $\sum x_i r_i = \tfrac16 - \tfrac23 + \tfrac12 = 0$, et la perte vaut $L = \tfrac1{36} + \tfrac19 + \tfrac1{36} = \tfrac16 \approx 0{,}167$. Nous montrerons en 1.3 comment y arriver automatiquement.

> ✅ **À retenir (gradient).**
>
> - Le gradient $\nabla f$ rassemble les dérivées partielles ; il pointe vers la **plus forte montée** et sa norme mesure la pente.
> - $-\nabla f$ pointe vers la plus forte **descente**.
> - Au minimum (ou au maximum, ou au col), le gradient est nul.
> - La règle de la composée rend le calcul du gradient d'une « somme de carrés d'erreurs » mécanique : c'est le cœur de l'entraînement des modèles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.6, exercice 1.5.

### 1.2.3 Intégrales : accumuler les petits changements

> 💡 **Intuition.** L'intégrale est l'opération inverse de la dérivée. Si la dérivée donne « la vitesse à chaque instant », l'**intégrale** donne « la distance parcourue sur un intervalle » : elle **additionne une infinité de petits morceaux**. Graphiquement, c'est l'**aire sous la courbe**.
>
> En data science, l'intégrale sert surtout à une chose : calculer des **probabilités**. Quand une quantité est décrite par une courbe de densité, la probabilité d'un événement est l'aire sous la courbe sur la zone concernée.

#### Calculer une aire avec des rectangles

L'aire sous une courbe $f$ entre $a$ et $b$ se note $\displaystyle\int_a^b f(x)\,dx$. L'idée de **Riemann** : découper l'intervalle en $n$ bandes étroites, approcher chaque bande par un rectangle de hauteur $f(x)$, et additionner. Plus $n$ est grand, meilleure est l'approximation.

> 🧪 **Exemple à la main.** Aire sous $f(x) = x^2$ entre 0 et 3, avec $n = 3$ rectangles de largeur 1 (hauteur mesurée au bord droit) : $1\cdot 1^2 + 1 \cdot 2^2 + 1\cdot 3^2 = 1 + 4 + 9 = 14$. C'est une approximation grossière (les rectangles dépassent la courbe). Avec $n = 6$ rectangles de largeur $0{,}5$ : $0{,}5\,(0{,}5^2 + 1^2 + 1{,}5^2 + 2^2 + 2{,}5^2 + 3^2) = 0{,}5 \times 22{,}75 = 11{,}375$. Mieux ! En continuant avec de plus en plus de rectangles, on obtient :

| $n$ | 3 | 6 | 30 | 300 | 3000 |
|---|---|---|---|---|---|
| aire approchée | 14,000 | 11,375 | 9,455 | 9,045 | 9,005 |

```python hide
def riemann(f, a, b, n):
    largeur = (b - a) / n
    xs = a + largeur * np.arange(1, n + 1)        # extrémités droites des bandes
    return np.sum(f(xs)) * largeur

for n in [3, 6, 30, 300, 3000]:
    print(f"n = {n:>4} rectangles : aire ≈ {riemann(lambda t: t**2, 0, 3, n):.4f}")
print("valeur exacte : 3^3 / 3 =", 3**3 / 3)
```
<!--sortie-->
```text
n =    3 rectangles : aire ≈ 14.0000
n =    6 rectangles : aire ≈ 11.3750
n =   30 rectangles : aire ≈ 9.4550
n =  300 rectangles : aire ≈ 9.0451
n = 3000 rectangles : aire ≈ 9.0045
valeur exacte : 3^3 / 3 = 9.0
```

Les approximations convergent vers **9** (la valeur exacte). L'intégrale *est* cette limite.

#### Le théorème fondamental : la dérivée à l'envers

Faut-il toujours découper en rectangles ? Heureusement non. Le **théorème fondamental de l'analyse** relie intégrale et dérivée :

> Si $F$ est une **primitive** de $f$ (c'est-à-dire $F' = f$), alors
> $$\int_a^b f(x)\,dx = F(b) - F(a).$$

> 🧪 **Exemple.** Pour $f(x) = x^2$, une primitive est $F(x) = x^3/3$ (car $(x^3/3)' = x^2$). Donc $\int_0^3 x^2\,dx = F(3) - F(0) = 9 - 0 = 9$. ✔ C'est la valeur vers laquelle convergeaient nos rectangles.

Quelques primitives à connaître :

| $f(x)$ | une primitive $F(x)$ |
|---|---|
| $x^n$ ($n \ne -1$) | $\dfrac{x^{n+1}}{n+1}$ |
| $e^{kx}$ | $\dfrac{e^{kx}}{k}$ |
| $\dfrac{1}{x}$ | $\ln\lvert x\rvert$ |

> 📐 **Pourquoi ça marche : l'idée de la preuve.** Notons $A(x) = \int_a^x f(t)\,dt$ l'aire accumulée jusqu'en $x$. Quand $x$ avance de $h$, l'aire gagne une fine bande de largeur $h$ et de hauteur à peu près $f(x)$ : $A(x+h) - A(x) \approx f(x)\,h$. En divisant par $h$ et en faisant tendre $h$ vers 0, on obtient $A'(x) = f(x)$. L'aire accumulée est donc **une** primitive de $f$ ; deux primitives ne diffèrent que d'une constante, qui disparaît dans la différence $F(b) - F(a)$. $\blacksquare$ (Preuve simplifiée, suffisante pour l'intuition.)

#### Un exemple : une commande dans les trois prochaines minutes ?

Sur le site de la boutique, en heure de pointe, une commande arrive en moyenne toutes les 2 minutes. On montrera au chapitre 2 que le temps d'attente $T$ (en minutes) avant la prochaine commande suit une **loi exponentielle** de taux $\lambda = 0{,}5$ par minute, dont la densité est

$$f(t) = \lambda\,e^{-\lambda t} = 0{,}5\,e^{-0{,}5\,t}, \qquad t \ge 0.$$

La probabilité qu'une commande arrive dans les 3 prochaines minutes est l'aire sous cette courbe entre 0 et 3.

> 🧪 **À la main.** Une primitive de $0{,}5\,e^{-0{,}5t}$ est $-e^{-0{,}5t}$ (on dérive : $-(-0{,}5)e^{-0{,}5t} = 0{,}5\,e^{-0{,}5t}$ ✔). Donc
>
> $$P(T \le 3) = \bigl[-e^{-0{,}5\,t}\bigr]_0^3 = -e^{-1{,}5} - (-e^{0}) = 1 - e^{-1{,}5} \approx 0{,}777.$$

```python hide
from scipy.integrate import quad

lam = 0.5
densite = lambda t: lam * np.exp(-lam * t)

p_riemann = riemann(densite, 0, 3, 3000)
p_quad, _ = quad(densite, 0, 3)
print("rectangles de Riemann (3000) :", round(p_riemann, 5))
print("intégration numérique (quad)  :", round(p_quad, 5))
print("formule  1 - exp(-1,5)        :", round(1 - np.exp(-1.5), 5))

total, _ = quad(densite, 0, np.inf)
print("aire totale sous la courbe    :", round(total, 5))
```
<!--sortie-->
```text
rectangles de Riemann (3000) : 0.77668
intégration numérique (quad)  : 0.77687
formule  1 - exp(-1,5)        : 0.77687
aire totale sous la courbe    : 1.0
```

![Densité du temps d'attente avant la prochaine commande. L'aire grisée entre 0 et 3 minutes vaut 0,777 : il y a environ 78 % de chances qu'une commande arrive dans les trois prochaines minutes.](figures/ch01-attente-densite.png)

**Lecture.** Le calcul exact et une intégration numérique concordent : environ **77,7 %** de chances. Et l'aire **totale** sous la courbe vaut 1 : c'est une exigence de toute densité de probabilité (la probabilité que *quelque chose* arrive est de 100 %). Nous reverrons ces idées en détail au chapitre 2.

> ⚠️ **Piège : les aires sous l'axe comptent négativement.** Si $f$ est négative sur une partie de l'intervalle, l'intégrale en tient compte avec un signe moins. L'intégrale mesure une quantité **algébrique** accumulée, pas toujours une surface géométrique.

> ✅ **À retenir (intégrale).**
>
> - $\int_a^b f(x)\,dx$ est l'aire (algébrique) sous la courbe entre $a$ et $b$ : une limite de sommes de rectangles.
> - Théorème fondamental : $\int_a^b f = F(b) - F(a)$ où $F' = f$.
> - Pour une densité de probabilité, l'aire sous la courbe sur une zone **est** la probabilité de cette zone ; l'aire totale vaut 1.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7.
