## 5.3 ➕ Pour aller plus loin : saisonnalité et prévision pour la planification

> 🧭 **Section complémentaire.** Elle prolonge 5.1 et 5.2 vers l'usage que fait la gérante d'une prévision : planifier. On y présente la régression avec variables indicatrices (qui sait tenir compte des promotions et des calendriers), le modèle ARIMA saisonnier (en une page), la prévision par canal, l'effet de l'horizon, les scénarios et la traduction d'une prévision en stocks et en personnel. Rien de ce qui suit n'est nécessaire au reste du volume.

Les méthodes de 5.2 prolongent le passé sans comprendre **pourquoi** les ventes varient. Or la gérante sait des choses sur l'avenir : le calendrier des promotions, les semaines de publicité prévues, les jours fériés. Une prévision pour la **planification** doit les utiliser, et leur donner un ordre de grandeur.

### 5.3.1 Régression avec variables indicatrices

L'idée est celle du chapitre 3 (régression linéaire), appliquée au temps : on explique le niveau de ventes de chaque jour par un **calendrier** (le mois, le jour de la semaine), des **décisions** (promotion, dépense publicitaire) et une **tendance**. Les variables qualitatives (le mois, le jour de semaine) deviennent des **indicatrices** : pour chaque modalité, une colonne qui vaut 1 si le jour est de cette modalité, 0 sinon. On prend le **logarithme** de la variable expliquée, pour que les coefficients se lisent comme des **pourcentages** d'effet (un coefficient de 0,17 correspond à une hausse d'environ 19 % : $e^{0{,}17}-1$).

On explique le **nombre de commandes** plutôt que le chiffre d'affaires : le nombre de commandes ne subit pas les remises et les hausses de prix, qui brouilleraient les effets que l'on veut isoler. Pour la publicité, on retient la dépense des **sept derniers jours** (en milliers d'euros), car l'effet d'un jour de publicité s'étale sur les jours suivants.

```python
dj = j.reset_index().assign(mois=lambda x: x["date"].dt.month, jds=lambda x: x["date"].dt.dayofweek, t=lambda x: (x["date"] - x["date"].min()).dt.days / 365.25)
dj["pub7"] = dj["depense_pub"].rolling(7, min_periods=1).sum() / 1000        # dépense des 7 derniers jours, en k€
tr5, te5 = dj[dj["date"] < "2025-01-01"], dj[dj["date"] >= "2025-01-01"]
mod = smf.ols("np.log(nb_commandes) ~ C(mois) + C(jds) + promo_active + pub7 + t", tr5).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
pct = lambda c: (np.exp(mod.params[c]) - 1) * 100
print({c: round(float(pct(c)), 1) for c in ("promo_active", "pub7", "t")})
```
<!--sortie-->
```text
{'promo_active': 21.7, 'pub7': -0.8, 't': 4.7}
```

```python hide
ic = (np.exp(mod.conf_int()) - 1) * 100
eff = pd.DataFrame({"estimation": [pct("promo_active"), pct("pub7"), pct("t")], "bas": [ic.loc[c, 0] for c in ("promo_active", "pub7", "t")], "haut": [ic.loc[c, 1] for c in ("promo_active", "pub7", "t")], "vérité": [18.0, 1.5, 6.0]},
                   index=["Jour de promotion", "+ 1 000 € de publicité sur 7 jours", "Tendance (par an)"])
for c, k in (("promo_active", "promo"), ("pub7", "pub"), ("t", "tend")):
    NUM(f"eff_{k}", fr(pct(c))); NUM(f"eff_{k}_lo", fr(ic.loc[c, 0])); NUM(f"eff_{k}_hi", fr(ic.loc[c, 1]))
NUM("n_train_j", len(tr5)); NUM("r2_ols", fr(mod.rsquared, 2))
FG.effets(eff)
```
<!--sortie-->
```text
NUM eff_promo 21,7
NUM eff_promo_lo 14,8
NUM eff_promo_hi 29,0
NUM eff_pub -0,8
NUM eff_pub_lo -6,4
NUM eff_pub_hi 5,2
NUM eff_tend 4,7
NUM eff_tend_lo 2,2
NUM eff_tend_hi 7,3
NUM n_train_j 731
NUM r2_ols 0,76
figure : ch05-effets-regression.png
```

![Effets estimés par la régression (points bleus, avec leur intervalle à 95 %) et valeurs programmées (losanges rouges).](figures/ch05-effets-regression.png)

Un **jour de promotion** augmente les commandes de **21,7 %** (intervalle de 14,8 % à 29,0 %). La **vérité programmée** est de +18 % : elle tombe dans l'intervalle, et l'analyse a retrouvé l'ordre de grandeur. La **tendance** est estimée à 4,7 % par an (intervalle de 2,2 % à 7,3 %) pour 6 % programmés : même constat. Pour la **publicité**, l'estimation est de -0,8 % par millier d'euros dépensé sur sept jours, avec un intervalle de -6,4 % à 5,2 % : **le zéro est au milieu de l'intervalle**. La vérité programmée est un effet de +1,5 %, qui existe bel et bien ; l'analyse ne peut pas le distinguer du hasard avec trois ans de données quotidiennes, parce qu'un effet de 1,5 % est noyé dans les variations de ±24 % d'un jour. Ce n'est pas une preuve d'inefficacité : c'est un défaut de **puissance** (section 2.5), et seule une expérience délibérée (tester la publicité sur certaines semaines seulement) permettrait de trancher.

La régression sert aussi à **prévoir**, à condition de connaître à l'avance les variables : le calendrier est connu, le programme de promotion se décide, la publicité se planifie. Prévoyons les commandes de 2025 avec le modèle ajusté sur 2023-2024, puis convertissons en chiffre d'affaires avec le **panier moyen** de la période d'entraînement.

```python
pred = np.exp(mod.predict(te5)) * np.exp(mod.mse_resid / 2)                  # correction de la retransformation du logarithme
mens = pd.DataFrame({"réel": te5.set_index("date")["nb_commandes"], "prévu": pred.values}).resample("MS").sum()
print("MAPE mensuelle sur les commandes :", round(O.mape(mens["réel"], mens["prévu"]), 1), "% | biais :", round((mens["prévu"].sum() / mens["réel"].sum() - 1) * 100, 1), "%")
```
<!--sortie-->
```text
MAPE mensuelle sur les commandes : 4.4 % | biais : -2.9 %
```

```python hide
mape_cmd = O.mape(mens["réel"], mens["prévu"]); biais_cmd = (mens["prévu"].sum() / mens["réel"].sum() - 1) * 100
panier = tr5["chiffre_affaires"].sum() / tr5["nb_commandes"].sum(); panier25 = te5["chiffre_affaires"].sum() / te5["nb_commandes"].sum()
ca_prev = mens["prévu"] * panier; ca_reel = te5.set_index("date")["chiffre_affaires"].resample("MS").sum()
NUM("mape_cmd", fr(mape_cmd)); NUM("biais_cmd", fr(biais_cmd)); NUM("panier_tr", fr(panier, 1)); NUM("panier_25", fr(panier25, 1))
NUM("mape_ca_reg", fr(O.mape(ca_reel, ca_prev))); NUM("biais_ca_reg", fr((ca_prev.sum() / ca_reel.sum() - 1) * 100))
NUM("mae_cmd_j", fr(O.mae(te5["nb_commandes"], pred), 1)); NUM("moy_cmd_j", fr(te5["nb_commandes"].mean(), 1))
```
<!--sortie-->
```text
NUM mape_cmd 4,4
NUM biais_cmd -2,9
NUM panier_tr 99,3
NUM panier_25 102,3
NUM mape_ca_reg 6,6
NUM biais_ca_reg -5,8
NUM mae_cmd_j 4,3
NUM moy_cmd_j 35,5
```

Sur les **commandes**, l'erreur mensuelle est de 4,4 % (biais de -2,9 %), meilleure que celle de toutes les méthodes simples de 5.2 sur le chiffre d'affaires. Ce n'est pas tout à fait comparable : la régression bénéficie ici de la **connaissance du calendrier de promotion de 2025** et ne subit pas l'effet prix. Si l'on convertit en euros avec le panier moyen de 2023-2024 (99,3 €, alors qu'il vaut 102,3 € en 2025), l'erreur sur le chiffre d'affaires est de 6,6 % (biais de -5,8 %) : la hausse de prix de 2025, que le modèle n'a pas vue, ramène l'erreur au niveau des méthodes simples de 5.2 (7,0 % pour la meilleure).

> 💡 **Intuition.** La régression ne prédit pas mieux **parce qu'elle est plus savante**, mais parce qu'elle sait quelque chose de plus : le calendrier. Son avantage disparaît quand ce que l'on connaît à l'avance est faux ou incomplet, comme ici pour les prix.

### 5.3.2 Le modèle ARIMA saisonnier, en une page

Les modèles **ARIMA** sont la famille classique de la prévision statistique. Leur nom décrit leurs ingrédients : une partie **autorégressive** (AR : la valeur d'aujourd'hui dépend des valeurs d'hier et d'avant-hier), une partie **d'intégration** (I : on travaille sur les **variations** plutôt que sur les niveaux, pour enlever la tendance), une partie **moyenne mobile** (MA : on corrige à l'aide des erreurs récentes). La version **saisonnière** applique les mêmes idées au motif qui se répète (ici, tous les 7 jours). On note $(p,d,q)\times(P,D,Q)_s$ les ordres de chaque partie et la période $s$ ; le modèle $(1,1,1)\times(0,1,1)_7$ est un classique de la série quotidienne.

En pratique, `statsmodels` s'en occupe : on donne la série (en logarithme, pour que la saison soit multiplicative) et les ordres, et l'on obtient des prévisions avec leurs intervalles.

```python
import statsmodels.api as sm
ajust = sm.tsa.SARIMAX(np.log(y[:"2025-09-30"].iloc[-180:]), order=(1, 1, 1), seasonal_order=(0, 1, 1, 7)).fit(disp=False, maxiter=50)
prevu = np.exp(ajust.forecast(28))                                       # 28 jours après le 30 septembre 2025
print("octobre 2025 : prévu", round(prevu[:28].sum()), "€ pour 28 jours ; réalisé", round(y["2025-10-01":"2025-10-28"].sum()), "€")
```
<!--sortie-->
```text
octobre 2025 : prévu 107991 € pour 28 jours ; réalisé 108802 €
```

```python hide
NUM("sar_prevu", fr(prevu[:28].sum(), 0)); NUM("sar_reel", fr(y["2025-10-01":"2025-10-28"].sum(), 0))
cmp_s = O.comparer_sarima_hw(y)
NUM("sar_n", len(cmp_s)); NUM("sar_mae", fr(cmp_s["SARIMA"].mean(), 0)); NUM("hw_mae", fr(cmp_s["Holt-Winters"].mean(), 0))
NUM("sar_tot", fr(cmp_s["SARIMA total"].mean())); NUM("hw_tot", fr(cmp_s["Holt-Winters total"].mean()))
```
<!--sortie-->
```text
NUM sar_prevu 107 991
NUM sar_reel 108 802
NUM sar_n 24
NUM sar_mae 718
NUM hw_mae 690
NUM sar_tot 12,4
NUM hw_tot 10,0
```

Pour octobre 2025 (28 jours), ce modèle prévoit 107 991 € pour 108 802 € réalisés. Un ajustement isolé ne prouve rien. Comparons donc, comme en 5.2.4, ce modèle à Holt-Winters sur 24 origines (une toutes les deux semaines en 2025), avec un horizon de 28 jours : la MAE quotidienne est de 718 € pour le modèle ARIMA saisonnier et de 690 € pour Holt-Winters ; l'erreur sur le total des 28 jours est de 12,4 % contre 10,0 %. **Le modèle plus savant ne fait pas mieux** : à ce pas et sur cette série, il retrouve la structure hebdomadaire que Holt-Winters capte déjà.

> ⚠️ **Prudence avec ARIMA.** Ces modèles demandent de **choisir des ordres**, de vérifier que la série est stationnaire après différenciation, et leurs paramètres peuvent devenir instables sur peu de données : en leur ajoutant des variables explicatives sur une série de 24 mois, nous avons obtenu des coefficients autorégressifs collés à 1 et des prévisions très biaisées. ARIMA vaut son prix quand on a **beaucoup de séries à prévoir** et le temps de les surveiller. Pour une boutique, le lissage exponentiel et la régression avec calendrier suffisent presque toujours.

### 5.3.3 Prévoir le total ou prévoir par canal ?

La gérante veut un chiffre pour l'ensemble, mais ses canaux n'évoluent pas pareil : de 2024 à 2025, la Boutique progresse de 0,5 %, les Réseaux de 13,4 % et le Site de 22,9 %. Deux stratégies : prévoir **directement le total**, ou prévoir **chaque canal** puis additionner (approche « du bas vers le haut »). Une troisième répartit la prévision du total selon les **parts** observées de chaque canal (« du haut vers le bas »).

```python
cc = O.ca_par_canal()                                             # chiffre d'affaires mensuel par canal
bu = sum(O.prevision_tendance_indices(cc[c], "2024-12-01") for c in cc)       # bas vers haut : somme des prévisions par canal
direct = O.prevision_tendance_indices(cc.sum(axis=1), "2024-12-01")            # prévision directe du total
reel = cc.sum(axis=1)["2025-01-01":]
print("MAPE du total : direct", round(O.mape(reel, direct), 1), "% | bas vers haut", round(O.mape(reel, bu), 1), "%")
```
<!--sortie-->
```text
MAPE du total : direct 7.0 % | bas vers haut 6.9 %
```

```python hide
NUM("hier_direct", fr(O.mape(reel, direct), 2)); NUM("hier_bu", fr(O.mape(reel, bu), 2))
part = cc[:"2024-12-01"].sum() / cc[:"2024-12-01"].sum().sum()
lignes = []
for c in cc:
    pc = O.prevision_tendance_indices(cc[c], "2024-12-01"); th = direct * part[c]; rc = cc[c]["2025-01-01":]
    lignes.append((c, O.mape(rc, pc), O.mape(rc, th)))
    NUM(f"hier_{c[:3]}_bu", fr(O.mape(rc, pc))); NUM(f"hier_{c[:3]}_td", fr(O.mape(rc, th)))
```
<!--sortie-->
```text
NUM hier_direct 6,99
NUM hier_bu 6,92
NUM hier_Bou_bu 9,3
NUM hier_Bou_td 10,2
NUM hier_Rés_bu 14,4
NUM hier_Rés_td 12,2
NUM hier_Sit_bu 10,5
NUM hier_Sit_td 19,5
```

Pour le **total**, les deux approches sont équivalentes (6,99 % pour la prévision directe, 6,92 % pour la somme des canaux). L'intérêt de l'approche par canal est ailleurs : elle donne une prévision **pour chaque canal**, utile pour planifier le stock du site et le personnel de la boutique. Et pour cela, partir du total est **mauvais** : répartir le total selon les parts de 2023-2024 donne, pour le Site, une erreur de 19,5 % contre 10,5 % en prévoyant le canal directement, parce que la part du Site croît (la répartition fixe ne le sait pas). Pour la Boutique, les deux approches sont comparables (10,2 % et 9,3 %).

> 🧭 **En pratique.** Prévoyez au niveau où l'on **décide** : le total pour le budget, le canal pour la logistique, la catégorie pour les achats. Plus on descend, plus le hasard pèse (5.2.6) : au-dessous d'un certain niveau de détail, la prévision individuelle est moins fiable qu'une répartition du total.

### 5.3.4 L'effet de l'horizon

Un horizon plus long donne-t-il une prévision moins bonne ? Pour des **niveaux**, oui ; pour des **sommes**, pas forcément. Comparons deux méthodes sur le total de $h$ jours, pour $h$ de 7 à 84, à toutes les origines hebdomadaires de 2025 : la première prolonge le **niveau récent** (moyenne des 28 derniers jours), la seconde reprend le **même jour de l'an dernier**, ajusté du niveau récent.

```python
tab_h = O.erreur_par_horizon(y)                                   # erreur relative (%) sur le total de h jours
print(tab_h.round(1).to_string())
```
<!--sortie-->
```text
    niveau récent (plat)  an dernier × niveau récent
7                   12.9                        12.5
14                  11.2                         8.8
28                  10.5                         6.5
56                  11.9                         4.6
84                  12.9                         4.5
```

```python hide
tab_h = O.erreur_par_horizon(y)
for h in tab_h.index:
    NUM(f"h_plat_{h}", fr(tab_h.loc[h, "niveau récent (plat)"])); NUM(f"h_ly_{h}", fr(tab_h.loc[h, "an dernier × niveau récent"]))
FG.horizon(tab_h)
```
<!--sortie-->
```text
NUM h_plat_7 12,9
NUM h_ly_7 12,5
NUM h_plat_14 11,2
NUM h_ly_14 8,8
NUM h_plat_28 10,5
NUM h_ly_28 6,5
NUM h_plat_56 11,9
NUM h_ly_56 4,6
NUM h_plat_84 12,9
NUM h_ly_84 4,5
figure : ch05-horizon.png
```

![Erreur relative sur le total des h jours suivants, selon l'horizon, pour une prévision plate et pour une prévision saisonnière.](figures/ch05-horizon.png)

La méthode **saisonnière** s'améliore avec l'horizon : l'erreur passe de 12,5 % pour une semaine à 6,5 % pour 28 jours et à 4,5 % pour 84 jours, parce que le hasard d'un jour à l'autre **se compense** quand on additionne, alors que la saison est connue. La prévision **plate** ne bénéficie pas de cet effet : elle ne s'améliore pas (12,9 % à une semaine, 12,9 % à 84 jours) parce qu'elle ignore que la saison **change** le niveau. Deux conséquences pratiques : prévoyez **des sommes** plutôt que des jours isolés, et donnez la saison à une prévision à long terme.

> ⚠️ **Piège.** L'erreur **relative** qui baisse avec l'horizon ne veut pas dire que le long terme est facile. Elle baisse parce que l'on additionne ; mais le **biais de niveau** (le changement de régime de 2025) ne s'efface pas, et il pèse davantage sur les horizons que l'on ne peut pas corriger en route.

### 5.3.5 Des scénarios plutôt qu'un chiffre

La gérante demande « combien en décembre prochain ? ». Une réponse honnête est un **chiffre central** accompagné de **scénarios** qui disent ce qui le ferait varier. Décembre 2025 a rapporté 183 845 €. Pour décembre 2026, la question est la **croissance**, et nous savons depuis 5.2 qu'elle est l'inconnue principale. Trois scénarios :

- **prudent** : la croissance de 2024 (+4,4 %), c'est-à-dire sans effet de prix ;
- **central** : la **tendance de fond** estimée en 5.1.6 (+6,5 % par an), sans nouvelle hausse de prix ;
- **avec hausse de prix** : la tendance de fond, plus un relèvement de prix de 3 % comme en 2025.

```python
dec25 = m["2025-12-01"]
scen = {"prudent": dec25 * (1 + 0.044), "central": dec25 * (1 + 0.065), "hausse de prix": dec25 * 1.065 * 1.03}
print({k: round(v) for k, v in scen.items()})
```
<!--sortie-->
```text
{'prudent': 191934, 'central': 195795, 'hausse de prix': 201669}
```

```python hide
for k, c in (("prudent", "sc_bas"), ("central", "sc_mid"), ("hausse de prix", "sc_haut")):
    NUM(c, fr(scen[k], 0))
NUM("dec25", fr(dec25, 0))
f36 = O.prevision_tendance_indices(m, "2025-12-01", 12)
NUM("mod_dec26", fr(f36["2026-12-01"], 0))
hist = {an: m[str(an)].values for an in (2023, 2024, 2025)}
FG.scenarios(m, hist, scen)
```
<!--sortie-->
```text
NUM sc_bas 191 934
NUM sc_mid 195 795
NUM sc_haut 201 669
NUM dec25 183 845
NUM mod_dec26 190 904
figure : ch05-scenarios.png
```

![Chiffre d'affaires mensuel des trois dernières années et trois scénarios pour décembre 2026.](figures/ch05-scenarios.png)

Les trois scénarios donnent 191 934 €, 195 795 € et 201 669 € pour décembre 2026. En comparaison, la méthode « tendance × indices » ajustée sur les 36 mois prévoit 190 904 €, **juste sous le scénario prudent** : la droite ajustée sur trois ans est un peu plus prudente que le scénario central, mais elle raconte la même histoire. L'écart entre le scénario prudent et le scénario avec hausse de prix est d'environ **5 %** : voilà l'ordre de grandeur de l'incertitude à déclarer, et il vient d'**une hypothèse** (le prix), pas du modèle.

Les scénarios servent aussi à **peser une décision**. Sur novembre, la régression de 5.3.1 donne l'effet d'une promotion : +21,7 % de commandes les jours de promotion. Le « Vendredi noir » couvre neuf jours de novembre ; sans lui, les commandes du mois baisseraient d'environ **6,1 %**, une fois l'effet des neuf jours retiré.

```python hide
NUM("ecart_sc", fr((scen["hausse de prix"] / scen["prudent"] - 1) * 100, 0))
mult = np.exp(mod.params["promo_active"]); sans_vn = (1 - (30 / (21 + 9 * mult))) * 100
NUM("sans_vn", fr((1 - 30 / (21 + 9 * mult)) * 100, 1))
```
<!--sortie-->
```text
NUM ecart_sc 5
NUM sans_vn 6,1
```

> 🧭 **En pratique.** Présentez trois chiffres et une phrase : « Entre X et Z, avec Y comme chiffre central ; l'écart vient surtout de la politique de prix ». Cela vaut mieux qu'un faux chiffre précis, et cela dit à la gérante **sur quoi elle a prise**.

### 5.3.6 De la prévision aux décisions : stock et personnel

Une prévision ne vaut que par les décisions qu'elle éclaire. Deux exemples chiffrés pour décembre 2026.

**Le personnel.** Le scénario central prévoit 195 795 € de chiffre d'affaires en décembre. Avec un panier moyen d'environ 100 €, cela fait environ 1 958 commandes, soit 63 par jour en moyenne. Les jours ne se valent pas : le samedi pèse 1,390 fois un jour moyen (5.1.7), soit environ 88 commandes un samedi de décembre. Si un collaborateur prépare environ **20 commandes par jour** (hypothèse illustrative : contrôle, emballage, expédition), il faut 5 personnes les samedis de pointe, contre 4 un jour moyen : dimensionner sur la moyenne laisserait chaque samedi en dessous de la charge. Pour couvrir l'incertitude, on vérifie le résultat sur le scénario **haut** (environ 3 % de commandes de plus), qui ne change pas ici le nombre de personnes.

**Le stock.** Pour un produit populaire, le stock de sécurité protège contre l'écart entre la demande prévue et la demande réelle pendant le délai de réapprovisionnement. Une formule classique : $\text{stock de sécurité}=z\times\sigma_j\times\sqrt{L}$, où $\sigma_j$ est l'écart-type de la demande **quotidienne**, $L$ le délai en jours et $z$ un coefficient lié au niveau de service visé ($z=1{,}65$ pour 95 %).

```python hide
top = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande"); top = top[top["date_commande"] >= "2025-11-01"]
p1 = top.groupby("id_produit")["quantite"].sum().idxmax()
dem = top[top["id_produit"] == p1].groupby("date_commande")["quantite"].sum().reindex(pd.date_range("2025-11-01", "2025-12-31").strftime("%Y-%m-%d"), fill_value=0)
mu_j, sd_j = dem.mean(), dem.std()
L = 14; ss = 1.65 * sd_j * np.sqrt(L); besoin = mu_j * L + ss
NUM("prod_top", int(p1)); NUM("mu_j", fr(mu_j, 2)); NUM("sd_j", fr(sd_j, 2)); NUM("ss", fr(ss, 0)); NUM("besoin_stock", fr(besoin, 0)); NUM("dem_delai", fr(mu_j * L, 0))
cmd_dec = scen["central"] / 100
NUM("cmd_dec", fr(cmd_dec, 0)); NUM("cmd_jour", fr(cmd_dec / 31, 0))
cmd_sam = cmd_dec / 31 * di[5]; NUM("cmd_sam", fr(cmd_sam, 0)); NUM("pers_sam", int(np.ceil(cmd_sam / 20))); NUM("pers_moy", int(np.ceil(cmd_dec / 31 / 20)))
```
<!--sortie-->
```text
NUM prod_top 41
NUM mu_j 3,69
NUM sd_j 2,61
NUM ss 16
NUM besoin_stock 68
NUM dem_delai 52
NUM cmd_dec 1 958
NUM cmd_jour 63
NUM cmd_sam 88
NUM pers_sam 5
NUM pers_moy 4
```

Pour le produit le plus vendu de novembre et décembre 2025, la demande est de 3,69 unités par jour en moyenne, avec un écart-type de 2,61. Pour un délai de réapprovisionnement de 14 jours et un niveau de service de 95 %, le stock de sécurité est d'environ **16 unités** ; le stock nécessaire au moment de commander est de 52 unités pour couvrir la demande attendue pendant le délai, plus ce stock de sécurité, soit **68 unités**. Un niveau de service plus exigeant (99 % ; $z=2{,}33$) augmente le stock de sécurité d'environ 40 % : **chaque point de service a un coût**, et c'est à la gérante de choisir.

### 5.3.7 Quand un modèle simple suffit

Résumons ce chapitre sur la question qui compte : **quel outil pour quelle situation ?**

| Situation | Outil recommandé | Pourquoi |
|---|---|---|
| Peu d'historique (moins de trois ans), décision à ± 10 % | Naïve saisonnière × croissance | Ne se trompe pas plus que les autres, s'explique en une phrase |
| Calendrier de promotions ou de publicité connu à l'avance | Régression avec indicatrices | Utilise ce que l'on sait de l'avenir, donne des effets chiffrés |
| Prévision quotidienne à court terme | Holt-Winters (saison de 7 jours) | Atteint presque le plancher du hasard |
| Prévision par canal ou catégorie | Méthode simple appliquée à chaque série, puis comparaison avec le total | Les parts changent ; la répartition fixe est mauvaise |
| Beaucoup de séries à suivre, des données longues | ARIMA saisonnier ou méthodes automatiques | Seulement si l'on a le temps de les surveiller |
| Changement de régime probable (prix, nouveau canal) | Scénarios | Aucun modèle ne le connaît : on dit ce que l'on suppose |

> ✅ **À retenir.**
> - La **régression avec indicatrices** (mois, jour, promotion, publicité, tendance) prévoit bien quand l'avenir **connu** est utilisé ; elle donne des effets en %, avec leur intervalle : la promotion se détecte, une publicité à +1,5 % reste dans le bruit.
> - Un modèle **ARIMA** n'est pas meilleur par nature : sur cette série, il fait jeu égal avec le lissage exponentiel, en demandant plus de soin.
> - Prévoyez **au niveau où l'on décide** ; les sommes sont plus faciles à prévoir que les jours isolés ; la saison aide d'autant plus que l'horizon est long.
> - Une prévision pour la planification se présente en **scénarios**, et se traduit en décisions (personnel de pointe, stock de sécurité) avec un niveau de service **choisi**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.8 et 5.9 et exercices 5.11 et 5.12.
