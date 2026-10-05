# Chapitre 2 : Apprentissage supervisé — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 2 du livre. Les **applications** reprennent, pas à pas et avec du code, les calculs que le livre n'a fait que résumer (descente de gradient, arbre, bagging et boosting écrits à la main, comparaisons de modèles) ; les **exercices** sont corrigés à la fin. Il se lit **de haut en bas** : les objets créés dans la section « Préparation » servent partout, et quelques applications réutilisent les précédentes. Les données sont celles du chapitre : `clients_ml.csv`, des clients d'une boutique simulée, avec la résiliation à 90 jours `churn_90j` comme cible.

## Préparation

Une seule cellule charge les bibliothèques, les données et le découpage entraînement/test (identique à celui du livre). Les colonnes `depense_6m`, `segment_vrai` et `commandes_apres_cible` ne sont **jamais** des variables d'entrée (cette dernière contient l'avenir : c'est une fuite d'information).

```python
import warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import log_loss, roc_auc_score
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

warnings.filterwarnings("ignore")
clients = pd.read_csv("donnees/clients_ml.csv")
y = clients["churn_90j"]
X = clients.drop(columns=["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"])
cat = ["ville", "canal_acquisition", "appareil", "categorie_preferee"]
num = [c for c in X.columns if c not in cat]
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.25, random_state=0, stratify=y)
Xtr_o = pd.get_dummies(Xtr, columns=cat, dtype=float)                                   # catégories en indicatrices (arbres, forêts)
Xte_o = pd.get_dummies(Xte, columns=cat, dtype=float).reindex(columns=Xtr_o.columns, fill_value=0.0)
Xtr_c, Xte_c = Xtr.copy(), Xte.copy()                                                    # catégories pandas (boosting)
for c in cat:
    Xtr_c[c] = pd.Categorical(Xtr[c], categories=sorted(Xtr[c].dropna().unique()))
    Xte_c[c] = pd.Categorical(Xte[c], categories=Xtr_c[c].cat.categories)
pre_lin = ColumnTransformer([("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), num),
                             ("cat", OneHotEncoder(handle_unknown="ignore"), cat)])
cv5 = StratifiedKFold(5, shuffle=True, random_state=0)
print(len(Xtr), "clients d'entraînement,", len(Xte), "de test ; taux de départ :", round(y.mean(), 3))
```
<!--sortie-->
```text
9000 clients d'entraînement, 3000 de test ; taux de départ : 0.14
```


## Applications

### Application 2.1 — La descente de gradient écrite à la main

*Sections du livre : 2.1.2 à 2.1.4.* **Objectif** : programmer la régression logistique « de zéro », vérifier qu'on retrouve `scikit-learn`, et voir l'effet du pas et de la mise à l'échelle.

**Étape 1 — un pas sur les quatre clients du livre.** On reprend $x=(-2,-1,1,3)$, $y=(0,0,1,1)$, $w=b=0$ et un pas de 0,5. Le gradient est $\frac1n\sum(p_i-y_i)x_i$.

```python
x4 = np.array([-2.0, -1.0, 1.0, 3.0]); y4 = np.array([0, 0, 1, 1])
w, b, pas = 0.0, 0.0, 0.5
p = 1 / (1 + np.exp(-(w * x4 + b)))
grad_w, grad_b = np.mean((p - y4) * x4), np.mean(p - y4)
print("gradient :", grad_w, grad_b, "-> nouveau w :", w - pas * grad_w)
```
<!--sortie-->
```text
gradient : -0.875 0.0 -> nouveau w : 0.4375
```

On retrouve $-0{,}875$ et $w=0{,}4375$ : le calcul à la main du livre.

**Étape 2 — la descente complète sur trois variables.** On standardise la récence, le nombre de commandes et la satisfaction (valeurs manquantes remplacées par la médiane) et l'on itère 500 fois.

```python
cols = ["recence_jours", "nb_commandes_12m", "satisfaction_moy"]
A = Xtr[cols].fillna(Xtr[cols].median()); mu, sd = A.mean(), A.std()
Z = ((A - mu) / sd).to_numpy(); Z1 = np.column_stack([np.ones(len(Z)), Z]); yy = ytr.to_numpy(float)

def descente(pas, n_iter=500, taille_lot=None, graine=0):
    rng = np.random.default_rng(graine); th = np.zeros(Z1.shape[1]); hist = []
    for _ in range(n_iter):
        idx = np.arange(len(Z1)) if taille_lot is None else rng.choice(len(Z1), taille_lot, replace=False)
        p = 1 / (1 + np.exp(-Z1[idx] @ th))
        th = th - pas * Z1[idx].T @ (p - yy[idx]) / len(idx)
        pc = 1 / (1 + np.exp(-Z1 @ th)); hist.append(-np.mean(yy * np.log(pc + 1e-12) + (1 - yy) * np.log(1 - pc + 1e-12)))
    return th, np.array(hist)

th, hist = descente(0.5)
sk = LogisticRegression(C=1e6, max_iter=5000).fit(Z, yy)
print("à la main  :", th.round(3))
print("scikit-learn:", np.r_[sk.intercept_, sk.coef_[0]].round(3))
```
<!--sortie-->
```text
à la main  : [-2.343  0.554 -0.711 -0.538]
scikit-learn: [-2.342  0.553 -0.713 -0.537]
```


Les deux jeux de coefficients coïncident à 0,002 près : la régression logistique de `scikit-learn` n'est pas autre chose qu'une descente de gradient (plus sophistiquée) sur cette perte. La perte atteinte est 0,328.

**Étape 3 — le pas d'apprentissage.** Comparons trois pas, puis la descente **stochastique** (mini-lots de 64 clients). (Avec des variables standardisées, la courbure de la perte est modérée : un pas de 0,5 est confortable, un pas de 60 est bien trop grand.)

```python
res = {}
for nom, kw in {"pas 0,02": dict(pas=0.02), "pas 0,5": dict(pas=0.5), "pas 60 (trop grand)": dict(pas=60.0), "SGD, lots de 64, pas 0,2": dict(pas=0.2, taille_lot=64)}.items():
    res[nom] = descente(**kw)[1]
print(pd.DataFrame({"perte à 50 itérations": {k: v[49] for k, v in res.items()}, "perte à 500": {k: v[-1] for k, v in res.items()}}).round(4))
```
<!--sortie-->
```text
                          perte à 50 itérations  perte à 500
pas 0,02                                 0.5711       0.3544
pas 0,5                                  0.3321       0.3285
pas 60 (trop grand)                      3.4504       2.1627
SGD, lots de 64, pas 0,2                 0.3536       0.3285
```


Un pas trop petit (0,02) n'a pas fini d'avancer après 500 itérations ; un pas bien choisi (0,5) atteint le minimum en quelques dizaines ; un pas **trop grand** (60) fait osciller la descente, qui ne converge pas (perte à 500 itérations : 2,16). La SGD, bruitée, arrive près du minimum en ne regardant que 64 clients par itération.

> **Pour aller plus loin.** Refaites l'étape 2 **sans standardiser** (utilisez `A.to_numpy()` à la place de `Z`) avec le plus grand pas qui ne diverge pas : mesurez la perte après 500 itérations.

### Application 2.2 — Chemins de régularisation

*Sections du livre : 2.1.5.* **Objectif** : voir comment la pénalité $\ell_1$ sélectionne des variables, et si cette sélection est **stable**.

**Étape 1 — le chemin.** Pour une grille de valeurs de `C` (petit = pénalité forte), on compte les coefficients non nuls et l'on mesure l'AUC en validation croisée.

```python
grille = np.logspace(-2.5, 0.5, 7)
lignes = []
for C in grille:
    mod = make_pipeline(pre_lin, LogisticRegression(C=C, penalty="l1", solver="liblinear", max_iter=2000, random_state=0))
    auc = cross_val_score(mod, Xtr, ytr, cv=cv5, scoring="roc_auc").mean()
    lignes.append({"C": round(C, 4), "coefficients non nuls": int((mod.fit(Xtr, ytr)[-1].coef_ != 0).sum()), "AUC CV": round(auc, 4)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
     C  coefficients non nuls  AUC CV
0.0032                      5  0.8244
0.0100                      9  0.8487
0.0316                     12  0.8561
0.1000                     25  0.8587
0.3162                     40  0.8604
1.0000                     42  0.8604
3.1623                     43  0.8602
```

**Étape 2 — la stabilité.** On refait la sélection sur 12 échantillons bootstrap avec `C=0.05` et l'on compte, pour chaque variable, la fréquence où elle est retenue.

```python
rng = np.random.default_rng(1)
noms = pre_lin.fit(Xtr, ytr).get_feature_names_out()
freq = np.zeros(len(noms))
for b in range(12):
    idx = rng.integers(0, len(Xtr), len(Xtr))
    m = make_pipeline(pre_lin, LogisticRegression(C=0.05, penalty="l1", solver="liblinear", max_iter=2000, random_state=0)).fit(Xtr.iloc[idx], ytr.iloc[idx])
    freq += (m[-1].coef_[0] != 0)
st = pd.Series(freq / 12, index=noms).sort_values(ascending=False)
print(st.head(8).round(2).to_string()); print("...\nvariables retenues à chaque fois :", int((st == 1).sum()), "; retenues parfois :", int(((st > 0) & (st < 1)).sum()))
```
<!--sortie-->
```text
num__age                                  1.0
num__anciennete_mois                      1.0
num__nb_commandes_12m                     1.0
num__panier_moyen                         1.0
num__recence_jours                        1.0
num__satisfaction_moy                     1.0
num__missingindicator_satisfaction_moy    1.0
num__part_achats_promo                    1.0
...
variables retenues à chaque fois : 10 ; retenues parfois : 24
```


Sur les 12 tirages, 10 variables sont retenues **à chaque fois** et 24 seulement **parfois** : le Lasso est fiable pour les signaux **forts** et **hésitant** pour les variables corrélées entre elles (laquelle choisir ?). Ne présentez jamais « les variables sélectionnées par le Lasso » comme *les* variables importantes sans cette vérification.

### Application 2.3 — Construire un arbre à la main, puis avec `scikit-learn`

*Sections du livre : 2.2.1 à 2.2.5.* **Objectif** : écrire la recherche de la meilleure coupe, puis la récursion.

**Étape 1 — le meilleur seuil d'une variable.**

```python
ex = pd.DataFrame({"recence": [15, 30, 45, 70, 95, 120, 160, 200, 260, 320], "satisfaction": [4.5, 3.0, 4.0, 4.1, 3.1, 4.4, 3.0, 4.3, 2.9, 3.8],
                   "parti": [0, 0, 0, 0, 0, 0, 1, 0, 1, 1]})
gini = lambda v: 1 - np.mean(v) ** 2 - (1 - np.mean(v)) ** 2 if len(v) else 0.0

def meilleure_coupe(df, variables, cible="parti"):
    meilleur = (0.0, None, None); g0 = gini(df[cible])
    for var in variables:
        v = np.sort(df[var].unique())
        for s in (v[:-1] + v[1:]) / 2:
            gche, drt = df[df[var] <= s], df[df[var] > s]
            gain = g0 - (len(gche) * gini(gche[cible]) + len(drt) * gini(drt[cible])) / len(df)
            if gain > meilleur[0] + 1e-12: meilleur = (gain, var, s)
    return meilleur
print(meilleure_coupe(ex, ["recence", "satisfaction"]))
```
<!--sortie-->
```text
(np.float64(0.27000000000000013), 'recence', np.float64(140.0))
```

**Étape 2 — la récursion.** On construit l'arbre jusqu'à des groupes purs ou une profondeur maximale.

```python
def construire(df, variables, prof=0, prof_max=3):
    if df["parti"].nunique() == 1 or prof == prof_max: return {"classe": round(df["parti"].mean(), 2), "n": len(df)}
    gain, var, s = meilleure_coupe(df, variables)
    if var is None: return {"classe": round(df["parti"].mean(), 2), "n": len(df)}
    return {"si": f"{var} <= {s:g}", "oui": construire(df[df[var] <= s], variables, prof + 1, prof_max), "non": construire(df[df[var] > s], variables, prof + 1, prof_max)}

def afficher(arbre, retrait=0):
    pad = "   " * retrait
    if "classe" in arbre: print(f"{pad}-> probabilité de départ {arbre['classe']} ({arbre['n']} clients)")
    else:
        print(f"{pad}si {arbre['si']} :"); afficher(arbre["oui"], retrait + 1); print(f"{pad}sinon :"); afficher(arbre["non"], retrait + 1)
afficher(construire(ex, ["recence", "satisfaction"]))
```
<!--sortie-->
```text
si recence <= 140 :
   -> probabilité de départ 0.0 (6 clients)
sinon :
   si satisfaction <= 4.05 :
      -> probabilité de départ 1.0 (3 clients)
   sinon :
      -> probabilité de départ 0.0 (1 clients)
```

On retrouve les deux questions du livre (récence ≤ 140, puis satisfaction ≤ 4,05).

**Étape 3 — sur les vraies données : profondeur et élagage.**

```python
from sklearn.tree import DecisionTreeClassifier
profs = [2, 3, 4, 5, 6, 8, 12]
for d in profs:
    m = DecisionTreeClassifier(max_depth=d, min_samples_leaf=5, random_state=0)
    print(d, round(cross_val_score(m, Xtr_o, ytr, cv=cv5, scoring="roc_auc").mean(), 4))
chemin = DecisionTreeClassifier(min_samples_leaf=5, random_state=0).cost_complexity_pruning_path(Xtr_o, ytr)
print("nombre de valeurs de alpha possibles :", len(chemin.ccp_alphas))
```
<!--sortie-->
```text
2 0.7926
3 0.8385
4 0.8613
5 0.863
6 0.8579
8 0.813
12 0.7631
nombre de valeurs de alpha possibles : 273
```


La validation croisée retient la profondeur 5 (AUC 0,863) : au-delà, l'arbre mémorise.

### Application 2.4 — Le bagging écrit à la main

*Sections du livre : 2.3.1 à 2.3.4.* **Objectif** : construire une forêt de bagging avec une boucle, calculer soi-même l'erreur hors sac, et vérifier la baisse de variance.

```python
rng = np.random.default_rng(0)
B, n = 60, len(Xtr_o)
Xn, yn = Xtr_o.to_numpy(), ytr.to_numpy()
arbres, masque_in = [], np.zeros((B, n), dtype=bool)
for b in range(B):
    idx = rng.integers(0, n, n); masque_in[b, np.unique(idx)] = True
    arbres.append(DecisionTreeClassifier(max_depth=8, min_samples_leaf=5, random_state=b).fit(Xn[idx], yn[idx]))
P_train = np.array([t.predict_proba(Xn)[:, 1] for t in arbres])                 # B x n
oob = np.where(~masque_in, P_train, np.nan); p_oob = np.nanmean(oob, axis=0)
print("part de clients hors sac par arbre :", round(float((~masque_in).mean()), 3))
print("AUC hors sac (fait main) :", round(roc_auc_score(yn[~np.isnan(p_oob)], p_oob[~np.isnan(p_oob)]), 4))
P_test = np.array([t.predict_proba(Xte_o.to_numpy())[:, 1] for t in arbres])
print("AUC test, 1 arbre :", round(roc_auc_score(yte, P_test[0]), 4), "; 60 arbres :", round(roc_auc_score(yte, P_test.mean(0)), 4))
```
<!--sortie-->
```text
part de clients hors sac par arbre : 0.369
AUC hors sac (fait main) : 0.8853
AUC test, 1 arbre : 0.8174 ; 60 arbres : 0.8962
```


Chaque arbre laisse de côté 37 % des clients (théorie : 36,8 %). L'AUC hors sac calculée à la main (0,885) estime la performance sans toucher au jeu de test, et la moyenne de 60 arbres (0,896) bat nettement un arbre isolé (0,817).

> **Pour aller plus loin.** Remplacez `DecisionTreeClassifier(...)` par `DecisionTreeClassifier(..., max_features="sqrt")` : vous obtenez une vraie forêt aléatoire. Comparez l'AUC de test de 60 arbres.

### Application 2.5 — Importances et variables de bruit

*Sections du livre : 2.3.6.* **Objectif** : constater les biais de l'importance par impureté et la dilution entre variables corrélées.

```python
from sklearn.ensemble import RandomForestClassifier
from sklearn.inspection import permutation_importance
rb = np.random.default_rng(5)
Xb, Xbt = Xtr_o.copy(), Xte_o.copy()
Xb["bruit_continu"], Xbt["bruit_continu"] = rb.normal(size=len(Xb)), rb.normal(size=len(Xbt))
Xb["bruit_id"], Xbt["bruit_id"] = rb.integers(0, 2000, len(Xb)).astype(float), rb.integers(0, 2000, len(Xbt)).astype(float)
Xb["recence_bis"], Xbt["recence_bis"] = Xb["recence_jours"] + rb.normal(0, 3, len(Xb)), Xbt["recence_jours"] + rb.normal(0, 3, len(Xbt))   # quasi-doublon
f = RandomForestClassifier(150, min_samples_leaf=5, max_features="sqrt", n_jobs=1, random_state=0).fit(Xb, ytr)
mdi = pd.Series(f.feature_importances_, index=Xb.columns)
perm = pd.Series(permutation_importance(f, Xbt, yte, scoring="roc_auc", n_repeats=3, random_state=0, n_jobs=1).importances_mean, index=Xb.columns)
cible = ["recence_jours", "recence_bis", "bruit_continu", "bruit_id", "satisfaction_moy"]
print(pd.DataFrame({"impureté": mdi[cible], "permutation": perm[cible]}).round(4))
```
<!--sortie-->
```text
                  impureté  permutation
recence_jours       0.0946       0.0118
recence_bis         0.0975       0.0073
bruit_continu       0.0366      -0.0005
bruit_id            0.0323      -0.0004
satisfaction_moy    0.1221       0.0276
```

Lisez le tableau : (1) les deux variables de **bruit** reçoivent une importance par impureté non négligeable et une importance par permutation proche de zéro ; (2) `recence_jours` et son quasi-doublon `recence_bis` **se partagent** l'importance : chacune paraît moins utile qu'elle ne l'est. Pour mesurer l'importance *d'un groupe* de variables corrélées, on permute le groupe entier, ou l'on retire le groupe et l'on remesure la performance (importance par suppression).

### Application 2.6 — Le gradient boosting écrit à la main

*Sections du livre : 2.4.1 et 2.4.2.* **Objectif** : programmer le boosting pour la perte quadratique (prédire la dépense `depense_6m`), puis pour la perte logistique (la résiliation), et le comparer à `scikit-learn`.

**Étape 1 — perte quadratique : les résidus.**

```python
from sklearn.tree import DecisionTreeRegressor
dep = clients.loc[Xtr.index, "depense_6m"].to_numpy(); dep_te = clients.loc[Xte.index, "depense_6m"].to_numpy()
Xn_te = Xte_o.to_numpy()
F, F_te, nu, hist = np.full(len(Xn), dep.mean()), np.full(len(Xn_te), dep.mean()), 0.1, []
for m in range(150):
    t = DecisionTreeRegressor(max_depth=3, min_samples_leaf=20, random_state=m).fit(Xn, dep - F)       # on ajuste les RÉSIDUS
    F += nu * t.predict(Xn); F_te += nu * t.predict(Xn_te)
    hist.append((m + 1, np.sqrt(np.mean((dep - F) ** 2)), np.sqrt(np.mean((dep_te - F_te) ** 2))))
h = pd.DataFrame(hist, columns=["arbres", "RMSE entraînement", "RMSE test"]).set_index("arbres")
print(h.loc[[1, 10, 50, 100, 150]].round(2)); print("RMSE de la prédiction constante :", round(float(np.sqrt(np.mean((dep_te - dep.mean()) ** 2))), 2))
```
<!--sortie-->
```text
        RMSE entraînement  RMSE test
arbres                              
1                  118.41     120.71
10                  97.83     100.45
50                  88.40      94.09
100                 85.26      94.00
150                 82.51      94.25
RMSE de la prédiction constante : 125.62
```

Le RMSE de test passe de 125,6 (prédiction constante) à 94,0 après 100 arbres ; ensuite il ne s'améliore plus et remonte légèrement (94,25 à 150 arbres) alors que celui de l'entraînement continue de baisser (82,5) : le modèle commence à s'ajuster au bruit, d'où l'intérêt de l'arrêt précoce.

**Étape 2 — perte logistique : $y-p$.** On travaille sur la log-cote $F$, avec des arbres de profondeur 3.

```python
F, F_te, hist = np.full(len(Xn), np.log(yn.mean() / (1 - yn.mean()))), np.full(len(Xn_te), np.log(yn.mean() / (1 - yn.mean()))), []
for m in range(200):
    p = 1 / (1 + np.exp(-F))
    t = DecisionTreeRegressor(max_depth=3, min_samples_leaf=20, random_state=m).fit(Xn, yn - p)         # pseudo-résidu : y - p
    F += 0.1 * t.predict(Xn); F_te += 0.1 * t.predict(Xn_te)
    if (m + 1) in (1, 25, 50, 100, 200): hist.append((m + 1, roc_auc_score(yte, F_te), log_loss(yte, 1 / (1 + np.exp(-F_te)))))
print(pd.DataFrame(hist, columns=["arbres", "AUC test", "perte logistique test"]).round(4).to_string(index=False))
```
<!--sortie-->
```text
 arbres  AUC test  perte logistique test
      1    0.8412                 0.4018
     25    0.8779                 0.3374
     50    0.8821                 0.3072
    100    0.8912                 0.2830
    200    0.8969                 0.2650
```


Notre boosting artisanal atteint 0,897 après 200 arbres ; `HistGradientBoostingClassifier`, avec des réglages comparables, 0,901. Les deux ne diffèrent que par les détails (histogrammes, valeurs de feuilles de Newton, traitement des valeurs manquantes).

### Application 2.7 — XGBoost et LightGBM : réglages, valeurs manquantes, catégories

*Sections du livre : 2.4.3 à 2.4.6.* **Objectif** : explorer les hyperparamètres principaux et les traitements natifs.

```python
import lightgbm as lgb
Xa, Xv, ya, yv = train_test_split(Xtr_c, ytr, test_size=0.2, stratify=ytr, random_state=1)
lignes = []
for lr in (0.1, 0.03):
    for nl in (7, 15, 31):
        m = lgb.LGBMClassifier(n_estimators=800, learning_rate=lr, num_leaves=nl, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, n_jobs=1, random_state=0, verbose=-1)
        m.fit(Xa, ya, eval_set=[(Xv, yv)], callbacks=[lgb.early_stopping(30, verbose=False)])
        lignes.append({"pas": lr, "feuilles": nl, "arbres retenus": m.best_iteration_, "AUC test": round(roc_auc_score(yte, m.predict_proba(Xte_c)[:, 1]), 4)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 pas  feuilles  arbres retenus  AUC test
0.10         7             115    0.9013
0.10        15              57    0.9013
0.10        31              58    0.8991
0.03         7             305    0.9037
0.03        15             246    0.9019
0.03        31             229    0.8987
```


Les six réglages donnent des AUC de test entre 0,899 et 0,904 : le boosting est **peu sensible** aux réglages fins une fois l'arrêt précoce utilisé.

**Valeurs manquantes et catégories.** Comparons le traitement natif à une imputation par la médiane et à un encodage des villes en codes entiers arbitraires.

```python
def auc_lgb(A, B):
    m = lgb.LGBMClassifier(n_estimators=800, learning_rate=0.05, num_leaves=15, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, n_jobs=1, random_state=0, verbose=-1)
    Aa, Av, ya_, yv_ = train_test_split(A, ytr, test_size=0.2, stratify=ytr, random_state=1)
    m.fit(Aa, ya_, eval_set=[(Av, yv_)], callbacks=[lgb.early_stopping(30, verbose=False)])
    return round(roc_auc_score(yte, m.predict_proba(B)[:, 1]), 4)
Ai, Bi = Xtr_c.copy(), Xte_c.copy(); Ai[num] = Ai[num].fillna(Xtr[num].median()); Bi[num] = Bi[num].fillna(Xtr[num].median())
Ak, Bk = Xtr_c.copy(), Xte_c.copy()
for c in cat: Ak[c], Bk[c] = Xtr_c[c].cat.codes, Xte_c[c].cat.codes
print({"natif": auc_lgb(Xtr_c, Xte_c), "valeurs manquantes imputées": auc_lgb(Ai, Bi), "catégories en codes entiers": auc_lgb(Ak, Bk)})
```
<!--sortie-->
```text
{'natif': 0.9026, 'valeurs manquantes imputées': 0.9028, 'catégories en codes entiers': 0.9027}
```

Les écarts sont faibles sur ces données, mais le traitement natif ne coûte rien. Essayez de **supprimer volontairement** 40 % des valeurs de `recence_jours` au hasard puis au hasard **pour les clients partis seulement** (une absence informative) : l'imputation perd l'information « manquant », le traitement natif la garde.

### Application 2.8 — Le match des modèles, avec comparaison appariée

*Sections du livre : 2.4.7.* **Objectif** : comparer trois modèles proprement : validation croisée **répétée**, différences **appariées**, test corrigé et bootstrap.

**Étape 1 — validation croisée répétée à 5 plis × 3 répétitions** (les mêmes plis pour tous les modèles).

```python
from sklearn.model_selection import RepeatedStratifiedKFold
rcv = RepeatedStratifiedKFold(n_splits=5, n_repeats=3, random_state=0)
mods = {"logistique": (make_pipeline(pre_lin, LogisticRegression(C=0.3, max_iter=1000)), Xtr),
        "forêt": (RandomForestClassifier(100, min_samples_leaf=5, max_features="sqrt", n_jobs=1, random_state=0), Xtr_o),
        "boosting": (HistGradientBoostingClassifier(learning_rate=0.05, max_iter=200, early_stopping=False, categorical_features="from_dtype", random_state=0), Xtr_c)}
S = {k: cross_val_score(m, A, ytr, cv=rcv, scoring="roc_auc") for k, (m, A) in mods.items()}
print(pd.DataFrame({k: [v.mean(), v.std()] for k, v in S.items()}, index=["moyenne", "écart-type (15 plis)"]).round(4))
```
<!--sortie-->
```text
                      logistique   forêt  boosting
moyenne                   0.8603  0.8856    0.8898
écart-type (15 plis)      0.0117  0.0131    0.0096
```

**Étape 2 — les différences appariées.** Pour chaque pli, on calcule la différence d'AUC entre deux modèles ; un test de Student **corrigé** (Nadeau et Bengio) tient compte de ce que les plis se recouvrent : la variance de la moyenne des différences est multipliée par $\frac1k+\frac{n_{test}}{n_{train}}$ au lieu de $\frac1k$ ($k=15$ plis ici).

```python
from scipy import stats
def compare(a, b):
    d = S[a] - S[b]; k = len(d); n_test, n_train = len(ytr) // 5, len(ytr) - len(ytr) // 5
    var_corr = d.var(ddof=1) * (1 / k + n_test / n_train)
    t = d.mean() / np.sqrt(var_corr); p = 2 * stats.t.sf(abs(t), k - 1)
    return {"écart moyen d'AUC": round(d.mean(), 4), "t corrigé": round(t, 2), "p": round(p, 4)}
print("boosting - logistique :", compare("boosting", "logistique")); print("boosting - forêt      :", compare("boosting", "forêt"))
```
<!--sortie-->
```text
boosting - logistique : {"écart moyen d'AUC": np.float64(0.0295), 't corrigé': np.float64(9.35), 'p': np.float64(0.0)}
boosting - forêt      : {"écart moyen d'AUC": np.float64(0.0042), 't corrigé': np.float64(0.99), 'p': np.float64(0.3392)}
```


Le boosting l'emporte clairement sur la régression logistique (écart 0,029, $p<0{,}001$). Face à la forêt, l'écart est de 0,004 avec $p=$ 0,339 : à ce niveau de précision, la différence n'est pas établie.

> ⚠️ **Le test de Student ordinaire** sur ces 15 différences ignorerait le recouvrement des plis et serait **trop optimiste** (il rejetterait trop souvent l'égalité). La correction ci-dessus est l'usage recommandé.

### Application 2.9 — Les modèles classiques face au fléau de la dimension

*Sections du livre : 2.5.* **Objectif** : mesurer comment k-NN, SVM et boosting réagissent à l'ajout de variables **inutiles**.

```python
from sklearn.neighbors import KNeighborsClassifier
rng = np.random.default_rng(2)
lignes = []
for k_bruit in (0, 20, 100, 300):
    bruit_tr, bruit_te = rng.normal(size=(len(Xtr), k_bruit)), rng.normal(size=(len(Xte), k_bruit))
    pre = pre_lin.fit(Xtr, ytr); A, B = pre.transform(Xtr), pre.transform(Xte)
    A = np.hstack([A.toarray() if hasattr(A, "toarray") else A, bruit_tr]); B = np.hstack([B.toarray() if hasattr(B, "toarray") else B, bruit_te])
    knn = KNeighborsClassifier(75).fit(A, ytr)
    hgb = HistGradientBoostingClassifier(learning_rate=0.1, max_iter=100, early_stopping=False, random_state=0).fit(np.hstack([Xtr_o.fillna(Xtr_o.median()).to_numpy(), bruit_tr]), ytr)
    lignes.append({"variables de bruit ajoutées": k_bruit, "AUC k-NN": round(roc_auc_score(yte, knn.predict_proba(B)[:, 1]), 4),
                   "AUC boosting": round(roc_auc_score(yte, hgb.predict_proba(np.hstack([Xte_o.fillna(Xtr_o.median()).to_numpy(), bruit_te]))[:, 1]), 4)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 variables de bruit ajoutées  AUC k-NN  AUC boosting
                           0    0.8562        0.9011
                          20    0.8442        0.9015
                         100    0.8166        0.8981
                         300    0.7975        0.9024
```


Le k-NN passe de 0,856 à 0,797 quand on ajoute 300 variables de pur bruit : les distances sont noyées. Le boosting, qui **choisit** les variables à chaque coupe, passe de 0,901 à 0,902. C'est l'illustration, sur données réelles, de la différence entre un modèle qui **mesure des distances** et un modèle qui **sélectionne**.

### Application 2.10 — Encodage ordonné, CatBoost et empilement sans fuite

*Sections du livre : 2.6.* **Objectif** : implémenter l'encodage ordonné d'une catégorie, le comparer à l'encodage naïf, puis empiler deux modèles en respectant la validation hors pli.

**Étape 1 — une variable à nombreuses modalités, encodée de deux façons.** On croise la ville et la tranche d'âge de dix ans : environ 140 « quartiers » de quelques dizaines de clients. On les encode par la moyenne de la cible, **naïvement** (en incluant le client lui-même) puis de façon **ordonnée** (seulement les clients qui le précèdent dans un ordre aléatoire), et l'on mesure l'AUC d'un modèle logistique sur cette seule colonne, sur l'entraînement **et** sur le test.

```python
rng = np.random.default_rng(0)
q_tr = (Xtr["ville"] + "_" + (Xtr["age"] // 10).astype(int).astype(str)).to_numpy()
q_te = (Xte["ville"] + "_" + (Xte["age"] // 10).astype(int).astype(str)).to_numpy()
prior, a = ytr.mean(), 20
stat = pd.DataFrame({"q": q_tr, "y": ytr.to_numpy()}).groupby("q")["y"].agg(["sum", "count"])
enc_naif = pd.Series(q_tr).map(stat["sum"] / stat["count"]).to_numpy()               # moyenne de la cible, client compris
enc_te = pd.Series(q_te).map((stat["sum"] + a * prior) / (stat["count"] + a)).fillna(prior).to_numpy()
somme, nb, enc_ord = {}, {}, np.zeros(len(q_tr))
for i in rng.permutation(len(q_tr)):                                                  # encodage ORDONNÉ : seulement les clients précédents
    z = q_tr[i]; enc_ord[i] = (somme.get(z, 0.0) + a * prior) / (nb.get(z, 0) + a)
    somme[z] = somme.get(z, 0.0) + ytr.iloc[i]; nb[z] = nb.get(z, 0) + 1
def auc_tr_te(e_tr):
    m = LogisticRegression().fit(e_tr.reshape(-1, 1), ytr)
    return round(roc_auc_score(ytr, m.predict_proba(e_tr.reshape(-1, 1))[:, 1]), 4), round(roc_auc_score(yte, m.predict_proba(enc_te.reshape(-1, 1))[:, 1]), 4)
print(len(stat), "modalités ; naïf (AUC entraînement, test) :", auc_tr_te(enc_naif), "; ordonné :", auc_tr_te(enc_ord))
```
<!--sortie-->
```text
134 modalités ; naïf (AUC entraînement, test) : (0.7545, 0.7135) ; ordonné : (0.7019, 0.7135)
```


Avec 134 modalités (environ 67 clients chacune), l'encodage naïf donne une AUC de 0,754 sur l'entraînement mais de 0,714 seulement sur le test : l'écart est la **fuite** (le client a contribué à la valeur qui le décrit). L'encodage ordonné donne 0,702 sur l'entraînement et 0,714 sur le test : **l'entraînement et le test racontent la même histoire**, ce qui est le signe d'une variable honnête. Plus les modalités sont rares, plus l'écart grandit (voir l'identifiant de zone du livre, 2.6.1).

**Étape 2 — l'empilement hors pli de deux modèles.**

```python
from sklearn.model_selection import cross_val_predict
from scipy.special import logit
bases = [(make_pipeline(pre_lin, LogisticRegression(C=0.3, max_iter=1000)), Xtr, Xte),
         (HistGradientBoostingClassifier(learning_rate=0.05, max_iter=200, early_stopping=False, categorical_features="from_dtype", random_state=0), Xtr_c, Xte_c)]
oof = np.column_stack([cross_val_predict(m, A, ytr, cv=cv5, method="predict_proba")[:, 1] for m, A, _ in bases])
pte = np.column_stack([m.fit(A, ytr).predict_proba(B)[:, 1] for m, A, B in bases])
L = lambda P: logit(np.clip(P, 1e-4, 1 - 1e-4))
meta = LogisticRegression().fit(L(oof), ytr)
print("coefficients du méta-modèle (logistique, boosting) :", meta.coef_[0].round(2))
print("AUC test : logistique", round(roc_auc_score(yte, pte[:, 0]), 4), "| boosting", round(roc_auc_score(yte, pte[:, 1]), 4), "| empilement", round(roc_auc_score(yte, meta.predict_proba(L(pte))[:, 1]), 4))
```
<!--sortie-->
```text
coefficients du méta-modèle (logistique, boosting) : [0.2  0.68]
AUC test : logistique 0.8659 | boosting 0.9032 | empilement 0.9028
```


L'empilement apprend à donner l'essentiel du poids au boosting (0,68) et un poids moindre au modèle linéaire (0,20). Mais son AUC de test (0,903) n'est pas supérieure à celle du boosting seul (0,903) : le modèle linéaire n'apporte presque rien de neuf (rappel des corrélations élevées entre modèles, section 2.6.2). Vérifiez que, si vous entraînez le méta-modèle sur les prédictions **faites sur l'entraînement** (`m.fit(A, ytr).predict_proba(A)`), le poids du modèle le plus « sur-ajusté » gonfle.

## Exercices

### Exercice 2.1 ⭐ — Quelle perte pour quelle marge ? (section 2.1.1)

Pour des marges $m=-1$, $0{,}5$ et $3$, calculez les pertes charnière $\max(0,1-m)$, logistique $\ln(1+e^{-m})$ et quadratique $(1-m)^2$. Laquelle punit un client **très bien classé** ? Laquelle ignore complètement les exemples de marge supérieure à 1 ?

### Exercice 2.2 ⭐⭐ — Un pas de gradient (section 2.1.3)

Trois clients : $x=(0,\,1,\,2)$, $y=(0,\,1,\,1)$. Partant de $w=0$, $b=0$, calculez le gradient de la perte logistique moyenne en $w$ et en $b$, puis les nouveaux paramètres après un pas de $\eta=0{,}4$. Calculez la perte avant et après.

### Exercice 2.3 ⭐⭐ — Seuillage contre rétrécissement (section 2.1.5)

Dans le cas orthonormé, les estimations non pénalisées sont $z=(2{,}4;\ -0{,}7;\ 0{,}2)$. Donnez les coefficients du Lasso ($\operatorname{signe}(z)(|z|-\lambda)_+$) et de Ridge ($z/(1+\lambda)$) pour $\lambda=0{,}5$. Combien de variables le Lasso conserve-t-il ? Pour quelle valeur de $\lambda$ élimine-t-il la deuxième variable ?

### Exercice 2.4 ⭐ — Quelle coupe choisir ? (section 2.2.3)

Un nœud contient 100 clients dont 30 sont partis. La coupe A sépare 40 clients (dont 25 partis) à gauche et 60 (dont 5 partis) à droite. La coupe B sépare 70 clients (dont 20 partis) à gauche et 30 (dont 10 partis) à droite. Calculez l'impureté de Gini du nœud et le gain de chaque coupe. Laquelle l'arbre choisit-il ?

### Exercice 2.5 ⭐⭐ — Un arbre de régression (section 2.2.4)

Huit clients : $x=(1,2,3,4,5,6,7,8)$, dépense $y=(5,7,6,8,30,28,33,31)$. Trouvez la meilleure coupe de la forme « $x\le s$ » au sens de la somme des carrés des écarts, puis la prédiction de chaque feuille et la somme des carrés résiduelle.

### Exercice 2.6 ⭐⭐⭐ — Élaguer par coût-complexité (section 2.2.5)

Une suite d'arbres emboîtés a pour nombres de feuilles et erreurs d'entraînement : $T_0$ (7 feuilles, erreur 10), $T_1$ (5, 12), $T_2$ (3, 18), $T_3$ (1, 30). Pour chaque arbre, calculez $R_\alpha(T)=R(T)+\alpha|T|$ avec $\alpha=0{,}5$, $2$ et $5$. Quel arbre est optimal pour chaque $\alpha$ ? À partir de quelle valeur de $\alpha$ passe-t-on de $T_0$ à $T_1$, de $T_1$ à $T_2$, de $T_2$ à $T_3$ ?

### Exercice 2.7 ⭐⭐ — Combien d'arbres ? (section 2.3.2)

Des arbres ont une variance $\sigma^2=4$ et une corrélation $\rho=0{,}2$. (a) Quelle est la variance de la moyenne de $B=25$ arbres ? (b) Quelle est la limite quand $B\to\infty$ ? (c) Combien d'arbres faut-il pour que la part « évitable » $\frac{1-\rho}{B}\sigma^2$ soit inférieure à 10 % de la part incompressible ? (d) Que devient la limite si une forêt aléatoire ramène $\rho$ à 0,1 ?

### Exercice 2.8 ⭐⭐ — Les clients hors sac (section 2.3.4)

Une forêt compte $B=300$ arbres sur $n=9\,000$ clients. (a) Combien de clients distincts contient en moyenne un échantillon bootstrap ? (b) Pour un client donné, combien d'arbres ne l'ont jamais vu, en moyenne ? (c) Avec seulement $B=10$ arbres, quelle est la probabilité qu'un client donné ne soit **hors sac pour aucun** arbre ?

### Exercice 2.9 ⭐⭐ — Deux tours de boosting (section 2.4.1)

Cinq clients, $x=(1,2,3,4,5)$ et $y=(2,4,3,11,15)$. Avec des souches et un pas $\nu=0{,}5$ : calculez $F_0$, les résidus, la première souche (meilleure coupe par somme des carrés), $F_1$, puis les nouveaux résidus.

### Exercice 2.10 ⭐⭐⭐ — Valeur de feuille et gain XGBoost (section 2.4.3)

Un nœud contient six clients avec les gradients $g=(-0{,}5;\ -0{,}5;\ -0{,}4;\ 0{,}5;\ 0{,}4;\ -0{,}6)$ et les hessiens $h=(0{,}25;\ 0{,}25;\ 0{,}24;\ 0{,}25;\ 0{,}24;\ 0{,}24)$, $\lambda=2$, $\gamma=0{,}1$. (a) Valeur de feuille si l'on ne coupe pas. (b) Gain de la coupe C1 qui sépare les clients $\{1,2,3\}$ des clients $\{4,5,6\}$, et de la coupe C2 qui sépare $\{1,2,6\}$ de $\{3,4,5\}$. (c) Laquelle choisir, et est-elle effectuée ?

### Exercice 2.11 ⭐⭐ — Bayes naïf avec lissage (section 2.5.3)

Parmi 20 clients (8 partis, 12 restés), on observe : $P(\text{pas de ticket}\mid\text{parti})=2/8$, $P(\text{pas de ticket}\mid\text{resté})=9/12$, $P(\text{courriel jamais ouvert}\mid\text{parti})=0/8$, $P(\text{courriel jamais ouvert}\mid\text{resté})=3/12$. (a) Probabilité de départ d'un client sans ticket et au courriel jamais ouvert, sans lissage. (b) Quel problème pose le 0 ? (c) Refaites le calcul avec le lissage de Laplace (ajouter 1 au numérateur et 2 au dénominateur de chaque probabilité conditionnelle).

### Exercice 2.12 ⭐⭐⭐ — Pourquoi moyenner des modèles corrélés rapporte peu (section 2.6.2)

Deux modèles ont la même variance d'erreur $\sigma^2=1$ et une corrélation d'erreur $\rho_e$. (a) Quelle est la variance d'erreur de leur moyenne ? Calculez-la pour $\rho_e=0$, $0{,}5$ et $0{,}9$. (b) Si le second modèle a une variance d'erreur $\sigma_2^2=4$ (il est nettement moins bon) et $\rho_e=0$, la moyenne **égale** est-elle meilleure que le premier modèle seul ? Quelle pondération optimale $(w,1-w)$ minimise la variance ? (c) Simulez (b) avec 100 000 tirages.

## Corrigés

### Corrigé 2.1

```python
m = np.array([-1.0, 0.5, 3.0])
print(pd.DataFrame({"marge": m, "charnière": np.maximum(0, 1 - m), "logistique": np.log1p(np.exp(-m)), "quadratique": (1 - m) ** 2}).round(3).to_string(index=False))
```
<!--sortie-->
```text
 marge  charnière  logistique  quadratique
  -1.0        2.0       1.313         4.00
   0.5        0.5       0.474         0.25
   3.0        0.0       0.049         4.00
```

La perte **quadratique** punit le client très bien classé ($m=3$ : $(1-3)^2=4$) : c'est absurde pour la classification. La perte **charnière** vaut exactement 0 dès que $m\ge1$ : les exemples bien classés avec marge suffisante sont **ignorés** (les autres sont les vecteurs de support). La logistique, elle, reste faiblement positive (0,049 pour $m=3$) et continue à pousser vers des marges plus grandes.

### Corrigé 2.2

Avec $w=b=0$, $p_i=0{,}5$ ; erreurs $p_i-y_i=(0{,}5;\ -0{,}5;\ -0{,}5)$. Donc $\partial L/\partial w=\frac13[0{,}5\times0+(-0{,}5)\times1+(-0{,}5)\times2]=-0{,}5$ et $\partial L/\partial b=\frac13(0{,}5-0{,}5-0{,}5)=-\frac16\approx-0{,}1667$. Après le pas $\eta=0{,}4$ : $w=0{,}2$, $b=0{,}0667$.

```python
x3, y3 = np.array([0.0, 1.0, 2.0]), np.array([0, 1, 1])
def perte3(w, b):
    p = 1 / (1 + np.exp(-(w * x3 + b))); return -np.mean(y3 * np.log(p) + (1 - y3) * np.log(1 - p))
print("gradient :", np.mean((0.5 - y3) * x3), np.mean(0.5 - y3), "| paramètres :", 0.4 * 0.5, 0.4 / 6, "| pertes :", round(perte3(0, 0), 4), "->", round(perte3(0.2, 0.4 / 6), 4))
```
<!--sortie-->
```text
gradient : -0.5 -0.16666666666666666 | paramètres : 0.2 0.06666666666666667 | pertes : 0.6931 -> 0.5942
```

### Corrigé 2.3

Lasso : $(2{,}4-0{,}5;\ -(0{,}7-0{,}5);\ 0)=(1{,}9;\ -0{,}2;\ 0)$ : **deux** variables conservées (la troisième, $|0{,}2|<0{,}5$, est annulée). Ridge : $z/1{,}5=(1{,}6;\ -0{,}467;\ 0{,}133)$ : aucune n'est annulée. Le Lasso élimine la deuxième variable dès que $\lambda\ge0{,}7$.

### Corrigé 2.4

$G(\text{nœud})=1-0{,}3^2-0{,}7^2=0{,}42$. Coupe A : gauche $p=\frac{25}{40}=0{,}625$, $G=1-0{,}625^2-0{,}375^2=0{,}469$ ; droite $p=\frac5{60}$, $G=0{,}153$ ; impureté $=0{,}4\times0{,}469+0{,}6\times0{,}153=0{,}279$ ; **gain $0{,}141$**. Coupe B : gauche $p=\frac{20}{70}$, $G=0{,}408$ ; droite $p=\frac13$, $G=0{,}444$ ; impureté $=0{,}7\times0{,}408+0{,}3\times0{,}444=0{,}419$ ; gain $0{,}001$. L'arbre choisit **A** : B ne sépare presque rien (les deux groupes restent aussi mélangés que le nœud).

```python
def gini2(p): return 1 - p ** 2 - (1 - p) ** 2
g0 = gini2(0.3)
print({"A": round(g0 - 0.4 * gini2(25 / 40) - 0.6 * gini2(5 / 60), 4), "B": round(g0 - 0.7 * gini2(20 / 70) - 0.3 * gini2(10 / 30), 4)})
```
<!--sortie-->
```text
{'A': 0.1408, 'B': 0.001}
```

### Corrigé 2.5

Les $y$ passent de 5-8 (clients 1 à 4) à 28-33 (clients 5 à 8) : la coupe naturelle est $x\le4{,}5$.

```python
xr, yr = np.arange(1, 9), np.array([5, 7, 6, 8, 30, 28, 33, 31.0])
sse = lambda v: ((v - v.mean()) ** 2).sum()
res = {s + 0.5: sse(yr[xr <= s]) + sse(yr[xr > s]) for s in range(1, 8)}
meilleur = min(res, key=res.get)
print({k: round(v, 1) for k, v in res.items()}); print("meilleure coupe : x <=", meilleur, "| feuilles :", yr[xr <= meilleur].mean(), yr[xr > meilleur].mean(), "| SSE :", round(res[meilleur], 1), "| SSE avant :", sse(yr))
```
<!--sortie-->
```text
{1.5: np.float64(961.7), 2.5: np.float64(753.3), 3.5: np.float64(420.0), 4.5: np.float64(18.0), 5.5: np.float64(459.5), 6.5: np.float64(684.0), 7.5: np.float64(991.4)}
meilleure coupe : x <= 4.5 | feuilles : 6.5 30.5 | SSE : 18.0 | SSE avant : 1170.0
```

À gauche la moyenne est $\frac{5+7+6+8}4=6{,}5$ (somme des carrés $2{,}25+0{,}25+0{,}25+2{,}25=5$), à droite $\frac{30+28+33+31}4=30{,}5$ (somme $0{,}25+6{,}25+6{,}25+0{,}25=13$) : somme résiduelle $18$, contre 1170 avant la coupe (moyenne générale 18,5).

### Corrigé 2.6

```python
arbres = {"T0": (7, 10), "T1": (5, 12), "T2": (3, 18), "T3": (1, 30)}
tab = pd.DataFrame({f"alpha = {a}": {k: R + a * L for k, (L, R) in arbres.items()} for a in (0.5, 2, 5)})
print(tab.round(1)); print(tab.idxmin().to_dict())
```
<!--sortie-->
```text
    alpha = 0.5  alpha = 2  alpha = 5
T0         13.5         24         45
T1         14.5         22         37
T2         19.5         24         33
T3         30.5         32         35
{'alpha = 0.5': 'T0', 'alpha = 2': 'T1', 'alpha = 5': 'T2'}
```

$\alpha=0{,}5$ : $T_0$ ($10+3{,}5=13{,}5$) ; $\alpha=2$ : $T_1$ ($12+10=22$ contre $24$ pour $T_0$ et $24$ pour $T_2$) ; $\alpha=5$ : $T_2$ ($18+15=33$ contre $37$ pour $T_1$ et $35$ pour $T_3$). Les seuils de passage valent $\frac{R(T_{k+1})-R(T_k)}{|T_k|-|T_{k+1}|}$ : de $T_0$ à $T_1$, $\frac{12-10}{7-5}=1$ ; de $T_1$ à $T_2$, $\frac{18-12}{5-3}=3$ ; de $T_2$ à $T_3$, $\frac{30-18}{3-1}=6$.

### Corrigé 2.7

(a) $\rho\sigma^2+\frac{1-\rho}B\sigma^2=0{,}2\times4+\frac{0{,}8\times4}{25}=0{,}8+0{,}128=0{,}928$. (b) $\rho\sigma^2=0{,}8$. (c) On veut $\frac{(1-\rho)\sigma^2}{B}\le0{,}1\,\rho\sigma^2$, soit $B\ge\frac{1-\rho}{0{,}1\rho}=\frac{0{,}8}{0{,}02}=40$ arbres. (d) La limite tombe à $0{,}1\times4=0{,}4$ : la décorrélation divise le plancher par deux.

```python
f = lambda B, rho, s2=4: rho * s2 + (1 - rho) * s2 / B
print(f(25, 0.2), f(10**9, 0.2), f(40, 0.2) - 0.8, 0.1 * 0.8, f(10**9, 0.1))
```
<!--sortie-->
```text
0.928 0.8000000032000001 0.07999999999999996 0.08000000000000002 0.40000000360000004
```

### Corrigé 2.8

(a) $n\bigl(1-(1-\frac1n)^n\bigr)\approx0{,}632\times9\,000\approx5\,689$ clients distincts. (b) Un arbre ne voit pas un client donné avec probabilité $0{,}368$ : $300\times0{,}368\approx110$ arbres en moyenne. (c) Il est hors sac pour un arbre avec probabilité $0{,}368$, donc pour **aucun** des 10 avec probabilité $(1-0{,}368)^{10}=0{,}632^{10}\approx0{,}0102$ : environ **1 client sur 100** n'aurait aucune prédiction hors sac.

```python
n = 9000; p_out = (1 - 1 / n) ** n
print(round(n * (1 - p_out)), round(300 * p_out, 1), round((1 - p_out) ** 10, 4))
```
<!--sortie-->
```text
5689 110.4 0.0102
```

### Corrigé 2.9

$F_0=\frac{2+4+3+11+15}5=7$ ; résidus $r=(-5;\ -3;\ -4;\ 4;\ 8)$. Meilleure coupe : $x\le3$ (moyennes des résidus $-4$ à gauche et $+6$ à droite ; le détail de toutes les coupes est donné par le code). Souche : $-4$ à gauche, $+6$ à droite ; avec $\nu=0{,}5$ : $F_1=7-2=5$ pour $x\le3$ et $7+3=10$ pour $x\ge4$. Nouveaux résidus : $y-F_1=(-3;\ -1;\ -2;\ 1;\ 5)$.

```python
xs5, ys5 = np.arange(1, 6), np.array([2, 4, 3, 11, 15.0])
r = ys5 - ys5.mean(); sse5 = lambda v: ((v - v.mean()) ** 2).sum()
print("F0 =", ys5.mean(), "| résidus :", r, "| somme des carrés selon la coupe :", {s + 0.5: round(sse5(r[:s]) + sse5(r[s:]), 2) for s in range(1, 5)})
F1 = np.where(xs5 <= 3, ys5.mean() + 0.5 * r[:3].mean(), ys5.mean() + 0.5 * r[3:].mean()); print("F1 =", F1, "| résidus 2 :", ys5 - F1)
```
<!--sortie-->
```text
F0 = 7.0 | résidus : [-5. -3. -4.  4.  8.] | somme des carrés selon la coupe : {1.5: np.float64(98.75), 2.5: np.float64(76.67), 3.5: np.float64(10.0), 4.5: np.float64(50.0)}
F1 = [ 5.  5.  5. 10. 10.] | résidus 2 : [-3. -1. -2.  1.  5.]
```


La coupe $x\le3$ est la meilleure : la somme des carrés des résidus tombe à 10 (gauche : $(-5+4)^2+(-3+4)^2+0=2$ ; droite : $(4-6)^2+(8-6)^2=8$), contre 98,8 pour $x\le1$, 76,7 pour $x\le2$ et 50 pour $x\le4$. Au tour 2, le client 5, dont le résidu vaut encore 5, serait la cible de la souche suivante.

### Corrigé 2.10

(a) $G=\sum g=-0{,}5-0{,}5-0{,}4+0{,}5+0{,}4-0{,}6=-1{,}1$ ; $H=1{,}47$ ; $w^*=-\frac{G}{H+\lambda}=\frac{1{,}1}{3{,}47}\approx0{,}317$.

```python
g = np.array([-0.5, -0.5, -0.4, 0.5, 0.4, -0.6]); h = np.array([0.25, 0.25, 0.24, 0.25, 0.24, 0.24]); lam, gam = 2.0, 0.1
def gain(gauche):
    gl, hl = g[gauche].sum(), h[gauche].sum(); gr, hr = g.sum() - gl, h.sum() - hl
    return 0.5 * (gl ** 2 / (hl + lam) + gr ** 2 / (hr + lam) - g.sum() ** 2 / (h.sum() + lam)) - gam
print("w* =", round(-g.sum() / (h.sum() + lam), 4), "| gain C1 =", round(gain([0, 1, 2]), 4), "| gain C2 =", round(gain([0, 1, 5]), 4))
```
<!--sortie-->
```text
w* = 0.317 | gain C1 = 0.0998 | gain C2 = 0.2386
```


(b) La coupe C1 sépare $\{1,2,3\}$ ($G=-1{,}4$, $H=0{,}74$) de $\{4,5,6\}$ ($G=0{,}3$, $H=0{,}73$) : gain 0,100. La coupe C2 sépare $\{1,2,6\}$ ($G=-1{,}6$) de $\{3,4,5\}$ ($G=+0{,}5$) : gain 0,239. (c) On choisit la coupe de **gain maximal**, ici C2 : elle regroupe presque tous les gradients négatifs d'un côté et isole les gradients positifs de l'autre. Elle est **effectuée**, parce que son gain est positif après soustraction de $\gamma$.

### Corrigé 2.11

(a) Score « parti » : $\frac8{20}\times\frac28\times\frac08=0$ ; score « resté » : $\frac{12}{20}\times\frac9{12}\times\frac3{12}=0{,}1125$ ; probabilité de départ $=0$. (b) Un **zéro** dans une probabilité conditionnelle annule tout le produit : le modèle affirme qu'aucun client parti n'a jamais « courriel jamais ouvert », donc exclut le départ **définitivement**, sur la seule base de 8 observations. (c) Avec le lissage : $P(\text{pas de ticket}\mid\text{parti})=\frac{2+1}{8+2}=0{,}3$, $P(\text{courriel}\mid\text{parti})=\frac{0+1}{8+2}=0{,}1$, $P(\text{pas de ticket}\mid\text{resté})=\frac{10}{14}=0{,}714$, $P(\text{courriel}\mid\text{resté})=\frac{4}{14}=0{,}286$. Scores : parti $0{,}4\times0{,}3\times0{,}1=0{,}012$ ; resté $0{,}6\times0{,}714\times0{,}286=0{,}1224$ ; probabilité de départ $\frac{0{,}012}{0{,}1344}\approx0{,}089$.

```python
sp = 8 / 20 * 3 / 10 * 1 / 10; sr = 12 / 20 * 10 / 14 * 4 / 14
print(round(sp, 4), round(sr, 4), round(sp / (sp + sr), 3))
```
<!--sortie-->
```text
0.012 0.1224 0.089
```

### Corrigé 2.12

(a) La variance de $\frac{e_1+e_2}2$ est $\frac{\sigma^2+\sigma^2+2\rho_e\sigma^2}4=\frac{(1+\rho_e)\sigma^2}2$ : $0{,}5$ pour $\rho_e=0$, $0{,}75$ pour $\rho_e=0{,}5$, $0{,}95$ pour $\rho_e=0{,}9$ : plus les erreurs sont corrélées, moins on gagne (au mieux, on divise par 2). (b) La moyenne égale a pour variance $\frac{1+4}4=1{,}25$, **plus** que le premier modèle seul (1) : mélanger avec un modèle nettement plus mauvais fait **perdre**. La pondération $(w,1-w)$ minimise $w^2\cdot1+(1-w)^2\cdot4$ pour $w=\frac{4}{5}=0{,}8$ (poids inversement proportionnel aux variances), avec une variance de $0{,}8$.

```python
rng = np.random.default_rng(0); e1, e2 = rng.normal(0, 1, 100000), rng.normal(0, 2, 100000)
print("seul :", round(e1.var(), 3), "| moyenne égale :", round(((e1 + e2) / 2).var(), 3), "| pondérée 0,8/0,2 :", round((0.8 * e1 + 0.2 * e2).var(), 3))
```
<!--sortie-->
```text
seul : 1.0 | moyenne égale : 1.256 | pondérée 0,8/0,2 : 0.802
```
