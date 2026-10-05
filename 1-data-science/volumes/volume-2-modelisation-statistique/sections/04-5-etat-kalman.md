## 4.5 ➕ Pour aller plus loin : modèles d'espace d'états et filtre de Kalman

> 🧭 **Section optionnelle.** Elle ne demande aucun prérequis nouveau (seulement le chapitre 1 de ce volume et la section 4.2), mais elle est plus abstraite que le reste du chapitre. Elle vaut le détour : les modèles ARIMA de 4.2 sont **un cas particulier** de ce cadre, et le **filtre de Kalman** que vous allez construire est l'algorithme qui a calculé, en coulisses, toutes les vraisemblances de `SARIMAX`.

### 4.5.1 L'idée : un état caché, des observations bruitées

La gérante voudrait connaître le **niveau réel** de ses ventes, c'est-à-dire ce que serait son chiffre d'affaires sans les accidents du mois (une grosse commande, un jour de pluie). Elle n'observe que le chiffre d'affaires du mois, qui est **le niveau réel plus du bruit**. Le niveau réel, lui, évolue lentement. C'est un problème à **deux niveaux** :

- une **équation d'observation** : ce que l'on mesure, $y_t=\mu_t+\varepsilon_t$, avec $\varepsilon_t\sim\mathcal N(0,\sigma_\varepsilon^2)$ ;
- une **équation d'état** : comment l'état caché évolue, $\mu_{t+1}=\mu_t+\eta_t$, avec $\eta_t\sim\mathcal N(0,\sigma_\eta^2)$.

C'est le **modèle de niveau local** (*local level*). Le niveau $\mu_t$ est une marche aléatoire (il dérive sans retour), que l'on n'observe qu'à travers le bruit $\varepsilon_t$. Tout le problème est de **reconstituer** $\mu_t$ à partir des $y_t$ : c'est le rôle du **filtre de Kalman**. L'idée se généralise à un état de plusieurs composantes (niveau, pente, saison, régression), et à des observations manquantes ; nous verrons les deux.

### 4.5.2 Le filtre de Kalman, à la main

À chaque date, le filtre maintient une **croyance** sur l'état : une loi normale $\mathcal N(a,P)$ dont $a$ est la meilleure estimation et $P$ l'incertitude. Il alterne deux gestes.

1. **Prédiction.** Entre deux dates, le niveau dérive : l'estimation ne bouge pas ($a_{t+1|t}=a_{t|t}$) mais l'incertitude grandit : $P_{t+1|t}=P_{t|t}+\sigma_\eta^2$.
2. **Mise à jour.** On observe $y_t$. L'**innovation** $v_t=y_t-a_{t|t-1}$ est la surprise (ce que l'on n'avait pas prévu). On corrige l'estimation d'une fraction $K_t$ de cette surprise :
$$a_{t|t}=a_{t|t-1}+K_t\,v_t,\qquad K_t=\frac{P_{t|t-1}}{P_{t|t-1}+\sigma_\varepsilon^2},\qquad P_{t|t}=(1-K_t)\,P_{t|t-1}.$$

Le coefficient $K_t$ s'appelle le **gain de Kalman**. Il vaut entre 0 et 1 et arbitre entre deux sources d'information : l'ancienne croyance (si elle est incertaine, $P$ grand, $K$ proche de 1 : on se fie à la mesure) et la mesure (si elle est bruyante, $\sigma_\varepsilon^2$ grand, $K$ proche de 0 : on se fie à l'ancienne croyance).

> 📐 **D'où vient la formule ?** C'est le calcul bayésien le plus simple : un a priori normal $\mathcal N(a,P)$ sur $\mu$, une mesure $y=\mu+\varepsilon$ avec $\varepsilon\sim\mathcal N(0,\sigma^2)$. La loi *a posteriori* de $\mu$ est normale, de précision (inverse de la variance) **égale à la somme des précisions** : $\dfrac1{P_{\text{post}}}=\dfrac1P+\dfrac1{\sigma^2}$, d'où $P_{\text{post}}=\dfrac{P\sigma^2}{P+\sigma^2}=(1-K)P$ ; et de moyenne égale à la **moyenne des deux informations pondérée par leur précision** : $a_{\text{post}}=\dfrac{a/P+y/\sigma^2}{1/P+1/\sigma^2}=a+K(y-a)$. Le filtre de Kalman est donc une mise à jour bayésienne répétée, avec une étape de « vieillissement » entre deux (nous reverrons ce principe au chapitre 6).

> 💡 **Exemple à la main.** Prenons $\sigma_\varepsilon^2=4$, $\sigma_\eta^2=1$, et une croyance initiale $\mathcal N(100,\,5)$ sur le niveau avant la première mesure. On observe $y_1=103$, $y_2=101$, $y_3=106$.
>
> **Date 1.** $a_{1|0}=100$, $P_{1|0}=5$. Variance de l'innovation : $F_1=P+\sigma_\varepsilon^2=9$. Gain $K_1=5/9=0{,}5556$. Surprise $v_1=103-100=3$. Donc $a_{1|1}=100+0{,}5556\times3=101{,}667$ et $P_{1|1}=5\times(1-0{,}5556)=2{,}222$.
> **Date 2.** Prédiction : $a_{2|1}=101{,}667$, $P_{2|1}=2{,}222+1=3{,}222$. $F_2=7{,}222$, $K_2=3{,}222/7{,}222=0{,}4462$. Surprise $v_2=101-101{,}667=-0{,}667$. Donc $a_{2|2}=101{,}667+0{,}4462\times(-0{,}667)=101{,}369$ et $P_{2|2}=3{,}222\times(1-0{,}4462)=1{,}785$.
> **Date 3.** $P_{3|2}=2{,}785$, $F_3=6{,}785$, $K_3=0{,}4104$, $v_3=106-101{,}369=4{,}631$, $a_{3|3}=101{,}369+0{,}4104\times4{,}631=103{,}270$, $P_{3|3}=1{,}642$.
>
> Observez deux choses : le gain **diminue** (0,56 puis 0,45 puis 0,41) à mesure que l'on en sait plus, et l'incertitude $P_{t|t}$ diminue aussi.

### 4.5.3 Le filtre de Kalman en numpy, et comparaison avec statsmodels

Le filtre complet pour le niveau local tient en une vingtaine de lignes (nous le programmons pas à pas dans l'application 4.2 du cahier). Il traite aussi les **observations manquantes** (une valeur `NaN`) : on ne fait alors **que la prédiction**, sans mise à jour, et l'incertitude grandit. À chaque étape, il cumule la **log-vraisemblance** gaussienne des innovations (c'est ce qu'optimisent les logiciels pour estimer les variances).

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.2 (le filtre de Kalman en numpy).

```python hide
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from statsmodels.tsa.statespace.structural import UnobservedComponents

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"

def kalman_niveau_local(y, s2_eps, s2_eta, a0, P0):
    """Filtre de Kalman du niveau local. (a0, P0) = croyance sur le niveau AVANT la première observation."""
    n = len(y)
    sortie = {k: np.zeros(n) for k in ["a_pred", "P_pred", "F", "K", "v", "a_filtre", "P_filtre"]}
    a, P, loglik = a0, P0, 0.0
    for t in range(n):
        sortie["a_pred"][t], sortie["P_pred"][t] = a, P
        if np.isnan(y[t]):                                    # observation manquante : pas de mise à jour
            sortie["F"][t] = sortie["K"][t] = sortie["v"][t] = np.nan
            a_f, P_f = a, P
        else:
            F = P + s2_eps                                    # variance de l'innovation
            v = y[t] - a                                      # innovation (surprise)
            K = P / F                                         # gain de Kalman
            a_f, P_f = a + K * v, P * (1 - K)
            loglik += -0.5 * (np.log(2 * np.pi * F) + v ** 2 / F)
            sortie["F"][t], sortie["K"][t], sortie["v"][t] = F, K, v
        sortie["a_filtre"][t], sortie["P_filtre"][t] = a_f, P_f
        a, P = a_f, P_f + s2_eta                              # prédiction pour la date suivante
    sortie["loglik"] = loglik
    return sortie

obs = np.array([103.0, 101.0, 106.0])
r = kalman_niveau_local(obs, s2_eps=4.0, s2_eta=1.0, a0=100.0, P0=5.0)
print(pd.DataFrame({k: r[k] for k in ["a_pred", "P_pred", "F", "K", "v", "a_filtre", "P_filtre"]}, index=[1, 2, 3]).round(4).to_string())

# la même chose avec statsmodels, avec la même croyance initiale connue
mod = UnobservedComponents(obs, level="llevel")
mod.ssm.initialize_known(np.array([100.0]), np.array([[5.0]]))
mod.ssm.loglikelihood_burn = 0                               # par défaut, statsmodels ignore le 1er terme de la vraisemblance
res_sm = mod.smooth([4.0, 1.0])                              # variances : irrégulière (4), niveau (1)
print("\nétat filtré statsmodels      :", res_sm.filtered_state[0].round(4), "| variances filtrées :", res_sm.filtered_state_cov[0, 0].round(4))
print("log-vraisemblance : numpy =", round(r["loglik"], 4), "| statsmodels =", round(res_sm.llf, 4))
```
<!--sortie-->
```text
     a_pred  P_pred       F       K       v  a_filtre  P_filtre
1  100.0000  5.0000  9.0000  0.5556  3.0000  101.6667    2.2222
2  101.6667  3.2222  7.2222  0.4462 -0.6667  101.3692    1.7846
3  101.3692  2.7846  6.7846  0.4104  4.6308  103.2698    1.6417

état filtré statsmodels      : [101.6667 101.3692 103.2698] | variances filtrées : [2.2222 1.7846 1.6417]
log-vraisemblance : numpy = -7.9124 | statsmodels = -7.9124
```

Le filtre écrit en numpy retrouve les valeurs calculées à la main (101,667 ; 101,369 ; 103,270) et celles de `statsmodels`, **à la quatrième décimale**, y compris la log-vraisemblance.

#### Estimer les variances

Dans la pratique, on ne connaît pas $\sigma_\varepsilon^2$ ni $\sigma_\eta^2$ : on les **estime par maximum de vraisemblance**. Sur un niveau local **simulé** de 200 points (variances programmées : 4 pour le bruit d'observation et 1 pour le niveau), l'estimation par maximum de vraisemblance donne $3{,}05$ (erreur type $0{,}45$) et $1{,}45$ (erreur type $0{,}38$).

```python hide
rng = np.random.default_rng(5)
n = 200
niveau = 100 + np.cumsum(rng.normal(0, 1.0, n))               # sigma_eta = 1
y_sim = niveau + rng.normal(0, 2.0, n)                        # sigma_eps = 2

mod = UnobservedComponents(y_sim, level="llevel")
ajust = mod.fit(disp=False)
print(pd.DataFrame({"programmé": [4.0, 1.0], "estimé": ajust.params, "erreur type": ajust.bse},
                   index=["variance du bruit d'observation", "variance du niveau"]).round(3).to_string())

```
<!--sortie-->
```text
                                 programmé  estimé  erreur type
variance du bruit d'observation        4.0   3.051        0.445
variance du niveau                     1.0   1.453        0.382
```

> ⚠️ **Estimer deux variances est difficile.** Les estimations sont dans la bonne région (3,05 pour 4 et 1,45 pour 1) mais avec de **grandes erreurs types** (la variance d'observation est sous-estimée d'environ deux erreurs types) : à partir de la seule série, la part du « bruit de mesure » et celle de la « vraie dérive » du niveau sont difficiles à séparer, comme $\varphi$ et $\theta$ en 4.2.3. Seul le **rapport** $q=\sigma_\eta^2/\sigma_\varepsilon^2$ gouverne le comportement du filtre (nous le voyons ci-dessous), ce qui limite l'effet de cette incertitude sur les prévisions.

### 4.5.4 Régime permanent et lissage exponentiel

Quand le filtre a tourné assez longtemps, le gain $K_t$ **se stabilise** à une valeur $K_\infty$. Calculons-la pour $\sigma_\varepsilon^2=4$ et $\sigma_\eta^2=1$ : en régime permanent, la variance prédite $p=P_{t+1|t}$ vérifie $p=\dfrac{p\,\sigma_\varepsilon^2}{p+\sigma_\varepsilon^2}+\sigma_\eta^2$. En multipliant par $p+4$ : $p(p+4)=4p+(p+4)$, soit $p^2-p-4=0$, d'où $p=\dfrac{1+\sqrt{17}}2\approx2{,}562$ et $K_\infty=\dfrac p{p+4}\approx0{,}390$.

Or, une fois $K$ constant, la mise à jour devient $a_{t|t}=a_{t-1|t-1}+K\,(y_t-a_{t-1|t-1})=K\,y_t+(1-K)\,a_{t-1|t-1}$ : exactement le **lissage exponentiel simple** de paramètre $\alpha=K_\infty$ (la moyenne mobile exponentielle bien connue des prévisionnistes). Le lissage exponentiel est donc le filtre de Kalman d'un niveau local en régime permanent. Une vérification numérique sur la série simulée le confirme.

```python hide
r = kalman_niveau_local(y_sim, 4.0, 1.0, a0=100.0, P0=25.0)
p = (1 + np.sqrt(17)) / 2
print("gain final du filtre :", round(r["K"][-1], 5), "| théorie p/(p+4) :", round(p / (p + 4), 5))

alpha = p / (p + 4)
lisse = np.zeros(n)
lisse[0] = r["a_filtre"][0]
for t in range(1, n):
    lisse[t] = alpha * y_sim[t] + (1 - alpha) * lisse[t - 1]
print("écart maximal lissage exponentiel / filtre de Kalman, après 30 pas :", f"{np.abs(lisse[30:] - r['a_filtre'][30:]).max():.1e}")
```
<!--sortie-->
```text
gain final du filtre : 0.39039 | théorie p/(p+4) : 0.39039
écart maximal lissage exponentiel / filtre de Kalman, après 30 pas : 2.2e-07
```

Le gain converge vers sa valeur théorique, et le lissage exponentiel avec $\alpha=0{,}39$ **est** le filtre de Kalman une fois le régime permanent atteint (écart de l'ordre de $10^{-7}$). Plus le niveau bouge vite par rapport au bruit ($q$ grand), plus $K_\infty$ est grand : le filtre « oublie » vite le passé.

### 4.5.5 Un modèle structurel pour les ventes de la boutique

L'intérêt des modèles d'espace d'états est de **mettre bout à bout** des composantes comprises : un niveau, une pente, une saison, des variables explicatives. C'est ce qu'on appelle un **modèle structurel**. Pour nos ventes (en logarithme, 96 mois d'apprentissage), prenons un niveau, une pente, une saison de période 12 et les variables `promo` et `covid`. Pour commencer, laissons la pente évoluer aléatoirement (le « *local linear trend* » classique) :

```python hide
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"]).set_index("mois")
v.index.freq = "MS"
y = np.log(v["ca"])
train, test = y[:"2023-12"], y["2024-01":]
X = v[["promo", "covid"]].astype(float)
Xtr, Xte = X[:"2023-12"], X["2024-01":]

mod_lt = UnobservedComponents(train, exog=Xtr, level="lltrend", seasonal=12, stochastic_seasonal=False)
fit_lt = mod_lt.fit(disp=False, maxiter=300)
print(pd.Series(fit_lt.params, index=mod_lt.param_names).round(5).to_string())
```
<!--sortie-->
```text
sigma2.irregular    0.00141
sigma2.level        0.00276
sigma2.trend        0.00000
beta.promo          0.11356
beta.covid         -0.54473
```

L'estimation donne une **variance de la pente égale à zéro** (`sigma2.trend` $=0{,}0000$ ; les autres variances valent $0{,}0014$ pour le bruit irrégulier et $0{,}0028$ pour le niveau) : les données disent que la pente est **constante**. Le modèle se simplifie alors en un niveau qui dérive à vitesse constante plus un bruit de niveau (en langage statsmodels : `level="rwdrift"`, une marche aléatoire avec dérive). Gardons ce modèle, plus simple, avec une saison **déterministe** (profil fixe) :

```python
mod_ss = UnobservedComponents(train, exog=Xtr, level="rwdrift", seasonal=12, stochastic_seasonal=False)
fit_ss = mod_ss.fit(disp=False, maxiter=300)
print(pd.Series(fit_ss.params, index=mod_ss.param_names).round(4).to_string())
```
<!--sortie-->
```text
sigma2.level    0.0054
beta.promo      0.1090
beta.covid     -0.5263
```

```python hide
prev_ss = fit_ss.get_forecast(24, exog=Xte).predicted_mean
print("\nRMSE (log) sur les 24 mois de test :", round(np.sqrt(np.mean((test - prev_ss) ** 2)), 4),
      "| biais (y - prévision) :", round(float(np.mean(test - prev_ss)), 4))
```
<!--sortie-->
```text

RMSE (log) sur les 24 mois de test : 0.0819 | biais (y - prévision) : -0.0364
```

Les variances et les effets estimés sont ci-dessus ; sur les 24 mois de test, le modèle structurel a une erreur (RMSE en logarithme) de $0{,}082$ et un biais de $-0{,}036$ : cette erreur se situe entre celle du modèle B (0,074) et celle des modèles A et C (environ 0,10). Il estime que l'effet de la promotion vaut environ $+0{,}11$ et celui du COVID environ $-0{,}53$, des valeurs voisines de celles de 4.2. Voyons les composantes que l'on peut **lire** dans ce modèle : le niveau lissé (la « vraie » tendance, débarrassée de la saison et du bruit) et le profil saisonnier.

```python hide
noms = mod_ss.state_names                                                         # noms des composantes de l'état caché
niveau_lisse = pd.Series(fit_ss.smoothed_state[noms.index("level")], index=train.index)         # composante de niveau
saison_lisse = pd.Series(fit_ss.smoothed_state[noms.index("seasonal")], index=train.index)       # composante saisonnière à la date t
print("composantes de l'état :", noms[:4], "...")
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 3.6), gridspec_kw={"width_ratios": [1.5, 1]})
ax1.plot(train.index, train, color="#c3c2b7", lw=1.2, label="log(ca) observé")
ax1.plot(niveau_lisse.index, niveau_lisse, color=VIOLET, lw=2.2, label="niveau lissé (filtre de Kalman)")
ax1.set_title("Le niveau réel, débarrassé de la saison et du bruit", fontsize=10)
ax1.legend(fontsize=8, loc="upper left")
profil = saison_lisse["2023-01":"2023-12"]
ax2.bar(range(1, 13), 100 * (np.exp(profil.values) - 1), color=AQUA)
ax2.set_xticks(range(1, 13))
ax2.set_xticklabels(["j", "f", "m", "a", "m", "j", "j", "a", "s", "o", "n", "d"])
ax2.set_title("Profil saisonnier (écart au niveau, en %)", fontsize=10)
ax2.axhline(0, color="#898781", lw=0.8)
for ax in (ax1, ax2):
    ax.grid(True, color="#e1e0d9", lw=0.6)
    ax.spines[["top", "right"]].set_visible(False)
plt.tight_layout()
plt.savefig("figures/ch04-structurel.png", bbox_inches="tight")
print("écart de décembre au niveau :", round(100 * (np.exp(profil.iloc[-1]) - 1)), "% ; de janvier :", round(100 * (np.exp(profil.iloc[0]) - 1)), "%")
```
<!--sortie-->
```text
composantes de l'état : ['level', 'trend', 'seasonal', 'seasonal.L1'] ...
écart de décembre au niveau : 59 % ; de janvier : -38 %
```

![À gauche : le logarithme du chiffre d'affaires (gris) et le niveau lissé par le filtre de Kalman (violet) qui en retire la saison et le bruit. À droite : le profil saisonnier estimé, avec le pic de décembre et le creux de janvier.](figures/ch04-structurel.png)

Le profil saisonnier estimé donne $+59\ \%$ en décembre et $-38\ \%$ en janvier par rapport au niveau.

### 4.5.6 Combler un trou : les données manquantes

Un atout décisif du filtre de Kalman est de traiter les **observations manquantes** sans bricolage : à une date sans mesure, il ne fait que prédire (l'incertitude grandit), et le **lissage** (qui utilise aussi l'avenir) reconstitue la valeur manquante avec son intervalle d'incertitude. Un cas réaliste : les registres de la gérante ont perdu les ventes de **mars à août 2022**. Nous effaçons ces six mois de la série d'apprentissage (nous connaissons les vraies valeurs, ce qui permet de vérifier), ajustons le modèle sur ce qui reste, puis **reconstituons** les mois manquants. Résultats (en logarithme du chiffre d'affaires), avec l'intervalle d'incertitude de Kalman et, pour comparer, deux méthodes sans modèle (interpolation linéaire, et « même mois l'an dernier » corrigé de la croissance annuelle) :

```python hide-code
trou = train["2022-03":"2022-08"].index
vraies = train[trou].copy()
train_trou = train.copy()
train_trou[trou] = np.nan

mod_na = UnobservedComponents(train_trou, exog=Xtr, level="rwdrift", seasonal=12, stochastic_seasonal=False)
fit_na = mod_na.fit(disp=False, maxiter=300)
lissage = fit_na.smoother_results
estim = pd.Series(lissage.smoothed_forecasts[0], index=train.index)[trou]
se = pd.Series(np.sqrt(lissage.smoothed_forecasts_error_cov[0, 0]), index=train.index)[trou]

# deux méthodes sans modèle, pour comparer : interpolation linéaire, et « même mois l'an dernier » corrigé de la croissance annuelle
lineaire = pd.Series(np.interp(np.arange(6), [-1, 6], [train["2022-02"].iloc[0], train["2022-09"].iloc[0]]), index=trou)
croissance = (train - train.shift(12))[:"2022-02"].mean()
an_dernier = pd.Series(train.shift(12)[trou].values + croissance, index=trou)

tab = pd.DataFrame({"vrai (log)": vraies, "Kalman": estim, "± 1,96 se": 1.96 * se, "interp. linéaire": lineaire, "an dernier + croiss.": an_dernier})
print(tab.round(3).to_string())
rmse = lambda a, b: np.sqrt(np.mean((a - b) ** 2))
print("\nRMSE de reconstitution (log) : Kalman =", round(rmse(vraies, estim), 3), "| interpolation linéaire =", round(rmse(vraies, lineaire), 3),
      "| an dernier corrigé =", round(rmse(vraies, an_dernier), 3))
print("mois réels dans l'intervalle à 95 % de Kalman :", int(((vraies >= estim - 1.96 * se) & (vraies <= estim + 1.96 * se)).sum()), "sur 6")
```
<!--sortie-->
```text
            vrai (log)  Kalman  ± 1,96 se  interp. linéaire  an dernier + croiss.
mois                                                                             
2022-03-01       7.400   7.371      0.142             7.127                 7.491
2022-04-01       7.553   7.442      0.183             7.182                 7.553
2022-05-01       7.711   7.550      0.201             7.238                 7.706
2022-06-01       7.667   7.661      0.201             7.293                 7.881
2022-07-01       7.803   7.722      0.183             7.349                 7.909
2022-08-01       7.717   7.674      0.142             7.404                 7.701

RMSE de reconstitution (log) : Kalman = 0.089 | interpolation linéaire = 0.383 | an dernier corrigé = 0.104
mois réels dans l'intervalle à 95 % de Kalman : 6 sur 6
```

Le filtre reconstitue les six mois avec une erreur quadratique moyenne de 0,09 en logarithme (soit 9 %) et les six vraies valeurs tombent dans son intervalle à 95 %, plus large au milieu du trou (là où l'on est le plus loin des mesures). C'est bien mieux que l'**interpolation linéaire** (0,38), qui ignore la saison et lisse une bosse qui existe réellement. La comparaison avec la méthode « l'an dernier corrigé de la croissance » (0,10) est plus serrée : elle utilise déjà la saison, mais pas l'information des mois qui entourent le trou. Les écarts du filtre ne sont pas nuls : la plus grosse erreur, en mai, est d'environ 0,16.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercice 4.10.

> ✅ **À retenir.**
> - Un **modèle d'espace d'états** distingue un **état caché** (niveau, pente, saison…) qui évolue, et des **observations bruitées**. Les ARIMA en sont un cas particulier.
> - Le **filtre de Kalman** alterne **prédiction** (l'incertitude grandit) et **mise à jour** : $a\leftarrow a+K(y-a)$, avec le **gain** $K=P/(P+\sigma_\varepsilon^2)$ qui arbitre entre ancienne croyance et mesure. C'est une mise à jour bayésienne répétée.
> - Il fournit aussi la **log-vraisemblance** des données : c'est elle qui sert à estimer les paramètres (variances), dans `SARIMAX` comme dans `UnobservedComponents`.
> - En régime permanent, le filtre d'un niveau local **est** un lissage exponentiel de paramètre $\alpha=K_\infty$.
> - Les **modèles structurels** assemblent niveau, pente, saison et variables explicatives en composantes lisibles ; ici, l'estimation de la variance de la pente à zéro a simplifié le modèle.
> - Les **observations manquantes** se traitent naturellement (prédire sans mettre à jour, puis lisser), avec une incertitude honnête.
