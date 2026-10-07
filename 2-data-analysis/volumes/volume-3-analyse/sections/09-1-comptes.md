## 9.1 Lire un compte de résultat et un bilan

Deux documents résument une entreprise. Le **compte de résultat** raconte **ce qui s'est passé pendant une période** (on a vendu, on a dépensé, on a gagné ou perdu) ; le **bilan** prend une **photographie à une date** (ce que l'entreprise possède et ce qu'elle doit). Un analyste doit savoir lire les deux, et surtout savoir **vérifier qu'ils racontent la même histoire que les ventes**.

### 9.1.1 Le compte de résultat : une cascade

Le compte de résultat se lit de haut en bas comme une **cascade** : on part du chiffre d'affaires, on retranche les coûts dans un ordre précis, et chaque sous-total répond à une question.

- Le **chiffre d'affaires hors taxes** (CA) est ce que les clients ont payé, moins la TVA, qui n'appartient pas à l'entreprise.
- Les **achats de marchandises** sont le coût de ce que l'on a vendu. On y ajoute la **variation de stock** : acheter n'est pas vendre, et un stock qui grossit a coûté de l'argent sans encore avoir rapporté.
- La **marge brute** est le CA moins le coût des marchandises vendues : c'est ce qui reste pour payer tout le reste.
- Les **charges d'exploitation** (personnel, loyers, marketing, livraison, frais bancaires, amortissements, autres) sont payées avec la marge brute. Ce qui reste est le **résultat d'exploitation**.

> 💡 **Intuition.** Pensez à une tarte. Le chiffre d'affaires est la tarte entière ; les marchandises en prennent une grosse part (62 % ici) ; la marge brute est le reste ; chaque charge prélève une tranche ; le résultat est la miette finale. Une entreprise ne devient pas rentable en vendant plus de tarte, mais en gardant plus de miettes.

Voici la marge brute des trois dernières années, en euros.

```python hide-code
t = ann[["ca_ht", "achats", "variation_stock", "marge_brute"]].T
t.index = ["Chiffre d'affaires HT", "Achats de marchandises", "Variation de stock", "Marge brute"]
print(tab(t))
```
<!--sortie-->
```text
annee                      2023     2024       2025
Chiffre d'affaires HT   949 111  991 218  1 103 969
Achats de marchandises  604 855  632 650    684 952
Variation de stock        1 624    1 803     −1 888
Marge brute             345 879  360 369    417 129
```

On vérifie la ligne : en 2025, $1\,103\,969-684\,952-1\,888=417\,129$. La marge brute **augmente** de 56 760 € entre 2024 et 2025, soit 50 centimes pour chaque euro de chiffre d'affaires supplémentaire. Reste à voir ce que les charges en font.

```python hide-code
t = ann[["frais_personnel", "loyers_charges", "marketing", "livraison", "frais_bancaires", "amortissements", "autres_charges", "charges_totales", "resultat_exploitation"]].T
t.index = ["Personnel", "Loyers et charges", "Marketing", "Livraison", "Frais bancaires", "Amortissements", "Autres charges", "Total des charges", "Résultat d'exploitation"]
print(tab(t))
```
<!--sortie-->
```text
annee                       2023     2024     2025
Personnel                128 930  129 781  141 121
Loyers et charges         61 200   61 200   64 800
Marketing                 51 199   59 975   73 145
Livraison                 23 109   26 940   31 517
Frais bancaires           17 084   17 842   19 872
Amortissements            22 800   22 800   22 800
Autres charges            24 604   24 232   23 995
Total des charges        328 926  342 770  377 250
Résultat d'exploitation   16 953   17 599   39 879
```

Le total des charges passe de 342 770 € à 377 250 €, soit **34 480 € de plus** en un an. La marge brute a gagné 56 760 €, les charges 34 480 € : la différence, 22 280 €, est la hausse du résultat. C'est la réponse à la première moitié de la question de la gérante : **sur chaque euro de chiffre d'affaires supplémentaire, il ne reste que 19,8 centimes** (22 280 / 112 751), parce que 50,3 centimes de marge brute sont mangés par 30,6 centimes de charges nouvelles, dont 11,7 centimes de marketing et 10,1 centimes de personnel.

> ⚠️ **Piège : le mot « marge ».** Dans l'usage francophone, **taux de marge** (marge divisée par le **coût d'achat**) et **taux de marque** (marge divisée par le **prix de vente**) sont deux choses différentes. Un article acheté 60 € et vendu 100 € hors taxes a un taux de marge de 66,7 % et un taux de marque de 40 %. Dans ce chapitre, « taux de marge brute » désigne la marge brute **divisée par le chiffre d'affaires** (soit le taux de marque), parce que c'est le plus utile pour comparer des années ; précisez toujours le dénominateur avec la personne qui vous lit.

### 9.1.2 Le bilan : ce qu'on possède, ce qu'on doit

Le bilan a deux colonnes qui **s'équilibrent toujours** : l'**actif** (ce que l'entreprise possède : machines et agencements, stock, créances sur les clients, trésorerie) et le **passif** (comment cela est financé : capitaux propres, emprunts, dettes envers les fournisseurs et autres dettes). L'équation, $\text{actif}=\text{passif}$, n'est pas une propriété de l'entreprise : c'est une propriété de la **comptabilité**, qui note chaque opération deux fois.

```python hide-code
t = bi[["immobilisations_nettes", "stock", "creances_clients", "tresorerie", "capitaux_propres", "emprunt", "dettes_fournisseurs", "autres_dettes"]].T
t.index = ["Immobilisations nettes", "Stock", "Créances clients", "Trésorerie", "Capitaux propres", "Emprunt", "Dettes fournisseurs", "Autres dettes"]
print(tab(t))
```
<!--sortie-->
```text
annee                      2023     2024     2025
Immobilisations nettes   95 000   87 200   79 400
Stock                   137 467  146 660  161 898
Créances clients         27 682   28 911   32 199
Trésorerie              119 231  119 698  134 754
Capitaux propres        161 867  174 186  202 102
Emprunt                  90 000   75 000   60 000
Dettes fournisseurs      70 566   73 809   79 911
Autres dettes            56 947   59 473   66 238
```

Les quatre premières lignes sont l'actif, les quatre dernières le passif. Chaque ligne a une signification utile à l'analyste :

- les **immobilisations nettes** sont les biens durables (agencements, matériel) diminués de leur usure comptable : elles baissent de 7 800 € par an (les amortissements) en l'absence d'investissement ;
- le **stock** est de la marchandise payée mais pas encore vendue : c'est de l'argent immobilisé ;
- les **créances clients** sont les ventes pas encore encaissées (peu de chose ici, puisqu'on paie en magasin ou en ligne) ;
- la **trésorerie** est l'argent disponible ;
- les **capitaux propres** sont l'argent apporté par les propriétaires, plus les bénéfices conservés ;
- l'**emprunt** diminue de 15 000 € par an ;
- les **dettes fournisseurs** sont les marchandises reçues mais pas encore payées.

> 🧭 **En pratique.** Un bilan se lit avec un **ordre de grandeur en tête** : ici, le stock (161 898 € en 2025) pèse presque autant que la trésorerie et les créances réunies, et le chiffre d'affaires annuel représente environ 2,7 fois le total du bilan (408 251 €). Une boutique est une entreprise de **stock** avant d'être une entreprise de capital.

### 9.1.3 Vérifier la cohérence : les comptes disent-ils la même chose que les ventes ?

Avant d'analyser des comptes, on s'assure qu'ils sont **cohérents avec ce que l'on connaît d'ailleurs**. C'est le réflexe du volume II (réconciliation) appliqué à la comptabilité, et il prend deux formes.

**Le chiffre d'affaires du compte de résultat doit se retrouver dans les ventes de la base**, à la TVA près. Les ventes de la base sont toutes toutes taxes comprises ; on les divise par 1,2 (la TVA fictive du chapitre) et l'on compare, mois par mois.

```python
ventes = O.ventes_mensuelles(cmd, lig)                     # CA HT mois par mois, reconstitué depuis la base
ecart = cr.set_index("mois")["ca_ht"] - ventes
print("mois comparés :", len(ecart), "| écart absolu maximal :", fr(ecart.abs().max(), 2), "€")
```
<!--sortie-->
```text
mois comparés : 36 | écart absolu maximal : 0,49 €
```

Les 36 mois concordent à moins de **49 centimes** près (les comptes sont arrondis à l'euro). Si l'écart avait été de plusieurs pour cent, il aurait fallu chercher : une promotion mal comptée, des ventes d'un autre canal oubliées, une TVA différente.

**Le bilan doit s'équilibrer.** On calcule actif moins passif année par année.

```python
actif = bi["immobilisations_nettes"] + bi["stock"] + bi["creances_clients"] + bi["tresorerie"]
passif = bi["capitaux_propres"] + bi["emprunt"] + bi["dettes_fournisseurs"] + bi["autres_dettes"]
print("actif - passif (€) :", {int(a): int(v) for a, v in (actif - passif).items()}, "| total du bilan 2025 :", fr(actif[2025]), "€")
```
<!--sortie-->
```text
actif - passif (€) : {2023: 0, 2024: 1, 2025: 0} | total du bilan 2025 : 408 251 €
```

L'écart est nul en 2023 et en 2025 et de **1 €** en 2024 : chaque ligne du bilan est arrondie à l'euro, et ces arrondis ne se compensent pas toujours. Un euro d'écart d'arrondi est normal ; mille euros ne le seraient pas.

> ✅ **À retenir.** Un compte de résultat se lit comme une cascade (chiffre d'affaires → marge brute → résultat), un bilan comme une égalité (actif = passif). Avant toute analyse, **recoupez** : le chiffre d'affaires avec les ventes, le bilan avec son équilibre. Un écart de quelques euros se range dans les arrondis ; au-delà, il se cherche.

### 9.1.4 Lire une année et lire un mois

La cascade de 2025 se lit d'un seul coup d'œil sur la figure suivante.

```python hide
O.fig_cascade(ann.loc[2025], "figures/ch09-cascade-2025.png")
```

![Du chiffre d'affaires de 2025 (1 104 k€ hors taxes) au résultat d'exploitation (40 k€) : les achats nets de variation de stock retirent 687 k€, puis sept charges retirent chacune de 20 à 141 k€.](figures/ch09-cascade-2025.png)

Les achats prennent 62,0 % du chiffre d'affaires ; le personnel 12,8 %, le marketing 6,6 %, les loyers 5,9 %, la livraison 2,9 %, les amortissements 2,1 %, les autres charges 2,2 %, les frais bancaires 1,8 %. Il reste 3,6 %. La lecture est immédiate : une **petite variation d'un gros poste** (deux points de marge sur les marchandises, soit 22 080 €) rapporte plus que la **suppression complète d'un petit poste** (les frais bancaires, 19 872 €). Pour gagner plus, la première question est « comment améliorer ce que l'on gagne sur chaque article ? » avant « comment réduire les petites charges ? ».

Le même compte, lu **mois par mois**, révèle autre chose : la **saison**.

```python hide-code
m25 = cr[cr["annee"] == 2025].set_index("mois")
nb_neg = cr[cr["resultat_exploitation"] < 0].groupby("annee").size()
print("mois en perte :", {int(a): int(v) for a, v in nb_neg.items()})
print("résultat de janvier et février 2025 :", fr(m25.loc["2025-01":"2025-02", "resultat_exploitation"].sum()), "€")
print("résultat de décembre 2025 :", fr(m25.loc["2025-12", "resultat_exploitation"]), "€ soit", fr(m25.loc["2025-12", "resultat_exploitation"] / ann.loc[2025, "resultat_exploitation"] * 100, 1), "% du résultat annuel")
print("résultat de novembre et décembre 2025 :", fr(m25.loc["2025-11":"2025-12", "resultat_exploitation"].sum()), "€ soit", fr(m25.loc["2025-11":"2025-12", "resultat_exploitation"].sum() / ann.loc[2025, "resultat_exploitation"] * 100, 1), "% du résultat annuel")
```
<!--sortie-->
```text
mois en perte : {2023: 5, 2024: 5, 2025: 4}
résultat de janvier et février 2025 : −8 071 €
résultat de décembre 2025 : 19 344 € soit 48,5 % du résultat annuel
résultat de novembre et décembre 2025 : 25 777 € soit 64,6 % du résultat annuel
```

Quatre à cinq mois par an sont **en perte** (janvier à avril en 2025) : l'entreprise perd 8 071 € en janvier et février, puis se rattrape avec l'été et surtout avec la fin d'année. **Décembre rapporte 19 344 €, soit 48,5 % du résultat de l'année**, et novembre et décembre ensemble 25 777 € (64,6 %). Ce profil a deux conséquences pour l'analyste : on ne juge jamais une année sur un trimestre, et l'on compare **un mois à son équivalent de l'année précédente**, pas au mois précédent. Les loyers, les salaires et les amortissements tombent chaque mois, quelle que soit l'activité ; c'est ce qui rend les creux de janvier si coûteux. Nous mesurerons cette rigidité en section 9.3.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.1 et exercices 9.1 à 9.3.
