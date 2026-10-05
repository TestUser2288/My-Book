# Chapitre 1 : Régression linéaire — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 1 du livre. Les **applications** reprennent, pas à pas et avec le code, les études que le livre résume ; les **exercices** (⭐ application directe, ⭐⭐ raisonnement, ⭐⭐⭐ synthèse) sont corrigés à la fin du chapitre. Les données (`donnees/clients.csv`, `donnees/enquete_satisfaction.csv`, `donnees/ventes_mensuelles.csv`, `donnees/ch01-relais.csv`) sont simulées avec des graines fixes. Prérequis : le chapitre 1 du livre, et le chapitre 1 de ce cahier exécuté dans l'ordre (les blocs de code partagent les mêmes variables).

## Préparation

Tout le chapitre part du même tableau : les 1 740 clients qui ont passé au moins une commande, avec le log de leur panier moyen, et les trois modèles `m1` (âge), `m2` (âge et canal) et `m3` (avec interaction) du livre.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats

clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()           # les clients actifs
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
df["a"] = df["age"] - 36                                       # âge centré sur 36 ans
df["log_panier"] = np.log(df["panier_moyen"])

m1 = smf.ols("log_panier ~ a", data=df).fit()
m2 = smf.ols("log_panier ~ a + C(canal)", data=df).fit()
m3 = smf.ols("log_panier ~ a * C(canal)", data=df).fit()
print(len(df), "clients actifs")
```
<!--sortie-->
```text
1740 clients actifs
```
```python hide
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)
```

> 💡 **Figures.** Le code qui trace les figures est repris dans les sources du dépôt (blocs marqués `hide` des fichiers `cahier/01-exercices.md` et `sections/01-*.md`) : il est exécuté à chaque vérification du livre, mais il n'est pas imprimé ici, pour ne garder que l'essentiel.

## Applications

### Application 1.1 — Retrouver les moindres carrés par la descente de gradient (section 1.1.3)

**Objectif.** Vérifier que la droite des quatre commandes (1, 22), (2, 41), (3, 66), (4, 79) s'obtient aussi en *descendant* la fonction $S(\boldsymbol\beta)=\|\mathbf y-\mathbf X\boldsymbol\beta\|^2$ pas à pas, comme au volume I (section 1.3.3). Le gradient est $-2\mathbf X^\top(\mathbf y-\mathbf X\boldsymbol\beta)$ ; on le moyenne sur $n$ pour garder un pas raisonnable.

**Étape 1 — la solution exacte.** C'est celle de la section 1.1.1 du livre : $(3\,;\,19{,}6)$.

```python
x = np.array([1, 2, 3, 4]); y = np.array([22, 41, 66, 79])
X = np.column_stack([np.ones(4), x])
print("équations normales :", np.linalg.solve(X.T @ X, X.T @ y))
```
<!--sortie-->
```text
équations normales : [ 3.  19.6]
```

**Étape 2 — la descente, avec $x$ centré.** Centrer $x$ (lui soustraire sa moyenne) rend les deux directions de $\mathbf X^\top\mathbf X$ orthogonales et accélère la convergence ; on retrouve ensuite la constante d'origine en retranchant $\hat\beta_1\bar x$.

```python
xc = x - x.mean()                                  # x centré : -1,5 ; -0,5 ; 0,5 ; 1,5
Xc = np.column_stack([np.ones(4), xc])
b = np.zeros(2)
pas = 0.1                                          # taux d'apprentissage
for it in range(200):
    gradient = -2 / len(y) * Xc.T @ (y - Xc @ b)   # gradient de la moyenne des carrés
    b = b - pas * gradient
print("descente de gradient (x centré) :", b.round(4))
print("solution exacte                 :", np.linalg.solve(Xc.T @ Xc, Xc.T @ y).round(4))
print("retour à l'échelle d'origine    : constante =", round(b[0] - b[1] * x.mean(), 3), "| pente =", round(b[1], 3))
```
<!--sortie-->
```text
descente de gradient (x centré) : [52.  19.6]
solution exacte                 : [52.  19.6]
retour à l'échelle d'origine    : constante = 3.0 | pente = 19.6
```

**Pour aller plus loin.** Remplacez `pas = 0.1` par 0,3 puis par 0,5, puis supprimez le centrage : que se passe-t-il, et pourquoi ? (Indice : les valeurs propres de $\mathbf X^\top\mathbf X/n$ fixent le pas maximal qui garantit la convergence.)

### Application 1.2 — Le panier selon l'âge et le canal, pas à pas (sections 1.1.7 à 1.1.9)

**Objectif.** Refaire l'étude de la section 1.1.7 : décrire le panier, ajuster `m1`, `m2` et `m3`, lire les coefficients (y compris en pourcentage), retrouver « toutes choses égales par ailleurs » avec le théorème de Frisch-Waugh-Lovell, et prédire un panier moyen en euros.

**Étape 1 — regarder le panier.** Une variable de montants est presque toujours asymétrique ; le log la symétrise.

```python
print("clients sans aucune commande :", int((clients["nb_commandes_an"] == 0).sum()), "sur", len(clients))
print("asymétrie du panier :", round(df["panier_moyen"].skew(), 2), "| du log du panier :", round(df["log_panier"].skew(), 2))
```
<!--sortie-->
```text
clients sans aucune commande : 260 sur 2000
asymétrie du panier : 1.44 | du log du panier : 0.11
```

**Étape 2 — deux modèles.** Lisez la formule : `log_panier ~ a + C(canal)` signifie « log-panier expliqué par l'âge centré et par le canal (variable qualitative) ». `statsmodels` fabrique la constante et les indicatrices.

```python
print(m1.summary().tables[1])
print(m2.summary().tables[1])
print("R² :", round(m1.rsquared, 4), "->", round(m2.rsquared, 4), "| R² ajusté de m2 :", round(m2.rsquared_adj, 4))
print(m2.model.exog[:6].astype(int), m2.model.exog_names)       # les six premières lignes de la matrice X
```
<!--sortie-->
```text
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
Intercept      4.0331      0.009    426.820      0.000       4.015       4.052
a              0.0090      0.001     10.050      0.000       0.007       0.011
==============================================================================
=======================================================================================
                          coef    std err          t      P>|t|      [0.025      0.975]
---------------------------------------------------------------------------------------
Intercept               4.2206      0.017    241.369      0.000       4.186       4.255
C(canal)[T.Site]       -0.1571      0.023     -6.807      0.000      -0.202      -0.112
C(canal)[T.Réseaux]    -0.3368      0.022    -14.977      0.000      -0.381      -0.293
a                       0.0092      0.001     10.862      0.000       0.008       0.011
=======================================================================================
R² : 0.0549 -> 0.1657 | R² ajusté de m2 : 0.1643
[[  1   0   1 -17]
 [  1   1   0   7]
 [  1   0   0  -1]
 [  1   0   1 -15]
 [  1   1   0  -6]
 [  1   0   1 -10]] ['Intercept', 'C(canal)[T.Site]', 'C(canal)[T.Réseaux]', 'a']
```

*Questions.* Que représente la constante de `m2` ? Combien vaut le panier **médian** d'un client de 36 ans acquis en boutique ?

**Étape 3 — lire un coefficient en pourcentage.** L'approximation « $100\beta$ % » n'est correcte que pour de petits coefficients ; la variation exacte est $100(e^\beta-1)$ %.

```python
for nom, coef in m2.params.items():
    if nom == "Intercept":
        continue
    print(f"{nom:22s} coefficient = {coef:+.3f} | approximation 100*beta = {100*coef:+.1f} % | exact 100*(exp(beta)-1) = {100*(np.exp(coef)-1):+.1f} %")
```
<!--sortie-->
```text
C(canal)[T.Site]       coefficient = -0.157 | approximation 100*beta = -15.7 % | exact 100*(exp(beta)-1) = -14.5 %
C(canal)[T.Réseaux]    coefficient = -0.337 | approximation 100*beta = -33.7 % | exact 100*(exp(beta)-1) = -28.6 %
a                      coefficient = +0.009 | approximation 100*beta = +0.9 % | exact 100*(exp(beta)-1) = +0.9 %
```

**Étape 4 — Frisch-Waugh-Lovell.** Le coefficient de l'âge dans `m2` est la pente entre deux résidus : celui du log-panier et celui de l'âge, une fois le canal « retiré » de l'un et de l'autre.

```python
res_y = smf.ols("log_panier ~ C(canal)", data=df).fit().resid        # log-panier, une fois le canal « retiré »
res_a = smf.ols("a ~ C(canal)", data=df).fit().resid                  # âge, une fois le canal « retiré »
pente_fwl = (res_a @ res_y) / (res_a @ res_a)
print("coefficient de l'âge dans le modèle complet :", round(m2.params["a"], 6))
print("pente obtenue par Frisch-Waugh-Lovell        :", round(pente_fwl, 6))
```
<!--sortie-->
```text
coefficient de l'âge dans le modèle complet : 0.00917
pente obtenue par Frisch-Waugh-Lovell        : 0.00917
```

**Étape 5 — calculer à la main ce que fait `statsmodels`.** Les coefficients sont la solution des équations normales sur la matrice $\mathbf X$ que le logiciel a construite ; le nombre de conditionnement n'est grand que parce que l'âge centré et les indicatrices ont des échelles très différentes.

```python
Xd = m2.model.exog                      # la matrice de plan d'expérience (n x p)
yd = m2.model.endog
beta_main = np.linalg.solve(Xd.T @ Xd, Xd.T @ yd)
print(pd.DataFrame({"à la main": beta_main, "statsmodels": m2.params.to_numpy()}, index=m2.params.index).round(6))
print("n =", Xd.shape[0], "| p =", Xd.shape[1])
print("nombre de conditionnement de X'X :", round(np.linalg.cond(Xd.T @ Xd), 1))
```
<!--sortie-->
```text
                     à la main  statsmodels
Intercept             4.220621     4.220621
C(canal)[T.Site]     -0.157139    -0.157139
C(canal)[T.Réseaux]  -0.336759    -0.336759
a                     0.009170     0.009170
n = 1740 | p = 4
nombre de conditionnement de X'X : 1501.8
```

**Étape 6 — prédire une moyenne en euros.** Le modèle prédit un log-panier ; $e^{\hat\mu}$ est la prédiction de la **médiane**. Pour la **moyenne**, il faut le facteur $e^{s^2/2}$ (loi normale) ou le facteur de Duan $\frac1n\sum e^{\hat\varepsilon_i}$.

```python
cible = df[(df["canal"] == "Boutique") & (df["age"].between(33, 39))]            # clients de la boutique, 33-39 ans
mu_hat = m2.predict(pd.DataFrame({"a": [0], "canal": pd.Categorical(["Boutique"], categories=["Boutique", "Site", "Réseaux"])})).iloc[0]
s2 = m2.scale
duan = np.exp(m2.resid).mean()
print("panier moyen observé (clients boutique, 33-39 ans) :", round(cible["panier_moyen"].mean(), 2), "€   (n =", len(cible), ")")
print("exp(mu chapeau)                  [médiane prédite] :", round(np.exp(mu_hat), 2), "€")
print("exp(mu chapeau + s²/2)           [moyenne, normale]:", round(np.exp(mu_hat + s2 / 2), 2), "€")
print("exp(mu chapeau) x facteur de Duan[moyenne, libre]  :", round(np.exp(mu_hat) * duan, 2), "€")
```
<!--sortie-->
```text
panier moyen observé (clients boutique, 33-39 ans) : 74.33 €   (n = 110 )
exp(mu chapeau)                  [médiane prédite] : 68.08 €
exp(mu chapeau + s²/2)           [moyenne, normale]: 72.91 €
exp(mu chapeau) x facteur de Duan[moyenne, libre]  : 72.96 €
```

**Étape 7 — l'interaction âge × canal.** Les deux lignes `a:C(canal)[…]` mesurent la différence de pente de l'âge par rapport à la boutique ; elles sont indiscernables de zéro.

```python
print(m3.summary().tables[1])
```
<!--sortie-->
```text
=========================================================================================
                            coef    std err          t      P>|t|      [0.025      0.975]
-----------------------------------------------------------------------------------------
Intercept                 4.2205      0.017    241.183      0.000       4.186       4.255
C(canal)[T.Site]         -0.1568      0.023     -6.788      0.000      -0.202      -0.112
C(canal)[T.Réseaux]      -0.3366      0.022    -14.961      0.000      -0.381      -0.292
a                         0.0086      0.002      5.115      0.000       0.005       0.012
a:C(canal)[T.Site]        0.0010      0.002      0.463      0.643      -0.003       0.005
a:C(canal)[T.Réseaux]     0.0005      0.002      0.235      0.814      -0.004       0.005
=========================================================================================
```

### Application 1.3 — Reconstruire les tableaux de `statsmodels` (sections 1.2.1 à 1.2.4)

**Objectif.** Retrouver à la main le tableau de `m2` (erreurs standard, $t$, p-valeurs, intervalles), tester une combinaison de coefficients, comparer deux modèles par un test $F$ et construire un intervalle de prédiction.

**Étape 1 — le tableau complet.** On calcule $s^2=\text{SCR}/(n-p)$, l'erreur standard $s\sqrt{c_{jj}}$, $t=\hat\beta_j/\text{se}$, la p-valeur et l'intervalle $\hat\beta_j\pm t_{n-p,\,0{,}975}\,\text{se}$.

```python
X = m2.model.exog
y = m2.model.endog
n, p = X.shape
XtX_inv = np.linalg.inv(X.T @ X)
beta = XtX_inv @ X.T @ y
residus = y - X @ beta
s2 = residus @ residus / (n - p)                       # estimation de sigma²
se = np.sqrt(s2 * np.diag(XtX_inv))                     # erreurs standard
t = beta / se                                           # statistiques t pour H0 : beta_j = 0
pval = 2 * stats.t.sf(np.abs(t), df=n - p)              # p-valeur bilatérale
crit = stats.t.ppf(0.975, df=n - p)                     # quantile de Student à 97,5 %
tab = pd.DataFrame({"coef": beta, "std err": se, "t": t, "P>|t|": pval,
                    "IC bas": beta - crit * se, "IC haut": beta + crit * se}, index=m2.params.index)
```
```python
print(tab.round(4))
print()
print("identique à statsmodels :", np.allclose(tab["std err"], m2.bse), np.allclose(tab["t"], m2.tvalues),
      np.allclose(tab[["IC bas", "IC haut"]].to_numpy(), m2.conf_int().to_numpy()))
print(f"s = {np.sqrt(s2):.4f} | quantile t(n-p, 97,5 %) = {crit:.4f}  (presque 1,96 : n - p = {n - p} est grand)")
```
<!--sortie-->
```text
                       coef  std err         t  P>|t|  IC bas  IC haut
Intercept            4.2206   0.0175  241.3693    0.0  4.1863   4.2549
C(canal)[T.Site]    -0.1571   0.0231   -6.8065    0.0 -0.2024  -0.1119
C(canal)[T.Réseaux] -0.3368   0.0225  -14.9770    0.0 -0.3809  -0.2927
a                    0.0092   0.0008   10.8618    0.0  0.0075   0.0108

identique à statsmodels : True True True
s = 0.3705 | quantile t(n-p, 97,5 %) = 1.9613  (presque 1,96 : n - p = 1736 est grand)
```

**Étape 2 — un test sur une combinaison.** « Le Site et Réseaux ont-ils le même panier, à âge égal ? » : $H_0:\beta_{\text{Site}}-\beta_{\text{Réseaux}}=0$ ; la variance de $\mathbf c^\top\hat{\boldsymbol\beta}$ est $\sigma^2\mathbf c^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf c$.

```python
c = np.array([0, 1, -1, 0])
diff = c @ beta
se_diff = np.sqrt(s2 * c @ XtX_inv @ c)
print(f"beta_Site - beta_Reseaux = {diff:.4f} | erreur standard = {se_diff:.4f} | t = {diff/se_diff:.2f} | p = {2*stats.t.sf(abs(diff/se_diff), n-p):.2e}")
print(m2.t_test("C(canal)[T.Site] - C(canal)[T.Réseaux] = 0"))
```
<!--sortie-->
```text
beta_Site - beta_Reseaux = 0.1796 | erreur standard = 0.0207 | t = 8.69 | p = 8.16e-18
                             Test for Constraints                             
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
c0             0.1796      0.021      8.691      0.000       0.139       0.220
==============================================================================
```

**Étape 3 — le test $F$.** Le canal compte-t-il (deux coefficients à la fois) ? Puis les autres usages du test $F$ : interaction, cas $q=1$, test global.

```python
# Le canal compte-t-il ?  M0 : log_panier ~ a   (m1)    contre   M1 : log_panier ~ a + canal   (m2)
scr0, scr1 = m1.ssr, m2.ssr
q = int(m2.df_model - m1.df_model)
F = ((scr0 - scr1) / q) / (scr1 / m2.df_resid)
pF = stats.f.sf(F, q, m2.df_resid)
print(f"SCR0 = {scr0:.2f} | SCR1 = {scr1:.2f} | q = {q} | F = {F:.2f} | p = {pF:.2e}")
print()
print(sm.stats.anova_lm(m1, m2).round(4))
```
<!--sortie-->
```text
SCR0 = 269.94 | SCR1 = 238.30 | q = 2 | F = 115.26 | p = 9.98e-48

   df_resid       ssr  df_diff  ss_diff       F  Pr(>F)
0    1738.0  269.9406      0.0      NaN     NaN     NaN
1    1736.0  238.2975      2.0  31.6431  115.26     0.0
```
```python
print("Interaction âge x canal (m2 contre m3) :")
print(sm.stats.anova_lm(m2, m3).round(4))
print()
a_t = m2.tvalues["a"]
print("cas q = 1 : t² de l'âge =", round(a_t**2, 3), "| F de la suppression de l'âge =", round(sm.stats.anova_lm(smf.ols("log_panier ~ C(canal)", df).fit(), m2).loc[1, "F"], 3))
print()
print("test global (m2) : F =", round(m2.fvalue, 2), "| p =", f"{m2.f_pvalue:.2e}")
```
<!--sortie-->
```text
Interaction âge x canal (m2 contre m3) :
   df_resid       ssr  df_diff  ss_diff       F  Pr(>F)
0    1736.0  238.2975      0.0      NaN     NaN     NaN
1    1734.0  238.2677      2.0   0.0299  0.1087   0.897

cas q = 1 : t² de l'âge = 117.979 | F de la suppression de l'âge = 117.979

test global (m2) : F = 114.93 | p = 6.88e-68
```

**Étape 4 — un intervalle de prédiction à la main.** Sur les quatre commandes de la section 1.1.1, quel montant prévoir pour **5 articles** ? On compare la formule $\hat y_0\pm t\,s\sqrt{h_0}$ (moyenne) et $\hat y_0\pm t\,s\sqrt{1+h_0}$ (prédiction) au résultat de `statsmodels`.

```python
x4 = np.array([1, 2, 3, 4]); y4 = np.array([22, 41, 66, 79])
d4 = pd.DataFrame({"x": x4, "y": y4})
mp = smf.ols("y ~ x", d4).fit()
nouveau = pd.DataFrame({"x": [5]})
pred = mp.get_prediction(nouveau).summary_frame(alpha=0.05)
print(pred.round(2).to_string())
x0 = np.array([1, 5]); X4 = np.column_stack([np.ones(4), x4])
h0 = x0 @ np.linalg.inv(X4.T @ X4) @ x0
s2_4 = mp.scale; tq = stats.t.ppf(0.975, 2)
print("à la main : h0 =", round(h0, 3), "| IC moyenne ±", round(tq*np.sqrt(s2_4*h0), 2), "| IC prédiction ±", round(tq*np.sqrt(s2_4*(1+h0)), 2))
```
<!--sortie-->
```text
    mean  mean_se  mean_ci_lower  mean_ci_upper  obs_ci_lower  obs_ci_upper
0  101.0     4.35          82.29         119.71         76.85        125.15
à la main : h0 = 1.5 | IC moyenne ± 18.71 | IC prédiction ± 24.15
```

**Étape 5 — les bandes de confiance et de prédiction.** On trace, pour les clients venus des réseaux sociaux, la droite de `m2` avec les deux bandes ; la bande de prédiction doit contenir environ 95 % des points.

```python hide
grille = pd.DataFrame({"age": np.arange(18, 76)})
grille["a"] = grille["age"] - 36
grille["canal"] = pd.Categorical(["Réseaux"] * len(grille), categories=["Boutique", "Site", "Réseaux"])
pf = m2.get_prediction(grille).summary_frame(alpha=0.05)

res_soc = df[df["canal"] == "Réseaux"]
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.scatter(res_soc["age"], res_soc["log_panier"], s=9, color=GRIS, alpha=0.55, label="clients Réseaux")
ax.fill_between(grille["age"], pf["obs_ci_lower"], pf["obs_ci_upper"], color=ORANGE, alpha=0.15, label="intervalle de prédiction à 95 % (un client)")
ax.fill_between(grille["age"], pf["mean_ci_lower"], pf["mean_ci_upper"], color=BLEU, alpha=0.45, label="intervalle de confiance à 95 % (le panier moyen)")
ax.plot(grille["age"], pf["mean"], color=BLEU, lw=2)
ax.set_xlabel("âge (ans)")
ax.set_ylabel("log du panier moyen")
ax.legend(frameon=False, loc="upper left", fontsize=8.5)
ax.set_ylim(2.3, 5.9)
plt.savefig("figures/ch01-bandes-prediction.png", dpi=200, bbox_inches="tight")
dans = ((res_soc["log_panier"] >= np.interp(res_soc["age"], grille["age"], pf["obs_ci_lower"])) &
        (res_soc["log_panier"] <= np.interp(res_soc["age"], grille["age"], pf["obs_ci_upper"]))).mean()
print(f"part des {len(res_soc)} clients Réseaux situés dans l'intervalle de prédiction à 95 % : {100*dans:.1f} %")
```
<!--sortie-->
```text
part des 687 clients Réseaux situés dans l'intervalle de prédiction à 95 % : 94.8 %
```

![Clients Réseaux : log du panier selon l'âge. La bande bleue (intervalle de confiance de la moyenne) est étroite ; la bande orange (prédiction pour un client) est beaucoup plus large et contient environ 95 % des points.](figures/ch01-bandes-prediction.png)

### Application 1.4 — Vérifier la théorie par simulation : couverture des intervalles et bootstrap (sections 1.2.5 et 1.2.6)

**Objectif.** Contrôler que « 95 % de confiance » veut bien dire 95 % de couverture quand le modèle est correct, puis comparer avec un bootstrap des couples, qui ne suppose pas la normalité.

**Étape 1 — la couverture.** On garde le vrai plan d'expérience de `m2`, on fixe de « vrais » coefficients, on simule 4 000 jeux de données et on compte combien d'intervalles contiennent la vérité.

```python
rng = np.random.default_rng(12)
beta_etoile = np.array([4.22, -0.17, -0.34, 0.009])               # nos « vrais » coefficients
sigma_v = 0.37
R = 4000
Ysim = X @ beta_etoile + rng.normal(0, sigma_v, size=(R, n))       # R jeux de données de n clients (lignes)
B = Ysim @ (XtX_inv @ X.T).T                                       # R estimations de beta (chaque ligne = un jeu)
E = Ysim - B @ X.T
S2 = (E**2).sum(axis=1) / (n - p)
SE = np.sqrt(S2[:, None] * np.diag(XtX_inv)[None, :])
Tst = (B - beta_etoile) / SE                                       # R x p statistiques t « vraies » (centrées sur la vérité)
low, high = B - crit * SE, B + crit * SE
couverture = ((low <= beta_etoile) & (beta_etoile <= high)).mean(axis=0)
print("couverture empirique de l'IC à 95 % :")
print(pd.Series(couverture, index=m2.params.index).round(3).to_string())
print("statistique t pour Réseaux : moyenne =", Tst[:, 2].mean().round(3), "| écart-type =", Tst[:, 2].std().round(3),
      "| écart-type théorique de t(n-p) =", round(np.sqrt((n - p) / (n - p - 2)), 3))
print("part de |t| > 1,96 quand H0 est vraie (erreur de type I) pour l'âge :", (np.abs(Tst[:, 3]) > 1.96).mean().round(3))
```
<!--sortie-->
```text
couverture empirique de l'IC à 95 % :
Intercept              0.944
C(canal)[T.Site]       0.951
C(canal)[T.Réseaux]    0.948
a                      0.950
statistique t pour Réseaux : moyenne = 0.008 | écart-type = 1.01 | écart-type théorique de t(n-p) = 1.001
part de |t| > 1,96 quand H0 est vraie (erreur de type I) pour l'âge : 0.05
```

**Étape 2 — le bootstrap des couples.** On tire avec remise des clients entiers, on réajuste, et on observe la variabilité des coefficients : aucune formule, aucune hypothèse de normalité.

```python
rng = np.random.default_rng(5)
B_boot = 2000
coefs = np.empty((B_boot, p))
for b in range(B_boot):
    idx = rng.integers(0, n, n)
    coefs[b] = np.linalg.lstsq(X[idx], y[idx], rcond=None)[0]
ic_boot = np.percentile(coefs, [2.5, 97.5], axis=0)
comp = pd.DataFrame({"IC t (bas)": m2.conf_int()[0].to_numpy(), "IC t (haut)": m2.conf_int()[1].to_numpy(),
                     "IC bootstrap (bas)": ic_boot[0], "IC bootstrap (haut)": ic_boot[1],
                     "se (formule)": m2.bse.to_numpy(), "se (bootstrap)": coefs.std(axis=0, ddof=1)}, index=m2.params.index)
print(comp.round(4).to_string())
```
<!--sortie-->
```text
                     IC t (bas)  IC t (haut)  IC bootstrap (bas)  IC bootstrap (haut)  se (formule)  se (bootstrap)
Intercept                4.1863       4.2549              4.1868               4.2545        0.0175          0.0172
C(canal)[T.Site]        -0.2024      -0.1119             -0.2021              -0.1131        0.0231          0.0227
C(canal)[T.Réseaux]     -0.3809      -0.2927             -0.3794              -0.2931        0.0225          0.0216
a                        0.0075       0.0108              0.0075               0.0108        0.0008          0.0008
```

*Pour aller plus loin.* Refaites l'étape 1 avec des erreurs très asymétriques (par exemple $\varepsilon=$ une loi exponentielle centrée). Que devient la couverture pour $n=1\,740$ ? Pour $n=30$ ?

### Application 1.5 — Le diagnostic complet de `m2` (section 1.3)

**Objectif.** Passer le modèle sur le panier en euros, puis celui sur son logarithme, à la visite médicale : graphiques de résidus, tests de Breusch-Pagan et de normalité, autocorrélation sur les ventes mensuelles, levier et distance de Cook, colinéarité, erreurs standard robustes.

**Étape 1 — les deux modèles et les trois graphiques.** Les graphiques sont ceux du livre (résidus contre valeurs ajustées, Q-Q, échelle-position).

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor

m_niv = smf.ols("panier_moyen ~ a + C(canal)", data=df).fit()       # panier en € : modèle « niveau »
ventes = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"])
ventes["t"] = np.arange(len(ventes))                                # numéro du mois : 0, 1, ..., 119
```
```python hide
def diagnostics(modele, axes, titre):
    ajuste = modele.fittedvalues
    r = modele.get_influence().resid_studentized_internal
    ax1, ax2, ax3 = axes
    ax1.scatter(ajuste, r, s=7, color=BLEU, alpha=0.45)
    lis = sm.nonparametric.lowess(r, ajuste, frac=0.4)
    ax1.plot(lis[:, 0], lis[:, 1], color=ORANGE, lw=2)
    ax1.axhline(0, color=GRIS, lw=1)
    ax1.set_xlabel("valeurs ajustées"); ax1.set_ylabel("résidu standardisé"); ax1.set_title(titre + " : résidus / ajustées", fontsize=10)
    th, emp = stats.probplot(r, dist="norm")[0]               # quantiles théoriques, quantiles observés
    ax2.scatter(th, emp, s=7, color=BLEU, alpha=0.45)
    lim = [min(th.min(), emp.min()), max(th.max(), emp.max())]
    ax2.plot(lim, lim, color=ORANGE, lw=2)
    ax2.set_xlabel("quantiles théoriques (loi normale)"); ax2.set_ylabel("quantiles observés"); ax2.set_title(titre + " : Q-Q", fontsize=10)
    ax3.scatter(ajuste, np.sqrt(np.abs(r)), s=7, color=BLEU, alpha=0.45)
    lis = sm.nonparametric.lowess(np.sqrt(np.abs(r)), ajuste, frac=0.4)
    ax3.plot(lis[:, 0], lis[:, 1], color=ORANGE, lw=2)
    ax3.set_xlabel("valeurs ajustées"); ax3.set_ylabel("racine de |résidu standardisé|"); ax3.set_title(titre + " : échelle-position", fontsize=10)

fig, axes = plt.subplots(2, 3, figsize=(12.5, 7.2))
diagnostics(m_niv, axes[0], "panier en €")
diagnostics(m2, axes[1], "log du panier")
plt.tight_layout()
plt.savefig("figures/ch01-diagnostics-niveau-log.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Diagnostics comparés. Ligne du haut : modèle sur le panier en € ; ligne du bas : modèle sur le log du panier.](figures/ch01-diagnostics-niveau-log.png)

**Étape 2 — Breusch-Pagan, à la main puis avec `statsmodels`.** On régresse les carrés des résidus sur $\mathbf X$ : $\text{LM}=n\,R^2_{\text{aux}}\sim\chi^2_{p-1}$.

```python
def breusch_pagan_main(modele):
    e2 = modele.resid.to_numpy() ** 2
    Xm = modele.model.exog
    aux = sm.OLS(e2, Xm).fit()                       # régression des carrés des résidus sur X
    LM = len(e2) * aux.rsquared
    return LM, stats.chi2.sf(LM, Xm.shape[1] - 1)

for nom, m in [("panier en €", m_niv), ("log du panier", m2)]:
    LM, p = breusch_pagan_main(m)
    LM_sm, p_sm = sm.stats.diagnostic.het_breuschpagan(m.resid, m.model.exog)[:2]
    print(f"{nom:14s} LM (main) = {LM:6.2f}  p = {p:.2e} | statsmodels : LM = {LM_sm:6.2f}  p = {p_sm:.2e}")
```
<!--sortie-->
```text
panier en €    LM (main) =  35.90  p = 7.86e-08 | statsmodels : LM =  35.90  p = 7.86e-08
log du panier  LM (main) =   1.92  p = 5.90e-01 | statsmodels : LM =   1.92  p = 5.90e-01
```

**Étape 3 — la normalité.** Asymétrie, aplatissement et tests de Shapiro et de Jarque-Bera.

```python
for nom, m in [("panier en €", m_niv), ("log du panier", m2)]:
    r = m.resid
    jb, pjb, sk, ku = sm.stats.jarque_bera(r)
    print(f"{nom:14s} asymétrie = {sk:5.2f} | aplatissement (excès) = {ku-3:5.2f} | Shapiro p = {stats.shapiro(r).pvalue:.2e} | Jarque-Bera p = {pjb:.2e}")
```
<!--sortie-->
```text
panier en €    asymétrie =  1.40 | aplatissement (excès) =  3.84 | Shapiro p = 1.25e-29 | Jarque-Bera p = 0.00e+00
log du panier  asymétrie =  0.11 | aplatissement (excès) = -0.06 | Shapiro p = 2.34e-01 | Jarque-Bera p = 1.63e-01
```

**Étape 4 — l'autocorrélation.** Sur les ventes mensuelles, avec une tendance simple en niveau puis en logarithme : Durbin-Watson et autocorrélation complète des résidus.

```python
mv_niv = smf.ols("ca ~ t", data=ventes).fit()
mv_log = smf.ols("np.log(ca) ~ t", data=ventes).fit()
for nom, m in [("ca ~ t", mv_niv), ("log(ca) ~ t", mv_log)]:
    dw = sm.stats.durbin_watson(m.resid)
    print(f"{nom:12s} R² = {m.rsquared:.3f} | Durbin-Watson = {dw:.2f} (rho ≈ {1 - dw/2:.2f}) | Breusch-Pagan p = {sm.stats.diagnostic.het_breuschpagan(m.resid, m.model.exog)[1]:.3f}")
```
<!--sortie-->
```text
ca ~ t       R² = 0.464 | Durbin-Watson = 1.56 (rho ≈ 0.22) | Breusch-Pagan p = 0.004
log(ca) ~ t  R² = 0.493 | Durbin-Watson = 1.56 (rho ≈ 0.22) | Breusch-Pagan p = 0.889
```
```python hide
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.8))
ax1.plot(ventes["mois"], mv_log.resid, color=BLEU, lw=1.2)
ax1.axhline(0, color=GRIS, lw=1)
ax1.set_ylabel("résidu de log(ca) ~ t"); ax1.set_title("Résidus dans le temps : une saisonnalité subsiste", fontsize=10)
pd.plotting.autocorrelation_plot(pd.Series(mv_log.resid.to_numpy()), ax=ax2, color=BLEU)
ax2.set_xlim(0, 36); ax2.set_title("Autocorrélation des résidus (décalages en mois)", fontsize=10)
plt.tight_layout()
plt.savefig("figures/ch01-residus-ventes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Résidus de log(ca) ~ t : vagues saisonnières (à gauche) et autocorrélation avec des pics aux décalages 12, 24 et 36 (à droite).](figures/ch01-residus-ventes.png)

**Étape 5 — levier et influence : un petit exemple, puis les clients.** Six points dont un très à droite : c'est son levier et sa distance de Cook qui le trahissent, pas son résidu.

```python
xs = np.array([1, 2, 3, 4, 5, 12.0])
ys = np.array([2.1, 3.9, 6.2, 7.8, 10.1, 14.0])          # le dernier point devrait être vers 24 si la tendance se poursuivait
Xs = np.column_stack([np.ones(6), xs])
ms = sm.OLS(ys, Xs).fit()
m5 = sm.OLS(ys[:5], Xs[:5]).fit()                         # sans le sixième point
infl = ms.get_influence()
print("pente avec les 6 points :", round(ms.params[1], 3), "| sans le sixième point :", round(m5.params[1], 3))
print("leviers h_ii :", infl.hat_matrix_diag.round(3), "(moyenne p/n =", round(2/6, 3), ")")
print("résidus bruts :", ms.resid.round(2))
print("résidus standardisés :", infl.resid_studentized_internal.round(2))
print("distances de Cook :", infl.cooks_distance[0].round(2))
print("prévision en x = 12 sans le sixième point :", round(m5.params[0] + m5.params[1] * 12, 1), "| observé :", ys[5])
# vérification de la formule de Cook par réajustement sans l'observation i
# résidu studentisé externe : formule sans réajustement, comparée à statsmodels
h6, e6 = infl.hat_matrix_diag, ms.resid
s_sans = np.sqrt((e6 @ e6 - e6**2 / (1 - h6)) / (6 - 2 - 1))
print("studentisés externes (main)  :", (e6 / (s_sans * np.sqrt(1 - h6))).round(2))
print("studentisés externes (statsm.):", infl.resid_studentized_external.round(2))
cook_main = []
for i in range(6):
    mi = sm.OLS(np.delete(ys, i), np.delete(Xs, i, axis=0)).fit()
    d = ms.params - mi.params
    cook_main.append(d @ Xs.T @ Xs @ d / (2 * ms.scale))
print("Cook par réajustement :", np.round(cook_main, 2))
```
<!--sortie-->
```text
pente avec les 6 points : 1.029 | sans le sixième point : 1.99
leviers h_ii : [0.325 0.247 0.196 0.17  0.17  0.892] (moyenne p/n = 0.333 )
résidus bruts : [-1.65 -0.88  0.39  0.96  2.24 -1.07]
résidus standardisés : [-1.23 -0.62  0.27  0.65  1.5  -1.99]
distances de Cook : [3.600e-01 6.000e-02 1.000e-02 4.000e-02 2.300e-01 1.643e+01]
prévision en x = 12 sans le sixième point : 23.9 | observé : 14.0
studentisés externes (main)  : [ -1.34  -0.56   0.23   0.59   1.96 -17.24]
studentisés externes (statsm.): [ -1.34  -0.56   0.23   0.59   1.96 -17.24]
Cook par réajustement : [3.600e-01 6.000e-02 1.000e-02 4.000e-02 2.300e-01 1.643e+01]
```
```python hide
fig, ax = plt.subplots(figsize=(6.6, 4.2))
xx = np.linspace(0, 13, 50)
ax.plot(xx, ms.params[0] + ms.params[1] * xx, color=ORANGE, lw=2, label="droite avec les 6 points")
ax.plot(xx, m5.params[0] + m5.params[1] * xx, color=BLEU, lw=2, label="droite sans le sixième point")
ax.scatter(xs[:5], ys[:5], color=ENCRE, s=36, zorder=3)
ax.scatter(xs[5:], ys[5:], color=ROUGE, s=60, zorder=3)
ax.annotate("point à fort levier", (12, 14.0), textcoords="offset points", xytext=(-95, -35), color=ROUGE,
            arrowprops=dict(arrowstyle="->", color=ROUGE))
ax.set_xlabel("x"); ax.set_ylabel("y"); ax.legend(frameon=False, loc="upper left")
ax.set_xlim(0, 13); ax.set_ylim(0, 27)
plt.savefig("figures/ch01-levier.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Un point à fort levier (rouge, x = 12) tire la droite orange vers lui.](figures/ch01-levier.png)

```python
infl = m2.get_influence()
h = infl.hat_matrix_diag
cook = infl.cooks_distance[0]
n, p = m2.model.exog.shape
print(f"n = {n}, p = {p} | levier moyen p/n = {p/n:.4f} | levier maximal = {h.max():.4f} | seuil 2p/n = {2*p/n:.4f}")
print(f"distance de Cook maximale = {cook.max():.4f} | seuil usuel 4/n = {4/n:.4f} | seuil d'alerte forte : 1")
print(f"nombre de clients au-dessus de 4/n : {(cook > 4/n).sum()} sur {n} ({100*(cook > 4/n).mean():.1f} %)")
print()
top = pd.DataFrame({"age": df["age"].to_numpy(), "canal": df["canal"].to_numpy(), "panier": df["panier_moyen"].to_numpy(),
                    "résidu stud. ext.": infl.resid_studentized_external, "levier": h, "Cook": cook}).sort_values("Cook", ascending=False).head(5)
print(top.round(4).to_string())
print()
print(m2.outlier_test().sort_values("unadj_p").head(3).round(4))
```
<!--sortie-->
```text
n = 1740, p = 4 | levier moyen p/n = 0.0023 | levier maximal = 0.0089 | seuil 2p/n = 0.0046
distance de Cook maximale = 0.0067 | seuil usuel 4/n = 0.0023 | seuil d'alerte forte : 1
nombre de clients au-dessus de 4/n : 84 sur 1740 (4.8 %)

      age     canal  panier  résidu stud. ext.  levier    Cook
864    43      Site  245.06             3.7254  0.0019  0.0067
747    48  Boutique   25.53            -2.9552  0.0030  0.0066
1060   66   Réseaux  131.04             1.9415  0.0061  0.0058
140    50      Site  189.89             2.8562  0.0027  0.0055
439    22   Réseaux  124.39             2.8921  0.0025  0.0052

      student_resid  unadj_p  bonf(p)
1001         3.7254   0.0002   0.3502
180          3.3254   0.0009   1.0000
1741         3.2648   0.0011   1.0000
```

**Étape 6 — la multicolinéarité.** On ajoute à `m2` l'âge en mois, presque redondant avec l'âge en années : prédictions intactes, coefficients ruinés ; puis le cas des termes polynomiaux non centrés.

```python
rng = np.random.default_rng(3)
df["age_mois"] = 12 * df["age"] + rng.normal(0, 3, len(df))         # presque redondant avec l'âge en années
print("corrélation âge (années) / âge (mois) :", round(np.corrcoef(df["age"], df["age_mois"])[0, 1], 4))

mc = smf.ols("log_panier ~ a + C(canal) + age_mois", data=df).fit()
print(pd.DataFrame({"m2 : coef": m2.params, "m2 : se": m2.bse, "avec age_mois : coef": mc.params, "avec age_mois : se": mc.bse}).round(4).to_string())
Xc = mc.model.exog
vif = pd.Series([variance_inflation_factor(Xc, i) for i in range(Xc.shape[1])], index=mc.params.index)
print()
print("VIF :", vif.round(1).to_dict())
print("R² de m2 :", round(m2.rsquared, 4), "| R² avec age_mois :", round(mc.rsquared, 4), " (prédictions aussi bonnes)")
```
<!--sortie-->
```text
corrélation âge (années) / âge (mois) : 0.9997
                     m2 : coef  m2 : se  avec age_mois : coef  avec age_mois : se
C(canal)[T.Réseaux]    -0.3368   0.0225               -0.3377              0.0225
C(canal)[T.Site]       -0.1571   0.0231               -0.1580              0.0231
Intercept               4.2206   0.0175                3.2552              1.2998
a                       0.0092   0.0008               -0.0176              0.0361
age_mois                   NaN      NaN                0.0022              0.0030

VIF : {'Intercept': 1.0, 'C(canal)[T.Site]': 1.5, 'C(canal)[T.Réseaux]': 1.5, 'a': 1828.5, 'age_mois': 1828.6}
R² de m2 : 0.1657 | R² avec age_mois : 0.166  (prédictions aussi bonnes)
```
```python
df["age2_brut"] = df["age"] ** 2
df["a2"] = df["a"] ** 2
mq_brut = smf.ols("log_panier ~ age + age2_brut + C(canal)", data=df).fit()
mq_centre = smf.ols("log_panier ~ a + a2 + C(canal)", data=df).fit()
for nom, m in [("non centré (âge, âge²)", mq_brut), ("centré (a, a²)", mq_centre)]:
    Xq = m.model.exog
    v = [round(float(variance_inflation_factor(Xq, i)), 1) for i in range(Xq.shape[1])]
    print(f"{nom:24s} VIF = {v} | p-valeur du terme quadratique = {m.pvalues.iloc[-1]:.3f}")
```
<!--sortie-->
```text
non centré (âge, âge²)   VIF = [1.0, 1.5, 1.5, 33.9, 33.9] | p-valeur du terme quadratique = 0.580
centré (a, a²)           VIF = [1.0, 1.5, 1.5, 1.0, 1.0] | p-valeur du terme quadratique = 0.580
```

**Étape 7 — les erreurs standard robustes.** Pour `m_niv`, on compare erreurs classiques, robustes (HC3) et bootstrap.

```python
m_hc3 = smf.ols("panier_moyen ~ a + C(canal)", data=df).fit(cov_type="HC3")
Xn, yn = m_niv.model.exog, m_niv.model.endog
rng = np.random.default_rng(8)
cb = np.array([np.linalg.lstsq(Xn[idx], yn[idx], rcond=None)[0] for idx in (rng.integers(0, len(yn), len(yn)) for _ in range(2000))])
print(pd.DataFrame({"se classique": m_niv.bse, "se robuste (HC3)": m_hc3.bse, "se bootstrap": cb.std(axis=0, ddof=1)}).round(3).to_string())
```
<!--sortie-->
```text
                     se classique  se robuste (HC3)  se bootstrap
Intercept                   1.149             1.306         1.274
C(canal)[T.Site]            1.518             1.688         1.659
C(canal)[T.Réseaux]         1.478             1.511         1.522
a                           0.055             0.055         0.055
```

**Étape 8 — les résidus partiels.** Une courbure systématique suggérerait d'ajouter un terme en âge² ; ici, le lissage suit la droite.

```python hide
fig, ax = plt.subplots(figsize=(6.6, 4.0))
partiel = m2.resid + m2.params["a"] * df["a"]
ax.scatter(df["age"], partiel, s=7, color=GRIS, alpha=0.45)
lis = sm.nonparametric.lowess(partiel, df["age"], frac=0.5)
ax.plot(lis[:, 0], lis[:, 1], color=ORANGE, lw=2.2, label="lissage local")
xa = np.linspace(18, 75, 50)
ax.plot(xa, m2.params["a"] * (xa - 36), color=BLEU, lw=2, ls="--", label="droite du modèle")
ax.set_xlabel("âge (ans)"); ax.set_ylabel("résidu partiel (effet de l'âge)")
ax.legend(frameon=False, loc="upper left")
plt.savefig("figures/ch01-residus-partiels.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Résidus partiels pour l'âge : le lissage local suit la droite du modèle.](figures/ch01-residus-partiels.png)

### Application 1.6 — Le surajustement, puis huit modèles en concurrence (sections 1.4.1 à 1.4.4)

**Objectif.** Voir le surajustement, vérifier à la main AIC, BIC et PRESS, écrire une validation croisée 10-fold et comparer huit modèles candidats sur les clients ayant répondu à l'enquête.

**Étape 1 — les données de l'enquête.** On fait la moyenne des questions q1–q4 (produits) et q5–q8 (service) et on les rattache aux clients actifs.

```python
from sklearn.model_selection import KFold

enq = pd.read_csv("donnees/enquete_satisfaction.csv")
enq["score_produit"] = enq[["q1", "q2", "q3", "q4"]].mean(axis=1)
enq["score_service"] = enq[["q5", "q6", "q7", "q8"]].mean(axis=1)
bq = df.merge(enq[["id_client", "score_produit", "score_service"]], on="id_client")     # clients actifs ayant répondu
print(len(enq), "répondants |", len(bq), "clients actifs répondants")
```
<!--sortie-->
```text
1212 répondants | 1076 clients actifs répondants
```

**Étape 2 — le surajustement.** On tire 40 clients pour entraîner un polynôme en l'âge de degré 0 à 8, on mesure l'erreur sur les autres, et on répète 300 fois.

```python
z = ((df["age"] - 36) / 10).to_numpy()                 # âge centré et réduit (évite les problèmes numériques des puissances)
yy = df["log_panier"].to_numpy()
rng = np.random.default_rng(21)
degres = np.arange(0, 9)
err_app, err_test = np.zeros((300, len(degres))), np.zeros((300, len(degres)))
for r in range(300):
    idx = rng.permutation(len(z))
    tr, te = idx[:40], idx[40:]
    for j, d in enumerate(degres):
        coef = np.polyfit(z[tr], yy[tr], d)
        err_app[r, j] = np.mean((yy[tr] - np.polyval(coef, z[tr])) ** 2)
        err_test[r, j] = np.mean((yy[te] - np.polyval(coef, z[te])) ** 2)
res = pd.DataFrame({"degré": degres, "erreur d'apprentissage": err_app.mean(axis=0), "erreur sur nouveaux clients": err_test.mean(axis=0)})
print(res.round(4).to_string(index=False))
```
<!--sortie-->
```text
 degré  erreur d'apprentissage  erreur sur nouveaux clients
     0                  0.1610                       0.1684
     1                  0.1490                       0.1629
     2                  0.1454                       0.1696
     3                  0.1423                       0.1853
     4                  0.1389                       0.2958
     5                  0.1353                       1.4399
     6                  0.1311                      50.3002
     7                  0.1261                     612.0571
     8                  0.1220                   12583.0488
```
```python hide
fig, ax = plt.subplots(figsize=(6.8, 4.2))
ax.plot(degres, err_app.mean(axis=0), "o-", color=BLEU, lw=2)
ax.plot(degres, err_test.mean(axis=0), "o-", color=ORANGE, lw=2)
ax.text(3.0, 0.108, "erreur sur les clients d'entraînement", color=BLEU, ha="left", va="center")
ax.text(0.1, 0.228, "erreur sur de\nnouveaux clients", color=ORANGE, ha="left", va="center")
ax.text(4.5, 0.33, "au-delà du degré 4, l'erreur\nexplose (axe coupé) :\n1,44 au degré 5,\nplus de 12 000 au degré 8", color=ORANGE, ha="left", va="center")
ax.set_xlabel("degré du polynôme en l'âge (complexité du modèle)")
ax.set_ylabel("erreur quadratique moyenne")
ax.set_xlim(-0.3, 8.5)
ax.set_ylim(0.10, 0.42)
plt.savefig("figures/ch01-surajustement.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Erreur d'apprentissage et erreur sur de nouveaux clients selon le degré du polynôme.](figures/ch01-surajustement.png)

**Étape 3 — AIC et BIC à la main.** La log-vraisemblance maximale du modèle gaussien est $-\frac n2(\log 2\pi+\log(\text{SCR}/n)+1)$ ; on pénalise par $k=p$ (convention de `statsmodels`).

```python
m_ex = smf.ols("log_panier ~ a + C(canal)", data=bq).fit()
n, p = m_ex.model.exog.shape
scr = m_ex.ssr
ll = -n / 2 * (np.log(2 * np.pi) + np.log(scr / n) + 1)
k = p                                                   # convention de statsmodels : on ne compte pas sigma²
print(f"log-vraisemblance : à la main = {ll:.3f} | statsmodels = {m_ex.llf:.3f}")
print(f"AIC : à la main = {-2*ll + 2*k:.3f} | statsmodels = {m_ex.aic:.3f}")
print(f"BIC : à la main = {-2*ll + k*np.log(n):.3f} | statsmodels = {m_ex.bic:.3f}")
```
<!--sortie-->
```text
log-vraisemblance : à la main = -431.472 | statsmodels = -431.472
AIC : à la main = 870.944 | statsmodels = 870.944
BIC : à la main = 890.868 | statsmodels = 890.868
```

**Étape 4 — PRESS : le leave-one-out sans refaire $n$ ajustements.** La formule $\hat\varepsilon_i/(1-h_{ii})$ est comparée à une boucle explicite.

```python
Xb, yb = m_ex.model.exog, m_ex.model.endog
h = m_ex.get_influence().hat_matrix_diag
press_formule = np.sum((m_ex.resid / (1 - h)) ** 2)
loo = np.empty(len(yb))
for i in range(len(yb)):                                           # n ajustements, un par client écarté
    mask = np.arange(len(yb)) != i
    b_i = np.linalg.lstsq(Xb[mask], yb[mask], rcond=None)[0]
    loo[i] = yb[i] - Xb[i] @ b_i
print(f"PRESS (formule, 1 ajustement)       = {press_formule:.4f}")
print(f"PRESS (boucle, {len(yb)} ajustements) = {np.sum(loo**2):.4f}")
print(f"erreur quadratique d'apprentissage (SCR) = {scr:.4f}  <- plus optimiste")
```
<!--sortie-->
```text
PRESS (formule, 1 ajustement)       = 141.5167
PRESS (boucle, 1076 ajustements) = 141.5167
erreur quadratique d'apprentissage (SCR) = 140.4879  <- plus optimiste
```

**Étape 5 — une validation croisée $K$-fold.** Mêmes paquets pour tous les modèles comparés.

```python
def cv_rmse(formule, data, K=10, graine=0):
    """RMSE de validation croisée K-fold (sur l'échelle du log-panier), mêmes paquets pour tous les modèles."""
    kf = KFold(n_splits=K, shuffle=True, random_state=graine)
    erreurs = []
    for tr, te in kf.split(data):
        m = smf.ols(formule, data=data.iloc[tr]).fit()
        pred = np.asarray(m.predict(data.iloc[te]))
        if pred.size == 1:                                       # modèle à constante seule : predict renvoie un seul nombre
            pred = np.repeat(pred, len(te))
        erreurs.append(data.iloc[te]["log_panier"].to_numpy() - pred)
    e = np.concatenate(erreurs)
    return np.sqrt(np.mean(e ** 2))

print("RMSE par validation croisée 10-fold, modèle log_panier ~ a + C(canal) :", round(cv_rmse("log_panier ~ a + C(canal)", bq), 4))
print("RMSE d'apprentissage                                                   :", round(np.sqrt(scr / n), 4))
```
<!--sortie-->
```text
RMSE par validation croisée 10-fold, modèle log_panier ~ a + C(canal) : 0.3629
RMSE d'apprentissage                                                   : 0.3613
```

**Étape 6 — huit modèles candidats.** M0 constante seule ; M1 âge ; M2 âge + canal ; M3 + score produit ; M4 + score service ; M5 M3 + ville + offre ; M6 M3 + âge² + interaction ; M7 tout.

```python
bq = bq.copy()
bq["a2"] = bq["a"] ** 2
candidats = {
    "M0": "log_panier ~ 1",
    "M1": "log_panier ~ a",
    "M2": "log_panier ~ a + C(canal)",
    "M3": "log_panier ~ a + C(canal) + score_produit",
    "M4": "log_panier ~ a + C(canal) + score_produit + score_service",
    "M5": "log_panier ~ a + C(canal) + score_produit + C(ville) + offre_bienvenue",
    "M6": "log_panier ~ a * C(canal) + a2 + score_produit",
    "M7": "log_panier ~ a * C(canal) + a2 + C(ville) + offre_bienvenue + score_produit + score_service",
}
```
```python
lignes, fits = [], {}
for nom, f in candidats.items():
    m = smf.ols(f, data=bq).fit()
    fits[nom] = m
    h = m.get_influence().hat_matrix_diag
    lignes.append({"modèle": nom, "paramètres p": int(m.df_model) + 1, "R²": m.rsquared, "R² ajusté": m.rsquared_adj,
                   "AIC": m.aic, "BIC": m.bic, "RMSE appr.": np.sqrt(m.mse_resid * m.df_resid / m.nobs),
                   "RMSE LOO (PRESS)": np.sqrt(np.mean((m.resid / (1 - h)) ** 2)), "RMSE CV10": cv_rmse(f, bq)})
tab = pd.DataFrame(lignes).set_index("modèle")
with pd.option_context("display.width", 200):
    print(tab.round(4).to_string())
print()
for crit in ["R² ajusté", "AIC", "BIC", "RMSE LOO (PRESS)", "RMSE CV10"]:
    meilleur = tab[crit].idxmax() if crit == "R² ajusté" else tab[crit].idxmin()
    print(f"meilleur modèle selon {crit:18s} : {meilleur}")
```
<!--sortie-->
```text
        paramètres p      R²  R² ajusté        AIC        BIC  RMSE appr.  RMSE LOO (PRESS)  RMSE CV10
modèle                                                                                                
M0                 1  0.0000     0.0000  1082.3441  1087.3251      0.3997            0.4001     0.4005
M1                 2  0.0663     0.0654  1010.5132  1020.4752      0.3863            0.3870     0.3872
M2                 4  0.1829     0.1807   870.9438   890.8679      0.3613            0.3627     0.3629
M3                 5  0.2542     0.2514   774.7862   799.6912      0.3452            0.3469     0.3478
M4                 6  0.2567     0.2532   773.1610   803.0470      0.3446            0.3466     0.3474
M5                11  0.2548     0.2478   785.8815   840.6726      0.3451            0.3487     0.3503
M6                 8  0.2549     0.2500   779.7843   819.6323      0.3451            0.3476     0.3485
M7                15  0.2582     0.2484   788.9871   863.7021      0.3443            0.3491     0.3506

meilleur modèle selon R² ajusté          : M4
meilleur modèle selon AIC                : M4
meilleur modèle selon BIC                : M3
meilleur modèle selon RMSE LOO (PRESS)   : M4
meilleur modèle selon RMSE CV10          : M4
```

**Étape 7 — les tests emboîtés.** Mêmes questions, posées par des tests $F$.

```python
print("M2 -> M3 (ajout du score produit) :")
print(sm.stats.anova_lm(fits["M2"], fits["M3"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
print("\nM3 -> M4 (ajout du score service) :")
print(sm.stats.anova_lm(fits["M3"], fits["M4"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
print("\nM3 -> M5 (ajout de la ville et de l'offre de bienvenue, 6 paramètres) :")
print(sm.stats.anova_lm(fits["M3"], fits["M5"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
print("\nM3 -> M6 (âge² et interactions, 3 paramètres) :")
print(sm.stats.anova_lm(fits["M3"], fits["M6"]).round(4).iloc[:, [0, 2, 4, 5]].to_string())
```
<!--sortie-->
```text
M2 -> M3 (ajout du score produit) :
   df_resid  df_diff         F  Pr(>F)
0    1072.0      0.0       NaN     NaN
1    1071.0      1.0  102.2966     0.0

M3 -> M4 (ajout du score service) :
   df_resid  df_diff       F  Pr(>F)
0    1071.0      0.0     NaN     NaN
1    1070.0      1.0  3.6111  0.0577

M3 -> M5 (ajout de la ville et de l'offre de bienvenue, 6 paramètres) :
   df_resid  df_diff       F  Pr(>F)
0    1071.0      0.0     NaN     NaN
1    1065.0      6.0  0.1493  0.9892

M3 -> M6 (âge² et interactions, 3 paramètres) :
   df_resid  df_diff       F  Pr(>F)
0    1071.0      0.0     NaN     NaN
1    1068.0      3.0  0.3316  0.8025
```

**Étape 8 — retrouver la vérité.** Les données étant simulées (`build/donnees2.py`), on compare le modèle M3 aux vraies valeurs, puis on prédit l'effet attendu par point de note du score produit.

```python
m3 = fits["M3"]
ic = m3.conf_int()
vrai_site, vrai_reseaux = 0.05 - 0.22, -0.12 - 0.22              # effets du Site et de Réseaux RELATIVEMENT à la Boutique
vrai = {"Intercept": np.nan, "C(canal)[T.Site]": vrai_site, "C(canal)[T.Réseaux]": vrai_reseaux, "a": 0.008}
comp = pd.DataFrame({"estimation (M3)": m3.params, "IC95 bas": ic[0], "IC95 haut": ic[1]})
comp["vérité"] = pd.Series(vrai)
comp["IC contient la vérité ?"] = [("oui" if (lo <= v <= hi) else "non") if not np.isnan(v) else "—" for lo, hi, v in zip(comp["IC95 bas"], comp["IC95 haut"], comp["vérité"])]
print(comp.round(4).to_string())
print()
print("Variables retenues dans M3 : âge, canal, score produit. Écartées par les critères : ville, offre, score service, âge², interactions.")
print("Dans M7 (le modèle « tout »), p-valeurs des variables sans effet réel :")
print(fits["M7"].pvalues[["C(ville)[T.Ville A]", "C(ville)[T.Ville B]", "C(ville)[T.Ville C]", "C(ville)[T.Ville D]", "C(ville)[T.Ville E]", "offre_bienvenue", "a2", "score_service"]].round(3).to_string())
```
<!--sortie-->
```text
                     estimation (M3)  IC95 bas  IC95 haut  vérité IC contient la vérité ?
Intercept                     3.6543    3.5385     3.7701     NaN                       —
C(canal)[T.Site]             -0.1573   -0.2114    -0.1032  -0.170                     oui
C(canal)[T.Réseaux]          -0.3519   -0.4045    -0.2993  -0.340                     oui
a                             0.0097    0.0078     0.0117   0.008                     oui
score_produit                 0.1557    0.1255     0.1859     NaN                       —

Variables retenues dans M3 : âge, canal, score produit. Écartées par les critères : ville, offre, score service, âge², interactions.
Dans M7 (le modèle « tout »), p-valeurs des variables sans effet réel :
C(ville)[T.Ville A]    0.901
C(ville)[T.Ville B]    0.934
C(ville)[T.Ville C]    0.526
C(ville)[T.Ville D]    0.808
C(ville)[T.Ville E]    0.883
offre_bienvenue        0.788
a2                     0.300
score_service          0.051
```
```python
lam = np.array([0.80, 0.70, 0.75, 0.60])
var_bruit = np.mean(1 - lam**2) / 4                       # variance du bruit de la moyenne de 4 questions (en unités de F1)
charge = lam.mean()                                        # poids moyen de F1 dans la moyenne des questions
fiabilite = charge**2 / (charge**2 + var_bruit)            # part de la variance de la note qui provient de F1
cov_F_score = 0.95 * charge
var_score = 0.95**2 * (charge**2 + var_bruit)
pente_F_sur_score = cov_F_score / var_score                # E[F1 | score] = pente * (score - moyenne)
print(f"fiabilité du score produit : {fiabilite:.2f}")
print(f"effet attendu par point de note : 0,12 x {pente_F_sur_score:.3f} = {0.12 * pente_F_sur_score:.3f}   | estimé dans M3 : {m3.params['score_produit']:.3f}  (IC95 % : [{ic.loc['score_produit', 0]:.3f} ; {ic.loc['score_produit', 1]:.3f}])")
```
<!--sortie-->
```text
fiabilité du score produit : 0.81
effet attendu par point de note : 0,12 x 1.192 = 0.143   | estimé dans M3 : 0.156  (IC95 % : [0.125 ; 0.186])
```

### Application 1.7 — La sélection automatique fabrique des découvertes (section 1.4.5)

**Objectif.** Montrer par simulation qu'une sélection ascendante par p-valeur « découvre » des variables dans du pur bruit, et qu'une procédure honnête (choisir sur une moitié, tester sur l'autre) retrouve le bon taux d'erreur.

**Étape 1 — la sélection ascendante.** On ajoute à chaque étape la variable la plus significative tant que sa p-valeur est inférieure à 0,05.

```python
def selection_ascendante(X, y, alpha=0.05):
    """Sélection ascendante par p-valeur. X : matrice n x q sans constante. Retourne la liste des colonnes retenues."""
    n, q = X.shape
    retenues = []
    while len(retenues) < q:
        meilleur, p_min = None, 1.0
        for j in range(q):
            if j in retenues:
                continue
            Z = np.column_stack([np.ones(n), X[:, retenues + [j]]])
            b, _, _, _ = np.linalg.lstsq(Z, y, rcond=None)
            e = y - Z @ b
            s2 = e @ e / (n - Z.shape[1])
            se = np.sqrt(s2 * np.linalg.inv(Z.T @ Z)[-1, -1])
            pj = 2 * stats.t.sf(abs(b[-1] / se), n - Z.shape[1])
            if pj < p_min:
                meilleur, p_min = j, pj
        if meilleur is None or p_min >= alpha:
            break
        retenues.append(meilleur)
    return retenues
```

**Étape 2 — une fonction qui renvoie les p-valeurs et le $R^2$ d'un modèle.**

```python
def ols_pvaleurs(X, y):
    Z = np.column_stack([np.ones(len(y)), X])
    b = np.linalg.lstsq(Z, y, rcond=None)[0]
    e = y - Z @ b
    s2 = e @ e / (len(y) - Z.shape[1])
    se = np.sqrt(s2 * np.diag(np.linalg.inv(Z.T @ Z)))
    return 2 * stats.t.sf(np.abs(b / se), len(y) - Z.shape[1])[1:], 1 - (e @ e) / np.sum((y - y.mean()) ** 2)
```

**Étape 3 — la simulation.** $y$ est indépendant des 20 variables ; 500 répétitions.

```python
rng = np.random.default_rng(99)
R, n_obs, q = 500, 100, 20
nb_retenues, r2_final, sig_final, sig_honnete, nb_honnete = [], [], [], [], []
for _ in range(R):
    X = rng.normal(size=(n_obs, q)); y = rng.normal(size=n_obs)            # y est indépendant de tout X
    ret = selection_ascendante(X, y)
    nb_retenues.append(len(ret))
    if ret:
        pv, r2 = ols_pvaleurs(X[:, ret], y)
        r2_final.append(r2); sig_final.append(np.mean(pv < 0.05))
    # procédure honnête : on choisit sur les 50 premiers, on teste sur les 50 autres
    ret_h = selection_ascendante(X[:50], y[:50])
    if ret_h:
        pv_h, _ = ols_pvaleurs(X[50:][:, ret_h], y[50:])
        sig_honnete.append(np.sum(pv_h < 0.05)); nb_honnete.append(len(ret_h))
nb_retenues = np.array(nb_retenues)
print(f"y est du pur bruit, indépendant des {q} variables explicatives (n = {n_obs}).")
print(f"part des jeux de données où au moins une variable est « découverte » : {np.mean(nb_retenues > 0):.1%}  (théorie pour une seule étape : 1 - 0,95^20 = {1 - 0.95**20:.1%})")
print(f"nombre moyen de variables retenues : {nb_retenues.mean():.2f}")
print(f"R² moyen du modèle final (quand il est non vide) : {np.mean(r2_final):.3f}  alors que le vrai R² est 0")
print(f"part de coefficients « significatifs à 5 % » dans le modèle final : {np.mean(sig_final):.1%}  (c'est trompeur : ils ont été choisis POUR l'être)")
print(f"procédure honnête (choix sur la moitié A, test sur la moitié B) : {np.sum(sig_honnete) / np.sum(nb_honnete):.1%} de significatifs parmi les variables retenues (≈ 5 % attendu)")
```
<!--sortie-->
```text
y est du pur bruit, indépendant des 20 variables explicatives (n = 100).
part des jeux de données où au moins une variable est « découverte » : 63.4%  (théorie pour une seule étape : 1 - 0,95^20 = 64.2%)
nombre moyen de variables retenues : 1.09
R² moyen du modèle final (quand il est non vide) : 0.093  alors que le vrai R² est 0
part de coefficients « significatifs à 5 % » dans le modèle final : 100.0%  (c'est trompeur : ils ont été choisis POUR l'être)
procédure honnête (choix sur la moitié A, test sur la moitié B) : 5.6% de significatifs parmi les variables retenues (≈ 5 % attendu)
```

*Questions.* Pourquoi la proportion de « découvertes » est-elle proche de $1-0{,}95^{20}$ ? Que vaut le taux de coefficients « significatifs » dans le modèle final, et pourquoi n'est-ce pas un taux d'erreur de type I ?

### Application 1.8 — Ridge et Lasso à la main (sections 1.5.1 et 1.5.2)

**Objectif.** Vérifier par simulation que Ridge peut battre les moindres carrés en erreur quadratique moyenne, puis écrire les formules de Ridge et du Lasso et les comparer à `scikit-learn`.

**Étape 1 — l'EQM de Ridge.** Deux variables corrélées à 0,98, $n=30$, vrais coefficients $(1,1)$ et $\sigma=1$ : biais², variance et EQM pour plusieurs $\lambda$.

```python
from sklearn.linear_model import Ridge, RidgeCV, Lasso, LassoCV, ElasticNetCV, lasso_path, LinearRegression
from sklearn.preprocessing import StandardScaler
```
```python
rng = np.random.default_rng(4)
n_s, rho = 30, 0.98
cov = np.array([[1, rho], [rho, 1]])
Xs = rng.multivariate_normal([0, 0], cov, size=n_s)
Xs = (Xs - Xs.mean(axis=0)) / Xs.std(axis=0)                     # variables centrées et standardisées, FIXES pour toute l'expérience
beta_vrai = np.array([1.0, 1.0]) / np.sqrt(n_s) * 3              # vrais coefficients (de petite taille relative au bruit)
R = 4000
resultats = {}
for lam in [0, 0.5, 1, 2, 5, 10, 20, 50]:
    M = np.linalg.solve(Xs.T @ Xs + lam * np.eye(2), Xs.T)       # (X'X + lambda I)^-1 X'
    erreurs = np.empty((R, 2))
    for r in range(R):
        y_s = Xs @ beta_vrai + rng.normal(0, 1, n_s)
        erreurs[r] = M @ y_s - beta_vrai
    if lam == 0:
        erreurs_mco = erreurs.copy()
    resultats[lam] = (np.mean(np.sum(erreurs**2, axis=1)), np.sum(erreurs.mean(axis=0)**2), np.sum(erreurs.var(axis=0)))
tab = pd.DataFrame(resultats, index=["EQM totale", "biais² total", "variance totale"]).T
tab.index.name = "lambda"
print("corrélation entre les deux variables :", round(np.corrcoef(Xs.T)[0, 1], 3))
print(tab.round(4).to_string())
print("corrélation entre les deux estimations MCO du même échantillon :", round(np.corrcoef(erreurs_mco.T)[0, 1], 3))
```
<!--sortie-->
```text
corrélation entre les deux variables : 0.984
        EQM totale  biais² total  variance totale
lambda                                           
0.0         2.0874        0.0002           2.0872
0.5         0.5132        0.0001           0.5131
1.0         0.2281        0.0003           0.2278
2.0         0.0899        0.0007           0.0892
5.0         0.0332        0.0038           0.0294
10.0        0.0292        0.0128           0.0164
20.0        0.0487        0.0378           0.0109
50.0        0.1310        0.1259           0.0052
corrélation entre les deux estimations MCO du même échantillon : -0.984
```

**Étape 2 — la formule de Ridge contre `scikit-learn`.** On standardise, on ne pénalise pas la constante (on centre $\mathbf y$), et on compare à `Ridge`.

```python
clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])
enq = pd.read_csv("donnees/enquete_satisfaction.csv")
enq["score_produit"] = enq[["q1", "q2", "q3", "q4"]].mean(axis=1)
enq["score_service"] = enq[["q5", "q6", "q7", "q8"]].mean(axis=1)
bq = df.merge(enq[["id_client", "score_produit", "score_service"]], on="id_client").reset_index(drop=True)

# Un petit jeu de variables : l'âge, le canal, les scores
Xp = pd.DataFrame({"age": bq["a"], "Site": (bq["canal"] == "Site").astype(float), "Réseaux": (bq["canal"] == "Réseaux").astype(float),
                   "score_produit": bq["score_produit"], "score_service": bq["score_service"]})
yv = bq["log_panier"].to_numpy()
sc = StandardScaler().fit(Xp)
Z = sc.transform(Xp)
yc = yv - yv.mean()
lam = 50.0
beta_main = np.linalg.solve(Z.T @ Z + lam * np.eye(Z.shape[1]), Z.T @ yc)
sk = Ridge(alpha=lam).fit(Z, yv)
print(pd.DataFrame({"à la main": beta_main, "scikit-learn": sk.coef_, "MCO (λ = 0)": LinearRegression().fit(Z, yv).coef_}, index=Xp.columns).round(5).to_string())
```
<!--sortie-->
```text
               à la main  scikit-learn  MCO (λ = 0)
age              0.09800       0.09800      0.10255
Site            -0.06342      -0.06342     -0.07490
Réseaux         -0.15797      -0.15797     -0.17241
score_produit    0.09827       0.09827      0.10322
score_service    0.02016       0.02016      0.02035
```

**Étape 3 — la descente par coordonnées du Lasso.** La mise à jour de chaque coefficient est un seuillage doux $S(\rho_j,\alpha)=\operatorname{signe}(\rho_j)\max(|\rho_j|-\alpha,0)$.

```python
def lasso_coordonnees(Z, y, alpha, n_iter=500):
    n_, p_ = Z.shape
    beta = np.zeros(p_)
    for _ in range(n_iter):
        for j in range(p_):
            r_partiel = y - Z @ beta + Z[:, j] * beta[j]              # résidu en retirant l'effet de toutes les variables sauf j
            rho = Z[:, j] @ r_partiel / n_
            beta[j] = np.sign(rho) * max(abs(rho) - alpha, 0.0)        # seuillage doux
    return beta

alpha = 0.05
b_main = lasso_coordonnees(Z, yc, alpha)
b_sk = Lasso(alpha=alpha, max_iter=100000, tol=1e-12).fit(Z, yv).coef_
print(pd.DataFrame({"à la main": b_main, "scikit-learn": b_sk, "MCO": LinearRegression().fit(Z, yv).coef_}, index=Xp.columns).round(5).to_string())
print("coefficients exactement nuls (à la main) :", list(Xp.columns[b_main == 0]))
```
<!--sortie-->
```text
               à la main  scikit-learn      MCO
age              0.05297       0.05297  0.10255
Site            -0.00000      -0.00000 -0.07490
Réseaux         -0.07486      -0.07486 -0.17241
score_produit    0.05465       0.05465  0.10322
score_service    0.00000       0.00000  0.02035
coefficients exactement nuls (à la main) : ['Site', 'score_service']
```

**Étape 4 — la géométrie.** Le point de contact entre une ellipse qui grandit et la région admissible : sommet du losange pour le Lasso (d'où les zéros), point lisse pour Ridge.

```python hide
def solution_contrainte(centre, A, region, r, n_pts=4000):
    """Point de la frontière de la région (norme p = 1 ou 2, rayon r) qui minimise (b-c)'A(b-c)."""
    t = np.linspace(0, 2 * np.pi, n_pts)
    if region == 2:
        pts = r * np.column_stack([np.cos(t), np.sin(t)])
    else:
        c, s_ = np.cos(t), np.sin(t)
        pts = r * np.column_stack([c, s_]) / (np.abs(c) + np.abs(s_))[:, None]
    d = pts - centre
    val = np.einsum("ij,jk,ik->i", d, A, d)
    k = np.argmin(val)
    return pts[k], val[k]

centre = np.array([2.0, 0.30])                                  # solution des moindres carrés
theta = np.deg2rad(-30)
Rot = np.array([[np.cos(theta), -np.sin(theta)], [np.sin(theta), np.cos(theta)]])
A = Rot @ np.diag([1.0, 3.0]) @ Rot.T                           # ellipses allongées
fig, axes = plt.subplots(1, 2, figsize=(10, 4.6))
for ax, region, titre in zip(axes, [2, 1], ["Ridge : contrainte en disque", "Lasso : contrainte en losange"]):
    r = 1.15
    t = np.linspace(0, 2 * np.pi, 400)
    if region == 2:
        ax.fill(r * np.cos(t), r * np.sin(t), color=BLEU, alpha=0.18)
        ax.plot(r * np.cos(t), r * np.sin(t), color=BLEU, lw=1.8)
    else:
        sommets = np.array([[r, 0], [0, r], [-r, 0], [0, -r], [r, 0]])
        ax.fill(sommets[:, 0], sommets[:, 1], color=BLEU, alpha=0.18)
        ax.plot(sommets[:, 0], sommets[:, 1], color=BLEU, lw=1.8)
    sol, val = solution_contrainte(centre, A, region, r)
    for niveau in [val * 0.25, val * 0.6, val, val * 2.4, val * 5]:           # ellipses de niveau
        u = np.linspace(0, 2 * np.pi, 400)
        w, V = np.linalg.eigh(A)
        el = np.sqrt(niveau) * (V @ np.diag(1 / np.sqrt(w)) @ np.vstack([np.cos(u), np.sin(u)])).T + centre
        ax.plot(el[:, 0], el[:, 1], color=ORANGE if np.isclose(niveau, val) else GRIS, lw=1.6 if np.isclose(niveau, val) else 0.9)
    ax.scatter(*centre, color=ENCRE, zorder=5, s=30); ax.annotate("moindres carrés", centre, textcoords="offset points", xytext=(6, 6), fontsize=9)
    ax.scatter(*sol, color=ROUGE, zorder=6, s=45); ax.annotate("solution\npénalisée", sol, textcoords="offset points", xytext=(14, -40) if region == 2 else (16, -42), color=ROUGE, fontsize=9)
    ax.axhline(0, color=GRIS, lw=0.8); ax.axvline(0, color=GRIS, lw=0.8)
    ax.set_xlim(-1.6, 3.1); ax.set_ylim(-1.6, 1.9); ax.set_aspect("equal")
    ax.set_xlabel("coefficient β₁"); ax.set_ylabel("coefficient β₂"); ax.set_title(titre, fontsize=10.5)
    print(f"{titre}: solution = ({sol[0]:.3f}, {sol[1]:.3f})")
plt.tight_layout()
plt.savefig("figures/ch01-geometrie-ridge-lasso.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
Ridge : contrainte en disque: solution = (1.071, 0.420)
Lasso : contrainte en losange: solution = (1.150, 0.000)
figure enregistrée
```

![La géométrie de la régularisation : disque (Ridge) et losange (Lasso).](figures/ch01-geometrie-ridge-lasso.png)

### Application 1.9 — Beaucoup de variables, peu de clients (section 1.5.4)

**Objectif.** Reproduire l'expérience du livre : 35 variables candidates (4 vraies, des variables sans effet et 20 de pur bruit) pour 120 clients d'entraînement ; comparer les moindres carrés, un modèle de référence qui connaît les vraies variables, Ridge, Lasso et Elastic Net sur 956 clients de test.

**Étape 1 — fabriquer les 35 variables.**

```python
rng = np.random.default_rng(31)
ville = bq["id_client"].map(clients.set_index("id_client")["ville"])
villes = pd.get_dummies(ville, prefix="ville", drop_first=True, dtype=float)       # 5 indicatrices (Autre = référence)
F = pd.DataFrame({
    "age": bq["a"].astype(float), "age_carre": bq["a"].astype(float) ** 2, "age_cube": bq["a"].astype(float) ** 3,
    "canal_Site": (bq["canal"] == "Site").astype(float), "canal_Reseaux": (bq["canal"] == "Réseaux").astype(float),
    "offre_bienvenue": bq["id_client"].map(clients.set_index("id_client")["offre_bienvenue"]).astype(float),
    "score_produit": bq["score_produit"], "score_service": bq["score_service"],
    "age_x_Site": bq["a"] * (bq["canal"] == "Site").astype(float), "age_x_Reseaux": bq["a"] * (bq["canal"] == "Réseaux").astype(float),
})
F = pd.concat([F, villes], axis=1)
bruit = pd.DataFrame(rng.normal(size=(len(F), 20)), columns=[f"bruit_{i+1:02d}" for i in range(20)])
F = pd.concat([F, bruit], axis=1)
signal = ["age", "canal_Site", "canal_Reseaux", "score_produit"]               # les variables qui ont un VRAI effet dans la simulation
print("nombre de variables candidates :", F.shape[1], "| dont du pur bruit :", 20, "| clients :", len(F))
```
<!--sortie-->
```text
nombre de variables candidates : 35 | dont du pur bruit : 20 | clients : 1076
```
```python
ordre = rng.permutation(len(F))
tr, te = ordre[:120], ordre[120:]
sc = StandardScaler().fit(F.iloc[tr])
Ztr, Zte = sc.transform(F.iloc[tr]), sc.transform(F.iloc[te])
ytr, yte = yv[tr], yv[te]
print("entraînement :", len(tr), "clients | test :", len(te), "clients")
```
<!--sortie-->
```text
entraînement : 120 clients | test : 956 clients
```

**Étape 2 — entraîner et comparer.** $\lambda$ est choisi par validation croisée à 10 paquets, sur l'échantillon d'entraînement seulement.

```python
def rmse(y, p):
    return float(np.sqrt(np.mean((y - p) ** 2)))

noms = list(F.columns)
idx_signal = [noms.index(v) for v in signal]
modeles = {}
modeles["MCO, 35 variables"] = LinearRegression().fit(Ztr, ytr)
ref = LinearRegression().fit(Ztr[:, idx_signal], ytr)
ridge = RidgeCV(alphas=np.logspace(-1, 3.5, 60), cv=10).fit(Ztr, ytr)
lasso = LassoCV(alphas=100, cv=10, random_state=0, max_iter=100000).fit(Ztr, ytr)
enet = ElasticNetCV(l1_ratio=[0.2, 0.5, 0.8, 0.95], alphas=60, cv=10, random_state=0, max_iter=100000).fit(Ztr, ytr)
modeles.update({"Ridge (λ par CV)": ridge, "Lasso (α par CV)": lasso, "Elastic Net (CV)": enet})
```
```python
lignes = [{"modèle": "constante seule", "RMSE apprentissage": rmse(ytr, np.full(len(ytr), ytr.mean())), "RMSE test": rmse(yte, np.full(len(yte), ytr.mean())),
           "variables non nulles": 0, "dont bruit": 0}]
lignes.append({"modèle": "référence : 4 vraies variables", "RMSE apprentissage": rmse(ytr, ref.predict(Ztr[:, idx_signal])),
               "RMSE test": rmse(yte, ref.predict(Zte[:, idx_signal])), "variables non nulles": 4, "dont bruit": 0})
for nom, m in modeles.items():
    coef = m.coef_
    non_nuls = np.abs(coef) > 1e-10
    lignes.append({"modèle": nom, "RMSE apprentissage": rmse(ytr, m.predict(Ztr)), "RMSE test": rmse(yte, m.predict(Zte)),
                   "variables non nulles": int(non_nuls.sum()), "dont bruit": int(sum(non_nuls[i] for i, n in enumerate(noms) if n.startswith("bruit")))})
res = pd.DataFrame(lignes).set_index("modèle")
print(res.round(4).to_string())
print()
print(f"Ridge : lambda choisi = {ridge.alpha_:.1f} | Lasso : alpha choisi = {lasso.alpha_:.4f} | Elastic Net : alpha = {enet.alpha_:.4f}, rho = {enet.l1_ratio_}")
```
<!--sortie-->
```text
                                RMSE apprentissage  RMSE test  variables non nulles  dont bruit
modèle                                                                                         
constante seule                             0.3803     0.4039                     0           0
référence : 4 vraies variables              0.3093     0.3612                     4           0
MCO, 35 variables                           0.2728     0.4152                    35          20
Ridge (λ par CV)                            0.3200     0.3765                    35          20
Lasso (α par CV)                            0.3032     0.3609                    15           7
Elastic Net (CV)                            0.3038     0.3608                    15           7

Ridge : lambda choisi = 134.0 | Lasso : alpha choisi = 0.0250 | Elastic Net : alpha = 0.0266, rho = 0.95
```

**Étape 3 — lire les coefficients et les chemins de régularisation.**

```python
coef = pd.DataFrame({"MCO": modeles["MCO, 35 variables"].coef_, "Ridge": ridge.coef_, "Lasso": lasso.coef_, "Elastic Net": enet.coef_}, index=noms)
vus = coef[(coef["Lasso"].abs() > 1e-10) | coef.index.isin(signal)]
print("coefficients (variables standardisées) pour les variables retenues par le Lasso ou vraiment utiles :")
print(vus.round(3).to_string())
print()
print("variables de bruit : plus grand |coefficient| MCO =", round(coef.loc[coef.index.str.startswith("bruit"), "MCO"].abs().max(), 3),
      "| Ridge =", round(coef.loc[coef.index.str.startswith("bruit"), "Ridge"].abs().max(), 3),
      "| Lasso =", round(coef.loc[coef.index.str.startswith("bruit"), "Lasso"].abs().max(), 3))
```
<!--sortie-->
```text
coefficients (variables standardisées) pour les variables retenues par le Lasso ou vraiment utiles :
                 MCO  Ridge  Lasso  Elastic Net
age            0.165  0.033  0.050        0.050
age_carre      0.052  0.015  0.011        0.010
canal_Site    -0.174 -0.033 -0.091       -0.090
canal_Reseaux -0.218 -0.056 -0.132       -0.131
score_produit  0.106  0.053  0.096        0.095
age_x_Reseaux -0.005  0.022  0.026        0.026
ville_Ville D -0.067 -0.021 -0.013       -0.013
ville_Ville E -0.037  0.013  0.004        0.003
bruit_01       0.073  0.024  0.025        0.024
bruit_02       0.060  0.012  0.013        0.012
bruit_11      -0.034 -0.016 -0.005       -0.004
bruit_13      -0.052 -0.013 -0.004       -0.003
bruit_14       0.020  0.020  0.021        0.021
bruit_19       0.013  0.015  0.004        0.003
bruit_20      -0.054 -0.021 -0.014       -0.014

variables de bruit : plus grand |coefficient| MCO = 0.073 | Ridge = 0.024 | Lasso = 0.025
```
```python hide
alphas_l, coefs_l, _ = lasso_path(Ztr, ytr - ytr.mean(), alphas=80)
alphas_r = np.logspace(-1, 4, 80)
coefs_r = np.array([np.linalg.solve(Ztr.T @ Ztr + a * np.eye(Ztr.shape[1]), Ztr.T @ (ytr - ytr.mean())) for a in alphas_r]).T
couleurs = {"age": VIOLET, "canal_Site": AQUA, "canal_Reseaux": ORANGE, "score_produit": BLEU}
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
for ax, al, cf, titre, choisi in [(ax1, alphas_r, coefs_r, "Ridge", ridge.alpha_), (ax2, alphas_l, coefs_l, "Lasso", lasso.alpha_)]:
    for i, nom in enumerate(noms):
        if nom in couleurs:
            continue
        ax.plot(np.log10(al), cf[i], color=GRIS, lw=0.7, alpha=0.55)
    for i, nom in enumerate(noms):
        if nom in couleurs:
            ax.plot(np.log10(al), cf[i], color=couleurs[nom], lw=2.2, label={"canal_Reseaux": "canal Réseaux"}.get(nom, nom.replace("_", " ")))
    ax.axvline(np.log10(choisi), color=ENCRE, ls="--", lw=1)
    ax.text(np.log10(choisi), ax.get_ylim()[1] * 0.92, " choisi par\n validation croisée", fontsize=8.5, va="top")
    ax.axhline(0, color=GRIS, lw=0.8)
    ax.set_xlabel("pénalité : log10(λ)" if titre == "Ridge" else "pénalité : log10(α)")
    ax.set_title(titre + " : coefficients (variables standardisées)", fontsize=10.5)
ax1.set_ylabel("valeur du coefficient")
ax1.legend(frameon=False, fontsize=8.5, loc="lower left")
ax1.invert_xaxis(); ax2.invert_xaxis()
plt.tight_layout()
plt.savefig("figures/ch01-chemins-regularisation.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Chemins de régularisation : Ridge (à gauche) et Lasso (à droite).](figures/ch01-chemins-regularisation.png)

### Application 1.10 — Huber à la main et données contaminées (sections 1.6.1 à 1.6.4)

**Objectif.** Écrire l'algorithme des moindres carrés repondérés (IRLS) pour la fonction de Huber, puis mesurer les dégâts d'une contamination (6 % de paniers multipliés par 10) sur les moindres carrés et sur Huber ; enfin voir la limite : les points à fort levier.

**Étape 1 — les données propres et les fonctions de perte.**

```python
import statsmodels.api as sm
df = clients[clients["nb_commandes_an"] > 0].copy().reset_index(drop=True)
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])
m_propre = smf.ols("log_panier ~ a + C(canal)", data=df).fit()
```
```python hide
u = np.linspace(-6, 6, 400)
c_h, c_t = 1.345, 4.685
rho_mco = u**2 / 2
rho_huber = np.where(np.abs(u) <= c_h, u**2 / 2, c_h * np.abs(u) - c_h**2 / 2)
rho_tukey = np.where(np.abs(u) <= c_t, c_t**2 / 6 * (1 - (1 - (u / c_t)**2)**3), c_t**2 / 6)
w_mco = np.ones_like(u)
w_huber = np.where(np.abs(u) <= c_h, 1.0, c_h / np.abs(u))
w_tukey = np.where(np.abs(u) <= c_t, (1 - (u / c_t)**2)**2, 0.0)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
for rho, nom, col in [(rho_mco, "moindres carrés", GRIS), (rho_huber, "Huber (c = 1,345)", BLEU), (rho_tukey, "Tukey bisquare (c = 4,685)", ORANGE)]:
    ax1.plot(u, rho, color=col, lw=2.2, label=nom)
ax1.set_ylim(0, 9); ax1.set_xlabel("résidu standardisé u"); ax1.set_ylabel("perte ρ(u)"); ax1.set_title("Perte attribuée à un résidu", fontsize=10.5)
ax1.legend(frameon=False, loc="upper center", fontsize=9)
for w, col, nom in [(w_mco, GRIS, "moindres carrés : poids constant égal à 1"), (w_huber, BLEU, "Huber : poids c/|u| au-delà de 1,345"), (w_tukey, ORANGE, "Tukey : poids nul au-delà de 4,685")]:
    ax2.plot(u, w, color=col, lw=2.2, label=nom)
ax2.set_ylim(-0.05, 1.15); ax2.set_xlabel("résidu standardisé u"); ax2.set_ylabel("poids w(u)"); ax2.set_title("Poids donné à l'observation", fontsize=10.5)
ax2.legend(frameon=False, loc="lower center", fontsize=8.5, bbox_to_anchor=(0.5, 0.08))
plt.tight_layout()
plt.savefig("figures/ch01-fonctions-robustes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Fonctions de perte et de poids : moindres carrés, Huber, Tukey.](figures/ch01-fonctions-robustes.png)

**Étape 2 — l'IRLS de Huber contre `RLM`.**

```python
def huber_irls(X, y, c=1.345, n_iter=100, tol=1e-10):
    beta = np.linalg.lstsq(X, y, rcond=None)[0]                  # départ : les moindres carrés
    for _ in range(n_iter):
        e = y - X @ beta
        s = np.median(np.abs(e - np.median(e))) / 0.6745        # échelle robuste (MAD)
        u = e / s
        w = np.where(np.abs(u) <= c, 1.0, c / np.abs(u))        # poids de Huber
        W = X.T * w                                              # X' diag(w)
        beta_new = np.linalg.solve(W @ X, W @ y)                 # régression pondérée
        if np.max(np.abs(beta_new - beta)) < tol:
            beta = beta_new
            break
        beta = beta_new
    return beta, w, s

Xp, yp = m_propre.model.exog, m_propre.model.endog
b_main, w_main, s_main = huber_irls(Xp, yp)
rlm = sm.RLM(yp, Xp, M=sm.robust.norms.HuberT(t=1.345)).fit()
print(pd.DataFrame({"MCO": m_propre.params, "Huber (à la main)": b_main, "RLM statsmodels": rlm.params}).round(4).to_string())
print(f"échelle robuste s : {s_main:.4f} | écart-type résiduel des MCO : {np.sqrt(m_propre.scale):.4f}")
print(f"part des clients dont le poids est inférieur à 1 : {np.mean(w_main < 1):.1%}")
```
<!--sortie-->
```text
                        MCO  Huber (à la main)  RLM statsmodels
Intercept            4.2206             4.2171           4.2172
C(canal)[T.Site]    -0.1571            -0.1602          -0.1602
C(canal)[T.Réseaux] -0.3368            -0.3331          -0.3332
a                    0.0092             0.0090           0.0090
échelle robuste s : 0.3667 | écart-type résiduel des MCO : 0.3705
part des clients dont le poids est inférieur à 1 : 18.1%
```

**Étape 3 — la contamination des paniers.** 6 % des paniers sont multipliés par 10 (une virgule mal placée).

```python
rng = np.random.default_rng(77)
dfc = df.copy()
cible = rng.choice(len(df), size=int(0.06 * len(df)), replace=False)       # 6 % de clients touchés
dfc.loc[cible, "panier_moyen"] = dfc.loc[cible, "panier_moyen"] * 10
dfc["log_panier"] = np.log(dfc["panier_moyen"])
contamine = np.zeros(len(df), dtype=bool); contamine[cible] = True
print(len(cible), "paniers corrompus sur", len(df), f"({contamine.mean():.1%})")
```
<!--sortie-->
```text
104 paniers corrompus sur 1740 (6.0%)
```
```python
m_mco_c = smf.ols("log_panier ~ a + C(canal)", data=dfc).fit()
rlm_c = smf.rlm("log_panier ~ a + C(canal)", data=dfc, M=sm.robust.norms.HuberT(t=1.345)).fit()
tab = pd.DataFrame({"MCO données propres": m_propre.params, "MCO contaminé": m_mco_c.params, "Huber contaminé": rlm_c.params})
tab_se = pd.DataFrame({"MCO données propres": m_propre.bse, "MCO contaminé": m_mco_c.bse, "Huber contaminé": rlm_c.bse})
print("Coefficients :"); print(tab.round(4).to_string())
print("\nErreurs standard :"); print(tab_se.round(4).to_string())
print(f"\nécart-type résiduel : MCO propre = {np.sqrt(m_propre.scale):.3f} | MCO contaminé = {np.sqrt(m_mco_c.scale):.3f} | échelle robuste de Huber = {rlm_c.scale:.3f}")
print(f"panier médian prédit pour un client Boutique de 36 ans : propre = {np.exp(m_propre.params['Intercept']):.1f} € | MCO contaminé = {np.exp(m_mco_c.params['Intercept']):.1f} € | Huber contaminé = {np.exp(rlm_c.params['Intercept']):.1f} €")
poids = rlm_c.weights
print(f"poids de Huber moyen : clients corrompus = {poids[contamine].mean():.2f} | clients intacts = {poids[~contamine].mean():.2f}")
```
<!--sortie-->
```text
Coefficients :
                     MCO données propres  MCO contaminé  Huber contaminé
Intercept                         4.2206         4.3898           4.2628
C(canal)[T.Site]                 -0.1571        -0.1853          -0.1573
C(canal)[T.Réseaux]              -0.3368        -0.3919          -0.3527
a                                 0.0092         0.0088           0.0091

Erreurs standard :
                     MCO données propres  MCO contaminé  Huber contaminé
Intercept                         0.0175         0.0314           0.0201
C(canal)[T.Site]                  0.0231         0.0414           0.0265
C(canal)[T.Réseaux]               0.0225         0.0403           0.0258
a                                 0.0008         0.0015           0.0010

écart-type résiduel : MCO propre = 0.370 | MCO contaminé = 0.665 | échelle robuste de Huber = 0.402
panier médian prédit pour un client Boutique de 36 ans : propre = 68.1 € | MCO contaminé = 80.6 € | Huber contaminé = 71.0 €
poids de Huber moyen : clients corrompus = 0.24 | clients intacts = 0.97
```
```python hide
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.scatter(dfc.loc[~contamine, "age"], dfc.loc[~contamine, "log_panier"], s=7, color=GRIS, alpha=0.5, label="paniers corrects")
ax.scatter(dfc.loc[contamine, "age"], dfc.loc[contamine, "log_panier"], s=14, color=ROUGE, alpha=0.8, label="paniers corrompus (× 10)")
s1 = smf.ols("log_panier ~ a", data=df).fit()
s2 = smf.ols("log_panier ~ a", data=dfc).fit()
s3 = smf.rlm("log_panier ~ a", data=dfc, M=sm.robust.norms.HuberT(t=1.345)).fit()
xa = np.linspace(18, 75, 50)
for m, col, nom, ls in [(s1, ENCRE, "MCO, données propres", "-"), (s2, ORANGE, "MCO, données contaminées", "-"), (s3, BLEU, "Huber, données contaminées", "--")]:
    ax.plot(xa, m.params["Intercept"] + m.params["a"] * (xa - 36), color=col, lw=2.2, ls=ls, label=nom)
ax.set_xlabel("âge (ans)"); ax.set_ylabel("log du panier moyen")
ax.legend(frameon=False, fontsize=8.5, loc="lower right", ncol=2)
ax.set_ylim(1.5, 7.6)
plt.savefig("figures/ch01-robuste-contamination.png", dpi=200, bbox_inches="tight")
print("pente (MCO propre) =", round(s1.params["a"], 4), "| (MCO contaminé) =", round(s2.params["a"], 4), "| (Huber contaminé) =", round(s3.params["a"], 4))
print("constante (MCO propre) =", round(s1.params["Intercept"], 3), "| (MCO contaminé) =", round(s2.params["Intercept"], 3), "| (Huber contaminé) =", round(s3.params["Intercept"], 3))
```
<!--sortie-->
```text
pente (MCO propre) = 0.009 | (MCO contaminé) = 0.0086 | (Huber contaminé) = 0.0092
constante (MCO propre) = 4.033 | (MCO contaminé) = 4.171 | (Huber contaminé) = 4.07
```

![Log-panier selon l'âge avec 6 % de paniers corrompus : droites des moindres carrés et de Huber.](figures/ch01-robuste-contamination.png)

**Étape 4 — la limite : les âges mal saisis.** Ils créent des points à très fort levier, contre lesquels Huber ne protège pas.

```python
rng = np.random.default_rng(78)
dfl = df.copy()
cible_l = rng.choice(len(df), size=int(0.01 * len(df)), replace=False)
dfl.loc[cible_l, "age"] = dfl.loc[cible_l, "age"] * 10
dfl["a"] = dfl["age"] - 36
print(len(cible_l), "âges corrompus ; âge maximal après contamination :", int(dfl["age"].max()), "ans")
m_mco_l = smf.ols("log_panier ~ a + C(canal)", data=dfl).fit()
rlm_l = smf.rlm("log_panier ~ a + C(canal)", data=dfl, M=sm.robust.norms.HuberT(t=1.345)).fit()
print(pd.DataFrame({"MCO propre": m_propre.params, "MCO âges corrompus": m_mco_l.params, "Huber âges corrompus": rlm_l.params}).round(4).to_string())
print(f"coefficient de l'âge : propre = {m_propre.params['a']:.4f} | MCO corrompu = {m_mco_l.params['a']:.4f} | Huber corrompu = {rlm_l.params['a']:.4f}")
print(f"levier maximal : {m_mco_l.get_influence().hat_matrix_diag.max():.3f} (levier moyen = {4/len(dfl):.4f})")
```
<!--sortie-->
```text
17 âges corrompus ; âge maximal après contamination : 640 ans
                     MCO propre  MCO âges corrompus  Huber âges corrompus
Intercept                4.2206              4.2156                4.2126
C(canal)[T.Site]        -0.1571             -0.1575               -0.1603
C(canal)[T.Réseaux]     -0.3368             -0.3349               -0.3338
a                        0.0092              0.0008                0.0009
coefficient de l'âge : propre = 0.0092 | MCO corrompu = 0.0008 | Huber corrompu = 0.0009
levier maximal : 0.126 (levier moyen = 0.0023)
```

### Application 1.11 — La régression quantile (section 1.6.5)

**Objectif.** Décrire l'effet du canal Réseaux sur toute la distribution du panier, en euros puis en logarithme.

```python
taus = [0.1, 0.25, 0.5, 0.75, 0.9]
res_niveau, res_log = [], []
for tau in taus:
    qn = smf.quantreg("panier_moyen ~ a + C(canal)", data=df).fit(q=tau)
    ql = smf.quantreg("log_panier ~ a + C(canal)", data=df).fit(q=tau)
    res_niveau.append((tau, qn.params["C(canal)[T.Réseaux]"], *qn.conf_int().loc["C(canal)[T.Réseaux]"]))
    res_log.append((tau, ql.params["C(canal)[T.Réseaux]"], *ql.conf_int().loc["C(canal)[T.Réseaux]"]))
rn = pd.DataFrame(res_niveau, columns=["tau", "coef", "bas", "haut"]).set_index("tau")
rl = pd.DataFrame(res_log, columns=["tau", "coef", "bas", "haut"]).set_index("tau")
mco_n = smf.ols("panier_moyen ~ a + C(canal)", data=df).fit()
print("Effet de Réseaux (par rapport à la Boutique) sur le panier en €, par quantile :")
print(rn.round(2).to_string())
print(f"(MCO, effet sur la moyenne : {mco_n.params['C(canal)[T.Réseaux]']:.2f} €)")
print("\nEffet de Réseaux sur le log du panier, par quantile :")
print(rl.round(3).to_string())
print(f"(MCO, effet sur la moyenne du log : {m_propre.params['C(canal)[T.Réseaux]']:.3f})")
```
<!--sortie-->
```text
Effet de Réseaux (par rapport à la Boutique) sur le panier en €, par quantile :
       coef    bas   haut
tau                      
0.10 -13.50 -16.18 -10.82
0.25 -14.40 -16.92 -11.89
0.50 -18.27 -21.44 -15.09
0.75 -24.22 -28.42 -20.02
0.90 -33.87 -40.70 -27.04
(MCO, effet sur la moyenne : -20.81 €)

Effet de Réseaux sur le log du panier, par quantile :
       coef    bas   haut
tau                      
0.10 -0.373 -0.448 -0.298
0.25 -0.331 -0.387 -0.275
0.50 -0.310 -0.369 -0.252
0.75 -0.339 -0.400 -0.278
0.90 -0.372 -0.446 -0.299
(MCO, effet sur la moyenne du log : -0.337)
```
```python hide
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0))
for ax, r, ref, titre, yl in [(ax1, rn, mco_n.params["C(canal)[T.Réseaux]"], "Panier en €", "effet de Réseaux (€)"),
                              (ax2, rl, m_propre.params["C(canal)[T.Réseaux]"], "Log du panier", "effet de Réseaux (log)")]:
    ax.fill_between(r.index, r["bas"], r["haut"], color=BLEU, alpha=0.2)
    ax.plot(r.index, r["coef"], "o-", color=BLEU, lw=2, label="régression quantile")
    ax.axhline(ref, color=ORANGE, lw=1.8, ls="--", label="moindres carrés (moyenne)")
    ax.set_xlabel("quantile τ du panier (0,1 = petits paniers ; 0,9 = grands paniers)"); ax.set_ylabel(yl); ax.set_title(titre, fontsize=10.5)
ax1.legend(frameon=False, fontsize=8.5, loc="lower left")
plt.tight_layout()
plt.savefig("figures/ch01-regression-quantile.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Effet du canal Réseaux selon le quantile du panier, en euros (à gauche) et en log (à droite).](figures/ch01-regression-quantile.png)

### Application 1.12 — Points relais : un modèle mixte de bout en bout (section 1.7)

**Objectif.** Simuler 30 points relais de tailles inégales, comparer trois traitements des groupes (mise en commun totale, nulle, partielle), ajuster un modèle à intercept puis à pente aléatoires, vérifier la formule du rétrécissement et mesurer par simulation le danger d'ignorer les groupes.

**Étape 1 — simuler les relais.** Le modèle vrai : $\text{note}_{ij}=12+1{,}2\,\text{urbain}_j+u_{0j}+(-0{,}7+u_{1j})(\text{délai}_{ij}-5)+\varepsilon_{ij}$.

```python
import warnings
```
```python
# Simulation des 30 points relais (graine fixe)
rng = np.random.default_rng(41)
J = 30
tailles = np.clip(np.round(rng.lognormal(np.log(12), 0.8, J)), 3, 60).astype(int)    # commandes par relais (très inégal)
urbain = (rng.random(J) < 0.5).astype(int)
u0 = rng.normal(0, 1.6, J)                                                           # vrai niveau de base de chaque relais
u1 = rng.normal(0, 0.3, J)                                                           # vraie sensibilité au retard de chaque relais
lignes = []
for j in range(J):
    delai = rng.integers(1, 11, tailles[j])
    note = 12 + 1.2 * urbain[j] + u0[j] + (-0.7 + u1[j]) * (delai - 5) + rng.normal(0, 1.8, tailles[j])
    for d, y in zip(delai, note):
        lignes.append((f"R{j + 1:02d}", urbain[j], int(d), round(float(y), 2)))
rel = pd.DataFrame(lignes, columns=["relais", "urbain", "delai", "note"])
rel.to_csv("donnees/ch01-relais.csv", index=False)         # fichier fourni avec le livre (lu aussi par R plus bas)
rel["dc"] = rel["delai"] - 5                                # délai centré : 0 = délai de 5 jours
print(rel.shape, "| relais :", rel["relais"].nunique(), "| relais urbains :", int(urbain.sum()))
print("commandes par relais : min =", tailles.min(), "| médiane =", int(np.median(tailles)), "| max =", tailles.max())
print("écart-type RÉALISÉ des 30 vrais niveaux de base u0 :", round(u0.std(ddof=1), 2), "(la loi dont ils sont tirés a un écart-type de 1,6)")
print(rel.head(5).to_string(index=False))
```
<!--sortie-->
```text
(484, 5) | relais : 30 | relais urbains : 14
commandes par relais : min = 4 | médiane = 11 | max = 58
écart-type RÉALISÉ des 30 vrais niveaux de base u0 : 1.31 (la loi dont ils sont tirés a un écart-type de 1,6)
relais  urbain  delai  note  dc
   R01       0      6 12.57   1
   R01       0      4 11.23  -1
   R01       0      8  4.98   3
   R01       0     10  7.56   5
   R02       1      6  9.91   1
```

**Étape 2 — mise en commun totale ou nulle.**

```python
m_commun = smf.ols("note ~ dc + urbain", data=rel).fit()                           # ignore les groupes
m_separe = smf.ols("note ~ dc + C(relais)", data=rel).fit()                         # une indicatrice par relais (urbain y est absorbé)
print("Mise en commun totale (MCO, groupes ignorés) :")
print(pd.DataFrame({"coef": m_commun.params, "erreur standard": m_commun.bse, "IC bas": m_commun.conf_int()[0], "IC haut": m_commun.conf_int()[1]}).round(3).to_string())
print(f"\nrésidu : s = {np.sqrt(m_commun.scale):.2f}")
print("\nPas de mise en commun : l'effet « urbain » n'est plus estimable (il est confondu avec les indicatrices de relais).")
print(f"coefficient du délai avec indicatrices de relais : {m_separe.params['dc']:.3f} (erreur standard {m_separe.bse['dc']:.3f})")
```
<!--sortie-->
```text
Mise en commun totale (MCO, groupes ignorés) :
             coef  erreur standard  IC bas  IC haut
Intercept  12.644            0.152  12.345   12.943
dc         -0.721            0.039  -0.796   -0.645
urbain      0.482            0.224   0.043    0.922

résidu : s = 2.44

Pas de mise en commun : l'effet « urbain » n'est plus estimable (il est confondu avec les indicatrices de relais).
coefficient du délai avec indicatrices de relais : -0.703 (erreur standard 0.034)
```

**Étape 3 — l'ICC : les groupes comptent-ils ?** D'abord les six villes (réponse : non), puis les relais (réponse : oui).

```python
clients = pd.read_csv("donnees/clients.csv")
cl = clients[clients["nb_commandes_an"] > 0].copy().reset_index(drop=True)
cl["canal"] = pd.Categorical(cl["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
cl["a"] = cl["age"] - 36
cl["log_panier"] = np.log(cl["panier_moyen"])
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    m_ville = smf.mixedlm("log_panier ~ a + C(canal)", cl, groups=cl["ville"]).fit(reml=True)
tau2_v, sigma2_v = m_ville.cov_re.iloc[0, 0], m_ville.scale
print(f"clients groupés par ville : variance entre villes tau² = {tau2_v:.5f} | variance résiduelle sigma² = {sigma2_v:.4f}")
print(f"ICC = tau²/(tau² + sigma²) = {tau2_v / (tau2_v + sigma2_v):.4f}")
```
<!--sortie-->
```text
clients groupés par ville : variance entre villes tau² = 0.00000 | variance résiduelle sigma² = 0.1373
ICC = tau²/(tau² + sigma²) = 0.0000
```
```python
m_ri = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"]).fit(reml=True)
tau2, sigma2 = m_ri.cov_re.iloc[0, 0], m_ri.scale
print(m_ri.summary().tables[1])
print(f"\nvariance entre relais tau² = {tau2:.3f} (écart-type {np.sqrt(tau2):.2f}) | variance résiduelle sigma² = {sigma2:.3f} (écart-type {np.sqrt(sigma2):.2f})")
print(f"ICC = {tau2 / (tau2 + sigma2):.3f} : environ {100 * tau2 / (tau2 + sigma2):.0f} % de la variance des notes (après effet du délai et du type de relais) est due au relais")
```
<!--sortie-->
```text
            Coef. Std.Err.        z  P>|z|  [0.025  0.975]
Intercept  12.489    0.364   34.284  0.000  11.775  13.202
dc         -0.710    0.034  -21.047  0.000  -0.776  -0.644
urbain      0.377    0.534    0.705  0.481  -0.671   1.424
Group Var   1.711    0.280                                

variance entre relais tau² = 1.711 (écart-type 1.31) | variance résiduelle sigma² = 4.350 (écart-type 2.09)
ICC = 0.282 : environ 28 % de la variance des notes (après effet du délai et du type de relais) est due au relais
```

**Étape 4 — le rétrécissement (BLUP).** Pour un relais de $n_j$ commandes, $\hat u_j=\frac{\tau^2}{\tau^2+\sigma^2/n_j}\,\bar r_j$ ; on le vérifie, puis on compare à la vérité.

```python
beta_ri = m_ri.fe_params
rel["r"] = rel["note"] - (beta_ri["Intercept"] + beta_ri["dc"] * rel["dc"] + beta_ri["urbain"] * rel["urbain"])      # résidus « fixes »
groupes = rel.groupby("relais")["r"].agg(["mean", "size"]).rename(columns={"mean": "r_bar", "size": "n_j"})
groupes["B"] = tau2 / (tau2 + sigma2 / groupes["n_j"])
groupes["u_formule"] = groupes["B"] * groupes["r_bar"]
groupes["u_statsmodels"] = [m_ri.random_effects[g]["Group"] for g in groupes.index]
groupes["u_vrai"] = u0
print("formule du BLUP = statsmodels :", np.allclose(groupes["u_formule"], groupes["u_statsmodels"]))
print(groupes.sort_values("n_j").iloc[[0, 1, 2, 14, 27, 28, 29]].round(3).to_string())
erreur_sans = np.sqrt(np.mean((groupes["r_bar"] - groupes["u_vrai"])**2))
erreur_part = np.sqrt(np.mean((groupes["u_statsmodels"] - groupes["u_vrai"])**2))
print(f"\nerreur quadratique moyenne par rapport aux vrais niveaux u0 :  sans mise en commun = {erreur_sans:.3f} | mise en commun partielle = {erreur_part:.3f}")
petits = groupes["n_j"] <= 8
print(f"  pour les {petits.sum()} petits relais (8 commandes ou moins) :   sans = {np.sqrt(np.mean((groupes.loc[petits, 'r_bar'] - groupes.loc[petits, 'u_vrai'])**2)):.3f} | partielle = {np.sqrt(np.mean((groupes.loc[petits, 'u_statsmodels'] - groupes.loc[petits, 'u_vrai'])**2)):.3f}")
```
<!--sortie-->
```text
formule du BLUP = statsmodels : True
        r_bar  n_j      B  u_formule  u_statsmodels  u_vrai
relais                                                     
R01    -1.983    4  0.611     -1.213         -1.213  -0.937
R05     0.997    4  0.611      0.610          0.610  -0.683
R10    -2.442    4  0.611     -1.493         -1.493   0.413
R19    -0.426   11  0.812     -0.346         -0.346   0.624
R12    -0.644   31  0.924     -0.595         -0.595  -0.548
R16     1.386   56  0.957      1.326          1.326   1.867
R29     1.257   58  0.958      1.204          1.204   0.725

erreur quadratique moyenne par rapport aux vrais niveaux u0 :  sans mise en commun = 0.900 | mise en commun partielle = 0.765
  pour les 10 petits relais (8 commandes ou moins) :   sans = 1.273 | partielle = 1.031
```
```python hide
ordre = groupes.sort_values("n_j").reset_index()
fig, ax = plt.subplots(figsize=(8.8, 4.8))
x = np.arange(len(ordre))
for i, ligne in ordre.iterrows():
    ax.plot([i, i], [ligne["r_bar"], ligne["u_statsmodels"]], color=GRIS, lw=1.2, zorder=1)
ax.scatter(x, ordre["r_bar"], facecolors="none", edgecolors=ORANGE, s=45, lw=1.6, zorder=3, label="sans mise en commun (moyenne du relais)")
ax.scatter(x, ordre["u_statsmodels"], color=BLEU, s=32, zorder=4, label="mise en commun partielle (BLUP)")
ax.scatter(x, ordre["u_vrai"], marker="_", color=ENCRE, s=130, lw=2, zorder=5, label="vérité (connue car simulée)")
ax.axhline(0, color=GRIS, lw=1)
ax.set_xticks(x); ax.set_xticklabels(ordre["n_j"], fontsize=7.5)
ax.set_xlabel("nombre de commandes du relais (relais classés du plus petit au plus grand)")
ax.set_ylabel("niveau de base du relais (écart à la moyenne, en points)")
ax.set_ylim(-3.3, 3.8)                                    # marge en haut pour la légende
ax.legend(frameon=False, loc="upper left", fontsize=8.5)
plt.savefig("figures/ch01-retrecissement.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Niveau de base des 30 relais : moyennes brutes, estimations rétrécies et vérité.](figures/ch01-retrecissement.png)

**Étape 5 — la pente aléatoire et le test du rapport de vraisemblance.** Sous $H_0$ la variance est au bord de l'espace des paramètres : mélange 50/50 de $\chi^2_1$ et $\chi^2_2$.

```python
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    m_rs = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"], re_formula="~dc").fit(reml=True, method="lbfgs")
print("Converge :", m_rs.converged)
print(m_rs.summary().tables[1])
G = m_rs.cov_re
print(f"\nécart-type des niveaux de base : {np.sqrt(G.iloc[0, 0]):.3f} (vrai : 1,6) | écart-type des pentes : {np.sqrt(G.iloc[1, 1]):.3f} (vrai : 0,3)")
print(f"corrélation niveau de base / pente : {G.iloc[0, 1] / np.sqrt(G.iloc[0, 0] * G.iloc[1, 1]):.2f} (vraie : 0) | écart-type résiduel : {np.sqrt(m_rs.scale):.3f} (vrai : 1,8)")
```
<!--sortie-->
```text
Converge : True
                 Coef. Std.Err.        z  P>|z|  [0.025  0.975]
Intercept       12.596    0.339   37.166  0.000  11.932  13.260
dc              -0.760    0.064  -11.806  0.000  -0.886  -0.634
urbain           0.277    0.501    0.553  0.581  -0.705   1.259
Group Var        1.427    0.252                                
Group x dc Cov   0.072    0.044                                
dc Var           0.079    0.017                                

écart-type des niveaux de base : 1.195 (vrai : 1,6) | écart-type des pentes : 0.281 (vrai : 0,3)
corrélation niveau de base / pente : 0.21 (vraie : 0) | écart-type résiduel : 1.930 (vrai : 1,8)
```
```python
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    ml_ri = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"]).fit(reml=False)      # optimiseur par défaut (voir la remarque ci-dessous)
    ml_rs = smf.mixedlm("note ~ dc + urbain", rel, groups=rel["relais"], re_formula="~dc").fit(reml=False, method="lbfgs")
LR = 2 * (ml_rs.llf - ml_ri.llf)
# Sous H0, la variance de la pente est sur le bord de l'espace des paramètres (>= 0) : loi limite = mélange 50/50 de chi²(1) et chi²(2)
p_val = 0.5 * stats.chi2.sf(LR, 1) + 0.5 * stats.chi2.sf(LR, 2)
print(f"log-vraisemblance (ML) : intercept aléatoire = {ml_ri.llf:.2f} | intercept + pente aléatoires = {ml_rs.llf:.2f}")
print(f"LR = {LR:.2f} | p-valeur (mélange de chi²) = {p_val:.2e}")
print(f"AIC : {-2 * ml_ri.llf + 2 * 5:.1f} (intercept aléatoire, 5 paramètres) contre {-2 * ml_rs.llf + 2 * 7:.1f} (intercept + pente, 7 paramètres)")
```
<!--sortie-->
```text
log-vraisemblance (ML) : intercept aléatoire = -1067.99 | intercept + pente aléatoires = -1047.41
LR = 41.15 | p-valeur (mélange de chi²) = 6.50e-10
AIC : 2146.0 (intercept aléatoire, 5 paramètres) contre 2108.8 (intercept + pente, 7 paramètres)
```
```python hide
fig, ax = plt.subplots(figsize=(8.0, 4.8))
dd = np.arange(-4, 5.01, 1.0)
for j, g in enumerate(sorted(rel["relais"].unique())):
    re = m_rs.random_effects[g]
    u_urb = urbain[j]
    y_g = m_rs.fe_params["Intercept"] + m_rs.fe_params["urbain"] * u_urb + re["Group"] + (m_rs.fe_params["dc"] + re["dc"]) * dd
    ax.plot(dd + 5, y_g, color=ORANGE if u_urb else AQUA, lw=0.9, alpha=0.55)
ax.plot(dd + 5, m_rs.fe_params["Intercept"] + m_rs.fe_params["dc"] * dd, color=ENCRE, lw=3, label="effet moyen (effets fixes), relais non urbain")
ax.scatter(rel["delai"], rel["note"], s=6, color=GRIS, alpha=0.35)
ax.plot([], [], color=ORANGE, lw=1.4, label="relais urbains"); ax.plot([], [], color=AQUA, lw=1.4, label="relais non urbains")
ax.set_xlabel("délai de livraison (jours)"); ax.set_ylabel("note de satisfaction (sur 20)")
ax.legend(frameon=False, fontsize=8.5, loc="lower left")
ax.set_xlim(0.7, 10.3)
plt.savefig("figures/ch01-droites-par-relais.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Droites de régression propres à chaque relais autour de l'effet moyen.](figures/ch01-droites-par-relais.png)

**Étape 6 — la même chose avec `lme4` en R.**

```r
suppressMessages(library(lme4))
d <- read.csv("donnees/ch01-relais.csv")
d$dc <- d$delai - 5
m <- lmer(note ~ dc + urbain + (1 + dc | relais), data = d)
print(round(fixef(m), 4))
print(VarCorr(m), digits = 4)
cat("log-vraisemblance REML :", round(as.numeric(logLik(m)), 3), "\n")
```
<!--sortie-->
```text
(Intercept)          dc      urbain 
    12.5960     -0.7598      0.2769 
 Groups   Name        Std.Dev. Corr
 relais   (Intercept) 1.1948       
          dc          0.2812   0.21
 Residual             1.9299       
log-vraisemblance REML : -1049.555 
```

**Étape 7 — pourquoi ignorer les groupes est dangereux.** On simule 300 jeux de données où le type de relais n'a **aucun** effet : la régression ordinaire rejette dans plus de la moitié des cas.

```python
rng2 = np.random.default_rng(2024)
R = 300
rej_mco, rej_mixte, z_mixte, tau2_est = 0, 0, [], []
degenere_lbfgs, degenere_defaut = 0, 0
groupe = np.repeat(np.arange(J), tailles)
urb_obs = urbain[groupe]
dc_obs = rel["dc"].to_numpy()
for r in range(R):
    u = rng2.normal(0, 1.6, J)
    y = 12 + u[groupe] - 0.7 * dc_obs + rng2.normal(0, 1.8, len(groupe))                   # AUCUN effet du type de relais
    d_sim = pd.DataFrame({"note": y, "dc": dc_obs, "urbain": urb_obs, "g": groupe})
    p_mco = sm.OLS(y, sm.add_constant(d_sim[["dc", "urbain"]])).fit().pvalues["urbain"]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        f = smf.mixedlm("note ~ dc + urbain", d_sim, groups=d_sim["g"]).fit(reml=True)                # optimiseur par défaut
        if r < 60:                                                                                   # même ajustement avec lbfgs, sur 60 répétitions
            f2 = smf.mixedlm("note ~ dc + urbain", d_sim, groups=d_sim["g"]).fit(reml=True, method="lbfgs")
            degenere_lbfgs += f2.cov_re.iloc[0, 0] < 1e-6
            degenere_defaut += f.cov_re.iloc[0, 0] < 1e-6
    rej_mco += p_mco < 0.05
    rej_mixte += f.pvalues["urbain"] < 0.05
    z_mixte.append(f.params["urbain"] / f.bse["urbain"])
    tau2_est.append(f.cov_re.iloc[0, 0])
```
```python
print(f"quand AUCUN effet n'existe, part de tests « significatifs à 5 % » sur la variable urbain, sur {R} simulations :")
print(f"  régression ordinaire (groupes ignorés) : {rej_mco / R:.1%}")
print(f"  modèle mixte (intercept aléatoire)     : {rej_mixte / R:.1%}   | écart-type de la statistique z : {np.std(z_mixte):.2f} (théorie : 1)")
print(f"variance entre relais estimée en moyenne : {np.mean(tau2_est):.2f} (vraie valeur : {1.6**2:.2f})")
print(f"sur 60 répétitions, ajustements qui dégénèrent (variance estimée = 0) : optimiseur par défaut = {degenere_defaut}/60 | lbfgs = {degenere_lbfgs}/60")
```
<!--sortie-->
```text
quand AUCUN effet n'existe, part de tests « significatifs à 5 % » sur la variable urbain, sur 300 simulations :
  régression ordinaire (groupes ignorés) : 55.3%
  modèle mixte (intercept aléatoire)     : 6.7%   | écart-type de la statistique z : 1.04 (théorie : 1)
variance entre relais estimée en moyenne : 2.54 (vraie valeur : 2.56)
sur 60 répétitions, ajustements qui dégénèrent (variance estimée = 0) : optimiseur par défaut = 0/60 | lbfgs = 43/60
```

## Exercices

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. Les exercices 1.1 à 1.8, 1.11 et 1.12 se résolvent surtout à la main ; les exercices 1.9, 1.10 et 1.13 demandent le code.

### Exercice 1.1 ⭐ — Moindres carrés à la main (section 1.1)

Trois commandes ont $x$ articles et un montant $y$ en € : $(1,\,2),\ (2,\,3),\ (4,\,7)$. (a) Écrivez $\mathbf X$ et $\mathbf y$, calculez $\mathbf X^\top\mathbf X$ et $\mathbf X^\top\mathbf y$, puis $\hat{\boldsymbol\beta}=(\hat\beta_0,\hat\beta_1)$. (b) Calculez les valeurs ajustées et les résidus, et vérifiez que $\mathbf X^\top\hat{\boldsymbol\varepsilon}=\mathbf 0$. (c) Calculez le $R^2$. (d) Quel montant prévoit-on pour 3 articles ?

### Exercice 1.2 ⭐ — Lire un modèle en log (section 1.1)

Le modèle `log_panier ~ a + C(canal)` du 1.1.7 donne : constante $4{,}2206$, Site $-0{,}1571$, Réseaux $-0{,}3368$, âge centré $0{,}0092$ par année. (a) Exprimez **exactement** (en pourcentage) l'effet du Site et de Réseaux par rapport à la boutique. (b) Quel effet pour 10 années d'âge de plus ? (c) Quel est le panier **médian** prédit d'une cliente de 46 ans acquise par le Site ? (d) Pourquoi dit-on « médian » et non « moyen » ?

### Exercice 1.3 ⭐⭐ — Régression simple (section 1.1)

Dans la régression simple $y=\beta_0+\beta_1x+\varepsilon$, démontrez que $\hat\beta_1=r\,\dfrac{s_y}{s_x}$ et que $R^2=r^2$, où $r$ est le coefficient de corrélation de Pearson entre $x$ et $y$. Vérifiez-le sur les quatre commandes du 1.1.1 ($x=1,2,3,4$ ; $y=22,41,66,79$).

### Exercice 1.4 ⭐⭐ — Test et intervalle à la main (section 1.2)

Pour Réseaux, `statsmodels` donne le coefficient $-0{,}3368$ et son erreur standard $0{,}0225$, avec $n-p=1736$ degrés de liberté (quantile de Student à 97,5 % : $1{,}961$). (a) Calculez la statistique $t$ et dites si l'on rejette $H_0:\beta=0$ à 5 %. (b) Donnez l'intervalle de confiance à 95 % de $\beta$, puis de l'effet multiplicatif $e^\beta$ exprimé en pourcentage. (c) Pour l'âge : coefficient $0{,}0092$, erreur standard $0{,}00085$ : quelle est la statistique $t$ ?

### Exercice 1.5 ⭐⭐ — Test $F$ (section 1.2)

Le modèle réduit `log_panier ~ a` a une somme des carrés résiduelle $\text{SCR}_0=269{,}94$ ; le modèle complet `log_panier ~ a + C(canal)` a $\text{SCR}_1=238{,}30$, avec $n-p_1=1736$. (a) Calculez la statistique $F$ du test « le canal est inutile ». Combien y a-t-il de contraintes $q$ ? (b) La valeur critique de $F_{2,\,1736}$ à 5 % est environ 3,0 : concluez. (c) Si $\text{SCR}_1$ valait 269,70 au lieu de 238,30 (le canal améliorait à peine l'ajustement), que vaudrait $F$ ? Que concluriez-vous ?

### Exercice 1.6 ⭐⭐ — Levier (section 1.3)

Quatre clients ont pour âge centré $x=(1,\,2,\,3,\,10)$. (a) Calculez le levier $h_{ii}=\frac1n+\frac{(x_i-\bar x)^2}{\sum_k(x_k-\bar x)^2}$ de chacun. Vérifiez que leur somme vaut $p=2$. (b) Quel client a le plus d'influence potentielle ? (c) Si $y_4$ augmente de 1, de combien augmente la valeur ajustée $\hat y_4$ ?

### Exercice 1.7 ⭐⭐ — PRESS (section 1.4)

Reprenez les trois points de l'exercice 1. (a) Calculez les leviers $h_{ii}$. (b) Calculez les erreurs de prédiction « sans le point » $\hat\varepsilon_i/(1-h_{ii})$ et la somme PRESS. (c) Vérifiez l'une d'elles en réajustant la droite sur les deux autres points. (d) Comparez PRESS à la somme des carrés résiduelle : que constatez-vous ?

### Exercice 1.8 ⭐⭐ — Multicolinéarité (section 1.3)

(a) Une variable explicative $x_j$ est expliquée à 99,5 % par les autres ($R_j^2=0{,}995$) : donnez son VIF et le facteur par lequel son erreur standard est multipliée. (b) Avec deux variables explicatives de corrélation 0,9, que vaut leur VIF ? (c) **Code.** Les huit questions de l'enquête de satisfaction (`q1` à `q8`) sont-elles gravement colinéaires entre elles ? Calculez leurs VIF.

### Exercice 1.9 ⭐⭐ — Prédire une moyenne en euros (section 1.1)

Avec le modèle `log_panier ~ a + C(canal)` : (a) donnez, pour un client **Réseaux de 25 ans**, le panier médian prédit ; (b) calculez une prédiction du panier **moyen** avec la correction de Duan ; (c) comparez à la moyenne observée des clients Réseaux âgés de 23 à 27 ans. Laquelle des deux prédictions est la plus proche, et pourquoi ?

### Exercice 1.10 ⭐⭐⭐ — Régression sur les ventes mensuelles (section 1.3)

Avec `donnees/ventes_mensuelles.csv` (120 mois), ajustez `log(ca) ~ t + C(mois) + promo + covid`, où `t` est le numéro du mois (0 à 119), `mois` le mois civil (1 à 12), `promo` indique un mois de promotion et `covid` les mois de mars à juin 2020. (a) Quelle est la croissance annuelle estimée ? (b) Quel est l'effet estimé de décembre par rapport à janvier (en facteur multiplicatif) ? (c) Quel est l'effet du confinement de 2020 sur les ventes, en pourcentage ? (d) Que disent le $R^2$ et le test de Durbin-Watson sur ce modèle ? Reste-t-il de la structure dans les résidus ?

### Exercice 1.11 ⭐⭐⭐ — Ridge, cas orthonormal (section 1.5)

Les colonnes de $\mathbf X$ sont orthonormales ($\mathbf X^\top\mathbf X=\mathbf I$). (a) Montrez que $\hat\beta_j^{\text{ridge}}=\hat\beta_j^{\text{MCO}}/(1+\lambda)$. (b) Pour un coefficient vrai $\beta=2$ et $\sigma=1$, calculez l'erreur quadratique moyenne $\text{EQM}(\lambda)=\dfrac{\lambda^2\beta^2+\sigma^2}{(1+\lambda)^2}$ pour $\lambda=0$, $0{,}25$ et $1$. (c) Quel $\lambda$ la minimise ? Vérifiez par le code sur une grille.

### Exercice 1.12 ⭐⭐ — Modèle mixte, calcul à la main (section 1.7)

Dans un modèle à intercept aléatoire, $\tau^2=2{,}0$ (variance entre groupes) et $\sigma^2=6{,}0$ (variance résiduelle). (a) Calculez l'ICC. (b) Un relais a $n_j=9$ commandes et une moyenne de résidus « fixes » $\bar r_j=3{,}2$ : calculez le facteur de rétrécissement $B_j$ et le BLUP $\hat u_j$. (c) Même question pour un relais de $n_j=2$ commandes avec la même moyenne de résidus. (d) Avec $J=20$ relais de 9 commandes chacun, quel est l'effectif effectif pour estimer une variable qui ne varie qu'entre relais ?

### Exercice 1.13 ⭐⭐ — Robustesse, simulation (section 1.6)

Simulez $n=100$ points $y=2+1{,}5x+\varepsilon$ ($x$ uniforme sur $[0,10]$, $\varepsilon\sim\mathcal N(0,1)$, graine 5), puis ajoutez 25 à $y$ pour 5 points tirés au hasard. Comparez les coefficients des moindres carrés, de Huber et de la régression médiane sur les données propres et corrompues. Que constatez-vous ?


## Corrigés

### Corrigé 1.1

(a) $\mathbf X=\begin{pmatrix}1&1\\1&2\\1&4\end{pmatrix}$, $\mathbf y=(2,3,7)^\top$. $\mathbf X^\top\mathbf X=\begin{pmatrix}3&7\\7&21\end{pmatrix}$ (déterminant $63-49=14$), $\mathbf X^\top\mathbf y=(12,\ 2+6+28)^\top=(12,\,36)^\top$. Donc $\hat{\boldsymbol\beta}=\frac1{14}\begin{pmatrix}21&-7\\-7&3\end{pmatrix}\begin{pmatrix}12\\36\end{pmatrix}=\frac1{14}\begin{pmatrix}252-252\\-84+108\end{pmatrix}=\begin{pmatrix}0\\12/7\end{pmatrix}$ : la droite passe **exactement par l'origine** : $\hat y=\frac{12}7x\approx1{,}714\,x$. (b) Ajustées : $\frac{12}7,\ \frac{24}7,\ \frac{48}7$ ; résidus : $\frac27,\ -\frac37,\ \frac17$ (soit $0{,}286;\ -0{,}429;\ 0{,}143$). Somme : $0$ ✓. $\sum x_i\hat\varepsilon_i=\frac27-\frac67+\frac47=0$ ✓. (c) $\text{SCR}=\frac{4+9+1}{49}=\frac27$ ; $\bar y=4$, $\text{SCT}=4+1+9=14$ ; $R^2=1-\frac{2/7}{14}=\frac{48}{49}\approx0{,}980$. (d) $\hat y(3)=\frac{36}7\approx5{,}14$ €.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")

x = np.array([1.0, 2, 4]); y = np.array([2.0, 3, 7])
X = np.column_stack([np.ones(3), x])
beta = np.linalg.solve(X.T @ X, X.T @ y)
res = y - X @ beta
print("beta =", beta.round(4), "| 12/7 =", round(12 / 7, 4))
print("résidus =", res.round(4), "| X'e =", (X.T @ res).round(10))
print("SCR =", round(res @ res, 4), "| R² =", round(1 - res @ res / ((y - y.mean())**2).sum(), 4), "| prévision en x = 3 :", round(beta[0] + 3 * beta[1], 4))
```
<!--sortie-->
```text
beta = [0.     1.7143] | 12/7 = 1.7143
résidus = [ 0.2857 -0.4286  0.1429] | X'e = [-0.  0.]
SCR = 0.2857 | R² = 0.9796 | prévision en x = 3 : 5.1429
```

### Corrigé 1.2

(a) Site : $e^{-0{,}1571}-1=-14{,}5\,\%$ ; Réseaux : $e^{-0{,}3368}-1=-28{,}6\,\%$ (et non −15,7 % et −33,7 % : l'approximation $100\beta$ est mauvaise pour de grands coefficients, 1.1.8). (b) $e^{10\times0{,}0092}-1=+9{,}6\,\%$. (c) Pour 46 ans, $a=10$ : $\hat\mu=4{,}2206-0{,}1571+10\times0{,}0092=4{,}1555$, donc $e^{4{,}1555}\approx63{,}8$ €. (d) Parce que $e^{\hat\mu}$ est la prédiction de la **médiane** de $y$ : pour la moyenne il faudrait la correction $e^{s^2/2}$ ou celle de Duan (1.1.8, et exercice 1.9).

```python
for nom, b in [("Site", -0.1571), ("Réseaux", -0.3368)]:
    print(f"{nom:10s}: {100 * (np.exp(b) - 1):+.1f} %")
print(f"10 ans d'âge : {100 * (np.exp(10 * 0.0092) - 1):+.1f} %")
print(f"panier médian prédit, 46 ans, Site : {np.exp(4.2206 - 0.1571 + 10 * 0.0092):.1f} €")
```
<!--sortie-->
```text
Site      : -14.5 %
Réseaux   : -28.6 %
10 ans d'âge : +9.6 %
panier médian prédit, 46 ans, Site : 63.8 €
```

### Corrigé 1.3

On sait (1.1.1, équations normales) que $\hat\beta_1=\dfrac{S_{xy}}{S_{xx}}$ avec $S_{xy}=\sum(x_i-\bar x)(y_i-\bar y)$ et $S_{xx}=\sum(x_i-\bar x)^2$. Or $r=\dfrac{S_{xy}}{\sqrt{S_{xx}S_{yy}}}$ et $\dfrac{s_y}{s_x}=\sqrt{S_{yy}/S_{xx}}$, donc $r\dfrac{s_y}{s_x}=\dfrac{S_{xy}}{\sqrt{S_{xx}S_{yy}}}\sqrt{\dfrac{S_{yy}}{S_{xx}}}=\dfrac{S_{xy}}{S_{xx}}=\hat\beta_1$. Pour le $R^2$ : $\hat y_i-\bar y=\hat\beta_1(x_i-\bar x)$, donc $\text{SCE}=\hat\beta_1^2S_{xx}=\dfrac{S_{xy}^2}{S_{xx}}$ et $R^2=\dfrac{\text{SCE}}{\text{SCT}}=\dfrac{S_{xy}^2}{S_{xx}S_{yy}}=r^2$. $\square$

```python
x4 = np.array([1.0, 2, 3, 4]); y4 = np.array([22.0, 41, 66, 79])
r = np.corrcoef(x4, y4)[0, 1]
b1 = np.polyfit(x4, y4, 1)[0]
print(f"r = {r:.5f} | r·sy/sx = {r * y4.std(ddof=1) / x4.std(ddof=1):.4f} | pente MCO = {b1:.4f}")
print(f"r² = {r**2:.5f} | R² du modèle = {sm.OLS(y4, sm.add_constant(x4)).fit().rsquared:.5f}")
```
<!--sortie-->
```text
r = 0.99350 | r·sy/sx = 19.6000 | pente MCO = 19.6000
r² = 0.98705 | R² du modèle = 0.98705
```

### Corrigé 1.4

(a) $t=-0{,}3368/0{,}0225=-14{,}97$ ; $|t|\gg1{,}961$ : on rejette $H_0$ (p-valeur de l'ordre de $10^{-48}$). (b) $-0{,}3368\pm1{,}961\times0{,}0225=[-0{,}381\,;\,-0{,}293]$ ; en pourcentage : $e^{-0{,}381}-1=-31{,}7\,\%$ et $e^{-0{,}293}-1=-25{,}4\,\%$ : un effet de **−25 % à −32 %**. (c) $t=0{,}0092/0{,}00085\approx10{,}8$.

```python
b, se, crit = -0.3368, 0.0225, stats.t.ppf(0.975, 1736)
print(f"t = {b / se:.2f} | p = {2 * stats.t.sf(abs(b / se), 1736):.1e} | quantile = {crit:.3f}")
lo, hi = b - crit * se, b + crit * se
print(f"IC de beta : [{lo:.3f} ; {hi:.3f}] | IC de l'effet : [{100 * (np.exp(lo) - 1):.1f} % ; {100 * (np.exp(hi) - 1):.1f} %]")
print(f"t de l'âge = {0.0092 / 0.00085:.2f}")
```
<!--sortie-->
```text
t = -14.97 | p = 9.8e-48 | quantile = 1.961
IC de beta : [-0.381 ; -0.293] | IC de l'effet : [-31.7 % ; -25.4 %]
t de l'âge = 10.82
```

### Corrigé 1.5

(a) $q=2$ (les deux coefficients du canal). $F=\dfrac{(269{,}94-238{,}30)/2}{238{,}30/1736}=\dfrac{15{,}82}{0{,}1373}\approx115{,}3$. (b) $115\gg3{,}0$ : on rejette l'hypothèse « le canal est inutile » (p-valeur de l'ordre de $10^{-47}$). (c) $F=\dfrac{(269{,}94-269{,}70)/2}{269{,}70/1736}=\dfrac{0{,}12}{0{,}1554}\approx0{,}77$, inférieur à 3,0 (et même à 1) : le canal n'apporte pas plus que du bruit, on ne rejette pas $H_0$.

```python
def F_stat(scr0, scr1, q, ddl):
    F = ((scr0 - scr1) / q) / (scr1 / ddl)
    return F, stats.f.sf(F, q, ddl)
print("cas observé  : F = %.2f, p = %.1e" % F_stat(269.94, 238.30, 2, 1736))
print("cas (c)      : F = %.2f, p = %.2f" % F_stat(269.94, 269.70, 2, 1736))
print("valeur critique F(2, 1736) à 5 % :", round(stats.f.ppf(0.95, 2, 1736), 3))
```
<!--sortie-->
```text
cas observé  : F = 115.25, p = 1.0e-47
cas (c)      : F = 0.77, p = 0.46
valeur critique F(2, 1736) à 5 % : 3.001
```

### Corrigé 1.6

(a) $\bar x=4$, $\sum(x_k-\bar x)^2=9+4+1+36=50$. $h_{11}=\frac14+\frac9{50}=0{,}43$ ; $h_{22}=\frac14+\frac4{50}=0{,}33$ ; $h_{33}=\frac14+\frac1{50}=0{,}27$ ; $h_{44}=\frac14+\frac{36}{50}=0{,}97$. Somme : $2{,}00=p$ ✓. (b) Le client d'âge 10, éloigné des autres : levier de 0,97 (presque 1). (c) $\partial\hat y_4/\partial y_4=h_{44}=0{,}97$ : la droite est presque **forcée** de passer par ce point ; $\hat y_4$ augmente de 0,97.

```python
x6 = np.array([1.0, 2, 3, 10]); X6 = np.column_stack([np.ones(4), x6])
h6 = np.diag(X6 @ np.linalg.inv(X6.T @ X6) @ X6.T)
print("leviers :", h6.round(3), "| somme =", h6.sum().round(3))
y6 = np.array([2.1, 3.9, 6.2, 20.0]); y6b = y6 + np.array([0, 0, 0, 1.0])
f1, f2 = sm.OLS(y6, X6).fit(), sm.OLS(y6b, X6).fit()
print("variation de la valeur ajustée du 4e point quand y4 augmente de 1 :", round(f2.fittedvalues[3] - f1.fittedvalues[3], 3))
```
<!--sortie-->
```text
leviers : [0.43 0.33 0.27 0.97] | somme = 2.0
variation de la valeur ajustée du 4e point quand y4 augmente de 1 : 0.97
```

### Corrigé 1.7

(a) $\bar x=7/3$, $S_{xx}=\frac{16}9+\frac19+\frac{25}9=\frac{42}9=\frac{14}3$ : $h_{11}=\frac13+\frac{16/9}{14/3}=\frac5{7}\approx0{,}714$ ; $h_{22}=\frac13+\frac{1/9}{14/3}=\frac5{14}\approx0{,}357$ ; $h_{33}=\frac13+\frac{25/9}{14/3}=\frac{13}{14}\approx0{,}929$ (somme $=2$ ✓). (b) Erreurs sans le point : $\frac{2/7}{2/7}=1$ ; $\frac{-3/7}{9/14}=-\frac23$ ; $\frac{1/7}{1/14}=2$. $\text{PRESS}=1+\frac49+4=\frac{49}9\approx5{,}44$. (c) Sans le point $(1,2)$ : la droite passe par $(2,3)$ et $(4,7)$, d'équation $y=2x-1$, et prévoit $1$ en $x=1$ : l'erreur est $2-1=1$ ✓. (d) PRESS ($5{,}44$) est près de **vingt fois** plus grand que la somme des carrés résiduelle ($2/7\approx0{,}286$) : avec 3 points seulement, l'ajustement « d'apprentissage » est trompeusement optimiste, surtout pour le point $x=4$ à fort levier (0,93), dont l'erreur sans lui est de 2 contre un résidu de 0,14.

```python
Xa = np.column_stack([np.ones(3), np.array([1.0, 2, 4])]); ya = np.array([2.0, 3, 7])
H = Xa @ np.linalg.inv(Xa.T @ Xa) @ Xa.T
e = ya - H @ ya; h = np.diag(H)
print("leviers :", h.round(3))
print("erreurs sans le point (formule) :", (e / (1 - h)).round(4), "| PRESS =", round(np.sum((e / (1 - h))**2), 4), "| 49/9 =", round(49 / 9, 4))
loo = []
for i in range(3):
    m = np.arange(3) != i
    b = np.linalg.lstsq(Xa[m], ya[m], rcond=None)[0]
    loo.append(ya[i] - Xa[i] @ b)
print("erreurs sans le point (réajustement) :", np.round(loo, 4), "| SCR =", round(e @ e, 4))
```
<!--sortie-->
```text
leviers : [0.714 0.357 0.929]
erreurs sans le point (formule) : [ 1.     -0.6667  2.    ] | PRESS = 5.4444 | 49/9 = 5.4444
erreurs sans le point (réajustement) : [ 1.     -0.6667  2.    ] | SCR = 0.2857
```

### Corrigé 1.8

(a) $\text{VIF}=\frac1{1-0{,}995}=200$ ; l'erreur standard est multipliée par $\sqrt{200}\approx14$. (b) Avec deux variables, $R_j^2=r^2=0{,}81$, donc $\text{VIF}=\frac1{0{,}19}\approx5{,}3$ : à surveiller (règle empirique : > 5). (c) Voir le code ci-dessous.

```python
from statsmodels.stats.outliers_influence import variance_inflation_factor
print("VIF (a) :", 1 / (1 - 0.995), "| racine :", round(np.sqrt(200), 1), "| VIF (b) :", round(1 / (1 - 0.9**2), 2))
enq = pd.read_csv("donnees/enquete_satisfaction.csv")
Q = sm.add_constant(enq[[f"q{i}" for i in range(1, 9)]])
vif = pd.Series([variance_inflation_factor(Q.to_numpy(), i) for i in range(1, Q.shape[1])], index=Q.columns[1:])
print(vif.round(2).to_string())
```
<!--sortie-->
```text
VIF (a) : 199.99999999999983 | racine : 14.1 | VIF (b) : 5.26
q1    1.60
q2    1.42
q3    1.47
q4    1.27
q5    1.71
q6    1.47
q7    1.63
q8    1.46
```

Les VIF des huit questions restent **modestes** (inférieurs à 2) : les questions d'un même bloc (produits d'un côté, service de l'autre) sont corrélées, mais pas au point de rendre un modèle instable. On peut donc les utiliser ensemble, ou les résumer par un score moyen comme au 1.4 (ce que l'analyse factorielle du chapitre 3 formalisera : section 3.2).

### Corrigé 1.9

(a) Panier médian prédit : $e^{\hat\mu}$ avec $\hat\mu$ la prédiction du modèle. (b) La prédiction de la moyenne s'obtient en multipliant par le facteur de Duan $\frac1n\sum_ie^{\hat\varepsilon_i}$. (c) On compare à la moyenne observée.

```python
clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])
m = smf.ols("log_panier ~ a + C(canal)", data=df).fit()
profil = pd.DataFrame({"a": [25 - 36], "canal": pd.Categorical(["Réseaux"], categories=["Boutique", "Site", "Réseaux"])})
mu = float(m.predict(profil).iloc[0])
duan = float(np.exp(m.resid).mean())
obs = df[(df["canal"] == "Réseaux") & (df["age"].between(23, 27))]["panier_moyen"]
print(f"(a) panier médian prédit      : {np.exp(mu):.2f} €")
print(f"(b) panier moyen prédit (Duan) : {np.exp(mu) * duan:.2f} €   [facteur de Duan = {duan:.4f} ; facteur exp(s²/2) = {np.exp(m.scale / 2):.4f}]")
print(f"(c) moyenne observée (Réseaux, 23-27 ans, n = {len(obs)}) : {obs.mean():.2f} € (erreur standard de cette moyenne : {obs.std() / np.sqrt(len(obs)):.2f}) | médiane observée : {obs.median():.2f} €")
# Test décisif : sur TOUS les clients, quelle prédiction reproduit la moyenne observée ?
mediane_pred = np.exp(m.fittedvalues)
print(f"tous les clients (n = {len(df)}) : moyenne observée = {df['panier_moyen'].mean():.2f} | moyenne de exp(mu) = {mediane_pred.mean():.2f} | moyenne de exp(mu) x Duan = {(mediane_pred * duan).mean():.2f}")
```
<!--sortie-->
```text
(a) panier médian prédit      : 43.95 €
(b) panier moyen prédit (Duan) : 47.10 €   [facteur de Duan = 1.0718 ; facteur exp(s²/2) = 1.0710]
(c) moyenne observée (Réseaux, 23-27 ans, n = 86) : 44.49 € (erreur standard de cette moyenne : 1.40) | médiane observée : 42.69 €
tous les clients (n = 1740) : moyenne observée = 61.23 | moyenne de exp(mu) = 57.12 | moyenne de exp(mu) x Duan = 61.22
```

Sur ce petit groupe (86 clients), **la moyenne observée (44,49) tombe plus près de la prédiction médiane (43,95) que de la prédiction corrigée (47,10)** : ce n'est pas une contradiction de la théorie, mais du bruit d'échantillonnage. L'erreur standard de cette moyenne observée est de 1,40 € (écart-type des paniers d'environ 13 €, divisé par $\sqrt{86}$) : la prédiction corrigée (47,10) est à 1,9 erreur standard de la moyenne observée, la prédiction médiane à 0,4 : sur un groupe aussi petit, ces deux écarts sont tous deux plausibles par hasard. Pour **départager** vraiment, il faut un grand échantillon : sur les 1 740 clients, la moyenne observée est de 61,23 € ; la moyenne des prédictions $e^{\hat\mu}$ (la médiane de chacun) n'en donne que 57,12 €, soit un défaut de 7 %, alors que les prédictions corrigées $e^{\hat\mu}\times$Duan redonnent 61,22 €. C'est la confirmation de la théorie du 1.1.8 : la rétro-transformation **naïve vise la médiane, pas la moyenne**, et sous-estime systématiquement le panier moyen ; la correction de Duan la rétablit. (En attendant, retenez qu'une comparaison sur 86 observations ne départage pas des écarts de 7 %.)

### Corrigé 1.10

```python
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"])
v["t"] = np.arange(len(v))
v["m"] = v["mois"].dt.month
mv = smf.ols("np.log(ca) ~ t + C(m) + promo + covid", data=v).fit()
ic = mv.conf_int()
print(f"(a) croissance annuelle : exp(12 x {mv.params['t']:.4f}) - 1 = {100 * (np.exp(12 * mv.params['t']) - 1):.1f} % par an   (IC95 % du coefficient mensuel : [{ic.loc['t', 0]:.4f} ; {ic.loc['t', 1]:.4f}])")
print(f"(b) décembre / janvier : x {np.exp(mv.params['C(m)[T.12]']):.2f}")
print(f"(c) confinement : {100 * (np.exp(mv.params['covid']) - 1):.0f} % sur les ventes   (IC95 % : [{100 * (np.exp(ic.loc['covid', 0]) - 1):.0f} % ; {100 * (np.exp(ic.loc['covid', 1]) - 1):.0f} %])")
print(f"    promotion : {100 * (np.exp(mv.params['promo']) - 1):+.1f} %   (IC95 % : [{100 * (np.exp(ic.loc['promo', 0]) - 1):+.1f} % ; {100 * (np.exp(ic.loc['promo', 1]) - 1):+.1f} %])")
r = mv.resid.to_numpy()
print(f"(d) R² = {mv.rsquared:.3f} (contre 0,493 pour la tendance seule) | écart-type résiduel = {np.sqrt(mv.scale):.3f} | Durbin-Watson = {sm.stats.durbin_watson(r):.2f} | autocorrélation d'ordre 1 des résidus = {np.corrcoef(r[1:], r[:-1])[0, 1]:.2f}")
```
<!--sortie-->
```text
(a) croissance annuelle : exp(12 x 0.0072) - 1 = 9.0 % par an   (IC95 % du coefficient mensuel : [0.0068 ; 0.0076])
(b) décembre / janvier : x 2.57
(c) confinement : -42 % sur les ventes   (IC95 % : [-46 % ; -37 %])
    promotion : +5.9 %   (IC95 % : [+1.3 % ; +10.7 %])
(d) R² = 0.964 (contre 0,493 pour la tendance seule) | écart-type résiduel = 0.078 | Durbin-Watson = 0.93 | autocorrélation d'ordre 1 des résidus = 0.54
```

(a) Les ventes croissent d'environ **9 % par an** (0,72 % par mois). (b) Décembre est environ **2,6 fois** plus fort que janvier, à tendance égale (la saisonnalité est massive). (c) Le confinement de 2020 correspond à une baisse d'environ **42 %** des ventes sur les quatre mois concernés (intervalle large, de −46 % à −37 %). L'effet des promotions est estimé à environ +6 %, avec un intervalle de confiance **large** (de +1 % à +11 %) : un mois de promotion est un événement rare (une quinzaine de mois sur 120) et la dépendance entre mois rend l'intervalle encore plus incertain. (d) Le $R^2$ monte à **0,96** : tendance, saisonnalité et chocs expliquent presque tout. Mais le **Durbin-Watson est de 0,93** : l'autocorrélation d'ordre 1 des résidus est **0,54**. Il reste donc de la structure : les erreurs successives se ressemblent, de sorte que les p-valeurs et intervalles ci-dessus sont **trop optimistes** (1.3.3). C'est exactement le sujet du chapitre 4 : modéliser cette dépendance (modèles ARIMA, section 4.2). *(Une dernière remarque : les données ayant été simulées, nous pouvons vérifier que les valeurs estimées retrouvent la vérité : croissance de 0,75 % par mois, facteur saisonnier décembre/janvier de $1{,}55/0{,}62\approx2{,}5$, effet du confinement de $-0{,}55$ en log (soit $-42\,\%$), effet des promotions de $+0{,}10$ en log (soit $+10{,}5\,\%$ : dans l'intervalle, mais près de sa borne haute), autocorrélation des erreurs de 0,5.)*

### Corrigé 1.11

(a) Avec $\mathbf X^\top\mathbf X=\mathbf I$, la formule de Ridge $(\mathbf X^\top\mathbf X+\lambda\mathbf I)^{-1}\mathbf X^\top\mathbf y$ devient $\frac1{1+\lambda}\mathbf X^\top\mathbf y=\frac1{1+\lambda}\hat{\boldsymbol\beta}^{\text{MCO}}$. (b) Pour $\beta=2,\sigma=1$ : $\text{EQM}(0)=1$ ; $\text{EQM}(0{,}25)=\dfrac{0{,}0625\times4+1}{1{,}5625}=\dfrac{1{,}25}{1{,}5625}=0{,}8$ ; $\text{EQM}(1)=\dfrac{4+1}{4}=1{,}25$. (c) La dérivée s'annule en $\lambda^\star=\sigma^2/\beta^2=0{,}25$ ; à ce point l'EQM vaut 0,8 (une baisse de 20 % par rapport aux moindres carrés), et elle redevient supérieure à 1 pour $\lambda>0{,}5$ ($\lambda=1$ donne 1,25).

```python
beta_v, sigma_v = 2.0, 1.0
eqm = lambda lam: (lam**2 * beta_v**2 + sigma_v**2) / (1 + lam)**2
for lam in [0, 0.25, 0.5, 1]:
    print(f"lambda = {lam:4.2f} : EQM = {eqm(lam):.4f}")
grille = np.linspace(0, 3, 30001)
print("lambda optimal sur la grille :", round(grille[np.argmin(eqm(grille))], 4), "| sigma²/beta² =", sigma_v**2 / beta_v**2)
rng = np.random.default_rng(1)
est = beta_v + rng.normal(0, sigma_v, 200000)                      # estimations MCO simulées
print("EQM simulée : MCO =", round(np.mean((est - beta_v)**2), 3), "| Ridge (lambda = 0,25) =", round(np.mean((est / 1.25 - beta_v)**2), 3))
```
<!--sortie-->
```text
lambda = 0.00 : EQM = 1.0000
lambda = 0.25 : EQM = 0.8000
lambda = 0.50 : EQM = 0.8889
lambda = 1.00 : EQM = 1.2500
lambda optimal sur la grille : 0.25 | sigma²/beta² = 0.25
EQM simulée : MCO = 0.998 | Ridge (lambda = 0,25) = 0.8
```

### Corrigé 1.12

(a) $\text{ICC}=\dfrac{2}{2+6}=0{,}25$. (b) $B_j=\dfrac{\tau^2}{\tau^2+\sigma^2/n_j}=\dfrac{2}{2+6/9}=\dfrac{2}{2{,}667}=0{,}75$ ; $\hat u_j=0{,}75\times3{,}2=2{,}4$ : on retient 75 % de l'écart observé. (c) Avec $n_j=2$ : $B_j=\dfrac{2}{2+3}=0{,}4$ et $\hat u_j=0{,}4\times3{,}2=1{,}28$ : un petit relais est rétréci bien davantage (60 % de l'écart est écarté, contre 25 % pour le grand). (d) Effet de plan $1+(m-1)\rho=1+8\times0{,}25=3$ ; $n=20\times9=180$ commandes valent $180/3=60$ observations indépendantes.

```python
tau2, sigma2 = 2.0, 6.0
print("ICC =", tau2 / (tau2 + sigma2))
for n_j in [9, 2]:
    B = tau2 / (tau2 + sigma2 / n_j)
    print(f"n_j = {n_j}: B = {B:.3f} | BLUP = {B * 3.2:.3f}")
deff = 1 + (9 - 1) * tau2 / (tau2 + sigma2)
print("effet de plan =", deff, "| effectif effectif =", 180 / deff)
```
<!--sortie-->
```text
ICC = 0.25
n_j = 9: B = 0.750 | BLUP = 2.400
n_j = 2: B = 0.400 | BLUP = 1.280
effet de plan = 3.0 | effectif effectif = 60.0
```

### Corrigé 1.13

```python
rng = np.random.default_rng(5)
n = 100
x = rng.uniform(0, 10, n)
y_propre = 2 + 1.5 * x + rng.normal(0, 1, n)
y_corr = y_propre.copy()
idx = rng.choice(n, 5, replace=False)
y_corr[idx] += 25
X = sm.add_constant(x)
lignes = {}
for nom, y in [("données propres", y_propre), ("données corrompues", y_corr)]:
    lignes[(nom, "MCO")] = sm.OLS(y, X).fit().params
    lignes[(nom, "Huber")] = sm.RLM(y, X, M=sm.robust.norms.HuberT()).fit().params
    lignes[(nom, "médiane")] = sm.QuantReg(y, X).fit(q=0.5).params
tab = pd.DataFrame(lignes, index=["constante", "pente"]).T
print("vrais coefficients : constante = 2, pente = 1,5")
print(tab.round(3).to_string())
```
<!--sortie-->
```text
vrais coefficients : constante = 2, pente = 1,5
                            constante  pente
données propres    MCO          2.356  1.450
                   Huber        2.375  1.441
                   médiane      2.297  1.436
données corrompues MCO          2.633  1.637
                   Huber        2.424  1.451
                   médiane      2.297  1.450
```

Sur les données **propres**, les trois méthodes donnent des résultats très proches. Après corruption de 5 % des points, les **moindres carrés dérivent** (la pente passe de 1,45 à 1,64 et la constante de 2,36 à 2,63), alors que **Huber et la régression médiane** restent presque inchangés (pente entre 1,44 et 1,45 dans les deux cas). C'est l'intuition du 1.6 : l'influence des points aberrants est plafonnée par les méthodes robustes.

