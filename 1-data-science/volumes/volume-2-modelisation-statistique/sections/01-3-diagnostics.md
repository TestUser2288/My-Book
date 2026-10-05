## 1.3 Diagnostics : le modèle est-il fiable ?

> 💡 **Intuition.** Un logiciel produit un tableau de coefficients quoi qu'on lui donne, même si le modèle est absurde. Les p-valeurs et les intervalles du 1.2 ne valent **que si les hypothèses H1 à H5 sont à peu près vraies**. Faire des diagnostics, c'est la visite médicale du modèle : on regarde ce qui reste *après* l'ajustement (les résidus), parce que les erreurs d'un modèle bien spécifié ne doivent contenir **aucune structure**. Si l'on voit une courbe, un entonnoir ou un point isolé dans les résidus, c'est que le modèle a raté quelque chose.

Nous reprenons les données des sections précédentes (modèles `m2` sur le log du panier et `m_niv` sur le panier en euros) et nous chargeons en plus les **ventes mensuelles** de la boutique (120 mois), qui nous serviront de deuxième terrain d'observation.

```python hide
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from statsmodels.stats.outliers_influence import variance_inflation_factor
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, ENCRE, GRIS, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#0b0b0b", "#898781", "#e34948"
STYLE = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": "#e1e0d9",
         "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb", "axes.facecolor": "#fcfcfb",
         "savefig.facecolor": "#fcfcfb", "font.size": 10, "axes.edgecolor": "#c3c2b7"}
plt.rcParams.update(STYLE)

clients = pd.read_csv("donnees/clients.csv")
df = clients[clients["nb_commandes_an"] > 0].copy()
df["canal"] = pd.Categorical(df["canal_acquisition"], categories=["Boutique", "Site", "Réseaux"])
df["a"] = df["age"] - 36
df["log_panier"] = np.log(df["panier_moyen"])

m_niv = smf.ols("panier_moyen ~ a + C(canal)", data=df).fit()      # panier en € : modèle « niveau »
m2 = smf.ols("log_panier ~ a + C(canal)", data=df).fit()           # log du panier : le modèle de 1.1 et 1.2

ventes = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"])
ventes["t"] = np.arange(len(ventes))                               # numéro du mois : 0, 1, ..., 119
print(len(df), "clients actifs |", len(ventes), "mois de ventes")
```
<!--sortie-->
```text
1740 clients actifs | 120 mois de ventes
```

### 1.3.1 Les résidus : brut, standardisé, studentisé

Le résidu brut $\hat\varepsilon_i=y_i-\hat y_i$ approche l'erreur $\varepsilon_i$. Mais attention : les résidus **n'ont pas tous la même variance**, même si les erreurs vraies, elles, l'ont.

> 📐 **Variance d'un résidu.** On a vu (1.1.5) que $\hat{\boldsymbol\varepsilon}=(\mathbf I-\mathbf H)\boldsymbol\varepsilon$. Donc
> $$\operatorname{Var}(\hat{\boldsymbol\varepsilon})=(\mathbf I-\mathbf H)\,\sigma^2\mathbf I\,(\mathbf I-\mathbf H)^\top=\sigma^2(\mathbf I-\mathbf H),\qquad\text{soit}\qquad\operatorname{Var}(\hat\varepsilon_i)=\sigma^2(1-h_{ii}),$$
> où $h_{ii}$ est le $i$-ième élément diagonal de la matrice chapeau (le **levier** de l'observation $i$, étudié plus loin).

Un point à fort levier « attire » la droite vers lui : son résidu est mécaniquement plus petit. Pour comparer les résidus entre eux, on les **standardise** :

| Résidu | Formule | Usage |
|---|---|---|
| brut | $\hat\varepsilon_i=y_i-\hat y_i$ | calcul de base |
| **standardisé** (*studentisé en interne*) | $r_i=\dfrac{\hat\varepsilon_i}{s\sqrt{1-h_{ii}}}$ | variance ≈ 1 pour tous : comparable |
| **studentisé externe** | $t_i=\dfrac{\hat\varepsilon_i}{s_{(i)}\sqrt{1-h_{ii}}}$ | $s_{(i)}$ = écart-type estimé **sans** l'observation $i$ ; suit exactement une loi $t_{n-p-1}$ si le modèle est correct : sert à **tester** si $i$ est aberrante |

Sur les quatre commandes du 1.1.1 (leviers 0,7 ; 0,3 ; 0,3 ; 0,7, résidus bruts −0,6 ; −1,2 ; +4,2 ; −2,4, écart-type résiduel $s=\sqrt{12{,}6}\approx3{,}55$), la formule donne les résidus standardisés hmtBc0{,}309$ ; hmtBc0{,}404$ ; {,}414$ ; hmtBc1{,}234$ ; `statsmodels` retrouve exactement les mêmes valeurs. On voit que le dernier point (levier 0,7) a un résidu brut de −2,4 qui, une fois standardisé, pèse presque autant que celui du point C.

```python hide
x4 = np.array([1, 2, 3, 4]); y4 = np.array([22, 41, 66, 79])
X4 = np.column_stack([np.ones(4), x4])
H4 = X4 @ np.linalg.inv(X4.T @ X4) @ X4.T
h4 = np.diag(H4)
e4 = y4 - H4 @ y4
n4, p4 = X4.shape
s4 = np.sqrt(e4 @ e4 / (n4 - p4))
r4 = e4 / (s4 * np.sqrt(1 - h4))                                         # standardisés
infl4 = sm.OLS(y4, X4).fit().get_influence()
print("leviers h_ii             :", h4.round(2))
print("résidus bruts            :", e4.round(2))
print("standardisés (main)      :", r4.round(3), "| statsmodels :", infl4.resid_studentized_internal.round(3))
```
<!--sortie-->
```text
leviers h_ii             : [0.7 0.3 0.3 0.7]
résidus bruts            : [-0.6 -1.2  4.2 -2.4]
standardisés (main)      : [-0.309 -0.404  1.414 -1.234] | statsmodels : [-0.309 -0.404  1.414 -1.234]
```

Pour le résidu studentisé externe, on n'a pas besoin de refaire $n$ régressions : $s_{(i)}^2=\big(\text{SCR}-\hat\varepsilon_i^2/(1-h_{ii})\big)/(n-p-1)$ (résultat classique, que `statsmodels` utilise aussi). Nous le vérifierons en 1.3.4 sur un exemple plus fourni. Sur ces *quatre* points, il est d'ailleurs dégénéré pour la commande C : les trois autres points $(1,22),(2,41),(4,79)$ sont **exactement alignés** (pente 19), donc $s_{(C)}=0$ et la statistique serait infinie. C'est une bonne illustration de ce qu'un test d'aberrance demande plus de points que cela.

### 1.3.2 Les graphiques de résidus : voir avant de tester

Trois graphiques suffisent à repérer l'essentiel :

1. **Résidus contre valeurs ajustées** : doit ressembler à un **nuage sans structure** centré sur 0. Une **courbe** signale une non-linéarité (H1) ; un **entonnoir** (dispersion qui augmente), une variance non constante (H4).
2. **Diagramme quantile-quantile (Q-Q) des résidus standardisés** : les points doivent suivre la diagonale si les erreurs sont normales (H5). Une queue relevée indique une asymétrie ou des valeurs extrêmes.
3. **Échelle-position** ($\sqrt{|r_i|}$ contre valeurs ajustées) : une tendance croissante confirme une variance non constante.

Mettons en concurrence **deux modèles pour le même phénomène** : le panier en euros (`m_niv`) et son logarithme (`m2`). Le premier est celui que l'on écrirait « naturellement » ; le second celui que nous avons choisi en 1.1.7 parce que le panier est asymétrique. Les diagnostics vont nous dire si ce choix était justifié.

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

![Diagnostics comparés. Ligne du haut : modèle sur le panier en € (résidus asymétriques, dispersion croissante, queue lourde à droite). Ligne du bas : modèle sur le log du panier (nuage homogène, points alignés sur la diagonale). La courbe orange est un lissage local.](figures/ch01-diagnostics-niveau-log.png)

La différence est nette. Pour le panier en euros (ligne du haut), les résidus sont très **asymétriques** : une nuée de points très hauts (jusqu'à 7 écarts-types), mais aucun point aussi bas, et le diagramme Q-Q montre une **queue droite très relevée** et une queue gauche trop courte. La dispersion augmente aussi avec la valeur ajustée : le lissage de l'échelle-position monte de 0,6 à 0,85 environ (l'entonnoir est modeste à l'œil, mais le test de Breusch-Pagan, ci-dessous, ne s'y trompe pas). Pour le log du panier (ligne du bas), le nuage est homogène, le lissage orange reste plat, et les points suivent la diagonale. La transformation logarithmique n'était donc pas un détail esthétique : elle rend le modèle **valide**.

> 💡 **Pourquoi le log résout le problème.** Quand les effets sont **multiplicatifs** ($y=\mu\cdot\eta$ avec $\eta$ un facteur aléatoire autour de 1), l'écart-type de $y$ est proportionnel à sa moyenne $\mu$ : les gros paniers fluctuent plus que les petits, exactement l'entonnoir observé. En passant au logarithme, $\log y=\log\mu+\log\eta$ : le bruit devient **additif** et de variance constante.

### 1.3.3 Les tests de diagnostic (et pourquoi ils ne remplacent pas les graphiques)

Des tests formalisent ce que l'œil voit.

**Variance non constante : le test de Breusch-Pagan.** Idée : si la variance dépend des variables explicatives, alors les carrés des résidus $\hat\varepsilon_i^2$ (estimations grossières de la variance) doivent être **prévisibles** à partir de $\mathbf X$. On régresse donc $\hat\varepsilon_i^2$ sur les mêmes variables ; si cette régression a un $R^2$ non négligeable, on rejette l'homoscédasticité. La statistique est $\text{LM}=n\,R^2_{\text{aux}}\sim\chi^2_{p-1}$ sous $H_0$ (variance constante). Calculons-la à la main pour les deux modèles et comparons à `statsmodels` :

```python hide
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

Pour le modèle en euros, `LM` vaut 35,9 (p-valeur de $8\times10^{-8}$) : l'homoscédasticité est nettement rejetée ; pour le modèle en logarithme, `LM` vaut 1,92 (p-valeur de 0,59) : on ne la rejette pas. Le calcul à la main coïncide avec celui de `statsmodels`.

**Normalité des erreurs.** Le test de Shapiro-Wilk et celui de Jarque-Bera (fondé sur l'asymétrie et l'aplatissement, volume I, section 3.7.5) comparent les résidus à une loi normale. Avec un grand $n$, ils détectent des écarts minuscules sans importance pratique : le diagramme Q-Q reste l'outil principal. Ici, l'asymétrie des résidus vaut 1,40 en euros (excès d'aplatissement de 3,84) contre 0,11 (−0,06) en logarithme ; les deux tests rejettent très nettement la normalité pour le modèle en euros (p-valeurs inférieures à $10^{-28}$) et ne la rejettent pas pour le modèle en logarithme (0,23 et 0,16).

```python hide
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

**Autocorrélation des erreurs (H4 : erreurs non corrélées).** Quand les observations sont ordonnées dans le temps, les erreurs successives peuvent se ressembler. Le test de **Durbin-Watson** mesure cela : $\text{DW}=\dfrac{\sum_{i\ge2}(\hat\varepsilon_i-\hat\varepsilon_{i-1})^2}{\sum_i\hat\varepsilon_i^2}\approx2(1-\hat\rho)$, où $\hat\rho$ est l'autocorrélation d'ordre 1 des résidus. Une valeur proche de 2 indique l'absence d'autocorrélation ; **inférieure à 2**, une autocorrélation positive. Les clients n'ont pas d'ordre naturel, donc ce test n'a pas de sens pour eux : utilisons plutôt les ventes mensuelles, avec le modèle d'une **tendance simple** $\text{ventes}_t=\beta_0+\beta_1 t+\varepsilon_t$, en niveau puis en logarithme.

```python hide
mv_niv = smf.ols("ca ~ t", data=ventes).fit()
mv_log = smf.ols("np.log(ca) ~ t", data=ventes).fit()
for nom, m in [("ca ~ t", mv_niv), ("log(ca) ~ t", mv_log)]:
    dw = sm.stats.durbin_watson(m.resid)
    print(f"{nom:12s} R² = {m.rsquared:.3f} | Durbin-Watson = {dw:.2f} (rho ≈ {1 - dw/2:.2f}) | Breusch-Pagan p = {sm.stats.diagnostic.het_breuschpagan(m.resid, m.model.exog)[1]:.3f}")

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
ca ~ t       R² = 0.464 | Durbin-Watson = 1.56 (rho ≈ 0.22) | Breusch-Pagan p = 0.004
log(ca) ~ t  R² = 0.493 | Durbin-Watson = 1.56 (rho ≈ 0.22) | Breusch-Pagan p = 0.889
figure enregistrée
```

![À gauche : les résidus du modèle de tendance sur le log des ventes forment des vagues saisonnières (ils ne sont pas du bruit pur). À droite : leur autocorrélation, avec des pics très nets aux décalages 12, 24 et 36 mois.](figures/ch01-residus-ventes.png)

Le $R^2$ du modèle en log est un peu meilleur, et c'est le seul des deux dont la variance est constante (Breusch-Pagan : $p=0{,}889$, contre $0{,}004$ en niveau). La valeur de Durbin-Watson, identique pour les deux modèles à deux décimales près (ce n'est pas une erreur de copie : la même structure temporelle persiste dans les deux jeux de résidus), est nettement inférieure à 2 : les erreurs sont **positivement autocorrélées** ($\hat\rho\approx0{,}22$ d'un mois sur le suivant). Mais la figure raconte une histoire bien plus riche que ce seul nombre. Le test de Durbin-Watson ne regarde que le **décalage d'un mois** ; or le graphique d'autocorrélation (à droite) montre trois pics très nets aux décalages **12, 24 et 36 mois** (autour de 0,6), et des creux négatifs vers 10 et 22 mois. La cause est identifiable : la **saisonnalité annuelle** (le pic de décembre revient chaque année), absente du modèle de tendance, se retrouve intégralement dans les résidus. Un seul test peut donc passer à côté d'une structure massive : *regardez toujours l'autocorrélation complète*.

Quand H4 (erreurs non corrélées) est violée, les estimations restent sans biais, mais **les erreurs standard sont fausses** (en général trop optimistes) : les p-valeurs du 1.2 ne sont plus fiables. La remédiation n'est pas un bricolage de régression ordinaire, mais les **modèles de séries temporelles** du chapitre 4 (section 4.1 : autocorrélation et décomposition saisonnière ; section 4.2 : ARIMA saisonniers).

> ⚠️ **Un test n'est pas un diagnostic.** (1) Avec un grand échantillon, un test rejette pour un écart minuscule et sans conséquence ; avec un petit échantillon, il laisse passer des défauts graves. (2) Un test ne dit pas **comment réparer**. (3) Les tests eux-mêmes supposent des hypothèses. Le bon réflexe : **graphique d'abord**, test ensuite pour *confirmer ce qu'on voit*, jugement enfin sur l'ampleur de l'écart.

### 1.3.4 Effet de levier et observations influentes

Certaines observations pèsent beaucoup plus que d'autres dans l'ajustement. Il faut distinguer trois notions, qu'on confond souvent :

- Un **point aberrant** (*outlier*) a un résidu **grand** : il est mal expliqué par le modèle.
- Un point à **fort levier** (*leverage*) a des valeurs de $\mathbf x$ **inhabituelles** (loin du centre des données) : il *peut* tirer la droite vers lui.
- Un point **influent** change **beaucoup** les résultats quand on le retire. Il est typiquement à la fois aberrant *et* à fort levier.

> 📐 **Le levier.** $h_{ii}=\mathbf x_i^\top(\mathbf X^\top\mathbf X)^{-1}\mathbf x_i$ est le $i$-ième élément diagonal de $\mathbf H$. Comme $\hat y_i=\sum_jh_{ij}y_j$, on a $\partial\hat y_i/\partial y_i=h_{ii}$ : c'est **le poids de $y_i$ dans sa propre prédiction**. Propriétés : $\tfrac1n\le h_{ii}\le1$ (avec constante) et $\sum_ih_{ii}=\operatorname{tr}\mathbf H=p$, donc le levier moyen vaut $p/n$. Règle empirique : un levier supérieur à $2p/n$ est « élevé ».
>
> **La distance de Cook** combine résidu et levier :
> $$D_i=\frac{(\hat{\boldsymbol\beta}-\hat{\boldsymbol\beta}_{(i)})^\top\mathbf X^\top\mathbf X\,(\hat{\boldsymbol\beta}-\hat{\boldsymbol\beta}_{(i)})}{p\,s^2}=\frac{r_i^2}{p}\cdot\frac{h_{ii}}{1-h_{ii}},$$
> où $\hat{\boldsymbol\beta}_{(i)}$ est l'estimateur calculé **sans** l'observation $i$ et $r_i$ le résidu standardisé. La première expression est la définition (« de combien l'ajustement bouge si j'enlève $i$, en unités d'erreur standard ») ; la seconde, un raccourci de calcul qui évite $n$ régressions. Il découle de l'identité $\hat{\boldsymbol\beta}-\hat{\boldsymbol\beta}_{(i)}=(\mathbf X^\top\mathbf X)^{-1}\mathbf x_i\,\hat\varepsilon_i/(1-h_{ii})$ (formule de Sherman-Morrison pour la mise à jour d'un inverse de matrice).

**Un petit exemple pour voir.** Six points : cinq bien alignés sur une droite de pente environ 2, et un sixième, **très à droite** ($x=12$), qui s'écarte de la tendance.

```python hide
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
pente avec les 6 points : 1.029 | sans le sixième point : 1.99
leviers h_ii : [0.325 0.247 0.196 0.17  0.17  0.892] (moyenne p/n = 0.333 )
résidus bruts : [-1.65 -0.88  0.39  0.96  2.24 -1.07]
résidus standardisés : [-1.23 -0.62  0.27  0.65  1.5  -1.99]
distances de Cook : [3.600e-01 6.000e-02 1.000e-02 4.000e-02 2.300e-01 1.643e+01]
prévision en x = 12 sans le sixième point : 23.9 | observé : 14.0
studentisés externes (main)  : [ -1.34  -0.56   0.23   0.59   1.96 -17.24]
studentisés externes (statsm.): [ -1.34  -0.56   0.23   0.59   1.96 -17.24]
Cook par réajustement : [3.600e-01 6.000e-02 1.000e-02 4.000e-02 2.300e-01 1.643e+01]
figure enregistrée
```

Sur ces six points, la pente vaut 1,03 avec les six points et 1,99 sans le sixième ; le levier du sixième point est de 0,89 (levier moyen $p/n=0{,}33$), son résidu standardisé de seulement −1,99, et sa distance de Cook de 16,4 (contre 0,36 au plus pour les cinq autres) ; sans lui, la tendance prévoyait 23,9 en $x=12$, alors qu'on a observé 14,0. Le calcul du résidu studentisé externe sans réajustement coïncide avec `statsmodels`.

![Un point à fort levier (rouge, x = 12) tire la droite orange vers lui. Sans ce point, la droite bleue suit le reste du nuage, et prévoit environ 24 en x = 12.](figures/ch01-levier.png)

Remarquez la leçon, qui surprend toujours : **le point influent a un résidu petit**. Comme la droite est tirée vers lui, son résidu brut est modeste (voyez la ligne des résidus), alors qu'il est très loin de ce que la tendance des cinq autres points prévoyait. C'est son **levier** (proche de 0,9, très au-dessus de la moyenne $p/n\approx0{,}33$) et sa **distance de Cook** qui le trahissent. Un diagnostic fondé sur les seuls résidus l'aurait laissé passer. Et la formule de Cook, retrouvée ici par réajustement sans chaque point, confirme le raccourci.

**Sur les clients de la boutique.** Appliquons ces outils au modèle `m2`. Avec 1 740 clients, un seul client ne pèse presque rien :

```python
infl = m2.get_influence()
h, cook = infl.hat_matrix_diag, infl.cooks_distance[0]
print(f"levier max = {h.max():.4f} | Cook max = {cook.max():.4f} | clients avec Cook > 4/n : {(cook > 4 / len(h)).sum()}")
```
<!--sortie-->
```text
levier max = 0.0089 | Cook max = 0.0067 | clients avec Cook > 4/n : 84
```

```python hide
n, p = m2.model.exog.shape
print(f"n = {n}, p = {p} | levier moyen p/n = {p/n:.4f} | levier maximal = {h.max():.4f} | seuil 2p/n = {2*p/n:.4f}")
print(f"distance de Cook maximale = {cook.max():.4f} | seuil usuel 4/n = {4/n:.4f} | seuil d'alerte forte : 1")
print(f"nombre de clients au-dessus de 4/n : {(cook > 4/n).sum()} sur {n} ({100*(cook > 4/n).mean():.1f} %)")
top = pd.DataFrame({"age": df["age"].to_numpy(), "canal": df["canal"].to_numpy(), "panier": df["panier_moyen"].to_numpy(),
                    "résidu stud. ext.": infl.resid_studentized_external, "levier": h, "Cook": cook}).sort_values("Cook", ascending=False).head(5)
print(top.round(4).to_string())
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

Aucun client n'a un levier ou une distance de Cook préoccupants : le plus grand levier (0,0089) est certes environ quatre fois le levier moyen (0,0023), mais il reste inférieur à 1 % (aucun client ne pèse même 1 % dans sa propre prédiction), et la distance de Cook maximale (0,0067) est plus de cent fois sous le seuil d'alerte de 1. Deux remarques de méthode :

- Le seuil « $D_i>4/n$ » est une **règle de dépistage**, pas un test : avec $n$ grand elle signale toujours quelques points (ici environ 5 % des clients), simplement parce que certains points sont toujours un peu plus éloignés que d'autres. Ce qui compte est qu'**aucun** ne soit isolé du lot. Regardez les valeurs, pas seulement le seuil.
- Le test des résidus studentisés externes, ajusté pour le nombre de tests (correction de **Bonferroni**, volume I, section 3.5.5), est un vrai test de « valeur aberrante » : la plus grande valeur absolue (environ 3,73) a une p-valeur brute de 0,0002, mais parmi 1 740 observations on s'attend à de telles valeurs : une fois la correction de Bonferroni appliquée, la p-valeur ajustée est de 0,35, rien de significatif.

> 💡 **Que faire d'une observation influente ?** Ne la supprimez **pas** automatiquement. (1) Vérifiez qu'il ne s'agit pas d'une **erreur de saisie** (un panier de 5 000 € au lieu de 50). (2) Si elle est authentique, regardez comment les conclusions changent **avec et sans** elle, et rapportez les deux. (3) Si elle représente un phénomène réel mais rare, envisagez une méthode **robuste** (section 1.6). Retirer un point « parce qu'il gêne » est l'une des formes les plus courantes de falsification involontaire.

### 1.3.5 La multicolinéarité : quand deux variables disent la même chose

Si deux variables explicatives sont presque redondantes, le modèle ne peut pas **départager** leurs effets. Les prédictions restent bonnes, mais les coefficients individuels deviennent **instables** et leurs erreurs standard explosent.

> 📐 **Pourquoi les erreurs standard explosent.** Par le théorème de Frisch-Waugh-Lovell (1.1.7), le coefficient de la variable $\mathbf x_j$ est la pente de la régression sur la partie de $\mathbf x_j$ qui n'est pas expliquée par les autres variables, soit $\tilde{\mathbf x}_j=\mathbf M_{-j}\mathbf x_j$ (les résidus de la régression de $\mathbf x_j$ sur les autres colonnes). Donc
> $$\operatorname{Var}(\hat\beta_j)=\frac{\sigma^2}{\|\tilde{\mathbf x}_j\|^2}=\frac{\sigma^2}{\text{SCT}_j\,(1-R_j^2)},$$
> où $\text{SCT}_j=\sum_i(x_{ij}-\bar x_j)^2$ et $R_j^2$ est le $R^2$ de la régression de $\mathbf x_j$ sur les autres variables explicatives. Quand $R_j^2\to1$ (colinéarité), la partie « propre » de $\mathbf x_j$ disparaît et la variance explose. Le **facteur d'inflation de la variance** est
> $$\text{VIF}_j=\frac{1}{1-R_j^2}.$$
> Règles empiriques : $\text{VIF}>5$ : à surveiller ; $\text{VIF}>10$ : problématique.

**Provoquons le problème.** Ajoutons au modèle `m2` l'âge **exprimé en mois**, mesuré avec un petit bruit (le client indique son âge « à peu près » ; l'âge en mois est quasiment $12\times$ l'âge en années) :

```python hide
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

Les prédictions sont aussi bonnes (le $R^2$ ne bouge pas), mais regardez les coefficients de l'âge : l'erreur standard de `a` est multipliée par plus de quarante, et le coefficient lui-même est devenu **négatif** et non significatif : pourtant, nous savons que l'effet de l'âge est positif. Les deux variables se « disputent » le même effet. Les VIF, de l'ordre de 1 800, le disent sans ambiguïté, alors que ceux des variables de canal restent bas (1,5). Les coefficients du **canal** sont, eux, intacts, car ils ne sont pas corrélés avec ce couple : la multicolinéarité n'abîme que les coefficients des variables concernées.

**Une colinéarité plus sournoise : les termes polynomiaux non centrés.** Si l'on ajoute le carré de l'âge pour tester une courbure, $\text{âge}$ et $\text{âge}^2$ sont très corrélés (les deux croissent ensemble). Le **centrage** règle le problème :

```python hide
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

Le terme quadratique n'est pas significatif dans les deux cas (la p-valeur du terme du second degré est identique avec ou sans centrage, comme il se doit : on décrit le *même* modèle), mais les VIF passent de plus de 30 à 1 après centrage, ce qui rend les coefficients lisibles. L'âge n'a pas de courbure détectable : la relation avec le log-panier est bien linéaire (H1 est plausible).

> 💡 **Que faire en cas de multicolinéarité ?** (1) **Retirer** une des variables redondantes, ou les **combiner** en une seule (moyenne, indice). (2) **Centrer** les variables avant de créer des puissances ou des interactions. (3) Si l'on tient à garder toutes les variables et que l'objectif est la **prédiction**, la **régularisation** (Ridge, section 1.5) stabilise les coefficients. (4) Si l'objectif est d'**interpréter** un effet précis, il faut accepter qu'on ne peut pas séparer l'effet de deux variables quasi identiques : il est plus honnête de le dire.

### 1.3.6 Variance non constante : que faire ?

Pour `m_niv`, nous avons vu que le défaut est net. Trois remèdes :

1. **Transformer la réponse** (le logarithme, ici : c'est la solution privilégiée, car elle rend le modèle plus naturel).
2. **Changer de famille de lois** (modèles linéaires généralisés, chapitre 2 : par exemple une régression Gamma, qui suppose précisément que l'écart-type est proportionnel à la moyenne).
3. **Garder le modèle en niveau et corriger les erreurs standard** par la méthode « robuste à l'hétéroscédasticité ». C'est utile quand on tient à l'échelle d'origine.

> 📐 **Erreurs standard de White (« sandwich »).** Si $\operatorname{Var}(\boldsymbol\varepsilon)=\boldsymbol\Omega$ est diagonale mais avec des $\sigma_i^2$ différents, alors $\hat{\boldsymbol\beta}$ reste sans biais, mais sa variance devient
> $$\operatorname{Var}(\hat{\boldsymbol\beta})=(\mathbf X^\top\mathbf X)^{-1}\Big(\sum_i\sigma_i^2\,\mathbf x_i\mathbf x_i^\top\Big)(\mathbf X^\top\mathbf X)^{-1}$$
> (le « sandwich » : deux tranches de pain $(\mathbf X^\top\mathbf X)^{-1}$ autour de la garniture). On remplace $\sigma_i^2$ par un estimateur : $\hat\varepsilon_i^2$ (version **HC0**), ou, plus prudent pour les échantillons de taille modérée, $\hat\varepsilon_i^2/(1-h_{ii})^2$ (version **HC3**). La formule classique $\sigma^2(\mathbf X^\top\mathbf X)^{-1}$ n'en est qu'un cas particulier (variances égales).

Comparons, pour `m_niv`, les erreurs standard classiques, robustes (HC3), et celles d'un bootstrap des couples (qui ne fait aucune hypothèse sur la variance) :

```python hide
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

Les erreurs standard robustes sont plus proches du bootstrap que les erreurs classiques pour la constante, le coefficient du Site et celui de Réseaux : la formule classique **sous-estimait** l'incertitude de ces coefficients (de 12 % environ pour la constante et le Site : pour le Site, 1,52 par la formule classique, 1,69 en robuste et 1,66 par bootstrap). Pour le coefficient de l'âge, tout concorde. L'écart n'est pas énorme, mais il va dans le sens qu'annonce la théorie. Dans les modèles où l'hétéroscédasticité est plus forte, il peut être considérable.

### 1.3.7 Courbure et variables manquantes : lire les graphiques de résidus partiels

Pour déceler une relation **non linéaire** avec une variable précise $x_j$, on trace les **résidus partiels** : $\hat\varepsilon_i+\hat\beta_jx_{ij}$ contre $x_{ij}$. Si la relation est linéaire, le nuage suit la droite de pente $\hat\beta_j$ ; une courbure systématique suggère d'ajouter un terme (carré, logarithme, ou une transformation plus flexible, cf. les GAM de la section 2.5).

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

![Résidus partiels pour l'âge : le lissage local (orange) suit la droite du modèle (bleu pointillé) : pas de courbure détectable.](figures/ch01-residus-partiels.png)

Le lissage orange épouse la droite bleue : la linéarité en l'âge est acceptable (ce que le test du terme quadratique, plus haut, confirmait). Notez que le lissage s'écarte un peu aux âges extrêmes, où il y a peu de clients : c'est du bruit d'échantillonnage, pas de la structure.

**Verdict sur `m2`.** Le modèle `log_panier ~ a + C(canal)` passe les contrôles : linéarité plausible, variance constante (Breusch-Pagan non significatif), résidus proches de la normale, aucune observation influente, pas de colinéarité entre ses variables. Les intervalles du 1.2 sont donc fiables. Ce n'est **pas** une preuve que le modèle est « vrai » (des variables importantes peuvent manquer), seulement que ses hypothèses ne sont pas manifestement violées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.5, exercices 1.6, 1.8 et 1.10.

> ✅ **À retenir (1.3).**
> - Les résidus d'un bon modèle ne contiennent **aucune structure**. Regardez : résidus contre ajustées (courbure, entonnoir), Q-Q (normalité), échelle-position (variance).
> - $\operatorname{Var}(\hat\varepsilon_i)=\sigma^2(1-h_{ii})$ : on **standardise** (ou studentise) les résidus avant de les comparer. Un point à fort levier a un résidu brut **petit** : ne vous fiez pas aux seuls résidus.
> - **Levier** $h_{ii}$ (valeurs inhabituelles de $\mathbf x$), **résidu** (écart à la prédiction) et **influence** (changement des résultats si on retire le point, **distance de Cook**) sont trois notions distinctes. Ne supprimez jamais un point sans enquêter.
> - **VIF** $=1/(1-R_j^2)$ mesure l'inflation de variance due à la colinéarité ; **centrer** avant de créer des puissances.
> - Si la variance n'est pas constante : transformer (log), changer de famille (GLM), ou corriger les erreurs standard (**sandwich**, HC3). Si les erreurs sont **autocorrélées** (séries temporelles) : chapitre 4.
> - Un test (Breusch-Pagan, Shapiro, Durbin-Watson) **complète** un graphique, il ne le remplace pas.
