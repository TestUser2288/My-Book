# Chapitre 5 : Évaluation, calibration et interprétabilité

> « Un modèle qui prédit bien ne vaut rien tant qu'on ne sait pas dire *à quel point*, *pour quelle décision* et *pourquoi*. »

Les quatre chapitres précédents ont appris à **construire** des modèles : séparer les données, valider, comparer des familles d'algorithmes, préparer les variables. Il reste l'essentiel : savoir ce que valent ces modèles une fois qu'on les a. Trois questions, qui reviennent à chaque projet, structurent ce chapitre.

1. **Est-il bon ?** Mais bon *pour quoi faire* ? Une exactitude de 90 % peut cacher un modèle inutile ; une AUC de 0,90 peut cacher un modèle mal réglé. Choisir la bonne mesure, et le bon seuil de décision, est un acte de métier avant d'être un acte statistique.
2. **Peut-on se fier à ses probabilités ?** Quand le modèle annonce « 30 % de risque de départ », se passe-t-il vraiment quelque chose environ trois fois sur dix ? C'est la **calibration**, condition de toute décision fondée sur un coût attendu.
3. **Pourquoi dit-il cela ?** Un modèle qui prédit sans que personne ne puisse l'expliquer est un modèle difficile à corriger, à défendre, ou à débusquer quand il triche. C'est l'**interprétabilité**.

## Le chemin de ce chapitre

- **5.1 Métriques** : de la matrice de confusion à la courbe ROC, à la courbe précision-rappel, aux coûts, au lift ; les métriques de régression.
- **5.2 Calibration** : le diagramme de fiabilité, pourquoi certains modèles mentent sur leurs probabilités, Platt, la régression isotonique, et l'effet des poids de classes.
- **5.3 Interprétabilité** : importance par permutation, effets partiels, LIME, et les valeurs de Shapley avec SHAP.
- ➕ **5.4 Équité, biais et éthique** : mesurer les écarts entre groupes sur un jeu **réel** de crédit, et ce que l'on ne peut pas avoir en même temps.
- ➕ **5.5 Prédiction conforme** : transformer n'importe quel modèle en un modèle qui annonce des *ensembles* ou des *intervalles* avec une garantie de couverture.

> 🧭 **Comment lire ce chapitre.** Les sections 5.1 à 5.3 forment le socle. Les sections 5.4 et 5.5 sont facultatives. Le livre démontre et explique ; le code qui produit chaque nombre cité est exécuté en coulisses (voir l'introduction du volume), et les exercices et applications sont dans le cahier.

## Le fil rouge : un même problème, trois modèles

Tout le chapitre s'appuie sur le même problème, celui du volume : **prédire, pour chacun des 12 000 clients de la boutique, s'il aura cessé de commander dans les 90 jours** (la variable `churn_90j`, qui vaut 1 pour 14 % des clients). Les données sont **simulées** (`clients_ml.csv`), ce qui permet de savoir ce qui a été programmé.

Conformément à la règle du chapitre 1 (section 1.1), les clients sont répartis une fois pour toutes en trois jeux, **stratifiés** sur la cible (chacun garde 14 % de partants) :

| Jeu | Clients | Rôle |
|---|---|---|
| Entraînement | 7 200 | ajuster les modèles |
| Calibration (ou validation) | 2 400 | régler les seuils, calibrer les probabilités, calibrer la prédiction conforme |
| Test | 2 400 | **évaluer une seule fois**, à la fin, sans jamais s'en servir pour décider |

Trois modèles sont ajustés sur le jeu d'entraînement, avec leurs réglages par défaut (le réglage fin est l'objet de la section 1.5) : une **régression logistique** sur variables centrées-réduites, une **forêt aléatoire** (150 arbres) et un **gradient boosting**. Voici leurs scores sur le jeu de test, mesurés avec les outils de la section suivante :

| Modèle | AUC | Précision moyenne (AP) | Log-loss | Brier |
|---|---:|---:|---:|---:|
| Régression logistique | 0,859 | 0,560 | 0,289 | 0,0872 |
| Forêt aléatoire | 0,888 | 0,624 | 0,269 | 0,0808 |
| Gradient boosting | 0,897 | 0,650 | 0,255 | 0,0758 |

Dans ce tableau, le boosting domine sur toutes les colonnes. Dans la pratique, on voudrait savoir **de combien** il domine, si la différence est due au hasard, ce qu'elle change pour la décision et si ses probabilités sont crédibles : c'est précisément ce que ce chapitre apprend à faire.

Deux jeux de données interviendront en plus : le **jeu réel** `credit_defaut.csv` (30 000 clients d'une banque, 22 % de défauts ; source : Yeh et Lien, 2009, licence CC0) pour l'équité en 5.4, et les mêmes clients de la boutique pour la prédiction conforme en 5.5.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : le chapitre tout entier est accompagné d'applications et d'exercices ; chaque section ci-dessous indique les siens.

```python hide
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings("ignore")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler
from sklearn import metrics as M

c = pd.read_csv("donnees/clients_ml.csv")
exclues = ["churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible", "id_client"]      # cibles, classe latente, FUITE, identifiant
X = pd.get_dummies(c.drop(columns=exclues), columns=["ville", "canal_acquisition", "appareil", "categorie_preferee"], dtype=float)
X["panier_manquant"] = c["panier_moyen"].isna().astype(float)
X["satisfaction_manquante"] = c["satisfaction_moy"].isna().astype(float)
y = c["churn_90j"]

# 60 % entraînement / 20 % calibration (et validation) / 20 % test, stratifiés sur la cible
Xa, Xte, ya, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
Xtr, Xca, ytr, yca = train_test_split(Xa, ya, test_size=0.25, random_state=0, stratify=ya)
med = Xtr.median()                                   # médianes calculées sur l'entraînement SEUL
Xtr, Xca, Xte = Xtr.fillna(med), Xca.fillna(med), Xte.fillna(med)
sc = StandardScaler().fit(Xtr)
lr = LogisticRegression(max_iter=3000).fit(sc.transform(Xtr), ytr)
rf = RandomForestClassifier(150, min_samples_leaf=5, random_state=0, n_jobs=1).fit(Xtr, ytr)
gb = HistGradientBoostingClassifier(random_state=0).fit(Xtr, ytr)
P = {"logistique": lr.predict_proba(sc.transform(Xte))[:, 1], "forêt": rf.predict_proba(Xte)[:, 1], "boosting": gb.predict_proba(Xte)[:, 1]}
print("tailles :", len(Xtr), len(Xca), len(Xte), "| prévalence :", round(ytr.mean(), 3), round(yca.mean(), 3), round(yte.mean(), 3))
for k, p in P.items():
    print(f"{k:11s} AUC {M.roc_auc_score(yte, p):.4f}  AP {M.average_precision_score(yte, p):.4f}  log-loss {M.log_loss(yte, p):.4f}  Brier {M.brier_score_loss(yte, p):.4f}")
```
<!--sortie-->
```text
tailles : 7200 2400 2400 | prévalence : 0.14 0.14 0.14
logistique  AUC 0.8593  AP 0.5600  log-loss 0.2886  Brier 0.0872
forêt       AUC 0.8881  AP 0.6235  log-loss 0.2687  Brier 0.0808
boosting    AUC 0.8971  AP 0.6496  log-loss 0.2548  Brier 0.0758
```
