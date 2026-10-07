# Chapitre 6 : Conception de KPI et cadres d'indicateurs

> « Ce qui se mesure se pilote, à condition de savoir ce que l'on mesure et pourquoi. »

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch06 as O
D = os.environ["DONNEES"]
d = O.charger(D)
k25, k24 = O.kpis(d, 2025), O.kpis(d, 2024)
print("lignes de commande :", len(d["x"]), "| sessions :", len(d["sess"]), "| livraisons :", len(d["liv"]))
```
<!--sortie-->
```text
lignes de commande : 83905 | sessions : 127022 | livraisons : 19420
```

Un lundi de janvier, la gérante pousse la porte de votre bureau avec une pile de feuilles. « Chaque lundi, je reçois **quarante chiffres** : le chiffre d'affaires par jour, par canal, par catégorie, le nombre de visites, le nombre de retours, le stock de chaque produit, les délais de livraison… J'y passe une heure, je ne sais plus ce qui compte, et la semaine dernière j'ai découvert un problème de livraison **trois semaines après** qu'il a commencé. **Lesquels dois-je suivre ?** »

C'est l'une des questions les plus fréquentes d'un analyste, et l'une des plus mal posées : on croit demander une liste, alors qu'on demande **une façon de décider**. Un chiffre n'est un indicateur que s'il fait agir. Les chapitres précédents de ce volume vous ont appris à **explorer**, à **tester**, à **expliquer** et à **prévoir** ; celui-ci vous apprend à **choisir ce que l'on regarde, chaque semaine, et à quelle condition on peut s'y fier**.

## Le chemin de ce chapitre

Le chapitre suit la question de la gérante, de la définition d'un chiffre à la lecture de ses variations.

- **6.1 Ce qui fait un bon KPI.** Un KPI (*key performance indicator*, indicateur clé de performance) est un chiffre **lié à une décision**, **défini par écrit** et **difficile à truquer**. Nous calculons une douzaine d'indicateurs de la boutique, par un seul code, et nous débusquons les pièges de calcul et les effets pervers : ce qui arrive quand le chiffre devient un objectif.
- **6.2 Arbres d'indicateurs et cadres de référence.** Un chiffre global (le chiffre d'affaires) se **décompose** en facteurs (trafic, conversion, panier) : l'arbre dit **où chercher** quand le chiffre bouge. Nous comparons aussi les grands cadres de référence (tableau de bord équilibré, AARRR, OKR, *North Star*) en gardant l'esprit critique.
- **6.3 Cibles, références et seuils.** Un chiffre sans point de comparaison ne dit rien. Nous voyons de quoi une cible est faite, quelles références utiliser (année précédente, budget, secteur), comment tracer des **seuils d'alerte** fondés sur la variabilité réelle, et comment distinguer **le bruit du signal**.

Le chapitre se termine par un **tableau de bord d'une page** et un **dictionnaire des KPI** que la gérante peut lire en cinq minutes.

> 💡 **Intuition.** Un tableau de bord n'est pas un album de photos des données : c'est un **instrument de bord**. Un pilote ne regarde pas tous les cadrans en permanence ; il en suit quelques-uns, dont il connaît les valeurs normales, et il sait ce qu'il fera si l'un d'eux sort de la zone.

## Les données du chapitre

Nous reprenons la boutique des chapitres précédents (volume I, et volume III, chapitre 1). Tout est **simulé**, et la vérité programmée est connue (docstring de `build/donnees_a3.py`) ; nous la révélons quand elle éclaire un indicateur.

> 📦 **Les données.** `commandes.csv` et `lignes_commande.csv` (2023 à 2025), `produits.csv`, `retours.csv`, `clients.csv`, `jours_exploitation.csv`, `sessions_web.csv` (127 022 sessions du site en 2025), `livraisons.csv`, `stock_quotidien.csv` (20 produits en 2025), `budget_reel_2025.csv`, `compte_resultat_mensuel.csv`, `bilan_annuel.csv` et `benchmark_secteur.csv` (médiane et quartiles **fictifs** du secteur). La TVA est fixée à 20 % **pour l'illustration**.

Toutes les données ne couvrent pas les mêmes périodes : les sessions du site et les stocks ne sont disponibles que pour **2025**, alors que les commandes remontent à 2023. Quand un indicateur n'existe que pour 2025, nous le dirons ; c'est déjà une leçon de ce chapitre : **un indicateur qui n'a pas d'historique ne peut pas être comparé**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.6 et exercices 6.1 à 6.12 ; chacun renvoie à la section du livre qui l'éclaire.
