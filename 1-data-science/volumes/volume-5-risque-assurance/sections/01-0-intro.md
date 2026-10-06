# Chapitre 1 : Risque de crédit et scoring

> « Prêter, c'est parier sur l'avenir d'une personne avec l'argent de quelqu'un d'autre. Le score est la façon d'écrire ce pari. »

Les volumes précédents vous ont appris à **construire et à valider** des modèles prédictifs. Ce volume les met au service d'un métier particulier : **mesurer des risques qui se paient en euros**, par une banque qui prête et par une mutuelle qui assure. Le premier de ces risques est le plus ancien et le mieux formalisé : celui qu'un emprunteur **ne rembourse pas**. C'est le **risque de crédit**.

Un établissement de crédit décide chaque jour des centaines ou des milliers de dossiers : accorder ou refuser, à quel taux, avec quelle limite. Il ne peut pas les examiner un par un ; il a besoin d'une **règle** qui transforme les informations d'un dossier en un nombre, le **score**, et d'une règle qui transforme ce nombre en décision. Cette règle doit être **efficace** (elle sépare bien les bons des mauvais payeurs), **stable** (elle ne s'effondre pas quand la clientèle change), **explicable** (on sait dire à un client pourquoi il est refusé, et au régulateur pourquoi le modèle est juste) et **calibrée** (quand elle annonce 3 % de défaut, il y a environ 3 % de défauts). Les trois premières sections du chapitre suivent ce fil : on **construit une grille de score** (1.1), on la **compare à des modèles plus souples** (1.2), puis on **mesure ce qu'elle vaut** avec les indicateurs du métier (1.3), le Gini, le KS et la courbe ROC. Trois sections facultatives prolongent le travail vers ce que la comptabilité et la réglementation réclament : le **WOE et l'IV** pour discrétiser proprement (1.4), les **pertes de crédit attendues** de la norme IFRS 9 avec leurs trois composantes PD, LGD et EAD (1.5), et les **matrices de migration** des notes (1.6).

> 🧭 **Ce que le chapitre suppose.** La régression logistique (volume II, section 2.2), la validation et les métriques (volume III, chapitres 1 et 5, en particulier 5.1 et 5.2 pour l'AUC et la calibration) et la notion de dérive (volume IV, section 4.7). Nous rappelons l'essentiel au moment utile.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 1.1 | Comment fabrique-t-on une grille de score ? | Cadrer, découper en classes, estimer sur les WOE, convertir en points |
| 1.2 | Une grille vaut-elle un modèle plus souple ? | Sur ces données, presque : la forme des effets compte plus que l'algorithme |
| 1.3 | Comment mesure-t-on un score ? | Gini, KS, calibration, stabilité, incertitude |
| ➕ 1.4 | Comment discrétiser sans se tromper ? | WOE, IV, regroupements monotones, pièges |
| ➕ 1.5 | Combien le portefeuille va-t-il perdre ? | PD × LGD × EAD, étapes IFRS 9, scénarios |
| ➕ 1.6 | Comment les notes évoluent-elles ? | Matrices de transition, cycle, PD sur plusieurs années |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers de ce chapitre sont **simulés** (graines fixes, générateur `build/donnees5.py`), sauf un détour sur un jeu **réel** en section 1.3 (clients d'une carte de crédit, source UCI, licence CC0, Yeh et Lien, 2009). La banque est fictive. Comme les données sont simulées, nous connaissons la **vérité programmée** et la révélons quand elle éclaire une étude : en vraie vie, personne ne vous la donne.

- `credits_conso.csv` : **40 000 prêts à la consommation**, décrits **à la souscription**, avec l'issue observée douze mois plus tard (`defaut_12m`, environ 6 %).
- `recouvrements.csv` : 6 000 prêts **entrés en défaut**, avec la perte réellement subie (section 1.5).
- `revolving_defauts.csv` : 8 000 lignes de crédit renouvelable en défaut (section 1.5).
- `portefeuille_ifrs9.csv` : 20 000 prêts en cours, avec leur probabilité de défaut à l'origine et aujourd'hui (section 1.5).
- `taux_defaut_macro.csv` : 80 trimestres de conjoncture et de taux de défaut du portefeuille (sections 1.3 et 1.5).
- `notations_panel.csv` : 5 000 emprunteurs notés chaque année pendant dix ans (section 1.6).

```python hide
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET
import outils_ch01 as O
style.setup()
tr, te = O.charger_credits()
y_tr, y_te = tr["defaut_12m"].values, te["defaut_12m"].values
```

Voici l'allure d'un dossier : onze informations connues **au moment de la demande**, et l'issue.

```python
print(tr.drop(columns="id_credit").head(3).T.to_string())
```
<!--sortie-->
```text
                       37690      20231    31011
age                       30         21       66
revenu_annuel        15010.0    25950.0  41940.0
anciennete_emploi        7.8        0.8      8.4
logement             heberge  locataire  heberge
objet                travaux    travaux     auto
montant              18900.0     4000.0   6000.0
duree_mois                36         60       60
taux_endettement       0.519       0.06    0.331
nb_incidents_12m           0          0        0
anciennete_relation     12.7        7.1      4.4
defaut_12m                 0          0        0
```

Les variables sont celles d'un dossier de crédit à la consommation : l'âge, le revenu annuel, l'ancienneté dans l'emploi, le logement, l'objet du prêt, le montant et la durée, le **taux d'endettement** (charges mensuelles, mensualité comprise, rapportées au revenu), le nombre d'incidents de paiement des douze derniers mois, l'ancienneté de la relation avec la banque. Deux variables ont des **valeurs manquantes** : le revenu (5 %) et l'ancienneté dans l'emploi (7 %). Nous verrons que le second manque **plus souvent chez les emprunteurs risqués** : un manquant n'est pas neutre.

Le jeu est découpé **une fois pour toutes** en un échantillon de **développement** (70 %, 28 000 prêts) et un échantillon de **test** (30 %, 12 000 prêts), tous deux avec la même proportion de défauts. On n'y touche pas pendant la construction (classes, coefficients) ; il sert ensuite à mesurer des candidats **fixés d'avance**, sans réglage fait en le regardant.

```python hide
print("NUM n_tr", len(tr)); print("NUM n_te", len(te))
print("NUM taux_tr", round(float(y_tr.mean()), 4)); print("NUM taux_te", round(float(y_te.mean()), 4))
print("NUM nb_def_tr", int(y_tr.sum()))
print("NUM manq_emploi", round(float(tr["anciennete_emploi"].isna().mean()), 3))
print("NUM manq_revenu", round(float(tr["revenu_annuel"].isna().mean()), 3))
print("NUM manq_emploi_def", round(float(tr.loc[tr.anciennete_emploi.isna(), "defaut_12m"].mean()), 3))
print("NUM manq_emploi_ok", round(float(tr.loc[tr.anciennete_emploi.notna(), "defaut_12m"].mean()), 3))
```
<!--sortie-->
```text
NUM n_tr 28000
NUM n_te 12000
NUM taux_tr 0.0597
NUM taux_te 0.0597
NUM nb_def_tr 1671
NUM manq_emploi 0.07
NUM manq_revenu 0.05
NUM manq_emploi_def 0.119
NUM manq_emploi_ok 0.055
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : toutes les applications partent de ces fichiers ; commencez par l'application 1.1.
