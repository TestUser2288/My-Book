## 8.1 Pareto et analyse ABC

### 8.1.1 Un constat, pas une loi

À la fin du XIXᵉ siècle, l'économiste Vilfredo Pareto observe qu'environ 80 % des terres d'un pays appartiennent à environ 20 % de ses habitants. Le **principe de Pareto**, ou « règle des 80/20 », en a gardé son nom : *une petite part des causes produit la plus grande part des effets*. En entreprise, on le décline : 20 % des produits font 80 % du chiffre d'affaires, 20 % des clients 80 % des ventes, 20 % des défauts 80 % des réclamations.

C'est un **constat empirique**, pas une loi : les proportions 80 et 20 sont un ordre de grandeur souvent rencontré, parfois très loin de la réalité. L'analyse sérieuse ne **suppose** pas la règle, elle la **mesure**. C'est le premier travail de ce chapitre.

### 8.1.2 Calculer une courbe de Pareto

Le calcul tient en trois gestes : **classer** les éléments du plus grand au plus petit, **cumuler** leur part de la valeur totale, et **comparer** avec la part des éléments cumulés. La fonction `pareto` du chapitre fait ces trois choses. Appliquons-la au chiffre d'affaires de 2025 par produit, par client, et aux montants remboursés par produit.

```python
ca_produit = l25.groupby("id_produit")["montant"].sum()
ca_client = l25.groupby("id_client")["montant"].sum()
retours_2025 = l25[l25["retournee"]].merge(ret[["id_ligne", "montant_rembourse"]], on="id_ligne")
rembourse = retours_2025.groupby("id_produit")["montant_rembourse"].sum()
courbes = {"produits (CA)": O.pareto(ca_produit), "clients (CA)": O.pareto(ca_client), "produits (remboursements)": O.pareto(rembourse)}
for nom, d in courbes.items():
    top20 = d.loc[d["part_elements"] <= 20, "part_cumulee"].max()
    n80 = int((d["part_cumulee"] < 80).sum() + 1)
    print(f"{nom:28s} {len(d):5d} éléments | les 20 % premiers font {top20:5.1f} % | pour 80 % de la valeur : {n80} éléments ({n80 / len(d) * 100:.0f} %)")
```
<!--sortie-->
```text
produits (CA)                  120 éléments | les 20 % premiers font  51.0 % | pour 80 % de la valeur : 56 éléments (47 %)
clients (CA)                  3875 éléments | les 20 % premiers font  51.8 % | pour 80 % de la valeur : 1753 éléments (45 %)
produits (remboursements)      120 éléments | les 20 % premiers font  53.2 % | pour 80 % de la valeur : 54 éléments (45 %)
```

**Lecture.** Aucune des trois courbes ne vérifie la règle des 80/20. Les 20 % de produits les plus vendus font **51,0 %** du chiffre d'affaires, les 20 % de clients les plus dépensiers **51,8 %**, les 20 % de produits les plus remboursés **53,2 %** des remboursements. Pour atteindre 80 % du chiffre d'affaires, il faut 56 produits sur 120 (47 %) et 1 753 clients sur 3 875 (45 %). La concentration existe, mais elle est plus proche de « 50/20 » que de « 80/20 » : c'est une clientèle et un catalogue assez équilibrés. Vérifier avant de croire est exactement le but.

```python hide
O.courbe_pareto("ch08-pareto.png", list(courbes.values()), "Courbes de Pareto de 2025", list(courbes))
```
<!--sortie-->
```text
figure : ch08-pareto.png
```

![Courbes de Pareto : produits, clients et remboursements. La diagonale en pointillés représenterait une répartition parfaitement égale ; les traits fins marquent 20 % des éléments et 80 % de la valeur.](figures/ch08-pareto.png)

### 8.1.3 L'analyse ABC

L'analyse **ABC** transforme la courbe en **classes d'action**. On classe les éléments par valeur décroissante et l'on trace deux seuils sur la part cumulée, classiquement 80 % et 95 % :

- **A** : les éléments qui, cumulés, font les 80 premiers pour cent de la valeur ;
- **B** : ceux qui apportent les 15 pour cent suivants ;
- **C** : ceux qui apportent les 5 derniers pour cent.

La fonction `classes_abc` applique la règle : un élément est en A tant que la part cumulée **avant lui** est inférieure à 80 %, en B jusqu'à 95 %, en C ensuite.

```python
abc = O.classes_abc(ca_produit)
ca_total = ca_produit.sum()
tab = pd.DataFrame({"produits": abc.value_counts(), "part des produits %": (abc.value_counts() / len(abc) * 100).round(1),
                    "part du CA %": (ca_produit.groupby(abc).sum() / ca_total * 100).round(1)}).sort_index()
print(tab.to_string())
```
<!--sortie-->
```text
   produits  part des produits %  part du CA %
A        56                 46.7          80.6
B        32                 26.7          14.6
C        32                 26.7           4.8
```

**Lecture.** La classe A compte 56 produits (46,7 % du catalogue) pour 80,6 % du chiffre d'affaires ; la classe B, 32 produits pour 14,6 % ; la classe C, 32 produits pour 4,8 %. La classe A reste **nombreuse** : il n'y a pas une poignée de produits à protéger, mais près de la moitié du catalogue.

> 💡 **Intuition.** Les seuils 80 et 95 sont des **conventions**, pas des constantes de la nature. Ce qui compte, c'est l'idée : séparer ce qui pèse lourd (à protéger), ce qui pèse moyennement (à suivre) et ce qui pèse peu (à questionner). Les changer (70-90, 85-98) est légitime, à condition de le dire.

### 8.1.4 Ce qui distingue les classes

Une classe n'a d'intérêt que si elle **dit quelque chose** : ses éléments diffèrent-ils des autres par la marge, par les retours, par la catégorie ?

```python
a = l25.assign(classe=l25["id_produit"].map(abc))
carac = a.groupby("classe").agg(ca=("montant", "sum"), marge=("marge", "sum"), lignes=("id_ligne", "size"), retours=("retournee", "sum"), prix=("prix_unitaire", "mean"))
carac["taux de marge %"] = (carac["marge"] / (carac["ca"] / 1.2) * 100).round(1)
carac["taux de retour %"] = (carac["retours"] / carac["lignes"] * 100).round(1)
carac["prix moyen"] = carac["prix"].round(1)
print(carac[["taux de marge %", "taux de retour %", "prix moyen"]].to_string())
print(pd.crosstab(a.drop_duplicates("id_produit")["classe"], a.drop_duplicates("id_produit")["categorie"]).to_string())
```
<!--sortie-->
```text
        taux de marge %  taux de retour %  prix moyen
classe                                               
A                  38.0               6.3        52.0
B                  37.3               6.0        23.0
C                  39.6               6.7        10.4
categorie  Bien-être  Cuisine  Décoration  Jardin  Maison  Papeterie
classe                                                              
A                  4       12          14      12      14          0
B                  9        4           4       4       5          6
C                  7        4           2       4       1         14
```

**Lecture.** Les classes **ne se distinguent ni par la marge** (38,0 %, 37,3 % et 39,6 %) **ni par les retours** (6,3 %, 6,0 % et 6,7 %), mais par le **prix moyen** (52 €, 23 € et 10 €) et par la **catégorie** : la Papeterie fournit 14 des 32 produits C et aucun produit A, alors que la Décoration et la Maison apportent 14 produits A chacune. Le classement par chiffre d'affaires reflète surtout le **prix** du produit.

### 8.1.5 Classer sur le chiffre d'affaires ou sur la marge ?

Classer par chiffre d'affaires est le choix par défaut, mais ce n'est pas le plus **utile** : un produit qui fait beaucoup de chiffre d'affaires à très faible marge pèse moins qu'il n'y paraît. On refait l'analyse sur la **marge** et l'on croise les deux classements.

```python
marge_produit = l25.groupby("id_produit")["marge"].sum()
abc_marge = O.classes_abc(marge_produit)
croise = pd.crosstab(abc.rename("classe CA"), abc_marge.rename("classe marge"))
print(croise.to_string())
change = abc[(abc != abc_marge.reindex(abc.index))]
print("produits dont la classe change :", len(change), "sur", len(abc))
```
<!--sortie-->
```text
classe marge   A   B   C
classe CA               
A             50   6   0
B              4  26   2
C              0   2  30
produits dont la classe change : 14 sur 120
```

**Lecture.** Quatorze produits sur 120 changent de classe quand on passe du chiffre d'affaires à la marge : six produits A en chiffre d'affaires sont B en marge, quatre B sont A, deux B sont C et deux C sont B. Une grande majorité reste dans sa classe : ici, les deux critères sont proches, parce que les taux de marge varient peu d'un produit à l'autre.

### 8.1.6 Ajouter la régularité de la demande : ABC-XYZ

Deux produits de même classe A peuvent se vendre très différemment : l'un se vend **régulièrement** chaque mois, l'autre par à-coups (un pic en décembre). Pour gérer un stock, la **régularité** compte autant que le volume. L'analyse **XYZ** classe les produits selon le **coefficient de variation** de leurs ventes mensuelles (l'écart-type divisé par la moyenne) : X (demande régulière), Y (variable), Z (irrégulière).

```python
mensuel = l25.groupby(["id_produit", "mois"])["quantite"].sum().unstack(fill_value=0)
cv = mensuel.std(axis=1) / mensuel.mean(axis=1)
xyz = pd.cut(cv, [0, 0.45, 0.60, 10], labels=["X", "Y", "Z"], right=False)
print("coefficient de variation : médiane", round(cv.median(), 2), "| min", round(cv.min(), 2), "| max", round(cv.max(), 2))
print(pd.crosstab(abc.rename("ABC"), xyz.rename("XYZ")).to_string())
```
<!--sortie-->
```text
coefficient de variation : médiane 0.48 | min 0.25 | max 0.88
XYZ   X   Y   Z
ABC            
A    23  21  12
B    16   8   8
C    13  13   6
```

**Lecture.** La demande mensuelle des produits est assez régulière : le coefficient de variation a pour médiane 0,48 (de 0,25 à 0,88). Parmi les 56 produits A, 23 sont X (réguliers), 21 Y et 12 Z (irréguliers) : ces douze produits sont ceux qui demandent un stock de sécurité, alors que les produits AX se gèrent plus simplement.

Les seuils du coefficient de variation (ici 0,45 et 0,60) se choisissent **d'après la distribution observée** : les seuils « classiques » ne séparent rien quand tous les produits ont une saisonnalité commune, comme ici. Le croisement des deux classements donne **neuf cases**, chacune appelant une politique : un produit AX demande une **disponibilité** excellente et un stock tendu ; un produit AZ demande un stock de sécurité ou un réapprovisionnement rapide ; un produit CZ est un candidat à l'arrêt ou à la fabrication à la demande.

### 8.1.7 Les pièges de l'analyse ABC

**La période.** Une classe est une **photographie**. Un produit lancé en cours d'année, ou saisonnier, est mal classé sur douze mois. Il faut au moins vérifier la **stabilité** des classes d'une année à l'autre avant de décider.

```python
abc_24 = O.classes_abc(lg[lg["annee"] == 2024].groupby("id_produit")["montant"].sum())
passage = pd.crosstab(abc_24.rename("classe 2024"), abc.reindex(abc_24.index).rename("classe 2025"))
print(passage.to_string())
print("produits A en 2024 restés A en 2025 :", round((abc_24[abc_24 == "A"].index.isin(abc[abc == "A"].index)).mean() * 100, 1), "%")
```
<!--sortie-->
```text
classe 2025   A   B   C
classe 2024            
A            54   1   0
B             2  30   1
C             0   1  31
produits A en 2024 restés A en 2025 : 98.2 %
```

**Lecture.** 54 des 55 produits A de 2024 sont restés A en 2025 (98,2 %) ; deux produits B passent en A, un A passe en B.

Ici, les classes sont très stables, parce que la popularité des produits est programmée constante dans les données simulées. Dans la réalité, des changements de classe sont fréquents, et **leur nombre est en lui-même une information** (un assortiment qui bouge vite, des modes).

**Les seuils.** Le nombre de produits en classe A dépend du seuil, parfois beaucoup.

```python
for s in ((70, 90), (80, 95), (90, 98)):
    c = O.classes_abc(ca_produit, seuils=s)
    print("seuils", s, "->", c.value_counts().sort_index().to_dict())
```
<!--sortie-->
```text
seuils (70, 90) -> {'A': 43, 'B': 31, 'C': 46}
seuils (80, 95) -> {'A': 56, 'B': 32, 'C': 32}
seuils (90, 98) -> {'A': 74, 'B': 28, 'C': 18}
```

**Lecture.** Le nombre de produits en classe A va de **43** (seuils 70/90) à **74** (seuils 90/98) : le seuil est un **choix qui change les chiffres**, pas un détail.

**Les produits sans historique et les ex aequo.** Un produit sans vente n'apparaît pas dans le classement : à ajouter explicitement en classe C. Deux produits de même valeur à la frontière entre deux classes peuvent être traités différemment par l'ordre du tri : on le sait, on l'écrit.

**Le chiffre d'affaires n'est pas la valeur.** On l'a vu en 8.1.5 : une classe A en chiffre d'affaires n'est pas toujours une classe A en marge, et la **marge nette de frais** (stockage, retours, remises) peut encore changer le classement. Le bon critère dépend de la décision à prendre.

### 8.1.8 Un seul nombre pour la concentration : le coefficient de Gini

Dire « les 20 % premiers font 51 % » est parlant, mais cela dépend du seuil de 20 %. Un nombre unique résume **toute** la courbe : le **coefficient de Gini**. Il compare la courbe cumulée à la répartition parfaitement égale : il vaut 0 quand tous les éléments pèsent pareil, et se rapproche de 1 quand un seul élément pèse presque tout. (C'est le double de l'aire entre la diagonale et la courbe de Lorenz, la version « croissante » de la courbe de Pareto.)

```python
print("Gini : produits (CA)", round(O.gini(ca_produit), 2), "| clients (CA)", round(O.gini(ca_client), 2), "| produits (remboursements)", round(O.gini(rembourse), 2))
print("repère : 4 éléments de poids 1, 1, 1, 1 ->", round(O.gini([1, 1, 1, 1]), 2), "| de poids 0, 0, 0, 4 ->", round(O.gini([0, 0, 0, 4]), 2))
```
<!--sortie-->
```text
Gini : produits (CA) 0.48 | clients (CA) 0.49 | produits (remboursements) 0.5
repère : 4 éléments de poids 1, 1, 1, 1 -> 0.0 | de poids 0, 0, 0, 4 -> 0.75
```

**Lecture.** Les trois concentrations sont presque identiques (Gini de 0,48, 0,49 et 0,50) : modérées, loin du maximum théorique ($1-1/n$, soit 0,75 pour quatre éléments dont un seul pèse tout). Le repère à quatre éléments aide à lire l'échelle : 0 pour une répartition égale, 0,75 quand un seul élément sur quatre pèse tout.

Le Gini permet de **comparer des concentrations** entre périodes, catégories ou entreprises sans choisir de seuil. Un Gini qui grimpe d'une année à l'autre signale une dépendance croissante à quelques produits ou quelques clients : un **risque**, pas seulement une statistique.

### 8.1.9 Qui sont les clients A ?

La même analyse s'applique aux clients. Une fois les classes construites, on regarde ce qui distingue les clients A des autres : fréquence d'achat, panier, canal.

```python
abc_client = O.classes_abc(ca_client)
cl = l25.assign(classe=l25["id_client"].map(abc_client))
nb_cmd = cmd[cmd["annee"] == 2025].assign(classe=lambda d: d["id_client"].map(abc_client)).groupby("classe").size()
par_classe = cl.groupby("classe").agg(clients=("id_client", "nunique"), ca=("montant", "sum"))
par_classe["part des clients %"] = (par_classe["clients"] / par_classe["clients"].sum() * 100).round(1)
par_classe["part du CA %"] = (par_classe["ca"] / par_classe["ca"].sum() * 100).round(1)
par_classe["commandes par client"] = (nb_cmd / par_classe["clients"]).round(2)
par_classe["part du site %"] = (cl[cl["canal"] == "Site"].groupby("classe")["montant"].sum() / par_classe["ca"] * 100).round(1)
print(par_classe[["clients", "part des clients %", "part du CA %", "commandes par client", "part du site %"]].to_string())
```
<!--sortie-->
```text
        clients  part des clients %  part du CA %  commandes par client  part du site %
classe                                                                                 
A          1753                45.2          80.0                  5.38            46.3
B          1060                27.4          15.0                  2.08            48.7
C          1062                27.4           5.0                  1.23            45.0
```

**Lecture.** Les 1 753 clients de classe A (45,2 % des clients) font 80,0 % du chiffre d'affaires, avec **5,4 commandes par client** contre 2,1 pour les B et 1,2 pour les C. Ils ne se distinguent pas par le **canal** (la part du Site est proche de 46 % dans les trois classes) : ce qui fait un client A, c'est la **fréquence d'achat**. Fidéliser ceux qui commandent déjà souvent est donc un levier plus évident que de les attirer vers un canal particulier.

### 8.1.10 La longue traîne : que vaut le bas du catalogue ?

Les produits de classe C font **5 %** du chiffre d'affaires : faut-il les supprimer ? La réponse n'est pas dans la classe, elle est dans le **panier**. Un produit C peut être acheté **avec** des produits A (il complète la commande) ou **seul**. Si l'on supprime un produit que les clients achètent avec d'autres, on risque de perdre aussi les autres ventes.

```python
paniers = l25.assign(classe=l25["id_produit"].map(abc)).groupby("id_commande")["classe"].agg(lambda s: set(s))
avec_c = paniers[paniers.map(lambda e: "C" in e)]
montants = l25.groupby("id_commande")["montant"].sum()
print("commandes avec au moins un produit C :", len(avec_c), "sur", len(paniers), "(", round(len(avec_c) / len(paniers) * 100, 1), "%)")
print("parmi elles, avec aussi un produit A :", round(avec_c.map(lambda e: "A" in e).mean() * 100, 1), "% | chiffre d'affaires de ces commandes :", round(montants[avec_c.index].sum() / montants.sum() * 100, 1), "% du total")
```
<!--sortie-->
```text
commandes avec au moins un produit C : 4425 sur 12946 ( 34.2 %)
parmi elles, avec aussi un produit A : 70.7 % | chiffre d'affaires de ces commandes : 31.7 % du total
```

**Lecture.** Un tiers des commandes (34,2 %) contient au moins un produit C, et 70,7 % d'entre elles contiennent aussi un produit A. Ces commandes représentent **31,7 %** du chiffre d'affaires total, soit plus de six fois les 4,8 % que pèsent les produits C eux-mêmes : supprimer un produit C sans regarder le panier serait risquer bien plus que son chiffre d'affaires.

On voit qu'un produit C pèse peu **par lui-même** mais que les commandes qui le contiennent pèsent beaucoup plus : le critère de décision n'est pas le chiffre d'affaires du produit, c'est ce que **perdrait** la boutique s'il disparaissait, ce qu'une analyse de paniers (ou un test) peut mesurer.

### 8.1.11 Des classes aux décisions

| Décision | Ce que disent les classes | Précaution |
|---|---|---|
| **Stock** | A : disponibilité maximale, suivi serré ; C : stock minimal | Croiser avec la régularité (XYZ) et les délais fournisseurs |
| **Assortiment** | C (surtout CZ) : candidats à l'arrêt | Un produit C peut **attirer** ou **compléter** des produits A (vérifier les paniers) |
| **Effort commercial** | A et clients A : fidéliser, protéger | Ne pas négliger les B, qui peuvent devenir A |
| **Qualité** | Pareto des retours : traiter d'abord les produits qui concentrent les remboursements | Distinguer retours évitables et retours de convenance |

> ✅ **À retenir.** Le Pareto **se mesure** : ici les 20 % de produits les plus vendus ne font pas 80 % du chiffre d'affaires. L'analyse ABC en fait des classes d'action ; on la croise avec la **marge** et la **régularité** ; on en vérifie la **stabilité** ; et l'on ne supprime pas un produit C sans avoir regardé ce qu'il apporte au panier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.1 à 8.4 et exercices 8.1 à 8.6.
