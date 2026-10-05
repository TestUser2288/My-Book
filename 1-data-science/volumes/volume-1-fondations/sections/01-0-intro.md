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

Nous allons suivre la boutique **la boutique** et ses questions concrètes :

- **1.1 Algèbre linéaire** : La gérante veut savoir quels clients se ressemblent, calculer son chiffre d'affaires par mois sans boucle interminable, et résumer un tableau de ventes en quelques tendances.
- **1.2 Analyse** : comment son bénéfice change-t-il quand elle modifie un prix un tout petit peu ? Et quelle est la probabilité qu'une commande arrive dans les trois prochaines minutes ?
- **1.3 Optimisation** : quel prix maximise ses recettes ? Comment répartir son budget publicitaire ?
- **1.4 Fiche de notations** : toutes les notations du livre, au même endroit.
- ➕ **Pour aller plus loin** : pourquoi l'ordinateur se trompe parfois (analyse numérique), et comment compter et relier des objets (mathématiques discrètes et graphes).

> 💡 **Comment lire ce chapitre.** Chaque notion suit le même rythme : une intuition, un exemple chiffré à la main, puis (si nécessaire) une démonstration, puis le code. Si une démonstration vous décourage, sautez-la : l'exemple et le code suffisent pour avancer. Revenez-y plus tard.
