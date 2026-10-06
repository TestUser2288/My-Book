## 1.5 ➕ PD, LGD, EAD et pertes de crédit attendues (IFRS 9)

> 🧭 **Section optionnelle.** Elle prolonge le score vers ce que la comptabilité réclame : un **montant en euros**, la perte que le portefeuille devrait subir. Les paramètres d'exemple (seuils d'étapes, pondérations de scénarios) sont **illustratifs** ; la norme IFRS 9 est citée dans l'état de nos connaissances à la rédaction (2026) et ses exigences exactes sont à vérifier dans le texte en vigueur. Rien ici n'est un conseil comptable.

Un score donne une probabilité. Une banque doit **provisionner** des euros. Le passage de l'un à l'autre est une multiplication de trois grandeurs, que l'on modélise **séparément** parce qu'elles ne s'expliquent pas par les mêmes causes : la **probabilité de défaut** (PD), la **perte en cas de défaut** (LGD, *loss given default*) et l'**exposition au défaut** (EAD, *exposure at default*). La **perte attendue** (*expected credit loss*, ECL) d'un prêt est

$$\text{ECL}=\text{PD}\times\text{LGD}\times\text{EAD}.$$

Pour un prêt de 10 000 € avec une PD de 3 %, une LGD de 45 % et une EAD de 10 000 €, la perte attendue est $0{,}03\times0{,}45\times10\,000=135\ €$. Cette perte n'est pas un risque, c'est un **coût prévisible** : la banque la couvre par le taux d'intérêt et par ses provisions. Le **risque** proprement dit (l'écart autour de cette moyenne) relève du capital (chapitre 4).

```python hide
import statsmodels.api as sm
from scipy.stats import binomtest
lg = pd.read_csv("donnees/recouvrements.csv")
rv = pd.read_csv("donnees/revolving_defauts.csv")
pf = pd.read_csv("donnees/portefeuille_ifrs9.csv")
```

### 1.5.1 La PD : douze mois ou toute la vie

Deux horizons coexistent. La **PD à 12 mois** est la probabilité de défaut dans l'année qui vient, celle que donne notre grille. La **PD sur la durée de vie** est la probabilité de défaut avant l'échéance du prêt, forcément plus grande. Si le risque annuel est constant et vaut $h$, la probabilité de **survivre** $t$ années est $(1-h)^t$, d'où

$$\text{PD}_{\text{cumulée}}(T)=1-(1-h)^T,\qquad \text{PD marginale de l'année } t=(1-h)^{t-1}\,h.$$

Pour $h=3\ \%$ : $1-0{,}97^3=8{,}7\ \%$ sur trois ans, $1-0{,}97^5=14{,}1\ \%$ sur cinq ans, avec des probabilités marginales de défaut de 3,00 %, 2,91 %, 2,82 %… qui diminuent un peu parce qu'il reste moins de survivants. L'hypothèse d'un risque constant est une simplification : en réalité, le risque dépend de l'âge du prêt, de la conjoncture et de la note, qui migre (section 1.6 donne la version « matrice de transition » de la même idée).

> 💡 **Pourquoi deux PD ?** Parce que la norme IFRS 9 demande de provisionner tantôt sur un an, tantôt sur la vie entière, selon l'état du prêt (1.5.5). La PD à 12 mois de la grille ne suffit pas toujours.

### 1.5.2 La LGD : ce que l'on perd vraiment

La LGD est la **part de l'exposition que l'on ne récupère pas** après le défaut : $\text{LGD}=1-\dfrac{\text{récupérations actualisées}}{\text{EAD}}$. Elle dépend de la **garantie** (une caution, un nantissement), du **recouvrement** (frais, délais) et du moment. Le fichier `recouvrements.csv` donne, pour 6 000 prêts entrés en défaut, la perte réellement subie en part de l'exposition, supposée **déjà actualisée** (c'est la convention de ce chapitre) ; il indique aussi le délai de recouvrement, d'une durée moyenne de 19 mois et demi, car un euro récupéré dans près de vingt mois vaut moins d'un euro aujourd'hui (à 6 % par an, environ 0,91 €).

Regardons d'abord la **distribution**, qui n'a rien d'une cloche :

```python hide
fig, axs = plt.subplots(1, 2, figsize=(9.4, 3.4))
axs[0].hist(lg["lgd_realisee"], bins=40, color=BLEU, alpha=0.85)
axs[0].set_xlabel("LGD réalisée (part de l'exposition perdue)"); axs[0].set_ylabel("prêts en défaut"); axs[0].set_title("Distribution de la LGD")
for g_, col in [("aucune", ROUGE), ("nantissement", ORANGE), ("caution", AQUA)]:
    axs[1].hist(lg.loc[lg["garantie"] == g_, "lgd_realisee"], bins=25, density=True, histtype="step", lw=1.8, color=col, label=f"{g_} (moyenne {lg.loc[lg['garantie'] == g_, 'lgd_realisee'].mean():.2f})")
axs[1].set_xlabel("LGD réalisée"); axs[1].set_ylabel("densité"); axs[1].set_title("Selon la garantie"); axs[1].legend(frameon=False, fontsize=8.5, loc="upper center")
fig.tight_layout(); fig.savefig("figures/ch01-lgd.png", dpi=200, bbox_inches="tight"); plt.close(fig)
print("NUM lgd_moy", round(float(lg["lgd_realisee"].mean()), 3)); print("NUM lgd_zero", round(float((lg["lgd_realisee"] == 0).mean()), 3))
print("NUM lgd_un", round(float((lg["lgd_realisee"] > 0.95).mean()), 3)); print("NUM delai_moy", round(float(lg["delai_recouvrement_mois"].mean()), 1))
print("NUM pv_6", round(float(1.06 ** (-lg["delai_recouvrement_mois"].mean() / 12)), 3))
for g_ in ("aucune", "caution", "nantissement"): print("NUM lgd", g_, round(float(lg.loc[lg["garantie"] == g_, "lgd_realisee"].mean()), 3), int((lg["garantie"] == g_).sum()))
```
<!--sortie-->
```text
NUM lgd_moy 0.459
NUM lgd_zero 0.119
NUM lgd_un 0.091
NUM delai_moy 19.5
NUM pv_6 0.91
NUM lgd aucune 0.609 2993
NUM lgd caution 0.269 1852
NUM lgd nantissement 0.373 1155
```

![Distribution de la perte en cas de défaut : en U (beaucoup de pertes quasi nulles ou quasi totales), et très différente selon la garantie.](figures/ch01-lgd.png)

La LGD moyenne est de 46 %. La forme est **en U** : 12 % des prêts sont intégralement récupérés (perte nulle), 9 % ne le sont presque pas du tout (perte supérieure à 95 %), et le reste se répartit entre les deux. La moyenne par garantie est très contrastée : **61 %** sans garantie (2 993 prêts), **37 %** avec nantissement (1 155 prêts), **27 %** avec caution (1 852 prêts).

Comment modéliser une grandeur bornée entre 0 et 1, en forme de U ? Quatre candidats, comparés sur 30 % de prêts de test (garantie, objet et montant comme variables) :

- la **moyenne globale** (la référence naïve) ;
- la **régression linéaire**, qui peut sortir de $[0,1]$ ;
- la **régression « fractionnelle »** : un GLM binomial avec lien logit, appliqué à la LGD prise comme une proportion (volume II, section 2.2 pour le lien logit), qui reste dans $[0,1]$ ;
- un **modèle en deux étapes** : la probabilité d'une perte nulle (régression logistique), puis la LGD moyenne parmi les pertes non nulles (régression fractionnelle).

```python hide-code
from sklearn.model_selection import train_test_split
ltr, lte = train_test_split(lg, test_size=0.3, random_state=1)
def conc(d): return pd.get_dummies(d[["garantie", "objet"]], drop_first=True).astype(float).assign(ead=np.log(d["ead"]) - 9)
Xl = sm.add_constant(conc(ltr)); Xt = sm.add_constant(conc(lte)).reindex(columns=Xl.columns)
p_ols = np.clip(sm.OLS(ltr["lgd_realisee"], Xl).fit().predict(Xt), 0, 1)
p_fr = sm.GLM(ltr["lgd_realisee"], Xl, family=sm.families.Binomial()).fit().predict(Xt)
zero = (ltr["lgd_realisee"] == 0).astype(int); pz = sm.Logit(zero, Xl).fit(disp=0).predict(Xt)
pos = ltr[ltr["lgd_realisee"] > 0]; pm = sm.GLM(pos["lgd_realisee"], Xl.loc[pos.index], family=sm.families.Binomial()).fit().predict(Xt)
p_2 = (1 - pz) * pm
naif = np.full(len(lte), ltr["lgd_realisee"].mean())
# plafond : la vraie espérance de la LGD, connue par construction (vérité programmée)
mu_vrai = 1 / (1 + np.exp(-(-0.2 + 1.0 * (lte["garantie"] == "aucune") - 0.7 * (lte["garantie"] == "caution") - 0.2 * (lte["garantie"] == "nantissement") + 0.25 * (lte["objet"] == "conso"))))
p_vrai_l = 0.88 * mu_vrai
yl = lte["lgd_realisee"].values
def r2(p): return 1 - np.sum((p - yl) ** 2) / np.sum((yl - yl.mean()) ** 2)
tl = pd.DataFrame({m: [np.mean(np.abs(p - yl)), np.sqrt(np.mean((p - yl) ** 2)), r2(np.asarray(p))] for m, p in
                   [("moyenne globale", naif), ("régression linéaire", p_ols), ("régression fractionnelle", p_fr), ("deux étapes", p_2), ("vraie espérance (plafond)", p_vrai_l.values)]},
                  index=["erreur absolue", "RMSE", "R²"]).T.round(4)
print(tl.to_string())
```
<!--sortie-->
```text
                           erreur absolue    RMSE      R²
moyenne globale                    0.3063  0.3443 -0.0003
régression linéaire                0.2591  0.3047  0.2165
régression fractionnelle           0.2591  0.3048  0.2163
deux étapes                        0.2591  0.3048  0.2163
vraie espérance (plafond)          0.2577  0.3049  0.2158
```

```python hide
for k, v in tl.iterrows(): print("NUM lgd_mod", k, v["erreur absolue"], v["R²"])
```
<!--sortie-->
```text
NUM lgd_mod moyenne globale 0.3063 -0.0003
NUM lgd_mod régression linéaire 0.2591 0.2165
NUM lgd_mod régression fractionnelle 0.2591 0.2163
NUM lgd_mod deux étapes 0.2591 0.2163
NUM lgd_mod vraie espérance (plafond) 0.2577 0.2158
```

Les trois modèles font **exactement aussi bien** (erreur absolue 0,259, $R^2=0{,}216$) et dépassent nettement la moyenne globale (0,306 ; $R^2$ nul). Le plafond lui-même, la vraie espérance conditionnelle connue par construction, n'est pas plus haut : **ce que l'on prédit de la LGD d'un prêt individuel est très limité**. La garantie explique la **moyenne** d'un segment, mais, à l'intérieur d'un segment, les pertes restent dispersées entre 0 et 1. La précision d'une LGD se juge donc **par segment**, et l'erreur individuelle importe peu pour une provision de portefeuille (où seule la moyenne compte).

⚠️ Trois précautions. D'abord, le recouvrement est **tardif et censuré** : les défauts récents n'ont pas fini de se recouvrer, et leur LGD observée est trop basse (on les exclut, ou on projette). Ensuite, les LGD sont **plus fortes en période de crise** (garanties moins valorisées, recouvrements plus lents) : les approches réglementaires demandent une LGD « de ralentissement » (*downturn*), ce que notre fichier ne permet pas d'estimer. Enfin, la régression linéaire peut sortir de $[0,1]$ avec d'autres variables ; ici, avec trois variables catégorielles, elle s'en abstient et l'écart n'apparaît pas.

### 1.5.3 L'EAD : ce que l'on aura prêté au moment du défaut

Pour un prêt amortissable, l'exposition à une date est connue (un tableau d'amortissement). Pour une **ligne de crédit renouvelable** (découvert, carte), le client peut **tirer** davantage avant de faire défaut. On modélise l'exposition au défaut par

$$\text{EAD}=\text{tirage}+\text{CCF}\times(\text{limite}-\text{tirage}),$$

où le **facteur de conversion en crédit** (CCF, *credit conversion factor*) est la part du montant **non tiré** qui sera tirée avant le défaut. Dans `revolving_defauts.csv`, 8 000 lignes qui ont fait défaut, avec leur tirage un an avant :

```python hide-code
rv["utilisation"] = rv["tirage_12m_avant"] / rv["limite"]
ccf_q = rv.groupby(pd.qcut(rv["utilisation"], 5)).agg(utilisation_moy=("utilisation", "mean"), ccf_moyen=("ccf_observe", "mean")).round(3)
ccf_q.index = [f"quintile {i}" for i in range(1, 6)]
print(ccf_q.to_string())
ols_c = sm.OLS(rv["ccf_observe"], sm.add_constant(rv[["utilisation"]])).fit()
ead_naive = rv["tirage_12m_avant"].sum(); ead_vrai = rv["ead"].sum()
ead_ccf = (rv["tirage_12m_avant"] + rv["ccf_observe"].mean() * (rv["limite"] - rv["tirage_12m_avant"])).sum()
print(f"EAD réelle totale {ead_vrai / 1e6:.1f} M€ ; tirages un an avant {ead_naive / 1e6:.1f} M€ ; EAD par CCF moyen {ead_ccf / 1e6:.1f} M€")
```
<!--sortie-->
```text
            utilisation_moy  ccf_moyen
quintile 1            0.137      0.495
quintile 2            0.272      0.443
quintile 3            0.383      0.414
quintile 4            0.506      0.357
quintile 5            0.691      0.299
EAD réelle totale 23.8 M€ ; tirages un an avant 14.5 M€ ; EAD par CCF moyen 23.4 M€
```

```python hide
print("NUM ccf_moy", round(float(rv["ccf_observe"].mean()), 3)); print("NUM ccf_pente", round(float(ols_c.params["utilisation"]), 3)); print("NUM ccf_r2", round(float(ols_c.rsquared), 3))
print("NUM ead_vrai", round(ead_vrai / 1e6, 1)); print("NUM ead_naive", round(ead_naive / 1e6, 1)); print("NUM ead_ccf", round(ead_ccf / 1e6, 1))
print("NUM ccf_q1", float(ccf_q.iloc[0, 1])); print("NUM ccf_q5", float(ccf_q.iloc[4, 1]))
```
<!--sortie-->
```text
NUM ccf_moy 0.402
NUM ccf_pente -0.348
NUM ccf_r2 0.105
NUM ead_vrai 23.8
NUM ead_naive 14.5
NUM ead_ccf 23.4
NUM ccf_q1 0.495
NUM ccf_q5 0.299
```

Le CCF moyen est de 0,40 : en moyenne, **40 % de ce qui n'était pas tiré l'est avant le défaut**. Il est plus fort pour les lignes **peu utilisées** (0,50 dans le premier quintile d'utilisation, 0,30 dans le dernier) : un client en difficulté vide sa réserve. Retenir comme EAD le tirage d'un an avant donnerait 14,5 M€ pour 23,8 M€ réellement exposés : l'exposition serait **sous-estimée de 39 %**. Appliquer le CCF moyen donne 23,4 M€, à 2 % de la réalité ; une régression du CCF sur l'utilisation (pente −0,35, $R^2$ de 0,10) est un progrès modeste. Comme pour la LGD, la moyenne est bien estimée, le détail individuel beaucoup moins.

### 1.5.4 IFRS 9 : trois étapes

La norme **IFRS 9** (en vigueur depuis 2018, dans l'état de nos connaissances ; à vérifier) remplace le provisionnement sur pertes **subies** par un provisionnement sur pertes **attendues**. Le principe est un classement des prêts en **trois étapes** (*stages*) :

| Étape | Situation du prêt | Provision |
|---|---|---|
| **1** | risque de crédit **pas sensiblement accru** depuis l'octroi | perte attendue à **12 mois** |
| **2** | risque de crédit **sensiblement accru** depuis l'octroi, sans défaut | perte attendue **sur la durée de vie** |
| **3** | **défaut avéré** | perte attendue sur la durée de vie, sur un prêt en défaut (PD = 1) |

L'idée est **prospective** : on n'attend pas le défaut pour provisionner, on le fait dès que le risque se dégrade nettement. La norme laisse à chaque établissement la définition précise de la « hausse sensible » ; elle fournit seulement des présomptions (un retard de plus de 30 jours signale en général une hausse sensible, un retard de plus de 90 jours un défaut). Nos **règles d'exemple**, sur les 20 000 prêts de `portefeuille_ifrs9.csv`, sont :

- étape **3** : retard de 90 jours ou plus ;
- étape **2** : retard de 30 jours ou plus, **ou** PD actuelle supérieure à 2,5 fois la PD d'origine, **ou** prêt restructuré ;
- étape **1** : tous les autres.

```python hide-code
etapes = O.etape_ifrs9(pf)
pf["etape"] = etapes
pf["ecl"] = O.ecl_ifrs9(pf, etapes)
tg = pf.groupby("etape").agg(prets=("ead", "size"), ead_M=("ead", lambda s: s.sum() / 1e6), ecl_M=("ecl", lambda s: s.sum() / 1e6))
tg["couverture_%"] = 100 * tg["ecl_M"] / tg["ead_M"]
tg.loc["total"] = [tg["prets"].sum(), tg["ead_M"].sum(), tg["ecl_M"].sum(), 100 * tg["ecl_M"].sum() / tg["ead_M"].sum()]
print(tg.round(2).to_string())
```
<!--sortie-->
```text
         prets   ead_M  ecl_M  couverture_%
etape                                      
1      16607.0  251.65   2.92          1.16
2       2923.0   43.43   1.78          4.09
3        470.0    7.32   2.89         39.48
total  20000.0  302.41   7.59          2.51
```

```python hide
print("NUM etapes", [int(x) for x in tg.loc[[1, 2, 3], "prets"]]); print("NUM ecl_etapes", [round(float(x), 2) for x in tg.loc[[1, 2, 3], "ecl_M"]])
print("NUM ecl_tot", round(float(tg.loc["total", "ecl_M"]), 2)); print("NUM couv", [round(float(x), 2) for x in tg["couverture_%"]])
all1 = O.ecl_ifrs9(pf, np.ones(len(pf), int)).sum(); allv = O.ecl_ifrs9(pf, np.full(len(pf), 2)).sum()
print("NUM all1", round(all1 / 1e6, 2)); print("NUM allv", round(allv / 1e6, 2)); print("NUM pd_moy_pf", round(float(pf["pd_actuelle"].mean()), 4))
print("NUM ratio_vie_12m", round(allv / all1, 2))
```
<!--sortie-->
```text
NUM etapes [16607, 2923, 470]
NUM ecl_etapes [2.92, 1.78, 2.89]
NUM ecl_tot 7.59
NUM couv [1.16, 4.09, 39.48, 2.51]
NUM all1 4.14
NUM allv 6.66
NUM pd_moy_pf 0.0352
NUM ratio_vie_12m 1.61
```

Le portefeuille compte 16 607 prêts en étape 1, 2 923 en étape 2 et 470 en étape 3, pour une exposition de 302 M€ et une **perte attendue totale de 7,6 M€** (2,5 % de l'exposition). La **couverture** (perte attendue rapportée à l'exposition) croît fortement d'une étape à l'autre : 1,2 % pour l'étape 1, 4,1 % pour l'étape 2, 39 % pour l'étape 3. Le passage d'une étape à l'autre est un **effet de seuil** : si l'on provisionnait **tout le portefeuille sur 12 mois**, la perte attendue serait de 4,1 M€ ; **tout sur la durée de vie**, de 6,7 M€, soit 1,6 fois plus, pour une durée résiduelle moyenne de 3,7 ans. Un prêt qui bascule en étape 2 voit donc sa provision **augmenter d'un coup**, ce qui rend le résultat de la banque **sensible aux règles de basculement**, un point que les régulateurs et les auditeurs examinent de près.

La perte attendue d'un prêt en étape 2 est la **somme sur les années** de sa vie résiduelle : probabilité de défaut dans l'année $t$ ($(1-h)^{t-1}h$, avec $h$ la PD annuelle), perte en cas de défaut et exposition à cette date (qui diminue avec l'amortissement), **actualisés** au taux d'intérêt effectif du prêt. Le détail est dans le cahier (application 1.7).

### 1.5.5 Le regard vers l'avant : les scénarios

IFRS 9 demande que la perte attendue reflète des **informations prospectives**, donc la conjoncture attendue et non seulement celle d'hier. Les établissements calculent la perte sous **plusieurs scénarios macroéconomiques** et en font une **moyenne pondérée par leur probabilité**. Pour traduire un scénario en PD, on s'appuie sur la relation historique entre conjoncture et défauts, celle de `taux_defaut_macro.csv` : une régression du logit du taux de défaut trimestriel sur la croissance, le chômage et la variation de l'immobilier.

```python hide-code
mac = pd.read_csv("donnees/taux_defaut_macro.csv")
mac["logit"] = np.log(mac["taux_defaut"] / (1 - mac["taux_defaut"]))
mod = sm.OLS(mac["logit"], sm.add_constant(mac[["croissance_pib", "chomage", "variation_immo"]])).fit()
print(mod.params.round(3).to_string()); print(f"R² = {mod.rsquared:.3f}")
sc = {"central": (1.4, 8.2, 0.6), "défavorable": (-1.0, 9.5, -2.5), "favorable": (2.4, 7.4, 2.5)}
poids = {"central": 0.5, "défavorable": 0.3, "favorable": 0.2}
def taux(v): return float(1 / (1 + np.exp(-(mod.params["const"] + mod.params["croissance_pib"] * v[0] + mod.params["chomage"] * v[1] + mod.params["variation_immo"] * v[2]))))
tx = {k: taux(v) for k, v in sc.items()}
ecl_sc = {k: O.ecl_ifrs9(pf, etapes, mult=tx[k] / tx["central"]).sum() / 1e6 for k in sc}
tsc = pd.DataFrame({"croissance": [v[0] for v in sc.values()], "chômage": [v[1] for v in sc.values()], "immobilier": [v[2] for v in sc.values()],
                    "défaut modélisé (%)": [100 * tx[k] for k in sc], "poids": [poids[k] for k in sc], "ECL (M€)": [ecl_sc[k] for k in sc]}, index=list(sc)).round(2)
print(tsc.to_string())
```
<!--sortie-->
```text
const            -5.030
croissance_pib   -0.401
chomage           0.245
variation_immo   -0.063
R² = 0.989
             croissance  chômage  immobilier  défaut modélisé (%)  poids  ECL (M€)
central             1.4      8.2         0.6                 2.61    0.5      7.59
défavorable        -1.0      9.5        -2.5                10.51    0.3     19.89
favorable           2.4      7.4         2.5                 1.29    0.2      5.27
```

```python hide
ecl_pond = sum(poids[k] * ecl_sc[k] for k in sc)
v_moy = sum(poids[k] * np.array(sc[k]) for k in sc); ecl_moy = O.ecl_ifrs9(pf, etapes, mult=taux(v_moy) / tx["central"]).sum() / 1e6
print("NUM mac_r2", round(float(mod.rsquared), 3)); print("NUM mac_coef", [round(float(mod.params[k]), 3) for k in mod.params.index])
print("NUM tx_sc", {k: round(100 * v, 2) for k, v in tx.items()}); print("NUM ecl_sc", {k: round(v, 2) for k, v in ecl_sc.items()})
print("NUM ecl_pond", round(ecl_pond, 2)); print("NUM ecl_macro_moy", round(ecl_moy, 2)); print("NUM prime_convexite", round(ecl_pond - ecl_moy, 2))
print("NUM ecl_x", {m_: round(O.ecl_ifrs9(pf, etapes, mult=m_).sum() / 1e6, 2) for m_ in (0.5, 1.0, 1.5, 2.0, 3.0)})
```
<!--sortie-->
```text
NUM mac_r2 0.989
NUM mac_coef [-5.03, -0.401, 0.245, -0.063]
NUM tx_sc {'central': 2.61, 'défavorable': 10.51, 'favorable': 1.29}
NUM ecl_sc {'central': np.float64(7.59), 'défavorable': np.float64(19.89), 'favorable': np.float64(5.27)}
NUM ecl_pond 10.82
NUM ecl_macro_moy 9.09
NUM prime_convexite 1.73
NUM ecl_x {0.5: np.float64(5.29), 1.0: np.float64(7.59), 1.5: np.float64(9.8), 2.0: np.float64(11.91), 3.0: np.float64(15.97)}
```

La régression explique l'essentiel des variations du logit du taux de défaut ($R^2=0{,}99$ sur l'historique) : un point de croissance en moins multiplie la cote de défaut par 1,5 (+49 %), un point de chômage en plus de 28 %. Le scénario **central** (la conjoncture moyenne de l'historique) donne 2,6 % de défaut ; le **défavorable** (récession modérée, chômage à 9,5 %, immobilier en baisse), 10,5 % ; le **favorable**, 1,3 %. Nous multiplions la PD de chaque prêt par le rapport entre le taux du scénario et celui du central (les étapes restent fixes pour simplifier : dans la réalité, un scénario défavorable fait aussi **basculer** des prêts en étape 2).

La perte attendue vaut 7,6 M€ dans le scénario central, 19,9 M€ dans le défavorable (multipliée par 2,6) et 5,3 M€ dans le favorable. Pondérées à 50 / 30 / 20 %, elles donnent une **perte attendue pondérée de 10,8 M€**, soit environ **43 % de plus que le central**. Un point mérite d'être compris : la perte au **scénario moyen** (la conjoncture pondérée : croissance 0,9 %, chômage 8,4 %) serait de 9,1 M€, **moins** que la perte pondérée des trois scénarios : la perte est une fonction **convexe** de la conjoncture (un mauvais scénario coûte plus que ce que gagne un bon), si bien que moyenner la conjoncture **sous-estime** la perte moyenne de 1,7 M€. C'est la raison pour laquelle la norme demande plusieurs scénarios et non un scénario « moyen ».

Enfin, la **sensibilité** de la provision à la PD est quasi linéaire pour les étapes 1 et 2 : une PD multipliée par 2 donne 11,9 M€ (1,6 fois la perte centrale, pas 2 fois, parce que l'étape 3, 2,9 M€, est insensible à la PD) et multipliée par 3, 16,0 M€.

⚠️ **Limites.** Les scénarios et leurs pondérations sont des **jugements**, que les auditeurs examinent ; la relation macro-défaut est estimée sur 80 trimestres d'**un seul portefeuille** ; les PD de `portefeuille_ifrs9.csv` sont supposées déjà « à la date » ; la LGD de ce fichier n'est pas ralentie.

> ✅ **À retenir.**
> - $\text{ECL}=\text{PD}\times\text{LGD}\times\text{EAD}$ : trois grandeurs modélisées séparément. La perte attendue est un **coût prévisible**, pas un risque.
> - **PD** : à 12 mois ou sur la vie ($1-(1-h)^T$ si le risque est constant). **LGD** : en U, très liée à la garantie, **peu prévisible individuellement** (les trois modèles testés ont le même $R^2$ de 0,22, plafond compris) mais bien estimée par segment. **EAD** : le CCF capte la part tirée avant le défaut (0,40 en moyenne) ; ignorer le tirage futur sous-estime l'exposition de 39 %.
> - **IFRS 9** : étape 1 (12 mois), étape 2 (durée de vie, après hausse sensible du risque), étape 3 (défaut). Le passage de 1 à 2 multiplie la provision (de 1,6 en moyenne ici).
> - Les **scénarios** pondérés remplacent un scénario moyen : la perte est **convexe** en la conjoncture, moyenner la conjoncture sous-estime la perte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.6 et 1.7, exercices 1.11 et 1.12.
