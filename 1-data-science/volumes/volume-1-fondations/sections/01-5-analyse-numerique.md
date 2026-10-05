## 1.5 ➕ Pour aller plus loin : analyse numérique

> 🧭 **Section optionnelle.** Vous pouvez la sauter sans perdre le fil du livre. Mais si un jour votre code donne un résultat « presque juste » et que vous ne comprenez pas pourquoi, c'est ici qu'est la réponse.

Les mathématiques des sections précédentes travaillent avec des nombres **exacts**. Un ordinateur, lui, n'en a pas : il stocke des nombres avec un nombre **fini** de chiffres. L'**analyse numérique** étudie ce que cela change. Bonne nouvelle : on peut tout comprendre avec quelques expériences.

### 1.5.1 Pourquoi 0,1 + 0,2 n'est pas égal à 0,3

> 💡 **Intuition.** En base 10, le nombre $1/3 = 0{,}3333\ldots$ ne s'écrit pas avec un nombre fini de chiffres. Il en va de même en base 2 pour $0{,}1$ : l'ordinateur en garde une **approximation**, très bonne mais pas exacte.

```python
print(0.1 + 0.2)
print(0.1 + 0.2 == 0.3)
print(f"{0.1:.25f}")
print(f"{0.3:.25f}")
```
<!--sortie-->
```text
0.30000000000000004
False
0.1000000000000000055511151
0.2999999999999999888977698
```

Les nombres décimaux de Python (type `float`) suivent la norme IEEE 754 en **double précision** : 64 bits, soit environ **16 chiffres significatifs**. L'erreur relative maximale d'un arrondi est appelée **epsilon machine** ; elle vaut environ $2{,}2\times10^{-16}$.

```python hide
import numpy as np
print("epsilon machine :", np.finfo(float).eps)
```
<!--sortie-->
```text
epsilon machine : 2.220446049250313e-16
```

> ✅ **Règle d'or.** On ne compare **jamais** deux flottants avec `==`. On teste s'ils sont *proches* :

```python
import math
print(math.isclose(0.1 + 0.2, 0.3))
print(np.isclose(0.1 + 0.2, 0.3))
```
<!--sortie-->
```text
True
True
```

Autre piège du même type, que nous avons rencontré en préparant ce livre : demander le logarithme de 1000 en base 10.

```python
print(math.log(1000, 10))      # calcule log(1000)/log(10) : deux arrondis
print(math.log10(1000))        # fonction dédiée : exacte ici
```
<!--sortie-->
```text
2.9999999999999996
3.0
```

Morale : quand une fonction **dédiée** existe (`log10`, `expm1`, `hypot`…), elle est plus précise que la formule naïve.

### 1.5.2 Les grands nombres avalent les petits

Additionner un très petit nombre à un très grand peut ne **rien changer** :

```python
print(1e16 + 1 == 1e16)
print(1e15 + 1 == 1e15)
```
<!--sortie-->
```text
True
False
```

Conséquence pratique : l'**ordre** des additions compte. Additionner un million de fois $0{,}1$ ne donne pas exactement 100 000 : une boucle d'additions successives renvoie $100\,000{,}000\,001\,33\ldots$, alors qu'une somme « compensée » (la fonction `math.fsum`) renvoie $100\,000{,}0$, exacte à l'arrondi final.

```python hide
s = 0.0
for _ in range(1_000_000):
    s += 0.1
print(s)
print(math.fsum([0.1] * 1_000_000))     # somme compensée : exacte à l'arrondi final
```
<!--sortie-->
```text
100000.00000133288
100000.0
```

### 1.5.3 L'annulation catastrophique

C'est le piège le plus important pour un data scientist. Quand on **soustrait deux nombres presque égaux**, les premiers chiffres s'annulent et il ne reste que… du bruit d'arrondi.

> 💡 **Intuition.** Vous mesurez deux immeubles de 300,00 m et 300,01 m, avec une règle précise au mètre près. Leur différence (0,01 m) est noyée dans l'imprécision.

Exemple réel : le calcul de la **variance**. Il existe deux formules équivalentes en mathématiques :

- formule stable : $\displaystyle \operatorname{Var} = \frac1n\sum (x_i - \bar{x})^2$ ;
- formule « du calcul à la main » : $\displaystyle \operatorname{Var} = \overline{x^2} - \bar{x}^2$ (moyenne des carrés moins carré de la moyenne).

Appliquons les deux à des chiffres d'affaires de l'ordre du milliard, avec une petite dispersion :

```python
rng = np.random.default_rng(0)
x = 1e9 + rng.normal(0, 1, size=1000)          # moyenne ~ 1 milliard, écart-type ~ 1

var_stable = np.mean((x - x.mean()) ** 2)
var_naive  = np.mean(x ** 2) - x.mean() ** 2

print("formule stable :", round(var_stable, 6))
print("formule naive  :", var_naive)
```
<!--sortie-->
```text
formule stable : 0.954046
formule naive  : -128.0
```

La vraie variance vaut environ 1. La formule stable la retrouve (0,95) ; la naïve donne **−128**, une variance *négative*, ce qui est impossible ! Elle est fausse, car $\overline{x^2}\approx 10^{18}$ et $\bar{x}^2\approx 10^{18}$ sont deux nombres presque égaux dont la différence est de l'ordre de 1 : on soustrait des nombres de 18 chiffres avec seulement 16 chiffres de précision.

> ⚠️ **Conséquence.** NumPy et pandas utilisent des algorithmes stables, pas la formule naïve. Moralité : **faites confiance aux fonctions des bibliothèques** plutôt que de recoder des formules vues en cours.

> 📐 **Pourquoi mathématiquement ?** Si $a$ et $b$ sont connus avec une erreur relative $\varepsilon$, leur différence $a-b$ a une erreur **absolue** d'environ $\varepsilon(|a|+|b|)$, donc une erreur **relative** de $\varepsilon\,\dfrac{|a|+|b|}{|a-b|}$. Quand $a \approx b$, le quotient est gigantesque : l'erreur relative explose.

### 1.5.4 Le conditionnement : quand un problème est « fragile »

Certains problèmes sont intrinsèquement sensibles : un minuscule changement des données change beaucoup la réponse. On mesure cette sensibilité par le **nombre de conditionnement** d'une matrice,

$$\kappa(\mathbf{A}) = \frac{\sigma_{\max}}{\sigma_{\min}},$$

le rapport entre sa plus grande et sa plus petite valeur singulière (section 1.1.4). Si $\kappa$ est grand, la matrice est « presque singulière » : c'est exactement le cas de la **multicollinéarité** vue au 1.1.

Voici un système $\mathbf{A}\mathbf{x}=\mathbf{b}$ dont les deux équations sont presque identiques :

```python
A = np.array([[1.0, 1.0],
              [1.0, 1.0001]])
b = np.array([2.0, 2.0001])
print("solution :", np.linalg.solve(A, b))
print("conditionnement :", round(np.linalg.cond(A)))
```
<!--sortie-->
```text
solution : [1. 1.]
conditionnement : 40002
```

Perturbons légèrement le second membre (changement de $10^{-4}$) :

```python
b2 = np.array([2.0, 2.0002])
print("solution perturbée :", np.linalg.solve(A, b2))
```
<!--sortie-->
```text
solution perturbée : [0. 2.]
```

Un changement de $0{,}0001$ sur les données a **complètement changé la solution** : de $(1, 1)$ à $(0, 2)$. Le conditionnement est de l'ordre de 40 000 : on peut perdre jusqu'à 4 à 5 chiffres de précision.

> ✅ **Règle empirique.** Avec $\kappa \approx 10^k$, on perd environ $k$ chiffres significatifs sur les 16 disponibles.

Deux conséquences pratiques :

1. Pour résoudre $\mathbf{A}\mathbf{x}=\mathbf{b}$, on utilise `np.linalg.solve(A, b)`, **pas** `np.linalg.inv(A) @ b` : c'est plus rapide **et** plus précis.
2. Centrer et standardiser les variables (1.3.3) diminue le conditionnement, ce qui explique en partie le gain de 335 à 18 itérations : sur notre exemple, $\kappa(\mathbf{X}^\top\mathbf{X})$ passe de $46{,}1$ à $1{,}5$.

```python hide
x = np.array([1.0, 2.0, 3.0])
X_brut = np.column_stack([x, np.ones(3)])
X_centre = np.column_stack([x - x.mean(), np.ones(3)])
print("kappa(X^T X) brut   :", round(np.linalg.cond(X_brut.T @ X_brut), 1))
print("kappa(X^T X) centré :", round(np.linalg.cond(X_centre.T @ X_centre), 1))
```
<!--sortie-->
```text
kappa(X^T X) brut   : 46.1
kappa(X^T X) centré : 1.5
```

### 1.5.5 Deux algorithmes classiques

**La méthode de Newton pour résoudre $f(x)=0$.** Idée : on remplace la courbe par sa **tangente** (1.2.1) et on prend l'endroit où la tangente coupe l'axe des abscisses :

$$x_{k+1} = x_k - \frac{f(x_k)}{f'(x_k)}.$$

Pour calculer $\sqrt{2}$, on cherche le zéro de $f(x) = x^2 - 2$, avec $f'(x) = 2x$, donc $x_{k+1} = x_k - \dfrac{x_k^2 - 2}{2x_k}$. En partant de $x_0 = 1$ :

| étape | $x$ | erreur |
|---|---|---|
| 0 | 1,000000000000000 | $4{,}1\times10^{-1}$ |
| 1 | 1,500000000000000 | $8{,}6\times10^{-2}$ |
| 2 | 1,416666666666667 | $2{,}5\times10^{-3}$ |
| 3 | 1,414215686274510 | $2{,}1\times10^{-6}$ |
| 4 | 1,414213562374690 | $1{,}6\times10^{-12}$ |
| 5 | 1,414213562373095 | 0 |


```python hide
x = 1.0
for k in range(6):
    print(f"étape {k} : x = {x:.15f}   erreur = {abs(x - 2**0.5):.2e}")
    x = x - (x**2 - 2) / (2 * x)
```
<!--sortie-->
```text
étape 0 : x = 1.000000000000000   erreur = 4.14e-01
étape 1 : x = 1.500000000000000   erreur = 8.58e-02
étape 2 : x = 1.416666666666667   erreur = 2.45e-03
étape 3 : x = 1.414215686274510   erreur = 2.12e-06
étape 4 : x = 1.414213562374690   erreur = 1.59e-12
étape 5 : x = 1.414213562373095   erreur = 0.00e+00
```

Le nombre de chiffres justes **double** à chaque étape (on parle de convergence quadratique). C'est ainsi que votre calculatrice calcule vraiment les racines carrées.

**La dichotomie.** Plus lente mais beaucoup plus robuste : si $f$ est continue et change de signe entre $a$ et $b$, il existe un zéro entre les deux. On coupe l'intervalle en deux, on garde la moitié qui change de signe, et on recommence. L'erreur est divisée par 2 à chaque tour.

```python hide
def dichotomie(f, a, b, tol=1e-10):
    n = 0
    while b - a > tol:
        m = (a + b) / 2
        if f(a) * f(m) <= 0:
            b = m
        else:
            a = m
        n += 1
    return (a + b) / 2, n

racine, n = dichotomie(lambda x: x**2 - 2, 0, 2)
print(f"racine = {racine:.10f} en {n} étapes")
```
<!--sortie-->
```text
racine = 1.4142135624 en 35 étapes
```

Pour $\sqrt{2}$ sur l'intervalle $[0, 2]$ avec une tolérance de $10^{-10}$, il faut 35 étapes à la dichotomie, contre 5 à Newton, pour une précision comparable. Newton est rapide mais peut diverger si on part mal ; la dichotomie est lente mais ne rate jamais. Les bibliothèques (`scipy.optimize.brentq`) combinent les deux.

> ✅ **À retenir (analyse numérique).**
>
> - Un flottant a ~16 chiffres significatifs ; on compare avec `isclose`, jamais avec `==`.
> - Soustraire deux nombres proches détruit la précision (annulation) : préférez les fonctions de bibliothèque.
> - Le conditionnement $\kappa$ mesure la fragilité d'un problème ; on perd environ $\log_{10}\kappa$ chiffres.
> - `solve` plutôt que `inv`. Centrer et standardiser améliore le conditionnement.
> - Newton : rapide mais capricieux ; dichotomie : lente mais sûre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : exercice 1.9.
