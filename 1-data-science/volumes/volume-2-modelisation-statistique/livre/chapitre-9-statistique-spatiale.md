# Chapitre 9 : ➕ Statistique spatiale

> « Tout est lié à tout le reste, mais ce qui est proche est plus lié que ce qui est lointain. »
> — Waldo Tobler, *première loi de la géographie* (1970)

> 🧭 **Chapitre complémentaire.** Ce chapitre est **entièrement facultatif** : rien dans les chapitres 1 à 6 ni dans le projet du volume n'en dépend. Il s'adresse à ceux dont les données ont une **position** : des adresses de clients, des points de livraison, des zones géographiques, des capteurs. Si c'est votre cas, vous verrez que presque tout ce que nous avons appris repose sur une hypothèse que l'espace met à mal : l'**indépendance** des observations.

La boutique livre maintenant dans toute une région. La gérante remarque des choses que les tableaux des chapitres précédents ne savent pas dire :

- *« Les délais de livraison longs sont groupés : quand un client d'un quartier attend longtemps, ses voisins aussi. »* Un point isolé ne serait pas un problème ; un **paquet** de retards, c'est un problème de tournée ou de route.
- *« Mes ventes par zone ont l'air de former des îlots : des zones où l'on vend beaucoup, entourées de zones où l'on vend beaucoup. »* Est-ce réel, ou est-ce l'œil qui voit des formes dans le hasard ?
- *« Je voudrais promettre un délai au client avant même d'avoir livré dans son quartier. »* Comment **prédire** une valeur en un endroit où l'on n'a rien mesuré ?
- *« Mes clients du quartier se regroupent-ils vraiment autour de la boutique, ou sont-ils répartis au hasard ? »*

Quatre questions, quatre outils : l'**autocorrélation spatiale**, le **variogramme** et le **krigeage**, les **processus ponctuels**. Les voici, dans l'ordre.

## Le chemin de ce chapitre

- **9.1 Données spatiales et cartes** : les trois grands types de données spatiales, la façon de repérer un point sur la Terre, de calculer une distance **sans se tromper**, et de dessiner une carte honnête sans fond de carte.
- **9.2 Autocorrélation spatiale** : définir « voisin » avec une **matrice de poids**, mesurer la ressemblance entre voisins avec l'**indice de Moran** (démontré, calculé à la main, puis testé par permutations), l'indice de **Geary**, et repérer *où* se trouvent les îlots avec les indices **locaux** (LISA).
- **9.3 Variogramme et krigeage** : décrire comment la ressemblance **décroît avec la distance**, ajuster un modèle (pépite, palier, portée), et **prédire** en un point non mesuré avec une **variance d'erreur** (le krigeage, dérivé avec des multiplicateurs de Lagrange).
- **9.4 Processus ponctuels** : quand ce sont les **positions** qui sont aléatoires ; hasard complet, agrégat ou répulsion ? Test des quadrats, plus proche voisin, fonction K de Ripley, enveloppes de Monte-Carlo.
- **Bilan du chapitre**, puis le **cahier** : applications guidées (le code complet de ce chapitre, pas à pas) et douze exercices corrigés.

> 🧭 **Comment travailler avec ce chapitre.** Aucune bibliothèque de cartographie n'est nécessaire (ni `geopandas`, ni `pykrige`) : tout est écrit avec NumPy, SciPy et matplotlib. C'est volontaire. Calculer soi-même un indice de Moran ou résoudre soi-même un système de krigeage est la meilleure garantie de comprendre ce que font ensuite les bibliothèques spécialisées. En contrepartie, les cartes n'ont **pas de fond de carte** (il faudrait télécharger des tuiles) : ce sont des graphiques de coordonnées, sobres mais honnêtes. Pour garder le livre lisible, les simulations et les tracés sont exécutés « en coulisses » : on y lit les résultats et les figures, et le code complet se trouve dans le cahier, chapitre 9 (applications 9.1 à 9.7).

> 📦 **Les données de ce chapitre.** Les données sont **simulées**, avec des graines fixes, de façon que nous connaissions la vérité et puissions vérifier que les méthodes la retrouvent. Le décor est une **région fictive** : les villes, les zones et les coordonnées sont inventées.
>
> - Une **grille de 12 × 12 zones** fictives (144 zones de 5 km de côté) avec des ventes par habitant qui présentent une autocorrélation spatiale *connue* (fichier `donnees/ch09-zones.csv`), plus une variable de contrôle sans aucune structure spatiale.
> - **200 livraisons** dans un carré de 100 km de côté, avec un délai en jours qui varie de façon continue dans l'espace (fichier `donnees/ch09-livraisons.csv`).
> - Des **semis de points** (adresses de clients), simulés directement dans les sections qui les utilisent.
> - Les **coordonnées de dix villes fictives** (A à J), écrites à la main, et le tableau `donnees/clients.csv` du volume pour les effectifs par ville.
>
> Le générateur du chapitre est dans `build/donnees_ch09.py` ; il est reconstruit pas à pas dans le cahier.


## 9.1 Données spatiales et cartes

Avant de mesurer quoi que ce soit, il faut comprendre ce qui change quand les données ont une **position** : à quoi ressemblent ces données, comment on repère un point sur la Terre, comment on mesure une distance sans se tromper, et comment on dessine une carte honnête. Cette section prépare le vocabulaire et les outils des trois suivantes.

> 💡 **Intuition.** Dans un tableau ordinaire, l'ordre des lignes n'a aucune importance : on peut les mélanger sans rien changer à la moyenne, à la régression ou au test. Dans des données spatiales, **où** se trouve chaque ligne fait partie de l'information. Deux clients voisins se ressemblent plus que deux clients éloignés, et c'est précisément ce qui casse l'hypothèse d'**indépendance** sur laquelle reposent presque tous les outils du volume I et des chapitres 1 et 2 de ce volume.

### 9.1.1 Pourquoi l'espace change tout

Un petit exemple pour sentir le problème. La gérante a mesuré le délai de quatre livraisons : deux dans la Ville A (les points $P_1$ et $P_2$, à quelques rues l'un de l'autre) et deux dans la Ville C ($P_3$ et $P_4$). Les délais sont 6, 7, 3 et 4 jours.

La moyenne est $(6+7+3+4)/4=5$ jours, et l'écart-type est d'environ 1,83 jour. Si les quatre livraisons étaient **indépendantes**, l'écart-type de la moyenne serait $s/\sqrt n\approx 0{,}91$ jour : la formule du volume I (section 2.4). Mais $P_1$ et $P_2$ ont subi la même route embouteillée, $P_3$ et $P_4$ la même route fluide. En réalité, nous n'avons pas **quatre** informations indépendantes, mais plutôt **deux** (une par ville). Notre moyenne est beaucoup moins précise que ne le dit la formule.

> ⚠️ **Le danger concret.** Avec des observations corrélées dans l'espace, les erreurs-types « habituelles » sont **trop petites**, les intervalles de confiance trop étroits et les p-valeurs trop optimistes. Nous aurons l'impression d'avoir 200 observations alors que nous en avons, au sens de l'information, bien moins. C'est la raison pour laquelle il faut **mesurer** la dépendance spatiale avant de lui faire confiance, et c'est l'objet de tout ce chapitre.

> 🧪 **La loi de Tobler en une phrase.** « Tout est lié à tout le reste, mais ce qui est proche est plus lié que ce qui est lointain. » Ce n'est pas un théorème, c'est une observation qui se vérifie pour les prix de l'immobilier, la température, les délais de livraison, les maladies contagieuses… et qui justifie tous les outils qui suivent : ils mesurent *à quelle vitesse* la ressemblance s'estompe avec la distance.

### 9.1.2 Trois types de données spatiales

Selon ce qui est aléatoire et ce qui est fixe, on distingue trois grandes familles. Savoir dans quelle famille on se trouve est la **première** question à se poser, car elle détermine les outils.

| Type | Ce qu'on observe | Ce qui est fixe / aléatoire | Exemple de la boutique | Outils (section) |
|---|---|---|---|---|
| **Géostatistique** | une valeur en des **points** d'un phénomène défini *partout* | les lieux sont choisis (fixes), la valeur est aléatoire | le délai de livraison, mesuré à 200 adresses, qui existe en tout point de la zone | variogramme, krigeage (9.3) |
| **Données surfaciques** (*lattice*) | une valeur par **zone** d'un découpage | le découpage est fixe, la valeur est aléatoire | les ventes par habitant de chaque zone | matrice de poids, Moran, Geary, LISA (9.2) |
| **Semis de points** | les **positions** elles-mêmes | les lieux sont **aléatoires** | les adresses des clients du quartier de la boutique | quadrats, plus proche voisin, K de Ripley (9.4) |

La frontière n'est pas étanche : les mêmes ventes peuvent être vues par zone (surfacique) ou, si l'on connaît les adresses, comme un semis de points avec une « marque » (le montant). Mais le **choix du modèle** suit toujours cette question : *qu'est-ce qui est aléatoire ici ?*

> 💡 **Un test pratique.** Imaginez que l'on refasse l'expérience. Si les **valeurs** changent mais pas les lieux (le même découpage en zones, d'autres ventes), c'est de la géostatistique ou du surfacique. Si ce sont les **lieux** qui changeraient (d'autres adresses de clients), c'est un semis de points.

### 9.1.3 Repérer un point : coordonnées et distances

Un point sur Terre se repère par sa **latitude** $\varphi$ (de −90° au pôle Sud à +90° au pôle Nord) et sa **longitude** $\lambda$ (de −180° à +180° à partir du méridien de Greenwich). Pour tout ce chapitre, la boutique livre dans une **région fictive** : dix villes imaginaires, dont voici les coordonnées (elles ne désignent aucun lieu réel ; la formule, elle, fonctionne avec n'importe quelles coordonnées).

| Ville | A | B | C | D | E | F | G | H | I | J |
|------------------|-----|-----|-----|-----|-----|-----|-----|-----|-----|-----|
| **Latitude** (°N) | 47,30 | 46,90 | 46,40 | 45,80 | 45,30 | 44,70 | 47,00 | 46,00 | 45,20 | 44,30 |
| **Longitude** (°E) | 3,20 | 4,60 | 3,60 | 4,90 | 3,40 | 5,30 | 6,40 | 6,70 | 6,60 | 3,70 |


**Piège n° 1 : un degré n'est pas une distance fixe.** Un degré de latitude vaut toujours à peu près 111 km (la Terre est presque une sphère de rayon $R\approx 6371$ km, et $1^\circ=\pi/180$ radian, donc $R\pi/180\approx 111{,}2$ km). Mais les méridiens se **rapprochent** quand on monte vers le pôle : un degré de longitude vaut $111{,}2\times\cos\varphi$ km. À la latitude de nos villes (environ 47°), $\cos 47^\circ\approx0{,}68$ : un degré de longitude ne vaut que **76 km**.

Faisons un calcul à la main pour la Ville A $(47{,}30\,;\,3{,}20)$ et la Ville B $(46{,}90\,;\,4{,}60)$, en prenant leur latitude moyenne $47{,}1^\circ$ (avec $\cos 47{,}1^\circ\approx0{,}681$) :

- écart de latitude : $0{,}40^\circ\times111{,}2\approx44{,}5$ km vers le sud ;
- écart de longitude : $1{,}40^\circ\times111{,}2\times0{,}681\approx106{,}0$ km vers l'est ;
- distance ≈ $\sqrt{44{,}5^2+106{,}0^2}\approx114{,}9$ km.

Si l'on avait oublié le $\cos\varphi$ et traité les degrés comme des unités égales, on aurait trouvé $111{,}2\times\sqrt{0{,}40^2+1{,}40^2}\approx161{,}9$ km : **41 % d'erreur**, parce que ce trajet est surtout est-ouest. Plus le trajet est orienté est-ouest, plus l'erreur grandit (nous le mesurons plus bas).

> 📐 **La formule de haversine (distance sur la sphère).** La plus courte distance entre deux points d'une sphère de rayon $R$ est un arc de **grand cercle**. Pour deux points $(\varphi_1,\lambda_1)$ et $(\varphi_2,\lambda_2)$ (en radians) :
>
> $$a=\sin^2\!\Big(\frac{\varphi_2-\varphi_1}{2}\Big)+\cos\varphi_1\cos\varphi_2\,\sin^2\!\Big(\frac{\lambda_2-\lambda_1}{2}\Big),\qquad d=2R\,\arcsin\sqrt a .$$
>
> **Contrôle de bon sens.** Si $\lambda_1=\lambda_2$ (même méridien), alors $a=\sin^2\big((\varphi_2-\varphi_1)/2\big)$ et $d=2R\arcsin\big|\sin((\varphi_2-\varphi_1)/2)\big|=R\,|\varphi_2-\varphi_1|$ : c'est bien la longueur d'un arc de cercle de rayon $R$ et d'angle $|\Delta\varphi|$. Pour une différence d'un degré, on retrouve $R\pi/180\approx111{,}2$ km. Le terme $\cos\varphi_1\cos\varphi_2$ est exactement le facteur de raccourcissement des méridiens.

C'est l'un des rares endroits de ce chapitre où le code est le plus court chemin vers la formule : quelques lignes suffisent, et NumPy calcule d'un coup les distances de tous les couples de villes si on lui donne des colonnes et des lignes (la diffusion du volume I, section 4.4).

```python
R = 6371.0   # rayon moyen de la Terre, en km

def haversine(lat1, lon1, lat2, lon2):
    """Distance de grand cercle en km (arguments en degrés ; NumPy diffuse sur les tableaux)."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(np.radians(lon2 - lon1) / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

print("1 degré de latitude            :", round(float(haversine(46.0, 4.0, 47.0, 4.0)), 1), "km")
print("1 degré de longitude à 45° N   :", round(float(haversine(45.0, 4.0, 45.0, 5.0)), 1), "km  (111,2 x cos 45° = 78,6)")
print("Ville A - Ville B              :", round(float(haversine(47.30, 3.20, 46.90, 4.60)), 1), "km")
```
<!--sortie-->
```text
1 degré de latitude            : 111.2 km
1 degré de longitude à 45° N   : 78.6 km  (111,2 x cos 45° = 78,6)
Ville A - Ville B              : 114.9 km
```

Le calcul à la main (114,9 km) et la formule donnent la même chose. Calculons maintenant la **matrice des distances** entre toutes les villes, un tableau de $10\times10$ valeurs symétrique, de diagonale nulle. Tout le chapitre utilisera des matrices de distances : on en lit ici l'essentiel.

```text
plus grande distance : Ville G - Ville J = 366 km
plus petite distance : Ville H - Ville I = 89 km
matrice symétrique : True | diagonale nulle : True
```

Sur quelques paires, mesurons l'erreur que l'on commet avec deux raccourcis tentants : (a) traiter les degrés comme des unités égales ($111{,}2\times$ la distance euclidienne en degrés), (b) projeter à plat avec la **projection équirectangulaire** centrée sur la latitude moyenne $\varphi_0$ des villes, $x=R(\lambda-\lambda_0)\cos\varphi_0$ et $y=R(\varphi-\varphi_0)$, puis prendre la distance euclidienne.

```text
paire  haversine_km  degres_bruts_km  erreur_%  equirect_km  erreur_eq_%
  A-B         114.9            161.9      40.9        117.1          1.9
  A-J         335.8            338.2       0.7        335.8         -0.0
  A-G         244.3            357.4      46.3        249.9          2.3
  G-J         366.3            424.6      15.9        365.8         -0.1
  C-H         242.7            347.5      43.2        244.0          0.6
```

Le raccourci « degrés bruts » **surestime** toujours (puisque $\cos\varphi<1$) : l'erreur va de 1 % à 46 % selon la direction du trajet. Elle est la plus forte pour A–G (46 %), un trajet presque exactement est-ouest, et la plus faible pour A–J (0,7 %), qui est surtout nord-sud. La projection équirectangulaire, elle, reste à moins de 2,5 % d'erreur sur toutes ces paires, ce qui est excellent pour une région de cette taille. C'est pour cela que, dans la pratique, on **projette** les coordonnées dans un système plan local, mesuré en mètres ou en kilomètres (le système UTM, par exemple, découpe la Terre en fuseaux de 6° de longitude), puis on travaille avec des distances euclidiennes ordinaires. Pour la suite de ce chapitre, nos zones font 100 km de côté : nous utiliserons directement des coordonnées planes **en kilomètres**.

> ⚠️ **À vol d'oiseau n'est pas « en camion ».** Les distances calculées ici sont des distances **à vol d'oiseau**. Entre deux villes, la distance **routière** est plus longue (parfois 30 % de plus), et le temps de trajet dépend de la route. Pour des questions de logistique, la bonne « distance » entre deux points est souvent un temps de parcours, qui n'est pas forcément symétrique ni euclidienne. Les outils de ce chapitre fonctionnent avec n'importe quelle distance… à condition que ses propriétés conviennent (nous y reviendrons aux sections 9.2 et 9.3).

### 9.1.4 Une carte sans fond de carte

Sans bibliothèque de cartographie, une carte est simplement un nuage de points $(x,y)$ avec **un rapport d'aspect correct** (un kilomètre vers l'est doit occuper la même longueur à l'écran qu'un kilomètre vers le nord). Pour des coordonnées en degrés, on y parvient en réglant le rapport d'aspect à $1/\cos\varphi_0$, ce qui revient à la projection équirectangulaire. Voyons-le avec les villes de la boutique, en dessinant un **symbole proportionnel** : la surface du disque est proportionnelle au nombre de clients de la ville (le fichier `clients.csv` du volume décrit des clients dans les villes A à E ; les clients des autres villes sont regroupés sous « Autre », sans position).


![Les dix villes fictives (points orange, nommées par leur lettre) et, pour les villes A à E, les effectifs de clients (disques bleus, surface proportionnelle). À gauche : un degré de longitude est dessiné aussi long qu'un degré de latitude, ce qui étire la carte d'est en ouest. À droite : le rapport d'aspect 1/cos(φ) rétablit les proportions.](figures/ch09-carte-villes.png)

Deux conseils de lecture. Les disques sont **proportionnels en surface** et non en rayon : si l'on doublait le rayon pour doubler la valeur, l'œil verrait une surface quatre fois plus grande, et le graphique mentirait. Et la carte de gauche, qui traite les degrés comme des unités égales (c'est ce que fait un `scatter(lon, lat)` avec `aspect="equal"`), déforme les distances : les villes y paraissent plus éloignées d'est en ouest qu'elles ne le sont.

Le même principe vaut pour les zones : pour afficher une valeur par zone (données surfaciques), on dessine une grille colorée (une « carte choroplèthe » dans le jargon). Deux jeux de données simulés servent de fil conducteur à la suite du chapitre.

| Jeu de données | Fichier | Contenu | Utilisé en |
|---|---|---|---|
| **Zones** (surfacique) | `donnees/ch09-zones.csv` | une grille $12\times12$ de 144 zones fictives de 5 km de côté ; ventes par habitant avec une autocorrélation spatiale *connue*, plus une variable témoin sans aucune structure spatiale | 9.2 |
| **Livraisons** (géostatistique) | `donnees/ch09-livraisons.csv` | 200 adresses dans un carré de 100 km de côté, avec le délai de livraison en jours, qui varie de façon continue dans l'espace | 9.3 |


![À gauche : ventes par habitant par zone (grille 12 × 12). À droite : délais de livraison observés en 200 adresses d'un carré de 100 km de côté.](figures/ch09-donnees-chapitre.png)

La carte de gauche ne ressemble pas à du « sel et poivre » : on y voit nettement une plage de faibles ventes au sud-est et des plages de fortes ventes au centre et au nord. La carte de droite est bien plus difficile à lire : des points de teintes voisines se côtoient, mais d'autres se mêlent, et l'œil hésite entre structure et hasard. C'est exactement pour cela qu'il faut **chiffrer** l'impression plutôt que de s'y fier. Mais avant, une mise en garde sur le dessin lui-même.

> ⚠️ **Les cartes mentent facilement.** Trois pièges classiques : (1) **la palette**, car une rampe séquentielle (clair → foncé) convient à une quantité ordonnée, et un arc-en-ciel invente des frontières qui n'existent pas ; (2) **les classes**, car découper une valeur continue en cinq paliers « égaux » ou en quantiles change complètement l'image ; (3) **la surface** : une grande zone peu peuplée attire l'œil autant qu'une petite zone très peuplée. Nous reviendrons sur ce dernier point dans le cahier (le *problème de l'unité spatiale modifiable*, exercice 9.7).

> ✅ **À retenir.**
> - L'espace casse l'**indépendance** : des observations proches se ressemblent, les erreurs-types usuelles sont trop optimistes.
> - Trois familles : **géostatistique** (valeurs en des points d'un champ continu), **surfacique** (une valeur par zone), **semis de points** (les positions sont aléatoires). On se demande d'abord : *qu'est-ce qui est aléatoire ?*
> - Un degré de longitude ne vaut pas un degré de latitude : $111{,}2\cos\varphi$ km contre 111,2 km. Pour des distances sur la Terre, on utilise **haversine** (ou on projette dans un plan local en kilomètres).
> - Une carte sans fond de carte reste utile : rapport d'aspect correct, symboles proportionnels **en surface**, palette séquentielle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.1, exercices 9.1 et 9.2.


## 9.2 Autocorrélation spatiale

> 💡 **Intuition.** La carte des ventes par zone (9.1) semble faite d'îlots. Pour savoir si cette impression est réelle, on pose une question simple : **la valeur d'une zone ressemble-t-elle à la moyenne de ses voisines ?** Si oui, les valeurs sont *positivement autocorrélées dans l'espace*. Si les zones voisines s'opposent (une forte entourée de faibles), l'autocorrélation est *négative*. Si le voisinage n'apprend rien sur la valeur, il n'y en a pas. L'indice de Moran transforme cette question en un nombre, et un test de permutation dit si ce nombre est plus grand que ce que le hasard produirait.

### 9.2.1 Définir « voisin » : la matrice de poids

Il n'existe pas de notion de voisinage « naturelle » : c'est à nous de la **choisir**, et ce choix s'écrit sous la forme d'une matrice $W$ de taille $n\times n$, la **matrice de poids** (ou de voisinage). Son coefficient $w_{ij}\ge0$ dit à quel point la zone $j$ compte comme voisine de la zone $i$, avec $w_{ii}=0$ (une zone n'est pas sa propre voisine). Les définitions usuelles :

- **Contiguïté « tour »** (*rook*) : $w_{ij}=1$ si les zones partagent une frontière (côté) ; **contiguïté « reine »** (*queen*) : si elles partagent une frontière *ou* un coin (sur une grille : 4 contre 8 voisins).
- **$k$ plus proches voisins** : $w_{ij}=1$ si $j$ est l'un des $k$ points les plus proches de $i$. Pratique pour des points (adresses), mais $W$ n'est plus symétrique.
- **Bande de distance** : $w_{ij}=1$ si la distance entre $i$ et $j$ ne dépasse pas un seuil $d$.
- **Inverse de la distance** : $w_{ij}=1/d_{ij}^{\alpha}$, où les points proches pèsent plus.

On **standardise** presque toujours par ligne : on divise chaque ligne par sa somme, de sorte que $\sum_j w_{ij}=1$. Alors $(Wz)_i$ est la **moyenne** des valeurs des voisins de $i$, ce qui rend les formules lisibles. Notons $S_0=\sum_{i,j}w_{ij}$ la somme de tous les poids (égale à $n$ après standardisation par ligne).

Un exemple minuscule que nous garderons pour les calculs à la main : une grille $3\times3$ de neuf zones numérotées de 0 à 8 ligne par ligne, avec la contiguïté « tour ».


Les coins ont 2 voisines, les bords 3, le centre 4 : au total $S_0=24$ liens orientés, soit 12 frontières communes comptées dans les deux sens. Pour obtenir la version standardisée par ligne, il suffit de diviser chaque ligne par sa somme.


### 9.2.2 L'indice de Moran

Soit $y_1,\dots,y_n$ les valeurs observées, $\bar y$ leur moyenne et $z_i=y_i-\bar y$ les valeurs **centrées**. L'**indice de Moran** est

$$I=\frac{n}{S_0}\;\frac{\sum_{i}\sum_{j}w_{ij}\,z_i\,z_j}{\sum_i z_i^2}.$$

Lisons-le morceau par morceau. Le numérateur $\sum_{ij}w_{ij}z_iz_j$ additionne, pour chaque paire de voisines, le **produit** de leurs écarts à la moyenne : il est positif quand les deux voisines sont du même côté de la moyenne (toutes deux hautes ou toutes deux basses) et négatif quand elles s'opposent. Le dénominateur $\sum z_i^2$ est la variance totale (à un facteur près), qui joue le rôle de **normalisation** : $I$ ressemble à un coefficient de corrélation entre une zone et ses voisines. Le facteur $n/S_0$ compense le nombre de liens.

> 💡 **Une lecture géométrique.** Avec une matrice standardisée par ligne ($S_0=n$), $I=\dfrac{z^\top Wz}{z^\top z}$. Mais $Wz$ est le vecteur des **moyennes des valeurs voisines**. Donc $I$ est exactement la **pente de la droite de régression** de « la moyenne de mes voisines » en fonction de « ma valeur » : le *diagramme de Moran* (nuage de $Wz$ contre $z$) montre ce que mesure l'indice. Une pente de 0,6 signifie : quand une zone est supérieure à la moyenne de 10, ses voisines le sont, en moyenne, de 6.

**Calcul à la main.** Sur la grille $3\times3$ avec des poids binaires ($S_0=24$), prenons les valeurs de 1 à 9 rangées ligne par ligne : une progression régulière, donc des voisines qui se ressemblent.

$$\begin{pmatrix}1&2&3\\4&5&6\\7&8&9\end{pmatrix},\qquad \bar y=5,\qquad z=\begin{pmatrix}-4&-3&-2\\-1&0&1\\2&3&4\end{pmatrix},\qquad \sum z_i^2=60.$$

La somme $\sum_{ij}w_{ij}z_iz_j$ compte chaque frontière deux fois, une fois dans chaque sens. Calculons les 12 produits sur les frontières, en les rangeant selon leur orientation.

- **Frontières horizontales** : $(-4)(-3)=12$ ; $(-3)(-2)=6$ ; $(-1)(0)=0$ ; $(0)(1)=0$ ; $(2)(3)=6$ ; $(3)(4)=12$ : total 36.
- **Frontières verticales** : $(-4)(-1)=4$ ; $(-1)(2)=-2$ ; $(-3)(0)=0$ ; $(0)(3)=0$ ; $(-2)(1)=-2$ ; $(1)(4)=4$ : total 4.

La somme sur les frontières vaut 40, donc $\sum_{ij}w_{ij}z_iz_j=2\times40=80$ et

$$I=\frac{9}{24}\times\frac{80}{60}=0{,}5 .$$

Dans l'autre sens, rangeons en **damier** : des 1 et des 9 qui alternent, de sorte que chaque zone n'ait que des voisines très différentes. Ici $\bar y=41/9$, les zones à 1 ont $z=-32/9$, celles à 9 ont $z=+40/9$, chaque frontière relie un 1 à un 9 (produit $-1280/81$), il y a 12 frontières donc $\sum_{ij}w_{ij}z_iz_j=-2\times12\times1280/81$, et $\sum z^2=11520/81$. Tous calculs faits, $I=\frac{9}{24}\times\frac{-30720}{11520}=-1$ : l'autocorrélation négative maximale. Vérifions les deux calculs, puis la version standardisée par ligne.

```python
def moran(y, W):
    """Indice de Moran de y pour la matrice de poids W (standardisée ou non)."""
    z = np.asarray(y, dtype=float) - np.mean(y)
    return len(z) / W.sum() * (z @ W @ z) / (z @ z)

progression = np.arange(1, 10)
damier = np.array([1, 9, 1, 9, 1, 9, 1, 9, 1], dtype=float)
print("progression 1..9, poids binaires     :", round(moran(progression, W3), 4))
print("damier,           poids binaires     :", round(moran(damier, W3), 4))
print("progression 1..9, poids standardisés :", round(moran(progression, W3s), 4))
print("E[I] sans autocorrélation, n = 9     :", round(-1 / (9 - 1), 4))
```
<!--sortie-->
```text
progression 1..9, poids binaires     : 0.5
damier,           poids binaires     : -1.0
progression 1..9, poids standardisés : 0.5556
E[I] sans autocorrélation, n = 9     : -0.125
```

Les valeurs 0,5 et −1 retrouvent nos calculs à la main. La version standardisée donne un nombre un peu différent : le **choix de $W$ fait partie du modèle** et il doit être indiqué avec le résultat.

> 📐 **Que vaut $I$ en l'absence d'autocorrélation ?** Sous l'hypothèse nulle « les valeurs sont échangeables » (aucune relation avec la position), toute permutation des $y_i$ sur les zones est aussi plausible qu'une autre. Pour $i\ne j$, $\mathbb E[z_iz_j]=\frac{1}{n(n-1)}\sum_{a\ne b}z_az_b=\frac{(\sum_a z_a)^2-\sum_a z_a^2}{n(n-1)}=-\frac{\sum_a z_a^2}{n(n-1)}$, car $\sum_a z_a=0$. Comme $w_{ii}=0$, il vient
>
> $$\mathbb E[I]=\frac{n}{S_0}\,\frac{\sum_{i\ne j}w_{ij}\,\mathbb E[z_iz_j]}{\sum z_i^2}=\frac{n}{S_0}\cdot S_0\cdot\frac{-1}{n(n-1)}=-\frac{1}{n-1}.$$
>
> Ce n'est pas exactement 0 (la contrainte « la moyenne des $z$ est nulle » induit une très légère corrélation négative), mais pour $n=144$ zones, $-1/143\approx-0{,}007$ : négligeable. Pour $n=9$, l'espérance vaut $-0{,}125$, ce qui est loin d'être négligeable : on **ne compare pas** un petit Moran à zéro mais à $-1/(n-1)$.

**Donner un sens à la valeur observée : deux voies.** Quelle valeur de $I$ est « grande » ? Il faut connaître la loi de $I$ sous l'hypothèse nulle.

1. **Approximation normale.** Sous une hypothèse de normalité des $y_i$, on connaît la variance de $I$ :
$$\operatorname{Var}(I)=\frac{n^2S_1-nS_2+3S_0^2}{(n^2-1)S_0^2}-\mathbb E[I]^2,$$
avec $S_1=\frac12\sum_{ij}(w_{ij}+w_{ji})^2$ et $S_2=\sum_i\big(\sum_j w_{ij}+\sum_j w_{ji}\big)^2$. On forme alors $z_I=(I-\mathbb E[I])/\sqrt{\operatorname{Var}(I)}$ et on le compare à une loi normale centrée réduite.
2. **Permutations.** Plus simple et sans hypothèse de loi : on **mélange** les valeurs sur les zones $B$ fois, on recalcule $I$ à chaque fois, et on regarde où tombe la valeur observée parmi ces $B$ valeurs. C'est le *test de permutation* du volume I (section 3.7.4), appliqué à l'espace. La p-valeur unilatérale pour une autocorrélation positive est $\dfrac{1+\#\{I^*\ge I_{\text{obs}}\}}{B+1}$.

Appliquons-les à nos 144 zones, avec la contiguïté « reine » (8 voisins). Les ventes ont été fabriquées par un **modèle autorégressif spatial** (SAR) : on part de bruits indépendants $e_i$ et on les propage dans l'espace par $z=(I-\rho W)^{-1}e$, de sorte que chaque zone est un reflet de ses voisines, avec une force $\rho=0{,}9$ (le générateur est dans `build/donnees_ch09.py`, et reconstruit pas à pas dans le cahier, application 9.2).


Nous disposons de deux variables : `ventes_hab` (structurée dans l'espace) et `ventes_bruit` (du bruit indépendant, **sans** structure spatiale ; sa moyenne et son écart-type sont proches de ceux de l'autre variable, sans être identiques). Cette deuxième variable est notre *témoin* : un bon indice doit y voir du hasard.

```text
    variable       I      E[I]  ecart_type       z  p_normale  p_permutation  sd_perm
  ventes_hab  0.6207 -0.006993     0.04429   14.17  6.802e-46         0.0001  0.04468
ventes_bruit -0.0214 -0.006993     0.04429 -0.3253     0.6275         0.6132  0.04445
```

La variable structurée a un indice de Moran nettement positif et une p-valeur proche de la plus petite que l'on puisse obtenir avec $B=9999$ permutations (jamais 0 : le $+1$ au numérateur représente la valeur observée elle-même). Le témoin, lui, est proche de $-1/(n-1)$ et sa p-valeur est élevée. Remarquons aussi que l'écart-type obtenu par permutations est voisin de celui de la formule normale : deux voies, une même conclusion.

> ⚠️ **L'indice ne vaut pas $\rho$.** Nous avons fabriqué les données avec $\rho=0{,}9$, mais $I\ne0{,}9$. Le paramètre $\rho$ d'un modèle SAR et l'indice de Moran mesurent la dépendance **sur des échelles différentes** : $\rho$ gouverne la façon dont un choc se propage de proche en proche, alors que $I$ résume la ressemblance moyenne entre voisines **directes**. Une forte propagation ($\rho$ proche de 1) produit de grandes plages, mais la ressemblance entre deux voisines immédiates reste partielle. Ne comparez jamais $I$ à une probabilité ou à un coefficient du modèle.

On voit mieux ce que mesure $I$ avec le **diagramme de Moran** (le nuage de la moyenne des voisines contre la valeur de la zone) et l'histogramme de la distribution nulle :


![À gauche : diagramme de Moran des ventes par habitant ; la pente de la droite est l'indice de Moran. À droite : distribution de I quand on mélange les valeurs au hasard sur les zones (hypothèse nulle) et valeur observée.](figures/ch09-moran.png)

La pente du diagramme est **égale** à l'indice de Moran, comme annoncé. L'histogramme de droite montre la loi de $I$ quand les valeurs sont distribuées au hasard : centrée sur un nombre proche de zéro, avec un étalement de l'ordre de 0,05. La valeur observée est loin à droite de cette loi : le hasard ne produit pas un tel alignement.

**La sensibilité au choix de $W$.** Le résultat dépend-il de notre définition du voisinage ? Recalculons $I$ avec cinq définitions, construites à partir des **distances** entre les centres des zones, ce qui est la façon de faire pour des points dans l'espace quelconques.

```text
                definition  voisins_moyens     I  I_temoin  p_permutation
   tour (distance <= 5 km)           3.667 0.627    -0.034          0.001
reine (distance <= 7,1 km)           7.028 0.621    -0.021          0.001
            bande de 10 km          10.361 0.572     0.009          0.001
    4 plus proches voisins           4.000 0.618    -0.013          0.001
    8 plus proches voisins           8.000 0.607     0.011          0.001
```

Tous les choix donnent un indice nettement positif et une p-valeur minimale, et le témoin reste proche de zéro. Mais **la valeur de $I$ change** : plus on élargit le voisinage, plus on mélange des zones qui se ressemblent peu, et plus l'indice diminue. Retenons-en une règle : une conclusion du type « il y a de l'autocorrélation » ne devrait pas dépendre du choix de $W$ ; la **valeur** de $I$, elle, n'a de sens que pour un $W$ donné. On indique donc toujours la définition choisie.

### 9.2.3 L'indice de Geary

L'indice de Moran compare chaque zone **à la moyenne** (par les écarts $z_i$). Celui de Geary compare directement les zones voisines **entre elles** :

$$C=\frac{n-1}{2S_0}\;\frac{\sum_{i}\sum_{j}w_{ij}\,(y_i-y_j)^2}{\sum_i z_i^2}.$$

Le numérateur est la somme des carrés des **différences** entre voisines, qui sera petite si les voisines se ressemblent. Sans autocorrélation, $\mathbb E[C]=1$. Une valeur **inférieure à 1** indique une autocorrélation positive ; supérieure à 1, une autocorrélation négative. L'échelle est donc inversée par rapport à Moran. Geary est plus sensible aux **différences locales** (à l'échelle d'une paire de voisines) alors que Moran, qui passe par la moyenne globale, est plus sensible à la structure d'ensemble.

> 📐 **Le lien avec le variogramme (9.3).** Le terme $\frac12(y_i-y_j)^2$ est exactement la *semi-variance* d'une paire, la brique du variogramme. L'indice de Geary est donc, à une normalisation près, une moyenne de semi-variances **sur les paires voisines** divisée par la variance totale. C'est une première approximation du variogramme à une seule distance.

```text
    variable      C  moyenne_perm  p_perm (C petit)
  ventes_hab 0.3950        1.0033            0.0010
ventes_bruit 0.9909        0.9997            0.4030
```

Les deux indices racontent la même histoire : la variable structurée a un $C$ bien inférieur à 1, le témoin est proche de 1.

### 9.2.4 Où sont les îlots ? Les indices locaux (LISA)

Un seul nombre pour toute la carte ne dit pas **où** se trouvent les îlots. Les **indicateurs locaux d'association spatiale** (LISA) décomposent l'indice de Moran en une contribution par zone :

$$I_i=\frac{z_i}{m_2}\sum_j w_{ij}\,z_j,\qquad m_2=\frac1n\sum_k z_k^2 .$$

Avec une matrice standardisée par ligne, la somme des $I_i$ vaut exactement $n\,I$. Chaque $I_i$ est positif quand la zone $i$ et ses voisines sont du même côté de la moyenne. Le signe de $z_i$ et celui de la moyenne voisine $Wz_i$ donnent les **quatre quadrants** du diagramme de Moran :

- **HH** : zone haute entourée de zones hautes (un **îlot de fortes valeurs**) ;
- **LL** : zone basse entourée de zones basses (un îlot de faibles valeurs) ;
- **HL / LH** : une zone haute entourée de basses (ou l'inverse), des **valeurs atypiques** locales.

Pour savoir si un $I_i$ est significatif, on utilise une **permutation conditionnelle** : on garde la valeur de la zone $i$ fixe, on mélange les autres valeurs sur les autres zones, et on recalcule $I_i$. Mais attention : nous faisons **144 tests à la fois**. Comme au volume I (section 3.5.5), sans correction nous attendrions environ 7 faux positifs (5 % de 144) même sur des données sans structure ; nous utiliserons la procédure de **Benjamini-Hochberg**.

```text
    variable  somme_Ii/n  I_global  p<0.05 brut  significatifs (BH)  HH  LL  HL  LH
  ventes_hab      0.6207    0.6207           49                  35  11  22   0   2
ventes_bruit     -0.0214   -0.0214            5                   0   0   0   0   0
```

La première colonne vérifie la propriété annoncée : la moyenne des $I_i$ est bien l'indice de Moran global. Sur le témoin, 5 zones sur 144 (3 %, soit à peu près les 5 % attendus du hasard) sortent avec la p-valeur brute : c'est le prix des tests multiples. La correction de Benjamini-Hochberg les écarte **toutes** (0 zone significative). Sur la variable structurée, 49 zones sont significatives avant correction et 35 après : 11 îlots de fortes valeurs (HH), 22 de faibles valeurs (LL) et 2 valeurs atypiques (LH). Regardons la carte des zones significatives.


![Carte des indicateurs locaux de Moran significatifs (Benjamini-Hochberg à 5 %). À gauche, les ventes par habitant : des îlots de fortes (rouge) et de faibles (bleu) valeurs. À droite, le témoin sans structure spatiale : presque rien n'est significatif.](figures/ch09-lisa.png)

La carte de gauche **localise** les îlots : l'indice global disait *qu'il y en a*, les indices locaux disent *où*. À droite, le témoin est quasiment vide.

> ⚠️ **Deux précautions.** (1) Les indices locaux ne sont **pas indépendants** (zones voisines partagent des voisines), donc le taux de faux positifs effectif est mal maîtrisé même avec la correction de Benjamini-Hochberg : on considère les zones signalées comme des **pistes à examiner**, pas comme des découvertes. (2) Les zones **en bordure** de la carte ont moins de voisines : leurs indices sont plus bruités (nous le mesurons dans le cahier, exercice 9.8).

### 9.2.5 Pourquoi cela compte : la régression qui voit des relations qui n'existent pas

Revenons à l'avertissement de 9.1.1 : l'autocorrélation rend les erreurs-types usuelles **trop petites**. Mesurons-le. Nous simulons **deux variables sans aucun lien** (deux champs spatiaux SAR indépendants, avec la même force $\rho=0{,}9$ que plus haut), nous régressons l'une sur l'autre par moindres carrés ordinaires et nous testons la pente à 5 %. Si la méthode est honnête, nous devrions rejeter à tort dans environ **5 %** des cas. Nous recommençons 1 000 fois.

```text
MCO : proportion de rejets à 5 % alors qu'il n'y a AUCUN lien : 0.459
variance d'une zone : 3.9 | variance de la moyenne de 144 zones : 0.706 | si indépendantes, ce serait 0.027
nombre efficace d'observations indépendantes : 5.5 sur 144
```

Le résultat est sans appel : au lieu des 5 % promis, le test usuel rejette à tort dans **46 %** des cas, presque une fois sur deux. Et pour estimer une moyenne, nos 144 zones valent environ **5,5 observations indépendantes** : la variance de la moyenne est de 0,71, contre 0,027 si les zones étaient indépendantes. Le test usuel suppose des erreurs indépendantes ; ici elles ne le sont pas, et l'erreur-type de la pente est sous-estimée d'un facteur important.

> 💡 **Le remède, dans son principe.** Il faut tenir compte de la dépendance dans le calcul. Si l'on **connaissait** la structure de covariance $\Sigma$ des erreurs, on appliquerait les **moindres carrés généralisés** (MCG), c'est-à-dire des moindres carrés sur des données *blanchies*. Pour notre modèle SAR, le blanchiment est explicite : multiplier le vecteur $y$ par $(I-\rho W)$ « défait » la propagation. Vérifions que cela rétablit le niveau du test, en supposant ici $\rho$ connu (c'est le cas idéal ; en pratique on l'estime).

```text
MCG avec rho connu : proportion de rejets à 5 % : 0.053
Moran des résidus MCO (première paire) : 0.425 | p-valeur par permutation : 0.001
```

Avec les moindres carrés généralisés, le niveau du test retombe à 5,3 %, tout près des 5 % annoncés. Et, comme le montre la dernière ligne, il existe un **signal d'alarme** simple pour une analyse réelle : calculer l'indice de Moran des **résidus** du modèle. S'il est significatif, les erreurs ne sont pas indépendantes et les erreurs-types usuelles sont à écarter.

> 💡 **En pratique.** On ne connaît pas $\rho$ : on l'estime avec un **modèle autorégressif spatial** (le *spatial lag* ou le *spatial error model*, estimés par maximum de vraisemblance), ou l'on modélise la covariance par un variogramme (section 9.3, krigeage universel), ou l'on utilise des **erreurs-types robustes par blocs spatiaux**. Les outils exacts sortent du cadre de ce chapitre, mais le message est général : *si vos observations sont proches dans l'espace, testez l'autocorrélation des résidus avant de lire vos p-valeurs.*

> ✅ **À retenir.**
> - Pour parler d'autocorrélation, il faut **définir le voisinage** : une matrice de poids $W$ (contiguïté, $k$ voisins, bande de distance), presque toujours standardisée par ligne. Ce choix fait partie du résultat.
> - **Indice de Moran** : $I=\frac{n}{S_0}\frac{\sum w_{ij}z_iz_j}{\sum z_i^2}$. Avec $W$ standardisée, c'est la pente de « moyenne des voisines » contre « valeur de la zone ». Sous l'hypothèse nulle, $\mathbb E[I]=-1/(n-1)$ ; on le teste par **permutations**.
> - **Geary** ($\mathbb E[C]=1$, $C<1$ pour une autocorrélation positive) est plus sensible aux différences locales.
> - Les **indices locaux** (LISA) disent *où* sont les îlots (HH, LL) et les valeurs atypiques (HL, LH) ; avec 144 tests, il faut **corriger** (Benjamini-Hochberg).
> - Ignorer l'autocorrélation fait **rejeter à tort** bien plus souvent que 5 % : testez l'indice de Moran des résidus avant de croire une p-valeur.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.2 et 9.3, exercices 9.3, 9.4, 9.7, 9.8 et 9.9.


## 9.3 Variogramme et krigeage

> 💡 **Intuition.** La gérante veut promettre un délai à une cliente d'un quartier où personne n'a encore été livré. Que peut-on dire ? Les livraisons **proches** de cette adresse sont informatives, celles qui sont loin le sont moins, et deux livraisons voisines l'une de l'autre se répètent (elles apportent à peu près la même information). Le **variogramme** mesure à quelle vitesse la ressemblance entre deux mesures s'estompe quand la distance augmente. Le **krigeage** s'en sert pour fabriquer, en tout point, la **meilleure moyenne pondérée** des mesures voisines, avec une **marge d'erreur**.

### 9.3.1 De la corrélation entre voisines à une fonction de la distance

Au 9.2, la ressemblance entre voisines était résumée par un seul nombre (Moran) pour une définition de voisinage fixée. En géostatistique, on décrit toute la courbe : *comment la ressemblance dépend de la distance $h$ qui sépare deux points*.

Le modèle de base écrit la mesure en un point $s$ du plan comme la somme d'un niveau moyen, d'un champ qui varie régulièrement et d'un bruit de mesure :

$$Z(s)=\mu+S(s)+\varepsilon(s).$$

On suppose que le champ est **stationnaire** : sa moyenne $\mu$ est la même partout et la dépendance entre deux points ne dépend que du **vecteur** qui les sépare, pas de l'endroit où ils sont. (L'hypothèse minimale, dite *intrinsèque*, ne demande que la stationnarité des **différences** $Z(s+h)-Z(s)$.) On définit alors le **semi-variogramme**

$$\gamma(h)=\tfrac12\,\mathbb E\big[(Z(s+h)-Z(s))^2\big],$$

la moitié de l'écart quadratique moyen entre deux mesures séparées par $h$. Il est nul à l'origine ($\gamma(0)=0$) et croît d'ordinaire avec $h$ : plus deux points sont éloignés, moins ils se ressemblent. Trois nombres décrivent la courbe :

- la **pépite** (*nugget*) $c_0$ : la valeur de $\gamma$ juste après 0. Elle regroupe le bruit de mesure et les variations à une échelle plus petite que la distance minimale entre points. Même deux mesures très proches ne se ressemblent pas parfaitement ;
- le **palier** (*sill*) : la valeur de $\gamma$ quand la courbe se stabilise. C'est la variance totale du processus ($c_0+c$) ;
- la **portée** (*range*) $a$ : la distance au-delà de laquelle deux points ne se ressemblent plus davantage qu'au hasard : deux points plus éloignés que la portée sont (presque) indépendants.

> 📐 **Lien avec la covariance.** Si le processus est de variance finie $C(0)$ et de covariance $C(h)=\operatorname{Cov}(Z(s),Z(s+h))$, alors
> $$\gamma(h)=\tfrac12\operatorname{Var}\big(Z(s+h)-Z(s)\big)=\tfrac12\big[C(0)+C(0)-2C(h)\big]=C(0)-C(h).$$
> Le variogramme est donc la covariance « retournée » : $\gamma$ monte quand $C$ descend, et le palier vaut $C(0)$. Le variogramme est plus général (il existe aussi quand la variance est infinie) et il se **déduit directement des données**, ce qui explique qu'il soit l'outil standard.

**Un calcul à la main.** Quatre mesures alignées aux abscisses 0, 1, 2 et 3 km, de valeurs 2, 3, 5 et 4. À la distance 1 km, il y a trois paires (0-1, 1-2, 2-3) dont les écarts au carré valent $(3-2)^2=1$, $(5-3)^2=4$ et $(4-5)^2=1$ : $\hat\gamma(1)=\frac{1+4+1}{2\times3}=1{,}0$. À 2 km, deux paires (0-2, 1-3) : $\frac{(5-2)^2+(4-3)^2}{2\times2}=\frac{9+1}{4}=2{,}5$. À 3 km, une seule paire : $\hat\gamma(3)=\frac{(4-2)^2}{2}=2{,}0$. Le diviseur est **deux fois le nombre de paires**, d'où le « semi » dans le mot.

### 9.3.2 Le variogramme empirique

Avec $n$ points, l'estimateur classique de la semi-variance à la distance $h$ est

$$\hat\gamma(h)=\frac{1}{2N(h)}\sum_{(i,j)\in N(h)}(z_i-z_j)^2,$$

où $N(h)$ est l'ensemble des paires dont la distance est « à peu près » $h$ (on découpe les distances en **classes** de largeur fixe) et $N(h)$ leur nombre. Nous l'avons programmé (cahier, application 9.4) et validé d'abord sur les quatre points ci-dessus : voici sa sortie, avec le nombre de paires de chaque classe.

```text
  h  gamma  paires
1.0    1.0       3
2.0    2.5       2
3.0    2.0       1
```

Les trois lignes redonnent nos calculs à la main : 1,0 ; 2,5 ; 2,0. Passons aux 200 livraisons. Elles ont été fabriquées par un générateur (`build/donnees_ch09.py`, reconstruit dans le cahier, application 9.4) dont les réglages sont la **vérité** que nous allons chercher à retrouver (nous ne la regarderons qu'après l'analyse) : un champ aléatoire gaussien stationnaire de covariance exponentielle, observé avec un bruit de mesure. Les 200 délais ont une moyenne de 4,27 jours et une variance de 1,21 jour².


Calculons le variogramme empirique de ces données, avec des classes de 5 km jusqu'à 50 km (la moitié de la taille du domaine : au-delà, les paires deviennent rares et dépendent de la forme du domaine, c'est la règle de pouce usuelle).

```text
     h  gamma  paires
 3.328  0.473     139
 7.817  0.784     384
12.655  1.057     683
17.572  1.265     849
22.550  1.250     992
27.537  1.190    1193
32.569  1.150    1278
37.539  1.211    1237
42.466  1.373    1332
47.408  1.426    1343
```

Le tableau montre un variogramme qui **monte puis se stabilise** : le comportement attendu d'un processus stationnaire. Remarquons aussi que le nombre de paires croît avec la distance (il y a bien plus de paires éloignées que de paires proches), si bien que les premières classes, justement les plus importantes pour estimer la pépite, sont aussi les moins fiables.

> ⚠️ **Le variogramme empirique est bruité.** Chaque point $\hat\gamma(h)$ est une moyenne de carrés d'écarts, un estimateur sensible aux valeurs extrêmes et fortement **corrélé** d'une classe à l'autre (les mêmes points participent à beaucoup de paires). Le choix de la largeur des classes est un compromis : des classes étroites donnent une courbe précise mais bruitée, des classes larges lissent la forme près de l'origine. Il existe des estimateurs robustes (Cressie-Hawkins, qui utilise la racine des écarts absolus), mais l'estimateur classique reste la référence pour des données à peu près gaussiennes.

### 9.3.3 Modèles de variogramme et ajustement

Une courbe en escalier de 10 points ne peut pas servir directement : il faut une **fonction** $\gamma(h)$ pour toute distance $h$, et pas n'importe laquelle : elle doit garantir qu'une variance calculée avec elle n'est jamais négative (on dit que $-\gamma$ doit être *conditionnellement définie positive*). On ne choisit donc pas une courbe au hasard : on utilise une famille de modèles **valides**. Trois sont standard, avec $c_0$ la pépite, $c$ le palier partiel (palier total $c_0+c$) et $a$ le paramètre de portée :

| Modèle | $\gamma(h)$ pour $h>0$ | Portée pratique | Allure près de l'origine |
|---|---|---|---|
| **Sphérique** | $c_0+c\left(\frac{3h}{2a}-\frac{h^3}{2a^3}\right)$ si $h<a$, sinon $c_0+c$ | $a$ (atteinte exactement) | linéaire |
| **Exponentiel** | $c_0+c\,(1-e^{-h/a})$ | $3a$ (95 % du palier) | linéaire |
| **Gaussien** | $c_0+c\,(1-e^{-(h/a)^2})$ | $\sqrt3\,a$ | **parabolique** (très lisse) |

La **portée pratique** est la distance où le variogramme atteint 95 % de son palier. Elle vaut $a$ pour le modèle sphérique, $3a$ pour l'exponentiel (qui n'atteint jamais exactement son palier) et $\sqrt 3\,a$ pour le gaussien. Le comportement près de l'origine traduit la régularité du phénomène : un variogramme linéaire correspond à un champ continu mais rugueux, un variogramme parabolique à un champ très lisse.

Pour ajuster un modèle, on cherche $(c_0,c,a)$ qui rapprochent le modèle des points empiriques par **moindres carrés pondérés**. Les classes contenant beaucoup de paires sont plus fiables et celles où $\gamma$ est petit ont une variance plus faible, d'où les poids (de Cressie) $N(h)/\gamma_{\text{modèle}}(h)^2$ : on minimise $\sum_k N_k\big(\hat\gamma_k/\gamma_k(\theta)-1\big)^2$.

```text
     modele  pepite  palier_partiel  palier_total  param_a  portee_pratique_km  critere
  sphérique   0.215           1.065         1.280   20.792              20.792   48.096
exponentiel   0.038           1.277         1.315    8.136              24.407   47.196
   gaussien   0.390           0.893         1.283   10.436              18.075   48.425
```

Les trois modèles proposent un **palier total** voisin (entre 1,28 et 1,32), mais des décompositions différentes entre pépite et portée : le modèle exponentiel trouve presque une pépite nulle et une portée pratique d'environ 24 km, le gaussien une pépite de 0,39 et une portée de 18 km. Leurs **critères** d'ajustement sont très proches (47,2 pour l'exponentiel, 48,1 et 48,4 pour les deux autres) : l'exponentiel est légèrement meilleur, mais **les données ne permettent pas de trancher** entre les formes. Regardons-les sur la figure.


![Variogramme empirique (points, taille proportionnelle au nombre de paires) et trois modèles ajustés. La ligne pointillée est la variance empirique des données, voisine du palier.](figures/ch09-variogramme.png)

> 🧪 **La vérité terrain.** Les données sont simulées : nous connaissons la bonne réponse. C'est un champ de covariance exponentielle $C(h)=1{,}0\,e^{-h/12}$, soit un palier partiel $c=1{,}0$ et un paramètre $a=12$ (portée pratique 36 km), observé avec une **pépite** de $0{,}4$ (palier total $1{,}4$). Comparons avec la ligne « exponentiel » du tableau : le **palier total** est bien retrouvé (1,32 contre 1,4), mais la **pépite** est très sous-estimée (0,04 contre 0,4) et la **portée pratique** aussi (24 km contre 36 km). Ce qui est facile à estimer, c'est la variance totale ; ce qui est difficile, c'est sa répartition entre bruit de mesure et dépendance spatiale. La suite montre que ce n'est pas une particularité de notre tirage.

**Cet ajustement est-il typique ?** Une seule série de 200 mesures est un seul tirage ; il est légitime de se demander ce qui se passerait avec d'autres tirages du même processus. Faisons l'expérience : nous répétons la simulation avec 30 graines différentes, nous réajustons à chaque fois le modèle exponentiel et nous regardons la dispersion des paramètres estimés.

```text
                 vérité  médiane  10e perc.  90e perc.
pepite              0.4     0.35       0.10       0.54
palier_partiel      1.0     1.04       0.78       1.38
param_a            12.0     9.64       5.29      17.33
portee_pratique    36.0    28.92      15.88      52.00
palier_total        1.4     1.38       1.05       1.63
```

> ⚠️ **Ce qu'il faut retenir de cette expérience.** Sur 30 tirages, le palier total est estimé avec une assez bonne précision (médiane 1,38 pour une vérité de 1,4), mais la pépite varie de 0,10 à 0,54 (entre le 10e et le 90e percentile) et la portée pratique de 16 à 52 km, pour des vérités de 0,4 et 36 km. La **médiane** de la portée pratique (29 km) est elle-même inférieure à la vérité : l'ajustement a tendance à la sous-estimer. Notre tirage (pépite 0,04, portée 24 km) est dans la queue basse de la distribution, sans être aberrant. Même avec 200 points, les paramètres du variogramme sont donc **peu précis** : la pépite et la portée sont particulièrement difficiles à identifier, parce que l'une et l'autre se jouent dans les toutes premières classes de distance, qui contiennent peu de paires. Ce n'est pas un défaut du programme, c'est la nature du problème. Deux conséquences pratiques : (1) ne jamais donner un variogramme ajusté comme un fait certain, (2) comme nous le verrons, le **krigeage** est heureusement assez peu sensible aux petites erreurs de variogramme.

### 9.3.4 Le krigeage : la meilleure moyenne pondérée

Nous voulons prédire $Z(s_0)$ en un point $s_0$ où nous n'avons pas mesuré. Cherchons un prédicteur de la forme d'une **moyenne pondérée** des $n$ mesures :

$$\hat Z(s_0)=\sum_{i=1}^n\lambda_i\,Z(s_i),\qquad \sum_i\lambda_i=1.$$

La contrainte $\sum\lambda_i=1$ garantit que le prédicteur est **sans biais** quand la moyenne $\mu$ est constante *mais inconnue* (c'est le **krigeage ordinaire**) : $\mathbb E[\hat Z]=\mu\sum\lambda_i=\mu$. Parmi tous les poids possibles, nous voulons ceux qui **minimisent l'erreur quadratique moyenne** $\mathbb E[(\hat Z(s_0)-Z(s_0))^2]$.

> 📐 **Dérivation.** Grâce à la contrainte, l'erreur se réécrit $Z(s_0)-\hat Z(s_0)=\sum_i\lambda_i\big(Z(s_0)-Z(s_i)\big)$ : c'est une combinaison d'**accroissements**, dont on connaît les moments grâce au variogramme. Pour deux accroissements $a=Z(s_0)-Z(s_i)$ et $b=Z(s_0)-Z(s_j)$, on a $ab=\tfrac12\big[a^2+b^2-(a-b)^2\big]$ et $a-b=Z(s_j)-Z(s_i)$, donc $\mathbb E[ab]=\gamma_{i0}+\gamma_{j0}-\gamma_{ij}$, en notant $\gamma_{ij}=\gamma(\|s_i-s_j\|)$. On en déduit, en utilisant $\sum\lambda=1$ :
>
> $$\sigma_K^2(\lambda)=\sum_i\sum_j\lambda_i\lambda_j(\gamma_{i0}+\gamma_{j0}-\gamma_{ij})=2\sum_i\lambda_i\gamma_{i0}-\sum_i\sum_j\lambda_i\lambda_j\gamma_{ij}=2\lambda^\top\gamma_0-\lambda^\top\Gamma\lambda,$$
>
> où $\Gamma=(\gamma_{ij})$ et $\gamma_0=(\gamma_{i0})_i$. On minimise sous la contrainte $\mathbf 1^\top\lambda=1$ avec un **multiplicateur de Lagrange** $m$ (comme au volume I, section 1.3.5) : $\mathcal L=2\lambda^\top\gamma_0-\lambda^\top\Gamma\lambda-2m(\mathbf 1^\top\lambda-1)$. En annulant le gradient en $\lambda$ : $\gamma_0-\Gamma\lambda-m\mathbf 1=0$. Le système à résoudre est donc
>
> $$\begin{pmatrix}\Gamma&\mathbf 1\\\mathbf 1^\top&0\end{pmatrix}\begin{pmatrix}\lambda\\m\end{pmatrix}=\begin{pmatrix}\gamma_0\\1\end{pmatrix},\qquad\boxed{\hat Z(s_0)=\lambda^\top Z},\qquad\boxed{\sigma_K^2=\lambda^\top\gamma_0+m}.$$
>
> (Pour la variance : $\Gamma\lambda=\gamma_0-m\mathbf 1$ donne $\lambda^\top\Gamma\lambda=\lambda^\top\gamma_0-m$, donc $\sigma_K^2=2\lambda^\top\gamma_0-(\lambda^\top\gamma_0-m)=\lambda^\top\gamma_0+m$.)

Trois choses à remarquer dans ce système. (1) Les poids dépendent **des distances entre les points de mesure** (la matrice $\Gamma$, qui sait que deux points voisins sont redondants) *et* de la distance de chaque point à la cible ($\gamma_0$) : on n'est pas une simple pondération par l'inverse de la distance. (2) La variance de krigeage $\sigma_K^2$ ne dépend **que de la géométrie et du variogramme**, pas des valeurs mesurées. (3) Le système est linéaire de taille $(n+1)$ : un seul appel à `numpy.linalg.solve`.

**Un exemple à la main.** Prenons le cas le plus simple : une dimension, un variogramme **linéaire** $\gamma(h)=h$, deux points de mesure à $x=0$ (valeur 10) et $x=3$ (valeur 16), et une cible à $x=1$. Alors $\Gamma=\begin{pmatrix}0&3\\3&0\end{pmatrix}$ et $\gamma_0=(1,2)^\top$. Le système s'écrit $3\lambda_2+m=1$, $3\lambda_1+m=2$, $\lambda_1+\lambda_2=1$. En soustrayant les deux premières équations, $3(\lambda_1-\lambda_2)=1$, donc $\lambda_1=\tfrac23$, $\lambda_2=\tfrac13$ et $m=0$. La prédiction vaut $\tfrac23\times10+\tfrac13\times16=12$ et la variance $\lambda^\top\gamma_0+m=\tfrac23+\tfrac23+0=\tfrac43$. Ce résultat porte un enseignement : **dans ce cas particulier, le krigeage est l'interpolation linéaire** (de 10 à 16 en trois km, soit 12 à 1 km). Vérifions-le en quelques lignes : le système bordé se construit par blocs et se résout d'un seul appel.


```python
x, z1, x0 = np.array([0.0, 3.0]), np.array([10.0, 16.0]), 1.0           # deux mesures, une cible
gam = lambda h: np.abs(h)                                                 # variogramme linéaire  γ(h) = h
A = np.block([[gam(x[:, None] - x[None, :]), np.ones((2, 1))],            # matrice bordée  [[Γ, 1], [1ᵀ, 0]]
              [np.ones((1, 2)), np.zeros((1, 1))]])
sol = np.linalg.solve(A, np.append(gam(x - x0), 1.0))                     # second membre  (γ0, 1)
lam, m = sol[:2], sol[2]
print("poids :", lam.round(4), "| prédiction :", round(float(lam @ z1), 4), "| variance :", round(float(lam @ gam(x - x0) + m), 4))
```
<!--sortie-->
```text
poids : [0.6667 0.3333] | prédiction : 12.0 | variance : 1.3333
```

Nous retrouvons les poids $\frac23,\frac13$, la prédiction 12 et la variance $\frac43$ du calcul à la main. Revenons aux livraisons, avec le modèle **exponentiel** ajusté. Prédisons d'abord en un point précis, par exemple l'adresse $(40,\,60)$, et examinons les poids.

```text
prédiction en (40, 60) : 4.75 jours | écart-type de krigeage : 0.77 jour
somme des poids : 1.0 | poids négatifs : 29 sur 200 | plus petit : -0.026 | plus grand : 0.532
 distance_km  poids  delai
       2.724  0.532  4.753
       4.740  0.158  4.849
       6.420  0.105  3.997
       8.405  0.102  5.156
      11.762  0.054  5.439
      11.745  0.032  3.196
```

Les poids les plus forts reviennent aux livraisons **les plus proches** de la cible (le plus grand, 0,53, est pour celle qui est à 2,7 km), leur somme vaut 1, et 29 des 200 poids sont **négatifs** (mais très petits, comme l'indique le plus petit d'entre eux) : ce n'est pas une anomalie. Quand un point en cache d'autres derrière lui (*effet d'écran*), le krigeage peut donner un poids légèrement négatif au point masqué. Une moyenne ordinaire ne le ferait jamais.

> 💡 **Le krigeage est un interpolateur exact.** Si la cible est l'un des points de mesure, le système donne le poids 1 à ce point et 0 aux autres : la prédiction redonne la mesure et la variance est nulle. C'est vrai ici même avec une pépite, parce que nous la traitons comme une propriété de la mesure (le point mesuré est connu). Si au contraire la pépite représente un bruit que l'on veut *filtrer*, on utilise une variante qui lisse au lieu d'interpoler (non traitée ici).

### 9.3.5 Une carte de prédiction et une carte d'incertitude

Prédisons maintenant en chacun des 625 points d'une grille régulière (le jeu `verite` contient aussi le **vrai** champ en ces points, grâce à la simulation) et comparons à trois alternatives : la **moyenne globale**, la méthode de l'**inverse de la distance au carré** (IDW, une moyenne pondérée sans variogramme) et le krigeage.

```text
RMSE par rapport au VRAI champ sur les 625 points de la grille :
  moyenne globale          : 0.916
  inverse de la distance^2 : 0.671
  krigeage ordinaire       : 0.645
écart-type de krigeage : de 0.35 à 1.08 jour (moyenne 0.77)
```

Dessinons le vrai champ, la prédiction par krigeage et l'écart-type de krigeage.


![De gauche à droite : le vrai champ de délais (connu car simulé), la prédiction par krigeage ordinaire à partir des 200 mesures, et l'écart-type d'erreur de krigeage (les points noirs sont les 200 livraisons mesurées). L'incertitude est faible près des mesures et monte dans les zones qui en sont éloignées.](figures/ch09-krigeage.png)

Contre le vrai champ, le krigeage obtient une erreur quadratique de 0,645 jour, contre 0,916 pour la moyenne globale (30 % de moins) et 0,671 pour l'inverse de la distance : l'IDW fait presque aussi bien (4 % d'écart), ce qui rappelle qu'une moyenne pondérée bien choisie est déjà un bon prédicteur. L'avantage décisif du krigeage n'est pas là, mais dans la carte de droite. La carte du centre reproduit les grandes structures du vrai champ, en plus lisse (le krigeage est une moyenne : il **lisse** et sous-estime donc les extrêmes). La carte de droite est une originalité du krigeage : elle dit **où la prédiction est fiable**, avant même d'avoir livré. Dans la pratique, c'est la carte qui guide le choix des **prochains points de mesure** : on va mesurer là où l'incertitude est la plus grande.

De quoi dépend cette incertitude ? Mesurons-le : pour chaque point de la grille, la distance au point de mesure le plus proche, et la façon dont l'écart-type de krigeage évolue avec elle, puis une comparaison entre les points proches d'un bord du domaine et les autres.

```text
corrélation entre l'écart-type de krigeage et la distance au point le plus proche : 0.924
  points de grille à 0-2 km d'une mesure : 145 points, écart-type moyen 0.59 jour
  points de grille à 2-4 km d'une mesure : 252 points, écart-type moyen 0.77 jour
  points de grille à 4-6 km d'une mesure : 173 points, écart-type moyen 0.87 jour
  points de grille à 6-10 km d'une mesure :  54 points, écart-type moyen 0.97 jour
écart-type moyen à moins de 8 km d'un bord : 0.779 | à l'intérieur : 0.770
```

L'écart-type de krigeage est presque une fonction croissante de la distance à la mesure la plus proche (corrélation de 0,92) : de 0,59 jour à moins de 2 km d'une mesure à 0,97 jour entre 6 et 10 km. Aucun **effet de bord** n'apparaît ici (0,78 jour près des bords contre 0,77 à l'intérieur) : avec 200 points répartis uniformément sur le carré, les bords sont aussi bien couverts que le centre. Il se manifesterait avec un échantillonnage plus clairsemé ou concentré au centre, où les points du bord n'auraient de voisins que d'un seul côté.


### 9.3.6 Évaluer honnêtement : la validation croisée

Comparer au vrai champ n'est possible que sur données simulées. Dans une vraie étude, on évalue par **validation croisée** : on retire une partie des mesures, on les prédit avec le reste, et on compare. Notre fichier contient une colonne `pli` (cinq plis de 40 points). Pour être honnête, il faut **réajuster le variogramme à chaque pli, uniquement sur les données d'entraînement** : sinon, le variogramme aurait « vu » les points à prédire.

```text
          RMSE (jours)  biais moyen
moyenne          1.097        0.000
IDW              0.994        0.040
krigeage         0.969        0.023

résidus standardisés du krigeage : moyenne = -0.021, variance = 1.710  (visé : 0 et 1)
couverture des intervalles de krigeage à 95 % : 0.895
```

Trois lectures. **(1)** Les trois méthodes sont comparées sur **les mêmes** 200 prédictions : le krigeage a la plus petite erreur (0,969 jour), devant l'IDW (0,994), elle-même meilleure que la moyenne globale (1,097). L'avantage du krigeage sur l'IDW est mince (2,5 %) : sur ce jeu, la qualité de la prédiction ponctuelle ne départage pas nettement les deux. **(2)** Le krigeage fournit en plus un **écart-type d'erreur** : on le contrôle avec les résidus *standardisés* $(z-\hat z)/\sigma_K$, qui devraient avoir une moyenne proche de 0 et une variance proche de 1 si les barres d'erreur sont bien calibrées, et avec la **couverture** des intervalles $\hat z\pm1{,}96\,\sigma_K$. La moyenne des résidus standardisés est bien proche de 0 (−0,02), mais leur **variance est de 1,71** et la couverture n'est que de 89,5 % au lieu de 95 %. **(3)** Les barres d'erreur sont donc **trop optimistes** : trop étroites d'un facteur $\sqrt{1{,}71}\approx1{,}3$. La cause est celle que nous avons vue à l'ajustement : un variogramme estimé avec une pépite trop faible (0,04 au lieu de 0,4) annonce une prédiction plus précise qu'elle ne l'est. Le krigeage donne de **bonnes prédictions** même avec un variogramme approximatif, mais ses **barres d'erreur**, elles, héritent de toute l'incertitude du variogramme.

> 💡 **Remarque sur la mesure d'erreur.** Notre cible, dans cette validation, est la **mesure bruitée** $Z$ (ce que l'on observerait), qui contient la pépite. Une partie de l'erreur est donc irréductible, quelle que soit la qualité du modèle : même un krigeage parfait ne peut pas prédire le bruit de mesure. C'est pour cela que le RMSE de la validation croisée est supérieur à celui calculé plus haut contre le champ sans bruit.

**Une alternative sans variogramme : un lissage par spline.** On peut aussi prédire le délai comme une fonction lisse $f(x,y)$ des coordonnées, par une **spline de plaque mince**, comme le fait `mgcv` en R (le modèle additif généralisé de la section 2.5 de ce volume). Le même protocole de validation croisée, avec les mêmes plis, a été appliqué à une spline (le code R est dans le cahier, application 9.4) :


La spline obtient une erreur de 0,974 jour, quasiment identique à celle du krigeage (0,969), ce qui n'a rien de surprenant : les deux sont des **lisseurs linéaires** du même type, et le krigeage avec variogramme exponentiel a une interprétation proche. Les avantages propres du krigeage sont (1) un **modèle explicite de la dépendance** (pépite, portée, que l'on peut interpréter), (2) des **variances de prédiction** natives (la spline en fournit aussi, par ses erreurs-types, avec d'autres hypothèses).

### 9.3.7 Les limites : tendance, anisotropie, extrapolation

**Si la moyenne n'est pas constante.** Le variogramme présuppose un processus stationnaire. Si la moyenne varie dans l'espace (une **tendance** : par exemple, les délais augmentent avec l'éloignement du dépôt), le variogramme empirique **monte sans jamais se stabiliser**, parce que les paires éloignées diffèrent aussi par leur niveau moyen. Illustrons-le en ajoutant aux délais une tendance linéaire de $0{,}04$ jour par km vers l'est, puis en l'ôtant par régression avant de calculer le variogramme.

```text
tendance estimée par régression :  [ 4.325e+00  4.200e-02 -3.000e-03] (constante, pente en x, pente en y)
   h  sans_tendance  avec_tendance  tendance_retiree
 7.8           0.78           0.84              0.78
17.6           1.27           1.41              1.27
27.5           1.19           1.50              1.19
37.5           1.21           1.79              1.22
47.4           1.43           2.36              1.42
57.4           1.35           2.64              1.35
67.4           1.21           3.29              1.19
```

**Si le phénomène dépend de la direction** (*anisotropie*) : un délai peut varier plus vite le long d'un axe routier que perpendiculairement. On le détecte en calculant des variogrammes **directionnels** (en ne gardant que les paires orientées dans une direction, à une tolérance d'angle près). S'ils diffèrent, un variogramme unique est inadapté.


![À gauche : variogramme des délais sans tendance (vert), avec une tendance linéaire ajoutée (rouge, qui ne se stabilise pas), et après retrait de la tendance par régression (bleu). À droite : variogrammes directionnels est-ouest et nord-sud, comparés au variogramme toutes directions confondues.](figures/ch09-limites-variogramme.png)

À gauche, la tendance non retirée fait monter le variogramme bien au-delà du palier (de 0,84 à 3,29 entre 8 et 67 km), alors que le retrait de la tendance par régression redonne une courbe presque identique à celle sans tendance. La régression retrouve d'ailleurs la tendance ajoutée : une pente de 0,042 jour par km vers l'est pour 0,04 en vérité, et une pente nulle (−0,003) vers le nord. À droite, les deux directions **ne sont pas superposées** : la courbe nord-sud est au-dessus de la courbe est-ouest à toutes les distances. Faut-il y voir de l'**anisotropie** ? Avec des données réelles, on ne peut pas le savoir d'emblée : des variogrammes directionnels sont calculés sur des secteurs d'angle étroits, donc sur **moins de paires**, et sont bruités. La bonne démarche est de **calibrer** ce que le hasard seul produit. Résumons l'écart par un rapport moyen $\gamma_{\text{N-S}}/\gamma_{\text{E-O}}$ sur les classes de distance, puis calculons le même rapport sur 60 jeux simulés **isotropes** (le même processus, 60 autres graines).

```text
rapport N-S / E-O observé : 1.243
rapport sur 60 jeux isotropes : médiane 1.020, 10e-90e percentiles 0.908 - 1.167
part des jeux isotropes dont le rapport est au moins aussi grand : 0.050
```

Le rapport observé (1,24) est dans la queue haute de ce que le hasard produit sous isotropie (médiane 1,02 ; 80 % des jeux entre 0,91 et 1,17) : environ 5 % des jeux isotropes l'atteignent ou le dépassent. C'est donc un cas **limite** : trop marqué pour être banal, pas assez pour conclure. Nous *savons* ici, par construction, que le champ est isotrope : l'écart observé est un accident de ce tirage. Avec des données réelles, on aurait hésité, et la réponse prudente serait de comparer des modèles avec et sans anisotropie (par exemple par validation croisée) plutôt que de se fier à un graphique.

> ⚠️ **Quatre mises en garde.**
> 1. **Stationnarité.** Avec une tendance, il faut la modéliser (krigeage universel : tendance par régression et résidu krigé) ou la retirer. Retirer une tendance par régression ordinaire peut sous-estimer légèrement la semi-variance aux grandes distances (ici, la courbe des résidus est presque confondue avec celle du processus sans tendance).
> 2. **Anisotropie.** Vérifiez-la sur des variogrammes directionnels avant de supposer qu'une seule portée convient.
> 3. **Extrapolation.** Le krigeage est un **interpolateur** : loin de toute mesure, ou hors de l'enveloppe des points mesurés, la prédiction revient vers la moyenne et la variance monte vers le palier (nous venons de voir l'écart-type croître avec la distance à la mesure la plus proche). Ne promettez pas un délai dans une zone qu'aucune mesure n'entoure.
> 4. **Variogramme estimé, non connu.** La variance de krigeage suppose le variogramme **connu**. Comme nous l'avons vu à l'expérience des 30 graines, il est en réalité estimé avec une grande incertitude : l'écart-type de krigeage est donc plutôt optimiste, ce que la validation croisée du 9.3.6 a confirmé (variance des résidus standardisés de 1,71 au lieu de 1).

> ✅ **À retenir.**
> - Le **semi-variogramme** $\gamma(h)=\frac12\mathbb E[(Z(s+h)-Z(s))^2]$ décrit comment la ressemblance s'estompe avec la distance ; pour un processus de variance finie, $\gamma(h)=C(0)-C(h)$. Ses paramètres : **pépite** (bruit et micro-variations), **palier** (variance totale), **portée** (distance de décorrélation).
> - On estime $\gamma$ par classes de distance (**variogramme empirique**, avec le nombre de paires), puis on **ajuste un modèle valide** (sphérique, exponentiel, gaussien) par moindres carrés pondérés. Pépite et portée sont peu précises, même avec 200 points.
> - Le **krigeage ordinaire** est le meilleur prédicteur linéaire sans biais : on résout $\begin{pmatrix}\Gamma&\mathbf 1\\\mathbf 1^\top&0\end{pmatrix}\binom{\lambda}{m}=\binom{\gamma_0}{1}$, la prédiction est $\lambda^\top z$ et la variance $\lambda^\top\gamma_0+m$.
> - On le **valide** par validation croisée *avec réajustement du variogramme à chaque pli*, et on contrôle les barres d'erreur par les résidus standardisés et la couverture.
> - Limites : **stationnarité** (tendance), **anisotropie**, **extrapolation**, et un variogramme qui est une estimation, pas une vérité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.4 et 9.5, exercices 9.5, 9.6 et 9.11.


## 9.4 Processus ponctuels

> 💡 **Intuition.** Jusqu'ici, les lieux étaient donnés (les 144 zones, les adresses de livraison choisies par les clients) et c'était la **valeur** qui était aléatoire. Maintenant, ce sont les **positions** elles-mêmes qui sont le phénomène : où habitent les clients de la boutique ? Sont-ils éparpillés au hasard, **regroupés** en quartiers (une publicité, un bouche-à-oreille) ou étonnamment **bien espacés** (chacun choisit une adresse à distance des autres) ? Pour répondre, on compare ce que l'on observe à ce que produirait le **hasard complet**.

### 9.4.1 Le hasard complet : le processus de Poisson spatial

Pour reconnaître un écart au hasard, il faut d'abord définir le hasard. Un semis de points est de **hasard spatial complet** (en anglais *complete spatial randomness*, CSR) quand il est un **processus de Poisson homogène** d'intensité $\lambda$ (nombre moyen de points par km²) :

1. le nombre de points dans une région $B$ suit une loi de Poisson de moyenne $\lambda\,|B|$, où $|B|$ est l'aire de la région ;
2. les nombres de points dans des régions **disjointes** sont indépendants ;
3. conditionnellement au nombre total de points $n$ dans la fenêtre, les points sont **indépendants et uniformes** sur la fenêtre.

La propriété 3 est la plus utile en pratique : fabriquer un semis aléatoire sur une fenêtre, c'est tirer $n$ points uniformes. Le CSR est notre **hypothèse nulle** : aucune attraction, aucune répulsion entre points, et la même densité partout. Les deux écarts typiques sont l'**agrégat** (points groupés en paquets) et la **régularité** (points qui se repoussent, avec une distance minimale entre eux).

Fabriquons trois semis de la même fenêtre de $10\times10$ km (100 km²) autour de la boutique, de 75 à 100 adresses de clients chacun (le nombre de points de l'agrégé est lui-même aléatoire) :

- un semis **aléatoire** (CSR) de 100 points uniformes ;
- un semis **agrégé**, par un processus de **Thomas** : des « centres » (des quartiers, des abonnés d'un même influenceur) tombent au hasard, puis chaque centre engendre un nombre de clients de loi de Poisson, répartis autour de lui selon une loi normale ;
- un semis **régulier**, par **inhibition séquentielle** : on tire des points uniformes l'un après l'autre en refusant ceux qui tomberaient à moins de $0{,}7$ km d'un point déjà accepté.


Le générateur du processus de Thomas montre bien le mécanisme d'agrégation ; les deux autres, plus simples, sont reconstruits dans le cahier (application 9.6).

```python
def semis_thomas(kappa, mu, sigma, rng):
    """Agrégat de Thomas : centres de Poisson (densité kappa), mu descendants en moyenne, étalement sigma."""
    marge = 3 * sigma                                            # on génère aussi des centres hors fenêtre
    n_centres = rng.poisson(kappa * (COTE + 2 * marge) ** 2)
    centres = rng.uniform(-marge, COTE + marge, size=(n_centres, 2))
    nb = rng.poisson(mu, size=n_centres)
    pts = np.repeat(centres, nb, axis=0) + rng.normal(0, sigma, size=(nb.sum(), 2))
    return pts[((pts >= 0) & (pts <= COTE)).all(axis=1)]         # on ne garde que ce qui tombe dans la fenêtre
```

On tire alors les trois semis (graine fixe) et on les dessine :

```text
aléatoire (CSR)          n = 100 points  (intensité estimée 1.00 par km²)
agrégé (Thomas)          n =  75 points  (intensité estimée 0.75 par km²)
régulier (inhibition)    n = 100 points  (intensité estimée 1.00 par km²)
figure enregistrée
```

![Trois semis de points dans une fenêtre de 10 km × 10 km : hasard complet (gauche), agrégat de Thomas (centre), régulier par inhibition (droite).](figures/ch09-semis.png)

Les différences se voient à l'œil : des paquets et des vides au centre, un espacement très uniforme à droite, et au hasard complet à gauche un mélange de petits groupes et de vides qui surprend : **le hasard n'est pas régulier**. C'est un piège classique : nous avons tendance à voir de l'agrégation dans un semis tout à fait aléatoire, parce que des points qui tombent par hasard près les uns des autres nous sautent aux yeux. D'où le besoin de tests.

### 9.4.2 Le test des quadrats

La méthode la plus simple : quadriller la fenêtre en $m$ cases égales et **compter** les points dans chaque case. Sous le CSR, conditionnellement au nombre $n$ de points, les comptages suivent une loi multinomiale de probabilités égales : chaque case a la même moyenne $\bar c=n/m$, et l'on s'attend à une variance voisine de la moyenne (propriété de la loi de Poisson). On forme la statistique de Pearson

$$\chi^2=\sum_{k=1}^m\frac{(c_k-\bar c)^2}{\bar c},\qquad\text{approximativement }\chi^2_{m-1}\text{ sous le CSR}$$

(une approximation raisonnable quand $\bar c\ge5$ environ). Rappelons qu'elle vaut $(m-1)$ fois l'**indice de dispersion** $\text{VMR}=s^2/\bar c$ (variance divisée par moyenne). Une valeur **grande** de $\chi^2$ indique de l'**agrégation** (certaines cases beaucoup plus peuplées que d'autres), une valeur **petite** de la **régularité** (comptages trop uniformes).

> 💡 **Un exemple à la main.** Quatre cases contenant 1, 1, 1 et 9 points : $\bar c=3$, donc $\chi^2=\frac{(-2)^2+(-2)^2+(-2)^2+6^2}{3}=\frac{12+36}{3}=16$ avec 3 degrés de liberté : bien au-delà de ce que le hasard produit (la valeur critique à 5 % est 7,81). Quatre cases à 3 points chacune : $\chi^2=0$, une régularité parfaite. La statistique mesure donc l'inégalité des comptages.

```text
exemple (1, 1, 1, 9) : 16.0 | valeur critique chi2(3) à 5 % : 7.81
                       chi2  ddl    VMR  p_agregat (chi2 grand)  p_regulier (chi2 petit)
aléatoire (CSR)         8.8   15 0.5867                  0.8877                   0.1123
agrégé (Thomas)       143.7   15  9.578               4.342e-23                        1
régulier (inhibition)     4   15 0.2667                  0.9977                 0.002263

comptages par case du semis agrégé (4 x 4) :
[[ 1  0  1 11]
 [19  0  0  0]
 [12  2 14  1]
 [ 0  0  0 14]]
```

Le test distingue bien les trois cas : le semis **agrégé** a une statistique très élevée (VMR bien supérieur à 1, p-valeur d'agrégation minuscule), le semis **régulier** une statistique très faible (VMR très inférieur à 1, p-valeur de régularité minuscule) et le semis **aléatoire** une valeur banale.

> ⚠️ **Les limites du test des quadrats.** (1) Le résultat dépend de la **taille des cases** : un agrégat de 1 km de diamètre passe inaperçu avec des cases de 5 km. Le test est un test **à une échelle**. (2) Il ne retient que les comptages et jette l'information de **position** à l'intérieur de chaque case. (3) La loi du $\chi^2$ n'est qu'une approximation quand les comptages sont petits. Les méthodes à base de **distances**, qui suivent, n'ont pas ces défauts.

### 9.4.3 Le plus proche voisin : l'indice de Clark-Evans

Pour chaque point, notons $d_i$ la distance à son **plus proche voisin**. Sous le CSR d'intensité $\lambda$, la probabilité que le plus proche voisin d'un point soit **au-delà** de la distance $r$ est celle de ne trouver **aucun** point dans un disque d'aire $\pi r^2$, soit (loi de Poisson de moyenne $\lambda\pi r^2$, valeur en 0) :

$$\mathbb P(d>r)=e^{-\lambda\pi r^2}\quad\Longrightarrow\quad G(r)=\mathbb P(d\le r)=1-e^{-\lambda\pi r^2}.$$

On en déduit la distance moyenne au plus proche voisin, $\mathbb E[d]=\int_0^\infty e^{-\lambda\pi r^2}\,dr=\dfrac{1}{2\sqrt\lambda}$, et sa variance, $\operatorname{Var}(d)=\dfrac{4-\pi}{4\pi\lambda}$. L'**indice de Clark-Evans** compare la distance moyenne observée à celle du hasard :

$$R=\frac{\bar d_{\text{obs}}}{1/(2\sqrt{\hat\lambda})},\qquad \hat\lambda=\frac nA,$$

avec $R=1$ pour le hasard, $R<1$ pour de l'agrégation (les voisins sont plus proches que prévu), $R>1$ pour de la régularité. Comme $\bar d$ est une moyenne de $n$ distances (supposées à peu près indépendantes), on obtient un test $z=(\bar d-\mathbb E[d])/\sqrt{\operatorname{Var}(d)/n}$ approximativement normal.

> ⚠️ **L'effet de bord.** Cette formule suppose un plan infini. Dans une **fenêtre finie**, un point près du bord a moins de voisins possibles (il n'y a rien au-delà), donc son plus proche voisin est en moyenne plus loin : $\bar d$ est **surestimé** et $R$ est biaisé vers le haut, ce qui peut faire conclure à tort à une régularité. Donnelly (1978) a proposé une correction pour une fenêtre de périmètre $P$ : $\mathbb E[\bar d]=0{,}5\sqrt{A/n}+(0{,}0514+0{,}041/\sqrt n)\,P/n$ et $\operatorname{Var}(\bar d)=0{,}070\,A/n^2+0{,}037\,P\sqrt{A/n^5}$. Au lieu de la croire sur parole, **vérifions-la par simulation** : nous simulons 4 000 semis CSR de 100 points dans notre fenêtre et nous comparons la moyenne et l'écart-type de $\bar d$ aux deux formules.

```text
                              moyenne de d   écart-type de d
simulation (4000 semis CSR)         0.5224            0.0288
formule naïve (plan infini)         0.5000            0.0261
formule de Donnelly                 0.5222            0.0291
```

La formule naïve sous-estime la moyenne (0,500 contre 0,523 simulé : près de 5 % d'écart) et l'écart-type ; celle de Donnelly colle à la simulation. Appliquons l'indice de Clark-Evans aux trois semis avec les deux versions, et ajoutons une troisième voie, qui évite toute formule : une **p-valeur de Monte-Carlo**. On simule $B=999$ semis CSR de même taille dans la **même fenêtre** et l'on regarde où tombe notre $\bar d$ : l'effet de bord est automatiquement pris en compte, puisque les semis simulés le subissent aussi.

```text
                        n  d_moyen  R (naïf)  R (Donnelly)  z (Donnelly)  p (Donnelly)  p (Monte-Carlo)
aléatoire (CSR)       100   0.5353     1.071         1.025        0.4506        0.6523            0.628
agrégé (Thomas)        75   0.2026    0.3509        0.3336        -10.28     8.252e-25            0.002
régulier (inhibition) 100    0.829     1.658         1.587         10.53     6.024e-26            0.002
```

Les trois voies s'accordent pour le semis agrégé (R très inférieur à 1) et pour le semis régulier (R supérieur à 1). Pour le semis aléatoire, le R naïf vaut un peu plus de 1 et pourrait faire croire à une légère régularité : c'est le biais de bord. Avec la correction de Donnelly, il est ramené près de 1.

**La fonction $G$ entière.** L'indice de Clark-Evans résume toutes les distances par leur moyenne. On peut regarder la **fonction de répartition empirique** de $d_i$, $\hat G(r)=\frac1n\#\{i:d_i\le r\}$, et la comparer à la courbe théorique $1-e^{-\lambda\pi r^2}$, avec une **enveloppe de Monte-Carlo** : un bandeau qui contient 95 % des courbes obtenues sur des semis CSR simulés. Si notre courbe sort du bandeau, le hasard complet est mis en défaut. Une courbe $\hat G$ qui **monte plus vite** que le hasard indique des voisins plus proches que prévu (agrégat) ; une courbe qui monte **plus lentement** indique de la répulsion.

```text
                semis  part des r hors enveloppe
      aléatoire (CSR)                      0.000
      agrégé (Thomas)                      0.741
régulier (inhibition)                      0.531
```

![Fonction G (part des points dont le plus proche voisin est à moins de r) pour les trois semis, avec l'enveloppe de Monte-Carlo (bandeau gris, 499 semis CSR de même taille) et la courbe théorique du plan infini (pointillés).](figures/ch09-fonction-G.png)

Le semis aléatoire reste dans le bandeau ; l'agrégé monte beaucoup plus vite (ses voisins sont proches) ; le régulier est **nul** jusqu'à la distance d'inhibition (0,7 km) puis monte brusquement. Remarquons que le bandeau est un peu décalé par rapport à la courbe théorique : il intègre l'effet de bord. C'est lui, et non la courbe en pointillés, qu'il faut regarder.

### 9.4.4 La fonction $K$ de Ripley

La fonction $G$ ne regarde que le **premier** voisin, donc l'échelle la plus petite. Pour étudier plusieurs échelles à la fois, Ripley a proposé la fonction $K$ : $K(r)$ est le **nombre moyen de points supplémentaires** que l'on trouve à moins de la distance $r$ d'un point typique, **divisé par l'intensité** $\lambda$ :

$$K(r)=\frac1\lambda\;\mathbb E\big[\#\{\text{autres points à distance}\le r\text{ d'un point typique}\}\big].$$

Sous le CSR, les autres points sont distribués comme un processus de Poisson indépendamment du point typique (propriété de Slivnyak) : le nombre moyen d'autres points dans un disque d'aire $\pi r^2$ vaut $\lambda\pi r^2$, donc

$$K_{\text{CSR}}(r)=\pi r^2.$$

Pour un agrégat, un point typique a **plus** de voisins que prévu à toutes les petites distances : $K(r)>\pi r^2$. Pour un semis régulier, il en a **moins** : $K(r)<\pi r^2$. On préfère tracer la version « stabilisée » $\;L(r)-r=\sqrt{K(r)/\pi}-r$, qui vaut 0 sous le CSR et dont la variance est à peu près constante en $r$. L'estimateur naïf est $\hat K(r)=\dfrac{A}{n(n-1)}\sum_{i\ne j}\mathbf 1\{d_{ij}\le r\}$.

> 💡 **Un exemple à la main.** Quatre adresses dans la fenêtre unité ($A=1$) : $(0{,}1;0{,}1)$, $(0{,}2;0{,}1)$, $(0{,}8;0{,}8)$, $(0{,}85;0{,}9)$. Les deux premières sont à $0{,}1$ l'une de l'autre, les deux dernières à $\sqrt{0{,}05^2+0{,}1^2}\approx0{,}112$, les autres paires à plus de $1$. Pour $r=0{,}2$, il y a 2 paires proches, donc 4 couples ordonnés $(i,j)$ avec $i\ne j$ : $\hat K(0{,}2)=\frac{1}{4\times3}\times4=0{,}333$, alors que $\pi r^2=0{,}126$ : le semis est nettement agrégé à cette échelle.

> ⚠️ **L'effet de bord, encore.** Un point proche du bord a une partie de son disque hors de la fenêtre : on y voit mécaniquement moins de voisins, et l'estimateur naïf **sous-estime** $K$ aux grandes distances. La correction la plus simple est la **méthode du bord** (*reduced-sample*) : pour une distance $r$, on ne compte que les points situés à plus de $r$ du bord (leurs disques sont entiers dans la fenêtre), soit $n_r$ points :
> $$\hat K(r)=\frac{A}{(n-1)\,n_r}\sum_{i:\,b_i\ge r}\#\{j\ne i:\ d_{ij}\le r\},$$
> où $b_i$ est la distance de $i$ au bord. Elle est sans biais, au prix d'une perte de données quand $r$ grandit : on limite donc $r$ au quart du côté de la fenêtre environ.

```text
K(0,2) de l'exemple à la main : 0.3333 | pi r^2 = 0.1257
à r = 2 km  ->  pi r^2 = 12.57 | moyenne sans correction : 10.42 | moyenne avec correction : 12.30
```

Sans correction, l'estimateur sous-estime nettement $K$ à 2 km : 10,4 en moyenne au lieu de $\pi r^2=12{,}6$, soit 17 % de trop peu. Avec la méthode du bord, on obtient 12,3 : un écart de 2 %, très inférieur. Passons à l'application : on compare la courbe $\hat L(r)-r$ de chaque semis à une enveloppe obtenue sur 499 semis CSR de même taille. Pour un **test global** (et non « point par point »), on utilise la statistique $T=\max_r|\hat L(r)-r|$, comparée à sa distribution sous CSR.

```text
                semis  T observé  T sim. (médiane)  p global (Monte-Carlo)  L-r moyen
      aléatoire (CSR)      0.092            0.1002                   0.672   -0.03473
      agrégé (Thomas)      1.095             0.133                   0.002     0.7666
régulier (inhibition)        0.7            0.1023                   0.002    -0.2289
```

![Fonction L(r) − r de Ripley pour les trois semis, avec l'enveloppe de Monte-Carlo (bandeau gris) obtenue sur 499 semis aléatoires de même taille. Au-dessus de 0 : agrégat ; en dessous : régularité.](figures/ch09-ripley.png)

La lecture est la suivante. Le semis **aléatoire** reste dans le bandeau à toutes les distances et sa p-valeur globale est banale. Le semis **agrégé** est très au-dessus du bandeau sur toute la plage, avec une forme caractéristique : l'écart se creuse jusqu'à un **maximum vers 1 km**, une échelle de quelques fois l'étalement $\sigma=0{,}4$ km des paquets, puis décroît quand le disque de rayon $r$ commence à englober plusieurs paquets, dont les voisins ne sont plus « en excès ». Le semis **régulier** est sous le bandeau aux petites distances, avec un **minimum exactement à la distance d'inhibition** (0,7 km). Ce n'est pas un hasard : tant que $r<0{,}7$ km, aucune paire de points n'est à moins de $r$, donc $\hat K(r)=0$ et $L(r)-r=-r$ (la droite descendante de la figure) ; au-delà de 0,7 km, les voisins apparaissent et la courbe remonte vers le bandeau.

> ⚠️ **Enveloppe point par point ≠ test global.** Un bandeau à 95 % *en chaque $r$* est dépassé quelque part avec une probabilité bien supérieure à 5 % si l'on regarde de nombreuses distances (c'est le même problème que les tests multiples). Pour **conclure**, utilisez la p-valeur **globale** de la statistique $T$ ; le bandeau sert à **voir** à quelles échelles l'écart se produit.

### 9.4.5 Attention : agrégat ou densité variable ?

Tout ce qui précède suppose que l'**intensité est homogène**. C'est le piège principal des processus ponctuels. Imaginez que les clients habitent plutôt près de la boutique, au centre de la fenêtre, parce que la densité d'habitation y est plus forte. Même si chacun a choisi son adresse **sans tenir compte des autres** (aucune interaction), le semis paraîtra agrégé : beaucoup de points au centre, peu en périphérie. La fonction $K$ ne distingue pas un **agrégat** (les points s'attirent) d'une **intensité qui varie** (les points s'accumulent là où la densité est forte).

```text
semis à densité variable, SANS interaction : T = 0.687 | p global CSR = 0.002
comptages par case (4 x 4) :
[[ 3  8  2  1]
 [ 4 13 15  7]
 [ 5 10 11  6]
 [ 1  8  5  1]]
```

![À gauche : 100 adresses indépendantes les unes des autres, mais avec une densité qui décroît du centre vers les bords. À droite : la fonction L(r) − r sort de l'enveloppe du hasard complet, alors qu'il n'y a aucune interaction entre les points.](figures/ch09-inhomogene.png)

Le test rejette le hasard complet alors qu'**aucun point n'attire les autres**. L'agrégat apparent est entièrement dû à la variation de la densité. Le remède est de comparer non pas à un CSR homogène mais à un **processus de Poisson inhomogène** d'intensité estimée $\hat\lambda(s)$ (par un lissage à noyau, par exemple), et d'utiliser la fonction **$K$ inhomogène** de Baddeley, Møller et Waagepetersen. Elle ne figure pas dans ce chapitre (nous ne l'avons pas implémentée) ; retenez le principe : **on ne peut parler d'agrégation entre les points qu'après avoir tenu compte de la densité qui varie**. Cette distinction entre *effet du premier ordre* (l'intensité) et *effet du second ordre* (l'interaction) est le cœur de la modélisation des semis de points.

> 💡 **Retour à la question de la gérante.** Pour savoir si ses clients du quartier sont **vraiment** regroupés autour de la boutique, elle ne peut pas se contenter d'un test de $K$ : elle doit d'abord se demander si la densité de population varie, c'est-à-dire si les habitants eux-mêmes sont plus nombreux près de la boutique. Un semis de clients qui reproduit simplement la répartition de la **population** ne dit rien sur son comportement. La comparaison utile est avec les habitants **non clients** (un semis de « contrôle ») ou avec une carte de densité de population.

> ✅ **À retenir.**
> - Un **semis de points** est un phénomène dont les **positions** sont aléatoires. La référence est le **hasard spatial complet** : un processus de Poisson homogène (comptages de Poisson, indépendance entre régions disjointes, points uniformes conditionnellement à leur nombre).
> - **Quadrats** : $\chi^2=\sum(c_k-\bar c)^2/\bar c$ (approximativement $\chi^2_{m-1}$) ; simple, mais dépend de la taille des cases.
> - **Plus proche voisin** : $G(r)=1-e^{-\lambda\pi r^2}$ sous le CSR, $\mathbb E[d]=1/(2\sqrt\lambda)$ ; indice de Clark-Evans $R<1$ pour un agrégat, $R>1$ pour de la régularité. Une fenêtre finie biaise $R$ (**effet de bord**) : corrigez (Donnelly) ou, mieux, utilisez une **p-valeur de Monte-Carlo** dans la même fenêtre.
> - **Fonction $K$ de Ripley** : $K_{\text{CSR}}(r)=\pi r^2$ ; $L(r)-r$ au-dessus de 0 pour l'agrégat, en dessous pour la régularité ; **correction de bord** indispensable ; utilisez un test **global** et non un bandeau point par point.
> - **Une intensité variable imite un agrégat** : avant de conclure à une interaction, tenez compte de la densité.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.6 et 9.7, exercices 9.10 et 9.12.


## Bilan du chapitre 9

Vous savez maintenant :

- distinguer les **trois familles** de données spatiales (géostatistique, surfacique, semis de points) en se demandant *qu'est-ce qui est aléatoire ?* ;
- repérer un point et **mesurer une distance** correctement (haversine, projection locale) et dessiner une carte honnête sans fond de carte ;
- **définir un voisinage** par une matrice de poids et mesurer l'**autocorrélation** avec les indices de **Moran** et de **Geary**, les tester par **permutations**, et localiser les îlots avec les indices locaux (LISA) en **corrigeant** les tests multiples ;
- expliquer pourquoi ignorer l'autocorrélation fait **rejeter à tort** (46 % de faux positifs au lieu de 5 % dans notre simulation) et la tester sur les **résidus** d'un modèle ;
- estimer et ajuster un **variogramme** (pépite, palier, portée), connaître ses incertitudes, et **prédire par krigeage** avec une variance d'erreur, en validant par **validation croisée** ;
- étudier un **semis de points** par quadrats, plus proche voisin et **fonction $K$ de Ripley**, avec une **enveloppe de Monte-Carlo** et une **correction de bord**.

Ce chapitre a aussi rassemblé les **limites** qui reviennent à chaque étape :

| Limite | Où elle apparaît | Précaution |
|---|---|---|
| **Effet de bord** | plus proche voisin (biais de $R$), fonction $K$, indices locaux | correction (Donnelly, méthode du bord), enveloppe de Monte-Carlo dans la même fenêtre, examiner les bords à part |
| **Problème de l'unité spatiale modifiable** | corrélations et indices calculés sur des zones | indiquer le découpage, tester plusieurs échelles, ne pas transposer à l'individu |
| **Non-stationnarité** | variogramme, krigeage | retirer ou modéliser la tendance (krigeage universel) |
| **Anisotropie** | variogramme | variogrammes directionnels, **calibrés** par simulation |
| **Densité variable** | fonction $K$ | $K$ inhomogène ; ne pas confondre premier et second ordre |
| **Variogramme estimé, pas connu** | barres d'erreur du krigeage | validation croisée avec réajustement, prudence sur les intervalles |

> ✅ **Si vous ne deviez retenir qu'une idée.** *L'espace n'est pas une colonne de plus dans le tableau : il change la nature de l'information.* Des observations voisines ne sont pas indépendantes, donc : définissez le voisinage, mesurez la dépendance, vérifiez-la dans les résidus, et attribuez-lui une incertitude honnête.

> 🧭 **Pour aller plus loin** (hors de ce chapitre) : les modèles de régression spatiale (*spatial lag* et *spatial error*, par maximum de vraisemblance), le krigeage universel et le co-krigeage, les modèles géostatistiques bayésiens, la fonction $K$ inhomogène et les modèles de Cox log-gaussiens pour les semis de points, la statistique spatio-temporelle. Ces extensions reposent exactement sur les trois idées que vous venez de pratiquer : un **voisinage**, une **fonction de dépendance** et une **comparaison à un hasard bien défini**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : applications 9.1 à 9.7 et exercices 9.1 à 9.12.
