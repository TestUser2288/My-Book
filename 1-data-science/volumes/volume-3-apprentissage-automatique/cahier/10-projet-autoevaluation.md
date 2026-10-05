# Projet du volume et auto-évaluation — exercices et applications

> 🧭 Ce chapitre du cahier clôt le volume III. Il contient **le projet du volume** (un pipeline d'apprentissage automatique complet sur un jeu de données **réel**, du modèle de référence à l'interprétation), puis l'**auto-évaluation**. Il ne demande aucune notion nouvelle : chaque étape renvoie à la section du livre qui l'explique. Le plus profitable : lire le cahier des charges, essayer seul, puis comparer.

## Projet du volume

### P.1 Le cahier des charges

Un établissement de crédit possède l'historique de **30 000 clients** titulaires d'une carte de crédit : limite de crédit, âge, situation, six mois d'historique de retards, de factures et de paiements. Pour chacun, on sait si le client a **fait défaut le mois suivant** (22 % des cas). Il veut un **modèle de risque** pour décider qui contacter en priorité (relance, révision de la limite).

> 📦 **Les données sont réelles.** Il s'agit du jeu « Default of Credit Card Clients » de l'UCI, publié sous licence CC0 (Yeh et Lien, 2009) : 30 000 clients d'une banque d'Asie en 2005. Le fichier `donnees/credit_defaut.csv` est fourni, aucune connexion n'est nécessaire. Les colonnes sont décrites en tête de `build/telecharger_credit.py`. Contrairement aux données simulées de la boutique, **on ne connaît pas la vérité** : on ne peut que mesurer, comparer et rester prudent.

La méthode suit onze étapes, chacune appuyée sur un chapitre du livre :

| Étape | Question | Chapitre du livre |
|---|---|---|
| P.2 Cadrer | Quelle décision ? Quelle métrique ? Quel coût d'erreur ? | 1.1, 5.1 |
| P.3 Auditer | Les données sont-elles saines ? Y a-t-il une fuite ? | 1.1, 4.1 |
| P.4 Séparer et références | Quel est le score à battre ? | 1.1, 1.4 |
| P.5 Variables | Peut-on aider le modèle ? | 4.1, 4.2 |
| P.6 Comparer | Quel modèle, avec quelle incertitude ? | 1.2, 2.1 à 2.4 |
| P.7 Régler | Que gagne-t-on à ajuster les hyperparamètres ? | 1.5 |
| P.8 Décider | Quel seuil, au vu des coûts ? | 4.3.5, 5.1.7 |
| P.9 Calibrer | Les probabilités sont-elles fiables ? | 5.2 |
| P.10 Évaluer une fois | Combien vaut le modèle final, avec sa marge d'erreur ? | 1.1, 1.4, 5.1 |
| P.11 Comprendre et vérifier l'équité | Pourquoi ces prédictions ? Sont-elles équitables ? | 5.3, 5.4 |
| P.12 Rapporter | Que dire, avec quelles limites ? | 1.4 |

### P.2 Étape 1 : cadrer

Avant de coder, on écrit **ce que le modèle servira à décider**. Ici : classer les clients par risque de défaut pour **choisir qui relancer**, avec un budget de contacts limité. Deux conséquences :

- on a besoin d'un **bon classement** (AUC, précision moyenne) et de **probabilités fiables** (calibration), pas seulement d'une étiquette ;
- les deux erreurs ne coûtent pas la même chose. Nous posons une **hypothèse de coût**, à discuter avec le métier : laisser passer un défaut coûte **5 unités**, une relance inutile en coûte **1** (livre, section 5.1.7).

La métrique principale sera la **précision moyenne** (*average precision*, section 5.1) car la classe positive est minoritaire, avec l'AUC et le **coût attendu** en complément. Les décisions de modélisation se prendront sur des données d'**entraînement** et de **validation** ; le **jeu de test** ne sera utilisé **qu'une fois**, à l'étape P.10.

### P.3 Étape 2 : auditer les données

```python
import warnings
import numpy as np
import pandas as pd

warnings.filterwarnings("ignore")
d = pd.read_csv("donnees/credit_defaut.csv")
print(d.shape, "| taux de défaut :", round(d["default"].mean(), 4), "| valeurs manquantes :", int(d.isna().sum().sum()))
for col in ["sex", "education", "marriage"]:
    print(col, d[col].value_counts().sort_index().to_dict())
print("pay_1 :", d["pay_1"].value_counts().sort_index().to_dict())
```
<!--sortie-->
```text
(30000, 24) | taux de défaut : 0.2212 | valeurs manquantes : 0
sex {1: 11888, 2: 18112}
education {0: 14, 1: 10585, 2: 14030, 3: 4917, 4: 123, 5: 280, 6: 51}
marriage {0: 54, 1: 13659, 2: 15964, 3: 323}
pay_1 : {-2: 2759, -1: 5686, 0: 14737, 1: 3688, 2: 2667, 3: 322, 4: 76, 5: 26, 6: 11, 7: 9, 8: 19}
```

Trois constats d'audit (livre, section 4.1) :

1. **Aucune valeur manquante**, mais des **codes non documentés** : `education` prend les valeurs 0, 5 et 6 et `marriage` la valeur 0, que la documentation ne prévoit pas. On les regroupera avec la modalité « autre ».
2. `pay_1` à `pay_6` mêlent des **états** (−2, −1, 0 : pas de retard) et des **mois de retard** (1 à 8) : c'est une variable ordinale, pas une grandeur continue.
3. **Pas de fuite évidente** : toutes les colonnes décrivent l'historique de septembre à avril, la cible porte sur le mois suivant. En revanche, **le jeu n'a pas de date par client** : on ne peut pas faire de séparation temporelle, et on le reconnaîtra dans les limites.

### P.4 Étape 3 : séparer et fixer des références

On sépare **60 % / 20 % / 20 %** (entraînement, validation, test) en conservant la proportion de défauts dans chaque jeu (stratification), avec une graine fixe.

```python
from sklearn.model_selection import train_test_split

X, y = d.drop(columns="default"), d["default"]
X_tv, X_te, y_tv, y_te = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
X_tr, X_va, y_tr, y_va = train_test_split(X_tv, y_tv, test_size=0.25, random_state=42, stratify=y_tv)
print(len(X_tr), len(X_va), len(X_te), "| taux de défaut :", [round(float(v.mean()), 3) for v in (y_tr, y_va, y_te)])
```
<!--sortie-->
```text
18000 6000 6000 | taux de défaut : [0.221, 0.221, 0.221]
```

Les **références** (livre, section 1.4) fixent le score à battre : prédire toujours la proportion de défauts, appliquer une **règle simple** (« défaut si au moins un mois de retard au dernier relevé »), et une **régression logistique** standardisée.

```python
from sklearn.dummy import DummyClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import average_precision_score, brier_score_loss, roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

def scores(nom, p):
    return {"modèle": nom, "AUC": roc_auc_score(y_va, p), "précision moy.": average_precision_score(y_va, p), "Brier": brier_score_loss(y_va, np.clip(p, 0, 1))}

dummy = DummyClassifier(strategy="prior").fit(X_tr, y_tr)
logit = make_pipeline(StandardScaler(), LogisticRegression(max_iter=2000)).fit(X_tr, y_tr)
refs = pd.DataFrame([scores("toujours la proportion", dummy.predict_proba(X_va)[:, 1]),
                     scores("règle : retard ≥ 1 mois", (X_va["pay_1"] >= 1).astype(float)),
                     scores("régression logistique", logit.predict_proba(X_va)[:, 1])])
print(refs.round(4).to_string(index=False))
```
<!--sortie-->
```text
                 modèle    AUC  précision moy.  Brier
 toujours la proportion 0.5000          0.2212 0.1723
règle : retard ≥ 1 mois 0.6793          0.3602 0.2222
  régression logistique 0.7242          0.4978 0.1455
```

La règle à une ligne obtient déjà une AUC de 0,68 ; la régression logistique atteint 0,72. Tout modèle plus complexe devra **justifier son surcroît de complexité** par un gain mesuré.

### P.5 Étape 4 : des variables qui parlent au métier

Le livre (section 4.2) rappelle que de bonnes variables valent souvent mieux qu'un modèle plus complexe. Ici, le **raisonnement métier** suggère trois familles :

- le **taux d'utilisation** de la limite : facture divisée par limite de crédit ;
- le **taux de remboursement** : paiement divisé par la facture du mois ;
- des **résumés de l'historique de retards** : nombre de mois en retard, retard maximal, retard moyen.

On les écrit dans une fonction **sans état** (elle n'apprend rien sur les données : pas de risque de fuite), puis on la place dans un `Pipeline`.

```python
def variables(X):
    X = X.copy()
    for k in range(1, 7):
        X[f"util_{k}"] = X[f"bill_amt{k}"] / X["limit_bal"]
        X[f"ratio_paiement_{k}"] = X[f"pay_amt{k}"] / (X[f"bill_amt{k}"].abs() + 1)
    retards = [f"pay_{k}" for k in range(1, 7)]
    X["nb_mois_retard"] = (X[retards] > 0).sum(axis=1)
    X["retard_max"], X["retard_moyen"] = X[retards].max(axis=1), X[retards].mean(axis=1)
    X["education"] = X["education"].replace({0: 4, 5: 4, 6: 4})
    X["marriage"] = X["marriage"].replace({0: 3})
    return X

F_tr, F_va = variables(X_tr), variables(X_va)
logit_f = make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)).fit(F_tr, y_tr)
print(pd.DataFrame([scores("logistique, variables brutes", logit.predict_proba(X_va)[:, 1]),
                    scores("logistique, variables métier", logit_f.predict_proba(F_va)[:, 1])]).round(4).to_string(index=False))
```
<!--sortie-->
```text
                      modèle    AUC  précision moy.  Brier
logistique, variables brutes 0.7242          0.4978 0.1455
logistique, variables métier 0.7525          0.5046 0.1412
```

Le modèle **linéaire** gagne environ 0,03 d'AUC (0,724 → 0,753) ; la précision moyenne progresse peu (0,498 → 0,505). Les variables métier résument l'historique sous une forme plus directement exploitable par un modèle linéaire, mais le gros du signal était déjà dans `pay_1`.

### P.6 Étape 5 : comparer des modèles, avec leur incertitude

On compare trois familles (livre, chapitre 2) par **validation croisée à 5 plis répétée** sur le jeu d'entraînement : la même découpe pour tous les modèles, de sorte que l'on puisse comparer les scores **pli par pli** (comparaison appariée, section 1.4).

```python
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import RepeatedStratifiedKFold, cross_val_score

cv = RepeatedStratifiedKFold(n_splits=5, n_repeats=2, random_state=0)
modeles = {
    "logistique": make_pipeline(StandardScaler(), LogisticRegression(max_iter=3000)),
    "forêt aléatoire": RandomForestClassifier(100, min_samples_leaf=5, random_state=0, n_jobs=2),
    "boosting": HistGradientBoostingClassifier(random_state=0),
}
cv_scores = {nom: cross_val_score(m, F_tr, y_tr, cv=cv, scoring="average_precision") for nom, m in modeles.items()}
tab = pd.DataFrame({n: [s.mean(), s.std(ddof=1)] for n, s in cv_scores.items()}, index=["moyenne", "écart-type des plis"]).T
print(tab.round(4).to_string())
```
<!--sortie-->
```text
                 moyenne  écart-type des plis
logistique        0.5125               0.0107
forêt aléatoire   0.5538               0.0119
boosting          0.5585               0.0128
```

Les scores des plis sont **corrélés** (les jeux d'entraînement se recouvrent) : un test de Student naïf sur leur différence serait trop optimiste. On utilise la **correction de Nadeau-Bengio** (livre, section 1.4.2), qui gonfle la variance du facteur $\frac1k+\frac{n_{test}}{n_{train}}$ :

```python
from scipy import stats

def difference_corrigee(a, b, n_test_sur_train=0.25):
    diff = np.asarray(a) - np.asarray(b)
    k = len(diff)
    t = diff.mean() / np.sqrt((1 / k + n_test_sur_train) * diff.var(ddof=1))
    return diff.mean(), 2 * stats.t.sf(abs(t), k - 1)

for a, b in [("boosting", "logistique"), ("forêt aléatoire", "logistique"), ("boosting", "forêt aléatoire")]:
    ecart, p = difference_corrigee(cv_scores[a], cv_scores[b])
    print(f"{a:16s} - {b:16s} : écart de précision moyenne = {ecart:+.4f}   p corrigée = {p:.4f}")
```
<!--sortie-->
```text
boosting         - logistique       : écart de précision moyenne = +0.0460   p corrigée = 0.0000
forêt aléatoire  - logistique       : écart de précision moyenne = +0.0413   p corrigée = 0.0000
boosting         - forêt aléatoire  : écart de précision moyenne = +0.0048   p corrigée = 0.0639
```

Lecture : le boosting et la forêt battent la régression logistique d'environ 0,04 à 0,05 de précision moyenne, un écart **nettement supérieur au bruit** des plis (p corrigée proche de 0). En revanche, l'avantage du boosting sur la forêt (0,005) est **trop petit pour être établi** : la p-valeur corrigée (0,064) ne passe pas le seuil de 5 %. On retiendra le boosting pour sa rapidité d'entraînement et parce qu'il se prête mieux au réglage, pas parce qu'il serait prouvé meilleur.

### P.7 Étape 6 : régler le boosting avec un budget limité

Le **réglage** est une optimisation : on la fait **sur l'entraînement uniquement**, avec la validation croisée, jamais sur le test (section 1.5). Un budget de **20 essais** d'Optuna explore la profondeur, le pas d'apprentissage et la régularisation d'un boosting LightGBM.

```python
import lightgbm as lgb
import optuna
from sklearn.model_selection import StratifiedKFold

optuna.logging.set_verbosity(optuna.logging.WARNING)
cv3 = StratifiedKFold(n_splits=3, shuffle=True, random_state=1)

def objectif(trial):
    params = dict(n_estimators=300, learning_rate=trial.suggest_float("learning_rate", 0.01, 0.2, log=True),
                  num_leaves=trial.suggest_int("num_leaves", 4, 64, log=True), min_child_samples=trial.suggest_int("min_child_samples", 10, 200, log=True),
                  reg_lambda=trial.suggest_float("reg_lambda", 1e-3, 30, log=True), subsample=0.8, subsample_freq=1,
                  colsample_bytree=trial.suggest_float("colsample_bytree", 0.4, 1.0), random_state=0, n_jobs=2, verbose=-1)
    return cross_val_score(lgb.LGBMClassifier(**params), F_tr, y_tr, cv=cv3, scoring="average_precision").mean()

etude = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=0))
etude.optimize(objectif, n_trials=20)
print("meilleure précision moyenne en validation croisée :", round(etude.best_value, 4))
print({k: round(v, 4) if isinstance(v, float) else v for k, v in etude.best_params.items()})
```
<!--sortie-->
```text
meilleure précision moyenne en validation croisée : 0.5648
{'learning_rate': 0.0349, 'num_leaves': 10, 'min_child_samples': 32, 'reg_lambda': 0.0018, 'colsample_bytree': 0.9249}
```

```python
base = cross_val_score(lgb.LGBMClassifier(n_estimators=300, random_state=0, n_jobs=2, verbose=-1), F_tr, y_tr, cv=cv3, scoring="average_precision").mean()
print(f"LightGBM par défaut : {base:.4f}  |  réglé : {etude.best_value:.4f}  |  gain : {etude.best_value - base:+.4f}")
```
<!--sortie-->
```text
LightGBM par défaut : 0.5383  |  réglé : 0.5648  |  gain : +0.0265
```

Le réglage apporte **+0,027 de précision moyenne** (0,538 → 0,565, soit environ 5 % de mieux) : un gain réel mais modeste, obtenu avec 20 essais seulement. Notons que le meilleur score de la validation croisée est **légèrement optimiste** (on a retenu le maximum de 20 essais) : c'est l'une des raisons pour lesquelles on garde un jeu de test intact.

### P.8 Étape 7 : choisir un seuil, en fonction des coûts

On ajuste le modèle réglé sur l'entraînement et on regarde le classement sur la **validation**. Pour décider **qui relancer**, il faut un **seuil**. Avec nos coûts (5 pour un défaut manqué, 1 pour une relance inutile), relancer un client est rentable dès que sa probabilité de défaut dépasse $\frac{1}{1+5}\approx 0{,}167$ (livre, section 5.1.7). On vérifie sur la validation en balayant les seuils.

```python
modele = lgb.LGBMClassifier(n_estimators=300, **{**etude.best_params}, subsample=0.8, subsample_freq=1, random_state=0, n_jobs=2, verbose=-1).fit(F_tr, y_tr)
p_va = modele.predict_proba(F_va)[:, 1]
cout = lambda seuil, y, p: 5 * np.sum((p < seuil) & (y == 1)) + 1 * np.sum((p >= seuil) & (y == 0))
seuils = np.linspace(0.05, 0.6, 56)
couts = np.array([cout(s, y_va.to_numpy(), p_va) for s in seuils])
s_opt = seuils[couts.argmin()]
print(f"seuil théorique 1/6 = {1/6:.3f} | seuil qui minimise le coût sur la validation = {s_opt:.2f}")
print(f"coût à ce seuil : {couts.min():.0f} | coût de « ne relancer personne » : {5 * y_va.sum()} | coût de « relancer tout le monde » : {(y_va == 0).sum()}")
print(f"à ce seuil : {np.mean(p_va >= s_opt):.1%} des clients relancés, {np.mean(p_va[y_va == 1] >= s_opt):.1%} des défauts attrapés")
seuils_voisins = [round(float(s_opt) - 0.05, 2), round(float(s_opt), 2), round(float(s_opt) + 0.05, 2)]
print("coûts aux seuils", seuils_voisins, ":", [int(cout(s, y_va.to_numpy(), p_va)) for s in seuils_voisins])
print(f"AUC en validation du modèle réglé : {roc_auc_score(y_va, p_va):.4f}")
```
<!--sortie-->
```text
seuil théorique 1/6 = 0.167 | seuil qui minimise le coût sur la validation = 0.17
coût à ce seuil : 3205 | coût de « ne relancer personne » : 6635 | coût de « relancer tout le monde » : 4673
à ce seuil : 41.5% des clients relancés, 74.4% des défauts attrapés
coûts aux seuils [0.12, 0.17, 0.22] : [3342, 3205, 3392]
AUC en validation du modèle réglé : 0.7873
```

Le seuil qui minimise le coût sur la validation (0,17) coïncide avec le seuil théorique (1/6), ce qui est rassurant : c'est le signe que les probabilités sont correctes. Relancer selon le modèle divise le coût par plus de deux par rapport à ne relancer personne (3 205 contre 6 635) et le réduit d'environ un tiers par rapport à relancer tout le monde (4 673). Les coûts aux seuils voisins (0,12 et 0,22 : 3 342 et 3 392, contre 3 205) montrent que la courbe est assez plate autour de l'optimum (+4 à +6 %) : mieux vaut un seuil choisi **d'après les coûts** qu'un 0,5 pris par habitude, mais sa valeur exacte compte peu.

### P.9 Étape 8 : les probabilités sont-elles fiables ?

Le seuil théorique $\frac16$ n'est valable que si les **probabilités sont calibrées** (livre, section 5.2). Vérifions par un **diagnostic de fiabilité** : on groupe les clients par probabilité prédite et on compare à la fréquence observée.

```python
from sklearn.calibration import calibration_curve

frac, moy = calibration_curve(y_va, p_va, n_bins=8, strategy="quantile")
print(pd.DataFrame({"probabilité prédite moyenne": moy, "fréquence observée": frac}).round(3).to_string(index=False))
```
<!--sortie-->
```text
 probabilité prédite moyenne  fréquence observée
                       0.041               0.052
                       0.068               0.075
                       0.098               0.091
                       0.131               0.131
                       0.164               0.167
                       0.224               0.235
                       0.355               0.349
                       0.660               0.671
```

Les probabilités prédites et les fréquences observées sont proches dans les huit groupes (par exemple 0,164 prédit contre 0,167 observé près du seuil de 0,17) : le modèle est **bien calibré**. C'est en partie parce qu'on l'a entraîné **sans pondérer les classes ni rééchantillonner** : ces techniques déforment les probabilités (livre, section 5.2). Si le modèle n'avait pas été calibré, on aurait appliqué une **régression isotonique** ou la méthode de Platt, **à l'intérieur de la validation croisée**.

### P.10 Étape 9 : évaluer une seule fois sur le test

Le modèle est figé : variables, hyperparamètres, seuil. On l'**ajuste sur l'ensemble entraînement + validation** et on l'évalue **une seule fois** sur le test. Pour exprimer l'incertitude, on calcule un **intervalle de confiance par bootstrap** du jeu de test (livre, section 1.4).

```python
F_tv, F_te = variables(X_tv), variables(X_te)
final = lgb.LGBMClassifier(n_estimators=300, **etude.best_params, subsample=0.8, subsample_freq=1, random_state=0, n_jobs=2, verbose=-1).fit(F_tv, y_tv)
p_te = final.predict_proba(F_te)[:, 1]
rng = np.random.default_rng(7)
boot = []
for _ in range(500):
    i = rng.integers(0, len(y_te), len(y_te))
    boot.append((roc_auc_score(y_te.iloc[i], p_te[i]), average_precision_score(y_te.iloc[i], p_te[i])))
boot = np.array(boot)
for j, nom in enumerate(["AUC", "précision moyenne"]):
    print(f"{nom:18s}: {[roc_auc_score, average_precision_score][j](y_te, p_te):.4f}   IC95 bootstrap [{np.percentile(boot[:, j], 2.5):.4f} ; {np.percentile(boot[:, j], 97.5):.4f}]")
print(f"coût au seuil {s_opt:.2f} : {cout(s_opt, y_te.to_numpy(), p_te):.0f}  (référence « ne relancer personne » : {5 * y_te.sum()})")
```
<!--sortie-->
```text
AUC               : 0.7822   IC95 bootstrap [0.7680 ; 0.7972]
précision moyenne : 0.5604   IC95 bootstrap [0.5343 ; 0.5887]
coût au seuil 0.17 : 3353  (référence « ne relancer personne » : 6635)
```

L'AUC sur le test (0,782) est proche de celle mesurée en validation (ligne « AUC en validation » de l'étape P.8) : pas de signe de sur-ajustement au jeu de validation. Surtout, **l'intervalle de confiance** rappelle l'incertitude : il s'étend sur environ ±0,015, de sorte que des différences d'AUC de quelques millièmes entre deux modèles seraient du bruit. Enfin le coût au seuil retenu (3 353) reste environ moitié de celui de « ne relancer personne » (6 635).

### P.11 Étape 10 : comprendre, puis vérifier l'équité

**Pourquoi** ces prédictions ? Deux outils (livre, section 5.3) : l'**importance par permutation** (global, calculée sur le test) et les **valeurs de SHAP** (global et local).

```python
from sklearn.inspection import permutation_importance

pi = permutation_importance(final, F_te, y_te, scoring="average_precision", n_repeats=5, random_state=0, n_jobs=2)
imp = pd.Series(pi.importances_mean, index=F_te.columns).sort_values(ascending=False)
print(imp.head(8).round(4).to_string())
```
<!--sortie-->
```text
pay_1             0.0973
retard_max        0.0310
bill_amt1         0.0145
nb_mois_retard    0.0124
retard_moyen      0.0079
pay_amt1          0.0047
limit_bal         0.0040
pay_amt2          0.0037
```

```python
import shap

echantillon = F_te.sample(500, random_state=0)
valeurs = shap.TreeExplainer(final).shap_values(echantillon)
valeurs = valeurs[1] if isinstance(valeurs, list) else valeurs
moy_abs = pd.Series(np.abs(valeurs).mean(axis=0), index=F_te.columns).sort_values(ascending=False)
print(moy_abs.head(8).round(3).to_string())
```
<!--sortie-->
```text
pay_1             0.289
retard_max        0.289
nb_mois_retard    0.157
bill_amt1         0.124
util_2            0.106
pay_amt2          0.097
limit_bal         0.095
pay_amt1          0.085
```

Les deux méthodes classent en tête l'**historique de retards** : `pay_1` (le statut de septembre), `retard_max` et `nb_mois_retard`, suivis par des montants de factures et de paiements. C'est ce que le métier attendrait ; la valeur de `pay_1` est loin devant les autres dans l'importance par permutation (0,097 contre 0,031 pour la suivante). L'importance **n'est pas une causalité** : « le retard de septembre fait monter le risque » décrit ce que le modèle utilise, pas ce qui arriverait si l'on intervenait sur le retard.

**Équité.** Le jeu contient des attributs **sensibles** (sexe, âge, situation). Même si le modèle ne les utilise pas comme principale information, on doit **vérifier** s'il traite les groupes de façon comparable (livre, section 5.4). Nous ne les avons pas exclus du modèle ; nous mesurons trois indicateurs par groupe, au seuil retenu : le **taux de clients relancés**, le **taux de défauts attrapés** (rappel) et le **taux de fausses relances**.

```python
def par_groupe(var, groupes):
    lignes = []
    for g, idx in groupes.items():
        y_g, p_g = y_te[idx].to_numpy(), p_te[idx.to_numpy()]
        sel = p_g >= s_opt
        lignes.append({var: g, "clients": len(y_g), "taux de défaut": y_g.mean(), "relancés": sel.mean(),
                       "défauts attrapés": sel[y_g == 1].mean(), "fausses relances": sel[y_g == 0].mean()})
    return pd.DataFrame(lignes)

sexe = X_te["sex"].map({1: "homme", 2: "femme"})
print(par_groupe("sexe", {g: sexe == g for g in ["homme", "femme"]}).round(3).to_string(index=False))
tranche = pd.cut(X_te["age"], [0, 29, 39, 49, 120], labels=["< 30", "30-39", "40-49", "50 et +"])
print(par_groupe("âge", {g: tranche == g for g in tranche.cat.categories}).round(3).to_string(index=False))
```
<!--sortie-->
```text
 sexe  clients  taux de défaut  relancés  défauts attrapés  fausses relances
homme     2402           0.234     0.463             0.754             0.374
femme     3598           0.213     0.402             0.718             0.316
    âge  clients  taux de défaut  relancés  défauts attrapés  fausses relances
   < 30     1912           0.223     0.439             0.754             0.348
  30-39     2198           0.206     0.392             0.717             0.308
  40-49     1341           0.233     0.434             0.721             0.347
50 et +      549           0.246     0.497             0.748             0.415
```

Lecture chiffrée. Les hommes sont relancés plus souvent que les femmes (46 % contre 40 %), ce qui va avec un taux de défaut plus élevé (23 % contre 21 %) ; leur rappel est un peu plus haut (75 % contre 72 %), mais ils subissent aussi plus de fausses relances (37 % contre 32 %). Par âge, c'est le groupe des 50 ans et plus qui est le plus relancé (50 %) et celui qui a le plus de fausses relances (42 %), mais il ne compte que 549 clients : ses taux sont peu précis.

> ⚠️ **Lecture prudente.** Des écarts de taux **ne prouvent pas** une discrimination, et leur absence ne prouve pas l'équité : les groupes ont des taux de défaut de base différents, et les critères d'équité (parité, égalité des chances, calibration) **ne peuvent pas tous être satisfaits en même temps** quand ces taux diffèrent (livre, section 5.4). Un tel tableau sert à **ouvrir la discussion** avec les juristes et le métier : quels écarts sont acceptables ? quel critère privilégier ? l'usage de l'âge ou du sexe est-il licite dans le contexte ? Ce ne sont pas des questions que le modèle peut trancher seul.

### P.12 Étape 11 : le rapport

Comme dans les volumes précédents, le rapport est **généré à partir des résultats déjà calculés**, sans nombre recopié à la main.

```python
def fr(x, d=1):
    return f"{x:,.{d}f}".replace(",", " ").replace(".", ",")

ic_auc = np.percentile(boot[:, 0], [2.5, 97.5])
rapport = f"""RAPPORT : MODÈLE DE RISQUE DE DÉFAUT
{"=" * 60}
Données : {fr(len(d), 0)} clients, taux de défaut {fr(100 * d['default'].mean())} %. Séparation 60/20/20, graine fixe.

1. Références (validation)
   - règle « retard ≥ 1 mois » : AUC {fr(roc_auc_score(y_va, (X_va['pay_1'] >= 1).astype(float)), 3)}
   - régression logistique     : AUC {fr(roc_auc_score(y_va, logit.predict_proba(X_va)[:, 1]), 3)}

2. Modèle retenu : boosting (LightGBM) sur variables métier, hyperparamètres réglés (20 essais)
   - test, une seule évaluation : AUC {fr(roc_auc_score(y_te, p_te), 3)} (IC95 : {fr(ic_auc[0], 3)} à {fr(ic_auc[1], 3)})
   - seuil de relance {fr(s_opt, 2)} (coût défaut manqué = 5, relance inutile = 1) : {fr(100 * np.mean(p_te >= s_opt))} % des clients relancés,
     {fr(100 * np.mean(p_te[y_te == 1] >= s_opt))} % des défauts attrapés

3. Limites
   - un seul établissement, une seule période, pas de date par client : pas de test hors temps ;
   - coûts des erreurs supposés, à valider avec le métier ;
   - importance et valeurs de SHAP décrivent le modèle, pas des causes ;
   - indicateurs d'équité calculés pour le sexe et l'âge : à discuter, pas à conclure.
"""
print(rapport)
```
<!--sortie-->
```text
RAPPORT : MODÈLE DE RISQUE DE DÉFAUT
============================================================
Données : 30 000 clients, taux de défaut 22,1 %. Séparation 60/20/20, graine fixe.

1. Références (validation)
   - règle « retard ≥ 1 mois » : AUC 0,679
   - régression logistique     : AUC 0,724

2. Modèle retenu : boosting (LightGBM) sur variables métier, hyperparamètres réglés (20 essais)
   - test, une seule évaluation : AUC 0,782 (IC95 : 0,768 à 0,797)
   - seuil de relance 0,17 (coût défaut manqué = 5, relance inutile = 1) : 42,6 % des clients relancés,
     73,3 % des défauts attrapés

3. Limites
   - un seul établissement, une seule période, pas de date par client : pas de test hors temps ;
   - coûts des erreurs supposés, à valider avec le métier ;
   - importance et valeurs de SHAP décrivent le modèle, pas des causes ;
   - indicateurs d'équité calculés pour le sexe et l'âge : à discuter, pas à conclure.
```

> ✅ **À retenir.** Un projet d'apprentissage automatique solide, c'est : **cadrer** la décision et les coûts, **auditer** les données, fixer des **références**, séparer correctement et **ne toucher au test qu'une fois**, **comparer avec leur incertitude**, **choisir le seuil** en fonction des coûts, **vérifier la calibration**, **expliquer** et **vérifier l'équité**, puis **rapporter** les limites. Le modèle lui-même n'est qu'une des onze étapes.

### P.13 Les limites de l'étude

- **Pas de séparation temporelle.** Le jeu n'a pas de date par client : on ne peut pas vérifier que le modèle tient dans le temps (dérive des données, changement de politique de crédit). En production, cette vérification est indispensable.
- **Un seul établissement et une seule période.** Les performances ne se transportent pas automatiquement à un autre pays ou à une autre année.
- **Les coûts sont une hypothèse.** Le seuil optimal dépend entièrement du rapport 5:1 posé au cadrage ; une analyse de **sensibilité** à ce rapport serait la suite naturelle.
- **Prédire n'est pas expliquer, ni décider.** Un modèle de risque ne dit pas **quelle action** réduirait le défaut ; pour cela, il faut des expériences (volume II, chapitre 7 et chapitre 8).
- **Les décisions affectent des personnes.** Relancer, réduire une limite ou refuser un crédit a des conséquences : documentation, contestation, surveillance de l'équité et supervision humaine font partie du projet.

## Auto-évaluation

**Mode d'emploi.** Répondez à voix haute ou par écrit **avant** de lire le corrigé, en une ou deux phrases. Les sections à relire sont indiquées dans le corrigé. Trente-cinq bonnes réponses sur les quarante signalent un volume bien assimilé ; les questions 33 à 40 portent sur les chapitres facultatifs (6 à 9) et ne comptent que si vous les avez lus.

### La démarche (chapitre 1)

1. Pourquoi l'erreur mesurée sur les données d'entraînement est-elle un mauvais indicateur de la performance future ?
2. Qu'appelle-t-on « fuite d'information » ? Donnez deux formes typiques.
3. Avec une validation croisée à 5 plis sur 1 000 observations, combien d'observations servent à l'entraînement et à l'évaluation à chaque pli, et combien de modèles ajuste-t-on ?
4. Pourquoi l'écart-type des scores des plis n'est-il pas une barre d'erreur valable pour la performance du modèle ?
5. Comment se décompose l'erreur quadratique attendue d'un modèle ? Que se passe-t-il quand on augmente la complexité ?
6. Un modèle obtient une AUC de 0,99 à l'entraînement et de 0,80 en validation. Que diagnostiquez-vous, et que tentez-vous ?
7. Pourquoi se compare-t-on toujours à une référence simple, et pourquoi n'ouvre-t-on le jeu de test qu'une fois ?

### Les modèles supervisés (chapitre 2)

8. Pourquoi minimise-t-on une perte « logistique » plutôt que le taux d'erreur de classification ?
9. Quelle est l'impureté de Gini d'un nœud contenant 30 clients qui ont résilié et 70 qui n'ont pas résilié ?
10. Quelle est la variance de la moyenne de $B=100$ prédicteurs de variance $\sigma^2=1$ et de corrélation $\rho=0{,}3$ ? Que montre ce résultat sur les forêts aléatoires ?
11. Que « apprend » chaque nouvel arbre dans un gradient boosting ?
12. Pourquoi l'importance « par impureté » d'une forêt est-elle trompeuse ? Que lui préfère-t-on ?
13. Quel est le rôle du pas d'apprentissage dans un boosting, et à quoi sert l'arrêt précoce ?
14. Quels modèles exigent des variables à la même échelle, et lesquels s'en passent ?

### Le non supervisé (chapitre 3)

15. Comment valider un regroupement quand on n'a aucune étiquette ?
16. Pour un point, la distance moyenne aux autres points de son groupe est 2 et la distance moyenne au groupe voisin le plus proche est 5. Quelle est sa silhouette ?
17. Pourquoi standardise-t-on les variables avant les k-means ?
18. L'ACP garde 70 % de la variance avec ses trois premières composantes. Quelle est l'erreur de reconstruction relative ?
19. Que ne faut-il surtout pas lire sur une carte t-SNE ou UMAP ?

### Les variables et le déséquilibre (chapitre 4)

20. Pourquoi un encodage « par la cible » calculé naïvement est-il trompeur, et comment le corriger ?
21. Les arbres ont-ils besoin de mise à l'échelle ? Et la régression logistique pénalisée ?
22. Qu'est-ce qu'une valeur manquante « MNAR » ? Que faire ?
23. Une relance inutile coûte 1 € et un défaut manqué 5 €. À partir de quelle probabilité de défaut relance-t-on ?
24. Quel effet ont les poids de classes et le rééchantillonnage sur les probabilités prédites et sur le classement des clients ?
25. Pourquoi ne doit-on jamais appliquer SMOTE avant la validation croisée ?

### Évaluation, calibration, interprétabilité (chapitre 5)

26. Une matrice de confusion donne TP = 40, FP = 60, FN = 10, TN = 890. Calculez exactitude, précision, rappel et $F_1$.
27. Quelle est l'interprétation probabiliste de l'AUC ?
28. Pourquoi la précision moyenne est-elle plus informative que l'AUC quand la classe positive est rare ?
29. Qu'est-ce qu'un modèle calibré ? Comment le vérifie-t-on et comment le répare-t-on ?
30. Calculez le score de Brier des prédictions 0,9 ; 0,2 ; 0,7 pour les étiquettes 1 ; 0 ; 0.
31. Que garantit la propriété d'efficacité des valeurs de Shapley ? SHAP établit-il des causes ?
32. Citez trois critères d'équité. Peut-on tous les satisfaire ?

### Les chapitres facultatifs (6 à 9)

33. Un détecteur de fraude affiche 99,19 % d'exactitude sur des données où 0,81 % des commandes sont frauduleuses. Que valent ces 99,19 % ?
34. Dans une forêt d'isolement, que vaut le score d'anomalie quand la longueur de chemin moyenne d'un point est égale à $c(n)$ ?
35. Trois clients achètent le produit A, quatre le produit B, et deux clients achètent les deux. Quelle est leur similarité cosinus ?
36. Un classement place des produits de pertinences (1, 0, 1). Calculez son NDCG@3.
37. Pourquoi la popularité est-elle si difficile à battre en recommandation ?
38. Quand l'apprentissage semi-supervisé peut-il nuire ?
39. Quel piège guette un jeu étiqueté constitué par apprentissage actif ?
40. Un agent met à jour $Q(s,a)=2$ avec $\alpha=0{,}5$, une récompense de 1, $\gamma=0{,}9$ et $\max_{a'}Q(s',a')=4$. Quelle est la nouvelle valeur ? Pourquoi un bandit n'est-il pas un test A/B ?

## Corrigés des questions

Pour les questions numériques, **calculons** plutôt que de nous fier à la mémoire.

```python
import numpy as np

print("Q3  plis de 1000/5 :", 1000 * 4 // 5, "pour l'entraînement,", 1000 // 5, "pour l'évaluation, 5 modèles")
print("Q9  Gini =", round(1 - (0.3**2 + 0.7**2), 3))
rho, sigma2, B = 0.3, 1.0, 100
print("Q10 variance de la moyenne =", round(rho * sigma2 + (1 - rho) * sigma2 / B, 4))
print("Q16 silhouette =", round((5 - 2) / max(2, 5), 3))
print("Q18 erreur de reconstruction relative =", round(1 - 0.70, 2))
print("Q23 seuil = 1 / (1 + 5) =", round(1 / 6, 4))
TP, FP, FN, TN = 40, 60, 10, 890
prec, rap = TP / (TP + FP), TP / (TP + FN)
print("Q26 exactitude", (TP + TN) / (TP + FP + FN + TN), "| précision", prec, "| rappel", rap, "| F1", round(2 * prec * rap / (prec + rap), 4))
print("Q30 Brier =", round(np.mean((np.array([0.9, 0.2, 0.7]) - np.array([1, 0, 0])) ** 2), 4))
print("Q34 score = 2^(-1) =", 2 ** -1)
print("Q35 cosinus =", round(2 / np.sqrt(3 * 4), 4))
dcg = lambda rel: sum(r / np.log2(i + 2) for i, r in enumerate(rel))
print("Q36 NDCG@3 =", round(dcg([1, 0, 1]) / dcg([1, 1, 0]), 4))
print("Q40 nouvelle valeur de Q =", 2 + 0.5 * (1 + 0.9 * 4 - 2))
```
<!--sortie-->
```text
Q3  plis de 1000/5 : 800 pour l'entraînement, 200 pour l'évaluation, 5 modèles
Q9  Gini = 0.42
Q10 variance de la moyenne = 0.307
Q16 silhouette = 0.6
Q18 erreur de reconstruction relative = 0.3
Q23 seuil = 1 / (1 + 5) = 0.1667
Q26 exactitude 0.93 | précision 0.4 | rappel 0.8 | F1 0.5333
Q30 Brier = 0.18
Q34 score = 2^(-1) = 0.5
Q35 cosinus = 0.5774
Q36 NDCG@3 = 0.9197
Q40 nouvelle valeur de Q = 3.3
```

**1.** Le modèle a été ajusté pour bien expliquer **ces** données : il en épouse aussi le bruit. L'erreur d'entraînement est donc en moyenne **trop optimiste** ; il faut mesurer sur des données que l'ajustement n'a pas vues. (1.1)

**2.** Une information qui **ne serait pas disponible au moment de la prédiction** se glisse dans l'apprentissage. Formes typiques : une variable calculée **après** la date de prédiction (par exemple les commandes des trois mois suivants pour prédire la résiliation) ; un prétraitement (imputation, mise à l'échelle, sélection de variables, encodage par la cible) **ajusté sur toutes les données avant** le découpage. Le résultat est un score flatteur qui s'effondre en production. (1.1, 1.2)

**3.** 800 observations pour l'entraînement, 200 pour l'évaluation à chaque pli, et **5 modèles** ajustés (code ci-dessus). (1.2.2)

**4.** Les jeux d'entraînement de deux plis **se recouvrent largement** : les scores sont corrélés, et l'écart-type entre plis **sous-estime** l'incertitude réelle sur la performance. Pour comparer deux modèles, on utilise des différences appariées avec une correction (test $t$ corrigé), ou un bootstrap. (1.2.4, 1.4.2)

**5.** $E[(y-\hat f)^2]=\text{bruit}+\text{biais}^2+\text{variance}$. Quand la complexité augmente, le biais diminue et la variance augmente : l'erreur de validation décrit une courbe en U, dont le minimum est le bon compromis. (1.3)

**6.** Un grand écart entre entraînement et validation est le signe d'un **surapprentissage** (variance trop élevée). Remèdes : simplifier le modèle (profondeur, régularisation), **plus de données**, moins de variables, arrêt précoce, moyenne de modèles (forêts). On le confirme par une courbe d'apprentissage. (1.3)

**7.** La référence (prédire la classe majoritaire, une règle métier, un modèle simple) donne **le score à battre** : un modèle sophistiqué qui ne la dépasse pas ne sert à rien. Le test ne sert qu'**une fois**, à la fin, parce que chaque consultation qui influence une décision en fait un jeu de validation, et son score devient optimiste. (1.4.1, 1.4.4)

**8.** Le taux d'erreur est **non convexe et non différentiable** : on ne sait pas l'optimiser efficacement. La perte logistique est un **substitut convexe** et dérivable, qui majore l'erreur et fournit des **probabilités**. (2.1)

**9.** $1-(0{,}3^2+0{,}7^2)=0{,}42$ (code ci-dessus). Un nœud pur vaut 0 ; le maximum pour deux classes est 0,5. (2.2.2)

**10.** $\rho\sigma^2+\frac{1-\rho}{B}\sigma^2=0{,}3+0{,}007=0{,}307$. Moyenner beaucoup d'arbres supprime presque toute la variance « individuelle », mais **pas** la part commune $\rho\sigma^2$ : d'où l'idée de **décorréler** les arbres (sous-ensemble aléatoire de variables à chaque coupure). (2.3.2, 2.3.3)

**11.** Il ajuste le **pseudo-résidu**, c'est-à-dire l'opposé du gradient de la perte par rapport aux prédictions actuelles : pour la perte quadratique, ce sont les résidus ordinaires. Le boosting est une descente de gradient **dans l'espace des fonctions**. (2.4)

**12.** L'importance par impureté **favorise les variables continues ou à nombreuses modalités** (elles offrent plus de découpages possibles) et se calcule sur les données d'entraînement. On préfère l'importance par **permutation** sur des données non vues, ou SHAP. (2.3.6, 5.3.2)

**13.** Un petit pas rend chaque arbre moins influent : le modèle apprend plus **lentement** mais généralise mieux, au prix de plus d'arbres. L'**arrêt précoce** interrompt l'ajout d'arbres quand l'erreur de validation cesse de s'améliorer, ce qui règle le nombre d'arbres automatiquement. (2.4)

**14.** Exigent la mise à l'échelle : les modèles à **distances** (k-NN, SVM, k-means), les modèles à **pénalité** (Ridge, Lasso) et la descente de gradient. Les **arbres** et leurs ensembles s'en passent, car ils ne comparent que l'ordre des valeurs. (2.1, 4.1)

**15.** Par **plusieurs épreuves qui se rejoignent** : critères internes (silhouette, Calinski–Harabasz, Davies–Bouldin), comparaison à une **référence sans structure**, **stabilité** par sous-échantillonnage, et, si l'on dispose d'une vérité, des indices externes (indice de Rand ajusté, information mutuelle normalisée). Jamais par un seul chiffre. (3.1)

**16.** $s=\frac{b-a}{\max(a,b)}=\frac{5-2}{5}=0{,}6$ : le point est bien rangé dans son groupe. Une silhouette proche de 0 signale un point à la frontière, une valeur négative un point probablement mal classé. (3.1.2)

**17.** Les k-means utilisent des **distances** : une variable en euros écrase une variable comprise entre 0 et 1. Dans notre étude, l'indice de Rand ajusté passe de 0,49 avec les variables standardisées à 0,08 sans standardisation. (3.1.6)

**18.** $1-0{,}70=0{,}30$ : l'erreur de reconstruction relative est la variance **non** conservée (théorème d'Eckart–Young). (3.2)

**19.** Les **distances entre groupes**, la **taille** des groupes et leurs formes fines. Ces projections préservent le voisinage local, pas la géométrie globale. (3.4)

**20.** Remplacer une modalité par la moyenne de la cible calculée **sur ses propres lignes** laisse fuiter la cible : sur un code qui n'est que du bruit, on obtient une AUC de 0,678 à l'entraînement et 0,510 au test. Remède : calculer l'encodage **hors pli** (out-of-fold) avec un lissage, à l'intérieur du pipeline. (4.1)

**21.** Les arbres, **non**. La régression logistique pénalisée, **oui** : la pénalité dépend de l'échelle des coefficients, donc de celle des variables. (4.1, 2.1)

**22.** Une valeur est manquante **de façon non aléatoire** : la probabilité de l'absence dépend de la valeur elle-même (par exemple, les clients mécontents répondent moins à l'enquête de satisfaction). On ajoute un **indicateur d'absence**, on n'impute qu'à l'intérieur du pipeline, et on reconnaît que l'imputation ne récupère pas l'information perdue. (4.1)

**23.** $\frac{c_{FP}}{c_{FP}+c_{FN}}=\frac{1}{1+5}\approx0{,}167$ : on relance dès que la probabilité de défaut dépasse environ 17 %, loin du seuil de 0,5 pris par habitude. (4.3.5)

**24.** Ils **décalent les probabilités** (elles deviennent trop élevées pour la classe rare) et déplacent le bon seuil, mais **n'améliorent pas, en général, le classement** des clients. Si l'on a besoin de probabilités, on recalibre ; si l'on a besoin d'un classement, ils sont rarement utiles. (4.3.2, 5.2)

**25.** Les points synthétiques sont créés à partir de points qui se retrouveront **dans les plis d'évaluation** : on évalue sur des points qui ressemblent à des copies de l'entraînement, et le score devient absurde (jusqu'à 0,999 d'AUC). Le rééchantillonnage ne doit se faire que sur les plis d'entraînement, dans un pipeline. (4.5)

**26.** Exactitude $=\frac{40+890}{1000}=0{,}93$ ; précision $=\frac{40}{100}=0{,}4$ ; rappel $=\frac{40}{50}=0{,}8$ ; $F_1=\frac{2\times0{,}4\times0{,}8}{1{,}2}\approx0{,}533$ (code ci-dessus). Une exactitude de 93 % cache une précision de 40 % : 5 % de positifs seulement. (5.1.2)

**27.** L'AUC est la **probabilité qu'un client positif tiré au hasard reçoive un score plus élevé qu'un client négatif** tiré au hasard (0,5 : aucun pouvoir de classement). Elle est liée à la statistique de Mann–Whitney. (5.1.4)

**28.** L'AUC est insensible à la prévalence et peut rester élevée alors que presque toutes les alertes sont fausses ; la **précision moyenne** mesure ce qu'on obtient dans la région utile (les premiers rangs) et son niveau de référence est la prévalence. Sur nos données de crédit, un classement au hasard donne une précision moyenne de 0,22 (la prévalence), et notre modèle atteint 0,56. (5.1.5)

**29.** Un modèle est **calibré** quand, parmi les clients à qui il attribue 30 %, environ 30 % ont l'événement. On le vérifie par un **diagramme de fiabilité** (et l'erreur de calibration), on le répare par la méthode de **Platt** (logistique sur le score) ou la **régression isotonique**, sur un jeu séparé de celui de l'ajustement. (5.2)

**30.** $\frac{(0{,}9-1)^2+(0{,}2-0)^2+(0{,}7-0)^2}{3}=\frac{0{,}01+0{,}04+0{,}49}{3}=0{,}18$ (code ci-dessus). Plus il est bas, mieux c'est ; 0 serait parfait. (5.1.6)

**31.** L'**efficacité** : la somme des contributions des variables est **exactement** la différence entre la prédiction du client et la prédiction moyenne. Mais SHAP **décrit le modèle**, pas le monde : une contribution élevée ne dit pas qu'agir sur la variable changerait le résultat. (5.3.5, 5.3.7)

**32.** Par exemple la **parité démographique** (même taux de décisions positives dans chaque groupe), l'**égalité des chances** (même rappel), la **parité prédictive** (même précision) ou la **calibration par groupe**. Quand les taux de base diffèrent entre groupes, on **ne peut pas** tous les satisfaire en même temps (résultat d'impossibilité) : il faut choisir et justifier. (5.4)

**33.** Elles ne valent **rien** : un détecteur qui ne signale jamais rien obtient 99,19 %. On juge un détecteur par la **précision moyenne**, le **rappel à budget d'alertes fixé** ou la précision@k, jamais par l'exactitude. (6.1)

**34.** $s=2^{-E[h]/c(n)}=2^{-1}=0{,}5$ : un point moyennement isolable, ni franchement anormal (s proche de 1) ni franchement normal (s inférieur à 0,5). (6.3.2)

**35.** $\cos=\frac{n_{AB}}{\sqrt{n_An_B}}=\frac{2}{\sqrt{3\times4}}\approx0{,}577$. (7.1)

**36.** $\text{DCG}=\frac1{\log_22}+0+\frac1{\log_24}=1{,}5$ ; le classement idéal (1, 1, 0) donne $1+\frac1{\log_23}\approx1{,}631$ ; NDCG@3 $\approx0{,}920$ (code ci-dessus). (7.4.1)

**37.** Dans un catalogue, quelques produits concentrent l'essentiel des achats : recommander **les plus achetés** contente déjà beaucoup de monde, et la personnalisation n'apporte que quelques points, mesurables seulement avec un protocole rigoureux. (7.1, 7.4)

**38.** Quand les **hypothèses** qui font de l'étiquette inconnue une information utile sont **violées** : classes qui se chevauchent, graphe où les voisins ne partagent pas la même étiquette (par exemple les clients de la boutique : 80,5 % de voisins de même étiquette contre 75,9 % au hasard), ou étiquettes peu représentatives. (8.1, 8.2)

**39.** Le jeu étiqueté n'est **pas représentatif** : on a étiqueté surtout des cas ambigus ou rares (38 % de résiliations contre 14 % réellement), et les probabilités du modèle sont **faussées** (0,078 prédit pour 0,14 réel). Il faut un jeu de test tiré au hasard et, au besoin, un recalibrage. (8.3)

**40.** $Q\leftarrow 2+0{,}5\,(1+0{,}9\times4-2)=3{,}3$ (code ci-dessus). Un **bandit** sert à **gagner en apprenant** : il alloue de plus en plus d'essais à ce qui marche (et paie un « regret »), alors qu'un test A/B sert à **conclure** avec une puissance connue et répartit les essais à égalité. (9.2, 9.3.3)

## Votre grille d'auto-évaluation

Pour chaque ligne : **je sais l'expliquer** / **je sais le faire** / **à revoir**.

| Compétence | Où la retravailler |
|---|---|
| Formuler un problème, séparer les données, éviter la fuite | 1.1 |
| Valider par validation croisée et en estimer l'incertitude | 1.2 |
| Diagnostiquer biais, variance, surapprentissage | 1.3 |
| Se comparer à une référence, comparer deux modèles | 1.4 |
| Régler des hyperparamètres sans se tromper | 1.5 |
| Calculer un arbre, expliquer forêts et boosting | 2.2, 2.3, 2.4 |
| Valider un regroupement sans étiquettes | 3.1 |
| Choisir une réduction de dimension | 3.2 |
| Encoder, mettre à l'échelle, traiter les manquants | 4.1 |
| Créer et sélectionner des variables | 4.2 |
| Traiter des classes déséquilibrées, choisir un seuil par les coûts | 4.3 |
| Choisir et lire des métriques | 5.1 |
| Vérifier et réparer la calibration | 5.2 |
| Expliquer un modèle (permutation, PDP, LIME, SHAP) | 5.3 |
| Auditer l'équité, quantifier l'incertitude | 5.4, 5.5 |
| Détecter des anomalies, recommander, apprendre avec peu d'étiquettes, décider en séquence | 6, 7, 8, 9 |
| Mener un projet d'apprentissage automatique de bout en bout | Projet du volume |
