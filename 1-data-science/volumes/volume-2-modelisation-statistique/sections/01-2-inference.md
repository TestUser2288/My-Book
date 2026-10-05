## 1.2 Inférence sur les coefficients

> 💡 **Intuition.** Les coefficients de `m2` (−0,34 pour Instagram, +0,009 par année d'âge…) sont calculés sur **un** échantillon de 1 740 clients. Avec un autre échantillon, on aurait obtenu d'autres valeurs. La question de l'inférence est : *de combien ces chiffres peuvent-ils bouger ?* et donc *que peut-on affirmer sur la vraie valeur ?* C'est exactement l'esprit du chapitre 3 du volume I (intervalles de confiance, tests), appliqué maintenant à chaque coefficient d'un modèle.

On part des mêmes données qu'en 1.1. Voici la préparation (identique), que nous ne détaillerons plus :

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, ENCRE, GRIS = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#898781"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Instagram"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])

m1 = smf.ols("log_panier ~ a", data=df).fit()
m2 = smf.ols("log_panier ~ a + C(canal)", data=df).fit()
m3 = smf.ols("log_panier ~ a * C(canal)", data=df).fit()
print(len(df), "clients | n - p pour m2 =", int(m2.df_resid))
```
<!--sortie-->
```text
1740 clients | n - p pour m2 = 1736
```

### 1.2.1 La loi des estimateurs sous l'hypothèse de normalité

Au 1.1.5, nous avons établi l'espérance et la variance de $\hat{\boldsymbol\beta}$. Pour fabriquer des tests et des intervalles exacts, il faut sa **loi** entière : c'est le rôle de l'hypothèse H5 (erreurs normales).

> 📐 **Théorème 3.** Sous H1 à H5 :
> 1. $\hat{\boldsymbol\beta}\sim\mathcal N\big(\boldsymbol\beta,\ \sigma^2(\mathbf X^\top\mathbf X)^{-1}\big)$ ;
> 2. $\dfrac{(n-p)\,s^2}{\sigma^2}=\dfrac{\text{SCR}}{\sigma^2}\sim\chi^2_{n-p}$ ;
> 3. $\hat{\boldsymbol\beta}$ et $s^2$ sont **indépendants**.
>
> *Démonstration.* (1) On a vu que $\hat{\boldsymbol\beta}=\boldsymbol\beta+\mathbf A\boldsymbol\varepsilon$ avec $\mathbf A=(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top$ : c'est une transformation linéaire d'un vecteur gaussien, donc un vecteur gaussien, d'espérance $\boldsymbol\beta$ et de variance $\sigma^2\mathbf A\mathbf A^\top=\sigma^2(\mathbf X^\top\mathbf X)^{-1}$.
> (3) Le résidu est $\hat{\boldsymbol\varepsilon}=(\mathbf I-\mathbf H)\boldsymbol\varepsilon$. Le couple $(\hat{\boldsymbol\beta},\hat{\boldsymbol\varepsilon})$ est gaussien (transformation linéaire de $\boldsymbol\varepsilon$), et sa covariance croisée vaut $\operatorname{Cov}(\mathbf A\boldsymbol\varepsilon,(\mathbf I-\mathbf H)\boldsymbol\varepsilon)=\sigma^2\mathbf A(\mathbf I-\mathbf H)^\top=\sigma^2(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top(\mathbf I-\mathbf H)=\mathbf 0$, car $\mathbf X^\top(\mathbf I-\mathbf H)=\mathbf 0$ (1.1.4). Pour des vecteurs gaussiens **conjoints**, covariance nulle ⇔ indépendance. Comme $s^2$ ne dépend que de $\hat{\boldsymbol\varepsilon}$, on obtient (3).
> (2) $\text{SCR}/\sigma^2=(\boldsymbol\varepsilon/\sigma)^\top(\mathbf I-\mathbf H)(\boldsymbol\varepsilon/\sigma)$, où $\boldsymbol\varepsilon/\sigma\sim\mathcal N(\mathbf 0,\mathbf I_n)$ et $\mathbf I-\mathbf H$ est un projecteur orthogonal de rang $n-p$. Dans une base orthonormée adaptée au projecteur, c'est la somme de $n-p$ carrés de lois $\mathcal N(0,1)$ indépendantes : une loi $\chi^2_{n-p}$ (théorème de Cochran). $\square$

Pour un coefficient $\beta_j$, la formule (1) donne $\hat\beta_j\sim\mathcal N(\beta_j,\ \sigma^2c_{jj})$ où $c_{jj}$ est le $j$-ième élément diagonal de $(\mathbf X^\top\mathbf X)^{-1}$. Comme $\sigma$ est inconnu, on le remplace par $s$ : l'**erreur standard** de $\hat\beta_j$ est $\operatorname{se}(\hat\beta_j)=s\sqrt{c_{jj}}$. Et le rapport d'une normale à la racine d'un $\chi^2$ indépendant, divisé par ses degrés de liberté, est une loi de Student (volume I, section 3.3.3) :

$$\boxed{\;T_j=\frac{\hat\beta_j-\beta_j}{\operatorname{se}(\hat\beta_j)}\;\sim\;t_{n-p}\;}$$

Reconstruisons à la main le tableau de `statsmodels` pour `m2`, colonne par colonne :

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
print(tab.round(4))
print()
print("identique à statsmodels :", np.allclose(tab["std err"], m2.bse), np.allclose(tab["t"], m2.tvalues),
      np.allclose(tab[["IC bas", "IC haut"]].to_numpy(), m2.conf_int().to_numpy()))
print(f"s = {np.sqrt(s2):.4f} | quantile t(n-p, 97,5 %) = {crit:.4f}  (presque 1,96 : n - p = {n - p} est grand)")
```
<!--sortie-->
```text
                         coef  std err         t  P>|t|  IC bas  IC haut
Intercept              4.2206   0.0175  241.3693    0.0  4.1863   4.2549
C(canal)[T.Site]      -0.1571   0.0231   -6.8065    0.0 -0.2024  -0.1119
C(canal)[T.Instagram] -0.3368   0.0225  -14.9770    0.0 -0.3809  -0.2927
a                      0.0092   0.0008   10.8618    0.0  0.0075   0.0108

identique à statsmodels : True True True
s = 0.3705 | quantile t(n-p, 97,5 %) = 1.9613  (presque 1,96 : n - p = 1736 est grand)
```

Chaque colonne a désormais une origine claire : l'erreur standard vient de $s\sqrt{c_{jj}}$, la statistique $t$ est le rapport coefficient / erreur standard, la p-valeur est la probabilité qu'un Student à $n-p$ degrés de liberté dépasse $|t|$ en valeur absolue, et l'intervalle de confiance est $\hat\beta_j\pm t_{n-p,\,0{,}975}\operatorname{se}(\hat\beta_j)$ (c'est la construction du volume I, section 3.3.3, appliquée à chaque coefficient).

### 1.2.2 Tester un coefficient, lire un intervalle

Le **test de Student** d'un coefficient teste $H_0:\beta_j=0$ contre $H_1:\beta_j\neq0$ : « une fois les autres variables prises en compte, cette variable apporte-t-elle une information ? ». La statistique est $t_j=\hat\beta_j/\operatorname{se}(\hat\beta_j)$, et on rejette $H_0$ au niveau 5 % si $|t_j|>t_{n-p,\,0{,}975}\approx1{,}96$.

Dans le tableau précédent, les trois coefficients du canal et de l'âge ont des $|t|$ très supérieurs à 1,96 (la plus petite valeur, pour l'âge, est de l'ordre de 11) : les p-valeurs sont minuscules : elles s'affichent `0.000` dans le tableau de `statsmodels` (ce qui signifie « inférieur à 0,0005 », et non « exactement nul »), et `0.0` dans notre tableau arrondi à quatre décimales.

> ⚠️ **Rappels du volume I, appliqués ici.** (1) Une p-valeur n'est **pas** la probabilité que $H_0$ soit vraie (3.5.2). (2) « Significatif » n'est pas « important » (3.5.3) : avec 1 740 clients, même un très petit effet serait détecté. Il faut donc toujours lire **l'estimation et son intervalle**, pas seulement le test. (3) Si l'on teste beaucoup de coefficients, il faut se méfier des faux positifs (3.5.5) : nous y reviendrons au 1.4.

L'**intervalle de confiance** est bien plus informatif que la p-valeur. Pour Instagram, l'intervalle sur le log-panier est environ $[-0{,}381\,;-0{,}293]$ ; en passant à l'exponentielle (une fonction croissante conserve les bornes), on obtient une **fourchette sur l'effet multiplicatif** :

```python
ic = m2.conf_int()
for nom in ["C(canal)[T.Site]", "C(canal)[T.Instagram]"]:
    bas, haut = ic.loc[nom]
    print(f"{nom:24s} effet sur le panier : {100*(np.exp(m2.params[nom])-1):+.1f} %   IC95 % : [{100*(np.exp(bas)-1):+.1f} % ; {100*(np.exp(haut)-1):+.1f} %]")
bas, haut = ic.loc["a"]
print(f"{'a (10 ans de plus)':24s} effet sur le panier : {100*(np.exp(10*m2.params['a'])-1):+.1f} %   IC95 % : [{100*(np.exp(10*bas)-1):+.1f} % ; {100*(np.exp(10*haut)-1):+.1f} %]")
```
<!--sortie-->
```text
C(canal)[T.Site]         effet sur le panier : -14.5 %   IC95 % : [-18.3 % ; -10.6 %]
C(canal)[T.Instagram]    effet sur le panier : -28.6 %   IC95 % : [-31.7 % ; -25.4 %]
a (10 ans de plus)       effet sur le panier : +9.6 %   IC95 % : [+7.8 % ; +11.4 %]
```

La phrase honnête à transmettre à Yasmine est donc : « *à âge égal, un client acquis par Instagram dépense environ 29 % de moins qu'un client de la boutique ; avec 95 % de confiance, la vraie différence se situe entre 25 % et 32 % de moins* ». Et pour l'âge : « *dix ans de plus sont associés à un panier de 8 à 11 % plus élevé* ».

**Un test peut aussi porter sur une combinaison de coefficients.** Par exemple : « le Site et Instagram ont-ils le même panier (à âge égal) ? ». L'hypothèse est $H_0:\beta_{\text{Site}}-\beta_{\text{Instagram}}=0$, c'est-à-dire $H_0:\mathbf c^\top\boldsymbol\beta=0$ avec $\mathbf c=(0,1,-1,0)^\top$. La variance de $\mathbf c^\top\hat{\boldsymbol\beta}$ est $\sigma^2\mathbf c^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf c$ : les covariances entre coefficients **comptent** (on ne peut pas se contenter de lire les deux erreurs standard du tableau).

```python
c = np.array([0, 1, -1, 0])
diff = c @ beta
se_diff = np.sqrt(s2 * c @ XtX_inv @ c)
print(f"beta_Site - beta_Instagram = {diff:.4f} | erreur standard = {se_diff:.4f} | t = {diff/se_diff:.2f} | p = {2*stats.t.sf(abs(diff/se_diff), n-p):.2e}")
print(m2.t_test("C(canal)[T.Site] - C(canal)[T.Instagram] = 0"))
```
<!--sortie-->
```text
beta_Site - beta_Instagram = 0.1796 | erreur standard = 0.0207 | t = 8.69 | p = 8.16e-18
                             Test for Constraints                             
==============================================================================
                 coef    std err          t      P>|t|      [0.025      0.975]
------------------------------------------------------------------------------
c0             0.1796      0.021      8.691      0.000       0.139       0.220
==============================================================================
```

### 1.2.3 Le test $F$ : tester plusieurs coefficients à la fois

Comment tester que le **canal** compte, quand il se traduit par *deux* coefficients (`Site` et `Instagram`) ? Faire deux tests $t$ séparés ne répond pas à la question (et multiplie les risques de faux positif). On utilise un **test $F$ de modèles emboîtés** : on compare le modèle complet $M_1$ (avec $p_1$ paramètres) au modèle réduit $M_0$ (avec $p_0<p_1$ paramètres, obtenu en imposant $q=p_1-p_0$ contraintes, par exemple « les deux coefficients du canal sont nuls »).

> 📐 **Statistique de Fisher.** En notant $\text{SCR}_0$ et $\text{SCR}_1$ les sommes de carrés résiduelles des deux modèles (le modèle réduit ajuste toujours moins bien : $\text{SCR}_0\ge\text{SCR}_1$),
> $$F=\frac{(\text{SCR}_0-\text{SCR}_1)/q}{\text{SCR}_1/(n-p_1)}\ \sim\ F_{q,\;n-p_1}\quad\text{sous }H_0 .$$
> *Pourquoi cette loi ?* Notons $\mathbf H_0$ et $\mathbf H_1$ les matrices chapeau des deux modèles (l'image de $\mathbf H_0$ est contenue dans celle de $\mathbf H_1$). Sous $H_0$, la vraie moyenne $\mathbf X\boldsymbol\beta$ appartient au petit sous-espace, donc $\text{SCR}_0-\text{SCR}_1=\boldsymbol\varepsilon^\top(\mathbf H_1-\mathbf H_0)\boldsymbol\varepsilon$ et $\text{SCR}_1=\boldsymbol\varepsilon^\top(\mathbf I-\mathbf H_1)\boldsymbol\varepsilon$. Les matrices $\mathbf H_1-\mathbf H_0$ et $\mathbf I-\mathbf H_1$ sont des projecteurs orthogonaux entre eux, de rangs $q$ et $n-p_1$ : par le théorème de Cochran, ce sont deux variables **indépendantes** de lois $\sigma^2\chi^2_q$ et $\sigma^2\chi^2_{n-p_1}$. Leur rapport, une fois divisé par les degrés de liberté, est par définition une loi de Fisher. $\square$
>
> L'intuition est limpide : le numérateur mesure **combien l'ajustement se dégrade** (par contrainte) quand on retire les variables ; le dénominateur est l'échelle de bruit du modèle complet. Si retirer les variables ne dégrade pas plus que du bruit, $F$ est proche de 1.

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

La statistique $F$ calculée à la main coïncide avec celle de `anova_lm`. Le canal est donc **très significatif** dans son ensemble.

Le même outil teste d'autres questions :

- **Le test global** du tableau de résultats (`F-statistic` dans `summary()`) compare le modèle complet au modèle réduit à la **seule constante** : « au moins une variable explicative est-elle utile ? ».
- **L'interaction âge × canal** (1.1.9) : `m3` contre `m2`, avec $q=2$ contraintes (« les deux différences de pente sont nulles »).
- **Un cas particulier** : quand $q=1$, $F=t^2$ (le test $F$ d'un seul coefficient est le carré du test $t$).

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

Pour l'interaction, la p-valeur est grande : rien n'indique que l'effet de l'âge diffère selon le canal. Le modèle plus simple `m2` suffit.

> 🧪 **Que se passe-t-il si les erreurs ne sont pas normales ?** Pour un grand échantillon, le théorème central limite (volume I, section 2.4.3) assure que $\hat{\boldsymbol\beta}$ est approximativement normal même si les erreurs ne le sont pas, de sorte que les tests $t$ et $F$ restent *approximativement* valides (avec les lois asymptotiques). Pour un petit échantillon avec des erreurs très asymétriques, il vaut mieux recourir au **bootstrap** (voir plus bas).

### 1.2.4 Intervalle de confiance et intervalle de prédiction

Deux questions très différentes se cachent derrière « prédire » :

1. **Quel est le panier moyen** des clients Instagram de 25 ans ? Il s'agit d'estimer une **espérance** $\mathbf x_0^\top\boldsymbol\beta$ : on veut un **intervalle de confiance de la moyenne**.
2. **Quel sera le panier** d'*un* nouveau client Instagram de 25 ans ? Il s'agit de prévoir une **observation** $y_0=\mathbf x_0^\top\boldsymbol\beta+\varepsilon_0$ : on veut un **intervalle de prédiction**, plus large, car il faut ajouter le bruit individuel $\varepsilon_0$.

> 📐 **Les deux formules.** La valeur prédite est $\hat y_0=\mathbf x_0^\top\hat{\boldsymbol\beta}$, de variance $\sigma^2\,\mathbf x_0^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf x_0$. Posons $h_0=\mathbf x_0^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf x_0$ (le « levier » du point $\mathbf x_0$). Alors
> $$\text{IC de la moyenne :}\ \ \hat y_0\pm t_{n-p,\,0{,}975}\;s\sqrt{h_0},\qquad\text{intervalle de prédiction :}\ \ \hat y_0\pm t_{n-p,\,0{,}975}\;s\sqrt{1+h_0}.$$
> Dans le second cas, l'erreur de prévision est $y_0-\hat y_0=\varepsilon_0-\mathbf x_0^\top(\hat{\boldsymbol\beta}-\boldsymbol\beta)$ : somme de deux termes **indépendants** ($\varepsilon_0$ est un nouveau bruit, indépendant de l'échantillon), d'où la variance $\sigma^2(1+h_0)$.

**À la main, sur les quatre commandes du 1.1.1.** Quel montant prévoir pour une commande de **5 articles** ? On a $\hat y_0=3+19{,}6\times5=101$ DT, $s^2=\text{SCR}/(n-p)=25{,}2/2=12{,}6$, et $\mathbf x_0=(1,5)^\top$ donne $h_0=\frac1{20}(30-2\cdot10\cdot5+4\cdot25)=\frac{30}{20}=1{,}5$ (calcul avec $(\mathbf X^\top\mathbf X)^{-1}=\frac1{20}\begin{pmatrix}30&-10\\-10&4\end{pmatrix}$). Avec $n-p=2$ degrés de liberté, $t_{2,\,0{,}975}\approx4{,}303$ : IC de la moyenne $101\pm4{,}303\sqrt{12{,}6\times1{,}5}\approx101\pm18{,}7$ ; intervalle de prédiction $101\pm4{,}303\sqrt{12{,}6\times2{,}5}\approx101\pm24{,}2$. Vérifions :

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

Ces intervalles sont énormes parce que $n=4$ et que $x_0=5$ est **hors de la plage** des données ($1$ à $4$) : $h_0=1{,}5$ est grand. C'est une propriété générale : $h_0$ **croît quand $\mathbf x_0$ s'éloigne du centre des données**, si bien que l'incertitude explose en **extrapolation**.

**Sur les clients de Dar Jasmin.** Dessinons, pour les clients acquis par Instagram, le nuage log-panier contre âge avec la droite ajustée par `m2`, la bande de confiance de la moyenne et la bande de prédiction.

```python
grille = pd.DataFrame({"age": np.arange(18, 76)})
grille["a"] = grille["age"] - 36
grille["canal"] = pd.Categorical(["Instagram"] * len(grille), categories=["Boutique", "Site", "Instagram"])
pf = m2.get_prediction(grille).summary_frame(alpha=0.05)

insta = df[df["canal"] == "Instagram"]
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.scatter(insta["age"], insta["log_panier"], s=9, color=GRIS, alpha=0.55, label="clients Instagram")
ax.fill_between(grille["age"], pf["obs_ci_lower"], pf["obs_ci_upper"], color=ORANGE, alpha=0.15, label="intervalle de prédiction à 95 % (un client)")
ax.fill_between(grille["age"], pf["mean_ci_lower"], pf["mean_ci_upper"], color=BLEU, alpha=0.45, label="intervalle de confiance à 95 % (le panier moyen)")
ax.plot(grille["age"], pf["mean"], color=BLEU, lw=2)
ax.set_xlabel("âge (ans)")
ax.set_ylabel("log du panier moyen")
ax.legend(frameon=False, loc="upper left", fontsize=8.5)
ax.set_ylim(2.3, 5.9)
plt.savefig("figures/ch01-bandes-prediction.png", dpi=200, bbox_inches="tight")
dans = ((insta["log_panier"] >= np.interp(insta["age"], grille["age"], pf["obs_ci_lower"])) &
        (insta["log_panier"] <= np.interp(insta["age"], grille["age"], pf["obs_ci_upper"]))).mean()
print(f"part des {len(insta)} clients Instagram situés dans l'intervalle de prédiction à 95 % : {100*dans:.1f} %")
```
<!--sortie-->
```text
part des 687 clients Instagram situés dans l'intervalle de prédiction à 95 % : 94.8 %
```

![Clients Instagram : log du panier selon l'âge. La bande bleue (intervalle de confiance de la moyenne) est étroite ; la bande orange (prédiction pour un client) est beaucoup plus large et contient environ 95 % des points.](figures/ch01-bandes-prediction.png)

Deux observations. La bande de **confiance** est étroite et se resserre autour de l'âge moyen (là où $h_0$ est minimal), tout en s'évasant aux âges extrêmes. La bande de **prédiction** est quasi parallèle à la droite et très large : elle est dominée par le terme « $1$ » (le bruit individuel), que **rien** ne peut réduire, même avec un échantillon infini. Retenons : *on peut connaître très précisément le panier moyen d'un groupe, et pourtant prévoir très mal le panier d'un individu*.

En dinars, il suffit d'appliquer l'exponentielle aux bornes (la transformation est croissante) :

```python
nouveau = pd.DataFrame({"a": [25 - 36], "canal": pd.Categorical(["Instagram"], categories=["Boutique", "Site", "Instagram"])})
r = m2.get_prediction(nouveau).summary_frame(alpha=0.05).iloc[0]
print(f"log-panier prédit : {r['mean']:.3f}")
print(f"panier médian prédit : {np.exp(r['mean']):.1f} DT | IC95 % de la médiane : [{np.exp(r['mean_ci_lower']):.1f} ; {np.exp(r['mean_ci_upper']):.1f}] DT")
print(f"un nouveau client Instagram de 25 ans : panier entre {np.exp(r['obs_ci_lower']):.1f} et {np.exp(r['obs_ci_upper']):.1f} DT avec 95 % de confiance")
```
<!--sortie-->
```text
log-panier prédit : 3.783
panier médian prédit : 43.9 DT | IC95 % de la médiane : [42.5 ; 45.4] DT
un nouveau client Instagram de 25 ans : panier entre 21.2 et 91.0 DT avec 95 % de confiance
```

Remarquez le vocabulaire : l'exponentielle des bornes de l'IC de $\mathbb E[\log y]$ donne un intervalle pour la **médiane** de $y$ (et non pour sa moyenne, cf. 1.1.8). L'intervalle de prédiction, lui, se transforme sans difficulté, car il concerne une observation.

### 1.2.5 Vérifier la théorie par simulation : la couverture des intervalles

Tout ceci repose sur H1-H5. Que vaut vraiment « 95 % de confiance » ? Vérifions-le comme on vérifie un théorème : en **répétant l'expérience** un grand nombre de fois quand on connaît la vérité. Utilisons le plan d'expérience réel $\mathbf X$ de `m2` (mêmes 1 740 clients), des coefficients vrais $\boldsymbol\beta^\star$ choisis par nous, un bruit normal d'écart-type 0,37, et générons 4 000 jeux de données. Pour chacun, nous construisons l'intervalle à 95 % du coefficient d'Instagram et vérifions s'il contient la vraie valeur.

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
print("statistique t pour Instagram : moyenne =", Tst[:, 2].mean().round(3), "| écart-type =", Tst[:, 2].std().round(3),
      "| écart-type théorique de t(n-p) =", round(np.sqrt((n - p) / (n - p - 2)), 3))
print("part de |t| > 1,96 quand H0 est vraie (erreur de type I) pour l'âge :", (np.abs(Tst[:, 3]) > 1.96).mean().round(3))
```
<!--sortie-->
```text
couverture empirique de l'IC à 95 % :
Intercept                0.944
C(canal)[T.Site]         0.951
C(canal)[T.Instagram]    0.948
a                        0.950
statistique t pour Instagram : moyenne = 0.008 | écart-type = 1.01 | écart-type théorique de t(n-p) = 1.001
part de |t| > 1,96 quand H0 est vraie (erreur de type I) pour l'âge : 0.05
```

Les intervalles à 95 % couvrent la vraie valeur dans environ 95 % des jeux de données, pour chacun des quatre coefficients, et la statistique $t$ centrée sur la vérité se comporte comme une loi de Student (moyenne nulle, écart-type voisin de 1). Quand l'hypothèse nulle est vraie, le test $t$ à 5 % se trompe dans environ 5 % des cas : c'est exactement ce que promet la théorie. **Mais** n'oublions pas que cette simulation **respecte** H1 à H5 par construction. Dans la vraie vie, la couverture dépend de la qualité du modèle : c'est tout l'objet de la section 1.3.

### 1.2.6 Quand on ne veut pas supposer la normalité : le bootstrap des couples

Le bootstrap du volume I (section 3.3.5) s'étend à la régression : on tire au hasard, **avec remise**, des **clients entiers** (le vecteur $(y_i,\mathbf x_i)$, d'où le nom de « bootstrap des couples »), on réajuste le modèle sur chaque rééchantillon, et on observe la variabilité des coefficients. Aucune formule, aucune hypothèse de normalité.

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
Intercept                  4.1863       4.2549              4.1868               4.2545        0.0175          0.0172
C(canal)[T.Site]          -0.2024      -0.1119             -0.2021              -0.1131        0.0231          0.0227
C(canal)[T.Instagram]     -0.3809      -0.2927             -0.3794              -0.2931        0.0225          0.0216
a                          0.0075       0.0108              0.0075               0.0108        0.0008          0.0008
```

Les deux approches donnent des intervalles quasi identiques : ici, la formule théorique est fiable. Le bootstrap devient précieux quand les hypothèses sont douteuses (erreurs très asymétriques, petit échantillon, quantité d'intérêt compliquée comme un rapport de coefficients).

### 1.2.7 Retour aux questions de Yasmine

Nous pouvons maintenant répondre honnêtement aux trois questions de l'introduction du chapitre :

1. **« Combien dépense un client Instagram de 50 ans par rapport à un client de la boutique de 30 ans ? »** C'est une combinaison linéaire de coefficients : effet du canal (−0,34) plus 20 ans d'âge (+20 × 0,009). Son intervalle de confiance s'obtient par la formule de variance d'une combinaison (1.2.2).
2. **« Est-ce le canal ou l'âge ? »** Le test $F$ du canal est très significatif **à âge égal** (1.2.3) : ce n'est pas l'âge. Et réciproquement.
3. **« Quel panier prévoir pour un nouveau client ? »** Un intervalle de prédiction, large (1.2.4).

```python
c1 = np.array([0, 0, 1, 20.0])              # coef_Instagram + 20 * coef_age  (par rapport à la référence « Boutique, 30 ans »)
est = c1 @ beta
se_c = np.sqrt(s2 * c1 @ XtX_inv @ c1)
bas, haut = est - crit * se_c, est + crit * se_c
print(f"effet estimé : {est:+.3f} (log) -> panier {100*(np.exp(est)-1):+.1f} %   IC95 % : [{100*(np.exp(bas)-1):+.1f} % ; {100*(np.exp(haut)-1):+.1f} %]")
print(m2.t_test("C(canal)[T.Instagram] + 20*a = 0").summary_frame().round(4).to_string())
```
<!--sortie-->
```text
effet estimé : -0.153 (log) -> panier -14.2 %   IC95 % : [-18.8 % ; -9.4 %]
      coef  std err       t  P>|t|  Conf. Int. Low  Conf. Int. Upp.
c0 -0.1534    0.028 -5.4802    0.0         -0.2083          -0.0985
```

Un client Instagram de 50 ans dépense donc, en moyenne géométrique, environ **14 % de moins** qu'un client de la boutique de 30 ans : les 20 ans d'âge de plus compensent un peu plus de la moitié de l'écart de canal. Cette comparaison de deux profils précis, avec son intervalle (de −19 % à −9 %), est typiquement ce qu'une simple comparaison de moyennes de groupes ne peut pas donner.

> ✅ **À retenir (1.2).**
> - Sous H1-H5, $\hat{\boldsymbol\beta}\sim\mathcal N(\boldsymbol\beta,\sigma^2(\mathbf X^\top\mathbf X)^{-1})$, $\text{SCR}/\sigma^2\sim\chi^2_{n-p}$, et les deux sont indépendants : d'où $T_j=(\hat\beta_j-\beta_j)/\operatorname{se}(\hat\beta_j)\sim t_{n-p}$ avec $\operatorname{se}(\hat\beta_j)=s\sqrt{c_{jj}}$.
> - Le **test $t$** teste un coefficient ; le **test $F$** de modèles emboîtés, $F=\frac{(\text{SCR}_0-\text{SCR}_1)/q}{\text{SCR}_1/(n-p_1)}$, teste $q$ contraintes à la fois (par exemple tout un facteur qualitatif, ou une interaction). Pour $q=1$, $F=t^2$.
> - Préférez les **intervalles de confiance** aux seules p-valeurs ; en échelle logarithmique, transformez les bornes par $e^{(\cdot)}$ pour parler en pourcentage.
> - **Intervalle de confiance de la moyenne** ($\hat y_0\pm t\,s\sqrt{h_0}$) et **intervalle de prédiction** ($\hat y_0\pm t\,s\sqrt{1+h_0}$) répondent à deux questions différentes ; le second ne peut pas rétrécir en dessous du bruit individuel, et les deux **s'élargissent en extrapolation**.
> - Une simulation confirme que « 95 % » signifie bien 95 % de couverture… **quand le modèle est correct** ; le bootstrap des couples est une alternative sans hypothèse de normalité.
