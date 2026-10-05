# Chapitre 7 : ➕ Systèmes de recommandation

> « Montrer à chacun les quelques produits, parmi des milliers, qu'il a une vraie chance d'aimer : voilà un problème de prédiction où la bonne réponse n'existe que dans l'avenir. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : les chapitres 1 à 5 se lisent et se comprennent sans lui. Il s'adresse à celles et ceux qui veulent voir comment les idées du volume (validation honnête, modèles de référence, factorisation, évaluation) se déclinent dans un problème qui n'est ni une classification ni une régression : **classer des produits pour chaque client**.

Quand la gérante ouvre la page d'accueil de sa boutique en ligne, elle aimerait que chaque visiteur voie en premier les produits qu'il est le plus susceptible d'acheter. Elle n'a pas de variable « client à retenir » à prédire, comme au chapitre 2 : elle a un **historique d'achats** et une question plus délicate, « parmi les 150 produits du catalogue, lesquels montrer à *ce* client-là, dans quel ordre ? ».

C'est le problème de la **recommandation**. Il est plus ouvert qu'il n'y paraît : on ne dispose que d'achats (jamais de « non, ce produit ne m'intéresse pas »), la plupart des cases du tableau clients × produits sont vides, les produits populaires écrasent les autres, et les recommandations changent elles-mêmes les achats futurs. Le volume a donné les outils pour s'y prendre : une démarche d'évaluation rigoureuse (chapitre 1), des modèles de référence à battre (section 1.4), de la régularisation (section 2.1), une factorisation de matrice (la décomposition en valeurs singulières du volume I, section 1.1.4, et l'ACP du volume II, section 3.1).

## Le chemin de ce chapitre

- **7.1 Données d'interaction et références simples** : ce que l'on observe vraiment, la matrice d'interactions, et deux premières méthodes qui ne demandent aucun apprentissage sophistiqué : la **popularité** et le **filtrage par contenu**.
- **7.2 Filtrage collaboratif** : « ceux qui ont acheté comme vous ont aussi acheté… ». Les méthodes de **voisinage**, entre clients et entre produits.
- **7.3 Factorisation matricielle** : résumer chaque client et chaque produit par quelques **facteurs latents**, appris en minimisant une erreur régularisée ; le cas des achats **implicites**.
- **7.4 Évaluation et démarrage à froid** : comment mesurer un classement, pourquoi un découpage aléatoire peut tromper, ce que valent les recommandations pour un **nouveau client** ou un **nouveau produit**, et pourquoi les recommandations modifient les données qui serviront à les améliorer.

> 💡 **Le fil rouge du chapitre.** À chaque étape, la même question : *par rapport à quoi ?* Une recommandation « personnalisée » n'a d'intérêt que si elle fait mieux que montrer à tout le monde les produits les plus vendus. Nous verrons que, sur les données de la boutique, cette référence très simple est étonnamment difficile à battre.

## Les données et le protocole

Nous utilisons deux fichiers de la boutique (simulés, comme tous ceux du volume) : `donnees/interactions.csv` (qui a acheté quoi, et combien de fois) et `donnees/produits_ml.csv` (catégorie, prix et caractère « nouveau » de chaque produit).

```python hide
import sys
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
import scipy.sparse as sp
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style
from outils_ch07 import *

style.setup()
BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET = style.BLEU, style.ORANGE, style.AQUA, style.VIOLET, style.ROUGE, style.MUET
inter, prod, R = charger()
nb_par_client = np.asarray(R.sum(axis=1)).ravel()
nb_par_produit = np.asarray(R.sum(axis=0)).ravel()
print(R.shape, R.nnz, f"{R.nnz / (R.shape[0] * R.shape[1]):.4f}")
print("clients sans achat :", int((nb_par_client == 0).sum()), "| avec au moins 5 achats :", int((nb_par_client >= 5).sum()))
print("part de lignes avec nb_achats > 1 :", round((inter.nb_achats > 1).mean(), 3), "| lignes avec note :", round(inter.note.notna().mean(), 3))
print("produits :", prod.categorie.value_counts().sort_index().to_dict(), "| nouveaux :", int(prod.nouveaute.sum()))
d = decouper(R, seed=7)
print("clients évalués :", len(d["users"]), "| achats : entraînement", d["R_train"].nnz, ", validation", d["val"].nnz, ", test", d["test"].nnz)
```
<!--sortie-->
```text
(3000, 150) 27687 0.0615
clients sans achat : 19 | avec au moins 5 achats : 2365
part de lignes avec nb_achats > 1 : 0.332 | lignes avec note : 0.249
produits : {'A': 44, 'B': 44, 'C': 31, 'D': 31} | nouveaux : 26
clients évalués : 2365 | achats : entraînement 17177 , validation 3987 , test 6523
```

Le tableau contient **3 000 clients** et **150 produits** ; les clients ont passé en tout **27 687** achats distincts (une paire client-produit compte une fois, quel que soit le nombre d'exemplaires achetés). Sur les 450 000 cases possibles du tableau, seules **6,2 %** sont remplies : c'est ce que l'on appelle une matrice **creuse**.

Pour évaluer honnêtement les méthodes, nous appliquons dès maintenant la règle du chapitre 1 : trois jeux de données, séparés **avant** de regarder quoi que ce soit.

- On ne retient pour l'évaluation que les clients ayant au moins **5 achats** : ils sont **2 365**.
- Pour chacun, on met de côté au hasard environ **25 %** de ses achats : ce sont les achats du **jeu de test**, que personne ne regardera avant la fin (**6 523** achats au total).
- Parmi les achats restants, on met de côté environ **20 %** : c'est le **jeu de validation** (**3 987** achats), qui servira à choisir les hyperparamètres.
- Tout le reste, **17 177** achats, forme le **jeu d'entraînement**. Les clients qui ont moins de 5 achats restent dans l'entraînement, mais ne sont pas évalués.

Une méthode reçoit donc les achats d'entraînement, produit pour chaque client évalué un **classement** des produits qu'il n'a pas encore achetés, et on regarde dans quelle mesure les achats retirés apparaissent en tête de liste. Les métriques précises sont définies en 7.4.1 ; en attendant, retenez l'idée : plus les achats cachés remontent haut dans le classement, meilleur est le modèle.

> ⚠️ **Une limite à connaître dès le départ.** Ces données ne contiennent **pas de dates**. Nous ne pouvons donc pas découper « le passé » et « l'avenir », comme on le ferait dans un vrai projet, et nous retirons des achats au hasard, client par client. Nous verrons en 7.4.3, sur une simulation où le temps existe, à quel point ce choix peut flatter les résultats.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : l'application 7.1 reconstruit la matrice d'interactions, la popularité et le filtrage par contenu pas à pas, et la préparation du cahier présente le protocole d'évaluation.
