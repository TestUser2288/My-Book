# Chapitre 1 : Risque de crédit et scoring — exercices et applications

> 🧭 **Ce chapitre du cahier** accompagne le chapitre 1 du livre. Il contient **huit applications guidées** (de petites études que vous refaites sur les données du volume) et **quatorze exercices** de difficulté croissante (⭐ calcul à la main, ⭐⭐ calcul puis code, ⭐⭐⭐ étude plus ouverte), tous **corrigés** en fin de chapitre. Les données sont **simulées** (générateur `build/donnees5.py`, vérité programmée en docstring), sauf le jeu réel `credit_defaut.csv` (UCI, CC0). Le fichier est **autonome** : une seule cellule recharge tout.

```python
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import outils_ch01 as O
import donnees5
from sklearn.linear_model import LogisticRegression
import statsmodels.api as sm

tr, te = O.charger_credits()                      # 28 000 prêts de développement, 12 000 de test (graine fixe)
y_tr, y_te = tr["defaut_12m"].values, te["defaut_12m"].values
print(len(tr), len(te), round(y_tr.mean(), 4), round(y_te.mean(), 4))
```
<!--sortie-->
```text
28000 12000 0.0597 0.0597
```

## Applications

### Application 1.1 — Construire la grille complète (section 1.1)

**Objectif.** Refaire, étape par étape, la grille du livre : tables WOE, régression, points, carte, score de chaque dossier du test, et vérifier la propriété du PDO.

**Étape 1 — les tables WOE et l'IV.** `O.tables_woe` applique les classes de `O.BORNES` (bornes choisies à la main) et calcule, pour chaque variable, effectifs, taux de défaut, WOE (lissé d'une demi-observation) et IV.

```python
tables = O.tables_woe(tr)
iv = pd.Series({v: t["iv"].sum() for v, t in tables.items()}).sort_values(ascending=False)
print(iv.round(3).to_string())
print(tables["revenu_annuel"][["effectif", "taux_defaut", "woe", "iv"]].round(3).to_string())
```
<!--sortie-->
```text
taux_endettement       0.403
anciennete_emploi      0.258
nb_incidents_12m       0.240
revenu_annuel          0.236
age                    0.145
montant                0.071
logement               0.054
anciennete_relation    0.051
duree_mois             0.029
objet                  0.015
                effectif  taux_defaut    woe     iv
classe                                             
1: <20000           3963        0.117 -0.731  0.105
2: 20000-26000      4594        0.072 -0.208  0.008
3: 26000-32000      4800        0.058  0.036  0.000
4: 32000-40000      5041        0.051  0.163  0.004
5: 40000-50000      4004        0.034  0.574  0.037
6: 50000+           4200        0.025  0.884  0.081
manquant            1398        0.069 -0.153  0.001
```

**Étape 2 — la régression sur les WOE.** On prédit « bon » (1 − défaut) à partir des WOE ; les coefficients proches de 1 correspondent à des variables presque indépendantes.

```python
W_tr = O.vers_woe(tr, tables)
lr = LogisticRegression(max_iter=2000).fit(W_tr, 1 - y_tr)
print(pd.Series(lr.coef_[0], index=W_tr.columns).round(2).to_string())
print("intercept :", round(float(lr.intercept_[0]), 3))
```
<!--sortie-->
```text
age                    0.85
taux_endettement       0.72
anciennete_emploi      0.80
revenu_annuel          0.65
montant                0.25
duree_mois             0.35
nb_incidents_12m       0.85
anciennete_relation    1.04
logement               1.01
objet                  0.98
intercept : 2.746
```

**Étape 3 — la carte de score.** La classe `O.Grille` refait les deux étapes et convertit en points (base 600 pour une cote de 50 contre 1, PDO de 20).

```python
G = O.Grille(tr, base=600, cotes_base=50, pdo=20)
carte = G.points_classes()
print("facteur", round(G.facteur, 2), " décalage", round(G.decalage, 2), " lignes de la carte :", len(carte))
print(carte[carte.variable.isin(["revenu_annuel", "logement", "objet"])].drop(columns="variable").to_string(index=False))
```
<!--sortie-->
```text
facteur 28.85  décalage 487.12  lignes de la carte : 50
        classe  effectif  taux_defaut    woe  points
     1: <20000      3963       0.1166 -0.731    42.9
2: 20000-26000      4594       0.0725 -0.208    52.7
3: 26000-32000      4800       0.0577  0.036    57.3
4: 32000-40000      5041       0.0512  0.163    59.7
5: 40000-50000      4004       0.0345  0.574    67.4
     6: 50000+      4200       0.0255  0.884    73.3
      manquant      1398       0.0687 -0.153    53.8
       heberge      5700       0.0744 -0.236    49.7
     locataire     11747       0.0668 -0.120    53.1
  proprietaire     10553       0.0438  0.326    66.2
          auto     11071       0.0557  0.073    58.7
         conso      9900       0.0690 -0.155    52.3
       travaux      7029       0.0528  0.130    60.3
```

**Étape 4 — scores et performance sur le test.** Un score élevé signale un dossier sûr : pour l'AUC, on passe au risque en changeant le signe.

```python
s_te = G.score(te)
print("AUC", round(O.auc(y_te, -s_te), 4), " Gini", round(O.gini(y_te, -s_te), 4), " KS", round(O.ks(y_te, -s_te), 4))
print("score : min", round(s_te.min()), " médian", round(np.median(s_te)), " max", round(s_te.max()))
```
<!--sortie-->
```text
AUC 0.7712  Gini 0.5425  KS 0.4058
score : min 442  médian 583  max 659
```

**Étape 5 — vérifier le PDO.** Si la mise à l'échelle est juste, la log-cote observée est une fonction affine du score de pente $1/\text{facteur}$ : regroupons le test en vingt tranches de score, calculons la log-cote observée (bons contre mauvais) et régressons.

```python
g = pd.DataFrame({"s": s_te, "y": y_te}); g["q"] = pd.qcut(g["s"], 20, labels=False)
t = g.groupby("q").agg(s=("s", "mean"), mauvais=("y", "sum"), n=("y", "size"))
t["logcote"] = np.log((t["n"] - t["mauvais"] + 0.5) / (t["mauvais"] + 0.5))
pente = np.polyfit(t["s"], t["logcote"], 1)[0]
print("pente observée", round(pente, 4), " pente attendue 1/facteur =", round(1 / G.facteur, 4))
print("points pour doubler la cote, observés :", round(np.log(2) / pente, 1), "(PDO visé : 20)")
```
<!--sortie-->
```text
pente observée 0.0336  pente attendue 1/facteur = 0.0347
points pour doubler la cote, observés : 20.7 (PDO visé : 20)
```

*À vous.* (a) Refaites la grille avec une base de 650 points pour une cote de 30 contre 1 et un PDO de 40 : la performance change-t-elle ? (b) Retirez les trois variables d'IV le plus faible : que perd l'AUC ?

### Application 1.2 — L'inférence des rejets (section 1.1.7)

**Objectif.** Mesurer le biais d'une grille construite sur les seuls acceptés, puis tester une correction par **parcelling** (étiquettes imputées aux refusés), en comparant à ce qu'aurait donné l'observation complète (que nous avons ici, par construction).

**Étape 1 — la politique d'acceptation.** On refuse les endettements supérieurs à 50 % et les clients de plus d'un incident.

```python
def acceptes(d):
    return (d["taux_endettement"] <= 0.5) & (d["nb_incidents_12m"] <= 1)
ok = acceptes(tr)
print("part acceptée :", round(ok.mean(), 3), " défaut des acceptés :", round(tr.loc[ok, "defaut_12m"].mean(), 4),
      " défaut des refusés (inconnu en pratique) :", round(tr.loc[~ok, "defaut_12m"].mean(), 4))
```
<!--sortie-->
```text
part acceptée : 0.885  défaut des acceptés : 0.0449  défaut des refusés (inconnu en pratique) : 0.1738
```

**Étape 2 — grille sur les acceptés seuls**, mesurée sur tous les demandeurs du test.

```python
Ga = O.Grille(tr[ok])
def bilan(G_, nom):
    return {"grille": nom, "AUC (tous)": round(O.auc(y_te, -G_.score(te)), 4), "PD annoncée": round(float(G_.pd_predite(te).mean()), 4)}
res = [bilan(O.Grille(tr), "tous les demandeurs (oracle)"), bilan(Ga, "acceptés seuls")]
```

**Étape 3 — parcelling.** On score les refusés avec la grille des acceptés, on leur impute une étiquette tirée au sort avec la probabilité $\min(1,\ m\times\text{PD annoncée})$, où $m$ est un coefficient de prudence (on teste 1 et 2), puis l'on reconstruit la grille sur acceptés + refusés étiquetés.

```python
rng = np.random.default_rng(0)
p_ref = Ga.pd_predite(tr[~ok])
for m in (1, 2):
    aug = tr.copy()
    aug.loc[~ok, "defaut_12m"] = (rng.random((~ok).sum()) < np.minimum(1, m * p_ref)).astype(int)
    res.append(bilan(O.Grille(aug), f"parcelling, coefficient {m}"))
print(pd.DataFrame(res).to_string(index=False)); print("défaut réel du test :", round(y_te.mean(), 4))
```
<!--sortie-->
```text
                      grille  AUC (tous)  PD annoncée
tous les demandeurs (oracle)      0.7712       0.0593
              acceptés seuls      0.7156       0.0439
   parcelling, coefficient 1      0.7198       0.0439
   parcelling, coefficient 2      0.7634       0.0494
défaut réel du test : 0.0597
```

*À vous.* Quelle valeur de $m$ rapproche le plus la PD annoncée du défaut réel ? Pourquoi ne pouvez-vous pas la choisir ainsi en pratique ?

### Application 1.3 — Trois modèles, un verdict (section 1.2)

**Objectif.** Comparer la grille, la logistique brute et un boosting monotone, avec incertitude, calibration et motifs de refus.

**Étape 1 — les trois modèles** (mêmes données, aucun réglage sur le test).

```python
import lightgbm as lgb
def brut(d):
    X = d[["age", "revenu_annuel", "anciennete_emploi", "montant", "duree_mois", "taux_endettement", "nb_incidents_12m", "anciennete_relation"]].copy()
    for k in ["revenu_annuel", "anciennete_emploi"]:
        X[k + "_manq"] = X[k].isna().astype(int)
    return pd.concat([X, pd.get_dummies(d[["logement", "objet"]]).astype(int)], axis=1)
Xb_tr, Xb_te = brut(tr), brut(te)
med = Xb_tr.median(); mu, sd = Xb_tr.fillna(med).mean(), Xb_tr.fillna(med).std()
p_lr = LogisticRegression(max_iter=3000).fit((Xb_tr.fillna(med) - mu) / sd, y_tr).predict_proba((Xb_te.fillna(med) - mu) / sd)[:, 1]
signes = {"taux_endettement": 1, "nb_incidents_12m": 1, "revenu_annuel": -1, "anciennete_emploi": -1, "anciennete_relation": -1}
gbm = lgb.LGBMClassifier(n_estimators=300, learning_rate=0.03, num_leaves=8, min_child_samples=200, subsample=0.8, subsample_freq=1,
                         colsample_bytree=0.8, monotone_constraints=[signes.get(c, 0) for c in Xb_tr.columns], random_state=0, verbose=-1).fit(Xb_tr, y_tr)
p_gbm = gbm.predict_proba(Xb_te)[:, 1]
r_grille = -O.Grille(tr).score(te)
print({k: round(O.auc(y_te, v), 4) for k, v in {"logistique": p_lr, "grille": r_grille, "boosting monotone": p_gbm}.items()})
```
<!--sortie-->
```text
{'logistique': 0.7618, 'grille': 0.7712, 'boosting monotone': 0.7737}
```

**Étape 2 — intervalles apparié et isolé.**

```python
for nom, v in {"logistique": p_lr, "grille": r_grille, "boosting monotone": p_gbm}.items():
    print(nom, np.round(O.bootstrap_auc(y_te, v, 300), 3))
for a, b, na, nb in [(r_grille, p_lr, "grille", "logistique"), (r_grille, p_gbm, "grille", "boosting")]:
    m_, ic = O.bootstrap_diff_auc(y_te, a, b, 300, 1)
    print(f"AUC {na} - AUC {nb} : {m_:+.4f}  [{ic[0]:+.4f} ; {ic[1]:+.4f}]")
```
<!--sortie-->
```text
logistique [0.743 0.78 ]
grille [0.751 0.791]
boosting monotone [0.754 0.791]
AUC grille - AUC logistique : +0.0097  [+0.0009 ; +0.0182]
AUC grille - AUC boosting : -0.0022  [-0.0089 ; +0.0040]
```

**Étape 3 — la calibration par dixième** (probabilités annoncées par le boosting et par la logistique, contre le défaut observé), et le score de Brier.

```python
from sklearn.metrics import brier_score_loss
cal = pd.DataFrame({"logistique": p_lr, "boosting": p_gbm, "défaut": y_te})
cal["groupe"] = pd.qcut(cal["boosting"], 10, labels=False) + 1
print(cal.groupby("groupe").mean().round(4).to_string())
print({k: round(brier_score_loss(y_te, v), 5) for k, v in {"logistique": p_lr, "boosting": p_gbm}.items()})
```
<!--sortie-->
```text
        logistique  boosting  défaut
groupe                              
1           0.0082    0.0075  0.0092
2           0.0146    0.0130  0.0192
3           0.0205    0.0177  0.0175
4           0.0271    0.0231  0.0225
5           0.0346    0.0296  0.0258
6           0.0431    0.0379  0.0450
7           0.0554    0.0493  0.0508
8           0.0716    0.0665  0.0675
9           0.1036    0.1004  0.1000
10          0.2185    0.2523  0.2392
{'logistique': 0.05041, 'boosting': 0.04997}
```

*À vous.* (a) Recalibrez le boosting par une régression logistique sur sa sortie (volume III, section 5.2) sur un échantillon à part, et comparez les Brier. (b) Imposez au boosting aussi la monotonie de l'âge : que se passe-t-il, et pourquoi est-ce une erreur ?

### Application 1.4 — Performance, seuil et stabilité (section 1.3)

**Objectif.** Choisir un seuil d'acceptation **par le profit**, calculer un PSI et constater que le test binomial rejette une PD correcte quand les défauts sont corrélés.

**Étape 1 — le profit d'un seuil.** Hypothèses de l'exercice (illustratives) : un bon prêt rapporte 450 € de marge, un défaut coûte 4 000 € de perte nette. Pour chaque seuil de score, le profit attendu est la somme, sur les dossiers acceptés, de la marge des bons moins la perte des mauvais.

```python
G = O.Grille(tr); s_te = G.score(te)
seuils = np.arange(500, 640, 10)
profit = [(450 * ((y_te == 0) & (s_te >= c)).sum() - 4000 * ((y_te == 1) & (s_te >= c)).sum()) / 1e3 for c in seuils]
tab = pd.DataFrame({"seuil": seuils, "acceptés (%)": [100 * (s_te >= c).mean() for c in seuils], "profit (k€)": profit}).round(1)
print(tab.to_string(index=False))
print("meilleur seuil :", int(seuils[int(np.argmax(profit))]), "points")
```
<!--sortie-->
```text
 seuil  acceptés (%)  profit (k€)
   500          98.9       2457.9
   510          98.0       2570.4
   520          96.8       2716.0
   530          94.7       2810.9
   540          91.2       2893.4
   550          85.7       2920.8
   560          78.3       2923.4
   570          67.6       2703.9
   580          53.9       2328.6
   590          39.0       1745.6
   600          24.3       1112.4
   610          12.5        599.4
   620           5.2        256.4
   630           1.7         86.4
meilleur seuil : 560 points
```

**Étape 2 — le PSI.** Simulons une nouvelle population plus jeune et plus endettée (tirage pondéré dans le test) et comparons.

```python
w = np.exp(1.2 * (te["age"] < 30) + 0.8 * (te["taux_endettement"] > 0.4)); w = w / w.sum()
nv = te.sample(6000, replace=True, weights=w, random_state=3)
print("PSI score :", round(O.psi(G.score(tr), G.score(nv), 10), 3), " PSI âge :", round(O.psi(tr["age"], nv["age"], 10), 3),
      " défaut observé :", round(nv["defaut_12m"].mean(), 4), " PD annoncée :", round(float(G.pd_predite(nv).mean()), 4))
```
<!--sortie-->
```text
PSI score : 0.129  PSI âge : 0.246  défaut observé : 0.0893  PD annoncée : 0.0873
```

**Étape 3 — le test binomial et la corrélation.** On simule un portefeuille de 20 000 prêts dont la **vraie** PD est 3 %, avec un facteur commun (corrélation d'actifs $\rho$, modèle de Vasicek) : la PD conditionnelle est $\Phi\bigl((\Phi^{-1}(0{,}03)-\sqrt\rho\,Z)/\sqrt{1-\rho}\bigr)$ avec $Z$ gaussien. On compte les rejets du test binomial à 5 %.

```python
from scipy.stats import binomtest, norm
rng = np.random.default_rng(0)
for rho in (0.0, 0.01, 0.03):
    rej = 0
    for _ in range(1000):
        pc = norm.cdf((norm.ppf(0.03) - np.sqrt(rho) * rng.normal()) / np.sqrt(1 - rho))
        rej += binomtest(int(rng.binomial(20000, pc)), 20000, 0.03).pvalue < 0.05
    print(f"corrélation {rho:.2f} : le test rejette à tort {rej / 1000:.1%} des portefeuilles")
```
<!--sortie-->
```text
corrélation 0.00 : le test rejette à tort 5.1% des portefeuilles
corrélation 0.01 : le test rejette à tort 73.4% des portefeuilles
corrélation 0.03 : le test rejette à tort 84.4% des portefeuilles
```

*À vous.* Tracez le profit en fonction du seuil (avec un pas de 2 points) si la perte d'un défaut passe de 4 000 € à 6 000 € : le seuil optimal monte-t-il ou descend-il ?

### Application 1.5 — WOE, IV et fusion monotone (section 1.4)

**Objectif.** Apprendre à regarder un découpage : fusion monotone, IV de développement contre IV de test, effet d'un découpage forcé sur la performance.

**Étape 1 — fusion monotone** sur quatre variables (sens attendu : le risque décroît avec la variable).

```python
for nom in ("revenu_annuel", "anciennete_relation", "anciennete_emploi", "age"):
    b, n, m = O.fusion_monotone(tr[nom], y_tr, 10, -1)
    print(f"{nom:20s} {len(b):2d} classes, IV {O.iv_partition(n, m):.3f}, taux (%) {np.round(100 * m / n, 1)}")
```
<!--sortie-->
```text
revenu_annuel         9 classes, IV 0.267, taux (%) [13.2  8.1  7.6  5.7  5.7  4.4  3.7  3.1  2.2]
anciennete_relation   9 classes, IV 0.054, taux (%) [8.2 7.  6.7 6.3 6.  5.5 5.3 4.6 3.5]
anciennete_emploi     7 classes, IV 0.262, taux (%) [10.2  8.6  6.6  5.3  4.6  3.2  2.8]
age                   5 classes, IV 0.127, taux (%) [13.4  6.3  5.8  5.1  5. ]
```

**Étape 2 — le bruit.** L'IV d'une variable sans aucun lien avec le défaut grandit avec le nombre de classes ; sur le test, il ne devrait pas.

```python
rng = np.random.default_rng(0)
bruit_tr, bruit_te = rng.normal(size=len(tr)), rng.normal(size=len(te))
def iv_dev_test(x, y, x2, y2, k):
    q = np.unique(np.quantile(x, np.linspace(0, 1, k + 1)[1:-1])); i = np.searchsorted(q, x, side="right")
    n = np.bincount(i, minlength=len(q) + 1); m = np.bincount(i, weights=y, minlength=len(q) + 1)
    b = n - m; pb = (b + .5) / (b.sum() + .5 * len(n)); pm = (m + .5) / (m.sum() + .5 * len(n)); woe = np.log(pb / pm)
    j = np.searchsorted(q, x2, side="right"); n2 = np.bincount(j, minlength=len(q) + 1); m2 = np.bincount(j, weights=y2, minlength=len(q) + 1); b2 = n2 - m2
    return round(O.iv_partition(n, m), 4), round(float(((b2 / b2.sum() - m2 / m2.sum()) * woe).sum()), 4)
for k in (3, 10, 30, 100):
    print(k, "classes (bruit) : IV développement, IV test =", iv_dev_test(bruit_tr, y_tr, bruit_te, y_te, k))
```
<!--sortie-->
```text
3 classes (bruit) : IV développement, IV test = (0.0001, 0.0008)
10 classes (bruit) : IV développement, IV test = (0.0022, 0.0008)
30 classes (bruit) : IV développement, IV test = (0.0194, -0.0025)
100 classes (bruit) : IV développement, IV test = (0.0553, -0.0155)
```

**Étape 3 — forcer la monotonie de l'âge coûte-t-il de la performance ?** On remplace les classes de l'âge par celles de la fusion monotone (bornes inférieures renvoyées par `fusion_monotone`) et l'on recalcule l'AUC de test. Les bornes du module sont **restaurées** ensuite.

```python
import copy
B0 = copy.deepcopy(O.BORNES)
b_age, _, _ = O.fusion_monotone(tr["age"], y_tr, 10, -1)
base = O.auc(y_te, -O.Grille(tr).score(te))
O.BORNES["age"] = list(b_age) + [np.inf]
forcee = O.auc(y_te, -O.Grille(tr).score(te))
O.BORNES.clear(); O.BORNES.update(B0)
print("bornes de l'âge forcées monotones :", np.round(b_age[1:], 0), "\nAUC test, classes de la main :", round(base, 4), " classes monotones :", round(forcee, 4))
```
<!--sortie-->
```text
bornes de l'âge forcées monotones : [26. 32. 36. 39.] 
AUC test, classes de la main : 0.7712  classes monotones : 0.7668
```

*À vous.* Faites la même comparaison pour le revenu (la monotonie y est justifiée) et pour le taux d'endettement.

### Application 1.6 — LGD et CCF (section 1.5)

**Objectif.** Modéliser la LGD (quatre modèles) et le CCF, puis calculer une exposition.

**Étape 1 — la distribution et les segments.**

```python
lg = pd.read_csv("donnees/recouvrements.csv")
print(lg["lgd_realisee"].describe().round(3).to_string())
print(lg.groupby("garantie")["lgd_realisee"].agg(["mean", "count"]).round(3).to_string())
print("pertes nulles :", round((lg["lgd_realisee"] == 0).mean(), 3), " pertes > 95 % :", round((lg["lgd_realisee"] > 0.95).mean(), 3))
```
<!--sortie-->
```text
count    6000.000
mean        0.459
std         0.342
min         0.000
25%         0.124
50%         0.450
75%         0.772
max         1.000
               mean  count
garantie                  
aucune        0.609   2993
caution       0.269   1852
nantissement  0.373   1155
pertes nulles : 0.12  pertes > 95 % : 0.091
```

**Étape 2 — quatre modèles** (moyenne, linéaire, fractionnel, deux étapes), sur 70 % des prêts, jugés sur 30 %.

```python
from sklearn.model_selection import train_test_split
ltr, lte = train_test_split(lg, test_size=0.3, random_state=1)
def conc(d): return pd.get_dummies(d[["garantie", "objet"]], drop_first=True).astype(float).assign(ead=np.log(d["ead"]) - 9)
Xl = sm.add_constant(conc(ltr)); Xt = sm.add_constant(conc(lte)).reindex(columns=Xl.columns); yl = lte["lgd_realisee"].values
p_ols = np.clip(sm.OLS(ltr["lgd_realisee"], Xl).fit().predict(Xt), 0, 1)
p_fr = sm.GLM(ltr["lgd_realisee"], Xl, family=sm.families.Binomial()).fit().predict(Xt)
pz = sm.Logit((ltr["lgd_realisee"] == 0).astype(int), Xl).fit(disp=0).predict(Xt)
pos = ltr[ltr["lgd_realisee"] > 0]
p_2 = (1 - pz) * sm.GLM(pos["lgd_realisee"], Xl.loc[pos.index], family=sm.families.Binomial()).fit().predict(Xt)
r2 = lambda p: 1 - np.sum((p - yl) ** 2) / np.sum((yl - yl.mean()) ** 2)
for nom, p in [("moyenne", np.full(len(yl), ltr["lgd_realisee"].mean())), ("linéaire", p_ols), ("fractionnel", p_fr), ("deux étapes", p_2)]:
    print(f"{nom:12s} erreur absolue {np.mean(np.abs(p - yl)):.4f}   R² {r2(np.asarray(p)):.4f}")
```
<!--sortie-->
```text
moyenne      erreur absolue 0.3063   R² -0.0003
linéaire     erreur absolue 0.2591   R² 0.2165
fractionnel  erreur absolue 0.2591   R² 0.2163
deux étapes  erreur absolue 0.2591   R² 0.2163
```

**Étape 3 — le CCF et l'exposition.**

```python
rv = pd.read_csv("donnees/revolving_defauts.csv"); rv["util"] = rv["tirage_12m_avant"] / rv["limite"]
print(rv.groupby(pd.qcut(rv["util"], 5))["ccf_observe"].mean().round(3).to_string())
ccf = rv["ccf_observe"].mean()
ead = rv["tirage_12m_avant"] + ccf * (rv["limite"] - rv["tirage_12m_avant"])
print("CCF moyen", round(ccf, 3), "| EAD réelle", round(rv["ead"].sum() / 1e6, 1), "M€ | EAD par CCF", round(ead.sum() / 1e6, 1), "M€ | tirages seuls", round(rv["tirage_12m_avant"].sum() / 1e6, 1), "M€")
```
<!--sortie-->
```text
util
(0.00441, 0.214]    0.495
(0.214, 0.328]      0.443
(0.328, 0.441]      0.414
(0.441, 0.577]      0.357
(0.577, 0.966]      0.299
CCF moyen 0.402 | EAD réelle 23.8 M€ | EAD par CCF 23.4 M€ | tirages seuls 14.5 M€
```

*À vous.* Estimez une LGD par **segment** (garantie × objet) et comparez son erreur à celle des modèles : que concluez-vous sur l'intérêt de modèles plus compliqués ?

### Application 1.7 — Perte attendue IFRS 9 (section 1.5)

**Objectif.** Calculer les étapes et la perte attendue d'un portefeuille, vérifier à la main un prêt, puis mesurer la sensibilité aux règles de basculement et aux scénarios.

**Étape 1 — étapes et perte attendue par étape.**

```python
pf = pd.read_csv("donnees/portefeuille_ifrs9.csv")
pf["etape"] = O.etape_ifrs9(pf); pf["ecl"] = O.ecl_ifrs9(pf, pf["etape"].values)
t = pf.groupby("etape").agg(prets=("ead", "size"), ead_M=("ead", lambda s: s.sum() / 1e6), ecl_M=("ecl", lambda s: s.sum() / 1e6))
t["couverture_%"] = 100 * t["ecl_M"] / t["ead_M"]
print(t.round(2).to_string()); print("ECL totale (M€) :", round(t["ecl_M"].sum(), 2))
```
<!--sortie-->
```text
       prets   ead_M  ecl_M  couverture_%
etape                                    
1      16607  251.65   2.92          1.16
2       2923   43.43   1.78          4.09
3        470    7.32   2.89         39.48
ECL totale (M€) : 7.59
```

**Étape 2 — vérifier un prêt à la main.** Prenons un prêt d'étape 2 et recalculons sa perte sur la durée de vie : somme sur les années $t$ de $(1-h)^{t-1}h\times\text{LGD}\times\text{EAD}_t/(1+r)^{t-0{,}5}$, avec $\text{EAD}_t=\text{EAD}\,(1-(t-0{,}5)/T)$ et un prorata pour la dernière année.

```python
p1 = pf[pf["etape"] == 2].iloc[0]
h, lgd, E, r, T = p1["pd_actuelle"], p1["lgd_estimee"], p1["ead"], p1["taux_effectif"], p1["maturite_residuelle"]
tot = 0.0
for t_ in range(1, int(np.ceil(T)) + 1):
    frac = min(1, T - (t_ - 1)); e_t = E * max(0, 1 - (t_ - 0.5) / T)
    tot += (1 - h) ** (t_ - 1) * h * frac * lgd * e_t / (1 + r) ** (t_ - 0.5)
print("à la main :", round(tot, 2), "| fonction :", round(float(p1["ecl"]), 2), "| (h, LGD, EAD, r, T) =", (h, lgd, E, r, T))
```
<!--sortie-->
```text
à la main : 49.18 | fonction : 49.18 | (h, LGD, EAD, r, T) = (np.float64(0.04207), np.float64(0.243), np.float64(7610.0), np.float64(0.0342), np.float64(1.4))
```

**Étape 3 — sensibilité au seuil de hausse sensible du risque.**

```python
lignes = []
for seuil in (2.0, 2.5, 3.0, 4.0):
    et = O.etape_ifrs9(pf, seuil_ratio=seuil)
    lignes.append((seuil, int((et == 2).sum()), O.ecl_ifrs9(pf, et).sum() / 1e6))
print(pd.DataFrame(lignes, columns=["seuil du ratio de PD", "prêts en étape 2", "ECL (M€)"]).round(2).to_string(index=False))
```
<!--sortie-->
```text
 seuil du ratio de PD  prêts en étape 2  ECL (M€)
                  2.0              4431      7.90
                  2.5              2923      7.59
                  3.0              2174      7.40
                  4.0              1489      7.23
```

**Étape 4 — scénarios.** On traduit trois scénarios macroéconomiques en multiplicateurs de PD par une régression du logit du taux de défaut sur la conjoncture (historique de 80 trimestres).

```python
mac = pd.read_csv("donnees/taux_defaut_macro.csv"); mac["logit"] = np.log(mac["taux_defaut"] / (1 - mac["taux_defaut"]))
mod = sm.OLS(mac["logit"], sm.add_constant(mac[["croissance_pib", "chomage", "variation_immo"]])).fit()
sc = {"central": (1.4, 8.2, 0.6), "défavorable": (-1.0, 9.5, -2.5), "favorable": (2.4, 7.4, 2.5)}; poids = {"central": .5, "défavorable": .3, "favorable": .2}
taux = {k: 1 / (1 + np.exp(-(mod.params["const"] + v[0] * mod.params["croissance_pib"] + v[1] * mod.params["chomage"] + v[2] * mod.params["variation_immo"]))) for k, v in sc.items()}
ecl = {k: O.ecl_ifrs9(pf, pf["etape"].values, mult=taux[k] / taux["central"]).sum() / 1e6 for k in sc}
print({k: round(100 * v, 2) for k, v in taux.items()}, {k: round(v, 2) for k, v in ecl.items()})
print("ECL pondérée :", round(sum(poids[k] * ecl[k] for k in sc), 2), "M€")
```
<!--sortie-->
```text
{'central': np.float64(2.61), 'défavorable': np.float64(10.51), 'favorable': np.float64(1.29)} {'central': np.float64(7.59), 'défavorable': np.float64(19.89), 'favorable': np.float64(5.27)}
ECL pondérée : 10.82 M€
```

*À vous.* Que devient l'ECL pondérée avec des poids 40 / 40 / 20 ? Et si le scénario défavorable fait basculer en étape 2 tous les prêts dont le retard dépasse 15 jours (utilisez `retard_2=15`) ?

### Application 1.8 — Matrice de migration (section 1.6)

**Objectif.** Estimer la matrice de transition, mesurer son incertitude, voir l'effet de la conjoncture, calculer des PD à plusieurs années et vérifier par simulation.

**Étape 1 — les effectifs et la matrice par cohortes.**

```python
panel = pd.read_csv("donnees/notations_panel.csv"); P_vrai = donnees5.matrice_vraie()
N = O.compter_transitions(panel); M = O.matrice_cohortes(N)
print(pd.DataFrame(N, index=range(1, 8), columns=["sortie"] + list(range(1, 8)) + ["défaut"]).to_string())
print("PD estimée (%) :", np.round(100 * M[:, 7], 2), "\nPD vraie   (%) :", np.round(100 * P_vrai[:, 7], 2))
```
<!--sortie-->
```text
   sortie     1     2     3     4     5     6    7  défaut
1      96  2150   205    29     1     2     0    0       1
2     280   254  5669   447    91    31    16    6       6
3     404    55   605  8401   625   174    46   26      23
4     390    26    91   653  7770   650   163   75      55
5     215     2     8    56   416  4179   439  141     109
6     115     0     5     3    44   174  1977  279     186
7      37     0     0     0     5    20    87  702     387
PD estimée (%) : [ 0.04  0.09  0.23  0.58  2.04  6.97 32.22] 
PD vraie   (%) : [ 0.1  0.1  0.2  0.5  1.7  5.9 28.3]
```

**Étape 2 — un intervalle de confiance par bootstrap d'emprunteurs.**

```python
C = np.zeros((5000, 7, 9), dtype=np.int32)
np.add.at(C, (panel["id_emprunteur"].values - 1, panel["note_debut"].values - 1, panel["note_fin"].values), 1)
rng = np.random.default_rng(0)
sim = []
for _ in range(200):
    Nb = C[rng.integers(0, 5000, 5000)].sum(axis=0); sim.append((Nb[:, 8] / Nb[:, 1:].sum(axis=1)))
lo, hi = np.percentile(sim, [2.5, 97.5], axis=0)
print(pd.DataFrame({"PD estimée": M[:, 7], "bas": lo, "haut": hi}, index=range(1, 8)).round(4).to_string())
```
<!--sortie-->
```text
   PD estimée     bas    haut
1      0.0004  0.0000  0.0013
2      0.0009  0.0003  0.0020
3      0.0023  0.0015  0.0033
4      0.0058  0.0044  0.0074
5      0.0204  0.0167  0.0245
6      0.0697  0.0614  0.0800
7      0.3222  0.2941  0.3462
```

**Étape 3 — calme contre récession.**

```python
calme = O.matrice_cohortes(O.compter_transitions(panel, [0, 1, 2, 3, 8, 9])); rec = O.matrice_cohortes(O.compter_transitions(panel, [5, 6]))
print(pd.DataFrame({"PD calme (%)": 100 * calme[:, 7], "PD récession (%)": 100 * rec[:, 7]}, index=range(1, 8)).round(2).to_string())
```
<!--sortie-->
```text
   PD calme (%)  PD récession (%)
1          0.07              0.00
2          0.08              0.08
3          0.13              0.49
4          0.45              1.11
5          1.39              4.71
6          4.95             14.07
7         24.49             51.55
```

**Étape 4 — PD à 5 ans, par puissance de matrice et par simulation.** On simule 20 000 trajectoires par note de départ avec la matrice estimée et l'on compte les défauts avant cinq ans.

```python
M_abs = np.vstack([M, np.r_[np.zeros(7), 1.0]]); PD_5 = np.linalg.matrix_power(M_abs, 5)[:7, 7]
rng = np.random.default_rng(1); cum = np.cumsum(M_abs, axis=1); sim5 = []
for note in range(7):
    etat = np.full(20000, note)
    for _ in range(5):
        etat = (rng.random(20000)[:, None] > cum[etat]).sum(axis=1).clip(max=7)
    sim5.append((etat == 7).mean())
print(pd.DataFrame({"puissance de matrice": PD_5, "simulation": sim5}, index=range(1, 8)).round(4).to_string())
```
<!--sortie-->
```text
   puissance de matrice  simulation
1                0.0037      0.0028
2                0.0120      0.0118
3                0.0270      0.0282
4                0.0649      0.0663
5                0.1696      0.1699
6                0.3926      0.3944
7                0.7648      0.7607
```

*À vous.* Estimez la matrice sur les **cinq premières années** seulement, puis prédisez les défauts observés sur les cinq dernières : à quel point la prédiction est-elle trompée par la conjoncture ?

## Exercices

### Exercice 1.1 ⭐ — Échelle de points (section 1.1)
Un établissement fixe un score de **650 points pour une cote de 30 contre 1** et un **PDO de 40**. (a) Calculez le facteur et le décalage. (b) Quel score correspond à une cote de 120 contre 1 ? (c) Quelle probabilité de défaut correspond à un score de 600 ?

### Exercice 1.2 ⭐ — WOE et IV à la main (section 1.1.4)
Une variable a trois classes. Classe A : 4 000 bons, 40 mauvais ; classe B : 5 000 bons, 150 mauvais ; classe C : 1 000 bons, 110 mauvais. Calculez le WOE de chaque classe et l'IV de la variable (sans lissage). Que concluez-vous sur la lecture usuelle de l'IV ?

### Exercice 1.3 ⭐⭐ — Fenêtres et fuite d'information (section 1.1.2)
(a) Classez en « autorisée » ou « interdite » pour un score d'octroi : l'âge à la demande, le nombre de retards du prêt dans ses six premiers mois, le revenu déclaré, le nombre d'incidents de paiement des douze mois précédant la demande, le solde du compte six mois après l'octroi, l'objet du prêt. (b) Un prêt est observé six mois seulement au lieu de douze : si le risque de défaut est réparti uniformément sur les douze mois, quel taux de défaut mesure-t-on ? Vérifiez par simulation.

### Exercice 1.4 ⭐ — Perte attendue et taux minimal (section 1.5)
Un prêt de 8 000 € a une PD de 4 % à un an et une LGD de 50 %. (a) Quelle est sa perte attendue sur l'année ? (b) De combien de points de taux doit-on majorer le coût de refinancement pour la couvrir, à exposition constante ? (c) Si la LGD réelle est de 61 % (prêt sans garantie), que devient la majoration ?

### Exercice 1.5 ⭐⭐ — Contraintes de monotonie (section 1.2.4)
Entraînez un boosting libre et un boosting monotone (voir l'application 1.3) puis calculez, sur une grille de taux d'endettement de 0,05 à 0,95, la probabilité prédite pour un dossier « médian » en ne faisant varier que ce taux. Comptez les **inversions** (endroits où la probabilité baisse quand le taux monte) pour chaque modèle.

### Exercice 1.6 ⭐ — AUC par comptage (section 1.3.1)
Huit dossiers, avec leur score de risque et leur issue : (0,95 ; M), (0,85 ; B), (0,70 ; M), (0,65 ; B), (0,55 ; M), (0,40 ; B), (0,30 ; B), (0,10 ; B) (M = mauvais, B = bon). Calculez l'AUC par comptage des paires, le Gini, puis le KS à la main.

### Exercice 1.7 ⭐⭐ — Le Gini ne dépend pas de la proportion de mauvais (section 1.3.2)
Simulez des scores gaussiens (moyenne 0 pour les bons, 1 pour les mauvais, écart-type 1) avec une proportion de mauvais $\pi=2\ \%$ puis $30\ \%$. Calculez l'AUC, puis l'accuracy ratio par l'aire sous la CAP, et comparez avec $2\,\text{AUC}-1$.

### Exercice 1.8 ⭐⭐ — PSI à la main (section 1.3.6)
La répartition du score en quatre classes était (30 %, 30 %, 25 %, 15 %) au développement et est de (20 %, 25 %, 30 %, 25 %) aujourd'hui. Calculez le PSI et interprétez-le avec les repères usuels. Quelle classe contribue le plus ?

### Exercice 1.9 ⭐ — IV avec une classe sans mauvais (section 1.4.4)
Une classe contient 300 bons et 0 mauvais, l'échantillon compte 20 000 bons et 400 mauvais. Que vaut son WOE sans lissage ? Avec un lissage d'une demi-observation par classe (la variable a cinq classes) ? Quelle règle adopter ?

### Exercice 1.10 ⭐⭐ — IV d'une variable de bruit (section 1.4.2)
Répétez 30 fois l'expérience d'une variable de pur bruit découpée en 50 classes d'effectifs égaux. Donnez la moyenne et le maximum de l'IV de développement. Proposez, à partir de ce résultat, un **seuil** en dessous duquel l'IV d'une variable à 50 classes ne prouve rien.

### Exercice 1.11 ⭐ — Perte attendue d'un prêt (section 1.5.4)
Un prêt de 20 000 € a une PD annuelle de 2 %, une LGD de 40 %, une maturité résiduelle de 3 ans, un taux effectif de 5 %. (a) Perte attendue à 12 mois (étape 1) avec actualisation à mi-année. (b) Perte sur la durée de vie (étape 2) avec une exposition qui s'amortit linéairement ($\text{EAD}_t=\text{EAD}\,(1-(t-0{,}5)/T)$) et une actualisation à mi-année. (c) Rapport des deux.

### Exercice 1.12 ⭐⭐ — L'effet de falaise (section 1.5.4)
Sur `portefeuille_ifrs9.csv`, faites varier le **seuil de retard de l'étape 2** (15, 30, 45, 60 jours, avec le ratio de PD à 2,5) et mesurez le nombre de prêts en étape 2 et la perte attendue totale. Quelle est la sensibilité de la provision à cette convention ?

### Exercice 1.13 ⭐ — Une matrice à trois états (section 1.6.4)
Trois états : A (sain), B (surveillé), D (défaut absorbant). Annuellement : A→A 0,90, A→B 0,08, A→D 0,02 ; B→A 0,10, B→B 0,75, B→D 0,15. Calculez à la main la PD à 2 ans puis à 3 ans de A et de B, et vérifiez avec `numpy`.

### Exercice 1.14 ⭐⭐⭐ — Chapman–Kolmogorov et conjoncture (section 1.6.5)
Sur `notations_panel.csv`, comparez, pour chaque note de départ, la probabilité observée de défaut **à deux ans** (note en début d'année $t$, défaut avant la fin de $t+1$, observé directement sur les emprunteurs suivis deux années) à celle que donne $P^2$ de la matrice estimée. Pourquoi l'écart n'est-il pas nul ? Recommencez en calculant $P^2$ avec les matrices *calme* et *récession* séparées et en pondérant par la fréquence de ces années.

## Corrigés

### Corrigé 1.1
(a) $\text{facteur}=40/\ln2=57{,}71$ ; $\text{décalage}=650-57{,}71\times\ln30=650-196{,}29=453{,}71$. (b) $453{,}71+57{,}71\times\ln120=453{,}71+276{,}28=730$ : on le vérifie sans calcul, puisque $120=30\times4$ est deux doublements de la cote, soit $650+2\times40=730$. (c) $\text{cote}=\exp((600-453{,}71)/57{,}71)=\exp(2{,}535)=12{,}6$ ; $\text{PD}=1/(1+12{,}6)=7{,}3\ \%$.

```python
f = 40 / np.log(2); d = 650 - f * np.log(30)
print(round(f, 2), round(d, 2), round(d + f * np.log(120), 1), round(1 / (1 + np.exp((600 - d) / f)), 4))
```
<!--sortie-->
```text
57.71 453.72 730.0 0.0735
```

### Corrigé 1.2
Totaux : bons 10 000, mauvais 300. Classe A : $g=0{,}40$, $b=40/300=0{,}1333$, WOE $=\ln(0{,}40/0{,}1333)=\ln3=1{,}099$. Classe B : $g=0{,}50$, $b=0{,}50$, WOE $=0$. Classe C : $g=0{,}10$, $b=110/300=0{,}3667$, WOE $=\ln(0{,}2727)=-1{,}299$. IV $=(0{,}40-0{,}1333)\times1{,}099+0+(0{,}10-0{,}3667)\times(-1{,}299)=0{,}293+0{,}346=0{,}639$. Au-dessus de 0,5 : lecture « suspect » ou, ici, simplement une variable **très** discriminante ; on cherche d'abord si elle est connue à la date de la demande.

```python
n = np.array([[4000, 40], [5000, 150], [1000, 110]]); g = n[:, 0] / n[:, 0].sum(); b = n[:, 1] / n[:, 1].sum()
print(np.round(np.log(g / b), 3), round(float(((g - b) * np.log(g / b)).sum()), 3))
```
<!--sortie-->
```text
[ 1.099  0.    -1.299] 0.639
```

### Corrigé 1.3
(a) **Autorisées** : âge à la demande, revenu déclaré, incidents des douze mois **précédant** la demande, objet. **Interdites** : retards du prêt dans ses six premiers mois et solde du compte six mois après l'octroi (postérieurs à la demande). (b) Si le défaut est réparti uniformément sur les douze mois, observer six mois ne révèle que **la moitié** des défauts : on mesure environ $0{,}5\times$ le taux vrai ; avec un taux de 6 %, on lit 3 %, et l'on prend pour « bons » des prêts qui feront défaut ensuite.

```python
rng = np.random.default_rng(0); n = 200000
instant = np.where(rng.random(n) < 0.06, rng.uniform(0, 12, n), np.inf)           # date du défaut (mois), ∞ = pas de défaut
print("taux sur 12 mois :", round(float((instant <= 12).mean()), 4), " taux sur 6 mois :", round(float((instant <= 6).mean()), 4))
```
<!--sortie-->
```text
taux sur 12 mois : 0.0598  taux sur 6 mois : 0.0299
```

### Corrigé 1.4
(a) $0{,}04\times0{,}5\times8\,000=160$ €. (b) $160/8\,000=2\ \%$ de l'exposition : une majoration de **2 points** de taux (à exposition constante sur l'année). (c) Avec une LGD de 61 % : $0{,}04\times0{,}61=2{,}44\ \%$, soit 0,44 point de plus : utiliser la LGD moyenne de 50 % sous-tarifie les prêts sans garantie.

### Corrigé 1.5
```python
d_med = {c: (te[c].median() if pd.api.types.is_numeric_dtype(te[c]) else te[c].mode()[0]) for c in te.columns if c not in ("id_credit", "defaut_12m")}
grille_dti = np.arange(0.05, 0.96, 0.01)
ref = pd.DataFrame([d_med] * len(grille_dti)); ref["taux_endettement"] = grille_dti
signes = {"taux_endettement": 1, "nb_incidents_12m": 1, "revenu_annuel": -1, "anciennete_emploi": -1, "anciennete_relation": -1}
def brut(d_):
    X = d_[["age", "revenu_annuel", "anciennete_emploi", "montant", "duree_mois", "taux_endettement", "nb_incidents_12m", "anciennete_relation"]].copy()
    for k in ["revenu_annuel", "anciennete_emploi"]: X[k + "_manq"] = X[k].isna().astype(int)
    return pd.concat([X, pd.get_dummies(d_[["logement", "objet"]]).astype(int)], axis=1)
Xa = brut(tr); mc = [signes.get(c, 0) for c in Xa.columns]
par = dict(n_estimators=300, learning_rate=0.03, num_leaves=8, min_child_samples=200, subsample=0.8, subsample_freq=1, colsample_bytree=0.8, random_state=0, verbose=-1)
libre = lgb.LGBMClassifier(**par).fit(Xa, y_tr); mono = lgb.LGBMClassifier(monotone_constraints=mc, **par).fit(Xa, y_tr)
Xr = brut(ref).reindex(columns=Xa.columns, fill_value=0)
for nom, m in [("libre", libre), ("monotone", mono)]:
    p = m.predict_proba(Xr)[:, 1]
    print(nom, "inversions :", int((np.diff(p) < -1e-12).sum()), "sur", len(p) - 1, "pas ; plus forte baisse :", round(float(np.diff(p).min()), 5))
```
<!--sortie-->
```text
libre inversions : 7 sur 90 pas ; plus forte baisse : -0.00166
monotone inversions : 0 sur 90 pas ; plus forte baisse : 0.0
```
Le boosting monotone n'a **aucune inversion** par construction ; le libre en a généralement quelques-unes : de petites baisses locales, accidents d'échantillon que l'on ne saurait pas justifier devant un client ou un auditeur.

### Corrigé 1.6
Mauvais : 0,95 ; 0,70 ; 0,55. Bons : 0,85 ; 0,65 ; 0,40 ; 0,30 ; 0,10. Paires (3 × 5 = 15) : 0,95 bat les 5 bons ; 0,70 bat 0,65, 0,40, 0,30, 0,10, soit 4 (pas 0,85) ; 0,55 bat 0,40, 0,30, 0,10, soit 3. Total $5+4+3=12$ sur 15 : AUC $=0{,}8$, Gini $=0{,}6$. KS : on classe par score décroissant ; TPR et FPR cumulés : après 0,95 : (1/3 ; 0) ; 0,85 : (1/3 ; 1/5) ; 0,70 : (2/3 ; 1/5) ; 0,65 : (2/3 ; 2/5) ; 0,55 : (1 ; 2/5) ; 0,40 : (1 ; 3/5) ; … La plus grande différence TPR − FPR est $1-\frac25=0{,}6$ (après 0,55). KS $=0{,}6$.

```python
y = np.array([1, 0, 1, 0, 1, 0, 0, 0]); s = np.array([.95, .85, .70, .65, .55, .40, .30, .10])
print(O.auc(y, s), O.gini(y, s), O.ks(y, s))
```
<!--sortie-->
```text
0.8 0.6000000000000001 0.6
```

### Corrigé 1.7
```python
from sklearn.metrics import roc_auc_score
rng = np.random.default_rng(0)
for pi in (0.02, 0.30):
    n = 400000; y = (rng.random(n) < pi).astype(int); s = rng.normal(y, 1.0)
    o = np.argsort(-s); cap = np.cumsum(y[o]) / y.sum(); x = np.arange(1, n + 1) / n
    aire = np.trapezoid(cap, x); ar = (aire - 0.5) / ((1 - y.mean() / 2) - 0.5)
    print(f"π = {y.mean():.3f}  AUC {roc_auc_score(y, s):.4f}  2·AUC−1 {2 * roc_auc_score(y, s) - 1:.4f}  accuracy ratio {ar:.4f}")
```
<!--sortie-->
```text
π = 0.020  AUC 0.7600  2·AUC−1 0.5201  accuracy ratio 0.5201
π = 0.300  AUC 0.7587  2·AUC−1 0.5174  accuracy ratio 0.5174
```
Les deux accuracy ratios coïncident avec $2\,\text{AUC}-1$ (≈ 0,52, car l'AUC théorique vaut $\Phi(1/\sqrt2)=0{,}760$), **quelle que soit la proportion de mauvais** : c'est la démonstration du livre, vérifiée.

### Corrigé 1.8
Contributions $(p_a-p_d)\ln(p_a/p_d)$ : classe 1 : $(0{,}20-0{,}30)\ln(0{,}20/0{,}30)=(-0{,}10)(-0{,}405)=0{,}0405$ ; classe 2 : $(-0{,}05)\ln(0{,}25/0{,}30)=(-0{,}05)(-0{,}182)=0{,}0091$ ; classe 3 : $(0{,}05)\ln(0{,}30/0{,}25)=0{,}05\times0{,}182=0{,}0091$ ; classe 4 : $(0{,}10)\ln(0{,}25/0{,}15)=0{,}10\times0{,}511=0{,}0511$. PSI $=0{,}1098$ : au-dessus de 0,10, un changement **à examiner**. La classe 4 contribue le plus (0,051, près de la moitié) : sa part est passée de 15 % à 25 %, dix points de population qui ont changé de classe.

```python
pa, pd_ = np.array([.20, .25, .30, .25]), np.array([.30, .30, .25, .15])
c = (pa - pd_) * np.log(pa / pd_); print(np.round(c, 4), round(float(c.sum()), 4))
```
<!--sortie-->
```text
[0.0405 0.0091 0.0091 0.0511] 0.1099
```

### Corrigé 1.9
Sans lissage : $b_j=0$, $\text{WOE}=\ln(g_j/0)=+\infty$ : inutilisable (et l'IV est infini). Avec lissage : $g=(300+0{,}5)/(20\,000+0{,}5\times5)=0{,}015$ ; $b=0{,}5/(400+2{,}5)=0{,}00124$ ; $\text{WOE}=\ln(0{,}015/0{,}00124)=2{,}49$ : fini, mais **très grand** et fondé sur 300 observations sans aucun mauvais. Règle : lisser, mais surtout **fusionner** une classe sans mauvais avec sa voisine (ou la plafonner), parce que l'absence de mauvais dans un échantillon fini ne prouve pas qu'il n'y en aura jamais (règle des « trois sur n » : zéro défaut sur 300 est compatible avec un taux vrai jusqu'à 1 %).

```python
g, b = 300.5 / 20002.5, 0.5 / 402.5; print(round(g, 4), round(b, 5), round(float(np.log(g / b)), 2))
```
<!--sortie-->
```text
0.015 0.00124 2.49
```

### Corrigé 1.10
```python
rng = np.random.default_rng(0); ivs = []
for _ in range(30):
    x = rng.normal(size=len(tr)); q = np.unique(np.quantile(x, np.linspace(0, 1, 51)[1:-1])); i = np.searchsorted(q, x, side="right")
    n = np.bincount(i, minlength=len(q) + 1); m = np.bincount(i, weights=y_tr, minlength=len(q) + 1); ivs.append(O.iv_partition(n, m))
print("IV du bruit à 50 classes : moyenne", round(float(np.mean(ivs)), 4), " maximum", round(float(np.max(ivs)), 4))
```
<!--sortie-->
```text
IV du bruit à 50 classes : moyenne 0.0299  maximum 0.0417
```
L'IV de développement d'un pur bruit à 50 classes est en moyenne de **0,030**, avec un maximum de 0,042 sur 30 répétitions : une variable à 50 classes dont l'IV est de 0,03 ne prouve **rien**. Un seuil raisonnable est de l'ordre du maximum observé sur du bruit (≈ 0,04 à 0,05), ce que justifie un ordre de grandeur : l'IV d'un bruit à $k$ classes vaut environ $(k-1)\,(1/M+1/B)$, soit ici $49\times(1/1\,671+1/26\,329)\approx0{,}03$.

### Corrigé 1.11
(a) $0{,}02\times0{,}40\times20\,000/1{,}05^{0{,}5}=160/1{,}0247=156{,}15$ €. (b) $h=0{,}02$ ; $\text{EAD}_1=20\,000(1-0{,}5/3)=16\,667$, $\text{EAD}_2=10\,000$, $\text{EAD}_3=3\,333$ ; probabilités marginales $0{,}02$, $0{,}0196$, $0{,}019208$ ; facteurs d'actualisation $1{,}05^{-0{,}5}=0{,}97590$, $1{,}05^{-1{,}5}=0{,}92943$, $1{,}05^{-2{,}5}=0{,}88517$. Termes : $0{,}02\times0{,}4\times16\,667\times0{,}9759=130{,}12$ ; $0{,}0196\times0{,}4\times10\,000\times0{,}92943=72{,}86$ ; $0{,}019208\times0{,}4\times3\,333\times0{,}88517=22{,}67$. Somme $\approx225{,}65$ €. (c) Rapport $225{,}65/156{,}15=1{,}45$.

```python
d1 = pd.DataFrame({"pd_actuelle": [0.02], "lgd_estimee": [0.40], "ead": [20000.0], "taux_effectif": [0.05], "maturite_residuelle": [3.0]})
print(O.ecl_ifrs9(d1, np.array([1])), O.ecl_ifrs9(d1, np.array([2])))
```
<!--sortie-->
```text
[156.14401167] [225.65701242]
```

### Corrigé 1.12
```python
pf = pd.read_csv("donnees/portefeuille_ifrs9.csv"); lignes = []
for jours in (15, 30, 45, 60):
    et = O.etape_ifrs9(pf, retard_2=jours); lignes.append((jours, int((et == 2).sum()), O.ecl_ifrs9(pf, et).sum() / 1e6))
print(pd.DataFrame(lignes, columns=["retard (jours)", "prêts en étape 2", "ECL (M€)"]).round(2).to_string(index=False))
```
<!--sortie-->
```text
 retard (jours)  prêts en étape 2  ECL (M€)
             15              3195      7.62
             30              2923      7.59
             45              2768      7.57
             60              2618      7.55
```
Passer de 30 à 15 jours fait entrer davantage de prêts en étape 2, donc en provision sur la vie : la perte attendue **monte** de 0,4 % (7,62 contre 7,59 M€), et elle baisse de 0,5 % en passant de 30 à 60 jours (7,55 M€). La sensibilité est **faible** (moins de 1 %) parce que les retards de 15 à 60 jours concernent peu de prêts, et parce que d'autres critères (ratio de PD, restructuration) alimentent déjà l'étape 2 ; elle est bien plus forte pour le **seuil du ratio de PD** (application 1.7, étape 3 : de 7,23 à 7,90 M€ entre les seuils de 4 et 2). La conclusion générale reste : la provision dépend de **conventions** de basculement qu'il faut documenter et surveiller.

### Corrigé 1.13
Matrice $P$ (A, B, D) : [[0,90 ; 0,08 ; 0,02], [0,10 ; 0,75 ; 0,15], [0 ; 0 ; 1]]. À 2 ans : $P^2_{A\to D}=0{,}90\times0{,}02+0{,}08\times0{,}15+0{,}02\times1=0{,}018+0{,}012+0{,}02=0{,}050$ ; $P^2_{B\to D}=0{,}10\times0{,}02+0{,}75\times0{,}15+0{,}15=0{,}002+0{,}1125+0{,}15=0{,}2645$. $P^2_{A\to A}=0{,}90^2+0{,}08\times0{,}10=0{,}818$ ; $P^2_{A\to B}=0{,}90\times0{,}08+0{,}08\times0{,}75=0{,}132$. À 3 ans : $P^3_{A\to D}=0{,}818\times0{,}02+0{,}132\times0{,}15+0{,}050=0{,}01636+0{,}0198+0{,}050=0{,}0862$ ; $P^2_{B\to A}=0{,}10\times0{,}90+0{,}75\times0{,}10=0{,}165$, $P^2_{B\to B}=0{,}10\times0{,}08+0{,}75^2=0{,}5705$ ; $P^3_{B\to D}=0{,}165\times0{,}02+0{,}5705\times0{,}15+0{,}2645=0{,}0033+0{,}0856+0{,}2645=0{,}3534$.

```python
P = np.array([[.90, .08, .02], [.10, .75, .15], [0, 0, 1.0]])
for n in (2, 3): print(n, np.round(np.linalg.matrix_power(P, n)[:2, 2], 4))
```
<!--sortie-->
```text
2 [0.05   0.2645]
3 [0.0862 0.3534]
```

### Corrigé 1.14
```python
panel = pd.read_csv("donnees/notations_panel.csv"); N = O.compter_transitions(panel); M = O.matrice_cohortes(N)
absorbe = lambda M_: np.vstack([M_, np.r_[np.zeros(7), 1.0]])
P2 = np.linalg.matrix_power(absorbe(M), 2)[:7, 7]
calme = absorbe(O.matrice_cohortes(O.compter_transitions(panel, [0, 1, 2, 3, 4, 7, 8, 9]))); rec = absorbe(O.matrice_cohortes(O.compter_transitions(panel, [5, 6])))
regime = lambda t: rec if t in (5, 6) else calme                                      # matrice de l'année t selon le régime
a = panel.set_index(["id_emprunteur", "annee"]); lignes = []
for k in range(1, 8):
    dep = panel[(panel["note_debut"] == k) & (panel["annee"] <= 8) & (panel["note_fin"] > 0)]       # notés k en t, non sortis en fin de t
    suiv = a.reindex(list(zip(dep["id_emprunteur"], dep["annee"] + 1)))
    obs = ((dep["note_fin"].values == 8) | (suiv["note_fin"].values == 8)).mean()                    # défaut en t ou en t+1
    w = dep.groupby("annee").size()
    p_reg = sum(w[t] * (regime(t) @ regime(t + 1))[k - 1, 7] for t in w.index) / w.sum()
    lignes.append((k, len(dep), obs, P2[k - 1], p_reg))
print(pd.DataFrame(lignes, columns=["note", "n", "observé", "P² (matrice moyenne)", "P² par régime"]).round(4).to_string(index=False))
```
<!--sortie-->
```text
 note    n  observé  P² (matrice moyenne)  P² par régime
    1 2163   0.0014                0.0009         0.0009
    2 6022   0.0033                0.0025         0.0026
    3 9304   0.0060                0.0062         0.0065
    4 8860   0.0157                0.0159         0.0164
    5 4960   0.0512                0.0510         0.0528
    6 2426   0.1645                0.1565         0.1612
    7 1084   0.5148                0.5160         0.5162
```
La probabilité de défaut à deux ans **observée** est très proche de $P^2$ pour toutes les notes (par exemple 0,0512 contre 0,0510 pour la note 5) : la relation de **Chapman–Kolmogorov** $P^{(2)}=P\cdot P$ est vérifiée, ce qui est cohérent avec des données simulées par une chaîne de Markov. Les écarts qui subsistent sont petits et viennent de deux sources : le bruit d'échantillonnage (surtout pour les notes extrêmes, 1 084 observations pour la note 7) et le fait que la matrice moyenne ne tient pas compte de **l'ordre des années** : la colonne « par régime », qui utilise la matrice de récession pour les années 5 et 6 et pondère par les effectifs réellement observés, rapproche la prédiction de l'observation pour la note 6 (0,1612 contre 0,1645 observé, au lieu de 0,1565). Sur des données réelles, ce test est un bon moyen de repérer un effet d'élan ou une dépendance à la durée dans la note : un $P^2$ nettement inférieur à l'observé signalerait une persistance que le modèle ignore.

## Pistes pour les « À vous » des applications

- **1.1** Un score de base différent change tous les points, mais **pas le rang** : l'AUC est identique (c'est une transformation affine de la log-cote). Retirer les trois variables d'IV le plus faible (objet, durée, ancienneté de la relation) coûte 0,006 d'AUC (0,765 contre 0,771) : la carte est plus courte pour une perte modeste, à comparer à l'intervalle de l'AUC (± 0,02).
- **1.2** Le coefficient 2 rapproche la PD annoncée du défaut réel (0,049 contre 0,060), le coefficient 1 ne corrige presque rien : mais on ne peut le choisir ainsi qu'**ici**, parce que nous connaissons l'issue des refusés. En pratique, le coefficient est un jugement, validé par des données externes ou une expérience d'acceptation.
- **1.3** (a) Une régression logistique sur la sortie du boosting, ajustée sur 30 % du développement mis de côté, fait baisser le Brier très légèrement (0,0504 contre 0,0502) : ce boosting est déjà presque calibré. (b) Une contrainte de monotonie sur l'âge est une **erreur** : la vérité est en U ; le modèle ne pourrait plus représenter le sur-risque des plus de 65 ans.
- **1.4** Avec une perte de 6 000 € par défaut, le seuil optimal **monte** (on devient plus sélectif) : de 556 points à 560 (et à 570 pour une perte de 8 000 €) sur une grille de pas 2 ; avec le pas de 10 de l'étape 1, la différence est invisible. Le profit au seuil optimal baisse de 2 958 à 2 337 k€.
- **1.5** Pour le revenu, la fusion monotone ne coûte presque rien (AUC 0,7709 contre 0,7712, neuf classes) ; pour le taux d'endettement, elle coûte 0,004 (0,767, sept classes) : la monotonie y est vraie, mais la fusion regroupe des classes de risques voisins et perd un peu de finesse.
- **1.6** Les LGD par segment (garantie × objet) font aussi bien que les modèles : l'erreur ne baisse pas, ce qui confirme que la moyenne par segment est ce que l'on peut prédire.
- **1.7** Avec les poids 40 / 40 / 20, l'ECL pondérée passe de 10,8 à 12,0 M€ (le scénario défavorable pèse davantage). Un seuil de retard de 15 jours ajoute 272 prêts en étape 2 (3 195 contre 2 923) mais l'ECL du scénario défavorable ne bouge que de 0,07 M€ (19,96 contre 19,89).
- **1.8** Estimée sur les cinq premières années (0 à 4, sans récession), la matrice prédit 1,8 % de défauts pour les années 5 et 6, contre 3,9 % observés : elle **sous-estime de plus de moitié** : la conjoncture ne se laisse pas prévoir par une matrice moyenne.
