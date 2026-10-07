# Chapitre 8 : ➕ Pareto, analyse ABC et benchmarking

> « Tout compter ne sert à rien : il faut savoir ce qui compte, et par rapport à qui. »

> 🧭 **Chapitre complémentaire.** Il est facultatif : le reste du volume ne le suppose pas. Il présente deux outils de **priorisation** très utilisés en entreprise : classer ce qui pèse le plus (Pareto, ABC), et se situer par rapport à des références (benchmarking).

La gérante revient avec une question à deux têtes : « *Quels produits sont vraiment importants pour la boutique, à qui consacrer mon énergie et mon stock ? Et, au fond, est-ce que je me débrouille bien par rapport aux autres boutiques de mon secteur ?* »

La première question est une affaire de **concentration** : quelques produits, quelques clients font-ils l'essentiel du chiffre d'affaires ? La seconde est une affaire de **comparaison** : un chiffre n'est ni bon ni mauvais en soi, il l'est par rapport à une référence. Les deux ont le même piège : donner une réponse nette, rassurante, **plus simple que ce que les données permettent**.

## Le chemin de ce chapitre

- **8.1 Pareto et analyse ABC** : tracer une courbe de Pareto, tester la règle « 80/20 » sur les produits, les clients et les retours, construire des classes A, B et C, les croiser avec la marge et avec la régularité de la demande, et éviter les pièges.
- **8.2 Benchmarking interne et externe** : comparer les canaux, les catégories et les mois entre eux, puis la boutique au secteur (avec des données **fictives**), lire un positionnement et décider quoi faire d'un écart.

## Les données du chapitre

On utilise les commandes, les lignes de commande, les produits, les retours et les clients de la boutique (2023–2025), ainsi que les sessions du site, le compte de résultat et le bilan, les livraisons et le stock quotidien pour calculer des indicateurs. Le fichier `benchmark_secteur.csv` donne, pour douze indicateurs, une **médiane** et deux **quartiles** d'un secteur : ces chiffres sont **fictifs**, inventés pour l'exercice, et ne décrivent aucun secteur réel. Toutes les données sont **simulées** ; la vérité programmée est dans la docstring de `build/donnees_a3.py`.

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch08 as O

D = os.environ["DONNEES"]
cmd, lg, prod, ret, cli = O.charger(D)
sect = pd.read_csv(os.path.join(D, "benchmark_secteur.csv"))
l25 = lg[lg["annee"] == 2025]
```
