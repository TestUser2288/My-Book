# Chapitre 1 : Principes de visualisation — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 1 du livre. Les **applications** sont de petites études guidées sur les données de la boutique : vous les refaites pas à pas, en produisant ou en critiquant des graphiques. Les **exercices** (⭐ à la main ou en une ligne, ⭐⭐ calcul puis code, ⭐⭐⭐ étude plus ouverte) sont **corrigés** à la fin. Presque tous demandent de **produire ou de juger un graphique ou un texte** : relisez toujours votre réponse comme le ferait la gérante, en trois secondes. Les données sont **simulées** ; les figures du cahier portent le préfixe `ch01-c-`.

Une première cellule charge les bibliothèques et les tables de la boutique ; les suivantes reprennent les noms ainsi définis.

```python
import os, sys, itertools
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
import matplotlib.pyplot as plt
import style, outils_ch01 as O

c = O.charger()                              # les tables de la boutique (simulées)
x, j, liv, sess = c["x"], c["j"], c["liv"], c["sess"]
fr = O.fr                                    # nombre à la française : 1 325,8
print(len(x), "lignes |", len(j), "jours |", len(liv), "livraisons |", len(sess), "sessions")
```
<!--sortie-->
```text
83905 lignes | 1096 jours | 19420 livraisons | 127022 sessions
```
<!--sortie-->

## Applications

### Application 1.1 — Une question, une forme (section 1.1)

**Objectif.** Partir d'une question écrite, et en déduire la forme du graphique.

**Étape 1 — la question.** Écrivez-la en une phrase : *« Quelle part du chiffre d'affaires 2025 vient de chaque canal ? »* C'est une **composition** (des parts d'un total) avec trois catégories : des barres triées conviennent, et un camembert serait ici acceptable (trois parts, l'une proche de la moitié).

**Étape 2 — le calcul.** On calcule les parts, on les trie.

```python
ca = O.ca_mensuel(2025, "canal").sum().sort_values()       # CA 2025 par canal, en €
part = ca / ca.sum() * 100
print(part.round(1).to_string())
```
<!--sortie-->
```text
canal
Réseaux     11.0
Boutique    42.3
Site        46.6
```
<!--sortie-->

**Étape 3 — la figure.** Barres horizontales triées, une couleur d'accent sur le canal du message, valeurs écrites, titre qui énonce la conclusion.

```python
fig, ax = plt.subplots(figsize=(7, 2.4))
ax.barh(part.index, part.values, color=[O.GRIS, O.GRIS, O.BLEU]); ax.grid(False); ax.set_xticks([])
for i, v in enumerate(part.values):
    ax.text(v + 0.8, i, fr(v, 1) + " %", va="center")
ax.set_xlim(0, 56)
ax.set_title(f"Le site fait {fr(part['Site'], 1)} % du chiffre d'affaires, devant la boutique", loc="left", fontweight="bold", fontsize=10)
style.save(fig, "ch01-c-canaux.png")
```
<!--sortie-->
```text
figure : ch01-c-canaux.png
```
<!--sortie-->

![Part du chiffre d'affaires 2025 par canal en barres triées, le site en bleu (46,6 %), la boutique (42,3 %) et les réseaux (11,0 %) en gris. Figure construite avec matplotlib (données simulées).](figures/ch01-c-canaux.png)

**À vous.** Réécrivez la question pour obtenir une **évolution** (« comment la part du site évolue-t-elle de mois en mois ? ») : quelle forme choisissez-vous ? (Réponse : une courbe, parts en ordonnée, mois en abscisse.)

### Application 1.2 — Camembert contre barres : mesurer ce que l'œil perd (section 1.1.2)

**Objectif.** Chiffrer la difficulté de lire des angles voisins.

On calcule, pour les six catégories triées, l'écart entre une part et la suivante : en points de pourcentage, en degrés d'angle (100 % = 360 degrés) et en relatif.

```python
cat = O.ca_categories()
part = cat / cat.sum() * 100
haut, bas = part.iloc[:-1], part.iloc[1:].values                      # chaque part et la suivante
ecart = pd.DataFrame({"points": haut - bas, "degrés": (haut - bas) * 3.6, "relatif %": (haut / bas - 1) * 100})
print(ecart.round(1).to_string())
```
<!--sortie-->
```text
            points  degrés  relatif %
categorie                            
Jardin         3.7    13.4       16.2
Maison         3.5    12.5       17.7
Décoration     1.9     6.9       10.9
Cuisine        8.7    31.5       98.5
Bien-être      4.6    16.5      107.5
```
<!--sortie-->

**À vous.** Quelle paire de catégories voisines serait la plus difficile à départager sur un camembert ? Sur des barres, que verrait-on ? (Indice : cherchez l'écart le plus faible en degrés.)

### Application 1.3 — Redessiner en cinq gestes (section 1.2)

**Objectif.** Refaire le chemin du brouillon au graphique final sur un nouveau jeu : la part de livraisons en retard par transporteur.

```python
ret = liv.groupby("transporteur")["retard"].mean().mul(100).sort_values()       # % de livraisons en retard
fig, (avant, apres) = plt.subplots(1, 2, figsize=(10, 3.2))
avant.bar(ret.index, ret.values, color=["red", "green", "blue"]); avant.set_title("Graphique 2")        # le brouillon
apres.barh(ret.index, ret.values, color=[O.GRIS, O.GRIS, O.ROUGE]); apres.grid(False); apres.set_xticks([])
for i, v in enumerate(ret.values):
    apres.text(v + 1, i, fr(v, 1) + " %", va="center")
apres.set_xlim(0, 62)
for bord in ("top", "right", "bottom"):
    apres.spines[bord].set_visible(False)
apres.set_title("Un colis sur deux du transporteur C arrive en retard,\nun sur six chez le transporteur A", loc="left", fontweight="bold", fontsize=10)
apres.text(0, -0.95, "Livraisons arrivées après le délai promis, 2023-2025. Source : livraisons.", fontsize=8, color=O.MUET)
fig.tight_layout(w_pad=3)
style.save(fig, "ch01-c-redessin.png")
print(ret.round(1).to_string())
```
<!--sortie-->
```text
figure : ch01-c-redessin.png
transporteur
Transporteur A    16.0
Transporteur B    26.6
Transporteur C    51.0
```
<!--sortie-->

![À gauche, le brouillon (trois couleurs vives, aucun titre informatif, axe sans unité) ; à droite, le même graphique redessiné : barres triées horizontales, accent sur le transporteur C, valeurs écrites, titre qui énonce la conclusion et source. Figure construite avec matplotlib (données simulées).](figures/ch01-c-redessin.png)

**À vous.** Listez les cinq gestes appliqués (ranger, une couleur d'accent, étiqueter, titrer, relire) et ce que vous retireriez encore. Vérifiez la phrase du titre : « un sur six » correspond-il à 16,0 % ?

### Application 1.4 — Trois titres pour une même courbe, et une annotation (section 1.2.3)

**Objectif.** Écrire un titre descriptif, un titre informatif, un titre à éviter, en faisant calculer les chiffres.

```python
m = O.ca_mensuel(2025) / 1000                      # CA mensuel 2025, en k€
dec24 = O.ca_mensuel(2024)[12] / 1000
titres = {
    "descriptif": "Chiffre d'affaires mensuel 2025",
    "informatif": f"Le chiffre d'affaires de décembre ({fr(m[12])} k€) dépasse de {fr((m[12] / dec24 - 1) * 100)} % celui de décembre 2024",
    "à éviter": "Les ventes explosent en fin d'année",
}
for nom, t in titres.items():
    print(f"{nom:11s}: {t}")
fig, ax = plt.subplots(figsize=(8, 3.2))
ax.plot(m.index, m.values, color=O.BLEU); ax.set_xticks(range(1, 13)); ax.set_xticklabels([k[:1].upper() for k in O.MOIS])
ax.annotate(f"décembre : {fr(m[12])} k€", (12, m[12]), (7.6, m[12] * 0.96), arrowprops=dict(arrowstyle="-", color=O.MUET), fontsize=9)
ax.set_ylim(0, 200); ax.set_ylabel("k€")
ax.set_title(titres["informatif"], loc="left", fontweight="bold", fontsize=9.5)
style.save(fig, "ch01-c-titre.png")
```
<!--sortie-->
```text
descriptif : Chiffre d'affaires mensuel 2025
informatif : Le chiffre d'affaires de décembre (184 k€) dépasse de 17 % celui de décembre 2024
à éviter   : Les ventes explosent en fin d'année
figure : ch01-c-titre.png
```
<!--sortie-->

![Chiffre d'affaires mensuel 2025 avec le titre informatif et le repère de décembre annoté. Figure construite avec matplotlib (données simulées).](figures/ch01-c-titre.png)

**À vous.** Pourquoi « explosent » est-il un titre à éviter ? Réécrivez-le avec un chiffre et une comparaison. Ajoutez une seconde annotation (par exemple le creux de février).

### Application 1.5 — Petits multiples à échelle commune (section 1.2.5)

**Objectif.** Montrer la part de retards, mois par mois, pour chaque transporteur, avec les deux autres en gris.

```python
liv["mois"] = pd.to_datetime(liv["date_commande"]).dt.month
p = liv.pivot_table(index="mois", columns="transporteur", values="retard", aggfunc="mean") * 100
fig, axs = plt.subplots(1, 3, figsize=(10, 2.8), sharey=True)
for a, t in zip(axs, p.columns):
    for autre in p.columns:
        a.plot(p.index, p[autre], color=O.GRILLE, lw=1)
    a.plot(p.index, p[t], color=O.BLEU, lw=2); a.set_title(t, loc="left", fontsize=9); a.set_xticks([1, 6, 12])
axs[0].set_ylabel("% de livraisons en retard")
fig.suptitle("En décembre, les trois transporteurs décrochent, le transporteur C le plus", x=0.01, ha="left", fontweight="bold", fontsize=10, y=1.08)
style.save(fig, "ch01-c-multiples.png")
print(p.loc[12].round(1).to_string())
```
<!--sortie-->
```text
figure : ch01-c-multiples.png
transporteur
Transporteur A    39.7
Transporteur B    59.2
Transporteur C    85.4
```
<!--sortie-->

![Trois petits graphiques à échelle commune : part des livraisons en retard par mois, pour chacun des trois transporteurs, avec les deux autres en gris. Figure construite avec matplotlib (données simulées).](figures/ch01-c-multiples.png)

**À vous.** Que se passerait-il avec `sharey=False` ? Quel message perdrait-on ? (Voir l'exercice 1.6.)

### Application 1.6 — Simuler le daltonisme sur les trois canaux (section 1.3.3)

**Objectif.** Mesurer, pour la palette (bleu, orange, aqua) du canal Boutique, Site, Réseaux, la paire de couleurs la plus proche selon la vision.

```python
cols = {"Boutique": O.BLEU, "Site": O.ORANGE, "Réseaux": O.AQUA}
dist = lambda a, b: float(np.linalg.norm((np.array(a) - np.array(b)) * 255))
vues = ["Vision typique", "Protanopie", "Deutéranopie", "Tritanopie", "Niveaux de gris"]
lignes = []
for nom in vues:
    sim = {k: (matplotlib.colors.to_rgb(v) if nom == "Vision typique" else O.simuler(v, nom)) for k, v in cols.items()}
    d = {f"{a}-{b}": dist(sim[a], sim[b]) for a, b in itertools.combinations(sim, 2)}
    pire = min(d, key=d.get)
    lignes.append((nom, pire, round(d[pire])))
print(pd.DataFrame(lignes, columns=["vision", "paire la plus proche", "distance"]).to_string(index=False))
```
<!--sortie-->
```text
         vision paire la plus proche  distance
 Vision typique     Boutique-Réseaux       108
     Protanopie         Site-Réseaux        88
   Deutéranopie         Site-Réseaux        80
     Tritanopie     Boutique-Réseaux        33
Niveaux de gris         Site-Réseaux        20
```
<!--sortie-->

**À vous.** Dans quelle vision la paire la plus proche devient-elle la plus problématique ? Que feriez-vous pour que le graphique reste lisible ? (Étiquettes directes, marqueurs différents, traits pleins et pointillés.)

### Application 1.7 — Les contrastes de la palette, et un texte qui passe (section 1.3.4)

**Objectif.** Calculer les contrastes de la palette sur fond blanc, puis **assombrir** une couleur jusqu'à ce qu'elle serve à écrire du texte courant.

```python
def assombrir(hexa, cible=4.5, fond="#ffffff"):
    v = np.array(matplotlib.colors.to_rgb(hexa))
    while O.contraste(tuple(v), fond) < cible:
        v = v * 0.97                                   # on réduit chaque primaire de 3 %
    return matplotlib.colors.to_hex(v)
for nom, h in (("bleu", O.BLEU), ("orange", O.ORANGE), ("aqua", O.AQUA), ("violet", O.VIOLET), ("rouge", O.ROUGE)):
    sombre = assombrir(h)
    print(f"{nom:7s} sur blanc : {O.contraste(h, '#ffffff'):4.1f} -> {sombre} : {O.contraste(sombre, '#ffffff'):4.1f}")
```
<!--sortie-->
```text
bleu    sur blanc :  4.4 -> #2974d0 :  4.7
orange  sur blanc :  3.2 -> #be542a :  4.7
aqua    sur blanc :  2.8 -> #15855d :  4.6
violet  sur blanc :  8.6 -> #4a3aa7 :  8.6
rouge   sur blanc :  4.0 -> #cf4342 :  4.6
```
<!--sortie-->

**À vous.** Quelles couleurs de la palette passent **telles quelles** pour du texte courant (4,5 : 1 au moins) ? Quelle couleur assombrie garderiez-vous pour écrire en orange ? Pourquoi ne pas simplement noircir toutes les couleurs ?

### Application 1.8 — Un axe tronqué et une période choisie, mesurés (sections 1.4.1 et 1.4.5)

**Objectif.** Mesurer ce qu'un axe tronqué et une fenêtre de trois mois permettent de dire.

```python
l = x.merge(c["ret"][["id_ligne"]].assign(r=1), on="id_ligne", how="left").fillna({"r": 0})
taux = l.groupby("categorie")["r"].mean().mul(100).sort_values()            # % de lignes retournées
print(taux.round(1).to_string())
app = (taux - 5) / (taux.min() - 5)                                          # hauteurs apparentes si l'axe part de 5 %
print("catégorie la plus haute / la plus basse : axe à 5 % ->", fr(app.max(), 1), "; axe à zéro ->", fr(taux.max() / taux.min(), 2))
m = O.ca_mensuel(2025)
var = {k: m[k + 2] / m[k] - 1 for k in range(1, 11)}                          # variation sur trois mois, à partir du mois k
print("plus forte hausse : à partir du mois", max(var, key=var.get), "->", fr(max(var.values()) * 100, 1), "%")
print("plus forte baisse : à partir du mois", min(var, key=var.get), "->", fr(min(var.values()) * 100, 1), "%")
```
<!--sortie-->
```text
categorie
Papeterie     5.4
Maison        5.9
Décoration    6.0
Bien-être     6.1
Cuisine       6.1
Jardin        6.2
catégorie la plus haute / la plus basse : axe à 5 % -> 2,7 ; axe à zéro -> 1,13
plus forte hausse : à partir du mois 10 -> 53,1 %
plus forte baisse : à partir du mois 6 -> -15,9 %
```
<!--sortie-->

**À vous.** Rédigez, pour chaque cas, la phrase **trompeuse** et la phrase **honnête**.

### Application 1.9 — Entonnoir des petits effectifs (section 1.4.6)

**Objectif.** Appliquer le diagramme en entonnoir aux taux de retour de **tous** les canaux et comparer à la situation des seuls réseaux du livre.

```python
g = l.groupby("id_produit")["r"].agg(["size", "sum"]).rename(columns={"size": "n", "sum": "r"})
g["taux"] = g["r"] / g["n"]
p0 = g["r"].sum() / g["n"].sum()
e = np.sqrt(p0 * (1 - p0) / g["n"])
for nom, z in (("95 %", 1.96), ("99,8 %", 3.09)):
    print(f"borne à {nom} : {int((g['taux'] > p0 + z * e).sum())} produits au-dessus, {int((g['taux'] < p0 - z * e).sum())} en dessous")
print("effectifs de", g["n"].min(), "à", g["n"].max(), "lignes ; taux moyen", fr(p0 * 100, 1), "%")
```
<!--sortie-->
```text
borne à 95 % : 3 produits au-dessus, 4 en dessous
borne à 99,8 % : 0 produits au-dessus, 0 en dessous
effectifs de 200 à 1628 lignes ; taux moyen 6,0 %
```
<!--sortie-->

**À vous.** Comparez avec le livre (section 1.4.6) : pourquoi, avec des effectifs de 200 à 1 600 lignes plutôt que de 17 à 174, y a-t-il moins de produits « suspects » ? Que conclure du nombre de produits au-dessus de la borne à 95 % par rapport au nombre attendu par hasard (trois sur cent vingt) ?

## Exercices

### Exercice 1.1 ⭐ — Six questions, six formes (section 1.1.1)

Pour chaque question de la gérante, nommez la **famille** de graphique et la **forme** : (a) « Quels produits se vendent le mieux ? » (b) « Les commandes montent-elles depuis un an ? » (c) « Comment se répartissent les montants de commande ? » (d) « La météo joue-t-elle sur les ventes ? » (e) « Où perd-on de l'argent entre la marge brute et le résultat ? » (f) « Combien de visiteurs perd-on entre la visite et le paiement ? »

### Exercice 1.2 ⭐ — Ranger les encodages (section 1.1.2)

(a) Classez de la plus à la moins précise : la couleur, la longueur, l'aire, la position sur une échelle commune, l'angle. (b) Calculez l'angle d'une part de 8,9 % et celui d'une part de 4,3 % (100 % = 360 degrés), puis leur rapport : le « deux fois plus » se lit-il bien sur un camembert ?

### Exercice 1.3 ⭐⭐ — Une cascade du chiffre d'affaires au résultat (section 1.1.4)

À partir du compte de résultat 2025, construisez les **étapes** d'une cascade allant du chiffre d'affaires hors taxe au résultat d'exploitation (achats, variation de stock, puis les sept charges), et vérifiez que la somme des étapes redonne le résultat.

### Exercice 1.4 ⭐ — Critiquer sans tracer (section 1.2.1)

Un collègue vous envoie un camembert en 3D à neuf parts de couleurs vives, avec une légende à droite, un fond dégradé, une ombre portée, sans titre, représentant les ventes par ville. Listez **huit défauts**, puis proposez le graphique que vous feriez.

### Exercice 1.5 ⭐⭐ — Trois titres pour un résultat (section 1.2.3)

Le retard de livraison dépasse 55 % en décembre. (a) Calculez la part de retards en décembre et hors décembre. (b) Écrivez un titre descriptif, un titre informatif, et un titre exagéré. (c) Dites pourquoi le troisième est à proscrire.

### Exercice 1.6 ⭐⭐⭐ — Échelle commune ou libre ? (section 1.2.5)

Tracez, pour les trois canaux, le chiffre d'affaires mensuel 2025 en **petits multiples** deux fois : une ligne à échelle commune, une ligne à échelle libre. Écrivez ce que chaque ligne permet de dire, et ce qu'elle cache.

### Exercice 1.7 ⭐ — Un gris qui passe, un gris qui ne passe pas (section 1.3.4)

Un collègue propose du texte en gris `#767676` sur blanc, un autre en `#777777`. Calculez le rapport de contraste de chacun. Lequel est conforme à la recommandation de 4,5 : 1 pour du texte courant ?

### Exercice 1.8 ⭐⭐ — Rouge, vert, bleu pour trois canaux (section 1.3.3)

On propose le rouge `#d62728`, le vert `#2ca02c` et le bleu `#1f77b4` pour la boutique, le site et les réseaux. Mesurez, pour les trois visions, la distance entre chaque paire de couleurs. Quelle paire est la plus exposée ? Proposez deux remèdes qui ne changent pas la palette.

### Exercice 1.9 ⭐ — Un axe coupé sur le budget (section 1.4.1)

Le chiffre d'affaires réalisé 2025 (1 325 k€) est comparé au budget (1 279 k€) sur des barres dont l'axe part de 1 250 k€. Calculez la hauteur apparente du réalisé par rapport au budget, et le rapport réel. Rédigez les deux phrases (trompeuse, honnête).

### Exercice 1.10 ⭐⭐ — La même fenêtre, un autre cycle (section 1.4.5)

On annonce : « les ventes ont progressé de 53 % en trois mois ». Pour **2023, 2024 et 2025**, calculez la variation d'octobre à décembre, et celle de juin à août. Que concluez-vous sur le choix de la fenêtre ?

### Exercice 1.11 ⭐⭐ — Taux et effectifs côte à côte (section 1.4.6)

Calculez la part de livraisons en retard pour chaque couple (transporteur, mode de livraison), avec l'effectif et la demi-largeur de l'intervalle à 95 %. Peut-on ici classer les cellules sans craindre le hasard ? Pourquoi la situation diffère-t-elle de celle des produits du livre ?

### Exercice 1.12 ⭐⭐ — Corrélation et saison (section 1.4.7)

Calculez la corrélation mensuelle entre dépense publicitaire et commandes sur les 36 mois, puis **après retrait de la moyenne de chaque mois-calendrier** (on soustrait à chaque valeur la moyenne des trois années pour le même mois). Que devient la corrélation ? Rédigez le titre honnête du nuage.

### Exercice 1.13 ⭐⭐ — Simpson trimestre par trimestre (section 1.4.9)

Comparez le chiffre d'affaires moyen par jour avec et sans promotion : globalement, puis **à trimestre égal**. Écrivez le message que la gérante doit retenir.

### Exercice 1.14 ⭐⭐⭐ — Auditer une page de tableau de bord (section 1.4)

Une page contient : (1) des barres de ventes par catégorie dont l'axe part de 90 % de la plus petite ; (2) deux courbes (publicité, commandes) à deux axes ; (3) un camembert à douze parts ; (4) un taux de retour par produit sans effectif ; (5) l'évolution « depuis septembre » du chiffre d'affaires. Pour chaque élément, remplissez : **qui est trompé, par quoi, avec quelle conséquence, quel correctif**.

## Corrigés

### Corrigé 1.1

| Question | Famille | Forme |
|---|---|---|
| (a) produits qui se vendent le mieux | comparer des quantités | barres horizontales triées (les dix premiers) |
| (b) les commandes montent-elles depuis un an | évolution dans le temps | courbe mensuelle, au moins un cycle complet |
| (c) répartition des montants | distribution | histogramme (ou boîte à moustaches par canal) |
| (d) la météo joue-t-elle ? | relation entre deux variables | nuage de points (température, ventes du jour) |
| (e) où perd-on de l'argent ? | passage d'un total à un autre | cascade |
| (f) visiteurs perdus entre visite et paiement | conversion étape par étape | barres d'entonnoir |

### Corrigé 1.2

(a) Du plus au moins précis : la **position** sur une échelle commune, la **longueur**, l'**angle**, l'**aire**, la **couleur**.

```python
parts = pd.Series({"bien-être": 8.9, "papeterie": 4.3})
ang = parts * 3.6
print(ang.round(1).to_string())
print("rapport des angles :", fr(ang["bien-être"] / ang["papeterie"], 2))
```
<!--sortie-->
```text
bien-être    32.0
papeterie    15.5
rapport des angles : 2,07
```
<!--sortie-->

(b) Le rapport est de 2,07 : « deux fois plus ». Les angles (32 et 15,5 degrés) sont **petits**, et la comparaison de deux petits angles est peu précise ; sur des barres, la longueur de l'une est visiblement le double de celle de l'autre, sans calcul.

### Corrigé 1.3

```python
cr = c["cr"]; d = cr[cr["mois"].str[:4] == "2025"].sum(numeric_only=True) / 1000        # k€
etapes = [("CA hors taxe", d["ca_ht"]), ("Achats", -d["achats"]), ("Variation de stock", d["variation_stock"])]
etapes += [(nom, -d[k]) for nom, k in (("Personnel", "frais_personnel"), ("Loyers", "loyers_charges"), ("Marketing", "marketing"), ("Livraison", "livraison"),
                                       ("Frais bancaires", "frais_bancaires"), ("Amortissements", "amortissements"), ("Autres charges", "autres_charges"))]
cumul = np.cumsum([v for _, v in etapes])
for (nom, v), cu in zip(etapes, cumul):
    print(f"{nom:20s} {v:9.0f}  cumul {cu:8.0f}")
print("résultat d'exploitation :", round(d["resultat_exploitation"]), "| somme des étapes :", round(cumul[-1]))
```
<!--sortie-->
```text
CA hors taxe              1104  cumul     1104
Achats                    -685  cumul      419
Variation de stock          -2  cumul      417
Personnel                 -141  cumul      276
Loyers                     -65  cumul      211
Marketing                  -73  cumul      138
Livraison                  -32  cumul      107
Frais bancaires            -20  cumul       87
Amortissements             -23  cumul       64
Autres charges             -24  cumul       40
résultat d'exploitation : 40 | somme des étapes : 40
```
<!--sortie-->

La somme des étapes redonne le résultat : c'est le test qu'une cascade doit toujours passer. (La variation de stock est ajoutée avec son signe : ici elle retire 2 k€. Ce qui compte pour une cascade est que les étapes **somment** exactement au résultat ; si le total diffère, un signe est faux, comme on le voit en inversant celui du stock.)

### Corrigé 1.4

Huit défauts : (1) la **3D** déforme les angles ; (2) **neuf parts** : illisible ; (3) **couleurs vives** sans sens ; (4) **légende** à droite qui oblige aux allers-retours ; (5) **fond dégradé** qui réduit le contraste ; (6) **ombre portée** qui n'apporte rien ; (7) **aucun titre**, donc aucun message ; (8) **ni valeurs ni source**. Le graphique à faire : des **barres horizontales triées** des huit premières villes plus « autres villes » en gris, valeurs en pourcentage au bout des barres, un titre du genre « Deux villes font plus d'un quart du chiffre d'affaires » (13,9 % et 12,4 %, soit 26,3 %), une source. (Voir 1.4.8.)

### Corrigé 1.5

```python
liv["dec"] = pd.to_datetime(liv["date_commande"]).dt.month == 12
t = liv.groupby("dec")["retard"].mean().mul(100)
print("hors décembre :", fr(t[False], 1), "% | décembre :", fr(t[True], 1), "%")
```
<!--sortie-->
```text
hors décembre : 21,6 % | décembre : 55,5 %
```
<!--sortie-->

(b) **Descriptif** : « Part des livraisons en retard, décembre et autres mois ». **Informatif** : « En décembre, plus d'un colis sur deux arrive en retard, contre un sur cinq le reste de l'année ». **Exagéré** : « La logistique s'effondre en fin d'année ». (c) Le troisième affirme une **cause** et une **gravité** que le graphique ne montre pas ; le deuxième dit ce que l'on mesure et laisse la gérante juger.

### Corrigé 1.6

```python
p = O.ca_mensuel(2025, "canal") / 1000
fig, axs = plt.subplots(2, 3, figsize=(10, 4.4), sharex=True)
for k, nom in enumerate(p.columns):
    for ligne, partage in enumerate((True, False)):
        a = axs[ligne, k]; a.plot(p.index, p[nom], color=O.BLEU, lw=2); a.set_title(nom + (" : échelle commune" if partage else " : échelle libre"), loc="left", fontsize=9)
        a.set_ylim(0, p.values.max() * 1.05) if partage else a.set_ylim(0, p[nom].max() * 1.1)
        a.set_xticks([1, 6, 12])
fig.suptitle("Échelle commune : le site pèse le plus ; échelle libre : chaque canal a sa saison", x=0.01, ha="left", fontweight="bold", fontsize=10)
fig.tight_layout()
style.save(fig, "ch01-c-echelles.png")
print((p.max() / p.min()).round(1).to_string())
```
<!--sortie-->
```text
figure : ch01-c-echelles.png
canal
Boutique    2.2
Réseaux     3.7
Site        2.6
```
<!--sortie-->

![Le chiffre d'affaires mensuel 2025 des trois canaux en petits multiples, en haut à échelle commune, en bas à échelle libre. Figure construite avec matplotlib (données simulées).](figures/ch01-c-echelles.png)

**Échelle commune** (ligne du haut) : on compare les **niveaux** (le site et la boutique dominent, les réseaux restent petits), mais la forme des réseaux s'aplatit. **Échelle libre** (ligne du bas) : on compare les **formes** (la même saison en fin d'année, la même baisse d'août pour le site), mais on perd le poids relatif des canaux. La sortie donne le rapport maximum/minimum de chaque canal sur l'année : ×2,2 pour la boutique, ×3,7 pour les réseaux, ×2,6 pour le site.

### Corrigé 1.7

```python
for h in ("#767676", "#777777"):
    print(h, round(O.contraste(h, "#ffffff"), 2))
```
<!--sortie-->
```text
#767676 4.54
#777777 4.48
```
<!--sortie-->

Le gris `#767676` donne **4,54 : 1**, au-dessus de 4,5 : il est conforme pour du texte courant. Le gris `#777777`, presque identique à l'œil, donne **4,48 : 1** : il passe sous le seuil. À une marche de gris près, la conclusion change : c'est pourquoi on **calcule** au lieu de juger à l'œil.

### Corrigé 1.8

```python
cols = {"rouge": "#d62728", "vert": "#2ca02c", "bleu": "#1f77b4"}
dist = lambda a, b: round(float(np.linalg.norm((np.array(a) - np.array(b)) * 255)))
for nom in ("Protanopie", "Deutéranopie", "Tritanopie"):
    sim = {k: O.simuler(v, nom) for k, v in cols.items()}
    print(f"{nom:13s}", {f"{a}-{b}": dist(sim[a], sim[b]) for a, b in itertools.combinations(sim, 2)})
print("vision typique", {f"{a}-{b}": dist(matplotlib.colors.to_rgb(cols[a]), matplotlib.colors.to_rgb(cols[b])) for a, b in itertools.combinations(cols, 2)})
```
<!--sortie-->
```text
Protanopie    {'rouge-vert': 89, 'rouge-bleu': 149, 'vert-bleu': 176}
Deutéranopie  {'rouge-vert': 30, 'rouge-bleu': 165, 'vert-bleu': 150}
Tritanopie    {'rouge-vert': 298, 'rouge-bleu': 289, 'vert-bleu': 22}
vision typique {'rouge-vert': 209, 'rouge-bleu': 244, 'vert-bleu': 143}
```
<!--sortie-->

La paire rouge-vert s'effondre en deutéranopie (30, contre 209 en vision typique) et reste faible en protanopie (89) ; en tritanopie, c'est la paire vert-bleu qui devient la plus proche (22). Deux remèdes **sans changer la palette** : (1) **étiqueter directement** les courbes ou les barres par le nom du canal ; (2) **doubler** la couleur par un **marqueur** (cercle, carré, triangle) ou un **style de trait** (plein, pointillé). On peut aussi faire varier la **luminosité** (un vert plus clair, un rouge plus foncé).

### Corrigé 1.9

```python
reel, budget = 1324.76, 1278.70                                  # k€ (voir la section 1.3.1)
print("hauteur apparente :", fr((reel - 1250) / (budget - 1250), 1), "| rapport réel :", fr(reel / budget, 3), f"(+{(reel / budget - 1) * 100:.1f} %)".replace(".", ","))
```
<!--sortie-->
```text
hauteur apparente : 2,6 | rapport réel : 1,036 (+3,6 %)
```
<!--sortie-->

**Trompeur** : « Le réalisé écrase le budget » (barre 2,6 fois plus haute). **Honnête** : « Le chiffre d'affaires dépasse le budget de 3,6 % (1 325 contre 1 279 k€) », avec un axe à zéro.

### Corrigé 1.10

```python
for an in (2023, 2024, 2025):
    m = O.ca_mensuel(an)
    print(an, "oct->déc :", fr((m[12] / m[10] - 1) * 100, 1), "% | juin->août :", fr((m[8] / m[6] - 1) * 100, 1), "%")
```
<!--sortie-->
```text
2023 oct->déc : 53,0 % | juin->août : -13,8 %
2024 oct->déc : 54,7 % | juin->août : -21,5 %
2025 oct->déc : 53,1 % | juin->août : -15,9 %
```
<!--sortie-->

La hausse d'octobre à décembre (environ 53 %) revient **chaque année**, et la baisse de juin à août aussi (de −14 % à −22 %) : ce sont des **saisons**. Annoncer l'une ou l'autre sans montrer les années précédentes suggère un événement là où il y a un calendrier. (On a vu en 1.4.5 qu'il faut un cycle complet et la comparaison au même mois de l'an dernier.)

### Corrigé 1.11

```python
t = liv.groupby(["transporteur", "mode_livraison"])["retard"].agg(["size", "mean"]).rename(columns={"size": "n", "mean": "taux"})
t["± 95 %"] = 1.96 * np.sqrt(t["taux"] * (1 - t["taux"]) / t["n"])
print((t.assign(taux=t["taux"] * 100, **{"± 95 %": t["± 95 %"] * 100}).sort_values("taux", ascending=False)).round(1).to_string())
```
<!--sortie-->
```text
                                   n  taux  ± 95 %
transporteur   mode_livraison                     
Transporteur C Point relais     1397  66.9     2.5
               Domicile         2099  42.0     2.1
               Retrait magasin   275  38.9     5.8
Transporteur B Point relais     2571  38.0     1.9
Transporteur A Point relais     3342  23.5     1.4
Transporteur B Domicile         3873  20.2     1.3
               Retrait magasin   471  17.6     3.4
Transporteur A Domicile         4765  11.4     0.9
               Retrait magasin   627  10.8     2.4
```
<!--sortie-->

Ici, les neuf cellules ont **plusieurs centaines à plusieurs milliers** de livraisons ; les demi-largeurs vont de 0,9 à 5,8 points, alors que les taux vont de 10,8 % à 66,9 % : le classement est **fiable**, sauf entre rangs voisins (38,9 % et 38,0 %, ou 11,4 % et 10,8 %), que les intervalles ne départagent pas. Pour les produits du livre, les effectifs sont de 17 à 174 lignes et les taux voisins (6,7 % en moyenne) : les écarts entre produits sont du même ordre que les intervalles. La règle est la même ; ce sont les **effectifs** et les **écarts** qui décident.

### Corrigé 1.12

```python
j2 = j.assign(mois=j["date"].dt.to_period("M"))
mo = j2.groupby("mois").agg(pub=("depense_pub", "sum"), cmd=("nb_commandes", "sum"))
mo["mn"] = mo.index.month
res = mo[["pub", "cmd"]] - mo.groupby("mn")[["pub", "cmd"]].transform("mean")        # on retire la moyenne de chaque mois-calendrier
print("corrélation brute :", fr(np.corrcoef(mo["pub"], mo["cmd"])[0, 1], 2), "| après retrait de la saison :", fr(np.corrcoef(res["pub"], res["cmd"])[0, 1], 2))
```
<!--sortie-->
```text
corrélation brute : 0,81 | après retrait de la saison : -0,11
```
<!--sortie-->

La corrélation brute (0,81) **disparaît** une fois la saison retirée (elle devient légèrement négative : le résidu est de l'ordre du bruit). Le titre honnête : « Publicité et commandes montent ensemble en fin d'année ; une fois la saison retirée, il ne reste aucune relation visible ».

### Corrigé 1.13

```python
j3 = j.assign(t=j["date"].dt.quarter)
glob = j3.groupby("promo_active")["chiffre_affaires"].mean()
trim = j3.groupby(["t", "promo_active"])["chiffre_affaires"].mean().unstack()
print("global :", glob.round(0).to_dict(), "->", fr((glob[1] / glob[0] - 1) * 100, 1), "%")
print(((trim[1] / trim[0] - 1) * 100).round(1).to_string())
```
<!--sortie-->
```text
global : {0: 3339.0, 1: 3300.0} -> -1,2 %
t
1     3.6
2     5.2
3     6.7
4    11.4
```
<!--sortie-->

Globalement la promotion paraît **faire perdre** 1,2 % ; **à trimestre égal**, elle fait gagner de 3,6 à 11,4 % de chiffre d'affaires par jour. Le message : « La comparaison globale est faussée par le calendrier (les promotions tombent hors de décembre, le meilleur mois) ; à saison égale, un jour de promotion rapporte plus. » (La question de la **marge**, que les remises dégradent, est une autre histoire, traitée au volume III.)

### Corrigé 1.14

| Élément | Qui est trompé | Par quoi | Conséquence | Correctif |
|---|---|---|---|---|
| (1) barres à axe coupé | la gérante | la longueur des barres (1.4.1) | écarts de 3 % perçus comme énormes | axe à zéro, valeurs écrites |
| (2) double axe | la direction | deux échelles choisies (1.4.4) | « la pub fait vendre » | deux graphiques ou un nuage, mention de la saison |
| (3) camembert à douze parts | le responsable de zone | angles voisins (1.4.8) | classement faux | barres triées, « autres » en gris |
| (4) taux sans effectif | la responsable des achats | petits effectifs (1.4.6) | produit retiré à tort | effectifs affichés, entonnoir |
| (5) « depuis septembre » | le financeur | choix des bornes (1.4.5) | pente saisonnière extrapolée | au moins un an, comparaison au même mois |
