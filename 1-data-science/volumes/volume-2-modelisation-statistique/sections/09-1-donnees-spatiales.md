## 9.1 Données spatiales et cartes

> 💡 **Intuition.** Dans un tableau ordinaire, l'ordre des lignes n'a aucune importance : on peut les mélanger sans rien changer à la moyenne, à la régression ou au test. Dans des données spatiales, **où** se trouve chaque ligne fait partie de l'information. Deux clients voisins se ressemblent plus que deux clients éloignés, et c'est précisément ce qui casse l'hypothèse d'**indépendance** sur laquelle reposent presque tous les outils du volume I et des chapitres 1 et 2 de ce volume.

### 9.1.1 Pourquoi l'espace change tout

Un petit exemple pour sentir le problème. La gérante a mesuré le délai de quatre livraisons : deux à Ville A (notées A et B, à quelques rues l'une de l'autre) et deux à Ville C (C et D). Les délais sont 6, 7, 3 et 4 jours.

La moyenne est $(6+7+3+4)/4=5$ jours, et l'écart-type est d'environ 1,83 jour. Si les quatre livraisons étaient **indépendantes**, l'écart-type de la moyenne serait $s/\sqrt n\approx 0{,}91$ jour : la formule du volume I (section 2.4). Mais A et B ont subi la même route embouteillée, C et D la même autoroute fluide. En réalité, nous n'avons pas **quatre** informations indépendantes, mais plutôt **deux** (une par ville). Notre moyenne est beaucoup moins précise que ne le dit la formule.

> ⚠️ **Le danger concret.** Avec des observations corrélées dans l'espace, les erreurs-types « habituelles » sont **trop petites**, les intervalles de confiance trop étroits et les p-valeurs trop optimistes. Nous aurons l'impression d'avoir 200 observations alors que nous en avons, au sens de l'information, bien moins. C'est la raison pour laquelle il faut **mesurer** la dépendance spatiale avant de lui faire confiance, et c'est l'objet de tout ce chapitre.

> 🧪 **La loi de Tobler en une phrase.** « Tout est lié à tout le reste, mais ce qui est proche est plus lié que ce qui est lointain. » Ce n'est pas un théorème, c'est une observation qui se vérifie pour les prix de l'immobilier, la température, les délais de livraison, les maladies contagieuses… et qui justifie tous les outils qui suivent : ils mesurent *à quelle vitesse* la ressemblance s'estompe avec la distance.

### 9.1.2 Trois types de données spatiales

Selon ce qui est aléatoire et ce qui est fixe, on distingue trois grandes familles. Savoir dans quelle famille on se trouve est la **première** question à se poser, car elle détermine les outils.

| Type | Ce qu'on observe | Ce qui est fixe / aléatoire | Exemple la boutique | Outils (section) |
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
    "ville": ["Ville E", "Ville A", "Ville B", "Ville D", "Kairouan", "Ville C", "Gafsa", "Gabès", "Djerba", "Tozeur"],
    "lat":   [36.81, 37.27, 36.46, 35.83, 35.68, 34.74, 34.43, 33.88, 33.88, 33.92],
    "lon":   [10.18,  9.87, 10.74, 10.61, 10.10, 10.76,  8.78, 10.10, 10.86,  8.13],
})
print(villes.to_string(index=False))
```
<!--sortie-->
```text
   ville   lat   lon
   Ville E 36.81 10.18
 Ville A 37.27  9.87
  Ville B 36.46 10.74
  Ville D 35.83 10.61
Kairouan 35.68 10.10
    Ville C 34.74 10.76
   Gafsa 34.43  8.78
   Gabès 33.88 10.10
  Djerba 33.88 10.86
  Tozeur 33.92  8.13
```

**Piège n° 1 : un degré n'est pas une distance fixe.** Un degré de latitude vaut toujours à peu près 111 km (la Terre est presque une sphère de rayon $R\approx 6371$ km, et $1^\circ=\pi/180$ radian, donc $R\pi/180\approx 111{,}2$ km). Mais les méridiens se **rapprochent** quand on monte vers le pôle : un degré de longitude vaut $111{,}2\times\cos\varphi$ km. À la latitude de Ville E (environ 37°), $\cos 37^\circ\approx0{,}80$ : un degré de longitude ne vaut que **89 km**.

Faisons un calcul à la main pour Ville E (36,81 ; 10,18) et Ville A (37,27 ; 9,87) :

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
print("Ville E - Ville A :", round(float(haversine(36.81, 10.18, 37.27, 9.87)), 1), "km")
```
<!--sortie-->
```text
1 degré de latitude  : 111.2 km
1 degré de longitude à 36° N : 90.0 km   (111,2 x cos 36° = 90.0 )
Ville E - Ville A : 58.1 km
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
paires = [("Ville E", "Ville A"), ("Ville E", "Ville C"), ("Ville E", "Tozeur"), ("Ville A", "Djerba"), ("Tozeur", "Djerba")]
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
 Ville E-Ville A          58.1             61.7       6.2         58.4          0.5
    Ville E-Ville C         236.0            239.0       1.3        236.1          0.0
  Ville E-Tozeur         371.2            394.0       6.1        371.3          0.0
Ville A-Djerba         387.4            392.7       1.4        387.5          0.0
 Tozeur-Djerba         252.0            303.6      20.5        247.8         -1.7
```

Le raccourci « degrés bruts » **surestime** toujours (puisque $\cos\varphi<1$) : l'erreur va de 1 % à 20 % selon la direction du trajet. Elle est la plus forte pour Tozeur–Djerba, un trajet presque exactement est-ouest (la différence de latitude est minime, celle de longitude est de plus de 2,7°), et la plus faible pour Ville E–Ville C et Ville A–Djerba, qui sont surtout nord-sud. La projection équirectangulaire, elle, reste à moins de 2 % d'erreur sur toutes ces paires, ce qui est excellent pour une région de la taille de la Tunisie. C'est pour cela que, dans la pratique, on **projette** les coordonnées dans un système plan local, mesuré en mètres ou en kilomètres (le système UTM, par exemple, fournit des zones de 6° de longitude, et la zone 32 couvre l'essentiel de la Tunisie), puis on travaille avec des distances euclidiennes ordinaires. Pour la suite de ce chapitre, nos zones font 100 km de côté : nous utiliserons directement des coordonnées planes **en kilomètres**.

> ⚠️ **À vol d'oiseau n'est pas « en camion ».** Les distances calculées ici sont des distances **à vol d'oiseau**. Entre deux villes, la distance **routière** est plus longue (parfois 30 % de plus), et le temps de trajet dépend de la route. Pour des questions de logistique, la bonne « distance » entre deux points est souvent un temps de parcours, qui n'est pas forcément symétrique ni euclidienne. Les outils de ce chapitre fonctionnent avec n'importe quelle distance… à condition que ses propriétés conviennent (nous y reviendrons aux sections 9.2 et 9.3).

### 9.1.4 Une carte sans fond de carte

Sans bibliothèque de cartographie, une carte est simplement un nuage de points $(x,y)$ avec **un rapport d'aspect correct** (un kilomètre vers l'est doit occuper la même longueur à l'écran qu'un kilomètre vers le nord). Pour des coordonnées en degrés, on y parvient en réglant le rapport d'aspect à $1/\cos\varphi_0$, ce qui revient à la projection équirectangulaire. Voyons-le avec les villes de la boutique, en dessinant un **symbole proportionnel** : la surface du disque est proportionnelle au nombre de clients de la ville (le fichier `clients.csv`, qui vit dans l'univers simulé du volume).

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
        decal, ha = ((-6, -11), "right") if r["ville"] == "Kairouan" else ((5, 4), "left")   # évite le disque de Ville D
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
Ville A      208    217.9
Ville B       252    243.6
Ville C         282    245.6
Ville D       337    247.0
Ville E        620    245.5
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
ax1.set_title("Ventes par habitant (€) par délégation")
ax1.set_xlabel("x (km)"); ax1.set_ylabel("y (km)")
fig.colorbar(im, ax=ax1, shrink=0.8, label="€ par habitant")

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
