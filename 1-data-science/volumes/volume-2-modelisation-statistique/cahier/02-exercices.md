# Chapitre 2 : Modèles linéaires généralisés — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 2 du livre. Les **applications** reprennent, pas à pas, les calculs que le livre n'a fait que résumer (l'algorithme IRLS écrit à la main, les vérifications numériques, les évaluations de modèles) ; les **exercices** sont corrigés à la fin. Les données sont celles du livre : `donnees/clients.csv` (2 000 clients), `donnees/enquete_satisfaction.csv` (notes de 1 à 5) et `donnees/ch02-sessions.csv` (1 500 sessions de navigation, simulées). Toutes les cellules de ce chapitre s'exécutent **dans l'ordre**, en partageant leurs variables.

## Préparation

Une seule cellule charge les bibliothèques et les trois fichiers ; les applications qui suivent s'en servent.


```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import expit

clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])  # référence : Boutique
enquete = pd.read_csv("donnees/enquete_satisfaction.csv")
enquete["note_produits"] = enquete[["q1", "q2", "q3", "q4"]].mean(axis=1)
enquete["note_service"] = enquete[["q5", "q6", "q7", "q8"]].mean(axis=1)
repondants = clients.merge(enquete[["id_client", "note_produits", "note_service"]], on="id_client")
sessions = pd.read_csv("donnees/ch02-sessions.csv")
print(len(clients), "clients,", len(repondants), "répondants à l'enquête,", len(sessions), "sessions")
```
<!--sortie-->
```text
2000 clients, 1212 répondants à l'enquête, 1500 sessions
```

## Applications

### Application 2.1 — L'algorithme IRLS écrit à la main

*Sections du livre : 2.1.5 et 2.2.5.* **Objectif** : programmer les moindres carrés repondérés itérés, vérifier qu'ils redonnent la solution connue sur un tout petit exemple, puis qu'ils reproduisent `statsmodels` sur le modèle de rachat.

**Étape 0 — Les quatre lignes du tableau de 2.1.3.** Pour chaque loi, $b'(\theta)$ et $\phi\,b''(\theta)$ (dérivées numériques de $b$) doivent coïncider avec la moyenne et la variance d'un grand échantillon simulé.

```python
rng = np.random.default_rng(21)

def d1(f, x):
    h = 1e-4 * abs(x)          # pas relatif : theta varie de 1/60 à 5 selon les lois
    return (f(x + h) - f(x - h)) / (2 * h)

def d2(f, x):
    h = 1e-4 * abs(x)
    return (f(x + h) - 2 * f(x) + f(x - h)) / h**2

N = 400_000
cas = [
    # nom, theta, b, phi, échantillon simulé
    ("Normale(5 ; sigma²=4)", 5.0, lambda t: t**2 / 2, 4.0, rng.normal(5, 2, N)),
    ("Bernoulli(0,3)", np.log(0.3 / 0.7), lambda t: np.log1p(np.exp(t)), 1.0, rng.binomial(1, 0.3, N)),
    ("Poisson(3)", np.log(3.0), lambda t: np.exp(t), 1.0, rng.poisson(3, N)),
    ("Gamma(moyenne 60 ; forme 4)", -1 / 60, lambda t: -np.log(-t), 1 / 4, rng.gamma(4, 60 / 4, N)),
]
lignes = []
for nom, theta, b, phi, echantillon in cas:
    lignes.append({"loi": nom, "b'(theta)": d1(b, theta), "phi * b''(theta)": phi * d2(b, theta),
                   "moyenne simulée": echantillon.mean(), "variance simulée": echantillon.var()})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
                        loi  b'(theta)  phi * b''(theta)  moyenne simulée  variance simulée
      Normale(5 ; sigma²=4)        5.0              4.00            4.998             4.005
             Bernoulli(0,3)        0.3              0.21            0.300             0.210
                 Poisson(3)        3.0              3.00            3.002             2.991
Gamma(moyenne 60 ; forme 4)       60.0            900.00           60.024           900.824
```

**Étape 1 — Quatre clients, un paramètre.** Quatre clients, dont trois ont racheté : $y=(1,0,1,1)$, modèle logistique sans variable. La solution exacte est $\hat\beta=\log3\approx1{,}0986$. À chaque itération, on calcule $\mu$, le poids $W=\mu(1-\mu)$, la réponse de travail $z=\eta+(y-\mu)/W$, puis la moyenne pondérée de $z$.

```python
y = np.array([1, 0, 1, 1])
beta = 0.0
for it in range(1, 6):
    eta = beta                      # modèle sans variable : eta = beta pour tous
    mu = 1 / (1 + np.exp(-eta))
    w = np.full(len(y), mu * (1 - mu))   # un poids par client : (dmu/deta)² / V(mu) = mu(1-mu)
    z = eta + (y - mu) / w          # réponse de travail
    beta = np.sum(w * z) / np.sum(w)
    print(f"itération {it} : mu = {mu:.4f}   W = {w[0]:.4f}   beta = {beta:.6f}")
print("valeur exacte   : log(3) =", round(np.log(3), 6))
```
<!--sortie-->
```text
itération 1 : mu = 0.5000   W = 0.2500   beta = 1.000000
itération 2 : mu = 0.7311   W = 0.1966   beta = 1.096339
itération 3 : mu = 0.7496   W = 0.1877   beta = 1.098611
itération 4 : mu = 0.7500   W = 0.1875   beta = 1.098612
itération 5 : mu = 0.7500   W = 0.1875   beta = 1.098612
valeur exacte   : log(3) = 1.098612
```

Les deux premières valeurs doivent être celles du calcul à la main du livre (1,000 puis 1,0963). Observez le nombre de décimales exactes à chaque pas.

**Étape 2 — L'algorithme en général.** On décrit une famille par son lien, son lien inverse, la dérivée $d\mu/d\eta$ et sa fonction de variance. La première cellule définit les familles, la seconde la fonction `irls`.

```python
from scipy.special import expit

FAMILLES = {
    # lien, lien inverse, dmu/deta (en fonction de eta), fonction de variance V(mu), valeur initiale de mu
    "binomial": dict(lien=lambda m: np.log(m / (1 - m)), inverse=expit,
                     dmu_deta=lambda e: expit(e) * (1 - expit(e)), variance=lambda m: m * (1 - m),
                     init=lambda y: (y + 0.5) / 2),
    "poisson": dict(lien=np.log, inverse=np.exp, dmu_deta=np.exp, variance=lambda m: m,
                    init=lambda y: y + 0.5),
    "gamma_log": dict(lien=np.log, inverse=np.exp, dmu_deta=np.exp, variance=lambda m: m**2,
                      init=lambda y: y),
}
```
```python
def irls(X, y, famille, tol=1e-10, max_iter=50):
    """Moindres carrés repondérés itérés. Renvoie les coefficients, leur matrice de covariance (phi = 1) et le détail."""
    f = FAMILLES[famille]
    mu = f["init"](y)
    eta = f["lien"](mu)
    for it in range(1, max_iter + 1):
        w = f["dmu_deta"](eta) ** 2 / f["variance"](mu)          # poids W_i
        z = eta + (y - mu) / f["dmu_deta"](eta)                  # réponse de travail z_i
        XtW = X.T * w
        beta = np.linalg.solve(XtW @ X, XtW @ z)                 # régression pondérée de z sur X
        nouveau_eta = X @ beta
        converge = np.max(np.abs(nouveau_eta - eta)) < tol
        eta, mu = nouveau_eta, f["inverse"](nouveau_eta)
        if converge:
            break
    w = f["dmu_deta"](eta) ** 2 / f["variance"](mu)
    cov = np.linalg.inv((X.T * w) @ X)                           # (X'WX)^-1 : covariance si phi = 1
    return dict(beta=beta, cov=cov, mu=mu, eta=eta, w=w, iterations=it)
```

**Étape 3 — Deux tests.** (1) Les quatre clients : IRLS doit retrouver $\log 3$. (2) Poisson sans variable sur les 2 000 clients : la solution doit être $\log\bar y$.

```python
# Test 1 : l'exemple à quatre clients
un = np.ones((4, 1))
r = irls(un, y.astype(float), "binomial")
print("logistique, 4 clients : beta =", r["beta"].round(6), "en", r["iterations"], "itérations")

# Test 2 : Poisson sans variable sur les vraies données : la solution doit être log(moyenne)
nb = clients["nb_commandes_an"].to_numpy(dtype=float)
r = irls(np.ones((len(nb), 1)), nb, "poisson")
print("Poisson, 2000 clients : beta =", r["beta"].round(6), "| log(moyenne) =", round(float(np.log(nb.mean())), 6), "| itérations :", r["iterations"])
```
<!--sortie-->
```text
logistique, 4 clients : beta = [1.098612] en 5 itérations
Poisson, 2000 clients : beta = [1.356608] | log(moyenne) = 1.356608 | itérations : 6
```

**Étape 4 — Comparaison avec `statsmodels` sur le modèle de rachat.** On construit la matrice $X$ avec `patsy`, comme le fait `statsmodels`, puis on compare coefficients et erreurs-types.

```python
from patsy import dmatrices

formule = "rachat_12m ~ offre_bienvenue + age + canal"
modele = smf.glm(formule, clients, family=sm.families.Binomial()).fit()
Y, X = dmatrices(formule, clients, return_type="dataframe")
r = irls(X.to_numpy(), Y.to_numpy().ravel(), "binomial")
comparaison = pd.DataFrame({
    "coef (IRLS main)": r["beta"], "coef (statsmodels)": modele.params.to_numpy(),
    "se (IRLS main)": np.sqrt(np.diag(r["cov"])), "se (statsmodels)": modele.bse.to_numpy(),
}, index=X.columns)
print(comparaison.round(6).to_string())
print("itérations :", r["iterations"], "| écart maximal sur les coefficients :", f"{np.max(np.abs(r['beta'] - modele.params.to_numpy())):.2e}")
```
<!--sortie-->
```text
                  coef (IRLS main)  coef (statsmodels)  se (IRLS main)  se (statsmodels)
Intercept                 0.588499            0.588499        0.185372          0.185372
canal[T.Réseaux]         -0.462955           -0.462955        0.115509          0.115509
canal[T.Site]            -0.167719           -0.167719        0.119619          0.119619
offre_bienvenue           0.493258            0.493258        0.090953          0.090953
age                      -0.015498           -0.015498        0.004351          0.004351
itérations : 5 | écart maximal sur les coefficients : 3.13e-14
```

**Étape 5 — Une propriété du lien canonique.** Pour la régression logistique, $\sum_i(y_i-\hat p_i)\,x_{ij}=0$ pour chaque colonne $x_j$, constante comprise. Vérifiez-le, puis expliquez pourquoi la somme des probabilités prédites égale le nombre de « oui ».

```python
residus = clients["rachat_12m"] - modele.fittedvalues
print("somme des résidus (y - p̂)                :", round(float(residus.sum()), 8))
print("somme des p̂ =", round(float(modele.fittedvalues.sum()), 3), "| nombre de 1 observés =", int(clients["rachat_12m"].sum()))
for col in ["offre_bienvenue", "age"]:
    print(f"somme des résidus × {col:16s}:", round(float((residus * clients[col]).sum()), 6))
```
<!--sortie-->
```text
somme des résidus (y - p̂)                : 0.0
somme des p̂ = 1019.0 | nombre de 1 observés = 1019
somme des résidus × offre_bienvenue : 0.0
somme des résidus × age             : 0.0
```

### Application 2.2 — L'offre de bienvenue : du tableau croisé aux effets marginaux

*Sections du livre : 2.2.1 à 2.2.7.* **Objectif** : refaire, pas à pas, l'étude du rachat : cotes, rapport de cotes, modèle complet, probabilités prédites, effets marginaux, puis les notes de l'enquête.

**Étape 1 — Probabilité, cote, logit, et effet d'un coefficient sur la probabilité.** Calculez le tableau (probabilité, cote, logit) pour quelques valeurs, puis montrez qu'un même effet de $+0{,}5$ sur le logit ne produit pas le même gain en points de pourcentage selon le point de départ.

```python
p = np.array([0.05, 0.10, 0.25, 0.50, 0.60, 0.75, 0.90, 0.95])
print(pd.DataFrame({"probabilité p": p, "cote p/(1-p)": p / (1 - p), "logit": np.log(p / (1 - p))}).round(3).to_string(index=False))
```
<!--sortie-->
```text
 probabilité p  cote p/(1-p)  logit
          0.05         0.053 -2.944
          0.10         0.111 -2.197
          0.25         0.333 -1.099
          0.50         1.000  0.000
          0.60         1.500  0.405
          0.75         3.000  1.099
          0.90         9.000  2.197
          0.95        19.000  2.944
```
```python
beta = 0.5                     # un effet de +0,5 sur le logit : OR = exp(0,5) ≈ 1,65
p0 = np.array([0.02, 0.10, 0.30, 0.50, 0.70, 0.90, 0.98])
p1 = expit(np.log(p0 / (1 - p0)) + beta)
print("OR =", round(float(np.exp(beta)), 3))
print(pd.DataFrame({"p avant": p0, "p après": p1, "gain (points)": 100 * (p1 - p0)}).round(3).to_string(index=False))
```
<!--sortie-->
```text
OR = 1.649
 p avant  p après  gain (points)
    0.02    0.033          1.255
    0.10    0.155          5.483
    0.30    0.414         11.404
    0.50    0.622         12.246
    0.70    0.794          9.369
    0.90    0.937          3.686
    0.98    0.988          0.777
```

**Étape 2 — Un seul prédicteur binaire.** Avant d'ajuster, tout se calcule à la main à partir du tableau croisé. Vérifiez que le coefficient de l'offre est exactement le logarithme du rapport de cotes (modèle saturé).

```python
croise = pd.crosstab(clients["offre_bienvenue"], clients["rachat_12m"])
print(croise)
sans, avec = croise.loc[0], croise.loc[1]
p_sans, p_avec = sans[1] / sans.sum(), avec[1] / avec.sum()
cote_sans, cote_avec = sans[1] / sans[0], avec[1] / avec[0]
print()
print(f"sans offre : {p_sans:.4f} ont racheté | cote = {cote_sans:.4f} | logit = {np.log(cote_sans):.4f}")
print(f"avec offre : {p_avec:.4f} ont racheté | cote = {cote_avec:.4f} | logit = {np.log(cote_avec):.4f}")
print(f"rapport de cotes (a*d)/(b*c) = {cote_avec / cote_sans:.4f} | log = {np.log(cote_avec / cote_sans):.4f}")
print(f"différence de risque = {p_avec - p_sans:.4f} | risque relatif = {p_avec / p_sans:.4f}")

m_offre = smf.glm("rachat_12m ~ offre_bienvenue", clients, family=sm.families.Binomial()).fit()
print()
print(m_offre.params.round(4).to_string())
print("exp(coefficient de l'offre) =", round(float(np.exp(m_offre.params["offre_bienvenue"])), 4))
```
<!--sortie-->
```text
rachat_12m         0    1
offre_bienvenue          
0                544  441
1                437  578

sans offre : 0.4477 ont racheté | cote = 0.8107 | logit = -0.2099
avec offre : 0.5695 ont racheté | cote = 1.3227 | logit = 0.2796
rapport de cotes (a*d)/(b*c) = 1.6316 | log = 0.4895
différence de risque = 0.1217 | risque relatif = 1.2719

Intercept         -0.2099
offre_bienvenue    0.4895
exp(coefficient de l'offre) = 1.6316
```

**Étape 3 — Le modèle complet et ses rapports de cotes.**

```python
modele = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
print(modele.summary().tables[1])
print()
print("log-vraisemblance :", round(modele.llf, 2), "| déviance :", round(modele.deviance, 2), "| AIC :", round(modele.aic, 2), "| n =", int(modele.nobs))
```
<!--sortie-->
```text
====================================================================================
                       coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------------
Intercept            0.5885      0.185      3.175      0.001       0.225       0.952
canal[T.Réseaux]    -0.4630      0.116     -4.008      0.000      -0.689      -0.237
canal[T.Site]       -0.1677      0.120     -1.402      0.161      -0.402       0.067
offre_bienvenue      0.4933      0.091      5.423      0.000       0.315       0.672
age                 -0.0155      0.004     -3.562      0.000      -0.024      -0.007
====================================================================================

log-vraisemblance : -1355.42 | déviance : 2710.83 | AIC : 2720.83 | n = 2000
```
```python
ic = modele.conf_int()
rapports = pd.DataFrame({"OR": np.exp(modele.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1]), "p-valeur": modele.pvalues})
print(rapports.round(3).to_string())
print()
print("OR pour +10 ans d'âge :", round(float(np.exp(10 * modele.params["age"])), 3))
```
<!--sortie-->
```text
                     OR  IC95 bas  IC95 haut  p-valeur
Intercept         1.801     1.253      2.590     0.001
canal[T.Réseaux]  0.629     0.502      0.789     0.000
canal[T.Site]     0.846     0.669      1.069     0.161
offre_bienvenue   1.638     1.370      1.957     0.000
age               0.985     0.976      0.993     0.000

OR pour +10 ans d'âge : 0.856
```

**Étape 4 — Probabilités prédites pour un profil, et effets marginaux moyens.** Prédisez, pour un client de 36 ans venu des réseaux, la probabilité de rachat avec et sans l'offre (puis vérifiez votre calcul avec `expit`). Calculez ensuite l'effet marginal moyen de l'offre et de l'âge, et comparez avec `get_margeff`.

```python
profil = pd.DataFrame({"offre_bienvenue": [0, 1], "age": [36, 36],
                       "canal": pd.Categorical(["Réseaux", "Réseaux"], categories=["Boutique", "Réseaux", "Site"])})
p_profil = modele.predict(profil)
b = modele.params
a_la_main = expit(b["Intercept"] + b["canal[T.Réseaux]"] + 36 * b["age"] + b["offre_bienvenue"] * np.array([0, 1]))
print("probabilités prédites (sans offre, avec offre) :", p_profil.round(4).to_numpy(), "| à la main :", a_la_main.round(4))
print("gain en points de pourcentage pour ce profil   :", round(100 * float(p_profil.iloc[1] - p_profil.iloc[0]), 2))
```
<!--sortie-->
```text
probabilités prédites (sans offre, avec offre) : [0.3936 0.5152] | à la main : [0.3936 0.5152]
gain en points de pourcentage pour ce profil   : 12.17
```
```python
avec_offre = clients.assign(offre_bienvenue=1)
sans_offre = clients.assign(offre_bienvenue=0)
effet_moyen = (modele.predict(avec_offre) - modele.predict(sans_offre)).mean()
print(f"effet marginal moyen de l'offre (modèle) : {100 * effet_moyen:.2f} points")
print(f"différence brute des taux de rachat      : {100 * (p_avec - p_sans):.2f} points")

# effet marginal moyen de l'âge : +1 an
effet_age = (modele.predict(clients.assign(age=clients["age"] + 1)) - modele.predict(clients)).mean()
print(f"effet marginal moyen d'un an de plus     : {100 * effet_age:.3f} point  (soit {100 * 10 * effet_age:.2f} points pour 10 ans)")

# contrôle avec la fonction de statsmodels (modèle Logit)
logit = smf.logit("rachat_12m ~ offre_bienvenue + age + canal", clients).fit(disp=0)
print()
print(logit.get_margeff(at="overall", dummy=True).summary_frame().round(4).to_string())
```
<!--sortie-->
```text
effet marginal moyen de l'offre (modèle) : 12.07 points
différence brute des taux de rachat      : 12.17 points
effet marginal moyen d'un an de plus     : -0.376 point  (soit -3.76 points pour 10 ans)

                   dy/dx  Std. Err.       z  Pr(>|z|)  Conf. Int. Low  Cont. Int. Hi.
canal[T.Réseaux] -0.1126     0.0277 -4.0625    0.0000         -0.1669         -0.0583
canal[T.Site]    -0.0405     0.0287 -1.4108    0.1583         -0.0967          0.0158
offre_bienvenue   0.1207     0.0220  5.4768    0.0000          0.0775          0.1640
age              -0.0038     0.0010 -3.6063    0.0003         -0.0058         -0.0017
```

**Étape 5 — Ajouter les notes de l'enquête (sur les répondants seulement).** Comparez le modèle de base et le modèle enrichi (AIC, rapports de cotes). Le rapport de cotes de l'offre change entre les deux, alors qu'elle est tirée au hasard : c'est la **non-collapsibilité**.

```python
m_base = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", repondants, family=sm.families.Binomial()).fit()
m_riche = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + note_produits + note_service", repondants,
                  family=sm.families.Binomial()).fit()
ic = m_riche.conf_int()
print(pd.DataFrame({"coef": m_riche.params, "OR": np.exp(m_riche.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1]),
                    "p": m_riche.pvalues}).round(3).to_string())
print()
print("répondants :", int(m_riche.nobs), "| AIC modèle de base :", round(m_base.aic, 1), "| AIC modèle avec notes :", round(m_riche.aic, 1))
print("écart-types des notes :", repondants[["note_produits", "note_service"]].std().round(2).to_dict())
print("OR de l'offre, sur ces mêmes répondants : sans les notes =", round(float(np.exp(m_base.params["offre_bienvenue"])), 3), "| avec les notes =", round(float(np.exp(m_riche.params["offre_bienvenue"])), 3))
```
<!--sortie-->
```text
                   coef     OR  IC95 bas  IC95 haut      p
Intercept        -3.626  0.027     0.010      0.069  0.000
canal[T.Réseaux] -0.474  0.622     0.458      0.845  0.002
canal[T.Site]    -0.244  0.783     0.570      1.075  0.131
offre_bienvenue   0.607  1.834     1.442      2.334  0.000
age              -0.018  0.983     0.971      0.994  0.003
note_produits     0.764  2.148     1.781      2.589  0.000
note_service      0.420  1.522     1.285      1.803  0.000

répondants : 1212 | AIC modèle de base : 1652.3 | AIC modèle avec notes : 1545.2
écart-types des notes : {'note_produits': 0.69, 'note_service': 0.73}
OR de l'offre, sur ces mêmes répondants : sans les notes = 1.749 | avec les notes = 1.834
```

### Application 2.3 — Évaluer un modèle de classement

*Sections du livre : 2.2.8 et 2.2.9.* **Objectif** : matrice de confusion, courbe ROC et AUC calculées de trois façons, calibration, évaluation hors échantillon, et un cas de séparation parfaite.

**Étape 1 — Matrice de confusion à plusieurs seuils.**

```python
y = repondants["rachat_12m"].to_numpy()
score = m_riche.fittedvalues.to_numpy()

def matrice(y, score, seuil):
    pred = (score >= seuil).astype(int)
    vp, fp = int(((pred == 1) & (y == 1)).sum()), int(((pred == 1) & (y == 0)).sum())
    fn, vn = int(((pred == 0) & (y == 1)).sum()), int(((pred == 0) & (y == 0)).sum())
    return vp, fp, fn, vn

for seuil in (0.5, 0.4, 0.6):
    vp, fp, fn, vn = matrice(y, score, seuil)
    print(f"seuil {seuil} : VP={vp} FP={fp} FN={fn} VN={vn} | exactitude={(vp + vn) / len(y):.3f} | "
          f"sensibilité={vp / (vp + fn):.3f} | spécificité={vn / (vn + fp):.3f} | précision={vp / (vp + fp):.3f}")
```
<!--sortie-->
```text
seuil 0.5 : VP=406 FP=228 FN=206 VN=372 | exactitude=0.642 | sensibilité=0.663 | spécificité=0.620 | précision=0.640
seuil 0.4 : VP=512 FP=353 FN=100 VN=247 | exactitude=0.626 | sensibilité=0.837 | spécificité=0.412 | précision=0.592
seuil 0.6 : VP=270 FP=112 FN=342 VN=488 | exactitude=0.625 | sensibilité=0.441 | spécificité=0.813 | précision=0.707
```

**Étape 2 — L'AUC de trois façons** (comparaison de paires, aire sous la courbe ROC, scikit-learn) : les trois valeurs doivent coïncider.

```python
from sklearn.metrics import roc_auc_score

def auc_paires(y, s):
    pos, neg = s[y == 1], s[y == 0]
    return (pos[:, None] > neg[None, :]).mean() + 0.5 * (pos[:, None] == neg[None, :]).mean()

# courbe ROC « à la main » : on trie les clients par score décroissant et on cumule
ordre = np.argsort(-score)
y_trie = y[ordre]
tpr = np.concatenate([[0], np.cumsum(y_trie) / y.sum()])
fpr = np.concatenate([[0], np.cumsum(1 - y_trie) / (1 - y).sum()])
auc_trapezes = np.trapezoid(tpr, fpr)

print("AUC par comparaison de paires :", round(float(auc_paires(y, score)), 4))
print("AUC par aire sous la courbe   :", round(float(auc_trapezes), 4))
print("AUC de scikit-learn           :", round(float(roc_auc_score(y, score)), 4))
print("AUC du modèle de base (sans les notes) :", round(float(roc_auc_score(y, m_base.fittedvalues)), 4))
```
<!--sortie-->
```text
AUC par comparaison de paires : 0.6975
AUC par aire sous la courbe   : 0.6975
AUC de scikit-learn           : 0.6975
AUC du modèle de base (sans les notes) : 0.599
```

**Étape 3 — Calibration** : regroupez les répondants par dixième de score et comparez la probabilité prédite à la fréquence observée. Le tracé de la courbe ROC et de la calibration (figure du livre) est produit par la cellule masquée qui suit.

```python
dec = pd.qcut(score, 10, labels=False)
calib = pd.DataFrame({"p prédite": score, "observé": y, "dixième": dec}).groupby("dixième").agg(
    p_predite=("p prédite", "mean"), observe=("observé", "mean"), n=("observé", "size"))
print(calib.round(3).to_string())
```
<!--sortie-->
```text
         p_predite  observe    n
dixième                         
0            0.212    0.287  122
1            0.308    0.207  121
2            0.377    0.397  121
3            0.433    0.421  121
4            0.485    0.537  121
5            0.537    0.479  121
6            0.582    0.595  121
7            0.635    0.628  121
8            0.698    0.661  121
9            0.783    0.836  122
```
```python hide
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ax = axes[0]
ordre_b = np.argsort(-m_base.fittedvalues.to_numpy())
yb = y[ordre_b]
tpr_b = np.concatenate([[0], np.cumsum(yb) / y.sum()]); fpr_b = np.concatenate([[0], np.cumsum(1 - yb) / (1 - y).sum()])
ax.plot(fpr, tpr, color=BLEU, lw=2); ax.plot(fpr_b, tpr_b, color=ORANGE, lw=2); ax.plot([0, 1], [0, 1], color="#898781", ls=":")
ax.text(0.45, 0.30, f"avec les notes : AUC = {roc_auc_score(y, score):.2f}", color=BLEU, fontsize=9)
ax.text(0.45, 0.22, f"sans les notes : AUC = {roc_auc_score(y, m_base.fittedvalues):.2f}", color=ORANGE, fontsize=9)
ax.text(0.45, 0.14, "hasard : AUC = 0,50", color="#898781", fontsize=9)
ax.set_xlabel("taux de faux positifs (1 - spécificité)"); ax.set_ylabel("taux de vrais positifs (sensibilité)"); ax.set_title("Courbe ROC")
ax = axes[1]
ax.plot([0, 1], [0, 1], color="#898781", ls=":")
ax.plot(calib["p_predite"], calib["observe"], "o-", color=AQUA, lw=1.8)
ax.set_xlabel("probabilité prédite (moyenne par dixième)"); ax.set_ylabel("fréquence observée de rachat"); ax.set_title("Calibration")
plt.tight_layout()
plt.savefig("figures/ch02-roc-calibration.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

**Étape 4 — Évaluer hors échantillon** : découpez 70 % / 30 %, ajustez sur la première part, évaluez sur la seconde. Répétez avec d'autres graines : l'AUC en test varie-t-elle plus que l'écart avec l'apprentissage ?

```python
rng = np.random.default_rng(5)
idx = rng.permutation(len(repondants))
n_app = int(0.7 * len(repondants))
app, test = repondants.iloc[idx[:n_app]], repondants.iloc[idx[n_app:]]
m_app = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + note_produits + note_service", app, family=sm.families.Binomial()).fit()
print("AUC en apprentissage :", round(float(roc_auc_score(app["rachat_12m"], m_app.fittedvalues)), 4), "(", len(app), "clients )")
print("AUC en test          :", round(float(roc_auc_score(test["rachat_12m"], m_app.predict(test))), 4), "(", len(test), "clients )")
```
<!--sortie-->
```text
AUC en apprentissage : 0.6841 ( 848 clients )
AUC en test          : 0.7193 ( 364 clients )
```

**Étape 5 — La séparation parfaite.** Six clients : les trois premiers n'ont pas racheté, les trois derniers si. Lisez attentivement l'avertissement et la valeur de la pente.

```python
import warnings
x_sep = np.array([1.0, 2, 3, 4, 5, 6])
y_sep = np.array([0, 0, 0, 1, 1, 1])
with warnings.catch_warnings(record=True) as avertissements:
    warnings.simplefilter("always")
    try:
        res = sm.GLM(y_sep, sm.add_constant(x_sep), family=sm.families.Binomial()).fit()
        print("pente estimée :", round(float(res.params[1]), 1), "| erreur-type de la pente :", round(float(res.bse[1]), 1))
        print("probabilités prédites (arrondies) :", res.fittedvalues.round(3).tolist())
    except Exception as e:
        print(type(e).__name__, ":", e)
    for message in sorted({str(a.message) for a in avertissements}):
        print("AVERTISSEMENT :", message)
```
<!--sortie-->
```text
pente estimée : 41.2 | erreur-type de la pente : 25719.8
probabilités prédites (arrondies) : [0.0, 0.0, 0.0, 1.0, 1.0, 1.0]
AVERTISSEMENT : Perfect separation or prediction detected, parameter may not be identified
```

### Application 2.4 — Comptages : Poisson, exposition, surdispersion

*Sections du livre : 2.3.1 à 2.3.3.* **Objectif** : modéliser le nombre de commandes, voir l'effet d'un oubli de l'exposition, mesurer la surdispersion et la corriger.

**Étape 1 — Un modèle de Poisson avec une variable catégorielle, puis complet.** Les exponentielles des coefficients sont des rapports de taux.

```python
moy = clients.groupby("canal", observed=True)["nb_commandes_an"].mean()
m_canal = smf.glm("nb_commandes_an ~ canal", clients, family=sm.families.Poisson()).fit()
print("moyennes observées par canal :", moy.round(4).to_dict())
print("rapports de moyennes / Boutique :", (moy / moy["Boutique"]).round(4).to_dict())
print("exp(coefficients) Poisson :", np.exp(m_canal.params).round(4).to_dict())
print("exp(Intercept) = moyenne de la boutique :", round(float(np.exp(m_canal.params["Intercept"])), 4))
```
<!--sortie-->
```text
moyennes observées par canal : {'Boutique': 4.1369, 'Réseaux': 3.4645, 'Site': 4.1971}
rapports de moyennes / Boutique : {'Boutique': 1.0, 'Réseaux': 0.8375, 'Site': 1.0145}
exp(coefficients) Poisson : {'Intercept': 4.1369, 'canal[T.Réseaux]': 0.8375, 'canal[T.Site]': 1.0145}
exp(Intercept) = moyenne de la boutique : 4.1369
```
```python
poisson = smf.glm("nb_commandes_an ~ age + canal + offre_bienvenue", clients, family=sm.families.Poisson()).fit()
ic = poisson.conf_int()
rr = pd.DataFrame({"coef": poisson.params, "RR": np.exp(poisson.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1]),
                   "p": poisson.pvalues})
print(rr.round(4).to_string())
```
<!--sortie-->
```text
                    coef      RR  IC95 bas  IC95 haut       p
Intercept         1.4637  4.3218    3.9509     4.7275  0.0000
canal[T.Réseaux] -0.1762  0.8385    0.7923     0.8873  0.0000
canal[T.Site]     0.0151  1.0152    0.9594     1.0742  0.6008
age              -0.0010  0.9990    0.9969     1.0011  0.3675
offre_bienvenue  -0.0189  0.9813    0.9385     1.0259  0.4051
```

**Étape 2 — L'exposition.** On simule 1 500 clients observés 3, 6, 9 ou 12 mois ; les clients anciens sont plus souvent abonnés à la newsletter ; le vrai effet de la newsletter est de multiplier le taux par 1,2. Comparez le modèle naïf, le modèle avec décalage $\log(\text{mois})$ et le modèle où $\log(\text{mois})$ est une variable libre.

```python
rng = np.random.default_rng(23)
n = 1500
mois_obs = rng.choice([3, 6, 9, 12], size=n)
p_newsletter = pd.Series(mois_obs).map({3: 0.15, 6: 0.30, 9: 0.45, 12: 0.65}).to_numpy()
newsletter = rng.binomial(1, p_newsletter)
taux_mensuel = 0.4 * 1.2 ** newsletter                     # commandes par mois : vrai RR = 1,2
sim = pd.DataFrame({"mois": mois_obs, "newsletter": newsletter, "commandes": rng.poisson(taux_mensuel * mois_obs)})

naif = smf.glm("commandes ~ newsletter", sim, family=sm.families.Poisson()).fit()
avec_offset = smf.glm("commandes ~ newsletter", sim, family=sm.families.Poisson(), offset=np.log(sim["mois"])).fit()
libre = smf.glm("commandes ~ newsletter + np.log(mois)", sim, family=sm.families.Poisson()).fit()

print("part de clients abonnés à la newsletter :", round(float(sim["newsletter"].mean()), 3))
print("exposition moyenne : sans newsletter =", round(sim.loc[sim.newsletter == 0, "mois"].mean(), 2), "mois | avec newsletter =", round(sim.loc[sim.newsletter == 1, "mois"].mean(), 2), "mois")
g = sim.groupby("newsletter").agg(commandes=("commandes", "sum"), clients_mois=("mois", "sum"))
g["taux par client-mois"] = g["commandes"] / g["clients_mois"]
print(g.round(4).to_string())
print()
print("vrai RR de la newsletter                 : 1.2")
print("RR sans tenir compte de la durée         :", round(float(np.exp(naif.params["newsletter"])), 3))
print("RR avec décalage log(mois)               :", round(float(np.exp(avec_offset.params["newsletter"])), 3),
      "  IC95 [", ", ".join(str(round(float(v), 3)) for v in np.exp(avec_offset.conf_int().loc["newsletter"])), "]")
print("RR avec log(mois) comme variable libre   :", round(float(np.exp(libre.params["newsletter"])), 3),
      "| coefficient de log(mois) :", round(float(libre.params["np.log(mois)"]), 3), "(attendu : 1)")
```
<!--sortie-->
```text
part de clients abonnés à la newsletter : 0.381
exposition moyenne : sans newsletter = 6.44 mois | avec newsletter = 9.05 mois
            commandes  clients_mois  taux par client-mois
newsletter                                               
0                2360          5979                0.3947
1                2451          5166                0.4744

vrai RR de la newsletter                 : 1.2
RR sans tenir compte de la durée         : 1.69
RR avec décalage log(mois)               : 1.202   IC95 [ 1.136, 1.272 ]
RR avec log(mois) comme variable libre   : 1.196 | coefficient de log(mois) : 1.017 (attendu : 1)
```

**Étape 3 — Mesurer la surdispersion** : rapport $X^2/\text{ddl}$ et test de Cameron-Trivedi.

```python
y = clients["nb_commandes_an"].to_numpy()
mu = poisson.fittedvalues.to_numpy()
print("Pearson X² =", round(poisson.pearson_chi2, 1), "| degrés de liberté =", int(poisson.df_resid), "| phi estimé =", round(poisson.pearson_chi2 / poisson.df_resid, 3))
print("déviance   =", round(poisson.deviance, 1), "| déviance / ddl =", round(poisson.deviance / poisson.df_resid, 3))

# Test de Cameron et Trivedi (1990) : sous Poisson, E[(y-mu)² - y] = 0 ; sous « variance = mu + alpha mu² », E[(y-mu)² - y] = alpha mu²
aux = ((y - mu) ** 2 - y) / mu
reg = sm.OLS(aux, mu).fit()        # régression de ((y-mu)²-y)/mu sur mu, sans constante : la pente estime alpha
print("alpha estimé par Cameron-Trivedi :", round(float(reg.params[0]), 3), "| t =", round(float(reg.tvalues[0]), 2))
```
<!--sortie-->
```text
Pearson X² = 6774.2 | degrés de liberté = 1995 | phi estimé = 3.396
déviance   = 6293.0 | déviance / ddl = 3.154
alpha estimé par Cameron-Trivedi : 0.609 | t = 12.47
```

**Étape 4 — Trois remèdes** : quasi-Poisson, erreurs-types robustes, binomiale négative. Vérifiez au passage par simulation que le mélange Poisson-Gamma a bien pour variance $\mu+\alpha\mu^2$.

```python
rng = np.random.default_rng(3)
mu0, alpha0, N = 4.0, 0.6, 400_000
lam = rng.gamma(shape=1 / alpha0, scale=mu0 * alpha0, size=N)       # Gamma de moyenne mu0 et de variance alpha0 * mu0²
tirages = rng.poisson(lam)
print(f"simulation : moyenne = {tirages.mean():.3f} | variance = {tirages.var():.3f}")
print(f"formule    : moyenne = {mu0:.3f} | variance = {mu0 + alpha0 * mu0**2:.3f}")
```
<!--sortie-->
```text
simulation : moyenne = 4.004 | variance = 13.640
formule    : moyenne = 4.000 | variance = 13.600
```
```python
formule = "nb_commandes_an ~ age + canal + offre_bienvenue"
quasi = smf.glm(formule, clients, family=sm.families.Poisson()).fit(scale="X2")
robuste = smf.glm(formule, clients, family=sm.families.Poisson()).fit(cov_type="HC0")
nb = smf.negativebinomial(formule, clients).fit(disp=0)

comp = pd.DataFrame({
    "coef Poisson": poisson.params, "coef NB": nb.params[poisson.params.index],
    "se Poisson": poisson.bse, "se quasi-Poisson": quasi.bse, "se robuste": robuste.bse, "se NB": nb.bse[poisson.params.index],
})
print()
print(comp.round(4).to_string())
print()
print("ratio se quasi-Poisson / se Poisson :", round(float((quasi.bse / poisson.bse).mean()), 3), "| racine de phi =", round(float(np.sqrt(poisson.pearson_chi2 / poisson.df_resid)), 3))
print("alpha (binomiale négative) =", round(float(nb.params["alpha"]), 3), "| IC95 :", [round(float(v), 3) for v in nb.conf_int().loc["alpha"]])
lr = 2 * (nb.llf - poisson.llf)
log10_p = stats.norm.logsf(np.sqrt(lr)) / np.log(10)      # 0,5 × P(khi-deux à 1 ddl > lr) = P(N(0,1) > sqrt(lr)) ; en log pour éviter le dépassement de capacité
print(f"AIC Poisson = {poisson.aic:.1f} | AIC binomiale négative = {nb.aic:.1f} | RV : 2(l_NB - l_Poisson) = {lr:.1f}, log10(p) = {log10_p:.0f}")
```
<!--sortie-->
```text

                  coef Poisson  coef NB  se Poisson  se quasi-Poisson  se robuste   se NB
Intercept               1.4637   1.4681      0.0458            0.0844      0.0837  0.0840
canal[T.Réseaux]       -0.1762  -0.1765      0.0289            0.0532      0.0529  0.0520
canal[T.Site]           0.0151   0.0148      0.0288            0.0531      0.0529  0.0534
age                    -0.0010  -0.0011      0.0011            0.0020      0.0019  0.0020
offre_bienvenue        -0.0189  -0.0156      0.0227            0.0419      0.0419  0.0411

ratio se quasi-Poisson / se Poisson : 1.843 | racine de phi = 1.843
alpha (binomiale négative) = 0.584 | IC95 : [0.528, 0.639]
AIC Poisson = 11715.5 | AIC binomiale négative = 9768.7 | RV : 2(l_NB - l_Poisson) = 1948.8, log10(p) = -425
```

**Étape 5 — Quelle loi décrit la distribution entière ?** Comparez les fréquences observées à celles que prédisent Poisson et la binomiale négative (la figure du livre est produite par la cellule masquée).

```python
valeurs = np.arange(0, 16)
obs = np.array([(y == k).mean() for k in valeurs])
mu_p = poisson.fittedvalues.to_numpy()
mu_nb = np.asarray(nb.predict())
a = float(nb.params["alpha"])
pred_p = np.array([stats.poisson.pmf(k, mu_p).mean() for k in valeurs])
pred_nb = np.array([stats.nbinom.pmf(k, 1 / a, (1 / a) / ((1 / a) + mu_nb)).mean() for k in valeurs])
print(pd.DataFrame({"observé": obs, "Poisson": pred_p, "binomiale négative": pred_nb}, index=valeurs).round(3).head(8).to_string())
print()
print("écart absolu moyen aux fréquences observées : Poisson =", round(float(np.abs(obs - pred_p).mean()), 4), "| binomiale négative =", round(float(np.abs(obs - pred_nb).mean()), 4))
```
<!--sortie-->
```text
   observé  Poisson  binomiale négative
0    0.130    0.022               0.133
1    0.154    0.082               0.157
2    0.158    0.156               0.147
3    0.130    0.199               0.126
4    0.096    0.192               0.103
5    0.088    0.149               0.081
6    0.060    0.097               0.063
7    0.048    0.055               0.048

écart absolu moyen aux fréquences observées : Poisson = 0.033 | binomiale négative = 0.0035
```
```python hide
fig, ax = plt.subplots(figsize=(7.2, 4.2))
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ax.bar(valeurs, obs, color="#c3c2b7", width=0.8, label="observé")
ax.plot(valeurs, pred_p, "o-", color=ORANGE, lw=1.8, ms=4, label="Poisson ajusté")
ax.plot(valeurs, pred_nb, "s-", color=BLEU, lw=1.8, ms=4, label="binomiale négative ajustée")
ax.set_xlabel("nombre de commandes dans l'année"); ax.set_ylabel("proportion de clients")
ax.set_title("Quelle loi décrit le mieux les comptages ?"); ax.legend(frameon=False)
plt.tight_layout()
plt.savefig("figures/ch02-poisson-vs-nb.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

### Application 2.5 — Montants : régression Gamma contre régression sur le logarithme

*Section du livre : 2.3.4.* **Objectif** : ajuster une régression Gamma à lien log sur les acheteurs, la reproduire avec IRLS, puis comparer ses prédictions en € à celles d'une régression sur $\log y$ (la médiane, pas la moyenne).

```python
acheteurs = clients[clients["depense_annuelle"] > 0].copy()
print("acheteurs :", len(acheteurs), "sur", len(clients), "| dépense moyenne =", round(acheteurs["depense_annuelle"].mean(), 1), "€ | médiane =", round(acheteurs["depense_annuelle"].median(), 1), "€")

formule_d = "depense_annuelle ~ age + canal + offre_bienvenue"
gamma = smf.glm(formule_d, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
print()
print(gamma.summary().tables[1])
phi = gamma.scale
print()
print("dispersion phi estimée =", round(phi, 3), "| coefficient de variation implicite =", round(float(np.sqrt(phi)), 3))
```
<!--sortie-->
```text
acheteurs : 1740 sur 2000 | dépense moyenne = 283.9 € | médiane = 193.4 €

====================================================================================
                       coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------------
Intercept            5.6086      0.098     57.234      0.000       5.417       5.801
canal[T.Réseaux]    -0.4988      0.061     -8.181      0.000      -0.618      -0.379
canal[T.Site]       -0.1518      0.063     -2.425      0.015      -0.275      -0.029
age                  0.0075      0.002      3.295      0.001       0.003       0.012
offre_bienvenue     -0.0098      0.048     -0.203      0.839      -0.104       0.085
====================================================================================

dispersion phi estimée = 1.009 | coefficient de variation implicite = 1.004
```

**Reproduction avec notre IRLS** (Application 2.1) : la dispersion $\phi$ est inconnue, on l'estime par $X^2/(n-p)$ et l'on multiplie la covariance par $\hat\phi$.

```python
from patsy import dmatrices

Yd, Xd = dmatrices(formule_d, acheteurs, return_type="dataframe")
r = irls(Xd.to_numpy(), Yd.to_numpy().ravel(), "gamma_log")
mu_d = r["mu"]
phi_main = np.sum((Yd.to_numpy().ravel() - mu_d) ** 2 / mu_d**2) / (len(acheteurs) - Xd.shape[1])
se_main = np.sqrt(np.diag(r["cov"]) * phi_main)
print(pd.DataFrame({"coef main": r["beta"], "coef statsmodels": gamma.params.to_numpy(), "se main": se_main, "se statsmodels": gamma.bse.to_numpy()},
                   index=Xd.columns).round(5).to_string())
print("phi (main) =", round(float(phi_main), 4), "| phi (statsmodels) =", round(phi, 4), "| itérations :", r["iterations"])
```
<!--sortie-->
```text
                  coef main  coef statsmodels  se main  se statsmodels
Intercept           5.60858           5.60858  0.09799         0.09799
canal[T.Réseaux]   -0.49879          -0.49879  0.06097         0.06097
canal[T.Site]      -0.15181          -0.15181  0.06260         0.06260
age                 0.00754           0.00754  0.00229         0.00229
offre_bienvenue    -0.00980          -0.00980  0.04819         0.04819
phi (main) = 1.0088 | phi (statsmodels) = 1.0088 | itérations : 11
```

**Gamma contre OLS sur $\log y$** : les rapports de moyennes sont voisins, mais pas les prédictions en €. Testez aussi la correction de Duan.

```python
ols_log = smf.ols("np.log(depense_annuelle) ~ age + canal + offre_bienvenue", acheteurs).fit()
print(pd.DataFrame({"effet (Gamma, log)": gamma.params, "effet (OLS sur log y)": ols_log.params}).round(4).to_string())
print()
y_d = acheteurs["depense_annuelle"]
naif_log = np.exp(ols_log.fittedvalues)
lissage = naif_log * np.mean(np.exp(ols_log.resid))                  # correction de Duan (« smearing »)
print("dépense moyenne observée                                  :", round(float(y_d.mean()), 1), "€")
print("moyenne des prédictions Gamma (lien log)                  :", round(float(gamma.fittedvalues.mean()), 1), "€")
print("moyenne des prédictions exp(OLS sur log y), sans correction :", round(float(naif_log.mean()), 1), "€")
print("idem avec la correction de Duan                           :", round(float(lissage.mean()), 1), "€")
print()
par_canal = pd.DataFrame({"observée": y_d.groupby(acheteurs["canal"], observed=True).mean(),
                          "Gamma": gamma.fittedvalues.groupby(acheteurs["canal"], observed=True).mean(),
                          "exp(OLS log)": naif_log.groupby(acheteurs["canal"], observed=True).mean()})
print(par_canal.round(1).to_string())
```
<!--sortie-->
```text
                  effet (Gamma, log)  effet (OLS sur log y)
Intercept                     5.6086                 5.1977
canal[T.Réseaux]             -0.4988                -0.4608
canal[T.Site]                -0.1518                -0.1381
age                           0.0075                 0.0075
offre_bienvenue              -0.0098                -0.0238

dépense moyenne observée                                  : 283.9 €
moyenne des prédictions Gamma (lien log)                  : 284.0 €
moyenne des prédictions exp(OLS sur log y), sans correction : 189.9 €
idem avec la correction de Duan                           : 283.1 €

          observée  Gamma  exp(OLS log)
canal                                  
Boutique     355.0  356.6         234.6
Réseaux      216.8  217.0         148.2
Site         307.2  306.1         204.1
```

### Application 2.6 — Vérifier un modèle : déviance, résidus, calibration, influence

*Sections du livre : 2.4.1 à 2.4.6.* **Objectif** : calculer la déviance à la main, comparer des modèles emboîtés, produire les résidus quantiles aléatoires, tester la calibration, comparer par AIC/BIC et repérer les observations influentes.

**Étape 1 — Déviance unitaire, calcul à la main.** Quatre clients avec $y=(2,5,3,8)$ commandes ; on compare avec `statsmodels`, puis sur les trois modèles du chapitre.

```python
from scipy.special import xlogy

def deviance_unitaire(famille, y, mu):
    """Déviance unitaire d(y, mu) pour chaque observation (xlogy gère la convention 0 log 0 = 0)."""
    if famille == "normale":
        return (y - mu) ** 2
    if famille == "poisson":
        return 2 * (xlogy(y, y / mu) - (y - mu))
    if famille == "bernoulli":
        return 2 * (xlogy(y, y / mu) + xlogy(1 - y, (1 - y) / (1 - mu)))
    if famille == "gamma":
        return 2 * (-np.log(y / mu) + (y - mu) / mu)
```
```python
y4 = np.array([2.0, 5, 3, 8])
mu4 = np.full(4, y4.mean())
print("déviance à la main    :", round(float(deviance_unitaire("poisson", y4, mu4).sum()), 4))
print("Pearson X² à la main  :", round(float((((y4 - mu4) ** 2) / mu4).sum()), 4))
m4 = sm.GLM(y4, np.ones((4, 1)), family=sm.families.Poisson()).fit()
print("déviance statsmodels  :", round(float(m4.deviance), 4), "| Pearson statsmodels :", round(float(m4.pearson_chi2), 4))
```
<!--sortie-->
```text
déviance à la main    : 4.5829
Pearson X² à la main  : 4.6667
déviance statsmodels  : 4.5829 | Pearson statsmodels : 4.6667
```
```python
# Les trois modèles des sections 2.2 et 2.3, sur les vraies données
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])
logi = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
poi = smf.glm("nb_commandes_an ~ age + canal + offre_bienvenue", clients, family=sm.families.Poisson()).fit()
acheteurs = clients[clients["depense_annuelle"] > 0]
gam = smf.glm("depense_annuelle ~ age + canal + offre_bienvenue", acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")

lignes = []
for nom, fam, res, y in [("logistique", "bernoulli", logi, clients["rachat_12m"]), ("Poisson", "poisson", poi, clients["nb_commandes_an"]),
                         ("Gamma", "gamma", gam, acheteurs["depense_annuelle"])]:
    d_main = deviance_unitaire(fam, y.to_numpy(float), res.fittedvalues.to_numpy()).sum()
    mu_nul = np.full(len(y), y.mean())
    d_nul = deviance_unitaire(fam, y.to_numpy(float), mu_nul).sum()
    lignes.append({"modèle": nom, "déviance (main)": d_main, "déviance (statsmodels)": res.deviance, "déviance nulle (main)": d_nul,
                   "déviance nulle (statsmodels)": res.null_deviance, "part de déviance expliquée": 1 - d_main / d_nul})
print()
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text

    modèle  déviance (main)  déviance (statsmodels)  déviance nulle (main)  déviance nulle (statsmodels)  part de déviance expliquée
logistique         2710.830                2710.830               2771.867                      2771.867                       0.022
   Poisson         6292.954                6292.954               6357.639                      6357.639                       0.010
     Gamma         1389.349                1389.349               1473.452                      1473.452                       0.057
```

**Étape 2 — Rapport de vraisemblance** entre modèles emboîtés (logistique, puis test $F$ pour la régression Gamma).

```python
def test_rv(complet, reduit, ddl):
    delta = reduit.deviance - complet.deviance
    return delta, ddl, stats.chi2.sf(delta, ddl)

formule_c = "rachat_12m ~ offre_bienvenue + age + canal"
complet = smf.glm(formule_c, clients, family=sm.families.Binomial()).fit()
essais = [("canal (2 ddl)", "rachat_12m ~ offre_bienvenue + age", 2),
          ("age (1 ddl)", "rachat_12m ~ offre_bienvenue + canal", 1),
          ("offre_bienvenue (1 ddl)", "rachat_12m ~ age + canal", 1)]
wald = complet.wald_test_terms(scalar=True).table
lignes = []
for nom, f_reduite, ddl in essais:
    reduit = smf.glm(f_reduite, clients, family=sm.families.Binomial()).fit()
    delta, q, p_rv = test_rv(complet, reduit, ddl)
    terme = nom.split(" ")[0]
    lignes.append({"variable retirée": nom, "D réduit - D complet": delta, "p (rapport de vraisemblance)": p_rv,
                   "p (Wald)": wald.loc[terme, "pvalue"]})
print(pd.DataFrame(lignes).round(4).to_string(index=False))
print()
print("déviance du modèle complet :", round(complet.deviance, 2), "| déviance sans l'offre :", round(smf.glm("rachat_12m ~ age + canal", clients, family=sm.families.Binomial()).fit().deviance, 2))
```
<!--sortie-->
```text
       variable retirée  D réduit - D complet  p (rapport de vraisemblance)  p (Wald)
          canal (2 ddl)               17.7355                        0.0001    0.0001
            age (1 ddl)               12.7919                        0.0003    0.0004
offre_bienvenue (1 ddl)               29.6401                        0.0000    0.0000

déviance du modèle complet : 2710.83 | déviance sans l'offre : 2740.47
```
```python
f_gamma = "depense_annuelle ~ age + canal + offre_bienvenue"
g_complet = smf.glm(f_gamma, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
phi_g = g_complet.scale
for nom, f_reduite, ddl in [("canal (2 ddl)", "depense_annuelle ~ age + offre_bienvenue", 2), ("offre_bienvenue (1 ddl)", "depense_annuelle ~ age + canal", 1)]:
    g_reduit = smf.glm(f_reduite, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
    F = (g_reduit.deviance - g_complet.deviance) / ddl / phi_g
    print(f"{nom:24s}: F = {F:7.2f} sur ({ddl}, {int(g_complet.df_resid)}) ddl | p = {stats.f.sf(F, ddl, g_complet.df_resid):.2e}")
```
<!--sortie-->
```text
canal (2 ddl)           : F =   37.09 sur (2, 1735) ddl | p = 1.69e-16
offre_bienvenue (1 ddl) : F =    0.04 sur (1, 1735) ddl | p = 8.39e-01
```

**Étape 3 — Résidus de Pearson et de déviance** du modèle de Poisson : leur écart-type devrait être voisin de 1 si le modèle était correct.

```python
r_p = poi.resid_pearson.to_numpy()
r_d = poi.resid_deviance.to_numpy()
print("Poisson : somme des carrés des résidus de Pearson   =", round(float((r_p ** 2).sum()), 1), "| X² =", round(poi.pearson_chi2, 1))
print("Poisson : somme des carrés des résidus de déviance =", round(float((r_d ** 2).sum()), 1), "| D  =", round(poi.deviance, 1))
print("résidus de Pearson : moyenne =", round(float(r_p.mean()), 3), "| écart-type =", round(float(r_p.std()), 3), "(attendu : environ 1 si le modèle est correct)")
print("part de |résidus de Pearson| > 2 :", round(float((np.abs(r_p) > 2).mean()), 3), "(attendu pour une loi normale : environ 0,046)")
```
<!--sortie-->
```text
Poisson : somme des carrés des résidus de Pearson   = 6774.2 | X² = 6774.2
Poisson : somme des carrés des résidus de déviance = 6293.0 | D  = 6293.0
résidus de Pearson : moyenne = -0.0 | écart-type = 1.84 (attendu : environ 1 si le modèle est correct)
part de |résidus de Pearson| > 2 : 0.175 (attendu pour une loi normale : environ 0,046)
```

**Étape 4 — Résidus quantiles aléatoires** (Dunn et Smyth) pour quatre modèles. Pour la logistique, comparez avec le modèle sans variable : que constatez-vous ?

```python
rng = np.random.default_rng(44)

def residus_quantiles(u_bas, u_haut):
    u = rng.uniform(u_bas, u_haut)
    return stats.norm.ppf(np.clip(u, 1e-12, 1 - 1e-12))

y_b = clients["rachat_12m"].to_numpy()
p_b = logi.fittedvalues.to_numpy()
rq_logi = residus_quantiles(np.where(y_b == 1, 1 - p_b, 0.0), np.where(y_b == 1, 1.0, 1 - p_b))
```

**Binomiale négative et Gamma** : leurs résidus quantiles se calculent avec la loi de répartition propre à chaque modèle.

```python
y_c = clients["nb_commandes_an"].to_numpy()
mu_p = poi.fittedvalues.to_numpy()
rq_poi = residus_quantiles(stats.poisson.cdf(y_c - 1, mu_p), stats.poisson.cdf(y_c, mu_p))

nbm = smf.negativebinomial("nb_commandes_an ~ age + canal + offre_bienvenue", clients).fit(disp=0)
a_nb, mu_nb = float(nbm.params["alpha"]), np.asarray(nbm.predict())
n_nb, p_nb = 1 / a_nb, (1 / a_nb) / ((1 / a_nb) + mu_nb)
rq_nb = residus_quantiles(stats.nbinom.cdf(y_c - 1, n_nb, p_nb), stats.nbinom.cdf(y_c, n_nb, p_nb))
```

**Résumé** : le modèle sans variable sert de point de comparaison pour la logistique ; on résume les moyenne, écart-type, part de $|r|>2$ et test de Kolmogorov-Smirnov.

```python
y_g = acheteurs["depense_annuelle"].to_numpy()
mu_g = gam.fittedvalues.to_numpy()
u_g = stats.gamma.cdf(y_g, a=1 / gam.scale, scale=mu_g * gam.scale)
rq_gam = stats.norm.ppf(np.clip(u_g, 1e-12, 1 - 1e-12))

# Même le modèle SANS variable (probabilité constante) donne des résidus quantiles « parfaits » pour un 0/1
p_nul = np.full(len(y_b), y_b.mean())
rq_nul = residus_quantiles(np.where(y_b == 1, 1 - p_nul, 0.0), np.where(y_b == 1, 1.0, 1 - p_nul))

resume = []
for nom, r in [("logistique", rq_logi), ("logistique sans variable", rq_nul), ("Poisson", rq_poi), ("binomiale négative", rq_nb), ("Gamma", rq_gam)]:
    resume.append({"modèle": nom, "moyenne": r.mean(), "écart-type": r.std(), "part de |r| > 2": (np.abs(r) > 2).mean(),
                   "p (Kolmogorov-Smirnov)": stats.kstest(r, "norm").pvalue})
print(pd.DataFrame(resume).round(3).to_string(index=False))
```
<!--sortie-->
```text
                  modèle  moyenne  écart-type  part de |r| > 2  p (Kolmogorov-Smirnov)
              logistique    0.010       1.009            0.048                   0.896
logistique sans variable   -0.020       1.008            0.040                   0.257
                 Poisson   -0.148       1.675            0.228                   0.000
      binomiale négative    0.004       0.991            0.045                   0.849
                   Gamma    0.087       0.833            0.023                   0.000
```
```python hide
fig, axes = plt.subplots(1, 4, figsize=(14, 3.7), sharex=True, sharey=True)
BLEU, ORANGE = "#2a78d6", "#eb6834"
for ax, (nom, r, c) in zip(axes, [("logistique", rq_logi, BLEU), ("Poisson", rq_poi, ORANGE), ("binomiale négative", rq_nb, BLEU), ("Gamma", rq_gam, BLEU)]):
    r = np.sort(r)
    theo = stats.norm.ppf((np.arange(1, len(r) + 1) - 0.5) / len(r))
    ax.plot(theo, r, ".", color=c, ms=3)
    ax.plot([-4, 4], [-4, 4], color="#52514e", lw=1)
    ax.set_title(nom); ax.set_xlabel("quantiles de la loi normale")
axes[0].set_ylabel("résidus quantiles aléatoires")
axes[0].set_xlim(-4, 4); axes[0].set_ylim(-4, 4)
plt.tight_layout()
plt.savefig("figures/ch02-residus-quantiles.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

**Étape 5 — Dispersion et calibration.** Le rapport $X^2/\text{ddl}$ pour la binomiale négative, puis le test de Hosmer-Lemeshow (sur le modèle de rachat, puis sur des sessions de navigation dont l'effet de la durée est « en cloche »).

```python
x2_nb = np.sum((y_c - mu_nb) ** 2 / (mu_nb + a_nb * mu_nb ** 2))
ddl_nb = len(y_c) - len(nbm.params) + 1          # on retire le paramètre alpha du compte des coefficients
print("Poisson            : X²/ddl =", round(poi.pearson_chi2 / poi.df_resid, 3))
print("binomiale négative : X²/ddl =", round(float(x2_nb / ddl_nb), 3))
```
<!--sortie-->
```text
Poisson            : X²/ddl = 3.396
binomiale négative : X²/ddl = 1.044
```
```python
def hosmer_lemeshow(y, p, g=10):
    classes = pd.qcut(p, g, labels=False, duplicates="drop")
    d = pd.DataFrame({"y": y, "p": p, "k": classes}).groupby("k").agg(O=("y", "sum"), E=("p", "sum"), n=("y", "size"))
    d["pbar"] = d["E"] / d["n"]
    hl = (((d["O"] - d["E"]) ** 2) / (d["E"] * (1 - d["pbar"]))).sum()
    ddl = len(d) - 2
    return hl, ddl, stats.chi2.sf(hl, ddl), d

hl, ddl, p_hl, tab = hosmer_lemeshow(clients["rachat_12m"].to_numpy(), logi.fittedvalues.to_numpy())
print(f"modèle de rachat : HL = {hl:.2f} sur {ddl} ddl, p = {p_hl:.3f}")

# Un modèle mal spécifié : sessions de navigation (simulées), effet de la durée en « cloche » mais modèle linéaire sur le logit
sessions = pd.read_csv("donnees/ch02-sessions.csv")
lineaire = smf.glm("achat ~ duree_min", sessions, family=sm.families.Binomial()).fit()
bosse = smf.glm("achat ~ duree_min + I(duree_min**2)", sessions, family=sm.families.Binomial()).fit()
for nom, res in [("linéaire sur le logit", lineaire), ("avec terme quadratique", bosse)]:
    hl_s, ddl_s, p_s, _ = hosmer_lemeshow(sessions["achat"].to_numpy(), res.fittedvalues.to_numpy())
    print(f"sessions, {nom:24s} : HL = {hl_s:6.2f} sur {ddl_s} ddl, p = {p_s:.4f} | AIC = {res.aic:.1f}")
```
<!--sortie-->
```text
modèle de rachat : HL = 6.15 sur 8 ddl, p = 0.631
sessions, linéaire sur le logit    : HL = 243.18 sur 8 ddl, p = 0.0000 | AIC = 1960.3
sessions, avec terme quadratique   : HL =  54.33 sur 8 ddl, p = 0.0000 | AIC = 1787.7
```

**Étape 6 — Résidus par classes** : comparez, par tranche de durée, la fréquence observée aux probabilités du modèle linéaire et du modèle quadratique. (La figure est produite par la cellule masquée.)

```python
tranches = pd.cut(sessions["duree_min"], bins=[0, 3, 5, 7, 9, 11, 13, 15, 18, 22, 40])
g = sessions.assign(p_lin=lineaire.fittedvalues, p_bosse=bosse.fittedvalues, tranche=tranches).groupby("tranche", observed=True).agg(
    duree=("duree_min", "mean"), observe=("achat", "mean"), p_lineaire=("p_lin", "mean"), p_bosse=("p_bosse", "mean"), n=("achat", "size"))
print(g.round(3).to_string())
```
<!--sortie-->
```text
           duree  observe  p_lineaire  p_bosse    n
tranche                                            
(0, 3]     2.265    0.189       0.630    0.174   37
(3, 5]     4.240    0.333       0.584    0.343  114
(5, 7]     6.113    0.381       0.539    0.489  231
(7, 9]     8.100    0.650       0.490    0.581  240
(9, 11]   10.051    0.740       0.443    0.600  223
(11, 13]  11.930    0.566       0.398    0.553  182
(13, 15]  14.071    0.320       0.350    0.422  147
(15, 18]  16.367    0.140       0.301    0.226  171
(18, 22]  19.996    0.079       0.232    0.037  101
(22, 40]  26.831    0.019       0.139    0.001   54
```
```python hide
fig, ax = plt.subplots(figsize=(7.2, 4.2))
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ax.plot(g["duree"], g["observe"], "o", color="#52514e", label="fréquence observée (par tranche)")
ax.plot(g["duree"], g["p_lineaire"], "-", color=ORANGE, lw=2, label="modèle linéaire sur le logit")
ax.plot(g["duree"], g["p_bosse"], "-", color=BLEU, lw=2, label="avec terme quadratique")
ax.set_xlabel("durée de la session (minutes)"); ax.set_ylabel("probabilité d'achat")
ax.set_title("Un modèle mal spécifié se voit dans les résidus par classes"); ax.legend(frameon=False, fontsize=9)
plt.tight_layout()
plt.savefig("figures/ch02-residus-par-classes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

**Étape 7 — AIC et BIC, observations influentes.** Cinq modèles de rachat, de « aucune variable » à « avec interactions » : les deux critères choisissent-ils le même ? Puis levier et distance de Cook du modèle logistique.

```python
formules = {
    "aucune variable": "rachat_12m ~ 1",
    "+ offre": "rachat_12m ~ offre_bienvenue",
    "+ offre + âge": "rachat_12m ~ offre_bienvenue + age",
    "+ offre + âge + canal": "rachat_12m ~ offre_bienvenue + age + canal",
    "+ offre × canal (interactions)": "rachat_12m ~ offre_bienvenue * canal + age",
}
lignes = []
ajustes = {}
for nom, f in formules.items():
    r = smf.glm(f, clients, family=sm.families.Binomial()).fit()
    ajustes[nom] = r
    lignes.append({"modèle": nom, "paramètres": len(r.params), "déviance": r.deviance, "AIC": r.aic, "BIC": r.bic_llf})
res = pd.DataFrame(lignes)
res["ΔAIC"] = res["AIC"] - res["AIC"].min()
res["ΔBIC"] = res["BIC"] - res["BIC"].min()
print(res.round(1).to_string(index=False))
delta_inter = ajustes["+ offre + âge + canal"].deviance - ajustes["+ offre × canal (interactions)"].deviance
print(f"\ntest du rapport de vraisemblance pour les 2 interactions : différence de déviance = {delta_inter:.2f}, p = {stats.chi2.sf(delta_inter, 2):.3f}")
```
<!--sortie-->
```text
                        modèle  paramètres  déviance    AIC    BIC  ΔAIC  ΔBIC
               aucune variable           1    2771.9 2773.9 2779.5  57.8  30.6
                       + offre           2    2742.1 2746.1 2757.3  30.1   8.5
                 + offre + âge           3    2728.6 2734.6 2751.4  18.5   2.5
         + offre + âge + canal           5    2710.8 2720.8 2748.8   4.8   0.0
+ offre × canal (interactions)           7    2702.1 2716.1 2755.3   0.0   6.4

test du rapport de vraisemblance pour les 2 interactions : différence de déviance = 8.77, p = 0.012
```
```python
infl = logi.get_influence()
levier = infl.hat_matrix_diag
cook = infl.cooks_distance[0]
print("levier moyen =", round(float(levier.mean()), 4), "(= p/n =", round(5 / len(clients), 4), ") | levier maximal =", round(float(levier.max()), 4))
print("distance de Cook maximale =", round(float(cook.max()), 4), "| seuil usuel 4/n =", round(4 / len(clients), 4), "| clients au-dessus du seuil :", int((cook > 4 / len(clients)).sum()))
pire = clients.loc[int(np.argmax(cook)), ["age", "canal_acquisition", "offre_bienvenue", "rachat_12m"]]
print("client le plus influent :", pire.to_dict())
print("probabilité de rachat prédite pour ce client :", round(float(logi.fittedvalues.iloc[int(np.argmax(cook))]), 3))
```
<!--sortie-->
```text
levier moyen = 0.0025 (= p/n = 0.0025 ) | levier maximal = 0.0076
distance de Cook maximale = 0.0023 | seuil usuel 4/n = 0.002 | clients au-dessus du seuil : 3
client le plus influent : {'age': 68, 'canal_acquisition': 'Boutique', 'offre_bienvenue': 0, 'rachat_12m': 1}
probabilité de rachat prédite pour ce client : 0.386
```

### Application 2.7 — Un GAM pour la durée des sessions

*Section du livre : 2.5.* **Objectif** : comprendre une base de fonctions (la base « chapeau » à la main), comparer des splines de 3, 6 et 15 fonctions, pénaliser la courbure, puis passer le test de calibration.

**Étape 1 — Une base « chapeau », à la main.** Quatre nœuds, quatre coefficients : calculez $f(5)$, $f(10)$, $f(14)$, $f(25)$.

```python
noeuds = np.array([0.0, 10.0, 20.0, 30.0])
def chapeau(x, k):
    return np.maximum(0.0, 1 - np.abs(x - noeuds[k]) / 10)

gamma = np.array([-1.8, 1.0, -1.2, -2.8])
for x in (5.0, 10.0, 14.0, 25.0):
    poids = [round(float(chapeau(x, k)), 2) for k in range(4)]
    f = sum(gamma[k] * chapeau(x, k) for k in range(4))
    print(f"x = {x:4.1f} : poids des 4 fonctions de base = {poids} -> f(x) = {f:.3f}")
```
<!--sortie-->
```text
x =  5.0 : poids des 4 fonctions de base = [0.5, 0.5, 0.0, 0.0] -> f(x) = -0.400
x = 10.0 : poids des 4 fonctions de base = [0.0, 1.0, 0.0, 0.0] -> f(x) = 1.000
x = 14.0 : poids des 4 fonctions de base = [0.0, 0.6, 0.4, 0.0] -> f(x) = 0.120
x = 25.0 : poids des 4 fonctions de base = [0.0, 0.0, 0.5, 0.5] -> f(x) = -2.000
```

**Étape 2 — Splines non pénalisées** de souplesse croissante, comparées à la vérité (connue, car les sessions sont simulées).

```python
sessions = pd.read_csv("donnees/ch02-sessions.csv")
def vrai_p(d):
    return expit(-1.8 + 3 * np.exp(-((d - 10) / 5) ** 2) - 0.04 * d)

grille = np.linspace(1, 35, 200)
p_vrai_obs = vrai_p(sessions["duree_min"].to_numpy())             # vraie probabilité de chaque session
rmse = lambda p_hat: float(np.sqrt(np.mean((p_hat - p_vrai_obs) ** 2)))

modeles = {
    "linéaire": "achat ~ duree_min",
    "quadratique": "achat ~ duree_min + I(duree_min**2)",
    "spline, 3 fonctions de base": "achat ~ bs(duree_min, df=3, lower_bound=0, upper_bound=40)",
    "spline, 6 fonctions de base": "achat ~ bs(duree_min, df=6, lower_bound=0, upper_bound=40)",
    "spline, 15 fonctions de base": "achat ~ bs(duree_min, df=15, lower_bound=0, upper_bound=40)",
}
courbes, lignes = {}, []
for nom, f in modeles.items():
    r = smf.glm(f, sessions, family=sm.families.Binomial()).fit()
    courbes[nom] = r.predict(pd.DataFrame({"duree_min": grille})).to_numpy()
    lignes.append({"modèle": nom, "paramètres": len(r.params), "AIC": r.aic, "erreur quadratique vs vérité": rmse(r.fittedvalues.to_numpy())})
print(pd.DataFrame(lignes).round(4).to_string(index=False))
```
<!--sortie-->
```text
                      modèle  paramètres       AIC  erreur quadratique vs vérité
                    linéaire           2 1960.2911                        0.1962
                 quadratique           3 1787.7267                        0.0776
 spline, 3 fonctions de base           4 1739.8372                        0.0630
 spline, 6 fonctions de base           7 1703.4622                        0.0306
spline, 15 fonctions de base          16 1708.0771                        0.0491
```

**Étape 3 — Pénaliser la courbure.** On prend 12 fonctions de base et l'on balaie le paramètre de lissage $\lambda$ (`alpha`), en gardant l'AIC minimal. Regardez comment les degrés de liberté effectifs diminuent quand $\lambda$ augmente.

```python
from statsmodels.gam.api import GLMGam, BSplines

base = BSplines(sessions[["duree_min"]], df=[12], degree=[3])          # 12 fonctions de base : large, la pénalité fera le tri
y_s = sessions["achat"].to_numpy()
X0 = np.ones((len(sessions), 1))                                       # constante seule : tout le reste est dans le lissage

lignes, ajustes = [], {}
for alpha in [0.01, 0.1, 1, 10, 30, 100, 1000, 10000]:
    res = GLMGam(y_s, exog=X0, smoother=base, alpha=alpha, family=sm.families.Binomial()).fit()
    ajustes[alpha] = res
    lignes.append({"alpha (lambda)": alpha, "edf du lissage": res.edf.sum() - 1, "AIC": res.aic,
                   "erreur quadratique vs vérité": rmse(res.fittedvalues)})
tab_alpha = pd.DataFrame(lignes)
print(tab_alpha.round(4).to_string(index=False))
alpha_opt = float(tab_alpha.loc[tab_alpha["AIC"].idxmin(), "alpha (lambda)"])
gam = ajustes[alpha_opt]
print("\nalpha retenu (AIC minimal) :", alpha_opt, "| edf du lissage =", round(float(gam.edf.sum() - 1), 2))
```
<!--sortie-->
```text
 alpha (lambda)  edf du lissage       AIC  erreur quadratique vs vérité
           0.01         10.9622 1709.0463                        0.0347
           0.10         10.6634 1708.4685                        0.0343
           1.00          9.2056 1705.9029                        0.0325
          10.00          6.5311 1702.7064                        0.0269
          30.00          5.1937 1704.1220                        0.0264
         100.00          3.8272 1711.9038                        0.0380
        1000.00          1.9769 1773.7390                        0.0995
       10000.00          1.2678 1900.7931                        0.1715

alpha retenu (AIC minimal) : 10.0 | edf du lissage = 6.53
```

**Étape 4 — Le GAM passe-t-il le test de Hosmer-Lemeshow ?** (la fonction `hosmer_lemeshow` est définie à l'application 2.6). La figure du livre est produite par la cellule masquée.

```python
for nom, p in [("linéaire", smf.glm("achat ~ duree_min", sessions, family=sm.families.Binomial()).fit().fittedvalues.to_numpy()),
               ("quadratique", smf.glm("achat ~ duree_min + I(duree_min**2)", sessions, family=sm.families.Binomial()).fit().fittedvalues.to_numpy()),
               ("GAM pénalisé", gam.fittedvalues)]:
    hl, ddl, p_val, _ = hosmer_lemeshow(y_s, p)
    print(f"{nom:14s}: HL = {hl:7.2f} sur {ddl} ddl, p = {p_val:.4f}")
```
<!--sortie-->
```text
linéaire      : HL =  243.18 sur 8 ddl, p = 0.0000
quadratique   : HL =   54.33 sur 8 ddl, p = 0.0000
GAM pénalisé  : HL =    6.29 sur 8 ddl, p = 0.6146
```
```python hide
grille = np.linspace(1, 35, 200)
def vrai_p(d):
    return expit(-1.8 + 3 * np.exp(-((d - 10) / 5) ** 2) - 0.04 * d)
p_gam = gam.predict(exog=np.ones((len(grille), 1)), exog_smooth=grille[:, None])
tranches = pd.cut(sessions["duree_min"], bins=[0, 3, 5, 7, 9, 11, 13, 15, 18, 22, 36])
pts = sessions.groupby(tranches, observed=True).agg(x=("duree_min", "mean"), y=("achat", "mean"))

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
BLEU, ORANGE, AQUA, VIOLET, GRIS = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#52514e"
ax = axes[0]
ax.scatter(pts["x"], pts["y"], color=GRIS, s=24, zorder=3)
ax.plot(grille, vrai_p(grille), color=GRIS, ls=":", lw=1.3)
for nom, c in [("spline, 3 fonctions de base", ORANGE), ("spline, 6 fonctions de base", BLEU), ("spline, 15 fonctions de base", VIOLET)]:
    ax.plot(grille, courbes[nom], color=c, lw=1.8)
ax.text(24, 0.62, "3 fonctions : trop rigide", color=ORANGE, fontsize=9)
ax.text(24, 0.55, "6 fonctions", color=BLEU, fontsize=9)
ax.text(24, 0.48, "15 fonctions : plus nerveux", color=VIOLET, fontsize=9)
ax.set_xlabel("durée de la session (minutes)"); ax.set_ylabel("probabilité d'achat"); ax.set_title("Splines sans pénalité")
ax = axes[1]
ax.scatter(pts["x"], pts["y"], color=GRIS, s=24, zorder=3, label="fréquence observée (par tranche)")
ax.plot(grille, vrai_p(grille), color=GRIS, ls=":", lw=1.3, label="vérité (connue car simulée)")
ax.plot(grille, p_gam, color=AQUA, lw=2, label=f"GAM pénalisé (edf = {gam.edf.sum() - 1:.1f})")
ax.set_xlabel("durée de la session (minutes)"); ax.set_title("Spline pénalisée (GAM)")
ax.legend(frameon=False, fontsize=8, loc="upper right")
plt.tight_layout()
plt.savefig("figures/ch02-gam-sessions.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
print("sessions de plus de 30 minutes :", int((sessions["duree_min"] > 30).sum()), "sur", len(sessions), "| de moins de 3 minutes :", int((sessions["duree_min"] < 3).sum()))
print("probabilité prédite par le GAM à 35 min :", round(float(p_gam[-1]), 3), "| vraie :", round(float(vrai_p(35.0)), 3))
```
<!--sortie-->
```text
figure enregistrée
sessions de plus de 30 minutes : 10 sur 1500 | de moins de 3 minutes : 33
probabilité prédite par le GAM à 35 min : 0.135 | vraie : 0.039
```

**Étape 5 — Avec R et `mgcv`.** Le paquet de référence choisit $\lambda$ par REML et donne des intervalles de confiance.

```r
suppressPackageStartupMessages(library(mgcv))
sessions <- read.csv("donnees/ch02-sessions.csv")
m <- gam(achat ~ s(duree_min), family = binomial, data = sessions, method = "REML")
print(summary(m))
```
<!--sortie-->
```text

Family: binomial 
Link function: logit 

Formula:
achat ~ s(duree_min)

Parametric coefficients:
            Estimate Std. Error z value Pr(>|z|)    
(Intercept)  -0.4779     0.0696  -6.867 6.58e-12 ***
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

Approximate significance of smooth terms:
             edf Ref.df Chi.sq p-value    
s(duree_min) 6.5  7.429  243.6  <2e-16 ***
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1

R-sq.(adj) =  0.211   Deviance explained = 17.5%
-REML = 858.59  Scale est. = 1         n = 1500
```
```r hide
grille <- data.frame(duree_min = seq(1, 35, length.out = 200))
p <- predict(m, grille, type = "link", se.fit = TRUE)
vrai <- plogis(-1.8 + 3 * exp(-((grille$duree_min - 10) / 5)^2) - 0.04 * grille$duree_min)
tranche <- cut(sessions$duree_min, breaks = c(0, 3, 5, 7, 9, 11, 13, 15, 18, 22, 36))
pts <- aggregate(cbind(duree_min, achat) ~ tranche, data = sessions, FUN = mean)

png("figures/ch02-gam-mgcv.png", width = 1300, height = 800, res = 200)
par(mar = c(4.2, 4.2, 2.2, 0.8))
plot(grille$duree_min, plogis(p$fit), type = "n", ylim = c(0, 0.85), xlab = "durée de la session (minutes)",
     ylab = "probabilité d'achat", main = "GAM (mgcv, REML) avec intervalle de confiance à 95 %")
polygon(c(grille$duree_min, rev(grille$duree_min)), c(plogis(p$fit - 1.96 * p$se.fit), rev(plogis(p$fit + 1.96 * p$se.fit))),
        col = "#cde2fb", border = NA)
lines(grille$duree_min, plogis(p$fit), col = "#2a78d6", lwd = 2)
lines(grille$duree_min, vrai, col = "#52514e", lty = 3, lwd = 1.5)
points(pts$duree_min, pts$achat, pch = 16, col = "#52514e")
invisible(legend("topright", legend = c("GAM ajusté", "intervalle à 95 %", "vérité (simulée)", "fréquences observées"),
                 lty = c(1, NA, 3, NA), pch = c(NA, 15, NA, 16), col = c("#2a78d6", "#cde2fb", "#52514e", "#52514e"), bty = "n", cex = 0.8))
invisible(dev.off())
cat("figure enregistrée\n")
dans_bande <- vrai >= plogis(p$fit - 1.96 * p$se.fit) & vrai <= plogis(p$fit + 1.96 * p$se.fit)
cat("part de la grille où la vraie courbe est dans la bande :", round(mean(dans_bande), 3), "\n")
```
<!--sortie-->
```text
figure enregistrée
part de la grille où la vraie courbe est dans la bande : 1 
```

**Étape 6 — Tester la linéarité de l'âge** dans le modèle de rachat : comparez le modèle linéaire et le modèle `s(age)`.

```r
library(mgcv)
clients <- read.csv("donnees/clients.csv")
clients$canal <- factor(clients$canal_acquisition, levels = c("Boutique", "Réseaux", "Site"))
lineaire <- gam(rachat_12m ~ offre_bienvenue + canal + age, family = binomial, data = clients, method = "REML")
souple <- gam(rachat_12m ~ offre_bienvenue + canal + s(age), family = binomial, data = clients, method = "REML")
print(round(summary(souple)$s.table, 3))
print(anova(lineaire, souple, test = "Chisq"))
print(AIC(lineaire, souple))
```
<!--sortie-->
```text
         edf Ref.df Chi.sq p-value
s(age) 1.579  1.971  13.87   0.001
Analysis of Deviance Table

Model 1: rachat_12m ~ offre_bienvenue + canal + age
Model 2: rachat_12m ~ offre_bienvenue + canal + s(age)
  Resid. Df Resid. Dev    Df Deviance Pr(>Chi)
1    1995.0     2710.8                        
2    1993.6     2709.4 1.364   1.4133   0.3311
               df     AIC
lineaire 5.000000 2720.83
souple   5.971442 2721.36
```

### Application 2.8 — Zéros en excès, Tweedie et modèle à deux parties

*Section du livre : 2.6.* **Objectif** : simuler un ZIP, voir que nos comptages n'ont pas d'excès de zéros mais de la surdispersion, voir un cas où l'inflation est réelle, estimer la puissance de Tweedie et comparer Tweedie au modèle à deux parties.

**Étape 1 — Un ZIP simulé** : comparez probabilité de zéro, moyenne et variance à la théorie.

```python
rng = np.random.default_rng(26)
pi, mu = 0.2, 3.0
actif = rng.random(400_000) >= pi
y = np.where(actif, rng.poisson(mu, 400_000), 0)
print(f"ZIP simulé    : P(0) = {np.mean(y == 0):.4f} | moyenne = {y.mean():.3f} | variance = {y.var():.3f} | variance / moyenne = {y.var() / y.mean():.3f}")
print(f"ZIP théorique : P(0) = {pi + (1 - pi) * np.exp(-mu):.4f} | moyenne = {(1 - pi) * mu:.3f} | variance = {(1 - pi) * mu * (1 + pi * mu):.3f} | variance / moyenne = {1 + pi * mu:.3f}")
print(f"Poisson(3)    : P(0) = {np.exp(-mu):.4f}")
```
<!--sortie-->
```text
ZIP simulé    : P(0) = 0.2407 | moyenne = 2.398 | variance = 3.836 | variance / moyenne = 1.600
ZIP théorique : P(0) = 0.2398 | moyenne = 2.400 | variance = 3.840 | variance / moyenne = 1.600
Poisson(3)    : P(0) = 0.0498
```

**Étape 2 — Nos comptages ont-ils des zéros en trop ?** Poisson, ZIP, binomiale négative, ZINB.

```python
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])
X = sm.add_constant(pd.get_dummies(clients[["age", "canal"]], drop_first=True, dtype=float))
y_c = clients["nb_commandes_an"]
infl = np.ones((len(clients), 1))

poi = sm.Poisson(y_c, X).fit(disp=0)
zip_ = sm.ZeroInflatedPoisson(y_c, X, exog_infl=infl).fit(disp=0, maxiter=300)
nb = sm.NegativeBinomial(y_c, X).fit(disp=0)
zinb = sm.ZeroInflatedNegativeBinomialP(y_c, X, exog_infl=infl, p=2).fit(disp=0, maxiter=500)

lignes = []
for nom, r in [("Poisson", poi), ("ZIP", zip_), ("binomiale négative", nb), ("ZINB", zinb)]:
    pi_hat = float(expit(r.params["inflate_const"])) if "inflate_const" in r.params.index else 0.0
    lignes.append({"modèle": nom, "paramètres": len(r.params), "log-vraisemblance": r.llf, "AIC": r.aic, "pi estimé": pi_hat})
print(pd.DataFrame(lignes).round(4).to_string(index=False))
print()
print("part de zéros observée :", round(float((y_c == 0).mean()), 4))
print("alpha (NB) =", round(float(nb.params["alpha"]), 3), "| alpha (ZINB) =", round(float(zinb.params["alpha"]), 3))
```
<!--sortie-->
```text
            modèle  paramètres  log-vraisemblance        AIC  pi estimé
           Poisson           4         -5853.0778 11714.1557     0.0000
               ZIP           5         -5536.1403 11082.2806     0.1181
binomiale négative           5         -4878.4227  9766.8453     0.0000
              ZINB           6         -4878.4227  9768.8453     0.0000

part de zéros observée : 0.13
alpha (NB) = 0.584 | alpha (ZINB) = 0.584
```

**Étape 3 — Un cas où l'inflation est réelle** : 25 % de comptes dormants.

```python
rng = np.random.default_rng(27)
n = 1500
x = rng.normal(size=n)
dormant = rng.random(n) < 0.25
y_sim = np.where(dormant, 0, rng.poisson(np.exp(0.9 + 0.4 * x)))
Xs = sm.add_constant(pd.DataFrame({"x": x}))
inf1 = np.ones((n, 1))

poi_s = sm.Poisson(y_sim, Xs).fit(disp=0)
nb_s = sm.NegativeBinomial(y_sim, Xs).fit(disp=0)
zip_s = sm.ZeroInflatedPoisson(y_sim, Xs, exog_infl=inf1).fit(disp=0, maxiter=300)

print("part de zéros observée :", round(float((y_sim == 0).mean()), 3), "| part de dormants simulée :", round(float(dormant.mean()), 3))
for nom, r in [("Poisson", poi_s), ("binomiale négative", nb_s), ("ZIP", zip_s)]:
    print(f"{nom:20s}: AIC = {r.aic:8.1f}")
print()
print("ZIP : pi estimé =", round(float(expit(zip_s.params["inflate_const"])), 3), "| proportion réellement simulée de dormants :", round(float(dormant.mean()), 3), "(probabilité programmée : 0.25)")
print("ZIP : coefficients du comptage (const, x) =", zip_s.params[["const", "x"]].round(3).to_numpy(), "(vrais : 0.9, 0.4)")
print("binomiale négative : coefficients (const, x) =", nb_s.params[["const", "x"]].round(3).to_numpy(), "| alpha =", round(float(nb_s.params["alpha"]), 3))
```
<!--sortie-->
```text
part de zéros observée : 0.316 | part de dormants simulée : 0.23
Poisson             : AIC =   5786.0
binomiale négative  : AIC =   5505.3
ZIP                 : AIC =   5292.1

ZIP : pi estimé = 0.233 | proportion réellement simulée de dormants : 0.23 (probabilité programmée : 0.25)
ZIP : coefficients du comptage (const, x) = [0.871 0.418] (vrais : 0.9, 0.4)
binomiale négative : coefficients (const, x) = [0.606 0.407] | alpha = 0.448
```

**Étape 4 — La loi de Tweedie** : vérifiez par simulation la probabilité de zéro, la moyenne et la variance pour deux valeurs de $\mu$.

```python
rng = np.random.default_rng(28)
p_tw, phi_tw, N = 1.5, 20.0, 400_000
lignes = []
for mu_tw in (50.0, 200.0):
    lam = mu_tw ** (2 - p_tw) / (phi_tw * (2 - p_tw))
    alpha = (2 - p_tw) / (p_tw - 1)
    theta = phi_tw * (p_tw - 1) * mu_tw ** (p_tw - 1)
    n_cmd = rng.poisson(lam, N)
    y_tw = np.where(n_cmd > 0, rng.gamma(np.maximum(n_cmd, 1) * alpha, theta), 0.0)
    lignes.append({"moyenne mu": mu_tw, "lambda": lam, "forme alpha": alpha, "échelle theta": theta,
                   "P(0) simulé": np.mean(y_tw == 0), "P(0) = exp(-lambda)": np.exp(-lam),
                   "moyenne simulée": y_tw.mean(), "variance simulée": y_tw.var(), "phi * mu^p": phi_tw * mu_tw ** p_tw})
print(pd.DataFrame(lignes).round(3).T.to_string(header=False))
```
<!--sortie-->
```text
moyenne mu             50.000    200.000
lambda                  0.707      1.414
forme alpha             1.000      1.000
échelle theta          70.711    141.421
P(0) simulé             0.492      0.243
P(0) = exp(-lambda)     0.493      0.243
moyenne simulée        49.984    200.039
variance simulée     7048.066  56394.773
phi * mu^p           7071.068  56568.542
```

**Étape 5 — Estimer la puissance $p$ avec R (`mgcv`).**

```r
suppressPackageStartupMessages(library(mgcv))
clients <- read.csv("donnees/clients.csv")
clients$canal <- factor(clients$canal_acquisition, levels = c("Boutique", "Réseaux", "Site"))
f <- depense_annuelle ~ age + canal + offre_bienvenue

puissances <- c(1.2, 1.3, 1.4, 1.45, 1.5, 1.6, 1.7, 1.8)
logv <- sapply(puissances, function(p) as.numeric(logLik(gam(f, family = Tweedie(p = p, link = "log"), data = clients, method = "REML"))))
print(data.frame(p = puissances, log_vraisemblance = round(logv, 1)))

m <- gam(f, family = tw(), data = clients, method = "REML")          # tw() estime p en même temps que les coefficients
p_hat <- m$family$getTheta(TRUE)
cat("puissance p estimée :", round(p_hat, 3), "| dispersion phi :", round(m$scale, 2), "\n")
print(round(summary(m)$p.table, 4))

mu <- fitted(m)
zeros_pred <- mean(exp(-mu^(2 - p_hat) / (m$scale * (2 - p_hat))))
cat("part de zéros prédite par le modèle de Tweedie :", round(zeros_pred, 3), "| observée :", round(mean(clients$depense_annuelle == 0), 3), "\n")
```
<!--sortie-->
```text
     p log_vraisemblance
1 1.20          -12492.1
2 1.30          -12352.9
3 1.40          -12304.5
4 1.45          -12299.8
5 1.50          -12306.0
6 1.60          -12352.6
7 1.70          -12460.1
8 1.80          -12680.0
puissance p estimée : 1.447 | dispersion phi : 19.78 
                Estimate Std. Error  t value Pr(>|t|)
(Intercept)       5.4730     0.0877  62.4383   0.0000
age               0.0081     0.0021   3.9372   0.0001
canalRéseaux     -0.5553     0.0547 -10.1570   0.0000
canalSite        -0.1509     0.0542  -2.7858   0.0054
offre_bienvenue  -0.0142     0.0435  -0.3260   0.7444
part de zéros prédite par le modèle de Tweedie : 0.153 | observée : 0.13 
```

**Étape 6 — Tweedie contre modèle à deux parties** (logistique $\times$ Gamma) : moyennes par canal, calibration par dixième, part de zéros prédite.

```python
f_rhs = "age + canal + offre_bienvenue"
clients["achete"] = (clients["depense_annuelle"] > 0).astype(int)
partie1 = smf.glm("achete ~ " + f_rhs, clients, family=sm.families.Binomial()).fit()
acheteurs = clients[clients["achete"] == 1]
partie2 = smf.glm("depense_annuelle ~ " + f_rhs, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
mu_deux = partie1.predict(clients) * partie2.predict(clients)                  # E[Y|x] = P(achète|x) × E[montant|achète, x]

tw = smf.glm("depense_annuelle ~ " + f_rhs, clients, family=sm.families.Tweedie(var_power=1.45, link=sm.families.links.Log())).fit(scale="X2")
mu_tw = tw.fittedvalues

print("coefficients de Tweedie (p = 1,45) :", tw.params.round(4).to_dict())
print()
tab = pd.DataFrame({"observée": clients.groupby("canal", observed=True)["depense_annuelle"].mean(),
                    "Tweedie": mu_tw.groupby(clients["canal"], observed=True).mean(),
                    "deux parties": mu_deux.groupby(clients["canal"], observed=True).mean()})
tab.loc["tous les clients"] = [clients["depense_annuelle"].mean(), mu_tw.mean(), mu_deux.mean()]
print(tab.round(1).to_string())
```
<!--sortie-->
```text
coefficients de Tweedie (p = 1,45) : {'Intercept': 5.4729, 'canal[T.Réseaux]': -0.5553, 'canal[T.Site]': -0.151, 'age': 0.0081, 'offre_bienvenue': -0.0142}

                  observée  Tweedie  deux parties
canal                                            
Boutique             316.3    316.7         317.2
Réseaux              182.5    182.8         183.0
Site                 272.9    272.3         271.7
tous les clients     247.0    247.0         247.0
```

**Calibration** : on compare enfin, par dixième de dépense prédite, les deux modèles à la dépense observée, et la part de zéros prédite.

```python
# calibration par dixième de dépense prédite
classes = pd.qcut(mu_deux, 10, labels=False)
dec = pd.DataFrame({"observée": clients["depense_annuelle"], "Tweedie": mu_tw, "deux parties": mu_deux, "dixième": classes}).groupby("dixième").mean()
print()
print(dec.round(1).to_string())
print()
print("écart absolu moyen, par dixième : Tweedie =", round(float((dec["Tweedie"] - dec["observée"]).abs().mean()), 2),
      "| deux parties =", round(float((dec["deux parties"] - dec["observée"]).abs().mean()), 2))
print("part de zéros prédite par le modèle à deux parties :", round(float(1 - partie1.fittedvalues.mean()), 3))
```
<!--sortie-->
```text

         observée  Tweedie  deux parties
dixième                                 
0           170.6    163.0         162.4
1           173.0    175.8         175.7
2           199.4    186.9         187.4
3           192.2    202.6         203.7
4           205.4    244.2         243.5
5           268.8    266.7         266.1
6           316.1    280.3         280.0
7           280.8    294.8         294.7
8           338.7    313.1         313.3
9           331.8    345.3         345.9

écart absolu moyen, par dixième : Tweedie = 16.3 | deux parties = 16.49
part de zéros prédite par le modèle à deux parties : 0.13
```

### Application 2.9 — La vérité dévoilée

*Section du livre : bilan du chapitre.* **Objectif** : comparer, pour les trois modèles du chapitre (rachat, commandes, dépense), les estimations à la vérité programmée dans `build/donnees2.py`, en erreurs-types, puis expliquer l'écart apparent sur le nombre de commandes par canal.

```python
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])

# (1) rachat : logistique (vérité sur l'échelle du logit, canal relatif à la boutique)
logi = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
# (2) nombre de commandes : binomiale négative (log de la moyenne)
nbm = smf.negativebinomial("nb_commandes_an ~ offre_bienvenue + age + canal", clients).fit(disp=0)
# (3) dépense moyenne de tous les clients : Tweedie p = 1,45 (log de la moyenne)
twd = smf.glm("depense_annuelle ~ offre_bienvenue + age + canal", clients, family=sm.families.Tweedie(var_power=1.45, link=sm.families.links.Log())).fit(scale="X2")
```

**Les écarts à la vérité**, estimation par estimation, pour les trois modèles :

```python
verite = {
    "rachat (logit)": (logi, {"offre_bienvenue": 0.55, "age": -0.015, "canal[T.Réseaux]": -0.30, "canal[T.Site]": -0.30}),
    "commandes (log moyenne)": (nbm, {"offre_bienvenue": 0.0, "age": -0.005, "canal[T.Réseaux]": -0.05, "canal[T.Site]": 0.10}),
    "dépense (log moyenne)": (twd, {"offre_bienvenue": 0.0, "age": 0.003, "canal[T.Réseaux]": -0.39, "canal[T.Site]": -0.07}),
}
lignes = []
for nom, (res, vrai) in verite.items():
    for param, v in vrai.items():
        est, se = float(res.params[param]), float(res.bse[param])
        lignes.append({"modèle": nom, "paramètre": param, "estimation": est, "erreur-type": se, "vérité": v, "écart (en erreurs-types)": (est - v) / se})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
print()
print("alpha (binomiale négative) :", round(float(nbm.params["alpha"]), 3), "| IC95 % :", nbm.conf_int().loc["alpha"].round(3).tolist())
```
<!--sortie-->
```text
                 modèle        paramètre  estimation  erreur-type  vérité  écart (en erreurs-types)
         rachat (logit)  offre_bienvenue       0.493        0.091   0.550                    -0.624
         rachat (logit)              age      -0.015        0.004  -0.015                    -0.114
         rachat (logit) canal[T.Réseaux]      -0.463        0.116  -0.300                    -1.411
         rachat (logit)    canal[T.Site]      -0.168        0.120  -0.300                     1.106
commandes (log moyenne)  offre_bienvenue      -0.016        0.041   0.000                    -0.379
commandes (log moyenne)              age      -0.001        0.002  -0.005                     1.938
commandes (log moyenne) canal[T.Réseaux]      -0.176        0.052  -0.050                    -2.430
commandes (log moyenne)    canal[T.Site]       0.015        0.053   0.100                    -1.597
  dépense (log moyenne)  offre_bienvenue      -0.014        0.051   0.000                    -0.277
  dépense (log moyenne)              age       0.008        0.002   0.003                     2.112
  dépense (log moyenne) canal[T.Réseaux]      -0.555        0.064  -0.390                    -2.570
  dépense (log moyenne)    canal[T.Site]      -0.151        0.064  -0.070                    -1.270

alpha (binomiale négative) : 0.584 | IC95 % : [0.528, 0.639]
```

**Un contrôle de plus** : les moyennes par canal du nombre de commandes sont-elles conformes à la vérité programmée ?

```python
# Écarts du modèle « commandes » : les moyennes par canal sont-elles conformes à la vérité programmée ?
var_f = 0.22 ** 2 + 0.10 ** 2 + 2 * 0.22 * 0.10 * 0.3                          # variance de 0,22 F1 + 0,10 F2
eff_canal = {"Boutique": 0.05, "Réseaux": 0.0, "Site": 0.15}
lignes = []
for canal, e in eff_canal.items():
    g = clients[clients["canal"] == canal]["nb_commandes_an"]
    ages = clients.loc[clients["canal"] == canal, "age"]
    attendu = np.exp(1.25 + e + var_f / 2) * np.mean(np.exp(-0.005 * (ages - 36)))   # E[N] sous la vérité programmée
    lignes.append({"canal": canal, "clients": len(g), "commandes attendues": attendu, "commandes observées": g.mean(),
                   "écart (en erreurs-types de la moyenne)": (g.mean() - attendu) / (g.std() / np.sqrt(len(g)))})
print()
print(pd.DataFrame(lignes).round(3).to_string(index=False))
print()
print("hétérogénéité attendue : (1 + 0,5) × (1 + variance relative de exp(0,22 F1 + 0,10 F2)) - 1 =", round((1 + 0.5) * np.exp(0.22 ** 2 + 0.10 ** 2 + 2 * 0.22 * 0.10 * 0.3) - 1, 3))
```
<!--sortie-->
```text

   canal  clients  commandes attendues  commandes observées  écart (en erreurs-types de la moyenne)
Boutique      504                3.818                4.137                                   1.930
 Réseaux      816                3.620                3.464                                  -1.293
    Site      680                4.219                4.197                                  -0.154

hétérogénéité attendue : (1 + 0,5) × (1 + variance relative de exp(0,22 F1 + 0,10 F2)) - 1 = 0.611
```

## Exercices

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse ou démonstration.

### Exercice 2.1 ⭐ — Cotes et logit (section 2.2.1–2.2.2 du livre)

(a) Un client a une probabilité de rachat de $0{,}8$ : quelle est sa cote, quel est son logit ? (b) Un modèle logistique donne $\operatorname{logit}(p)=-0{,}4+0{,}9\,x$, où $x$ est le nombre de commandes passées l'an dernier. Calculez $p$ pour $x=0,1,2$. (c) Quel est le rapport de cotes associé à une commande de plus ? De combien de points de pourcentage la probabilité augmente-t-elle de $x=0$ à $x=1$, puis de $x=1$ à $x=2$ ? Pourquoi ne sont-ils pas égaux ?

### Exercice 2.2 ⭐ — Rapport de cotes, risque relatif (section 2.2.3 du livre)

Sur 200 clients abonnés à la newsletter, 60 ont acheté ; sur 300 clients non abonnés, 45 ont acheté. Calculez à la main la différence de risque, le risque relatif et le rapport de cotes, puis un intervalle de confiance à 95 % de ce dernier (erreur-type du log-OR : $\sqrt{1/a+1/b+1/c+1/d}$). Vérifiez avec une régression logistique.

### Exercice 2.3 ⭐ — Régression de Poisson (section 2.3.1 du livre)

Un modèle de Poisson pour le nombre de commandes annuelles donne $\log\mu=1{,}2-0{,}01\times\text{âge}+0{,}2\times\text{site}$ (la variable « site » vaut 1 pour un client acquis par le site, 0 pour la boutique). (a) Nombre moyen de commandes d'un client de 40 ans acquis par le site, et d'un client de 40 ans acquis en boutique. (b) Par quel facteur le nombre moyen est-il multiplié pour 10 ans de plus ? (c) Probabilité qu'un client de 40 ans acquis par le site ne passe **aucune** commande, si la loi de Poisson est correcte.

### Exercice 2.4 ⭐⭐ — IRLS à la main (section 2.1.5 du livre)

Trois clients : $x=(0,1,2)$ et $y=(1,3,5)$ commandes. On ajuste un modèle de Poisson, $\log\mu=\beta_0+\beta_1x$. (a) À partir de $\beta^{(0)}=(0,0)$, calculez à la main **une itération** d'IRLS (poids, réponse de travail, régression pondérée). (b) Écrivez le code complet de l'algorithme jusqu'à convergence et comparez à `statsmodels`.

### Exercice 2.5 ⭐⭐ — Déviance et rapport de vraisemblance (section 2.4.1–2.4.2 du livre)

Avec les données de l'exercice 2.4 : (a) calculez à la main la déviance du modèle **sans variable** ($\hat\mu=\bar y$) et la statistique de Pearson. (b) Quelle est la déviance du modèle avec $x$ ? Testez, par le rapport de vraisemblance, l'utilité de $x$ (1 degré de liberté).

### Exercice 2.6 ⭐⭐ — Décalage (section 2.3.2 du livre)

Trois transporteurs ont livré des colis et enregistré des retards : A a livré 200 milliers de colis pour 30 retards ; B, 50 milliers pour 12 retards ; C, 400 milliers pour 40 retards. (a) Calculez les taux de retard par millier de colis et les rapports de taux B/A et C/A. (b) Ajustez une régression de Poisson avec et sans décalage (*offset*) : que concluriez-vous dans chaque cas ?

### Exercice 2.7 ⭐⭐ — Surdispersion (section 2.3.3 du livre)

Une régression de Poisson, sur $n=305$ clients avec 5 paramètres, donne une statistique de Pearson $X^2=540$. Le coefficient de la variable « Réseaux » est $0{,}30$ avec une erreur-type de $0{,}12$. (a) Estimez la dispersion $\hat\phi$. (b) Corrigez l'erreur-type et la statistique $z$. La conclusion change-t-elle au seuil de 5 % ?

### Exercice 2.8 ⭐⭐ — Régression sur $\log y$ (section 2.3.4 du livre)

On régresse le logarithme des dépenses sur des variables explicatives ; pour un client donné, le modèle prédit $\log\hat y=5{,}0$ et l'écart-type résiduel est $\hat\sigma=0{,}9$. (a) Que vaut $e^{5{,}0}$ ? Est-ce la dépense moyenne prévue ? (b) Si les résidus sont normaux, quelle est la dépense moyenne prévue ? Vérifiez par simulation.

### Exercice 2.9 ⭐⭐ — Comparer des modèles (section 2.4.5 du livre)

Les déviances de trois modèles de rachat sont $D_{\text{complet}}=2\,710{,}83$ (offre, âge, canal : 5 paramètres), $D_{\text{sans offre}}=2\,740{,}47$ (4 paramètres) et $D_{\text{sans canal}}=2\,728{,}57$ (3 paramètres), pour $n=2\,000$. (a) Testez par le rapport de vraisemblance l'utilité de l'offre, puis du canal. (b) Calculez la différence d'AIC et de BIC dans chaque cas. Les critères s'accordent-ils avec les tests ?

### Exercice 2.10 ⭐⭐⭐ — Sur les données : la ville (section 2.4.2 du livre)

Le fichier `clients.csv` contient la ville de chaque client. La ville améliore-t-elle le modèle de rachat `offre + âge + canal` ? Utilisez le test du rapport de vraisemblance, l'AIC et le BIC, et interprétez.

### Exercice 2.11 ⭐⭐ — Choisir un seuil (section 2.2.8 du livre)

Avec le modèle de rachat enrichi des notes de l'enquête (section 2.2.7), trouvez le seuil qui maximise l'**indice de Youden** $J=\text{sensibilité}+\text{spécificité}-1$, et comparez-le au seuil de 0,5.

### Exercice 2.12 ⭐⭐ — GAM : choisir la souplesse (section 2.5.2 du livre)

Sur les sessions de navigation (`ch02-sessions.csv`), ajustez des régressions logistiques sur des B-splines de 4 à 12 fonctions de base et choisissez le nombre qui minimise l'AIC. Quel est l'avantage de la pénalisation sur cette recherche ?

### Exercice 2.13 ⭐⭐ — Zéros en excès (section 2.6.1 du livre)

Dans un modèle ZIP de moyenne de la partie Poisson $\mu=4$, quelle probabilité d'inflation $\pi$ donne un rapport variance/moyenne égal à 2 ? Quelle est alors la probabilité d'observer un zéro ? Vérifiez par simulation.

### Exercice 2.14 ⭐⭐⭐ — Démonstration et Tweedie (section 2.1.3, 2.6.3 du livre)

(a) Montrez que la loi Gamma de moyenne $\mu$ et de forme $\nu$ appartient à la famille exponentielle, avec $\theta=-1/\mu$, $b(\theta)=-\log(-\theta)$ et $\phi=1/\nu$, et retrouvez $\mathrm{Var}(Y)=\mu^2/\nu$ avec la proposition de 2.1.3. (b) Pour une loi de Tweedie de moyenne $\mu=100$, $\phi=15$, $p=1{,}3$, calculez la probabilité de zéro, puis les paramètres $(\lambda,\alpha,\theta)$ de la somme Poisson-Gamma correspondante, et vérifiez par simulation.


## Corrigés

### Corrigé 2.1

(a) Cote $=0{,}8/0{,}2=4$ ; logit $=\log4\approx1{,}386$. (b) $p(0)=\operatorname{expit}(-0{,}4)=0{,}401$ ; $p(1)=\operatorname{expit}(0{,}5)=0{,}622$ ; $p(2)=\operatorname{expit}(1{,}4)=0{,}802$. (c) Le rapport de cotes est $e^{0{,}9}=2{,}46$ pour une commande de plus. La probabilité augmente de $22{,}1$ points puis de $18{,}0$ points : l'effet est **constant sur le logit** mais pas sur la probabilité (il est maximal autour de $p=0{,}5$ et diminue quand on s'en éloigne : 2.2.2).

```python
print("cote =", 0.8 / 0.2, "| logit =", round(float(np.log(4)), 4))
p_x = expit(-0.4 + 0.9 * np.array([0, 1, 2]))
print("probabilités :", p_x.round(4), "| OR =", round(float(np.exp(0.9)), 4))
print("gains en points :", (100 * np.diff(p_x)).round(2))
```
<!--sortie-->
```text
cote = 4.0 | logit = 1.3863
probabilités : [0.4013 0.6225 0.8022] | OR = 2.4596
gains en points : [22.11 17.97]
```

### Corrigé 2.2

$\hat p_1=60/200=0{,}30$ et $\hat p_0=45/300=0{,}15$. Différence de risque $=0{,}15$ (15 points) ; risque relatif $=0{,}30/0{,}15=2{,}0$ ; rapport de cotes $=\dfrac{0{,}30/0{,}70}{0{,}15/0{,}85}=\dfrac{0{,}4286}{0{,}1765}=2{,}43$. Erreur-type du log-OR : $\sqrt{\frac1{60}+\frac1{140}+\frac1{45}+\frac1{255}}=0{,}2235$ ; intervalle de $\log$ OR : $0{,}887\pm1{,}96\times0{,}2235$, soit $[0{,}449;\ 1{,}325]$, donc OR dans $[1{,}57;\ 3{,}76]$. Le RR (2,0) est plus petit que l'OR (2,43) : l'OR exagère le risque relatif car l'événement n'est pas rare (15 % à 30 %).

```python
a, b, c, d = 60, 140, 45, 255                              # avec : achat / non-achat ; sans : achat / non-achat
p1, p0 = a / (a + b), c / (c + d)
or_ = (a * d) / (b * c)
se = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)
print(f"différence de risque = {p1 - p0:.3f} | RR = {p1 / p0:.3f} | OR = {or_:.4f}")
print(f"IC95 % de l'OR : [{np.exp(np.log(or_) - 1.96 * se):.3f} ; {np.exp(np.log(or_) + 1.96 * se):.3f}]  (erreur-type du log-OR = {se:.4f})")
tab2 = pd.DataFrame({"newsletter": [1] * 200 + [0] * 300, "achat": [1] * 60 + [0] * 140 + [1] * 45 + [0] * 255})
m2 = smf.glm("achat ~ newsletter", tab2, family=sm.families.Binomial()).fit()
print("régression logistique : OR =", round(float(np.exp(m2.params["newsletter"])), 4), "| IC95 % :", np.exp(m2.conf_int().loc["newsletter"]).round(3).tolist())
```
<!--sortie-->
```text
différence de risque = 0.150 | RR = 2.000 | OR = 2.4286
IC95 % de l'OR : [1.567 ; 3.764]  (erreur-type du log-OR = 0.2235)
régression logistique : OR = 2.4286 | IC95 % : [1.567, 3.764]
```

### Corrigé 2.3

(a) Site, 40 ans : $\mu=e^{1{,}2-0{,}4+0{,}2}=e^{1{,}0}=2{,}718$ commandes ; boutique : $e^{0{,}8}=2{,}226$. (b) Pour 10 ans de plus : $e^{-0{,}1}=0{,}905$, soit 9,5 % de commandes en moins. Le site est associé à $e^{0{,}2}=1{,}221$ fois plus de commandes que la boutique. (c) $P(Y=0)=e^{-\mu}=e^{-2{,}718}=0{,}066$ : 6,6 % de zéros attendus (sous Poisson).

```python
mu_site, mu_boutique = np.exp(1.2 - 0.01 * 40 + 0.2), np.exp(1.2 - 0.01 * 40)
print("moyennes (site, boutique) :", round(float(mu_site), 3), round(float(mu_boutique), 3))
print("facteur pour +10 ans :", round(float(np.exp(-0.1)), 4), "| facteur site/boutique :", round(float(np.exp(0.2)), 4))
print("P(Y = 0 | site, 40 ans) =", round(float(stats.poisson.pmf(0, mu_site)), 4))
```
<!--sortie-->
```text
moyennes (site, boutique) : 2.718 2.226
facteur pour +10 ans : 0.9048 | facteur site/boutique : 1.2214
P(Y = 0 | site, 40 ans) = 0.066
```

### Corrigé 2.4

(a) Avec $\beta^{(0)}=(0,0)$ : $\eta=0$, $\mu=e^0=1$ pour tous, donc $W_i=\mu_i=1$ (pour Poisson avec lien log, $W=\mu$) et $z_i=\eta_i+(y_i-\mu_i)/\mu_i=(0,2,4)$. La régression de $z$ sur $x$ (poids tous égaux à 1) a pour pente $\frac{\sum(x-1)(z-2)}{\sum(x-1)^2}=\frac{(-1)(-2)+0+(1)(2)}{2}=2$ et pour ordonnée $\bar z-2\bar x=2-2=0$ : donc $\beta^{(1)}=(0;\ 2)$. (b) La deuxième itération, avec $\mu=(1;\,e^2;\,e^4)$, donne déjà des valeurs bien plus raisonnables ; l'algorithme converge en quelques pas (voir le code).

```python
x4 = np.array([0.0, 1, 2]); y4 = np.array([1.0, 3, 5])
X4 = np.column_stack([np.ones(3), x4])
beta = np.zeros(2)
for it in range(1, 9):
    eta = X4 @ beta
    mu = np.exp(eta)
    w = mu                                           # poids de Poisson (lien log)
    z = eta + (y4 - mu) / mu                          # réponse de travail
    beta = np.linalg.solve(X4.T @ (w[:, None] * X4), X4.T @ (w * z))
    if it <= 4:
        print(f"itération {it} : beta = {beta.round(5)}")
m4 = sm.GLM(y4, X4, family=sm.families.Poisson()).fit()
print("après 8 itérations :", beta.round(6), "| statsmodels :", m4.params.round(6))
```
<!--sortie-->
```text
itération 1 : beta = [0. 2.]
itération 2 : beta = [-0.17925  1.63377]
itération 3 : beta = [0.00434 1.15568]
itération 4 : beta = [0.1661  0.82978]
après 8 itérations : [0.207929 0.723349] | statsmodels : [0.207929 0.723349]
```

### Corrigé 2.5

(a) Sans variable, $\hat\mu=3$ : $D=2\big[1\log\frac13+3\log1+5\log\frac53-(9-9)\big]=2[-1{,}0986+0+2{,}5541]=2{,}911$ ; Pearson $=\frac{(1-3)^2+0+(5-3)^2}{3}=2{,}667$. (b) La déviance du modèle avec $x$, calculée ci-dessous, est beaucoup plus petite : la différence $D_0-D_1$ se compare à $\chi^2_1$.

```python
mu0 = np.full(3, y4.mean())
d0 = 2 * np.sum(y4 * np.log(y4 / mu0) - (y4 - mu0))
print("déviance sans variable :", round(float(d0), 4), "| Pearson :", round(float(np.sum((y4 - mu0) ** 2 / mu0)), 4))
m0 = sm.GLM(y4, np.ones((3, 1)), family=sm.families.Poisson()).fit()
print("statsmodels : déviance nulle =", round(float(m0.deviance), 4), "| déviance avec x =", round(float(m4.deviance), 4))
delta = m0.deviance - m4.deviance
print(f"rapport de vraisemblance : {delta:.4f} sur 1 ddl, p = {stats.chi2.sf(delta, 1):.4f}")
```
<!--sortie-->
```text
déviance sans variable : 2.911 | Pearson : 2.6667
statsmodels : déviance nulle = 2.911 | déviance avec x = 0.1363
rapport de vraisemblance : 2.7748 sur 1 ddl, p = 0.0958
```

La déviance du modèle avec $x$ est de 0,136 : il épouse presque parfaitement les trois points (la pente estimée est $0{,}7233$, soit un facteur $e^{0{,}7233}=2{,}06$ par unité de $x$). La différence $2{,}911-0{,}136=2{,}77$ donne pourtant $p=0{,}096$ : au seuil de 5 %, on **ne rejette pas** l'absence d'effet de $x$. Avec seulement 3 observations, le test a très peu de puissance (et l'approximation par un $\chi^2$ est de toute façon douteuse pour un si petit échantillon) : une pente énorme n'est pas « significative » faute de données.

### Corrigé 2.6

(a) Taux par millier de colis : A $=30/200=0{,}15$ ; B $=12/50=0{,}24$ ; C $=40/400=0{,}10$. Rapports de taux : B/A $=1{,}6$, C/A $=0{,}667$ : B est le transporteur le plus mauvais, C le meilleur. (b) Avec le décalage $\log(\text{exposition})$, le modèle (saturé : 3 paramètres pour 3 transporteurs) reproduit exactement ces rapports. **Sans** décalage, il compare des nombres bruts de retards (30, 12, 40) : il conclut que B a $12/30=0{,}4$ fois les retards de A et C $1{,}33$ fois : un renversement complet, parce que C livre beaucoup plus de colis.

```python
transp = pd.DataFrame({"transporteur": ["A", "B", "C"], "milliers": [200, 50, 400], "retards": [30, 12, 40]})
transp["taux"] = transp["retards"] / transp["milliers"]
print(transp.to_string(index=False))
avec = smf.glm("retards ~ transporteur", transp, family=sm.families.Poisson(), offset=np.log(transp["milliers"])).fit()
sans = smf.glm("retards ~ transporteur", transp, family=sm.families.Poisson()).fit()
print("rapports de taux avec décalage (B/A, C/A) :", np.exp(avec.params[["transporteur[T.B]", "transporteur[T.C]"]]).round(3).tolist())
print("rapports sans décalage (B/A, C/A)         :", np.exp(sans.params[["transporteur[T.B]", "transporteur[T.C]"]]).round(3).tolist())
```
<!--sortie-->
```text
transporteur  milliers  retards  taux
           A       200       30  0.15
           B        50       12  0.24
           C       400       40  0.10
rapports de taux avec décalage (B/A, C/A) : [1.6, 0.667]
rapports sans décalage (B/A, C/A)         : [0.4, 1.333]
```

### Corrigé 2.7

(a) $\hat\phi=X^2/(n-p)=540/(305-5)=1{,}8$. (b) L'erreur-type corrigée est $0{,}12\times\sqrt{1{,}8}=0{,}161$, et $z=0{,}30/0{,}161=1{,}86$ au lieu de $2{,}5$. La p-valeur passe de $0{,}012$ à $0{,}063$ : l'effet est **significatif** à 5 % avec la loi de Poisson, mais **ne l'est plus** après correction. C'est exactement le danger de la surdispersion non corrigée.

```python
phi = 540 / (305 - 5)
se_c = 0.12 * np.sqrt(phi)
z_nc, z_c = 0.30 / 0.12, 0.30 / se_c
print(f"phi = {phi:.2f} | erreur-type corrigée = {se_c:.4f}")
print(f"z non corrigé = {z_nc:.2f} (p = {2 * stats.norm.sf(z_nc):.4f}) | z corrigé = {z_c:.2f} (p = {2 * stats.norm.sf(z_c):.4f})")
```
<!--sortie-->
```text
phi = 1.80 | erreur-type corrigée = 0.1610
z non corrigé = 2.50 (p = 0.0124) | z corrigé = 1.86 (p = 0.0624)
```

### Corrigé 2.8

(a) $e^{5{,}0}=148{,}4$ € : c'est la **médiane** prévue (si les résidus de $\log y$ sont symétriques), pas la moyenne. (b) Pour $\log Y\sim\mathcal N(5;\,0{,}9^2)$, $E[Y]=e^{5+\sigma^2/2}=e^{5+0{,}405}=148{,}4\times1{,}499=222{,}5$ € : la moyenne est **50 % plus grande** que $e^{5}$. Ne pas retransformer sans correction revient à sous-estimer systématiquement la dépense moyenne (2.3.4).

```python
rng = np.random.default_rng(8)
y_sim = rng.lognormal(mean=5.0, sigma=0.9, size=1_000_000)
print("exp(5,0) =", round(float(np.exp(5.0)), 1), "| médiane simulée :", round(float(np.median(y_sim)), 1))
print("exp(5 + sigma²/2) =", round(float(np.exp(5.0 + 0.9 ** 2 / 2)), 1), "| moyenne simulée :", round(float(y_sim.mean()), 1))
```
<!--sortie-->
```text
exp(5,0) = 148.4 | médiane simulée : 148.6
exp(5 + sigma²/2) = 222.5 | moyenne simulée : 222.6
```

### Corrigé 2.9

(a) Offre : $\Delta D=2\,740{,}47-2\,710{,}83=29{,}64$ sur 1 ddl, $p=5{,}2\times10^{-8}$ ; canal : $\Delta D=2\,728{,}57-2\,710{,}83=17{,}74$ sur 2 ddl, $p=1{,}4\times10^{-4}$. Les deux variables sont nécessaires. (b) $\Delta\mathrm{AIC}=\Delta D-2q$ et $\Delta\mathrm{BIC}=\Delta D-q\log n$ (avec $\log2000=7{,}60$) : pour l'offre, $\Delta\mathrm{AIC}=27{,}64$ et $\Delta\mathrm{BIC}=22{,}04$ ; pour le canal, $\Delta\mathrm{AIC}=13{,}74$ et $\Delta\mathrm{BIC}=2{,}54$. Tous les écarts sont positifs : les critères gardent chaque variable, en accord avec les tests ; le BIC est beaucoup moins enthousiaste pour le canal ($+2{,}5$ seulement), qui est le cas le plus marginal.

```python
n = 2000
for nom, d_red, d_comp, q in [("offre", 2740.47, 2710.83, 1), ("canal", 2728.57, 2710.83, 2)]:
    dd = d_red - d_comp
    print(f"{nom:6s}: ΔD = {dd:6.2f} sur {q} ddl | p = {stats.chi2.sf(dd, q):.2e} | ΔAIC = {dd - 2 * q:6.2f} | ΔBIC = {dd - q * np.log(n):6.2f}")
```
<!--sortie-->
```text
offre : ΔD =  29.64 sur 1 ddl | p = 5.20e-08 | ΔAIC =  27.64 | ΔBIC =  22.04
canal : ΔD =  17.74 sur 2 ddl | p = 1.41e-04 | ΔAIC =  13.74 | ΔBIC =   2.54
```

### Corrigé 2.10

Ajoutons la ville (6 modalités, donc 5 paramètres de plus) au modèle de rachat et testons.

```python
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])
base = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
avec_ville = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + C(ville)", clients, family=sm.families.Binomial()).fit()
dd = base.deviance - avec_ville.deviance
print(f"ΔD = {dd:.2f} sur 5 ddl | p (rapport de vraisemblance) = {stats.chi2.sf(dd, 5):.3f}")
print(f"AIC : sans ville = {base.aic:.1f} | avec ville = {avec_ville.aic:.1f} | BIC : sans = {base.bic_llf:.1f} | avec = {avec_ville.bic_llf:.1f}")
ic = avec_ville.conf_int()
print(pd.DataFrame({"OR": np.exp(avec_ville.params), "IC95 bas": np.exp(ic[0]), "IC95 haut": np.exp(ic[1])}).filter(like="ville", axis=0).round(3).to_string())
```
<!--sortie-->
```text
ΔD = 1.13 sur 5 ddl | p (rapport de vraisemblance) = 0.952
AIC : sans ville = 2720.8 | avec ville = 2729.7 | BIC : sans = 2748.8 | avec = 2785.7
                        OR  IC95 bas  IC95 haut
C(ville)[T.Ville A]  0.985     0.687      1.411
C(ville)[T.Ville B]  1.002     0.713      1.407
C(ville)[T.Ville C]  0.901     0.648      1.253
C(ville)[T.Ville D]  1.062     0.774      1.457
C(ville)[T.Ville E]  1.023     0.773      1.354
```

La ville n'améliore pas le modèle : $\Delta D=1{,}13$ pour 5 degrés de liberté ($p=0{,}95$, un résultat parfaitement banal si la ville n'a aucun effet). L'AIC **se dégrade** (de 2 720,8 à 2 729,7) et le BIC encore davantage (de 2 748,8 à 2 785,7) : les cinq paramètres de plus ne rapportent presque rien en vraisemblance. Les rapports de cotes de toutes les villes par rapport à la ville de référence (Autre) sont compris entre 0,90 et 1,06, avec des intervalles de confiance qui contiennent tous 1. **Conclusion : la ville n'a pas d'effet détectable sur le rachat**, et l'on garde le modèle sans elle. (Nous verrons plus bas que, dans la simulation, la ville n'a effectivement aucun rôle.)

### Corrigé 2.11

On balaye les seuils de 0,05 à 0,95 et l'on garde celui qui maximise $J$.

```python
enquete = pd.read_csv("donnees/enquete_satisfaction.csv")
enquete["note_produits"] = enquete[["q1", "q2", "q3", "q4"]].mean(axis=1)
enquete["note_service"] = enquete[["q5", "q6", "q7", "q8"]].mean(axis=1)
rep = clients.merge(enquete[["id_client", "note_produits", "note_service"]], on="id_client")
riche = smf.glm("rachat_12m ~ offre_bienvenue + age + canal + note_produits + note_service", rep, family=sm.families.Binomial()).fit()
yr, sr = rep["rachat_12m"].to_numpy(), riche.fittedvalues.to_numpy()

seuils = np.arange(0.05, 0.96, 0.01)
sens = np.array([((sr >= s) & (yr == 1)).sum() / (yr == 1).sum() for s in seuils])
spec = np.array([((sr < s) & (yr == 0)).sum() / (yr == 0).sum() for s in seuils])
J = sens + spec - 1
k = int(np.argmax(J))
print(f"seuil optimal (Youden) = {seuils[k]:.2f} | sensibilité = {sens[k]:.3f} | spécificité = {spec[k]:.3f} | J = {J[k]:.3f}")
k5 = int(np.argmin(np.abs(seuils - 0.5)))
print(f"seuil 0,50            : sensibilité = {sens[k5]:.3f} | spécificité = {spec[k5]:.3f} | J = {J[k5]:.3f}")
print("part de rachat dans l'échantillon :", round(float(yr.mean()), 3))
```
<!--sortie-->
```text
seuil optimal (Youden) = 0.57 | sensibilité = 0.526 | spécificité = 0.772 | J = 0.298
seuil 0,50            : sensibilité = 0.663 | spécificité = 0.620 | J = 0.283
part de rachat dans l'échantillon : 0.505
```

Le seuil de Youden est de **0,57** : sensibilité 0,526, spécificité 0,772, $J=0{,}298$. Au seuil de 0,5, $J=0{,}283$. Le gain est minuscule : la surface de $J$ est très plate autour de son maximum. Gardez deux idées en tête. (1) Un seuil « optimal » choisi sur les données qui ont servi à l'ajuster est un peu optimiste (2.2.8). (2) L'indice de Youden donne le même poids aux deux types d'erreur ; dans la pratique, le bon seuil dépend de leurs **coûts** (ici : relancer inutilement un client coûte peu, laisser partir un client précieux coûte cher).

### Corrigé 2.12

On ajuste une spline pour chaque `df` et l'on compare les AIC.

```python
sessions = pd.read_csv("donnees/ch02-sessions.csv")
lignes = []
for k in range(4, 13):
    r = smf.glm(f"achat ~ bs(duree_min, df={k}, lower_bound=0, upper_bound=40)", sessions, family=sm.families.Binomial()).fit()
    lignes.append({"fonctions de base": k, "paramètres": len(r.params), "AIC": r.aic})
res = pd.DataFrame(lignes)
res["ΔAIC"] = res["AIC"] - res["AIC"].min()
print(res.round(1).to_string(index=False))
print("nombre de fonctions de base retenu :", int(res.loc[res["AIC"].idxmin(), "fonctions de base"]))
```
<!--sortie-->
```text
 fonctions de base  paramètres    AIC  ΔAIC
                 4           5 1722.1  18.7
                 5           6 1704.2   0.8
                 6           7 1703.5   0.0
                 7           8 1703.6   0.1
                 8           9 1703.9   0.4
                 9          10 1705.7   2.2
                10          11 1707.4   4.0
                11          12 1709.1   5.7
                12          13 1707.7   4.2
nombre de fonctions de base retenu : 6
```

L'AIC est minimal pour 6 fonctions de base (1 703,5), mais les valeurs pour 5, 7 et 8 fonctions n'en sont qu'à 0,8, 0,1 et 0,4 point : un **plateau**, pas un minimum net. À 4 fonctions la courbe est trop rigide ($+18{,}7$) ; à partir de 9 fonctions l'AIC remonte de 2 à 6 points. L'avantage de la **pénalisation** est précisément d'éviter cette recherche à tâtons : on prend une base large et c'est le paramètre de lissage $\lambda$, choisi automatiquement, qui règle la souplesse (nous avions obtenu 6,5 degrés de liberté effectifs, au milieu de ce plateau).

### Corrigé 2.13

Le rapport variance/moyenne d'un ZIP vaut $1+\pi\mu$. Avec $\mu=4$ : $1+4\pi=2$, donc $\pi=0{,}25$. La probabilité d'un zéro est $\pi+(1-\pi)e^{-\mu}=0{,}25+0{,}75\,e^{-4}=0{,}25+0{,}75\times0{,}0183=0{,}2637$.

```python
rng = np.random.default_rng(13)
N = 1_000_000
y_zip = np.where(rng.random(N) < 0.25, 0, rng.poisson(4, N))
print(f"variance / moyenne simulée = {y_zip.var() / y_zip.mean():.3f} (attendu 2) | P(0) simulée = {np.mean(y_zip == 0):.4f} | formule = {0.25 + 0.75 * np.exp(-4):.4f}")
```
<!--sortie-->
```text
variance / moyenne simulée = 2.001 (attendu 2) | P(0) simulée = 0.2641 | formule = 0.2637
```

### Corrigé 2.14

(a) La densité de la loi Gamma de moyenne $\mu$ et de forme $\nu$ est $f(y)=\dfrac{1}{\Gamma(\nu)}\Big(\dfrac\nu\mu\Big)^\nu y^{\nu-1}e^{-\nu y/\mu}$, donc $\log f=\nu\big(-\tfrac y\mu-\log\mu\big)+(\nu-1)\log y+\nu\log\nu-\log\Gamma(\nu)$. Avec $\theta=-1/\mu$, $\phi=1/\nu$ et $b(\theta)=-\log(-\theta)=\log\mu$, on obtient $\dfrac{y\theta-b(\theta)}{\phi}=\nu\big(-\tfrac y\mu-\log\mu\big)$ : le reste ne dépend pas de $\theta$, c'est $c(y,\phi)$. Alors $b'(\theta)=-1/\theta=\mu$ et $b''(\theta)=1/\theta^2=\mu^2$, d'où $\mathrm{Var}(Y)=\phi\,b''(\theta)=\mu^2/\nu$ : le coefficient de variation $1/\sqrt\nu$ est constant. (b) $P(Y=0)=\exp\big(-\mu^{2-p}/(\phi(2-p))\big)$ avec $\mu^{0{,}7}=100^{0{,}7}=25{,}12$, donc $\lambda=25{,}12/(15\times0{,}7)=2{,}392$ et $P(Y=0)=e^{-2{,}392}=0{,}091$. Puis $\alpha=\frac{2-p}{p-1}=\frac{0{,}7}{0{,}3}=2{,}333$ et $\theta=\phi(p-1)\mu^{p-1}=15\times0{,}3\times100^{0{,}3}=4{,}5\times3{,}981=17{,}91$ ; on vérifie $\lambda\alpha\theta=2{,}392\times2{,}333\times17{,}91\approx100$.

```python
mu_t, phi_t, p_t = 100.0, 15.0, 1.3
lam = mu_t ** (2 - p_t) / (phi_t * (2 - p_t)); alpha = (2 - p_t) / (p_t - 1); theta = phi_t * (p_t - 1) * mu_t ** (p_t - 1)
print(f"lambda = {lam:.3f} | alpha = {alpha:.3f} | theta = {theta:.3f} | lambda*alpha*theta = {lam * alpha * theta:.2f} | P(0) = exp(-lambda) = {np.exp(-lam):.4f}")
rng = np.random.default_rng(14)
N = 500_000
n_cmd = rng.poisson(lam, N)
y_t = np.where(n_cmd > 0, rng.gamma(np.maximum(n_cmd, 1) * alpha, theta), 0.0)
print(f"simulation : P(0) = {np.mean(y_t == 0):.4f} | moyenne = {y_t.mean():.2f} | variance = {y_t.var():.1f} | phi * mu^p = {phi_t * mu_t ** p_t:.1f}")
```
<!--sortie-->
```text
lambda = 2.392 | alpha = 2.333 | theta = 17.915 | lambda*alpha*theta = 100.00 | P(0) = exp(-lambda) = 0.0914
simulation : P(0) = 0.0918 | moyenne = 99.82 | variance = 5962.3 | phi * mu^p = 5971.6
```

La simulation confirme le calcul : $P(Y=0)=0{,}0918$ simulée pour $0{,}0914$ théorique, moyenne $99{,}82$ pour 100, variance $5\,962$ pour $\phi\mu^p=5\,972$. Les paramètres $(\lambda,\alpha,\theta)=(2{,}392;\ 2{,}333;\ 17{,}91)$ sont donc cohérents avec la loi de Tweedie annoncée.
