# Chapitre 5 : Séries temporelles et analyse de tendance — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 5 du livre. Les **applications** sont de petites études guidées sur le chiffre d'affaires de la boutique (la série quotidienne de 2023 à 2025, ses incidents, ses canaux) ; vous les refaites pas à pas, puis vous répondez aux questions « À vous ». Les **exercices** sont notés ⭐ (direct), ⭐⭐ (demande de la réflexion), ⭐⭐⭐ (étude plus longue). Les **corrigés** donnent le calcul à la main quand il existe, puis le code. Les données sont **simulées** et leur vérité est programmée (voir le livre).

Une première cellule charge les bibliothèques et les données ; les cellules suivantes reprennent les noms ainsi définis.

```python
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
import outils_ch05 as O

j, m = O.charger()                                      # j : chiffre d'affaires TTC quotidien (et commandes) ; m : chiffre d'affaires mensuel
y = j["chiffre_affaires"]
lig, cmd = O.lire("lignes_commande.csv"), O.lire("commandes.csv")
print(len(j), "jours,", len(m), "mois | CA 2025 :", round(y["2025"].sum()), "€")
```
<!--sortie-->
```text
1096 jours, 36 mois | CA 2025 : 1324764 €
```


## Applications

### Application 5.1 — Composantes et comparaison à l'an dernier (sections 5.1.1 à 5.1.3)

**Objectif.** Comparer le chiffre d'affaires de 2025 à celui de 2024 de trois façons, et voir pourquoi deux d'entre elles trompent.

**Étape 1 — Mois sur mois et variation annuelle.** On calcule, pour chaque mois de 2025, la variation par rapport au mois précédent et par rapport au même mois de 2024.

```python
mom = (m.pct_change() * 100)["2025"]                       # mois sur mois
yoy = (m["2025"].values / m["2024"].values - 1) * 100     # même mois, an dernier
print("mois sur mois : de", round(mom.min(), 1), "à", round(mom.max(), 1), "% | variation annuelle : de", round(yoy.min(), 1), "à", round(yoy.max(), 1), "%")
```
<!--sortie-->
```text
mois sur mois : de -43.3 à 27.8 % | variation annuelle : de -1.2 à 18.5 %
```

**Étape 2 — Le glissement annuel.** On somme les douze derniers mois et on compare à la somme des douze mois précédents.

```python
r12 = m.rolling(12).sum()
gliss = ((r12 / r12.shift(12) - 1) * 100).dropna()
print(gliss.iloc[[0, 6, 11]].round(1).to_string())
```
<!--sortie-->
```text
date
2024-12-01    4.4
2025-06-01    5.0
2025-11-01    9.2
```


**Lecture.** Le mois sur mois va de -43,3 % à 27,8 % : il mesure surtout la saison. La variation annuelle va de -1,2 % à 18,5 % : la saison est écartée, mais le bruit mensuel reste. Le glissement annuel, lui, est lisible et montre l'accélération : 4,4 %, 5,0 % puis 9,2 % aux dates 12/2024, 06/2025 et 11/2025.

**À vous.** Refaites l'étape 2 pour le seul canal Site (chiffre d'affaires mensuel : `O.ca_par_canal()["Site"]`). Le glissement annuel du Site à fin 2025 est-il supérieur ou inférieur à celui de l'ensemble ? De combien ?

### Application 5.2 — Indices saisonniers et décomposition (sections 5.1.4 et 5.1.5)

**Objectif.** Calculer à la main les indices saisonniers trimestriels, puis les comparer à ceux de `seasonal_decompose`.

**Étape 1 — La moyenne mobile centrée sur quatre trimestres.** Pour des trimestres, la moyenne centrée prend 0,5 fois les extrêmes, 1 fois les trois du milieu, le tout divisé par 4.

```python
q = m.resample("QS").sum()
ma = (0.5 * q.shift(2) + q.shift(1) + q + q.shift(-1) + 0.5 * q.shift(-2)) / 4
rap = (q / ma).dropna()
print(rap.round(3).to_string())
```
<!--sortie-->
```text
date
2023-07-01    0.930
2023-10-01    1.312
2024-01-01    0.769
2024-04-01    1.001
2024-07-01    0.920
2024-10-01    1.279
2025-01-01    0.806
2025-04-01    0.959
Freq: QS-JAN
```

**Étape 2 — Moyenner par trimestre et normaliser.**

```python
par_t = rap.groupby(rap.index.quarter).mean()
iq = par_t / par_t.mean()
print(iq.round(3).to_dict(), "| moyenne :", round(iq.mean(), 3))
```
<!--sortie-->
```text
{1: 0.79, 2: 0.983, 3: 0.928, 4: 1.299} | moyenne : 1.0
```

**Étape 3 — Comparer à `seasonal_decompose` sur les mois.** On regroupe ensuite les indices mensuels par trimestre.

```python
from statsmodels.tsa.seasonal import seasonal_decompose
dm = seasonal_decompose(m, model="multiplicative", period=12)
idx_m = dm.seasonal.iloc[:12]; idx_m.index = range(1, 13)
print({t: round(idx_m[[3 * t - 2, 3 * t - 1, 3 * t]].mean(), 3) for t in range(1, 5)})
```
<!--sortie-->
```text
{1: np.float64(0.789), 2: np.float64(0.984), 3: np.float64(0.926), 4: np.float64(1.3)}
```


**Lecture.** Huit rapports (8) donnent les indices trimestriels 0,790, 0,983, 0,928 et 1,299 ; en regroupant les indices mensuels de `seasonal_decompose` par trimestre, on trouve 0,789, 0,984, 0,926 et 1,300 : les deux calculs racontent la même saison, à la différence près que les mois d'un même trimestre ont des indices différents (regrouper les mois perd du détail).

**À vous.** Ajoutez l'indice du mois de décembre à l'étape 3. Quel trimestre « perd » le plus de détail quand on regroupe les mois ?

### Application 5.3 — Calendrier et tendance (sections 5.1.6 et 5.1.7)

**Objectif.** Mesurer l'effet du jour de semaine, puis la tendance du chiffre d'affaires désaisonnalisé avec son intervalle.

**Étape 1 — Indice du jour de semaine.**

```python
dow = y.groupby(y.index.dayofweek).mean()
di = dow / dow.mean()
print(di.round(2).to_dict())                     # 0 = lundi ... 6 = dimanche
```
<!--sortie-->
```text
{0: 0.97, 1: 0.88, 2: 0.93, 3: 0.99, 4: 1.17, 5: 1.39, 6: 0.66}
```

**Étape 2 — Tendance avec erreurs robustes.** On désaisonnalise par les indices mensuels, puis on ajuste une droite sur le logarithme.

```python
idx = O.indices_saisonniers(m)
des = m / idx.reindex(m.index.month).values
t = np.arange(len(m)) / 12
reg = sm.OLS(np.log(des.values), sm.add_constant(t)).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
print(round((np.exp(reg.params[1]) - 1) * 100, 1), "% par an ; intervalle :", np.round((np.exp(reg.conf_int()[1]) - 1) * 100, 1))
```
<!--sortie-->
```text
8.2 % par an ; intervalle : [ 6.4 10. ]
```

**Étape 3 — La même régression, sans correction de l'autocorrélation.** On compare la largeur des intervalles.

```python
reg0 = sm.OLS(np.log(des.values), sm.add_constant(t)).fit()
print("largeur de l'intervalle : ordinaire", round(float(np.diff(reg0.conf_int()[1])[0]) * 100, 1), "| robuste", round(float(np.diff(reg.conf_int()[1])[0]) * 100, 1), "points de log %")
```
<!--sortie-->
```text
largeur de l'intervalle : ordinaire 3.1 | robuste 3.3 points de log %
```


**Lecture.** Le samedi pèse 1,39, le vendredi 1,17 et le dimanche 0,66 fois un jour moyen. La tendance est de 8,2 % par an (6,4 % à 10,0 %). L'intervalle de la régression ordinaire est large de 3,1 points, celui de la régression robuste de 3,3 : la correction de l'autocorrélation élargit l'intervalle, ce qui est honnête.

**À vous.** Refaites l'étape 2 sur le nombre de commandes mensuel plutôt que sur le chiffre d'affaires. La croissance est-elle plus proche de la vérité programmée (6 % par an) ? Pourquoi ?

### Application 5.4 — Trouver les incidents (section 5.1.8)

**Objectif.** Détecter des jours anormaux, puis juger la détection avec la vérité programmée.

**Étape 1 — Les doublons exacts.**

```python
ji = O.jours(incidents=True)
print("dates en double :", ji.index[ji.index.duplicated()].strftime("%d/%m/%Y").tolist())
```
<!--sortie-->
```text
dates en double : ['20/10/2025']
```

**Étape 2 — Le score z robuste, à plusieurs seuils.** On compare les jours signalés aux incidents réels (la vérité n'est ouverte qu'ici).

```python
z = O.residus_robustes(ji)
v = O.lire("verite_incidents.csv", parse_dates=["date"])
stat = set(v["date"]) - {pd.Timestamp("2025-10-20")}                 # le doublon est trouvé à l'étape 1
for s in (3, 3.5, 4):
    f = set(z[z.abs() > s].index)
    print(f"seuil {s} : {len(f)} signalés | vrais {len(f & stat)} | fausses alertes {len(f - stat)}")
```
<!--sortie-->
```text
seuil 3 : 18 signalés | vrais 7 | fausses alertes 11
seuil 3.5 : 8 signalés | vrais 4 | fausses alertes 4
seuil 4 : 3 signalés | vrais 2 | fausses alertes 1
```

**Étape 3 — Corriger l'erreur de saisie.** On remplace le jour le plus extrême par sa valeur attendue (la médiane des mêmes jours de semaine voisins) et l'on regarde l'effet sur le mois.

```python
jour = z.abs().idxmax()
yi = ji[~ji.index.duplicated()]["chiffre_affaires"].asfreq("D")
voisins = yi[[jour + pd.Timedelta(days=7 * k) for k in (-4, -3, -2, -1, 1, 2, 3, 4)]]
yc = yi.copy(); yc[jour] = voisins.median()
print(jour.date(), "| valeur saisie :", round(yi[jour]), "€ | valeur corrigée :", round(yc[jour]), "€ | CA du mois : avant", round(yi[jour.strftime("%Y-%m")].sum()), "après", round(yc[jour.strftime("%Y-%m")].sum()))
```
<!--sortie-->
```text
2025-09-09 | valeur saisie : 30983 € | valeur corrigée : 2773 € | CA du mois : avant 141337 après 113127
```


**Lecture.** Aux seuils 3, 3,5 et 4, on signale 18, 8 et 3 jours, dont 7, 4 et 2 vrais incidents (sur 7) : un seuil plus bas trouve plus d'incidents mais lève 11 fausses alertes au lieu de 1. Le jour le plus extrême est le 09/09/2025 (saisi 30 983 €, corrigé 2 773 €) : la correction ramène le mois de 141 337 € à 113 127 €.

**À vous.** Quelle valeur du seuil choisiriez-vous si une fausse alerte coûte 10 minutes de vérification et un incident manqué 2 heures ? Justifiez avec le tableau ci-dessus.

### Application 5.5 — Moyennes mobiles et retard (section 5.2.1)

**Objectif.** Vérifier numériquement qu'une moyenne mobile arrière retarde de $(w-1)/2$ jours, et mesurer l'effet du lissage.

**Étape 1 — La moyenne arrière et la moyenne centrée.**

```python
d = y["2025-09-01":]
arriere = d.rolling(7).mean()
centree = d.rolling(7, center=True).mean()
dec = arriere.shift(-3).dropna()
print("moyenne arrière = moyenne centrée décalée de 3 jours :", np.allclose(dec, centree.loc[dec.index]))
```
<!--sortie-->
```text
moyenne arrière = moyenne centrée décalée de 3 jours : True
```

**Étape 2 — La fenêtre et la variabilité.** On compare l'écart-type du chiffre d'affaires lissé selon la fenêtre.

```python
print({w: round(d.rolling(w).mean().std()) for w in (1, 7, 14, 28)})
```
<!--sortie-->
```text
{1: 1570, 7: 978, 14: 924, 28: 844}
```

**Étape 3 — La moyenne exponentielle.** On regarde l'âge moyen des données pour plusieurs α.

```python
for a in (0.05, 0.15, 0.5):
    print("α =", a, "| âge moyen :", round((1 - a) / a, 1), "jours | écart-type :", round(d.ewm(alpha=a).mean().std()))
```
<!--sortie-->
```text
α = 0.05 | âge moyen : 19.0 jours | écart-type : 719
α = 0.15 | âge moyen : 5.7 jours | écart-type : 930
α = 0.5 | âge moyen : 1.0 jours | écart-type : 1144
```


**Lecture.** L'égalité est vérifiée (oui) : la moyenne arrière d'aujourd'hui est la moyenne centrée de **trois jours plus tôt**. Plus la fenêtre est longue, plus l'écart-type baisse : 1 570 € au jour, 978 € sur 7 jours, 924 € sur 14 jours, 844 € sur 28 jours ; la contrepartie est le retard.

**À vous.** Quelle fenêtre choisiriez-vous pour surveiller en temps réel le chiffre d'affaires d'une boutique ouverte tous les jours ? Pour détecter un début de promotion en moins de trois jours ?

### Application 5.6 — Prévoir 2025 avec 2023-2024 (sections 5.2.2 et 5.2.3)

**Objectif.** Comparer six méthodes sur les douze mois de 2025 et mesurer l'effet d'une fuite d'information.

**Étape 1 — Les six méthodes et leurs erreurs.**

```python
F, train, test = O.previsions_mensuelles(m)
tab = O.tableau_erreurs(F, train, test)
print(tab[["MAE", "MAPE %", "biais %"]].round(1).to_string())
```
<!--sortie-->
```text
                                    MAE  MAPE %  biais %
méthode                                                 
naïve (dernier mois)            51330.5    52.8     42.5
naïve saisonnière               11487.8    10.2    -10.2
naïve saisonnière × croissance   8148.3     7.2     -6.2
moyenne des 12 derniers mois    20528.8    16.7    -10.2
tendance linéaire × indices      7792.3     7.0     -6.2
Holt-Winters                     8019.8     7.1     -6.3
```

**Étape 2 — La même méthode, avec fuite.** On calcule les indices saisonniers sur les 36 mois au lieu de 24.

```python
idx_tout = O.indices_saisonniers(m)
b = np.polyfit(np.arange(24), (train / O.indices_saisonniers(train).reindex(train.index.month).values).values, 1)
f_triche = np.polyval(b, np.arange(24, 36)) * idx_tout.reindex(test.index.month).values
print("MAPE honnête :", round(tab.loc["tendance linéaire × indices", "MAPE %"], 1), "| avec fuite :", round(O.mape(test, f_triche), 1))
```
<!--sortie-->
```text
MAPE honnête : 7.0 | avec fuite : 6.0
```

**Étape 3 — Un intervalle de prévision.** On prend le rapport réalisé/prévu des douze mois pour la méthode « tendance × indices » et l'on regarde sa dispersion.

```python
r = (test.values / F["tendance linéaire × indices"])
print("rapport réalisé/prévu : de", round(r.min(), 2), "à", round(r.max(), 2), "| moyenne", round(r.mean(), 2))
```
<!--sortie-->
```text
rapport réalisé/prévu : de 0.95 à 1.14 | moyenne 1.07
```


**Lecture.** Les erreurs mensuelles (MAPE) sont de 10,2 % pour la naïve saisonnière, 7,2 % avec la croissance, 7,0 % pour tendance × indices et 7,1 % pour Holt-Winters ; le biais commun est de -6,2 %. La fuite ramène l'erreur de tendance × indices à 6,0 %. Le rapport réalisé/prévu va de 0,95 à 1,14 (moyenne 1,07) : l'intervalle qu'on en tirerait serait **décentré** (le réalisé est presque toujours au-dessus du prévu), signe d'un biais.

**À vous.** Ajoutez à la liste une méthode « moyenne des deux dernières années, mois par mois » et comparez son MAPE aux autres.

### Application 5.7 — Plusieurs origines et intervalle (sections 5.2.4 et 5.2.5)

**Objectif.** Comparer deux méthodes quotidiennes à 48 origines, puis calibrer et vérifier un intervalle.

**Étape 1 — Les 48 origines.**

```python
mae_o, tot_o = O.origines(y)
print(pd.DataFrame({"MAE par jour": mae_o.mean(), "erreur absolue 28 j (%)": tot_o.abs().mean()}).round(1).to_string())
```
<!--sortie-->
```text
                            MAE par jour  erreur absolue 28 j (%)
naïve saisonnière 7 j              891.5                     10.4
moyenne des 4 mêmes jours          802.3                     11.7
même jour l'an dernier             872.0                      9.8
an dernier × niveau récent         897.1                      7.2
Holt-Winters (7 j)                 717.6                     10.9
```

**Étape 2 — Une différence appariée avec son incertitude.** Pour comparer « an dernier × niveau » et Holt-Winters, on prend la différence des erreurs **absolues** à chaque origine, puis on estime l'incertitude par un bootstrap **par blocs** de 4 origines consécutives (les origines voisines se chevauchent).

```python
dif = (tot_o["Holt-Winters (7 j)"].abs() - tot_o["an dernier × niveau récent"].abs()).values
rng = np.random.default_rng(0)
blocs = [dif[i:i + 4] for i in range(0, len(dif), 4)]
boot = [np.concatenate([blocs[k] for k in rng.integers(0, len(blocs), len(blocs))]).mean() for _ in range(3000)]
print("différence moyenne :", round(dif.mean(), 1), "points ; intervalle à 95 % :", np.round(np.percentile(boot, [2.5, 97.5]), 1))
```
<!--sortie-->
```text
différence moyenne : 3.7 points ; intervalle à 95 % : [0.9 6.7]
```

**Étape 3 — La couverture d'un intervalle à 80 %.**

```python
r = 1 / (1 + tot_o["an dernier × niveau récent"] / 100)
bas, haut = r.iloc[:24].quantile([0.10, 0.90])
print("intervalle", round(bas, 2), "à", round(haut, 2), "| couverture sur la seconde moitié :", round(r.iloc[24:].between(bas, haut).mean() * 100), "%")
```
<!--sortie-->
```text
intervalle 0.89 à 1.1 | couverture sur la seconde moitié : 79 %
```


**Lecture.** « An dernier × niveau » a une MAE quotidienne de 897 € et Holt-Winters de 718 € ; sur les totaux de 28 jours, c'est l'inverse (7,2 % contre 10,9 %). La différence moyenne d'erreur (Holt-Winters moins l'autre) est de 3,7 points, avec un intervalle de 0,9 à 6,7 : **zéro n'est pas dans l'intervalle**, la méthode saisonnière est donc réellement meilleure sur les totaux. L'intervalle à 80 % (0,89 à 1,10 fois la prévision) a une couverture de 79 % sur la seconde moitié.

**À vous.** Refaites l'étape 2 en comparant la naïve saisonnière de 7 jours à « la moyenne des 4 mêmes jours ». La différence est-elle significative ?

### Application 5.8 — Régression avec indicatrices (section 5.3.1)

**Objectif.** Estimer l'effet de la promotion, de la publicité et de la tendance sur les commandes, puis comparer à la vérité programmée.

**Étape 1 — Préparer les variables.**

```python
dj = j.reset_index().assign(mois=lambda x: x["date"].dt.month, jds=lambda x: x["date"].dt.dayofweek, t=lambda x: (x["date"] - x["date"].min()).dt.days / 365.25)
dj["pub7"] = dj["depense_pub"].rolling(7, min_periods=1).sum() / 1000
tr5, te5 = dj[dj["date"] < "2025-01-01"], dj[dj["date"] >= "2025-01-01"]
```

**Étape 2 — Ajuster et lire les effets.**

```python
mod = smf.ols("np.log(nb_commandes) ~ C(mois) + C(jds) + promo_active + pub7 + t", tr5).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
ic = (np.exp(mod.conf_int()) - 1) * 100
for c in ("promo_active", "pub7", "t"):
    print(c, round((np.exp(mod.params[c]) - 1) * 100, 1), "% ; intervalle", np.round(ic.loc[c].values, 1))
```
<!--sortie-->
```text
promo_active 21.7 % ; intervalle [14.8 29. ]
pub7 -0.8 % ; intervalle [-6.4  5.2]
t 4.7 % ; intervalle [2.2 7.3]
```

**Étape 3 — Prévoir 2025 et mesurer l'erreur.**

```python
pred = np.exp(mod.predict(te5)) * np.exp(mod.mse_resid / 2)
mens = pd.DataFrame({"réel": te5.set_index("date")["nb_commandes"], "prévu": pred.values}).resample("MS").sum()
print("MAPE mensuelle :", round(O.mape(mens["réel"], mens["prévu"]), 1), "% ; MAE par jour :", round(O.mae(te5["nb_commandes"], pred), 1), "commandes")
```
<!--sortie-->
```text
MAPE mensuelle : 4.4 % ; MAE par jour : 4.3 commandes
```


**Lecture.** La promotion augmente les commandes de 21,7 % (14,8 à 29,0 %), la vérité étant de +18 % : retrouvée. La publicité donne -0,8 % (-6,4 à 5,2 %) par millier d'euros sur 7 jours : indiscernable de zéro, alors que l'effet programmé est de +1,5 %. La tendance est de 4,7 % par an pour 6 % programmés. L'erreur de prévision de 2025 est de 4,4 % par mois et de 4,3 commandes par jour.

**À vous.** Ajoutez la température comme variable explicative. Son effet est-il significatif ? Retrouve-t-on l'idée que la température agit sur le **mélange** des produits, pas sur le nombre de commandes ?

### Application 5.9 — Décembre prochain et planification (sections 5.3.5 et 5.3.6)

**Objectif.** Construire trois scénarios pour décembre 2026, puis en déduire un besoin en personnel et en stock.

**Étape 1 — Trois scénarios de croissance.**

```python
dec25 = m["2025-12-01"]
scen = {"prudent": dec25 * 1.044, "central": dec25 * 1.065, "hausse de prix": dec25 * 1.065 * 1.03}
print({k: round(v) for k, v in scen.items()})
```
<!--sortie-->
```text
{'prudent': 191934, 'central': 195795, 'hausse de prix': 201669}
```

**Étape 2 — Du chiffre d'affaires aux commandes et au personnel.** Avec un panier moyen de 100 € et 20 commandes préparées par personne et par jour (hypothèse illustrative), on dimensionne la journée de pointe.

```python
dow = y.groupby(y.index.dayofweek).mean(); di = dow / dow.mean()
for k, v in scen.items():
    cmd_j = v / 100 / 31
    print(f"{k:15s} commandes/jour : {cmd_j:5.1f} | samedi : {cmd_j * di[5]:5.1f} | personnes le samedi : {int(np.ceil(cmd_j * di[5] / 20))}")
```
<!--sortie-->
```text
prudent         commandes/jour :  61.9 | samedi :  86.0 | personnes le samedi : 5
central         commandes/jour :  63.2 | samedi :  87.8 | personnes le samedi : 5
hausse de prix  commandes/jour :  65.1 | samedi :  90.4 | personnes le samedi : 5
```

**Étape 3 — Le stock de sécurité d'un produit.** Pour le **deuxième** produit le plus vendu en novembre et décembre 2025, avec un délai de 14 jours et un niveau de service de 95 % ($z=1{,}65$) :

```python
x = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande"); x = x[x["date_commande"] >= "2025-11-01"]
p2 = x.groupby("id_produit")["quantite"].sum().sort_values(ascending=False).index[1]
dem = x[x["id_produit"] == p2].groupby("date_commande")["quantite"].sum().reindex(pd.date_range("2025-11-01", "2025-12-31").strftime("%Y-%m-%d"), fill_value=0)
ss = 1.65 * dem.std() * np.sqrt(14)
print("produit", p2, "| demande moyenne :", round(dem.mean(), 2), "par jour | stock de sécurité :", round(ss), "| stock au moment de commander :", round(dem.mean() * 14 + ss))
```
<!--sortie-->
```text
produit 42 | demande moyenne : 3.57 par jour | stock de sécurité : 16 | stock au moment de commander : 66
```


**Lecture.** Les trois scénarios donnent 191 934 €, 195 795 € et 201 669 € pour décembre 2026. Un samedi de pointe compte environ 86, 88 ou 90 commandes, soit 5, 5 et 5 personnes. Pour le produit 42 (demande moyenne de 3,57 par jour), le stock de sécurité est de 16 unités et le stock au moment de commander de 66.

**À vous.** Quel scénario retiendriez-vous pour le recrutement d'intérimaires ? Et pour la commande de stock ? Une même prévision ne sert pas forcément à deux décisions de la même façon : pourquoi ?

## Exercices

### Exercice 5.1 ⭐ — Le mois court (section 5.1.2)

Un mois de 28 jours a rapporté 70 000 € ; le mois précédent, de 31 jours, a rapporté 77 000 €. De combien le chiffre d'affaires **par jour** a-t-il varié ? Que dire de la baisse du chiffre d'affaires mensuel ?

### Exercice 5.2 ⭐ — Mois sur mois ou an sur an ? (section 5.1.3)

Les chiffres d'affaires mensuels de deux années sont, en k€ : année 1 : 60, 70, 100 ; année 2 : 66, 77, 108 (janvier, février, mars). Calculez la variation annuelle de chaque mois, puis la variation annuelle du trimestre, et la moyenne des trois variations mensuelles. Laquelle des deux dernières est la bonne, et pourquoi ?

### Exercice 5.3 ⭐⭐ — Indices saisonniers à la main (section 5.1.4)

Voici douze trimestres de ventes (en k€), sur trois ans : année 1 : 80, 100, 90, 130 ; année 2 : 88, 108, 99, 143 ; année 3 : 97, 119, 109, 157. Calculez à la main (puis vérifiez par le code) la moyenne mobile centrée sur quatre trimestres pour les trimestres où elle existe, les rapports, les indices trimestriels normalisés, et la série désaisonnalisée de l'année 3.

### Exercice 5.4 ⭐⭐ — Additif ou multiplicatif ? (section 5.1.5)

Pour le canal **Réseaux**, calculez le rapport et la différence entre décembre et février, pour 2023, 2024 et 2025. La saison du canal est-elle plutôt additive ou multiplicative ? Comparez à la conclusion du livre pour l'ensemble.

### Exercice 5.5 ⭐⭐ — La croissance des commandes (section 5.1.6)

Estimez la croissance annuelle du **nombre de commandes** mensuel (série désaisonnalisée, logarithme, erreurs robustes) et donnez son intervalle à 95 %. Contient-il la vérité programmée de 6 % ? Pourquoi l'estimation est-elle plus proche de 6 % que celle du chiffre d'affaires ?

### Exercice 5.6 ⭐⭐ — Choisir un seuil selon le coût (section 5.1.8)

Une fausse alerte coûte 1 unité (une vérification inutile) et un incident manqué en coûte 5. Parmi les seuils 3, 3,5 et 4 du score z robuste, lequel minimise le coût total sur les sept incidents statistiques de `jours_incidents.csv` ? Et si l'incident manqué ne coûte que 2 unités ?

### Exercice 5.7 ⭐ — Lissage exponentiel à la main (section 5.2.1)

Avec $\alpha=0{,}3$ et les valeurs 100, 120, 90, 110, calculez à la main les quatre valeurs lissées (avec $s_1=y_1$), puis vérifiez avec pandas. Quel est l'âge moyen des données ?

### Exercice 5.8 ⭐⭐ — MAE, RMSE, MAPE (section 5.2.3)

Le réalisé est $(200,\,150,\,100,\,50)$ et la prévision $(180,\,160,\,120,\,40)$. Calculez à la main la MAE, la RMSE et le MAPE. Pourquoi le MAPE est-il le plus sensible à la valeur 50 ? Que devient chaque mesure si l'on remplace 40 par 5 ?

### Exercice 5.9 ⭐⭐ — Prévoir le canal Site (section 5.2.2)

Pour le canal **Site**, prévoyez 2025 avec 2023-2024 par la naïve saisonnière, la naïve saisonnière × croissance et « tendance × indices », et comparez les MAPE. Quelle méthode se trompe le plus, et pourquoi (pensez à la croissance du canal) ?

### Exercice 5.10 ⭐⭐⭐ — Comparer deux méthodes avec leur incertitude (sections 5.2.4 et 5.2.5)

À 24 origines (une toutes les deux semaines en 2025), comparez la naïve saisonnière de 7 jours et « la moyenne des 4 mêmes jours » sur le total de 28 jours. Donnez la différence moyenne d'erreur absolue et son intervalle de bootstrap par blocs. Peut-on dire laquelle est meilleure ?

### Exercice 5.11 ⭐⭐ — L'effet de la pluie (section 5.3.1)

Ajoutez la pluie (`pluie_mm > 1`, indicatrice) à la régression de 5.3.1, séparément pour le nombre de commandes **total**. Son effet est-il significatif ? La vérité programmée est −8 % pour la Boutique et +5 % pour le Site : que devriez-vous attendre sur le total, et pourquoi l'analyse a-t-elle du mal à le voir ?

### Exercice 5.12 ⭐⭐⭐ — Prévoir par canal et planifier (sections 5.3.3 à 5.3.6)

Prévoyez décembre 2026 pour chaque canal par « tendance × indices » ajustée sur les 36 mois, additionnez, et comparez à la prévision directe du total et aux trois scénarios de l'application 5.9. Quel canal pèse le plus dans la croissance prévue ? Commentez en trois phrases ce que vous diriez à la gérante.

## Corrigés

### Corrigé 5.1

Par jour : $70\,000/28=2\,500$ € contre $77\,000/31\approx2\,484$ € : le chiffre d'affaires **par jour** est quasiment stable (+0,6 %), alors que le chiffre d'affaires mensuel baisse de $70/77-1\approx-9{,}1\ \%$. La « baisse » vient presque entièrement de la durée du mois.

```python
print(round(70000 / 28), round(77000 / 31), round((70000 / 28) / (77000 / 31) * 100 - 100, 1), round((70 / 77 - 1) * 100, 1))
```
<!--sortie-->
```text
2500 2484 0.6 -9.1
```

### Corrigé 5.2

Variations mensuelles : $66/60-1=10\ \%$, $77/70-1=10\ \%$, $108/100-1=8\ \%$. Trimestre : $(66+77+108)/(60+70+100)-1=251/230-1\approx9{,}1\ \%$. La moyenne des trois variations vaut $9{,}33\ \%$. La **bonne** réponse est la variation du trimestre (9,1 %) : on somme les montants avant de calculer le pourcentage ; la moyenne des pourcentages pèse de la même façon un petit mois et un grand mois.

```python
a1, a2 = np.array([60, 70, 100.]), np.array([66, 77, 108.])
print((a2 / a1 - 1).round(3), round(a2.sum() / a1.sum() - 1, 4), round((a2 / a1 - 1).mean(), 4))
```
<!--sortie-->
```text
[0.1  0.1  0.08] 0.0913 0.0933
```

### Corrigé 5.3

Moyennes centrées (0,5·y(t−2) + y(t−1) + y(t) + y(t+1) + 0,5·y(t+2), divisé par 4) pour les trimestres 3 à 10. Par exemple pour le trimestre 3 : $(0{,}5\times80+100+90+130+0{,}5\times88)/4=(40+100+90+130+44)/4=101{,}0$ ; rapport $90/101=0{,}891$. On fait de même pour les autres et l'on moyenne par position.

```python
s = pd.Series([80, 100, 90, 130, 88, 108, 99, 143, 97, 119, 109, 157.], index=pd.period_range("2001Q1", periods=12, freq="Q"))
ma = (0.5 * s.shift(2) + s.shift(1) + s + s.shift(-1) + 0.5 * s.shift(-2)) / 4
rap = (s / ma).dropna(); par = rap.groupby(rap.index.quarter).mean(); ind = par / par.mean()
print(ma.dropna().round(1).tolist()); print(rap.round(3).tolist()); print(ind.round(3).to_dict())
print("année 3 désaisonnalisée :", (s.iloc[8:].values / ind.reindex([1, 2, 3, 4]).values).round(1))
```
<!--sortie-->
```text
[101.0, 103.0, 105.1, 107.9, 110.6, 113.1, 115.8, 118.8]
[0.891, 1.262, 0.837, 1.001, 0.895, 1.264, 0.838, 1.002]
{1: 0.839, 2: 1.003, 3: 0.894, 4: 1.265}
année 3 désaisonnalisée : [115.7 118.7 121.9 124.2]
```


Le premier rapport est 0,891 (moyenne centrée 101,0). Les indices trimestriels valent 0,839, 1,003, 0,894 et 1,265 ; la série désaisonnalisée de l'année 3 est : 115,7 ; 118,7 ; 121,9 ; 124,2 k€. La série montre alors une progression régulière, sans le profil en dents de scie de la saison.

### Corrigé 5.4

```python
cc = O.ca_par_canal()["Réseaux"]
for an in (2023, 2024, 2025):
    print(an, "rapport déc/fév :", round(cc[f"{an}-12-01"] / cc[f"{an}-02-01"], 2), "| différence :", round(cc[f"{an}-12-01"] - cc[f"{an}-02-01"]))
```
<!--sortie-->
```text
2023 rapport déc/fév : 2.48 | différence : 10284
2024 rapport déc/fév : 2.18 | différence : 9075
2025 rapport déc/fév : 3.73 | différence : 14932
```


Rapports : 2,48, 2,18, 3,73 ; différences : 10 284 €, 9 075 €, 14 932 €. Sur un petit canal, le bruit mensuel est grand et ni le rapport ni la différence ne sont aussi stables que pour l'ensemble : la conclusion est **moins nette**. On garde le modèle multiplicatif par prudence (la saison s'applique à un niveau qui croît) mais on le dit : avec un seul mois de chaque type par an, on ne peut pas trancher sur un canal de cette taille.

### Corrigé 5.5

```python
cmm = j["nb_commandes"].resample("MS").sum()
ic_ = O.indices_saisonniers(cmm); dc = cmm / ic_.reindex(cmm.index.month).values
r_ = sm.OLS(np.log(dc.values), sm.add_constant(np.arange(36) / 12)).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
print(round((np.exp(r_.params[1]) - 1) * 100, 1), np.round((np.exp(r_.conf_int()[1]) - 1) * 100, 1))
```
<!--sortie-->
```text
6.9 [5.6 8.2]
```


La croissance des commandes est de 6,9 % par an (5,6 % à 8,2 %) : l'intervalle contient bien 6 %. L'estimation est plus proche de la vérité que celle du chiffre d'affaires (8,2 %, qui contient aussi la hausse de prix de 2025 et les remises) parce que le nombre de commandes **ne subit pas** les prix.

### Corrigé 5.6

```python
cout = {}
for s in (3, 3.5, 4):
    f = set(z[z.abs() > s].index); manque = len(stat - f); fausses = len(f - stat)
    cout[s] = (fausses * 1 + manque * 5, fausses * 1 + manque * 2, fausses, manque)
print(cout)
```
<!--sortie-->
```text
{3: (11, 11, 11, 0), 3.5: (19, 10, 4, 3), 4: (26, 11, 1, 5)}
```


Avec un coût de 5 par incident manqué, les coûts totaux sont 11 (seuil 3), 19 (3,5) et 26 (4) : le meilleur seuil est **3**. Avec un coût de 2, ils sont 11, 10 et 11 : le meilleur seuil est **3.5**. Plus l'incident manqué coûte cher par rapport à la fausse alerte, plus on baisse le seuil.

### Corrigé 5.7

$s_1=100$ ; $s_2=0{,}3\times120+0{,}7\times100=106$ ; $s_3=0{,}3\times90+0{,}7\times106=101{,}2$ ; $s_4=0{,}3\times110+0{,}7\times101{,}2=103{,}84$. Âge moyen : $(1-\alpha)/\alpha=0{,}7/0{,}3\approx2{,}3$ périodes.

```python
print(pd.Series([100, 120, 90, 110]).ewm(alpha=0.3, adjust=False).mean().round(2).tolist(), round(0.7 / 0.3, 1))
```
<!--sortie-->
```text
[100.0, 106.0, 101.2, 103.84] 2.3
```

### Corrigé 5.8

Erreurs absolues : 20, 10, 20, 10 → MAE $=60/4=15$. Carrés : 400, 100, 400, 100 → somme 1 000 → RMSE $=\sqrt{250}\approx15{,}8$. Erreurs relatives : $20/200=10\ \%$, $10/150\approx6{,}7\ \%$, $20/100=20\ \%$, $10/50=20\ \%$ → MAPE $\approx14{,}2\ \%$. La valeur 50 est la plus petite : une erreur de 10 y pèse 20 %, autant que 20 sur la valeur 100. En remplaçant 40 par 5, l'erreur de ce point passe à 45 (90 %).

```python
def mesures(r, p):
    r, p = np.array(r, float), np.array(p, float)
    return round(O.mae(r, p), 1), round(O.rmse(r, p), 1), round(O.mape(r, p), 1)
print(mesures([200, 150, 100, 50], [180, 160, 120, 40]), mesures([200, 150, 100, 50], [180, 160, 120, 5]))
```
<!--sortie-->
```text
(15.0, 15.8, 14.2) (23.8, 27.0, 31.7)
```


Avec 40, on trouve MAE 15,0, RMSE 15,8, MAPE 14,2 % ; avec 5, MAE 23,8, RMSE 27,0 et MAPE 31,7 % : la RMSE réagit plus que la MAE à la grosse erreur.

### Corrigé 5.9

```python
cs = O.ca_par_canal()["Site"]
tr_s, te_s = cs[:"2024-12-01"], cs["2025-01-01":]
sn = O.prevision_naive_saisonniere(tr_s, 12)
g = tr_s.iloc[-12:].sum() / tr_s.iloc[-24:-12].sum()
ti = O.prevision_tendance_indices(cs, "2024-12-01").values
print({"naïve saisonnière": round(O.mape(te_s, sn), 1), "× croissance": round(O.mape(te_s, sn * g), 1), "tendance × indices": round(O.mape(te_s, ti), 1)}, "| croissance passée :", round((g - 1) * 100, 1), "%")
```
<!--sortie-->
```text
{'naïve saisonnière': 19.0, '× croissance': 8.1, 'tendance × indices': 10.5} | croissance passée : 19.0 %
```


Erreurs : 19,0 % (naïve saisonnière), 8,1 % (avec croissance) et 10,5 % (tendance × indices). La croissance passée du Site (+19,0 %) est inférieure à celle de 2025 (+22,9 %) : toutes les méthodes sous-estiment, et la naïve saisonnière sans croissance, qui suppose un canal immobile, se trompe le plus. Ici, la méthode la plus simple qui ajoute la croissance passée (8,1 %) fait même mieux que la droite ajustée (10,5 %), parce que cette droite sous-estime une croissance déjà forte. Plus un canal change de rythme, plus la prévision simple se trompe.

### Corrigé 5.10

```python
H = 28; origs = pd.date_range("2025-01-07", "2025-12-02", freq="14D")
dif = []
for o in origs:
    fut = y[o + pd.Timedelta(days=1): o + pd.Timedelta(days=H)]
    if len(fut) < H:
        continue
    f, _ = O.previsions_28j(y, o, H)
    dif.append(abs(f["naïve saisonnière 7 j"].sum() / fut.sum() - 1) - abs(f["moyenne des 4 mêmes jours"].sum() / fut.sum() - 1))
dif = np.array(dif) * 100
rng = np.random.default_rng(1)
bl = [dif[i:i + 3] for i in range(0, len(dif), 3)]
boot = [np.concatenate([bl[k] for k in rng.integers(0, len(bl), len(bl))]).mean() for _ in range(3000)]
print(len(dif), round(dif.mean(), 2), np.round(np.percentile(boot, [2.5, 97.5]), 2))
```
<!--sortie-->
```text
24 -3.11 [-10.77   2.61]
```


Sur 24 origines, la différence moyenne d'erreur absolue (naïve de 7 jours moins moyenne des 4 mêmes jours) est de -3,11 points, avec un intervalle de -10,77 à 2,61 : **zéro est dans l'intervalle**. La naïve de 7 jours fait en moyenne un peu mieux, mais avec si peu d'origines et des fenêtres qui se chevauchent, on ne peut pas départager ces deux méthodes ; on garde la plus simple.

### Corrigé 5.11

```python
dj["pluie"] = (dj["pluie_mm"] > 1).astype(int)
tr5, te5 = dj[dj["date"] < "2025-01-01"], dj[dj["date"] >= "2025-01-01"]
mp = smf.ols("np.log(nb_commandes) ~ C(mois) + C(jds) + promo_active + pub7 + t + pluie", tr5).fit(cov_type="HAC", cov_kwds={"maxlags": 7})
icp = (np.exp(mp.conf_int().loc["pluie"]) - 1) * 100
print(round((np.exp(mp.params["pluie"]) - 1) * 100, 1), "% ; intervalle", np.round(icp.values, 1), "| p =", round(mp.pvalues["pluie"], 3))
```
<!--sortie-->
```text
-1.6 % ; intervalle [-4.3  1.2] | p = 0.257
```


L'effet estimé de la pluie sur le total est de -1,6 % (intervalle -4,3 % à 1,2 %, p = 0,26) : non significatif. Attendu : la Boutique vend environ la moitié des commandes et perd 8 %, le Site, environ 40 %, gagne 5 % : l'effet net est de l'ordre de −2 % (≈ 0,5×(−8) + 0,4×(+5)), **trop petit** pour émerger du bruit quotidien (±24 %). Pour voir l'effet, il faut séparer les canaux : l'effet a des signes opposés selon le canal, et leur somme s'annule presque.

### Corrigé 5.12

```python
cc = O.ca_par_canal()
f26 = {c: O.prevision_tendance_indices(cc[c], "2025-12-01")["2026-12-01"] for c in cc}
direct = O.prevision_tendance_indices(cc.sum(axis=1), "2025-12-01")["2026-12-01"]
print({c: round(v) for c, v in f26.items()}, "| somme :", round(sum(f26.values())), "| direct :", round(direct))
print("croissance prévue vs déc. 2025 par canal (%) :", {c: round((f26[c] / cc[c]["2025-12-01"] - 1) * 100, 1) for c in cc})
```
<!--sortie-->
```text
{'Boutique': 72118, 'Réseaux': 20939, 'Site': 96932} | somme : 189990 | direct : 190904
croissance prévue vs déc. 2025 par canal (%) : {'Boutique': np.float64(-1.7), 'Réseaux': np.float64(2.6), 'Site': np.float64(7.6)}
```


Les prévisions de décembre 2026 sont 72 118 € (Boutique), 20 939 € (Réseaux) et 96 932 € (Site), soit 189 990 € au total, contre 190 904 € par la prévision directe du total et 191 934 à 201 669 € pour les scénarios (application 5.9). Les croissances par canal par rapport à décembre 2025 sont de -1,7 % (Boutique), 2,6 % (Réseaux) et 7,6 % (Site) : le **Site** porte la croissance, la Boutique recule légèrement. À la gérante : « le chiffre d'affaires de décembre 2026 sera entre 190 000 € et 200 000 € environ, la fourchette dépendant surtout de la politique de prix ; le Site est le canal qui progresse, la Boutique stagne ou recule un peu ; prévoyez le stock et les équipes en conséquence plutôt que de répartir le total au prorata de l'an dernier. »
