## 4.4 ➕ Pour aller plus loin : fréquence, sévérité, ratio sinistres/primes et ratio combiné

> 🧭 Section optionnelle.

La section 4.2 a montré que les moins de 25 ans perdent de l'argent. Elle n'a pas dit **pourquoi**, ni **de combien** le tarif devrait changer. Pour y répondre, on sépare le coût en deux morceaux (**fréquence** et **sévérité**), on les explique chacun par un **modèle linéaire généralisé** (GLM) qui tient compte de plusieurs caractéristiques à la fois, et l'on compare ce que le modèle dit du risque à ce que le tarif fait payer.

### 4.4.1 Pourquoi séparer fréquence et coût moyen

Le S/P d'un segment est le produit de trois quantités.

> 📐 **S/P = fréquence × coût moyen ÷ prime moyenne.**
> Comparer deux segments revient à comparer trois rapports : celui des fréquences, celui des coûts moyens, celui des primes.

Appliquons-le aux moins de 25 ans et aux 40-59 ans (2021-2024).

```python
t = O.table_sp(d, "classe_age")
t["prime_moy"] = t["primes"] / t["exposition"]
j, r = t.loc["< 25 ans"], t.loc["40-59 ans"]
print("fréquence x", round(j["frequence"] / r["frequence"], 2), "| coût moyen x", round(j["cout_moyen"] / r["cout_moyen"], 2), "| prime x", round(j["prime_moy"] / r["prime_moy"], 2))
print("S/P : x", round(j["sp"] / r["sp"], 2), "=", round(j["frequence"] / r["frequence"] * j["cout_moyen"] / r["cout_moyen"] / (j["prime_moy"] / r["prime_moy"]), 2))
```
<!--sortie-->
```text
fréquence x 4.39 | coût moyen x 1.31 | prime x 3.23
S/P : x 1.78 = 1.78
```

Un jeune conducteur a **4,4 fois plus de sinistres** qu'un conducteur de 40-59 ans, chaque sinistre coûte **1,3 fois plus** en moyenne, et sa prime n'est que **3,2 fois** plus élevée : le S/P est donc **1,8 fois** celui de l'autre segment (102 % contre 57,5 %). La fréquence explique l'essentiel de l'écart ; le coût moyen en rajoute un peu ; **la prime ne compense pas** assez.

### 4.4.2 Le GLM de Poisson avec exposition

Un nombre de sinistres est un **comptage** (0, 1, 2…) : on le modélise par une **loi de Poisson**. Le GLM de Poisson relie la fréquence attendue aux caractéristiques de la police par une **exponentielle** : chaque caractéristique **multiplie** la fréquence par un coefficient. C'est exactement ce que fait un tarif : un prix de base multiplié par des coefficients d'âge, de zone, de puissance.

> 📐 **Pour qui veut la formule.** Pour une police-année *i* d'exposition *e*ᵢ et de caractéristiques *x*ᵢ, on suppose que le nombre de sinistres *N*ᵢ suit une loi de Poisson d'espérance *e*ᵢ · exp(β₀ + β·*x*ᵢ). Autrement dit, ln E[*N*ᵢ] = ln(*e*ᵢ) + β₀ + β·*x*ᵢ : le terme ln(*e*ᵢ), sans coefficient à estimer, s'appelle un ***offset***. Il dit qu'**à risque égal, deux fois plus d'exposition donne deux fois plus de sinistres**. Le coefficient exp(β) d'une modalité est un **rapport de fréquences**, toutes les autres caractéristiques étant fixées.

Un exemple à la main. Si la fréquence de base (40-59 ans, zone A, usage privé, puissance 1) est de 4,0 % par année-police, et si les coefficients sont 2,8 pour les moins de 25 ans et 1,5 pour la zone C, la fréquence d'un jeune conducteur de la zone C est de 4,0 % × 2,8 × 1,5 = **16,8 %** : un sinistre tous les six ans en moyenne.

L'appel de bibliothèque tient en quelques lignes. La table de départ a **une ligne par police et par année** (2021-2024, ce qui laisse de côté l'année 2025, incomplète) avec le nombre de sinistres déclarés.

```python
import statsmodels.api as sm, statsmodels.formula.api as smf
base = O.police_annees(d)
f = "nb ~ C(classe_age, Treatment('40-59 ans')) + C(zone, Treatment('A')) + C(puissance) + C(usage, Treatment('Privé')) + np.log(bonus)"
mod = smf.glm(f, data=base, family=sm.families.Poisson(), offset=np.log(base["exposition"])).fit()
print(O.relativites(mod, "classe_age", "40-59 ans").round(2).to_string())
print(O.relativites(mod, "zone", "A").round(2).to_string())
```
<!--sortie-->
```text
             rapport   bas  haut
25-39 ans       1.20  1.10  1.31
60 ans et +     1.16  1.05  1.29
< 25 ans        2.84  2.56  3.16
40-59 ans       1.00  1.00  1.00
   rapport   bas  haut
B     1.19  1.08  1.30
C     1.51  1.38  1.66
D     1.80  1.63  1.99
A     1.00  1.00  1.00
```

```python hide
O.fig_glm(d)
disp = float((mod.resid_pearson ** 2).sum() / mod.df_resid)
print(round(disp, 3), round(float(mod.params["np.log(bonus)"]), 2))
```
<!--sortie-->
```text
figure : ch04-glm-age.png
1.021 1.36
```

![Rapport de fréquence de chaque tranche d'âge à la tranche 40-59 ans (GLM de Poisson, intervalle à 95 %) et écart de prix correspondant dans la grille de tarif.](figures/ch04-glm-age.png)

Les moins de 25 ans ont une fréquence **2,84 fois** celle des 40-59 ans (intervalle de 2,56 à 3,16), à zone, puissance, usage et bonus égaux. Les 25-39 ans sont à 1,20 et les 60 ans et plus à 1,16. Pour les zones, la zone D a 1,80 fois la fréquence de la zone A, la zone C 1,51 fois et la zone B 1,19 fois. L'élasticité du bonus-malus (le coefficient du logarithme) est estimée à 1,36, quand le simulateur en programme 1,5. Le **test de dispersion** (la statistique de Pearson divisée par les degrés de liberté vaut 1,02) montre qu'une loi de Poisson est un bon choix ici : s'il avait été nettement supérieur à 1, le modèle aurait sous-estimé l'incertitude et il aurait fallu une loi plus souple (binomiale négative, par exemple).

> 💡 **Pourquoi « toutes choses égales par ailleurs » compte.** Les jeunes conducteurs ont aussi un coefficient de bonus-malus plus élevé (moins d'expérience de conduite sans accident) : la comparaison brute de la fréquence mélange l'effet de l'âge et celui du bonus. Le GLM sépare les deux, comme la régression multiple du volume III, chapitre 3.

### 4.4.3 La sévérité : un modèle de Gamma

Le **coût d'un sinistre** est un nombre positif, asymétrique, à queue longue : on le modélise par une **loi Gamma** avec une fonction de lien logarithmique, ce qui donne, comme pour la fréquence, des **coefficients multiplicatifs**. Pour que les gros dommages corporels ne dominent pas l'estimation, nous nous limitons ici aux **sinistres matériels**, plus homogènes, et nous testons si la zone ou l'âge changent leur coût, ainsi qu'une tendance par année (l'inflation).

```python
mod_s = O.glm_severite(d)
ci = np.exp(mod_s.conf_int()).round(2)
ci.columns = ["bas", "haut"]
res = pd.concat([np.exp(mod_s.params).round(3).rename("rapport"), ci], axis=1).iloc[1:]
res.index = [i.split("[T.")[-1].rstrip("]") for i in res.index]
print(res.to_string())
```
<!--sortie-->
```text
             rapport   bas  haut
B              0.987  0.91  1.07
C              0.998  0.92  1.08
D              1.024  0.94  1.12
25-39 ans      0.962  0.89  1.04
60 ans et +    0.990  0.91  1.08
< 25 ans       0.980  0.91  1.06
annee_rel      1.024  0.99  1.05
```

**Aucun effet n'est détectable** : tous les intervalles contiennent 1. La zone D est estimée à +2 % (de −6 % à +12 %), alors que le simulateur programme +5 % pour les zones C et D : l'intervalle contient cette valeur, mais **aussi zéro**. La tendance annuelle est de **+2,4 %** par an (de −1 % à +5 %), ce qui est compatible avec l'inflation programmée de 4 % par an, et avec zéro. Avec environ 3 300 sinistres matériels et une dispersion forte, **les données ne permettent pas de conclure sur la sévérité**, alors que la fréquence se lit très nettement. C'est une leçon générale : le coût d'un sinistre est beaucoup plus difficile à expliquer que sa fréquence, et un modèle qui prétend le contraire avec peu de données est suspect.

> ⚠️ **Piège : conclure à l'absence d'effet.** Un intervalle qui contient 1 ne dit pas « il n'y a pas d'effet » : il dit « les données ne permettent pas de trancher ». Ici, une hausse de 5 % du coût par année est parfaitement compatible avec l'estimation, et c'est justement un écart de ce type qui fait glisser le S/P d'année en année.

### 4.4.4 Le tarif est-il suffisant ?

Comparons, tranche d'âge par tranche d'âge, **ce que coûte** une année-police (la prime pure observée) et **ce que le tarif fait payer**.

```python
t = O.table_sp(d, "classe_age").loc[["< 25 ans", "25-39 ans", "40-59 ans", "60 ans et +"]]
t["prime_moy"] = t["primes"] / t["exposition"]
t["prime_pure"] = t["sp"] * t["prime_moy"]
t["hausse_requise"] = t["sp"] / (1 - O.FRAIS) - 1
print(t[["prime_moy", "prime_pure"]].round(0).join((t["hausse_requise"] * 100).round(0)).to_string())
```
<!--sortie-->
```text
             prime_moy  prime_pure  hausse_requise
classe_age                                        
< 25 ans        1159.0      1183.0            42.0
25-39 ans        524.0       329.0           -13.0
40-59 ans        359.0       206.0           -20.0
60 ans et +      426.0       256.0           -16.0
```

Pour les moins de 25 ans, la prime moyenne (1 159 €) **égale** presque la prime pure (1 183 €) : il ne reste **rien** pour les frais, qui représentent 28 % de la prime. Pour que le ratio combiné atteigne 100 %, il faudrait un S/P de 72 %, donc une hausse de **42 %** de leur prime. Les 25-39 ans, au contraire, paient environ **13 % de trop** par rapport à l'équilibre, comme les 40-59 ans (**20 % de trop**) et les 60 ans et plus (**16 % de trop**) : ils **subventionnent** les moins de 25 ans.

> ⚠️ **Piège : en faire une recommandation brute.** Augmenter de 42 % la prime d'un segment fait fuir des clients, et ce sont **souvent les meilleurs risques de ce segment qui partent d'abord** (c'est la **sélection adverse**) : le S/P de ceux qui restent peut même **empirer**. Une recommandation sérieuse présente donc plusieurs scénarios (hausse progressive, hausse partielle accompagnée d'une franchise, action sur le bonus-malus), avec leur effet probable sur le volume, et reconnaît que **l'analyse montre le besoin**, pas la **réaction du marché**.

Quant à la dérive d'ensemble, elle se lit sur le ratio de l'ensemble du portefeuille. Le S/P ultime estimé par le chain ladder passe de 72,4 % (2024) à **77,3 %** (2025) ; pour ramener le ratio combiné à 100 % sur 2025, il faudrait une hausse moyenne des primes de l'ordre de **7 %**, **si** les coûts n'augmentent plus. Or l'inflation des coûts de 4 % par an, contre 2 % de revalorisation du tarif, fait monter le S/P d'environ **2 % par an en valeur relative** (près d'un point et demi de S/P).

```python hide
f_, cmp_ = O.comparer_provisions(d)
sp25 = float(cmp_.loc[2025, "ultime_cl"] / bil.loc[2025, "primes"])
print(round(sp25 * 100, 1), round((sp25 / (1 - O.FRAIS) - 1) * 100, 1), int(mod_s.nobs))
assert round(sp25 * 100, 1) == 77.3
```
<!--sortie-->
```text
77.3 7.4 3262
```

### 4.4.5 Le ratio combiné par segment, avec prudence

Le ratio combiné d'un segment se calcule comme celui de l'ensemble (S/P + frais). Mais **les frais ne sont pas répartis également** : un contrat vendu par un courtier ne coûte pas autant à acquérir qu'un contrat en agence, et un jeune conducteur demande plus de gestion de sinistres. Notre jeu de données suppose un taux de frais **uniforme** de 28 %, ce qui est une simplification : un ratio combiné par segment n'est donc qu'un **ordre de grandeur**. Les trois précautions de la section 4.1.6 s'appliquent : effectifs, intervalles, gros sinistres.

> ✅ **À retenir.** (1) Le S/P d'un segment se décompose en **fréquence × coût moyen ÷ prime moyenne** ; (2) un **GLM de Poisson avec offset d'exposition** donne des rapports de fréquence **toutes choses égales par ailleurs** ; le GLM de Gamma fait de même pour le coût, mais ce dernier est bien plus difficile à estimer ; (3) un intervalle qui contient 1 signifie « on ne sait pas », pas « pas d'effet » ; (4) comparer la prime pure à la prime facturée dit **quels segments sont sous-tarifés**, mais ne dit rien de la **réaction du marché** ; (5) un ratio combiné par segment dépend d'une **répartition des frais** qui est elle-même une hypothèse.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.6 (un GLM de fréquence et la lecture d'un tarif), exercices 4.9 et 4.10.
