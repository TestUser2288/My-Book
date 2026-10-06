## 7.3 Shiny : un graphe de dépendances

Streamlit rejoue un script ; **Shiny** (créé pour R, aujourd'hui disponible aussi pour Python) fait autre chose. Le développeur ne décrit pas une suite d'instructions, il décrit **qui dépend de quoi** ; le système se charge de ne recalculer que ce qui est périmé. Cette section construit ce mécanisme en miniature, le compare à Streamlit **en comptant les calculs réellement refaits**, puis donne des critères de choix.

### 7.3.1 Un autre modèle mental

Une application Shiny contient trois sortes d'éléments.

| Élément | Rôle | Exemple dans l'application de ventes |
|---|---|---|
| **Entrée** (*input*) | une valeur fixée par l'utilisateur | l'année, la fenêtre de lissage |
| **Calcul réactif** (*reactive*) | un résultat intermédiaire qui **dépend** d'entrées ou d'autres calculs ; il est **mémorisé** | charger, filtrer, agréger |
| **Sortie** (*output*) | ce qui s'affiche à l'écran | le graphique lissé |

Les liens se déduisent **automatiquement** : quand un calcul lit une entrée ou un autre calcul, le système note la dépendance. Quand une entrée change, il marque comme **périmés** tous ceux qui en dépendent, directement ou non, puis recalcule seulement les sorties visibles, et seulement les calculs dont elles ont besoin.

Voici le même type d'application en Shiny pour Python (extrait **non exécuté** : la bibliothèque n'est pas installée dans l'environnement de rédaction, et ce livre n'écrit sous les blocs que des sorties réellement obtenues).

```python noexec
from shiny import App, reactive, render, ui

app_ui = ui.page_sidebar(
    ui.sidebar(ui.input_slider("recence", "Jours depuis la dernière commande", 0, 365, 60)),
    ui.output_text("risque"))

def server(input, output, session):
    @reactive.calc                      # calcul mémorisé, recalculé seulement si `recence` change
    def score():
        return input.recence() / 365
    @render.text                        # sortie : se met à jour quand `score` est périmé
    def risque():
        return f"{100 * score():.1f} %"

app = App(app_ui, server)
```

Trois remarques pour comparer avec Streamlit. Les entrées s'**appellent** comme des fonctions (`input.recence()`), et c'est cet appel qui enregistre la dépendance. La disposition de l'écran (`app_ui`) est **séparée** du calcul (`server`), alors que Streamlit les mélange dans un même script. Et un calcul décoré par `@reactive.calc` joue un rôle comparable à celui d'un `@st.cache_data` bien réglé, mais **sans que l'on déclare les arguments** : le système sait ce qui a changé.

> 💡 **Shiny pour R ou pour Python ?** Les deux partagent les mêmes idées (entrées, calculs réactifs, sorties) ; la version R est la plus ancienne, la version Python la plus récente. Le bon critère n'est pas la mode mais **le langage du modèle** : notre modèle de résiliation est en Python (LightGBM), l'écrire en R obligerait à le réimplémenter ou à faire dialoguer les deux langages. Pour une équipe d'analystes qui travaille en R, c'est l'inverse.

### 7.3.2 Un graphe réactif en miniature

Pour comprendre le mécanisme, le plus sûr est de le construire. Un **noeud** est soit une valeur d'entrée, soit un calcul. Le point essentiel est dans `__call__` : quand un calcul en cours en **lit** un autre, il s'inscrit comme son lecteur.

```python
class Noeud:
    """Une entrée (f=None) ou un calcul qui dépend d'autres noeuds."""
    actif = None                                 # le noeud en train de se calculer
    def __init__(self, f=None, valeur=None):
        self.f, self.valeur, self.valide = f, valeur, f is None
        self.lecteurs = set()                    # ceux qui m'ont lu
    def __call__(self):
        if Noeud.actif is not None:
            self.lecteurs.add(Noeud.actif)       # on enregistre la dépendance
        if not self.valide:                      # paresseux : calcul à la demande
            avant, Noeud.actif = Noeud.actif, self
            self.valeur, self.valide = self.f(), True
            Noeud.actif = avant
        return self.valeur
```

Il manque la propagation du « périmé » : quand un noeud change, tous ses lecteurs, et les lecteurs de leurs lecteurs, doivent être invalidés.

```python
def invalider(self):
    """Marque les lecteurs de ce noeud (et leurs lecteurs) comme périmés."""
    self.valide = self.f is None                 # une entrée reste valide, un calcul non
    lecteurs, self.lecteurs = self.lecteurs, set()
    for n in lecteurs:
        if n.valide:
            n.invalider()
Noeud.invalider = invalider
```

Reste le côté « application » : une **sortie** est un noeud que l'on rafraîchit systématiquement, et une **entrée** n'invalide ses lecteurs que si sa valeur a **réellement changé**.

```python
SORTIES = []
def sortie(f):
    n = Noeud(f); SORTIES.append(n); return n

def entree(n, valeur):
    if valeur != n.valeur:                       # même valeur : rien à faire
        n.valeur = valeur
        n.invalider()

def rafraichir():
    for s in SORTIES:
        if not s.valide:
            s()
```

Une trentaine de lignes suffisent pour les trois propriétés qui définissent le modèle réactif : les dépendances sont **découvertes à l'exécution**, les calculs sont **paresseux** (rien n'est calculé tant que personne ne le demande) et **mémorisés** (ils ne sont refaits que s'ils sont périmés).

> ⚠️ **Ce que ce jouet ne fait pas.** Un vrai système réactif gère aussi les erreurs, l'annulation d'un calcul en cours, plusieurs utilisateurs, l'ordre précis des mises à jour et les dépendances qui disparaissent d'un calcul à l'autre. Ce n'est qu'un moyen de **comprendre** le principe, pas de le remplacer.

### 7.3.3 Même scénario, quatre mises en œuvre

Reprenons l'application de ventes de la section 7.2 (charger le fichier, filtrer sur l'année, agréger par semaine, lisser) et écrivons-la avec notre miniature. Chaque étape annonce sa propre exécution à un compteur. Les fonctions décrivent les calculs ; les noeuds `charger`, `filtre` et `semaine`, créés à la dernière ligne, les enveloppent.

```python hide
APPELS = {k: 0 for k in ETAPES}
def compte(etape):
    APPELS[etape] += 1
```

```python
annee, fenetre = Noeud(valeur=2025), Noeud(valeur=4)
def lire():     compte("charger"); return pd.read_csv(os.environ["APP_VENTES"], parse_dates=["date"])
def filtrer():  compte("filtrer"); d = charger(); return d[d["date"].dt.year == annee()]
def agreger():  compte("agreger"); return filtre().set_index("date")["ventes"].resample("W").sum()
def lisser():   compte("lisser");  return semaine().rolling(fenetre(), min_periods=1).mean()
charger, filtre, semaine = Noeud(lire), Noeud(filtrer), Noeud(agreger)
graphique = sortie(lisser)
```

Même séquence d'interactions que pour Streamlit : démarrage, trois déplacements du curseur de lissage, changement d'année.

```python hide
def mesurer_mini():
    for k in APPELS: APPELS[k] = 0
    entree(annee, 2025); entree(fenetre, 4)
    lignes, prec = [], dict(APPELS)
    rafraichir()
    lignes.append([APPELS[k] for k in ETAPES])
    for cible, v in [(fenetre, 2), (fenetre, 6), (fenetre, 9), (annee, 2024)]:
        prec = dict(APPELS)
        entree(cible, v); rafraichir()
        lignes.append([APPELS[k] - prec[k] for k in ETAPES])
    return np.array(lignes)
MESURES["Graphe réactif (miniature)"] = mesurer_mini()
```

Il reste la même application en **vrai Shiny pour R**, dont le comportement est testable sans navigateur grâce à `testServer`, l'équivalent R de `AppTest`. Le serveur déclare trois calculs réactifs et une sortie ; un compteur est incrémenté à chaque exécution.

```r
serveur <- function(input, output, session) {
  donnees <- reactive({ compte("charger"); read.csv(Sys.getenv("APP_VENTES")) })
  annee <- reactive({ compte("filtrer"); d <- donnees(); d[substr(d$date, 1, 4) == input$annee, ] })
  hebdo <- reactive({ compte("agreger"); d <- annee()
                      tapply(d$ventes, cut(as.Date(d$date), "week"), sum) })
  output$graphique <- renderText({
    compte("lisser"); k <- input$fenetre
    lisse <- stats::filter(hebdo(), rep(1 / k, k), sides = 1)
    sprintf("%d semaines", length(lisse))
  })
}
```

```r hide
suppressMessages(library(shiny))
n <- c(charger = 0, filtrer = 0, agreger = 0, lisser = 0)
compte <- function(etape) n[etape] <<- n[etape] + 1
trace <- NULL
testServer(serveur, {
  session$setInputs(annee = "2025", fenetre = 4)
  invisible(output$graphique); trace <<- rbind(trace, n)
  for (f in c(2, 6, 9)) {
    prec <- n; session$setInputs(fenetre = f); invisible(output$graphique); trace <<- rbind(trace, n - prec)
  }
  prec <- n; session$setInputs(annee = "2024"); invisible(output$graphique); trace <<- rbind(trace, n - prec)
})
write.csv(trace, file.path(Sys.getenv("CH7_TMP"), "trace_r.csv"), row.names = FALSE)
cat("total R :", sum(trace), "\n")
```
<!--sortie-->
```text
total R : 10 
```

```python hide-code
tr_r = pd.read_csv(os.path.join(TMP, "trace_r.csv"))[ETAPES].to_numpy()
MESURES["Shiny pour R"] = tr_r
tab = pd.DataFrame({nom.replace(" (miniature)", ""): m.sum(axis=1) for nom, m in MESURES.items()}, index=INTERACTIONS)
tab.loc["TOTAL"] = tab.sum()
print(tab.to_string())
ident = bool((MESURES["Streamlit avec cache"] == MESURES["Graphe réactif (miniature)"]).all() and (MESURES["Shiny pour R"] == MESURES["Graphe réactif (miniature)"]).all())
print("matrices étape par étape identiques (cache, miniature, R) :", ident)
```
<!--sortie-->
```text
            Streamlit sans cache  Streamlit avec cache  Graphe réactif  Shiny pour R
démarrage                      4                     4               4             4
lissage 2                      4                     1               1             1
lissage 6                      4                     1               1             1
lissage 9                      4                     1               1             1
année 2024                     4                     3               3             3
TOTAL                         20                    10              10            10
matrices étape par étape identiques (cache, miniature, R) : True
```

```python hide
NUM("tot_mini", MESURES["Graphe réactif (miniature)"].sum(), 0)
NUM("tot_r", MESURES["Shiny pour R"].sum(), 0)
```
<!--sortie-->
```text
NUM tot_mini 10
NUM tot_r 10
```

Étapes réellement exécutées à chaque interaction (somme des quatre étapes). Le résultat est net : le graphe réactif, sans que le développeur ait écrit une ligne de cache, refait **10 étapes** (miniature) et **10** (vrai Shiny pour R) pour la séquence où Streamlit sans cache en refait 20. Le détail étape par étape est **identique** à celui de Streamlit avec cache : changer la fenêtre de lissage ne recalcule que le lissage, changer l'année recalcule le filtrage, l'agrégation et le lissage, mais pas le chargement.

```python hide
fig, axes = plt.subplots(2, 2, figsize=(10.2, 4.6))
noms = ["charger", "filtrer", "agréger", "lisser"]
choix = [("Streamlit sans cache", "Streamlit sans cache"), ("Graphe réactif", "Graphe réactif (miniature)")]
for i, (titre_ligne, cle) in enumerate(choix):
    for j, (inter, titre_col) in enumerate([(2, "on déplace le curseur de lissage"), (4, "on change l'année")]):
        ax = axes[i, j]; ax.set_axis_off(); ax.set_xlim(0, 10); ax.set_ylim(0, 3.2)
        faits = MESURES[cle][inter] > 0
        for k, nom in enumerate(noms):
            x0 = 0.4 + 2.4 * k
            ax.add_patch(plt.Rectangle((x0, 0.55), 1.9, 1.0, fc=ORANGE if faits[k] else "#f0efec", ec=ENCRE2 if faits[k] else style.AXE, lw=1.2))
            ax.text(x0 + 0.95, 1.05, nom, ha="center", va="center", fontsize=9, color=ENCRE if faits[k] else ENCRE2)
            if k < 3:
                ax.annotate("", xy=(x0 + 2.4, 1.05), xytext=(x0 + 1.9, 1.05), arrowprops=dict(arrowstyle="->", color=MUET))
        cible = 3 if inter == 2 else 1
        ax.annotate("", xy=(0.4 + 2.4 * cible + 0.95, 1.6), xytext=(0.4 + 2.4 * cible + 0.95, 2.45), arrowprops=dict(arrowstyle="->", color=BLEU, lw=1.6))
        ax.text(0.4 + 2.4 * cible + 0.95, 2.7, "lissage" if inter == 2 else "année", ha="center", color=BLEU, fontsize=9)
        ax.set_title(f"{titre_ligne} : {titre_col}", fontsize=9, loc="left")
fig.text(0.5, -0.02, "Orange : l'étape est ré-exécutée. Gris : le résultat précédent est réutilisé.", ha="center", color=ENCRE2, fontsize=9)
fig.tight_layout()
style.save(fig, "ch07-graphe-reactif.png")
```
<!--sortie-->
```text
figure : ch07-graphe-reactif.png
```

![Ce qui est recalculé après deux types d'interaction. En haut, Streamlit sans cache : les quatre étapes sont refaites à chaque fois. En bas, graphe réactif (ou Streamlit avec cache) : seules les étapes situées en aval de l'entrée modifiée sont refaites. Schéma construit à partir des comptages mesurés.](figures/ch07-graphe-reactif.png)

> 🧭 **Lecture.** Il ne s'agit pas de ce qui est affiché (les quatre mises en œuvre décrivent le même calcul), mais de **ce qui est recalculé**, donc de **responsabilité**. Dans Streamlit, c'est au développeur de décider quoi mettre en cache et de veiller à ce que les arguments permettent de reconnaître un calcul déjà fait. Dans Shiny, la dépendance est découverte par le système, mais le développeur doit penser son application **en graphe** dès le départ.

### 7.3.4 Retarder le calcul : bouton et contexte réactif

Quand le calcul est long, on ne veut pas qu'il démarre à chaque mouvement de curseur. Streamlit propose le formulaire (section 7.2.3) ; Shiny propose un calcul **déclenché par un événement**, `eventReactive`, qui ne s'exécute que lorsqu'un bouton est cliqué et ignore les entrées qui changent entre-temps. Mesurons-le : le curseur est déplacé quatre fois, puis le bouton est cliqué, puis le curseur est encore déplacé, puis un deuxième clic.

```r
k <- 0
serveur2 <- function(input, output, session) {
  resultat <- eventReactive(input$calculer, { k <<- k + 1; input$fenetre * 2 })
  output$sortie <- renderText(resultat())
}
testServer(serveur2, {
  etat <- function(titre, r = output$sortie) cat(sprintf("%-18s: %s | calculs : %d\n", titre, r, k))
  for (f in c(4, 2, 6, 9)) session$setInputs(fenetre = f)
  etat("avant clic", tryCatch(output$sortie, error = function(e) "(aucun résultat)"))
  session$setInputs(calculer = 1);  etat("après le clic")
  session$setInputs(fenetre = 12);  etat("curseur déplacé")
  session$setInputs(calculer = 2);  etat("deuxième clic")
})
```
<!--sortie-->
```text
avant clic        : (aucun résultat) | calculs : 0
après le clic    : 18 | calculs : 1
curseur déplacé : 18 | calculs : 1
deuxième clic    : 24 | calculs : 2
```

Avant le premier clic, **aucun** calcul n'a eu lieu et aucun résultat n'est affiché ; au clic, le calcul utilise la **dernière** valeur du curseur (9, soit 18) ; déplacer ensuite le curseur ne change **rien** à l'écran tant que l'on ne clique pas à nouveau. C'est le comportement attendu d'un bouton « Calculer » ; d'après la documentation, un formulaire de Streamlit (section 7.2.3) répond au même besoin.

Dernière particularité du modèle réactif : une valeur réactive ne peut être lue **que dans un contexte réactif** (un calcul ou une sortie). Le système refuse de la lire ailleurs, parce qu'il ne saurait pas qui prévenir en cas de changement.

```r
valeur <- reactiveVal(1)
essai <- tryCatch(valeur(), error = function(e) strsplit(conditionMessage(e), "\n")[[1]][1])
cat("hors contexte réactif :", essai, "\n")
cat("avec isolate()        :", isolate(valeur()), "\n")
```
<!--sortie-->
```text
hors contexte réactif : Operation not allowed without an active reactive context. 
avec isolate()        : 1 
```

Lire une valeur **hors** contexte réactif est donc une erreur ; `isolate()` permet de la lire **sans** créer de dépendance, ce qui est précisément ce que l'on souhaite lorsqu'un calcul doit utiliser une valeur sans être relancé quand elle change. Ce message d'erreur signale typiquement une lecture d'entrée placée hors d'un calcul réactif, ce que l'on écrit facilement par habitude de scripteur.

### 7.3.5 Choisir entre Streamlit et Shiny

Le tableau suivant résume des **appréciations générales** (aucune n'est une mesure, hormis le comptage vu plus haut).

| Critère | Streamlit | Shiny (R ou Python) |
|---|---|---|
| **Modèle** | un script rejoué de haut en bas | un graphe de dépendances |
| **Prise en main** | très rapide : on écrit comme un script | un peu plus longue : il faut penser en entrées, calculs, sorties |
| **Calculs coûteux** | à protéger **à la main** (cache) | mémorisés **par construction** |
| **Interface complexe** (plusieurs onglets dépendants, tableaux de bord riches) | possible, mais le rejeu complique l'état | le graphe est fait pour cela |
| **Langage du modèle** | Python | R ou Python selon la version |
| **Test sans navigateur** | `AppTest` | `testServer` (R) |
| **Idéal pour** | une démonstration rapide d'un modèle Python | un tableau de bord interactif de longue durée, ou une équipe R |

Il n'y a pas de gagnant universel. **Pour la démonstration du modèle de résiliation à la gérante**, Streamlit convient : une seule page, un calcul modeste, aucune dépendance entre plusieurs écrans. Pour un tableau de bord où quinze filtres s'enchaînent, le modèle réactif évite des soucis d'état ; pour une équipe qui écrit déjà tout en R, Shiny pour R est le choix naturel. Dans tous les cas, **le code du modèle reste en dehors de l'interface**, dans un module que l'on peut tester seul : c'est ce qui permet de changer d'outil sans tout réécrire.

> ✅ **À retenir.**
> - Streamlit **rejoue un script**, Shiny **suit un graphe** : même résultat, mais deux manières de ne pas recalculer.
> - Un système réactif tient en peu de lignes : dépendances **découvertes à l'exécution**, calculs **paresseux** et **mémorisés**, invalidation **en cascade**.
> - Nos mesures donnent 20 étapes pour Streamlit sans cache, 10 pour Streamlit avec cache, 10 pour la miniature et 10 pour Shiny pour R.
> - Un calcul déclenché par un bouton (`eventReactive`, formulaire) évite de relancer à chaque mouvement de curseur.
> - Le choix dépend du **langage du modèle**, de la **complexité** de l'écran et de **l'équipe**, pas d'une supériorité technique.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : application 7.5, exercices 7.8 à 7.10.

```
```