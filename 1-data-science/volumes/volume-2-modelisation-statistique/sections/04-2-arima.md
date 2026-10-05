## 4.2 Modèles ARIMA et saisonniers

> 💡 **Intuition.** Une série temporelle, c'est un enchaînement : ce qui se passe aujourd'hui dépend un peu de ce qui s'est passé hier, et un peu des **surprises** récentes. Les modèles ARIMA formalisent ces deux idées avec deux briques. La brique **AR** (*autorégressive*) dit : « la valeur d'aujourd'hui est un écho de celle d'hier ». La brique **MA** (*moyenne mobile*, *moving average*) dit : « la valeur d'aujourd'hui garde la trace des chocs d'hier ». On les assemble, on ajoute une différenciation (le **I** de *integrated*) et une version saisonnière, et on obtient la famille la plus utilisée de la prévision statistique.

Nous partons des briques sur des séries **simulées**, où l'on connaît la vérité, pour comprendre ce que chaque modèle fabrique et comment le reconnaître. Puis nous les appliquerons aux ventes de la boutique.

### 4.2.1 Les deux briques : AR et MA

Dans toute la suite, $\varepsilon_t$ désigne un **bruit blanc** (4.1.5), les « surprises » du mois : des chocs indépendants, centrés, de variance $\sigma^2$.

- **AR(1)** : $\;Y_t=\varphi\,Y_{t-1}+\varepsilon_t$. La valeur du jour est une fraction $\varphi$ de celle de la veille, plus une surprise. Si $\varphi=0{,}7$, 70 % du niveau d'hier « survit » aujourd'hui.
- **AR($p$)** : $\;Y_t=\varphi_1Y_{t-1}+\dots+\varphi_pY_{t-p}+\varepsilon_t$ (une régression sur ses $p$ propres valeurs passées).
- **MA(1)** : $\;Y_t=\varepsilon_t+\theta\,\varepsilon_{t-1}$. La valeur du jour est la surprise du jour plus une fraction $\theta$ de la surprise d'hier. Un choc a donc un effet qui dure **exactement un pas**, puis disparaît.
- **MA($q$)** : $\;Y_t=\varepsilon_t+\theta_1\varepsilon_{t-1}+\dots+\theta_q\varepsilon_{t-q}$.

> 💡 **Deux mémoires différentes.** Dans un AR, un choc se **propage indéfiniment** en s'estompant (hier m'influence, qui a influencé avant-hier, etc.). Dans un MA($q$), un choc a un effet **limité** à $q$ pas. Pensez à un AR comme à une cloche qui résonne, et à un MA comme à un coup de tampon qui laisse une trace de durée fixe.

Comment reconnaître l'un ou l'autre sur des données ? Grâce à leurs **signatures** dans l'autocorrélation (ACF) et l'autocorrélation partielle (PACF) de 4.1.4 :

| Modèle | ACF | PACF |
|---|---|---|
| AR($p$) | décroît progressivement (géométriquement) | **s'annule après le décalage $p$** |
| MA($q$) | **s'annule après le décalage $q$** | décroît progressivement |
| ARMA($p,q$) | décroît progressivement | décroît progressivement |

Voici ces signatures pour trois modèles : AR(1) avec $\varphi=0{,}7$, AR(2) avec $\varphi_1=0{,}5$ et $\varphi_2=0{,}3$, MA(1) avec $\theta=0{,}7$. Les barres sont les autocorrélations **théoriques** du modèle ; les points rouges sont celles d'une trajectoire simulée de 500 points.

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
from statsmodels.tsa.arima_process import ArmaProcess, arma_acf, arma_pacf
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.statespace.sarimax import SARIMAX
from statsmodels.tsa.stattools import acf, pacf
from statsmodels.stats.diagnostic import acorr_ljungbox

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
modeles_sim = {"AR(1), phi = 0,7": ([1, -0.7], [1]),
               "AR(2), phi = (0,5 ; 0,3)": ([1, -0.5, -0.3], [1]),
               "MA(1), theta = 0,7": ([1], [1, 0.7])}      # convention de statsmodels : polynômes en B, AR avec signe moins

fig, axes = plt.subplots(2, 3, figsize=(11, 5.2), sharey=True)
for j, (nom, (ar, ma)) in enumerate(modeles_sim.items()):
    x = ArmaProcess(ar, ma).generate_sample(500, distrvs=np.random.default_rng(10 + j).standard_normal)
    for i, (theo, emp, titre, c) in enumerate([(arma_acf(ar, ma, 13), acf(x, nlags=12, fft=False), "ACF", BLEU),
                                                (arma_pacf(ar, ma, 13), pacf(x, nlags=12, method="ols"), "PACF", ORANGE)]):
        ax = axes[i, j]
        ax.vlines(np.arange(13), 0, theo, color=c, lw=2, alpha=0.55)
        ax.plot(np.arange(13), emp, "o", color=ROUGE, ms=3.5)
        ax.axhline(0, color="#898781", lw=0.8)
        ax.axhspan(-1.96 / np.sqrt(500), 1.96 / np.sqrt(500), color=c, alpha=0.10, lw=0)
        ax.set_title(f"{titre} - {nom}", fontsize=9.5)
        if i == 1:
            ax.set_xlabel("décalage")
plt.tight_layout()
plt.savefig("figures/ch04-signatures.png", bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Signatures théoriques (barres) et empiriques (points rouges, 500 observations simulées) : l'AR(1) a une ACF qui décroît et une PACF qui s'arrête au décalage 1 ; l'AR(2) a une PACF qui s'arrête au décalage 2 ; le MA(1) a une ACF qui s'arrête au décalage 1 et une PACF qui décroît.](figures/ch04-signatures.png)

Les signatures du tableau apparaissent nettement : la PACF de l'AR(1) n'a qu'une barre, celle de l'AR(2) en a deux, et l'ACF du MA(1) n'en a qu'une. Retenez cette figure : **c'est l'outil d'identification des modèles** que nous utiliserons en 4.2.4.

### 4.2.2 L'AR(1) et le MA(1) en profondeur

#### L'AR(1) : stationnarité, variance, autocorrélations

> 📐 **Proposition.** Soit $Y_t=\varphi Y_{t-1}+\varepsilon_t$ avec $|\varphi|<1$. Alors la série admet la représentation $Y_t=\sum_{j=0}^{\infty}\varphi^j\varepsilon_{t-j}$, elle est stationnaire, de moyenne $0$ et de variance $\gamma(0)=\dfrac{\sigma^2}{1-\varphi^2}$, et son autocorrélation est $\rho(k)=\varphi^{k}$.
>
> **Démonstration.** En remplaçant $Y_{t-1}$ par $\varphi Y_{t-2}+\varepsilon_{t-1}$, puis $Y_{t-2}$, etc., on obtient $Y_t=\varepsilon_t+\varphi\varepsilon_{t-1}+\varphi^2\varepsilon_{t-2}+\dots$. La série $\sum\varphi^{2j}$ converge si et seulement si $|\varphi|<1$, vers $1/(1-\varphi^2)$. Les $\varepsilon$ étant non corrélés, $\operatorname{Var}(Y_t)=\sigma^2\sum_j\varphi^{2j}=\sigma^2/(1-\varphi^2)$, indépendant de $t$ ; la moyenne est nulle. Pour l'autocovariance, on multiplie l'équation par $Y_{t-k}$ ($k\ge1$) et on prend l'espérance : $\gamma(k)=\varphi\,\gamma(k-1)$ (car $\varepsilon_t$ est non corrélé avec $Y_{t-k}$). Donc $\gamma(k)=\varphi^k\gamma(0)$ et $\rho(k)=\varphi^k$. $\blacksquare$
>
> Si $|\varphi|\ge1$, la somme diverge : la série **n'est pas stationnaire** (pour $\varphi=1$, c'est la marche aléatoire de 4.1.3 ; pour $|\varphi|>1$, elle explose).

> 💡 **Exemple à la main.** Avec $\varphi=0{,}5$ et $\sigma=1$ : $\gamma(0)=1/(1-0{,}25)=1{,}333$ ; $\rho(1)=0{,}5$, $\rho(2)=0{,}25$, $\rho(3)=0{,}125$. La mémoire est divisée par deux à chaque pas, et un choc d'il y a trois mois n'a plus que 12,5 % d'influence.

```python hide
ar, ma = [1, -0.5], [1]
print("autocorrélations théoriques de l'AR(1), phi = 0,5 :", arma_acf(ar, ma, 4).round(4))
x = ArmaProcess(ar, ma).generate_sample(200000, distrvs=np.random.default_rng(3).standard_normal)
print("variance : théorie", round(1 / (1 - 0.25), 3), "| simulation", round(x.var(), 3))
print("autocorrélations simulées (décalages 1 à 3) :", np.round([np.corrcoef(x[:-k], x[k:])[0, 1] for k in (1, 2, 3)], 3))
```
<!--sortie-->
```text
autocorrélations théoriques de l'AR(1), phi = 0,5 : [1.    0.5   0.25  0.125]
variance : théorie 1.333 | simulation 1.328
autocorrélations simulées (décalages 1 à 3) : [0.498 0.248 0.125]
```

Une simulation de 200 000 points le confirme : variance de 1,328 (théorie : 1,333) et autocorrélations de 0,498, 0,248 et 0,125 aux décalages 1 à 3.

Qu'est-ce que la condition $|\varphi|<1$ devient pour un AR($p$) ? On écrit l'équation avec l'**opérateur retard** $B$ (défini par $BY_t=Y_{t-1}$) : $\varphi(B)Y_t=\varepsilon_t$ avec $\varphi(z)=1-\varphi_1z-\dots-\varphi_pz^p$. La série est stationnaire si et seulement si **toutes les racines du polynôme $\varphi(z)$ sont en dehors du cercle unité** ($|z|>1$). Pour l'AR(1), l'unique racine est $z=1/\varphi$, et $|1/\varphi|>1\iff|\varphi|<1$. On retrouve la condition. Vérifions pour deux AR(2) : pour $\varphi=(0{,}5\,;\,0{,}3)$, les racines ont pour modules 2,84 et 1,17 (toutes deux supérieures à 1 : stationnaire) ; pour $\varphi=(0{,}5\,;\,0{,}6)$, elles ont pour modules 1,77 et 0,94 (**non stationnaire**).

```python hide
for nom, (phi1, phi2) in {"phi = (0,5 ; 0,3)": (0.5, 0.3), "phi = (0,5 ; 0,6)": (0.5, 0.6)}.items():
    racines = np.roots([-phi2, -phi1, 1])                   # polynôme 1 - phi1 z - phi2 z^2
    verdict = "stationnaire" if np.all(np.abs(racines) > 1) else "NON stationnaire"
    print(f"AR(2) {nom} : modules des racines = {np.abs(racines).round(3)}  ->  {verdict}")
```
<!--sortie-->
```text
AR(2) phi = (0,5 ; 0,3) : modules des racines = [2.84  1.174]  ->  stationnaire
AR(2) phi = (0,5 ; 0,6) : modules des racines = [1.773 0.94 ]  ->  NON stationnaire
```

Le second modèle a une racine de module $0{,}94<1$ : sa trajectoire diverge, même si chaque coefficient « a l'air raisonnable ».

#### Le MA(1) : autocorrélation et inversibilité

> 📐 **Proposition.** Pour $Y_t=\varepsilon_t+\theta\varepsilon_{t-1}$ : $\gamma(0)=\sigma^2(1+\theta^2)$, $\gamma(1)=\theta\sigma^2$, $\gamma(k)=0$ pour $k\ge2$. Donc $\rho(1)=\dfrac{\theta}{1+\theta^2}$ et $\rho(k)=0$ au-delà. Un MA est toujours stationnaire.
>
> **Démonstration.** $\operatorname{Var}(Y_t)=\sigma^2+\theta^2\sigma^2$. Et $\operatorname{Cov}(Y_t,Y_{t-1})=\operatorname{Cov}(\varepsilon_t+\theta\varepsilon_{t-1},\varepsilon_{t-1}+\theta\varepsilon_{t-2})=\theta\sigma^2$ (seul le terme $\theta\varepsilon_{t-1}\cdot\varepsilon_{t-1}$ survit). $\blacksquare$

Une subtilité qui surprend : **deux valeurs de $\theta$ donnent exactement la même autocorrélation**, car $\theta/(1+\theta^2)$ est inchangé si l'on remplace $\theta$ par $1/\theta$. Pour $\theta=0{,}5$ comme pour $\theta=2$, on a $\rho(1)=0{,}4$ (un calcul par programme le confirme).

```python hide
for th in (0.5, 2.0):
    print(f"theta = {th} : rho(1) = {arma_acf([1], [1, th], 3)[1]:.3f}  (formule : {th / (1 + th ** 2):.3f})")
```
<!--sortie-->
```text
theta = 0.5 : rho(1) = 0.400  (formule : 0.400)
theta = 2.0 : rho(1) = 0.400  (formule : 0.400)
```

Les données ne permettent donc pas de distinguer les deux. Par convention, on retient celui qui est **inversible** : $|\theta|<1$. Pourquoi ? Un MA(1) inversible peut se réécrire $\varepsilon_t=\sum_{j\ge0}(-\theta)^jY_{t-j}$ : on peut **reconstituer les chocs passés à partir des observations**, ce qui est indispensable pour estimer et prévoir. Si $|\theta|>1$, cette somme diverge. La condition est la même que pour l'AR, côté MA : les racines de $\theta(z)=1+\theta_1z+\dots$ doivent être hors du cercle unité.

### 4.2.3 ARMA, ARIMA et SARIMA

On assemble les briques. Avec l'opérateur retard $B$ :

- **ARMA($p,q$)** : $\varphi(B)\,Y_t=\theta(B)\,\varepsilon_t$.
- **ARIMA($p,d,q$)** : on applique d'abord $d$ différenciations : $\varphi(B)(1-B)^d\,Y_t=\theta(B)\,\varepsilon_t$. Le « I » signifie que $Y$ doit être *intégrée* $d$ fois pour revenir de la série différenciée à $Y$.
- **SARIMA($p,d,q)(P,D,Q)_s$** : on ajoute des briques et des différences **saisonnières**, de période $s$ ($s=12$ pour des données mensuelles) :
$$\varphi(B)\,\Phi(B^s)\,(1-B)^d(1-B^s)^D\,Y_t=\theta(B)\,\Theta(B^s)\,\varepsilon_t.$$

> 📐 **Le « modèle de la compagnie aérienne ».** Le SARIMA$(0,1,1)(0,1,1)_{12}$, popularisé par Box et Jenkins sur les passagers aériens, s'écrit $(1-B)(1-B^{12})Y_t=(1+\theta B)(1+\Theta B^{12})\varepsilon_t$. En développant, $Y_t-Y_{t-1}-Y_{t-12}+Y_{t-13}=\varepsilon_t+\theta\varepsilon_{t-1}+\Theta\varepsilon_{t-12}+\theta\Theta\varepsilon_{t-13}$. Le membre de gauche compare le mois courant au mois précédent, **et** compare ce changement au changement observé un an plus tôt. Avec deux paramètres seulement, ce modèle décrit une tendance, une saison qui évolue lentement, et du bruit : il est le point de départ naturel des séries mensuelles.

#### Comment estime-t-on ces modèles ?

Pour un AR(1), c'est une régression. Estimer $\varphi$ revient à régresser $y_t$ sur $y_{t-1}$ par moindres carrés (c'est la méthode des *moindres carrés conditionnels*), ce qui donne $\hat\varphi=\sum y_ty_{t-1}/\sum y_{t-1}^2$ pour une série centrée. Pour les modèles avec une partie MA, les chocs $\varepsilon_t$ ne sont pas observés, et l'on maximise la **vraisemblance gaussienne** : à chaque date, on calcule la prévision à un pas, et on suppose que l'erreur de prévision suit une loi normale ; la vraisemblance est le produit de ces densités. Le calcul récursif utilise le **filtre de Kalman**, que nous verrons en 4.5. Sur un AR(1) simulé de 300 points (vrai $\varphi=0{,}7$), les moindres carrés donnent $0{,}712$ et le maximum de vraisemblance $0{,}710$.

```python hide
x = ArmaProcess([1, -0.7], [1]).generate_sample(300, distrvs=np.random.default_rng(21).standard_normal)
phi_mco = (x[1:] * x[:-1]).sum() / (x[:-1] ** 2).sum()          # moindres carrés (série centrée en théorie)
phi_mv = ARIMA(x, order=(1, 0, 0), trend="n").fit().params[0]    # maximum de vraisemblance
print("vraie valeur : 0.7 | moindres carrés :", round(phi_mco, 4), "| maximum de vraisemblance :", round(phi_mv, 4))
```
<!--sortie-->
```text
vraie valeur : 0.7 | moindres carrés : 0.7119 | maximum de vraisemblance : 0.7097
```

Les deux estimations sont très proches l'une de l'autre (écart d'environ 0,002) et de la vraie valeur. Qu'en est-il de leur **précision** ? Un résultat classique (Kendall, 1954) dit que l'estimateur des moindres carrés d'un AR(1) est **biaisé vers zéro** : $\mathbb E[\hat\varphi]\approx\varphi-\dfrac{1+3\varphi}{n}$. Une simulation de 4 000 séries de 100 points avec $\varphi=0{,}6$ donne une moyenne des estimations de $0{,}571$ (la formule prédit $0{,}572$), avec un écart-type de $0{,}084$.

```python hide
rng = np.random.default_rng(11)
estimations = []
for _ in range(4000):
    e = rng.normal(size=150)
    s = np.zeros(150)
    for t in range(1, 150):
        s[t] = 0.6 * s[t - 1] + e[t]
    s = s[50:]                                     # on jette 50 points de « mise en route »
    d = s - s.mean()
    estimations.append((d[1:] * d[:-1]).sum() / (d[:-1] ** 2).sum())
print("phi = 0,6, n = 100 : moyenne des estimations =", round(np.mean(estimations), 4),
      "| formule 0,6 - (1 + 3 x 0,6)/100 =", round(0.6 - (1 + 3 * 0.6) / 100, 4),
      "| écart-type =", round(np.std(estimations), 3))
```
<!--sortie-->
```text
phi = 0,6, n = 100 : moyenne des estimations = 0.571 | formule 0,6 - (1 + 3 x 0,6)/100 = 0.572 | écart-type = 0.084
```

Le biais est petit (environ $-0{,}03$ pour $n=100$), mais réel : avec peu de données, un AR estimé paraît **moins persistant** qu'il ne l'est. Étudions maintenant un ARMA(1,1) ($\varphi=0{,}6$, $\theta=0{,}4$) : sur une série de 500 points, l'estimation donne $\hat\varphi=0{,}58$ (erreur type $0{,}04$) et $\hat\theta=0{,}45$ (erreur type $0{,}05$) ; sur 200 séries de 200 points, les moyennes des estimations sont $0{,}59$ et $0{,}41$, avec un écart-type de $0{,}08$ pour chacune.

```python hide
x = ArmaProcess([1, -0.6], [1, 0.4]).generate_sample(500, distrvs=np.random.default_rng(12).standard_normal)
ajust = ARIMA(x, order=(1, 0, 1), trend="n").fit()
print(pd.DataFrame({"estimation": ajust.params, "erreur type": ajust.bse}, index=["phi", "theta", "sigma2"]).round(3))
print()
essais = []
for k in range(200):
    s = ArmaProcess([1, -0.6], [1, 0.4]).generate_sample(200, distrvs=np.random.default_rng(1000 + k).standard_normal)
    essais.append(ARIMA(s, order=(1, 0, 1), trend="n").fit().params[:2])
essais = np.array(essais)
print("200 séries de 200 points : moyenne des estimations (phi, theta) =", essais.mean(0).round(3),
      "| écart-type =", essais.std(0).round(3))
```
<!--sortie-->
```text
        estimation  erreur type
phi          0.582        0.044
theta        0.447        0.053
sigma2       0.951        0.062

200 séries de 200 points : moyenne des estimations (phi, theta) = [0.591 0.408] | écart-type = [0.076 0.08 ]
```

Sur la série de 500 points, les estimations sont proches des vraies valeurs (0,6 et 0,4), à l'intérieur de leurs marges d'erreur. Sur 200 séries de 200 points, la moyenne est proche de la vérité, mais la **dispersion** est importante (de l'ordre de 0,08 pour chaque paramètre) : estimer les deux paramètres d'un ARMA est nettement plus incertain qu'estimer un AR seul, parce que $\varphi$ et $\theta$ jouent des rôles voisins.

> ⚠️ **Un piège classique : la redondance.** Un ARMA(1,1) avec $\varphi=\theta'$ (où le MA est « l'opposé » de l'AR) se simplifie : $(1-\varphi B)Y_t=(1-\varphi B)\varepsilon_t$ donne $Y_t=\varepsilon_t$. Quand les deux racines sont presque égales, les paramètres ne sont plus identifiables. Si votre modèle estime $\varphi\approx0{,}9$ et $\theta\approx-0{,}9$, il est probablement trop gros : **simplifiez**.

### 4.2.4 La méthode de Box-Jenkins appliquée aux ventes de la boutique

Box et Jenkins ont proposé un cycle en quatre temps : **(1) identifier** la structure à partir de l'ACF et de la PACF, **(2) estimer** les paramètres, **(3) diagnostiquer** les résidus, et, si tout est correct, **(4) prévoir**. Appliquons-le à notre série d'apprentissage (96 mois, en logarithme).

**Étape 1 : stationnariser.** D'après 4.1.6, la série a une tendance et une saison. Les deux différences ($d=1$ et $D=1$, $s=12$) font disparaître la tendance et la saison **stochastiques**. Regardons ce qui reste :

```python hide
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"]).set_index("mois")
v.index.freq = "MS"
y = np.log(v["ca"])
train, test = y[:"2023-12"], y["2024-01":]
X = v[["promo", "covid"]].astype(float)
Xtr = X[:"2023-12"]

def tracer_acf(ax, valeurs, n, titre, couleur=BLEU):
    k = np.arange(len(valeurs))
    ax.vlines(k, 0, valeurs, color=couleur, lw=2)
    ax.plot(k, valeurs, "o", color=couleur, ms=3.5)
    ax.axhline(0, color="#898781", lw=0.8)
    b = 1.96 / np.sqrt(n)
    ax.axhspan(-b, b, color=couleur, alpha=0.10, lw=0)
    ax.set_title(titre)
    ax.set_xlabel("décalage (mois)")
    ax.set_ylim(-1, 1)

w = train.diff().diff(12).dropna()
print("série différenciée (1 et 12) :", len(w), "observations ; bande de confiance +/-", round(1.96 / np.sqrt(len(w)), 3))
print("ACF  décalages 1 à 14 :", acf(w, nlags=14, fft=False)[1:].round(2))
print("PACF décalages 1 à 14 :", pacf(w, nlags=14, method="ols")[1:].round(2))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.4))
tracer_acf(ax1, acf(w, nlags=24, fft=False), len(w), "ACF de la série différenciée (1 et 12)")
tracer_acf(ax2, pacf(w, nlags=24, method="ols"), len(w), "PACF de la série différenciée (1 et 12)", ORANGE)
plt.tight_layout()
plt.savefig("figures/ch04-acf-diff.png", bbox_inches="tight")
```
<!--sortie-->
```text
série différenciée (1 et 12) : 83 observations ; bande de confiance +/- 0.215
ACF  décalages 1 à 14 : [-0.01 -0.12  0.   -0.23 -0.17 -0.08  0.15  0.02  0.04  0.14 -0.03 -0.43
 -0.02 -0.01]
PACF décalages 1 à 14 : [-0.01 -0.12  0.   -0.25 -0.19 -0.18  0.09 -0.08 -0.02  0.06  0.01 -0.5
 -0.02 -0.14]
```

![ACF et PACF de la série différenciée (différence première et différence saisonnière) : une barre négative nette au décalage 12 dans les deux graphiques ; les autres barres restent dans la bande ou l'effleurent.](figures/ch04-acf-diff.png)

**Lecture.** La série différenciée n'a plus de mémoire à long terme. Il reste une **seule structure nette** : une forte barre négative au décalage 12 dans l'ACF (environ $-0{,}43$) et dans la PACF (environ $-0{,}50$). Selon le tableau de 4.2.1, une ACF qui s'arrête au décalage 12 (un seul pic saisonnier) évoque un **MA saisonnier d'ordre 1** ($Q=1$). Aux décalages courts (1 à 3), rien ne dépasse la bande ; le décalage 4 l'effleure à peine (une barre sur quatorze : à ne pas sur-interpréter). La partie non saisonnière est donc modeste, peut-être nulle. On part donc du modèle de la compagnie aérienne, SARIMA$(0,1,1)(0,1,1)_{12}$, et de ses voisins.

**Étape 2 : estimer, avec des variables explicatives.** Nous savons qu'il y a eu un accident (COVID) et des promotions. Nous les ajoutons comme **variables explicatives** (*exogènes*) : le modèle devient une régression dont les erreurs suivent un SARIMA. (Nous détaillons cette idée en 4.2.5.) Ajustons une petite grille de modèles avec $d=1$, $D=1$, $p,q\in\{0,1,2\}$ et $Q\in\{0,1\}$, et comparons-les par **AIC** et **BIC** (chapitre 1, section 1.4 : ces critères mesurent l'ajustement en pénalisant la complexité ; plus petit = meilleur).

```python hide-code
import itertools

lignes = []
for p, q, Q in itertools.product((0, 1, 2), (0, 1, 2), (0, 1)):
    m = SARIMAX(train, exog=Xtr, order=(p, 1, q), seasonal_order=(0, 1, Q, 12)).fit(disp=False, maxiter=200)
    lignes.append({"p": p, "q": q, "Q": Q, "AIC": m.aic, "BIC": m.bic, "convergé": m.mle_retvals["converged"]})
grille = pd.DataFrame(lignes).sort_values("AIC").reset_index(drop=True)
print("les 8 meilleurs modèles par AIC (d = 1, D = 1, s = 12) :")
print(grille.head(8).round(1).to_string())
print()
print("tous convergés :", bool(grille["convergé"].all()), "| meilleur par BIC : (p, q, Q) =", tuple(grille.sort_values("BIC").iloc[0][["p", "q", "Q"]].astype(int)))
```
<!--sortie-->
```text
les 8 meilleurs modèles par AIC (d = 1, D = 1, s = 12) :
   p  q  Q    AIC    BIC  convergé
0  1  1  1 -176.7 -162.2      True
1  2  1  1 -175.5 -158.6      True
2  1  2  1 -175.5 -158.6      True
3  0  2  1 -173.3 -158.8      True
4  2  2  1 -172.9 -153.5      True
5  2  0  1 -166.4 -151.9      True
6  0  1  1 -165.9 -153.8      True
7  0  0  1 -164.7 -155.1      True

tous convergés : True | meilleur par BIC : (p, q, Q) = (1, 1, 1)
```

Le modèle SARIMAX$(1,1,1)(0,1,1)_{12}$ arrive en tête à la fois par l'AIC et par le BIC. Voici son ajustement (`Xtr` contient les colonnes `promo` et `covid` de la période d'apprentissage) et ses coefficients :

```python
mod_A = SARIMAX(train, exog=Xtr, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False)
print(mod_A.summary().tables[1])
```
<!--sortie-->
```text
==============================================================================
                 coef    std err          z      P>|z|      [0.025      0.975]
------------------------------------------------------------------------------
promo          0.1061      0.022      4.887      0.000       0.064       0.149
covid         -0.5371      0.037    -14.464      0.000      -0.610      -0.464
ar.L1          0.5583      0.115      4.870      0.000       0.334       0.783
ma.L1         -0.9919      0.331     -3.001      0.003      -1.640      -0.344
ma.S.L12      -0.8889      0.262     -3.389      0.001      -1.403      -0.375
sigma2         0.0047      0.002      2.383      0.017       0.001       0.009
==============================================================================
```

> ⚠️ **Les deux coefficients MA sont proches de $-1$ : un signal d'alerte.** `ma.L1` vaut environ $-0{,}99$ et `ma.S.L12` environ $-0{,}89$, avec de très grandes incertitudes (erreurs types de l'ordre de $0{,}3$). Rappelez-vous la sur-différenciation de 4.1.6 : différencier une série qui n'en avait pas besoin crée un MA dont le coefficient est $-1$. Un MA non saisonnier proche de $-1$ suggère que la **différence première** est de trop (la tendance serait **déterministe**, une droite, et non un cumul de chocs) ; un MA **saisonnier** proche de $-1$ suggère que la **différence saisonnière** l'est aussi (la saison serait **déterministe** : le même profil chaque année, fixé une fois pour toutes, et non un profil qui évolue). Le modèle a trouvé le meilleur ajustement *parmi les modèles différenciés*, mais ses propres coefficients nous disent qu'il compense une différenciation excessive. Nous allons mettre cette hypothèse à l'épreuve en 4.2.7.

### 4.2.5 Variables explicatives : la régression à erreurs ARMA

Le modèle que vient d'ajuster `SARIMAX` est une **régression à erreurs ARIMA** :

$$\log y_t=\beta_1\,\text{promo}_t+\beta_2\,\text{covid}_t+\eta_t,\qquad \eta_t\sim\text{SARIMA}(1,1,1)(0,1,1)_{12}.$$

Les variables explicatives interviennent **en niveau** (pas différenciées) et l'ARIMA décrit ce qui reste. C'est la bonne façon de combiner une régression (chapitre 1) et de la mémoire temporelle : si l'on ignorait la mémoire des erreurs, les erreurs types de la régression seraient fausses (le volume I, section 2.4, suppose l'indépendance).

Les coefficients se lisent comme des pourcentages, puisque la variable dépendante est un logarithme : un coefficient $\beta$ correspond à un facteur $e^\beta$, soit une variation de $100\,(e^\beta-1)\,\%$. Ici, la promotion correspond à $+11{,}2\ \%$ (intervalle à 95 % : de $+6{,}6$ à $+16{,}0\ \%$) et le COVID à $-41{,}6\ \%$ (de $-45{,}7$ à $-37{,}1\ \%$).

```python hide
for nom in ("promo", "covid"):
    b = mod_A.params[nom]
    lo, hi = mod_A.conf_int().loc[nom]
    print(f"{nom:6s} : coefficient = {b:+.3f}  ->  effet = {100 * (np.exp(b) - 1):+.1f} %   (IC 95 % : {100 * (np.exp(lo) - 1):+.1f} % à {100 * (np.exp(hi) - 1):+.1f} %)")
```
<!--sortie-->
```text
promo  : coefficient = +0.106  ->  effet = +11.2 %   (IC 95 % : +6.6 % à +16.0 %)
covid  : coefficient = -0.537  ->  effet = -41.6 %   (IC 95 % : -45.7 % à -37.1 %)
```

Une promotion est associée à des ventes environ 11 % plus élevées le mois où elle a lieu, et les quatre mois de COVID à des ventes environ 42 % plus basses, toutes choses égales par ailleurs. Sans ces deux variables, le modèle aurait dû « expliquer » le COVID par du bruit, ce qui aurait dégradé tous les paramètres : l'AIC passe de $-98{,}1$ sans variables explicatives à $-176{,}7$ avec, et l'écart-type estimé des chocs de $0{,}107$ à $0{,}068$.

```python hide
sans = SARIMAX(train, order=(1, 1, 1), seasonal_order=(0, 1, 1, 12)).fit(disp=False)
print("AIC sans variables explicatives :", round(sans.aic, 1), "| avec promo et COVID :", round(mod_A.aic, 1))
print("écart-type estimé des chocs (sigma) : sans =", round(np.sqrt(sans.params['sigma2']), 3), "| avec =", round(np.sqrt(mod_A.params['sigma2']), 3))
```
<!--sortie-->
```text
AIC sans variables explicatives : -98.1 | avec promo et COVID : -176.7
écart-type estimé des chocs (sigma) : sans = 0.107 | avec = 0.068
```

> 💡 **Les variables explicatives doivent être connues pour prévoir.** Pour prévoir 2026, il faudra fournir la valeur future de `promo` (les promotions sont décidées par la gérante : on peut les supposer connues ou raisonner en scénarios) et de `covid` (nulle). Une variable explicative inconnue dans le futur est inutilisable telle quelle : il faudrait la prévoir elle-même.

### 4.2.6 Le diagnostic des résidus

Un modèle n'est pas fini quand il est ajusté : il faut vérifier qu'il a **tout expliqué**, c'est-à-dire que ses résidus ressemblent à un bruit blanc gaussien. On regarde quatre choses : les résidus dans le temps (pas de structure, variance stable), l'ACF des résidus (pas de barre hors bande), la normalité (histogramme et QQ-plot) et le test de Ljung-Box. Les premiers résidus d'un SARIMA avec différences (ici 13) n'ont pas de sens (ils servent à initialiser le calcul) : on les ignore.

```python hide
res = mod_A.resid.iloc[13:]                       # on ignore les 13 premiers (initialisation des différences)
sig = res.std()
fig, axes = plt.subplots(2, 2, figsize=(11, 6))
axes[0, 0].plot(res.index, res / sig, color=BLEU, lw=1.2)
axes[0, 0].axhline(0, color="#898781", lw=0.8)
axes[0, 0].set_title("Résidus standardisés")
axes[0, 1].hist(res / sig, bins=18, density=True, color=BLEU, alpha=0.7)
xs = np.linspace(-4, 4, 200)
axes[0, 1].plot(xs, stats.norm.pdf(xs), color=ORANGE, lw=2)
axes[0, 1].set_title("Histogramme et loi normale")
sm.qqplot(res / sig, line="45", ax=axes[1, 0], markerfacecolor=BLEU, markeredgecolor=BLEU, ms=4)
axes[1, 0].set_title("QQ-plot")
axes[1, 0].set_xlabel("quantiles théoriques")
axes[1, 0].set_ylabel("quantiles observés")
tracer_acf(axes[1, 1], acf(res, nlags=24, fft=False), len(res), "ACF des résidus", ORANGE)
plt.tight_layout()
plt.savefig("figures/ch04-diagnostics.png", bbox_inches="tight")

nb_param = 3                                     # phi, theta, Theta : les paramètres AR/MA estimés
lb = acorr_ljungbox(res, lags=[12, 24], model_df=nb_param)
print("Ljung-Box sur les résidus (degrés de liberté réduits de", nb_param, ") :")
print(lb.round(3).to_string())
print("Shapiro-Wilk (normalité) : p =", round(stats.shapiro(res).pvalue, 3))
print("plus grand résidu standardisé en valeur absolue :", round((res / sig).abs().max(), 2), "le", (res / sig).abs().idxmax().strftime("%Y-%m"))
```
<!--sortie-->
```text
Ljung-Box sur les résidus (degrés de liberté réduits de 3 ) :
    lb_stat  lb_pvalue
12    8.923      0.444
24   22.329      0.381
Shapiro-Wilk (normalité) : p = 0.334
plus grand résidu standardisé en valeur absolue : 2.37 le 2017-12
```

![Diagnostic des résidus du SARIMAX(1,1,1)(0,1,1)12 : résidus standardisés sans structure, histogramme proche de la loi normale, QQ-plot proche de la droite, ACF sans barre hors bande.](figures/ch04-diagnostics.png)

Les résidus ne montrent pas de structure : l'ACF reste dans la bande, les p-valeurs de Ljung-Box sont grandes ($0{,}44$ et $0{,}38$ aux décalages 12 et 24 : on ne rejette pas « bruit blanc »), la normalité n'est pas rejetée (Shapiro-Wilk : $p=0{,}33$). Le modèle a donc **capté l'essentiel de la dynamique linéaire** de la série d'apprentissage.

> ⚠️ **Un bon diagnostic ne prouve pas un bon modèle.** Des résidus blancs montrent qu'il ne reste pas d'**autocorrélation exploitable**, pas que le modèle **prévoira bien** : un modèle trop flexible peut avoir des résidus parfaits sur l'apprentissage et prévoir mal (surajustement). Seule la prévision hors échantillon (4.3) le dira.

### 4.2.7 Deux visions du monde : saison stochastique ou déterministe ?

Nous avons soupçonné plusieurs fois que la tendance et la saison sont **déterministes** (4.1.6 : tests ambigus ; 4.2.4 : deux coefficients MA proches de $-1$). Construisons deux modèles alternatifs, qui **différencient moins** :

- **Modèle B** : SARIMAX$(1,0,0)(0,1,1)_{12}$ avec tendance linéaire (`trend="ct"`) : on garde la différence saisonnière mais on modélise la tendance par une droite.
- **Modèle C** : régression sur **tendance linéaire + 11 indicatrices de mois + promo + COVID**, avec des **erreurs AR(1)**. Ici, la saison est un profil fixe (11 coefficients) et aucune différenciation n'est appliquée.

```python hide-code
mois = pd.get_dummies(pd.Series(v.index.month, index=v.index).astype(str).str.zfill(2), prefix="m", drop_first=True, dtype=float)
XX = pd.concat([pd.Series(1.0, index=v.index, name="const"),
                pd.Series(np.arange(len(v), dtype=float), index=v.index, name="t"), mois, X], axis=1)

mod_B = SARIMAX(train, exog=Xtr, order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="ct").fit(disp=False, maxiter=300)
mod_C = ARIMA(train, exog=XX[:"2023-12"], order=(1, 0, 0), trend="n").fit()

tableau = pd.DataFrame({
    "modèle A : SARIMAX(1,1,1)(0,1,1)": [mod_A.params["promo"], mod_A.params["covid"]],
    "modèle B : (1,0,0)(0,1,1) + tendance": [mod_B.params["promo"], mod_B.params["covid"]],
    "modèle C : régression + AR(1)": [mod_C.params["promo"], mod_C.params["covid"]]}, index=["promo", "covid"])
print(tableau.round(3).T.to_string())
print()
print("modèle C : pente de la tendance =", round(mod_C.params["t"], 4), "par mois, soit", round(100 * (np.exp(12 * mod_C.params["t"]) - 1), 1), "% par an ;",
      "AR(1) : phi =", round(mod_C.params["ar.L1"], 3), "| sigma =", round(np.sqrt(mod_C.params["sigma2"]), 3))
print("AIC : A =", round(mod_A.aic, 1), "| B =", round(mod_B.aic, 1), "| C =", round(mod_C.aic, 1))
```
<!--sortie-->
```text
                                      promo  covid
modèle A : SARIMAX(1,1,1)(0,1,1)      0.106 -0.537
modèle B : (1,0,0)(0,1,1) + tendance  0.100 -0.506
modèle C : régression + AR(1)         0.106 -0.541

modèle C : pente de la tendance = 0.0077 par mois, soit 9.7 % par an ; AR(1) : phi = 0.539 | sigma = 0.06
AIC : A = -176.7 | B = -174.3 | C = -232.5
```

Les trois modèles s'accordent sur les effets de la promotion (coefficient d'environ 0,10 à 0,11, soit +10 à +11 %) et du COVID (coefficient d'environ −0,51 à −0,54, soit −40 à −42 %). Ils diffèrent sur la **dynamique**. Le modèle C décrit une croissance régulière de 0,0077 par mois (9,7 % par an), un AR(1) modéré ($\varphi=0{,}54$), et il obtient l'AIC le plus bas de loin ($-232{,}5$, contre $-176{,}7$ et $-174{,}3$). Attention : **cette comparaison d'AIC n'a pas de sens**.

> ⚠️ **On ne compare pas des AIC entre modèles de différenciations différentes.** L'AIC est calculé à partir de la vraisemblance des **données modélisées**. Le modèle A modélise une série différenciée deux fois, le modèle B une série différenciée une fois, le modèle C la série non différenciée : les vraisemblances portent sur des objets différents, et leurs valeurs ne sont pas comparables (même si le logiciel les affiche sans protester). L'AIC ne peut départager que des modèles de **même $d$ et même $D$** (comme dans la grille de 4.2.4). Pour comparer A, B et C, il n'y a **qu'un seul juge** légitime : leurs **prévisions** sur des données qu'ils n'ont pas vues. C'est l'objet de 4.3.

### 4.2.8 Le même travail en R : `auto.arima`

Les statisticiens utilisent aussi R, où le paquet `forecast` propose `auto.arima`, qui automatise la grille de 4.2.4 (et choisit même les différences par des tests de racine unitaire). Voici ce que donne la fonction sur la même série d'apprentissage, avec les mêmes variables explicatives :

```r
suppressPackageStartupMessages(library(forecast))
d <- read.csv("donnees/ventes_mensuelles.csv")
d <- d[1:96, ]                                       # les 96 mois d'apprentissage
y <- ts(log(d$ca), start = c(2016, 1), frequency = 12)
xreg <- as.matrix(d[, c("promo", "covid")])
modele <- auto.arima(y, xreg = xreg, seasonal = TRUE, ic = "aicc")
print(modele)
```
<!--sortie-->
```text
Series: y 
Regression with ARIMA(0,0,1)(0,1,1)[12] errors 

Coefficients:
         ma1     sma1   drift   promo    covid
      0.4942  -0.8836  0.0078  0.0976  -0.5425
s.e.  0.0798   0.2637  0.0004  0.0210   0.0459

sigma^2 = 0.005107:  log likelihood = 96.73
AIC=-181.47   AICc=-180.38   BIC=-166.88
```

R a retenu un **ARIMA$(0,0,1)(0,1,1)_{12}$ avec une dérive** (une tendance linéaire, `drift`) : pas de différence première, une différence saisonnière, un MA(1) de coefficient d'environ 0,49 et un MA saisonnier d'environ $-0{,}88$. Les effets estimés sont voisins des nôtres (promo : $0{,}098$ ; COVID : $-0{,}54$). Ce choix automatique, fondé sur des tests de racine unitaire pour $d$ et $D$, **va dans le même sens que nos soupçons** : la tendance se modélise bien par une dérive déterministe, sans différence première. Il diffère de la grille de 4.2.4, où nous avions *imposé* $d=1$ ; `auto.arima` utilise de plus l'AICc (une version de l'AIC corrigée pour les petits échantillons). Ce n'est pas une contradiction, mais un rappel : **la sélection automatique n'est pas une vérité**, seulement un point de départ à confronter au diagnostic et à la prévision.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercices 4.3, 4.4 et 4.8.

> ✅ **À retenir.**
> - **AR** : la valeur d'aujourd'hui est un écho de ses propres valeurs passées ; **MA** : elle garde la trace des chocs récents. Signatures : un AR($p$) a une PACF qui s'arrête à $p$, un MA($q$) une ACF qui s'arrête à $q$.
> - **AR(1) stationnaire $\iff|\varphi|<1$**, avec $\gamma(0)=\sigma^2/(1-\varphi^2)$ et $\rho(k)=\varphi^k$. **MA inversible $\iff|\theta|<1$** ; deux valeurs $\theta$ et $1/\theta$ ont la même ACF. Pour un AR($p$) ou MA($q$), les racines du polynôme doivent être hors du cercle unité.
> - **SARIMA$(p,d,q)(P,D,Q)_s$** : $\varphi(B)\Phi(B^s)(1-B)^d(1-B^s)^DY_t=\theta(B)\Theta(B^s)\varepsilon_t$. L'estimation se fait par maximum de vraisemblance ; l'estimateur d'un AR(1) est biaisé vers zéro d'environ $(1+3\varphi)/n$.
> - **Box-Jenkins** : stationnariser, identifier avec ACF/PACF, estimer plusieurs candidats, comparer par AIC/BIC (**à même $d$ et $D$ seulement**), diagnostiquer les résidus (Ljung-Box avec degrés de liberté réduits du nombre de paramètres AR et MA).
> - Une **régression à erreurs ARIMA** (`SARIMAX` avec variables explicatives) combine les effets de variables connues et la mémoire des erreurs ; les coefficients en log se lisent en pourcentages.
> - Un coefficient MA proche de $-1$ signale souvent une **sur-différenciation** : ici, une saison qui pourrait être déterministe.
> - Des résidus blancs ne garantissent pas de bonnes prévisions. **Le juge de paix est la prévision hors échantillon** (4.3).
