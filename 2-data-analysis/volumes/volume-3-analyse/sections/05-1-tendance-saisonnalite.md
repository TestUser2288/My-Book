## 5.1 Tendances et saisonnalité

La première question de la gérante demande de **séparer** ce qui monte de ce qui revient. Cette section donne les outils pour le faire : une décomposition en composantes, une comparaison honnête à l'année précédente, des indices saisonniers que l'on sait calculer à la main, une prise en compte du calendrier, et des réflexes pour traiter les ruptures et les incidents. Tout se fait sur le chiffre d'affaires TTC de la boutique.

### 5.1.1 Trois composantes

Une série temporelle $y_t$ (le chiffre d'affaires du mois $t$) se lit comme la combinaison de trois ingrédients.

- La **tendance** $T_t$ : le niveau de fond, qui évolue lentement (la clientèle grandit, les prix montent). C'est ce que la gérante appelle « progresser vraiment ».
- La **saison** $S_t$ : un motif qui **se répète à intervalle fixe**, ici chaque année (décembre fort, février faible) et chaque semaine (samedi fort, dimanche faible).
- Le **résidu** $R_t$ : tout le reste, c'est-à-dire le hasard (le nombre de clients qui poussent la porte un mardi donné) et les événements ponctuels.

Deux manières de les assembler. Dans le **modèle additif**, $y_t=T_t+S_t+R_t$ : la saison ajoute ou retire un nombre **d'euros** constant (« décembre ajoute 60 000 € »). Dans le **modèle multiplicatif**, $y_t=T_t\times S_t\times R_t$ : la saison multiplie le niveau par un **coefficient** (« décembre vaut 1,58 fois un mois moyen »). Le choix dépend de la forme de la série : si l'amplitude des oscillations **grandit avec le niveau**, le multiplicatif est le bon modèle (nous le vérifierons en 5.1.5).

> 💡 **Intuition.** Pensez à un thermomètre de cuisine placé dans un four dont on monte la température : la tendance est la température de consigne, la saison est la montée et la descente de chaque cycle de chauffe, le résidu est le tremblement de l'aiguille. On ne juge pas la consigne en regardant l'aiguille à un instant.

Pour **voir** la tendance, on remplace chaque mois par la moyenne des douze mois qui l'entourent : sur une année complète, la saison s'annule (chaque mois du calendrier apparaît une fois), et ce qui reste est le niveau de fond. C'est la **moyenne mobile centrée** que l'on étudiera en détail en 5.2.1.

![Chiffre d'affaires mensuel (bleu) et sa tendance (orange), calculée par une moyenne mobile centrée sur douze mois. L'écart entre les deux courbes est la saison et le résidu.](figures/ch05-composantes.png)

```python hide
FG.composantes(m)
```
<!--sortie-->
```text
figure : ch05-composantes.png
```

La tendance est lisse et monte : de juillet 2023 à juin 2025, elle passe de 95 281 € à 109 291 € par mois. La moyenne mobile centrée ne peut pas être calculée aux deux extrémités (il faut six mois avant et après), ce qui est un premier piège que nous retrouverons (5.1.9).

### 5.1.2 Choisir le pas : jour, semaine ou mois

La même série existe à plusieurs **pas** : 1 096 points au jour, environ 157 à la semaine, 36 au mois. Le pas n'est pas neutre.

- **Au jour**, la série est dominée par le **calendrier** (le samedi vend plus que le lundi) et par le hasard : on voit surtout du bruit et un créneau hebdomadaire.
- **À la semaine**, le créneau disparaît (chaque semaine contient chaque jour de semaine une fois) ; il reste la saison annuelle et le bruit.
- **Au mois**, la série est lisible, mais elle ne compte plus que 36 points et ses mois ont des **longueurs inégales** (28 à 31 jours) et des compositions inégales (quatre ou cinq samedis).

```python hide
FG.pas(j)
jm = j["chiffre_affaires"].resample("MS").agg(["sum", "size"])
NUM("jan25", fr(jm.loc["2025-01-01", "sum"], 0)); NUM("fev25", fr(jm.loc["2025-02-01", "sum"], 0))
NUM("jan25_j", fr(jm.loc["2025-01-01", "sum"] / 31, 0)); NUM("fev25_j", fr(jm.loc["2025-02-01", "sum"] / 28, 0))
NUM("ecart_mois", fr((jm.loc["2025-02-01", "sum"] / jm.loc["2025-01-01", "sum"] - 1) * 100))
NUM("ecart_jour", fr((jm.loc["2025-02-01", "sum"] / 28 / (jm.loc["2025-01-01", "sum"] / 31) - 1) * 100))
```
<!--sortie-->
```text
figure : ch05-pas.png
NUM jan25 89 179
NUM fev25 72 642
NUM jan25_j 2 877
NUM fev25_j 2 594
NUM ecart_mois -18,5
NUM ecart_jour -9,8
```

![Le même chiffre d'affaires de septembre à décembre 2025 au jour, à la semaine et au mois.](figures/ch05-pas.png)

Un exemple suffit pour se méfier des mois bruts. Février 2025 a vendu 72 642 € et janvier 89 179 € : février est **-18,5 %** plus bas. Mais janvier a 31 jours et février 28 : ramené **au jour**, février vend 2 594 € par jour contre 2 877 € en janvier, soit seulement **-9,8 %**. Plus de la moitié de l'écart apparent vient simplement de la longueur du mois.

> 🧭 **En pratique.** Choisissez le pas selon **la décision**. Un réapprovisionnement hebdomadaire se pilote à la semaine ; un budget annuel au mois. Gardez toujours la série au pas le plus fin : on peut toujours agréger, on ne peut jamais désagréger. Et n'agrégez pas des pourcentages (5.1.9) : on **somme** les montants, puis on calcule le pourcentage.

### 5.1.3 Comparer à la même période de l'an dernier

La saison rend inutile la comparaison d'un mois au précédent : décembre bat toujours novembre. La comparaison honnête met en face **le même mois de l'année précédente**, où la saison est la même : c'est la **variation annuelle** (ou « à un an d'écart »).

$$\text{variation annuelle}_t=\frac{y_t}{y_{t-12}}-1.$$

Elle supprime la saison, mais elle reste **bruyante** quand on la calcule mois par mois. On le voit sur 2025 : les variations mensuelles vont de -1,2 % à 18,5 %, avec un écart-type de 6,2 points, alors que l'année entière progresse de 11,4 %. Un mois isolé qui « baisse de 1 % » n'invalide pas une tendance de +11 %.

```python hide
yoy25 = (m["2025"].values / m["2024"].values - 1) * 100
NUM("yoy_min", fr(yoy25.min())); NUM("yoy_max", fr(yoy25.max())); NUM("yoy_sd", fr(yoy25.std()))
r12 = m.rolling(12).sum(); g12 = (r12 / r12.shift(12) - 1) * 100
for d, cle in (("2024-12-01", "g_dec24"), ("2025-03-01", "g_mar25"), ("2025-06-01", "g_jun25"), ("2025-09-01", "g_sep25"), ("2025-12-01", "g_dec25")):
    NUM(cle, fr(g12[d]))
NUM("jan_dec", fr((m["2025-01-01"] / m["2024-12-01"] - 1) * 100))
```
<!--sortie-->
```text
NUM yoy_min -1,2
NUM yoy_max 18,5
NUM yoy_sd 6,2
NUM g_dec24 4,4
NUM g_mar25 5,1
NUM g_jun25 5,0
NUM g_sep25 7,4
NUM g_dec25 11,4
NUM jan_dec -43,3
```

Pour lisser le bruit sans perdre la comparaison à l'an dernier, on utilise le **glissement annuel** : on somme les **douze derniers mois** et l'on compare à la somme des douze mois d'un an plus tôt. Cette mesure couvre toujours une année complète, donc toute la saison. Ses valeurs racontent l'accélération : 4,4 % à fin 2024, 5,1 % à fin mars 2025, 5,0 % à fin juin, 7,4 % à fin septembre, et 11,4 % à fin 2025. La progression ne se répartit donc pas uniformément : elle s'est nettement accélérée à partir de l'été 2025.

> ⚠️ **Piège : la comparaison de mois consécutifs.** De décembre 2024 à janvier 2025, le chiffre d'affaires « chute » de **-43,3 %**. Personne n'en conclura à une catastrophe : janvier est toujours le lendemain de décembre. Comparer deux mois voisins sur une série saisonnière mesure la saison, pas la tendance. Quand on doit absolument comparer un mois au précédent, on le fait sur la série **désaisonnalisée** (5.1.4 et 5.1.5).

### 5.1.4 Les indices saisonniers, calculés à la main

Un **indice saisonnier** dit de combien un mois s'écarte d'un mois moyen **à cause de la saison seule**. La méthode classique tient en trois étapes, que l'on déroule d'abord sur les **trimestres** (douze nombres, calculables à la main), puis que l'on applique aux mois.

1. **Isoler la tendance** : moyenne mobile centrée sur un cycle complet. Avec des trimestres, un cycle compte quatre périodes ; pour que la moyenne soit centrée sur un trimestre précis, on prend 0,5 fois le trimestre le plus ancien, les trois du milieu entiers, et 0,5 fois le plus récent, le tout divisé par 4.
2. **Rapport à la tendance** : on divise la valeur observée par cette moyenne ; un rapport de 1,3 signifie « 30 % au-dessus du niveau de fond ».
3. **Moyenner par position** : on moyenne les rapports d'un même trimestre sur les années, puis on **normalise** pour que la moyenne des indices soit 1.

```python hide
q = m.resample("QS").sum()
ma = (0.5 * q.shift(2) + q.shift(1) + q + q.shift(-1) + 0.5 * q.shift(-2)) / 4
tq = pd.DataFrame({"trimestre": [f"T{d.quarter} {d.year}" for d in q.index], "CA (k€)": (q / 1000).round(1).values, "tendance (k€)": (ma / 1000).round(1).values, "rapport": (q / ma).round(3).values}).dropna()
rap = (q / ma).dropna(); par_t = rap.groupby(rap.index.quarter).mean(); iq = par_t / par_t.mean()
for i in range(1, 5):
    NUM(f"iq{i}", fr(iq[i], 3)); NUM(f"rq{i}_moy", fr(par_t[i], 3))
NUM("som_rq", fr(par_t.sum(), 3))
assert abs(iq.mean() - 1) < 1e-9
tq_aff = tq.copy()
tq_aff["tendance (k€)"] = tq_aff["tendance (k€)"].map(lambda v: fr(v)); tq_aff["CA (k€)"] = tq_aff["CA (k€)"].map(lambda v: fr(v)); tq_aff["rapport"] = tq_aff["rapport"].map(lambda v: fr(v, 3))
```
<!--sortie-->
```text
NUM iq1 0,790
NUM rq1_moy 0,787
NUM iq2 0,983
NUM rq2_moy 0,980
NUM iq3 0,928
NUM rq3_moy 0,925
NUM iq4 1,299
NUM rq4_moy 1,295
NUM som_rq 3,988
```

Voici, sur les huit trimestres où la moyenne centrée existe (les deux premiers et les deux derniers trimestres de la série n'en ont pas), le calcul de l'étape 1 et de l'étape 2.

```python hide-code
print(tq_aff.to_string(index=False))
```
<!--sortie-->
```text
trimestre CA (k€) tendance (k€) rapport
  T3 2023   267,0         286,9   0,930
  T4 2023   381,7         290,9   1,312
  T1 2024   226,0         293,9   0,769
  T2 2024   296,4         296,2   1,001
  T3 2024   276,4         300,6   0,920
  T4 2024   390,7         305,6   1,279
  T1 2025   251,6         312,1   0,806
  T2 2025   310,8         324,1   0,959
```

Les rapports d'un même trimestre se ressemblent d'une année à l'autre : le quatrième trimestre tourne autour de 1,3 (1,295 en moyenne), le premier autour de 0,8 (0,787). On moyenne par trimestre, puis on **normalise** : la somme des quatre moyennes vaut 3,988, alors qu'elle devrait valoir 4 ; on divise donc chaque moyenne par 3,988 / 4. Les indices trimestriels sont :

| Trimestre | T1 | T2 | T3 | T4 |
|---|---|---|---|---|
| Indice saisonnier | 0,790 | 0,983 | 0,928 | 1,299 |

Le quatrième trimestre vend donc environ **30 % de plus** qu'un trimestre moyen, le premier environ **21 % de moins**. Pour les **mois**, la méthode est identique, avec une moyenne centrée sur douze mois (en fait deux moyennes de douze mois décalées d'un mois, pour que le centre tombe sur un mois précis) : on obtient douze indices dont la moyenne vaut 1.

```python
idx = O.indices_saisonniers(m)              # rapport à la moyenne mobile centrée, moyenné par mois, normalisé
print(idx.round(3).to_dict())
```
<!--sortie-->
```text
{1: 0.821, 2: 0.677, 3: 0.87, 4: 0.906, 5: 1.032, 6: 1.014, 7: 0.945, 8: 0.819, 9: 1.015, 10: 1.036, 11: 1.281, 12: 1.583}
```

```python hide
NUM("idx_dec", fr(idx[12], 3)); NUM("idx_fev", fr(idx[2], 3)); NUM("idx_nov", fr(idx[11], 3)); NUM("idx_jan", fr(idx[1], 3)); NUM("idx_aout", fr(idx[8], 3))
NUM("idx_som", fr(idx.sum(), 3))
FG.indices(idx)
```
<!--sortie-->
```text
NUM idx_dec 1,583
NUM idx_fev 0,677
NUM idx_nov 1,281
NUM idx_jan 0,821
NUM idx_aout 0,819
NUM idx_som 12,000
figure : ch05-indices.png
```

![Indices saisonniers mensuels du chiffre d'affaires : mois moyen = 1.](figures/ch05-indices.png)

Décembre vaut 1,583 fois un mois moyen, novembre 1,281, février seulement 0,677 ; les douze indices somment à 12,000. **Désaisonnaliser** une série, c'est diviser chaque mois par son indice : on obtient ce que le mois « aurait vendu » dans un mois moyen, et les mois deviennent enfin comparables entre eux.

> 📐 **Pourquoi normaliser ?** Un indice saisonnier n'a de sens que **relativement** : si tous les indices étaient multipliés par 2, la saison ne changerait pas, mais la série désaisonnalisée serait divisée par 2 et sa tendance serait faussée d'un facteur arbitraire. La normalisation (moyenne 1) fixe l'échelle : la série désaisonnalisée a le **même niveau moyen** que la série d'origine.

### 5.1.5 Décomposer : additif ou multiplicatif, `seasonal_decompose` et STL

Deux outils de `statsmodels` font ce calcul, et bien davantage, en une ligne : `seasonal_decompose` (la méthode à la main de la section précédente) et **STL** (*Seasonal-Trend decomposition using Loess*), plus souple.

```python
from statsmodels.tsa.seasonal import seasonal_decompose, STL
dm = seasonal_decompose(m, model="multiplicative", period=12)     # observé = tendance × saison × résidu
st = STL(np.log(m), period=12, robust=True).fit()                  # même idée sur le logarithme (somme = produit)
print("janvier, indice classique :", round(dm.seasonal.iloc[0], 3), "| indices STL des trois janviers :", np.exp(st.seasonal[st.seasonal.index.month == 1]).round(3).values)
```
<!--sortie-->
```text
janvier, indice classique : 0.821 | indices STL des trois janviers : [0.735 0.8   0.871]
```

```python hide
dm = seasonal_decompose(m, model="multiplicative", period=12)
res = dm.resid.dropna()
NUM("dm_jan", fr(dm.seasonal.iloc[0], 3)); sj = np.exp(st.seasonal[st.seasonal.index.month == 1]).values; NUM("stl_j1", fr(sj[0], 3)); NUM("stl_j2", fr(sj[1], 3)); NUM("stl_j3", fr(sj[2], 3)); NUM("res_sd", fr(res.std() * 100)); NUM("res_min", fr(res.min(), 3)); NUM("res_max", fr(res.max(), 3))
NUM("res_pire_mois", f"{res.idxmin().month:02d}/{res.idxmin().year}")
tend = dm.trend.dropna(); NUM("tend_debut", fr(tend.iloc[0], 0)); NUM("tend_fin", fr(tend.iloc[-1], 0))
FG.decomposition(m)
dec = {an: (m[f"{an}-12-01"] / m[f"{an}-02-01"], m[f"{an}-12-01"] - m[f"{an}-02-01"]) for an in (2023, 2024, 2025)}
for an in dec:
    NUM(f"rap{an}", fr(dec[an][0], 2)); NUM(f"dif{an}", fr(dec[an][1], 0))
```
<!--sortie-->
```text
NUM dm_jan 0,821
NUM stl_j1 0,735
NUM stl_j2 0,800
NUM stl_j3 0,871
NUM res_sd 3,0
NUM res_min 0,941
NUM res_max 1,052
NUM res_pire_mois 01/2024
NUM tend_debut 95 281
NUM tend_fin 109 291
figure : ch05-decomposition.png
NUM rap2023 2,50
NUM dif2023 94 306
NUM rap2024 2,46
NUM dif2024 93 366
NUM rap2025 2,53
NUM dif2025 111 202
```

Les deux outils racontent la même saison, avec une nuance instructive. `seasonal_decompose` impose un **profil unique** pour toute la période : janvier vaut 0,821, exactement la valeur calculée à la main plus haut. STL, plus souple, laisse le profil **évoluer lentement** : son indice de janvier est de 0,735 en 2023, 0,800 en 2024 et 0,871 en 2025. Un janvier qui s'étoffe d'une année sur l'autre est un fait que le profil unique ignore ; avec trois années seulement, on ne sait pas encore s'il s'agit d'une vraie évolution de la saison ou du bruit. Avec `robust=True`, STL n'est en outre pas dérangé par un mois exceptionnel.

![Décomposition multiplicative du chiffre d'affaires mensuel : observé, tendance, saison et résidu.](figures/ch05-decomposition.png)

**Additif ou multiplicatif ?** Regardons l'écart entre décembre et février, chaque année. Le **rapport** décembre/février est quasi constant : 2,50 en 2023, 2,46 en 2024, 2,53 en 2025. La **différence** en euros, elle, augmente : 94 306 € en 2023, 93 366 € en 2024, 111 202 € en 2025. La saison se comporte comme un **coefficient** qui s'applique à un niveau qui monte : c'est le signe d'un modèle **multiplicatif**. En pratique, si l'on hésite, on prend le logarithme de la série : un modèle multiplicatif devient additif, et tous les outils additifs redeviennent utilisables.

Le **résidu** de la décomposition est un indice autour de 1 : il va de 0,941 à 1,052, avec un écart-type de 3,0 % (la valeur la plus basse est celle de 01/2024, le mois où la série s'écarte le plus de « tendance × saison »). Un résidu qui garderait une structure (une série de mois consécutifs tous du même côté de 1, par exemple) dirait que la décomposition a oublié quelque chose, par exemple une **rupture**.

### 5.1.6 La tendance progresse-t-elle vraiment ?

La tendance extraite par la décomposition est une série ; on peut lui poser une question chiffrée : **de combien progresse-t-elle par an, et peut-on distinguer cette progression du hasard ?** On désaisonnalise la série, puis on ajuste une droite sur le **logarithme** : la pente d'une droite sur un logarithme est un **taux de croissance** (une pente de 0,06 signifie environ +6 % par an).

```python
des = m / idx.reindex(m.index.month).values                  # série désaisonnalisée
t = np.arange(len(m)) / 12                                    # le temps en années
reg = sm.OLS(np.log(des.values), sm.add_constant(t)).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
print("croissance annuelle :", round((np.exp(reg.params[1]) - 1) * 100, 1), "% ; intervalle à 95 % :", np.round((np.exp(reg.conf_int()[1]) - 1) * 100, 1))
```
<!--sortie-->
```text
croissance annuelle : 8.2 % ; intervalle à 95 % : [ 6.4 10. ]
```

```python hide
NUM("croiss", fr((np.exp(reg.params[1]) - 1) * 100)); lo, hi = (np.exp(reg.conf_int()[1]) - 1) * 100
NUM("croiss_lo", fr(lo)); NUM("croiss_hi", fr(hi)); assert reg.pvalues[1] < 0.001
ap = (m.index >= "2025-01-01").astype(float)
reg2 = sm.OLS(np.log(des.values), sm.add_constant(np.column_stack([t, ap]))).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
NUM("tend2", fr((np.exp(reg2.params[1]) - 1) * 100)); l2, h2 = (np.exp(reg2.conf_int()[1]) - 1) * 100; NUM("tend2_lo", fr(l2)); NUM("tend2_hi", fr(h2))
NUM("saut", fr((np.exp(reg2.params[2]) - 1) * 100)); ls, hs = (np.exp(reg2.conf_int()[2]) - 1) * 100; NUM("saut_lo", fr(ls)); NUM("saut_hi", fr(hs))
```
<!--sortie-->
```text
NUM croiss 8,2
NUM croiss_lo 6,4
NUM croiss_hi 10,0
NUM tend2 6,5
NUM tend2_lo 3,6
NUM tend2_hi 9,6
NUM saut 3,5
NUM saut_lo -0,8
NUM saut_hi 8,0
```

La progression estimée est de **8,2 % par an**, avec un intervalle à 95 % de 6,4 % à 10,0 %. Zéro est loin de l'intervalle (la probabilité qu'une telle pente apparaisse par hasard est inférieure à un pour mille) : **oui, les ventes progressent vraiment, au-delà de la saison**.

Deux précautions de méthode. D'abord, les erreurs d'une série temporelle sont **corrélées** d'un mois au suivant ; une régression ordinaire, qui suppose des erreurs indépendantes, annoncerait un intervalle **trop étroit**. L'option `cov_type="HAC"` (erreurs robustes à l'autocorrélation) corrige cela. Ensuite, la droite suppose une croissance **régulière**. Or nous savons que 2025 est différente (prix, voir 5.1.8). Ajoutons à la régression un **saut** de niveau en janvier 2025 : la tendance est alors de **6,5 % par an** (intervalle 3,6 % à 9,6 %) et le saut de **3,5 %** (intervalle -0,8 % à 8,0 %). Les intervalles sont larges, parce que trois années ne fournissent que 36 points ; mais les deux estimations sont proches de ce que la **vérité programmée** annonce : une demande qui croît de **6 % par an** et un prix catalogue relevé de **3 %** au 1er janvier 2025.

> 🧪 **Remarque.** La tendance à +8,2 % de la première régression est un **mélange** : de la croissance de fond (6 %) et d'un relèvement de prix ponctuel (3 %) étalé sur toute la série. Elle décrit bien le passé, et prédit mal le futur : si les prix ne montent plus, la progression sera plus proche de 6 % que de 8,2 %. Une tendance estimée n'est jamais une loi ; c'est un **résumé du passé** dont on doit connaître les ingrédients.

### 5.1.7 Le calendrier : jours de la semaine, mois inégaux

Au jour, le calendrier domine tout. On le mesure par un **indice du jour de semaine**, obtenu comme les indices mensuels : la moyenne du chiffre d'affaires de chaque jour de semaine, divisée par la moyenne générale.

```python
dow = j["chiffre_affaires"].groupby(j.index.dayofweek).mean()
print((dow / dow.mean()).round(3).to_dict())          # 0 = lundi ... 6 = dimanche
```
<!--sortie-->
```text
{0: 0.972, 1: 0.882, 2: 0.93, 3: 0.994, 4: 1.174, 5: 1.39, 6: 0.657}
```

```python hide
di = dow / dow.mean()
for i, n in enumerate(["lun", "mar", "mer", "jeu", "ven", "sam", "dim"]):
    NUM(f"dow_{n}", fr(di[i], 3))
NUM("sam_dim", fr(di[5] / di[6], 1))
cal = pd.Series(di.reindex(j.index.dayofweek).values, index=j.index).resample("MS").mean()
NUM("cal_min", fr(cal.min(), 3)); NUM("cal_max", fr(cal.max(), 3)); NUM("cal_ecart", fr((cal.max() / cal.min() - 1) * 100))
FG.jours_semaine(di)
```
<!--sortie-->
```text
NUM dow_lun 0,972
NUM dow_mar 0,882
NUM dow_mer 0,930
NUM dow_jeu 0,994
NUM dow_ven 1,174
NUM dow_sam 1,390
NUM dow_dim 0,657
NUM sam_dim 2,1
NUM cal_min 0,984
NUM cal_max 1,019
NUM cal_ecart 3,5
figure : ch05-jours-semaine.png
```

![Indice du jour de semaine du chiffre d'affaires quotidien : le samedi est le jour fort, le dimanche le jour faible.](figures/ch05-jours-semaine.png)

Le samedi vend 1,390 fois un jour moyen, le dimanche 0,657 : le samedi vend **2,1 fois plus** que le dimanche. Ce motif hebdomadaire est de loin le plus fort de la série ; il est aussi la raison pour laquelle on ne compare jamais « hier » à « avant-hier ».

Au mois, le calendrier agit de façon plus discrète : un mois qui compte cinq samedis au lieu de quatre est mécaniquement un peu plus fort. En pondérant chaque jour par son indice, on obtient un **facteur de calendrier mensuel**. Sur nos 36 mois, il varie de 0,984 à 1,019, soit un écart de **3,5 %** entre le mois le mieux et le moins bien doté. L'effet est modeste, mais il suffit à produire des variations de quelques points d'un mois sur l'autre. Pour une analyse fine, on **corrige** le mois en le divisant par ce facteur ; pour une analyse grossière, on se contente de savoir qu'il existe et de comparer des **mois entiers** à des mois entiers.

> 🧭 **En pratique.** Pour les boutiques ouvertes tous les jours, les « jours ouvrés » ne comptent pas ; pour une entreprise fermée le week-end, on comparerait des **mois à nombre égal de jours ouvrés**. Les jours fériés mobiles (Pâques) et les vacances scolaires sont d'autres effets de calendrier du même type : on les traite avec des variables indicatrices (5.3.1).

### 5.1.8 Ruptures et incidents

Une série réelle n'est pas une jolie courbe : elle contient des **ruptures** (un changement durable de niveau) et des **incidents** (un jour exceptionnel). Les deux faussent une décomposition ; on les traite **avant**.

#### Une rupture : le prix catalogue de 2025

Si les ventes passent d'un niveau à un autre le 1er janvier, on cherche **ce qui a changé ce jour-là**. Ici, c'est le prix : comparons le prix catalogue de chaque produit en 2025 et en 2024.

```python hide
lig = O.lire("lignes_commande.csv"); cmd = O.lire("commandes.csv")
x = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande"); x["an"] = x["date_commande"].str[:4]
pp = x.groupby(["id_produit", "an"])["prix_unitaire"].mean().unstack()
rap = (pp["2025"] / pp["2024"]).dropna()
NUM("rap_prix_med", fr(rap.median(), 3)); NUM("rap_prix_min", fr(rap.min(), 3)); NUM("rap_prix_max", fr(rap.max(), 3)); NUM("n_prod_prix", len(rap))
p24, p25 = x[x.an == "2024"]["prix_unitaire"].mean(), x[x.an == "2025"]["prix_unitaire"].mean()
NUM("prix_moy24", fr(p24, 2)); NUM("prix_moy25", fr(p25, 2)); NUM("prix_evo", fr((p25 / p24 - 1) * 100))
```
<!--sortie-->
```text
NUM rap_prix_med 1,030
NUM rap_prix_min 1,030
NUM rap_prix_max 1,031
NUM n_prod_prix 120
NUM prix_moy24 36,51
NUM prix_moy25 37,85
NUM prix_evo 3,7
```

Pour les 120 produits vendus les deux années, le rapport du prix de 2025 à celui de 2024 est de **1,030** pour la médiane (minimum 1,030, maximum 1,031) : une **hausse uniforme de 3 %**. Le prix moyen par ligne montre +3,7 % (de 36,51 € à 37,85 €) parce que le mélange des produits vendus change aussi ; comparer produit à produit isole l'effet prix. Conséquence pour l'analyse : une partie de la progression de 2025 n'est **pas** de la demande. On la sépare en **modélisant la rupture** (comme en 5.1.6) ou en exprimant la série en volumes (quantités) plutôt qu'en euros.

#### Des incidents : trouver ce qui sort du bruit

La variante `jours_incidents.csv` contient, sans que le fichier le dise, des jours anormaux. On les cherche en deux temps. D'abord, les **contrôles exacts** : une journée présente deux fois se trouve avec un simple test de doublon sur la date.

```python
ji = O.jours(incidents=True)
print("dates en double :", ji.index[ji.index.duplicated()].strftime("%d/%m/%Y").tolist())
```
<!--sortie-->
```text
dates en double : ['20/10/2025']
```

Ensuite, les incidents **statistiques** : on ajuste un modèle simple du chiffre d'affaires du jour (jour de semaine, mois, promotion, tendance), robuste aux valeurs extrêmes, et l'on signale les jours dont le **résidu** est très grand. Pour comparer des écarts, on les ramène à un **score z robuste** : l'écart divisé par sa dispersion habituelle, mesurée par la **MAD** (écart absolu médian), qui ne se laisse pas gonfler par les incidents eux-mêmes.

```python
z = O.residus_robustes(ji)                       # score z robuste de chaque jour (modèle : semaine, mois, promotion, tendance)
signales = z[z.abs() > 3.5]
print(len(signales), "jours signalés :", {d.strftime("%d/%m/%y"): round(v, 1) for d, v in signales.items()})
```
<!--sortie-->
```text
8 jours signalés : {'12/02/23': 3.8, '26/06/23': -3.6, '19/08/24': -4.2, '02/02/25': -3.5, '13/03/25': -6.2, '14/03/25': -3.7, '28/04/25': -4.0, '09/09/25': 10.4}
```

```python hide
v = O.lire("verite_incidents.csv", parse_dates=["date"]); vrais = set(v["date"]); nb_v = len(v)
stat = vrais - {pd.Timestamp("2025-10-20")}
res_seuil = {}
for s in (3.5, 3.0):
    f = z[z.abs() > s]; fs = set(f.index)
    res_seuil[s] = (len(fs), len(fs & stat), len(fs - stat))
    NUM(f"sig_{str(s).replace('.', '')}", len(fs)); NUM(f"vrai_{str(s).replace('.', '')}", len(fs & stat)); NUM(f"faux_{str(s).replace('.', '')}", len(fs - stat))
NUM("nb_v", nb_v); NUM("nb_stat", len(stat)); NUM("mad_pct", fr((np.exp(z.attrs["mad"]) - 1) * 100, 0))
FG.incidents(z, sorted(vrais))
j_ok = O.jours()["chiffre_affaires"]; ji1 = ji[~ji.index.duplicated()]["chiffre_affaires"]
NUM("sep_err", fr(ji1["2025-09"].sum(), 0)); NUM("sep_ok", fr(j_ok["2025-09"].sum(), 0)); NUM("sep_ratio", fr(ji1["2025-09"].sum() / j_ok["2025-09"].sum(), 2))
```
<!--sortie-->
```text
NUM sig_35 8
NUM vrai_35 4
NUM faux_35 4
NUM sig_30 18
NUM vrai_30 7
NUM faux_30 11
NUM nb_v 8
NUM nb_stat 7
NUM mad_pct 24
figure : ch05-incidents.png
NUM sep_err 141 337
NUM sep_ok 113 453
NUM sep_ratio 1,25
```

![Score z robuste de chaque jour. Les points orange sont signalés au seuil de 3,5 ; les cercles rouges sont les incidents réellement injectés.](figures/ch05-incidents.png)

Au seuil 3,5, 8 jours sont signalés, dont 4 sont de vrais incidents statistiques et 4 de fausses alertes ; en abaissant le seuil à 3, 18 jours sont signalés, dont 7 vrais incidents et 11 fausses alertes. **Ouvrons la vérité programmée** : elle contient 8 incidents (une panne du site de trois jours, une grosse commande professionnelle de 4 200 €, une erreur de saisie qui multiplie par dix le chiffre d'affaires d'un jour, deux jours de fermeture exceptionnelle de la boutique, et la journée en double). Le doublon est trouvé par le contrôle exact ; parmi les 7 incidents statistiques, la règle en retrouve **4** au seuil 3,5 et **7** au seuil 3, au prix de fausses alertes.

La leçon est celle de tout détecteur : **on ne peut détecter que ce qui sort du bruit**. Le chiffre d'affaires d'un jour fluctue d'environ ±24 % sans incident (c'est la dispersion de référence du modèle, la MAD) ; une panne qui retire 55 % des ventes d'un jour ne dépasse pas toujours ce niveau. Les incidents très marqués (l'erreur ×10) sont trouvés par tous les seuils ; les incidents modestes ne se distinguent du hasard qu'au prix de fausses alertes. Le seuil se choisit selon le **coût** d'une erreur : laisser passer un incident, ou vérifier à tort une journée normale.

Que faire d'un incident, une fois trouvé ? Trois traitements, du plus au moins prudent.

- **Le signaler** et garder la valeur (un incident réel fait partie de l'histoire : une vraie panne a bien coûté des ventes).
- **La corriger** quand c'est une **erreur de saisie** : remplacer la valeur par sa valeur attendue ou par la bonne valeur retrouvée à la source. L'erreur de septembre fait passer le mois de 113 453 € à 141 337 €, soit **1,25 fois** la bonne valeur : laissée telle quelle, elle fausserait la tendance et la prévision de la fin d'année.
- **L'exclure** de l'ajustement d'un modèle tout en la gardant dans les données, quand elle n'est pas représentative de l'avenir (une commande exceptionnelle).

> ⚠️ **Piège.** Supprimer silencieusement les jours qui « dérangent » est le meilleur moyen d'obtenir des prévisions trop belles. Chaque traitement se **documente** (chapitre 4 du volume II) : quelle date, quelle règle, quel effet sur le total.

### 5.1.9 Cinq pièges classiques

1. **Comparer des mois consécutifs sur une série saisonnière** (5.1.3) : on mesure la saison, pas la tendance.
2. **Faire la moyenne de pourcentages.** La croissance du chiffre d'affaires de 2025 sur 2024 est de **11,4 %** pour l'ensemble ; par canal, elle est de 0,5 % pour la Boutique, 13,4 % pour les Réseaux et 22,9 % pour le Site. La moyenne simple de ces trois pourcentages donne 12,3 %, ce qui **n'est pas** le taux de l'ensemble : les canaux ont des poids différents. On somme les montants, puis on calcule le pourcentage.
3. **Oublier les bords de la série.** Une moyenne mobile centrée sur douze mois perd six mois au début et six à la fin : sur 36 mois, la tendance n'en couvre que 24. Une décomposition qui « invente » la tendance aux extrémités se trompe justement là où l'on veut prévoir.
4. **Conclure avec trop peu de cycles.** Trois années ne donnent que trois observations par mois pour estimer chaque indice saisonnier : un mois exceptionnel pèse beaucoup. Il faut le dire dans les intervalles (5.1.6) et ne pas sur-interpréter.
5. **Lisser avant de tester ou de prévoir.** Une moyenne mobile crée une **fausse régularité** : ses valeurs voisines partagent des données, donc elles sont très corrélées. Calculer un écart-type ou une corrélation sur une série lissée donne une précision illusoire. On lisse pour **regarder**, pas pour estimer.

```python hide
lg2 = lig.merge(cmd[["id_commande", "date_commande", "canal"]], on="id_commande"); lg2["an"] = lg2["date_commande"].str[:4]
ca_c = lg2.pivot_table(index="canal", columns="an", values="montant", aggfunc="sum")
gc = (ca_c["2025"] / ca_c["2024"] - 1) * 100
NUM("g_boutique", fr(gc["Boutique"])); NUM("g_reseaux", fr(gc["Réseaux"])); NUM("g_site", fr(gc["Site"])); NUM("g_moy", fr(gc.mean()))
NUM("g_tot", fr((ca_c["2025"].sum() / ca_c["2024"].sum() - 1) * 100))
```
<!--sortie-->
```text
NUM g_boutique 0,5
NUM g_reseaux 13,4
NUM g_site 22,9
NUM g_moy 12,3
NUM g_tot 11,4
```

> ✅ **À retenir.**
> - Une série temporelle se décompose en **tendance, saison et résidu** ; le modèle est **multiplicatif** quand l'amplitude de la saison grandit avec le niveau.
> - On compare à la **même période de l'an dernier** (variation annuelle) ou, pour lisser le bruit, au **glissement annuel** sur douze mois ; jamais deux mois consécutifs sur une série saisonnière.
> - Un **indice saisonnier** est le rapport moyen à la tendance, normalisé pour valoir 1 en moyenne ; **désaisonnaliser**, c'est diviser par lui.
> - La tendance se mesure par la pente d'une droite sur le **logarithme** de la série désaisonnalisée, avec des erreurs **robustes à l'autocorrélation**, et se lit avec son intervalle.
> - Le **calendrier** (jours de la semaine, longueur des mois) est un effet fort à court terme ; **ruptures** et **incidents** se traitent avant de décomposer, et le traitement se documente.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.4 et exercices 5.1 à 5.6.
