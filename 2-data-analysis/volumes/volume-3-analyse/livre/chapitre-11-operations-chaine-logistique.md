# Chapitre 11 : ➕ Analytique des opérations et de la chaîne logistique

> « Un client ne juge pas votre entrepôt : il juge le jour où le colis arrive. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il applique les outils des chapitres 1 et 2 (distributions, intervalles de confiance, comparaison de proportions) à des questions d'**opérations** : livrer à l'heure, ne pas manquer de stock, choisir des fournisseurs fiables.

La gérante de la boutique vous écrit un mardi, d'un ton un peu las : « *Plusieurs clients se plaignent de livraisons tardives, et de mon côté je tombe en rupture sur des produits qui se vendent bien. Je ne sais pas si le problème vient des transporteurs, de mes fournisseurs ou de ma façon de commander. Peux-tu regarder ?* »

C'est une question d'analyste, et elle a une particularité : **trois problèmes se cachent derrière une seule plainte**. Un colis en retard peut venir de la préparation (la boutique), du transport (le transporteur) ou d'une période de forte demande (décembre). Une rupture peut venir d'un fournisseur lent, d'un point de commande trop bas ou d'une demande qui a monté. Ces causes se confondent dans une moyenne, et c'est précisément le travail de l'analyste de les **séparer**.

Le chapitre suit la chaîne dans l'ordre où le client la vit, mais en sens inverse de la cause : d'abord ce que le client a vu (la livraison, section 11.1), ensuite ce que la boutique contrôle le plus (ses stocks, section 11.2), enfin ce qu'elle contrôle le moins (ses fournisseurs, section 11.3). Trois idées l'organisent. La première est qu'**un délai se décrit par sa distribution, pas par sa moyenne** : le client qui attend huit jours ne se console pas parce que la moyenne est de six. La deuxième est qu'un stock est un **compromis chiffrable** entre le service rendu et l'argent immobilisé : on peut mettre un prix sur chaque point de rupture évité. La troisième est qu'une comparaison entre fournisseurs ou entre transporteurs n'a de sens qu'avec son **incertitude** : sur quelques dizaines de commandes, tout le monde a l'air bon ou mauvais selon la semaine.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un cours de logistique : nous n'optimisons pas de tournées, ne dimensionnons pas d'entrepôt et ne modélisons pas de réseaux. Nous mesurons ce que les données de la boutique permettent de mesurer, avec des formules simples et une honnêteté sur leurs limites.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 11.1 | Les livraisons sont-elles tardives, et à cause de qui ? | Délais par étape, centiles plutôt que moyenne, comparaison de transporteurs avec intervalles, effet de décembre |
| 11.2 | Pourquoi des ruptures, et comment les réduire ? | Rotation et couverture, point de commande et stock de sécurité, quantité économique, compromis service/stock rejoué sur les données |
| 11.3 | Quels fournisseurs sont fiables ? | Délai promis contre réel, taux de service, carte de performance avec intervalles, impact sur les ruptures |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateur `build/donnees_a3.py`) : la boutique est fictive. Nous connaissons donc la **vérité programmée** et nous la révélerons à la fin de chaque étude, pour que vous voyiez ce que l'analyse retrouve et ce qu'elle manque.

- `livraisons.csv` : une ligne par commande envoyée (canaux Site et Réseaux, 2023 à 2025), avec le transporteur, les dates d'expédition et de livraison, le délai promis au client (six jours), un indicateur de retard et un indicateur de colis abîmé (section 11.1).
- `stock_quotidien.csv` : le niveau de stock, la demande et l'éventuelle rupture de **vingt produits**, **chaque jour de 2025**, avec le point de commande en vigueur (section 11.2).
- `reappro_fournisseur.csv` : **1 500 commandes d'achat** de 2023 à 2025, avec le fournisseur, le délai promis et le délai réel, la quantité commandée et la quantité reçue (section 11.3).
- `produits.csv`, `commandes.csv`, `retours.csv` : le prix et le coût des produits, les commandes et les retours, pour relier un retard à un coût (sections 11.1 et 11.2).

Le fichier des livraisons contient aussi des commandes en « retrait en magasin » : le client vient chercher son colis, et un transporteur figure pourtant dans le fichier (un transfert entre entrepôt et magasin, ou une saisie par défaut). Un retrait n'est pas une livraison au sens du client : nous les écartons dès le départ, et c'est notre premier choix d'analyste à documenter.


Dans le fichier brut, 1 373 des 19 420 lignes sont des retraits en magasin ; il reste **18 047 livraisons** à analyser.


## 11.1 Livraisons et niveau de service

La première question de la gérante est celle du client : *arrive-t-il à l'heure ?* Cette section décompose un délai de livraison en étapes, le décrit par sa distribution plutôt que par sa moyenne, compare les transporteurs en tenant compte de l'incertitude, démêle l'effet de décembre, puis chiffre ce que coûtent un colis abîmé et un retard. Elle se termine par la comparaison avec la vérité programmée.

### 11.1.1 Une livraison, trois étapes

Du clic du client à la porte, trois choses se passent : la boutique **prépare** la commande (de la commande à l'expédition), le transporteur **transporte** (de l'expédition à la livraison), et le tout forme le délai **total** que le client a vu. Chaque étape a un responsable différent, donc chaque étape doit se mesurer séparément : un délai total de six jours ne dit pas qui a perdu du temps.

Le fichier contient les trois dates ; il suffit de les soustraire. Les délais se comptent en **jours entiers** (le fichier ne donne pas l'heure), ce qui rend les centiles « en escalier » : nous y reviendrons.

```python
etapes = liv[["preparation", "transport", "total"]]
resume = etapes.describe(percentiles=[0.5, 0.9, 0.95]).loc[["mean", "50%", "90%", "95%", "max"]]
print(resume.round(2))
```
<!--sortie-->
```text
      preparation  transport  total
mean         1.61       4.13   5.74
50%          1.00       4.00   6.00
90%          3.00       6.00   8.00
95%          3.00       6.00   8.00
max          8.00      10.00  14.00
```


La préparation prend en moyenne 1,61 jour (médiane de 1 jour), le transport 4,13 jours (médiane de 4 jours) : le **transport représente environ 72 % du délai total**. Le total moyen est de 5,74 jours, la médiane de 6 jours, et les 10 % de livraisons les plus lentes prennent 8 jours ou plus. Le plus long délai observé est de 14 jours.

> 💡 **Intuition.** Quand on cherche l'étape qui coûte le plus de temps, on compare les **moyennes par étape** (c'est elles qui s'additionnent). Quand on cherche à savoir ce que vit le client, on regarde la **distribution du total**.

### 11.1.2 La moyenne, la médiane et les centiles

Un délai est une variable **asymétrique** : il est borné en bas (on ne livre pas en moins de deux jours) et peut s'étirer en haut (un colis perdu, un week-end, un transporteur débordé). Pour une telle variable, la moyenne cache la queue, qui est précisément ce dont se plaignent les clients. Le bon résumé est un petit jeu de **centiles** : la médiane (la moitié des clients attendent moins), le 90e centile (neuf clients sur dix attendent moins) et le 95e.

Mais le centile seul ne parle pas à la gérante, qui a **promis six jours**. La grandeur qui parle au client est le **taux de livraison à l'heure** : la part des commandes livrées dans le délai promis. Les logisticiens l'appellent parfois OTIF (*on time, in full* : à l'heure et complet) quand ils y ajoutent la complétude ; nous n'avons ici que l'heure.


Sur l'ensemble de la période, **72,8 % des commandes arrivent dans les six jours promis** et **27,2 % en retard**. Un détail éclaire la fragilité de la promesse : 25,8 % des commandes arrivent **le dernier jour permis**, et le moindre aléa les fait basculer dans les 27,2 % de retards. Une promesse fixée sur la médiane se rompt une fois sur quatre : c'est un choix, pas une fatalité.


![Répartition des délais totaux de livraison : les barres bleues respectent la promesse de six jours, les barres orange la dépassent.](figures/ch11-delais.png)

> ⚠️ **Piège.** Des délais en jours entiers donnent des centiles qui sautent (le 90e et le 95e centiles valent ici le même nombre). Ne comparez pas des centiles de deux périodes à un jour près sans regarder l'histogramme.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.1, exercices 11.1 et 11.2.

### 11.1.3 Qui est en retard ? Comparer les transporteurs

Trois transporteurs se partagent les envois. La question de la gérante devient : *leur taux de retard diffère-t-il vraiment, ou est-ce le hasard ?* La réponse passe par ce que vous avez appris au chapitre 1 : un taux calculé sur un échantillon est entouré d'une **erreur d'échantillonnage**, et on la mesure par un intervalle de confiance. Pour une proportion, l'intervalle de **Wilson** est plus fiable que la formule de base quand la proportion est proche de 0 ou de 1 ; la fonction `wilson` de `build/outils_ch11.py` le calcule.

```python
rows = []
for nom, g in liv.groupby("transporteur"):
    p, bas, haut = O.wilson(g["retard"].sum(), len(g))
    rows.append((nom, len(g), round(p * 100, 1), round(bas * 100, 1), round(haut * 100, 1)))
print(pd.DataFrame(rows, columns=["transporteur", "envois", "retard %", "borne basse", "borne haute"]).to_string(index=False))
```
<!--sortie-->
```text
  transporteur  envois  retard %  borne basse  borne haute
Transporteur A    8107      16.4         15.6         17.2
Transporteur B    6444      27.3         26.2         28.4
Transporteur C    3496      51.9         50.3         53.6
```


Le transporteur A est en retard sur **16,4 %** de ses 8 107 envois (intervalle de 15,6 à 17,2 %), le B sur **27,3 %** (26,2 à 28,4 %) et le C sur **51,9 %** (50,3 à 53,6 %). Les intervalles **ne se recouvrent pas** : l'écart n'est pas un accident d'échantillonnage. Le test classique de comparaison de deux proportions (celui de la section 2.1) confirme pour A contre B : la statistique $z$ vaut 16,0, très loin des valeurs que le hasard produit (une valeur de 2 suffit à rejeter l'égalité). Le transporteur C, qui assure 19 % des envois, est en retard **une fois sur deux**.

Un troisième facteur se glisse dans les données : le **mode de livraison**. Le point relais s'ajoute au trajet (le colis attend le client), et l'on s'attend à plus de retards qu'à domicile.


Les envois à domicile sont en retard dans 20,6 % des cas, ceux en point relais dans **36,9 %**. Faut-il craindre que la différence entre transporteurs vienne de leur répartition entre domicile et relais ? Non : le point relais pèse 41 % des envois du transporteur A et 40 % de ceux du C, pratiquement la même chose. Quand deux facteurs sont **répartis de la même façon** dans les groupes comparés, la comparaison simple est fiable ; c'est quand leur répartition diffère qu'il faut stratifier, comme dans la sous-section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.2, exercice 11.3.

### 11.1.4 Décembre : stratifier avant de conclure

Le taux de retard n'est pas stable dans l'année. Une courbe par mois le montre immédiatement : le niveau de base est proche de 22 %, et **décembre explose**.


![Part des commandes livrées en retard selon le mois de commande : environ un cinquième toute l'année, plus de la moitié en décembre.](figures/ch11-retard-mois.png)

En décembre, **56,7 %** des commandes sont en retard, contre 22,1 % le reste de l'année. Les deux étapes se dégradent : la préparation passe de 1,54 à 2,04 jour(s) en moyenne, le transport de 4,01 à 4,80 jours. Les commandes de décembre ne représentent que 14,7 % des envois, mais elles pèsent beaucoup sur le taux global.

La question pratique est : *le classement des transporteurs tient-il en décembre et hors décembre ?* C'est la **stratification** : on calcule le même indicateur dans des sous-groupes où le facteur gênant est constant, puis on compare.

```python
strate = liv.assign(periode=np.where(liv["mois"] == 12, "décembre", "autres mois"))
print((strate.pivot_table(index="transporteur", columns="periode", values="retard", aggfunc="mean") * 100).round(1))
```
<!--sortie-->
```text
periode         autres mois  décembre
transporteur                         
Transporteur A         12.1      41.0
Transporteur B         21.9      59.9
Transporteur C         45.7      87.0
```


Hors décembre, les taux sont de 12,1 % (A), 21,9 % (B) et 45,7 % (C) ; en décembre, de 41,0 %, 59,9 % et 87,0 %. Le **classement est le même** dans les deux strates (A, puis B, puis C), et l'écart entre transporteurs ne vient donc pas de leur répartition dans l'année : leur part mensuelle ne varie, pour chacun, que de 4,0 points d'un mois à l'autre. En revanche, **décembre aggrave tout le monde** : même le meilleur transporteur voit son taux de retard multiplié par plus de trois.

> 🧪 **Remarque.** Ici la stratification confirme la comparaison simple, ce qui n'arrive pas toujours. Si le transporteur C avait assuré la moitié des envois de décembre et presque aucun le reste de l'année, sa mauvaise note aurait été en partie celle de décembre : un classique « paradoxe de Simpson » (volume I, section 1.1). Calculer par strate est le **réflexe de sécurité**, même quand il ne change pas la conclusion.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.2, exercice 11.4.

### 11.1.5 Colis abîmés et coût d'un retard

Un colis abîmé est un autre échec de service, plus rare. Même méthode : taux par transporteur, avec intervalle.


Le transporteur A abîme 0,9 % de ses colis (intervalle de 0,7 à 1,1 %), le B 1,4 % et le C **4,2 %** (3,6 à 4,9 %) : quatre à cinq fois plus que le meilleur. En chiffres bruts : le transporteur C a abîmé 147 colis ; au taux du transporteur A, il en aurait abîmé environ 116 de moins. Si l'on suppose qu'un colis abîmé coûte au moins la valeur d'un panier moyen (100 € ici, remplacement ou remboursement), l'excédent de casse du transporteur C représente environ **11 616 €** sur trois ans, sans compter l'insatisfaction.

Et le **retard** ? Le chiffrer est plus délicat, parce que le coût direct n'est pas visible dans les livraisons. Un réflexe d'analyste consiste à chercher le signal dans les **retours** : si les clients en retard renvoient plus, c'est un coût mesurable ; s'ils déclarent renvoyer « pour livraison tardive », c'est un indice. Le fichier des retours contient un motif « Livraison tardive » : voyons ce qu'il vaut.


Parmi les commandes livrées à l'heure, 18,2 % donnent lieu à un retour ; parmi les commandes livrées en retard, 18,0 %. **Le retard ne fait pas renvoyer davantage.** Le motif « Livraison tardive » existe pourtant : 605 retours (soit 12,1 % des retours) pour 26 941 € remboursés sur trois ans. Mais, parmi les retours de ce type que l'on peut relier à une livraison en ligne (424), **73 % concernent une commande livrée à l'heure** : le motif déclaré ne correspond pas au retard réel.

> ⚠️ **Piège.** Un motif de retour est une **déclaration**, pas un constat. Il peut cacher un autre motif (on invoque la livraison pour ne pas dire « changement d'avis »), refléter une mauvaise saisie, ou relever d'une perception (« six jours, c'est long »). Avant de chiffrer le « coût du retard » avec les motifs, comparez-les à la réalité mesurée, comme ici. Le seul coût du retard que ces données **établissent** est donc nul en remboursements : le coût réel est ailleurs (réputation, réachat), et il se mesure avec d'autres données (enquête de satisfaction, taux de réachat).

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.3, exercice 11.5.

### 11.1.6 Ce que la vérité programmée dit

Les données ont été fabriquées avec des paramètres connus. Voici ce que notre analyse retrouve.


| Quantité | Vérité programmée | Observé |
|---|---|---|
| Transport du B par rapport au A | + 0,6 jour | + 0,62 jour |
| Transport du C par rapport au A | + 1,4 jour | + 1,45 jour |
| Point relais par rapport au domicile | + 0,8 jour | + 0,77 jour |
| Colis abîmés (A, B, C) | 1,0 %, 1,4 %, 3,5 % | 0,9 %, 1,4 %, 4,2 % |
| Décembre : préparation, transport | + 0,5 jour, + 0,8 jour | + 0,50 jour, + 0,79 jour |

Les écarts de délai sont retrouvés à quelques centièmes de jour près. Le taux de colis abîmés du transporteur C (4,2 %) est un peu supérieur au taux programmé (3,5 %), mais l'intervalle de 3,6 à 4,9 % n'exclut la valeur programmée que de justesse : sur un seul échantillon de 3 496 envois, un écart de cette taille se produit environ une fois sur vingt (c'est la définition d'un intervalle à 95 %). **Un taux de casse se connaît à quelques dixièmes de point près, pas davantage**.


> ✅ **À retenir.**
> - Un délai se mesure **par étape** (préparation, transport) et se résume par une **médiane et des centiles**, jamais par la seule moyenne.
> - Le **taux de livraison à l'heure** est l'indicateur du client : il dépend de la promesse choisie.
> - Une comparaison de taux entre transporteurs s'accompagne d'**intervalles de confiance** ; une **stratification** (par mois, par mode) vérifie qu'elle ne vient pas d'un autre facteur.
> - Un **motif déclaré** n'est pas une mesure : on le confronte aux faits avant d'en tirer un coût.


## 11.2 Stocks : rotation, ruptures, point de commande

Cette section traite de ce que la boutique contrôle le plus directement : combien elle garde en stock et quand elle commande. Elle mesure d'abord la **rotation** et la **couverture**, puis les **ruptures** et leur coût, établit la règle du **point de commande** avec son **stock de sécurité**, **rejoue** l'année avec une autre règle pour chiffrer le compromis entre service et argent immobilisé, et termine par la **quantité économique de commande**, dont elle montre aussi les limites.

### 11.2.1 Rotation et couverture

Un stock a deux visages. Pour le gérant, c'est de l'argent immobilisé ; pour le client, c'est la garantie de trouver le produit. Deux indicateurs les relient. La **couverture** est le nombre de jours de vente que le stock permet de couvrir :

$$\text{couverture (jours)}=\frac{\text{stock moyen}}{\text{demande moyenne par jour}}.$$

La **rotation** est son inverse annualisé : combien de fois par an le stock « se renouvelle » :

$$\text{rotation}=\frac{\text{ventes annuelles}}{\text{stock moyen}}\approx\frac{365}{\text{couverture}}.$$

Un exemple à la main : un produit se vend 1,5 unité par jour et la boutique en garde en moyenne 24. La couverture est de 24 / 1,5 = 16 jours, la rotation de 365 / 16 ≈ 22,8 fois par an. Plus la couverture est courte, moins on immobilise d'argent, mais plus on est exposé à la rupture.

Le fichier `stock_quotidien.csv` donne, pour vingt produits qui se vendent bien, le stock de fin de journée et la demande de chaque jour de 2025.

```python
par_produit = stk.groupby("id_produit").agg(demande_j=("demande", "mean"), stock_moyen=("stock_fin_jour", "mean"), rupture=("rupture", "mean"))
par_produit["couverture_j"] = par_produit["stock_moyen"] / par_produit["demande_j"]
par_produit["rotation"] = 365 / par_produit["couverture_j"]
print(par_produit.round(2).head(4))
```
<!--sortie-->
```text
            demande_j  stock_moyen  rupture  couverture_j  rotation
id_produit                                                         
1                1.63        25.86     0.08         15.84     23.04
2                1.41        22.87     0.05         16.21     22.52
3                1.55        24.70     0.08         15.96     22.88
4                1.31        22.34     0.05         17.09     21.35
```


Sur ces vingt produits, la demande moyenne est de 1,54 unité par jour et par produit. La couverture va de 15,1 à 17,3 jours, avec une moyenne de **16,1 jours** (rotation d'environ 22,7 fois par an). Calculée sur l'ensemble des unités (stock total divisé par demande totale), la couverture est de 16,1 jours.

> ⚠️ **Piège.** Cette rotation est celle de vingt **produits phares**, nettement plus élevée que celle de l'assortiment complet, où des produits dorment longtemps. On ne la compare pas à une rotation moyenne de secteur (voir la section 8.2 sur le benchmarking) sans comparer des périmètres identiques.

### 11.2.2 Les ruptures

Une **rupture** est une journée où la demande n'a pas pu être entièrement servie. Le fichier la signale par un indicateur ; sa moyenne est le **taux de rupture** (la part des jours produit en rupture).


**7,4 % des jours produit sont en rupture**, de 4,7 % à 10,4 % selon le produit : le problème n'est pas limité à un produit mal géré, il est **général**. Les ruptures arrivent par **épisodes** : 186 épisodes sur l'année pour 537 jours en rupture, soit 2,9 jour(s) par épisode en moyenne (38 % des épisodes ne durent qu'un jour, le plus long dure 15 jours). Un épisode est le signe qu'une commande à un fournisseur est arrivée trop tard.

**Combien coûte une rupture ?** Le fichier ne dit pas combien d'unités ont été **perdues** : un jour de rupture, on sait que la demande n'a pas été servie en entier, pas de combien. On encadre donc la perte par deux bornes. Au minimum, **une unité** par jour de rupture ; au maximum, **toute la demande du jour** (si le stock était déjà à zéro depuis le matin). On valorise chaque unité perdue par sa **marge unitaire hors taxe** (prix de vente hors taxe moins coût d'achat).

```python
marge_u = (prod.set_index("id_produit")["prix_vente"] / 1.2 - prod.set_index("id_produit")["cout_achat"])
stk["marge_u"] = stk["id_produit"].map(marge_u)
rupt = stk[stk["rupture"] == 1]
borne_basse = (rupt["marge_u"] * 1).sum()
borne_haute = (rupt["marge_u"] * rupt["demande"]).sum()
print(round(borne_basse), round(borne_haute))
```
<!--sortie-->
```text
5723 17333
```


La marge unitaire moyenne de ces produits est de 10,4 € hors taxe. La perte de marge due aux ruptures est donc comprise entre **5 723 €** et **17 333 €** pour l'année 2025, soit au plus 15,0 % de la marge que ces vingt produits ont produite (115 874 €). La fourchette est large, et c'est normal : **elle dit honnêtement ce que le fichier ne sait pas**. On ne présente pas à la gérante un chiffre unique « précis » qui cacherait ce manque de mesure ; on lui propose plutôt de **mesurer** les ventes perdues (par exemple en notant la demande non servie à la caisse et sur le site).

![Part des jours en rupture par produit : presque tous dépassent l'objectif de 5 % fixé pour l'illustration.](figures/ch11-ruptures.png)

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.4, exercice 11.6.

### 11.2.3 Le point de commande et le stock de sécurité

Pourquoi les ruptures ? Pour le comprendre, il faut regarder la **règle** qui déclenche les commandes. Beaucoup de petites enseignes utilisent un **point de commande** : dès que le stock descend au niveau $R$, on commande une quantité $Q$. Il reste à choisir $R$. Le bon raisonnement est celui-ci : entre le moment où l'on commande et celui où la marchandise arrive, les clients continuent d'acheter. Le point de commande doit donc couvrir **la demande pendant le délai de réapprovisionnement**, plus une marge pour les aléas, le **stock de sécurité** :

$$R=\underbrace{\bar d\,\bar L}_{\text{demande attendue pendant le délai}}+\underbrace{z\,\sigma_{DL}}_{\text{stock de sécurité}},\qquad \sigma_{DL}=\sqrt{\bar L\,\sigma_d^{2}+\bar d^{2}\,\sigma_L^{2}}.$$

Ici $\bar d$ et $\sigma_d$ sont la moyenne et l'écart-type de la demande **journalière**, $\bar L$ et $\sigma_L$ la moyenne et l'écart-type du **délai** (en jours), et $z$ le coefficient du niveau de service souhaité (1,645 pour 95 % des cycles sans rupture). Le terme sous la racine additionne deux sources d'incertitude : la demande qui varie d'un jour à l'autre pendant les $L$ jours, et le délai lui-même qui varie, ce qui décale toute la consommation.

> 📐 **D'où vient la formule ?** Pendant un délai de $L$ jours, la demande totale est la somme de $L$ demandes journalières indépendantes de variance $\sigma_d^2$ : sa variance vaut $L\,\sigma_d^2$ si $L$ est connu. Si $L$ est lui-même aléatoire, la loi de la variance totale ajoute le terme $\bar d^{\,2}\sigma_L^{2}$ (la variance du délai, multipliée par le carré de la demande moyenne). Le stock de sécurité est alors le quantile correspondant à $z$ de cette demande-pendant-le-délai, supposée à peu près normale.

Un exemple à la main : $\bar d=1{,}5$, $\sigma_d=1{,}7$, $\bar L=11$ jours, $\sigma_L=3{,}7$ jours. La demande attendue pendant le délai est de $1{,}5\times 11=16{,}5$ unités. L'écart-type vaut $\sqrt{11\times 1{,}7^2+1{,}5^2\times 3{,}7^2}=\sqrt{31{,}8+30{,}8}\approx 7{,}9$. Pour 95 % de service, le stock de sécurité est $1{,}645\times 7{,}9\approx 13$, et $R\approx 30$ unités. **La variabilité du délai pèse autant que celle de la demande** : c'est pourquoi un fournisseur peu fiable (section 11.3) coûte cher en stock.

Reste à estimer ces quantités. La demande se lit dans le fichier. Le délai de réapprovisionnement, lui, n'est pas dans `stock_quotidien.csv`, mais on peut le **reconstituer** : une arrivée de marchandise se voit comme une hausse brutale du stock, et la commande a été déclenchée le jour où le stock a franchi le point de commande. Le nombre de jours entre les deux est le délai observé.

```python
delais = O.delais_reconstitues(stk)
dstats = stk.groupby("id_produit")["demande"].agg(["mean", "std"])
d_moy, d_std, L_moy, L_std = dstats["mean"].mean(), dstats["std"].mean(), delais.mean(), delais.std(ddof=1)
print(len(delais), round(L_moy, 1), round(L_std, 1), round(d_moy, 2), round(d_std, 2))
```
<!--sortie-->
```text
186 11.1 3.7 1.54 1.68
```


Sur 186 réapprovisionnements reconstitués, le délai moyen est de **11,1 jours** avec un écart-type de **3,7 jours** : 89 % des délais valent exactement 7, 10 ou 14 jours (les délais habituels des fournisseurs) et le reste forme une **queue de retards** allant jusqu'à 23 jours. La demande journalière moyenne est de 1,54 unité, avec un écart-type de 1,68 : plus grand que la moyenne, parce qu'un jour peut compter une commande de plusieurs unités.

![Distribution des délais de réapprovisionnement reconstitués à partir des hausses de stock : trois valeurs habituelles et des retards.](figures/ch11-delais-reappro.png)

```python
z = 1.645
sigma_dl = np.sqrt(L_moy * dstats["std"] ** 2 + dstats["mean"] ** 2 * L_std ** 2)
rop_formule = np.ceil(dstats["mean"] * L_moy + z * sigma_dl)
rop_actuel = stk.groupby("id_produit")["point_de_commande"].first()
print(round(rop_actuel.mean(), 1), round(rop_formule.mean(), 1))
```
<!--sortie-->
```text
13.3 30.6
```


Le point de commande **actuellement appliqué** est en moyenne de 13,3 unités, soit environ **8,6 jours de demande**. Or le délai moyen est de 11,1 jours : la boutique déclenche ses commandes **trop tard, avant même de parler de variabilité**. Le stock de sécurité de la formule serait de 13,1 unités en moyenne (pour 17,1 unités de demande attendue pendant le délai), et le point de commande recommandé de **30,6 unités**, plus du double de la règle actuelle. Part des délais supérieurs à 9 jours (la couverture offerte par la règle actuelle) : 71 %. C'est une explication directe des ruptures.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.4, exercice 11.7.

### 11.2.4 Rejouer l'histoire : le compromis entre service et stock

Une formule dit ce qu'il faudrait faire ; l'analyste doit aussi dire **ce que cela coûterait**. On peut le faire en **rejouant** l'année 2025 : on reprend la demande réelle de chaque produit jour par jour, on applique une règle de commande, avec des délais tirés dans la distribution observée, et l'on mesure le taux de rupture et le stock moyen obtenus. La fonction `rejouer` de `build/outils_ch11.py` le fait ; la quantité commandée est celle de la boutique (environ 30 jours de demande).

```python
Q = {p: int(dstats.loc[p, "mean"] * 30) + 5 for p in dstats.index}
actuel = O.rejouer(stk, rop_actuel.to_dict(), Q, delais)
propose = O.rejouer(stk, rop_formule.to_dict(), Q, delais)
print([round(float(x), 3) for x in actuel], [round(float(x), 3) for x in propose])
```
<!--sortie-->
```text
[0.07, 16.147, 9.857] [0.013, 26.032, 11.012]
```


Premier contrôle : **le modèle reproduit-il la réalité ?** Avec la règle actuelle, le rejeu donne 7,0 % de jours en rupture, contre 7,4 % observé : un écart de 0,3 point. On peut faire confiance au rejeu pour comparer des règles. Avec le point de commande de la formule, le taux de rupture tombe à **1,3 %** (objectif visé : environ 5 %, et la formule vise un service de 95 % **par cycle**, donc nettement moins de jours en rupture). Le prix à payer est une couverture qui passe de 16,1 à **26,0 jours** de demande : **61 % de stock en plus**.

On peut parcourir tout le compromis en multipliant le point de commande actuel par un coefficient, de 0,5 à 2.


![Compromis entre le stock moyen et le taux de rupture, rejoué sur 2025 : la courbe descend quand on augmente le point de commande ; les deux règles comparées sont marquées.](figures/ch11-compromis.png)

La courbe a la forme habituelle : **les premiers jours de stock ajoutés évitent beaucoup de ruptures, les derniers presque aucune**. Doubler le point de commande actuel amène le taux de rupture à 1,9 % pour une couverture de 23,4 jours. Choisir un niveau sur cette courbe n'est pas une question statistique, c'est une **décision de gestion** : combien de jours de stock la gérante accepte-t-elle de financer pour gagner un point de service ?

Pour la lui présenter, il faut traduire en euros. Supposons que l'argent immobilisé coûte 20 % par an (financement, assurance, vieillissement) : c'est une **hypothèse**, que la gérante doit confirmer.

```python
cout_u = prod.set_index("id_produit")["cout_achat"]
stock_en_plus_u = (dstats["mean"] * (propose[1] - actuel[1])).sum()         # unités immobilisées en plus
valeur_en_plus = (dstats["mean"] * (propose[1] - actuel[1]) * cout_u.loc[dstats.index]).sum()
print(round(stock_en_plus_u), round(valeur_en_plus), round(0.20 * valeur_en_plus))
```
<!--sortie-->
```text
304 4937 987
```


Le surplus de stock représente environ **304 unités**, soit 4 937 € au prix d'achat, et un coût de détention de **987 € par an**. En face, la marge sauvée en évitant les ruptures est comprise (selon les deux bornes de la section 11.2.2) entre **4 641 €** et **14 055 €** par an. Même avec la borne basse, la marge sauvée vaut **4,7 fois** le coût de détention : la décision tient **quelle que soit la vraie valeur des ventes perdues**, ce qui est précisément ce que l'on cherche d'une recommandation faite avec une mesure incomplète. Mesurer les ventes perdues, plutôt que de les encadrer, reste la première amélioration à apporter aux données : elle permettrait de choisir le **niveau** de la règle, pas son principe.

> ⚠️ **Piège.** Un rejeu est un **modèle** : la demande est supposée inchangée quand on change la politique, ce qui est raisonnable ici, mais on suppose aussi que les ruptures passées n'ont pas « caché » de demande. Il ne remplace pas un test en conditions réelles sur quelques produits.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.5, exercice 11.7.

### 11.2.5 La quantité économique de commande

Reste la seconde moitié de la règle : **combien** commander ? Commander souvent coûte des frais fixes (préparation de la commande, transport) ; commander beaucoup immobilise du stock. La **quantité économique de commande** (formule de Wilson) minimise la somme des deux coûts :

$$Q^{*}=\sqrt{\frac{2\,D\,S}{H}},\qquad \text{coût annuel}(Q)=\frac{D}{Q}\,S+\frac{Q}{2}\,H,$$

où $D$ est la demande annuelle, $S$ le coût d'une commande et $H$ le coût de détention d'une unité pendant un an.

> 📐 **D'où vient la formule ?** Le premier terme est le nombre de commandes par an multiplié par leur coût fixe, il décroît avec $Q$ ; le second est le stock moyen ($Q/2$, car le stock descend de $Q$ à 0) multiplié par le coût de détention, il croît avec $Q$. La somme est minimale quand les deux termes sont égaux, c'est-à-dire pour $Q^{*}=\sqrt{2DS/H}$, et le coût minimal vaut alors $\sqrt{2DSH}$.

Un exemple à la main : un produit se vend $D=560$ unités par an, coûte 12 € à l'achat ; on suppose 25 € de frais par commande et 20 % de coût de détention, donc $H=0{,}20\times 12=2{,}40$ € par unité et par an. Alors $Q^{*}=\sqrt{2\times 560\times 25/2{,}40}\approx 108$ unités, soit 70 jours de demande. Passer à 51 unités (la pratique actuelle, environ 30 jours de demande) ne coûte pas beaucoup plus : le coût vaut $560/51\times 25+51/2\times 2{,}4\approx 335$ € contre $560/108\times 25+108/2\times 2{,}4\approx 259$ € à l'optimum.


Sur nos vingt produits, la quantité économique moyenne est de 119 unités (79 jours de demande), contre 51 unités (33 jours) en pratique. Le coût annuel d'approvisionnement et de détention serait de 5 651 € à l'optimum contre 7 176 €, soit une économie de **1 525 €** (21 %). Deux enseignements : le gain est **modeste** à côté de celui qu'apporterait un meilleur point de commande, et le coût est **plat au voisinage** de l'optimum : une quantité 25 % trop grande ne coûte que 2,5 % de plus, 25 % trop petite 4,2 % ; il ne grimpe que loin de l'optimum (deux fois la quantité optimale : 25 % de plus, trois fois : 67 %). La précision du calcul compte donc peu, l'ordre de grandeur suffit.

> ⚠️ **Limites de la formule.** Elle suppose une demande **régulière**, des coûts $S$ et $H$ **connus** (en pratique, très incertains : le « 25 € » ci-dessus est une hypothèse), pas de remise de quantité, pas de contrainte de place ni de péremption, et un **délai connu**. Elle donne la taille de commande, pas son déclenchement ; et elle est muette sur ce qui compte le plus ici, la **fiabilité des fournisseurs** : c'est l'objet de la section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.5, exercice 11.8.

### 11.2.6 Ce que la vérité programmée dit

La politique de la boutique a été programmée ainsi : point de commande égal à **9 jours** de demande moyenne, quantité commandée de **30 jours** de demande plus 5 unités, délais de **7, 10 ou 14 jours** avec, dans 15 % des cas, un retard supplémentaire de 3 à 9 jours. Notre analyse retrouve ces paramètres sans les connaître : le point de commande de 8,6 jours est lu dans le fichier, les délais de 7, 10 et 14 jours sont reconstitués (89 % des cas), et leur moyenne de 11,1 jours est cohérente avec les 10,3 jours des trois délais de base plus l'effet des 15 % de retards (environ 11,2 jours en moyenne). Le rejeu retrouve le taux de rupture observé à 0,3 point près : c'est la meilleure preuve que le modèle est assez bon pour comparer des règles.

> ✅ **À retenir.**
> - **Couverture** = stock moyen / demande par jour ; **rotation** = 365 / couverture. Comparer des périmètres identiques.
> - Un **taux de rupture** se mesure sur la demande non servie ; quand on ne la connaît pas, on **encadre** la perte par deux bornes plutôt que d'inventer un chiffre.
> - **Point de commande** = demande pendant le délai + stock de sécurité ; la variabilité du **délai** pèse autant que celle de la demande.
> - Un **rejeu** de l'histoire chiffre le compromis service/stock ; il doit d'abord reproduire la réalité observée.
> - La **quantité économique** donne un ordre de grandeur de la taille de commande ; le coût est plat autour de l'optimum.


## 11.3 Fournisseurs : fiabilité et délais

Un stock bien réglé suppose que le fournisseur livre quand il l'a dit. Cette section mesure la **fiabilité** des huit fournisseurs de la boutique sur deux plans, le **délai** (promis contre réel) et la **quantité** (commandée contre reçue), les compare avec des intervalles de confiance, les résume dans une **carte de performance**, puis chiffre par simulation ce que coûte, en ruptures, un fournisseur peu fiable.

### 11.3.1 Promis contre réel : deux façons de mesurer un retard

Chaque commande d'achat porte un **délai promis** (7, 10, 14 ou 21 jours selon le produit) et un **délai réel**. L'**écart** est la différence : positif, le fournisseur est en retard ; négatif ou nul, il est à l'heure ou en avance. Mais comment compter les « retards » ? Un jour de retard n'a pas le même sens qu'une semaine. Deux conventions se complètent : le **taux de retard strict** (toute commande avec un écart positif) et le **taux de retard significatif**, avec une tolérance fixée **avant** de regarder les résultats, ici **3 jours ou plus**.

```python
rea["retard_3j"] = (rea["ecart_j"] >= 3).astype(int)
print(rea[["ecart_j"]].describe().loc[["mean", "50%", "max"]].round(2).T)
print("retard strict :", round(rea["en_retard"].mean() * 100, 1), "% | retard de 3 jours ou plus :", round(rea["retard_3j"].mean() * 100, 1), "%")
```
<!--sortie-->
```text
         mean  50%   max
ecart_j  1.34  0.0  18.0
retard strict : 41.2 % | retard de 3 jours ou plus : 18.1 %
```


Sur 1 500 commandes, l'écart moyen est de 1,34 jour (médiane de 0, maximum de 18) : 30,1 % des commandes arrivent le jour dit, 28,7 % en avance. Le retard strict touche 41,2 % des commandes, mais le retard de **3 jours ou plus** seulement 18,1 %. L'écart entre les deux nombres est un rappel : **la définition d'un retard est une décision**, à fixer avec les personnes qui commandent (trois jours de retard sur un produit courant, est-ce grave ?).

### 11.3.2 Reçu contre commandé : le taux de service

Un fournisseur peut être ponctuel et livrer moins que prévu. Le **taux de service quantitatif** est le rapport entre la quantité reçue et la quantité commandée (le complément de la quantité manquante) ; une commande est **complète** si l'on a reçu au moins 98 % de la quantité commandée (tolérance fixée à l'avance).


Pour l'ensemble des fournisseurs, le taux de service moyen est de **96,2 %** et 54,3 % des commandes sont reçues **complètes** (à 2 % près). Un chiffre global masque deux choses : l'écart entre fournisseurs et l'écart entre commandes. C'est ce que montre la carte de performance.

### 11.3.3 La carte de performance, avec ses intervalles

Pour chaque fournisseur, on calcule les trois mesures **et leur incertitude** : le taux de retard de 3 jours ou plus avec un intervalle de Wilson (section 11.1.3), l'écart moyen et le taux de service avec un intervalle de confiance de la moyenne (volume I, section 1.3.3).

```python
rows = []
for nom, g in rea.groupby("fournisseur"):
    p, bas, haut = O.wilson(g["retard_3j"].sum(), len(g))
    e = stats.t.interval(0.95, len(g) - 1, g["ecart_j"].mean(), stats.sem(g["ecart_j"]))
    s = stats.t.interval(0.95, len(g) - 1, g["taux_service"].mean(), stats.sem(g["taux_service"]))
    rows.append((nom[-1], len(g), p * 100, bas * 100, haut * 100, g["ecart_j"].mean(), e[0], e[1], g["taux_service"].mean() * 100, s[0] * 100, s[1] * 100))
carte = pd.DataFrame(rows, columns=["f", "n", "retard3", "r_bas", "r_haut", "ecart", "e_bas", "e_haut", "service", "s_bas", "s_haut"])
print(carte[["f", "n", "retard3", "ecart", "service"]].round(1).to_string(index=False))
```
<!--sortie-->
```text
f   n  retard3  ecart  service
A 174     14.4    0.7     98.1
B 170     12.4    1.1     97.9
C 191     13.6    1.1     97.9
D 200     15.0    1.1     97.9
E 205     45.9    3.9     85.1
F 188     15.4    1.3     98.1
G 190     10.5    0.5     97.9
H 182     14.3    0.9     98.0
```


![Carte de performance des huit fournisseurs avec intervalles de confiance à 95 % : retards de trois jours ou plus, écart moyen de délai et taux de service. Le fournisseur E se détache nettement.](figures/ch11-fournisseurs.png)

Le fournisseur **E** se détache sur les trois mesures : 45,9 % de retards de 3 jours ou plus (intervalle de 39,2 à 52,7 %), un écart moyen de 3,89 jours et un taux de service de 85,1 %. Les sept autres sont **groupés** : leurs taux de retard vont de 10,5 à 15,4 % et leurs taux de service de 97,9 à 98,1 %. Entre eux, les intervalles se chevauchent largement : avec 170 à 205 commandes chacun, **on ne peut pas dire** que le fournisseur G est meilleur que le A ou que le H est moins bon que le B. Un classement de huit fournisseurs par la valeur brute d'un indicateur invente des rangs que les données ne soutiennent pas.

> 🧪 **Remarque.** Le test de Student sur l'écart moyen (E contre les autres) est écrasant, mais il n'ajoute rien à la figure : quand les intervalles sont aussi séparés, l'analyste peut s'épargner le test et **montrer l'image**. Le test est utile pour les cas limites, comme l'éventuelle différence entre H et G.

### 11.3.4 Une note multicritère, et sa fragilité

La gérante demande « une note par fournisseur ». On peut la construire en combinant les critères avec des **pondérations**. Une méthode simple : ramener chaque critère entre 0 (pire fournisseur) et 1 (meilleur) puis calculer une moyenne pondérée, par exemple 40 % pour la ponctualité, 40 % pour la quantité, 20 % pour la régularité (écart-type du délai).

```python
reg = rea.groupby("fournisseur")["delai_reel_j"].std()
crit = pd.DataFrame({"ponctualite": -carte.set_index("f")["retard3"].values, "quantite": carte["service"].values, "regularite": -reg.values}, index=carte["f"])
norm = (crit - crit.min()) / (crit.max() - crit.min())
poids = {"A": [0.4, 0.4, 0.2], "B": [0.6, 0.2, 0.2], "C": [0.2, 0.6, 0.2], "D": [0.34, 0.33, 0.33]}
rangs = pd.DataFrame({k: (norm @ pd.Series(w, index=norm.columns)).rank(ascending=False).astype(int) for k, w in poids.items()})
print(rangs.T)
```
<!--sortie-->
```text
f  A  B  C  D  E  F  G  H
A  3  6  4  7  8  5  1  2
B  3  5  4  7  8  6  1  2
C  3  6  5  7  8  4  1  2
D  3  6  4  7  8  5  1  2
```


Le fournisseur E est **dernier (rang 8) quelles que soient les pondérations**. Pour les sept autres, les rangs bougent peu mais bougent : le fournisseur F, par exemple, va du **4e au 6e rang** selon les poids, soit 2 places d'écart, alors que ses intervalles chevauchent ceux de ses voisins. La note multicritère est donc utile pour **repérer les cas extrêmes** (E en dernier, G en tête), pas pour départager des fournisseurs voisins : c'est le même enseignement que pour les intervalles.

> ⚠️ **Piège.** Une note unique donne une impression de précision que les données n'ont pas. Si l'on doit publier un classement, on publie aussi la **sensibilité aux pondérations** et les intervalles : la gérante choisira les poids qui correspondent à ses priorités (ponctualité, complétude, régularité), pas l'analyste.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : application 11.6, exercices 11.9 et 11.10.

### 11.3.5 Ce que coûte un fournisseur peu fiable : un rejeu

Pour relier fournisseurs et ruptures, on réutilise le rejeu de la section 11.2.4, mais avec des délais tirés dans les **commandes d'achat de chaque fournisseur** (limitées aux produits à délai promis de 7, 10 ou 14 jours, comme ceux du fichier des stocks). On compare ce que donnerait un réapprovisionnement **entièrement** auprès de E ou entièrement auprès d'un fournisseur fiable comme G, avec la règle de commande actuelle puis avec la règle de la formule recalculée pour chaque fournisseur.

```python
def delais_fournisseur(f):
    g = rea[(rea["fournisseur"] == f) & rea["delai_promis_j"].isin([7, 10, 14])]
    return g["delai_reel_j"].values
Q = {p: int(dstats.loc[p, "mean"] * 30) + 5 for p in dstats.index}
res = {}
for f in ("Fournisseur E", "Fournisseur G"):
    dl = delais_fournisseur(f)
    rop_f = {p: int(np.ceil(dstats.loc[p, "mean"] * dl.mean() + 1.645 * np.sqrt(dl.mean() * dstats.loc[p, "std"] ** 2 + dstats.loc[p, "mean"] ** 2 * dl.std(ddof=1) ** 2))) for p in dstats.index}
    res[f] = (dl.mean(), dl.std(ddof=1), O.rejouer(stk, rop_actuel.to_dict(), Q, dl, n_rep=10), O.rejouer(stk, rop_f, Q, dl, n_rep=10))
for f, (m, s, a, b) in res.items():
    print(f, round(m, 1), round(s, 1), "| règle actuelle :", round(a[0] * 100, 1), "% rupture, couverture", round(a[1], 1), "| règle adaptée :", round(b[0] * 100, 1), "%, couverture", round(b[1], 1))
```
<!--sortie-->
```text
Fournisseur E 14.0 5.8 | règle actuelle : 10.9 % rupture, couverture 14.9 | règle adaptée : 1.7 %, couverture 28.8
Fournisseur G 11.2 4.0 | règle actuelle : 7.2 % rupture, couverture 16.1 | règle adaptée : 1.2 %, couverture 26.4
```


Avec la règle de commande actuelle, un approvisionnement chez G (délai moyen de 11,2 jours, écart-type de 4,0) donnerait 7,2 % de jours en rupture, un approvisionnement chez E (délai moyen de 14,0 jours, écart-type de 5,8) 10,9 %. Pour tenir un service raisonnable avec E, il faut **adapter la règle** : le stock moyen monte alors à 28,8 jours de demande (pour 1,7 % de ruptures), contre 26,4 jours avec G (1,2 % de ruptures). **Le fournisseur peu fiable coûte 9 % de stock en plus pour un service comparable** : c'est son vrai prix, celui qui ne figure pas sur la facture.

### 11.3.6 Pièges de la comparaison de fournisseurs

Quatre pièges guettent l'analyste.

**Les petits échantillons.** Huit fournisseurs, chacun 170 à 205 commandes : suffisant pour repérer E, pas pour classer les sept autres. Dès que l'on croise le fournisseur avec le produit, les cellules tombent à une ou deux commandes et plus rien n'est lisible.

**Le mélange de produits et de délais promis.** Un fournisseur qui livre des produits à 21 jours aura un écart en jours plus grand qu'un autre qui livre à 7 jours, sans être moins fiable. Quand les délais promis diffèrent, on compare l'**écart relatif** (écart divisé par le délai promis) ou l'on stratifie par délai promis.

**La sélection.** La gérante confie peut-être ses produits les plus difficiles à un fournisseur donné : sa performance reflète alors aussi la difficulté des produits, pas seulement son sérieux. Ici, l'affectation est aléatoire dans les données, ce qui n'est presque jamais le cas en réalité.

**Le temps.** Un fournisseur peut s'être dégradé (ou amélioré) en cours de période : une moyenne sur trois ans masque la tendance. Un graphique mensuel du taux de retard est un contrôle bon marché.

### 11.3.7 Ce que la vérité programmée dit

Les données ont été fabriquées avec des paramètres connus : pour le fournisseur E, une probabilité de retard supplémentaire de 45 % (de 3 à 14 jours) et un taux de service tiré entre 70 et 100 % (moyenne 85 %) ; pour tous les autres, 10 % de retard supplémentaire et un taux de service entre 96 et 100 % (moyenne 98 %).

| Quantité | Vérité programmée | Observé |
|---|---|---|
| Taux de service de E | environ 85 % | 85,1 % |
| Taux de service des autres fournisseurs | environ 98 % | de 97,9 à 98,1 % |
| Retards de 3 jours ou plus : E | beaucoup plus que les autres | 45,9 % |
| Retards de 3 jours ou plus : autres | environ le dixième des commandes et quelques retards de bruit | de 10,5 à 15,4 % |

L'analyse retrouve **le seul fournisseur réellement différent** et ne distingue pas les sept autres, ce qui est exactement conforme à la vérité : il n'y a rien à distinguer entre eux.

> ✅ **À retenir.**
> - Un **retard** se définit avec une tolérance fixée à l'avance ; on mesure aussi la **quantité** reçue.
> - Une **carte de performance** donne pour chaque fournisseur ses indicateurs **et leurs intervalles** : elle repère les cas extrêmes, pas les écarts de quelques points.
> - Une **note multicritère** dépend de ses pondérations ; on publie sa sensibilité.
> - Le **vrai coût** d'un fournisseur peu fiable est le stock supplémentaire qu'il impose pour un même service ; un **rejeu** le chiffre.


## Bilan du chapitre 11

Vous savez maintenant :

- **décomposer** un délai de livraison en étapes (préparation, transport), le **décrire** par sa médiane et ses centiles, et **mesurer** le taux de livraison à l'heure par rapport à la promesse faite au client ;
- **comparer** des transporteurs avec des **intervalles de confiance**, **stratifier** par mois et par mode de livraison pour vérifier qu'un écart ne vient pas d'ailleurs, et **chiffrer** la casse ;
- **confronter** un motif de retour déclaré à la réalité mesurée avant de lui prêter un coût ;
- **calculer** la couverture, la rotation et le taux de rupture, **encadrer** les ventes perdues quand on ne les mesure pas, et **établir** un point de commande avec son stock de sécurité à partir de la demande et du **délai** reconstitués ;
- **rejouer** l'histoire avec une autre règle de commande pour chiffrer le compromis entre service et stock, et **situer** la quantité économique de commande avec ses limites ;
- **évaluer** des fournisseurs sur le délai et la quantité, avec une carte de performance honnête sur son incertitude, une note multicritère dont on connaît la fragilité, et un rejeu qui traduit leur fiabilité en stock.

Le tableau ci-dessous résume ce que nous avons **mesuré** sur les données de la boutique.


| Question | Mesure |
|---|---|
| Livraisons à l'heure (promesse de 6 jours) | 72,8 % ; **16,4 %, 27,3 % et 51,9 %** de retard pour les transporteurs A, B et C |
| Effet de décembre | 56,7 % de retards contre 22,1 % le reste de l'année, pour tous les transporteurs |
| Colis abîmés (A, B, C) | 0,9 %, 1,4 %, 4,2 % |
| Le retard fait-il renvoyer ? | non : 18,0 % de retours après une livraison tardive, 18,2 % sinon |
| Jours en rupture | 7,4 % des jours produit ; perte de marge de 5 723 à 17 333 € |
| Point de commande | actuel : 13,3 unités ; recommandé : 30,6 unités |
| Compromis rejoué | ruptures de 7,0 % à 1,3 % pour 61 % de stock en plus |
| Fournisseur E | retards de 3 jours ou plus : 45,9 % ; taux de service : 85,1 % ; stock supplémentaire pour un service comparable : 9 % |

Le fil conducteur du chapitre tient en une phrase : **en opérations, la plainte unique du client recouvre plusieurs causes que seule une décomposition sépare, et chaque comparaison mérite son intervalle**. Le transport, décembre et le point relais jouent chacun leur rôle dans les retards ; la règle de commande, plus que le hasard, explique les ruptures ; un seul fournisseur sur huit est réellement en cause.

> 🧭 **En pratique : lire un tableau de bord d'opérations.**
> 1. Est-ce un **taux** (à l'heure, complet, en rupture) avec sa base et sa période ?
> 2. Les comparaisons ont-elles des **intervalles** ? Les écarts les dépassent-ils ?
> 3. A-t-on **stratifié** (mois, mode, produit) avant d'accuser un acteur ?
> 4. Les **définitions** (retard, rupture, complet) sont-elles écrites ?
> 5. Le chiffre en euros vient-il d'une **mesure**, d'une **fourchette** ou d'une **hypothèse** ?

Le chapitre 12 quitte les marchandises pour les **personnes** : effectifs, rémunération et départs, avec une question que les opérations ne posent pas, celle de ce que l'on a le **droit** de calculer.

> 📒 **Pour s'entraîner.** Cahier, chapitre 11 : applications 11.1 à 11.6 (délais et service, transporteurs et décembre, retours et coût, ruptures et point de commande, rejeu et quantité économique, fournisseurs) et exercices 11.1 à 11.10.
