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
4. un **point à retenir** et les pièges à éviter.

Chaque idée importante reçoit au moins un exemple « sans issue de secours » : un exemple si concret qu'on ne puisse plus se dire « je n'ai pas compris ».

### Un livre, et son cahier

Pour que la lecture reste fluide, **le livre ne contient ni exercices, ni corrigés, ni longues applications** : il explique, il montre des exemples, il démontre. Tout ce qui sert à **s'entraîner** vit dans un second ouvrage, le **Cahier d'exercices et d'applications** de ce volume : des exercices corrigés, classés par difficulté, des applications guidées sur des données réalistes, et le projet de clôture du volume.

Les deux ouvrages se répondent. À la fin des sections concernées, une ligne de ce type vous indique quoi faire ensuite :

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1, exercices 3.1 à 3.4.

Le cahier est organisé comme le livre : le chapitre 3 du cahier accompagne le chapitre 3 du livre. Une manière efficace de travailler : **lire une section du livre, puis faire sans attendre les exercices indiqués**, avec un crayon, avant de regarder les corrigés.

### Les encadrés

Pour que la lecture reste fluide, chaque type de contenu a son pictogramme :

| Pictogramme | Rôle |
|---|---|
| 💡 **Intuition** | L'idée en langage courant, sans formule. À lire en premier. |
| 🧪 **Exemple** | Un calcul concret, souvent refait à la main. |
| 📐 **Démonstration** | Le raisonnement rigoureux. On peut la sauter à la première lecture, mais elle est ce qui rend la compréhension durable. |
| ⚠️ **Piège** | Une erreur classique, que presque tout le monde fait une fois. |
| ✅ **À retenir** | Le résumé à garder en mémoire. |
| 🧭 **Repère** | Un guide de lecture, ou l'annonce d'une section optionnelle. |
| 📒 **Pour s'entraîner** | Un renvoi vers les exercices et applications du cahier. |
| ➕ **Pour aller plus loin** | Section facultative : approfondissement, outil ou sujet connexe. |

### Le principe « essentiel / pour aller plus loin »

Dans chaque chapitre, tout ce qui n'est **pas** marqué ➕ constitue le **parcours essentiel**. Il est complet : un lecteur qui suit uniquement ce parcours acquiert la vue d'ensemble et les compétences utiles pour la suite de la série.

Les sections marquées **➕ Pour aller plus loin** sont des cadeaux, pas des obligations : elles approfondissent un point, présentent un outil de plus ou ouvrent une porte. Certains lecteurs préfèrent se concentrer sur la grande idée ; d'autres aiment creuser. Les deux manières de lire ce livre sont bonnes.

### Trois parcours de lecture

| Parcours | Pour qui | Que lire |
|---|---|---|
| **Essentiel** | Vous voulez la vue d'ensemble, vite | Le livre sans les démonstrations 📐 ni les sections ➕ ; les 💡, 🧪, ⚠️ et ✅ suffisent |
| **Complet** | Vous voulez comprendre en profondeur | Tout le parcours essentiel, démonstrations comprises, et les exercices du cahier après chaque section |
| **Praticien** | Vous aimez coder avant de théoriser | Le chapitre 6 (outils), puis le 4 (programmation), puis le 5 (SQL), avec les applications du cahier ; les chapitres 1 à 3 ensuite |

> 💡 **Vous n'avez jamais programmé ?** Pas de panique : dans les chapitres de programmation, chaque bloc de code est suivi de **sa sortie réelle**, et chaque bloc est court. On peut donc lire le livre sans rien exécuter et comprendre ce qui se passe. Quand vous serez prêt(e), le chapitre 4 (section 4.1) vous apprend Python depuis zéro, et le cahier vous propose de quoi pratiquer.

## Le fil rouge : la boutique

Apprendre sur des données abstraites est ennuyeux. Tout au long de ce volume, nous travaillerons donc sur une même histoire :

> **La gérante** dirige **une boutique** qui vend des produits artisanaux (céramiques, textiles, bijoux, cosmétiques) dans son magasin, sur son site web et sur les réseaux sociaux. Elle vend, elle livre, elle reçoit des retours. Elle a des questions ; vous allez l'aider à y répondre avec des données.

Voici quelques-unes de ses questions, et le chapitre où nous y répondrons :

| Question de la gérante | Outil | Chapitre |
|---|---|---|
| « Quels clients se ressemblent ? » | vecteurs, similarité | 1 |
| « Comment ajuster mes prix pour maximiser le chiffre d'affaires ? » | optimisation | 1 |
| « Cette commande est-elle une fraude ? » | théorème de Bayes | 2 |
| « Combien de commandes dois-je prévoir à 14 h ? » | loi de Poisson | 2 |
| « Mon nouveau transporteur est-il vraiment plus rapide ? » | tests d'hypothèses | 3 |
| « Combien vaut mon panier moyen, à ±2 euros près ? » | intervalle de confiance | 3 |
| « Comment automatiser mes rapports de ventes ? » | Python, pandas | 4 |
| « Quels sont mes dix meilleurs clients ? » | SQL | 5 |
| « Comment retrouver la version de mon analyse d'il y a un mois ? » | Git | 6 |

**Une précision importante :** cette boutique, son personnel, ses clients et toutes ses données sont **fictifs**. Les chiffres sont générés par ordinateur, avec des règles simples que nous connaissons, ce qui permet de vérifier que nos méthodes retrouvent bien la réalité. Toute ressemblance avec une entreprise réelle serait une coïncidence.

## Le code de ce livre

Ce livre n'est pas un manuel de programmation, sauf dans les chapitres 4, 5 et 6, qui enseignent précisément Python, SQL, Git et la ligne de commande. La règle est donc simple :

- **le code n'apparaît que lorsqu'il aide à comprendre** : quand on apprend à programmer, quand l'exemple *est* un morceau de code (une requête SQL, une commande Git), ou quand un phénomène numérique se montre mieux qu'il ne se décrit ;
- **les blocs sont courts** (une quinzaine de lignes au plus) et chacun est suivi de sa sortie réelle ;
- **les calculs, les simulations et les graphiques qui illustrent un résultat** sont bien produits par du code, mais ce code n'encombre pas le texte : les chiffres cités sont reproductibles, et les versions complètes se trouvent dans le cahier et dans le dépôt du livre.

Les exemples sont écrits en **Python** (langage principal), avec quelques exemples en **R** et en **SQL**. Les données aléatoires sont générées avec une **graine** (*seed*) fixée : en rejouant le code, vous obtiendrez les mêmes nombres que dans le livre, à de très légères variations près selon les versions des bibliothèques. Les jeux de données utilisés (un tableau de commandes, puis une petite base SQL) sont fournis dans le dossier `donnees/`.

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
                              Cahier : le projet du volume, l'étude complète de la boutique
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

Avant de commencer, le **cahier** propose un petit **test de départ** de dix questions, à faire en dix minutes, au crayon, **sans calculatrice** : un peu de calcul, de probabilités, de dérivation et une question sur la programmation. Les réponses et la manière d'interpréter votre score y sont données.

> 📒 **Pour s'entraîner.** Cahier, mode d'emploi : test de départ.

La règle de lecture est simple. Si vous êtes à l'aise, commencez par le chapitre 1. Si le test vous a fait hésiter, lisez d'abord le « Rappel express » qui suit : ce n'est pas une affaire de talent, seulement de pratique.

Maintenant, au travail. La gérante nous attend, et sa boutique reçoit une commande à l'instant.


# Rappel express : les bases à avoir en tête

*Quelques pages pour remettre en route ce qu'on a vu au collège et au lycée. Rien ici n'est nouveau : tout sert dans la suite du livre. Si tout vous semble évident, passez directement au chapitre 1.*

## R.1 Fractions et pourcentages

Une **fraction** est une division : $\frac{3}{4}$ veut dire « 3 divisé par 4 », soit $0{,}75$. Pour additionner deux fractions, on les met sur le même dénominateur :

$$\frac{3}{4} + \frac{5}{6} = \frac{3 \times 3}{4 \times 3} + \frac{5 \times 2}{6 \times 2} = \frac{9}{12} + \frac{10}{12} = \frac{19}{12}.$$

Un **pourcentage** est une fraction de dénominateur 100. « Prendre 25 % de 120 € » revient à calculer $120 \times \frac{25}{100} = 30$ €.

> 🧪 **Exemple (la boutique).** Un article coûte 240 €. La gérante propose une remise de 15 %.
>
> - Montant de la remise : $240 \times 0{,}15 = 36$ €.
> - Nouveau prix : $240 - 36 = 204$ €, ou directement $240 \times 0{,}85 = 204$ €.
>
> **Astuce** : « baisser de 15 % » revient à **multiplier par 0,85**. « Augmenter de 19 % » (la TVA) revient à multiplier par 1,19.

> ⚠️ **Piège.** Une hausse de 20 % suivie d'une baisse de 20 % **ne ramène pas** au prix de départ : $100 \to 120 \to 96$. Les pourcentages se multiplient, ils ne s'additionnent pas.


## R.2 Puissances et racines

$a^n$ signifie « $a$ multiplié $n$ fois par lui-même » : $2^3 = 2 \times 2 \times 2 = 8$. Les règles à connaître :

$$a^m \times a^n = a^{m+n}, \qquad \frac{a^m}{a^n} = a^{m-n}, \qquad (a^m)^n = a^{mn}, \qquad a^0 = 1, \qquad a^{-n} = \frac{1}{a^n}.$$

La **racine carrée** $\sqrt{a}$ est le nombre positif dont le carré vaut $a$ : $\sqrt{49} = 7$. On a aussi $\sqrt{a} = a^{1/2}$.

> 🧪 **Exemple.** $2^{10} = 1024$ ; $10^{-2} = 0{,}01$ ; $\sqrt{2} \approx 1{,}414$. Et $2^3 \times 2^4 = 2^7 = 128$, qu'on vérifie : $8 \times 16 = 128$.

## R.3 Équations et fonctions affines

Résoudre une équation du premier degré, c'est isoler l'inconnue en faisant la **même opération des deux côtés** :

$$2x - 7 = 11 \;\Longrightarrow\; 2x = 18 \;\Longrightarrow\; x = 9.$$

Une **fonction affine** s'écrit $y = ax + b$. Le nombre $a$ est la **pente** (de combien $y$ augmente quand $x$ augmente de 1), et $b$ est l'**ordonnée à l'origine** (la valeur de $y$ quand $x = 0$).

> 🧪 **Exemple.** Les frais de livraison de la boutique valent 5 € de forfait plus 0,80 € par kilo. Si $x$ est le poids en kilos :
>
> $$\text{frais}(x) = 0{,}8\,x + 5.$$
>
> Pour un colis de 6 kg : $0{,}8 \times 6 + 5 = 9{,}8$ €. La pente (0,8) est le coût d'un kilo de plus ; l'ordonnée à l'origine (5) est le forfait.

Cette idée, « une pente et une ordonnée à l'origine », reviendra souvent : c'est la base de la régression linéaire.

## R.4 Le symbole $\sum$ (somme)

En statistique, on additionne sans arrêt. Pour ne pas écrire $x_1 + x_2 + \dots + x_n$ à chaque fois, on utilise le grand sigma :

$$\sum_{i=1}^{n} x_i = x_1 + x_2 + \dots + x_n.$$

Cela se lit : « somme, pour $i$ allant de 1 à $n$, des $x_i$ ». C'est exactement une boucle `for` qui additionne.

> 🧪 **Exemple.** Les ventes de la boutique sur cinq jours (en euros) : $x_1 = 120,\; x_2 = 80,\; x_3 = 200,\; x_4 = 100,\; x_5 = 150$.
>
> $$\sum_{i=1}^{5} x_i = 120 + 80 + 200 + 100 + 150 = 650 \text{ €.}$$
>
> La **moyenne** est $\bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i = \frac{650}{5} = 130$ €.


Deux propriétés utiles (elles se vérifient en écrivant les sommes) :

$$\sum (x_i + y_i) = \sum x_i + \sum y_i, \qquad \sum c\,x_i = c \sum x_i \quad (c \text{ constante}).$$

## R.5 Exponentielle et logarithme

Le **logarithme** répond à la question : « *à quelle puissance faut-il élever la base pour obtenir ce nombre ?* ». Ainsi $\log_{10}(1000) = 3$, car $10^3 = 1000$.

En data science, on utilise surtout le **logarithme népérien** $\ln$ (base $e \approx 2{,}718$), et son opposé, la **fonction exponentielle** $e^x$. Ce qu'il faut savoir :

$$\ln(ab) = \ln a + \ln b, \qquad \ln(a^n) = n \ln a, \qquad \ln(e^x) = x, \qquad e^{a+b} = e^a e^b.$$

> 💡 **Intuition.** Le logarithme transforme les **produits en sommes**. C'est précieux : une somme est bien plus facile à manipuler (et à dériver) qu'un produit. C'est la raison pour laquelle, plus tard, nous prendrons le log de produits de probabilités pour estimer des paramètres.

> 🧪 **Exemple.** Un placement double tous les 10 ans. Après 30 ans, il a été multiplié par $2^3 = 8$. Combien de « doublements » faut-il pour multiplier par 1000 ? $\log_2(1000) \approx 9{,}97$, soit environ 10 doublements.


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

Cinq petites questions de vérification, avec leurs réponses, vous attendent dans le cahier : si vous savez y répondre, vous avez tout ce qu'il faut pour commencer.

> 📒 **Pour s'entraîner.** Cahier, mode d'emploi : exercices du rappel express (0.1 à 0.5).
