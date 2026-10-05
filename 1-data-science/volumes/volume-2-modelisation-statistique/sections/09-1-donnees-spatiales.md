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

```python hide
import numpy as np
import pandas as pd

villes = pd.DataFrame({
    "ville": ["Ville A", "Ville B", "Ville C", "Ville D", "Ville E", "Ville F", "Ville G", "Ville H", "Ville I", "Ville J"],
    "lat":   [47.30, 46.90, 46.40, 45.80, 45.30, 44.70, 47.00, 46.00, 45.20, 44.30],
    "lon":   [ 3.20,  4.60,  3.60,  4.90,  3.40,  5.30,  6.40,  6.70,  6.60,  3.70],
})
```

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

```python hide-code
lat, lon = villes["lat"].to_numpy(), villes["lon"].to_numpy()
D = haversine(lat[:, None], lon[:, None], lat[None, :], lon[None, :])     # (10, 10)
i, j = np.triu_indices(10, 1)
loin, pres = D[i, j].argmax(), D[i, j].argmin()
print(f"plus grande distance : {villes.ville[i[loin]]} - {villes.ville[j[loin]]} = {D[i, j][loin]:.0f} km")
print(f"plus petite distance : {villes.ville[i[pres]]} - {villes.ville[j[pres]]} = {D[i, j][pres]:.0f} km")
print("matrice symétrique :", np.allclose(D, D.T), "| diagonale nulle :", np.allclose(np.diag(D), 0))
```
<!--sortie-->
```text
plus grande distance : Ville G - Ville J = 366 km
plus petite distance : Ville H - Ville I = 89 km
matrice symétrique : True | diagonale nulle : True
```

Sur quelques paires, mesurons l'erreur que l'on commet avec deux raccourcis tentants : (a) traiter les degrés comme des unités égales ($111{,}2\times$ la distance euclidienne en degrés), (b) projeter à plat avec la **projection équirectangulaire** centrée sur la latitude moyenne $\varphi_0$ des villes, $x=R(\lambda-\lambda_0)\cos\varphi_0$ et $y=R(\varphi-\varphi_0)$, puis prendre la distance euclidienne.

```python hide-code
def naif(lat1, lon1, lat2, lon2):
    return 111.19 * np.hypot(lat2 - lat1, lon2 - lon1)

def equirect(lat1, lon1, lat2, lon2, lat0):
    c = np.cos(np.radians(lat0))
    return R * np.radians(1) * np.hypot(lat2 - lat1, (lon2 - lon1) * c)

lat0 = villes["lat"].mean()
paires = [("Ville A", "Ville B"), ("Ville A", "Ville J"), ("Ville A", "Ville G"), ("Ville G", "Ville J"), ("Ville C", "Ville H")]
lignes = []
for a, b in paires:
    ra, rb = villes.set_index("ville").loc[a], villes.set_index("ville").loc[b]
    vrai = float(haversine(ra.lat, ra.lon, rb.lat, rb.lon))
    n = float(naif(ra.lat, ra.lon, rb.lat, rb.lon))
    e = float(equirect(ra.lat, ra.lon, rb.lat, rb.lon, lat0))
    lignes.append({"paire": f"{a[-1]}-{b[-1]}", "haversine_km": vrai, "degres_bruts_km": n, "erreur_%": 100 * (n / vrai - 1),
                   "equirect_km": e, "erreur_eq_%": 100 * (e / vrai - 1)})
print(pd.DataFrame(lignes).round(1).to_string(index=False))
```
<!--sortie-->
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

```python hide
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

clients = pd.read_csv("donnees/clients.csv")
par_ville = clients.groupby("ville").agg(clients=("id_client", "size"), depense=("depense_annuelle", "mean")).round(1)
print(par_ville.to_string())

carte = villes.merge(par_ville, left_on="ville", right_index=True, how="left")   # les villes F à J n'ont pas de clients dans ce fichier
BLEU, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"

fig, axes = plt.subplots(1, 2, figsize=(10.5, 5.2))
for ax, titre, corrige in zip(axes, ["Degrés traités comme des unités égales", "Aspect corrigé (1 / cos de la latitude)"], [False, True]):
    ax.scatter(carte["lon"], carte["lat"], s=18, color=ORANGE, zorder=3)
    ax.scatter(carte["lon"], carte["lat"], s=carte["clients"].fillna(0) * 1.5, color=BLEU, alpha=0.35, zorder=2)
    for _, r in carte.iterrows():
        ax.annotate(r["ville"][-1], (r["lon"], r["lat"]), xytext=(6, 5), ha="left", textcoords="offset points", fontsize=9)
    ax.set_title(titre, fontsize=10)
    ax.set_xlabel("longitude (°E)")
    ax.set_xlim(2.4, 7.6)
    ax.set_ylim(43.8, 47.8)
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
Ville B      252    243.6
Ville C      282    245.6
Ville D      337    247.0
Ville E      620    245.5
figure enregistrée
```

![Les dix villes fictives (points orange, nommées par leur lettre) et, pour les villes A à E, les effectifs de clients (disques bleus, surface proportionnelle). À gauche : un degré de longitude est dessiné aussi long qu'un degré de latitude, ce qui étire la carte d'est en ouest. À droite : le rapport d'aspect 1/cos(φ) rétablit les proportions.](figures/ch09-carte-villes.png)

Deux conseils de lecture. Les disques sont **proportionnels en surface** et non en rayon : si l'on doublait le rayon pour doubler la valeur, l'œil verrait une surface quatre fois plus grande, et le graphique mentirait. Et la carte de gauche, qui traite les degrés comme des unités égales (c'est ce que fait un `scatter(lon, lat)` avec `aspect="equal"`), déforme les distances : les villes y paraissent plus éloignées d'est en ouest qu'elles ne le sont.

Le même principe vaut pour les zones : pour afficher une valeur par zone (données surfaciques), on dessine une grille colorée (une « carte choroplèthe » dans le jargon). Deux jeux de données simulés servent de fil conducteur à la suite du chapitre.

| Jeu de données | Fichier | Contenu | Utilisé en |
|---|---|---|---|
| **Zones** (surfacique) | `donnees/ch09-zones.csv` | une grille $12\times12$ de 144 zones fictives de 5 km de côté ; ventes par habitant avec une autocorrélation spatiale *connue*, plus une variable témoin sans aucune structure spatiale | 9.2 |
| **Livraisons** (géostatistique) | `donnees/ch09-livraisons.csv` | 200 adresses dans un carré de 100 km de côté, avec le délai de livraison en jours, qui varie de façon continue dans l'espace | 9.3 |

```python hide
zones = pd.read_csv("donnees/ch09-zones.csv")
liv = pd.read_csv("donnees/ch09-livraisons.csv")
print("zones :", zones.shape, "| livraisons :", liv.shape)
print(liv["delai_jours"].describe().round(2).to_string())

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(11, 4.6))

# Gauche : carte « choroplèthe » des ventes par habitant, grille 12 x 12 (une case = 5 km x 5 km)
grille = zones["ventes_hab"].to_numpy().reshape(12, 12)
im = ax1.imshow(grille, origin="lower", extent=(0, 60, 0, 60), cmap="Blues")
ax1.set_title("Ventes par habitant (€) par zone")
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
zones : (144, 8) | livraisons : (200, 4)
count    200.00
mean       4.27
std        1.10
min        1.59
25%        3.62
50%        4.26
75%        5.07
max        7.53
figure enregistrée
```

![À gauche : ventes par habitant par zone (grille 12 × 12). À droite : délais de livraison observés en 200 adresses d'un carré de 100 km de côté.](figures/ch09-donnees-chapitre.png)

La carte de gauche ne ressemble pas à du « sel et poivre » : on y voit nettement une plage de faibles ventes au sud-est et des plages de fortes ventes au centre et au nord. La carte de droite est bien plus difficile à lire : des points de teintes voisines se côtoient, mais d'autres se mêlent, et l'œil hésite entre structure et hasard. C'est exactement pour cela qu'il faut **chiffrer** l'impression plutôt que de s'y fier. Mais avant, une mise en garde sur le dessin lui-même.

> ⚠️ **Les cartes mentent facilement.** Trois pièges classiques : (1) **la palette**, car une rampe séquentielle (clair → foncé) convient à une quantité ordonnée, et un arc-en-ciel invente des frontières qui n'existent pas ; (2) **les classes**, car découper une valeur continue en cinq paliers « égaux » ou en quantiles change complètement l'image ; (3) **la surface** : une grande zone peu peuplée attire l'œil autant qu'une petite zone très peuplée. Nous reviendrons sur ce dernier point dans le cahier (le *problème de l'unité spatiale modifiable*, exercice 9.7).

> ✅ **À retenir.**
> - L'espace casse l'**indépendance** : des observations proches se ressemblent, les erreurs-types usuelles sont trop optimistes.
> - Trois familles : **géostatistique** (valeurs en des points d'un champ continu), **surfacique** (une valeur par zone), **semis de points** (les positions sont aléatoires). On se demande d'abord : *qu'est-ce qui est aléatoire ?*
> - Un degré de longitude ne vaut pas un degré de latitude : $111{,}2\cos\varphi$ km contre 111,2 km. Pour des distances sur la Terre, on utilise **haversine** (ou on projette dans un plan local en kilomètres).
> - Une carte sans fond de carte reste utile : rapport d'aspect correct, symboles proportionnels **en surface**, palette séquentielle.

> 📒 **Pour s'entraîner.** Cahier, chapitre 9 : application 9.1, exercices 9.1 et 9.2.
