# Chapitre 7 : ➕ Analyse des écarts et des causes racines

> « Un écart n'est pas une réponse : c'est une question que le budget pose à la réalité. »

> 🧭 **Chapitre complémentaire.** Il est facultatif : le reste du volume ne le suppose pas. Il montre comment passer d'un chiffre qui « ne colle pas au budget » à une explication **chiffrée** (décomposer l'écart) puis à une **cause** que l'on peut défendre (tester des hypothèses), ou à l'aveu honnête qu'on ne peut pas conclure.

À la réunion de janvier, la gérante pose le problème : « *Le chiffre d'affaires de 2025 dépasse le budget de 3,6 %, la marge de 8,6 %, et pourtant la Boutique est en dessous du budget sur les deux. Que s'est-il passé ? Et qu'est-ce que je change pour 2026 ?* »

Deux questions en une. La première est **descriptive** : *où* sont les écarts et *de quoi* sont-ils faits ? La seconde est **causale** : *pourquoi* ? Elles n'appellent pas les mêmes méthodes, et la confusion des deux est l'erreur classique : on explique un écart par la première histoire plausible, sans l'avoir vérifiée.

## Le chemin de ce chapitre

- **7.1 Budget contre réalisé** : lire un écart (absolu, relatif, favorable ou défavorable), construire le tableau d'écarts, décider quels écarts méritent une explication, et reconnaître les pièges (compensations, budget irréaliste, périodes décalées).
- **7.2 Décomposer un écart (prix, volume, mix)** : séparer l'écart de chiffre d'affaires, puis de marge, en effets qui **somment exactement** à l'écart total.
- **7.3 Remonter aux causes** : les cinq pourquoi, le diagramme d'Ishikawa, des hypothèses **testables** que l'on teste avec les données, et la façon d'écrire une conclusion honnête.

## Les données du chapitre

Le fichier `budget_reel_2025.csv` donne, pour chaque mois de 2025, chaque catégorie et chaque canal, le budget et le réalisé (chiffre d'affaires, quantités, prix moyen, marge). Le budget a été construit à partir de **l'année 2024 réelle** multipliée par un coefficient de croissance, avec quelques erreurs de plan selon la catégorie : c'est ce que fait la plupart des entreprises. Pour tester des hypothèses, on utilise aussi la base de la boutique (`commandes.csv`, `lignes_commande.csv`, `produits.csv`), les jours d'exploitation (`jours_exploitation.csv`) et le stock des vingt produits les plus vendus (`stock_quotidien.csv`). Toutes les données sont **simulées** ; la vérité programmée est dans la docstring de `build/donnees_a3.py`.

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch07 as O

D = os.environ["DONNEES"]
lire = lambda nom, **kw: pd.read_csv(os.path.join(D, nom), **kw)
bud = lire("budget_reel_2025.csv")
cmd = lire("commandes.csv", parse_dates=["date_commande"])
lig = lire("lignes_commande.csv")
prod = lire("produits.csv")
jours = lire("jours_exploitation.csv", parse_dates=["date"])
stock = lire("stock_quotidien.csv", parse_dates=["date"])
cmd["annee"] = cmd["date_commande"].dt.year
TVA = 0.20
```
