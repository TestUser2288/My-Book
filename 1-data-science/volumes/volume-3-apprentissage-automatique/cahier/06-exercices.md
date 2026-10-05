# Chapitre 6 : ➕ Détection d'anomalies et de fraude — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 6 du livre (chapitre complémentaire). Les **applications** reprennent pas à pas, avec le code complet, ce que le livre n'a fait que résumer : mesurer un détecteur sous déséquilibre extrême, les scores de distance et de densité, une forêt d'isolement écrite à la main, l'autoencodeur et l'ACP, et le tri des alertes. Les **exercices** sont corrigés à la fin du chapitre. Données : `donnees/transactions.csv` (60 000 commandes, 0,8 % de fraude, deux types). Le chapitre est **autonome** : il recharge ses données et refait la séparation apprentissage/test du livre ; mais ses applications s'appuient les unes sur les autres (une fonction définie dans une application sert aux suivantes), il faut donc les exécuter dans l'ordre.

## Préparation

Une première cellule charge les bibliothèques et construit les dix variables du livre (avec l'heure codée par un cercle, car 23 h est voisine de 0 h) ; la suivante fait la séparation apprentissage/test (graine 0, stratifiée sur la fraude), standardise, et prépare un échantillon de référence de 10 000 commandes pour les méthodes de voisinage.

```python
import sys, warnings
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import average_precision_score, roc_auc_score
sys.path.insert(0, "build"); import style; style.setup()       # style des figures du volume
warnings.filterwarnings("ignore")

t = pd.read_csv("donnees/transactions.csv")
X = pd.DataFrame({
    "log_montant": np.log(t["montant"]),
    "sin_heure": np.sin(2 * np.pi * t["heure"] / 24), "cos_heure": np.cos(2 * np.pi * t["heure"] / 24),
    "log_distance": np.log1p(t["distance_facturation_livraison_km"]), "nb_cmd_24h": t["nb_commandes_24h"],
    "log_age_compte": np.log1p(t["age_compte_jours"]), "ip_different": t["ip_pays_different"],
    "appareil_inconnu": 1 - t["appareil_connu"], "log_delai": np.log1p(t["delai_depuis_derniere_cmd_h"]), "nb_articles": t["nb_articles"]})
print(X.shape, "| fraudes :", int(t["fraude"].sum()), "soit", round(100 * t["fraude"].mean(), 2), "%")
```
<!--sortie-->
```text
(60000, 10) | fraudes : 486 soit 0.81 %
```

```python
(X_app, X_test, y_app, y_test, type_app, type_test, montant_app, montant_test) = train_test_split(
    X, t["fraude"].values, t["type_fraude"].values, t["montant"].values, test_size=0.3, random_state=0, stratify=t["fraude"].values)
scaler = StandardScaler().fit(X_app)
Z_app, Z_test = scaler.transform(X_app), scaler.transform(X_test)
reference = np.random.default_rng(0).choice(len(Z_app), 10000, replace=False)
valid = np.setdiff1d(np.arange(len(Z_app)), reference)            # 32 000 commandes étiquetées, pour régler les méthodes
Z_val, y_val = Z_app[valid], y_app[valid]
budget = int(np.ceil(0.01 * len(y_test)))                          # 180 alertes : 1 % du jeu de test
R = {}
def evaluer(nom, score):
    """AUC, AP, précision au budget, et part des fraudes de chaque type retrouvées parmi les `budget` alertes."""
    alertes = np.argsort(-score)[:budget]
    R[nom] = dict(AUC=roc_auc_score(y_test, score), AP=average_precision_score(y_test, score), precision=y_test[alertes].mean(),
                  rappel1=np.isin(np.where(type_test == 1)[0], alertes).mean(), rappel2=np.isin(np.where(type_test == 2)[0], alertes).mean())
    return {k: round(float(v), 3) for k, v in R[nom].items()}
print("apprentissage :", len(y_app), "| validation :", len(y_val), "| test :", len(y_test), "dont", int(y_test.sum()), "fraudes | budget :", budget)
```
<!--sortie-->
```text
apprentissage : 42000 | validation : 32000 | test : 18000 dont 146 fraudes | budget : 180
```

## Applications

### Application 6.1 — Mesurer un détecteur sous déséquilibre extrême (section 6.1)

**Contexte.** La gérante dispose d'un modèle supervisé et veut savoir ce qu'il vaut réellement, et combien d'alertes il est raisonnable de traiter chaque jour. **Objectif.** Calculer à la main la matrice de confusion, la précision, le rappel et l'AP, puis chercher le nombre d'alertes qui minimise le coût selon le prix d'une vérification.

**Étape 1 : un modèle supervisé de référence.** Un gradient boosting avec pondération des classes (chapitre 2, section 2.4 ; chapitre 4, section 4.3), entraîné sur le jeu d'apprentissage :

```python
from sklearn.ensemble import HistGradientBoostingClassifier

modele = HistGradientBoostingClassifier(class_weight="balanced", max_iter=150, random_state=0).fit(X_app, y_app)
score_gbm = modele.predict_proba(X_test)[:, 1]
print(evaluer("Gradient boosting (supervisé)", score_gbm))
```
<!--sortie-->
```text
{'AUC': 0.971, 'AP': 0.646, 'precision': 0.55, 'rappel1': 0.716, 'rappel2': 0.631}
```

**Étape 2 : la matrice de confusion à plusieurs budgets.** Pour un nombre $n$ d'alertes (les $n$ commandes les plus suspectes), on compte les vraies alertes ($VP$), les fausses ($FP$), les fraudes manquées ($FN$) et les commandes normales laissées passer ($VN$).

```python
def mesures(score, n_alertes):
    alertes = np.argsort(-score)[:n_alertes]
    vp = int(y_test[alertes].sum()); fp = n_alertes - vp; fn = int(y_test.sum()) - vp; vn = len(y_test) - n_alertes - fn
    return dict(alertes=n_alertes, VP=vp, FP=fp, FN=fn, VN=vn, exactitude=(vp + vn) / len(y_test), precision=vp / n_alertes, rappel=vp / y_test.sum())

print(pd.DataFrame([mesures(score_gbm, n) for n in (50, 100, 180, 300, 500)]).round(3).to_string(index=False))
```
<!--sortie-->
```text
 alertes  VP  FP  FN    VN  exactitude  precision  rappel
      50  47   3  99 17851       0.994       0.94   0.322
     100  71  29  75 17825       0.994       0.71   0.486
     180  99  81  47 17773       0.993       0.55   0.678
     300 108 192  38 17662       0.987       0.36   0.740
     500 120 380  26 17474       0.977       0.24   0.822
```

**Lecture.** Quand le budget passe de 50 à 500 alertes, la précision s'effondre (de 94 % à 24 %) et le rappel progresse (de 32 % à 82 %), tandis que l'exactitude ne bouge presque pas (de 99,4 % à 97,7 %) : elle ne distingue rien d'utile. Aucune mesure de la table ne dit à elle seule combien d'alertes traiter : il faut les coûts (étape 4).

**Étape 3 : la précision moyenne, recalculée à la main.** Si l'on parcourt les commandes de la plus suspecte à la moins suspecte, la précision moyenne est la moyenne des précisions mesurées aux rangs où l'on trouve une fraude :

```python
ordre = np.argsort(-score_gbm)
est_fraude = y_test[ordre] == 1
precision_rang = np.cumsum(y_test[ordre]) / np.arange(1, len(ordre) + 1)       # précision après n alertes
ap_main = precision_rang[est_fraude].mean()                                    # moyenne aux rangs des fraudes
print("AP à la main :", round(float(ap_main), 4), "| scikit-learn :", round(float(average_precision_score(y_test, score_gbm)), 4))
```
<!--sortie-->
```text
AP à la main : 0.6463 | scikit-learn : 0.6463
```

**Étape 4 : le nombre d'alertes optimal dépend du coût de vérification.** On suppose qu'une fraude manquée coûte le montant de la commande et qu'une vérification coûte `revue` euros.

```python
def courbe_cout(score, revue):
    ordre = np.argsort(-score)
    manque = (y_test * montant_test).sum() - np.cumsum(y_test[ordre] * montant_test[ordre])
    return manque + revue * np.arange(1, len(ordre) + 1)

cout_sans = (y_test * montant_test).sum()
print("coût sans aucune alerte :", round(float(cout_sans)), "€")
for revue in (1, 4, 10, 25):
    c = courbe_cout(score_gbm, revue); n_opt = int(c.argmin() + 1)
    print(f"vérification à {revue:2d} € : optimum à {n_opt:4d} alertes, coût {c[n_opt - 1]:7.0f} €, gain {100 * (1 - c[n_opt - 1] / cout_sans):.0f} %")
```
<!--sortie-->
```text
coût sans aucune alerte : 14404 €
vérification à  1 € : optimum à 1569 alertes, coût    2853 €, gain 80 %
vérification à  4 € : optimum à  461 alertes, coût    4453 €, gain 69 %
vérification à 10 € : optimum à  175 alertes, coût    6260 €, gain 57 %
vérification à 25 € : optimum à  175 alertes, coût    8885 €, gain 38 %
```

**Lecture.** Plus la vérification est chère, moins il faut d'alertes et plus le gain par rapport à l'absence de détecteur diminue : l'optimum passe de 1 569 alertes (vérification à 1 €) à 461 (à 4 €), puis à 175 alertes pour une vérification à 10 € **et** à 25 € (le même nombre : au-delà de la 175e alerte, les fraudes deviennent trop rares dans la liste pour que la décision dépende de la valeur exacte du coût dans cette fourchette). La règle sous-jacente est simple : **une alerte supplémentaire vaut la peine tant que (probabilité de fraude de la commande) × (montant moyen d'une fraude) est supérieur au coût de vérification** (exercice 6.4).

### Application 6.2 — z-score, Mahalanobis et masquage (section 6.2.1 et 6.2.2)

**Objectif.** Refaire les calculs du livre sur les montants d'un compte, comparer trois façons de combiner les z-scores, vérifier la distance de Mahalanobis, et mesurer l'effet du **masquage** quand la contamination augmente.

**Étape 1 : un z-score masqué par son propre outlier.**

```python
x = np.array([12, 15, 14, 13, 16, 15, 480.])
mad = np.median(np.abs(x - np.median(x)))
print("z classique de 480 :", round(float((480 - x.mean()) / x.std(ddof=1)), 2), "| z robuste :", round(float((480 - np.median(x)) / (1.4826 * mad)), 1))
print("constante 1,4826 : MAD d'une loi normale réduite (simulation) =", round(float(np.median(np.abs(np.random.default_rng(0).normal(size=1_000_000)))), 4), "; 1/1,4826 =", round(1 / 1.4826, 4))
```
<!--sortie-->
```text
z classique de 480 : 2.27 | z robuste : 313.6
constante 1,4826 : MAD d'une loi normale réduite (simulation) = 0.6757 ; 1/1,4826 = 0.6745
```

**Étape 2 : trois variantes de z-score sur les six variables continues.** Sommer les valeurs absolues des z-scores ; pour la version robuste, deux traitements du MAD nul (variable ignorée, ou repli sur l'écart absolu moyen multiplié par 1,2533).

```python
cont = ["log_montant", "log_distance", "nb_cmd_24h", "log_age_compte", "log_delai", "nb_articles"]
mu, sd = X_app[cont].mean(), X_app[cont].std()
med = X_app[cont].median(); ecarts = (X_app[cont] - med).abs(); mad = ecarts.median()
repli = pd.Series(np.where(mad > 0, 1.4826 * mad, 1.2533 * ecarts.mean()), index=cont)
print("variables à MAD nul :", [c for c in cont if mad[c] == 0])
print("classique       ", evaluer("z classique", ((X_test[cont] - mu) / sd).abs().sum(axis=1).values))
print("robuste (MAD)   ", evaluer("z robuste (MAD seul)", ((X_test[cont] - med) / (1.4826 * mad).replace(0, np.nan)).abs().fillna(0).sum(axis=1).values))
print("robuste (repli) ", evaluer("z robuste (repli)", ((X_test[cont] - med) / repli).abs().sum(axis=1).values))
```
<!--sortie-->
```text
variables à MAD nul : ['nb_cmd_24h']
classique        {'AUC': 0.939, 'AP': 0.433, 'precision': 0.378, 'rappel1': 0.457, 'rappel2': 0.477}
robuste (MAD)    {'AUC': 0.89, 'AP': 0.296, 'precision': 0.317, 'rappel1': 0.568, 'rappel2': 0.169}
robuste (repli)  {'AUC': 0.93, 'AP': 0.331, 'precision': 0.317, 'rappel1': 0.222, 'rappel2': 0.6}
```

**Lecture.** Les trois variantes ne trouvent pas les mêmes fraudes : regardez les deux colonnes `rappel1` et `rappel2`. La variante qui ignore la variable à MAD nul (le nombre de commandes des dernières 24 heures) manque presque toutes les prises de contrôle (type 2), signées justement par des rafales de commandes.

**Étape 3 : la distance de Mahalanobis, calculée deux fois.** À la main avec l'inverse de la matrice de covariance, puis avec `scikit-learn`. Les deux calculs ne diffèrent que par la convention de la covariance (`np.cov` divise par $n-1$, `EmpiricalCovariance` par $n$), c'est-à-dire d'un facteur $n/(n-1)$ très proche de 1 :

```python
from sklearn.covariance import EmpiricalCovariance

precision_app = np.linalg.inv(np.cov(Z_app.T))
d2_main = np.einsum("ij,jk,ik->i", Z_test, precision_app, Z_test)
d2_sk = EmpiricalCovariance().fit(Z_app).mahalanobis(Z_test)
print("écart maximal entre les deux calculs :", float(np.abs(d2_main - d2_sk).max()))
print(evaluer("Mahalanobis", d2_main))
```
<!--sortie-->
```text
écart maximal entre les deux calculs : 0.0038964685454629944
{'AUC': 0.946, 'AP': 0.382, 'precision': 0.311, 'rappel1': 0.198, 'rappel2': 0.615}
```

**Étape 4 : le masquage en fonction de la contamination.** On simule un groupe normal de 1 000 points corrélés ($\rho=0{,}8$) auquel on ajoute des points contaminants regroupés loin du centre, dans une proportion croissante. On compte la part des contaminants détectés (au-dessus du quantile 97,5 % du $\chi^2$ à 2 degrés de liberté) par la distance classique et par la distance robuste (MCD).

```python
from scipy.stats import chi2
from sklearn.covariance import MinCovDet

rng = np.random.default_rng(5); lignes = []
normaux = rng.multivariate_normal([0, 0], [[1, 0.8], [0.8, 1]], 1000)
for taux in (0.02, 0.05, 0.10, 0.20, 0.30):
    n_c = int(1000 * taux / (1 - taux))
    contam = rng.multivariate_normal([4.5, -2.5], 0.25 * np.eye(2), n_c)
    donnees = np.vstack([normaux, contam]); seuil = chi2.ppf(0.975, 2)
    d_c = np.einsum("ij,jk,ik->i", donnees - donnees.mean(0), np.linalg.inv(np.cov(donnees.T)), donnees - donnees.mean(0))
    d_r = MinCovDet(random_state=0, support_fraction=0.7).fit(donnees).mahalanobis(donnees)
    lignes.append(dict(contamination=taux, contaminants=n_c, detectes_classique=round(float((d_c[1000:] > seuil).mean()), 2), detectes_robuste=round(float((d_r[1000:] > seuil).mean()), 2)))
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 contamination  contaminants  detectes_classique  detectes_robuste
          0.02            20                1.00               1.0
          0.05            52                1.00               1.0
          0.10           111                0.75               1.0
          0.20           250                0.00               1.0
          0.30           428                0.00               1.0
```

**Lecture.** Jusqu'à 5 % de contamination, la distance classique détecte tous les contaminants ; à 10 %, elle n'en détecte plus que 75 % ; à 20 % et 30 %, **aucun** : le groupe contaminant étire tellement la covariance estimée qu'il se masque lui-même. L'estimateur robuste (MCD, qui travaille sur 70 % des points) les détecte tous, même à 30 %. En théorie, il ne peut pas tolérer plus de contamination que la part de points qu'il exclut (ici 30 %) : au-delà, son sous-ensemble « sain » contiendrait lui-même des contaminants.

### Application 6.3 — Plus proches voisins et LOF (section 6.2.3 et 6.2.4)

**Objectif.** Choisir le nombre de voisins sur le jeu de validation, mesurer l'effet de la standardisation et de la taille de l'échantillon de référence, écrire le LOF « à la main » et le vérifier, puis régler le LOF.

**Étape 1 : choisir $k$ sur la validation, avec et sans standardisation.** Pour chaque $k$, la précision moyenne sur le jeu de validation (qui sert à choisir) et sur le jeu de test (qui sert à juger) :

```python
from sklearn.neighbors import NearestNeighbors

def grille_knn(Z_ref, Z_v, Z_t, ks=(1, 5, 10, 30, 100)):
    nn = NearestNeighbors(n_neighbors=max(ks)).fit(Z_ref)
    dv, dt = nn.kneighbors(Z_v)[0], nn.kneighbors(Z_t)[0]
    return pd.DataFrame({"k": ks, "AP validation": [average_precision_score(y_val, dv[:, :k].mean(axis=1)) for k in ks],
                         "AP test": [average_precision_score(y_test, dt[:, :k].mean(axis=1)) for k in ks]}).round(3)

standard = grille_knn(Z_app[reference], Z_val, Z_test)
brut = grille_knn(X_app.values[reference], X_app.values[valid], X_test.values)
k_knn = int(standard.loc[standard["AP validation"].idxmax(), "k"])
print("variables standardisées\n", standard.to_string(index=False), "\nvariables brutes\n", brut.to_string(index=False), "\nk choisi :", k_knn)
```
<!--sortie-->
```text
variables standardisées
   k  AP validation  AP test
  1          0.261    0.303
  5          0.350    0.411
 10          0.382    0.444
 30          0.400    0.460
100          0.399    0.448 
variables brutes
   k  AP validation  AP test
  1          0.279    0.402
  5          0.355    0.486
 10          0.386    0.503
 30          0.426    0.511
100          0.446    0.508 
k choisi : 30
```

**Lecture.** La validation retient $k=30$ (AP de 0,400 ; $k=100$ donne 0,399) et le jeu de test classe les réglages dans le même ordre. Autre résultat : sur les **variables brutes**, les voisins font mieux pour tous les $k$ (0,511 pour $k=30$ contre 0,460 avec la standardisation). Une hypothèse explique cet écart : la standardisation multiplie les deux variables binaires (IP étrangère, appareil inconnu), d'écart-type 0,20 et 0,30, par 5 et 3,3, alors que les variables continues, d'écart-type voisin de 1, ne bougent presque pas. Vérifions-la en ne standardisant **que** les variables continues :

```python
binaires = [list(X.columns).index(c) for c in ("ip_different", "appareil_inconnu")]
Z_mixte_app, Z_mixte_test = Z_app.copy(), Z_test.copy()
Z_mixte_app[:, binaires] = X_app.values[:, binaires]; Z_mixte_test[:, binaires] = X_test.values[:, binaires]    # binaires laissées en 0/1
d = NearestNeighbors(n_neighbors=k_knn).fit(Z_mixte_app[reference]).kneighbors(Z_mixte_test)[0].mean(axis=1)
print("AP test, continues standardisées et binaires en 0/1 :", round(float(average_precision_score(y_test, d)), 3))
```
<!--sortie-->
```text
AP test, continues standardisées et binaires en 0/1 : 0.513
```

Le résultat (voir la sortie) est du même ordre que celui des variables brutes : l'hypothèse est confirmée. Moralité : **standardiser mécaniquement toutes les colonnes n'est pas toujours neutre**, surtout avec des variables binaires rares.

**Étape 2 : la taille de l'échantillon de référence.** Comparer chaque commande à un échantillon plus grand coûte plus de temps ; qu'y gagne-t-on ?

```python
rng_r = np.random.default_rng(1)
for taille in (500, 2000, 5000, 10000, 20000):
    idx = rng_r.choice(len(Z_app), taille, replace=False)
    d = NearestNeighbors(n_neighbors=k_knn).fit(Z_app[idx]).kneighbors(Z_test)[0].mean(axis=1)
    print(f"référence de {taille:6d} commandes : AP test = {average_precision_score(y_test, d):.3f}")
```
<!--sortie-->
```text
référence de    500 commandes : AP test = 0.370
référence de   2000 commandes : AP test = 0.458
référence de   5000 commandes : AP test = 0.465
référence de  10000 commandes : AP test = 0.468
référence de  20000 commandes : AP test = 0.476
```

**Étape 3 : le LOF écrit à la main.** Une fonction qui calcule le LOF pour des points de dimension quelconque, avec les définitions de la section 6.2.4 ($k$-distance, distance d'atteignabilité, densité locale), vérifiée contre `scikit-learn` sur 60 points aléatoires.

```python
from sklearn.neighbors import LocalOutlierFactor

def lof_main(P, k):
    D = np.sqrt(((P[:, None, :] - P[None, :, :]) ** 2).sum(axis=2))
    ordre = np.argsort(D, axis=1)
    voisins = ordre[:, 1:k + 1]                                  # les k plus proches voisins (sans le point lui-même)
    kdist = D[np.arange(len(P)), ordre[:, k]]                     # k-distance de chaque point
    atteint = np.maximum(kdist[voisins], np.take_along_axis(D, voisins, axis=1))   # distance d'atteignabilité à chaque voisin
    lrd = 1 / atteint.mean(axis=1)                                # densité d'atteignabilité locale
    return lrd[voisins].mean(axis=1) / lrd

P = np.random.default_rng(2).normal(size=(60, 2))
ecart = np.abs(lof_main(P, 5) + LocalOutlierFactor(n_neighbors=5).fit(P).negative_outlier_factor_).max()
print("écart maximal avec scikit-learn :", float(ecart))
```
<!--sortie-->
```text
écart maximal avec scikit-learn : 3.012434746096915e-10
```

**Étape 4 : le LOF sur les transactions, réglé sur la validation.**

```python
lignes = []
for k in (10, 30, 100, 300):
    lof = LocalOutlierFactor(n_neighbors=k, novelty=True).fit(Z_app[reference])
    lignes.append(dict(k=k, AP_validation=average_precision_score(y_val, -lof.score_samples(Z_val)), score_test=-lof.score_samples(Z_test)))
k_lof = max(lignes, key=lambda r: r["AP_validation"])["k"]
for r in lignes:
    print(f"k = {r['k']:3d} : AP validation {r['AP_validation']:.3f} |", evaluer(f"LOF k={r['k']}", r["score_test"]))
print("k choisi sur la validation :", k_lof)
```
<!--sortie-->
```text
k =  10 : AP validation 0.114 | {'AUC': 0.886, 'AP': 0.113, 'precision': 0.183, 'rappel1': 0.309, 'rappel2': 0.123}
k =  30 : AP validation 0.243 | {'AUC': 0.945, 'AP': 0.306, 'precision': 0.322, 'rappel1': 0.432, 'rappel2': 0.354}
k = 100 : AP validation 0.408 | {'AUC': 0.956, 'AP': 0.471, 'precision': 0.444, 'rappel1': 0.58, 'rappel2': 0.508}
k = 300 : AP validation 0.433 | {'AUC': 0.944, 'AP': 0.492, 'precision': 0.411, 'rappel1': 0.519, 'rappel2': 0.492}
k choisi sur la validation : 300
```

**Lecture.** Le LOF est **extrêmement sensible** à $k$ : sur la validation, la précision moyenne passe de 0,114 ($k=10$) à 0,243 ($k=30$), 0,408 ($k=100$) puis 0,433 ($k=300$) ; le jeu de test classe les réglages dans le même ordre (0,113 ; 0,306 ; 0,471 ; 0,492). À $k=300$, le LOF retrouve 52 % des fraudes de type 1 et 49 % de celles de type 2, mieux que les voisins simples (AP de 0,460). Le meilleur $k$ est en bout de grille : essayez $k=500$ ou $1\,000$ (exercice laissé au lecteur) et observez si la courbe plafonne.

### Application 6.4 — Une forêt d'isolement écrite à la main (section 6.3)

**Objectif.** Construire des arbres d'isolement avec quelques lignes de `numpy`, les assembler en forêt, calculer le score $s=2^{-E[h]/c(n)}$, et comparer avec `scikit-learn`.

**Étape 1 : un arbre d'isolement.** À chaque nœud, on tire une variable au hasard, puis une coupure uniforme entre son minimum et son maximum, jusqu'à isoler les points ou atteindre la hauteur maximale. Un nœud est un quadruplet (variable, coupure, enfant gauche, enfant droit) ; une feuille est le nombre de points qu'elle contient.

```python
def c_de_n(n):
    return 0.0 if n <= 1 else (1.0 if n == 2 else 2 * (np.log(n - 1) + 0.5772156649) - 2 * (n - 1) / n)

def arbre(P, hauteur_max, rng, h=0):
    if h >= hauteur_max or len(P) <= 1:
        return len(P)                                             # feuille : nombre de points restants
    j = rng.integers(P.shape[1]); bas, haut = P[:, j].min(), P[:, j].max()
    if bas == haut:
        return len(P)
    coupure = rng.uniform(bas, haut); gauche = P[:, j] < coupure
    return (j, coupure, arbre(P[gauche], hauteur_max, rng, h + 1), arbre(P[~gauche], hauteur_max, rng, h + 1))
```

**Étape 2 : la profondeur d'isolement de chaque point.** Pour une feuille qui contient encore $m>1$ points (hauteur maximale atteinte), on ajoute $c(m)$, la longueur moyenne attendue pour finir de les isoler.

```python
def profondeurs(noeud, P, h=0):
    if not isinstance(noeud, tuple):
        return np.full(len(P), h + c_de_n(noeud))
    j, coupure, g, d = noeud
    masque = P[:, j] < coupure; sortie = np.empty(len(P))
    sortie[masque] = profondeurs(g, P[masque], h + 1); sortie[~masque] = profondeurs(d, P[~masque], h + 1)
    return sortie

# petit test : les 8 valeurs du livre (section 6.3.1)
v = np.array([[2], [3], [3.5], [4], [4.5], [5], [5.5], [30.]]); rng = np.random.default_rng(0)
moy = np.mean([profondeurs(arbre(v, 8, rng), v) for _ in range(3000)], axis=0)
print("coupures moyennes :", dict(zip([2, 3, 3.5, 4, 4.5, 5, 5.5, 30], moy.round(2))))
```
<!--sortie-->
```text
coupures moyennes : {2: np.float64(3.0), 3: np.float64(4.21), 3.5: np.float64(4.68), 4: np.float64(4.77), 4.5: np.float64(4.66), 5: np.float64(4.35), 5.5: np.float64(3.54), 30: np.float64(1.13)}
```

**Étape 3 : la forêt, le score et la comparaison avec `scikit-learn`.** 100 arbres de 256 points, hauteur maximale $\lceil\log_2 256\rceil=8$.

```python
from scipy.stats import spearmanr
from sklearn.ensemble import IsolationForest

rng = np.random.default_rng(0); psi = 256
foret = [arbre(Z_app[rng.choice(len(Z_app), psi, replace=False)], 8, rng) for _ in range(100)]
esperance_h = np.mean([profondeurs(a, Z_test) for a in foret], axis=0)
score_main = 2 ** (-esperance_h / c_de_n(psi))
score_sk = -IsolationForest(n_estimators=100, max_samples=psi, random_state=0).fit(Z_app).score_samples(Z_test)
print("ma forêt     :", evaluer("Forêt d'isolement (à la main)", score_main))
print("scikit-learn :", evaluer("Forêt d'isolement (sklearn)", score_sk))
print("corrélation de rang entre les deux scores :", round(float(spearmanr(score_main, score_sk)[0]), 3), "| score moyen d'une commande normale :", round(float(score_main[y_test == 0].mean()), 3))
```
<!--sortie-->
```text
ma forêt     : {'AUC': 0.935, 'AP': 0.325, 'precision': 0.306, 'rappel1': 0.111, 'rappel2': 0.708}
scikit-learn : {'AUC': 0.924, 'AP': 0.293, 'precision': 0.278, 'rappel1': 0.099, 'rappel2': 0.646}
corrélation de rang entre les deux scores : 0.968 | score moyen d'une commande normale : 0.462
```

**Lecture.** Notre forêt de 100 arbres obtient une précision moyenne de 0,325 et celle de `scikit-learn`, avec 100 arbres aussi, de 0,293 : les rangs des scores sont très corrélés (0,968) mais pas identiques, car les deux forêts tirent des variables et des coupures différentes. L'écart de 0,03 est de l'ordre du **bruit dû à l'aléa** d'une forêt de 100 arbres : deux forêts construites de la même façon avec des graines différentes ne donnent pas exactement le même détecteur. Les deux retrouvent surtout le type 2 (71 % et 65 %) et peu le type 1 (11 % et 10 %). Le score moyen d'une commande normale est de 0,462, proche des 0,5 que prévoit la théorie pour un point moyen.

**Étape 4 : de quel seuil parle-t-on ?** En calculant le score sur le jeu d'apprentissage (sans étiquette), on obtient la distribution des scores « normaux » ; fixer une contamination $c$, c'est retenir le quantile $1-c$ de cette distribution comme seuil.

```python
esperance_app = np.mean([profondeurs(a, Z_app[:10000]) for a in foret], axis=0)
score_app = 2 ** (-esperance_app / c_de_n(psi))
for c in (0.005, 0.0081, 0.02, 0.05):
    seuil = np.quantile(score_app, 1 - c); drapeau = score_main >= seuil
    print(f"contamination {c:6.4f} : seuil {seuil:.3f}, {drapeau.sum():5d} alertes, précision {y_test[drapeau].mean():.3f}, rappel {y_test[drapeau].sum() / y_test.sum():.3f}")
```
<!--sortie-->
```text
contamination 0.0050 : seuil 0.609,   109 alertes, précision 0.413, rappel 0.308
contamination 0.0081 : seuil 0.598,   158 alertes, précision 0.335, rappel 0.363
contamination 0.0200 : seuil 0.572,   367 alertes, précision 0.188, rappel 0.473
contamination 0.0500 : seuil 0.546,   910 alertes, précision 0.103, rappel 0.644
```

**Lecture.** Le nombre d'alertes suit la contamination choisie (158 alertes pour 0,0081, 367 pour 0,02 et 910 pour 0,05, sur 18 000 commandes). Plus on alerte, plus le rappel augmente (de 31 % à 64 %) et plus la précision s'effondre (de 41 % à 10 %) : fixer la contamination, c'est choisir un point de cette courbe, donc un budget d'alertes.

### Application 6.5 — Autoencodeur et ACP (section 6.4)

**Objectif.** Vérifier numériquement qu'un autoencodeur linéaire se comporte comme une ACP, examiner la convergence d'un réseau, tester l'hypothèse que l'instabilité vient d'un entraînement trop court, et reproduire la **procédure de sélection sur un jeu de validation** du livre.

**Étape 1 : un autoencodeur linéaire est une ACP à une composante.** Un `MLPRegressor` avec une couche cachée d'un seul neurone et une activation identité, entraîné à reconstruire ses entrées, calcule une projection linéaire sur une droite. L'erreur de reconstruction doit donc ressembler à celle de l'ACP à une composante :

```python
from sklearn.decomposition import PCA
from sklearn.neural_network import MLPRegressor

pca1 = PCA(n_components=1).fit(Z_app)
err_pca = ((Z_test - pca1.inverse_transform(pca1.transform(Z_test))) ** 2).sum(axis=1)
ae_lin = MLPRegressor(hidden_layer_sizes=(1,), activation="identity", max_iter=500, random_state=0).fit(Z_app[reference], Z_app[reference])
err_ae = ((ae_lin.predict(Z_test) - Z_test) ** 2).sum(axis=1)
print("corrélation entre les deux erreurs de reconstruction :", round(float(np.corrcoef(err_pca, err_ae)[0, 1]), 3))
print("ACP (1 composante)      :", evaluer("ACP 1 composante", err_pca))
print("autoencodeur linéaire   :", evaluer("AE linéaire (1 neurone)", err_ae))
```
<!--sortie-->
```text
corrélation entre les deux erreurs de reconstruction : 1.0
ACP (1 composante)      : {'AUC': 0.946, 'AP': 0.391, 'precision': 0.311, 'rappel1': 0.198, 'rappel2': 0.615}
autoencodeur linéaire   : {'AUC': 0.945, 'AP': 0.386, 'precision': 0.322, 'rappel1': 0.198, 'rappel2': 0.646}
```

**Lecture.** Les deux erreurs de reconstruction sont corrélées à plus de 0,999 et donnent la même précision moyenne (0,39) : l'autoencodeur linéaire entraîné par descente de gradient retrouve l'ACP, comme le prévoit le théorème d'Eckart-Young (exercice 6.10).

**Étape 2 : la convergence.** Le livre entraîne les réseaux sur 100 itérations seulement ; a-t-on convergé ? La courbe de perte et le nombre d'itérations effectuées répondent :

```python
ae = MLPRegressor(hidden_layer_sizes=(6, 3, 6), activation="tanh", max_iter=100, random_state=0).fit(Z_app[reference], Z_app[reference])
fig, ax = plt.subplots(figsize=(6.5, 3.4))
ax.plot(ae.loss_curve_, color=style.BLEU); ax.set_yscale("log")
ax.set_xlabel("itération (époque)"); ax.set_ylabel("perte d'entraînement (échelle log)")
plt.tight_layout(); plt.savefig("figures/ch06-cahier-perte.png", dpi=200, bbox_inches="tight"); plt.close()
print("itérations effectuées :", ae.n_iter_, "sur 100 permises | perte finale :", round(float(ae.loss_curve_[-1]), 4), "| 10 itérations avant :", round(float(ae.loss_curve_[-11]), 4))
```
<!--sortie-->
```text
itérations effectuées : 100 sur 100 permises | perte finale : 0.2699 | 10 itérations avant : 0.271
```

![Perte d'entraînement de l'autoencodeur (6, 3, 6) au fil des itérations, en échelle logarithmique.](figures/ch06-cahier-perte.png)

**Étape 3 : l'instabilité vient-elle d'un entraînement trop court ?** Pour deux architectures instables dans le livre, on compare 100 et 400 itérations, sur trois graines. *Attention : cet examen utilise le jeu de test pour étudier un phénomène, pas pour choisir un réglage.*

```python
def ap_ae(h, iters, graine):
    r = MLPRegressor(hidden_layer_sizes=h, activation="tanh", max_iter=iters, random_state=graine).fit(Z_app[reference], Z_app[reference])
    return average_precision_score(y_test, ((r.predict(Z_test) - Z_test) ** 2).sum(axis=1))

for h in ((5,), (16, 8, 16)):
    for iters in (100, 400):
        aps = [ap_ae(h, iters, g) for g in range(3)]
        print(f"{str(h):12s} {iters:3d} itérations : AP par graine {np.round(aps, 3)}, moyenne {np.mean(aps):.3f}")
```
<!--sortie-->
```text
(5,)         100 itérations : AP par graine [0.068 0.176 0.109], moyenne 0.117
(5,)         400 itérations : AP par graine [0.067 0.176 0.109], moyenne 0.117
(16, 8, 16)  100 itérations : AP par graine [0.135 0.127 0.087], moyenne 0.116
(16, 8, 16)  400 itérations : AP par graine [0.135 0.127 0.091], moyenne 0.118
```

**Lecture.** Au bout des 100 itérations permises, la perte de l'autoencodeur (6, 3, 6) ne diminue presque plus (0,2699 contre 0,2710 dix itérations plus tôt). Et laisser 400 itérations aux deux architectures les moins bonnes ne change **pas** leur précision moyenne (0,117 dans les deux cas pour (5,) ; 0,116 puis 0,118 pour (16, 8, 16)) : l'instabilité observée dans le livre ne vient donc pas d'un entraînement trop court. Chaque réseau converge vers une solution qui dépend de son initialisation.

**Choix sur la validation (étape 4).** Le comité de trois réseaux (6, 3, 6) l'emporte nettement sur les deux autres architectures, à la fois sur la validation (0,452 contre 0,241 et 0,183) et sur le test (0,484 contre 0,256 et 0,201) : la validation désigne la bonne architecture.

**Étape 4 : choisir l'architecture sur le jeu de validation.** La procédure du livre en miniature : trois architectures, trois graines, comité de trois réseaux ; on choisit sur la validation, on juge sur le test.

```python
def comite(h, graines=(0, 1, 2)):
    sv, st = [], []
    for g in graines:
        r = MLPRegressor(hidden_layer_sizes=h, activation="tanh", max_iter=100, random_state=g).fit(Z_app[reference], Z_app[reference])
        ev = ((r.predict(Z_val) - Z_val) ** 2).sum(axis=1); et = ((r.predict(Z_test) - Z_test) ** 2).sum(axis=1)
        sv.append((ev - ev.mean()) / ev.std()); st.append((et - ev.mean()) / ev.std())          # échelle fixée sur la validation
    return np.mean(sv, axis=0), np.mean(st, axis=0)

resultat = {h: comite(h) for h in ((3,), (6, 3, 6), (10, 5, 10))}
for h, (sv, st) in resultat.items():
    print(f"{str(h):10s} AP validation {average_precision_score(y_val, sv):.3f} | AP test {average_precision_score(y_test, st):.3f}")
choix = max(resultat, key=lambda h: average_precision_score(y_val, resultat[h][0]))
print("architecture choisie sur la validation :", choix)
```
<!--sortie-->
```text
(3,)       AP validation 0.241 | AP test 0.256
(6, 3, 6)  AP validation 0.452 | AP test 0.484
(10, 5, 10) AP validation 0.183 | AP test 0.201
architecture choisie sur la validation : (6, 3, 6)
```

### Application 6.6 — Trier les alertes : combiner les détecteurs (section 6.4.5)

**Objectif.** Comparer ce que trouvent trois détecteurs de familles différentes, tester des combinaisons, utiliser les scores non supervisés comme **variables d'un modèle supervisé**, et traduire le tout en euros.

**Étape 1 : trois détecteurs, ajustés sans étiquette sur l'échantillon de référence.** Les distances aux voisins, la forêt d'isolement et un comité de trois autoencodeurs (6, 3, 6). Comme aucun n'a vu les commandes du jeu de validation, on peut y calculer leurs scores sans biais.

```python
from sklearn.ensemble import IsolationForest

voisins = NearestNeighbors(n_neighbors=k_knn).fit(Z_app[reference])        # k_knn : choisi à l'application 6.3
iso = IsolationForest(n_estimators=200, random_state=0).fit(Z_app[reference])
s_val, s_test = {}, {}
for nom, Z, sortie in (("validation", Z_val, s_val), ("test", Z_test, s_test)):
    sortie["voisins"] = voisins.kneighbors(Z)[0].mean(axis=1)
    sortie["isolement"] = -iso.score_samples(Z)
sv, st = comite((6, 3, 6), graines=(0, 1, 2, 3))
s_val["autoencodeur"], s_test["autoencodeur"] = sv, st
for nom in s_test:
    print(f"{nom:13s}", evaluer(nom, s_test[nom]))
```
<!--sortie-->
```text
voisins       {'AUC': 0.959, 'AP': 0.46, 'precision': 0.367, 'rappel1': 0.259, 'rappel2': 0.692}
isolement     {'AUC': 0.935, 'AP': 0.332, 'precision': 0.289, 'rappel1': 0.111, 'rappel2': 0.662}
autoencodeur  {'AUC': 0.962, 'AP': 0.526, 'precision': 0.478, 'rappel1': 0.519, 'rappel2': 0.677}
```

**Étape 2 : se recouvrent-ils ?** Si deux détecteurs retrouvent les mêmes commandes, les combiner n'apporte rien. On mesure le recouvrement de leurs 180 alertes (indice de Jaccard : taille de l'intersection divisée par la taille de l'union) :

```python
alertes = {nom: set(np.argsort(-s)[:budget]) for nom, s in s_test.items()}
for a, b in (("voisins", "isolement"), ("voisins", "autoencodeur"), ("isolement", "autoencodeur")):
    inter = len(alertes[a] & alertes[b])
    print(f"{a:10s} et {b:13s} : {inter:3d} alertes communes, Jaccard = {inter / len(alertes[a] | alertes[b]):.2f}")
```
<!--sortie-->
```text
voisins    et isolement     : 133 alertes communes, Jaccard = 0.59
voisins    et autoencodeur  : 119 alertes communes, Jaccard = 0.49
isolement  et autoencodeur  :  85 alertes communes, Jaccard = 0.31
```

**Lecture.** Les voisins et la forêt d'isolement se recouvrent beaucoup (133 alertes communes sur 180, Jaccard de 0,59) : ils voient en grande partie les mêmes fraudes, les combiner n'ajoutera pas grand-chose. La forêt d'isolement et l'autoencodeur se recouvrent beaucoup moins (85 alertes communes, Jaccard de 0,31) : ils sont plus complémentaires.

**Étape 3 : des combinaisons.** Moyenne des rangs de deux ou trois détecteurs, ou maximum des rangs (une alerte dès qu'un détecteur la juge très suspecte).

```python
from scipy.stats import rankdata
rang = {nom: rankdata(s) / len(s) for nom, s in s_test.items()}
combos = {"rang moyen (3)": sum(rang.values()) / 3, "rang moyen (voisins + autoencodeur)": (rang["voisins"] + rang["autoencodeur"]) / 2,
          "rang maximal (3)": np.maximum.reduce(list(rang.values()))}
for nom, s in combos.items():
    print(f"{nom:38s}", evaluer(nom, s))
```
<!--sortie-->
```text
rang moyen (3)                         {'AUC': 0.957, 'AP': 0.435, 'precision': 0.356, 'rappel1': 0.259, 'rappel2': 0.662}
rang moyen (voisins + autoencodeur)    {'AUC': 0.962, 'AP': 0.507, 'precision': 0.439, 'rappel1': 0.444, 'rappel2': 0.662}
rang maximal (3)                       {'AUC': 0.96, 'AP': 0.497, 'precision': 0.439, 'rappel1': 0.407, 'rappel2': 0.708}
```

**Lecture.** Aucune combinaison ne dépasse l'autoencodeur seul (précision moyenne de 0,526). La meilleure, la moyenne des rangs des voisins et de l'autoencodeur (0,507), s'en rapproche ; la moyenne des trois (0,435) est tirée vers le bas par la forêt d'isolement, nettement moins bonne. Combiner n'aide que si les membres sont de qualité comparable.

**Étape 4 : les scores non supervisés comme variables d'un modèle supervisé.** On entraîne un gradient boosting **sur le jeu de validation** (32 000 commandes étiquetées, qui n'ont servi ni à ajuster les détecteurs ni à les juger), avec les dix variables seules, ou avec les dix variables plus les trois scores. Quelques centaines de fraudes seulement : le réglage du modèle compte, et nous le choisissons par **validation croisée à 5 plis sur le jeu de validation**, sans regarder le test.

```python
from sklearn.model_selection import StratifiedKFold, cross_val_predict

X_val_df, X_test_df = X_app.iloc[valid].reset_index(drop=True), X_test.reset_index(drop=True)
plus = lambda X_, s: X_.assign(**{f"score_{k}": v for k, v in s.items()})
jeux = {"variables seules": (X_val_df, X_test_df), "variables + 3 scores": (plus(X_val_df, s_val), plus(X_test_df, s_test))}
reglages = {"profondeur libre": {}, "profondeur 3": dict(max_depth=3, learning_rate=0.05)}
cv = StratifiedKFold(5, shuffle=True, random_state=0); lignes = []
for nj, (A, _) in jeux.items():
    for nr, kw in reglages.items():
        m = HistGradientBoostingClassifier(class_weight="balanced", max_iter=150, random_state=0, **kw)
        p_cv = cross_val_predict(m, A, y_val, cv=cv, method="predict_proba")[:, 1]
        lignes.append(dict(jeu=nj, reglage=nr, AP_validation_croisee=round(float(average_precision_score(y_val, p_cv)), 3)))
res_cv = pd.DataFrame(lignes); print(res_cv.to_string(index=False))
```
<!--sortie-->
```text
                 jeu          reglage  AP_validation_croisee
    variables seules profondeur libre                  0.537
    variables seules     profondeur 3                  0.595
variables + 3 scores profondeur libre                  0.426
variables + 3 scores     profondeur 3                  0.498
```

```python
meilleur = res_cv.loc[res_cv["AP_validation_croisee"].idxmax()]
A, B = jeux[meilleur["jeu"]]
sup_choisi = HistGradientBoostingClassifier(class_weight="balanced", max_iter=150, random_state=0, **reglages[meilleur["reglage"]]).fit(A, y_val)
score_sup = sup_choisi.predict_proba(B)[:, 1]
print("choisi par validation croisée :", dict(meilleur[["jeu", "reglage"]]))
print("sur le jeu de test :", evaluer("GBM choisi par validation croisée", score_sup))
```
<!--sortie-->
```text
choisi par validation croisée : {'jeu': 'variables seules', 'reglage': 'profondeur 3'}
sur le jeu de test : {'AUC': 0.957, 'AP': 0.655, 'precision': 0.511, 'rappel1': 0.654, 'rappel2': 0.6}
```

**Lecture.** La validation croisée est claire : **les trois scores n'aident pas** le modèle supervisé (précision moyenne de 0,426 avec les scores contre 0,537 sans, à profondeur libre ; 0,498 contre 0,595 avec des arbres de profondeur 3). On retient donc les variables seules avec des arbres de profondeur 3, qui obtiennent 0,655 sur le jeu de test, soit autant que le modèle du livre entraîné sur les 42 000 commandes (0,646) alors qu'ici il n'en a vu que 32 000. Pourquoi les scores n'apportent-ils rien ? Une explication plausible, que nous n'avons pas testée, est qu'ils sont des fonctions des mêmes dix variables, que le gradient boosting exploite déjà directement, et que trois variables de plus augmentent le risque de sur-ajustement avec seulement 246 fraudes pour apprendre. Retenez la **méthode** (régler par validation croisée avant de regarder le test) plus que le résultat.

**Étape 5 : en euros.** Pour chaque méthode, le coût total au budget de 180 alertes (fraudes manquées plus 4 € par vérification), en pourcentage du coût sans détecteur :

```python
sans = (y_test * montant_test).sum()
ligne = lambda nom, s: f"{nom:34s} {courbe_cout(s, 4.0)[budget - 1]:7.0f} €  ({100 * (1 - courbe_cout(s, 4.0)[budget - 1] / sans):3.0f} % d'économie)"
for nom, s_ in [("gradient boosting (apprentissage)", score_gbm), ("GBM choisi par validation croisée", score_sup),
                ("voisins", s_test["voisins"]), ("forêt d'isolement", s_test["isolement"]), ("autoencodeur (comité de 4)", s_test["autoencodeur"]),
                ("rang moyen (3)", combos["rang moyen (3)"])]:
    print(ligne(nom, s_))
```
<!--sortie-->
```text
gradient boosting (apprentissage)     5230 €  ( 64 % d'économie)
GBM choisi par validation croisée     6018 €  ( 58 % d'économie)
voisins                               8932 €  ( 38 % d'économie)
forêt d'isolement                    10205 €  ( 29 % d'économie)
autoencodeur (comité de 4)            6572 €  ( 54 % d'économie)
rang moyen (3)                        8697 €  ( 40 % d'économie)
```

## Exercices

### Exercice 6.1 ⭐ — Deux détecteurs, une même exactitude (section 6.1.3)

Sur 5 000 commandes, dont 40 frauduleuses, le détecteur A ne déclenche jamais d'alerte ; le détecteur B déclenche 60 alertes, dont 30 sont de vraies fraudes. Calculez l'exactitude, la précision, le rappel et la mesure F1 de chacun. Que remarque-t-on ?

### Exercice 6.2 ⭐ — Précision moyenne à la main (section 6.1.5)

Un détecteur classe huit commandes de la plus suspecte à la moins suspecte ; les étiquettes dans cet ordre sont : fraude, normale, fraude, normale, normale, fraude, normale, normale (soit 3 fraudes sur 8). (a) Donnez la précision et le rappel après 1, 3 et 6 alertes. (b) Calculez la précision moyenne (AP) comme la moyenne des précisions aux rangs des fraudes.

### Exercice 6.3 ⭐⭐ — Taux de base et formule de Bayes (section 6.1.3)

Une boutique reçoit 0,5 % de commandes frauduleuses. Un détecteur retrouve 90 % des fraudes et déclenche une fausse alerte sur 2 % des commandes normales. (a) Quelle est la probabilité qu'une alerte soit une vraie fraude ? (b) Quel taux de fausses alertes faudrait-il pour que la moitié des alertes soient justes (à rappel inchangé) ?

### Exercice 6.4 ⭐⭐ — Combien d'alertes traiter ? (section 6.1.6)

Une fraude manquée coûte en moyenne 70 € ; une vérification coûte 5 €. Sur un jeu de 100 fraudes, un détecteur en retrouve 40 dans ses 100 premières alertes, 60 dans les 200 premières, 70 dans les 300, 75 dans les 400 et 78 dans les 500. (a) Calculez le coût total pour chaque nombre d'alertes. (b) À partir de quelle précision marginale une alerte supplémentaire cesse-t-elle de valoir la peine ? Vérifiez-le sur les tranches de 100 alertes.

### Exercice 6.5 ⭐ — z-score classique contre z-score robuste (section 6.2.1)

Les montants (en €) d'un compte sont 20, 22, 21, 19, 23, 20, 21, 22 et 95. Calculez le z-score de 95 avec la moyenne et l'écart-type, puis avec la médiane et le MAD. Lequel signale la commande ?

### Exercice 6.6 ⭐⭐ — Mahalanobis à la main (section 6.2.2)

Deux variables standardisées ont pour corrélation $\rho=0{,}6$. Calculez la distance de Mahalanobis au carré des points $A=(1,1)$, $B=(1,-1)$ et $C=(2,0)$, et comparez avec leur distance euclidienne au carré. Lesquels dépassent le seuil du $\chi^2$ à 2 degrés de liberté au niveau 95 % (5,99) ?

### Exercice 6.7 ⭐⭐ — LOF sur cinq points (section 6.2.4)

Cinq points sur une droite sont aux abscisses $0 ;\ 1 ;\ 2{,}2 ;\ 3{,}5 ;\ 9$. Avec $k=2$, calculez pour chaque point sa $2$-distance, ses voisins, sa densité d'atteignabilité locale, puis son LOF. Quel point est le plus anormal ?

### Exercice 6.8 ⭐ — La constante $c(n)$ et le score d'isolement (section 6.3.2)

Pour $n=16$ points, calculez $c(16)$, puis le score d'anomalie d'un point isolé en moyenne en 3 coupures, d'un autre isolé en 6 coupures, et d'un point dont la longueur moyenne vaut $c(16)$. Lesquels sont jugés anormaux (score supérieur à 0,5) ?

### Exercice 6.9 ⭐⭐ — Contamination et seuil (section 6.3.4)

Sur 1 000 commandes, 8 sont frauduleuses. On fixe la contamination d'une forêt d'isolement à 2 %, ce qui déclenche 20 alertes ; parmi elles, 60 % des fraudes sont retrouvées. (a) Quelle est la précision ? (b) On fixe maintenant la contamination à 5 % : 50 alertes, 85 % des fraudes retrouvées. Calculez la précision. (c) Qu'est-ce qui, dans la vie réelle, devrait guider le choix de la contamination ?

### Exercice 6.10 ⭐⭐⭐ — Un autoencodeur linéaire est une ACP (section 6.4.2)

Soit $X$ un tableau centré de $n$ lignes et $p$ colonnes, de décomposition en valeurs singulières $X=U\Sigma V^\top$. (a) Montrez que l'approximation de rang $q$ de $X$ au sens des moindres carrés est $XV_qV_q^\top$, où $V_q$ contient les $q$ premières colonnes de $V$, et que l'erreur totale vaut $\sum_{j>q}\sigma_j^2$. (b) Montrez que l'erreur de reconstruction d'une ligne $x_i$ vaut $\lVert x_i\rVert^2-\lVert V_q^\top x_i\rVert^2$. (c) Vérifiez numériquement ces deux résultats sur un tableau simulé.

### Exercice 6.11 ⭐⭐ — Pourquoi limiter le goulot ? (section 6.4.3)

On dispose de 1 000 points normaux de deux variables corrélées ($\rho=0{,}9$) et de 10 anomalies placées à contre-courant de la corrélation. On entraîne deux autoencodeurs linéaires (activation identité) : un goulot d'un neurone, un goulot de deux neurones. (a) Que prévoyez-vous, **en théorie**, pour l'erreur de reconstruction moyenne des points normaux et des anomalies, dans chaque cas ? (b) Vérifiez par simulation, avec deux optimiseurs : le solveur par défaut (`adam`, par descente de gradient) et le solveur `lbfgs` (qui résout le problème à haute précision). Que constatez-vous ?

### Exercice 6.12 ⭐⭐⭐ — Un budget, deux détecteurs (section 6.4.5)

Avec les scores des voisins et de la forêt d'isolement de l'application 6.6, comparez trois façons d'utiliser les 180 alertes du budget : (a) les 180 premières du détecteur des voisins ; (b) les 90 premières de chaque détecteur (sans doublon, en complétant au besoin) ; (c) les 180 premières de la moyenne de leurs rangs. Laquelle retrouve le plus de fraudes ? Expliquez ce que cela montre sur la complémentarité.

## Corrigés

### Corrigé 6.1

Détecteur A : $VP=0$, $FP=0$, $FN=40$, $VN=4\,960$. Exactitude $4\,960/5\,000=99{,}2\ \%$ ; précision indéfinie (aucune alerte) ; rappel $0$.
Détecteur B : $VP=30$, $FP=30$, $FN=10$, $VN=4\,930$. Exactitude $(30+4\,930)/5\,000=\mathbf{99{,}2\ \%}$ ; précision $30/60=50\ \%$ ; rappel $30/40=75\ \%$ ; $F_1=2\times0{,}5\times0{,}75/(0{,}5+0{,}75)=0{,}6$.
**Les deux détecteurs ont exactement la même exactitude (99,2 %)**, alors que A est inutile et que B retrouve les trois quarts des fraudes. L'exactitude ne mesure ici que la proportion de commandes normales.

### Corrigé 6.2

(a) Rangs : 1 (fraude), 2 (normale), 3 (fraude), 4, 5 (normales), 6 (fraude), 7, 8 (normales).
Après 1 alerte : 1 vraie fraude, précision $1/1=1$, rappel $1/3$. Après 3 : 2 fraudes, précision $2/3\approx0{,}667$, rappel $2/3$. Après 6 : 3 fraudes, précision $3/6=0{,}5$, rappel $3/3=1$.
(b) Les précisions aux rangs des fraudes (1, 3 et 6) sont $1$, $2/3$ et $1/2$ : $\mathrm{AP}=(1+0{,}667+0{,}5)/3\approx\mathbf{0{,}722}$.

```python
print("AP à la main :", round(float(np.mean([1 / 1, 2 / 3, 3 / 6])), 4))
```
<!--sortie-->
```text
AP à la main : 0.7222
```

### Corrigé 6.3

(a) Par la formule de Bayes, avec $P(F)=0{,}005$, $P(A\mid F)=0{,}9$, $P(A\mid\bar F)=0{,}02$ :
$$P(F\mid A)=\frac{0{,}9\times0{,}005}{0{,}9\times0{,}005+0{,}02\times0{,}995}=\frac{0{,}0045}{0{,}0244}\approx\mathbf{0{,}184}.$$
Moins de deux alertes sur dix sont de vraies fraudes.
(b) On veut $P(F\mid A)=0{,}5$, c'est-à-dire autant de vraies que de fausses alertes : $0{,}0045=0{,}995\,x$, d'où $x\approx0{,}0045$ : un taux de fausses alertes d'environ **0,45 %**, soit quatre fois moins que le taux de départ.

```python
p, rec, fpr = 0.005, 0.9, 0.02
print("précision :", round(rec * p / (rec * p + fpr * (1 - p)), 3), "| taux de fausses alertes pour 50 % :", round(rec * p / (1 - p), 4))
```
<!--sortie-->
```text
précision : 0.184 | taux de fausses alertes pour 50 % : 0.0045
```

### Corrigé 6.4

(a) Coût $=(100-\text{trouvées})\times70+5\,n$ :

| Alertes | Fraudes trouvées | Manquées | Coût de manque | Coût de vérification | **Total** |
|---:|---:|---:|---:|---:|---:|
| 100 | 40 | 60 | 4 200 | 500 | **4 700** |
| 200 | 60 | 40 | 2 800 | 1 000 | **3 800** |
| 300 | 70 | 30 | 2 100 | 1 500 | **3 600** |
| 400 | 75 | 25 | 1 750 | 2 000 | **3 750** |
| 500 | 78 | 22 | 1 540 | 2 500 | **4 040** |

Le minimum est à **300 alertes** (3 600 €).
(b) Une alerte supplémentaire rapporte, en moyenne, $p\times70$ € (où $p$ est la probabilité qu'elle soit une vraie fraude) et coûte 5 € : elle vaut la peine si $p>5/70\approx\mathbf{7{,}1\ \%}$. Les tranches : de 200 à 300, 10 fraudes de plus pour 100 alertes, $p=10\ \%>7{,}1\ \%$ : on continue ; de 300 à 400, 5 fraudes de plus, $p=5\ \%<7{,}1\ \%$ : on s'arrête. L'optimum est bien à 300.

### Corrigé 6.5

Moyenne : $263/9\approx29{,}2$ ; écart-type (avec $n-1$) : $\approx24{,}7$ ; $z=(95-29{,}2)/24{,}7\approx\mathbf{2{,}66}$ : **sous le seuil de 3**, la commande n'est pas signalée (masquage). Médiane : 21 ; écarts absolus à 21 : $1,1,0,2,2,1,0,1,74$, rangés $0,0,1,1,1,1,2,2,74$, de médiane **1** ; $\mathrm{MAD}=1$ ; $z^{\text{rob}}=(95-21)/(1{,}4826\times1)\approx\mathbf{49{,}9}$ : la commande est signalée sans ambiguïté.

```python
x = np.array([20, 22, 21, 19, 23, 20, 21, 22, 95.])
print("z classique :", round(float((95 - x.mean()) / x.std(ddof=1)), 2), "| z robuste :", round(float((95 - np.median(x)) / (1.4826 * np.median(np.abs(x - np.median(x))))), 1))
```
<!--sortie-->
```text
z classique : 2.66 | z robuste : 49.9
```

### Corrigé 6.6

Avec $\rho=0{,}6$ : $\Sigma^{-1}=\dfrac1{1-0{,}36}\begin{pmatrix}1&-0{,}6\\-0{,}6&1\end{pmatrix}=\dfrac1{0{,}64}\begin{pmatrix}1&-0{,}6\\-0{,}6&1\end{pmatrix}$. Pour $x=(a,b)$ : $d_M^2=\dfrac{a^2-1{,}2ab+b^2}{0{,}64}$.
- $A=(1,1)$ : $\dfrac{1-1{,}2+1}{0{,}64}=\dfrac{0{,}8}{0{,}64}=\mathbf{1{,}25}$ (distance euclidienne² : 2) ;
- $B=(1,-1)$ : $\dfrac{1+1{,}2+1}{0{,}64}=\dfrac{3{,}2}{0{,}64}=\mathbf{5{,}0}$ (euclidienne² : 2) ;
- $C=(2,0)$ : $\dfrac{4}{0{,}64}=\mathbf{6{,}25}$ (euclidienne² : 4).

Seul $C$ dépasse 5,99. $A$ et $B$ sont à la même distance euclidienne, mais $B$ va à contre-courant de la corrélation positive et sa distance de Mahalanobis est quatre fois supérieure à celle de $A$ ; $B$ reste pourtant sous le seuil, et $C$, simplement plus éloigné du centre, le franchit.

```python
S = np.array([[1, 0.6], [0.6, 1]])
for p in [(1, 1), (1, -1), (2, 0)]:
    p = np.array(p); print(p, "euclidienne^2 =", float(p @ p), "| Mahalanobis^2 =", round(float(p @ np.linalg.inv(S) @ p), 3))
```
<!--sortie-->
```text
[1 1] euclidienne^2 = 2.0 | Mahalanobis^2 = 1.25
[ 1 -1] euclidienne^2 = 2.0 | Mahalanobis^2 = 5.0
[2 0] euclidienne^2 = 4.0 | Mahalanobis^2 = 6.25
```

### Corrigé 6.7

Distances entre points voisins : 1 ; 1,2 ; 1,3 ; 5,5.

| Point | 2 voisins | 2-distance | densité lrd | LOF |
|---|---|---:|---:|---:|
| 0 | 1 ; 2,2 | 2,2 | 0,588 | 0,945 |
| 1 | 0 ; 2,2 | 1,2 | 0,571 | 0,988 |
| 2,2 | 1 ; 3,5 | 1,3 | 0,541 | 1,015 |
| 3,5 | 2,2 ; 1 | 2,5 | 0,526 | 1,056 |
| 9 | 3,5 ; 2,2 | 6,8 | 0,163 | **3,281** |

(Par exemple, pour le point 9 : distances d'atteignabilité à 3,5 et à 2,2 : $\max\{2{,}5;\,5{,}5\}=5{,}5$ et $\max\{1{,}3;\,6{,}8\}=6{,}8$, moyenne 6,15, d'où $\mathrm{lrd}=1/6{,}15\approx0{,}163$ ; les voisins ont des densités 0,526 et 0,541, et $\mathrm{LOF}=\dfrac{(0{,}526+0{,}541)/2}{0{,}163}\approx3{,}28$.) **Le point 9** est le plus anormal ; les quatre autres ont un LOF voisin de 1.

```python
from sklearn.neighbors import LocalOutlierFactor
pts = np.array([0, 1, 2.2, 3.5, 9.0]).reshape(-1, 1)
print("LOF (scikit-learn) :", (-LocalOutlierFactor(n_neighbors=2).fit(pts).negative_outlier_factor_).round(3))
```
<!--sortie-->
```text
LOF (scikit-learn) : [0.945 0.988 1.015 1.056 3.281]
```

### Corrigé 6.8

$c(16)=2\bigl(\ln15+0{,}5772\bigr)-\dfrac{2\times15}{16}=2\times3{,}285-1{,}875\approx\mathbf{4{,}70}$. Scores : $E[h]=3$ : $2^{-3/4{,}70}\approx\mathbf{0{,}64}$ ; $E[h]=6$ : $2^{-6/4{,}70}\approx\mathbf{0{,}41}$ ; $E[h]=c(16)$ : $2^{-1}=\mathbf{0{,}5}$. Seul le premier point (isolé en moyenne en 3 coupures) est jugé anormal (score > 0,5) ; le deuxième, enfoui plus profondément que la moyenne, est jugé très normal.

```python
c16 = 2 * (np.log(15) + 0.5772156649) - 2 * 15 / 16
print(round(float(c16), 3), [round(float(2 ** (-e / c16)), 3) for e in (3, 6, c16)])
```
<!--sortie-->
```text
4.696 [0.642, 0.412, 0.5]
```

### Corrigé 6.9

(a) 8 fraudes $\times$ 60 % $=4{,}8$ retrouvées sur 20 alertes : précision $4{,}8/20=\mathbf{24\ \%}$.
(b) 8 fraudes $\times$ 85 % $=6{,}8$ retrouvées sur 50 alertes : précision $6{,}8/50=\mathbf{13{,}6\ \%}$ ; le rappel monte de 60 % à 85 %, mais le prix est une précision divisée par près de deux.
(c) La contamination n'est pas une propriété des données (on ne connaît pas la vraie proportion de fraudes) : c'est un **choix opérationnel**. Il doit être guidé par le **budget d'alertes** que l'on peut traiter et par le **coût** d'une fraude manquée comparé au coût d'une vérification (section 6.1.6), idéalement évalué sur un petit jeu étiqueté.

### Corrigé 6.10

(a) Par le théorème d'Eckart-Young (volume I, section 1.1.4), la meilleure approximation de rang $\le q$ de $X$ au sens de la norme de Frobenius est $X_q=U_q\Sigma_qV_q^\top$, avec une erreur $\lVert X-X_q\rVert_F^2=\sum_{j>q}\sigma_j^2$. Or $XV_q=U_q\Sigma_q$ (car $V^\top V=I$), donc $X_q=XV_qV_q^\top$. Un autoencodeur linéaire reconstruit $X$ par $XAB$ avec $A\in\mathbb R^{p\times q}$, $B\in\mathbb R^{q\times p}$ : $AB$ est de rang $\le q$, donc $XAB$ aussi ; la meilleure reconstruction possible est $X_q$, atteinte pour $A=V_q$ et $B=V_q^\top$. L'autoencodeur linéaire optimal projette donc sur le sous-espace des $q$ premières composantes principales : c'est l'ACP.
(b) Pour une ligne $x_i$, la reconstruction est $\hat x_i=V_qV_q^\top x_i$, projection orthogonale de $x_i$ sur le sous-espace engendré par $V_q$. Par le théorème de Pythagore, $\lVert x_i\rVert^2=\lVert\hat x_i\rVert^2+\lVert x_i-\hat x_i\rVert^2$ et $\lVert\hat x_i\rVert^2=\lVert V_q^\top x_i\rVert^2$ (car les colonnes de $V_q$ sont orthonormées), d'où $\lVert x_i-\hat x_i\rVert^2=\lVert x_i\rVert^2-\lVert V_q^\top x_i\rVert^2$.
(c) Vérification :

```python
rng = np.random.default_rng(0)
A = rng.normal(size=(5, 5)); M = rng.normal(size=(300, 5)) @ A                 # un tableau à 5 colonnes corrélées
M = M - M.mean(axis=0); q = 2
U, sig, Vt = np.linalg.svd(M, full_matrices=False); Vq = Vt[:q].T
erreur_totale = ((M - M @ Vq @ Vq.T) ** 2).sum()
print("erreur totale :", round(float(erreur_totale), 4), "| somme des sigma_j^2 (j > q) :", round(float((sig[q:] ** 2).sum()), 4))
par_ligne = (M ** 2).sum(axis=1) - ((M @ Vq) ** 2).sum(axis=1)
print("écart maximal sur l'erreur par ligne :", float(np.abs(par_ligne - ((M - M @ Vq @ Vq.T) ** 2).sum(axis=1)).max()))
```
<!--sortie-->
```text
erreur totale : 1162.9741 | somme des sigma_j^2 (j > q) : 1162.9741
écart maximal sur l'erreur par ligne : 1.9317880628477724e-14
```

### Corrigé 6.11

(a) Avec **un neurone** de goulot, le réseau ne peut représenter qu'une droite, celle de la corrélation : les points normaux, proches de cette droite, ont une petite erreur ; les anomalies, à contre-courant, en sont éloignées et ont une grande erreur. Avec **deux neurones** pour deux variables, le goulot n'est plus un goulot : le réseau peut représenter l'identité et reconstruire **tous** les points, anomalies comprises. En théorie, les deux erreurs sont alors **presque nulles** et les anomalies sont invisibles.
(b) Simulation :

```python
from sklearn.neural_network import MLPRegressor
rng = np.random.default_rng(0)
normaux = rng.multivariate_normal([0, 0], [[1, 0.9], [0.9, 1]], 1000)
anomalies = np.column_stack([rng.uniform(1.5, 2.5, 10), -rng.uniform(1.5, 2.5, 10)])      # à contre-courant : x et y de signes opposés
for solveur in ("adam", "lbfgs"):
    for q in (1, 2):
        ae = MLPRegressor(hidden_layer_sizes=(q,), activation="identity", max_iter=2000, random_state=0, solver=solveur).fit(normaux, normaux)
        err = lambda D: ((ae.predict(D) - D) ** 2).sum(axis=1).mean()
        print(f"{solveur:5s} goulot de {q} : erreur des normaux {err(normaux):.2e}, erreur des anomalies {err(anomalies):.2e}")
```
<!--sortie-->
```text
adam  goulot de 1 : erreur des normaux 1.01e-01, erreur des anomalies 7.58e+00
adam  goulot de 2 : erreur des normaux 1.59e-02, erreur des anomalies 1.03e+00
lbfgs goulot de 1 : erreur des normaux 9.61e-02, erreur des anomalies 7.30e+00
lbfgs goulot de 2 : erreur des normaux 1.06e-09, erreur des anomalies 2.04e-08
```

**Lecture.** Avec un neurone, l'erreur des anomalies est environ 75 fois celle des points normaux, quel que soit l'optimiseur (7,6 contre 0,10 avec `adam` ; 7,3 contre 0,096 avec `lbfgs`) : le réseau est contraint de projeter sur une droite. Avec deux neurones et le solveur `lbfgs`, le réseau apprend l'identité : **les deux erreurs sont presque nulles** (de l'ordre de $10^{-9}$ et $10^{-8}$), et l'anomalie est parfaitement reconstruite, donc invisible. Avec `adam`, en revanche, l'optimisation s'arrête avant d'avoir appris l'identité : l'erreur des anomalies reste élevée (1,03 contre 0,016 pour les normaux) et le détecteur *fonctionne encore*. Une explication plausible, que nous n'avons pas testée, est que la direction de faible variance (0,1 sur un total de 2) fournit un gradient faible et est apprise lentement. Ce qui est établi, c'est que **la capacité effective d'un réseau dépend de l'optimisation autant que de l'architecture** : un goulot trop large peut sembler sans danger tant que l'entraînement est insuffisant, et cesser de l'être avec un meilleur optimiseur. C'est une raison de plus de régler sur un jeu de validation.

### Corrigé 6.12

On réutilise les scores `s_test` de l'application 6.6 :

```python
voisins_s, iso_s = s_test["voisins"], s_test["isolement"]
def trouvees(indices): return int(y_test[list(indices)].sum())
a = np.argsort(-voisins_s)[:budget]
moitie = budget // 2
ens = list(np.argsort(-voisins_s)[:moitie])
for i in np.argsort(-iso_s):                                  # on complète avec la forêt, sans doublon
    if len(ens) >= budget: break
    if i not in ens: ens.append(i)
c = np.argsort(-(rankdata(voisins_s) + rankdata(iso_s)))[:budget]
print("(a) 180 premières des voisins            :", trouvees(a), "fraudes sur", int(y_test.sum()))
print("(b) 90 + 90 sans doublon                 :", trouvees(ens))
print("(c) 180 premières du rang moyen          :", trouvees(c))
```
<!--sortie-->
```text
(a) 180 premières des voisins            : 66 fraudes sur 146
(b) 90 + 90 sans doublon                 : 59
(c) 180 premières du rang moyen          : 57
```

**Lecture.** Les 180 premières alertes des voisins retrouvent **66** fraudes sur 146, la combinaison 90 + 90 en retrouve 59 et la moyenne des rangs 57 : **aucune des combinaisons ne fait mieux que le meilleur détecteur seul**. La raison est double. D'une part, la forêt d'isolement est moins bonne que les voisins sur ces données (AP de 0,33 contre 0,46) : lui consacrer la moitié du budget retire des alertes de meilleure qualité. D'autre part, les deux détecteurs se recouvrent fortement (133 alertes communes sur 180, indice de Jaccard de 0,59, application 6.6) : la forêt d'isolement apporte peu de commandes que les voisins n'avaient pas déjà dans leurs 180 premières, et la combinaison (b) remplace les rangs 91 à 180 des voisins par des alertes de la forêt, de moindre qualité. Combiner demande des détecteurs **comparables en qualité** et **complémentaires** (peu de recouvrement).
