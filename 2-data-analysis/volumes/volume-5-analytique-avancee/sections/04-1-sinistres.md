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

```python hide
v = d["ver"]
non_decl = v.loc[~v["declare_au_31_12_2025"], "cout_ultime"]
print(len(non_decl), round(non_decl.sum() / 1e3), round(non_decl.sum() / O.vrai_ultime(d).loc[2025] * 100, 1))
```
<!--sortie-->
```text
114 414 4.7
```

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

```python hide
O.fig_triangle(d)
```
<!--sortie-->
```text
figure : ch04-triangle.png
```

![Le triangle de développement des paiements (cumulés, en millions d'euros) : chaque ligne est une année de survenance, chaque colonne un délai. La partie basse droite correspond à des paiements futurs, qu'il reste à prévoir.](figures/ch04-triangle.png)

```python hide
rest = np.cumprod(f[::-1])[::-1]
print(np.round(1 / np.append(rest, 1.0), 3), round(float(rest[0]), 2))
assert round(float(rest[0]), 1) == 3.1 and round(1 / rest[0] * 100) == 32 and round(1 / rest[1] * 100) == 71 and round(1 / rest[2] * 100) == 85
ex_ = d["ex"].groupby("annee").size()
assert ex_[2021] == 8987 and ex_[2025] == 23177
```
<!--sortie-->
```text
[0.32  0.711 0.852 0.937 1.   ] 3.12
```

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

```python hide
O.fig_sp_annee_classe(d)
```
<!--sortie-->
```text
figure : ch04-sp-annee-classe.png
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

```python hide
cu = d["sin"]["cout_ultime"]
n1 = int(len(d["sin"]) * 0.01)
print(round(cu.median()), round(cu.max()), int((cu > 100000).sum()), n1, round(cu.nlargest(n1).sum() / cu.sum() * 100, 1))
assert round(cu.median()) == 1962 and round(cu.max()) == 474293 and (cu > 100000).sum() == 31 and n1 == 51
z = d["sin"][d["sin"]["an"] <= 2024].nlargest(1, "cout_ultime")
print(z[["zone", "cout_ultime"]].round(0).to_string(index=False))
```
<!--sortie-->
```text
1962 474293 31 51 28.6
zone  cout_ultime
   A     311328.0
```

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

```python hide
ic = O.ic_sp(d, "zone")
ic_plaf = O.ic_sp(d, "zone", ecreter=50000)
print((ic * 100).round(0).to_string())
print((ic_plaf * 100).round(0).to_string())
O.fig_zone_gros(d)
```
<!--sortie-->
```text
    bas   haut
A  70.0  102.0
B  50.0   68.0
C  54.0   73.0
D  56.0   80.0
    bas  haut
A  58.0  73.0
B  46.0  55.0
C  49.0  59.0
D  50.0  63.0
figure : ch04-zone-gros-sinistre.png
```

![Ratio sinistres/primes par zone (2021-2024), avant et après plafonnement de chaque sinistre à 50 000 €, avec l'intervalle à 90 % obtenu par bootstrap.](figures/ch04-zone-gros-sinistre.png)

Le S/P brut de la zone A est compris, à 90 %, entre 70 % et 102 % ; celui de la zone D, entre 56 % et 80 %. Les deux intervalles **se chevauchent** : avec les données brutes, on ne peut pas affirmer que la zone A est plus mauvaise que la zone D. Après plafonnement, l'intervalle de la zone A (de 58 à 73 %) reste au-dessus de celui de la zone B (de 46 à 55 %), mais chevauche encore ceux de C et D.

> 🧭 **En pratique : trois façons de traiter les gros sinistres.**
> 1. **Plafonner** chaque sinistre à un seuil (par exemple 50 000 €) pour comparer les segments sur la sinistralité « courante », puis **ajouter une charge pour les gros sinistres**, calculée sur l'ensemble du portefeuille (où ils sont assez nombreux pour être stables).
> 2. **Analyser séparément** les gros sinistres : combien, quelle nature, quelle évolution.
> 3. **Toujours accompagner un S/P de segment d'un intervalle** ou, au minimum, d'un effectif (nombre de sinistres et nombre de sinistres graves).

> ✅ **À retenir.** (1) On mesure un portefeuille d'assurance en **fréquence** (par année-police), **coût moyen**, **S/P** et **ratio combiné** ; (2) la **dernière année est incomplète** (déclarations et paiements tardifs) : on la complète ou on s'abstient ; (3) le **triangle de développement** et la méthode **chain ladder** estiment ce qu'il reste à payer, sous l'hypothèse d'un rythme stable, avec des facteurs de queue fragiles ; (4) **les gros sinistres** rendent trompeurs les S/P des petits segments : plafonner, analyser à part, donner un intervalle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.1 (fréquence, coût, S/P et combiné), application 4.2 (un triangle à la main), exercices 4.1 à 4.3.
