# Chapitre 4 : Ingénierie des variables et données déséquilibrées

> « Les algorithmes ne voient pas vos données : ils voient les nombres que vous leur donnez. »

Les chapitres précédents ont traité du **modèle** : comment l'évaluer (chapitre 1), quelles familles choisir (chapitre 2). Ce chapitre s'occupe de ce qui se passe **avant** le modèle : la façon dont on **présente** les données à l'algorithme. Un même modèle, sur les mêmes clients, peut passer d'un résultat médiocre à un très bon résultat selon la manière dont une ville est codée, dont une valeur manquante est remplacée, ou dont une règle de bon sens est transformée en variable. Et il peut se tromper de façon spectaculaire, tout en affichant 99 % d'exactitude, quand ce qu'il doit détecter est rare.

## Le chemin de ce chapitre

- **4.1 Encodage, mise à l'échelle, transformations** : transformer des catégories, des unités et des valeurs manquantes en nombres que les modèles savent lire, **sans fuite d'information** ; assembler le tout dans un `Pipeline`.
- **4.2 Création et sélection de variables** : fabriquer des variables qui expriment ce que l'on sait du métier, découvrir des seuils à partir des données, repérer redondances et fuites.
- **4.3 Classes déséquilibrées** : pourquoi l'exactitude trompe, ce que font réellement les poids de classes, le rééchantillonnage, et le rôle décisif du **seuil de décision** et des **coûts**.
- ➕ **4.4 Méthodes de sélection de variables** : filtre, enveloppe, méthodes intégrées, et le piège du biais de sélection.
- ➕ **4.5 SMOTE et variantes** : fabriquer des exemples synthétiques, et surtout savoir quand ne pas le faire.
- **Bilan du chapitre**.

> 🧭 **Fil rouge du chapitre : l'ordre des opérations.** Presque toutes les erreurs graves de ce chapitre ont la même forme : une opération qui *apprend quelque chose des données* (une moyenne, une catégorie fréquente, un seuil, un échantillon synthétique) est appliquée **avant** la séparation entre entraînement et validation. Le jeu de validation « sait » alors des choses sur lui-même, et la performance affichée est trop belle. Retenez la règle ; nous la rencontrerons cinq fois : **tout ce qui est appris est appris sur le jeu d'entraînement, et seulement lui** (chapitre 1, section 1.1).

## Les données du chapitre

Deux fichiers de la boutique servent d'exemples (tous deux **simulés** ; voir l'introduction du volume).

| Fichier | Contenu | Cible | Sert pour |
|---|---|---|---|
| `clients_ml.csv` | 12 000 clients observés au 31 décembre 2025 : âge, ville (20 modalités), canal d'acquisition, activité des 12 derniers mois, satisfaction, assistance, promotions… | `churn_90j` : le client ne commande plus dans les 90 jours suivants (14 % des clients) | encodage, échelles, valeurs manquantes, création de variables, sélection |
| `transactions.csv` | 60 000 commandes en ligne : montant, heure, appareil, distance entre adresses, ancienneté du compte… | `fraude` : la commande est frauduleuse (0,8 % des commandes) | classes déséquilibrées, SMOTE |

```python hide
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.metrics import roc_auc_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
GRIS = "#898781"

clients = pd.read_csv("donnees/clients_ml.csv")
y = clients["churn_90j"]
tr, te = train_test_split(clients.index, test_size=0.25, random_state=0, stratify=y)
ytr, yte = y[tr], y[te]

NUM = ["age", "anciennete_mois", "nb_commandes_12m", "montant_12m", "recence_jours", "nb_retours_12m",
       "nb_tickets_support_12m", "programme_fidelite", "nb_promos_recues_12m", "part_achats_promo",
       "taux_ouverture_email", "satisfaction_moy", "delai_livraison_moy", "panier_moyen"]


def auc_logit(X, **kw):
    """AUC test d'une régression logistique (imputation médiane + indicateurs, standardisation) sur le découpage fixé."""
    m = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(), LogisticRegression(max_iter=3000, **kw))
    m.fit(X.loc[tr], ytr)
    return round(roc_auc_score(yte, m.predict_proba(X.loc[te])[:, 1]), 3)


def auc_gbm(X):
    """AUC test d'un gradient boosting (valeurs manquantes gérées nativement) sur le découpage fixé."""
    m = HistGradientBoostingClassifier(random_state=0, max_iter=100).fit(X.loc[tr], ytr)
    return round(roc_auc_score(yte, m.predict_proba(X.loc[te])[:, 1]), 3)


print(len(clients), "clients ;", len(tr), "pour l'entraînement,", len(te), "pour le test ; part de départs :", round(y.mean(), 3))
print("référence sur les 14 variables numériques brutes : logistique", auc_logit(clients[NUM]), "| boosting", auc_gbm(clients[NUM]))
```
<!--sortie-->
```text
12000 clients ; 9000 pour l'entraînement, 3000 pour le test ; part de départs : 0.14
référence sur les 14 variables numériques brutes : logistique 0.858 | boosting 0.892
```

Le découpage entraînement/test (75 % / 25 %, stratifié sur la cible, graine fixée) est le même dans tout le chapitre ; il est fait **une fois pour toutes, avant** tout apprentissage. Sur les variables numériques brutes, une régression logistique atteint une AUC de 0,858 sur le jeu de test et un gradient boosting 0,892 : ce sont nos **points de départ**. Les sections qui suivent montrent ce que valent, ou ne valent pas, les différentes façons de préparer les variables.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : le chapitre du cahier commence par une section « Préparation » qui recharge ces données et refait ce découpage.
