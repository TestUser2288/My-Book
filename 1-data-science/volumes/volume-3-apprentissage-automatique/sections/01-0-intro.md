# Chapitre 1 : La démarche d'apprentissage automatique

> « Un modèle qui n'a jamais été testé sur des données neuves n'est pas un modèle : c'est une promesse. »

Les volumes I et II vous ont appris à **comprendre** des données : décrire, estimer, tester, modéliser pour expliquer. Ce volume change de question. On ne cherche plus d'abord *pourquoi* un client part, mais **lequel** partira, afin d'agir à temps : la gérante veut une liste de cent clients à contacter cette semaine. C'est le terrain de l'**apprentissage automatique** (*machine learning*, ML) : construire des modèles dont la qualité se juge à leur capacité de **prédire des cas qu'ils n'ont jamais vus**.

Ce premier chapitre est le plus important du volume, et pourtant il ne contient presque aucun « algorithme à la mode ». Il enseigne la **démarche**, c'est-à-dire la discipline qui sépare un modèle utile d'un modèle qui n'a l'air bon que sur le papier. Les chapitres suivants fourniront les modèles ; celui-ci fournit les règles du jeu. Si vous ne deviez lire qu'un chapitre de ce volume, ce serait celui-ci.

## Le chemin de ce chapitre

- **1.1 Formulation du problème et séparation des données** : qu'est-ce qu'on prédit, avec quelles informations, jugé comment ? Pourquoi on met des données de côté, et le piège numéro un : la **fuite d'information**.
- **1.2 Validation croisée** : exploiter les données au mieux sans tricher, et savoir à quel point l'estimation est incertaine.
- **1.3 Compromis biais-variance et surapprentissage** : pourquoi un modèle trop souple ou trop rigide échoue, démontré proprement.
- **1.4 Modèles de référence et rigueur expérimentale** : battre un modèle simple, comparer deux modèles avec un intervalle d'incertitude, rapporter honnêtement.
- ➕ **1.5 Réglage des hyperparamètres** : grille, recherche aléatoire, optimisation bayésienne avec Optuna, arrêt précoce, et le piège du réglage.

> 📒 **Pour s'entraîner.** Chaque section de ce chapitre renvoie à des applications et à des exercices du **cahier** (chapitre 1). Le livre explique ; le cahier fait pratiquer.

## Les données du chapitre

Presque tout le chapitre s'appuie sur un seul tableau : `clients_ml.csv`, **12 000 clients de la boutique observés au 31 décembre 2025**. Il est **simulé** (graine fixe), comme dans les volumes précédents : la vérité est connue de l'auteur, ce qui permettra à plusieurs reprises de vérifier qu'une méthode fait bien ce qu'elle prétend. La question posée est celle de la gérante : **ce client ne commandera-t-il plus dans les 90 jours qui viennent ?** Cette cible s'appelle `churn_90j` (1 : le client est parti ; 0 : il reste).

| Famille | Variables |
|---|---|
| Profil | `age`, `ville` (20 modalités), `canal_acquisition` (Boutique, Site, Réseaux), `appareil` (parfois manquant), `anciennete_mois` |
| Comportement d'achat | `nb_commandes_12m`, `panier_moyen` (manquant s'il n'y a aucune commande), `montant_12m`, `recence_jours` (jours depuis la dernière commande), `nb_retours_12m`, `part_achats_promo`, `categorie_preferee` |
| Relation | `satisfaction_moy` (manquante pour environ 13 % des clients), `nb_tickets_support_12m`, `programme_fidelite`, `nb_promos_recues_12m`, `taux_ouverture_email`, `delai_livraison_moy` |
| Contexte | `revenu_zone` (indice de la zone de résidence) |
| À prédire | `churn_90j` |

Le tableau contient aussi trois colonnes qui **ne sont pas des variables d'entrée** : `depense_6m` (la dépense future, utilisée dans d'autres chapitres), `segment_vrai` (une classe cachée, utilisée pour valider les méthodes non supervisées) et `commandes_apres_cible`, qui est un **piège volontaire**. Nous le désamorcerons à la section 1.1.6 : retenez seulement, pour l'instant, qu'on ne la donnera jamais au modèle.

```python hide
import sys, time, warnings
import numpy as np
import pandas as pd
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
sys.path.insert(0, "build")
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE2, MUET
style.setup()
from sklearn.model_selection import (train_test_split, cross_val_score, cross_validate, StratifiedKFold, KFold,
                                     RepeatedStratifiedKFold, GroupKFold, TimeSeriesSplit, ShuffleSplit, learning_curve, validation_curve)
from sklearn.metrics import roc_auc_score, average_precision_score
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.dummy import DummyClassifier

df = pd.read_csv("donnees/clients_ml.csv")
CATEG = ["ville", "canal_acquisition", "appareil", "categorie_preferee"]
NUM = [c for c in df.columns if c not in CATEG + ["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"]]
X = df[NUM + CATEG].copy()
for c in CATEG:
    X[c] = X[c].astype("category")
y = df["churn_90j"]

def modele_logit(C=1.0):
    prep = ColumnTransformer([("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), NUM),
                              ("cat", OneHotEncoder(handle_unknown="ignore"), CATEG)])
    return make_pipeline(prep, LogisticRegression(C=C, max_iter=2000))

def modele_hgb(**kw):
    return HistGradientBoostingClassifier(categorical_features="from_dtype", random_state=0, **kw)

X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
print(X.shape, round(y.mean(), 4), X_tr.shape, X_te.shape, round(y_tr.mean(), 4), round(y_te.mean(), 4))
print("valeurs manquantes :", X.isna().sum()[X.isna().sum() > 0].to_dict())
```
<!--sortie-->
```text
(12000, 19) 0.1404 (9000, 19) (3000, 19) 0.1404 0.1403
valeurs manquantes : {'panier_moyen': 1630, 'satisfaction_moy': 1533, 'delai_livraison_moy': 1434, 'appareil': 1829}
```

Sur les 12 000 clients, **14,0 %** sont partis (environ 1 685) : le problème est **déséquilibré** (nous y reviendrons au chapitre 4), et quatre variables ont des valeurs manquantes, de 12 % à 15 % des clients selon la variable (le panier moyen manque pour 1 630 clients, qui n'ont passé aucune commande). Dans tout le chapitre, deux modèles servent de fil conducteur, volontairement très différents : une **régression logistique** (le modèle du volume II, section 2.2) et un **gradient boosting** (un ensemble d'arbres, étudié en détail à la section 2.4 : ici, on l'utilise comme une boîte performante). Ils jouent le rôle de deux « candidats » à comparer avec rigueur.

> 🧭 **Comment lire ce chapitre.** Le code qui produit les figures et les chiffres cités est **exécuté mais masqué** : le livre ne montre que de courts extraits quand ils aident à comprendre. Les applications complètes, avec tout leur code, sont dans le **cahier**.
