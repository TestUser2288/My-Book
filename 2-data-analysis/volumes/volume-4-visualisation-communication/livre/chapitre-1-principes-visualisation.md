# Chapitre 1 : Principes de visualisation

> « Un graphique n'est pas une illustration de l'analyse : c'est l'analyse, telle que l'autre va la lire. »


Un lundi, la gérante vous transmet un message d'une ligne, accompagné d'une capture d'écran : « **Je reçois ton graphique et je ne comprends pas ce qu'il faut en conclure.** » Le graphique en question est celui que vous avez envoyé vendredi, avec fierté : la conversion du site selon la source de trafic, six barres de six couleurs, une grille noire, une légende, un titre qui dit « Graphique 1 ». Tous les chiffres sont justes. Et pourtant, une lectrice attentive, qui connaît son métier mieux que vous, n'en tire rien.

Ce n'est pas un problème de données : c'est un problème de **traduction**. Entre le tableau de chiffres que vous avez sous les yeux et la décision que la gérante doit prendre, il y a une personne, et cette personne dispose de quelques secondes. Le graphique est ce qui franchit cet espace. S'il est mal choisi, mal ordonné, trop chargé, trompeur sans le vouloir, le travail d'analyse des trois volumes précédents est perdu à la dernière étape.

![Avant et après : le même tableau de six conversions par source, à gauche tel que l'outil le produit par défaut, à droite après quelques gestes simples (tri, une couleur, étiquettes directes, titre qui énonce la conclusion). Figure construite avec matplotlib à partir des sessions du site 2025 (données simulées).](figures/ch01-avant-apres.png)


La figure ci-dessus est le programme de ce chapitre. À gauche, les réglages par défaut ; à droite, les mêmes données après une demi-heure de travail. Rien n'a été ajouté qui ne figure déjà dans le tableau : on a **trié**, **retiré**, **nommé** et **énoncé**. Le message, lui, ne change pas : l'e-mail convertit environ **quatre fois** mieux que les réseaux sociaux (8,7 % contre 2,2 %). Mais à droite, la gérante le **lit** en trois secondes.

Ce chapitre fixe les principes qui rendent cela possible. Il ne parle encore d'aucun outil : les outils de tableaux de bord arrivent au chapitre 2, la programmation des graphiques au chapitre 3. Les principes, eux, valent pour tous.

## Le chemin de ce chapitre

- **1.1 Choisir le bon graphique.** On part de la **question** que pose la lectrice, pas du type de graphique que l'on sait faire. Un arbre de décision, la **hiérarchie des encodages visuels** (position, longueur, angle, aire, couleur), les mêmes données dites de quatre façons, le catalogue (barres, courbes, nuages, histogrammes, cascades, cartes thermiques) et ce qu'il vaut mieux éviter (camemberts chargés, doubles axes, radars, 3D).
- **1.2 Clarté, simplicité et mise en page.** Retirer ce qui ne dit rien, ordonner, étiqueter directement, écrire un **titre qui énonce la conclusion**, soigner axes et unités, comparer en **petits multiples**, penser à la salle de projection, et **redessiner** un graphique en cinq gestes, avant et après.
- **1.3 ➕ Théorie des couleurs, accessibilité, systèmes de design.** Trois familles de palettes, la couleur qui a un sens et un seul, le **daltonisme** simulé par le calcul, le **contraste** calculé selon une formule publique, et la **page de design** qui rend cohérents tous les tableaux de bord d'une entreprise.
- **1.4 ➕ Erreurs courantes et graphiques trompeurs.** Dix pièges, chacun avec le graphique qui trompe et sa version corrigée : axe tronqué, aires et 3D, échelles différentes, double axe, période choisie, pourcentages sans effectifs, corrélation suggérée, camembert à neuf parts, paradoxe de Simpson en image, échelle logarithmique non signalée. Pour chacun : **qui est trompé, par quoi, avec quelle conséquence**.

> 💡 **Intuition.** Un graphique est un **argument**. Comme tout argument, il a une thèse (ce qu'il faut conclure), des preuves (les données) et une forme (ce qui le rend convaincant, ou trompeur). Choisir un graphique, c'est choisir la forme la plus **honnête** et la plus **rapide à lire** pour une thèse que l'on peut défendre.

> ⚠️ **Piège.** « C'est mon outil qui l'a fait comme ça » n'est pas une justification. Les réglages par défaut d'un logiciel ne connaissent ni votre lectrice, ni votre question, ni la décision qui suit : ils produisent un graphique **possible**, pas un graphique **bon**.

## Les données du chapitre

Les exemples viennent de la **boutique** simulée des volumes précédents : commandes et lignes de commande 2023–2025 (chiffre d'affaires de 1 139, 1 189 puis 1 325 k€), jours d'exploitation (publicité, promotions, météo), sessions du site en 2025 (conversion par source), compte de résultat, retours de marchandises, **villes** (vingt villes fictives, de « Ville A » à « Ville T », dans un plan inventé), et la série « avec incidents » (une panne du site, une fermeture exceptionnelle) du volume III. Tout est **simulé** ; la vérité programmée sert ici de juge : un graphique est « fidèle » s'il laisse voir ce qui s'est réellement passé dans les données.

Les personnes sont désignées **par leur fonction** : la gérante, la responsable logistique, le financeur. Les nombres de la prose sont calculés par des blocs exécutés ; les figures sont toutes dessinées avec matplotlib (le code est rangé dans `build/outils_ch01.py` pour ne pas encombrer le texte). Aucune capture d'un produit commercial n'apparaît dans ce chapitre.


## 1.1 Choisir le bon graphique

Avant de dessiner quoi que ce soit, il faut savoir **ce que la lectrice cherche** : comparer, suivre une évolution, voir une répartition, repérer une relation, situer un écart. Cette section donne une méthode pour passer de la question au graphique, explique pourquoi certaines formes se lisent mieux que d'autres (c'est de la perception, pas du goût), montre les mêmes données dites de quatre façons, puis passe en revue les graphiques à connaître et ceux qu'il vaut mieux éviter.

### 1.1.1 On part de la question, pas du graphique

Un analyste débutant ouvre son outil, choisit « graphique » dans le menu, puis regarde ce que l'outil propose. Un analyste expérimenté fait l'inverse : il écrit d'abord, en une phrase, **la question à laquelle le graphique doit répondre**. Le type de graphique en découle presque toujours.

![Arbre de décision : à chaque question que l'on se pose sur les données correspond une famille de graphiques. Schéma dessiné avec matplotlib.](figures/ch01-arbre.png)


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


- **Barres groupées** : « *quel canal est le plus fort, mois par mois ?* » On compare des hauteurs voisines. En décembre, le site vend 90 k€, la boutique 73 k€ et les réseaux 20 k€. Trente-six barres, c'est beaucoup : on lit bien un mois, mal une tendance.
- **Courbes** : « *comment chaque canal évolue-t-il ?* » On suit une forme dans le temps ; le site dépasse la boutique presque tous les mois (sauf en avril et en août), et sa baisse d'août est plus marquée. Les courbes sont **étiquetées directement** (le nom au bout du trait) : pas besoin de légende.
- **Aires empilées** : « *quel est le total, et de quoi se compose-t-il ?* » Le total de décembre (184 k€) se lit d'un coup. En revanche, seule la couche du bas (la boutique) part du zéro : la forme de la couche du milieu mêle son évolution propre et celle de la couche du dessous. On ne s'en sert pas pour comparer les canaux.
- **Carte thermique** : « *où sont les mois forts de chaque canal ?* » Elle donne un repérage très rapide (décembre, plus foncé), mais **aucun chiffre précis**.

Sur l'année entière, le site représente 46,6 % du chiffre d'affaires (618 k€ sur 1 325 k€), la boutique 42,3 % et les réseaux 11,0 %. Aucun des quatre graphiques ne dit cela d'emblée : c'est une **cinquième question** (la composition de l'année), qui appelle encore une autre forme (une barre unique à 100 %, ou trois barres triées).

> ⚠️ **Piège.** Faire **un seul** graphique qui réponde à toutes les questions. Il n'existe pas : un graphique est bon pour **une** question, et un rapport en contient plusieurs. La section 1.2 y revient avec l'exigence d'un message par figure.

### 1.1.4 Le catalogue : huit graphiques à connaître

Voici les graphiques de base, regroupés par question, tous dessinés avec les données de la boutique.

![Huit graphiques à connaître, chacun avec sa question : comparer, suivre dans le temps, composer, voir une distribution, relier deux variables, comparer à une cible, suivre un entonnoir, situer des lieux. Figure construite avec matplotlib (données simulées).](figures/ch01-galerie.png)


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


On y lit sans calcul que le personnel (141 k€), le marketing (73 k€) et les loyers (65 k€) absorbent à eux trois **67 %** de la marge brute, et que le résultat d'exploitation n'en conserve que 9,6 %. Un tableau donnerait les mêmes nombres ; la cascade donne en plus **leur poids relatif** et **l'ordre dans lequel ils s'enchaînent**. Son titre, lui, énonce la conclusion (« les charges font le trajet »), ce que nous apprendrons à faire en 1.2.3.

**La carte thermique (« heatmap »)** croise deux catégories, ici le jour de la semaine et le mois, et représente le nombre de commandes par une intensité de couleur.

![Carte thermique des commandes de 2025 : le jour de la semaine en lignes, le mois en colonnes, le nombre de commandes écrit dans chaque case. Figure construite avec matplotlib (données simulées).](figures/ch01-heatmap.png)


Sur les 12 946 commandes de 2025, le samedi en concentre 2 607 (20,1 %) et le dimanche 1 212 (9,4 %). Deux motifs apparaissent d'un coup d'œil : une **colonne** (novembre et décembre, 26 % des commandes de l'année) et une **ligne** (le samedi). La case la plus foncée (le samedi de décembre, 341 commandes) vaut **5,4 fois** la plus claire (le dimanche de février, 63). Écrire les valeurs dans les cases compense la faible précision de la couleur (1.1.2).

> 🧭 **En pratique.** Pour une carte thermique, une rampe **séquentielle** (du clair au foncé, une seule teinte) convient aux comptages ; une rampe **divergente** (deux teintes de part et d'autre d'un centre neutre) convient aux écarts à une référence (budget, moyenne). La section 1.3.1 montre les deux.

### 1.1.5 Ce qu'il vaut mieux éviter, et pourquoi

Certains graphiques sont si répandus qu'on les croit neutres. Ils ont tous une alternative qui se lit mieux.

**Le camembert.** Il convient à **deux ou trois parts**, dont l'une s'approche d'un quart, d'un demi ou des trois quarts (des angles que l'œil repère), et dont la **somme est un tout**. Dès que l'on compare des parts voisines, la barre l'emporte.

![Camembert et barres triées pour les mêmes six parts du chiffre d'affaires 2025 par catégorie (jardin 26,7 %, maison 23,0 %, décoration 19,5 %, cuisine 17,6 %, bien-être 8,9 %, papeterie 4,3 %). Figure construite avec matplotlib (données simulées).](figures/ch01-camembert.png)


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


## 1.2 Clarté, simplicité et mise en page

Le bon type de graphique ne suffit pas : un graphique peut être juste et illisible. Cette section donne les gestes qui transforment un graphique « correct » en graphique **clair** : retirer, ordonner, nommer, titrer, aligner, comparer, adapter à la salle. Elle se termine par un redesign complet, étape par étape, de celui que la gérante n'a pas compris.

### 1.2.1 Retirer ce qui ne dit rien

Chaque élément d'un graphique demande un petit effort à l'œil : un trait, une couleur, une légende, une grille. Quand l'élément **porte de l'information**, l'effort vaut la peine. Quand il n'en porte pas, il fait seulement concurrence aux éléments qui comptent. On appelle parfois cela le **rapport données/encre** : la part de l'encre (des pixels) qui dessine des données, par rapport à celle qui dessine autre chose.

Regardons le graphique de départ, celui que votre outil a produit sans aucun réglage, sur la conversion du site par source de trafic :

![Cinq étapes du redessin d'un même graphique : le brouillon (réglages par défaut), puis le tri, une couleur d'accentuation, l'étiquetage direct sans grille ni axe, enfin le titre qui énonce la conclusion. Figure construite avec matplotlib à partir des sessions web 2025 (données simulées).](figures/ch01-etapes.png)


Le premier panneau (« le brouillon ») cumule des défauts courants que l'on peut compter :

- **Six couleurs vives** pour six catégories qui n'ont aucune raison d'être distinguées par la couleur (l'axe les nomme déjà).
- Une **légende** qui répète ce que dit l'axe, et qui chevauche la grille.
- Une **grille noire** et épaisse, plus visible que les données.
- Un axe vertical appelé « valeur », sans unité ; un titre, « Graphique 1 », qui ne dit rien.
- Des noms **inclinés** à 45 degrés, qu'il faut pencher la tête pour lire, et des noms bruts de la base (« referent », « reseaux ») au lieu d'un langage humain.

Pour décider quoi retirer, un test simple : **si je masque cet élément, la lectrice perd-elle quelque chose ?** Si non, on le retire. Le test paraît brutal ; il donne presque toujours un graphique meilleur. La seule exception est ce qui est nécessaire pour **ne pas se tromper** : l'unité, la période, la source, un zéro.

> 💡 **Intuition.** Un graphique clair n'est pas un graphique **vide** : c'est un graphique où tout ce qui reste a une raison. La grille, par exemple, n'est pas interdite ; on la garde **très claire** (elle sert à lire une valeur) ou on la remplace par les valeurs écrites sur les barres.

### 1.2.2 Ordonner et étiqueter directement

**Ordonner.** Les catégories d'une base de données sont souvent dans l'ordre alphabétique, ou dans l'ordre où elles sont apparues : cet ordre n'a **aucun sens** pour la lectrice. Il faut ranger :

- par **valeur décroissante** (ou croissante) pour une comparaison de catégories : le plus grand en haut d'un graphique horizontal ;
- par **ordre naturel** quand il existe : les mois dans l'ordre du calendrier, les tranches d'âge de la plus jeune à la plus âgée, les étapes d'un entonnoir dans l'ordre du parcours ;
- et seulement en dernier recours, par ordre alphabétique (quand on cherche un nom précis dans une longue liste).

Dans le deuxième panneau de la figure précédente, le simple tri fait apparaître immédiatement le classement : l'e-mail (8,7 %), le direct (6,9 %), la recherche naturelle (4,0 %), les sites partenaires (3,8 %), la publicité payante (3,0 %), les réseaux (2,2 %). On a aussi mis les barres à l'**horizontale**, parce que les noms sont longs : un nom couché se lit sans effort.

**Étiqueter directement.** Une légende oblige l'œil à faire des allers-retours entre la barre et la clé de couleur. Quand on peut écrire le nom **sur** ou **à côté** de l'élément, on supprime la légende :

- pour des barres, le nom est déjà sur l'axe, et la **valeur** s'écrit au bout de la barre (panneau 3) ;
- pour des courbes, le nom s'écrit **au bout du trait** (nous l'avons fait pour les courbes de la section 1.1.3) ;
- pour un nuage, on étiquette les quelques points qui comptent et on laisse les autres anonymes.

Avec les valeurs écrites, l'axe horizontal et la grille deviennent inutiles : on les retire. Le tableau ci-dessous résume la logique de ces trois premiers gestes.

| Geste | Ce que l'on retire | Ce que l'on gagne |
|---|---|---|
| Trier | l'ordre arbitraire de la base | le classement lu sans effort |
| Étiqueter directement | la légende et l'axe des valeurs | des allers-retours en moins |
| Renommer | les noms bruts (« referent ») | un langage que la lectrice comprend |

### 1.2.3 Le titre qui dit la conclusion

Le titre est la **première chose lue**, et très souvent la seule. Il y a deux façons de s'en servir :

- le titre **descriptif** dit de quoi parle le graphique : « Chiffre d'affaires mensuel 2025 » ;
- le titre **informatif** dit **ce qu'il faut en conclure** : « Le chiffre d'affaires mensuel est multiplié par 2,5 entre février et décembre : novembre et décembre font 25 % de l'année. »

![Même courbe, deux titres : à gauche le titre descriptif, à droite le titre informatif, avec deux repères annotés (février et décembre) et la zone novembre-décembre en surbrillance. Figure construite avec matplotlib à partir du chiffre d'affaires mensuel 2025 (données simulées).](figures/ch01-titre.png)


Les deux courbes sont identiques. Mais à gauche, la lectrice doit chercher l'information : où est la bosse ? de combien ? pourquoi la montrer ? À droite, on lui dit : de 73 k€ en février à 184 k€ en décembre, soit **2,5 fois** plus, et les deux derniers mois font un quart de l'année (24,7 %). Elle peut être en désaccord, mais elle sait **ce que vous affirmez**.

Une recette pour un titre informatif : **un sujet, un verbe, un chiffre, une comparaison**. « Le chiffre d'affaires (sujet) est multiplié (verbe) par 2,5 (chiffre) entre février et décembre (comparaison). » On met l'information secondaire (période, unité, méthode) dans un **sous-titre** plus petit, en gris, et la **source** en pied de graphique.

> ⚠️ **Piège.** Un titre informatif **s'engage** : il doit être vrai, et le graphique doit le montrer. « Les ventes s'effondrent » sous une baisse de deux pour cent est un mensonge ; « Les ventes baissent de 2 % » est une information. Le titre n'est pas un endroit pour exagérer.

**Annoter ce que l'on sait.** Un graphique peut aussi porter des **annotations** : une phrase courte, au bon endroit, qui explique un creux ou une bosse. Voici le chiffre d'affaires quotidien de la boutique sur dix semaines de 2025, sans puis avec annotation.

![Chiffre d'affaires quotidien du 1er mars au 15 mai 2025 : à gauche sans annotation, avec des creux inexpliqués ; à droite avec les deux événements connus (une panne du site sur trois jours, une fermeture exceptionnelle sur deux jours). Figure construite avec matplotlib à partir de la série « avec incidents » (données simulées).](figures/ch01-annotation.png)


À gauche, les deux creux interrogent : une erreur de mesure, une vraie baisse ? À droite, un simple bandeau les explique : la **panne du site** de trois jours (1,18 k€ par jour en moyenne, soit 39 % d'un jour ordinaire, dont la médiane est de 3,04 k€) et la **fermeture exceptionnelle** de deux jours (1,33 k€, soit 44 %). La lectrice ne se demande plus ce qui s'est passé ; elle peut passer à la question suivante. Annoter, c'est faire à sa place le travail d'enquête que vous avez déjà fait.

### 1.2.4 Axes, unités, alignement et hiérarchie visuelle

Quelques règles courtes, qui évitent la plupart des erreurs de lecture.

**Les axes.**

- Une **barre** commence **toujours** à zéro (la longueur est la mesure). Une **courbe** peut ne pas commencer à zéro, à condition que l'axe soit **lisible** et que l'on ne cherche pas à faire croire à une catastrophe ou à un miracle (1.4.1).
- L'**unité** est écrite : « k€ », « % », « commandes par jour ». Un axe sans unité oblige à deviner.
- Les **graduations** sont peu nombreuses, rondes (0, 50, 100, 150) et à la française : espace pour les milliers, virgule pour les décimales.
- On évite de **couper** un axe au milieu (les « zigzags » qui sautent des valeurs) ; si une donnée dépasse les autres, on la sort dans un second graphique.

**Les nombres.** On arrondit à ce que la décision demande : « 1 325 k€ » et non « 1 324 763,72 € ». On garde le **même nombre de décimales** dans toute une série (8,7 %, 6,9 %, 4,0 % : pas 8,7 %, 6,9 % et 4 %). Un nombre sans unité ni période n'est pas un résultat.

**L'alignement et l'espace.** On aligne à **gauche** les titres, les sous-titres et les notes sur une même ligne verticale (celle du bord de l'axe) ; on laisse de l'espace **blanc** entre les blocs plutôt que des traits ; on regroupe ce qui va ensemble (un titre et son sous-titre) et on sépare ce qui est différent.

**La hiérarchie visuelle.** Dans un graphique, tout n'est pas aussi important. On le dit par la **taille** (le titre plus grand que les graduations), le **poids** (le titre en gras), la **couleur** (une seule teinte vive, le reste en gris) et la **position** (le message en haut à gauche, la source en bas). Une règle utile : on devrait pouvoir **flouter** la figure et distinguer encore le titre, l'élément mis en valeur et le reste.

> 🧭 **En pratique.** Gardez une **seule couleur d'accentuation** par graphique (le bleu du livre) et mettez tout le contexte en gris. L'œil va tout de suite à ce qui est coloré, donc ce qui est coloré doit être ce que vous voulez dire.

### 1.2.5 Les petits multiples

Quand on a **plusieurs séries à comparer dans le temps**, la tentation est de tout tracer sur un seul graphique. Avec trois courbes, cela fonctionne ; avec six, cela devient un plat de spaghettis. Les **petits multiples** (ou « petits graphiques juxtaposés ») offrent une alternative : **un petit graphique par série, tous à la même échelle, côte à côte**.

![À gauche, six courbes de chiffre d'affaires mensuel par catégorie sur un seul graphique ; à droite, les mêmes courbes en petits multiples, une catégorie par case, avec les cinq autres en gris pour repère. Figure construite avec matplotlib à partir des ventes 2025 (données simulées).](figures/ch01-petits-multiples.png)


À gauche, on peine à suivre quelle courbe est laquelle, et plusieurs courbes se confondent. À droite, chaque case raconte une histoire simple :

- le **jardin** culmine en juillet (56,7 k€) et redescend ;
- la **décoration** reste entre 13 et 28 k€ de janvier à novembre, puis **plus que double** entre novembre et décembre (60,9 k€, soit 2,2 fois novembre) ;
- la **maison**, la **cuisine**, le **bien-être** et la **papeterie** montent en fin d'année, la papeterie restant sous 8 k€ par mois.

Trois règles pour réussir des petits multiples : la **même échelle** dans toutes les cases (sinon on compare des pentes qui n'ont pas la même unité, voir 1.4.3) ; **l'ordre** des cases significatif (par valeur, par saison, pas par hasard) ; et les **autres séries en gris** dans chaque case, pour que l'on voie comment chacune se situe par rapport aux autres.

### 1.2.6 Penser à la salle : lisibilité en projection

Un graphique conçu sur un écran de bureau est souvent illisible une fois projeté dans une salle de réunion ou réduit pour entrer dans une diapositive. Deux raisons : la **distance** (on lit de loin) et la **réduction** (la taille des caractères diminue avec celle de la figure).

![Le même graphique avec des polices de 6,5 points (à gauche) et de 12 points (à droite) : à trois mètres de l'écran, seule la version de droite se lit. Figure construite avec matplotlib à partir de la conversion du site par source (données simulées).](figures/ch01-projection.png)


Les repères de ce livre sont les suivants :

- **18 points au minimum** pour tout texte projeté, **24 points ou plus** pour les titres ;
- une figure insérée dans une diapositive est **réduite** : une police de 10 points dans une figure de 11 pouces de large, ramenée à 6 pouces de large, devient une police de **5,5 points**. On dessine donc la figure **à la taille** où elle sera vue, ou l'on augmente les polices ;
- **peu d'éléments** : six barres se lisent à trois mètres, soixante non ;
- des **traits épais** (au moins 2 points) et des **marqueurs gros** ;
- un **fort contraste** avec le fond (section 1.3.4) ; un fond clair et uni se lit mieux qu'un fond dégradé ou photographique ;

> ⚠️ **Piège.** Tester son graphique **à l'écran, de près**. Reculez de trois mètres, ou réduisez-le à la taille d'un timbre-poste : si vous n'y voyez plus que du gris, il faut simplifier.

### 1.2.7 Un seul message : redessiner en cinq gestes

Le chemin qui mène du brouillon de la section 1.2.1 au graphique final tient en cinq gestes, que l'on peut appliquer à presque tout graphique :

1. **Ranger** : trier, orienter à l'horizontale si les noms sont longs, renommer.
2. **Une couleur, un accent** : tout en gris sauf l'élément du message (ici l'e-mail).
3. **Étiqueter directement** : les valeurs au bout des barres ; retirer légende, grille et axe devenu inutile.
4. **Titrer par la conclusion** : un titre qui énonce le message, une source en pied.
5. **Relire** : le test du flou, le test du « rien à retirer », la lecture par quelqu'un d'autre.

Voici le cœur du dernier état, en quinze lignes : on voit que la qualité vient du **choix des éléments**, pas de la quantité de code.

```python
import matplotlib.pyplot as plt
s = F["conv"].sort_values()                         # conversion du site par source, en %
fig, ax = plt.subplots(figsize=(6, 3))
ax.barh(s.index, s.values, color=["#b9b8b0"] * 5 + ["#2a78d6"])   # gris, sauf l'e-mail
for i, v in enumerate(s.values):
    ax.text(v + 0.1, i, f"{v:.1f} %".replace(".", ","), va="center")
ax.set_title("L'e-mail convertit 4 fois mieux que les réseaux sociaux", loc="left", fontweight="bold")
ax.set_xticks([]); ax.grid(False)
for bord in ("top", "right", "bottom", "left"):
    ax.spines[bord].set_visible(False)
print(len(ax.patches), "barres ; titre :", ax.get_title(loc="left"))
plt.close(fig)
```
<!--sortie-->
```text
6 barres ; titre : L'e-mail convertit 4 fois mieux que les réseaux sociaux
```

Le sixième geste, **la liste de contrôle**, vaut d'être épinglée au-dessus du bureau :

| Question avant d'envoyer | Réponse attendue |
|---|---|
| Ai-je **une seule idée** ? | Oui, et je peux la dire en une phrase. |
| Le **titre** dit-il la conclusion ? | Oui, avec un chiffre. |
| Les barres sont-elles **triées** ? | Oui, ou l'ordre est naturel. |
| Les **couleurs** ont-elles un sens ? | Oui, une couleur d'accent, le reste en gris. |
| Puis-je **retirer** quelque chose ? | Non : tout ce qui reste sert. |
| L'**unité**, la **période** et la **source** sont-elles là ? | Oui, en petit, mais lisibles. |

> ✅ **À retenir.** La clarté n'est pas un talent artistique : c'est une **procédure**. Ranger, accentuer, nommer, titrer, relire. Un graphique clair est un graphique où la lectrice n'a rien à deviner.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.3 à 1.5, exercices 1.4 à 1.6.


## 1.3 ➕ Théorie des couleurs, accessibilité, systèmes de design pour tableaux de bord

La couleur est l'outil le plus puissant et le plus mal employé de la visualisation : elle attire l'œil avant tout le reste, et elle ne se lit pas de la même façon pour tout le monde. Cette section pose trois familles de palettes, la règle « une couleur, un sens », la **simulation du daltonisme** et le **calcul du contraste**, puis montre comment réunir ces décisions dans une **page de design** que l'on applique à tous les tableaux de bord de l'entreprise. C'est une section facultative pour qui veut seulement faire un graphique correct, mais indispensable pour qui construit des tableaux de bord que d'autres liront chaque jour.

### 1.3.1 Trois familles de palettes

On n'utilise pas la même palette pour des **catégories**, pour des **quantités ordonnées** et pour des **écarts autour d'un centre**.

![Trois familles de palettes : qualitative (des catégories sans ordre), séquentielle (du faible au fort, ici le chiffre d'affaires 2025 par catégorie et par mois en k€) et divergente (un écart à un budget, centré sur zéro : le bleu est au-dessus du budget, le rouge en dessous). Figure construite avec matplotlib (données simulées).](figures/ch01-palettes.png)


- **Qualitative** (panneau de gauche) : des teintes **bien distinctes**, sans ordre entre elles, pour des **catégories**. Six teintes au plus : au-delà, l'œil ne les distingue plus et la lectrice doit consulter la légende (on regroupe alors, ou on passe en petits multiples, section 1.2.5).
- **Séquentielle** (au milieu) : **une teinte**, du clair au foncé, pour une **quantité ordonnée** (du faible au fort). Les valeurs vont ici de 2,9 k€ (papeterie en juillet) à 60,9 k€ (décoration en décembre). Le foncé signifie « beaucoup », sans exception.
- **Divergente** (à droite) : deux teintes de part et d'autre d'un **centre neutre**, pour un **écart à une référence**. La référence est ici le budget : sur les soixante-douze cases (six catégories, douze mois), vingt-deux sont **en dessous** du budget (en rouge), les autres au-dessus (en bleu). L'écart extrême (+32,4 %, jardin en octobre) dépasse la limite de ±25 % de l'échelle : au-delà, toutes les cases ont la même teinte, ce qu'une note devrait signaler.

Trois erreurs classiques à éviter :

- Utiliser une palette **qualitative** (arc-en-ciel) pour une quantité : l'œil lit des **catégories** là où il y a un continuum, et croit voir des frontières nettes là où il n'y en a pas.
- Utiliser une palette **séquentielle** pour un écart : le centre (« conforme au budget ») devient une couleur arbitraire au milieu de l'échelle.
- Placer le **centre** d'une palette divergente ailleurs que sur la valeur neutre : le zéro doit être gris clair, pas bleu pâle.

> 💡 **Intuition.** Choisir une palette, c'est répondre à la question : « *qu'est-ce que la couleur doit dire ?* » Des catégories distinctes ? Une intensité ? Un côté du seuil ? La réponse décide de la famille.

### 1.3.2 Une couleur, un sens (et un seul)

Dans un ensemble de graphiques, une couleur doit toujours **signifier la même chose** : si le bleu désigne le canal « Boutique » dans un graphique, il ne désigne pas « budget » dans le suivant. Sans cette discipline, la lectrice doit relire la légende de chaque figure, ce qui est exactement ce que les couleurs devaient lui épargner.

Quelques conventions simples :

- une **couleur principale** (ici le bleu) pour l'élément du message ; le **gris** pour le contexte ;
- une **couleur d'alerte** (rouge) réservée à ce qui est défavorable, et une **couleur de réussite** (aqua) à ce qui est favorable. On les emploie **avec parcimonie** : un tableau de bord où tout est rouge ou vert ne signale plus rien ;
- jamais de **signification culturelle** supposée universelle : le rouge n'est « mauvais » que dans les contextes où cela a été convenu, et le vert « bon » de même ;
- la **même couleur** pour la même catégorie **dans tout le document** (la boutique est toujours bleue, le site toujours orange).

> ⚠️ **Piège.** « Rouge pour les pertes, vert pour les gains » semble évident. Ce n'est pas lisible par tout le monde (1.3.3), ni toujours exact : une baisse des retours est une **bonne** nouvelle. Dire en mots ce que la couleur signifie (« en dessous du budget », « au-dessus ») vaut mieux que de supposer la lecture.

### 1.3.3 Le daltonisme : simuler au lieu de supposer

On désigne par « daltonisme » une famille de particularités de la vision des couleurs. La forme la plus fréquente est la difficulté à distinguer le **rouge** et le **vert** (elle touche environ un homme sur douze, et beaucoup moins de femmes). Les deux grands types sont la **protanopie** (absence de la sensibilité au rouge) et la **deutéranopie** (absence de la sensibilité au vert) ; plus rare, la **tritanopie** concerne le bleu et le jaune.

On n'a pas besoin de deviner ce que voient ces personnes : on peut le **calculer**. Chaque type de vision correspond à une **matrice 3 × 3** qui transforme les couleurs d'origine en couleurs perçues. Les matrices utilisées ici ont été publiées en 2009 par Machado et ses collègues ; on convertit d'abord la couleur sRGB en intensités lumineuses linéaires, on multiplie par la matrice, puis on revient à l'sRGB.

```python
import numpy as np
from matplotlib.colors import to_rgb
M_DEUT = np.array([[0.367322, 0.860646, -0.227968],        # deutéranopie (sévérité 1,0)
                   [0.280085, 0.672501, 0.047413],
                   [-0.011820, 0.042940, 0.968881]])
def vue_deut(couleur):
    v = np.array(to_rgb(couleur))
    lin = np.where(v <= 0.04045, v / 12.92, ((v + 0.055) / 1.055) ** 2.4)    # sRGB -> linéaire
    o = np.clip(M_DEUT @ lin, 0, 1)
    return np.where(o <= 0.0031308, 12.92 * o, 1.055 * o ** (1 / 2.4) - 0.055)
rouge, vert = "#d62728", "#2ca02c"
dist = lambda a, b: round(float(np.linalg.norm((np.array(a) - np.array(b)) * 255)))
print("distance rouge-vert, vision typique :", dist(to_rgb(rouge), to_rgb(vert)))
print("distance rouge-vert, deutéranopie   :", dist(vue_deut(rouge), vue_deut(vert)))
```
<!--sortie-->
```text
distance rouge-vert, vision typique : 209
distance rouge-vert, deutéranopie   : 30
```

La « distance » est ici la longueur du segment entre deux couleurs dans l'espace rouge-vert-bleu (de 0 à 441) : elle n'est qu'un repère grossier, mais l'ordre de grandeur parle. Le rouge et le vert classiques, qui sont à **209** l'un de l'autre pour une vision typique, tombent à **30** en deutéranopie : ils deviennent deux bruns presque indiscernables.

![Les mêmes barres vues par différentes personnes. Ligne du haut : la palette « rouge-vert » classique ; ligne du bas : la palette du livre. Colonnes : vision typique, protanopie, deutéranopie, tritanopie, niveaux de gris (impression en noir et blanc). Simulation calculée avec matplotlib.](figures/ch01-daltonisme.png)


La ligne du haut montre le résultat : en protanopie et en deutéranopie, les cinq barres « rouge-vert » se réduisent à des nuances d'olive et de brun. En niveaux de gris, ce qui arrive aussi à une page imprimée en noir et blanc, le rouge et le vert ont presque la même **luminosité** (rapport de 1,48 seulement) : on ne les distingue plus non plus. La palette du livre, en bas, fait mieux sur les teintes : le bleu reste bleu et l'orange devient un ocre bien distinct en protanopie et en deutéranopie. Elle n'est pas pour autant parfaite : l'orange et le rouge, déjà proches pour une vision typique (distance 38), le deviennent encore davantage en deutéranopie (31), et en niveaux de gris le bleu et le rouge (rapport de luminosité de 1,12), comme l'orange et l'aqua (1,14), sont presque identiques. **C'est pourquoi la palette ne suffit jamais** : les barres portent leur nom, et les séries leur étiquette.

Les règles qui en découlent sont simples :

1. **Ne jamais faire porter l'information par la couleur seule.** Doubler la couleur par une **étiquette** (le nom du canal au bout de la courbe), un **symbole** (▲ ▼), une **forme** de marqueur ou un **motif** (hachures, traits pleins et pointillés).
2. **Varier la luminosité**, pas seulement la teinte : un clair et un foncé se distinguent dans toutes les formes de vision.
3. **Éviter l'association rouge-vert** pour des catégories qui s'opposent. Si la convention du métier l'impose (favorable/défavorable), ajouter le signe (+ et −) ou un mot.
4. **Tester** : simuler les trois formes avant de publier un graphique ou un tableau de bord, comme on relit l'orthographe.

> ✅ **À retenir.** Un graphique doit rester lisible **sans la couleur** (en noir et blanc, ou pour une personne qui confond rouge et vert). La couleur renforce l'information, elle n'en est pas le seul porteur.

### 1.3.4 Le contraste se calcule

Un texte gris clair sur fond blanc fatigue l'œil et devient illisible à la projection. Plutôt que de juger « à l'œil », on mesure le **rapport de contraste** entre deux couleurs, avec la formule publiée dans les recommandations d'accessibilité du web (les « WCAG »). Elle part de la **luminance relative** d'une couleur, qui mesure combien de lumière elle émet, avec un poids différent pour chaque primaire (l'œil est plus sensible au vert qu'au bleu) :

$$L = 0{,}2126\,R + 0{,}7152\,G + 0{,}0722\,B \qquad\text{(après conversion en intensités linéaires)}$$

Le rapport de contraste entre deux couleurs de luminances $L_1 \ge L_2$ vaut alors $(L_1 + 0{,}05)\,/\,(L_2 + 0{,}05)$. Il va de **1** (deux couleurs identiques) à **21** (noir sur blanc). Les recommandations demandent au moins **4,5 : 1** pour un texte courant, et **3 : 1** pour un grand texte (18 points ou 14 points en gras) et pour les éléments graphiques utiles à la compréhension (barres, traits, icônes).

```python
def lum_relative(c):
    lin = [v / 12.92 if v <= 0.04045 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * lin[0] + 0.7152 * lin[1] + 0.0722 * lin[2]
def rapport_contraste(c1, c2):
    a, b = sorted([lum_relative(c1), lum_relative(c2)], reverse=True)
    return (a + 0.05) / (b + 0.05)
print("noir sur blanc :", round(rapport_contraste((0, 0, 0), (1, 1, 1)), 1))
print("bleu du livre sur blanc :", round(rapport_contraste(to_rgb("#2a78d6"), (1, 1, 1)), 1))
```
<!--sortie-->
```text
noir sur blanc : 21.0
bleu du livre sur blanc : 4.4
```

Le noir sur blanc atteint le maximum (21 : 1), comme prévu. Le bleu du livre sur blanc donne 4,4 : 1, **juste sous** le seuil de 4,5 pour un texte courant. On peut s'en servir pour des titres, des traits et des barres, pas pour un paragraphe en petits caractères.

![Rapport de contraste de huit combinaisons de couleurs, calculé avec la formule des recommandations d'accessibilité, sur le fond clair du livre : seuls les textes sombres atteignent 4,5 : 1 ; l'aqua (2,7 : 1) et un gris trop clair (1,7 : 1) sont insuffisants. Figure construite avec matplotlib.](figures/ch01-contraste.png)


La figure applique la formule aux couleurs du livre, sur son fond clair. Le texte principal (19,2 : 1) et le texte secondaire (7,7 : 1) passent largement. Le gris des graduations (3,5 : 1) ne convient qu'à de grands éléments : c'est un choix délibéré, car on veut qu'une graduation se **voie à peine**. Le bleu (4,3 : 1) et l'orange (3,1 : 1) conviennent aux traits et aux grands titres, pas à un texte courant. L'aqua (2,7 : 1) est **insuffisant** pour écrire : on le réserve aux surfaces (une barre, une aire), toujours **doublées d'une étiquette**. Enfin, un gris très clair sur blanc (1,7 : 1) est un classique du « texte discret » que personne ne lit.

> 🧭 **En pratique.** Les chiffres importants s'écrivent en **encre** (noir ou gris très foncé), jamais en couleur claire. La couleur sert à désigner un élément, pas à écrire sur lui. Et pour un texte écrit **sur** une couleur (un chiffre dans une barre), on calcule le contraste dans les deux sens : blanc sur le bleu du livre donne 4,4 : 1, juste acceptable pour un grand texte.

### 1.3.5 Une page de design pour tous les tableaux de bord

Quand une entreprise produit des dizaines de tableaux de bord, il arrive que chacun ait ses couleurs, ses polices, sa façon de nommer « chiffre d'affaires » (hors taxe ? toutes taxes comprises ?). La lectrice qui passe de l'un à l'autre doit **réapprendre** à lire à chaque fois. La réponse tient en une page : le **système de design** (ou « charte graphique des données »), qui fixe une fois pour toutes les choix de cette section.

![Une page de règles pour les tableaux de bord de la boutique : palette (avec le sens de chaque couleur), typographie, grille, composants (une carte d'indicateur, une carte de graphique) et conventions. Maquette dessinée avec matplotlib ; elle ne reproduit l'interface d'aucun outil.](figures/ch01-design.png)


La page de la figure tient en cinq rubriques :

1. **Palette** : cinq couleurs plus un gris, chacune avec son **rôle** (principal, à regarder, favorable, secondaire, défavorable, contexte).
2. **Typographie** : trois ou quatre tailles, avec leur usage (titre de page, titre de graphique qui énonce la conclusion, texte, source).
3. **Grille et espacements** : une marge, une gouttière, un nombre de colonnes, un plafond de visuels par page (six, ici).
4. **Composants** : la forme d'une carte d'indicateur (ci-dessus : « Chiffre d'affaires, 2025 : 1 325 k€, +11,4 % sur 2024 ») et celle d'une carte de graphique.
5. **Conventions** : « un titre = une conclusion », « toujours la période, l'unité, la source », « jamais la couleur seule », des **noms** sans ambiguïté (« CA hors taxe », jamais « CA » seul), le format des nombres.

Trois bénéfices, du plus évident au plus sous-estimé : la **cohérence** (la lectrice reconnaît tout de suite ce qu'elle voit), la **vitesse** (on ne rediscute pas des couleurs à chaque nouveau tableau de bord), et la **qualité** (les décisions d'accessibilité sont prises **une fois**, par quelqu'un qui a le temps de les tester, plutôt que dix fois, par quelqu'un qui est pressé).

> 🧭 **En pratique.** Conservez la page de design **à côté du code ou du fichier du tableau de bord**, avec un numéro de version, et relisez-la avant chaque nouveau tableau de bord. Les outils de tableaux de bord (chapitre 2) permettent d'enregistrer une palette et un thème pour les réutiliser ; les menus changent d'une version à l'autre : à vérifier dans la documentation de votre outil.

> ✅ **À retenir.** Trois familles de palettes pour trois usages ; une couleur, un sens ; la couleur n'est **jamais** seule ; le contraste se **calcule** ; et tout cela se range dans une **page de design** que l'on applique partout.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.6 et 1.7, exercices 1.7 et 1.8.


## 1.4 ➕ Erreurs courantes et graphiques trompeurs

Un graphique peut tromper sans qu'aucun chiffre soit faux. Il suffit d'un axe qui ne part pas de zéro, d'une période bien choisie ou de deux échelles ajustées pour que la lectrice tire une conclusion que les données ne soutiennent pas. Cette section présente **dix pièges**. Chacun est montré par un graphique qui trompe, puis par sa version corrigée ; et pour chacun, nous répondons à trois questions, parce que c'est ainsi que l'on mesure la gravité d'une erreur : **qui est trompé, par quoi, avec quelle conséquence**.

Une précision avant de commencer : la plupart de ces pièges sont **involontaires**. On les commet parce que l'outil le propose par défaut, parce que le graphique « avait l'air mieux » ainsi, ou parce que l'on n'a pas vu ce que la lectrice verrait. Mais l'effet est le même, et la responsabilité de la personne qui publie aussi.

> ⚠️ **Règle d'honnêteté.** Si un graphique vous plaît **parce qu'il appuie votre message**, relisez-le comme si vous cherchiez à le contredire. Les trois questions de cette section (qui, quoi, quelle conséquence) servent à cela.

### 1.4.1 L'axe tronqué

**Le piège.** Une barre représente une valeur par sa **longueur**. Si l'axe ne part pas de zéro, la longueur ne représente plus la valeur : elle représente l'**écart** à la valeur où l'on a coupé. Les chiffres d'affaires de 2023, 2024 et 2025 (1 139, 1 189 et 1 325 k€) en donnent un exemple.

![À gauche, les trois chiffres d'affaires annuels sur des barres dont l'axe est coupé à 1 100 k€ : 2025 paraît presque six fois plus haut que 2023. À droite, les mêmes barres avec un axe à zéro : +16 % en deux ans. Figure construite avec matplotlib (données simulées).](figures/ch01-axe-tronque.png)


```python
t = F["t"]
visuel = (t[2025] - 1100) / (t[2023] - 1100)        # hauteurs des barres si l'axe part de 1 100 k€
reel = t[2025] / t[2023]
print(f"hauteur apparente : x{visuel:.1f} ; rapport réel : x{reel:.2f} (+{(reel - 1) * 100:.0f} %)")
```
<!--sortie-->
```text
hauteur apparente : x5.8 ; rapport réel : x1.16 (+16 %)
```

Avec un axe coupé à 1 100 k€, la barre de 2025 paraît **5,8 fois** plus haute que celle de 2023 ; en réalité, elle ne l'est que de 16 %. Le graphique de droite, à zéro, dit la vérité.

**Qui est trompé, par quoi, avec quelle conséquence ?** *La gérante, ou le financeur*, par la **longueur des barres**, qui laisse croire à un quasi-sextuplement de l'activité. *Conséquence :* un investissement ou un recrutement décidé sur une croissance imaginaire ; et, quand la réalité rattrape l'enthousiasme, une confiance durablement entamée dans tous les graphiques de l'analyste.

**Le correctif.** Pour des **barres**, l'axe part de zéro, sans exception. Pour une **courbe**, on peut ne pas partir de zéro, à condition que l'axe soit visible et que l'on ne cherche pas à dramatiser (si l'écart est petit, on le **dit** dans le titre : « +16 % en deux ans »).

### 1.4.2 Les aires proportionnelles au mauvais carré, et la 3D

**Le piège.** Quand on représente une valeur par un cercle, un carré ou une icône, il faut décider ce qui est proportionnel à la valeur : la **dimension** (rayon, côté) ou l'**aire**. Si l'on prend le rayon, une valeur trois fois plus grande donne un cercle d'une aire **neuf** fois plus grande, et c'est l'aire que l'œil perçoit.

![À gauche, des cercles dont le rayon est proportionnel à la valeur (1, 2, 3) : celui de la valeur 3 paraît neuf fois plus grand que celui de la valeur 1. À droite, des cercles dont l'aire est proportionnelle à la valeur : l'impression de 1 à 3 est respectée. Schéma dessiné avec matplotlib.](figures/ch01-aire-rayon.png)


Le même effet vaut pour les **graphiques en 3D** : une barre en perspective ne se lit plus contre une grille, sa hauteur dépend de l'angle de vue, et celles du fond sont partiellement cachées. Il n'y a **aucun cas** où l'effet 3D aide à lire un chiffre.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Tout lecteur*, par l'**aire** et la **perspective**, qui amplifient les grandes valeurs. *Conséquence :* des écarts surestimés ou mal classés (la barre de devant paraît plus grande que celle de derrière, même quand elle est plus petite).

**Le correctif.** Représenter les valeurs par la **longueur** (barres planes) ; si l'on doit absolument utiliser des cercles (une carte), faire l'**aire** proportionnelle à la valeur, et ajouter des **étiquettes chiffrées**. Pas de 3D.

### 1.4.3 Des échelles différentes qui rendent comparable ce qui ne l'est pas

**Le piège.** Quand on place deux graphiques côte à côte avec des **axes propres** à chacun, ils ont l'air aussi grands l'un que l'autre, même si l'un représente sept fois plus que l'autre. Les chiffres d'affaires mensuels de la boutique et des réseaux sociaux en 2025 le montrent.

![En haut, deux courbes (boutique, réseaux sociaux) avec chacune son propre axe : les deux variations semblent de même ampleur. En bas, les mêmes courbes sur le même axe de 0 à 85 k€ : l'échelle réelle apparaît. Figure construite avec matplotlib (données simulées).](figures/ch01-echelles.png)


En haut, la courbe de la boutique et celle des réseaux ont toutes les deux une allure ascendante spectaculaire, et on peut les croire de poids comparable. En bas, avec un axe commun, la boutique atteint 73,4 k€ en décembre et les réseaux 20,4 k€ : les réseaux ne représentent que **11,0 %** du chiffre d'affaires de l'année. On voit aussi que, relativement, les réseaux progressent **plus** de février à décembre (×3,7) que la boutique (×2,2), mais à partir d'un niveau bien plus bas : les deux lectures sont vraies, et c'est l'axe commun qui permet de les tenir ensemble.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Un responsable qui compare des canaux*, par l'**apparente égalité** de graphiques à axes libres. *Conséquence :* un budget publicitaire réparti comme si les deux canaux avaient le même poids.

**Le correctif.** Quand on **compare**, on met les séries sur **le même axe** (petits multiples à échelle commune, section 1.2.5). Quand on veut montrer la **forme** d'une série à petite échelle, on peut laisser un axe libre, mais on le **dit** (« axe propre à chaque graphique ») et l'on évite de les juxtaposer comme s'ils étaient comparables.

### 1.4.4 Le double axe

**Le piège.** Deux courbes sur un seul graphique, l'une lue à gauche (en k€), l'autre à droite (en nombre de commandes) : on peut choisir les deux échelles pour que les courbes **coïncident**, ou au contraire qu'elles divergent. Avec la publicité et les commandes mensuelles de 2025, voici ce que donne un bon choix d'échelles.

![À gauche, la publicité mensuelle (axe de gauche, de 0 à 14 k€) et le nombre de commandes (axe de droite, de 0 à 2 000) en 2025 : les deux courbes semblent se suivre, parce que les deux échelles ont été choisies pour cela. À droite, le nuage de points des mêmes douze mois : la relation se voit sans choix d'échelle. Figure construite avec matplotlib (données simulées).](figures/ch01-double-axe.png)


La corrélation entre les deux séries, sur ces douze mois, vaut 0,80 : elle existe réellement. Mais le graphique de gauche **ne le prouve pas** : l'accord apparent des courbes est le résultat de l'échelle choisie à droite (0 à 2 000) et à gauche (0 à 14). Avec 0 à 3 000 à droite, la courbe des commandes serait bien moins pentue et ne ressemblerait plus à celle de la publicité. Le nuage de droite, lui, **ne dépend d'aucun choix** : un point par mois, la publicité en abscisse, les commandes en ordonnée.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Une direction qui lit « la pub fait vendre »*, par la **coïncidence fabriquée** de deux échelles. *Conséquence :* un budget de publicité augmenté sur la foi d'une ressemblance de courbes qui aurait pu être obtenue avec n'importe quelles deux séries.

**Le correctif.** Deux graphiques **superposés** sur le même axe du temps (un par série), ou un nuage de points. Si l'on emploie malgré tout un double axe, on **colore** chaque axe comme sa courbe et on écrit les unités ; on évite d'ajuster les échelles pour que les courbes se touchent. Mais la corrélation, même réelle, n'est **pas une cause** : voir 1.4.7.

### 1.4.5 La période choisie

**Le piège.** « Les ventes ont progressé de 53 % en trois mois. » La phrase est **vraie** : le chiffre d'affaires mensuel passe de 120 k€ en octobre à 184 k€ en décembre 2025. Mais présentée seule, elle laisse croire à une accélération.

![À gauche, une courbe sur trois mois seulement (octobre à décembre 2025), titrée « les ventes ont progressé de 53 % en trois mois ». À droite, trois années entières : la même hausse se reproduit chaque fin d'année (zone orangée), c'est une saison. Figure construite avec matplotlib (données simulées).](figures/ch01-cerises.png)


Sur trois années entières, la même hausse d'octobre à décembre se retrouve chaque fois : +53,0 % en 2023, +54,7 % en 2024, +53,1 % en 2025. Ce n'est pas une accélération, c'est la **saison**. Et l'on peut aussi, en choisissant d'autres bornes, raconter l'inverse : de janvier à février 2025, le chiffre d'affaires baisse de 19 %, et personne ne dira pourtant que la boutique s'effondre.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Le financeur ou la gérante*, par le **choix des bornes**. *Conséquence :* une prévision extrapolée d'une pente saisonnière (on commande trop de stock en janvier, on recrute en décembre pour une demande qui ne durera pas).

**Le correctif.** Montrer **au moins un cycle complet** (un an de plus que ce que l'on veut dire), comparer **au même mois de l'an dernier**, et dire pourquoi on a choisi la période. Une phrase honnête vaut mieux qu'une période flatteuse : « Le chiffre d'affaires de décembre est supérieur de 17 % à celui de décembre 2024. »

### 1.4.6 Les pourcentages sans effectifs

**Le piège.** Un classement de **taux** (« les produits les plus retournés ») met en haut les produits qui ont **peu de ventes**, parce qu'un petit effectif fait varier un taux par à-coups. Prenons les retours de marchandises sur les lignes vendues par les réseaux sociaux : 120 produits, un taux moyen de retour de 6,7 %.

![À gauche, le classement des six produits au taux de retour le plus élevé (de 19 % à 14 %), sans leurs effectifs. À droite, le taux de chaque produit en fonction du nombre de lignes vendues, avec la moyenne (trait plein) et les bornes à 95 % (pointillés) : les petits effectifs s'étalent en entonnoir. Figure construite avec matplotlib (données simulées).](figures/ch01-effectifs.png)


À gauche, le classement semble alarmant : le produit 116 retourne **18,5 %** de ses ventes, trois fois la moyenne. Mais le produit 116 n'a été vendu que **27 fois** par les réseaux, et **5** de ces lignes ont été retournées. Un retour de plus ou de moins déplace son taux de **3,7 points**. Le produit « typique » a 64,5 lignes vendues ; les six du palmarès en ont entre 27 et 65.

Pour savoir si ces taux sont **trop** élevés, on compare chaque taux à ce que le seul hasard donnerait pour un effectif de cette taille : une borne autour de la moyenne, qui se resserre quand l'effectif grandit (le « diagramme en entonnoir » de droite).

```python
p0 = F["ret_moy"] / 100                                  # taux de retour moyen des réseaux
g = F["ret_g"]
ecart = np.sqrt(p0 * (1 - p0) / g["n"])
for nom, z in (("95 %", 1.96), ("99,8 %", 3.09)):
    haut = int((g["taux"] / 100 > p0 + z * ecart).sum())
    print(f"produits au-dessus de la borne à {nom} : {haut}")
print("attendu par hasard à 95 % :", round(0.025 * len(g)))
```
<!--sortie-->
```text
produits au-dessus de la borne à 95 % : 6
produits au-dessus de la borne à 99,8 % : 0
attendu par hasard à 95 % : 3
```

Six produits dépassent la borne à 95 %, pour **trois** attendus par pur hasard sur 120 produits ; aucun ne dépasse la borne à 99,8 %. Le bon message n'est donc ni « ces produits sont mauvais » ni « tout va bien » : c'est « **à surveiller**, avec des effectifs trop petits pour conclure ».

**Qui est trompé, par quoi, avec quelle conséquence ?** *La responsable des achats*, par un **classement de taux sans effectifs**. *Conséquence :* un produit retiré du catalogue, ou un fournisseur mis en cause, sur la foi de cinq retours.

**Le correctif.** Toujours **donner l'effectif** à côté du taux (« 18,5 % de 27 lignes »), ne classer que les produits ayant un effectif minimal, ou tracer un **diagramme en entonnoir** qui montre où le hasard suffit à expliquer l'écart (les intervalles et les petits effectifs sont traités au volume III, chapitres 2 et 4).

### 1.4.7 La corrélation suggérée

**Le piège.** Deux courbes qui montent ensemble ne se **causent** pas forcément. Ici, la publicité et les commandes de la boutique, mois par mois, sur trois ans.

![À gauche, le nuage de points de la publicité mensuelle et des commandes mensuelles sur 36 mois, titré « corrélation 0,81 ». À droite, le même nuage où novembre-décembre sont en orange, mars-mai en bleu et les autres mois en gris : la saison commande à la fois la publicité et les ventes. Figure construite avec matplotlib (données simulées).](figures/ch01-correlation.png)


Sur 36 mois, la corrélation est de **0,81** : forte. La figure de droite explique pourquoi elle ne prouve rien : en novembre et décembre, la boutique dépense en moyenne **12 214 €** en publicité, contre **5 158 €** les autres mois (2,4 fois plus), et enregistre **1 574** commandes contre **898** (1,8 fois plus). La saison fait monter les deux. Si l'on retire novembre et décembre, la corrélation tombe à **0,16** : presque rien. (Ce piège et la façon de le démêler sont traités au volume III, chapitres 2 et 3 : ici, on retient que le **graphique** ne doit pas suggérer une cause que l'analyse n'a pas établie.)

**Qui est trompé, par quoi, avec quelle conséquence ?** *La gérante*, par un **nuage ou un titre qui parle de corrélation sans la mettre en perspective**. *Conséquence :* doubler le budget publicitaire en comptant sur un effet que la saison seule expliquait.

**Le correctif.** Colorer ou séparer par la variable cachée (la saison), **comparer à saison égale**, et écrire le titre avec prudence : « Publicité et commandes montent ensemble en fin d'année, mais la saison suffit à l'expliquer. »

### 1.4.8 Le camembert à neuf parts

**Le piège.** Au-delà de quatre ou cinq parts, un camembert ne se lit plus : les couleurs se confondent, la légende oblige à des allers-retours et les parts voisines sont indiscernables. Le chiffre d'affaires 2025 par ville (20 villes fictives) en fait un cas d'école.

![À gauche, un camembert à neuf parts (les huit premières villes et « autres villes ») : couleurs et angles voisins se confondent. À droite, les mêmes parts en barres triées, avec « autres villes » (30,4 %) en gris. Figure construite avec matplotlib (données simulées).](figures/ch01-camembert-neuf.png)


Deux parts, la ville F (6,2 %) et la ville G (6,0 %), ne diffèrent que de 0,2 point, soit **0,8 degré** d'angle : personne ne peut les départager sur un camembert. Sur les barres, l'ordre et les valeurs sont immédiats. Et la plus grande « part » est celle des **autres villes** (30,4 %), qui est un fourre-tout : on la met en gris, en bas, pour qu'elle ne passe pas pour une ville.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Un responsable de zone*, par une légende illisible et des angles voisins. *Conséquence :* un classement des villes faux, donc une priorité commerciale mal placée.

**Le correctif.** Barres triées, étiquettes chiffrées, regroupement des petites catégories en un « autres » discret, ou limitation du graphique aux huit premières.

### 1.4.9 Le paradoxe de Simpson en image

**Le piège.** Une moyenne globale peut dire l'inverse de chaque sous-groupe (c'est le paradoxe de Simpson, vu au volume III, chapitre 1). Un graphique qui ne montre que la moyenne globale trompe d'autant plus qu'il est « simple ». Le chiffre d'affaires moyen par jour, avec et sans promotion, en est un exemple.

![À gauche, le chiffre d'affaires moyen par jour des jours sans promotion (3 339 €) et des jours de promotion (3 300 €) : la promotion « rapporte moins ». À droite, la même comparaison mois par mois (janvier, juin, juillet, novembre, les seuls mois avec des promotions) : la promotion rapporte plus, chaque fois. Figure construite avec matplotlib (données simulées).](figures/ch01-simpson.png)


```python
promo = F["promo_glob"]                                   # CA moyen par jour : sans (0) et avec (1) promotion
mois = F["promo_mois"]                                    # idem, mois par mois (les mois qui ont des promotions)
print(promo.round(0).to_string())
print(((mois[1] / mois[0] - 1) * 100).round(1).to_string())
```
<!--sortie-->
```text
promo_active
0    3339.0
1    3300.0
mois
1     15.5
6      2.2
7      6.7
11    15.3
```

À gauche, un jour de promotion rapporte en moyenne 3 300 €, soit **1,2 % de moins** qu'un jour sans promotion (3 339 €). À droite, mois par mois, la promotion rapporte **plus** : +15,5 % en janvier, +2,2 % en juin, +6,7 % en juillet, +15,3 % en novembre. L'explication est une question de **composition** : les 153 jours de promotion tombent en janvier (63 jours), juin (21), juillet (42) et novembre (27), jamais en décembre, alors que les jours **sans** promotion incluent tout décembre, le meilleur mois de l'année (5 357 € par jour en moyenne). La moyenne globale compare des jours de saisons différentes.

**Qui est trompé, par quoi, avec quelle conséquence ?** *La gérante*, par une **moyenne globale** présentée sans la saison. *Conséquence :* suppression d'une promotion qui rapporte réellement, pour une raison qui tient au calendrier.

**Le correctif.** Comparer **à situation égale** (même mois, même jour de la semaine) et le montrer : le deuxième graphique est le bon.

### 1.4.10 L'échelle logarithmique non signalée

**Le piège.** Une échelle logarithmique transforme les **rapports** en **distances égales** : de 1 à 10 occupe autant de place que de 10 à 100. Elle est précieuse pour des valeurs qui s'étalent sur plusieurs ordres de grandeur (ou pour des taux de croissance), mais elle **comprime** les écarts, et, utilisée sans le dire, elle trompe. Le chiffre d'affaires 2025 des 120 produits, du plus au moins vendu, en donne l'exemple.

![À gauche, le chiffre d'affaires 2025 de chacun des 120 produits en barres sur une échelle linéaire : quelques produits dominent. À droite, le même graphique en échelle logarithmique non signalée : la décroissance paraît douce et régulière. Figure construite avec matplotlib (données simulées).](figures/ch01-log.png)


À gauche, on voit ce qu'il y a de vrai : quelques produits dominent (le premier réalise 66,0 k€, soit **7,9 fois** le produit médian), et dix produits font à eux seuls **29,1 %** du chiffre d'affaires. À droite, la même série en échelle logarithmique, sans mention, semble une pente régulière : les écarts entre produits paraissent modestes. De plus, une **barre** sur une échelle logarithmique ne mesure plus rien : sa longueur dépend de l'endroit, arbitraire, où l'axe est coupé.

**Qui est trompé, par quoi, avec quelle conséquence ?** *Une lectrice non technique*, par une **échelle qu'elle n'a pas reconnue**. *Conséquence :* sous-estimer la concentration du chiffre d'affaires, donc le risque de dépendre de quelques produits.

**Le correctif.** On utilise l'échelle logarithmique **seulement** pour des courbes (jamais des barres), on **l'écrit** (« échelle logarithmique ») dans l'axe ou le titre, et on met en évidence les graduations (1, 10, 100) qui font comprendre qu'un pas est un facteur 10.

### 1.4.11 Une liste de contrôle avant de publier

Pour terminer, voici la liste à parcourir **avant d'envoyer** un graphique. Chaque ligne renvoie à un piège de cette section.

| Piège | La question à se poser |
|---|---|
| Axe tronqué (1.4.1) | Mes barres partent-elles de zéro ? |
| Aires et 3D (1.4.2) | La grandeur est-elle représentée par une longueur, ou par une aire proportionnelle à la valeur ? |
| Échelles différentes (1.4.3) | Si je compare, les axes sont-ils communs ? Sinon, est-ce écrit ? |
| Double axe (1.4.4) | Les deux échelles sont-elles choisies sans arrière-pensée ? Un nuage ne serait-il pas plus honnête ? |
| Période choisie (1.4.5) | Mon graphique montre-t-il au moins un cycle complet ? |
| Pourcentages sans effectifs (1.4.6) | L'effectif est-il visible à côté du taux ? |
| Corrélation suggérée (1.4.7) | Une variable cachée (saison, taille, prix) explique-t-elle les deux courbes ? |
| Camembert à neuf parts (1.4.8) | Plus de quatre parts ? Alors des barres. |
| Simpson (1.4.9) | Ma moyenne mélange-t-elle des sous-groupes qui ne sont pas comparables ? |
| Échelle logarithmique (1.4.10) | Est-elle écrite ? Mes barres sont-elles à échelle linéaire ? |

> ✅ **À retenir.** Un graphique trompeur n'est pas un graphique faux : c'est un graphique **vrai qui suggère une conclusion fausse**. Pour chaque graphique, demandez : *qui pourrait être trompé, par quoi, avec quelle conséquence ?* Et préférez toujours la version qui montre les effectifs, l'axe complet, la période entière et la comparaison à situation égale.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.8 et 1.9, exercices 1.9 à 1.14.


## Bilan du chapitre 1

Vous savez maintenant :

- **partir de la question** de la lectrice pour choisir le graphique (comparer, suivre, composer, distribuer, relier, expliquer un passage, croiser) plutôt que de partir de l'outil ;
- **ranger les encodages** par précision de lecture (position, longueur, angle, aire, couleur) et compenser par des étiquettes chiffrées chaque fois que l'on quitte la position ou la longueur ;
- **dire les mêmes données de quatre façons** et savoir à quelle question répond chacune ;
- **éviter** les camemberts chargés, les doubles axes, les radars, la 3D et les jauges, et leur substituer des barres, deux graphiques superposés ou un nuage ;
- **retirer, ordonner, nommer, titrer, relire** : redessiner un graphique en cinq gestes, avec un **titre qui énonce la conclusion**, une seule couleur d'accentuation, des étiquettes directes ;
- **comparer en petits multiples** à échelle commune, et **annoter** ce que l'on sait des creux et des bosses ;
- **adapter** la figure à la salle (18 points au minimum, peu d'éléments, traits épais) ;
- (en option) **choisir une palette** selon ce que la couleur doit dire (catégories, intensité, écart), ne jamais faire porter l'information par la couleur seule, **simuler le daltonisme** et **calculer le contraste** ;
- (en option) **fixer le tout dans une page de design** applicable à tous les tableaux de bord ;
- (en option) **reconnaître dix pièges** (axe tronqué, aires et 3D, échelles différentes, double axe, période choisie, pourcentages sans effectifs, corrélation suggérée, camembert à neuf parts, Simpson en image, échelle logarithmique non signalée) et poser pour chacun la question : *qui est trompé, par quoi, avec quelle conséquence ?*

Le tableau suivant résume le chapitre en six questions, à parcourir **avant d'envoyer un graphique**.

| Question | Ce qu'on attend comme réponse |
|---|---|
| **Quelle question le graphique pose-t-il ?** | Une phrase, avec la décision qui suit. |
| **Quelle forme ?** | Celle qui répond à cette question par une position ou une longueur (barres, courbe, nuage). |
| **Que peut-on retirer ?** | Tout ce qui ne dit rien : légende redondante, grille lourde, couleurs sans sens. |
| **Que dit le titre ?** | La conclusion, avec un chiffre ; l'unité, la période et la source en pied. |
| **Qui ne le verra pas bien ?** | Une personne daltonienne, un écran de projection, une impression en noir et blanc : le graphique reste lisible. |
| **Qui pourrait être trompé ?** | Personne : axe à zéro, période complète, effectifs visibles, comparaison à situation égale. |

Le fil conducteur du chapitre tient en une phrase : **un graphique est un argument, et la lectrice doit pouvoir le lire, le croire et le contester**. Il vous reste, dans le volume, à voir **où fabriquer** ces graphiques : les outils de tableaux de bord (chapitre 2), la programmation en Python (chapitre 3), puis la façon de les ranger dans un récit (chapitre 4) et de les présenter (chapitre 5).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.9 (choisir une forme, camembert contre barres, redessin en cinq gestes, titres et annotations, petits multiples, simulation du daltonisme, contrastes d'une palette, axe tronqué et période choisie, entonnoir et paradoxe de Simpson) et exercices 1.1 à 1.14.
