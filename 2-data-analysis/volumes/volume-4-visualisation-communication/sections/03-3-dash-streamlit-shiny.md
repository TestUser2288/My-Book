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

```python noexec
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

```python noexec
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

```python noexec
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

```python noexec
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

```r noexec
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

```r noexec
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
