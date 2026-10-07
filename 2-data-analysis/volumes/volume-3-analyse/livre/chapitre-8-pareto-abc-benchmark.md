# Chapitre 8 : ➕ Pareto, analyse ABC et benchmarking

> « Tout compter ne sert à rien : il faut savoir ce qui compte, et par rapport à qui. »

> 🧭 **Chapitre complémentaire.** Il est facultatif : le reste du volume ne le suppose pas. Il présente deux outils de **priorisation** très utilisés en entreprise : classer ce qui pèse le plus (Pareto, ABC), et se situer par rapport à des références (benchmarking).

La gérante revient avec une question à deux têtes : « *Quels produits sont vraiment importants pour la boutique, à qui consacrer mon énergie et mon stock ? Et, au fond, est-ce que je me débrouille bien par rapport aux autres boutiques de mon secteur ?* »

La première question est une affaire de **concentration** : quelques produits, quelques clients font-ils l'essentiel du chiffre d'affaires ? La seconde est une affaire de **comparaison** : un chiffre n'est ni bon ni mauvais en soi, il l'est par rapport à une référence. Les deux ont le même piège : donner une réponse nette, rassurante, **plus simple que ce que les données permettent**.

## Le chemin de ce chapitre

- **8.1 Pareto et analyse ABC** : tracer une courbe de Pareto, tester la règle « 80/20 » sur les produits, les clients et les retours, construire des classes A, B et C, les croiser avec la marge et avec la régularité de la demande, et éviter les pièges.
- **8.2 Benchmarking interne et externe** : comparer les canaux, les catégories et les mois entre eux, puis la boutique au secteur (avec des données **fictives**), lire un positionnement et décider quoi faire d'un écart.

## Les données du chapitre

On utilise les commandes, les lignes de commande, les produits, les retours et les clients de la boutique (2023–2025), ainsi que les sessions du site, le compte de résultat et le bilan, les livraisons et le stock quotidien pour calculer des indicateurs. Le fichier `benchmark_secteur.csv` donne, pour douze indicateurs, une **médiane** et deux **quartiles** d'un secteur : ces chiffres sont **fictifs**, inventés pour l'exercice, et ne décrivent aucun secteur réel. Toutes les données sont **simulées** ; la vérité programmée est dans la docstring de `build/donnees_a3.py`.


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


## 8.2 Benchmarking interne et externe

### 8.2.1 Se comparer, à qui ?

Un chiffre isolé ne dit presque rien : un taux de retour de 6,3 % est-il bon ? On ne le sait qu'**en le comparant**. Le *benchmarking* (ou étalonnage) consiste à se situer par rapport à des références. On en distingue trois sortes.

- **Interne** : comparer des parties de l'entreprise entre elles (canaux, catégories, périodes). Les définitions sont les mêmes, les données sont à portée de main : c'est la comparaison la plus **fiable**.
- **Externe, sectorielle** : comparer à des statistiques de secteur (médiane, quartiles). Elle situe l'entreprise dans son marché, mais les définitions et les périmètres sont rarement identiques.
- **Concurrentielle ou fonctionnelle** : comparer à un concurrent précis, ou à la meilleure pratique d'une fonction (par exemple la logistique), même hors du secteur. Elle est plus riche et plus difficile : les données manquent.

### 8.2.2 Le benchmarking interne

Comparer les **canaux** entre eux révèle des écarts de comportement sans aucune hypothèse sur le monde extérieur.

```python
a = l25.copy()
cmd25 = cmd[cmd["annee"] == 2025]
interne = a.groupby("canal").agg(ca=("montant", "sum"), marge=("marge", "sum"), lignes=("id_ligne", "size"), retours=("retournee", "sum"))
interne["commandes"] = cmd25.groupby("canal").size()
interne["panier moyen"] = (interne["ca"] / interne["commandes"]).round(1)
interne["taux de marge %"] = (interne["marge"] / (interne["ca"] / 1.2) * 100).round(1)
interne["taux de retour %"] = (interne["retours"] / interne["lignes"] * 100).round(1)
print(interne[["panier moyen", "taux de marge %", "taux de retour %"]].to_string())
```
<!--sortie-->
```text
          panier moyen  taux de marge %  taux de retour %
canal                                                    
Boutique         103.1             38.0               3.3
Réseaux          102.4             38.1               6.9
Site             101.6             37.9               8.8
```

**Lecture.** Les trois canaux ont presque le même panier moyen (de 101,6 € à 103,1 €) et le même taux de marge (de 37,9 % à 38,1 %), mais des **taux de retour très différents** : 3,3 % en Boutique, 6,9 % sur les Réseaux, 8,8 % sur le Site. La comparaison interne désigne tout de suite l'endroit où chercher.

On peut de même comparer les **catégories** (le taux de marge, le taux de retour) ou les **mois** (un indice de saisonnalité). La règle est de comparer ce qui est **comparable** : le panier moyen d'un canal à un autre, oui ; le chiffre d'affaires de décembre à celui de février, non sans corriger de la saisonnalité (chapitre 5).

```python
cat = a.groupby("categorie").agg(ca=("montant", "sum"), marge=("marge", "sum"), lignes=("id_ligne", "size"), retours=("retournee", "sum"))
cat["taux de marge %"] = (cat["marge"] / (cat["ca"] / 1.2) * 100).round(1)
cat["taux de retour %"] = (cat["retours"] / cat["lignes"] * 100).round(1)
print(cat[["taux de marge %", "taux de retour %"]].sort_values("taux de retour %").to_string())
```
<!--sortie-->
```text
            taux de marge %  taux de retour %
categorie                                    
Papeterie              36.9               6.0
Cuisine                37.3               6.2
Décoration             39.7               6.3
Bien-être              35.1               6.3
Maison                 37.9               6.3
Jardin                 38.3               6.6
```

**Lecture.** Le taux de marge varie de 35,1 % (Bien-être) à 39,7 % (Décoration), alors que les taux de retour des catégories sont presque identiques (de 6,0 % à 6,6 %) : l'écart de retour vient du **canal**, pas de la catégorie.

### 8.2.3 Le benchmarking externe : les chiffres du secteur

Le fichier `benchmark_secteur.csv` donne, pour douze indicateurs, la **médiane** du secteur et ses deux **quartiles** : un quart des entreprises sont en dessous du premier quartile, un quart au-dessus du troisième, la moitié entre les deux. **Ces chiffres sont fictifs.** On calcule les indicateurs de la boutique pour 2025 avec la même définition que le fichier (la fonction `indicateurs_boutique` du chapitre), puis on les **positionne**.

```python
ind = O.indicateurs_boutique(D, 2025)
pos = O.positionner(ind, sect)
vue = pos[["indicateur", "valeur", "mediane_secteur", "quartile_1", "quartile_3", "ecart_std", "verdict"]].copy()
vue[["valeur", "ecart_std"]] = vue[["valeur", "ecart_std"]].round(2)
print(vue.to_string(index=False))
```
<!--sortie-->
```text
                            indicateur  valeur  mediane_secteur  quartile_1  quartile_3  ecart_std              verdict
              Taux de marge brute (HT)   37.96             38.0        33.0        42.0      -0.01 proche de la médiane
               Taux de retour (lignes)    6.29              5.5         3.5         8.5       0.21 proche de la médiane
                          Panier moyen  102.33             92.0        70.0       118.0       0.29            favorable
            Taux de conversion du site    4.78              2.6         1.8         3.8       1.47            favorable
               Part du site dans le CA   46.63             35.0        20.0        50.0       0.52               neutre
            Rotation du stock (par an)    4.23              4.2         3.0         5.8       0.01 proche de la médiane
              Taux de rupture de stock    7.36              4.0         2.0         7.0       0.91          défavorable
                  Livraisons à l'heure   73.47             92.0        86.0        96.0      -2.50          défavorable
        Coût d'acquisition d'un client  115.37             18.0        11.0        27.0       8.21          défavorable
              Clients actifs à 12 mois   64.58             42.0        30.0        55.0       1.22            favorable
Part des frais de personnel dans le CA   12.78             24.0        19.0        29.0      -1.51            favorable
```

**Lecture.** Quatre indicateurs sont favorables (panier moyen, conversion du site, clients actifs, part des frais de personnel), trois sont proches de la médiane (marge, retours, rotation), un est neutre (part du site) et trois sont défavorables : le taux de rupture, les livraisons à l'heure et le coût d'acquisition. Les écarts les plus grands sont ceux du **coût d'acquisition** (+8,2 écarts-types), des **livraisons à l'heure** (−2,5) et de la **conversion** (+1,5) : des valeurs aussi extrêmes sont suspectes avant d'être spectaculaires (8.2.5).

Pour chaque indicateur, on lit trois choses : **où** se situe la boutique (en dessous du premier quartile, dans l'intervalle, au-dessus du troisième), **de combien** (l'**écart standardisé** : l'écart à la médiane divisé par un écart-type robuste, estimé par l'écart interquartile divisé par 1,349 ; un écart de 1 signifie « un écart-type au-dessus de la médiane ») et **dans quel sens** c'est bon ou mauvais. Le sens est essentiel : un taux de retour **plus bas** que la médiane est favorable, une conversion **plus basse** est défavorable, et la part du site dans le chiffre d'affaires est une affaire de **stratégie**, ni bonne ni mauvaise.

L'indicateur manquant est le **désabonnement e-mail** : on n'a pas de données d'envoi, et c'est un bon exemple d'une comparaison **impossible** faute de mesure. On ne l'invente pas.

### 8.2.4 Lire un positionnement

Un tableau de douze lignes se lit mal ; une figure aide. Le « radar » (toile d'araignée) est populaire mais trompeur : l'ordre des axes change la forme, et les surfaces n'ont pas de sens. On préfère une **bande interquartile** par indicateur, avec la valeur de la boutique en point.


![Positionnement de la boutique par rapport au secteur : pour chaque indicateur, la bande bleue est l'intervalle interquartile du secteur (du premier au troisième quartile), le trait gris est la médiane et le point est la valeur de la boutique, vert si favorable, rouge si défavorable, orange si neutre, bleu si proche de la médiane. Les valeurs extrêmes (coût d'acquisition, livraisons à l'heure) sont ramenées au bord de la figure : leur écart réel est donné dans le tableau.](figures/ch08-positionnement.png)

### 8.2.5 La comparabilité : trois « écarts » qui sont des écarts de définition

Avant de conclure que la boutique est « très bonne » ou « très mauvaise » sur un indicateur, il faut vérifier que l'on **compare la même chose**. Trois indicateurs du tableau précédent sont suspects.

- Le **coût d'acquisition d'un client** : la boutique l'a calculé en divisant **tout** le budget marketing (y compris la fidélisation et le courriel aux clients existants) par le nombre de **nouveaux** clients inscrits dans l'année. Le secteur le calcule peut-être par canal payant, ou sur les clients **réellement acquis** par la publicité. Le numérateur et le dénominateur ne sont pas les mêmes. (L'exercice 8.8 du cahier montre qu'une définition plus étroite ne ramène pas pour autant le chiffre vers la médiane : un écart peut être **à la fois** partiellement artificiel et en partie réel.)
- Les **livraisons à l'heure** : la proportion dépend du **délai promis**. La boutique promet six jours ; un concurrent qui promet dix jours sera « à l'heure » plus souvent, sans livrer plus vite.
- La **part des frais de personnel** : le compte de résultat de la boutique ne contient que ses propres salaires, alors qu'un chiffre de secteur inclut généralement tous les frais de personnel de l'entreprise, entrepôt et siège compris.

```python
vue2 = pos.set_index("indicateur")[["valeur", "mediane_secteur"]].round(1)
vue2["rapport à la médiane"] = (vue2["valeur"] / vue2["mediane_secteur"]).round(2)
print(vue2.loc[["Coût d'acquisition d'un client", "Livraisons à l'heure", "Part des frais de personnel dans le CA"]].to_string())
```
<!--sortie-->
```text
                                        valeur  mediane_secteur  rapport à la médiane
indicateur                                                                           
Coût d'acquisition d'un client           115.4             18.0                  6.41
Livraisons à l'heure                      73.5             92.0                  0.80
Part des frais de personnel dans le CA    12.8             24.0                  0.53
```

**Lecture.** Le coût d'acquisition est **6,4 fois** la médiane du secteur, les livraisons à l'heure 80 % de la médiane, les frais de personnel 53 %. Ce sont les trois indicateurs les plus éloignés, et ce sont aussi trois indicateurs dont la **définition** diffère : avant de conclure à un problème (ou à un exploit), il faut aligner la définition.

D'autres vérifications sont systématiques : la **période** (douze mois glissants ou année civile ?), la **taille** (une boutique de quelques centaines de milliers d'euros se compare mal à une chaîne), le **périmètre** (tous canaux ou seulement le web ?), et la **source** (qui a produit les chiffres du secteur, sur quel échantillon ?).

### 8.2.6 Que faire d'un écart avec le secteur ?

Un écart avec le secteur est une **question**, pas un verdict. Trois filtres, dans l'ordre.

1. **Est-il comparable ?** Si la définition diffère, on corrige la définition avant de s'inquiéter.
2. **Est-il matériel et de bon sens ?** Un écart défavorable d'une fraction d'écart-type sur un indicateur secondaire ne mérite pas une action. Un écart défavorable de plus d'un écart-type sur un indicateur central, si.
3. **Peut-on agir dessus ?** On compare ensuite avec le chapitre 7 : décomposer, formuler des hypothèses, tester.

```python
priorite = pos[(pos["verdict"] == "défavorable")].assign(importance=lambda d: d["ecart_std"].abs()).sort_values("importance", ascending=False)
print(priorite[["indicateur", "ecart_std", "position"]].round(2).to_string(index=False))
```
<!--sortie-->
```text
                    indicateur  ecart_std                 position
Coût d'acquisition d'un client       8.21 au-dessus du 3e quartile
          Livraisons à l'heure      -2.50     sous le 1er quartile
      Taux de rupture de stock       0.91 au-dessus du 3e quartile
```

**Lecture.** Les trois écarts défavorables sont le coût d'acquisition (8,21 écarts-types), les livraisons à l'heure (−2,50) et le taux de rupture de stock (0,91). Les deux premiers sont ceux dont la définition est suspecte (8.2.5) ; le troisième, **7,4 %** de jours-produits en rupture contre une médiane de 4,0 % et un troisième quartile à 7,0 %, est le moins suspect, et il rejoint le constat du chapitre 7 (ruptures concentrées en novembre et en décembre). C'est le candidat naturel à une analyse approfondie.

Cette liste ordonne les écarts **défavorables**, mais elle ne tient pas compte de la comparabilité : à vous d'écarter ceux qui relèvent d'une définition différente (8.2.5) avant de les transformer en plan d'action.

> ⚠️ **Piège.** « Être dans la médiane » n'est pas un objectif. Une boutique peut avoir de bonnes raisons stratégiques d'être **au-dessus** du secteur sur un indicateur (une livraison plus rapide qui coûte plus cher) et **en dessous** sur un autre. Le benchmarking **informe** les choix, il ne les **remplace** pas.

### 8.2.7 Se comparer à soi-même dans le temps

La référence la plus honnête reste **soi-même l'an dernier** : même définition, même périmètre. On compare les indicateurs de 2025 à ceux de 2024 (quand les données existent pour les deux années).

```python
i24, i25 = O.indicateurs_boutique(D, 2024), O.indicateurs_boutique(D, 2025)
evo = i24.merge(i25, on=["indicateur", "sens"], suffixes=(" 2024", " 2025")).dropna()
evo["évolution"] = (evo["valeur 2025"] / evo["valeur 2024"] - 1).mul(100).round(1)
evo["sens du changement"] = np.where(evo["sens"] == 0, "neutre", np.where(np.sign(evo["évolution"]) * evo["sens"] > 0, "favorable", "défavorable"))
print(evo[["indicateur", "valeur 2024", "valeur 2025", "évolution", "sens du changement"]].round(1).to_string(index=False))
```
<!--sortie-->
```text
                            indicateur  valeur 2024  valeur 2025  évolution sens du changement
              Taux de marge brute (HT)         36.2         38.0        4.9          favorable
               Taux de retour (lignes)          5.8          6.3        7.8        défavorable
                          Panier moyen         98.9        102.3        3.5          favorable
               Part du site dans le CA         42.2         46.6       10.4             neutre
            Rotation du stock (par an)          4.3          4.2       -1.9        défavorable
                  Livraisons à l'heure         73.6         73.5       -0.1        défavorable
        Coût d'acquisition d'un client         90.1        115.4       28.1        défavorable
              Clients actifs à 12 mois         58.0         64.6       11.4          favorable
Part des frais de personnel dans le CA         13.1         12.8       -2.4          favorable
```

**Lecture.** La marge progresse de 36,2 % à 38,0 % (+4,9 %) et le panier de 98,9 € à 102,3 € (+3,5 %) ; la part du Site gagne plus de quatre points. Mais le taux de retour **se dégrade** (de 5,8 % à 6,3 %), le **coût d'acquisition** augmente de 28 % (de 90 € à 115 €) et les livraisons à l'heure **stagnent** (73,6 % puis 73,5 %). Contrairement à l'écart avec le secteur, cette hausse du coût d'acquisition est une comparaison de **même définition** : c'est un signal à prendre au sérieux, bien plus que l'écart de niveau avec une médiane de secteur.

Un indicateur qui se **dégrade** alors qu'il est « bon » par rapport au secteur appelle une vigilance ; un indicateur « mauvais » mais qui **s'améliore** appelle un suivi plutôt qu'un plan d'urgence. La position (le secteur) et la trajectoire (soi-même) se lisent **ensemble**.

### 8.2.8 Un tableau de bord de benchmark

Une comparaison qui ne se répète pas ne sert à rien. On en fait un **tableau de bord** simple, tenu à jour chaque trimestre, avec **cinq colonnes** : l'indicateur (et sa définition écrite), la valeur de la boutique, la référence (secteur, année précédente), le verdict (favorable, défavorable, proche, neutre) et le **propriétaire** de l'indicateur. Deux règles le gardent utile : **peu** d'indicateurs (huit à douze, comme ici) pour qu'on les lise vraiment, et une **revue** périodique des définitions, parce qu'un indicateur dont la définition dérive en silence rend toutes les comparaisons fausses.

### 8.2.9 Meilleures pratiques et limites

- **Écrire les définitions** de chaque indicateur (numérateur, dénominateur, période, périmètre), avant de comparer.
- **Comparer des distributions**, pas seulement des moyennes : médiane et quartiles disent où l'on se situe parmi les autres.
- **Garder la comparaison interne** comme référence principale : elle est la plus fiable et la plus actionnable.
- **Dater** les chiffres externes et en citer la source ; en cas de doute, demander la définition.
- **Limites** : les statistiques de secteur sont des moyennes sur des entreprises hétérogènes ; une comparaison en un point du temps ne dit rien de la **trajectoire** ; et un indicateur « meilleur » n'est pas toujours une **cause** de meilleurs résultats.

> ✅ **À retenir.** On compare d'abord en **interne**, puis au **secteur** avec ses quartiles. On lit la position, l'**écart standardisé** et le **sens**. Avant de conclure, on vérifie que l'on compare la **même définition**, la même période et le même périmètre : plusieurs « écarts » viennent de la définition, pas de la performance.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : application 8.5 et exercices 8.7 à 8.9.


## Bilan du chapitre 8

Vous savez maintenant :

- **tracer et lire** une courbe de Pareto, et **tester** la règle des 80/20 sur les produits, les clients et les retours au lieu de la supposer ;
- **construire** une analyse ABC (classes à 80 % et 95 % de la valeur), caractériser les classes, la **croiser** avec la marge et avec la régularité de la demande (ABC-XYZ), et en vérifier la **stabilité** et la sensibilité aux seuils ;
- **relier** les classes à des décisions (stock, assortiment, effort commercial, qualité) en connaissant leurs précautions ;
- **comparer en interne** (canaux, catégories, mois) puis **au secteur** (médiane, quartiles, écart standardisé, sens favorable ou défavorable), et **vérifier la comparabilité** (définitions, délai promis, périmètre) avant de conclure ;
- **transformer** un écart avec le secteur en question, puis en plan d'action avec les outils du chapitre 7.

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.1 à 8.5 et exercices 8.1 à 8.9.

Le fil conducteur tient en une phrase : **prioriser, c'est mesurer la concentration et se situer, mais avec des définitions et des seuils que l'on écrit**. Une règle comme « 80/20 » ou une médiane de secteur ne vaut que si l'on sait ce qu'elle mesure.
