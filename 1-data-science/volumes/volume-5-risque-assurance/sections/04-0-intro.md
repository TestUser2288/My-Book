# Chapitre 4 : Cadre réglementaire

> « Un capital n'est pas une réserve de précaution : c'est le prix de la survie les jours où tout va mal. »

Les trois premiers chapitres vous ont appris à **chiffrer un risque** : une probabilité de défaut (chapitre 1), un prix et une provision d'assurance (chapitre 2), une perte extrême à un seuil donné (chapitre 3). Ce chapitre répond à une question que se posent tôt ou tard tous les modélisateurs de ce métier : **qui impose ces chiffres, qui les contrôle, et pourquoi ?** Une banque et une mutuelle d'assurance ne sont pas des entreprises comme les autres. Elles gardent l'argent d'autrui, elles promettent de le rendre ou de payer un sinistre **des années plus tard**, et leur faillite coûte cher à des personnes qui n'ont aucun moyen de la prévoir. Les autorités fixent donc des règles : combien de **fonds propres** détenir face aux risques pris, **comment mesurer** ces risques, et **quoi publier**.

La banque et la mutuelle de ce livre sont fictives : aucune entité, aucun régulateur, aucun pays particulier n'apparaît. Nous étudions des **cadres internationaux**, par leur logique et leurs formules : le cadre de Bâle pour les banques, un régime de type Solvabilité II pour les assureurs, les normes comptables IFRS 9 et IFRS 17, les principes du Takaful (l'assurance fondée sur la mutualisation, conforme à la finance islamique), et la lutte contre le blanchiment. Pour chacun, l'objectif est le même : que vous sachiez **ce que mesure le texte, quelles hypothèses il cache, comment le calculer sur un exemple et ce qu'il laisse volontairement de côté**.

> ⚠️ **Ce chapitre n'est pas un conseil.** Rien de ce chapitre ne constitue un conseil juridique, comptable ou financier. Les textes réglementaires changent, leur transposition varie d'un pays à l'autre, et les valeurs numériques que nous utilisons (coefficients, seuils, matrices de corrélation) sont des **valeurs d'illustration** ou des ordres de grandeur, établies d'après l'état des textes tel que nous le connaissons à la rédaction (2026). Pour toute décision réelle, **lisez le texte en vigueur dans votre juridiction** et faites valider vos calculs par les personnes responsables. Les mêmes précautions valent pour les chapitres facultatifs.

## Le chemin de ce chapitre

- **4.1 Cadre de Bâle** : pourquoi un capital réglementaire, les trois piliers, les actifs pondérés par le risque, et la **formule des notations internes**, démontrée à partir d'un modèle à un facteur puis vérifiée par simulation, puis appliquée au portefeuille de prêts du chapitre 1.
- **4.2 Cadre Solvabilité** : le bilan « économique » d'un assureur, la meilleure estimation et la marge de risque, le **capital de solvabilité requis** agrégé par une matrice de corrélation, et ce que vaut cette agrégation.
- **4.3 Principes du Takaful** : l'assurance par partage mutuel du risque, ses deux fonds, sa gouvernance, et ce qui change (et ne change pas) pour le modélisateur.
- ➕ **4.4 IFRS 17, Bâle III finalisé et paysage national** : comment un contrat d'assurance entre dans les comptes, un plancher de capital qui limite les modèles internes, et comment aborder un cadre national **sans le nommer**.
- ➕ **4.5 Takaful et finance islamique** : l'excédent technique, les modèles wakala et moudaraba comparés sur des données, le déficit et le prêt sans intérêt, et les contrats de finance islamique usuels.
- ➕ **4.6 Lutte contre le blanchiment et analytique de la fraude** : règles, graphes, détection d'anomalies et apprentissage supervisé sur des transactions simulées, avec leurs charges d'alertes.

Chaque section peut se lire seule pour son idée principale ; les calculs réutilisent les modèles des chapitres précédents sans en dépendre : **tout est recalculé ici**.

> 📦 **Données de ce chapitre.** Trois jeux **simulés**, avec une vérité connue (voir l'introduction du volume) : `credits_conso.csv` (40 000 prêts, défaut à 12 mois) et `recouvrements.csv` (pertes réalisées sur 6 000 défauts) pour le capital des banques ; `takaful_fonds.csv` (trois fonds suivis sur quinze ans : cotisations, sinistres, frais de gestion, rendement) pour la section Takaful ; `transactions_lab.csv` (110 000 transactions de 3 000 comptes), `comptes_lab.csv` et `verite_lab.csv` pour le blanchiment. Les schémas suspects de ce dernier jeu sont **programmés**, donc plus nets que dans la réalité : les performances mesurées sont **optimistes**, et le texte le rappelle chaque fois.

```python hide
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style
style.setup()
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from outils_ch04 import *

# --- le portefeuille de prêts du chapitre 1, recalculé ici : une PD par prêt (logistique), une LGD moyenne, une EAD
credits = charger("credits_conso.csv")
recouv = charger("recouvrements.csv")
Xc = pd.get_dummies(credits.drop(columns=["id_credit", "defaut_12m"]), drop_first=True).astype(float)
Xc = Xc.fillna(Xc.median())
Xa, Xb, ya, yb = train_test_split(Xc, credits["defaut_12m"], test_size=0.5, random_state=0)
mu_c, sd_c = Xa.mean(), Xa.std()
modele_pd = LogisticRegression(max_iter=3000).fit((Xa - mu_c) / sd_c, ya)
pd_hat = modele_pd.predict_proba((Xb - mu_c) / sd_c)[:, 1]
LGD = round(recouv["lgd_realisee"].mean(), 2)
pf = pd.DataFrame({"pd": np.clip(pd_hat, 0.0003, 0.60),
                   "ead": credits.loc[Xb.index, "montant"].values * 0.7,      # encours moyen : 70 % du montant initial
                   "defaut": yb.values})
pf["k"] = k_detail(pf["pd"], LGD)
pf["rwa"] = 12.5 * pf["k"] * pf["ead"]
EAD = pf["ead"].sum()
print("prêts :", len(pf), "| EAD (M€) :", round(EAD / 1e6, 1), "| PD moyenne :", round(pf["pd"].mean(), 4), "| LGD :", LGD)
```
<!--sortie-->
```text
prêts : 20000 | EAD (M€) : 135.5 | PD moyenne : 0.0582 | LGD : 0.46
```
