## 7.2 Théorie du portefeuille

La section précédente a traité le **passif** comme une donnée. Celle-ci s'occupe de l'**actif** seul : on dispose d'un capital et de quelques classes d'actifs aux rendements incertains ; comment le répartir ? Harry Markowitz a proposé en 1952 une réponse qui tient en une idée : **le risque d'un portefeuille n'est pas la moyenne des risques de ses composants**, parce que les composants ne bougent pas tous ensemble.

```python hide
c_, rend, regimes, pv_, mo_ = O.charger()
ACT = list(rend.columns)
mu, S = O.stats_annuelles(rend)
sd = np.sqrt(np.diag(S))
Corr = S / np.outer(sd, sd)
RF = 0.015
NUM("n_jours", len(rend)); NUM("n_annees", len(rend) / 252)
```
<!--sortie-->
```text
NUM n_jours 4000
NUM n_annees 15.873015873015873
```

### 7.2.1 Rendement et risque d'un portefeuille

Soit n actifs, de rendements aléatoires r₁, …, r_n, de rendements espérés μ = (μ₁, …, μ_n) et de matrice de covariance Σ (de terme général σ_ij = ρ_ij σ_i σ_j). Un portefeuille est un vecteur de poids w = (w₁, …, w_n), de somme 1. Son rendement a pour moyenne et variance
$$\mu_p=w^\top\mu,\qquad \sigma_p^2=w^\top\Sigma\,w=\sum_{i,j}w_iw_j\sigma_{ij}.$$
La moyenne est la moyenne des moyennes : rien de surprenant. La variance, elle, contient les **covariances** : c'est la clé de la diversification.

**Deux actifs, à la main.** Un actif risqué (« actions » : μ₁ = 6 %, σ₁ = 20 %) et un actif sûr (« obligations » : μ₂ = 3 %, σ₂ = 5 %), de corrélation ρ. Pour un portefeuille moitié-moitié, le rendement espéré vaut 4,5 % quel que soit ρ, et la variance
$$\sigma_p^2=0{,}25\times0{,}04+0{,}25\times0{,}0025+2\times0{,}25\times\rho\times0{,}20\times0{,}05=0{,}010625+0{,}005\,\rho .$$

| Corrélation ρ | Variance | Écart-type du portefeuille 50/50 |
|---|---|---|
| −0,5 | 0,008125 | 9,01 % |
| 0,2 | 0,011625 | 10,78 % |
| 1 | 0,015625 | 12,50 % |

À ρ = 1, l'écart-type est la moyenne des écarts-types (12,5 % = 0,5 × 20 % + 0,5 × 5 %) : aucune diversification. À ρ < 1, il est **strictement inférieur** : on obtient le même rendement espéré avec moins de risque. C'est le seul « repas gratuit » de la finance.

```python hide
for rho, var, sig in ((-0.5, 0.008125, 0.0901), (0.2, 0.011625, 0.1078), (1.0, 0.015625, 0.125)):
    v = 0.25 * 0.04 + 0.25 * 0.0025 + 2 * 0.25 * rho * 0.20 * 0.05
    assert abs(v - var) < 1e-12 and abs(np.sqrt(v) - sig) < 5e-5
```

### 7.2.2 La frontière efficiente à deux actifs

Faisons varier le poids w de l'actif risqué entre 0 et 1. Les couples (σ_p, μ_p) dessinent une courbe : la **frontière**, qui va du portefeuille 100 % sûr (w = 0) au portefeuille 100 % risqué (w = 1). Sa forme dépend de ρ : droite si ρ = 1, courbe de plus en plus creusée quand ρ diminue.

> 📐 **Le portefeuille de variance minimale à deux actifs.** Avec les poids w et 1 − w, σ_p² = w²σ₁² + (1 − w)²σ₂² + 2w(1 − w)ρσ₁σ₂. On dérive par rapport à w et on annule :
> $$w^\star=\frac{\sigma_2^2-\rho\,\sigma_1\sigma_2}{\sigma_1^2+\sigma_2^2-2\rho\,\sigma_1\sigma_2}.$$
> Le dénominateur est positif (c'est la variance de r₁ − r₂). Le numérateur est **négatif** si ρ > σ₂/σ₁, auquel cas w* < 0 : sans vente à découvert, la variance minimale s'obtient avec 0 % d'actif risqué.

Avec nos chiffres, σ₂/σ₁ = 0,25. Pour ρ = 0,2, w* = 0,0005/0,0385 ≈ 0,013 : on détient presque uniquement l'actif sûr, avec un peu d'actions qui **réduisent** le risque (la variance minimale, 4,99 %, est inférieure à 5 %). Pour ρ = 0,5, le numérateur est négatif, et le portefeuille de variance minimale est 100 % obligations (5,0 %).

```python hide
s1, s2, m1, m2 = 0.20, 0.05, 0.06, 0.03
def wstar(rho): return (s2**2 - rho * s1 * s2) / (s1**2 + s2**2 - 2 * rho * s1 * s2)
def vol2(w, rho): return np.sqrt(w**2 * s1**2 + (1 - w)**2 * s2**2 + 2 * w * (1 - w) * rho * s1 * s2)
NUM("w_star_02", wstar(0.2)); NUM("sig_min_02", 100 * vol2(wstar(0.2), 0.2)); NUM("sig_min_05", 100 * s2)
ws = np.linspace(0, 1, 101)
fig, ax = plt.subplots(figsize=(6.4, 3.8))
for rho, col in ((-0.5, AQUA), (0.2, BLEU), (1.0, ORANGE)):
    ax.plot(100 * np.array([vol2(w, rho) for w in ws]), 100 * (ws * m1 + (1 - ws) * m2), color=col, label=f"ρ = {rho}".replace(".", ","))
ax.scatter([100 * s1, 100 * s2], [100 * m1, 100 * m2], color=ENCRE2, zorder=3)
ax.annotate("actions", (100 * s1, 100 * m1), xytext=(-42, -4), textcoords="offset points")
ax.annotate("obligations", (100 * s2, 100 * m2), xytext=(6, -10), textcoords="offset points")
ax.set_xlabel("écart-type annuel (%)"); ax.set_ylabel("rendement espéré (%)"); ax.legend(loc="lower right")
style.save(fig, "ch07-frontiere-2actifs.png")
```
<!--sortie-->
```text
NUM w_star_02 0.012987012987012984
NUM sig_min_02 4.993502271458874
NUM sig_min_05 5.0
figure : ch07-frontiere-2actifs.png
```

![Frontière de deux actifs (actions : rendement espéré 6 %, écart-type 20 % ; obligations : 3 % et 5 %) pour trois corrélations. Plus la corrélation est faible, plus la courbe se creuse vers la gauche : à rendement égal, on prend moins de risque.](figures/ch07-frontiere-2actifs.png)

### 7.2.3 Cinq actifs : la frontière sur nos données

Passons aux cinq classes d'actifs de `rendements_marche.csv`. Les paramètres μ et Σ sont **estimés** sur les 4 000 jours d'historique (rendements journaliers moyens × 252, covariances × 252) : c'est une première convention, et la section 7.2.6 montrera ce qu'elle cache. Le calcul de la frontière se fait par optimisation numérique : pour chaque rendement cible, on cherche les poids de variance minimale, de somme 1, **sans vente à découvert** (poids positifs).

```python
mu, S = O.stats_annuelles(rend)            # rendements moyens et covariance, annualisés
w_min = O.min_variance(S)                  # portefeuille de variance minimale
w_tan = O.tangent(mu, S, rf=0.015)         # portefeuille de ratio de Sharpe maximal (taux sans risque 1,5 %)
```

Le **ratio de Sharpe** d'un portefeuille est (μ_p − r_f)/σ_p : le rendement en excès du taux sans risque, par unité de risque. Le portefeuille « tangent » est celui qui le maximise ; on le trouve en traçant, depuis le point (0, r_f), la droite la plus pentue qui touche la frontière.

```python hide-code
tab = pd.DataFrame({"rendement (%)": 100 * mu, "volatilité (%)": 100 * sd,
                    "poids variance min. (%)": 100 * w_min, "poids tangent (%)": 100 * w_tan}, index=ACT).round(1)
print(tab.to_string())
print()
print("portefeuille variance minimale :", round(100 * O.vol_ptf(w_min, S), 2), "% de volatilité,", round(100 * (w_min @ mu), 2), "% de rendement")
print("portefeuille tangent           :", round(100 * O.vol_ptf(w_tan, S), 2), "% de volatilité,", round(100 * (w_tan @ mu), 2), "% de rendement")
NUM("vol_min", 100 * O.vol_ptf(w_min, S)); NUM("mu_min", 100 * (w_min @ mu))
NUM("vol_tan", 100 * O.vol_ptf(w_tan, S)); NUM("mu_tan", 100 * (w_tan @ mu))
NUM("w_obl_min", 100 * w_min[2]); NUM("w_obl_tan", 100 * w_tan[2]); NUM("w_imm_tan", 100 * w_tan[3])
NUM("sharpe_tan", (w_tan @ mu - RF) / O.vol_ptf(w_tan, S))
we = np.full(5, 0.2)
NUM("vol_eq", 100 * O.vol_ptf(we, S)); NUM("mu_eq", 100 * (we @ mu)); NUM("sharpe_eq", (we @ mu - RF) / O.vol_ptf(we, S))
NUM("sharpe_obl", (mu[2] - RF) / sd[2]); NUM("sharpe_actA", (mu[0] - RF) / sd[0])
```
<!--sortie-->
```text
             rendement (%)  volatilité (%)  poids variance min. (%)  poids tangent (%)
actions_A              5.6            18.7                      1.9                3.8
actions_B              4.3            22.8                      1.2                0.0
obligations            4.0             4.4                     88.8               84.0
immobilier             5.7            13.2                      6.2               12.2
matieres              -2.9            22.0                      1.9                0.0

portefeuille variance minimale : 4.09 % de volatilité, 4.03 % de rendement
portefeuille tangent           : 4.19 % de volatilité, 4.29 % de rendement
NUM vol_min 4.089868238090334
NUM mu_min 4.026407480941068
NUM vol_tan 4.188319863573829
NUM mu_tan 4.287995591581401
NUM w_obl_min 88.84166102309152
NUM w_obl_tan 83.98434443296364
NUM w_imm_tan 12.172675863313193
NUM sharpe_tan 0.6656596636347749
NUM vol_eq 11.65583286155107
NUM mu_eq 3.3624536400000022
NUM sharpe_eq 0.1597872637779194
NUM sharpe_obl 0.5772969912342076
NUM sharpe_actA 0.22116114746699628
```

Trois constats. **(1)** Le portefeuille de variance minimale est presque entièrement en obligations (89 %) : c'est de loin l'actif le moins volatil. **(2)** Le portefeuille tangent l'est aussi (84 % d'obligations, 12 % d'immobilier) : sur cet historique, le ratio de Sharpe des obligations (0,58) écrase celui des actions (0,22 pour l'indice A). **(3)** Le portefeuille « égal pondéré » (20 % de chaque classe) a une volatilité de 11,7 % pour un rendement de 3,4 %, soit un Sharpe de 0,16 : l'optimisation fait gagner beaucoup, **sur l'historique**. La section 7.2.6 demande si ce gain survit à l'avenir.

```python hide
rng_f = np.random.default_rng(3)
Wrand = rng_f.dirichlet(np.ones(5), 3000)
mus_r = Wrand @ mu; vols_r = np.sqrt(np.einsum("ij,jk,ik->i", Wrand, S, Wrand))
cibles = np.linspace(w_min @ mu, mu.max(), 40)
Wf = O.frontiere(mu, S, cibles)
vols_f = np.sqrt(np.einsum("ij,jk,ik->i", Wf, S, Wf))
fig, ax = plt.subplots(figsize=(6.8, 4.0))
ax.scatter(100 * vols_r, 100 * mus_r, s=4, color=MUET, alpha=0.35, label="portefeuilles aléatoires")
ax.plot(100 * vols_f, 100 * cibles, color=BLEU, label="frontière efficiente")
for i, nom in enumerate(ACT):
    ax.scatter(100 * sd[i], 100 * mu[i], color=ENCRE2, zorder=3)
    dec = (8, -14) if nom == "obligations" else (5, 3)
    ax.annotate(nom.replace("_", " "), (100 * sd[i], 100 * mu[i]), xytext=dec, textcoords="offset points", fontsize=8)
ax.scatter(100 * O.vol_ptf(w_min, S), 100 * (w_min @ mu), color=AQUA, marker="s", zorder=4, label="variance minimale")
ax.scatter(100 * O.vol_ptf(w_tan, S), 100 * (w_tan @ mu), color=ORANGE, marker="D", zorder=4, label="tangent")
x_cml = np.linspace(0, 100 * 0.12, 20)
ax.plot(x_cml, 100 * RF + x_cml * (w_tan @ mu - RF) / O.vol_ptf(w_tan, S), color=ORANGE, lw=1.0, ls="--")
ax.set_xlim(0, 25); ax.set_ylim(-4, 12)
ax.set_xlabel("écart-type annuel (%)"); ax.set_ylabel("rendement annuel moyen (%)"); ax.legend(loc="upper left", fontsize=8)
style.save(fig, "ch07-frontiere-5actifs.png")
```
<!--sortie-->
```text
figure : ch07-frontiere-5actifs.png
```

![Cinq classes d'actifs de `rendements_marche.csv` : les actifs pris isolément (points), 3 000 portefeuilles aléatoires (nuage gris), la frontière efficiente sans vente à découvert (courbe bleue), le portefeuille de variance minimale et le portefeuille tangent, avec la droite qui part du taux sans risque (1,5 %). Les matières premières, au rendement moyen négatif sur l'historique, sont dominées.](figures/ch07-frontiere-5actifs.png)

### 7.2.4 Contributions au risque

Savoir qu'un portefeuille a une volatilité de 10 % ne dit pas **qui** la produit. Comme σ_p(w) est **homogène de degré 1** (multiplier tous les poids par λ multiplie σ_p par λ), le théorème d'Euler donne
$$\sigma_p=\sum_i w_i\frac{\partial\sigma_p}{\partial w_i},\qquad \frac{\partial\sigma_p}{\partial w_i}=\frac{(\Sigma w)_i}{\sigma_p}.$$
La **contribution au risque** de l'actif i est donc RC_i = w_i(Σw)_i/σ_p, et les contributions **s'additionnent** exactement à la volatilité du portefeuille. Un actif peut peser 20 % du capital et 70 % du risque.

La **parité des risques** (*risk parity*) cherche les poids qui égalisent les contributions : RC_i = σ_p/n pour tout i. Pas de formule fermée en général ; on résout numériquement.

```python hide-code
def rp_obj(w): 
    rc = O.contributions_risque(np.abs(w) / np.abs(w).sum(), S)
    return float(((rc - rc.mean()) ** 2).sum())
from scipy.optimize import minimize
res_rp = minimize(rp_obj, np.full(5, 0.2), method="Nelder-Mead", options={"xatol": 1e-9, "fatol": 1e-16, "maxiter": 20000})
w_rp = np.abs(res_rp.x) / np.abs(res_rp.x).sum()
tab = {}
for nom, w in (("égal pondéré", we), ("variance min.", w_min), ("parité des risques", w_rp)):
    rc = O.contributions_risque(w, S); tab[nom] = list((100 * rc / rc.sum()).round(0).astype(int)) + [round(100 * O.vol_ptf(w, S), 1)]
print("part de chaque actif dans le risque (%), puis volatilité du portefeuille (%)")
print(pd.DataFrame(tab, index=ACT + ["volatilité"]).to_string(float_format=lambda x: f"{x:g}"))
rc_eq = O.contributions_risque(we, S) / O.vol_ptf(we, S)
NUM("rc_eq_actions", 100 * (rc_eq[0] + rc_eq[1])); NUM("rc_eq_obl", 100 * rc_eq[2])
NUM("vol_rp", 100 * O.vol_ptf(w_rp, S)); NUM("w_rp_obl", 100 * w_rp[2]); NUM("mu_rp", 100 * (w_rp @ mu))
assert abs(O.contributions_risque(we, S).sum() - O.vol_ptf(we, S)) < 1e-12
```
<!--sortie-->
```text
part de chaque actif dans le risque (%), puis volatilité du portefeuille (%)
             égal pondéré  variance min.  parité des risques
actions_A              26              2                  20
actions_B              33              1                  20
obligations             0             89                  20
immobilier             16              6                  20
matieres               25              2                  20
volatilité           11.7            4.1                 5.8
NUM rc_eq_actions 58.894695480984524
NUM rc_eq_obl 0.13104321161395846
NUM vol_rp 5.780075085270962
NUM w_rp_obl 62.29466897961221
NUM mu_rp 3.783987101618801
```

Dans le portefeuille égal pondéré, les deux indices d'actions, qui pèsent 40 % du capital, produisent 59 % du risque ; les obligations, 20 % du capital, en produisent 0,1 %. La parité des risques doit pour cela mettre 62 % du capital en obligations, ce qui donne une volatilité de 5,8 % et un rendement de 3,8 % sur l'historique.

> 💡 **Intuition.** Répartir le **capital** également n'est pas répartir le **risque** également. La contribution au risque est la bonne comptabilité pour dire « d'où viendra la prochaine mauvaise nouvelle ».

### 7.2.5 L'idée du CAPM

Si **tous** les investisseurs raisonnaient comme Markowitz avec les mêmes anticipations, ils détiendraient tous le même portefeuille risqué (le tangent), et ce portefeuille serait le **marché** lui-même. Le **modèle d'équilibre des actifs financiers** (CAPM, Sharpe 1964) en tire une conséquence : le rendement espéré d'un actif ne dépend que de son **bêta**, sa sensibilité au marché,
$$\mu_i-r_f=\beta_i\,(\mu_m-r_f),\qquad \beta_i=\frac{\operatorname{cov}(r_i,r_m)}{\operatorname{var}(r_m)}.$$
Le risque **propre** d'un actif (celui qui n'est pas lié au marché) se diversifie et n'est pas rémunéré.

Pour voir le bêta à l'œuvre, prenons comme « marché » la moyenne des deux indices d'actions :

```python hide-code
rm = rend[["actions_A", "actions_B"]].mean(axis=1)
beta = {a: float(np.cov(rend[a], rm)[0, 1] / rm.var()) for a in ACT}
mum = rm.mean() * 252
tab = pd.DataFrame({"bêta": beta, "rendement observé (%)": 100 * pd.Series(mu, index=ACT),
                    "rendement CAPM (%)": {a: 100 * (RF + beta[a] * (mum - RF)) for a in ACT}}).round(2)
print(tab.to_string())
NUM("beta_obl", beta["obligations"]); NUM("beta_imm", beta["immobilier"]); NUM("beta_mat", beta["matieres"])
NUM("capm_imm", 100 * (RF + beta["immobilier"] * (mum - RF))); NUM("obs_imm", 100 * mu[3])
```
<!--sortie-->
```text
             bêta  rendement observé (%)  rendement CAPM (%)
actions_A    0.88                   5.63                4.57
actions_B    1.12                   4.34                5.40
obligations -0.02                   4.02                1.44
immobilier   0.40                   5.71                2.91
matieres     0.41                  -2.89                2.92
NUM beta_obl -0.017996729993034907
NUM beta_imm 0.40409575779034085
NUM beta_mat 0.4083400104677518
NUM capm_imm 2.9081799252739544
NUM obs_imm 5.7071637000000015
```

Le bêta des obligations est -0,02 (quasi indépendantes des actions), celui de l'immobilier 0,40, celui des matières premières 0,41. Le CAPM prévoit pour l'immobilier un rendement de 2,9 % ; l'historique donne 5,7 %. **L'écart n'est pas une erreur du modèle : c'est une propriété des données**, dont les rendements espérés ont été programmés sans aucune référence au CAPM. Dans la réalité, on observe des écarts (les « alphas ») et on ne sait jamais s'ils sont du bruit d'estimation ou de l'information : voir la section suivante.

> ⚠️ **Limites.** Le CAPM suppose des investisseurs identiques, un marché observable (le « vrai » portefeuille de marché contient tous les actifs, y compris les actifs non cotés), un seul horizon et des rendements décrits par leur moyenne et leur variance. Il reste utile comme **langage** (bêta, risque systématique, risque propre) bien plus que comme prévision.

### 7.2.6 L'estimation, maillon faible

L'optimisation de Markowitz est un **amplificateur d'erreurs** : elle surpondère les actifs dont les paramètres estimés flattent le rendement, et sous-pondère ceux dont ils sont défavorables. Or on estime μ et Σ avec peu de données.

**Les rendements espérés sont très mal connus.** L'écart-type de la moyenne d'un rendement annuel observé pendant T années est σ/√T. Avec T = 15,9 ans, pour l'indice d'actions A (volatilité 19 %), cela fait ± 4,7 points : la moyenne observée (5,6 %) est compatible, à deux erreurs types, avec des rendements espérés allant de -4 % à 15 %. Le tableau compare les moyennes observées à la **vérité programmée** (rendement espéré journalier de 4, 4, 1, 2 et 1 pour dix mille, soit environ 10,1 %, 10,1 %, 2,5 %, 5,0 % et 2,5 % par an) :

```python hide-code
vrai = np.array([4, 4, 1, 2, 1]) * 1e-4 * 252
se = sd / np.sqrt(len(rend) / 252)
tab = pd.DataFrame({"observé (%)": 100 * mu, "vrai (%)": 100 * vrai, "erreur type (pts)": 100 * se,
                    "écart en erreurs types": (mu - vrai) / se}, index=ACT).round(1)
print(tab.to_string())
NUM("sd_A", 100 * sd[0]); NUM("se_A", 100 * se[0]); NUM("mu_A", 100 * mu[0])
NUM("ic_lo", 100 * (mu[0] - 2 * se[0])); NUM("ic_hi", 100 * (mu[0] + 2 * se[0])); NUM("mu_mat", 100 * mu[4]); NUM("vrai_mat", 100 * vrai[4])
NUM("ecart_max", np.abs((mu - vrai) / se).max())
```
<!--sortie-->
```text
             observé (%)  vrai (%)  erreur type (pts)  écart en erreurs types
actions_A            5.6      10.1                4.7                    -0.9
actions_B            4.3      10.1                5.7                    -1.0
obligations          4.0       2.5                1.1                     1.4
immobilier           5.7       5.0                3.3                     0.2
matieres            -2.9       2.5                5.5                    -1.0
NUM sd_A 18.687930711775554
NUM se_A 4.6906333815543295
NUM mu_A 5.633044200000001
NUM ic_lo -3.748222563108657
NUM ic_hi 15.01431096310866
NUM mu_mat -2.885185799999999
NUM vrai_mat 2.52
NUM ecart_max 1.36932999812444
```

Aucun écart n'est « anormal » (le plus grand est de 1,4 erreur type), et pourtant l'estimation place les matières premières à -2,9 % alors que leur rendement espéré vrai est de 2,5 %, et classe l'immobilier (5,7 %) devant l'indice d'actions B alors que le rendement espéré vrai de l'immobilier (5,0 %) est deux fois plus faible que celui des actions (10,1 %). **L'optimiseur s'appuie donc sur du bruit.**

**Les poids optimaux sautent d'une fenêtre à l'autre.** On découpe l'historique en fenêtres d'un an (250 jours), on calcule à chaque fois le portefeuille de variance minimale et le portefeuille tangent, puis on regarde la stabilité des poids :

```python hide
from sklearn.covariance import LedoitWolf
fen = [(s0, s0 + 250) for s0 in range(0, len(rend) - 500, 250)]
Wmin_f, Wtan_f, Wlw_f = [], [], []
oos = {"empirique": [], "rétrécie (Ledoit–Wolf)": [], "poids égaux": []}
for s0, s1 in fen:
    est = rend.iloc[s0:s1]; ev = rend.iloc[s1:s1 + 250]
    mu_e, S_e = O.stats_annuelles(est)
    S_lw = LedoitWolf().fit(est).covariance_ * 252
    wm_, wt_, wl_ = O.min_variance(S_e), O.tangent(mu_e, S_e, RF), O.min_variance(S_lw)
    Wmin_f.append(wm_); Wtan_f.append(wt_); Wlw_f.append(wl_)
    for nom, w in (("empirique", wm_), ("rétrécie (Ledoit–Wolf)", wl_), ("poids égaux", we)):
        oos[nom].append(ev.to_numpy() @ w)
Wmin_f, Wtan_f = np.array(Wmin_f), np.array(Wtan_f)
NUM("n_fen", len(fen))
NUM("lw_obl", 100 * np.mean(np.array(Wlw_f)[:, 2])); NUM("emp_obl", 100 * Wmin_f[:, 2].mean())
NUM("tan_obl_min", 100 * Wtan_f[:, 2].min()); NUM("tan_obl_max", 100 * Wtan_f[:, 2].max())
NUM("tan_act_max", 100 * Wtan_f[:, :2].sum(axis=1).max())
NUM("min_obl_min", 100 * Wmin_f[:, 2].min()); NUM("min_obl_max", 100 * Wmin_f[:, 2].max())
NUM("turn_tan", float(np.mean(np.abs(np.diff(Wtan_f, axis=0)).sum(axis=1))))
NUM("turn_min", float(np.mean(np.abs(np.diff(Wmin_f, axis=0)).sum(axis=1))))
fig, axs = plt.subplots(1, 2, figsize=(9.4, 3.5), sharey=True)
for ax, Wf_, titre in ((axs[0], Wmin_f, "variance minimale"), (axs[1], Wtan_f, "portefeuille tangent")):
    for j, nom in enumerate(ACT):
        ax.scatter(np.full(len(Wf_), j) + np.random.default_rng(j).uniform(-0.12, 0.12, len(Wf_)), 100 * Wf_[:, j], s=16, color=[BLEU, VIOLET, AQUA, ORANGE, ROUGE][j])
    ax.set_xticks(range(5)); ax.set_xticklabels([n.replace("_", "\n") for n in ACT], fontsize=8); ax.set_title(titre, fontsize=10)
axs[0].set_ylabel("poids (%) selon la fenêtre d'un an")
style.save(fig, "ch07-instabilite.png")
```
<!--sortie-->
```text
NUM n_fen 14
NUM lw_obl 77.32210657238386
NUM emp_obl 85.63968932845609
NUM tan_obl_min 0.0
NUM tan_obl_max 100.0
NUM tan_act_max 59.34394929984344
NUM min_obl_min 69.75535004844967
NUM min_obl_max 93.55093142954121
NUM turn_tan 1.073164501616729
NUM turn_min 0.18992087147983866
figure : ch07-instabilite.png
```

![Poids des cinq actifs dans les portefeuilles de variance minimale (à gauche) et tangent (à droite), recalculés sur chacune des fenêtres successives d'un an (un point par fenêtre). La variance minimale, qui n'utilise que les covariances, est stable ; le portefeuille tangent, qui utilise aussi les rendements moyens, change de visage d'une année à l'autre.](figures/ch07-instabilite.png)

Sur 14 fenêtres, le poids des obligations dans le portefeuille de variance minimale reste entre 70 % et 94 % ; celui du portefeuille tangent varie de 0 % à 100 %, avec jusqu'à 59 % d'actions certaines années. La rotation (somme des variations absolues de poids d'une fenêtre à la suivante, 2 au maximum) vaut 0,19 en moyenne pour la variance minimale et 1,07 pour le tangent. **La variance minimale dépend seulement de Σ, bien estimée ; le tangent dépend de μ, mal estimé.**

**Le rétrécissement de la covariance.** Quand le nombre d'actifs n s'approche du nombre d'observations T, la covariance empirique devient instable (elle compte n(n + 1)/2 paramètres). Le remède classique de **Ledoit et Wolf** consiste à la **rétrécir** vers une cible simple (une matrice scalaire) : Σ* = (1 − δ) S + δ · m · I, où m est la variance moyenne et δ ∈ [0, 1] est choisi par une formule de risque quadratique. Testons-le deux fois, en jugeant les portefeuilles de variance minimale sur des données qu'ils n'ont pas vues :

```python hide-code
for nom in oos:
    NUM("oos_" + nom[:3], float(np.mean([np.std(r_) * np.sqrt(252) for r_ in oos[nom]])) * 100)
res60 = O.experience_retrecissement(n=60, T=120, reps=100, seed=1)
print("5 actifs réels, estimation sur 250 jours, test sur les 250 suivants (volatilité annuelle, %)")
print(pd.Series({k: round(float(np.mean([np.std(r_) * np.sqrt(252) for r_ in v])) * 100, 2) for k, v in oos.items()}).to_string())
print()
print("60 actifs simulés, estimation sur 120 jours, volatilité VRAIE (%)")
print(pd.Series(dict(zip(["empirique", "rétrécie (Ledoit–Wolf)", "poids égaux", "optimum vrai"], (100 * res60).round(2)))).to_string())
NUM("lw60_emp", 100 * res60[0]); NUM("lw60_lw", 100 * res60[1]); NUM("lw60_eq", 100 * res60[2]); NUM("lw60_opt", 100 * res60[3])
```
<!--sortie-->
```text
NUM oos_emp 4.030384294524111
NUM oos_rét 4.334113286267227
NUM oos_poi 11.072743921763355
5 actifs réels, estimation sur 250 jours, test sur les 250 suivants (volatilité annuelle, %)
empirique                  4.03
rétrécie (Ledoit–Wolf)     4.33
poids égaux               11.07

60 actifs simulés, estimation sur 120 jours, volatilité VRAIE (%)
empirique                  1.03
rétrécie (Ledoit–Wolf)     0.90
poids égaux               10.28
optimum vrai               0.73
NUM lw60_emp 1.0305149087762866
NUM lw60_lw 0.8989668954229215
NUM lw60_eq 10.275877674205237
NUM lw60_opt 0.73359987781327
```

Avec **5 actifs réels et 250 jours**, le rétrécissement **n'aide pas** : la covariance empirique est déjà bien estimée, et le rétrécissement vers la matrice scalaire relève la variance estimée des actifs peu volatils : le poids moyen des obligations passe de 86 % à 77 %, ce qui rend le portefeuille plus risqué. Avec **60 actifs simulés et 120 jours**, il aide nettement : la volatilité vraie du portefeuille construit sur la covariance rétrécie est 0,90 %, contre 1,03 % avec la covariance empirique ; le minimum possible, avec la vraie covariance, est 0,73 %. Quant aux poids égaux (10,3 %), ils sont dix fois plus risqués : ne rien optimiser n'est pas une solution non plus.

> ✅ **À retenir.** (1) Un portefeuille de variance minimale ne dépend que de Σ ; un portefeuille tangent dépend de μ, très mal connu. (2) Les poids « optimaux » d'un historique sont un **résultat avec incertitude**, pas une vérité. (3) Le rétrécissement de la covariance est utile quand n s'approche de T, inutile (voire nuisible) quand n est petit. (4) On **contraint** les poids (bornes, pas de vente à découvert) et on **diversifie les méthodes** pour que le portefeuille ne dépende pas d'une estimation fragile.

### 7.2.7 La diversification en période de stress

La diversification dépend des **corrélations**, et celles-ci ne sont pas constantes. Dans `marche_verite.csv`, chaque jour est étiqueté « calme » ou « stress » ; **on ne connaît pas cette étiquette en réalité**, mais elle permet de mesurer ce que l'on aurait vu si on l'avait connue.

```python hide-code
reg = regimes.reindex(rend.index)
out = {}
cov_reg = {}
for g in ("calme", "stress"):
    Rg = rend[reg == g]; mug, Sg = O.stats_annuelles(Rg); sdg = np.sqrt(np.diag(Sg)); cov_reg[g] = (Sg, sdg)
    out[g] = [len(Rg), round(100 * sdg[0]), round(Sg[0, 1] / sdg[0] / sdg[1], 2), round(Sg[0, 3] / sdg[0] / sdg[3], 2),
              round(100 * O.vol_ptf(we, Sg), 1), round(100 * O.vol_ptf(w_min, Sg), 1)]
print(pd.DataFrame(out, index=["jours", "volatilité actions A (%)", "corrélation A–B", "corrélation A–immobilier",
                               "volatilité égal pondéré (%)", "volatilité variance min. (%)"]).to_string(float_format=lambda x: f"{x:g}"))
NUM("part_stress", 100 * (reg == "stress").mean()); NUM("n_stress", int((reg == "stress").sum()))
NUM("volA_calme", 100 * cov_reg["calme"][1][0]); NUM("volA_stress", 100 * cov_reg["stress"][1][0])
NUM("vol_min_calme", 100 * O.vol_ptf(w_min, cov_reg["calme"][0])); NUM("vol_min_stress", 100 * O.vol_ptf(w_min, cov_reg["stress"][0]))
NUM("vol_eq_calme", 100 * O.vol_ptf(we, cov_reg["calme"][0])); NUM("vol_eq_stress", 100 * O.vol_ptf(we, cov_reg["stress"][0]))
NUM("corrAB_stress", cov_reg["stress"][0][0, 1] / cov_reg["stress"][1][0] / cov_reg["stress"][1][1])
NUM("corrAB_calme", cov_reg["calme"][0][0, 1] / cov_reg["calme"][1][0] / cov_reg["calme"][1][1])
```
<!--sortie-->
```text
                              calme  stress
jours                          3718     282
volatilité actions A (%)         16      38
corrélation A–B                0.57    0.89
corrélation A–immobilier       0.43    0.87
volatilité égal pondéré (%)     9.5    27.1
volatilité variance min. (%)    3.6     7.9
NUM part_stress 7.049999999999999
NUM n_stress 282
NUM volA_calme 16.288569897557117
NUM volA_stress 38.181025579624006
NUM vol_min_calme 3.642538879463517
NUM vol_min_stress 7.905887846449958
NUM vol_eq_calme 9.511104049729584
NUM vol_eq_stress 27.10878517551788
NUM corrAB_stress 0.885792994364173
NUM corrAB_calme 0.5731072398636516
```

Les jours de stress (7 % des jours) doublent la volatilité (indice A : 16 % en calme, 38 % en stress), et les corrélations entre actions et immobilier **s'envolent** (A–B de 0,57 à 0,89). Les actifs qui se diversifiaient hier chutent ensemble aujourd'hui. Le portefeuille de variance minimale, dont la volatilité « moyenne » est 4,1 %, a une volatilité de 3,6 % en calme et de 7,9 % en stress ; le portefeuille égal pondéré passe de 9,5 % à 27,1 %.

```python hide
fig, axs = plt.subplots(1, 2, figsize=(9.0, 3.6))
for ax, g in zip(axs, ("calme", "stress")):
    Sg, sdg = cov_reg[g]; Cg = Sg / np.outer(sdg, sdg)
    im = ax.imshow(Cg, cmap=style.DIV, vmin=-1, vmax=1)
    ax.set_xticks(range(5)); ax.set_yticks(range(5))
    ax.set_xticklabels([n.replace("_", "\n") for n in ACT], fontsize=7); ax.set_yticklabels([n.replace("_", " ") for n in ACT], fontsize=8)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{Cg[i, j]:.2f}".replace(".", ","), ha="center", va="center", fontsize=7, color="black")
    ax.set_title(f"régime {g}", fontsize=10); ax.grid(False)
style.save(fig, "ch07-correlations-regimes.png")
```
<!--sortie-->
```text
figure : ch07-correlations-regimes.png
```

![Matrices de corrélation des cinq actifs dans les jours « calmes » (à gauche) et dans les jours de « stress » (à droite). En stress, les corrélations entre les deux indices d'actions et l'immobilier approchent 0,9 ; les obligations restent indépendantes.](figures/ch07-correlations-regimes.png)

Une autre façon de voir la même chose : les **queues** des rendements. Le rendement journalier d'un portefeuille n'est pas gaussien. La kurtosis en excès (0 pour une loi normale) de l'indice A vaut 19, celle du portefeuille de variance minimale 7 : les extrêmes sont beaucoup plus fréquents que ne le dit la loi normale. Pour le portefeuille de variance minimale, la perte journalière dépassée un jour sur cent est de 0,71 % sur l'historique, mais de 0,58 % si l'on suppose les rendements gaussiens de même moyenne et de même variance : la loi normale **sous-estime** la perte d'environ 21 %. Les mesures de risque (VaR et expected shortfall, section 3.1) dépendent de ce choix.

```python hide
from scipy import stats
rp = rend.to_numpy() @ w_min
NUM("kurt_A", float(stats.kurtosis(rend["actions_A"]))); NUM("kurt_min", float(stats.kurtosis(rp)))
NUM("var_emp", -100 * np.quantile(rp, 0.01)); NUM("var_norm", -100 * (rp.mean() - 2.326 * rp.std()))
NUM("sous_est", 100 * (np.quantile(rp, 0.01) / (rp.mean() - 2.326 * rp.std()) - 1))
```
<!--sortie-->
```text
NUM kurt_A 19.185304610154223
NUM kurt_min 7.028402913227358
NUM var_emp 0.7076717524196441
NUM var_norm 0.5832120633865758
NUM sous_est 21.340383172179255
```

> ⚠️ **Piège : la corrélation moyenne ment.** Une matrice de corrélation estimée sur tout l'historique mélange les jours calmes et les jours de stress : elle prédit un risque (4,1 %) qui n'est celui d'aucun des deux régimes, et qui **sous-estime** le risque quand on en a le plus besoin. Les remèdes (modèles à régimes, corrélations de stress, **scénarios**) font l'objet du chapitre 3 (3.2 : stress tests).

> ✅ **À retenir.** (1) Le risque d'un portefeuille dépend des covariances, pas seulement des volatilités. (2) La frontière efficiente est un **outil de réflexion**, dont les entrées (μ, Σ) sont estimées avec erreur. (3) Les corrélations montent en stress : la diversification est la plus fragile quand elle est la plus utile. (4) Un portefeuille se juge aussi sur ses queues.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.5 à 7.7 et exercices 7.6 à 7.10.
