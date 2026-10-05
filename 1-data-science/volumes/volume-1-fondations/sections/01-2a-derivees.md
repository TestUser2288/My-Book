## 1.2 Analyse : mesurer le changement

L'algèbre linéaire nous a appris à décrire des données. L'**analyse** nous apprend à décrire comment les choses **changent**. C'est ce qui permet de répondre à des questions comme : « si j'augmente mon prix d'un dinar, mes recettes montent-elles ou descendent-elles, et de combien ? ». Elle repose sur deux notions : la **dérivée** (le changement instantané) et l'**intégrale** (le changement accumulé).

### 1.2.1 La dérivée : la vitesse à laquelle une fonction change

> 💡 **Intuition.** Si une fonction décrit **où vous en êtes**, sa dérivée décrit **à quelle vitesse vous avancez**. Dans une voiture, la distance parcourue est la fonction ; le compteur de vitesse affiche sa dérivée. Graphiquement, la dérivée en un point est la **pente de la tangente** à la courbe en ce point.

#### Une fonction pour commencer

Une **fonction** associe à chaque valeur d'entrée $x$ une valeur de sortie $f(x)$. Voici celle que nous utiliserons dans cette section : le bénéfice hebdomadaire de Yasmine pour une poterie, en fonction du nombre $q$ de pièces vendues. Plus elle en vend, plus elle doit baisser le prix, et il y a 300 DT de frais fixes :

$$P(q) = -2q^2 + 80q - 300.$$

Par exemple, $P(20) = -2\cdot 400 + 1600 - 300 = 500$ DT.

#### D'abord, une idée de limite

Pour définir la dérivée, il faut la notion de **limite** : la valeur *vers laquelle tend* une quantité quand on s'approche d'un point, même si l'on ne peut pas l'atteindre.

> 🧪 **Exemple.** Considérons $f(x) = \dfrac{x^2 - 1}{x - 1}$. Elle n'est pas définie en $x = 1$ (division par zéro). Mais que se passe-t-il quand $x$ s'en approche ?

```python
import numpy as np

def f(x):
    return (x**2 - 1) / (x - 1)

for x in [0.9, 0.99, 0.999, 1.001, 1.01, 1.1]:
    print(f"x = {x:<6}  f(x) = {f(x):.4f}")
```
<!--sortie-->
```text
x = 0.9     f(x) = 1.9000
x = 0.99    f(x) = 1.9900
x = 0.999   f(x) = 1.9990
x = 1.001   f(x) = 2.0010
x = 1.01    f(x) = 2.0100
x = 1.1     f(x) = 2.1000
```

On voit que $f(x)$ se rapproche de **2**. On écrit $\lim_{x \to 1} f(x) = 2$. (Algébriquement, $x^2 - 1 = (x-1)(x+1)$, donc $f(x) = x + 1$ dès que $x \ne 1$.) Une limite décrit un comportement **au voisinage** d'un point, pas au point lui-même.

#### Définition de la dérivée

Comment mesurer la pente d'une courbe en un seul point ? Une pente se mesure entre deux points. L'idée est donc de prendre deux points très proches, $x$ et $x + h$, et de regarder la pente de la droite qui les relie : le **taux d'accroissement**

$$\frac{f(x + h) - f(x)}{h}.$$

Puis de faire tendre $h$ vers zéro. La **dérivée** est la limite, quand elle existe :

$$f'(x) = \lim_{h \to 0} \frac{f(x + h) - f(x)}{h}.$$

> 🧪 **Exemple chiffré.** Prenons $f(x) = x^2$ au point $x = 3$ et rapprochons $h$ de zéro :

```python
def carre(x):
    return x**2

for h in [1, 0.1, 0.01, 0.001, 0.0001]:
    taux = (carre(3 + h) - carre(3)) / h
    print(f"h = {h:<7} taux d'accroissement = {taux:.4f}")
```
<!--sortie-->
```text
h = 1       taux d'accroissement = 7.0000
h = 0.1     taux d'accroissement = 6.1000
h = 0.01    taux d'accroissement = 6.0100
h = 0.001   taux d'accroissement = 6.0010
h = 0.0001  taux d'accroissement = 6.0001
```

Les valeurs se rapprochent de **6**. Et $2 \times 3 = 6$ : la dérivée de $x^2$ semble être $2x$. Prouvons-le.

> 📐 **Démonstration : la dérivée de $x^2$ est $2x$.**
>
> $$\frac{(x+h)^2 - x^2}{h} = \frac{x^2 + 2xh + h^2 - x^2}{h} = \frac{2xh + h^2}{h} = 2x + h.$$
>
> Quand $h \to 0$, cette quantité tend vers $2x$. Donc $(x^2)' = 2x$. $\blacksquare$
>
> Notez que les calculs numériques ci-dessus suivent exactement ce résultat : le taux vaut $2\cdot 3 + h = 6 + h$, soit 7, 6,1, 6,01, 6,001, 6,0001.

#### Les règles de calcul

On ne recalcule pas une limite à chaque fois. On utilise des règles, qu'il faut connaître par cœur :

| Fonction | Dérivée | Exemple |
|---|---|---|
| constante $c$ | $0$ | $(7)' = 0$ |
| $x^n$ | $n\,x^{n-1}$ | $(x^3)' = 3x^2$ ; $(\sqrt{x})' = \frac{1}{2\sqrt{x}}$ |
| $e^{x}$ | $e^{x}$ | |
| $\ln x$ | $\dfrac1x$ | |
| somme $f + g$ | $f' + g'$ | $(x^2 + 5x)' = 2x + 5$ |
| multiple $c\,f$ | $c\,f'$ | $(4x^3)' = 12x^2$ |
| produit $f\,g$ | $f'g + fg'$ | $(x\,e^x)' = e^x + x\,e^x$ |
| composée $f(g(x))$ | $f'(g(x))\cdot g'(x)$ | voir ci-dessous |

La dernière règle, celle de la **dérivée d'une composée** (ou « règle de la chaîne »), est la plus importante pour la suite : c'est elle qui fait fonctionner l'entraînement de tous les réseaux de neurones. Elle dit : *dérivez l'extérieur sans toucher à l'intérieur, puis multipliez par la dérivée de l'intérieur.*

> 🧪 **Exemple.** $h(x) = (3x + 1)^2$. L'extérieur est « carré », l'intérieur est $3x + 1$.
>
> $$h'(x) = \underbrace{2\,(3x+1)}_{\text{dérivée de l'extérieur}} \times \underbrace{3}_{\text{dérivée de l'intérieur}} = 6(3x+1) = 18x + 6.$$
>
> **Contrôle** : en développant, $h(x) = 9x^2 + 6x + 1$, dont la dérivée est $18x + 6$. ✔
>
> Autre exemple, qui servira bientôt : $\dfrac{d}{dx}\,e^{-0{,}5x} = -0{,}5\,e^{-0{,}5x}$ (l'intérieur est $-0{,}5x$, de dérivée $-0{,}5$).

Pour **vérifier** une dérivée calculée à la main (ou dénicher une erreur), on peut la comparer à une dérivée numérique : on calcule la pente entre $x - h$ et $x + h$ pour un très petit $h$ (la « différence centrée »).

```python
def derivee_numerique(f, x, h=1e-6):
    return (f(x + h) - f(x - h)) / (2 * h)

tests = [
    ("x^3 en x = 2",       lambda x: x**3,             2.0, 3 * 2.0**2),
    ("(3x+1)^2 en x = 1",  lambda x: (3 * x + 1)**2,   1.0, 6 * (3 * 1.0 + 1)),
    ("exp(-0.5x) en x = 2", lambda x: np.exp(-0.5 * x), 2.0, -0.5 * np.exp(-1.0)),
    ("ln(2x) en x = 4",    lambda x: np.log(2 * x),    4.0, 1 / 4.0),
]
for nom, fonction, x0, exacte in tests:
    print(f"{nom:<20} numérique = {derivee_numerique(fonction, x0):9.6f}   formule = {exacte:9.6f}")
```
<!--sortie-->
```text
x^3 en x = 2         numérique = 12.000000   formule = 12.000000
(3x+1)^2 en x = 1    numérique = 24.000000   formule = 24.000000
exp(-0.5x) en x = 2  numérique = -0.183940   formule = -0.183940
ln(2x) en x = 4      numérique =  0.250000   formule =  0.250000
```

> ✅ **Bonne habitude.** Chaque fois que vous dérivez une expression compliquée, comparez-la à une dérivée numérique. Les erreurs de signe et les oublis de « fois la dérivée de l'intérieur » sont les fautes les plus courantes.

#### 🛠️ Application : à quel niveau de ventes le bénéfice est-il maximal ?

Reprenons $P(q) = -2q^2 + 80q - 300$. Observons-la d'abord :

```python
def benefice(q):
    return -2 * q**2 + 80 * q - 300

for q in [10, 15, 20, 25, 30]:
    print(f"q = {q:>2}   bénéfice = {benefice(q):>4} DT")
```
<!--sortie-->
```text
q = 10   bénéfice =  300 DT
q = 15   bénéfice =  450 DT
q = 20   bénéfice =  500 DT
q = 25   bénéfice =  450 DT
q = 30   bénéfice =  300 DT
```

Le bénéfice monte, atteint un sommet, puis redescend : c'est une parabole « en cloche ». **Au sommet, la tangente est horizontale, donc la dérivée est nulle.** C'est la clé de l'optimisation. On dérive :

$$P'(q) = -4q + 80.$$

On résout $P'(q) = 0$ : $-4q + 80 = 0$, donc $q = 20$ pièces, pour un bénéfice $P(20) = 500$ DT.

La dérivée a aussi une lecture économique directe : c'est le **bénéfice marginal**, le gain approximatif que rapporte la pièce supplémentaire. En $q = 10$, $P'(10) = -40 + 80 = 40$ DT. Vérifions avec la vraie différence :

```python
print("gain réel de la 11e pièce : P(11) - P(10) =", benefice(11) - benefice(10), "DT")
print("pente en q = 10           : P'(10) = -4*10 + 80 =", -4 * 10 + 80, "DT")
```
<!--sortie-->
```text
gain réel de la 11e pièce : P(11) - P(10) = 38 DT
pente en q = 10           : P'(10) = -4*10 + 80 = 40 DT
```

La pente (40) est une bonne approximation du gain réel (38) : elle est exacte pour une variation infiniment petite, et approchée pour une variation d'une pièce. Enfin, confirmons le sommet par une recherche numérique, sans utiliser la dérivée :

```python
from scipy.optimize import minimize_scalar

res = minimize_scalar(lambda q: -benefice(q), bounds=(0, 40), method="bounded")
print(f"optimum numérique : q = {res.x:.3f}, bénéfice = {-res.fun:.2f} DT")
```
<!--sortie-->
```text
optimum numérique : q = 20.000, bénéfice = 500.00 DT
```

(On minimise $-P$ puisque la fonction cherche un minimum : maximiser $P$ revient à minimiser $-P$.)

![Bénéfice hebdomadaire en fonction du nombre de pièces vendues. En q = 10 la tangente monte avec une pente de 40 ; en q = 20 elle est horizontale : c'est le sommet.](figures/ch01-benefice-tangentes.png)

#### Comment savoir si c'est un maximum ou un minimum ?

Une dérivée nulle signale un point **candidat**, pas forcément un maximum. On regarde alors la **dérivée seconde** $f''$ (la dérivée de la dérivée, qui mesure comment la pente elle-même change) :

- $f''(x) < 0$ : la pente décroît, la courbe est une « bosse », c'est un **maximum local** ;
- $f''(x) > 0$ : la pente croît, la courbe est un « creux », c'est un **minimum local** ;
- $f''(x) = 0$ : on ne peut pas conclure.

Ici $P''(q) = -4 < 0$ : c'est bien un maximum. 

> ⚠️ **Piège.** « Dérivée nulle » ne veut pas dire « extremum ». Pour $f(x) = x^3$, on a $f'(0) = 3\cdot 0^2 = 0$, et pourtant la fonction ne fait que croître : en 0, la tangente est horizontale mais la courbe continue de monter (c'est un *point d'inflexion*). Vérifiez toujours avec la dérivée seconde ou en comparant les valeurs de part et d'autre.

> ✅ **À retenir (dérivée).**
>
> - $f'(x)$ est la pente de la tangente en $x$ : c'est le taux de variation instantané.
> - Les cinq règles à maîtriser : puissances, somme, multiple, produit, composée.
> - Pour optimiser : on cherche $f'(x) = 0$, puis on contrôle avec $f''$.
> - Comparer une dérivée à la main à une dérivée numérique permet de détecter les erreurs.
