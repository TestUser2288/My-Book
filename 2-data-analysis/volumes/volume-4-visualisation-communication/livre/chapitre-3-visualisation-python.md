# Chapitre 3 : Visualisation avec Python

> « Un graphique que l'on ne peut pas refaire n'est qu'une image ; un graphique que l'on peut refaire est une analyse. »

La gérante vous écrit un lundi matin : « *Peux-tu me faire le graphique des ventes par canal pour la réunion de jeudi ? En couleurs lisibles, avec les chiffres sur les barres. Et si tu peux, que je puisse cliquer dessus pour voir le détail.* » Trois demandes en une phrase : un graphique **juste**, un graphique **lisible**, un graphique **interactif**. Les chapitres 1 et 2 ont posé les principes (quel type de graphique, quelle mise en page, quel tableau de bord) ; celui-ci apprend à les **fabriquer avec du code**.

Pourquoi du code plutôt qu'un outil à cliquer ? Pour une raison que l'on a déjà rencontrée dans toute la série : la **reproductibilité**. Un graphique construit à la souris se refait à la souris, avec les mêmes oublis ; un graphique construit par un script se refait en une commande, le mois suivant, sur les nouvelles données, et l'on peut **tester** qu'il montre bien les chiffres qu'il prétend montrer. C'est aussi pour cela que, dans ce chapitre, **le code est le sujet** : les blocs restent courts, mais vous les verrez presque tous.

## Le chemin de ce chapitre

- **3.1 matplotlib et seaborn** : l'anatomie d'une figure, les graphiques de base (barres, lignes, nuages, histogrammes), les étiquettes directes, les petits multiples, le thème maison du livre, puis seaborn pour les graphiques statistiques ; la même figure en R avec ggplot2 pour comparer les syntaxes.
- **3.2 plotly et graphiques interactifs** : survol, zoom, filtre par légende ; de vraies captures de figures interactives ; quand l'interactivité aide, quand elle gêne.
- ➕ **3.3 Tableaux de bord avec Dash, Streamlit et Shiny** : le même mini-tableau de bord écrit dans trois outils libres, testé, photographié.
- ➕ **3.4 Cartes et visualisation géospatiale** : cercles proportionnels et polygones sur un plan **fictif**, normaliser par habitant, savoir quand une carte ne sert à rien.

## Les données du chapitre

Les mêmes données de la boutique que dans les volumes précédents (ventes par ligne de commande, clients, jours d'exploitation, sessions web, livraisons) et un fichier de **villes fictives** avec des coordonnées dans un plan imaginaire (`villes.csv`) : aucune carte du monde réel n'est utilisée. Toutes les données sont **simulées**.

> 🧭 **En pratique.** Les figures de ce chapitre sont produites par le code que vous lisez. Les captures d'outils interactifs (plotly, Dash, Streamlit, Shiny) sont de **vraies captures** de ces outils **libres**, lancés sur la machine qui a écrit le livre ; aucune interface d'un logiciel commercial n'est reproduite.

```python
import sys
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import style, outils_ch03 as O
style.setup()                       # le thème maison du livre (voir 3.1.6)
x = O.ventes()                      # une ligne par ligne de commande : montant, date, canal, client, catégorie
print(len(x), "lignes de commande |", x["date_commande"].min().date(), "->", x["date_commande"].max().date())
```
<!--sortie-->
```text
83905 lignes de commande | 2023-01-01 -> 2025-12-31
```
<!--sortie-->


## 3.1 matplotlib et seaborn

**matplotlib** est la bibliothèque de dessin de base de Python : presque toutes les autres (seaborn, pandas, scikit-learn) l'utilisent en coulisse. Elle est un peu verbeuse, mais elle donne le contrôle de **chaque** élément d'une figure, et c'est ce contrôle qui sépare un graphique par défaut d'un graphique qui fait passer un message.

### 3.1.1 Trois couches, et l'anatomie d'une figure

Tout graphique statistique, quel que soit l'outil, se décrit en **trois couches**. Les **données** (un tableau), les **esthétiques** (quelle colonne va sur quel attribut visuel : position horizontale, hauteur, couleur, taille) et la **géométrie** (la forme dessinée : barres, lignes, points). Un graphique à barres du chiffre d'affaires par canal : le tableau est « un canal et un chiffre d'affaires par ligne », l'esthétique est « canal en abscisse, chiffre d'affaires en hauteur, couleur selon le canal », la géométrie est « une barre par ligne ».

<!--sortie-->

![Les trois couches d'un graphique. Schéma dessiné avec matplotlib.](figures/ch03-trois-couches.png)

Cette grammaire est explicite dans ggplot2 (voir 3.1.9) ; elle est implicite dans matplotlib, où l'on **dessine** étape par étape. Il faut donc connaître le vocabulaire de ce que l'on dessine.

<!--sortie-->

![Anatomie d'une figure matplotlib. Schéma dessiné avec matplotlib.](figures/ch03-anatomie.png)

Une **Figure** est l'image entière ; elle contient un ou plusieurs **Axes**, c'est-à-dire des zones de dessin avec leur titre et leurs deux **Axis** (l'axe horizontal et l'axe vertical, avec graduations et étiquettes). Tout ce qui s'y dessine (une ligne, une barre, un texte, la légende) est un **Artist**. Presque tous les gestes de ce chapitre sont « prendre l'Axes et lui dire quoi dessiner », et la bonne habitude est l'**interface orientée objet** : on crée `fig, ax = plt.subplots()` puis l'on écrit `ax.bar(…)`, `ax.set_title(…)`. (L'interface plus ancienne `plt.bar(…)` agit sur un « Axes courant » implicite : elle suffit pour un essai, elle devient confuse dès qu'il y a deux graphiques.)

Voici le graphique demandé par la gérante, **sans aucun réglage** : le chiffre d'affaires 2025 par canal.

```python
ca = x[x["annee"] == 2025].groupby("canal")["montant"].sum() / 1000
fig, ax = plt.subplots()
ax.bar(ca.index, ca.values)
O.sauver(fig, "ch03-barres-defaut.png")
print(ca.round(1).to_dict())
```
<!--sortie-->
```text
figure : ch03-barres-defaut.png
{'Boutique': 561.0, 'Réseaux': 146.1, 'Site': 617.7}
```
<!--sortie-->

![Le graphique par défaut : correct, mais il ne dit rien.](figures/ch03-barres-defaut.png)

Ce graphique est **exact**, et c'est tout ce qu'on peut en dire : pas de titre, pas de chiffres, des barres de la même couleur dans l'ordre alphabétique, des graduations en milliers d'euros sans unité, un cadre et un quadrillage qui n'apportent rien. Le lecteur doit chercher le message ; nous allons le lui donner.

### 3.1.2 Du graphique par défaut au graphique qui dit quelque chose

On applique cinq retouches, chacune justifiée par le chapitre 1 : **ordonner** les barres (du plus grand au plus petit, sauf s'il existe un ordre naturel), **étiqueter directement** les barres plutôt que de forcer à lire l'axe, **supprimer** ce qui ne sert pas (axe vertical, quadrillage, cadre), **colorer avec intention** (une couleur par canal, la même dans tout le document), et **titrer par le message**, pas par la description.

```python
ca = x[x["annee"] == 2025].groupby("canal")["montant"].sum().sort_values(ascending=False) / 1000
fig, ax = plt.subplots(figsize=(5.6, 3.2))
barres = ax.bar(ca.index, ca.values, color=[O.COUL[c] for c in ca.index], width=0.62)
ax.bar_label(barres, labels=[f"{O.fr(v)} k€" for v in ca.values], padding=3, color=style.ENCRE)
ax.set(ylim=(0, ca.max() * 1.15), yticks=[])
ax.grid(False)
ax.spines["left"].set_visible(False)
part = ca[["Site", "Boutique"]].sum() / ca.sum() * 100
ax.set_title(f"Le Site et la Boutique font {part:.0f} % du chiffre d'affaires 2025", loc="left", fontweight="bold")
O.sauver(fig, "ch03-barres-final.png")
print({c: O.fr(v) for c, v in ca.items()}, "|", round(part, 1), "%")
```
<!--sortie-->
```text
figure : ch03-barres-final.png
{'Site': '618', 'Boutique': '561', 'Réseaux': '146'} | 89.0 %
```
<!--sortie-->

![Le même graphique après les cinq retouches : le message est dans le titre, les chiffres sur les barres.](figures/ch03-barres-final.png)

Le titre n'est pas écrit à la main : il est **calculé** (`part`). Ainsi, quand on rejoue le script sur les ventes du mois suivant, le titre reste vrai ; c'est l'avantage du code, et c'est aussi un piège (un titre automatique qui dit « fait 89 % » ne doit jamais dire une chose fausse si les données changent : on le teste, voir 3.1.8). L'axe vertical a disparu parce que chaque barre porte son chiffre ; **on ne supprime pas** un axe quand les chiffres ne sont pas écrits ailleurs.

> ⚠️ **Piège.** Les barres doivent **partir de zéro** : leur longueur représente la valeur. Raccourcir l'axe vertical (par exemple le faire commencer à 500) fait paraître trois fois plus grand un écart de 10 % ; la section 1.4 montre ce piège en détail. Pour une courbe, en revanche, on peut resserrer l'axe : on lit une position, pas une longueur.

### 3.1.3 Lignes : les séries temporelles

Pour une évolution, on passe à la **ligne**. La bonne pratique est de **supprimer la légende** et d'écrire le nom de chaque série **au bout de sa ligne** (étiquette directe) : l'œil n'a plus à faire la navette entre la courbe et une boîte de couleurs.

```python
m = x.groupby(["mois", "canal"])["montant"].sum().unstack()[O.CANAUX] / 1000
t = m.index.to_timestamp()
fig, ax = plt.subplots(figsize=(7.0, 3.4))
for canal in O.CANAUX:
    ax.plot(t, m[canal], color=O.COUL[canal])
    ax.text(t[-1] + pd.Timedelta(days=12), m[canal].iloc[-1], canal, color=O.COUL[canal], va="center", fontweight="bold")
ax.set_xlim(t[0], t[-1] + pd.Timedelta(days=95)); ax.set_ylabel("k€ par mois")
ax.xaxis.set_major_locator(mdates.MonthLocator(bymonth=[1, 7])); ax.xaxis.set_major_formatter(mdates.DateFormatter("%m/%Y"))
ax.annotate("décembre 2025 : le pic de trois ans", xy=(t[-1], m["Site"].iloc[-1]), xytext=(t[-3], 84), ha="right", arrowprops=dict(arrowstyle="->", color=style.MUET))
ax.set_title("Chiffre d'affaires mensuel par canal, 2023-2025", loc="left", fontweight="bold")
O.sauver(fig, "ch03-serie-mensuelle.png")
print("pic :", m.sum(axis=1).idxmax(), "|", O.fr(m.sum(axis=1).max()), "k€")
```
<!--sortie-->
```text
figure : ch03-serie-mensuelle.png
pic : 2025-12 | 184 k€
```
<!--sortie-->

![Chiffre d'affaires mensuel par canal : étiquettes directes, une annotation sur le fait marquant.](figures/ch03-serie-mensuelle.png)

On voit d'un coup d'œil la **saisonnalité** (un pic chaque fin d'année), la croissance du Site (de 422 à 618 k€ par an en trois ans), et le fait que le Site dépasse la Boutique en décembre 2025. L'annotation (`ax.annotate`) désigne l'unique fait sur lequel on veut attirer le regard : **une annotation par graphique suffit** ; dix annotations noient le message.

### 3.1.4 Histogrammes et nuages de points

L'**histogramme** montre la forme d'une distribution (volume I, section 1.1) ; le **nuage de points** montre la liaison entre deux variables. Les paniers de 2025 sont **asymétriques** : on les montre d'abord sur une échelle linéaire, puis sur une échelle **logarithmique**, qui étale les petites valeurs et rend la forme plus lisible.

```python
panier = x[x["annee"] == 2025].groupby("id_commande")["montant"].sum()
fig, (g, d) = plt.subplots(1, 2, figsize=(7.6, 3))
g.hist(panier, bins=np.arange(0, 700, 20), color=style.BLEU)
d.hist(panier, bins=np.logspace(np.log10(panier.min()), np.log10(panier.max()), 30), color=style.BLEU)
d.set_xscale("log")
for ax_, titre in ((g, "échelle linéaire"), (d, "échelle logarithmique")):
    ax_.axvline(panier.median(), color=style.ORANGE); ax_.set_title(titre); ax_.set_xlabel("panier (€)")
g.text(panier.median() + 10, g.get_ylim()[1] * 0.9, f"médiane {panier.median():.0f} €", color=style.ORANGE)
O.sauver(fig, "ch03-histogrammes.png")
print(len(panier), "commandes | moyenne", round(panier.mean(), 1), "| médiane", round(panier.median(), 1), "| maximum", round(panier.max()))
```
<!--sortie-->
```text
figure : ch03-histogrammes.png
12946 commandes | moyenne 102.3 | médiane 81.6 | maximum 988
```
<!--sortie-->

![Les paniers de 2025 : une queue vers la droite à gauche, une forme presque symétrique à droite, sur échelle logarithmique.](figures/ch03-histogrammes.png)

La médiane (82 €) est nettement sous la moyenne (102 €) : la distribution est étirée vers les gros paniers. Sur l'échelle logarithmique, la forme devient presque symétrique, signe que les paniers se comportent comme des **produits** de facteurs plutôt que comme des sommes. Le choix de l'échelle est une décision d'analyste, et l'on **dit** laquelle on a prise.

Le nuage de points, lui, sert à voir une relation sans la supposer. Voici la dépense publicitaire quotidienne contre le nombre de commandes, en distinguant les jours de promotion.

```python
j = O.jours(); j25 = j[j["annee"] == 2025]
fig, ax = plt.subplots(figsize=(5.6, 3.4))
for promo, couleur, nom in ((0, style.MUET, "jour ordinaire"), (1, style.ORANGE, "jour de promotion")):
    d_ = j25[j25["promo_active"] == promo]
    ax.scatter(d_["depense_pub"], d_["nb_commandes"], s=14, alpha=0.6, color=couleur, label=nom)
ax.set(xlabel="dépense publicitaire du jour (€)", ylabel="commandes du jour")
ax.legend(loc="upper left")
O.sauver(fig, "ch03-nuage.png")
print("corrélation :", round(j25["depense_pub"].corr(j25["nb_commandes"]), 2))
```
<!--sortie-->
```text
figure : ch03-nuage.png
corrélation : 0.54
```
<!--sortie-->

![Dépense publicitaire et commandes, jour par jour en 2025 : une liaison nette, qui n'est pas une cause (volume III, chapitre 2).](figures/ch03-nuage.png)

La corrélation vaut 0,54 : la dépense et les commandes montent ensemble. Un graphique **montre**, il ne **prouve** pas : nous savons (volume III, section 2.3) que la saison fait monter les deux. Une transparence (`alpha`) de 0,6 évite que les points se masquent les uns les autres quand ils sont nombreux.

### 3.1.5 Petits multiples

Quand on veut comparer plusieurs groupes, **plusieurs petits graphiques identiques** valent mieux qu'un seul graphique chargé : c'est le principe des **petits multiples**. Avec matplotlib, c'est `plt.subplots(1, 3)`, et l'argument important est `sharey=True` : tous les graphiques partagent la **même échelle verticale**, donc leurs hauteurs se comparent.

```python
fig, axes = plt.subplots(1, 3, figsize=(8, 2.7), sharey=True)
for ax, canal in zip(axes, O.CANAUX):
    ax.plot(t, m[canal], color=O.COUL[canal])
    ax.set_title(canal, loc="left", color=O.COUL[canal], fontweight="bold")
    ax.xaxis.set_major_locator(mdates.YearLocator()); ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
axes[0].set_ylabel("k€ par mois")
O.sauver(fig, "ch03-petits-multiples.png")
print("maximum mensuel (k€) :", {c: round(m[c].max()) for c in O.CANAUX})
```
<!--sortie-->
```text
figure : ch03-petits-multiples.png
maximum mensuel (k€) : {'Boutique': 81, 'Site': 90, 'Réseaux': 20}
```
<!--sortie-->

![Un petit graphique par canal, sur la même échelle verticale : le canal Réseaux est petit, et on le voit.](figures/ch03-petits-multiples.png)

Avec `sharey=True`, le canal Réseaux apparaît **petit**, ce qu'il est (un maximum de 20 k€ par mois, contre 90 pour le Site). Sans cet argument, chaque graphique serait étiré sur toute la hauteur et le canal Réseaux paraîtrait aussi important que les autres. Choisir d'**uniformiser ou non** l'échelle est un choix de sens : on uniformise pour comparer des ordres de grandeur, on libère pour comparer des **formes**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 et 3.2, exercices 3.1 à 3.4.

### 3.1.6 Le thème maison du livre

Les retouches précédentes seraient fastidieuses à répéter dans chaque script. On les range dans un **thème** : un jeu de réglages appliqué une fois (`style.setup()`), qui fixe les polices, les tailles, le fond, la grille discrète, la suppression des cadres inutiles et, surtout, une **palette** fixe. Voici l'essentiel du fichier `style.py` utilisé dans tout le livre.

```python
plt.rcParams.update({
    "axes.spines.top": False, "axes.spines.right": False,      # pas de cadre inutile
    "axes.grid": True, "grid.color": style.GRILLE,             # grille discrète
    "axes.titlesize": 11, "font.size": 10,                     # tailles lisibles
    "legend.frameon": False,
    "figure.facecolor": style.SURFACE, "savefig.dpi": 200,
})
print({n: getattr(style, n) for n in ("BLEU", "ORANGE", "AQUA", "VIOLET", "ROUGE")})
```
<!--sortie-->
```text
{'BLEU': '#2a78d6', 'ORANGE': '#eb6834', 'AQUA': '#1baf7a', 'VIOLET': '#4a3aa7', 'ROUGE': '#e34948'}
```
<!--sortie-->

Une palette est un **choix de conception** : cinq couleurs distinctes, dans un ordre fixe, et la **même couleur pour la même chose** dans tout le document (le Site est toujours orange). Il faut aussi la **mesurer** : le rapport de contraste entre une couleur et le fond (formule des règles d'accessibilité du web, qui demandent au moins 3 pour un élément graphique).

```python
def luminance(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contraste(a, b):
    la, lb = luminance(a), luminance(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

print({n: round(contraste(getattr(style, n), style.SURFACE), 1) for n in ("BLEU", "ORANGE", "AQUA", "ROUGE", "VIOLET", "GRILLE")})
```
<!--sortie-->
```text
{'BLEU': 4.3, 'ORANGE': 3.1, 'AQUA': 2.7, 'ROUGE': 3.9, 'VIOLET': 8.3, 'GRILLE': 1.3}
```
<!--sortie-->

Le bleu (4,3), l'orange (3,1) et le rouge (3,9) passent le seuil de 3 ; l'**aqua** (2,7) reste en dessous : on ne doit **jamais** s'y fier seul. Dans nos graphiques, la couleur de l'aqua est toujours doublée d'un **nom** (étiquette directe) : la couleur n'est jamais la seule information. Cette règle d'accessibilité est développée au chapitre 1 (section 1.3). La grille, volontairement, a un contraste de 1,3 : elle doit se **voir à peine**.

**Enregistrer** une figure demande de choisir le **format** et la **résolution**. Un graphique pour un document imprimé ou projeté s'enregistre en **image** (PNG) à 200 points par pouce, ou en **vectoriel** (SVG, PDF), qui reste net à toute taille et pèse peu pour un graphique simple.

```python
import os, tempfile
dossier = O.dossier_temp()
tailles = {}
for ext in ("png", "svg", "pdf"):
    chemin = os.path.join(dossier, "defaut." + ext)
    O.barres_defaut(x).savefig(chemin, dpi=200)
    tailles[ext] = os.path.getsize(chemin) // 1024
print("taille en Ko :", tailles)
O.supprimer_dossier(dossier)
```
<!--sortie-->
```text
taille en Ko : {'png': 23, 'svg': 19, 'pdf': 10}
```
<!--sortie-->

Pour ce graphique simple, le vectoriel pèse moins que l'image. Il pèse **plus** pour un nuage de 100 000 points (chaque point est un objet) : on rastérise alors (`rasterized=True`). La règle pratique : **vectoriel pour les graphiques à peu d'éléments, PNG pour les nuages denses et pour le web**. La taille de la figure (`figsize`, en pouces) doit correspondre à l'emplacement visé : une figure de 5,6 pouces de large tient dans une colonne de rapport sans être réduite, et le texte reste à la taille voulue.

### 3.1.7 seaborn : les graphiques statistiques

**seaborn** est construit sur matplotlib. Il fournit en une ligne des graphiques **statistiques** (distributions par groupe, cartes thermiques, nuages avec droite de tendance) et il s'occupe des agrégations. Il retourne des objets matplotlib : on peut ensuite les retoucher avec `ax.set_title` comme avant.

Les paniers par canal, avec une **boîte à moustaches** (médiane, quartiles, valeurs extrêmes) :

```python
p25 = x[x["annee"] == 2025].groupby(["id_commande", "canal"], as_index=False)["montant"].sum()
g = sns.catplot(data=p25, x="canal", y="montant", order=O.CANAUX, kind="box", hue="canal", palette=O.COUL, height=3.2, aspect=1.5, fliersize=2)
g.set_axis_labels("", "panier (€)")
g.figure.subplots_adjust(top=0.86)
g.figure.suptitle("Les paniers se ressemblent d'un canal à l'autre", x=0.02, ha="left", fontweight="bold")
O.sauver(g.figure, "ch03-seaborn-paniers.png")
print(p25.groupby("canal")["montant"].median().round(1).reindex(O.CANAUX).to_dict())
```
<!--sortie-->
```text
figure : ch03-seaborn-paniers.png
{'Boutique': 82.0, 'Site': 81.2, 'Réseaux': 81.2}
```
<!--sortie-->

![Distribution des paniers par canal (seaborn, boîtes à moustaches).](figures/ch03-seaborn-paniers.png)

Les trois boîtes sont presque identiques : les médianes vont de 81 à 82 €. Sans le graphique, on aurait pu croire à un panier plus élevé sur le Site ; avec lui, on voit qu'il n'y a **pas de différence** de panier entre les canaux (la différence est dans le **nombre** de commandes). La **carte thermique** (`heatmap`) montre deux variables catégorielles et une valeur : ici, le nombre moyen de commandes par jour selon le mois et le jour de la semaine.

```python
piv = j25.pivot_table(index="mois", columns="jour_semaine", values="nb_commandes", aggfunc="mean")
fig, ax = plt.subplots(figsize=(6.2, 4))
sns.heatmap(piv, annot=True, fmt=".0f", cmap=style.SEQ, cbar=False, linewidths=0.5, ax=ax)
ax.set_xticklabels(["lun", "mar", "mer", "jeu", "ven", "sam", "dim"], rotation=0); ax.set(xlabel="", ylabel="mois"); ax.grid(False)
ax.set_title("Commandes par jour en moyenne, 2025 : le samedi et décembre", loc="left", fontweight="bold")
O.sauver(fig, "ch03-seaborn-carte-thermique.png")
print("samedi de décembre :", round(piv.loc[12, 6]), "| dimanche de janvier :", round(piv.loc[1, 7]))
```
<!--sortie-->
```text
figure : ch03-seaborn-carte-thermique.png
samedi de décembre : 85 | dimanche de janvier : 20
```
<!--sortie-->

![Commandes moyennes par jour selon le mois et le jour de la semaine (carte thermique).](figures/ch03-seaborn-carte-thermique.png)

Le samedi de décembre compte 85 commandes en moyenne, le dimanche de janvier 20 : un rapport de plus de quatre. Une carte thermique est un bon outil pour les **motifs croisés** (saison × semaine), à condition de **noter les valeurs** dans les cases (`annot=True`) et d'utiliser une échelle de couleur **séquentielle** (du clair au foncé), pas un arc-en-ciel.

Reste une subtilité sur laquelle seaborn est discret : ses graphiques **ajoutent des intervalles de confiance par défaut** (une bande autour d'une courbe ou une barre d'erreur sur une barre). Cet intervalle décrit l'incertitude sur la **moyenne**, calculée par rééchantillonnage des observations ; il **suppose** que les observations sont **indépendantes**, et il ne décrit pas la **dispersion** des valeurs.

```python
dec = j[j["mois"] == 12]["nb_commandes"]
se = dec.std() / np.sqrt(len(dec))
print("décembre :", len(dec), "jours | moyenne", round(dec.mean(), 1), "| écart-type des jours", round(dec.std(), 1), "| erreur type de la moyenne", round(se, 2))
print("intervalle de confiance de la moyenne : %.1f à %.1f | jours observés : %d à %d" % (dec.mean() - 1.96 * se, dec.mean() + 1.96 * se, dec.min(), dec.max()))
```
<!--sortie-->
```text
décembre : 93 jours | moyenne 55.9 | écart-type des jours 13.9 | erreur type de la moyenne 1.44
intervalle de confiance de la moyenne : 53.1 à 58.8 | jours observés : 31 à 97
```
<!--sortie-->

La moyenne de décembre est connue à environ **±3 commandes** près (de 53 à 59), alors que les jours individuels vont de 31 à 97. Un lecteur qui prend la bande pour la **plage de variation des jours** se trompe d'un facteur dix environ. Quand le graphique doit montrer la variabilité, on montre les **jours** (boîte à moustaches, nuage) ; quand il doit montrer la précision d'une moyenne, on montre l'intervalle **et on le dit dans la légende**.

### 3.1.8 Reproductibilité : une figure est une fonction

Un script de graphique devient fiable quand on l'enferme dans une **fonction qui reçoit les données et retourne la figure**, sans lire de fichier ni modifier d'état global. On peut alors la rejouer sur d'autres données et la **tester**.

```python
def figure_ventes_canal(donnees, annee):
    ca = donnees[donnees["annee"] == annee].groupby("canal")["montant"].sum().sort_values(ascending=False) / 1000
    fig, ax = plt.subplots(figsize=(5.6, 3.2))
    barres = ax.bar(ca.index, ca.values, color=[O.COUL[c] for c in ca.index], width=0.62)
    ax.bar_label(barres, labels=[f"{O.fr(v)} k€" for v in ca.values], padding=3)
    ax.set(ylim=(0, ca.max() * 1.15), yticks=[]); ax.grid(False)
    return fig

for annee in (2024, 2025):
    fig = figure_ventes_canal(x, annee)
    hauteurs = [b.get_height() for b in fig.axes[0].patches]
    attendu = x[x["annee"] == annee].groupby("canal")["montant"].sum().sort_values(ascending=False) / 1000
    print(annee, "| hauteurs des barres :", [round(float(h), 1) for h in hauteurs], "| égales au tableau :", np.allclose(hauteurs, attendu.values))
    plt.close(fig)
```
<!--sortie-->
```text
2024 | hauteurs des barres : [558.1, 502.5, 128.8] | égales au tableau : True
2025 | hauteurs des barres : [617.7, 561.0, 146.1] | égales au tableau : True
```
<!--sortie-->

On ne teste pas les **pixels** (ils changent d'une version à l'autre) mais les **données dessinées** : les hauteurs des barres, les valeurs des lignes (`ax.lines[0].get_ydata()`), le texte du titre. Ce test attrape l'erreur la plus grave d'un graphique, celle qui ne se voit pas : une barre qui montre un autre chiffre que celui du tableau. Deux autres règles de reproductibilité : **fixer les graines** quand le graphique contient de l'aléatoire (un nuage décalé aléatoirement pour ne pas empiler les points, `rng = np.random.default_rng(0)`) et **enregistrer la figure par le script**, jamais par une capture d'écran.

> ✅ **À retenir.** Une figure matplotlib est une `Figure` qui contient des `Axes` ; on la construit en cinq retouches (ordre, étiquettes directes, suppression du superflu, couleur avec intention, titre qui dit le message), on range les réglages dans un thème, et l'on enferme chaque graphique dans une fonction que l'on peut tester.

### 3.1.9 La même figure en R avec ggplot2

R et ggplot2 expriment les trois couches de 3.1.1 **explicitement**. Voici le même graphique : les données (`ca`), les esthétiques (`aes`), la géométrie (`geom_col`), puis les retouches. La figure enregistrée est celle du R, pas celle du Python.

```r
library(ggplot2); library(dplyr, warn.conflicts = FALSE)
dossier <- Sys.getenv("DONNEES")
l <- read.csv(file.path(dossier, "lignes_commande.csv")); cm <- read.csv(file.path(dossier, "commandes.csv"))
ca <- inner_join(l, cm, by = "id_commande") |> filter(substr(date_commande, 1, 4) == "2025") |>
  group_by(canal) |> summarise(ca = sum(montant) / 1000)
p <- ggplot(ca, aes(reorder(canal, -ca), ca, fill = canal)) + geom_col(width = 0.62) +
  geom_text(aes(label = paste(format(round(ca), big.mark = " "), "k€")), vjust = -0.5) +
  scale_fill_manual(values = c(Boutique = "#2a78d6", Site = "#eb6834", Réseaux = "#1baf7a")) +
  scale_y_continuous(expand = expansion(mult = c(0, 0.12))) +
  labs(x = NULL, y = NULL, title = "Le Site et la Boutique font 89 % du chiffre d'affaires 2025") +
  theme_minimal() + theme(legend.position = "none", axis.text.y = element_blank(), panel.grid = element_blank(),
                          plot.title = element_text(face = "bold", size = 10), plot.title.position = "plot")
ggsave(file.path(dirname(dossier), "figures", "ch03-ggplot-barres.png"), p, width = 6.2, height = 3.2, dpi = 200)
print(as.data.frame(ca |> mutate(ca = round(ca, 1))))
```
<!--sortie-->
```text
     canal    ca
1 Boutique 561.0
2  Réseaux 146.1
3     Site 617.7
```
<!--sortie-->

![Le même graphique avec ggplot2 : mêmes données, mêmes couleurs, syntaxe en couches.](figures/ch03-ggplot-barres.png)

Les deux figures disent la même chose. La différence est dans la **manière de penser** : ggplot2 **décrit** le graphique (on additionne des couches avec `+`), matplotlib le **dessine** (on donne des ordres à un Axes). Le tableau suivant met en regard les gestes équivalents.

| Geste | matplotlib / seaborn | ggplot2 |
|---|---|---|
| Barres | `ax.bar(x, y)` | `geom_col()` |
| Nuage de points | `ax.scatter(x, y)` | `geom_point()` |
| Courbe | `ax.plot(x, y)` | `geom_line()` |
| Histogramme | `ax.hist(v, bins=…)` | `geom_histogram(bins = …)` |
| Couleur selon une colonne | `color=[…]`, `hue=` (seaborn) | `aes(fill = canal)` |
| Petits multiples | `plt.subplots(1, 3)` ; `sns.relplot(col=…)` | `facet_wrap(~ canal)` |
| Titre, étiquettes | `ax.set_title`, `ax.set(xlabel=…)` | `labs(title = …, x = …)` |
| Thème | `plt.rcParams`, `style.setup()` | `theme_minimal()`, `theme(…)` |
| Enregistrer | `fig.savefig(…, dpi=…)` | `ggsave(…, dpi = …)` |

### 3.1.10 ➕ Les autres bibliothèques de graphiques

matplotlib et seaborn ne sont pas les seules options, et il est utile d'en connaître d'autres, ne serait-ce que pour reconnaître leur code. Nous ne les exécutons pas ici (elles ne font pas partie de l'environnement du livre) ; leurs fonctionnalités sont à **vérifier dans la documentation de votre version**.

- **plotnine** reprend la grammaire des graphiques de ggplot2 en Python : on écrit `ggplot(donnees, aes(...)) + geom_col()`, comme en 3.1.9. C'est le choix naturel pour qui vient de R.
- **Altair** est **déclaratif** : on décrit le lien entre colonnes et attributs visuels, et la bibliothèque produit une spécification (au format JSON, de la famille Vega-Lite) que le navigateur dessine. Les graphiques sont interactifs par construction, et la spécification est un texte que l'on peut versionner.
- **Bokeh** produit, comme plotly, des pages web interactives, avec un accent sur les grands volumes de données et sur les applications serveur.

Le choix se règle sur trois questions : **le support** (image fixe ou page web), **l'équipe** (quelle syntaxe connaît-elle ?) et **le contrôle** dont on a besoin (matplotlib reste le plus fin). Quelle que soit la bibliothèque, les règles des chapitres 1 et 2 ne changent pas : un outil ne choisit ni le message, ni le bon type de graphique.

> ⚠️ **Piège : les figures s'accumulent.** matplotlib garde en mémoire chaque figure ouverte jusqu'à ce qu'on la ferme (`plt.close(fig)`). Un script qui en produit des centaines (un graphique par client, par exemple) sans les fermer finit par saturer la mémoire et par déclencher un avertissement. Les fonctions de ce chapitre qui enregistrent une figure la ferment ensuite ; prenez la même habitude.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.3 à 3.5, exercices 3.5 à 3.9.

<!--sortie-->


## 3.2 plotly et graphiques interactifs

Un graphique **interactif** réagit à la souris : une infobulle apparaît au survol, on peut zoomer, masquer une série en cliquant sur sa légende. Pour la gérante qui voulait « cliquer pour voir le détail », c'est la réponse naturelle, et **plotly** est la bibliothèque libre la plus répandue pour cela. Ses figures sont des pages web : elles s'ouvrent dans un navigateur, s'insèrent dans un tableau de bord (section 3.3) et s'envoient en pièce jointe. Dans ce livre papier, on ne peut pas cliquer : les figures de cette section sont donc de **vraies captures** (navigateur sans interface) de pages plotly **réelles**, avec le geste simulé (survol, clic) indiqué dans la légende.

### 3.2.1 Deux niveaux : plotly express et graph_objects

plotly s'utilise à deux niveaux. **plotly express** (`px`) fabrique une figure complète en une ligne à partir d'un tableau, un peu comme seaborn. **graph_objects** (`go`) construit la figure pièce par pièce, comme matplotlib, et permet tout régler. On commence par `px`, on descend à `go` quand il faut une personnalisation précise.

```python
import os
import plotly.express as px
import plotly.graph_objects as go
ca = x[x["annee"] == 2025].groupby("canal", as_index=False)["montant"].sum().sort_values("montant", ascending=False)
f1 = px.bar(ca, x="canal", y="montant", color="canal", color_discrete_map=O.COUL)
f2 = go.Figure(go.Bar(x=ca["canal"], y=ca["montant"], marker_color=[O.COUL[c] for c in ca["canal"]]))
print(type(f1).__name__, "|", len(f1.data), "série(s) pour px,", len(f2.data), "pour go |", sorted(f2.to_dict()))
print("mêmes hauteurs :", sorted(float(v) for s in f1.data for v in s.y) == sorted(float(v) for v in f2.data[0].y))
```
<!--sortie-->
```text
Figure | 3 série(s) pour px, 1 pour go | ['data', 'layout']
mêmes hauteurs : True
```
<!--sortie-->

Une figure plotly est une simple **structure de données** : des séries (`data`) et une mise en page (`layout`), que l'on peut afficher, modifier ou convertir en texte JSON. C'est ce qui permet à la page web de la redessiner à chaque geste. Notez que `px` crée **une série par valeur de la colonne de couleur** (ici trois séries d'une barre), alors que notre figure `go` n'a qu'une série de trois barres : le résultat visible est le même, la structure interne ne l'est pas.

### 3.2.2 Survol, zoom, légende : l'interactivité en trois gestes

Voici le graphique des ventes par canal, rendu interactif et habillé d'un **gabarit sobre** (`simple_white`). Le point important est le texte de l'infobulle (`hovertemplate`) : il dit **exactement** ce que l'on veut lire, avec son unité, au lieu du texte technique par défaut.

```python
dossier = O.dossier_temp()
fig = px.bar(ca, x="canal", y="montant", color="canal", color_discrete_map=O.COUL, template="simple_white")
fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:,.0f} € en 2025<extra></extra>")
fig.update_layout(separators=", ", showlegend=False, xaxis_title=None, yaxis_title="€", title="Chiffre d'affaires 2025 par canal : survolez une barre")
barres = os.path.join(dossier, "barres.html")
fig.write_html(barres, include_plotlyjs=True)
print("page HTML autonome :", round(os.path.getsize(barres) / 1e6, 1), "Mo")
O.capturer_html(barres, os.path.join(O.FIG, "ch03-plotly-barres.png"), 900, 460, survol=".bars .point >> nth=1")
```
<!--sortie-->
```text
page HTML autonome : 4.8 Mo
capture existante : ch03-plotly-barres.png
```
<!--sortie-->

![Capture réelle d'une figure plotly : le survol de la barre du Site affiche une infobulle ; la barre d'outils (appareil photo, zoom, déplacement, sélection, réinitialisation) est en haut à droite.](figures/ch03-plotly-barres.png)

Le fichier HTML pèse plusieurs mégaoctets parce qu'il **embarque la bibliothèque** (`include_plotlyjs=True`) : il fonctionne **hors ligne**, ce qui est ce qu'on veut pour un envoi par courriel ; avec `include_plotlyjs="cdn"`, il ne fait que quelques dizaines de kilo-octets mais exige une connexion pour charger la bibliothèque. Pour une série temporelle, deux réglages changent tout : le **mode de survol unifié** (`hovermode="x unified"`), qui affiche toutes les séries d'un même mois dans une seule infobulle, et le **curseur de plage** (`rangeslider`), qui permet de zoomer sur une période.

```python
mois = x.groupby([x["mois"].dt.to_timestamp().rename("mois"), "canal"], as_index=False)["montant"].sum()
fig = px.line(mois, x="mois", y="montant", color="canal", color_discrete_map=O.COUL, template="simple_white")
fig.update_traces(hovertemplate="%{y:,.0f} €")
fig.update_xaxes(rangeslider_visible=True, tickformat="%m/%Y")
fig.update_layout(separators=", ", hovermode="x unified", yaxis_title="€ par mois", xaxis_title=None, legend_title=None, title="Chiffre d'affaires mensuel par canal")
serie = os.path.join(dossier, "serie.html")
fig.write_html(serie, include_plotlyjs=True)
O.capturer_html(serie, os.path.join(O.FIG, "ch03-plotly-survol.png"), 1000, 520, survol=(0.78, 0.3))
print("séries :", [t.name for t in fig.data])
```
<!--sortie-->
```text
capture existante : ch03-plotly-survol.png
séries : ['Boutique', 'Réseaux', 'Site']
```
<!--sortie-->

![Capture réelle : survol unifié d'un mois (les trois canaux dans une infobulle) et curseur de plage sous le graphique.](figures/ch03-plotly-survol.png)

Les deux autres gestes se simulent de même : un **clic sur un nom de la légende** masque la série correspondante (ici on retire le Site pour regarder de près la Boutique et les Réseaux), et un **glissé** sur le graphique sélectionne une zone à agrandir.

```python
O.capturer_html(serie, os.path.join(O.FIG, "ch03-plotly-zoom.png"), 1000, 520,
                clic=['.legend .traces:has-text("Site")'], glisser=[(0.62, 0.5, 0.9, 0.5)])
print("captures de la section :", sorted(f for f in os.listdir(O.FIG) if f.startswith("ch03-plotly")))
```
<!--sortie-->
```text
capture existante : ch03-plotly-zoom.png
captures de la section : ['ch03-plotly-barres.png', 'ch03-plotly-survol.png', 'ch03-plotly-zoom.png']
```
<!--sortie-->

![Capture réelle : légende cliquée (série masquée) et zone agrandie par glissé.](figures/ch03-plotly-zoom.png)

### 3.2.3 Quand l'interactivité aide, et quand elle gêne

L'interactivité **aide** quand le lecteur doit **explorer** : beaucoup de points ou de séries, des détails à la demande (le montant exact d'un mois), des filtres qu'il choisit lui-même. Elle sert bien un tableau de bord consulté chaque semaine (chapitre 2). Elle **gêne** dans quatre cas.

1. **Le support est fixe.** Un rapport imprimé, un PDF, une diapositive : le survol n'existe pas. Une figure destinée à ces supports doit **se suffire à elle-même** : étiquettes directes, annotation du fait marquant, titre qui dit le message, comme en 3.1.
2. **Le message ne doit pas se chercher.** Si le fait important n'apparaît qu'au survol, la plupart des lecteurs ne le verront pas. L'information essentielle est **visible sans geste** ; l'interactivité n'apporte que le **détail**.
3. **L'accessibilité.** Une infobulle ne s'obtient pas au clavier, ni avec un lecteur d'écran, ni sur un téléphone sans souris sans geste précis. On double l'interactivité d'un **tableau** ou d'un **texte alternatif** qui donne le message.
4. **La reproductibilité.** Une page interactive est difficile à archiver et à citer ; on **garde une image** de ce qui a été montré à la réunion.

> ⚠️ **Piège.** Une figure interactive **séduit** : elle donne l'impression d'une analyse approfondie. Mais l'ajout de survol et de zoom n'améliore ni la question, ni la justesse du chiffre. Un bon graphique statique vaut mieux qu'un mauvais graphique interactif.

### 3.2.4 plotly ou matplotlib ?

Le choix ne tient pas à la qualité mais à l'**usage**. Le tableau résume ce que nous avons vu.

| | matplotlib / seaborn | plotly |
|---|---|---|
| Sortie principale | image fixe (PNG, SVG, PDF) | page web interactive (HTML) |
| Rapport imprimé, PDF, diapositive | **oui** | non (il faut une capture) |
| Exploration, tableau de bord | possible, peu confortable | **oui** |
| Contrôle des détails | **très fin** | bon, via `update_layout` |
| Taille du fichier | quelques dizaines de Ko | plusieurs Mo (bibliothèque embarquée) |
| Accessibilité clavier, lecteur d'écran | image + texte alternatif | à soigner (tableau associé) |
| Reproductibilité d'une réunion | **très bonne** (une image) | plus fragile (page à archiver) |

Une pratique courante : **explorer** avec plotly, **livrer** une image matplotlib ou une capture. Dans les deux cas, la discipline est la même : un titre qui dit le message, des unités, des couleurs avec intention, une annotation unique.

> ✅ **À retenir.** plotly produit des pages web interactives (survol, zoom, filtre par légende) à partir d'une structure de données ; on l'emploie pour **explorer** et pour les **tableaux de bord**, jamais comme seul support d'un message : l'information essentielle doit rester visible **sans geste**, et une image doit en rester la trace.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.6, exercices 3.10 à 3.12.


## 3.3 ➕ Pour aller plus loin : tableaux de bord avec Dash, Streamlit et Shiny

Les outils de tableau de bord à interface graphique (chapitre 2) ne conviennent pas toujours : on peut vouloir un tableau de bord **versionné**, **testé**, branché sur n'importe quelle source, déployable sans licence. Trois outils **libres** répondent à ce besoin en quelques dizaines de lignes de code : **Dash** (Python, par les auteurs de plotly), **Streamlit** (Python) et **Shiny** (R, et depuis peu Python). Cette section écrit le **même** mini-tableau de bord dans les trois, le **teste** sans navigateur, puis le **photographie** pour de vrai.

### 3.3.1 Le cahier des charges commun

La gérante demande : « *un écran avec le chiffre d'affaires et le nombre de commandes, la répartition par catégorie, l'évolution par mois, et deux réglages : les canaux à inclure et l'année.* » Soit deux **entrées** (canaux, année), un **calcul** commun (filtrer les ventes) et trois **sorties** (deux chiffres, un diagramme en barres, une courbe). Les trois outils différent par la façon dont ils relient les entrées aux sorties : c'est leur **modèle d'exécution**.

| Outil | Modèle d'exécution | Ce que fait l'outil à chaque changement d'une entrée |
|---|---|---|
| **Streamlit** | le script se **rejoue** de haut en bas | relance tout le script (les données chargées sont gardées en cache) |
| **Dash** | des **fonctions de rappel** (callbacks) déclarées | appelle la fonction reliée à l'entrée modifiée, avec ses entrées et sorties déclarées |
| **Shiny** | un **graphe réactif** | recalcule seulement les expressions qui dépendent de l'entrée modifiée |

Les trois applications ci-dessous sont **écrites dans ce livre** : le code que vous lisez est extrait par le script de construction du chapitre, enregistré dans un dossier temporaire, puis **testé et lancé**. Il n'y a donc pas de copie de l'application qui pourrait diverger du texte.

### 3.3.2 Streamlit : un script qui se rejoue

```python
# app_streamlit.py (1/2)
import os, pandas as pd, plotly.express as px, streamlit as st
@st.cache_data
def charger():
    d = os.environ["DONNEES"]
    c = pd.read_csv(f"{d}/commandes.csv", parse_dates=["date_commande"])
    p = pd.read_csv(f"{d}/produits.csv")[["id_produit", "categorie"]]
    l = pd.read_csv(f"{d}/lignes_commande.csv").merge(p, on="id_produit")
    return l.merge(c[["id_commande", "date_commande", "canal"]], on="id_commande")
ventes = charger()
st.title("Ventes de la boutique")
```

```python
# app_streamlit.py (2/2)
tous = sorted(ventes["canal"].unique())
canaux = st.sidebar.multiselect("Canaux", tous, default=tous)
annee = st.sidebar.slider("Année", 2023, 2025, 2025)
v = ventes[ventes["canal"].isin(canaux) & (ventes["date_commande"].dt.year == annee)]
st.metric("Chiffre d'affaires (€)", f"{v['montant'].sum():,.0f}".replace(",", " "))
st.metric("Commandes", v["id_commande"].nunique())
st.plotly_chart(px.bar(v.groupby("categorie", as_index=False)["montant"].sum(), x="categorie", y="montant"))
mois = v.groupby(v["date_commande"].dt.to_period("M").astype(str), as_index=False)["montant"].sum()
st.plotly_chart(px.line(mois, x="date_commande", y="montant"))
```

Le script se lit comme une page : un titre, des réglages dans la barre latérale, des chiffres, deux graphiques. Les données sont chargées **une fois** (`@st.cache_data`), sinon elles seraient relues à chaque clic. **Tester** une application Streamlit sans navigateur est possible : `AppTest` exécute le script, permet de **manipuler les widgets** et de **lire les éléments produits**.

```python
import os, sys
from streamlit.testing.v1 import AppTest
apps = O.dossier_apps()
print("applications extraites du livre :", O.extraire_apps("sections/03-3-dash-streamlit-shiny.md", apps))
at = AppTest.from_file(os.path.join(apps, "app_streamlit.py"), default_timeout=120).run()
ca25 = x[x["annee"] == 2025]["montant"].sum()
print("2025 :", [m.value for m in at.metric], "| attendu :", O.fr(ca25), x[x["annee"] == 2025]["id_commande"].nunique())
at.sidebar.multiselect[0].unselect("Réseaux").run()
at.sidebar.slider[0].set_value(2024).run()
ca24 = x[(x["annee"] == 2024) & (x["canal"] != "Réseaux")]
print("2024 hors Réseaux :", [m.value for m in at.metric], "| attendu :", O.fr(ca24["montant"].sum()), ca24["id_commande"].nunique(), "| exceptions :", len(at.exception))
```
<!--sortie-->
```text
applications extraites du livre : ['app_dash.py', 'app_shiny.R', 'app_streamlit.py']
2025 : ['1 324 764', '12946'] | attendu : 1 324 764 12946
2024 hors Réseaux : ['1 060 674', '10730'] | attendu : 1 060 674 10730 | exceptions : 0
```
<!--sortie-->

On vérifie ce qui compte : **les chiffres affichés sont ceux du tableau pandas**, après avoir retiré un canal et changé d'année. Le test ne voit pas l'aspect de la page (couleurs, alignement) : il valide le **calcul**, pas le **rendu**. C'est exactement la division du travail qu'on souhaite : la machine vérifie les chiffres, l'œil vérifie la page.

### 3.3.3 Dash : des fonctions de rappel

```python
# app_dash.py (1/2)
import os, pandas as pd, plotly.express as px
from dash import Dash, dcc, html, Input, Output
d = os.environ["DONNEES"]
c = pd.read_csv(f"{d}/commandes.csv", parse_dates=["date_commande"])
p = pd.read_csv(f"{d}/produits.csv")[["id_produit", "categorie"]]
v = pd.read_csv(f"{d}/lignes_commande.csv").merge(p, on="id_produit").merge(c[["id_commande", "date_commande", "canal"]], on="id_commande")
CANAUX = sorted(v["canal"].unique())
app = Dash(__name__)
app.layout = html.Div([html.H3("Ventes de la boutique"), dcc.Checklist(id="canaux", options=CANAUX, value=CANAUX, inline=True),
    dcc.Slider(2023, 2025, 1, value=2025, id="annee", marks={a: str(a) for a in (2023, 2024, 2025)}), html.Div(id="kpi"),
    dcc.Graph(id="cat", style={"height": "230px"}), dcc.Graph(id="serie", style={"height": "230px"})], style={"width": "760px", "margin": "auto"})
```

```python
# app_dash.py (2/2)
@app.callback(Output("kpi", "children"), Output("cat", "figure"), Output("serie", "figure"), Input("canaux", "value"), Input("annee", "value"))
def maj(canaux, annee):
    s = v[v["canal"].isin(canaux) & (v["date_commande"].dt.year == annee)]
    kpi = f"Chiffre d'affaires : {s['montant'].sum():,.0f} € | commandes : {s['id_commande'].nunique()}".replace(",", " ")
    cat = px.bar(s.groupby("categorie", as_index=False)["montant"].sum(), x="categorie", y="montant")
    mois = s.groupby(s["date_commande"].dt.to_period("M").astype(str), as_index=False)["montant"].sum()
    return kpi, cat, px.line(mois, x="date_commande", y="montant")
if __name__ == "__main__":
    app.run(port=int(os.environ.get("PORT", 8050)))
```

Dash sépare nettement la **mise en page** (`app.layout`, une arborescence de composants) du **comportement** (la fonction `maj`, reliée par `Input` et `Output`). Chaque composant a un identifiant ; le décorateur déclare « quand `canaux` ou `annee` change, appelle `maj` et mets le résultat dans `kpi`, `cat` et `serie` ». C'est plus verbeux que Streamlit, mais le **graphe des dépendances est explicite**, ce qui aide pour les grosses applications. Le test le plus simple appelle la **fonction de rappel directement**, sans serveur.

```python
import importlib.util
os.environ["PORT"] = "0"
spec = importlib.util.spec_from_file_location("app_dash", os.path.join(apps, "app_dash.py"))
mod = importlib.util.module_from_spec(spec); spec.loader.exec_module(mod)
kpi, fig_cat, fig_serie = mod.maj(["Boutique", "Site"], 2025)
ca = x[(x["annee"] == 2025) & (x["canal"] != "Réseaux")]
print(kpi, "| attendu :", O.fr(ca["montant"].sum()), ca["id_commande"].nunique())
print("catégories dans le graphique :", sorted(fig_cat.data[0].x), "| mois :", len(fig_serie.data[0].x))
```
<!--sortie-->
```text
Chiffre d'affaires : 1 178 689 € | commandes : 11520 | attendu : 1 178 689 11520
catégories dans le graphique : ['Bien-être', 'Cuisine', 'Décoration', 'Jardin', 'Maison', 'Papeterie'] | mois : 12
```
<!--sortie-->

### 3.3.4 Shiny : un graphe réactif

```r
# app_shiny.R (1/2)
library(shiny); library(dplyr, warn.conflicts = FALSE); library(ggplot2)
d <- Sys.getenv("DONNEES")
v <- inner_join(read.csv(file.path(d, "lignes_commande.csv")), read.csv(file.path(d, "commandes.csv")), by = "id_commande") |>
  inner_join(read.csv(file.path(d, "produits.csv"))[, c("id_produit", "categorie")], by = "id_produit") |>
  mutate(annee = as.integer(substr(date_commande, 1, 4)), mois = substr(date_commande, 1, 7))
ui <- fluidPage(titlePanel("Ventes de la boutique"), sidebarLayout(
  sidebarPanel(checkboxGroupInput("canaux", "Canaux", sort(unique(v$canal)), selected = sort(unique(v$canal))),
               sliderInput("annee", "Année", 2023, 2025, 2025, sep = "")),
  mainPanel(textOutput("kpi"), plotOutput("cat", height = 220), plotOutput("serie", height = 220))))
```

```r
# app_shiny.R (2/2)
server <- function(input, output, session) {
  sel <- reactive(filter(v, canal %in% input$canaux, annee == input$annee))
  output$kpi <- renderText(paste0("Chiffre d'affaires : ", format(round(sum(sel()$montant)), big.mark = " "), " € | commandes : ", n_distinct(sel()$id_commande)))
  output$cat <- renderPlot(sel() |> group_by(categorie) |> summarise(ca = sum(montant)) |>
    ggplot(aes(reorder(categorie, -ca), ca)) + geom_col(fill = "#2a78d6") + scale_y_continuous(labels = scales::label_number(big.mark = " ")) + labs(x = NULL, y = "€") + theme_minimal())
  output$serie <- renderPlot(sel() |> group_by(mois) |> summarise(ca = sum(montant)) |>
    ggplot(aes(mois, ca, group = 1)) + geom_line(color = "#eb6834") + labs(x = NULL, y = "€") + theme_minimal())
}
shinyApp(ui, server)
```

Le cœur de Shiny est `reactive` : l'expression `sel()` n'est calculée que **si l'une de ses entrées a changé**, et les trois sorties la **réutilisent** (le filtrage n'est fait qu'une fois, pas trois). C'est ce que Streamlit obtient avec le cache et Dash en le recalculant dans la fonction de rappel. `testServer` exécute le serveur **sans navigateur**.

```r
library(shiny)
app <- shinyAppFile(file.path(Sys.getenv("TMPDIR"), "ch03-apps", "app_shiny.R"))
testServer(app, {
  session$setInputs(canaux = c("Boutique", "Site"), annee = 2025)
  cat("kpi :", output$kpi, "\n")
  session$setInputs(annee = 2024)
  cat("kpi :", output$kpi, "\n")
})
```
<!--sortie-->
```text
kpi : Chiffre d'affaires : 1 178 689 € | commandes : 11520 
kpi : Chiffre d'affaires : 1 060 674 € | commandes : 10730 
```
<!--sortie-->

Les trois outils donnent, pour les mêmes réglages, le **même chiffre** : c'est la preuve que les trois applications calculent la même chose (la comparaison à pandas dans les deux premiers tests, la lecture du KPI dans le troisième).

### 3.3.5 Les trois applications, photographiées

On lance chaque application dans un sous-processus local sur un port libre, on la photographie avec un navigateur sans interface, puis on **arrête** le processus : aucune application ne reste active. Ce sont de vraies captures de ces outils libres.

```python
env = {"DONNEES": os.environ["DONNEES"], "PORT": "{port}"}
fig_ = lambda nom: os.path.join(O.FIG, nom)
O.photographier_appli([sys.executable, "-m", "streamlit", "run", os.path.join(apps, "app_streamlit.py"), "--server.headless", "true", "--server.address", "127.0.0.1",
                       "--server.port", "{port}", "--browser.gatherUsageStats", "false"], fig_("ch03-app-streamlit.png"), "Chiffre d'affaires", env=env, hauteur=1450)
O.photographier_appli([sys.executable, os.path.join(apps, "app_dash.py")], fig_("ch03-app-dash.png"), "Chiffre d'affaires", env=env, hauteur=560)
O.photographier_appli(["Rscript", "-e", "shiny::runApp(file.path(Sys.getenv('TMPDIR'), 'ch03-apps', 'app_shiny.R'), port = {port}, launch.browser = FALSE)"],
                      fig_("ch03-app-shiny.png"), "Chiffre d'affaires", env=env, hauteur=520)
print(sorted(f for f in os.listdir(O.FIG) if f.startswith("ch03-app-")))
```
<!--sortie-->
```text
capture existante : ch03-app-streamlit.png
capture existante : ch03-app-dash.png
capture existante : ch03-app-shiny.png
['ch03-app-dash.png', 'ch03-app-shiny.png', 'ch03-app-streamlit.png']
```
<!--sortie-->

![Capture réelle de l'application Streamlit : réglages à gauche, deux chiffres, deux graphiques.](figures/ch03-app-streamlit.png)

![Capture réelle de l'application Dash : le même contenu, la mise en page est celle que l'on a écrite.](figures/ch03-app-dash.png)

![Capture réelle de l'application Shiny (R) : mêmes réglages, mêmes chiffres.](figures/ch03-app-shiny.png)

Le **style par défaut** diffère (Streamlit soigne l'apparence sans effort, Dash et Shiny demandent un peu de mise en forme), mais **le contenu est le même**. On voit aussi la limite d'un tableau de bord produit en peu de lignes : pas de titres qui disent un message, pas de hiérarchie visuelle ; la section 2.3 (conception d'un tableau de bord) explique ce que l'on ajouterait avant de le livrer.

### 3.3.6 Déploiement, secrets, et choix de l'outil

Mettre ces applications à disposition d'autres personnes soulève des questions que le notebook ne posait pas. **Où tourne-t-elle ?** Sur un serveur (une machine de l'entreprise, un service d'hébergement), dont il faut assurer la disponibilité. **Qui a le droit de la voir ?** Une authentification, ou un accès restreint au réseau interne. **Où sont les secrets ?** Mot de passe de la base, clés d'API : **jamais dans le code** ni dans le dépôt, mais dans des **variables d'environnement** ou un gestionnaire de secrets (ici, le seul réglage externe est le dossier des données, `DONNEES`). **Qui la maintient ?** Une application est un petit **produit** : elle a des versions, des bogues, des utilisateurs. L'automatisation des traitements est traitée au volume V, chapitre 2.

Quand choisir quoi ? **Streamlit** pour aller vite et obtenir un joli résultat : prototypes, outils internes simples ; son modèle (le script se rejoue) est facile à comprendre, moins adapté aux interfaces très interactives. **Dash** pour les tableaux de bord construits autour de graphiques plotly, avec un contrôle fin des interactions, et quand on a besoin d'un composant précis. **Shiny** quand l'équipe travaille en **R**, ou pour les graphes réactifs complexes. Dans tous les cas, ces outils s'adressent à quelqu'un qui **sait programmer** : pour un décideur qui veut construire son propre tableau de bord sans code, les outils du chapitre 2 restent le bon choix.

> ✅ **À retenir.** Dash, Streamlit et Shiny fabriquent un tableau de bord avec quelques dizaines de lignes de code : script rejoué, fonctions de rappel ou graphe réactif. On **teste le calcul** sans navigateur (`AppTest`, appel direct de la fonction de rappel, `testServer`) et l'on **regarde la page** soi-même ; secrets hors du code, déploiement et maintenance sont de vraies charges.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.7 et 3.8, exercices 3.13 et 3.14.


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

```python
# non exécuté : nécessite geopandas et un fichier de contours administratifs (hypothétique)
import geopandas as gpd
zones = gpd.read_file("contours_regions.geojson")                 # une ligne par région, une colonne « geometry »
carte = zones.merge(ventes_par_region, on="region")              # jointure attributaire
carte.plot(column="ca_par_habitant", cmap="Blues", legend=True, edgecolor="white")
```

Deux questions de **droits** se posent dès que l'on sort du plan fictif. Les **tuiles** (les images du fond de carte que les cartes interactives téléchargent) viennent de services tiers, avec des **conditions d'utilisation** et des mentions d'**attribution** obligatoires, et parfois des limites d'usage ou un coût ; il faut les lire. Les **contours administratifs** et les **bases d'adresses** ont aussi une licence, qui peut interdire la redistribution : on la vérifie avant de publier une carte. Enfin, une carte de **personnes** (clients, patients) peut révéler des informations personnelles : des points précis sur une carte sont des **adresses** ; on les **agrège** (par zone, avec des seuils de petits effectifs) avant de les montrer (volume II, chapitre 5).

> ✅ **À retenir.** Une carte est utile quand la **position** compte ; on proportionne la **surface** (cercles), on **normalise** les valeurs absolues (par habitant), on se méfie du **biais des grandes zones**, et l'on joint des **barres** à toute carte qui doit servir à comparer. Les projections déforment, les fonds de carte ont des licences, et des points précis sur des personnes sont des données personnelles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.9, exercices 3.15 et 3.16.

<!--sortie-->


## Bilan du chapitre 3

Vous savez maintenant :

- **décrire** un graphique par ses trois couches (données, esthétiques, géométrie) et nommer les objets de matplotlib (Figure, Axes, Axis, Artist) ;
- **transformer** un graphique par défaut en graphique qui porte un message en cinq retouches : ordre, étiquettes directes, suppression du superflu, couleur avec intention, titre qui dit le message ;
- **tracer** barres, courbes, histogrammes (échelle linéaire et logarithmique), nuages de points et **petits multiples**, avec ou sans échelle partagée ;
- **ranger** vos réglages dans un thème, **mesurer** le contraste d'une palette, **choisir** le format d'enregistrement ;
- **utiliser** seaborn (boîtes, cartes thermiques) et **lire** ses intervalles de confiance sans les prendre pour une dispersion ;
- **enfermer** un graphique dans une fonction et **tester** les données qu'il dessine ;
- **écrire** la même figure en ggplot2 et passer d'une syntaxe à l'autre ;
- **construire** des figures plotly interactives (survol, zoom, légende), savoir quand elles aident ou gênent, et les **photographier** pour un support fixe ;
- (en option) **écrire** le même tableau de bord avec Streamlit, Dash et Shiny, le **tester** sans navigateur et le **photographier** ;
- (en option) **tracer** des cartes en cercles proportionnels et en zones colorées, **normaliser** par habitant, reconnaître le biais des grandes zones et savoir quand préférer des barres.

Le fil conducteur du chapitre tient en une phrase : **un graphique est un programme que l'on peut rejouer, tester et relire**. Ce que l'on a gagné en code (reproductibilité, tests, thème) n'a de valeur que si les choix de conception du chapitre 1 y sont appliqués : le bon type de graphique, une mise en page claire, des couleurs accessibles, un titre qui dit le message.

Le chapitre 4 passe du graphique au **récit** : comment assembler des graphiques, des chiffres et du texte pour **raconter une analyse** et rédiger un rapport qui sera lu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 (barres, séries, thème, seaborn, test et ggplot2, plotly, Streamlit et Dash, Shiny, cartes) et exercices 3.1 à 3.16.

<!--sortie-->
