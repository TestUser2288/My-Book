# Chapitre 9 : ➕ Analyse financière

> 🧭 **Chapitre complémentaire.** Ce chapitre est entièrement facultatif : le reste du volume ne le suppose pas. Il montre comment un analyste lit les comptes de l'entreprise, mesure sa rentabilité et sépare les coûts qui suivent l'activité de ceux qui ne la suivent pas.

> « Le chiffre d'affaires est une opinion, la marge est un fait, la trésorerie est la réalité. »


La gérante pose la question à la fin de la réunion de janvier, en tapotant sur la feuille des ventes : « Nous avons vendu **11 % de plus** en 2025, et pourtant j'ai l'impression de ne rien gagner. Où passe l'argent ? »

C'est une très bonne question, et la bonne réponse n'est pas « dans les charges » : c'est une **suite de chiffres reliés entre eux**. Le chiffre d'affaires ne se transforme pas en gain : il paie d'abord les marchandises, puis le personnel, le loyer, la publicité, la livraison, la banque, et ce qui reste est le résultat. Voyons ce que disent les comptes.

```python
print("chiffre d'affaires hors taxes (€) :", {int(a): fr(v) for a, v in ann["ca_ht"].items()})
print("croissance du chiffre d'affaires :", {int(a): fr(v * 100, 1) + " %" for a, v in ann["ca_ht"].pct_change().dropna().items()})
print("résultat d'exploitation (€) :", {int(a): fr(v) for a, v in ann["resultat_exploitation"].items()})
print("part du résultat dans le chiffre d'affaires 2025 :", fr(ann.loc[2025, "resultat_exploitation"] / ann.loc[2025, "ca_ht"] * 100, 1), "%")
```
<!--sortie-->
```text
chiffre d'affaires hors taxes (€) : {2023: '949 111', 2024: '991 218', 2025: '1 103 969'}
croissance du chiffre d'affaires : {2024: '4,4 %', 2025: '11,4 %'}
résultat d'exploitation (€) : {2023: '16 953', 2024: '17 599', 2025: '39 879'}
part du résultat dans le chiffre d'affaires 2025 : 3,6 %
```

Le chiffre d'affaires hors taxes a progressé de 11,4 % en 2025 (après 4,4 % en 2024), et le résultat d'exploitation a **plus que doublé** (de 17 599 € à 39 879 €, soit +127 %). Pourtant, il ne représente que **3,6 %** du chiffre d'affaires : sur 100 € hors taxes vendus, 3,60 € restent à l'entreprise. L'impression de la gérante est donc exacte, et il faut l'expliquer : c'est le programme de ce chapitre.

> ⚠️ **Avertissement : des comptes simulés et simplifiés.** Les comptes de ce chapitre sont **fabriqués** à partir des ventes de la boutique : TVA fictive de 20 %, achats égaux aux quantités vendues multipliées par le coût d'achat, résultat net **approché** à 70 % du résultat d'exploitation (pour tenir compte, grossièrement, de l'impôt et des intérêts), bilan **équilibré par construction**. Les règles réelles (plan comptable, traitement des stocks, de la TVA, des amortissements, impôts) dépendent de **votre pays** et de votre entreprise. Ce chapitre apprend à **lire et à interroger** des comptes, pas à les établir, et rien ne s'y substitue à l'avis d'un comptable.

## Le chemin de ce chapitre

- **9.1 Lire un compte de résultat et un bilan** : ce que chaque ligne mesure, comment vérifier que les comptes sont cohérents avec les ventes de la base, comment lire une année et un mois.
- **9.2 Rentabilité et ratios** : marges, rentabilité des capitaux, rotation du stock, délais de règlement, besoin en fonds de roulement, liquidité, endettement ; comparaison dans le temps et avec un secteur fictif.
- **9.3 Analyse des coûts et seuil de rentabilité** : coûts fixes et variables estimés par régression, point mort, marge de sécurité, levier opérationnel, rentabilité par canal et clés de répartition, effet d'une hausse de prix ou de volume.

## Les données du chapitre

> 📦 **Les données.** `compte_resultat_mensuel.csv` (36 mois de comptes de la boutique) et `bilan_annuel.csv` (2023 à 2025), les ventes de la base (`commandes.csv`, `lignes_commande.csv`, `produits.csv`) pour recouper les comptes, `campagnes.csv` (dépenses de marketing de 2025) et `benchmark_secteur.csv` (médiane et quartiles **fictifs** d'un secteur). Tout est **simulé** ; les vérités programmées sont dans `build/donnees_a3.py`.


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

```text
annee                      2023     2024       2025
Chiffre d'affaires HT   949 111  991 218  1 103 969
Achats de marchandises  604 855  632 650    684 952
Variation de stock        1 624    1 803     −1 888
Marge brute             345 879  360 369    417 129
```

On vérifie la ligne : en 2025, $1\,103\,969-684\,952-1\,888=417\,129$. La marge brute **augmente** de 56 760 € entre 2024 et 2025, soit 50 centimes pour chaque euro de chiffre d'affaires supplémentaire. Reste à voir ce que les charges en font.

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


![Du chiffre d'affaires de 2025 (1 104 k€ hors taxes) au résultat d'exploitation (40 k€) : les achats nets de variation de stock retirent 687 k€, puis sept charges retirent chacune de 20 à 141 k€.](figures/ch09-cascade-2025.png)

Les achats prennent 62,0 % du chiffre d'affaires ; le personnel 12,8 %, le marketing 6,6 %, les loyers 5,9 %, la livraison 2,9 %, les amortissements 2,1 %, les autres charges 2,2 %, les frais bancaires 1,8 %. Il reste 3,6 %. La lecture est immédiate : une **petite variation d'un gros poste** (deux points de marge sur les marchandises, soit 22 080 €) rapporte plus que la **suppression complète d'un petit poste** (les frais bancaires, 19 872 €). Pour gagner plus, la première question est « comment améliorer ce que l'on gagne sur chaque article ? » avant « comment réduire les petites charges ? ».

Le même compte, lu **mois par mois**, révèle autre chose : la **saison**.

```text
mois en perte : {2023: 5, 2024: 5, 2025: 4}
résultat de janvier et février 2025 : −8 071 €
résultat de décembre 2025 : 19 344 € soit 48,5 % du résultat annuel
résultat de novembre et décembre 2025 : 25 777 € soit 64,6 % du résultat annuel
```

Quatre à cinq mois par an sont **en perte** (janvier à avril en 2025) : l'entreprise perd 8 071 € en janvier et février, puis se rattrape avec l'été et surtout avec la fin d'année. **Décembre rapporte 19 344 €, soit 48,5 % du résultat de l'année**, et novembre et décembre ensemble 25 777 € (64,6 %). Ce profil a deux conséquences pour l'analyste : on ne juge jamais une année sur un trimestre, et l'on compare **un mois à son équivalent de l'année précédente**, pas au mois précédent. Les loyers, les salaires et les amortissements tombent chaque mois, quelle que soit l'activité ; c'est ce qui rend les creux de janvier si coûteux. Nous mesurerons cette rigidité en section 9.3.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.1 et exercices 9.1 à 9.3.


## 9.2 Rentabilité et ratios

Un chiffre isolé ne dit presque rien : 39 879 € de résultat, est-ce beaucoup ? Les **ratios** rapportent un chiffre à un autre (un résultat au chiffre d'affaires, un stock aux achats) pour obtenir des mesures **comparables** d'une année à l'autre, d'une entreprise à l'autre, d'un canal à l'autre. Cette section en présente quatre familles : les marges, la rentabilité, la gestion du cycle d'exploitation (stock, clients, fournisseurs) et la solidité financière.

### 9.2.1 Les marges : ce que l'on garde sur chaque euro vendu

Le **taux de marge brute** est la marge brute divisée par le chiffre d'affaires hors taxes ; le **taux de marge d'exploitation** est le résultat d'exploitation divisé par ce même chiffre d'affaires. Le premier mesure ce que l'on gagne **sur les marchandises**, le second ce qui reste **après toutes les charges**.

```text
annee                             2023  2024  2025
Taux de marge brute (%)           36,4  36,4  37,8
Taux de marge d'exploitation (%)   1,8   1,8   3,6
Part du personnel dans le CA (%)  13,6  13,1  12,8
```

Le taux de marge brute est stable de 2023 à 2024 (36,4 %) puis gagne 1,4 point en 2025 (37,8 %). **C'est la bonne nouvelle du compte** : la même cascade, sur 1 104 k€, rapporte environ 15 800 € de plus qu'avec le taux de 2024. D'où vient-il ? Probablement d'une hausse des prix de 3 % au début de 2025 et d'un mélange de ventes légèrement différent ; l'analyse des écarts (chapitre 7) apprend à le démontrer. Le taux de marge d'exploitation double, de 1,8 % à 3,6 % : la marge brute gagne 1,4 point, les charges n'en reprennent qu'une partie.

> 📐 **Pour qui veut la formule.** Le résultat d'exploitation s'écrit $R = \tau\,\text{CA} - C$, où $\tau$ est le taux de marge brute et $C$ l'ensemble des charges. Si le chiffre d'affaires est multiplié par $(1+g)$ et les charges par $(1+h)$ avec $h<g$, le résultat augmente de $\tau g\,\text{CA}-hC$ : on gagne si la **marge brute supplémentaire** dépasse les **charges supplémentaires**. Entre 2024 et 2025 : $0{,}503\times112\,751 = 56\,760$ de marge brute (en prenant la marge sur le seul chiffre d'affaires **supplémentaire**) contre $34\,480$ de charges.

### 9.2.2 La rentabilité : que rapporte l'argent investi ?

La marge dit ce que l'on garde sur les ventes ; la **rentabilité** dit ce que l'on gagne par rapport à **l'argent investi** par les propriétaires. Le ratio le plus courant est la **rentabilité des capitaux propres** (en anglais *return on equity*) : le résultat net divisé par les capitaux propres.

Nos comptes ne donnent pas le résultat net ; nous l'**approchons** par 70 % du résultat d'exploitation (hypothèse simplificatrice). La rentabilité obtenue est de 7,3 % en 2023, 7,1 % en 2024 et 13,8 % en 2025.

```python
print("résultat net approché (€) :", {int(a): fr(v) for a, v in rat["resultat_net_approche"].items()})
print("rentabilité des capitaux propres (%) :", {int(a): fr(v * 100, 1) for a, v in rat["rentabilite_capitaux_propres"].items()})
```
<!--sortie-->
```text
résultat net approché (€) : {2023: '11 867', 2024: '12 319', 2025: '27 915'}
rentabilité des capitaux propres (%) : {2023: '7,3', 2024: '7,1', 2025: '13,8'}
```

La rentabilité des capitaux propres a presque doublé en 2025 : le résultat a plus que doublé, les capitaux propres n'ont augmenté que de 16 %. **Mais** elle dépend aussi du dénominateur : une entreprise peut afficher une belle rentabilité parce que ses capitaux propres sont faibles (elle est très endettée) ; il faut donc la lire avec les ratios d'endettement de la section 9.2.4.

> ⚠️ **Piège : une rentabilité n'est pas une performance.** Un taux de 13,8 % est sans signification tant qu'on ne sait pas **à quoi** on le compare : au taux d'un placement sans risque, à celui du secteur, à celui des années précédentes. Et il repose ici sur un résultat net **approché** : ne citez jamais un taux de ce chapitre comme celui d'une entreprise réelle.

### 9.2.3 Stock, clients, fournisseurs : le cycle d'exploitation

Entre le moment où l'on paie une marchandise et celui où l'on encaisse sa vente, de l'argent est **immobilisé**. Trois mesures l'expriment en jours.

- La **rotation du stock** compare les achats de l'année au stock de fin d'année : 4,4 en 2023, 4,3 en 2024 et 4,2 en 2025, c'est-à-dire que le stock se renouvelle un peu plus de quatre fois par an. En jours, $365/4{,}23\approx86$ jours de stock en 2025, contre 83 en 2023 : **le stock grossit un peu plus vite que les achats**.
- Le **délai de règlement des clients** divise les créances clients par le chiffre d'affaires et multiplie par 365 : 10,6 jours.
- Le **délai de règlement des fournisseurs** divise les dettes fournisseurs par les achats : 42,6 jours.

Ces deux délais sont **identiques** les trois années : ce n'est pas une constante de la nature, c'est une conséquence de la façon dont les comptes ont été fabriqués (créances et dettes proportionnelles aux ventes et aux achats). Dans des comptes réels, une dérive de ces délais serait un signal précieux.

Le **besoin en fonds de roulement** (BFR) résume le cycle : ce que l'on doit **financer** pour que l'activité tourne. Nous le définissons ici comme $\text{stock}+\text{créances clients}-\text{dettes fournisseurs}$.

```python
t = rat[["rotation_stock", "jours_stock", "delai_clients_j", "delai_fournisseurs_j", "bfr", "bfr_jours_ca"]].T
t.index = ["Rotation du stock (par an)", "Jours de stock", "Délai clients (jours)", "Délai fournisseurs (jours)", "BFR (€)", "BFR en jours de CA"]
txt = t.astype(object).apply(lambda r: r.map(lambda v: fr(v, 0 if r.name == "BFR (€)" else 1)), axis=1)
print(txt.to_string())
```
<!--sortie-->
```text
annee                         2023     2024     2025
Rotation du stock (par an)     4,4      4,3      4,2
Jours de stock                83,0     84,6     86,3
Délai clients (jours)         10,6     10,6     10,6
Délai fournisseurs (jours)    42,6     42,6     42,6
BFR (€)                     94 583  101 762  114 186
BFR en jours de CA            36,4     37,5     37,8
```

Le BFR passe de 94 583 € à 114 186 € : l'activité exige **19 603 € de financement de plus** en deux ans, soit plus du tiers du résultat d'exploitation cumulé de 2024 et 2025 (57 478 €). Autrement dit, **une partie du résultat n'est pas de la trésorerie** : elle dort dans le stock. Un résultat positif et une trésorerie qui baisse sont compatibles, et c'est un classique de la croissance.

> 💡 **Intuition.** Le résultat dit si l'on est **rentable** ; la trésorerie dit si l'on est **solvable** ; le BFR fait le lien entre les deux. Une entreprise qui grandit vite a besoin de plus de stock, donc de plus de financement : elle peut manquer d'argent alors qu'elle gagne de l'argent.

### 9.2.4 Liquidité et endettement : l'entreprise est-elle solide ?

La **liquidité** mesure la capacité de payer ses dettes à court terme. On rapporte l'actif qui se transforme en argent dans l'année (stock, créances, trésorerie) aux dettes exigibles dans l'année (fournisseurs, autres dettes, et la part de l'emprunt à rembourser, que nous supposons égale à 15 000 € par an). La **liquidité générale** utilise tout cet actif ; la **liquidité immédiate** seulement la trésorerie.

L'**endettement** compare l'emprunt aux capitaux propres, et l'**autonomie financière** la part des capitaux propres dans l'ensemble des financements.

```text
annee                       2023  2024  2025
Liquidité générale          2,00  1,99  2,04
Liquidité immédiate         0,84  0,81  0,84
Emprunt / capitaux propres  0,56  0,43  0,30
Autonomie financière        0,43  0,46  0,50
```

La liquidité générale est stable, autour de 2,0 : l'entreprise dispose de deux euros d'actif à court terme pour chaque euro de dette à court terme. La liquidité immédiate est de 0,84 : la trésorerie seule ne couvre pas **toutes** les dettes exigibles, mais le stock est vendable. Surtout, l'**endettement baisse** (de 0,56 à 0,30) et l'autonomie financière monte (de 0,43 à 0,50) : l'entreprise rembourse son emprunt et conserve ses bénéfices. Elle est de plus en plus solide, et c'est une autre réponse à la gérante : la rentabilité est faible, mais la **structure financière s'améliore**.

> 🧭 **En pratique.** Il n'existe pas de seuil universel : un ratio de liquidité « acceptable » dépend du secteur, de la saison et des habitudes de paiement. On compare une entreprise à **elle-même dans le temps** et à des entreprises **semblables**, jamais à une valeur magique.

### 9.2.5 Analyse horizontale et analyse verticale

Deux façons très simples de lire des comptes méritent des noms.

- L'**analyse horizontale** compare une même ligne **dans le temps** : le chiffre d'affaires croît de 11,4 %, le résultat de 126,6 %, le stock de 10,4 % (de 146 660 € à 161 898 €), le marketing de 22,0 % (de 59 975 € à 73 145 €).
- L'**analyse verticale** exprime chaque ligne **en pourcentage d'une base** (le chiffre d'affaires pour le compte de résultat, le total du bilan pour le bilan) : le personnel pèse 12,8 % du chiffre d'affaires, le stock 39,7 % du total du bilan.

```python
base = ann.loc[[2024, 2025], ["ca_ht", "achats", "frais_personnel", "marketing", "livraison", "resultat_exploitation"]]
print("évolution 2025 / 2024 (%) :", {k: fr(v, 1) for k, v in ((base.loc[2025] / base.loc[2024] - 1) * 100).items()})
print("stock / total du bilan 2025 (%) :", fr(bi.loc[2025, "stock"] / actif[2025] * 100, 1))
```
<!--sortie-->
```text
évolution 2025 / 2024 (%) : {'ca_ht': '11,4', 'achats': '8,3', 'frais_personnel': '8,7', 'marketing': '22,0', 'livraison': '17,0', 'resultat_exploitation': '126,6'}
stock / total du bilan 2025 (%) : 39,7
```

Le tableau d'évolution montre ce que le cahier des charges demande : le **marketing croît deux fois plus vite que le chiffre d'affaires** (+22,0 % contre +11,4 %), la livraison de 17,0 %, le personnel de 8,7 % (moins vite que les ventes), les achats de 8,3 %. Les écarts entre ces taux, rapportés à la taille de chaque poste, expliquent la formation du résultat.

### 9.2.6 Comparer à un secteur, sans surinterpréter

Un secteur fournit des repères : la médiane et les quartiles de chaque indicateur sur un échantillon d'entreprises. Les valeurs du jeu `benchmark_secteur.csv` sont **fictives**, mais le raisonnement est réel.

```python
ref = bm.set_index("indicateur")
ligne = lambda nom, valeur: (nom, fr(valeur, 1), fr(ref.loc[nom, "quartile_1"], 1) + " – " + fr(ref.loc[nom, "quartile_3"], 1))
print(*[ligne("Taux de marge brute (HT)", rat.loc[2025, "taux_marge_brute"] * 100),
        ligne("Rotation du stock (par an)", rat.loc[2025, "rotation_stock"]),
        ligne("Part des frais de personnel dans le CA", rat.loc[2025, "part_personnel"] * 100)], sep="\n")
```
<!--sortie-->
```text
('Taux de marge brute (HT)', '37,8', '33,0 – 42,0')
('Rotation du stock (par an)', '4,2', '3,0 – 5,8')
('Part des frais de personnel dans le CA', '12,8', '19,0 – 29,0')
```

La boutique est **dans la fourchette** du secteur pour la marge brute (37,8 % pour une médiane de 38,0 %) et pour la rotation du stock (4,2 pour une médiane de 4,2) ; sa part de personnel (12,8 %) est **bien en dessous du premier quartile** (19 %). Faut-il s'en réjouir ? Non, pas sans enquête : la boutique emploie peu de monde par rapport à son chiffre d'affaires (c'est une petite structure, et d'autres tâches sont peut-être assurées par la gérante ou par un groupe), ou ses charges de personnel sont mal rapportées. **Un écart au secteur est une question, pas une réponse.**

> ⚠️ **Pièges de la comparaison.** (1) Les définitions varient d'une source à l'autre (rotation calculée sur les achats ou sur le coût des ventes ; marge avant ou après remises). (2) Les entreprises d'un « secteur » sont très hétérogènes (taille, mix de canaux). (3) Un ratio dans la médiane n'est pas bon par nature, et un ratio hors fourchette n'est pas mauvais par nature. (4) Les valeurs du secteur sont ici fictives ; les valeurs réelles datent et se vérifient.

> ✅ **À retenir.** Les ratios rendent les comptes comparables : **marges** (ce qu'on garde sur les ventes), **rentabilité** (ce qu'on gagne sur l'argent investi), **cycle d'exploitation** (stock, délais, BFR) et **solidité** (liquidité, endettement). On les lit **dans le temps** et **avec des repères**, en gardant en tête que chaque ratio a une définition qu'il faut écrire.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.2 et exercices 9.4 à 9.6.


## 9.3 Analyse des coûts et seuil de rentabilité

Pourquoi les 112 751 € de chiffre d'affaires supplémentaire n'ont-ils laissé que 22 280 € de résultat ? Parce que **tous les coûts ne réagissent pas de la même façon à l'activité** : certains suivent les ventes, d'autres tombent chaque mois quoi qu'il arrive. Séparer les deux est le geste central de l'analyse des coûts, et il conduit à trois questions pratiques : à partir de quel chiffre d'affaires gagne-t-on de l'argent ? Quelle est la marge de sécurité ? Quel canal rapporte vraiment ?

### 9.3.1 Coûts fixes et coûts variables

Un **coût variable** augmente quand l'activité augmente (les marchandises, les commissions de paiement, la livraison) ; un **coût fixe** ne dépend pas, à court terme, de l'activité (le loyer, les amortissements, la plupart des salaires). La frontière est souvent floue : un salaire peut être fixe pour le contrat et variable par les heures supplémentaires ; une dépense de publicité est fixe **une fois décidée** mais elle est choisie en fonction de la saison.

Plutôt que de classer à l'intuition, on peut **mesurer** : pour chaque ligne de coût, on cherche comment la dépense mensuelle varie avec le chiffre d'affaires du mois, par une régression linéaire sur les 36 mois :

$$\text{coût}_{\text{mois}} = a + b\times \text{CA}_{\text{mois}}.$$

La pente $b$ est la **part variable** (les centimes de coût par euro de chiffre d'affaires), la constante $a$ la **part fixe mensuelle**.

```python
r = reg[["pente", "constante", "r2", "ic_bas", "ic_haut"]].copy()
r.index = ["Achats", "Personnel", "Loyers", "Marketing", "Livraison", "Frais bancaires", "Amortissements", "Autres charges"]
print(r.drop(index="Amortissements").round(3).to_string())
```
<!--sortie-->
```text
                 pente  constante     r2  ic_bas  ic_haut
Achats           0.610   1832.130  0.989   0.587    0.633
Personnel        0.046   7178.626  0.923   0.042    0.051
Loyers           0.002   5070.676  0.057  -0.001    0.004
Marketing        0.043   1524.341  0.595   0.030    0.055
Livraison        0.033   -486.180  0.929   0.029    0.036
Frais bancaires  0.018     -0.246  1.000   0.018    0.018
Autres charges   0.003   1771.860  0.118   0.000    0.006
```

Chaque ligne se lit ainsi : les **achats** suivent le chiffre d'affaires à 0,610 € par euro (intervalle de confiance de 0,587 à 0,633) avec un $R^2$ de 0,99 : ce sont des coûts **purement variables**. Les **frais bancaires** valent 0,018 € par euro, sans aucun bruit ($R^2=1{,}00$) : une commission proportionnelle. La **livraison** est variable (0,033 €, $R^2=0{,}93$). Le **personnel** a une part fixe de 7 179 € par mois et une part variable de 0,046 € par euro (de 0,042 à 0,051), ce qui s'interprète comme des primes ou des heures supplémentaires. Les **loyers**, les **autres charges** et les **amortissements** ont une pente nulle ou négligeable : ils sont **fixes**.

Le **marketing** demande de la prudence : sa pente est de 0,043 € par euro, mais le $R^2$ n'est que de 0,60. Ce n'est pas un lien mécanique entre les ventes et la publicité : la dépense est **décidée selon le calendrier** (plus forte en novembre, décembre et au printemps), précisément quand les ventes sont fortes. Le traiter comme variable reviendrait à croire que les ventes **provoquent** la dépense ; nous le traiterons donc comme un coût **fixe** à l'échelle de l'année (une décision budgétaire), tout en gardant en tête que c'est un choix de modèle.

> ⚠️ **Piège : une pente n'est pas une loi.** La régression décrit **ce qui s'est passé** sur 36 mois, avec les arrondis et les saisons. Elle suppose que la relation est linéaire et stable ; un nouveau loyer, une renégociation de commissions la rendraient fausse. Et, comme toute estimation, elle a un intervalle de confiance : celui du personnel va de 0,042 à 0,051, soit un facteur 1,2 entre les bornes.

### 9.3.2 La marge sur coûts variables et le point mort

Avec cette séparation, on obtient deux quantités :

- les **coûts variables** de 2025 : achats nets de la variation de stock, livraison, frais bancaires et la part variable du personnel (0,046 € par euro de chiffre d'affaires), soit 789 506 €, c'est-à-dire **71,5 %** du chiffre d'affaires ;
- les **coûts fixes** de 2025 : tout le reste (loyers, marketing, amortissements, autres charges et la part fixe du personnel), soit 274 584 €.

La **marge sur coûts variables** (MCV) est le chiffre d'affaires moins les coûts variables : c'est ce qui reste **pour payer les coûts fixes**, puis pour faire le résultat. Son **taux** est de $1-0{,}715=28{,}5\ \%$ : sur chaque euro vendu, 28,5 centimes contribuent aux coûts fixes.

Le **seuil de rentabilité** (ou **point mort**) est le chiffre d'affaires pour lequel la MCV couvre exactement les coûts fixes, c'est-à-dire pour lequel le résultat est nul :

$$\text{CA}^{*}=\frac{\text{coûts fixes}}{\text{taux de MCV}}.$$

Pourquoi cette formule ? Le résultat vaut $R=\tau_{\text{MCV}}\times\text{CA}-\text{CF}$. Il s'annule quand $\text{CA}=\text{CF}/\tau_{\text{MCV}}$.

```python
x = ann.loc[2025]
cv = (x["achats"] - x["variation_stock"]) + x["livraison"] + x["frais_bancaires"] + reg.loc["frais_personnel", "pente"] * x["ca_ht"]
cf = x["charges_totales"] - x["livraison"] - x["frais_bancaires"] - reg.loc["frais_personnel", "pente"] * x["ca_ht"]
pm = O.point_mort(x["ca_ht"], cv, cf)
print("coûts variables :", fr(cv), "€ (", fr(cv / x["ca_ht"] * 100, 1), "% du CA ) | coûts fixes :", fr(cf), "€")
print("taux de MCV :", fr(pm["taux_mcv"] * 100, 1), "% | seuil de rentabilité :", fr(pm["seuil"]), "€ | contrôle du résultat :", fr(x["ca_ht"] - cv - cf), "€")
```
<!--sortie-->
```text
coûts variables : 789 506 € ( 71,5 % du CA ) | coûts fixes : 274 584 €
taux de MCV : 28,5 % | seuil de rentabilité : 963 968 € | contrôle du résultat : 39 879 €
```

Le seuil de rentabilité de 2025 est de **963 968 €** de chiffre d'affaires, contre 1 103 969 € réalisés. Le résultat de contrôle retombe bien sur le résultat d'exploitation (39 879 €). En commandes : avec un panier moyen de 85,27 € hors taxes (1 103 969 € pour 12 946 commandes), le seuil correspond à **11 304 commandes**, contre 12 946 réalisées.


![Droites des produits (bleu) et des coûts totaux (rouge) selon le chiffre d'affaires annuel de 2025 : elles se croisent au point mort, à 964 k€ ; la boutique a réalisé 1 104 k€, au-dessus du seuil. Les coûts fixes (pointillés) sont de 275 k€ à chiffre d'affaires nul.](figures/ch09-point-mort-2025.png)

> 💡 **Intuition.** Sous le point mort, chaque euro de chiffre d'affaires **réduit la perte** de 28,5 centimes ; au-dessus, chaque euro **augmente le bénéfice** de 28,5 centimes. La droite des coûts totaux est moins pentue que celle des produits, parce que les coûts variables ne prennent que 71,5 % de chaque euro : la différence est la marge qui construit le résultat.

### 9.3.3 Marge de sécurité et levier opérationnel

Deux indicateurs complètent le point mort.

La **marge de sécurité** est la part du chiffre d'affaires qui pourrait disparaître avant d'atteindre le seuil : $(\text{CA}-\text{CA}^{*})/\text{CA}$. En 2025, elle est de **12,7 %** : si le chiffre d'affaires baisse de plus de 12,7 %, l'entreprise perd de l'argent.

Le **levier opérationnel** (ou degré de levier) est le rapport de la MCV au résultat : il dit **de combien de pour cent bouge le résultat quand le chiffre d'affaires bouge de 1 %**. En 2025, il vaut 7,9 : +1 % de chiffre d'affaires donne environ +7,9 % de résultat (et −1 % donne −7,9 %). Plus les coûts fixes sont lourds, plus l'effet est grand, dans les deux sens.

```python
comp = {}
for an in (2023, 2024, 2025):
    y = ann.loc[an]
    pv_ = reg.loc["frais_personnel", "pente"] * y["ca_ht"]
    cv_ = (y["achats"] - y["variation_stock"]) + y["livraison"] + y["frais_bancaires"] + pv_
    cf_ = y["charges_totales"] - y["livraison"] - y["frais_bancaires"] - pv_
    comp[an] = O.point_mort(y["ca_ht"], cv_, cf_) | {"cf": cf_, "ca": y["ca_ht"]}
print(pd.DataFrame(comp).T[["ca", "cf", "seuil", "marge_securite", "levier"]].round(3).to_string())
```
<!--sortie-->
```text
             ca          cf       seuil  marge_securite  levier
2023   949111.0  244648.722  887600.830           0.065  15.430
2024   991218.0  251947.937  926493.471           0.065  15.314
2025  1103969.0  274583.882  963967.803           0.127   7.885
```

Les trois années se comparent : le seuil passe de 887 601 € à 963 968 € (+8,6 %), les coûts fixes de 244 649 € à 274 584 € (+12,2 %), mais le chiffre d'affaires a progressé plus vite, de sorte que la marge de sécurité **double** (de 6,5 % à 12,7 %) et que le levier opérationnel **est divisé par deux** (de 15,4 à 7,9). C'est la seconde réponse à la gérante, qui dit plus que le simple taux de marge : **l'entreprise s'est éloignée du précipice**. En 2023 et 2024, une baisse de 6,5 % des ventes aurait suffi à effacer le résultat ; en 2025, il en faudrait près du double. Ce qui ressemble à un faible profit est en réalité un profit **moins fragile**.

> 🧭 **En pratique.** Le levier opérationnel est un **grossissement** : il amplifie les bonnes années et les mauvaises. Une activité saisonnière avec des coûts fixes lourds (loyers, salaires) est très sensible : un mois de décembre raté pèse sur toute l'année, car décembre rapporte à lui seul près de la moitié du résultat.

### 9.3.4 La rentabilité par canal : le piège des clés de répartition

La gérante veut savoir quel canal (Boutique, Site, Réseaux) rapporte de l'argent. On calcule pour chacun la marge brute (ventes hors taxes moins coût d'achat des marchandises vendues), puis on lui retire ses coûts.

- Certains coûts sont **directs** : la livraison (seulement Site et Réseaux), les frais bancaires (au prorata des ventes), le marketing (nous affectons les dépenses de publicité payante et d'e-mails au Site, et les dépenses sur les réseaux sociaux au canal Réseaux : c'est une **hypothèse** du chapitre).
- D'autres sont **communs** : le personnel, les loyers, les amortissements, les autres charges. Pour les imputer aux canaux, il faut une **clé de répartition**, c'est-à-dire un choix.

La **contribution** d'un canal est sa marge brute moins ses coûts directs : c'est ce qu'il apporte au paiement des coûts communs. Le **résultat** d'un canal est sa contribution moins sa part des coûts communs, qui dépend de la clé.

```python
g, tot = O.rentabilite_canal(cmd, lig, prod, cr, camp)
t = g[["ca_ht", "marge_brute", "contribution", "resultat_cle_ca", "resultat_cle_commandes"]].round(0).astype(int)
t.columns = ["CA HT", "Marge brute", "Contribution", "Résultat (clé CA)", "Résultat (clé commandes)"]
print(t.to_string())
```
<!--sortie-->
```text
           CA HT  Marge brute  Contribution  Résultat (clé CA)  Résultat (clé commandes)
canal                                                                                   
Boutique  467478       177622        169207              62194                     62975
Réseaux   121729        46392         15683             -12183                    -12154
Site      514763       195003        109595              -8242                     -9052
```


![Contribution et résultat par canal en 2025, avec deux clés de répartition des charges communes. La Boutique gagne dans tous les cas ; les canaux Réseaux et Site sont en perte avec chaque clé, tout en apportant une contribution positive.](figures/ch09-canaux.png)

La **Boutique** rapporte 169 207 € de contribution et 62 194 € de résultat avec la clé « chiffre d'affaires » (62 975 € avec la clé « commandes »). Les canaux **Réseaux** et **Site** ont chacun une contribution positive (15 683 € et 109 595 €) mais un **résultat négatif** une fois leur part des coûts communs imputée (−12 183 € et −8 242 € avec la clé « chiffre d'affaires »). Le choix de la clé change les chiffres de quelques centaines d'euros (ici, 9 052 € de perte pour le Site avec la clé « commandes »), mais **pas la conclusion**, parce que les deux clés répartissent les coûts communs presque de la même façon : le panier moyen est voisin d'un canal à l'autre (environ 85 € hors taxes).

La question « faut-il arrêter le canal Réseaux ? » montre le danger de lire le résultat par canal : arrêter Réseaux **supprimerait sa contribution de 15 683 €** ; les coûts communs qu'on lui impute (27 866 €) ne disparaîtraient pas pour autant (le loyer reste le même). Le résultat de l'entreprise **baisserait** de 15 683 €, et non pas augmenterait de 12 183 €. À l'inverse, si une réorganisation permet de supprimer une partie réelle des coûts communs, le calcul change. La règle pratique : **pour décider de garder ou d'arrêter un canal, on regarde la contribution (et ce qu'on peut réellement économiser), pas le résultat après répartition.**

La somme des résultats par canal (41 769 €) diffère du résultat d'exploitation de l'entreprise (39 879 €) de 1 890 € : c'est la **variation de stock** de −1 888 €, qui n'est affectée à aucun canal, plus 2 € d'arrondis.

> ⚠️ **Piège : les clés de répartition fabriquent des résultats.** Répartir au prorata du chiffre d'affaires revient à dire que chaque euro vendu coûte autant en personnel et en loyer ; répartir au prorata des commandes dit que chaque commande coûte autant. Aucune clé n'est « vraie ». Si deux clés raisonnables donnent des conclusions opposées, la bonne question n'est pas « laquelle choisir ? » mais « **que me dit la contribution, qui ne dépend d'aucune clé ?** ».

### 9.3.5 Hausse de prix ou hausse de volume ?

Le modèle coûts fixes / coûts variables permet de chiffrer deux leviers très différents. Une **hausse de prix de 1 %** à volume égal ajoute 1 % au chiffre d'affaires **sans ajouter** d'achats ni de livraison ; seuls les coûts proportionnels aux ventes (frais bancaires, part variable du personnel) augmentent. Une **hausse de volume de 1 %** ajoute 1 % au chiffre d'affaires **et** 1 % à tous les coûts variables.

```python
ca25 = x["ca_ht"]
liees_ca = x["frais_bancaires"] + reg.loc["frais_personnel", "pente"] * ca25          # coûts proportionnels au chiffre d'affaires
prix = 0.01 * ca25 - 0.01 * liees_ca
volume = 0.01 * (ca25 - cv)
print("effet sur le résultat : +1 % de prix :", fr(prix), "€ ( +", fr(prix / x["resultat_exploitation"] * 100, 1), "% ) | +1 % de volume :", fr(volume), "€ ( +", fr(volume / x["resultat_exploitation"] * 100, 1), "% )")
```
<!--sortie-->
```text
effet sur le résultat : +1 % de prix : 10 328 € ( + 25,9 % ) | +1 % de volume : 3 145 € ( + 7,9 % )
```

**Un point de prix vaut trois points de volume** : +1 % de prix rapporte 10 328 € (+25,9 % de résultat), +1 % de volume 3 145 € (+7,9 %), soit un rapport de 3,3. C'est le résultat le plus utile du chapitre pour une discussion avec la gérante : une hausse de prix de 3 % faite en 2025 a probablement contribué plus au résultat que la hausse du nombre de commandes. Attention toutefois : la hausse de prix **n'est pas gratuite**, car elle peut faire baisser le volume ; on cherche alors la baisse de volume qui annule le gain, et c'est le sujet de l'analyse de sensibilité (chapitre 13).

> ✅ **À retenir.** Séparer coûts **fixes** et **variables** (par régression, avec un intervalle) donne le **point mort**, la **marge de sécurité** et le **levier opérationnel**. Pour juger un canal ou un produit, on regarde sa **contribution** plutôt que son résultat après clé de répartition, et l'on garde à l'esprit qu'**un point de prix vaut bien plus qu'un point de volume** quand les coûts variables sont élevés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.3 à 9.5 et exercices 9.7 à 9.9.


## Bilan du chapitre 9

Vous savez maintenant :

- **lire** un compte de résultat comme une cascade (chiffre d'affaires, marge brute, charges, résultat d'exploitation) et un bilan comme une égalité (actif = passif), et **vérifier** leur cohérence : le chiffre d'affaires des comptes retrouvé dans les ventes de la base à 49 centimes près, un bilan équilibré à 1 € d'arrondi près ;
- **expliquer** une évolution par la comparaison de deux cascades : entre 2024 et 2025, +112 751 € de chiffre d'affaires, +56 760 € de marge brute, +34 480 € de charges, donc +22 280 € de résultat, soit **19,8 centimes** par euro supplémentaire vendu ;
- **calculer** et interpréter les ratios de marge (taux de marge brute de 36,4 % à 37,8 %, taux de marge d'exploitation de 1,8 % à 3,6 %), de rentabilité (rentabilité des capitaux propres approchée de 7,1 % à 13,8 %), de cycle d'exploitation (86 jours de stock, besoin en fonds de roulement de 114 186 €) et de solidité (liquidité générale de 2,0, endettement de 0,56 à 0,30) ;
- **comparer** à un secteur sans surinterpréter : un écart est une question, pas une réponse ;
- **séparer** coûts fixes et variables par régression (achats à 0,610 € par euro de chiffre d'affaires, frais bancaires à 0,018 €, personnel à part fixe et part variable), et en déduire le **point mort** (963 968 €), la **marge de sécurité** (12,7 %) et le **levier opérationnel** (7,9) ;
- **juger un canal** par sa contribution plutôt que par un résultat dépendant de la clé de répartition, et chiffrer l'effet d'une hausse de prix (+1 % : 10 328 €) contre une hausse de volume (+1 % : 3 145 €).

Le tableau suivant résume la réponse à la gérante : « pourquoi gagnons-nous si peu ? ».

| Question | Ce que nous avons mesuré |
|---|---|
| Combien reste-t-il de 100 € vendus ? | 3,60 € de résultat d'exploitation, 62 € partent en marchandises |
| Pourquoi si peu de gain pour 11 % de ventes en plus ? | Sur chaque euro supplémentaire, 50 centimes de marge brute, 30 centimes de charges nouvelles (dont 12 de marketing et 10 de personnel) : il reste 20 centimes |
| Le résultat progresse-t-il quand même ? | Oui : +127 % ; la marge brute gagne 1,4 point (prix, mix) |
| L'entreprise est-elle plus fragile ou plus solide ? | Plus solide : marge de sécurité de 6,5 % à 12,7 %, levier divisé par deux, endettement de 0,56 à 0,30 |
| Où est l'argent ? | Une partie dort dans le stock : le besoin en fonds de roulement a gagné 19 603 € en deux ans |
| Quel levier compte le plus ? | Un point de prix rapporte 3,3 fois un point de volume |

Trois idées à emporter. **D'abord, un résultat est une cascade, pas un nombre** : on l'explique en comparant deux cascades poste par poste. **Ensuite, la rentabilité, la solidité et la trésorerie sont trois questions différentes** : une entreprise peut gagner de l'argent et en manquer (le stock), ou en gagner peu et se consolider. **Enfin, les coûts n'ont pas tous la même élasticité à l'activité** : c'est la séparation entre fixe et variable qui explique le levier opérationnel, le point mort et le sens d'une décision (prix, volume, canal).

> ⚠️ **Rappel d'honnêteté.** Les comptes de ce chapitre sont **simulés et simplifiés** (TVA fictive, résultat net approché, bilan équilibré par construction, délais constants), le secteur est fictif et la séparation des coûts est celle d'un **modèle** : un comptable ou un contrôleur de gestion réel dispose de plus d'informations (comptes détaillés, traitement des stocks, impôts) et de règles propres à votre pays. Rien ici n'est un avis comptable ou fiscal.

Les chapitres suivants prolongent cette lecture : le chapitre 10 relie les dépenses de marketing aux ventes (coût d'acquisition, retour sur investissement) et le chapitre 13 pousse l'analyse de sensibilité plus loin (par exemple, de combien le volume peut baisser après une hausse de prix).

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.1 à 9.5 (recoupement des comptes, ratios, coûts fixes et variables, rentabilité par canal, hausse de prix ou de volume) et exercices 9.1 à 9.9.
