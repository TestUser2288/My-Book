## 1.2 Analyse bivariée et multivariée

> **La question de la gérante.** « Les jours où je dépense plus en publicité, je vends plus. Et mes clients du site n'achètent pas comme ceux de la boutique, non ? »

Une fois chaque variable comprise seule, on les regarde **deux à deux** (analyse **bivariée**), puis **trois ou plus** (analyse **multivariée**). Le but n'est pas encore de prouver une cause, mais de repérer les **relations** et de formuler des questions précises. La méthode dépend, encore, du type des deux variables.

| Variable 1 | Variable 2 | Dessin | Résumé |
|---|---|---|---|
| Quantitative | Quantitative | nuage de points, courbe lissée | corrélation (Pearson, Spearman) |
| Quantitative | Qualitative | boîtes par groupe, moyennes avec intervalle | moyenne et médiane par groupe |
| Qualitative | Qualitative | tableau croisé, barres empilées | profils lignes, taux par groupe |

### 1.2.1 Deux variables quantitatives : nuage et corrélation

Reprenons la remarque de la gérante : les commandes du jour dépendent-elles de la dépense publicitaire du jour ? Chaque jour est un point.

```python
print("corrélation commandes - publicité :", round(j["depense_pub"].corr(j["nb_commandes"]), 2), "(Pearson),", round(j["depense_pub"].corr(j["nb_commandes"], method="spearman"), 2), "(Spearman)")
print("corrélation commandes - température :", round(j["temperature_moy"].corr(j["nb_commandes"]), 2), "(Pearson),", round(j["temperature_moy"].corr(j["nb_commandes"], method="spearman"), 2), "(Spearman)")
```
<!--sortie-->
```text
corrélation commandes - publicité : 0.53 (Pearson), 0.38 (Spearman)
corrélation commandes - température : -0.21 (Pearson), -0.15 (Spearman)
```

```python hide
O.fig_nuages()
```
<!--sortie-->
```text
figure : ch01-nuages.png
```

![Commandes du jour contre la dépense publicitaire du jour (à gauche) et contre la température (à droite), avec une courbe lissée.](figures/ch01-nuages.png)

À gauche, le nuage est incliné vers le haut : la corrélation de Pearson est de 0,53. La **courbe lissée** (une régression locale, qui suit la tendance sans imposer de droite) montre que la relation n'est pas une droite parfaite : presque plate sous 200 € de dépense, puis montante. À droite, la température donne un nuage en forme de « montagne » : peu de commandes quand il fait très froid ou très chaud, un maximum vers 10 °C. La corrélation vaut −0,21 : un seul nombre résume mal une relation qui monte puis redescend.

> 💡 **Pearson, Spearman, et un dessin.** Le coefficient de **Pearson** mesure à quel point les points s'alignent sur une **droite**. Celui de **Spearman** utilise seulement les **rangs** : il mesure si la relation est **monotone** (toujours croissante ou toujours décroissante), droite ou non, et il est moins sensible aux valeurs extrêmes. Quand les deux diffèrent beaucoup (ici 0,53 et 0,38 pour la publicité), c'est un signal : la relation n'est pas une droite, ou quelques jours extrêmes pèsent lourd. **Dessinez toujours le nuage avant de croire un coefficient** : le volume I l'a montré avec les jeux d'Anscombe.

Voici le point le plus important de cette section. La corrélation de 0,53 entre dépense publicitaire et commandes **ne dit pas** que la publicité fait vendre. Les deux variables dépendent peut-être d'une troisième : **la saison**. La gérante dépense davantage en novembre et décembre, et c'est aussi quand on vend le plus. Vérifions en comparant « à mois égal » : on retire de chaque variable la moyenne de son mois.

```python
j2 = j.assign(mois=j["date"].dt.month)
for c in ["depense_pub", "nb_commandes", "temperature_moy"]:
    j2[c + "_ecart"] = j2[c] - j2.groupby("mois")[c].transform("mean")
print("commandes - publicité, à mois égal :", round(j2["depense_pub_ecart"].corr(j2["nb_commandes_ecart"]), 2))
print("commandes - température, à mois égal :", round(j2["temperature_moy_ecart"].corr(j2["nb_commandes_ecart"]), 2))
```
<!--sortie-->
```text
commandes - publicité, à mois égal : 0.1
commandes - température, à mois égal : -0.04
```

La corrélation avec la publicité tombe de 0,53 à 0,10 ; celle avec la température de −0,21 à −0,04. **La plus grande partie du lien venait de la saison.** Il reste un faible lien résiduel (0,10) pour la publicité. Est-il causal ? Le volume I a posé la question ; nous y reviendrons avec les outils du chapitre 3. L'exploration, elle, a fait son travail : elle a transformé la question (« la publicité fait-elle vendre ? ») en une autre, plus précise (« **à saison égale**, quel est l'effet d'une dépense supplémentaire ? »).

### 1.2.2 Une variable quantitative et une variable qualitative : comparer des groupes

Comparer un montant selon une catégorie est la question la plus courante d'un analyste : le panier selon le canal, le délai selon le transporteur, la dépense selon le segment. On dessine une **boîte par groupe**, côte à côte, sur le même axe, et l'on résume par la **moyenne avec son intervalle de confiance**.

```python
g = cmd.groupby("canal")["panier"].agg(["mean", "median", "std", "count"])
g["demi_intervalle"] = 1.96 * g["std"] / np.sqrt(g["count"])
print(g.round(2).to_string())
t = liv.groupby("transporteur")["delai"].agg(["mean", "median", "std", "count"])
t["demi_intervalle"] = 1.96 * t["std"] / np.sqrt(t["count"])
print(t.round(2).to_string())
```
<!--sortie-->
```text
            mean  median    std  count  demi_intervalle
canal                                                  
Boutique  100.90   79.80  80.87  16975             1.22
Réseaux   100.52   79.70  81.48   3957             2.54
Site       99.77   79.76  80.39  15463             1.27
                mean  median   std  count  demi_intervalle
transporteur                                              
Transporteur A  5.21     5.0  1.35   8734             0.03
Transporteur B  5.82     6.0  1.32   6915             0.03
Transporteur C  6.68     7.0  1.33   3771             0.04
```

```python hide
O.fig_groupes()
```
<!--sortie-->
```text
figure : ch01-groupes.png
```

![Panier par canal (à gauche) et délai de livraison par transporteur (à droite) : deux comparaisons de groupes.](figures/ch01-groupes.png)

Deux comparaisons, deux conclusions opposées.

- **Le panier selon le canal.** Les trois boîtes sont presque identiques. Les moyennes (100,9 € en boutique, 99,8 € sur le site, 100,5 € pour les réseaux) diffèrent de moins de 1,2 €, et leurs intervalles (±1,2 €, ±1,3 € et ±2,5 €) se **recouvrent largement** : on ne peut pas dire que les trois canaux ont des paniers différents. Une absence de différence est un résultat : la gérante peut cesser de se demander si « les clients du site dépensent moins ».
- **Le délai selon le transporteur.** Les moyennes (5,2 ; 5,8 et 6,7 jours) sont séparées de plus de 0,5 jour, et les intervalles (±0,03 à ±0,04 jour) ne se recouvrent pas du tout : la différence est **nette**. Le transporteur C livre en moyenne un jour et demi après le transporteur A, et 9,1 % de ses livraisons dépassent 8 jours, contre 1,7 % pour A. Voilà une vraie piste, que le chapitre 11 poursuivra.

> 🧭 **En pratique : lire un intervalle.** Quand deux intervalles de confiance **ne se recouvrent pas**, la différence est probablement réelle. Quand ils se recouvrent largement, on ne peut rien affirmer (c'est la logique des tests du chapitre 2). Le cas intermédiaire (léger recouvrement) demande un test : ne concluez pas à l'œil.

### 1.2.3 Deux variables qualitatives : tableaux croisés et profils

Pour deux variables qualitatives, on construit un **tableau croisé**, puis on le lit en **pourcentages par ligne** (le profil de chaque groupe), pas en effectifs bruts. Les effectifs dépendent de la taille des groupes ; les profils les comparent à armes égales.

```python
print((pd.crosstab(cmd["canal"], cmd["mode_livraison"], normalize="index") * 100).round(1).to_string())
```
<!--sortie-->
```text
mode_livraison  Domicile  Point relais  Retrait magasin
canal                                                  
Boutique             0.0           0.0            100.0
Réseaux             54.7          38.4              6.9
Site                55.4          37.5              7.1
```

```python hide
O.fig_profils()
```
<!--sortie-->
```text
figure : ch01-profils.png
```

![Mode de livraison selon le canal, en pourcentage des commandes de chaque canal.](figures/ch01-profils.png)

Le tableau est très contrasté : **toutes** les commandes de la boutique sont en retrait magasin (c'est la définition du canal), alors que le site et les réseaux ont des profils presque identiques (55 % à domicile, 37 à 38 % en point relais, 7 % en retrait). Cette relation est **structurelle** : elle ne nous apprend rien, elle vérifie que les données respectent une règle de l'entreprise. C'est aussi un rôle de l'exploration.

Deux autres tableaux croisés sont plus instructifs.

```python
lc = lig.merge(cmd[["id_commande", "canal"]], on="id_commande")
lc["retourne"] = lc["id_ligne"].isin(ret["id_ligne"])
print((lc.groupby("canal")["retourne"].mean() * 100).round(1).to_dict())
print((pd.crosstab(cmd["canal"], cmd["code_promo"].replace("", "aucun"), normalize="index") * 100).round(1).to_string())
```
<!--sortie-->
```text
{'Boutique': 3.1, 'Réseaux': 6.7, 'Site': 9.0}
code_promo  BIENVENUE  FIDELITE  SOLDES  aucun
canal                                         
Boutique          0.9       6.4     8.3   84.4
Réseaux           0.7       6.6     8.8   83.9
Site              0.9       7.0     8.1   84.1
```

Le **taux de retour** (part des lignes renvoyées) dépend fortement du canal : 3,1 % en boutique, 6,7 % pour les réseaux, 9,0 % sur le site. Le **code promo**, en revanche, est utilisé de la même façon partout : 84 % sans code dans chaque canal, `SOLDES` entre 8,1 % et 8,8 %. Comment dire, sans test, si un écart est « grand » ? On résume la **force** de la liaison entre deux qualitatives par un indicateur qui varie de 0 (indépendance) à 1 (liaison parfaite), le *V de Cramér*, construit à partir du **khi-deux** :

```python
from scipy.stats import chi2_contingency
def cramer(t):
    chi2 = chi2_contingency(t)[0]
    return (chi2 / (t.values.sum() * (min(t.shape) - 1))) ** 0.5
print("canal et retour :", round(cramer(pd.crosstab(lc["canal"], lc["retourne"])), 3), "| canal et code promo :", round(cramer(pd.crosstab(cmd["canal"], cmd["code_promo"])), 3))
```
<!--sortie-->
```text
canal et retour : 0.118 | canal et code promo : 0.01
```

La liaison canal-retour (0,118) est **plus de dix fois** plus forte que la liaison canal-promo (0,010) : le canal compte pour comprendre les retours, pas pour comprendre l'usage des codes. Le test du khi-deux, qui dit si une liaison est plus grande que ce que le hasard produirait, est présenté au chapitre 2 ; retenez pour l'instant que **plus l'effectif est grand, plus le test détecte de petites liaisons** : un indicateur de force comme le V de Cramér se lit mieux qu'une probabilité.

### 1.2.4 Trois variables ou plus

Dès que l'on croise trois variables, deux outils prennent le relais : les **couleurs et les facettes** (des petits graphiques côte à côte, un par groupe) pour **voir** ; la **matrice de corrélation** pour **balayer** beaucoup de variables d'un coup.

```python
cols = ["nb_commandes", "chiffre_affaires", "temperature_moy", "pluie_mm", "promo_active", "depense_pub"]
print(j[cols].corr().round(2).to_string())
```
<!--sortie-->
```text
                  nb_commandes  chiffre_affaires  temperature_moy  pluie_mm  promo_active  depense_pub
nb_commandes              1.00              0.92            -0.21     -0.03          0.07         0.53
chiffre_affaires          0.92              1.00            -0.07     -0.04         -0.01         0.42
temperature_moy          -0.21             -0.07             1.00     -0.03         -0.08        -0.36
pluie_mm                 -0.03             -0.04            -0.03      1.00          0.03         0.03
promo_active              0.07             -0.01            -0.08      0.03          1.00         0.14
depense_pub               0.53              0.42            -0.36      0.03          0.14         1.00
```

```python hide
O.fig_correlations()
```
<!--sortie-->
```text
figure : ch01-correlations.png
```

![Matrice de corrélation des indicateurs journaliers.](figures/ch01-correlations.png)

La matrice se lit en cherchant les cases **foncées**, et en se méfiant de chacune. Ici :

- `nb_commandes` et `chiffre_affaires` sont presque redondants (0,92) : l'un s'explique par l'autre, inutile de les mettre ensemble dans une analyse.
- La **publicité** est liée aux commandes (0,53) et à la **température** (−0,36) : la gérante dépense davantage quand il fait froid, c'est-à-dire en fin d'année. Voilà le chemin de la confusion : la température n'agit pas sur la publicité, c'est la **saison** qui agit sur les deux.
- La **pluie** n'est liée à rien (de −0,04 à 0,03) : à cette échelle (le jour, toutes catégories), elle ne se voit pas.
- La **promotion** semble sans lien avec le chiffre d'affaires (−0,01) ; la section suivante montre que cette absence est trompeuse.

> ⚠️ **Piège : une matrice de corrélation ne dit pas les non-linéarités.** Une relation en « montagne » (la température) peut donner un coefficient proche de zéro. Une matrice **balaie**, elle ne **conclut** pas : chaque case qui intéresse mérite son nuage de points.

### 1.2.5 Le paradoxe de Simpson dans les vraies données

Voici le piège le plus déroutant de l'analyse bivariée. Comparons le chiffre d'affaires journalier moyen les jours **avec** et **sans** promotion.

```python
print("CA moyen par jour (€) :", j.groupby("promo_active")["chiffre_affaires"].mean().round(0).to_dict(), "| part des jours en promotion :", round(j["promo_active"].mean() * 100, 1), "%")
m = j2[j2["mois"].isin([1, 6, 7, 11])].groupby(["mois", "promo_active"])["chiffre_affaires"].mean().unstack().round(0)
m["écart (€)"] = m[1] - m[0]
print(m.rename(columns={0: "sans promotion", 1: "avec promotion"}).to_string())
```
<!--sortie-->
```text
CA moyen par jour (€) : {0: 3339.0, 1: 3300.0} | part des jours en promotion : 14.0 %
promo_active  sans promotion  avec promotion  écart (€)
mois                                                   
1                     2253.0          2601.0      348.0
6                     3338.0          3411.0       73.0
7                     3078.0          3283.0      205.0
11                    4224.0          4872.0      648.0
```

```python hide
O.fig_simpson()
```
<!--sortie-->
```text
figure : ch01-simpson.png
```

![Chiffre d'affaires journalier moyen avec et sans promotion : tous les jours confondus (à gauche), puis à mois égal (à droite).](figures/ch01-simpson.png)

Tous jours confondus, les jours de promotion rapportent **moins** (3 300 €) que les autres (3 339 €). On serait tenté de conclure que la promotion **détruit** du chiffre d'affaires. Mais regardez mois par mois : dans **chacun** des quatre mois qui contiennent à la fois des jours de promotion et des jours sans promotion (janvier, juin, juillet, novembre), les jours de promotion rapportent **plus** : +348 €, +73 €, +205 € et +648 €.

Comment les deux lectures peuvent-elles être vraies à la fois ? Parce que **la promotion n'est pas répartie au hasard dans l'année**. Elle tombe surtout en janvier et en juillet (soldes), deux mois creux, et seulement une semaine en novembre. Les jours « sans promotion » comprennent décembre, le meilleur mois de l'année, qui n'a **aucun** jour de promotion. Comparer des jours de promotion (plutôt en saison basse) à des jours sans promotion (dont la haute saison) compare des **populations différentes**. C'est le **paradoxe de Simpson** : une relation observée sur l'ensemble s'inverse (ou disparaît) quand on la regarde **dans chaque sous-groupe**.

> 💡 **Quel chiffre croire ?** Pour répondre à « la promotion fait-elle vendre ? », il faut comparer des jours **comparables** : ici, à mois égal, car la saison est la variable qui pèse sur tout le reste. Le chiffre agrégé est exact, mais il répond à une autre question (« en moyenne, les jours de promotion sont-ils meilleurs ? ») et c'est une **mauvaise** réponse à la première. La règle générale : quand un groupe n'est pas formé au hasard, **cherchez la variable qui détermine à la fois l'appartenance au groupe et le résultat**. On l'appelle une **variable de confusion**.

La **vérité programmée** de ces données est que la promotion augmente de 18 % le nombre de commandes d'un jour donné. Sur les quatre mois comparables, l'exploration retrouve une hausse du même sens (par exemple de 24 à 30 commandes en janvier, de 44 à 55 en novembre), mais pas encore son ampleur exacte : isoler un effet demande un modèle de régression, qui fait l'objet du chapitre 3.

### 1.2.6 Ce que l'exploration multivariée permet, et ce qu'elle ne permet pas

À l'issue de cette section, trois habitudes sont à retenir.

1. **Un coefficient ne remplace pas un dessin.** Dessinez le nuage, la boîte, le profil.
2. **Une relation n'est pas une cause.** Avant d'interpréter, demandez-vous quelle troisième variable peut agir sur les deux (la saison, le canal, la taille).
3. **Comparer, c'est comparer des comparables.** Quand les groupes ne sont pas formés au hasard, comparez **à variable de confusion égale** (à mois égal, à canal égal…), ou ajustez par un modèle.

> ✅ **À retenir.** Le type des deux variables décide du dessin et du résumé : nuage et corrélation (deux quantitatives), boîtes et moyennes avec intervalle (une de chaque), tableaux croisés et profils (deux qualitatives). Trois variables : facettes et matrice de corrélation. La saison explique l'essentiel du lien entre publicité et ventes ; le paradoxe de Simpson montre qu'un chiffre agrégé peut dire l'inverse de chaque sous-groupe.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.3 et 1.4, exercices 1.5 à 1.8.
