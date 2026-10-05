# Chapitre 9 : ➕ Statistique spatiale

> « Tout est lié à tout le reste, mais ce qui est proche est plus lié que ce qui est lointain. »
> — Waldo Tobler, *première loi de la géographie* (1970)

> 🧭 **Chapitre complémentaire.** Ce chapitre est **entièrement facultatif** : rien dans les chapitres 1 à 6 ni dans le projet du volume n'en dépend. Il s'adresse à ceux dont les données ont une **position** : des adresses de clients, des points de livraison, des zones géographiques, des capteurs. Si c'est votre cas, vous verrez que presque tout ce que nous avons appris repose sur une hypothèse que l'espace met à mal : l'**indépendance** des observations.

Dar Jasmin livre maintenant dans tout le nord du pays. Yasmine remarque des choses que les tableaux des chapitres précédents ne savent pas dire :

- *« Les délais de livraison longs sont groupés : quand un client de Zaghouan attend longtemps, ses voisins aussi. »* Un point isolé ne serait pas un problème ; un **paquet** de retards, c'est un problème de tournée ou de route.
- *« Mes ventes par délégation ont l'air de former des îlots : des zones où l'on vend beaucoup, entourées de zones où l'on vend beaucoup. »* Est-ce réel, ou est-ce l'œil qui voit des formes dans le hasard ?
- *« Je voudrais promettre un délai au client avant même d'avoir livré dans son quartier. »* Comment **prédire** une valeur en un endroit où l'on n'a rien mesuré ?
- *« Mes clients de la médina se regroupent-ils vraiment autour de la boutique, ou sont-ils répartis au hasard ? »*

Quatre questions, quatre outils : l'**autocorrélation spatiale**, le **variogramme** et le **krigeage**, les **processus ponctuels**. Les voici, dans l'ordre.

## Le chemin de ce chapitre

- **9.1 Données spatiales et cartes** : les trois grands types de données spatiales, la façon de repérer un point sur la Terre, de calculer une distance **sans se tromper**, et de dessiner une carte honnête sans fond de carte.
- **9.2 Autocorrélation spatiale** : définir « voisin » avec une **matrice de poids**, mesurer la ressemblance entre voisins avec l'**indice de Moran** (démontré, calculé à la main, puis testé par permutations), l'indice de **Geary**, et repérer *où* se trouvent les îlots avec les indices **locaux** (LISA).
- **9.3 Variogramme et krigeage** : décrire comment la ressemblance **décroît avec la distance**, ajuster un modèle (pépite, palier, portée), et **prédire** en un point non mesuré avec une **variance d'erreur** (le krigeage, dérivé avec des multiplicateurs de Lagrange).
- **9.4 Processus ponctuels** : quand ce sont les **positions** qui sont aléatoires ; hasard complet, agrégat ou répulsion ? Test des quadrats, plus proche voisin, fonction K de Ripley, enveloppes de Monte-Carlo.
- **9.5 Exercices corrigés**, puis le bilan du chapitre.

> 🛠️ **Comment travailler avec ce chapitre.** Aucune bibliothèque de cartographie n'est nécessaire (ni `geopandas`, ni `pykrige`) : tout est écrit avec NumPy, SciPy et matplotlib. C'est volontaire. Calculer soi-même un indice de Moran ou résoudre soi-même un système de krigeage est la meilleure garantie de comprendre ce que font ensuite les bibliothèques spécialisées. En contrepartie, les cartes n'ont **pas de fond de carte** (il faudrait télécharger des tuiles) : ce sont des graphiques de coordonnées, sobres mais honnêtes.

> 📦 **Les données de ce chapitre.** Les données sont **simulées**, avec des graines fixes, de façon que nous connaissions la vérité et puissions vérifier que les méthodes la retrouvent.
>
> - Une **grille de 12 × 12 « délégations » fictives** (144 zones de 5 km de côté) avec des ventes par habitant qui présentent une autocorrélation spatiale *connue* (fichier `donnees/ch09-delegations.csv`), plus une variable de contrôle sans aucune structure spatiale.
> - **200 livraisons** dans un carré de 100 km de côté, avec un délai en jours qui varie de façon continue dans l'espace (fichier `donnees/ch09-livraisons.csv`).
> - Des **semis de points** (adresses de clients), simulés directement dans les sections qui les utilisent.
> - Les **coordonnées géographiques de dix villes tunisiennes**, qui sont des valeurs **approximatives** écrites à la main et arrondies au centième de degré (à vérifier avant tout usage cartographique réel), et le tableau `donnees/clients.csv` du volume pour les effectifs par ville.
>
> Le générateur du chapitre est dans `build/donnees_ch09.py` ; son code est celui qui est imprimé aux sections 9.2 et 9.3.


## 9.1 Données spatiales et cartes

> 💡 **Intuition.** Dans un tableau ordinaire, l'ordre des lignes n'a aucune importance : on peut les mélanger sans rien changer à la moyenne, à la régression ou au test. Dans des données spatiales, **où** se trouve chaque ligne fait partie de l'information. Deux clients voisins se ressemblent plus que deux clients éloignés, et c'est précisément ce qui casse l'hypothèse d'**indépendance** sur laquelle reposent presque tous les outils du volume I et des chapitres 1 et 2 de ce volume.

### 9.1.1 Pourquoi l'espace change tout

Un petit exemple pour sentir le problème. Yasmine a mesuré le délai de quatre livraisons : deux à Bizerte (notées A et B, à quelques rues l'une de l'autre) et deux à Sfax (C et D). Les délais sont 6, 7, 3 et 4 jours.

La moyenne est $(6+7+3+4)/4=5$ jours, et l'écart-type est d'environ 1,83 jour. Si les quatre livraisons étaient **indépendantes**, l'écart-type de la moyenne serait $s/\sqrt n\approx 0{,}91$ jour : la formule du volume I (section 2.4). Mais A et B ont subi la même route embouteillée, C et D la même autoroute fluide. En réalité, nous n'avons pas **quatre** informations indépendantes, mais plutôt **deux** (une par ville). Notre moyenne est beaucoup moins précise que ne le dit la formule.

> ⚠️ **Le danger concret.** Avec des observations corrélées dans l'espace, les erreurs-types « habituelles » sont **trop petites**, les intervalles de confiance trop étroits et les p-valeurs trop optimistes. Nous aurons l'impression d'avoir 200 observations alors que nous en avons, au sens de l'information, bien moins. C'est la raison pour laquelle il faut **mesurer** la dépendance spatiale avant de lui faire confiance, et c'est l'objet de tout ce chapitre.

> 🧪 **La loi de Tobler en une phrase.** « Tout est lié à tout le reste, mais ce qui est proche est plus lié que ce qui est lointain. » Ce n'est pas un théorème, c'est une observation qui se vérifie pour les prix de l'immobilier, la température, les délais de livraison, les maladies contagieuses… et qui justifie tous les outils qui suivent : ils mesurent *à quelle vitesse* la ressemblance s'estompe avec la distance.

### 9.1.2 Trois types de données spatiales

Selon ce qui est aléatoire et ce qui est fixe, on distingue trois grandes familles. Savoir dans quelle famille on se trouve est la **première** question à se poser, car elle détermine les outils.

| Type | Ce qu'on observe | Ce qui est fixe / aléatoire | Exemple Dar Jasmin | Outils (section) |
|---|---|---|---|---|
| **Géostatistique** | une valeur en des **points** d'un phénomène défini *partout* | les lieux sont choisis (fixes), la valeur est aléatoire | le délai de livraison, mesuré à 200 adresses, qui existe en tout point de la zone | variogramme, krigeage (9.3) |
| **Données surfaciques** (*lattice*) | une valeur par **zone** d'un découpage | le découpage est fixe, la valeur est aléatoire | les ventes par habitant de chaque délégation | matrice de poids, Moran, Geary, LISA (9.2) |
| **Semis de points** | les **positions** elles-mêmes | les lieux sont **aléatoires** | les adresses des clients de la médina | quadrats, plus proche voisin, K de Ripley (9.4) |

La frontière n'est pas étanche : les mêmes ventes peuvent être vues par zone (surfacique) ou, si l'on connaît les adresses, comme un semis de points avec une « marque » (le montant). Mais le **choix du modèle** suit toujours cette question : *qu'est-ce qui est aléatoire ici ?*

> 💡 **Un test pratique.** Imaginez que l'on refasse l'expérience. Si les **valeurs** changent mais pas les lieux (le même 12 × 12 de délégations, d'autres ventes), c'est de la géostatistique ou du surfacique. Si ce sont les **lieux** qui changeraient (d'autres adresses de clients), c'est un semis de points.

### 9.1.3 Repérer un point : coordonnées et distances

Un point sur Terre se repère par sa **latitude** $\varphi$ (de −90° au pôle Sud à +90° au pôle Nord) et sa **longitude** $\lambda$ (de −180° à +180° à partir du méridien de Greenwich). Voici dix villes tunisiennes, avec des coordonnées **approximatives**, arrondies au centième de degré (nous les avons saisies à la main : elles suffisent pour apprendre, mais à vérifier pour tout usage réel).

```python
import numpy as np
import pandas as pd

villes = pd.DataFrame({
    "ville": ["Tunis", "Bizerte", "Nabeul", "Sousse", "Kairouan", "Sfax", "Gafsa", "Gabès", "Djerba", "Tozeur"],
    "lat":   [36.81, 37.27, 36.46, 35.83, 35.68, 34.74, 34.43, 33.88, 33.88, 33.92],
    "lon":   [10.18,  9.87, 10.74, 10.61, 10.10, 10.76,  8.78, 10.10, 10.86,  8.13],
})
print(villes.to_string(index=False))
```
<!--sortie-->
```text
   ville   lat   lon
   Tunis 36.81 10.18
 Bizerte 37.27  9.87
  Nabeul 36.46 10.74
  Sousse 35.83 10.61
Kairouan 35.68 10.10
    Sfax 34.74 10.76
   Gafsa 34.43  8.78
   Gabès 33.88 10.10
  Djerba 33.88 10.86
  Tozeur 33.92  8.13
```

**Piège n° 1 : un degré n'est pas une distance fixe.** Un degré de latitude vaut toujours à peu près 111 km (la Terre est presque une sphère de rayon $R\approx 6371$ km, et $1^\circ=\pi/180$ radian, donc $R\pi/180\approx 111{,}2$ km). Mais les méridiens se **rapprochent** quand on monte vers le pôle : un degré de longitude vaut $111{,}2\times\cos\varphi$ km. À la latitude de Tunis (environ 37°), $\cos 37^\circ\approx0{,}80$ : un degré de longitude ne vaut que **89 km**.

Faisons un calcul à la main pour Tunis (36,81 ; 10,18) et Bizerte (37,27 ; 9,87) :

- écart de latitude : $0{,}46^\circ\times111{,}2\approx51{,}2$ km vers le nord ;
- écart de longitude : $0{,}31^\circ\times111{,}2\times\cos(37{,}0^\circ)\approx27{,}5$ km vers l'ouest (avec $\cos 37{,}0^\circ\approx0{,}80$) ;
- distance ≈ $\sqrt{51{,}2^2+27{,}5^2}\approx58{,}1$ km.

Si l'on avait oublié le $\cos\varphi$ et traité les degrés comme des unités égales, on aurait trouvé $111{,}2\times\sqrt{0{,}46^2+0{,}31^2}\approx 61{,}7$ km : 6 % d'erreur, sur une distance courte. Et plus le trajet est orienté est-ouest, plus l'erreur grandit (nous le mesurons plus bas).

> 📐 **La formule de haversine (distance sur la sphère).** La plus courte distance entre deux points d'une sphère de rayon $R$ est un arc de **grand cercle**. Pour deux points $(\varphi_1,\lambda_1)$ et $(\varphi_2,\lambda_2)$ (en radians) :
>
> $$a=\sin^2\!\Big(\frac{\varphi_2-\varphi_1}{2}\Big)+\cos\varphi_1\cos\varphi_2\,\sin^2\!\Big(\frac{\lambda_2-\lambda_1}{2}\Big),\qquad d=2R\,\arcsin\sqrt a .$$
>
> **Contrôle de bon sens.** Si $\lambda_1=\lambda_2$ (même méridien), alors $a=\sin^2\big((\varphi_2-\varphi_1)/2\big)$ et $d=2R\arcsin\big|\sin((\varphi_2-\varphi_1)/2)\big|=R\,|\varphi_2-\varphi_1|$ : c'est bien la longueur d'un arc de cercle de rayon $R$ et d'angle $|\Delta\varphi|$. Pour une différence d'un degré, on retrouve $R\pi/180\approx111{,}2$ km. Le terme $\cos\varphi_1\cos\varphi_2$ est exactement le facteur de raccourcissement des méridiens.

```python
R = 6371.0   # rayon moyen de la Terre, en km

def haversine(lat1, lon1, lat2, lon2):
    """Distance de grand cercle en km (arguments en degrés ; NumPy diffuse sur les tableaux)."""
    p1, p2 = np.radians(lat1), np.radians(lat2)
    dphi = p2 - p1
    dlam = np.radians(lon2) - np.radians(lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dlam / 2) ** 2
    return 2 * R * np.arcsin(np.sqrt(a))

# Contrôle : un degré le long d'un méridien
print("1 degré de latitude  :", round(float(haversine(36.0, 10.0, 37.0, 10.0)), 1), "km")
print("1 degré de longitude à 36° N :", round(float(haversine(36.0, 10.0, 36.0, 11.0)), 1), "km   (111,2 x cos 36° =", round(111.19 * np.cos(np.radians(36)), 1), ")")
print("Tunis - Bizerte :", round(float(haversine(36.81, 10.18, 37.27, 9.87)), 1), "km")
```
<!--sortie-->
```text
1 degré de latitude  : 111.2 km
1 degré de longitude à 36° N : 90.0 km   (111,2 x cos 36° = 90.0 )
Tunis - Bizerte : 58.1 km
```

Le calcul à la main (58,1 km) et la formule donnent la même chose. Calculons maintenant la **matrice des distances** entre toutes les villes. Tout le chapitre utilisera des matrices de distances : autant apprendre la technique tout de suite. Le principe est de transformer les vecteurs en colonnes et en lignes pour que NumPy calcule les $10\times10$ paires d'un coup (la diffusion du chapitre 4.4 du volume I).

```python
lat, lon = villes["lat"].to_numpy(), villes["lon"].to_numpy()
D = haversine(lat[:, None], lon[:, None], lat[None, :], lon[None, :])     # (10, 10)
court = ["Tun", "Biz", "Nab", "Sou", "Kai", "Sfa", "Gaf", "Gab", "Dje", "Toz"]
print(pd.DataFrame(D.round(0).astype(int), index=court, columns=court).to_string())
print()
print("matrice symétrique :", np.allclose(D, D.T), "| diagonale nulle :", np.allclose(np.diag(D), 0))
```
<!--sortie-->
```text
     Tun  Biz  Nab  Sou  Kai  Sfa  Gaf  Gab  Dje  Toz
Tun    0   58   63  116  126  236  293  326  332  371
Biz   58    0  119  173  178  292  331  378  387  404
Nab   63  119    0   71  104  191  287  293  287  369
Sou  116  173   71    0   49  122  228  222  218  310
Kai  126  178  104   49    0  121  184  200  212  266
Sfa  236  292  191  122  121    0  185  113   96  258
Gaf  293  331  287  228  184  185    0  136  201   82
Gab  326  378  293  222  200  113  136    0   70  182
Dje  332  387  287  218  212   96  201   70    0  252
Toz  371  404  369  310  266  258   82  182  252    0

matrice symétrique : True | diagonale nulle : True
```

Sur quelques paires, mesurons l'erreur que l'on commet avec deux raccourcis tentants : (a) traiter les degrés comme des unités égales ($111{,}2\times$ la distance euclidienne en degrés), (b) projeter à plat avec la **projection équirectangulaire** centrée sur la latitude moyenne $\varphi_0$, $x=R(\lambda-\lambda_0)\cos\varphi_0$ et $y=R(\varphi-\varphi_0)$, puis prendre la distance euclidienne.

```python
def naif(lat1, lon1, lat2, lon2):
    return 111.19 * np.hypot(lat2 - lat1, lon2 - lon1)

def equirect(lat1, lon1, lat2, lon2, lat0):
    c = np.cos(np.radians(lat0))
    return R * np.radians(1) * np.hypot(lat2 - lat1, (lon2 - lon1) * c)

lat0 = villes["lat"].mean()
paires = [("Tunis", "Bizerte"), ("Tunis", "Sfax"), ("Tunis", "Tozeur"), ("Bizerte", "Djerba"), ("Tozeur", "Djerba")]
lignes = []
for a, b in paires:
    ra, rb = villes.set_index("ville").loc[a], villes.set_index("ville").loc[b]
    vrai = float(haversine(ra.lat, ra.lon, rb.lat, rb.lon))
    n = float(naif(ra.lat, ra.lon, rb.lat, rb.lon))
    e = float(equirect(ra.lat, ra.lon, rb.lat, rb.lon, lat0))
    lignes.append({"paire": f"{a}-{b}", "haversine_km": vrai, "degres_bruts_km": n, "erreur_%": 100 * (n / vrai - 1),
                   "equirect_km": e, "erreur_eq_%": 100 * (e / vrai - 1)})
print(pd.DataFrame(lignes).round(1).to_string(index=False))
```
<!--sortie-->
```text
         paire  haversine_km  degres_bruts_km  erreur_%  equirect_km  erreur_eq_%
 Tunis-Bizerte          58.1             61.7       6.2         58.4          0.5
    Tunis-Sfax         236.0            239.0       1.3        236.1          0.0
  Tunis-Tozeur         371.2            394.0       6.1        371.3          0.0
Bizerte-Djerba         387.4            392.7       1.4        387.5          0.0
 Tozeur-Djerba         252.0            303.6      20.5        247.8         -1.7
```

Le raccourci « degrés bruts » **surestime** toujours (puisque $\cos\varphi<1$) : l'erreur va de 1 % à 20 % selon la direction du trajet. Elle est la plus forte pour Tozeur–Djerba, un trajet presque exactement est-ouest (la différence de latitude est minime, celle de longitude est de plus de 2,7°), et la plus faible pour Tunis–Sfax et Bizerte–Djerba, qui sont surtout nord-sud. La projection équirectangulaire, elle, reste à moins de 2 % d'erreur sur toutes ces paires, ce qui est excellent pour une région de la taille de la Tunisie. C'est pour cela que, dans la pratique, on **projette** les coordonnées dans un système plan local, mesuré en mètres ou en kilomètres (le système UTM, par exemple, fournit des zones de 6° de longitude, et la zone 32 couvre l'essentiel de la Tunisie), puis on travaille avec des distances euclidiennes ordinaires. Pour la suite de ce chapitre, nos zones font 100 km de côté : nous utiliserons directement des coordonnées planes **en kilomètres**.

> ⚠️ **À vol d'oiseau n'est pas « en camion ».** Les distances calculées ici sont des distances **à vol d'oiseau**. Entre deux villes, la distance **routière** est plus longue (parfois 30 % de plus), et le temps de trajet dépend de la route. Pour des questions de logistique, la bonne « distance » entre deux points est souvent un temps de parcours, qui n'est pas forcément symétrique ni euclidienne. Les outils de ce chapitre fonctionnent avec n'importe quelle distance… à condition que ses propriétés conviennent (nous y reviendrons aux sections 9.2 et 9.3).

### 9.1.4 Une carte sans fond de carte

Sans bibliothèque de cartographie, une carte est simplement un nuage de points $(x,y)$ avec **un rapport d'aspect correct** (un kilomètre vers l'est doit occuper la même longueur à l'écran qu'un kilomètre vers le nord). Pour des coordonnées en degrés, on y parvient en réglant le rapport d'aspect à $1/\cos\varphi_0$, ce qui revient à la projection équirectangulaire. Voyons-le avec les villes de Dar Jasmin, en dessinant un **symbole proportionnel** : la surface du disque est proportionnelle au nombre de clients de la ville (le fichier `clients.csv`, qui vit dans l'univers simulé du volume).

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

clients = pd.read_csv("donnees/clients.csv")
par_ville = clients.groupby("ville").agg(clients=("id_client", "size"), depense=("depense_annuelle", "mean")).round(1)
print(par_ville.to_string())

carte = villes.merge(par_ville, left_on="ville", right_index=True, how="left")   # « Autre » n'a pas de position
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"

fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.2))
for ax, titre, corrige in zip(axes, ["Degrés traités comme des unités égales", "Aspect corrigé (1 / cos de la latitude)"], [False, True]):
    ax.scatter(carte["lon"], carte["lat"], s=18, color=ORANGE, zorder=3)
    ax.scatter(carte["lon"], carte["lat"], s=carte["clients"].fillna(0) * 1.5, color=BLEU, alpha=0.35, zorder=2)
    for _, r in carte.iterrows():
        decal, ha = ((-6, -11), "right") if r["ville"] == "Kairouan" else ((5, 4), "left")   # évite le disque de Sousse
        ax.annotate(r["ville"], (r["lon"], r["lat"]), xytext=decal, ha=ha, textcoords="offset points", fontsize=8)
    ax.set_title(titre, fontsize=10)
    ax.set_xlabel("longitude (°E)")
    ax.set_xlim(7.5, 11.9)
    ax.set_ylim(33.5, 37.6)
    ax.set_aspect(1 / np.cos(np.radians(lat0)) if corrige else 1.0)   # 1.0 : un degré = un degré, dans les deux sens
axes[0].set_ylabel("latitude (°N)")
plt.tight_layout()
plt.savefig("figures/ch09-carte-villes.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
         clients  depense
ville                    
Autre        301    274.0
Bizerte      208    217.9
Nabeul       252    243.6
Sfax         282    245.6
Sousse       337    247.0
Tunis        620    245.5
figure enregistrée
```

![Les dix villes (points orange) et les effectifs de clients (disques bleus, surface proportionnelle). À gauche : un degré de longitude est dessiné aussi long qu'un degré de latitude, ce qui étire la carte d'est en ouest. À droite : le rapport d'aspect 1/cos(φ) rétablit les proportions.](figures/ch09-carte-villes.png)

Deux conseils de lecture. Les disques sont **proportionnels en surface** et non en rayon : si l'on doublait le rayon pour doubler la valeur, l'œil verrait une surface quatre fois plus grande, et le graphique mentirait. Et la carte de gauche, qui traite les degrés comme des unités égales (c'est ce que fait un `scatter(lon, lat)` avec `aspect="equal"`), déforme les distances : les villes y paraissent plus éloignées d'est en ouest qu'elles ne le sont.

Le même principe vaut pour les zones : pour afficher une valeur par délégation (données surfaciques), on dessine une grille colorée (une « carte choroplèthe » dans le jargon). Chargeons nos deux jeux de données de travail, la grille de délégations et les 200 livraisons, et regardons-les côte à côte.

```python
deleg = pd.read_csv("donnees/ch09-delegations.csv")
liv = pd.read_csv("donnees/ch09-livraisons.csv")
print(deleg.head(4).to_string(index=False))
print()
print(liv.head(4).to_string(index=False))
print()
print("délégations :", deleg.shape, "| livraisons :", liv.shape)
print(liv["delai_jours"].describe().round(2).to_string())
```
<!--sortie-->
```text
 id  lig  col    x   y  population  ventes_hab  ventes_bruit
  0    0    0  2.5 2.5        3811       60.70         58.02
  1    0    1  7.5 2.5        6211       64.84         43.91
  2    0    2 12.5 2.5        5702       52.04         47.84
  3    0    3 17.5 2.5        5151       63.46         48.15

    x     y  delai_jours  pli
69.77 31.38        5.465    4
12.12 32.36        5.798    1
93.12 78.97        5.374    2
 1.00 19.89        2.985    0

délégations : (144, 8) | livraisons : (200, 4)
count    200.00
mean       4.27
std        1.10
min        1.59
25%        3.62
50%        4.26
75%        5.07
max        7.53
```

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

# Gauche : carte « choroplèthe » des ventes par habitant, grille 12 x 12 (une case = 5 km x 5 km)
grille = deleg["ventes_hab"].to_numpy().reshape(12, 12)
im = ax1.imshow(grille, origin="lower", extent=(0, 60, 0, 60), cmap="Blues")
ax1.set_title("Ventes par habitant (DT) par délégation")
ax1.set_xlabel("x (km)"); ax1.set_ylabel("y (km)")
fig.colorbar(im, ax=ax1, shrink=0.8, label="DT par habitant")

# Droite : délai de livraison en 200 adresses
sc = ax2.scatter(liv["x"], liv["y"], c=liv["delai_jours"], cmap="Oranges", s=46, edgecolor="#555555", linewidth=0.3)
ax2.set_title("Délai de livraison (jours) à 200 adresses")
ax2.set_xlabel("x (km)"); ax2.set_ylabel("y (km)")
ax2.set_aspect("equal")
fig.colorbar(sc, ax=ax2, shrink=0.8, label="jours")
plt.tight_layout()
plt.savefig("figures/ch09-donnees-chapitre.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![À gauche : ventes par habitant par délégation (grille 12 × 12). À droite : délais de livraison observés en 200 adresses d'un carré de 100 km de côté.](figures/ch09-donnees-chapitre.png)

La carte de gauche ne ressemble pas à du « sel et poivre » : on y voit nettement une plage de faibles ventes au sud-est et des plages de fortes ventes au centre et au nord. La carte de droite est bien plus difficile à lire : des points de teintes voisines se côtoient, mais d'autres se mêlent, et l'œil hésite entre structure et hasard. C'est exactement pour cela qu'il faut **chiffrer** l'impression plutôt que de s'y fier. Mais avant, une mise en garde sur le dessin lui-même.

> ⚠️ **Les cartes mentent facilement.** Trois pièges classiques : (1) **la palette**, car une rampe séquentielle (clair → foncé) convient à une quantité ordonnée, et un arc-en-ciel invente des frontières qui n'existent pas ; (2) **les classes**, car découper une valeur continue en cinq paliers « égaux » ou en quantiles change complètement l'image ; (3) **la surface** : une grande zone peu peuplée attire l'œil autant qu'une petite zone très peuplée. Nous reviendrons sur ce dernier point à la section 9.5 (le *problème de l'unité spatiale modifiable*).

> ✅ **À retenir.**
> - L'espace casse l'**indépendance** : des observations proches se ressemblent, les erreurs-types usuelles sont trop optimistes.
> - Trois familles : **géostatistique** (valeurs en des points d'un champ continu), **surfacique** (une valeur par zone), **semis de points** (les positions sont aléatoires). On se demande d'abord : *qu'est-ce qui est aléatoire ?*
> - Un degré de longitude ne vaut pas un degré de latitude : $111{,}2\cos\varphi$ km contre 111,2 km. Pour des distances sur la Terre, on utilise **haversine** (ou on projette dans un plan local en kilomètres).
> - Une carte sans fond de carte reste utile : rapport d'aspect correct, symboles proportionnels **en surface**, palette séquentielle.


## 9.2 Autocorrélation spatiale

> 💡 **Intuition.** La carte des ventes par délégation (9.1) semble faite d'îlots. Pour savoir si cette impression est réelle, on pose une question simple : **la valeur d'une zone ressemble-t-elle à la moyenne de ses voisines ?** Si oui, les valeurs sont *positivement autocorrélées dans l'espace*. Si les zones voisines s'opposent (une forte entourée de faibles), l'autocorrélation est *négative*. Si le voisinage n'apprend rien sur la valeur, il n'y en a pas. L'indice de Moran transforme cette question en un nombre, et un test de permutation dit si ce nombre est plus grand que ce que le hasard produirait.

### 9.2.1 Définir « voisin » : la matrice de poids

Il n'existe pas de notion de voisinage « naturelle » : c'est à nous de la **choisir**, et ce choix s'écrit sous la forme d'une matrice $W$ de taille $n\times n$, la **matrice de poids** (ou de voisinage). Son coefficient $w_{ij}\ge0$ dit à quel point la zone $j$ compte comme voisine de la zone $i$, avec $w_{ii}=0$ (une zone n'est pas sa propre voisine). Les définitions usuelles :

- **Contiguïté « tour »** (*rook*) : $w_{ij}=1$ si les zones partagent une frontière (côté) ; **contiguïté « reine »** (*queen*) : si elles partagent une frontière *ou* un coin (sur une grille : 4 contre 8 voisins).
- **$k$ plus proches voisins** : $w_{ij}=1$ si $j$ est l'un des $k$ points les plus proches de $i$. Pratique pour des points (adresses), mais $W$ n'est plus symétrique.
- **Bande de distance** : $w_{ij}=1$ si la distance entre $i$ et $j$ ne dépasse pas un seuil $d$.
- **Inverse de la distance** : $w_{ij}=1/d_{ij}^{\alpha}$, où les points proches pèsent plus.

On **standardise** presque toujours par ligne : on divise chaque ligne par sa somme, de sorte que $\sum_j w_{ij}=1$. Alors $(Wz)_i$ est la **moyenne** des valeurs des voisins de $i$, ce qui rend les formules lisibles. Notons $S_0=\sum_{i,j}w_{ij}$ la somme de tous les poids (égale à $n$ après standardisation par ligne).

Un exemple minuscule que nous garderons pour les calculs à la main : une grille $3\times3$ de neuf zones numérotées de 0 à 8 ligne par ligne, avec la contiguïté « tour ».

```python
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

def contiguite_tour(n_lig, n_col):
    """Matrice binaire des voisins par un côté (haut, bas, gauche, droite)."""
    n = n_lig * n_col
    W = np.zeros((n, n))
    for i in range(n_lig):
        for j in range(n_col):
            for di, dj in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
                if 0 <= i + di < n_lig and 0 <= j + dj < n_col:
                    W[i * n_col + j, (i + di) * n_col + (j + dj)] = 1
    return W

W3 = contiguite_tour(3, 3)
print(W3.astype(int))
print("nombre de voisins par zone :", W3.sum(axis=1).astype(int))
print("S0 (somme de tous les poids) :", int(W3.sum()))
```
<!--sortie-->
```text
[[0 1 0 1 0 0 0 0 0]
 [1 0 1 0 1 0 0 0 0]
 [0 1 0 0 0 1 0 0 0]
 [1 0 0 0 1 0 1 0 0]
 [0 1 0 1 0 1 0 1 0]
 [0 0 1 0 1 0 0 0 1]
 [0 0 0 1 0 0 0 1 0]
 [0 0 0 0 1 0 1 0 1]
 [0 0 0 0 0 1 0 1 0]]
nombre de voisins par zone : [2 3 2 3 4 3 2 3 2]
S0 (somme de tous les poids) : 24
```

Les coins ont 2 voisines, les bords 3, le centre 4 : au total $S_0=24$ liens orientés, soit 12 frontières communes comptées dans les deux sens. Pour obtenir la version standardisée par ligne, il suffit de diviser chaque ligne par sa somme.

```python
def std_lignes(W):
    """Standardise par ligne : chaque ligne somme à 1 (les lignes de zéros sont laissées intactes)."""
    s = W.sum(axis=1, keepdims=True)
    return np.divide(W, s, out=np.zeros_like(W), where=s > 0)

W3s = std_lignes(W3)
print(np.round(W3s[4], 2), "<- ligne du centre : 1/4 pour chacun de ses 4 voisins")
print("somme de chaque ligne :", W3s.sum(axis=1))
```
<!--sortie-->
```text
[0.   0.25 0.   0.25 0.   0.25 0.   0.25 0.  ] <- ligne du centre : 1/4 pour chacun de ses 4 voisins
somme de chaque ligne : [1. 1. 1. 1. 1. 1. 1. 1. 1.]
```

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

Appliquons-les à nos 144 délégations, avec la contiguïté « reine » (8 voisins). Voici d'abord le code qui a fabriqué les ventes (la même fonction est dans `build/donnees_ch09.py`). On part de bruits indépendants $e_i$ et on les propage dans l'espace par $z=(I-\rho W)^{-1}e$ : un **modèle autorégressif spatial** (SAR), où chaque zone est un reflet de ses voisines, avec une force $\rho=0{,}9$.

```python
def contiguite_reine(n_lig, n_col):
    """Voisins par un côté ou un coin (8 directions)."""
    n = n_lig * n_col
    W = np.zeros((n, n))
    for i in range(n_lig):
        for j in range(n_col):
            for di in (-1, 0, 1):
                for dj in (-1, 0, 1):
                    if (di, dj) != (0, 0) and 0 <= i + di < n_lig and 0 <= j + dj < n_col:
                        W[i * n_col + j, (i + di) * n_col + (j + dj)] = 1
    return W

def delegations(seed=9, n_lig=12, n_col=12, rho=0.9):
    rng = np.random.default_rng(seed)
    W = std_lignes(contiguite_reine(n_lig, n_col))
    n = n_lig * n_col
    e = rng.normal(size=n)
    z = np.linalg.solve(np.eye(n) - rho * W, e)               # z = (I - rho W)^-1 e
    pop = np.round(rng.lognormal(8.5, 0.5, n)).astype(int)
    lig, col = np.divmod(np.arange(n), n_col)
    return pd.DataFrame({"id": np.arange(n), "lig": lig, "col": col, "x": col * 5.0 + 2.5, "y": lig * 5.0 + 2.5,
                         "population": pop, "ventes_hab": np.round(50 + 8 * z, 2),
                         "ventes_bruit": np.round(rng.normal(50, 8, n), 2)})

deleg = delegations()
fichier = pd.read_csv("donnees/ch09-delegations.csv")
print("identique au fichier fourni :", np.allclose(deleg[["ventes_hab", "ventes_bruit"]], fichier[["ventes_hab", "ventes_bruit"]]))
print(deleg[["ventes_hab", "ventes_bruit"]].describe().round(2).to_string())
```
<!--sortie-->
```text
identique au fichier fourni : True
       ventes_hab  ventes_bruit
count      144.00        144.00
mean        52.89         50.22
std         13.51          8.15
min         19.29         29.97
25%         44.29         43.90
50%         53.43         50.36
75%         62.67         56.50
max         81.49         71.64
```

Nous disposons de deux variables : `ventes_hab` (structurée dans l'espace) et `ventes_bruit` (du bruit indépendant, **sans** structure spatiale ; sa moyenne et son écart-type sont proches de ceux de l'autre variable, sans être identiques). Cette deuxième variable est notre *témoin* : un bon indice doit y voir du hasard.

```python
W = std_lignes(contiguite_reine(12, 12))
n = len(deleg)

def stats_poids(W):
    S0 = W.sum()
    S1 = 0.5 * ((W + W.T) ** 2).sum()
    S2 = ((W.sum(axis=1) + W.sum(axis=0)) ** 2).sum()
    return S0, S1, S2

def moran_normal(y, W):
    """I, E[I], écart-type sous normalité et z_I."""
    n = len(y)
    S0, S1, S2 = stats_poids(W)
    E = -1 / (n - 1)
    var = (n**2 * S1 - n * S2 + 3 * S0**2) / ((n**2 - 1) * S0**2) - E**2
    I = moran(y, W)
    return I, E, np.sqrt(var), (I - E) / np.sqrt(var)

def moran_permutations(y, W, B=9999, seed=1):
    """B valeurs de I obtenues en mélangeant y sur les zones."""
    rng = np.random.default_rng(seed)
    z = np.asarray(y, dtype=float) - np.mean(y)
    idx = np.argsort(rng.random((B, len(z))), axis=1)          # B permutations de 0..n-1
    Z = z[idx]                                                  # chaque ligne est un mélange de z
    return len(z) / W.sum() * (((Z @ W) * Z).sum(axis=1)) / (z @ z)

lignes = []
for nom in ["ventes_hab", "ventes_bruit"]:
    y = deleg[nom].to_numpy()
    I, E, sd, zI = moran_normal(y, W)
    sim = moran_permutations(y, W)
    p_perm = (1 + (sim >= I).sum()) / (len(sim) + 1)
    lignes.append({"variable": nom, "I": I, "E[I]": E, "ecart_type": sd, "z": zI, "p_normale": stats.norm.sf(zI),
                   "p_permutation": p_perm, "sd_perm": sim.std()})
res = pd.DataFrame(lignes)
with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 150):
    print(res.to_string(index=False))
```
<!--sortie-->
```text
    variable       I      E[I]  ecart_type       z  p_normale  p_permutation  sd_perm
  ventes_hab  0.6207 -0.006993     0.04429   14.17  6.802e-46         0.0001  0.04468
ventes_bruit -0.0214 -0.006993     0.04429 -0.3253     0.6275         0.6132  0.04445
```

La variable structurée a un indice de Moran nettement positif et une p-valeur proche de la plus petite que l'on puisse obtenir avec $B=9999$ permutations (jamais 0 : le $+1$ au numérateur représente la valeur observée elle-même). Le témoin, lui, est proche de $-1/(n-1)$ et sa p-valeur est élevée. Remarquons aussi que l'écart-type obtenu par permutations est voisin de celui de la formule normale : deux voies, une même conclusion.

> ⚠️ **L'indice ne vaut pas $\rho$.** Nous avons fabriqué les données avec $\rho=0{,}9$, mais $I\ne0{,}9$. Le paramètre $\rho$ d'un modèle SAR et l'indice de Moran mesurent la dépendance **sur des échelles différentes** : $\rho$ gouverne la façon dont un choc se propage de proche en proche, alors que $I$ résume la ressemblance moyenne entre voisines **directes**. Une forte propagation ($\rho$ proche de 1) produit de grandes plages, mais la ressemblance entre deux voisines immédiates reste partielle. Ne comparez jamais $I$ à une probabilité ou à un coefficient du modèle.

On voit mieux ce que mesure $I$ avec le **diagramme de Moran** (le nuage de la moyenne des voisines contre la valeur de la zone) et l'histogramme de la distribution nulle :

```python
BLEU, ORANGE, AQUA, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#e34948"
y = deleg["ventes_hab"].to_numpy()
zc = y - y.mean()
lag = W @ zc
I_obs = moran(y, W)
sim = moran_permutations(y, W)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.4))
ax1.scatter(zc, lag, s=16, color=BLEU, alpha=0.7)
pente, ordonnee = np.polyfit(zc, lag, 1)
xs = np.array([zc.min(), zc.max()])
ax1.plot(xs, pente * xs + ordonnee, color=ORANGE, lw=2)
ax1.axhline(0, color="#999999", lw=0.8); ax1.axvline(0, color="#999999", lw=0.8)
ax1.set_xlabel("écart à la moyenne de la zone  z"); ax1.set_ylabel("moyenne des écarts des voisines  W z")
ax1.set_title(f"Diagramme de Moran (pente = I = {pente:.3f})")

ax2.hist(sim, bins=50, color="#b9d0f0", edgecolor="white")
ax2.axvline(I_obs, color=ORANGE, lw=2)
ax2.annotate(f"I observé = {I_obs:.3f}", (I_obs, 400), xytext=(-8, 0), textcoords="offset points", ha="right", color=ORANGE)
ax2.set_xlabel("I après mélange des valeurs (9999 permutations)"); ax2.set_ylabel("effectif")
ax2.set_title("Ce que produirait le hasard")
plt.tight_layout()
plt.savefig("figures/ch09-moran.png", dpi=200, bbox_inches="tight")
print("pente du diagramme :", round(pente, 4), "| I :", round(I_obs, 4), "| identiques :", np.isclose(pente, I_obs))
```
<!--sortie-->
```text
pente du diagramme : 0.6207 | I : 0.6207 | identiques : True
```

![À gauche : diagramme de Moran des ventes par habitant ; la pente de la droite est l'indice de Moran. À droite : distribution de I quand on mélange les valeurs au hasard sur les zones (hypothèse nulle) et valeur observée.](figures/ch09-moran.png)

La pente du diagramme est **égale** à l'indice de Moran, comme annoncé. L'histogramme de droite montre la loi de $I$ quand les valeurs sont distribuées au hasard : centrée sur un nombre proche de zéro, avec un étalement de l'ordre de 0,05. La valeur observée est loin à droite de cette loi : le hasard ne produit pas un tel alignement.

**La sensibilité au choix de $W$.** Le résultat dépend-il de notre définition du voisinage ? Recalculons $I$ avec cinq définitions, construites à partir des **distances** entre les centres des zones, ce qui est la façon de faire pour des points dans l'espace quelconques.

```python
xy = deleg[["x", "y"]].to_numpy()
Dd = np.sqrt(((xy[:, None, :] - xy[None, :, :]) ** 2).sum(axis=2))      # distances euclidiennes (km)

def poids_bande(D, d):
    W = ((D > 0) & (D <= d)).astype(float)
    return W

def poids_knn(D, k):
    W = np.zeros_like(D)
    for i in range(len(D)):
        voisins = np.argsort(D[i])[1:k + 1]                         # on saute la distance nulle (soi-même)
        W[i, voisins] = 1
    return W

variantes = {
    "tour (distance <= 5 km)": poids_bande(Dd, 5.0),
    "reine (distance <= 7,1 km)": poids_bande(Dd, 7.1),
    "bande de 10 km": poids_bande(Dd, 10.0),
    "4 plus proches voisins": poids_knn(Dd, 4),
    "8 plus proches voisins": poids_knn(Dd, 8),
}
lignes = []
for nom, Wv in variantes.items():
    Ws = std_lignes(Wv)
    sim_v = moran_permutations(y, Ws, B=999, seed=3)
    I_v = moran(y, Ws)
    lignes.append({"definition": nom, "voisins_moyens": Wv.sum(axis=1).mean(), "I": I_v,
                   "I_temoin": moran(deleg["ventes_bruit"].to_numpy(), Ws),
                   "p_permutation": (1 + (sim_v >= I_v).sum()) / 1000})
with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 150):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
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

```python
def geary(y, W):
    y = np.asarray(y, dtype=float)
    z = y - y.mean()
    diff2 = (y[:, None] - y[None, :]) ** 2
    return (len(y) - 1) * (W * diff2).sum() / (2 * W.sum() * (z @ z))

def geary_permutations(y, W, B=999, seed=4):
    rng = np.random.default_rng(seed)
    return np.array([geary(rng.permutation(y), W) for _ in range(B)])

lignes = []
for nom in ["ventes_hab", "ventes_bruit"]:
    yy = deleg[nom].to_numpy()
    C = geary(yy, W)
    sim_c = geary_permutations(yy, W)
    lignes.append({"variable": nom, "C": C, "moyenne_perm": sim_c.mean(), "p_perm (C petit)": (1 + (sim_c <= C).sum()) / (len(sim_c) + 1)})
with pd.option_context("display.float_format", "{:.4f}".format, "display.width", 150):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
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

```python
def lisa(y, W, B=999, seed=2):
    """Moran local, quadrant, et p-valeur bilatérale par permutation conditionnelle."""
    rng = np.random.default_rng(seed)
    y = np.asarray(y, dtype=float)
    n = len(y)
    z = y - y.mean()
    m2 = (z @ z) / n
    lag = W @ z
    Ii = z * lag / m2
    pv = np.empty(n)
    for i in range(n):
        voisins = np.flatnonzero(W[i])
        poids = W[i, voisins]
        r = rng.random((B, n))
        r[:, i] = 2.0                                           # exclut la zone i du tirage
        tire = np.argsort(r, axis=1)[:, :len(voisins)]          # valeurs tirées pour les voisins
        sim = z[i] * (z[tire] * poids).sum(axis=1) / m2
        p_haut = (1 + (sim >= Ii[i]).sum()) / (B + 1)
        p_bas = (1 + (sim <= Ii[i]).sum()) / (B + 1)
        pv[i] = min(1.0, 2 * min(p_haut, p_bas))
    quadrant = np.where(z > 0, np.where(lag > 0, "HH", "HL"), np.where(lag > 0, "LH", "LL"))
    return Ii, quadrant, pv

def benjamini_hochberg(p, alpha=0.05):
    """Renvoie un tableau booléen des hypothèses rejetées (FDR contrôlé à alpha)."""
    p = np.asarray(p)
    m = len(p)
    ordre = np.argsort(p)
    ok = p[ordre] <= (np.arange(1, m + 1) / m) * alpha
    rejet = np.zeros(m, dtype=bool)
    if ok.any():
        rejet[ordre[: np.max(np.flatnonzero(ok)) + 1]] = True
    return rejet

lignes = []
resultats = {}
for nom in ["ventes_hab", "ventes_bruit"]:
    Ii, quad, pv = lisa(deleg[nom].to_numpy(), W)
    rej = benjamini_hochberg(pv)
    resultats[nom] = (Ii, quad, pv, rej)
    comptes = pd.Series(np.where(rej, quad, "non significatif")).value_counts()
    lignes.append({"variable": nom, "somme_Ii/n": Ii.sum() / len(Ii), "I_global": moran(deleg[nom].to_numpy(), W),
                   "p<0.05 brut": int((pv < 0.05).sum()), "significatifs (BH)": int(rej.sum()),
                   "HH": int(comptes.get("HH", 0)), "LL": int(comptes.get("LL", 0)),
                   "HL": int(comptes.get("HL", 0)), "LH": int(comptes.get("LH", 0))})
with pd.option_context("display.float_format", "{:.4f}".format, "display.width", 170):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
    variable  somme_Ii/n  I_global  p<0.05 brut  significatifs (BH)  HH  LL  HL  LH
  ventes_hab      0.6207    0.6207           49                  35  11  22   0   2
ventes_bruit     -0.0214   -0.0214            5                   0   0   0   0   0
```

La première colonne vérifie la propriété annoncée : la moyenne des $I_i$ est bien l'indice de Moran global. Sur le témoin, 5 zones sur 144 (3 %, soit à peu près les 5 % attendus du hasard) sortent avec la p-valeur brute : c'est le prix des tests multiples. La correction de Benjamini-Hochberg les écarte **toutes** (0 zone significative). Sur la variable structurée, 49 zones sont significatives avant correction et 35 après : 11 îlots de fortes valeurs (HH), 22 de faibles valeurs (LL) et 2 valeurs atypiques (LH). Regardons la carte des zones significatives.

```python
couleurs = {"HH": ROUGE, "LL": BLEU, "HL": ORANGE, "LH": AQUA, "ns": "#e8e6df"}
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.8))
for ax, nom in zip(axes, ["ventes_hab", "ventes_bruit"]):
    Ii, quad, pv, rej = resultats[nom]
    cat = np.where(rej, quad, "ns").reshape(12, 12)
    for i in range(12):
        for j in range(12):
            ax.add_patch(plt.Rectangle((j * 5, i * 5), 5, 5, facecolor=couleurs[cat[i, j]], edgecolor="white", linewidth=0.8))
    ax.set_xlim(0, 60); ax.set_ylim(0, 60); ax.set_aspect("equal")
    ax.set_title("ventes par habitant (structurées)" if nom == "ventes_hab" else "témoin (bruit sans structure)", fontsize=10)
    ax.set_xlabel("x (km)")
axes[0].set_ylabel("y (km)")
poignees = [plt.Rectangle((0, 0), 1, 1, facecolor=couleurs[k]) for k in ["HH", "LL", "HL", "LH", "ns"]]
fig.legend(poignees, ["HH : haut entouré de haut", "LL : bas entouré de bas", "HL : haut entouré de bas", "LH : bas entouré de haut", "non significatif"],
           loc="lower center", ncol=5, frameon=False, fontsize=8)
plt.tight_layout(rect=(0, 0.07, 1, 1))
plt.savefig("figures/ch09-lisa.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Carte des indicateurs locaux de Moran significatifs (Benjamini-Hochberg à 5 %). À gauche, les ventes par habitant : des îlots de fortes (rouge) et de faibles (bleu) valeurs. À droite, le témoin sans structure spatiale : presque rien n'est significatif.](figures/ch09-lisa.png)

La carte de gauche **localise** les îlots : l'indice global disait *qu'il y en a*, les indices locaux disent *où*. À droite, le témoin est quasiment vide.

> ⚠️ **Deux précautions.** (1) Les indices locaux ne sont **pas indépendants** (zones voisines partagent des voisines), donc le taux de faux positifs effectif est mal maîtrisé même avec la correction de Benjamini-Hochberg : on considère les zones signalées comme des **pistes à examiner**, pas comme des découvertes. (2) Les zones **en bordure** de la carte ont moins de voisines : leurs indices sont plus bruités (nous y reviendrons à la section 9.5).

### 9.2.5 Pourquoi cela compte : la régression qui voit des relations qui n'existent pas

Revenons à l'avertissement de 9.1.1 : l'autocorrélation rend les erreurs-types usuelles **trop petites**. Mesurons-le. Nous simulons **deux variables sans aucun lien** (deux champs spatiaux SAR indépendants, avec la même force $\rho=0{,}9$ que plus haut), nous régressons l'une sur l'autre par moindres carrés ordinaires et nous testons la pente à 5 %. Si la méthode est honnête, nous devrions rejeter à tort dans environ **5 %** des cas. Nous recommençons 1 000 fois.

```python
from scipy import stats

A = np.linalg.inv(np.eye(n) - 0.9 * W)                         # (I - rho W)^-1, rho = 0,9
rng = np.random.default_rng(5)
reps = 1000
Y = A @ rng.normal(size=(n, reps))                             # 1000 champs « y », indépendants entre eux
X = A @ rng.normal(size=(n, reps))                             # 1000 champs « x », indépendants de y

# MCO vectorisée : pente et test de Student sur la pente, pour chacune des 1000 paires
xc, yc = X - X.mean(axis=0), Y - Y.mean(axis=0)
b = (xc * yc).sum(axis=0) / (xc ** 2).sum(axis=0)
res = yc - b * xc
s2 = (res ** 2).sum(axis=0) / (n - 2)
t = b / np.sqrt(s2 / (xc ** 2).sum(axis=0))
p_mco = 2 * stats.t.sf(np.abs(t), n - 2)
print("MCO : proportion de rejets à 5 % alors qu'il n'y a AUCUN lien :", round((p_mco < 0.05).mean(), 3))

# Nombre « efficace » d'observations indépendantes pour estimer une moyenne
var_y = Y.var()                                                # variance d'une zone
var_moy = Y.mean(axis=0).var()                                 # variance de la moyenne des 144 zones
print("variance d'une zone :", round(var_y, 2), "| variance de la moyenne de 144 zones :", round(var_moy, 3),
      "| si indépendantes, ce serait", round(var_y / n, 3))
print("nombre efficace d'observations indépendantes :", round(var_y / var_moy, 1), "sur", n)
```
<!--sortie-->
```text
MCO : proportion de rejets à 5 % alors qu'il n'y a AUCUN lien : 0.459
variance d'une zone : 3.9 | variance de la moyenne de 144 zones : 0.706 | si indépendantes, ce serait 0.027
nombre efficace d'observations indépendantes : 5.5 sur 144
```

Le résultat est sans appel : au lieu des 5 % promis, le test usuel rejette à tort dans **46 %** des cas, presque une fois sur deux. Et pour estimer une moyenne, nos 144 zones valent environ **5,5 observations indépendantes** : la variance de la moyenne est de 0,71, contre 0,027 si les zones étaient indépendantes. Le test usuel suppose des erreurs indépendantes ; ici elles ne le sont pas, et l'erreur-type de la pente est sous-estimée d'un facteur important.

> 💡 **Le remède, dans son principe.** Il faut tenir compte de la dépendance dans le calcul. Si l'on **connaissait** la structure de covariance $\Sigma$ des erreurs, on appliquerait les **moindres carrés généralisés** (MCG), c'est-à-dire des moindres carrés sur des données *blanchies*. Pour notre modèle SAR, le blanchiment est explicite : multiplier le vecteur $y$ par $(I-\rho W)$ « défait » la propagation. Vérifions que cela rétablit le niveau du test, en supposant ici $\rho$ connu (c'est le cas idéal ; en pratique on l'estime).

```python
T = np.eye(n) - 0.9 * W                                        # opérateur de blanchiment (rho connu)
un = np.ones(n)
rejets = 0
for r in range(reps):
    ys = T @ Y[:, r]
    Xs = np.column_stack([T @ un, T @ X[:, r]])               # constante et x, blanchis
    coef, *_ = np.linalg.lstsq(Xs, ys, rcond=None)
    resid = ys - Xs @ coef
    s2 = resid @ resid / (n - 2)
    cov = s2 * np.linalg.inv(Xs.T @ Xs)
    tt = coef[1] / np.sqrt(cov[1, 1])
    rejets += 2 * stats.t.sf(abs(tt), n - 2) < 0.05
print("MCG avec rho connu : proportion de rejets à 5 % :", rejets / reps)

# Et dans une seule paire (la première) : les résidus des MCO révèlent le problème
Xd = np.column_stack([np.ones(n), X[:, 0]])
beta = np.linalg.lstsq(Xd, Y[:, 0], rcond=None)[0]
residus = Y[:, 0] - Xd @ beta
sim_r = moran_permutations(residus, W, B=999, seed=6)
print("Moran des résidus MCO (première paire) :", round(moran(residus, W), 3),
      "| p-valeur par permutation :", round((1 + (sim_r >= moran(residus, W)).sum()) / 1000, 3))
```
<!--sortie-->
```text
MCG avec rho connu : proportion de rejets à 5 % : 0.053
Moran des résidus MCO (première paire) : 0.425 | p-valeur par permutation : 0.001
```

Avec les moindres carrés généralisés, le niveau du test retombe à 5,3 %, tout près des 5 % annoncés. Et, comme le montre la dernière ligne, il existe un **signal d'alarme** simple pour une analyse réelle : calculer l'indice de Moran des **résidus** du modèle. S'il est significatif, les erreurs ne sont pas indépendantes et les erreurs-types usuelles sont à écarter.

> 🛠️ **En pratique.** On ne connaît pas $\rho$ : on l'estime avec un **modèle autorégressif spatial** (le *spatial lag* ou le *spatial error model*, estimés par maximum de vraisemblance), ou l'on modélise la covariance par un variogramme (section 9.3, krigeage universel), ou l'on utilise des **erreurs-types robustes par blocs spatiaux**. Les outils exacts sortent du cadre de ce chapitre, mais le message est général : *si vos observations sont proches dans l'espace, testez l'autocorrélation des résidus avant de lire vos p-valeurs.*

> ✅ **À retenir.**
> - Pour parler d'autocorrélation, il faut **définir le voisinage** : une matrice de poids $W$ (contiguïté, $k$ voisins, bande de distance), presque toujours standardisée par ligne. Ce choix fait partie du résultat.
> - **Indice de Moran** : $I=\frac{n}{S_0}\frac{\sum w_{ij}z_iz_j}{\sum z_i^2}$. Avec $W$ standardisée, c'est la pente de « moyenne des voisines » contre « valeur de la zone ». Sous l'hypothèse nulle, $\mathbb E[I]=-1/(n-1)$ ; on le teste par **permutations**.
> - **Geary** ($\mathbb E[C]=1$, $C<1$ pour une autocorrélation positive) est plus sensible aux différences locales.
> - Les **indices locaux** (LISA) disent *où* sont les îlots (HH, LL) et les valeurs atypiques (HL, LH) ; avec 144 tests, il faut **corriger** (Benjamini-Hochberg).
> - Ignorer l'autocorrélation fait **rejeter à tort** bien plus souvent que 5 % : testez l'indice de Moran des résidus avant de croire une p-valeur.


## 9.3 Variogramme et krigeage

> 💡 **Intuition.** Yasmine veut promettre un délai à une cliente de Zaghouan, où personne n'a encore été livré. Que peut-on dire ? Les livraisons **proches** de cette adresse sont informatives, celles qui sont loin le sont moins, et deux livraisons voisines l'une de l'autre se répètent (elles apportent à peu près la même information). Le **variogramme** mesure à quelle vitesse la ressemblance entre deux mesures s'estompe quand la distance augmente. Le **krigeage** s'en sert pour fabriquer, en tout point, la **meilleure moyenne pondérée** des mesures voisines, avec une **marge d'erreur**.

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

où $N(h)$ est l'ensemble des paires dont la distance est « à peu près » $h$ (on découpe les distances en **classes** de largeur fixe) et $N(h)$ leur nombre. Le code suivant fabrique cet estimateur. Nous le validons d'abord sur les quatre points ci-dessus.

```python
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats, optimize

def distances(P, Q=None):
    Q = P if Q is None else Q
    return np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(axis=2))

def variogramme_empirique(coords, z, largeur=5.0, hmax=50.0, angle=None, tol=22.5):
    """Semi-variogramme empirique par classes de distance. Si `angle` (en degrés, 0 = est, 90 = nord)
    est donné, on ne garde que les paires orientées dans cette direction (à +/- tol degrés près)."""
    n = len(z)
    i, j = np.triu_indices(n, 1)
    h = distances(coords)[i, j]
    g = 0.5 * (z[i] - z[j]) ** 2
    garde = np.ones(len(h), dtype=bool)
    if angle is not None:
        theta = np.degrees(np.arctan2(coords[j, 1] - coords[i, 1], coords[j, 0] - coords[i, 0])) % 180
        ecart = np.abs(theta - angle)
        garde = np.minimum(ecart, 180 - ecart) <= tol
    classes = np.arange(0, hmax + largeur, largeur)
    lignes = []
    for a, b in zip(classes[:-1], classes[1:]):
        m = garde & (h > a) & (h <= b)
        if m.any():
            lignes.append({"h": h[m].mean(), "gamma": g[m].mean(), "paires": int(m.sum())})
    return pd.DataFrame(lignes)

# Validation sur les quatre points de l'exemple à la main (classes de 1 km)
P4 = np.array([[0.0, 0], [1, 0], [2, 0], [3, 0]])
z4 = np.array([2.0, 3, 5, 4])
print(variogramme_empirique(P4, z4, largeur=1.0, hmax=3.0).to_string(index=False))
```
<!--sortie-->
```text
  h  gamma  paires
1.0    1.0       3
2.0    2.5       2
3.0    2.0       1
```

Les trois lignes redonnent nos calculs à la main : 1,0 ; 2,5 ; 2,0. Passons aux 200 livraisons. Voici d'abord le code qui les a fabriquées, c'est-à-dire la **vérité** que nous allons chercher à retrouver (nous ne la regarderons qu'après l'analyse). C'est un champ aléatoire gaussien stationnaire de covariance exponentielle, observé avec un bruit de mesure.

```python
def livraisons(seed=27, n=200, cote=100.0, sill=1.0, a=12.0, pepite=0.4, moyenne=4.0):
    rng = np.random.default_rng(seed)
    g = np.linspace(2, cote - 2, 25)                          # grille de prédiction 25 x 25
    gx, gy = np.meshgrid(g, g)
    grille = np.column_stack([gx.ravel(), gy.ravel()])
    obs = rng.uniform(0, cote, size=(n, 2))
    pts = np.vstack([obs, grille])
    C = sill * np.exp(-distances(pts) / a)                     # covariance exponentielle C(h) = sill * exp(-h/a)
    champ = moyenne + np.linalg.cholesky(C + 1e-8 * np.eye(len(pts))) @ rng.normal(size=len(pts))
    z = champ[:n] + rng.normal(0, np.sqrt(pepite), n)         # champ + bruit de mesure (la pépite)
    df = pd.DataFrame({"x": np.round(obs[:, 0], 2), "y": np.round(obs[:, 1], 2), "delai_jours": np.round(z, 3)})
    df["pli"] = rng.permutation(np.arange(n) % 5)             # 5 plis pour la validation croisée
    verite = pd.DataFrame({"x": grille[:, 0], "y": grille[:, 1], "champ": champ[n:]})
    return df, verite

liv, verite = livraisons()
fichier = pd.read_csv("donnees/ch09-livraisons.csv")
print("identique au fichier fourni :", np.allclose(liv[["x", "y", "delai_jours"]], fichier[["x", "y", "delai_jours"]]))
coords = liv[["x", "y"]].to_numpy()
z = liv["delai_jours"].to_numpy()
print(f"n = {len(z)} | moyenne = {z.mean():.2f} jours | variance = {z.var(ddof=1):.2f}")
```
<!--sortie-->
```text
identique au fichier fourni : True
n = 200 | moyenne = 4.27 jours | variance = 1.21
```

Calculons le variogramme empirique de ces données, avec des classes de 5 km jusqu'à 50 km (la moitié de la taille du domaine : au-delà, les paires deviennent rares et dépendent de la forme du domaine, c'est la règle de pouce usuelle).

```python
emp = variogramme_empirique(coords, z, largeur=5.0, hmax=50.0)
print(emp.round(3).to_string(index=False))
```
<!--sortie-->
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

```python
def gamma_sph(h, c0, c, a):
    h = np.asarray(h, dtype=float)
    g = np.where(h < a, c0 + c * (1.5 * h / a - 0.5 * (h / a) ** 3), c0 + c)
    return np.where(h > 0, g, 0.0)

def gamma_exp(h, c0, c, a):
    h = np.asarray(h, dtype=float)
    return np.where(h > 0, c0 + c * (1 - np.exp(-h / a)), 0.0)

def gamma_gau(h, c0, c, a):
    h = np.asarray(h, dtype=float)
    return np.where(h > 0, c0 + c * (1 - np.exp(-(h / a) ** 2)), 0.0)

MODELES = {"sphérique": gamma_sph, "exponentiel": gamma_exp, "gaussien": gamma_gau}
PORTEE_PRATIQUE = {"sphérique": lambda a: a, "exponentiel": lambda a: 3 * a, "gaussien": lambda a: np.sqrt(3) * a}

def ajuster(emp, modele, v0=None):
    """Ajuste (c0, c, a) par moindres carrés pondérés (poids de Cressie) ; renvoie les paramètres et le critère."""
    h, g, N = emp["h"].to_numpy(), emp["gamma"].to_numpy(), emp["paires"].to_numpy()
    v = g.max() if v0 is None else v0
    def residus(p):
        return np.sqrt(N) * (g / np.maximum(modele(h, *p), 1e-9) - 1)
    meilleur = None
    for a0 in (h.max() / 6, h.max() / 3, h.max() / 1.5):          # plusieurs départs : le critère n'est pas convexe
        r = optimize.least_squares(residus, x0=[0.1 * v, v, a0], bounds=([0, 1e-6, 1e-3], [10 * v, 10 * v, 10 * h.max()]))
        if meilleur is None or r.cost < meilleur.cost:
            meilleur = r
    return meilleur.x, 2 * meilleur.cost

lignes, ajustements = [], {}
for nom, f in MODELES.items():
    p, crit = ajuster(emp, f)
    ajustements[nom] = p
    lignes.append({"modele": nom, "pepite": p[0], "palier_partiel": p[1], "palier_total": p[0] + p[1],
                   "param_a": p[2], "portee_pratique_km": PORTEE_PRATIQUE[nom](p[2]), "critere": crit})
with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 150):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
     modele  pepite  palier_partiel  palier_total  param_a  portee_pratique_km  critere
  sphérique   0.215           1.065         1.280   20.792              20.792   48.096
exponentiel   0.038           1.277         1.315    8.136              24.407   47.196
   gaussien   0.390           0.893         1.283   10.436              18.075   48.425
```

Les trois modèles proposent un **palier total** voisin (entre 1,28 et 1,32), mais des décompositions différentes entre pépite et portée : le modèle exponentiel trouve presque une pépite nulle et une portée pratique d'environ 24 km, le gaussien une pépite de 0,39 et une portée de 18 km. Leurs **critères** d'ajustement sont très proches (47,2 pour l'exponentiel, 48,1 et 48,4 pour les deux autres) : l'exponentiel est légèrement meilleur, mais **les données ne permettent pas de trancher** entre les formes. Regardons-les sur la figure.

```python
BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
hh = np.linspace(0.01, 50, 300)
fig, ax = plt.subplots(figsize=(7.4, 4.6))
ax.scatter(emp["h"], emp["gamma"], s=np.sqrt(emp["paires"]) * 3, color="#444444", zorder=3, label="empirique (taille = nb de paires)")
for (nom, f), couleur in zip(MODELES.items(), [AQUA, ORANGE, VIOLET]):
    ax.plot(hh, f(hh, *ajustements[nom]), color=couleur, lw=2, label=nom)
ax.axhline(z.var(ddof=1), color="#999999", lw=0.8, ls="--")
ax.annotate("variance empirique des données", (50, z.var(ddof=1)), xytext=(-4, 4), textcoords="offset points", ha="right", fontsize=8, color="#666666")
ax.set_xlabel("distance h (km)"); ax.set_ylabel("semi-variance  γ(h)  (jours²)")
ax.set_title("Variogramme empirique des délais de livraison et trois modèles ajustés")
ax.set_xlim(0, 52); ax.set_ylim(0, None)
ax.legend(frameon=False, loc="lower right", fontsize=8)
plt.tight_layout()
plt.savefig("figures/ch09-variogramme.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Variogramme empirique (points, taille proportionnelle au nombre de paires) et trois modèles ajustés. La ligne pointillée est la variance empirique des données, voisine du palier.](figures/ch09-variogramme.png)

> 🧪 **La vérité terrain.** Les données sont simulées : nous connaissons la bonne réponse. C'est un champ de covariance exponentielle $C(h)=1{,}0\,e^{-h/12}$, soit un palier partiel $c=1{,}0$ et un paramètre $a=12$ (portée pratique 36 km), observé avec une **pépite** de $0{,}4$ (palier total $1{,}4$). Comparons avec la ligne « exponentiel » du tableau : le **palier total** est bien retrouvé (1,32 contre 1,4), mais la **pépite** est très sous-estimée (0,04 contre 0,4) et la **portée pratique** aussi (24 km contre 36 km). Ce qui est facile à estimer, c'est la variance totale ; ce qui est difficile, c'est sa répartition entre bruit de mesure et dépendance spatiale. La suite montre que ce n'est pas une particularité de notre tirage.

**Cet ajustement est-il typique ?** Une seule série de 200 mesures est un seul tirage ; il est légitime de se demander ce qui se passerait avec d'autres tirages du même processus. Faisons l'expérience : nous répétons la simulation avec 30 graines différentes, nous réajustons à chaque fois le modèle exponentiel et nous regardons la dispersion des paramètres estimés.

```python
rangs = []
for s in range(100, 130):
    d_s, _ = livraisons(seed=s)
    e_s = variogramme_empirique(d_s[["x", "y"]].to_numpy(), d_s["delai_jours"].to_numpy())
    p, _ = ajuster(e_s, gamma_exp)
    rangs.append({"pepite": p[0], "palier_partiel": p[1], "param_a": p[2], "portee_pratique": 3 * p[2], "palier_total": p[0] + p[1]})
rangs = pd.DataFrame(rangs)
verite_p = {"pepite": 0.4, "palier_partiel": 1.0, "param_a": 12.0, "portee_pratique": 36.0, "palier_total": 1.4}
resume = pd.DataFrame({"vérité": pd.Series(verite_p), "médiane": rangs.median(), "10e perc.": rangs.quantile(0.10), "90e perc.": rangs.quantile(0.90)})
print(resume.round(2).to_string())
```
<!--sortie-->
```text
                 vérité  médiane  10e perc.  90e perc.
pepite              0.4     0.35       0.10       0.54
palier_partiel      1.0     1.04       0.78       1.38
param_a            12.0     9.64       5.29      17.33
portee_pratique    36.0    28.92      15.88      52.00
palier_total        1.4     1.38       1.05       1.63
```

> ⚠️ **Ce qu'il faut retenir de cette expérience.** Sur 30 tirages, le palier total est estimé avec une assez bonne précision (médiane 1,38 pour une vérité de 1,4), mais la pépite varie de 0,10 à 0,54 (entre le 10e et le 90e percentile) et la portée pratique de 16 à 52 km, pour des vérités de 0,4 et 36 km. La **médiane** de la portée pratique (29 km) est elle-même inférieure à la vérité : l'ajustement a tendance à la sous-estimer. Notre tirage (pépite 0,04, portée 24 km) est dans la queue basse de la distribution, sans être aberrant. Même avec 200 points, les paramètres du variogramme sont donc **peu précis** : la pépite et la portée sont particulièrement difficiles à identifier, parce que l'une et l'autre se jouent dans les toutes premières classes de distance, qui contiennent peu de paires. Ce n'est pas un défaut de notre code, c'est la nature du problème. Deux conséquences pratiques : (1) ne jamais donner un variogramme ajusté comme un fait certain, (2) comme nous le verrons, le **krigeage** est heureusement assez peu sensible aux petites erreurs de variogramme.

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

**Un exemple à la main.** Prenons le cas le plus simple : une dimension, un variogramme **linéaire** $\gamma(h)=h$, deux points de mesure à $x=0$ (valeur 10) et $x=3$ (valeur 16), et une cible à $x=1$. Alors $\Gamma=\begin{pmatrix}0&3\\3&0\end{pmatrix}$ et $\gamma_0=(1,2)^\top$. Le système s'écrit $3\lambda_2+m=1$, $3\lambda_1+m=2$, $\lambda_1+\lambda_2=1$. En soustrayant les deux premières équations, $3(\lambda_1-\lambda_2)=1$, donc $\lambda_1=\tfrac23$, $\lambda_2=\tfrac13$ et $m=0$. La prédiction vaut $\tfrac23\times10+\tfrac13\times16=12$ et la variance $\lambda^\top\gamma_0+m=\tfrac23+\tfrac23+0=\tfrac43$. Ce résultat porte un enseignement : **dans ce cas particulier, le krigeage est l'interpolation linéaire** (de 10 à 16 en trois km, soit 12 à 1 km). Vérifions avec une fonction générale.

```python
def krigeage_ordinaire(coords, z, cibles, modele, params):
    """Krigeage ordinaire : renvoie prédictions, variances de krigeage et poids (une colonne par cible)."""
    n = len(z)
    G = modele(distances(coords), *params)                       # Gamma (diagonale nulle)
    A = np.zeros((n + 1, n + 1))
    A[:n, :n] = G
    A[:n, n] = 1.0
    A[n, :n] = 1.0
    g0 = modele(distances(coords, cibles), *params)              # gamma_0, une colonne par cible
    B = np.vstack([g0, np.ones((1, cibles.shape[0]))])
    sol = np.linalg.solve(A, B)
    lam, m = sol[:n], sol[n]
    pred = lam.T @ z
    var = (lam * g0).sum(axis=0) + m
    return pred, var, lam

lineaire = lambda h, pente: np.where(np.asarray(h) > 0, pente * np.asarray(h), 0.0)
pred, var, lam = krigeage_ordinaire(np.array([[0.0, 0], [3, 0]]), np.array([10.0, 16.0]), np.array([[1.0, 0]]), lineaire, (1.0,))
print("poids :", lam.ravel().round(4), "| prédiction :", pred.round(4), "| variance :", var.round(4))
```
<!--sortie-->
```text
poids : [0.6667 0.3333] | prédiction : [12.] | variance : [1.3333]
```

Nous retrouvons les poids $\frac23,\frac13$, la prédiction 12 et la variance $\frac43$ du calcul à la main. Revenons aux livraisons, avec le modèle **exponentiel** ajusté. Prédisons d'abord en un point précis, par exemple l'adresse $(40,\,60)$, et examinons les poids.

```python
mod, par = gamma_exp, ajustements["exponentiel"]
cible = np.array([[40.0, 60.0]])
pred, var, lam = krigeage_ordinaire(coords, z, cible, mod, par)
lam = lam.ravel()
dist = distances(coords, cible).ravel()
ordre = np.argsort(-np.abs(lam))[:6]
print(f"prédiction en (40, 60) : {pred[0]:.2f} jours | écart-type de krigeage : {np.sqrt(var[0]):.2f} jour")
print("somme des poids :", round(lam.sum(), 6), "| poids négatifs :", int((lam < 0).sum()), "sur", len(lam),
      f"| plus petit : {lam.min():.3f} | plus grand : {lam.max():.3f}")
print(pd.DataFrame({"distance_km": dist[ordre], "poids": lam[ordre], "delai": z[ordre]}).round(3).to_string(index=False))
```
<!--sortie-->
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

```python
grille = verite[["x", "y"]].to_numpy()
pred_k, var_k, _ = krigeage_ordinaire(coords, z, grille, mod, par)

def idw(coords, z, cibles, puissance=2.0):
    d = np.maximum(distances(cibles, coords), 1e-9)
    w = 1.0 / d ** puissance
    return (w * z).sum(axis=1) / w.sum(axis=1)

pred_i = idw(coords, z, grille)
vrai = verite["champ"].to_numpy()
rmse = lambda a, b: float(np.sqrt(np.mean((a - b) ** 2)))
print("RMSE par rapport au VRAI champ sur les 625 points de la grille :")
print(f"  moyenne globale          : {rmse(np.full_like(vrai, z.mean()), vrai):.3f}")
print(f"  inverse de la distance^2 : {rmse(pred_i, vrai):.3f}")
print(f"  krigeage ordinaire       : {rmse(pred_k, vrai):.3f}")
print(f"écart-type de krigeage : de {np.sqrt(var_k.min()):.2f} à {np.sqrt(var_k.max()):.2f} jour (moyenne {np.sqrt(var_k).mean():.2f})")
```
<!--sortie-->
```text
RMSE par rapport au VRAI champ sur les 625 points de la grille :
  moyenne globale          : 0.916
  inverse de la distance^2 : 0.671
  krigeage ordinaire       : 0.645
écart-type de krigeage : de 0.35 à 1.08 jour (moyenne 0.77)
```

Dessinons le vrai champ, la prédiction par krigeage et l'écart-type de krigeage.

```python
fig, axes = plt.subplots(1, 3, figsize=(13.5, 4.4))
vmin, vmax = min(vrai.min(), pred_k.min()), max(vrai.max(), pred_k.max())
cartes = [(vrai, "Vrai champ (connu par simulation)", "Oranges", dict(vmin=vmin, vmax=vmax)),
          (pred_k, "Krigeage : prédiction", "Oranges", dict(vmin=vmin, vmax=vmax)),
          (np.sqrt(var_k), "Krigeage : écart-type d'erreur", "Purples", {})]
for ax, (champ, titre, cmap, kw) in zip(axes, cartes):
    im = ax.imshow(champ.reshape(25, 25), origin="lower", extent=(0, 100, 0, 100), cmap=cmap, **kw)
    ax.set_title(titre, fontsize=10)
    ax.set_xlabel("x (km)")
    fig.colorbar(im, ax=ax, shrink=0.78)
    if "écart-type" in titre:
        ax.scatter(coords[:, 0], coords[:, 1], s=5, color="#222222", alpha=0.6)
axes[0].set_ylabel("y (km)")
plt.tight_layout()
plt.savefig("figures/ch09-krigeage.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![De gauche à droite : le vrai champ de délais (connu car simulé), la prédiction par krigeage ordinaire à partir des 200 mesures, et l'écart-type d'erreur de krigeage (les points noirs sont les 200 livraisons mesurées). L'incertitude est faible près des mesures et monte dans les zones qui en sont éloignées.](figures/ch09-krigeage.png)

Contre le vrai champ, le krigeage obtient une erreur quadratique de 0,645 jour, contre 0,916 pour la moyenne globale (30 % de moins) et 0,671 pour l'inverse de la distance : l'IDW fait presque aussi bien (4 % d'écart), ce qui rappelle qu'une moyenne pondérée bien choisie est déjà un bon prédicteur. L'avantage décisif du krigeage n'est pas là, mais dans la carte de droite. La carte du centre reproduit les grandes structures du vrai champ, en plus lisse (le krigeage est une moyenne : il **lisse** et sous-estime donc les extrêmes). La carte de droite est une originalité du krigeage : elle dit **où la prédiction est fiable**, avant même d'avoir livré. Dans la pratique, c'est la carte qui guide le choix des **prochains points de mesure** : on va mesurer là où l'incertitude est la plus grande.

De quoi dépend cette incertitude ? Mesurons-le : pour chaque point de la grille, la distance au point de mesure le plus proche, et la façon dont l'écart-type de krigeage évolue avec elle, puis une comparaison entre les points proches d'un bord du domaine et les autres.

```python
dmin = distances(grille, coords).min(axis=1)                     # distance au point mesuré le plus proche
sd_k = np.sqrt(var_k)
bord = np.minimum.reduce([grille[:, 0], 100 - grille[:, 0], grille[:, 1], 100 - grille[:, 1]])
print("corrélation entre l'écart-type de krigeage et la distance au point le plus proche :", round(np.corrcoef(sd_k, dmin)[0, 1], 3))
for a_, b_ in [(0, 2), (2, 4), (4, 6), (6, 10)]:
    m = (dmin >= a_) & (dmin < b_)
    print(f"  points de grille à {a_}-{b_} km d'une mesure : {int(m.sum()):3d} points, écart-type moyen {sd_k[m].mean():.2f} jour")
print(f"écart-type moyen à moins de 8 km d'un bord : {sd_k[bord < 8].mean():.3f} | à l'intérieur : {sd_k[bord >= 8].mean():.3f}")
```
<!--sortie-->
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

```python
plis = liv["pli"].to_numpy()
pred_cv = {"moyenne": np.empty(len(z)), "IDW": np.empty(len(z)), "krigeage": np.empty(len(z))}
sig_cv = np.empty(len(z))
for k in range(5):
    tr, te = plis != k, plis == k
    emp_k = variogramme_empirique(coords[tr], z[tr])
    p_k, _ = ajuster(emp_k, gamma_exp)                            # variogramme réajusté sur l'entraînement
    pk, vk, _ = krigeage_ordinaire(coords[tr], z[tr], coords[te], gamma_exp, p_k)
    pred_cv["krigeage"][te] = pk
    sig_cv[te] = np.sqrt(vk)
    pred_cv["IDW"][te] = idw(coords[tr], z[tr], coords[te])
    pred_cv["moyenne"][te] = z[tr].mean()

tab = pd.DataFrame({nom: {"RMSE (jours)": rmse(p, z), "biais moyen": float(np.mean(p - z))} for nom, p in pred_cv.items()}).T
print(tab.round(3).to_string())
std_res = (z - pred_cv["krigeage"]) / sig_cv
couvert = np.mean(np.abs(z - pred_cv["krigeage"]) <= 1.96 * sig_cv)
print(f"\nrésidus standardisés du krigeage : moyenne = {std_res.mean():.3f}, variance = {std_res.var(ddof=1):.3f}  (visé : 0 et 1)")
print(f"couverture des intervalles de krigeage à 95 % : {couvert:.3f}")
```
<!--sortie-->
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

**Une alternative sans variogramme : un lissage par spline.** On peut aussi prédire le délai comme une fonction lisse $f(x,y)$ des coordonnées, par une **spline de plaque mince**, comme le fait `mgcv` en R (le modèle additif généralisé de la section 2.5 de ce volume). Voici le même protocole de validation croisée, avec les mêmes plis :

```r
library(mgcv)
d <- read.csv("donnees/ch09-livraisons.csv")
pred <- numeric(nrow(d))
for (k in 0:4) {
  tr <- d[d$pli != k, ]
  te <- d[d$pli == k, ]
  g <- gam(delai_jours ~ s(x, y, k = 60), data = tr, method = "REML")
  pred[d$pli == k] <- predict(g, newdata = te)
}
cat("RMSE par validation croisée (spline de plaque mince, mgcv) :", round(sqrt(mean((d$delai_jours - pred)^2)), 3), "\n")
cat("biais moyen :", round(mean(pred - d$delai_jours), 3), "\n")
```
<!--sortie-->
```text
Loading required package: nlme
This is mgcv 1.9-1. For overview type 'help("mgcv-package")'.
RMSE par validation croisée (spline de plaque mince, mgcv) : 0.974 
biais moyen : 0.009 
```

La spline obtient une erreur de 0,974 jour, quasiment identique à celle du krigeage (0,969), ce qui n'a rien de surprenant : les deux sont des **lisseurs linéaires** du même type, et le krigeage avec variogramme exponentiel a une interprétation proche. Les avantages propres du krigeage sont (1) un **modèle explicite de la dépendance** (pépite, portée, que l'on peut interpréter), (2) des **variances de prédiction** natives (la spline en fournit aussi, par ses erreurs-types, avec d'autres hypothèses).

### 9.3.7 Les limites : tendance, anisotropie, extrapolation

**Si la moyenne n'est pas constante.** Le variogramme présuppose un processus stationnaire. Si la moyenne varie dans l'espace (une **tendance** : par exemple, les délais augmentent avec l'éloignement du dépôt), le variogramme empirique **monte sans jamais se stabiliser**, parce que les paires éloignées diffèrent aussi par leur niveau moyen. Illustrons-le en ajoutant aux délais une tendance linéaire de $0{,}04$ jour par km vers l'est, puis en l'ôtant par régression avant de calculer le variogramme.

```python
z_tend = z + 0.04 * coords[:, 0]                                  # tendance ajoutée : +0,04 jour/km vers l'est
X = np.column_stack([np.ones(len(z)), coords])
beta = np.linalg.lstsq(X, z_tend, rcond=None)[0]
z_res = z_tend - X @ beta                                         # résidus de la régression sur (x, y)
e_tend = variogramme_empirique(coords, z_tend, largeur=5.0, hmax=70.0)
e_res = variogramme_empirique(coords, z_res, largeur=5.0, hmax=70.0)
e_ref = variogramme_empirique(coords, z, largeur=5.0, hmax=70.0)
print("tendance estimée par régression : ", beta.round(3), "(constante, pente en x, pente en y)")
print(pd.DataFrame({"h": e_ref["h"].round(1), "sans_tendance": e_ref["gamma"], "avec_tendance": e_tend["gamma"],
                    "tendance_retiree": e_res["gamma"]}).round(2).iloc[[1, 3, 5, 7, 9, 11, 13]].to_string(index=False))
```
<!--sortie-->
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

```python
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.2))
ax1.plot(e_ref["h"], e_ref["gamma"], "o-", color=AQUA, label="sans tendance")
ax1.plot(e_tend["h"], e_tend["gamma"], "o-", color=ROUGE, label="avec une tendance linéaire non retirée")
ax1.plot(e_res["h"], e_res["gamma"], "o-", color=BLEU, label="tendance retirée par régression")
ax1.set_xlabel("distance h (km)"); ax1.set_ylabel("semi-variance (jours²)"); ax1.set_title("Une tendance fait « monter » le variogramme")
ax1.legend(frameon=False, fontsize=8, loc="upper left")
for angle, couleur, nom in [(0, ORANGE, "est-ouest (0°)"), (90, VIOLET, "nord-sud (90°)")]:
    e_dir = variogramme_empirique(coords, z, largeur=7.5, hmax=45.0, angle=angle, tol=22.5)
    ax2.plot(e_dir["h"], e_dir["gamma"], "o-", color=couleur, label=nom)
e_om = variogramme_empirique(coords, z, largeur=7.5, hmax=45.0)
ax2.plot(e_om["h"], e_om["gamma"], "--", color="#444444", label="toutes directions")
ax2.set_xlabel("distance h (km)"); ax2.set_ylabel("semi-variance (jours²)"); ax2.set_title("Variogrammes directionnels")
ax2.legend(frameon=False, fontsize=8, loc="lower right")
plt.tight_layout()
plt.savefig("figures/ch09-limites-variogramme.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![À gauche : variogramme des délais sans tendance (vert), avec une tendance linéaire ajoutée (rouge, qui ne se stabilise pas), et après retrait de la tendance par régression (bleu). À droite : variogrammes directionnels est-ouest et nord-sud, comparés au variogramme toutes directions confondues.](figures/ch09-limites-variogramme.png)

À gauche, la tendance non retirée fait monter le variogramme bien au-delà du palier (de 0,84 à 3,29 entre 8 et 67 km), alors que le retrait de la tendance par régression redonne une courbe presque identique à celle sans tendance. La régression retrouve d'ailleurs la tendance ajoutée : une pente de 0,042 jour par km vers l'est pour 0,04 en vérité, et une pente nulle (−0,003) vers le nord. À droite, les deux directions **ne sont pas superposées** : la courbe nord-sud est au-dessus de la courbe est-ouest à toutes les distances. Faut-il y voir de l'**anisotropie** ? Avec des données réelles, on ne peut pas le savoir d'emblée : des variogrammes directionnels sont calculés sur des secteurs d'angle étroits, donc sur **moins de paires**, et sont bruités. La bonne démarche est de **calibrer** ce que le hasard seul produit. Résumons l'écart par un rapport moyen $\gamma_{\text{N-S}}/\gamma_{\text{E-O}}$ sur les classes de distance, puis calculons le même rapport sur 60 jeux simulés **isotropes** (le même processus, 60 autres graines).

```python
def rapport_ns_eo(c, zz):
    ns_ = variogramme_empirique(c, zz, largeur=7.5, hmax=45.0, angle=90, tol=22.5)["gamma"].to_numpy()
    eo_ = variogramme_empirique(c, zz, largeur=7.5, hmax=45.0, angle=0, tol=22.5)["gamma"].to_numpy()
    m_ = min(len(ns_), len(eo_))
    return float(np.mean(ns_[:m_] / eo_[:m_]))

r_obs = rapport_ns_eo(coords, z)
r_sim = []
for s_ in range(100, 160):
    d_s, _ = livraisons(seed=s_)
    r_sim.append(rapport_ns_eo(d_s[["x", "y"]].to_numpy(), d_s["delai_jours"].to_numpy()))
r_sim = np.array(r_sim)
print(f"rapport N-S / E-O observé : {r_obs:.3f}")
print(f"rapport sur 60 jeux isotropes : médiane {np.median(r_sim):.3f}, 10e-90e percentiles {np.percentile(r_sim, 10):.3f} - {np.percentile(r_sim, 90):.3f}")
print(f"part des jeux isotropes dont le rapport est au moins aussi grand : {np.mean(r_sim >= r_obs):.3f}")
```
<!--sortie-->
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


## 9.4 Processus ponctuels

> 💡 **Intuition.** Jusqu'ici, les lieux étaient donnés (les 144 délégations, les adresses de livraison choisies par les clients) et c'était la **valeur** qui était aléatoire. Maintenant, ce sont les **positions** elles-mêmes qui sont le phénomène : où habitent les clients de la boutique de la médina ? Sont-ils éparpillés au hasard, **regroupés** en quartiers (une publicité, un bouche-à-oreille) ou étonnamment **bien espacés** (chacun choisit une adresse à distance des autres) ? Pour répondre, on compare ce que l'on observe à ce que produirait le **hasard complet**.

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

```python
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

COTE = 10.0                                  # fenêtre carrée de 10 km de côté
AIRE = COTE ** 2                             # 100 km²

def distances(P, Q=None):
    Q = P if Q is None else Q
    return np.sqrt(((P[:, None, :] - Q[None, :, :]) ** 2).sum(axis=2))

def semis_poisson(n, rng):
    """CSR conditionnel à n : n points indépendants et uniformes."""
    return rng.uniform(0, COTE, size=(n, 2))

def semis_thomas(kappa, mu, sigma, rng):
    """Agrégat de Thomas : centres de Poisson (densité kappa), mu descendants en moyenne, étalement sigma."""
    marge = 3 * sigma                                            # on génère aussi des centres hors fenêtre
    n_centres = rng.poisson(kappa * (COTE + 2 * marge) ** 2)
    centres = rng.uniform(-marge, COTE + marge, size=(n_centres, 2))
    nb = rng.poisson(mu, size=n_centres)
    pts = np.repeat(centres, nb, axis=0) + rng.normal(0, sigma, size=(nb.sum(), 2))
    return pts[((pts >= 0) & (pts <= COTE)).all(axis=1)]         # on ne garde que ce qui tombe dans la fenêtre

def semis_inhibition(n, rmin, rng):
    """Inhibition séquentielle simple : points uniformes refusés s'ils sont à moins de rmin d'un point accepté."""
    pts = []
    while len(pts) < n:
        p = rng.uniform(0, COTE, size=2)
        if not pts or (np.hypot(*(np.array(pts) - p).T) >= rmin).all():
            pts.append(p)
    return np.array(pts)

rng = np.random.default_rng(2025)
semis = {
    "aléatoire (CSR)": semis_poisson(100, rng),
    "agrégé (Thomas)": semis_thomas(kappa=0.08, mu=12, sigma=0.4, rng=rng),
    "régulier (inhibition)": semis_inhibition(100, 0.7, rng),
}
for nom, pts in semis.items():
    print(f"{nom:24s} n = {len(pts):3d} points  (intensité estimée {len(pts) / AIRE:.2f} par km²)")

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
fig, axes = plt.subplots(1, 3, figsize=(12.5, 4.3))
for ax, (nom, pts), couleur in zip(axes, semis.items(), [BLEU, ORANGE, AQUA]):
    ax.scatter(pts[:, 0], pts[:, 1], s=16, color=couleur, edgecolor="white", linewidth=0.4)
    ax.set_xlim(0, COTE); ax.set_ylim(0, COTE); ax.set_aspect("equal")
    ax.set_title(f"{nom} : {len(pts)} adresses", fontsize=10)
    ax.set_xlabel("x (km)")
axes[0].set_ylabel("y (km)")
plt.tight_layout()
plt.savefig("figures/ch09-semis.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
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

```python
def comptages(pts, m=4):
    """Comptages par case d'un quadrillage m x m de la fenêtre."""
    bornes = np.linspace(0, COTE, m + 1)
    H, _, _ = np.histogram2d(pts[:, 0], pts[:, 1], bins=[bornes, bornes])
    return H.ravel()

def test_quadrats(pts, m=4):
    c = comptages(pts, m)
    chi2 = ((c - c.mean()) ** 2).sum() / c.mean()
    ddl = len(c) - 1
    return {"chi2": chi2, "ddl": ddl, "VMR": c.var(ddof=1) / c.mean(),
            "p_agregat (chi2 grand)": stats.chi2.sf(chi2, ddl), "p_regulier (chi2 petit)": stats.chi2.cdf(chi2, ddl)}

# l'exemple à la main
print("exemple (1, 1, 1, 9) :", round(((np.array([1, 1, 1, 9]) - 3) ** 2).sum() / 3, 2), "| valeur critique chi2(3) à 5 % :", round(stats.chi2.ppf(0.95, 3), 2))
res = pd.DataFrame({nom: test_quadrats(pts) for nom, pts in semis.items()}).T
with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 160):
    print(res.to_string())
print("\ncomptages par case du semis agrégé (4 x 4) :")
print(comptages(semis["agrégé (Thomas)"]).reshape(4, 4).astype(int))
```
<!--sortie-->
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

```python
def plus_proches(pts):
    D = distances(pts)
    np.fill_diagonal(D, np.inf)
    return D.min(axis=1)

rng = np.random.default_rng(1)
n0 = 100
dbar = np.array([plus_proches(semis_poisson(n0, rng)).mean() for _ in range(4000)])
P = 4 * COTE
naif = 0.5 * np.sqrt(AIRE / n0)
don = 0.5 * np.sqrt(AIRE / n0) + (0.0514 + 0.041 / np.sqrt(n0)) * P / n0
sd_naif = np.sqrt((4 - np.pi) / (4 * np.pi * n0 * (n0 / AIRE)))
sd_don = np.sqrt(0.070 * AIRE / n0 ** 2 + 0.037 * P * np.sqrt(AIRE / n0 ** 5))
print(f"{'':28s}{'moyenne de d':>14s}{'écart-type de d':>18s}")
print(f"{'simulation (4000 semis CSR)':28s}{dbar.mean():14.4f}{dbar.std():18.4f}")
print(f"{'formule naïve (plan infini)':28s}{naif:14.4f}{sd_naif:18.4f}")
print(f"{'formule de Donnelly':28s}{don:14.4f}{sd_don:18.4f}")
```
<!--sortie-->
```text
                              moyenne de d   écart-type de d
simulation (4000 semis CSR)         0.5224            0.0288
formule naïve (plan infini)         0.5000            0.0261
formule de Donnelly                 0.5222            0.0291
```

La formule naïve sous-estime la moyenne (0,500 contre 0,523 simulé : près de 5 % d'écart) et l'écart-type ; celle de Donnelly colle à la simulation. Appliquons l'indice de Clark-Evans aux trois semis avec les deux versions, et ajoutons une troisième voie, qui évite toute formule : une **p-valeur de Monte-Carlo**. On simule $B=999$ semis CSR de même taille dans la **même fenêtre** et l'on regarde où tombe notre $\bar d$ : l'effet de bord est automatiquement pris en compte, puisque les semis simulés le subissent aussi.

```python
def clark_evans(pts, B=999, seed=7):
    n = len(pts)
    d = plus_proches(pts).mean()
    R_naif = d / (0.5 * np.sqrt(AIRE / n))
    E_don = 0.5 * np.sqrt(AIRE / n) + (0.0514 + 0.041 / np.sqrt(n)) * P / n
    s_don = np.sqrt(0.070 * AIRE / n ** 2 + 0.037 * P * np.sqrt(AIRE / n ** 5))
    z_don = (d - E_don) / s_don
    rng = np.random.default_rng(seed)
    sim = np.array([plus_proches(semis_poisson(n, rng)).mean() for _ in range(B)])
    p_mc = 2 * (1 + min((sim <= d).sum(), (sim >= d).sum())) / (B + 1)      # bilatérale
    return {"n": n, "d_moyen": d, "R (naïf)": R_naif, "R (Donnelly)": d / E_don, "z (Donnelly)": z_don,
            "p (Donnelly)": 2 * stats.norm.sf(abs(z_don)), "p (Monte-Carlo)": min(1.0, p_mc)}

res = pd.DataFrame({nom: clark_evans(pts) for nom, pts in semis.items()}).T
with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 170):
    print(res.to_string())
```
<!--sortie-->
```text
                        n  d_moyen  R (naïf)  R (Donnelly)  z (Donnelly)  p (Donnelly)  p (Monte-Carlo)
aléatoire (CSR)       100   0.5353     1.071         1.025        0.4506        0.6523            0.628
agrégé (Thomas)        75   0.2026    0.3509        0.3336        -10.28     8.252e-25            0.002
régulier (inhibition) 100    0.829     1.658         1.587         10.53     6.024e-26            0.002
```

Les trois voies s'accordent pour le semis agrégé (R très inférieur à 1) et pour le semis régulier (R supérieur à 1). Pour le semis aléatoire, le R naïf vaut un peu plus de 1 et pourrait faire croire à une légère régularité : c'est le biais de bord. Avec la correction de Donnelly, il est ramené près de 1.

**La fonction $G$ entière.** L'indice de Clark-Evans résume toutes les distances par leur moyenne. On peut regarder la **fonction de répartition empirique** de $d_i$, $\hat G(r)=\frac1n\#\{i:d_i\le r\}$, et la comparer à la courbe théorique $1-e^{-\lambda\pi r^2}$, avec une **enveloppe de Monte-Carlo** : un bandeau qui contient 95 % des courbes obtenues sur des semis CSR simulés. Si notre courbe sort du bandeau, le hasard complet est mis en défaut. Une courbe $\hat G$ qui **monte plus vite** que le hasard indique des voisins plus proches que prévu (agrégat) ; une courbe qui monte **plus lentement** indique de la répulsion.

```python
def G_emp(pts, rs):
    d = plus_proches(pts)
    return np.array([(d <= r).mean() for r in rs])

rs_G = np.linspace(0, 1.6, 81)
rng = np.random.default_rng(11)
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.9), sharey=True)
lignes = []
for ax, (nom, pts), couleur in zip(axes, semis.items(), [BLEU, ORANGE, AQUA]):
    n = len(pts)
    sims = np.array([G_emp(semis_poisson(n, rng), rs_G) for _ in range(499)])
    bas, haut = np.percentile(sims, [2.5, 97.5], axis=0)
    theorique = 1 - np.exp(-(n / AIRE) * np.pi * rs_G ** 2)
    ax.fill_between(rs_G, bas, haut, color="#cfcfc8", alpha=0.8, label="enveloppe CSR (95 %)")
    ax.plot(rs_G, theorique, color="#555555", lw=1, ls="--", label="théorie (plan infini)")
    ax.plot(rs_G, G_emp(pts, rs_G), color=couleur, lw=2.2, label="observé")
    ax.set_title(nom, fontsize=10); ax.set_xlabel("distance r (km)")
    sortie = (G_emp(pts, rs_G) < bas) | (G_emp(pts, rs_G) > haut)
    lignes.append({"semis": nom, "part des r hors enveloppe": sortie.mean()})
axes[0].set_ylabel("G(r)")
axes[0].legend(frameon=False, fontsize=8, loc="lower right")
plt.tight_layout()
plt.savefig("figures/ch09-fonction-G.png", dpi=200, bbox_inches="tight")
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
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

```python
def ripley_K(pts, rs, bord=True):
    """Estimateur de K, avec ou sans correction de bord (méthode du bord)."""
    n = len(pts)
    D = distances(pts)
    np.fill_diagonal(D, np.inf)
    b = np.minimum.reduce([pts[:, 0], COTE - pts[:, 0], pts[:, 1], COTE - pts[:, 1]])
    K = np.full(len(rs), np.nan)
    for k, r in enumerate(rs):
        garde = (b >= r) if bord else np.ones(n, dtype=bool)
        nr = garde.sum()
        if nr > 0:
            K[k] = AIRE * (D[garde] <= r).sum() / ((n - 1) * nr)
    return K

# Contrôle sur l'exemple à la main (fenêtre unité) : on neutralise le bord pour retrouver 0,333
P4 = np.array([[0.1, 0.1], [0.2, 0.1], [0.8, 0.8], [0.85, 0.9]])
D4 = distances(P4); np.fill_diagonal(D4, np.inf)
print("K(0,2) de l'exemple à la main :", round(1.0 * (D4 <= 0.2).sum() / (4 * 3), 4), "| pi r^2 =", round(np.pi * 0.2 ** 2, 4))

# L'effet de bord, mesuré : moyenne de K sur 300 semis CSR, avec et sans correction, à r = 2 km
rs = np.linspace(0.1, 2.0, 20)
rng = np.random.default_rng(3)
Kn, Kc = [], []
for _ in range(300):
    pts_sim = semis_poisson(100, rng)                           # le même semis sert aux deux estimateurs
    Kn.append(ripley_K(pts_sim, rs, bord=False))
    Kc.append(ripley_K(pts_sim, rs, bord=True))
Kn, Kc = np.array(Kn), np.array(Kc)
print(f"à r = 2 km  ->  pi r^2 = {np.pi * 4:.2f} | moyenne sans correction : {Kn[:, -1].mean():.2f} | moyenne avec correction : {np.nanmean(Kc[:, -1]):.2f}")
```
<!--sortie-->
```text
K(0,2) de l'exemple à la main : 0.3333 | pi r^2 = 0.1257
à r = 2 km  ->  pi r^2 = 12.57 | moyenne sans correction : 10.42 | moyenne avec correction : 12.30
```

Sans correction, l'estimateur sous-estime nettement $K$ à 2 km : 10,4 en moyenne au lieu de $\pi r^2=12{,}6$, soit 17 % de trop peu. Avec la méthode du bord, on obtient 12,3 : un écart de 2 %, très inférieur. Passons à l'application : on compare la courbe $\hat L(r)-r$ de chaque semis à une enveloppe obtenue sur 499 semis CSR de même taille. Pour un **test global** (et non « point par point »), on utilise la statistique $T=\max_r|\hat L(r)-r|$, comparée à sa distribution sous CSR.

```python
def L_centre(pts, rs):
    return np.sqrt(ripley_K(pts, rs) / np.pi) - rs

rng = np.random.default_rng(21)
fig, axes = plt.subplots(1, 3, figsize=(12.5, 3.9), sharey=True)
lignes = []
for ax, (nom, pts), couleur in zip(axes, semis.items(), [BLEU, ORANGE, AQUA]):
    n = len(pts)
    sims = np.array([L_centre(semis_poisson(n, rng), rs) for _ in range(499)])
    bas, haut = np.nanpercentile(sims, [2.5, 97.5], axis=0)
    obs = L_centre(pts, rs)
    T_obs = np.nanmax(np.abs(obs))
    T_sim = np.nanmax(np.abs(sims), axis=1)
    lignes.append({"semis": nom, "T observé": T_obs, "T sim. (médiane)": np.median(T_sim),
                   "p global (Monte-Carlo)": (1 + (T_sim >= T_obs).sum()) / (len(T_sim) + 1),
                   "L-r moyen": np.nanmean(obs)})
    ax.fill_between(rs, bas, haut, color="#cfcfc8", alpha=0.8, label="enveloppe CSR (95 %, point par point)")
    ax.axhline(0, color="#555555", lw=1, ls="--")
    ax.plot(rs, obs, color=couleur, lw=2.2, label="observé")
    ax.set_title(nom, fontsize=10); ax.set_xlabel("distance r (km)")
axes[0].set_ylabel("L(r) - r  (0 = hasard complet)")
axes[0].legend(frameon=False, fontsize=8, loc="lower left")
plt.tight_layout()
plt.savefig("figures/ch09-ripley.png", dpi=200, bbox_inches="tight")
with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 170):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
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

```python
def semis_inhomogene(n, rng, etalement=2.5):
    """100 points indépendants, mais avec une densité qui décroît du centre vers les bords."""
    pts = []
    while len(pts) < n:
        p = rng.uniform(0, COTE, size=2)
        if rng.random() < np.exp(-((p - COTE / 2) ** 2).sum() / (2 * etalement ** 2)):
            pts.append(p)
    return np.array(pts)

rng = np.random.default_rng(31)
inho = semis_inhomogene(100, rng)
obs = L_centre(inho, rs)
sims = np.array([L_centre(semis_poisson(100, rng), rs) for _ in range(499)])
T_obs, T_sim = np.nanmax(np.abs(obs)), np.nanmax(np.abs(sims), axis=1)
print(f"semis à densité variable, SANS interaction : T = {T_obs:.3f} | p global CSR = {(1 + (T_sim >= T_obs).sum()) / 500:.3f}")
q = comptages(inho, 4).reshape(4, 4)
print("comptages par case (4 x 4) :")
print(q.astype(int))

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4.2))
ax1.scatter(inho[:, 0], inho[:, 1], s=16, color=VIOLET, edgecolor="white", linewidth=0.4)
ax1.set_xlim(0, COTE); ax1.set_ylim(0, COTE); ax1.set_aspect("equal")
ax1.set_title("100 adresses indépendantes, densité forte au centre", fontsize=10); ax1.set_xlabel("x (km)"); ax1.set_ylabel("y (km)")
bas, haut = np.nanpercentile(sims, [2.5, 97.5], axis=0)
ax2.fill_between(rs, bas, haut, color="#cfcfc8", alpha=0.8, label="enveloppe CSR (95 %)")
ax2.axhline(0, color="#555555", lw=1, ls="--")
ax2.plot(rs, obs, color=VIOLET, lw=2.2, label="observé")
ax2.set_xlabel("distance r (km)"); ax2.set_ylabel("L(r) - r"); ax2.set_title("La fonction K voit un « agrégat » qui n'en est pas un", fontsize=10)
ax2.legend(frameon=False, fontsize=8, loc="upper left")
plt.tight_layout()
plt.savefig("figures/ch09-inhomogene.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
semis à densité variable, SANS interaction : T = 0.687 | p global CSR = 0.002
comptages par case (4 x 4) :
[[ 3  8  2  1]
 [ 4 13 15  7]
 [ 5 10 11  6]
 [ 1  8  5  1]]
figure enregistrée
```

![À gauche : 100 adresses indépendantes les unes des autres, mais avec une densité qui décroît du centre vers les bords. À droite : la fonction L(r) − r sort de l'enveloppe du hasard complet, alors qu'il n'y a aucune interaction entre les points.](figures/ch09-inhomogene.png)

Le test rejette le hasard complet alors qu'**aucun point n'attire les autres**. L'agrégat apparent est entièrement dû à la variation de la densité. Le remède est de comparer non pas à un CSR homogène mais à un **processus de Poisson inhomogène** d'intensité estimée $\hat\lambda(s)$ (par un lissage à noyau, par exemple), et d'utiliser la fonction **$K$ inhomogène** de Baddeley, Møller et Waagepetersen. Elle ne figure pas dans ce chapitre (nous ne l'avons pas implémentée) ; retenez le principe : **on ne peut parler d'agrégation entre les points qu'après avoir tenu compte de la densité qui varie**. Cette distinction entre *effet du premier ordre* (l'intensité) et *effet du second ordre* (l'interaction) est le cœur de la modélisation des semis de points.

> 🛠️ **Retour à la question de Yasmine.** Pour savoir si ses clients de la médina sont **vraiment** regroupés autour de la boutique, elle ne peut pas se contenter d'un test de $K$ : elle doit d'abord se demander si la densité de population varie, c'est-à-dire si les habitants eux-mêmes sont plus nombreux près de la boutique. Un semis de clients qui reproduit simplement la répartition de la **population** ne dit rien sur son comportement. La comparaison utile est avec les habitants **non clients** (un semis de « contrôle ») ou avec une carte de densité de population.

> ✅ **À retenir.**
> - Un **semis de points** est un phénomène dont les **positions** sont aléatoires. La référence est le **hasard spatial complet** : un processus de Poisson homogène (comptages de Poisson, indépendance entre régions disjointes, points uniformes conditionnellement à leur nombre).
> - **Quadrats** : $\chi^2=\sum(c_k-\bar c)^2/\bar c$ (approximativement $\chi^2_{m-1}$) ; simple, mais dépend de la taille des cases.
> - **Plus proche voisin** : $G(r)=1-e^{-\lambda\pi r^2}$ sous le CSR, $\mathbb E[d]=1/(2\sqrt\lambda)$ ; indice de Clark-Evans $R<1$ pour un agrégat, $R>1$ pour de la régularité. Une fenêtre finie biaise $R$ (**effet de bord**) : corrigez (Donnelly) ou, mieux, utilisez une **p-valeur de Monte-Carlo** dans la même fenêtre.
> - **Fonction $K$ de Ripley** : $K_{\text{CSR}}(r)=\pi r^2$ ; $L(r)-r$ au-dessus de 0 pour l'agrégat, en dessous pour la régularité ; **correction de bord** indispensable ; utilisez un test **global** et non un bandeau point par point.
> - **Une intensité variable imite un agrégat** : avant de conclure à une interaction, tenez compte de la densité.


## 9.5 Exercices du chapitre 9

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les corrigés réutilisent les fonctions définies dans les sections 9.1 à 9.4 (`haversine`, `moran`, `variogramme_empirique`, `krigeage_ordinaire`, `semis_thomas`, `ripley_K`…) : le chapitre est exécuté d'un seul tenant.

### Énoncés

**Exercice 1 ⭐ (quel type de données ?).** Pour chaque situation, dites s'il s'agit de données **géostatistiques**, **surfaciques** ou d'un **semis de points**, et nommez l'outil de ce chapitre qui répond à la question. (a) Yasmine relève la **température** à l'intérieur de 40 entrepôts de stockage répartis dans la région et veut estimer la température dans un entrepôt qu'elle n'a pas visité. (b) Elle dispose du **taux de retour de colis** de chacune des 24 gouvernorats et se demande si les gouvernorats voisins ont des taux semblables. (c) Elle a les **adresses** de tous ses clients de Sousse et se demande si elles se regroupent. (d) Un transporteur mesure le **délai de livraison** à 300 adresses et veut cartographier le délai moyen attendu sur toute la zone.

**Exercice 2 ⭐ (haversine à la main).** Calculez à la main la distance entre Tunis $(36{,}81^\circ\text{N};\,10{,}18^\circ\text{E})$ et Sousse $(35{,}83^\circ\text{N};\,10{,}61^\circ\text{E})$, en utilisant la latitude moyenne pour le facteur $\cos\varphi$. Comparez au résultat de la formule de haversine.

**Exercice 3 ⭐⭐ (Moran sur quatre zones).** Quatre zones alignées A–B–C–D (chacune voisine de la précédente et de la suivante) ont pour valeurs $1,\,2,\,3,\,4$. (a) Calculez à la main l'indice de Moran avec les poids binaires, puis avec les poids standardisés par ligne. (b) Quelle est son espérance sous l'hypothèse nulle ? (c) Il n'y a que $4!=24$ façons de ranger ces valeurs sur les zones : calculez la distribution **exacte** de $I$ et la p-valeur de l'alignement observé.

**Exercice 4 ⭐⭐ (lire un indice local).** Dans une carte, la zone $i$ a un écart à la moyenne $z_i=+12$ et la moyenne des écarts de ses voisines vaut $(Wz)_i=-8$. La variance empirique est $m_2=100$. (a) Dans quel quadrant se trouve la zone ? (b) Que vaut son indice local $I_i$ ? (c) Peut-on conclure que c'est une valeur atypique significative ? Que faudrait-il faire ?

**Exercice 5 ⭐⭐ (variogramme à la main).** Cinq mesures alignées aux abscisses 0, 1, 2, 3 et 4 km ont pour valeurs $3,\,5,\,4,\,8,\,7$. Calculez le variogramme empirique aux distances 1, 2, 3 et 4 km. Que pouvez-vous dire de la forme de la courbe et de la fiabilité de ces estimations ?

**Exercice 6 ⭐⭐ (krigeage à la main).** En dimension 1, avec le variogramme linéaire $\gamma(h)=0{,}5\,h$, on a mesuré 20 en $x=0$ et 30 en $x=4$. (a) Écrivez et résolvez le système de krigeage ordinaire pour prédire en $x=1$ ; donnez la prédiction et la variance. (b) Si les valeurs mesurées étaient 0 et 100 au lieu de 20 et 30, la variance de krigeage changerait-elle ? Pourquoi ?

**Exercice 7 ⭐⭐ (le problème de l'unité spatiale modifiable).** On construit une variable $x$ corrélée aux `ventes_hab` des 144 délégations (la graine est donnée dans le corrigé). On **agrège** ensuite les zones en blocs de $2\times2$, $3\times3$, $4\times4$ et $6\times6$ cases (moyenne par bloc). Comment évoluent la corrélation entre $x$ et les ventes, l'écart-type des ventes et l'indice de Moran ? Qu'en conclure pour l'interprétation d'une corrélation calculée sur des zones ?

**Exercice 8 ⭐⭐ (l'effet de bord sur les indices locaux).** Sur la grille $12\times12$ avec voisinage « reine », les cases ont 3 voisines (coins), 5 (bords) ou 8 (intérieur). Sans autocorrélation, la variance de l'indice local $I_i$ devrait varier comme $1/k$ où $k$ est le nombre de voisines. Vérifiez-le par simulation et expliquez pourquoi les zones de bord sont plus souvent « significatives » avec une p-valeur naïve.

**Exercice 9 ⭐⭐ (nombre efficace d'observations).** Pour un modèle SAR sur la grille $12\times12$ avec $\rho\in\{0{,}3;\,0{,}5;\,0{,}7;\,0{,}9;\,0{,}95\}$, estimez par simulation le **nombre efficace d'observations indépendantes** pour estimer une moyenne, défini par $n_{\text{eff}}=\operatorname{Var}(y_i)/\operatorname{Var}(\bar y)$. Commentez.

**Exercice 10 ⭐⭐ (cases vides).** On répartit 100 points au hasard (CSR) dans une fenêtre de $10\times10$ km, divisée en $4\times4$ cases. (a) Quelle est, à la main, la probabilité qu'une case donnée soit vide, et le nombre moyen de cases vides ? (b) Vérifiez par simulation, puis comparez au nombre de cases vides du semis agrégé de la section 9.4. Que cela dit-il ?

**Exercice 11 ⭐⭐⭐ (l'estimateur du variogramme est-il sans biais ?).** Le variogramme empirique est une moyenne de $\frac12(z_i-z_j)^2$. Montrez que $\mathbb E\big[\tfrac12(Z(s+h)-Z(s))^2\big]=\gamma(h)$ pour un processus stationnaire de moyenne $\mu$, puis vérifiez par simulation, en moyennant le variogramme empirique de 60 jeux de livraisons indépendants (même processus que 9.3) et en le comparant au variogramme **vrai** $\gamma(h)=0{,}4+1{,}0\,(1-e^{-h/12})$.

**Exercice 12 ⭐⭐⭐ (la fonction $K$ d'un processus de Thomas).** Pour un processus de Thomas de densité de centres $\kappa$ et d'étalement $\sigma$ (par coordonnée), on admet que la fonction de corrélation de paires est $g(r)=1+\dfrac{1}{4\pi\kappa\sigma^2}e^{-r^2/(4\sigma^2)}$. (a) Montrez que $K(r)=\pi r^2+\dfrac1\kappa\big(1-e^{-r^2/(4\sigma^2)}\big)$. (b) Vérifiez par simulation pour $\kappa=0{,}5$, $\mu=2$, $\sigma=0{,}4$, puis pour $\kappa=0{,}08$, $\mu=12$, $\sigma=0{,}4$. Que constatez-vous ?

### Corrigés

**Corrigé 1.** (a) **Géostatistique** : la température existe en tout point de la région et on la mesure en 40 lieux ; on veut prédire ailleurs : variogramme et **krigeage**. (b) **Surfacique** : une valeur par zone, la question est la ressemblance entre zones voisines : matrice de poids et **indice de Moran** (avec 24 zones seulement, on teste par permutations et on indique la définition du voisinage). (c) **Semis de points** : ce sont les positions qui sont le phénomène ; on les compare au hasard complet avec les quadrats, le plus proche voisin et la fonction **$K$ de Ripley**, en pensant à la densité de population qui peut varier (9.4.5). (d) **Géostatistique** : un délai défini en tout point mesuré en 300 adresses ; **variogramme et krigeage** donnent la carte du délai attendu et une carte d'incertitude.

**Corrigé 2.** $\Delta\varphi=0{,}98^\circ$ donne $0{,}98\times111{,}2\approx109{,}0$ km vers le sud. $\Delta\lambda=0{,}43^\circ$ : avec $\cos(36{,}32^\circ)\approx0{,}806$, $0{,}43\times111{,}2\times0{,}806\approx38{,}5$ km vers l'est. La distance est $\sqrt{109{,}0^2+38{,}5^2}\approx115{,}6$ km.

```python
print("haversine Tunis - Sousse :", round(float(haversine(36.81, 10.18, 35.83, 10.61)), 1), "km")
print("estimation à la main     :", round(float(np.hypot(0.98 * 111.2, 0.43 * 111.2 * np.cos(np.radians(36.32)))), 1), "km")
```
<!--sortie-->
```text
haversine Tunis - Sousse : 115.6 km
estimation à la main     : 115.6 km
```

**Corrigé 3.** (a) Les écarts à la moyenne $\bar y=2{,}5$ sont $z=(-1{,}5;-0{,}5;0{,}5;1{,}5)$ et $\sum z^2=5$. Les frontières sont A–B, B–C et C–D : produits $(-1{,}5)(-0{,}5)=0{,}75$, $(-0{,}5)(0{,}5)=-0{,}25$, $(0{,}5)(1{,}5)=0{,}75$, de somme $1{,}25$. **Poids binaires** ($S_0=6$ liens orientés) : $\sum_{ij}w_{ij}z_iz_j=2\times1{,}25=2{,}5$ et $I=\frac46\times\frac{2{,}5}{5}=\frac13$. **Poids standardisés** ($S_0=4$) : A et D n'ont qu'une voisine (poids 1), B et C deux (poids $\frac12$ chacune), donc $z^\top Wz=z_Az_B+\tfrac12z_B(z_A+z_C)+\tfrac12z_C(z_B+z_D)+z_Dz_C=0{,}75+0{,}25+0{,}25+0{,}75=2$ et $I=\frac{2}{5}=0{,}4$. (b) $\mathbb E[I]=-1/(n-1)=-\frac13$ : avec $n=4$ zones seulement, l'espérance sous le hasard est loin de zéro. (c) On énumère les 24 permutations.

```python
from itertools import permutations

W4 = std_lignes(np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], dtype=float))
W4b = np.array([[0, 1, 0, 0], [1, 0, 1, 0], [0, 1, 0, 1], [0, 0, 1, 0]], dtype=float)
vals = np.array([1.0, 2, 3, 4])
print("I (poids binaires)      :", round(moran(vals, W4b), 4), "| I (poids standardisés) :", round(moran(vals, W4), 4))
toutes = np.array([moran(np.array(p), W4) for p in permutations(vals)])
print("nombre de permutations :", len(toutes), "| valeurs distinctes de I :", np.unique(toutes.round(4)).tolist())
print("moyenne de I sur les 24 permutations :", round(toutes.mean(), 4), "(= -1/(n-1) =", round(-1 / 3, 4), ")")
print("p-valeur exacte (I >= observé) :", round(float((toutes >= moran(vals, W4) - 1e-12).mean()), 4))
```
<!--sortie-->
```text
I (poids binaires)      : 0.3333 | I (poids standardisés) : 0.4
nombre de permutations : 24 | valeurs distinctes de I : [-0.9, -0.6, -0.5, -0.3, 0.0, 0.3, 0.4]
moyenne de I sur les 24 permutations : -0.3333 (= -1/(n-1) = -0.3333 )
p-valeur exacte (I >= observé) : 0.0833
```

L'espérance exacte sur les permutations est bien $-\frac13$. L'alignement observé (1, 2, 3, 4) et son image inversée (4, 3, 2, 1) sont les deux seuls arrangements qui atteignent cette valeur maximale : la p-valeur exacte est $2/24\approx0{,}083$, **supérieure à 5 %**. Avec quatre zones, aucune autocorrélation, même parfaite, ne peut être significative : c'est le prix du petit nombre de permutations.

**Corrigé 4.** (a) $z_i>0$ (zone haute) et $(Wz)_i<0$ (voisines basses) : quadrant **HL** (haute entourée de basses). (b) $I_i=\dfrac{z_i\,(Wz)_i}{m_2}=\dfrac{12\times(-8)}{100}=-0{,}96$ : négatif, car la zone s'oppose à ses voisines. (c) Non : un indice local négatif ne dit rien de sa significativité. Il faut une **permutation conditionnelle** (fixer $z_i$, mélanger les autres valeurs) pour obtenir une p-valeur, puis **corriger** pour les tests multiples (Benjamini-Hochberg), comme au 9.2.4.

**Corrigé 5.** Distance 1 : paires (3,5), (5,4), (4,8), (8,7) ; carrés des écarts 4, 1, 16, 1, total 22 ; $\hat\gamma(1)=\frac{22}{2\times4}=2{,}75$. Distance 2 : (3,4), (5,8), (4,7) ; carrés 1, 9, 9, total 19 ; $\hat\gamma(2)=\frac{19}{2\times3}\approx3{,}17$. Distance 3 : (3,8), (5,7) ; carrés 25, 4 ; $\hat\gamma(3)=\frac{29}{2\times2}=7{,}25$. Distance 4 : (3,7) ; $\hat\gamma(4)=\frac{16}{2}=8$.

```python
P5 = np.array([[0.0, 0], [1, 0], [2, 0], [3, 0], [4, 0]])
z5 = np.array([3.0, 5, 4, 8, 7])
print(variogramme_empirique(P5, z5, largeur=1.0, hmax=4.0).round(3).to_string(index=False))
```
<!--sortie-->
```text
  h  gamma  paires
1.0  2.750       4
2.0  3.167       3
3.0  7.250       2
4.0  8.000       1
```

La courbe est **croissante** (2,75 ; 3,17 ; 7,25 ; 8) et ne montre aucun palier : on ne peut pas estimer de portée. Deux raisons : il y a très peu de données, et ces valeurs montrent une **tendance** (elles augmentent avec l'abscisse), qui fait monter le variogramme (9.3.7). Surtout, le nombre de paires **diminue** avec la distance (4, 3, 2, 1) : l'estimation à 4 km repose sur **une seule paire** et n'a quasiment aucune fiabilité. C'est l'inverse de ce qui se passe en deux dimensions, où les paires lointaines sont nombreuses, mais cela rappelle qu'un variogramme se lit en regardant les effectifs.

**Corrigé 6.** (a) $\Gamma=\begin{pmatrix}0&2\\2&0\end{pmatrix}$ (car $\gamma(4)=2$) et $\gamma_0=(\gamma(1),\gamma(3))^\top=(0{,}5;\,1{,}5)^\top$. Les équations sont $2\lambda_2+m=0{,}5$, $2\lambda_1+m=1{,}5$ et $\lambda_1+\lambda_2=1$. En soustrayant, $2(\lambda_1-\lambda_2)=1$, donc $\lambda_1=0{,}75$, $\lambda_2=0{,}25$ et $m=0$. Prédiction : $0{,}75\times20+0{,}25\times30=22{,}5$, variance $\lambda^\top\gamma_0+m=0{,}75\times0{,}5+0{,}25\times1{,}5=0{,}75$. C'est l'interpolation linéaire (de 20 à 30 sur 4 km, soit 22,5 à 1 km). (b) **Non** : la variance de krigeage $\lambda^\top\gamma_0+m$ ne dépend que de la **géométrie** (les distances) et du variogramme, jamais des valeurs mesurées. Les poids sont identiques, donc la prédiction vaudrait $0{,}75\times0+0{,}25\times100=25$ et la variance resterait $0{,}75$. Le krigeage dit à quel point le *plan d'échantillonnage* est informatif, pas si les données observées sont « surprenantes ».

```python
for valeurs in ([20.0, 30.0], [0.0, 100.0]):
    pred, var, lam = krigeage_ordinaire(np.array([[0.0, 0], [4, 0]]), np.array(valeurs), np.array([[1.0, 0]]), lineaire, (0.5,))
    print("valeurs", valeurs, "-> poids", lam.ravel().round(3), "| prédiction", pred.round(3), "| variance", var.round(3))
```
<!--sortie-->
```text
valeurs [20.0, 30.0] -> poids [0.75 0.25] | prédiction [22.5] | variance [0.75]
valeurs [0.0, 100.0] -> poids [0.75 0.25] | prédiction [25.] | variance [0.75]
```

**Corrigé 7.** Nous construisons $x$ comme un mélange de `ventes_hab` standardisées et d'un autre champ SAR indépendant, puis nous agrégeons.

```python
Wr = std_lignes(contiguite_reine(12, 12))
rng7 = np.random.default_rng(5)
A7 = np.linalg.inv(np.eye(144) - 0.9 * Wr)
y7 = deleg["ventes_hab"].to_numpy()
champ = A7 @ rng7.normal(size=144)
x7 = 0.5 * (y7 - y7.mean()) / y7.std() + 0.87 * champ / champ.std()

def agrege(v, k):
    m = 12 // k
    return v.reshape(12, 12).reshape(m, k, m, k).mean(axis=(1, 3)).ravel()

lignes = []
for k in (1, 2, 3, 4, 6):
    m = 12 // k
    ya, xa = agrege(y7, k), agrege(x7, k)
    I_k = moran(ya, std_lignes(contiguite_reine(m, m))) if m >= 3 else np.nan
    lignes.append({"bloc": f"{k} x {k}", "zones": m * m, "corr(x, ventes)": np.corrcoef(xa, ya)[0, 1],
                   "ecart_type_ventes": ya.std(), "Moran_ventes": I_k, "E[I]": -1 / (m * m - 1) if m >= 3 else np.nan})
with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 150):
    print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 bloc  zones  corr(x, ventes)  ecart_type_ventes  Moran_ventes   E[I]
1 x 1    144            0.597             13.468         0.621 -0.007
2 x 2     36            0.619             11.142         0.570 -0.029
3 x 3     16            0.646             10.010         0.291 -0.067
4 x 4      9            0.774              9.350        -0.054 -0.125
6 x 6      4            0.869              8.431           NaN    NaN
```

La **corrélation augmente** avec l'agrégation (de 0,60 sur les 144 zones à 0,87 sur les 4 blocs de $6\times6$), l'**écart-type** des ventes diminue (de 13,5 à 8,4 : les moyennes de blocs lissent les fluctuations) et l'**indice de Moran** chute : de 0,62 à 0,57 (blocs de $2\times2$), à 0,29 ($3\times3$, soit 16 zones) puis à $-0{,}05$ ($4\times4$, soit 9 zones), à comparer à $-0{,}125$ sous le hasard pour 9 zones : à cette échelle, l'autocorrélation a pratiquement disparu (et avec 9 zones, un test aurait de toute façon très peu de puissance). Les mêmes personnes, les mêmes ventes, trois « résultats » différents selon le découpage : c'est le **problème de l'unité spatiale modifiable** (MAUP). Une corrélation calculée sur des zones n'est vraie que pour **ce découpage** : on ne peut pas la transposer à l'échelle des individus (sophisme écologique), ni à un autre découpage, sans précaution.

**Corrigé 8.** On simule le hasard en mélangeant les valeurs de `ventes_bruit` et on calcule, pour chaque case, l'indice local $I_i=z_i(Wz)_i/m_2$.

```python
rng8 = np.random.default_rng(8)
zb = deleg["ventes_bruit"].to_numpy() - deleg["ventes_bruit"].mean()
m2 = zb @ zb / 144
perms = np.argsort(rng8.random((3000, 144)), axis=1)
Zs = zb[perms]
Ii_sim = Zs * (Zs @ Wr.T) / m2                                   # (3000, 144) : indices locaux sous H0
k_vois = contiguite_reine(12, 12).sum(axis=1)
lignes = []
for kk in (3, 5, 8):
    cols = k_vois == kk
    lignes.append({"voisines": kk, "cases": int(cols.sum()), "variance de I_i": Ii_sim[:, cols].var(), "variance x k": Ii_sim[:, cols].var() * kk})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
 voisines  cases  variance de I_i  variance x k
        3      4            0.333         1.000
        5     40            0.191         0.957
        8    100            0.117         0.936
```

La variance de $I_i$ est environ **2,8 fois plus grande** pour un coin (3 voisines) que pour une case intérieure (8 voisines), à comparer au rapport théorique $8/3\approx2{,}67$ ; la colonne « variance × $k$ » est à peu près constante, ce qui confirme la loi en $1/k$ : la moyenne des voisines est plus bruitée quand il y a moins de voisines. Une zone de bord ressemble donc plus facilement à une valeur extrême par hasard, et une p-valeur calculée avec la **même** loi pour toutes les zones la déclarerait trop souvent significative. Les **permutations conditionnelles** du 9.2.4 évitent ce piège, car elles tirent exactement le bon nombre de voisines pour chaque zone. Par prudence, on examine séparément les zones de bord.

**Corrigé 9.** Pour chaque $\rho$, on simule 4 000 champs SAR et on compare la variance d'une zone à celle de la moyenne des 144 zones.

```python
rng9 = np.random.default_rng(9)
lignes = []
for rho in (0.3, 0.5, 0.7, 0.9, 0.95):
    Y9 = np.linalg.inv(np.eye(144) - rho * Wr) @ rng9.normal(size=(144, 4000))
    lignes.append({"rho": rho, "variance d'une zone": Y9.var(), "variance de la moyenne": Y9.mean(axis=0).var(), "n_eff": Y9.var() / Y9.mean(axis=0).var()})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
 rho  variance d'une zone  variance de la moyenne  n_eff
0.30                1.052                   0.014 75.715
0.50                1.179                   0.028 42.577
0.70                1.555                   0.077 20.203
0.90                3.917                   0.708  5.532
0.95                8.383                   2.805  2.989
```

Le nombre efficace d'observations **s'effondre** quand $\rho$ augmente : d'environ 76 pour $\rho=0{,}3$, il tombe à 43 pour $\rho=0{,}5$, à 20 pour $\rho=0{,}7$, à 5,5 pour $\rho=0{,}9$ (la valeur de la section 9.2.5) et à 3 pour $\rho=0{,}95$. Même pour une dépendance modérée ($\rho=0{,}5$), les 144 zones n'apportent l'information que d'environ 43 observations indépendantes. C'est la raison de la surconfiance des tests usuels.

**Corrigé 10.** (a) Les cases ont une aire de $2{,}5\times2{,}5=6{,}25$ km² et l'intensité vaut $\lambda=1$ par km² : le nombre de points d'une case suit approximativement une loi de Poisson de moyenne $6{,}25$, donc $\mathbb P(\text{vide})=e^{-6{,}25}\approx0{,}0019$. Plus exactement, conditionnellement à $n=100$ points, chaque point tombe hors d'une case donnée avec la probabilité $\frac{15}{16}$ : $\mathbb P(\text{vide})=(15/16)^{100}\approx0{,}0016$. Pour 16 cases, le nombre moyen de cases vides est $16\times0{,}0016\approx0{,}025$ : sous le hasard complet, on s'attend à **ne presque jamais** voir de case vide.

```python
print("e^-6,25 =", round(float(np.exp(-6.25)), 5), "| (15/16)^100 =", round((15 / 16) ** 100, 5), "| 16 x (15/16)^100 =", round(16 * (15 / 16) ** 100, 4))
rng10 = np.random.default_rng(10)
vides = [(comptages(semis_poisson(100, rng10)) == 0).sum() for _ in range(5000)]
print("nombre moyen de cases vides sur 5000 semis CSR :", round(float(np.mean(vides)), 4), "| part des semis avec au moins une case vide :", round(float(np.mean(np.array(vides) > 0)), 4))
print("cases vides dans le semis agrégé :", int((comptages(semis["agrégé (Thomas)"]) == 0).sum()), "sur 16")
```
<!--sortie-->
```text
e^-6,25 = 0.00193 | (15/16)^100 = 0.00157 | 16 x (15/16)^100 = 0.0252
nombre moyen de cases vides sur 5000 semis CSR : 0.0226 | part des semis avec au moins une case vide : 0.0224
cases vides dans le semis agrégé : 7 sur 16
```

(b) La simulation confirme le calcul (environ 0,025 case vide en moyenne). Le semis agrégé de 9.4 a **7 cases vides sur 16** : un événement quasi impossible sous le hasard, qui est un autre visage de l'agrégation. (Attention : ce semis compte 75 points et non 100, ce qui rend les cases vides un peu plus plausibles, sans changer la conclusion.)

**Corrigé 11.** Notons $\delta=Z(s+h)-Z(s)$. Par stationnarité, $\mathbb E[Z(s+h)]=\mathbb E[Z(s)]=\mu$, donc $\mathbb E[\delta]=0$, et $\mathbb E[\delta^2]=\operatorname{Var}(\delta)$. Par définition du semi-variogramme, $\gamma(h)=\frac12\mathbb E[\delta^2]$. L'estimateur $\hat\gamma(h)$ est une moyenne de $\frac12\delta^2$ sur des paires **dont la distance est $h$** : son espérance est donc $\gamma(h)$ ; il est sans biais **à $\mu$ inconnue** (ce qui le distingue de la covariance empirique, qui exige d'estimer la moyenne). Le seul biais vient du regroupement par classes (nous comparons à $\gamma$ à la distance moyenne de la classe) et d'éventuelles tendances. Vérifions par simulation.

```python
accumule = []
for graine in range(300, 360):
    d_sim, _ = livraisons(seed=graine)
    accumule.append(variogramme_empirique(d_sim[["x", "y"]].to_numpy(), d_sim["delai_jours"].to_numpy()))
h_moy = np.mean([e["h"].to_numpy() for e in accumule], axis=0)
g_moy = np.mean([e["gamma"].to_numpy() for e in accumule], axis=0)
g_sd = np.std([e["gamma"].to_numpy() for e in accumule], axis=0, ddof=1) / np.sqrt(len(accumule))
vrai_g = gamma_exp(h_moy, 0.4, 1.0, 12.0)
print(pd.DataFrame({"h": h_moy, "gamma_moyen": g_moy, "erreur_type_moyenne": g_sd, "gamma_vrai": vrai_g, "ecart_%": 100 * (g_moy / vrai_g - 1)}).round(3).to_string(index=False))
```
<!--sortie-->
```text
     h  gamma_moyen  erreur_type_moyenne  gamma_vrai  ecart_%
 3.324        0.632                0.011       0.642   -1.592
 7.745        0.867                0.014       0.876   -0.956
12.636        1.033                0.019       1.051   -1.751
17.593        1.164                0.022       1.169   -0.416
22.548        1.242                0.027       1.247   -0.389
27.549        1.303                0.030       1.299    0.277
32.529        1.329                0.032       1.334   -0.326
37.509        1.367                0.037       1.356    0.809
42.512        1.404                0.036       1.371    2.385
47.503        1.405                0.037       1.381    1.719
```

La moyenne sur 60 jeux colle au variogramme vrai à toutes les distances, à moins de 2,5 % près, et les écarts restent de l'ordre de l'erreur-type de la moyenne (colonne suivante) : rien ne montre de biais. Mais regardons la colonne des erreurs-types : elle **augmente avec la distance**. C'est la signature d'une corrélation forte entre classes de distance voisines et de grandes fluctuations d'un jeu à l'autre aux distances élevées : une moyenne de 60 jeux est précise, mais **un seul jeu** de données réelles est un tirage unique, d'où la dispersion observée en 9.3.3 sur les paramètres ajustés.

**Corrigé 12.** (a) Par définition, $K(r)=\int_0^r 2\pi s\,g(s)\,ds$ (le nombre moyen d'autres points à moins de $r$, divisé par $\lambda$, est l'intégrale de la fonction de corrélation de paires sur le disque). Donc $K(r)=\pi r^2+\dfrac{2\pi}{4\pi\kappa\sigma^2}\int_0^r s\,e^{-s^2/(4\sigma^2)}\,ds$. Or $\int_0^r s\,e^{-s^2/(4\sigma^2)}ds=2\sigma^2\big(1-e^{-r^2/(4\sigma^2)}\big)$, d'où $K(r)=\pi r^2+\dfrac{1}{2\kappa\sigma^2}\cdot2\sigma^2\big(1-e^{-r^2/(4\sigma^2)}\big)=\pi r^2+\dfrac1\kappa\big(1-e^{-r^2/(4\sigma^2)}\big)$. Remarquons que $K$ ne dépend ni de $\mu$ ni de l'intensité totale : l'excès par rapport au hasard est $\frac1\kappa(1-e^{-r^2/4\sigma^2})$, et il tend vers $1/\kappa$ (le nombre moyen de centres par km² est $\kappa$, donc $1/\kappa$ est l'aire d'« un agrégat »). (b) Simulons.

```python
def K_thomas_theorique(r, kappa, sigma):
    return np.pi * r ** 2 + (1 / kappa) * (1 - np.exp(-r ** 2 / (4 * sigma ** 2)))

rs12 = np.array([0.25, 0.5, 1.0, 1.5, 2.0])
for kappa, mu, sigma, B in [(0.5, 2, 0.4, 500), (0.08, 12, 0.4, 300)]:
    rng12 = np.random.default_rng(12)
    Ks, effectifs = [], []
    while len(Ks) < B:
        pts12 = semis_thomas(kappa, mu, sigma, rng12)
        if len(pts12) > 10:
            Ks.append(ripley_K(pts12, rs12))
            effectifs.append(len(pts12))
    Ks = np.array(Ks)
    theo = K_thomas_theorique(rs12, kappa, sigma)
    tab = pd.DataFrame({"r": rs12, "pi r^2 (hasard)": np.pi * rs12 ** 2, "K théorique": theo, "K simulé (moyenne)": np.nanmean(Ks, axis=0)})
    tab["écart_%"] = 100 * (tab["K simulé (moyenne)"] / tab["K théorique"] - 1)
    print(f"kappa = {kappa}, mu = {mu}, sigma = {sigma}  ({B} semis) | nombre de points : moyenne {np.mean(effectifs):.0f}, "
          f"écart-type {np.std(effectifs):.0f}, coefficient de variation {np.std(effectifs) / np.mean(effectifs):.0%}")
    print(tab.round(2).to_string(index=False))
    print()
```
<!--sortie-->
```text
kappa = 0.5, mu = 2, sigma = 0.4  (500 semis) | nombre de points : moyenne 101, écart-type 17, coefficient de variation 16%
   r  pi r^2 (hasard)  K théorique  K simulé (moyenne)  écart_%
0.25             0.20         0.38                0.38    -0.15
0.50             0.79         1.43                1.43    -0.19
1.00             3.14         4.72                4.68    -0.82
1.50             7.07         9.01                8.81    -2.25
2.00            12.57        14.56               13.96    -4.13

kappa = 0.08, mu = 12, sigma = 0.4  (300 semis) | nombre de points : moyenne 97, écart-type 31, coefficient de variation 32%
   r  pi r^2 (hasard)  K théorique  K simulé (moyenne)  écart_%
0.25             0.20         1.36                1.46     7.63
0.50             0.79         4.83                5.16     6.94
1.00             3.14        13.02               13.67     4.95
1.50             7.07        19.20               19.05    -0.77
2.00            12.57        25.04               23.21    -7.34
```

Pour le premier réglage (agrégats faibles et nombreux : en moyenne 2 descendants par centre), la simulation retrouve la théorie à moins de 1 % jusqu'à $r=1$ km, puis s'en écarte de $-2{,}3\,\%$ à 1,5 km et de $-4{,}1\,\%$ à 2 km. Pour le second (agrégats forts : 12 descendants par centre), les écarts sont nettement plus importants et de **signe variable** : $+7{,}6\,\%$ à 0,25 km, $+5\,\%$ à 1 km, $-7{,}3\,\%$ à 2 km. **Cela ne signifie pas que la formule est fausse**, mais que l'**estimateur** $\hat K$ est biaisé quand le nombre total de points varie beaucoup d'un semis à l'autre : le coefficient de variation de $n$ est de 16 % pour le premier réglage et de 32 % pour le second (voir la ligne imprimée au-dessus de chaque tableau). Une cause probable est que l'estimateur divise par un nombre de points aléatoire, lui-même corrélé aux comptages de voisins : l'espérance d'un rapport n'est pas le rapport des espérances. Ajoutons que, pour les grandes distances, la méthode du bord n'utilise qu'une petite fraction des points (à 2 km, seuls ceux situés à plus de 2 km du bord, soit 36 %). Morale : **ne pas surinterpréter $\hat K$ pour des semis très agrégés ni aux grandes distances**, ce que résume la règle de ne pas dépasser le quart du côté de la fenêtre.

---

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
