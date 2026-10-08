# Chapitre 4 : Analytique du risque et de l'assurance

> « Un assureur vend une promesse dont il ne connaît le coût qu'après coup. »


Votre travail à la boutique se passe bien. Un matin, la directrice générale du groupe vous annonce que, pour un trimestre, la direction des risques de deux sociétés voisines (un **petit assureur automobile** et une **petite banque** qui finance des particuliers et des commerces) a besoin d'un analyste. Vous n'y connaissez ni le vocabulaire de l'assurance ni celui du crédit. Dès la première réunion, la directrice des risques pose deux questions :

> « *Nos comptes disent que 2025 a été une bonne année pour l'assurance. Est-ce vrai ? Et à la banque, où se cache le prochain problème, avant qu'il n'apparaisse dans les comptes ?* »

Ce sont des questions de **risque** : on cherche à mesurer ce qui peut coûter de l'argent dans l'avenir, à partir de ce que l'on voit dans le passé. Les deux métiers semblent éloignés, mais ils partagent un point de départ : **on a déjà vendu le produit** (un contrat d'assurance, un prêt) **et l'on ne connaît pas encore son coût final**. Un sinistre déclaré aujourd'hui sera payé dans trois ans ; un prêt octroyé il y a six mois fera peut-être défaut l'an prochain. L'analyse du risque consiste à **estimer ce coût final avant qu'il ne soit connu**, et à **surveiller** que l'estimation ne dérive pas.

> 💡 **Intuition.** Vous avez déjà rencontré cette situation sans la nommer. Un **triangle de développement** (section 4.1) est une **analyse de cohortes** (volume III, chapitre 4) : on suit des groupes d'âge différent et l'on compare à âge égal. Un **ratio sinistres/primes** est un **KPI** (volume III, chapitre 6) dont le numérateur est incomplet. Un **suivi de portefeuille** est un **tableau de bord** (volume IV, chapitre 2) dont chaque chiffre doit se rapprocher de la comptabilité. Ce chapitre applique des outils que vous connaissez à un domaine où les erreurs coûtent cher.

## Le chemin de ce chapitre

Nous suivons la directrice des risques, d'abord à l'assurance, puis à la banque, puis dans l'art de produire des états fiables.

- **4.1 Analyse des sinistres.** Exposition, fréquence, coût moyen, **ratio sinistres/primes** ; pourquoi la dernière année est toujours incomplète ; le **triangle de développement** et la **méthode chain ladder** pour estimer ce qui reste à payer, jugée ensuite avec la vérité ; les **gros sinistres**, qui faussent les comparaisons par segment.
- **4.2 Suivi de portefeuille.** À l'assurance, le mix et la rentabilité par segment ; au crédit, les **tranches de retard**, les **créances douteuses**, les **cohortes d'octroi** comparées à âge égal, la **matrice de transition** des retards, la **concentration**, et une dérive sectorielle qui apparaît en 2025.
- **4.3 Reporting de gestion et réglementaire.** Ce qui distingue les deux familles de rapports ; la **définition unique** de chaque indicateur ; le **rapprochement avec la comptabilité** ; la validation à quatre yeux, les versions et le journal.
- **4.4 ➕ Fréquence, sévérité, ratio sinistres/primes et ratio combiné.** Un **modèle linéaire généralisé** de Poisson (avec exposition) et de Gamma pour comprendre **pourquoi** certains segments perdent de l'argent, et de combien le tarif devrait bouger.
- **4.5 ➕ Indicateurs d'alerte précoce.** Quels signaux précèdent un défaut, comment construire une alerte **sans tricher avec le futur**, et comment l'évaluer au regard de la **charge de travail** du comité de crédit.
- **4.6 ➕ Reporting réglementaire et de gestion pour banques et assureurs.** Des **maquettes génériques d'états** avec leurs **contrôles de cohérence**, leurs rapprochements et la justification des écarts. Aucun format officiel n'est reproduit.

## Les données du chapitre

> 📦 **Les données.** Deux portefeuilles **simulés** (graine fixe, aucune donnée réelle), décrits dans la docstring de `build/donnees_a5.py`. **Assurance automobile** (2021-2025, situation au 31 décembre 2025) : `polices.csv` (30 000 contrats), `expositions.csv` (une ligne par police et par année, avec la prime acquise), `sinistres.csv` (5 113 sinistres déclarés), `paiements.csv` (7 093 règlements). **Crédit** (prêts octroyés de janvier 2022 à juin 2025, suivi mensuel jusqu'en décembre 2025) : `prets.csv` (12 000 prêts), `suivi_mensuel.csv` (environ 230 000 lignes prêt-mois : encours, jours de retard, incidents de paiement, utilisation du découvert). Deux fichiers de **vérité** (`verite_sinistres.csv`, `verite_prets.csv`) donnent le coût final de chaque sinistre et le mois de défaut de chaque prêt : ils **n'existeraient pas dans la vie réelle** et ne servent qu'à **juger a posteriori** nos estimations. Deux petits fichiers du chapitre (`ch04-compta-primes.csv`, `ch04-regularisations.csv`) représentent le « grand livre » comptable fictif de l'assureur.

Un mot sur le cadre. L'assureur et la banque sont **fictifs** : aucun nom, aucun pays, aucune autorité de contrôle, aucune loi réelle n'apparaît. Quand nous parlons de règles « internationales » (Bâle pour les banques, IFRS 9 et IFRS 17 pour les provisions et les contrats d'assurance, Solvabilité pour les assureurs), c'est **à titre d'exemples de familles de règles**, sans reproduire leurs seuils ni leurs formats : les seuils de ce chapitre sont **inventés** et dits tels. Vos calculs de ce chapitre ne sont donc pas des calculs réglementaires.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.7 et exercices 4.1 à 4.12 ; chacun renvoie à la section du livre qui l'éclaire.


## 4.1 Analyse des sinistres

Cette section répond à la première question de la directrice : « 2025 est-elle une bonne année ? ». Pour y répondre sans se tromper, il faut d'abord apprendre à **mesurer** un portefeuille d'assurance (exposition, fréquence, coût, ratio sinistres/primes), puis comprendre pourquoi **la dernière année n'est jamais comparable aux autres**, estimer ce qu'il reste à payer par un **triangle de développement**, et enfin se méfier des **gros sinistres**, qui suffisent à brouiller n'importe quelle comparaison par segment.

### 4.1.1 Ce que l'on mesure : exposition, fréquence, coût moyen et prime pure

Un contrat d'assurance protège pendant une durée. Un contrat qui n'a été en vigueur que six mois n'a pas eu autant d'occasions d'avoir un sinistre qu'un contrat couvert toute l'année : pour comparer des périodes ou des segments, on ne divise donc pas par le nombre de contrats, mais par l'**exposition**, mesurée en **années-police** (une année-police = un contrat couvert pendant un an).

> 📐 **Les quatre grandeurs de base.**
> - **Fréquence** = nombre de sinistres ÷ exposition (en sinistres par année-police) ;
> - **coût moyen** = coût total des sinistres ÷ nombre de sinistres ;
> - **prime pure** = fréquence × coût moyen = coût total ÷ exposition : c'est ce que coûte, en moyenne, une année-police ;
> - **ratio sinistres/primes (S/P)** = coût total des sinistres ÷ primes acquises.

Un exemple à la main. Un assureur a 1 000 contrats : 800 sont couverts toute l'année et 200 seulement six mois. L'exposition est de 800 + 200 × 0,5 = **900 années-police**. Il enregistre 63 sinistres pour un coût total de 283 500 €. La fréquence est 63 ÷ 900 = **7,0 %** par année-police (et non 63 ÷ 1 000 = 6,3 %, qui ignorerait les contrats couverts six mois). Le coût moyen est 283 500 ÷ 63 = **4 500 €**. La prime pure est 0,07 × 4 500 = **315 €** par année-police, ce que l'on retrouve en divisant directement : 283 500 ÷ 900 = 315 €. Si l'assureur facture en moyenne 450 € par année-police, son S/P est 315 ÷ 450 = **70 %**.

La **prime acquise** est la part de la prime qui correspond à la période de couverture déjà écoulée : une prime annuelle de 600 € encaissée le 1ᵉʳ juillet n'est acquise qu'à moitié au 31 décembre (300 €). Mettre au numérateur des sinistres d'une période et au dénominateur des primes encaissées pour une autre période est une erreur classique : les deux doivent porter sur **la même période de couverture**.

Voici le tableau annuel de notre assureur. Le fichier `expositions.csv` donne l'exposition et la prime acquise de chaque police et de chaque année ; `sinistres.csv` donne les sinistres, rattachés à leur **année de survenance** (l'année où l'accident a eu lieu, pas celle où il est déclaré ou payé).

```python
t = bil[["exposition", "primes", "nb", "frequence", "cout_moyen", "sp_declare"]].copy()
t["primes"] = (t["primes"] / 1e3).round(0)
print(t.round({"exposition": 0, "cout_moyen": 0, "frequence": 3, "sp_declare": 3}).to_string())
```
<!--sortie-->
```text
       exposition   primes    nb  frequence  cout_moyen  sp_declare
annee                                                              
2021       5408.0   2471.0   350      0.065      4255.0       0.603
2022      11254.0   5226.0   816      0.073      4092.0       0.639
2023      15168.0   7178.0  1088      0.072      4383.0       0.664
2024      18304.0   8847.0  1288      0.070      5157.0       0.751
2025      21355.0  10517.0  1571      0.074      5516.0       0.824
```

Les primes sont en milliers d'euros. Le **coût d'un sinistre** est ici la **charge dossier par dossier** : ce qui a déjà été payé, plus la **réserve** que le gestionnaire a mise de côté pour ce qu'il reste à payer sur les dossiers ouverts.

> 🧭 **En pratique.** La première chose à vérifier dans un tableau de ce genre est la **cohérence des périodes** : le nombre de lignes d'exposition croît avec le portefeuille (9 000 police-années en 2021, 23 000 en 2025), et c'est bien l'exposition, pas le nombre de contrats, qui entre au dénominateur.

### 4.1.2 Ratio sinistres/primes et ratio combiné

Le tableau montre une tendance préoccupante : le S/P déclaré passe de **60 %** en 2021 à **82 %** en 2025, alors que la fréquence ne bouge presque pas (6,5 à 7,4 %). C'est donc le **coût moyen** qui monte (de 4 255 € à 5 516 €) sans que les primes suivent.

Un S/P seul ne dit pas si l'assureur gagne ou perd de l'argent, parce qu'il faut aussi payer le fonctionnement : les salaires, les commissions des intermédiaires, les systèmes, les locaux. On les regroupe dans les **frais**, exprimés en proportion des primes acquises. Dans notre exemple fictif, les frais représentent **28 %** des primes. Le **ratio combiné** additionne les deux :

> 📐 **Ratio combiné** = S/P + ratio de frais = (sinistres + frais) ÷ primes acquises.
> En dessous de 100 %, l'activité d'assurance seule (avant produits financiers) gagne de l'argent ; au-dessus de 100 %, elle en perd.

Avec 28 % de frais, le seuil d'équilibre technique est un S/P de **72 %**. À 60 % (2021), le ratio combiné est de 88 % : 12 centimes de profit technique pour 1 € de prime. À 82 % (2025), il est de **110 %** : 10 centimes de perte pour 1 € de prime. La réponse à la première moitié de la question de la directrice semble donc être **non, 2025 n'est pas une bonne année**, mais elle est encore provisoire. Les chiffres de 2025, en particulier, comportent deux faiblesses que les sections suivantes lèvent.

### 4.1.3 Le piège de la dernière année

Les sinistres d'une année ne sont jamais tous connus le 31 décembre de cette année-là. Deux phénomènes se superposent.

- **Les déclarations tardives.** Un accident survenu le 28 décembre peut n'être déclaré que mi-janvier. Les sinistres « survenus mais pas encore déclarés » s'appellent, en anglais, *incurred but not reported* (**IBNR**), et l'on parle d'IBNR en français aussi.
- **Les paiements tardifs et les réserves.** Un dossier déclaré en mars peut être réglé en deux mois (un pare-brise) ou en trois ans (un dommage corporel). Tant que le dossier est ouvert, son coût final est une **estimation** (la réserve), qui peut se tromper dans les deux sens.

Les délais de déclaration de notre assureur se mesurent directement.

```python
s = d["sin"]
delai = (s["date_declaration"] - s["date_survenance"]).dt.days
print(delai.describe(percentiles=[.5, .9, .99]).round(0).to_string())
print("déclarés après plus de 30 jours :", O.pct((delai > 30).mean(), 1))
```
<!--sortie-->
```text
count    5113.0
mean       20.0
std        20.0
min         0.0
50%        14.0
90%        46.0
99%        92.0
max       213.0
déclarés après plus de 30 jours : 21,0 %
```

La moitié des sinistres est déclarée en deux semaines, mais une petite partie arrive très tard (le plus long délai observé dépasse sept mois). Ce retard a une conséquence visible sur le dernier trimestre.

```python
s25 = s[s["an"] == 2025]
print(s25.groupby(s25["date_survenance"].dt.quarter).size().to_string())
```
<!--sortie-->
```text
date_survenance
1    365
2    399
3    468
4    339
```

Le quatrième trimestre compte **339** sinistres contre **468** au troisième, soit un recul de 28 %. Faut-il y voir une amélioration ? Non : l'assureur ne connaît pas encore les sinistres de décembre dont la déclaration n'est pas arrivée. Grâce au fichier de vérité, nous savons que **114 sinistres** survenus en 2025 ne sont pas encore déclarés au 31 décembre, pour un coût final de 414 k€, soit environ 5 % du coût de l'année.


> ⚠️ **Piège : comparer la dernière année brute aux autres.** Une baisse du nombre de sinistres, du coût payé ou du S/P sur la dernière période est presque toujours **un artefact du retard**. Avant de commenter une variation récente, on demande : « les données de cette période sont-elles aussi complètes que celles des périodes précédentes ? ». Si la réponse est non, on **complète** (par une méthode comme celle de la section suivante) ou l'on **s'abstient**.

### 4.1.4 Le triangle de développement

Pour estimer ce qu'il reste à payer, les actuaires ont inventé un outil simple : le **triangle de développement**. Chaque ligne est une **année de survenance** ; chaque colonne est un **délai** (le nombre d'années écoulées entre l'année de survenance et l'année du paiement). La cellule (2022, délai 1) contient la somme payée en 2023 pour des sinistres survenus en 2022. On y met les paiements **cumulés**. Comme on s'arrête au 31 décembre 2025, la partie inférieure droite du tableau est **vide : c'est l'avenir**, d'où la forme de triangle.

Un exemple à la main, avec trois années. Les cumuls (en milliers d'euros) sont :

| Année de survenance | Délai 0 | Délai 1 | Délai 2 |
|---|---|---|---|
| A | 100 | 160 | 176 |
| B | 120 | 190 | *à prévoir* |
| C | 140 | *à prévoir* | *à prévoir* |

La **méthode chain ladder** (« échelle à chaînes ») repose sur une idée : **le rythme de paiement des années passées se reproduira**. On mesure ce rythme par des **facteurs de développement**, c'est-à-dire le rapport entre deux colonnes consécutives, calculé sur toutes les années où l'on connaît les deux.

- Facteur du délai 0 au délai 1 : (160 + 190) ÷ (100 + 120) = 350 ÷ 220 = **1,59** : les années passées ont payé 59 % de plus pendant la deuxième année qu'elles n'avaient payé dès la première.
- Facteur du délai 1 au délai 2 : 176 ÷ 160 = **1,10** (une seule année l'a observé).

On prolonge ensuite chaque ligne jusqu'à l'**ultime** (le coût final) en multipliant le dernier cumul observé par les facteurs qui restent : B donnera 190 × 1,10 = **209** ; C donnera 140 × 1,59 × 1,10 = **245**. Ce qu'il reste à payer est l'ultime moins le déjà-payé : 0 pour A, 19 pour B, 105 pour C, soit **124** au total.

Appliquons maintenant la méthode au triangle de l'assureur.

```python
inc, cum = O.triangle(d)
f, t_cl = O.chain_ladder(cum)
print("facteurs :", np.round(f, 3))
print((cum / 1e6).round(2).to_string())
```
<!--sortie-->
```text
facteurs : [2.222 1.197 1.101 1.067]
delai     0     1     2     3     4
an                                 
2021   0.36  1.02  1.25  1.40  1.49
2022   1.20  2.51  3.00  3.28   NaN
2023   1.59  3.36  3.99   NaN   NaN
2024   2.00  4.56   NaN   NaN   NaN
2025   2.60   NaN   NaN   NaN   NaN
```


![Le triangle de développement des paiements (cumulés, en millions d'euros) : chaque ligne est une année de survenance, chaque colonne un délai. La partie basse droite correspond à des paiements futurs, qu'il reste à prévoir.](figures/ch04-triangle.png)


Les facteurs se lisent de gauche à droite : les paiements doublent presque au cours de la deuxième année (facteur 2,22), puis augmentent de 20 %, de 10 % et de 7 %. Le produit des quatre facteurs vaut **3,1** : à la fin de l'année de survenance, un peu moins du tiers du coût final (32 %) seulement a été payé. C'est pour cela que le paiement d'une année récente ne dit presque rien de son coût.

> 💡 **Pourquoi des facteurs et pas des pourcentages ?** On pourrait raisonner en « part payée à chaque délai » (32 %, 71 %, 85 %…). C'est équivalent, mais les facteurs se calculent **directement** sur les données observées, sans hypothèse supplémentaire, et se combinent par simple multiplication.

La méthode suppose que le **schéma de paiement est stable** : mêmes types de sinistres, mêmes pratiques de règlement, même inflation. Dès que l'un de ces éléments change (un nouveau directeur des sinistres règle plus vite, une réforme allonge les procédures), le passé ne ressemble plus à l'avenir et le résultat est faux sans qu'aucun calcul ne le signale.

### 4.1.5 Juger l'estimation avec la vérité

Dans la vie réelle, on ne saurait jamais si l'estimation était bonne avant des années. Ici, le fichier de vérité nous donne le **coût final réel** de chaque année. Comparons, année par année, trois choses : l'estimation **dossier par dossier** (payé + réserves des gestionnaires), l'estimation **chain ladder**, et la **vérité**.

```python
f, cmp = O.comparer_provisions(d)
print((cmp[["paye", "charge_dossiers", "ultime_cl", "ultime_vrai"]] / 1e6).round(2).to_string())
print((cmp[["ecart_cl", "ecart_dossiers"]] * 100).round(1).to_string())
```
<!--sortie-->
```text
      paye  charge_dossiers  ultime_cl  ultime_vrai
2021  1.49             1.49       1.49         1.49
2022  3.28             3.34       3.50         3.33
2023  3.99             4.77       4.68         4.67
2024  4.56             6.64       6.41         6.52
2025  2.60             8.67       8.13         8.73
      ecart_cl  ecart_dossiers
2021       0.0             0.0
2022       5.1             0.2
2023       0.2             2.0
2024      -1.7             1.8
2025      -6.9            -0.7
```


![À gauche : le ratio sinistres/primes par année de survenance selon trois estimations (dossiers, chain ladder, vérité). À droite : le ratio par tranche d'âge du conducteur, sur 2021-2024.](figures/ch04-sp-annee-classe.png)

Trois enseignements.

1. **Les deux méthodes se trompent peu, et dans des directions différentes.** Pour 2024, le chain ladder est à −1,7 % de la vérité et les dossiers à +1,8 %. Pour 2025, le chain ladder **sous-estime de 6,9 %** (8,13 M€ contre 8,73 M€), tandis que l'estimation par dossiers est à −0,7 % : le chain ladder ne voit que les paiements, or il n'y en a eu que 2,6 M€ sur 2025, et une toute petite variation du premier facteur se multiplie par trois.
2. **Les facteurs de la queue sont fragiles.** Pour 2022, le chain ladder **surestime de 5,1 %** : le dernier facteur (1,07, du délai 3 au délai 4) n'a été observé que sur **une seule année** (2021) : un seul point ne dit rien de la variabilité. Quand un facteur repose sur une seule observation, il faut le dire, ou le remplacer par un jugement.
3. **Aucune méthode ne dispense de regarder les dossiers ouverts.** Le chain ladder indique un ordre de grandeur global ; les gestionnaires de sinistres connaissent chaque dossier. La pratique est de comparer les deux et d'expliquer l'écart, pas de choisir arbitrairement.

> ⚠️ **Piège : un chiffre unique pour les provisions.** Une provision est une **estimation**, pas une mesure. Présentée sans fourchette, elle donne une fausse impression de précision. Les actuaires utilisent des méthodes plus riches pour fabriquer une distribution (bootstrap sur le triangle, par exemple) ; notre chain ladder simple n'en donne pas, et c'est une limite à dire explicitement dans le rapport.

Avec les estimations complétées, on peut reprendre la question de départ. Le S/P ultime de 2025 est de **77 %** par le chain ladder, de 82 % par les dossiers, de 83 % d'après la vérité. Dans tous les cas, il dépasse nettement le seuil de 72 % : la **réponse** à la directrice est donc : « *non, 2025 n'est pas une bonne année : même en tenant compte de ce qui n'est pas encore connu, le ratio combiné dépasse 100 %. Et le S/P augmente depuis 2021.* »

### 4.1.6 Les gros sinistres, les segments trompeurs

Le coût d'un sinistre n'est pas réparti comme la taille des habitants d'une ville : il est **très inégal**. Dans notre portefeuille, le sinistre médian coûte 1 962 € mais le plus coûteux dépasse 474 000 € ; **31 sinistres** dépassent 100 000 € ; et les 51 plus gros sinistres (1 % du nombre) représentent **28,6 %** du coût total. On parle de **queue lourde**.


Une conséquence directe : comparer des S/P de segments un peu petits est **dangereux**. Comparons le S/P des quatre zones sur 2021-2024.

```python
brut = O.sp_par_segment(d, "zone")
plaf = O.sp_par_segment(d, "zone", ecreter=50000)
print((pd.DataFrame({"brut": brut, "plafonné": plaf}) * 100).round(1).to_string())
```
<!--sortie-->
```text
      brut  plafonné
zone                
A     84.6      65.2
B     58.4      50.4
C     63.0      54.0
D     67.5      56.0
```

La zone A est la plus mauvaise (S/P de **85 %**, contre 58 % pour la zone B). Il serait tentant de recommander une hausse de tarif de 30 % dans la zone A. Mais la zone A est aussi celle qui contient le plus gros dossier de la période (311 000 €). Quand on **plafonne** chaque sinistre à 50 000 €, le S/P de la zone A passe à **65 %**, et l'écart avec les autres zones se réduit sans disparaître. Pour savoir si cet écart est une réalité ou du hasard, on calcule un **intervalle de confiance par bootstrap** : on retire au hasard (avec remise) les sinistres de chaque zone, on recalcule le S/P, et l'on répète mille fois.


![Ratio sinistres/primes par zone (2021-2024), avant et après plafonnement de chaque sinistre à 50 000 €, avec l'intervalle à 90 % obtenu par bootstrap.](figures/ch04-zone-gros-sinistre.png)

Le S/P brut de la zone A est compris, à 90 %, entre 70 % et 102 % ; celui de la zone D, entre 56 % et 80 %. Les deux intervalles **se chevauchent** : avec les données brutes, on ne peut pas affirmer que la zone A est plus mauvaise que la zone D. Après plafonnement, l'intervalle de la zone A (de 58 à 73 %) reste au-dessus de celui de la zone B (de 46 à 55 %), mais chevauche encore ceux de C et D.

> 🧭 **En pratique : trois façons de traiter les gros sinistres.**
> 1. **Plafonner** chaque sinistre à un seuil (par exemple 50 000 €) pour comparer les segments sur la sinistralité « courante », puis **ajouter une charge pour les gros sinistres**, calculée sur l'ensemble du portefeuille (où ils sont assez nombreux pour être stables).
> 2. **Analyser séparément** les gros sinistres : combien, quelle nature, quelle évolution.
> 3. **Toujours accompagner un S/P de segment d'un intervalle** ou, au minimum, d'un effectif (nombre de sinistres et nombre de sinistres graves).

> ✅ **À retenir.** (1) On mesure un portefeuille d'assurance en **fréquence** (par année-police), **coût moyen**, **S/P** et **ratio combiné** ; (2) la **dernière année est incomplète** (déclarations et paiements tardifs) : on la complète ou on s'abstient ; (3) le **triangle de développement** et la méthode **chain ladder** estiment ce qu'il reste à payer, sous l'hypothèse d'un rythme stable, avec des facteurs de queue fragiles ; (4) **les gros sinistres** rendent trompeurs les S/P des petits segments : plafonner, analyser à part, donner un intervalle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.1 (fréquence, coût, S/P et combiné), application 4.2 (un triangle à la main), exercices 4.1 à 4.3.


## 4.2 Suivi de portefeuille

Un **portefeuille** est l'ensemble des contrats (ou des prêts) qu'une société détient à un moment donné. Le **suivi** consiste à le lire régulièrement, par segment et dans le temps, pour repérer ce qui se dégrade avant que les comptes ne le montrent. Nous commençons par l'assurance (où la question est « quels segments perdent de l'argent ? »), puis nous passons au crédit, qui demande des outils propres : les **tranches de retard**, les **cohortes** lues à âge égal, la **matrice de transition**, la **concentration**.

### 4.2.1 À l'assurance : mix et rentabilité par segment

On appelle **mix** la répartition du portefeuille entre ses segments (âge, zone, usage, canal de vente…). Un portefeuille est rentable si **chaque segment** paie, ou si les segments qui perdent sont assez petits pour être compensés. Pour le savoir, on met côte à côte, pour chaque segment, sa **part de l'exposition**, sa **part des primes**, sa **fréquence**, son **S/P** et son **ratio combiné**.

```python
t = O.table_sp(d, "classe_age").loc[["< 25 ans", "25-39 ans", "40-59 ans", "60 ans et +"]]
t["part_expo"] = t["exposition"] / t["exposition"].sum()
t["part_primes"] = t["primes"] / t["primes"].sum()
t["resultat_k"] = t["primes"] * (1 - t["combine"]) / 1e3
print((t[["part_expo", "part_primes", "frequence", "sp", "combine"]] * 100).round(1).join(t["resultat_k"].round(0)).to_string())
```
<!--sortie-->
```text
             part_expo  part_primes  frequence     sp  combine  resultat_k
classe_age                                                                
< 25 ans           7.4         18.2       22.5  102.1    130.1     -1301.0
25-39 ans         25.6         28.3        7.1   62.7     90.7       626.0
40-59 ans         48.4         36.8        5.1   57.5     85.5      1267.0
60 ans et +       18.5         16.7        6.0   60.2     88.2       468.0
```

Les moins de 25 ans représentent **7,4 %** de l'exposition et **18 %** des primes : ils paient cher, mais pas assez. Leur fréquence est de **22,5 %** par année-police, contre 5,1 % pour les 40-59 ans, soit **4,4 fois plus** ; leur S/P atteint **102 %** et leur ratio combiné **130 %**. Ce segment perd à lui seul environ **1,3 million d'euros** sur quatre ans, que gagnent les autres segments. Le tarif corrige le risque dans le bon sens, mais **pas assez** : nous le mesurerons avec un modèle en section 4.4.

> ⚠️ **Piège : lire un ratio par segment sans regarder le volume.** Un segment qui a un très mauvais ratio mais 3 % de l'exposition ne se traite pas comme un segment qui pèse 30 %. Et, on l'a vu en 4.1.6, un ratio de petit segment peut n'être que du hasard : un tableau de portefeuille sérieux donne, pour chaque ligne, **l'effectif et un intervalle**.

### 4.2.2 Au crédit : encours, tranches de retard et créances douteuses

La banque finance des particuliers (crédits à la consommation) et des professionnels (commerces, entreprises de services, du bâtiment, de la restauration, de l'industrie). Au total, **12 000 prêts** ont été octroyés de janvier 2022 à juin 2025, pour **180,7 M€** (9 062 prêts à des particuliers, 2 938 à des professionnels ; le prêt médian est de 9 900 €). Chaque mois, pour chaque prêt encore actif, on connaît l'**encours** (le capital restant dû) et le **nombre de jours de retard** sur la dernière échéance.

On range les prêts dans cinq **tranches de retard** : **0** (à jour), **1 à 29 jours**, **30 à 59 jours**, **60 à 89 jours**, et **90 jours ou plus**. La dernière est conventionnelle : on parle de **défaut** à partir de 90 jours de retard, et de **créances douteuses** pour les encours des prêts en défaut. Cette convention est un choix de gestion ; les cadres réglementaires internationaux en proposent des définitions plus détaillées, qui ne sont pas reproduites ici.

Trois indicateurs se déduisent de cette classification.

- Le **taux de créances douteuses** = créances douteuses ÷ (encours sain + créances douteuses).
- Les **provisions** : une somme mise de côté pour absorber les pertes attendues. Chaque tranche reçoit un **taux de provisionnement** : plus le retard est ancien, plus la probabilité de perte est grande. Pour l'exemple, nous prenons des taux **fictifs** (0,5 % pour les prêts à jour, 2 %, 10 %, 30 % puis 55 % pour la tranche 90+).
- Le **taux de couverture** = provisions totales ÷ créances douteuses : il dit quelle part des créances douteuses est « déjà couverte » par les provisions.


Une limite du jeu de données doit être dite avant de calculer. Le suivi mensuel d'un prêt s'arrête **au mois du défaut** : on ne sait pas ce qui se passe ensuite (recouvrement, abandon de créance). Pour mesurer le stock de créances douteuses, nous faisons donc une **hypothèse de simplification** : un prêt entré en défaut reste douteux **douze mois** avant d'être passé en perte. C'est un choix d'école ; une banque réelle suit ses créances douteuses jusqu'à leur extinction.

```python
st = O.stock_mensuel(d)
cols = ["encours", "douteux", "taux_douteux", "couverture"]
sel = st.loc[pd.to_datetime(["2024-12-01", "2025-06-01", "2025-12-01"]), cols]
sel[["encours", "douteux"]] = (sel[["encours", "douteux"]] / 1e6).round(1)
print(sel.round(3).to_string())
```
<!--sortie-->
```text
            encours  douteux  taux_douteux  couverture
2024-12-01     70.7      2.9         0.039       0.745
2025-06-01     76.2      4.3         0.054       0.674
2025-12-01     56.7      4.5         0.073       0.625
```

Le taux de créances douteuses passe de **3,9 %** (décembre 2024) à **5,4 %** (juin 2025), puis à **7,3 %** (décembre 2025), et le taux de couverture baisse de 75 % à 62 %. Faut-il s'alarmer ? Il faut d'abord regarder le **dénominateur** : l'encours sain **baisse** de 76,2 à 56,7 M€ entre juin et décembre 2025. La raison est un fait propre à notre jeu de données : **aucun prêt n'a été octroyé après juin 2025**, le portefeuille s'éteint donc par amortissement, alors que les créances douteuses (entrées en défaut sur les douze derniers mois) ne diminuent presque pas. Une partie de la hausse du taux est donc **mécanique**.

> 💡 **Intuition.** Un ratio peut monter parce que son numérateur augmente **ou** parce que son dénominateur diminue. Sur un portefeuille qui s'éteint, ou sur un portefeuille jeune qui grossit vite, le taux de créances douteuses est un mauvais thermomètre. C'est une raison de plus pour suivre les **cohortes d'octroi** à âge égal, qui ne dépendent pas de la taille du portefeuille à la date de mesure.

### 4.2.3 Cohortes d'octroi : comparer à âge égal

Une **cohorte d'octroi** (ou **millésime**) regroupe les prêts accordés pendant une même période : ici, un semestre. Pour savoir si un millésime est plus risqué qu'un autre, la comparaison la plus simple consiste à calculer, pour chaque millésime, **la part des prêts passés en défaut**. Elle est trompeuse, comme le montre un exemple à la main.

> Le millésime « 2023 S1 » compte 1 000 prêts suivis depuis 24 mois : 90 sont en défaut, soit **9,0 %**. Le millésime « 2025 S1 » compte 1 000 prêts suivis depuis 6 mois : 18 sont en défaut, soit **1,8 %**. Le second est-il cinq fois meilleur ? Non : il a eu **quatre fois moins de temps** pour se dégrader. À six mois, le premier millésime en avait 20 sur 1 000, soit 2,0 % : presque identique.

Il faut donc comparer **à âge égal** : pour chaque millésime et chaque âge (en mois depuis l'octroi), on calcule le **risque de défaut du mois** (défauts du mois ÷ prêts encore suivis à cet âge), puis on **cumule** : la probabilité d'avoir fait défaut à l'âge *a* est 1 − Π(1 − risque du mois). La courbe s'arrête quand moins de 300 prêts restent suivis : c'est la **troncature à droite** (volume III, chapitre 4).

```python
cc = O.courbes_cohortes(d)
brut = O.defauts_par_millesime_brut(d)
print(pd.DataFrame({"brut": brut * 100}).join(cc.loc[[12, 18]].T * 100, how="left").round(1).to_string())
```
<!--sortie-->
```text
           brut   12    18
millesime                 
2022 S1     8.3  4.1   7.6
2022 S2     8.9  5.2   7.9
2023 S1     9.2  5.0   8.1
2023 S2     9.1  5.3   8.3
2024 S1    11.3  6.7  11.4
2024 S2     6.2  5.7   NaN
2025 S1     2.9  NaN   NaN
```


![À gauche, la part brute de prêts en défaut par millésime (trompeuse : les récents ont eu moins de temps). À droite, le défaut cumulé à âge égal : le millésime 2024 S1 se détache.](figures/ch04-cohortes.png)

Le taux brut classe les millésimes de façon absurde : 2025 S1 paraît le meilleur (2,9 %), 2024 S2 aussi (6,2 %). À âge égal, l'image est différente : à 12 mois, le millésime **2024 S1** est à **6,7 %** de défaut contre 4,1 à 5,3 % pour les quatre premiers millésimes ; à 18 mois, il est à **11,4 %** contre 7,6 à 8,3 %. C'est un millésime **plus risqué**, ce qui correspond à une explication plausible (des critères d'octroi relâchés au premier semestre 2024 : nous le savons parce que le simulateur l'a programmé, mais un analyste le *découvrirait* par cette analyse et irait vérifier auprès de la direction du crédit). Le millésime suivant (2024 S2) retrouve une courbe proche des autres.

> ⚠️ **Piège : une cohorte récente ne se juge pas sur son taux brut.** Un millésime qui n'a que trois mois ne dit rien de ses défauts à dix-huit mois. Les courbes à âge égal sont le seul outil honnête, **avec leurs effectifs** (on ne garde que les âges où il reste assez de prêts observés).

### 4.2.4 La matrice de transition des retards

Un prêt en retard de 15 jours ce mois-ci sera-t-il à jour, toujours en retard, ou plus en retard le mois prochain ? La **matrice de transition** répond : chaque ligne est la tranche de départ, chaque colonne la tranche d'arrivée un mois plus tard, chaque case la **part des prêts** qui font ce passage. On parle aussi de **roll rates** (taux de glissement).

Un exemple à la main. Sur 100 prêts à jour, 95 le restent, 4 passent à « 1-29 jours » et 1 sort (remboursé). Sur 50 prêts de la tranche « 1-29 jours », 40 reviennent à jour, 5 y restent et 5 glissent en « 30-59 jours ». La ligne « 0 » est donc (95 %, 4 %, 0 %, …, 1 %) et la ligne « 1-29 » est (80 %, 10 %, 10 %, …).

```python
n, p = O.matrice_transition(d)
print((p * 100).round(1).to_string())
```
<!--sortie-->
```text
suiv        0  1-29  30-59  60-89    90+  Sortie
tranche                                         
0        94.2   3.7    0.4    0.0    0.1     1.7
1-29     81.1   9.8    7.4    0.0    0.0     1.8
30-59    55.9   2.3    0.1   40.8    0.0     0.8
60-89     0.0   0.0    0.0    0.0  100.0     0.0
```


![Matrice de transition mensuelle entre tranches de retard (en pourcentage de la ligne). La colonne « Sortie » regroupe les prêts remboursés ou arrivés à échéance.](figures/ch04-transitions.png)

La lecture se fait ligne par ligne. Un prêt à jour le reste dans **94,2 %** des cas ; il passe en retard de 1 à 29 jours dans 3,7 % des cas ; 0,1 % des prêts à jour passent **directement** en défaut (ce sont des défauts « brutaux », sans retard préalable). Un prêt en retard de **30 à 59 jours** revient à jour dans 55,9 % des cas, mais glisse vers 60-89 jours dans **40,8 %** des cas. Un prêt de la tranche 60-89 jours passe en défaut **dans 100 % des cas**.

> ⚠️ **Cette dernière valeur est une simplification du simulateur.** Dans nos données simulées, aucun prêt en retard de 60 à 89 jours ne se redresse : c'est une propriété de la façon dont le simulateur fabrique les retards avant un défaut. Dans la réalité, certains prêts se régularisent, et le taux de 100 % serait nettement plus bas. Retenez la **méthode**, pas ce chiffre.

Cette matrice permet de passer du mois à un **horizon**. En la multipliant par elle-même (en rendant « 90+ » et « Sortie » absorbants, c'est-à-dire sans retour), on obtient la probabilité d'être en défaut dans 1, 3, 6 ou 12 mois selon la tranche de départ.

> 📐 **Pour qui veut la formule.** Si *P* est la matrice mensuelle (avec les états absorbants), la probabilité d'être dans l'état *j* dans *h* mois en partant de *i* est l'élément (*i*, *j*) de *P*ʰ. C'est le principe des chaînes de Markov ; l'hypothèse est que les transitions d'un mois ne dépendent que de l'état présent et sont stables dans le temps.

```python
print(O.proba_defaut_horizon(n).mul(100).round(1).to_string())
```
<!--sortie-->
```text
          1      3      6      12
0        0.1    0.5    1.6    3.7
1-29     0.0    3.2    4.5    6.5
30-59    0.0   41.0   41.6   42.9
60-89  100.0  100.0  100.0  100.0
```

Un prêt à jour fait défaut dans les 6 mois avec une probabilité de **1,6 %** ; un prêt en retard de moins de 30 jours, de **4,5 %** ; un prêt en retard de 30 à 59 jours, de **41,6 %**. On tient là un **outil de provisionnement** (les taux de provision par tranche doivent croître comme ces probabilités) et un **outil d'alerte** (la tranche 30-59 jours est un signal fort). La section 4.5 va plus loin en cherchant des signaux **avant** les premiers retards.

### 4.2.5 La concentration du portefeuille

Même si chaque prêt est sain, un portefeuille peut être **fragile** parce qu'il dépend trop d'un secteur, d'une région, d'un client. La **concentration** mesure cette dépendance. La mesure la plus simple est la **part** de chaque catégorie dans l'encours ; un indicateur de synthèse est l'**indice de Herfindahl-Hirschman** (HHI), la **somme des carrés des parts**.

> 📐 **HHI.** Pour *n* catégories de parts *s*₁, …, *s*ₙ (somme égale à 1) : HHI = Σ *s*ᵢ². Il vaut 1/*n* quand toutes les parts sont égales (diversification maximale) et 1 quand tout est dans une seule catégorie.

Par exemple, avec quatre catégories à 40 %, 30 %, 20 % et 10 % : 0,16 + 0,09 + 0,04 + 0,01 = **0,30**, à comparer à 1/4 = 0,25 pour une répartition égale.

```python
conc = O.concentration(d, "2025-06-01")
reg = O.concentration(d, "2025-06-01", "region")
pro = conc.drop("Particuliers") / conc.drop("Particuliers").sum()
print((conc * 100).round(1).to_dict())
print("HHI secteurs :", round(O.hhi(conc), 3), "| professionnels seuls :", round(O.hhi(pro), 3), "| régions :", round(O.hhi(reg), 3))
```
<!--sortie-->
```text
{'Particuliers': 48.7, 'Commerce': 16.3, 'Services': 13.1, 'Bâtiment': 9.9, 'Restauration': 7.0, 'Industrie': 5.0}
HHI secteurs : 0.298 | professionnels seuls : 0.232 | régions : 0.26
```

Au 30 juin 2025, les particuliers représentent **48,7 %** de l'encours sain ; le secteur le plus exposé parmi les professionnels est le **Commerce** (16,3 % de l'encours, soit **32 %** de l'encours professionnel). Le HHI des secteurs vaut **0,30** (minimum possible avec six catégories : 0,17), celui des professionnels seuls **0,23** (minimum 0,20) et celui des régions **0,26** (minimum 0,25 pour quatre régions) : les régions sont **très bien réparties**, les secteurs un peu moins.

La concentration n'est un risque que si elle rencontre un **choc** : un secteur qui se dégrade. C'est ce que montre la sous-section suivante.

### 4.2.6 Une dérive à repérer : Commerce et Restauration en 2025

Pour détecter une dérive, on compare le **taux de défaut** de chaque secteur sur deux périodes. Comme les prêts sont à des âges différents, on calcule un taux par **prêt-mois** (défauts ÷ nombre de prêts suivis dans le mois) que l'on annualise (multiplié par 12), et l'on y ajoute un **intervalle** fondé sur le nombre de défauts (loi de Poisson).

```python
g = O.risque_secteur(d)
a = g.pivot(index="secteur", columns="periode", values=["dfl", "taux"])
a["taux"] = (a["taux"] * 100).round(1)
print(a.loc[["Commerce", "Restauration", "Bâtiment", "Services", "Industrie", "Particuliers"]].to_string())
```
<!--sortie-->
```text
                dfl         taux      
periode       apres  avant apres avant
secteur                               
Commerce       53.0   27.0   8.8   6.0
Restauration   22.0   10.0   7.7   4.3
Bâtiment       20.0   17.0   5.4   6.0
Services       17.0   13.0   3.4   3.3
Industrie      10.0    4.0   5.1   2.7
Particuliers  285.0  214.0   4.7   4.5
```


![À gauche, taux de défaut annuel pour 100 prêts par secteur en 2024 et en 2025, avec intervalle à 95 %. À droite, la part de chaque secteur dans l'encours sain et l'indice de concentration.](figures/ch04-secteurs.png)

Le taux de défaut du **Commerce** passe de **6,0** à **8,8** défauts par an pour 100 prêts, celui de la **Restauration** de **4,3** à **7,7**. Pris séparément, chaque secteur a un intervalle large (dix défauts seulement pour la Restauration en 2024). En les regroupant, la comparaison devient plus nette : 37 défauts en 2024 et 75 défauts en 2025 pour les deux secteurs ensemble, soit **5,5 puis 8,5** défauts par an pour 100 prêts (un facteur 1,5). Un test sur la répartition des défauts entre les deux périodes (test binomial, en tenant compte des prêts-mois de chaque période) donne une **p-valeur de 0,03** : la hausse n'est probablement pas due au hasard. D'autres secteurs montrent aussi des variations (l'industrie passe de 4 à 10 défauts) mais avec **trop peu de défauts** pour conclure.


La dérive de ces deux secteurs rencontre une **concentration** : ils représentent 23 % de l'encours sain. C'est exactement le genre de situation qu'un tableau de suivi doit signaler à la directrice : « *deux secteurs qui pèsent près du quart du portefeuille voient leur taux de défaut augmenter de moitié ; nous recommandons d'examiner les nouveaux octrois dans ces secteurs et de revoir les provisions.* » Cette phrase **n'affirme pas la cause** : le simulateur nous la dit (un choc programmé sur 2025), mais dans la réalité l'analyste signalerait le fait, proposerait des hypothèses (conjoncture, saisonnalité, un lot de dossiers particulier) et demanderait à la direction du crédit de les vérifier.

> ✅ **À retenir.** (1) À l'assurance, le **mix** et le **ratio par segment** (avec effectifs et intervalles) montrent où le portefeuille perd de l'argent ; (2) au crédit, on range les prêts en **tranches de retard** et l'on suit les **créances douteuses**, le **taux de couverture** et leurs **dénominateurs** ; (3) les **cohortes d'octroi** se comparent **à âge égal**, jamais sur le taux brut ; (4) la **matrice de transition** donne des probabilités de défaut par tranche et à différents horizons ; (5) la **concentration** (parts, HHI) mesure une fragilité qui devient un risque quand un choc la touche.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.3 (cohortes à âge égal), application 4.4 (matrice de transition et probabilités à horizon), exercices 4.4 à 4.6.


## 4.3 Reporting de gestion et réglementaire

Un analyste de banque ou d'assurance passe une grande partie de son temps à produire des **états** : des tableaux d'indicateurs, envoyés chaque mois ou chaque trimestre à la direction, parfois au superviseur. Leur point commun avec tout ce que vous avez vu dans ce livre est qu'un chiffre y est lu par quelqu'un qui **décide**. Leur particularité est que l'erreur y est **coûteuse** : une décision fausse, une sanction, une perte de confiance. Cette section décrit ce qui distingue les deux grandes familles d'états, puis les quatre habitudes qui les rendent fiables : une **définition unique**, un **rapprochement** avec la comptabilité, une **validation à quatre yeux**, un **journal**.

### 4.3.1 Deux familles de rapports

Le **reporting de gestion** sert à piloter : il est lu par la direction, le comité de crédit, les équipes de souscription. Sa forme et ses indicateurs sont **choisis par l'entreprise**. Le **reporting réglementaire** est exigé par une **autorité de contrôle** (le « superviseur ») : sa forme, ses définitions et ses échéances sont **imposés de l'extérieur**.

| | Reporting de gestion | Reporting réglementaire |
|---|---|---|
| **Qui lit** | direction, comités, responsables d'équipe | superviseur, parfois le public |
| **Qui fixe les définitions** | l'entreprise | une règle extérieure, qu'il faut appliquer à la lettre |
| **Fréquence** | adaptée au pilotage (hebdomadaire, mensuelle) | imposée (trimestrielle, annuelle…) |
| **Forme** | libre, lisible | modèles imposés, cases numérotées |
| **Délai** | « dès que possible » | échéance ferme |
| **Tolérance aux erreurs** | une erreur se corrige dans le numéro suivant | une erreur peut entraîner une correction officielle, voire une sanction |
| **Preuves à garder** | utiles | **obligatoires** : calcul, version, validation, données sources |

Il existe, à l'échelle internationale, de grandes **familles de règles** que l'on rencontre dans ces rapports. Pour les banques, des règles sur le **capital** et la **liquidité** (la famille dite de Bâle) ; pour la mesure des **pertes de crédit attendues** et le classement des prêts par niveaux de risque, la norme comptable IFRS 9 ; pour les **contrats d'assurance**, la norme IFRS 17 ; pour le **capital des assureurs**, des régimes de type « Solvabilité ». Nous les citons **à titre d'exemples**. Aucun calcul de ce chapitre n'est un calcul réglementaire : les définitions, les seuils et les formats varient d'un pays à l'autre et changent avec le temps, et c'est à la **fonction conformité** de l'entreprise de vous les fournir. Votre rôle d'analyste est de **produire des chiffres qui résistent à une vérification**.

> 🧭 **En pratique : les deux familles se ressemblent plus qu'on ne croit.** Un bon rapport de gestion a la même discipline qu'un rapport réglementaire (définitions écrites, contrôles, journal) ; il est simplement moins contraint. Prendre l'habitude du second pour le premier est une bonne protection : les chiffres de gestion d'aujourd'hui deviennent souvent les chiffres du superviseur de demain.

### 4.3.2 Un indicateur, une définition, un calcul, un propriétaire

Deux personnes qui calculent « l'encours douteux » peuvent trouver deux nombres (retard à partir de 90 jours ou de 91 ? encours à la date du défaut ou capital restant dû à la date de l'état ? incluant les intérêts ?). Pour l'éviter, on tient un **dictionnaire des indicateurs**. Chaque ligne répond à cinq questions : *quelle définition* (écrite, sans ambiguïté), *quelle source*, *qui en est propriétaire*, *quel contrôle* la valide, *quelle date de référence*.

| Indicateur | Définition écrite | Source | Propriétaire | Contrôle |
|---|---|---|---|---|
| Primes acquises | prime annuelle × exposition de la période | système de gestion des contrats | direction technique | rapprochement avec la comptabilité |
| Fréquence | nombre de sinistres de l'année de survenance ÷ exposition | gestion des contrats et des sinistres | direction technique | exposition non nulle ; nombre cohérent avec le mois précédent |
| S/P ultime | coût ultime estimé ÷ primes acquises | triangle et dossiers | actuariat | écart entre méthodes expliqué |
| Ratio combiné | S/P ultime + frais ÷ primes acquises | comptabilité analytique | direction financière | recalculé par une autre personne |
| Encours sain | capital restant dû des prêts de moins de 90 jours de retard à la date de l'état | système de crédit | direction du crédit | somme des tranches = total |
| Créances douteuses | encours des prêts en défaut (90 jours ou plus) | système de crédit | direction des risques | rapprochement avec la comptabilité |
| Taux de couverture | provisions ÷ créances douteuses | comptabilité | direction des risques | provisions = somme par tranche |
| Concentration (HHI) | somme des carrés des parts d'encours par secteur | système de crédit | direction des risques | parts de somme égale à 1 |

> 💡 **Intuition.** Ce dictionnaire est l'équivalent, pour un état, de ce que le **dictionnaire de données** est pour une base (volume II, section 4.2) : sans lui, chaque lecteur fait sa propre lecture et deux chiffres divergent sans que personne ne sache lequel croire. C'est aussi la règle « un chiffre, un seul calcul » (volume III, section 6.3.6) appliquée à l'organisation.

Voici le « pack » de chiffres que le dictionnaire permet de produire, pour l'assureur (année de survenance 2024) et pour la banque (30 juin 2025). Les fonctions qui les calculent sont **écrites une seule fois** et appelées par tous les états.

```python
ka, kb = O.kpi_assureur(d, 2024), O.kpi_banque(d, "2025-06-01")
print("assureur :", {k: round(float(v), 3) for k, v in ka.items() if k in ("frequence", "sp", "combine")})
print("banque   :", {"douteux_M€": round(float(kb["douteux"]) / 1e6, 2), "taux": round(float(kb["taux_douteux"]), 3), "couverture": round(float(kb["couverture"]), 3)})
```
<!--sortie-->
```text
assureur : {'frequence': 0.07, 'sp': 0.724, 'combine': 1.004}
banque   : {'douteux_M€': 4.35, 'taux': 0.054, 'couverture': 0.674}
```

### 4.3.3 Le rapprochement avec la comptabilité

Le **rapprochement** (ou réconciliation, volume II, chapitre 3) est le contrôle le plus important : on compare un chiffre de gestion à **un autre chiffre censé représenter la même chose**, issu d'un autre système, en l'occurrence la comptabilité. Si les deux ne concordent pas, **l'un des deux est faux**, ou bien la différence est **expliquée** (une date de comptabilisation différente, par exemple).

Dans notre exemple, la comptabilité fictive de l'assureur donne les primes comptabilisées de chaque année (`ch04-compta-primes.csv`). On compare avec les primes acquises du système de gestion et l'on fixe une **tolérance** : un écart relatif de 0,1 % est accepté sans explication.

```python
compta = pd.read_csv(os.path.join(D, "ch04-compta-primes.csv"))
rap = O.rapprochement(d, compta, tolerance=0.001)
print(rap.assign(ecart_rel=(rap["ecart_rel"] * 100).round(2)).to_string())
```
<!--sortie-->
```text
          gestion      compta    ecart  ecart_rel      verdict
annee                                                         
2021    2470714.0   2470714.0      0.0       0.00     conforme
2022    5226472.0   5226472.0      0.0       0.00     conforme
2023    7178339.0   7178339.0      0.0       0.00     conforme
2024    8846669.0   8767049.0  79620.0       0.91  à expliquer
2025   10517276.0  10517276.0      0.0       0.00     conforme
```

Quatre années sont conformes à l'euro près. En **2024**, le système de gestion donne 8 846 669 € et la comptabilité 8 767 049 €, soit un **écart de 79 620 €** (0,91 %), neuf fois la tolérance : il faut **l'expliquer** avant de publier. Le fichier des régularisations comptables contient six lignes, toutes datées de janvier 2025 (des régularisations de prime, des avenants tardifs, une annulation tardive) : elles ont été enregistrées par la gestion sur l'exercice 2024 mais par la comptabilité sur 2025.

```python
reg = pd.read_csv(os.path.join(D, "ch04-regularisations.csv"))
print(reg["montant"].sum(), "=", rap.loc[2024, "ecart"], "->", "écart entièrement expliqué" if reg["montant"].sum() == rap.loc[2024, "ecart"] else "écart résiduel")
```
<!--sortie-->
```text
79620.0 = 79620.0 -> écart entièrement expliqué
```

Les six régularisations expliquent **la totalité** de l'écart. Un rapport honnête le dit en une ligne (« écart de 79 620 € entre gestion et comptabilité, expliqué par six régularisations comptabilisées en janvier 2025 ») et conserve la liste. Un écart **inexpliqué**, même petit, doit bloquer la publication : on l'étudie d'abord.

Le rapprochement n'attrape pas que des différences de calendrier : il attrape aussi **vos propres erreurs de calcul**. L'une des plus fréquentes est la **multiplication des lignes** après une jointure. Si l'on joint les primes (une ligne par police et par année) aux sinistres (une ligne par sinistre) pour calculer un ratio, une police qui a eu deux sinistres voit sa prime **comptée deux fois**.

```python
x = d["ex"].merge(d["sin"][["id_police", "an"]], left_on=["id_police", "annee"], right_on=["id_police", "an"], how="left")
print("lignes avant :", len(d["ex"]), "| après :", len(x), "| primes avant :", round(d["ex"]["prime_acquise"].sum() / 1e6, 2), "M€ | après :", round(x["prime_acquise"].sum() / 1e6, 2), "M€")
```
<!--sortie-->
```text
lignes avant : 84875 | après : 85216 | primes avant : 34.24 M€ | après : 34.56 M€
```

Le nombre de lignes passe de 84 875 à 85 216 et le total des primes de 34,24 à 34,56 M€ (+0,9 %, neuf fois la tolérance). Aucun message d'erreur n'est affiché, aucun graphique n'est suspect ; seul le **rapprochement avec la comptabilité** (ou un simple contrôle « nombre de lignes avant = nombre de lignes après ») révèle le problème. La bonne façon de faire est de **résumer d'abord** les sinistres au niveau « police-année » (une ligne par police et par année), puis de joindre.

> ⚠️ **Piège : une jointure silencieuse.** Une jointure entre une table de clés uniques et une table où la clé se répète **multiplie** les lignes de la première. Les chiffres ont l'air plausibles (un peu trop grands). Les contrôles à toujours faire : **comparer les effectifs et les totaux avant et après** chaque jointure, et **rapprocher** le total final d'une source indépendante.

### 4.3.4 Validation à quatre yeux, versions et journal

Même avec des contrôles automatiques, une seconde personne relit. La règle des **quatre yeux** : celui qui produit un état n'est pas celui qui le valide. Le validateur ne refait pas tout ; il vérifie quatre choses : les **définitions** (ce sont bien celles du dictionnaire), les **contrôles** (ils ont tourné et sont conformes), les **variations** (celles qui dépassent un seuil sont commentées) et la **cohérence avec le rapport précédent**. Sa validation est **enregistrée**, avec la date.


![La chaîne d'un état fiable : extraction et contrôles d'entrée, calculs versionnés, rapprochement et revue à quatre yeux, publication ; le journal des exécutions garde la trace de chaque étape.](figures/ch04-flux-reporting.png)

Le **journal des exécutions** garde de quoi **refaire et prouver** un chiffre : la **version du code** qui l'a calculé, la **date de coupure des données** (« situation au 31 décembre 2025 »), le **résultat de chaque contrôle**, le **nom du validateur**. Un contrôle simple : refaire le calcul à partir des mêmes données et du même code doit donner **exactement les mêmes chiffres**. On peut le prouver avec une **empreinte** (un hachage) de l'ensemble des chiffres publiés.

```python
import hashlib, json
pack = {"assureur": {k: round(float(v), 4) for k, v in ka.items()}, "banque": {k: round(float(v), 4) for k, v in kb.items()}}
print(hashlib.sha256(json.dumps(pack, sort_keys=True).encode()).hexdigest()[:16])
```
<!--sortie-->
```text
158906c3a69519fe
```

Cette empreinte (seize caractères d'un résumé cryptographique) change **dès qu'un seul chiffre change**. Elle ne dit pas que le chiffre est juste ; elle dit qu'**on retrouve exactement le même**. Quand l'état du mois suivant est calculé, on garde l'empreinte de l'état précédent : en cas de contestation, on refait le calcul et l'on compare.

### 4.3.5 Calendrier, corrections et tolérance

Trois règles pratiques complètent le dispositif.

- **Une date de coupure par état.** Tout chiffre est « à la date du… ». Les données qui arrivent après la coupure vont dans l'état suivant : on **ne les glisse pas en silence** dans un état déjà validé.
- **Une version par état.** Quand une erreur est découverte après publication, on **publie une version corrigée** (« v2 ») avec la liste de ce qui a changé et pourquoi, plutôt que de modifier le fichier existant. Les lecteurs doivent pouvoir savoir **quel chiffre a été vu quand**.
- **Une tolérance fixée à l'avance.** Dire « 0,1 % d'écart de rapprochement sans explication » avant de calculer évite de rationaliser a posteriori. La tolérance dépend de l'enjeu : à la banque, une tolérance sur un état réglementaire sera beaucoup plus serrée que sur un tableau de bord d'équipe.

> ✅ **À retenir.** (1) Le **reporting de gestion** est choisi par l'entreprise, le **reporting réglementaire** est imposé : la discipline est la même, la tolérance à l'erreur non ; (2) chaque indicateur a une **définition écrite, une source, un propriétaire, un contrôle** (le dictionnaire) ; (3) on **rapproche** les chiffres de gestion de la comptabilité, avec une tolérance fixée d'avance, et un écart inexpliqué bloque la publication ; (4) on fait valider par une **seconde personne**, on garde un **journal** (version, date de coupure, contrôles, validateur) et une **empreinte** pour prouver qu'on retrouve les mêmes chiffres ; (5) les erreurs les plus fréquentes sont des **jointures silencieuses** : on compare les effectifs et les totaux avant et après.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.5 (rapprochement et jointure), exercices 4.7 et 4.8.


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


### 4.4.5 Le ratio combiné par segment, avec prudence

Le ratio combiné d'un segment se calcule comme celui de l'ensemble (S/P + frais). Mais **les frais ne sont pas répartis également** : un contrat vendu par un courtier ne coûte pas autant à acquérir qu'un contrat en agence, et un jeune conducteur demande plus de gestion de sinistres. Notre jeu de données suppose un taux de frais **uniforme** de 28 %, ce qui est une simplification : un ratio combiné par segment n'est donc qu'un **ordre de grandeur**. Les trois précautions de la section 4.1.6 s'appliquent : effectifs, intervalles, gros sinistres.

> ✅ **À retenir.** (1) Le S/P d'un segment se décompose en **fréquence × coût moyen ÷ prime moyenne** ; (2) un **GLM de Poisson avec offset d'exposition** donne des rapports de fréquence **toutes choses égales par ailleurs** ; le GLM de Gamma fait de même pour le coût, mais ce dernier est bien plus difficile à estimer ; (3) un intervalle qui contient 1 signifie « on ne sait pas », pas « pas d'effet » ; (4) comparer la prime pure à la prime facturée dit **quels segments sont sous-tarifés**, mais ne dit rien de la **réaction du marché** ; (5) un ratio combiné par segment dépend d'une **répartition des frais** qui est elle-même une hypothèse.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.6 (un GLM de fréquence et la lecture d'un tarif), exercices 4.9 et 4.10.


## 4.5 ➕ Pour aller plus loin : indicateurs d'alerte précoce

> 🧭 Section optionnelle.

La directrice des risques avait posé une deuxième question : « *où se cache le prochain problème, avant qu'il n'apparaisse dans les comptes ?* ». La matrice de transition de la section 4.2 répond en partie (un prêt qui passe à 30 jours de retard est un signal fort), mais **trente jours de retard, c'est déjà tard**. Un **indicateur d'alerte précoce** (en anglais *early warning indicator*) cherche des signaux **plus en amont** : des comportements qui précèdent les retards. L'enjeu est de les construire **sans tricher avec le futur** et de les évaluer honnêtement.

### 4.5.1 Signaux retardés et signaux avancés

On distingue deux familles.

- Les **indicateurs retardés** décrivent un événement **déjà arrivé** : les jours de retard, le défaut lui-même. Utiles pour mesurer, ils préviennent trop tard.
- Les **indicateurs avancés** décrivent un comportement qui **précède** l'événement : des incidents de paiement (un prélèvement rejeté, une échéance payée en deux fois), une utilisation croissante du découvert, une baisse des entrées d'argent sur le compte.

Notre suivi mensuel contient trois signaux : `jours_retard` (retardé), `incidents_3m` (nombre d'incidents de paiement sur les trois derniers mois) et `utilisation_decouvert` (part du découvert autorisé utilisée, entre 0 et 1), ces deux derniers étant avancés. Un quatrième élément est connu à l'octroi : le **score d'origine**.

### 4.5.2 Regarder les mois qui précèdent le défaut

Avant de construire un modèle, on **regarde**. Pour les prêts qui font défaut, on se place *x* mois avant le défaut (*x* = 0 est le mois du défaut) et l'on calcule la valeur moyenne de chaque signal ; on compare avec les prêts qui ne font jamais défaut. On utilise ici la date du défaut, **connue après coup**, uniquement pour **décrire** : on ne s'en servira pas pour prédire.

```python
sg = O.signaux_avant_defaut(d)
print(sg.round(2).to_string())
```
<!--sortie-->
```text
        jours_retard  incidents_3m  utilisation_decouvert
avant                                                    
0.0            99.52          0.10                   0.13
1.0            51.69          1.38                   0.46
2.0            30.39          1.25                   0.44
3.0            12.49          1.17                   0.42
4.0             9.04          0.93                   0.40
5.0             0.00          0.87                   0.37
6.0             0.56          0.67                   0.34
7.0             0.76          0.10                   0.13
8.0             0.78          0.10                   0.13
jamais          0.71          0.10                   0.13
```

Les prêts qui ne font jamais défaut ont, en moyenne, 0,71 jour de retard, 0,10 incident et 13 % de découvert utilisé. Six mois avant le défaut, les **jours de retard** n'ont pas bougé (0,6), mais les **incidents** sont déjà 6,7 fois plus nombreux (0,67) et le **découvert** utilisé est à 34 % : les signaux avancés se détachent **dès le sixième mois**. À 4 mois, un retard d'environ 9 jours apparaît ; à 2 mois, 30 jours ; à 1 mois, 52 jours. Le retard est donc un **signal tardif**, alors que les incidents et le découvert donnent **plusieurs mois d'avance**.

### 4.5.3 Construire l'alerte sans tricher

Il s'agit de **prédire** ; trois règles évitent les erreurs classiques.

1. **Une ligne par prêt et par mois, avec uniquement ce que l'on sait ce mois-là.** Pour un prêt au mois *t*, les variables sont calculées à partir des lignes **jusqu'à *t* inclus** (les retards de *t*, le découvert moyen sur trois mois, la variation de découvert sur trois mois, les incidents sur trois mois). Utiliser le futur (même par inadvertance, par exemple une moyenne de découvert calculée sur tout l'historique du prêt, défaut compris) donnerait un modèle magnifique en test et inutilisable en vie réelle.
2. **Une cible claire.** Nous fixons un **horizon de six mois** : la cible vaut 1 si le prêt fait défaut dans les six mois qui suivent (et n'est pas déjà en défaut), 0 sinon. On ne garde que les mois dont l'horizon est **entièrement observé** (jusqu'en juin 2025), sinon un défaut survenu en décembre 2025 serait compté comme absent pour un prêt observé en octobre.
3. **Une séparation dans le temps.** On apprend sur **2023** et l'on teste sur **2024 et le premier semestre 2025**, comme on le ferait vraiment : le modèle n'a pas vu la période sur laquelle on le juge.

Le modèle est une **régression logistique** simple (volume III, chapitre 3), sur des variables centrées et réduites.

```python
m, tr, te, coef = O.modele_alerte(d)
print(len(tr), "lignes d'apprentissage (2023) |", len(te), "lignes de test (2024 à juin 2025)")
print("part de cas positifs :", O.pct(tr["y"].mean(), 1), "|", O.pct(te["y"].mean(), 1))
print(coef.round(2).to_dict())
```
<!--sortie-->
```text
44787 lignes d'apprentissage (2023) | 122609 lignes de test (2024 à juin 2025)
part de cas positifs : 2,6 % | 2,4 %
{'jours_retard': 0.36, 'incidents_3m': 0.6, 'dec_moy3': 0.99, 'dec_delta': 0.26, 'score_origine': -0.72}
```

Dans la table d'apprentissage, **2,6 %** des lignes sont des cas positifs : la classe est **rare**. Les coefficients (les variables étant réduites) montrent que l'utilisation du découvert est le signal le plus fort (0,99), devant les incidents (0,60), alors que le score d'origine joue dans le sens attendu (−0,72 : un meilleur score à l'octroi, moins de risque) et que les jours de retard comptent moins (0,36), une fois les autres signaux pris en compte.

> 💡 **Une ligne n'est pas un prêt.** Un prêt qui fera défaut dans cinq mois apparaît comme un cas positif à chacun des cinq mois qui précèdent. Les « 2,4 % de cas positifs » comptent des **prêt-mois**, pas des prêts. Il faut y penser quand on parle de nombre d'alertes.

### 4.5.4 Évaluer au regard de la charge du comité

Un comité de crédit ne peut pas examiner tous les prêts : il examine, par exemple, **les cent dossiers les mieux notés chaque mois**. On évalue donc l'alerte **sous cette contrainte**.

- La **précision** est la part des dossiers examinés qui font vraiment défaut dans les six mois (combien de temps le comité perd-il ?).
- Le **rappel** est la part de **tous les défauts à venir** qui figurent parmi les dossiers examinés (combien de défauts rate-t-il ?).

On calcule les deux chaque mois pour un nombre *k* de dossiers, et l'on prend la moyenne. On refait le calcul **en ne gardant que les prêts qui n'ont pas encore 30 jours de retard** : ce sont ceux que le comité ne verrait pas autrement, puisque les prêts déjà en retard sont déjà suivis.

```python
ev = O.evaluer_topk(te)
ev2 = O.evaluer_topk(te[te["jours_retard"] < 30])
print((pd.concat([ev, ev2], axis=1, keys=["tous les prêts", "pas encore à 30 jours"]) * 100).round(0).to_string())
```
<!--sortie-->
```text
    tous les prêts        pas encore à 30 jours       
         precision rappel             precision rappel
k                                                     
25           100.0   16.0                  99.0   21.0
50           100.0   31.0                  90.0   37.0
100           88.0   54.0                  58.0   48.0
200           52.0   64.0                  33.0   54.0
400           28.0   69.0                  18.0   59.0
```

```python
regle = te[te["jours_retard"] >= 30]
print("prêts signalés par mois :", round(len(regle) / te["mois"].nunique(), 1))
print("précision :", O.pct(regle["y"].mean(), 1), "| rappel :", O.pct(regle["y"].sum() / te["y"].sum(), 1))
```
<!--sortie-->
```text
prêts signalés par mois : 67.5
précision : 60,8 % | rappel : 24,8 %
```


![À gauche, précision et rappel de l'alerte selon le nombre de prêts examinés chaque mois, comparés à la règle « déjà 30 jours de retard ». À droite, nombre de mois entre la première alerte et le défaut.](figures/ch04-alertes.png)

Avec un comité qui examine **100 dossiers par mois**, 88 % des dossiers examinés font défaut dans les six mois (la précision) et l'on attrape 54 % des défauts à venir (le rappel). La **règle de référence**, « examiner tout prêt qui a déjà 30 jours de retard ou plus », sélectionne en moyenne 68 prêts par mois, avec une précision de 61 % et un rappel de 25 % : **l'alerte attrape plus de deux fois plus de défauts avec une charge comparable**. Si l'on retire les prêts déjà en retard, la tâche est plus difficile : la précision à 100 dossiers tombe à 58 % et le rappel à 48 %, mais elle reste **utile**, car ces prêts sont ceux que personne ne regarde encore.

Deux enseignements de la figure. D'abord, **précision et rappel s'opposent** : plus on examine de dossiers, plus on attrape de défauts (le rappel monte de 16 % à 69 % entre 25 et 400 dossiers) mais plus la proportion de vrais cas baisse (de 100 % à 28 %). Le **choix de k est une décision de gestion**, pas de statistique : il dépend du temps du comité et du coût d'une alerte inutile (un client contacté à tort, une relation abîmée). Ensuite, le rappel plafonne à **69 %**, pas à 100 %.

### 4.5.5 Le délai d'anticipation et les défauts brutaux

Pour les prêts qui font défaut et qui ont été signalés par l'alerte (top 100 d'un mois), on mesure le **nombre de mois entre la première alerte et le défaut**. La médiane est de **4 mois** : un comité averti dispose en général de quatre mois pour agir (rencontrer l'emprunteur, renégocier l'échéancier, demander une garantie), ce qui est précieux.

Pourquoi le rappel plafonne-t-il à 69 % ? Parce que **29 % des défauts sont brutaux** : le prêt passe de « à jour » à « défaut » sans signal préalable (fraude, décès, faillite soudaine d'un client). Nous le savons parce que le simulateur le programme ; dans la vie réelle, la part de défauts brutaux se **découvre** après coup, en examinant ce que les prêts défaillants montraient auparavant. Aucune alerte basée sur les comportements ne peut les anticiper : **un plafond de rappel est une propriété du problème**, pas du modèle.


> ⚠️ **Piège : promettre mieux que le plafond.** Si l'on présente à la direction un rappel de 95 %, il faut se demander si l'on n'a pas utilisé l'information du futur. Un résultat **trop beau** est un résultat à vérifier avant d'être célébré.

### 4.5.6 De l'alerte à l'action

Une alerte n'est utile que si elle déclenche quelque chose. Trois pratiques font la différence.

- **Une action prévue pour chaque niveau d'alerte** : un appel du conseiller, une proposition de rééchelonnement, une revue du dossier. Sans action, le modèle ne sert à rien.
- **Un retour d'expérience.** On enregistre ce qui s'est passé pour chaque dossier examiné (dossier régularisé, défaut évité, défaut malgré l'action). C'est ce retour qui permet de **recalibrer le seuil** et de mesurer l'efficacité des actions.
- **Une surveillance du modèle.** Le modèle a été appris en 2023. La précision au top-100 se calcule **chaque trimestre** : elle vaut 80 % au premier trimestre 2024 et 94 à 98 % début 2025. Elle monte, ce qui n'est pas un signe de vieillissement, mais elle dépend du **nombre de cas positifs** et de la **taille du portefeuille** (qui grossit entre 2024 et 2025). Un modèle d'alerte se surveille donc comme un indicateur : on **compare chaque trimestre** la précision, le rappel et le nombre d'alertes, et l'on réapprend quand ils dérivent.

```python
print({str(k): int(round(v * 100)) for k, v in O.precision_par_trimestre(te).items()})
```
<!--sortie-->
```text
{'2024Q1': 80, '2024Q2': 81, '2024Q3': 84, '2024Q4': 93, '2025Q1': 98, '2025Q2': 94}
```

> ✅ **À retenir.** (1) Les **indicateurs avancés** (incidents, découvert) donnent plusieurs mois d'avance, les jours de retard arrivent trop tard ; (2) on construit l'alerte **sans le futur**, avec un **horizon**, une **séparation dans le temps** et des mois dont l'horizon est entièrement observé ; (3) on évalue la précision et le rappel **au regard de la charge** du comité (top-*k*) et par rapport à une **règle simple** ; (4) le **délai d'anticipation** (4 mois en médiane) fait la valeur de l'alerte ; (5) les **défauts brutaux** plafonnent le rappel : c'est une limite du problème ; (6) l'alerte doit déclencher une action, et le modèle se **surveille** trimestre après trimestre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.7 (seuil d'alerte selon la charge du comité), exercice 4.11.


## 4.6 ➕ Pour aller plus loin : reporting réglementaire et de gestion pour banques et assureurs

> 🧭 Section optionnelle.

La section 4.3 a posé les principes. Celle-ci les met en pratique sur deux **états** fabriqués de bout en bout : un état de gestion de l'assureur et un état de gestion de la banque, avec leurs **contrôles de cohérence** et la manière de **justifier un écart**. Ce sont des **maquettes génériques** : aucun format officiel d'aucune autorité n'est reproduit, les numéros de cases (A01, B03…) sont inventés, et les seuils (5 points de variation, 0,1 % de tolérance) sont des choix d'exemple.

### 4.6.1 Un état est un tableau de cases numérotées

Un état de reporting n'a pas la liberté d'un graphique. Chaque **case** a un **numéro stable**, un **libellé**, une **définition écrite** (celle du dictionnaire, section 4.3.2) et un **contrôle**. Un état bien fait se lit de haut en bas comme un petit calcul : les cases de départ sont des **montants issus des systèmes**, les suivantes sont des **cases calculées** à partir des premières, et la dernière donne les **ratios**. Le lecteur (ou le superviseur) peut ainsi **refaire l'arithmétique**.


![Maquette générique d'un état de gestion de l'assureur pour l'année 2024 : chaque case a un numéro, un libellé et une valeur ; les cases A04 à A06 sont calculées à partir des cases A01 à A03.](figures/ch04-maquette-etat.png)

Le numéro stable est essentiel : quand on **modifie** un état d'une période à l'autre (une case ajoutée, une définition précisée), la numérotation permet de comparer **la case A05 de cette année à la case A05 de l'an passé**, et de tenir un **historique des changements**.

### 4.6.2 Deux états de gestion

Voici l'état de l'assureur pour l'année de survenance 2024 et celui de la banque au 30 juin 2025. Toutes les valeurs viennent des fonctions écrites **une fois** pour le dictionnaire (section 4.3.2).

```python
ea, eb = O.etat_assureur(d, 2024), O.etat_banque(d, "2025-06-01")
print(O.afficher_etat(ea).to_string())
print(O.afficher_etat(eb).to_string())
```
<!--sortie-->
```text
                               libelle    valeur
case                                            
A01                    Primes acquises  8 847 k€
A02   Coût ultime estimé des sinistres  6 409 k€
A03                              Frais  2 477 k€
A04                 Résultat technique    −40 k€
A05                          Ratio S/P    72,4 %
A06                      Ratio combiné   100,4 %
                            libelle     valeur
case                                          
B01                    Encours sain  76 171 k€
B02              Créances douteuses   4 347 k€
B03      Taux de créances douteuses      5,4 %
B04       Provisions (taux fictifs)   2 928 k€
B05              Taux de couverture     67,4 %
B06   Indice de concentration (HHI)      0,298
B07           Nombre de prêts sains      8 315
```

L'assureur affiche **8 847 k€** de primes acquises, **6 409 k€** de sinistres estimés et **2 477 k€** de frais, soit un résultat technique de **−40 k€** : un ratio combiné de **100,4 %**, tout juste au-dessus de l'équilibre. La banque affiche **76,2 M€** d'encours sain, **4,3 M€** de créances douteuses (**5,4 %**), un taux de couverture de **67 %** (avec nos taux de provisionnement fictifs) et un indice de concentration de **0,30**. Chaque case se retrouve dans les sections 4.1, 4.2 et 4.3.

### 4.6.3 Les contrôles de cohérence

On distingue quatre familles de contrôles, de la plus simple à la plus exigeante.

1. **Contrôles arithmétiques internes** : les cases calculées sont bien égales à ce que leur définition donne. Ces contrôles sont presque triviaux, mais ils attrapent les erreurs de mise en page (une formule cassée dans un tableur, un arrondi mal placé).
2. **Contrôles de complétude** : toutes les polices ou tous les prêts du système source sont bien représentés (aucun prêt sans fiche, aucun sinistre sans contrat).
3. **Contrôles entre sources** (les rapprochements de la section 4.3.3) : le chiffre de gestion et le chiffre comptable concordent, ou l'écart est expliqué.
4. **Contrôles de variation** : une case qui varie de plus d'un seuil par rapport à la période précédente doit être **commentée**.

```python
print(O.controles_etats(ea, eb).to_string())
```
<!--sortie-->
```text
A04 = A01 - A02 - A03      True
A05 = A02 / A01            True
A06 = A05 + frais / A01    True
B03 = B02 / (B01 + B02)    True
B05 = B04 / B02            True
0 < HHI <= 1               True
```

Les six contrôles arithmétiques passent. **Un contrôle qui ne peut jamais échouer ne sert à rien** : pour s'assurer que les nôtres fonctionnent, on **injecte une erreur** et l'on vérifie qu'ils la détectent. Ici, on augmente les frais de 10 % sans mettre à jour les cases calculées.

```python
ea_faux = ea.copy()
ea_faux.loc["A03", "valeur"] *= 1.10
print(O.controles_etats(ea_faux, eb).loc[lambda s: ~s].to_string())
```
<!--sortie-->
```text
A04 = A01 - A02 - A03      False
A06 = A05 + frais / A01    False
```

Deux contrôles passent au rouge : A04 (le résultat technique ne vaut plus A01 − A02 − A03) et A06 (le ratio combiné ne vaut plus A05 plus les frais divisés par les primes). Le contrôle de l'état fonctionne.

```python
prec, cour = O.kpi_assureur(d, 2023), O.kpi_assureur(d, 2024)
var = (cour["sp"] - prec["sp"]) * 100
print(round(var, 1), "points de S/P :", "commentaire requis" if abs(var) > 5 else "variation ordinaire")
print("complétude :", bool(d["suivi"]["id_pret"].isin(d["prets"]["id_pret"]).all()), bool(d["sin"]["id_police"].isin(d["pol"]["id_police"]).all()))
```
<!--sortie-->
```text
7.2 points de S/P : commentaire requis
complétude : True True
```


Le S/P ultime passe de 65,3 % (2023) à 72,4 % (2024), soit **+7,2 points** : au-dessus du seuil de 5 points, **un commentaire est exigé**. Les contrôles de complétude passent : chaque prêt du suivi a sa fiche, chaque sinistre a son contrat.

> 🧭 **En pratique : où mettre les contrôles.** On les écrit **dans le code qui produit l'état**, pas dans un tableur à côté. Chaque exécution **échoue** (ou au minimum **prévient**) si un contrôle bloquant échoue, et le résultat de tous les contrôles va dans le journal (section 4.3.4). C'est la même démarche que les tests automatiques d'un programme.

### 4.6.4 Justifier un écart ou une variation

Un contrôle de variation ou de rapprochement qui échoue appelle une **justification écrite**. Elle suit toujours le même plan en quatre éléments : **le fait** (ce qui a varié, de combien), **la cause établie** (ce qu'on a vérifié), **la cause probable** (ce qu'on suppose, dite comme telle), **la suite** (ce qui est décidé). Pour la variation de S/P ci-dessus :

> **A05, ratio S/P 2024 : +7,2 points (65,3 % → 72,4 %).** *Fait* : le coût moyen d'un sinistre estimé passe de 4 305 € à 4 976 € (+15,6 %) pendant que la fréquence reste stable (7,2 % → 7,0 %) et que la prime moyenne n'augmente que de 2 %. *Cause établie* : la hausse vient du coût moyen, pas de la fréquence (le tableau annuel de la section 4.1.1 le montre). *Cause probable* : une inflation des coûts supérieure à la revalorisation du tarif ; à confirmer avec la direction des sinistres, car nous n'avons pas décomposé l'écart par nature de sinistre. *Suite* : décomposition par nature et par segment, puis revue du tarif au prochain comité.

La phrase **ne prétend pas connaître la cause** quand elle ne la connaît pas : elle sépare ce qui est vérifié de ce qui est supposé (c'est la règle de la section 4.2.6 : une dérive se **signale**, ses causes se **proposent**). Le seuil de matérialité (« à partir de quel écart justifie-t-on ? ») est fixé à l'avance.

### 4.6.5 Ce que le reporting réglementaire ajoute

Un état destiné à un superviseur reprend tout ce qui précède et y **ajoute des contraintes** que nous ne simulons pas.

- **Un modèle imposé** : cases, définitions et regroupements fixés par le texte applicable ; l'analyste **ne choisit plus** ses définitions, il les **applique** et documente son interprétation quand le texte laisse un doute.
- **Une échéance ferme et un calendrier** : l'état doit partir à une date donnée, ce qui oblige à planifier la production, les contrôles et la validation à rebours.
- **Une piste d'audit** : on doit pouvoir **refaire le calcul** plusieurs années après (données, code, paramètres conservés), et montrer qui a validé quoi.
- **Une attestation** : un responsable signe l'état et en assume l'exactitude, d'où l'insistance sur les contrôles et la validation à quatre yeux.
- **Une procédure de correction** : une erreur découverte après envoi se corrige selon une procédure fixée, avec les justifications.

> ⚠️ **Rappel d'honnêteté.** Ce chapitre ne vous prépare pas à remplir un état réglementaire réel : les textes applicables (leurs définitions, leurs seuils, leurs formats) dépendent de votre pays, de votre activité et de leur version en vigueur ; ils ne figurent pas ici, et il faudra les obtenir auprès de la fonction conformité. Ce que vous emportez est la **discipline** : définitions écrites, contrôles qui échouent vraiment, rapprochement, validation, journal.

> ✅ **À retenir.** (1) Un état est un tableau de **cases numérotées** qui se lisent comme un petit calcul ; (2) quatre familles de contrôles : **arithmétiques**, **complétude**, **entre sources**, **variation** ; (3) on **teste ses contrôles** en injectant une erreur ; (4) on **justifie** un écart en séparant le fait, la cause établie, la cause probable et la suite ; (5) le reporting réglementaire ajoute **modèle imposé, échéance, piste d'audit, attestation, procédure de correction**, que nous ne simulons pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : exercice 4.12 (écrire des contrôles et justifier un écart).


## Bilan du chapitre 4


Vous savez maintenant :

- **mesurer un portefeuille d'assurance** : exposition en années-police, fréquence, coût moyen, prime pure, **ratio sinistres/primes** et **ratio combiné** (S/P + frais), et **savoir pourquoi la dernière année est incomplète** (déclarations et paiements tardifs) ;
- **construire un triangle de développement**, calculer des **facteurs** et un **ultime** par la méthode **chain ladder**, et **juger l'estimation avec la vérité** (de +5,1 % pour 2022 à −6,9 % pour 2025), en sachant qu'un facteur de queue fondé sur une seule année est fragile ;
- **se méfier des gros sinistres** : 1 % des sinistres pèse 28,6 % du coût, et un S/P de segment sans intervalle peut désigner à tort « la pire zone » (85 % brut, 65 % plafonné) ;
- **lire le mix et la rentabilité par segment** (les moins de 25 ans : fréquence ×4,4, S/P de 102 %, ratio combiné de 130 %) et **suivre un portefeuille de crédit** par tranches de retard, créances douteuses, taux de couverture, en regardant **le dénominateur** ;
- **comparer des cohortes d'octroi à âge égal** (le millésime 2024 S1 à 11,4 % de défaut à 18 mois contre 7,6 à 8,3 %), **construire une matrice de transition** et en tirer des probabilités de défaut à horizon, **mesurer la concentration** (HHI) et **repérer une dérive sectorielle** (Commerce et Restauration, de 5,5 à 8,5 défauts par an pour 100 prêts) ;
- **produire un état fiable** : un indicateur, une définition, un propriétaire ; un **rapprochement** avec la comptabilité (écart de 79 620 € expliqué par six régularisations) ; des contrôles **testés par injection d'erreur** ; une validation à quatre yeux, un journal et une empreinte ;
- ➕ **expliquer** la fréquence par un **GLM de Poisson avec exposition** (2,84 fois plus de sinistres pour les moins de 25 ans, à caractéristiques égales), reconnaître qu'on n'explique **pas** la sévérité avec ces données, et **chiffrer un tarif insuffisant** (+42 % pour les moins de 25 ans) ;
- ➕ **construire une alerte précoce sans le futur** (apprentissage 2023, test 2024-2025), l'évaluer **au regard de la charge du comité** (88 % de précision et 54 % de rappel pour cent dossiers par mois, contre 61 % et 25 % pour la règle « 30 jours de retard »), mesurer son **délai d'anticipation** (4 mois) et son **plafond** (29 % de défauts brutaux) ;
- ➕ **justifier un écart** en séparant le fait, la cause établie, la cause probable et la suite.

Le tableau suivant résume ce que nous avons mesuré dans ce chapitre.

| Question | Résultat |
|---|---|
| S/P déclaré de 2021 et de 2025 | 60 % puis 82 % (ratio combiné de 2025 supérieur à 100 %, même complété : S/P de 77 à 83 %) |
| Facteurs de développement des paiements | 2,22 ; 1,20 ; 1,10 ; 1,07 (32 % du coût final est payé la première année) |
| Écart du chain ladder à la vérité | +5,1 % (2022), +0,2 % (2023), −1,7 % (2024), −6,9 % (2025) |
| Part des 1 % de sinistres les plus coûteux | 28,6 % du coût total |
| S/P de la zone A, brut puis plafonné à 50 000 € | 85 % puis 65 % (intervalle brut de 70 à 102 %) |
| Moins de 25 ans : fréquence, S/P, ratio combiné | ×4,4 ; 102 % ; 130 % (hausse de tarif requise : 42 %) |
| GLM de Poisson : moins de 25 ans contre 40-59 ans | 2,84 (de 2,56 à 3,16) |
| Taux de créances douteuses | 3,9 % (déc. 2024), 5,4 % (juin 2025) |
| Défaut cumulé à 18 mois, millésime 2024 S1 contre les autres | 11,4 % contre 7,6 à 8,3 % |
| Probabilité de défaut dans les 6 mois, selon la tranche | 1,6 % (à jour), 4,5 % (1-29 jours), 41,6 % (30-59 jours) |
| Commerce et Restauration, défauts par an pour 100 prêts | 5,5 puis 8,5 (p = 0,03) |
| Alerte précoce, 100 dossiers par mois | précision 88 %, rappel 54 %, délai médian 4 mois, plafond 69 % |
| Rapprochement des primes 2024 | écart de 79 620 € (0,91 %), expliqué |

Le fil conducteur du chapitre tient en une phrase : **on ne connaît pas encore le coût de ce que l'on a déjà vendu, et le travail de l'analyste est de l'estimer honnêtement, de le surveiller, et de dire ce que l'on ne sait pas**. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **Comparer à période égale, à âge égal.** Ne jamais mettre côte à côte une année complète et une année incomplète, ni une cohorte de vingt-quatre mois et une de six.
> 2. **Donner un intervalle et un effectif.** Un ratio de segment, une provision, un taux de défaut sans intervalle sont des chiffres sans humilité.
> 3. **Contrôler, tester les contrôles, garder la trace.** Un état n'est pas fiable parce qu'il a l'air juste, mais parce qu'il se rapproche d'une autre source, que ses contrôles peuvent échouer et que l'on peut le refaire à l'identique.

> ⚠️ **Rappel d'honnêteté.** Tout est **simulé**, et les « vérités » (coûts finaux, mois de défaut, défauts brutaux, millésime relâché, choc sectoriel) ne sont connues que parce que nous avons écrit le simulateur. Plusieurs chiffres reposent sur des **hypothèses de simplification** que nous avons dites : un prêt en défaut reste « douteux » douze mois, les taux de provisionnement sont **fictifs**, les frais sont uniformes à 28 %, aucun prêt de 60 à 89 jours ne se redresse, et le portefeuille de crédit s'éteint après juin 2025. Aucun calcul de ce chapitre n'est un calcul réglementaire : les règles et formats officiels ne sont pas reproduits.

Le chapitre 5, complémentaire, traite d'un outil que beaucoup d'analystes ont déjà essayé : les **grands modèles de langage** (LLM). On y verra ce qu'ils peuvent faire pour une analyse (écrire une requête SQL, rédiger un commentaire, fabriquer des données de test) et, surtout, **comment vérifier** ce qu'ils produisent, avec le même esprit de contrôle que dans ce chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.7 (fréquence et ratio combiné, triangle à la main, cohortes à âge égal, matrice de transition, rapprochement, GLM et tarif, seuil d'alerte) et exercices 4.1 à 4.12.
