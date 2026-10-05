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

```bash noexec
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
