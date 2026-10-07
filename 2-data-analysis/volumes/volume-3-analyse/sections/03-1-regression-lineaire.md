## 3.1 Régression linéaire pour expliquer et estimer

Cette section construit la régression pas à pas : d'abord une droite sur six points que l'on calcule à la main, puis un modèle à plusieurs variables sur les 1 090 jours de la boutique, avec ses précautions d'emploi. Le fil rouge est la question de la gérante : *que fait la promotion, que fait la publicité, toutes choses égales par ailleurs ?*

### 3.1.1 Une droite qui passe « au mieux » parmi les points

Reprenons les six jours du volume I (section 1.4.1) : la dépense publicitaire $x$ (en euros) et le nombre de commandes $y$ des six premiers jours de novembre 2025 à partir du lundi 3. Le nuage est dispersé ; on veut pourtant une **règle** qui, à une dépense, associe un nombre de commandes **attendu**. La plus simple est une droite :

$$\hat y = a + b\,x .$$

Il y a une infinité de droites. La régression retient celle qui **se trompe le moins**, au sens suivant : pour chaque jour, on mesure l'écart vertical $e_i=y_i-\hat y_i$ entre le point et la droite (le **résidu**), et l'on choisit $a$ et $b$ qui minimisent la somme des **carrés** de ces écarts. C'est la méthode des **moindres carrés**. Pourquoi des carrés ? Parce qu'ils empêchent les écarts positifs et négatifs de s'annuler, et parce qu'ils punissent davantage les grosses erreurs. La solution s'écrit avec les mêmes sommes que la corrélation :

$$b=\frac{\sum (x_i-\bar x)(y_i-\bar y)}{\sum (x_i-\bar x)^2}=\frac{S_{xy}}{S_{xx}},\qquad a=\bar y-b\,\bar x .$$

La droite passe toujours par le point moyen $(\bar x,\bar y)$, et sa **pente** $b$ est la covariance divisée par la variance de $x$. Avec les sommes du volume I ($S_{xy}=2\,948{,}7$, $S_{xx}=74\,298{,}8$, $\bar x=395{,}2$ et $\bar y=46{,}3$) :

$$b=\frac{2\,948{,}7}{74\,298{,}8}\approx 0,0397\ \text{commande par euro},\qquad a=46{,}3-0,0397\times395{,}2\approx 30,7.$$

Soit une prévision de 30,7 commandes pour une dépense nulle, plus 4,0 commandes pour chaque centaine d'euros dépensés. Le tableau suivant donne, pour chaque jour, la valeur prévue et le résidu.

```python hide-code
x6 = np.array([242, 358, 374, 583, 325, 489.]); y6 = np.array([32, 45, 32, 41, 58, 70.])
chk = jr[jr["date"] >= "2025-11-03"].head(6)
assert np.allclose(chk["depense_pub"].round(0).values, x6) and (chk["nb_commandes"].values == y6).all()
sxy, sxx = ((x6 - x6.mean()) * (y6 - y6.mean())).sum(), ((x6 - x6.mean()) ** 2).sum()
b6 = sxy / sxx; a6 = y6.mean() - b6 * x6.mean()
fit6 = a6 + b6 * x6; res6 = y6 - fit6
r2_6 = 1 - (res6 ** 2).sum() / ((y6 - y6.mean()) ** 2).sum()
tab6 = pd.DataFrame({"x (pub, €)": x6.astype(int), "y (commandes)": y6.astype(int), "prévu": fit6.round(1), "résidu e": res6.round(1), "e au carré": (res6 ** 2).round(1)})
print(tab6.to_string(index=False))
print("somme des carrés des résidus :", round((res6 ** 2).sum(), 1), "| somme des résidus :", round(res6.sum(), 1))
NUM("pente6", round(b6, 6)); NUM("ord6", round(a6, 3)); NUM("pente6x100", round(b6 * 100, 3)); NUM("r2_6", round(r2_6, 4))
NUM("ssr6", round((res6 ** 2).sum(), 1)); NUM("sst6", round(((y6 - y6.mean()) ** 2).sum(), 1))
assert round(sxy, 1) == 2948.7 and round(sxx, 1) == 74298.8
```
<!--sortie-->
```text
 x (pub, €)  y (commandes)  prévu  résidu e  e au carré
        242             32   40.3      -8.3        68.1
        358             45   44.9       0.1         0.0
        374             32   45.5     -13.5       182.1
        583             41   53.8     -12.8       163.5
        325             58   43.5      14.5       208.8
        489             70   50.1      19.9       397.7
somme des carrés des résidus : 1020.3 | somme des résidus : -0.0
NUM pente6 0.039687
NUM ord6 30.651
NUM pente6x100 3.969
NUM r2_6 0.1029
NUM ssr6 1020.3
NUM sst6 1137.3
```

Deux remarques. D'abord, **les résidus s'annulent** (leur somme vaut zéro) : c'est une propriété de la droite des moindres carrés, pas un hasard. Ensuite, la somme des carrés des résidus vaut 1020,3, à comparer à la variabilité totale des commandes autour de leur moyenne, $\sum (y_i-\bar y)^2=1137{,}3$. Le rapport mesure ce que la droite a **expliqué** :

$$R^2=1-\frac{\sum e_i^2}{\sum (y_i-\bar y)^2}=1-\frac{1020,3}{1137,3}\approx 0,103 .$$

Le $R^2$ est la part de la variabilité de $y$ que le modèle reproduit. Ici, 10% : la dépense publicitaire explique **un dixième** des écarts entre ces six jours, et c'est exactement le carré de la corrélation trouvée au volume I (0,32). Une pente positive, un $R^2$ modeste, six points : on ne peut rien conclure, et la section suivante apprend à le dire avec des chiffres.

![Six jours de novembre : dépense publicitaire et commandes, droite des moindres carrés et résidus (segments verticaux).](figures/ch03-moindres-carres.png)

```python hide
fig, ax = plt.subplots(figsize=(6.4, 3.6))
ax.scatter(x6, y6, color=BLEU, zorder=3, s=36)
xx = np.linspace(200, 620, 50); ax.plot(xx, a6 + b6 * xx, color=ORANGE, lw=1.8)
for xi, yi, fi in zip(x6, y6, fit6):
    ax.plot([xi, xi], [yi, fi], color=MUET, lw=1.0, ls="--")
ax.axhline(y6.mean(), color=MUET, lw=0.8, alpha=0.6); ax.text(205, y6.mean() + 1.2, "moyenne des commandes", fontsize=8, color=MUET)
ax.set_xlabel("Dépense publicitaire du jour (€)"); ax.set_ylabel("Commandes du jour")
ax.set_title("La droite qui minimise la somme des carrés des écarts", loc="left")
fig.savefig("figures/ch03-moindres-carres.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

Le même calcul, fait sur les 1 090 jours de la boutique, se réduit à un appel de bibliothèque. Nous régressons le nombre de commandes sur la dépense publicitaire **du jour**.

```python
naif = smf.ols("nb_commandes ~ depense_pub", data=jr).fit()      # y ~ x : une droite
print(naif.summary2().tables[1].round(3))
print("R2 =", round(naif.rsquared, 3), "| R2 ajusté =", round(naif.rsquared_adj, 3), "| n =", int(naif.nobs))
```
<!--sortie-->
```text
              Coef.  Std.Err.       t  P>|t|  [0.025  0.975]
Intercept    20.658     0.700  29.530    0.0  19.285  22.031
depense_pub   0.061     0.003  20.528    0.0   0.055   0.066
R2 = 0.279 | R2 ajusté = 0.279 | n = 1090
```

```python hide
NUM("naif_pente", round(naif.params["depense_pub"], 4)); NUM("naif_ord", round(naif.params["Intercept"], 2)); NUM("naif_r2", round(naif.rsquared, 3))
NUM("naif_pente100", round(naif.params["depense_pub"] * 100, 2)); NUM("naif_se", round(naif.bse["depense_pub"], 4)); NUM("naif_lo", round(naif.conf_int().loc["depense_pub", 0], 4)); NUM("naif_hi", round(naif.conf_int().loc["depense_pub", 1], 4))
NUM("naif_t", round(naif.tvalues["depense_pub"], 1)); NUM("naif_r2aj", round(naif.rsquared_adj, 3))
```
<!--sortie-->
```text
NUM naif_pente 0.0605
NUM naif_ord 20.66
NUM naif_r2 0.279
NUM naif_pente100 6.05
NUM naif_se 0.0029
NUM naif_lo 0.0547
NUM naif_hi 0.0663
NUM naif_t 20.5
NUM naif_r2aj 0.279
```

### 3.1.2 Lire un tableau de résultats

Le tableau précédent contient, pour chaque coefficient, six nombres. Les connaître tous, et savoir à quoi ils servent, est la première compétence d'un analyste qui utilise une régression.

- **`Coef.`** : l'estimation. La pente vaut 0,0605 : en moyenne, **un euro de publicité de plus le même jour s'accompagne de 0,060 commande de plus**, soit environ 6,0 commandes pour 100 €. L'ordonnée (20,7) est le nombre de commandes attendu pour une dépense nulle.
- **`Std.Err.`** : l'**erreur type**, c'est-à-dire l'incertitude de l'estimation due à l'échantillon (volume I, section 1.3). Plus il y a de jours, plus elle est petite ; plus les points sont dispersés, plus elle est grande. Ici, 0,0029.
- **`t`** : le coefficient divisé par son erreur type (20,5). Ordre de grandeur utile : un $|t|$ supérieur à 2 signale un coefficient que le hasard d'échantillonnage explique mal.
- **`P>|t|`** : la **p-valeur** : la probabilité d'obtenir un coefficient au moins aussi éloigné de zéro **si** l'effet réel était nul. Elle est ici indiquée comme nulle (en réalité inférieure à 0,0005). Attention : elle ne dit ni si l'effet est grand, ni s'il est causal.
- **`[0.025 ; 0.975]`** : l'**intervalle de confiance à 95 %** : de 0,0547 à 0,0663. C'est le nombre le plus utile à montrer à la gérante, parce qu'il dit **de combien l'estimation peut se tromper**.

Sous le tableau, deux mesures de qualité globale. Le **$R^2$** (0,279) est la part de la variabilité des commandes reproduite par la droite. Le **$R^2$ ajusté** (0,279) corrige le $R^2$ du fait qu'ajouter une variable, même absurde, le fait toujours monter : on retire une pénalité qui dépend du nombre de variables $p$,

$$R^2_{\text{ajusté}}=1-(1-R^2)\,\frac{n-1}{n-p-1}.$$

Avec 1 090 jours et une seule variable, la correction est minuscule ; elle devient importante quand on ajoute des dizaines de variables (nous allons le faire).

> 💡 **Intuition.** Une régression est un **résumé** : elle remplace un nuage de points par une règle et un ordre de grandeur de ses erreurs. L'erreur type et l'intervalle de confiance répondent à « si j'avais observé d'autres jours, de combien le coefficient aurait-il changé ? ». Le $R^2$, lui, répond à une question différente : « de combien le modèle réduit-il l'incertitude sur les commandes d'un jour donné ? ». Un coefficient peut être très **précis** (petit intervalle) et un $R^2$ pourtant **faible**.

La droite ci-dessus affirme que la publicité fait gagner 6,0 commandes par centaine d'euros. Hélas, c'est le **même** piège que celui de la section 1.4.3 du volume I, et nous allons le défaire en ajoutant des variables.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1 et exercices 3.1 à 3.3.

### 3.1.3 Passer à plusieurs variables : « toutes choses égales par ailleurs »

Quand on ajoute des variables explicatives, la droite devient un modèle à plusieurs entrées :

$$y = \beta_0+\beta_1x_1+\beta_2x_2+\dots+\beta_px_p+\varepsilon .$$

Chaque coefficient $\beta_k$ se lit alors **« toutes choses égales par ailleurs »** : c'est la variation moyenne de $y$ quand $x_k$ augmente d'une unité **et que toutes les autres variables du modèle restent fixes**. C'est l'idée qui répond à la gérante : comparer des jours de promotion et des jours sans promotion **qui se ressemblent par ailleurs** (même jour de la semaine, même mois, même tendance), au lieu de comparer des soldes de janvier à des journées de décembre.

Nous utiliserons une variable plus parlante que la dépense du jour : la **dépense des sept derniers jours** `pub_hebdo`, en milliers d'euros (une publicité agit plus qu'un jour). Nous prenons aussi le **logarithme** des commandes comme grandeur à expliquer, ce qui permettra de lire les coefficients en pourcentage (section 3.1.5). Le modèle complet est le suivant ; la syntaxe « formule » de `statsmodels` s'écrit presque comme l'équation.

```python
f = "np.log(nb_commandes) ~ promo_active + pub_hebdo + pluie_jour + C(jour_semaine) + C(mois) + t"
mod = smf.ols(f, data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})   # erreurs robustes (section 3.1.7)
cle = ["promo_active", "pub_hebdo", "pluie_jour", "t"]
print(mod.summary2().tables[1].loc[cle, ["Coef.", "Std.Err.", "[0.025", "0.975]"]].round(3))
print("R2 =", round(mod.rsquared, 3), "| R2 ajusté =", round(mod.rsquared_adj, 3))
```
<!--sortie-->
```text
              Coef.  Std.Err.  [0.025  0.975]
promo_active  0.175     0.025   0.127   0.224
pub_hebdo     0.001     0.027  -0.052   0.055
pluie_jour   -0.017     0.011  -0.039   0.005
t             0.063     0.006   0.051   0.075
R2 = 0.777 | R2 ajusté = 0.772
```

```python hide
mco = smf.ols(f, data=jr).fit()                       # mêmes coefficients, erreurs types classiques
ic = mod.conf_int()
NUM("promo_pct", round(O.pct(mod.params["promo_active"]), 1)); NUM("promo_lo", round(O.pct(ic.loc["promo_active", 0]), 1)); NUM("promo_hi", round(O.pct(ic.loc["promo_active", 1]), 1))
NUM("pub_pct", round(O.pct(mod.params["pub_hebdo"]), 2)); NUM("pub_lo", round(O.pct(ic.loc["pub_hebdo", 0]), 1)); NUM("pub_hi", round(O.pct(ic.loc["pub_hebdo", 1]), 1))
NUM("pluie_pct", round(O.pct(mod.params["pluie_jour"]), 1)); NUM("pluie_lo", round(O.pct(ic.loc["pluie_jour", 0]), 1)); NUM("pluie_hi", round(O.pct(ic.loc["pluie_jour", 1]), 1))
NUM("trend_pct", round(O.pct(mod.params["t"]), 1)); NUM("r2", round(mod.rsquared, 3)); NUM("r2aj", round(mod.rsquared_adj, 3)); NUM("n_param", len(mod.params))
NUM("promo_coef", round(mod.params["promo_active"], 3)); NUM("promo_p", round(mod.pvalues["promo_active"], 6)); NUM("pub_coef", round(mod.params["pub_hebdo"], 4)); NUM("pub_p", round(mod.pvalues["pub_hebdo"], 2))
NUM("pub_hebdo_sd", round(jr["pub_hebdo"].std(), 2)); NUM("pub_hebdo_min", round(jr["pub_hebdo"].min(), 2)); NUM("pub_hebdo_max", round(jr["pub_hebdo"].max(), 2))
```
<!--sortie-->
```text
NUM promo_pct 19.2
NUM promo_lo 13.5
NUM promo_hi 25.1
NUM pub_pct 0.14
NUM pub_lo -5.1
NUM pub_hi 5.7
NUM pluie_pct -1.7
NUM pluie_lo -3.8
NUM pluie_hi 0.5
NUM trend_pct 6.5
NUM r2 0.777
NUM r2aj 0.772
NUM n_param 22
NUM promo_coef 0.175
NUM promo_p 0.0
NUM pub_coef 0.0014
NUM pub_p 0.96
NUM pub_hebdo_sd 0.68
NUM pub_hebdo_min 0.67
NUM pub_hebdo_max 3.7
```

Les quatre lignes affichées sont les **effets d'intérêt**. Le tableau complet compte 22 coefficients, car il contient aussi les jours de la semaine et les mois (section 3.1.4). Lisons-les en pourcentage (nous verrons au 3.1.5 pourquoi $e^{\beta}-1$) :

- **La promotion** : +19,2 % de commandes les jours de promotion, avec un intervalle de confiance de +13,5 % à +25,1 %. L'effet est net : l'intervalle est loin de zéro.
- **La publicité** : +0,14 % de commandes pour 1 000 € dépensés de plus sur la semaine, avec un intervalle de -5,1 % à +5,7 %. L'intervalle **contient zéro** : le modèle **ne détecte pas** d'effet de la publicité. Ce n'est pas la même chose que de dire qu'il n'y en a pas, nous y reviendrons.
- **La pluie** : -1,7 % de commandes les jours de pluie, intervalle de -3,8 % à +0,5 % : plutôt négatif, mais proche de ce que le hasard peut produire.
- **Le temps** (en années) : +6,5 % de commandes par an, toutes choses égales par ailleurs : la tendance de fond de la boutique.

Le modèle explique 78% de la variabilité du logarithme des commandes (le $R^2$ ajusté est de 0,772). Mais voyons surtout ce qui s'est passé pour la publicité : la droite de la section précédente promettait une forte hausse, et le modèle complet ne trouve plus rien. Pour le comprendre, construisons le modèle **marche par marche**.

```python hide
fA = "np.log(nb_commandes) ~ promo_active + pub_hebdo"
fB = fA + " + C(jour_semaine)"
fC = fB + " + C(mois)"
lignes = []
for nom, fm in [("A. promotion et publicité seules", fA), ("B. + jour de la semaine", fB), ("C. + mois", fC), ("D. + pluie et tendance (modèle complet)", f)]:
    m = smf.ols(fm, data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
    lignes.append((nom, O.pct(m.params["promo_active"]), O.pct(m.params["pub_hebdo"]), O.pct(m.conf_int().loc["pub_hebdo", 0]), O.pct(m.conf_int().loc["pub_hebdo", 1]), m.rsquared))
marches = pd.DataFrame(lignes, columns=["modèle", "promo", "pub", "pub_lo", "pub_hi", "r2"])
for i, cle_ in enumerate("ABCD"):
    NUM(f"mA_promo".replace("A", cle_), round(marches.loc[i, "promo"], 1)); NUM(f"mA_pub".replace("A", cle_), round(marches.loc[i, "pub"], 1)); NUM(f"mA_r2".replace("A", cle_), round(marches.loc[i, "r2"], 2))
```
<!--sortie-->
```text
NUM mA_promo 2.4
NUM mA_pub 31.4
NUM mA_r2 0.25
NUM mB_promo 2.0
NUM mB_pub 31.5
NUM mB_r2 0.57
NUM mC_promo 18.8
NUM mC_pub -0.2
NUM mC_r2 0.76
NUM mD_promo 19.2
NUM mD_pub 0.1
NUM mD_r2 0.78
```

```python hide-code
t = marches.copy()
t["promo"] = t["promo"].map("{:+.1f} %".format); t["pub"] = t["pub"].map("{:+.1f} %".format)
t["pub (IC 95 %)"] = [f"[{lo:+.1f} ; {hi:+.1f}]" for lo, hi in zip(marches["pub_lo"], marches["pub_hi"])]
t["R2"] = t["r2"].map("{:.2f}".format)
print(t[["modèle", "promo", "pub", "pub (IC 95 %)", "R2"]].to_string(index=False))
```
<!--sortie-->
```text
                                 modèle   promo     pub   pub (IC 95 %)   R2
       A. promotion et publicité seules  +2.4 % +31.4 % [+25.7 ; +37.4] 0.25
                B. + jour de la semaine  +2.0 % +31.5 % [+25.9 ; +37.4] 0.57
                              C. + mois +18.8 %  -0.2 %   [-6.5 ; +6.6] 0.76
D. + pluie et tendance (modèle complet) +19.2 %  +0.1 %   [-5.1 ; +5.7] 0.78
```

C'est le résultat central de la section. Dans le modèle A, qui ne contrôle rien, **la publicité semble multiplier les commandes de +31 % par millier d'euros** hebdomadaire et **la promotion semble inutile** (+2,4 %). Chaque ajout de variable corrige un peu : le jour de la semaine (B) ne change presque rien, mais le **mois** (C) fait tout basculer. Pourquoi ? Parce que la dépense publicitaire est **plus forte en novembre-décembre et au printemps**, quand les ventes sont déjà hautes pour d'autres raisons, et que les promotions tombent dans les creux de janvier et de l'été : les comparer sans tenir compte du mois, c'est comparer des saisons, pas des effets.

> ⚠️ **Piège.** Un coefficient n'est jamais « l'effet de la variable » : c'est l'effet **conditionnel aux autres variables du modèle**. Changez la liste des variables, et le coefficient change, parfois de signe. Le choix des variables à contrôler est une décision d'analyste (il faut contrôler ce qui influence à la fois la cause supposée et le résultat, comme la saison), pas un détail technique.

![Effet estimé de la publicité (par millier d'euros hebdomadaire) et de la promotion, selon les variables de contrôle ajoutées.](figures/ch03-marche-par-marche.png)

```python hide
fig, axs = plt.subplots(1, 2, figsize=(9, 3.4), sharey=False)
noms = ["A", "B", "C", "D"]
axs[0].bar(noms, marches["pub"], color=[ROUGE, MUET, MUET, BLEU]); axs[0].axhline(0, color=ENCRE2, lw=0.8)
axs[0].errorbar(noms, marches["pub"], yerr=[marches["pub"] - marches["pub_lo"], marches["pub_hi"] - marches["pub"]], fmt="none", ecolor=ENCRE2, lw=1, capsize=3)
axs[0].set_title("Effet de la publicité (% par k€ hebdo.)", loc="left", fontsize=10); axs[0].set_xlabel("modèle")
axs[1].bar(noms, marches["promo"], color=[ROUGE, MUET, MUET, BLEU]); axs[1].axhline(0, color=ENCRE2, lw=0.8)
axs[1].set_title("Effet de la promotion (%)", loc="left", fontsize=10); axs[1].set_xlabel("modèle")
for i, v in enumerate(marches["pub"]):
    axs[0].text(i, marches["pub_hi"].iloc[i] + 1.5, f"{v:+.1f}".replace(".", ","), ha="center", fontsize=8)
for i, v in enumerate(marches["promo"]):
    axs[1].text(i, v + 0.5, f"{v:+.1f}".replace(".", ","), ha="center", fontsize=8)
axs[0].set_ylim(-10, 44); axs[1].set_ylim(0, 22)
fig.savefig("figures/ch03-marche-par-marche.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

### 3.1.4 Les variables qualitatives : jours, mois, canaux

Le jour de la semaine et le mois sont des **catégories**, pas des quantités : le jour « 6 » n'est pas « deux fois » le jour « 3 ». La formule `C(jour_semaine)` demande à `statsmodels` de créer, pour chaque catégorie sauf une, une variable **indicatrice** valant 1 si le jour est de cette catégorie et 0 sinon. La catégorie omise est la **référence** (ici le lundi, jour 1, et janvier) : chaque coefficient se lit **par rapport à elle**.

| jour | coefficient (log) | effet par rapport au lundi |
|---|---:|---:|
| mardi (2) | -0,057 | -5,6 % |
| samedi (6) | +0,375 | +45,5 % |
| dimanche (7) | -0,366 | -30,7 % |

```python hide
def coef(nom): return mod.params[nom]
NUM("c_mar", round(coef("C(jour_semaine)[T.2]"), 3)); NUM("p_mar", round(O.pct(coef("C(jour_semaine)[T.2]")), 1))
NUM("c_sam", round(coef("C(jour_semaine)[T.6]"), 3)); NUM("p_sam", round(O.pct(coef("C(jour_semaine)[T.6]")), 1))
NUM("c_dim", round(coef("C(jour_semaine)[T.7]"), 3)); NUM("p_dim", round(O.pct(coef("C(jour_semaine)[T.7]")), 1))
NUM("c_dec", round(coef("C(mois)[T.12]"), 3)); NUM("p_dec", round(O.pct(coef("C(mois)[T.12]")), 1)); NUM("p_aout", round(O.pct(coef("C(mois)[T.8]")), 1))
NUM("n_dummies_jour", 6); NUM("n_dummies_mois", 11)
```
<!--sortie-->
```text
NUM c_mar -0.057
NUM p_mar -5.6
NUM c_sam 0.375
NUM p_sam 45.5
NUM c_dim -0.366
NUM p_dim -30.7
NUM c_dec 0.754
NUM p_dec 112.5
NUM p_aout -11.0
NUM n_dummies_jour 6
NUM n_dummies_mois 11
```

Un samedi apporte +45,5 % de commandes par rapport à un lundi, un dimanche -30,7 %, toutes choses égales par ailleurs ; décembre +112,5 % par rapport à janvier. Le choix de la référence ne change **pas** le modèle (les prévisions sont identiques), il change seulement la façon de lire les coefficients : prenez comme référence la catégorie la plus naturelle ou la plus fréquente.

Il y a deux pièges. Le premier est la **trappe aux variables indicatrices** : on ne peut pas inclure les sept jours **et** une constante, car leur somme égale toujours la constante (les colonnes seraient parfaitement redondantes) ; d'où le jour omis. Le second est de croire qu'un mois ou un jour « significatif » est une découverte : février et juillet n'ont pas de coefficient significatif par rapport à janvier, et c'est l'ensemble des mois qui compte (un test global, que `statsmodels` donne par `anova_lm`, répond à « le mois joue-t-il un rôle ? »).

Le canal (Boutique, Site, Réseaux) se traite de la même manière, et la section 3.3 en donnera un exemple sur les retours.

### 3.1.5 Les logarithmes : des effets en pourcentage et des élasticités

Pourquoi expliquer le **logarithme** des commandes plutôt que les commandes ? Parce qu'en entreprise, les effets sont presque toujours **proportionnels** : une promotion ne fait pas « 6 commandes de plus » tous les jours, elle fait « 19 % de plus », c'est-à-dire 6 un jour calme et 15 un jour chargé. Dans un modèle sur le logarithme, un coefficient $\beta$ se lit comme une variation relative :

$$\ln y=\beta_0+\beta_1x_1+\dots \;\Longrightarrow\; \text{quand }x_1\text{ augmente d'une unité, }y\text{ est multiplié par }e^{\beta_1}.$$

L'effet en pourcentage est donc $e^{\beta_1}-1$. Pour un petit coefficient, c'est presque $\beta_1$ lui-même (0,175 pour la promotion donne $e^{0{,}175}-1=19{,}2$ %, ce qui n'est pas tout à fait 0,175) ; pour un coefficient plus grand, l'écart se voit (décembre : coefficient 0,754, effet +112,5 %).

> 📐 **Pourquoi $e^{\beta}-1$.** Si $\ln y$ augmente de $\beta$, alors $y$ est multiplié par $e^{\beta}$ : le pourcentage de variation est $e^{\beta}-1$. Pour $\beta=0{,}1$ : $e^{0{,}1}=1{,}105$, soit $+10{,}5\ \%$ et non $+10\ \%$.

Si l'on prend aussi le logarithme de la variable explicative, le coefficient devient une **élasticité** : une variation de 1 % de $x$ s'accompagne d'une variation de $\beta$ % de $y$. Appliquons-le à la publicité (en remplaçant `pub_hebdo` par son logarithme) :

```python
mod_log = smf.ols(f.replace("pub_hebdo", "np.log(pub_hebdo)"), data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
el, (lo, hi) = mod_log.params["np.log(pub_hebdo)"], mod_log.conf_int().loc["np.log(pub_hebdo)"]
print("élasticité de la publicité :", round(el, 3), "| intervalle de confiance à 95 % :", round(lo, 3), "à", round(hi, 3))
```
<!--sortie-->
```text
élasticité de la publicité : -0.01 | intervalle de confiance à 95 % : -0.088 à 0.067
```

```python hide
NUM("el", round(el, 3)); NUM("el_lo", round(lo, 3)); NUM("el_hi", round(hi, 3))
```
<!--sortie-->
```text
NUM el -0.01
NUM el_lo -0.088
NUM el_hi 0.067
```

L'élasticité estimée est de -0,010 (intervalle de -0,088 à +0,067) : une dépense publicitaire 10 % plus élevée ne s'accompagne d'aucun effet détectable sur les commandes. L'intervalle va d'une légère baisse à une légère hausse : le message est le même que précédemment, **les données ne permettent pas de trancher**.

### 3.1.6 Les interactions : l'effet dépend-il du contexte ?

Jusqu'ici, l'effet de la promotion est supposé **identique** tous les jours de la semaine. Est-ce plausible ? Peut-être qu'une promotion « marche » mieux le week-end. On teste cette hypothèse par une **interaction** : on ajoute au modèle le produit de la promotion par le jour de la semaine, et l'on regarde si cet ajout **améliore** significativement le modèle.

```python
from statsmodels.stats.anova import anova_lm
mod_int = smf.ols(f.replace("promo_active", "promo_active * C(jour_semaine)"), data=jr).fit()
test_int = anova_lm(mco, mod_int)                  # F-test : l'interaction apporte-t-elle quelque chose ?
print("p-valeur du test d'interaction promotion x jour :", round(test_int["Pr(>F)"].iloc[1], 3))
```
<!--sortie-->
```text
p-valeur du test d'interaction promotion x jour : 0.152
```

```python hide
NUM("p_inter", round(test_int["Pr(>F)"].iloc[1], 3))
```
<!--sortie-->
```text
NUM p_inter 0.152
```

La p-valeur est de 0,15 : rien n'autorise à dire que la promotion agit différemment selon le jour. On garde donc le modèle simple, et c'est une règle de prudence : **ne pas ajouter d'interaction parce qu'on les trouve intéressantes**, mais parce qu'une raison métier ou un test l'exige. Chaque interaction ajoutée dépense de la précision et multiplie les résultats « significatifs par hasard » (si vous testez vingt interactions, une sera significative au seuil de 5 % même si aucune n'existe).

### 3.1.7 Vérifier le modèle : résidus, robustesse, colinéarité, points influents

Un modèle de régression repose sur des hypothèses. On ne les « démontre » pas, on les **inspecte** avec quatre contrôles, par ordre de gravité.

**1. Regarder les résidus.** Si le modèle est adapté, les résidus (écarts entre le réel et le prévu) n'ont **pas de structure** : pas de courbe, pas d'éventail. Le graphique des résidus contre les valeurs prévues est le contrôle le plus utile.

![À gauche, résidus du modèle complet contre valeurs prévues ; à droite, diagramme quantile-quantile des résidus.](figures/ch03-diagnostics.png)

```python hide
from statsmodels.stats.diagnostic import het_breuschpagan
from statsmodels.stats.stattools import durbin_watson
from statsmodels.stats.outliers_influence import variance_inflation_factor as vif
res = mco.resid; prev = mco.fittedvalues
fig, axs = plt.subplots(1, 2, figsize=(9, 3.4))
axs[0].scatter(prev, res, s=7, color=BLEU, alpha=0.5); axs[0].axhline(0, color=ORANGE, lw=1.2)
axs[0].set_xlabel("Valeur prévue (log des commandes)"); axs[0].set_ylabel("Résidu"); axs[0].set_title("Résidus et valeurs prévues", loc="left", fontsize=10)
import scipy.stats as st
th = st.norm.ppf((np.arange(1, len(res) + 1) - 0.5) / len(res)); axs[1].scatter(th, np.sort(res) / res.std(), s=7, color=BLEU, alpha=0.6)
axs[1].plot([-3, 3], [-3, 3], color=ORANGE, lw=1.2); axs[1].set_xlabel("Quantiles de la loi normale"); axs[1].set_ylabel("Quantiles des résidus (réduits)"); axs[1].set_title("Diagramme quantile-quantile", loc="left", fontsize=10)
fig.savefig("figures/ch03-diagnostics.png", dpi=200, bbox_inches="tight"); plt.close(fig)
bp = het_breuschpagan(res, mco.model.exog)[1]; dw = durbin_watson(res)
NUM("bp_p", round(bp, 4)); NUM("dw", round(dw, 2))
NUM("se_promo_cl", round(mco.bse["promo_active"], 4)); NUM("se_promo_hac", round(mod.bse["promo_active"], 4)); NUM("se_pub_cl", round(mco.bse["pub_hebdo"], 4)); NUM("se_pub_hac", round(mod.bse["pub_hebdo"], 4))
X = mco.model.exog; noms_x = mco.model.exog_names
NUM("vif_pub", round(vif(X, noms_x.index("pub_hebdo")), 1)); NUM("vif_promo", round(vif(X, noms_x.index("promo_active")), 1)); NUM("vif_t", round(vif(X, noms_x.index("t")), 1))
cd = mco.get_influence().cooks_distance[0]; top = np.argsort(cd)[-3:][::-1]
NUM("seuil_cook", round(4 / len(jr), 4)); NUM("cook_max", round(cd[top[0]], 3)); NUM("cook_date1", jr.loc[top[0], "date"].date()); NUM("cook_date2", jr.loc[top[1], "date"].date()); NUM("n_cook", int((cd > 4 / len(jr)).sum()))
NUM("cook_cmd1", int(jr.loc[top[0], "nb_commandes"]))
```
<!--sortie-->
```text
NUM bp_p 0.0001
NUM dw 1.99
NUM se_promo_cl 0.0215
NUM se_promo_hac 0.0248
NUM se_pub_cl 0.0234
NUM se_pub_hac 0.0274
NUM vif_pub 8.7
NUM vif_promo 1.9
NUM vif_t 1.1
NUM seuil_cook 0.0037
NUM cook_max 0.034
NUM cook_date1 2024-01-01
NUM cook_date2 2024-01-02
NUM n_cook 59
NUM cook_cmd1 14
```

Les résidus sont centrés sur zéro, sans courbure, mais leur dispersion est **plus grande pour les jours à peu de commandes** (partie gauche du nuage) : c'est normal pour des comptages, dont la variabilité relative diminue avec le niveau. Le diagramme quantile-quantile (à droite) compare les résidus à une loi normale : les points suivent la diagonale, avec de légers écarts aux extrémités. Un test formel (Breusch-Pagan) confirme l'inégalité de variance (p-valeur de 0,0001, c'est-à-dire pratiquement nulle).

**2. Corriger les erreurs types.** Une variance qui change n'invalide pas les coefficients, mais fausse leurs **erreurs types** et donc les intervalles. De même, sur une série de jours consécutifs, les résidus d'un jour peuvent ressembler à ceux de la veille (**autocorrélation**). La statistique de Durbin-Watson vaut 1,99 (proche de 2 : pas d'autocorrélation notable), mais on prend la précaution d'utiliser des erreurs types **robustes** (de type « HAC », qui tiennent compte des deux phénomènes) : c'est ce que fait l'option `cov_type="HAC"` utilisée plus haut. L'effet est modeste ici : l'erreur type de la promotion passe de 0,0215 à 0,0248, celle de la publicité de 0,0234 à 0,0274. Retenez le principe : **les coefficients ne bougent pas, les intervalles s'élargissent**.

**3. Chercher la colinéarité.** Quand deux variables explicatives varient presque ensemble, le modèle ne sait pas leur attribuer séparément l'effet : les coefficients deviennent **instables** et leurs intervalles très larges. Le **facteur d'inflation de la variance** (VIF) mesure cette redondance : il vaut 1 pour une variable indépendante des autres, et l'on s'inquiète au-delà de 5 à 10. Ici, la dépense publicitaire a un VIF de 8,7 (elle est très liée aux mois), la promotion de 1,9 et le temps de 1,1. La publicité est donc la variable que le modèle a **le plus de mal à isoler**, ce qui explique en partie la largeur de son intervalle.

**4. Repérer les jours influents.** Un jour peut tirer la droite à lui à lui seul. La **distance de Cook** mesure combien les coefficients changeraient si l'on retirait ce jour. Un seuil usuel est $4/n$, soit 0,0037 ici ; 59 jours le dépassent. Le plus influent est le 2024-01-01 (distance 0,034), un jour de très peu de commandes (14) en tout début de janvier ; le deuxième est le 2024-01-02. Rien d'alarmant : on regarde ces jours, on comprend pourquoi, et l'on vérifie que les conclusions ne tiennent pas à eux seuls.

> ✅ **À retenir.** Quatre contrôles : (1) les **résidus** sans structure, (2) des **erreurs types robustes** quand on travaille sur des jours consécutifs, (3) la **colinéarité** (VIF), (4) les **jours influents**. Aucun ne « valide » un modèle ; ils permettent d'écarter les défauts grossiers, et de dire honnêtement quelle confiance accorder aux intervalles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.2 à 3.4 et exercices 3.4 à 3.8.

### 3.1.8 Expliquer ou prédire ?

Un même modèle peut servir à deux choses, qui ne demandent pas les mêmes précautions.

- **Expliquer** : estimer l'effet d'une variable (promotion, publicité). Ce qui compte : le **bon choix des variables de contrôle** et la **précision** des coefficients (intervalles). Le $R^2$ importe peu : un modèle qui explique peu de variance peut quand même estimer un effet de façon fiable.
- **Prédire** : annoncer les commandes de demain. Ce qui compte : l'**erreur sur des jours que le modèle n'a pas vus**. Le $R^2$ calculé sur les données d'ajustement est trompeur, puisque le modèle a été réglé pour coller à elles.

On juge donc une prévision sur des données **mises de côté** : nous ajustons le modèle sur 2023 et 2024, puis nous prévoyons chaque jour de 2025. Comme référence, deux prévisions naïves : « le même jour de la semaine, 364 jours plus tôt » et le modèle A de la section 3.1.3 (promotion et publicité seulement).

```python
app, test = jr[jr["annee"] <= 2024], jr[jr["annee"] == 2025]          # on ajuste sur le passé, on juge sur l'avenir
m_app = smf.ols(f, data=app).fit()
prevu = np.exp(m_app.predict(test))                                    # retour des logarithmes aux commandes
mae = (test["nb_commandes"] - prevu).abs().mean()
print("erreur absolue moyenne en 2025 :", round(mae, 2), "commandes par jour (moyenne observée :", round(test["nb_commandes"].mean(), 1), ")")
```
<!--sortie-->
```text
erreur absolue moyenne en 2025 : 4.44 commandes par jour (moyenne observée : 35.5 )
```

```python hide
mape = ((test["nb_commandes"] - prevu).abs() / test["nb_commandes"]).mean()
ref364 = jr.set_index("date")["nb_commandes"].shift(364).reindex(test["date"]).values
mae_naif364 = np.nanmean(np.abs(test["nb_commandes"].values - ref364))
m_nsaison = smf.ols(fA, data=app).fit()
mae_nsaison = (test["nb_commandes"] - np.exp(m_nsaison.predict(test))).abs().mean()
NUM("mae", round(mae, 2)); NUM("mape", round(mape * 100, 1)); NUM("mae_364", round(mae_naif364, 2)); NUM("mae_nsaison", round(mae_nsaison, 2)); NUM("moy_test", round(test["nb_commandes"].mean(), 1)); NUM("r2_app", round(m_app.rsquared, 3))
NUM("gain_364", round((1 - mae / mae_naif364) * 100, 0)); NUM("n_app", len(app)); NUM("n_test", len(test))
sem = test.assign(prevu=prevu.values, mois_=test["date"].dt.to_period("W")).groupby("mois_").agg(reel=("nb_commandes", "mean"), prevu=("prevu", "mean"))
fig, ax = plt.subplots(figsize=(9, 3.4))
ax.plot(sem.index.to_timestamp(), sem["reel"], color=BLEU, lw=1.4, label="observé (moyenne hebdomadaire)")
ax.plot(sem.index.to_timestamp(), sem["prevu"], color=ORANGE, lw=1.4, label="prévu par le modèle (ajusté sur 2023-2024)")
ax.set_ylabel("Commandes par jour"); ax.legend(frameon=False, fontsize=8, loc="upper left"); ax.set_title("Prévisions pour 2025 d'un modèle qui n'a jamais vu 2025", loc="left")
fig.savefig("figures/ch03-previsions-2025.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```
<!--sortie-->
```text
NUM mae 4.44
NUM mape 12.9
NUM mae_364 6.66
NUM mae_nsaison 8.98
NUM moy_test 35.5
NUM r2_app 0.757
NUM gain_364 33.0
NUM n_app 725
NUM n_test 365
```

![Commandes moyennes par jour et par semaine en 2025 : observées et prévues par un modèle ajusté sur 2023 et 2024.](figures/ch03-previsions-2025.png)

L'erreur absolue moyenne est de 4,44 commandes par jour (soit 12,9 % en moyenne), pour une moyenne de 35,5 commandes par jour. Trois comparaisons donnent la mesure : la prévision « même jour, 364 jours plus tôt » se trompe de 6,66 commandes par jour ; le modèle A, sans saison, de 8,98. Le modèle complet réduit donc l'erreur de la référence naïve d'environ 33 %. Et le $R^2$ sur les données d'ajustement (0,76) ne dit pas cela : il faut mesurer **sur des jours mis de côté**.

> ⚠️ **Piège.** Un modèle peut très bien **expliquer** (coefficients fiables) et mal **prédire** (beaucoup de bruit autour de la moyenne), et l'inverse. Un bon $R^2$ n'est ni nécessaire ni suffisant pour estimer l'effet d'une promotion, et un coefficient « significatif » ne garantit pas une bonne prévision. Dites toujours **lequel des deux usages** vous visez.

### 3.1.9 Ce que disait la vérité programmée

La comparaison avec ce qui a été programmé est la meilleure façon de savoir si la méthode a fait son travail. Voici ce que le modèle complet a retrouvé.

| Effet | Estimation (intervalle à 95 %) | Vérité programmée |
|---|---|---|
| Promotion | +19,2 % (+13,5 ; +25,1) | +18 % de commandes |
| Publicité, par 1 000 € hebdomadaires | +0,1 % (-5,1 ; +5,7) | +1,5 % |
| Pluie | -1,7 % (-3,8 ; +0,5) | environ −1,7 % en moyenne (−8 % en boutique, +5 % sur le site, selon le poids de chaque canal) |
| Samedi par rapport à lundi | +45,5 % | +47 % (1,40 contre 0,95) |
| Tendance par an | +6,5 % | +6 % |

La promotion est **retrouvée** avec précision (l'effet programmé de +18 % est dans l'intervalle). Les jours de la semaine et la tendance aussi. La pluie, dont l'effet est faible et compensé entre les canaux, reste dans l'incertitude. Quant à la publicité, **l'effet programmé (+1,5 %) est dans l'intervalle, mais l'intervalle est trop large pour le mesurer** : on ne peut pas distinguer +1,5 % de zéro, ni de +5 %. C'est une leçon importante : l'absence d'effet détecté n'est pas la preuve d'une absence d'effet. Il aurait fallu beaucoup plus de jours, ou une expérience volontaire (faire varier la dépense au hasard), pour trancher.

Enfin, un mot sur le **chiffre d'affaires**. Si l'on refait le même modèle sur le chiffre d'affaires plutôt que sur le nombre de commandes, l'effet de la promotion tombe à +8,3 %, au lieu de +19,2 % sur les commandes : c'est que les promotions s'accompagnent de remises de 5 à 20 % sur les prix. La promotion **fait venir** plus de commandes, mais chacune **rapporte moins** ; la question de la gérante (« est-ce que ça rapporte ? ») ne se résume pas au nombre de commandes.

```python hide
mod_ca = smf.ols(f.replace("np.log(nb_commandes)", "np.log(chiffre_affaires)"), data=jr).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
NUM("promo_ca", round(O.pct(mod_ca.params["promo_active"]), 1)); NUM("pub_ca", round(O.pct(mod_ca.params["pub_hebdo"]), 1))
```
<!--sortie-->
```text
NUM promo_ca 8.3
NUM pub_ca -0.0
```

> ✅ **À retenir.**
> - La régression ajuste la droite (ou le plan) qui **minimise la somme des carrés des écarts** ; la pente est la covariance divisée par la variance de $x$.
> - Un coefficient se lit « **toutes choses égales par ailleurs** » : il dépend des autres variables du modèle. Changez les contrôles, il change.
> - Lisez toujours **l'intervalle de confiance**, pas seulement la p-valeur : un intervalle qui contient zéro et un intervalle étroit autour de zéro ne disent pas la même chose.
> - Sur le logarithme de $y$, $e^{\beta}-1$ est l'effet en pourcentage ; avec un logarithme de chaque côté, $\beta$ est une élasticité.
> - Quatre contrôles : résidus, erreurs types robustes, colinéarité (VIF), points influents.
> - **Expliquer** demande les bons contrôles ; **prédire** demande des **données mises de côté**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.5 et exercices 3.9 à 3.10.
