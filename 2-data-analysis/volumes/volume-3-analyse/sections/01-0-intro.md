# Chapitre 1 : Analyse exploratoire des données

> « Avant de chercher pourquoi, regardez à quoi ça ressemble. »

La gérante passe la tête dans la porte de votre bureau, une tasse de café à la main :

— Avant de me dire *pourquoi* les ventes bougent, dis-moi à quoi elles **ressemblent**. Je ne sais même pas ce qu'est une journée normale, chez nous.

Vous aviez prévu de lancer un modèle, un test, une régression. Elle a raison de vous arrêter : on ne choisit pas une méthode d'analyse avant d'avoir **regardé** les données. Les volumes précédents vous ont appris à les lire (volume I), puis à les rendre fiables (volume II). Ce chapitre ouvre le volume III par l'étape que tous les analystes expérimentés font en premier, et qu'ils ne sautent jamais : l'**analyse exploratoire des données**, ou *EDA* (*exploratory data analysis*).

L'exploration n'a pas pour but de **prouver** quelque chose. Elle sert à quatre choses, et seulement à celles-là :

1. **Comprendre la forme** de chaque variable (où se trouve le centre, jusqu'où va la queue, combien de modalités) pour savoir quels résumés ont un sens ;
2. **Repérer les relations** entre variables, pour formuler des questions précises que les chapitres suivants testeront ;
3. **Découvrir les surprises** : des motifs que l'on attendait (la saison, le week-end) et des anomalies que l'on n'attendait pas (une panne, une erreur de saisie) ;
4. **Décider** de la suite : quelle méthode, sur quelles données, avec quelles précautions.

Une exploration réussie se reconnaît à un livrable simple : une page où l'on peut écrire, pour chaque variable importante, **une phrase** qui la décrit et **une action** qu'elle entraîne.

## Le chemin de ce chapitre

Le **parcours essentiel** compte trois sections, qui vont de la plus simple des questions à la plus fine :

- **1.1 Analyse univariée** : *à quoi ressemble chaque variable, prise seule ?* Les histogrammes et leurs classes, la boîte à moustaches, les quantiles, l'échelle logarithmique ; les barres ordonnées pour les catégories ; la série dans le temps. Trois pièges de lecture.
- **1.2 Analyse bivariée et multivariée** : *comment deux variables, puis trois, varient-elles ensemble ?* Nuages et lissage, comparaisons de groupes, tableaux croisés, matrice de corrélation, et un phénomène qui fait peur à tous les analystes : le **paradoxe de Simpson**, que nous retrouverons dans les vraies données de la boutique.
- **1.3 Repérer les motifs et les anomalies** : *qu'est-ce qui est régulier, qu'est-ce qui sort du lot ?* Jour de la semaine, saison, changement de niveau ; puis une méthode simple et robuste pour détecter des **incidents** dans les ventes, évaluée contre la vérité programmée. Une anomalie n'est pas une erreur, et une erreur n'est pas un événement : la différence décide de ce que l'on fait.

Une section facultative (➕) complète le tout : **1.4 Une liste de contrôle EDA réutilisable**, avec une fonction qui produit automatiquement un premier rapport d'exploration sur n'importe quel tableau.

> 🧭 **Comment lire ce chapitre.** Chaque section part d'une **question** de la gérante, regarde les **données** de la boutique, et finit par **ce que l'on peut dire** (et ce que l'on ne peut pas dire). Le code est court : l'essentiel est de savoir **quoi regarder**, pas de savoir écrire le graphique. Les figures sont produites par du code caché, que vous retrouverez dans le cahier. Ce chapitre suppose le volume I (statistique descriptive : médiane, quartiles, écart-type, section 1.1 ; corrélation, section 1.4) et le volume II (données propres).

## Les données du chapitre

> 📦 **Les données.** Tout le volume s'appuie sur les données **simulées** de la boutique (le générateur est dans `build/donnees_a3.py`) :
>
> - `commandes.csv` et `lignes_commande.csv` : 36 395 commandes et 83 905 lignes entre janvier 2023 et décembre 2025 ;
> - `clients.csv`, `produits.csv` (120 produits, 6 catégories) et `retours.csv` ;
> - `jours_exploitation.csv` : une ligne par jour (commandes, chiffre d'affaires, température, pluie, promotion, dépense publicitaire) ;
> - `livraisons.csv` : les commandes livrées (Site et Réseaux), avec le transporteur et les dates ;
> - `jours_incidents.csv` : les mêmes jours d'exploitation, mais avec **des incidents injectés**, dont la liste exacte est dans `verite_incidents.csv`. Nous n'ouvrirons ce dernier fichier qu'à la fin de la section 1.3, comme on ouvre une correction.
>
> Comme les données sont fabriquées, nous connaissons la **vérité** qui les a générées ; nous la révélerons quand elle est instructive.

On commence par charger les tableaux. Une commande est composée d'une ou plusieurs **lignes** ; son **panier** est la somme de ses lignes.

```python
import sys, warnings
sys.path.insert(0, "build")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import outils_ch01 as O

donnees = O.charger()
cmd, lig, prod, ret, j, cli, liv, ji, vi = (donnees[k] for k in ["cmd", "lig", "prod", "ret", "j", "cli", "liv", "ji", "vi"])
print(len(cmd), "commandes,", len(lig), "lignes,", len(prod), "produits,", len(cli), "clients,", len(j), "jours")
print(cmd[["id_commande", "date_commande", "canal", "mode_livraison", "code_promo", "panier"]].head(3).to_string(index=False))
```
<!--sortie-->
```text
36395 commandes, 83905 lignes, 120 produits, 6000 clients, 1096 jours
 id_commande date_commande    canal  mode_livraison code_promo  panier
           1    2023-01-01     Site        Domicile               83.8
           2    2023-01-01 Boutique Retrait magasin               80.7
           3    2023-01-01 Boutique Retrait magasin               60.8
```

Avant de calculer quoi que ce soit, on se pose la question que se pose tout bon analyste devant un tableau : **que représente une ligne, et quelles sont les colonnes ?** Ici, une ligne de `cmd` est une commande, une ligne de `j` est un jour, une ligne de `liv` est une livraison. Nous verrons au fil du chapitre que choisir le bon tableau, c'est déjà choisir la bonne question.
