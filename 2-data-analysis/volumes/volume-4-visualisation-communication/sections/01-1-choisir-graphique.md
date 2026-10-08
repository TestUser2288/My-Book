## 1.1 Choisir le bon graphique

Avant de dessiner quoi que ce soit, il faut savoir **ce que la lectrice cherche** : comparer, suivre une évolution, voir une répartition, repérer une relation, situer un écart. Cette section donne une méthode pour passer de la question au graphique, explique pourquoi certaines formes se lisent mieux que d'autres (c'est de la perception, pas du goût), montre les mêmes données dites de quatre façons, puis passe en revue les graphiques à connaître et ceux qu'il vaut mieux éviter.

### 1.1.1 On part de la question, pas du graphique

Un analyste débutant ouvre son outil, choisit « graphique » dans le menu, puis regarde ce que l'outil propose. Un analyste expérimenté fait l'inverse : il écrit d'abord, en une phrase, **la question à laquelle le graphique doit répondre**. Le type de graphique en découle presque toujours.

![Arbre de décision : à chaque question que l'on se pose sur les données correspond une famille de graphiques. Schéma dessiné avec matplotlib.](figures/ch01-arbre.png)

```python hide
O.fig_arbre()
```
<!--sortie-->
```text
figure : ch01-arbre.png
```

Lisons l'arbre avec trois questions de la gérante :

- « Quelles catégories pèsent le plus dans le chiffre d'affaires ? » C'est une **comparaison de quantités** entre catégories : des barres horizontales, triées.
- « Est-ce que les ventes remontent ? » C'est une **évolution dans le temps** : une courbe.
- « Est-ce que les jours de forte publicité sont aussi les jours de forte vente ? » C'est une **relation entre deux variables** : un nuage de points.

Deux graphiques ne répondent pas à la même question, même avec les mêmes données. La **première règle** de ce chapitre tient en une ligne : *si vous ne savez pas écrire la question, vous ne savez pas encore quel graphique faire*.

> 💡 **Intuition.** Le bon graphique est celui qui rend la **comparaison utile** immédiate. Si la question est « qui est le plus grand ? », le graphique doit placer les grandeurs côte à côte, sur une même ligne de base. Si la question est « comment cela évolue-t-il ? », il doit relier les points dans l'ordre du temps. Tout le reste est décoration.

Avant de continuer, une distinction qui évite beaucoup d'erreurs : **explorer** et **expliquer** ne demandent pas le même graphique. Pour explorer, vous en produisez vingt, rapides et laids, pour vous seul : c'est le travail du volume III. Pour expliquer, vous en choisissez **un**, que vous soignez, parce qu'une autre personne le lira sans vous. Ce chapitre traite de la seconde situation.

### 1.1.2 Ce que l'œil sait faire : la hiérarchie des encodages

Un graphique transforme des nombres en **marques visuelles** : des positions, des longueurs, des angles, des aires, des couleurs. Mais toutes les marques ne se valent pas : des expériences de psychologie de la perception, répétées depuis plusieurs décennies, montrent que nous comparons très **précisément** des positions le long d'une même échelle, assez bien des longueurs, moins bien des angles, mal des aires, et très mal des intensités de couleur.

![Les six chiffres d'affaires par catégorie encodés par la position, la longueur, l'angle, l'aire et l'intensité de la couleur : la même information devient de moins en moins facile à ranger. Schéma dessiné avec matplotlib à partir du chiffre d'affaires 2025 (données simulées).](figures/ch01-encodages.png)

```python hide
O.fig_encodages()
cat, part = F["cat"], F["part_cat"]
assert [round(v) for v in cat.values] == [354, 305, 259, 233, 118, 57]
assert [round(v, 1) for v in part.values] == [26.7, 23.0, 19.5, 17.6, 8.9, 4.3]
```
<!--sortie-->
```text
figure : ch01-encodages.png
```

Dans la figure, les six mêmes chiffres d'affaires par catégorie (de 354 k€ pour le jardin à 57 k€ pour la papeterie) sont montrés de cinq façons. Essayez de **ranger** les six catégories du plus grand au plus petit dans chaque panneau :

1. **Position** (points sur une échelle commune) : l'ordre se lit sans effort, et l'écart aussi.
2. **Longueur** (barres) : presque aussi précis, à condition que les barres partent du **même zéro**.
3. **Angle** (parts d'un camembert) : l'ordre des grandes parts se devine, celui des parts voisines devient incertain.
4. **Aire** (cercles) : on sait que « c'est plus grand », pas de combien.
5. **Couleur** (intensité) : on distingue clair et foncé, pas six niveaux.

Un petit calcul rend l'écart concret. Un camembert traduit 100 % en 360 degrés : la différence entre deux parts voisines se joue en quelques degrés.

```python
angle = F["part_cat"] * 3.6                    # 100 % = 360 degrés
print(angle.round(0).head(4).to_string())
print("écart Jardin - Maison :", round(angle.iloc[0] - angle.iloc[1]), "degrés")
```
<!--sortie-->
```text
categorie
Jardin        96.0
Maison        83.0
Décoration    70.0
Cuisine       63.0
écart Jardin - Maison : 13 degrés
```

Le jardin pèse 16 % de plus que la maison (354 contre 305 k€) ; sur le camembert, cela fait **13 degrés** d'écart entre deux angles de 96 et 83 degrés. Sur des barres, l'écart de 16 % est celui de deux longueurs, que l'œil mesure directement.

> ✅ **À retenir.** Quand on a le choix, on encode l'information importante par la **position** ou la **longueur**, jamais par l'aire ou la couleur seule. La couleur sert à **distinguer** (des catégories) ou à **mettre en valeur** (un élément), pas à **mesurer**.

Cette hiérarchie n'interdit rien : un camembert, une carte avec des cercles ou une carte thermique ont leur place. Elle indique **le prix à payer** : chaque fois que l'on quitte la position ou la longueur, on perd en précision, donc on doit compenser par des **étiquettes chiffrées** ou par un message simple.

### 1.1.3 Le même jeu de données, dit de quatre façons

Prenons un seul tableau : le chiffre d'affaires mensuel 2025 de chacun des trois canaux, soit trente-six nombres. Quatre graphiques raisonnables existent, et **chacun répond à une question différente**.

![Le chiffre d'affaires mensuel 2025 par canal, dit de quatre façons : barres groupées, courbes, aires empilées, carte thermique. Figure construite avec matplotlib (données simulées).](figures/ch01-quatre-facons.png)

```python hide
O.fig_quatre_facons()
cd, ca = F["canal_dec"], F["canal_an"]
assert [round(v) for v in (cd["Site"], cd["Boutique"], cd["Réseaux"])] == [90, 73, 20] and round(cd.sum()) == 184
assert [round(ca[k] / ca.sum() * 100, 1) for k in ("Site", "Boutique", "Réseaux")] == [46.6, 42.3, 11.0]
assert round(ca.sum()) == 1325
pc = O.ca_mensuel(2025, "canal")
assert list(pc.index[pc["Site"] < pc["Boutique"]]) == [4, 8]
assert round(F["cat"]["Jardin"] / F["cat"]["Maison"], 2) == 1.16 and round(F["part_cat"]["Décoration"] - F["part_cat"]["Cuisine"], 1) == 1.9
assert round(F["part_cat"]["Bien-être"] / F["part_cat"]["Papeterie"], 1) == 2.1
```
<!--sortie-->
```text
figure : ch01-quatre-facons.png
```

- **Barres groupées** : « *quel canal est le plus fort, mois par mois ?* » On compare des hauteurs voisines. En décembre, le site vend 90 k€, la boutique 73 k€ et les réseaux 20 k€. Trente-six barres, c'est beaucoup : on lit bien un mois, mal une tendance.
- **Courbes** : « *comment chaque canal évolue-t-il ?* » On suit une forme dans le temps ; le site dépasse la boutique presque tous les mois (sauf en avril et en août), et sa baisse d'août est plus marquée. Les courbes sont **étiquetées directement** (le nom au bout du trait) : pas besoin de légende.
- **Aires empilées** : « *quel est le total, et de quoi se compose-t-il ?* » Le total de décembre (184 k€) se lit d'un coup. En revanche, seule la couche du bas (la boutique) part du zéro : la forme de la couche du milieu mêle son évolution propre et celle de la couche du dessous. On ne s'en sert pas pour comparer les canaux.
- **Carte thermique** : « *où sont les mois forts de chaque canal ?* » Elle donne un repérage très rapide (décembre, plus foncé), mais **aucun chiffre précis**.

Sur l'année entière, le site représente 46,6 % du chiffre d'affaires (618 k€ sur 1 325 k€), la boutique 42,3 % et les réseaux 11,0 %. Aucun des quatre graphiques ne dit cela d'emblée : c'est une **cinquième question** (la composition de l'année), qui appelle encore une autre forme (une barre unique à 100 %, ou trois barres triées).

> ⚠️ **Piège.** Faire **un seul** graphique qui réponde à toutes les questions. Il n'existe pas : un graphique est bon pour **une** question, et un rapport en contient plusieurs. La section 1.2 y revient avec l'exigence d'un message par figure.

### 1.1.4 Le catalogue : huit graphiques à connaître

Voici les graphiques de base, regroupés par question, tous dessinés avec les données de la boutique.

![Huit graphiques à connaître, chacun avec sa question : comparer, suivre dans le temps, composer, voir une distribution, relier deux variables, comparer à une cible, suivre un entonnoir, situer des lieux. Figure construite avec matplotlib (données simulées).](figures/ch01-galerie.png)

```python hide
O.fig_galerie()
```
<!--sortie-->
```text
figure : ch01-galerie.png
```

| Graphique | Il répond à… | À retenir | Piège |
|---|---|---|---|
| **Barres** (horizontales si les noms sont longs) | Comparer des quantités entre catégories | **Toujours** partir de zéro ; trier par valeur, sauf ordre naturel (mois, âges) | Axe tronqué (1.4.1) ; trop de barres |
| **Courbe** | Suivre une évolution dans le temps | Le temps est en abscisse, régulier ; l'axe peut ne pas partir de zéro **si on le dit** | Relier des points qui ne se suivent pas ; peu de points |
| **Barres empilées à 100 %** | Comparer des compositions | Mettre en bas la part importante ; peu de segments | Plus de quatre segments : on ne compare plus que celui du bas |
| **Histogramme** | Voir la forme d'une variable (asymétrie, valeurs extrêmes) | Choisir la largeur des classes, la dire | Largeur arbitraire qui crée ou efface des pics |
| **Boîte à moustaches** | Comparer des distributions entre groupes | Médiane, quartiles, valeurs extrêmes visibles | Cache les formes (bimodalité) ; à expliquer à un public non technique |
| **Nuage de points** | Voir (et calculer) la relation entre deux variables | Un point par unité ; courbe de tendance en option | La corrélation n'est pas une cause (1.4.7) |
| **Cascade** | Expliquer le passage d'un total à un autre | Un seul total de départ, des étapes ordonnées, un total d'arrivée | Étapes trop nombreuses ; aucun repère du total |
| **Carte thermique** | Croiser deux catégories (jour × mois) | Palette **séquentielle**, valeurs écrites dans les cellules | Rampe de couleurs mal choisie (1.3.1) |

Deux graphiques de ce catalogue méritent un exemple chiffré : la cascade et la carte thermique, qui sont moins connues des débutants.

**La cascade (« waterfall »)** explique **comment on passe d'un total à un autre**. Depuis la marge brute de 2025 (417 k€) jusqu'au résultat d'exploitation (40 k€), le trajet est une suite de charges.

![Cascade : de la marge brute de 2025 (417 k€) au résultat d'exploitation (40 k€), les charges retirées une à une. Figure construite avec matplotlib à partir du compte de résultat simulé.](figures/ch01-cascade.png)

```python hide
res = O.fig_cascade()
cr = F["cr"]
ch = ["frais_personnel", "loyers_charges", "marketing", "livraison", "frais_bancaires", "amortissements", "autres_charges"]
assert round(cr["marge_brute"]) == 417 and round(cr["resultat_exploitation"]) == 40
assert [round(cr[k]) for k in ch] == [141, 65, 73, 32, 20, 23, 24]
assert round(cr["marge_brute"] - cr[ch].sum()) == round(cr["resultat_exploitation"])
assert round((cr["frais_personnel"] + cr["loyers_charges"] + cr["marketing"]) / cr["marge_brute"] * 100) == 67
assert round(cr["resultat_exploitation"] / cr["marge_brute"] * 100, 1) == 9.6
```
<!--sortie-->
```text
figure : ch01-cascade.png
```

On y lit sans calcul que le personnel (141 k€), le marketing (73 k€) et les loyers (65 k€) absorbent à eux trois **67 %** de la marge brute, et que le résultat d'exploitation n'en conserve que 9,6 %. Un tableau donnerait les mêmes nombres ; la cascade donne en plus **leur poids relatif** et **l'ordre dans lequel ils s'enchaînent**. Son titre, lui, énonce la conclusion (« les charges font le trajet »), ce que nous apprendrons à faire en 1.2.3.

**La carte thermique (« heatmap »)** croise deux catégories, ici le jour de la semaine et le mois, et représente le nombre de commandes par une intensité de couleur.

![Carte thermique des commandes de 2025 : le jour de la semaine en lignes, le mois en colonnes, le nombre de commandes écrit dans chaque case. Figure construite avec matplotlib (données simulées).](figures/ch01-heatmap.png)

```python hide
O.fig_heatmap_semaine()
sem = F["sem"]
j_tot, m_tot = sem.sum(axis=1), sem.sum(axis=0)
assert sem.values.sum() == 12946
assert j_tot[5] == 2607 and j_tot[6] == 1212
assert round(j_tot[5] / sem.values.sum() * 100, 1) == 20.1 and round(j_tot[6] / sem.values.sum() * 100, 1) == 9.4
assert sem.loc[5, 12] == 341 and sem.loc[6, 2] == 63 and round(341 / 63, 1) == 5.4
assert round((m_tot[11] + m_tot[12]) / sem.values.sum() * 100) == 26
```
<!--sortie-->
```text
figure : ch01-heatmap.png
```

Sur les 12 946 commandes de 2025, le samedi en concentre 2 607 (20,1 %) et le dimanche 1 212 (9,4 %). Deux motifs apparaissent d'un coup d'œil : une **colonne** (novembre et décembre, 26 % des commandes de l'année) et une **ligne** (le samedi). La case la plus foncée (le samedi de décembre, 341 commandes) vaut **5,4 fois** la plus claire (le dimanche de février, 63). Écrire les valeurs dans les cases compense la faible précision de la couleur (1.1.2).

> 🧭 **En pratique.** Pour une carte thermique, une rampe **séquentielle** (du clair au foncé, une seule teinte) convient aux comptages ; une rampe **divergente** (deux teintes de part et d'autre d'un centre neutre) convient aux écarts à une référence (budget, moyenne). La section 1.3.1 montre les deux.

### 1.1.5 Ce qu'il vaut mieux éviter, et pourquoi

Certains graphiques sont si répandus qu'on les croit neutres. Ils ont tous une alternative qui se lit mieux.

**Le camembert.** Il convient à **deux ou trois parts**, dont l'une s'approche d'un quart, d'un demi ou des trois quarts (des angles que l'œil repère), et dont la **somme est un tout**. Dès que l'on compare des parts voisines, la barre l'emporte.

![Camembert et barres triées pour les mêmes six parts du chiffre d'affaires 2025 par catégorie (jardin 26,7 %, maison 23,0 %, décoration 19,5 %, cuisine 17,6 %, bien-être 8,9 %, papeterie 4,3 %). Figure construite avec matplotlib (données simulées).](figures/ch01-camembert.png)

```python hide
O.fig_camembert()
assert [round(v, 1) for v in F["part_cat"].values] == [26.7, 23.0, 19.5, 17.6, 8.9, 4.3]
```
<!--sortie-->
```text
figure : ch01-camembert.png
```

Sur le camembert, on devine que le jardin est la plus grande part et la papeterie la plus petite. On ne **voit pas** que la décoration (19,5 %) dépasse la cuisine (17,6 %) de moins de deux points, ni que le bien-être pèse environ deux fois la papeterie. Sur les barres triées, tout cela se lit sans effort, et les pourcentages écrits à droite évitent toute estimation.

**Le double axe.** Deux courbes, l'une à l'échelle de gauche, l'autre à l'échelle de droite : la lectrice croit voir que les courbes « se suivent », mais c'est vous qui avez choisi les deux échelles. La section 1.4.4 montre comment on peut faire coïncider presque n'importe quelles deux séries ; à la place, on trace deux graphiques l'un au-dessus de l'autre (même axe du temps), ou un nuage de points.

**Le graphique en radar (en toile d'araignée).** Il aligne des variables sur des axes rayonnants et relie les valeurs par un polygone. On compare mal des **aires** de polygones, et l'ordre des axes (arbitraire) change la forme. Une série de petites barres, une par variable, répond à la même question avec une précision bien meilleure.

**La 3D et les effets d'ombre.** Une barre en perspective cache celles qui sont derrière, déforme les hauteurs selon l'angle de vue, et ajoute une **troisième dimension qui ne porte aucune information**. Il n'y a pas de cas où la version 3D lit mieux que la version plane ; elle ajoute seulement du bruit et des occasions de tromper (1.4.2).

**Le « donut » et la jauge de voiture.** Ce sont des camemberts évidés ou des demi-camemberts : ils ajoutent à la perte de précision de l'angle celle de l'aire, pour économiser de la place. Pour **un seul** indicateur par rapport à une cible, un nombre en grand, accompagné de son écart à la cible, est plus lisible.

> ⚠️ **Piège.** Choisir une forme « parce qu'elle fait moderne » ou « parce que le logiciel la propose en premier ». Si une forme demande une explication pour être lue, elle fait perdre à votre lectrice le temps que vous vouliez lui faire gagner.

### 1.1.6 Une méthode en cinq questions

Pour choisir, posez ces cinq questions dans l'ordre :

1. **Quelle est la question de la lectrice**, en une phrase ? (Comparer ? Suivre ? Composer ? Relier ? Écarter ?)
2. **Quelle décision suivra ?** Si aucune, il faut peut-être un chiffre, pas un graphique.
3. **Combien de valeurs ?** Deux à quinze : barres. Trente et plus dans le temps : courbe. Des milliers de points : nuage ou histogramme.
4. **Quelle précision faut-il ?** Une comparaison fine demande la position ou la longueur ; un repérage grossier supporte la couleur.
5. **Dans quel contexte sera-t-il lu ?** Un écran de bureau, une salle de projection, une feuille imprimée en noir et blanc ? Cela change la taille, les couleurs et la quantité d'information (1.2.6 et 1.3).

> ✅ **À retenir.** La forme découle de la **question**, la précision de la **hiérarchie des encodages**, la sobriété de la **lectrice**. Quand deux formes se valent, prenez celle qui demande le moins d'explication.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 et 1.2, exercices 1.1 à 1.3.
