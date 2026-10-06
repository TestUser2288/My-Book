## 2.4 ➕ Pour aller plus loin : GLM tarifaires et théorie de la crédibilité

> 🧭 **Section optionnelle.** Elle ouvre le capot du GLM de la section 2.2 (déviance, tests, formes des variables continues, régularisation), présente la **théorie de la crédibilité**, l'outil historique de l'actuaire pour doser *données propres* et *information a priori*, puis compare le GLM à un boosting. Elle suppose acquis le volume II, chapitre 2 (GLM) et le volume III, chapitre 2 (boosting).

### 2.4.1 Sous le capot du GLM : déviance et tests

Un GLM de comptage décrit $E[N_i]=\mu_i=e_i\exp(x_i^\top\beta)$. On l'ajuste en maximisant la vraisemblance, et l'on compare des modèles par la **déviance**, qui mesure l'écart à un modèle parfait (un paramètre par observation) :
$$D=2\sum_i\Bigl[N_i\ln\frac{N_i}{\hat\mu_i}-(N_i-\hat\mu_i)\Bigr]\qquad(\text{avec } 0\ln0=0).$$
C'est deux fois la différence des log-vraisemblances, et c'est **l'équivalent, pour un modèle de Poisson, de la somme des carrés des résidus**. Pour trois contrats avec $N=(0,1,0)$ et $\hat\mu=(0{,}10\,;0{,}20\,;0{,}05)$ : $D=2\bigl[0{,}10+(\ln5-0{,}8)+0{,}05\bigr]={{h_dev|3}}$.

> 📐 **Test du rapport de vraisemblance.** Si le modèle $M_0$ (à $p_0$ paramètres) est contenu dans le modèle $M_1$ (à $p_1>p_0$), alors, sous $M_0$, $D_0-D_1\sim\chi^2_{p_1-p_0}$ approximativement : ajouter des variables diminue toujours la déviance, et le test dit si la baisse dépasse ce que le hasard donnerait. On l'utilise pour décider si une variable (ou un bloc de modalités) mérite sa place.

Construisons le modèle pas à pas sur 2022-2023 :

```python hide
formule0 = "nb_sinistres ~ 1"
etapes = [("taux global", "nb_sinistres ~ 1"),
          ("+ zone", "nb_sinistres ~ C(zone, Treatment('Zone C'))"),
          ("+ âge (7 classes)", "nb_sinistres ~ C(zone, Treatment('Zone C')) + C(classe_age, Treatment('40-49'))"),
          ("+ bonus-malus", "nb_sinistres ~ C(zone, Treatment('Zone C')) + C(classe_age, Treatment('40-49')) + bonus_malus"),
          ("+ puissance, usage, carburant, âge véhicule", formule)]
lignes = []; prec = None
for nom, fo in etapes:
    m_ = smf.glm(fo, tr, family=sm.families.Poisson(), offset=np.log(tr["exposition"])).fit()
    k = len(m_.params)
    dd = np.nan if prec is None else prec[0] - m_.deviance
    pv = np.nan if prec is None else stats.chi2.sf(dd, k - prec[1])
    lignes.append((nom, k, m_.deviance, m_.aic, dd, pv)); prec = (m_.deviance, k)
tab_dev = pd.DataFrame(lignes, columns=["modèle", "paramètres", "déviance", "AIC", "baisse de déviance", "p-valeur"]).set_index("modèle")
NUM("dev_nulle", tab_dev["déviance"].iloc[0]); NUM("dev_complet", tab_dev["déviance"].iloc[-1])
NUM("lr_zone", tab_dev["baisse de déviance"].iloc[1]); NUM("lr_age", tab_dev["baisse de déviance"].iloc[2]); NUM("lr_bm", tab_dev["baisse de déviance"].iloc[3])
NUM("lr_reste", tab_dev["baisse de déviance"].iloc[4])
y_h = np.array([0, 1, 0]); mu_h = np.array([0.10, 0.20, 0.05])
NUM("h_dev", deviance_poisson(y_h, mu_h))
```

```python hide-code
aff = pd.DataFrame({"paramètres": tab_dev["paramètres"], "déviance": tab_dev["déviance"].map("{:.1f}".format), "AIC": tab_dev["AIC"].map("{:.1f}".format),
                    "baisse de déviance": tab_dev["baisse de déviance"].map(lambda v: "" if np.isnan(v) else f"{v:.1f}"),
                    "p-valeur": tab_dev["p-valeur"].map(lambda v: "" if np.isnan(v) else f"{v:.1e}")})
print(aff.to_string())
```

Chaque étape fait baisser la déviance (de {{dev_nulle|int}} à {{dev_complet|int}}), et l'on mesure la contribution : la zone retire {{lr_zone|int}} (pour 5 paramètres), l'âge {{lr_age|int}} (6 paramètres), le bonus-malus {{lr_bm|int}} (1 paramètre), le reste {{lr_reste|int}}. Toutes ces baisses sont très supérieures à ce que donnerait le hasard (un $\chi^2$ à 5 degrés de liberté dépasse rarement 11). **La déviance est une somme sur 70 000 contrats et ne se lit qu'en comparaison** : sa valeur absolue ne dit rien.

> ⚠️ **Les résidus d'un modèle de comptage sont illisibles contrat par contrat.** Avec une moyenne de 0,06 sinistre par contrat, un résidu de déviance ne prend que deux ou trois valeurs distinctes. On vérifie donc l'adéquation en **regroupant** les contrats (par dixièmes du tarif, par classe d'âge, par zone) et en comparant sinistres observés et prédits dans chaque groupe, comme pour la courbe de calibration du volume III (section 5.2).

### 2.4.2 Variables continues : classes, splines, interactions

L'âge du conducteur est continu, mais son effet ne l'est pas : le risque est élevé avant 25 ans, puis presque plat. Trois façons de le coder : une **variable linéaire** (un seul coefficient : $\ln\mu$ varie à pente constante), des **classes** (une relativité par tranche, comme dans notre tarif) ou une **spline** (une courbe lisse à quelques degrés de liberté). Elles se départagent sur l'année suivante, avec la déviance **hors période** (2024) :

```python hide
def fit_pois(fo, data=tr):
    return smf.glm(fo, data, family=sm.families.Poisson(), offset=np.log(data["exposition"])).fit()
rest = "puissance + C(zone, Treatment('Zone C')) + bonus_malus + C(usage) + C(carburant) + age_vehicule"
y24n = te["nb_sinistres"].values; e24n = te["exposition"].values
def dev24(m_):
    return deviance_poisson(y24n, m_.predict(te, offset=np.zeros(len(te))) * e24n)
variantes = {"âge linéaire": fit_pois("nb_sinistres ~ age_conducteur + " + rest),
             "âge en 7 classes": freq,
             "âge par spline (5 d.l.)": fit_pois("nb_sinistres ~ bs(age_conducteur, df=5) + " + rest),
             "classes + interaction âge × usage": fit_pois(formule + " + C(classe_age, Treatment('40-49')):C(usage)")}
tab_v = pd.DataFrame({"paramètres": [len(m_.params) for m_ in variantes.values()],
                      "AIC (2022-2023)": [m_.aic for m_ in variantes.values()],
                      "déviance 2024": [dev24(m_) for m_ in variantes.values()]}, index=list(variantes))
plat_mod = fit_pois("nb_sinistres ~ 1"); dev_plat24 = dev24(plat_mod)
NUM("dv_lin", tab_v.loc["âge linéaire", "déviance 2024"]); NUM("dv_cl", tab_v.loc["âge en 7 classes", "déviance 2024"])
NUM("dv_sp", tab_v.loc["âge par spline (5 d.l.)", "déviance 2024"]); NUM("dv_int", tab_v.loc["classes + interaction âge × usage", "déviance 2024"])
NUM("dv_plat", dev_plat24)
m_int = variantes["classes + interaction âge × usage"]
lr_int = freq.deviance - m_int.deviance; df_int = int(round(m_int.df_model - freq.df_model))
NUM("lr_int", lr_int); NUM("df_int", df_int); NUM("p_int", stats.chi2.sf(lr_int, df_int))
```

```python hide-code
print(tab_v.round(1).to_string())
```

La variable **linéaire** est nettement moins bonne ({{dv_lin|int}} de déviance en 2024 contre {{dv_cl|int}} pour les sept classes) : le modèle impose une pente continue là où l'effet est un **saut** chez les jeunes conducteurs. La **spline** fait mieux que le linéaire mais pas aussi bien que les classes ({{dv_sp|int}}) : ici la vérité programmée est un palier (moins de 25 ans, plus de 70 ans), que des classes épousent mieux qu'une courbe lisse. Sur des données réelles, avec un effet plus progressif, la conclusion pourrait s'inverser ; on teste. Enfin l'**interaction** âge × usage n'apporte rien (baisse de déviance de {{lr_int|1}} pour {{df_int|int}} paramètres, $p={{p_int|2}}$) : **le test dit de ne pas la garder**, et la vérité programmée n'en contient pas. Un modèle sans interaction est un tarif plus lisible, plus stable et plus facile à justifier.

### 2.4.3 Régularisation : quand les cellules sont trop nombreuses

Imaginons maintenant un tarif plus fin : une relativité par **combinaison** zone × puissance × classe d'âge, soit plus de 300 cellules. Plusieurs sont presque vides, et l'estimateur du maximum de vraisemblance y dit n'importe quoi (une cellule à 8 années d'exposition et un sinistre « a » une fréquence de 12 %). La **régularisation** (volume II, section 1.5) pénalise les coefficients grands. Pour un modèle de Poisson, avec une pénalité de type ridge de force $\alpha$, on minimise $D(\beta)/(2n)+\tfrac{\alpha}{2}\lVert\beta\rVert_2^2$.

```python hide
from sklearn.linear_model import PoissonRegressor
cell = pd.get_dummies(pol["zone"] + "|" + pol["puissance"].astype(str) + "|" + pol["classe_age"], dtype=float)
princ = pd.get_dummies(pol[["zone", "classe_age", "usage", "carburant"]], dtype=float)
num = ((pol[["puissance", "bonus_malus", "age_vehicule"]] - pol[["puissance", "bonus_malus", "age_vehicule"]].mean()) / pol[["puissance", "bonus_malus", "age_vehicule"]].std())
Xc = pd.concat([princ, num, cell], axis=1)
X_cell_tr = Xc.loc[tr.index].values; X_cell_te = Xc.loc[te.index].values
y_tr = (tr["nb_sinistres"] / tr["exposition"]).values; e_tr = tr["exposition"].values
NUM("n_cellules", cell.shape[1])
lignes = []
for al in (1e-6, 1e-5, 1e-4, 1e-3, 1e-2):
    rg = PoissonRegressor(alpha=al, max_iter=500).fit(X_cell_tr, y_tr, sample_weight=e_tr)
    lignes.append((al, deviance_poisson(y24n, rg.predict(X_cell_te) * e24n)))
tab_reg = pd.DataFrame(lignes, columns=["alpha", "déviance 2024"]).set_index("alpha")
best = tab_reg["déviance 2024"].idxmin()
NUM("reg_best", best); NUM("reg_dev_best", tab_reg["déviance 2024"].min()); NUM("reg_dev_faible", tab_reg["déviance 2024"].iloc[0]); NUM("reg_dev_forte", tab_reg["déviance 2024"].iloc[-1])
```

```python
from sklearn.linear_model import PoissonRegressor
reg = PoissonRegressor(alpha=1e-4, max_iter=500)              # alpha = force de la pénalité (ridge)
reg.fit(X_cell_tr, y_tr, sample_weight=e_tr)                  # fréquence par unité d'exposition, pondérée par l'exposition
```

```python hide-code
print(tab_reg.round(1).to_string())
```

Sur les {{n_cellules|int}} cellules, la déviance de 2024 est mauvaise quand la pénalité est trop faible ({{reg_dev_faible|int}} pour $\alpha=10^{-6}$ : le modèle apprend le bruit des cellules vides), s'améliore jusqu'à un optimum ({{reg_dev_best|int}} pour $\alpha={{reg_best|sci}}$), puis se dégrade quand la pénalité écrase les relativités ({{reg_dev_forte|int}} pour $\alpha=10^{-2}$, le tarif plat valant {{dv_plat|int}}). Le réglage de $\alpha$ se fait, comme tout hyperparamètre, **hors période** ou par validation croisée par blocs d'années (volume III, section 1.5). Même à son optimum, le modèle à cellules ne fait pas mieux que le GLM sans cellules ({{dv_cl|int}}) : la finesse du tarif ne paie que si elle est domptée, et ne paie pas toujours.

### 2.4.4 La théorie de la crédibilité

La crédibilité répond à une question que l'on se pose chaque fois qu'un segment est petit : **dans quelle mesure faut-il croire l'expérience propre d'un groupe, par rapport à la moyenne du portefeuille ?** Si la zone F n'a que 40 années d'exposition et 6 sinistres (15 %), la moyenne de 6,6 % du portefeuille est plus fiable que le 15 % observé. À l'inverse, un segment de 10 000 années d'exposition doit être cru.

L'estimateur de crédibilité est une moyenne pondérée :
$$\hat\lambda_g=Z_g\,\bar x_g+(1-Z_g)\,\mu,\qquad Z_g=\frac{w_g}{w_g+k},$$
où $\bar x_g$ est la fréquence observée du groupe $g$, $\mu$ la moyenne générale, $w_g$ l'exposition du groupe et $k$ une constante, **le point de crédibilité à 50 %** : un groupe d'exposition $k$ a $Z=1/2$. Le coefficient $Z_g$ croît de 0 à 1 avec le volume.

**Un exemple à la main.** Avec $\mu=6{,}6$ %, $k=500$ années d'exposition : un groupe de 1 000 années à 5,0 % reçoit $Z=1\,000/1\,500=0{,}667$, d'où $0{,}667\times5{,}0+0{,}333\times6{,}6=5{,}5$ % ; un groupe de 50 années à 12 % reçoit $Z=50/550=0{,}091$, d'où $0{,}091\times12+0{,}909\times6{,}6=7{,}1$ %. Le premier est quasiment cru (on lui retire un tiers de son écart à la moyenne), le second est ramené presque entièrement vers la moyenne.

> 📐 **Pourquoi cette forme, et d'où vient $k$ ?** Le modèle de **Bühlmann–Straub** suppose que chaque groupe a un taux « vrai » $\Lambda_g$ tiré d'une loi de moyenne $\mu$ et de variance $a$ (l'**hétérogénéité entre groupes**), et que, sachant $\Lambda_g$, la fréquence observée sur une exposition $w$ a pour variance $s^2/w$ (la **variance de processus**). Parmi tous les estimateurs linéaires de $\Lambda_g$, le meilleur au sens des moindres carrés est la moyenne pondérée ci-dessus, avec $k=s^2/a$. On estime $s^2$ par la variance intra-groupes (entre années, pour un même groupe) et $a$ par la variance entre groupes corrigée du bruit de processus. **Le point de crédibilité est le rapport bruit sur signal.**
>
> Dans le cas de la fréquence, avec la loi Poisson–Gamma de la section 2.1.3 (taux $\lambda\Theta$, $\Theta$ de moyenne 1 et de variance $\alpha$), la crédibilité est **exacte** : la moyenne a posteriori de $\lambda\Theta$ sachant $N$ sinistres sur une exposition $e$ est $\lambda\,(r+N)/(r+\lambda e)$ avec $r=1/\alpha$, soit $Z\,(N/e)+(1-Z)\lambda$ avec $Z=e/(e+k)$ et $k=1/(\alpha\lambda)$. Pour un contrat individuel, $k=1/(0{,}4\times0{,}066)\approx38$ années d'exposition.

Appliquons-le à un vrai problème : des **cellules tarifaires** zone × puissance × usage ($6\times9\times2=108$ cellules, de très inégale taille). On estime la fréquence de chaque cellule sur 2022 et 2023, on applique la crédibilité de Bühlmann–Straub (années comme périodes d'un même groupe), puis on juge ces estimations sur **2024**, contre l'expérience brute et contre la moyenne générale.

```python hide
pol["cellule"] = pol["zone"] + "|" + pol["puissance"].astype(str) + "|" + pol["usage"]
g = pol[pol["annee"] <= 2023].groupby(["cellule", "annee"]).agg(n=("nb_sinistres", "sum"), e=("exposition", "sum")).reset_index()
fr = g.pivot(index="cellule", columns="annee", values="n") / g.pivot(index="cellule", columns="annee", values="e")
wt = g.pivot(index="cellule", columns="annee", values="e")
cs = buhlmann_straub(fr.values, wt.fillna(0).values)
Z = cs["Z"]; cred = Z * cs["xi"] + (1 - Z) * cs["mu"]
t24 = pol[pol["annee"] == 2024].groupby("cellule").agg(n=("nb_sinistres", "sum"), e=("exposition", "sum"))
dd = pd.DataFrame({"brute": cs["xi"], "crédibilité": cred, "moyenne": cs["mu"]}, index=fr.index).join(t24, how="inner")
dev_c = {k: deviance_poisson(dd["n"], (dd[k] * dd["e"]).clip(lower=1e-6)) for k in ("brute", "crédibilité", "moyenne")}
NUM("bs_mu", cs["mu"]); NUM("bs_k", cs["k"]); NUM("n_cell", len(fr)); NUM("z_med", np.median(Z)); NUM("z_min", Z.min()); NUM("z_max", Z.max())
NUM("w_med", np.median(cs["wi"]))
NUM("dc_brute", dev_c["brute"]); NUM("dc_cred", dev_c["crédibilité"]); NUM("dc_moy", dev_c["moyenne"])
fig, ax = plt.subplots(figsize=(6.6, 4.0))
ax.scatter(cs["wi"], 100 * cs["xi"], s=14, color=MUET, alpha=0.8, label="fréquence brute 2022-2023")
ax.scatter(cs["wi"], 100 * cred, s=14, color=BLEU, alpha=0.9, label="après crédibilité")
ax.axhline(100 * cs["mu"], color=ORANGE, lw=1.2, ls="--"); ax.set_xscale("log")
ax.set_xlabel("exposition de la cellule 2022-2023 (années, échelle logarithmique)"); ax.set_ylabel("fréquence annuelle (%)")
ax.set_title("La crédibilité ramène les petites cellules vers la moyenne"); ax.legend(frameon=False, fontsize=8, loc="upper right")
fig.tight_layout(); fig.savefig("figures/ch02-credibilite.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

![Fréquence annuelle de chacune des cellules tarifaires, brute (gris) et après crédibilité (bleu), selon leur exposition ; la ligne orange est la moyenne du portefeuille. Les petites cellules, très dispersées, sont ramenées vers la moyenne.](figures/ch02-credibilite.png)

L'estimation donne une moyenne de {{bs_mu|pc1}} %, un point de crédibilité de $k\approx{{bs_k|int}}$ années d'exposition (beaucoup plus que les 38 d'un contrat individuel, parce que les cellules rassemblent des centaines de contrats dont l'hétérogénéité *résiduelle* est faible) et une crédibilité médiane de {{z_med|pc0}} % pour une cellule médiane de {{w_med|int}} années d'exposition. Sur 2024, la déviance des fréquences de cellules est de {{dc_brute|int}} pour l'expérience brute, {{dc_moy|int}} pour la moyenne générale et **{{dc_cred|int}} pour l'estimateur de crédibilité** : il bat les deux, parce qu'il est brut là où les données sont abondantes et conservateur ailleurs.

> 🧪 **Crédibilité et GLM.** Les deux répondent au même besoin avec des outils différents. Le **GLM** partage l'information entre cellules *par la structure* (une relativité de zone et une relativité de puissance valent pour toutes les cellules : un modèle additif sur l'échelle logarithmique) ; la **crédibilité** la partage *par la moyenne* (une cellule est tirée vers le groupe). Dans la pratique, on les combine : le GLM donne la moyenne a priori de chaque cellule, et la crédibilité dose l'écart de l'expérience de la cellule à ce a priori. La théorie des modèles à effets aléatoires (volume II, section 1.7) en est la forme moderne.

### 2.4.5 GLM ou boosting ?

Le volume III a montré la supériorité fréquente du **gradient boosting** sur les tableaux de données. Pour la tarification, la question est : à quoi bon un GLM, plus rigide ? Comparons sur la fréquence, avec une objective de Poisson, 200 arbres peu profonds (huit feuilles), validés hors période :

```python hide
import lightgbm as lgb
cols = ["age_conducteur", "puissance", "zone", "bonus_malus", "usage", "carburant", "age_vehicule"]
Xg = pol[cols].copy()
for c in ("zone", "usage", "carburant"):
    Xg[c] = Xg[c].astype("category")
def lgbm(mono=None, n=200):
    p = dict(objective="poisson", n_estimators=n, learning_rate=0.03, num_leaves=8, min_child_samples=300, subsample=0.8,
             subsample_freq=1, colsample_bytree=0.8, random_state=0, n_jobs=1, verbose=-1, deterministic=True, force_row_wise=True)
    if mono: p["monotone_constraints"] = mono
    return lgb.LGBMRegressor(**p).fit(Xg.loc[tr.index], y_tr, sample_weight=e_tr)
mono = [0, 1, 0, 1, 0, 0, 0]
g1 = lgbm(); g2 = lgbm(mono); g3 = lgbm(None, 600)
dev_g = {"boosting, 200 arbres": deviance_poisson(y24n, g1.predict(Xg.loc[te.index]) * e24n),
         "boosting, contraintes de monotonie": deviance_poisson(y24n, g2.predict(Xg.loc[te.index]) * e24n),
         "boosting, 600 arbres": deviance_poisson(y24n, g3.predict(Xg.loc[te.index]) * e24n)}
tab_g = pd.DataFrame({"déviance 2024": {"tarif plat": dev_plat24, "GLM (âge en classes)": dev24(freq), **dev_g}})
NUM("dg_glm", dev24(freq)); NUM("dg_b200", dev_g["boosting, 200 arbres"]); NUM("dg_bmono", dev_g["boosting, contraintes de monotonie"]); NUM("dg_b600", dev_g["boosting, 600 arbres"])
```

```python hide-code
print(tab_g.round(1).to_string())
```

Le GLM obtient {{dg_glm|int}} ; le boosting {{dg_b200|int}} avec 200 arbres, {{dg_bmono|int}} avec des contraintes de monotonie sur la puissance et le bonus-malus, et {{dg_b600|int}} avec 600 arbres (il dérive : plus d'arbres, c'est plus de surapprentissage). **Le boosting ne fait pas mieux que le GLM ici**, et ce n'est pas un hasard : la vérité programmée est **multiplicative et sans interaction**, exactement la forme d'un GLM. Le boosting n'a rien à découvrir que le GLM ne sache déjà, et il paie sa flexibilité en variance.

Sur des données réelles, où des interactions et des non-linéarités existent, le boosting l'emporte parfois ; les assureurs l'utilisent alors de trois manières. (1) **Comme référence** : si le boosting bat nettement le GLM, il y a une structure que le GLM manque, à chercher. (2) **Comme source de variables** : on repère les interactions importantes (par SHAP, volume III, section 5.3) et on les ajoute au GLM. (3) **En production**, avec contraintes de monotonie et explicabilité, quand le régulateur et le marché l'acceptent. Ce qui compte, ce n'est pas l'algorithme : c'est la **lisibilité** du tarif, la **stabilité** de ses relativités d'une année à l'autre, et la capacité à **justifier** chaque écart de prix.

> ✅ **À retenir.**
> - On compare des GLM par leur **déviance** et par un test du rapport de vraisemblance ; la valeur absolue de la déviance ne signifie rien.
> - La forme d'une variable continue (linéaire, classes, spline) se choisit **hors période** ; une interaction se garde seulement si elle améliore nettement la déviance.
> - La **régularisation** domestique les cellules trop fines ; son intensité se règle hors période.
> - La **crédibilité** $Z=w/(w+k)$ pèse expérience propre et moyenne ; $k$ est le rapport entre variance de processus et hétérogénéité entre groupes. Elle bat l'expérience brute et la moyenne générale sur des cellules inégales.
> - Un boosting ne bat pas un GLM quand la structure vraie est multiplicative et additive ; c'est avant tout un étalon, pas un remplaçant.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7 et exercices 2.9 à 2.10 (déviance et test, crédibilité de Bühlmann–Straub, GLM contre boosting).
