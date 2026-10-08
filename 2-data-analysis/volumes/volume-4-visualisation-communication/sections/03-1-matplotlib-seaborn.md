## 3.1 matplotlib et seaborn

**matplotlib** est la bibliothèque de dessin de base de Python : presque toutes les autres (seaborn, pandas, scikit-learn) l'utilisent en coulisse. Elle est un peu verbeuse, mais elle donne le contrôle de **chaque** élément d'une figure, et c'est ce contrôle qui sépare un graphique par défaut d'un graphique qui fait passer un message.

### 3.1.1 Trois couches, et l'anatomie d'une figure

Tout graphique statistique, quel que soit l'outil, se décrit en **trois couches**. Les **données** (un tableau), les **esthétiques** (quelle colonne va sur quel attribut visuel : position horizontale, hauteur, couleur, taille) et la **géométrie** (la forme dessinée : barres, lignes, points). Un graphique à barres du chiffre d'affaires par canal : le tableau est « un canal et un chiffre d'affaires par ligne », l'esthétique est « canal en abscisse, chiffre d'affaires en hauteur, couleur selon le canal », la géométrie est « une barre par ligne ».

```python hide
O.sauver(O.trois_couches(), "ch03-trois-couches.png")
```
<!--sortie-->
```text
figure : ch03-trois-couches.png
```
<!--sortie-->

![Les trois couches d'un graphique. Schéma dessiné avec matplotlib.](figures/ch03-trois-couches.png)

Cette grammaire est explicite dans ggplot2 (voir 3.1.9) ; elle est implicite dans matplotlib, où l'on **dessine** étape par étape. Il faut donc connaître le vocabulaire de ce que l'on dessine.

```python hide
O.sauver(O.anatomie(), "ch03-anatomie.png")
```
<!--sortie-->
```text
figure : ch03-anatomie.png
```
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

```python hide
a = x.groupby(["annee", "canal"])["montant"].sum().unstack() / 1000
assert [round(a.loc[2023, "Site"]), round(a.loc[2025, "Site"])] == [422, 618]
assert m.loc["2025-12", "Site"] > m.loc["2025-12", "Boutique"] and m.sum(axis=1).idxmax() == pd.Period("2025-12")
assert 81 <= p25.groupby("canal")["montant"].median().min() and p25.groupby("canal")["montant"].median().max() < 82.6
assert (dec.min(), dec.max()) == (31, 97) and round(1.96 * se) == 3
assert round(piv.loc[12, 6]) == 85 and round(piv.loc[1, 7]) == 20 and piv.loc[12, 6] / piv.loc[1, 7] > 4
assert round(panier.median()) == 82 and round(panier.mean()) == 102 and round(j25["depense_pub"].corr(j25["nb_commandes"]), 2) == 0.54
assert (round(m["Réseaux"].max()), round(m["Site"].max())) == (20, 90)
```
<!--sortie-->
