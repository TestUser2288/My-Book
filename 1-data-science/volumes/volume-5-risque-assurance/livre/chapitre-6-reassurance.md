# Chapitre 6 : ➕ Bases de la réassurance et de sa tarification

> « Réassurer, c'est acheter de la tranquillité. Son prix se calcule, et surtout il se discute. »

> 🧭 **Chapitre complémentaire.** Il peut être lu sans le reste du volume, mais il suppose les notions de sévérité à queue lourde (volume II, section 6.5), de VaR et d'*expected shortfall* (section 3.1) et de capital réglementaire (section 4.2). Le chapitre 7 en est indépendant.

Une mutuelle d'assurance a un métier simple à énoncer : mettre en commun des risques pour que chacun supporte une part prévisible d'un aléa que, seul, il ne pourrait pas porter. Mais la mutuelle est elle-même exposée à un aléa qu'elle ne peut pas diluer indéfiniment : **quelques sinistres très gros** (un incendie qui détruit un entrepôt, une tempête qui touche tout un territoire le même jour) peuvent à eux seuls faire basculer un exercice, voire menacer sa solvabilité. La **réassurance** est l'assurance de l'assureur : la mutuelle (la **cédante**) transfère à un **réassureur** une partie de ses risques, contre une prime.

Ce chapitre répond à trois questions, dans l'ordre où une cédante se les pose.

## Le chemin de ce chapitre

| Section | Question | Ce que vous saurez faire |
|---|---|---|
| **6.1 Principes et formes** | Comment un traité partage-t-il les sinistres entre cédante et réassureur ? | Distinguer **proportionnel** et **non proportionnel**, calculer à la main ce que cède chaque forme, lire une clause (priorité, portée, réintégration). |
| **6.2 Tarifer un traité** | Combien vaut une tranche de sinistres gros ? | Estimer une prime pure par le *burning cost*, par une loi de queue (GPD) et par l'exposition ; **chiffrer l'incertitude** ; passer de la prime pure à la prime technique. |
| **6.3 Choisir une couverture** | Que gagne-t-on à réassurer, et à quel prix ? | Simuler la charge annuelle, comparer des programmes par le **coût d'un euro de capital économisé**, regarder le risque de contrepartie et l'épuisement des garanties. |

Le fil conducteur est celui du volume : **chiffrer un risque, puis prouver que le chiffre tient**. Ici, la preuve est difficile, parce que le risque réassuré est précisément celui dont on a **le moins d'observations** : on parle de sinistres qui arrivent une fois en cinq ans, une fois en vingt ans. Vous verrez qu'une estimation correcte peut se tromper de 10 %, de 30 %, ou de beaucoup plus sur une tranche haute, **sans qu'aucun calcul n'ait été faux**.

## Les données du chapitre

> 📦 **Données.** Deux fichiers **simulés**, sans lien avec une entreprise réelle.
> - `sinistres_gros.csv` : 2 898 sinistres « incendie » de la mutuelle sur 15 ans (2010 à 2024), avec l'année de survenance et le montant en €. Le nombre de sinistres croît d'environ 3 % par an, parce que le portefeuille grandit.
> - `cat_annuel.csv` : la perte annuelle due à des **événements catastrophiques** sur 40 ans (1985 à 2024), en €, avec beaucoup d'années à zéro.
>
> Comme toujours, les données sont fabriquées par un programme : nous **connaissons la vérité** (la loi des sinistres, la loi des catastrophes, le taux de croissance), et nous la révélerons au fil des études pour juger les estimations. En pratique, elle n'est jamais connue.


Les sinistres se résument en quelques lignes :

```python
sg, cat = O.charger()
print(sg["montant"].describe().round(0))
```
<!--sortie-->
```text
count       2898.0
mean      115984.0
std       290925.0
min          189.0
25%        10088.0
50%        30118.0
75%        86846.0
max      4310320.0
Name: montant, dtype: float64
```

Le sinistre médian vaut 30 118 €, le sinistre moyen 115 984 € : **la moyenne vaut près de quatre fois la médiane**, signe d'une distribution très asymétrique. Les 177 sinistres de plus de 500 000 € (6,1 % des sinistres) pèsent 53 % du montant total ; le plus gros atteint 4 310 320 €. Les catastrophes sont encore plus rares : 17 années sur 40 ont connu un événement, et la pire a coûté 35 614 167 €. Ce sont ces queues que la réassurance vient couvrir, et ce sont elles qui rendent leur prix incertain.

> ⚠️ **Deux conventions de lecture.** Les tranches s'écrivent « **portée xs priorité** » : « 1 M€ xs 1 M€ » désigne la tranche qui paie la part d'un sinistre comprise **entre 1 M€ et 2 M€**. Et tous les montants « au niveau 2025 » désignent l'**exposition attendue de l'année 2025** (environ 249 sinistres par an, contre 160 en 2010).


## 6.1 Principes et formes de réassurance

Avant de tarifer un traité, il faut comprendre ce qu'il fait : qui paie quoi, quand, et dans quelle proportion. Cette section pose le vocabulaire, montre **pourquoi** une cédante réassure (c'est une affaire de variance et de capital, pas de moyenne), puis décrit les deux grandes familles de traités en calculant, **à la main**, ce que chacune cède sur huit sinistres.

### 6.1.1 Pourquoi réassurer ?

Une cédante ne réassure pas pour réduire son coût moyen : en moyenne, la réassurance **coûte** (le réassureur facture ses frais et une marge). Elle réassure pour trois raisons qui concernent la **dispersion** du résultat.

**Stabiliser le résultat.** Un exercice où un seul sinistre pèse un quart de la charge annuelle est un exercice imprévisible. Les dirigeants, les adhérents, le régulateur et les agences de notation préfèrent un résultat qui ne dépend pas d'un coup du sort.

**Gagner de la capacité.** Un assureur ne peut accepter un risque de 50 M€ que si une perte totale ne l'anéantit pas. En cédant la part qui dépasse ce qu'il peut porter, il accepte des risques plus gros, donc gagne des clients.

**Économiser du capital.** Le capital réglementaire (section 4.2) et le capital économique dépendent de la queue de la distribution des pertes. Transférer la queue au réassureur réduit le capital immobilisé. Nous mesurerons cela en 6.3.

Le vocabulaire se résume en quelques mots. La **cédante** est l'assureur direct qui cède ; le **réassureur** accepte la cession ; le **rétrocessionnaire** réassure le réassureur. Un **traité** couvre automatiquement tout un portefeuille selon des règles convenues ; une **facultative** couvre un risque isolé, négocié au cas par cas. Les montants **bruts** sont ceux de la cédante avant réassurance, les montants **nets** après. La **prime cédée** est ce que la cédante paie, les **récupérations** ce que le réassureur rembourse.

#### Un coup d'œil sur la variance

Pourquoi la réassurance agit-elle surtout sur les gros sinistres ? Parce que la variance de la charge annuelle vient d'eux. Notons $S=X_1+\dots+X_N$ la charge annuelle, où le nombre de sinistres $N$ suit une loi de Poisson de moyenne $\lambda$ et où les montants $X_i$ sont indépendants, de même loi, de moyenne $\mu$.

> 📐 **Variance de la charge annuelle.** Par la formule de l'espérance totale, $E[S]=\lambda\mu$. Par la formule de la variance totale,
> $$\operatorname{Var}(S)=E[\operatorname{Var}(S\mid N)]+\operatorname{Var}(E[S\mid N])=E[N]\operatorname{Var}(X)+\operatorname{Var}(N)\,\mu^2=\lambda\bigl(\operatorname{Var}(X)+\mu^2\bigr)=\lambda\,E[X^2],$$
> puisque $E[N]=\operatorname{Var}(N)=\lambda$ pour une loi de Poisson. Le **coefficient de variation** de la charge annuelle vaut donc
> $$\mathrm{CV}(S)=\frac{\sqrt{\lambda E[X^2]}}{\lambda\mu}=\sqrt{\frac{1+\mathrm{CV}(X)^2}{\lambda}}.$$

Deux enseignements. D'abord, avec $\lambda$ sinistres par an, le CV décroît comme $1/\sqrt\lambda$ : **quadrupler** le portefeuille ne fait que **diviser par deux** l'incertitude relative. Ensuite, le CV dépend du **CV d'un sinistre** : une queue lourde (un $E[X^2]$ gigantesque) annule les bénéfices de la mutualisation.

Appliquons-le à nos sinistres. Le CV d'un sinistre vaut 2,51 ; avec 249 sinistres attendus, le CV de la charge annuelle brute est de 17,1 %. Si la cédante **plafonne** chaque sinistre à 500 000 € (c'est ce que fait un excédent de sinistre « 500 xs 500 »), le CV d'un sinistre net tombe à 1,55, et celui de la charge annuelle à 11,7 %. Pour obtenir la même régularité **sans** réassurance, il faudrait un portefeuille **2,1 fois plus gros**.


> 💡 **Réassurer, c'est couper la queue.** La loi des grands nombres protège des petits sinistres (ils se compensent), pas des gros (ils dominent la variance). La réassurance est l'outil qui s'attaque exactement à ce que la mutualisation ne sait pas faire.

### 6.1.2 Les traités proportionnels

Dans un traité **proportionnel**, cédante et réassureur partagent **à la fois les primes et les sinistres, dans la même proportion**. Deux variantes existent.

**La quote-part.** La cédante cède un pourcentage fixe $\alpha$ de **chaque** risque : prime $\alpha P$, sinistre $\alpha X$. Le réassureur verse en outre à la cédante une **commission de cession** (un pourcentage de la prime cédée), qui couvre les frais d'acquisition et de gestion qu'elle a engagés. Le partage est simple et sans négociation sur les sinistres : le réassureur « suit la fortune » de la cédante.

**L'excédent de plénitude** (on dit aussi *surplus*). La cédante fixe une **plénitude** $R$, le montant maximal qu'elle garde sur un risque. Pour un risque de capital assuré (valeur exposée) $V_i$, elle cède la fraction
$$\tau_i=\max\Bigl(0,\;1-\frac{R}{V_i}\Bigr)$$
de ce risque, avec la même fraction de la prime et de chaque sinistre sur ce risque. Les petits risques ($V_i\le R$) restent entièrement chez la cédante ; les gros sont partagés. Le traité **homogénéise** ainsi le portefeuille net : aucun risque ne dépasse $R$ en valeur exposée.

#### Un exemple à la main

Huit sinistres de l'année (en k€), chacun survenu sur un risque dont le capital assuré est connu :

| Sinistre | Capital assuré | Quote-part 30 % : cédé | Taux de cession (plénitude 1 000) | Plénitude : cédé | 500 xs 500 : cédé |
|---|---:|---:|---:|---:|---:|
| 30 | 200 | 9 | 0 % | 0 | 0 |
| 45 | 300 | 13,5 | 0 % | 0 | 0 |
| 80 | 500 | 24 | 0 % | 0 | 0 |
| 120 | 800 | 36 | 0 % | 0 | 0 |
| 250 | 1 000 | 75 | 0 % | 0 | 0 |
| 600 | 2 500 | 180 | 60 % | 360 | 100 |
| 900 | 3 000 | 270 | 66,7 % | 600 | 400 |
| 2 000 | 5 000 | 600 | 80 % | 1 600 | 500 |
| **Total : 4 025** | | **1 207,5** | | **2 560** | **1 000** |

Avec la quote-part de 30 %, la cédante garde 2 817,5 : chaque sinistre est réduit de 30 %, **la forme de la distribution ne change pas**, seule son échelle. Avec l'excédent de plénitude de 1 000, elle cède plus (2 560) et garde 1 465 : le traité prélève surtout sur les gros risques, donc sur les gros sinistres. Pour le sinistre de 600, par exemple, le risque valait 2 500, la cédante en garde $1\,000/2\,500=40\,\%$ et cède donc $60\,\%\times600=360$.

![Trois façons de partager les mêmes huit sinistres. En bleu, la part gardée par la cédante ; en orange, la part cédée.](figures/ch06-formes.png)


> ⚠️ **La quote-part ne réduit pas le risque relatif.** Elle réduit de 30 % la perte maximale en euros, mais le sinistre de 2 000 reste, à l'échelle de l'année, le sinistre qui domine. Elle sert surtout à **alléger le capital** et à **financer la croissance** (la commission). Pour couper la queue, il faut un traité qui se déclenche **sur les gros montants**.

### 6.1.3 Les traités non proportionnels

Dans un traité **non proportionnel**, le réassureur ne paie que **la part des sinistres qui dépasse un seuil**, et la prime n'est plus un pourcentage de la prime d'origine : elle se tarife (section 6.2).

**L'excédent de sinistre par risque** (*per risk excess of loss*). La tranche « $L$ xs $a$ » a une **priorité** $a$ (le montant que la cédante garde toujours) et une **portée** $L$ (le maximum que le réassureur paie par sinistre). Pour un sinistre $X$, le réassureur paie
$$R(X)=\min\bigl(\max(X-a,\,0),\;L\bigr),$$
et la cédante garde $X-R(X)$. Sur nos huit sinistres, la tranche « 500 xs 500 » paie $100$ pour le sinistre de 600, $400$ pour celui de 900, et $500$ (la portée entière) pour celui de 2 000 : **1 000 en tout**, soit un quart du total, alors qu'elle n'intervient que sur trois sinistres.

**L'excédent de sinistre par événement** (*catastrophe*, ou cat XL). Même mécanisme, mais le sinistre est **la somme des pertes d'un même événement** (une tempête, une inondation) sur toutes les polices touchées, dans une fenêtre de temps que la clause précise. Il couvre l'accumulation, pas le sinistre unitaire.

**Le stop-loss** couvre la **charge annuelle totale**, ou le rapport sinistres à primes, au-delà d'un seuil. Avec une prime de 4 500 et une garantie « 1 000 xs 3 500 », une année à 4 025 de sinistres coûte au réassureur $4\,025-3\,500=525$.

**Les clauses de limite annuelle et de réintégration.** Une tranche à portée $L$ ne peut pas être consommée sans fin. Un **plafond annuel** (*annual aggregate limit*) borne le total payé sur l'année, souvent à $(1+k)L$ où $k$ est le nombre de **réintégrations** : après un sinistre qui consomme une partie de la portée, la garantie est **reconstituée**, contre une **prime de réintégration**, généralement proportionnelle à la portée utilisée (*pro rata amount*).

Voyons-le sur la tranche « 500 xs 500 », de prime annuelle 300 (un montant d'exemple), avec **une** réintégration à 100 % pro rata du montant. Les trois sinistres touchent la tranche pour $100$, $400$ puis $500$. Les deux premiers consomment $500$ de portée au total, qui sont reconstitués : prime de réintégration $300\times100/500=60$, puis $300\times400/500=240$, soit **300**. Pour le troisième, la seule réintégration disponible est épuisée : il est payé (le plafond annuel est de $2\times500=1\,000$, atteint), mais ne donne pas lieu à reconstitution. Bilan de l'année : récupérations $1\,000$, coût de la protection $300+300=600$, **gain net 400**.


On exprime souvent le prix d'une tranche de deux façons. Le **taux de prime** divise la prime de la tranche par la **prime d'origine** de la cédante (la prime sur laquelle elle porte). Le **rate on line** (**ROL**) divise la prime par la **portée** $L$ ; son inverse, la **période de retour** (*payback*), est le nombre d'années de prime nécessaires pour payer une perte totale de la tranche. Un ROL de 5 % correspond à un *payback* de 20 ans : c'est le langage des tranches de catastrophe, rarement touchées.

| | Proportionnel | Non proportionnel |
|---|---|---|
| Partage | primes et sinistres, même proportion | les sinistres au-delà d'un seuil |
| Effet sur la variance | réduit l'échelle, pas la forme | **coupe la queue** |
| Prix | proportion de la prime d'origine (± commission) | tarifé selon l'exposition et l'expérience (6.2) |
| Intérêts | alignés : le réassureur suit la cédante | la cédante garde la fréquence ; le réassureur porte la sévérité |
| Usage typique | financer la croissance, alléger le capital | protéger contre les sinistres gros et les accumulations |

### 6.1.4 Lire un programme de réassurance

Une cédante achète rarement un seul traité. Elle empile des **couches** : une quote-part ou un petit excédent « de travail » en bas (on y est touché plusieurs fois par an), des excédents par risque au milieu, une couverture catastrophe en haut, parfois un stop-loss au sommet. La **rétention** est ce qui reste chez la cédante sous la première couche ; chaque couche est vendue à un ou plusieurs réassureurs qui se partagent la **ligne**.

Trois précautions à garder en mémoire quand on lit un programme.

**La définition de ce qui est couvert.** Un « événement » (une catastrophe) est défini par une période et une zone ; deux tempêtes à dix jours d'intervalle peuvent compter pour une ou pour deux. Les **exclusions** (guerre, risques nucléaires, cyber…) limitent la couverture réelle. Le **risque de base** (*basis risk*) est l'écart entre ce que la cédante subit et ce que le contrat paie.

**Le calendrier.** Un sinistre survenu en 2025 sera peut-être payé en 2029. Les récupérations de réassurance entrent donc dans le **provisionnement** (chapitre 2, section 2.3) : on provisionne les sinistres bruts **et** la part qui reviendra du réassureur.

**La solidité du réassureur.** La réassurance transforme un risque d'assurance en un **risque de contrepartie** : la créance sur le réassureur n'a de valeur que si celui-ci paie. Nous le chiffrerons en 6.3.4.

> ✅ **À retenir.** Un traité proportionnel partage tout au prorata et allège le capital ; un traité non proportionnel ne paie que les sinistres qui dépassent une priorité et coupe la queue de la distribution. La variance de la charge annuelle vient des gros sinistres : c'est là que la réassurance est la plus efficace. Une tranche se décrit par sa **priorité**, sa **portée**, ses **réintégrations** et son **plafond annuel**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 et 6.2, exercices 6.1 à 6.5.


## 6.2 Tarifer un traité

Combien doit coûter la tranche « 1 M€ xs 1 M€ » ? Le réassureur répond par une **prime pure** (la charge annuelle attendue de la tranche), puis par un **chargement** pour le risque et les frais. Cette section estime la prime pure de trois façons (l'expérience, la loi de queue, l'exposition), les compare à la **vérité programmée**, mesure l'incertitude de chacune, traite à part le cas des catastrophes, et passe enfin de la prime pure à la prime technique.

### 6.2.1 L'expérience : le *burning cost* et le piège de l'exposition

La méthode la plus naturelle demande : « **combien la tranche aurait-elle coûté, chaque année passée ?** ». On rejoue l'historique des sinistres à travers la tranche, année par année, et l'on fait la moyenne. C'est le **burning cost** (coût de la « combustion » passée de la tranche).

Pour que cette moyenne ait un sens, il faut ramener chaque année passée **à la situation de l'année couverte**. Trois corrections s'imposent :

1. **Développer** les sinistres récents, dont le montant final n'est pas connu (chapitre 2, sections 2.3 et 2.5). Dans nos données, les montants sont finaux ; en pratique, c'est une étape à part entière.
2. **Indexer** les montants passés au niveau de coût actuel (inflation des sinistres), **avant** d'appliquer la tranche, puisque la tranche s'applique à chaque sinistre au prix d'aujourd'hui.
3. **Ajuster l'exposition** : une année où le portefeuille était plus petit aurait produit plus de sinistres avec le portefeuille d'aujourd'hui.

Avec $C_t$ la charge de la tranche sur l'année $t$ et $E_t$ l'exposition de cette année (nombre de risques, primes, capitaux assurés…), le *burning cost* de l'année couverte $T$ est
$$\mathrm{BC}=\frac1n\sum_{t=1}^{n}C_t\cdot\frac{E_T}{E_t}.$$

Ici, le portefeuille croît de 3 % par an : l'exposition de 2025 vaut $1{,}03^{15}\approx1,56$ fois celle de 2010. Comparons le *burning cost* **brut** (sans correction) et **ajusté** de l'exposition, aux trois tranches « par risque » suivantes.

```python
for a, L in O.COUCHES:
    brut, _ = O.burning_cost(sg, a, L, ajuste=False)
    ajuste, _ = O.burning_cost(sg, a, L)
    print(f"{L/1e6:g} xs {a/1e6:g} : brut {brut/1e6:.2f} M€  ajusté {ajuste/1e6:.2f} M€  vérité {O.prix_vrai(a, L)/1e6:.2f} M€")
```
<!--sortie-->
```text
0.5 xs 0.5 : brut 3.19 M€  ajusté 4.07 M€  vérité 4.47 M€
1 xs 1 : brut 1.95 M€  ajusté 2.50 M€  vérité 2.63 M€
2 xs 2 : brut 0.78 M€  ajusté 1.01 M€  vérité 1.42 M€
```

Le *burning cost* brut sous-estime de 29, 26 et 45 % les trois tranches : il traite 2010 et 2024 comme si le portefeuille avait toujours eu la même taille. L'ajustement d'exposition supprime ce **biais** (il reste des écarts de -9 %, -5 % et -29 %, signes compris, qui relèvent du **bruit d'échantillonnage** que nous mesurerons en 6.2.4).

![Charge annuelle de chaque tranche, brute (gris) et ramenée à l'exposition 2025 (bleu). La ligne orange est la charge annuelle attendue réelle.](figures/ch06-burning.png)

La figure montre ce que cache la moyenne : la tranche haute (« 2 M€ xs 2 M€ ») a coûté **moins de 0,09 M€ par an de 2015 à 2021**, puis jusqu'à 2,1 M€ en 2024. Une tarification fondée sur la seule période calme aurait donné un prix dérisoire.

> ⚠️ **L'indexation est une hypothèse, pas une formalité.** L'inflation des sinistres s'**applique avant la tranche**, et la tranche **l'amplifie** : si tous les sinistres augmentent de 4 % par an, un sinistre de 900 000 € passe en dix ans à environ 1,33 M€, c'est-à-dire qu'il **entre** dans la tranche « 1 M€ xs 1 M€ » qu'il ne touchait pas. C'est l'**effet de levier de l'inflation sur les tranches**. Dans nos données, il n'y a **aucune** inflation de la sévérité : sur les sinistres de plus de 500 000 €, la pente du logarithme du montant selon l'année est de -0,41 % par an (statistiquement nulle). Si l'on avait indexé à 4 % par habitude, les trois tranches auraient été surestimées de 46, 73 et 86 % : une erreur de **+86 %** sur la tranche la plus haute. Le taux d'indexation doit être **estimé et justifié**, pas hérité.


> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.3 et exercices 6.6 et 6.7.

### 6.2.2 La tarification par l'exposition

Le *burning cost* exige un historique. Pour un **nouveau traité**, ou une tranche qui n'a jamais été touchée, on ne peut pas s'y fier. La **tarification par l'exposition** part d'une autre idée : au lieu d'observer ce que la tranche a coûté, on **décrit la répartition des sinistres** à l'aide d'une **courbe d'exposition**, et l'on en déduit la part de la charge totale qui tombe dans la tranche.

Soit $X$ un sinistre. La **courbe d'exposition** (ou *limited expected value* normalisée) est
$$G(d)=\frac{E[\min(X,d)]}{E[X]},$$
la **part de la charge attendue qui se situe sous le plafond $d$**. La charge attendue d'une tranche « $L$ xs $a$ » est alors
$$E\bigl[\min(\max(X-a,0),L)\bigr]=E[X]\,\bigl(G(a+L)-G(a)\bigr),$$
puisque $\min(\max(X-a,0),L)=\min(X,a+L)-\min(X,a)$. Multipliée par le nombre attendu de sinistres $\lambda$, elle donne la prime pure de la tranche. En pratique, on applique la courbe à **chaque risque de capital assuré $V_i$** (le plafond relatif est $d/V_i$), à l'aide de courbes publiées pour chaque type de risque : c'est ce qu'on fait pour les risques industriels, quand l'historique est mince.

Notre jeu de données n'a pas de capitaux assurés ; nous pouvons toutefois **estimer la courbe d'exposition à partir des sinistres eux-mêmes**, en euros.

| Plafond $d$ | 100 000 | 250 000 | 500 000 | 1 000 000 | 2 000 000 | 3 000 000 |
|---|---:|---:|---:|---:|---:|---:|
| $G(d)$ | 37,8 % | 56,9 % | 73,5 % | 87,7 % | 96,4 % | 99,3 % |

Lecture : 73,5 % de la charge attendue se situe sous 500 000 € par sinistre ; les **26,5 % restants** viennent des parties de sinistres au-delà de 500 000 €, et 12,3 % au-delà de 1 M€. La tranche « 1 M€ xs 1 M€ » reçoit donc $G(2\,\mathrm{M€})-G(1\,\mathrm{M€})=8,7$ % de la charge : en multipliant par la charge annuelle attendue (249 sinistres de moyenne 115 984 €), on trouve 2,52 M€, contre 2,63 M€ en vérité. Pour les trois tranches, cette approche « **fréquence × sévérité empirique** » donne 4,11, 2,52 et 1,00 M€.

#### Un exemple à la main avec une loi de Pareto

Supposons que les sinistres au-delà de 500 000 € soient au nombre de 15 par an et suivent une loi de Pareto de paramètre 2 : $P(X>x\mid X>u)=(u/x)^2$ avec $u=500\,000$. La charge annuelle attendue de la tranche « 1 M€ xs 1 M€ » est
$$15\int_{1\,000\,000}^{2\,000\,000}\Bigl(\frac{500\,000}{x}\Bigr)^2dx=15\times(500\,000)^2\Bigl(\frac1{1\,000\,000}-\frac1{2\,000\,000}\Bigr)=15\times125\,000=1\,875\,000\ \text{€}.$$
On voit le mécanisme : **tout repose sur la forme supposée de la queue**. Avec un exposant de 1,5 (queue plus lourde) la même tranche coûterait 3,11 M€ ; avec 3 (queue plus légère), 0,70 M€.


> 💡 **Deux méthodes, deux informations.** Le *burning cost* dit ce que la tranche **a coûté** ; l'exposition dit ce que la tranche **devrait coûter** si les sinistres se répartissent comme le suppose la courbe. Quand l'historique est riche, la première est plus honnête ; quand il est mince, la seconde est la seule disponible, et sa validité dépend de la courbe choisie.

### 6.2.3 Ajuster une loi de queue : la GPD

Le *burning cost* de la tranche haute repose sur très peu de sinistres. Pour mieux utiliser l'information, on **ajuste une loi** à la queue et l'on calcule la prime par une formule. La théorie des valeurs extrêmes (volume II, section 6.5) assure que les dépassements d'un seuil élevé $u$ suivent, sous des conditions générales, une **loi de Pareto généralisée** (GPD) :
$$P(X-u>y\mid X>u)=\Bigl(1+\xi\,\frac{y}{\beta}\Bigr)^{-1/\xi},\qquad y\ge0,$$
où $\xi$ est l'**indice de queue** (plus il est grand, plus la queue est lourde ; $\xi\ge1$ rend la moyenne infinie) et $\beta$ un paramètre d'échelle.

Pour un seuil $u$ et un nombre annuel $\lambda_u$ de dépassements, la prime pure d'une tranche « $L$ xs $a$ » avec $a\ge u$ est
$$\lambda_u\int_a^{a+L}\Bigl(1+\xi\,\frac{x-u}{\beta}\Bigr)^{-1/\xi}dx=\lambda_u\,\frac{\beta}{1-\xi}\Bigl[\Bigl(1+\xi\frac{a-u}{\beta}\Bigr)^{1-1/\xi}-\Bigl(1+\xi\frac{a+L-u}{\beta}\Bigr)^{1-1/\xi}\Bigr].$$

> 📐 **Pourquoi cette formule.** Pour un sinistre $X$, $\min(\max(X-a,0),L)=\int_a^{a+L}\mathbf 1\{X>x\}\,dx$. En prenant l'espérance (échange de l'intégrale et de l'espérance, théorème de Fubini) et en multipliant par le nombre annuel $\lambda$ de sinistres, la charge annuelle attendue vaut $\int_a^{a+L}\lambda P(X>x)\,dx$. Or, pour $x\ge u$, $\lambda P(X>x)=\lambda_u\,P(X>x\mid X>u)$, la survie de la GPD. Une primitive de $\bigl(1+\xi\frac{x-u}{\beta}\bigr)^{-1/\xi}$ est $-\frac{\beta}{1-\xi}\bigl(1+\xi\frac{x-u}{\beta}\bigr)^{1-1/\xi}$, d'où la formule.

Ajustons-la au seuil de 500 000 €, avec le nombre annuel de dépassements ramené à l'exposition de 2025.

```python
u = 5e5
exces = sg["montant"].values[sg["montant"].values > u] - u
xi, _, beta = stats.genpareto.fit(exces, floc=0)
lam_u = O.taux_depassement(sg, u)
print(f"n = {len(exces)}  xi = {xi:.3f}  beta = {beta:,.0f}  lambda_u = {lam_u:.1f} par an")
```
<!--sortie-->
```text
n = 177  xi = 0.416  beta = 312,975  lambda_u = 15.0 par an
```

On obtient $\hat\xi=0,416$ et $\hat\beta=312 975$ € sur 177 dépassements, soit 15,0 par an au niveau 2025. Les prix de la formule sont de 4,11, 2,21 et 1,02 M€ pour les trois tranches.

> ⚠️ **Le choix du seuil est un choix de modèle.** Si $u$ est trop bas, la loi ne suit plus la GPD (on y mêle le corps de la distribution) ; trop haut, il reste trop peu de points. On regarde la **stabilité** de $\hat\xi$ quand $u$ varie. La figure ci-dessous le montre : $\hat\xi$ vaut 0,22 au seuil de 300 000 €, 0,42 à 500 000 €, et -0,15 à 1 M€, où il devient **négatif** (une queue qui « s'arrête ») alors que nous savons que la vraie queue est très lourde ($\xi=0{,}55$). À ce seuil, il ne reste que 49 dépassements : la bande d'incertitude de $\hat\xi$ est large, et le résultat n'est pas fiable.

![À gauche, l'excès moyen au-delà d'un seuil ; à droite, l'estimation de l'indice de queue selon le seuil, avec sa bande d'incertitude.](figures/ch06-gpd.png)

Le prix de la tranche la plus haute dépend de ce choix. Avec les seuils de 300 000 €, de 500 000 € et de 1 M€, le prix de « 2 M€ xs 2 M€ » vaut respectivement 0,83, 1,02 et 0,93 M€, alors que la vérité est de 1,42 M€. **Aucun** de ces chiffres n'est faux au sens du calcul : ils reflètent l'incertitude du modèle, qu'il faut annoncer plutôt que cacher.


Mettons toutes les estimations côte à côte, en M€ par an au niveau de 2025.

| Tranche | *Burning cost* brut | *Burning cost* ajusté | Fréquence × sévérité | GPD (seuil 500 000) | **Vérité** |
|---|---:|---:|---:|---:|---:|
| 0,5 M€ xs 0,5 M€ | 3,19 | 4,07 | 4,11 | 4,11 | **4,47** |
| 1 M€ xs 1 M€ | 1,95 | 2,50 | 2,52 | 2,21 | **2,63** |
| 2 M€ xs 2 M€ | 0,78 | 1,01 | 1,00 | 1,02 | **1,42** |

Trois remarques. La correction d'exposition est **indispensable** : le brut est loin de tout le reste. Les trois estimations corrigées sont **voisines** entre elles : elles utilisent les mêmes données, donc partagent les mêmes aléas. Et elles sont **toutes en dessous** de la vérité sur la tranche haute. Est-ce un biais de méthode ou la malchance de ces quinze années ? C'est la question de la section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.4 et 6.5 et exercices 6.8 à 6.10.

### 6.2.4 Mesurer l'incertitude : le même tarif aurait pu être très différent

Nos quinze années d'observation sont **un tirage parmi beaucoup d'autres possibles**. Pour mesurer l'incertitude d'une estimation, on veut savoir ce qu'elle serait sur d'autres tirages. On en a deux moyens.

**Le bootstrap par années.** On rééchantillonne les **années** (avec remise) : chaque année est une observation de la charge annuelle de la tranche. On refait le calcul du *burning cost* sur chaque rééchantillon, et l'on lit un intervalle de 2,5 % à 97,5 %. On rééchantillonne des années entières et non des sinistres, parce que les sinistres d'une même année partagent la même exposition. Voici l'intervalle pour les trois tranches :

| Tranche | Estimation ajustée | Intervalle à 95 % (bootstrap) | Largeur relative |
|---|---:|---|---:|
| 0,5 M€ xs 0,5 M€ | 4,07 M€ | de 3,45 à 4,65 | ± 15 % |
| 1 M€ xs 1 M€ | 2,50 M€ | de 1,77 à 3,20 | ± 29 % |
| 2 M€ xs 2 M€ | 1,01 M€ | de 0,56 à 1,54 | ± 49 % |

L'incertitude **grandit à mesure que l'on monte**, parce que la tranche haute est touchée par peu de sinistres : dans l'historique, seuls 15 sinistres dépassent 2 M€. La vérité, qui reste dans les trois intervalles ici, n'y serait pas **forcément** : « 95 % » n'est pas « toujours ».

**Rejouer l'expérience sous la vérité.** Puisque nous connaissons la loi qui a produit les données, nous pouvons refaire **300 fois** l'aventure « quinze années d'observation », calculer chaque fois le *burning cost* ajusté, et regarder la dispersion. C'est un luxe de simulation : en vrai, on n'a qu'une histoire.

| Tranche | Moyenne des 300 estimations | Coefficient de variation | Part des estimations sous la vérité |
|---|---:|---:|---:|
| 0,5 M€ xs 0,5 M€ | 4,46 M€ | 8 % | 51 % |
| 1 M€ xs 1 M€ | 2,63 M€ | 16 % | 50 % |
| 2 M€ xs 2 M€ | 1,42 M€ | 31 % | 51 % |

La moyenne des estimations est **voisine de la vérité** : la méthode corrigée de l'exposition n'est pas biaisée. Mais son **erreur typique** est de 8 %, 16 % et 31 % : une erreur de -29 % sur la tranche haute (celle de notre échantillon) est donc banale, de l'ordre d'un écart-type. Le réassureur et la cédante qui s'accordent sur le prix de la tranche haute se mettent d'accord sur un chiffre dont l'incertitude est **du même ordre que le chargement qu'ils négocient**.

![Estimations de la charge annuelle de chaque tranche : *burning cost* brut (gris), ajusté avec son intervalle bootstrap (bleu), GPD (violet). La ligne orange est la vérité.](figures/ch06-tranches.png)


> 💡 **Une prime est une estimation.** Le « prix » d'une tranche haute est, avec 15 ans de données, une fourchette large. Les réassureurs le savent : c'est pourquoi les tranches hautes se tarifient avec des **modèles**, des **hypothèses prudentes** et des **chargements**, et pas avec la seule moyenne observée.

### 6.2.5 Les catastrophes : peu de données, beaucoup d'incertitude

Pour les catastrophes, l'historique est encore plus mince : **17 événements en 40 ans**. Le tarif d'une tranche de catastrophe repose sur le **modèle de queue** presque seul.

Nous ajustons une loi de Pareto $P(X>x)=(x_m/x)^{\alpha}$ aux pertes des années à événement, avec un minimum $x_m=2$ M€ (la plus petite perte observée vaut 2,11 M€). L'estimateur du maximum de vraisemblance de $\alpha$ est $\hat\alpha=n/\sum\ln(x_i/x_m)$, soit ici 1,33, et la fréquence des années à événement vaut 42,5 %. Le tableau compare l'estimation empirique, la loi ajustée et la vérité, pour trois tranches.

| Tranche | Empirique | Pareto ajusté | Vérité | Intervalle bootstrap |
|---|---:|---:|---:|---|
| 5 M€ xs 5 M€ | 0,46 | 0,39 | **0,54** | 0,11 à 0,89 |
| 10 M€ xs 10 M€ | 0,26 | 0,31 | **0,50** | 0,00 à 0,79 |
| 20 M€ xs 20 M€ | 0,39 | 0,24 | **0,46** | 0,00 à 1,17 |

L'intervalle de la tranche « 10 M€ xs 10 M€ » commence à **zéro** : certains rééchantillonnages de 40 ans n'ont aucune perte dans la tranche. Sur 40 ans, la loi ajustée sous-estime la queue ($\hat\alpha=1,33$ contre une vérité de 1,11) : l'exposant est surestimé, la queue paraît plus légère, les tranches hautes sont sous-tarifées, et la méthode empirique se trompe dans le même sens. Avec 17 points, un écart de cette taille est banal : **les observations de pertes extrêmes sont rares par nature**, et un échantillon court ne contient en général pas la pire perte possible.

![À gauche, la queue des pertes d'événement (échelle logarithmique) : observations, loi ajustée et vérité. À droite, la charge annuelle de trois tranches de catastrophe selon la méthode.](figures/ch06-cat.png)

Pour une tranche de catastrophe, on parle plutôt en **ROL** qu'en pourcentage de prime. Si la tranche « 10 M€ xs 10 M€ » est vendue à son prix pur de 0,50 M€, son ROL est de 5,0 %, soit une période de retour de 20 ans : pendant ce temps, la cédante paie chaque année, et ne récupère l'équivalent d'une portée entière, en moyenne, qu'une fois en 20 ans. Le réassureur n'a guère plus d'information que nous : il s'appuie sur des **modèles de catastrophe** (physiques ou statistiques), hors du champ de cet ouvrage.


> ⚠️ **Quand les données manquent, le chargement n'est pas un luxe.** Une tranche de catastrophe dont l'espérance est connue à un facteur deux près se vend nécessairement avec un chargement important : il rémunère l'incertitude du réassureur autant que son risque.

### 6.2.6 De la prime pure à la prime technique

La prime pure est l'espérance de la charge. Le prix facturé par le réassureur, la **prime technique**, ajoute un **chargement** qui couvre les frais, le coût du capital et la marge. Deux principes classiques, tous deux **illustratifs** ici (les paramètres sont ceux d'un exemple, pas ceux d'un marché) :

- **Le principe de l'écart-type** : $\pi=E[S]+k\,\sigma(S)$, où $S$ est la charge annuelle de la tranche et $k$ un coefficient d'aversion (nous prenons $k=0{,}15$).
- **Le principe du coût du capital** : le réassureur immobilise un capital $K$ pour porter le risque (la perte inattendue à 99,5 %, $K=\mathrm{VaR}_{99{,}5\,\%}(S)-E[S]$, voir section 3.1) et exige un rendement de $i$ sur ce capital : $\pi=E[S]+i\,K$ (nous prenons $i=8\,\%$).

Pour les calculer, il faut la **distribution** de la charge annuelle de la tranche, pas seulement sa moyenne. Nous la simulons (20 000 années, nombre de sinistres de Poisson, montants tirés sous la loi des sinistres) :

| Tranche | Espérance | Écart-type | VaR à 99,5 % | Capital $K$ | Prime (écart-type) | Prime (coût du capital) |
|---|---:|---:|---:|---:|---:|---:|
| 1 M€ xs 1 M€ | 2,61 M€ | 1,43 M€ | 7,04 M€ | 4,43 M€ | 2,82 M€ (+8 %) | 2,96 M€ (+14 %) |
| 2 M€ xs 2 M€ | 1,42 M€ | 1,49 M€ | 6,45 M€ | 5,03 M€ | 1,64 M€ (+16 %) | 1,82 M€ (+28 %) |

Plus la tranche est haute, plus le **risque relatif** est grand (l'écart-type est supérieur à l'espérance pour la tranche « 2 M€ xs 2 M€ »), donc plus le chargement relatif l'est aussi. Un chargement unique, exprimé en pourcentage de la prime pure, ne peut pas convenir aux deux tranches : il faut ajouter 8 % à la première et 16 % à la seconde avec le principe de l'écart-type, ou 14 % et 28 % avec le coût du capital. Le chargement suit le **risque**, pas la prime.

Reste le coût des **réintégrations** et d'éventuelles **commissions** de courtage, qui s'ajoutent à la prime technique. Le prix final n'est donc pas une simple « moyenne plus dix pour cent » : c'est un compromis entre le modèle du réassureur, son appétit, son capital disponible et la concurrence du moment.


> ✅ **À retenir.** La prime pure d'une tranche s'estime par l'expérience (*burning cost*, **à ajuster de l'exposition et de l'inflation**, qui s'amplifie dans les tranches), par une loi de queue (GPD), ou par l'exposition (courbe d'exposition) ; ces méthodes se comparent mais partagent les mêmes données. Pour les tranches hautes et les catastrophes, l'incertitude est **du même ordre que le chargement** : il faut la mesurer (bootstrap) et l'annoncer. La prime technique ajoute un chargement proportionnel au **risque** (écart-type, coût du capital), pas à la prime pure.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.3 à 6.8, exercices 6.6 à 6.12.


## 6.3 Choisir une couverture

Savoir tarifer une tranche ne dit pas s'il faut l'acheter. Cette section se place du côté de la **cédante** : elle simule la charge annuelle, mesure ce que chaque programme de réassurance retire de la volatilité et du capital, et le compare à son coût. Elle termine par ce qui peut mal tourner : un réassureur qui ne paie pas, une garantie épuisée, un prix qui semble trop beau.

### 6.3.1 Le modèle de la cédante

Pour comparer des programmes, il faut un **modèle du résultat annuel** de la cédante. Le nôtre est volontairement simple :

- le nombre de sinistres de l'année suit une loi de Poisson de moyenne 249 (niveau d'exposition de 2025) ;
- chaque montant est tiré avec remise parmi les sinistres observés (nous reprenons la loi **empirique**, pas la vérité) ;
- la prime d'origine $P$ est fixée pour que la sinistralité attendue soit de **70 %** de $P$, les frais de **25 %** et la marge attendue de **5 %** ;
- le résultat annuel brut est $R=0{,}75\,P-S$, où $S$ est la charge annuelle brute.

Nous mesurons un programme par quatre grandeurs : la **moyenne** et l'**écart-type** du résultat, la **probabilité de ruine** (un résultat inférieur à $-C_0$ avec un capital de départ $C_0=8$ M€), et la **perte inattendue** $K=E[R]-q_{0{,}5\,\%}(R)$, le capital qu'il faut détenir pour absorber une année à 1 chance sur 200. $K$ est une version simplifiée du capital réglementaire (VaR à 99,5 % sur un an, section 4.2) ; la VaR et l'*expected shortfall* sont détaillées en section 3.1.

```python
simu = O.simuler(N=20000, seed=2026)          # 20 000 années au niveau d'exposition 2025
prime = simu["brute"].mean() / 0.70           # sinistres 70 %, frais 25 %, marge 5 %
resultat_brut = 0.75 * prime - simu["brute"]  # prime nette de frais, moins les sinistres
K0 = resultat_brut.mean() - np.percentile(resultat_brut, 0.5)
print(f"prime {prime/1e6:.1f} M€  résultat moyen {resultat_brut.mean()/1e6:.2f}  écart-type {resultat_brut.std()/1e6:.2f}  K {K0/1e6:.1f}")
```
<!--sortie-->
```text
prime 41.3 M€  résultat moyen 2.06  écart-type 4.95  K 14.3
```

La prime d'origine est de 41,3 M€ ; le résultat moyen est de 2,06 M€ (5 % de la prime), avec un écart-type de 4,95 M€, soit **plus de deux fois le résultat attendu** : une année sur trois environ est déficitaire. Une année sur 200, le résultat tombe à -12,2 M€ : $K=14,3$ M€. Avec un capital de 8 M€, la probabilité de ruine à un an vaut 3,0 %.

> ⚠️ **Limites du modèle.** Les sinistres sont tirés **parmi ceux déjà observés** : une année simulée ne peut pas contenir un sinistre plus gros que le plus gros observé (4 310 320 €). La queue est donc **tronquée**, et les capitaux ci-dessous sont des **minima**. Nous ne simulons pas non plus d'événement catastrophique dans cette étape (il fait l'objet de 6.3.3).

### 6.3.2 Comparer des programmes

Cinq programmes sont comparés au cas sans réassurance. Les prix sont des **hypothèses d'exemple**, pas des cotations : pour les excédents de sinistre, la prime est l'espérance simulée des récupérations multipliée par $1+$ un chargement ; pour la quote-part, la prime cédée est 20 % de $P$ et la commission de cession est de 25 % de la prime cédée (elle couvre les frais, cf. 6.1.2).

| Programme | Chargement | Coût annuel | Écart-type | $K$ | Capital économisé | Coût par € économisé | Ruine à 8 M€ |
|---|---:|---:|---:|---:|---:|---:|---:|
| Aucun | | | 4,95 M€ | 14,25 M€ | | | 3,0 % |
| XL 0,5 M€ xs 0,5 M€ | 30 % | 1,23 M€ | 3,89 M€ | 11,35 M€ | 2,90 M€ | 0,42 | 2,0 % |
| XL 1 M€ xs 1 M€ | 35 % | 0,88 M€ | 3,92 M€ | 11,25 M€ | 3,00 M€ | 0,29 | 1,5 % |
| XL 2 M€ xs 2 M€ | 50 % | 0,50 M€ | 4,38 M€ | 12,44 M€ | 1,82 M€ | 0,27 | 2,0 % |
| Quote-part 20 % | commission 25 % | 0,41 M€ | 3,96 M€ | 11,40 M€ | 2,85 M€ | 0,14 | 1,3 % |
| Stop-loss 10 M€ xs 38 M€ | 40 % | 0,04 M€ | 4,70 M€ | 9,22 M€ | 5,03 M€ | 0,008 | 0,0 % |

Le **coût annuel** est la prime payée moins les récupérations attendues : c'est la **marge du réassureur**, ce que la cédante abandonne en moyenne pour réduire son risque. Le **coût par euro économisé** divise ce coût par le capital libéré ($K$ sans réassurance moins $K$ avec).

![À gauche, la distribution du résultat annuel sans réassurance et avec trois programmes. À droite, le coût de chaque programme et le capital qu'il économise ; la droite en pointillé marque le point d'équilibre pour un coût du capital de 8 %.](figures/ch06-programmes.png)

La lecture est instructive.

**Les tranches « de travail » coûtent cher pour ce qu'elles font.** « 0,5 M€ xs 0,5 M€ » est touchée une quinzaine de fois par an : la cédante paie une prime de 5,3 M€ pour récupérer 4,1 M€ en moyenne, c'est-à-dire un échange presque certain d'argent contre de l'argent, **moins** un chargement de 1,23 M€. Elle libère 2,9 M€ de capital, soit 0,42 € de coût par euro économisé.

**La quote-part est la moins chère des protections « générales »**, parce que la commission de cession de 25 % rembourse exactement les frais de la cédante : le coût ne vient que de l'écart entre la marge de la cédante et celle du réassureur. Elle réduit le risque dans la même proportion que la cession (20 %), mais ne cible pas la queue.

**Le stop-loss est de loin le plus efficace par euro**, parce qu'il ne protège que l'extrême (il se déclenche dans 4,1 % des années), exactement là où se situe $K$. Mais il est aussi le plus **fragile** : son prix repose sur la queue de la distribution, que nous connaissons le moins bien (6.2.4), et un réassureur le vend rarement à un chargement aussi bas que les 40 % supposés.

Les écarts entre programmes voisins doivent être lus avec prudence. Avec 20 000 années simulées, le quantile à 0,5 % repose sur 100 années ; son erreur-type, estimée par bootstrap, est de 0,30 M€. Une différence de $K$ de quelques dixièmes de M€ n'est pas significative.


#### Combien faudrait-il que la protection coûte ?

Si la cédante raisonne **uniquement** en coût du capital (un euro de capital immobilisé lui coûte 8 % par an), une protection vaut son prix quand $\text{coût}\le 8\,\%\times\text{capital libéré}$. Pour les trois excédents de sinistre, cela correspond à des chargements d'**équilibre** de 6 %, 10 % et 15 % de la prime pure, très inférieurs aux chargements supposés (30 %, 35 %, 50 %). **Au seul coût du capital, ces tranches ne se paient pas.** Alors pourquoi en acheter ?

Parce que le coût du capital n'est pas la seule raison. La cédante achète aussi :

- de la **stabilité** (l'écart-type du résultat) : la cédante cotée, la mutuelle qui fait face à ses adhérents, l'entreprise qui doit verser des dividendes réguliers valorisent un résultat moins volatil ;
- le respect d'une **contrainte** : un ratio de solvabilité à tenir (section 4.2), une notation à préserver, une probabilité de ruine à ne pas dépasser (la colonne « ruine » du tableau) ; dans ce cas, c'est la **contrainte** qui fixe le besoin de réassurance, et le coût est le prix de la conformité ;
- de la **capacité** pour souscrire des risques plus gros, dont la marge compense le coût.

> 💡 **Un programme se juge sur un tableau, pas sur un chiffre.** Le coût, la volatilité, le capital, la ruine : on regarde les quatre, et l'on décide selon ce qui contraint réellement la cédante. Un programme qui économise beaucoup de capital pour un coût élevé n'est « bon » que si le capital est effectivement rare.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.9 et exercices 6.9 à 6.12.

### 6.3.3 Et la catastrophe ?

Ajoutons maintenant la perte annuelle liée aux événements catastrophiques. Nous la tirons de **trois façons**, que nous avons déjà rencontrées en 6.2.5 : par tirage avec remise parmi les 40 années **observées**, par la loi de **Pareto ajustée** ($\hat\alpha=1,33$), et sous la **vérité** ($\alpha=1{,}11$).

Le réassureur propose une **tour** de trois tranches : 5 M€ xs 5 M€, 10 M€ xs 10 M€ et 20 M€ xs 20 M€, qui couvre les pertes d'événement jusqu'à 40 M€. Nous supposons que son prix vaut **1,5 fois l'espérance sous la vérité** (le réassureur dispose de modèles de catastrophe) : 2,26 M€ par an. La cédante, elle, juge l'intérêt de la tour avec **son** modèle de la catastrophe.

| Vue de la cédante sur la catastrophe | Perte cat. moyenne | Perte cat. à 99,5 % | $K$ sans tour | $K$ avec tour | Capital économisé | Coût par € économisé |
|---|---:|---:|---:|---:|---:|---:|
| Années observées (rééchantillonnage) | 2,7 M€ | 35,6 M€ | 37,1 M€ | 15,1 M€ | 22,0 M€ | 0,05 |
| Pareto ajusté | 2,8 M€ | 47,2 M€ | 44,7 M€ | 18,2 M€ | 26,6 M€ | 0,05 |
| **Vérité programmée** | 5,7 M€ | 114,2 M€ | 108,0 M€ | 74,5 M€ | 33,5 M€ | 0,02 |

Trois constats. D'abord, la **catastrophe domine tout** : avec elle, $K$ passe de 14,3 M€ à 37,1 M€ dès la vue la plus optimiste, soit presque le niveau de la prime (41,3 M€) : la cédante de l'exemple **ne peut pas porter** ce risque sans réassurance. Ensuite, **la vue de la cédante change la valeur de la tour** : avec les seules années observées, la tour semble coûter 0,05 € par euro de capital libéré ; avec la vérité, 0,02 €. Les données courtes rendent la protection **moins attrayante qu'elle ne l'est**, parce qu'elles sous-estiment la queue (6.2.5). Enfin, même avec une tour jusqu'à 40 M€, le capital restant est de 74,5 M€ sous la vérité : **au-delà de 40 M€, la cédante porte tout**, et un seul événement de 100 M€ suffit à ruiner le portefeuille. Une tour se dimensionne sur ce que l'on est prêt à perdre, pas sur ce que les données montrent.


### 6.3.4 Contrepartie, épuisement et prix trop bas

La réassurance déplace le risque ; elle ne le supprime pas. Trois fragilités méritent un chiffre.

#### Le risque de contrepartie

Une créance sur un réassureur n'a de valeur que si celui-ci paie. Simulons le **stop-loss** du tableau précédent dans trois mondes : un réassureur **toujours solvable** ; un réassureur qui fait défaut avec une probabilité de 0,5 % par an, **indépendamment** des sinistres, et ne paie alors que la moitié des récupérations ; et un réassureur qui fait défaut avec une probabilité de 10 % **précisément les années où la charge brute dépasse son 99ᵉ centile** (un défaut lié à un événement majeur, qui frappe souvent plusieurs cédantes à la fois).

| Monde | Probabilité de ruine à 8 M€ |
|---|---:|
| Aucune réassurance | 2,98 % |
| Réassureur toujours solvable | 0,04 % |
| Défaut indépendant (0,5 % par an) | 0,05 % |
| Défaut lié aux gros sinistres (10 % dans le 1 % pire) | 0,14 % |

Un défaut **indépendant** change peu le résultat (la ruine reste proche de 0,05 %). Un défaut **corrélé aux sinistres** (0,14 %) multiplie la probabilité de ruine par 3,2 par rapport au cas parfait : le réassureur manque **quand on a le plus besoin de lui**. C'est le **risque de corrélation défavorable** (*wrong-way risk*). Les parades sont la **diversification** des réassureurs, une exigence de **notation** minimale, le **nantissement** de garanties et des clauses de résiliation en cas de dégradation.

#### L'épuisement de la garantie

Revenons à la tranche « 2 M€ xs 2 M€ ». Si on la vend avec une **réintégration** (plafond annuel de 4 M€, soit deux portées), la charge annuelle de la tranche atteint ce plafond dans 7,7 % des années. Sans réintégration (plafond de 2 M€), la garantie s'épuise dans 36,6 % des années, et **la part des pertes attendues qui n'est pas couverte** vaut 26 % de l'espérance : le plafond annuel retire du prix de la tranche ce qu'il retire de la couverture.

#### Le prix trop bas

Une offre de réassurance moins chère que les autres peut être une bonne affaire ou un risque caché. Les points de contrôle sont toujours les mêmes :

> ⚠️ **Quand le prix est trop beau, cherchez où le risque est passé.**
> 1. **Un plafond annuel trop bas** : sans réintégration, la tranche « 2 M€ xs 2 M€ » ne couvre que 74 % de l'espérance de pertes ; comparez son prix à celui d'une tranche réintégrable.
> 2. **Une définition étroite de l'événement** (durée trop courte, zone restreinte) : la tranche ne se déclenche pas quand la cédante en a besoin.
> 3. **Des exclusions** non chiffrées, qui retirent du champ les scénarios coûteux.
> 4. **Une notation faible** du réassureur, ou un portefeuille de réassureurs trop concentré : le risque de contrepartie.
> 5. **Un prix de cycle** : en marché mou, le prix baisse sous le niveau durable, puis remonte brutalement ; ce qui est bon marché cette année est cher à renouveler.
> 6. **Un risque de base** : l'indice déclencheur ne suit pas les pertes réelles de la cédante.


### 6.3.5 Une méthode pour décider

> 🧭 **En pratique : choisir une couverture.**
> 1. **Formuler ce qui contraint** : ratio de solvabilité, probabilité de ruine acceptable, volatilité du résultat, capacité de souscription. Sans contrainte claire, le coût du capital seul conclut presque toujours « ne pas réassurer ».
> 2. **Modéliser la charge annuelle brute** (fréquence × sévérité, catastrophes à part) et dire ce que le modèle ne sait pas faire (queue tronquée, peu d'observations).
> 3. **Chiffrer chaque programme** : coût attendu, écart-type, capital économisé, ruine, **coût par euro de capital économisé**.
> 4. **Éprouver la sensibilité** : à la queue (vue observée contre ajustée), au chargement, au seuil, à l'exposition future.
> 5. **Regarder la contrepartie** : notation, concentration, corrélation avec les sinistres.
> 6. **Lire les clauses** : priorité par rapport au capital (si la priorité dépasse ce que le capital peut absorber, la cédante est ruinée avant que la garantie ne joue), plafonds, réintégrations, définitions.
> 7. **Réévaluer chaque année** : l'exposition croît, les prix de marché varient, les modèles vieillissent (section 3.4 pour la validation de ces modèles).

> ✅ **À retenir.** Un programme de réassurance se juge sur **quatre axes** : coût, volatilité, capital, contrainte. Au seul coût du capital, les tranches basses se paient rarement ; la réassurance vaut par la **contrainte** qu'elle permet de tenir. Les données courtes **sous-estiment la queue** : la valeur de la protection catastrophe est plus grande que ne le disent les observations. Un réassureur est une **contrepartie** (surtout si son défaut est corrélé aux sinistres), et un plafond annuel bas retire à la couverture ce qu'il retire au prix.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.9 et 6.10, exercices 6.9 à 6.12.


## Bilan du chapitre 6

Vous savez maintenant :

- **expliquer** pourquoi une cédante réassure : non pour réduire son coût moyen, mais pour **stabiliser** son résultat, gagner de la **capacité** et **économiser du capital** ; et pourquoi la variance de la charge annuelle vient des gros sinistres, que la mutualisation ne diminue pas (17,1 % de coefficient de variation brut, 11,7 % une fois les sinistres plafonnés à 500 000 €) ;
- **distinguer** les traités **proportionnels** (quote-part, excédent de plénitude : mêmes proportions de primes et de sinistres) des traités **non proportionnels** (excédent de sinistre « portée xs priorité », par événement, stop-loss), calculer à la main ce que chacun cède sur huit sinistres (1 207,5, 2 560 et 1 000 sur 4 025), et lire les **réintégrations**, le **plafond annuel**, le **taux de prime** et le **ROL** ;
- **estimer** la prime pure d'une tranche par le *burning cost* (à **ajuster de l'exposition et de l'inflation**), par une loi de queue **GPD** (avec sa formule fermée) et par l'**exposition** (courbe $G(d)$) ;
- **mesurer l'incertitude** par le bootstrap par années, et savoir que l'erreur typique d'un tarif à quinze ans d'historique est de 8 %, 16 % et 31 % pour trois tranches de plus en plus hautes ;
- **traiter** les catastrophes avec peu de données (une loi de Pareto ajustée sur 17 événements, des tranches dont l'espérance est incertaine à un facteur deux), et passer de la prime pure à la **prime technique** (écart-type, coût du capital) ;
- **comparer** des programmes sur quatre axes (coût, volatilité, capital, ruine) par le **coût d'un euro de capital économisé**, évaluer l'effet d'une tour de catastrophe selon la vue que l'on a de la queue, et chiffrer le **risque de contrepartie** et l'**épuisement** d'une garantie.

Le chapitre a mis des chiffres sur des idées souvent qualitatives.

| Ce que l'on a vu | Résultat mesuré |
|---|---|
| *Burning cost* brut contre ajusté de l'exposition | sous-estimation de 29 à 45 % sans ajustement |
| Indexation de 4 % par habitude, alors que la sévérité est stable | tranches surestimées de 46 à 86 % |
| GPD sur le seuil de 1 M€ | $\hat\xi=-0,15$ (vérité 0,55) : seuil trop haut, trop peu de points |
| Bootstrap sur la tranche 2 M€ xs 2 M€ | intervalle à 95 % de 0,56 à 1,54 M€ (vérité 1,42) |
| Catastrophes : $\hat\alpha$ sur 17 événements | 1,33 contre 1,11 en vérité |
| Coût par euro de capital économisé | stop-loss 0,008 ; quote-part 0,14 ; excédents de sinistre de 0,27 à 0,42 |
| Défaut du réassureur lié aux gros sinistres | probabilité de ruine multipliée par 3,2 |

Le fil conducteur du chapitre tient en une phrase : **le prix d'une protection est une estimation incertaine d'un risque rare, et sa valeur dépend de ce qui contraint la cédante**. L'incertitude du tarif est de l'ordre de grandeur du chargement que l'on négocie ; les données courtes sous-estiment la queue ; la couverture n'est jamais plus solide que le contrat et que le réassureur.

> ⚠️ **Rappel d'honnêteté.** Les sinistres et les catastrophes sont **simulés** : nous avons pu comparer les estimations à la vérité, ce que personne ne peut faire en pratique. Les chargements, le coût du capital (8 %), la structure de frais (25 %) et les prix des programmes sont des **hypothèses d'exemple**, pas des conditions de marché. Les modèles de catastrophe, la modélisation de la dépendance entre branches, et le traitement comptable et prudentiel de la réassurance dépassent ce chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.10 (répartir huit sinistres entre trois traités, coefficient de variation selon la rétention, *burning cost*, courbe d'exposition, GPD, bootstrap, tranche de catastrophe, prime de risque, comparaison de programmes, contrepartie et épuisement) et exercices 6.1 à 6.12.

Le chapitre 7 change de sujet : il relie ce que l'on **doit** (le passif d'un assureur) à ce que l'on **détient** (ses placements), avec la gestion actif-passif et la théorie du portefeuille.
