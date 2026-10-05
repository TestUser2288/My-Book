# Rappel express : les bases à avoir en tête

*Quelques pages pour remettre en route ce qu'on a vu au collège et au lycée. Rien ici n'est nouveau : tout sert dans la suite du livre. Si tout vous semble évident, passez directement au chapitre 1.*

## R.1 Fractions et pourcentages

Une **fraction** est une division : $\frac{3}{4}$ veut dire « 3 divisé par 4 », soit $0{,}75$. Pour additionner deux fractions, on les met sur le même dénominateur :

$$\frac{3}{4} + \frac{5}{6} = \frac{3 \times 3}{4 \times 3} + \frac{5 \times 2}{6 \times 2} = \frac{9}{12} + \frac{10}{12} = \frac{19}{12}.$$

Un **pourcentage** est une fraction de dénominateur 100. « Prendre 25 % de 120 DT » revient à calculer $120 \times \frac{25}{100} = 30$ DT.

> 🧪 **Exemple (Dar Jasmin).** Un tapis coûte 240 DT. Yasmine propose une remise de 15 %.
>
> - Montant de la remise : $240 \times 0{,}15 = 36$ DT.
> - Nouveau prix : $240 - 36 = 204$ DT, ou directement $240 \times 0{,}85 = 204$ DT.
>
> **Astuce** : « baisser de 15 % » revient à **multiplier par 0,85**. « Augmenter de 19 % » (la TVA) revient à multiplier par 1,19.

> ⚠️ **Piège.** Une hausse de 20 % suivie d'une baisse de 20 % **ne ramène pas** au prix de départ : $100 \to 120 \to 96$. Les pourcentages se multiplient, ils ne s'additionnent pas.

```python
prix = 100
prix = prix * 1.20   # +20 %
prix = prix * 0.80   # -20 %
print(prix)
```
<!--sortie-->
```text
96.0
```

## R.2 Puissances et racines

$a^n$ signifie « $a$ multiplié $n$ fois par lui-même » : $2^3 = 2 \times 2 \times 2 = 8$. Les règles à connaître :

$$a^m \times a^n = a^{m+n}, \qquad \frac{a^m}{a^n} = a^{m-n}, \qquad (a^m)^n = a^{mn}, \qquad a^0 = 1, \qquad a^{-n} = \frac{1}{a^n}.$$

La **racine carrée** $\sqrt{a}$ est le nombre positif dont le carré vaut $a$ : $\sqrt{49} = 7$. On a aussi $\sqrt{a} = a^{1/2}$.

> 🧪 **Exemple.** $2^{10} = 1024$ ; $10^{-2} = 0{,}01$ ; $\sqrt{2} \approx 1{,}414$. Et $2^3 \times 2^4 = 2^7 = 128$, qu'on vérifie : $8 \times 16 = 128$.

## R.3 Équations et fonctions affines

Résoudre une équation du premier degré, c'est isoler l'inconnue en faisant la **même opération des deux côtés** :

$$2x - 7 = 11 \;\Longrightarrow\; 2x = 18 \;\Longrightarrow\; x = 9.$$

Une **fonction affine** s'écrit $y = ax + b$. Le nombre $a$ est la **pente** (de combien $y$ augmente quand $x$ augmente de 1), et $b$ est l'**ordonnée à l'origine** (la valeur de $y$ quand $x = 0$).

> 🧪 **Exemple.** Les frais de livraison de Dar Jasmin valent 5 DT de forfait plus 0,80 DT par kilo. Si $x$ est le poids en kilos :
>
> $$\text{frais}(x) = 0{,}8\,x + 5.$$
>
> Pour un colis de 6 kg : $0{,}8 \times 6 + 5 = 9{,}8$ DT. La pente (0,8) est le coût d'un kilo de plus ; l'ordonnée à l'origine (5) est le forfait.

Cette idée, « une pente et une ordonnée à l'origine », reviendra souvent : c'est la base de la régression linéaire.

## R.4 Le symbole $\sum$ (somme)

En statistique, on additionne sans arrêt. Pour ne pas écrire $x_1 + x_2 + \dots + x_n$ à chaque fois, on utilise le grand sigma :

$$\sum_{i=1}^{n} x_i = x_1 + x_2 + \dots + x_n.$$

Cela se lit : « somme, pour $i$ allant de 1 à $n$, des $x_i$ ». C'est exactement une boucle `for` qui additionne.

> 🧪 **Exemple.** Les ventes de Dar Jasmin sur cinq jours (en dinars) : $x_1 = 120,\; x_2 = 80,\; x_3 = 200,\; x_4 = 100,\; x_5 = 150$.
>
> $$\sum_{i=1}^{5} x_i = 120 + 80 + 200 + 100 + 150 = 650 \text{ DT.}$$
>
> La **moyenne** est $\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i = \frac{650}{5} = 130$ DT.

```python
ventes = [120, 80, 200, 100, 150]
total = sum(ventes)
moyenne = total / len(ventes)
print(total, moyenne)
```
<!--sortie-->
```text
650 130.0
```

Deux propriétés utiles (elles se vérifient en écrivant les sommes) :

$$\sum (x_i + y_i) = \sum x_i + \sum y_i, \qquad \sum c\,x_i = c \sum x_i \quad (c \text{ constante}).$$

## R.5 Exponentielle et logarithme

Le **logarithme** répond à la question : « *à quelle puissance faut-il élever la base pour obtenir ce nombre ?* ». Ainsi $\log_{10}(1000) = 3$, car $10^3 = 1000$.

En data science, on utilise surtout le **logarithme népérien** $\ln$ (base $e \approx 2{,}718$), et son opposé, la **fonction exponentielle** $e^x$. Ce qu'il faut savoir :

$$\ln(ab) = \ln a + \ln b, \qquad \ln(a^n) = n \ln a, \qquad \ln(e^x) = x, \qquad e^{a+b} = e^a e^b.$$

> 💡 **Intuition.** Le logarithme transforme les **produits en sommes**. C'est précieux : une somme est bien plus facile à manipuler (et à dériver) qu'un produit. C'est la raison pour laquelle, plus tard, nous prendrons le log de produits de probabilités pour estimer des paramètres.

> 🧪 **Exemple.** Un placement double tous les 10 ans. Après 30 ans, il a été multiplié par $2^3 = 8$. Combien de « doublements » faut-il pour multiplier par 1000 ? $\log_2(1000) \approx 9{,}97$, soit environ 10 doublements.

```python
import math
print(math.log10(1000))        # logarithme en base 10
print(math.log2(1000))         # logarithme en base 2
print(math.log(math.e**5))     # ln(e^5)
```
<!--sortie-->
```text
3.0
9.965784284662087
5.0
```

## R.6 Fonctions, graphes et équations de droites

Une **fonction** associe à chaque entrée $x$ une sortie $f(x)$. Son **graphe** est la courbe des points $(x, f(x))$. Quelques fonctions que nous croiserons :

| Fonction | Forme | Allure |
|---|---|---|
| affine | $ax + b$ | droite |
| carré | $x^2$ | parabole (« bol », avec un minimum en 0) |
| exponentielle | $e^x$ | croît de plus en plus vite |
| logarithme | $\ln x$ | croît de plus en plus lentement |
| racine | $\sqrt{x}$ | croît lentement |

## R.7 Un peu de vocabulaire de programmation

Avant de lire du code, retenez trois mots :

- une **variable** : un nom pour une valeur (`prix = 45.0`) ;
- une **fonction** : une recette réutilisable (`sum([1, 2, 3])` renvoie 6) ;
- une **liste** : une suite ordonnée de valeurs (`[120, 80, 200]`).

Le reste sera expliqué quand il apparaîtra, et le chapitre 4 reprend tout depuis le début.

## Faites le point

Si vous savez répondre à ces cinq questions, vous avez tout ce qu'il faut pour commencer :

1. Quel est le prix final d'un article à 80 DT avec 19 % de TVA ?
2. Que vaut $\sum_{i=1}^{4} i^2$ ?
3. Quelle est la pente de $y = -3x + 10$ ?
4. Simplifiez $\ln(e^2 \times e^3)$.
5. Combien font $\sqrt{81} + 2^{-1}$ ?

**Réponses.** (1) $80 \times 1{,}19 = 95{,}2$ DT. (2) $1 + 4 + 9 + 16 = 30$. (3) $-3$ (la droite descend). (4) $\ln(e^5) = 5$. (5) $9 + 0{,}5 = 9{,}5$.
