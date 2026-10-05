# Chapitre 5 : Évaluation, calibration et interprétabilité — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 5 du livre. Les **applications** refont pas à pas, sur les données de la boutique et sur le jeu réel de crédit, les calculs que le livre n'a fait que résumer (métriques, seuils, calibration, importances, SHAP, équité, prédiction conforme) ; les **exercices** se travaillent d'abord à la main, et leurs **corrigés** viennent à la fin. Chaque exercice indique la section du livre qu'il met en pratique.

## Préparation

Une seule cellule charge les bibliothèques et les données, répartit les clients en trois jeux (entraînement 7 200, calibration 2 400, test 2 400, stratifiés sur `churn_90j`) et ajuste les trois modèles du chapitre : régression logistique, forêt aléatoire et gradient boosting. Les applications suivantes en réutilisent les noms : `P` (probabilités de test des trois modèles), `p` (celles du boosting), `yt` (les départs observés sur le jeu de test).


```python
import numpy as np, pandas as pd, warnings, math, itertools
warnings.filterwarnings("ignore")
import matplotlib; matplotlib.use("Agg"); import matplotlib.pyplot as plt
from sklearn import metrics as M
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import HistGradientBoostingClassifier, RandomForestClassifier
from sklearn.preprocessing import StandardScaler

c = pd.read_csv("donnees/clients_ml.csv")
X = pd.get_dummies(c.drop(columns=["churn_90j", "depense_6m", "segment_vrai", "commandes_apres_cible", "id_client"]),
                   columns=["ville", "canal_acquisition", "appareil", "categorie_preferee"], dtype=float)
X["panier_manquant"] = c["panier_moyen"].isna().astype(float); X["satisfaction_manquante"] = c["satisfaction_moy"].isna().astype(float)
y = c["churn_90j"]
Xa, Xte, ya, yte = train_test_split(X, y, test_size=0.2, random_state=0, stratify=y)
Xtr, Xca, ytr, yca = train_test_split(Xa, ya, test_size=0.25, random_state=0, stratify=ya)
med = Xtr.median(); Xtr, Xca, Xte = Xtr.fillna(med), Xca.fillna(med), Xte.fillna(med)       # médianes de l'entraînement seul
sc = StandardScaler().fit(Xtr)
lr = LogisticRegression(max_iter=3000).fit(sc.transform(Xtr), ytr)
rf = RandomForestClassifier(150, min_samples_leaf=5, random_state=0, n_jobs=1).fit(Xtr, ytr)
gb = HistGradientBoostingClassifier(random_state=0).fit(Xtr, ytr)
P = {"logistique": lr.predict_proba(sc.transform(Xte))[:, 1], "forêt": rf.predict_proba(Xte)[:, 1], "boosting": gb.predict_proba(Xte)[:, 1]}
yt = yte.to_numpy(); p = P["boosting"]
print(len(Xtr), len(Xca), len(Xte), round(yt.mean(), 3), {k: round(M.roc_auc_score(yt, v), 4) for k, v in P.items()})
```
<!--sortie-->
```text
7200 2400 2400 0.14 {'logistique': 0.8593, 'forêt': 0.8881, 'boosting': 0.8971}
```
Les AUC du chapitre (0,859 ; 0,888 ; 0,897) sont retrouvées : les découpages et les graines sont les mêmes que dans le livre.

## Applications

### Application 5.1 — Du score à la décision : seuils, coûts et gain

*Sections du livre : 5.1.2 à 5.1.7.* **Objectif** : transformer les probabilités du boosting en une décision de campagne, et vérifier jusqu'où la formule du seuil $t^\star=c/(sV)$ est fiable. Un contact coûte $c=5$ €, sauve un partant avec la probabilité $s=0{,}4$, et un client sauvé vaut $V=60$ €.

**Étape 1 — Le gain de la campagne pour quelques seuils.** La fonction `gain_net` additionne, pour les clients dont le score atteint le seuil, le gain attendu (`s * V` pour un partant) et retranche le coût de contact.


```python
def gain_net(score, t, c_contact=5.0, s=0.4, V=60.0):
    contacte = score >= t
    return float((s * V * yt[contacte]).sum() - c_contact * contacte.sum())

for t in [0.05, 0.1, 0.2, 0.3, 0.5]:
    yh = (p >= t).astype(int)
    print(f"t={t:.2f}  alertes={yh.sum():4d}  précision={M.precision_score(yt, yh):.3f}  rappel={M.recall_score(yt, yh):.3f}  gain={gain_net(p, t):7.1f} €")
```
<!--sortie-->
```text
t=0.05  alertes= 954  précision=0.322  rappel=0.911  gain= 2598.0 €
t=0.10  alertes= 692  précision=0.399  rappel=0.819  gain= 3164.0 €
t=0.20  alertes= 460  précision=0.517  rappel=0.706  gain= 3412.0 €
t=0.30  alertes= 350  précision=0.603  rappel=0.626  gain= 3314.0 €
t=0.50  alertes= 230  précision=0.709  rappel=0.484  gain= 2762.0 €
```
Parmi les cinq seuils essayés, le meilleur est 0,2 (3 412 €) ; le seuil habituel de 0,5 n'en rapporte que 2 762 €, parce qu'il ne détecte que 48 % des partants.

**Étape 2 — Le seuil optimal sur une grille fine.**


```python
grille = np.round(np.arange(0.02, 0.8, 0.01), 2)
g = np.array([gain_net(p, t) for t in grille])
print("seuil optimal :", grille[g.argmax()], "| gain :", round(g.max(), 1), "| seuil théorique c/(sV) :", round(5 / (0.4 * 60), 3))
```
<!--sortie-->
```text
seuil optimal : 0.18 | gain : 3473.0 | seuil théorique c/(sV) : 0.208
```
Le maximum observé est de 3 473 € au seuil 0,18. Le seuil théorique $5/24=0{,}208$ en donne 3 391 € : 82 € de moins (2,4 %), car le gain d'un jeu de 2 400 clients est bruité et la courbe est plate autour de l'optimum.

**Étape 3 — Sensibilité à l'économie du problème.** On fait varier la probabilité de succès $s$ et le coût de contact $c$, et l'on compare le seuil théorique au seuil optimal de la grille.


```python
lignes = []
for s in [0.2, 0.4, 0.6]:
    for cc in [2.0, 5.0, 10.0]:
        gg = np.array([gain_net(p, t, cc, s) for t in grille])
        lignes.append((s, cc, round(cc / (s * 60), 3), grille[gg.argmax()], round(gg.max(), 0)))
print(pd.DataFrame(lignes, columns=["succès s", "coût c", "seuil théorique", "seuil optimal (grille)", "gain max"]).to_string(index=False))
```
<!--sortie-->
```text
 succès s  coût c  seuil théorique  seuil optimal (grille)  gain max
      0.2     2.0            0.167                    0.12    1988.0
      0.2     5.0            0.417                    0.40     832.0
      0.2    10.0            0.833                    0.79      58.0
      0.4     2.0            0.083                    0.05    5460.0
      0.4     5.0            0.208                    0.18    3473.0
      0.4    10.0            0.417                    0.40    1664.0
      0.6     2.0            0.056                    0.05    9144.0
      0.6     5.0            0.139                    0.12    6596.0
      0.6    10.0            0.278                    0.30    4096.0
```
Dans les neuf cas, le seuil optimal observé reste proche du seuil théorique (écart maximal de 0,05 avec la grille). La logique est celle attendue : plus un contact coûte cher, ou moins il réussit, plus le seuil monte et moins on contacte. Dans le cas extrême ($s=0{,}2$, $c=10$ €), le seuil théorique est de 0,83 et le gain maximal tombe à 58 € : presque aucun client ne justifie un contact.

**Étape 4 — La formule suppose de bonnes probabilités, donc dépend du modèle.** On applique le même seuil théorique aux trois modèles.


```python
t_th = 5 / (0.4 * 60)
for k, pk in P.items():
    print(f"{k:11s} contacts {int((pk >= t_th).sum()):4d}  gain au seuil théorique {gain_net(pk, t_th):7.1f} €  | meilleur gain sur la grille {max(gain_net(pk, t) for t in grille):7.1f} €")
```
<!--sortie-->
```text
logistique  contacts  568  gain au seuil théorique  2776.0 €  | meilleur gain sur la grille  2829.0 €
forêt       contacts  550  gain au seuil théorique  3226.0 €  | meilleur gain sur la grille  3352.0 €
boosting    contacts  445  gain au seuil théorique  3391.0 €  | meilleur gain sur la grille  3473.0 €
```
À seuil identique, les modèles ne contactent pas le même nombre de clients (568, 550 et 445) et ne rapportent pas autant : 2 776 € pour la logistique, 3 226 € pour la forêt, 3 391 € pour le boosting. Un écart d'AUC de 0,04 représente donc, ici, environ 600 € de gain par campagne de 2 400 clients. Remarquez aussi que, pour la logistique et la forêt, le seuil théorique est un peu moins bon que le meilleur seuil de la grille (écart de 53 € et de 126 €) : leurs probabilités sont un peu moins justes (voir l'application 5.5).

*Pour aller plus loin.* Ajoutez une contrainte de budget (« au plus 300 contacts ») : le seuil optimal devient celui qui sélectionne exactement 300 clients. Comparez le gain à celui du seuil théorique (445 contacts).

### Application 5.2 — La courbe ROC, l'AUC et la précision moyenne reconstruites à la main

*Sections du livre : 5.1.4 et 5.1.5.* **Objectif** : ne plus voir l'AUC comme une boîte noire en la recalculant de trois façons, puis voir de ses propres yeux pourquoi elle ne réagit pas à la prévalence.

**Étape 1 — La courbe ROC par tri des scores.** On trie les clients par score décroissant ; en descendant la liste, le rappel (parmi les positifs) et le taux de fausses alertes (parmi les négatifs) augmentent. L'aire se calcule par trapèzes.


```python
def roc_manuelle(y_vrai, score):
    ordre = np.argsort(-score, kind="stable"); ys, ss = y_vrai[ordre], score[ordre]
    tp, fp = np.cumsum(ys), np.cumsum(1 - ys)
    garde = np.r_[np.diff(ss) != 0, True]                       # un point par valeur distincte du score
    return np.r_[0, fp[garde] / fp[-1]], np.r_[0, tp[garde] / tp[-1]]

fpr, tpr = roc_manuelle(yt, p)
auc_trapeze = np.sum(np.diff(fpr) * (tpr[1:] + tpr[:-1]) / 2)
print("AUC par trapèzes :", round(auc_trapeze, 4), "| scikit-learn :", round(M.roc_auc_score(yt, p), 4), "| points de la courbe :", len(fpr))
```
<!--sortie-->
```text
AUC par trapèzes : 0.8971 | scikit-learn : 0.8971 | points de la courbe : 2401
```
L'aire par trapèzes (0,8971) est celle de `scikit-learn`. La courbe a 2 401 points : un par valeur distincte de score, plus l'origine.

**Étape 2 — L'AUC comme statistique de Mann-Whitney.** Par les rangs : on additionne les rangs des positifs, on retranche le minimum possible, et l'on divise par le nombre de paires.


```python
from scipy.stats import rankdata
rangs = rankdata(p)
n_pos, n_neg = int(yt.sum()), int((1 - yt).sum())
U = rangs[yt == 1].sum() - n_pos * (n_pos + 1) / 2                # statistique de Mann-Whitney
print("U / (n+ n-) =", round(U / (n_pos * n_neg), 4), "| nombre de paires :", n_pos * n_neg)
```
<!--sortie-->
```text
U / (n+ n-) = 0.8971 | nombre de paires : 695231
```
Le résultat est le même, 0,8971, calculé sur 695 231 paires (337 partants fois 2 063 fidèles) : l'AUC est la probabilité qu'un partant ait un score supérieur à celui d'un fidèle (volume I, section 3.7.2).

**Étape 3 — La précision moyenne.**


```python
prec, rap, _ = M.precision_recall_curve(yt, p)                     # le rappel est décroissant dans ces tableaux
ap_manuelle = -np.sum(np.diff(rap) * prec[:-1])
print("AP à la main :", round(ap_manuelle, 4), "| scikit-learn :", round(M.average_precision_score(yt, p), 4))
```
<!--sortie-->
```text
AP à la main : 0.6496 | scikit-learn : 0.6496
```
**Étape 4 — L'effet de la prévalence.** On donne à chaque client fidèle un poids $m$ : c'est comme si l'on avait $m$ fois plus de fidèles, avec les mêmes scores.


```python
lignes = []
for m in [1, 3, 10, 30]:
    w = np.where(yt == 0, float(m), 1.0)
    lignes.append((m, round((w * yt).sum() / w.sum(), 3), round(M.roc_auc_score(yt, p, sample_weight=w), 4), round(M.average_precision_score(yt, p, sample_weight=w), 4)))
print(pd.DataFrame(lignes, columns=["négatifs x m", "prévalence", "AUC", "AP"]).to_string(index=False))
```
<!--sortie-->
```text
 négatifs x m  prévalence    AUC     AP
            1       0.140 0.8971 0.6496
            3       0.052 0.8971 0.4399
           10       0.016 0.8971 0.2343
           30       0.005 0.8971 0.1152
```
L'AUC reste figée à 0,8971 quel que soit $m$ ; la précision moyenne s'effondre de 0,650 à 0,115 quand la prévalence passe de 14 % à 0,5 %. Pour un détecteur de fraude (prévalence de l'ordre du pour-cent), c'est la seconde colonne qui décrit l'expérience réelle de l'utilisateur.

### Application 5.3 — Lift, gain et incertitude sur la comparaison de deux modèles

*Section du livre : 5.1.8.* **Objectif** : raisonner en budget (« je ne peux contacter que 20 % des clients »), puis se demander si l'avantage d'un modèle sur un autre est plus grand que le bruit.

**Étape 1 — Part des partants atteints et lift, pour trois budgets.**


```python
def capture(score, part):
    k = int(part * len(score)); o = np.argsort(-score)[:k]
    return yt[o].sum() / yt.sum(), yt[o].mean() / yt.mean()          # part des partants atteints, lift

lignes = [(k, part, *np.round(capture(pk, part), 3)) for k, pk in P.items() for part in (0.1, 0.2, 0.3)]
print(pd.DataFrame(lignes, columns=["modèle", "part contactée", "partants atteints", "lift"]).to_string(index=False))
```
<!--sortie-->
```text
    modèle  part contactée  partants atteints  lift
logistique             0.1              0.412 4.125
logistique             0.2              0.641 3.205
logistique             0.3              0.760 2.532
     forêt             0.1              0.481 4.807
     forêt             0.2              0.706 3.531
     forêt             0.3              0.813 2.710
  boosting             0.1              0.499 4.985
  boosting             0.2              0.724 3.620
  boosting             0.3              0.831 2.770
```
En contactant 10 % des clients, le boosting atteint 49,9 % des partants (lift 4,99), la forêt 48,1 % et la logistique 41,2 %. À 20 % de budget : 72,4 %, 70,6 % et 64,1 %. Les deux modèles à arbres sont proches ; la logistique est nettement en retrait.

**Étape 2 — Du budget au gain en euros.** Avec les mêmes économies que l'application 5.1 (24 € d'espérance par partant contacté, 5 € par contact), on compare le gain du modèle à celui d'un ciblage au hasard.


```python
for part in [0.05, 0.1, 0.2, 0.3, 0.5]:
    k = int(part * len(p)); o = np.argsort(-p)[:k]
    modele = 24 * yt[o].sum() - 5 * k                                # 24 = 0,4 x 60 : gain attendu d'un partant contacté ; 5 € par contact
    hasard = 24 * yt.mean() * k - 5 * k                              # espérance avec un ciblage au hasard
    print(f"{part:4.0%} contactés ({k:4d}) : gain du modèle {modele:7.1f} € | gain d'un ciblage au hasard {hasard:7.1f} €")
```
<!--sortie-->
```text
  5% contactés ( 120) : gain du modèle  1776.0 € | gain d'un ciblage au hasard  -195.6 €
 10% contactés ( 240) : gain du modèle  2832.0 € | gain d'un ciblage au hasard  -391.2 €
 20% contactés ( 480) : gain du modèle  3456.0 € | gain d'un ciblage au hasard  -782.4 €
 30% contactés ( 720) : gain du modèle  3120.0 € | gain d'un ciblage au hasard -1173.6 €
 50% contactés (1200) : gain du modèle  1608.0 € | gain d'un ciblage au hasard -1956.0 €
```
Le ciblage au hasard perd de l'argent à tous les budgets (chaque contact coûte 5 € et ne rapporte en moyenne que $24\times0{,}14=3{,}4$ €). Le modèle atteint son maximum vers 20 % de budget (3 456 €) puis décroît, puisque les contacts supplémentaires visent des clients dont le risque est inférieur au seuil de rentabilité.

**Étape 3 — Le bruit du jeu de test.** L'AUC du boosting dépasse celle de la logistique de 0,038 : cet écart est-il plus grand que le hasard ? On rééchantillonne 300 fois les clients du jeu de test (*bootstrap*, volume I, section 3.3.5) et l'on recalcule l'écart à chaque fois, **pour les deux modèles sur les mêmes clients** (comparaison appariée).


```python
rng = np.random.default_rng(0); n = len(yt); diffs = []
for _ in range(300):
    i = rng.integers(0, n, n)                                        # rééchantillonnage des clients du jeu de test
    diffs.append(M.roc_auc_score(yt[i], P["boosting"][i]) - M.roc_auc_score(yt[i], P["logistique"][i]))
obs = M.roc_auc_score(yt, P["boosting"]) - M.roc_auc_score(yt, P["logistique"])
print("écart d'AUC observé :", round(obs, 4), "| intervalle à 95 % (bootstrap apparié) :", np.round(np.percentile(diffs, [2.5, 97.5]), 4))
```
<!--sortie-->
```text
écart d'AUC observé : 0.0378 | intervalle à 95 % (bootstrap apparié) : [0.0254 0.05  ]
```
L'intervalle à 95 % de l'écart d'AUC est de $[0{,}025\ ;\ 0{,}050]$ : il exclut 0, et l'avantage du boosting sur la logistique est donc réel, du moins sur ce type de données. *Pour aller plus loin :* refaites l'exercice pour la forêt contre le boosting. L'écart observé est de 0,009 : l'intervalle contient-il 0 ?

### Application 5.4 — Régression : quelle perte pour quelle décision ?

*Section du livre : 5.1.10.* **Objectif** : constater que le « meilleur » modèle dépend de la métrique, donc de la décision. Un stock doit être préparé pour la dépense des six mois à venir de chaque client. Manquer 1 € de demande (rupture) coûte 3 €, en prévoir 1 € de trop (surstock) coûte 1 €.

**Étape 1 — Trois modèles, trois pertes d'entraînement.** Un boosting entraîné à minimiser l'erreur quadratique (il prédit la moyenne), un autre l'erreur absolue (la médiane), un troisième la perte pinball de niveau 0,75 (le troisième quartile).


```python
from sklearn.ensemble import HistGradientBoostingRegressor as HGBR
yr = c["depense_6m"]; ytr_r, yte_r = yr.loc[Xtr.index].to_numpy(), yr.loc[Xte.index].to_numpy()
modeles = {"moyenne (carré)": HGBR(max_iter=150, random_state=0), "médiane (absolu)": HGBR(loss="absolute_error", max_iter=150, random_state=0),
           "quantile 0,75": HGBR(loss="quantile", quantile=0.75, max_iter=150, random_state=0)}
pred = {k: np.clip(m.fit(Xtr, ytr_r).predict(Xte), 0, None) for k, m in modeles.items()}
def pinball(yv, q, tau): return float(np.mean(np.maximum(tau * (yv - q), (tau - 1) * (yv - q))))
for k, q in pred.items():
    print(f"{k:17s} MAE {M.mean_absolute_error(yte_r, q):6.2f}  RMSE {M.mean_squared_error(yte_r, q) ** 0.5:6.2f}  pinball(0,75) {pinball(yte_r, q, 0.75):6.2f}  part des y <= prévision {np.mean(yte_r <= q):.3f}")
```
<!--sortie-->
```text
moyenne (carré)   MAE  59.21  RMSE  98.61  pinball(0,75)  29.23  part des y <= prévision 0.612
médiane (absolu)  MAE  55.42  RMSE  97.14  pinball(0,75)  31.41  part des y <= prévision 0.558
quantile 0,75     MAE  67.10  RMSE 104.40  pinball(0,75)  25.94  part des y <= prévision 0.729
```
Chacun gagne sur la métrique qui est sa perte : le modèle de la médiane a la plus petite erreur absolue (55,4 €), le modèle quantile la plus petite perte pinball de niveau 0,75 (25,9). (Le modèle de la médiane a aussi un RMSE légèrement meilleur que celui de la moyenne, 97,1 contre 98,6 : l'écart est faible et la perte d'entraînement n'a pas à coïncider avec la métrique d'évaluation.) Le modèle quantile a la **pire** erreur absolue (67,1 €), et il n'est pas biaisé « par erreur » : il vise volontairement le troisième quartile ; 72,9 % des clients ont une dépense inférieure à sa prévision (la cible est 75 %).

**Étape 2 — La perte qui compte : le coût du stock.** Le coût d'une rupture est trois fois celui d'un surstock : le niveau optimal est le quantile de niveau $\tau=\dfrac{c_{\text{rupture}}}{c_{\text{rupture}}+c_{\text{surstock}}}=0{,}75$ (c'est le problème du « vendeur de journaux »).


```python
c_rupture, c_surstock = 3.0, 1.0            # manquer 1 € de demande coûte 3 € ; en prévoir 1 € de trop coûte 1 €
print("niveau optimal tau = c_rupture / (c_rupture + c_surstock) =", c_rupture / (c_rupture + c_surstock))
for k, q in pred.items():
    cout = np.mean(np.where(yte_r > q, c_rupture * (yte_r - q), c_surstock * (q - yte_r)))
    print(f"{k:17s} coût moyen par client : {cout:6.2f} €")
```
<!--sortie-->
```text
niveau optimal tau = c_rupture / (c_rupture + c_surstock) = 0.75
moyenne (carré)   coût moyen par client : 116.92 €
médiane (absolu)  coût moyen par client : 125.64 €
quantile 0,75     coût moyen par client : 103.75 €
```
Le coût moyen par client est de **103,8 €** avec le modèle quantile, contre **116,9 €** avec le modèle de la moyenne et **125,6 €** avec celui de la médiane : 11 % d'économie, alors que ce modèle a la pire erreur absolue de la liste. Le bon modèle est celui dont **la perte est la perte de la décision**.

### Application 5.5 — Diagnostiquer et réparer la calibration

*Sections du livre : 5.2.1 à 5.2.6.* **Objectif** : mesurer la calibration de modèles, réparer une logistique pondérée, et chiffrer en euros le coût d'une mauvaise calibration.

**Étape 1 — Diagnostic.** On ajoute aux trois modèles la logistique pondérée (`class_weight="balanced"`), puis l'on affiche le score de Brier, l'ECE et la probabilité moyenne prédite. On regarde enfin le diagramme de fiabilité de la forêt sous forme de tableau.


```python
def fiabilite(yv, pv, n_bins=10):
    groupes = np.array_split(np.argsort(pv), n_bins)                  # classes de même effectif
    return np.array([[pv[g].mean(), yv[g].mean(), len(g)] for g in groupes])
def ece(yv, pv, n_bins=10):
    t = fiabilite(yv, pv, n_bins); return float(np.sum(t[:, 2] * np.abs(t[:, 0] - t[:, 1])) / t[:, 2].sum())

lr_pond = LogisticRegression(max_iter=3000, class_weight="balanced").fit(sc.transform(Xtr), ytr)
P["logistique pondérée"] = lr_pond.predict_proba(sc.transform(Xte))[:, 1]
for k, pk in P.items():
    print(f"{k:21s} Brier {M.brier_score_loss(yt, pk):.4f}  ECE {ece(yt, pk):.4f}  probabilité moyenne {pk.mean():.3f}")
print(pd.DataFrame(fiabilite(yt, P["forêt"]), columns=["prob. moyenne", "taux observé", "effectif"]).round(3).to_string(index=False))
```
<!--sortie-->
```text
logistique            Brier 0.0872  ECE 0.0120  probabilité moyenne 0.136
forêt                 Brier 0.0808  ECE 0.0314  probabilité moyenne 0.139
boosting              Brier 0.0758  ECE 0.0137  probabilité moyenne 0.128
logistique pondérée   Brier 0.1542  ECE 0.2087  probabilité moyenne 0.349
 prob. moyenne  taux observé  effectif
         0.003         0.004     240.0
         0.011         0.000     240.0
         0.022         0.008     240.0
         0.040         0.033     240.0
         0.062         0.038     240.0
         0.093         0.079     240.0
         0.135         0.100     240.0
         0.193         0.150     240.0
         0.284         0.317     240.0
         0.543         0.675     240.0
```
La logistique pondérée classe bien (voir son AUC dans le livre) mais annonce en moyenne 35 % de départs alors qu'ils sont 14 % : Brier de 0,154, ECE de 0,209. La forêt est sous-confiante : dans la dernière classe, elle annonce 54 % pour 68 % observés.

**Étape 2 — Platt et isotonique, ajustés sur le jeu de calibration.**


```python
from sklearn.isotonic import IsotonicRegression
def logit(s): s = np.clip(s, 1e-4, 1 - 1e-4); return np.log(s / (1 - s)).reshape(-1, 1)

yc = yca.to_numpy(); s_cal = lr_pond.predict_proba(sc.transform(Xca))[:, 1]       # calibration sur le jeu de CALIBRATION
platt = LogisticRegression(C=1e6, max_iter=1000).fit(logit(s_cal), yc)
iso = IsotonicRegression(out_of_bounds="clip").fit(s_cal, yc)
s_te = P["logistique pondérée"]
versions = {"brut": s_te, "Platt": platt.predict_proba(logit(s_te))[:, 1], "isotonique": iso.predict(s_te)}
for k, pk in versions.items(): print(f"{k:11s} Brier {M.brier_score_loss(yt, pk):.4f}  ECE {ece(yt, pk):.4f}")
print("Platt : pente", round(float(platt.coef_[0, 0]), 3), "| ordonnée", round(float(platt.intercept_[0]), 3), "| ln(pi/(1-pi)) =", round(float(np.log(ytr.mean() / (1 - ytr.mean()))), 3))
```
<!--sortie-->
```text
brut        Brier 0.1542  ECE 0.2087
Platt       Brier 0.0881  ECE 0.0145
isotonique  Brier 0.0887  ECE 0.0191
Platt : pente 1.063 | ordonnée -1.789 | ln(pi/(1-pi)) = -1.812
```
Les deux méthodes ramènent le Brier de 0,154 à 0,088-0,089 (celui d'une logistique ordinaire est de 0,087) et l'ECE de 0,209 à 0,015-0,019. L'ordonnée de Platt, $-1{,}789$, est proche de $\ln\frac{\pi}{1-\pi}=-1{,}812$ : la méthode a retrouvé, sans qu'on le lui dise, le décalage de prévalence créé par les poids de classes (exercice 5.8).

**Étape 3 — Ce que cela change pour la décision.** On applique le seuil théorique de l'application 5.1 ($0{,}208$) aux probabilités brutes, puis recalibrées.


```python
t_th = 5 / (0.4 * 60)                       # seuil théorique de la campagne (application 5.1) : valable pour des probabilités CALIBRÉES
for k, pk in versions.items():
    print(f"{k:11s} contacts {int((pk >= t_th).sum()):4d}  gain net {gain_net(pk, t_th):8.1f} €")
```
<!--sortie-->
```text
brut        contacts 1363  gain net    937.0 €
Platt       contacts  589  gain net   2671.0 €
isotonique  contacts  571  gain net   2617.0 €
```
Avec les probabilités brutes, le seuil théorique fait contacter **1 363 clients** et ne rapporte que **937 €** ; avec les probabilités recalibrées, 589 clients et **2 671 €** (571 clients et 2 617 € pour l'isotonique). Le classement des clients est pourtant identique : la mauvaise calibration a coûté plus de 1 700 € **sans que l'AUC ne bouge**.

### Application 5.6 — Trois importances, trois questions

*Sections du livre : 5.3.2 et 5.3.6.* **Objectif** : comparer l'importance par permutation, la moyenne des valeurs SHAP et l'importance « gain » de LightGBM, et comprendre pourquoi elles diffèrent.

**Étape 1 — Les trois tableaux dans un seul.**


```python
import lightgbm as lgb, shap
from sklearn.inspection import permutation_importance
mg = lgb.LGBMClassifier(n_estimators=150, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=0.8, subsample_freq=1,
                        colsample_bytree=0.8, random_state=0, verbose=-1, n_jobs=1).fit(Xtr, ytr)
perm = permutation_importance(mg, Xte, yte, scoring="roc_auc", n_repeats=5, random_state=0, n_jobs=1).importances_mean
sv = shap.TreeExplainer(mg).shap_values(Xte.iloc[:500]); sv = sv[1] if isinstance(sv, list) else sv
gain = mg.booster_.feature_importance("gain")
tab = pd.DataFrame({"permutation": perm, "SHAP moyen": np.abs(sv).mean(axis=0), "gain (part)": gain / gain.sum()}, index=Xte.columns)
print(tab.sort_values("SHAP moyen", ascending=False).head(8).round(4).to_string())
```
<!--sortie-->
```text
                      permutation  SHAP moyen  gain (part)
age                        0.0655      0.6834       0.1962
montant_12m                0.0403      0.6476       0.1271
recence_jours              0.0612      0.5583       0.1909
part_achats_promo          0.0200      0.2780       0.0744
satisfaction_moy           0.0409      0.2666       0.1380
nb_commandes_12m           0.0072      0.2179       0.0402
programme_fidelite         0.0088      0.2036       0.0281
taux_ouverture_email      -0.0008      0.1394       0.0347
```
L'âge, la récence et le montant annuel dominent selon les trois mesures. Mais voyez `taux_ouverture_email` : sa permutation est négative (−0,0008, c'est-à-dire nulle au bruit près), alors que sa contribution SHAP moyenne (0,139) et sa part de gain (3,5 %) sont substantielles.

**Étape 2 — Les rangs.**


```python
rangs = tab.rank(ascending=False)
print(rangs.corr(method="spearman").round(3))
print(rangs.loc[["taux_ouverture_email", "panier_moyen", "anciennete_mois"]].astype(int))
```
<!--sortie-->
```text
             permutation  SHAP moyen  gain (part)
permutation        1.000       0.642        0.618
SHAP moyen         0.642       1.000        0.951
gain (part)        0.618       0.951        1.000
                      permutation  SHAP moyen  gain (part)
taux_ouverture_email           47           8            7
panier_moyen                   45          10           10
anciennete_mois                11          11            8
```
Les deux mesures qui regardent **l'intérieur du modèle** (SHAP et gain) concordent presque parfaitement (corrélation de rangs de Spearman 0,951) ; la permutation, qui mesure la **perte de performance sur le jeu de test**, s'accorde moins avec elles (0,64 et 0,62). L'écart le plus net : `taux_ouverture_email`, au 7ᵉ ou 8ᵉ rang des deux premières mesures et au 47ᵉ pour la permutation. Chaque mesure répond à sa question.

**Étape 3 — Les variables corrélées se partagent l'importance.** On ajoute à `recence_jours` une copie bruitée (écart-type du bruit : 0, 15 puis 50 jours) et l'on mesure l'importance par permutation de l'originale et de la copie.


```python
for bruit in [0, 15, 50]:
    rng = np.random.default_rng(0)                                   # même graine pour chaque niveau de bruit
    A, B = Xtr.copy(), Xte.copy()
    A["copie"] = A["recence_jours"] + rng.normal(0, bruit, len(A)); B["copie"] = B["recence_jours"] + rng.normal(0, bruit, len(B))
    m = lgb.LGBMClassifier(n_estimators=150, learning_rate=0.05, num_leaves=15, min_child_samples=40, subsample=0.8, subsample_freq=1,
                           colsample_bytree=0.8, random_state=0, verbose=-1, n_jobs=1).fit(A, ytr)
    imp = pd.Series(permutation_importance(m, B, yte, scoring="roc_auc", n_repeats=5, random_state=0, n_jobs=1).importances_mean, index=B.columns)
    print(f"bruit de {bruit:2d} jours : récence {imp['recence_jours']:.4f}  copie {imp['copie']:.4f}  somme {imp['recence_jours'] + imp['copie']:.4f}")
```
<!--sortie-->
```text
bruit de  0 jours : récence 0.0551  copie -0.0002  somme 0.0549
bruit de 15 jours : récence 0.0189  copie 0.0126  somme 0.0315
bruit de 50 jours : récence 0.0330  copie 0.0026  somme 0.0356
```
Sans bruit (copie exacte), LightGBM n'utilise en pratique qu'une des deux colonnes : la récence garde 0,0551 et la copie 0. Avec un bruit de 15 jours, l'importance se **partage** (0,0189 et 0,0126) et la somme (0,0315) est bien inférieure à l'importance de la récence seule (0,0612 dans le livre). Avec un bruit de 50 jours, la copie est trop bruitée pour servir (0,0330 contre 0,0026). Moralité : la **répartition** de l'importance entre variables voisines n'est pas stable, ni interprétable seule.

### Application 5.7 — Expliquer un client : SHAP, LIME et stabilité

*Sections du livre : 5.3.4 à 5.3.6.* **Objectif** : expliquer une prédiction individuelle de trois façons, et vérifier ce qui est exact et ce qui est approché.

**Étape 1 — SHAP et l'efficacité.** On choisit un client dont le risque prédit est proche de 55 %.


```python
pm = mg.predict_proba(Xte)[:, 1]; idx = int(np.argsort(np.abs(pm - 0.55))[0])     # un client dont le risque prédit est proche de 55 %
phi = shap.TreeExplainer(mg).shap_values(Xte.iloc[[idx]]); phi = (phi[1] if isinstance(phi, list) else phi)[0]
haut = np.argsort(-np.abs(phi))[:5]
print("client", idx, "| probabilité prédite", round(float(pm[idx]), 3), "| départ observé", int(yte.iloc[idx]))
print([(Xte.columns[j], round(float(phi[j]), 3), float(Xte.iloc[idx, j])) for j in haut])
base = float(np.ravel(shap.TreeExplainer(mg).expected_value)[-1])
print("base + somme des SHAP =", round(base + phi.sum(), 4), "| sortie brute du modèle =", round(float(mg.predict(Xte.iloc[[idx]], raw_score=True)[0]), 4))
```
<!--sortie-->
```text
client 961 | probabilité prédite 0.548 | départ observé 0
[('age', 1.019, 26.0), ('recence_jours', 0.848, 365.0), ('part_achats_promo', 0.622, 0.804), ('montant_12m', 0.565, 0.0), ('satisfaction_moy', -0.485, 5.0)]
base + somme des SHAP = 0.1945 | sortie brute du modèle = 0.1945
```
Le client numéro 961 a un risque de 0,548 (il est finalement resté). Ses cinq plus fortes contributions : l'âge (26 ans, $+1{,}02$), une dernière commande vieille d'un an ($+0{,}85$), une part d'achats en promotion de 80 % ($+0{,}62$), aucun achat dans l'année ($+0{,}57$), et une satisfaction de 5 qui fait baisser le risque ($-0{,}49$). La valeur de base plus la somme des 47 contributions redonne la sortie brute du modèle, 0,1945 en log-cote : c'est l'efficacité de Shapley, exacte.

**Étape 2 — L'instabilité de LIME dépend du nombre d'échantillons.** Pour 300, 1 500 et 6 000 clients fictifs, on relance LIME avec cinq graines et l'on mesure le recouvrement des cinq variables les plus importantes.


```python
from lime.lime_tabular import LimeTabularExplainer
def vars_lime(graine, n_ech):
    ex = LimeTabularExplainer(Xtr.to_numpy(), feature_names=list(Xtr.columns), mode="classification", random_state=graine)
    e = ex.explain_instance(Xte.iloc[idx].to_numpy(), mg.predict_proba, num_features=5, num_samples=n_ech)
    return {next(v for v in Xtr.columns if v in t) for t, _ in e.as_list()}
for n_ech in [300, 1500, 6000]:
    ens = [vars_lime(g, n_ech) for g in range(5)]
    jac = [len(ens[i] & ens[j]) / len(ens[i] | ens[j]) for i in range(5) for j in range(i + 1, 5)]
    print(f"{n_ech:5d} échantillons : recouvrement moyen {np.mean(jac):.2f}, minimum {min(jac):.2f}")
```
<!--sortie-->
```text
  300 échantillons : recouvrement moyen 0.63, minimum 0.43
 1500 échantillons : recouvrement moyen 0.80, minimum 0.67
 6000 échantillons : recouvrement moyen 1.00, minimum 1.00
```
Avec 300 échantillons, deux graines partagent en moyenne 63 % de leurs variables (minimum 43 %) ; avec 1 500, 80 % (minimum 67 %) ; avec 6 000, **100 %**. LIME se stabilise quand on lui donne assez d'échantillons ; le prix est le temps de calcul. Une explication LIME sans mention du nombre d'échantillons et de la graine n'est pas reproductible.

**Étape 3 — Shapley exact par énumération.** Pour un modèle simple (une régression logistique sur trois variables, sortie en log-cote), on calcule les valeurs de Shapley du même client en énumérant toutes les coalitions (avec un fond de 300 clients), puis on les compare à la formule $\beta_j(x_j-\bar x_j)$.


```python
cols = ["recence_jours", "satisfaction_manquante", "nb_tickets_support_12m"]
m3 = LogisticRegression(max_iter=1000).fit(Xtr[cols], ytr)
fond = Xtr[cols].sample(300, random_state=0).to_numpy(); x0 = Xte[cols].iloc[idx].to_numpy()
def v(S):                                    # valeur d'une coalition S : on fixe les variables de S au client, les autres suivent le fond
    Z = fond.copy(); Z[:, list(S)] = x0[list(S)]
    return float((Z @ m3.coef_[0] + m3.intercept_[0]).mean())
phi_exact = [sum(math.factorial(len(S)) * math.factorial(2 - len(S)) / 6 * (v(S + (j,)) - v(S))
                 for r in range(3) for S in itertools.combinations([k for k in range(3) if k != j], r)) for j in range(3)]
print("Shapley exact :", np.round(phi_exact, 4), "| formule beta_j (x_j - moyenne) :", np.round(m3.coef_[0] * (x0 - fond.mean(axis=0)), 4))
```
<!--sortie-->
```text
Shapley exact : [ 1.6919  0.0497 -0.1831] | formule beta_j (x_j - moyenne) : [ 1.6919  0.0497 -0.1831]
```
Les deux calculs coïncident au dernier chiffre (1,6919 ; 0,0497 ; −0,1831) : pour un modèle linéaire, la valeur de Shapley d'une variable est exactement son coefficient fois l'écart du client à la moyenne (exercice 5.10).

### Application 5.8 — Audit d'équité sur le jeu réel de crédit

*Sections du livre : 5.4.1 à 5.4.4.* **Objectif** : auditer un modèle de défaut par groupe, mesurer l'incertitude des écarts, puis tester l'équité « par ignorance ». Les données sont **réelles** (UCI, licence CC0) et l'étude est une illustration méthodologique (voir l'avertissement de la section 5.4.1).

**Étape 1 — Le modèle.**


```python
cr = pd.read_csv("donnees/credit_defaut.csv")
cr["groupe_age"] = pd.cut(cr["age"], [0, 29, 44, 200], labels=["moins de 30 ans", "30 à 44 ans", "45 ans et plus"]).astype(str)
cr["sexe"] = cr["sex"].map({1: "hommes", 2: "femmes"})
var_avec = [k for k in cr.columns if k not in ("default", "groupe_age", "sexe")]
tr, te = train_test_split(cr, test_size=0.3, random_state=0, stratify=cr["default"])
m_avec = HistGradientBoostingClassifier(max_iter=150, random_state=0).fit(tr[var_avec], tr["default"])
s = m_avec.predict_proba(te[var_avec])[:, 1]; y5 = te["default"].to_numpy(); t_alerte = float(np.quantile(s, 0.75))
print(cr.shape, "| taux de défaut", round(cr["default"].mean(), 4), "| AUC test", round(M.roc_auc_score(y5, s), 4), "| seuil (25 % d'alertes)", round(t_alerte, 3))
```
<!--sortie-->
```text
(30000, 26) | taux de défaut 0.2212 | AUC test 0.7765 | seuil (25 % d'alertes) 0.271
```
Le jeu compte 30 000 clients et 26 colonnes (24 d'origine plus deux colonnes de groupes), pour un taux de défaut de 22,1 %. Le modèle atteint une AUC de 0,7765 ; on signale les 25 % de dossiers les plus risqués (score supérieur à 0,271).

**Étape 2 — L'audit par groupe.**


```python
def par_groupe(score, y, g, t):
    lignes = {}
    for nom in np.unique(g):
        m = g == nom; al = score[m] >= t; yy = y[m]
        tp, fp = (al & (yy == 1)).sum(), (al & (yy == 0)).sum(); fn, tn = (~al & (yy == 1)).sum(), (~al & (yy == 0)).sum()
        lignes[nom] = dict(effectif=int(m.sum()), taux_defaut=yy.mean(), taux_alerte=al.mean(), rappel=tp / (tp + fn), fausses_alertes=fp / (fp + tn), precision=tp / (tp + fp))
    return pd.DataFrame(lignes).T
for var in ["sexe", "groupe_age"]:
    print(par_groupe(s, y5, te[var].to_numpy(), t_alerte).round(3).to_string(), "\n")
```
<!--sortie-->
```text
        effectif  taux_defaut  taux_alerte  rappel  fausses_alertes  precision
femmes    5353.0        0.206        0.234   0.571            0.147      0.502
hommes    3647.0        0.244        0.273   0.574            0.176      0.513 

                 effectif  taux_defaut  taux_alerte  rappel  fausses_alertes  precision
30 à 44 ans        4497.0        0.212        0.234   0.533            0.154      0.483
45 ans et plus     1618.0        0.255        0.279   0.610            0.165      0.559
moins de 30 ans    2885.0        0.216        0.258   0.608            0.162      0.509 
```
Selon le sexe, le rappel est presque identique (0,571 et 0,574), mais le taux d'alerte (0,234 contre 0,273) et le taux de fausses alertes (0,147 contre 0,176) diffèrent. Selon l'âge, le rappel varie de 0,533 (30-44 ans) à 0,61 (les deux autres classes).

**Étape 3 — Les écarts sont-ils plus grands que le bruit ?** On rééchantillonne 300 fois les 9 000 dossiers du jeu de test et l'on recalcule les écarts maximaux selon le sexe.


```python
def ecarts(score, y, g, t):
    tab = par_groupe(score, y, g, t); return np.array([np.ptp(tab["taux_alerte"]), np.ptp(tab["rappel"])])
g_sexe = te["sexe"].to_numpy(); rng = np.random.default_rng(0); n = len(y5); b = []
for _ in range(300):
    i = rng.integers(0, n, n); b.append(ecarts(s[i], y5[i], g_sexe[i], t_alerte))
b = np.array(b); obs = ecarts(s, y5, g_sexe, t_alerte)
print("écart de taux d'alerte :", round(obs[0], 3), "IC 95 %", np.round(np.percentile(b[:, 0], [2.5, 97.5]), 3), "| écart de rappel :", round(obs[1], 3), "IC 95 %", np.round(np.percentile(b[:, 1], [2.5, 97.5]), 3))
```
<!--sortie-->
```text
écart de taux d'alerte : 0.039 IC 95 % [0.023 0.057] | écart de rappel : 0.003 IC 95 % [0.001 0.053]
```
L'écart de taux d'alerte (0,039) a un intervalle à 95 % de $[0{,}023\ ;\ 0{,}057]$ : il est solidement positif. L'écart de rappel (0,003) a un intervalle de $[0{,}001\ ;\ 0{,}053]$ : l'égalité des chances est « presque réalisée » sur l'échantillon, mais **les données ne permettent pas d'exclure** un écart de l'ordre de 5 points. (Un écart maximal entre groupes est toujours positif par construction : son intervalle de bootstrap ne contient jamais 0.)

**Étape 4 — Retirer le sexe, et chercher des proxys.**


```python
var_sans = [k for k in var_avec if k != "sex"]
m_sans = HistGradientBoostingClassifier(max_iter=150, random_state=0).fit(tr[var_sans], tr["default"])
s2 = m_sans.predict_proba(te[var_sans])[:, 1]; t2 = float(np.quantile(s2, 0.75))
print("AUC sans le sexe :", round(M.roc_auc_score(y5, s2), 4), "| écarts (alerte, rappel) sans le sexe :", np.round(ecarts(s2, y5, g_sexe, t2), 4), "| avec :", np.round(obs, 4))
from sklearn.model_selection import cross_val_predict
proxy = cross_val_predict(HistGradientBoostingClassifier(max_iter=100, random_state=0), cr[var_sans], (cr["sex"] == 2).astype(int), cv=3, method="predict_proba")[:, 1]
print("AUC pour retrouver le sexe à partir des autres variables :", round(M.roc_auc_score((cr["sex"] == 2).astype(int), proxy), 4))
```
<!--sortie-->
```text
AUC sans le sexe : 0.7741 | écarts (alerte, rappel) sans le sexe : [0.0301 0.0009] | avec : [0.0393 0.0029]
AUC pour retrouver le sexe à partir des autres variables : 0.6441
```
Sans la variable sexe, l'AUC passe de 0,7765 à 0,7741 ; les écarts d'alerte et de rappel selon le sexe passent de (0,0393 ; 0,0029) à (0,0301 ; 0,0009) : ils diminuent un peu sans disparaître. Et les autres variables suffisent à retrouver le sexe avec une AUC de 0,644 : elles en sont des proxys.

### Application 5.9 — Des seuils par groupe, et ce qu'ils coûtent

*Section du livre : 5.4.5.* **Objectif** : comparer trois politiques de décision (seuil unique, égalité des chances, parité démographique) sur le sexe et sur l'âge, avec un coût d'erreur (un défaut manqué coûte 5, une fausse alerte 1).

**Étape 1 — Les trois politiques.**


```python
def politique(score, y, g, mode, t0):
    cible = ((score >= t0) & (y == 1)).sum() / (y == 1).sum(); al = np.zeros(len(y), dtype=bool)
    for nom in np.unique(g):
        m = g == nom
        if mode == "unique": t = t0
        elif mode == "chances": t = np.quantile(score[m & (y == 1)], 1 - cible)          # même rappel dans tous les groupes
        else: t = np.quantile(score[m], 0.75)                                            # même taux d'alerte (25 %) dans tous les groupes
        al[m] = score[m] >= t
    return al
c_fn, c_fp = 5.0, 1.0
for var in ["sexe", "groupe_age"]:
    g = te[var].to_numpy()
    for mode in ["unique", "chances", "parite"]:
        al = politique(s, y5, g, mode, t_alerte); tab = par_groupe(al.astype(float), y5, g, 0.5)
        cout = (c_fn * (~al & (y5 == 1)).sum() + c_fp * (al & (y5 == 0)).sum()) / len(y5) * 1000
        print(f"{var:10s} {mode:8s} coût {cout:6.1f} | écarts : alerte {np.ptp(tab['taux_alerte']):.3f}  rappel {np.ptp(tab['rappel']):.3f}  précision {np.ptp(tab['precision']):.3f}  fausses alertes {np.ptp(tab['fausses_alertes']):.3f}")
```
<!--sortie-->
```text
sexe       unique   coût  596.1 | écarts : alerte 0.039  rappel 0.003  précision 0.011  fausses alertes 0.030
sexe       chances  coût  597.0 | écarts : alerte 0.036  rappel 0.001  précision 0.016  fausses alertes 0.025
sexe       parite   coût  594.9 | écarts : alerte 0.000  rappel 0.040  précision 0.052  fausses alertes 0.009
groupe_age unique   coût  596.1 | écarts : alerte 0.044  rappel 0.077  précision 0.076  fausses alertes 0.011
groupe_age chances  coût  601.1 | écarts : alerte 0.036  rappel 0.002  précision 0.143  fausses alertes 0.054
groupe_age parite   coût  598.3 | écarts : alerte 0.000  rappel 0.051  précision 0.121  fausses alertes 0.031
```
Les résultats sont ceux du tableau de 5.4.5. Pour l'âge, par exemple, l'égalité des chances ramène l'écart de rappel de 0,077 à 0,002, mais fait passer l'écart de précision de 0,076 à 0,143 et l'écart de fausses alertes de 0,011 à 0,054. Le coût moyen (595 à 601 pour 1 000 dossiers) varie peu.

**Étape 2 — D'autres groupes, et le piège des petits effectifs.**


```python
te2 = te.copy()
te2["etat_civil"] = te2["marriage"].map({1: "marié(e)", 2: "célibataire"}).fillna("autre")
te2["etudes"] = te2["education"].map({1: "supérieures", 2: "université", 3: "lycée"}).fillna("autre")
for var in ["etat_civil", "etudes"]:
    print(par_groupe(s, y5, te2[var].to_numpy(), t_alerte).round(3).to_string(), "\n")
```
<!--sortie-->
```text
             effectif  taux_defaut  taux_alerte  rappel  fausses_alertes  precision
autre           122.0        0.197        0.221   0.500            0.153      0.444
célibataire    4780.0        0.205        0.235   0.569            0.149      0.495
marié(e)       4098.0        0.241        0.268   0.578            0.169      0.520 

             effectif  taux_defaut  taux_alerte  rappel  fausses_alertes  precision
autre           139.0        0.108        0.043   0.133            0.032      0.333
lycée          1450.0        0.268        0.300   0.624            0.182      0.556
supérieures    3170.0        0.190        0.216   0.564            0.134      0.496
université     4241.0        0.232        0.265   0.564            0.174      0.495 
```
Selon la situation matrimoniale, les taux d'alerte (0,235 pour les célibataires, 0,268 pour les mariés) suivent les taux de défaut (0,205 et 0,241). Selon le niveau d'études, les clients de niveau « lycée » ont le taux de défaut le plus élevé (0,268). Le groupe « autre » (139 clients, 10,8 % de défaut, rappel 0,133) est trop petit pour que ses taux soient interprétables : **un écart mesuré sur quelques dizaines de cas positifs est essentiellement du bruit**, et un audit sérieux le dit.

### Application 5.10 — Prédiction conforme : classification et régression

*Sections du livre : 5.5.1 à 5.5.6.* **Objectif** : construire des ensembles de prédiction avec garantie, constater que la garantie est marginale, la vérifier par simulation pour deux modèles et plusieurs tailles de calibration, puis passer à la régression.

**Étape 1 — Ensembles LAC et correction de Mondrian.**


```python
alpha = 0.10
def q_conf(sc_, alpha):
    sc_ = np.sort(sc_); k = int(np.ceil((len(sc_) + 1) * (1 - alpha)))          # k-ième plus petit score, k = ceil((n+1)(1-alpha))
    return float(sc_[k - 1]) if k <= len(sc_) else float("inf")
pcal, ptest = gb.predict_proba(Xca), gb.predict_proba(Xte); ycal = yca.to_numpy()
s_cal = 1 - pcal[np.arange(len(ycal)), ycal]; q = q_conf(s_cal, alpha)
ens = (1 - ptest) <= q; couv = ens[np.arange(len(yt)), yt]
print("q =", round(q, 4), "| couverture", round(couv.mean(), 4), "| partants", round(couv[yt == 1].mean(), 4), "| fidèles", round(couv[yt == 0].mean(), 4), "| taille moyenne", round(ens.sum(1).mean(), 3))
qk = [q_conf(s_cal[ycal == k], alpha) for k in (0, 1)]                            # Mondrian : un quantile par classe
ens_m = np.column_stack([(1 - ptest[:, 0]) <= qk[0], (1 - ptest[:, 1]) <= qk[1]]); cm = ens_m[np.arange(len(yt)), yt]
print("Mondrian : partants", round(cm[yt == 1].mean(), 4), "| fidèles", round(cm[yt == 0].mean(), 4), "| taille moyenne", round(ens_m.sum(1).mean(), 3))
```
<!--sortie-->
```text
q = 0.5221 | couverture 0.9025 | partants 0.4955 | fidèles 0.969 | taille moyenne 1.006
Mondrian : partants 0.9021 | fidèles 0.9157 | taille moyenne 1.213
```
La couverture globale est de 90,25 %, mais elle n'est que de 49,6 % pour les partants. Avec un quantile par classe (Mondrian), elle devient valable dans chaque classe (90,2 % et 91,6 %) au prix d'ensembles un peu plus gros (1,21 classe en moyenne contre 1,01).

**Étape 2 — La garantie ne dépend pas du modèle.** On répète 400 fois le tirage d'un jeu de calibration de $n$ clients dans le pool (calibration + test) et l'on mesure la couverture sur les autres, pour le boosting puis pour la régression logistique, à comparer à la loi Bêta théorique.


```python
from scipy.stats import beta as beta_
def simule(scores, n_cal, reps=400, seed=1):
    rng = np.random.default_rng(seed); cov = []
    for _ in range(reps):
        perm = rng.permutation(len(scores)); q = q_conf(scores[perm[:n_cal]], alpha); cov.append((scores[perm[n_cal:]] <= q).mean())
    return np.mean(cov), np.std(cov)
yy = np.concatenate([ycal, yt]); Z = pd.concat([Xca, Xte])
pools = {"boosting": gb.predict_proba(Z), "logistique": lr.predict_proba(sc.transform(Z))}
for nom, pp in pools.items():
    sp = 1 - pp[np.arange(len(yy)), yy]
    for n_cal in [50, 100, 300, 1000]:
        m_, sd_ = simule(sp, n_cal); k = int(np.ceil((n_cal + 1) * (1 - alpha))); th = beta_(k, n_cal + 1 - k)
        print(f"{nom:10s} n = {n_cal:4d} : couverture {m_:.4f} (écart-type {sd_:.4f}) | théorie {th.mean():.4f} ({th.std():.4f})")
```
<!--sortie-->
```text
boosting   n =   50 : couverture 0.9009 (écart-type 0.0416) | théorie 0.9020 (0.0412)
boosting   n =  100 : couverture 0.8994 (écart-type 0.0303) | théorie 0.9010 (0.0296)
boosting   n =  300 : couverture 0.9001 (écart-type 0.0171) | théorie 0.9003 (0.0172)
boosting   n = 1000 : couverture 0.8998 (écart-type 0.0104) | théorie 0.9001 (0.0095)
logistique n =   50 : couverture 0.9030 (écart-type 0.0400) | théorie 0.9020 (0.0412)
logistique n =  100 : couverture 0.9000 (écart-type 0.0294) | théorie 0.9010 (0.0296)
logistique n =  300 : couverture 0.9004 (écart-type 0.0175) | théorie 0.9003 (0.0172)
logistique n = 1000 : couverture 0.8998 (écart-type 0.0105) | théorie 0.9001 (0.0095)
```
Pour les deux modèles, la couverture moyenne est de 90 % à 0,3 point près, **quelle que soit la taille $n$** de la calibration, et l'écart-type colle à la théorie (0,0416 contre 0,0412 pour $n=50$ ; 0,0171 contre 0,0172 pour $n=300$). Le modèle compte pour la **taille des ensembles**, pas pour la validité. (À $n=1\,000$, l'écart-type observé, 0,0104, est légèrement supérieur à celui de la théorie, 0,0095 : le jeu de test restant n'a plus que 3 800 clients, et ses fluctuations propres s'ajoutent.)

**Étape 3 — Régression : largeur constante contre CQR.**


```python
yr = c["depense_6m"]; ytr_r, ycal_r, yte_r = (yr.loc[X_.index].to_numpy() for X_ in (Xtr, Xca, Xte))
reg = HGBR(max_iter=150, random_state=0).fit(Xtr, ytr_r)
q_r = q_conf(np.abs(ycal_r - reg.predict(Xca)), alpha); mu = reg.predict(Xte); lo, hi = np.maximum(mu - q_r, 0), mu + q_r
gl, gh = (HGBR(loss="quantile", quantile=a, max_iter=150, random_state=0).fit(Xtr, ytr_r) for a in (alpha / 2, 1 - alpha / 2))
q_c = q_conf(np.maximum(gl.predict(Xca) - ycal_r, ycal_r - gh.predict(Xca)), alpha)
lo2, hi2 = np.maximum(gl.predict(Xte) - q_c, 0), gh.predict(Xte) + q_c
tert = pd.qcut(mu, 3, labels=["basse", "moyenne", "haute"])
for nom, (l, h) in {"largeur constante": (lo, hi), "CQR": (lo2, hi2)}.items():
    ok = (yte_r >= l) & (yte_r <= h)
    print(f"{nom:18s} couverture {ok.mean():.3f}  largeur moyenne {np.mean(h - l):6.1f}  par tiers de prévision :", {t: round(float(ok[tert == t].mean()), 3) for t in tert.categories})
```
<!--sortie-->
```text
largeur constante  couverture 0.910  largeur moyenne  210.1  par tiers de prévision : {'basse': 0.994, 'moyenne': 0.975, 'haute': 0.76}
CQR                couverture 0.910  largeur moyenne  185.3  par tiers de prévision : {'basse': 0.922, 'moyenne': 0.916, 'haute': 0.892}
```
Les deux méthodes couvrent 91 % des clients, mais la régression quantile conformalisée est plus étroite en moyenne (185 € contre 210 €) et beaucoup plus homogène : la couverture par tiers de prévision vaut 0,92 ; 0,92 ; 0,89, contre 0,99 ; 0,98 ; 0,76 pour les intervalles de largeur constante.

## Exercices

### Exercice 5.1 ⭐ — Matrice de confusion à la main (section 5.1.2)

Sur 1 000 clients, 75 vont partir. Le modèle émet 60 alertes, dont 45 sont justes.
1. Complétez la matrice de confusion.
2. Calculez l'exactitude, la précision, le rappel, la spécificité, le $F_1$, le $F_2$ et le coefficient de Matthews.
3. Comparez l'exactitude à celle du modèle « personne ne part ».

### Exercice 5.2 ⭐ — Mesures $F_\beta$ (section 5.1.2)

Un modèle a une précision de 0,8 et un rappel de 0,5. Calculez $F_1$, $F_2$ et $F_{0{,}5}$. Manquer un départ coûte quatre fois plus cher qu'une fausse alerte : laquelle des trois mesures est la plus cohérente avec cette situation ? Pourquoi ne remplace-t-elle pas un calcul de coût ?

### Exercice 5.3 ⭐⭐ — L'AUC par les paires (section 5.1.4)

Quatre clients qui partent ont les scores 0,9 ; 0,8 ; 0,55 et 0,4. Cinq clients fidèles ont les scores 0,7 ; 0,5 ; 0,4 ; 0,2 et 0,1.
1. Combien y a-t-il de paires (partant, fidèle) ?
2. Calculez l'AUC comme proportion de paires bien ordonnées (une égalité compte pour une demi-paire).
3. Donnez les points $(\mathrm{FPR},\mathrm{TPR})$ de la courbe ROC et retrouvez l'AUC par trapèzes.

### Exercice 5.4 ⭐⭐ — ROC contre précision-rappel (section 5.1.5)

Un détecteur a un rappel de 0,8 et un taux de fausses alertes de 0,1. Exprimez sa précision en fonction de la prévalence $\pi$, puis calculez-la pour $\pi=10\ \%$, $1\ \%$ et $0{,}1\ \%$. Que devient le point ROC ? Quelle conséquence pour le choix entre l'AUC et l'AP ?

### Exercice 5.5 ⭐⭐ — Le seuil par les coûts et la calibration (section 5.1.7)

Une campagne coûte 8 € par contact, réussit avec la probabilité 0,25 et rapporte 120 € par succès.
1. Quel est le seuil théorique ?
2. Le modèle annonce des probabilités **deux fois trop grandes**. Que se passe-t-il si l'on applique le seuil de la question 1 à ces probabilités ? Quel seuil faut-il appliquer ? Vérifiez sur les probabilités du boosting (jeu de test).

### Exercice 5.6 ⭐ — Log-loss et score de Brier (section 5.1.6)

Cinq prédictions $\hat p=(0{,}9;\ 0{,}8;\ 0{,}3;\ 0{,}6;\ 0{,}1)$ pour les résultats $y=(1;\ 1;\ 0;\ 1;\ 0)$. Calculez la log-loss et le score de Brier, puis le score de Brier du modèle constant, et le « score de compétence » du modèle.

### Exercice 5.7 ⭐⭐ — L'ECE à la main (section 5.2.1)

Quatre classes de 100 clients : probabilité moyenne prédite 0,05 ; 0,20 ; 0,50 ; 0,80 ; taux observés 0,08 ; 0,15 ; 0,60 ; 0,70. Calculez l'ECE. Dans quelles classes le modèle est-il optimiste ou pessimiste ? Quelles différences sont plausiblement dues au hasard ?

### Exercice 5.8 ⭐⭐⭐ — Poids de classes et décalage de l'ordonnée (section 5.2.6)

Montrez que, si l'on entraîne une régression logistique avec des poids qui donnent à chaque classe la moitié du poids total, l'ordonnée à l'origine est décalée de $-\ln\frac{\pi}{1-\pi}$ par rapport à celle d'un modèle sans poids, et que les pentes sont inchangées. Vérifiez par simulation.

### Exercice 5.9 ⭐⭐ — Valeurs de Shapley à la main (section 5.3.5)

Trois variables A, B, C ont les valeurs de coalition $v(\varnothing)=0$, $v(A)=10$, $v(B)=20$, $v(C)=0$, $v(AB)=40$, $v(AC)=10$, $v(BC)=20$, $v(ABC)=45$.
1. Calculez les valeurs de Shapley de A, B et C en listant les six ordres d'arrivée.
2. Vérifiez l'efficacité.
3. La variable C n'apporte rien seule : pourquoi n'est-elle pas un « joueur nul » ?

### Exercice 5.10 ⭐⭐⭐ — SHAP d'un modèle linéaire (section 5.3.6)

Pour $f(x)=\beta_0+\sum_j\beta_jx_j$ et des variables indépendantes, montrez que la valeur de Shapley (version « on remplace les variables absentes par leur distribution ») de la variable $j$ est $\varphi_j=\beta_j\,(x_j-E[X_j])$. Vérifiez sur $\beta=(2,-1,0{,}5)$, $x=(3,0,2)$.

### Exercice 5.11 ⭐⭐ — Les critères d'équité (section 5.4.2)

Deux groupes ont les matrices de confusion suivantes (VP, FP, FN, VN) : groupe A : (40, 20, 20, 120) ; groupe B : (30, 10, 30, 230). Calculez pour chacun le taux de défaut, le taux d'alerte, le rappel, le taux de fausses alertes et la précision. Lesquels des critères (parité démographique, égalité des chances, parité prédictive, égalité des fausses alertes) sont satisfaits ?

### Exercice 5.12 ⭐⭐⭐ — L'impossibilité (section 5.4.4)

Démontrez l'identité $\mathrm{FPR}=\dfrac{p}{1-p}\cdot\dfrac{1-\mathrm{PPV}}{\mathrm{PPV}}\cdot(1-\mathrm{FNR})$. Application : deux groupes ont la même précision (0,6) et le même rappel (0,5) mais des prévalences de 30 % et de 10 %. Quels taux de fausses alertes en résulte-t-il ? Qu'en concluez-vous ?

### Exercice 5.13 ⭐⭐ — Le quantile conforme (section 5.5.2)

Dix-neuf scores de calibration (triés) : 0,02 ; 0,05 ; 0,07 ; 0,09 ; 0,12 ; 0,15 ; 0,18 ; 0,21 ; 0,25 ; 0,29 ; 0,33 ; 0,38 ; 0,41 ; 0,46 ; 0,52 ; 0,58 ; 0,66 ; 0,74 ; 0,91.
1. Calculez $\hat q$ pour $\alpha=0{,}10$ puis $\alpha=0{,}20$.
2. Un client a une probabilité de départ de 0,30 (score $1-\hat p_y$ pour chaque classe). Donnez son ensemble de prédiction dans les deux cas.
3. Que devient $\hat q$ avec seulement 8 scores et $\alpha=0{,}10$ ? Interprétez.

### Exercice 5.14 ⭐⭐⭐ — La loi de la couverture (section 5.5.3)

Si les scores sont continus, montrez que, **conditionnellement au jeu de calibration**, la couverture d'un nouveau score suit une loi Bêta$(k,\,n+1-k)$. Calculez sa moyenne et son écart-type pour $n=99$ et $\alpha=0{,}10$, puis vérifiez par simulation avec des scores uniformes.

## Corrigés

### Corrigé 5.1

1. VP = 45, FP = 60 − 45 = 15, FN = 75 − 45 = 30, VN = 1 000 − 45 − 15 − 30 = 910.
2. Exactitude $=955/1000=0{,}955$ ; précision $=45/60=0{,}75$ ; rappel $=45/75=0{,}60$ ; spécificité $=910/925\approx0{,}984$ ; $F_1=\dfrac{2\times0{,}75\times0{,}6}{1{,}35}\approx0{,}667$ ; $F_2=\dfrac{5\times0{,}75\times0{,}6}{4\times0{,}75+0{,}6}=0{,}625$ ; MCC $=\dfrac{45\times910-15\times30}{\sqrt{60\cdot75\cdot925\cdot940}}\approx0{,}648$.
3. « Personne ne part » a une exactitude de $925/1000=0{,}925$ : le modèle ne gagne que trois points d'exactitude, alors qu'il détecte 60 % des départs.


```python
VP, FP, FN, VN = 45, 15, 30, 910
n = VP + FP + FN + VN; P_, R_ = VP / (VP + FP), VP / (VP + FN)
print("exactitude", (VP + VN) / n, "| précision", P_, "| rappel", R_, "| spécificité", round(VN / (VN + FP), 4), "| majoritaire", (FP + VN) / n)
print("F1", round(2 * P_ * R_ / (P_ + R_), 4), "| F2", round(5 * P_ * R_ / (4 * P_ + R_), 4), "| MCC", round((VP * VN - FP * FN) / math.sqrt((VP + FP) * (VP + FN) * (VN + FP) * (VN + FN)), 4))
```
<!--sortie-->
```text
exactitude 0.955 | précision 0.75 | rappel 0.6 | spécificité 0.9838 | majoritaire 0.925
F1 0.6667 | F2 0.625 | MCC 0.6475
```
### Corrigé 5.2

$F_1=\dfrac{2\times0{,}8\times0{,}5}{1{,}3}\approx0{,}615$ ; $F_2=\dfrac{5\times0{,}8\times0{,}5}{4\times0{,}8+0{,}5}=\dfrac{2}{3{,}7}\approx0{,}541$ ; $F_{0{,}5}=\dfrac{1{,}25\times0{,}8\times0{,}5}{0{,}25\times0{,}8+0{,}5}=\dfrac{0{,}5}{0{,}7}\approx0{,}714$. Dans le $F_\beta$, le rappel compte $\beta^2$ fois plus que la précision ; si manquer un départ coûte quatre fois plus cher qu'une fausse alerte, $\beta=2$ (soit $\beta^2=4$) est cohérent, d'où $F_2\approx0{,}54$. Mais le $F_\beta$ est un compromis *heuristique* : il ignore le nombre de vrais négatifs et la valeur réelle des gains. Pour décider, on calcule le coût attendu (section 5.1.7).


```python
P_, R_ = 0.8, 0.5
for beta in [1, 2, 0.5]:
    print(f"F{beta} =", round((1 + beta ** 2) * P_ * R_ / (beta ** 2 * P_ + R_), 4))
```
<!--sortie-->
```text
F1 = 0.6154
F2 = 0.5405
F0.5 = 0.7143
```
### Corrigé 5.3

1. $4\times5=20$ paires.
2. Paires gagnées : 0,9 bat les 5 fidèles (5) ; 0,8 bat les 5 (5) ; 0,55 bat 0,5 ; 0,4 ; 0,2 ; 0,1 mais pas 0,7 (4) ; 0,4 bat 0,2 et 0,1 (2) et est à égalité avec le 0,4 fidèle (0,5). Total $5+5+4+2+0{,}5=16{,}5$, d'où $\mathrm{AUC}=16{,}5/20=0{,}825$.
3. En balayant les seuils de haut en bas : $(0;\,0)\to(0;\,0{,}25)\to(0;\,0{,}5)$ (après 0,9 et 0,8) $\to(0{,}2;\,0{,}5)$ (0,7 fidèle) $\to(0{,}2;\,0{,}75)$ (0,55) $\to(0{,}4;\,0{,}75)$ (0,5 fidèle) $\to(0{,}6;\,1)$ (0,4 : deux clients à égalité, un de chaque classe) $\to(0{,}8;\,1)\to(1;\,1)$. Aire par trapèzes : $0{,}2\times0{,}5+0{,}2\times0{,}75+0{,}2\times\frac{0{,}75+1}{2}+0{,}2\times1+0{,}2\times1=0{,}1+0{,}15+0{,}175+0{,}2+0{,}2=0{,}825$.


```python
pos = np.array([0.9, 0.8, 0.55, 0.4]); neg = np.array([0.7, 0.5, 0.4, 0.2, 0.1])
gagnees = (pos[:, None] > neg[None, :]).sum() + 0.5 * (pos[:, None] == neg[None, :]).sum()
print("paires :", pos.size * neg.size, "| gagnées (égalité = 1/2) :", gagnees, "| AUC =", gagnees / (pos.size * neg.size))
print("AUC scikit-learn :", M.roc_auc_score([1] * 4 + [0] * 5, np.r_[pos, neg]))
```
<!--sortie-->
```text
paires : 20 | gagnées (égalité = 1/2) : 16.5 | AUC = 0.825
AUC scikit-learn : 0.825
```
### Corrigé 5.4

La précision est $\dfrac{VP}{VP+FP}=\dfrac{\mathrm{TPR}\cdot\pi}{\mathrm{TPR}\cdot\pi+\mathrm{FPR}\cdot(1-\pi)}$ (on normalise par la taille de l'échantillon : les positifs sont $\pi n$, les négatifs $(1-\pi)n$). Avec TPR $=0{,}8$ et FPR $=0{,}1$ : $\pi=10\ \%$ : $\dfrac{0{,}08}{0{,}08+0{,}09}=0{,}471$ ; $\pi=1\ \%$ : $\dfrac{0{,}008}{0{,}008+0{,}099}=0{,}075$ ; $\pi=0{,}1\ \%$ : $\dfrac{0{,}0008}{0{,}0008+0{,}0999}=0{,}0079$. Le point ROC $(0{,}1;\,0{,}8)$ n'a pas bougé, mais moins d'une alerte sur cent est justifiée à 0,1 % de prévalence. L'AUC ne voit pas ce phénomène ; la précision moyenne, si.


```python
tpr, fpr = 0.8, 0.1
for prev in [0.1, 0.01, 0.001]:
    print(f"prévalence {prev:5.3f} : précision = {tpr * prev / (tpr * prev + fpr * (1 - prev)):.4f}")
```
<!--sortie-->
```text
prévalence 0.100 : précision = 0.4706
prévalence 0.010 : précision = 0.0748
prévalence 0.001 : précision = 0.0079
```
### Corrigé 5.5

1. $t^\star=\dfrac{c}{sV}=\dfrac{8}{0{,}25\times120}=\dfrac{8}{30}\approx0{,}267$.
2. Si le modèle annonce $\hat p=2p$, le client $p$ est contacté dès que $2p\ge0{,}267$, c'est-à-dire $p\ge0{,}133$ : on contacte trop de clients (585 au lieu de 373 sur le jeu de test), parmi lesquels beaucoup ne sont pas rentables. Il faut appliquer le seuil **corrigé** $2t^\star=0{,}533$ aux probabilités gonflées, ce qui revient au même seuil sur les vraies probabilités. Vérification : le gain est de 3 496 € avec les vraies probabilités au seuil théorique, **3 180 €** avec les probabilités doublées au même seuil (perte de 316 €), et de nouveau **3 496 €** au seuil corrigé.


```python
c_, s_, V_ = 8.0, 0.25, 120.0
t_th = c_ / (s_ * V_); print("seuil théorique :", round(t_th, 4))
for facteur in [1.0, 2.0]:                    # le modèle annonce-t-il la vraie probabilité (x1) ou le double (x2) ?
    pk = np.clip(p * facteur, 0, 1)
    print(f"probabilités x{facteur:.0f} : gain au seuil théorique {gain_net(pk, t_th, c_, s_, V_):7.1f} € ({int((pk >= t_th).sum())} contacts) | au seuil corrigé {facteur * t_th:.3f} : {gain_net(pk, facteur * t_th, c_, s_, V_):7.1f} € ({int((pk >= facteur * t_th).sum())} contacts)")
```
<!--sortie-->
```text
seuil théorique : 0.2667
probabilités x1 : gain au seuil théorique  3496.0 € (373 contacts) | au seuil corrigé 0.267 :  3496.0 € (373 contacts)
probabilités x2 : gain au seuil théorique  3180.0 € (585 contacts) | au seuil corrigé 0.533 :  3496.0 € (373 contacts)
```
### Corrigé 5.6

Log-loss : $-\ln0{,}9=0{,}105$ ; $-\ln0{,}8=0{,}223$ ; $-\ln0{,}7=0{,}357$ ; $-\ln0{,}6=0{,}511$ ; $-\ln0{,}9=0{,}105$ ; moyenne $\approx0{,}260$. Brier : $(0{,}01+0{,}04+0{,}09+0{,}16+0{,}01)/5=0{,}062$. Le modèle constant annonce la fréquence $0{,}6$ : $(3\times0{,}16+2\times0{,}36)/5=0{,}24$. Score de compétence : $1-0{,}062/0{,}24\approx0{,}74$.


```python
ph = np.array([0.9, 0.8, 0.3, 0.6, 0.1]); yv = np.array([1, 1, 0, 1, 0])
print("log-loss", round(float(-(yv * np.log(ph) + (1 - yv) * np.log(1 - ph)).mean()), 4), "| Brier", round(float(((ph - yv) ** 2).mean()), 4), "| Brier du modèle constant", round(float(((yv.mean() - yv) ** 2).mean()), 4))
```
<!--sortie-->
```text
log-loss 0.2603 | Brier 0.062 | Brier du modèle constant 0.24
```
### Corrigé 5.7

$\mathrm{ECE}=\dfrac14(0{,}03+0{,}05+0{,}10+0{,}10)=0{,}07$. Classes 1 et 3 : le modèle est **pessimiste** (il annonce moins que le taux observé : 0,05 pour 0,08 ; 0,50 pour 0,60) ; classes 2 et 4 : **optimiste** (0,20 pour 0,15 ; 0,80 pour 0,70). Avec 100 clients par classe, le taux observé fluctue de $\sqrt{p(1-p)/100}$, soit 0,022 ; 0,040 ; 0,050 ; 0,040 : les écarts de 0,03 et de 0,05 (classes 1 et 2) valent environ 1,2 à 1,4 écart-type et peuvent être dus au hasard ; les écarts de 0,10 (classes 3 et 4) valent 2 à 2,5 écarts-types : ils sont plus probablement réels.


```python
classes = np.array([[100, 0.05, 0.08], [100, 0.20, 0.15], [100, 0.50, 0.60], [100, 0.80, 0.70]])
print("ECE =", round(float(np.sum(classes[:, 0] * np.abs(classes[:, 1] - classes[:, 2])) / classes[:, 0].sum()), 4))
```
<!--sortie-->
```text
ECE = 0.07
```
### Corrigé 5.8

Notons $\pi$ la vraie prévalence et $\mathrm{LR}(x)$ le rapport de vraisemblance $P(x\mid Y=1)/P(x\mid Y=0)$. La vraie cote *a posteriori* est $\frac{\pi}{1-\pi}\mathrm{LR}(x)$ : si le modèle logistique est correct, $\operatorname{logit}P(Y=1\mid x)=\ln\frac{\pi}{1-\pi}+\ln\mathrm{LR}(x)=\beta_0+\beta^\top x$. Avec des poids qui donnent la moitié du poids total à chaque classe, la vraisemblance pondérée est celle d'un échantillon où les deux classes sont à égalité : la prévalence apparente est $\pi'=\frac12$, la cote *a posteriori* apprise est $\frac{\pi'}{1-\pi'}\mathrm{LR}(x)=\mathrm{LR}(x)$. Le logit appris est donc $\ln\mathrm{LR}(x)=\beta_0+\beta^\top x-\ln\frac{\pi}{1-\pi}$ : seule l'ordonnée est décalée, de $-\ln\frac{\pi}{1-\pi}$. Dans la simulation (vraie ordonnée $-2$, prévalence 0,164), le modèle ordinaire estime $-2{,}019$, le modèle pondéré $-0{,}389$ : le décalage est de $1{,}631$ et $-\ln\frac{0{,}1638}{0{,}8362}=1{,}630$ ; les pentes sont les mêmes à 0,001 près.


```python
rng = np.random.default_rng(0); n = 60000; xs = rng.normal(size=(n, 2)); b0 = -2.0
vrai = 1 / (1 + np.exp(-(b0 + 1.0 * xs[:, 0] - 0.5 * xs[:, 1]))); yy_ = rng.binomial(1, vrai)
m_n = LogisticRegression(C=1e6).fit(xs, yy_); m_b = LogisticRegression(C=1e6, class_weight="balanced").fit(xs, yy_)
pi_ = yy_.mean()
print("prévalence", round(pi_, 4), "| ordonnées : normale", round(float(m_n.intercept_[0]), 3), "pondérée", round(float(m_b.intercept_[0]), 3),
      "| écart", round(float(m_b.intercept_[0] - m_n.intercept_[0]), 3), "| -ln(pi/(1-pi)) =", round(float(-np.log(pi_ / (1 - pi_))), 3))
print("pentes : normale", np.round(m_n.coef_[0], 3), "pondérée", np.round(m_b.coef_[0], 3))
```
<!--sortie-->
```text
prévalence 0.1638 | ordonnées : normale -2.019 pondérée -0.389 | écart 1.631 | -ln(pi/(1-pi)) = 1.63
pentes : normale [ 1.025 -0.516] pondérée [ 1.024 -0.515]
```
### Corrigé 5.9

Ordres (apports de A, B, C) : ABC : (10 ; 30 ; 5) ; ACB : (10 ; 35 ; 0) ; BAC : (20 ; 20 ; 5) ; BCA : (25 ; 20 ; 0) ; CAB : (10 ; 35 ; 0) ; CBA : (25 ; 20 ; 0). (Exemple, ordre CAB : $v(C)-v(\varnothing)=0$, puis $v(AC)-v(C)=10$, puis $v(ABC)-v(AC)=35$.) Moyennes : $\varphi_A=100/6\approx16{,}67$, $\varphi_B=160/6\approx26{,}67$, $\varphi_C=10/6\approx1{,}67$. La somme est $45=v(ABC)-v(\varnothing)$ : efficacité vérifiée. C n'est pas un joueur nul parce qu'il apporte 5 lorsqu'il arrive après A et B (45 − 40), même s'il n'apporte rien avec A seul ou avec B seul : un **joueur nul** est un joueur qui n'apporte **jamais** rien, quelle que soit la coalition.


```python
v = {(): 0, ("A",): 10, ("B",): 20, ("C",): 0, ("A", "B"): 40, ("A", "C"): 10, ("B", "C"): 20, ("A", "B", "C"): 45}
val = lambda S: v[tuple(sorted(S))]
phi = {j: 0.0 for j in "ABC"}
for ordre in itertools.permutations("ABC"):
    pris = []
    for j in ordre:
        phi[j] += (val(pris + [j]) - val(pris)) / 6; pris.append(j)
print({k: round(x, 4) for k, x in phi.items()}, "| somme", round(sum(phi.values()), 4))
```
<!--sortie-->
```text
{'A': 16.6667, 'B': 26.6667, 'C': 1.6667} | somme 45.0
```
### Corrigé 5.10

Avec des variables indépendantes et la valeur de coalition $v(S)=E\bigl[f(X)\mid X_S=x_S\bigr]=\beta_0+\sum_{j\in S}\beta_jx_j+\sum_{j\notin S}\beta_jE[X_j]$ (le modèle est linéaire, l'espérance se décompose), l'apport marginal de $j$ à une coalition $S$ qui ne le contient pas est $v(S\cup\{j\})-v(S)=\beta_j\bigl(x_j-E[X_j]\bigr)$, **indépendamment de $S$**. La moyenne pondérée de quantités constantes est cette constante : $\varphi_j=\beta_j(x_j-E[X_j])$. Numériquement, avec $\beta=(2,-1,0{,}5)$ et $x=(3,0,2)$, l'énumération exacte et la formule donnent les mêmes trois valeurs (4,0128 ; 0,9944 ; 0,5620 sur ce fond de 500 tirages), dont la somme est $f(x)-E[f(X)]$.


```python
rng = np.random.default_rng(1); beta_ = np.array([2.0, -1.0, 0.5]); fond = rng.normal(1.0, 1.0, size=(500, 3)); x0 = np.array([3.0, 0.0, 2.0])
def v(S):
    Z = fond.copy(); Z[:, list(S)] = x0[list(S)]; return float((Z @ beta_).mean())
phi = [sum(math.factorial(len(S)) * math.factorial(2 - len(S)) / 6 * (v(S + (j,)) - v(S)) for r in range(3) for S in itertools.combinations([k for k in range(3) if k != j], r)) for j in range(3)]
print("Shapley exact :", np.round(phi, 4), "| beta_j (x_j - moyenne_j) :", np.round(beta_ * (x0 - fond.mean(axis=0)), 4))
```
<!--sortie-->
```text
Shapley exact : [4.0128 0.9944 0.562 ] | beta_j (x_j - moyenne_j) : [4.0128 0.9944 0.562 ]
```
### Corrigé 5.11

| | Groupe A | Groupe B |
|---|---:|---:|
| Taux de défaut | 0,300 | 0,200 |
| Taux d'alerte | 0,300 | 0,133 |
| Rappel | 0,667 | 0,500 |
| Fausses alertes | 0,143 | 0,042 |
| Précision | 0,667 | 0,750 |

Les écarts sont de 0,167 pour le taux d'alerte (parité démographique), 0,167 pour le rappel (égalité des chances), 0,101 pour les fausses alertes et 0,083 pour la précision : **aucun des critères n'est satisfait**. On vérifie l'identité de l'exercice 5.12 : pour A, $\frac{0{,}3}{0{,}7}\cdot\frac{1/3}{2/3}\cdot0{,}667=0{,}143$.


```python
groupes = {"A": dict(TP=40, FP=20, FN=20, TN=120), "B": dict(TP=30, FP=10, FN=30, TN=230)}
for g, d in groupes.items():
    n = sum(d.values()); pos = d["TP"] + d["FN"]
    print(g, "| n", n, "| défaut", round(pos / n, 3), "| alerte", round((d["TP"] + d["FP"]) / n, 3), "| rappel", round(d["TP"] / pos, 3),
          "| fausses alertes", round(d["FP"] / (d["FP"] + d["TN"]), 3), "| précision", round(d["TP"] / (d["TP"] + d["FP"]), 3))
```
<!--sortie-->
```text
A | n 200 | défaut 0.3 | alerte 0.3 | rappel 0.667 | fausses alertes 0.143 | précision 0.667
B | n 300 | défaut 0.2 | alerte 0.133 | rappel 0.5 | fausses alertes 0.042 | précision 0.75
```
### Corrigé 5.12

Les effectifs d'un groupe de taille $n$ sont $VP=(1-\mathrm{FNR})\,p\,n$ et $FP=\mathrm{FPR}\,(1-p)\,n$. La précision est $\mathrm{PPV}=\dfrac{VP}{VP+FP}$, soit $FP=VP\cdot\dfrac{1-\mathrm{PPV}}{\mathrm{PPV}}$. En remplaçant : $\mathrm{FPR}\,(1-p)\,n=(1-\mathrm{FNR})\,p\,n\cdot\dfrac{1-\mathrm{PPV}}{\mathrm{PPV}}$, d'où l'identité. Application : le facteur $\dfrac{1-\mathrm{PPV}}{\mathrm{PPV}}(1-\mathrm{FNR})=\dfrac{0{,}4}{0{,}6}\times0{,}5=\dfrac13$ est le même pour les deux groupes ; il reste $\mathrm{FPR}=\dfrac{p}{1-p}\cdot\dfrac13$ : 0,143 pour $p=0{,}30$ et 0,037 pour $p=0{,}10$. **Deux groupes de prévalences différentes ne peuvent pas avoir à la fois la même précision, le même rappel et les mêmes fausses alertes**, sauf pour un classifieur parfait.


```python
for nom, prev in [("A", 0.30), ("B", 0.10)]:
    fpr = prev / (1 - prev) * (1 - 0.6) / 0.6 * 0.5
    print(f"groupe {nom} : prévalence {prev} -> taux de fausses alertes imposé {fpr:.4f}")
```
<!--sortie-->
```text
groupe A : prévalence 0.3 -> taux de fausses alertes imposé 0.1429
groupe B : prévalence 0.1 -> taux de fausses alertes imposé 0.0370
```
### Corrigé 5.13

1. $\alpha=0{,}10$ : $k=\lceil20\times0{,}9\rceil=18$ : $\hat q$ est le 18ᵉ plus petit score, **0,74**. $\alpha=0{,}20$ : $k=\lceil20\times0{,}8\rceil=16$ : $\hat q=0{,}58$.
2. Pour $\hat p_{\text{partant}}=0{,}30$ : le score de la classe « partant » est $1-0{,}30=0{,}70$ et celui de « fidèle » est $0{,}30$. Avec $\hat q=0{,}74$, les deux sont $\le\hat q$ : l'ensemble est {fidèle, partant}. Avec $\hat q=0{,}58$, seul « fidèle » (0,30) reste : l'ensemble est {fidèle}. Un niveau de confiance plus exigeant (90 % au lieu de 80 %) rend les ensembles plus gros.
3. Avec $n=8$ et $\alpha=0{,}10$ : $k=\lceil9\times0{,}9\rceil=9>8$, donc $\hat q=+\infty$ et l'ensemble contient **toutes les classes** : avec trop peu de données de calibration, la garantie à 90 % ne peut être tenue qu'en ne disant rien. Il faut $n\ge\frac{1}{\alpha}-1=9$ pour que $\hat q$ soit fini (ici $n=9$ donne le plus grand des scores, 0,25).


```python
scores = np.array([0.02, 0.05, 0.07, 0.09, 0.12, 0.15, 0.18, 0.21, 0.25, 0.29, 0.33, 0.38, 0.41, 0.46, 0.52, 0.58, 0.66, 0.74, 0.91])
for n_, a in [(19, 0.10), (19, 0.20), (9, 0.10), (8, 0.10)]:
    k = math.ceil((n_ + 1) * (1 - a)); print(f"n = {n_:2d}, alpha = {a} : k = {k}", "-> q =", np.sort(scores[:n_])[k - 1] if k <= n_ else "infini (ensemble = toutes les classes)")
```
<!--sortie-->
```text
n = 19, alpha = 0.1 : k = 18 -> q = 0.74
n = 19, alpha = 0.2 : k = 16 -> q = 0.58
n =  9, alpha = 0.1 : k = 9 -> q = 0.25
n =  8, alpha = 0.1 : k = 9 -> q = infini (ensemble = toutes les classes)
```
### Corrigé 5.14

Si les scores sont continus, la couverture d'un nouveau score, conditionnellement au jeu de calibration, est $F(\hat q)$ où $F$ est la fonction de répartition des scores et $\hat q=S_{(k)}$ est le $k$-ième plus petit des $n$ scores de calibration. Or $F(S_{(k)})$ est le $k$-ième plus petit de $n$ variables uniformes (le théorème de la transformation intégrale de probabilité), de loi Bêta$(k,\,n+1-k)$. Sa moyenne est $\dfrac{k}{n+1}$ et sa variance $\dfrac{k(n+1-k)}{(n+1)^2(n+2)}$. Avec $n=99$ et $\alpha=0{,}10$ : $k=\lceil100\times0{,}9\rceil=90$, donc moyenne $0{,}9$ et écart-type $\sqrt{\dfrac{90\times10}{100^2\times101}}\approx0{,}0299$. La simulation (20 000 jeux de calibration uniformes) donne bien 0,9000 et 0,0299.


```python
rng = np.random.default_rng(0); n, alpha_ = 99, 0.10; k = math.ceil((n + 1) * (1 - alpha_)); cov = []
for _ in range(20000):
    cal = np.sort(rng.random(n)); cov.append(cal[k - 1])               # pour des scores U(0,1), la couverture d'un jeu de calibration est le k-ième plus petit score
print("k =", k, "| couverture moyenne", round(np.mean(cov), 4), "écart-type", round(np.std(cov), 4), "| Bêta(k, n+1-k) :", round(k / (n + 1), 4), round(math.sqrt(k * (n + 1 - k) / ((n + 1) ** 2 * (n + 2))), 4))
```
<!--sortie-->
```text
k = 90 | couverture moyenne 0.9 écart-type 0.0299 | Bêta(k, n+1-k) : 0.9 0.0299
```


> ✅ **Ce que vous avez pratiqué.** Le calcul à la main de toutes les métriques et de leurs liens (matrice de confusion, AUC, précision-rappel, coûts, log-loss, Brier) ; la calibration, de la mesure à la réparation ; l'interprétabilité (permutation, SHAP, LIME, Shapley exact) ; l'audit d'équité sur un jeu réel, ses limites mathématiques et statistiques ; la prédiction conforme avec sa preuve et sa vérification par simulation.
