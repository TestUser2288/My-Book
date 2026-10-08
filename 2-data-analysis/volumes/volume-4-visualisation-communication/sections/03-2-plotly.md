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
