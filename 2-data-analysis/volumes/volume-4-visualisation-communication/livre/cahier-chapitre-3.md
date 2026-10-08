# Chapitre 3 : Visualisation avec Python — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 3 du livre. Les **applications** sont de petites études guidées sur les données de la boutique : vous les refaites pas à pas, puis vous répondez aux **exercices**, dont les **corrigés** sont à la fin. Presque tous les exercices demandent de **produire** ou de **critiquer** un graphique, et la plupart des corrigés **montrent** la figure attendue. Les captures d'outils interactifs sont de vraies captures d'outils libres, lancés localement.

Une première cellule charge les bibliothèques et les données ; les cellules suivantes reprennent les noms ainsi définis.

```python
import os, sys
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import seaborn as sns
import style, outils_ch03 as O
style.setup()

x = O.ventes()                  # une ligne par ligne de commande : montant, date, canal, client, catégorie
j = O.jours()                   # une ligne par jour d'exploitation
liv = O.lire("livraisons.csv", parse_dates=["date_commande", "date_expedition", "date_livraison"])
print(len(x), "lignes de commande |", len(j), "jours |", len(liv), "livraisons")
```
<!--sortie-->
```text
83905 lignes de commande | 1096 jours | 19420 livraisons
```
<!--sortie-->

<!--sortie-->

## Applications

### Application 3.1 — Du graphique par défaut au graphique qui dit quelque chose (sections 3.1.1 et 3.1.2)

**Objectif.** Partir du graphique que matplotlib produit sans réglage, puis le transformer en graphique qui porte un message, en suivant les cinq retouches du livre.

**Étape 1 — Le graphique par défaut.** Le chiffre d'affaires 2025 par catégorie de produits, sans aucun réglage.

```python
cat = x[x["annee"] == 2025].groupby("categorie")["montant"].sum().sort_values(ascending=False) / 1000
fig, ax = plt.subplots()
ax.bar(cat.sort_index().index, cat.sort_index().values)
O.sauver(fig, "ch03-cah-categories-defaut.png")
print(cat.sort_index().round(1).to_dict())
```
<!--sortie-->
```text
figure : ch03-cah-categories-defaut.png
{'Bien-être': 117.5, 'Cuisine': 233.3, 'Décoration': 258.7, 'Jardin': 354.0, 'Maison': 304.6, 'Papeterie': 56.6}
```
<!--sortie-->

![Le graphique par défaut : barres de la même couleur, dans l'ordre alphabétique.](figures/ch03-cah-categories-defaut.png)

**Étape 2 — Les cinq retouches.** Ordre décroissant, barres **horizontales** (les noms de catégories se lisent mieux), étiquettes directes, suppression de l'axe et du quadrillage, **une** couleur d'accent sur la catégorie qui compte, titre qui dit le message.

```python
tri = cat.sort_values()                                      # barres horizontales : la plus grande en haut
fig, ax = plt.subplots(figsize=(5.8, 3.3))
couleurs = [style.BLEU if c == tri.idxmax() else style.MUET for c in tri.index]
barres = ax.barh(tri.index, tri.values, color=couleurs, height=0.62)
ax.bar_label(barres, labels=[f"{fr(v, 0)} k€" for v in tri.values], padding=3)
ax.set(xlim=(0, tri.max() * 1.15), xticks=[]); ax.grid(False); ax.spines["bottom"].set_visible(False)
part = tri.max() / tri.sum() * 100
ax.set_title(f"{tri.idxmax()} est la première catégorie : {part:.0f} % du chiffre d'affaires 2025", loc="left", fontweight="bold", fontsize=10)
O.sauver(fig, "ch03-cah-categories-final.png")
print(tri.idxmax(), "|", round(part, 1), "% | rapport entre la première et la dernière :", round(tri.max() / tri.min(), 2))
```
<!--sortie-->
```text
figure : ch03-cah-categories-final.png
Jardin | 26.7 % | rapport entre la première et la dernière : 6.25
```
<!--sortie-->

![Les mêmes données après les cinq retouches.](figures/ch03-cah-categories-final.png)

**Étape 3 — Vérifier le titre.** Le titre est calculé : il ne doit jamais mentir. Comptez, en une ligne, combien de catégories dépassent un sixième du chiffre d'affaires (la part d'une catégorie « moyenne ») et dites si la catégorie mise en avant est vraiment une exception ou si les six catégories se ressemblent.

```python
print((cat / cat.sum()).round(3).to_dict(), "| au-dessus d'un sixième :", int((cat / cat.sum() > 1 / 6).sum()))
```
<!--sortie-->
```text
{'Jardin': 0.267, 'Maison': 0.23, 'Décoration': 0.195, 'Cuisine': 0.176, 'Bien-être': 0.089, 'Papeterie': 0.043} | au-dessus d'un sixième : 4
```
<!--sortie-->

Quatre catégories sur six dépassent un sixième du chiffre d'affaires : Jardin (27 %) est **la première**, devant Maison (23 %), mais elle ne « domine » pas. Le titre « première catégorie » est honnête ; « domine » ne le serait pas.

**À retenir.** Une couleur d'accent n'a de sens que si **un** élément se distingue vraiment ; si les barres sont proches, le message honnête est « elles se ressemblent », pas « une catégorie domine ».

### Application 3.2 — Séries temporelles et petits multiples (sections 3.1.3 à 3.1.5)

**Objectif.** Comparer trois années mois par mois avec des étiquettes directes, puis voir ce que change l'échelle partagée dans des petits multiples.

**Étape 1 — Trois années superposées.** On met les mois de 1 à 12 en abscisse et une ligne par année ; l'étiquette de l'année est écrite au bout de la ligne.

```python
mm = x.groupby(["annee", x["date_commande"].dt.month])["montant"].sum().unstack(0) / 1000   # index : mois 1 à 12 ; colonnes : années
couleurs = {2023: style.MUET, 2024: style.ENCRE2, 2025: style.BLEU}
fig, ax = plt.subplots(figsize=(6.4, 3.3))
for a in mm.columns:
    ax.plot(mm.index, mm[a], color=couleurs[a], linewidth=2.2 if a == 2025 else 1.4)
    ax.text(12.15, mm[a].iloc[-1] + {2023: -5, 2024: 5, 2025: 0}[a], str(a), color=couleurs[a], va="center", fontweight="bold")
ax.set(xlim=(1, 12.9), xticks=range(1, 13), xlabel="mois", ylabel="k€")
croiss = mm[2025].sum() / mm[2024].sum() * 100 - 100
ax.set_title(f"2025 dépasse 2024 de {croiss:.0f} % et la forme saisonnière ne change pas", loc="left", fontweight="bold", fontsize=10)
O.sauver(fig, "ch03-cah-annees.png")
print({a: round(mm[a].sum()) for a in mm.columns}, "| meilleur mois 2025 :", mm[2025].idxmax())
```
<!--sortie-->
```text
figure : ch03-cah-annees.png
{2023: 1139, 2024: 1189, 2025: 1325} | meilleur mois 2025 : 12
```
<!--sortie-->

![Trois années superposées, mois par mois.](figures/ch03-cah-annees.png)

**Étape 2 — Des petits multiples, avec et sans échelle commune.** En haut, chaque canal a **sa** échelle ; en bas, tous partagent la même.

```python
m = x.groupby(["mois", "canal"])["montant"].sum().unstack()[O.CANAUX] / 1000
t = m.index.to_timestamp()
fig, axes = plt.subplots(2, 3, figsize=(8, 4.4), sharex=True)
for k, canal in enumerate(O.CANAUX):
    for l_ in (0, 1):
        axes[l_, k].plot(t, m[canal], color=O.COUL[canal])
    axes[0, k].set_title(canal, loc="left", color=O.COUL[canal], fontweight="bold")
    axes[1, k].set_ylim(0, m.values.max() * 1.05)
    axes[1, k].xaxis.set_major_locator(mdates.YearLocator()); axes[1, k].xaxis.set_major_formatter(mdates.DateFormatter("%Y"))
axes[0, 0].set_ylabel("échelle libre (k€)"); axes[1, 0].set_ylabel("échelle commune (k€)")
O.sauver(fig, "ch03-cah-multiples.png")
print("maximum mensuel (k€) :", {c: round(m[c].max()) for c in O.CANAUX})
```
<!--sortie-->
```text
figure : ch03-cah-multiples.png
maximum mensuel (k€) : {'Boutique': 81, 'Site': 90, 'Réseaux': 20}
```
<!--sortie-->

![Petits multiples : échelle libre en haut, échelle commune en bas.](figures/ch03-cah-multiples.png)

**À retenir.** Le haut répond à « quelle **forme** a chaque canal ? » (la saison est visible partout), le bas répond à « **combien** pèse chaque canal ? » (les Réseaux sont petits). On ne choisit pas au hasard : on choisit selon la question.

### Application 3.3 — Un thème, un contraste, un format (section 3.1.6)

**Objectif.** Ranger les réglages dans un thème appliqué localement, mesurer le contraste de la palette, et choisir un format d'enregistrement.

**Étape 1 — Un thème local.** `plt.rc_context` applique des réglages **le temps d'un bloc**, sans modifier le reste du script.

```python
theme = {"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True, "grid.color": style.GRILLE,
         "axes.titleweight": "bold", "axes.titlelocation": "left", "legend.frameon": False, "axes.axisbelow": True}
ca = O.ca_canal(x) / 1000
with plt.rc_context(theme):
    fig, ax = plt.subplots(figsize=(4.6, 2.6))
    ax.bar(ca.index, ca.values, color=[O.COUL[c] for c in ca.index], width=0.6)
    ax.set_title("Chiffre d'affaires 2025 (k€)")
O.sauver(fig, "ch03-cah-theme.png")
print("réglages du thème :", len(theme), "| grille après le bloc :", plt.rcParams["axes.grid"])
```
<!--sortie-->
```text
figure : ch03-cah-theme.png
réglages du thème : 8 | grille après le bloc : True
```
<!--sortie-->

![Un graphique tracé avec le thème local.](figures/ch03-cah-theme.png)

**Étape 2 — Mesurer le contraste.** La fonction du livre donne le rapport de contraste ; on l'applique aux couleurs de la palette **sur le fond blanc** et sur le fond du livre, et l'on cherche, pour l'aqua, une version assez foncée pour du **texte** (rapport d'au moins 4,5).

```python
def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contraste(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

def assombrir(h, f):
    return "#" + "".join(f"{int(int(h[i:i + 2], 16) * f):02x}" for i in (1, 3, 5))

noms = ("BLEU", "ORANGE", "AQUA", "VIOLET", "ROUGE")
print({n: (round(contraste(getattr(style, n), "#ffffff"), 1), round(contraste(getattr(style, n), style.SURFACE), 1)) for n in noms})
f = next(f for f in np.arange(1.0, 0.2, -0.02) if contraste(assombrir(style.AQUA, f), style.SURFACE) >= 4.5)
print("aqua assombri pour du texte :", assombrir(style.AQUA, f), "| facteur", round(f, 2), "| contraste", round(contraste(assombrir(style.AQUA, f), style.SURFACE), 1))
```
<!--sortie-->
```text
{'BLEU': (4.4, 4.3), 'ORANGE': (3.2, 3.1), 'AQUA': (2.8, 2.7), 'VIOLET': (8.6, 8.3), 'ROUGE': (4.0, 3.9)}
aqua assombri pour du texte : #14845c | facteur 0.76 | contraste 4.6
```
<!--sortie-->

**Étape 3 — Choisir un format.** On enregistre le même nuage de **20 000 points** en PNG, en SVG et en PDF, avec et sans `rasterized=True` pour le vectoriel.

```python
rng = np.random.default_rng(0)
px_, py_ = rng.normal(size=20000), rng.normal(size=20000)
dossier = O.dossier_temp()
tailles = {}
for nom, ras in (("png", False), ("svg", False), ("svg rastérisé", True), ("pdf", False)):
    fig, ax = plt.subplots(figsize=(4, 3)); ax.scatter(px_, py_, s=3, rasterized=ras)
    chemin = os.path.join(dossier, "nuage." + nom.split()[0]); fig.savefig(chemin, dpi=200); plt.close(fig)
    tailles[nom] = os.path.getsize(chemin) // 1024
O.supprimer_dossier(dossier)
print("taille en Ko :", tailles)
```
<!--sortie-->
```text
taille en Ko : {'png': 46, 'svg': 2090, 'svg rastérisé': 46, 'pdf': 300}
```
<!--sortie-->

**À retenir.** Un vectoriel pèse autant que le nombre d'objets : pour un nuage dense, on **rastérise** les points tout en gardant les axes et les textes vectoriels.

### Application 3.4 — seaborn : distribution, carte thermique et intervalle (section 3.1.7)

**Objectif.** Comparer les délais de livraison des trois transporteurs, repérer les retards par mois, puis distinguer l'incertitude d'une moyenne de la dispersion des observations.

**Étape 1 — Les délais par transporteur.** Le délai est le nombre de jours entre l'expédition et la livraison.

```python
liv["delai"] = (liv["date_livraison"] - liv["date_expedition"]).dt.days
g = sns.catplot(data=liv, x="transporteur", y="delai", kind="box", hue="transporteur", palette=[style.BLEU, style.ORANGE, style.AQUA], height=3.2, aspect=1.5, fliersize=2)
g.set_axis_labels("", "délai (jours)")
O.sauver(g.figure, "ch03-cah-delais.png")
print(liv.groupby("transporteur")["delai"].agg(["median", "mean", "max"]).round(1).to_string())
```
<!--sortie-->
```text
figure : ch03-cah-delais.png
                median  mean  max
transporteur                     
Transporteur A     3.0   3.6   10
Transporteur B     4.0   4.2   10
Transporteur C     5.0   5.0   10
```
<!--sortie-->

![Délais de livraison par transporteur (boîtes à moustaches).](figures/ch03-cah-delais.png)

**Étape 2 — Le taux de retard par mois et transporteur.** Une carte thermique avec les valeurs écrites dans les cases.

```python
retard = liv.pivot_table(index="transporteur", columns=liv["date_commande"].dt.month, values="retard", aggfunc="mean") * 100
fig, ax = plt.subplots(figsize=(7.4, 2.4))
sns.heatmap(retard, annot=True, fmt=".0f", cmap=style.SEQ, cbar=False, linewidths=0.5, ax=ax)
ax.set(xlabel="mois de la commande", ylabel=""); ax.grid(False); ax.set_title("Part des livraisons en retard (%) : décembre ressort", loc="left", fontweight="bold", fontsize=10)
O.sauver(fig, "ch03-cah-retards.png")
pire, mieux = retard.stack().idxmax(), retard.stack().idxmin()
print(f"pire case : {pire[0]}, mois {int(pire[1])} ({retard.stack().max():.0f} %) | meilleure : {mieux[0]}, mois {int(mieux[1])} ({retard.stack().min():.0f} %)")
```
<!--sortie-->
```text
figure : ch03-cah-retards.png
pire case : Transporteur C, mois 12 (85 %) | meilleure : Transporteur A, mois 4 (10 %)
```
<!--sortie-->

![Taux de retard par transporteur et par mois.](figures/ch03-cah-retards.png)

**Étape 3 — Un intervalle n'est pas une dispersion.** `sns.barplot` trace par défaut un intervalle de confiance de la moyenne ; avec `errorbar="sd"`, il trace l'écart-type. On lit les deux sur un même graphique.

```python
fig, (g1, g2) = plt.subplots(1, 2, figsize=(7, 2.9), sharey=True)
sns.barplot(data=liv, x="transporteur", y="delai", color=style.BLEU, ax=g1)
sns.barplot(data=liv, x="transporteur", y="delai", color=style.BLEU, errorbar="sd", ax=g2)
g1.set_title("intervalle de confiance de la moyenne"); g2.set_title("écart-type des livraisons"); g1.set(ylabel="délai (jours)"); g2.set(ylabel="")
for a in (g1, g2):
    a.set_xticks(range(3), ["A", "B", "C"]); a.set_xlabel("transporteur")
O.sauver(fig, "ch03-cah-ic-sd.png")
s = liv.groupby("transporteur")["delai"].agg(["mean", "std", "count"])
print((1.96 * s["std"] / np.sqrt(s["count"])).round(2).to_dict(), "| écarts-types :", s["std"].round(2).to_dict())
```
<!--sortie-->
```text
figure : ch03-cah-ic-sd.png
{'Transporteur A': 0.02, 'Transporteur B': 0.02, 'Transporteur C': 0.03} | écarts-types : {'Transporteur A': 1.02, 'Transporteur B': 1.0, 'Transporteur C': 1.0}
```
<!--sortie-->

![À gauche l'intervalle de la moyenne (minuscule), à droite l'écart-type (large).](figures/ch03-cah-ic-sd.png)

**À retenir.** Avec près de 20 000 livraisons, l'intervalle de la moyenne est minuscule : il dit que la moyenne est précise, pas que tous les colis arrivent au même moment. La légende doit nommer ce que la barre d'erreur représente.

### Application 3.5 — Une figure testée, et la même en R (sections 3.1.8 et 3.1.9)

**Objectif.** Enfermer un graphique dans une fonction, tester les données qu'il dessine, puis l'écrire en ggplot2.

**Étape 1 — La fonction et son test.** La fonction reçoit le tableau des jours et une année, et retourne la figure du chiffre d'affaires mensuel.

```python
def figure_mensuelle(jours, annee):
    d = jours[jours["annee"] == annee].groupby("mois")["chiffre_affaires"].sum() / 1000
    fig, ax = plt.subplots(figsize=(5.6, 3))
    ax.plot(d.index, d.values, color=style.BLEU, marker="o")
    ax.set(xticks=range(1, 13), ylabel="k€"); ax.set_title(f"Chiffre d'affaires {annee} : {fr(d.sum(), 0)} k€", loc="left", fontweight="bold")
    return fig

fig = figure_mensuelle(j, 2025)
tracé = fig.axes[0].lines[0].get_ydata()
attendu = j[j["annee"] == 2025].groupby("mois")["chiffre_affaires"].sum().to_numpy() / 1000
print("points tracés :", len(tracé), "| égaux au tableau :", np.allclose(tracé, attendu), "| titre :", fig.axes[0].get_title(loc="left"))
O.sauver(fig, "ch03-cah-test-mensuel.png")
```
<!--sortie-->
```text
points tracés : 12 | égaux au tableau : True | titre : Chiffre d'affaires 2025 : 1 325 k€
figure : ch03-cah-test-mensuel.png
```
<!--sortie-->

![La figure produite par la fonction testée.](figures/ch03-cah-test-mensuel.png)

**Étape 2 — La même chose en R.** On refait la série en ggplot2 et l'on compare le total au total Python.

```r
library(ggplot2)
jr <- read.csv(file.path(Sys.getenv("DONNEES"), "jours_exploitation.csv"))
jr$annee <- as.integer(substr(jr$date, 1, 4)); jr$mois <- as.integer(substr(jr$date, 6, 7))
d <- aggregate(chiffre_affaires ~ mois, data = jr[jr$annee == 2025, ], FUN = function(v) sum(v) / 1000)
p <- ggplot(d, aes(mois, chiffre_affaires)) + geom_line(color = "#2a78d6") + geom_point(color = "#2a78d6") +
  scale_x_continuous(breaks = 1:12) + labs(x = NULL, y = "k€") + theme_minimal()
ggsave(file.path(dirname(Sys.getenv("DONNEES")), "figures", "ch03-cah-ggplot-mensuel.png"), p, width = 5.6, height = 3, dpi = 200)
cat("total 2025 (k€) :", round(sum(d$chiffre_affaires), 1), "\n")
```
<!--sortie-->
```text
total 2025 (k€) : 1324.8 
```
<!--sortie-->

![La même série tracée avec ggplot2.](figures/ch03-cah-ggplot-mensuel.png)

```python
print("total 2025 (k€) côté Python :", round(attendu.sum(), 1))
```
<!--sortie-->
```text
total 2025 (k€) côté Python : 1324.8
```
<!--sortie-->

**À retenir.** Les deux langages donnent le **même total** : le test porte sur les nombres, pas sur l'apparence des deux figures.

### Application 3.6 — plotly : une page interactive (section 3.2)

**Objectif.** Construire une figure plotly avec une infobulle utile, vérifier sa structure, mesurer le poids de la page et la photographier.

```python
import plotly.express as px
cc = x[x["annee"] == 2025].groupby(["categorie", "canal"], as_index=False)["montant"].sum()
fig = px.bar(cc, x="categorie", y="montant", color="canal", color_discrete_map=O.COUL, template="simple_white", category_orders={"canal": O.CANAUX})
fig.update_traces(hovertemplate="<b>%{x}</b> — %{fullData.name}<br>%{y:,.0f} €<extra></extra>")
fig.update_layout(separators=", ", xaxis_title=None, yaxis_title="€, 2025", legend_title=None, title="Chiffre d'affaires 2025 par catégorie et par canal")
dossier = O.dossier_temp()
for nom, mode in (("autonome", True), ("cdn", "cdn")):
    chemin = os.path.join(dossier, nom + ".html"); fig.write_html(chemin, include_plotlyjs=mode)
    print(nom, ":", round(os.path.getsize(chemin) / 1024), "Ko")
print("séries :", [t.name for t in fig.data], "| une série par canal :", len(fig.data) == 3)
O.capturer_html(os.path.join(dossier, "autonome.html"), os.path.join(O.FIG, "ch03-cah-plotly.png"), 900, 460, survol=".bars .point >> nth=4")
O.supprimer_dossier(dossier)
```
<!--sortie-->
```text
autonome : 4713 Ko
cdn : 11 Ko
séries : ['Boutique', 'Site', 'Réseaux'] | une série par canal : True
capture existante : ch03-cah-plotly.png
```
<!--sortie-->

![Capture réelle de la page plotly : infobulle d'une barre empilée.](figures/ch03-cah-plotly.png)

Les barres sont **empilées** par défaut (`barmode="relative"`) : la hauteur totale se lit bien, la comparaison d'un canal d'une catégorie à l'autre beaucoup moins, sauf pour le canal du bas. Essayez `barmode="group"` et dites ce que vous gagnez et ce que vous perdez (exercice 3.11).

### Application 3.7 — Streamlit et Dash : tester sans navigateur (section 3.3)

**Objectif.** Écrire une toute petite application Streamlit, la tester avec `AppTest`, puis tester de la même façon la fonction de rappel d'une application Dash.

**Étape 1 — Streamlit.** L'application a un sélecteur de catégorie et deux chiffres.

```python
from streamlit.testing.v1 import AppTest
dossier = O.dossier_temp()
code = '''import os, pandas as pd, streamlit as st
d = os.environ["DONNEES"]
l = pd.read_csv(f"{d}/lignes_commande.csv").merge(pd.read_csv(f"{d}/produits.csv")[["id_produit", "categorie"]], on="id_produit")
cat = st.selectbox("Catégorie", sorted(l["categorie"].unique()))
v = l[l["categorie"] == cat]
st.metric("Chiffre d'affaires (€)", f"{v['montant'].sum():,.0f}".replace(",", " "))
st.metric("Lignes vendues", len(v))
'''
app = os.path.join(dossier, "mini.py"); open(app, "w").write(code)
at = AppTest.from_file(app, default_timeout=120).run()
print("première catégorie :", at.selectbox[0].value, [m.value for m in at.metric])
at.selectbox[0].select("Jardin").run()
lj = x[x["categorie"] == "Jardin"]
print("Jardin :", [m.value for m in at.metric], "| attendu :", fr(lj["montant"].sum(), 0), len(lj))
```
<!--sortie-->
```text
première catégorie : Bien-être ['324 037', '10347']
Jardin : ['970 379', '14977'] | attendu : 970 379 14977
```
<!--sortie-->

**Étape 2 — Dash.** On déclare une application avec une fonction de rappel, puis on **appelle la fonction directement**.

```python
from dash import Dash, dcc, html, Input, Output
ap = Dash(__name__)
ap.layout = html.Div([dcc.Dropdown(["Boutique", "Site", "Réseaux"], "Site", id="canal"), html.Div(id="sortie")])

@ap.callback(Output("sortie", "children"), Input("canal", "value"))
def maj(canal):
    return f"{canal} : {x[(x['canal'] == canal) & (x['annee'] == 2025)]['montant'].sum():,.0f} €".replace(",", " ")

print(maj("Site"), "|", maj("Réseaux"))
print("attendu :", fr(O.ca_canal(x)["Site"], 0), "|", fr(O.ca_canal(x)["Réseaux"], 0))
O.supprimer_dossier(dossier)
```
<!--sortie-->
```text
Site : 617 715 € | Réseaux : 146 074 €
attendu : 617 715 | 146 074
```
<!--sortie-->

**À retenir.** Dans les deux cas, le test vérifie le **calcul** sans lancer de serveur ni de navigateur ; la page elle-même se regarde à l'œil (exercice 3.14).

### Application 3.8 — Shiny : un graphe réactif qui ne recalcule qu'une fois (section 3.3.4)

**Objectif.** Vérifier avec `testServer` qu'une expression `reactive` est calculée **une seule fois** même si deux sorties la lisent.

```r
library(shiny)
d <- Sys.getenv("DONNEES")
l <- merge(read.csv(file.path(d, "lignes_commande.csv")), read.csv(file.path(d, "produits.csv"))[, c("id_produit", "categorie")], by = "id_produit")
calculs <- 0
serveur <- function(input, output, session) {
  sel <- reactive({ calculs <<- calculs + 1; l[l$categorie == input$categorie, ] })
  output$ca <- renderText(format(round(sum(sel()$montant)), big.mark = " "))
  output$n <- renderText(nrow(sel()))
}
testServer(serveur, {
  session$setInputs(categorie = "Jardin")
  cat("chiffre d'affaires :", output$ca, "| lignes :", output$n, "| calculs du filtre :", calculs, "\n")
  session$setInputs(categorie = "Cuisine")
  cat("chiffre d'affaires :", output$ca, "| lignes :", output$n, "| calculs du filtre :", calculs, "\n")
})
```
<!--sortie-->
```text
chiffre d'affaires : 970 379 | lignes : 14977 | calculs du filtre : 1 
chiffre d'affaires : 658 996 | lignes : 14750 | calculs du filtre : 2 
```
<!--sortie-->

Deux sorties lisent `sel()`, mais le filtre n'est calculé **qu'une fois par changement de catégorie** : c'est ce que « graphe réactif » veut dire.

### Application 3.9 — Cartes sur un plan fictif (section 3.4)

**Objectif.** Comparer les villes par nombre de clients et par nombre de clients pour 1 000 habitants, avec des cercles proportionnels, et voir ce que change la normalisation.

```python
v = O.ventes_villes(x)
v["clients"] = O.lire("clients.csv").groupby("ville").size()
v["clients_1000"] = v["clients"] / v["habitants"] * 1000
fig, axes = plt.subplots(1, 2, figsize=(9, 3.9))
for ax, col, titre in zip(axes, ("clients", "clients_1000"), ("nombre de clients", "clients pour 1 000 habitants")):
    ax.scatter(v["x_km"], v["y_km"], s=v[col] / v[col].max() * 700, color=style.BLEU, alpha=0.55, edgecolor="white")
    for ville, r in v.nlargest(3, col).iterrows():
        ax.annotate(ville, (r["x_km"], r["y_km"]), ha="center", va="center", fontsize=8)
    ax.set(xlim=(-5, 125), ylim=(-5, 95), aspect="equal", xticks=[], yticks=[]); ax.grid(False); ax.set_title(titre, loc="left", fontsize=10)
O.sauver(fig, "ch03-cah-cartes.png")
print("trois premières villes :", list(v.nlargest(3, "clients").index), "| par 1 000 habitants :", list(v.nlargest(3, "clients_1000").index))
```
<!--sortie-->
```text
figure : ch03-cah-cartes.png
trois premières villes : ['Ville A', 'Ville B', 'Ville C'] | par 1 000 habitants : ['Ville C', 'Ville D', 'Ville A']
```
<!--sortie-->

![Cercles proportionnels : à gauche le nombre de clients, à droite la densité de clients.](figures/ch03-cah-cartes.png)

Ville B sort du podium quand on normalise (Ville D y entre) : le nombre de clients suit la population, la densité mesure la **pénétration** de la boutique.

## Exercices

### Exercice 3.1 ⭐ — Trois couches (section 3.1.1)

Un graphique montre, pour chacun des 120 produits, le prix de vente (abscisse) et la quantité vendue en 2025 (ordonnée) ; les points sont colorés par catégorie et leur taille est proportionnelle au chiffre d'affaires du produit. Décrivez ce graphique selon les **trois couches** : données, esthétiques, géométrie. Combien d'attributs visuels sont utilisés ?

### Exercice 3.2 ⭐ — Critiquer et refaire (section 3.1.2)

Le code ci-dessous trace le chiffre d'affaires par canal avec cinq défauts, tous traités dans la section 3.1.2. **Listez les cinq défauts**, puis **refaites** le graphique en les corrigeant.

```python
ca = x[x["annee"] == 2025].groupby("canal")["montant"].sum()
fig, ax = plt.subplots()
ax.bar(ca.index, ca.values, color=["red", "green", "blue"])
ax.set_ylim(100000, ca.max() * 1.02)
ax.set_title("Graphique 1")
```

### Exercice 3.3 ⭐⭐ — Un titre qui dit le message, et qui reste vrai (section 3.1.3)

Pour la série mensuelle du chiffre d'affaires de 2025, écrivez en une phrase le message que vous voulez faire passer. Puis écrivez le titre **calculé** (avec `f"…"`) et ajoutez une **assertion** qui échoue si le message cesse d'être vrai (par exemple si le mois de pointe change). Pourquoi est-ce important quand le script sera rejoué sur les données du mois suivant ?

### Exercice 3.4 ⭐⭐ — Échelle commune ou libre ? (section 3.1.5)

Tracez le chiffre d'affaires 2025 de chacune des six catégories en six petits graphiques (par mois), d'abord avec `sharey=True`, puis avec `sharey=False`. Pour chaque version, écrivez la **question** à laquelle elle répond le mieux.

### Exercice 3.5 ⭐ — Un orange lisible (section 3.1.6)

Le rapport de contraste de l'orange de la palette sur le fond du livre est de 3,1 : suffisant pour une barre, insuffisant pour du texte (qui demande 4,5). Trouvez une version **assombrie** de l'orange dont le contraste dépasse 4,5, et dites pourquoi on n'écrit pas toutes les étiquettes avec la couleur pure de la série.

### Exercice 3.6 ⭐⭐ — Quel format pour quel usage ? (section 3.1.6)

Pour chacun des quatre usages suivants, choisissez PNG, SVG ou PDF et justifiez en une phrase : (a) une figure à insérer dans un courriel à la direction ; (b) un nuage de 200 000 points dans un rapport imprimé ; (c) une figure simple à agrandir sur une affiche ; (d) une figure pour une page web.

### Exercice 3.7 ⭐⭐ — Écrire la légende d'un intervalle (section 3.1.7)

Avec `sns.lineplot`, tracez la **moyenne mensuelle du nombre de commandes par jour** en 2025 (une valeur par jour, groupée par mois), avec la bande d'incertitude par défaut. Écrivez la **légende** qui dit ce que représente la bande, puis une seconde version avec `errorbar="sd"` et sa légende. Laquelle répond à « de combien varient les jours d'un même mois ? »

### Exercice 3.8 ⭐⭐ — Le test qui attrape une erreur invisible (section 3.1.8)

La fonction ci-dessous trie les valeurs mais pas les étiquettes : le graphique est **faux sans que rien ne se voie** à l'exécution. Écrivez le test qui l'attrape, puis corrigez la fonction.

```python
def barres_canaux(ca):
    fig, ax = plt.subplots()
    ax.bar(ca.index, ca.sort_values(ascending=False).values)
    return fig
```

### Exercice 3.9 ⭐⭐ — De matplotlib à ggplot2 (section 3.1.9)

Traduisez en R avec ggplot2 un histogramme des paniers 2025 (par commande), **un par canal** (trois petits histogrammes sur la même échelle), avec une ligne verticale à la médiane. Quel équivalent de `sharey=True` utilise-t-on ?

### Exercice 3.10 ⭐ — Même figure, deux niveaux (section 3.2.1)

Construisez avec `plotly.graph_objects` la courbe du chiffre d'affaires mensuel du canal Site. Comparez avec la version `plotly.express` : combien de séries dans chacune ? Quelle clé de `fig.to_dict()` contient la mise en page ?

### Exercice 3.11 ⭐⭐ — Une infobulle utile (section 3.2.2)

Écrivez un `hovertemplate` qui affiche, pour chaque barre du chiffre d'affaires par catégorie, le nom de la catégorie, le chiffre d'affaires en k€ et **sa part dans le total**. Vérifiez que les parts de toutes les barres somment à 100 %. Essayez ensuite `barmode="group"` pour la figure de l'application 3.6 et dites ce que vous gagnez et ce que vous perdez.

### Exercice 3.12 ⭐⭐ — Interactif ou statique ? (section 3.2.3)

Pour chaque situation, dites si une figure interactive est un bon choix, et pourquoi : (a) un rapport mensuel envoyé en PDF ; (b) un tableau de bord consulté chaque lundi par la gérante ; (c) une diapositive projetée en réunion ; (d) une page d'exploration pour l'analyste qui cherche les jours aberrants.

### Exercice 3.13 ⭐⭐ — Que rejoue Streamlit ? (section 3.3.2)

Une application Streamlit charge un fichier de 200 Mo (sans cache), affiche un sélecteur, puis un graphique filtré. L'utilisateur change quatre fois le sélecteur. Combien de fois le fichier est-il lu ? Que change `@st.cache_data` ? Qu'est-ce que ce modèle d'exécution a de plus simple et de plus coûteux que celui de Shiny ?

### Exercice 3.14 ⭐⭐⭐ — Le cas limite (section 3.3.3)

La fonction de rappel de l'application 3.7 (Dash) est appelée avec une liste de canaux. Écrivez une version qui reçoit une **liste vide** (l'utilisateur a tout décoché) : que se passe-t-il avec une version naïve ? Écrivez le test qui l'attrape, puis la version robuste qui affiche un message plutôt que de planter.

### Exercice 3.15 ⭐⭐ — Normaliser une carte (section 3.4)

Classez les villes par chiffre d'affaires 2025 puis par chiffre d'affaires **par habitant**. Combien de villes figurent dans les cinq premières des deux classements ? Quelle conclusion un lecteur de chaque classement tirerait-il ?

### Exercice 3.16 ⭐⭐⭐ — Le piège de la moyenne des taux (section 3.4)

On veut le chiffre d'affaires par habitant de chacune des quatre régions. Calculez-le de **deux façons** : la moyenne des rapports de chaque ville, et le rapport des totaux (chiffre d'affaires de la région divisé par ses habitants). Les résultats diffèrent-ils ? Laquelle est la bonne, et pourquoi ? Faut-il une carte ou des barres pour présenter le résultat ?

## Corrigés

### Corrigé 3.1

- **Données** : un tableau de 120 lignes (une par produit) avec le prix, la quantité vendue, la catégorie et le chiffre d'affaires.
- **Esthétiques** : prix → position horizontale ; quantité → position verticale ; catégorie → couleur ; chiffre d'affaires → taille. **Quatre attributs visuels**.
- **Géométrie** : des points (un par produit).

Le graphique est lisible mais chargé : la taille s'estime mal (voir le chapitre 1, section 1.1, sur la comparaison des aires). Si la taille ne sert pas la question posée, mieux vaut la retirer.

### Corrigé 3.2

Les cinq défauts : (1) des couleurs **sans sens** (rouge, vert, bleu : le rouge et le vert se confondent pour un daltonien, et aucune ne relie le canal à sa couleur du reste du document) ; (2) un **axe tronqué** qui commence à 100 000 : les barres ne partent plus de zéro et exagèrent les écarts ; (3) des barres **non triées** (ordre alphabétique) ; (4) **aucun chiffre** sur les barres ni unité sur l'axe ; (5) un titre qui **décrit** au lieu de dire le message (« Graphique 1 »). Le cadre et le quadrillage superflus sont un sixième défaut mineur.

```python
ca = x[x["annee"] == 2025].groupby("canal")["montant"].sum().sort_values(ascending=False) / 1000
fig, ax = plt.subplots(figsize=(5.6, 3.2))
barres = ax.bar(ca.index, ca.values, color=[O.COUL[c] for c in ca.index], width=0.62)
ax.bar_label(barres, labels=[f"{fr(v, 0)} k€" for v in ca.values], padding=3)
ax.set(ylim=(0, ca.max() * 1.15), yticks=[]); ax.grid(False); ax.spines["left"].set_visible(False)
ax.set_title(f"Le Site et la Boutique font {ca[['Site', 'Boutique']].sum() / ca.sum() * 100:.0f} % du chiffre d'affaires 2025", loc="left", fontweight="bold")
O.sauver(fig, "ch03-cah-c32.png")
print("axe tronqué à 100 000 : la barre des Réseaux paraît", round((ca.min() - 100) / (ca.max() - 100) * 100), "% de la plus grande, alors qu'elle en fait", round(ca.min() / ca.max() * 100), "%")
```
<!--sortie-->
```text
figure : ch03-cah-c32.png
axe tronqué à 100 000 : la barre des Réseaux paraît 9 % de la plus grande, alors qu'elle en fait 24 %
```
<!--sortie-->

![Le graphique corrigé.](figures/ch03-cah-c32.png)

### Corrigé 3.3

Message : « décembre est le mois de pointe de 2025 ». Le titre est calculé, et une assertion protège le message.

```python
d = j[j["annee"] == 2025].groupby("mois")["chiffre_affaires"].sum() / 1000
pic = d.idxmax()
assert pic == 12, "le message « décembre est le mois de pointe » n'est plus vrai"
titre = f"Le mois {pic} est le mois de pointe de 2025 : {fr(d.max(), 0)} k€, soit {fr(d.max() / d.drop(pic).mean(), 1)} fois un mois ordinaire"
fig, ax = plt.subplots(figsize=(5.8, 3))
ax.plot(d.index, d.values, color=style.BLEU, marker="o"); ax.set(xticks=range(1, 13), ylabel="k€")
ax.set_title(titre, loc="left", fontweight="bold", fontsize=9)
O.sauver(fig, "ch03-cah-c33.png")
print(titre)
```
<!--sortie-->
```text
figure : ch03-cah-c33.png
Le mois 12 est le mois de pointe de 2025 : 184 k€, soit 1,8 fois un mois ordinaire
```
<!--sortie-->

![Le titre calculé dit le message.](figures/ch03-cah-c33.png)

Sans l'assertion, un script rejoué sur d'autres données pourrait afficher « Le mois 11 est le mois de pointe » avec un commentaire écrit à la main qui parle encore de décembre : le graphique et le texte se contrediraient sans que personne le voie. L'assertion **échoue bruyamment** : c'est ce qu'on veut.

### Corrigé 3.4

```python
cm = x[x["annee"] == 2025].groupby(["categorie", x["date_commande"].dt.month])["montant"].sum().unstack(0) / 1000
fig, axes = plt.subplots(2, 6, figsize=(13, 4.2), sharex=True)
fig.subplots_adjust(wspace=0.35)
for k, c in enumerate(cm.columns):
    for l_ in (0, 1):
        axes[l_, k].plot(cm.index, cm[c], color=style.BLEU)
    axes[0, k].set_title(c, loc="left", fontsize=9, fontweight="bold")
    axes[1, k].set_ylim(0, cm.values.max() * 1.05); axes[1, k].set_xticks([1, 6, 12])
axes[0, 0].set_ylabel("échelle libre"); axes[1, 0].set_ylabel("échelle commune")
O.sauver(fig, "ch03-cah-c34.png")
print("maximum mensuel (k€) :", cm.max().round(1).to_dict())
```
<!--sortie-->
```text
figure : ch03-cah-c34.png
maximum mensuel (k€) : {'Bien-être': 18.0, 'Cuisine': 33.7, 'Décoration': 60.9, 'Jardin': 56.7, 'Maison': 44.7, 'Papeterie': 7.8}
```
<!--sortie-->

![Six catégories : échelle libre en haut, échelle commune en bas.](figures/ch03-cah-c34.png)

L'**échelle commune** répond à « quelle catégorie pèse le plus, et de combien ? » ; l'**échelle libre** répond à « la saison est-elle la même dans toutes les catégories ? » (on compare des formes). Ici les maxima mensuels vont de 8 k€ (Papeterie) à 61 k€ (Décoration) : avec l'échelle commune, la Papeterie est écrasée mais on voit qu'elle est petite ; avec l'échelle libre, on lit sa saison mais on croirait qu'elle pèse autant que les autres. Plus les catégories diffèrent en taille, plus le choix compte.

### Corrigé 3.5

```python
def lum(h):
    c = [int(h[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    c = [v / 12.92 if v <= 0.03928 else ((v + 0.055) / 1.055) ** 2.4 for v in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]

def contraste(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)

for f in (1.0, 0.8, 0.7, 0.6, 0.5):
    h = "#" + "".join(f"{int(int(style.ORANGE[i:i + 2], 16) * f):02x}" for i in (1, 3, 5))
    print(f"facteur {f:.1f} : {h} -> contraste {contraste(h, style.SURFACE):.1f}")
```
<!--sortie-->
```text
facteur 1.0 : #eb6834 -> contraste 3.1
facteur 0.8 : #bc5329 -> contraste 4.6
facteur 0.7 : #a44824 -> contraste 5.8
facteur 0.6 : #8d3e1f -> contraste 7.2
facteur 0.5 : #75341a -> contraste 9.0
```
<!--sortie-->

Dès 80 % de la teinte d'origine (`#bc5329`), le contraste atteint 4,6 : c'est la réponse minimale ; à 70 % (`#a44824`) il atteint 5,8, avec une marge de sécurité. On n'écrit pas toutes les étiquettes avec la couleur pure de la série parce que l'**orange pur est trop clair pour du texte** : une barre est un grand aplat, qu'un contraste de 3 suffit à distinguer, alors que de petites lettres exigent 4,5. Solution courante : colorer la **barre** avec la couleur pure et l'**étiquette** avec le gris foncé du texte, ou avec la version assombrie.

### Corrigé 3.6

(a) **PNG** : universel, léger pour une figure simple, lisible par tous les logiciels de courrier. (b) **PNG** (ou PDF avec `rasterized=True`) : 200 000 points en vectoriel donneraient un fichier énorme et lent ; l'image fixe garde la taille constante. (c) **SVG ou PDF** : le vectoriel reste net à n'importe quelle taille. (d) **SVG** pour un graphique simple (net sur tous les écrans, léger), **PNG** pour un graphique dense.

### Corrigé 3.7

```python
d = j[j["annee"] == 2025]
fig, (g1, g2) = plt.subplots(1, 2, figsize=(8, 3), sharey=True)
sns.lineplot(data=d, x="mois", y="nb_commandes", color=style.BLEU, ax=g1)
sns.lineplot(data=d, x="mois", y="nb_commandes", color=style.BLEU, errorbar="sd", ax=g2)
g1.set_title("bande : intervalle de confiance à 95 % de la moyenne", fontsize=9); g2.set_title("bande : écart-type des jours", fontsize=9)
for a in (g1, g2):
    a.set(xticks=range(1, 13), xlabel="mois", ylabel="commandes par jour")
O.sauver(fig, "ch03-cah-c37.png")
s = d[d["mois"] == 12]["nb_commandes"]
print("décembre : moyenne", round(s.mean(), 1), "| demi-largeur de l'intervalle", round(1.96 * s.std() / np.sqrt(len(s)), 1), "| écart-type", round(s.std(), 1))
```
<!--sortie-->
```text
figure : ch03-cah-c37.png
décembre : moyenne 59.8 | demi-largeur de l'intervalle 5.1 | écart-type 14.5
```
<!--sortie-->

![À gauche l'intervalle de la moyenne, à droite l'écart-type.](figures/ch03-cah-c37.png)

Légende de la version par défaut : « la ligne est le nombre moyen de commandes par jour ; la bande est l'**intervalle de confiance à 95 %** de cette moyenne (elle mesure la précision de la moyenne mensuelle, pas la variation des jours) ». Légende de la seconde : « la bande est **plus ou moins un écart-type** des commandes quotidiennes du mois ». C'est la **seconde** qui répond à « de combien varient les jours d'un même mois ? ».

### Corrigé 3.8

Le test compare les hauteurs des barres **à leurs étiquettes** : il attrape l'erreur d'une barre qui porte le nom d'un autre canal.

```python
def barres_canaux(ca):
    fig, ax = plt.subplots()
    ax.bar(ca.index, ca.sort_values(ascending=False).values)           # version fautive : valeurs triées, étiquettes non triées
    return fig

def barres_canaux_juste(ca):
    ca = ca.sort_values(ascending=False)
    fig, ax = plt.subplots()
    ax.bar(ca.index, ca.values)
    return fig

def lire_barres(fig):
    ax = fig.axes[0]
    return {t.get_text(): b.get_height() for t, b in zip(ax.get_xticklabels(), ax.patches)}

ca = x[x["annee"] == 2025].groupby("canal")["montant"].sum()
for nom, f in (("fautive", barres_canaux), ("corrigée", barres_canaux_juste)):
    fig = f(ca); fig.canvas.draw()
    lu = lire_barres(fig)
    print(nom, ": toutes les barres portent le bon chiffre :", all(np.isclose(lu[c], ca[c]) for c in lu))
    plt.close(fig)
```
<!--sortie-->
```text
fautive : toutes les barres portent le bon chiffre : False
corrigée : toutes les barres portent le bon chiffre : True
```
<!--sortie-->

La version fautive passe l'œil (trois barres, des étiquettes) mais échoue au test : une barre porte le chiffre d'un autre canal. C'est l'erreur la plus grave d'un graphique, précisément parce qu'elle est **invisible**.

### Corrigé 3.9

```r
library(ggplot2); library(dplyr, warn.conflicts = FALSE)
d <- Sys.getenv("DONNEES")
l <- read.csv(file.path(d, "lignes_commande.csv")); cm <- read.csv(file.path(d, "commandes.csv"))
pa <- inner_join(l, cm, by = "id_commande") |> filter(substr(date_commande, 1, 4) == "2025") |>
  group_by(id_commande, canal) |> summarise(panier = sum(montant), .groups = "drop")
med <- pa |> group_by(canal) |> summarise(mediane = median(panier))
p <- ggplot(pa, aes(panier)) + geom_histogram(binwidth = 20, fill = "#2a78d6") +
  geom_vline(data = med, aes(xintercept = mediane), color = "#eb6834") + facet_wrap(~ canal) + coord_cartesian(xlim = c(0, 700)) + labs(x = "panier (€)", y = "commandes") + theme_minimal()
ggsave(file.path(dirname(d), "figures", "ch03-cah-c39.png"), p, width = 7, height = 2.6, dpi = 200)
print(as.data.frame(med |> mutate(mediane = round(mediane, 1))))
```
<!--sortie-->
```text
     canal mediane
1 Boutique    82.0
2  Réseaux    81.2
3     Site    81.2
```
<!--sortie-->

![Trois histogrammes de paniers, une ligne à la médiane.](figures/ch03-cah-c39.png)

Dans `facet_wrap`, les échelles sont **communes par défaut** (`scales = "fixed"`), l'équivalent de `sharey=True` ; pour les libérer, on écrit `facet_wrap(~ canal, scales = "free_y")`.

### Corrigé 3.10

```python
import plotly.express as px
import plotly.graph_objects as go
site = x[x["canal"] == "Site"].groupby(x["date_commande"].dt.to_period("M").dt.to_timestamp())["montant"].sum().reset_index()
f_go = go.Figure(go.Scatter(x=site["date_commande"], y=site["montant"], mode="lines", line_color=style.ORANGE))
f_px = px.line(site, x="date_commande", y="montant")
print("séries : go", len(f_go.data), "| px", len(f_px.data), "| clés de to_dict :", sorted(f_go.to_dict()), "| mise en page : 'layout'")
print("mêmes ordonnées :", list(f_go.data[0].y) == list(f_px.data[0].y))
```
<!--sortie-->
```text
séries : go 1 | px 1 | clés de to_dict : ['data', 'layout'] | mise en page : 'layout'
mêmes ordonnées : True
```
<!--sortie-->

Chaque figure a une série ; la mise en page se trouve sous la clé `layout`. Avec `px`, la couleur n'est pas fixée (elle prend la couleur par défaut du gabarit) ; avec `go`, on la règle explicitement (`line_color`).

### Corrigé 3.11

```python
cat = x[x["annee"] == 2025].groupby("categorie", as_index=False)["montant"].sum()
cat["part"] = cat["montant"] / cat["montant"].sum() * 100
cat["k"] = cat["montant"] / 1000
fig = px.bar(cat.sort_values("k", ascending=False), x="categorie", y="k", custom_data=["part"], template="simple_white")
fig.update_traces(hovertemplate="<b>%{x}</b><br>%{y:,.0f} k€ — %{customdata[0]:.1f} % du total<extra></extra>", marker_color=style.BLEU)
fig.update_layout(separators=", ", xaxis_title=None, yaxis_title="k€", title="Chiffre d'affaires 2025 par catégorie")
print("somme des parts :", round(cat["part"].sum(), 6), "| infobulle de la première barre :", fig.data[0].hovertemplate[:40])
dossier = O.dossier_temp(); chemin = os.path.join(dossier, "cat.html"); fig.write_html(chemin, include_plotlyjs=True)
O.capturer_html(chemin, os.path.join(O.FIG, "ch03-cah-c311.png"), 800, 420, survol=".bars .point >> nth=0")
O.supprimer_dossier(dossier)
```
<!--sortie-->
```text
somme des parts : 100.0 | infobulle de la première barre : <b>%{x}</b><br>%{y:,.0f} k€ — %{customda
capture existante : ch03-cah-c311.png
```
<!--sortie-->

![Capture réelle : l'infobulle donne la valeur et la part.](figures/ch03-cah-c311.png)

Avec `barmode="group"` (barres côte à côte), on **gagne** la comparaison d'un canal d'une catégorie à l'autre (toutes les barres partent de zéro) ; on **perd** la lecture du total de la catégorie. Les barres **empilées** font l'inverse. Le bon choix dépend de la question : « combien au total ? » ou « quel canal domine ? ».

### Corrigé 3.12

(a) **Non** : un PDF n'a pas de survol ; la figure doit se suffire (étiquettes directes, titre qui dit le message). (b) **Oui** : un lecteur régulier explore par canal et par mois ; mais le message essentiel reste visible sans geste. (c) **Non** : on ne clique pas en réunion ; une image nette, avec le fait marquant annoté. (d) **Oui** : l'analyste cherche, survole et zoome ; c'est l'usage où l'interactivité rapporte le plus. Dans tous les cas où l'on **livre**, on garde une image de ce qui a été montré.

### Corrigé 3.13

Le script se **rejoue en entier** à chaque changement : sans cache, le fichier est lu **cinq fois** (une fois au chargement et une fois après chacun des quatre changements). Avec `@st.cache_data`, il n'est lu qu'**une fois** (le résultat est gardé et réutilisé). Le modèle est plus **simple** (un script linéaire, pas de graphe de dépendances à déclarer) mais plus **coûteux** : à chaque clic, tout ce qui n'est pas en cache est recalculé, alors que Shiny ne recalcule que les expressions qui dépendent de l'entrée modifiée.

### Corrigé 3.14

Avec une liste vide, la fonction naïve filtre un tableau vide, et `.sum()` d'un tableau vide donne 0 : l'application affiche « 0 € » sans signaler que l'utilisateur n'a rien sélectionné. Selon le graphique, un tableau vide peut aussi lever une erreur. Le test appelle la fonction avec la liste vide.

```python
def maj_robuste(canaux):
    if not canaux:
        return "Choisissez au moins un canal."
    s = x[x["canal"].isin(canaux) & (x["annee"] == 2025)]
    return f"{', '.join(canaux)} : {s['montant'].sum():,.0f} €".replace(",", " ")

def maj_naive(canaux):
    s = x[x["canal"].isin(canaux) & (x["annee"] == 2025)]
    return f"{s['montant'].sum():,.0f} €"

print("naïve, liste vide :", maj_naive([]), "| robuste, liste vide :", maj_robuste([]))
assert maj_robuste([]) != "0 €"
print("robuste, un canal :", maj_robuste(["Site"]))
```
<!--sortie-->
```text
naïve, liste vide : 0 € | robuste, liste vide : Choisissez au moins un canal.
robuste, un canal : Site : 617 715 €
```
<!--sortie-->

La version naïve ne plante pas mais **ment par omission** : un « 0 € » affiché en gros laisse croire que les ventes sont nulles. La version robuste dit ce qui se passe. Un tableau de bord doit prévoir l'état « rien de sélectionné » comme les autres.

### Corrigé 3.15

```python
v = O.ventes_villes(x)
r1, r2 = v["ca"].rank(ascending=False), v["par_habitant"].rank(ascending=False)
commun = sorted(set(r1[r1 <= 5].index) & set(r2[r2 <= 5].index))
print("cinq premières en chiffre d'affaires :", list(r1.nsmallest(5).index))
print("cinq premières par habitant         :", list(r2.nsmallest(5).index))
print("villes en commun :", len(commun), commun)
```
<!--sortie-->
```text
cinq premières en chiffre d'affaires : ['Ville A', 'Ville B', 'Ville C', 'Ville D', 'Ville E']
cinq premières par habitant         : ['Ville C', 'Ville D', 'Ville A', 'Ville E', 'Ville I']
villes en commun : 4 ['Ville A', 'Ville C', 'Ville D', 'Ville E']
```
<!--sortie-->

Quatre villes sur cinq sont communes aux deux classements (A, C, D et E) : la différence tient à **Ville B**, deuxième en chiffre d'affaires mais absente du classement par habitant (170 000 habitants, environ 1 € chacun), remplacée par **Ville I**. Le lecteur du classement en **chiffre d'affaires** voit en Ville B un marché majeur ; celui du classement **par habitant** y voit un marché à peine exploité. Les deux ont raison pour leur question ; l'erreur est de présenter l'un comme s'il répondait à l'autre.

### Corrigé 3.16

```python
par_ville = v.groupby("region").agg(ca=("ca", "sum"), habitants=("habitants", "sum"), moy_taux=("par_habitant", "mean"))
par_ville["rapport_totaux"] = par_ville["ca"] / par_ville["habitants"]
print(par_ville[["moy_taux", "rapport_totaux"]].round(2).to_string())
fig, ax = plt.subplots(figsize=(5, 2.8))
tri = par_ville["rapport_totaux"].sort_values()
ax.barh(tri.index, tri.values, color=style.BLEU, height=0.55); ax.grid(axis="y", visible=False); ax.set_axisbelow(True); ax.set(xlabel="€ par habitant, 2025")
ax.set_title("Chiffre d'affaires par habitant et par région", loc="left", fontweight="bold", fontsize=10)
O.sauver(fig, "ch03-cah-c316.png")
print("écart maximal entre les deux méthodes :", round((par_ville["moy_taux"] - par_ville["rapport_totaux"]).abs().max(), 2), "€")
```
<!--sortie-->
```text
          moy_taux  rapport_totaux
region                            
Région 1      2.01            1.42
Région 2      1.07            0.69
Région 3      3.92            2.01
Région 4      0.53            0.30
figure : ch03-cah-c316.png
écart maximal entre les deux méthodes : 1.92 €
```
<!--sortie-->

![Chiffre d'affaires par habitant et par région, calculé par le rapport des totaux.](figures/ch03-cah-c316.png)

La **bonne** méthode est le **rapport des totaux** : le chiffre d'affaires de la région divisé par sa population. La moyenne des rapports donne le même poids à une petite ville et à une grande, alors qu'elles n'ont pas le même nombre d'habitants : c'est une moyenne **non pondérée** de taux. Ici le classement des régions est le même, mais les valeurs sont presque **doublées** (3,92 € contre 2,01 € pour la Région 3) : on aurait annoncé un chiffre faux. Pour quatre régions, des **barres** suffisent et valent mieux : le classement est immédiat et les valeurs sont écrites ; une carte de quatre zones n'apporterait que la position, dont la question ne parle pas.
