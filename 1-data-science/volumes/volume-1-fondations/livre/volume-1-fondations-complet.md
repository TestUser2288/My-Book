# DATA SCIENCE

## Volume I : Fondations

### Mathématiques, probabilités, statistique, programmation, bases de données et outils

*Série 1 : Data Science — de zéro aux applications en risque et assurance*

---

# Avant-propos

## Bienvenue

Ce livre est le premier d'une série de six volumes qui racontent, pas à pas, comment on devient data scientist : on part de ce qu'il y a de plus simple (additionner des nombres, ranger des données dans un tableau) et on arrive à ce qu'il y a de plus récent (modèles de langage, mise en production, modélisation du risque en banque et en assurance).

Ce premier volume est le **socle**. Il ne contient aucun modèle « à la mode » : ni réseau de neurones, ni intelligence artificielle spectaculaire. Il contient ce qui rend tout le reste possible :

- les **mathématiques** dont on a vraiment besoin (et seulement celles-là) ;
- les **probabilités**, qui donnent un langage précis à l'incertitude ;
- la **statistique**, qui apprend à tirer des conclusions honnêtes à partir de données imparfaites ;
- la **programmation**, pour que la machine fasse les calculs à notre place ;
- les **bases de données et le SQL**, pour aller chercher l'information là où elle vit ;
- les **outils de travail** (Git, notebooks, ligne de commande), pour travailler proprement et reproduire ses résultats.

Si vous ne deviez retenir qu'une idée de ce livre, ce serait celle-ci :

> **La data science n'est pas de la magie. C'est de l'artisanat : des mathématiques simples, du code propre et beaucoup de bon sens, appliqués avec méthode.**

Un artisan, ça se forme avec des gestes répétés. C'est pourquoi ce livre est rempli d'exemples chiffrés que vous pouvez refaire à la main, puis refaire avec l'ordinateur.

## À qui s'adresse ce livre ?

À toute personne qui veut apprendre le métier depuis le début :

- l'étudiant ou l'étudiante qui entre dans une filière de statistique, d'informatique ou d'ingénierie ;
- la personne en reconversion qui veut comprendre ce qu'il y a sous le capot des outils ;
- l'analyste qui sait faire des tableaux croisés et veut passer à la modélisation ;
- l'ingénieur ou l'ingénieure déjà formé(e) qui veut un ouvrage de référence clair pour réviser ses bases.

**Prérequis** : le niveau de mathématiques du lycée, de la curiosité, et un ordinateur. Aucune expérience de programmation n'est supposée. Si certaines notions de base sont rouillées, le « Rappel express » qui suit cet avant-propos les remet en route en quelques pages.

## Comment ce livre est construit

Les livres de mathématiques ont souvent deux défauts opposés. Certains sont **rigoureux mais froids** : des définitions, des théorèmes, des démonstrations, et on se demande à quoi tout cela sert. D'autres sont **sympathiques mais flous** : on a l'impression d'avoir compris, puis on ne sait plus rien refaire seul.

Ce volume essaie d'éviter les deux, en **alternant systématiquement** :

1. une **intuition** simple, avec une image ou une histoire ;
2. un **exemple chiffré** assez petit pour être refait à la main ;
3. quand c'est utile, une **démonstration rigoureuse**, pour que la certitude remplace la confiance aveugle ;
4. une **petite application réelle** que l'on exécute avec du code ;
5. des **exercices corrigés** pour vérifier que l'idée est bien entrée.

Chaque idée importante reçoit au moins un exemple « sans issue de secours » : un exemple si concret qu'on ne puisse plus se dire « je n'ai pas compris ».

### Les encadrés

Pour que la lecture reste fluide, chaque type de contenu a son pictogramme :

| Pictogramme | Rôle |
|---|---|
| 💡 **Intuition** | L'idée en langage courant, sans formule. À lire en premier. |
| 🧪 **Exemple** | Un calcul concret, souvent refait à la main. |
| 📐 **Démonstration** | Le raisonnement rigoureux. On peut la sauter à la première lecture, mais elle est ce qui rend la compréhension durable. |
| 🛠️ **Application** | Une petite application réelle, avec du code. |
| ⚠️ **Piège** | Une erreur classique, que presque tout le monde fait une fois. |
| ✅ **À retenir** | Le résumé à garder en mémoire. |
| 🏋️ **Exercices** | À faire avec un crayon avant de regarder les corrigés. |
| ➕ **Pour aller plus loin** | Section facultative : approfondissement, outil ou sujet connexe. |

### Le principe « essentiel / pour aller plus loin »

Dans chaque chapitre, tout ce qui n'est **pas** marqué ➕ constitue le **parcours essentiel**. Il est complet : un lecteur qui suit uniquement ce parcours acquiert la vue d'ensemble et les compétences utiles pour la suite de la série.

Les sections marquées **➕ Pour aller plus loin** sont des cadeaux, pas des obligations : elles approfondissent un point, présentent un outil de plus ou ouvrent une porte. Certains lecteurs préfèrent se concentrer sur la grande idée ; d'autres aiment creuser. Les deux manières de lire ce livre sont bonnes.

### Trois parcours de lecture

| Parcours | Pour qui | Que lire |
|---|---|---|
| **Essentiel** | Vous voulez la vue d'ensemble, vite | Les encadrés 💡 🧪 🛠️ ✅, sans les 📐 ni les ➕ |
| **Complet** | Vous voulez comprendre en profondeur | Tout le parcours essentiel, démonstrations comprises, plus les exercices |
| **Praticien** | Vous aimez coder avant de théoriser | Le chapitre 6 (outils), puis le 4 (programmation), puis le 5 (SQL), puis les chapitres 1 à 3 |

> 💡 **Vous n'avez jamais programmé ?** Pas de panique : chaque bloc de code est suivi de **sa sortie réelle**. On peut donc lire le livre sans rien exécuter et comprendre ce qui se passe. Quand vous serez prêt(e), le chapitre 4 (section 4.1) vous apprend Python depuis zéro.

## Le fil rouge : la boutique Dar Jasmin

Apprendre sur des données abstraites est ennuyeux. Tout au long de ce volume, nous travaillerons donc sur une même histoire :

> **Yasmine** vient de lancer **Dar Jasmin**, une boutique en ligne d'artisanat tunisien : poteries, huile d'olive, tapis, bijoux. Elle vend, elle livre, elle reçoit des retours. Elle a des questions ; vous allez l'aider à y répondre avec des données.

Voici quelques-unes de ses questions, et le chapitre où nous y répondrons :

| Question de Yasmine | Outil | Chapitre |
|---|---|---|
| « Quels clients se ressemblent ? » | vecteurs, similarité | 1 |
| « Comment ajuster mes prix pour maximiser le chiffre d'affaires ? » | optimisation | 1 |
| « Cette commande est-elle une fraude ? » | théorème de Bayes | 2 |
| « Combien de commandes dois-je prévoir à 14 h ? » | loi de Poisson | 2 |
| « Mon nouveau transporteur est-il vraiment plus rapide ? » | tests d'hypothèses | 3 |
| « Combien vaut mon panier moyen, à ±2 dinars près ? » | intervalle de confiance | 3 |
| « Comment automatiser mes rapports de ventes ? » | Python, pandas | 4 |
| « Quels sont mes dix meilleurs clients ? » | SQL | 5 |
| « Comment retrouver la version de mon analyse d'il y a un mois ? » | Git | 6 |

**Une précision importante :** Dar Jasmin et toutes ses données sont **fictifs**. Les chiffres sont générés par ordinateur, avec des règles simples que nous connaissons, ce qui permet de vérifier que nos méthodes retrouvent bien la réalité. Toute ressemblance avec une vraie boutique serait une coïncidence.

## Le code de ce livre

Les exemples de code sont écrits en **Python** (langage principal du livre), avec quelques exemples en **R** et en **SQL**. Chaque exemple Python ou SQL est suivi de sa sortie, introduite par un bloc grisé comme celui-ci :

```python
prix = [45.0, 12.5, 80.0]
print(f"Total du panier : {sum(prix):.2f} DT")
```
<!--sortie-->
```text
Total du panier : 137.50 DT
```

Les données aléatoires sont générées avec une **graine** (*seed*) fixée, ce qui fait qu'en rejouant le code, vous obtiendrez les mêmes nombres que dans le livre, à de très légères variations près selon les versions des bibliothèques.

Pour installer ce qu'il faut, un seul jeu de commandes suffit (détaillé au chapitre 6) :

```bash
python -m venv .venv
source .venv/bin/activate        # sous Windows : .venv\Scripts\activate
pip install numpy pandas scipy matplotlib seaborn
```

## La carte du volume

```text
 Chapitre 1 : Mathématiques ──┐
                              ├──► Chapitre 3 : Statistique ──► Volume II
 Chapitre 2 : Probabilités ───┘                │
                                               │
 Chapitre 4 : Programmation ──► Chapitre 5 : SQL ──► Chapitre 6 : Outils
                                               │
                                               ▼
                              Projet du volume : l'étude complète de Dar Jasmin
```

| Chapitre | Il répond à la question… | À la fin, vous saurez… |
|---|---|---|
| 1. Mathématiques | De quels outils mathématiques a-t-on besoin ? | manipuler vecteurs et matrices, dériver, minimiser une fonction |
| 2. Probabilités | Comment parler d'incertitude avec précision ? | calculer des probabilités, reconnaître les lois usuelles, comprendre la loi des grands nombres |
| 3. Statistique | Que peut-on conclure à partir d'un échantillon ? | estimer, construire un intervalle de confiance, tester une hypothèse |
| 4. Programmation | Comment faire calculer l'ordinateur ? | écrire du Python, manipuler des données avec pandas, tracer des graphiques |
| 5. SQL | Comment interroger une base de données ? | écrire des requêtes avec jointures, agrégations et fonctions fenêtres |
| 6. Outils | Comment travailler proprement ? | utiliser Git, des notebooks, la ligne de commande |

## Faites le point : un petit test de départ

Prenez dix minutes, un crayon, et répondez **sans calculatrice**. Les réponses sont juste après.

1. Calculez $\dfrac{3}{4} + \dfrac{5}{6}$.
2. Développez $(x + 2)^2$.
3. Résolvez $2x - 7 = 11$.
4. Quelle est la moyenne des nombres 4, 8, 15, 16, 23, 42 ?
5. On lance deux dés équilibrés. Quelle est la probabilité que la somme fasse 7 ?
6. Quelle est la dérivée de $x^2$ ?
7. Calculez $2^3 \times 2^4$.
8. Que vaut $\log_{10}(1000)$ ?
9. Un article coûte 120 DT. On applique 25 % de remise. Quel est le nouveau prix ?
10. Dans une phrase : à quoi sert une « variable » en programmation ?

**Réponses.**

1. $\frac{3}{4} + \frac{5}{6} = \frac{9}{12} + \frac{10}{12} = \frac{19}{12}$.
2. $(x+2)^2 = x^2 + 4x + 4$.
3. $2x = 18$, donc $x = 9$.
4. $(4+8+15+16+23+42)/6 = 108/6 = 18$.
5. Il y a $6 \times 6 = 36$ résultats possibles, dont 6 donnent 7 : (1,6), (2,5), (3,4), (4,3), (5,2), (6,1). Probabilité : $6/36 = 1/6$.
6. $2x$.
7. $2^{3+4} = 2^7 = 128$.
8. $3$, car $10^3 = 1000$.
9. $120 \times 0{,}75 = 90$ DT.
10. Une variable est un nom qui désigne une valeur gardée en mémoire (par exemple `prix = 45.0`), que l'on peut relire et modifier.

**Comment interpréter votre score ?**

- **8 à 10 bonnes réponses** : vous êtes prêt(e). Commencez par le chapitre 1.
- **5 à 7** : lisez d'abord le « Rappel express », puis commencez.
- **Moins de 5** : lisez le « Rappel express » attentivement, en refaisant les calculs à la main. Ce n'est pas une affaire de talent, seulement de pratique.

Maintenant, au travail. Yasmine nous attend, et sa boutique reçoit une commande à l'instant.


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


---

# Chapitre 1 : Mathématiques pour la data science

> « Un tableau de données, c'est une **matrice**.
> Un modèle, c'est une **fonction**.
> Apprendre, c'est **minimiser une erreur**. »

Ces trois phrases résument ce chapitre. Si elles vous paraissent mystérieuses, c'est normal : à la fin du chapitre, elles vous sembleront évidentes.

## Pourquoi des mathématiques ?

On entend parfois que « la data science, ce sont des bibliothèques Python : on appelle `fit()` et c'est fini ». C'est vrai… jusqu'au jour où le modèle donne un résultat absurde et où l'on doit comprendre pourquoi. Les mathématiques sont ce qui permet alors de **raisonner au lieu de deviner**.

Rassurez-vous : il ne s'agit pas de refaire un cursus de mathématiques. Il suffit de **quatre familles d'idées**, que nous construirons de zéro :

| Idée | Ce que c'est | À quoi ça sert en data science |
|---|---|---|
| **Vecteurs et matrices** | des listes et des tableaux de nombres, avec des règles de calcul | représenter les données, comparer des individus, réduire la dimension |
| **Dérivées et gradients** | la mesure de « à quelle vitesse ça change » | savoir dans quel sens améliorer un modèle |
| **Intégrales** | la mesure d'une « quantité accumulée » | calculer des probabilités (chapitre 2) |
| **Optimisation** | trouver le meilleur choix selon un critère | entraîner (presque) tous les modèles |

## Le chemin de ce chapitre

Nous allons suivre la boutique **Dar Jasmin** et ses questions concrètes :

- **1.1 Algèbre linéaire** : Yasmine veut savoir quels clients se ressemblent, calculer son chiffre d'affaires par mois sans boucle interminable, et résumer un tableau de ventes en quelques tendances.
- **1.2 Analyse** : comment son bénéfice change-t-il quand elle modifie un prix un tout petit peu ? Et quelle est la probabilité qu'une commande arrive dans les trois prochaines minutes ?
- **1.3 Optimisation** : quel prix maximise ses recettes ? Comment répartir son budget publicitaire ?
- **1.4 Fiche de notations** : toutes les notations du livre, au même endroit.
- ➕ **Pour aller plus loin** : pourquoi l'ordinateur se trompe parfois (analyse numérique), et comment compter et relier des objets (mathématiques discrètes et graphes).

> 💡 **Comment lire ce chapitre.** Chaque notion suit le même rythme : une intuition, un exemple chiffré à la main, puis (si nécessaire) une démonstration, puis le code. Si une démonstration vous décourage, sautez-la : l'exemple et le code suffisent pour avancer. Revenez-y plus tard.


## 1.1 Algèbre linéaire

L'algèbre linéaire est le langage des tableaux de nombres. Tout ce que fait un modèle de data science, de la régression la plus simple au réseau de neurones le plus profond, s'écrit avec elle. Nous allons en construire les quatre briques : **vecteurs**, **matrices**, **valeurs propres** et **décomposition en valeurs singulières**.

### 1.1.1 Vecteurs : décrire un client par une liste de nombres

> 💡 **Intuition.** Un **vecteur** est une liste ordonnée de nombres. On peut le voir de deux façons, qui sont les deux faces d'une même pièce :
>
> - comme une **flèche** partant de l'origine et pointant vers un point ;
> - comme la **fiche d'identité** d'un individu : une ligne de tableau où chaque case décrit une caractéristique.
>
> En data science, la seconde vision est la plus utile : *un individu = un vecteur*.

#### Un exemple concret

Dar Jasmin compte, pour chaque client, le nombre d'achats dans trois catégories : **poteries**, **huile d'olive**, **bijoux**. Chaque client devient un vecteur à trois composantes :

| Client | Poteries | Huile | Bijoux | Vecteur |
|---|---|---|---|---|
| Amel | 3 | 1 | 0 | $\mathbf{a} = (3, 1, 0)$ |
| Bilel | 6 | 2 | 0 | $\mathbf{b} = (6, 2, 0)$ |
| Chaima | 0 | 1 | 4 | $\mathbf{c} = (0, 1, 4)$ |

On note $\mathbf{a} = (a_1, a_2, \dots, a_p)$ un vecteur à $p$ composantes, et $\mathbb{R}^p$ l'ensemble de tous les vecteurs à $p$ composantes réelles. Ici $p = 3$ : nos clients vivent dans $\mathbb{R}^3$.

> ✅ **Convention du livre.** Un nombre seul (un *scalaire*) s'écrit en italique : $a$, $\lambda$. Un vecteur s'écrit en gras minuscule : $\mathbf{a}$. Une matrice s'écrit en gras majuscule : $\mathbf{A}$.

#### Les opérations de base

**Addition.** On additionne composante par composante. Si Amel et Chaima regroupent leurs achats :

$$\mathbf{a} + \mathbf{c} = (3+0,\; 1+1,\; 0+4) = (3, 2, 4).$$

**Multiplication par un scalaire.** On multiplie chaque composante :

$$2\,\mathbf{a} = (2 \times 3,\; 2 \times 1,\; 2 \times 0) = (6, 2, 0) = \mathbf{b}.$$

Regardez bien : **Bilel est exactement « deux fois Amel »**. Il achète les mêmes choses dans les mêmes proportions, simplement en plus grande quantité. Nous allons voir comment la mathématique capture cette idée.

**Combinaison linéaire.** Combiner les deux opérations donne une *combinaison linéaire* : $\lambda_1 \mathbf{u}_1 + \lambda_2 \mathbf{u}_2$. Par exemple, « la moitié d'Amel plus un tiers de Chaima » est $\tfrac12 \mathbf{a} + \tfrac13 \mathbf{c}$. Presque tout ce que nous ferons en modélisation est une combinaison linéaire de quelque chose.

En Python, la bibliothèque **NumPy** manipule les vecteurs comme des objets à part entière :

```python
import numpy as np

amel   = np.array([3, 1, 0])
bilel  = np.array([6, 2, 0])
chaima = np.array([0, 1, 4])

print("Amel + Chaima :", amel + chaima)
print("2 x Amel      :", 2 * amel)
print("Bilel == 2 x Amel ?", np.array_equal(bilel, 2 * amel))
```
<!--sortie-->
```text
Amel + Chaima : [3 2 4]
2 x Amel      : [6 2 0]
Bilel == 2 x Amel ? True
```

#### Le produit scalaire : mesurer l'accord entre deux vecteurs

Le **produit scalaire** de deux vecteurs de même taille est la somme des produits des composantes :

$$\mathbf{a} \cdot \mathbf{b} = \sum_{i=1}^{p} a_i b_i = a_1 b_1 + a_2 b_2 + \dots + a_p b_p.$$

> 🧪 **Exemple à la main.**
>
> $\mathbf{a} \cdot \mathbf{b} = 3 \times 6 + 1 \times 2 + 0 \times 0 = 18 + 2 + 0 = 20.$
>
> $\mathbf{a} \cdot \mathbf{c} = 3 \times 0 + 1 \times 1 + 0 \times 4 = 0 + 1 + 0 = 1.$

> 💡 **Intuition.** Le produit scalaire est grand quand les deux vecteurs « vont dans le même sens » (ils ont des composantes fortes aux mêmes endroits), proche de 0 quand ils n'ont rien en commun, et négatif quand ils s'opposent. Amel et Bilel s'entendent bien (20) ; Amel et Chaima presque pas (1) : le seul point commun est une unité d'huile.

La **norme** d'un vecteur est sa longueur, donnée par le théorème de Pythagore généralisé :

$$\|\mathbf{a}\| = \sqrt{\mathbf{a} \cdot \mathbf{a}} = \sqrt{a_1^2 + a_2^2 + \dots + a_p^2}.$$

Pour nos clients : $\|\mathbf{a}\| = \sqrt{9 + 1 + 0} = \sqrt{10} \approx 3{,}162$, $\|\mathbf{b}\| = \sqrt{36 + 4} = \sqrt{40} \approx 6{,}325$ et $\|\mathbf{c}\| = \sqrt{0 + 1 + 16} = \sqrt{17} \approx 4{,}123$. On remarque que $\|\mathbf{b}\| = 2\|\mathbf{a}\|$ : doubler un vecteur double sa longueur.

Le produit scalaire a aussi une **interprétation géométrique** qui est fondamentale :

$$\mathbf{a} \cdot \mathbf{b} = \|\mathbf{a}\|\,\|\mathbf{b}\|\cos\theta,$$

où $\theta$ est l'angle entre les deux flèches. En isolant le cosinus, on obtient la **similarité cosinus** :

$$\cos\theta = \frac{\mathbf{a} \cdot \mathbf{b}}{\|\mathbf{a}\|\,\|\mathbf{b}\|}.$$

> 🧪 **Exemple à la main.**
>
> - Amel et Bilel : $\cos\theta = \dfrac{20}{\sqrt{10}\,\sqrt{40}} = \dfrac{20}{\sqrt{400}} = \dfrac{20}{20} = 1$. Même direction : **mêmes goûts**.
> - Amel et Chaima : $\cos\theta = \dfrac{1}{\sqrt{10}\,\sqrt{17}} = \dfrac{1}{\sqrt{170}} \approx 0{,}077$. Presque perpendiculaires : **goûts très différents**.

La similarité cosinus ignore la *taille* des vecteurs et ne regarde que leur *direction*. C'est exactement ce que l'on veut pour comparer des profils d'achat : un gros acheteur et un petit acheteur qui ont les mêmes goûts doivent apparaître comme semblables.

```python
def cosinus(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

print("cos(Amel, Bilel)  =", round(cosinus(amel, bilel), 4))
print("cos(Amel, Chaima) =", round(cosinus(amel, chaima), 4))
```
<!--sortie-->
```text
cos(Amel, Bilel)  = 1.0
cos(Amel, Chaima) = 0.0767
```

> 📐 **Démonstration : pourquoi le cosinus reste toujours entre −1 et 1.**
>
> Il faut montrer que $|\mathbf{a}\cdot\mathbf{b}| \le \|\mathbf{a}\|\,\|\mathbf{b}\|$. C'est l'**inégalité de Cauchy-Schwarz**. Supposons $\mathbf{b} \neq \mathbf{0}$ et considérons, pour un réel $t$ quelconque, la quantité
>
> $$q(t) = \|\mathbf{a} - t\,\mathbf{b}\|^2 = \|\mathbf{a}\|^2 - 2t\,(\mathbf{a}\cdot\mathbf{b}) + t^2 \|\mathbf{b}\|^2.$$
>
> Une norme au carré est toujours positive ou nulle, donc $q(t) \ge 0$ **pour tout** $t$. Or $q$ est un trinôme du second degré en $t$ ; pour qu'il ne prenne jamais de valeur négative, son discriminant doit être négatif ou nul :
>
> $$\Delta = 4(\mathbf{a}\cdot\mathbf{b})^2 - 4\|\mathbf{a}\|^2\|\mathbf{b}\|^2 \le 0 \;\Longleftrightarrow\; (\mathbf{a}\cdot\mathbf{b})^2 \le \|\mathbf{a}\|^2\|\mathbf{b}\|^2.$$
>
> En prenant la racine carrée, $|\mathbf{a}\cdot\mathbf{b}| \le \|\mathbf{a}\|\,\|\mathbf{b}\|$, donc $-1 \le \cos\theta \le 1$. $\blacksquare$
>
> L'égalité (cosinus égal à ±1) a lieu exactement quand le discriminant est nul, c'est-à-dire quand il existe un $t$ tel que $\mathbf{a} = t\,\mathbf{b}$ : les deux vecteurs sont alignés. C'est le cas d'Amel et Bilel.

#### La distance entre deux vecteurs

La **distance euclidienne** entre deux individus est la norme de leur différence :

$$d(\mathbf{a}, \mathbf{b}) = \|\mathbf{a} - \mathbf{b}\| = \sqrt{\sum_{i=1}^{p}(a_i - b_i)^2}.$$

> 🧪 **Exemple.**
>
> - $d(\mathbf{a}, \mathbf{b}) = \|(3-6,\, 1-2,\, 0-0)\| = \|(-3, -1, 0)\| = \sqrt{10} \approx 3{,}162.$
> - $d(\mathbf{a}, \mathbf{c}) = \|(3-0,\, 1-1,\, 0-4)\| = \|(3, 0, -4)\| = \sqrt{9 + 0 + 16} = 5.$

```python
print("distance(Amel, Bilel)  =", round(np.linalg.norm(amel - bilel), 3))
print("distance(Amel, Chaima) =", round(np.linalg.norm(amel - chaima), 3))
```
<!--sortie-->
```text
distance(Amel, Bilel)  = 3.162
distance(Amel, Chaima) = 5.0
```

Remarquez la nuance. Selon le **cosinus**, Amel et Bilel sont *identiques* (1) ; selon la **distance**, ils sont *à 3,16 unités l'un de l'autre*, parce que Bilel achète plus. Ni l'une ni l'autre mesure n'est « la bonne » : elles répondent à des questions différentes.

| Mesure | Elle répond à… | À utiliser quand… |
|---|---|---|
| **Cosinus** | « Ont-ils les mêmes goûts ? » | seule la *proportion* compte (profils, textes, recommandations) |
| **Distance** | « Sont-ils proches en valeur absolue ? » | la *quantité* compte (regroupement par niveau de dépense, par exemple) |

> ⚠️ **Piège : les unités.** La distance additionne des carrés de différences, donc une variable exprimée en grands nombres écrase les autres. Soit trois clients décrits par (âge, panier moyen en DT) : $P = (30,\; 100)$, $Q = (60,\; 102)$ et $R = (31,\; 160)$.
>
> - $d(P, Q) = \sqrt{30^2 + 2^2} = \sqrt{904} \approx 30{,}1$
> - $d(P, R) = \sqrt{1^2 + 60^2} = \sqrt{3601} \approx 60{,}0$
>
> Selon la distance, $P$ (30 ans) ressemble davantage à $Q$ (60 ans) qu'à $R$ (31 ans), simplement parce que 60 dinars « pèsent » plus que 30 ans dans le calcul ! La cause : les deux variables n'ont pas la même échelle. Le remède est de **standardiser** les variables avant de les comparer, ce que nous ferons au chapitre 3.

> ✅ **À retenir (vecteurs).**
>
> - Un individu est un vecteur ; ses composantes sont ses caractéristiques.
> - Le produit scalaire $\sum a_i b_i$ mesure l'accord entre deux vecteurs ; la norme mesure leur longueur.
> - Le cosinus compare les **directions**, la distance compare les **positions**. Toujours se demander laquelle des deux correspond à la question posée.
> - Avant de comparer des variables d'échelles différentes, on les standardise.


### 1.1.2 Matrices : le tableau de données devient un objet mathématique

> 💡 **Intuition.** Une **matrice** est un tableau rectangulaire de nombres, rangés en lignes et en colonnes. Si un vecteur est « un individu », une matrice est « **tous les individus à la fois** » : chaque ligne est un individu, chaque colonne est une variable. Un fichier de données, c'est une matrice.

On note $\mathbf{A} \in \mathbb{R}^{n \times p}$ une matrice à $n$ lignes et $p$ colonnes (on dit « $n$ par $p$ »), et $a_{ij}$ le nombre situé à la ligne $i$ et à la colonne $j$. Une matrice carrée a autant de lignes que de colonnes ($n = p$).

#### Un exemple concret

Yasmine a noté ses ventes des trois premiers mois pour trois produits (poteries, huile, bijoux). Chaque **ligne** est un mois, chaque **colonne** un produit :

$$\mathbf{V} = \begin{pmatrix} 10 & 40 & 20 \\ 12 & 35 & 25 \\ 15 & 50 & 18 \end{pmatrix} \begin{array}{l} \leftarrow \text{janvier} \\ \leftarrow \text{février} \\ \leftarrow \text{mars} \end{array}$$

Les prix unitaires sont $\mathbf{p} = (45,\; 12,\; 30)$ dinars. Question : quel est le chiffre d'affaires de chaque mois ?

#### Le produit matrice-vecteur

Pour janvier, c'est un produit scalaire : $10 \times 45 + 40 \times 12 + 20 \times 30 = 450 + 480 + 600 = 1\,530$ DT. On fait de même pour février et mars. Calculer ces trois produits scalaires d'un coup, c'est ce qu'on appelle le **produit matrice-vecteur** $\mathbf{V}\mathbf{p}$ :

$$\mathbf{V}\mathbf{p} = \begin{pmatrix} 10\cdot 45 + 40\cdot 12 + 20\cdot 30 \\ 12\cdot 45 + 35\cdot 12 + 25\cdot 30 \\ 15\cdot 45 + 50\cdot 12 + 18\cdot 30 \end{pmatrix} = \begin{pmatrix} 1530 \\ 1710 \\ 1815 \end{pmatrix}.$$

Formellement, $(\mathbf{V}\mathbf{p})_i = \sum_j v_{ij}\, p_j$ : la composante $i$ du résultat est le produit scalaire de la **ligne $i$** de $\mathbf{V}$ avec $\mathbf{p}$.

> 💡 **Une seconde lecture, tout aussi utile.** On peut aussi voir $\mathbf{V}\mathbf{p}$ comme une **combinaison linéaire des colonnes** de $\mathbf{V}$ :
>
> $$\mathbf{V}\mathbf{p} = 45 \begin{pmatrix}10\\12\\15\end{pmatrix} + 12 \begin{pmatrix}40\\35\\50\end{pmatrix} + 30 \begin{pmatrix}20\\25\\18\end{pmatrix}.$$
>
> Le chiffre d'affaires est « 45 fois les ventes de poteries, plus 12 fois les ventes d'huile, plus 30 fois les ventes de bijoux ». C'est exactement ce que fait une régression linéaire : un mélange pondéré de colonnes.

```python
import numpy as np

V = np.array([[10, 40, 20],    # janvier : poteries, huile, bijoux
              [12, 35, 25],    # février
              [15, 50, 18]])   # mars
prix = np.array([45, 12, 30])

print("Forme de V  :", V.shape)
print("CA par mois :", V @ prix)
```
<!--sortie-->
```text
Forme de V  : (3, 3)
CA par mois : [1530 1710 1815]
```

L'opérateur `@` est le produit matriciel de Python. Il évite d'écrire une boucle.

#### Le produit matrice-matrice

Et si Yasmine veut comparer deux grilles de prix : les prix actuels et les prix augmentés de 10 % ? On met les deux grilles côte à côte dans une matrice $\mathbf{P}$ (une colonne par scénario) et on calcule $\mathbf{V}\mathbf{P}$.

**Règle de calcul.** Le produit de $\mathbf{A} \in \mathbb{R}^{n\times p}$ par $\mathbf{B} \in \mathbb{R}^{p \times q}$ est la matrice $\mathbf{C} = \mathbf{A}\mathbf{B} \in \mathbb{R}^{n \times q}$ dont l'élément $(i, j)$ est le produit scalaire de la **ligne $i$** de $\mathbf{A}$ avec la **colonne $j$** de $\mathbf{B}$ :

$$c_{ij} = \sum_{k=1}^{p} a_{ik}\, b_{kj}.$$

> ⚠️ **Règle d'or des dimensions.** Pour multiplier, le **nombre de colonnes de $\mathbf{A}$ doit égaler le nombre de lignes de $\mathbf{B}$** : $(n \times \mathbf{p})(\mathbf{p} \times q) \to (n \times q)$. Les deux $p$ « du milieu » doivent être identiques et disparaissent ; il reste $n \times q$. Quand un code plante avec une erreur de « forme » (*shape*), c'est presque toujours cette règle qui est violée.

```python
P = np.array([[45, 49.5],      # poteries : prix actuel, prix +10 %
              [12, 13.2],      # huile
              [30, 33.0]])     # bijoux
print(V @ P)
```
<!--sortie-->
```text
[[1530.  1683. ]
 [1710.  1881. ]
 [1815.  1996.5]]
```

Chaque ligne est un mois, chaque colonne un scénario. La deuxième colonne vaut 1,1 fois la première, comme attendu.

> ⚠️ **Piège : le produit matriciel n'est pas commutatif.** En général, $\mathbf{A}\mathbf{B} \neq \mathbf{B}\mathbf{A}$. Un petit exemple suffit à s'en convaincre :
>
> $$\mathbf{A} = \begin{pmatrix}1&2\\3&4\end{pmatrix}, \quad \mathbf{B} = \begin{pmatrix}0&1\\1&0\end{pmatrix}.$$
>
> Calcul de $\mathbf{A}\mathbf{B}$ : première ligne $(1\cdot 0 + 2\cdot 1,\; 1\cdot 1 + 2\cdot 0) = (2, 1)$ ; seconde ligne $(3\cdot 0 + 4 \cdot 1,\; 3\cdot 1 + 4\cdot 0) = (4, 3)$. Donc $\mathbf{A}\mathbf{B} = \begin{pmatrix}2&1\\4&3\end{pmatrix}$ : multiplier à droite par $\mathbf{B}$ **échange les colonnes** de $\mathbf{A}$.
>
> Calcul de $\mathbf{B}\mathbf{A}$ : on trouve $\begin{pmatrix}3&4\\1&2\end{pmatrix}$ : multiplier à gauche par $\mathbf{B}$ **échange les lignes** de $\mathbf{A}$. Les deux résultats sont différents.

```python
A = np.array([[1, 2], [3, 4]])
B = np.array([[0, 1], [1, 0]])
print("A @ B =\n", A @ B)
print("B @ A =\n", B @ A)
```
<!--sortie-->
```text
A @ B =
 [[2 1]
 [4 3]]
B @ A =
 [[3 4]
 [1 2]]
```

Ce que l'on garde, en revanche : le produit est **associatif** ($(\mathbf{A}\mathbf{B})\mathbf{C} = \mathbf{A}(\mathbf{B}\mathbf{C})$) et **distributif** ($\mathbf{A}(\mathbf{B}+\mathbf{C}) = \mathbf{A}\mathbf{B} + \mathbf{A}\mathbf{C}$).

#### La transposée

La **transposée** $\mathbf{A}^\top$ d'une matrice échange ses lignes et ses colonnes : $(\mathbf{A}^\top)_{ij} = a_{ji}$. Une matrice $3 \times 2$ devient une matrice $2 \times 3$. On a la règle $(\mathbf{A}\mathbf{B})^\top = \mathbf{B}^\top \mathbf{A}^\top$ (l'ordre s'inverse).

Pour un vecteur colonne $\mathbf{x}$, le nombre $\mathbf{x}^\top \mathbf{x} = \sum x_i^2 = \|\mathbf{x}\|^2$ est son carré de norme : le produit scalaire s'écrit donc $\mathbf{a}\cdot\mathbf{b} = \mathbf{a}^\top\mathbf{b}$. Vous croiserez cette écriture partout.

#### La matrice identité et l'inverse

La **matrice identité** $\mathbf{I}$ (des 1 sur la diagonale, des 0 ailleurs) est le « 1 » des matrices : $\mathbf{I}\mathbf{A} = \mathbf{A}\mathbf{I} = \mathbf{A}$.

L'**inverse** d'une matrice carrée $\mathbf{A}$, quand il existe, est la matrice $\mathbf{A}^{-1}$ telle que

$$\mathbf{A}\mathbf{A}^{-1} = \mathbf{A}^{-1}\mathbf{A} = \mathbf{I}.$$

C'est l'analogue de $a \times \frac{1}{a} = 1$. Pour une matrice $2 \times 2$, il existe une formule simple. Si $\mathbf{A} = \begin{pmatrix}a&b\\c&d\end{pmatrix}$, son **déterminant** est $\det\mathbf{A} = ad - bc$, et lorsque $\det \mathbf{A} \neq 0$ :

$$\mathbf{A}^{-1} = \frac{1}{ad - bc}\begin{pmatrix}d&-b\\-c&a\end{pmatrix}.$$

> 🧪 **Exemple.** Soit $\mathbf{A} = \begin{pmatrix}2&1\\5&3\end{pmatrix}$. Son déterminant vaut $2\times 3 - 1\times 5 = 1$, donc
>
> $$\mathbf{A}^{-1} = \begin{pmatrix}3&-1\\-5&2\end{pmatrix}.$$
>
> **Vérification** : $\mathbf{A}\mathbf{A}^{-1} = \begin{pmatrix}2\cdot 3 + 1\cdot(-5) & 2\cdot(-1) + 1\cdot 2\\ 5\cdot 3 + 3\cdot(-5) & 5\cdot(-1) + 3\cdot 2\end{pmatrix} = \begin{pmatrix}1&0\\0&1\end{pmatrix}$. ✔

```python
A = np.array([[2, 1], [5, 3]])
A_inv = np.linalg.inv(A)
print(A_inv.round(6) + 0)          # le "+ 0" évite l'affichage de -0.
print((A @ A_inv).round(6) + 0)
```
<!--sortie-->
```text
[[ 3. -1.]
 [-5.  2.]]
[[1. 0.]
 [0. 1.]]
```

#### Résoudre un système d'équations linéaires

Voici l'utilité majeure de l'inverse. Yasmine a perdu sa liste de prix, mais retrouve deux factures :

- commande 1 : 2 poteries + 1 huile = 102 DT ;
- commande 2 : 1 poterie + 3 huiles = 81 DT.

Notons $x_1$ le prix d'une poterie et $x_2$ celui d'une huile. Le système s'écrit $\mathbf{M}\mathbf{x} = \mathbf{b}$ avec

$$\mathbf{M} = \begin{pmatrix}2&1\\1&3\end{pmatrix}, \quad \mathbf{x} = \begin{pmatrix}x_1\\x_2\end{pmatrix}, \quad \mathbf{b} = \begin{pmatrix}102\\81\end{pmatrix}.$$

> 🧪 **Résolution à la main.** $\det\mathbf{M} = 2\times 3 - 1 \times 1 = 5$ et $\mathbf{M}^{-1} = \frac15\begin{pmatrix}3&-1\\-1&2\end{pmatrix}$. Donc
>
> $$\mathbf{x} = \mathbf{M}^{-1}\mathbf{b} = \frac15\begin{pmatrix}3\cdot 102 - 81\\ -102 + 2\cdot 81\end{pmatrix} = \frac15\begin{pmatrix}225\\60\end{pmatrix} = \begin{pmatrix}45\\12\end{pmatrix}.$$
>
> Une poterie coûte **45 DT**, une huile **12 DT**. Vérifions : $2 \times 45 + 12 = 102$ ✔ et $45 + 3\times 12 = 81$ ✔.

```python
M = np.array([[2, 1], [1, 3]])
b = np.array([102, 81])
print("Prix retrouvés :", np.linalg.solve(M, b))
```
<!--sortie-->
```text
Prix retrouvés : [45. 12.]
```

> ⚠️ **Piège : en pratique, on évite d'inverser.** Pour résoudre $\mathbf{M}\mathbf{x} = \mathbf{b}$, on utilise `np.linalg.solve`, jamais `np.linalg.inv(M) @ b` : c'est plus rapide et plus précis (voir la section ➕ sur l'analyse numérique). L'inverse est un outil de **raisonnement** ; la machine, elle, résout directement.

#### Quand le système n'a pas de solution unique : déterminant et rang

Imaginons que la commande 2 soit en réalité « 4 poteries + 2 huiles = 204 DT » : c'est exactement le **double** de la commande 1. Elle n'apporte **aucune information nouvelle**. Il y a alors une infinité de couples de prix qui conviennent. Le déterminant le détecte : $\det\begin{pmatrix}2&1\\4&2\end{pmatrix} = 2\times 2 - 1\times 4 = 0$. On dit que la matrice est **singulière** (non inversible).

Une notion plus générale est le **rang** : le nombre de colonnes (ou de lignes) *linéairement indépendantes*, c'est-à-dire qui ne s'obtiennent pas comme combinaison des autres. Ici le rang vaut 1 au lieu de 2.

```python
S = np.array([[2, 1], [4, 2]])
print("déterminant :", np.linalg.det(S))
print("rang        :", np.linalg.matrix_rank(S))
```
<!--sortie-->
```text
déterminant : 0.0
rang        : 1
```

> 🛠️ **Application : des colonnes redondantes.** Cette situation est fréquente dans les vraies données. Supposons qu'un fichier contienne le prix hors taxes (HT) *et* le prix toutes taxes comprises (TTC = 1,19 × HT). La seconde colonne est un multiple de la première : elle ne dit rien de plus.

```python
ht = np.array([40.0, 25.0, 60.0, 15.0])
table = np.column_stack([ht, 1.19 * ht])    # deux colonnes : HT et TTC
print("rang de la table :", np.linalg.matrix_rank(table), "(alors qu'il y a 2 colonnes)")
```
<!--sortie-->
```text
rang de la table : 1 (alors qu'il y a 2 colonnes)
```

Un modèle de régression qui utiliserait ces deux colonnes serait incapable de départager leurs rôles. C'est le problème de la **multicolinéarité**, que nous retrouverons au volume II.

#### Application : la matrice des similarités entre clients

Revenons à nos clients et à la similarité cosinus. Ajoutons deux clients, Dorra et Elyes, et mettons les cinq profils dans une matrice $\mathbf{X}$ (une ligne par client, une colonne par catégorie).

L'astuce : si l'on **normalise** chaque ligne pour que sa norme vaille 1, on obtient une matrice $\mathbf{U}$ dont chaque ligne est un vecteur de longueur 1. Alors le produit scalaire de deux lignes de $\mathbf{U}$ est directement leur cosinus. Et **tous** les produits scalaires entre lignes sont rassemblés dans le produit $\mathbf{U}\mathbf{U}^\top$ :

$$(\mathbf{U}\mathbf{U}^\top)_{ij} = \mathbf{u}_i \cdot \mathbf{u}_j = \cos\theta_{ij}.$$

```python
clients = {"Amel": [3, 1, 0], "Bilel": [6, 2, 0], "Chaima": [0, 1, 4],
           "Dorra": [1, 0, 5], "Elyes": [2, 2, 2]}
noms = list(clients)
X = np.array(list(clients.values()), dtype=float)        # une ligne par client

U = X / np.linalg.norm(X, axis=1, keepdims=True)         # chaque ligne ramenée à la norme 1
S = U @ U.T                                              # toutes les similarités d'un coup

print(" " * 8 + "".join(f"{n:>8}" for n in noms))
for i, n in enumerate(noms):
    print(f"{n:<8}" + "".join(f"{S[i, j]:8.2f}" for j in range(len(noms))))
```
<!--sortie-->
```text
            Amel   Bilel  Chaima   Dorra   Elyes
Amel        1.00    1.00    0.08    0.19    0.73
Bilel       1.00    1.00    0.08    0.19    0.73
Chaima      0.08    0.08    1.00    0.95    0.70
Dorra       0.19    0.19    0.95    1.00    0.68
Elyes       0.73    0.73    0.70    0.68    1.00
```

Lecture : la diagonale vaut 1 (chacun ressemble parfaitement à lui-même), la matrice est symétrique (la ressemblance d'Amel à Bilel est celle de Bilel à Amel), Amel et Bilel valent 1,00, et Chaima et Dorra, tous deux fans de bijoux, sont très proches. Elyes, qui achète un peu de tout, est moyennement proche de chacun (entre 0,68 et 0,73) sans avoir de « jumeau » parmi eux.

Pour recommander un produit à Chaima, Yasmine pourrait regarder ce qu'achète son voisin le plus proche, ici Dorra. Avec une seule multiplication de matrices, nous avons comparé les cinq clients entre eux ; avec cinq mille clients, ce serait la même ligne de code.

> ✅ **À retenir (matrices).**
>
> - Une matrice est un tableau $n \times p$ : lignes = individus, colonnes = variables.
> - $(\mathbf{A}\mathbf{B})_{ij}$ = ligne $i$ de $\mathbf{A}$ $\cdot$ colonne $j$ de $\mathbf{B}$ ; les dimensions doivent s'emboîter : $(n\times p)(p \times q)$.
> - Le produit matriciel n'est **pas commutatif**.
> - Résoudre $\mathbf{M}\mathbf{x} = \mathbf{b}$ : on utilise `np.linalg.solve`. Si $\det\mathbf{M} = 0$ (rang insuffisant), il n'y a pas de solution unique.
> - Des colonnes redondantes font chuter le rang : c'est la source de la multicolinéarité.


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
print("trace =", np.trace(A), " somme des valeurs propres =", valeurs.sum())
print("det   =", round(np.linalg.det(A), 4), " produit des valeurs propres =", valeurs.prod())
```
<!--sortie-->
```text
valeurs propres : [1. 3.]
vecteurs propres (en colonnes) :
 [[-0.7071  0.7071]
 [ 0.7071  0.7071]]
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

```python
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

#### 🛠️ Application : la direction principale d'un nuage de clients

Yasmine mesure, pour 200 clients, le nombre de visites mensuelles sur son site et leur dépense mensuelle. Elle soupçonne que les deux sont liées. On **standardise** chaque variable (on retranche la moyenne et on divise par l'écart-type, pour qu'elles aient la même échelle, comme promis dans la section sur les vecteurs), puis on calcule la **matrice de covariance** des deux variables standardisées :

$$\mathbf{C} = \begin{pmatrix} 1 & r \\ r & 1 \end{pmatrix},$$

où $r$ est la corrélation entre les deux variables. C'est une matrice symétrique : le théorème spectral s'applique.

```python
rng = np.random.default_rng(42)
n = 200
visites = rng.normal(6, 2, n)                        # visites par mois
depense = 15 * visites + rng.normal(0, 12, n)        # dépense en DT, liée aux visites

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

**Lecture.** La plus grande valeur propre (environ 1,90) correspond à la direction $(0{,}71;\; 0{,}71)$, la diagonale : c'est l'axe le long duquel le nuage de clients est le plus étiré, l'axe « client actif et dépensier ». Elle capte environ **95 %** de toute la variabilité. La seconde (0,10) correspond à la direction perpendiculaire, qui ne représente que les écarts « dépense inhabituelle pour ce nombre de visites ».

Autrement dit, on peut résumer ces deux variables par **une seule** (la position le long de l'axe principal), en ne perdant que 5 % de l'information. C'est le principe de l'**analyse en composantes principales** (ACP), que nous étudierons en détail au volume II : *trouver les directions de plus grande variance, ce sont les vecteurs propres de la matrice de covariance*.

> ✅ **À retenir (valeurs propres).**
>
> - $\mathbf{A}\mathbf{v} = \lambda\mathbf{v}$ : un vecteur propre garde sa direction, la valeur propre dit de combien il est étiré.
> - On les trouve avec $\det(\mathbf{A} - \lambda\mathbf{I}) = 0$. Somme des valeurs propres = trace ; produit = déterminant.
> - Une matrice symétrique a des valeurs propres réelles et des vecteurs propres orthogonaux ; $\mathbf{A} = \mathbf{V}\boldsymbol{\Lambda}\mathbf{V}^\top$.
> - Les vecteurs propres de la matrice de covariance sont les axes principaux d'un nuage de données.

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

#### 🛠️ Application : résumer un tableau de ventes

Yasmine a les ventes hebdomadaires de 6 produits sur 8 semaines. Les données sont simulées selon une règle simple : *ventes = popularité du produit × effet de la semaine + un peu de bruit*. Une telle structure « produit × saison » doit se retrouver dans la première couche de la SVD.

```python
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

```python
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

**Lecture.** La première valeur singulière (environ 202) est près de soixante fois plus grande que la deuxième (environ 3,5) : **99,9 %** de l'« énergie » du tableau est dans une seule couche. Une approximation de rang 1, qui ne stocke que 15 nombres au lieu de 48, reproduit le tableau avec une erreur relative d'environ 2,7 %. Le reste (les couches 2 à 6) est du bruit.

La SVD a donc **retrouvé toute seule** la structure « popularité × saison » que nous avions mise dans les données, sans qu'on lui dise de la chercher. Vous venez de voir le principe de la **réduction de dimension** et celui des **systèmes de recommandation** par factorisation de matrices, deux sujets que nous développerons aux volumes suivants.

> ✅ **À retenir (SVD).**
>
> - Toute matrice se décompose en $\mathbf{A} = \mathbf{U}\boldsymbol{\Sigma}\mathbf{V}^\top$ : rotation, étirement, rotation.
> - Les valeurs singulières mesurent l'importance de chaque couche ; leur nombre non nul est le rang.
> - Garder les $k$ premières couches donne la meilleure approximation de rang $k$ (Eckart-Young) : c'est la base de la compression, du débruitage et de l'ACP.
> - L'ACP n'est rien d'autre que la SVD des données centrées.


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

Vérifions numériquement en $(1, 1)$, en mesurant la pente de $f$ dans quatre directions :

```python
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

La pente mesurée est maximale (6,325, soit $\|\nabla f\| = \sqrt{40}$) dans la direction du gradient, et minimale (−6,325) dans la direction opposée. Aucune autre direction ne fait mieux.

![Courbes de niveau de f(x,y) = x² + 3y² (chaque ellipse est une « altitude » constante) et, en chaque point, la direction de la plus forte descente (−gradient). Les flèches sont perpendiculaires aux courbes de niveau et pointent vers le fond du bol.](figures/ch01-gradient-contours.png)

Deux faits à retenir sur cette figure : le gradient est **perpendiculaire aux courbes de niveau**, et **−gradient pointe vers le bas**. C'est exactement ce que nous utiliserons en 1.3 pour descendre vers le minimum.

#### 🛠️ Application : la pente de l'erreur d'une droite

Yasmine veut ajuster une droite $y = ax + b$ à trois mesures $(x_i, y_i)$ : $(1, 2)$, $(2, 3)$ et $(3, 5)$. Pour mesurer la qualité d'une droite candidate, on utilise la **somme des carrés des erreurs** :

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

```python
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

Au point $(1{,}5\;;\;1/3)$, le gradient est **nul** : on est au fond du bol. Nous montrerons en 1.3 comment y arriver automatiquement.

> ✅ **À retenir (gradient).**
>
> - Le gradient $\nabla f$ rassemble les dérivées partielles ; il pointe vers la **plus forte montée** et sa norme mesure la pente.
> - $-\nabla f$ pointe vers la plus forte **descente**.
> - Au minimum (ou au maximum, ou au col), le gradient est nul.
> - La règle de la composée rend le calcul du gradient d'une « somme de carrés d'erreurs » mécanique : c'est le cœur de l'entraînement des modèles.

### 1.2.3 Intégrales : accumuler les petits changements

> 💡 **Intuition.** L'intégrale est l'opération inverse de la dérivée. Si la dérivée donne « la vitesse à chaque instant », l'**intégrale** donne « la distance parcourue sur un intervalle » : elle **additionne une infinité de petits morceaux**. Graphiquement, c'est l'**aire sous la courbe**.
>
> En data science, l'intégrale sert surtout à une chose : calculer des **probabilités**. Quand une quantité est décrite par une courbe de densité, la probabilité d'un événement est l'aire sous la courbe sur la zone concernée.

#### Calculer une aire avec des rectangles

L'aire sous une courbe $f$ entre $a$ et $b$ se note $\displaystyle\int_a^b f(x)\,dx$. L'idée de **Riemann** : découper l'intervalle en $n$ bandes étroites, approcher chaque bande par un rectangle de hauteur $f(x)$, et additionner. Plus $n$ est grand, meilleure est l'approximation.

> 🧪 **Exemple à la main.** Aire sous $f(x) = x^2$ entre 0 et 3, avec $n = 3$ rectangles de largeur 1 (hauteur mesurée au bord droit) : $1\cdot 1^2 + 1 \cdot 2^2 + 1\cdot 3^2 = 1 + 4 + 9 = 14$. C'est une approximation grossière (les rectangles dépassent la courbe). Avec $n = 6$ rectangles de largeur $0{,}5$ : $0{,}5\,(0{,}5^2 + 1^2 + 1{,}5^2 + 2^2 + 2{,}5^2 + 3^2) = 0{,}5 \times 22{,}75 = 11{,}375$. Mieux !

```python
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

Les approximations convergent vers **9**. L'intégrale *est* cette limite.

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

#### 🛠️ Application : une commande dans les trois prochaines minutes ?

Sur le site de Dar Jasmin, en heure de pointe, une commande arrive en moyenne toutes les 2 minutes. On montrera au chapitre 2 que le temps d'attente $T$ (en minutes) avant la prochaine commande suit une **loi exponentielle** de taux $\lambda = 0{,}5$ par minute, dont la densité est

$$f(t) = \lambda\,e^{-\lambda t} = 0{,}5\,e^{-0{,}5\,t}, \qquad t \ge 0.$$

La probabilité qu'une commande arrive dans les 3 prochaines minutes est l'aire sous cette courbe entre 0 et 3.

> 🧪 **À la main.** Une primitive de $0{,}5\,e^{-0{,}5t}$ est $-e^{-0{,}5t}$ (on dérive : $-(-0{,}5)e^{-0{,}5t} = 0{,}5\,e^{-0{,}5t}$ ✔). Donc
>
> $$P(T \le 3) = \bigl[-e^{-0{,}5\,t}\bigr]_0^3 = -e^{-1{,}5} - (-e^{0}) = 1 - e^{-1{,}5} \approx 0{,}777.$$

```python
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

**Lecture.** Les trois méthodes concordent : environ **77,7 %** de chances. Et l'aire **totale** sous la courbe vaut 1 : c'est une exigence de toute densité de probabilité (la probabilité que *quelque chose* arrive est de 100 %). Nous reverrons ces idées en détail au chapitre 2.

> ⚠️ **Piège : les aires sous l'axe comptent négativement.** Si $f$ est négative sur une partie de l'intervalle, l'intégrale en tient compte avec un signe moins. L'intégrale mesure une quantité **algébrique** accumulée, pas toujours une surface géométrique.

> ✅ **À retenir (intégrale).**
>
> - $\int_a^b f(x)\,dx$ est l'aire (algébrique) sous la courbe entre $a$ et $b$ : une limite de sommes de rectangles.
> - Théorème fondamental : $\int_a^b f = F(b) - F(a)$ où $F' = f$.
> - Pour une densité de probabilité, l'aire sous la courbe sur une zone **est** la probabilité de cette zone ; l'aire totale vaut 1.


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

Voici un vrai petit problème de décision, qui combine tout le chapitre. Yasmine a testé huit prix pour un même bol en céramique, chacun pendant une semaine :

| Prix $p$ (DT) | 25 | 28 | 31 | 34 | 37 | 40 | 43 | 46 |
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

Treize itérations seulement. Le modèle trouvé est $q \approx 143{,}9 - 2{,}11\,p$ : **chaque dinar de hausse fait perdre environ 2,1 ventes par semaine**. (La ligne `polyfit` vérifie notre résultat avec la fonction toute faite de NumPy.)

**Étape 2 : exprimer les recettes.** Les recettes sont le prix multiplié par les quantités vendues :

$$R(p) = p \cdot q(p) = p\,(\alpha + \beta\,p) = \alpha\,p + \beta\,p^2.$$

**Étape 3 : maximiser.** On dérive et on annule : $R'(p) = \alpha + 2\beta\,p = 0$, d'où

$$p^\star = -\frac{\alpha}{2\beta}.$$

Comme $\beta < 0$, on a $R'' = 2\beta < 0$ : c'est bien un maximum.

```python
p_opt = -alpha / (2 * beta)
R = lambda p: p * (alpha + beta * p)
print(f"prix optimal p* = {p_opt:.2f} DT")
print(f"recettes prévues à p* : {R(p_opt):8.1f} DT par semaine")
print(f"recettes prévues à 40 DT : {R(40):8.1f} DT par semaine")
print(f"recettes prévues à 46 DT : {R(46):8.1f} DT par semaine")
```
<!--sortie-->
```text
prix optimal p* = 34.09 DT
recettes prévues à p* :   2453.7 DT par semaine
recettes prévues à 40 DT :   2380.0 DT par semaine
recettes prévues à 46 DT :   2154.3 DT par semaine
```

![À gauche : les huit mesures et la droite de demande ajustée. À droite : les recettes prévues selon le prix, avec leur maximum vers 34 DT.](figures/ch01-demande-recettes.png)

**Résultat.** Le prix qui maximise les recettes est d'environ **34 DT**, avec 2 454 DT de recettes hebdomadaires prévues. Au prix actuel de 40 DT, elles seraient de 2 380 DT : baisser le prix de 6 dinars rapporterait un peu plus de **70 DT par semaine**, soit environ 3 % de mieux.

> ⚠️ **Prudence.** Ce résultat est obtenu avec **huit** points et un modèle très simple. Il ne dit rien de l'incertitude (de combien $p^\star$ pourrait-il se tromper ?), ni du bénéfice (ici nous avons maximisé les *recettes*, sans tenir compte des coûts), ni de l'extrapolation hors de la plage de prix testée. Ces questions sont l'objet du chapitre 3 (statistique) et du volume II (régression). Retenez la démarche : **modéliser, écrire la fonction objectif, la dériver, l'annuler.**

### 1.3.5 Optimisation sous contraintes : les multiplicateurs de Lagrange

Dans la vraie vie, on n'optimise presque jamais librement : on a un **budget**, une capacité, un poids maximal. On cherche alors le meilleur choix **parmi ceux qui respectent une contrainte**.

> 💡 **Intuition.** Vous voulez atteindre le point le plus haut d'une colline, mais vous devez rester sur un sentier. Au meilleur point du sentier, vous ne pouvez plus monter en suivant le sentier : celui-ci est **tangent à une courbe de niveau** de la colline. À cet endroit, la direction de plus forte montée de la colline (le gradient de $f$) est **perpendiculaire au sentier**, donc **parallèle au gradient de la contrainte** (qui, lui aussi, est perpendiculaire au sentier).

#### Un exemple concret

Yasmine dispose de 1 000 DT de budget publicitaire à répartir entre Facebook ($x$ dinars) et Instagram ($y$ dinars). Elle estime les recettes générées par :

$$R(x, y) = 80\sqrt{x} + 120\sqrt{y}.$$

(La racine carrée traduit des **rendements décroissants** : les premiers dinars investis rapportent plus que les derniers.) Elle veut maximiser $R$ sous la contrainte $x + y = 1000$.

**La méthode de Lagrange.** On introduit un nombre $\lambda$ (le *multiplicateur*) et on forme le **lagrangien** :

$$\mathcal{L}(x, y, \lambda) = 80\sqrt{x} + 120\sqrt{y} - \lambda\,(x + y - 1000).$$

On annule toutes ses dérivées partielles :

- $\dfrac{\partial\mathcal{L}}{\partial x} = \dfrac{40}{\sqrt{x}} - \lambda = 0$
- $\dfrac{\partial\mathcal{L}}{\partial y} = \dfrac{60}{\sqrt{y}} - \lambda = 0$
- $\dfrac{\partial\mathcal{L}}{\partial \lambda} = -(x + y - 1000) = 0$ (qui redonne la contrainte).

> 🧪 **Résolution à la main.** Les deux premières équations donnent $\dfrac{40}{\sqrt{x}} = \dfrac{60}{\sqrt{y}}$, donc $\sqrt{y} = 1{,}5\sqrt{x}$, soit $y = 2{,}25\,x$. En reportant dans la contrainte : $x + 2{,}25\,x = 1000$, donc
>
> $$x = \frac{1000}{3{,}25} \approx 307{,}7\ \text{DT}, \qquad y = 2{,}25\,x \approx 692{,}3\ \text{DT}.$$
>
> Recettes : $80\sqrt{307{,}7} + 120\sqrt{692{,}3} \approx 1\,403{,}3 + 3\,157{,}4 = 4\,560{,}7$ DT.

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

**Le multiplicateur $\lambda$ a une signification concrète.** Au point optimal, $\lambda = 40/\sqrt{x} \approx 40/17{,}54 \approx 2{,}28$. C'est le **prix de l'ombre** (*shadow price*) de la contrainte : **un dinar de budget supplémentaire rapporterait environ 2,28 DT de recettes en plus**, si l'on réoptimise la répartition. Vérifions :

```python
meilleur = lambda B: R2([B / 3.25, B - B / 3.25])       # répartition optimale pour un budget B
print("gain réel avec 1 DT de plus :", round(meilleur(1001) - meilleur(1000), 4))
print("multiplicateur lambda       :", round(40 / np.sqrt(x_th), 4))
```
<!--sortie-->
```text
gain réel avec 1 DT de plus : 2.2798
multiplicateur lambda       : 2.2804
```

C'est une information précieuse pour fixer un budget : 1 DT de publicité en plus rapporte environ 2,28 DT de recettes. Il n'est donc rentable d'augmenter le budget que si la marge brute de Yasmine dépasse $1/2{,}28 \approx 44\,\%$ (sinon la dépense supplémentaire coûte plus qu'elle ne rapporte).

> ✅ **À retenir (optimisation).**
>
> - Apprendre = minimiser une fonction de perte. $\arg\min$ désigne le point où le minimum est atteint.
> - Si la fonction est **convexe**, tout minimum local est global. La perte des moindres carrés est convexe (hessienne $2\mathbf{X}^\top\mathbf{X}$ positive) ; elle a un fond unique si les colonnes de $\mathbf{X}$ sont indépendantes.
> - Descente de gradient : $\boldsymbol{\theta}_{k+1} = \boldsymbol{\theta}_k - \eta\,\nabla f(\boldsymbol{\theta}_k)$. Le pas $\eta$ ne doit être ni trop petit (lent) ni trop grand (divergence : $\eta < 2/\lambda_{\max}$ pour une fonction quadratique).
> - **Centrer et standardiser** les variables arrondit le bol et accélère considérablement la descente.
> - Sous contrainte, on annule les dérivées du lagrangien ; $\lambda$ mesure la valeur marginale de la contrainte.


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

Les nombres décimaux de Python (type `float`) suivent la norme IEEE 754 en **double précision** : 64 bits, soit environ **16 chiffres significatifs**. L'erreur relative maximale d'un arrondi est appelée **epsilon machine** :

```python
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

Conséquence pratique : l'**ordre** des additions compte. Additionner un million de fois $0{,}1$ ne donne pas exactement 100 000.

```python
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
2. Centrer et standardiser les variables (1.3.3) diminue le conditionnement, ce qui explique en partie le gain de 335 à 18 itérations.

```python
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

Pour calculer $\sqrt{2}$, on cherche le zéro de $f(x) = x^2 - 2$, avec $f'(x) = 2x$ :

```python
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

```python
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

Il faut 35 étapes à la dichotomie, contre 5 à Newton, pour une précision comparable. Newton est rapide mais peut diverger si on part mal ; la dichotomie est lente mais ne rate jamais. Les bibliothèques (`scipy.optimize.brentq`) combinent les deux.

> ✅ **À retenir (analyse numérique).**
>
> - Un flottant a ~16 chiffres significatifs ; on compare avec `isclose`, jamais avec `==`.
> - Soustraire deux nombres proches détruit la précision (annulation) : préférez les fonctions de bibliothèque.
> - Le conditionnement $\kappa$ mesure la fragilité d'un problème ; on perd environ $\log_{10}\kappa$ chiffres.
> - `solve` plutôt que `inv`. Centrer et standardiser améliore le conditionnement.
> - Newton : rapide mais capricieux ; dichotomie : lente mais sûre.


## 1.6 ➕ Pour aller plus loin : mathématiques discrètes et graphes

> 🧭 **Section optionnelle.** Tout ce qui précède traitait de quantités qui varient de façon *continue* (prix, temps, pentes). Ici, on compte et on relie : des objets distincts, des choix, des liens. Ces outils servent pour les probabilités (chapitre 2), les algorithmes (chapitre 4), les bases de données (chapitre 5) et les systèmes de recommandation.

### 1.6.1 Ensembles : le langage de base

Un **ensemble** est une collection d'objets distincts, sans ordre. Yasmine propose quatre produits : $P = \{\text{bol}, \text{tapis}, \text{lampe}, \text{plateau}\}$. Ses clients de la semaine ont acheté des sous-ensembles de $P$.

Les opérations de la fiche de notations (1.4.2) se testent directement en Python avec le type `set` :

```python
panier_amel = {"bol", "tapis", "lampe"}
panier_karim = {"bol", "plateau"}

print("union          :", sorted(panier_amel | panier_karim))
print("intersection   :", sorted(panier_amel & panier_karim))
print("amel sans karim:", sorted(panier_amel - panier_karim))
print("taille         :", len(panier_amel))
```
<!--sortie-->
```text
union          : ['bol', 'lampe', 'plateau', 'tapis']
intersection   : ['bol']
amel sans karim: ['lampe', 'tapis']
taille         : 3
```

> 💡 **Application : similarité de Jaccard.** Comment mesurer à quel point deux paniers se ressemblent ? On divise la taille de ce qu'ils ont **en commun** par la taille de ce qu'ils ont **au total** :
>
> $$J(A, B) = \frac{|A\cap B|}{|A\cup B|}.$$
>
> Elle vaut 1 si les paniers sont identiques, 0 s'ils n'ont rien en commun. C'est l'équivalent « ensembliste » de la similarité cosinus du 1.1.1.

```python
def jaccard(a, b):
    return len(a & b) / len(a | b)

print("Jaccard(Amel, Karim) =", round(jaccard(panier_amel, panier_karim), 3))
```
<!--sortie-->
```text
Jaccard(Amel, Karim) = 0.25
```

Un seul produit en commun (le bol), sur quatre produits au total : $1/4 = 0{,}25$.

### 1.6.2 Compter : le principe multiplicatif

> 💡 **Intuition.** Si vous avez 3 pulls et 4 pantalons, vous avez $3\times 4 = 12$ tenues. Quand on enchaîne des choix indépendants, on **multiplie** le nombre d'options.

Yasmine veut proposer un **coffret cadeau** : un produit principal (4 choix), un emballage (3 choix), une carte message (2 choix). Le nombre de coffrets différents est $4\times3\times2 = 24$.

**Permutations.** De combien de façons peut-on **ranger** $n$ objets distincts dans l'ordre ? $n$ choix pour la première place, $n-1$ pour la suivante, etc. :

$$n! = n\times(n-1)\times\dots\times 2\times 1.$$

Les 4 produits peuvent être alignés en vitrine de $4! = 24$ façons.

**Arrangements et combinaisons.** Choisir $k$ objets parmi $n$ :

- *quand l'ordre compte* (podium : 1er, 2e, 3e) : $\dfrac{n!}{(n-k)!}$ ;
- *quand l'ordre ne compte pas* (un panier de 3 produits) :

$$\binom{n}{k} = \frac{n!}{k!\,(n-k)!}.$$

> 📐 **Pourquoi cette formule ?** Il y a $\frac{n!}{(n-k)!}$ façons de choisir $k$ objets *dans l'ordre*. Mais chaque groupe de $k$ objets a été compté $k!$ fois (une fois par ordre possible). On divise donc par $k!$.

```python
import math
print("tenues             :", 3 * 4)
print("coffrets           :", 4 * 3 * 2)
print("ordres de vitrine  :", math.factorial(4))
print("paniers de 2 parmi 4:", math.comb(4, 2))
print("podium 3 parmi 10  :", math.perm(10, 3))
print("paniers de 3 parmi 40:", math.comb(40, 3))
```
<!--sortie-->
```text
tenues             : 12
coffrets           : 24
ordres de vitrine  : 24
paniers de 2 parmi 4: 6
podium 3 parmi 10  : 720
paniers de 3 parmi 40: 9880
```

> 🧪 **Attention à l'explosion.** Si le catalogue contient 40 produits, il y a déjà 9 880 paniers de trois produits. Pour des paniers de dix produits parmi 40, on dépasse les 847 millions :

```python
print(math.comb(40, 10))
```
<!--sortie-->
```text
847660528
```

C'est pourquoi les algorithmes de recommandation ne peuvent pas **énumérer** tous les cas : on y reviendra avec la complexité (section ➕ du chapitre 4).

**Le triangle de Pascal et le binôme.** Les nombres $\binom{n}{k}$ se calculent par la règle $\binom{n}{k}=\binom{n-1}{k-1}+\binom{n-1}{k}$ et vérifient $(a+b)^n=\sum_k\binom{n}{k}a^k b^{n-k}$. Nous les retrouverons au chapitre 2 dans la **loi binomiale**.

### 1.6.3 Les graphes : modéliser des relations

Un **graphe** est un ensemble de **sommets** (des objets) et d'**arêtes** (des liens entre eux). Tout ce qui est « réseau » est un graphe : amis sur un réseau social, routes entre villes, produits souvent achetés ensemble, pages web reliées par des liens.

Voici le graphe des produits **achetés ensemble** dans la boutique : deux produits sont reliés si au moins un client les a pris dans le même panier.

```python
produits = ["bol", "tapis", "lampe", "plateau", "coussin"]
aretes = [("bol", "plateau"), ("bol", "tapis"), ("tapis", "lampe"),
          ("tapis", "coussin"), ("lampe", "coussin")]

# liste d'adjacence : pour chaque sommet, la liste de ses voisins
voisins = {p: [] for p in produits}
for a, b in aretes:
    voisins[a].append(b)
    voisins[b].append(a)

for p in produits:
    print(f"{p:8s} -> {voisins[p]}")
print("degrés :", {p: len(v) for p, v in voisins.items()})
```
<!--sortie-->
```text
bol      -> ['plateau', 'tapis']
tapis    -> ['bol', 'lampe', 'coussin']
lampe    -> ['tapis', 'coussin']
plateau  -> ['bol']
coussin  -> ['tapis', 'lampe']
degrés : {'bol': 2, 'tapis': 3, 'lampe': 2, 'plateau': 1, 'coussin': 2}
```

Le **degré** d'un sommet est son nombre de voisins : le tapis (degré 3) est le produit le plus « connecté », donc un bon candidat pour une promotion croisée.

**La matrice d'adjacence.** On peut ranger le graphe dans une matrice $\mathbf{A}$ : $A_{ij}=1$ si $i$ et $j$ sont reliés, 0 sinon.

```python
import numpy as np
idx = {p: i for i, p in enumerate(produits)}
A = np.zeros((5, 5), dtype=int)
for a, b in aretes:
    A[idx[a], idx[b]] = A[idx[b], idx[a]] = 1
print(A)
print("symétrique :", (A == A.T).all())
```
<!--sortie-->
```text
[[0 1 0 1 0]
 [1 0 1 0 1]
 [0 1 0 0 1]
 [1 0 0 0 0]
 [0 1 1 0 0]]
symétrique : True
```

> 📐 **Propriété remarquable : les puissances de $\mathbf{A}$ comptent les chemins.** L'élément $(\mathbf{A}^k)_{ij}$ est le **nombre de chemins de longueur $k$** entre $i$ et $j$.
>
> *Preuve pour $k=2$.* Par définition du produit matriciel, $(\mathbf{A}^2)_{ij}=\sum_{m} A_{im}A_{mj}$. Le terme $A_{im}A_{mj}$ vaut 1 exactement quand $i$—$m$ et $m$—$j$ sont deux arêtes, c'est-à-dire quand $m$ est un intermédiaire possible. La somme compte donc les intermédiaires, c'est-à-dire les chemins en deux pas. Le cas général se démontre par récurrence sur $k$ avec le même argument. $\blacksquare$

```python
A2 = A @ A
print("chemins de longueur 2 entre bol et lampe :", A2[idx["bol"], idx["lampe"]])
print("chemins de longueur 2 entre tapis et tapis :", A2[idx["tapis"], idx["tapis"]])
A3 = np.linalg.matrix_power(A, 3)
print("trace de A^3 / 6 = nombre de triangles :", np.trace(A3) // 6)
```
<!--sortie-->
```text
chemins de longueur 2 entre bol et lampe : 1
chemins de longueur 2 entre tapis et tapis : 3
trace de A^3 / 6 = nombre de triangles : 1
```

Entre le bol et la lampe, il y a un seul chemin en deux pas (bol → tapis → lampe). Le tapis a trois chemins de longueur 2 vers lui-même : c'est son degré (il part vers un voisin et revient). Et la trace de $\mathbf{A}^3$ compte les triangles (chaque triangle est compté 6 fois : 3 sommets de départ × 2 sens) ; ici on trouve 1 triangle : tapis–lampe–coussin. Un triangle dans un graphe de co-achat signale un trio de produits qui se vendent bien ensemble.

### 1.6.4 Parcourir un graphe : la recherche en largeur

> 💡 **Intuition.** Vous lancez une pierre dans l'eau : les ondes atteignent d'abord les voisins directs, puis les voisins des voisins, etc. La **recherche en largeur** (*BFS*, *breadth-first search*) explore un graphe de la même manière, « cercle par cercle ». Elle trouve le **plus court chemin** (en nombre d'arêtes) entre deux sommets.

L'algorithme utilise une **file** (premier arrivé, premier servi) :

1. Mettre le sommet de départ dans la file, avec la distance 0.
2. Tant que la file n'est pas vide : retirer le premier sommet ; pour chacun de ses voisins non encore vus, noter sa distance (celle du sommet + 1) et le mettre en fin de file.

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

Depuis le plateau : le bol est à distance 1, le tapis à 2, la lampe et le coussin à 3. Si un client achète un plateau, la « chaîne de recommandations » la plus courte vers une lampe passe par le bol puis le tapis.

> ✅ **À retenir (discret et graphes).**
>
> - Ensembles : $\cup$, $\cap$, $\setminus$ ; Jaccard $=|A\cap B|/|A\cup B|$.
> - Principe multiplicatif ; $n!$ ordres ; $\binom{n}{k}$ choix sans ordre ; ça explose très vite.
> - Un graphe = sommets + arêtes ; le stocker en **liste d'adjacence** ou en **matrice d'adjacence**.
> - $(\mathbf{A}^k)_{ij}$ = nombre de chemins de longueur $k$ de $i$ à $j$.
> - BFS : exploration par cercles, plus courts chemins sur graphe non pondéré.


## 1.7 Exercices du chapitre 1

> 🧭 **Mode d'emploi.** Essayez chaque exercice **sur papier ou dans un notebook avant** de lire le corrigé. Les exercices sont rangés par difficulté croissante : ⭐ (application directe), ⭐⭐ (demande un raisonnement), ⭐⭐⭐ (synthèse). Les corrigés sont juste après l'énoncé de la série, avec le calcul à la main **et** la vérification par code.

### Énoncés

**Exercice 1 ⭐ (cosinus).** Deux clientes sont décrites par leurs achats (bols, tapis, lampes) : $\mathbf{u}=(1,2,2)$ et $\mathbf{v}=(2,0,1)$. Calculez leur similarité cosinus. Sont-elles plutôt semblables ?

**Exercice 2 ⭐ (produit matriciel et système).** Soit $\mathbf{A}=\begin{pmatrix}2&1\\1&3\end{pmatrix}$ et $\mathbf{b}=\begin{pmatrix}5\\10\end{pmatrix}$. (a) Calculez $\mathbf{A}^2$. (b) Résolvez $\mathbf{A}\mathbf{x}=\mathbf{b}$ à la main (par substitution), puis vérifiez avec NumPy.

**Exercice 3 ⭐⭐ (valeurs propres).** Trouvez les valeurs propres et des vecteurs propres de $\mathbf{M}=\begin{pmatrix}4&1\\2&3\end{pmatrix}$. Vérifiez que la trace est la somme et le déterminant le produit des valeurs propres.

**Exercice 4 ⭐ (dérivées).** Pour $f(x)=x^3-6x^2+9x$, calculez $f'$, trouvez les points où la pente est nulle, et déterminez s'il s'agit de minima ou de maxima grâce à $f''$.

**Exercice 5 ⭐⭐ (gradient).** Pour $f(x,y)=x^2+3y^2$, calculez le gradient en $(1,1)$ puis effectuez **un pas** de descente de gradient avec $\eta=0{,}1$. La valeur de $f$ a-t-elle diminué ?

**Exercice 6 ⭐⭐ (pas d'apprentissage).** Soit $f(x)=2(x-1)^2$. (a) Écrivez la récurrence de la descente de gradient. (b) Pour quelles valeurs de $\eta$ converge-t-elle ? (c) Quelle valeur de $\eta$ converge en un seul pas ?

**Exercice 7 ⭐⭐ (Lagrange).** Yasmine dispose de 10 mètres de ruban pour entourer un rectangle de tissu. Quel rectangle d'aire maximale peut-on former ? Utilisez un multiplicateur de Lagrange, c'est-à-dire maximisez $xy$ sous la contrainte $x+y=5$ (demi-périmètre), et interprétez $\lambda$.

**Exercice 8 ⭐⭐⭐ (Python : régression à la main).** Les ventes de bougies en fonction de la température sont : $x=(10,15,20,25)$ et $y=(40,35,28,22)$. (a) Ajustez la droite $y=ax+b$ avec les équations normales. (b) Retrouvez le résultat par descente de gradient sur la variable **centrée**. (c) Prédisez les ventes à 18 °C.

**Exercice 9 ⭐⭐ (analyse numérique).** Expliquez pourquoi `0.1 * 3 == 0.3` est faux en Python et écrivez le test correct. Puis donnez la formule du nombre de chiffres perdus pour un conditionnement $\kappa=10^6$.

**Exercice 10 ⭐⭐ (graphes).** Dans le graphe de co-achat du 1.6, calculez avec $\mathbf{A}^2$ le nombre de chemins de longueur 2 entre « plateau » et « tapis », puis entre « bol » et « coussin ». Vérifiez en les énumérant à la main.

### Corrigés

**Corrigé 1.** $\mathbf{u}\cdot\mathbf{v}=1\cdot2+2\cdot0+2\cdot1=4$. $\lVert\mathbf{u}\rVert=\sqrt{1+4+4}=3$, $\lVert\mathbf{v}\rVert=\sqrt{4+0+1}=\sqrt5$. Donc $\cos\theta=\dfrac{4}{3\sqrt5}\approx0{,}596$.

```python
import numpy as np
u = np.array([1, 2, 2]); v = np.array([2, 0, 1])
cos = u @ v / (np.linalg.norm(u) * np.linalg.norm(v))
print("cosinus =", round(cos, 3), "  angle =", round(np.degrees(np.arccos(cos)), 1), "degrés")
```
<!--sortie-->
```text
cosinus = 0.596   angle = 53.4 degrés
```

Un cosinus de 0,6 correspond à un angle d'environ 53° : **moyennement semblables** (1 = identiques, 0 = rien en commun). Elles aiment toutes deux les bols mais diffèrent sur les tapis.

**Corrigé 2.** (a) $\mathbf{A}^2=\begin{pmatrix}2\cdot2+1\cdot1&2\cdot1+1\cdot3\\1\cdot2+3\cdot1&1\cdot1+3\cdot3\end{pmatrix}=\begin{pmatrix}5&5\\5&10\end{pmatrix}$. (b) Les équations sont $2x+y=5$ et $x+3y=10$. De la première : $y=5-2x$. En remplaçant : $x+15-6x=10$, donc $-5x=-5$, $x=1$ et $y=3$.

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

**Corrigé 3.** Le polynôme caractéristique est $\det(\mathbf{M}-\lambda\mathbf{I})=(4-\lambda)(3-\lambda)-2=\lambda^2-7\lambda+10=(\lambda-5)(\lambda-2)$. Les valeurs propres sont $5$ et $2$. Pour $\lambda=5$ : $(\mathbf{M}-5\mathbf{I})\mathbf{v}=\begin{pmatrix}-1&1\\2&-2\end{pmatrix}\mathbf{v}=\mathbf{0}$ donne $\mathbf{v}=(1,1)$. Pour $\lambda=2$ : $\begin{pmatrix}2&1\\2&1\end{pmatrix}\mathbf{v}=\mathbf{0}$ donne $\mathbf{v}=(1,-2)$. Trace : $4+3=7=5+2$ ✓. Déterminant : $4\cdot3-1\cdot2=10=5\times2$ ✓.

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

**Corrigé 4.** $f'(x)=3x^2-12x+9=3(x-1)(x-3)$, nulle en $x=1$ et $x=3$. $f''(x)=6x-12$. En $x=1$ : $f''=-6<0$, c'est un **maximum local** ($f(1)=4$). En $x=3$ : $f''=6>0$, c'est un **minimum local** ($f(3)=0$).

```python
f = lambda x: x**3 - 6*x**2 + 9*x
print("f(1) =", f(1), " f(3) =", f(3))
```
<!--sortie-->
```text
f(1) = 4  f(3) = 0
```

**Corrigé 5.** $\nabla f=(2x,\,6y)$, donc $\nabla f(1,1)=(2,6)$. Le pas : $(1,1)-0{,}1\,(2,6)=(0{,}8;\,0{,}4)$. Avant : $f(1,1)=1+3=4$. Après : $f(0{,}8;0{,}4)=0{,}64+3\cdot0{,}16=1{,}12$. La valeur a bien diminué (de 4 à 1,12).

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

**Corrigé 6.** (a) $f'(x)=4(x-1)$, donc $x_{k+1}=x_k-4\eta(x_k-1)$, soit $x_{k+1}-1=(1-4\eta)(x_k-1)$. (b) L'écart à 1 est multiplié par $(1-4\eta)$ à chaque pas ; il tend vers 0 si $|1-4\eta|<1$, c'est-à-dire $0<\eta<\tfrac12$. (On retrouve $\eta<2/\lambda_{\max}$ avec $f''=4$.) (c) Le facteur est nul si $\eta=\tfrac14$ : on tombe sur le minimum en un seul pas.

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

**Corrigé 7.** On maximise $g(x,y)=xy$ sous $x+y=5$. Lagrangien : $\mathcal{L}=xy-\lambda(x+y-5)$. Les conditions $\partial_x\mathcal{L}=y-\lambda=0$ et $\partial_y\mathcal{L}=x-\lambda=0$ donnent $x=y=\lambda$. La contrainte donne $2\lambda=5$, donc $x=y=2{,}5$ m : le **carré** de 2,5 m de côté, d'aire $6{,}25\ \text{m}^2$. Le multiplicateur $\lambda=2{,}5$ s'interprète comme le prix de l'ombre : un mètre de demi-périmètre en plus rapporte environ 2,5 m² d'aire en plus (l'aire optimale est $(c/2)^2$ et sa dérivée par rapport à $c$ est $c/2=2{,}5$).

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

**Corrigé 8.** (a) On construit $\mathbf{X}$ avec une colonne $x$ et une colonne de 1, puis on résout $\mathbf{X}^\top\mathbf{X}\boldsymbol\theta=\mathbf{X}^\top\mathbf{y}$. (b) On centre $x$ (moyenne 17,5), on descend le gradient, puis on revient à l'ordonnée d'origine par $b=b'-a\bar{x}$. (c) On évalue la droite en 18. Attention au pas : la hessienne vaut ici $2\mathbf{X}_c^\top\mathbf{X}_c=\operatorname{diag}(250,\,8)$, donc il faut $\eta<2/250=0{,}008$ ; nous prendrons $\eta=0{,}003$.

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

**Corrigé 9.** Le nombre $0{,}1$ n'a pas d'écriture finie en base 2 ; `0.1 * 3` vaut `0.30000000000000004`, un flottant différent de celui de `0.3`. Le bon test est `math.isclose(0.1 * 3, 0.3)`. Pour $\kappa=10^6$ on perd environ $\log_{10}\kappa=6$ chiffres significatifs sur les 16 disponibles : il en reste environ 10.

```python
import math
print(0.1 * 3, 0.1 * 3 == 0.3, math.isclose(0.1 * 3, 0.3))
```
<!--sortie-->
```text
0.30000000000000004 False True
```

**Corrigé 10.** Avec l'ordre des produits `["bol","tapis","lampe","plateau","coussin"]` (indices 0 à 4), on lit $(\mathbf{A}^2)_{\text{plateau},\text{tapis}}$ et $(\mathbf{A}^2)_{\text{bol},\text{coussin}}$. À la main : plateau—bol—tapis est le seul chemin en deux pas du plateau au tapis (le plateau n'a qu'un voisin, le bol), donc 1. Bol—tapis—coussin est le seul chemin en deux pas du bol au coussin (les voisins du bol sont plateau et tapis ; seul le tapis touche le coussin), donc 1.

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

---

## Bilan du chapitre 1

Vous savez maintenant :

- **représenter** des données comme des vecteurs et des matrices, mesurer des ressemblances (produit scalaire, cosinus), résoudre des systèmes et comprendre le rang ;
- **décomposer** une matrice (valeurs propres, SVD) pour en extraire la structure — l'idée derrière l'ACP ;
- **dériver** et calculer un gradient pour savoir comment une quantité réagit à ses paramètres ;
- **optimiser** : écrire une fonction de perte, la minimiser par descente de gradient, gérer les contraintes avec Lagrange ;
- **lire** une formule grâce à la fiche de notations, et **se méfier** des arrondis de l'ordinateur.

Le chapitre 2 change de point de vue : jusqu'ici, nos nombres étaient certains. Désormais ils seront **aléatoires**, et il faudra apprendre à raisonner dans l'incertitude.


---

# Chapitre 2 : Probabilités

> « Le hasard n'est pas le désordre :
> c'est un ordre qui apparaît quand on regarde **assez de fois**. »

Dans le chapitre 1, tous nos nombres étaient connus avec certitude. Mais les données réelles ne le sont jamais : demain, Yasmine vendra peut-être 12 bols, peut-être 25. Un client cliquera ou non sur la publicité. Un paiement sera légitime ou frauduleux. Les **probabilités** sont le langage mathématique de cette incertitude, et la **statistique** (chapitre 3) en est la réciproque : à partir de ce qu'on observe, remonter à ce qui se passe « derrière ».

## Le chemin de ce chapitre

- **2.1 Probabilités et formule de Bayes** : calculer des chances, mettre à jour ses croyances quand on apprend quelque chose. C'est le cœur du raisonnement en incertitude, et il est plus subtil qu'il n'y paraît.
- **2.2 Variables aléatoires et lois usuelles** : donner un « visage » au hasard avec les lois de Bernoulli, binomiale, de Poisson, uniforme, exponentielle et normale, et savoir laquelle choisir.
- **2.3 Espérance, variance, covariance** : résumer une loi par quelques nombres, et mesurer comment deux variables bougent ensemble.
- **2.4 Loi des grands nombres et théorème central limite** : les deux résultats qui rendent la statistique possible. Pourquoi une moyenne sur beaucoup d'observations devient fiable, et pourquoi la courbe en cloche est partout.
- ➕ **Pour aller plus loin** : la théorie de la mesure (ce que « probabilité » veut vraiment dire) et les processus stochastiques (le hasard qui évolue dans le temps).
- **2.7 Exercices corrigés**.

> 💡 **Deux manières de voir une probabilité.**
> - **Fréquentiste** : $P(\text{pile})=0{,}5$ signifie que, sur un très grand nombre de lancers, environ la moitié donne pile.
> - **Bayésienne** : $P(\text{la livraison arrivera demain})=0{,}8$ exprime un **degré de confiance**, même pour un événement qui n'arrivera qu'une fois.
>
> Les règles de calcul sont les mêmes dans les deux cas. Nous utiliserons les deux interprétations selon les situations.

> 🛠️ **Notre outil : la simulation.** Beaucoup de résultats de ce chapitre se démontrent. Mais on peut aussi **les voir** en faisant « jouer » l'ordinateur des milliers de fois. Nous utiliserons systématiquement les deux : la démonstration pour *comprendre pourquoi*, la simulation pour *y croire*. Avec NumPy, le générateur aléatoire s'obtient par `rng = np.random.default_rng(graine)`. La **graine** (*seed*) fixe la suite de nombres tirés : avec la même graine, vous obtiendrez exactement les mêmes résultats que dans ce livre.


## 2.1 Probabilités et formule de Bayes

### 2.1.1 Le vocabulaire : univers, événements, probabilité

> 💡 **Intuition.** Une **expérience aléatoire** est une situation dont l'issue est incertaine : lancer un dé, observer si un visiteur achète, mesurer le temps avant la prochaine commande. On liste d'abord **tout ce qui peut arriver**, puis on attribue à chaque possibilité un nombre entre 0 et 1 qui mesure sa chance.

- L'**univers** $\Omega$ (oméga) est l'ensemble de toutes les issues possibles. Pour un dé : $\Omega=\{1,2,3,4,5,6\}$.
- Un **événement** est une partie de $\Omega$ : « obtenir un nombre pair » est $A=\{2,4,6\}$.
- La **probabilité** $P(A)$ est un nombre entre 0 (impossible) et 1 (certain).

Quand toutes les issues sont **équiprobables** (un dé non truqué), on compte :

$$P(A)=\frac{\text{nombre d'issues favorables}}{\text{nombre d'issues possibles}}=\frac{|A|}{|\Omega|}.$$

Ici, la section 1.6 sur le dénombrement nous sert directement : $P(\text{pair})=3/6=0{,}5$.

**Les trois règles du jeu.** Toute la théorie des probabilités découle de trois règles (les *axiomes de Kolmogorov*) :

1. $P(A)\ge 0$ pour tout événement $A$.
2. $P(\Omega)=1$ : il arrive forcément *quelque chose*.
3. Si $A$ et $B$ sont **incompatibles** (jamais ensemble), alors $P(A\cup B)=P(A)+P(B)$.

> 📐 **Trois conséquences immédiates.**
>
> - **Complémentaire** : $P(\bar{A})=1-P(A)$. *Preuve* : $A$ et $\bar{A}$ sont incompatibles et leur union est $\Omega$, donc $P(A)+P(\bar{A})=P(\Omega)=1$. $\blacksquare$
> - **Union quelconque** : $P(A\cup B)=P(A)+P(B)-P(A\cap B)$. *Preuve* : en additionnant $P(A)$ et $P(B)$ on compte deux fois $A\cap B$ ; on retire donc une fois ce qui est en trop. (Formellement, on écrit $A\cup B$ comme union des trois morceaux incompatibles $A\setminus B$, $A\cap B$, $B\setminus A$.) $\blacksquare$
> - **Monotonie** : si $A\subset B$ alors $P(A)\le P(B)$.

**Exemple chiffré.** Yasmine envoie une promotion. La chance qu'un client ouvre l'e-mail est $P(O)=0{,}4$, celle qu'il visite le site est $P(V)=0{,}3$, et celle qu'il fasse les deux est $P(O\cap V)=0{,}2$. Quelle est la probabilité qu'il fasse **au moins une** des deux choses ?

$$P(O\cup V)=0{,}4+0{,}3-0{,}2=0{,}5.$$

Sans retrancher 0,2, on aurait trouvé 0,7 : on aurait compté deux fois les gens qui font les deux.

### 2.1.2 Voir une probabilité : la simulation

Une probabilité est la valeur vers laquelle tend la **fréquence** quand on répète l'expérience. Vérifions-le sur un dé, en lançant 10, 100, 1 000, 100 000 fois et en notant la fréquence de « 6 » (qui devrait être proche de $1/6\approx0{,}1667$) :

```python
import numpy as np
rng = np.random.default_rng(1)

for n in (10, 100, 1_000, 100_000):
    lancers = rng.integers(1, 7, size=n)          # entiers de 1 à 6 inclus
    freq = (lancers == 6).mean()
    print(f"{n:>7} lancers : fréquence de 6 = {freq:.4f}   (écart à 1/6 : {abs(freq - 1/6):.4f})")
```
<!--sortie-->
```text
     10 lancers : fréquence de 6 = 0.2000   (écart à 1/6 : 0.0333)
    100 lancers : fréquence de 6 = 0.1500   (écart à 1/6 : 0.0167)
   1000 lancers : fréquence de 6 = 0.1650   (écart à 1/6 : 0.0017)
 100000 lancers : fréquence de 6 = 0.1665   (écart à 1/6 : 0.0002)
```

Vous voyez l'écart se réduire à mesure que $n$ grandit. Ce phénomène porte un nom, la **loi des grands nombres** ; nous le démontrerons en 2.4.

> 🧪 **Astuce de programmation.** `(lancers == 6)` crée un tableau de booléens (`True`/`False`) ; sa moyenne vaut la **proportion** de `True`, car `True` compte pour 1 et `False` pour 0. C'est l'idiome de base pour estimer une probabilité par simulation.

### 2.1.3 Probabilité conditionnelle : changer d'information

> 💡 **Intuition.** Les probabilités dépendent de ce que l'on sait. La probabilité qu'une personne prise au hasard achète est de 20 %. Mais si l'on **sait** qu'elle vient d'Instagram, ce n'est plus la même question : on se restreint à la population Instagram.

Voici les 1 000 dernières visites de Dar Jasmin, classées par canal d'arrivée et par résultat (achat ou non) :

| | Achat | Pas d'achat | Total |
|---|---:|---:|---:|
| **Instagram** | 60 | 340 | 400 |
| **Site (recherche)** | 70 | 280 | 350 |
| **Boutique (passage)** | 75 | 175 | 250 |
| **Total** | 205 | 795 | 1 000 |

- $P(\text{achat})=205/1000=0{,}205$.
- $P(\text{achat et Instagram})=60/1000=0{,}06$.
- Parmi les 400 visiteurs Instagram, 60 achètent : $P(\text{achat}\mid\text{Instagram})=60/400=0{,}15$.

Cette dernière quantité se note $P(A\mid B)$, « probabilité de $A$ **sachant** $B$ ». Remarquez qu'on peut la retrouver à partir des probabilités globales :

$$P(A\mid B)=\frac{P(A\cap B)}{P(B)}=\frac{0{,}06}{0{,}40}=0{,}15 .$$

C'est la **définition** de la probabilité conditionnelle (valable si $P(B)>0$) : on divise par $P(B)$ parce qu'on a **réduit l'univers** à $B$.

```python
import pandas as pd      # bibliothèque de tableaux, étudiée en détail à la section 4.4
tableau = pd.DataFrame({"achat": [60, 70, 75], "pas_achat": [340, 280, 175]},
                       index=["Instagram", "Site", "Boutique"])
tableau["total"] = tableau.sum(axis=1)
tableau["P(achat | canal)"] = (tableau["achat"] / tableau["total"]).round(3)
print(tableau)
print("P(achat) global =", tableau["achat"].sum() / tableau["total"].sum())
```
<!--sortie-->
```text
           achat  pas_achat  total  P(achat | canal)
Instagram     60        340    400              0.15
Site          70        280    350              0.20
Boutique      75        175    250              0.30
P(achat) global = 0.205
```

Le canal « Boutique » convertit deux fois mieux qu'Instagram (30 % contre 15 %). Mais attention à ne pas confondre :

> ⚠️ **$P(A\mid B)\neq P(B\mid A)$.** Ici, $P(\text{achat}\mid\text{Instagram})=0{,}15$ ; mais $P(\text{Instagram}\mid\text{achat})=60/205\approx0{,}29$. Parmi les acheteurs, 29 % viennent d'Instagram, alors que parmi les visiteurs Instagram, seuls 15 % achètent. Ce sont deux questions différentes. Cette confusion est l'erreur de raisonnement la plus répandue, y compris chez les professionnels (nous en verrons un cas spectaculaire plus bas).

**La règle du produit.** En réarrangeant la définition :

$$P(A\cap B)=P(A\mid B)\,P(B).$$

Pour qu'un visiteur soit **à la fois** Instagram **et** acheteur, il faut d'abord qu'il vienne d'Instagram (0,40), puis qu'il achète sachant cela (0,15) : $0{,}40\times0{,}15=0{,}06$ ✓.

### 2.1.4 Indépendance

Deux événements sont **indépendants** si en connaître un ne change rien à la probabilité de l'autre : $P(A\mid B)=P(A)$, ce qui équivaut à

$$P(A\cap B)=P(A)\,P(B).$$

Dans le tableau, achat et canal sont-ils indépendants ? Si oui, on aurait $P(\text{achat}\mid\text{Instagram})=P(\text{achat})$. Or $0{,}15\neq0{,}205$ : **ils ne sont pas indépendants**. Le canal d'arrivée *informe* sur la probabilité d'achat, et c'est précisément ce qu'on cherche en analyse de données : repérer les variables qui informent sur d'autres.

> 🧪 **Indépendance ≠ incompatibilité.** Deux événements incompatibles ($A\cap B=\emptyset$) de probabilités non nulles sont au contraire **très dépendants** : si $A$ arrive, on est *certain* que $B$ n'arrive pas.

**Exemple d'événements indépendants.** Deux lancers de pièce successifs : $P(\text{pile puis pile})=0{,}5\times0{,}5=0{,}25$. Plus généralement, pour $n$ événements indépendants, on multiplie.

> 💡 **Application : « au moins un ».** Chaque colis a 2 % de chances d'être endommagé, indépendamment des autres. Sur 30 colis, quelle est la probabilité qu'**au moins un** soit endommagé ? Le complémentaire est « aucun n'est endommagé », de probabilité $0{,}98^{30}$. Donc

$$P(\text{au moins un})=1-0{,}98^{30}.$$

```python
print("P(au moins un colis endommagé sur 30) =", round(1 - 0.98 ** 30, 4))
```
<!--sortie-->
```text
P(au moins un colis endommagé sur 30) = 0.4545
```

Environ 45 % : avec 30 colis, il est presque *aussi probable qu'improbable* d'avoir au moins un problème, bien que chaque colis soit sûr à 98 %. Passer par le complémentaire est le réflexe à avoir pour tout « au moins un ».

### 2.1.5 La formule des probabilités totales

> 💡 **Intuition.** Pour trouver la probabilité d'un événement, on peut **découper** la population en groupes qui ne se chevauchent pas et dont l'union est tout l'univers (une **partition**), calculer la probabilité dans chaque groupe, puis faire la moyenne **pondérée** par la taille des groupes.

Si $B_1,\dots,B_k$ forment une partition de $\Omega$ :

$$P(A)=\sum_{j=1}^{k}P(A\mid B_j)\,P(B_j).$$

> 📐 **Preuve.** Les événements $A\cap B_j$ sont deux à deux incompatibles et leur union est $A$. Par l'axiome 3, $P(A)=\sum_j P(A\cap B_j)$. On applique ensuite la règle du produit à chaque terme : $P(A\cap B_j)=P(A\mid B_j)P(B_j)$. $\blacksquare$

**Exemple.** Reprenons le tableau : $P(\text{achat})=0{,}15\times0{,}40+0{,}20\times0{,}35+0{,}30\times0{,}25=0{,}06+0{,}07+0{,}075=0{,}205$. On retrouve bien 205/1000.

### 2.1.6 La formule de Bayes

Voici le résultat le plus célèbre de ce chapitre. On connaît $P(A\mid B)$ et on veut **renverser** la condition pour obtenir $P(B\mid A)$.

> 📐 **Formule de Bayes.** Pour $P(A)>0$ et $P(B)>0$,
>
> $$P(B\mid A)=\frac{P(A\mid B)\,P(B)}{P(A)}.$$
>
> *Preuve.* La règle du produit s'écrit de deux façons : $P(A\cap B)=P(A\mid B)P(B)=P(B\mid A)P(A)$. En divisant la seconde égalité par $P(A)$, on obtient la formule. $\blacksquare$
>
> Avec la partition $B_1,\dots,B_k$ et la formule des probabilités totales au dénominateur :
>
> $$P(B_i\mid A)=\frac{P(A\mid B_i)\,P(B_i)}{\sum_j P(A\mid B_j)\,P(B_j)}.$$

Les trois ingrédients ont des noms qu'on retrouvera tout au long de la data science :

| Terme | Nom | Signification |
|---|---|---|
| $P(B)$ | **a priori** (*prior*) | ce que l'on croyait *avant* d'observer |
| $P(A\mid B)$ | **vraisemblance** (*likelihood*) | à quel point l'observation est probable *si* $B$ est vrai |
| $P(B\mid A)$ | **a posteriori** (*posterior*) | ce que l'on croit *après* avoir observé |

**Exemple fondateur : l'alerte antifraude.** Dar Jasmin reçoit des paiements en ligne. Parmi eux, **1 %** sont frauduleux. Le système de détection se déclenche pour **95 %** des paiements frauduleux (c'est sa *sensibilité*), mais aussi pour **5 %** des paiements légitimes (ses *fausses alertes*). Un paiement déclenche l'alerte. **Quelle est la probabilité qu'il soit réellement frauduleux ?**

Réfléchissez avant de lire : beaucoup de gens répondent « environ 95 % ». Calculons.

*Méthode des « fréquences naturelles »* (la plus intuitive) : imaginons **10 000 paiements**.

- 1 % de fraudes : **100** paiements frauduleux. Le système en repère 95 % : **95** alertes justifiées.
- 99 % de légitimes : **9 900** paiements. Le système se trompe pour 5 % d'entre eux : **495** fausses alertes.
- Au total : $95+495=590$ alertes, dont seulement 95 sont justifiées.

$$P(\text{fraude}\mid\text{alerte})=\frac{95}{590}\approx0{,}161.$$

**Moins de 16 %.** Une alerte sur six seulement est une vraie fraude. La formule de Bayes donne exactement la même chose :

$$P(F\mid A)=\frac{P(A\mid F)\,P(F)}{P(A\mid F)\,P(F)+P(A\mid\bar{F})\,P(\bar{F})}=\frac{0{,}95\times0{,}01}{0{,}95\times0{,}01+0{,}05\times0{,}99}=\frac{0{,}0095}{0{,}0590}.$$

```python
p_f = 0.01                 # a priori : proportion de fraudes
sens = 0.95                # P(alerte | fraude)
fausse_alerte = 0.05       # P(alerte | légitime)

p_alerte = sens * p_f + fausse_alerte * (1 - p_f)          # probabilités totales
p_f_sachant_alerte = sens * p_f / p_alerte                 # Bayes
print("P(alerte)          =", round(p_alerte, 4))
print("P(fraude | alerte) =", round(p_f_sachant_alerte, 4))
```
<!--sortie-->
```text
P(alerte)          = 0.059
P(fraude | alerte) = 0.161
```

> 💡 **Pourquoi est-ce si contre-intuitif ?** Parce que la fraude est **rare** (1 %). Même un détecteur très bon produit, sur l'immense masse de paiements honnêtes, beaucoup plus de fausses alertes que de vraies. On appelle cela l'**erreur du taux de base** (*base rate fallacy*). Elle explique pourquoi un test médical « fiable à 95 % » pour une maladie rare donne surtout de faux positifs, et pourquoi il est si difficile de repérer des événements rares (fraude, panne, défaut).

**Mettre à jour en continu.** Supposons que le **même paiement** soit examiné par un second système indépendant, qui se déclenche aussi. La probabilité *a posteriori* d'hier devient l'*a priori* d'aujourd'hui :

```python
def mise_a_jour(prior, sens, fausse_alerte):
    """Probabilité de fraude après une nouvelle alerte."""
    return sens * prior / (sens * prior + fausse_alerte * (1 - prior))

p = 0.01
for i in range(1, 4):
    p = mise_a_jour(p, 0.95, 0.05)
    print(f"après {i} alerte(s) : P(fraude) = {p:.3f}")
```
<!--sortie-->
```text
après 1 alerte(s) : P(fraude) = 0.161
après 2 alerte(s) : P(fraude) = 0.785
après 3 alerte(s) : P(fraude) = 0.986
```

Après une alerte : 16 %. Après deux : 78,5 %. Après trois : 98,6 %. Chaque nouvelle information **déplace** la croyance, et c'est exactement ce que fait un modèle bayésien. Ce schéma « prior → vraisemblance → posterior » est le fondement de l'inférence bayésienne et du filtre antispam que nous esquissons plus bas.

### 2.1.7 Application : un mini-classifieur (le filtre naïf de Bayes)

Yasmine reçoit trop d'avis clients à lire un par un. Elle veut les classer automatiquement en « positif » ou « négatif ». Voici un échantillon de 20 avis déjà étiquetés, où l'on note si le mot **« cassé »** y apparaît :

| | Avis positif | Avis négatif |
|---|---:|---:|
| Nombre d'avis | 14 | 6 |
| … dont contenant « cassé » | 1 | 5 |

Un nouvel avis contient « cassé ». Est-il positif ou négatif ?

- A priori : $P(\text{pos})=14/20=0{,}7$ et $P(\text{nég})=0{,}3$.
- Vraisemblances : $P(\text{cassé}\mid\text{pos})=1/14$, $P(\text{cassé}\mid\text{nég})=5/6$.

$$P(\text{nég}\mid\text{cassé})=\frac{\tfrac56\times0{,}3}{\tfrac56\times0{,}3+\tfrac1{14}\times0{,}7}=\frac{0{,}25}{0{,}25+0{,}05}\approx0{,}833.$$

```python
prior = {"pos": 14 / 20, "neg": 6 / 20}
vrais = {"pos": 1 / 14, "neg": 5 / 6}
non_normalise = {c: prior[c] * vrais[c] for c in prior}
total = sum(non_normalise.values())
print({c: round(v / total, 3) for c, v in non_normalise.items()})
```
<!--sortie-->
```text
{'pos': 0.167, 'neg': 0.833}
```

L'avis est négatif avec 83 % de confiance. Le **classifieur naïf de Bayes** étend cette idée à des dizaines de mots à la fois, en supposant (naïvement) que les mots sont indépendants entre eux *sachant la classe*, ce qui permet de **multiplier** leurs vraisemblances. Malgré cette hypothèse fausse, il marche étonnamment bien pour le texte ; nous le retrouverons au volume II.

### 2.1.8 Trois paradoxes pour s'entraîner à se méfier de l'intuition

**Le problème de Monty Hall.** Dans un jeu télévisé, trois portes : derrière l'une, une voiture ; derrière les deux autres, une chèvre. Vous choisissez la porte 1. L'animateur, qui **sait** où est la voiture, ouvre une porte où il y a une chèvre (disons la 3) et vous propose de **changer** pour la porte 2. Faut-il changer ?

Beaucoup pensent « c'est du 50/50, donc peu importe ». Simulons plutôt :

```python
rng = np.random.default_rng(3)
n = 100_000
voiture = rng.integers(0, 3, size=n)       # porte gagnante
choix = np.zeros(n, dtype=int)             # on choisit toujours la porte 0

# si on ne change pas, on gagne quand notre porte est la bonne
gain_rester = (voiture == choix).mean()
# si on change : l'animateur élimine une chèvre, on prend l'autre porte ;
# on gagne donc exactement quand notre premier choix était MAUVAIS
gain_changer = (voiture != choix).mean()
print("gain en restant  :", round(gain_rester, 3))
print("gain en changeant:", round(gain_changer, 3))
```
<!--sortie-->
```text
gain en restant  : 0.333
gain en changeant: 0.667
```

Changer fait gagner dans environ **2 cas sur 3**. Explication : votre premier choix a 1/3 de chances d'être le bon, et l'animateur ne change pas cela. Les 2/3 restants se « concentrent » sur l'unique autre porte fermée. (L'animateur apporte de l'information *parce qu'il ne choisit pas au hasard* : il évite la voiture.)

**Le paradoxe des anniversaires.** Dans une salle de 23 personnes, quelle est la probabilité que deux d'entre elles au moins aient le même anniversaire ? Dites un chiffre avant de continuer. Par le complémentaire (et le principe multiplicatif de 1.6) :

$$P(\text{coïncidence})=1-\frac{365}{365}\cdot\frac{364}{365}\cdots\frac{365-n+1}{365}.$$

```python
def p_anniversaire(n):
    p_aucune = 1.0
    for i in range(n):
        p_aucune *= (365 - i) / 365
    return 1 - p_aucune

for n in (10, 23, 40, 70):
    print(f"{n:>3} personnes : P(au moins une coïncidence) = {p_anniversaire(n):.3f}")
```
<!--sortie-->
```text
 10 personnes : P(au moins une coïncidence) = 0.117
 23 personnes : P(au moins une coïncidence) = 0.507
 40 personnes : P(au moins une coïncidence) = 0.891
 70 personnes : P(au moins une coïncidence) = 0.999
```

Dès **23** personnes, la probabilité dépasse **50 %** ; à 70, elle est quasi certaine. Contre-intuitif parce qu'on pense à *notre* anniversaire alors que ce sont les $\binom{23}{2}=253$ **paires** qui comptent. Pour la data science, c'est la clé pour comprendre les **collisions** (deux clients avec le même identifiant haché, deux enregistrements en double) : elles arrivent bien plus tôt qu'on ne l'imagine.

**Le paradoxe de Simpson.** Une tendance observée dans plusieurs groupes peut s'**inverser** quand on les fusionne. Exemple : Yasmine teste deux versions d'une page de paiement, A et B, auprès de clients sur mobile et sur ordinateur.

| | Mobile | Ordinateur | Total |
|---|---:|---:|---:|
| **Page A** | 20 / 100 = 20 % | 210 / 700 = 30 % | 230 / 800 = 28,75 % |
| **Page B** | 150 / 700 = 21,4 % | 40 / 100 = 40 % | 190 / 800 = 23,75 % |

B est meilleure sur mobile (21,4 % contre 20 %) **et** sur ordinateur (40 % contre 30 %), pourtant A est meilleure au total (28,75 % contre 23,75 %).

```python
import pandas as pd
d = pd.DataFrame({
    "page":   ["A", "A", "B", "B"],
    "appareil": ["mobile", "ordi", "mobile", "ordi"],
    "achats": [20, 210, 150, 40],
    "visites": [100, 700, 700, 100]})
d["taux"] = (d["achats"] / d["visites"]).round(3)
print(d)
print(d.groupby("page")[["achats", "visites"]].sum().assign(taux=lambda t: (t.achats / t.visites).round(4)))
```
<!--sortie-->
```text
  page appareil  achats  visites   taux
0    A   mobile      20      100  0.200
1    A     ordi     210      700  0.300
2    B   mobile     150      700  0.214
3    B     ordi      40      100  0.400
      achats  visites    taux
page                         
A        230      800  0.2875
B        190      800  0.2375
```

L'explication est que la page A a reçu surtout des clients sur ordinateur (qui achètent beaucoup, quelle que soit la page), alors que B a reçu surtout des clients sur mobile (qui achètent moins). Le total mélange l'effet de la page avec l'effet de l'appareil. La leçon est cruciale : **une moyenne globale peut cacher une variable qui explique tout**. Avant de conclure, on se demande toujours : « quels sous-groupes cachés se mélangent ici ? ». Nous creuserons cette idée de *confusion* au volume III.

> ✅ **À retenir (probabilités et Bayes).**
>
> - Une probabilité est un nombre entre 0 et 1 respectant 3 axiomes ; on en déduit $P(\bar A)=1-P(A)$ et $P(A\cup B)=P(A)+P(B)-P(A\cap B)$.
> - Pour un « au moins un », passez par le **complémentaire**.
> - $P(A\mid B)=P(A\cap B)/P(B)$ ; règle du produit $P(A\cap B)=P(A\mid B)P(B)$ ; indépendance $\iff P(A\cap B)=P(A)P(B)$.
> - **Probabilités totales** : $P(A)=\sum_j P(A\mid B_j)P(B_j)$.
> - **Bayes** : $P(B\mid A)=\dfrac{P(A\mid B)P(B)}{P(A)}$ ; *posterior* ∝ *vraisemblance* × *prior*.
> - $P(A\mid B)\neq P(B\mid A)$, et méfiez-vous de l'**erreur du taux de base** et du **paradoxe de Simpson**.


## 2.2 Variables aléatoires et lois usuelles

### 2.2.1 Qu'est-ce qu'une variable aléatoire ?

> 💡 **Intuition.** Jusqu'ici nous parlions d'**événements** (« le client achète »). Mais les données sont des **nombres** : le montant du panier, le nombre de commandes, le temps d'attente. Une **variable aléatoire** (v.a.) est simplement **un nombre dont la valeur dépend du hasard**. On la note par une majuscule, $X$, et ses valeurs possibles par des minuscules, $x$.

Exemples chez Dar Jasmin :

- $X$ = nombre de commandes reçues entre 14 h et 15 h (0, 1, 2, 3, …) ;
- $Y$ = montant en dinars du prochain panier (n'importe quel nombre positif) ;
- $B$ = 1 si le prochain visiteur achète, 0 sinon.

On distingue deux familles :

| | Variable **discrète** | Variable **continue** |
|---|---|---|
| Valeurs | une liste dénombrable : 0, 1, 2, … | tout un intervalle de réels |
| Exemple | nombre de commandes | temps d'attente, montant exact |
| Description | **fonction de masse** $P(X=k)$ | **densité** $f(x)$ |
| Probabilité d'un intervalle | somme des $P(X=k)$ | **aire** sous la densité (intégrale du chapitre 1) |

> ⚠️ **Piège à connaître dès maintenant.** Pour une variable continue, la probabilité d'une valeur **exacte** est **zéro** : $P(X=2{,}5\text{ min})=0$. Avez-vous déjà mesuré un temps d'attente de *exactement* 2,500000… minutes ? Seuls des **intervalles** ont une probabilité : $P(2\le X\le3)$. La densité $f(x)$ n'est donc *pas* une probabilité : c'est une probabilité *par unité de longueur* (comme une densité de population se mesure en habitants par km²).

**La fonction de répartition.** Pour les deux familles, on peut définir

$$F(x)=P(X\le x),$$

la probabilité de rester **sous** le seuil $x$. Elle croît de 0 à 1. Elle sert à tout : $P(a<X\le b)=F(b)-F(a)$, et la **probabilité d'excéder** un seuil est $P(X>x)=1-F(x)$. Pour une variable continue, $F(x)=\int_{-\infty}^x f(t)\,dt$, et inversement $f=F'$ : c'est le théorème fondamental du 1.2.4.

Dans tout le chapitre, nous utiliserons la bibliothèque **SciPy** (`scipy.stats`), qui fournit pour chaque loi les mêmes méthodes :

| Méthode | Rôle |
|---|---|
| `.pmf(k)` / `.pdf(x)` | masse (discret) ou densité (continu) |
| `.cdf(x)` | fonction de répartition $F(x)=P(X\le x)$ |
| `.sf(x)` | « survie » $P(X>x)=1-F(x)$ (plus précis que `1 - cdf`) |
| `.ppf(q)` | **quantile** : la valeur $x$ telle que $F(x)=q$ (inverse de `cdf`) |
| `.rvs(size, random_state)` | **simuler** des tirages |
| `.mean()`, `.var()`, `.std()` | espérance, variance, écart-type (section 2.3) |

### 2.2.2 Loi de Bernoulli : le oui/non

C'est la plus simple : une expérience à **deux issues**, « succès » (1) avec probabilité $p$, « échec » (0) avec probabilité $1-p$.

$$P(B=1)=p,\qquad P(B=0)=1-p.$$

Le visiteur d'Instagram qui achète avec probabilité $p=0{,}15$ est une Bernoulli(0,15). On la note $B\sim\text{Bern}(p)$ (le symbole $\sim$ se lit « suit la loi »). C'est la brique de base de toutes les prédictions « oui/non » (clic, achat, fraude, désabonnement).

### 2.2.3 Loi binomiale : compter les succès

> 💡 **Intuition.** Vous répétez **$n$ fois** la même expérience de Bernoulli, **indépendamment** ; la loi binomiale décrit le **nombre de succès**.

Yasmine reçoit 20 visiteurs venant de la publicité ; chacun achète avec la probabilité $p=0{,}2$, indépendamment des autres. Soit $X$ le nombre d'acheteurs. Quelle est la probabilité d'avoir **exactement 4 acheteurs** ?

> 📐 **Construction de la formule.** Prenons une configuration précise, par exemple : les 4 premiers visiteurs achètent, les 16 suivants non. Par indépendance, sa probabilité est $p^4(1-p)^{16}$. Mais il y a d'autres configurations avec 4 acheteurs : on choisit **lesquels** des 20 visiteurs achètent, soit $\binom{20}{4}$ façons (section 1.6). Chacune a **la même** probabilité $p^4(1-p)^{16}$, et les configurations sont incompatibles : on additionne.
>
> $$P(X=k)=\binom{n}{k}\,p^k\,(1-p)^{n-k},\qquad k=0,1,\dots,n.$$

Pour $k=4$ : $\binom{20}{4}=4845$, donc $P(X=4)=4845\times0{,}2^4\times0{,}8^{16}\approx0{,}218$.

```python
from scipy import stats
import numpy as np
import math

n, p = 20, 0.2
# à la main, avec la formule
print("à la main :", round(math.comb(n, 4) * p**4 * (1 - p)**(n - 4), 4))
# avec scipy
X = stats.binom(n, p)
print("scipy     :", round(X.pmf(4), 4))
print("P(X >= 6) :", round(X.sf(5), 4), "  (sf(5) = P(X > 5))")
print("P(X <= 2) :", round(X.cdf(2), 4))
```
<!--sortie-->
```text
à la main : 0.2182
scipy     : 0.2182
P(X >= 6) : 0.1958   (sf(5) = P(X > 5))
P(X <= 2) : 0.2061
```

Quatre acheteurs est le résultat le plus fréquent (21,8 %), ce qui est logique car $20\times0{,}2=4$. Mais **six acheteurs ou plus** arrive avec une probabilité de presque 20 % : un jour « exceptionnel » n'est pas si exceptionnel. Voyez la forme complète :

![Loi binomiale et loi de Poisson : les probabilités de chaque valeur.](figures/ch02-lois-discretes.png)

**Vérification par simulation.** Simulons 100 000 journées de 20 visiteurs :

```python
rng = np.random.default_rng(10)
jours = rng.binomial(n=20, p=0.2, size=100_000)       # un nombre d'acheteurs par jour
print("fréquence de X = 4 :", round((jours == 4).mean(), 4))
print("fréquence de X >= 6:", round((jours >= 6).mean(), 4))
```
<!--sortie-->
```text
fréquence de X = 4 : 0.2195
fréquence de X >= 6: 0.1956
```

Les fréquences simulées retombent sur les valeurs théoriques, à quelques millièmes près.

### 2.2.4 Loi de Poisson : compter des événements rares

> 💡 **Intuition.** On compte les **événements qui surviennent au hasard dans le temps ou l'espace** : appels à un standard, commandes par heure, fautes de frappe par page, pannes par mois. On connaît seulement la **cadence moyenne** $\lambda$ (« en moyenne 3 commandes par heure »).

$$P(X=k)=e^{-\lambda}\frac{\lambda^k}{k!},\qquad k=0,1,2,\dots$$

Si Yasmine reçoit en moyenne **3 commandes par heure**, la probabilité de ne **recevoir aucune** commande pendant une heure est $e^{-3}\approx0{,}0498$, soit 5 % : environ une heure sur vingt est complètement vide. La probabilité d'en recevoir **exactement 3** est $e^{-3}\cdot3^3/3!\approx0{,}224$.

```python
Y = stats.poisson(mu=3)                      # scipy appelle λ « mu »
print("P(0 commande)  =", round(Y.pmf(0), 4))
print("P(3 commandes) =", round(Y.pmf(3), 4))
print("P(>= 6)        =", round(Y.sf(5), 4))
print("P(>= 10)       =", round(Y.sf(9), 5))
```
<!--sortie-->
```text
P(0 commande)  = 0.0498
P(3 commandes) = 0.224
P(>= 6)        = 0.0839
P(>= 10)       = 0.0011
```

Six commandes ou plus en une heure arrive environ 8 % du temps : utile pour dimensionner le personnel d'emballage.

> 📐 **D'où vient cette formule : Poisson comme limite de la binomiale.** Découpons l'heure en $n$ très petits intervalles (disons $n=3600$ secondes). Dans chacun, une commande arrive avec une probabilité minuscule $p=\lambda/n$ (pour que la moyenne $np$ reste égale à $\lambda$). Le nombre de commandes est alors binomial$(n,\lambda/n)$ et

> $$P(X=k)=\binom nk\Bigl(\frac\lambda n\Bigr)^k\Bigl(1-\frac\lambda n\Bigr)^{n-k}
> =\frac{\lambda^k}{k!}\cdot\frac{n(n-1)\cdots(n-k+1)}{n^k}\cdot\Bigl(1-\frac\lambda n\Bigr)^{n}\Bigl(1-\frac\lambda n\Bigr)^{-k}.$$
>
> Quand $n\to\infty$ : la fraction $\frac{n(n-1)\cdots(n-k+1)}{n^k}\to1$ (il y a $k$ facteurs, chacun tend vers 1) ; $(1-\lambda/n)^n\to e^{-\lambda}$ (la définition de l'exponentielle) ; $(1-\lambda/n)^{-k}\to1$. Il reste $e^{-\lambda}\lambda^k/k!$. $\blacksquare$

Vérifions-le numériquement : binomiale$(1000;\,0{,}003)$ contre Poisson$(3)$ :

```python
for k in range(0, 6):
    b = stats.binom(1000, 0.003).pmf(k)
    q = stats.poisson(3).pmf(k)
    print(f"k = {k} : binomiale = {b:.5f}   Poisson = {q:.5f}")
```
<!--sortie-->
```text
k = 0 : binomiale = 0.04956   Poisson = 0.04979
k = 1 : binomiale = 0.14914   Poisson = 0.14936
k = 2 : binomiale = 0.22415   Poisson = 0.22404
k = 3 : binomiale = 0.22438   Poisson = 0.22404
k = 4 : binomiale = 0.16828   Poisson = 0.16803
k = 5 : binomiale = 0.10087   Poisson = 0.10082
```

Les deux colonnes sont presque identiques. **Règle pratique** : quand $n$ est grand et $p$ petit, on peut remplacer Binomiale$(n,p)$ par Poisson$(np)$.

### 2.2.5 Les variables continues : la densité

Pour une variable continue, la loi est donnée par une **densité** $f$ : une fonction positive dont l'aire totale vaut 1, avec

$$P(a\le X\le b)=\int_a^b f(x)\,dx.$$

C'est ici que l'intégrale du chapitre 1 trouve son usage : une probabilité est une **aire**. Trois lois continues essentielles :

![Trois lois continues : uniforme, exponentielle, normale.](figures/ch02-lois-continues.png)

#### Loi uniforme : « aucune préférence »

$X\sim\mathcal{U}(a,b)$ : toutes les valeurs de $[a,b]$ sont également probables, de densité $\frac1{b-a}$. Un client appelle à une heure uniformément répartie entre 0 et 10 minutes après le début de l'heure : $P(X\le3)=3/10$. Le générateur aléatoire de l'ordinateur produit des $\mathcal{U}(0,1)$ ; toutes les autres lois en sont fabriquées.

#### Loi exponentielle : le temps d'attente

$X\sim\text{Exp}(\lambda)$ avec densité $f(x)=\lambda e^{-\lambda x}$ pour $x\ge0$. C'est le **temps d'attente** entre deux événements d'un processus de Poisson (nous l'avions rencontrée en 1.2.4). Sa fonction de répartition est $F(x)=1-e^{-\lambda x}$, donc

$$P(X>x)=e^{-\lambda x}.$$

Si les clients arrivent à la cadence de $\lambda=0{,}5$ par minute (un toutes les 2 minutes en moyenne), la probabilité d'attendre **plus de 3 minutes** le prochain client est $e^{-0{,}5\times3}=e^{-1{,}5}\approx0{,}223$.

```python
T = stats.expon(scale=1 / 0.5)         # scipy utilise scale = 1/λ
print("P(attendre > 3 min) =", round(T.sf(3), 4), " (formule : exp(-1.5) =", round(math.exp(-1.5), 4), ")")
print("médiane du temps d'attente :", round(T.ppf(0.5), 3), "min")
print("90 % des attentes sont < ", round(T.ppf(0.90), 2), "min")
```
<!--sortie-->
```text
P(attendre > 3 min) = 0.2231  (formule : exp(-1.5) = 0.2231 )
médiane du temps d'attente : 1.386 min
90 % des attentes sont <  4.61 min
```

La **médiane** (1,39 min) est inférieure à la moyenne (2 min) : la loi exponentielle est **asymétrique**, avec quelques attentes très longues qui tirent la moyenne vers le haut.

> 📐 **La propriété d'absence de mémoire.** Si vous avez déjà attendu 2 minutes sans voir de client, la probabilité d'attendre encore 3 minutes est **la même** que si vous veniez d'arriver. Preuve :
>
> $$P(X>s+t\mid X>s)=\frac{P(X>s+t)}{P(X>s)}=\frac{e^{-\lambda(s+t)}}{e^{-\lambda s}}=e^{-\lambda t}=P(X>t).\ \blacksquare$$
>
> La première égalité est la définition du conditionnel (car $\{X>s+t\}\subset\{X>s\}$). Le processus « ne se souvient pas » de ce qui s'est passé : il n'y a pas de « retard » à rattraper. (Contre-intuitif pour un bus supposé passer toutes les 10 minutes, mais exact pour des arrivées vraiment aléatoires.)

```python
# vérification numérique : P(X > 5 | X > 2)  ==  P(X > 3)
print(round(T.sf(5) / T.sf(2), 6), round(T.sf(3), 6))
```
<!--sortie-->
```text
0.22313 0.22313
```

#### Loi normale : la courbe en cloche

$X\sim\mathcal{N}(\mu,\sigma^2)$, de densité

$$f(x)=\frac1{\sigma\sqrt{2\pi}}\exp\Bigl(-\frac{(x-\mu)^2}{2\sigma^2}\Bigr).$$

Deux paramètres : $\mu$ **centre** la cloche, $\sigma$ (l'écart-type) mesure son **étalement**. On la rencontre partout : tailles, erreurs de mesure, moyennes d'échantillons (on verra pourquoi en 2.4).

Les ventes quotidiennes de Dar Jasmin suivent à peu près $\mathcal{N}(\mu=120,\ \sigma=15)$. Aucune formule fermée n'existe pour la fonction de répartition : on utilise l'ordinateur.

```python
V = stats.norm(loc=120, scale=15)
print("P(X > 150)             =", round(V.sf(150), 4))
print("P(105 < X < 135)       =", round(V.cdf(135) - V.cdf(105), 4))
print("jour 'exceptionnel' : 95 % des jours sont sous", round(V.ppf(0.95), 1), "ventes")
```
<!--sortie-->
```text
P(X > 150)             = 0.0228
P(105 < X < 135)       = 0.6827
jour 'exceptionnel' : 95 % des jours sont sous 144.7 ventes
```

![Les ventes quotidiennes suivent N(120 ; 15²). Un jour à plus de 150 ventes survient environ 2 fois sur 100.](figures/ch02-normale-zones.png)

**Centrer et réduire : le score $z$.** Comment comparer des valeurs de lois différentes ? On mesure **combien d'écarts-types** on est du centre :

$$z=\frac{x-\mu}{\sigma}.$$

Si $X\sim\mathcal{N}(\mu,\sigma^2)$, alors $Z=(X-\mu)/\sigma\sim\mathcal{N}(0,1)$, la **loi normale centrée réduite**. Un jour à 150 ventes correspond à $z=(150-120)/15=2$ : deux écarts-types au-dessus de la moyenne. Toutes les probabilités normales se ramènent à celles de $\mathcal{N}(0,1)$, dont on retient trois repères :

| Intervalle | Probabilité |
|---|---|
| $\mu\pm1\sigma$ | environ **68 %** |
| $\mu\pm2\sigma$ | environ **95 %** |
| $\mu\pm3\sigma$ | environ **99,7 %** |

```python
for k in (1, 2, 3):
    print(f"P(|Z| < {k}) = {stats.norm.cdf(k) - stats.norm.cdf(-k):.4f}")
print("z tel que P(Z < z) = 0.975 :", round(stats.norm.ppf(0.975), 3))
```
<!--sortie-->
```text
P(|Z| < 1) = 0.6827
P(|Z| < 2) = 0.9545
P(|Z| < 3) = 0.9973
z tel que P(Z < z) = 0.975 : 1.96
```

Ce dernier nombre, **1,96**, apparaîtra sans cesse dans les intervalles de confiance du chapitre 3.

> 🧪 **Test express « est-ce normal ? ».** Un jour à 190 ventes ($z=4{,}67$) serait extraordinairement rare si la loi était vraiment normale (environ 1 chance sur 700 000 d'être aussi haut). Si cela arrive, la loi n'est probablement pas la bonne ou un événement particulier s'est produit (promotion, fête). Détecter les valeurs avec $|z|$ très grand est la méthode de base de détection d'anomalies.

### 2.2.6 Quelle loi choisir ?

| Situation | Loi | Paramètres |
|---|---|---|
| un oui/non | Bernoulli | $p$ |
| nombre de succès sur $n$ essais indépendants | Binomiale | $n,\ p$ |
| nombre d'événements dans un intervalle, cadence $\lambda$ | Poisson | $\lambda$ |
| temps d'attente entre deux événements | Exponentielle | $\lambda$ |
| aucune préférence sur un intervalle | Uniforme | $a,\ b$ |
| somme de nombreux petits effets, mesures | Normale | $\mu,\ \sigma$ |

> ✅ **À retenir (variables aléatoires et lois).**
>
> - Une variable aléatoire est un nombre issu du hasard. Discrète : on décrit $P(X=k)$. Continue : on décrit une densité, et les probabilités sont des **aires**.
> - La fonction de répartition $F(x)=P(X\le x)$ ; avec `scipy.stats` : `pmf/pdf`, `cdf`, `sf`, `ppf`, `rvs`.
> - Bernoulli (oui/non), binomiale (compter les succès, $\binom nk p^k(1-p)^{n-k}$), Poisson (événements rares, $e^{-\lambda}\lambda^k/k!$).
> - Exponentielle : temps d'attente, sans mémoire. Normale : cloche, score $z$, règle 68-95-99,7.
> - Simulez toujours pour vérifier vos formules.


## 2.3 Espérance, variance, covariance

Une loi complète (une courbe, un tableau) est riche mais encombrante. Dans la pratique, on la résume par **quelques nombres** : où est son centre ? De combien s'étale-t-elle ? Comment deux variables évoluent-elles ensemble ?

### 2.3.1 L'espérance : la moyenne « à long terme »

> 💡 **Intuition.** L'**espérance** $E[X]$ est la valeur moyenne que prendrait $X$ si on répétait l'expérience un très grand nombre de fois. C'est une **moyenne pondérée** : chaque valeur est comptée proportionnellement à sa probabilité.

Pour une variable discrète et pour une variable continue (de densité $f$) :

$$E[X]=\sum_k k\,P(X=k)\qquad\text{et}\qquad E[X]=\int_{-\infty}^{+\infty}x\,f(x)\,dx.$$

**Exemple 1 : le dé.** $E[X]=1\cdot\tfrac16+2\cdot\tfrac16+\dots+6\cdot\tfrac16=\tfrac{21}6=3{,}5$. Remarquez que l'espérance n'est **pas** une valeur possible : on n'obtiendra jamais 3,5. C'est un centre de gravité, pas un résultat.

**Exemple 2 : une décision.** Yasmine hésite à lancer une nouvelle lampe. Elle envisage trois scénarios pour le bénéfice du premier trimestre :

| Scénario | Probabilité | Bénéfice (DT) |
|---|---:|---:|
| Grand succès | 0,3 | +5 000 |
| Succès moyen | 0,5 | +1 000 |
| Échec | 0,2 | −3 000 |

$$E[X]=0{,}3\times5000+0{,}5\times1000+0{,}2\times(-3000)=1500+500-600=1400.$$

Le lancement rapporte **en moyenne** 1 400 DT. Une option alternative sûre rapporterait 1 200 DT. Faut-il lancer ? L'espérance seule dit oui, mais elle ne dit rien du **risque** : il y a 20 % de chances de perdre de l'argent. C'est exactement le rôle de la variance, ci-dessous.

```python
import numpy as np
benefices = np.array([5000, 1000, -3000])
probas = np.array([0.3, 0.5, 0.2])

esperance = (benefices * probas).sum()
print("E[X] =", esperance)
```
<!--sortie-->
```text
E[X] = 1400.0
```

#### Propriétés de l'espérance

> 📐 **Linéarité.** Pour toutes variables $X$, $Y$ et constantes $a$, $b$ :
>
> $$E[aX+b]=aE[X]+b,\qquad E[X+Y]=E[X]+E[Y].$$
>
> *Preuve de la première (cas discret).* $E[aX+b]=\sum_k(ak+b)P(X=k)=a\sum_k kP(X=k)+b\sum_kP(X=k)=aE[X]+b\cdot1$. $\blacksquare$
>
> La seconde se démontre de la même façon avec une somme double. Elle est **toujours vraie, même si $X$ et $Y$ sont dépendantes** : c'est ce qui la rend si puissante.

**Exemple d'usage.** Si les ventes du jour ont une espérance de 120 bols à 25 DT l'unité, les recettes $25X$ ont pour espérance $25\times120=3000$ DT : on multiplie simplement.

**Application élégante : l'espérance d'une binomiale.** Une binomiale $X\sim\text{Bin}(n,p)$ est la somme de $n$ Bernoulli : $X=B_1+\dots+B_n$, avec $E[B_i]=1\cdot p+0\cdot(1-p)=p$. Par linéarité,

$$E[X]=E[B_1]+\dots+E[B_n]=np.$$

Sans aucun calcul avec $\binom nk$ ! Pour nos 20 visiteurs à 20 % : $E[X]=4$, ce qu'on avait deviné.

| Loi | Espérance |
|---|---|
| Bernoulli$(p)$ | $p$ |
| Binomiale$(n,p)$ | $np$ |
| Poisson$(\lambda)$ | $\lambda$ |
| Exponentielle$(\lambda)$ | $1/\lambda$ |
| Uniforme$(a,b)$ | $(a+b)/2$ |
| Normale$(\mu,\sigma^2)$ | $\mu$ |

> ⚠️ **Attention : $E[XY]\neq E[X]E[Y]$ en général**, et $E[f(X)]\neq f(E[X])$ en général. Exemple : pour le dé, $E[X^2]=\tfrac{91}6\approx15{,}17$, alors que $(E[X])^2=12{,}25$. L'écart entre ces deux nombres est justement la **variance**.

### 2.3.2 La variance : mesurer l'étalement

Deux commerçants ont chacun un bénéfice moyen de 1 000 DT par mois. Chez l'un, c'est toujours entre 950 et 1 050. Chez l'autre, ça varie de −2 000 à +4 000. Même espérance, risques très différents. La **variance** mesure l'écart typique au centre :

$$\operatorname{Var}(X)=E\bigl[(X-\mu)^2\bigr],\qquad \mu=E[X].$$

On prend le **carré** de l'écart pour que les écarts positifs et négatifs ne se compensent pas. L'**écart-type** $\sigma=\sqrt{\operatorname{Var}(X)}$ ramène le résultat à l'unité d'origine (des dinars, pas des dinars²).

> 📐 **Formule de calcul (« moyenne des carrés moins carré de la moyenne »).**
>
> $$\operatorname{Var}(X)=E[X^2]-\bigl(E[X]\bigr)^2.$$
>
> *Preuve.* On développe le carré : $(X-\mu)^2=X^2-2\mu X+\mu^2$. Par linéarité, $E[(X-\mu)^2]=E[X^2]-2\mu E[X]+\mu^2=E[X^2]-2\mu^2+\mu^2=E[X^2]-\mu^2$. $\blacksquare$

*(Rappel de la section ➕ analyse numérique : cette formule est parfaite sur le papier, mais dangereuse sur ordinateur si $\mu$ est grand devant $\sigma$.)*

**Retour à la lampe.** Calculons $E[X^2]$ puis la variance :

$$E[X^2]=0{,}3\times5000^2+0{,}5\times1000^2+0{,}2\times3000^2=7{,}5\cdot10^6+0{,}5\cdot10^6+1{,}8\cdot10^6=9{,}8\cdot10^6,$$

$$\operatorname{Var}(X)=9{,}8\cdot10^6-1400^2=9{,}8\cdot10^6-1{,}96\cdot10^6=7{,}84\cdot10^6,\qquad\sigma=2800\ \text{DT}.$$

```python
e_carre = (benefices**2 * probas).sum()
variance = e_carre - esperance**2
print("E[X^2]   =", e_carre)
print("Var(X)   =", variance)
print("écart-type =", np.sqrt(variance))
print("P(perte)   =", probas[benefices < 0].sum())
```
<!--sortie-->
```text
E[X^2]   = 9800000.0
Var(X)   = 7840000.0
écart-type = 2800.0
P(perte)   = 0.2
```

L'écart-type (2 800 DT) est **deux fois plus grand** que l'espérance (1 400 DT) : l'option est très risquée. Face à l'option sûre à 1 200 DT, le gain moyen n'est supérieur que de 200 DT alors que le risque est considérable. Beaucoup de gens (et de gérants) préféreraient l'option sûre. Il n'y a pas de « bonne » réponse mathématique : la variance **quantifie** le risque pour que la décision soit éclairée.

#### Propriétés de la variance

> 📐 **Effet d'un changement d'échelle.** $\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X)$.
>
> *Preuve.* $E[aX+b]=a\mu+b$, donc $(aX+b)-E[aX+b]=a(X-\mu)$ et $\operatorname{Var}(aX+b)=E[a^2(X-\mu)^2]=a^2\operatorname{Var}(X)$. $\blacksquare$
>
> Conséquences : ajouter une constante ($+b$) ne change pas l'étalement ; multiplier par $a$ multiplie l'écart-type par $|a|$. Convertir des dinars en euros multiplie l'écart-type par le taux de change, et c'est tout.

> 📐 **Somme de variables indépendantes.** Si $X$ et $Y$ sont **indépendantes**, $\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)$. (Nous démontrons le cas général au 2.3.3.)

**Variance d'une binomiale.** $B_i$ de Bernoulli : $E[B_i^2]=p$ (car $B_i^2=B_i$), donc $\operatorname{Var}(B_i)=p-p^2=p(1-p)$. Pour $X=\sum B_i$ avec des $B_i$ indépendantes : $\operatorname{Var}(X)=np(1-p)$.

| Loi | Variance |
|---|---|
| Bernoulli$(p)$ | $p(1-p)$ |
| Binomiale$(n,p)$ | $np(1-p)$ |
| Poisson$(\lambda)$ | $\lambda$ (variance = espérance !) |
| Exponentielle$(\lambda)$ | $1/\lambda^2$ |
| Uniforme$(a,b)$ | $(b-a)^2/12$ |
| Normale$(\mu,\sigma^2)$ | $\sigma^2$ |

Vérifions numériquement avec `scipy` et par simulation :

```python
from scipy import stats
rng = np.random.default_rng(21)

lois = {"Binomiale(20; 0,2)": (stats.binom(20, 0.2), rng.binomial(20, 0.2, 200_000)),
        "Poisson(3)":         (stats.poisson(3),     rng.poisson(3, 200_000)),
        "Exponentielle(0,5)": (stats.expon(scale=2), rng.exponential(2, 200_000)),
        "Normale(120; 15)":   (stats.norm(120, 15),  rng.normal(120, 15, 200_000))}

print(f"{'loi':<20}{'E théo':>9}{'E simulé':>10}{'Var théo':>10}{'Var simulée':>12}")
for nom, (loi, ech) in lois.items():
    print(f"{nom:<20}{loi.mean():>9.3f}{ech.mean():>10.3f}{loi.var():>10.3f}{ech.var():>12.3f}")
```
<!--sortie-->
```text
loi                    E théo  E simulé  Var théo Var simulée
Binomiale(20; 0,2)      4.000     4.004     3.200       3.209
Poisson(3)              3.000     3.005     3.000       3.006
Exponentielle(0,5)      2.000     2.001     4.000       3.968
Normale(120; 15)      120.000   120.001   225.000     225.467
```

La **loi de Poisson** a la propriété particulière que sa variance est égale à son espérance. Si les commandes de Yasmine varient *beaucoup plus* que leur moyenne (on parle de **sur-dispersion**), c'est un signe que le modèle de Poisson est trop simple.

### 2.3.3 Covariance et corrélation : bouger ensemble

> 💡 **Intuition.** Les jours où Yasmine dépense plus en publicité, vend-elle plus ? On cherche à mesurer si deux variables **varient dans le même sens**. Chaque jour, on regarde si $X$ est au-dessus de sa moyenne et si $Y$ l'est aussi : si les deux écarts ont **le même signe** la plupart du temps, la covariance est positive.

$$\operatorname{Cov}(X,Y)=E\bigl[(X-\mu_X)(Y-\mu_Y)\bigr]=E[XY]-E[X]E[Y].$$

**Exemple à la main.** Quatre semaines : dépenses publicitaires $x=(10,20,30,40)$ DT et ventes $y=(12,18,26,32)$.

- Moyennes : $\bar x=25$, $\bar y=22$.
- Écarts à la moyenne : $x-\bar x=(-15,-5,5,15)$ et $y-\bar y=(-10,-4,4,10)$.
- Produits : $(150,\ 20,\ 20,\ 150)$, de somme 340, donc covariance $=340/4=85$.

```python
x = np.array([10, 20, 30, 40.0]); y = np.array([12, 18, 26, 32.0])
cov_xy = ((x - x.mean()) * (y - y.mean())).mean()
print("covariance (à la main) =", cov_xy)
print("np.cov (n-1)           =", np.cov(x, y)[0, 1].round(2), "  <- divise par n-1, voir chapitre 3")
```
<!--sortie-->
```text
covariance (à la main) = 85.0
np.cov (n-1)           = 113.33   <- divise par n-1, voir chapitre 3
```

> ⚠️ **$n$ ou $n-1$ ?** `np.cov` divise par $n-1$ (estimateur sans biais, section 3.2) et donne 113,33 ; la formule de la **loi** divise par $n$. Pour de grands échantillons la différence disparaît ; ici avec $n=4$ elle est visible. On y reviendra.

**Problème : la covariance dépend des unités.** Si on mesure les dépenses en centimes, la covariance est multipliée par 100 sans que la relation change ! On **normalise** en divisant par les écarts-types, ce qui donne la **corrélation** de Pearson :

$$\rho_{XY}=\frac{\operatorname{Cov}(X,Y)}{\sigma_X\,\sigma_Y}\in[-1,\ 1].$$

> 📐 **Pourquoi $\rho$ est toujours entre −1 et 1.** C'est exactement l'inégalité de Cauchy–Schwarz du chapitre 1 ! Rangez les écarts à la moyenne $(x_i-\bar x)$ dans un vecteur $\mathbf{u}$ et $(y_i-\bar y)$ dans $\mathbf{v}$. Alors $\operatorname{Cov}\propto\mathbf{u}\cdot\mathbf{v}$, $\sigma_X\propto\lVert\mathbf{u}\rVert$, $\sigma_Y\propto\lVert\mathbf{v}\rVert$ (avec le même facteur $1/n$), et
>
> $$\rho=\frac{\mathbf{u}\cdot\mathbf{v}}{\lVert\mathbf{u}\rVert\,\lVert\mathbf{v}\rVert}=\cos\theta\in[-1,1].$$
>
> **La corrélation est le cosinus de l'angle entre les deux vecteurs d'écarts.** $\rho=1$ : même direction ; $\rho=-1$ : directions opposées ; $\rho=0$ : vecteurs perpendiculaires (orthogonaux). $\blacksquare$

Ici : $\rho=\dfrac{85}{\sqrt{125\times58}}\approx0{,}998$, une relation presque parfaitement linéaire.

```python
print("corrélation :", np.corrcoef(x, y)[0, 1].round(4))
```
<!--sortie-->
```text
corrélation : 0.9983
```

![Quatre nuages de points et leur corrélation. Le dernier montre qu'une corrélation nulle n'implique pas l'indépendance.](figures/ch02-correlations.png)

> ⚠️ **Trois mises en garde essentielles.**
>
> 1. **Corrélation n'est pas causalité.** Les glaces et les coups de soleil sont corrélés ; ni l'un ne cause l'autre : c'est la chaleur qui explique les deux. (Le volume III reviendra longuement sur les causes.)
> 2. **Indépendantes ⇒ non corrélées, mais pas l'inverse.** Le dernier nuage de la figure est une parabole : $Y$ est une **fonction exacte** de $X$ (à un peu de bruit près), donc très dépendante, pourtant $\rho\approx0$. Cela arrive parce que $\rho$ ne détecte que les relations **linéaires**.
> 3. **Regardez toujours le nuage de points.** Un chiffre unique peut cacher une structure très différente (nous le montrerons avec les « quartets » de la section 3.1).

> 📐 **Variance d'une somme (cas général).** $\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)+2\operatorname{Cov}(X,Y)$.
>
> *Preuve.* Posons $\tilde X=X-\mu_X$ et $\tilde Y=Y-\mu_Y$. Alors $\operatorname{Var}(X+Y)=E[(\tilde X+\tilde Y)^2]=E[\tilde X^2]+2E[\tilde X\tilde Y]+E[\tilde Y^2]$, ce qui est bien $\operatorname{Var}X+2\operatorname{Cov}(X,Y)+\operatorname{Var}Y$. $\blacksquare$
>
> Si $X$ et $Y$ sont indépendantes, $\operatorname{Cov}=0$ et on retrouve l'additivité des variances.

**Application : la diversification.** Les ventes quotidiennes de bols ($X$) et de tapis ($Y$) ont chacune une moyenne de 50 et un écart-type de 10. Quelle est la variabilité des ventes **totales** $X+Y$ ?

- Si les deux produits sont **corrélés positivement** ($\rho=+0{,}5$) : $\operatorname{Var}=100+100+2\times0{,}5\times100=300$, soit $\sigma\approx17{,}3$.
- Si les deux produits sont **corrélés négativement** ($\rho=-0{,}5$ : quand l'un se vend mal, l'autre se vend bien) : $\operatorname{Var}=100+100-100=100$, soit $\sigma=10$.

```python
rng = np.random.default_rng(8)
for rho in (0.5, -0.5):
    cov = [[100, rho * 100], [rho * 100, 100]]            # matrice de covariance
    ventes = rng.multivariate_normal([50, 50], cov, size=100_000)
    total = ventes.sum(axis=1)
    print(f"rho = {rho:+.1f} : écart-type du total = {total.std():.2f}   (théorie : {np.sqrt(200 + 2 * rho * 100):.2f})")
```
<!--sortie-->
```text
rho = +0.5 : écart-type du total = 17.29   (théorie : 17.32)
rho = -0.5 : écart-type du total = 9.97   (théorie : 10.00)
```

Mêmes moyennes, mêmes écarts-types individuels, mais un total **bien moins variable** (écart-type de 10 au lieu de 17) quand les produits se compensent. C'est le principe de la **diversification** : on réunit des produits (ou des placements) dont les hauts et les bas ne coïncident pas, pour stabiliser le tout.

#### La matrice de covariance

Avec plusieurs variables, on range toutes les variances et covariances dans une **matrice de covariance** $\boldsymbol\Sigma$ : variances sur la diagonale, covariances ailleurs. Elle est **symétrique** et ses valeurs propres sont **positives** ; c'est celle dont nous avions calculé les vecteurs propres au 1.1.3 (aperçu de l'ACP).

```python
rng = np.random.default_rng(2)
n = 365
temperature = rng.normal(25, 6, n)
visites = 80 + 3 * temperature + rng.normal(0, 15, n)
ventes = 0.2 * visites + rng.normal(0, 3, n)

donnees = np.column_stack([temperature, visites, ventes])
print("matrice de covariance :")
print(np.cov(donnees.T).round(1))
print("matrice de corrélation :")
print(np.corrcoef(donnees.T).round(2))
```
<!--sortie-->
```text
matrice de covariance :
[[ 36.7 106.2  22.6]
 [106.2 529.4 107.1]
 [ 22.6 107.1  31.1]]
matrice de corrélation :
[[1.   0.76 0.67]
 [0.76 1.   0.84]
 [0.67 0.84 1.  ]]
```

La matrice de **corrélation** est la covariance « normalisée » : diagonale de 1 et tout entre −1 et 1. Ici, on lit que la température est fortement corrélée aux visites, et que les visites sont corrélées aux ventes ; la corrélation température–ventes, un peu plus faible, est un effet **indirect** (la température agit sur les visites, qui agissent sur les ventes).

> ✅ **À retenir (espérance, variance, covariance).**
>
> - $E[X]$ = moyenne pondérée à long terme ; **linéaire** : $E[aX+b]=aE[X]+b$, $E[X+Y]=E[X]+E[Y]$ toujours.
> - $\operatorname{Var}(X)=E[(X-\mu)^2]=E[X^2]-\mu^2$ ; $\sigma=\sqrt{\operatorname{Var}}$ ; $\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X)$.
> - $\operatorname{Var}(X+Y)=\operatorname{Var}X+\operatorname{Var}Y+2\operatorname{Cov}(X,Y)$ : la covariance mesure comment les variables se combinent.
> - $\rho=\operatorname{Cov}/(\sigma_X\sigma_Y)$ est un **cosinus** : entre −1 et 1, sans unité. Il ne mesure que le lien **linéaire**, et ne prouve jamais une causalité.
> - La matrice de covariance range toutes les covariances ; c'est l'objet central de l'ACP.


## 2.4 Loi des grands nombres et théorème central limite

Ces deux résultats sont la **raison d'être de la statistique**. Le premier dit : *avec assez de données, la moyenne observée se rapproche de la vraie valeur.* Le second dit : *et l'erreur qui reste suit presque toujours la même courbe en cloche.* Ensemble, ils permettent de transformer un échantillon en conclusion chiffrée avec une marge d'erreur.

### 2.4.1 La moyenne d'échantillon est elle-même une variable aléatoire

Observons $n$ clients et notons $X_1,\dots,X_n$ leurs paniers. Ces variables sont **indépendantes et identiquement distribuées** (on écrit **i.i.d.**) : indépendantes entre elles, et issues de la même loi, d'espérance $\mu$ et de variance $\sigma^2$. Leur **moyenne d'échantillon** est

$$\bar X_n=\frac{X_1+\dots+X_n}{n}.$$

Un point capital, que beaucoup de débutants manquent : **$\bar X_n$ est elle-même aléatoire**. Si on reprend un autre échantillon de $n$ clients, on obtient une autre moyenne. Quelle est sa loi ? Par les propriétés de la section 2.3 :

$$E[\bar X_n]=\frac1n\sum E[X_i]=\mu,\qquad \operatorname{Var}(\bar X_n)=\frac1{n^2}\sum\operatorname{Var}(X_i)=\frac{n\sigma^2}{n^2}=\frac{\sigma^2}{n}.$$

- La moyenne d'échantillon est **centrée sur la vraie moyenne** $\mu$ (on dit qu'elle est **sans biais**).
- Sa dispersion vaut $\sigma/\sqrt n$, appelée **erreur-type** (*standard error*). Elle **diminue** quand $n$ augmente, mais seulement comme $1/\sqrt n$ : pour diviser l'erreur par 2, il faut **4 fois** plus de données ; par 10, il en faut 100 fois plus.

> 💡 **Pourquoi la variance se divise par $n$ ?** Quand on moyenne, les écarts positifs d'un client compensent partiellement les écarts négatifs d'un autre. L'aléa « se dilue » : c'est le même phénomène que la diversification vue en 2.3.3.

### 2.4.2 La loi des grands nombres

> 📐 **Énoncé (loi faible des grands nombres).** Si $X_1,X_2,\dots$ sont i.i.d. d'espérance $\mu$ et de variance finie, alors pour tout $\varepsilon>0$,
>
> $$P\bigl(|\bar X_n-\mu|\ge\varepsilon\bigr)\xrightarrow[n\to\infty]{}0.$$
>
> En mots : la probabilité que la moyenne observée s'écarte de $\mu$ de plus de $\varepsilon$ **tend vers 0**.

Voyons-le en action sur le taux de conversion de Dar Jasmin (vraie valeur $p=0{,}205$). Quatre « expériences » indépendantes observent les visiteurs un à un et notent la proportion d'acheteurs au fil du temps :

![À gauche : la proportion observée se stabilise sur la vraie valeur, quel que soit le départ. À droite : avec une loi de Cauchy, la moyenne ne converge jamais.](figures/ch02-lgn.png)

Au début, les courbes sont chaotiques (avec 3 visiteurs, la proportion vaut 0, 33 % ou 67 %…) ; puis elles s'**écrasent** autour de 0,205. C'est la loi des grands nombres.

> 📐 **Démonstration.** Elle repose sur une inégalité très utile.
>
> **Inégalité de Markov.** Pour une variable $Y\ge0$ et $a>0$ : $P(Y\ge a)\le E[Y]/a$.
> *Preuve.* $E[Y]\ge E[Y\cdot\mathbb 1_{Y\ge a}]\ge a\,P(Y\ge a)$. $\blacksquare$
>
> **Inégalité de Tchebychev.** On applique Markov à $Y=(X-\mu)^2$ avec $a=\varepsilon^2$ :
> $$P(|X-\mu|\ge\varepsilon)\le\frac{\operatorname{Var}(X)}{\varepsilon^2}.$$
>
> **Conclusion.** Appliquée à $\bar X_n$, dont la variance vaut $\sigma^2/n$ :
> $$P\bigl(|\bar X_n-\mu|\ge\varepsilon\bigr)\le\frac{\sigma^2}{n\,\varepsilon^2}\xrightarrow[n\to\infty]{}0.\ \blacksquare$$

La preuve donne même une information **quantitative** : la borne décroît comme $1/n$. Appliquons-la. Combien de visiteurs faut-il observer pour que la proportion mesurée soit à **±2 points** de la vérité avec une probabilité d'au moins 95 % ? Ici $\sigma^2=p(1-p)=0{,}163$ et $\varepsilon=0{,}02$ ; on veut $\dfrac{0{,}163}{n\times0{,}0004}\le0{,}05$.

```python
import numpy as np
from scipy import stats

p = 0.205
sigma2 = p * (1 - p)
eps = 0.02
n_tchebychev = sigma2 / (0.05 * eps**2)
print("variance d'un acheteur/non-acheteur :", round(sigma2, 4))
print("n garanti par Tchebychev            :", round(n_tchebychev))
```
<!--sortie-->
```text
variance d'un acheteur/non-acheteur : 0.163
n garanti par Tchebychev            : 8149
```

Tchebychev garantit le résultat à partir d'environ **8 150 visiteurs**. C'est une borne **sûre mais très pessimiste** (elle marche pour *n'importe quelle* loi). Le théorème central limite, ci-dessous, donnera beaucoup mieux.

> ⚠️ **L'erreur du joueur.** « La roulette est tombée 5 fois sur rouge, le noir est *dû*. » Faux : la loi des grands nombres ne dit **pas** que le hasard « compense » le passé. Chaque tirage est indépendant. Elle dit que la **proportion** se stabilise parce que les premiers tirages sont **dilués** dans une masse de tirages futurs, pas parce que le futur corrige le passé.

> 🧪 **Quand elle échoue : la loi de Cauchy.** Le graphique de droite montre la moyenne cumulée de tirages d'une loi de Cauchy, une loi aux queues si lourdes qu'elle **n'a pas d'espérance** : des valeurs gigantesques surviennent régulièrement et ruinent la moyenne. La moyenne ne se stabilise *jamais*. Moralité : les hypothèses d'un théorème comptent. Dans les données réelles (revenus, tailles de fichiers, populations de villes), les **valeurs extrêmes** peuvent rendre la moyenne instable ; on utilise alors la **médiane**, plus robuste.

### 2.4.3 Le théorème central limite

La loi des grands nombres dit *où* va la moyenne ; le **théorème central limite** (TCL) dit *comment elle fluctue autour*.

> 📐 **Énoncé.** Soient $X_1,\dots,X_n$ i.i.d. d'espérance $\mu$ et de variance $\sigma^2$ finie. Alors, quand $n$ est grand,
>
> $$\frac{\bar X_n-\mu}{\sigma/\sqrt n}\ \approx\ \mathcal N(0,1),\qquad\text{c'est-à-dire}\qquad \bar X_n\approx\mathcal N\!\Bigl(\mu,\ \frac{\sigma^2}n\Bigr).$$

La portée est stupéfiante : **quelle que soit la loi d'origine** (asymétrique, discrète, bizarre), la moyenne d'un grand nombre d'observations est **approximativement normale**. C'est la raison pour laquelle la courbe en cloche est partout : *beaucoup de phénomènes sont la somme de nombreux petits effets indépendants.*

**Voyons-le.** Partons de la loi exponentielle (très asymétrique, voir 2.2.5) et regardons la distribution de la moyenne de $n=1,2,10,50$ observations, sur 20 000 échantillons. La courbe orange est la loi normale prédite par le TCL.

![Distribution de la moyenne d'échantillon pour des tirages exponentiels. À n = 1 on voit la loi d'origine ; dès n = 10 la cloche apparaît ; à n = 50 elle est quasi parfaite. La courbe orange est la loi normale prédite par le TCL.](figures/ch02-tcl.png)

Le même résultat se mesure avec un seul chiffre, l'**asymétrie** (*skewness*) de la distribution, qui vaut 0 pour une cloche parfaite :

```python
rng = np.random.default_rng(4)
for n in (1, 2, 10, 50, 500):
    moyennes = rng.exponential(1.0, size=(20_000, n)).mean(axis=1)
    print(f"n = {n:>3} : moyenne = {moyennes.mean():.3f}   écart-type = {moyennes.std():.3f}"
          f"   (théorie 1/√n = {1 / np.sqrt(n):.3f})   asymétrie = {stats.skew(moyennes):+.2f}")
```
<!--sortie-->
```text
n =   1 : moyenne = 0.997   écart-type = 1.004   (théorie 1/√n = 1.000)   asymétrie = +2.02
n =   2 : moyenne = 1.005   écart-type = 0.706   (théorie 1/√n = 0.707)   asymétrie = +1.41
n =  10 : moyenne = 0.999   écart-type = 0.316   (théorie 1/√n = 0.316)   asymétrie = +0.59
n =  50 : moyenne = 1.000   écart-type = 0.141   (théorie 1/√n = 0.141)   asymétrie = +0.29
n = 500 : moyenne = 0.999   écart-type = 0.045   (théorie 1/√n = 0.045)   asymétrie = +0.12
```

On observe trois choses : la moyenne reste à 1 (sans biais) ; l'écart-type suit la loi $1/\sqrt n$ ; l'asymétrie s'efface (de 2 pour $n=1$ vers 0).

> 📐 **Idée de la preuve (esquisse).** On étudie la **fonction génératrice des moments** $M(t)=E[e^{tZ}]$ de la variable centrée réduite $Z_n=\sqrt n(\bar X_n-\mu)/\sigma$. Par indépendance, $M_{Z_n}(t)=\bigl[M(t/\sqrt n)\bigr]^n$ où $M$ est celle d'une variable centrée réduite. Un développement de Taylor donne $M(s)=1+\tfrac{s^2}2+o(s^2)$ (le terme en $s$ disparaît car l'espérance est nulle, et le coefficient de $s^2$ est $\operatorname{Var}/2=\tfrac12$). Donc $M_{Z_n}(t)=\bigl(1+\tfrac{t^2}{2n}+o(1/n)\bigr)^n\to e^{t^2/2}$, qui est précisément la fonction génératrice de $\mathcal N(0,1)$. Une démonstration complète, avec fonctions caractéristiques, relève de la ➕ théorie de la mesure (section 2.5).

### 2.4.4 Applications

**Application 1 : la probabilité sur une moyenne.** Les paniers de Dar Jasmin sont très asymétriques (beaucoup de petits achats, quelques gros) ; supposons-les exponentiels de moyenne 60 DT, donc d'écart-type 60 DT. Yasmine regarde les 40 prochains paniers. Quelle est la probabilité que leur **moyenne dépasse 70 DT** ?

Par le TCL, $\bar X_{40}\approx\mathcal N\bigl(60,\ 60^2/40\bigr)$, d'erreur-type $60/\sqrt{40}\approx9{,}49$. Le score $z$ est $(70-60)/9{,}49\approx1{,}05$, d'où $P\approx0{,}146$.

```python
mu, sigma, n = 60, 60, 40
se = sigma / np.sqrt(n)
approx_tcl = stats.norm(mu, se).sf(70)

rng = np.random.default_rng(5)
paniers = rng.exponential(60, size=(200_000, n))          # 200 000 échantillons de 40 paniers
simule = (paniers.mean(axis=1) > 70).mean()
print("erreur-type    :", round(se, 2))
print("P(moyenne > 70) par le TCL :", round(approx_tcl, 4))
print("P(moyenne > 70) simulée    :", round(simule, 4))
```
<!--sortie-->
```text
erreur-type    : 9.49
P(moyenne > 70) par le TCL : 0.1459
P(moyenne > 70) simulée    : 0.1477
```

Environ 15 % ; l'approximation normale est assez proche de la simulation (elle sous-estime très légèrement la queue de droite, à cause de l'asymétrie de la loi d'origine). Observez ce que le TCL a fait : **sans connaître la loi des paniers**, seulement leur moyenne et leur écart-type, on a répondu à une question de probabilité.

**Application 2 : de combien de visiteurs a-t-on besoin ?** Reprenons la question du 2.4.2 avec le TCL. La proportion observée $\hat p\approx\mathcal N\bigl(p,\ p(1-p)/n\bigr)$. Avec probabilité 95 %, $\hat p$ est à moins de $1{,}96$ erreurs-types de $p$ (le fameux 1,96 du 2.2.5). On veut donc

$$1{,}96\sqrt{\frac{p(1-p)}n}\le\varepsilon\iff n\ge\Bigl(\frac{1{,}96}{\varepsilon}\Bigr)^2p(1-p).$$

```python
n_tcl = (1.96 / eps) ** 2 * p * (1 - p)
print("n nécessaire par le TCL :", round(n_tcl))
print("n garanti par Tchebychev :", round(n_tchebychev))
```
<!--sortie-->
```text
n nécessaire par le TCL : 1565
n garanti par Tchebychev : 8149
```

Le TCL demande environ **1 565 visiteurs** au lieu de 8 150 : **5 fois moins**. Cette formule est celle des **tailles d'échantillon** des sondages et des tests A/B (chapitre 3).

> 🧪 **Vérifions par simulation** que 1 570 visiteurs (arrondi) suffisent bien à tenir la marge de ±2 points, dans environ 95 % des cas :

```python
rng = np.random.default_rng(6)
n_obs = 1570
taux = rng.binomial(n_obs, p, size=100_000) / n_obs
print("part des échantillons à moins de 2 points de la vérité :", round((np.abs(taux - p) <= eps).mean(), 4))
```
<!--sortie-->
```text
part des échantillons à moins de 2 points de la vérité : 0.9514
```

**Application 3 : la normale approche la binomiale.** Une binomiale est une somme de $n$ Bernoulli ; le TCL dit donc que pour $n$ grand, $\text{Bin}(n,p)\approx\mathcal N\bigl(np,\ np(1-p)\bigr)$. Sur 100 visiteurs à 20 % de conversion, quelle est la probabilité d'avoir **au moins 30 acheteurs** ?

```python
b = stats.binom(100, 0.2)
exact = b.sf(29)                                   # P(X >= 30) = P(X > 29)
approx = stats.norm(20, 4).sf(29.5)                # correction de continuité : on coupe à 29,5
print("exact (binomiale)     :", round(exact, 4))
print("approx. normale       :", round(approx, 4))
print("approx. sans correction:", round(stats.norm(20, 4).sf(30), 4))
```
<!--sortie-->
```text
exact (binomiale)     : 0.0112
approx. normale       : 0.0088
approx. sans correction: 0.0062
```

La **correction de continuité** (couper à 29,5 plutôt qu'à 30) améliore sensiblement l'approximation : on remplace des barres discrètes par une courbe continue, et la barre « 30 » occupe l'intervalle [29,5 ; 30,5].

### 2.4.5 Un mot de prudence

Le TCL est un résultat **asymptotique** : « $\approx$ » devient exact quand $n\to\infty$. À partir de quelle taille est-ce valable ? Cela dépend de la loi d'origine :

| Loi d'origine | $n$ suffisant (règle empirique) |
|---|---|
| symétrique (uniforme, normale) | quelques unités à 10 |
| modérément asymétrique (exponentielle) | une trentaine |
| très asymétrique, queues lourdes | des centaines, voire jamais (si la variance est infinie) |

> ✅ **À retenir (LGN et TCL).**
>
> - $\bar X_n$ est une variable aléatoire : $E[\bar X_n]=\mu$, $\operatorname{Var}(\bar X_n)=\sigma^2/n$, **erreur-type** $=\sigma/\sqrt n$. L'erreur diminue en $1/\sqrt n$ : quatre fois plus de données pour deux fois moins d'erreur.
> - **LGN** : $\bar X_n\to\mu$ (preuve par Tchebychev). Elle ne dit rien d'un « rattrapage » du hasard.
> - **TCL** : $\dfrac{\bar X_n-\mu}{\sigma/\sqrt n}\approx\mathcal N(0,1)$ pour *toute* loi de variance finie. C'est le pont entre les probabilités et la statistique.
> - Utilisations : probabilités sur des moyennes, taille d'échantillon $n\ge(1{,}96/\varepsilon)^2p(1-p)$, approximation normale de la binomiale.
> - Les hypothèses comptent : avec des queues très lourdes (Cauchy), rien de tout cela ne marche.


## 2.5 ➕ Pour aller plus loin : la théorie de la mesure (ce que « probabilité » veut vraiment dire)

> 🧭 **Section optionnelle**, plus abstraite. Elle n'est pas nécessaire pour la suite du livre. Elle répond à une question que se posent les lecteurs curieux : *« jusqu'ici, on a dit « une probabilité est un nombre entre 0 et 1 qui vérifie des règles », mais pour quels événements est-elle définie, et pourquoi ces règles ? »*

### 2.5.1 Le problème : on ne peut pas mesurer tous les ensembles

Pour un dé, tout est simple : $\Omega$ a six éléments et on peut attribuer une probabilité à **n'importe quelle** partie. Mais prenons une variable **uniforme sur $[0,1]$** : on voudrait que la probabilité d'un intervalle soit sa **longueur** ($P([a,b])=b-a$). Peut-on étendre cette idée à **tous** les sous-ensembles de $[0,1]$ en gardant des règles raisonnables (invariance par translation, additivité) ?

**Non.** En 1905, Giuseppe Vitali a construit des ensembles « pathologiques » auxquels aucune longueur cohérente ne peut être attribuée (la construction utilise l'axiome du choix). Ce n'est pas une curiosité : cela oblige à **limiter** les événements auxquels on attribue une probabilité.

### 2.5.2 Le cadre : un espace probabilisé $(\Omega,\mathcal F,P)$

La théorie moderne (Kolmogorov, 1933) est fondée sur trois objets.

- $\Omega$ : l'**univers** (toutes les issues).
- $\mathcal F$ : une **tribu** (ou σ-algèbre), c'est-à-dire la famille des événements **dont on sait parler**. Elle doit contenir $\Omega$, être stable par complémentaire et par **union dénombrable**. (Pour $[0,1]$, on prend la tribu **borélienne**, engendrée par les intervalles.)
- $P$ : une **mesure de probabilité** sur $\mathcal F$, avec $P(\Omega)=1$ et la **σ-additivité** : pour des événements $A_1,A_2,\dots$ deux à deux incompatibles,

$$P\Bigl(\bigcup_{i=1}^{\infty}A_i\Bigr)=\sum_{i=1}^{\infty}P(A_i).$$

Notez la différence avec l'axiome 3 du 2.1.1 : on demande l'additivité pour des unions **infinies dénombrables**, pas seulement finies. C'est elle qui rend possibles les passages à la limite (comme la loi des grands nombres).

> 💡 **Intuition.** La tribu est la liste des « questions autorisées » : « la variable tombe-t-elle entre 0,3 et 0,4 ? », « est-elle rationnelle ? », « est-elle dans l'union d'une suite d'intervalles ? ». La mesure $P$ répond à chacune par un nombre.

### 2.5.3 Une conséquence surprenante : événements de probabilité 0 qui arrivent

Soit $X$ uniforme sur $[0,1]$. Pour tout réel $x$, $P(X=x)=0$ (déjà vu en 2.2.1). Et pourtant $X$ prend bien *une* valeur. Un événement de probabilité nulle n'est donc **pas impossible**.

> 📐 **Les rationnels ont une probabilité nulle.** Les nombres rationnels de $[0,1]$ forment un ensemble **dénombrable** : $q_1,q_2,q_3,\dots$. Par σ-additivité,
>
> $$P(X\in\mathbb Q)=\sum_{i=1}^\infty P(X=q_i)=\sum_{i=1}^\infty 0=0.$$
>
> **Presque sûrement**, un nombre tiré au hasard dans $[0,1]$ est irrationnel ! (On dit qu'un événement est vrai **presque sûrement** (p.s.) quand sa probabilité vaut 1.)

### 2.5.4 L'espérance comme intégrale

En théorie de la mesure, une **variable aléatoire** est une fonction $X:\Omega\to\mathbb R$ **mesurable** (pour toute question « $X\le x$ ? », la réponse est un événement de la tribu). Son espérance est l'**intégrale de Lebesgue** :

$$E[X]=\int_\Omega X\,dP .$$

Cette seule définition recouvre les cas discret ($\sum$) et continu ($\int f$) du 2.3.1, mais aussi les cas **mixtes** que ni l'un ni l'autre ne gère. Voici un exemple pratique.

> 💡 **Un cas réel : les dépenses « à zéros ».** Un client visitant la boutique dépense **0 DT** avec une probabilité de 70 % (il regarde sans acheter) ; sinon sa dépense suit une loi exponentielle de moyenne 80 DT. Cette variable n'a **ni** fonction de masse (car elle prend un continuum de valeurs) **ni** densité (car elle a un « atome » en 0 : $P(X=0)=0{,}7>0$). C'est une loi **mixte**. Mais son espérance se calcule sans difficulté : on décompose selon le cas.

$$E[X]=0{,}7\times0+0{,}3\times80=24\ \text{DT}.$$

```python
import numpy as np
rng = np.random.default_rng(31)
n = 500_000
achete = rng.random(n) < 0.3
depense = np.where(achete, rng.exponential(80, size=n), 0.0)

print("P(X = 0) simulée :", round((depense == 0).mean(), 4))
print("E[X] simulée      :", round(depense.mean(), 2), "(théorie : 24)")
print("médiane           :", round(np.median(depense), 2), "(70 % des clients ne dépensent rien)")
```
<!--sortie-->
```text
P(X = 0) simulée : 0.6998
E[X] simulée      : 24.03 (théorie : 24)
médiane           : 0.0 (70 % des clients ne dépensent rien)
```

Les données réelles de commerce sont très souvent de ce type (« zero-inflated »), et c'est la raison pour laquelle on ne peut pas toujours plaquer une loi normale ou exponentielle sans réfléchir.

> ⚠️ **Un conseil pratique.** Pour une loi mixte, la moyenne (24) et la médiane (0) racontent des histoires totalement différentes. Résumer par un seul nombre est trompeur ; il faut présenter la part de zéros et la moyenne conditionnelle aux achats.

### 2.5.5 Les modes de convergence

Quand on dit « $\bar X_n$ converge vers $\mu$ », encore faut-il dire **en quel sens**. Pour des variables aléatoires, il existe plusieurs façons, de la plus forte à la plus faible :

| Mode | Notation | Signification | Exemple |
|---|---|---|---|
| **Presque sûre** | $X_n\xrightarrow{p.s.}X$ | pour (presque) chaque « histoire » $\omega$, la suite de nombres $X_n(\omega)$ converge au sens usuel | **loi forte** des grands nombres |
| **En probabilité** | $X_n\xrightarrow{P}X$ | $P(\lvert X_n-X\rvert>\varepsilon)\to0$ | **loi faible** (démontrée en 2.4.2) |
| **En loi** | $X_n\xrightarrow{\mathcal L}X$ | les fonctions de répartition convergent | **TCL** |

On a : p.s. ⟹ en probabilité ⟹ en loi (et jamais l'inverse en général). La **loi forte** des grands nombres, plus difficile à démontrer, affirme que, pour *presque* chaque suite d'observations, la moyenne cumulée converge. C'est ce que montre chacune des courbes de la figure de la section 2.4.2 : chaque trajectoire se stabilise.

> 💡 **Pourquoi se soucier de cela ?** Pour un praticien, la différence compte surtout dans la formulation des garanties : « avec une probabilité 95 %, mon estimation est à ±2 points » est un énoncé **en probabilité/en loi** sur *un* échantillon ; « mon estimateur finira par donner la bonne valeur » est un énoncé **presque sûr** sur une suite infinie de données.

### 2.5.6 La densité comme dérivée d'une mesure

Quand dit-on qu'une variable « a une densité » ? Réponse : quand sa loi $P_X$ est **absolument continue** par rapport à la mesure de Lebesgue (la « longueur »), c'est-à-dire que tout ensemble de longueur nulle a probabilité nulle. Le **théorème de Radon–Nikodym** garantit alors l'existence d'une densité $f$ telle que $P_X(A)=\int_Af(x)\,dx$. Dans l'exemple des dépenses à zéros, $P_X(\{0\})=0{,}7$ alors que $\{0\}$ est de longueur nulle : pas de densité, ce que nous avions remarqué.

> ✅ **À retenir (théorie de la mesure).**
>
> - On ne peut pas assigner de probabilité à *tous* les sous-ensembles : on se limite à une **tribu** $\mathcal F$.
> - Un espace probabilisé est $(\Omega,\mathcal F,P)$ avec $P$ **σ-additive**.
> - Un événement de probabilité 0 n'est pas impossible ; « presque sûrement » = avec probabilité 1.
> - Espérance = intégrale de Lebesgue ; elle gère les lois mixtes (atome + densité).
> - Trois convergences : presque sûre ⟹ en probabilité ⟹ en loi (LGN forte, LGN faible, TCL).


## 2.6 ➕ Pour aller plus loin : les processus stochastiques

> 🧭 **Section optionnelle.** Jusqu'ici, une variable aléatoire était un nombre tiré **une fois**. Un **processus stochastique** est une variable aléatoire qui **évolue dans le temps** : $X_0,X_1,X_2,\dots$ Les stocks, les clients actifs, le cours d'une action, le nombre d'appels : tout cela est une suite de variables aléatoires dépendantes les unes des autres.

### 2.6.1 La marche aléatoire

> 💡 **Intuition.** Chaque jour, le stock d'un produit varie de +1 ou −1 de façon aléatoire. Où sera-t-il après 100 jours ?

On part de $S_0=0$ et on pose $S_n=S_{n-1}+\xi_n$ où chaque pas $\xi_n$ vaut $+1$ ou $-1$ avec probabilité $\tfrac12$. Comme $E[\xi_n]=0$ et $\operatorname{Var}(\xi_n)=1$, les propriétés du 2.3 (somme de variables indépendantes) donnent

$$E[S_n]=0,\qquad\operatorname{Var}(S_n)=n,\qquad\sigma(S_n)=\sqrt n.$$

Une marche aléatoire n'a donc **pas de tendance**, mais elle s'écarte de 0 de l'ordre de $\sqrt n$. Après 100 pas, on s'attend à être à environ 10 de l'origine, pas à 100 ! C'est la même loi en $\sqrt n$ que celle de l'erreur-type.

```python
import numpy as np
rng = np.random.default_rng(14)

pas = rng.choice([-1, 1], size=(20_000, 100))           # 20 000 marches de 100 pas
position_finale = pas.sum(axis=1)
print("moyenne des positions finales :", round(position_finale.mean(), 3))
print("écart-type des positions      :", round(position_finale.std(), 3), "(théorie : √100 = 10)")
print("P(|S_100| <= 10)              :", round((np.abs(position_finale) <= 10).mean(), 3))
```
<!--sortie-->
```text
moyenne des positions finales : 0.082
écart-type des positions      : 10.076 (théorie : √100 = 10)
P(|S_100| <= 10)              : 0.723
```

Par le TCL, $S_n/\sqrt n\approx\mathcal N(0,1)$ : environ 68 % des marches finissent à moins de $\sqrt n$ de l'origine (ici, 72 % : un peu plus que 68 %, car la borne $\pm10$ est incluse et la marche ne prend que des valeurs paires).

> 🧪 **La marche aléatoire est partout.** Le cours d'une action est souvent modélisé comme une marche aléatoire (le **mouvement brownien**, limite continue de la marche quand les pas deviennent infiniment petits). Elle explique aussi pourquoi les prévisions à long terme sont si incertaines : l'incertitude grandit en $\sqrt{\text{temps}}$.

### 2.6.2 Les chaînes de Markov : le futur ne dépend que du présent

> 💡 **Intuition.** Dans une **chaîne de Markov**, la probabilité de passer à l'état suivant ne dépend que de l'**état actuel**, pas de la manière dont on y est arrivé :
>
> $$P(X_{n+1}=j\mid X_n=i,\ X_{n-1},\dots,X_0)=P(X_{n+1}=j\mid X_n=i)=P_{ij}.$$

Yasmine classe chaque mois ses clients en trois états : **Actif** (A : au moins 2 achats ce mois), **Occasionnel** (O : 1 achat) et **Inactif** (I : aucun achat). Elle a estimé les transitions d'un mois au suivant :

| de ↓ / vers → | Actif | Occasionnel | Inactif |
|---|---:|---:|---:|
| **Actif** | 0,80 | 0,15 | 0,05 |
| **Occasionnel** | 0,30 | 0,50 | 0,20 |
| **Inactif** | 0,10 | 0,20 | 0,70 |

On range ces nombres dans la **matrice de transition** $\mathbf{P}$ : chaque **ligne** est une loi de probabilité (somme égale à 1).

```python
P = np.array([[0.80, 0.15, 0.05],
              [0.30, 0.50, 0.20],
              [0.10, 0.20, 0.70]])
etats = ["Actif", "Occasionnel", "Inactif"]
print("somme des lignes :", P.sum(axis=1))
```
<!--sortie-->
```text
somme des lignes : [1. 1. 1.]
```

**Où sera un client dans 2 mois ?** Un client Actif aujourd'hui peut être Actif dans 2 mois de plusieurs façons : A→A→A, A→O→A, A→I→A. La probabilité totale est $0{,}8\times0{,}8+0{,}15\times0{,}3+0{,}05\times0{,}1=0{,}64+0{,}045+0{,}005=0{,}69$. Mais c'est **exactement** le produit matriciel de la ligne A par la colonne A de $\mathbf{P}$ ! En général :

> 📐 **Les probabilités de transition en $n$ pas sont les éléments de $\mathbf{P}^n$.** (Même mécanisme que pour compter les chemins d'un graphe au 1.6.3 : la formule des probabilités totales fait apparaître le produit matriciel.)

```python
P2 = np.linalg.matrix_power(P, 2)
print("P^2 :\n", P2.round(3))
print("P(Actif -> Actif en 2 mois) =", P2[0, 0].round(3))
```
<!--sortie-->
```text
P^2 :
 [[0.69  0.205 0.105]
 [0.41  0.335 0.255]
 [0.21  0.255 0.535]]
P(Actif -> Actif en 2 mois) = 0.69
```

**Et dans 12 mois, ou 2 ans ?** On calcule des puissances plus élevées :

```python
for n in (1, 3, 6, 12, 24):
    Pn = np.linalg.matrix_power(P, n)
    print(f"n = {n:>2} mois : ligne 'Actif' = {Pn[0].round(4)}   ligne 'Inactif' = {Pn[2].round(4)}")
```
<!--sortie-->
```text
n =  1 mois : ligne 'Actif' = [0.8  0.15 0.05]   ligne 'Inactif' = [0.1 0.2 0.7]
n =  3 mois : ligne 'Actif' = [0.624 0.227 0.149]   ligne 'Inactif' = [0.298 0.266 0.436]
n =  6 mois : ligne 'Actif' = [0.5368 0.2448 0.2183]   ligne 'Inactif' = [0.4366 0.2581 0.3053]
n = 12 mois : ligne 'Actif' = [0.5034 0.2495 0.247 ]   ligne 'Inactif' = [0.4941 0.2508 0.2551]
n = 24 mois : ligne 'Actif' = [0.5  0.25 0.25]   ligne 'Inactif' = [0.4999 0.25   0.25  ]
```

Observez : à mesure que $n$ grandit, **toutes les lignes deviennent identiques**. Le système « oublie » son point de départ : qu'un client ait commencé Actif ou Inactif, sa probabilité d'être dans chaque état dans 2 ans est la même. Cette loi limite $\boldsymbol\pi$ s'appelle la **distribution stationnaire**.

**La calculer exactement : valeurs propres, encore !** La loi stationnaire vérifie $\boldsymbol\pi\mathbf{P}=\boldsymbol\pi$ : elle ne change plus après une transition. En transposant, $\mathbf{P}^\top\boldsymbol\pi^\top=\boldsymbol\pi^\top$ : c'est un **vecteur propre de $\mathbf{P}^\top$ pour la valeur propre 1** (section 1.1.3).

```python
valeurs, vecteurs = np.linalg.eig(P.T)
k = np.argmin(np.abs(valeurs - 1))                 # la valeur propre égale à 1
pi = np.real(vecteurs[:, k])
pi = pi / pi.sum()                                 # normaliser pour que la somme soit 1
for e, v in zip(etats, pi):
    print(f"{e:<12} {v:.4f}")
print("valeurs propres de P :", np.round(np.real(valeurs), 3))
```
<!--sortie-->
```text
Actif        0.5000
Occasionnel  0.2500
Inactif      0.2500
valeurs propres de P : [1.    0.673 0.327]
```

À long terme, exactement **50 %** des clients sont Actifs, **25 %** Occasionnels et **25 %** Inactifs. Les deux autres valeurs propres (0,673 et 0,327, de module < 1) pilotent la **vitesse** de convergence : plus elles sont petites, plus vite le système oublie son passé.

**Une application économique : la valeur à long terme d'un client.** Supposons qu'un client Actif rapporte en moyenne 30 DT par mois, un Occasionnel 10 DT, un Inactif 0 DT. À long terme, le revenu moyen mensuel par client est $\boldsymbol\pi\cdot\mathbf{v}$ :

```python
v = np.array([30, 10, 0])
print("revenu mensuel moyen par client (long terme) :", round(pi @ v, 2), "DT")
```
<!--sortie-->
```text
revenu mensuel moyen par client (long terme) : 17.5 DT
```

Soit 17,5 DT par client et par mois. Cette quantité permet à Yasmine de **chiffrer** l'effet d'une campagne : si une relance fait passer la probabilité Inactif→Actif de 0,10 à 0,20, quel est le gain ? Il suffit de modifier $\mathbf{P}$ et de recalculer $\boldsymbol\pi$.

```python
def revenu_long_terme(P, v):
    valeurs, vecteurs = np.linalg.eig(P.T)
    pi = np.real(vecteurs[:, np.argmin(np.abs(valeurs - 1))])
    pi = pi / pi.sum()
    return pi @ v

P_relance = np.array([[0.80, 0.15, 0.05],
                      [0.30, 0.50, 0.20],
                      [0.20, 0.20, 0.60]])           # Inactif -> Actif passe de 0,10 à 0,20
print("avant relance :", round(revenu_long_terme(P, v), 2), "DT")
print("après relance :", round(revenu_long_terme(P_relance, v), 2), "DT")
```
<!--sortie-->
```text
avant relance : 17.5 DT
après relance : 19.3 DT
```

La relance fait gagner environ 1,8 DT par client et par mois, soit +10 %. Avec 2 000 clients, cela représente environ 3 600 DT par mois, de quoi décider si la relance vaut son coût. C'est un modèle simple, mais l'idée (états, transitions, régime permanent) est utilisée en analyse de la fidélité, en marketing, et à la base de l'algorithme PageRank de Google (le web est une chaîne de Markov dont les états sont les pages).

### 2.6.3 Le processus de Poisson : des arrivées au hasard

Un **processus de Poisson** de cadence $\lambda$ modélise des événements arrivant au hasard et indépendamment : appels, commandes, pannes. Il a deux visages **équivalents**, que nous avons déjà croisés :

- le **nombre** d'événements dans une durée $t$ suit une loi de **Poisson**$(\lambda t)$ (2.2.4) ;
- les **temps d'attente** entre événements successifs sont **exponentiels**$(\lambda)$, indépendants (2.2.5).

Vérifions que ces deux visages coïncident, en construisant le processus par ses temps d'attente puis en comptant :

```python
from scipy import stats
rng = np.random.default_rng(15)
lam = 3                                               # 3 commandes par heure
n_heures = 50_000

comptes = np.empty(n_heures, dtype=int)
for h in range(n_heures):
    t, k = 0.0, 0
    while True:
        t += rng.exponential(1 / lam)                 # temps d'attente jusqu'à la prochaine commande
        if t > 1.0:                                   # on sort de l'heure
            break
        k += 1
    comptes[h] = k

print("moyenne des comptes   :", round(comptes.mean(), 3), "(théorie 3)")
print("variance des comptes  :", round(comptes.var(), 3), "(théorie 3)")
for k in range(0, 7):
    print(f"P(N = {k}) : simulée = {(comptes == k).mean():.4f}   Poisson(3) = {stats.poisson(3).pmf(k):.4f}")
```
<!--sortie-->
```text
moyenne des comptes   : 3.005 (théorie 3)
variance des comptes  : 2.98 (théorie 3)
P(N = 0) : simulée = 0.0492   Poisson(3) = 0.0498
P(N = 1) : simulée = 0.1491   Poisson(3) = 0.1494
P(N = 2) : simulée = 0.2228   Poisson(3) = 0.2240
P(N = 3) : simulée = 0.2241   Poisson(3) = 0.2240
P(N = 4) : simulée = 0.1687   Poisson(3) = 0.1680
P(N = 5) : simulée = 0.1023   Poisson(3) = 0.1008
P(N = 6) : simulée = 0.0511   Poisson(3) = 0.0504
```

Les fréquences simulées (obtenues **uniquement** avec des temps d'attente exponentiels) correspondent à la loi de Poisson : les deux descriptions sont bien le même objet. C'est pourquoi les files d'attente (guichets, serveurs, centres d'appels) se modélisent presque toujours avec ce processus.

> ✅ **À retenir (processus stochastiques).**
>
> - Un processus stochastique est une famille $(X_t)$ de variables aléatoires indexée par le temps.
> - **Marche aléatoire** : $E[S_n]=0$, $\sigma(S_n)=\sqrt n$ ; l'incertitude croît en $\sqrt{\text{temps}}$.
> - **Chaîne de Markov** : le futur ne dépend que du présent ; probabilités en $n$ pas $=\mathbf{P}^n$ ; **loi stationnaire** = vecteur propre de $\mathbf{P}^\top$ pour la valeur propre 1.
> - **Processus de Poisson** : nombres de Poisson ⇔ temps d'attente exponentiels.


## 2.7 Exercices du chapitre 2

> 🧭 Même mode d'emploi qu'au chapitre 1 : cherchez d'abord, comparez ensuite. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse.

### Énoncés

**Exercice 1 ⭐ (union).** Pour une newsletter : $P(\text{ouvre})=0{,}35$, $P(\text{clique})=0{,}25$, $P(\text{ouvre et clique})=0{,}10$. Quelle est la probabilité qu'un destinataire fasse **au moins une** des deux actions ? Qu'il ne fasse **aucune** ?

**Exercice 2 ⭐⭐ (Bayes).** Dans l'atelier d'un fournisseur, 2 % des bols sont défectueux. Un contrôle automatique signale 90 % des bols défectueux, mais aussi 4 % des bols corrects. Un bol est signalé : quelle est la probabilité qu'il soit réellement défectueux ? Interprétez.

**Exercice 3 ⭐ (« au moins un »).** Chaque colis a 2 % de chances d'être endommagé, indépendamment des autres. (a) Probabilité qu'au moins un colis soit endommagé parmi 50 ? (b) Combien de colis faut-il pour que cette probabilité dépasse 90 % ?

**Exercice 4 ⭐ (binomiale).** Sur 15 visiteurs d'une publicité, chacun achète avec la probabilité 0,3. Calculez $P(X=5)$, l'espérance et l'écart-type de $X$, et $P(X\ge8)$.

**Exercice 5 ⭐⭐ (Poisson et exponentielle).** Le service client reçoit en moyenne 4 appels par heure (processus de Poisson). (a) Probabilité de ne recevoir **aucun** appel pendant une demi-heure ? (b) Le temps d'attente entre deux appels est exponentiel : quelle est sa moyenne, et quelle est la probabilité d'attendre plus de 20 minutes ? (c) On a déjà attendu 10 minutes sans appel : quelle est la probabilité d'attendre **encore** 20 minutes ?

**Exercice 6 ⭐⭐ (normale).** Le poids des colis expédiés suit $\mathcal N(500\text{ g},\ 40^2)$. (a) Probabilité qu'un colis pèse moins de 450 g ? (b) Entre 460 et 540 g ? (c) Quel poids n'est dépassé que par 1 % des colis ?

**Exercice 7 ⭐⭐ (espérance et variance).** Un jeu de fidélité distribue : 0 DT avec la probabilité 0,80 ; 10 DT avec 0,15 ; 50 DT avec 0,05. Calculez l'espérance, la variance et l'écart-type du gain. Si participer coûte 5 DT, le jeu est-il favorable au client ? Et si le client joue 100 fois, quelle est l'espérance et l'écart-type de son gain total ?

**Exercice 8 ⭐⭐ (covariance).** Cinq clients ont noté le délai de livraison ($x=1,2,3,4,5$ jours) et leur satisfaction ($y=2,4,5,4,5$ sur 5). Calculez à la main la covariance (divisée par $n$), la variance de chaque variable et la corrélation. Vérifiez avec NumPy.

**Exercice 9 ⭐⭐⭐ (TCL).** Le panier d'un client a une moyenne de 45 DT et un écart-type de 30 DT (loi très asymétrique). On observe 100 clients. (a) Quelle est la loi approchée de la moyenne ? (b) Probabilité que la moyenne dépasse 50 DT ? (c) Combien de clients faut-il observer pour que l'erreur-type de la moyenne soit inférieure à 1 DT ? (d) Vérifiez (b) par simulation. Attention : une loi exponentielle de moyenne 45 a un écart-type de 45, pas 30 ; quelle loi asymétrique de moyenne 45 et d'écart-type 30 peut-on utiliser à la place ?

**Exercice 10 ⭐⭐⭐ (Markov).** Chaque jour, une machine est **en marche** (M) ou **en panne** (P). Si elle est en marche, elle tombe en panne le lendemain avec probabilité 0,1. Si elle est en panne, elle est réparée le lendemain avec probabilité 0,4. (a) Écrivez la matrice de transition. (b) Si elle est en marche aujourd'hui, quelle est la probabilité qu'elle le soit après-demain ? (c) Quelle est la proportion de temps passée en panne à long terme ?

### Corrigés

**Corrigé 1.** $P(\text{au moins une})=0{,}35+0{,}25-0{,}10=0{,}50$. Aucune : $1-0{,}50=0{,}50$. (On retranche l'intersection pour ne pas la compter deux fois ; le complémentaire de « au moins une » est « aucune ».)

**Corrigé 2.** Sur 10 000 bols : 200 défectueux, dont 180 signalés ; 9 800 corrects, dont 392 signalés à tort. Total des signalements : 572, dont 180 justifiés : $180/572\approx0{,}315$.

```python
p_def, sens, fausse = 0.02, 0.90, 0.04
p_signal = sens * p_def + fausse * (1 - p_def)
print("P(défectueux | signalé) =", round(sens * p_def / p_signal, 4))
```
<!--sortie-->
```text
P(défectueux | signalé) = 0.3147
```

Seulement **31,5 %** : même avec un bon contrôle, **deux bols signalés sur trois sont corrects**, car les défauts sont rares (erreur du taux de base). Ils justifient une seconde vérification plutôt qu'un rejet automatique.

**Corrigé 3.** (a) $1-0{,}98^{50}\approx0{,}636$. (b) On veut $1-0{,}98^n>0{,}9\iff0{,}98^n<0{,}1\iff n>\dfrac{\ln0{,}1}{\ln0{,}98}\approx113{,}97$, donc **114 colis**.

```python
import numpy as np
from scipy import stats
print("(a)", round(1 - 0.98**50, 4))
print("(b)", np.log(0.1) / np.log(0.98), "-> n =", int(np.ceil(np.log(0.1) / np.log(0.98))))
```
<!--sortie-->
```text
(a) 0.6358
(b) 113.97408559184939 -> n = 114
```

**Corrigé 4.** $P(X=5)=\binom{15}5\,0{,}3^5\,0{,}7^{10}$. $E[X]=np=4{,}5$ ; $\sigma=\sqrt{np(1-p)}=\sqrt{3{,}15}\approx1{,}775$ ; $P(X\ge8)=1-P(X\le7)$.

```python
X = stats.binom(15, 0.3)
print("P(X=5)  =", round(X.pmf(5), 4))
print("E, sigma=", X.mean(), round(X.std(), 3))
print("P(X>=8) =", round(X.sf(7), 4))
```
<!--sortie-->
```text
P(X=5)  = 0.2061
E, sigma= 4.5 1.775
P(X>=8) = 0.05
```

**Corrigé 5.** (a) Sur une demi-heure, $N\sim\text{Poisson}(4\times0{,}5=2)$ : $P(N=0)=e^{-2}\approx0{,}135$. (b) Le temps d'attente est $\text{Exp}(4/\text{h})$, de moyenne $1/4$ h $=15$ min. 20 min $=1/3$ h : $P(T>1/3)=e^{-4/3}\approx0{,}264$. (c) Par absence de mémoire, c'est la même probabilité : **0,264**.

```python
print("(a)", round(np.exp(-2), 4), round(stats.poisson(2).pmf(0), 4))
T = stats.expon(scale=1 / 4)               # unité : heure
print("(b)", round(T.sf(1 / 3), 4))
print("(c)", round(T.sf(10 / 60 + 1 / 3) / T.sf(10 / 60), 4))
```
<!--sortie-->
```text
(a) 0.1353 0.1353
(b) 0.2636
(c) 0.2636
```

**Corrigé 6.** (a) $z=(450-500)/40=-1{,}25$, $P=\Phi(-1{,}25)\approx0{,}106$. (b) $z$ de $-1$ à $+1$ : $\approx0{,}683$. (c) $z_{0{,}99}\approx2{,}326$, donc $500+2{,}326\times40\approx593$ g.

```python
W = stats.norm(500, 40)
print("(a)", round(W.cdf(450), 4))
print("(b)", round(W.cdf(540) - W.cdf(460), 4))
print("(c)", round(W.ppf(0.99), 1))
```
<!--sortie-->
```text
(a) 0.1056
(b) 0.6827
(c) 593.1
```

**Corrigé 7.** $E=0{,}15\times10+0{,}05\times50=1{,}5+2{,}5=4$ DT. $E[X^2]=0{,}15\times100+0{,}05\times2500=15+125=140$, $\operatorname{Var}=140-16=124$, $\sigma\approx11{,}1$ DT. À 5 DT la partie, l'espérance du **gain net** est $4-5=-1$ DT : défavorable en moyenne (c'est favorable à la boutique). Sur 100 parties (indépendantes) : espérance $100\times4=400$ DT, variance $100\times124=12\,400$, écart-type $\sqrt{12400}\approx111$ DT. Remarquez que l'écart-type relatif diminue : 111/400 = 28 % contre 11,1/4 = 278 % pour une seule partie.

```python
gains = np.array([0, 10, 50]); probas = np.array([0.8, 0.15, 0.05])
E = (gains * probas).sum(); V = (gains**2 * probas).sum() - E**2
print("E =", E, " Var =", round(V, 2), " sigma =", round(np.sqrt(V), 2))
print("100 parties : E =", 100 * E, " sigma =", round(np.sqrt(100 * V), 1))
```
<!--sortie-->
```text
E = 4.0  Var = 124.0  sigma = 11.14
100 parties : E = 400.0  sigma = 111.4
```

**Corrigé 8.** Moyennes $\bar x=3$, $\bar y=4$. Écarts : $x-\bar x=(-2,-1,0,1,2)$, $y-\bar y=(-2,0,1,0,1)$. Produits : $4,0,0,0,2$, de somme 6, donc $\operatorname{Cov}=6/5=1{,}2$. $\operatorname{Var}(x)=(4+1+0+1+4)/5=2$ ; $\operatorname{Var}(y)=(4+0+1+0+1)/5=1{,}2$. $\rho=\dfrac{1{,}2}{\sqrt{2\times1{,}2}}=\dfrac{1{,}2}{1{,}549}\approx0{,}775$. Lecture : la corrélation est *positive* : plus la livraison est lente, plus la satisfaction serait élevée ? Ce n'est pas plausible : avec seulement cinq points, c'est probablement un hasard de l'échantillon. Nous verrons au chapitre 3 comment tester si une corrélation observée est significative.

```python
x = np.array([1, 2, 3, 4, 5.0]); y = np.array([2, 4, 5, 4, 5.0])
print("cov =", ((x - x.mean()) * (y - y.mean())).mean(), "  var x, y =", x.var(), y.var())
print("rho =", round(np.corrcoef(x, y)[0, 1], 4))
```
<!--sortie-->
```text
cov = 1.2   var x, y = 2.0 1.2
rho = 0.7746
```

**Corrigé 9.** (a) Par le TCL, $\bar X_{100}\approx\mathcal N(45,\ 30^2/100)=\mathcal N(45,\ 3^2)$ : erreur-type 3 DT. (b) $z=(50-45)/3\approx1{,}667$, $P(\bar X>50)\approx0{,}048$. (c) $\sigma/\sqrt n<1\iff n>900$. (d) Pour la simulation, une exponentielle de moyenne 45 a un écart-type de **45** (pas 30) : elle ne convient pas. On utilise une loi Gamma de moyenne 45 et d'écart-type 30 (forme $k=(45/30)^2=2{,}25$, échelle $\theta=30^2/45=20$). La simulation donne 5,1 % contre 4,8 % par le TCL : l'écart vient de l'asymétrie résiduelle à $n=100$.

```python
print("(b) TCL :", round(stats.norm(45, 3).sf(50), 4))
rng = np.random.default_rng(9)
echantillons = rng.gamma(shape=2.25, scale=20, size=(100_000, 100))
print("moyenne, écart-type du panier simulé :", echantillons.mean().round(2), echantillons.std().round(2))
print("(b) simulée :", round((echantillons.mean(axis=1) > 50).mean(), 4))
print("(c) n minimal :", (30 / 1) ** 2)
```
<!--sortie-->
```text
(b) TCL : 0.0478
moyenne, écart-type du panier simulé : 45.01 30.0
(b) simulée : 0.0512
(c) n minimal : 900.0
```

**Corrigé 10.** (a) $\mathbf{P}=\begin{pmatrix}0{,}9&0{,}1\\0{,}4&0{,}6\end{pmatrix}$ (lignes M, P). (b) $\mathbf{P}^2_{MM}=0{,}9\times0{,}9+0{,}1\times0{,}4=0{,}85$. (c) On cherche $\boldsymbol\pi=(\pi_M,\pi_P)$ avec $\boldsymbol\pi\mathbf P=\boldsymbol\pi$ : de la seconde colonne, $0{,}1\pi_M+0{,}6\pi_P=\pi_P$, soit $0{,}1\pi_M=0{,}4\pi_P$, donc $\pi_M=4\pi_P$ ; avec $\pi_M+\pi_P=1$ : $\pi_P=0{,}2$. La machine est en panne **20 % du temps** à long terme.

```python
P = np.array([[0.9, 0.1], [0.4, 0.6]])
print("P^2[M,M] =", np.linalg.matrix_power(P, 2)[0, 0])
w, V = np.linalg.eig(P.T)
pi = np.real(V[:, np.argmin(np.abs(w - 1))]); pi /= pi.sum()
print("loi stationnaire :", pi.round(3))
```
<!--sortie-->
```text
P^2[M,M] = 0.8500000000000001
loi stationnaire : [0.8 0.2]
```

---

## Bilan du chapitre 2

Vous savez maintenant :

- **calculer** des probabilités (complémentaire, union, conditionnel) et **inverser** un conditionnement avec Bayes, en vous méfiant de l'erreur du taux de base ;
- **modéliser** un phénomène par la bonne loi (Bernoulli, binomiale, Poisson, exponentielle, normale) et calculer des probabilités avec `scipy.stats` ;
- **résumer** une loi par son espérance et sa variance, et mesurer le lien entre deux variables par la covariance et la corrélation ;
- **comprendre** pourquoi une moyenne devient fiable (LGN) et pourquoi son erreur est normale (TCL), avec une erreur-type en $\sigma/\sqrt n$ ;
- (en option) **situer** tout cela dans le cadre de la théorie de la mesure et des processus stochastiques.

Le chapitre 3 retourne le problème : on ne **connaît** plus la loi, on a seulement des **données**, et il faut en déduire la loi. C'est la statistique.


---

# Chapitre 3 : Statistique

> « Les probabilités vont de la **cause** vers les **données**.
> La statistique fait le chemin inverse : des **données** vers la cause. »

Au chapitre 2, nous *connaissions* la loi (par exemple « le taux de conversion est 20,5 % ») et nous calculions la probabilité d'observer certaines données. Dans la vie réelle, c'est l'inverse : on **observe** des données (400 commandes) et on veut deviner la loi (« quel est le vrai panier moyen ? Le canal Instagram est-il vraiment moins rentable que la boutique ? »). C'est le travail de la **statistique**.

## Le chemin de ce chapitre

- **3.1 Statistique descriptive** : résumer et regarder les données (moyenne, médiane, quantiles, graphiques) avant toute chose.
- **3.2 Estimation** : déduire un paramètre inconnu d'un échantillon (méthode des moments, maximum de vraisemblance), et juger la qualité d'un estimateur.
- **3.3 Intervalles de confiance** : ne pas donner un seul chiffre, mais une **fourchette** honnête.
- **3.4 Tests d'hypothèses** : décider, avec un risque maîtrisé, si un effet observé est réel ou dû au hasard (tests de moyenne, de proportion, du khi-deux, A/B).
- **3.5 p-valeurs, puissance et tests multiples** : bien interpréter les résultats, dimensionner une expérience, éviter les faux positifs.
- ➕ **Pour aller plus loin** : les sondages (comment échantillonner), et les méthodes non paramétriques (quand on ne veut pas supposer de loi).
- **3.8 Exercices corrigés**.

> 💡 **Le fil conducteur : un jeu de 400 commandes.** Tout au long du chapitre nous travaillons sur un même tableau de 400 commandes de Dar Jasmin (canal, montant, délai de livraison, satisfaction). Il est **simulé** (graine fixe) pour que vous puissiez reproduire chaque calcul, et vous verrez qu'on y retrouve des phénomènes tout à fait réalistes : montants asymétriques, différences entre canaux, lien entre délai et satisfaction.

> 🛠️ **Outils.** Nous utilisons `pandas` pour les tableaux (étudié en détail à la section 4.4 : ici on n'utilise que les gestes de base, expliqués au passage) et `scipy.stats` pour les calculs statistiques.


## 3.1 Statistique descriptive

> 💡 **Intuition.** Avant de modéliser, de tester ou de prédire quoi que ce soit, on **regarde** les données. La statistique descriptive, c'est l'art de résumer un tableau de centaines de lignes en quelques nombres et quelques graphiques *fidèles*. C'est aussi la meilleure façon de repérer des erreurs de saisie, des valeurs aberrantes et des surprises, **avant** qu'elles ne faussent une analyse.

### 3.1.1 Population, échantillon, variables

Deux mots que nous utiliserons constamment :

- La **population** est l'ensemble complet qui nous intéresse (*toutes* les commandes passées et à venir de Dar Jasmin).
- L'**échantillon** est la partie que l'on a effectivement observée (nos 400 commandes).

On calcule des **statistiques** sur l'échantillon pour apprendre des choses sur les **paramètres** de la population, qui eux restent inconnus. (On notera $\bar x$ la moyenne de l'échantillon et $\mu$ celle de la population.)

Chaque colonne d'un tableau est une **variable**. Son type décide des calculs et des graphiques qui ont un sens :

| Type | Exemple | Résumés adaptés |
|---|---|---|
| **Quantitative continue** | montant (DT) | moyenne, médiane, écart-type, histogramme |
| **Quantitative discrète** | nombre d'articles, délai en jours | idem, ou fréquences de chaque valeur |
| **Qualitative nominale** | canal (Instagram / Site / Boutique) | effectifs, proportions, diagramme en barres |
| **Qualitative ordinale** | satisfaction (1 à 5) | effectifs, médiane, quantiles (la moyenne est discutable) |

> ⚠️ **La moyenne d'une variable ordinale** (satisfaction de 1 à 5) est très répandue mais n'a pas de sens strict : l'écart entre 1 et 2 est-il le même qu'entre 4 et 5 ? On la calcule quand même par convention, mais en gardant ceci en tête.

### 3.1.2 Charger et regarder le jeu de données

Voici la construction du jeu de données utilisé dans tout le chapitre. Vous n'avez pas besoin de comprendre chaque ligne maintenant : l'important est le **résultat**, un tableau de 400 commandes.

```python
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(100)
n = 400
canal = rng.choice(["Instagram", "Site", "Boutique"], size=n, p=[0.4, 0.35, 0.25])
base = {"Instagram": 3.7, "Site": 3.9, "Boutique": 4.1}
montant = np.round(np.exp(rng.normal([base[c] for c in canal], 0.55)), 1)
livraison = np.where(canal == "Boutique", 0, np.round(rng.gamma(4, 0.9, size=n)) + 1).astype(int)
satisfaction = np.clip(np.round(4.6 - 0.18 * livraison + rng.normal(0, 0.7, size=n)), 1, 5).astype(int)

df = pd.DataFrame({"canal": canal, "montant": montant,
                   "livraison": livraison, "satisfaction": satisfaction})
print(df.head(8))
print()
print("dimensions :", df.shape)
```
<!--sortie-->
```text
       canal  montant  livraison  satisfaction
0   Boutique     44.8          0             4
1       Site     34.5          2             4
2  Instagram     88.2          5             4
3  Instagram     30.1          4             4
4   Boutique    110.1          0             5
5       Site     39.8          5             3
6   Boutique     74.7          0             5
7   Boutique    108.7          0             4

dimensions : (400, 4)
```

Chaque ligne est une commande. `livraison` est le délai en jours (0 pour un retrait en boutique) et `satisfaction` une note de 1 à 5. Les trois premiers gestes à faire sur n'importe quel tableau :

```python
print(df.dtypes)                       # le type de chaque colonne
print()
print(df.isna().sum())                 # valeurs manquantes par colonne
print()
print(df.describe().round(2))          # résumé numérique
```
<!--sortie-->
```text
canal               str
montant         float64
livraison         int64
satisfaction      int64
dtype: object

canal           0
montant         0
livraison       0
satisfaction    0
dtype: int64

       montant  livraison  satisfaction
count   400.00     400.00        400.00
mean     60.25       3.29          3.96
std      38.02       2.56          0.80
min       8.60       0.00          1.00
25%      34.18       0.00          3.00
50%      51.00       3.00          4.00
75%      75.82       5.00          5.00
max     255.70      13.00          5.00
```

`describe()` donne d'un coup : effectif (`count`), moyenne (`mean`), écart-type (`std`), minimum, quartiles (25 %, 50 %, 75 %) et maximum. Aucune valeur manquante. Le montant moyen est d'environ 60 DT, mais le **maximum dépasse 250 DT** alors que la **médiane** (50 %) est d'environ 51 DT : la distribution est probablement **asymétrique**. Regardons cela de plus près.

### 3.1.3 Mesures de position : où est le centre ?

**La moyenne** $\bar x=\frac1n\sum x_i$ est le centre de gravité. **La médiane** est la valeur qui partage l'échantillon en deux moitiés égales : 50 % des commandes sont en dessous. **Le mode** est la valeur la plus fréquente.

Voici un petit exemple à la main pour sentir la différence. Cinq commandes : $20,\ 25,\ 30,\ 35,\ 400$ DT (la dernière est un gros achat professionnel). La moyenne vaut $(20+25+30+35+400)/5=102$ DT : aucune commande n'est proche de ce chiffre ! La médiane (la valeur du milieu après tri) vaut 30 DT, bien plus représentative d'une commande « typique ».

> 💡 **Règle de base.** La moyenne est sensible aux valeurs extrêmes ; la médiane est **robuste**. Quand la distribution est asymétrique, la moyenne est tirée vers la queue longue : **moyenne > médiane** pour une asymétrie à droite (cas des montants, revenus, durées).

```python
m = df["montant"]
print("moyenne :", round(m.mean(), 2))
print("médiane :", round(m.median(), 2))
print("moyenne tronquée (10 % de chaque côté) :", round(stats.trim_mean(m, 0.10), 2))
print("mode approximatif (classes de 10 DT) :", int(m.round(-1).mode()[0]), "DT")
```
<!--sortie-->
```text
moyenne : 60.25
médiane : 51.0
moyenne tronquée (10 % de chaque côté) : 54.9
mode approximatif (classes de 10 DT) : 40 DT
```

La moyenne (60 DT) dépasse nettement la médiane (51 DT) : quelques grosses commandes tirent la moyenne vers le haut. La **moyenne tronquée**, qui écarte les 10 % de valeurs les plus extrêmes de chaque côté, se situe entre les deux.

**Les quantiles** généralisent la médiane : le quantile à $q$ % est la valeur sous laquelle se trouvent $q$ % des observations. Les **quartiles** (25 %, 50 %, 75 %) découpent l'échantillon en quatre parts égales.

```python
print(m.quantile([0.05, 0.25, 0.50, 0.75, 0.95]).round(1))
```
<!--sortie-->
```text
0.05     19.0
0.25     34.2
0.50     51.0
0.75     75.8
0.95    128.6
Name: montant, dtype: float64
```

On lit par exemple : « 95 % des commandes font moins de ~130 DT », une information très utile pour dimensionner un seuil de livraison gratuite.

### 3.1.4 Mesures de dispersion : de combien ça varie ?

Deux boutiques dont le panier moyen est de 60 DT peuvent être très différentes si l'une a des paniers tous compris entre 55 et 65 et l'autre entre 5 et 300.

- **L'étendue** : max − min. Simple, mais entièrement dictée par deux valeurs extrêmes.
- **La variance** $s^2=\dfrac1{n-1}\sum(x_i-\bar x)^2$ et l'**écart-type** $s=\sqrt{s^2}$.
- **L'écart interquartile** (IQR) : $Q_3-Q_1$, l'étalement des 50 % du milieu. Robuste.
- **Le coefficient de variation** $s/\bar x$ : l'écart-type en proportion de la moyenne, sans unité, utile pour comparer des échelles différentes.

> ⚠️ **Pourquoi $n-1$ et pas $n$ ?** Pandas et NumPy ne donnent pas toujours la même chose : `pandas` divise par $n-1$ par défaut, `np.var` par $n$. Nous démontrons au 3.2 que $n-1$ est la bonne version pour **estimer** la variance de la population à partir d'un échantillon. Pour $n=400$ la différence est minime, mais pour $n=5$ elle est de 25 %.

```python
print("écart-type (pandas, n-1) :", round(m.std(), 2))
print("écart-type (numpy,  n)   :", round(np.std(m), 2))
print("étendue                  :", round(m.max() - m.min(), 1))
q1, q3 = m.quantile(0.25), m.quantile(0.75)
print("IQR                      :", round(q3 - q1, 1))
print("coefficient de variation :", round(m.std() / m.mean(), 2))
```
<!--sortie-->
```text
écart-type (pandas, n-1) : 38.02
écart-type (numpy,  n)   : 37.97
étendue                  : 247.1
IQR                      : 41.6
coefficient de variation : 0.63
```

Un écart-type de 38 DT pour une moyenne de 60 DT : un coefficient de variation de 63 %, ce qui est **très dispersé** (typique des montants).

### 3.1.5 La forme : histogrammes, asymétrie, boîtes à moustaches

Les nombres ne disent pas tout. **L'histogramme** découpe l'axe en classes et compte les observations dans chacune. La **boîte à moustaches** (*boxplot*) résume la distribution en cinq nombres : la boîte va du premier au troisième quartile, le trait central est la médiane, et les « moustaches » s'étendent jusqu'aux dernières valeurs situées à moins de $1{,}5\times\text{IQR}$ de la boîte ; les points au-delà sont signalés comme **valeurs atypiques** (*outliers*).

![À gauche : histogramme des 400 montants, avec la moyenne (orange) tirée vers la droite de la médiane (violet). À droite : boîtes à moustaches du montant selon le canal.](figures/ch03-distribution-montants.png)

On lit sur l'histogramme une **asymétrie à droite** : beaucoup de petites commandes, quelques très grosses. Sur le boxplot, la boutique a des commandes plus élevées que le site, lui-même plus élevé qu'Instagram. (Est-ce une vraie différence ou du hasard d'échantillonnage ? C'est la question du 3.4.)

L'**asymétrie** (*skewness*) se mesure par un nombre : nulle pour une courbe symétrique, positive à droite.

```python
print("asymétrie :", round(stats.skew(m), 2))
q1, q3 = m.quantile([0.25, 0.75])
borne_haute = q3 + 1.5 * (q3 - q1)
print("seuil haut des valeurs atypiques :", round(borne_haute, 1), "DT")
print("nombre de commandes au-dessus    :", int((m > borne_haute).sum()))
```
<!--sortie-->
```text
asymétrie : 1.75
seuil haut des valeurs atypiques : 138.3 DT
nombre de commandes au-dessus    : 17
```

> 💡 **Que faire d'une valeur atypique ?** Surtout **ne pas la supprimer automatiquement**. Se demander : est-ce une *erreur* (saisie : 2 500 au lieu de 25,00) ? Alors on corrige. Est-ce une valeur *légitime* mais rare (gros client professionnel) ? Alors on la garde et on utilise des résumés robustes. Les valeurs atypiques sont souvent l'information la plus intéressante : un fraudeur, une panne, une opportunité.

**Transformer pour symétriser.** Pour des variables positives très asymétriques, le **logarithme** rapproche la forme d'une cloche :

```python
lm = np.log(m)
print("asymétrie du montant            :", round(stats.skew(m), 2))
print("asymétrie du logarithme         :", round(stats.skew(lm), 2))
print("moyenne et médiane de log(montant) :", round(lm.mean(), 2), round(lm.median(), 2))
```
<!--sortie-->
```text
asymétrie du montant            : 1.75
asymétrie du logarithme         : -0.07
moyenne et médiane de log(montant) : 3.92 3.93
```

Après transformation, l'asymétrie est presque nulle et moyenne ≈ médiane : le montant suit approximativement une loi **log-normale** (le logarithme est normal). Beaucoup de grandeurs économiques sont dans ce cas, car elles résultent de **multiplications** d'effets (là où la loi normale vient d'additions, TCL du 2.4).

### 3.1.6 Variables qualitatives et comparaison de groupes

Pour une variable catégorielle, on compte (**effectifs**) et on calcule des **proportions** (fréquences). Pour comparer des groupes, on utilise `groupby`.

```python
print(df["canal"].value_counts())
print()
print(df["canal"].value_counts(normalize=True).round(3))
print()
print(df.groupby("canal")["montant"].agg(["count", "mean", "median", "std"]).round(1))
```
<!--sortie-->
```text
canal
Site         148
Instagram    138
Boutique     114
Name: count, dtype: int64

canal
Site         0.370
Instagram    0.345
Boutique     0.285
Name: proportion, dtype: float64

           count  mean  median   std
canal                               
Boutique     114  74.8    64.8  40.6
Instagram    138  49.0    41.5  31.1
Site         148  59.5    49.5  38.3
```

Les trois canaux apportent respectivement 138, 148 et 114 commandes (Instagram, Site, Boutique). Les paniers moyens sont d'environ 49, 60 et 75 DT : la boutique domine en valeur par commande. Mais attention :

> ⚠️ **Une différence observée n'est pas forcément une différence réelle.** Avec 114 à 148 commandes par canal, le hasard seul peut créer des écarts de quelques dinars. Pour savoir si l'écart entre 49 et 75 DT est « assez grand » pour être crédible, il faut un **test** (3.4) ou un **intervalle de confiance** (3.3). La statistique descriptive décrit ; elle ne *conclut* pas.

### 3.1.7 Relier deux variables : corrélation, et pourquoi il faut toujours dessiner

La **corrélation de Pearson** (2.3.3), calculée sur l'échantillon, mesure le lien *linéaire* entre deux variables quantitatives.

```python
print(df[["montant", "livraison", "satisfaction"]].corr().round(2))
```
<!--sortie-->
```text
              montant  livraison  satisfaction
montant          1.00      -0.20          0.07
livraison       -0.20       1.00         -0.53
satisfaction     0.07      -0.53          1.00
```

La corrélation entre le délai de livraison et la satisfaction est d'environ −0,53 : plus la livraison est lente, moins les clients sont satisfaits ; c'est cohérent avec le bon sens. En revanche, le montant n'est que faiblement lié à la satisfaction (+0,07).

**La corrélation de Spearman** est la corrélation de Pearson calculée sur les **rangs** (1er, 2e, 3e…). Elle détecte toute relation **monotone** (pas seulement linéaire) et résiste aux valeurs extrêmes.

```python
rho_s, _ = stats.spearmanr(df["livraison"], df["satisfaction"])
print("Spearman (livraison, satisfaction) :", round(rho_s, 2))
```
<!--sortie-->
```text
Spearman (livraison, satisfaction) : -0.51
```

> 🧪 **Le quartet d'Anscombe : pourquoi on dessine toujours.** En 1973, le statisticien Francis Anscombe a construit **quatre jeux de données** qui ont exactement les mêmes moyennes, variances, corrélation et droite de régression… mais des formes totalement différentes.

```python
x = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
ys = [[8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68],
      [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74],
      [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73],
      [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]]
xs = [x, x, x, [8] * 7 + [19] + [8] * 3]

for nom, a, b in zip(["I", "II", "III", "IV"], xs, ys):
    pente, ordonnee = np.polyfit(a, b, 1)
    print(f"jeu {nom:<3}: moy x = {np.mean(a):.2f}  moy y = {np.mean(b):.2f}  "
          f"corr = {np.corrcoef(a, b)[0, 1]:.3f}  droite : y = {pente:.2f} x + {ordonnee:.2f}")
```
<!--sortie-->
```text
jeu I  : moy x = 9.00  moy y = 7.50  corr = 0.816  droite : y = 0.50 x + 3.00
jeu II : moy x = 9.00  moy y = 7.50  corr = 0.816  droite : y = 0.50 x + 3.00
jeu III: moy x = 9.00  moy y = 7.50  corr = 0.816  droite : y = 0.50 x + 3.00
jeu IV : moy x = 9.00  moy y = 7.50  corr = 0.817  droite : y = 0.50 x + 3.00
```

Les quatre lignes sont quasiment identiques. Voici pourtant les quatre jeux :

![Le quartet d'Anscombe : mêmes statistiques, formes radicalement différentes. I : relation linéaire ordinaire. II : relation courbe. III : une valeur atypique fausse la droite. IV : un seul point (à droite) crée toute la corrélation.](figures/ch03-anscombe.png)

> ✅ **Règle d'or : on dessine d'abord, on calcule ensuite.** Un résumé numérique est une compression de l'information, avec perte. Seul un graphique révèle ce qui a été perdu.

> ✅ **À retenir (statistique descriptive).**
>
> - Population (inconnue) vs échantillon (observé) ; paramètres vs statistiques.
> - Position : moyenne (sensible aux extrêmes), médiane (robuste), quantiles. Dispersion : écart-type ($n-1$), IQR, coefficient de variation.
> - Montants, revenus, durées : souvent asymétriques à droite ; le logarithme symétrise. Ne supprimez pas les valeurs atypiques sans réfléchir.
> - Histogramme et boxplot pour la forme ; `groupby` pour comparer des groupes ; Pearson (linéaire) et Spearman (monotone) pour deux variables.
> - **Toujours tracer** (Anscombe). Une différence observée n'est pas encore une différence prouvée.


## 3.2 Estimation

> 💡 **Intuition.** La population a des paramètres (un panier moyen $\mu$, un taux de conversion $p$, un taux d'arrivée $\lambda$) que personne ne connaît. À partir d'un **échantillon**, on fabrique une **estimation**. La formule qui transforme l'échantillon en estimation s'appelle un **estimateur**. Il y a toujours plusieurs estimateurs possibles ; la question est : **lequel choisir, et à quel point peut-on lui faire confiance ?**

### 3.2.1 Un estimateur est une variable aléatoire

Notons $\theta$ un paramètre inconnu (n'importe lequel) et $\hat\theta$ (« thêta chapeau ») son estimateur. Comme l'échantillon est aléatoire, $\hat\theta$ **l'est aussi** : un autre échantillon donnerait une autre estimation. C'est exactement l'idée de la moyenne d'échantillon $\bar X_n$ au 2.4.1.

On peut le **voir** en jouant à Dieu : traitons nos 400 commandes comme *toute* la population (de moyenne connue) et tirons dedans des échantillons de 30 commandes, en recalculant la moyenne à chaque fois.

```python
import numpy as np
import pandas as pd
from scipy import stats
from scipy import optimize

rng = np.random.default_rng(11)
population = df["montant"].to_numpy()
print("moyenne de la 'population' :", round(population.mean(), 2))

moyennes = np.array([rng.choice(population, size=30, replace=False).mean() for _ in range(10_000)])
print("moyenne des 10 000 moyennes d'échantillons :", round(moyennes.mean(), 2))
print("écart-type de ces moyennes (erreur-type)    :", round(moyennes.std(), 2))
print("théorie sigma/sqrt(n)                       :", round(population.std() / np.sqrt(30), 2))
print("3 échantillons au hasard :", [round(float(rng.choice(population, 30).mean()), 1) for _ in range(3)])
```
<!--sortie-->
```text
moyenne de la 'population' : 60.25
moyenne des 10 000 moyennes d'échantillons : 60.3
écart-type de ces moyennes (erreur-type)    : 6.59
théorie sigma/sqrt(n)                       : 6.93
3 échantillons au hasard : [54.2, 59.5, 60.3]
```

Chaque échantillon de 30 commandes donne une moyenne différente (ci-dessus : 54,2 ; 59,5 ; 60,3), mais **en moyenne** ces moyennes tombent sur la vraie valeur (60,25), avec une dispersion de l'ordre de 7 DT. Cette dispersion est l'**erreur-type** : elle mesure la précision de l'estimateur. (Le petit écart avec la théorie vient du tirage **sans remise** dans une population finie.)

### 3.2.2 Qu'est-ce qu'un bon estimateur ?

On juge un estimateur sur trois critères, que l'on comprend très bien avec l'image d'un tir à la cible :

- **Le biais** : $\operatorname{Biais}(\hat\theta)=E[\hat\theta]-\theta$. Les tirs sont-ils centrés sur la cible, ou systématiquement décalés ? Un estimateur est **sans biais** si ce biais vaut 0.
- **La variance** : $\operatorname{Var}(\hat\theta)$. Les tirs sont-ils groupés ou dispersés ?
- **La cohérence** (ou *consistance*) : l'estimateur converge-t-il vers $\theta$ quand $n\to\infty$ ? (La loi des grands nombres l'assure pour la moyenne.)

Un bon estimateur est à la fois **peu biaisé** et **peu variable**. On les combine dans l'**erreur quadratique moyenne** :

> 📐 **Décomposition biais–variance.**
> $$\operatorname{EQM}(\hat\theta)=E\bigl[(\hat\theta-\theta)^2\bigr]=\operatorname{Var}(\hat\theta)+\operatorname{Biais}(\hat\theta)^2.$$
>
> *Preuve.* Notons $m=E[\hat\theta]$. On écrit $\hat\theta-\theta=(\hat\theta-m)+(m-\theta)$ et on développe le carré :
> $$E[(\hat\theta-\theta)^2]=E[(\hat\theta-m)^2]+2(m-\theta)\,E[\hat\theta-m]+(m-\theta)^2.$$
> Le terme du milieu est nul car $E[\hat\theta-m]=0$. Il reste $\operatorname{Var}(\hat\theta)+(m-\theta)^2$. $\blacksquare$

Cette formule a une conséquence profonde, qui reviendra tout au long du volume II : **accepter un petit biais peut réduire l'erreur totale si cela réduit beaucoup la variance**. C'est le principe de la régularisation en apprentissage automatique.

### 3.2.3 Pourquoi divise-t-on par $n-1$ pour la variance ?

Nous avons promis cette démonstration (3.1.4 et 2.3.3). Soit $X_1,\dots,X_n$ i.i.d. de moyenne $\mu$ et de variance $\sigma^2$. L'estimateur « naturel » de $\sigma^2$ est $\hat\sigma^2_n=\frac1n\sum(X_i-\bar X)^2$. Est-il sans biais ?

> 📐 **Calcul.** On insère $\mu$ : $X_i-\bar X=(X_i-\mu)-(\bar X-\mu)$. Alors
>
> $$\sum_i(X_i-\bar X)^2=\sum_i(X_i-\mu)^2-n(\bar X-\mu)^2.$$
>
> (En développant : $\sum(X_i-\mu)^2-2(\bar X-\mu)\sum(X_i-\mu)+n(\bar X-\mu)^2$ et $\sum(X_i-\mu)=n(\bar X-\mu)$, d'où le résultat.) Prenons l'espérance : $E[(X_i-\mu)^2]=\sigma^2$ et $E[(\bar X-\mu)^2]=\operatorname{Var}(\bar X)=\sigma^2/n$. Donc
>
> $$E\Bigl[\sum_i(X_i-\bar X)^2\Bigr]=n\sigma^2-n\cdot\frac{\sigma^2}n=(n-1)\,\sigma^2.$$
>
> Par conséquent $E[\hat\sigma^2_n]=\dfrac{n-1}n\sigma^2<\sigma^2$ : l'estimateur « divisé par $n$ » **sous-estime** la variance. Pour corriger, on divise par $n-1$ :
> $$S^2=\frac1{n-1}\sum_i(X_i-\bar X)^2,\qquad E[S^2]=\sigma^2.\ \blacksquare$$

> 💡 **Pourquoi intuitivement ?** Les données sont toujours plus proches de **leur propre** moyenne $\bar X$ que de la vraie moyenne $\mu$ (car $\bar X$ est justement construite pour être au centre des données). Mesurer les écarts à $\bar X$ sous-estime donc légèrement les écarts à $\mu$. L'échantillon a aussi « perdu un degré de liberté » : une fois $\bar X$ calculée, seules $n-1$ valeurs sont libres, la dernière est imposée.

Voyons-le sur ordinateur pour de **tout petits** échantillons ($n=5$), où l'effet est maximal (vraie variance = 1) :

```python
rng = np.random.default_rng(3)
x = rng.normal(0, 1, size=(100_000, 5))                 # 100 000 échantillons de taille 5
v_n = x.var(axis=1, ddof=0).mean()                      # divisé par n
v_n1 = x.var(axis=1, ddof=1).mean()                     # divisé par n-1
print("moyenne des estimations, division par n   :", round(v_n, 3), "  (théorie (n-1)/n = 0.8)")
print("moyenne des estimations, division par n-1 :", round(v_n1, 3))
```
<!--sortie-->
```text
moyenne des estimations, division par n   : 0.801   (théorie (n-1)/n = 0.8)
moyenne des estimations, division par n-1 : 1.001
```

![Distribution des estimations de la variance sur 100 000 échantillons de taille 5 : en divisant par n, on sous-estime en moyenne (0,80) ; en divisant par n−1, on est centré sur la vraie valeur (1).](figures/ch03-biais-variance.png)

> ⚠️ **Subtilité.** $S^2$ est sans biais pour la **variance**, mais $S=\sqrt{S^2}$ reste (très légèrement) biaisé pour l'écart-type, car la racine carrée n'est pas linéaire. Ce biais est négligeable en pratique.

### 3.2.4 La méthode des moments

> 💡 **Idée.** Les paramètres d'une loi s'expriment à l'aide de ses moments (espérance, variance…). La **méthode des moments** consiste à **égaler les moments théoriques aux moments observés** et à résoudre. C'est simple et intuitif.

**Exemple 1 : le taux d'arrivée.** Les temps (en minutes) séparant 25 commandes successives suivent une loi exponentielle de paramètre $\lambda$ inconnu. On sait que $E[T]=1/\lambda$. On égale à la moyenne observée $\bar t$ : $1/\hat\lambda=\bar t$, donc $\hat\lambda=1/\bar t$.

```python
rng = np.random.default_rng(7)
attentes = rng.exponential(scale=2.0, size=25)          # vraie valeur : lambda = 0.5 par minute (moyenne 2 min)
print("moyenne observée   :", round(attentes.mean(), 3), "minutes")
print("lambda estimé (1/moyenne) :", round(1 / attentes.mean(), 3), "(vraie valeur : 0.5)")
```
<!--sortie-->
```text
moyenne observée   : 1.988 minutes
lambda estimé (1/moyenne) : 0.503 (vraie valeur : 0.5)
```

**Exemple 2 : une loi à deux paramètres.** Les montants sont modélisés par une loi **Gamma** de forme $k$ et d'échelle $\theta$, avec $E[X]=k\theta$ et $\operatorname{Var}(X)=k\theta^2$. En égalant à la moyenne $\bar x$ et à la variance $s^2$ observées, on obtient deux équations : $\hat\theta=s^2/\bar x$ et $\hat k=\bar x^2/s^2$.

```python
xbar, s2 = m.mean(), m.var()
theta_mom = s2 / xbar
k_mom = xbar**2 / s2
print("Gamma par les moments : k =", round(k_mom, 3), "  theta =", round(theta_mom, 2))
```
<!--sortie-->
```text
Gamma par les moments : k = 2.511   theta = 23.99
```

La méthode des moments est rapide, mais elle n'est pas toujours la plus précise. La suivante est la référence.

### 3.2.5 Le maximum de vraisemblance

> 💡 **Intuition.** Yasmine lance une nouvelle promotion et observe 7 achats sur 20 visiteurs. Quelle valeur du taux de conversion $p$ rend ces données **les plus plausibles** ? Si $p$ valait 0,05, observer 7 acheteurs sur 20 serait très improbable ; si $p$ valait 0,9, tout autant. Il existe une valeur intermédiaire pour laquelle ce résultat est **le moins surprenant possible** : c'est l'estimation du maximum de vraisemblance.

**La vraisemblance** $L(\theta)$ est la probabilité (ou la densité) d'observer **les données effectivement observées**, vue comme une fonction du paramètre $\theta$. Pour des observations indépendantes $x_1,\dots,x_n$ :

$$L(\theta)=\prod_{i=1}^n f(x_i;\theta).$$

L'estimateur du maximum de vraisemblance (EMV, *MLE*) est la valeur $\hat\theta$ qui **maximise** $L(\theta)$. Comme les produits sont pénibles à dériver et numériquement instables (le produit de nombreuses probabilités minuscules s'écrase vers 0), on maximise plutôt le **logarithme** de la vraisemblance, qui transforme le produit en somme et a le même maximum (le logarithme est croissant) :

$$\ell(\theta)=\ln L(\theta)=\sum_{i=1}^n\ln f(x_i;\theta).$$

C'est de l'optimisation (section 1.3) : on dérive et on annule.

> 📐 **Exemple complet : le taux de conversion.** On observe $k$ achats sur $n$ visiteurs. Le modèle est binomial : $L(p)=\binom nk p^k(1-p)^{n-k}$, donc
>
> $$\ell(p)=\ln\tbinom nk+k\ln p+(n-k)\ln(1-p).$$
>
> On dérive : $\ell'(p)=\dfrac kp-\dfrac{n-k}{1-p}$. En annulant : $k(1-p)=(n-k)p\iff k=np$, d'où
>
> $$\hat p=\frac kn.$$
>
> La dérivée seconde $\ell''(p)=-\frac k{p^2}-\frac{n-k}{(1-p)^2}<0$ : c'est bien un **maximum**. $\blacksquare$
>
> L'estimateur du maximum de vraisemblance est donc tout simplement la **proportion observée**, ce qui rassure : la méthode retrouve le bon sens.

Pour $k=7$, $n=20$ : $\hat p=0{,}35$. La figure montre la vraisemblance et la log-vraisemblance en fonction de $p$ ; le maximum est atteint en $0{,}35$, et la log-vraisemblance est une courbe en cloche inversée, bien plus facile à optimiser.

![Vraisemblance (à gauche) et log-vraisemblance (à droite) pour 7 achats sur 20 visiteurs. Le maximum est en p = 0,35.](figures/ch03-vraisemblance.png)

Vérifions par calcul numérique : on cherche le maximum sur une grille, puis avec un optimiseur (la méthode générale quand il n'y a pas de formule).

```python
k, n_obs = 7, 20
grille = np.linspace(0.001, 0.999, 999)
loglik = stats.binom.logpmf(k, n_obs, grille)
print("maximum sur une grille :", round(grille[np.argmax(loglik)], 3))

# optimiseur : on minimise la log-vraisemblance NÉGATIVE
res = optimize.minimize_scalar(lambda p: -stats.binom.logpmf(k, n_obs, p), bounds=(0.001, 0.999), method="bounded")
print("optimiseur             :", round(res.x, 4))
```
<!--sortie-->
```text
maximum sur une grille : 0.35
optimiseur             : 0.35
```

**D'autres exemples classiques** (mêmes calculs, à faire en exercice) :

| Modèle | Estimateur du maximum de vraisemblance |
|---|---|
| Bernoulli / binomiale | $\hat p=\bar x$ (proportion observée) |
| Poisson$(\lambda)$ | $\hat\lambda=\bar x$ |
| Exponentielle$(\lambda)$ | $\hat\lambda=1/\bar x$ |
| Normale$(\mu,\sigma^2)$ | $\hat\mu=\bar x$ ; $\hat\sigma^2=\frac1n\sum(x_i-\bar x)^2$ (⚠️ divisé par $n$ : biaisé !) |

On retrouve pour l'exponentielle la même formule qu'avec les moments. Remarquez la dernière ligne : l'EMV de la variance divise par $n$, donc est **légèrement biaisé**. Le maximum de vraisemblance n'est pas toujours sans biais ; il a d'autres qualités.

**Quand il n'y a pas de formule : l'optimisation numérique.** Pour la loi Gamma des montants, on ne peut pas résoudre à la main. On confie la log-vraisemblance à un optimiseur, exactement comme au chapitre 1 (la descente de gradient en est l'ancêtre) :

```python
def neg_loglik_gamma(params, x):
    k, theta = params
    if k <= 0 or theta <= 0:
        return np.inf
    return -stats.gamma.logpdf(x, a=k, scale=theta).sum()

res = optimize.minimize(neg_loglik_gamma, x0=[k_mom, theta_mom], args=(m.to_numpy(),), method="Nelder-Mead")
k_mle, theta_mle = res.x
print("Gamma par maximum de vraisemblance : k =", round(k_mle, 3), " theta =", round(theta_mle, 2))
print("Gamma par moments                  : k =", round(k_mom, 3), " theta =", round(theta_mom, 2))
print("log-vraisemblance maximale :", round(-res.fun, 1))
print("log-vraisemblance (moments):", round(-neg_loglik_gamma([k_mom, theta_mom], m.to_numpy()), 1))
```
<!--sortie-->
```text
Gamma par maximum de vraisemblance : k = 3.001  theta = 20.07
Gamma par moments                  : k = 2.511  theta = 23.99
log-vraisemblance maximale : -1938.9
log-vraisemblance (moments): -1942.2
```

Le maximum de vraisemblance trouve des paramètres de log-vraisemblance **plus élevée** que ceux des moments (c'est sa définition : il est le meilleur *pour les données observées*). Ici les deux approches donnent des valeurs du même ordre (la forme passe de 2,5 à 3,0). N'oubliez pas qu'une loi Gamma n'est qu'un **modèle** des montants parmi d'autres (on a vu au 3.1.5 qu'une loi log-normale convient aussi bien) : estimer les paramètres ne dit pas si le modèle est juste. Notez aussi que la bibliothèque sait faire tout cela d'un coup :

```python
k_sp, loc_sp, theta_sp = stats.gamma.fit(m, floc=0)       # floc=0 : on impose une borne inférieure à 0
print("scipy.stats.gamma.fit :", round(k_sp, 3), round(theta_sp, 2))
```
<!--sortie-->
```text
scipy.stats.gamma.fit : 3.001 20.07
```

### 3.2.6 Pourquoi le maximum de vraisemblance est la référence

Sous des conditions de régularité raisonnables, l'EMV a quatre propriétés remarquables, que l'on admettra :

1. **Cohérent** : $\hat\theta\to\theta$ quand $n\to\infty$.
2. **Asymptotiquement normal** : $\hat\theta\approx\mathcal N\bigl(\theta,\ 1/(nI(\theta))\bigr)$ pour $n$ grand, où $I(\theta)$ est l'**information de Fisher** (la courbure moyenne de la log-vraisemblance autour du maximum : plus le pic est pointu, plus on est précis).
3. **Asymptotiquement efficace** : parmi les estimateurs cohérents, il a (presque) la plus petite variance possible.
4. **Invariant par reparamétrisation** : si $\hat\theta$ est l'EMV de $\theta$, alors $g(\hat\theta)$ est l'EMV de $g(\theta)$.

Le point 2 donne directement l'**erreur-type** : pour la proportion, $I(p)=\frac1{p(1-p)}$, donc

$$\operatorname{SE}(\hat p)=\sqrt{\frac{\hat p(1-\hat p)}n}.$$

```python
p_hat, n_obs = 7 / 20, 20
se = np.sqrt(p_hat * (1 - p_hat) / n_obs)
print("p chapeau =", p_hat, "  erreur-type =", round(se, 3))
print("avec 10 fois plus de données (70/200) :", round(np.sqrt(0.35 * 0.65 / 200), 3))
```
<!--sortie-->
```text
p chapeau = 0.35   erreur-type = 0.107
avec 10 fois plus de données (70/200) : 0.034
```

Avec 20 visiteurs, l'erreur-type est de 0,107 (près de 11 points !) : $\hat p=0{,}35$ est très imprécis. Avec 200 visiteurs, elle tombe à 0,034. Estimer, c'est bien ; **chiffrer l'incertitude de l'estimation** est mieux : c'est l'objet de la section suivante.

> ✅ **À retenir (estimation).**
>
> - Un **estimateur** est une formule appliquée à l'échantillon ; c'est une variable aléatoire dont on étudie le **biais**, la **variance**, la **cohérence**. $\operatorname{EQM}=\operatorname{Var}+\operatorname{Biais}^2$.
> - $\bar X$ est sans biais pour $\mu$, et **$S^2$ (divisé par $n-1$)** est sans biais pour $\sigma^2$ (preuve en 3.2.3).
> - **Moments** : on égale moments théoriques et observés. **Maximum de vraisemblance** : on maximise $\ell(\theta)=\sum\ln f(x_i;\theta)$ ; formule fermée si possible, optimiseur sinon.
> - Pour une proportion, l'EMV est la fréquence observée, d'erreur-type $\sqrt{\hat p(1-\hat p)/n}$.
> - L'EMV est cohérent, asymptotiquement normal et efficace : c'est l'outil standard.


## 3.3 Intervalles de confiance

> 💡 **Intuition.** Dire « le panier moyen est de 60,25 DT » est trompeur : cela suggère une précision que l'on n'a pas. Un meilleur énoncé est : « le panier moyen se situe, avec une confiance de 95 %, entre 56,5 et 64,0 DT ». L'**intervalle de confiance** (IC) transforme une estimation ponctuelle en une **fourchette honnête**, dont la largeur reflète l'incertitude.

### 3.3.1 Construire un intervalle pour une moyenne

Rappelons ce que nous savons (2.4) : par le théorème central limite, $\bar X_n\approx\mathcal N(\mu,\ \sigma^2/n)$. Donc le score centré réduit $\dfrac{\bar X_n-\mu}{\sigma/\sqrt n}$ suit à peu près $\mathcal N(0,1)$, et comme $P(-1{,}96\le Z\le1{,}96)=0{,}95$ :

> 📐 **Construction.**
>
> $$P\Bigl(-1{,}96\le\frac{\bar X_n-\mu}{\sigma/\sqrt n}\le1{,}96\Bigr)=0{,}95.$$
>
> On isole $\mu$ au milieu de l'encadrement : multiplier par $\sigma/\sqrt n$, puis soustraire $\bar X_n$ et multiplier par $-1$ (ce qui renverse les inégalités) :
>
> $$P\Bigl(\bar X_n-1{,}96\frac{\sigma}{\sqrt n}\ \le\ \mu\ \le\ \bar X_n+1{,}96\frac{\sigma}{\sqrt n}\Bigr)=0{,}95.$$
>
> L'**intervalle de confiance à 95 %** est donc $\bar x\pm1{,}96\,\dfrac{\sigma}{\sqrt n}$. $\blacksquare$

Il a une structure à retenir absolument, qui se retrouvera partout :

$$\text{estimation}\ \pm\ \text{(valeur critique)}\times\text{(erreur-type)}.$$

**Exemple à la main.** Sur 400 commandes, $\bar x=60{,}25$ DT et $s=38{,}02$. L'erreur-type est $38{,}02/\sqrt{400}=1{,}90$. L'IC à 95 % est $60{,}25\pm1{,}96\times1{,}90=60{,}25\pm3{,}73$, soit **[56,5 ; 64,0]** DT.

### 3.3.2 Que veut dire « 95 % de confiance » ?

C'est la phrase la plus mal comprise de la statistique. Elle ne signifie **pas** « il y a 95 % de chances que la vraie moyenne soit dans cet intervalle-ci ». La vraie moyenne $\mu$ est un nombre **fixe** (inconnu) : elle y est ou elle n'y est pas. Ce qui est aléatoire, c'est l'**intervalle** (il change à chaque échantillon).

> 💡 **La bonne lecture :** *si l'on répétait l'expérience un très grand nombre de fois, avec un nouvel échantillon à chaque fois, 95 % des intervalles ainsi construits contiendraient la vraie valeur.* La confiance porte sur la **méthode**, pas sur un intervalle particulier.

Voyons-le. Soixante échantillons de 40 commandes, un intervalle à 95 % pour chacun, et la vraie moyenne (connue ici car on traite nos 400 commandes comme la population) en pointillés :

![60 intervalles de confiance à 95 % construits sur 60 échantillons différents de 40 commandes. Les intervalles en rouge n'atteignent pas la vraie moyenne : environ 1 sur 20 en moyenne (5 sur 60 ici, une fluctuation normale).](figures/ch03-couverture.png)

Mesurons-le précisément, sur 20 000 échantillons :

```python
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(21)
population = df["montant"].to_numpy()
mu = population.mean()
n_ech, essais = 40, 20_000
t_crit = stats.t.ppf(0.975, n_ech - 1)

couvre = 0
largeurs = []
for _ in range(essais):
    e = rng.choice(population, size=n_ech, replace=False)
    se = e.std(ddof=1) / np.sqrt(n_ech)
    lo, hi = e.mean() - t_crit * se, e.mean() + t_crit * se
    couvre += (lo <= mu <= hi)
    largeurs.append(hi - lo)
print("part des intervalles contenant la vraie moyenne :", round(couvre / essais, 4))
print("largeur moyenne :", round(np.mean(largeurs), 2), "DT")
```
<!--sortie-->
```text
part des intervalles contenant la vraie moyenne : 0.9451
largeur moyenne : 23.88 DT
```

La couverture est proche de 95 % (un peu moins : la loi des montants est asymétrique et $n=40$ est modeste ; nous reviendrons sur ces limites). L'idée est donc validée.

> ⚠️ **Deux erreurs d'interprétation à éviter.**
> 1. « La vraie valeur a 95 % de chances d'être dans [56,5 ; 64,0] » : formulation courante, rigoureusement fausse dans l'approche fréquentiste (dans l'approche bayésienne, elle est correcte pour un *intervalle de crédibilité*).
> 2. « 95 % des **commandes** sont dans cet intervalle » : confusion entre la précision de la **moyenne** et la dispersion des **données**. L'IC de la moyenne est étroit ([56,5 ; 64,0]), alors que 95 % des commandes sont entre 19 et 129 DT (3.1.3).

### 3.3.3 Quand l'écart-type est inconnu : la loi de Student

En pratique, on ne connaît **pas** $\sigma$ ; on le remplace par son estimation $s$. Mais $s$ est elle-même aléatoire, ce qui ajoute de l'incertitude : pour de petits échantillons, on tomberait trop souvent à côté avec la valeur 1,96. William Gosset (qui signait « Student » en 1908, alors qu'il travaillait dans une brasserie Guinness) a montré que la bonne loi pour $\dfrac{\bar X-\mu}{S/\sqrt n}$ est la **loi de Student à $n-1$ degrés de liberté** (si les données sont à peu près normales).

C'est une cloche comme la normale, mais avec des **queues plus lourdes** (plus de prudence), qui tend vers $\mathcal N(0,1)$ quand $n$ augmente :

```python
for ddl in (2, 5, 10, 30, 100, 1000):
    print(f"degrés de liberté = {ddl:>4} : valeur critique à 95 % = {stats.t.ppf(0.975, ddl):.3f}")
print("loi normale                      :", round(stats.norm.ppf(0.975), 3))
```
<!--sortie-->
```text
degrés de liberté =    2 : valeur critique à 95 % = 4.303
degrés de liberté =    5 : valeur critique à 95 % = 2.571
degrés de liberté =   10 : valeur critique à 95 % = 2.228
degrés de liberté =   30 : valeur critique à 95 % = 2.042
degrés de liberté =  100 : valeur critique à 95 % = 1.984
degrés de liberté = 1000 : valeur critique à 95 % = 1.962
loi normale                      : 1.96
```

Avec 2 degrés de liberté (3 observations), la valeur critique est 4,30 : l'intervalle est plus de deux fois plus large qu'avec 1,96. Dès 30 degrés de liberté, on est proche de 2,04 ; avec 400 observations, la différence avec 1,96 est imperceptible.

L'intervalle devient $\bar x\pm t_{n-1,\,0{,}975}\dfrac{s}{\sqrt n}$. Voici le calcul pour nos 400 commandes, à la main puis avec `scipy` :

```python
m = df["montant"]
n = len(m)
xbar, s = m.mean(), m.std(ddof=1)
se = s / np.sqrt(n)
t_crit = stats.t.ppf(0.975, n - 1)
print(f"moyenne = {xbar:.2f}   erreur-type = {se:.2f}   t critique = {t_crit:.3f}")
print(f"IC à 95 % (à la main) : [{xbar - t_crit * se:.2f} ; {xbar + t_crit * se:.2f}]")
print("IC à 95 % (scipy)     :", np.round(stats.t.interval(0.95, n - 1, loc=xbar, scale=se), 2))
```
<!--sortie-->
```text
moyenne = 60.25   erreur-type = 1.90   t critique = 1.966
IC à 95 % (à la main) : [56.51 ; 63.98]
IC à 95 % (scipy)     : [56.51 63.98]
```

**Et pour chaque canal ?** On répète le calcul par groupe :

```python
def ic_moyenne(x, niveau=0.95):
    x = np.asarray(x)
    se = x.std(ddof=1) / np.sqrt(len(x))
    return stats.t.interval(niveau, len(x) - 1, loc=x.mean(), scale=se)

for canal in ["Instagram", "Site", "Boutique"]:
    x = df.loc[df["canal"] == canal, "montant"]
    lo, hi = ic_moyenne(x)
    print(f"{canal:<10} n = {len(x):>3}   moyenne = {x.mean():5.1f}   IC95 % = [{lo:5.1f} ; {hi:5.1f}]")
```
<!--sortie-->
```text
Instagram  n = 138   moyenne =  49.0   IC95 % = [ 43.8 ;  54.2]
Site       n = 148   moyenne =  59.5   IC95 % = [ 53.3 ;  65.7]
Boutique   n = 114   moyenne =  74.8   IC95 % = [ 67.3 ;  82.4]
```

Les intervalles d'Instagram ([43,8 ; 54,2]) et de la boutique ([67,3 ; 82,4]) **sont très éloignés** : c'est un indice sérieux que ces deux canaux diffèrent vraiment. L'intervalle du site ([53,3 ; 65,7]) chevauche légèrement celui d'Instagram mais pas celui de la boutique. Attention : « les intervalles se chevauchent » ne prouve **pas** que les moyennes sont égales, et même des intervalles qui se touchent peuvent cacher une différence significative. La bonne méthode est de construire un intervalle (ou un test) pour la **différence** elle-même, ce que nous ferons au 3.4.

> 💡 **Ce qui fait varier la largeur.** La demi-largeur est $t\times s/\sqrt n$. Elle **diminue** quand $n$ augmente (en $1/\sqrt n$), **augmente** quand la dispersion $s$ augmente, et **augmente** quand on exige plus de confiance (99 % donne un intervalle plus large que 95 %). Il n'y a pas de gratuité : plus de certitude coûte en précision.

```python
for niveau in (0.80, 0.90, 0.95, 0.99):
    lo, hi = ic_moyenne(m, niveau)
    print(f"confiance {niveau:.0%} : [{lo:.2f} ; {hi:.2f}]   largeur = {hi - lo:.2f}")
```
<!--sortie-->
```text
confiance 80% : [57.81 ; 62.69]   largeur = 4.88
confiance 90% : [57.11 ; 63.38]   largeur = 6.27
confiance 95% : [56.51 ; 63.98]   largeur = 7.47
confiance 99% : [55.33 ; 65.17]   largeur = 9.84
```

### 3.3.4 Intervalle pour une proportion

Pour un taux de conversion $\hat p=k/n$, l'erreur-type vue au 3.2.6 est $\sqrt{\hat p(1-\hat p)/n}$, et l'intervalle approché (dit de **Wald**) est

$$\hat p\pm1{,}96\sqrt{\frac{\hat p(1-\hat p)}n}.$$

Sur 1 000 visiteurs dont 205 achètent : $0{,}205\pm1{,}96\times0{,}0128=0{,}205\pm0{,}025$, soit **[18,0 % ; 23,0 %]**.

Mais cet intervalle devient **mauvais** pour de petits échantillons ou des proportions proches de 0 ou 1. Par exemple, avec 0 achat sur 20 visiteurs, $\hat p=0$ et l'intervalle de Wald est $[0\,;\,0]$ : « on est certain que le taux de conversion est exactement nul » ! Absurde. L'**intervalle de Wilson** corrige cela : il est centré non pas sur $\hat p$ mais sur une valeur légèrement « tirée vers 1/2 », et ne sort jamais de $[0,1]$.

```python
def ic_wald(k, n, niveau=0.95):
    p = k / n
    z = stats.norm.ppf(1 - (1 - niveau) / 2)
    d = z * np.sqrt(p * (1 - p) / n)
    return max(0, p - d), min(1, p + d)

def ic_wilson(k, n, niveau=0.95):
    return stats.binomtest(k, n).proportion_ci(confidence_level=niveau, method="wilson")[:2]

for k, n_obs in [(205, 1000), (7, 20), (0, 20), (2, 15)]:
    wald, wilson = ic_wald(k, n_obs), ic_wilson(k, n_obs)
    print(f"{k:>3}/{n_obs:<5} p = {k / n_obs:.3f}   Wald = [{wald[0]:.3f} ; {wald[1]:.3f}]   Wilson = [{wilson[0]:.3f} ; {wilson[1]:.3f}]")
```
<!--sortie-->
```text
205/1000  p = 0.205   Wald = [0.180 ; 0.230]   Wilson = [0.181 ; 0.231]
  7/20    p = 0.350   Wald = [0.141 ; 0.559]   Wilson = [0.181 ; 0.567]
  0/20    p = 0.000   Wald = [0.000 ; 0.000]   Wilson = [0.000 ; 0.161]
  2/15    p = 0.133   Wald = [0.000 ; 0.305]   Wilson = [0.037 ; 0.379]
```

Pour 1 000 visiteurs, les deux méthodes coïncident. Pour 7/20, l'intervalle est très large : **[0,18 ; 0,57]** pour Wilson, c'est-à-dire que 20 visiteurs ne permettent quasiment rien de conclure. Pour 0/20, Wilson dit que le taux réel peut aller jusqu'à environ 16 % (la fameuse « règle de trois » : avec 0 événement sur $n$, la borne haute à 95 % est environ $3/n=15\,\%$).

> ✅ **Conseil pratique.** Pour une proportion, utilisez **Wilson** (ou une méthode exacte) plutôt que Wald, sauf si $n$ est très grand et $p$ loin de 0 et 1.

### 3.3.5 Quand il n'y a pas de formule : le bootstrap

Et si l'on veut un intervalle pour la **médiane**, un quantile, un rapport, ou toute autre statistique pour laquelle on ne connaît pas de formule d'erreur-type ? Le **bootstrap** (Efron, 1979) offre une solution étonnamment simple et générale.

> 💡 **Idée.** On ne peut pas retirer de nouveaux échantillons dans la vraie population, mais on peut **rééchantillonner dans l'échantillon lui-même**. On tire $n$ valeurs **avec remise** dans nos $n$ observations (certaines apparaissent plusieurs fois, d'autres pas), on recalcule la statistique, et on recommence des milliers de fois. La dispersion des valeurs obtenues imite la dispersion qu'on aurait observée en échantillonnant la vraie population.

**L'algorithme (intervalle « percentile »).**

1. Répéter $B$ fois (par exemple 10 000) : tirer un échantillon de taille $n$ avec remise ; calculer la statistique.
2. L'intervalle à 95 % est formé des percentiles 2,5 % et 97,5 % des $B$ valeurs obtenues.

```python
rng = np.random.default_rng(42)
x = df["montant"].to_numpy()
B = 10_000

meds = np.array([np.median(rng.choice(x, size=len(x), replace=True)) for _ in range(B)])
moys = np.array([rng.choice(x, size=len(x), replace=True).mean() for _ in range(B)])

print("médiane observée :", np.median(x))
print("IC bootstrap 95 % de la médiane :", np.percentile(meds, [2.5, 97.5]).round(1))
print("IC bootstrap 95 % de la moyenne :", np.percentile(moys, [2.5, 97.5]).round(1))
print("(à comparer à l'IC de Student de la moyenne :", np.round(stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=x.std(ddof=1) / np.sqrt(len(x))), 1), ")")
```
<!--sortie-->
```text
médiane observée : 51.0
IC bootstrap 95 % de la médiane : [47.3 55.1]
IC bootstrap 95 % de la moyenne : [56.7 64. ]
(à comparer à l'IC de Student de la moyenne : [56.5 64. ] )
```

Pour la moyenne, le bootstrap donne pratiquement le même résultat que la formule de Student : rassurant. Pour la **médiane**, qui n'a pas de formule simple, il fournit un intervalle ([environ 47 ; 55] DT) que l'on n'aurait pas pu obtenir à la main.

> 🧪 **Limites.** Le bootstrap suppose que l'échantillon est représentatif de la population ; il marche mal pour des statistiques « extrêmes » (le maximum), avec de très petits échantillons, ou en présence de très fortes dépendances entre observations. Il reste un outil de base du data scientist, car il généralise à **n'importe quelle** statistique sans calcul mathématique.

### 3.3.6 Dimensionner un échantillon

On peut renverser le raisonnement : *quelle précision veut-on ?* Si Yasmine veut estimer le panier moyen à ±2 DT près, avec une confiance de 95 % et en supposant $s\approx38$ DT, il faut $1{,}96\times38/\sqrt n\le2$, soit

$$n\ge\Bigl(\frac{1{,}96\,s}{\varepsilon}\Bigr)^2=\Bigl(\frac{1{,}96\times38}2\Bigr)^2\approx1\,387\ \text{commandes}.$$

```python
s, eps = 38, 2
print("n pour une marge de ±2 DT :", int(np.ceil((1.96 * s / eps) ** 2)))
print("n pour une marge de ±1 DT :", int(np.ceil((1.96 * s / 1) ** 2)))
```
<!--sortie-->
```text
n pour une marge de ±2 DT : 1387
n pour une marge de ±1 DT : 5548
```

Diviser la marge par 2 demande **4 fois plus de données** (la loi en $1/\sqrt n$ du 2.4). C'est pourquoi gagner de la précision devient vite très coûteux.

> ✅ **À retenir (intervalles de confiance).**
>
> - Structure universelle : **estimation ± valeur critique × erreur-type**.
> - IC de la moyenne : $\bar x\pm t_{n-1}\,s/\sqrt n$ (Student). IC d'une proportion : préférez **Wilson** à Wald.
> - « Confiance à 95 % » signifie : **la méthode** capture la vraie valeur dans 95 % des échantillons possibles. Ce n'est pas une probabilité sur la vraie valeur.
> - Largeur : $\downarrow$ avec $n$ (en $1/\sqrt n$) ; $\uparrow$ avec la dispersion et avec le niveau de confiance.
> - **Bootstrap** : rééchantillonner avec remise pour obtenir un IC de n'importe quelle statistique.
> - $n\ge(z\,s/\varepsilon)^2$ pour viser une marge $\varepsilon$.


## 3.4 Tests d'hypothèses

> 💡 **Intuition : le tribunal.** Un test d'hypothèses fonctionne comme un procès. On part de la **présomption d'innocence** (l'hypothèse « il ne se passe rien », appelée $H_0$). On examine les **preuves** (les données). Si les preuves sont **très improbables** dans un monde où l'accusé est innocent, on le **condamne** (on rejette $H_0$). Sinon, on **acquitte** : cela ne prouve pas son innocence, cela veut seulement dire que les preuves sont insuffisantes.

### 3.4.1 Le vocabulaire et la méthode

- **Hypothèse nulle $H_0$** : l'état de référence, « pas d'effet, pas de différence ». Par exemple : « le panier moyen vaut 55 DT ».
- **Hypothèse alternative $H_1$** : ce que l'on cherche à montrer. « Le panier moyen est différent de 55 DT » (test **bilatéral**), ou « supérieur à 55 DT » (test **unilatéral**).
- **Statistique de test** $T$ : un nombre calculé sur l'échantillon qui mesure l'écart entre les données et ce que prédit $H_0$.
- **Niveau de signification $\alpha$** (souvent 5 %) : le risque que l'on accepte de se tromper en rejetant $H_0$ alors qu'elle est vraie.
- **p-valeur** : la probabilité, **si $H_0$ est vraie**, d'obtenir un résultat **au moins aussi extrême** que celui observé. Petite p-valeur = les données sont surprenantes sous $H_0$.

**Les deux erreurs possibles.**

| | $H_0$ est vraie | $H_0$ est fausse |
|---|---|---|
| **On rejette $H_0$** | ❌ **Erreur de type I** (faux positif), probabilité $\alpha$ | ✅ bonne décision (probabilité $1-\beta$ = **puissance**) |
| **On ne rejette pas $H_0$** | ✅ bonne décision | ❌ **Erreur de type II** (faux négatif), probabilité $\beta$ |

On **fixe** $\alpha$ à l'avance, et on cherche à garder $\beta$ petit (c'est la question de la puissance, 3.5).

**La recette en 5 étapes**, valable pour tous les tests de ce chapitre :

1. Poser $H_0$ et $H_1$.
2. Choisir $\alpha$ (avant de regarder les données !).
3. Calculer la statistique de test.
4. Calculer la p-valeur (ou comparer à la valeur critique).
5. Conclure : si $p<\alpha$, **rejeter** $H_0$ ; sinon, **ne pas rejeter** (et jamais « accepter »).

### 3.4.2 Test de Student sur une moyenne

> 🛠️ **Question de Yasmine.** Son objectif de panier moyen était de 55 DT. Les 400 commandes confirment-elles que le panier moyen **diffère** de 55 DT ?

1. $H_0:\mu=55$ ; $H_1:\mu\neq55$.
2. $\alpha=0{,}05$.
3. Statistique de test (la même construction qu'au 3.3.3, centrée sur la valeur de $H_0$) :

$$t=\frac{\bar x-\mu_0}{s/\sqrt n}=\frac{60{,}25-55}{38{,}02/\sqrt{400}}=\frac{5{,}25}{1{,}90}\approx2{,}76.$$

Sous $H_0$, $t$ suit une loi de Student à $n-1=399$ degrés de liberté. 4. La p-valeur est la probabilité qu'une telle loi donne une valeur **au moins aussi éloignée de 0** que 2,76, des deux côtés : $p=2\,P(T_{399}>2{,}76)$.

```python
import numpy as np
import pandas as pd
from scipy import stats

m = df["montant"]
mu0 = 55
n = len(m)
t_obs = (m.mean() - mu0) / (m.std(ddof=1) / np.sqrt(n))
p_val = 2 * stats.t.sf(abs(t_obs), df=n - 1)
print("t observé :", round(t_obs, 3))
print("p-valeur  :", round(p_val, 4))
print("valeur critique à 5 % :", round(stats.t.ppf(0.975, n - 1), 3))
res = stats.ttest_1samp(m, popmean=mu0)           # la fonction toute faite
print("scipy     : t =", round(res.statistic, 3), "  p =", round(res.pvalue, 4))
```
<!--sortie-->
```text
t observé : 2.76
p-valeur  : 0.0061
valeur critique à 5 % : 1.966
scipy     : t = 2.76   p = 0.0061
```

5. **Conclusion.** $p=0{,}006<0{,}05$ : on rejette $H_0$. Le panier moyen est significativement supérieur à 55 DT (il est en fait de 60,25 ; l'IC à 95 % du 3.3.3 était [56,5 ; 64,0], qui n'inclut pas 55 : **un test bilatéral à 5 % et un IC à 95 % disent la même chose**).

![Statistique de test sous H₀. Gauche : la valeur observée (2,76) tombe dans la zone de rejet (queues orange, 5 % au total). Droite : une valeur de 1,10 tomberait dans la zone de non-rejet.](figures/ch03-test-rejet.png)

> ⚠️ **« Ne pas rejeter » n'est pas « accepter ».** Si $p$ avait été de 0,30, on aurait dit « les données ne permettent pas de conclure que $\mu\neq55$ », pas « $\mu=55$ ». L'absence de preuve n'est pas la preuve de l'absence. (Un petit échantillon peut échouer à détecter un grand effet : c'est le problème de la puissance.)

### 3.4.3 Comparer deux groupes : le test de Welch

> 🛠️ **Question de Yasmine.** Les clients de la **boutique** dépensent-ils plus que ceux d'**Instagram** ? Les moyennes observées sont 74,8 et 49,0 DT, soit un écart de 25,8 DT. Cet écart est-il crédible ou dû au hasard ?

On teste $H_0:\mu_B=\mu_I$ contre $H_1:\mu_B\neq\mu_I$. On compare la différence des moyennes à son erreur-type. Comme les deux échantillons sont indépendants, les variances **s'additionnent** (2.3.3) :

$$t=\frac{\bar x_B-\bar x_I}{\sqrt{\dfrac{s_B^2}{n_B}+\dfrac{s_I^2}{n_I}}}.$$

C'est le **test de Welch**, qui n'exige pas que les deux groupes aient la même variance (c'est la version à utiliser par défaut ; l'ancien test de Student à variances égales est moins sûr).

```python
b = df.loc[df["canal"] == "Boutique", "montant"]
i = df.loc[df["canal"] == "Instagram", "montant"]

diff = b.mean() - i.mean()
se_diff = np.sqrt(b.var(ddof=1) / len(b) + i.var(ddof=1) / len(i))
print("différence des moyennes :", round(diff, 2), "DT")
print("erreur-type de la différence :", round(se_diff, 2))
print("t à la main :", round(diff / se_diff, 3))

res = stats.ttest_ind(b, i, equal_var=False)         # equal_var=False -> test de Welch
print("scipy (Welch) : t =", round(res.statistic, 3), "  p =", res.pvalue, "  ddl =", round(res.df, 1))
```
<!--sortie-->
```text
différence des moyennes : 25.8 DT
erreur-type de la différence : 4.64
t à la main : 5.565
scipy (Welch) : t = 5.565   p = 8.016365853327231e-08   ddl = 208.4
```

La statistique est $t\approx5{,}56$ et la p-valeur est de l'ordre de $10^{-7}$ : si les deux canaux avaient la même dépense moyenne, observer un écart aussi grand serait **quasi impossible**. On rejette $H_0$.

**Un test ne dit pas « de combien ».** Une p-valeur minuscule dit que l'effet est *réel*, pas qu'il est *grand*. Il faut toujours accompagner un test d'un **intervalle de confiance de la différence** et d'une **taille d'effet** :

```python
t_c = stats.t.ppf(0.975, res.df)
print(f"IC95 % de la différence : [{diff - t_c * se_diff:.1f} ; {diff + t_c * se_diff:.1f}] DT")

s_pooled = np.sqrt(((len(b) - 1) * b.var(ddof=1) + (len(i) - 1) * i.var(ddof=1)) / (len(b) + len(i) - 2))
print("d de Cohen :", round(diff / s_pooled, 2))
```
<!--sortie-->
```text
IC95 % de la différence : [16.7 ; 34.9] DT
d de Cohen : 0.72
```

Le client de la boutique dépense en moyenne entre 17 et 35 DT de plus (IC à 95 %). Le **d de Cohen** (la différence en nombre d'écarts-types) vaut environ 0,7 : un effet « moyen à grand » selon les conventions usuelles (0,2 petit, 0,5 moyen, 0,8 grand).

> 🧪 **Et la distribution asymétrique ?** Le test de Student suppose des moyennes à peu près normales (ce que le TCL assure pour des groupes de plus d'une centaine d'observations) ; il reste correct ici. Pour de petits groupes très asymétriques, on teste plutôt $\log(\text{montant})$, ou on utilise un test non paramétrique (➕ 3.7). Vérifions que la conclusion tient sur l'échelle logarithmique :

```python
res_log = stats.ttest_ind(np.log(b), np.log(i), equal_var=False)
print("test sur log(montant) : t =", round(res_log.statistic, 2), "  p =", res_log.pvalue)
res_si = stats.ttest_ind(df.loc[df["canal"] == "Site", "montant"], i, equal_var=False)
print("Site contre Instagram  : t =", round(res_si.statistic, 2), "  p =", round(res_si.pvalue, 4))
```
<!--sortie-->
```text
test sur log(montant) : t = 6.46   p = 5.400582683884821e-10
Site contre Instagram  : t = 2.55   p = 0.0113
```

Même conclusion. Pour Site contre Instagram, $p\approx0{,}011$ : l'écart (10,5 DT) est aussi significatif au seuil de 5 %, mais bien moins fortement.

**Le test apparié.** Quand les deux séries concernent **les mêmes individus** (avant/après), on ne compare pas deux groupes indépendants : on calcule la **différence pour chaque individu** et on teste que sa moyenne est nulle. Exemple : 8 colis dont on a mesuré le délai avant et après un changement de transporteur.

```python
avant = np.array([5, 4, 6, 7, 5, 6, 8, 5])
apres = np.array([4, 4, 5, 6, 5, 5, 6, 4])
d = avant - apres
print("différences :", d, "  moyenne :", d.mean())
res = stats.ttest_rel(avant, apres)
print("test apparié : t =", round(res.statistic, 2), "  p =", round(res.pvalue, 4))
print("(ttest_1samp sur les différences donne la même chose :", round(stats.ttest_1samp(d, 0).pvalue, 4), ")")
```
<!--sortie-->
```text
différences : [1 0 1 1 0 1 2 1]   moyenne : 0.875
test apparié : t = 3.86   p = 0.0062
(ttest_1samp sur les différences donne la même chose : 0.0062 )
```

Le nouveau transporteur fait gagner en moyenne 0,875 jour ($p\approx0{,}006$). Ignorer l'appariement (comme si les groupes étaient indépendants) donnerait un test beaucoup moins sensible, car on gaspillerait l'information que chaque colis est comparé à lui-même :

```python
print("(à tort, test non apparié : p =", round(stats.ttest_ind(avant, apres).pvalue, 3), ")")
```
<!--sortie-->
```text
(à tort, test non apparié : p = 0.128 )
```

### 3.4.4 Test sur une proportion

> 🛠️ **Question de Yasmine.** Historiquement, le taux de conversion était de 18 %. Sur les 1 000 dernières visites, 205 ont acheté (20,5 %). Y a-t-il une amélioration réelle ?

$H_0:p=0{,}18$ contre $H_1:p\neq0{,}18$. Sous $H_0$, l'erreur-type est $\sqrt{p_0(1-p_0)/n}$ (on utilise la valeur de $H_0$, pas l'estimation) et la statistique

$$z=\frac{\hat p-p_0}{\sqrt{p_0(1-p_0)/n}}=\frac{0{,}205-0{,}18}{\sqrt{0{,}18\times0{,}82/1000}}=\frac{0{,}025}{0{,}01215}\approx2{,}06.$$

On compare à la loi normale (TCL). Il existe aussi un test **exact** basé sur la loi binomiale, sans approximation :

```python
k, n_v, p0 = 205, 1000, 0.18
z = (k / n_v - p0) / np.sqrt(p0 * (1 - p0) / n_v)
print("z =", round(z, 3), "  p-valeur (approx. normale) =", round(2 * stats.norm.sf(abs(z)), 4))
print("test exact binomial : p-valeur =", round(stats.binomtest(k, n_v, p0).pvalue, 4))
```
<!--sortie-->
```text
z = 2.058   p-valeur (approx. normale) = 0.0396
test exact binomial : p-valeur = 0.0436
```

Les deux p-valeurs (0,040 et 0,044) sont **juste en dessous** de 0,05. On rejette $H_0$, mais de peu : c'est une preuve **modérée**, pas écrasante. Un intervalle de Wilson pour $p$, [18,1 % ; 23,1 %], inclut à peine 18 %. Lecture honnête : « il y a des indices d'amélioration, à confirmer avec davantage de données ».

### 3.4.5 Le test A/B : comparer deux proportions

C'est le test le plus utilisé en pratique dans le web et le marketing. Yasmine essaie deux versions de sa page produit. La version A (1 000 visiteurs) donne 120 achats (12 %), la version B (1 000 visiteurs) donne 150 achats (15 %). B est-elle meilleure ?

$H_0:p_A=p_B$. Sous $H_0$, les deux groupes ont le même taux, estimé en **regroupant** les données : $\hat p=\frac{120+150}{2000}=0{,}135$. L'erreur-type de la différence est $\sqrt{\hat p(1-\hat p)\bigl(\frac1{n_A}+\frac1{n_B}\bigr)}$ et

$$z=\frac{\hat p_B-\hat p_A}{\sqrt{\hat p(1-\hat p)\bigl(\frac1{n_A}+\frac1{n_B}\bigr)}}=\frac{0{,}03}{0{,}01528}\approx1{,}96.$$

```python
kA, nA, kB, nB = 120, 1000, 150, 1000
p_pool = (kA + kB) / (nA + nB)
se = np.sqrt(p_pool * (1 - p_pool) * (1 / nA + 1 / nB))
z = (kB / nB - kA / nA) / se
print("z =", round(z, 3), "  p-valeur =", round(2 * stats.norm.sf(abs(z)), 4))

# IC de la différence (erreur-type non regroupée)
se_nr = np.sqrt((kA / nA) * (1 - kA / nA) / nA + (kB / nB) * (1 - kB / nB) / nB)
d = kB / nB - kA / nA
print(f"différence = {d:.3f}   IC95 % = [{d - 1.96 * se_nr:.4f} ; {d + 1.96 * se_nr:.4f}]")
```
<!--sortie-->
```text
z = 1.963   p-valeur = 0.0496
différence = 0.030   IC95 % = [0.0001 ; 0.0599]
```

$p\approx0{,}0496$ : **tout juste** sous le seuil de 5 %, et l'intervalle de la différence ([0,0 ; 6 points]) frôle zéro. La conclusion « B est meilleure » est **fragile**. Ce cas, très courant, illustre pourquoi le seuil de 0,05 n'est pas une frontière magique : 0,0496 et 0,0504 ne sont pas deux mondes différents (nous y revenons en 3.5).

### 3.4.6 Le test du khi-deux : deux variables qualitatives sont-elles liées ?

> 🛠️ **Question de Yasmine.** La proportion de clients **satisfaits** (note ≥ 4) dépend-elle du canal de vente ?

On range les données dans un **tableau de contingence** :

```python
df["satisfait"] = df["satisfaction"] >= 4
tableau = pd.crosstab(df["canal"], df["satisfait"])
print(tableau)
print()
print(pd.crosstab(df["canal"], df["satisfait"], normalize="index").round(3))
```
<!--sortie-->
```text
satisfait  False  True 
canal                  
Boutique       5    109
Instagram     51     87
Site          45    103

satisfait  False  True 
canal                  
Boutique   0.044  0.956
Instagram  0.370  0.630
Site       0.304  0.696
```

$H_0$ : le canal et la satisfaction sont **indépendants**. Si c'était vrai, la proportion de satisfaits serait la même dans chaque canal (et égale à la proportion globale). On calcule alors, pour chaque case, l'**effectif attendu sous $H_0$** :

$$E_{ij}=\frac{(\text{total de la ligne }i)\times(\text{total de la colonne }j)}{\text{total général}}.$$

La statistique du khi-deux mesure l'écart entre effectifs observés ($O_{ij}$) et attendus :

$$\chi^2=\sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}.$$

Sous $H_0$, elle suit une loi du khi-deux à $(\text{lignes}-1)(\text{colonnes}-1)$ degrés de liberté. Plus les écarts sont grands, plus $\chi^2$ est grand.

```python
from scipy.stats import chi2_contingency
chi2, p, ddl, attendus = chi2_contingency(tableau)
print("effectifs attendus sous H0 :")
print(pd.DataFrame(attendus, index=tableau.index, columns=tableau.columns).round(1))
print(f"\nkhi-deux = {chi2:.2f}   ddl = {ddl}   p-valeur = {p:.2e}")

n_tot = tableau.values.sum()
cramer_v = np.sqrt(chi2 / (n_tot * (min(tableau.shape) - 1)))
print("V de Cramér :", round(cramer_v, 2))
```
<!--sortie-->
```text
effectifs attendus sous H0 :
satisfait  False  True 
canal                  
Boutique    28.8   85.2
Instagram   34.8  103.2
Site        37.4  110.6

khi-deux = 38.40   ddl = 2   p-valeur = 4.60e-09
V de Cramér : 0.31
```

Dans la boutique, il y a **109 satisfaits sur 114** (96 %), alors que l'on en attendrait environ 85 si le canal n'avait aucun effet (soit 24 de plus) ; sur Instagram, 63 % seulement (87 sur 138). La statistique est $\chi^2\approx38$ pour 2 degrés de liberté : $p\approx5\times10^{-9}$. On rejette l'indépendance. Le **V de Cramér** (0 = indépendance, 1 = lien parfait) vaut 0,31 : un lien d'intensité moyenne. (Attention : la boutique n'a pas de délai de livraison, ce qui explique sans doute en grande partie l'écart ; l'association n'est pas une causalité.)

> ⚠️ **Condition de validité.** L'approximation du khi-deux est fiable si **tous les effectifs attendus sont au moins 5**. Sinon, on utilise le test exact de Fisher (`scipy.stats.fisher_exact` pour un tableau 2×2).

### 3.4.7 Comment choisir son test ?

| Question | Données | Test |
|---|---|---|
| La moyenne vaut-elle $\mu_0$ ? | 1 variable quantitative | Student à un échantillon |
| Deux groupes indépendants ont-ils la même moyenne ? | quantitative × 2 groupes | **Welch** |
| Avant/après sur les mêmes individus ? | quantitatives appariées | Student apparié |
| Plus de 2 groupes ? | quantitative × $k$ groupes | ANOVA (`f_oneway`) ou Kruskal-Wallis (➕ 3.7) |
| La proportion vaut-elle $p_0$ ? | 1 variable binaire | z (ou binomial exact) |
| Deux proportions égales ? (A/B) | binaire × 2 groupes | z à deux proportions, ou khi-deux |
| Deux variables qualitatives liées ? | catégorielle × catégorielle | **khi-deux** (ou Fisher) |
| Deux variables quantitatives liées ? | quantitative × quantitative | test de corrélation (`pearsonr`, `spearmanr`) |

> ✅ **À retenir (tests d'hypothèses).**
>
> - On fixe $H_0$ (« rien ne se passe »), $H_1$, $\alpha$ ; on calcule une statistique de test et sa **p-valeur** ; on rejette si $p<\alpha$.
> - Deux erreurs : **type I** (faux positif, probabilité $\alpha$) et **type II** (faux négatif, probabilité $\beta$). Puissance $=1-\beta$.
> - « Ne pas rejeter » ≠ « accepter ». Une p-valeur faible dit que l'effet est *réel*, pas qu'il est *grand* : donnez toujours l'**IC** de l'effet et une **taille d'effet**.
> - Student (une moyenne), **Welch** (deux moyennes), apparié, z (proportions), **khi-deux** (deux variables qualitatives).
> - Un test bilatéral à 5 % équivaut à regarder si 0 (ou la valeur de $H_0$) est dans l'IC à 95 %.


## 3.5 p-valeurs, puissance et tests multiples

Au 3.4, nous avons *utilisé* la p-valeur. Voici maintenant comment ne pas s'en servir de travers. Cette section est celle qui vous évitera le plus d'erreurs concrètes : une bonne partie des « découvertes » publiées qui ne se reproduisent pas viennent de ce que nous allons voir.

### 3.5.1 Ce que la p-valeur est vraiment

> 📐 **Définition.** La **p-valeur** est la probabilité, calculée **en supposant $H_0$ vraie**, d'obtenir une statistique de test **au moins aussi extrême** que celle observée.

$$p=P\bigl(\text{résultat aussi extrême ou plus}\ \big|\ H_0\bigr).$$

Observez la direction du conditionnement : c'est $P(\text{données}\mid H_0)$ et **non** $P(H_0\mid\text{données})$. Nous avons vu au 2.1 que **inverser un conditionnement est l'erreur classique**.

Pour la sentir, rien de mieux que de fabriquer un monde où $H_0$ est vraie et de regarder les p-valeurs qu'on obtient. Simulons 10 000 tests de Student de deux groupes de 30 individus **tirés dans la même loi** (donc aucune vraie différence) :

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(1)
pvals_h0 = np.array([stats.ttest_ind(rng.normal(0, 1, 30), rng.normal(0, 1, 30)).pvalue for _ in range(10_000)])

print("proportion de p < 0,05 quand H0 est vraie :", round((pvals_h0 < 0.05).mean(), 4))
print("proportion de p < 0,01                     :", round((pvals_h0 < 0.01).mean(), 4))
print("proportion de p < 0,50                     :", round((pvals_h0 < 0.50).mean(), 4))
print("moyenne des p-valeurs                      :", round(pvals_h0.mean(), 3))
```
<!--sortie-->
```text
proportion de p < 0,05 quand H0 est vraie : 0.0486
proportion de p < 0,01                     : 0.0103
proportion de p < 0,50                     : 0.5013
moyenne des p-valeurs                      : 0.499
```

Quand $H_0$ est vraie, **la p-valeur suit une loi uniforme sur $[0,1]$** : 5 % des tests donnent $p<0{,}05$, 1 % donnent $p<0{,}01$, etc. C'est exactement ce que signifie « niveau $\alpha=5\,\%$ » : **un test sur vingt crie au loup à tort** quand il n'y a rien. Ce n'est pas un défaut du test, c'est sa définition.

Et quand $H_0$ est **fausse** ? Les p-valeurs se tassent vers 0 :

```python
pvals_h1 = np.array([stats.ttest_ind(rng.normal(0.8, 1, 30), rng.normal(0, 1, 30)).pvalue for _ in range(10_000)])
print("avec un vrai effet (d = 0,8) : proportion de p < 0,05 :", round((pvals_h1 < 0.05).mean(), 3))
print("histogramme (10 classes) sous H0 :", np.histogram(pvals_h0, bins=10, range=(0, 1))[0])
print("histogramme (10 classes) sous H1 :", np.histogram(pvals_h1, bins=10, range=(0, 1))[0])
```
<!--sortie-->
```text
avec un vrai effet (d = 0,8) : proportion de p < 0,05 : 0.865
histogramme (10 classes) sous H0 : [ 980 1008 1028 1006  991  985 1036  964 1024  978]
histogramme (10 classes) sous H1 : [9248  419  160   62   47   25   16    9    7    7]
```

Sous $H_0$, l'histogramme est **plat** ; sous $H_1$, il est entassé à gauche. C'est un outil de diagnostic précieux : si vous testez des milliers de variables et que l'histogramme de vos p-valeurs est plat, il n'y a probablement **rien** à trouver.

### 3.5.2 Ce que la p-valeur n'est pas

> ⚠️ **Cinq contresens fréquents.** Une p-valeur de 0,03 ne signifie **pas** :
>
> 1. que $H_0$ a 3 % de chances d'être vraie ;
> 2. que $H_1$ a 97 % de chances d'être vraie ;
> 3. que l'effet est **grand** ou **important** ;
> 4. que l'on obtiendrait de nouveau $p<0{,}05$ en refaisant l'étude (la **reproductibilité** dépend de la puissance) ;
> 5. qu'on a 3 % de chances de se tromper en rejetant $H_0$.

**Le point 5 mérite une démonstration**, car il est lourd de conséquences. Le risque réel de se tromper quand on rejette dépend de la **proportion d'hypothèses qui sont vraies** au départ : on retrouve la formule de Bayes de la section 2.1 et l'erreur du taux de base !

> 💡 **Exemple.** Yasmine teste 1 000 idées d'amélioration (couleur d'un bouton, texte d'une promotion, ordre des produits…). Réalistement, **10 %** seulement ont un vrai effet (100 vraies idées, 900 inutiles). Son test a un niveau $\alpha=5\,\%$ et une puissance de 80 %.
>
> - Vraies idées détectées : $100\times0{,}80=80$.
> - Idées inutiles « détectées » à tort : $900\times0{,}05=45$.
> - Au total, 125 résultats « significatifs », dont **45 sont des faux positifs**.

$$P(\text{fausse découverte}\mid\text{significatif})=\frac{45}{125}=36\,\%.$$

Plus d'un résultat « significatif » sur trois est faux, alors que $\alpha$ n'est que de 5 % ! Même mécanisme que l'alerte antifraude du 2.1.6. C'est pourquoi on exige des preuves plus fortes pour des hypothèses peu plausibles a priori (« des affirmations extraordinaires exigent des preuves extraordinaires »).

```python
alpha, puissance, part_vraies = 0.05, 0.80, 0.10
vrais_positifs = part_vraies * puissance
faux_positifs = (1 - part_vraies) * alpha
print("proportion de faux parmi les significatifs :", round(faux_positifs / (vrais_positifs + faux_positifs), 3))
```
<!--sortie-->
```text
proportion de faux parmi les significatifs : 0.36
```

### 3.5.3 Signification statistique ≠ importance pratique

Avec assez de données, **n'importe quelle** différence, même ridicule, devient « significative ». Un exemple extrême : deux versions d'une page ont des taux de conversion de 20,00 % et 20,10 %, mesurés sur 10 millions de visiteurs chacune.

```python
nA = nB = 10_000_000
pA, pB = 0.2000, 0.2010
p_pool = (pA + pB) / 2
z = (pB - pA) / np.sqrt(p_pool * (1 - p_pool) * (2 / nA))
print("z =", round(z, 2), "   p-valeur =", f"{2 * stats.norm.sf(z):.1e}")
print("gain absolu :", round((pB - pA) * 100, 2), "point de pourcentage")
```
<!--sortie-->
```text
z = 5.58    p-valeur = 2.3e-08
gain absolu : 0.1 point de pourcentage
```

La p-valeur est inférieure à 0,001 (hautement « significatif »), mais le gain est de **0,1 point** de conversion. Est-il utile ? Cela dépend du coût du changement, pas de la p-valeur. **Toujours rapporter la taille de l'effet et son intervalle de confiance**, jamais seulement « $p<0{,}05$ ».

### 3.5.4 La puissance : savoir si l'on peut voir ce qu'on cherche

> 💡 **Intuition.** Un test est comme un détecteur de métaux. Un détecteur peu sensible ne signale pas un petit objet enterré profondément : **l'absence de signal ne prouve pas l'absence d'objet**. La **puissance** $1-\beta$ est la probabilité que le test détecte un effet **s'il existe vraiment** (de taille donnée).

La puissance dépend de quatre choses liées entre elles :

| Facteur | Si... | ...alors la puissance |
|---|---|---|
| **Taille de l'effet** | grandit | augmente |
| **Taille d'échantillon** $n$ | grandit | augmente |
| **Dispersion** des données | diminue | augmente |
| **Niveau** $\alpha$ | on l'assouplit (0,10 au lieu de 0,05) | augmente (au prix de plus de faux positifs) |

**Retour sur notre test A/B du 3.4.5** (12 % contre 15 %, 1 000 visiteurs par version). Quelle était la puissance de cette expérience ? Sous $H_1$ avec $p_A=0{,}12$ et $p_B=0{,}15$, l'erreur-type de la différence est $\sqrt{\frac{0{,}12\times0{,}88}{1000}+\frac{0{,}15\times0{,}85}{1000}}=0{,}0154$, et la statistique de test est centrée sur $0{,}03/0{,}0154=1{,}95$. La puissance est donc la probabilité que cette statistique dépasse 1,96 :

$$\text{puissance}=P\bigl(Z>1{,}96-1{,}95\bigr)\approx0{,}50.$$

```python
def puissance_ab(p1, p2, n, alpha=0.05):
    se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    return stats.norm.cdf(abs(p2 - p1) / se - stats.norm.ppf(1 - alpha / 2))

print("puissance de l'expérience A/B du 3.4.5 :", round(puissance_ab(0.12, 0.15, 1000), 3))

# vérification par simulation
rng = np.random.default_rng(2)
rejets = 0
for _ in range(10_000):
    a, b = rng.binomial(1000, 0.12), rng.binomial(1000, 0.15)
    pp = (a + b) / 2000
    z = (b / 1000 - a / 1000) / np.sqrt(pp * (1 - pp) * 2 / 1000)
    rejets += abs(z) > 1.96
print("puissance simulée                     :", rejets / 10_000)
```
<!--sortie-->
```text
puissance de l'expérience A/B du 3.4.5 : 0.502
puissance simulée                     : 0.4954
```

La puissance n'était que de **50 %** : même si B est réellement meilleure de 3 points, l'expérience n'avait qu'**une chance sur deux** de le détecter. Le résultat « tout juste significatif » obtenu était donc de la chance autant que de l'information. Un test sous-dimensionné est un pari.

**Dimensionner l'expérience avant de la lancer.** On fixe l'effet minimal intéressant (ici +3 points), $\alpha=5\,\%$ et la puissance voulue (80 % est l'usage), puis on calcule $n$ :

$$n\ \text{par groupe}=\frac{(z_{1-\alpha/2}+z_{1-\beta})^2\,\bigl[p_1(1-p_1)+p_2(1-p_2)\bigr]}{(p_2-p_1)^2}.$$

```python
za, zb = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
def n_par_groupe(p1, p2):
    return (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2

for delta in (0.05, 0.03, 0.02, 0.01):
    print(f"détecter 12 % -> {12 + delta * 100:.0f} % : {int(np.ceil(n_par_groupe(0.12, 0.12 + delta))):>6} visiteurs par version")
```
<!--sortie-->
```text
détecter 12 % -> 17 % :    775 visiteurs par version
détecter 12 % -> 15 % :   2033 visiteurs par version
détecter 12 % -> 14 % :   4435 visiteurs par version
détecter 12 % -> 13 % :  17166 visiteurs par version
```

Pour détecter 3 points avec 80 % de puissance, il faut **environ 2 000 visiteurs par version**, soit le double de ce que Yasmine avait. Pour détecter 1 point, il en faut **près de 18 000**. La loi en $1/\text{effet}^2$ est impitoyable : diviser l'effet par 3 multiplie les besoins par 9.

![À gauche : puissance d'un test A/B en fonction du nombre de visiteurs, pour trois tailles d'effet. À droite : si l'on « jette un œil » aux résultats de plus en plus souvent et que l'on s'arrête dès que p < 0,05, le taux de faux positifs explose (sous H₀).](figures/ch03-puissance.png)

> ⚠️ **L'arrêt prématuré (*peeking*).** Dans une expérience en ligne, la tentation est forte de regarder les résultats chaque jour et de s'arrêter dès que $p<0{,}05$. La figure de droite montre le résultat : en regardant 20 fois, **le taux de faux positifs passe de 5 % à environ 25 %**, alors qu'il n'y a *aucun* effet réel. Règle : **fixer la taille d'échantillon à l'avance et ne conclure qu'à la fin** (ou utiliser des méthodes séquentielles conçues pour cela).

### 3.5.5 Les tests multiples : le piège du « fouillis de comparaisons »

> 💡 **Intuition.** Si vous lancez un dé 20 fois, vous obtiendrez presque sûrement un 6 quelque part. Si vous effectuez 20 tests à 5 %, il est presque sûr que l'un d'eux sera « significatif » par pur hasard.

Raisonnons comme au 2.1.4 (« au moins un ») : si les 20 tests sont indépendants et que toutes les hypothèses nulles sont vraies, la probabilité d'avoir **au moins un faux positif** est

$$1-(1-\alpha)^m=1-0{,}95^{20}\approx0{,}64.$$

```python
for m_tests in (1, 5, 10, 20, 50, 100):
    print(f"{m_tests:>3} tests : P(au moins un faux positif) = {1 - 0.95 ** m_tests:.3f}")
```
<!--sortie-->
```text
  1 tests : P(au moins un faux positif) = 0.050
  5 tests : P(au moins un faux positif) = 0.226
 10 tests : P(au moins un faux positif) = 0.401
 20 tests : P(au moins un faux positif) = 0.642
 50 tests : P(au moins un faux positif) = 0.923
100 tests : P(au moins un faux positif) = 0.994
```

Avec 100 tests, c'est quasi certain (99,4 %). Dès que l'on teste plusieurs variables, segments ou métriques, il faut en tenir compte. C'est exactement ce qui arrive quand on « fouille » un jeu de données : on regarde 40 sous-groupes et on rapporte celui qui sort (« les femmes de 25 à 34 ans achètent plus le jeudi »).

**Les corrections classiques.** On teste $m$ hypothèses nulles, avec les p-valeurs $p_1,\dots,p_m$.

- **Bonferroni** : on rejette $H_i$ si $p_i<\alpha/m$. Simple, très prudent (le **FWER**, probabilité d'au moins un faux positif, reste ≤ $\alpha$) mais il perd beaucoup de puissance quand $m$ est grand.
- **Holm** : trie les p-valeurs et applique des seuils $\alpha/m,\ \alpha/(m-1),\dots$ ; **toujours** au moins aussi puissant que Bonferroni, avec la même garantie. À préférer.
- **Benjamini–Hochberg (BH)** : contrôle non plus le risque d'*un seul* faux positif, mais la **proportion de fausses découvertes** parmi les rejets (le **FDR**, *false discovery rate*). Moins strict, beaucoup plus puissant. Idéal en exploration (criblage de centaines de variables).

> 📐 **Procédure de Benjamini–Hochberg.** Trier les p-valeurs : $p_{(1)}\le\dots\le p_{(m)}$. Trouver le plus grand $k$ tel que $p_{(k)}\le\dfrac km\,\alpha$. Rejeter les hypothèses correspondant à $p_{(1)},\dots,p_{(k)}$.

Mettons-les à l'épreuve dans une simulation réaliste : Yasmine compare 100 catégories de produits entre deux périodes. Parmi elles, **10** ont vraiment changé (effet $d=1$) et **90** n'ont pas bougé. Chaque comparaison utilise 40 observations par période.

```python
rng = np.random.default_rng(5)
m_tests, n_vrais, n_obs = 100, 10, 40
vraie_diff = np.array([1.0] * n_vrais + [0.0] * (m_tests - n_vrais))
pvals = np.array([stats.ttest_ind(rng.normal(d, 1, n_obs), rng.normal(0, 1, n_obs)).pvalue for d in vraie_diff])

def bonferroni(p, alpha=0.05):
    return p < alpha / len(p)

def holm(p, alpha=0.05):
    ordre = np.argsort(p)
    rejet = np.zeros(len(p), dtype=bool)
    for rang, idx in enumerate(ordre):
        if p[idx] < alpha / (len(p) - rang):
            rejet[idx] = True
        else:
            break
    return rejet

def benjamini_hochberg(p, alpha=0.05):
    m = len(p)
    ordre = np.argsort(p)
    seuils = (np.arange(1, m + 1) / m) * alpha
    ok = p[ordre] <= seuils
    rejet = np.zeros(m, dtype=bool)
    if ok.any():
        k = np.max(np.where(ok)[0])
        rejet[ordre[: k + 1]] = True
    return rejet

vrai = vraie_diff > 0
for nom, rejet in [("aucune correction (p < 0,05)", pvals < 0.05), ("Bonferroni", bonferroni(pvals)),
                   ("Holm", holm(pvals)), ("Benjamini-Hochberg", benjamini_hochberg(pvals))]:
    tp, fp = int((rejet & vrai).sum()), int((rejet & ~vrai).sum())
    print(f"{nom:<30} découvertes = {tp + fp:>2}   vraies = {tp:>2}   fausses = {fp:>2}")
```
<!--sortie-->
```text
aucune correction (p < 0,05)   découvertes = 12   vraies =  9   fausses =  3
Bonferroni                     découvertes =  7   vraies =  7   fausses =  0
Holm                           découvertes =  7   vraies =  7   fausses =  0
Benjamini-Hochberg             découvertes =  9   vraies =  9   fausses =  0
```

Lecture (pour cette graine) : sans correction, on « découvre » 12 effets, dont **3 sont de fausses alertes** (sur 90 hypothèses nulles, on s'attend à environ 4,5 faux positifs à 5 %). Bonferroni et Holm n'en gardent que 7, **tous vrais**, mais au prix d'avoir **raté** 3 vrais effets. Benjamini-Hochberg en retrouve 9 vrais sans aucun faux ici ; par construction, il garantit seulement qu'en moyenne la part de fausses découvertes reste sous 5 %. Le compromis est net : plus on corrige strictement, moins on se trompe, mais plus on rate de vrais effets.

> ✅ **Quel choix pratique ?**
> - Décision importante, peu d'hypothèses, un faux positif coûteux (lancer un produit, un traitement) : **Holm** (ou Bonferroni).
> - Exploration de nombreuses hypothèses, où l'on vérifiera ensuite les candidats : **Benjamini-Hochberg**.
> - Le mieux de tout : **décider à l'avance** de la ou des questions testées. Une analyse exploratoire est une source d'hypothèses, pas une preuve.

### 3.5.6 Les bonnes pratiques, en dix lignes

1. Écrire $H_0$, $H_1$, $\alpha$ et le plan d'analyse **avant** de regarder les données.
2. Dimensionner l'échantillon pour une puissance d'au moins 80 %.
3. Ne pas s'arrêter dès que $p<0{,}05$ (*peeking*).
4. Compter **tous** les tests effectués, pas seulement ceux qui « marchent », et corriger si nécessaire.
5. Rapporter la **taille d'effet** et un **intervalle de confiance**, pas seulement la p-valeur.
6. Distinguer significativité statistique et importance pratique.
7. Ne pas dire « accepter $H_0$ » : dire « pas de preuve suffisante ».
8. Se méfier d'un résultat « juste significatif » (0,04) : il est fragile.
9. Marquer clairement ce qui est **exploratoire** et ce qui est **confirmatoire**.
10. Refaire l'expérience si la décision est importante : la **réplication** est la meilleure preuve.

> ✅ **À retenir (p-valeurs, puissance, tests multiples).**
>
> - $p=P(\text{données aussi extrêmes}\mid H_0)$. Sous $H_0$, elle est **uniforme** sur $[0,1]$ ; 5 % des tests donnent $p<0{,}05$ par hasard.
> - Ce n'est ni $P(H_0\mid\text{données})$, ni la taille de l'effet. Le taux de fausses découvertes dépend de la proportion d'hypothèses vraies (Bayes).
> - **Puissance** $=1-\beta$ : dépend de l'effet, de $n$, de la dispersion et de $\alpha$. Dimensionner avant l'expérience : $n\propto1/\text{effet}^2$.
> - **Tests multiples** : $1-(1-\alpha)^m$ ; corriger par **Holm** (FWER) ou **Benjamini-Hochberg** (FDR). Pas de *peeking*, pas de *p-hacking*.


## 3.6 ➕ Pour aller plus loin : les sondages et l'échantillonnage

> 🧭 **Section optionnelle.** Tout ce chapitre suppose que l'échantillon est « tiré au hasard dans la population ». Mais **comment** l'obtient-on, et que se passe-t-il quand ce n'est pas le cas ? La théorie des sondages répond à ces questions, essentielles pour une enquête de satisfaction, une étude de marché, ou tout jeu de données dont on ne maîtrise pas la collecte.

### 3.6.1 Le biais de sélection : le pire ennemi

> 💡 **Une leçon historique.** En 1936, le magazine *Literary Digest* prédit la défaite de Roosevelt à l'élection américaine, d'après plus de **2 millions** de réponses reçues à son questionnaire. Roosevelt a été réélu largement. Au même moment, le tout jeune institut Gallup, avec un échantillon de quelques milliers de personnes seulement mais mieux choisi, avait prévu la victoire. Le magazine avait sollicité ses abonnés, des annuaires et des propriétaires de voitures : des personnes **plus aisées que la moyenne** des électeurs. Aucune quantité de données ne corrige un échantillon qui **ne représente pas** la population.

C'est la leçon centrale de cette section : **la taille de l'échantillon réduit la variance, pas le biais.** Un million d'observations mal choisies donne un résultat précis… et faux.

Les formes de biais les plus courantes :

| Biais | Mécanisme | Exemple chez Dar Jasmin |
|---|---|---|
| **Sélection** | la méthode de recrutement favorise certains profils | enquête par e-mail : seuls les clients déjà inscrits à la newsletter répondent |
| **Non-réponse** | les répondants diffèrent des non-répondants | seuls les clients très contents (ou très fâchés) répondent |
| **Survie** | on n'observe que ceux « qui restent » | analyser uniquement les clients encore actifs surestime la satisfaction |
| **Couverture** | une partie de la population n'est pas dans la base | un sondage en ligne ignore les clients sans accès à Internet |

### 3.6.2 L'échantillonnage aléatoire simple

Dans un **échantillon aléatoire simple** (EAS), chaque individu de la base de sondage a la **même probabilité** d'être choisi, et tous les groupes de $n$ individus sont également probables. C'est le modèle de tout ce que nous avons fait. L'estimateur de la moyenne est $\bar x$ ; quand on tire **sans remise** dans une population de taille finie $N$, l'erreur-type est corrigée par le **facteur de population finie** :

$$\operatorname{SE}(\bar x)=\frac{\sigma}{\sqrt n}\sqrt{1-\frac nN}.$$

Si l'on interroge une grande part de la population ($n/N$ non négligeable), l'incertitude diminue plus vite. Si $n\ll N$ (le cas habituel), le facteur vaut presque 1 : **ce qui compte, c'est $n$, pas la fraction interrogée**. Voilà pourquoi sonder 1 000 personnes suffit autant pour un pays de 10 millions d'habitants que pour une ville de 100 000.

**La marge d'erreur d'un sondage.** Pour une proportion estimée à $\hat p$ avec $n$ personnes, la marge d'erreur à 95 % est $1{,}96\sqrt{\hat p(1-\hat p)/n}$. Son maximum est atteint pour $\hat p=0{,}5$, ce qui donne la **règle à retenir** : $\text{marge}\approx\dfrac{1}{\sqrt n}$.

```python
import numpy as np
from scipy import stats

for n_s in (100, 400, 1000, 2500, 10000):
    marge = 1.96 * np.sqrt(0.25 / n_s)
    print(f"n = {n_s:>6} : marge d'erreur maximale = ±{marge * 100:.1f} points   (règle 1/sqrt(n) = ±{100 / np.sqrt(n_s):.1f})")
```
<!--sortie-->
```text
n =    100 : marge d'erreur maximale = ±9.8 points   (règle 1/sqrt(n) = ±10.0)
n =    400 : marge d'erreur maximale = ±4.9 points   (règle 1/sqrt(n) = ±5.0)
n =   1000 : marge d'erreur maximale = ±3.1 points   (règle 1/sqrt(n) = ±3.2)
n =   2500 : marge d'erreur maximale = ±2.0 points   (règle 1/sqrt(n) = ±2.0)
n =  10000 : marge d'erreur maximale = ±1.0 points   (règle 1/sqrt(n) = ±1.0)
```

Avec 1 000 personnes : ±3,1 points. Pour obtenir ±1 point, il en faut près de 10 000. C'est pourquoi les sondages nationaux s'arrêtent le plus souvent autour de 1 000 à 2 000 personnes. Et cette marge ne couvre que **l'erreur d'échantillonnage** : elle ne dit rien du biais de sélection ou de non-réponse, qui sont souvent plus grands.

### 3.6.3 L'échantillonnage stratifié

> 💡 **Intuition.** Si la population est composée de groupes **homogènes en eux-mêmes mais différents entre eux** (les canaux de vente !), il est dommage de laisser le hasard décider combien de chaque groupe tombera dans l'échantillon. On **découpe** la population en **strates** et on tire un échantillon aléatoire **dans chaque strate**, en proportion de sa taille. On garantit ainsi une représentation fidèle, et l'on gagne en précision.

**L'estimateur stratifié** pondère les moyennes de strates par leur poids dans la population : $\bar x_{\text{strat}}=\sum_h W_h\bar x_h$ avec $W_h=N_h/N$.

Montrons le gain par simulation. La base clients de Dar Jasmin compte 10 000 personnes réparties en trois canaux, dont les dépenses moyennes diffèrent nettement :

```python
rng = np.random.default_rng(50)
tailles = {"Instagram": 4000, "Site": 3500, "Boutique": 2500}
base = {"Instagram": 3.7, "Site": 3.9, "Boutique": 4.1}
canaux_pop = np.concatenate([[c] * n for c, n in tailles.items()])
depenses_pop = np.concatenate([np.exp(rng.normal(base[c], 0.55, size=n)) for c, n in tailles.items()])
N = len(depenses_pop)
vraie_moyenne = depenses_pop.mean()
print("taille de la population :", N, "   vraie dépense moyenne :", round(vraie_moyenne, 2), "DT")

n_ech, essais = 200, 5000
est_eas, est_strat = [], []
masques = {c: canaux_pop == c for c in tailles}
poids = {c: tailles[c] / N for c in tailles}
for _ in range(essais):
    # EAS : 200 clients au hasard dans toute la base
    est_eas.append(rng.choice(depenses_pop, size=n_ech, replace=False).mean())
    # stratifié proportionnel : 80 Instagram, 70 Site, 50 Boutique
    moy = 0
    for c in tailles:
        n_h = int(round(n_ech * poids[c]))
        moy += poids[c] * rng.choice(depenses_pop[masques[c]], size=n_h, replace=False).mean()
    est_strat.append(moy)

print("EAS         : moyenne =", round(np.mean(est_eas), 2), "  erreur-type =", round(np.std(est_eas), 2))
print("Stratifié   : moyenne =", round(np.mean(est_strat), 2), "  erreur-type =", round(np.std(est_strat), 2))
print("gain de variance :", round(1 - np.var(est_strat) / np.var(est_eas), 3))
```
<!--sortie-->
```text
taille de la population : 10000    vraie dépense moyenne : 56.4 DT
EAS         : moyenne = 56.39   erreur-type = 2.46
Stratifié   : moyenne = 56.39   erreur-type = 2.36
gain de variance : 0.081
```

Les deux estimateurs sont **sans biais** (leur moyenne tombe sur la vraie valeur), mais l'estimateur stratifié est **plus précis** : son erreur-type (2,36 DT) est inférieure d'environ 4 % à celle de l'EAS (2,46 DT), soit 8 % de variance en moins. Le gain est modeste ici car les différences entre canaux, bien que réelles, restent petites comparées à la dispersion *à l'intérieur* de chaque canal. Il serait bien plus grand si les strates étaient très différentes entre elles.

> 📐 **Pourquoi ça marche : décomposition de la variance.** La variance totale se décompose en variance **entre** strates et variance **à l'intérieur** des strates : $\sigma^2=\sigma^2_{\text{entre}}+\sigma^2_{\text{intra}}$. Dans un EAS, le hasard de la composition de l'échantillon introduit l'incertitude liée à la variance *entre* strates. La stratification **fixe** cette composition, et seule la variance *intra* demeure : l'erreur-type diminue exactement de la part « entre ».

**L'allocation de Neyman.** On peut aller plus loin : au lieu d'allouer proportionnellement à la taille, on interroge **davantage** les strates **plus hétérogènes** (de grand écart-type) : $n_h\propto N_h\sigma_h$. Ici, la boutique est la plus dispersée (écart-type de ses dépenses plus élevé en valeur absolue) : on gagnerait à en sur-échantillonner un peu.

### 3.6.4 Autres plans de sondage

| Plan | Principe | Avantage | Inconvénient |
|---|---|---|---|
| **Systématique** | un individu tous les $k$ dans la liste | simple | biais si la liste a une périodicité |
| **Par grappes** | on tire des groupes entiers (magasins, classes) puis on interroge tout le groupe | peu coûteux (déplacements) | moins précis (individus d'une grappe se ressemblent) |
| **À plusieurs degrés** | tirage de grappes puis d'individus dans les grappes | pratique pour de vastes populations | calcul d'erreur plus complexe |
| **Par quotas** | on remplit des quotas (âge, sexe…) sans tirage aléatoire | rapide, peu coûteux | pas de théorie d'erreur rigoureuse |
| **De convenance** | on prend ceux qui sont disponibles | très facile | **biais incontrôlable** |

Les plans aléatoires (EAS, stratifié, grappes) permettent de **quantifier** l'incertitude ; les plans de quotas ou de convenance non. C'est une raison de plus de se méfier des « sondages » de réseaux sociaux.

### 3.6.5 Redresser un échantillon biaisé : la pondération

On ne choisit pas toujours son échantillon. Yasmine envoie un questionnaire de satisfaction à tous ses clients ; les **réponses sont inégalement réparties** : les clients de la boutique répondent très peu (ils ne laissent pas d'e-mail), ceux d'Instagram beaucoup. Parmi les 300 réponses : 150 d'Instagram, 120 du site et 30 de la boutique, alors que la clientèle réelle est répartie en 40 % / 35 % / 25 %.

Si l'on moyenne naïvement les 300 réponses, la boutique est **sous-représentée** (10 % au lieu de 25 %). Or les clients de la boutique sont aussi les plus satisfaits : on **sous-estime** donc la satisfaction globale. La solution est de **pondérer** chaque réponse par $w=\dfrac{\text{part dans la population}}{\text{part dans l'échantillon}}$ (une *post-stratification*).

```python
satisf_vraie = {"Instagram": 0.63, "Site": 0.70, "Boutique": 0.96}   # taux de satisfaits par canal (3.4.6)
pop_part = {"Instagram": 0.40, "Site": 0.35, "Boutique": 0.25}
rep = {"Instagram": 150, "Site": 120, "Boutique": 30}
n_rep = sum(rep.values())

naif = sum(rep[c] * satisf_vraie[c] for c in rep) / n_rep
poids_c = {c: pop_part[c] / (rep[c] / n_rep) for c in rep}
pondere = sum(rep[c] * poids_c[c] * satisf_vraie[c] for c in rep) / sum(rep[c] * poids_c[c] for c in rep)
vrai = sum(pop_part[c] * satisf_vraie[c] for c in pop_part)

print("poids :", {c: round(w, 2) for c, w in poids_c.items()})
print("satisfaction vraie (population) :", round(vrai, 3))
print("estimation naïve                :", round(naif, 3))
print("estimation pondérée             :", round(pondere, 3))
```
<!--sortie-->
```text
poids : {'Instagram': 0.8, 'Site': 0.87, 'Boutique': 2.5}
satisfaction vraie (population) : 0.737
estimation naïve                : 0.691
estimation pondérée             : 0.737
```

La moyenne naïve (environ 69 %) sous-estime la vraie valeur (73,7 %) ; la pondération corrige l'erreur. Chaque réponse de la boutique « compte pour » 2,5 réponses (poids 2,5) et chaque réponse d'Instagram pour 0,8. (Cette correction n'est valable que si, **à l'intérieur de chaque canal**, répondants et non-répondants sont comparables : la pondération redresse les déséquilibres **observables**, pas ceux que l'on ne mesure pas.)

> ✅ **À retenir (sondages).**
>
> - **La taille ne corrige pas le biais** (*Literary Digest*) ; ce qui compte, c'est la qualité du tirage.
> - EAS : marge d'erreur $\approx1/\sqrt n$ (±3 points pour 1 000 personnes), indépendante de la taille de la population si elle est grande.
> - **Stratification** : on tire dans chaque groupe, en proportion ; estimateur $\sum W_h\bar x_h$, plus précis que l'EAS quand les strates diffèrent.
> - Plans par grappes, de quotas, de convenance : moins précis ou sans théorie d'erreur.
> - On redresse un échantillon déséquilibré par **pondération** ($w=$ part population / part échantillon), sous réserve de comparabilité à l'intérieur des groupes.


## 3.7 ➕ Pour aller plus loin : les méthodes non paramétriques

> 🧭 **Section optionnelle.** Les tests du 3.4 (Student, Welch) supposent, au moins approximativement, une loi normale des moyennes. Les méthodes **non paramétriques** (ou *sans loi*) évitent de postuler une forme de distribution. Elles sont précieuses pour de petits échantillons, des variables ordinales (notes de 1 à 5) ou des données très asymétriques et pleines de valeurs extrêmes.

### 3.7.1 Remplacer les valeurs par leurs rangs

> 💡 **Intuition.** Au lieu de travailler sur les valeurs, on les **range** du plus petit au plus grand et l'on travaille sur leurs **rangs** (1er, 2e, 3e…). Une valeur extrême de 1 000 000 n'a que le rang « dernier » : elle ne peut plus fausser le résultat. Les rangs perdent un peu d'information (l'ampleur des écarts), mais gagnent une **robustesse** considérable.

```python
import numpy as np
import pandas as pd
from scipy import stats

x = np.array([12, 15, 14, 10, 13, 40])     # un client a dépensé 40 : valeur extrême
print("valeurs :", x)
print("rangs   :", stats.rankdata(x))
```
<!--sortie-->
```text
valeurs : [12 15 14 10 13 40]
rangs   : [2. 5. 4. 1. 3. 6.]
```

L'extrême (40) reçoit simplement le rang 6, le même qu'il aurait eu en valant 16.

### 3.7.2 Le test de Mann-Whitney (deux groupes indépendants)

C'est l'équivalent non paramétrique du test de Welch. On mélange les deux groupes, on range toutes les valeurs, puis on regarde si les rangs d'un groupe sont systématiquement plus élevés que ceux de l'autre.

> 💡 **Interprétation très parlante.** La statistique $U/(n_1n_2)$ est la probabilité qu'une observation tirée au hasard dans le groupe A **dépasse** une observation tirée au hasard dans le groupe B. Valeur 0,5 : aucune différence ; proche de 1 : A domine B. (C'est aussi l'**AUC** du volume II.)

**Un cas où le test de Student se trompe.** Deux petits groupes de 6 commandes. Dans le premier, un client dépense une somme exceptionnelle :

```python
ga = np.array([12, 15, 14, 10, 13, 40])
gb = np.array([9, 8, 11, 10, 7, 12])
print("moyennes :", ga.mean().round(1), gb.mean().round(1))
print("Welch          : p =", round(stats.ttest_ind(ga, gb, equal_var=False).pvalue, 3))
print("Mann-Whitney   : p =", round(stats.mannwhitneyu(ga, gb).pvalue, 3))
```
<!--sortie-->
```text
moyennes : 17.3 9.5
Welch          : p = 0.15
Mann-Whitney   : p = 0.02
```

Presque **tous** les clients du premier groupe dépensent plus que ceux du second ; seul le cas de 40 gonfle la variance et noie l'effet dans le test de Student ($p\approx0{,}15$, non significatif). Le test de Mann-Whitney, lui, voit la domination systématique du groupe A ($p\approx0{,}02$, significatif). C'est le gain de puissance de la robustesse quand les données sont « sales ».

**Sur nos 400 commandes** (boutique contre Instagram) :

```python
b = df.loc[df["canal"] == "Boutique", "montant"]
i = df.loc[df["canal"] == "Instagram", "montant"]
u = stats.mannwhitneyu(b, i, alternative="two-sided")
print("U =", u.statistic, "  p-valeur =", u.pvalue)
print("P(commande boutique > commande Instagram) =", round(u.statistic / (len(b) * len(i)), 3))
```
<!--sortie-->
```text
U = 11246.0   p-valeur = 4.410098845865466e-09
P(commande boutique > commande Instagram) = 0.715
```

Une commande de la boutique dépasse une commande d'Instagram dans 71 % des paires comparées ($p\approx4\times10^{-9}$). Conclusion identique à celle du test de Welch, avec une interprétation plus intuitive.

### 3.7.3 Autres tests de rangs

| Situation | Test paramétrique | Équivalent non paramétrique |
|---|---|---|
| 2 groupes indépendants | Welch | **Mann-Whitney** (`mannwhitneyu`) |
| 2 séries appariées | Student apparié | **Wilcoxon** des rangs signés (`wilcoxon`) |
| $k>2$ groupes | ANOVA (`f_oneway`) | **Kruskal-Wallis** (`kruskal`) |
| Corrélation | Pearson | **Spearman** / **Kendall** (`spearmanr`, `kendalltau`) |

```python
# Wilcoxon : les 8 colis avant/après du 3.4.3
avant = np.array([5, 4, 6, 7, 5, 6, 8, 5])
apres = np.array([4, 4, 5, 6, 5, 5, 6, 4])
print("Wilcoxon apparié :", round(stats.wilcoxon(avant, apres).pvalue, 4))

# Kruskal-Wallis : les trois canaux ensemble
groupes = [df.loc[df["canal"] == c, "montant"] for c in ["Instagram", "Site", "Boutique"]]
print("ANOVA          : p =", f"{stats.f_oneway(*groupes).pvalue:.1e}")
print("Kruskal-Wallis : p =", f"{stats.kruskal(*groupes).pvalue:.1e}")

# Corrélation entre le délai et la satisfaction (variable ordinale)
print("Pearson  :", np.round(stats.pearsonr(df["livraison"], df["satisfaction"]), 3))
print("Spearman :", np.round(stats.spearmanr(df["livraison"], df["satisfaction"]), 3))
print("Kendall  :", np.round(stats.kendalltau(df["livraison"], df["satisfaction"]), 3))
```
<!--sortie-->
```text
Wilcoxon apparié : 0.0312
ANOVA          : p = 3.4e-07
Kruskal-Wallis : p = 9.4e-09
Pearson  : [-0.532  0.   ]
Spearman : [-0.511  0.   ]
Kendall  : [-0.437  0.   ]
```

Les lignes de corrélation donnent (coefficient, p-valeur) ; la p-valeur arrondie vaut 0. Pour la satisfaction (note de 1 à 5, **ordinale**), Spearman et Kendall sont plus appropriés que Pearson. Dans les trois cas, le lien entre délai et satisfaction est très significatif.

> ✅ **Quand choisir le non paramétrique ?** Données ordinales ; petits échantillons ($n<20$) d'allure non normale ; valeurs extrêmes qu'on ne veut pas supprimer. Si les données sont vraiment normales, le test de Student est un peu plus puissant (de l'ordre de 5 %) : le non paramétrique est une **assurance bon marché**.

### 3.7.4 Les tests de permutation : l'idée la plus simple de la statistique

> 💡 **Intuition.** $H_0$ dit : « le canal n'a aucun effet sur le montant ». Si c'est vrai, l'étiquette « boutique » ou « Instagram » collée sur une commande est **arbitraire** : on aurait pu l'échanger avec n'importe quelle autre. Alors **mélangeons** les étiquettes au hasard, recalculons la différence de moyennes, et recommençons des milliers de fois. On obtient ainsi la **distribution de la différence quand $H_0$ est vraie**, sans aucune hypothèse de loi. La p-valeur est la fréquence des mélanges qui donnent une différence au moins aussi grande que celle observée.

```python
rng = np.random.default_rng(12)
valeurs = np.concatenate([b.to_numpy(), i.to_numpy()])
n_b = len(b)
diff_obs = b.mean() - i.mean()

n_perm = 20_000
diffs = np.empty(n_perm)
for k in range(n_perm):
    melange = rng.permutation(valeurs)
    diffs[k] = melange[:n_b].mean() - melange[n_b:].mean()

p_perm = (np.sum(np.abs(diffs) >= abs(diff_obs)) + 1) / (n_perm + 1)
print("différence observée :", round(diff_obs, 2), "DT")
print("plus grande différence parmi les 20 000 mélanges :", round(np.abs(diffs).max(), 2), "DT")
print("p-valeur de permutation :", p_perm)
```
<!--sortie-->
```text
différence observée : 25.8 DT
plus grande différence parmi les 20 000 mélanges : 20.58 DT
p-valeur de permutation : 4.999750012499375e-05
```

Aucun des 20 000 mélanges n'atteint la différence observée de 25,8 DT : la différence maximale obtenue par hasard est bien plus petite. On majore donc la p-valeur par $1/20\,001\approx5\times10^{-5}$ (le « +1 » évite de déclarer p = 0). Faisons maintenant la même chose sur la petite expérience à 6 + 6 commandes, où l'on peut même énumérer toutes les permutations possibles :

```python
from itertools import combinations
tout = np.concatenate([ga, gb])
obs = tout[:6].mean() - tout[6:].mean()
n_plus_extreme, total = 0, 0
for idx in combinations(range(12), 6):                 # les 924 façons de choisir 6 commandes sur 12
    masque = np.zeros(12, dtype=bool)
    masque[list(idx)] = True
    d = tout[masque].mean() - tout[~masque].mean()
    n_plus_extreme += abs(d) >= abs(obs) - 1e-12
    total += 1
print("nombre de permutations :", total)
print("p-valeur exacte de permutation :", round(n_plus_extreme / total, 4))
```
<!--sortie-->
```text
nombre de permutations : 924
p-valeur exacte de permutation : 0.0173
```

Il y a $\binom{12}{6}=924$ manières de répartir les 12 valeurs en deux groupes (clin d'œil au 1.6 !) ; la p-valeur est la proportion de ces 924 répartitions dont l'écart de moyennes est au moins aussi grand que celui observé. Le test est **exact** et n'a besoin d'aucune hypothèse. Il est très souple : on peut l'appliquer à **n'importe quelle statistique** (médiane, rapport, corrélation), comme le bootstrap.

### 3.7.5 Tester la normalité

Comment savoir si l'hypothèse de normalité du test de Student est raisonnable ? Deux outils.

**Le diagramme quantile-quantile (QQ-plot)** : on compare les quantiles des données à ceux d'une loi normale ; si les points suivent la droite, c'est normal. **Le test de Shapiro-Wilk** : $H_0$ = « les données sont normales ».

```python
print("Shapiro-Wilk sur le montant      : p =", f"{stats.shapiro(df['montant']).pvalue:.1e}")
print("Shapiro-Wilk sur log(montant)    : p =", round(stats.shapiro(np.log(df["montant"])).pvalue, 3))
z = stats.zscore(np.log(df["montant"]))
print("Kolmogorov-Smirnov (log, normal) : p =", round(stats.kstest(z, "norm").pvalue, 3))
```
<!--sortie-->
```text
Shapiro-Wilk sur le montant      : p = 3.0e-18
Shapiro-Wilk sur log(montant)    : p = 0.846
Kolmogorov-Smirnov (log, normal) : p = 0.879
```

Le montant brut est **clairement non normal** ($p\approx10^{-18}$), alors que son logarithme est tout à fait compatible avec la normalité (pas de rejet : $p\approx0{,}85$), ce qui confirme la structure **log-normale** vue au 3.1.5. Le **test de Kolmogorov-Smirnov** compare la fonction de répartition observée à celle d'une loi donnée (ou deux échantillons entre eux).

> ⚠️ **Piège : tester la normalité n'est pas toujours utile.** Avec beaucoup de données, ces tests rejettent la normalité pour des écarts infimes sans conséquence ; avec peu de données, ils ne détectent rien. On s'appuie surtout sur les **graphiques** et sur le **TCL** : la normalité de la **moyenne** (ce qui compte pour Student) est assurée dès que $n$ est grand, même si les données ne sont pas normales.

> ✅ **À retenir (non paramétrique).**
>
> - Travailler sur les **rangs** rend robuste aux valeurs extrêmes et applicable aux données ordinales.
> - **Mann-Whitney** (2 groupes), **Wilcoxon** (apparié), **Kruskal-Wallis** ($k$ groupes), **Spearman/Kendall** (corrélation).
> - **Test de permutation** : on mélange les étiquettes pour fabriquer la loi de la statistique sous $H_0$ ; valable pour toute statistique.
> - **Shapiro-Wilk** et **Kolmogorov-Smirnov** testent une loi, mais préférez les graphiques et le TCL.


## 3.8 Exercices du chapitre 3

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse.

### Énoncés

**Exercice 1 ⭐ (descriptif).** Huit commandes en DT : $12,\,15,\,15,\,18,\,20,\,22,\,25,\,60$. Calculez la moyenne, la médiane, le mode, l'écart-type (avec $n-1$) et l'écart interquartile. Quelle mesure de position est la plus représentative, et pourquoi ?

**Exercice 2 ⭐ (variance sans biais).** Un échantillon de 5 délais de livraison : $4,\,8,\,6,\,5,\,7$ jours. Calculez la variance en divisant par $n$ puis par $n-1$. Laquelle utiliser pour estimer la variance de **tous** les délais ?

**Exercice 3 ⭐⭐ (maximum de vraisemblance).** Le nombre de commandes par heure a été relevé 8 fois : $2,\,3,\,1,\,4,\,0,\,3,\,2,\,5$. On modélise par une loi de Poisson$(\lambda)$. (a) Écrivez la log-vraisemblance et trouvez $\hat\lambda$ en dérivant. (b) Avec cette estimation, quelle est la probabilité de ne recevoir aucune commande pendant une heure ?

**Exercice 4 ⭐ (IC d'une moyenne).** Sur $n=36$ commandes : $\bar x=52$ DT, $s=12$ DT. Donnez un intervalle de confiance à 95 % de la moyenne, puis à 99 %. Quelle est la signification du « 95 % » ?

**Exercice 5 ⭐⭐ (IC d'une proportion).** Un questionnaire envoyé à 60 clients donne 18 « très satisfaits ». Calculez l'IC à 95 % de la vraie proportion par la méthode de Wald et par celle de Wilson. Pourquoi sont-ils différents ?

**Exercice 6 ⭐⭐ (test sur une moyenne).** Le transporteur promet un délai moyen de 3 jours. Sur 25 colis, on mesure en moyenne 3,6 jours avec un écart-type de 1,5 jour. (a) Testez $H_0:\mu=3$ contre $H_1:\mu\neq3$ à 5 %. (b) Que change un test unilatéral $H_1:\mu>3$ ? (c) Peut-on dire que le transporteur respecte sa promesse ?

**Exercice 7 ⭐⭐ (test A/B).** Version A : 45 achats sur 500 visiteurs. Version B : 66 achats sur 500 visiteurs. (a) B est-elle meilleure, à 5 % ? (b) Donnez un IC de la différence. (c) Quelle était la puissance de ce test si le vrai écart est celui observé ?

**Exercice 8 ⭐⭐ (khi-deux).** Parmi 100 clients ayant reçu un code promo, 30 ont acheté ; parmi 100 clients sans code, 45 ont acheté. Le code a-t-il un effet ? Construisez le tableau, calculez les effectifs attendus et le test du khi-deux. Comparez avec le test de deux proportions.

**Exercice 9 ⭐⭐⭐ (taille d'échantillon).** Le taux de conversion actuel est de 20 %. Yasmine veut détecter une hausse à 24 % avec une puissance de 80 % et $\alpha=5\,\%$. (a) Combien de visiteurs par version ? (b) Et pour détecter 22 % ? (c) Expliquez le rapport entre les deux résultats.

**Exercice 10 ⭐⭐⭐ (tests multiples).** Un analyste teste 8 hypothèses et obtient les p-valeurs $0{,}001;\ 0{,}008;\ 0{,}012;\ 0{,}030;\ 0{,}040;\ 0{,}200;\ 0{,}500;\ 0{,}700$. Lesquelles sont rejetées à 5 % (a) sans correction, (b) avec Bonferroni, (c) avec Holm, (d) avec Benjamini-Hochberg ?

### Corrigés

**Corrigé 1.** Moyenne : $187/8=23{,}375$. Triées : $12,15,15,18,20,22,25,60$ : la médiane est $(18+20)/2=19$. Mode : 15. Écart-type ($n-1$) : voir le code (≈ 15,4). Les quartiles (méthode de NumPy) donnent un IQR de 7,75. La **médiane** (19) est la plus représentative : la moyenne (23,4) est tirée vers le haut par la commande de 60 DT (valeur extrême), qui est supérieure de plus du double au reste.

```python
import numpy as np
from scipy import stats
x = np.array([12, 15, 15, 18, 20, 22, 25, 60])
print("moyenne :", x.mean(), " médiane :", np.median(x), " mode :", stats.mode(x).mode)
print("écart-type (n-1) :", round(x.std(ddof=1), 2))
print("IQR :", np.percentile(x, 75) - np.percentile(x, 25))
```
<!--sortie-->
```text
moyenne : 23.375  médiane : 19.0  mode : 15
écart-type (n-1) : 15.38
IQR : 7.75
```

**Corrigé 2.** $\bar x=6$ ; écarts : $-2,2,0,-1,1$ ; carrés : $4,4,0,1,1$ ; somme $=10$. Division par $n$ : $10/5=2$. Division par $n-1$ : $10/4=2{,}5$. Pour estimer la variance de la **population**, on utilise $n-1$ (estimateur sans biais, 3.2.3).

```python
d = np.array([4, 8, 6, 5, 7])
print("var (n)   :", d.var(ddof=0), "   var (n-1) :", d.var(ddof=1))
```
<!--sortie-->
```text
var (n)   : 2.0    var (n-1) : 2.5
```

**Corrigé 3.** (a) $\ell(\lambda)=\sum_i\bigl(-\lambda+x_i\ln\lambda-\ln x_i!\bigr)=-n\lambda+\ln\lambda\sum x_i-\sum\ln x_i!$. $\ell'(\lambda)=-n+\dfrac{\sum x_i}{\lambda}=0\Rightarrow\hat\lambda=\bar x=\dfrac{20}8=2{,}5$ (c'est un maximum car $\ell''=-\sum x_i/\lambda^2<0$). (b) $P(N=0)=e^{-2{,}5}\approx0{,}082$.

```python
x = np.array([2, 3, 1, 4, 0, 3, 2, 5])
lam = x.mean()
print("lambda chapeau =", lam, "  P(0 commande) =", round(np.exp(-lam), 4))
grille = np.linspace(0.5, 6, 1101)
print("maximum sur grille :", round(grille[np.argmax([stats.poisson.logpmf(x, g).sum() for g in grille])], 2))
```
<!--sortie-->
```text
lambda chapeau = 2.5   P(0 commande) = 0.0821
maximum sur grille : 2.5
```

**Corrigé 4.** Erreur-type : $12/\sqrt{36}=2$. Valeur critique de Student à 35 ddl : 2,030 (95 %) et 2,724 (99 %). IC 95 % : $52\pm2{,}030\times2=[47{,}9\,;\,56{,}1]$. IC 99 % : $52\pm2{,}724\times2=[46{,}6\,;\,57{,}4]$ (plus large : plus de confiance coûte en précision). « 95 % » : si l'on répétait l'enquête de nombreuses fois, environ 95 % des intervalles ainsi construits contiendraient la vraie moyenne.

```python
n, xbar, s = 36, 52, 12
se = s / np.sqrt(n)
for niveau in (0.95, 0.99):
    t = stats.t.ppf(1 - (1 - niveau) / 2, n - 1)
    print(f"{niveau:.0%} : t = {t:.3f}   IC = [{xbar - t * se:.1f} ; {xbar + t * se:.1f}]")
```
<!--sortie-->
```text
95% : t = 2.030   IC = [47.9 ; 56.1]
99% : t = 2.724   IC = [46.6 ; 57.4]
```

**Corrigé 5.** $\hat p=18/60=0{,}30$. Wald : erreur-type $\sqrt{0{,}3\times0{,}7/60}=0{,}0592$, IC $0{,}30\pm0{,}116=[0{,}184\,;\,0{,}416]$. Wilson (voir le code) donne environ $[0{,}199\,;\,0{,}425]$ : légèrement décalé vers le centre et plus large à droite. Wilson est plus fiable car il tient compte du fait que l'erreur-type dépend de $p$ lui-même, d'où une meilleure couverture pour $n$ modeste.

```python
k, n = 18, 60
p = k / n
d = 1.96 * np.sqrt(p * (1 - p) / n)
print("Wald   : [", round(p - d, 3), ";", round(p + d, 3), "]")
w = stats.binomtest(k, n).proportion_ci(confidence_level=0.95, method="wilson")
print("Wilson : [", round(w.low, 3), ";", round(w.high, 3), "]")
```
<!--sortie-->
```text
Wald   : [ 0.184 ; 0.416 ]
Wilson : [ 0.199 ; 0.425 ]
```

**Corrigé 6.** (a) $t=\dfrac{3{,}6-3}{1{,}5/\sqrt{25}}=\dfrac{0{,}6}{0{,}3}=2{,}0$ avec 24 ddl. Valeur critique bilatérale à 5 % : 2,064. Comme $2{,}0<2{,}064$ (et $p\approx0{,}057$), on **ne rejette pas** $H_0$ de justesse. (b) En unilatéral, $p\approx0{,}028<0{,}05$ : on rejette. Mais on ne peut choisir le sens du test **qu'avant** de voir les données et si l'on n'est vraiment intéressé que par un dépassement ; décider après coup serait tricher. (c) Honnêtement : les données sont **à la limite** : le retard moyen estimé est de 0,6 jour, l'IC à 95 % ($3{,}6\pm2{,}064\times0{,}3=[2{,}98\,;\,4{,}22]$) inclut 3 de justesse. On ne peut ni affirmer que la promesse est tenue, ni qu'elle ne l'est pas ; il faut davantage de colis.

```python
n, xbar, s, mu0 = 25, 3.6, 1.5, 3
t = (xbar - mu0) / (s / np.sqrt(n))
print("t =", t, "  p bilatérale =", round(2 * stats.t.sf(t, n - 1), 4), "  p unilatérale =", round(stats.t.sf(t, n - 1), 4))
tc = stats.t.ppf(0.975, n - 1)
print("IC95 % : [", round(xbar - tc * s / np.sqrt(n), 2), ";", round(xbar + tc * s / np.sqrt(n), 2), "]")
```
<!--sortie-->
```text
t = 2.0000000000000004   p bilatérale = 0.0569   p unilatérale = 0.0285
IC95 % : [ 2.98 ; 4.22 ]
```

**Corrigé 7.** (a) $\hat p_A=0{,}09$, $\hat p_B=0{,}132$, $\hat p=\frac{111}{1000}=0{,}111$. $z=\dfrac{0{,}042}{\sqrt{0{,}111\times0{,}889\times(2/500)}}=\dfrac{0{,}042}{0{,}01987}\approx2{,}11$, $p\approx0{,}035$ : significatif à 5 %. (b) Erreur-type non regroupée $\approx0{,}0194$, donc IC $=0{,}042\pm0{,}039=[0{,}003\,;\,0{,}081]$ : l'écart est positif, mais très imprécis (de 0,3 à 8 points !). (c) La puissance, si le vrai écart est celui observé, est d'environ 56 % : l'expérience était sous-dimensionnée (voir le code).

```python
kA, kB, n = 45, 66, 500
pA, pB = kA / n, kB / n
pp = (kA + kB) / (2 * n)
z = (pB - pA) / np.sqrt(pp * (1 - pp) * 2 / n)
print("z =", round(z, 3), "  p =", round(2 * stats.norm.sf(z), 4))
se = np.sqrt(pA * (1 - pA) / n + pB * (1 - pB) / n)
print("IC95 % de la différence : [", round(pB - pA - 1.96 * se, 4), ";", round(pB - pA + 1.96 * se, 4), "]")
print("puissance :", round(stats.norm.cdf((pB - pA) / se - 1.96), 3))
```
<!--sortie-->
```text
z = 2.114   p = 0.0345
IC95 % de la différence : [ 0.0031 ; 0.0809 ]
puissance : 0.563
```

**Corrigé 8.** Tableau : code promo : 30 achats, 70 non ; sans code : 45 achats, 55 non. Totaux : colonnes 75 et 125 ; lignes 100 et 100. Effectifs attendus (sous indépendance) : achats $100\times75/200=37{,}5$ dans chaque ligne ; non-achats $62{,}5$. Chaque case s'écarte de son attendu de $7{,}5$, donc $\chi^2=\sum\frac{(O-E)^2}{E}=2\times\dfrac{7{,}5^2}{37{,}5}+2\times\dfrac{7{,}5^2}{62{,}5}=3{,}0+1{,}8=4{,}8$ (sans correction de continuité), 1 ddl, $p\approx0{,}029$ (0,041 avec la correction de Yates, plus prudente). **Attention : le code promo est associé à *moins* d'achats** (30 % contre 45 %) : le test signale une différence, pas son sens. (Et le test à deux proportions donne $z^2=\chi^2$ : même $p$.)

```python
from scipy.stats import chi2_contingency
tab = np.array([[30, 70], [45, 55]])
chi2, p, ddl, att = chi2_contingency(tab, correction=False)
print("attendus :\n", att)
print("khi-deux =", round(chi2, 3), " p =", round(p, 4), " (avec correction de Yates :", round(chi2_contingency(tab)[1], 4), ")")
pp = 75 / 200
z = (0.45 - 0.30) / np.sqrt(pp * (1 - pp) * 2 / 100)
print("z =", round(z, 3), " z^2 =", round(z**2, 3), " p =", round(2 * stats.norm.sf(abs(z)), 4))
```
<!--sortie-->
```text
attendus :
 [[37.5 62.5]
 [37.5 62.5]]
khi-deux = 4.8  p = 0.0285  (avec correction de Yates : 0.0409 )
z = 2.191  z^2 = 4.8  p = 0.0285
```

**Corrigé 9.** (a) $n=\dfrac{(1{,}96+0{,}8416)^2\,[0{,}2\times0{,}8+0{,}24\times0{,}76]}{0{,}04^2}\approx1\,680$ par version. (b) Pour 22 %, l'effet est deux fois plus petit : $n\approx6\,500$. (c) Diviser l'effet par 2 multiplie $n$ par **environ 4** : $n\propto1/\text{effet}^2$.

```python
za, zb = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
def n_groupe(p1, p2):
    return (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2
print("20 -> 24 % :", int(np.ceil(n_groupe(0.20, 0.24))), "  20 -> 22 % :", int(np.ceil(n_groupe(0.20, 0.22))))
print("rapport :", round(n_groupe(0.20, 0.22) / n_groupe(0.20, 0.24), 2))
```
<!--sortie-->
```text
20 -> 24 % : 1680   20 -> 22 % : 6507
rapport : 3.87
```

**Corrigé 10.** (a) Sans correction : $p<0{,}05$ pour les 5 premières. (b) Bonferroni : seuil $0{,}05/8=0{,}00625$ : seule 0,001 est rejetée. (c) Holm : seuils $0{,}05/8=0{,}00625$, $0{,}05/7=0{,}00714$, $0{,}05/6=0{,}00833$, … : $0{,}001<0{,}00625$ ✓ ; $0{,}008>0{,}00714$ ✗ : on s'arrête. Un seul rejet, comme Bonferroni. (d) BH : seuils $\frac k8\times0{,}05$ : $0{,}00625;\ 0{,}0125;\ 0{,}01875;\ 0{,}025;\ 0{,}03125;\dots$ ; $p_{(1)}=0{,}001\le0{,}00625$ ✓, $p_{(2)}=0{,}008\le0{,}0125$ ✓, $p_{(3)}=0{,}012\le0{,}01875$ ✓, $p_{(4)}=0{,}030>0{,}025$ ✗, $p_{(5)}=0{,}040>0{,}03125$ ✗. Le plus grand $k$ qui convient est 3 : les **trois** premières sont rejetées.

```python
p = np.array([0.001, 0.008, 0.012, 0.030, 0.040, 0.200, 0.500, 0.700])
m = len(p)
print("sans correction :", int((p < 0.05).sum()), "rejets")
print("Bonferroni      :", int((p < 0.05 / m).sum()), "rejets")
rang = np.arange(1, m + 1)
holm = np.cumprod(p < 0.05 / (m - rang + 1))     # on s'arrête au premier échec
print("Holm            :", int(holm.sum()), "rejets")
ok = p <= rang / m * 0.05
print("Benjamini-Hochberg :", int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0, "rejets")
```
<!--sortie-->
```text
sans correction : 5 rejets
Bonferroni      : 1 rejets
Holm            : 1 rejets
Benjamini-Hochberg : 3 rejets
```

---

## Bilan du chapitre 3

Vous savez maintenant :

- **décrire** un jeu de données (position, dispersion, forme, relations) et **toujours dessiner avant de calculer** ;
- **estimer** un paramètre (moments, maximum de vraisemblance), juger un estimateur par son biais et sa variance, et savoir pourquoi on divise par $n-1$ ;
- **quantifier l'incertitude** par des intervalles de confiance (Student, Wilson, bootstrap), sans en faire une mauvaise lecture ;
- **tester** une hypothèse (Student, Welch, proportions, A/B, khi-deux) en distinguant significativité et importance pratique ;
- **dimensionner** une expérience (puissance), et **éviter les faux positifs** (tests multiples, *peeking*) ;
- (en option) **échantillonner** correctement et employer des méthodes **sans hypothèse de loi**.

Le chapitre 4 change de registre : après la théorie, la **pratique du code**. Python, R, algorithmes, NumPy, pandas, visualisations : ce sont les outils qui permettront d'appliquer tout ce que vous venez d'apprendre sur de vraies données.


---

# Chapitre 4 : Programmation

> « Les mathématiques vous disent **quoi** calculer.
> La programmation vous permet de le calculer sur **un million de lignes**. »

Jusqu'ici, nous avons utilisé du code comme un outil de vérification. Ce chapitre prend le code **au sérieux** : c'est lui qui transforme vos idées en résultats reproductibles. Pas besoin d'avoir jamais programmé : on part de zéro. Si vous programmez déjà, parcourez les premières sections en diagonale et attardez-vous sur NumPy, pandas et les visualisations.

## Le chemin de ce chapitre

- **4.1 Python** : le langage de ce livre, des variables aux fonctions, avec un petit programme complet (la caisse de la boutique).
- **4.2 R** : l'autre grand langage de la statistique ; on refait les mêmes analyses pour comparer.
- **4.3 Algorithmes et structures de données** : piles, files, dictionnaires, récursion, tris, recherche. Penser comme un informaticien.
- **4.4 NumPy et pandas** : les deux bibliothèques qui font de Python un outil d'analyse de données.
- **4.5 Visualisations** : choisir le bon graphique, le tracer proprement, avec matplotlib, pandas, seaborn et ggplot2.
- ➕ **Pour aller plus loin** : programmation orientée objet, code propre et tests (4.6) ; d'autres langages (4.7) ; complexité algorithmique (4.8).
- **4.9 Exercices corrigés**.

> 🛠️ **Comment travailler avec ce chapitre.** *Tapez* le code vous-même plutôt que de le copier : c'est la seule façon d'apprendre à programmer. Modifiez-le, cassez-le, observez les messages d'erreur. Ils sont vos amis : un message d'erreur lu attentivement dit presque toujours où est le problème. Pour exécuter du code Python, vous pouvez utiliser un notebook Jupyter (section 6.2) ou simplement un terminal avec la commande `python`.

> 📦 **Le fichier de données.** Au chapitre 3, nous avons construit un tableau de 400 commandes. Il a été enregistré dans le fichier `donnees/commandes.csv`, fourni avec le livre (c'est la sortie de `df.to_csv("donnees/commandes.csv", index=False)` appliqué au tableau du 3.1.2). Nous l'utiliserons pour les sections 4.2, 4.4 et 4.5, ainsi qu'au chapitre 5 (SQL).
