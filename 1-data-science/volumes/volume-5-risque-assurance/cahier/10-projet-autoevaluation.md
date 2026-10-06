# Projet du volume et auto-évaluation — exercices et applications

> 🧭 Ce chapitre du cahier clôt le volume V. Il contient **le projet du volume** : construire le **tarif d'une assurance automobile** pour la mutuelle, du jeu de données au rapport, en **validant** chaque étape hors période et en écrivant les **notes réglementaires** qui accompagneraient le modèle ; une **variante** reprend la démarche pour un **score de crédit**. Il ne demande aucune notion nouvelle : chaque étape s'appuie sur un chapitre du livre. Puis vient l'**auto-évaluation** (quarante questions).

## Projet du volume

### P.1 Le cahier des charges

La mutuelle prépare son **tarif 2025** pour l'assurance automobile. La direction technique pose six exigences :

1. **Un tarif lisible** : une prime = une prime de base × quelques coefficients (âge, zone, usage…), que les conseillers peuvent expliquer.
2. **Un tarif validé hors période** : le modèle est ajusté sur 2022–2023 et jugé sur 2024, jamais sur ses propres données.
3. **Un tarif équilibré** : le ratio sinistres sur primes attendu doit être proche de la cible (72 %), l'ensemble des primes couvrant sinistres, frais et marge.
4. **Un tarif robuste** : on connaît l'effet d'une inflation plus forte ou d'une fréquence plus élevée, et le capital nécessaire pour absorber une mauvaise année.
5. **Un tarif justifiable** : variables autorisées, absence de proxy douteux, documentation, avis de validation indépendant.
6. **Un tarif honnête** : on dit ce que le modèle ne sait pas.

La méthode suit huit étapes, chacune appuyée sur un chapitre du livre :

| Étape | Question | Chapitre du livre |
|---|---|---|
| P.2 Auditer et découper | Les données sont-elles saines ? Comment valider hors période ? | 2.1, 2.2 |
| P.3 Fréquence | Combien de sinistres par année-police ? | 2.1, 2.4 |
| P.4 Sévérité | Combien coûte un sinistre ? Que faire des gros ? | 2.1, 6.2 |
| P.5 Prime pure et validation | La prime pure classe-t-elle bien les polices ? | 2.2 |
| P.6 Du modèle au tarif | Quelles primes commerciales, quels coefficients ? | 2.2, 2.4 |
| P.7 Robustesse et capital | Que se passe-t-il si l'année est mauvaise ? | 3.1, 3.2, 4.2 |
| P.8 Notes réglementaires | Le modèle est-il documentable, équitable, validable ? | 3.4, 4.2 |
| P.9 Le rapport | Peut-on publier ce tarif ? | tous |

> 📦 **Les données.** `donnees/polices_auto.csv` (100 000 lignes police-année, 2022 à 2024) et `donnees/sinistres_auto.csv` (un sinistre par ligne). Elles sont **simulées** : la vérité est programmée (docstring de `build/donnees5.py`) et nous la révélerons en fin d'étude. Aucune variable protégée (sexe, origine…) n'y figure.

### P.2 Étape 1 : auditer les données et découper hors période

On vérifie d'abord ce que l'on a : volumes par année, expositions, fréquence observée, valeurs incohérentes. Puis on **découpe dans le temps** : 2022 et 2023 pour ajuster, 2024 pour juger (volume III, section 1.1).

```python
import numpy as np, pandas as pd, statsmodels.api as sm, statsmodels.formula.api as smf
import warnings; warnings.filterwarnings("ignore")

pol = pd.read_csv("donnees/polices_auto.csv")
sin = pd.read_csv("donnees/sinistres_auto.csv")
audit = pol.groupby("annee").agg(lignes=("id_police", "size"), exposition=("exposition", "sum"), sinistres=("nb_sinistres", "sum"))
audit["frequence"] = (audit["sinistres"] / audit["exposition"]).round(4)
print(audit.round(0).astype({"lignes": int, "exposition": int, "sinistres": int}).assign(frequence=audit["frequence"]))
print("sinistres du fichier sinistres == somme des nb_sinistres :", len(sin) == pol["nb_sinistres"].sum())
print("expositions hors ]0 ; 1] :", int(((pol["exposition"] <= 0) | (pol["exposition"] > 1)).sum()))
```
<!--sortie-->
```text
       lignes  exposition  sinistres  frequence
annee                                          
2022    30244       26200       1679     0.0641
2023    32741       28321       1907     0.0673
2024    37015       32081       2136     0.0666
sinistres du fichier sinistres == somme des nb_sinistres : True
expositions hors ]0 ; 1] : 0
```

> ✅ **À retenir.** La fréquence est **stable** d'une année à l'autre (autour de 6,6 %) : c'est ce qui autorise à juger sur 2024 un modèle ajusté sur 2022–2023. La **sévérité**, elle, dérive avec l'inflation : nous y reviendrons en P.4.

On regroupe aussi les variables continues en **classes** (âge, ancienneté du véhicule, bonus-malus). Les classes sont des choix de métier, que l'on documente ; elles rendent le tarif lisible et captent les effets non linéaires.

```python
pol["classe_age"] = pd.cut(pol["age_conducteur"], [17, 24, 34, 49, 64, 70, 120], labels=["18-24", "25-34", "35-49", "50-64", "65-70", "71+"]).astype(str)
pol["classe_veh"] = pd.cut(pol["age_vehicule"], [-1, 2, 5, 10, 30], labels=["0-2", "3-5", "6-10", "11+"]).astype(str)
pol["classe_bm"] = pd.cut(pol["bonus_malus"], [0, 60, 80, 100, 200], labels=["<=60", "61-80", "81-100", ">100"]).astype(str)
sin = sin.merge(pol.drop(columns=["annee", "exposition", "nb_sinistres"]), on="id_police", how="left")
ajust = pol[pol["annee"] <= 2023].copy()
test = pol[pol["annee"] == 2024].copy()
print("lignes d'ajustement :", len(ajust), "| lignes de test :", len(test))
```
<!--sortie-->
```text
lignes d'ajustement : 62985 | lignes de test : 37015
```

### P.3 Étape 2 : la fréquence

La fréquence suit une loi de Poisson dont la moyenne est proportionnelle à l'**exposition** (le temps pendant lequel la police est en risque) : c'est l'**offset** $\ln(\text{exposition})$ du GLM (volume II, section 2.3 ; livre, 2.1). On compare à une référence, la fréquence moyenne constante.

```python
formule_f = "nb_sinistres ~ C(classe_age) + C(zone) + C(classe_bm) + puissance + C(usage) + C(carburant) + C(classe_veh)"
mod_f = smf.glm(formule_f, data=ajust, family=sm.families.Poisson(), offset=np.log(ajust["exposition"])).fit()
print("dispersion de Pearson :", round(mod_f.pearson_chi2 / mod_f.df_resid, 3))

def deviance_poisson(y, mu):
    y, mu = np.asarray(y, float), np.asarray(mu, float)
    return 2 * (np.where(y > 0, y * np.log(np.where(y > 0, y / mu, 1.0)), 0) - (y - mu)).sum()

mu_test = mod_f.predict(test, offset=np.log(test["exposition"]))
mu_ref = (ajust["nb_sinistres"].sum() / ajust["exposition"].sum()) * test["exposition"]
print("déviance test : modèle", round(deviance_poisson(test["nb_sinistres"], mu_test)), "| référence", round(deviance_poisson(test["nb_sinistres"], mu_ref)))
print("sinistres prévus 2024 :", round(mu_test.sum()), "| observés :", int(test["nb_sinistres"].sum()))
```
<!--sortie-->
```text
dispersion de Pearson : 1.028
déviance test : modèle 12056 | référence 12226
sinistres prévus 2024 : 2109 | observés : 2136
```

La dispersion de Pearson proche de 1 dit qu'un Poisson suffit **à l'échelle de la police** (l'hétérogénéité non observée existe, mais sa variance est petite devant la moyenne quand la fréquence annuelle est de 6,6 %) ; elle compte davantage à l'échelle d'un **portefeuille** (étape P.7).

```python
rel_f = np.exp(mod_f.params).round(3)
rel_f = rel_f[rel_f.index != "Intercept"]
print(rel_f.to_string())
```
<!--sortie-->
```text
C(classe_age)[T.25-34]                0.559
C(classe_age)[T.35-49]                0.516
C(classe_age)[T.50-64]                0.554
C(classe_age)[T.65-70]                0.578
C(classe_age)[T.71+]                  0.692
C(zone)[T.Zone B]                     1.057
C(zone)[T.Zone C]                     1.122
C(zone)[T.Zone D]                     1.229
C(zone)[T.Zone E]                     1.501
C(zone)[T.Zone F]                     1.543
C(classe_bm)[T.81-100]                1.117
C(classe_bm)[T.<=60]                  0.912
C(classe_bm)[T.>100]                  1.300
C(usage)[T.professionnel]             1.152
C(carburant)[T.essence]               0.968
C(carburant)[T.hybride_electrique]    0.904
C(classe_veh)[T.11+]                  0.790
C(classe_veh)[T.3-5]                  0.922
C(classe_veh)[T.6-10]                 0.863
puissance                             1.058
```

**Lecture.** Les coefficients sont des **multiplicateurs** de la fréquence à modalité de référence (18-24 ans, zone A, bonus-malus de 61 à 80, usage privé, véhicule neuf). Un conducteur de 35 à 49 ans a une fréquence d'environ la moitié (0,52) de celle d'un jeune ; la zone F pèse 1,54 contre 1 pour la zone A ; un usage professionnel ajoute 15 %. La vérité programmée (docstring de `build/donnees5.py`) donnait un rapport de 1,73 entre jeunes et adultes (soit 0,58 dans ce sens) et de 1,65 entre les zones F et A : le modèle retrouve l'ordre de grandeur, avec l'écart d'estimation que l'on attend sur 63 000 lignes.

### P.4 Étape 3 : la sévérité et les gros sinistres

Un sinistre coûte en moyenne quelques milliers d'euros, mais certains sinistres corporels coûtent plusieurs centaines de milliers : la moyenne est **tirée par la queue**. On sépare donc le coût en deux : une partie **écrêtée** à 100 000 €, que l'on modélise, et la partie **au-delà**, que l'on mutualise par un **coefficient de gros sinistres** unique (livre, 2.1 et 6.2). Regardons d'abord comment la queue se comporte d'une année à l'autre.

```python
SEUIL = 100_000
sin["cout_ecrete"] = sin["montant"].clip(upper=SEUIL)
sin["cout_exces"] = sin["montant"] - sin["cout_ecrete"]
expo_an = pol.groupby("annee")["exposition"].sum()
par_an = sin.groupby("annee").agg(sinistres=("montant", "size"), gros=("montant", lambda m: int((m > SEUIL).sum())), exces=("cout_exces", "sum"))
par_an["exces_par_annee_police"] = (par_an["exces"] / expo_an).round(1)
print(par_an[["sinistres", "gros", "exces_par_annee_police"]])
```
<!--sortie-->
```text
       sinistres  gros  exces_par_annee_police
annee                                         
2022        1679    28                   187.4
2023        1907    29                   240.4
2024        2136    28                    84.8
```

Le **nombre** de gros sinistres est stable, mais leur **coût total** varie du simple au triple : la queue est volatile, et c'est ce qui rend la sévérité difficile à estimer.

On ramène aussi les montants à un **niveau de prix commun** : les coûts augmentent avec le temps, donc un sinistre de 2022 coûte « moins cher » qu'un sinistre de 2024. Peut-on estimer cette **tendance** sur les années d'ajustement ? Essayons, sans toucher à 2024.

```python
sin_aj = sin[sin["annee"] <= 2023]
tendance = smf.glm("cout_ecrete ~ annee", data=sin_aj, family=sm.families.Gamma(sm.families.links.Log())).fit()
ic = np.exp(tendance.conf_int().loc["annee"])
print("tendance estimée :", round(float(np.exp(tendance.params["annee"])) - 1, 3), "| intervalle à 95 % : [", round(ic[0] - 1, 3), ";", round(ic[1] - 1, 3), "]")
infl = 1.04      # hypothèse retenue : indice externe du coût des sinistres (la vérité programmée vaut aussi 0,04)
sin["cout_2024"] = sin["cout_ecrete"] * infl ** (2024 - sin["annee"])
sin["exces_2024"] = sin["cout_exces"] * infl ** (2024 - sin["annee"])
sin_aj = sin[sin["annee"] <= 2023]
```
<!--sortie-->
```text
tendance estimée : -0.092 | intervalle à 95 % : [ -0.239 ; 0.085 ]
```



Deux années de sinistres bruités ne suffisent pas à mesurer une tendance : l'**intervalle est large** et contient des valeurs absurdes. On retient donc un **indice externe** (hypothèse écrite, à documenter dans le dossier), ce que ferait un actuaire.

Reste à choisir la **complexité du modèle de sévérité**. On compare trois candidats par la déviance Gamma, en ajustant sur 2022 et en jugeant sur 2023 (le test de 2024 reste intact).

```python
def deviance_gamma(y, mu):
    y, mu = np.asarray(y, float), np.asarray(mu, float)
    return 2 * (-np.log(y / mu) + (y - mu) / mu).sum()

candidats = {"constante": "cout_2024 ~ 1", "zone + puissance": "cout_2024 ~ C(zone) + puissance",
             "complet": "cout_2024 ~ C(classe_age) + C(zone) + puissance + C(usage) + C(classe_veh)"}
a22, a23 = sin[sin["annee"] == 2022], sin[sin["annee"] == 2023]
devs = {}
for nom, f in candidats.items():
    m = smf.glm(f, data=a22, family=sm.families.Gamma(sm.families.links.Log())).fit()
    devs[nom] = round(deviance_gamma(a23["cout_2024"], m.predict(a23)))
print(devs)
# règle de parcimonie : on ne complique que si la déviance baisse d'au moins 1 %
choix = next(nom for nom in candidats if devs[nom] <= 1.01 * min(devs.values()))
mod_s = smf.glm(candidats[choix], data=sin_aj, family=sm.families.Gamma(sm.families.links.Log())).fit()
print("modèle de sévérité retenu :", choix, "| sévérité écrêtée moyenne (prix 2024) :", round(mod_s.predict(sin_aj).mean()))
```
<!--sortie-->
```text
{'constante': 2837, 'zone + puissance': 2834, 'complet': 2815}
modèle de sévérité retenu : constante | sévérité écrêtée moyenne (prix 2024) : 5538
```

Les trois déviances diffèrent de moins de 1 % : aucune complication ne **se démarque du bruit**. La règle de parcimonie retient la **constante** : la sévérité est **mutualisée**, et la segmentation du tarif repose sur la fréquence.

> ⚠️ **Attention.** Avec quelques milliers de sinistres, un modèle de sévérité riche **ne bat pas toujours une moyenne constante** : les coefficients estimés sont du bruit, et ce bruit se paie hors période. En pratique, beaucoup de tarifs mutualisent la sévérité et segmentent surtout la **fréquence**, qui s'estime bien mieux.

### P.5 Étape 4 : la prime pure et sa validation hors période

La **prime pure** d'une police est l'espérance de sa charge annuelle : fréquence prévue × sévérité écrêtée prévue × (1 + coefficient de gros sinistres). Le coefficient est le rapport de l'excédent à la charge écrêtée sur les années d'ajustement, aux prix de 2024. On valide d'abord la partie **écrêtée**, qui porte l'essentiel du signal, puis on regarde les gros sinistres à part.

```python
coef_gros = sin_aj["exces_2024"].sum() / sin_aj["cout_2024"].sum()
sev_test = mod_s.predict(test.assign(cout_2024=1.0))
test["prime_ecretee"] = mu_test.values * sev_test.values
test["prime_pure"] = test["prime_ecretee"] * (1 + coef_gros)
sin24 = sin[sin["annee"] == 2024]
test["charge_ecretee"] = test["id_police"].map(sin24.groupby("id_police")["cout_ecrete"].sum()).fillna(0.0)
test["charge_reelle"] = test["id_police"].map(sin24.groupby("id_police")["montant"].sum()).fillna(0.0)
print("coefficient de gros sinistres :", round(coef_gros, 3))
print("charge écrêtée par année-police : prévue", round(test["prime_ecretee"].sum() / test["exposition"].sum(), 1), "| réelle", round(test["charge_ecretee"].sum() / test["exposition"].sum(), 1))
print("charge totale par année-police : prévue", round(test["prime_pure"].sum() / test["exposition"].sum(), 1), "| réelle", round(test["charge_reelle"].sum() / test["exposition"].sum(), 1))
```
<!--sortie-->
```text
coefficient de gros sinistres : 0.624
charge écrêtée par année-police : prévue 364.1 | réelle 342.7
charge totale par année-police : prévue 591.3 | réelle 427.5
```

**Lecture.** Sur la partie écrêtée, la prévision est proche du réel : 364 € prévus contre 343 € par année-police, soit un écart de 6 %. La charge **totale** est beaucoup plus éloignée (591 € prévus contre 428 €) pour une seule raison : en 2024, les gros sinistres ont coûté 85 € par année-police alors que les deux années précédentes en avaient coûté 187 et 240. Ce n'est pas une erreur de modèle, c'est la **volatilité de la queue** : un seul exercice de validation ne permet pas de juger le coefficient de gros sinistres.

On juge ensuite le **classement** de la partie écrêtée : on trie les polices par prime pure, on regroupe en déciles d'exposition et on compare la charge réelle à la charge prévue (courbe de lift), puis on résume par un **coefficient de Gini** de la courbe de Lorenz ordonnée (livre, 2.2).

```python
def table_deciles(df, score, reel, k=10):
    d = df.sort_values(score).copy()
    d["decile"] = np.minimum((d["exposition"].cumsum() / d["exposition"].sum() * k).astype(int), k - 1) + 1
    t = d.groupby("decile").agg(expo=("exposition", "sum"), prevue=(score, "sum"), reelle=(reel, "sum"))
    return t.assign(ratio=t["reelle"] / t["prevue"])

def gini_lorenz(df, score, reel):
    d = df.sort_values(score)
    x = np.r_[0, (d["exposition"].cumsum() / d["exposition"].sum()).values]
    y = np.r_[0, (d[reel].cumsum() / d[reel].sum()).values]
    return 1 - 2 * np.trapezoid(y, x)

dec = table_deciles(test, "prime_ecretee", "charge_ecretee")
print(dec["ratio"].round(2).to_dict())
print("Gini de la prime écrêtée (2024) :", round(gini_lorenz(test, "prime_ecretee", "charge_ecretee"), 3))
```
<!--sortie-->
```text
{1: 1.13, 2: 0.97, 3: 1.15, 4: 0.89, 5: 1.0, 6: 0.76, 7: 0.77, 8: 0.85, 9: 1.1, 10: 0.89}
Gini de la prime écrêtée (2024) : 0.123
```

**Lecture.** Le Gini de 0,12 est modeste, et c'est normal : une charge de sinistres est dominée par le **hasard** (94 % des polices n'ont aucun sinistre dans l'année) : le signal à classer est faible devant le bruit. Les rapports réel/prévu par décile s'écartent de 1 de moins de 25 % ; ces écarts sont **du même ordre** que le bruit simulé ci-dessous.

Un décile est un petit échantillon (≈ 200 sinistres) : le rapport réel/prévu y fluctue de **plus ou moins 20 %** autour de 1 par pur hasard. Pour savoir si l'écart est du bruit, on le **simule** : on rejoue 300 fois la charge de chaque décile avec les coûts observés et la fréquence prévue (livre, 2.2).

```python
rng0 = np.random.default_rng(7)
couts_ec = sin_aj["cout_2024"].values
sim = []
for k in range(1, 11):
    lam_k = dec.loc[k, "prevue"] / couts_ec.mean()          # nombre moyen de sinistres du décile
    ch_k = np.array([rng0.choice(couts_ec, rng0.poisson(lam_k)).sum() for _ in range(300)])
    sim.append(ch_k.std() / ch_k.mean())
print("écart relatif typique dû au hasard, par décile :", np.round(sim, 2))
```
<!--sortie-->
```text
écart relatif typique dû au hasard, par décile : [0.22 0.23 0.21 0.23 0.21 0.19 0.2  0.19 0.17 0.15]
```

Le bruit typique d'un décile va de **15 à 23 %** : les écarts observés au tableau précédent sont donc **compatibles avec le hasard**. Un tarif ne se juge pas décile par décile sur une année ; on regarde le classement global (Gini), la calibration d'ensemble et la tendance sur plusieurs années.

On compare enfin à une **référence plus flexible**, un boosting de gradient à perte de Poisson sur la seule fréquence (volume III, section 2.4), pour vérifier que le GLM ne laisse pas de signal sur la table.

```python
import lightgbm as lgb
vars_m = ["age_conducteur", "age_vehicule", "puissance", "bonus_malus", "anciennete_permis"]
Xa = pd.concat([ajust[vars_m], pd.get_dummies(ajust[["zone", "usage", "carburant"]], dtype=float)], axis=1)
Xt = pd.concat([test[vars_m], pd.get_dummies(test[["zone", "usage", "carburant"]], dtype=float)], axis=1)
gbm = lgb.LGBMRegressor(objective="poisson", n_estimators=150, learning_rate=0.03, num_leaves=6, min_child_samples=300,
                        subsample=0.8, subsample_freq=1, random_state=0, verbose=-1)
gbm.fit(Xa, ajust["nb_sinistres"] / ajust["exposition"], sample_weight=ajust["exposition"])
mu_gbm = gbm.predict(Xt) * test["exposition"].values
print("déviance test Poisson : GLM", round(deviance_poisson(test["nb_sinistres"], mu_test)), "| boosting", round(deviance_poisson(test["nb_sinistres"], mu_gbm)))
test = test.assign(freq_glm=mu_test.values, freq_gbm=mu_gbm)
print("Gini de la fréquence (2024) : GLM", round(gini_lorenz(test, "freq_glm", "nb_sinistres"), 3), "| boosting", round(gini_lorenz(test, "freq_gbm", "nb_sinistres"), 3))
```
<!--sortie-->
```text
déviance test Poisson : GLM 12056 | boosting 12073
Gini de la fréquence (2024) : GLM 0.125 | boosting 0.113
```

**Lecture.** Le boosting ne fait pas mieux que le GLM (déviance 12 073 contre 12 056, Gini 0,113 contre 0,125) : il n'y a **pas de signal oublié** par le tarif, et le GLM garde l'avantage de la **lisibilité**. C'est le résultat attendu ici : la vérité programmée est log-linéaire.

### P.6 Étape 5 : du modèle au tarif

La prime commerciale ajoute à la prime pure les **frais** (acquisition, gestion) et une **marge**. Avec 25 % de frais et 3 % de marge, calculés sur la prime commerciale : $\text{prime} = \dfrac{\text{prime pure}}{1-0{,}25-0{,}03}$, soit un ratio sinistres/primes visé de 72 % (livre, 2.2). On vérifie ce ratio sur 2024, **hors gros sinistres** puis **avec**, et on regarde la **dispersion** des primes (une prime trop disparate fait fuir les bons risques).

```python
FRAIS, MARGE = 0.25, 0.03
test["prime"] = test["prime_pure"] / (1 - FRAIS - MARGE)
sp_ecrete = test["charge_ecretee"].sum() / (test["prime_ecretee"].sum() / (1 - FRAIS - MARGE))
sp_total = test["charge_reelle"].sum() / test["prime"].sum()
print("ratio sinistres/primes visé : 0.72 | réalisé 2024 hors gros sinistres :", round(sp_ecrete, 3), "| avec gros sinistres :", round(sp_total, 3))
ap = test["prime"] / test["exposition"]
print("prime annualisée : min", round(ap.min()), "| médiane", round(ap.median()), "| max", round(ap.max()), "| rapport max/min", round(ap.max() / ap.min(), 1))
```
<!--sortie-->
```text
ratio sinistres/primes visé : 0.72 | réalisé 2024 hors gros sinistres : 0.678 | avec gros sinistres : 0.521
prime annualisée : min 351 | médiane 747 | max 3289 | rapport max/min 9.4
```

**Lecture.** Hors gros sinistres, le ratio réalisé (0,68) est proche de la cible de 0,72 (l'écart reflète les 6 % de la partie écrêtée). Avec les gros sinistres, il tombe à 0,52, pour la raison déjà vue : 2024 a été une bonne année pour la queue. Les primes annualisées vont de 351 € à 3 289 € (médiane 747 €) : un rapport de 9,4 entre la plus chère et la moins chère, un écart que la direction commerciale devra juger acceptable.

Un tarif se publie en **coefficients arrondis** : chaque modalité reçoit un multiplicateur par rapport à la modalité de référence, arrondi à deux décimales, puis on rebalance la prime de base pour que le **total des primes reste inchangé**.

```python
rel = np.exp(mod_f.params).drop("Intercept")
rel_arrondi = rel.round(2)
print("coefficients (extraits) :", rel_arrondi.loc[[i for i in rel_arrondi.index if "Zone F" in i or "professionnel" in i]].to_dict())
print("écart maximal dû à l'arrondi :", round((rel_arrondi / rel - 1).abs().max(), 3))
```
<!--sortie-->
```text
coefficients (extraits) : {'C(zone)[T.Zone F]': 1.54, 'C(usage)[T.professionnel]': 1.15}
écart maximal dû à l'arrondi : 0.009
```

> ⚠️ **Attention.** Arrondir est un acte de **tarification** : un écart de 0,5 point sur un coefficient déplace la prime de milliers de clients. On le mesure (ici moins de 1 %) et l'on rebalance ; on ne l'ignore pas.

### P.7 Étape 6 : robustesse et capital

Une prime **moyenne** suffisante ne dit pas ce qui arrive **une mauvaise année**. On simule la charge annuelle du portefeuille 2025 (à même exposition qu'en 2024) : le nombre de sinistres est **binomial négatif**, dont la variance additionne trois sources (le hasard de Poisson, l'hétérogénéité non observée entre polices — variance 0,4, vérité programmée — et un **choc commun** de 5 % qui touche toutes les polices à la fois, hypothèse), le coût de chaque sinistre est tiré dans les coûts observés remis au **niveau de prix 2025** (livre, 2.1 ; modèle collectif). On compare deux situations : **sans réassurance**, et avec un **traité en excédent de sinistre** qui prend en charge, pour chaque sinistre, la part au-delà de 250 000 € contre une prime égale à 135 % de l'espérance cédée (chargement d'exemple, livre 6.2 et 6.3).

```python
rng = np.random.default_rng(2025)
lam = test["freq_glm"].sum()                                  # nombre moyen de sinistres 2025 (même exposition)
theta, CHOC_COMMUN, PRIORITE, CHARG_REASS = 0.4, 0.05, 250_000, 1.35
var_nb = lam + theta * (test["freq_glm"] ** 2).sum() + (CHOC_COMMUN * lam) ** 2
print("nombre de sinistres 2025 : moyenne", round(lam), "| écart-type", round(var_nb ** 0.5), "| dont Poisson seul", round(lam ** 0.5))
prime_totale = test["prime"].sum() * infl                     # prime 2025 = tarif 2024 indexé : hypothèse simple

def simuler(freq_mult=1.0, infl_extra=0.0, n_sim=3000, seed=11):
    r = np.random.default_rng(seed)
    m_, v_ = lam * freq_mult, lam * freq_mult + theta * (test["freq_glm"] ** 2).sum() * freq_mult ** 2 + (CHOC_COMMUN * lam * freq_mult) ** 2
    nb = r.negative_binomial(m_ ** 2 / (v_ - m_), m_ / v_, n_sim)
    cs = sin["montant"].values * (infl + infl_extra) ** (2025 - sin["annee"].values)
    brut = np.empty(n_sim); net = np.empty(n_sim)
    for i, k in enumerate(nb):
        c = r.choice(cs, k)
        brut[i], net[i] = c.sum(), np.minimum(c, PRIORITE).sum()
    cede_moy = lam * freq_mult * np.maximum(cs - PRIORITE, 0).mean()
    return brut, net + CHARG_REASS * cede_moy                 # charge nette = gardée + prime de réassurance

brut, net = simuler()
for nom, ch in [("sans réassurance", brut), ("avec excédent de sinistre", net)]:
    print(f"{nom:27s} moyenne {ch.mean()/1e6:5.2f} M€ | quantile 99,5 % {np.quantile(ch, 0.995)/1e6:5.2f} M€ | capital (99,5 % - moyenne) {(np.quantile(ch, 0.995) - ch.mean())/1e6:5.2f} M€")
```
<!--sortie-->
```text
nombre de sinistres 2025 : moyenne 2109 | écart-type 115 | dont Poisson seul 46
sans réassurance            moyenne 17.57 M€ | quantile 99,5 % 25.60 M€ | capital (99,5 % - moyenne)  8.03 M€
avec excédent de sinistre   moyenne 18.79 M€ | quantile 99,5 % 22.29 M€ | capital (99,5 % - moyenne)  3.50 M€
```

**Lecture.** Au quantile 99,5 %, la charge annuelle est d'environ 25,6 M€ pour une moyenne de 17,6 M€ : le **capital de risque** (différence) est de 8,0 M€ sans réassurance et de 3,5 M€ avec le traité en excédent de sinistre, qui coûte environ 1,2 M€ de plus en moyenne (la prime de réassurance, chargée à 135 %). Le traité **stabilise** : il réduit le capital de plus de moitié pour un surcoût moyen d'environ 7 %.

Puis on **dégrade** les hypothèses : inflation de la sévérité plus forte de 6 points, fréquence plus élevée de 15 %. On compare les ratios sinistres/primes (charge nette de réassurance) obtenus, en moyenne et au quantile 99,5 %.

```python
for nom, fm, ie in [("central", 1.0, 0.0), ("inflation +6 pts", 1.0, 0.06), ("fréquence +15 %", 1.15, 0.0), ("les deux", 1.15, 0.06)]:
    b_, n_ = simuler(fm, ie)
    print(f"{nom:18s} S/P net moyen {n_.mean()/prime_totale:.3f} | S/P net au quantile 99,5 % {np.quantile(n_, 0.995)/prime_totale:.3f} | sans réassurance : {np.quantile(b_, 0.995)/prime_totale:.3f}")
```
<!--sortie-->
```text
central            S/P net moyen 0.686 | S/P net au quantile 99,5 % 0.813 | sans réassurance : 0.934
inflation +6 pts   S/P net moyen 0.775 | S/P net au quantile 99,5 % 0.910 | sans réassurance : 1.050
fréquence +15 %    S/P net moyen 0.788 | S/P net au quantile 99,5 % 0.936 | sans réassurance : 1.063
les deux           S/P net moyen 0.891 | S/P net au quantile 99,5 % 1.049 | sans réassurance : 1.194
```

**Lecture.** Dans le scénario central, la charge nette moyenne représente 69 % des primes et 81 % au quantile 99,5 %. Si l'inflation est plus forte de 6 points **et** la fréquence plus élevée de 15 %, le ratio moyen monte à 89 % et dépasse 100 % au quantile 99,5 % (105 % avec le traité, 119 % sans) : la mutuelle perd de l'argent les mauvaises années. Ces scénarios ne sont **pas des prévisions** : ils montrent quelles hypothèses pèsent le plus, ici la fréquence (+15 %) un peu plus que l'inflation (+6 points).

> ⚠️ **Attention.** Le capital de la queue dépend **entièrement** de l'ajustement de la queue. Avec une trentaine de gros sinistres par an et une loi à variance quasi infinie, la mauvaise année simulée ne reflète que les gros sinistres observés ; un autre échantillon donnerait un autre quantile. C'est ce que la réassurance achète : de la **stabilité**, et la possibilité de **borner** ce que l'on ne sait pas mesurer.

### P.8 Étape 7 : les notes réglementaires

Le modèle n'est pas fini quand l'ajustement est fait : il faut pouvoir **le défendre**. Cette étape produit trois pièces. Les deux premières se **vérifient par le calcul**.

**Variables autorisées et proxies.** Aucune variable protégée n'est dans le modèle, mais une variable permise peut en être le **substitut** (un proxy). On mesure la dépendance de chaque variable de tarification avec l'âge, que beaucoup de textes encadrent, pour savoir ce que le tarif transmet indirectement (volume III, section 5.4).

```python
cor_age = pol[["age_conducteur", "age_vehicule", "puissance", "bonus_malus", "anciennete_permis"]].corr()["age_conducteur"].drop("age_conducteur").round(2)
print(cor_age.to_string())
```
<!--sortie-->
```text
age_vehicule         0.00
puissance            0.00
bonus_malus         -0.26
anciennete_permis    0.99
```

**Lecture.** L'**ancienneté du permis** est corrélée à 0,99 avec l'âge : c'est un **substitut presque parfait**. Elle est exclue du tarif retenu (qui contient déjà l'âge) ; l'ajouter à un modèle qui n'aurait pas eu l'âge reviendrait à faire entrer l'âge **par la fenêtre**. La corrélation du bonus-malus avec l'âge (−0,26) est modérée : cette variable est **comportementale** (elle résume le passé de sinistres) mais elle transmet aussi, en partie, l'âge.

**Stabilité du portefeuille.** On compare la distribution des classes d'âge de 2024 à celle de l'ajustement par le **PSI** (volume IV, section 4.7) : un portefeuille qui change de forme invalide les coefficients.

```python
def psi(attendu, actuel, eps=1e-4):
    p = np.clip(attendu / attendu.sum(), eps, None); q = np.clip(actuel / actuel.sum(), eps, None)
    return float(((q - p) * np.log(q / p)).sum())

for col in ["classe_age", "zone", "classe_bm"]:
    a = ajust.groupby(col)["exposition"].sum(); t = test.groupby(col)["exposition"].sum().reindex(a.index)
    print(f"PSI {col:11s}", round(psi(a.values, t.values), 4))
```
<!--sortie-->
```text
PSI classe_age  0.0004
PSI zone        0.0001
PSI classe_bm   0.0
```

**Lecture.** Les PSI sont presque nuls (≪ 0,10) : le portefeuille de 2024 a la même forme que celui de l'ajustement. C'est trop beau pour être vrai en réalité : ici la simulation tire chaque année dans la même population. Un PSI proche de 0,25 serait le signal qu'il faut reprendre l'étude (volume IV, section 4.7).

**La fiche de validation.** Un second regard, indépendant de l'équipe qui a construit le modèle, répond à une grille. Voici la nôtre, à remplir par les chiffres des étapes précédentes (livre, 3.4 et 4.2).

| Question | Réponse tirée du projet |
|---|---|
| Les données sont-elles complètes et cohérentes ? | P.2 : fichiers cohérents, expositions valides |
| Le modèle a-t-il été jugé hors période ? | P.3 et P.5 : ajusté sur 2022–2023, jugé sur 2024 |
| Surpasse-t-il une référence simple ? | P.3 : déviance de test plus basse que la fréquence constante |
| Un modèle plus flexible fait-il mieux ? | P.5 : comparaison au boosting |
| Le tarif est-il équilibré ? | P.6 : ratio S/P visé et réalisé |
| Que se passe-t-il en cas de stress ? | P.7 : quatre scénarios |
| Les variables sont-elles défendables ? | P.8 : pas de variable protégée ; corrélations avec l'âge |
| Qui est responsable, et quand revalide-t-on ? | à décider : propriétaire du modèle, revue annuelle, seuils de dérive |

> ⚠️ **Rappel.** Ces notes illustrent une **démarche** ; elles ne sont pas un avis juridique, comptable ou actuariel. Les exigences exactes dépendent du pays et du texte en vigueur : à faire vérifier par les fonctions compétentes.

### P.9 Étape 8 : le rapport

On regroupe les critères en un **tableau de décision**, chaque critère étant fixé **avant** de regarder les résultats.

```python
criteres = {
    "déviance de test inférieure à la référence constante": deviance_poisson(test["nb_sinistres"], mu_test) < deviance_poisson(test["nb_sinistres"], mu_ref),
    "sinistres prévus en 2024 à ±3 % des observés": abs(mu_test.sum() / test["nb_sinistres"].sum() - 1) < 0.03,
    "Gini de la prime écrêtée > 0,10": gini_lorenz(test, "prime_ecretee", "charge_ecretee") > 0.10,
    "ratio S/P 2024 hors gros sinistres dans [0,65 ; 0,80]": 0.65 <= sp_ecrete <= 0.80,
    "ratio S/P 2024 avec gros sinistres inférieur à 0,90": sp_total < 0.90,
    "ratio S/P net au quantile 99,5 % (scénario central) < 1,30": np.quantile(net, 0.995) / prime_totale < 1.30,
    "PSI de chaque variable < 0,10": all(psi(ajust.groupby(c)["exposition"].sum().values, test.groupby(c)["exposition"].sum().reindex(ajust.groupby(c)["exposition"].sum().index).values) < 0.10 for c in ["classe_age", "zone", "classe_bm"]),
}
for k, v in criteres.items():
    print("OK  " if v else "KO  ", k)
print("\nDécision :", "GO pour le tarif 2025" if all(criteres.values()) else "NO GO : revoir le tarif")
```
<!--sortie-->
```text
OK   déviance de test inférieure à la référence constante
OK   sinistres prévus en 2024 à ±3 % des observés
OK   Gini de la prime écrêtée > 0,10
OK   ratio S/P 2024 hors gros sinistres dans [0,65 ; 0,80]
OK   ratio S/P 2024 avec gros sinistres inférieur à 0,90
OK   ratio S/P net au quantile 99,5 % (scénario central) < 1,30
OK   PSI de chaque variable < 0,10

Décision : GO pour le tarif 2025
```

**Lecture.** Les sept critères sont satisfaits : décision **GO**. Notez ce que la décision ne dit pas : elle ne dit pas que le tarif est « juste », elle dit qu'il satisfait des critères fixés **à l'avance**. Notez aussi que le ratio 2024 « avec gros sinistres » (0,52) est bas **par chance** (la queue a été clémente), et que le critère de la queue est satisfait même sans traité (0,93), mais avec un capital plus de deux fois plus élevé (8,0 contre 3,5 M€).

**Ce que dit la vérité programmée.** Fréquence : le modèle a retrouvé les effets d'âge, de zone, d'usage, de bonus-malus (à l'incertitude près) ; sévérité : les vrais effets (puissance, zone) sont minuscules, ce qui justifie la sévérité mutualisée ; inflation : 4 % par an, que deux années de données ne permettaient pas d'estimer ; queue : le coefficient de gros sinistres est volatil parce que la queue de Pareto simulée a une variance quasi infinie. Dans une étude réelle, on ne dispose pas de cette vérité : seuls les contrôles hors période et les scénarios nous protègent.

> ✅ **À retenir.** Un tarif n'est pas une prédiction : c'est une **décision** (un prix) prise sous incertitude et défendue par un dossier. La qualité d'un modèle de tarification se juge sur trois plans à la fois : **classer** les risques, **équilibrer** le total, **résister** au mauvais scénario.

### P.10 Les limites de l'étude

- **Données simulées.** La fréquence, la sévérité et l'inflation obéissent à des lois simples ; la réalité apporte des ruptures (sinistres de masse, changements de comportement, fraude) que ce jeu ne contient pas.
- **Une seule branche.** Aucun lien avec les autres produits de la mutuelle, la réassurance (chapitre 6) ou la solvabilité complète (4.2) : le « capital de risque » de P.7 est un indicateur, pas un SCR.
- **Sévérité peu précise.** Quelques milliers de sinistres, des gros sinistres rares : l'écrêtement à 100 000 € est un choix que l'on devrait revalider chaque année.
- **Inflation supposée constante.** L'indexation de P.7 est une hypothèse, pas une prévision.
- **Équité non étudiée en détail.** On a vérifié l'absence de variable protégée et mesuré des corrélations ; un audit d'équité complet demande des données sur les groupes concernés (volume III, section 5.4).

### P.11 Variante : un score de crédit

La même démarche s'applique à un **score** de crédit (chapitre 1). Avec `donnees/credits_conso.csv` (prêts à la souscription, défaut à 12 mois), voici une version courte : découper, ajuster une logistique, juger par le **Gini** et le **KS**, puis vérifier la **calibration**.

```python
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve

cr = pd.read_csv("donnees/credits_conso.csv")
cr["revenu_manquant"] = cr["revenu_annuel"].isna().astype(int)
cr["emploi_manquant"] = cr["anciennete_emploi"].isna().astype(int)
cr = cr.fillna({"revenu_annuel": cr["revenu_annuel"].median(), "anciennete_emploi": cr["anciennete_emploi"].median()})
cr["age_u"] = (cr["age"] - 47) ** 2 / 100
cr["dti_coude"] = np.maximum(0, cr["taux_endettement"] - 0.5)
X = pd.concat([cr.drop(columns=["id_credit", "defaut_12m", "logement", "objet"]), pd.get_dummies(cr[["logement", "objet"]], drop_first=True, dtype=float)], axis=1)
Xa, Xt, ya, yt = train_test_split(X, cr["defaut_12m"], test_size=0.3, random_state=0, stratify=cr["defaut_12m"])
mu_, sd_ = Xa.mean(), Xa.std()
lr = LogisticRegression(max_iter=2000).fit((Xa - mu_) / sd_, ya)
p = lr.predict_proba((Xt - mu_) / sd_)[:, 1]
fpr, tpr, _ = roc_curve(yt, p)
print("AUC :", round(roc_auc_score(yt, p), 3), "| Gini :", round(2 * roc_auc_score(yt, p) - 1, 3), "| KS :", round((tpr - fpr).max(), 3))
print("défaut observé :", round(yt.mean(), 4), "| défaut prévu moyen :", round(p.mean(), 4))
```
<!--sortie-->
```text
AUC : 0.782 | Gini : 0.563 | KS : 0.421
défaut observé : 0.0597 | défaut prévu moyen : 0.0596
```

Le **Gini** (0,56) et le **KS** (0,42) mesurent le classement ; l'égalité du taux de défaut prévu (5,96 %) et observé (5,97 %) mesure la calibration d'ensemble. Ajouter à la logistique les deux transformations (`age_u`, `dti_coude`) que la vérité programmée contenait est un acte de **connaissance du métier** : sans elles, la logistique linéaire passe à côté de l'âge en U et du coude de l'endettement (chapitre 1, 1.1 et 1.2).

## Auto-évaluation

**Mode d'emploi.** Répondez à voix haute ou par écrit **avant** de lire le corrigé, en une ou deux phrases. Les sections à relire sont indiquées dans le corrigé. Trente-cinq bonnes réponses sur quarante signalent un volume bien assimilé ; les questions des chapitres facultatifs (➕ sections 1.4 à 1.6, 2.4 à 2.6, 3.3, 3.4, 4.4 à 4.6, chapitres 5 à 7) comptent si vous les avez lues. Les paramètres des exemples sont **illustratifs**.

### Risque de crédit (chapitre 1)

1. Une AUC de 0,78 correspond à quel coefficient de Gini ? Que mesure-t-il, et que ne mesure-t-il pas ?
2. Dans une base de 9 400 bons payeurs et 600 mauvais payeurs, une classe contient 300 bons et 50 mauvais. Quel est son poids de l'évidence (WOE), et que dit son signe ?
3. Une grille est calée à 600 points pour une cote de 50 contre 1, avec 20 points pour doubler la cote. Combien de points pour une cote de 100 contre 1 ? De 200 contre 1 ?
4. Pourquoi une grille construite par classes bat-elle parfois une régression logistique « brute » sur les mêmes variables ?
5. Une perte attendue vaut PD × LGD × EAD. Calculez-la pour une PD à douze mois de 2 %, une LGD de 45 % et une exposition de 10 000 €, puis (sans actualiser) pour une PD sur la durée de vie de 5 %. À quelle étape IFRS 9 correspond chaque chiffre ?
6. Un modèle prédit 1 % de défaut pour 1 000 prêts ; on en observe 18. Le modèle est-il bien calibré ? Calculez l'écart réduit.
7. Avec la matrice de transition annuelle (3 états : bon, moyen, défaut) dont les lignes sont (0,90 ; 0,08 ; 0,02), (0,10 ; 0,80 ; 0,10) et (0 ; 0 ; 1), quelle est la probabilité de défaut sur deux ans d'un emprunteur « bon » ?
8. Pourquoi une matrice de transition estimée sur dix ans ne décrit-elle pas ce qui arrivera pendant une récession ?

### Modélisation actuarielle (chapitre 2)

9. Une mutuelle observe 120 sinistres sur 2 000 années d'exposition. Quelle est la fréquence ? Combien de sinistres attend-on pour une police exposée six mois ?
10. La fréquence moyenne d'une police est de 0,07 par an et l'hétérogénéité non observée est de variance 0,4. Quelle est la variance du nombre de sinistres et le rapport variance sur moyenne ? Que dit ce rapport sur le choix entre Poisson et binomiale négative à l'échelle de la police ?
11. Une fréquence de 0,066 et une sévérité moyenne de 5 500 € : quelle est la prime pure ? Quelle prime commerciale pour un ratio sinistres/primes visé de 72 % ?
12. Dans le triangle cumulé (année 1 : 100, 150, 165 ; année 2 : 110, 168 ; année 3 : 120), quels sont les facteurs de développement du chain ladder et la provision totale ?
13. Pourquoi valide-t-on un tarif sur une période **postérieure** à celle de l'ajustement plutôt que sur un échantillon tiré au hasard ?
14. Un groupe de 500 années d'exposition a une fréquence de 5 % ; la moyenne générale est de 6,6 % et le point de crédibilité vaut $k=1\,000$ années. Quelle est la fréquence créditée ?
15. Pourquoi écrête-t-on les sinistres avant de modéliser leur sévérité, et que fait-on de la partie écrêtée ?
16. En assurance santé, que sont la sélection adverse et l'aléa moral ? Donnez un symptôme de chacun dans les données.

### Mesures de risque et stress tests (chapitre 3)

17. Les pertes quotidiennes d'un portefeuille suivent une loi normale centrée d'écart-type 2 %. Calculez la VaR à 99 % et l'expected shortfall à 99 %.
18. Quelle est la VaR à dix jours par la règle de la racine ? Quand la règle devient-elle fausse ?
19. Pourquoi dit-on que la VaR n'est pas une mesure de risque « cohérente » alors que l'expected shortfall l'est ?
20. Un modèle de VaR à 99 % compte 5 dépassements en 250 jours. Quelle zone du feu tricolore ? Le test de Kupiec rejette-t-il le modèle ? Et avec 10 dépassements ?
21. Qu'est-ce qu'un stress test inversé, et en quoi diffère-t-il d'un stress test classique ?
22. Pourquoi la VaR à 99,9 % d'une perte opérationnelle estimée sur dix ans de données est-elle peu fiable ?

### Cadre réglementaire (chapitre 4)

23. Avec la formule IRB des « autres expositions de détail » (corrélation donnée par la formule du texte), calculez le besoin de capital K et le poids de risque pour une PD de 2 % et une LGD de 45 % (quantile 99,9 %).
24. Qu'est-ce qu'un ratio de fonds propres et quel risque la formule IRB a-t-elle pour but de couvrir ?
25. Trois modules de risque ont pour charges 100, 60 et 40 ; leurs corrélations sont de 0,25 entre le premier et chacun des autres et de 0,5 entre les deux derniers. Quelle est la charge agrégée ? Quelles hypothèses cache cette formule ?
26. Les fonds propres éligibles valent 330 M€ et le capital de solvabilité requis 254 M€. Quel est le ratio de solvabilité ? Que se passerait-il en dessous de 100 % ?
27. Dans le Takaful, quels sont les deux fonds, et qui supporte un déficit du fonds des participants ?
28. Dans le modèle wakala, les cotisations de l'année valent 10 M€, la commission de gestion 20 % et les sinistres 6 M€ : quel est l'excédent technique, et à qui revient-il ?
29. Une règle de détection de blanchiment lève 54 alertes dont 38 fausses. Quelle est la précision ? Pourquoi une fenêtre de temps améliore-t-elle la règle ?

### Assurance vie (chapitre 5)

30. Avec un taux d'intérêt de 3 % et une rente viagère anticipée $\ddot a_x=18$, quelle est la valeur du capital décès $A_x$ ?
31. Un portefeuille compte 38 décès contre 50 attendus : quel est le rapport réel/attendu, et peut-on conclure que les assurés vivent plus longtemps que la population ?
32. Quelles contraintes d'identification impose-t-on au modèle de Lee–Carter, et pourquoi ?
33. Une baisse de la mortalité est-elle une bonne nouvelle pour un assureur de rentes ? Pour un assureur de capitaux décès ?

### Réassurance (chapitre 6)

34. Une tranche de 200 000 € en excédent de 100 000 € s'applique à trois sinistres de 50 000, 150 000 et 400 000 €. Que cède-t-on ?
35. Une cession en quote-part de 30 % porte sur 10 M€ de primes et 7 M€ de sinistres : quelles sont les primes et les sinistres conservés ?
36. Pourquoi le *burning cost* d'une tranche haute sous-estime-t-il souvent le coût réel quand on dispose de peu d'années ?

### Actif-passif et portefeuille (chapitre 7)

37. Un zéro-coupon de maturité 5 ans, taux de 5 % : quelles sont sa duration et sa duration modifiée ? De combien varie son prix si les taux montent d'un point ?
38. Un portefeuille est composé à 60 % d'un actif de volatilité 10 % et à 40 % d'un actif de volatilité 20 % ; leur corrélation est de 0,3. Quelle est la volatilité du portefeuille ? Comparez à la moyenne pondérée des volatilités.
39. Pourquoi l'égalité des durations de l'actif et du passif ne suffit-elle pas à immuniser le surplus quand l'actif ne vaut pas le passif ?
40. Pourquoi la diversification d'un portefeuille d'actions décevra-t-elle en période de crise ?

## Corrigés des questions

Pour les questions numériques, **calculons** plutôt que de nous fier à la mémoire.

```python
import numpy as np
from scipy.stats import norm, binom, chi2

print("Q1  Gini =", round(2 * 0.78 - 1, 2))
print("Q2  WOE =", round(np.log((300 / 9400) / (50 / 600)), 3))
f = 20 / np.log(2); off = 600 - f * np.log(50)
print("Q3  points pour 100 :", round(off + f * np.log(100), 1), "| pour 200 :", round(off + f * np.log(200), 1))
print("Q5  ECL 12 mois :", round(0.02 * 0.45 * 10000), "€ | durée de vie :", round(0.05 * 0.45 * 10000), "€")
mu6, sd6 = 1000 * 0.01, np.sqrt(1000 * 0.01 * 0.99)
print("Q6  écart réduit :", round((18 - mu6) / sd6, 2), "| p unilatérale :", round(binom.sf(17, 1000, 0.01), 4))
P = np.array([[0.90, 0.08, 0.02], [0.10, 0.80, 0.10], [0, 0, 1.0]])
print("Q7  PD à 2 ans :", round((P @ P)[0, 2], 3))
print("Q9  fréquence :", 120 / 2000, "| six mois :", 0.5 * 120 / 2000)
print("Q10 variance :", round(0.07 + 0.4 * 0.07 ** 2, 5), "| rapport :", round((0.07 + 0.4 * 0.07 ** 2) / 0.07, 3))
print("Q11 prime pure :", 0.066 * 5500, "| commerciale :", round(0.066 * 5500 / 0.72, 1))
f1, f2 = (150 + 168) / (100 + 110), 165 / 150
u = [165, 168 * f2, 120 * f1 * f2]
print("Q12 facteurs :", round(f1, 4), f2, "| provision :", round(u[1] - 168 + u[2] - 120, 1))
Z = 500 / (500 + 1000)
print("Q14 Z =", round(Z, 3), "| fréquence créditée :", round(Z * 0.05 + (1 - Z) * 0.066, 4))
z99 = norm.ppf(0.99)
print("Q17 VaR :", round(z99 * 2, 2), "% | ES :", round(2 * norm.pdf(z99) / 0.01, 2), "%")
print("Q18 VaR à 10 jours :", round(z99 * 2 * np.sqrt(10), 1), "%")
def kupiec(x, n=250, p=0.01):
    ph = x / n
    lr = -2 * ((n - x) * np.log(1 - p) + x * np.log(p) - (n - x) * np.log(1 - ph) - x * np.log(ph))
    return round(float(lr), 2), round(float(chi2.sf(lr, 1)), 4)
print("Q20 Kupiec (LR, p) : 5 dépassements", kupiec(5), "| 10 dépassements", kupiec(10))
pd_, lgd = 0.02, 0.45
w = (1 - np.exp(-35 * pd_)) / (1 - np.exp(-35)); rho = 0.03 * w + 0.16 * (1 - w)
K = lgd * (norm.cdf((norm.ppf(pd_) + np.sqrt(rho) * norm.ppf(0.999)) / np.sqrt(1 - rho)) - pd_)
print("Q23 corrélation :", round(rho, 4), "| K :", round(K, 4), "| poids de risque :", round(K * 12.5, 3))
c = np.array([100, 60, 40.]); R = np.array([[1, .25, .25], [.25, 1, .5], [.25, .5, 1]])
print("Q25 charge agrégée :", round(float(np.sqrt(c @ R @ c)), 1), "| somme :", c.sum())
print("Q26 ratio :", round(330 / 254 * 100), "%")
print("Q28 excédent :", 10 - 0.2 * 10 - 6, "M€")
print("Q29 précision :", round((54 - 38) / 54, 3))
d = 0.03 / 1.03
print("Q30 A_x =", round(1 - d * 18, 4))
print("Q31 A/E =", round(38 / 50, 2), "| intervalle de Poisson à 95 % :", round(chi2.ppf(0.025, 76) / 2 / 50, 2), "-", round(chi2.ppf(0.975, 78) / 2 / 50, 2))
cl = np.array([50e3, 150e3, 400e3])
print("Q34 cédé :", np.clip(cl - 100e3, 0, 200e3).tolist(), "= total", np.clip(cl - 100e3, 0, 200e3).sum())
print("Q35 primes conservées :", 10 * 0.7, "M€ | sinistres conservés :", round(7 * 0.7, 1), "M€")
print("Q37 duration modifiée :", round(5 / 1.05, 2), "| variation du prix :", round(-5 / 1.05, 2), "%")
wp, sg = np.array([.6, .4]), np.array([.10, .20])
var = (wp ** 2 * sg ** 2).sum() + 2 * wp[0] * wp[1] * 0.3 * sg[0] * sg[1]
print("Q38 volatilité :", round(np.sqrt(var) * 100, 2), "% | moyenne pondérée :", round(wp @ sg * 100, 1), "%")
```
<!--sortie-->
```text
Q1  Gini = 0.56
Q2  WOE = -0.96
Q3  points pour 100 : 620.0 | pour 200 : 640.0
Q5  ECL 12 mois : 90 € | durée de vie : 225 €
Q6  écart réduit : 2.54 | p unilatérale : 0.0138
Q7  PD à 2 ans : 0.046
Q9  fréquence : 0.06 | six mois : 0.03
Q10 variance : 0.07196 | rapport : 1.028
Q11 prime pure : 363.0 | commerciale : 504.2
Q12 facteurs : 1.5143 1.1 | provision : 96.7
Q14 Z = 0.333 | fréquence créditée : 0.0607
Q17 VaR : 4.65 % | ES : 5.33 %
Q18 VaR à 10 jours : 14.7 %
Q20 Kupiec (LR, p) : 5 dépassements (1.96, 0.1619) | 10 dépassements (12.96, 0.0003)
Q23 corrélation : 0.0946 | K : 0.0464 | poids de risque : 0.58
Q25 charge agrégée : 150.3 | somme : 200.0
Q26 ratio : 130 %
Q28 excédent : 2.0 M€
Q29 précision : 0.296
Q30 A_x = 0.4757
Q31 A/E = 0.76 | intervalle de Poisson à 95 % : 0.54 - 1.04
Q34 cédé : [0.0, 50000.0, 200000.0] = total 250000.0
Q35 primes conservées : 7.0 M€ | sinistres conservés : 4.9 M€
Q37 duration modifiée : 4.76 | variation du prix : -4.76 %
Q38 volatilité : 11.35 % | moyenne pondérée : 14.0 %
```

**1.** $\text{Gini}=2\times0{,}78-1=0{,}56$. Il mesure le **pouvoir de classement** : la probabilité qu'un mauvais payeur reçoive un score plus risqué qu'un bon, rééchelonnée entre 0 et 1. Il ne dit rien de la **calibration** (les probabilités prédites sont-elles les bonnes ?) ni de la valeur économique d'un seuil (1.3.2).

**2.** $\text{WOE}=\ln\dfrac{300/9\,400}{50/600}\approx-0{,}96$ (code ci-dessus). Un WOE **négatif** signifie que la classe pèse moins parmi les bons (3,2 %) que parmi les mauvais (8,3 %) : elle est **plus risquée** que l'ensemble (1.1.4).

**3.** 620 points pour 100 contre 1 et 640 pour 200 contre 1 : chaque doublement de la cote vaut un PDO de 20 points (1.1.5).

**4.** Parce que les effets réels sont **non linéaires** (âge en U, coude de l'endettement) : un découpage en classes les capte, alors qu'une logistique linéaire sur la variable brute impose une pente unique (1.2.3).

**5.** 90 € à douze mois (**étape 1**), 225 € sur la durée de vie (**étape 2**, après une dégradation sensible du risque depuis l'octroi). Dans l'étape 3 (prêt en défaut), la PD vaut 100 % (1.5.1, 1.5.4).

**6.** On attend 10 défauts, avec un écart-type de 3,15 ; 18 défauts donnent un écart réduit de 2,54 (probabilité unilatérale d'environ 1,4 %) : le modèle **sous-estime** le risque. À nuancer : le test binomial suppose les défauts indépendants ; un facteur commun (la conjoncture) augmente la variance et rend l'écart moins surprenant (1.3.7).

**7.** $0{,}90\times0{,}02+0{,}08\times0{,}10+0{,}02\times1=0{,}046$, soit 4,6 % (1.6.4) : le défaut est un état **absorbant**, on s'y retrouve en passant par « moyen ».

**8.** Une matrice estimée sur dix ans est une **moyenne** sur des années calmes et agitées. La conjoncture déforme la matrice (les baisses de note sont plus fréquentes en récession) : l'hypothèse d'**homogénéité** dans le temps est fausse, et il faut conditionner par la conjoncture (1.6.3, 1.6.5).

**9.** $120/2\,000=6\ \%$ ; $0{,}5\times0{,}06=0{,}03$ sinistre pour six mois : l'**exposition** multiplie la fréquence (2.1.2).

**10.** Variance $=0{,}07+0{,}4\times0{,}07^2=0{,}07196$ ; rapport $1{,}028$. À l'échelle d'une police, la sur-dispersion est **discrète** : un Poisson suffit presque, la binomiale négative n'apporte qu'une correction de quelques pour cent (2.1.3).

**11.** Prime pure $=0{,}066\times5\,500=363$ € ; prime commerciale $=363/0{,}72\approx504$ € (2.2.1, 2.2.4).

**12.** $f_1=(150+168)/(100+110)\approx1{,}514$, $f_2=165/150=1{,}1$ ; charges ultimes 165, 184,8 et 199,9, soit une provision de $0+16{,}8+79{,}9\approx96{,}7$ (2.3.3).

**13.** Parce qu'un tarif sert à **prédire l'avenir**. Un échantillon tiré au hasard mélange passé et futur, et ignore ce qui change dans le temps (inflation, composition du portefeuille) : il rend le modèle meilleur qu'il ne sera (2.2.5).

**14.** $Z=500/(500+1\,000)=1/3$ ; fréquence créditée $=\tfrac13\times5\ \%+\tfrac23\times6{,}6\ \%\approx6{,}07\ \%$ : un groupe de taille modeste est ramené vers la moyenne (2.4.4).

**15.** Quelques sinistres très gros dominent la moyenne et rendent la sévérité **instable**. On modélise la partie **écrêtée** (stable) et l'on **mutualise l'excédent** par un coefficient, ou on le transfère à un traité de réassurance (2.1.5, 6.2).

**16.** La **sélection adverse** : les assurés qui s'attendent à consommer beaucoup choisissent les garanties riches (dans les données, la part des assurés en affection de longue durée croît avec le niveau). L'**aléa moral** : à état de santé égal, une meilleure couverture fait consommer davantage (le coût moyen croît avec le niveau, même hors ALD) (2.6.3).

**17.** $\text{VaR}_{99\,\%}=2{,}326\times2\ \%\approx4{,}65\ \%$ ; $\text{ES}_{99\,\%}=\sigma\,\varphi(z)/(1-\alpha)\approx5{,}33\ \%$ (3.1.3, 3.1.7).

**18.** $4{,}65\ \%\times\sqrt{10}\approx14{,}7\ \%$. La règle suppose des pertes **indépendantes et de même loi** d'un jour à l'autre ; elle échoue quand elles sont autocorrélées ou que la volatilité change (3.1.6).

**19.** La VaR n'est pas **sous-additive** : on peut construire deux positions dont la VaR de la somme dépasse la somme des VaR (le contre-exemple à deux prêts de 3.1.8). L'expected shortfall l'est toujours, ce qui garantit que fusionner deux portefeuilles ne **crée** pas de risque.

**20.** 5 dépassements : zone **orange** (le vert va jusqu'à 4) ; Kupiec : $LR=1{,}96$, $p\approx0{,}16$ : on **ne rejette pas**. Avec 10 : zone **rouge**, $LR\approx12{,}96$, $p<0{,}001$ : rejet. Un test sur 250 jours a une faible **puissance** (3.4.2, 3.4.5, 3.4.6).

**21.** On part d'un **événement inacceptable** (capital sous le minimum, par exemple) et l'on cherche les scénarios qui y mènent, au lieu de prendre un scénario et de mesurer sa perte (3.2.7).

**22.** Le quantile à 99,9 % d'une perte agrégée dépend de la **queue**, ajustée sur quelques dizaines de grosses pertes : l'indice de queue a un intervalle très large et la VaR varie de plus de 50 % selon la graine du Monte-Carlo (3.3.3).

**23.** $\rho\approx9{,}5\ \%$, $K\approx4{,}6\ \%$, soit un poids de risque d'environ **58 %** ($K\times12{,}5$) (4.1.4, 4.1.5). La formule couvre la **perte inattendue** au quantile 99,9 % à un an ; la perte attendue est provisionnée.

**24.** Le **ratio de fonds propres** est le rapport des fonds propres aux actifs pondérés par le risque ; il doit rester au-dessus de minima fixés par le cadre (4.1.2). La formule IRB sert à calculer le **capital** qui absorbe les pertes inattendues dans les cas extrêmes (4.1.4).

**25.** $\sqrt{c^\top R\,c}\approx150{,}3$, contre 200 pour la somme : le **bénéfice de diversification** vaut près de 25 %. La formule suppose des dépendances **linéaires et constantes** et n'est exacte que pour des pertes normales ; avec des marges asymétriques ou une dépendance de queue, la charge peut être plus élevée (4.2.4, 4.2.5).

**26.** $330/254\approx130\ \%$. Sous 100 %, les fonds propres ne couvrent plus le capital requis : le cadre prévoit des **mesures d'intervention** du contrôleur (plan de rétablissement, par exemple) (4.2.6) ; les seuils exacts relèvent du texte applicable.

**27.** Le **fonds des participants** (cotisations, sinistres) et le **fonds de l'opérateur** (commissions, capital). Un déficit du fonds des participants est comblé par un **prêt sans intérêt** (*qard hassan*) de l'opérateur, remboursé par les excédents futurs (4.3.2, 4.5.4).

**28.** Excédent technique $=10-0{,}2\times10-6=2$ M€ : la commission de 2 M€ revient à l'opérateur, et l'excédent appartient au **fonds des participants** (distribué ou mis en réserve selon les règles du contrat) (4.5.1, 4.5.2).

**29.** Précision $=(54-38)/54\approx0{,}30$. Le fractionnement est un **comportement rapproché dans le temps** : sans fenêtre, la règle accumule les dépôts de l'année entière et déclenche pour des commerces légitimes ; limitée à 14 jours, elle cible le schéma (4.6.3).

**30.** $A_x=1-d\,\ddot a_x=1-0{,}0291\times18\approx0{,}476$, soit 0,476 € de capital décès par euro assuré (5.2.2).

**31.** $38/50=0{,}76$, mais l'intervalle de Poisson à 95 % (de 0,54 à 1,04) **contient 1** : avec si peu de décès, on ne peut pas conclure à une surmortalité ou à une sous-mortalité (5.1.5).

**32.** $\sum_x b_x=1$ et $\sum_t k_t=0$ : sans ces contraintes, on peut multiplier $b_x$ par une constante et diviser $k_t$ par elle, ou translater $k_t$ en corrigeant $a_x$ (**non-identifiabilité**) (5.3.1).

**33.** Mauvaise nouvelle pour un assureur de **rentes** (on paie plus longtemps), bonne pour un assureur de **capitaux décès** (on paie plus tard et moins souvent) (5.2.5).

**34.** Les trois sinistres cèdent 0, 50 000 et 200 000 € : **250 000 €** au total (le troisième épuise la tranche : 400 000 − 100 000 > 200 000) (6.1.3).

**35.** On conserve 70 % : **7 M€** de primes et **4,9 M€** de sinistres (la réassurance proportionnelle ne change pas le ratio S/P, hors commissions) (6.1.2).

**36.** Une tranche haute n'est touchée que par des sinistres **rares** : sur peu d'années, l'expérience en contient peu ou pas, et l'estimation est très instable (une erreur de l'ordre de 30 % sur une tranche haute dans le chapitre) ; on s'appuie alors sur une loi de queue et sur la tarification par l'exposition (6.2.1, 6.2.3, 6.2.4).

**37.** Un zéro-coupon à 5 ans a une duration de **5 ans**, une duration modifiée de $5/1{,}05\approx4{,}76$ ; si les taux montent d'un point, le prix baisse d'environ **4,76 %** (approximation de premier ordre) (7.1.2).

**38.** $\sigma_p=\sqrt{0{,}6^2\times0{,}1^2+0{,}4^2\times0{,}2^2+2\times0{,}6\times0{,}4\times0{,}3\times0{,}1\times0{,}2}\approx11{,}35\ \%$, contre 14 % pour la moyenne pondérée : c'est la **diversification** (7.2.1).

**39.** La variation du surplus est $A\,D_A-L\,D_L$ (en proportion du choc de taux) : elle s'annule si $D_A\,A=D_L\,L$, c'est-à-dire si les **sensibilités en euros** sont égales, pas les durations (7.1.4).

**40.** En crise, les **corrélations montent** : les actions chutent ensemble, et la diversification promise par des corrélations estimées en période calme disparaît (7.2.7, 3.2.8).

## Votre grille d'auto-évaluation

Pour chaque ligne : **je sais l'expliquer** / **je sais le faire** / **à revoir**.

| Compétence | Où la retravailler |
|---|---|
| Construire une grille de score et lire une carte de score | 1.1 |
| Comparer des modèles de défaut et expliquer un refus | 1.2 |
| Mesurer un score : Gini, KS, calibration, stabilité | 1.3 |
| Calculer un WOE et une IV, regrouper de façon monotone | 1.4 |
| Chiffrer une perte attendue (PD, LGD, EAD, étapes IFRS 9) | 1.5 |
| Estimer et utiliser une matrice de transition | 1.6 |
| Modéliser fréquence et sévérité, gérer la queue | 2.1 |
| Construire et valider un tarif | 2.2, 2.4 |
| Provisionner par chain ladder et juger l'incertitude | 2.3, 2.5 |
| Raisonner sur l'assurance santé | 2.6 |
| Calculer et comparer VaR et ES | 3.1 |
| Concevoir un stress test | 3.2 |
| Chiffrer risque opérationnel, marché, liquidité | 3.3 |
| Backtester et valider un modèle | 3.4 |
| Appliquer la logique de Bâle (IRB) | 4.1 |
| Appliquer la logique de Solvabilité (SCR, solvabilité) | 4.2 |
| Expliquer le Takaful et répartir un excédent | 4.3, 4.5 |
| Situer IFRS 17 et les réformes de Bâle | 4.4 |
| Détecter le blanchiment et la fraude | 4.6 |
| Construire une table de mortalité, calculer primes et provisions de vie | 5.1, 5.2 |
| Modéliser la mortalité avec Lee–Carter | 5.3 |
| Tarifer et choisir un traité de réassurance | 6 |
| Gérer l'actif et le passif, optimiser un portefeuille | 7 |
| Mener un projet de tarification validé de bout en bout | Projet du volume |
