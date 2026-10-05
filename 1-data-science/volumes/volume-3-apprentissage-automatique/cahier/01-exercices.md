# Chapitre 1 : La démarche d'apprentissage automatique — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 1 du livre (formulation, validation croisée, biais-variance, rigueur expérimentale, réglage). Les **applications** reprennent, avec tout leur code, les expériences dont le livre ne montre que les résultats ; les **exercices** font manipuler les idées à la main. Données : `donnees/clients_ml.csv` (12 000 clients simulés, voir le livre). Prérequis : Python, pandas, scikit-learn.

## Préparation

Toutes les applications partent des mêmes lignes : charger les clients, exclure les colonnes qui ne sont pas des variables d'entrée, et réserver 25 % des clients pour un test final que l'on n'ouvrira qu'à l'application 1.7.

```python
import numpy as np, pandas as pd, warnings
warnings.filterwarnings("ignore")
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.metrics import roc_auc_score
from sklearn.pipeline import make_pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier

df = pd.read_csv("donnees/clients_ml.csv")
CATEG = ["ville", "canal_acquisition", "appareil", "categorie_preferee"]
EXCLUS = ["id_client", "churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible"]
NUM = [c for c in df.columns if c not in CATEG + EXCLUS]
X = df[NUM + CATEG].copy()
X[CATEG] = X[CATEG].astype("category")
y = df["churn_90j"]
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=0)
print(X_tr.shape, X_te.shape, round(y_tr.mean(), 4))
```
<!--sortie-->
```text
(9000, 19) (3000, 19) 0.1404
```

Puis les deux modèles du chapitre : une régression logistique précédée d'un prétraitement (imputation par la médiane avec indicateur de valeur manquante, centrage-réduction, encodage des catégories) et un gradient boosting qui gère seul les valeurs manquantes et les catégories.

```python
def modele_logit(C=1.0):
    prep = ColumnTransformer([
        ("num", make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler()), NUM),
        ("cat", OneHotEncoder(handle_unknown="ignore"), CATEG)])
    return make_pipeline(prep, LogisticRegression(C=C, max_iter=2000))

def modele_hgb(**kw):
    return HistGradientBoostingClassifier(categorical_features="from_dtype", random_state=0, **kw)

cv5 = StratifiedKFold(5, shuffle=True, random_state=0)
for nom, m in [("régression logistique", modele_logit()), ("gradient boosting", modele_hgb())]:
    print(nom, cross_val_score(m, X_tr, y_tr, cv=cv5, scoring="roc_auc").mean().round(4))
```
<!--sortie-->
```text
régression logistique 0.8603
gradient boosting 0.8881
```

## Applications

### Application 1.1 — Détecter la fuite d'information (section 1.1.6)

**Contexte.** Le tableau contient une colonne `commandes_apres_cible` (commandes des trois mois suivants). Un stagiaire l'a ajoutée aux variables d'entrée et annonce un gain spectaculaire. Vous devez le quantifier, comprendre pourquoi il est faux, puis étudier un second type de fuite : le prétraitement fait avant la validation.

**Étape 1 : mesurer le « gain ».**

```python
Xl = X_tr.copy()
Xl["commandes_apres_cible"] = df.loc[X_tr.index, "commandes_apres_cible"]
sans = cross_val_score(modele_hgb(), X_tr, y_tr, cv=5, scoring="roc_auc").mean()
avec = cross_val_score(modele_hgb(), Xl, y_tr, cv=5, scoring="roc_auc").mean()
print("sans :", round(sans, 4), "| avec :", round(avec, 4), "| écart :", round(avec - sans, 4))
```
<!--sortie-->
```text
sans : 0.8895 | avec : 0.9221 | écart : 0.0325
```

**Étape 2 : regarder l'importance de la colonne** (perte d'AUC quand on mélange ses valeurs, sur un jeu de validation).

```python
from sklearn.inspection import permutation_importance
a, b, ya, yb = train_test_split(Xl, y_tr, test_size=0.3, stratify=y_tr, random_state=1)
m = modele_hgb().fit(a, ya)
pi = permutation_importance(m, b, yb, scoring="roc_auc", n_repeats=3, random_state=0)
print(pd.Series(pi.importances_mean, index=b.columns).sort_values(ascending=False).head(4).round(3))
```
<!--sortie-->
```text
commandes_apres_cible    0.156
age                      0.047
recence_jours            0.034
satisfaction_moy         0.024
dtype: float64
```

**Étape 3 : l'audit du calendrier.** On construit le tableau « variable → connue au 31 décembre ? » : c'est lui, et non les chiffres, qui tranche.

```python
audit = pd.DataFrame({"variable": ["recence_jours", "nb_tickets_support_12m", "satisfaction_moy", "commandes_apres_cible"],
                      "calculée à partir de": ["historique jusqu'au 31/12", "tickets avant le 31/12", "enquêtes avant le 31/12", "commandes de janvier à mars"],
                      "connue à t0 ?": ["oui", "oui", "oui", "NON"]})
print(audit.to_string(index=False))
```
<!--sortie-->
```text
              variable        calculée à partir de connue à t0 ?
         recence_jours   historique jusqu'au 31/12           oui
nb_tickets_support_12m      tickets avant le 31/12           oui
      satisfaction_moy     enquêtes avant le 31/12           oui
 commandes_apres_cible commandes de janvier à mars           NON
```

**Étape 4 : la contamination par la sélection de variables.** Sur 100 clients fictifs et 2 000 variables de bruit, comparez une sélection faite *avant* la validation croisée et une sélection faite *dans* le pipeline, pour 5 graines.

```python
from sklearn.feature_selection import SelectKBest, f_classif
avant, dans = [], []
for graine in range(5):
    rng = np.random.default_rng(graine)
    Xn, yn = rng.normal(size=(100, 2000)), rng.integers(0, 2, 100)
    cv = StratifiedKFold(5, shuffle=True, random_state=graine)
    Xs = SelectKBest(f_classif, k=10).fit_transform(Xn, yn)
    avant.append(cross_val_score(LogisticRegression(max_iter=1000), Xs, yn, cv=cv, scoring="roc_auc").mean())
    pipe = make_pipeline(SelectKBest(f_classif, k=10), LogisticRegression(max_iter=1000))
    dans.append(cross_val_score(pipe, Xn, yn, cv=cv, scoring="roc_auc").mean())
print("avant :", np.round(avant, 3), "| dans le pipeline :", np.round(dans, 3))
```
<!--sortie-->
```text
avant : [0.879 0.857 0.895 0.892 0.877] | dans le pipeline : [0.602 0.435 0.599 0.543 0.617]
```

**À vous.** (a) Pourquoi l'AUC « avec » n'atteint-elle pas 1,0, alors que la colonne est tirée de l'avenir ? (b) Quel est le rôle d'un `Pipeline` dans la seconde expérience ? (c) Donnez un exemple de fuite temporelle dans un projet de prévision de ventes.

### Application 1.2 — La loterie du découpage unique (section 1.2.1)

**Objectif.** Mesurer la variabilité d'une estimation par découpage unique, et voir comment elle diminue avec la taille du jeu de validation.

```python
def auc_decoupage(n, graine):
    sub = X_tr.sample(n, random_state=0)
    ys = y_tr.loc[sub.index]
    a, b, ya, yb = train_test_split(sub, ys, test_size=0.2, stratify=ys, random_state=graine)
    return roc_auc_score(yb, modele_logit().fit(a, ya).predict_proba(b)[:, 1])

for n in (500, 2000, 6000):
    aucs = np.array([auc_decoupage(n, s) for s in range(100)])
    print(f"n = {n:5d} : AUC moyenne {aucs.mean():.3f} | écart-type {aucs.std():.3f} | min {aucs.min():.3f} | max {aucs.max():.3f}")
```
<!--sortie-->
```text
n =   500 : AUC moyenne 0.872 | écart-type 0.046 | min 0.748 | max 0.948
n =  2000 : AUC moyenne 0.862 | écart-type 0.025 | min 0.790 | max 0.914
n =  6000 : AUC moyenne 0.864 | écart-type 0.013 | min 0.830 | max 0.890
```

**À vous.** Le nombre de clients partis dans le jeu de validation vaut environ $0{,}14\times0{,}2\,n$. Vérifiez que l'écart-type de l'AUC décroît à peu près comme l'inverse de la racine de ce nombre. Que conclure sur la taille minimale d'un jeu de validation ?

### Application 1.3 — Combien de plis ? (section 1.2.2)

**Objectif.** Comparer plusieurs $k$ en comparant chaque estimation par validation croisée à la vraie performance du modèle (mesurée sur des clients laissés de côté).

```python
resultats = {k: [] for k in (2, 5, 10, 20)}
vrai = []
for r in range(10):
    sb = X_tr.sample(1000, random_state=100 + r)
    ys = y_tr.loc[sb.index]
    hors = X_tr.drop(sb.index)
    vrai.append(roc_auc_score(y_tr.loc[hors.index], modele_logit().fit(sb, ys).predict_proba(hors)[:, 1]))
    for k in resultats:
        cv = StratifiedKFold(k, shuffle=True, random_state=r)
        resultats[k].append(cross_val_score(modele_logit(), sb, ys, cv=cv, scoring="roc_auc").mean())
print("vraie AUC :", round(np.mean(vrai), 4))
for k, v in resultats.items():
    print(f"k = {k:2d} : estimation {np.mean(v):.4f} | biais {np.mean(v) - np.mean(vrai):+.4f} | écart-type {np.std(v):.4f}")
```
<!--sortie-->
```text
vraie AUC : 0.8441
k =  2 : estimation 0.8335 | biais -0.0106 | écart-type 0.0212
k =  5 : estimation 0.8454 | biais +0.0013 | écart-type 0.0139
k = 10 : estimation 0.8455 | biais +0.0015 | écart-type 0.0145
k = 20 : estimation 0.8471 | biais +0.0030 | écart-type 0.0133
```

**À vous.** Ajoutez la validation « un seul laissé de côté » sur 100 clients (`LeaveOneOut`) : pourquoi la mesure d'AUC par pli y est-elle impossible, et comment la contourner (indice : `cross_val_predict`) ?

### Application 1.4 — Valider une série temporelle sans tricher (section 1.2.3)

**Objectif.** Montrer qu'une validation croisée aléatoire est trompeuse sur une série temporelle. On simule une série mensuelle (tendance, saisonnalité, bruit corrélé), on construit des variables retardées, et on compare trois estimations de l'erreur.

```python
from sklearn.model_selection import KFold, TimeSeriesSplit
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

rng = np.random.default_rng(7)
T = 144
t = np.arange(T)
bruit = np.zeros(T)
for i in range(1, T):
    bruit[i] = 0.8 * bruit[i - 1] + rng.normal(0, 2)
d = pd.DataFrame({"y": 100 + 0.5 * t + 8 * np.sin(2 * np.pi * t / 12) + bruit})
for lag in (1, 2, 3, 12):
    d[f"l{lag}"] = d.y.shift(lag)
d["mois"] = t % 12
d = d.dropna().reset_index(drop=True)
Xs, ys = d.drop(columns="y"), d.y
```

```python
def modele():
    return RandomForestRegressor(100, min_samples_leaf=2, random_state=0, n_jobs=1)

def rmse(u, v):
    return np.sqrt(mean_squared_error(u, v))

alea = -cross_val_score(modele(), Xs, ys, cv=KFold(5, shuffle=True, random_state=0), scoring="neg_root_mean_squared_error").mean()
temps = -cross_val_score(modele(), Xs, ys, cv=TimeSeriesSplit(5), scoring="neg_root_mean_squared_error").mean()
n = len(d)
futur = rmse(ys[n - 24:], modele().fit(Xs[:n - 24], ys[:n - 24]).predict(Xs[n - 24:]))
print("RMSE : CV aléatoire", round(alea, 2), "| CV temporelle", round(temps, 2), "| 24 derniers mois", round(futur, 2))
```
<!--sortie-->
```text
RMSE : CV aléatoire 3.51 | CV temporelle 7.31 | 24 derniers mois 6.75
```

**À vous.** (a) Ajoutez `gap=12` à `TimeSeriesSplit` : que change cet espace entre entraînement et validation, et dans quelle situation est-il utile ? (b) Refaites l'expérience sans la variable `l1` : l'écart entre validation aléatoire et temporelle diminue-t-il ? Pourquoi ?

### Application 1.5 — Biais et variance par simulation (section 1.3.4)

**Objectif.** Estimer, pour des polynômes de degré croissant, le biais carré et la variance en simulant de nombreux jeux d'entraînement, et vérifier la décomposition $\text{erreur}=\sigma^2+\text{biais}^2+\text{variance}$.

```python
from numpy.polynomial import Polynomial

rng = np.random.default_rng(1)
f = lambda x: np.sin(1.5 * np.pi * x)
sigma, N, R = 0.3, 30, 500
grille = np.linspace(0, 1, 200)
lignes = []
for degre in range(1, 8):
    P = np.empty((R, len(grille)))
    for r in range(R):
        x = rng.uniform(0, 1, N)
        P[r] = Polynomial.fit(x, f(x) + rng.normal(0, sigma, N), degre)(grille)
    lignes.append((degre, ((P.mean(0) - f(grille)) ** 2).mean(), P.var(0).mean()))
tab = pd.DataFrame(lignes, columns=["degré", "biais²", "variance"])
tab["erreur attendue"] = tab["biais²"] + tab["variance"] + sigma ** 2
print(tab.round(4).to_string(index=False))
```
<!--sortie-->
```text
 degré  biais²  variance  erreur attendue
     1  0.1835    0.0241           0.2976
     2  0.0330    0.0166           0.1396
     3  0.0033    0.0175           0.1108
     4  0.0003    0.0252           0.1155
     5  0.0001    0.0758           0.1659
     6  0.0003    0.1434           0.2337
     7  0.0012    0.4150           0.5062
```

**Vérification directe de la décomposition.** On mesure l'erreur quadratique sur de **nouvelles** observations (avec leur bruit) pour le degré 3, et on la compare à la somme des trois termes.

```python
errs = []
for r in range(R):
    x = rng.uniform(0, 1, N)
    p = Polynomial.fit(x, f(x) + rng.normal(0, sigma, N), 3)
    xn = rng.uniform(0, 1, 200)
    errs.append(((f(xn) + rng.normal(0, sigma, 200) - p(xn)) ** 2).mean())
print("erreur mesurée (degré 3) :", round(np.mean(errs), 4), "| somme biais² + variance + bruit :", tab.loc[2, "erreur attendue"].round(4))
```
<!--sortie-->
```text
erreur mesurée (degré 3) : 0.1086 | somme biais² + variance + bruit : 0.1108
```

**À vous.** Doublez la taille de l'échantillon ($N=60$) : que deviennent le biais et la variance, et le degré optimal ? Redémontrez la décomposition sur une feuille, sans regarder le livre.

### Application 1.6 — Courbes d'apprentissage et diagnostic (sections 1.3.5 et 1.3.6)

**Objectif.** Dessiner les courbes d'apprentissage de trois modèles et poser un diagnostic pour chacun.

```python
from sklearn.model_selection import learning_curve
from sklearn.tree import DecisionTreeClassifier

tailles = [200, 500, 1000, 2000, 4000, 6000]
cv3 = StratifiedKFold(3, shuffle=True, random_state=0)
arbre = make_pipeline(SimpleImputer(strategy="median"), DecisionTreeClassifier(random_state=0))
for nom, mod, Xm in [("régression logistique", modele_logit(), X_tr), ("gradient boosting", modele_hgb(), X_tr), ("arbre profond", arbre, X_tr[NUM])]:
    _, train, val = learning_curve(mod, Xm, y_tr, train_sizes=tailles, cv=cv3, scoring="roc_auc")[:3]
    print(f"{nom:22s} entraînement {train.mean(1).round(3)} | validation {val.mean(1).round(3)}")
```
<!--sortie-->
```text
régression logistique  entraînement [0.974 0.91  0.892 0.883 0.872 0.868] | validation [0.826 0.833 0.845 0.851 0.857 0.86 ]
gradient boosting      entraînement [1.    1.    1.    1.    1.    0.999] | validation [0.827 0.847 0.863 0.869 0.877 0.886]
arbre profond          entraînement [1. 1. 1. 1. 1. 1.] | validation [0.657 0.651 0.675 0.686 0.677 0.682]
```

**À vous.** Pour chaque modèle, répondez : biais ou variance ? Collecter deux fois plus de clients aiderait-il ? Quelle action concrète proposez-vous ? Puis tracez la courbe de validation de l'arbre selon `max_depth` (de 1 à 20) avec `validation_curve`, et retrouvez la profondeur optimale.

### Application 1.7 — Comparer deux modèles avec rigueur (section 1.4)

**Objectif.** Comparer la régression logistique et le gradient boosting avec un test $t$ corrigé, un test de McNemar et un bootstrap, puis ouvrir le jeu de test **une seule fois**.

```python
from scipy import stats
from sklearn.model_selection import ShuffleSplit

J = 15
al, ah = [], []
for a, b in ShuffleSplit(J, test_size=0.25, random_state=0).split(X_tr, y_tr):
    al.append(roc_auc_score(y_tr.iloc[b], modele_logit().fit(X_tr.iloc[a], y_tr.iloc[a]).predict_proba(X_tr.iloc[b])[:, 1]))
    ah.append(roc_auc_score(y_tr.iloc[b], modele_hgb().fit(X_tr.iloc[a], y_tr.iloc[a]).predict_proba(X_tr.iloc[b])[:, 1]))
d = np.array(ah) - np.array(al)
n1, n2 = len(a), len(b)
t_naif = d.mean() / np.sqrt(d.var(ddof=1) / J)
t_corr = d.mean() / np.sqrt((1 / J + n2 / n1) * d.var(ddof=1))
print("écart moyen", d.mean().round(4), "| t naïf", t_naif.round(2), "| t corrigé", t_corr.round(2), "| p corrigée", round(2 * stats.t.sf(abs(t_corr), J - 1), 6))
```
<!--sortie-->
```text
écart moyen 0.0296 | t naïf 17.71 | t corrigé 7.23 | p corrigée 4e-06
```

```python
a, b, ya, yb = train_test_split(X_tr, y_tr, test_size=0.3, stratify=y_tr, random_state=2)
pl = modele_logit().fit(a, ya).predict_proba(b)[:, 1]
ph = modele_hgb().fit(a, ya).predict_proba(b)[:, 1]
juste_l, juste_h = (pl > 0.25) == yb.values, (ph > 0.25) == yb.values
bb, cc = int((juste_l & ~juste_h).sum()), int((~juste_l & juste_h).sum())
chi2 = (abs(bb - cc) - 1) ** 2 / (bb + cc)
print("McNemar : b =", bb, "c =", cc, "chi2 =", round(chi2, 2), "p =", stats.chi2.sf(chi2, 1))
rng = np.random.default_rng(0)
ecarts = []
for _ in range(1000):
    i = rng.choice(len(yb), len(yb))
    ecarts.append(roc_auc_score(yb.values[i], ph[i]) - roc_auc_score(yb.values[i], pl[i]))
print("bootstrap : écart d'AUC", round(roc_auc_score(yb, ph) - roc_auc_score(yb, pl), 4), "| IC95", np.percentile(ecarts, [2.5, 97.5]).round(4))
```
<!--sortie-->
```text
McNemar : b = 120 c = 211 chi2 = 24.47 p = 7.54250626803909e-07
bootstrap : écart d'AUC 0.0235 | IC95 [0.0112 0.0364]
```

**Le jeu de test, une seule fois.**

```python
ml, mh = modele_logit().fit(X_tr, y_tr), modele_hgb().fit(X_tr, y_tr)
p_l, p_h = ml.predict_proba(X_te)[:, 1], mh.predict_proba(X_te)[:, 1]
rng = np.random.default_rng(1)
bl, bh = [], []
for _ in range(1000):
    i = rng.choice(len(y_te), len(y_te))
    bl.append(roc_auc_score(y_te.values[i], p_l[i]))
    bh.append(roc_auc_score(y_te.values[i], p_h[i]))
for nom, v, bs in [("régression logistique", roc_auc_score(y_te, p_l), bl), ("gradient boosting", roc_auc_score(y_te, p_h), bh)]:
    print(f"{nom} : AUC test {v:.4f}, IC95 {np.percentile(bs, [2.5, 97.5]).round(4)}")
```
<!--sortie-->
```text
régression logistique : AUC test 0.8656, IC95 [0.8476 0.8829]
gradient boosting : AUC test 0.8996, IC95 [0.8829 0.9137]
```

**À vous.** Quelle question chacun des trois outils (test $t$ corrigé, McNemar, bootstrap) pose-t-il réellement ? Pourquoi le test $t$ naïf conclut-il avec une statistique 2,5 fois plus grande ? Si le résultat du test vous déplaisait, que feriez-vous *sans* le consommer ?

### Application 1.8 — Grille, recherche aléatoire et Optuna (section 1.5)

**Objectif.** Comparer trois stratégies de réglage d'un gradient boosting, avec un budget de 20 essais, sur un sous-échantillon de 3 000 clients.

```python
import optuna
from scipy.stats import loguniform, randint
from sklearn.model_selection import GridSearchCV, RandomizedSearchCV
optuna.logging.set_verbosity(optuna.logging.WARNING)

X3 = X_tr.sample(3000, random_state=0)
y3 = y_tr.loc[X3.index]
cv = StratifiedKFold(3, shuffle=True, random_state=0)
grille = {"learning_rate": [0.03, 0.1, 0.3], "max_leaf_nodes": [8, 31, 63]}
gs = GridSearchCV(modele_hgb(), grille, cv=cv, scoring="roc_auc").fit(X3, y3)
print("grille (9 essais) :", gs.best_params_, round(gs.best_score_, 4))
```
<!--sortie-->
```text
grille (9 essais) : {'learning_rate': 0.03, 'max_leaf_nodes': 8} 0.894
```

```python
dist = {"learning_rate": loguniform(0.01, 0.5), "max_leaf_nodes": randint(4, 128),
        "l2_regularization": loguniform(1e-3, 10), "min_samples_leaf": randint(5, 100)}
rs = RandomizedSearchCV(modele_hgb(), dist, n_iter=20, cv=cv, scoring="roc_auc", random_state=0).fit(X3, y3)
print("aléatoire (20 essais) :", round(rs.best_score_, 4))

def objectif(essai):
    p = {"learning_rate": essai.suggest_float("learning_rate", 0.01, 0.5, log=True),
         "max_leaf_nodes": essai.suggest_int("max_leaf_nodes", 4, 128),
         "l2_regularization": essai.suggest_float("l2_regularization", 1e-3, 10, log=True),
         "min_samples_leaf": essai.suggest_int("min_samples_leaf", 5, 100)}
    return cross_val_score(modele_hgb(**p), X3, y3, cv=cv, scoring="roc_auc").mean()

etude = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=0))
etude.optimize(objectif, n_trials=20)
print("TPE (20 essais) :", round(etude.best_value, 4))
```
<!--sortie-->
```text
aléatoire (20 essais) : 0.8932
TPE (20 essais) : 0.8928
```

**L'arrêt précoce.**

```python
m = modele_hgb(early_stopping=True, validation_fraction=0.15, n_iter_no_change=10, max_iter=500).fit(X_tr, y_tr)
print("arrêt après", m.n_iter_, "itérations ; AUC en validation croisée des paramètres retenus :",
      round(cross_val_score(modele_hgb(max_iter=m.n_iter_), X_tr, y_tr, cv=cv5, scoring="roc_auc").mean(), 4))
```
<!--sortie-->
```text
arrêt après 55 itérations ; AUC en validation croisée des paramètres retenus : 0.8892
```

**À vous.** Répétez la recherche aléatoire avec 10 graines : la dispersion des meilleurs scores est-elle plus grande que l'écart entre les trois méthodes ? Que conclure sur « la meilleure méthode » ?

### Application 1.9 — L'optimisme du réglage et la validation imbriquée (section 1.5.5)

**Objectif.** Mesurer comment l'optimisme d'un réglage croît avec le nombre d'essais, sur des étiquettes aléatoires (aucun signal), et vérifier que la validation imbriquée le corrige.

```python
from sklearn.tree import DecisionTreeClassifier

rng = np.random.default_rng(0)
Xb = X_tr[NUM].fillna(X_tr[NUM].median()).sample(1150, random_state=1).values
yb_ = rng.integers(0, 2, 1150)
Xa, Xh, ya_, yh = Xb[:150], Xb[150:], yb_[:150], yb_[150:]
dist_arbre = {"max_depth": randint(1, 12), "min_samples_leaf": randint(1, 20), "max_features": randint(1, len(NUM))}
for n_essais in (1, 10, 100, 300):
    r = RandomizedSearchCV(DecisionTreeClassifier(random_state=0), dist_arbre, n_iter=n_essais, cv=5, scoring="roc_auc", random_state=0).fit(Xa, ya_)
    neuf = roc_auc_score(yh, r.predict_proba(Xh)[:, 1])
    print(f"{n_essais:4d} essais : meilleur AUC en validation croisée {r.best_score_:.3f} | AUC sur 1000 clients neufs {neuf:.3f}")
```
<!--sortie-->
```text
   1 essais : meilleur AUC en validation croisée 0.503 | AUC sur 1000 clients neufs 0.514
  10 essais : meilleur AUC en validation croisée 0.623 | AUC sur 1000 clients neufs 0.493
 100 essais : meilleur AUC en validation croisée 0.651 | AUC sur 1000 clients neufs 0.533
 300 essais : meilleur AUC en validation croisée 0.661 | AUC sur 1000 clients neufs 0.533
```

```python
rech = RandomizedSearchCV(DecisionTreeClassifier(random_state=0), dist_arbre, n_iter=30, cv=3, scoring="roc_auc", random_state=0)
imbrique = cross_val_score(rech, Xa, ya_, cv=StratifiedKFold(5, shuffle=True, random_state=0), scoring="roc_auc")
print("validation imbriquée :", imbrique.mean().round(3))
```
<!--sortie-->
```text
validation imbriquée : 0.483
```

**À vous.** Tracez l'optimisme (meilleur score de validation moins score sur données neuves) en fonction du nombre d'essais. À quelle vitesse croît-il ? Quel lien avec l'espérance du maximum de $n$ variables aléatoires ?

## Exercices

### Exercice 1.1 ⭐ — Risque empirique à la main (section 1.1.1)

Cinq clients ont pour réponse $y=(1,0,0,1,0)$ et pour probabilités prédites $\hat p=(0{,}8;\ 0{,}3;\ 0{,}6;\ 0{,}4;\ 0{,}1)$. Calculez l'exactitude (seuil 0,5), la perte logarithmique, l'erreur de Brier (moyenne de $(\hat p-y)^2$) et l'AUC.

### Exercice 1.2 ⭐ — Le piège de l'exactitude (section 1.1.3)

Sur un jeu de transactions où 2 % sont frauduleuses, le modèle A répond toujours « non frauduleuse ». Le modèle B détecte 60 % des fraudes mais déclenche une fausse alerte sur 3 % des transactions légitimes. Calculez l'exactitude de chacun. Lequel est utile ? Quelle métrique choisiriez-vous ?

### Exercice 1.3 ⭐⭐ — Audit du calendrier (section 1.1.6)

On prédit, au 31 décembre, si un client partira dans les 90 jours. Pour chacune des variables suivantes, dites si l'on peut l'utiliser, et justifiez : (a) le nombre de commandes de l'année écoulée ; (b) le montant du dernier remboursement demandé, enregistré en février ; (c) la satisfaction déclarée dans l'enquête de novembre ; (d) l'indicateur « compte clôturé » (valeur au 31 mars) ; (e) la moyenne, calculée sur tous les clients (y compris ceux du futur jeu de test), des paniers de chaque ville ; (f) le numéro du client (croissant avec la date d'inscription).

### Exercice 1.4 ⭐ — Un seul laissé de côté, à la main (section 1.2.2)

Trois montants : $y=(1,4,10)$. Le « modèle » est la moyenne des observations d'entraînement. Calculez l'erreur quadratique d'entraînement, l'erreur LOO (un seul laissé de côté), et vérifiez le rapport $\left(\frac n{n-1}\right)^2$.

### Exercice 1.5 ⭐⭐ — Construire des plis (section 1.2.3)

(a) On a 23 observations et on fait une validation croisée à 5 plis (sans mélange) : donnez la taille de chaque pli, le nombre de modèles entraînés et la taille de l'entraînement à chaque essai. (b) Sur 50 clients dont 7 sont partis, à 5 plis **stratifiés** : combien de partis dans chaque pli ?

### Exercice 1.6 ⭐⭐ — Découpage temporel (section 1.2.3)

On a 12 mois numérotés de 0 à 11 et on utilise `TimeSeriesSplit(n_splits=3)`. Écrivez à la main les indices d'entraînement et de validation de chaque essai, puis vérifiez avec le code. Pourquoi ce découpage est-il préférable à un tirage aléatoire de plis pour prévoir les ventes ?

### Exercice 1.7 ⭐⭐ — Le meilleur estimateur biaisé (section 1.3.2)

On estime une moyenne $\mu=3$ avec $n=9$ observations de variance $\sigma^2=9$. Montrez que l'estimateur $c\,\bar y$ a pour erreur quadratique $(c-1)^2\mu^2+c^2\sigma^2/n$, trouvez $c^\star$, calculez l'erreur minimale, et comparez avec celle de $\bar y$.

### Exercice 1.8 ⭐⭐⭐ — Lire des courbes d'apprentissage (section 1.3.6)

Deux modèles, A et B, ont été évalués avec des quantités croissantes de données. **A** : entraînement 0,99 / 0,97 / 0,94 / 0,92 ; validation 0,70 / 0,76 / 0,80 / 0,82 (pour 100, 300, 1 000 et 3 000 clients). **B** : entraînement 0,76 / 0,75 / 0,74 / 0,74 ; validation 0,70 / 0,72 / 0,73 / 0,73. Posez un diagnostic pour chacun (biais ou variance), dites si collecter des données aiderait, et proposez deux actions pour chaque modèle.

### Exercice 1.9 ⭐⭐ — Le test $t$ corrigé (section 1.4.2)

Sur $J=10$ découpages (800 observations d'entraînement et 200 de validation), les écarts d'exactitude entre deux modèles valent, en points de pourcentage : $2;\ 4;\ 3;\ 5;\ 1;\ 3;\ 4;\ 2;\ 3;\ 3$. Calculez la statistique $t$ naïve, la statistique corrigée, et l'intervalle de confiance à 95 % corrigé (on donne $t_{0{,}975;\,9}=2{,}262$).

### Exercice 1.10 ⭐⭐ — McNemar (section 1.4.2)

Deux classifieurs sont comparés sur 500 clients. Ils divergent sur 35 d'entre eux : A a raison et B tort pour 25 clients, A tort et B raison pour 10. Calculez la statistique de McNemar avec correction de continuité et la probabilité critique. La différence est-elle significative à 5 % ? à 1 % ?

### Exercice 1.11 ⭐⭐ — Combien d'essais aléatoires ? (section 1.5.2)

Une zone de réglages « excellents » occupe 2 % de l'espace de recherche. (a) Quelle est la probabilité d'en toucher au moins un avec 50 tirages aléatoires ? (b) Combien de tirages pour 90 % ? (c) Une grille à 5 valeurs pour 4 hyperparamètres compte combien de points ? Si seuls 2 hyperparamètres comptent, combien de valeurs distinctes chacun reçoit-il dans la grille ? et dans 50 tirages aléatoires ?

### Exercice 1.12 ⭐⭐⭐ — L'optimisme du maximum (section 1.5.5)

On évalue 100 modèles **sans aucune compétence** (scores aléatoires) sur un jeu de validation de 200 clients dont 28 sont partis. (a) Estimez par simulation l'AUC espérée du meilleur des 100. (b) Que vaut alors l'AUC « annoncée » du modèle sélectionné, et celle qu'il aura sur de nouvelles données ? (c) Reliez ce résultat à la validation imbriquée.

## Corrigés

### Corrigé 1.1

*Exactitude* : prédictions à 0,5 : $(1,0,1,0,0)$ contre $y=(1,0,0,1,0)$ : justes pour les clients 1, 2 et 5, donc $3/5=0{,}6$.
*Perte logarithmique* : les termes $-\ln$(probabilité attribuée au réel) valent $0{,}223$ ; $0{,}357$ ; $0{,}916$ ; $0{,}916$ ; $0{,}105$, de somme $2{,}518$, soit $2{,}518/5=0{,}504$.
*Brier* : $(0{,}04+0{,}09+0{,}36+0{,}36+0{,}01)/5=0{,}172$.
*AUC* : positifs (0,8 ; 0,4), négatifs (0,3 ; 0,6 ; 0,1) : 6 paires. 0,8 bat les trois négatifs (3) ; 0,4 bat 0,3 et 0,1 mais pas 0,6 (2) : $5/6\approx0{,}833$.

```python
from sklearn.metrics import log_loss, brier_score_loss
yy, pp = np.array([1, 0, 0, 1, 0]), np.array([0.8, 0.3, 0.6, 0.4, 0.1])
print((pp > 0.5).astype(int).tolist(), round(((pp > 0.5) == yy).mean(), 3), round(log_loss(yy, pp), 4), round(brier_score_loss(yy, pp), 4), round(roc_auc_score(yy, pp), 4))
```
<!--sortie-->
```text
[1, 0, 1, 0, 0] 0.6 0.5036 0.172 0.8333
```

### Corrigé 1.2

Modèle A : exactitude $=98\,\%$ (il ne se trompe que sur les fraudes), mais il ne détecte **aucune** fraude : il est inutile. Modèle B : exactitude $=0{,}02\times0{,}60+0{,}98\times0{,}97=0{,}012+0{,}9506=96{,}3\,\%$, **inférieure** à celle de A, alors qu'il détecte 60 % des fraudes. L'exactitude classe mal ces deux modèles. On choisit plutôt le **rappel** (part des fraudes détectées), la **précision** (part des alertes justifiées) et surtout le **coût** : coût d'une fraude manquée contre coût d'une fausse alerte. La précision de B vaut $\frac{0{,}012}{0{,}012+0{,}0294}\approx29\,\%$ : environ trois alertes sur dix sont de vraies fraudes.

### Corrigé 1.3

(a) **Oui** : calculée sur le passé. (b) **Non** : enregistré en février, donc après $t_0$ (fuite par la cible : un remboursement tardif est une conséquence du comportement futur). (c) **Oui** : l'enquête de novembre précède $t_0$. (d) **Non** : c'est la cible déguisée (compte clôturé au 31 mars). (e) **À éviter telle quelle** : une moyenne calculée sur *tous* les clients, y compris ceux du futur jeu de test, fait entrer de l'information du test dans l'apprentissage (contamination) ; elle doit être calculée **sur le jeu d'entraînement seulement**, à l'intérieur du pipeline. (f) **Prudence** : un numéro croissant encode la date d'inscription (ancienneté), ce qui peut être légitime, mais il n'a aucun sens causal et se dégrade si la numérotation change ; on préfère l'ancienneté explicite.

### Corrigé 1.4

Moyenne $\bar y=5$ ; erreur d'entraînement $\frac{(1-5)^2+(4-5)^2+(10-5)^2}3=\frac{16+1+25}3=14$. LOO : on retire 1, on prédit $\frac{4+10}2=7$, erreur $-6$ ; on retire 4, on prédit $\frac{1+10}2=5{,}5$, erreur $-1{,}5$ ; on retire 10, on prédit $\frac{1+4}2=2{,}5$, erreur $7{,}5$. Erreur LOO : $\frac{36+2{,}25+56{,}25}3=31{,}5$. Rapport : $31{,}5/14=2{,}25=(3/2)^2$ ✓.

```python
yv = np.array([1., 4., 10.])
loo = np.array([yv[i] - np.delete(yv, i).mean() for i in range(3)])
print(loo, (loo ** 2).mean(), ((yv - yv.mean()) ** 2).mean(), (loo ** 2).mean() / ((yv - yv.mean()) ** 2).mean())
```
<!--sortie-->
```text
[-6.  -1.5  7.5] 31.5 14.0 2.25
```

### Corrigé 1.5

(a) $23=5\times4+3$ : trois plis de 5 observations et deux de 4 (ou l'inverse, selon l'ordre) : tailles $(5,5,5,4,4)$. **5 modèles** sont entraînés ; à chaque essai l'entraînement compte $23-5=18$ ou $23-4=19$ observations. (b) $50/5=10$ clients par pli ; les 7 partis se répartissent aussi également que possible : deux plis en contiennent 2 et trois plis en contiennent 1.

```python
from sklearn.model_selection import KFold
print([len(v) for _, v in KFold(5).split(np.arange(23))])
yy50 = np.array([1] * 7 + [0] * 43)
print([int(yy50[v].sum()) for _, v in StratifiedKFold(5, shuffle=True, random_state=0).split(np.zeros(50), yy50)])
```
<!--sortie-->
```text
[5, 5, 5, 4, 4]
[2, 2, 1, 1, 1]
```

### Corrigé 1.6

La taille de validation est $12\,/\,(3+1)=3$. Essai 1 : entraînement $\{0,1,2\}$, validation $\{3,4,5\}$ ; essai 2 : entraînement $\{0,\dots,5\}$, validation $\{6,7,8\}$ ; essai 3 : entraînement $\{0,\dots,8\}$, validation $\{9,10,11\}$. Chaque validation est **postérieure** à l'entraînement, comme en production ; un tirage aléatoire de plis entraînerait sur des mois situés après ceux à prévoir (fuite temporelle, application 1.4).

```python
from sklearn.model_selection import TimeSeriesSplit
for tr, va in TimeSeriesSplit(3).split(np.arange(12)):
    print(tr.tolist(), va.tolist())
```
<!--sortie-->
```text
[0, 1, 2] [3, 4, 5]
[0, 1, 2, 3, 4, 5] [6, 7, 8]
[0, 1, 2, 3, 4, 5, 6, 7, 8] [9, 10, 11]
```

### Corrigé 1.7

$\mathbb E[c\bar y]=c\mu$, donc biais $=(c-1)\mu$ ; variance $c^2\sigma^2/n$ ; l'erreur quadratique est la somme du biais carré et de la variance : $(c-1)^2\mu^2+c^2\sigma^2/n$. Sa dérivée en $c$ vaut $2(c-1)\mu^2+2c\sigma^2/n$, qui s'annule pour $c^\star=\dfrac{\mu^2}{\mu^2+\sigma^2/n}$. Ici $\mu^2=9$ et $\sigma^2/n=1$ : $c^\star=0{,}9$. L'erreur minimale vaut $(0{,}1)^2\times9+0{,}81\times1=0{,}09+0{,}81=0{,}90$, contre $1$ pour $\bar y$ : un gain de 10 %.

```python
c = np.linspace(0.5, 1.2, 8); mu, s2, n = 3.0, 9.0, 9
print(np.round((c - 1) ** 2 * mu ** 2 + c ** 2 * s2 / n, 3), "| optimum", mu ** 2 / (mu ** 2 + s2 / n), "| erreur minimale", (0.9 - 1) ** 2 * 9 + 0.81)
```
<!--sortie-->
```text
[2.5 1.8 1.3 1.  0.9 1.  1.3 1.8] | optimum 0.9 | erreur minimale 0.9
```

### Corrigé 1.8

**A** : l'entraînement reste très supérieur à la validation (0,92 contre 0,82 à 3 000 clients), mais l'écart se **réduit** et la validation **monte encore** (0,70 → 0,82) : c'est la **variance**. Collecter des données aiderait. Actions : régulariser ou simplifier le modèle (profondeur, pénalité), moyenner plusieurs modèles (forêts). **B** : les deux courbes **se rejoignent** à un niveau bas (0,74 et 0,73) et plafonnent : c'est le **biais**. Plus de données n'aidera presque pas. Actions : un modèle plus souple (plus de profondeur, interactions), de meilleures variables (chapitre 4).

### Corrigé 1.9

Moyenne $\bar d=3$ ; écarts à la moyenne : $-1;1;0;2;-2;0;1;-1;0;0$, carrés de somme $12$, donc $s_d^2=12/9=1{,}333$. Naïf : $t=\dfrac3{\sqrt{1{,}333/10}}=\dfrac3{0{,}365}=8{,}2$. Facteur de correction $\frac1{10}+\frac{200}{800}=0{,}35$ : $t=\dfrac3{\sqrt{0{,}35\times1{,}333}}=\dfrac3{0{,}683}=4{,}4$. Erreur-type corrigée $0{,}683$ ; intervalle : $3\pm2{,}262\times0{,}683=3\pm1{,}55$, soit $[1{,}5\ ;\ 4{,}5]$ points : la différence est significative, mais deux fois moins nettement que ne le laissait croire le test naïf.

```python
d = np.array([2, 4, 3, 5, 1, 3, 4, 2, 3, 3], float)
tn = d.mean() / np.sqrt(d.var(ddof=1) / 10); tc = d.mean() / np.sqrt(0.35 * d.var(ddof=1)); se = np.sqrt(0.35 * d.var(ddof=1))
print(round(tn, 2), round(tc, 2), round(d.mean() - 2.262 * se, 2), round(d.mean() + 2.262 * se, 2))
```
<!--sortie-->
```text
8.22 4.39 1.45 4.55
```

### Corrigé 1.10

$\chi^2=\dfrac{(|25-10|-1)^2}{35}=\dfrac{14^2}{35}=\dfrac{196}{35}=5{,}6$ (1 degré de liberté), soit une probabilité critique de $0{,}018$ : significatif à 5 %, **non significatif à 1 %**. (Le test exact, binomial de paramètre $1/2$ sur 35 désaccords, donne une valeur voisine.)

```python
from scipy import stats
print(round((abs(25 - 10) - 1) ** 2 / 35, 2), round(stats.chi2.sf(5.6, 1), 4), round(stats.binomtest(10, 35, 0.5).pvalue, 4))
```
<!--sortie-->
```text
5.6 0.018 0.0167
```

### Corrigé 1.11

(a) $1-0{,}98^{50}=1-0{,}364=0{,}636$. (b) $n\ge\dfrac{\ln0{,}1}{\ln0{,}98}\approx114$ tirages. (c) $5^4=625$ points de grille. Si seuls 2 hyperparamètres comptent, chacun ne reçoit que **5 valeurs distinctes** dans la grille (les 625 points ne font que 25 combinaisons utiles, répétées 25 fois), alors que 50 tirages aléatoires lui en donnent **50 valeurs distinctes** : c'est l'argument de Bergstra et Bengio.

```python
print(round(1 - 0.98 ** 50, 3), int(np.ceil(np.log(0.1) / np.log(0.98))), 5 ** 4)
```
<!--sortie-->
```text
0.636 114 625
```

### Corrigé 1.12

On simule 100 scorers aléatoires sur 200 clients (28 partis) et on retient le meilleur ; on répète 300 fois.

```python
rng = np.random.default_rng(0)
yv = np.array([1] * 28 + [0] * 172)
maxima = [max(roc_auc_score(yv, rng.random(200)) for _ in range(100)) for _ in range(300)]
print("AUC du meilleur des 100 : moyenne", np.mean(maxima).round(3), "| 5e-95e centiles", np.percentile(maxima, [5, 95]).round(3))
```
<!--sortie-->
```text
AUC du meilleur des 100 : moyenne 0.647 | 5e-95e centiles [0.614 0.688]
```

(a) Le meilleur de 100 modèles sans compétence obtient en moyenne une AUC voisine de **0,65** (de 0,61 à 0,69 pour 90 % des répétitions), alors que chacun vaut 0,5 en espérance : l'écart-type d'une AUC mesurée sur 28 positifs et 172 négatifs est $\sqrt{201/(12\times28\times172)}\approx0{,}06$, et le maximum de 100 variables presque normales dépasse leur moyenne d'environ 2,5 écarts-types, soit $0{,}5+2{,}5\times0{,}06\approx0{,}65$. (b) L'AUC **annoncée** par la validation est donc environ 0,65 ; sur de nouvelles données, le modèle sélectionné retombe à **0,5**. (c) La validation imbriquée évalue la *procédure* « essayer 100 modèles, retenir le meilleur » sur des clients que la sélection n'a pas vus ; elle donne 0,5, ce qui est la vérité.
