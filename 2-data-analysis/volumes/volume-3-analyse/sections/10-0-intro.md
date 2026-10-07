# Chapitre 10 : ➕ Analytique marketing et web (Google Analytics)

> « Un clic n'est pas une visite, une visite n'est pas une commande, et une commande n'est pas forcément due à la publicité qui l'a précédée. »

> 🧭 **Chapitre complémentaire.** Il applique les méthodes du volume (proportions et intervalles de confiance, entonnoirs, régression, tests) à l'activité **marketing et web** de la boutique. Rien de ce qui suit n'est nécessaire à la suite du volume.

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch10 as O
import matplotlib.pyplot as plt
from style import setup as style_setup, save, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET
style_setup()
s, camp, cmd, lig, prod = O.charger()
m = O.marge_commandes(cmd, lig, prod)
print("sessions :", len(s), "| commandes rattachées :", int(s["commande"].sum()), "| lignes de campagne :", len(camp))
```
<!--sortie-->
```text
sessions : 127022 | commandes rattachées : 6078 | lignes de campagne : 36
```

La gérante vous écrit en début de semaine :

« *Je dépense environ 3 500 € par mois en publicité payante, plus des campagnes sur les réseaux et par e-mail. Est-ce que c'est rentable ? Et quel canal dois-je développer ?* »

La question a l'air simple. Elle contient en réalité **quatre** questions, qui demandent chacune une méthode différente :

1. **D'où viennent les visiteurs, et lesquels achètent ?** C'est de l'analyse de **trafic** et de **conversion** (section 10.1).
2. **Combien coûte une commande, un client ?** C'est du **coût d'acquisition** (section 10.2).
3. **Cette dépense a-t-elle *causé* des commandes ?** C'est une question d'**attribution** et d'**incrémentalité**, bien plus difficile que les deux précédentes (section 10.2).
4. **Peut-on se fier aux chiffres de l'outil d'analyse web ?** C'est de la **réconciliation** avec les commandes réelles (section 10.3).

## Le chemin de ce chapitre

- **10.1 Sessions, sources et entonnoir de conversion** : le vocabulaire (visiteur, session, source, appareil), la conversion par source avec son intervalle de confiance, l'entonnoir et ses abandons, la saison, et le piège « plus de trafic, conversion plus basse ».
- **10.2 Coût d'acquisition, retour sur investissement et attribution** : coût par clic, par commande, par nouveau client ; ROAS et ROI en euros de marge ; le lien entre dépense et commandes ; les modèles d'attribution ; l'idée du groupe témoin.
- **10.3 Lire un outil d'analyse web sans se faire piéger** : correspondance entre le vocabulaire d'un outil comme Google Analytics et nos calculs, données incomplètes (consentement, bloqueurs), échantillonnage, et réconciliation avec la base de commandes.

> ⚠️ **Honnêteté sur l'outil.** Google Analytics est un produit commercial dont l'interface, les noms de rapports et certains calculs **changent avec la version**. Ce chapitre **ne l'exécute pas** et n'en reproduit aucun écran : il en décrit les **notions** (marquées « non exécuté ») et refait **les mêmes calculs** avec pandas, sur un fichier de sessions que l'on maîtrise. Pour tout menu ou nom précis : *à vérifier dans la documentation de votre version*.

## Les données du chapitre

> 📦 **Les données.** Elles sont **simulées** (vérité programmée dans la docstring de `build/donnees_a3.py`).
> - `sessions_web.csv` : 127 022 sessions du site en 2025 (`source`, `appareil`, `nouveau_visiteur`, pages vues, durée, étapes de l'entonnoir, `id_commande` pour les sessions qui ont commandé).
> - `campagnes.csv` : dépenses, impressions et clics mensuels des trois sources **payantes** (`payant`, `email`, `reseaux`).
> - `commandes.csv`, `lignes_commande.csv`, `produits.csv` : la base de la boutique, pour relier une session à une commande, à un montant et à une marge (TVA fictive de 20 %).

Un point de méthode avant de commencer. Dans `sessions_web.csv`, **chaque session a une seule source** et **chaque commande est rattachée à une seule session** : c'est une simplification que l'on n'a jamais dans la réalité (un client visite souvent plusieurs fois avant d'acheter). Quand une section a besoin de parcours à plusieurs contacts, nous les **fabriquons** et nous le disons.

Les 6 078 commandes du canal Site de 2025 sont toutes rattachées à une session : sur ces 127 022 sessions, la conversion globale est de 4,78 %.

```python hide
assert len(s) == 127022 and int(s["commande"].sum()) == 6078 and round(s["commande"].mean() * 100, 2) == 4.78
```
