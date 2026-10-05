## 2.4 Déviance, qualité d'ajustement, vérification du modèle

> 💡 **Intuition.** Un modèle ajusté, ce n'est pas un modèle **validé**. Dans la régression linéaire, on jugeait un modèle par la somme des carrés des résidus (RSS) et par le $R^2$. Dans un GLM, l'équivalent de la RSS est la **déviance** : une mesure de l'écart entre le modèle ajusté et le meilleur modèle imaginable. Elle sert à **comparer** des modèles emboîtés (test du rapport de vraisemblance), et les **résidus** servent à détecter ce que le modèle n'a pas compris. Dans tous les cas, la règle est la même : on regarde ce qui reste *après* l'ajustement.

### 2.4.1 La déviance

Pour chaque observation, on peut imaginer un modèle « parfait » qui prédit exactement $y_i$ : c'est le **modèle saturé** (un paramètre par observation). Sa log-vraisemblance $\ell_{\text{sat}}$ est la plus grande possible. La **déviance** d'un modèle ajusté mesure son retard sur ce modèle saturé :
$$D=2\big[\ell_{\text{sat}}-\ell(\hat\beta)\big]=\sum_{i=1}^n d(y_i,\hat\mu_i),$$
où $d(y,\mu)$ est la **déviance unitaire** de l'observation (dépend de la famille). C'est un $\chi^2$ pour des données groupées assez grandes. La déviance joue pour un GLM le rôle de la **somme des carrés des résidus** : pour la loi normale, $d(y,\mu)=(y-\mu)^2$ et $D=\mathrm{RSS}/\sigma^2$.

| Famille | Déviance unitaire $d(y,\mu)$ |
|---|---|
| Normale | $(y-\mu)^2$ |
| Poisson | $2\big[y\log\frac{y}{\mu}-(y-\mu)\big]$ |
| Bernoulli | $2\big[y\log\frac{y}{\mu}+(1-y)\log\frac{1-y}{1-\mu}\big]$ (avec la convention $0\log0=0$) |
| Gamma | $2\big[-\log\frac{y}{\mu}+\frac{y-\mu}{\mu}\big]$ |

**Un calcul à la main.** Quatre clients ont passé $y=(2,5,3,8)$ commandes ; le modèle sans variable (Poisson) estime $\hat\mu=\bar y=4{,}5$ pour tous. La déviance est $D=2\sum_i\big[y_i\log\frac{y_i}{\hat\mu}-(y_i-\hat\mu)\big]$ ; comme $\sum(y_i-\hat\mu)=0$, il reste $D=2\sum y_i\log\frac{y_i}{4{,}5}$. Terme par terme : $2\log\frac{2}{4{,}5}=-1{,}622$ ; $5\log\frac{5}{4{,}5}=0{,}527$ ; $3\log\frac{3}{4{,}5}=-1{,}216$ ; $8\log\frac{8}{4{,}5}=4{,}603$. Leur somme vaut $2{,}2915$, d'où $D=4{,}583$. La statistique de Pearson, elle, vaut $\sum\frac{(y_i-\hat\mu)^2}{\hat\mu}=\frac{6{,}25+0{,}25+2{,}25+12{,}25}{4{,}5}=4{,}667$ : proche de la déviance, comme c'est généralement le cas.

Un programme confirme ce calcul et l'étend aux modèles des sections précédentes (cahier, application 2.6).

```python hide-code
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats
from scipy.special import xlogy

def deviance_unitaire(famille, y, mu):
    """Déviance unitaire d(y, mu) pour chaque observation (xlogy gère la convention 0 log 0 = 0)."""
    if famille == "normale":
        return (y - mu) ** 2
    if famille == "poisson":
        return 2 * (xlogy(y, y / mu) - (y - mu))
    if famille == "bernoulli":
        return 2 * (xlogy(y, y / mu) + xlogy(1 - y, (1 - y) / (1 - mu)))
    if famille == "gamma":
        return 2 * (-np.log(y / mu) + (y - mu) / mu)

y4 = np.array([2.0, 5, 3, 8])
mu4 = np.full(4, y4.mean())
print("déviance à la main    :", round(float(deviance_unitaire("poisson", y4, mu4).sum()), 4))
print("Pearson X² à la main  :", round(float((((y4 - mu4) ** 2) / mu4).sum()), 4))
m4 = sm.GLM(y4, np.ones((4, 1)), family=sm.families.Poisson()).fit()
print("déviance statsmodels  :", round(float(m4.deviance), 4), "| Pearson statsmodels :", round(float(m4.pearson_chi2), 4))

# Les trois modèles des sections 2.2 et 2.3, sur les vraies données
clients = pd.read_csv("donnees/clients.csv")
clients["canal"] = pd.Categorical(clients["canal_acquisition"], categories=["Boutique", "Réseaux", "Site"])
logi = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
poi = smf.glm("nb_commandes_an ~ age + canal + offre_bienvenue", clients, family=sm.families.Poisson()).fit()
acheteurs = clients[clients["depense_annuelle"] > 0]
gam = smf.glm("depense_annuelle ~ age + canal + offre_bienvenue", acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")

lignes = []
for nom, fam, res, y in [("logistique", "bernoulli", logi, clients["rachat_12m"]), ("Poisson", "poisson", poi, clients["nb_commandes_an"]),
                         ("Gamma", "gamma", gam, acheteurs["depense_annuelle"])]:
    d_main = deviance_unitaire(fam, y.to_numpy(float), res.fittedvalues.to_numpy()).sum()
    mu_nul = np.full(len(y), y.mean())
    d_nul = deviance_unitaire(fam, y.to_numpy(float), mu_nul).sum()
    lignes.append({"modèle": nom, "déviance (main)": d_main, "déviance (statsmodels)": res.deviance, "déviance nulle (main)": d_nul,
                   "déviance nulle (statsmodels)": res.null_deviance, "part de déviance expliquée": 1 - d_main / d_nul})
print()
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
déviance à la main    : 4.5829
Pearson X² à la main  : 4.6667
déviance statsmodels  : 4.5829 | Pearson statsmodels : 4.6667

    modèle  déviance (main)  déviance (statsmodels)  déviance nulle (main)  déviance nulle (statsmodels)  part de déviance expliquée
logistique         2710.830                2710.830               2771.867                      2771.867                       0.022
   Poisson         6292.954                6292.954               6357.639                      6357.639                       0.010
     Gamma         1389.349                1389.349               1473.452                      1473.452                       0.057
```

Dans l'exemple à quatre clients, notre calcul (4,5829) et celui de `statsmodels` coïncident, de même que la statistique de Pearson (4,6667). Pour les trois modèles des sections précédentes, la déviance calculée à la main est **identique** à celle du logiciel (par exemple 2 710,83 pour la logistique, 6 292,95 pour Poisson, 1 389,35 pour Gamma), ainsi que la déviance nulle. La part de déviance expliquée est de **2,2 %** pour la logistique, **1,0 %** pour Poisson et **5,7 %** pour Gamma : des valeurs faibles, typiques de résultats individuels très aléatoires (rachat ou non, nombre de commandes d'un client).

> 💡 **« Part de déviance expliquée ».** Le rapport $1-D/D_{\text{nulle}}$ est l'analogue du $R^2$ : il mesure la fraction de la déviance du modèle sans variable (le plus simple possible) que l'on a réussi à « expliquer ». C'est un pseudo-$R^2$, et il est **souvent faible** pour des données individuelles discrètes : un faible pseudo-$R^2$ n'est pas un défaut en soi (le hasard est important), mais il rappelle l'ampleur du travail qui reste.

> ⚠️ **La déviance d'un modèle binaire n'est pas un test d'ajustement.** Pour des 0/1 individuels, la déviance vaut $-2\ell$ et ne suit pas un $\chi^2$ ; il est **inutile** de la comparer à ses degrés de liberté (voir 2.4.4 pour le bon outil). Pour des comptages ou des données groupées à effectifs assez grands, en revanche, déviance et Pearson divisées par les degrés de liberté doivent être proches de 1 si le modèle est correct.

### 2.4.2 Comparer des modèles emboîtés : le test du rapport de vraisemblance

Deux modèles sont **emboîtés** si le plus petit s'obtient en fixant certains coefficients du plus grand à zéro. Si le petit modèle est correct, la différence de déviance suit, pour de grands échantillons, un $\chi^2$ dont le nombre de degrés de liberté est le nombre de coefficients retirés :
$$D_{\text{réduit}}-D_{\text{complet}}=2\big[\ell_{\text{complet}}-\ell_{\text{réduit}}\big]\ \approx\ \chi^2_q.$$
Pour retirer une variable à $q$ niveaux (le canal en a trois : $q=2$), cette différence permet de tester **globalement** son utilité, ce que les tests de Wald coefficient par coefficient ne font pas.


Pour une variable, le test tient en trois lignes : on ajuste le modèle sans elle et l'on regarde de combien la déviance augmente. Pour l'offre :

```python
complet = smf.glm("rachat_12m ~ offre_bienvenue + age + canal", clients, family=sm.families.Binomial()).fit()
sans_offre = smf.glm("rachat_12m ~ age + canal", clients, family=sm.families.Binomial()).fit()
delta = sans_offre.deviance - complet.deviance      # hausse de la déviance quand on retire l'offre
print(f"hausse de la déviance : {delta:.2f}  (p = {stats.chi2.sf(delta, 1):.1e})")
```
<!--sortie-->
```text
hausse de la déviance : 29.64  (p = 5.2e-08)
```


```python hide-code
def test_rv(complet, reduit, ddl):
    delta = reduit.deviance - complet.deviance
    return delta, ddl, stats.chi2.sf(delta, ddl)

formule_c = "rachat_12m ~ offre_bienvenue + age + canal"
complet = smf.glm(formule_c, clients, family=sm.families.Binomial()).fit()
essais = [("canal (2 ddl)", "rachat_12m ~ offre_bienvenue + age", 2),
          ("age (1 ddl)", "rachat_12m ~ offre_bienvenue + canal", 1),
          ("offre_bienvenue (1 ddl)", "rachat_12m ~ age + canal", 1)]
wald = complet.wald_test_terms(scalar=True).table
lignes = []
for nom, f_reduite, ddl in essais:
    reduit = smf.glm(f_reduite, clients, family=sm.families.Binomial()).fit()
    delta, q, p_rv = test_rv(complet, reduit, ddl)
    terme = nom.split(" ")[0]
    lignes.append({"variable retirée": nom, "D réduit - D complet": delta, "p (rapport de vraisemblance)": p_rv,
                   "p (Wald)": wald.loc[terme, "pvalue"]})
print(pd.DataFrame(lignes).round(4).to_string(index=False))
print()
print("déviance du modèle complet :", round(complet.deviance, 2), "| déviance sans l'offre :", round(smf.glm("rachat_12m ~ age + canal", clients, family=sm.families.Binomial()).fit().deviance, 2))
```
<!--sortie-->
```text
       variable retirée  D réduit - D complet  p (rapport de vraisemblance)  p (Wald)
          canal (2 ddl)               17.7355                        0.0001    0.0001
            age (1 ddl)               12.7919                        0.0003    0.0004
offre_bienvenue (1 ddl)               29.6401                        0.0000    0.0000

déviance du modèle complet : 2710.83 | déviance sans l'offre : 2740.47
```

Retirer le canal (2 coefficients) augmente la déviance de 17,74 ($p=0{,}0001$) ; retirer l'âge, de 12,79 ($p=0{,}0003$) ; retirer l'offre, de 29,64 ($p<0{,}0001$) : la déviance du modèle complet est de 2 710,83, contre 2 740,47 sans l'offre. Les p-valeurs du rapport de vraisemblance et celles de Wald (qui testent les mêmes hypothèses) sont ici très proches (par exemple 0,0003 contre 0,0004 pour l'âge) : avec 2 000 observations et des effets modestes, les deux tests s'accordent. La différence apparaît pour de petits échantillons ou des effets très forts, où le rapport de vraisemblance est le plus fiable.

**Quand la dispersion $\phi$ est inconnue** (Gamma, normale, quasi-Poisson), la différence de déviance divisée par $\hat\phi$ n'est plus un $\chi^2$ exact : on utilise un test $F$ (comme en régression linéaire),
$$F=\frac{(D_{\text{réduit}}-D_{\text{complet}})/q}{\hat\phi_{\text{complet}}}\ \sim\ F_{q,\;n-p}.$$
Appliquons-le à la régression Gamma de 2.3 : le canal (2 ddl) et l'offre (1 ddl) ont-ils un effet sur la dépense des acheteurs ?

```python hide
f_gamma = "depense_annuelle ~ age + canal + offre_bienvenue"
g_complet = smf.glm(f_gamma, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
phi_g = g_complet.scale
for nom, f_reduite, ddl in [("canal (2 ddl)", "depense_annuelle ~ age + offre_bienvenue", 2), ("offre_bienvenue (1 ddl)", "depense_annuelle ~ age + canal", 1)]:
    g_reduit = smf.glm(f_reduite, acheteurs, family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
    F = (g_reduit.deviance - g_complet.deviance) / ddl / phi_g
    print(f"{nom:24s}: F = {F:7.2f} sur ({ddl}, {int(g_complet.df_resid)}) ddl | p = {stats.f.sf(F, ddl, g_complet.df_resid):.2e}")
```
<!--sortie-->
```text
canal (2 ddl)           : F =   37.09 sur (2, 1735) ddl | p = 1.69e-16
offre_bienvenue (1 ddl) : F =    0.04 sur (1, 1735) ddl | p = 8.39e-01
```

Le canal a un effet très net sur la dépense des acheteurs ($F=37{,}09$ sur $(2;1\,735)$ degrés de liberté, $p\approx10^{-16}$) ; l'offre, aucun ($F=0{,}04$, $p=0{,}84$). Pour un seul degré de liberté, $F$ est le carré de la statistique $t$ de Wald et les deux tests donnent la même p-valeur : on retrouve ici exactement la p-valeur 0,839 du tableau de la section 2.3.4.

### 2.4.3 Les résidus d'un GLM

Dans la régression linéaire, le résidu est $y_i-\hat y_i$, et son graphique contre la valeur ajustée doit ressembler à un nuage sans structure. Dans un GLM, la variance varie avec la moyenne, donc les résidus bruts $y_i-\hat\mu_i$ ne sont pas comparables entre eux. On les **standardise** :

- **Résidu de Pearson** : $r_i^P=\dfrac{y_i-\hat\mu_i}{\sqrt{\phi\,V(\hat\mu_i)}}$ (on divise par l'écart-type attendu). La somme de leurs carrés est la statistique de Pearson $X^2$.
- **Résidu de déviance** : $r_i^D=\mathrm{signe}(y_i-\hat\mu_i)\sqrt{d(y_i,\hat\mu_i)}$. La somme de leurs carrés est la déviance $D$. Leur loi est souvent plus proche de la normale que celle des résidus de Pearson.

```python hide
r_p = poi.resid_pearson.to_numpy()
r_d = poi.resid_deviance.to_numpy()
print("Poisson : somme des carrés des résidus de Pearson   =", round(float((r_p ** 2).sum()), 1), "| X² =", round(poi.pearson_chi2, 1))
print("Poisson : somme des carrés des résidus de déviance =", round(float((r_d ** 2).sum()), 1), "| D  =", round(poi.deviance, 1))
print("résidus de Pearson : moyenne =", round(float(r_p.mean()), 3), "| écart-type =", round(float(r_p.std()), 3), "(attendu : environ 1 si le modèle est correct)")
print("part de |résidus de Pearson| > 2 :", round(float((np.abs(r_p) > 2).mean()), 3), "(attendu pour une loi normale : environ 0,046)")
```
<!--sortie-->
```text
Poisson : somme des carrés des résidus de Pearson   = 6774.2 | X² = 6774.2
Poisson : somme des carrés des résidus de déviance = 6293.0 | D  = 6293.0
résidus de Pearson : moyenne = -0.0 | écart-type = 1.84 (attendu : environ 1 si le modèle est correct)
part de |résidus de Pearson| > 2 : 0.175 (attendu pour une loi normale : environ 0,046)
```

Les deux sommes de carrés reproduisent exactement $X^2=6\,774{,}2$ et $D=6\,293{,}0$. L'écart-type des résidus de Pearson vaut **1,84** au lieu de 1 (c'est $\sqrt{\hat\phi}=\sqrt{3{,}40}$), et 17,5 % d'entre eux dépassent 2 en valeur absolue, contre environ 4,6 % pour une loi normale : les résidus sont beaucoup trop dispersés, ce qui confirme la surdispersion vue en 2.3.3.

**Le problème des données discrètes.** Pour un 0/1 ou un comptage, les résidus de Pearson et de déviance prennent des valeurs **discrètes** : même avec le bon modèle, leur graphique ne ressemble pas à un nuage normal. On utilise alors les **résidus quantiles aléatoires** de Dunn et Smyth (1996), qui ont une propriété remarquable : si le modèle est correct, ils suivent **exactement** une loi normale standard, quelle que soit la famille.

> 📐 **Construction.** Soit $F_i$ la fonction de répartition prédite par le modèle pour l'observation $i$ (Poisson de moyenne $\hat\mu_i$, etc.). Si $Y_i$ est continue et que le modèle est correct, $U_i=F_i(Y_i)$ suit une loi uniforme sur $[0,1]$ (c'est la **transformée intégrale de probabilité**), et $\Phi^{-1}(U_i)$ suit une loi normale standard ($\Phi$ : fonction de répartition normale). Si $Y_i$ est discrète, $F_i(Y_i)$ n'est pas uniforme (il prend un nombre fini de valeurs) ; on **randomise** : on tire $U_i$ uniformément dans l'intervalle $\big[F_i(y_i-1),\,F_i(y_i)\big]$ (la marche de la fonction de répartition au point $y_i$), puis on pose $r_i=\Phi^{-1}(U_i)$. Si le modèle est correct, $U_i$ est uniforme et $r_i\sim\mathcal N(0,1)$.

Appliquons-les à nos quatre modèles : la logistique, la régression de Poisson, la binomiale négative, la régression Gamma. Si le modèle est bon, le graphique « quantiles théoriques contre quantiles observés » (QQ-plot) suit la diagonale.

```python hide
rng = np.random.default_rng(44)

def residus_quantiles(u_bas, u_haut):
    u = rng.uniform(u_bas, u_haut)
    return stats.norm.ppf(np.clip(u, 1e-12, 1 - 1e-12))

y_b = clients["rachat_12m"].to_numpy()
p_b = logi.fittedvalues.to_numpy()
rq_logi = residus_quantiles(np.where(y_b == 1, 1 - p_b, 0.0), np.where(y_b == 1, 1.0, 1 - p_b))

y_c = clients["nb_commandes_an"].to_numpy()
mu_p = poi.fittedvalues.to_numpy()
rq_poi = residus_quantiles(stats.poisson.cdf(y_c - 1, mu_p), stats.poisson.cdf(y_c, mu_p))

nbm = smf.negativebinomial("nb_commandes_an ~ age + canal + offre_bienvenue", clients).fit(disp=0)
a_nb, mu_nb = float(nbm.params["alpha"]), np.asarray(nbm.predict())
n_nb, p_nb = 1 / a_nb, (1 / a_nb) / ((1 / a_nb) + mu_nb)
rq_nb = residus_quantiles(stats.nbinom.cdf(y_c - 1, n_nb, p_nb), stats.nbinom.cdf(y_c, n_nb, p_nb))

y_g = acheteurs["depense_annuelle"].to_numpy()
mu_g = gam.fittedvalues.to_numpy()
u_g = stats.gamma.cdf(y_g, a=1 / gam.scale, scale=mu_g * gam.scale)
rq_gam = stats.norm.ppf(np.clip(u_g, 1e-12, 1 - 1e-12))

# Même le modèle SANS variable (probabilité constante) donne des résidus quantiles « parfaits » pour un 0/1
p_nul = np.full(len(y_b), y_b.mean())
rq_nul = residus_quantiles(np.where(y_b == 1, 1 - p_nul, 0.0), np.where(y_b == 1, 1.0, 1 - p_nul))

resume = []
for nom, r in [("logistique", rq_logi), ("logistique sans variable", rq_nul), ("Poisson", rq_poi), ("binomiale négative", rq_nb), ("Gamma", rq_gam)]:
    resume.append({"modèle": nom, "moyenne": r.mean(), "écart-type": r.std(), "part de |r| > 2": (np.abs(r) > 2).mean(),
                   "p (Kolmogorov-Smirnov)": stats.kstest(r, "norm").pvalue})
print(pd.DataFrame(resume).round(3).to_string(index=False))

fig, axes = plt.subplots(1, 4, figsize=(14, 3.7), sharex=True, sharey=True)
BLEU, ORANGE = "#2a78d6", "#eb6834"
for ax, (nom, r, c) in zip(axes, [("logistique", rq_logi, BLEU), ("Poisson", rq_poi, ORANGE), ("binomiale négative", rq_nb, BLEU), ("Gamma", rq_gam, BLEU)]):
    r = np.sort(r)
    theo = stats.norm.ppf((np.arange(1, len(r) + 1) - 0.5) / len(r))
    ax.plot(theo, r, ".", color=c, ms=3)
    ax.plot([-4, 4], [-4, 4], color="#52514e", lw=1)
    ax.set_title(nom); ax.set_xlabel("quantiles de la loi normale")
axes[0].set_ylabel("résidus quantiles aléatoires")
axes[0].set_xlim(-4, 4); axes[0].set_ylim(-4, 4)
plt.tight_layout()
plt.savefig("figures/ch02-residus-quantiles.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
                  modèle  moyenne  écart-type  part de |r| > 2  p (Kolmogorov-Smirnov)
              logistique    0.010       1.009            0.048                   0.896
logistique sans variable   -0.020       1.008            0.040                   0.257
                 Poisson   -0.148       1.675            0.228                   0.000
      binomiale négative    0.004       0.991            0.045                   0.849
                   Gamma    0.087       0.833            0.023                   0.000
figure enregistrée
```

![QQ-plots des résidus quantiles aléatoires pour quatre modèles. Si le modèle est correct, les points suivent la diagonale. Le modèle de Poisson (orange) s'en écarte nettement ; le modèle Gamma s'écarte aussi, dans la queue inférieure.](figures/ch02-residus-quantiles.png)

Lisons les statistiques résumées et les QQ-plots.

- **Poisson** : écart-type des résidus de 1,68, 22,8 % de résidus au-delà de $\pm2$ (pour 4,6 % attendus), p-valeur de Kolmogorov-Smirnov nulle. La courbe est nettement plus raide que la diagonale : les résidus sont trop dispersés, le modèle sous-estime la variabilité.
- **Binomiale négative** : moyenne 0,004, écart-type 0,991, 4,5 % au-delà de $\pm2$, $p=0{,}85$ : les résidus sont **indiscernables d'une loi normale**. La famille est adaptée.
- **Gamma** : écart-type 0,83 et p-valeur nulle. La courbe est plate dans la queue inférieure (les résidus ne descendent pas sous $-1{,}6$ environ) et trop haute dans la queue supérieure. Le modèle Gamma avec un coefficient de variation de 1 attend beaucoup de petites dépenses, alors qu'une dépense annuelle d'acheteur vaut au moins un panier, et qu'un panier est rarement très petit. Les **moyennes** prédites sont bonnes (nous l'avons vu en 2.3.4), mais la **forme** de la loi est fausse : la régression Gamma reste valide pour estimer l'effet des variables sur la moyenne (c'est une méthode de quasi-vraisemblance), mais il ne faudrait pas s'en servir pour simuler des dépenses ou calculer des intervalles de prévision. La section 2.6 propose un modèle plus adapté.
- **Logistique** : écart-type 1,009, $p=0{,}90$. **Attention : ce résultat ne prouve rien.** Pour un résultat 0/1, les résidus quantiles aléatoires sont normaux dès que la probabilité *moyenne* est correcte : le modèle **sans aucune variable** donne lui aussi des résidus parfaits (écart-type 1,008, $p=0{,}26$). Pour une réponse binaire, le QQ-plot ne détecte rien ; il faut regarder la calibration, le test de Hosmer-Lemeshow et les résidus par classes (2.4.4).

### 2.4.4 Mesurer la qualité d'ajustement

**Surdispersion.** Pour un modèle de comptage, on a déjà un indicateur : Pearson $X^2/\text{ddl}$ doit être proche de 1. Pour la binomiale négative, la variance est $\mu+\alpha\mu^2$ ; on calcule donc $X^2$ avec cette variance.

```python hide
x2_nb = np.sum((y_c - mu_nb) ** 2 / (mu_nb + a_nb * mu_nb ** 2))
ddl_nb = len(y_c) - len(nbm.params) + 1          # on retire le paramètre alpha du compte des coefficients
print("Poisson            : X²/ddl =", round(poi.pearson_chi2 / poi.df_resid, 3))
print("binomiale négative : X²/ddl =", round(float(x2_nb / ddl_nb), 3))
```
<!--sortie-->
```text
Poisson            : X²/ddl = 3.396
binomiale négative : X²/ddl = 1.044
```

Le rapport vaut **3,40** pour Poisson (nettement supérieur à 1 : surdispersion) et **1,04** pour la binomiale négative : avec la bonne forme de variance, la dispersion est correctement décrite.

**Le test de Hosmer-Lemeshow pour la régression logistique.** Pour des 0/1 individuels, on regroupe les clients par classes de probabilité prédite (dix classes de même effectif) et l'on compare, dans chaque classe $k$, le nombre observé de « oui » $O_k$ au nombre attendu $E_k=\sum_{i\in k}\hat p_i$. La statistique
$$HL=\sum_{k=1}^{g}\frac{(O_k-E_k)^2}{E_k\,(1-\bar p_k)}\ \approx\ \chi^2_{g-2}$$
(où $\bar p_k=E_k/n_k$ est la probabilité moyenne de la classe) est grande si le modèle est mal calibré. C'est la version formelle de la courbe de calibration de la section 2.2.8.

```python hide-code
def hosmer_lemeshow(y, p, g=10):
    classes = pd.qcut(p, g, labels=False, duplicates="drop")
    d = pd.DataFrame({"y": y, "p": p, "k": classes}).groupby("k").agg(O=("y", "sum"), E=("p", "sum"), n=("y", "size"))
    d["pbar"] = d["E"] / d["n"]
    hl = (((d["O"] - d["E"]) ** 2) / (d["E"] * (1 - d["pbar"]))).sum()
    ddl = len(d) - 2
    return hl, ddl, stats.chi2.sf(hl, ddl), d

hl, ddl, p_hl, tab = hosmer_lemeshow(clients["rachat_12m"].to_numpy(), logi.fittedvalues.to_numpy())
print(f"modèle de rachat : HL = {hl:.2f} sur {ddl} ddl, p = {p_hl:.3f}")

# Un modèle mal spécifié : sessions de navigation (simulées), effet de la durée en « cloche » mais modèle linéaire sur le logit
sessions = pd.read_csv("donnees/ch02-sessions.csv")
lineaire = smf.glm("achat ~ duree_min", sessions, family=sm.families.Binomial()).fit()
bosse = smf.glm("achat ~ duree_min + I(duree_min**2)", sessions, family=sm.families.Binomial()).fit()
for nom, res in [("linéaire sur le logit", lineaire), ("avec terme quadratique", bosse)]:
    hl_s, ddl_s, p_s, _ = hosmer_lemeshow(sessions["achat"].to_numpy(), res.fittedvalues.to_numpy())
    print(f"sessions, {nom:24s} : HL = {hl_s:6.2f} sur {ddl_s} ddl, p = {p_s:.4f} | AIC = {res.aic:.1f}")
```
<!--sortie-->
```text
modèle de rachat : HL = 6.15 sur 8 ddl, p = 0.631
sessions, linéaire sur le logit    : HL = 243.18 sur 8 ddl, p = 0.0000 | AIC = 1960.3
sessions, avec terme quadratique   : HL =  54.33 sur 8 ddl, p = 0.0000 | AIC = 1787.7
```

Pour le modèle de rachat, $HL=6{,}15$ sur 8 degrés de liberté ($p=0{,}63$) : rien n'indique une mauvaise calibration, ce qui confirme la lecture de la courbe de calibration de 2.2.8. Pour les sessions de navigation, au contraire, le modèle linéaire sur le logit est rejeté de façon écrasante ($HL=243$, AIC $=1\,960{,}3$). Ajouter un terme quadratique améliore beaucoup les choses (HL tombe à 54,3 et l'AIC à 1 787,7, soit **172 points** de moins), mais le test rejette encore : le modèle quadratique n'est **pas suffisant** non plus. Un test qui rejette dit « quelque chose ne va pas », pas « quoi » : regardons le graphique.

**Le graphique de résidus par classes.** Pour **voir** ce que le test détecte, on regroupe les sessions par tranches de durée et l'on compare, pour chaque tranche, la fréquence d'achat observée à celle prédite par le modèle linéaire.

```python hide
tranches = pd.cut(sessions["duree_min"], bins=[0, 3, 5, 7, 9, 11, 13, 15, 18, 22, 40])
g = sessions.assign(p_lin=lineaire.fittedvalues, p_bosse=bosse.fittedvalues, tranche=tranches).groupby("tranche", observed=True).agg(
    duree=("duree_min", "mean"), observe=("achat", "mean"), p_lineaire=("p_lin", "mean"), p_bosse=("p_bosse", "mean"), n=("achat", "size"))
print(g.round(3).to_string())

fig, ax = plt.subplots(figsize=(7.2, 4.2))
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"
ax.plot(g["duree"], g["observe"], "o", color="#52514e", label="fréquence observée (par tranche)")
ax.plot(g["duree"], g["p_lineaire"], "-", color=ORANGE, lw=2, label="modèle linéaire sur le logit")
ax.plot(g["duree"], g["p_bosse"], "-", color=BLEU, lw=2, label="avec terme quadratique")
ax.set_xlabel("durée de la session (minutes)"); ax.set_ylabel("probabilité d'achat")
ax.set_title("Un modèle mal spécifié se voit dans les résidus par classes"); ax.legend(frameon=False, fontsize=9)
plt.tight_layout()
plt.savefig("figures/ch02-residus-par-classes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
           duree  observe  p_lineaire  p_bosse    n
tranche                                            
(0, 3]     2.265    0.189       0.630    0.174   37
(3, 5]     4.240    0.333       0.584    0.343  114
(5, 7]     6.113    0.381       0.539    0.489  231
(7, 9]     8.100    0.650       0.490    0.581  240
(9, 11]   10.051    0.740       0.443    0.600  223
(11, 13]  11.930    0.566       0.398    0.553  182
(13, 15]  14.071    0.320       0.350    0.422  147
(15, 18]  16.367    0.140       0.301    0.226  171
(18, 22]  19.996    0.079       0.232    0.037  101
(22, 40]  26.831    0.019       0.139    0.001   54
figure enregistrée
```

![Fréquence d'achat observée par tranche de durée de session (points), modèle linéaire sur le logit (orange) et modèle avec terme quadratique (bleu). Le modèle linéaire rate la bosse ; le terme quadratique la capte mieux, mais pas parfaitement.](figures/ch02-residus-par-classes.png)

Le modèle linéaire (orange) prédit une probabilité d'achat **décroissante** avec la durée, alors que les fréquences observées montent jusqu'à environ 10 minutes puis redescendent : il prédit 0,63 pour les sessions de 2 minutes (observé : 0,19) et 0,44 autour de 10 minutes (observé : 0,74). Les résidus par classes dessinent une structure nette (négatifs, puis positifs, puis négatifs) : c'est la signature d'un **mauvais choix de forme fonctionnelle**. Le terme quadratique (bleu) capte la bosse, mais pas parfaitement : il sous-estime le sommet (0,60 prédit, 0,74 observé à 10 minutes) et descend trop bas dans la queue (0,001 prédit contre 0,019 observé au-delà de 22 minutes). Une parabole sur le logit retombe trop vite : il faut une forme plus souple, celle des modèles additifs généralisés (section 2.5).

### 2.4.5 Comparer des modèles non emboîtés : AIC et BIC

Le test du rapport de vraisemblance ne vaut que pour des modèles emboîtés. Pour comparer des modèles quelconques (par exemple Poisson et binomiale négative, ou deux ensembles de variables différents), on utilise des **critères d'information**, qui pénalisent la vraisemblance par le nombre de paramètres $k$ :
$$\mathrm{AIC}=-2\ell+2k,\qquad \mathrm{BIC}=-2\ell+k\log n.$$
Plus la valeur est **petite**, mieux c'est. Le BIC pénalise plus lourdement la complexité dès que $n>7$, et conduit à des modèles plus parcimonieux. Ils ne mesurent que la qualité *relative* des modèles comparés : le meilleur d'une liste de mauvais modèles reste un mauvais modèle (d'où l'importance des résidus).

```python hide-code
formules = {
    "aucune variable": "rachat_12m ~ 1",
    "+ offre": "rachat_12m ~ offre_bienvenue",
    "+ offre + âge": "rachat_12m ~ offre_bienvenue + age",
    "+ offre + âge + canal": "rachat_12m ~ offre_bienvenue + age + canal",
    "+ offre × canal (interactions)": "rachat_12m ~ offre_bienvenue * canal + age",
}
lignes = []
ajustes = {}
for nom, f in formules.items():
    r = smf.glm(f, clients, family=sm.families.Binomial()).fit()
    ajustes[nom] = r
    lignes.append({"modèle": nom, "paramètres": len(r.params), "déviance": r.deviance, "AIC": r.aic, "BIC": r.bic_llf})
res = pd.DataFrame(lignes)
res["ΔAIC"] = res["AIC"] - res["AIC"].min()
res["ΔBIC"] = res["BIC"] - res["BIC"].min()
print(res.round(1).to_string(index=False))
delta_inter = ajustes["+ offre + âge + canal"].deviance - ajustes["+ offre × canal (interactions)"].deviance
print(f"\ntest du rapport de vraisemblance pour les 2 interactions : différence de déviance = {delta_inter:.2f}, p = {stats.chi2.sf(delta_inter, 2):.3f}")
```
<!--sortie-->
```text
                        modèle  paramètres  déviance    AIC    BIC  ΔAIC  ΔBIC
               aucune variable           1    2771.9 2773.9 2779.5  57.8  30.6
                       + offre           2    2742.1 2746.1 2757.3  30.1   8.5
                 + offre + âge           3    2728.6 2734.6 2751.4  18.5   2.5
         + offre + âge + canal           5    2710.8 2720.8 2748.8   4.8   0.0
+ offre × canal (interactions)           7    2702.1 2716.1 2755.3   0.0   6.4

test du rapport de vraisemblance pour les 2 interactions : différence de déviance = 8.77, p = 0.012
```

L'AIC diminue à chaque variable ajoutée (de $\Delta=57{,}8$ pour le modèle sans variable jusqu'à 0 pour le modèle avec interactions) et **retient donc le modèle le plus complexe**. Le BIC, plus sévère, est minimal pour le modèle **sans interactions** (celui avec les interactions a $\Delta\mathrm{BIC}=6{,}4$). Le test du rapport de vraisemblance donne $p=0{,}012$ pour les deux interactions. C'est ici un cas limite où les critères divergent. Que faire ? Une interaction que l'on n'avait **pas prévue** et qui n'est « significative » qu'à $p=0{,}012$ est typiquement un résultat à regarder avec méfiance (volume I, section 3.5.5 : quand on teste beaucoup d'effets, quelques-uns paraissent significatifs par hasard) ; on garde de préférence le modèle plus simple, plus facile à expliquer, sauf raison métier d'attendre une interaction. Nous verrons, dans la « vérité dévoilée » du bilan, ce qu'il en était réellement.

### 2.4.6 Observations influentes

Une observation peut peser démesurément sur l'ajustement : par son **levier** (ses variables explicatives sont extrêmes) et par son **résidu** (le modèle la prédit mal). La **distance de Cook** combine les deux et mesure de combien les coefficients bougeraient si on retirait cette observation.

```python hide
infl = logi.get_influence()
levier = infl.hat_matrix_diag
cook = infl.cooks_distance[0]
print("levier moyen =", round(float(levier.mean()), 4), "(= p/n =", round(5 / len(clients), 4), ") | levier maximal =", round(float(levier.max()), 4))
print("distance de Cook maximale =", round(float(cook.max()), 4), "| seuil usuel 4/n =", round(4 / len(clients), 4), "| clients au-dessus du seuil :", int((cook > 4 / len(clients)).sum()))
pire = clients.loc[int(np.argmax(cook)), ["age", "canal_acquisition", "offre_bienvenue", "rachat_12m"]]
print("client le plus influent :", pire.to_dict())
print("probabilité de rachat prédite pour ce client :", round(float(logi.fittedvalues.iloc[int(np.argmax(cook))]), 3))
```
<!--sortie-->
```text
levier moyen = 0.0025 (= p/n = 0.0025 ) | levier maximal = 0.0076
distance de Cook maximale = 0.0023 | seuil usuel 4/n = 0.002 | clients au-dessus du seuil : 3
client le plus influent : {'age': 68, 'canal_acquisition': 'Boutique', 'offre_bienvenue': 0, 'rachat_12m': 1}
probabilité de rachat prédite pour ce client : 0.386
```

Le levier moyen vaut exactement $p/n=5/2\,000=0{,}0025$ (c'est toujours le cas), et le levier maximal 0,0076, soit environ trois fois la moyenne : aucun client n'est extrême dans ses variables. La distance de Cook maximale n'est que de 0,0023, à peine au-dessus du seuil usuel $4/n=0{,}002$ (que trois clients dépassent) : des valeurs de l'ordre du millième n'inquiètent pas. Le client le plus influent (68 ans, acquis en boutique, sans offre) avait une probabilité prédite de 38,6 % de racheter, et il a racheté : un âge élevé, donc proche de l'extrémité de la plage d'âges, et un résultat un peu surprenant, mais rien d'aberrant ; à en juger par sa distance de Cook, le retirer ne déplacerait les coefficients que de très peu.

### 2.4.7 Une démarche en quatre temps

> 🧭 **La checklist de vérification d'un GLM.**
> 1. **La famille et le lien conviennent-ils ?** Résidus quantiles aléatoires (QQ-plot) ; $X^2/\text{ddl}$ pour la surdispersion ; histogramme des observations.
> 2. **La forme de chaque effet est-elle bonne ?** Résidus (ou fréquences observées) contre chaque variable explicative, par classes ; Hosmer-Lemeshow pour la calibration ; ajouter un terme quadratique ou un GAM (2.5) en cas de courbure.
> 3. **Y a-t-il des observations influentes ?** Levier, distance de Cook ; refaire l'ajustement sans les observations suspectes pour voir si les conclusions changent.
> 4. **Le modèle est-il utile ?** Pseudo-$R^2$, AUC ou erreur de prévision, **sur des données de test** ; comparaison avec un modèle de référence simple.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.6, exercices 2.5, 2.9 et 2.10.

> ✅ **À retenir**
> - La **déviance** $D=2(\ell_{\text{sat}}-\ell)$ est l'équivalent GLM de la somme des carrés des résidus. Le **rapport de vraisemblance** (différence de déviances entre modèles emboîtés) est le test de référence ; avec une dispersion estimée, on utilise un test $F$.
> - Les **résidus de Pearson et de déviance** servent aux comptages ; pour des données discrètes, préférez les **résidus quantiles aléatoires** : normaux si le modèle est bon.
> - Pour des 0/1 individuels, la déviance **n'est pas** un test d'ajustement ; utilisez la calibration et le test de Hosmer-Lemeshow.
> - **AIC / BIC** comparent des modèles quelconques (plus petit = mieux), mais ne disent rien de la qualité absolue.
> - Contrôlez toujours : **dispersion**, **forme des effets**, **observations influentes**, **performance hors échantillon**.
