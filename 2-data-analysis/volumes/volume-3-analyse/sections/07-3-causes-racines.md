## 7.3 Remonter aux causes

### 7.3.1 De « où » à « pourquoi »

La décomposition a localisé l'écart : beaucoup de **volume**, venu du **Site** ; une **marge unitaire** meilleure que prévu ; une **Boutique** en retrait. Elle n'a pas dit pourquoi. Passer de l'un à l'autre est le moment où l'analyste est le plus tenté de **raconter** plutôt que de **démontrer** : une histoire plausible (« c'est la météo », « les clients préfèrent le web ») est toujours disponible, et elle est souvent fausse.

Une méthode simple évite ce travers :

1. **Poser l'écart** avec précision (quoi, où, de combien).
2. **Lister les causes possibles** sans les juger (le diagramme d'Ishikawa, ci-dessous).
3. **Transformer chaque cause en hypothèse testable** : une affirmation qui peut être **fausse**, avec le test et les données qui permettraient de la réfuter.
4. **Tester**, avec les données disponibles, et noter le résultat tel qu'il est.
5. **Conclure avec le bon niveau de certitude**, et proposer des actions proportionnées.

### 7.3.2 Les cinq pourquoi

La technique des **cinq pourquoi** consiste à demander « pourquoi ? » à répétition, jusqu'à une cause sur laquelle on peut **agir** ou que l'on peut **tester**. Pour la Boutique, qui est à −6,5 % du budget de chiffre d'affaires :

| Niveau | Question | Réponse | Preuve |
|---|---|---|---|
| 1 | Pourquoi le chiffre d'affaires de la Boutique est-il sous le budget ? | Moins d'unités vendues que prévu | décomposition : l'effet volume domine |
| 2 | Pourquoi moins d'unités ? | Moins de commandes que prévu | nombre de commandes comparé au budget |
| 3 | Pourquoi moins de commandes ? | Des hypothèses : météo, promotions, ruptures, transfert vers le Site | à tester (7.3.4) |
| 4 | Pourquoi le budget en attendait-il plus ? | Il appliquait la même croissance à tous les canaux | règle de construction du budget, tendance passée |
| 5 | Pourquoi cette règle ? | Elle est simple et ne tient pas compte de la migration vers le Site | à documenter, à corriger |

Les « pourquoi » 1 et 2 se vérifient dans les chiffres. Le troisième ouvre des **hypothèses**, qu'il faut départager. Les deux derniers touchent à la **méthode de budget** : une cause racine fréquente d'un écart est que le budget lui-même reposait sur une hypothèse qui s'est révélée fausse.

> ⚠️ **Piège.** La méthode des cinq pourquoi est un **fil conducteur**, pas une preuve : à chaque marche, c'est vous qui choisissez « la » réponse. La règle est d'accompagner chaque marche d'une **preuve** (un chiffre, un test) ou de signaler qu'elle manque.

### 7.3.3 Le diagramme d'Ishikawa

Le diagramme d'Ishikawa (ou « arête de poisson ») range les causes possibles par **famille** autour d'un effet, pour s'assurer qu'on n'en oublie pas. Il ne démontre rien : c'est un outil d'**exploration**, qui précède les tests.

```python hide
O.ishikawa("ch07-ishikawa.png", {"Clients et canaux": ["Migration vers le Site", "Fréquentation du magasin"], "Prix et promotions": ["Hausse de tarif de janvier", "Calendrier des promotions"],
           "Produits et stock": ["Ruptures de stock", "Assortiment"], "Budget et méthode": ["Croissance uniforme", "Coût d'achat anticipé"],
           "Environnement": ["Météo (pluie)", "Calendrier (samedis)"], "Données": ["Définitions", "Retards d'enregistrement"]}, "Boutique sous le budget")
```
<!--sortie-->
```text
figure : ch07-ishikawa.png
```

![Diagramme d'Ishikawa de l'écart « Boutique sous le budget » : six familles de causes possibles.](figures/ch07-ishikawa.png)

### 7.3.4 Des hypothèses que l'on peut tester

Chaque branche du diagramme devient une **affirmation réfutable**. Prenons les plus plausibles et testons-les, avec les données de la boutique.

**H1. « La pluie a freiné la Boutique. »** Si elle l'a fait, 2025 doit compter **plus** de jours de pluie que 2024. **H2. « Il y a eu moins de promotions. »** Alors le nombre de jours de promotion doit avoir baissé.

```python
jours["annee"] = jours["date"].dt.year
jours["pluvieux"] = jours["pluie_mm"] > 1
print(jours.groupby("annee").agg(jours=("date", "size"), jours_pluvieux=("pluvieux", "sum"), jours_promo=("promo_active", "sum"), temperature=("temperature_moy", "mean")).round(1).loc[[2024, 2025]].to_string())
```
<!--sortie-->
```text
       jours  jours_pluvieux  jours_promo  temperature
annee                                                 
2024     366             111           51         12.9
2025     365              92           51         13.1
```

**Lecture.** 2025 compte **92** jours de pluie contre **111** en 2024, soit 19 de moins, et **51** jours de promotion les deux années ; la température moyenne est la même. **H1** et **H2** ne tiennent pas : la pluie aurait même dû aider la Boutique.

**H3. « Des ruptures de stock sur les produits phares ont fait perdre des ventes. »** Nous n'avons le stock quotidien que pour **2025** et pour **vingt produits** : on peut mesurer les ruptures, pas les comparer à l'année précédente.

```python
rupt = stock.groupby(stock["date"].dt.month)["rupture"].mean().mul(100).round(1)
print("jours-produits en rupture par mois (%) :", rupt.to_dict())
print("sur l'année :", round(stock["rupture"].mean() * 100, 1), "% des", len(stock), "jours-produits ; produits touchés :", stock.loc[stock["rupture"] == 1, "id_produit"].nunique(), "sur 20")
```
<!--sortie-->
```text
jours-produits en rupture par mois (%) : {1: 6.0, 2: 3.6, 3: 5.6, 4: 7.3, 5: 2.7, 6: 3.7, 7: 6.3, 8: 2.1, 9: 6.0, 10: 7.6, 11: 12.8, 12: 24.2}
sur l'année : 7.4 % des 7300 jours-produits ; produits touchés : 20 sur 20
```

**Lecture.** 7,4 % des 7 300 jours-produits sont en rupture, et les vingt produits sont touchés au moins une fois ; les ruptures se concentrent en novembre (12,8 %) et en décembre (24,2 %). C'est un vrai problème, mais le test ne peut pas relier ces ruptures à l'écart de la Boutique : il manque 2024 pour comparer et les ventes **perdues** ne sont pas observées. **H3 reste non démontrée.**

**H4. « Les clients de la Boutique sont passés au Site. »** Si c'est vrai, les clients qui achètent **les deux années** doivent avoir déplacé une part de leurs achats de la Boutique vers le Site. On compare, pour chaque client présent en 2024 et en 2025, la part de ses commandes passées en Boutique, avec un intervalle de confiance obtenu par rééchantillonnage des clients.

```python
x = cmd[cmd["annee"].isin([2024, 2025])]
deux = x.groupby("id_client")["annee"].nunique()
ids = deux[deux == 2].index
y = x[x["id_client"].isin(ids)].assign(boutique=lambda d: (d["canal"] == "Boutique").astype(int))
part = y.groupby(["id_client", "annee"])["boutique"].mean().unstack()
diff = part[2025] - part[2024]
graines = np.random.default_rng(0).integers(0, 10**6, 500)
boot = np.array([diff.sample(len(diff), replace=True, random_state=int(s)).mean() for s in graines])
print(len(ids), "clients présents les deux années | part Boutique : 2024", round(part[2024].mean() * 100, 1), "% ; 2025", round(part[2025].mean() * 100, 1), "%")
print("variation :", round(diff.mean() * 100, 1), "points | IC à 95 % :", np.round(np.percentile(boot, [2.5, 97.5]) * 100, 1))
```
<!--sortie-->
```text
2828 clients présents les deux années | part Boutique : 2024 46.8 % ; 2025 42.9 %
variation : -3.9 points | IC à 95 % : [-5.7 -2. ]
```

**Lecture.** Sur 2 828 clients présents les deux années, la part de leurs commandes passée en Boutique tombe de 46,8 % à 42,9 % : −3,9 points, avec un intervalle à 95 % de −5,7 à −2,0, qui **exclut zéro**. **H4** a résisté à un test qui pouvait la réfuter.

**H5. « Le budget supposait une croissance de la Boutique que l'historique ne justifiait pas. »** On compare la croissance **supposée** par le budget à la croissance **observée** avant 2025.

```python
lg = lig.merge(cmd[["id_commande", "annee", "canal"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
qte = lg.groupby(["annee", "canal"])["quantite"].sum().unstack()
hist = ((qte.loc[2024] / qte.loc[2023] - 1) * 100).round(1)
suppose = ((bud.groupby("canal")["quantite_budget"].sum() / qte.loc[2024] - 1) * 100).round(1)
realise = ((qte.loc[2025] / qte.loc[2024] - 1) * 100).round(1)
print(pd.DataFrame({"2024 contre 2023": hist, "supposée par le budget": suppose, "2025 réalisée": realise}).to_string())
```
<!--sortie-->
```text
          2024 contre 2023  supposée par le budget  2025 réalisée
canal                                                            
Boutique              -5.6                     4.1           -3.0
Réseaux                8.1                     4.1            8.0
Site                  19.2                     4.2           18.9
```

**Lecture.** Le budget supposait +4 % de quantités pour **chaque** canal. Or la Boutique avait **perdu** 5,6 % de quantités en 2024 (et en perdra 3,0 % en 2025), alors que le Site en gagnait 19,2 % (et 18,9 % en 2025). **H5** est établie : l'écart de la Boutique est, pour une grande part, une erreur de budget.

**H6. « Le budget anticipait une hausse des coûts d'achat qui n'a pas eu lieu. »** Elle expliquerait l'effet « coût » de la marge. Le coût d'achat unitaire est connu pour 2024 et 2025 ; celui que le budget suppose se déduit du budget lui-même (prix moyen hors taxe moins marge unitaire).

```python
cu = lg.assign(c=lg["quantite"] * lg["cout_achat"]).groupby("annee").agg(c=("c", "sum"), q=("quantite", "sum"))
cu["cout_unitaire"] = cu["c"] / cu["q"]
qb = bud["quantite_budget"].sum()
cout_budget = bud["ca_budget"].sum() / qb / (1 + TVA) - bud["marge_budget"].sum() / qb
print("coût d'achat par unité : 2024", round(cu.loc[2024, "cout_unitaire"], 2), "| supposé par le budget", round(cout_budget, 2), "| réalisé 2025", round(cu.loc[2025, "cout_unitaire"], 2))
print("hausse supposée :", round((cout_budget / cu.loc[2024, "cout_unitaire"] - 1) * 100, 1), "% | hausse réalisée :", round((cu.loc[2025, "cout_unitaire"] / cu.loc[2024, "cout_unitaire"] - 1) * 100, 1), "%")
```
<!--sortie-->
```text
coût d'achat par unité : 2024 18.99 | supposé par le budget 19.58 | réalisé 2025 19.13
hausse supposée : 3.1 % | hausse réalisée : 0.8 %
```

**Lecture.** Le coût d'achat par unité est passé de 18,99 € à 19,13 € (+0,8 %), alors que le budget en supposait 19,58 € (+3,1 %). **H6** est établie : elle explique les 0,48 € par unité de l'effet « coût ».

**H7. « L'effet prix vient d'une hausse de tarif du 1er janvier. »** Si le tarif a changé, le prix catalogue **d'un même produit** doit avoir augmenté d'une année à l'autre, dans tout le catalogue.

```python
tarif = lg.groupby(["id_produit", "annee"])["prix_unitaire"].median().unstack()
rapport = (tarif[2025] / tarif[2024]).dropna()
print("produits vendus les deux années :", len(rapport), "| rapport de prix 2025 / 2024 : médiane", round(rapport.median(), 3), "| min", round(rapport.min(), 3), "| max", round(rapport.max(), 3))
```
<!--sortie-->
```text
produits vendus les deux années : 120 | rapport de prix 2025 / 2024 : médiane 1.03 | min 1.03 | max 1.031
```

**Lecture.** Les 120 produits vendus les deux années ont un prix catalogue multiplié par 1,03 (de 1,030 à 1,031) : la hausse de tarif est **générale**. **H7** est établie ; elle est aussi ce que le budget attendait (de l'ordre de +3 % de prix moyen), d'où un effet prix modeste.

### 7.3.5 Corrélation, cause : ce que ces tests permettent de dire

Aucun de ces tests n'est une **expérience** : on n'a pas tiré au sort les clients qui passent au Site. Chaque test **réfute** ou **soutient** une hypothèse, selon trois niveaux de preuve (que le chapitre 2 a introduits avec la corrélation et la causalité) :

- une hypothèse **réfutée** par les données est écartée proprement (la prédiction ne s'est pas réalisée) ;
- une hypothèse **soutenue** a résisté à un test qui aurait pu la réfuter, mais d'autres explications restent possibles ;
- une hypothèse **non testable avec les données disponibles** reste, honnêtement, **non démontrée**.

Un test qui ne peut pas échouer ne prouve rien. Le test H4 aurait pu montrer que la part de la Boutique n'a **pas** bougé chez les mêmes clients ; il montre le contraire. Il ne prouve pas que le Site « prend » les clients de la Boutique (on n'a pas de groupe témoin), mais il rend l'hypothèse **probable** et écarte l'explication « la clientèle de la Boutique a disparu ».

### 7.3.6 Cinq pièges du raisonnement causal

Même avec de bons tests, cinq erreurs reviennent.

- **Le biais de confirmation.** On cherche des chiffres qui soutiennent l'histoire déjà choisie, et l'on s'arrête dès qu'on en trouve. Le remède est de **formuler d'abord** ce qui réfuterait l'hypothèse, comme on l'a fait pour H1 et H2.
- **Le « après donc à cause de ».** Le Site a progressé **en même temps** que la Boutique reculait : la coïncidence dans le temps ne prouve pas que l'un a causé l'autre. Les deux peuvent avoir une cause commune (un changement d'habitudes, une saison).
- **Les causes multiples.** Un écart a presque toujours **plusieurs** causes, de poids différents. Chercher « la » cause est un piège ; on cherche **les causes principales** et on chiffre leur part quand c'est possible (c'est le rôle de la décomposition).
- **La cause unique rassurante.** « C'est la météo » est confortable parce qu'elle ne demande aucune action. Une cause à laquelle on ne peut rien est suspecte : elle doit passer les mêmes tests que les autres.
- **Les données qui manquent.** L'absence de preuve n'est pas la preuve de l'absence : pour les ruptures de stock, on n'a pas conclu que « ce n'est pas la cause », on a conclu que **le test est impossible** avec les données actuelles.

Quand on **peut** agir, la meilleure preuve de causalité est une **expérience** : un test A/B (chapitre 2) tire au sort les clients ou les magasins, et supprime d'un coup les biais de sélection. Une analyse d'écart a posteriori ne le peut pas : elle **éclaire** une décision, elle ne la **prouve** pas.

### 7.3.7 Écrire la conclusion

La conclusion d'une analyse d'écart se présente en **tableau d'hypothèses**, avec un **statut** pour chacune, afin que le lecteur voie ce qui est établi et ce qui ne l'est pas.

| Hypothèse | Test | Résultat | Statut |
|---|---|---|---|
| H1 pluie | jours de pluie 2025 contre 2024 | moins de jours de pluie en 2025 | **rejetée** (elle aurait joué en sens inverse) |
| H2 promotions | jours de promotion | identiques | **rejetée** |
| H3 ruptures | taux de rupture 2025 | 7,4 % des jours-produits ; pas de comparaison possible | **non démontrée** |
| H4 transfert vers le Site | part Boutique des mêmes clients | −3,9 points, intervalle de −5,7 à −2,0 | **probable** |
| H5 budget irréaliste | croissance supposée contre historique | +4 % supposés, −5,6 % observés l'année d'avant | **établie** (c'est un fait du budget) |
| H6 coût d'achat | hausse supposée contre réalisée | +3,1 % supposés, +0,8 % réalisés | **établie** |
| H7 hausse de tarif | rapport des prix d'un même produit | rapport de 1,03 pour tout le catalogue | **établie** |

On y ajoute **ce qu'on ne sait pas** et **ce qu'il faudrait pour le savoir** : un historique de ruptures sur 2024, la décomposition du transfert (quels clients, quels produits), un groupe témoin si l'on teste une action.

### 7.3.8 Du constat à l'action

Une analyse d'écart qui n'aboutit à aucune décision a été inutile. On propose des **actions proportionnées au niveau de certitude** : une cause établie justifie un changement de méthode ; une cause probable, un test ou un suivi ; une cause non démontrée, une collecte de données.

| Action | Cause visée | Indicateur de suivi | Quand |
|---|---|---|---|
| Budgéter par canal, avec une croissance propre à chacun | H5 | écart de chaque canal au budget | prochain budget |
| Supposer le coût d'achat de l'année précédente, sauf contrat connu | H6 | coût unitaire réalisé contre budget | prochain budget |
| Suivre la part des commandes par canal et par client | H4 | part de la Boutique chez les clients fidèles | tous les mois |
| Historiser les ruptures de stock | H3 | taux de rupture par produit | dès maintenant |

> ✅ **À retenir.** Passer de « où » à « pourquoi » demande des **hypothèses réfutables** et des **tests**, pas des histoires. Une conclusion honnête classe chaque hypothèse (rejetée, probable, établie, non démontrée), dit ce qui manque, et propose des actions **proportionnées** à la certitude. Souvent, la cause racine d'un écart est dans le **budget** lui-même.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.5 et 7.6, exercices 7.8 à 7.10.
