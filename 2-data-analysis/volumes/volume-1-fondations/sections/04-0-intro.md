# Chapitre 4 : Python et R pour l'analyse

> « Un calcul que l'on sait refaire d'un clic vaut mieux qu'un calcul parfait que l'on ne refera jamais. »

La gérante vous arrête dans le couloir, un lundi matin :

> — Chaque lundi, je veux le même tableau : les ventes de la semaine par canal, comparées à la même semaine de l'an dernier. Jusqu'ici, une collègue (qui a quitté la boutique) le refaisait à la main dans un classeur, en une heure, avec une chance sur trois de se tromper de ligne. Peux-tu l'automatiser ?

Vous avez déjà deux outils pour répondre : le tableur (chapitre 2) et le langage SQL (chapitre 3). Ce chapitre ajoute le troisième, celui qui fait le plus gagner de temps quand une analyse **se répète** ou **grossit** : un langage de programmation pensé pour les données. Deux sont couramment utilisés par les analystes : **Python**, avec la bibliothèque **pandas**, et **R**, avec l'ensemble de paquets appelé **tidyverse**. Nous apprenons les deux côte à côte, sur le même problème, avec les mêmes chiffres à l'arrivée.

## Le chemin de ce chapitre

- **4.1 Les fondamentaux de pandas** : une table de données dans Python (le *DataFrame*), la lire, la sélectionner, la filtrer, la compléter.
- **4.2 Les fondamentaux du tidyverse** : les mêmes gestes en R, avec les verbes de `dplyr` et le tube `|>`.
- **4.3 Lire, filtrer, regrouper, restructurer** : un export de caisse désordonné remis en état, des agrégats, des jointures, des tableaux croisés, et enfin **le tableau du lundi** de la gérante.
- **4.4 Notebooks d'analyse** : un document qui mêle texte, code et résultats, et les précautions à prendre pour qu'il soit reproductible.
- **4.5 ➕ R : ggplot2 et Shiny** : la grammaire des graphiques et une application interactive.
- **4.6 ➕ Python : NumPy, polars, rapports avec Jupyter** : le moteur de calcul sous pandas, une alternative plus rapide, et des rapports automatiques.

> 🧭 **Parcours essentiel.** Les sections 4.1 à 4.4 suffisent pour la suite du volume. Les sections 4.5 et 4.6, marquées ➕, élargissent la boîte à outils : lisez-les quand le besoin se présente.

## Pourquoi un langage, alors qu'Excel et SQL existent ?

Le tableur est excellent pour regarder les données, essayer une idée, produire un tableau que quelqu'un d'autre retouchera. SQL est excellent pour interroger de **gros volumes** rangés dans une base. Un langage de programmation apporte trois choses de plus.

- **La répétition sans effort.** Un programme est une recette écrite : on la rejoue le lundi suivant, ou sur un autre fichier, sans refaire les gestes. Une erreur corrigée dans la recette est corrigée pour toujours.
- **La traçabilité.** Le programme **dit** ce qui a été fait, ligne par ligne : quel fichier lu, quelles lignes écartées, quelles colonnes calculées. Un collègue, ou vous dans six mois, peut le relire et le contester. Un clic dans un menu ne laisse aucune trace.
- **L'étendue.** Nettoyer un texte, ajuster un modèle, tracer cent graphiques, lire dix fichiers d'un coup : ce qui est pénible dans un tableur tient en quelques lignes.

Le prix à payer est une marche d'entrée : il faut apprendre une syntaxe. Ce chapitre la rend la plus douce possible, en n'apprenant du langage que ce dont un analyste se sert pour **manipuler des tables**. Il ne remplace pas un cours de programmation, et n'en a pas l'ambition.

## Python ou R ?

La question revient toujours, et la réponse honnête est : **les deux font très bien le travail**, et la différence tient plus aux habitudes de l'entourage qu'aux capacités.

| | Python (pandas) | R (tidyverse) |
|---|---|---|
| Origine | langage généraliste, devenu langage de la donnée | langage conçu par des statisticiens |
| Points forts | un seul langage pour l'analyse, l'automatisation, le web, l'apprentissage automatique | statistique, graphiques (`ggplot2`), rapports, très bonne lisibilité des enchaînements |
| Syntaxe pour manipuler une table | des **méthodes** enchaînées avec des points : `table.query(...).groupby(...)` | des **verbes** reliés par un tube : `filter(...)`, `group_by(...)`, `summarise(...)` |
| Écosystème rencontré | équipes de données, informatique, industrie | recherche, santé, enquêtes, statistique publique |

Dans un poste d'analyste, vous rencontrerez les deux. Savoir lire l'un quand on écrit l'autre est un vrai atout, et les concepts sont les mêmes : **sélectionner, filtrer, calculer, regrouper, joindre, restructurer**. Vous verrez qu'une fois un geste compris dans un langage, on le retrouve dans l'autre en quelques minutes.

## Comment lire les blocs de ce chapitre

Chaque notion est montrée **deux fois** : un bloc Python (avec pandas), puis un bloc R (avec le tidyverse). Les deux blocs répondent à la même question, et **leurs résultats coïncident** : c'est la **vérification croisée**, un réflexe d'analyste que nous cultivons tout au long du volume. Quand deux outils indépendants donnent le même chiffre, on a une bonne raison de lui faire confiance ; quand ils diffèrent, on a trouvé quelque chose à comprendre. Pour que cette comparaison ne soit pas qu'une affirmation, un bloc caché la fait réellement, et le livre en affiche le verdict : « identique au résultat de pandas : TRUE ».

Une première illustration, avant d'entrer dans le détail : le chiffre d'affaires de 2025, calculé par chaque langage. Python lit deux fichiers, les relie par le numéro de commande et additionne les montants de l'année.

```python hide
import os, sys
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
import outils_ch04 as O

pd.set_option("display.width", 100)
pd.set_option("display.max_columns", 12)
O.ouvrir_pont()
```

```r hide
options(tidyverse.quiet = TRUE, width = 100, pillar.width = 100)
library(tidyverse)
pont <- function(nom) read_csv(file.path(Sys.getenv("CH4_TMP"), paste0(nom, ".csv")), show_col_types = FALSE)
verifier <- function(r, nom, nd = 1) {
  p <- as.data.frame(pont(nom)); r <- as.data.frame(r)
  ok <- identical(dim(r), dim(p)) && all(mapply(function(a, b) {
    if (is.numeric(a) && is.numeric(b)) isTRUE(all.equal(round(a, nd), round(b, nd), tolerance = 1e-6)) else identical(as.character(a), as.character(b))
  }, r, p))
  cat("identique au résultat de pandas :", ok, "\n")
  invisible(ok)
}
```

```python
lignes = pd.read_csv("donnees/lignes_commande.csv")
commandes = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
ventes = lignes.merge(commandes, on="id_commande")
ca_2025 = ventes.loc[ventes["date_commande"].dt.year == 2025, "montant"].sum()
print(round(ca_2025, 2))
```
<!--sortie-->
```text
1324763.72
```

R fait la même chose, avec un tube `|>` qui se lit « et ensuite » : on lit les deux fichiers, on les relie, on garde 2025, on additionne.

```r
ventes <- read_csv("donnees/lignes_commande.csv", show_col_types = FALSE) |>
  left_join(read_csv("donnees/commandes.csv", show_col_types = FALSE), by = "id_commande")
ca <- ventes |> filter(year(date_commande) == 2025) |> summarise(ca = sum(montant)) |> pull(ca)
cat(sprintf("%.2f", ca), "\n")
```
<!--sortie-->
```text
1324763.72 
```

```python hide
O.pont_ecrire(pd.DataFrame({"ca": [round(ca_2025, 2)]}), "ca_2025")
```

```r hide-code
verifier(tibble(ca = round(ca, 2)), "ca_2025", nd = 2)
```
<!--sortie-->
```text
identique au résultat de pandas : TRUE 
```

Les deux langages donnent le même chiffre d'affaires pour 2025, à l'euro et au centime près. Ce petit programme contient déjà l'essentiel de ce chapitre : lire, relier, filtrer, additionner. Il suffit maintenant de **comprendre chaque pas** et de savoir l'enchaîner.

> 📦 **Les données du chapitre.** Elles viennent de la boutique, **simulée** (les données sont fictives, générées avec des graines fixes) : `clients.csv` (6 000 clients), `produits.csv` (120 produits), `commandes.csv` (36 395 commandes de 2023 à 2025), `lignes_commande.csv` (une ligne par produit commandé, avec la quantité, le prix et la remise), `retours.csv`, `jours_exploitation.csv` (un jour par ligne : commandes, chiffre d'affaires, météo, promotion) et `export_caisse_brut.csv`, un export de caisse **désordonné** que nous remettrons en état en 4.3. Les fichiers sont dans le dossier `donnees/` ; la description complète est en tête du volume.
