# Chapitre 4 : Ingénierie des variables et données déséquilibrées — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 4 du livre. Les **applications** reprennent, pas à pas, ce que le livre n'a fait que résumer : un pipeline complet, l'encodage par la cible écrit à la main, la comparaison de stratégies pour les valeurs manquantes, la création de variables, les stratégies pour classes rares, la sélection de variables et SMOTE. Les **exercices** (à la main d'abord, puis avec du code) sont corrigés à la fin. Données : `clients_ml.csv` (le départ des clients, 14 %) et `transactions.csv` (la fraude, 0,8 %). Prérequis : les sections 4.1 à 4.5 du livre, selon l'exercice.

## Préparation

Une seule cellule charge les données et refait le découpage du livre (75 % / 25 %, stratifié, graine 0) ; les applications s'en servent.

```python
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split, cross_val_score, cross_validate, StratifiedKFold, cross_val_predict
from sklearn.metrics import roc_auc_score, average_precision_score, precision_score, recall_score, f1_score
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.preprocessing import StandardScaler
from sklearn.impute import SimpleImputer
from sklearn.pipeline import make_pipeline

clients = pd.read_csv("donnees/clients_ml.csv")
y = clients["churn_90j"]
tr, te = train_test_split(clients.index, test_size=0.25, random_state=0, stratify=y)
ytr, yte = y[tr], y[te]
NUM = ["age", "anciennete_mois", "nb_commandes_12m", "montant_12m", "recence_jours", "nb_retours_12m",
       "nb_tickets_support_12m", "programme_fidelite", "nb_promos_recues_12m", "part_achats_promo",
       "taux_ouverture_email", "satisfaction_moy", "delai_livraison_moy", "panier_moyen"]
QUAL = ["ville", "canal_acquisition", "appareil", "categorie_preferee"]

trans = pd.read_csv("donnees/transactions.csv")
Xt = pd.get_dummies(trans.drop(columns=["id_commande", "fraude", "type_fraude"]), dtype=float)
yt = trans["fraude"]
Xa, Xb, ya, yb = train_test_split(Xt, yt, test_size=0.3, random_state=0, stratify=yt)
print(len(clients), "clients, part de départs", round(y.mean(), 3), "|", len(trans), "commandes, part de fraudes", round(yt.mean(), 4))
```
<!--sortie-->
```text
12000 clients, part de départs 0.14 | 60000 commandes, part de fraudes 0.0081
```

## Applications

### Application 4.1 — Un pipeline complet, pas à pas (sections 4.1.6)

**Objectif.** Construire un modèle de départ de clients qui prend la table **brute** en entrée et refait tout son prétraitement lui-même, puis l'utiliser sur un nouveau client.

**Étape 1 : quelles colonnes de quel type ?** Quatorze variables numériques (dont quatre avec des valeurs manquantes) et quatre qualitatives.

```python
print("valeurs manquantes par variable numérique :")
print(clients[NUM].isna().sum()[lambda s: s > 0].to_dict())
print("modalités par variable qualitative :", clients[QUAL].nunique().to_dict())
```
<!--sortie-->
```text
valeurs manquantes par variable numérique :
{'satisfaction_moy': 1533, 'delai_livraison_moy': 1434, 'panier_moyen': 1630}
modalités par variable qualitative : {'ville': 20, 'canal_acquisition': 3, 'appareil': 3, 'categorie_preferee': 4}
```

**Étape 2 : le prétraitement.** Pour les numériques : imputation par la médiane avec indicateurs d'absence, puis standardisation. Pour les qualitatives : imputation par la modalité la plus fréquente, puis *one-hot*.

```python
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder

numeriques = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler())
categories = make_pipeline(SimpleImputer(strategy="most_frequent"), OneHotEncoder(handle_unknown="ignore"))
prep = ColumnTransformer([("num", numeriques, NUM), ("cat", categories, QUAL)])
modele = make_pipeline(prep, LogisticRegression(max_iter=3000))
cv = cross_val_score(modele, clients.loc[tr], ytr, cv=5, scoring="roc_auc")
print(f"validation croisée : AUC {cv.mean():.3f} (± {cv.std():.3f})")
```
<!--sortie-->
```text
validation croisée : AUC 0.860 (± 0.013)
```

**Étape 3 : qu'a produit le prétraitement ?** On ajuste sur tout l'entraînement et on regarde les colonnes créées.

```python
modele.fit(clients.loc[tr], ytr)
noms = modele[:-1].get_feature_names_out()
print(len(noms), "colonnes en entrée du modèle :", sum(n.startswith("num__") for n in noms), "numériques (dont indicateurs),",
      sum(n.startswith("cat__") for n in noms), "issues de l'encodage disjonctif")
print("exemples :", list(noms[:3]), "...", list(noms[-3:]))
print(f"AUC test : {roc_auc_score(yte, modele.predict_proba(clients.loc[te])[:, 1]):.3f}")
```
<!--sortie-->
```text
47 colonnes en entrée du modèle : 17 numériques (dont indicateurs), 30 issues de l'encodage disjonctif
exemples : ['num__age', 'num__anciennete_mois', 'num__nb_commandes_12m'] ... ['cat__categorie_preferee_B', 'cat__categorie_preferee_C', 'cat__categorie_preferee_D']
AUC test : 0.866
```

**Étape 4 : le même problème avec un boosting.** Un boosting ne demande ni mise à l'échelle ni imputation, et sait traiter des modalités directement si on lui déclare les colonnes qualitatives (type `category`).

```python
brut = clients[NUM + QUAL].copy()
for col in QUAL:
    brut[col] = brut[col].astype("category")
gb = HistGradientBoostingClassifier(random_state=0, max_iter=100, categorical_features="from_dtype").fit(brut.loc[tr], ytr)
print(f"boosting sans aucun prétraitement : AUC test {roc_auc_score(yte, gb.predict_proba(brut.loc[te])[:, 1]):.3f}")
```
<!--sortie-->
```text
boosting sans aucun prétraitement : AUC test 0.900
```

**Étape 5 : un seul objet pour la production.** Le pipeline accepte une ligne brute, avec ses valeurs manquantes.

```python
nouveau = pd.DataFrame([{"age": 33, "anciennete_mois": 20, "nb_commandes_12m": 1, "montant_12m": 40.0, "recence_jours": 210,
                         "nb_retours_12m": 0, "nb_tickets_support_12m": 3, "programme_fidelite": 0, "nb_promos_recues_12m": 5,
                         "part_achats_promo": 0.7, "taux_ouverture_email": 0.1, "satisfaction_moy": np.nan, "delai_livraison_moy": 4.0,
                         "panier_moyen": 40.0, "ville": "Ville C", "canal_acquisition": "Réseaux", "appareil": np.nan,
                         "categorie_preferee": "B"}])
print("probabilité de départ du nouveau client :", round(float(modele.predict_proba(nouveau)[0, 1]), 3))
```
<!--sortie-->
```text
probabilité de départ du nouveau client : 0.367
```

**Pour aller plus loin.** Remplacez `OneHotEncoder` par l'encodage de la fréquence puis comparez les deux pipelines en validation croisée : l'écart dépasse-t-il l'écart-type d'un pli à l'autre ?

### Application 4.2 — L'encodage par la cible, hors pli, écrit à la main (section 4.1.2)

**Objectif.** Écrire les trois variantes de l'encodage par la cible et mesurer leur fuite sur une variable **de pur bruit**, un code postal à 400 modalités tiré au hasard.

**Étape 1 : la variable de bruit.**

```python
rng = np.random.default_rng(4)
code_postal = pd.Series(rng.integers(0, 400, len(clients)), index=clients.index)
print("clients par code (entraînement), en moyenne :", round(len(tr) / 400, 1))
```
<!--sortie-->
```text
clients par code (entraînement), en moyenne : 22.5
```

**Étape 2 : l'encodage naïf et l'encodage lissé.** Le lissage $\frac{n_m\bar y_m+k\mu}{n_m+k}$ rapproche les petites modalités de la moyenne générale.

```python
def encodage_naif(col_tr, y_tr, col_te, k=0):
    mu = y_tr.mean()
    g = y_tr.groupby(col_tr).agg(["sum", "count"])
    moy = (g["sum"] + k * mu) / (g["count"] + k)
    return col_tr.map(moy), col_te.map(moy).fillna(mu)

for k in (0, 20):
    a, b = encodage_naif(code_postal[tr], ytr, code_postal[te], k)
    print(f"lissage k = {k:2d} : AUC entraînement {roc_auc_score(ytr, a):.3f} | AUC test {roc_auc_score(yte, b):.3f}")
```
<!--sortie-->
```text
lissage k =  0 : AUC entraînement 0.678 | AUC test 0.510
lissage k = 20 : AUC entraînement 0.678 | AUC test 0.510
```

**Étape 3 : le calcul hors pli.** Les lignes du pli $j$ sont encodées avec les statistiques des autres plis.

```python
from sklearn.model_selection import KFold

def encodage_hors_pli(col_tr, y_tr, plis=5, graine=0):
    sortie = pd.Series(index=col_tr.index, dtype=float)
    for i, j in KFold(plis, shuffle=True, random_state=graine).split(col_tr):
        moy = y_tr.iloc[i].groupby(col_tr.iloc[i]).mean()
        sortie.iloc[j] = col_tr.iloc[j].map(moy).fillna(y_tr.iloc[i].mean()).values
    return sortie

oof = encodage_hors_pli(code_postal[tr], ytr)
print("hors pli, AUC entraînement :", round(roc_auc_score(ytr, oof), 3))
```
<!--sortie-->
```text
hors pli, AUC entraînement : 0.509
```

**Étape 4 : le piège du « leave-one-out ».** On retire seulement la ligne courante. Dans une même modalité, la valeur encodée dépend alors de **sa propre étiquette** : on le vérifie sur la vraie ville.

```python
ville = clients.loc[tr, "ville"]
somme, effectif = ytr.groupby(ville).transform("sum"), ytr.groupby(ville).transform("count")
loo = (somme - ytr) / (effectif - 1)
centre = loo - loo.groupby(ville).transform("mean")           # on retire l'effet de la ville : il reste l'écart intra-ville
print("écart intra-ville moyen, clients PARTIS :", round(centre[ytr == 1].mean(), 4))
print("écart intra-ville moyen, clients RESTÉS :", round(centre[ytr == 0].mean(), 4))
print("AUC de -(encodage LOO centré) pour retrouver la cible :", round(roc_auc_score(ytr, -centre), 3))
```
<!--sortie-->
```text
écart intra-ville moyen, clients PARTIS : -0.0018
écart intra-ville moyen, clients RESTÉS : 0.0003
AUC de -(encodage LOO centré) pour retrouver la cible : 1.0
```

**Lecture.** Le calcul naïf, même lissé (les deux lignes sont identiques : le lissage atténue les valeurs extrêmes mais ne supprime pas la fuite), donne une AUC d'entraînement de 0,678 pour une variable sans aucun lien avec la cible, qui retombe à 0,510 sur le test. Le calcul hors pli ne fuit pas (0,509). Le *leave-one-out* fuit **à l'envers** : dans une même ville, un client parti reçoit une valeur plus *basse* qu'un client resté, puisqu'on lui a retiré sa propre étiquette. Une fois l'effet de la ville retiré, cet écart est **exact** et sépare parfaitement les deux groupes : un arbre peut en tirer parti pour retrouver la cible.

### Application 4.3 — Valeurs manquantes : quand l'indicateur d'absence compte (section 4.1.5)

**Objectif.** Comparer des stratégies d'imputation en validation croisée, puis mesurer comment l'intérêt de l'indicateur d'absence évolue avec la force du lien entre absence et cible.

**Étape 1 : six stratégies, avec leur incertitude.**

```python
from sklearn.experimental import enable_iterative_imputer
from sklearn.impute import KNNImputer, IterativeImputer

strategies = {"moyenne": SimpleImputer(strategy="mean"), "médiane": SimpleImputer(strategy="median"),
              "médiane + indicateurs": SimpleImputer(strategy="median", add_indicator=True),
              "kNN (k = 5)": KNNImputer(n_neighbors=5), "itérative": IterativeImputer(random_state=0, max_iter=5)}
cv = StratifiedKFold(5, shuffle=True, random_state=0)
for nom, imp in strategies.items():
    m = make_pipeline(imp, StandardScaler(), LogisticRegression(max_iter=3000))
    s = cross_val_score(m, clients.loc[tr, NUM], ytr, cv=cv, scoring="roc_auc")
    print(f"{nom:24s} AUC {s.mean():.3f} (± {s.std():.3f})")
```
<!--sortie-->
```text
moyenne                  AUC 0.857 (± 0.009)
médiane                  AUC 0.856 (± 0.009)
médiane + indicateurs    AUC 0.857 (± 0.009)
kNN (k = 5)              AUC 0.855 (± 0.010)
itérative                AUC 0.855 (± 0.009)
```

**Étape 2 : le cas simulé, avec une force de lien variable.** La variable $x$ est liée à la cible ; elle est manquante avec une probabilité $q_1$ pour les départs et $q_0=0{,}10$ pour les autres.

```python
def auc_selon_absence(q1, graine=11, n=6000):
    r = np.random.default_rng(graine)
    x = r.normal(size=n)
    yy = r.binomial(1, 1 / (1 + np.exp(-(-1.5 + 0.8 * x))))
    manquant = r.random(n) < np.where(yy == 1, q1, 0.10)
    X = pd.DataFrame({"x": np.where(manquant, np.nan, x)})
    a, b, ya_, yb_ = train_test_split(X, yy, test_size=0.3, random_state=0, stratify=yy)
    sortie = []
    for ind in (False, True):
        m = make_pipeline(SimpleImputer(strategy="mean", add_indicator=ind), LogisticRegression()).fit(a, ya_)
        sortie.append(roc_auc_score(yb_, m.predict_proba(b)[:, 1]))
    return sortie

for q1 in (0.10, 0.25, 0.40, 0.55, 0.70):
    sans, avec = auc_selon_absence(q1)
    print(f"absence chez les départs {q1:.2f} : AUC sans indicateur {sans:.3f}, avec indicateur {avec:.3f}")
```
<!--sortie-->
```text
absence chez les départs 0.10 : AUC sans indicateur 0.714, avec indicateur 0.715
absence chez les départs 0.25 : AUC sans indicateur 0.688, avec indicateur 0.732
absence chez les départs 0.40 : AUC sans indicateur 0.644, avec indicateur 0.778
absence chez les départs 0.55 : AUC sans indicateur 0.610, avec indicateur 0.819
absence chez les départs 0.70 : AUC sans indicateur 0.569, avec indicateur 0.864
```

**Lecture.** Dans les vraies données, toutes les stratégies sont indiscernables. Dans la simulation, l'écart entre « sans » et « avec » indicateur **croît avec le lien entre absence et cible**, et il est nul quand l'absence est aléatoire ($q_1=0{,}10$, comme chez les autres). L'indicateur ne coûte presque rien : ajoutez-le dès que vous doutez.

### Application 4.4 — Créer des variables RFM et mesurer leur apport (section 4.2)

**Objectif.** Fabriquer des variables métier, découvrir des seuils sur l'entraînement, et vérifier par permutation que les nouvelles variables servent vraiment.

**Étape 1 : variables génériques et profils RFM.**

```python
def fabriquer(df):
    f = df[NUM].copy()
    f["frequence_mensuelle"] = df["nb_commandes_12m"] / np.minimum(df["anciennete_mois"], 12)
    f["taux_retour"] = (df["nb_retours_12m"] / df["nb_commandes_12m"].replace(0, np.nan)).fillna(0)
    f["tickets_par_commande"] = df["nb_tickets_support_12m"] / (df["nb_commandes_12m"] + 1)
    f["jamais_commande"] = (df["nb_commandes_12m"] == 0).astype(int)
    f["log_recence"] = np.log1p(df["recence_jours"])
    return f

F = fabriquer(clients)
print(F[["frequence_mensuelle", "taux_retour", "tickets_par_commande"]].describe().loc[["mean", "50%", "max"]].round(2))
```
<!--sortie-->
```text
      frequence_mensuelle  taux_retour  tickets_par_commande
mean                 0.37         0.07                  0.22
50%                  0.25         0.00                  0.00
max                 12.00         1.00                  8.00
```

**Étape 2 : des classes de récence, avec des bornes lues sur l'entraînement.** On coupe la récence en quintiles **de l'entraînement** et on applique les mêmes bornes au test.

```python
bornes = clients.loc[tr, "recence_jours"].quantile([0.2, 0.4, 0.6, 0.8]).values
F["classe_recence"] = np.digitize(clients["recence_jours"], bornes)
print("bornes (jours) :", bornes.round(0))
print(clients.loc[tr].assign(classe=F.loc[tr, "classe_recence"]).groupby("classe")["churn_90j"].mean().round(3).to_dict())
```
<!--sortie-->
```text
bornes (jours) : [ 15.  38.  76. 203.]
{0: 0.062, 1: 0.055, 2: 0.079, 3: 0.137, 4: 0.367}
```

**Étape 3 : les règles découvertes.** Les seuils (160 jours, satisfaction 3,15, promotions 0,60) viennent d'un arbre de profondeur 3 ajusté sur l'entraînement (livre, 4.2.2).

```python
F["inactif_et_mecontent"] = ((clients["recence_jours"] > 160) & (clients["satisfaction_moy"] < 3.15)).astype(int)
F["promo_sans_fidelite"] = ((clients["part_achats_promo"] > 0.60) & (clients["programme_fidelite"] == 0)).astype(int)
brutes, riches = NUM, [c for c in F.columns if c != "classe_recence"]
for nom, cols in [("14 variables brutes", brutes), ("variables enrichies", riches)]:
    m = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(), LogisticRegression(max_iter=3000))
    m.fit(F.loc[tr, cols], ytr)
    print(f"{nom:22s} ({len(cols):2d} colonnes) AUC test {roc_auc_score(yte, m.predict_proba(F.loc[te, cols])[:, 1]):.3f}")
```
<!--sortie-->
```text
14 variables brutes    (14 colonnes) AUC test 0.858
variables enrichies    (21 colonnes) AUC test 0.886
```

**Étape 4 : les nouvelles variables servent-elles ?** Importance par permutation, sur une partie de l'entraînement mise de côté.

```python
from sklearn.inspection import permutation_importance

a_in, a_val, y_in, y_val = train_test_split(F.loc[tr, riches], ytr, test_size=0.3, random_state=0, stratify=ytr)
m = make_pipeline(SimpleImputer(strategy="median", add_indicator=True), StandardScaler(), LogisticRegression(max_iter=3000)).fit(a_in, y_in)
perm = permutation_importance(m, a_val, y_val, scoring="roc_auc", n_repeats=5, random_state=0, n_jobs=1)
top = pd.Series(perm.importances_mean, index=riches).sort_values(ascending=False).head(6)
print(top.round(4).to_string())
```
<!--sortie-->
```text
age                     0.0596
nb_commandes_12m        0.0560
promo_sans_fidelite     0.0516
inactif_et_mecontent    0.0416
recence_jours           0.0214
panier_moyen            0.0028
```

**Lecture.** Les variables enrichies font passer l'AUC de 0,858 à 0,886 (la version complète du livre, avec une règle de plus et deux variables supplémentaires, atteint 0,900). L'importance par permutation montre que les **indicateurs de règles** servent vraiment : `promo_sans_fidelite` (0,052) et `inactif_et_mecontent` (0,042) sont dans les quatre premières, devant la récence brute (0,021). L'âge arrive en tête (0,060) : une relation en U, que la régression logistique doit se contenter d'approcher par une droite.

### Application 4.5 — Toutes les stratégies pour classes rares, sur la fraude (sections 4.3.1 à 4.3.3)

**Objectif.** Comparer sur les mêmes plis la régression logistique et le boosting avec : rien, poids équilibrés, sous- et sur-échantillonnage, en rapportant la PR-AUC avec son écart-type. Le rééchantillonnage est **dans le pipeline**.

```python
from imblearn.pipeline import Pipeline as PipeIB
from imblearn.over_sampling import RandomOverSampler
from imblearn.under_sampling import RandomUnderSampler

cv = StratifiedKFold(5, shuffle=True, random_state=0)
lg = lambda **k: LogisticRegression(max_iter=3000, **k)
gb = lambda **k: HistGradientBoostingClassifier(random_state=0, max_iter=100, **k)
modeles = {
    "logistique": PipeIB([("sc", StandardScaler()), ("m", lg())]),
    "logistique + poids": PipeIB([("sc", StandardScaler()), ("m", lg(class_weight="balanced"))]),
    "logistique + sous-éch. (1:5)": PipeIB([("sc", StandardScaler()), ("u", RandomUnderSampler(sampling_strategy=0.2, random_state=0)), ("m", lg())]),
    "boosting": PipeIB([("m", gb())]),
    "boosting + poids": PipeIB([("m", gb(class_weight="balanced"))]),
}
for nom, mod in modeles.items():
    r = cross_validate(mod, Xa, ya, cv=cv, scoring={"auc": "roc_auc", "ap": "average_precision"})
    print(f"{nom:30s} AUC {r['test_auc'].mean():.3f} (± {r['test_auc'].std():.3f}) | PR-AUC {r['test_ap'].mean():.3f} (± {r['test_ap'].std():.3f})")
```
<!--sortie-->
```text
logistique                     AUC 0.907 (± 0.019) | PR-AUC 0.280 (± 0.059)
logistique + poids             AUC 0.910 (± 0.018) | PR-AUC 0.219 (± 0.041)
logistique + sous-éch. (1:5)   AUC 0.910 (± 0.017) | PR-AUC 0.255 (± 0.040)
boosting                       AUC 0.950 (± 0.010) | PR-AUC 0.575 (± 0.040)
boosting + poids               AUC 0.966 (± 0.013) | PR-AUC 0.544 (± 0.072)
```

**Lecture.** Le classement des modèles est stable (le boosting domine la régression logistique de très loin : PR-AUC de 0,54 à 0,58 contre 0,22 à 0,28). Les **traitements** de déséquilibre n'améliorent pas la PR-AUC ; ils la dégradent même un peu (de 0,03 à 0,06), un écart du même ordre que l'écart-type entre plis (0,04 à 0,07). L'AUC-ROC, elle, reste stable ou monte (0,950 à 0,966 pour le boosting). Pour trancher entre deux traitements proches, il faut un **test apparié** ou un *bootstrap* (livre, 4.3.6).

### Application 4.6 — Choisir un seuil par les coûts (section 4.3.5)

**Objectif.** Pour trois rapports de coûts, calculer le seuil théorique $s^\star=\frac{c_{FP}}{c_{FP}+c_{FN}}$, le comparer au seuil optimal empirique trouvé sur des prédictions **hors pli**, puis évaluer le coût sur le test.

**Étape 1 : prédictions hors pli et modèle final.**

```python
modele = HistGradientBoostingClassifier(random_state=0, max_iter=100)
oof = cross_val_predict(modele, Xa, ya, cv=StratifiedKFold(5, shuffle=True, random_state=0), method="predict_proba")[:, 1]
p_test = modele.fit(Xa, ya).predict_proba(Xb)[:, 1]
```

**Étape 2 : une fonction de coût et trois scénarios.**

```python
def cout(p, vrai, s, c_fn, c_fp):
    bloque = p >= s
    return int(((~bloque) & (vrai == 1)).sum() * c_fn + (bloque & (vrai == 0)).sum() * c_fp)

grille = np.linspace(0.005, 0.95, 190)
for c_fn, c_fp in [(10, 5), (100, 5), (500, 5)]:
    s_theo = c_fp / (c_fp + c_fn)
    s_emp = grille[int(np.argmin([cout(oof, ya.values, s, c_fn, c_fp) for s in grille]))]
    print(f"c_FN = {c_fn:3d}, c_FP = {c_fp} : seuil théorique {s_theo:.3f} | seuil hors pli {s_emp:.3f} | coût test à 0,5 : "
          f"{cout(p_test, yb.values, 0.5, c_fn, c_fp):6d} | au seuil théorique : {cout(p_test, yb.values, s_theo, c_fn, c_fp):6d} | au seuil hors pli : {cout(p_test, yb.values, s_emp, c_fn, c_fp):6d}")
```
<!--sortie-->
```text
c_FN =  10, c_FP = 5 : seuil théorique 0.333 | seuil hors pli 0.515 | coût test à 0,5 :    855 | au seuil théorique :    860 | au seuil hors pli :    855
c_FN = 100, c_FP = 5 : seuil théorique 0.048 | seuil hors pli 0.025 | coût test à 0,5 :   7155 | au seuil théorique :   5575 | au seuil hors pli :   5420
c_FN = 500, c_FP = 5 : seuil théorique 0.010 | seuil hors pli 0.005 | coût test à 0,5 :  35155 | au seuil théorique :  16495 | au seuil hors pli :  14865
```

**Lecture.** Plus la fraude coûte cher par rapport à une fausse alerte, plus le seuil optimal descend et plus le seuil de 0,5 est coûteux : de 855 € (rapport 2) à 35 155 € (rapport 100), contre 16 495 € au seuil théorique et 14 865 € au seuil hors pli. Les deux seuils calculés donnent des **coûts voisins** (860 contre 855 ; 5 575 contre 5 420 ; 16 495 contre 14 865) même quand ils diffèrent (0,333 contre 0,515 dans le premier scénario, où le modèle est si confiant que beaucoup de seuils se valent) : tant que les probabilités du modèle sont à peu près calibrées, la formule suffit.

### Application 4.7 — Sélection de variables : trois familles et un piège (section 4.4)

**Objectif.** Comparer filtre, enveloppe et méthode intégrée sur les clients enrichis de variables de bruit, puis mesurer comment le biais de sélection dépend du nombre de variables et de clients.

**Étape 1 : les clients, plus cinq variables de bruit.**

```python
from sklearn.feature_selection import mutual_info_classif, RFE

rng = np.random.default_rng(5)
Xs = clients[NUM].copy()
for k in range(3):
    Xs[f"bruit_continu_{k + 1}"] = rng.normal(size=len(Xs))
for k in range(2):
    Xs[f"bruit_discret_{k + 1}"] = rng.integers(0, 12, len(Xs))
A = pd.DataFrame(SimpleImputer(strategy="median").fit_transform(Xs.loc[tr]), columns=Xs.columns, index=tr)
As = pd.DataFrame(StandardScaler().fit_transform(A), columns=A.columns, index=tr)
bruits = [c for c in A.columns if c.startswith("bruit")]
```

**Étape 2 : trois sélections de 8 variables.**

```python
mi = pd.Series(mutual_info_classif(A, ytr, random_state=0), index=A.columns).sort_values(ascending=False)
sel_mi = list(mi.index[:8])
sel_rfe = list(As.columns[RFE(LogisticRegression(max_iter=3000), n_features_to_select=8).fit(As, ytr).support_])
l1 = LogisticRegression(penalty="l1", solver="liblinear", C=0.05, max_iter=5000).fit(As, ytr)
sel_l1 = list(As.columns[l1.coef_[0] != 0])
for nom, sel in [("information mutuelle", sel_mi), ("RFE", sel_rfe), ("pénalité L1", sel_l1)]:
    print(f"{nom:22s} {len(sel):2d} variables, bruit retenu : {[v for v in sel if v in bruits]}")
```
<!--sortie-->
```text
information mutuelle    8 variables, bruit retenu : []
RFE                     8 variables, bruit retenu : []
pénalité L1            14 variables, bruit retenu : ['bruit_continu_1', 'bruit_continu_2', 'bruit_discret_1']
```

**Étape 3 : le biais de sélection selon $p$ et $n$.** Cible aléatoire ; on sélectionne les 10 meilleures variables, avant ou dans la validation croisée.

```python
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline

def auc_biais(n, p, graines=15):
    avant, dans = [], []
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    for g in range(graines):
        r = np.random.default_rng(g)
        X, yy = r.normal(size=(n, p)), r.integers(0, 2, n)
        Xk = SelectKBest(f_classif, k=10).fit_transform(X, yy)
        avant.append(cross_val_score(LogisticRegression(max_iter=2000), Xk, yy, cv=cv, scoring="roc_auc").mean())
        pipe = Pipeline([("sel", SelectKBest(f_classif, k=10)), ("lr", LogisticRegression(max_iter=2000))])
        dans.append(cross_val_score(pipe, X, yy, cv=cv, scoring="roc_auc").mean())
    return np.mean(avant), np.mean(dans)

for n, p in [(150, 50), (150, 500), (150, 2000), (600, 500), (2000, 500)]:
    a, d = auc_biais(n, p)
    print(f"n = {n:4d}, p = {p:4d} : AUC sélection avant la validation {a:.3f} | dans la validation {d:.3f}")
```
<!--sortie-->
```text
n =  150, p =   50 : AUC sélection avant la validation 0.652 | dans la validation 0.481
n =  150, p =  500 : AUC sélection avant la validation 0.790 | dans la validation 0.474
n =  150, p = 2000 : AUC sélection avant la validation 0.836 | dans la validation 0.475
n =  600, p =  500 : AUC sélection avant la validation 0.656 | dans la validation 0.498
n = 2000, p =  500 : AUC sélection avant la validation 0.594 | dans la validation 0.503
```

**Lecture.** Le biais croît avec le nombre de variables candidates $p$ et décroît avec le nombre de clients $n$ : il est énorme quand $p\gg n$ (génomique, textes) et négligeable avec beaucoup de lignes. La sélection faite dans la validation est toujours honnête (autour de 0,5).

### Application 4.8 — SMOTE et variantes dans un pipeline (section 4.5)

**Objectif.** Comparer SMOTE, Borderline-SMOTE, ADASYN et SMOTE-NC dans un pipeline ; mesurer l'effet de $k$ ; refaire la fuite par rééchantillonnage.

**Étape 1 : le pipeline SMOTE avec le nombre de voisins.**

```python
from imblearn.over_sampling import SMOTE, BorderlineSMOTE, ADASYN

cv = StratifiedKFold(5, shuffle=True, random_state=0)
for k in (2, 5, 15):
    pipe = PipeIB([("sc", StandardScaler()), ("o", SMOTE(k_neighbors=k, random_state=0)), ("m", LogisticRegression(max_iter=3000))])
    s = cross_val_score(pipe, Xa, ya, cv=cv, scoring="average_precision")
    print(f"SMOTE, k = {k:2d} : PR-AUC {s.mean():.3f} (± {s.std():.3f})")
```
<!--sortie-->
```text
SMOTE, k =  2 : PR-AUC 0.220 (± 0.043)
SMOTE, k =  5 : PR-AUC 0.214 (± 0.039)
SMOTE, k = 15 : PR-AUC 0.215 (± 0.037)
```

**Étape 2 : trois variantes, avec boosting.**

```python
for nom, o in [("SMOTE", SMOTE(random_state=0)), ("Borderline-SMOTE", BorderlineSMOTE(random_state=0)), ("ADASYN", ADASYN(random_state=0))]:
    pipe = PipeIB([("o", o), ("m", HistGradientBoostingClassifier(random_state=0, max_iter=100))])
    s = cross_val_score(pipe, Xa, ya, cv=cv, scoring="average_precision")
    print(f"{nom:18s} + boosting : PR-AUC {s.mean():.3f} (± {s.std():.3f})")
```
<!--sortie-->
```text
SMOTE              + boosting : PR-AUC 0.500 (± 0.033)
Borderline-SMOTE   + boosting : PR-AUC 0.573 (± 0.043)
ADASYN             + boosting : PR-AUC 0.495 (± 0.038)
```

**Étape 3 : SMOTE-NC avec une variable qualitative.** On rend les départs rares (3 %) en gardant tous les clients restés et seulement une partie des partis, et on traite `ville` comme variable nominale.

```python
from imblearn.over_sampling import SMOTENC

rare = pd.concat([clients[clients.churn_90j == 0], clients[clients.churn_90j == 1].sample(frac=0.2, random_state=0)])
Xr = rare[["age", "recence_jours", "nb_commandes_12m", "montant_12m"]].copy()
Xr["ville_code"] = rare["ville"].astype("category").cat.codes
yr = rare["churn_90j"]
pipe = PipeIB([("o", SMOTENC(categorical_features=[4], random_state=0)), ("m", HistGradientBoostingClassifier(random_state=0, max_iter=100))])
s = cross_val_score(pipe, Xr, yr, cv=cv, scoring="average_precision")
s0 = cross_val_score(HistGradientBoostingClassifier(random_state=0, max_iter=100), Xr, yr, cv=cv, scoring="average_precision")
print("part de départs :", round(yr.mean(), 3))
print("SMOTE-NC + boosting  : PR-AUC", round(s.mean(), 3), "(± %.3f)" % s.std())
print("sans rééchantillonnage : PR-AUC", round(s0.mean(), 3), "(± %.3f)" % s0.std())
```
<!--sortie-->
```text
part de départs : 0.032
SMOTE-NC + boosting  : PR-AUC 0.207 (± 0.035)
sans rééchantillonnage : PR-AUC 0.187 (± 0.008)
```

**Étape 4 : la fuite.** Sur-échantillonner **avant** la validation croisée.

```python
Xo, yo = RandomOverSampler(random_state=0).fit_resample(Xr, yr)
fuite = cross_val_score(HistGradientBoostingClassifier(random_state=0, max_iter=100), Xo, yo, cv=cv, scoring="average_precision")
honnete = cross_val_score(HistGradientBoostingClassifier(random_state=0, max_iter=100), Xr, yr, cv=cv, scoring="average_precision")
print(f"PR-AUC avec fuite (rééchantillonnage avant la validation) : {fuite.mean():.3f} | sans rééchantillonnage : {honnete.mean():.3f}")
```
<!--sortie-->
```text
PR-AUC avec fuite (rééchantillonnage avant la validation) : 0.972 | sans rééchantillonnage : 0.187
```

**Lecture.** Avec la régression logistique, le nombre de voisins $k$ ne change rien (0,214 à 0,220). Avec le boosting, **Borderline-SMOTE (0,573) égale le boosting sans traitement (0,575)**, tandis que SMOTE (0,500) et ADASYN (0,495) le dégradent d'environ 0,08 : une explication plausible est qu'en ne fabriquant des points qu'à la frontière, Borderline modifie moins la zone centrale des classes (c'est une hypothèse, que ces données ne démontrent pas). SMOTE-NC obtient 0,207 contre 0,187 sans rééchantillonnage : un écart apparent, mais **plus petit que son écart-type entre plis (0,035)**, donc sans valeur probante. La fuite, elle, donne 0,972 contre 0,187 : un score absurde pour un problème difficile.

## Exercices

Les exercices sont rangés par difficulté (⭐ calcul direct, ⭐⭐ raisonnement, ⭐⭐⭐ synthèse ou expérience). Essayez-les **à la main d'abord** ; les corrigés suivent.

### Exercice 4.1 ⭐ — L'encodage par la cible, à la main (section 4.1.2)

Huit clients habitent trois villes. La cible vaut 1 si le client est parti : ville P, quatre clients : 1, 1, 0, 0 ; ville Q, trois clients : 1, 0, 0 ; ville R, un client : 1.

(a) Calculez l'encodage par la cible naïf de chaque ville, et la moyenne générale.
(b) Calculez l'encodage lissé avec $k=4$ : $\frac{n_m\bar y_m+k\mu}{n_m+k}$.
(c) Quelle ville est la plus suspecte, et pourquoi ?
(d) Quelle valeur attribuer à un client d'une ville S absente de l'entraînement ?

### Exercice 4.2 ⭐ — Mettre à l'échelle (section 4.1.3)

Cinq montants : 2, 4, 6, 8, 10.

(a) Standardisez-les (écart-type de la population).
(b) Appliquez le min-max, puis la transformation robuste (médiane, écart interquartile $Q_3-Q_1$ avec $Q_1=4$ et $Q_3=8$).
(c) Remplacez le dernier montant par 100. Quelles transformations changent pour les quatre premières valeurs ?

### Exercice 4.3 ⭐⭐ — Box-Cox et Yeo-Johnson (section 4.1.4)

(a) Appliquez la transformation de Box-Cox avec $\lambda=\frac12$ puis avec $\lambda=0$ aux valeurs 1, 4, 9, 16. Que remarquez-vous pour $\lambda=\frac12$ ?
(b) Calculez la transformation de Yeo-Johnson de $x=-3$ puis de $x=5$ pour $\lambda=1$. Que fait cette transformation pour $\lambda=1$ ?

### Exercice 4.4 ⭐⭐ — Mécanismes d'absence (section 4.1.5)

Pour chaque situation, donnez le mécanisme (MCAR, MAR, MNAR ou structurel) et le traitement que vous conseillez.

(a) Un capteur de température tombe en panne de temps en temps, sans rapport avec la température.
(b) Dans un questionnaire, les personnes aux revenus les plus élevés refusent plus souvent de déclarer leur revenu.
(c) La tension artérielle n'est mesurée que pour les patients de plus de 60 ans (l'âge est toujours renseigné).
(d) Le « panier moyen » est vide pour les clients qui n'ont jamais commandé.

### Exercice 4.5 ⭐⭐⭐ — Trouver les fuites (section 4.1.6)

Voici un script qui prétend évaluer un modèle de départ de clients :

```python
X = SimpleImputer(strategy="median").fit_transform(df.drop(columns="y"))
X = StandardScaler().fit_transform(X)
X = SelectKBest(f_classif, k=10).fit_transform(X, df["y"])
Xtr, Xte, ytr, yte = train_test_split(X, df["y"], stratify=df["y"], random_state=0)
Xtr, ytr = SMOTE(random_state=0).fit_resample(Xtr, ytr)
modele = LogisticRegression().fit(Xtr, ytr)
print(roc_auc_score(yte, modele.predict_proba(Xte)[:, 1]))
```

(a) Repérez les étapes qui fuient et celles qui sont correctes.
(b) Réécrivez le script avec un `Pipeline`.
(c) Mesurez l'écart sur des données de pur bruit (200 lignes, 100 variables, cible aléatoire).

### Exercice 4.6 ⭐ — Créer des variables (section 4.2.1)

Trois clients : A (4 commandes, 1 retour, 2 tickets, ancienneté 30 mois, 200 € sur 12 mois), B (aucune commande, ancienneté 8 mois) et C (10 commandes, 4 retours, 5 tickets, ancienneté 5 mois, 800 €). Calculez pour chacun : le taux de retour (0 s'il n'y a pas de commande), les tickets par commande $\frac{\text{tickets}}{\text{commandes}+1}$, la fréquence mensuelle $\frac{\text{commandes}}{\min(\text{ancienneté},12)}$ et le montant par commande. Pour quel client une variable est-elle indéfinie ?

### Exercice 4.7 ⭐⭐ — Coder une heure sur un cercle (section 4.2.4)

(a) Donnez les coordonnées $(\sin\frac{2\pi h}{24},\cos\frac{2\pi h}{24})$ pour $h=23$, $h=1$ et $h=12$.
(b) Calculez les distances euclidiennes entre 23 h et 1 h, puis entre 23 h et 12 h, et comparez avec les distances sur l'entier $h$.

### Exercice 4.8 ⭐⭐ — Variable disponible ou fuite ? (section 4.2.6)

On veut prédire, au 1er du mois, si un abonné **résiliera dans le mois**. Pour chaque variable, dites si elle est utilisable ou si elle constitue une fuite : (a) le nombre de tickets d'assistance des six mois précédents ; (b) la date de résiliation (vide si l'abonné reste) ; (c) le montant facturé pendant le mois ; (d) la note d'une enquête de satisfaction envoyée à la fin du mois ; (e) l'ancienneté au 1er du mois ; (f) un « segment client » calculé avec un modèle entraîné sur l'historique complet, y compris le mois à prédire.

### Exercice 4.9 ⭐ — Lire une table de confusion (section 4.3.1)

Sur 1 000 commandes : 40 fraudes détectées, 60 fausses alertes, 10 fraudes manquées, 890 commandes normales laissées passer. Calculez l'exactitude, la précision, le rappel et le F1. Comparez l'exactitude avec celle d'un modèle qui répond toujours « pas de fraude ».

### Exercice 4.10 ⭐⭐ — Ce que font les poids (section 4.3.2)

La fréquence de la classe rare est $\pi=0{,}02$ ; on pondère la classe rare par $w=10$.

(a) Quelle est la cote de la classe rare, et celle estimée par un modèle sans variable explicative après pondération ?
(b) Quelle probabilité cela donne-t-il ?
(c) Un modèle pondéré annonce $p_w=0{,}5$ pour un client. Quelle est la probabilité corrigée ?
(d) À quelle probabilité réelle correspond le seuil de 0,5 du modèle pondéré ?

### Exercice 4.11 ⭐⭐⭐ — Un seuil par les coûts (section 4.3.5)

Une fraude manquée coûte $c_{FN}=50$ € et une fausse alerte $c_{FP}=2$ €.

(a) Calculez le seuil théorique.
(b) Dix commandes, avec leur probabilité prédite (calibrée) et leur vraie classe : $p=(0{,}9;\ 0{,}6;\ 0{,}3;\ 0{,}2;\ 0{,}1;\ 0{,}08;\ 0{,}05;\ 0{,}04;\ 0{,}02;\ 0{,}01)$, $y=(1;\,0;\,1;\,0;\,0;\,0;\,1;\,0;\,0;\,0)$. Calculez le coût total au seuil 0,5 puis au seuil théorique.
(c) Les probabilités viennent d'un modèle pondéré avec $w=20$. Quel seuil faut-il appliquer à ces probabilités gonflées pour obtenir la même décision que le seuil théorique ?

### Exercice 4.12 ⭐⭐ — Mesurer le biais de sélection (section 4.4)

Simulez 100 clients, 1 000 variables de bruit et une cible aléatoire. Sélectionnez les 10 meilleures variables, puis évaluez par validation croisée, (a) en sélectionnant **avant** la validation et (b) **dans** la validation (20 tirages). (c) Comment l'écart évolue-t-il si l'on passe à 1 000 clients ? Expliquez.

### Exercice 4.13 ⭐⭐ — SMOTE à la main (section 4.5.1)

(a) Deux fraudes voisines sont $x=(2;\,10)$ et $x'=(6;\,18)$. Quel point synthétique SMOTE crée-t-il pour $\lambda=0{,}25$, puis pour $\lambda=0{,}9$ ?
(b) Pourquoi les points synthétiques sont-ils toujours sur le segment $[x,x']$ ?
(c) Pour une variable qualitative `canal`, les cinq voisins d'une fraude ont pour canaux : Site, Site, Réseaux, Boutique, Site. Que fait SMOTE-NC ?

### Exercice 4.14 ⭐⭐⭐ — La fuite par rééchantillonnage, sur des données réelles (section 4.5.4)

Le jeu `load_breast_cancer` de scikit-learn (569 tumeurs réelles) est livré avec la bibliothèque. Gardez toutes les tumeurs bénignes et seulement 30 tumeurs malignes (la classe rare, à détecter). Mesurez la PR-AUC d'un classeur des plus proches voisins ($k=1$) en validation croisée : (a) avec le sur-échantillonnage **dans** un pipeline, (b) avec le sur-échantillonnage **avant** la validation croisée. Expliquez pourquoi le $k=1$ rend la fuite si spectaculaire.

## Corrigés

### Corrigé 4.1

(a) Ville P : $\frac24=0{,}5$ ; ville Q : $\frac13\approx0{,}333$ ; ville R : $\frac11=1$. Moyenne générale : $\frac48=0{,}5$.
(b) Avec $k=4$ : P : $\frac{4\times0{,}5+4\times0{,}5}{4+4}=0{,}5$ ; Q : $\frac{3\times\frac13+4\times0{,}5}{3+4}=\frac37\approx0{,}429$ ; R : $\frac{1\times1+4\times0{,}5}{1+4}=0{,}6$.
(c) **La ville R** : elle ne contient qu'un client, et son encodage naïf (1,0) est exactement l'étiquette de ce client. Le lissage ramène la valeur à 0,6.
(d) La moyenne générale, 0,5 (valeur de repli).

```python
y_ex = pd.Series([1, 1, 0, 0, 1, 0, 0, 1], index=list("PPPPQQQR"))
g = y_ex.groupby(level=0).agg(["mean", "count"])
lisse = (g["count"] * g["mean"] + 4 * y_ex.mean()) / (g["count"] + 4)
print(pd.DataFrame({"naïf": g["mean"], "lissé (k = 4)": lisse}).round(3).T.to_string())
print("moyenne générale :", y_ex.mean())
```
<!--sortie-->
```text
                 P      Q    R
naïf           0.5  0.333  1.0
lissé (k = 4)  0.5  0.429  0.6
moyenne générale : 0.5
```

### Corrigé 4.2

(a) Moyenne 6, écart-type de la population $\sqrt{8}\approx2{,}828$ : $z=(-1{,}414;\ -0{,}707;\ 0;\ 0{,}707;\ 1{,}414)$.
(b) Min-max : $(0;\ 0{,}25;\ 0{,}5;\ 0{,}75;\ 1)$. Robuste : $(x-6)/4=(-1;\ -0{,}5;\ 0;\ 0{,}5;\ 1)$.
(c) Avec 100, la moyenne vaut 24 et l'écart-type environ 38,05 : la standardisation donne $(-0{,}578;\ -0{,}526;\ -0{,}473;\ -0{,}420;\ 2{,}0)$ et le min-max $(0;\ 0{,}020;\ 0{,}041;\ 0{,}061;\ 1)$ : les quatre premières valeurs sont **écrasées**. La transformation robuste laisse les quatre premières **inchangées** $(-1;\ -0{,}5;\ 0;\ 0{,}5)$ et envoie la dernière à $23{,}5$.

```python
for valeurs in ([2, 4, 6, 8, 10], [2, 4, 6, 8, 100]):
    v = np.array(valeurs, float)
    q1, q3 = np.percentile(v, [25, 75])
    print(valeurs, "\n  standardisé", ((v - v.mean()) / v.std()).round(3), "\n  min-max   ", ((v - v.min()) / (v.max() - v.min())).round(3),
          "\n  robuste   ", ((v - np.median(v)) / (q3 - q1)).round(3))
```
<!--sortie-->
```text
[2, 4, 6, 8, 10] 
  standardisé [-1.414 -0.707  0.     0.707  1.414] 
  min-max    [0.   0.25 0.5  0.75 1.  ] 
  robuste    [-1.  -0.5  0.   0.5  1. ]
[2, 4, 6, 8, 100] 
  standardisé [-0.578 -0.526 -0.473 -0.42   1.997] 
  min-max    [0.    0.02  0.041 0.061 1.   ] 
  robuste    [-1.  -0.5  0.   0.5 23.5]
```

### Corrigé 4.3

(a) Pour $\lambda=\frac12$ : $\frac{\sqrt x-1}{1/2}=2(\sqrt x-1)$, soit $(0;\ 2;\ 4;\ 6)$ : l'écart entre valeurs devient **constant** (2). C'est normal : 1, 4, 9, 16 sont des carrés parfaits, et la racine les ramène à 1, 2, 3, 4 régulièrement espacés. Pour $\lambda=0$ : $\ln x=(0;\ 1{,}386;\ 2{,}197;\ 2{,}773)$ : les écarts diminuent, la queue de droite est resserrée.
(b) Pour $\lambda=1$ : si $x=5\ge0$, $\frac{(5+1)^1-1}{1}=5$ ; si $x=-3<0$, $-\frac{(1+3)^{2-1}-1}{2-1}=-3$. Pour $\lambda=1$ la transformation de Yeo-Johnson est l'**identité** : on ne change rien, ce qui est la valeur « neutre » du paramètre.

```python
x = np.array([1, 4, 9, 16.0])
print("Box-Cox lambda = 0,5 :", (np.sqrt(x) - 1) / 0.5, "| lambda = 0 :", np.log(x).round(3))
from scipy.stats import yeojohnson
print("Yeo-Johnson, lambda = 1 :", yeojohnson(np.array([-3.0, 5.0]), lmbda=1.0))
```
<!--sortie-->
```text
Box-Cox lambda = 0,5 : [0. 2. 4. 6.] | lambda = 0 : [0.    1.386 2.197 2.773]
Yeo-Johnson, lambda = 1 : [-3.  5.]
```

### Corrigé 4.4

(a) **MCAR** (au hasard, sans lien avec la valeur) : supprimer les lignes ou imputer par la médiane est sans biais ; l'indicateur d'absence est inutile.
(b) **MNAR** : l'absence dépend de la valeur manquante elle-même. On ne peut pas la corriger complètement ; on ajoute un **indicateur d'absence** et on le signale comme limite de l'étude.
(c) **MAR** : l'absence dépend d'une variable **observée** (l'âge). On peut imputer en s'appuyant sur l'âge (imputation conditionnelle) et garder l'indicateur.
(d) **Structurel** : la valeur n'existe pas (aucune commande, donc aucun panier). Ne pas imputer par la moyenne : on crée un indicateur (« jamais commandé ») et on traite ces clients comme un groupe à part.

### Corrigé 4.5

(a) **Fuites** : l'imputation, la standardisation et surtout la **sélection de variables** sont faites avant la séparation, donc elles utilisent aussi les lignes du test (et, pour la sélection, **les étiquettes du test**). **Correct** : SMOTE n'est appliqué qu'après la séparation, sur l'entraînement.
(b) Le pipeline suivant apprend toutes les étapes sur les plis d'entraînement seulement.
(c) Sur du bruit pur, l'AUC devrait valoir 0,5. Le script fautif donne une valeur trompeusement élevée.

```python
from sklearn.feature_selection import SelectKBest, f_classif
from imblearn.over_sampling import SMOTE

def fautif(X, yy):
    Z = StandardScaler().fit_transform(SimpleImputer(strategy="median").fit_transform(X))
    Z = SelectKBest(f_classif, k=10).fit_transform(Z, yy)
    ztr, zte, ytr_, yte_ = train_test_split(Z, yy, stratify=yy, random_state=0)
    ztr, ytr_ = SMOTE(random_state=0).fit_resample(ztr, ytr_)
    return roc_auc_score(yte_, LogisticRegression().fit(ztr, ytr_).predict_proba(zte)[:, 1])

def correct(X, yy):
    Xtr_, Xte_, ytr_, yte_ = train_test_split(X, yy, stratify=yy, random_state=0)
    pipe = PipeIB([("imp", SimpleImputer(strategy="median")), ("sc", StandardScaler()), ("sel", SelectKBest(f_classif, k=10)),
                   ("smote", SMOTE(random_state=0)), ("lr", LogisticRegression())]).fit(Xtr_, ytr_)
    return roc_auc_score(yte_, pipe.predict_proba(Xte_)[:, 1])

avant, apres = [], []
for g in range(20):
    r = np.random.default_rng(g)
    X, yy = r.normal(size=(200, 100)), r.integers(0, 2, 200)
    avant.append(fautif(X, yy)); apres.append(correct(X, yy))
print(f"AUC de test sur du bruit pur : script fautif {np.mean(avant):.3f} | pipeline {np.mean(apres):.3f}")
```
<!--sortie-->
```text
AUC de test sur du bruit pur : script fautif 0.714 | pipeline 0.485
```

La différence tient à la sélection : choisir les 10 meilleures variables sur **toutes** les lignes (étiquettes du test comprises) trouve des variables qui, par hasard, ressemblent à la cible aussi sur le test.

### Corrigé 4.6

| client | taux de retour | tickets par commande | fréquence mensuelle | montant par commande |
|---|---|---|---|---|
| A | $\frac14=0{,}25$ | $\frac{2}{4+1}=0{,}4$ | $\frac4{12}\approx0{,}333$ | $\frac{200}{4}=50$ |
| B | $0$ (convention) | $\frac0{0+1}=0$ | $\frac08=0$ | **indéfini** (division par zéro) |
| C | $\frac4{10}=0{,}4$ | $\frac5{11}\approx0{,}455$ | $\frac{10}5=2$ | $\frac{800}{10}=80$ |

Pour le client B, le **montant par commande** est indéfini : il faut le laisser manquant (avec un indicateur « jamais commandé »), pas le remplacer par 0, qui voudrait dire « il commande pour 0 € ».

```python
t = pd.DataFrame({"cmd": [4, 0, 10], "ret": [1, 0, 4], "tick": [2, 0, 5], "anc": [30, 8, 5], "mont": [200, 0, 800]}, index=list("ABC"))
print(pd.DataFrame({"taux_retour": (t.ret / t.cmd.replace(0, np.nan)).fillna(0), "tickets_par_cmd": t.tick / (t.cmd + 1),
                    "freq_mensuelle": t.cmd / np.minimum(t.anc, 12), "montant_par_cmd": t.mont / t.cmd.replace(0, np.nan)}).round(3))
```
<!--sortie-->
```text
   taux_retour  tickets_par_cmd  freq_mensuelle  montant_par_cmd
A         0.25            0.400           0.333             50.0
B         0.00            0.000           0.000              NaN
C         0.40            0.455           2.000             80.0
```

### Corrigé 4.7

(a) Angles de $15^\circ\times h$. $h=23$ : $345^\circ$, $(\sin,\cos)=(-0{,}2588;\ 0{,}9659)$ ; $h=1$ : $15^\circ$, $(0{,}2588;\ 0{,}9659)$ ; $h=12$ : $180^\circ$, $(0;\ -1)$.
(b) $d(23\,\text{h},1\,\text{h})=\sqrt{(0{,}2588+0{,}2588)^2+0^2}=0{,}518$ ; $d(23\,\text{h},12\,\text{h})=\sqrt{0{,}2588^2+1{,}9659^2}\approx1{,}983$. Sur l'entier, les distances sont 22 et 11 : minuit semble **plus loin** de 23 h que midi. Sur le cercle, 23 h et 1 h sont proches (0,518) et 23 h et midi opposés (1,983), comme dans la réalité.

```python
h = np.array([23, 1, 12])
pts = np.c_[np.sin(2 * np.pi * h / 24), np.cos(2 * np.pi * h / 24)]
print(pts.round(4))
print("d(23 h, 1 h) =", np.linalg.norm(pts[0] - pts[1]).round(3), "| d(23 h, 12 h) =", np.linalg.norm(pts[0] - pts[2]).round(3))
```
<!--sortie-->
```text
[[-0.2588  0.9659]
 [ 0.2588  0.9659]
 [ 0.     -1.    ]]
d(23 h, 1 h) = 0.518 | d(23 h, 12 h) = 1.983
```

### Corrigé 4.8

(a) **Utilisable** : connu au 1er du mois (historique). (b) **Fuite** : la date de résiliation est précisément ce qu'on veut prédire. (c) **Fuite** : le montant facturé dans le mois dépend de la résiliation (un abonné résilié ne reçoit pas de facture complète). (d) **Fuite** : une enquête envoyée à la fin du mois suit la résiliation et peut en dépendre. (e) **Utilisable** : connu au 1er du mois. (f) **Fuite possible** : le modèle a vu le mois à prédire pendant son entraînement ; la variable contient de l'information du futur. Question de contrôle pour chaque variable : *à quelle date cette valeur est-elle connue, par rapport à la date de prédiction ?*

### Corrigé 4.9

Exactitude : $\frac{40+890}{1\,000}=0{,}93$. Précision : $\frac{40}{40+60}=0{,}4$. Rappel : $\frac{40}{40+10}=0{,}8$. F1 : $\frac{2\times0{,}4\times0{,}8}{0{,}4+0{,}8}\approx0{,}533$. Le modèle paresseux a une exactitude de $\frac{950}{1\,000}=0{,}95$, **supérieure** à celle du modèle utile (0,93), alors que son rappel est nul : l'exactitude est trompeuse.

```python
vp, fp, fn, vn = 40, 60, 10, 890
prec, rap = vp / (vp + fp), vp / (vp + fn)
print("exactitude", (vp + vn) / 1000, "| précision", prec, "| rappel", rap, "| F1", round(2 * prec * rap / (prec + rap), 3), "| modèle paresseux :", (vn + fp) / 1000)
```
<!--sortie-->
```text
exactitude 0.93 | précision 0.4 | rappel 0.8 | F1 0.533 | modèle paresseux : 0.95
```

### Corrigé 4.10

(a) Cote de la classe rare : $\frac{0{,}02}{0{,}98}\approx0{,}0204$. Après pondération, la cote estimée est multipliée par $w$ : $0{,}204$.
(b) $p^\star=\frac{0{,}204}{1+0{,}204}\approx0{,}169$ : une probabilité de 2 % est devenue 16,9 %.
(c) Cote pondérée $\frac{0{,}5}{0{,}5}=1$, divisée par $w=10$ : $0{,}1$, soit $p=\frac{0{,}1}{1{,}1}\approx0{,}0909$.
(d) La même : un seuil de 0,5 sur le modèle pondéré revient à un seuil de **9,1 %** sur la probabilité réelle.

```python
pi, w = 0.02, 10
cote = pi / (1 - pi)
print("cote", round(cote, 4), "-> pondérée", round(w * cote, 4), "-> probabilité", round(w * cote / (1 + w * cote), 4))
pw = 0.5
print("probabilité corrigée de p_w = 0,5 :", round(pw / (pw + (1 - pw) * w), 4))
```
<!--sortie-->
```text
cote 0.0204 -> pondérée 0.2041 -> probabilité 0.1695
probabilité corrigée de p_w = 0,5 : 0.0909
```

### Corrigé 4.11

(a) $s^\star=\frac{2}{2+50}\approx0{,}0385$.
(b) Au seuil 0,5, on bloque les commandes 1 et 2 (probabilités 0,9 et 0,6). La commande 2 est une fausse alerte (2 €) ; les fraudes 3 et 7 passent (2 fraudes manquées, 100 €) : coût **102 €**. Au seuil 0,0385, on bloque les huit commandes dont $p\ge0{,}04$ : aucune fraude manquée, cinq fausses alertes (commandes 2, 4, 5, 6, 8) : coût **10 €**.
(c) Le seuil sur la probabilité gonflée est $\frac{s^\star w}{1-s^\star+s^\star w}=\frac{0{,}0385\times20}{1-0{,}0385+0{,}769}\approx0{,}444$ : on bloque dès que le modèle pondéré dépasse **0,444**.

```python
p = np.array([0.9, 0.6, 0.3, 0.2, 0.1, 0.08, 0.05, 0.04, 0.02, 0.01]); v = np.array([1, 0, 1, 0, 0, 0, 1, 0, 0, 0])
cout_ex = lambda s: int(((p < s) & (v == 1)).sum() * 50 + ((p >= s) & (v == 0)).sum() * 2)
s_star = 2 / 52
print("seuil théorique", round(s_star, 4), "| coût à 0,5 :", cout_ex(0.5), "| coût au seuil théorique :", cout_ex(s_star))
print("seuil équivalent pour un modèle pondéré (w = 20) :", round(s_star * 20 / (1 - s_star + s_star * 20), 3))
```
<!--sortie-->
```text
seuil théorique 0.0385 | coût à 0,5 : 102 | coût au seuil théorique : 10
seuil équivalent pour un modèle pondéré (w = 20) : 0.444
```

### Corrigé 4.12

```python
from sklearn.feature_selection import SelectKBest, f_classif
from sklearn.pipeline import Pipeline

def biais(n, p, graines=20):
    avant, dans = [], []
    cv = StratifiedKFold(5, shuffle=True, random_state=0)
    for g in range(graines):
        r = np.random.default_rng(g)
        X, yy = r.normal(size=(n, p)), r.integers(0, 2, n)
        avant.append(cross_val_score(LogisticRegression(max_iter=2000), SelectKBest(f_classif, k=10).fit_transform(X, yy), yy, cv=cv, scoring="roc_auc").mean())
        dans.append(cross_val_score(Pipeline([("s", SelectKBest(f_classif, k=10)), ("m", LogisticRegression(max_iter=2000))]), X, yy, cv=cv, scoring="roc_auc").mean())
    return np.mean(avant), np.mean(dans)

for n in (100, 1000):
    a, d = biais(n, 1000)
    print(f"n = {n:4d}, p = 1000 : AUC sélection avant {a:.3f} | dans la validation {d:.3f}")
```
<!--sortie-->
```text
n =  100, p = 1000 : AUC sélection avant 0.866 | dans la validation 0.489
n = 1000, p = 1000 : AUC sélection avant 0.639 | dans la validation 0.492
```

(a)-(b) Avec 100 clients et 1 000 variables, la sélection **avant** la validation donne une AUC de 0,866 sur du bruit pur, la sélection **dans** la validation 0,489 (le hasard). (c) Avec 1 000 clients le biais diminue (0,639 au lieu de 0,866) sans disparaître : parmi 1 000 variables aléatoires, il est plus difficile qu'avec 100 clients d'en trouver 10 qui ressemblent à la cible **par hasard**, car la corrélation fortuite d'une variable avec la cible décroît en $1/\sqrt n$.

### Corrigé 4.13

(a) $x+\lambda(x'-x)$ avec $x'-x=(4;\,8)$ : pour $\lambda=0{,}25$ : $(2+1;\ 10+2)=(3;\ 12)$ ; pour $\lambda=0{,}9$ : $(2+3{,}6;\ 10+7{,}2)=(5{,}6;\ 17{,}2)$.
(b) Parce que $x+\lambda(x'-x)=(1-\lambda)x+\lambda x'$ avec $\lambda\in[0,1]$ est une **combinaison convexe** de $x$ et $x'$ : elle décrit exactement le segment qui les relie.
(c) SMOTE-NC ne peut pas interpoler une catégorie : le point synthétique reçoit la modalité **la plus fréquente parmi les voisins**, ici « Site » (3 voisins sur 5).

### Corrigé 4.14

```python
from sklearn.datasets import load_breast_cancer
from sklearn.neighbors import KNeighborsClassifier

d = load_breast_cancer(as_frame=True)
X_bc, y_bc = d.data, (d.target == 0).astype(int)                  # 1 = tumeur maligne (la classe rare)
r = np.random.default_rng(0)
idx = np.r_[np.where(y_bc == 0)[0], r.choice(np.where(y_bc == 1)[0], 30, replace=False)]
Xr, yr = X_bc.iloc[idx], y_bc.iloc[idx]
cv = StratifiedKFold(5, shuffle=True, random_state=0)
dans = cross_val_score(PipeIB([("sc", StandardScaler()), ("o", RandomOverSampler(random_state=0)), ("m", KNeighborsClassifier(1))]), Xr, yr, cv=cv, scoring="average_precision")
Xo, yo = RandomOverSampler(random_state=0).fit_resample(StandardScaler().fit_transform(Xr), yr)
avant = cross_val_score(KNeighborsClassifier(1), Xo, yo, cv=cv, scoring="average_precision")
print("part de tumeurs malignes :", round(yr.mean(), 3))
print(f"suréchantillonnage DANS le pipeline : PR-AUC {dans.mean():.3f} | AVANT la validation croisée : {avant.mean():.3f}")
```
<!--sortie-->
```text
part de tumeurs malignes : 0.078
suréchantillonnage DANS le pipeline : PR-AUC 0.881 | AVANT la validation croisée : 0.994
```

Le sur-échantillonnage avant la validation recopie chaque tumeur maligne plusieurs fois : une copie tombe dans le pli d'entraînement, une autre dans le pli de validation. Avec $k=1$, le classeur retrouve **la copie exacte** du point à évaluer (distance 0) et reprend son étiquette : le score est artificiellement parfait. Ici, 7,8 % des tumeurs retenues sont malignes ; la PR-AUC passe de 0,881 (pipeline correct) à 0,994 (fuite). Le $k=1$ est le cas extrême, parce que ce classeur ne fait que retrouver le point le plus proche.
