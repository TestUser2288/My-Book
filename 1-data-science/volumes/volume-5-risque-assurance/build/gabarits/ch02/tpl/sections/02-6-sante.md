## 2.6 ➕ Pour aller plus loin : l'assurance santé

> 🧭 **Section optionnelle.** L'assurance santé réutilise la boîte à outils de la tarification (GLM, Gamma/Tweedie, validation hors période), mais elle pose des problèmes d'une autre nature : le coût est **continu et positif presque toujours** (on consomme tous des soins), il est **concentré** sur une minorité de personnes malades, et **le choix du niveau de garantie dépend de la santé de l'assuré**. Les données sont celles de `sante_assures.csv` (simulées).

### 2.6.1 Que coûte la santé ?

Le fichier compte {{n_sante|int}} lignes *assuré-année* (2022 à 2024) pour {{n_membres|int}} personnes différentes, soit {{expo_s|int}} années d'exposition. Le coût annuel moyen est de {{cpe_moy|int}} € par année d'exposition. Quatre postes le composent.

```python hide
sante["cpe"] = sante["cout_total"] / sante["exposition"]
sante["tranche"] = pd.cut(sante["age"], [-1, 17, 29, 44, 59, 74, 120], labels=["0-17", "18-29", "30-44", "45-59", "60-74", "75+"])
postes = {"consultations": "cout_consultations", "hospitalisation": "cout_hospitalisation", "pharmacie": "cout_pharmacie", "dentaire": "cout_dentaire"}
parts = {k: sante[v].sum() / sante["cout_total"].sum() for k, v in postes.items()}
NUM("n_membres", sante["id_assure"].nunique()); NUM("expo_s", sante["exposition"].sum()); NUM("cpe_moy", sante["cout_total"].sum() / sante["exposition"].sum())
for k, cle in (("consultations", "p_cons"), ("hospitalisation", "p_hosp"), ("pharmacie", "p_pharma"), ("dentaire", "p_dent")):
    NUM(cle, parts[k])
cs = np.sort(sante["cout_total"].values)[::-1]; cum = np.cumsum(cs) / cs.sum()
for frac, cle in ((0.01, "top1"), (0.05, "top5"), (0.10, "top10"), (0.20, "top20")):
    NUM(cle, cum[int(frac * len(cs)) - 1])
NUM("zero_part", (sante["cout_total"] == 0).mean())
tr_age = sante.groupby(["tranche", "ald"], observed=True).apply(lambda g: g["cout_total"].sum() / g["exposition"].sum()).unstack()
NUM("ald_x", (sante.loc[sante["ald"] == 1, "cout_total"].sum() / sante.loc[sante["ald"] == 1, "exposition"].sum()) / (sante.loc[sante["ald"] == 0, "cout_total"].sum() / sante.loc[sante["ald"] == 0, "exposition"].sum()))
NUM("ald_part", sante["ald"].mean())
NUM("cpe_jeune", sante.loc[sante["tranche"] == "18-29", "cout_total"].sum() / sante.loc[sante["tranche"] == "18-29", "exposition"].sum())
NUM("cpe_vieux", sante.loc[sante["tranche"] == "75+", "cout_total"].sum() / sante.loc[sante["tranche"] == "75+", "exposition"].sum())
fig, ax = plt.subplots(1, 2, figsize=(10.5, 4.0))
xs = np.arange(1, len(cs) + 1) / len(cs); asc = np.cumsum(cs[::-1]) / cs.sum()
ax[0].plot(xs, asc, color=BLEU, lw=2); ax[0].plot([0, 1], [0, 1], color=style.AXE, ls=":", lw=1)
ax[0].set_xlabel("part cumulée des assurés-années (du moins au plus coûteux)"); ax[0].set_ylabel("part cumulée du coût")
ax[0].set_title("Une minorité porte l'essentiel du coût")
for etat, col, nom in ((0, BLEU, "sans ALD"), (1, ORANGE, "avec ALD")):
    ax[1].plot(range(len(tr_age)), tr_age[etat], "o-", color=col, lw=1.8, ms=4, label=nom)
ax[1].set_xticks(range(len(tr_age))); ax[1].set_xticklabels(tr_age.index.astype(str)); ax[1].set_xlabel("tranche d'âge"); ax[1].set_ylabel("coût par année d'exposition (€)")
ax[1].set_title("Le coût selon l'âge et l'affection longue durée"); ax[1].legend(frameon=False)
fig.tight_layout(); fig.savefig("figures/ch02-sante.png", dpi=200, bbox_inches="tight"); plt.close(fig)
```

```python hide-code
print(pd.Series({k: f"{100 * v:.0f} %" for k, v in parts.items()}, name="part du coût").to_string())
```

L'**hospitalisation** pèse {{p_hosp|pc0}} % du coût, les consultations {{p_cons|pc0}} %, la pharmacie {{p_pharma|pc0}} %, le dentaire {{p_dent|pc0}} %. Surtout, le coût est **très concentré** : les 5 % d'assurés-années les plus coûteux représentent {{top5|pc0}} % du coût total, les 10 % les plus coûteux {{top10|pc0}} %, et le 1 % le plus coûteux à lui seul {{top1|pc0}} %. C'est une concentration moins extrême que celle des sinistres automobiles (section 2.1.5), mais elle domine la gestion du risque : **le coût d'un portefeuille santé se joue sur quelques malades**.

![À gauche : courbe de concentration du coût (plus elle s'éloigne de la diagonale, plus le coût est concentré sur peu d'assurés). À droite : coût annuel par année d'exposition selon la tranche d'âge, avec ou sans affection de longue durée (ALD) ; les points avec ALD aux âges extrêmes reposent sur peu d'assurés.](figures/ch02-sante.png)

Deux facteurs dominent. L'**âge** : de {{cpe_jeune|int}} € pour les 18-29 ans à {{cpe_vieux|int}} € pour les plus de 75 ans. Et l'**affection de longue durée** (ALD, maladie chronique) : elle concerne {{ald_part|pc0}} % des lignes et multiplie le coût par {{ald_x|1}} environ. Contrairement à l'automobile, **la part des assurés sans aucun coût est quasi nulle** ({{zero_part|pc3}} % des lignes) : tout le monde consomme au moins de la pharmacie. Les modèles « à excès de zéros » ou « à deux parties » (probabilité d'avoir un coût, puis montant) sont donc inutiles ici.

### 2.6.2 Modéliser le coût annuel

Le coût par année d'exposition étant positif et asymétrique, on le modélise par un **GLM Gamma à lien logarithmique**, pondéré par l'exposition (une ligne couvrant trois mois pèse un quart d'une ligne d'un an). On compare quatre tarifs, du plus simple au plus fin, sur 2022-2023 pour estimer et sur 2024 pour juger :

```python
tr_s = sante[sante["annee"] <= 2023]
modele = smf.glm("cpe ~ age + I(age ** 2) + ald + C(niveau) + C(sexe)", tr_s,
                 family=sm.families.Gamma(sm.families.links.Log()), freq_weights=tr_s["exposition"]).fit()
```

```python hide
te_s = sante[sante["annee"] == 2024].copy()
def gamma_fit(fo):
    return smf.glm(fo, tr_s, family=sm.families.Gamma(sm.families.links.Log()), freq_weights=tr_s["exposition"]).fit()
mods = {"plat": None, "âge": gamma_fit("cpe ~ age + I(age ** 2)"), "âge + ALD": gamma_fit("cpe ~ age + I(age ** 2) + ald"),
        "âge + ALD + niveau + sexe": modele}
ys = te_s["cout_total"].values; es = te_s["exposition"].values
plat_s = tr_s["cout_total"].sum() / tr_s["exposition"].sum()
res_s = []
for nom, m_ in mods.items():
    pred = np.full(len(te_s), plat_s) if m_ is None else m_.predict(te_s).values
    res_s.append((nom, lorenz_gini(pred * es, ys, es)[2], (pred * es).sum() / ys.sum()))
tab_s = pd.DataFrame(res_s, columns=["tarif", "Gini 2024", "prévu / observé"]).set_index("tarif")
NUM("gs_age", tab_s.loc["âge", "Gini 2024"]); NUM("gs_ald", tab_s.loc["âge + ALD", "Gini 2024"]); NUM("gs_tout", tab_s.loc["âge + ALD + niveau + sexe", "Gini 2024"])
NUM("gs_plat", tab_s.loc["plat", "Gini 2024"]); NUM("cal_tout", tab_s.loc["âge + ALD + niveau + sexe", "prévu / observé"])
rng = np.random.default_rng(3)
alea_s = [lorenz_gini(rng.random(len(ys)) * es, ys, es)[2] for _ in range(100)]
NUM("gs_alea", np.std(alea_s))
```

```python hide-code
print(tab_s.round(3).to_string())
```

L'indice de Gini passe de {{gs_plat|2}} pour le tarif plat à {{gs_age|2}} avec l'âge seul, {{gs_ald|2}} en ajoutant l'ALD et {{gs_tout|2}} avec le niveau de garantie et le sexe (bruit d'un tarif aléatoire : {{gs_alea|3}}). L'**ALD** est le gain le plus important : c'est une information que l'assureur connaît (par la déclaration, les remboursements précédents) et qui sépare nettement les coûts. Le niveau apporte encore, mais pour une raison qui n'est pas du tout celle que l'on croit : c'est l'objet de la section suivante. Le tarif complet est calibré à {{cal_tout|pc0}} % du coût observé en 2024 (prévu sur observé).

### 2.6.3 Sélection adverse et aléa moral

Regardons le coût selon le niveau de garantie (basique, confort, premium) :

```python hide
nv = sante.groupby("niveau").apply(lambda g: pd.Series({"coût par année d'exposition": g["cout_total"].sum() / g["exposition"].sum(), "part d'ALD": g["ald"].mean(), "âge moyen": g["age"].mean()}))
nv = nv.loc[["basique", "confort", "premium"]]
raw_conf = nv.loc["confort", "coût par année d'exposition"] / nv.loc["basique", "coût par année d'exposition"]
raw_prem = nv.loc["premium", "coût par année d'exposition"] / nv.loc["basique", "coût par année d'exposition"]
NUM("raw_conf", raw_conf); NUM("raw_prem", raw_prem)
NUM("ald_bas", nv.loc["basique", "part d'ALD"]); NUM("ald_prem", nv.loc["premium", "part d'ALD"])
NUM("age_bas", nv.loc["basique", "âge moyen"]); NUM("age_prem", nv.loc["premium", "âge moyen"])
mfull = smf.glm("cpe ~ age + I(age ** 2) + ald + C(niveau, Treatment('basique')) + C(sexe)", sante, family=sm.families.Gamma(sm.families.links.Log()), freq_weights=sante["exposition"]).fit()
ci_f = np.exp(mfull.conf_int())
cn = "C(niveau, Treatment('basique'))[T.confort]"; pn = "C(niveau, Treatment('basique'))[T.premium]"
NUM("adj_conf", np.exp(mfull.params[cn])); NUM("adj_prem", np.exp(mfull.params[pn])); NUM("adj_prem_bas", ci_f.loc[pn, 0]); NUM("adj_prem_haut", ci_f.loc[pn, 1])
prem = sante[sante["niveau"] == "premium"].copy()
prem_bas = prem.assign(niveau="basique")
A = (mfull.predict(prem_bas) * prem["exposition"]).sum() / prem["exposition"].sum()          # les membres premium, s'ils avaient le comportement « basique »
B = (mfull.predict(prem) * prem["exposition"]).sum() / prem["exposition"].sum()               # les mêmes, au niveau premium
Cb = nv.loc["basique", "coût par année d'exposition"]
NUM("selection", A / Cb); NUM("comportement", B / A); NUM("total_sel", B / Cb)
tab_nv = nv.copy(); tab_nv["coût par année d'exposition"] = tab_nv["coût par année d'exposition"].round(0)
tab_nv["part d'ALD"] = (100 * tab_nv["part d'ALD"]).round(1); tab_nv["âge moyen"] = tab_nv["âge moyen"].round(1)
```

```python hide-code
print(tab_nv.to_string())
```

Le niveau « premium » coûte {{raw_prem|1}} fois le niveau « basique » ({{raw_conf|2}} pour « confort »). On y verrait, à tort, la conséquence d'une meilleure garantie. Deux mécanismes très différents s'y mélangent :

- la **sélection adverse** : les personnes malades choisissent plus souvent la meilleure garantie (la part d'ALD passe de {{ald_bas|pc0}} % en basique à {{ald_prem|pc0}} % en premium) ; l'âge moyen, lui, est le même ({{age_bas|1}} et {{age_prem|1}} ans) ;
- l'**aléa moral** : une garantie plus généreuse **change le comportement** (on consulte plus, on prend le dentaire).

Pour les séparer, on ajuste un modèle sur l'âge, l'ALD et le sexe : l'effet « niveau » ajusté vaut alors **{{adj_prem|2}}** pour premium (intervalle à 95 % de {{adj_prem_bas|2}} à {{adj_prem_haut|2}}) et {{adj_conf|2}} pour confort. La décomposition est multiplicative : le rapport de {{total_sel|2}} (proche du rapport brut, mais calculé avec les valeurs ajustées du modèle) vaut {{selection|2}} de **sélection** (leur coût si on leur donnait le comportement « basique », par rapport au coût des assurés basique) fois {{comportement|2}} d'**aléa moral**. Les deux effets pèsent autant l'un que l'autre.

> ⚠️ **Pourquoi c'est un problème de tarif.** Si l'on tarife la différence entre niveaux sur le rapport brut ({{raw_prem|1}}), on facture à l'assuré une différence de comportement qui est en réalité, pour moitié, une différence de santé : le prix du premium devient prohibitif pour ceux qui n'ont pas d'ALD, qui quittent alors le niveau, ce qui élève encore le coût moyen des restants. C'est la **spirale d'antisélection** classique. L'assureur doit tarifer le niveau sur la **composition réelle** de ses assurés (et la surveiller), et se protéger par des délais de carence, une sélection médicale ou une **mutualisation** assumée.

### 2.6.4 Table de morbidité et mutualisation

Une **table de morbidité** donne, par âge, la fréquence et le coût moyen des événements de santé. On la lit ici par tranche d'âge : le nombre d'hospitalisations pour 1 000 années d'exposition, le coût moyen d'un séjour, le nombre annuel de consultations et le coût annuel.

```python hide
tm = sante.groupby("tranche", observed=True).apply(lambda g: pd.Series({
    "hospitalisations / 1000 ans": 1000 * g["nb_hospitalisations"].sum() / g["exposition"].sum(),
    "coût moyen d'un séjour (€)": g["cout_hospitalisation"].sum() / max(g["nb_hospitalisations"].sum(), 1),
    "consultations / an": g["nb_consultations"].sum() / g["exposition"].sum(),
    "coût annuel (€)": g["cout_total"].sum() / g["exposition"].sum(),
    "exposition (ans)": g["exposition"].sum()}))
NUM("hosp_jeune", tm.loc["0-17", "hospitalisations / 1000 ans"]); NUM("hosp_vieux", tm.loc["75+", "hospitalisations / 1000 ans"])
NUM("sejour_min", tm["coût moyen d'un séjour (€)"].min()); NUM("sejour_max", tm["coût moyen d'un séjour (€)"].max())
NUM("cons_jeune", tm.loc["0-17", "consultations / an"]); NUM("cons_vieux", tm.loc["75+", "consultations / an"])
e_tot = sante["exposition"].sum(); c_tot = sante["cout_total"].sum()
jeunes = sante["tranche"].isin(["0-17", "18-29"])
e_j = sante.loc[jeunes, "exposition"].sum(); c_j = sante.loc[jeunes, "cout_total"].sum()
NUM("part_jeunes_s", e_j / e_tot); NUM("cpe_jeunes", c_j / e_j); NUM("surprix", (c_tot / e_tot) / (c_j / e_j) - 1)
depart = 0.30
c_apres = (c_tot - depart * c_j) / (e_tot - depart * e_j)
NUM("prime_apres", c_apres); NUM("hausse_apres", c_apres / (c_tot / e_tot) - 1)
```

```python hide-code
print(tm.round(1).to_string())
```

Trois régularités. Les hospitalisations croissent avec l'âge : de {{hosp_jeune|int}} pour 1 000 années d'exposition chez les 0-17 ans à {{hosp_vieux|int}} chez les plus de 75 ans. Les consultations aussi (de {{cons_jeune|1}} à {{cons_vieux|1}} par an). En revanche, **le coût moyen d'un séjour varie peu et sans tendance nette** ({{sejour_min|int}} € à {{sejour_max|int}} € selon la tranche d'âge) : c'est la *fréquence*, pas la gravité, qui augmente avec l'âge. On retrouve la décomposition fréquence × sévérité de la section 2.2.

**Mutualiser, ou tarifer par âge ?** Une mutuelle peut appliquer une **prime unique** (la mutualisation) ou une prime par âge. Avec une prime unique égale au coût moyen ({{cpe_moy|int}} €), les assurés de moins de 30 ans (qui représentent {{part_jeunes_s|pc0}} % de l'exposition) paient {{surprix|pc0}} % **de plus** que leur coût ({{cpe_jeunes|int}} € par an), et subventionnent les autres. C'est un choix de solidarité, qui a un prix : si 30 % des moins de 30 ans partent (parce qu'un concurrent leur propose moins cher), la prime d'équilibre des restants passe à {{prime_apres|int}} €, soit **{{hausse_apres|pc1}} % de plus**, ce qui incite d'autres bons risques à partir à leur tour. La solidarité n'est tenable que si elle est **encadrée** (obligation d'assurance, règles de tarification communes pour tout le marché) ou compensée (ajustement de risque entre assureurs).

### 2.6.5 Inflation médicale, grands risques et ajustement de risque

**Tendance.** Les coûts de santé progressent avec les prix, mais aussi avec la fréquence de consommation. Un modèle qui contrôle l'âge, l'ALD, le niveau et le sexe, et ajoute l'année, estime la tendance annuelle du coût à l'unité d'exposition.

```python hide
mt = smf.glm("cpe ~ age + I(age ** 2) + ald + C(niveau) + C(sexe) + I(annee - 2022)", sante, family=sm.families.Gamma(sm.families.links.Log()), freq_weights=sante["exposition"]).fit()
NUM("tend_sante", np.exp(mt.params["I(annee - 2022)"]) - 1)
NUM("tend_bas", np.exp(mt.conf_int().loc["I(annee - 2022)", 0]) - 1); NUM("tend_haut", np.exp(mt.conf_int().loc["I(annee - 2022)", 1]) - 1)
gros = sante[sante["cout_total"] > 10000]
NUM("gros_part", gros["cout_total"].sum() / sante["cout_total"].sum()); NUM("gros_n", len(gros) / len(sante))
NUM("gros_seuil_n", len(gros))
```

L'estimation donne {{tend_sante|pc1}} % par an (intervalle à 95 % de {{tend_bas|pc1}} % à {{tend_haut|pc1}} %). La vérité programmée est une inflation de 3 % sur le coût unitaire des consultations et des hospitalisations, nulle sur les autres postes : le résultat global se situe donc naturellement un peu en dessous de 3 %. **Une tendance se projette pour l'année tarifée** : sans ajustement, un tarif construit sur les années passées est d'avance en retard.

**Grands risques.** Les {{gros_seuil_n|int}} lignes de plus de 10 000 € de coût annuel ne représentent que {{gros_n|pc1}} % des lignes, mais {{gros_part|pc0}} % du coût. Comme en automobile (section 2.1.5), on les traite à part : on **écrête** le coût individuel dans le tarif et l'on met en commun la charge au-delà (une **mutualisation des grands risques** entre assureurs, ou une réassurance : chapitre 6).

**Ajustement de risque.** Quand plusieurs assureurs se partagent un même marché obligatoire à prime commune, celui qui attire les malades est pénalisé. On corrige par un **ajustement de risque** : chaque assureur reverse ou reçoit une compensation fonction du profil de ses assurés (âge, sexe, ALD), calculée à partir d'un modèle de coût comme celui de la section 2.6.2. C'est l'application la plus directe de ce que nous avons fait, avec un enjeu politique : ce qu'on compense (l'âge, l'ALD) et ce qu'on ne compense pas (le comportement) se décide par la loi.

> ✅ **À retenir.**
> - Le coût de santé est **positif presque toujours** (un GLM Gamma convient, pas de modèle à excès de zéros) et **très concentré** sur quelques assurés.
> - Les facteurs dominants sont l'**âge** et l'**affection de longue durée** ; le coût d'un séjour varie peu avec l'âge, c'est la **fréquence** qui croît.
> - L'effet brut du niveau de garantie mélange **sélection adverse** et **aléa moral** ; un modèle ajusté permet de les séparer (ici, à parts égales).
> - Une prime **unique** subventionne les jeunes ; si ceux-ci partent, la prime d'équilibre des restants monte (spirale d'antisélection) : la solidarité demande un cadre.
> - Les grands risques s'écrêtent et se mutualisent ; l'**ajustement de risque** compense les différences de profil entre assureurs.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.9 et exercice 2.14 (coût santé, sélection adverse et aléa moral, table de morbidité).
