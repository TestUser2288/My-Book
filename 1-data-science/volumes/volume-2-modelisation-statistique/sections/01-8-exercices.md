## 1.8 Exercices corrigés

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 1 à 8 et 11 à 12 se résolvent surtout à la main ; les exercices 9, 10 et 13 demandent le code.

### Énoncés

**Exercice 1 ⭐ (moindres carrés à la main).** Trois commandes ont $x$ articles et un montant $y$ en € : $(1,\,2),\ (2,\,3),\ (4,\,7)$. (a) Écrivez $\mathbf X$ et $\mathbf y$, calculez $\mathbf X^\top\mathbf X$ et $\mathbf X^\top\mathbf y$, puis $\hat{\boldsymbol\beta}=(\hat\beta_0,\hat\beta_1)$. (b) Calculez les valeurs ajustées et les résidus, et vérifiez que $\mathbf X^\top\hat{\boldsymbol\varepsilon}=\mathbf 0$. (c) Calculez le $R^2$. (d) Quel montant prévoit-on pour 3 articles ?

**Exercice 2 ⭐ (lire un modèle en log).** Le modèle `log_panier ~ a + C(canal)` du 1.1.7 donne : constante $4{,}2206$, Site $-0{,}1571$, Réseaux $-0{,}3368$, âge centré $0{,}0092$ par année. (a) Exprimez **exactement** (en pourcentage) l'effet du Site et d'Réseaux par rapport à la boutique. (b) Quel effet pour 10 années d'âge de plus ? (c) Quel est le panier **médian** prédit d'une cliente de 46 ans acquise par le Site ? (d) Pourquoi dit-on « médian » et non « moyen » ?

**Exercice 3 ⭐⭐ (régression simple).** Dans la régression simple $y=\beta_0+\beta_1x+\varepsilon$, démontrez que $\hat\beta_1=r\,\dfrac{s_y}{s_x}$ et que $R^2=r^2$, où $r$ est le coefficient de corrélation de Pearson entre $x$ et $y$. Vérifiez-le sur les quatre commandes du 1.1.1 ($x=1,2,3,4$ ; $y=22,41,66,79$).

**Exercice 4 ⭐⭐ (test et intervalle à la main).** Pour Réseaux, `statsmodels` donne le coefficient $-0{,}3368$ et son erreur standard $0{,}0225$, avec $n-p=1736$ degrés de liberté (quantile de Student à 97,5 % : $1{,}961$). (a) Calculez la statistique $t$ et dites si l'on rejette $H_0:\beta=0$ à 5 %. (b) Donnez l'intervalle de confiance à 95 % de $\beta$, puis de l'effet multiplicatif $e^\beta$ exprimé en pourcentage. (c) Pour l'âge : coefficient $0{,}0092$, erreur standard $0{,}00085$ : quelle est la statistique $t$ ?

**Exercice 5 ⭐⭐ (test $F$).** Le modèle réduit `log_panier ~ a` a une somme des carrés résiduelle $\text{SCR}_0=269{,}94$ ; le modèle complet `log_panier ~ a + C(canal)` a $\text{SCR}_1=238{,}30$, avec $n-p_1=1736$. (a) Calculez la statistique $F$ du test « le canal est inutile ». Combien y a-t-il de contraintes $q$ ? (b) La valeur critique de $F_{2,\,1736}$ à 5 % est environ 3,0 : concluez. (c) Si $\text{SCR}_1$ valait 269,70 au lieu de 238,30 (le canal améliorait à peine l'ajustement), que vaudrait $F$ ? Que concluriez-vous ?

**Exercice 6 ⭐⭐ (levier).** Quatre clients ont pour âge centré $x=(1,\,2,\,3,\,10)$. (a) Calculez le levier $h_{ii}=\frac1n+\frac{(x_i-\bar x)^2}{\sum_k(x_k-\bar x)^2}$ de chacun. Vérifiez que leur somme vaut $p=2$. (b) Quel client a le plus d'influence potentielle ? (c) Si $y_4$ augmente de 1, de combien augmente la valeur ajustée $\hat y_4$ ?

**Exercice 7 ⭐⭐ (PRESS).** Reprenez les trois points de l'exercice 1. (a) Calculez les leviers $h_{ii}$. (b) Calculez les erreurs de prédiction « sans le point » $\hat\varepsilon_i/(1-h_{ii})$ et la somme PRESS. (c) Vérifiez l'une d'elles en réajustant la droite sur les deux autres points. (d) Comparez PRESS à la somme des carrés résiduelle : que constatez-vous ?

**Exercice 8 ⭐⭐ (multicolinéarité).** (a) Une variable explicative $x_j$ est expliquée à 99,5 % par les autres ($R_j^2=0{,}995$) : donnez son VIF et le facteur par lequel son erreur standard est multipliée. (b) Avec deux variables explicatives de corrélation 0,9, que vaut leur VIF ? (c) **Code.** Les huit questions de l'enquête de satisfaction (`q1` à `q8`) sont-elles gravement colinéaires entre elles ? Calculez leurs VIF.

**Exercice 9 ⭐⭐ (prédire une moyenne en euros).** Avec le modèle `log_panier ~ a + C(canal)` : (a) donnez, pour un client **Réseaux de 25 ans**, le panier médian prédit ; (b) calculez une prédiction du panier **moyen** avec la correction de Duan ; (c) comparez à la moyenne observée des clients Réseaux âgés de 23 à 27 ans. Laquelle des deux prédictions est la plus proche, et pourquoi ?

**Exercice 10 ⭐⭐⭐ (régression sur les ventes mensuelles).** Avec `donnees/ventes_mensuelles.csv` (120 mois), ajustez `log(ca) ~ t + C(mois) + promo + covid`, où `t` est le numéro du mois (0 à 119), `mois` le mois civil (1 à 12), `promo` indique un mois de promotion et `covid` les mois de mars à juin 2020. (a) Quelle est la croissance annuelle estimée ? (b) Quel est l'effet estimé de décembre par rapport à janvier (en facteur multiplicatif) ? (c) Quel est l'effet du confinement de 2020 sur les ventes, en pourcentage ? (d) Que disent le $R^2$ et le test de Durbin-Watson sur ce modèle ? Reste-t-il de la structure dans les résidus ?

**Exercice 11 ⭐⭐⭐ (Ridge, cas orthonormal).** Les colonnes de $\mathbf X$ sont orthonormales ($\mathbf X^\top\mathbf X=\mathbf I$). (a) Montrez que $\hat\beta_j^{\text{ridge}}=\hat\beta_j^{\text{MCO}}/(1+\lambda)$. (b) Pour un coefficient vrai $\beta=2$ et $\sigma=1$, calculez l'erreur quadratique moyenne $\text{EQM}(\lambda)=\dfrac{\lambda^2\beta^2+\sigma^2}{(1+\lambda)^2}$ pour $\lambda=0$, $0{,}25$ et $1$. (c) Quel $\lambda$ la minimise ? Vérifiez par le code sur une grille.

**Exercice 12 ⭐⭐ (modèle mixte, calcul à la main).** Dans un modèle à intercept aléatoire, $\tau^2=2{,}0$ (variance entre groupes) et $\sigma^2=6{,}0$ (variance résiduelle). (a) Calculez l'ICC. (b) Un relais a $n_j=9$ commandes et une moyenne de résidus « fixes » $\bar r_j=3{,}2$ : calculez le facteur de rétrécissement $B_j$ et le BLUP $\hat u_j$. (c) Même question pour un relais de $n_j=2$ commandes avec la même moyenne de résidus. (d) Avec $J=20$ relais de 9 commandes chacun, quel est l'effectif effectif pour estimer une variable qui ne varie qu'entre relais ?

**Exercice 13 ⭐⭐ (robustesse, simulation).** Simulez $n=100$ points $y=2+1{,}5x+\varepsilon$ ($x$ uniforme sur $[0,10]$, $\varepsilon\sim\mathcal N(0,1)$, graine 5), puis ajoutez 25 à $y$ pour 5 points tirés au hasard. Comparez les coefficients des moindres carrés, de Huber et de la régression médiane sur les données propres et corrompues. Que constatez-vous ?

### Corrigés

**Corrigé 1.** (a) $\mathbf X=\begin{pmatrix}1&1\\1&2\\1&4\end{pmatrix}$, $\mathbf y=(2,3,7)^\top$. $\mathbf X^\top\mathbf X=\begin{pmatrix}3&7\\7&21\end{pmatrix}$ (déterminant $63-49=14$), $\mathbf X^\top\mathbf y=(12,\ 2+6+28)^\top=(12,\,36)^\top$. Donc $\hat{\boldsymbol\beta}=\frac1{14}\begin{pmatrix}21&-7\\-7&3\end{pmatrix}\begin{pmatrix}12\\36\end{pmatrix}=\frac1{14}\begin{pmatrix}252-252\\-84+108\end{pmatrix}=\begin{pmatrix}0\\12/7\end{pmatrix}$ : la droite passe **exactement par l'origine** : $\hat y=\frac{12}7x\approx1{,}714\,x$. (b) Ajustées : $\frac{12}7,\ \frac{24}7,\ \frac{48}7$ ; résidus : $\frac27,\ -\frac37,\ \frac17$ (soit $0{,}286;\ -0{,}429;\ 0{,}143$). Somme : $0$ ✓. $\sum x_i\hat\varepsilon_i=\frac27-\frac67+\frac47=0$ ✓. (c) $\text{SCR}=\frac{4+9+1}{49}=\frac27$ ; $\bar y=4$, $\text{SCT}=4+1+9=14$ ; $R^2=1-\frac{2/7}{14}=\frac{48}{49}\approx0{,}980$. (d) $\hat y(3)=\frac{36}7\approx5{,}14$ €.

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

**Corrigé 2.** (a) Site : $e^{-0{,}1571}-1=-14{,}5\,\%$ ; Réseaux : $e^{-0{,}3368}-1=-28{,}6\,\%$ (et non −15,7 % et −33,7 % : l'approximation $100\beta$ est mauvaise pour de grands coefficients, 1.1.8). (b) $e^{10\times0{,}0092}-1=+9{,}6\,\%$. (c) Pour 46 ans, $a=10$ : $\hat\mu=4{,}2206-0{,}1571+10\times0{,}0092=4{,}1555$, donc $e^{4{,}1555}\approx63{,}8$ €. (d) Parce que $e^{\hat\mu}$ est la prédiction de la **médiane** de $y$ : pour la moyenne il faudrait la correction $e^{s^2/2}$ ou celle de Duan (1.1.8, et exercice 9).

```python
for nom, b in [("Site", -0.1571), ("Réseaux", -0.3368)]:
    print(f"{nom:10s}: {100 * (np.exp(b) - 1):+.1f} %")
print(f"10 ans d'âge : {100 * (np.exp(10 * 0.0092) - 1):+.1f} %")
print(f"panier médian prédit, 46 ans, Site : {np.exp(4.2206 - 0.1571 + 10 * 0.0092):.1f} €")
```
<!--sortie-->
```text
Site      : -14.5 %
Réseaux : -28.6 %
10 ans d'âge : +9.6 %
panier médian prédit, 46 ans, Site : 63.8 €
```

**Corrigé 3.** On sait (1.1.1, équations normales) que $\hat\beta_1=\dfrac{S_{xy}}{S_{xx}}$ avec $S_{xy}=\sum(x_i-\bar x)(y_i-\bar y)$ et $S_{xx}=\sum(x_i-\bar x)^2$. Or $r=\dfrac{S_{xy}}{\sqrt{S_{xx}S_{yy}}}$ et $\dfrac{s_y}{s_x}=\sqrt{S_{yy}/S_{xx}}$, donc $r\dfrac{s_y}{s_x}=\dfrac{S_{xy}}{\sqrt{S_{xx}S_{yy}}}\sqrt{\dfrac{S_{yy}}{S_{xx}}}=\dfrac{S_{xy}}{S_{xx}}=\hat\beta_1$. Pour le $R^2$ : $\hat y_i-\bar y=\hat\beta_1(x_i-\bar x)$, donc $\text{SCE}=\hat\beta_1^2S_{xx}=\dfrac{S_{xy}^2}{S_{xx}}$ et $R^2=\dfrac{\text{SCE}}{\text{SCT}}=\dfrac{S_{xy}^2}{S_{xx}S_{yy}}=r^2$. $\square$

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

**Corrigé 4.** (a) $t=-0{,}3368/0{,}0225=-14{,}97$ ; $|t|\gg1{,}961$ : on rejette $H_0$ (p-valeur de l'ordre de $10^{-48}$). (b) $-0{,}3368\pm1{,}961\times0{,}0225=[-0{,}381\,;\,-0{,}293]$ ; en pourcentage : $e^{-0{,}381}-1=-31{,}7\,\%$ et $e^{-0{,}293}-1=-25{,}4\,\%$ : un effet de **−25 % à −32 %**. (c) $t=0{,}0092/0{,}00085\approx10{,}8$.

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

**Corrigé 5.** (a) $q=2$ (les deux coefficients du canal). $F=\dfrac{(269{,}94-238{,}30)/2}{238{,}30/1736}=\dfrac{15{,}82}{0{,}1373}\approx115{,}3$. (b) $115\gg3{,}0$ : on rejette l'hypothèse « le canal est inutile » (p-valeur de l'ordre de $10^{-47}$). (c) $F=\dfrac{(269{,}94-269{,}70)/2}{269{,}70/1736}=\dfrac{0{,}12}{0{,}1554}\approx0{,}77$, inférieur à 3,0 (et même à 1) : le canal n'apporte pas plus que du bruit, on ne rejette pas $H_0$.

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

**Corrigé 6.** (a) $\bar x=4$, $\sum(x_k-\bar x)^2=9+4+1+36=50$. $h_{11}=\frac14+\frac9{50}=0{,}43$ ; $h_{22}=\frac14+\frac4{50}=0{,}33$ ; $h_{33}=\frac14+\frac1{50}=0{,}27$ ; $h_{44}=\frac14+\frac{36}{50}=0{,}97$. Somme : $2{,}00=p$ ✓. (b) Le client d'âge 10, éloigné des autres : levier de 0,97 (presque 1). (c) $\partial\hat y_4/\partial y_4=h_{44}=0{,}97$ : la droite est presque **forcée** de passer par ce point ; $\hat y_4$ augmente de 0,97.

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

**Corrigé 7.** (a) $\bar x=7/3$, $S_{xx}=\frac{16}9+\frac19+\frac{25}9=\frac{42}9=\frac{14}3$ : $h_{11}=\frac13+\frac{16/9}{14/3}=\frac5{7}\approx0{,}714$ ; $h_{22}=\frac13+\frac{1/9}{14/3}=\frac5{14}\approx0{,}357$ ; $h_{33}=\frac13+\frac{25/9}{14/3}=\frac{13}{14}\approx0{,}929$ (somme $=2$ ✓). (b) Erreurs sans le point : $\frac{2/7}{2/7}=1$ ; $\frac{-3/7}{9/14}=-\frac23$ ; $\frac{1/7}{1/14}=2$. $\text{PRESS}=1+\frac49+4=\frac{49}9\approx5{,}44$. (c) Sans le point $(1,2)$ : la droite passe par $(2,3)$ et $(4,7)$, d'équation $y=2x-1$, et prévoit $1$ en $x=1$ : l'erreur est $2-1=1$ ✓. (d) PRESS ($5{,}44$) est près de **vingt fois** plus grand que la somme des carrés résiduelle ($2/7\approx0{,}286$) : avec 3 points seulement, l'ajustement « d'apprentissage » est trompeusement optimiste, surtout pour le point $x=4$ à fort levier (0,93), dont l'erreur sans lui est de 2 contre un résidu de 0,14.

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

**Corrigé 8.** (a) $\text{VIF}=\frac1{1-0{,}995}=200$ ; l'erreur standard est multipliée par $\sqrt{200}\approx14$. (b) Avec deux variables, $R_j^2=r^2=0{,}81$, donc $\text{VIF}=\frac1{0{,}19}\approx5{,}3$ : à surveiller (règle empirique : > 5). (c) Voir le code ci-dessous.

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

**Corrigé 9.** (a) Panier médian prédit : $e^{\hat\mu}$ avec $\hat\mu$ la prédiction du modèle. (b) La prédiction de la moyenne s'obtient en multipliant par le facteur de Duan $\frac1n\sum_ie^{\hat\varepsilon_i}$. (c) On compare à la moyenne observée.

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

**Corrigé 10.**

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

**Corrigé 11.** (a) Avec $\mathbf X^\top\mathbf X=\mathbf I$, la formule de Ridge $(\mathbf X^\top\mathbf X+\lambda\mathbf I)^{-1}\mathbf X^\top\mathbf y$ devient $\frac1{1+\lambda}\mathbf X^\top\mathbf y=\frac1{1+\lambda}\hat{\boldsymbol\beta}^{\text{MCO}}$. (b) Pour $\beta=2,\sigma=1$ : $\text{EQM}(0)=1$ ; $\text{EQM}(0{,}25)=\dfrac{0{,}0625\times4+1}{1{,}5625}=\dfrac{1{,}25}{1{,}5625}=0{,}8$ ; $\text{EQM}(1)=\dfrac{4+1}{4}=1{,}25$. (c) La dérivée s'annule en $\lambda^\star=\sigma^2/\beta^2=0{,}25$ ; à ce point l'EQM vaut 0,8 (une baisse de 20 % par rapport aux moindres carrés), et elle redevient supérieure à 1 pour $\lambda>0{,}5$ ($\lambda=1$ donne 1,25).

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

**Corrigé 12.** (a) $\text{ICC}=\dfrac{2}{2+6}=0{,}25$. (b) $B_j=\dfrac{\tau^2}{\tau^2+\sigma^2/n_j}=\dfrac{2}{2+6/9}=\dfrac{2}{2{,}667}=0{,}75$ ; $\hat u_j=0{,}75\times3{,}2=2{,}4$ : on retient 75 % de l'écart observé. (c) Avec $n_j=2$ : $B_j=\dfrac{2}{2+3}=0{,}4$ et $\hat u_j=0{,}4\times3{,}2=1{,}28$ : un petit relais est rétréci bien davantage (60 % de l'écart est écarté, contre 25 % pour le grand). (d) Effet de plan $1+(m-1)\rho=1+8\times0{,}25=3$ ; $n=20\times9=180$ commandes valent $180/3=60$ observations indépendantes.

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

**Corrigé 13.**

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

---

## Bilan du chapitre 1

Vous savez maintenant :

- **écrire et résoudre** un modèle linéaire $\mathbf y=\mathbf X\boldsymbol\beta+\boldsymbol\varepsilon$ par les équations normales, comprendre pourquoi la solution est une **projection orthogonale** et démontrer le théorème de **Gauss-Markov** ;
- **interpréter** les coefficients (variables qualitatives par indicatrices, « toutes choses égales par ailleurs », modèles en logarithmes, rétro-transformation pour prédire une moyenne) ;
- **faire de l'inférence** : erreurs standard, tests $t$ et $F$ de modèles emboîtés, intervalles de confiance et de **prédiction**, bootstrap des couples, en sachant sous quelles hypothèses ils sont valables ;
- **poser un diagnostic** : graphiques de résidus, tests de Breusch-Pagan et de Durbin-Watson, **levier** et **distance de Cook**, **VIF**, erreurs standard robustes, et savoir remédier aux défauts (transformer, centrer, changer de modèle) ;
- **choisir un modèle** sans tricher : AIC, BIC, validation croisée (PRESS), tests emboîtés, et se méfier de la sélection automatique ;
- (en option) **régulariser** (Ridge, Lasso, Elastic Net) quand les variables sont nombreuses, **résister** aux aberrations (Huber, régression quantile) et **modéliser des données groupées** (effets mixtes, rétrécissement).

Le chapitre 2 généralise la régression à des réponses qui ne sont **ni continues ni normales** : un client rachète-t-il (oui/non) ? combien de commandes passe-t-il (un entier) ? C'est le cadre des **modèles linéaires généralisés**, dont la régression linéaire de ce chapitre est le cas particulier le plus simple.
