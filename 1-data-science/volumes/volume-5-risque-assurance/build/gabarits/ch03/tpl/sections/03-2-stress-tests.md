## 3.2 Stress tests et scénarios

La section précédente mesurait le risque **à partir de la distribution observée** des pertes. Un stress test pose une autre question : *que se passe-t-il si… ?* Si le chômage monte de deux points, si les taux gagnent deux points, si les marchés se comportent comme pendant le pire épisode connu. Un stress test ne donne **aucune probabilité** : il décrit une situation plausible mais sévère et en chiffre les conséquences. La VaR répond « quelle est la perte d'un mauvais jour ordinaire ? », le stress test répond « quelle serait la perte d'un jour qui ne l'est pas ? ».

### 3.2.1 Pourquoi stresser, quand on a une VaR ?

Trois raisons, toutes déjà entrevues. Premièrement, la VaR historique **ne connaît que ce qui s'est produit** : un événement absent de la fenêtre n'existe pas pour elle. Deuxièmement, la VaR est un chiffre de quantile : elle ne mesure rien au-delà, alors que la survie d'un établissement se joue justement au-delà. Troisièmement, les relations estimées en période calme (volatilités, corrélations) **changent** en période de crise, comme le montre le graphique de volatilité de la section précédente. Les superviseurs et les directions des risques demandent donc les deux : une mesure statistique pour le suivi courant, des scénarios pour la résistance aux chocs.

Un bon scénario obéit à quatre critères : il est **plausible** (on peut raconter comment il arriverait), **sévère** (il fait mal), **cohérent** (ses variables bougent ensemble de façon réaliste : un krach actions sans effet sur le crédit est suspect), et **pertinent** pour le portefeuille testé (un choc sur une matière première que l'on ne détient pas ne dit rien).

### 3.2.2 Les sensibilités : un choc, un facteur

La forme la plus simple de stress est l'**analyse de sensibilité** : on fait varier **un seul** facteur de risque et l'on mesure la perte. Pour notre portefeuille de 100 M€, la perte pour une baisse de 10 % de chaque actif pris isolément est proportionnelle à son poids : 3,5 M€ pour les actions A, 1,5 M€ pour les actions B, 3 M€ pour les obligations, 1 M€ pour l'immobilier et 1 M€ pour les matières premières. Le résultat se lit en une seconde, ce qui fait son intérêt, mais il est **incohérent** : dans la réalité, les actifs ne bougent pas un par un.

Un scénario *hypothétique* construit à la main fait bouger tous les facteurs ensemble. Prenons un « krach actions » : actions A −30 %, actions B −35 %, immobilier coté −20 %, matières premières −25 %, et des obligations qui **montent** de 3 % (fuite vers la qualité). La perte est la somme pondérée des chocs :

| Actif | Montant | Choc | Perte (M€) |
|---|---|---|---|
| Actions A | 35 M€ | −30 % | 10,50 |
| Actions B | 15 M€ | −35 % | 5,25 |
| Obligations | 30 M€ | +3 % | −0,90 |
| Immobilier coté | 10 M€ | −20 % | 2,00 |
| Matières premières | 10 M€ | −25 % | 2,50 |
| **Total** | **100 M€** | | **{{krach_total}}** |

La perte totale est de {{krach_total}} M€, soit {{krach_pct}} % du portefeuille : environ {{krach_vs_var}} fois la VaR historique à 99 % d'un jour ({{var_h99}} M€). Ce rapport n'a rien d'alarmant ou de rassurant en soi : il rappelle que la VaR et le scénario ne mesurent pas la même chose, l'une un jour ordinaire sévère, l'autre une crise.

```python hide
montants = np.array([35, 15, 30, 10, 10])
chocs = np.array([-0.30, -0.35, 0.03, -0.20, -0.25])
pertes_scen = -montants * chocs
O.num("krach_total", pertes_scen.sum(), ".2f")
O.num("krach_pct", pertes_scen.sum(), ".1f")
O.num("krach_vs_var", pertes_scen.sum() / O.var_hist(L, 0.99), ".0f")
```
<!--sortie-->

### 3.2.3 Les scénarios historiques

Un **scénario historique** rejoue un épisode réel sur le portefeuille actuel. Il a l'immense avantage de la cohérence (les chocs se sont réellement produits ensemble) et de la crédibilité (« cela est arrivé »). Dans nos données, l'épisode le pire est la fenêtre de **dix jours consécutifs** dont la perte cumulée est la plus forte : {{worst10}} M€, atteinte en fenêtre terminée le {{date_worst10}}. À titre de comparaison, la VaR à 99 % sur dix jours obtenue par la règle de la racine (section 3.1.6) est de {{var10_racine}} M€ : le pire épisode observé coûte **{{ratio_worst10}} fois** plus. Rien d'anormal : cet épisode se situe en régime de stress, que la VaR calibrée sur toute l'histoire dilue.

```python hide
S10 = pd.Series(L, index=r.index).rolling(10).sum()
O.num("worst10", S10.max(), ".1f")
O.num("date_worst10", S10.idxmax().strftime("%d/%m/%Y"), "s")
O.num("ratio_worst10", S10.max() / (np.sqrt(10) * O.var_hist(L, 0.99)), ".1f")
```
<!--sortie-->

Un scénario historique a deux limites. Il suppose que le **portefeuille d'aujourd'hui** réagit comme celui d'hier (alors que sa composition a changé), et il est **prisonnier du passé** : la prochaine crise ne ressemblera pas à la précédente. D'où la complémentarité avec les scénarios hypothétiques, qui explorent des situations jamais observées.

### 3.2.4 Des variables macroéconomiques aux défauts de crédit

Pour la banque, le stress test le plus important relie l'**économie** aux **défauts** de son portefeuille de crédits. La démarche standard comporte trois étapes : estimer un modèle statistique entre les variables macroéconomiques et le taux de défaut, construire des trajectoires macroéconomiques (de base, adverse, sévère), puis en déduire des pertes.

Nos données donnent 80 trimestres de croissance du PIB, de chômage, de variation des prix de l'immobilier et de taux de défaut annualisé du portefeuille, avec une récession entre les trimestres 48 et 54. Un taux de défaut est une proportion, comprise entre 0 et 1 : on modélise donc sa **transformation logit**, $\ln\dfrac{p}{1-p}$, par une régression linéaire des trois variables (comme pour la régression logistique, volume II, section 2.2). Un appel suffit.

```python
import statsmodels.api as sm
t = pd.read_csv("donnees/taux_defaut_macro.csv")
y = np.log(t["taux_defaut"] / (1 - t["taux_defaut"]))
X = sm.add_constant(t[["croissance_pib", "chomage", "variation_immo"]])
macro = sm.OLS(y, X).fit()
print(macro.params.round(3).to_dict(), round(macro.rsquared, 3))
```
<!--sortie-->

```python hide
O.num("b_pib", macro.params["croissance_pib"], ".3f")
O.num("b_chom", macro.params["chomage"], ".3f")
O.num("b_immo", macro.params["variation_immo"], ".3f")
O.num("r2_macro", macro.rsquared, ".3f")
O.num("odds_chom", np.exp(macro.params["chomage"]), ".2f")
O.num("odds_pib", np.exp(macro.params["croissance_pib"]), ".2f")
```
<!--sortie-->

Chaque point de croissance en plus **multiplie** les chances de défaut par {{odds_pib}} (donc les réduit), chaque point de chômage en plus les multiplie par {{odds_chom}}, et le modèle explique {{r2_macro}} de la variance du logit. L'ajustement est spectaculaire, trop pour être honnête : il tient à ce que les données sont simulées avec une relation de ce type. Il faut donc lui faire passer l'épreuve que la réalité imposerait : **a-t-il prévu la crise avant de la voir ?** Réestimons le modèle sur les seuls 44 premiers trimestres (calmes) et comparons sa prédiction au taux réellement observé pendant la récession.

![Taux de défaut observé (courbe pleine) et prédit par le modèle estimé sur les 44 premiers trimestres seulement (tirets). La zone grisée est la récession.](figures/ch03-modele-macro.png)

```python hide
tr = t["trimestre"] <= 44
m_tr = sm.OLS(y[tr], X[tr]).fit()
pred = 1 / (1 + np.exp(-m_tr.predict(X)))
rec_ = (t["trimestre"] >= 48) & (t["trimestre"] <= 55)
O.num("peak_reel", 100 * t.loc[rec_, "taux_defaut"].max(), ".1f")
O.num("peak_pred", 100 * pred[rec_].max(), ".1f")
O.num("rmse_oot", 100 * np.sqrt(((pred[~tr] - t.loc[~tr, "taux_defaut"]) ** 2).mean()), ".2f")
fig, ax = plt.subplots(figsize=(8.4, 3.4))
ax.axvspan(48, 55, color=MUET, alpha=0.2, lw=0)
ax.plot(t["trimestre"], 100 * t["taux_defaut"], color=BLEU, label="observé")
ax.plot(t["trimestre"], 100 * pred, color=ORANGE, ls="--", label="prédit (estimé sur les trimestres 1 à 44)")
ax.axvline(44, color=ENCRE2, lw=0.8)
ax.text(44.5, 12.2, "fin de l'estimation", fontsize=8.5, color=ENCRE2)
ax.set_xlabel("trimestre")
ax.set_ylabel("taux de défaut (%)")
ax.legend(loc="upper left")
style.save(fig, "ch03-modele-macro.png")
```
<!--sortie-->

Le modèle appris **avant** la crise en annonce un sommet de {{peak_pred}} % contre {{peak_reel}} % observé, avec une erreur quadratique moyenne de {{rmse_oot}} point sur les 36 trimestres suivants. C'est un très bon résultat, et il faut l'interpréter avec méfiance : dans nos données la relation macro-défaut est **stable** par construction. Dans la réalité, trois obstacles se dressent : l'échantillon est court (quelques dizaines de trimestres, une ou deux récessions), les variables macroéconomiques sont corrélées entre elles (les coefficients individuels sont instables), et surtout la relation **change** quand le comportement des emprunteurs ou la politique d'octroi change. Un modèle qui a bien « prédit » une crise passée n'a pas démontré qu'il prédira la suivante.

> ⚠️ **Piège.** Un excellent $R^2$ sur 80 points et trois variables explicatives d'allure économique n'est pas une preuve de causalité ni de stabilité. Les modèles de stress test sont fréquemment estimés sur très peu de crises : on teste leur **robustesse** (changer la période, retirer une variable) plus qu'on ne célèbre leur ajustement.

### 3.2.5 Du scénario aux pertes de crédit

Reste à définir les scénarios et à traduire les taux de défaut en pertes. Nous prenons un portefeuille de crédits de **500 M€** d'encours (EAD) et une perte en cas de défaut (LGD) égale à la moyenne des pertes observées sur nos défauts passés, soit {{lgd_moy}} % (fichier `recouvrements.csv`, chapitre 1). La perte annuelle attendue est le taux de défaut moyen de l'année multiplié par l'encours et par la LGD. Trois trajectoires de quatre trimestres sont comparées : le **scénario de base** prolonge la moyenne des quatre derniers trimestres (croissance de {{sc_base_pib}} %, chômage de {{sc_base_cho}} %) ; le **scénario adverse** reproduit une récession comparable à la pire observée (croissance de −1,5 %, chômage montant à 9,5 %, immobilier −3 % par trimestre) ; le **scénario sévère** va au-delà de tout ce que nos 80 trimestres ont connu (croissance de −3 %, chômage à 11 %, immobilier −6 %).

| Scénario | Croissance | Chômage (fin) | Immobilier | Taux de défaut moyen | Perte annuelle | En % de l'encours |
|---|---|---|---|---|---|---|
| Base | {{sc_base_pib}} % | {{sc_base_cho}} % | {{sc_base_immo}} % | {{sc_base_taux}} % | {{sc_base_perte}} M€ | {{sc_base_pct}} % |
| Adverse | −1,5 % | 9,5 % | −3,0 % | {{sc_adv_taux}} % | {{sc_adv_perte}} M€ | {{sc_adv_pct}} % |
| Sévère | −3,0 % | 11,0 % | −6,0 % | {{sc_sev_taux}} % | {{sc_sev_perte}} M€ | {{sc_sev_pct}} % |

```python hide
rec = pd.read_csv("donnees/recouvrements.csv")
lgd = rec["lgd_realisee"].mean()
EAD = 500.0
O.num("lgd_moy", 100 * lgd, ".1f")
base = t.iloc[-4:][["croissance_pib", "chomage", "variation_immo"]].mean().values

def trajectoire(pib, cho_fin, immo):
    cho = np.linspace(base[1], cho_fin, 5)[1:]
    Xs = np.column_stack([np.ones(4), np.full(4, pib), cho, np.full(4, immo)])
    return 1 / (1 + np.exp(-(Xs @ macro.params.values)))

scen = {"base": (base[0], base[1], base[2]), "adv": (-1.5, 9.5, -3.0), "sev": (-3.0, 11.0, -6.0)}
for k, (a, b, c) in scen.items():
    p = trajectoire(a, b, c)
    O.num(f"sc_{k}_taux", 100 * p.mean(), ".1f")
    O.num(f"sc_{k}_perte", p.mean() * EAD * lgd, ".1f")
    O.num(f"sc_{k}_pct", 100 * p.mean() * lgd, ".1f")
O.num("sc_base_pib", base[0], ".1f")
O.num("sc_base_cho", base[1], ".1f")
O.num("sc_base_immo", base[2], ".1f")
O.num("max_hist", 100 * t["taux_defaut"].max(), ".1f")
O.num("ratio_adv_base", trajectoire(*scen["adv"]).mean() / trajectoire(*scen["base"]).mean(), ".1f")
```
<!--sortie-->

La perte annuelle passe de {{sc_base_perte}} M€ en base à {{sc_adv_perte}} M€ en scénario adverse (un facteur {{ratio_adv_base}}) puis à {{sc_sev_perte}} M€ en sévère. Deux remarques s'imposent. D'abord, la **non-linéarité** : une récession de l'ampleur de la pire observée multiplie la perte par {{ratio_adv_base}}, parce que le logit transforme une somme de petits effets en une explosion du taux. Ensuite, le scénario sévère aboutit à un taux de défaut de {{sc_sev_taux}} %, plus du double du maximum jamais observé dans l'échantillon ({{max_hist}} %) : le modèle **extrapole** loin de ses données, et son résultat n'a plus la même fiabilité que celui du scénario adverse. Un chiffre de stress est d'autant moins sûr qu'il est extrême, ce que les superviseurs savent et c'est pourquoi les résultats sont toujours présentés avec leurs hypothèses.

Enfin, la perte de crédit n'est qu'une partie du tableau. Un vrai stress test fait aussi varier les **marges d'intérêt**, les **valeurs de garantie** (donc la LGD, qui augmente quand l'immobilier baisse), les **provisions** et le **coût du risque**, puis consolide le tout dans une évolution du **ratio de fonds propres** (chapitre 4). Retenons le principe : on enchaîne *scénario macro → variables de risque → pertes → capital*.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.5, exercice 3.6.

### 3.2.6 Le choc de taux d'intérêt

Une banque et surtout une mutuelle d'assurance détiennent beaucoup d'obligations : leur valeur dépend de la courbe des taux. Une obligation de coupon $c$, de nominal 100 et de maturité $T$ a pour prix $P=\sum_{t=1}^{T}\dfrac{\text{flux}_t}{(1+y_t)^t}$, où $y_t$ est le taux d'actualisation de l'échéance $t$ lu sur la courbe. Quand les taux montent, le prix baisse, d'autant plus que la maturité est longue.

> 📐 **Duration et convexité.** Par un développement de Taylor du prix en fonction d'un déplacement parallèle $\Delta y$ de la courbe, $\dfrac{\Delta P}{P}\approx-D\,\Delta y+\dfrac12\,C\,(\Delta y)^2$, où $D=-\dfrac{1}{P}\dfrac{dP}{dy}$ est la **duration modifiée** et $C=\dfrac1P\dfrac{d^2P}{dy^2}$ la **convexité**. La duration est la sensibilité de premier ordre ; la convexité corrige la courbure (le prix baisse moins que ne le prévoit la droite quand les taux montent, et monte plus quand ils baissent).

Prenons trois obligations (2 ans à 2 %, 5 ans à 3 %, 10 ans à 3,5 %) actualisées sur la courbe du dernier mois de nos données, et chiffrons l'effet d'un choc parallèle de +100, +200 et +300 points de base (pb) sur l'obligation à 10 ans, dont la duration est de {{dur10}} et la convexité de {{conv10}}.

| Choc | Prix exact | Duration seule | Duration + convexité |
|---|---|---|---|
| +100 pb | {{ex10_1}} % | {{d10_1}} % | {{dc10_1}} % |
| +200 pb | {{ex10_2}} % | {{d10_2}} % | {{dc10_2}} % |
| +300 pb | {{ex10_3}} % | {{d10_3}} % | {{dc10_3}} % |

La duration seule surestime la baisse (elle ne voit pas que la courbe du prix se redresse) et l'erreur grossit avec le choc ; l'ajout de la convexité ramène l'écart à {{gap_dc}} point sur +300 pb. Pour un choc de faible amplitude, l'approximation est excellente ; pour un stress, on **réévalue intégralement** le portefeuille (c'est ce que fait la colonne « prix exact »).

![Variation du prix de l'obligation à 10 ans selon le choc parallèle de taux : réévaluation exacte (trait plein), approximation par la duration (tirets) et par duration et convexité (pointillés).](figures/ch03-taux-duration.png)

```python hide
cb = pd.read_csv("donnees/courbe_taux.csv")
f120 = O.courbe_a(120, cb)
bonds = [(2, 0.02), (5, 0.03), (10, 0.035)]
P0 = [O.prix_obligation(cp, mt, f120) for mt, cp in bonds]

def duration_convexite(cp, mt):
    h = 1e-4
    p0 = O.prix_obligation(cp, mt, f120)
    pu = O.prix_obligation(cp, mt, f120, choc=lambda tt: h)
    pdn = O.prix_obligation(cp, mt, f120, choc=lambda tt: -h)
    return -(pu - pdn) / (2 * h * p0), (pu + pdn - 2 * p0) / (h * h * p0)

D10, C10 = duration_convexite(0.035, 10)
O.num("dur10", D10, ".1f")
O.num("conv10", C10, ".0f")
O.num("gap_dc", 100 * abs(-D10 * 0.03 + 0.5 * C10 * 0.03 ** 2 - (O.prix_obligation(0.035, 10, f120, choc=lambda tt: 0.03) / P0[2] - 1)), ".1f")
chocs_bp = [0.01, 0.02, 0.03]
ex = [O.prix_obligation(0.035, 10, f120, choc=lambda tt, d=d: d) / P0[2] - 1 for d in chocs_bp]
for i, d in enumerate(chocs_bp, 1):
    O.num(f"ex10_{i}", 100 * ex[i - 1], ".1f")
    O.num(f"d10_{i}", -100 * D10 * d, ".1f")
    O.num(f"dc10_{i}", 100 * (-D10 * d + 0.5 * C10 * d * d), ".1f")
grille = np.linspace(-0.01, 0.04, 41)
exact = [O.prix_obligation(0.035, 10, f120, choc=lambda tt, d=d: d) / P0[2] - 1 for d in grille]
fig, ax = plt.subplots(figsize=(7.6, 3.6))
ax.plot(100 * grille, 100 * np.array(exact), color=BLEU, label="réévaluation exacte")
ax.plot(100 * grille, 100 * (-D10 * grille), color=ORANGE, ls="--", label="duration seule")
ax.plot(100 * grille, 100 * (-D10 * grille + 0.5 * C10 * grille ** 2), color=AQUA, ls=":", lw=2.4, label="duration et convexité")
ax.set_xlabel("choc parallèle de taux (points de pourcentage)")
ax.set_ylabel("variation du prix (%)")
ax.legend()
style.save(fig, "ch03-taux-duration.png")
```
<!--sortie-->

Un choc parallèle est trop simple : les courbes réelles **se déforment** (pentification, aplatissement). Un scénario *historique de taux* applique à la courbe actuelle la déformation observée entre deux dates. Entre les mois 60 et 90 de nos données (le cycle de hausse), les taux ont monté de {{hist_1}} pb à 3 mois, de {{hist_2}} pb à 1 an et jusqu'à {{hist_30}} pb à 30 ans. Appliquée à trois obligations de 10 M€ chacune, cette déformation coûte {{bond_loss_hist}} M€ (soit {{bond_pct_hist}} % du portefeuille obligataire), contre {{bond_loss_par}} M€ pour un choc parallèle de +100 pb : la forme du choc compte autant que son ampleur.

```python hide
chg = cb[cb["mois"] == 90].iloc[0, 1:].values.astype(float) - cb[cb["mois"] == 60].iloc[0, 1:].values.astype(float)
fh = lambda tt: np.interp(tt, O.MATS, chg)
pertes_h = [10 * (1 - O.prix_obligation(cp, mt, f120, choc=fh) / p0) for (mt, cp), p0 in zip(bonds, P0)]
pertes_p = [10 * (1 - O.prix_obligation(cp, mt, f120, choc=lambda tt: 0.01) / p0) for (mt, cp), p0 in zip(bonds, P0)]
O.num("hist_1", 1e4 * chg[0], ".0f")
O.num("hist_2", 1e4 * chg[1], ".0f")
O.num("hist_30", 1e4 * chg[-1], ".0f")
O.num("bond_loss_hist", sum(pertes_h), ".2f")
O.num("bond_pct_hist", 100 * sum(pertes_h) / 30, ".1f")
O.num("bond_loss_par", sum(pertes_p), ".2f")
```
<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.6, exercice 3.7.

### 3.2.7 Le stress test inversé

Un stress test classique part d'un scénario et calcule la perte. Le **stress test inversé** (*reverse stress test*) fait le chemin contraire : il part d'un **résultat inacceptable** (le capital est épuisé, le ratio passe sous le seuil) et cherche *quel scénario y conduit*, puis demande s'il est plausible. L'exercice est salutaire parce qu'il oblige à regarder les vulnérabilités que les scénarios « raisonnables » n'effleurent pas.

Supposons que les fonds propres disponibles pour absorber les pertes de crédit s'élèvent à **25 M€** (5 % de l'encours). Paramétrons une famille de scénarios qui va continûment du scénario de base ($s=0$) au scénario sévère ($s=1$), et cherchons l'intensité $s$ pour laquelle la perte annuelle atteint 25 M€. On trouve $s=$ {{rv_s}} % de la distance entre base et sévère, ce qui correspond à une croissance de {{rv_pib}} % et à un chômage de {{rv_cho}} % en fin d'année. Ce scénario est **moins sévère que la récession déjà observée** dans l'échantillon (croissance minimale de {{hist_pib_min}} %, chômage maximal de {{hist_cho_max}} %) : le coussin de 25 M€ ne résisterait pas à une récession plus douce que celle que le portefeuille a déjà connue. C'est une conclusion que ni la VaR ni un scénario « raisonnable » n'auraient fait apparaître.

```python hide
from scipy import optimize
sev = scen["sev"]

def perte_s(s):
    a = base[0] + s * (sev[0] - base[0]); b = base[1] + s * (sev[1] - base[1]); c = base[2] + s * (sev[2] - base[2])
    return trajectoire(a, b, c).mean() * EAD * lgd

s_star = optimize.brentq(lambda s: perte_s(s) - 25.0, 0.0, 1.5)
O.num("rv_s", 100 * s_star, ".0f")
O.num("rv_pib", base[0] + s_star * (sev[0] - base[0]), ".1f")
O.num("rv_cho", base[1] + s_star * (sev[1] - base[1]), ".1f")
O.num("hist_pib_min", t["croissance_pib"].min(), ".1f")
O.num("hist_cho_max", t["chomage"].max(), ".1f")
```
<!--sortie-->

Le raisonnement inversé est précieux justement parce qu'il évite le piège du scénario « confortable » : il ne dit pas si la banque est solide, il dit **ce qu'il faudrait pour qu'elle ne le soit plus**, et laisse la direction juger si c'est crédible.

### 3.2.8 Quand les corrélations montent

Dernier point, essentiel : la diversification **disparaît quand on en a le plus besoin**. Le graphique compare les corrélations estimées sur les jours calmes et sur les jours de stress de nos données.

![Corrélations des rendements journaliers entre actifs, estimées sur les jours calmes (à gauche) et sur les jours de stress (à droite). Les actions, l'immobilier et les matières premières se resserrent ; les obligations restent presque indépendantes.](figures/ch03-correlations-regimes.png)

```python hide
rc = r[O.ACTIFS][rg == "calme"]
rs = r[O.ACTIFS][rg == "stress"]
cc, cs = rc.corr().values, rs.corr().values
fig, axes = plt.subplots(1, 2, figsize=(8.6, 3.8))
noms = ["act. A", "act. B", "oblig.", "immo.", "mat."]
for ax, c, titre in zip(axes, (cc, cs), ("jours calmes", "jours de stress")):
    im = ax.imshow(c, cmap=style.DIV, vmin=-1, vmax=1)
    ax.set_xticks(range(5), noms, rotation=45, ha="right", fontsize=8.5)
    ax.set_yticks(range(5), noms, fontsize=8.5)
    ax.set_title(titre)
    ax.grid(False)
    for i in range(5):
        for j in range(5):
            ax.text(j, i, f"{c[i, j]:.2f}".replace(".", ","), ha="center", va="center", fontsize=7.5, color=ENCRE2)
fig.colorbar(im, ax=axes, shrink=0.8)
style.save(fig, "ch03-correlations-regimes.png")
O.num("corr_AB_c", cc[0, 1], ".2f")
O.num("corr_AB_s", cs[0, 1], ".2f")
O.num("corr_Aimm_c", cc[0, 3], ".2f")
O.num("corr_Aimm_s", cs[0, 3], ".2f")
O.num("corr_Aob_c", cc[0, 2], ".2f")
O.num("corr_Aob_s", cs[0, 2], ".2f")
def ratio_div(sub):
    sdv = sub.std().values * O.POIDS
    return O.pertes_portefeuille(sub).std() / (sdv * O.VALEUR).sum()
O.num("div_c", ratio_div(rc), ".2f")
O.num("div_s", ratio_div(rs), ".2f")
O.num("var_normal_c", O.var_normale(0, O.pertes_portefeuille(rc).std(), 0.99), ".2f")
O.num("var_normal_s", O.var_normale(0, O.pertes_portefeuille(rs).std(), 0.99), ".2f")
```
<!--sortie-->

La corrélation entre les actions A et les actions B passe de {{corr_AB_c}} à {{corr_AB_s}}, celle entre les actions A et l'immobilier de {{corr_Aimm_c}} à {{corr_Aimm_s}}, alors que celle avec les obligations reste proche de zéro ({{corr_Aob_c}} puis {{corr_Aob_s}}). Mesurons l'effet de diversification par le rapport entre l'écart-type du portefeuille et la somme des écarts-types pondérés des actifs (1 = aucune diversification, 0 = diversification totale) : il vaut {{div_c}} en jours calmes, mais {{div_s}} en jours de stress. **La diversification a perdu une part importante de son effet au moment où elle devait servir.** La VaR normale à 99 % vaut {{var_normal_c}} M€ avec les caractéristiques des jours calmes, {{var_normal_s}} M€ avec celles des jours de stress : le seul changement de régime multiplie le risque par {{ratio_regime}}.

```python hide
O.num("ratio_regime", O.var_normale(0, O.pertes_portefeuille(rs).std(), 0.99) / O.var_normale(0, O.pertes_portefeuille(rc).std(), 0.99), ".1f")
```
<!--sortie-->

C'est la raison pour laquelle les scénarios de stress **n'utilisent pas les corrélations moyennes** : ils appliquent des corrélations de crise (souvent proches de 1 pour les actifs risqués), ou, comme dans notre scénario « krach » de 3.2.2, des chocs simultanés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.8 (pour le stress inversé).

### 3.2.9 Gouvernance et limites des stress tests

Un stress test n'est utile que si l'on en tire une décision. Trois précautions résument la pratique. **Gouvernance** : les scénarios sont proposés par la fonction de gestion des risques, **discutés** par la direction, **révisés** régulièrement, et les résultats sont reliés à des **actions** (réduire une exposition, relever le capital, préparer un plan de financement). **Limites** : un scénario est une histoire parmi d'autres ; il y a un risque de se concentrer sur la crise passée (le « dernier conflit »), d'ignorer les effets de second tour (une vente forcée fait baisser les prix, qui déclenche d'autres ventes), et de croire à la précision des chiffres (voir le modèle macro, qui extrapole). **Complémentarité** : le stress test ne remplace pas la VaR, il la complète. La VaR dit comment le risque courant se répartit, le stress dit où l'on casse.

> ✅ **À retenir.**
> - Un stress test répond à « et si ? » ; il ne donne **aucune probabilité**, mais une perte conditionnelle à un scénario plausible et sévère.
> - On distingue sensibilités (un facteur), scénarios historiques (cohérents, mais prisonniers du passé) et scénarios hypothétiques (construits, plus libres).
> - Un scénario macroéconomique relie l'économie aux défauts par un modèle statistique : *macro → taux de défaut → perte → capital*. Les relations extrapolées au-delà des données sont moins fiables.
> - Un choc de taux se chiffre par duration et convexité pour les petits chocs, par réévaluation complète pour les grands ; la **forme** du choc compte.
> - Le stress test **inversé** part d'un résultat inacceptable et cherche le scénario qui y mène.
> - Les corrélations montent en crise : la diversification mesurée en période calme est un mirage au moment où l'on en a besoin.
