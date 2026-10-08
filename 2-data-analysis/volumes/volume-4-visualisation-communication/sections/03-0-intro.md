# Chapitre 3 : Visualisation avec Python

> « Un graphique que l'on ne peut pas refaire n'est qu'une image ; un graphique que l'on peut refaire est une analyse. »

La gérante vous écrit un lundi matin : « *Peux-tu me faire le graphique des ventes par canal pour la réunion de jeudi ? En couleurs lisibles, avec les chiffres sur les barres. Et si tu peux, que je puisse cliquer dessus pour voir le détail.* » Trois demandes en une phrase : un graphique **juste**, un graphique **lisible**, un graphique **interactif**. Les chapitres 1 et 2 ont posé les principes (quel type de graphique, quelle mise en page, quel tableau de bord) ; celui-ci apprend à les **fabriquer avec du code**.

Pourquoi du code plutôt qu'un outil à cliquer ? Pour une raison que l'on a déjà rencontrée dans toute la série : la **reproductibilité**. Un graphique construit à la souris se refait à la souris, avec les mêmes oublis ; un graphique construit par un script se refait en une commande, le mois suivant, sur les nouvelles données, et l'on peut **tester** qu'il montre bien les chiffres qu'il prétend montrer. C'est aussi pour cela que, dans ce chapitre, **le code est le sujet** : les blocs restent courts, mais vous les verrez presque tous.

## Le chemin de ce chapitre

- **3.1 matplotlib et seaborn** : l'anatomie d'une figure, les graphiques de base (barres, lignes, nuages, histogrammes), les étiquettes directes, les petits multiples, le thème maison du livre, puis seaborn pour les graphiques statistiques ; la même figure en R avec ggplot2 pour comparer les syntaxes.
- **3.2 plotly et graphiques interactifs** : survol, zoom, filtre par légende ; de vraies captures de figures interactives ; quand l'interactivité aide, quand elle gêne.
- ➕ **3.3 Tableaux de bord avec Dash, Streamlit et Shiny** : le même mini-tableau de bord écrit dans trois outils libres, testé, photographié.
- ➕ **3.4 Cartes et visualisation géospatiale** : cercles proportionnels et polygones sur un plan **fictif**, normaliser par habitant, savoir quand une carte ne sert à rien.

## Les données du chapitre

Les mêmes données de la boutique que dans les volumes précédents (ventes par ligne de commande, clients, jours d'exploitation, sessions web, livraisons) et un fichier de **villes fictives** avec des coordonnées dans un plan imaginaire (`villes.csv`) : aucune carte du monde réel n'est utilisée. Toutes les données sont **simulées**.

> 🧭 **En pratique.** Les figures de ce chapitre sont produites par le code que vous lisez. Les captures d'outils interactifs (plotly, Dash, Streamlit, Shiny) sont de **vraies captures** de ces outils **libres**, lancés sur la machine qui a écrit le livre ; aucune interface d'un logiciel commercial n'est reproduite.

```python
import sys
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import style, outils_ch03 as O
style.setup()                       # le thème maison du livre (voir 3.1.6)
x = O.ventes()                      # une ligne par ligne de commande : montant, date, canal, client, catégorie
print(len(x), "lignes de commande |", x["date_commande"].min().date(), "->", x["date_commande"].max().date())
```
<!--sortie-->
```text
83905 lignes de commande | 2023-01-01 -> 2025-12-31
```
<!--sortie-->
