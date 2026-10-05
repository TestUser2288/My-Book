## 4.4 ➕ Pour aller plus loin : séries multivariées, cointégration et GARCH

> 🧭 **Section optionnelle.** Les sections 4.1 à 4.3 traitent **une** série à la fois et se suffisent à elles-mêmes. Ici, nous élargissons le cadre dans trois directions : **plusieurs séries qui s'influencent** (VAR), **des séries qui dérivent mais restent liées** (cointégration), et **une variabilité qui change dans le temps** (GARCH). Si vous cherchez l'essentiel, sautez à la section 4.5 ou aux exercices.

### 4.4.1 Plusieurs séries à la fois : le modèle VAR

Le chiffre d'affaires et le **nombre de commandes** sont deux séries liées. Un modèle **VAR** (*vector autoregression*) décrit chacune comme une combinaison du passé de *toutes* les séries. Pour deux séries $y_{1,t}$ et $y_{2,t}$, regroupées dans le vecteur $\mathbf y_t$, le VAR(1) s'écrit

$$\mathbf y_t=\mathbf c+A\,\mathbf y_{t-1}+\boldsymbol\varepsilon_t,\qquad A=\begin{pmatrix}a_{11}&a_{12}\\a_{21}&a_{22}\end{pmatrix}.$$

C'est un AR(1) où le coefficient $\varphi$ devient une **matrice**. Chaque ligne est une régression linéaire ordinaire (chapitre 1) de $y_{i,t}$ sur les deux retards : le coefficient $a_{12}$ dit combien le passé de la série 2 aide à prévoir la série 1, **au-delà** du passé de la série 1 elle-même.

> 📐 **Stationnarité d'un VAR(1).** Comme pour l'AR(1) ($|\varphi|<1$), la condition est que **toutes les valeurs propres de $A$ soient de module strictement inférieur à 1** (volume I, section 1.1.3 : une valeur propre mesure de combien la matrice étire une direction ; $A^k\to0$ si et seulement si ce facteur est inférieur à 1). Pour un VAR($p$), on applique la même condition à la « matrice compagne » du système.

> 💡 **Exemple à la main.** Soit $A=\begin{pmatrix}0{,}5&0{,}2\\0{,}1&0{,}4\end{pmatrix}$. Sa trace vaut $0{,}9$ et son déterminant $0{,}5\times0{,}4-0{,}2\times0{,}1=0{,}18$. Les valeurs propres sont solutions de $\lambda^2-0{,}9\lambda+0{,}18=0$, soit $\lambda=\frac{0{,}9\pm\sqrt{0{,}81-0{,}72}}2=\frac{0{,}9\pm0{,}3}2$, donc $0{,}6$ et $0{,}3$ : le système est stationnaire. Si un choc de 1 frappe la série 1 à la date 0, la réponse au pas $k$ est la première colonne de $A^k$ : $(1;0)$, puis $(0{,}5;\,0{,}1)$, puis $A^2\binom10=(0{,}27;\,0{,}09)$… C'est la **fonction de réponse impulsionnelle** : un choc sur une série se propage dans l'autre.

```python hide
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.api import VAR
from statsmodels.tsa.stattools import coint, adfuller
from statsmodels.stats.diagnostic import het_arch, acorr_ljungbox
from arch import arch_model

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
A = np.array([[0.5, 0.2], [0.1, 0.4]])
print("valeurs propres de A :", np.linalg.eigvals(A).round(3), "-> stationnaire :", bool(np.all(np.abs(np.linalg.eigvals(A)) < 1)))
for k in (1, 2, 3):
    print(f"réponse à un choc unitaire sur la série 1, pas {k} :", (np.linalg.matrix_power(A, k) @ np.array([1, 0])).round(3))
```
<!--sortie-->
```text
valeurs propres de A : [0.6+0.j 0.3+0.j] -> stationnaire : True
réponse à un choc unitaire sur la série 1, pas 1 : [0.5 0.1]
réponse à un choc unitaire sur la série 1, pas 2 : [0.27 0.09]
réponse à un choc unitaire sur la série 1, pas 3 : [0.153 0.063]
```

#### Un exemple : ventes et commandes

Le VAR suppose des séries **stationnaires**. Pour les rendre telles, on utilise l'idée de 4.2.7 : on retire de chaque série (en logarithme) sa **tendance, sa saison, la promotion et le COVID** par régression, et on garde l'**écart** — ce qui reste quand on a enlevé tout ce qu'on sait expliquer. Ces écarts sont stationnaires (nous le vérifions) et ce sont eux qui portent la dynamique conjointe. Nous utilisons les 96 mois d'apprentissage.

```python hide
tr = XX[:"2023-12"]                                       # tendance, mois, promo, covid (objet défini en 4.3)
ecarts = pd.DataFrame({"e_ca": sm.OLS(np.log(v["ca"][:"2023-12"]), tr).fit().resid,
                       "e_nb": sm.OLS(np.log(v["nb_commandes"][:"2023-12"]), tr).fit().resid})
print("écarts-types :", ecarts.std().round(3).to_dict(), "| corrélation instantanée :", round(ecarts.corr().iloc[0, 1], 3))
for c in ecarts:
    print(f"test ADF de {c} : p-valeur = {adfuller(ecarts[c], regression='n', autolag='AIC')[1]:.1e}")

modele = VAR(ecarts)
print(modele.select_order(4).summary())
var1 = modele.fit(maxlags=1)
print(pd.concat({"coefficient": var1.params, "p-valeur": var1.pvalues}, axis=1).round(3).to_string())
print("modules des valeurs propres de la matrice A estimée :", np.abs(np.linalg.eigvals(var1.coefs[0])).round(3))
```
<!--sortie-->
```text
écarts-types : {'e_ca': 0.072, 'e_nb': 0.226} | corrélation instantanée : 0.235
test ADF de e_ca : p-valeur = 2.6e-07
test ADF de e_nb : p-valeur = 7.5e-08
 VAR Order Selection (* highlights the minimums) 
=================================================
      AIC         BIC         FPE         HQIC   
-------------------------------------------------
0      -8.241      -8.186   0.0002636      -8.219
1     -8.515*     -8.351*  0.0002004*     -8.449*
2      -8.479      -8.205   0.0002077      -8.369
3      -8.493      -8.109   0.0002051      -8.338
4      -8.466      -7.973   0.0002107      -8.267
-------------------------------------------------
        coefficient        p-valeur       
               e_ca   e_nb     e_ca   e_nb
const        -0.001 -0.005    0.930  0.825
L1.e_ca       0.520  0.675    0.000  0.036
L1.e_nb       0.026 -0.003    0.368  0.976
modules des valeurs propres de la matrice A estimée : [0.552 0.035]
```

Les deux écarts sont stationnaires (tests ADF : p-valeurs de l'ordre de $10^{-7}$). Les critères (AIC, BIC) choisissent **un seul retard**. Voici l'estimation du VAR(1) (un seul appel ; `ecarts` contient les deux écarts) :

```python
from statsmodels.tsa.api import VAR
var1 = VAR(ecarts).fit(maxlags=1)          # chaque écart est régressé sur les retards des deux écarts
print(var1.params.round(3))
```
<!--sortie-->
```text
          e_ca   e_nb
const   -0.001 -0.005
L1.e_ca  0.520  0.675
L1.e_nb  0.026 -0.003
```

Lecture des coefficients : l'écart de chiffre d'affaires d'un mois influence celui du mois suivant (coefficient d'environ $0{,}52$, comme le AR(1) du modèle C), et il **prévoit aussi** l'écart du nombre de commandes ($\approx0{,}68$, p-valeur $\approx0{,}04$). L'effet inverse (commandes $\to$ chiffre d'affaires) est proche de zéro.

> 📐 **Causalité au sens de Granger.** On dit que $x$ *cause* $y$ **au sens de Granger** si le passé de $x$ améliore la prévision de $y$ au-delà de son propre passé ; on le teste par un test de Fisher sur les coefficients du retard de $x$ dans l'équation de $y$ (hypothèse nulle : ils sont tous nuls). Ici, le chiffre d'affaires « précède » le nombre de commandes ($F=4{,}41$, $p=0{,}037$), mais pas l'inverse ($F=0{,}81$, $p=0{,}37$) ; la figure ci-dessous montre les réponses impulsionnelles.

```python hide
g1 = var1.test_causality("e_nb", ["e_ca"], kind="f")
g2 = var1.test_causality("e_ca", ["e_nb"], kind="f")
print(f"le chiffre d'affaires précède le nombre de commandes : F = {g1.test_statistic:.2f}, p = {g1.pvalue:.3f}")
print(f"le nombre de commandes précède le chiffre d'affaires : F = {g2.test_statistic:.2f}, p = {g2.pvalue:.3f}")

irf = var1.irf(8)
fig, axes = plt.subplots(1, 2, figsize=(10, 3.4), sharey=False)
for ax, (j, nom) in zip(axes, [(0, "choc sur l'écart de chiffre d'affaires"), (1, "choc sur l'écart de nombre de commandes")]):
    ax.plot(range(9), irf.irfs[:, 0, j], "o-", color=BLEU, lw=1.6, ms=4, label="réponse du chiffre d'affaires")
    ax.plot(range(9), irf.irfs[:, 1, j], "o-", color=ORANGE, lw=1.6, ms=4, label="réponse du nombre de commandes")
    ax.axhline(0, color="#898781", lw=0.8)
    ax.set_title(nom, fontsize=10)
    ax.set_xlabel("mois après le choc")
    ax.grid(True, color="#e1e0d9", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
axes[0].legend(fontsize=8)
plt.tight_layout()
plt.savefig("figures/ch04-var-irf.png", bbox_inches="tight")
```
<!--sortie-->
```text
le chiffre d'affaires précède le nombre de commandes : F = 4.41, p = 0.037
le nombre de commandes précède le chiffre d'affaires : F = 0.81, p = 0.369
```

![Fonctions de réponse impulsionnelle du VAR(1) : un choc de 1 sur l'écart de chiffre d'affaires (à gauche) se transmet à l'écart de commandes avec un effet plus important, puis s'atténue ; un choc sur les commandes (à droite) a très peu d'effet sur le chiffre d'affaires.](figures/ch04-var-irf.png)

> ⚠️ **« Cause au sens de Granger » ne veut pas dire « cause ».** Le test dit seulement que le passé du chiffre d'affaires **aide à prévoir** le nombre de commandes. Ici, la raison est connue, puisque nous avons fabriqué les données : le nombre de commandes est tiré d'une loi de Poisson dont la moyenne est le chiffre d'affaires du mois divisé par 58 (le panier moyen). Le nombre de commandes est donc une **mesure bruitée** du chiffre d'affaires *du même mois* ; comme le chiffre d'affaires est lui-même autocorrélé, son passé aide à prévoir cette mesure, et un nombre de commandes passé n'apporte rien de plus sur le chiffre d'affaires futur que le chiffre d'affaires passé lui-même. Aucune « influence » ne passe d'un mois à l'autre : c'est de l'**information**, pas de la causalité. Pour parler de causalité, il faut un schéma d'étude, pas un test de précédence (chapitre 7).

### 4.4.2 Cointégration : des séries qui dérivent ensemble

Passons à un autre piège, plus dangereux. Deux séries qui montent toutes les deux **semblent** liées, même si elles n'ont rien à voir. Prenons deux marches aléatoires **indépendantes** (4.1.3), régressons l'une sur l'autre, et regardons ce que dit la régression du chapitre 1. Nous avons répété l'expérience 1 000 fois (figure ci-dessous) :

```python hide
rng = np.random.default_rng(31)
n_sim = 1000
t_stats, r2, dw = [], [], []
for _ in range(n_sim):
    a = np.cumsum(rng.normal(size=100))
    b = np.cumsum(rng.normal(size=100))                      # indépendante de a par construction
    f = sm.OLS(a, sm.add_constant(b)).fit()
    t_stats.append(f.tvalues[1])
    r2.append(f.rsquared)
    dw.append(sm.stats.durbin_watson(f.resid))
t_stats = np.array(t_stats)
print("régressions d'une marche aléatoire sur une AUTRE, indépendante (100 points) :")
print("part des pentes « significatives » à 5 % :", round(np.mean(np.abs(t_stats) > 1.96), 3), " (on attendrait 0,05)")
print("R2 moyen :", round(np.mean(r2), 3), "| statistique de Durbin-Watson moyenne :", round(np.mean(dw), 3), " (2 = pas d'autocorrélation)")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 3.4))
a = np.cumsum(np.random.default_rng(5).normal(size=100))
b = np.cumsum(np.random.default_rng(6).normal(size=100))
ax1.plot(a, color=BLEU, lw=1.5, label="série 1")
ax1.plot(b, color=ORANGE, lw=1.5, label="série 2")
ax1.set_title("deux marches aléatoires indépendantes", fontsize=10)
ax1.legend(fontsize=8)
ax2.hist(t_stats, bins=50, color=BLEU, alpha=0.75)
ax2.axvline(-1.96, color=ROUGE, ls="--", lw=1.2)
ax2.axvline(1.96, color=ROUGE, ls="--", lw=1.2)
ax2.set_title("statistique t de la pente, 1 000 régressions", fontsize=10)
ax2.set_xlabel("valeur de t (les tirets marquent ±1,96)")
for ax in (ax1, ax2):
    ax.grid(True, color="#e1e0d9", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-regression-fallacieuse.png", bbox_inches="tight")
```
<!--sortie-->
```text
régressions d'une marche aléatoire sur une AUTRE, indépendante (100 points) :
part des pentes « significatives » à 5 % : 0.769  (on attendrait 0,05)
R2 moyen : 0.244 | statistique de Durbin-Watson moyenne : 0.172  (2 = pas d'autocorrélation)
```

![À gauche, deux marches aléatoires indépendantes qui semblent évoluer ensemble. À droite, les statistiques t de la pente de 1 000 régressions de ce type : elles sont bien plus dispersées que la loi de Student, et une majorité franchit les seuils de ±1,96.](figures/ch04-regression-fallacieuse.png)

Résultat : près de **quatre régressions sur cinq** (76,9 %) déclarent « significatif » un lien qui n'existe pas (au lieu de 5 %), avec un $R^2$ moyen de 0,244 et une statistique de Durbin-Watson moyenne de 0,17, très basse (les résidus sont très autocorrélés). C'est la **régression fallacieuse** (Granger et Newbold, 1974) : quand les séries ne sont pas stationnaires, les p-valeurs de la régression sont **fausses** (les hypothèses du chapitre 1 ne tiennent plus). Règle de prudence : si le $R^2$ est supérieur à la statistique de Durbin-Watson, méfiez-vous.

Comment distinguer une vraie relation d'une illusion ? Par la **cointégration**. Deux séries non stationnaires (intégrées d'ordre 1) sont **cointégrées** s'il existe une combinaison linéaire $y_t-\beta x_t$ qui, elle, est **stationnaire** : les deux séries dérivent, mais **elles dérivent ensemble**, comme deux promeneurs liés par une corde élastique. Exemple plausible pour la boutique : un indice du coût des matières premières ($x_t$, une marche aléatoire) et le prix moyen de vente ($y_t$), qui suit le coût avec un écart temporaire. Nous les **simulons** : $x_t$ est une marche aléatoire, $y_t=2+1{,}5\,x_t+u_t$ avec $u_t$ un AR(1) de coefficient $0{,}6$.

La **méthode d'Engle et Granger** a deux temps : (1) on régresse $y$ sur $x$ ; (2) on teste la **racine unitaire des résidus** (ADF de 4.1.6, avec des seuils adaptés car les résidus sont estimés). S'ils sont stationnaires, il y a cointégration.

```python hide
rng = np.random.default_rng(31)
n = 150
x = np.cumsum(rng.normal(size=n))
u = np.zeros(n)
for t in range(1, n):
    u[t] = 0.6 * u[t - 1] + rng.normal(0, 0.5)
y_coint = 2 + 1.5 * x + u
y_indep = np.cumsum(rng.normal(size=n))                      # une série qui n'a rien à voir avec x

for nom, serie in [("y cointégrée avec x", y_coint), ("y indépendante de x", y_indep)]:
    stat, p, _ = coint(serie, x, trend="c")
    print(f"{nom:22s} : statistique d'Engle-Granger = {stat:6.2f} | p-valeur = {p:.3f}")

reg = sm.OLS(y_coint, sm.add_constant(x)).fit()
print("régression de y sur x : constante =", round(reg.params[0], 3), "| pente =", round(reg.params[1], 3), "  (programmé : 2 et 1,5)")
```
<!--sortie-->
```text
y cointégrée avec x    : statistique d'Engle-Granger =  -4.54 | p-valeur = 0.001
y indépendante de x    : statistique d'Engle-Granger =  -2.55 | p-valeur = 0.257
régression de y sur x : constante = 2.118 | pente = 1.494   (programmé : 2 et 1,5)
```

Avec `statsmodels`, le test tient en une ligne :

```python
from statsmodels.tsa.stattools import coint
stat, p, _ = coint(y_coint, x, trend="c")          # test d'Engle-Granger ; y_coint et x : les deux séries simulées
print(round(stat, 2), round(p, 3))
```
<!--sortie-->
```text
-4.54 0.001
```

Sur nos deux séries cointégrées, la statistique vaut $-4{,}54$ ($p=0{,}001$) ; pour une série indépendante de $x$, $-2{,}55$ ($p=0{,}26$). La régression de $y$ sur $x$ donne une constante de $2{,}118$ et une pente de $1{,}494$ (programmé : 2 et 1,5).

Pour la série cointégrée, le test rejette « pas de cointégration » (p-valeur proche de 0,001) et la pente estimée est très proche de 1,5 (les estimateurs de cointégration sont *super-convergents* : ils convergent à la vitesse $n$ au lieu de $\sqrt n$). Pour la série indépendante, le test ne rejette pas.

> 📐 **Le modèle à correction d'erreur.** Si $y_t-\beta x_t-c=u_t$ avec $u_t=\varphi u_{t-1}+e_t$ stationnaire ($|\varphi|<1$), alors en différenciant $y_t=\beta x_t+c+u_t$ : $\Delta y_t=\beta\,\Delta x_t+\Delta u_t=\beta\,\Delta x_t+(\varphi-1)\,u_{t-1}+e_t$. En remplaçant $u_{t-1}$ par l'**écart à l'équilibre** $y_{t-1}-\beta x_{t-1}-c$, on obtient
> $$\Delta y_t=\gamma\,\Delta x_t+\alpha\,(y_{t-1}-\beta x_{t-1}-c)+e_t,\qquad \gamma=\beta,\quad\alpha=\varphi-1<0.$$
> Le coefficient $\alpha$ est la **vitesse de rappel** : une fraction $|\alpha|=1-\varphi$ de l'écart à l'équilibre se résorbe à chaque période. Ici, on s'attend à $\alpha=-0{,}4$ et $\gamma=1{,}5$.

```python hide
ecart = (y_coint - reg.params[1] * x - reg.params[0])[:-1]            # écart à l'équilibre à la date t-1
dy, dx = np.diff(y_coint), np.diff(x)
ecm = sm.OLS(dy, sm.add_constant(np.column_stack([ecart, dx]))).fit()
print(pd.DataFrame({"estimation": ecm.params[1:], "erreur type": ecm.bse[1:], "théorie": [0.6 - 1, 1.5]},
                   index=["alpha (rappel)", "gamma (effet immédiat)"]).round(3).to_string())
```
<!--sortie-->
```text
                        estimation  erreur type  théorie
alpha (rappel)              -0.417        0.068     -0.4
gamma (effet immédiat)       1.524        0.040      1.5
```

Les estimations sont proches de la théorie ($\hat\alpha\approx-0{,}42$ pour $-0{,}4$ ; $\hat\gamma\approx1{,}52$ pour $1{,}5$) : environ 40 % de l'écart entre le prix de vente et son équilibre se résorbent chaque période, et une hausse immédiate du coût se répercute presque un pour un (à 1,5) sur le prix.

### 4.4.3 Quand la variabilité change : le modèle GARCH

Les modèles précédents supposent que les chocs $\varepsilon_t$ ont une **variance constante**. Certaines séries violent cette hypothèse de façon flagrante : en finance, les rendements calmes alternent avec des périodes agitées (**clusters de volatilité**). C'est le cas, par exemple, d'un taux de change qui préoccupe la gérante quand elle paie un fournisseur étranger : la variation quotidienne du taux est difficile à prévoir **en moyenne**, mais ses variations *absolues* se regroupent.

> 🧭 **Les données de cette sous-section sont simulées** : un jeu de 1 500 « rendements quotidiens » (en %) tiré d'un modèle GARCH(1,1) à paramètres connus (graine 41). Nous n'avons pas de série réelle de taux de change hors ligne ; ce n'est donc **pas** un historique réel.

Le modèle **GARCH(1,1)** (Bollerslev, 1986) écrit le rendement $r_t=\mu+\varepsilon_t$, avec $\varepsilon_t=\sigma_tz_t$ ($z_t$ de loi $\mathcal N(0,1)$) et une variance qui **évolue** :

$$\sigma_t^2=\omega+\alpha\,\varepsilon_{t-1}^2+\beta\,\sigma_{t-1}^2.$$

Un gros choc hier ($\varepsilon_{t-1}^2$ grand) augmente la variance d'aujourd'hui (terme en $\alpha$) ; et la variance est persistante (terme en $\beta$).

> 📐 **Variance inconditionnelle.** Si $\alpha+\beta<1$, la variance moyenne à long terme existe : en prenant l'espérance de l'équation (avec $\mathbb E[\varepsilon_{t-1}^2]=\mathbb E[\sigma_{t-1}^2]=\sigma^2$), on obtient $\sigma^2=\omega+(\alpha+\beta)\sigma^2$, d'où $\sigma^2=\dfrac{\omega}{1-\alpha-\beta}$. La quantité $\alpha+\beta$ mesure la **persistance** de la volatilité.

> 💡 **Exemple à la main.** Avec $\omega=0{,}05$, $\alpha=0{,}10$, $\beta=0{,}85$ : la variance de long terme est $0{,}05/(1-0{,}95)=1$. Si hier le rendement s'est écarté de sa moyenne de $\varepsilon_{t-1}=3$ (un choc de 3 écarts-types) alors que la variance valait 1, la variance d'aujourd'hui sera $0{,}05+0{,}10\times9+0{,}85\times1=1{,}8$ : presque le double, d'un seul coup.

```python hide
omega, alpha, beta, mu = 0.05, 0.10, 0.85, 0.02
print("variance de long terme :", round(omega / (1 - alpha - beta), 3), "| variance après un choc de 3 :", round(omega + alpha * 9 + beta * 1, 3))

rng = np.random.default_rng(41)
n = 1500
sig2 = np.zeros(n)
r = np.zeros(n)
sig2[0] = omega / (1 - alpha - beta)
for t in range(n):
    if t > 0:
        sig2[t] = omega + alpha * (r[t - 1] - mu) ** 2 + beta * sig2[t - 1]
    r[t] = mu + np.sqrt(sig2[t]) * rng.normal()

print("kurtosis (excès) des rendements :", round(pd.Series(r).kurt(), 2), "(0 pour une loi normale)")
print("Ljung-Box (10 retards) sur les rendements : p =", round(float(acorr_ljungbox(r, lags=[10])["lb_pvalue"].iloc[0]), 4))
print("Ljung-Box (10 retards) sur les carrés    : p =", f"{float(acorr_ljungbox((r - r.mean()) ** 2, lags=[10])['lb_pvalue'].iloc[0]):.1e}")
print("test ARCH-LM (5 retards)                 : p =", f"{het_arch(r - r.mean(), nlags=5)[1]:.1e}")
```
<!--sortie-->
```text
variance de long terme : 1.0 | variance après un choc de 3 : 1.8
kurtosis (excès) des rendements : 0.25 (0 pour une loi normale)
Ljung-Box (10 retards) sur les rendements : p = 0.0019
Ljung-Box (10 retards) sur les carrés    : p = 4.7e-22
test ARCH-LM (5 retards)                 : p = 1.1e-08
```

Les rendements eux-mêmes n'ont, par construction, **aucune** mémoire dans leur moyenne ; leurs **carrés** (la variance) en ont beaucoup : le test de Ljung-Box appliqué aux carrés, et le test ARCH-LM (qui régresse $\varepsilon_t^2$ sur ses retards), rejettent massivement l'hypothèse de variance constante (p-valeurs de l'ordre de $10^{-22}$ et $10^{-8}$) ; l'excès de kurtosis des rendements est modeste (0,25). Remarquez que le Ljung-Box appliqué aux rendements bruts rejette *aussi* faiblement (p-valeur d'environ 0,002) alors qu'il n'y a pas de mémoire en moyenne : ce test suppose une variance constante, et il est lui-même perturbé quand elle ne l'est pas. C'est une raison de plus de tester les carrés. Ajustons le GARCH(1,1) avec la bibliothèque `arch` :

```python
from arch import arch_model
fit = arch_model(r, mean="Constant", vol="GARCH", p=1, q=1).fit(disp="off")      # r : les 1 500 rendements
```

```python hide-code
res = pd.DataFrame({"programmé": [mu, omega, alpha, beta], "estimé": fit.params.values, "erreur type": fit.std_err.values},
                   index=["mu", "omega", "alpha", "beta"])
print(res.round(3).to_string())
```
<!--sortie-->
```text
       programmé  estimé  erreur type
mu          0.02   0.010        0.024
omega       0.05   0.041        0.013
alpha       0.10   0.070        0.014
beta        0.85   0.891        0.020
```

```python hide
a_hat, b_hat, w_hat = fit.params["alpha[1]"], fit.params["beta[1]"], fit.params["omega"]
print("\npersistance alpha + beta :", round(a_hat + b_hat, 3), "(programmé 0,95) | variance de long terme estimée :", round(w_hat / (1 - a_hat - b_hat), 3), "(programmé 1)")

fv = fit.forecast(horizon=20).variance.iloc[-1].values
print("prévision de la variance aux horizons 1, 5, 10 et 20 jours :", fv[[0, 4, 9, 19]].round(3))
z = fit.resid / fit.conditional_volatility
print("diagnostic : Ljung-Box des résidus standardisés AU CARRÉ, p =", round(float(acorr_ljungbox(z ** 2, lags=[10])["lb_pvalue"].iloc[0]), 3))
```
<!--sortie-->
```text

persistance alpha + beta : 0.961 (programmé 0,95) | variance de long terme estimée : 1.054 (programmé 1)
prévision de la variance aux horizons 1, 5, 10 et 20 jours : [0.735 0.782 0.83  0.903]
diagnostic : Ljung-Box des résidus standardisés AU CARRÉ, p = 0.548
```

Les estimations se rapprochent des vraies valeurs, avec des écarts de l'ordre de une à deux erreurs types ($\alpha$ est sous-estimé de deux erreurs types environ, $\beta$ surestimé d'autant : ils jouent des rôles voisins, comme $\varphi$ et $\theta$ en 4.2.3, et leurs erreurs se compensent). C'est la **persistance** $\alpha+\beta$ (0,961 pour 0,95) qui est bien estimée. Après ajustement, les résidus standardisés au carré n'ont plus de mémoire : le modèle a absorbé le regroupement de volatilité. La prévision de la variance **remonte lentement vers sa valeur de long terme** (d'environ 0,74 à un jour à 0,90 à vingt jours, pour une cible de 1,05) : comme la prévision d'un AR(1) (4.3.1) qui revient vers sa moyenne, mais lentement, car la persistance est proche de 1.

```python hide
fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 5.4), sharex=True)
ax1.plot(r, color=BLEU, lw=0.7)
ax1.set_ylabel("rendement (%)")
ax2.plot(np.sqrt(sig2), color="#898781", lw=1.6, label="volatilité programmée")
ax2.plot(fit.conditional_volatility, color=ORANGE, lw=1.2, label="volatilité estimée par le GARCH")
ax2.set_ylabel("écart-type conditionnel")
ax2.set_xlabel("jour")
ax2.legend(loc="upper right", fontsize=8)
for ax in (ax1, ax2):
    ax.grid(True, color="#e1e0d9", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-garch.png", bbox_inches="tight")
```

![Rendements simulés (en haut), avec des périodes calmes et agitées, et volatilité conditionnelle (en bas) : la volatilité programmée (gris) et celle estimée par le GARCH (orange) se superposent presque.](figures/ch04-garch.png)

> ⚠️ **Ce que le GARCH modélise, et ce qu'il ne modélise pas.** Il prévoit la **variance** (donc l'incertitude, les intervalles de prévision, le risque), pas le niveau. Il est fondamental en gestion du risque financier (le volume V y reviendra). Sa validité repose sur l'hypothèse de loi (ici normale) pour les $z_t$ ; sur des données réelles, les queues sont souvent plus épaisses, et on utilise une loi de Student.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercices 4.11 et 4.12.

> ✅ **À retenir.**
> - Un **VAR($p$)** régresse chaque série sur les retards de **toutes** les séries ; il est stationnaire si les valeurs propres de la matrice (compagne) sont de module $<1$ ; les **réponses impulsionnelles** suivent la propagation d'un choc.
> - La **causalité de Granger** est une précédence prédictive, **pas** une causalité.
> - La **régression entre séries non stationnaires est trompeuse** : environ quatre fois sur cinq, deux marches aléatoires indépendantes paraissent « significativement » liées. Méfiance quand $R^2>$ Durbin-Watson.
> - **Cointégration** : deux séries intégrées dont une combinaison est stationnaire ; test d'Engle-Granger ; le **modèle à correction d'erreur** a pour coefficient de rappel $\alpha=\varphi-1$.
> - **GARCH(1,1)** : $\sigma_t^2=\omega+\alpha\varepsilon_{t-1}^2+\beta\sigma_{t-1}^2$ ; variance de long terme $\omega/(1-\alpha-\beta)$ ; il modélise la volatilité qui se regroupe. Les rendements ont peu de mémoire, leurs **carrés** beaucoup.
