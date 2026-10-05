## 4.5 Premières visualisations

> 💡 **Intuition.** Un tableau de 400 lignes, personne ne le « lit » vraiment ; un graphique bien choisi, on le comprend en trois secondes. Au 3.1 nous avons vu avec le quartet d'Anscombe que des données très différentes peuvent avoir **les mêmes statistiques** : seul le dessin révèle la différence. Visualiser n'est donc pas de la décoration, c'est un **outil de réflexion** (on dessine pour *comprendre*) et un **outil de communication** (on dessine pour *convaincre* sans tromper).
>
> Cette section a trois objectifs : savoir **quel graphique choisir** selon la question (4.5.1), savoir **le tracer** avec les trois bibliothèques les plus utilisées (matplotlib et pandas, seaborn, puis ggplot2 en R : 4.5.2 à 4.5.5), et savoir **éviter les graphiques trompeurs** (4.5.6).

> 🧭 **Pour la suite du livre.** Nous ne ferons ici que les graphiques fondamentaux. Les graphiques interactifs, les cartes ou les tableaux de bord complets sont abordés dans la série Data Analyst.

Pour être autonome, cette section recharge les données de 4.4 (même graine, mêmes résultats) et règle l'apparence des figures du livre : traits fins, grille discrète, pas de cadre inutile.

```python
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

BLEU, ORANGE, AQUA, VIOLET = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7"     # la palette du livre
COULEURS = {"Réseaux": BLEU, "Site": ORANGE, "Boutique": AQUA}

plt.rcParams.update({
    "figure.facecolor": "white", "axes.facecolor": "white",
    "axes.spines.top": False, "axes.spines.right": False,
    "axes.grid": True, "grid.color": "#e1e0d9", "grid.linewidth": 0.6,
    "axes.titlesize": 11, "axes.labelcolor": "#52514e", "legend.frameon": False,
})

# le jeu de données de 4.4 (identique : mêmes graines)
df = pd.read_csv("donnees/commandes.csv")
rng = np.random.default_rng(7)
jours = rng.integers(0, 140, size=len(df))
df["date"] = pd.Timestamp("2026-01-05") + pd.to_timedelta(jours, unit="D")
df["id_client"] = rng.integers(1, 121, size=len(df))
df = df.sort_values("date").reset_index(drop=True)
df["semaine"] = df["date"].dt.to_period("W").dt.start_time
hebdo = df.groupby("semaine").agg(commandes=("montant", "count"), ca=("montant", "sum"))
print(df.shape, "|", len(hebdo), "semaines | CA total :", round(df["montant"].sum(), 1), "€")
```
<!--sortie-->
```text
(400, 7) | 20 semaines | CA total : 24098.3 €
```

### 4.5.1 Quel graphique pour quelle question ?

La première erreur du débutant est de commencer par se demander « quel joli graphique ? ». La bonne démarche est inverse : on part de la **question**, puis du **type des variables** (revoyez le tableau du 3.1.1), et le graphique s'impose presque tout seul.

| La question | Les variables | Le graphique | Pourquoi |
|---|---|---|---|
| Comment se répartissent les montants ? | 1 quantitative | **histogramme** (ou boîte à moustaches) | montre la forme : symétrie, queue, valeurs atypiques |
| Quelle part de chaque canal ? | 1 qualitative | **diagramme en barres** (trié) | on compare des longueurs alignées, ce que l'œil fait très bien |
| Quel canal vend le plus ? | 1 qualitative + 1 quantitative | **barres** (une valeur par groupe) ou **boîtes à moustaches** (toute la distribution) | comparer des groupes |
| Comment évolue le chiffre d'affaires ? | 1 quantitative + le temps | **courbe** | la ligne relie les points : on voit la tendance |
| Les retards de livraison font-ils baisser la satisfaction ? | 2 quantitatives | **nuage de points** | montre la forme de la relation, pas seulement un nombre |
| Comment se croisent deux variables qualitatives ? | 2 qualitatives | **carte de chaleur** (*heatmap*) d'un tableau croisé | couleur = fréquence |

> 💡 **Trois questions avant de tracer.** (1) *Quel message* veux-je faire passer en une phrase ? (2) *Quelles variables* sont en jeu, et de quel type ? (3) *Qui va lire* ce graphique, en combien de temps ? Un graphique pour votre propre exploration peut être brouillon ; un graphique pour un patron pressé doit contenir **un message et un seul**.

> ⚠️ **Et le camembert ?** Il est partout, mais il est un mauvais choix dès qu'il y a plus de trois parts : l'œil compare mal des angles et des aires, bien mieux des **longueurs**. Pour montrer 3 canaux, un camembert est acceptable ; pour 8 produits, des barres triées sont toujours plus lisibles. (Les camemberts « en 3D » sont à proscrire absolument, voir 4.5.6.)

### 4.5.2 Anatomie d'un graphique matplotlib

**matplotlib** est la bibliothèque de base de la visualisation en Python : presque toutes les autres (pandas, seaborn…) s'appuient dessus. Elle est très complète, donc un peu intimidante ; comprendre sa structure suffit à s'y retrouver.

![Les pièces d'un graphique matplotlib : la Figure (la page entière), l'Axes (le repère, cadre pointillé), puis les éléments dessinés dedans.](figures/ch04-anatomie.png)

- La **Figure** est la page entière (sa taille se règle avec `figsize=(largeur, hauteur)` en pouces).
- L'**Axes** (au pluriel malgré les apparences : c'est *un* repère) est la zone où l'on dessine. Une figure peut en contenir un seul ou plusieurs (une grille 2×2, par exemple).
- Dans un Axes vivent des **objets** : lignes, barres, points, textes, légende, graduations, grille.

Il existe deux manières de s'en servir. L'interface « état » (`plt.plot(...)`) agit sur « le graphique courant » : très courte, mais confuse dès qu'il y a plusieurs panneaux. L'interface **orientée objet** crée explicitement la figure et l'axes, puis envoie des commandes à *l'axes* : c'est celle que nous utiliserons toujours, car elle ne laisse aucune ambiguïté sur « où » l'on dessine.

```python
fig, ax = plt.subplots(figsize=(7, 3.6))              # une figure contenant un seul Axes
ax.plot(hebdo.index, hebdo["ca"], marker="o", ms=4, color=BLEU)
ax.set_title("Chiffre d'affaires hebdomadaire de la boutique")
ax.set_xlabel("semaine (lundi)")
ax.set_ylabel("chiffre d'affaires (€)")
ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))   # dates au format jour/mois
fig.autofmt_xdate()                                    # incline les dates si nécessaire
fig.savefig("figures/ch04-premier-graphique.png", dpi=150, bbox_inches="tight")
plt.close(fig)                                         # libère la mémoire
print("figure enregistrée :", "semaine la plus forte =", hebdo["ca"].idxmax().date(), f"({hebdo['ca'].max():.0f} €)")
```
<!--sortie-->
```text
figure enregistrée : semaine la plus forte = 2026-03-23 (1737 €)
```

![Notre premier graphique : une courbe du chiffre d'affaires par semaine.](figures/ch04-premier-graphique.png)

Tout y est : un **titre**, des **axes nommés avec leur unité**, une ligne avec des **marqueurs** (un point par semaine, pour ne pas laisser croire que l'on connaît les valeurs entre les semaines). La courbe est irrégulière d'une semaine à l'autre, ce qui est normal : chaque semaine ne compte qu'entre 14 et 27 commandes, donc quelques gros paniers suffisent à faire bondir le total. Pour voir la **tendance**, on lisse avec une moyenne mobile, que nous ajouterons en 4.5.3.

> 🛠️ **Le patron de tous les graphiques matplotlib.** (1) `fig, ax = plt.subplots(...)` ; (2) `ax.plot / ax.bar / ax.hist / ax.scatter(...)` ; (3) `ax.set_title / set_xlabel / set_ylabel` ; (4) `fig.savefig(...)`. Pour *plusieurs* panneaux : `fig, axes = plt.subplots(2, 2)` renvoie un tableau d'Axes que l'on indexe `axes[0, 0]`, `axes[0, 1]`, etc. (c'est un tableau NumPy, voir 4.4.2).

### 4.5.3 Les quatre graphiques essentiels, avec pandas

pandas offre une méthode `.plot` sur ses Series et DataFrames, qui appelle matplotlib en coulisses et **renvoie l'Axes** : on peut donc la combiner avec tout ce qui précède, en lui passant l'argument `ax=`. Voici les quatre graphiques que vous tracerez le plus souvent, dans une seule figure à quatre panneaux :

1. **histogramme** des montants ;
2. **barres horizontales** du chiffre d'affaires par canal (triées) ;
3. **courbe** du chiffre d'affaires hebdomadaire avec sa moyenne mobile ;
4. **nuage de points** livraison/satisfaction.

Pour le quatrième, un détail d'importance. La livraison est un nombre entier de jours et la satisfaction une note entière de 1 à 5 : beaucoup de commandes tombent *exactement au même point*, et un nuage de points normal en cacherait la plupart. On les **décale aléatoirement d'un tout petit peu** (« jitter », en français *jitter* ou *bruitage*) et on rend les points translucides : les zones denses apparaissent plus foncées.

```python
fig, axes = plt.subplots(2, 2, figsize=(10.5, 7.2))
fig.subplots_adjust(hspace=0.38, wspace=0.28)

# 1. histogramme (pandas)
ax = axes[0, 0]
df["montant"].plot.hist(bins=30, ax=ax, color=BLEU, alpha=0.7, edgecolor="white")
ax.axvline(df["montant"].median(), color=ORANGE, ls="--", lw=2)
ax.text(df["montant"].median() + 5, ax.get_ylim()[1] * 0.9, "médiane", color=ORANGE)
ax.set(title="Histogramme : la distribution des montants", xlabel="montant d'une commande (€)", ylabel="nombre de commandes")

# 2. barres horizontales, triées (pandas)
ax = axes[0, 1]
ca_canal = df.groupby("canal")["montant"].sum().sort_values()
ca_canal.plot.barh(ax=ax, color=[COULEURS[c] for c in ca_canal.index], alpha=0.8)
for i, v in enumerate(ca_canal):
    ax.text(v + 80, i, f"{v:,.0f} €".replace(",", " "), va="center")
ax.set(title="Barres : le chiffre d'affaires par canal", xlabel="chiffre d'affaires (€)", ylabel="", xlim=(0, ca_canal.max() * 1.2))
ax.grid(axis="y", visible=False)

# 3. courbe + moyenne mobile (pandas)
ax = axes[1, 0]
hebdo["ca"].plot(ax=ax, color=BLEU, alpha=0.45, marker="o", ms=3, label="une semaine")
hebdo["ca"].rolling(4).mean().plot(ax=ax, color=ORANGE, lw=2.5, label="moyenne mobile sur 4 semaines")
ax.set_ylim(top=2100)                                   # on laisse de la place en haut pour la légende
ax.legend(loc="upper left")
ax.set(title="Courbe : l'évolution dans le temps", xlabel="semaine", ylabel="chiffre d'affaires (€)")

# 4. nuage de points avec jitter (matplotlib)
ax = axes[1, 1]
bruit = np.random.default_rng(5)
x = df["livraison"] + bruit.uniform(-0.25, 0.25, len(df))
y = df["satisfaction"] + bruit.uniform(-0.25, 0.25, len(df))
ax.scatter(x, y, s=14, alpha=0.35, color=VIOLET, edgecolors="none")
ax.set_yticks(range(1, 6))
ax.set(title="Nuage de points : livraison et satisfaction", xlabel="délai de livraison (jours)", ylabel="note de satisfaction")

fig.savefig("figures/ch04-essentiels.png", dpi=150, bbox_inches="tight")
plt.close(fig)
r = df[["livraison", "satisfaction"]].corr().iloc[0, 1]
print("corrélation livraison / satisfaction :", round(r, 2))
print("part du CA du canal en tête :", f"{ca_canal.iloc[-1] / ca_canal.sum():.0%}")
```
<!--sortie-->
```text
corrélation livraison / satisfaction : -0.53
part du CA du canal en tête : 37%
```

![Les quatre graphiques essentiels : histogramme, barres triées, courbe avec moyenne mobile, nuage de points « bruité ».](figures/ch04-essentiels.png)

**Comment lire chaque panneau** (c'est aussi comme cela qu'on doit *légender* un graphique dans un rapport) :

- **Histogramme** : la forme est asymétrique à droite, avec une longue queue de grosses commandes ; la médiane (trait orange, 51 €) est nettement sous la moyenne (60 €), tirée vers le haut par les grosses commandes (revoir 3.1.5).
- **Barres** : on lit au premier coup d'œil l'ordre des canaux, et les valeurs sont écrites au bout des barres : plus besoin de deviner sur l'axe. Les barres sont **triées** : un classement doit être lisible.
- **Courbe** : le trait pâle est le chiffre d'affaires de chaque semaine, très irrégulier ; le trait orange, plus lisse, montre la **tendance**.
- **Nuage de points** : plus le délai augmente, plus les notes basses apparaissent ; la corrélation affichée (−0,53) est négative et d'intensité moyenne : un retard fait *tendanciellement* baisser la note, sans que ce soit une règle absolue (beaucoup de commandes tardives ont quand même 4).

> 🧪 **Pourquoi `.plot` renvoie-t-il l'Axes ?** Parce que ainsi tout est modifiable après coup : titre, limites, annotations. Si vous écrivez `ax = df["montant"].plot.hist()`, vous pouvez ensuite faire `ax.set_title(...)`. pandas propose aussi `.plot.bar()`, `.plot.line()`, `.plot.box()`, `.plot.scatter(x=, y=)`, `.plot.pie()`, `.plot.area()`… Pour l'exploration rapide, c'est imbattable (une ligne par graphique).

### 4.5.4 seaborn : des graphiques statistiques en une ligne

**seaborn** est une couche au-dessus de matplotlib spécialisée dans les graphiques **statistiques**. Son atout : on lui donne le **tableau complet** (`data=df`) et on dit quelle colonne va où (`x=`, `y=`, `hue=` pour la couleur), et seaborn s'occupe des regroupements, des légendes et des couleurs.

Deux exemples. D'abord la distribution des montants **selon le canal**, en histogramme et en boîte à moustaches :

```python
import seaborn as sns

sns.set_theme(style="whitegrid", rc={"axes.spines.top": False, "axes.spines.right": False})
ordre = ["Réseaux", "Site", "Boutique"]

fig, axes = plt.subplots(1, 2, figsize=(11, 4), gridspec_kw={"width_ratios": [1.3, 1], "wspace": 0.25})
sns.histplot(data=df, x="montant", hue="canal", hue_order=ordre, palette=COULEURS, bins=30,
             element="step", alpha=0.3, ax=axes[0])
axes[0].set(title="Histogrammes superposés selon le canal", xlabel="montant (€)", ylabel="nombre de commandes")

sns.boxplot(data=df, x="canal", y="montant", order=ordre, hue="canal", palette=COULEURS, legend=False,
            width=0.55, fliersize=3, ax=axes[1])
axes[1].set(title="Boîtes à moustaches selon le canal", xlabel="", ylabel="montant (€)")

fig.savefig("figures/ch04-seaborn-distributions.png", dpi=150, bbox_inches="tight")
plt.close(fig)
print(df.groupby("canal")["montant"].median().reindex(ordre).round(1).to_string())
```
<!--sortie-->
```text
canal
Réseaux    41.5
Site         49.5
Boutique     64.8
```

![Avec seaborn, une ligne suffit pour séparer les données par canal : histogrammes superposés et boîtes à moustaches.](figures/ch04-seaborn-distributions.png)

Les médianes imprimées confirment la lecture : 64,8 € pour la boutique, 49,5 € pour le site, 41,5 € pour Réseaux. (Cette différence est-elle réelle ou due au hasard ? C'est la question d'un test statistique, 3.4.)

Deuxième exemple : une **carte de chaleur** pour le croisement de deux variables qualitatives, le canal et la note de satisfaction. On calcule d'abord le tableau croisé (en proportions par canal), puis on le colore :

```python
tab = pd.crosstab(df["canal"], df["satisfaction"], normalize="index").loc[ordre]
print(tab.round(2))

fig, ax = plt.subplots(figsize=(6.5, 3))
sns.heatmap(tab, annot=True, fmt=".0%", cmap="Blues", cbar=False, linewidths=2, linecolor="white", ax=ax)
ax.set(title="Part de chaque note, selon le canal", xlabel="note de satisfaction", ylabel="")
fig.savefig("figures/ch04-seaborn-heatmap.png", dpi=150, bbox_inches="tight")
plt.close(fig)
```
<!--sortie-->
```text
satisfaction     1     2     3     4     5
canal                                     
Réseaux     0.00  0.06  0.31  0.49  0.14
Site          0.01  0.05  0.25  0.54  0.16
Boutique      0.00  0.00  0.04  0.42  0.54
```

![Carte de chaleur : chaque ligne (canal) somme à 100 %. Plus la case est foncée, plus la note est fréquente dans ce canal.](figures/ch04-seaborn-heatmap.png)

Chaque ligne du tableau somme à 1 (donc 100 %) : on lit « *parmi* les commandes de la boutique, 54 % ont donné la note 5 » (contre 14 % pour Réseaux et 16 % pour le Site). La case la plus foncée de la ligne Boutique est à droite (la note 5), celles d'Réseaux et du Site sont sur la note 4, avec une part importante de 3 : la boutique, où la livraison est immédiate, a les clients les plus satisfaits.

> 💡 **matplotlib, pandas ou seaborn ?** Ce n'est pas un choix exclusif : seaborn et pandas **dessinent dans des Axes matplotlib**, que l'on peut retoucher avec les méthodes de 4.5.2. Règle pratique : pandas `.plot` pour regarder vite, seaborn pour les graphiques statistiques avec groupes, matplotlib pour tout ce qui doit être personnalisé au pixel près.

### 4.5.5 ggplot2 : la grammaire des graphiques en R

En R, la bibliothèque de référence est **ggplot2**. Son idée, la « **grammaire des graphiques** » (*grammar of graphics*), est de **décrire** un graphique par couches plutôt que de le dessiner pas à pas :

- les **données** (`ggplot(data, ...)`) ;
- une **correspondance esthétique** `aes(x=, y=, fill=)` : quelle colonne va sur quel axe ou dans quelle couleur ;
- une ou plusieurs **géométries** `geom_...()` : histogramme, barres, points, lignes ;
- éventuellement des **facettes** (`facet_wrap`) pour faire un panneau par groupe, des **échelles** et un **thème**.

On additionne ces couches avec le signe `+`. Reproduisons l'histogramme par canal ; R lit le même fichier CSV (les bases du langage R sont présentées en 4.2) :

```r
library(ggplot2)
commandes <- read.csv("donnees/commandes.csv")
commandes$canal <- factor(commandes$canal, levels = c("Réseaux", "Site", "Boutique"))
print(aggregate(montant ~ canal, data = commandes, FUN = function(x) round(median(x), 1)))

p <- ggplot(commandes, aes(x = montant, fill = canal)) +
  geom_histogram(bins = 30, alpha = 0.8, colour = "white") +
  facet_wrap(~ canal, ncol = 1) +
  scale_fill_manual(values = c(Réseaux = "#2a78d6", Site = "#eb6834", Boutique = "#1baf7a")) +
  labs(title = "Distribution des montants selon le canal", x = "montant (€)", y = "nombre de commandes") +
  theme_minimal(base_size = 11) +
  theme(legend.position = "none")
ggsave("figures/ch04-ggplot-montants.png", plot = p, width = 7, height = 5, dpi = 150)
cat("figure enregistrée\n")
```
<!--sortie-->
```text
      canal montant
1 Réseaux    41.5
2      Site    49.5
3  Boutique    64.8
figure enregistrée
```

![Le même type de graphique avec ggplot2 : un panneau par canal (facettes), même échelle horizontale.](figures/ch04-ggplot-montants.png)

On retrouve les mêmes médianes qu'en Python (confirmant que les deux outils lisent bien les mêmes données). Le tableau suivant résume la différence de philosophie :

| | matplotlib / seaborn (Python) | ggplot2 (R) |
|---|---|---|
| Style | **impératif** : on construit pas à pas (figure → axes → éléments) | **déclaratif** : on décrit le résultat par couches |
| Séparer par groupe | `hue=` (seaborn) ou une boucle sur les groupes | `fill=`, `colour=`, ou `facet_wrap()` |
| Personnalisation fine | très grande, mais verbeuse | grande, via `theme()` et `scale_*()` |
| Combiner plusieurs couches | appels successifs sur le même `ax` | `+ geom_...()` |

> 🧪 **Honnêteté d'exécution.** Les graphiques de cette section ont tous été produits par le code affiché (sauf trois dessins explicatifs, produits par `build/fig_ch04.py` : l'anatomie d'une figure, le broadcasting et l'axe tronqué) ; le bloc R ci-dessus a bien été exécuté (R avec ggplot2). Les versions de bibliothèques peuvent légèrement modifier l'aspect (polices, marges) sans changer l'information.

### 4.5.6 Bien faire, mal faire : les pièges du graphique trompeur

Un graphique peut mentir sans qu'une seule donnée soit fausse. Voici les six pièges les plus répandus. Le premier mérite une démonstration.

**Piège n°1 : l'axe tronqué.** Comparons la satisfaction moyenne d'Réseaux et du Site. Les deux graphiques ci-dessous montrent **exactement les mêmes deux nombres**.

```python
moy = df[df["canal"].isin(["Réseaux", "Site"])].groupby("canal")["satisfaction"].mean()
insta, site = moy["Réseaux"], moy["Site"]
print("moyennes :", round(insta, 2), "et", round(site, 2))
print("écart réel : +", round((site / insta - 1) * 100, 1), "%")
print("barre du Site / barre d'Réseaux si l'axe commence à 3,70 :", round((site - 3.70) / (insta - 3.70), 1), "fois plus haute")
```
<!--sortie-->
```text
moyennes : 3.72 et 3.79
écart réel : + 2.0 %
barre du Site / barre d'Réseaux si l'axe commence à 3,70 : 5.2 fois plus haute
```

![Mêmes données, deux impressions opposées : à gauche l'axe commence à 3,70, à droite à 0.](figures/ch04-axe-tronque.png)

À gauche, avec un axe qui commence à 3,70, la barre du Site paraît **plus de 5 fois plus haute** que celle d'Réseaux (c'est le « 5,2 fois » imprimé ci-dessus) ; à droite, sur un axe complet, les deux barres sont quasiment identiques, ce qui correspond bien à l'écart réel de 2 %. **Règle : pour un diagramme en barres, l'axe doit commencer à 0**, car c'est la *longueur* de la barre qui porte l'information. (Pour une courbe ou un nuage de points, c'est la position qui compte : on peut zoomer, à condition de le signaler.)

**Les autres pièges, et leurs remèdes :**

| Piège | Pourquoi c'est un problème | Remède |
|---|---|---|
| **Camembert en 3D, ou à beaucoup de parts** | la perspective déforme les aires ; l'œil compare mal les angles | barres triées, en 2D |
| **Double axe vertical** | on peut rendre n'importe quelle corrélation « visible » en choisissant les échelles | deux graphiques superposés, ou un seul axe |
| **Trop de couleurs** | 10 couleurs sans ordre : personne ne retient la légende | 3 à 5 couleurs, avec un sens (une couleur = un canal, partout dans le document) |
| **Points superposés** | 400 observations qui se cachent les unes les autres (voir le jitter, 4.5.3) | transparence, bruitage, ou histogramme 2D |
| **Titre vague** (« Graphique 3 ») | le lecteur doit deviner la conclusion | un titre qui **dit** le message : « La boutique a les clients les plus satisfaits » |
| **Axes sans nom ni unité** | « 60 », mais de quoi ? | toujours nommer et donner l'unité (€, jours, %) |

> ✅ **La liste de contrôle d'un bon graphique.** (1) Un message, un titre qui le dit. (2) Le bon type de graphique pour la question (tableau 4.5.1). (3) Des axes nommés avec leurs unités ; **zéro pour les barres**. (4) Des barres **triées** quand elles représentent un classement. (5) Peu de couleurs, avec un sens constant. (6) Lisible en noir et blanc et pour un daltonien : ne pas reposer sur l'opposition rouge/vert seule. (7) La source des données et la date, si l'on communique à d'autres.

### 4.5.7 Enregistrer, réutiliser : de la figure au rapport

Un graphique n'est utile que s'il sort de votre ordinateur. `fig.savefig(chemin)` choisit le format d'après l'extension, avec trois réglages à connaître :

| Format | Quand l'utiliser |
|---|---|
| **PNG** (`.png`) | pages web, diapositives, e-mails : image « pixels », léger |
| **SVG / PDF** (`.svg`, `.pdf`) | impression, articles, LaTeX : image **vectorielle**, nette à toute taille |
| `dpi=` | résolution en pixels par pouce : **150** pour l'écran, **300** pour l'impression |
| `bbox_inches="tight"` | rogne les marges blanches inutiles |

```python
import os
import tempfile

dossier = tempfile.mkdtemp()
fig, ax = plt.subplots(figsize=(4, 2.5))
ax.bar(ordre, [df[df["canal"] == c]["montant"].sum() for c in ordre], color=[COULEURS[c] for c in ordre])
for ext in ["png", "svg", "pdf"]:
    chemin = os.path.join(dossier, f"exemple.{ext}")
    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    print(f".{ext} enregistré, taille non nulle :", os.path.getsize(chemin) > 0)
plt.close(fig)
```
<!--sortie-->
```text
.png enregistré, taille non nulle : True
.svg enregistré, taille non nulle : True
.pdf enregistré, taille non nulle : True
```

> 🛠️ **Application : le tableau de bord de la gérante.** Mettons tout en commun dans une **fonction** qui produit en une fois la figure que la gérante joint à son rapport du lundi (celui de 4.4.13). Remarquez que chaque panneau a un **titre qui énonce sa conclusion**, calculée à partir des données (et non écrite à la main) : si les chiffres changent, le titre reste vrai.

```python
def tableau_de_bord(df, chemin):
    """Dessine le tableau de bord de la boutique à partir du DataFrame `df` et l'enregistre dans `chemin`."""
    ca = df.groupby("semaine")["montant"].sum()
    lisse = ca.rolling(4).mean().dropna()
    par_canal = df.groupby("canal")["montant"].sum().sort_values()
    notes = df["satisfaction"].value_counts().sort_index()
    sens = "monte" if lisse.iloc[-1] > lisse.iloc[0] else "baisse"

    fig = plt.figure(figsize=(10.5, 6.6))
    grille = fig.add_gridspec(2, 2, height_ratios=[1.15, 1], hspace=0.5, wspace=0.3)

    ax = fig.add_subplot(grille[0, :])                              # panneau du haut : toute la largeur
    ax.plot(ca.index, ca.values, color=BLEU, alpha=0.35, marker="o", ms=3)
    ax.plot(lisse.index, lisse.values, color=BLEU, lw=2.5)
    ax.set_title(f"Le chiffre d'affaires hebdomadaire {sens} : de {lisse.iloc[0]:.0f} à {lisse.iloc[-1]:.0f} € (moyenne mobile)")
    ax.set_ylabel("€ par semaine")
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=4))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))

    ax = fig.add_subplot(grille[1, 0])
    ax.barh(par_canal.index, par_canal.values, color=[COULEURS[c] for c in par_canal.index], alpha=0.85)
    for i, v in enumerate(par_canal):
        ax.text(v + 80, i, f"{v / par_canal.sum():.0%}".replace("%", " %"), va="center")
    ax.set_title(f"{par_canal.index[-1]} : {par_canal.iloc[-1] / par_canal.sum():.0%} du chiffre d'affaires".replace("%", " %"))
    ax.set_xlabel("chiffre d'affaires (€)")
    ax.set_xlim(0, par_canal.max() * 1.2)
    ax.grid(axis="y", visible=False)

    ax = fig.add_subplot(grille[1, 1])
    ax.bar(notes.index, notes.values, color=[ORANGE if n <= 2 else BLEU for n in notes.index], alpha=0.85)
    ax.set_title(f"{(df['satisfaction'] >= 4).mean():.0%} des clients notent 4 ou 5".replace("%", " %"))
    ax.set_xlabel("note de satisfaction")
    ax.set_ylabel("commandes")
    ax.grid(axis="x", visible=False)

    fig.savefig(chemin, dpi=150, bbox_inches="tight")
    plt.close(fig)
    return par_canal.index[-1], round(float(lisse.iloc[-1]), 1)


print(tableau_de_bord(df, "figures/ch04-tableau-de-bord.png"))
```
<!--sortie-->
```text
('Site', 1433.7)
```

![Le tableau de bord produit par la fonction : trois panneaux, chacun avec un titre qui énonce sa conclusion.](figures/ch04-tableau-de-bord.png)

Lisons-le comme le ferait la gérante : la tendance du chiffre d'affaires est à la hausse (1 080 → 1 434 € par semaine en moyenne mobile), le Site et la Boutique pèsent chacun plus d'un tiers des ventes, et trois clients sur quatre sont satisfaits (4 ou 5). Voilà le chemin complet : des **données brutes** (fichier CSV) aux **tableaux** (pandas, 4.4) puis aux **figures** prêtes à insérer dans un rapport, le tout dans un script que l'on peut relancer chaque semaine. C'est l'esprit de la **recherche reproductible** que nous retrouverons au chapitre 6.

> ✅ **À retenir (visualisation).**
>
> 1. On part de la **question** et du **type des variables**, pas du joli graphique ;
> 2. matplotlib : `fig, ax = plt.subplots()`, on dessine dans l'`ax`, on nomme, on enregistre ; pandas `.plot` et seaborn dessinent dans le même cadre ;
> 3. quatre fondamentaux : histogramme (forme), barres triées (comparaison), courbe (temps), nuage de points (relation) ;
> 4. **barres : l'axe commence à zéro** ; pas de 3D ; peu de couleurs, avec un sens ; titre = message ;
> 5. ggplot2 (R) décrit un graphique par **couches** : données + esthétique + géométrie ;
> 6. **PNG** pour l'écran, **PDF/SVG** pour l'impression ; une fonction de tracé rend l'analyse reproductible.
