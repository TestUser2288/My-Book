# Chapitre 9 : ➕ Analyse financière

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : le reste du volume ne le suppose pas. Il montre comment un analyste lit les comptes de l'entreprise, mesure sa rentabilité et sépare les coûts qui suivent l'activité de ceux qui ne la suivent pas.

> « Le chiffre d'affaires est une opinion, la marge est un fait, la trésorerie est la réalité. »

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch09 as O
import matplotlib.pyplot as plt
from style import setup as style_setup, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET
style_setup()
pd.options.display.width = 140
cr, bil, cmd, lig, prod, camp, bm = O.charger()
ann = O.annuel(cr)
bi = bil.set_index("annee")
rat = O.ratios(ann, bi)
reg = O.couts_regression(cr)
fr = lambda x, nd=0: f"{x:,.{nd}f}".replace(",", " ").replace(".", ",").replace("-", "−")
def tab(df, nd=0):
    """tableau en euros, séparateur d'espace et virgule décimale"""
    return df.map(lambda x: fr(x, nd)).to_string()
```

La gérante pose la question à la fin de la réunion de janvier, en tapotant sur la feuille des ventes : « Nous avons vendu **11 % de plus** en 2025, et pourtant j'ai l'impression de ne rien gagner. Où passe l'argent ? »

C'est une très bonne question, et la bonne réponse n'est pas « dans les charges » : c'est une **suite de chiffres reliés entre eux**. Le chiffre d'affaires ne se transforme pas en gain : il paie d'abord les marchandises, puis le personnel, le loyer, la publicité, la livraison, la banque, et ce qui reste est le résultat. Voyons ce que disent les comptes.

```python
print("chiffre d'affaires hors taxes (€) :", {int(a): fr(v) for a, v in ann["ca_ht"].items()})
print("croissance du chiffre d'affaires :", {int(a): fr(v * 100, 1) + " %" for a, v in ann["ca_ht"].pct_change().dropna().items()})
print("résultat d'exploitation (€) :", {int(a): fr(v) for a, v in ann["resultat_exploitation"].items()})
print("part du résultat dans le chiffre d'affaires 2025 :", fr(ann.loc[2025, "resultat_exploitation"] / ann.loc[2025, "ca_ht"] * 100, 1), "%")
```
<!--sortie-->
```text
chiffre d'affaires hors taxes (€) : {2023: '949 111', 2024: '991 218', 2025: '1 103 969'}
croissance du chiffre d'affaires : {2024: '4,4 %', 2025: '11,4 %'}
résultat d'exploitation (€) : {2023: '16 953', 2024: '17 599', 2025: '39 879'}
part du résultat dans le chiffre d'affaires 2025 : 3,6 %
```

Le chiffre d'affaires hors taxes a progressé de 11,4 % en 2025 (après 4,4 % en 2024), et le résultat d'exploitation a **plus que doublé** (de 17 599 € à 39 879 €, soit +127 %). Pourtant, il ne représente que **3,6 %** du chiffre d'affaires : sur 100 € hors taxes vendus, 3,60 € restent à l'entreprise. L'impression de la gérante est donc exacte, et il faut l'expliquer : c'est le programme de ce chapitre.

> ⚠️ **Avertissement : des comptes simulés et simplifiés.** Les comptes de ce chapitre sont **fabriqués** à partir des ventes de la boutique : TVA fictive de 20 %, achats égaux aux quantités vendues multipliées par le coût d'achat, résultat net **approché** à 70 % du résultat d'exploitation (pour tenir compte, grossièrement, de l'impôt et des intérêts), bilan **équilibré par construction**. Les règles réelles (plan comptable, traitement des stocks, de la TVA, des amortissements, impôts) dépendent de **votre pays** et de votre entreprise. Ce chapitre apprend à **lire et à interroger** des comptes, pas à les établir, et rien ne s'y substitue à l'avis d'un comptable.

## Le chemin de ce chapitre

- **9.1 Lire un compte de résultat et un bilan** : ce que chaque ligne mesure, comment vérifier que les comptes sont cohérents avec les ventes de la base, comment lire une année et un mois.
- **9.2 Rentabilité et ratios** : marges, rentabilité des capitaux, rotation du stock, délais de règlement, besoin en fonds de roulement, liquidité, endettement ; comparaison dans le temps et avec un secteur fictif.
- **9.3 Analyse des coûts et seuil de rentabilité** : coûts fixes et variables estimés par régression, point mort, marge de sécurité, levier opérationnel, rentabilité par canal et clés de répartition, effet d'une hausse de prix ou de volume.

## Les données du chapitre

> 📦 **Les données.** `compte_resultat_mensuel.csv` (36 mois de comptes de la boutique) et `bilan_annuel.csv` (2023 à 2025), les ventes de la base (`commandes.csv`, `lignes_commande.csv`, `produits.csv`) pour recouper les comptes, `campagnes.csv` (dépenses de marketing de 2025) et `benchmark_secteur.csv` (médiane et quartiles **fictifs** d'un secteur). Tout est **simulé** ; les vérités programmées sont dans `build/donnees_a3.py`.
