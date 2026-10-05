# Chapitre 5 : Analyse de survie — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 5 du livre (censure, Kaplan-Meier, Cox, modèles paramétriques, risques concurrents). Vous y trouverez **six applications guidées**, qui écrivent à la main les estimateurs du chapitre et les comparent aux bibliothèques, puis **treize exercices corrigés**. Les données sont celles du livre : `donnees/clients.csv` (2 000 clients, simulés) et, pour la dernière application, une table de risques concurrents simulée dans le chapitre. Prérequis : les sections 5.1 à 5.5 du livre.

## Préparation

Les estimateurs du chapitre sont écrits dans `build/outils_ch05.py` (on y trouve le code complet de `kaplan_meier`, `logrank`, `cox_ph`, `test_ph`, `ajuster`, `incidence_cumulee`, etc.). Chaque application en rappelle l'idée et l'utilise ; les exercices les réutilisent. Commençons par charger la boîte à outils et les données.

```python
import sys
sys.path.insert(0, "build")                      # dossier de la boîte à outils du chapitre
import numpy as np
import pandas as pd
from scipy import stats
from outils_ch05 import *                        # kaplan_meier, logrank, cox_ph, ajuster, incidence_cumulee...

c = pd.read_csv("donnees/clients.csv")
y, d = c["duree_mois"].to_numpy(), c["churn"].to_numpy()          # durées et départs observés des 2 000 clients
y8 = np.array([3, 5, 6, 8, 10, 12, 14, 14.])                      # les huit clients du livre (5.1.1)
d8 = np.array([1, 1, 0, 1, 0, 1, 0, 0])
print(len(c), "clients,", int(d.sum()), "départs observés")
```
<!--sortie-->
```text
2000 clients, 977 départs observés
```

## Applications

### Application 5.1 — L'expérience de la censure

**Objectif.** Voir de ses yeux que les moyennes « naïves » sont biaisées, mesurer la part des pertes de vue, et estimer un taux de départ constant avec la vraisemblance censurée (livre, 5.1).

**Étape 1 : une expérience contrôlée.** Nous simulons 5 000 clients dont nous connaissons les vraies durées (loi de Weibull de forme 1,35 et d'échelle 36 mois), puis nous les observons pendant une durée aléatoire entre 6 et 60 mois.

```python
from math import gamma

rng = np.random.default_rng(51)
n, k, echelle = 5000, 1.35, 36.0
T_vraie = echelle * rng.weibull(k, n)            # durées complètes (inconnues en pratique)
C = rng.uniform(6, 60, n)                        # durée pendant laquelle on peut observer chaque client
yy = np.minimum(T_vraie, C)                      # ce que l'on voit
parti = (T_vraie <= C).astype(int)

print(f"part de clients censurés                   : {100 * (1 - parti.mean()):.1f} %")
print(f"VRAIE durée moyenne (formule exacte)       : {echelle * gamma(1 + 1 / k):.1f} mois")
print(f"(1) moyenne de toutes les durées observées : {yy.mean():.1f} mois")
print(f"(2) moyenne des seuls clients partis       : {yy[parti == 1].mean():.1f} mois")
```
<!--sortie-->
```text
part de clients censurés                   : 44.8 %
VRAIE durée moyenne (formule exacte)       : 33.0 mois
(1) moyenne de toutes les durées observées : 21.5 mois
(2) moyenne des seuls clients partis       : 18.5 mois
```

*Lecture.* Les deux moyennes naïves sont très en dessous de la vérité, et aucune ne se rapproche si l'on ajoute des clients : ce sont des estimateurs biaisés. *À essayer :* observer pendant 30 à 84 mois au lieu de 6 à 60. Que deviennent les deux moyennes ?

**Étape 2 : d'où viennent les durées censurées du fichier ?** La date de fin d'observation est le 31 décembre 2025. Un client censuré dont la durée vaut exactement son suivi possible est un censuré administratif ; les autres sont des pertes de vue.

```python
c["date_inscription"] = pd.to_datetime(c["date_inscription"])
c["suivi_possible"] = (pd.Timestamp("2025-12-31") - c["date_inscription"]).dt.days / 30.4375

censures = c[c["churn"] == 0]
admin = (censures["duree_mois"] - censures["suivi_possible"]).abs() < 0.01
print("censurés administratifs :", int(admin.sum()), "| pertes de vue :", int((~admin).sum()))
print("suivi possible de", round(c["suivi_possible"].min(), 1), "à", round(c["suivi_possible"].max(), 1), "mois")
```
<!--sortie-->
```text
censurés administratifs : 660 | pertes de vue : 363
suivi possible de 6.0 à 84.0 mois
```

**Étape 3 : le taux de départ constant.** Pour un risque constant, le maximum de vraisemblance donne $\hat\lambda=D/\sum y_i$. Vérifions-le sur les huit clients avec un optimiseur (la fonction `log_vraisemblance_exp` est dans la boîte à outils), puis appliquons-le aux 2 000 clients.

```python
from scipy.optimize import minimize_scalar

opt = minimize_scalar(lambda l: -log_vraisemblance_exp(l, y8, d8), bounds=(1e-4, 1), method="bounded")
print(f"8 clients : λ̂ (optimiseur) = {opt.x:.4f} | formule D/Σy = {d8.sum() / y8.sum():.4f}")

lam = d.sum() / y.sum()
se = lam / np.sqrt(d.sum())
print(f"2000 clients : D = {d.sum()}, exposition = {y.sum():,.0f} mois-clients")
print(f"λ̂ = {lam:.5f} par mois (IC95 : {lam - 1.96 * se:.5f} à {lam + 1.96 * se:.5f})")
print(f"durée moyenne 1/λ̂ = {1 / lam:.1f} mois | médiane ln2/λ̂ = {np.log(2) / lam:.1f} mois | moyenne naïve : {y.mean():.1f} mois")
```
<!--sortie-->
```text
8 clients : λ̂ (optimiseur) = 0.0556 | formule D/Σy = 0.0556
2000 clients : D = 977, exposition = 46,761 mois-clients
λ̂ = 0.02089 par mois (IC95 : 0.01958 à 0.02220)
durée moyenne 1/λ̂ = 47.9 mois | médiane ln2/λ̂ = 33.2 mois | moyenne naïve : 23.4 mois
```

*Lecture.* L'estimation exponentielle donne environ 48 mois de durée moyenne, plus du double de la moyenne naïve. Mais elle suppose un risque constant : l'application 5.2 montrera que Kaplan-Meier ne le confirme pas.

### Application 5.2 — Kaplan-Meier écrit à la main

**Objectif.** Construire l'estimateur de Kaplan-Meier, le comparer à `statsmodels` et à R, en donner l'incertitude et deux résumés : la médiane et la durée moyenne restreinte (livre, 5.2.1 à 5.2.4, 5.2.7).

**Étape 1 : les huit clients.** Le tableau donne, à chaque instant de départ, l'ensemble à risque $n_j$, les départs $d_j$ et la survie cumulée. La fonction `kaplan_meier(y, d)` de la boîte à outils renvoie les instants, les effectifs à risque, les départs, la survie et la somme de Greenwood.

```python
print(tableau_km(y8, d8).to_string(index=False))
tj8, n8, dj8, S8, gw8 = kaplan_meier(y8, d8)
print("survie aux instants de départ :", S8.round(4))
```
<!--sortie-->
```text
 t_j  n_j (à risque)  d_j (départs)  censurés en t_j  d_j/n_j  S(t_j)  somme Greenwood
 3.0               8              1                0   0.1250   0.875           0.0179
 5.0               7              1                0   0.1429   0.750           0.0417
 8.0               5              1                0   0.2000   0.600           0.0917
12.0               3              1                0   0.3333   0.400           0.2583
survie aux instants de départ : [0.875 0.75  0.6   0.4  ]
```

*Lecture.* On retrouve les valeurs du livre : 0,875, 0,75, 0,6, puis 0,4. Les censurés sortent de l'ensemble à risque sans faire bouger la courbe.

**Étape 2 : les 2 000 clients, comparés à `statsmodels`.**

```python
from statsmodels.duration.survfunc import SurvfuncRight

tj, n, dj, S, gw = kaplan_meier(y, d)
sf = SurvfuncRight(y, d)
print(f"{'mois':>5} {'à la main':>10} {'statsmodels':>12} {'ET Greenwood':>13} {'ET statsmodels':>15}")
for t in (12, 24, 36, 48, 60):
    i = np.searchsorted(sf.surv_times, t, side="right") - 1
    s = surv_at(t, tj, S)
    print(f"{t:>5} {s:>10.5f} {sf.surv_prob[i]:>12.5f} {s * np.sqrt(surv_at(t, tj, gw, avant=0.0)):>13.5f} {sf.surv_prob_se[i]:>15.5f}")
```
<!--sortie-->
```text
 mois  à la main  statsmodels  ET Greenwood  ET statsmodels
   12    0.82519      0.82519       0.00888         0.00888
   24    0.63376      0.63376       0.01211         0.01211
   36    0.45275      0.45275       0.01396         0.01396
   48    0.30758      0.30758       0.01498         0.01498
   60    0.24754      0.24754       0.01558         0.01558
```

Et avec la référence de la discipline, le paquet R `survival` :

```r
library(survival)
clients <- read.csv("donnees/clients.csv")
km_all <- survfit(Surv(duree_mois, churn) ~ 1, data = clients)
print(summary(km_all, times = c(12, 24, 36, 48, 60)))
```
<!--sortie-->
```text
Call: survfit(formula = Surv(duree_mois, churn) ~ 1, data = clients)

 time n.risk n.event survival std.err lower 95% CI upper 95% CI
   12   1378     323    0.825 0.00888        0.808        0.843
   24    814     286    0.634 0.01211        0.610        0.658
   36    416     200    0.453 0.01396        0.426        0.481
   48    186     111    0.308 0.01498        0.280        0.338
   60     96      31    0.248 0.01558        0.219        0.280
```

*Lecture.* Les trois sources donnent la même courbe et les mêmes erreurs standard. Remarquez la colonne `n.risk` de R : à 60 mois, il reste 96 clients sous observation contre 1 378 à 12 mois.

**Étape 3 : les intervalles de confiance.** Trois constructions (plan, log, log-log), à 36 et 60 mois, puis pour les huit clients :

```python
for t in (36, 60):
    s, plan, log_, loglog = intervalles(t, tj, S, gw)
    print(f"t = {t} : S = {s:.4f} | plan [{plan[0]:.4f} ; {plan[1]:.4f}] | log [{log_[0]:.4f} ; {log_[1]:.4f}] | log-log [{loglog[0]:.4f} ; {loglog[1]:.4f}]")
s8, plan8, log8, ll8 = intervalles(12, tj8, S8, gw8)
print(f"8 clients, t = 12 : S = {s8:.2f} | plan [{plan8[0]:.2f} ; {plan8[1]:.2f}] | log-log [{ll8[0]:.2f} ; {ll8[1]:.2f}]")
```
<!--sortie-->
```text
t = 36 : S = 0.4528 | plan [0.4254 ; 0.4801] | log [0.4262 ; 0.4810] | log-log [0.4252 ; 0.4799]
t = 60 : S = 0.2475 | plan [0.2170 ; 0.2781] | log [0.2188 ; 0.2800] | log-log [0.2176 ; 0.2786]
8 clients, t = 12 : S = 0.40 | plan [0.00 ; 0.80] | log-log [0.07 ; 0.73]
```

*Lecture.* Sur 2 000 clients, les trois intervalles sont presque identiques. Sur huit clients, l'intervalle plan est immense (de presque 0 à 0,80) ; le log-log est plus raisonnable.

**Étape 4 : médiane et durée moyenne restreinte.**

```python
z = 1.959964
S_bas, S_haut = S * np.exp(-z * np.sqrt(gw)), S * np.exp(z * np.sqrt(gw))      # bande « log »
print(f"médiane : {tj[S <= 0.5][0]:.2f} mois ; IC95 [{tj[S_bas <= 0.5][0]:.1f} ; {tj[S_haut <= 0.5][0]:.1f}]")
print("durée moyenne restreinte, 8 clients, tau = 14 :", round(rmst(tj8, S8, 14), 2), "mois")
for tau in (24, 36, 60):
    print(f"2000 clients, tau = {tau} : {rmst(tj, S, tau):.2f} mois")
```
<!--sortie-->
```text
médiane : 32.45 mois ; IC95 [29.9 ; 34.2]
durée moyenne restreinte, 8 clients, tau = 14 : 10.2 mois
2000 clients, tau = 24 : 19.76 mois
2000 clients, tau = 36 : 26.19 mois
2000 clients, tau = 60 : 33.94 mois
```

**Étape 5 : et si les pertes de vue étaient des départs ? (analyse de sensibilité)** On recompte comme départs les clients censurés avant la fin de l'étude : c'est le pire cas.

```python
c["date_inscription"] = pd.to_datetime(c["date_inscription"])
suivi = (pd.Timestamp("2025-12-31") - c["date_inscription"]).dt.days / 30.4375
perdu = ((c["churn"] == 0) & (suivi - c["duree_mois"] > 0.01)).to_numpy()
tj_p, _, _, S_p, _ = kaplan_meier(y, np.where(perdu, 1, d))         # pertes de vue recomptées comme départs
print("pertes de vue :", int(perdu.sum()))
for t in (12, 24, 36):
    print(f"{t:>3} mois : censure non informative {surv_at(t, tj, S):.3f} | pire cas {surv_at(t, tj_p, S_p):.3f}")
```
<!--sortie-->
```text
pertes de vue : 363
 12 mois : censure non informative 0.825 | pire cas 0.753
 24 mois : censure non informative 0.634 | pire cas 0.526
 36 mois : censure non informative 0.453 | pire cas 0.341
```

*Lecture.* À 36 mois, la survie passe de 0,45 à 0,34 dans le pire cas : l'hypothèse de censure non informative pèse plus que l'incertitude statistique.

### Application 5.3 — Comparer des groupes, et le piège de l'entrée tardive

**Objectif.** Écrire le test du log-rank, le comparer aux logiciels, corriger les comparaisons multiples et mesurer l'effet d'une entrée tardive (livre, 5.2.5 et 5.2.6).

**Étape 1 : le log-rank sur les huit clients.** Imaginons que C, E, F et G aient reçu l'offre. `logrank(y, d, groupe)` renvoie les départs observés et attendus, le $\chi^2$, ses degrés de liberté et la p-valeur.

```python
groupe8 = np.array(["sans", "sans", "avec", "sans", "avec", "avec", "avec", "sans"])      # clients A à H
O8, E8, chi8, ddl8, p8 = logrank(y8, d8, groupe8)
print(f"observés {O8} | attendus {E8.round(3)} | chi2 = {chi8:.2f} | p = {p8:.3f}")
```
<!--sortie-->
```text
observés [1. 3.] | attendus [2.338 1.662] | chi2 = 1.87 | p = 0.171
```

**Étape 2 : l'offre de bienvenue sur les 2 000 clients, avec trois outils.**

```python
from statsmodels.duration.survfunc import survdiff

O, E, chi2, ddl, p = logrank(y, d, c["offre_bienvenue"])
print(f"à la main   : observés {O.astype(int)}, attendus {E.round(1)}, chi2 = {chi2:.2f}, p = {p:.1e}")
print("statsmodels : chi2 = %.2f, p = %.1e" % survdiff(y, d, c["offre_bienvenue"]))
```
<!--sortie-->
```text
à la main   : observés [528 449], attendus [435.6 541.4], chi2 = 35.54, p = 2.5e-09
statsmodels : chi2 = 35.54, p = 2.5e-09
```

```r
print(survdiff(Surv(duree_mois, churn) ~ offre_bienvenue, data = clients))
```
<!--sortie-->
```text
Call:
survdiff(formula = Surv(duree_mois, churn) ~ offre_bienvenue, 
    data = clients)

                     N Observed Expected (O-E)^2/E (O-E)^2/V
offre_bienvenue=0  985      528      436      19.6      35.5
offre_bienvenue=1 1015      449      541      15.8      35.5

 Chisq= 35.5  on 1 degrees of freedom, p= 3e-09 
```

**Étape 3 : trois canaux, puis deux à deux avec la correction de Holm.**

```python
O3, E3, chi3, ddl3, p3 = logrank(y, d, c["canal_acquisition"])
print(f"3 canaux : chi2 = {chi3:.1f} à {ddl3} ddl, p = {p3:.1e}")

paires = [("Boutique", "Réseaux"), ("Boutique", "Site"), ("Site", "Réseaux")]
brutes = []
for a, b in paires:
    m = c["canal_acquisition"].isin([a, b]).to_numpy()
    brutes.append(logrank(y[m], d[m], c["canal_acquisition"].to_numpy()[m])[4])
holm, courant = np.empty(3), 0.0
for rang, i in enumerate(np.argsort(brutes)):
    courant = max(courant, min(1.0, (3 - rang) * brutes[i]))       # (m - rang) x p, puis suite croissante
    holm[i] = courant
print(pd.DataFrame({"comparaison": [f"{a} / {b}" for a, b in paires], "p brute": brutes, "p Holm": holm}).to_string(index=False, float_format=lambda x: f"{x:.2e}"))
```
<!--sortie-->
```text
3 canaux : chi2 = 55.0 à 2 ddl, p = 1.1e-12
       comparaison  p brute   p Holm
Boutique / Réseaux 5.27e-13 1.58e-12
   Boutique / Site 8.61e-04 8.61e-04
    Site / Réseaux 3.02e-05 6.05e-05
```

**Étape 4 : autres pondérations du log-rank.**

```python
for nom, w, kw in [("log-rank", None, {}), ("Gehan-Breslow", "gb", {}), ("Tarone-Ware", "tw", {}), ("Fleming-Harrington p=1", "fh", {"fh_p": 1})]:
    chi, pv = survdiff(y, d, c["offre_bienvenue"], weight_type=w, **kw)
    print(f"{nom:<24} chi2 = {chi:6.2f}   p = {pv:.1e}")
```
<!--sortie-->
```text
log-rank                 chi2 =  35.54   p = 2.5e-09
Gehan-Breslow            chi2 =  31.45   p = 2.0e-08
Tarone-Ware              chi2 =  35.12   p = 3.1e-09
Fleming-Harrington p=1   chi2 =  34.98   p = 3.3e-09
```

**Étape 5 : l'entrée tardive.** 6 000 clients de loi de Weibull ne sont enregistrés qu'à leur adhésion au programme de fidélité (uniforme entre 0 et 30 mois après le premier achat) s'ils sont encore clients. Ignorer cette règle surestime la survie ; `kaplan_meier(..., entree=...)` la respecte.

```python
rng = np.random.default_rng(52)
N = 6000
T = 36 * rng.weibull(1.35, N)                    # durées vraies
E = rng.uniform(0, 30, N)                        # date d'adhésion (mois après le premier achat)
vus = T > E                                      # seuls les clients encore là à l'adhésion sont enregistrés
Tv, Ev = T[vus], E[vus]
Cv = Ev + rng.uniform(6, 60, vus.sum())          # fin d'observation après l'adhésion
Yv, Dv = np.minimum(Tv, Cv), (Tv <= Cv).astype(int)

tj_n, _, _, S_n, _ = kaplan_meier(Yv, Dv)                       # entrées tardives ignorées
tj_c, _, _, S_c, _ = kaplan_meier(Yv, Dv, entree=Ev)             # entrées tardives prises en compte
sf_e = SurvfuncRight(Yv, Dv, entry=Ev)
print("clients vus :", int(vus.sum()), "sur", N)
print(f"{'mois':>5} {'vraie S(t)':>11} {'ignorer':>9} {'avec entrée':>12} {'statsmodels':>12}")
for t in (6, 12, 24, 36):
    i = np.searchsorted(sf_e.surv_times, t, side="right") - 1
    print(f"{t:>5} {np.exp(-(t / 36) ** 1.35):>11.3f} {surv_at(t, tj_n, S_n):>9.3f} {surv_at(t, tj_c, S_c):>12.3f} {sf_e.surv_prob[i]:>12.3f}")
```
<!--sortie-->
```text
clients vus : 4417 sur 6000
 mois  vraie S(t)   ignorer  avec entrée  statsmodels
    6       0.915     0.988        0.913        0.913
   12       0.797     0.940        0.804        0.804
   24       0.561     0.759        0.577        0.577
   36       0.368     0.490        0.365        0.365
```

*Lecture.* Ignorer l'entrée donne 0,76 à 24 mois pour une vérité de 0,56. En la prenant en compte, on est à deux points près.

### Application 5.4 — Le modèle de Cox à la main

**Objectif.** Calculer la vraisemblance partielle, la maximiser par Newton-Raphson, ajuster Cox sur les 2 000 clients, tester la proportionnalité des risques et prédire des courbes (livre, 5.3).

**Étape 1 : Newton-Raphson sur les huit clients.** La fonction `score_info(beta, y, d, x)` calcule le score $U(\beta)$ et l'information $I(\beta)$ d'une covariable. On suppose que C, E, F et G ont reçu l'offre.

```python
x8 = np.array([0, 0, 1, 0, 1, 1, 1, 0], float)            # 1 = a reçu l'offre

U0, I0 = score_info(0.0, y8, d8, x8)
print(f"en beta = 0 : U = {U0:.4f}, I = {I0:.4f}, U²/I = {U0 ** 2 / I0:.3f} (chi2 du log-rank des huit clients : 1.87)")
beta = 0.0
for it in range(5):                                        # Newton-Raphson : beta <- beta + U/I
    U, I = score_info(beta, y8, d8, x8)
    beta += U / I
    print(f"itération {it + 1} : beta = {beta:8.5f}")
print("rapport de risques estimé :", round(np.exp(beta), 3))
```
<!--sortie-->
```text
en beta = 0 : U = -1.3381, I = 0.9571, U²/I = 1.871 (chi2 du log-rank des huit clients : 1.87)
itération 1 : beta = -1.39804
itération 2 : beta = -1.45965
itération 3 : beta = -1.46056
itération 4 : beta = -1.46057
itération 5 : beta = -1.46057
rapport de risques estimé : 0.232
```

*Lecture.* La statistique de score en $\beta=0$ égale le $\chi^2$ du log-rank (1,87), et la méthode converge en quatre itérations.

**Étape 2 : les 2 000 clients.** `cox_ph(y, d, X)` maximise la vraisemblance partielle (ex aequo à la Breslow) et renvoie les coefficients et leur matrice de covariance.

```python
X = pd.get_dummies(c[["offre_bienvenue", "age", "canal_acquisition"]], drop_first=True, dtype=float)
fit = cox_ph(y, d, X.to_numpy())
se = np.sqrt(np.diag(fit["cov"]))
tableau = pd.DataFrame({"coef": fit["beta"], "ET": se, "HR": np.exp(fit["beta"]),
                        "HR bas": np.exp(fit["beta"] - 1.96 * se), "HR haut": np.exp(fit["beta"] + 1.96 * se)}, index=X.columns)
print(tableau.round(4).to_string())
```
<!--sortie-->
```text
                             coef      ET      HR  HR bas  HR haut
offre_bienvenue           -0.4061  0.0645  0.6662  0.5871   0.7561
age                       -0.0136  0.0030  0.9865  0.9806   0.9924
canal_acquisition_Réseaux  0.6351  0.0842  1.8872  1.6002   2.2256
canal_acquisition_Site     0.3258  0.0887  1.3851  1.1641   1.6481
```

Comparaison avec `statsmodels` et avec R :

```python
from statsmodels.duration.hazard_regression import PHReg

ph = PHReg(y, X, status=d, ties="breslow").fit()
print("statsmodels :", np.round(ph.params, 5))
print("à la main   :", np.round(fit["beta"], 5))
```
<!--sortie-->
```text
statsmodels : [-0.40612 -0.01363  0.63508  0.3258 ]
à la main   : [-0.40612 -0.01363  0.63508  0.3258 ]
```

```r
clients$canal_acquisition <- factor(clients$canal_acquisition, levels = c("Boutique", "Réseaux", "Site"))
cox_r <- coxph(Surv(duree_mois, churn) ~ offre_bienvenue + age + canal_acquisition, data = clients, ties = "breslow")
print(round(summary(cox_r)$coefficients[, c("coef", "se(coef)")], 5))
```
<!--sortie-->
```text
                             coef se(coef)
offre_bienvenue          -0.40612  0.06454
age                      -0.01363  0.00304
canal_acquisitionRéseaux  0.63508  0.08415
canal_acquisitionSite     0.32580  0.08869
```

**Étape 3 : la proportionnalité des risques.** `test_ph` calcule le test de score de Grambsch-Therneau (le temps est remplacé par son rang) pour chaque variable et globalement.

```python
chi2_j, chi2_glob = test_ph(y, d, X.to_numpy(), fit)
res_ph = pd.DataFrame({"chi2": chi2_j, "p": stats.chi2.sf(chi2_j, 1)}, index=X.columns)
res_ph.loc["GLOBAL (4 ddl)"] = [chi2_glob, stats.chi2.sf(chi2_glob, 4)]
print(res_ph.round(4).to_string())
```
<!--sortie-->
```text
                             chi2       p
offre_bienvenue            0.5588  0.4548
age                        0.7292  0.3931
canal_acquisition_Réseaux  2.2063  0.1375
canal_acquisition_Site     0.0146  0.9037
GLOBAL (4 ddl)             4.9502  0.2924
```

```r
print(cox.zph(cox_r, transform = "rank", terms = FALSE))
```
<!--sortie-->
```text
                          chisq df    p
offre_bienvenue          0.5588  1 0.45
age                      0.7292  1 0.39
canal_acquisitionRéseaux 2.2063  1 0.14
canal_acquisitionSite    0.0146  1 0.90
GLOBAL                   4.9502  4 0.29
```

**Étape 4 : des risques qui se croisent.** Deux groupes de 750 clients : risque décroissant (Weibull de forme 0,8) pour A, croissant (forme 1,8) pour B. Cox donne un seul rapport de risques, que le test dénonce.

```python
rng = np.random.default_rng(54)
nn = 1500
g = np.repeat([0, 1], nn // 2)
T = np.where(g == 0, 30 * rng.weibull(0.8, nn), 40 * rng.weibull(1.8, nn))
C = rng.uniform(10, 80, nn)
yc, dc = np.minimum(T, C), (T <= C).astype(int)
Xg = g[:, None].astype(float)

fit_c = cox_ph(yc, dc, Xg)
chi2_c, _ = test_ph(yc, dc, Xg, fit_c)
print(f"HR (B contre A) = {np.exp(fit_c['beta'][0]):.2f} | test de proportionnalité : chi2 = {chi2_c[0]:.1f}, p = {stats.chi2.sf(chi2_c[0], 1):.1e}")
```
<!--sortie-->
```text
HR (B contre A) = 0.73 | test de proportionnalité : chi2 = 216.3, p = 5.7e-49
```

**Étape 5 : le biais d'immortalité.** La carte de fidélité (aucun effet réel) est remise au mois 12 aux clients encore là. Traitée comme variable fixe, elle semble protectrice ; traitée comme variable dépendant du temps, elle est neutre.

```python
rng = np.random.default_rng(53)
N = 3000
T = rng.exponential(1 / 0.03, N)                           # risque constant, indépendant de la carte
C = rng.uniform(24, 60, N)
Y, D = np.minimum(T, C), (T <= C).astype(int)
carte = (Y > 12) & (rng.random(N) < 0.5)                    # carte remise au mois 12 à la moitié des clients encore là

naif = PHReg(Y, carte.astype(float)[:, None], status=D, ties="efron").fit()
porteurs = np.where(carte)[0]                              # deux épisodes pour les porteurs : [0, 12[ puis [12, Y]
debut = np.concatenate([np.zeros(N), np.full(len(porteurs), 12.0)])
fin = np.concatenate([np.where(carte, 12.0, Y), Y[porteurs]])
statut = np.concatenate([np.where(carte, 0, D), D[porteurs]])
x_carte = np.concatenate([np.zeros(N), np.ones(len(porteurs))])
juste = PHReg(fin, x_carte[:, None], status=statut, entry=debut, ties="efron").fit()
print(f"analyse naïve   : HR = {np.exp(naif.params[0]):.2f}")
print(f"analyse correcte : HR = {np.exp(juste.params[0]):.2f}")
```
<!--sortie-->
```text
analyse naïve   : HR = 0.46
analyse correcte : HR = 1.03
```

**Étape 6 : prédire des courbes de survie.** Le risque cumulé de base est estimé par Breslow ; $S(t\mid x)=\exp[-H_0(t)\,e^{x^\top\beta}]$.

```python
H0 = np.cumsum(fit["dj"] / fit["s0"])                      # risque cumulé de base
def survie_pred(t, x):
    i = np.searchsorted(fit["tj"], t, side="right") - 1
    return float(np.exp(-(H0[i] if i >= 0 else 0.0) * np.exp(np.asarray(x, float) @ fit["beta"])))

profils = {"A : Réseaux, 25 ans, sans offre": [0, 25, 1, 0], "B : Réseaux, 25 ans, avec offre": [1, 25, 1, 0],
           "C : Boutique, 45 ans, avec offre": [1, 45, 0, 0]}            # colonnes : offre, âge, Réseaux, Site
for nom, x in profils.items():
    print(f"{nom:<34}", [round(survie_pred(t, x), 3) for t in (12, 24, 36, 60)])
```
<!--sortie-->
```text
A : Réseaux, 25 ans, sans offre    [0.711, 0.438, 0.23, 0.069]
B : Réseaux, 25 ans, avec offre    [0.797, 0.577, 0.375, 0.168]
C : Boutique, 45 ans, avec offre   [0.912, 0.801, 0.673, 0.487]
```

**Étape 7 : l'indice de concordance.**

```python
print("indice de concordance :", round(indice_concordance(y, d, X.to_numpy() @ fit["beta"]), 4))
```
<!--sortie-->
```text
indice de concordance : 0.6052
```

### Application 5.5 — Modèles paramétriques et valeur vie client

**Objectif.** Ajuster par maximum de vraisemblance quatre lois de durée, choisir par l'AIC, puis chiffrer une valeur vie client avec une analyse de sensibilité (livre, 5.4). **Les hypothèses de marge, d'actualisation et de coût de l'offre sont inventées** : à remplacer par les vôtres.

**Étape 1 : quatre lois.** `ajuster(loi, y, d, X)` maximise la vraisemblance d'un modèle de temps de vie accéléré ; la première colonne de `X` est la constante.

```python
Xd = pd.get_dummies(c[["offre_bienvenue", "age", "canal_acquisition"]], drop_first=True, dtype=float)
Xc = np.column_stack([np.ones(len(c)), Xd.to_numpy()])
noms = ["(constante)"] + list(Xd.columns)

ajust = {loi: ajuster(loi, y, d, Xc) for loi in ("weibull", "lognormale", "loglogistique")}
ajust["exponentielle"] = ajuster("weibull", y, d, Xc, sigma_fixe=1.0)

wb = ajust["weibull"]
se_w = np.sqrt(np.diag(wb["cov"]))
print(pd.DataFrame({"gamma": wb["theta"][:-1], "ET": se_w[:-1], "e^gamma": np.exp(wb["theta"][:-1])}, index=noms).round(4).to_string())
print("sigma =", round(np.exp(wb["theta"][-1]), 4), "-> forme k =", round(1 / np.exp(wb["theta"][-1]), 4), "| log-vraisemblance :", round(wb["ll"], 3))
```
<!--sortie-->
```text
                            gamma      ET  e^gamma
(constante)                3.5257  0.0970  33.9765
offre_bienvenue            0.3132  0.0489   1.3678
age                        0.0102  0.0023   1.0102
canal_acquisition_Réseaux -0.4799  0.0636   0.6188
canal_acquisition_Site    -0.2452  0.0671   0.7825
sigma = 0.7563 -> forme k = 1.3223 | log-vraisemblance : -4657.378
```

```r
w_r <- survreg(Surv(duree_mois, churn) ~ offre_bienvenue + age + canal_acquisition, data = clients, dist = "weibull")
print(round(summary(w_r)$table, 4))
```
<!--sortie-->
```text
                           Value Std. Error        z     p
(Intercept)               3.5257     0.0970  36.3418 0e+00
offre_bienvenue           0.3132     0.0489   6.4037 0e+00
age                       0.0102     0.0023   4.4328 0e+00
canal_acquisitionRéseaux -0.4799     0.0636  -7.5472 0e+00
canal_acquisitionSite    -0.2452     0.0671  -3.6565 3e-04
Log(scale)               -0.2794     0.0253 -11.0435 0e+00
```

**Étape 2 : choisir la loi.**

```python
lignes = [{"loi": loi, "paramètres": r["k"], "log-vraisemblance": round(r["ll"], 2), "AIC": round(2 * r["k"] - 2 * r["ll"], 2)} for loi, r in ajust.items()]
print(pd.DataFrame(lignes).sort_values("AIC").to_string(index=False))
lr = 2 * (ajust["weibull"]["ll"] - ajust["exponentielle"]["ll"])
print(f"exponentielle contre Weibull : chi2 = {lr:.1f} (1 ddl), p = {stats.chi2.sf(lr, 1):.1e}")
```
<!--sortie-->
```text
          loi  paramètres  log-vraisemblance     AIC
      weibull           6           -4657.38 9326.76
loglogistique           6           -4663.73 9339.45
   lognormale           6           -4697.20 9406.40
exponentielle           5           -4710.58 9431.17
exponentielle contre Weibull : chi2 = 106.4 (1 ddl), p = 6.0e-25
```

**Étape 3 : conversion vers Cox.** Pour la Weibull, $\beta=-\gamma/\sigma$ : les coefficients convertis doivent être proches de ceux de l'application 5.4.

```python
sigma = np.exp(wb["theta"][-1])
print(pd.DataFrame({"Weibull converti": -wb["theta"][1:-1] / sigma, "Cox (application 5.4)": fit["beta"]}, index=noms[1:]).round(4).to_string())
```
<!--sortie-->
```text
                           Weibull converti  Cox (application 5.4)
offre_bienvenue                     -0.4141                -0.4061
age                                 -0.0135                -0.0136
canal_acquisition_Réseaux            0.6346                 0.6351
canal_acquisition_Site               0.3242                 0.3258
```

**Étape 4 : la valeur vie client.** Marge de 6 € par mois et par client actif, taux d'actualisation de 1 % par mois, horizon de 240 mois (hypothèses). La survie du modèle de Weibull est moyennée sur chaque groupe.

```python
m_mensuelle, taux, mois = 6.0, 0.01, np.arange(0, 240)
k_hat = 1 / sigma
lam = np.exp(Xc @ wb["theta"][:-1])                         # échelle e^{x gamma} de chaque client

def S_groupe(masque):
    return np.array([np.mean(np.exp(-(t / lam[masque]) ** k_hat)) for t in mois])

groupes = {"tous": np.ones(len(c), bool), "sans offre": (c["offre_bienvenue"] == 0).to_numpy(), "avec offre": (c["offre_bienvenue"] == 1).to_numpy()}
for nom, masque in groupes.items():
    S_g = S_groupe(masque)
    print(f"{nom:<12} survie à 36 mois = {S_g[36]:.3f} | CLV = {m_mensuelle * np.sum(S_g / (1 + taux) ** mois):.1f} €")
```
<!--sortie-->
```text
tous         survie à 36 mois = 0.453 | CLV = 186.1 €
sans offre   survie à 36 mois = 0.384 | CLV = 165.8 €
avec offre   survie à 36 mois = 0.521 | CLV = 205.8 €
```

**Étape 5 : l'offre est-elle rentable ?** Gain net $=m\sum_t(S_1-S_0)(1+r)^{-t}-\text{coût}$, selon la marge et le taux d'actualisation.

```python
S0, S1 = S_groupe(groupes["sans offre"]), S_groupe(groupes["avec offre"])
cout_offre = 10.0
res = pd.DataFrame({f"marge {m} €": [m * np.sum((S1 - S0) * (1 + r) ** (-mois)) - cout_offre for r in (0.005, 0.01, 0.02)] for m in (3, 6, 9)},
                   index=[f"taux {100 * r:.1f} %/mois" for r in (0.005, 0.01, 0.02)])
print(res.round(1).to_string())
```
<!--sortie-->
```text
                 marge 3 €  marge 6 €  marge 9 €
taux 0.5 %/mois       16.5       42.9       69.4
taux 1.0 %/mois       10.0       30.0       50.0
taux 2.0 %/mois        2.4       14.7       27.1
```

*Lecture.* Le gain net est positif dans les neuf cas, mais son ordre de grandeur varie d'un facteur 30 : la conclusion « l'offre est rentable » est robuste, pas le chiffre.

### Application 5.6 — Risques concurrents

**Objectif.** Estimer les incidences cumulées de deux causes de sortie (départ volontaire, fermeture forcée), voir pourquoi « 1 − Kaplan-Meier » trompe, et comparer modèle par cause et modèle de Fine et Gray (livre, 5.5).

**Étape 1 : dix clients.** Issues : 0 = censuré, 1 = départ volontaire, 2 = fermeture forcée.

```python
t10 = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 12.])
c10 = np.array([1, 2, 1, 0, 2, 1, 0, 1, 2, 0])
tj10, S10, (F1_10, F2_10) = incidence_cumulee(t10, c10)
print(pd.DataFrame({"t_j": tj10, "S": S10, "F1": F1_10, "F2": F2_10, "S+F1+F2": S10 + F1_10 + F2_10}).round(3).to_string(index=False))

tj_n, S_n, (F1_naif,) = incidence_cumulee(t10, np.where(c10 == 1, 1, 0))          # cause 2 traitée comme censure
print(f"1 - KM naïf à t = 9 : {1 - S_n[-1]:.3f} | incidence correcte F1(9) = {F1_10[5]:.3f}")
```
<!--sortie-->
```text
 t_j     S    F1    F2  S+F1+F2
 2.0 0.900 0.100 0.000      1.0
 3.0 0.800 0.100 0.100      1.0
 4.0 0.700 0.200 0.100      1.0
 6.0 0.583 0.200 0.217      1.0
 7.0 0.467 0.317 0.217      1.0
 9.0 0.311 0.472 0.217      1.0
10.0 0.156 0.472 0.372      1.0
1 - KM naïf à t = 9 : 0.580 | incidence correcte F1(9) = 0.472
```

**Étape 2 : une simulation à vérité connue.** 6 000 clients : départ volontaire de loi de Weibull (forme 1,3), allongé par l'offre ; fermeture forcée à taux constant de 0,6 % par mois, multiplié par 2,2 pour le canal Réseaux, sans effet de l'offre ; censure uniforme entre 12 et 72 mois.

```python
rng = np.random.default_rng(55)
n = 6000
offre = rng.integers(0, 2, n)
reseaux = (rng.random(n) < 0.45).astype(int)
T1 = 40 * np.exp(0.40 * offre) * rng.weibull(1.3, n)       # départ volontaire
T2 = rng.exponential(1 / (0.006 * np.exp(0.8 * reseaux)))  # fermeture forcée
C = rng.uniform(12, 72, n)
t_obs = np.minimum.reduce([T1, T2, C])
cause = np.where(C <= np.minimum(T1, T2), 0, np.where(T1 <= T2, 1, 2))
rc = pd.DataFrame({"duree": t_obs, "cause": cause, "offre": offre, "reseaux": reseaux})
rc.to_csv("donnees/ch05-risques-concurrents.csv", index=False)            # relu par R plus bas
print("issues (0 = censuré) :", rc["cause"].value_counts().sort_index().to_dict())
```
<!--sortie-->
```text
issues (0 = censuré) : {0: 2079, 1: 2655, 2: 1266}
```

**Étape 3 : incidences cumulées, estimées de trois façons.**

```python
tj, S, (F1, F2) = incidence_cumulee(rc["duree"], rc["cause"])
tj_1, S_1, (F1_naif,) = incidence_cumulee(rc["duree"], np.where(rc["cause"] == 1, 1, 0))
for t in (12, 24, 36, 48):
    i, i1 = np.searchsorted(tj, t, side="right") - 1, np.searchsorted(tj_1, t, side="right") - 1
    print(f"{t:>3} mois : S = {S[i]:.3f} | F1 = {F1[i]:.3f} | F2 = {F2[i]:.3f} | 1 - KM naïf = {F1_naif[i1]:.3f}")
```
<!--sortie-->
```text
 12 mois : S = 0.762 | F1 = 0.143 | F2 = 0.095 | 1 - KM naïf = 0.151
 24 mois : S = 0.538 | F1 = 0.299 | F2 = 0.163 | 1 - KM naïf = 0.335
 36 mois : S = 0.367 | F1 = 0.422 | F2 = 0.211 | 1 - KM naïf = 0.494
 48 mois : S = 0.251 | F1 = 0.514 | F2 = 0.235 | 1 - KM naïf = 0.627
```

```r
library(cmprsk)
rc <- read.csv("donnees/ch05-risques-concurrents.csv")
ci <- cuminc(rc$duree, rc$cause)
print(round(timepoints(ci, c(12, 24, 36, 48))$est, 4))
```
<!--sortie-->
```text
        12     24     36     48
1 1 0.1428 0.2993 0.4217 0.5141
1 2 0.0948 0.1629 0.2109 0.2350
```

```python
from lifelines import AalenJohansenFitter

aj1 = AalenJohansenFitter(calculate_variance=False, seed=1).fit(rc["duree"], rc["cause"], event_of_interest=1)
print([round(float(aj1.cumulative_density_.loc[:t].iloc[-1, 0]), 4) for t in (12, 24, 36, 48)])
```
<!--sortie-->
```text
[0.1428, 0.2993, 0.4217, 0.5141]
```

**Étape 4 : modèle par cause et modèle de Fine et Gray.**

```python
from statsmodels.duration.hazard_regression import PHReg

for k in (1, 2):
    m = PHReg(rc["duree"], rc[["offre", "reseaux"]], status=(rc["cause"] == k).astype(int), ties="efron").fit()
    print(f"cause {k} : HR propres à la cause", {nom: round(float(v), 3) for nom, v in zip(["offre", "reseaux"], np.exp(m.params))})
```
<!--sortie-->
```text
cause 1 : HR propres à la cause {'offre': 0.584, 'reseaux': 0.974}
cause 2 : HR propres à la cause {'offre': 1.033, 'reseaux': 2.316}
```

```r
cov <- cbind(offre = rc$offre, reseaux = rc$reseaux)
for (k in 1:2) {
  f <- crr(rc$duree, rc$cause, cov, failcode = k, cencode = 0)
  cat("Fine-Gray, cause", k, "\n"); print(round(summary(f)$conf.int[, c(1, 3, 4)], 3))
}
```
<!--sortie-->
```text
Fine-Gray, cause 1 
        exp(coef)  2.5% 97.5%
offre       0.604 0.560 0.652
reseaux     0.792 0.733 0.855
Fine-Gray, cause 2 
        exp(coef)  2.5% 97.5%
offre       1.219 1.091 1.361
reseaux     2.280 2.036 2.554
```

*Lecture.* Dans le modèle par cause, l'offre réduit le risque de départ volontaire (HR ≈ 0,58) et n'a aucun effet sur celui de fermeture ; dans le modèle de Fine et Gray, elle *augmente* pourtant l'incidence de la fermeture forcée (≈ 1,22), par effet de compétition. De même, Réseaux n'a aucun effet direct sur le départ volontaire, mais un rapport de sous-distribution de 0,79 : les clients de ce canal sont plus souvent éliminés avant.

## Exercices

Les exercices sont classés par difficulté : ⭐ (application directe), ⭐⭐ (demande de réfléchir), ⭐⭐⭐ (synthèse). **Cherchez d'abord seul(e)**, à la main quand c'est demandé, avant de lire le corrigé. Les fonctions de `build/outils_ch05.py` (`kaplan_meier`, `logrank`, `cox_ph`, `test_ph`, `ajuster`, `incidence_cumulee`, etc.), importées dans la préparation, sont réutilisées dans les corrigés.

### Exercice 5.1 ⭐ — Censure et Kaplan-Meier à la main (sections 5.1, 5.2 du livre)

La gérante suit six clients : $(4;\text{parti})$, $(7;\text{censuré})$, $(9;\text{parti})$, $(12;\text{parti})$, $(15;\text{censuré})$, $(20;\text{censuré})$ (durées en mois). (a) Calculez la moyenne de toutes les durées, puis celle des seuls clients partis. (b) Calculez la courbe de Kaplan-Meier à la main. (c) Donnez la médiane de survie. (d) Calculez la durée moyenne restreinte jusqu'à 20 mois.

### Exercice 5.2 ⭐ — Relations entre les fonctions (section 5.1 du livre)

Un client a, à l'âge $t$ de la relation (en mois), un risque instantané $h(t)=0{,}0008\,t$. (a) Déduisez $H(t)$ et $S(t)$. (b) Calculez $S(24)$ et la médiane. (c) De quelle loi de Weibull s'agit-il ? Donnez sa durée moyenne.

### Exercice 5.3 ⭐ — Taux constant (section 5.1 du livre)

Sur un échantillon, on observe 40 départs pour un total de 1 600 mois-clients d'exposition. (a) Estimez le taux de départ mensuel $\lambda$ (exponentielle), son écart-type et un intervalle de confiance à 95 %. (b) Estimez $S(24)$ et la durée moyenne. (c) Testez $H_0:\lambda=0{,}03$ par le test de Wald et par le rapport de vraisemblance.

### Exercice 5.4 ⭐⭐ — Greenwood (section 5.2 du livre)

Huit clients : $(2;1)$, $(3;1)$, $(3;1)$, $(5;0)$, $(6;1)$, $(8;0)$, $(9;1)$, $(11;0)$ (durée ; 1 = parti, 0 = censuré). Construisez le tableau de Kaplan-Meier (avec les ex aequo), puis donnez $\hat S(6)$, son erreur standard de Greenwood et son intervalle de confiance log-log à 95 %.

### Exercice 5.5 ⭐⭐ — Log-rank (section 5.2 du livre)

Deux groupes de cinq clients. Groupe A : $(3;1)$, $(6;1)$, $(8;0)$, $(10;1)$, $(12;0)$. Groupe B : $(5;1)$, $(7;1)$, $(9;1)$, $(11;0)$, $(13;0)$. Calculez à la main le test du log-rank (tableau aux instants de départ : ensembles à risque, départs attendus, variances), concluez, puis vérifiez avec `statsmodels`.

### Exercice 5.6 ⭐⭐ — Durée moyenne restreinte (section 5.2 du livre)

Les courbes de survie de deux campagnes sont des escaliers. Campagne A : $S=1$ jusqu'à 6 mois, $0{,}8$ sur $[6,12[$, $0{,}5$ sur $[12,18[$, $0{,}3$ ensuite. Campagne B : $S=1$ jusqu'à 9 mois, $0{,}9$ sur $[9,15[$, $0{,}7$ sur $[15,21[$, $0{,}6$ ensuite. Calculez la durée moyenne restreinte à 24 mois de chaque campagne et leur différence. Que signifie ce nombre ?

### Exercice 5.7 ⭐⭐ — Lire une sortie de Cox (section 5.3 du livre)

Un modèle de Cox donne : offre de bienvenue $\hat\beta=-0{,}40$ (ET $0{,}065$), âge $\hat\beta=-0{,}0136$ (ET $0{,}0030$), canal Réseaux (contre Boutique) $\hat\beta=0{,}635$ (ET $0{,}084$). (a) Donnez pour chaque variable le rapport de risques, son IC95 et le $z$ de Wald. (b) Quel est l'effet de dix années d'âge de plus ? (c) Quel est le rapport de risques d'un client Réseaux *avec* offre contre un client Boutique *sans* offre, à âge égal ? (d) La survie à 24 mois d'un client de référence est de 0,80 : quelle est celle du même client avec l'offre ? (e) Un AFT Weibull donne $\hat\gamma_{\text{offre}}=0{,}35$ avec $\hat\sigma=0{,}74$ : quel rapport de risques équivalent ?

### Exercice 5.8 ⭐⭐ — Le biais d'immortalité (section 5.3 du livre)

Simulez 2 000 clients dont les durées sont exponentielles de taux 2 % par mois (graine 8), censurées uniformément entre 18 et 48 mois. Un cadeau est remis au mois 6 à la moitié des clients encore présents. Estimez l'effet du cadeau (qui n'en a aucun) (a) en traitant « a reçu le cadeau » comme une variable fixe, (b) correctement, avec une variable dépendant du temps. Commentez.

### Exercice 5.9 ⭐⭐ — Estimer la forme de Weibull de deux façons (section 5.4 du livre)

Pour l'ensemble des 2 000 clients (sans covariables), estimez la forme $k$ de la loi de Weibull (a) par le graphique de Weibull : régression de $\ln(-\ln\hat S_{KM})$ sur $\ln t$ entre 6 et 60 mois ; (b) par maximum de vraisemblance. Comparez, et expliquez l'écart avec la valeur $k=1{,}35$ utilisée pour simuler.

### Exercice 5.10 ⭐⭐⭐ — Log-rank et Cox (section 5.3 du livre)

(a) Montrez que le score du modèle de Cox à une variable binaire en $\beta=0$ vaut $O_1-E_1$. (b) Vérifiez numériquement, sur les 2 000 clients (variable `offre_bienvenue`), que la statistique de score $U^2/I$ est très proche du $\chi^2$ du log-rank. Pourquoi n'est-elle pas *exactement* égale ?

### Exercice 5.11 ⭐⭐⭐ — Décider : le seuil de rentabilité (section 5.4 du livre)

Reprenez les survies moyennes avec et sans offre du 5.4.5. L'offre de bienvenue coûte maintenant 25 € par client. À partir de quelle **marge mensuelle** par client actif est-elle rentable, pour un taux d'actualisation de 1 % par mois ? Et pour 2 % ?

### Exercice 5.12 ⭐⭐⭐ — Risques concurrents à la main (section 5.5 du livre)

Huit clients, durées et causes de sortie (0 = censuré, 1 = départ volontaire, 2 = fermeture forcée) : $(1;1)$, $(2;2)$, $(3;1)$, $(4;0)$, $(5;2)$, $(6;1)$, $(7;0)$, $(9;2)$. Calculez à la main les incidences cumulées $\hat F_1$ et $\hat F_2$ (estimateur d'Aalen-Johansen) et la survie totale. Vérifiez que $\hat S+\hat F_1+\hat F_2=1$. Comparez $\hat F_1$ à « $1-\mathrm{KM}$ » où la cause 2 est traitée comme une censure.

### Exercice 5.13 ⭐⭐⭐ — Proportionnalité des risques sur des données réelles (section 5.3 du livre)

Reprenez les données de récidive de Rossi (5.3.9). Appliquez le test de score de proportionnalité des risques du 5.3.5 à chacune des sept covariables. Quelles variables posent problème ? Que feriez-vous ?

## Corrigés

### Corrigé 5.1

(a) Moyenne de toutes les durées : $(4+7+9+12+15+20)/6\approx11{,}17$ mois ; moyenne des seuls clients partis : $(4+9+12)/3\approx8{,}33$ mois. Les deux sont biaisées (5.1.1). (b) Départs aux mois 4, 9 et 12. À 4 mois, 6 clients à risque : $5/6=0{,}833$. À 9 mois (le client censuré à 7 est sorti), 4 clients à risque : $0{,}833\times3/4=0{,}625$. À 12 mois, 3 clients à risque : $0{,}625\times2/3=0{,}417$. (c) La courbe passe sous 0,5 au mois 12 : **médiane = 12 mois**. (d) $\mathrm{RMST}(20)=4\times1+5\times0{,}833+3\times0{,}625+8\times0{,}417=4+4{,}167+1{,}875+3{,}333=13{,}375$ mois.

```python
import numpy as np
import pandas as pd
from scipy import stats

y1 = np.array([4, 7, 9, 12, 15, 20.]); d1 = np.array([1, 0, 1, 1, 0, 0])
tj1, n1, dj1, S1_, gw1 = kaplan_meier(y1, d1)
print("moyenne de toutes les durées :", round(y1.mean(), 2), "| des seuls partis :", round(y1[d1 == 1].mean(), 2))
print("S aux instants de départ", tj1, ":", S1_.round(4), "| à risque :", n1)
print("médiane :", tj1[S1_ <= 0.5][0], "| RMST(20) :", round(rmst(tj1, S1_, 20), 3))
```
<!--sortie-->
```text
moyenne de toutes les durées : 11.17 | des seuls partis : 8.33
S aux instants de départ [ 4.  9. 12.] : [0.8333 0.625  0.4167] | à risque : [6 4 3]
médiane : 12.0 | RMST(20) : 13.375
```

### Corrigé 5.2

(a) $H(t)=\int_0^t0{,}0008u\,du=0{,}0004\,t^2$, donc $S(t)=\exp(-0{,}0004\,t^2)$. (b) $S(24)=\exp(-0{,}0004\times576)=e^{-0{,}2304}\approx0{,}794$ ; la médiane vérifie $0{,}0004\,t^2=\ln2$, donc $t=\sqrt{\ln2/0{,}0004}\approx41{,}6$ mois. (c) Une Weibull a $H(t)=(t/\sigma)^k$ : on lit $k=2$ et $\sigma^{-2}=0{,}0004$, soit $\sigma=50$ mois. La durée moyenne vaut $\sigma\,\Gamma(1+1/k)=50\,\Gamma(1{,}5)\approx44{,}3$ mois.

```python
from math import gamma, log
from scipy.integrate import quad
print("S(24) =", round(np.exp(-0.0004 * 24 ** 2), 4), "| médiane =", round(np.sqrt(log(2) / 0.0004), 2))
print("moyenne par la formule :", round(50 * gamma(1.5), 2), "| par intégration de S :", round(quad(lambda t: np.exp(-0.0004 * t ** 2), 0, np.inf)[0], 2))
```
<!--sortie-->
```text
S(24) = 0.7942 | médiane = 41.63
moyenne par la formule : 44.31 | par intégration de S : 44.31
```

### Corrigé 5.3

(a) $\hat\lambda=D/E=40/1600=0{,}025$ par mois ; $\widehat{se}=\hat\lambda/\sqrt D=0{,}025/\sqrt{40}\approx0{,}00395$ ; IC95 : $0{,}025\pm1{,}96\times0{,}00395$, soit $[0{,}0173\ ;\ 0{,}0327]$. (b) $\hat S(24)=e^{-0{,}025\times24}=e^{-0{,}6}\approx0{,}549$ ; durée moyenne $1/\hat\lambda=40$ mois. (c) Wald : $z=(0{,}025-0{,}03)/0{,}00395\approx-1{,}26$, $p\approx0{,}21$. Rapport de vraisemblance : $2[\ell(\hat\lambda)-\ell(0{,}03)]=2[D\ln(\hat\lambda/0{,}03)-(\hat\lambda-0{,}03)E]=2[40\ln(0{,}8333)+8]\approx1{,}41$, $p\approx0{,}23$. Les deux tests concluent de la même façon : **on ne rejette pas** $\lambda=0{,}03$ (les données sont compatibles aussi avec ce taux).

```python
D, E = 40, 1600
lam = D / E; se = lam / np.sqrt(D)
print(f"lambda = {lam:.4f}, ET = {se:.5f}, IC95 = [{lam - 1.96 * se:.4f} ; {lam + 1.96 * se:.4f}]")
print(f"S(24) = {np.exp(-lam * 24):.4f}, durée moyenne = {1 / lam:.1f} mois")
z = (lam - 0.03) / se
lr = 2 * (D * np.log(lam / 0.03) - (lam - 0.03) * E)
print(f"Wald : z = {z:.3f}, p = {2 * stats.norm.sf(abs(z)):.3f} | rapport de vraisemblance : chi2 = {lr:.3f}, p = {stats.chi2.sf(lr, 1):.3f}")
```
<!--sortie-->
```text
lambda = 0.0250, ET = 0.00395, IC95 = [0.0173 ; 0.0327]
S(24) = 0.5488, durée moyenne = 40.0 mois
Wald : z = -1.265, p = 0.206 | rapport de vraisemblance : chi2 = 1.414, p = 0.234
```

### Corrigé 5.4

Départs : mois 2 (1 départ, 8 à risque : $7/8$), mois 3 (2 départs, 7 à risque : $5/7$), mois 6 (1 départ, 4 à risque, car le client censuré à 5 est sorti : $3/4$), mois 9 (1 départ, 2 à risque : $1/2$). D'où $\hat S(2)=0{,}875$, $\hat S(3)=0{,}875\times5/7=0{,}625$, $\hat S(6)=0{,}625\times3/4=0{,}469$, $\hat S(9)=0{,}234$. Greenwood : $\sum\frac{d_j}{n_j(n_j-d_j)}=\frac1{8\times7}+\frac2{7\times5}+\frac1{4\times3}=0{,}0179+0{,}0571+0{,}0833=0{,}1583$ ; l'erreur standard de $\hat S(6)$ vaut $0{,}469\times\sqrt{0{,}1583}\approx0{,}187$. Intervalle log-log : $\hat S^{\exp(\pm1{,}96\sqrt{G}/|\ln\hat S|)}$ avec $1{,}96\times\sqrt{0{,}1583}/|\ln0{,}469|=0{,}780/0{,}757=1{,}03$, d'où $[0{,}469^{2{,}80}\ ;\ 0{,}469^{1/2{,}80}]\approx[0{,}12\ ;\ 0{,}76]$ : un intervalle immense, faute de données.

```python
y4 = np.array([2, 3, 3, 5, 6, 8, 9, 11.]); d4 = np.array([1, 1, 1, 0, 1, 0, 1, 0])
tj4, n4, dj4, S4, gw4 = kaplan_meier(y4, d4)
print(pd.DataFrame({"t_j": tj4, "à risque": n4, "départs": dj4, "S": S4.round(4), "somme Greenwood": gw4.round(4)}).to_string(index=False))
s, plan, log_, loglog = intervalles(6, tj4, S4, gw4)
print(f"S(6) = {s:.4f} ; ET = {s * np.sqrt(surv_at(6, tj4, gw4)):.4f} ; IC log-log = [{loglog[0]:.3f} ; {loglog[1]:.3f}]")
```
<!--sortie-->
```text
 t_j  à risque  départs      S  somme Greenwood
 2.0         8        1 0.8750           0.0179
 3.0         7        2 0.6250           0.0750
 6.0         4        1 0.4688           0.1583
 9.0         2        1 0.2344           0.6583
S(6) = 0.4688 ; ET = 0.1865 ; IC log-log = [0.120 ; 0.763]
```

### Corrigé 5.5

Aux instants de départ 3, 5, 6, 7, 9 et 10, on a respectivement $n_j=10,9,8,7,5,4$ clients à risque, dont $n_{Aj}=5,4,4,3,2,2$ dans le groupe A. Chaque instant compte un seul départ : $E_{Aj}=n_{Aj}/n_j$ et $V_j=\frac{n_{Aj}}{n_j}(1-\frac{n_{Aj}}{n_j})$. Le code donne le détail :

```python
y5 = np.array([3, 6, 8, 10, 12, 5, 7, 9, 11, 13.]); d5 = np.array([1, 1, 0, 1, 0, 1, 1, 1, 0, 0])
g5 = np.array(["A"] * 5 + ["B"] * 5)
lignes, O1, E1, V1 = [], 0, 0.0, 0.0
for t in np.unique(y5[d5 == 1]):
    n_ = int(np.sum(y5 >= t)); nA = int(np.sum((y5 >= t) & (g5 == "A")))
    dd = int(np.sum((y5 == t) & (d5 == 1))); dA = int(np.sum((y5 == t) & (d5 == 1) & (g5 == "A")))
    e = dd * nA / n_; v = dd * (nA / n_) * (1 - nA / n_) * (n_ - dd) / (n_ - 1)
    lignes.append((t, n_, nA, dd, dA, round(e, 4), round(v, 4))); O1 += dA; E1 += e; V1 += v
print(pd.DataFrame(lignes, columns=["t_j", "n_j", "n_Aj", "d_j", "départ en A", "E_Aj", "V_j"]).to_string(index=False))
chi5 = (O1 - E1) ** 2 / V1
print(f"O_A = {O1}, E_A = {E1:.3f}, V = {V1:.3f}, chi2 = {chi5:.3f}, p = {stats.chi2.sf(chi5, 1):.3f}")
from statsmodels.duration.survfunc import survdiff
print("statsmodels : chi2 = %.3f, p = %.3f" % survdiff(y5, d5, g5))
```
<!--sortie-->
```text
 t_j  n_j  n_Aj  d_j  départ en A   E_Aj    V_j
 3.0   10     5    1            1 0.5000 0.2500
 5.0    9     4    1            0 0.4444 0.2469
 6.0    8     4    1            1 0.5000 0.2500
 7.0    7     3    1            0 0.4286 0.2449
 9.0    5     2    1            0 0.4000 0.2400
10.0    4     2    1            1 0.5000 0.2500
O_A = 3, E_A = 2.773, V = 1.482, chi2 = 0.035, p = 0.852
statsmodels : chi2 = 0.035, p = 0.852
```

Le groupe A a 3 départs pour 2,77 attendus : $\chi^2\approx0{,}03$, $p\approx0{,}85$. Avec dix clients, on ne peut rien conclure ; c'est tout à fait normal, et c'est la raison pour laquelle on ne compare pas des groupes aussi petits.

### Corrigé 5.6

$\mathrm{RMST}_A(24)=6\times1+6\times0{,}8+6\times0{,}5+6\times0{,}3=6+4{,}8+3+1{,}8=15{,}6$ mois ; $\mathrm{RMST}_B(24)=9\times1+6\times0{,}9+6\times0{,}7+3\times0{,}6=9+5{,}4+4{,}2+1{,}8=20{,}4$ mois. La différence est de **4,8 mois** : en moyenne, sur les 24 premiers mois, un client de la campagne B reste 4,8 mois de plus dans la clientèle qu'un client de la campagne A. Contrairement au rapport de risques, cette quantité s'interprète sans hypothèse de proportionnalité et se lit directement en unités de temps (ou, multipliée par la marge mensuelle, en euros).

```python
tjA, SA = np.array([6, 12, 18.]), np.array([0.8, 0.5, 0.3])
tjB, SB = np.array([9, 15, 21.]), np.array([0.9, 0.7, 0.6])
print("RMST(24) A :", round(rmst(tjA, SA, 24), 2), "| B :", round(rmst(tjB, SB, 24), 2), "| différence :", round(rmst(tjB, SB, 24) - rmst(tjA, SA, 24), 2))
```
<!--sortie-->
```text
RMST(24) A : 15.6 | B : 20.4 | différence : 4.8
```

### Corrigé 5.7

(a) $\mathrm{HR}=e^{\hat\beta}$, IC $=e^{\hat\beta\pm1{,}96\,se}$, $z=\hat\beta/se$ : offre $0{,}670$ ($[0{,}590\ ;\ 0{,}761]$, $z=-6{,}15$) ; âge $0{,}986$ ($[0{,}981\ ;\ 0{,}992]$, $z=-4{,}53$) ; Réseaux $1{,}887$ ($[1{,}60\ ;\ 2{,}22]$, $z=7{,}56$). (b) $e^{10\times(-0{,}0136)}\approx0{,}873$ : dix ans de plus réduisent le risque d'environ 13 %. (c) Les effets se multiplient : $e^{-0{,}40+0{,}635}=e^{0{,}235}\approx1{,}26$ (le canal Réseaux l'emporte sur l'offre). (d) $S(t\mid x)=S_0(t)^{\exp(x^\top\beta)}$ : $0{,}80^{0{,}670}\approx0{,}861$. (e) $\hat\beta=-\hat\gamma/\hat\sigma=-0{,}35/0{,}74\approx-0{,}473$, soit $\mathrm{HR}=e^{-0{,}473}\approx0{,}623$.

```python
b = np.array([-0.40, -0.0136, 0.635]); se_ = np.array([0.065, 0.0030, 0.084])
print(pd.DataFrame({"HR": np.exp(b), "IC bas": np.exp(b - 1.96 * se_), "IC haut": np.exp(b + 1.96 * se_), "z": b / se_}, index=["offre", "age", "Réseaux"]).round(3).to_string())
print("+10 ans :", round(np.exp(10 * b[1]), 3), "| Réseaux avec offre / Boutique sans offre :", round(np.exp(b[0] + b[2]), 3))
print("S(24) avec offre :", round(0.80 ** np.exp(b[0]), 3), "| HR depuis AFT :", round(np.exp(-0.35 / 0.74), 3))
```
<!--sortie-->
```text
            HR  IC bas  IC haut      z
offre    0.670   0.590    0.761 -6.154
age      0.986   0.981    0.992 -4.533
Réseaux  1.887   1.601    2.225  7.560
+10 ans : 0.873 | Réseaux avec offre / Boutique sans offre : 1.265
S(24) avec offre : 0.861 | HR depuis AFT : 0.623
```

### Corrigé 5.8

Dans l'analyse (a), le cadeau n'est donné qu'à ceux qui ont **survécu** jusqu'au mois 6 : ils ont une avance garantie, et le modèle y voit un effet protecteur qui n'existe pas. Dans l'analyse (b), le cadeau est une variable qui passe de 0 à 1 au mois 6 (deux épisodes pour les clients concernés), et seuls les clients **présents au mois 6** sont comparés entre eux.

```python
from statsmodels.duration.hazard_regression import PHReg

rng = np.random.default_rng(8)
N = 2000
T = rng.exponential(1 / 0.02, N)
C = rng.uniform(18, 48, N)
Y, D = np.minimum(T, C), (T <= C).astype(int)
cadeau = (Y > 6) & (rng.random(N) < 0.5)
naif = PHReg(Y, cadeau.astype(float)[:, None], status=D, ties="efron").fit()
porteurs = np.where(cadeau)[0]
debut = np.concatenate([np.zeros(N), np.full(len(porteurs), 6.0)])
fin = np.concatenate([np.where(cadeau, 6.0, Y), Y[porteurs]])
statut = np.concatenate([np.where(cadeau, 0, D), D[porteurs]])
x_tv = np.concatenate([np.zeros(N), np.ones(len(porteurs))])
juste = PHReg(fin, x_tv[:, None], status=statut, entry=debut, ties="efron").fit()
for nom, m in (("naïve (variable fixe)", naif), ("correcte (dépend du temps)", juste)):
    print(f"{nom:<28} HR = {np.exp(m.params[0]):.2f}  IC95 [{np.exp(m.params[0] - 1.96 * m.bse[0]):.2f} ; {np.exp(m.params[0] + 1.96 * m.bse[0]):.2f}]")
```
<!--sortie-->
```text
naïve (variable fixe)        HR = 0.64  IC95 [0.56 ; 0.74]
correcte (dépend du temps)   HR = 1.00  IC95 [0.86 ; 1.16]
```

L'analyse naïve conclut à un effet protecteur net (un HR bien inférieur à 1), l'analyse correcte à un effet nul (HR proche de 1, intervalle contenant 1) : c'est le **biais d'immortalité**.

### Corrigé 5.9

(a) Si $S(t)=\exp[-(t/\sigma)^k]$, alors $\ln(-\ln S)=k\ln t-k\ln\sigma$ : la pente de la droite est $k$. (b) Le maximum de vraisemblance sans covariable est l'estimation de $k=1/\hat\sigma$ dans `ajuster` avec une seule colonne de 1.

```python
c = pd.read_csv("donnees/clients.csv")
y, d = c["duree_mois"].to_numpy(), c["churn"].to_numpy()
tj_, _, _, S_, _ = kaplan_meier(y, d)
garde = (tj_ >= 6) & (tj_ <= 60)
pente, ord_, r, _, _ = stats.linregress(np.log(tj_[garde]), np.log(-np.log(S_[garde])))
mv = ajuster("weibull", y, d, np.ones((len(y), 1)))
print(f"forme par le graphique de Weibull : k = {pente:.3f} (r = {r:.3f}) | forme par maximum de vraisemblance : k = {1 / np.exp(mv['theta'][-1]):.3f}")
```
<!--sortie-->
```text
forme par le graphique de Weibull : k = 1.296 (r = 1.000) | forme par maximum de vraisemblance : k = 1.281
```

Les deux méthodes donnent une forme voisine de 1,3 (1,30 et 1,28) et légèrement inférieure à la vraie valeur 1,35. La raison est celle du 5.4.7 : en **ignorant les covariables** (offre, canal, âge, facteur de service non observé), le risque de la population est un mélange de risques individuels, dont la croissance apparente est plus lente. L'ajout des covariables mesurées dans le modèle du 5.4.3 faisait passer la forme à 1,32, et l'ajout du facteur non observé (modèle « oracle » du 5.4.7) à 1,40 : la vraie valeur (1,35) n'est approchée, à l'erreur d'échantillonnage près, que si l'on tient compte de *toutes* les covariables, y compris celles qu'on ne mesure pas. Les deux méthodes d'estimation (graphique, maximum de vraisemblance) s'accordent entre elles ; c'est le *modèle* qui est incomplet, pas la méthode.

### Corrigé 5.10

(a) En $\beta=0$, $e^{\beta x_k}=1$ : la moyenne pondérée de $x$ dans l'ensemble à risque $R_j$ est la proportion $n_{1j}/n_j$ de clients du groupe 1. Le score est $\sum_j\sum_{i\text{ parti en }t_j}\big(x_i-n_{1j}/n_j\big)=\sum_j\big(d_{1j}-d_j\,n_{1j}/n_j\big)=O_1-E_1$. (b) L'information en $\beta=0$ est $\sum_{i}\mathrm{Var}_{R_i}(x)=\sum_i\frac{n_{1}}{n}(1-\frac{n_{1}}{n})$ (somme sur *chaque* départ), alors que le log-rank utilise la variance hypergéométrique, avec le facteur $\frac{n_j-d_j}{n_j-1}$ qui corrige les départs simultanés. Les deux coïncident exactement quand il n'y a **jamais** d'ex aequo.

```python
off = c["offre_bienvenue"].to_numpy().astype(float)
U0, I0 = score_info(0.0, y, d, off)                       # fonction du 5.3.2 : boucle sur chaque départ (ex aequo à la Breslow)
O, E, chi_lr, _, _ = logrank(y, d, off)
print(f"Cox : score U = {U0:.3f}, information I = {I0:.3f}, U²/I = {U0 ** 2 / I0:.3f}")
print(f"log-rank : O1 - E1 = {O[1] - E[1]:.3f}, chi2 = {chi_lr:.3f}")
```
<!--sortie-->
```text
Cox : score U = -92.383, information I = 240.231, U²/I = 35.527
log-rank : O1 - E1 = -92.383, chi2 = 35.535
```

Le score est exactement $O_1-E_1$ (même valeur, signe compris, puisque $x=1$ désigne le groupe avec offre), et les deux statistiques ne diffèrent que de 0,008 sur 35,5 : la différence vient de la correction des ex aequo dans la variance.

### Corrigé 5.11

Le gain actualisé de l'offre vaut $\Delta=\sum_t(S_1(t)-S_0(t))(1+r)^{-t}$ « mois de présence actualisés » ; l'offre est rentable si $m\,\Delta>25$, c'est-à-dire $m>m^\star=25/\Delta$.

```python
Xc = np.column_stack([np.ones(len(c)), pd.get_dummies(c[["offre_bienvenue", "age", "canal_acquisition"]], drop_first=True, dtype=float).to_numpy()])
wb = ajuster("weibull", y, d, Xc)                             # Weibull du livre (5.4.3) : forme k et échelle de chaque client
k_hat, lam_i, mois = 1 / np.exp(wb["theta"][-1]), np.exp(Xc @ wb["theta"][:-1]), np.arange(240)
S_groupe = lambda masque: np.array([np.mean(np.exp(-(t / lam_i[masque]) ** k_hat)) for t in mois])
S0, S1 = S_groupe((c["offre_bienvenue"] == 0).to_numpy()), S_groupe((c["offre_bienvenue"] == 1).to_numpy())
cout = 25.0
for r in (0.01, 0.02):
    v = (1 + r) ** (-mois)
    delta = np.sum((S1 - S0) * v)
    print(f"taux {100 * r:.0f} %/mois : gain en mois de présence actualisés = {delta:.3f} -> marge de rentabilité m* = {cout / delta:.2f} €/mois")
```
<!--sortie-->
```text
taux 1 %/mois : gain en mois de présence actualisés = 6.663 -> marge de rentabilité m* = 3.75 €/mois
taux 2 %/mois : gain en mois de présence actualisés = 4.124 -> marge de rentabilité m* = 6.06 €/mois
```

Avec une actualisation de 1 % par mois, l'offre devient rentable dès que la marge mensuelle par client actif dépasse environ **3,75 €** ; avec 2 %, il faut environ **6 €**. L'offre est donc beaucoup moins coûteuse à justifier si la marge est élevée : c'est la lecture pratique du tableau de sensibilité du 5.4.5.

### Corrigé 5.12

Instants de sortie : 1, 2, 3, 5, 6, 9 (les censures aux mois 4 et 7 réduisent seulement les ensembles à risque). Aux mois 1 ($n=8$) : $d_1=1$ ; 2 ($n=7$) : $d_2=1$ ; 3 ($n=6$) : $d_1=1$ ; 5 ($n=4$) : $d_2=1$ ; 6 ($n=3$) : $d_1=1$ ; 9 ($n=1$) : $d_2=1$. On applique $\hat F_k(t)=\sum\hat S(t_j^-)\,d_{kj}/n_j$.

```python
y12 = np.array([1, 2, 3, 4, 5, 6, 7, 9.]); c12 = np.array([1, 2, 1, 0, 2, 1, 0, 2])
tj12, S12, (F1_12, F2_12) = incidence_cumulee(y12, c12)
print(pd.DataFrame({"t_j": tj12, "S": S12, "F1": F1_12, "F2": F2_12, "S + F1 + F2": S12 + F1_12 + F2_12}).round(4).to_string(index=False))
tj_n12, S_n12, (F1_naif12,) = incidence_cumulee(y12, np.where(c12 == 1, 1, 0))
print("1 - KM (cause 2 traitée comme censure), aux instants de la cause 1 :", (1 - S_n12).round(4), "| F1 correcte au dernier instant de cause 1 :", round(F1_12[-2], 4))
```
<!--sortie-->
```text
 t_j      S     F1     F2  S + F1 + F2
 1.0 0.8750 0.1250 0.0000          1.0
 2.0 0.7500 0.1250 0.1250          1.0
 3.0 0.6250 0.2500 0.1250          1.0
 5.0 0.4688 0.2500 0.2812          1.0
 6.0 0.3125 0.4062 0.2812          1.0
 9.0 0.0000 0.4062 0.5938          1.0
1 - KM (cause 2 traitée comme censure), aux instants de la cause 1 : [0.125  0.2708 0.5139] | F1 correcte au dernier instant de cause 1 : 0.4062
```

La somme $\hat S+\hat F_1+\hat F_2$ vaut 1 à chaque instant. À 6 mois, la probabilité de départ volontaire est $\hat F_1(6)=0{,}406$ ; en traitant la cause 2 comme une censure, on obtiendrait « $1-\mathrm{KM}$ » $=0{,}514$, soit 11 points de trop : la compétition des fermetures forcées (aux mois 2, 5 et 9) est ignorée.

### Corrigé 5.13

On applique `test_ph` à l'ajustement de Cox des données de Rossi (la fonction `cox_ph` du 5.3.3 accepte n'importe quelle matrice de covariables).

```python
from lifelines.datasets import load_rossi

rossi = load_rossi()
Xr = rossi.drop(columns=["week", "arrest"])
fit_r = cox_ph(rossi["week"].to_numpy(), rossi["arrest"].to_numpy(), Xr.to_numpy())
chi_r, chi_glob_r = test_ph(rossi["week"].to_numpy(), rossi["arrest"].to_numpy(), Xr.to_numpy(), fit_r)
out = pd.DataFrame({"HR (Breslow)": np.exp(fit_r["beta"]), "chi2 PH": chi_r, "p": stats.chi2.sf(chi_r, 1)}, index=Xr.columns)
print(out.round(3).to_string())
print(f"test global : chi2 = {chi_glob_r:.2f} (7 ddl), p = {stats.chi2.sf(chi_glob_r, 7):.3f}")
```
<!--sortie-->
```text
      HR (Breslow)  chi2 PH      p
fin          0.685    1.371  0.242
age          0.944    0.893  0.345
race         1.369    2.245  0.134
wexp         0.860    4.128  0.042
mar          0.649    0.089  0.765
paro         0.919    0.021  0.886
prio         1.095    1.618  0.203
test global : chi2 = 10.93 (7 ddl), p = 0.142
```

La proportionnalité est plausible pour six des sept covariables. Seule l'expérience professionnelle (`wexp`) a une p-valeur inférieure à 0,05 ($p=0{,}042$), et le test **global** ne rejette rien ($p=0{,}14$). Avec sept tests, obtenir une p-valeur à 0,04 arrive souvent par hasard (volume I, section 3.5.5) : ce n'est pas une preuve de violation. La démarche prudente : tracer le graphique log-log de `wexp`, et si un doute subsiste, **stratifier** sur cette variable (elle est binaire) ou ajouter un effet qui dépend du temps, puis voir si les autres coefficients, en particulier celui de l'aide financière, bougent. S'ils ne bougent pas, la conclusion principale est robuste.

---
