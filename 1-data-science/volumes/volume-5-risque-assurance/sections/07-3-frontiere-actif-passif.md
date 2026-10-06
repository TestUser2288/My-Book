## 7.3 De la frontière efficiente à l'actif-passif

Les deux sections précédentes se sont ignorées : la première a traité l'actif comme un moyen d'**apparier** un passif, la seconde a choisi des actifs **sans passif**. Un gestionnaire d'assurance doit faire les deux en même temps : le critère n'est pas le risque de l'actif, c'est le risque du **surplus**. Cette section reprend la théorie du portefeuille avec le bon objet, puis mesure le risque du surplus par une VaR et une expected shortfall, et enfin le simule sur dix ans.

```python hide
b = O.Bilan(surplus=0.10)
w_app = b.poids_zc()
dY, ann = O.tirages_annuels(b, 5000, 21)
X, dliab = O.pnl_instruments(b, dY, ann)
S0 = b.A0 - b.L0
NUM("S0_M", S0 / 1e6); NUM("n_scen", len(dY))
strat = {"Marché": {5: 0.40, "act": 0.45, "imm": 0.15},
         "Apparié": w_app,
         "Mixte": {k: 0.8 * v for k, v in w_app.items()} | {"act": 0.14, "imm": 0.06}}
```
<!--sortie-->
```text
NUM S0_M 46.02259525825697
NUM n_scen 5000
```

### 7.3.1 Le surplus comme objet à optimiser

Sur un an, la variation du surplus d'une allocation w vaut
$$\Delta S=\underbrace{A_0\,w^\top r}_{\text{gain de l'actif}}-\underbrace{\Delta L}_{\text{variation du passif (et prestations)}},$$
où r est le vecteur des rendements des instruments. Sa variance se décompose :
$$\operatorname{Var}(\Delta S)=A_0^2\,w^\top\Sigma_r\,w\;-\;2A_0\,w^\top\operatorname{Cov}(r,\Delta L)\;+\;\operatorname{Var}(\Delta L).$$
Le premier terme est le risque de l'actif seul (celui de Markowitz). Le deuxième est le **terme de couverture** : il récompense les actifs qui varient **comme le passif**. Le troisième ne dépend pas de w. Minimiser le risque du surplus, c'est donc **régresser le passif sur les actifs** : le meilleur portefeuille est celui qui **réplique** le passif, et non celui qui minimise la variance de l'actif.

> 💡 **Intuition.** Pour une famille qui doit payer un loyer fixe dans cinq ans, le placement le moins risqué n'est pas le plus stable d'année en année : c'est celui qui vaudra exactement le loyer dans cinq ans. Le risque se mesure **par rapport à la dette**, pas dans l'absolu.

Pour le vérifier, on tire 5 000 scénarios annuels (courbe des taux et marchés tirés dans l'historique, voir plus bas), on calcule pour chaque scénario le gain en euros de six instruments (zéros-coupons de maturités 5, 10, 20 et 30 ans, actions, immobilier) et la variation du passif, **avec revalorisation complète**. Comparons deux critères :

- **Markowitz sans passif** : le portefeuille de variance minimale des **actifs** ;
- **réplication** : le portefeuille de variance minimale du **surplus**.

```python hide-code
from scipy.optimize import minimize
Cx = np.cov(X.T) / 1e12
res_mk = minimize(lambda w: w @ Cx @ w, np.full(6, 1 / 6), constraints=[{"type": "eq", "fun": lambda w: w.sum() - 1}],
                  bounds=[(0, 1)] * 6, method="SLSQP", options={"ftol": 1e-16})
w_mk = res_mk.x
w_rep = O.surplus_min_variance(X, dliab)
tab = {}
for nom, w in (("variance min. de l'actif", w_mk), ("réplication du passif", w_rep)):
    dS = X @ w - dliab
    tab[nom] = list((100 * w).round(0).astype(int)) + [round(dS.std() / 1e6, 1)]
print("poids (%) puis écart-type de la variation annuelle du surplus (M€)")
print(pd.DataFrame(tab, index=O.NOMS_INSTR + ["écart-type du surplus"]).to_string(float_format=lambda x: f"{x:g}"))
NUM("sd_mk", (X @ w_mk - dliab).std() / 1e6); NUM("sd_rep", (X @ w_rep - dliab).std() / 1e6)
NUM("sd_liab", dliab.std() / 1e6)
NUM("w_mk_z5", 100 * w_mk[0]); NUM("w_rep_z5", 100 * w_rep[0]); NUM("w_rep_z10", 100 * w_rep[1]); NUM("w_rep_z30", 100 * w_rep[3])
NUM("w_rep_risque", 100 * (w_rep[4] + w_rep[5]))
```
<!--sortie-->
```text
poids (%) puis écart-type de la variation annuelle du surplus (M€)
                       variance min. de l'actif  réplication du passif
ZC 5 ans                                     99                     48
ZC 10 ans                                     0                     14
ZC 20 ans                                     0                      0
ZC 30 ans                                     0                     38
actions                                       1                      0
immobilier                                    1                      0
écart-type du surplus                      22.2                    0.4
NUM sd_mk 22.24321548367511
NUM sd_rep 0.4200616799472272
NUM sd_liab 30.94542997774432
NUM w_mk_z5 98.6125162111943
NUM w_rep_z5 47.827796486785346
NUM w_rep_z10 14.330419319574442
NUM w_rep_z30 37.818072975317506
NUM w_rep_risque 0.02371121832234738
```

Le portefeuille de variance minimale **de l'actif** est presque entièrement en zéro-coupon à 5 ans (99 %), l'actif le moins volatil ; il laisse un surplus dont l'écart-type annuel est de **22,2 M€**, soit 72 % du risque du passif lui-même (30,9 M€) : il ne le couvre presque pas. Le portefeuille de **réplication** utilise des maturités 5, 10 et 30 ans (48 %, 14 % et 38 %) et aucun actif risqué (0 %) ; l'écart-type du surplus tombe à **0,4 M€**, soit environ 53 fois moins. Le meilleur actif pour ce passif n'est pas l'actif le moins risqué : c'est celui qui **lui ressemble**.

```python hide
NUM("rapport_sd", (X @ w_mk - dliab).std() / (X @ w_rep - dliab).std())
NUM("ratio_mk_liab", 100 * (X @ w_mk - dliab).std() / dliab.std())
```
<!--sortie-->
```text
NUM rapport_sd 52.95226045486832
NUM ratio_mk_liab 71.8788380050697
```

### 7.3.2 Optimiser sous contrainte de risque

Aucun gestionnaire ne se contente de répliquer : un portefeuille de réplication rapporte peu, et l'on a de bonnes raisons de prendre un peu de risque pour augmenter le gain espéré. Le problème devient celui de la section 7.2, avec le surplus à la place du portefeuille :
$$\max_{w}\;\mathbb{E}[\Delta S]\quad\text{sous}\quad \sum_j w_j=1,\; w_j\ge0,\;\;\sigma(\Delta S)\le\sigma_{\text{budget}}.$$
On balaie le **budget de risque** σ_budget (l'écart-type annuel du surplus que la direction accepte) et on lit l'allocation qui rapporte le plus.

```python hide-code
bud = np.array([2, 5, 10, 20, 40, 80]) * 1e6
Wfront = O.surplus_frontiere(X, dliab, bud)
tab = {}
for sb, w in zip(bud, Wfront):
    dS = X @ w - dliab
    tab[f"{sb/1e6:.0f} M€"] = list((100 * w).round(0).astype(int)) + [round(dS.mean() / 1e6, 1)]
print("allocation (%) et gain espéré du surplus (M€) selon le budget de risque (écart-type annuel du surplus)")
print(pd.DataFrame(tab, index=O.NOMS_INSTR + ["gain espéré (M€)"]).to_string(float_format=lambda x: f"{x:g}"))
gains = [(X @ w - dliab).mean() / 1e6 for w in Wfront]
NUM("gain_2", gains[0]); NUM("gain_10", gains[2]); NUM("gain_40", gains[4]); NUM("gain_80", gains[5])
NUM("risque_10_pct", 100 * (Wfront[2][4] + Wfront[2][5]))
NUM("risque_80_pct", 100 * (Wfront[5][4] + Wfront[5][5]))
```
<!--sortie-->
```text
allocation (%) et gain espéré du surplus (M€) selon le budget de risque (écart-type annuel du surplus)
                  2 M€  5 M€  10 M€  20 M€  40 M€  80 M€
ZC 5 ans            56    49     39     19      0      0
ZC 10 ans            0     0      0      0      0      0
ZC 20 ans            0     0      0      0      0      0
ZC 30 ans           42    45     50     59     54     12
actions              1     2      4      9     16     24
immobilier           1     3      6     13     31     65
gain espéré (M€)   1.7   2.5    3.7    6.2   10.6     16
NUM gain_2 1.7157182791349535
NUM gain_10 3.7236071707487657
NUM gain_40 10.560725460418782
NUM gain_80 16.02227501989792
NUM risque_10_pct 10.64231843368498
NUM risque_80_pct 88.18717031210659
```

Le tableau se lit de gauche à droite comme un **dial de risque**. À 2 M€ d'écart-type, on retrouve la réplication (gain espéré de 1,7 M€). À 10 M€, la part d'actifs risqués est de 11 % ; à 80 M€, de 88 %, pour un gain espéré de 16 M€. **Le gain espéré croît bien plus lentement que le risque** : multiplier le risque par 40 (de 2 à 80 M€) ne multiplie le gain que par 9. Et ce gain est un **gain historique** : les espérances viennent des mêmes tirages que le risque, avec toutes les réserves de la section 7.2.6.

```python hide
NUM("rapport_gain", gains[5] / gains[0])
sds = np.array([(X @ w - dliab).std() / 1e6 for w in Wfront]); mus = np.array(gains)
Cxr = np.cov(X.T) / 1e12
wm_s = {"Marché": O.poids_vecteur(strat["Marché"]), "Apparié": O.poids_vecteur(strat["Apparié"]), "Mixte": O.poids_vecteur(strat["Mixte"]),
        "Markowitz sans passif": w_mk}
fig, ax = plt.subplots(figsize=(6.8, 4.0))
bgrid = np.linspace(1, 90, 25) * 1e6
Wg = O.surplus_frontiere(X, dliab, bgrid)
ax.plot([(X @ w - dliab).std() / 1e6 for w in Wg], [(X @ w - dliab).mean() / 1e6 for w in Wg], color=BLEU, label="frontière du surplus")
for (nom, w), col in zip(wm_s.items(), (ORANGE, AQUA, VIOLET, ROUGE)):
    d_ = X @ w - dliab
    ax.scatter(d_.std() / 1e6, d_.mean() / 1e6, color=col, s=36, zorder=3)
    ax.annotate(nom, (d_.std() / 1e6, d_.mean() / 1e6), xytext=(6, -3), textcoords="offset points", fontsize=8)
ax.set_xlabel("écart-type annuel de la variation du surplus (M€)"); ax.set_ylabel("gain espéré du surplus (M€)")
ax.set_xlim(0, 105)
style.save(fig, "ch07-frontiere-surplus.png")
```
<!--sortie-->
```text
NUM rapport_gain 9.338523238195128
figure : ch07-frontiere-surplus.png
```

![Frontière du surplus : gain espéré du surplus (M€) en fonction de son écart-type annuel, pour l'allocation de gain maximal à budget de risque donné (courbe), et pour quatre allocations de référence (points). Les quatre allocations de référence sont **sous** la frontière : pour le même risque, une allocation optimisée rapporte plus. « Markowitz sans passif » est le plus éloigné : il prend du risque de surplus pour un gain espéré négatif.](figures/ch07-frontiere-surplus.png)

> ⚠️ **Piège : une frontière qui dépend du modèle de passif.** Tout ce qui précède suppose le passif connu : prestations fixes, mortalité figée. Si les prestations dépendent des taux (garantie de taux minimum, rachats), le passif est **optionnel** et le meilleur actif change. Le résultat d'une optimisation actif-passif n'est jamais meilleur que le modèle de passif sur lequel il repose.

### 7.3.3 VaR et expected shortfall du surplus

La direction ne regarde pas l'écart-type, elle regarde les **pertes extrêmes** : quelle baisse du surplus un an « sur 200 » ? Ce sont la VaR à 99,5 % sur un an (le quantile de la perte, c'est l'idée du capital requis du régime Solvabilité, section 4.2) et l'expected shortfall (la perte moyenne dans la queue, section 3.1). On les calcule sur les scénarios annuels :

```python hide-code
KEY = {"Marché": "mar", "Apparié": "app", "Mixte": "mix", "Optimisé (10 M€)": "opt", "Markowitz sans passif": "mk"}
pf = {"Marché": wm_s["Marché"], "Apparié": wm_s["Apparié"], "Mixte": wm_s["Mixte"], "Optimisé (10 M€)": Wfront[2],
      "Markowitz sans passif": w_mk}
lignes = {}
for nom, w in pf.items():
    dS = X @ w - dliab
    v, e = O.var_es(dS)
    lignes[nom] = [round(dS.mean() / 1e6, 1), round(dS.std() / 1e6, 1), round(v / 1e6, 1), round(e / 1e6, 1),
                   round(S0 / v, 2)]
    k = KEY[nom]
    NUM("var_" + k, v / 1e6); NUM("es_" + k, e / 1e6); NUM("cov_" + k, S0 / v); NUM("p_neg_" + k, 100 * ((dS + S0) < 0).mean())
print(pd.DataFrame(lignes, index=["gain espéré (M€)", "écart-type (M€)", "VaR 99,5 % (M€)", "ES 99 % (M€)",
                                  "surplus initial / VaR"]).T.to_string(float_format=lambda x: f"{x:g}"))
```
<!--sortie-->
```text
NUM var_mar 134.1491567818308
NUM es_mar 138.57008182863942
NUM cov_mar 0.3430703282995982
NUM p_neg_mar 17.36
NUM var_app 5.149561246166238
NUM es_app 5.858566366294979
NUM cov_app 8.937187666720154
NUM p_neg_app 0.0
NUM var_mix 40.809950530820274
NUM es_mix 42.072182975024475
NUM cov_mix 1.1277297487410585
NUM p_neg_mix 0.13999999999999999
NUM var_opt 18.499473855705833
NUM es_opt 19.137203432171088
NUM cov_opt 2.4877786047986503
NUM p_neg_opt 0.0
NUM var_mk 62.57615094648593
NUM es_mk 66.58164103694848
NUM cov_mk 0.7354654219243162
NUM p_neg_mk 3.0
                       gain espéré (M€)  écart-type (M€)  VaR 99,5 % (M€)  ES 99 % (M€)  surplus initial / VaR
Marché                              9.5             58.2            134.1         138.6                   0.34
Apparié                             0.4                2              5.1           5.9                   8.94
Mixte                               3.7             18.2             40.8          42.1                   1.13
Optimisé (10 M€)                    3.7               10             18.5          19.1                   2.49
Markowitz sans passif              -0.8             22.2             62.6          66.6                   0.74
```

Le même bilan, avec le même surplus initial de 46 M€, donne des diagnostics opposés :

- avec l'allocation « Marché » (45 % d'actions, 15 % d'immobilier, 40 % d'obligations à 5 ans), la perte à 99,5 % est de **134 M€**, soit 2,9 fois le surplus : un tel assureur est **insolvable** au sens de Solvabilité sur ce modèle jouet (surplus / VaR = 0,34) ;
- avec l'allocation « Apparié », elle est de **5,1 M€** (surplus / VaR = 8,9) ;
- avec l'allocation « Mixte » (80 % apparié, 20 % d'actifs risqués), de 41 M€ (1,1 fois couvert) ;
- le portefeuille « Markowitz sans passif », qui minimise le risque de l'actif, perd jusqu'à 63 M€ pour un gain espéré **négatif** (-0,8 M€) : il est 12 fois plus risqué que l'allocation « Apparié », alors qu'il est le moins risqué **des actifs**.

```python hide
NUM("cov_inv_mar", 1 / (S0 / O.var_es(X @ pf["Marché"] - dliab)[0]))
NUM("gain_mk", (X @ pf["Markowitz sans passif"] - dliab).mean() / 1e6)
NUM("rapport_var_mk", O.var_es(X @ pf["Markowitz sans passif"] - dliab)[0] / O.var_es(X @ pf["Apparié"] - dliab)[0])
```
<!--sortie-->
```text
NUM cov_inv_mar 2.9148542369036208
NUM gain_mk -0.8348007625472512
NUM rapport_var_mk 12.151744188511755
```

Une VaR estimée sur 5 000 tirages repose sur une **queue de 25 observations** à 99,5 % : elle est incertaine. Deux sources d'incertitude se distinguent : l'**erreur de tirage** (on aurait pu tirer d'autres scénarios dans le même historique), qui diminue quand on tire davantage ; et l'**erreur d'historique** (on n'a observé que 119 variations mensuelles de taux), qui ne diminue pas. On les mesure par **rééchantillonnage** (*bootstrap*).

```python hide-code
import copy
rng_b = np.random.default_rng(5)
wmix = pf["Mixte"]
dS_mix = X @ wmix - dliab
bs = [O.var_es(dS_mix[rng_b.integers(0, len(dS_mix), len(dS_mix))])[0] / 1e6 for _ in range(300)]
lo, hi = np.percentile(bs, [2.5, 97.5])
bs2 = []
for r_ in range(200):
    b2 = copy.copy(b); b2.dC = b.dC[rng_b.integers(0, len(b.dC), len(b.dC))]
    dY2, ann2 = O.tirages_annuels(b2, 2000, 1000 + r_)
    X2, dl2 = O.pnl_instruments(b2, dY2, ann2)
    bs2.append(O.var_es(X2 @ wmix - dl2)[0] / 1e6)
lo2, hi2 = np.percentile(bs2, [2.5, 97.5])
print(f"VaR 99,5 % de l'allocation Mixte : {O.var_es(dS_mix)[0]/1e6:.1f} M€")
print(f"intervalle à 95 %, erreur de tirage seule         : [{lo:.1f} ; {hi:.1f}]")
print(f"intervalle à 95 %, historique des taux rééchantillonné : [{lo2:.1f} ; {hi2:.1f}]")
NUM("var_mix_lo", lo); NUM("var_mix_hi", hi); NUM("var_mix_lo2", lo2); NUM("var_mix_hi2", hi2)
```
<!--sortie-->
```text
VaR 99,5 % de l'allocation Mixte : 40.8 M€
intervalle à 95 %, erreur de tirage seule         : [39.0 ; 42.3]
intervalle à 95 %, historique des taux rééchantillonné : [34.8 ; 46.8]
NUM var_mix_lo 39.014770999564675
NUM var_mix_hi 42.32436470195427
NUM var_mix_lo2 34.78396059254116
NUM var_mix_hi2 46.79178291894242
```

L'erreur de tirage seule donne un intervalle étroit (de 39 à 42 M€ pour une estimation de 41 M€). Mais si l'on rééchantillonne aussi l'**historique des taux**, l'intervalle s'élargit à [35 ; 47] M€ : la seconde source d'incertitude domine. Et aucun de ces intervalles ne mesure l'**erreur de modèle** (taux et actions indépendants, passif fixe). À 99,5 %, **ne jamais présenter la VaR sans son incertitude**.

```python hide
fig, axs = plt.subplots(1, 3, figsize=(9.6, 3.3), sharex=True)
for ax, nom, col in zip(axs, ("Marché", "Mixte", "Apparié"), (ORANGE, VIOLET, AQUA)):
    d_ = (X @ pf[nom] - dliab) / 1e6
    ax.hist(d_, bins=60, color=col, alpha=0.8)
    v, e = O.var_es(X @ pf[nom] - dliab)
    ax.axvline(-v / 1e6, color=ENCRE2, lw=1.2, ls="--"); ax.axvline(-S0 / 1e6, color=ROUGE, lw=1.2)
    ax.set_title(nom, fontsize=10); ax.set_xlabel("variation du surplus (M€)")
axs[0].set_ylabel("scénarios")
axs[0].text(-S0 / 1e6, axs[0].get_ylim()[1] * 0.92, " − surplus initial", color=ROUGE, fontsize=7, ha="right")
style.save(fig, "ch07-var-surplus.png")
```
<!--sortie-->
```text
figure : ch07-var-surplus.png
```

![Distribution de la variation annuelle du surplus (5 000 scénarios) pour trois allocations. Trait pointillé : −VaR à 99,5 % ; trait rouge : le surplus initial, qu'une perte supérieure efface. À gauche (« Marché »), la queue dépasse le surplus ; à droite (« Apparié »), la distribution est étroite autour de zéro.](figures/ch07-var-surplus.png)

> 📐 **Pourquoi la VaR du surplus n'est pas la VaR de l'actif.** La VaR de l'actif dit combien l'on peut perdre sur les placements. Celle du surplus dit combien l'on peut perdre **de marge de manœuvre** : une baisse des taux qui fait perdre 5 % à l'actif obligataire n'est pas un risque si elle fait gagner 5 % au passif. Les cadres réglementaires (chapitre 4) raisonnent sur le surplus, pas sur l'actif.

### 7.3.4 Une simulation sur dix ans

Le risque sur un an ne dit pas ce qui se passe sur le long terme : le passif se paie, les taux dérivent, les marchés ont des cycles. On simule donc dix années de plus : à chaque année, la courbe des taux évolue (tirage de douze variations mensuelles de l'historique, courbe positive), les actifs gagnent un rendement annuel tiré dans l'historique, la prestation de l'année est payée par les actifs, le passif restant est **revalorisé** sur la nouvelle courbe. On suit le **taux de couverture** A_k/L_k : il passe sous 1 quand l'actif ne suffit plus à couvrir le passif.

```python hide-code
alm = {}
for nom, w in {"Marché": strat["Marché"], "Apparié": strat["Apparié"], "Mixte": strat["Mixte"]}.items():
    alm[nom] = O.simuler_alm(b, w, N=2000, annees=10, seed=11)
lignes = {}
for nom, FR in alm.items():
    lignes[nom] = [round(np.median(FR[:, 10]), 2), round(np.quantile(FR[:, 10], 0.05), 2),
                   round(100 * (FR[:, 10] < 1).mean(), 1), round(100 * (FR.min(axis=1) < 1).mean(), 1)]
    K_ = KEY[nom]
    NUM("med_" + K_, np.median(FR[:, 10])); NUM("q05_" + K_, np.quantile(FR[:, 10], 0.05))
    NUM("pfin_" + K_, 100 * (FR[:, 10] < 1).mean()); NUM("pjam_" + K_, 100 * (FR.min(axis=1) < 1).mean())
print(pd.DataFrame(lignes, index=["médiane A/L à 10 ans", "5e percentile", "P(A/L < 1 à 10 ans) %", "P(A/L < 1 un jour) %"]).T.to_string(float_format=lambda x: f"{x:g}"))
```
<!--sortie-->
```text
NUM med_mar 1.3818214774806274
NUM q05_mar 0.6501620710381487
NUM pfin_mar 21.8
NUM pjam_mar 48.449999999999996
NUM med_app 1.1428602620319577
NUM q05_app 1.0706587331224326
NUM pfin_app 0.25
NUM pjam_app 0.25
NUM med_mix 1.243340036494016
NUM q05_mix 0.9766938092546391
NUM pfin_mix 6.65
NUM pjam_mix 14.000000000000002
         médiane A/L à 10 ans  5e percentile  P(A/L < 1 à 10 ans) %  P(A/L < 1 un jour) %
Marché                   1.38           0.65                   21.8                  48.4
Apparié                  1.14           1.07                    0.2                   0.2
Mixte                    1.24           0.98                    6.6                    14
```

Résultats pour un taux de couverture initial de 1,10 :

- l'allocation « Marché » a la **meilleure médiane** (1,38) et la pire queue : dans 48 % des trajectoires, le taux de couverture passe sous 1 au moins une fois, et dans 22 % il est encore sous 1 à dix ans ;
- l'allocation « Apparié » a une médiane plus faible (1,14) mais **presque aucun risque** (P(A/L < 1 un jour) = 0,2 %) ;
- l'allocation « Mixte » est intermédiaire : médiane 1,24, probabilité de passer sous 1 un jour de 14 %.

```python hide
NUM("couv_init", b.A0 / b.L0)
fig, axs = plt.subplots(1, 3, figsize=(9.8, 3.4), sharey=True)
for ax, (nom, FR), col in zip(axs, alm.items(), (ORANGE, AQUA, VIOLET)):
    an = np.arange(11)
    q = np.quantile(FR, [0.05, 0.25, 0.5, 0.75, 0.95], axis=0)
    ax.fill_between(an, q[0], q[4], color=col, alpha=0.18); ax.fill_between(an, q[1], q[3], color=col, alpha=0.30)
    ax.plot(an, q[2], color=col); ax.axhline(1, color=ROUGE, lw=1.0)
    ax.set_title(nom, fontsize=10); ax.set_xlabel("année")
axs[0].set_ylabel("taux de couverture A / L"); axs[0].set_ylim(0.4, 2.6)
for ax in axs:
    ax.set_xticks(range(0, 11, 2))
style.save(fig, "ch07-alm-dix-ans.png")
```
<!--sortie-->
```text
NUM couv_init 1.1
figure : ch07-alm-dix-ans.png
```

![Taux de couverture (actif / passif) sur dix ans, 2 000 trajectoires simulées, pour trois allocations : médiane (trait), intervalle interquartile (bande foncée) et intervalle 5–95 % (bande claire). La ligne rouge est le seuil de couverture 1.](figures/ch07-alm-dix-ans.png)

Enfin, **le surplus initial est une assurance**. On refait la simulation de l'allocation « Mixte » avec un surplus initial de 5 %, 10 % et 20 % du passif :

```python hide-code
lignes = {}
for s_ in (0.05, 0.10, 0.20):
    bb = O.Bilan(surplus=s_)
    wmix = {k: 0.8 * v for k, v in bb.poids_zc().items()} | {"act": 0.14, "imm": 0.06}
    FR = O.simuler_alm(bb, wmix, N=2000, annees=10, seed=11)
    lignes[f"{100*s_:.0f} %"] = [round(100 * (FR.min(axis=1) < 1).mean(), 1), round(np.median(FR[:, 10]), 2)]
    NUM(f"pjam_s{int(100*s_)}", 100 * (FR.min(axis=1) < 1).mean())
print(pd.DataFrame(lignes, index=["P(A/L < 1 un jour) %", "médiane A/L à 10 ans"]).T.to_string(float_format=lambda x: f"{x:g}"))
```
<!--sortie-->
```text
NUM pjam_s5 33.95
NUM pjam_s10 14.000000000000002
NUM pjam_s20 1.8499999999999999
      P(A/L < 1 un jour) %  médiane A/L à 10 ans
5 %                     34                  1.16
10 %                    14                  1.24
20 %                   1.8                  1.41
```

La probabilité de passer sous 1 un jour tombe de 34 % (surplus initial de 5 %) à 1,8 % (20 %) : **le capital est le dernier rempart quand la gestion actif-passif n'a pas tout couvert**, ce qui est l'esprit des exigences de fonds propres du chapitre 4.

### 7.3.5 Ce que le modèle ne sait pas faire

Il faut être aussi précis sur les limites que sur les résultats. Les chiffres de cette section dépendent d'hypothèses qui sont **toutes contestables** :

- **Les taux et les actions sont indépendants** dans les données (simulées séparément). Dans la réalité, ils sont corrélés, et cette corrélation peut changer de signe selon l'époque : elle modifie la VaR du surplus, dans un sens ou dans l'autre.
- **Les scénarios sont tirés dans un historique de 10 ans pour les taux et de 16 ans pour les marchés.** Un rééchantillonnage ne crée aucun événement qui ne soit déjà dans l'historique. Le cycle de hausse des taux du mois 60 au mois 90 est le pire mouvement du jeu ; un pire existe sans doute (section 3.2).
- **Le passif est fixe.** Pas de rachats (qui dépendent des taux), pas de garanties de taux, pas d'amélioration de la longévité, pas de frais. Ces ingrédients rendent le passif **optionnel**, et les durations, calculées sur des flux fixes, fausses.
- **Pas de risque de crédit ni d'écart de crédit** : les obligations sont des zéro-coupons sans défaut.
- **Pas de coûts de transaction ni de rééquilibrage dynamique** : les portefeuilles sont rééquilibrés sans frais chaque année.
- **Les rendements espérés sont historiques** et donc bruités (section 7.2.6).
- **La VaR est une convention** : un seuil à 99,5 % sur un an, avec des intervalles d'incertitude larges (section 7.3.3).

Un modèle ALM réel est calibré sur des scénarios économiques générés (modèles de taux, d'actions et d'inflation corrélés), validé de façon indépendante (section 3.4) et revu chaque année. Le but de ce chapitre n'était pas d'en fournir un, mais de faire comprendre **pourquoi** ils sont construits comme ils le sont.

> ✅ **À retenir.** (1) Le critère est le risque du **surplus**, pas celui de l'actif : le portefeuille de variance minimale de l'actif peut être le pire pour le surplus. (2) Le meilleur actif pour un passif est celui qui le **réplique** ; le risque s'ajoute ensuite comme un « dial » dont le gain espéré croît bien plus lentement que le risque. (3) La VaR et l'ES du surplus mesurent la perte de marge de manœuvre ; leur estimation à 99,5 % est incertaine. (4) Sur dix ans, le surplus initial et l'appariement protègent ; l'allocation « de marché » a la meilleure médiane et la pire queue. (5) Toutes ces conclusions dépendent d'hypothèses de modèle (indépendance, passif fixe, historique court) qu'il faut écrire et contester.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.8 et exercice 7.11.
