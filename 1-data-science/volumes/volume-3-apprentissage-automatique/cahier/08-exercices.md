# Chapitre 8 : ➕ Apprentissage semi-supervisé et actif — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 8 du livre (apprentissage semi-supervisé et actif). Vous y trouverez **huit applications guidées**, où l'on écrit à la main ce que le livre a seulement montré (courbes d'apprentissage, auto-apprentissage, propagation d'étiquettes, co-apprentissage, boucle active, comité, biais d'échantillonnage, coût), puis **douze exercices** avec corrigés. Les données sont les deux jeux du livre : les **chiffres manuscrits** (réels, `load_digits`) et les **clients de la boutique** (simulés, `donnees/clients_ml.csv`).

## Préparation

Le chargement des deux jeux (réservoir d'entraînement et jeu de test, variables centrées-réduites pour les clients) est dans `build/outils_ch08.py`. Le reste, c'est-à-dire tout l'intéressant, est écrit ici, à la main.

```python
import sys
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.linear_model import LogisticRegression
import outils_ch08 as o                              # charger_digits, charger_churn, tirer_etiquettes...

Xp, Xt, yp, yt = o.charger_digits()                  # chiffres : réservoir (1 347 images) et test (450)
Xc, Xct, yc, yct = o.charger_churn()                 # clients : réservoir (9 000) et test (3 000)
print("chiffres", Xp.shape, Xt.shape, "| clients", Xc.shape, Xct.shape, "| taux de résiliation", round(yc.mean(), 3))
```
<!--sortie-->
```text
chiffres (1347, 64) (450, 64) | clients (9000, 49) (3000, 49) | taux de résiliation 0.14
```

## Applications

### Application 8.1 — La courbe d'apprentissage selon le budget d'étiquettes

**Objectif.** Construire la courbe de référence du livre (section 8.1.5) et mesurer à quel point un tirage unique est trompeur.

**Étape 1 : un seul tirage de 10 étiquettes.** On choisit 10 images au hasard, on entraîne, on mesure sur le jeu de test.

```python
rng = np.random.default_rng(0)
idx = rng.choice(len(Xp), 10, replace=False)
modele = LogisticRegression(max_iter=2000).fit(Xp[idx], yp[idx])
print("classes présentes parmi les 10 étiquettes :", len(set(yp[idx])), "sur 10 | précision sur le test :", round(modele.score(Xt, yt), 3))
```
<!--sortie-->
```text
classes présentes parmi les 10 étiquettes : 8 sur 10 | précision sur le test : 0.398
```

**Étape 2 : répéter le tirage.** Pour chaque budget, 10 tirages indépendants (graines 100 à 109). On garde la moyenne, l'écart-type, le minimum et le maximum.

```python
budgets = [10, 20, 50, 100, 200, 400]
lignes = []
for nl in budgets:
    scores = []
    for s in range(10):
        i = np.random.default_rng(100 + s).choice(len(Xp), nl, replace=False)
        scores.append(LogisticRegression(max_iter=2000).fit(Xp[i], yp[i]).score(Xt, yt))
    lignes.append((nl, np.mean(scores), np.std(scores), np.min(scores), np.max(scores)))
tab = pd.DataFrame(lignes, columns=["étiquettes", "moyenne", "écart-type", "min", "max"]).round(3)
print(tab.to_string(index=False))
```
<!--sortie-->
```text
 étiquettes  moyenne  écart-type   min   max
         10    0.429       0.082 0.331 0.571
         20    0.577       0.056 0.489 0.651
         50    0.782       0.042 0.729 0.844
        100    0.874       0.010 0.856 0.891
        200    0.927       0.008 0.913 0.940
        400    0.947       0.009 0.933 0.960
```

**Étape 3 : combien de tirages faut-il ?** L'erreur-type de la moyenne de $n$ tirages est $\sigma/\sqrt n$. À 10 étiquettes, avec l'écart-type observé, combien de tirages pour que la moyenne soit connue à ± 0,01 près (une erreur-type) ?

```python
sigma10 = tab.loc[tab["étiquettes"] == 10, "écart-type"].iloc[0]
print("écart-type à 10 étiquettes :", sigma10, "| erreur-type de la moyenne de 10 tirages :", round(sigma10 / np.sqrt(10), 3))
print("tirages nécessaires pour une erreur-type de 0,01 :", int(np.ceil((sigma10 / 0.01) ** 2)))
```
<!--sortie-->
```text
écart-type à 10 étiquettes : 0.082 | erreur-type de la moyenne de 10 tirages : 0.026
tirages nécessaires pour une erreur-type de 0,01 : 68
```

**Pour aller plus loin.** Refaites la courbe avec un autre modèle, par exemple les 3 plus proches voisins, et comparez : la méthode de référence change-t-elle l'allure de la courbe ?

```python
from sklearn.neighbors import KNeighborsClassifier
lignes = []
for nl in (10, 20, 50, 100, 200):
    sc_lr, sc_knn = [], []
    for s in range(10):
        i = np.random.default_rng(100 + s).choice(len(Xp), nl, replace=False)
        sc_lr.append(LogisticRegression(max_iter=2000).fit(Xp[i], yp[i]).score(Xt, yt))
        sc_knn.append(KNeighborsClassifier(3).fit(Xp[i], yp[i]).score(Xt, yt))
    lignes.append((nl, np.mean(sc_lr), np.mean(sc_knn)))
print(pd.DataFrame(lignes, columns=["étiquettes", "logistique", "3 voisins"]).round(3).to_string(index=False))
```
<!--sortie-->
```text
 étiquettes  logistique  3 voisins
         10       0.429      0.312
         20       0.577      0.502
         50       0.782      0.764
        100       0.874      0.866
        200       0.927      0.930
```

### Application 8.2 — Auto-apprentissage : écrire la boucle, regarder les pseudo-étiquettes

**Objectif.** Écrire l'algorithme de la section 8.2.1 sans `SelfTrainingClassifier`, puis regarder, tour par tour, **combien** de pseudo-étiquettes sont ajoutées et **quelle part est juste**.

**Étape 1 : la boucle.** À chaque tour : on entraîne sur les points étiquetés, on prédit les non étiquetés, on ajoute ceux dont la confiance dépasse le seuil. On garde une trace de la précision des pseudo-étiquettes, que nous pouvons calculer car nous connaissons les vraies étiquettes (`yp`) : dans une vraie étude, ce serait impossible.

```python
def auto_apprentissage(X, y_part, y_vrai, seuil=0.9, tours=10):
    y = y_part.copy()
    journal = []
    for t in range(1, tours + 1):
        lab = y != -1
        modele = LogisticRegression(max_iter=2000).fit(X[lab], y[lab])
        libres = np.where(~lab)[0]
        P = modele.predict_proba(X[libres])
        sur = P.max(axis=1) >= seuil
        if not sur.any():
            break
        ajoutes = libres[sur]
        y[ajoutes] = modele.classes_[P[sur].argmax(axis=1)]
        journal.append((t, len(ajoutes), (y[ajoutes] == y_vrai[ajoutes]).mean()))
    return LogisticRegression(max_iter=2000).fit(X[y != -1], y[y != -1]), journal
```

**Étape 2 : un tirage de 50 étiquettes, seuil 0,7.** (Au seuil 0,9, ce tirage ne contient aucun point assez sûr : la boucle n'ajouterait rien. Le seuil de 0,7 permet de voir le mécanisme à l'œuvre.)

```python
rng = np.random.default_rng(100)
idx = rng.choice(len(Xp), 50, replace=False)
y_part = np.full(len(Xp), -1)
y_part[idx] = yp[idx]
modele_auto, journal = auto_apprentissage(Xp, y_part, yp, seuil=0.7)
seul = LogisticRegression(max_iter=2000).fit(Xp[idx], yp[idx])
print(pd.DataFrame(journal, columns=["tour", "pseudo-étiquettes ajoutées", "part juste"]).round(3).to_string(index=False))
print("précision test : auto-apprentissage", round(modele_auto.score(Xt, yt), 3), "| supervisé seul", round(seul.score(Xt, yt), 3))
```
<!--sortie-->
```text
 tour  pseudo-étiquettes ajoutées  part juste
    1                         216       1.000
    2                         402       0.978
    3                         234       0.889
    4                         120       0.550
    5                          80       0.338
    6                          43       0.326
    7                          20       0.650
    8                          10       0.800
    9                           9       1.000
   10                           8       0.875
précision test : auto-apprentissage 0.802 | supervisé seul 0.831
```

**Étape 3 : vérifier contre scikit-learn, puis balayer le seuil sur 10 tirages.**

```python
from sklearn.semi_supervised import SelfTrainingClassifier
lignes = []
for seuil in (0.7, 0.8, 0.9, 0.95):
    ma, sk, ba = [], [], []
    for s in range(10):
        i = np.random.default_rng(100 + s).choice(len(Xp), 50, replace=False)
        yp_ = np.full(len(Xp), -1); yp_[i] = yp[i]
        ma.append(auto_apprentissage(Xp, yp_, yp, seuil)[0].score(Xt, yt))
        sk.append(SelfTrainingClassifier(LogisticRegression(max_iter=2000), threshold=seuil).fit(Xp, yp_).score(Xt, yt))
        ba.append(LogisticRegression(max_iter=2000).fit(Xp[i], yp[i]).score(Xt, yt))
    lignes.append((seuil, np.mean(ma), np.mean(sk), np.mean(ba)))
print(pd.DataFrame(lignes, columns=["seuil", "ma boucle", "scikit-learn", "supervisé seul"]).round(3).to_string(index=False))
```
<!--sortie-->
```text
 seuil  ma boucle  scikit-learn  supervisé seul
  0.70      0.698         0.698           0.782
  0.80      0.593         0.593           0.782
  0.90      0.706         0.706           0.782
  0.95      0.781         0.781           0.782
```

**Lecture.** Le journal montre l'histoire en deux temps. Aux **deux premiers tours**, la boucle ajoute 216 puis 402 pseudo-étiquettes, **justes à 100 % puis 98 %** : ce sont les cas faciles, très loin de la frontière. Mais dès le **quatrième tour**, les points ajoutés ne sont plus justes qu'à 55 %, puis 34 % et 33 % aux tours 5 et 6 : la boucle continue d'ajouter des points qu'elle se trompe à classer, qui deviennent des données d'entraînement. Le modèle final (0,802) est **moins bon** que le supervisé seul (0,831). C'est le biais de confirmation de la section 8.2.2. Dans le balayage des seuils, **ma boucle et celle de scikit-learn donnent exactement les mêmes précisions** (0,698 ; 0,593 ; 0,706 ; 0,781) et aucune ne dépasse le supervisé seul (0,782 en moyenne) : le seuil 0,95 le rejoint seulement parce qu'il n'ajoute presque rien.

### Application 8.3 — La propagation d'étiquettes, du graphe à la solution fermée

**Objectif.** Calculer $F^*=(1-\alpha)(I-\alpha S)^{-1}Y$ (section 8.2.4) sur un graphe de plus proches voisins, vérifier qu'on retrouve `LabelSpreading`, et **voir** pourquoi un trop petit nombre de voisins est catastrophique.

**Étape 1 : la solution fermée sur un graphe de voisinage.**

```python
import scipy.sparse as sp
from scipy.sparse.linalg import spsolve
from sklearn.neighbors import kneighbors_graph

def propagation(X, y_part, k=7, alpha=0.2, nb_classes=10):
    W = kneighbors_graph(X, k, mode="connectivity", include_self=False)
    W = ((W + W.T) > 0).astype(float)                       # graphe symétrique
    d = np.asarray(W.sum(axis=1)).ravel()
    S = sp.diags(1 / np.sqrt(d)) @ W @ sp.diags(1 / np.sqrt(d))
    Y = np.zeros((len(X), nb_classes))
    lab = y_part != -1
    Y[lab, y_part[lab]] = 1
    return spsolve((sp.eye(len(X)) - alpha * S).tocsc(), (1 - alpha) * Y), W
```

**Étape 2 : comparer à scikit-learn.** Même tirage de 50 étiquettes qu'à l'application précédente.

```python
from sklearn.semi_supervised import LabelSpreading
F, W = propagation(Xp, y_part, k=7, alpha=0.2)
ma_classe = F.argmax(axis=1)
sk = LabelSpreading(kernel="knn", n_neighbors=7, alpha=0.2, max_iter=200).fit(Xp, y_part)
libres = y_part == -1
print("précision sur les points non étiquetés : ma solution", round((ma_classe[libres] == yp[libres]).mean(), 3),
      "| scikit-learn", round((sk.transduction_[libres] == yp[libres]).mean(), 3))
print("accord entre les deux sur les classes :", round((ma_classe == sk.transduction_).mean(), 3))
```
<!--sortie-->
```text
précision sur les points non étiquetés : ma solution 0.928 | scikit-learn 0.925
accord entre les deux sur les classes : 0.932
```

**Étape 3 : le graphe est-il connexe ?** Un graphe en plusieurs morceaux a des îlots que les étiquettes n'atteignent jamais. On compte les composantes connexes, et celles qui ne contiennent **aucune** étiquette.

```python
from scipy.sparse.csgraph import connected_components
lignes = []
for k in (3, 5, 7, 15):
    F_k, W_k = propagation(Xp, y_part, k=k)
    nb_comp, comp = connected_components(W_k, directed=False)
    sans_etiquette = sum(1 for c in range(nb_comp) if not (y_part[comp == c] != -1).any())
    acc = (F_k.argmax(axis=1)[libres] == yp[libres]).mean()
    lignes.append((k, nb_comp, sans_etiquette, int((~np.isin(comp, np.unique(comp[y_part != -1]))).sum()), acc))
print(pd.DataFrame(lignes, columns=["k", "composantes", "dont sans étiquette", "points non atteints", "précision (non étiquetés)"]).round(3).to_string(index=False))
```
<!--sortie-->
```text
 k  composantes  dont sans étiquette  points non atteints  précision (non étiquetés)
 3            2                    0                    0                      0.915
 5            2                    0                    0                      0.922
 7            1                    0                    0                      0.928
15            1                    0                    0                      0.924
```

**Lecture.** Notre solution fermée et `LabelSpreading` s'accordent sur 93 % des classes et donnent des précisions voisines sur les points non étiquetés (0,928 contre 0,925). L'écart vient du **graphe** : le nôtre est symétrisé, celui de scikit-learn ne l'est pas. Cela change tout pour les petits $k$ : notre graphe est **connexe dès $k=7$** (une seule composante), et même à $k=3$ ou $k=5$ il n'a que deux composantes, **toutes deux contenant des étiquettes** (aucune sans étiquette, aucun point non atteint). Du coup, avec 50 étiquettes, notre implémentation atteint **0,915 dès $k=3$**. L'effondrement de `LabelSpreading` à $k=3$ (0,29 avec 20 étiquettes, section 8.2.5 du livre) tient donc au graphe **orienté** de scikit-learn, où 86 % des points ne reçoivent aucun score, et non à un manque de voisins en soi. **Leçon : symétrisez le graphe**, ou prenez $k\ge7$.

### Application 8.4 — Co-apprentissage : un essai instructif

**Objectif.** Tester le co-apprentissage de la section 8.2.3 sur deux « vues » d'un chiffre, la moitié haute et la moitié basse de l'image, et constater que les **hypothèses** de la méthode ne sont pas réunies.

**Étape 1 : les deux vues, et leur valeur individuelle.** Une image 8 × 8 est stockée sous forme de 64 pixels ; les 32 premiers sont les 4 lignes du haut, les 32 suivants celles du bas. Avec 100 étiquettes, que vaut chaque moitié seule ? Et les deux ensemble ?

```python
vue1, vue2 = slice(0, 32), slice(32, 64)
rng = np.random.default_rng(100)
idx = rng.choice(len(Xp), 100, replace=False)
a1 = LogisticRegression(max_iter=2000).fit(Xp[idx][:, vue1], yp[idx]).score(Xt[:, vue1], yt)
a2 = LogisticRegression(max_iter=2000).fit(Xp[idx][:, vue2], yp[idx]).score(Xt[:, vue2], yt)
a12 = LogisticRegression(max_iter=2000).fit(Xp[idx], yp[idx]).score(Xt, yt)
print("moitié haute seule :", round(a1, 3), "| moitié basse seule :", round(a2, 3), "| image entière :", round(a12, 3))
```
<!--sortie-->
```text
moitié haute seule : 0.72 | moitié basse seule : 0.722 | image entière : 0.864
```

**Étape 2 : la boucle de co-apprentissage.** À chaque tour, chaque modèle étiquette les 10 points non étiquetés dont il est le plus sûr, et ces étiquettes sont ajoutées au jeu **commun**. La prédiction finale multiplie les probabilités des deux modèles.

```python
def co_apprentissage(X, idx, y, tours=10, ajout=10):
    etiq = {int(i): int(y[i]) for i in idx}
    for _ in range(tours):
        for v in (vue1, vue2):
            L = np.array(sorted(etiq))
            m = LogisticRegression(max_iter=2000).fit(X[L][:, v], [etiq[i] for i in L])
            U = np.array([i for i in range(len(X)) if i not in etiq])
            P = m.predict_proba(X[U][:, v])
            meilleurs = np.argsort(-P.max(axis=1))[:ajout]
            for j in meilleurs:
                etiq[int(U[j])] = int(m.classes_[P[j].argmax()])
    return etiq

etiq = co_apprentissage(Xp, idx[:30], yp)             # on part de 30 étiquettes seulement
ajoutes = [i for i in etiq if i not in set(idx[:30])]
print("pseudo-étiquettes ajoutées :", len(ajoutes), "| part juste :", round(np.mean([etiq[i] == yp[i] for i in ajoutes]), 3))
```
<!--sortie-->
```text
pseudo-étiquettes ajoutées : 200 | part juste : 0.305
```

**Étape 3 : l'effet final.**

```python
L = np.array(sorted(etiq))
yl = np.array([etiq[i] for i in L])
m1 = LogisticRegression(max_iter=2000).fit(Xp[L][:, vue1], yl)
m2 = LogisticRegression(max_iter=2000).fit(Xp[L][:, vue2], yl)
pred = m1.classes_[(m1.predict_proba(Xt[:, vue1]) * m2.predict_proba(Xt[:, vue2])).argmax(axis=1)]
base = LogisticRegression(max_iter=2000).fit(Xp[idx[:30]], yp[idx[:30]]).score(Xt, yt)
print("précision test : co-apprentissage", round((pred == yt).mean(), 3), "| supervisé seul avec les mêmes 30 étiquettes", round(base, 3))
```
<!--sortie-->
```text
précision test : co-apprentissage 0.376 | supervisé seul avec les mêmes 30 étiquettes 0.671
```

**Lecture.** Chaque moitié d'image, avec 100 étiquettes, donne environ **0,72** de précision, contre **0,86** pour l'image entière : chaque vue est **informative mais insuffisante**. Avec seulement 30 étiquettes, c'est pire : les pseudo-étiquettes ajoutées (200) ne sont justes que dans **30,5 %** des cas, et le co-apprentissage finit à **0,376**, contre **0,671** pour le supervisé seul. Trois raisons : (1) aucune vue ne **suffit** à elle seule ; (2) les deux vues ne sont pas **indépendantes sachant la classe** : elles décrivent le même tracé, et quand l'une se trompe, l'autre se trompe souvent de la même façon, au lieu de la corriger ; (3) 200 pseudo-étiquettes à 30 % de justesse **noient** les 30 vraies étiquettes. Les hypothèses de la section 8.2.3 sont des conditions, pas des détails.

### Application 8.5 — Quand les graphes échouent : et si l'on choisissait mieux les variables ?

**Objectif.** Reprendre le diagnostic de la section 8.2.6 (homophilie) sur les clients, et tester une idée : construire le graphe non sur les 49 variables, mais sur **six** variables de comportement.

**Étape 1 : l'homophilie selon les variables retenues.**

```python
from sklearn.neighbors import NearestNeighbors
c = pd.read_csv("donnees/clients_ml.csv")
colonnes = ["recence_jours", "nb_commandes_12m", "satisfaction_moy", "nb_tickets_support_12m", "nb_retours_12m", "part_achats_promo"]
X6 = c[colonnes].copy()
X6["satisfaction_moy"] = X6["satisfaction_moy"].fillna(X6["satisfaction_moy"].median())
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
A6, B6, a6, b6 = train_test_split(X6.to_numpy(), c["churn_90j"].to_numpy(), test_size=0.25, random_state=0, stratify=c["churn_90j"])
A6 = StandardScaler().fit(A6).transform(A6)

def homophilie(X, y, k=7):
    voisins = NearestNeighbors(n_neighbors=k + 1).fit(X).kneighbors(X, return_distance=False)[:, 1:]
    return (y[voisins] == y[:, None]).mean(), y[voisins[y == 1]].mean()

for nom, (X_, y_) in {"49 variables": (Xc, yc), "6 variables de comportement": (A6, a6)}.items():
    h, h1 = homophilie(X_, y_)
    print(f"{nom:28s} voisins de même étiquette : {h:.3f} | parmi les résiliations, voisins qui résilient : {h1:.3f}")
```
<!--sortie-->
```text
49 variables                 voisins de même étiquette : 0.805 | parmi les résiliations, voisins qui résilient : 0.269
6 variables de comportement  voisins de même étiquette : 0.822 | parmi les résiliations, voisins qui résilient : 0.358
```

**Étape 2 : la propagation sur ces deux graphes.** Même protocole qu'au livre (étiquettes tirées en respectant la proportion de résiliations ; AUC sur les clients non étiquetés atteints), 6 tirages.

```python
from sklearn.semi_supervised import LabelSpreading
from sklearn.metrics import roc_auc_score

def auc_propagation(X, y, nl, graines=6):
    res = []
    for s in range(graines):
        e = o.tirer_etiquettes(y, nl, np.random.default_rng(10 + s), stratifie=True)
        y_p = np.full(len(X), -1); y_p[e] = y[e]
        D = LabelSpreading(kernel="knn", n_neighbors=10, alpha=0.2, max_iter=100).fit(X, y_p).label_distributions_
        z = D.sum(axis=1)
        ok = (y_p == -1) & (z > 0)
        sup = LogisticRegression(max_iter=2000).fit(X[e], y[e]).predict_proba(X[ok])[:, 1]
        res.append((roc_auc_score(y[ok], D[ok, 1] / z[ok]), roc_auc_score(y[ok], sup)))
    return np.mean(res, axis=0)

for nl in (100, 300):
    for nom, (X_, y_) in {"49 variables": (Xc, yc), "6 variables": (A6, a6)}.items():
        p, s_ = auc_propagation(X_, y_, nl)
        print(f"{nl:3d} étiquettes, graphe sur {nom:12s} : AUC propagation {p:.3f} | AUC supervisé (mêmes points) {s_:.3f}")
```
<!--sortie-->
```text
100 étiquettes, graphe sur 49 variables : AUC propagation 0.527 | AUC supervisé (mêmes points) 0.727
100 étiquettes, graphe sur 6 variables  : AUC propagation 0.646 | AUC supervisé (mêmes points) 0.782
300 étiquettes, graphe sur 49 variables : AUC propagation 0.577 | AUC supervisé (mêmes points) 0.787
300 étiquettes, graphe sur 6 variables  : AUC propagation 0.681 | AUC supervisé (mêmes points) 0.810
```

**Lecture.** Avec six variables de comportement, le graphe est un peu plus « propre » : la part de voisins de même étiquette passe de 0,805 à 0,822, et surtout, parmi les clients qui résilient, la part de voisins qui résilient aussi passe de 0,269 à **0,358** (pour un taux de base de 0,14). La propagation en profite : son AUC passe de **0,527 à 0,646** (100 étiquettes) et de **0,577 à 0,681** (300). **Choisir les variables qui comptent aide beaucoup**, mais cela ne suffit pas : le modèle supervisé, évalué sur les mêmes clients, atteint **0,782** et **0,810**. Ici, la classe dépend de **seuils** et d'**interactions** (une récence supérieure à un seuil *et* une satisfaction basse, par exemple), qu'un graphe de proximité ne sait pas exprimer, alors qu'un modèle supervisé le peut.

### Application 8.6 — La boucle d'apprentissage actif, écrite à la main

**Objectif.** Écrire la boucle de la section 8.3.1 avec la stratégie de la marge, et la comparer au tirage au hasard sur les chiffres.

**Étape 1 : la boucle.** Elle part de `n0` étiquettes tirées au hasard, puis demande `lot` étiquettes à chaque tour, jusqu'au budget.

```python
def boucle(X, y, Xtest, ytest, strategie, n0=10, lot=10, budget=100, graine=0):
    rng = np.random.default_rng(graine)
    etiq = list(rng.choice(len(X), n0, replace=False))
    courbe = []
    while True:
        m = LogisticRegression(max_iter=1000).fit(X[etiq], y[etiq])
        courbe.append((len(etiq), m.score(Xtest, ytest)))
        if len(etiq) >= budget:
            return np.array(courbe)
        libres = np.setdiff1d(np.arange(len(X)), etiq)
        if strategie == "aleatoire":
            choix = rng.choice(libres, lot, replace=False)
        else:
            P = np.zeros((len(libres), 10))
            P[:, m.classes_] = m.predict_proba(X[libres])      # les classes jamais vues ont la probabilité 0
            tri = np.sort(P, axis=1)
            choix = libres[np.argsort(tri[:, -1] - tri[:, -2])[:lot]]   # petite marge = grande hésitation
        etiq += [int(i) for i in choix]
```

**Étape 2 : dix tirages par stratégie.**

```python
res = {st: np.array([boucle(Xp, yp, Xt, yt, st, graine=s)[:, 1] for s in range(10)]) for st in ("aleatoire", "marge")}
budgets = list(range(10, 101, 10))
tab = pd.DataFrame({"étiquettes": budgets, "aléatoire": res["aleatoire"].mean(axis=0), "marge": res["marge"].mean(axis=0)}).round(3)
print(tab.iloc[[1, 2, 4, 5, 9]].to_string(index=False))
d = res["marge"][:, 5] - res["aleatoire"][:, 5]
print("à 60 étiquettes : écart moyen", round(d.mean(), 3), "| tirages où la marge gagne :", int((d > 0).sum()), "sur 10")
```
<!--sortie-->
```text
 étiquettes  aléatoire  marge
         20      0.572  0.584
         30      0.646  0.727
         50      0.786  0.833
         60      0.834  0.874
        100      0.888  0.927
à 60 étiquettes : écart moyen 0.04 | tirages où la marge gagne : 8 sur 10
```

**Pour aller plus loin : la taille du lot.** Demander les étiquettes **une à une** est le plus efficace, mais le moins pratique (un réentraînement par étiquette). Que perd-on avec des lots plus gros ? (5 tirages, budget 100.)

```python
lignes = []
for lot in (1, 5, 10, 25):
    r = [boucle(Xp, yp, Xt, yt, "marge", lot=lot, budget=100, graine=s)[-1, 1] for s in range(5)]
    lignes.append((lot, np.mean(r)))
print(pd.DataFrame(lignes, columns=["taille du lot", "précision à 100 étiquettes"]).round(3).to_string(index=False))
```
<!--sortie-->
```text
 taille du lot  précision à 100 étiquettes
             1                       0.928
             5                       0.928
            10                       0.926
            25                       0.931
```

**Lecture.** Notre boucle retrouve le résultat du livre : la marge dépasse le hasard à 30 étiquettes (0,727 contre 0,646), à 60 (0,874 contre 0,834) et à 100 (0,927 contre 0,888). Mais l'**écart à 60 étiquettes est de 4 points** (la marge gagne dans 8 tirages sur 10), contre 7 points et 10 tirages sur 10 dans le livre : ici le jeu initial est tiré avec le même générateur que les tirages aléatoires, donc les 10 tirages ne sont pas les mêmes. Le **sens** du résultat est stable ; son **amplitude** dépend du détail du protocole, d'où l'intérêt de répéter. Pour la taille du lot, **rien de mesurable** : 0,928 (lots de 1 ou de 5), 0,926 (10), 0,931 (25), des différences très inférieures à la variabilité entre tirages (5 tirages seulement). À ce budget, on peut demander les étiquettes par gros lots sans rien perdre.

### Application 8.7 — Comité et densité

**Objectif.** Écrire à la main les deux critères des sections 8.3.3 et 8.3.4, puis les faire tourner dans la même boucle (`o.boucle_active` est la boucle de l'application précédente, avec ces critères branchés dedans).

**Étape 1 : les deux scores.**

```python
def score_comite(Xl, yl, Xlibres, nb_membres=5, graine=0):
    rng = np.random.default_rng(graine)
    votes = []
    for _ in range(nb_membres):
        b = rng.choice(len(Xl), len(Xl), replace=True)                    # rééchantillonnage avec remise
        votes.append(LogisticRegression(max_iter=1000).fit(Xl[b], yl[b]).predict(Xlibres))
    votes = np.array(votes)
    freq = np.stack([(votes == k).mean(axis=0) for k in range(10)], axis=1)
    return -(freq * np.log(freq + 1e-12)).sum(axis=1)                      # entropie du vote

def densite(X, nb_ref=400, graine=0):
    ref = X[np.random.default_rng(graine).choice(len(X), nb_ref, replace=False)]
    A = X / np.linalg.norm(X, axis=1, keepdims=True); B = ref / np.linalg.norm(ref, axis=1, keepdims=True)
    return (A @ B.T).mean(axis=1)                                          # similarité cosinus moyenne

m = LogisticRegression(max_iter=1000).fit(Xp[:30], yp[:30])
print("désaccord maximal du comité sur 5 modèles :", round(score_comite(Xp[:30], yp[:30], Xp[30:], 5).max(), 3), "(ln 5 = 1,609)")
print("densité : minimum", round(densite(Xp).min(), 3), "| médiane", round(np.median(densite(Xp)), 3), "| maximum", round(densite(Xp).max(), 3))
```
<!--sortie-->
```text
désaccord maximal du comité sur 5 modèles : 1.609 (ln 5 = 1,609)
densité : minimum 0.548 | médiane 0.689 | maximum 0.788
```

**Étape 2 : l'effet du nombre de membres et de l'exposant de densité.** (5 tirages, 10 étiquettes de départ, lots de 10, budget 60.)

```python
def precision_a_60(strategie, **kw):
    r = []
    for s in range(5):
        idx0 = o.tirer_etiquettes(yp, 10, np.random.default_rng(500 + s))
        r.append(o.boucle_active(Xp, yp, Xt, yt, strategie, idx0, 10, 60, graine=s, k=10, **kw)[-1, 1])
    return np.mean(r)

lignes = [("aléatoire", precision_a_60("aleatoire")), ("marge", precision_a_60("marge"))]
for M in (3, 5, 15):
    lignes.append((f"comité de {M} modèles", precision_a_60("comite", nb_comite=M)))
for beta in (0.0, 1.0, 2.0):
    lignes.append((f"entropie × densité^{beta:g}", precision_a_60("densite", beta=beta)))
print(pd.DataFrame(lignes, columns=["stratégie", "précision à 60 étiquettes"]).round(3).to_string(index=False))
```
<!--sortie-->
```text
           stratégie  précision à 60 étiquettes
           aléatoire                      0.778
               marge                      0.880
 comité de 3 modèles                      0.828
 comité de 5 modèles                      0.823
comité de 15 modèles                      0.860
entropie × densité^0                      0.743
entropie × densité^1                      0.731
entropie × densité^2                      0.712
```

**Lecture.** À 60 étiquettes (5 tirages) : tirage au hasard **0,778**, marge **0,880**. Le comité est entre les deux : **0,828** avec 3 modèles, **0,823** avec 5, **0,860** avec 15. Plus de membres aident plutôt (15 contre 3 ou 5), avec un coût proportionnel et un bruit d'échantillonnage non négligeable sur 5 tirages. Côté densité, l'exposant $\beta=0$ revient à l'entropie seule (**0,743**, sous le hasard) ; $\beta=1$ donne 0,731 et $\beta=2$ donne 0,712 : sur les chiffres, **plus on pondère par la densité, plus c'est mauvais**, ce qui confirme le constat du livre (8.3.5).

### Application 8.8 — Biais d'échantillonnage, démarrage à froid et coût

**Objectif.** Sur les clients de la boutique, reproduire le biais de la section 8.3.6, le corriger par un échantillon aléatoire, puis chiffrer le tout en euros.

**Étape 1 : la stratégie d'incertitude sur les clients.** 5 tirages, 40 étiquettes de départ, lots de 20, budget 300 ; le modèle final de chaque tirage est conservé.

```python
resultats = {}
for st in ("aleatoire", "incertitude"):
    lignes = []
    for s in range(5):
        idx0 = o.tirer_etiquettes(yc, 40, np.random.default_rng(700 + s), stratifie=True)
        courbe, etiq = o.boucle_active(Xc, yc, Xct, yct, st, idx0, 20, 300, graine=s, k=2, metrique="auc", renvoyer_etiq=True)
        m = LogisticRegression(max_iter=1000).fit(Xc[etiq], yc[etiq])
        lignes.append((courbe[-1, 1], yc[etiq].mean(), m.predict_proba(Xct)[:, 1].mean(), m, etiq))
    resultats[st] = lignes
    print(f"{st:12s} AUC {np.mean([l[0] for l in lignes]):.3f} | part de résiliations parmi les étiquetés {np.mean([l[1] for l in lignes]):.3f} | probabilité moyenne prédite {np.mean([l[2] for l in lignes]):.3f}")
print("taux réel dans le test :", round(yct.mean(), 3))
```
<!--sortie-->
```text
aleatoire    AUC 0.813 | part de résiliations parmi les étiquetés 0.148 | probabilité moyenne prédite 0.142
incertitude  AUC 0.829 | part de résiliations parmi les étiquetés 0.371 | probabilité moyenne prédite 0.077
taux réel dans le test : 0.14
```

**Étape 2 : recalibrer avec 200 étiquettes aléatoires de plus.** On ajuste une régression logistique à une variable sur le score du modèle (mise à l'échelle de Platt).

```python
from sklearn.metrics import brier_score_loss
lignes = []
for st, res in resultats.items():
    av, ap, ba, bp = [], [], [], []
    for s, (_, _, _, m, etiq) in enumerate(res):
        libres = np.setdiff1d(np.arange(len(Xc)), etiq)
        cal = np.random.default_rng(900 + s).choice(libres, 200, replace=False)
        platt = LogisticRegression(C=1e6).fit(m.decision_function(Xc[cal]).reshape(-1, 1), yc[cal])
        p0 = m.predict_proba(Xct)[:, 1]
        p1 = platt.predict_proba(m.decision_function(Xct).reshape(-1, 1))[:, 1]
        av.append(p0.mean()); ap.append(p1.mean()); ba.append(brier_score_loss(yct, p0)); bp.append(brier_score_loss(yct, p1))
    lignes.append((st, np.mean(av), np.mean(ap), np.mean(ba), np.mean(bp)))
print(pd.DataFrame(lignes, columns=["stratégie", "proba moyenne avant", "après", "Brier avant", "après"]).round(4).to_string(index=False))
```
<!--sortie-->
```text
  stratégie  proba moyenne avant  après  Brier avant  après
  aleatoire               0.1419 0.1394       0.1078 0.0994
incertitude               0.0771 0.1293       0.1079 0.0957
```

**Étape 3 : le démarrage à froid, en nombre de classes couvertes.** Combien de chiffres différents contiennent 10 images tirées au hasard, comparé aux 10 médoïdes d'un k-means ?

```python
rng = np.random.default_rng(0)
alea = np.mean([len(set(yp[rng.choice(len(Xp), 10, replace=False)])) for _ in range(1000)])
med = np.mean([len(set(yp[o.init_medoides(Xp, 10, graine=s)])) for s in range(10)])
print("classes couvertes : tirage aléatoire", round(alea, 2), "| médoïdes", round(med, 2))
```
<!--sortie-->
```text
classes couvertes : tirage aléatoire 6.54 | médoïdes 9.2
```

**Étape 4 : le coût.** Avec 4 € par étiquette, 200 étiquettes de calibrage et une économie de $s$ étiquettes grâce à la stratégie active, à partir de quelle économie $s$ l'opération est-elle rentable **si l'on a besoin de probabilités calibrées** ? Et si l'on ne veut que classer ?

```python
cout_etiquette, etiquettes_calibrage = 4.0, 200
print("économie minimale pour amortir le calibrage :", etiquettes_calibrage, "étiquettes (", cout_etiquette * etiquettes_calibrage, "€ )")
print("si l'on ne veut que classer : toute économie est bonne à prendre (aucun calibrage nécessaire)")
```
<!--sortie-->
```text
économie minimale pour amortir le calibrage : 200 étiquettes ( 800.0 € )
si l'on ne veut que classer : toute économie est bonne à prendre (aucun calibrage nécessaire)
```

**Lecture.** **Biais.** Avec 300 étiquettes (5 tirages), l'AUC est de 0,829 pour l'incertitude et de 0,813 pour le hasard. Mais la part de résiliations parmi les clients étiquetés est de **0,371** (contre 0,148 pour le hasard) et la probabilité moyenne prédite est de **0,077** (contre 0,142 pour le hasard) alors que le taux réel est de 0,14. **Recalibrage.** Avec seulement 200 étiquettes aléatoires de plus, la probabilité moyenne du modèle actif remonte à **0,129** (pas tout à fait 0,14 : 200 étiquettes sont peu ; le livre en utilise 300 et atteint 0,141), et son score de Brier passe de 0,1079 à **0,0957**, meilleur que celui du modèle aléatoire recalibré (0,0994). **Démarrage à froid.** 10 images aléatoires couvrent 6,5 chiffres sur 10, 10 médoïdes en couvrent 9,2. **Coût.** À 4 € l'étiquette, le calibrage de 200 étiquettes coûte 800 € : le choix actif doit donc économiser *plus de 200 étiquettes* pour être rentable si l'on a besoin de probabilités fiables ; s'il ne s'agit que de classer, le calibrage est inutile et toute économie est bonne à prendre.

## Exercices

### Exercice 8.1 ⭐ — Une étape d'EM dur à la main (section 8.1.2)

Une seule variable $x$, deux classes A et B. Deux points étiquetés : A en $-1$, B en $+0{,}4$. Six points sans étiquette : $-2{,}2$, $-1{,}9$, $-1{,}5$, $+1{,}2$, $+1{,}6$, $+2{,}1$. (a) Où est la frontière « milieu des deux points étiquetés » ? (b) Étiquetez provisoirement les six points, recalculez les centres, puis la frontière. (c) Une deuxième étape change-t-elle quelque chose ?

### Exercice 8.2 ⭐⭐ — Combien de tirages ? (section 8.1.5)

À 10 étiquettes, la précision d'un modèle supervisé a un écart-type de 0,082 d'un tirage à l'autre. (a) Quelle est l'erreur-type de la moyenne de 10 tirages ? (b) Combien de tirages faut-il pour connaître la moyenne à ± 0,01 (une erreur-type) ? (c) Pourquoi une comparaison **appariée** (mêmes étiquettes pour les deux méthodes) demande-t-elle en général moins de tirages ?

### Exercice 8.3 ⭐⭐ — Quelle hypothèse est en jeu ? (section 8.1.3)

Pour chaque situation, dites laquelle des quatre hypothèses (lissage, groupes, basse densité, variété) est en jeu, et si elle est plausible. (a) Classer des photos de produits en défaut ou non, avec 30 photos étiquetées et 20 000 sans étiquette, les photos de produits défectueux formant un groupe visuellement distinct. (b) Prédire la résiliation des clients à partir de 49 variables de natures très différentes. (c) Reconnaître des gestes de la main à partir de capteurs : les gestes forment des trajectoires continues dans un espace de grande dimension. (d) Séparer deux populations dont les distributions se chevauchent presque entièrement.

### Exercice 8.4 ⭐ — Pseudo-étiquettes et erreurs attendues (section 8.2.1)

Un modèle produit, pour cinq points sans étiquette, les confiances suivantes : $0{,}97$, $0{,}93$, $0{,}91$, $0{,}88$, $0{,}55$. (a) Avec un seuil de $0{,}9$, quels points sont pseudo-étiquetés ? (b) Si ces confiances étaient de vraies probabilités, combien d'erreurs attend-on parmi les points ajoutés ? (c) Sur les chiffres, au seuil 0,8, la part de pseudo-étiquettes justes était de 0,73 (livre, 8.2.1). Que dit-elle de la calibration du modèle ?

### Exercice 8.5 ⭐⭐ — Propagation sur quatre nœuds (section 8.2.4)

Chaîne de quatre nœuds $1-2-3-4$ (arêtes $1$–$2$, $2$–$3$, $3$–$4$, poids 1). Le nœud 1 est étiqueté A, le nœud 4 est étiqueté B. Avec $\alpha=0{,}5$ : (a) calculez les degrés et la matrice $S$ ; (b) calculez le premier tour de la diffusion pour la colonne A ; (c) calculez la solution fermée $F^*$ (à la machine) et les classes ; (d) expliquez le résultat.

### Exercice 8.6 ⭐⭐⭐ — Pourquoi la propagation converge (section 8.2.4)

Montrez que les valeurs propres de $S=D^{-1/2}WD^{-1/2}$ sont de module au plus 1, puis que la récurrence $F^{(t+1)}=\alpha SF^{(t)}+(1-\alpha)Y$ converge vers $(1-\alpha)(I-\alpha S)^{-1}Y$ pour tout $\alpha\in]0,1[$.

### Exercice 8.7 ⭐ — Trois critères, un classement (section 8.3.2)

Trois candidats, trois classes : a $=(0{,}7;\ 0{,}2;\ 0{,}1)$, b $=(0{,}4;\ 0{,}4;\ 0{,}2)$, c $=(0{,}34;\ 0{,}33;\ 0{,}33)$. Calculez pour chacun la confiance minimale, l'écart entre les deux meilleures classes et l'entropie, puis classez-les du plus utile au moins utile selon chaque critère.

### Exercice 8.8 ⭐⭐ — Équivalence à deux classes (section 8.3.2)

Pour **deux** classes, avec $p=P(1\mid x)$, montrez que la confiance minimale, la marge et l'entropie classent les points dans le même ordre.

### Exercice 8.9 ⭐⭐ — Entropie du vote (section 8.3.3)

Un comité de 7 modèles vote entre 3 classes. Calculez l'entropie du vote pour les répartitions $(7,0,0)$, $(4,2,1)$ et $(3,3,1)$ et classez-les.

### Exercice 8.10 ⭐⭐ — Un test des signes (section 8.3.5)

Sur 10 tirages, la marge fait mieux que le hasard à 60 étiquettes dans les 10 tirages (livre, 8.3.5). Sous l'hypothèse « aucune différence », chaque tirage donne l'avantage à l'une ou l'autre stratégie avec probabilité 1/2. Quelle est la probabilité d'un résultat aussi extrême (10 sur 10 dans un sens ou dans l'autre) ? Que conclure ? Quelles sont les limites de ce raisonnement ?

### Exercice 8.11 ⭐⭐⭐ — Corriger le biais d'échantillonnage par les proportions ? (section 8.3.6)

Un modèle est entraîné sur un jeu où la part de positifs est $\pi_s$ alors que la vraie part est $\pi$. (a) Si le jeu a été obtenu en **sur-échantillonnant** les positifs, indépendamment des variables $x$, montrez que les cotes (*odds*) du modèle sont à corriger d'un facteur $\dfrac{\pi/(1-\pi)}{\pi_s/(1-\pi_s)}$. (b) Vérifiez-le par simulation sur les clients. (c) Appliquez la même correction au modèle entraîné par **apprentissage actif** (stratégie d'incertitude, 400 étiquettes, 38 % de positifs). Que constatez-vous ? Expliquez.

### Exercice 8.12 ⭐⭐ — Quand l'apprentissage actif est-il rentable ? (section 8.3.8)

Mettre en place une boucle active coûte, une fois, 1 000 € d'ingénierie. Chaque projet économise ensuite 60 étiquettes à 4 € l'unité. (a) Combien de projets pour amortir l'investissement ? (b) Même question si chaque étiquette ne coûte que 0,40 € et que l'économie est de 50 étiquettes. (c) Quel autre coût faut-il compter si l'on a besoin de probabilités calibrées ?

## Corrigés

### Corrigé 8.1

(a) La frontière est au milieu de $-1$ et $0{,}4$ : $\dfrac{-1+0{,}4}{2}=-0{,}3$.

(b) Les trois points de gauche ($-2{,}2$, $-1{,}9$, $-1{,}5$) sont à gauche de $-0{,}3$ : provisoirement A. Les trois points de droite sont B. Nouveaux centres : $\bar x_A=\dfrac{-1-2{,}2-1{,}9-1{,}5}{4}=-1{,}65$ et $\bar x_B=\dfrac{0{,}4+1{,}2+1{,}6+2{,}1}{4}=1{,}325$. Nouvelle frontière : $\dfrac{-1{,}65+1{,}325}{2}=-0{,}1625$.

(c) Aucun point ne change de côté de $-0{,}1625$ : l'étape est **stable**, l'algorithme a convergé. La frontière est passée de $-0{,}3$ à $-0{,}1625$, soit plus près du creux (autour de $0$ si les classes sont symétriques).

```python
a, b = -1.0, 0.4
U = np.array([-2.2, -1.9, -1.5, 1.2, 1.6, 2.1])
f = (a + b) / 2
for tour in range(1, 4):
    A = [a] + [u for u in U if u < f]
    B = [b] + [u for u in U if u >= f]
    f_nouveau = (np.mean(A) + np.mean(B)) / 2
    print("tour", tour, ": centres", round(np.mean(A), 4), round(np.mean(B), 4), "| frontière", round(f_nouveau, 4))
    f = f_nouveau
```
<!--sortie-->
```text
tour 1 : centres -1.65 1.325 | frontière -0.1625
tour 2 : centres -1.65 1.325 | frontière -0.1625
tour 3 : centres -1.65 1.325 | frontière -0.1625
```

### Corrigé 8.2

(a) $0{,}082/\sqrt{10}\approx0{,}026$. (b) On veut $0{,}082/\sqrt n\le0{,}01$, soit $n\ge(0{,}082/0{,}01)^2=67{,}24$ : **68 tirages**. (c) Quand les deux méthodes reçoivent les **mêmes étiquettes**, la variabilité due au tirage affecte les deux de la même façon et **s'annule en grande partie dans la différence** : l'écart-type de la *différence* est bien plus faible que celui de chaque précision, donc moins de tirages suffisent pour détecter un écart.

```python
print("erreur-type pour 10 tirages :", round(0.082 / np.sqrt(10), 3), "| tirages pour 0,01 :", int(np.ceil((0.082 / 0.01) ** 2)))
```
<!--sortie-->
```text
erreur-type pour 10 tirages : 0.026 | tirages pour 0,01 : 68
```

### Corrigé 8.3

(a) **Groupes** (et basse densité) : les défauts forment un groupe distinct, la frontière passe dans le creux : plausible, le semi-supervisé a de bonnes chances d'aider. (b) **Lissage** : « deux clients proches ont la même réaction » est **douteux** quand les variables sont de natures très différentes et que la classe dépend de seuils et d'interactions (livre, 8.2.6). Prudence. (c) **Variété** : des trajectoires continues dans un grand espace, le graphe de voisinage est adapté : plausible. (d) **Aucune** n'est vérifiée : il n'y a pas de creux, la forme de $p(x)$ ne renseigne pas sur la frontière : le semi-supervisé n'apportera rien (voire nuira).

### Corrigé 8.4

(a) Aux confiances $\ge0{,}9$ : les trois premiers points ($0{,}97$, $0{,}93$, $0{,}91$). (b) Si ces confiances étaient exactes, les erreurs attendues seraient $(1-0{,}97)+(1-0{,}93)+(1-0{,}91)=0{,}03+0{,}07+0{,}09=0{,}19$ sur 3 points, soit **6,3 %**. (c) Au seuil 0,8, le modèle annonce **au moins 80 %** de confiance sur chaque pseudo-étiquette, donc il devrait avoir raison au moins 80 % du temps. Il n'a raison que dans 73 % des cas : il est **trop sûr de lui** (mal calibré, section 5.2), ce qui explique le biais de confirmation.

### Corrigé 8.5

(a) Degrés : $d=(1,2,2,1)$. $S_{12}=\dfrac1{\sqrt{1\cdot2}}\approx0{,}7071$, $S_{23}=\dfrac1{\sqrt{2\cdot2}}=0{,}5$, $S_{34}=\dfrac1{\sqrt{2\cdot1}}\approx0{,}7071$. (b) Colonne A, $F^{(0)}=(1,0,0,0)$ : nœud 1 : $0{,}5\cdot1=0{,}5$ (le terme de voisinage est nul au départ) ; nœud 2 : $0{,}5\cdot0{,}7071\cdot1\approx0{,}354$ ; nœuds 3 et 4 : $0$.

```python
W = np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], float)
d = W.sum(axis=1)
S = W / np.sqrt(np.outer(d, d))
Y = np.zeros((4, 2)); Y[0, 0] = 1; Y[3, 1] = 1
al = 0.5
F1 = al * S @ Y + (1 - al) * Y
Fs = (1 - al) * np.linalg.inv(np.eye(4) - al * S) @ Y
print("S =\n", S.round(4)); print("tour 1, colonne A :", F1[:, 0].round(3))
print("F* (A, B) :\n", Fs.round(3)); print("classes :", np.array(list("AB"))[Fs.argmax(axis=1)])
```
<!--sortie-->
```text
S =
 [[0.     0.7071 0.     0.    ]
 [0.7071 0.     0.5    0.    ]
 [0.     0.5    0.     0.7071]
 [0.     0.     0.7071 0.    ]]
tour 1, colonne A : [0.5   0.354 0.    0.   ]
F* (A, B) :
 [[0.578 0.022]
 [0.22  0.063]
 [0.063 0.22 ]
 [0.022 0.578]]
classes : ['A' 'A' 'B' 'B']
```

(c) et (d) : voir la sortie ci-dessus. La chaîne étant **symétrique**, les nœuds 2 et 3 sont les symétriques l'un de l'autre : le nœud 2, plus proche de 1, reçoit A ; le nœud 3, plus proche de 4, reçoit B ; la frontière est exactement au milieu de l'arête $2$–$3$.

### Corrigé 8.6

**Valeurs propres de $S$.** Posons $P=D^{-1}W$ : ses entrées sont positives et chaque ligne somme à 1 (matrice **stochastique**). Si $Pv=\lambda v$ et $i$ est l'indice de la composante de $v$ de plus grand module, $|\lambda||v_i|=\bigl|\sum_jP_{ij}v_j\bigr|\le\sum_jP_{ij}|v_j|\le|v_i|$, donc $|\lambda|\le1$. Or $S=D^{1/2}PD^{-1/2}$ est **semblable** à $P$ : mêmes valeurs propres. Donc toutes celles de $S$ sont dans $[-1,1]$.

**Convergence.** Le rayon spectral de $\alpha S$ est au plus $\alpha<1$, donc $(\alpha S)^t\to0$. En dépliant, $F^{(t)}=(\alpha S)^tY+(1-\alpha)\sum_{s=0}^{t-1}(\alpha S)^sY$. Le premier terme tend vers 0, et la série de Neumann $\sum_s(\alpha S)^s$ converge vers $(I-\alpha S)^{-1}$ (car $I-\alpha S$ est inversible, ses valeurs propres étant $1-\alpha\lambda\ge1-\alpha>0$). D'où $F^{(t)}\to(1-\alpha)(I-\alpha S)^{-1}Y$. Vérification numérique sur le graphe à six nœuds du livre :

```python
W6 = np.zeros((6, 6))
for i, j in [(0, 1), (0, 2), (1, 2), (2, 3), (3, 4), (3, 5), (4, 5)]:
    W6[i, j] = W6[j, i] = 1
d6 = W6.sum(axis=1); S6 = W6 / np.sqrt(np.outer(d6, d6))
Y6 = np.zeros((6, 2)); Y6[0, 0] = 1; Y6[5, 1] = 1
F = Y6.copy()
for t in range(60):
    F = 0.5 * S6 @ F + 0.5 * Y6
Fstar = 0.5 * np.linalg.inv(np.eye(6) - 0.5 * S6) @ Y6
print("valeurs propres de S dans [-1, 1] :", np.linalg.eigvalsh(S6).round(3))
print("écart maximal entre l'itération (60 tours) et la solution fermée :", float(np.abs(F - Fstar).max()))
```
<!--sortie-->
```text
valeurs propres de S dans [-1, 1] : [-0.629 -0.5   -0.5   -0.167  0.795  1.   ]
écart maximal entre l'itération (60 tours) et la solution fermée : 1.1102230246251565e-16
```

### Corrigé 8.7

```python
cand = {"a": [0.7, 0.2, 0.1], "b": [0.4, 0.4, 0.2], "c": [0.34, 0.33, 0.33]}
lignes = []
for nom, p in cand.items():
    p = np.array(p)
    tri = np.sort(p)[::-1]
    lignes.append((nom, 1 - tri[0], tri[0] - tri[1], -(p * np.log(p)).sum()))
tab = pd.DataFrame(lignes, columns=["candidat", "1 - max", "écart", "entropie"]).set_index("candidat")
print(tab.round(4).to_string())
print("classement par confiance minimale :", list(tab["1 - max"].sort_values(ascending=False).index))
print("classement par marge             :", list(tab["écart"].sort_values().index))
print("classement par entropie          :", list(tab["entropie"].sort_values(ascending=False).index))
```
<!--sortie-->
```text
          1 - max  écart  entropie
candidat                          
a            0.30   0.50    0.8018
b            0.60   0.00    1.0549
c            0.66   0.01    1.0985
classement par confiance minimale : ['c', 'b', 'a']
classement par marge             : ['b', 'c', 'a']
classement par entropie          : ['c', 'b', 'a']
```

Le candidat b a **exactement** deux classes à égalité (0,4 et 0,4) : la marge est nulle, elle le désigne comme le plus incertain. Le candidat c est presque uniforme sur les trois classes : la confiance minimale et l'entropie le placent en tête. Seule la marge les départage différemment.

### Corrigé 8.8

Pour deux classes, $P(1\mid x)=p$ et $P(0\mid x)=1-p$. La confiance minimale vaut $1-\max(p,1-p)=\tfrac12-\bigl|p-\tfrac12\bigr|$ ; la marge (écart entre les deux meilleures) vaut $|2p-1|=2\bigl|p-\tfrac12\bigr|$ ; l'entropie $H(p)=-p\ln p-(1-p)\ln(1-p)$ est une fonction **symétrique** autour de $\tfrac12$ et **décroissante en $|p-\tfrac12|$** (sa dérivée $\ln\frac{1-p}{p}$ est positive pour $p<\tfrac12$). Les trois sont donc des fonctions **monotones** de la distance $|p-\tfrac12|$ : ils classent les points dans le même ordre (le plus incertain étant celui dont $p$ est le plus proche de $\tfrac12$).

### Corrigé 8.9

```python
for votes in [(7, 0, 0), (4, 2, 1), (3, 3, 1)]:
    f = np.array(votes) / 7
    f = f[f > 0]
    print(votes, "entropie du vote :", round(float(-(f * np.log(f)).sum()), 4))
```
<!--sortie-->
```text
(7, 0, 0) entropie du vote : -0.0
(4, 2, 1) entropie du vote : 0.9557
(3, 3, 1) entropie du vote : 1.0042
```

Le classement, du plus utile au moins utile : $(3,3,1)$ (deux classes presque à égalité, une troisième marginale), puis $(4,2,1)$, puis $(7,0,0)$ (unanimité : score nul, rien à apprendre du désaccord).

### Corrigé 8.10

La probabilité que les 10 tirages donnent l'avantage à la **même** stratégie, dans un sens ou dans l'autre, est $2\times(1/2)^{10}=2/1024\approx0{,}002$ : très peu probable si les deux stratégies étaient équivalentes. On peut donc écarter l'hypothèse « aucune différence » à 60 étiquettes sur ces données. **Limites** : le test des signes ignore la **taille** des écarts ; les 10 tirages partagent le même jeu de test et le même réservoir, donc ne sont pas indépendants au sens strict ; le résultat vaut pour **ces** données, ce modèle et ce budget, pas en général.

```python
from scipy.stats import binom
print("P(10 sur 10 dans un sens ou l'autre) =", round(2 * binom.pmf(10, 10, 0.5), 5))
```
<!--sortie-->
```text
P(10 sur 10 dans un sens ou l'autre) = 0.00195
```

### Corrigé 8.11

(a) Si la sélection d'un point dépend **seulement** de son étiquette $y$ (pas de $x$), alors $P_s(x\mid y)=P(x\mid y)$ et seule la proportion de classes change. Par Bayes, $\dfrac{P_s(1\mid x)}{P_s(0\mid x)}=\dfrac{P(x\mid1)\,\pi_s}{P(x\mid0)\,(1-\pi_s)}$, tandis que $\dfrac{P(1\mid x)}{P(0\mid x)}=\dfrac{P(x\mid1)\,\pi}{P(x\mid0)\,(1-\pi)}$. D'où $\text{cotes vraies}=\text{cotes du modèle}\times\dfrac{\pi/(1-\pi)}{\pi_s/(1-\pi_s)}$.

(b) et (c) : on le vérifie sur les clients, d'abord pour un sur-échantillonnage des positifs indépendant de $x$ (cas (a)), puis pour le jeu étiqueté par apprentissage actif.

```python
def corriger(p, pi_s, pi=0.14):
    cotes = p / (1 - p) * (pi / (1 - pi)) / (pi_s / (1 - pi_s))
    return cotes / (1 + cotes)

res_a, res_b = [], []
for s in range(10):
    rng = np.random.default_rng(1000 + s)
    pos, neg = np.where(yc == 1)[0], np.where(yc == 0)[0]
    e = np.r_[rng.choice(pos, 150, replace=False), rng.choice(neg, 250, replace=False)]      # 37,5 % de positifs, tirés sans regarder x
    p = LogisticRegression(max_iter=1000).fit(Xc[e], yc[e]).predict_proba(Xct)[:, 1]
    res_a.append((p.mean(), corriger(p, yc[e].mean()).mean()))
    idx0 = o.tirer_etiquettes(yc, 40, np.random.default_rng(700 + s), stratifie=True)
    _, ea = o.boucle_active(Xc, yc, Xct, yct, "incertitude", idx0, 20, 400, graine=s, k=2, metrique="auc", renvoyer_etiq=True)
    pa = LogisticRegression(max_iter=1000).fit(Xc[ea], yc[ea]).predict_proba(Xct)[:, 1]
    res_b.append((pa.mean(), corriger(pa, yc[ea].mean()).mean(), yc[ea].mean()))
print("sur-échantillonnage aléatoire : proba moyenne avant", round(np.mean([r[0] for r in res_a]), 3), "| après correction", round(np.mean([r[1] for r in res_a]), 3))
print("apprentissage actif           : proba moyenne avant", round(np.mean([r[0] for r in res_b]), 3), "| après correction", round(np.mean([r[1] for r in res_b]), 3), "| part de positifs", round(np.mean([r[2] for r in res_b]), 3))
print("taux réel :", round(yct.mean(), 3))
```
<!--sortie-->
```text
sur-échantillonnage aléatoire : proba moyenne avant 0.279 | après correction 0.152
apprentissage actif           : proba moyenne avant 0.078 | après correction 0.046 | part de positifs 0.384
taux réel : 0.14
```

**Résultats.** Pour un **sur-échantillonnage aléatoire** des positifs (37,5 % de positifs), le modèle brut **surestime** le risque (probabilité moyenne 0,279) et la correction de la question (a) le ramène à **0,152**, proche du taux réel de 0,14 : la correction marche, comme prévu. Pour le jeu étiqueté par **apprentissage actif** (38,4 % de positifs), c'est l'inverse : le modèle brut **sous-estime** le risque (0,078) et la correction l'abaisse encore, à **0,046**, plus loin de la vérité. Le biais de l'apprentissage actif n'est donc **pas** un simple changement de proportion de classes. Les points ont été choisis en fonction de leurs **variables** $x$ (ils sont près de la frontière du modèle), si bien que l'hypothèse de la question (a), « la sélection ne dépend que de $y$ », est fausse ; la correction par les proportions ne s'applique pas. Nous n'avons pas isolé par une expérience le mécanisme exact de la sous-estimation. Le remède éprouvé est celui du livre : **recalibrer sur un petit échantillon aléatoire**.

### Corrigé 8.12

(a) Une économie de $60\times4=240$ € par projet : $1\,000/240\approx4{,}2$, soit **5 projets**. (b) Économie de $50\times0{,}40=20$ € par projet : $1\,000/20=50$ projets. (c) Si l'on a besoin de **probabilités calibrées**, il faut compter les étiquettes **aléatoires** supplémentaires du recalibrage (livre, 8.3.6 : 300 étiquettes, soit 1 200 € à 4 € l'unité), qui peuvent dépasser l'économie réalisée sur le choix des points ; il faut aussi compter le coût de **maintenance** du système (réentraînement, files d'attente d'annotation).

```python
import math
print("projets pour amortir (cas a) :", math.ceil(1000 / (60 * 4)), "| (cas b) :", math.ceil(1000 / (50 * 0.40)))
```
<!--sortie-->
```text
projets pour amortir (cas a) : 5 | (cas b) : 50
```
