## 3.4 ➕ Pour aller plus loin : cartes et visualisation géospatiale

La gérante demande : « *peux-tu me montrer d'où viennent nos ventes ? Une carte, ce serait parlant.* » Une carte est le bon graphique quand **la position compte** (où se trouvent les clients, où sont les entrepôts) et le mauvais quand la question porte sur un **classement** ou sur une **évolution**. Cette section construit deux types de cartes, **sans aucune donnée géographique réelle** : les 20 villes de la boutique sont des points d'un **plan fictif** (en kilomètres), ce qui suffit à toucher tous les pièges du genre sans télécharger un fond de carte, ni dépendre d'un service tiers.

### 3.4.1 Les données : des villes dans un plan fictif

Le fichier `villes.csv` donne, pour chaque ville, deux coordonnées (`x_km`, `y_km`) dans un rectangle de 120 par 90 kilomètres, une **région** fictive et un **nombre d'habitants** fictif. On y ajoute le chiffre d'affaires 2025 de chaque ville (les clients ont une ville ; les commandes, un client).

```python
v = O.ventes_villes(x)
print(v.sort_values("ca", ascending=False)[["region", "habitants", "ca", "par_habitant"]].head(5).round({"ca": 0, "par_habitant": 1}))
print("chiffre d'affaires total des 20 villes :", O.fr(v["ca"].sum()), "€ | habitants :", O.fr(v["habitants"].sum()))
```
<!--sortie-->
```text
           region  habitants        ca  par_habitant
ville                                               
Ville A  Région 1      43700  184324.0           4.2
Ville B  Région 1     170000  164880.0           1.0
Ville C  Région 3      11300  121696.0          10.8
Ville D  Région 3      17000  116870.0           6.9
Ville E  Région 3      47800  102757.0           2.1
chiffre d'affaires total des 20 villes : 1 324 764 € | habitants : 1 307 700
```
<!--sortie-->

Le **chiffre d'affaires** et le **chiffre d'affaires par habitant** ne racontent pas la même histoire : une grande ville peut vendre beaucoup sans que sa population achète beaucoup. On va le voir de deux façons.

### 3.4.2 Les cercles proportionnels

Quand on a un **nombre par lieu**, la carte la plus fidèle est souvent celle des **cercles proportionnels** : un cercle par ville, centré sur sa position, dont la **surface** est proportionnelle à la valeur. On proportionne la **surface** et non le rayon : doubler la valeur doit doubler l'aire ; si l'on doublait le rayon, l'aire quadruplerait et l'œil surestimerait l'écart (c'est l'argument `s` de `scatter`, qui est une surface).

```python
fig, ax = plt.subplots(figsize=(6.4, 4.6))
ax.scatter(v["x_km"], v["y_km"], s=v["ca"] / v["ca"].max() * 1500, color=style.BLEU, alpha=0.55, edgecolor="white")
for ville, r in v.nlargest(5, "ca").iterrows():
    ax.annotate(f"{ville}\n{r['ca'] / 1000:.0f} k€", (r["x_km"], r["y_km"]), ha="center", va="center", fontsize=8, color=style.ENCRE)
ax.set(xlabel="km (plan fictif)", ylabel="km", aspect="equal", xlim=(-5, 125), ylim=(-5, 95)); ax.grid(False)
ax.set_title("Chiffre d'affaires 2025 par ville (surface du cercle proportionnelle)", loc="left", fontweight="bold", fontsize=10)
O.sauver(fig, "ch03-carte-cercles.png")
print("les 5 premières villes pèsent", round(v.nlargest(5, "ca")["ca"].sum() / v["ca"].sum() * 100), "% du chiffre d'affaires")
```
<!--sortie-->
```text
figure : ch03-carte-cercles.png
les 5 premières villes pèsent 52 % du chiffre d'affaires
```
<!--sortie-->

![Carte en cercles proportionnels dans un plan fictif : les 5 premières villes sont annotées.](figures/ch03-carte-cercles.png)

La carte montre **où** se concentre l'activité, et qu'elle n'est pas répartie comme le territoire. On a laissé une échelle en kilomètres et un repère orthonormé (`aspect="equal"`) : sans cela, les distances seraient déformées. Elle ne permet toutefois pas de **lire** les valeurs : pour cela, il faut un tableau ou des barres.

### 3.4.3 Une carte colorée (choroplèthe) sur des territoires fictifs

Une carte **choroplèthe** colore des **zones** selon une valeur. Sans fonds de carte administratif, on découpe le plan en **zones d'influence** : à chaque ville son **polygone de Voronoï**, l'ensemble des points du plan plus proches d'elle que de toute autre. Le calcul tient en quelques lignes (la fonction `voronoi_polygones` de `outils_ch03.py` coupe un rectangle par la médiatrice de chaque paire de villes). On colore ensuite par une échelle **séquentielle** (du clair au foncé), jamais par un arc-en-ciel.

```python
from matplotlib.patches import Polygon
pts = v[["x_km", "y_km"]].to_numpy()
zones = O.voronoi_polygones(pts, borne=(0, 120, 0, 90))
fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
for ax, col, titre in zip(axes, ("ca", "par_habitant"), ("chiffre d'affaires (k€)", "chiffre d'affaires par habitant (€)")):
    val = v[col] / (1000 if col == "ca" else 1)
    norm = plt.Normalize(val.min(), val.max())
    for poly, valeur in zip(zones, val):
        ax.add_patch(Polygon(poly, facecolor=style.SEQ(norm(valeur)), edgecolor="white", linewidth=1))
    ax.scatter(pts[:, 0], pts[:, 1], s=6, color=style.ENCRE); ax.set(xlim=(0, 120), ylim=(0, 90), aspect="equal", xticks=[], yticks=[]); ax.grid(False)
    ax.set_title(titre, loc="left", fontsize=10); fig.colorbar(plt.cm.ScalarMappable(norm, style.SEQ), ax=ax, shrink=0.7)
O.sauver(fig, "ch03-carte-choroplethe.png")
print("zones :", len(zones), "| ville la plus foncée, par habitant :", v["par_habitant"].idxmax(), "| en chiffre d'affaires :", v["ca"].idxmax())
```
<!--sortie-->
```text
figure : ch03-carte-choroplethe.png
zones : 20 | ville la plus foncée, par habitant : Ville C | en chiffre d'affaires : Ville A
```
<!--sortie-->

![Deux cartes colorées du même plan fictif : à gauche le chiffre d'affaires, à droite le chiffre d'affaires par habitant.](figures/ch03-carte-choroplethe.png)

Les deux cartes se ressemblent par endroits (les villes A, C, D et E sont foncées des deux côtés) et divergent pour les **grandes villes**. **Ville B**, deuxième en chiffre d'affaires, est pâle sur la carte de droite : 170 000 habitants qui rapportent environ 1 € chacun. À l'inverse, **Ville C**, avec 11 300 habitants, rapporte près de 11 € par habitant. Le lecteur de la carte de gauche voit en Ville B un marché majeur ; celui de la carte de droite, un marché à peine exploité. **Aucun n'a tort** : ils répondent à deux questions différentes (« où est le chiffre d'affaires ? » et « où la clientèle est-elle la plus dense ? »). La règle d'or : **une valeur absolue sur une carte reflète d'abord la population** ; pour mesurer une intensité, on **normalise** (par habitant, par client, par magasin).

### 3.4.4 Le biais des grandes zones

Il existe un second piège, **visuel** celui-là : l'œil juge l'importance d'une zone à sa **surface**, pas à sa valeur. Or la surface d'un territoire n'a presque aucun lien avec le nombre de personnes qui y vivent : sur notre plan, les villes les plus peuplées sont serrées, les moins peuplées ont de la place.

```python
def aire(p):
    return 0.5 * abs(np.dot(p[:, 0], np.roll(p[:, 1], -1)) - np.dot(p[:, 1], np.roll(p[:, 0], -1)))
v["surface_zone"] = [aire(p) for p in zones]
gros = v.nlargest(5, "habitants")
print("corrélation surface de la zone / habitants :", round(v["surface_zone"].corr(v["habitants"]), 2))
print("les 5 villes les plus peuplées :", round(gros["habitants"].sum() / v["habitants"].sum() * 100), "% des habitants,", round(gros["surface_zone"].sum() / v["surface_zone"].sum() * 100), "% de la carte")
```
<!--sortie-->
```text
corrélation surface de la zone / habitants : 0.17
les 5 villes les plus peuplées : 54 % des habitants, 24 % de la carte
```
<!--sortie-->

La corrélation est faible : la taille des zones ne suit pas la population. Les cinq villes les plus peuplées regroupent plus de la moitié des habitants, mais n'occupent qu'un quart de la carte : une carte colorée **sous-représente visuellement** les endroits où vit le plus de monde, et donne de l'importance à des territoires peu peuplés. Les remèdes sont connus : des **cercles proportionnels** (3.4.2), qui donnent à chaque lieu une taille liée à sa valeur ; des **cartes en carreaux** (une case de même taille par entité) ; et surtout **joindre un tableau ou des barres** à toute carte qui sert à comparer.

### 3.4.5 Une carte, ou un tableau ?

Si la question est « quelles sont les cinq premières villes ? », une carte est le **mauvais** outil : on ne classe pas des surfaces à l'œil. Un diagramme en barres horizontales, trié, répond mieux, en montrant en plus les valeurs.

```python
tri = v.sort_values("ca")
top5 = list(tri.index[-5:])
fig, ax = plt.subplots(figsize=(6.2, 4.6))
ax.barh(tri.index, tri["ca"] / 1000, color=[style.BLEU if ville in top5 else style.MUET for ville in tri.index])
ax.set(xlabel="k€, 2025"); ax.grid(axis="y", visible=False); ax.set_axisbelow(True)
ax.set_title("Le classement est plus lisible en barres qu'en carte", loc="left", fontweight="bold", fontsize=10)
O.sauver(fig, "ch03-carte-ou-barres.png")
rang = v["ca"].rank(ascending=False); rang_h = v["par_habitant"].rank(ascending=False)
print("corrélation de rang (chiffre d'affaires, par habitant) :", round(rang.corr(rang_h), 2), "| villes dans les cinq premières des deux classements :", sorted(set(rang[rang <= 5].index) & set(rang_h[rang_h <= 5].index)))
```
<!--sortie-->
```text
figure : ch03-carte-ou-barres.png
corrélation de rang (chiffre d'affaires, par habitant) : 0.62 | villes dans les cinq premières des deux classements : ['Ville A', 'Ville C', 'Ville D', 'Ville E']
```
<!--sortie-->

![Le classement des villes en barres horizontales triées.](figures/ch03-carte-ou-barres.png)

Les barres rendent le classement immédiat, avec les cinq premières villes en bleu. Elles ne disent pas **où** sont les villes : c'est le rôle de la carte. La combinaison gagnante est donc **la carte pour la position, les barres pour la valeur** : deux graphiques complémentaires plutôt qu'un graphique qui fait mal les deux.

### 3.4.6 Projection : pourquoi une carte déforme

Représenter une surface courbe (la Terre) sur une feuille plate impose de **déformer** : aucune projection ne conserve à la fois les surfaces, les distances et les angles. Notre plan fictif est plat, donc exempt de ce problème ; avec de vraies coordonnées (latitude, longitude, exprimées en degrés), il faut le connaître. Un degré de longitude, par exemple, ne représente pas la même distance partout.

```python
for lat in (0, 45, 60, 75):
    print(f"latitude {lat:2d}° : 1° de longitude vaut {111.32 * np.cos(np.radians(lat)):6.1f} km | 1° de latitude vaut environ 111 km")
```
<!--sortie-->
```text
latitude  0° : 1° de longitude vaut  111.3 km | 1° de latitude vaut environ 111 km
latitude 45° : 1° de longitude vaut   78.7 km | 1° de latitude vaut environ 111 km
latitude 60° : 1° de longitude vaut   55.7 km | 1° de latitude vaut environ 111 km
latitude 75° : 1° de longitude vaut   28.8 km | 1° de latitude vaut environ 111 km
```
<!--sortie-->

Un graphique tracé directement en degrés (longitude en abscisse, latitude en ordonnée) étire donc les régions éloignées de l'équateur. Les outils de cartographie gèrent les projections pour vous, mais il faut savoir qu'elles existent et **choisir** celle qui convient à la question (surfaces, distances ou angles).

### 3.4.7 Les outils réels : à décrire, non exécutés ici

Avec de vraies données géographiques, on utilise des bibliothèques spécialisées : **geopandas** (des tableaux pandas dont une colonne est une géométrie, avec jointures spatiales et projections) et **folium** (cartes interactives dans le navigateur, sur fonds de carte). Voici à quoi ressemble une carte choroplèthe réelle ; ce bloc est **non exécuté** ici (aucune donnée géographique n'est utilisée dans ce livre et aucun accès réseau n'est fait).

```python noexec
# non exécuté : nécessite geopandas et un fichier de contours administratifs (hypothétique)
import geopandas as gpd
zones = gpd.read_file("contours_regions.geojson")                 # une ligne par région, une colonne « geometry »
carte = zones.merge(ventes_par_region, on="region")              # jointure attributaire
carte.plot(column="ca_par_habitant", cmap="Blues", legend=True, edgecolor="white")
```

Deux questions de **droits** se posent dès que l'on sort du plan fictif. Les **tuiles** (les images du fond de carte que les cartes interactives téléchargent) viennent de services tiers, avec des **conditions d'utilisation** et des mentions d'**attribution** obligatoires, et parfois des limites d'usage ou un coût ; il faut les lire. Les **contours administratifs** et les **bases d'adresses** ont aussi une licence, qui peut interdire la redistribution : on la vérifie avant de publier une carte. Enfin, une carte de **personnes** (clients, patients) peut révéler des informations personnelles : des points précis sur une carte sont des **adresses** ; on les **agrège** (par zone, avec des seuils de petits effectifs) avant de les montrer (volume II, chapitre 5).

> ✅ **À retenir.** Une carte est utile quand la **position** compte ; on proportionne la **surface** (cercles), on **normalise** les valeurs absolues (par habitant), on se méfie du **biais des grandes zones**, et l'on joint des **barres** à toute carte qui doit servir à comparer. Les projections déforment, les fonds de carte ont des licences, et des points précis sur des personnes sont des données personnelles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.9, exercices 3.15 et 3.16.

```python hide
assert [round(v.loc["Ville B", c], 1) for c in ("par_habitant",)] == [1.0] and round(v.loc["Ville C", "par_habitant"]) == 11
assert v.loc["Ville B", "ca"] == v["ca"].nlargest(2).iloc[-1] and v.loc["Ville B", "habitants"] == 170000 and v.loc["Ville C", "habitants"] == 11300
assert set(v["ca"].nlargest(5).index) & set(v["par_habitant"].nlargest(5).index) == {"Ville A", "Ville C", "Ville D", "Ville E"}
assert gros["habitants"].sum() / v["habitants"].sum() > 0.5 and gros["surface_zone"].sum() / v["surface_zone"].sum() < 0.26 and v["surface_zone"].corr(v["habitants"]) < 0.3
```
<!--sortie-->
