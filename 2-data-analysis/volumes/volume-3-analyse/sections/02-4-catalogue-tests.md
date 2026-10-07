## 2.4 ➕ Pour aller plus loin : catalogue des tests statistiques

Cette section est un **catalogue de poche**. Pour chaque test classique : la question à laquelle il répond, ses conditions d'emploi, un exemple exécuté sur les données de la boutique, et la façon de lire le résultat. La section 2.1 en a présenté quatre ; nous ajoutons ici le khi-deux, l'ANOVA avec son test post hoc, et les tests de normalité, et nous rassemblons le tout dans un tableau de choix.

### 2.4.1 Le tableau de choix

| Test | Question | Variable(s) | Conditions principales | Alternative robuste |
|---|---|---|---|---|
| $t$ de Student / Welch | Deux moyennes diffèrent-elles ? | numérique, 2 groupes indépendants | pas de valeurs extrêmes, ou $n$ assez grand | Mann-Whitney, bootstrap |
| $t$ apparié | La moyenne des différences est-elle nulle ? | numérique, mesures appariées | différences à peu près symétriques | Wilcoxon |
| $z$ de deux proportions | Deux taux diffèrent-ils ? | binaire, 2 groupes | effectifs attendus ≥ 5 par case | Fisher |
| Khi-deux d'indépendance | Deux variables catégorielles sont-elles liées ? | 2 catégorielles | effectifs attendus ≥ 5 par case | Fisher, regrouper |
| Khi-deux d'ajustement | La répartition observée suit-elle une répartition donnée ? | 1 catégorielle | effectifs attendus ≥ 5 | test exact |
| ANOVA à un facteur | Plusieurs moyennes diffèrent-elles ? | numérique, 3 groupes ou plus | variances voisines, résidus à peu près normaux | Kruskal-Wallis |
| Mann-Whitney | Un groupe tend-il à avoir des valeurs plus grandes ? | numérique ou ordinale, 2 groupes | aucune condition de forme | — |
| Shapiro-Wilk | Les données sont-elles compatibles avec une loi normale ? | numérique | échantillon modéré | diagramme quantile-quantile |

> ⚠️ **Piège.** Tous ces tests supposent des observations **indépendantes** (une personne ne compte qu'une fois, un jour ne dépend pas du précédent). Cette condition est plus importante que la forme de la distribution, et c'est la plus souvent violée : séries temporelles, clients revenus plusieurs fois, sessions d'un même visiteur.

### 2.4.2 Student, Welch, et le test de normalité

Nous avons comparé en 2.1.6 le panier moyen des commandes du Site et de la Boutique avec le $t$ de Welch. Le test de **Shapiro-Wilk** vérifie la condition de normalité : son hypothèse nulle est que les données **sont** normales. On l'applique ici à 500 paniers pris au hasard.

```python
paniers = cmd.loc[cmd["date_commande"] >= "2025-01-01", ["canal", "panier"]]
echantillon = paniers.loc[paniers["canal"] == "Site", "panier"].sample(500, random_state=1)
w1, q1 = stats.shapiro(echantillon); w2, q2 = stats.shapiro(np.log(echantillon))
print(f"Shapiro, paniers : W = {w1:.3f}, p = {q1:.0e} | paniers en logarithme : W = {w2:.3f}, p = {q2:.0e}")
```
<!--sortie-->
```text
Shapiro, paniers : W = 0.833, p = 2e-22 | paniers en logarithme : W = 0.972, p = 3e-08
```

Dans les deux cas la p-valeur est minuscule (de l'ordre de $10^{-22}$ pour les montants, $10^{-8}$ pour leur logarithme) : les paniers ne sont **pas** normaux, ni même log-normaux. Faut-il abandonner le test $t$ ? Non : avec des milliers d'observations par groupe, le **théorème central limite** rend la **moyenne** approximativement normale même quand les données ne le sont pas. Ce n'est pas le test de normalité qui décide, mais la **taille de l'échantillon** et la présence de valeurs extrêmes. Pour des petits échantillons, regardez plutôt un histogramme et un diagramme quantile-quantile, et préférez un test non paramétrique ou un bootstrap.

> 💡 **Intuition.** Un test de normalité sur un grand échantillon rejette presque toujours, parce qu'il détecte des écarts minuscules à la normale. Sur un petit échantillon, il ne détecte presque rien. Il répond mal à la question que l'on se pose vraiment : « *mon test $t$ est-il fiable ?* ».

### 2.4.3 Le khi-deux d'indépendance et d'ajustement

Le **khi-deux d'indépendance** teste le lien entre deux variables **catégorielles** : il compare le tableau croisé observé à celui que l'on obtiendrait si les deux variables étaient indépendantes. Exemple : le **taux de retour** dépend-il du canal de vente ?

```python
l25 = lig.merge(cmd[["id_commande", "canal", "date_commande"]], on="id_commande")
l25 = l25[l25["date_commande"] >= "2025-01-01"].assign(retour=lambda t: t["id_ligne"].isin(ret["id_ligne"]).astype(int))
tableau = pd.crosstab(l25["canal"], l25["retour"])
khi, p, ddl, _ = stats.chi2_contingency(tableau)
print(tableau.assign(taux=(tableau[1] / tableau.sum(axis=1)).round(4)).to_string())
print("khi-deux :", round(khi, 1), "| ddl :", ddl, "| p =", f"{p:.0e}", "| V de Cramér :", round(np.sqrt(khi / tableau.values.sum()), 3))
```
<!--sortie-->
```text
retour        0     1    taux
canal                        
Boutique  12192   419  0.0332
Réseaux    3060   228  0.0693
Site      12699  1229  0.0882
khi-deux : 342.5 | ddl : 2 | p = 4e-75 | V de Cramér : 0.107
```

Les taux de retour sont de **3,3 %** en Boutique, **6,9 %** sur Réseaux et **8,8 %** sur le Site. Le khi-deux (342,5, deux degrés de liberté) rejette l'indépendance avec une p-valeur de l'ordre de $10^{-75}$. Le **V de Cramér** (0,11 ici) mesure l'**intensité** du lien, entre 0 et 1 : le lien est net, mais d'intensité modeste (le canal n'explique pas tout : la catégorie de produit, le prix, la saison jouent aussi).

Le **khi-deux d'ajustement** compare une répartition **observée** à une répartition **attendue**. Les commandes de 2025 sont-elles réparties de façon uniforme sur les sept jours de la semaine ?

```python
par_jour = pd.to_datetime(cmd.loc[cmd["date_commande"] >= "2025-01-01", "date_commande"]).dt.dayofweek.value_counts().sort_index()
ajust = stats.chisquare(par_jour.values)
print("commandes par jour (lundi → dimanche) :", par_jour.values.tolist(), "| khi-deux :", round(ajust.statistic, 1), "| p =", f"{ajust.pvalue:.0e}")
```
<!--sortie-->
```text
commandes par jour (lundi → dimanche) : [1765, 1692, 1788, 1805, 2077, 2607, 1212] | khi-deux : 578.4 | p = 1e-121
```

La répartition n'est évidemment pas uniforme : le samedi (2 607 commandes) pèse plus du double du dimanche (1 212). La **vérité programmée** (samedi +40 %, dimanche −35 %) se lit dans les comptes. Le test, ici, n'apprend rien que l'œil ne voie : il devient utile quand la répartition est plus subtile, ou quand il faut **chiffrer** l'écart à une répartition de référence.

### 2.4.4 L'ANOVA et le test post hoc de Tukey

L'**ANOVA** (analyse de la variance) étend le test $t$ à **trois groupes ou plus** : elle demande si **au moins une** moyenne diffère des autres. Elle compare la variation **entre** les groupes à la variation **à l'intérieur** des groupes : si la première est grande par rapport à la seconde, les groupes diffèrent. Exemple : le **montant d'une ligne de commande** dépend-il de la catégorie de produit ?

```python
cat = l25.merge(prod[["id_produit", "categorie"]], on="id_produit")
groupes = [g["montant"] for _, g in cat.groupby("categorie")]
f = stats.f_oneway(*groupes)
print(cat.groupby("categorie")["montant"].agg(lignes="size", moyenne="mean", mediane="median").round(1).to_string())
print("ANOVA : F =", round(f.statistic, 1), "| p =", f.pvalue, "| Kruskal-Wallis p =", stats.kruskal(*groupes).pvalue)
gm = cat["montant"].mean()
print("part de variance expliquée (eta²) :", round(sum(len(g) * (g.mean() - gm) ** 2 for g in groupes) / ((cat["montant"] - gm) ** 2).sum(), 3))
```
<!--sortie-->
```text
            lignes  moyenne  mediane
categorie                           
Bien-être     3675     32.0     26.7
Cuisine       5141     45.4     40.1
Décoration    5897     43.9     30.8
Jardin        5393     65.6     55.1
Maison        5300     57.5     50.4
Papeterie     4421     12.8     10.2
ANOVA : F = 1096.0 | p = 0.0 | Kruskal-Wallis p = 0.0
part de variance expliquée (eta²) : 0.155
```

La moyenne d'une ligne va de **12,8 €** (papeterie) à **65,6 €** (jardin) ; l'ANOVA donne $F=1\,096$ et une p-valeur nulle (en pratique inférieure à $10^{-300}$), le test de Kruskal-Wallis, version sans condition de forme, aussi. Environ **16 %** de la variance des montants s'explique par la catégorie (le $\eta^2$ de l'ANOVA).

L'ANOVA dit **qu'il y a** une différence, pas **entre quels groupes**. Pour le savoir, on compare les groupes **deux à deux**, mais avec une **correction** : avec six catégories, on fait 15 comparaisons, et sans correction on aurait presque une chance sur deux d'en trouver une « significative » par hasard. Le **test de Tukey** compare toutes les paires en gardant un risque global de 5 %.

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd
tk = pairwise_tukeyhsd(cat["montant"], cat["categorie"])
tab = pd.DataFrame(tk._results_table.data[1:], columns=tk._results_table.data[0])
print("paires comparées :", len(tab), "| paires différentes à 5 % :", int(tab["reject"].sum()))
print(tab.loc[~tab["reject"], ["group1", "group2", "meandiff", "p-adj"]].to_string(index=False))
```
<!--sortie-->
```text
paires comparées : 15 | paires différentes à 5 % : 14
 group1     group2  meandiff  p-adj
Cuisine Décoration   -1.5058  0.328
```

Sur 15 paires, **14** diffèrent ; la seule paire dont la différence n'est pas démontrée est **cuisine contre décoration** (1,5 € d'écart, p = 0,33). À l'inverse, la même ANOVA sur le **panier par canal** (Boutique, Site, Réseaux) donne $F=0{,}45$ et $p=0{,}64$ : aucune différence entre canaux, et le test de Tukey ne rejette aucune paire.

```python hide-code
paniers_canal = [g["panier"] for _, g in cmd[cmd["date_commande"] >= "2025-01-01"].groupby("canal")]
fc = stats.f_oneway(*paniers_canal)
tc = pairwise_tukeyhsd(cmd.loc[cmd["date_commande"] >= "2025-01-01", "panier"], cmd.loc[cmd["date_commande"] >= "2025-01-01", "canal"])
print("panier selon les trois canaux : F =", round(fc.statistic, 2), ", p =", round(fc.pvalue, 3), "| paires rejetées par Tukey :", int(tc.reject.sum()))
```
<!--sortie-->
```text
panier selon les trois canaux : F = 0.45 , p = 0.639 | paires rejetées par Tukey : 0
```

### 2.4.5 Mann-Whitney et Wilcoxon

Le test de **Mann-Whitney** (ou Wilcoxon-Mann-Whitney) compare **deux groupes indépendants** sans supposer de forme : il utilise les rangs. Exemple : le nombre de commandes par jour diffère-t-il entre les jours de promotion (153 jours) et les autres (943 jours) ?

```python
promo, normal = jours.loc[jours["promo_active"] == 1, "nb_commandes"], jours.loc[jours["promo_active"] == 0, "nb_commandes"]
print("moyenne :", round(promo.mean(), 1), "contre", round(normal.mean(), 1), "| médiane :", promo.median(), "contre", normal.median(), "| Mann-Whitney p =", round(stats.mannwhitneyu(promo, normal).pvalue, 3))
```
<!--sortie-->
```text
moyenne : 35.4 contre 32.8 | médiane : 31.0 contre 30.0 | Mann-Whitney p = 0.029
```

Les jours de promotion ont 35,4 commandes en moyenne contre 32,8 les autres jours (médianes 31 et 30), et le test donne $p=0{,}029$ : significatif, mais l'**écart brut** (+8 %) est bien inférieur à l'effet réel de la promotion (+18 %), parce que la promotion tombe en saison creuse (section 2.3.6). Cet exemple rappelle la limite de tout test **non apparié ni ajusté** : il compare des jours qui diffèrent aussi par la saison. Le **test de Wilcoxon** pour échantillons appariés (2.1.6) en est la version pour des mesures sur les mêmes unités.

> ✅ **À retenir.** Choisissez le test à partir de **trois questions** : quelle variable (binaire, numérique, catégorielle) ? combien de groupes ? les groupes sont-ils indépendants ou appariés ? Vérifiez ensuite l'**indépendance** des observations, la **taille** des effectifs et les **valeurs extrêmes**. La plupart des tests « robustes » donnent la même conclusion que leur version classique sur de grands échantillons : la vraie difficulté est de bien poser la question.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercice 2.12.
