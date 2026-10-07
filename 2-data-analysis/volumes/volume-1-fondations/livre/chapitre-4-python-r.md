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


```text
identique au résultat de pandas : TRUE 
```

Les deux langages donnent le même chiffre d'affaires pour 2025, à l'euro et au centime près. Ce petit programme contient déjà l'essentiel de ce chapitre : lire, relier, filtrer, additionner. Il suffit maintenant de **comprendre chaque pas** et de savoir l'enchaîner.

> 📦 **Les données du chapitre.** Elles viennent de la boutique, **simulée** (les données sont fictives, générées avec des graines fixes) : `clients.csv` (6 000 clients), `produits.csv` (120 produits), `commandes.csv` (36 395 commandes de 2023 à 2025), `lignes_commande.csv` (une ligne par produit commandé, avec la quantité, le prix et la remise), `retours.csv`, `jours_exploitation.csv` (un jour par ligne : commandes, chiffre d'affaires, météo, promotion) et `export_caisse_brut.csv`, un export de caisse **désordonné** que nous remettrons en état en 4.3. Les fichiers sont dans le dossier `donnees/` ; la description complète est en tête du volume.


## 4.1 Les fondamentaux de pandas

**pandas** est la bibliothèque de Python qui sait manipuler des tables : lire un fichier, trier, filtrer, calculer de nouvelles colonnes, regrouper. Cette section en donne les gestes de base, un par un, sur les commandes de la boutique. Elle commence par quelques mots de Python, juste ce qu'il faut pour lire les exemples sans se perdre.

### 4.1.1 Python en dix minutes

Python est un langage où l'on **donne des noms à des valeurs** (des *variables*), puis où l'on calcule avec ces noms. Le signe `=` n'est pas une égalité mathématique : il range une valeur sous un nom. Tout ce qui suit un `#` est un commentaire, ignoré par l'ordinateur.

```python
prix = 19.9                 # un nombre décimal
quantite = 3                # un nombre entier
total = prix * quantite
print(total)
print(round(total, 2))
```
<!--sortie-->
```text
59.699999999999996
59.7
```

Le premier résultat étonne : l'ordinateur calcule en binaire, et la plupart des décimaux ne s'y écrivent pas exactement, d'où un résidu minuscule. Pour **afficher** un montant, on arrondit avec `round`. Ce détail explique pourquoi, dans tout le chapitre, nos montants sont arrondis à deux décimales avant d'être affichés ou comparés.

Deux structures reviennent sans cesse. Une **liste** range des éléments dans l'ordre, entre crochets ; on en prend un par sa position, **en commençant à zéro**. Un **dictionnaire** range des paires « clé : valeur » entre accolades ; on retrouve une valeur par sa clé. Une **fonction** est une recette à laquelle on donne un nom : `def` la définit, `return` renvoie le résultat, et l'indentation (quatre espaces) délimite son contenu.

```python
canaux = ["Boutique", "Site", "Réseaux"]
remises = {"SOLDES": 0.20, "BIENVENUE": 0.10, "FIDELITE": 0.05}

def prix_remise(prix, code):
    return prix * (1 - remises.get(code, 0))     # sans code connu : remise 0

print(canaux[0], len(canaux), remises["SOLDES"])
print(round(prix_remise(49.9, "FIDELITE"), 2), round(prix_remise(49.9, "AUCUN"), 2))
```
<!--sortie-->
```text
Boutique 3 0.2
47.4 49.9
```

Enfin, Python ne connaît au départ qu'une petite partie de ce qu'il sait faire : pour le reste, on **importe** des bibliothèques. La ligne `import pandas as pd` charge pandas et lui donne le surnom `pd`, que tout le monde utilise. Chaque fonction de la bibliothèque s'appelle ensuite par `pd.nom_de_la_fonction`.

> 🧭 **En pratique.** Vous n'avez pas besoin de maîtriser davantage de Python pour la suite : on se sert surtout de pandas, et ses gestes s'apprennent en les pratiquant. Quand un message d'erreur apparaît, lisez sa **dernière ligne** : elle dit presque toujours ce qui ne va pas (un nom mal orthographié, une parenthèse oubliée).

### 4.1.2 Le DataFrame et la Series

Dans pandas, une table s'appelle un **DataFrame** : des lignes (les observations), des colonnes (les variables), chaque colonne ayant **un seul type**. Une colonne prise isolément est une **Series**. Le gabarit de lecture est toujours le même : `pd.read_csv("fichier.csv")` renvoie un DataFrame.

```python
commandes = pd.read_csv("donnees/commandes.csv")
print(commandes.shape)
print(commandes.head(3))
```
<!--sortie-->
```text
(36395, 7)
   id_commande date_commande  heure  id_client     canal   mode_livraison code_promo
0            1    2023-01-01  15:35       2637      Site         Domicile        NaN
1            2    2023-01-01  16:32         96  Boutique  Retrait magasin        NaN
2            3    2023-01-01  18:07       3490  Boutique  Retrait magasin        NaN
```

`shape` donne le nombre de lignes et de colonnes ; `head(3)` montre les trois premières lignes (sans argument, cinq). Regardez toujours vos données après les avoir lues : ce petit coup d'œil détecte la moitié des problèmes. Le **type** de chaque colonne se lit avec `dtypes`.

```python
print(commandes.dtypes)
```
<!--sortie-->
```text
id_commande       int64
date_commande       str
heure               str
id_client         int64
canal               str
mode_livraison      str
code_promo          str
dtype: object
```

Les colonnes numériques sont de type `int64` (entiers) ou `float64` (décimaux). Les textes sont de type `str`, depuis la version 3 de pandas ; dans les versions plus anciennes, vous verriez `object`, et un bloc de code écrit pour l'une fonctionne presque toujours avec l'autre. Remarquez que `date_commande` est lue comme **du texte** : pandas ne devine pas qu'il s'agit de dates. Nous allons le lui dire.

### 4.1.3 Lire un fichier : les arguments qui comptent

`read_csv` accepte des dizaines d'arguments. Une poignée suffit presque toujours.

| Argument | À quoi il sert | Exemple |
|---|---|---|
| `sep` | le séparateur de colonnes | `sep=";"` (fichiers « à la française ») |
| `decimal` | le signe décimal | `decimal=","` |
| `encoding` | le codage des caractères accentués | `encoding="cp1252"` (anciens fichiers Windows) |
| `parse_dates` | les colonnes à lire comme des dates | `parse_dates=["date_commande"]` |
| `dtype` | forcer le type d'une colonne | `dtype={"id_client": "str"}` |
| `usecols`, `nrows` | ne lire que certaines colonnes, ou les premières lignes | `usecols=["id_ligne", "montant"]`, `nrows=1000` |
| `na_values` | les textes à traiter comme « manquant » | `na_values=["n/a", "-"]` |

On range donc les dates dans le bon type dès la lecture. Voici le chargement de toutes les tables dont nous aurons besoin dans ce chapitre.

```python
commandes = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
lignes = pd.read_csv("donnees/lignes_commande.csv")
produits = pd.read_csv("donnees/produits.csv")
clients = pd.read_csv("donnees/clients.csv", parse_dates=["date_inscription"])
retours = pd.read_csv("donnees/retours.csv", parse_dates=["date_retour"])
jours = pd.read_csv("donnees/jours_exploitation.csv", parse_dates=["date"])
print({nom: len(t) for nom, t in [("commandes", commandes), ("lignes", lignes), ("clients", clients), ("retours", retours)]})
print(commandes["date_commande"].dtype)
```
<!--sortie-->
```text
{'commandes': 36395, 'lignes': 83905, 'clients': 6000, 'retours': 5002}
datetime64[us]
```

Le type affiché pour la date, `datetime64`, est celui des **dates et heures** : on peut désormais en extraire l'année, le mois, le jour de la semaine, ou les comparer. Un type bien choisi à la lecture évite des heures de travail ensuite.

> ⚠️ **Piège : un identifiant n'est pas un nombre.** Le numéro d'un client ou d'une commande se lit comme un entier, mais ne se somme pas et ne se moyenne pas : « le numéro moyen des clients » n'a aucun sens. Quand un identifiant commence par des zéros (`00123`), la lecture comme entier les supprime : forcez alors `dtype="str"`. La section 5.1 reviendra sur cette distinction entre types de données.

### 4.1.4 Sélectionner : colonnes, lignes, cellules

Il y a trois façons de désigner une partie d'une table. Les **crochets** sélectionnent des **colonnes** : un nom donne une Series, une liste de noms donne un DataFrame.

```python
canal = commandes["canal"]                        # une colonne : une Series
extrait = commandes[["id_commande", "canal"]]     # deux colonnes : un DataFrame
print(type(canal).__name__, extrait.shape)
```
<!--sortie-->
```text
Series (36395, 2)
```

`.loc` sélectionne par **étiquette** (le nom des lignes et des colonnes) ; `.iloc` sélectionne par **position** (le rang, en commençant à zéro). Les deux se ressemblent et se comportent **différemment** sur un point : avec `.loc`, la borne de fin est **incluse** ; avec `.iloc`, elle est **exclue**.

```python
print(commandes.loc[0:2, ["id_commande", "canal"]])
print(commandes.iloc[0:2, [0, 4]])
```
<!--sortie-->
```text
   id_commande     canal
0            1      Site
1            2  Boutique
2            3  Boutique
   id_commande     canal
0            1      Site
1            2  Boutique
```

La première commande renvoie trois lignes (les étiquettes 0, 1 et 2), la seconde deux lignes (les positions 0 et 1). C'est l'une des sources d'erreur les plus fréquentes des débutants : en cas de doute, comptez les lignes obtenues.

### 4.1.5 Filtrer : garder les lignes qui répondent à une condition

Filtrer, c'est garder les lignes pour lesquelles une condition est vraie. On écrit la condition comme un calcul, qui produit une colonne de vrais et de faux, et on la passe entre crochets. Pour combiner plusieurs conditions, on utilise `&` (et), `|` (ou) et `~` (non), **en entourant chaque condition de parenthèses** quand on les écrit en une seule expression.

Combien de commandes passées sur le Site en 2025 avec le code `SOLDES` ?

```python
est_site = commandes["canal"] == "Site"
en_2025 = commandes["date_commande"].dt.year == 2025
avec_soldes = commandes["code_promo"] == "SOLDES"
print(len(commandes[est_site & en_2025 & avec_soldes]))
```
<!--sortie-->
```text
495
```

Trois conditions, nommées une à une, se relisent mieux qu'une seule ligne interminable. La méthode `query` permet d'écrire le même filtre sous forme de texte, souvent plus lisible ; `isin` teste l'appartenance à une liste ; `between` teste l'appartenance à un intervalle (bornes incluses).

```python
n_query = len(commandes.query("canal == 'Site' and date_commande >= '2025-01-01' and code_promo == 'SOLDES'"))
n_isin = commandes["canal"].isin(["Boutique", "Réseaux"]).sum()
n_nov = commandes["date_commande"].between("2025-11-01", "2025-11-30").sum()
print(n_query, n_isin, n_nov)
```
<!--sortie-->
```text
495 20932 1509
```

On retrouve les 495 commandes du premier filtre (par une autre écriture), puis 20 932 commandes passées en boutique ou sur les réseaux, et 1 509 commandes en novembre 2025. Les mêmes comptages en R sont faits en section 4.2.

### 4.1.6 Colonnes calculées et tri

Créer une colonne, c'est lui donner un nom et un calcul qui porte sur d'autres colonnes, ligne par ligne. La méthode `assign` le fait sans modifier la table d'origine : elle renvoie une **nouvelle** table. Sur les lignes de commande, calculons le montant avant remise, la remise en euros, puis vérifions que le fichier est cohérent.

```python
l2 = lignes.assign(
    brut=lambda d: d["quantite"] * d["prix_unitaire"],
    remise_eur=lambda d: d["brut"] * d["remise_pct"] / 100,
)
print((l2["brut"] - l2["remise_eur"] - l2["montant"]).abs().max().round(2))
```
<!--sortie-->
```text
0.01
```

La notation `lambda d: …` se lit « pour une table `d`, calculer … » : elle permet à la seconde colonne d'utiliser la première, tout juste créée. Le plus grand écart vaut un centime : `montant = quantité × prix × (1 − remise)` pour **toutes** les lignes, à l'arrondi du montant au centime près. Le fichier est cohérent, et nous pourrons nous fier à `montant`.

Trier se fait par `sort_values`, en précisant la colonne et le sens. Les cinq lignes les plus chères :

```python
print(l2.sort_values("montant", ascending=False).head(5)[["id_ligne", "quantite", "prix_unitaire", "remise_pct", "montant"]])
```
<!--sortie-->
```text
       id_ligne  quantite  prix_unitaire  remise_pct  montant
68711     68712         4         157.49           0   629.96
78316     78317         4         157.49           0   629.96
70637     70638         4         157.49           0   629.96
64160     64161         4         157.49           0   629.96
23327     23328         4         152.90           0   611.60
```

### 4.1.7 Valeurs manquantes et comptages

Une cellule vide est lue comme **`NaN`** (« not a number »), la valeur manquante de pandas. `isna()` la détecte, et la somme des vrais donne le nombre de manquants par colonne.

```python
print(commandes.isna().sum())
```
<!--sortie-->
```text
id_commande           0
date_commande         0
heure                 0
id_client             0
canal                 0
mode_livraison        0
code_promo        30652
dtype: int64
```

Seul `code_promo` a des manquants, pour une raison **métier** : une cellule vide signifie « pas de code promotionnel ». Ce n'est pas une donnée perdue. Pour compter proprement, on le dit explicitement avec `fillna`, puis `value_counts` donne la fréquence de chaque valeur ; avec `normalize=True`, des proportions.

```python
codes = commandes["code_promo"].fillna("aucun")
print((codes.value_counts(normalize=True) * 100).round(1))
```
<!--sortie-->
```text
code_promo
aucun        84.2
SOLDES        8.3
FIDELITE      6.7
BIENVENUE     0.9
Name: proportion, dtype: float64
```

> ⚠️ **Piège : `NaN` n'est égal à rien, pas même à lui-même.** `commandes["code_promo"] == np.nan` ne renvoie que des faux : pour tester un manquant, utilisez toujours `isna()` (ou `notna()`). Par ailleurs, la plupart des calculs (somme, moyenne) **ignorent** les `NaN` : une moyenne sur une colonne à moitié vide est une moyenne sur la moitié des lignes, sans le dire. Interrogez toujours le nombre de manquants **avant** de calculer.

### 4.1.8 La méthode chaînée

Chaque méthode de pandas renvoie une table, sur laquelle on peut appliquer la suivante : on peut donc **enchaîner** les étapes, une par ligne, dans des parenthèses. Le résultat se lit de haut en bas comme une recette. Quelle est, selon le canal, la part des commandes de 2025 passées avec un code promotionnel ?

```python
part_promo = (
    commandes
    .loc[commandes["date_commande"].dt.year == 2025]
    .assign(avec_code=lambda d: d["code_promo"].notna())
    .groupby("canal")["avec_code"].mean()
    .mul(100).round(1)
)
print(part_promo)
```
<!--sortie-->
```text
canal
Boutique    15.1
Réseaux     15.0
Site        15.8
Name: avec_code, dtype: float64
```

La part est d'environ 15 % dans les trois canaux : les codes ne sont pas l'affaire d'un canal en particulier. Chaque ligne du programme est une étape : on garde 2025, on ajoute un indicateur « a un code », on regroupe par canal, on prend la moyenne de l'indicateur (la moyenne de vrais et de faux est la proportion de vrais), on exprime en pourcentage. Ce style est précisément celui que le tidyverse rend plus naturel encore, comme on le voit en 4.2.

Une dernière propriété mérite d'être connue : dans pandas 3, un extrait de table est toujours **une copie indépendante**. Modifier l'extrait ne touche jamais la table d'origine, ce qui supprime une classe entière d'erreurs qui hantait les versions précédentes.

```python
extrait = commandes.loc[commandes["canal"] == "Site"].copy()
extrait["canal"] = "X"
print(commandes["canal"].unique().tolist())
```
<!--sortie-->
```text
['Site', 'Boutique', 'Réseaux']
```

> ✅ **À retenir.** Une table pandas est un *DataFrame* ; on **lit** en précisant séparateur, décimale, encodage et colonnes de dates ; on **sélectionne** avec `[]`, `.loc` (étiquettes, fin incluse) et `.iloc` (positions, fin exclue) ; on **filtre** avec des conditions combinées par `&`, `|`, `~` ; on **calcule** avec `assign` ; on **compte** avec `value_counts` ; on **enchaîne** les étapes entre parenthèses. Un manquant se détecte par `isna()`, jamais par `==`.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 et 4.2, exercices 4.1 à 4.5.


## 4.2 Les fondamentaux du tidyverse

Le **tidyverse** est un ensemble de paquets R qui partagent une même philosophie : des tables bien rangées (une ligne par observation, une colonne par variable) et des **verbes** simples, qui se lisent comme des phrases et s'enchaînent avec un **tube**. Cette section reprend, en R, les gestes de la section 4.1, sur les mêmes données et avec les mêmes résultats.

### 4.2.1 R, les paquets et le tube

R est, comme Python, un langage où l'on range des valeurs sous des noms. Deux différences se remarquent tout de suite : l'affectation s'écrit avec une flèche `<-` (`x <- 5`), et les positions **commencent à 1** (le premier élément d'une liste est le numéro 1, pas le numéro 0). Les structures de base sont les **vecteurs** (`c(...)`, qui peuvent être nommés) et les **fonctions**.

```r
canaux <- c("Boutique", "Site", "Réseaux")
remises <- c(SOLDES = 0.20, BIENVENUE = 0.10, FIDELITE = 0.05)
prix_remise <- function(prix, code) prix * (1 - ifelse(code %in% names(remises), remises[code], 0))
cat(canaux[1], length(canaux), remises["SOLDES"], "\n")
cat(round(prix_remise(49.9, "FIDELITE"), 2), round(prix_remise(49.9, "AUCUN"), 2), "\n")
```
<!--sortie-->
```text
Boutique 3 0.2 
47.4 49.9 
```

On retrouve exactement les valeurs du programme Python de 4.1.1 (la fonction `ifelse` joue le rôle de `get` avec une valeur par défaut). Pour le reste, R vient avec des **paquets** que l'on installe une fois (`install.packages("tidyverse")`) et que l'on charge à chaque session avec `library`. Le paquet `tidyverse` en charge plusieurs d'un coup : `readr` pour lire, `dplyr` pour manipuler les tables, `tidyr` pour les restructurer, `ggplot2` pour les graphiques, `stringr` pour le texte, `lubridate` pour les dates, `forcats` pour les catégories.

```r
library(tidyverse)
commandes <- read_csv("donnees/commandes.csv", show_col_types = FALSE)
commandes |> head(3)
```
<!--sortie-->
```text
# A tibble: 3 × 7
  id_commande date_commande heure  id_client canal    mode_livraison  code_promo
        <dbl> <date>        <time>     <dbl> <chr>    <chr>           <chr>     
1           1 2023-01-01    15:35       2637 Site     Domicile        <NA>      
2           2 2023-01-01    16:32         96 Boutique Retrait magasin <NA>      
3           3 2023-01-01    18:07       3490 Boutique Retrait magasin <NA>      
```

(Les messages de chargement des paquets ne sont pas reproduits dans ce livre.) Une table R s'appelle un **tibble** : un data frame dont l'affichage est plus lisible, qui indique le type de chaque colonne sous son nom (`<dbl>` pour un décimal, `<chr>` pour un texte, `<date>` pour une date) et qui n'imprime que ce qui tient à l'écran. Deux remarques sur ce résultat. D'abord, **`readr` reconnaît les dates au format ISO** (`2023-01-01`) dès la lecture, alors que pandas demande `parse_dates`. Ensuite, un tibble n'a pas de numéros de ligne : la table n'a pas d'« index » comme celle de pandas.

Le **tube** `|>` est l'outil central de R pour l'analyse. Il prend ce qui est à sa gauche et le donne comme premier argument à la fonction de droite : `commandes |> head(3)` équivaut à `head(commandes, 3)`. Un enchaînement de verbes se lit alors du haut vers le bas, **« et ensuite »** : « prends les commandes, **et ensuite** garde celles de 2025, **et ensuite** regroupe par canal… ».

### 4.2.2 Lire avec readr

`read_csv` lit un fichier séparé par des virgules ; `read_csv2` lit un fichier « à la française » (séparateur point-virgule, virgule décimale). Pour un contrôle plus fin, l'argument `locale` règle le signe décimal et l'encodage, et `col_types` force le type des colonnes. Chargeons toutes les tables du chapitre, puis jetons un coup d'œil avec `glimpse`, l'équivalent de `dtypes` plus quelques valeurs.

```r
lignes <- read_csv("donnees/lignes_commande.csv", show_col_types = FALSE)
produits <- read_csv("donnees/produits.csv", show_col_types = FALSE)
clients <- read_csv("donnees/clients.csv", show_col_types = FALSE)
retours <- read_csv("donnees/retours.csv", show_col_types = FALSE)
jours <- read_csv("donnees/jours_exploitation.csv", show_col_types = FALSE)
cat(nrow(commandes), nrow(lignes), nrow(clients), nrow(retours), "\n")
glimpse(commandes)
```
<!--sortie-->
```text
36395 83905 6000 5002 
Rows: 36,395
Columns: 7
$ id_commande    <dbl> 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, …
$ date_commande  <date> 2023-01-01, 2023-01-01, 2023-01-01, 2023-01-01, 2023-01-01, 2023-01-01, 20…
$ heure          <time> 15:35:00, 16:32:00, 18:07:00, 17:10:00, 12:00:00, 19:32:00, 18:10:00, 15:5…
$ id_client      <dbl> 2637, 96, 3490, 743, 2931, 3017, 1418, 1038, 2689, 995, 3722, 4054, 495, 65…
$ canal          <chr> "Site", "Boutique", "Boutique", "Boutique", "Boutique", "Boutique", "Boutiq…
$ mode_livraison <chr> "Domicile", "Retrait magasin", "Retrait magasin", "Retrait magasin", "Retra…
$ code_promo     <chr> NA, NA, NA, NA, NA, NA, "FIDELITE", NA, "FIDELITE", NA, NA, "SOLDES", NA, N…
```

Les quatre nombres de lignes sont ceux que pandas a donnés en 4.1.3. Le résumé de `glimpse` liste chaque colonne avec son type et ses premières valeurs : c'est le réflexe de « regarder ses données » avant toute chose.


```text
identique au résultat de pandas : TRUE 
```

### 4.2.3 Les verbes de dplyr

Cinq verbes couvrent l'essentiel du travail quotidien sur une table, auxquels s'ajoutent `count` et `left_join`.

| Verbe | Rôle | Équivalent pandas |
|---|---|---|
| `select()` | choisir des colonnes | `df[["a", "b"]]` |
| `filter()` | garder des lignes | `df[condition]`, `df.query()` |
| `mutate()` | créer ou modifier des colonnes | `df.assign()` |
| `arrange()` | trier | `df.sort_values()` |
| `summarise()` avec `group_by()` | résumer, par groupes | `df.groupby().agg()` |
| `count()` | compter les lignes par valeur | `df.value_counts()` |
| `left_join()` | relier deux tables | `df.merge(how="left")` |

Commençons par `filter`. Les conditions séparées par une virgule sont **toutes** exigées (un « et ») ; `%in%` teste l'appartenance à un vecteur et `between` l'appartenance à un intervalle. Voici les trois comptages de 4.1.5.

```r
n1 <- commandes |> filter(canal == "Site", year(date_commande) == 2025, code_promo == "SOLDES") |> nrow()
n2 <- commandes |> filter(canal %in% c("Boutique", "Réseaux")) |> nrow()
n3 <- commandes |> filter(between(date_commande, as.Date("2025-11-01"), as.Date("2025-11-30"))) |> nrow()
cat(n1, n2, n3, "\n")
```
<!--sortie-->
```text
495 20932 1509 
```

```text
identique au résultat de pandas : TRUE 
```

Trois nombres identiques à ceux de pandas (495, 20 932 et 1 509). Notez deux différences d'écriture. R sait qu'une valeur manquante dans une condition donne ni vrai ni faux et **écarte** la ligne, tandis que pandas traite `NaN == "SOLDES"` comme faux : le résultat est le même. Et `mutate` permet à une colonne d'utiliser **immédiatement** celle qui vient d'être créée, sans la notation `lambda` de pandas.

```r
l2 <- lignes |> mutate(brut = quantite * prix_unitaire, remise_eur = brut * remise_pct / 100)
cat(round(max(abs(l2$brut - l2$remise_eur - l2$montant)), 2), "\n")
l2 |> arrange(desc(montant)) |> select(id_ligne, quantite, prix_unitaire, remise_pct, montant) |> head(5)
```
<!--sortie-->
```text
0.01 
# A tibble: 5 × 5
  id_ligne quantite prix_unitaire remise_pct montant
     <dbl>    <dbl>         <dbl>      <dbl>   <dbl>
1    64161        4          157.          0    630.
2    68712        4          157.          0    630.
3    70638        4          157.          0    630.
4    78317        4          157.          0    630.
5    10446        4          153.          0    612.
```

Le tri décroissant s'écrit `desc()`, et `select` choisit les colonnes à afficher : on retrouve les cinq lignes les plus chères de 4.1.6 (le tibble n'affiche que trois chiffres significatifs, d'où `157.` pour 157,49 : l'**affichage** est arrondi, pas la valeur). Reste le couple `group_by` et `summarise`, qui reproduit le groupement de 4.1.8 : la part des commandes de 2025 passées avec un code promotionnel, par canal.

```r
part_promo_r <- commandes |>
  filter(year(date_commande) == 2025) |>
  group_by(canal) |>
  summarise(part_promo = round(100 * mean(!is.na(code_promo)), 1))
part_promo_r
```
<!--sortie-->
```text
# A tibble: 3 × 2
  canal    part_promo
  <chr>         <dbl>
1 Boutique       15.1
2 Réseaux        15  
3 Site           15.8
```

```text
identique au résultat de pandas : TRUE 
```

Le `!` signifie « non » : `!is.na(code_promo)` est vrai quand un code existe, et la moyenne de vrais et de faux est la proportion de vrais, comme en Python. Le verbe `count`, enfin, compte les lignes par valeur ; c'est la version courte de `group_by` suivi de `summarise(n = n())`.

```r
commandes |> count(canal, sort = TRUE)
```
<!--sortie-->
```text
# A tibble: 3 × 2
  canal        n
  <chr>    <int>
1 Boutique 16975
2 Site     15463
3 Réseaux   3957
```

### 4.2.4 Dates, texte et catégories : lubridate, stringr, forcats

Trois paquets du tidyverse rendent les opérations courantes sur les dates, les textes et les catégories plus agréables. **lubridate** extrait les composantes d'une date (`year`, `month`, `isoweek`) et arrondit une date à son début de mois (`floor_date`). **stringr** manipule les textes (`str_to_title`, `str_detect`, `str_replace`). **forcats** ordonne et regroupe les catégories (`fct_infreq` classe par fréquence).

```r
commandes |> mutate(mois = floor_date(date_commande, "month")) |> count(mois) |> head(3)
str_to_title(c("BOÎTE RUSTIQUE", "tapis nordique"))
levels(fct_infreq(commandes$code_promo))
```
<!--sortie-->
```text
# A tibble: 3 × 2
  mois           n
  <date>     <int>
1 2023-01-01   785
2 2023-02-01   642
3 2023-03-01   801
[1] "Boîte Rustique" "Tapis Nordique"
[1] "SOLDES"    "FIDELITE"  "BIENVENUE"
```

Le premier résultat donne le nombre de commandes des trois premiers mois ; le deuxième remet des majuscules aux initiales (y compris sur une lettre accentuée) ; le troisième liste les codes promotionnels, du plus fréquent au plus rare. On retrouve ces gestes en Python avec `dt.to_period("M")`, `str.title()` et `value_counts()` : la logique est la même, seule la syntaxe diffère.

### 4.2.5 L'équivalence entre pandas et le tidyverse

Une fois la logique comprise, passer d'un langage à l'autre revient à traduire. Le tableau suivant sert d'aide-mémoire.

| Geste | pandas (Python) | tidyverse (R) |
|---|---|---|
| Lire un CSV | `pd.read_csv("f.csv")` | `read_csv("f.csv")` |
| Voir la structure | `df.dtypes`, `df.head()` | `glimpse(df)`, `head(df)` |
| Choisir des colonnes | `df[["a", "b"]]` | `select(df, a, b)` |
| Filtrer | `df[df["a"] > 3]`, `df.query("a > 3")` | `filter(df, a > 3)` |
| Créer une colonne | `df.assign(c=lambda d: d.a * 2)` | `mutate(df, c = a * 2)` |
| Trier | `df.sort_values("a", ascending=False)` | `arrange(df, desc(a))` |
| Résumer par groupe | `df.groupby("g").agg(m=("a", "mean"))` | `group_by(df, g)` puis `summarise(m = mean(a))` |
| Compter | `df["g"].value_counts()` | `count(df, g)` |
| Joindre | `df.merge(t, on="k", how="left")` | `left_join(df, t, by = "k")` |
| Manquant ? | `df["a"].isna()` | `is.na(df$a)` |
| Large vers long | `df.melt(...)` | `pivot_longer(df, ...)` |
| Long vers large | `df.pivot_table(...)` | `pivot_wider(df, ...)` |

### 4.2.6 Ce qui surprend quand on passe de l'un à l'autre

Trois différences causent la plupart des erreurs de traduction. La première, déjà vue : Python compte les positions **à partir de zéro**, R **à partir de un**. La deuxième : l'**égalité** se teste par `==` dans les deux langages, mais `=` n'est pas la même chose partout (affectation en R et en Python, argument nommé dans un appel de fonction). La troisième est plus sournoise : le traitement **par défaut** des valeurs manquantes.

```python
x = pd.Series([1.0, 2.0, np.nan])
print(x.sum(), x.mean())
```
<!--sortie-->
```text
3.0 1.5
```

```r
x <- c(1, 2, NA)
sum(x); mean(x); mean(x, na.rm = TRUE)
```
<!--sortie-->
```text
[1] NA
[1] NA
[1] 1.5
```

Python (pandas) **ignore** les manquants et renvoie 3 pour la somme et 1,5 pour la moyenne. R **propage** le manquant : la somme d'un vecteur qui contient un `NA` est `NA`, ce qui oblige à écrire `na.rm = TRUE` pour les ignorer. Aucun des deux choix n'est faux, mais ils conduisent à des bugs inverses : dans pandas, on oublie qu'un calcul a écarté des lignes ; dans R, on s'aperçoit tout de suite qu'un `NA` traîne. La leçon est valable partout : **comptez toujours vos manquants avant de calculer**.

> ✅ **À retenir.** Le tidyverse range les verbes par fonction : `select` (colonnes), `filter` (lignes), `mutate` (calculs), `arrange` (tri), `group_by` + `summarise` (résumés), `count`, `left_join` ; le tube `|>` les relie, comme les points de la méthode chaînée de pandas. Les résultats sont ceux de pandas, à la syntaxe près ; les pièges sont l'indexation (à partir de 1) et les manquants (propagés par défaut).

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.3, exercice 4.6.


## 4.3 Lire, filtrer, regrouper, restructurer

Les sections précédentes ont posé les gestes de base. Celle-ci les met au travail sur des cas d'analyste : remettre en état un export désordonné, résumer par groupes, relier des tables, changer la forme d'un tableau, calculer des moyennes glissantes et comparer des semaines d'une année à l'autre. Elle se termine par la réponse à la gérante : **le tableau du lundi**.

### 4.3.1 Lire un export désordonné

Le fichier `export_caisse_brut.csv` est un export de caisse de la boutique physique pour la semaine du 3 au 9 novembre 2025. Il a l'allure de ce que produisent beaucoup de logiciels de gestion : fait pour être **lu par un humain**, pas par un programme. Avant de le lire avec pandas, regardons-le tel quel, ligne par ligne.

```python
with open("donnees/export_caisse_brut.csv", encoding="cp1252") as f:
    lignes_brutes = f.read().splitlines()
print("\n".join(lignes_brutes[:6]))
print("...")
print(lignes_brutes[-1])
```
<!--sortie-->
```text
Export caisse - Boutique;;;;;;;
Période du 03/11/2025 au 09/11/2025;;;;;;;
;;;;;;;
N° ticket;Date;Heure;Article;Catégorie;Qté;Prix unitaire;Montant
T33133;03/11/2025;09:00;BOÎTE RUSTIQUE;Maison;2;52,43;104,86
T33137;03/11/2025;10:35;Tapis nordique;Maison;1;64,79;64,79
...
;;;;;;Total;11561,47
```

On y voit cinq défauts typiques. Trois lignes de **titre** précèdent l'en-tête des colonnes. Le séparateur est le **point-virgule** et les décimaux s'écrivent avec une **virgule** (`52,43`). Les dates sont au format **jour/mois/année**. La dernière ligne est un **total**, qui n'est pas une vente. Et, comme on le verra, l'en-tête **se répète** à plusieurs endroits (le logiciel le réimprime à chaque « page »). Un sixième défaut ne se voit pas : le fichier est encodé en `cp1252`, l'ancien codage des fichiers Windows, et non en UTF-8. Lu avec le mauvais codage, il produit une erreur ou des accents mutilés.

```python
try:
    pd.read_csv("donnees/export_caisse_brut.csv", sep=";")
except UnicodeDecodeError as e:
    print(type(e).__name__, "-", e.reason)
```
<!--sortie-->
```text
UnicodeDecodeError - invalid continuation byte
```

Avec les bons arguments, la lecture réussit. On saute les trois lignes de titre avec `skiprows=3`.

```python
brut = pd.read_csv("donnees/export_caisse_brut.csv", sep=";", encoding="cp1252", skiprows=3)
print(brut.shape)
print(brut["Qté"].dtype, brut["Montant"].dtype)
```
<!--sortie-->
```text
(285, 8)
str str
```

Il y a 285 lignes, mais le résultat est décevant : même la quantité est lue comme **du texte**. La cause est que la colonne contient des mots (la ligne d'en-tête répétée, et le mot « Total ») : une seule cellule non numérique suffit à faire lire toute la colonne comme du texte. Il faut donc écarter ces lignes parasites **avant** de convertir. On garde les lignes dont le numéro de ticket est renseigné et n'est pas le mot « N° ticket », puis on convertit les dates (au format `%d/%m/%Y`) et les nombres (en remplaçant la virgule décimale par un point).

```python
caisse = brut[brut["N° ticket"].notna() & (brut["N° ticket"] != "N° ticket")].copy()
print(len(brut) - len(caisse), "lignes écartées :", brut["N° ticket"].isna().sum(), "total,", (brut["N° ticket"] == "N° ticket").sum(), "en-têtes répétés")
total_fichier = float(brut.iloc[-1]["Montant"].replace(",", "."))
caisse["Date"] = pd.to_datetime(caisse["Date"], format="%d/%m/%Y")
for col in ["Qté", "Prix unitaire", "Montant"]:
    caisse[col] = pd.to_numeric(caisse[col].str.replace(",", "."))
print(caisse[["Date", "Qté", "Prix unitaire", "Montant"]].dtypes)
```
<!--sortie-->
```text
5 lignes écartées : 1 total, 4 en-têtes répétés
Date             datetime64[us]
Qté                       int64
Prix unitaire           float64
Montant                 float64
dtype: object
```

Reste à traiter les **valeurs manquantes** : huit lignes n'ont pas de montant. On peut le **reconstituer** (quantité × prix unitaire), mais avant de le faire, vérifions que ce calcul est légitime et mesurons son effet en le comparant au total que le fichier annonce lui-même. Cette comparaison est un réflexe : **toute transformation doit se réconcilier avec un chiffre connu**.

```python
print(caisse["Montant"].isna().sum())
manquants = caisse[caisse["Montant"].isna()]
tickets = manquants["N° ticket"].str[1:].astype(int)
print(commandes.loc[commandes["id_commande"].isin(tickets), ["id_commande", "code_promo"]].dropna())
print(manquants.loc[manquants["N° ticket"] == "T33353", ["Article", "Qté", "Prix unitaire"]])
caisse["Montant"] = caisse["Montant"].fillna((caisse["Qté"] * caisse["Prix unitaire"]).round(2))
print(round(caisse["Montant"].sum(), 2), total_fichier, round(caisse["Montant"].sum() - total_fichier, 2))
```
<!--sortie-->
```text
8
       id_commande code_promo
33352        33353   FIDELITE
            Article  Qté  Prix unitaire
205  Boîte rustique    1          52.43
11564.09 11561.47 2.62
```

Le total reconstitué est de 11 564,09 €, et le fichier annonce 11 561,47 € : **2,62 € d'écart**. D'où vient-il ? L'un des huit tickets sans montant (le numéro 33353) a été payé avec le code `FIDELITE`, qui accorde 5 % de remise ; or le calcul « quantité × prix » ignore les remises. Cinq pour cent de 52,43 €, le prix de la ligne concernée, font 2,62 €. L'écart est expliqué au centime : on **sait** que les 280 lignes restantes sont fiables, et que la reconstitution surestime d'une remise que la caisse ne nous donne pas. En pratique, on garderait la reconstitution en la documentant (le chapitre 4 du volume II traite de la documentation des transformations).

Dernier défaut : le **texte**. Des articles sont en majuscules (`BOÎTE RUSTIQUE`) et des catégories en minuscules (`bien-être`), ce qui crée de faux doublons : pour pandas, `Maison` et `maison` sont deux catégories.

```python
print(caisse["Catégorie"].nunique(), caisse["Article"].nunique())
caisse["Catégorie"] = caisse["Catégorie"].str.capitalize()
caisse["Article"] = caisse["Article"].str.capitalize()
print(caisse["Catégorie"].nunique(), caisse["Article"].nunique())
```
<!--sortie-->
```text
10 71
6 58
```

La mise en forme normalisée ramène les 10 catégories apparentes à 6, qui sont les vraies, et les 71 articles apparents à 58. Faisons le même travail en R. Le paquet `readr` lit tout en texte avec `col_types = cols(.default = col_character())`, puis `dmy` convertit les dates jour-mois-année et `parse_number` les nombres, avec la virgule décimale précisée dans `locale`. La fonction `coalesce` remplace un manquant par une autre valeur, et `str_to_sentence` met une majuscule initiale.

```r
brut <- read_delim("donnees/export_caisse_brut.csv", delim = ";", skip = 3, col_types = cols(.default = col_character()),
                   locale = locale(encoding = "cp1252", decimal_mark = ","))
nombre <- function(x) parse_number(x, locale = locale(decimal_mark = ","))
caisse_r <- brut |>
  filter(!is.na(`N° ticket`), `N° ticket` != "N° ticket") |>
  mutate(Date = dmy(Date), across(c(Qté, `Prix unitaire`, Montant), nombre)) |>
  mutate(Montant = coalesce(Montant, round(Qté * `Prix unitaire`, 2)),
         across(c(Catégorie, Article), str_to_sentence))
cat(nrow(caisse_r), round(sum(caisse_r$Montant), 2), n_distinct(caisse_r$Catégorie), n_distinct(caisse_r$Article), "\n")
```
<!--sortie-->
```text
280 11564.09 6 58 
```


```text
identique au résultat de pandas : TRUE 
```

Même nombre de lignes (280), même total, mêmes comptes de catégories et d'articles. Remarquez comme le programme R, avec ses verbes, se lit presque comme la liste des défauts que nous venons d'énumérer : c'est l'intérêt du style « et ensuite ».

> 🧭 **En pratique : la routine d'un fichier étranger.** (1) Regarder le texte brut avant de lire. (2) Lire **tout en texte** si l'on a un doute sur les types. (3) Écarter les lignes parasites (titres, totaux, en-têtes répétés). (4) Convertir types, dates et nombres. (5) Traiter les manquants, en sachant pourquoi ils manquent. (6) Normaliser les textes. (7) **Réconcilier** avec un total connu. Le volume II consacre un chapitre entier à ces tâches ; retenez dès maintenant que chaque étape doit être écrite, pas faite à la main.

### 4.3.2 Regrouper : une question, un groupe, un calcul

Presque toute question d'analyse revient à : « combien, **par** quoi ? » Le regroupement (*split-apply-combine*) découpe la table en groupes, calcule un résumé dans chacun, puis rassemble les résultats. Pour poser cette base, il nous faut une table de **ventes** qui relie, ligne par ligne, la commande (date, canal), le produit (catégorie, coût) et le montant. C'est le travail d'une **jointure**, dont la section 4.3.3 détaillera le mécanisme ; admettons-la pour l'instant.

```python
ventes = (lignes.merge(commandes, on="id_commande")
                .merge(produits[["id_produit", "categorie", "cout_achat"]], on="id_produit", validate="m:1")
                .assign(annee=lambda d: d["date_commande"].dt.year))
resume = (ventes.groupby("canal")
          .agg(ca=("montant", "sum"), commandes=("id_commande", "nunique"), montant_moyen_ligne=("montant", "mean"))
          .assign(panier_moyen=lambda d: d["ca"] / d["commandes"]).round(1))
print(resume)
```
<!--sortie-->
```text
                 ca  commandes  montant_moyen_ligne  panier_moyen
canal                                                            
Boutique  1712728.8      16975                 43.5         100.9
Réseaux    397741.7       3957                 43.8         100.5
Site      1542686.8      15463                 43.5          99.8
```

`groupby("canal")` découpe par canal ; `agg` calcule **plusieurs** résumés en une fois, chacun avec le nom de la colonne résultat (`ca=("montant", "sum")` se lit « `ca` est la somme de `montant` »). `nunique` compte les valeurs **distinctes** : une commande compte plusieurs lignes, il faut compter chaque numéro de commande une fois. Ce petit tableau contient une leçon importante : la gérante a demandé le « panier moyen », mais **de quoi** la moyenne ? Le montant moyen **d'une ligne** est d'environ 43,5 € dans les trois canaux ; le montant moyen **d'une commande** (le panier) est d'environ 100 €. Les deux sont corrects, ils répondent à deux questions différentes, et confondre l'un avec l'autre fausse la décision. Le panier est ici de 100,9 € en boutique, 100,5 € sur les réseaux et 99,8 € sur le Site : presque identique, malgré des chiffres d'affaires très différents.

Le regroupement sert aussi à calculer des **parts**. La méthode `transform` renvoie, pour chaque ligne, le résultat du groupe auquel elle appartient (ici, le chiffre d'affaires total de l'année) : on peut alors calculer la part de chaque canal sans perdre le détail des lignes.

```python
ca_an_canal = ventes.groupby(["annee", "canal"], as_index=False)["montant"].sum()
total_annee = ca_an_canal.groupby("annee")["montant"].transform("sum")
ca_an_canal["part_pct"] = (ca_an_canal["montant"] / total_annee * 100).round(1)
print(ca_an_canal.pivot(index="annee", columns="canal", values="part_pct"))
```
<!--sortie-->
```text
canal  Boutique  Réseaux  Site
annee                         
2023       52.1     10.8  37.1
2024       46.9     10.8  42.2
2025       42.3     11.0  46.6
```

La lecture est immédiate : en 2023, la boutique réalise 52,1 % du chiffre d'affaires et le Site 37,1 % ; en 2025, le Site (46,6 %) a dépassé la boutique (42,3 %), tandis que les réseaux restent stables, autour de 11 %. La gérante demandait si le Site faisait « perdre des clients à la boutique » : la question est plus fine (le chiffre d'affaires de la boutique a baissé de 2023 à 2024 puis s'est stabilisé), mais la **tendance** de fond est là, et elle vient de ce premier regroupement.

Voici le même travail en R. Le `group_by` suivi de `summarise` calcule les résumés ; `n_distinct` est l'équivalent de `nunique`.

```r
ventes_r <- lignes |>
  left_join(commandes, by = "id_commande") |>
  left_join(select(produits, id_produit, categorie, cout_achat), by = "id_produit") |>
  mutate(annee = year(date_commande))
resume_r <- ventes_r |> group_by(canal) |>
  summarise(ca = sum(montant), commandes = n_distinct(id_commande), montant_moyen_ligne = mean(montant)) |>
  mutate(panier_moyen = ca / commandes, across(where(is.numeric), \(x) round(x, 1)))
resume_r
```
<!--sortie-->
```text
# A tibble: 3 × 5
  canal          ca commandes montant_moyen_ligne panier_moyen
  <chr>       <dbl>     <dbl>               <dbl>        <dbl>
1 Boutique 1712729.     16975                43.5        101. 
2 Réseaux   397742.      3957                43.8        100. 
3 Site     1542687.     15463                43.5         99.8
```


```text
identique au résultat de pandas : TRUE 
```

Pour la part par année, `mutate` appliqué à une table **groupée** joue le rôle de `transform` : la somme du `mutate` est calculée dans chaque groupe.

```r
ventes_r |> group_by(annee, canal) |> summarise(ca = sum(montant), .groups = "drop_last") |>
  mutate(part_pct = round(100 * ca / sum(ca), 1)) |> select(-ca) |> pivot_wider(names_from = canal, values_from = part_pct)
```
<!--sortie-->
```text
# A tibble: 3 × 4
# Groups:   annee [3]
  annee Boutique Réseaux  Site
  <dbl>    <dbl>   <dbl> <dbl>
1  2023     52.1    10.8  37.1
2  2024     46.9    10.8  42.2
3  2025     42.3    11    46.6
```

Les parts sont celles de pandas (et, ici encore, l'affichage d'un tibble arrondit : `101.` pour un panier de 100,9 € dans le tableau précédent, alors que la valeur n'est pas arrondie). Le résultat s'affiche avec une mention « Groups: annee » : la table est restée **groupée** par année après le `summarise`, ce qui change le comportement des verbes suivants. L'argument `.groups = "drop"` ou la fonction `ungroup()` retire ce regroupement : c'est un piège classique de dplyr, qui explique des résultats surprenants quand on oublie de dégrouper.

### 4.3.3 Joindre : relier deux tables par une clé

Une **jointure** relie les lignes de deux tables qui partagent une valeur, la **clé** : le numéro de commande relie `lignes` à `commandes`, le numéro de produit relie `lignes` à `produits`. Trois variantes couvrent la plupart des cas.

| Jointure | Lignes conservées | pandas | dplyr |
|---|---|---|---|
| **gauche** | toutes celles de la table de gauche ; les colonnes de droite sont manquantes quand il n'y a pas de correspondance | `how="left"` | `left_join` |
| **interne** | seulement celles qui ont une correspondance des deux côtés | `how="inner"` | `inner_join` |
| **complète** | toutes celles des deux tables | `how="outer"` | `full_join` |

La jointure **gauche** est la plus utile : on part de la table qui nous intéresse (les lignes de vente) et on lui **ajoute** des informations, sans en perdre. Le danger principal est la **multiplication des lignes** : si la clé n'est pas unique dans la table de droite, chaque ligne de gauche est dupliquée autant de fois qu'elle a de correspondances, et tous les totaux sont faussés **sans qu'aucune erreur n'apparaisse**. Simulons-le en ajoutant au catalogue de produits un doublon du produit numéro 1.

```python
doublon = pd.concat([produits, produits.head(1)])
print(len(lignes.merge(produits, on="id_produit")), len(lignes.merge(doublon, on="id_produit")))
try:
    lignes.merge(doublon, on="id_produit", validate="m:1")
except Exception as e:
    print(type(e).__name__, "-", str(e).split(";")[0])
```
<!--sortie-->
```text
83905 85345
MergeError - Merge keys are not unique in right dataset
```

Avec le catalogue correct, la jointure garde les 83 905 lignes ; avec le doublon, elle en produit 85 345, soit 1 440 de plus : le nombre de lignes de commande du produit 1, **comptées deux fois**. Le chiffre d'affaires de ce produit serait doublé sans alerte. L'argument `validate="m:1"` (« plusieurs à un ») dit à pandas ce que l'on attend : plusieurs lignes à gauche pour une seule à droite. Si ce n'est pas le cas, pandas **refuse** et lève une erreur. C'est une assurance qui coûte quelques caractères : prenez l'habitude de l'écrire.

Dans dplyr, l'argument équivalent est `relationship = "many-to-one"`.

```r
doublon_r <- bind_rows(produits, head(produits, 1))
cat(nrow(suppressWarnings(left_join(lignes, produits, by = "id_produit"))),
    nrow(suppressWarnings(left_join(lignes, doublon_r, by = "id_produit"))), "\n")
tryCatch(left_join(lignes, doublon_r, by = "id_produit", relationship = "many-to-one"),
         error = function(e) cat("erreur :", conditionMessage(e) |> str_split_1("\n") |> head(1), "\n"))
```
<!--sortie-->
```text
83905 85345 
erreur : Each row in `x` must match at most 1 row in `y`. 
```

Mêmes nombres, même refus. (Par défaut, dplyr se contente d'un **avertissement** quand il détecte une relation « plusieurs à plusieurs » ; nous l'avons masqué ici, mais en situation réelle ne l'ignorez jamais.) Reste à utiliser nos jointures. Deux questions que la gérante se pose depuis longtemps : quelle est la **marge** par catégorie, et quelle part des lignes est **retournée** ? On reconnaît un retour par la présence de la ligne dans `retours`.

```python
retourne = lignes[["id_ligne"]].assign(retourne=lignes["id_ligne"].isin(retours["id_ligne"]))
taux_retour = (ventes.merge(retourne, on="id_ligne").groupby("categorie")["retourne"].mean() * 100).round(1)
marge = ventes.assign(marge=lambda d: d["montant"] - d["quantite"] * d["cout_achat"]).groupby("categorie")[["marge", "montant"]].sum()
cat_tab = pd.DataFrame({"taux_retour_pct": taux_retour, "taux_marge_pct": (marge["marge"] / marge["montant"] * 100).round(1)})
print(cat_tab)
```
<!--sortie-->
```text
            taux_retour_pct  taux_marge_pct
categorie                                  
Bien-être               6.1            45.0
Cuisine                 6.1            46.9
Décoration              6.0            49.0
Jardin                  6.2            47.5
Maison                  5.9            47.4
Papeterie               5.4            46.3
```

Les taux de retour sont presque identiques d'une catégorie à l'autre (entre 5,4 % et 6,2 %), et le taux de marge varie de 45,0 % pour le bien-être à 49,0 % pour la décoration. Voici le même calcul en R.

```r
retourne_r <- lignes |> mutate(retourne = id_ligne %in% retours$id_ligne) |> select(id_ligne, retourne)
cat_tab_r <- ventes_r |> left_join(retourne_r, by = "id_ligne") |> group_by(categorie) |>
  summarise(taux_retour_pct = round(100 * mean(retourne), 1),
            taux_marge_pct = round(100 * sum(montant - quantite * cout_achat) / sum(montant), 1))
cat_tab_r
```
<!--sortie-->
```text
# A tibble: 6 × 3
  categorie  taux_retour_pct taux_marge_pct
  <chr>                <dbl>          <dbl>
1 Bien-être              6.1           45  
2 Cuisine                6.1           46.9
3 Décoration             6             49  
4 Jardin                 6.2           47.5
5 Maison                 5.9           47.4
6 Papeterie              5.4           46.3
```


```text
identique au résultat de pandas : TRUE 
```

Le taux de retour, presque uniforme **par catégorie**, ne l'est pas du tout **par canal**. Changer le regroupement change l'histoire : c'est la raison d'être de l'analyse.

```python
tx_canal = ventes.merge(retourne, on="id_ligne").groupby("canal")["retourne"].mean().mul(100).round(1)
print(tx_canal.to_dict(), "| remboursé :", round(retours["montant_rembourse"].sum()), "€")
```
<!--sortie-->
```text
{'Boutique': 3.1, 'Réseaux': 6.7, 'Site': 9.0} | remboursé : 221010 €
```

Un retour sur 11 lignes vendues sur le Site (9,0 %), contre une sur 32 en boutique (3,1 %) et 6,7 % sur les réseaux. Le montant total remboursé sur trois ans est de 221 010 €, soit 6,05 % du chiffre d'affaires : voilà la réponse à la question « combien nous coûtent les retours ? », et l'indication que le **canal**, bien plus que la catégorie, est le levier à examiner.

### 4.3.4 Restructurer : le format large et le format long

Un même tableau peut s'écrire de deux façons. Le **format large** a une colonne par modalité : une colonne `Boutique`, une `Réseaux`, une `Site`. C'est le format de lecture, celui d'un tableau de synthèse. Le **format long** a une ligne par observation : une ligne par couple (année, canal), avec une colonne `canal` et une colonne `ca`. C'est le format de calcul, celui que les graphiques, les modèles et les regroupements préfèrent.


![Le même tableau en format large (à gauche) et en format long (à droite) : les noms de colonnes `Boutique`, `Réseaux`, `Site` deviennent des valeurs d'une colonne `canal`. Chiffres d'affaires en milliers d'€.](figures/ch04-large-long.png)

On passe de l'un à l'autre avec deux opérations : **pivoter** vers le large (`pivot_table` dans pandas, `pivot_wider` dans tidyr) et **dépivoter** vers le long (`melt` dans pandas, `pivot_longer` dans tidyr).

```python
large = ca_an_canal.pivot_table(index="annee", columns="canal", values="montant", aggfunc="sum").round(0)
long = large.reset_index().melt(id_vars="annee", var_name="canal", value_name="ca")
print(large)
print(long.head(4))
```
<!--sortie-->
```text
canal  Boutique   Réseaux      Site
annee                              
2023   593612.0  122880.0  422440.0
2024   558143.0  128787.0  502531.0
2025   560974.0  146074.0  617715.0
   annee     canal        ca
0   2023  Boutique  593612.0
1   2024  Boutique  558143.0
2   2025  Boutique  560974.0
3   2023   Réseaux  122880.0
```

Le premier résultat est le tableau de synthèse que l'on mettrait dans un rapport ; le second est la même information, rangée pour qu'un graphique ou un calcul s'en empare (une colonne pour l'axe, une pour la couleur, une pour la valeur). Le même aller-retour en R :

```r
large_r <- ventes_r |> group_by(annee, canal) |> summarise(ca = round(sum(montant)), .groups = "drop") |>
  pivot_wider(names_from = canal, values_from = ca)
long_r <- large_r |> pivot_longer(-annee, names_to = "canal", values_to = "ca")
large_r
head(long_r, 3)
```
<!--sortie-->
```text
# A tibble: 3 × 4
  annee Boutique Réseaux   Site
  <dbl>    <dbl>   <dbl>  <dbl>
1  2023   593612  122880 422440
2  2024   558143  128787 502531
3  2025   560974  146074 617715
# A tibble: 3 × 3
  annee canal        ca
  <dbl> <chr>     <dbl>
1  2023 Boutique 593612
2  2023 Réseaux  122880
3  2023 Site     422440
```

> 💡 **Intuition.** Si les en-têtes de colonnes sont des **valeurs** (des canaux, des mois, des années), la table est large ; si ce sont des **noms de variables** (le canal, le mois, le montant), elle est longue. Un graphique réclame presque toujours une table longue ; un lecteur humain préfère presque toujours une table large.

### 4.3.5 Fenêtres glissantes et comparaisons dans le temps

Un chiffre quotidien est bruité : un samedi de pluie, un jour de soldes. Pour voir la tendance, on le **lisse** par une **moyenne glissante** : à chaque jour, la moyenne des sept derniers jours. En pandas, `rolling(7).mean()` la calcule ; avec `center=True`, la fenêtre est centrée sur le jour au lieu de le suivre.

```python
jours = jours.assign(ca_7j=jours["chiffre_affaires"].rolling(7).mean(),
                     ca_7j_centre=jours["chiffre_affaires"].rolling(7, center=True).mean())
print(jours.iloc[5:9][["chiffre_affaires", "ca_7j", "ca_7j_centre"]].round(0).assign(date=jours["date"].dt.date))
print(pd.Timestamp("2025-12-31").isocalendar())
```
<!--sortie-->
```text
   chiffre_affaires   ca_7j  ca_7j_centre        date
5            2691.0     NaN        2431.0  2023-01-06
6            2391.0  2027.0        2328.0  2023-01-07
7            1732.0  2162.0        2169.0  2023-01-08
8            3091.0  2431.0        2172.0  2023-01-09
datetime.IsoCalendarDate(year=2026, week=1, weekday=3)
```

Les six premiers jours n'ont **pas** de moyenne glissante « suivante » : il faut sept jours d'historique pour la calculer (d'où le `NaN` du 6 janvier), alors que la version centrée existe dès le quatrième jour mais nécessite trois jours de **futur**, ce qui l'exclut pour une prévision. Le 7 janvier 2023, le chiffre d'affaires du jour était de 2 391 € alors que la moyenne des sept derniers jours était de 2 027 € : le lissage change la lecture.

Pour comparer une semaine à la même semaine de l'an dernier, il faut une définition de la « semaine ». On utilise la **semaine ISO** : elle commence le lundi et appartient à l'année qui contient son jeudi. La conséquence est surprenante : le **31 décembre 2025** appartient à la **semaine 1 de 2026**. Pour cette raison, une comparaison d'année à année doit utiliser **l'année ISO** (et non l'année du calendrier), faute de quoi les premiers et derniers jours de l'année seraient rangés dans la mauvaise semaine. Calculons le chiffre d'affaires par semaine ISO et par canal.

```python
iso = ventes["date_commande"].dt.isocalendar()
ventes = ventes.assign(annee_iso=iso["year"].astype(int), semaine=iso["week"].astype(int))
sem = ventes.groupby(["annee_iso", "semaine", "canal"], as_index=False)["montant"].sum()
print(sem[(sem["semaine"] == 45) & (sem["annee_iso"] >= 2024)])
```
<!--sortie-->
```text
     annee_iso  semaine     canal   montant
290       2024       45  Boutique  12783.90
291       2024       45   Réseaux   2856.28
292       2024       45      Site  12089.19
446       2025       45  Boutique  11561.47
447       2025       45   Réseaux   4581.86
448       2025       45      Site  14096.67
```

Deux lignes par canal pour la semaine 45 : celle de 2024 et celle de 2025. On a les ingrédients du tableau du lundi.

> ⚠️ **Piège : décaler de 52 semaines.** Pour « la même semaine l'an dernier », on pourrait décaler la série hebdomadaire de 52 lignes. Mais certaines années ISO ont **53** semaines : le décalage dérive alors d'une semaine. Joindre sur le couple (année ISO moins un, numéro de semaine), comme nous allons le faire, est plus sûr.

### 4.3.6 Le tableau du lundi

Nous pouvons maintenant répondre à la gérante. On écrit une **fonction** qui prend un numéro de semaine et une année, et renvoie le tableau : les ventes par canal de cette semaine, de la même semaine l'année précédente, et l'évolution en pourcentage. Une fonction est une recette réutilisable : c'est ce qui fait passer du calcul **ponctuel** à l'**automatisation**.

```python
def tableau_du_lundi(semaine, annee):
    cur = sem[(sem.annee_iso == annee) & (sem.semaine == semaine)].set_index("canal")["montant"]
    pre = sem[(sem.annee_iso == annee - 1) & (sem.semaine == semaine)].set_index("canal")["montant"]
    t = pd.DataFrame({"cette_semaine": cur, "meme_semaine_an_dernier": pre})
    t.loc["Total"] = t.sum()
    t["evolution_pct"] = (t["cette_semaine"] / t["meme_semaine_an_dernier"] - 1) * 100
    return t.round(1)

lundi = tableau_du_lundi(45, 2025)
print(lundi)
```
<!--sortie-->
```text
          cette_semaine  meme_semaine_an_dernier  evolution_pct
canal                                                          
Boutique        11561.5                  12783.9           -9.6
Réseaux          4581.9                   2856.3           60.4
Site            14096.7                  12089.2           16.6
Total           30240.0                  27729.4            9.1
```

La semaine du 3 au 9 novembre 2025 a rapporté 30 240,0 € au total, contre 27 729,4 € la semaine correspondante de 2024 : **+9,1 %**. Mais la moyenne cache des mouvements opposés : la boutique recule de 9,6 % (11 561,5 € contre 12 783,9 €), le Site progresse de 16,6 % et les réseaux de 60,4 %. Ce dernier chiffre impressionne, mais il part d'une **petite base** (2 856,3 € l'an dernier) : +1 725,6 € suffisent, soit quelques commandes de plus. Un analyste ne livre jamais un pourcentage sans le montant qui le porte. Écrivons la même fonction en R.

```r
sem_r <- ventes_r |> mutate(annee_iso = isoyear(date_commande), semaine = isoweek(date_commande)) |>
  group_by(annee_iso, semaine, canal) |> summarise(montant = sum(montant), .groups = "drop")
sem_r <- bind_rows(sem_r, sem_r |> group_by(annee_iso, semaine) |> summarise(montant = sum(montant), canal = "Total", .groups = "drop"))
tableau_du_lundi_r <- function(s, a) {
  sem_r |> filter(semaine == s, annee_iso %in% c(a, a - 1)) |>
    mutate(periode = if_else(annee_iso == a, "cette_semaine", "meme_semaine_an_dernier")) |>
    select(canal, periode, montant) |> pivot_wider(names_from = periode, values_from = montant) |>
    relocate(cette_semaine, .after = canal) |>
    mutate(evolution_pct = (cette_semaine / meme_semaine_an_dernier - 1) * 100, across(where(is.numeric), \(x) round(x, 1)))
}
lundi_r <- tableau_du_lundi_r(45, 2025)
lundi_r
```
<!--sortie-->
```text
# A tibble: 4 × 4
  canal    cette_semaine meme_semaine_an_dernier evolution_pct
  <chr>            <dbl>                   <dbl>         <dbl>
1 Boutique        11562.                  12784.          -9.6
2 Réseaux          4582.                   2856.          60.4
3 Site            14097.                  12089.          16.6
4 Total           30240                   27729.           9.1
```


```text
identique au résultat de pandas : TRUE 
```

Les deux langages produisent le même tableau. Une dernière vérification croisée, d'une autre nature : le chiffre d'affaires de la boutique en semaine 45 de 2025 est de **11 561,47 €** dans la table `sem`, et c'est **exactement** le total que l'export de caisse de la section 4.3.1 annonçait. Le fichier désordonné, remis en état à la main, et les données de la base racontent la même histoire : les chiffres sont fiables.


![Chiffre d'affaires hebdomadaire total (milliers d'€) par semaine ISO, 2025 contre 2024. Le point orange est la semaine 45, celle du tableau du lundi.](figures/ch04-semaines.png)

Il reste à « automatiser » : rendre la fonction capable de produire, sans intervention, le tableau de la **semaine qui vient de s'achever**. À partir de la date du jour, `isocalendar()` donne l'année et le numéro de la semaine ISO ; on retranche une semaine pour avoir la semaine **terminée**, puis on appelle la fonction. Le programme complet tient dans un fichier de script, que l'ordinateur lance de lui-même chaque lundi matin grâce à un planificateur de tâches (`cron` sur Linux, le Planificateur de tâches de Windows).

```bash
# crontab : chaque lundi à 7 h, exécuter le script qui écrit le tableau dans le dossier partagé
0 7 * * 1  cd /chemin/vers/le/projet && python tableau_du_lundi.py
```

> ✅ **À retenir.** Un fichier étranger se lit en trois temps : **regarder**, **lire avec les bons arguments**, **nettoyer** ; et toute transformation se **réconcilie** avec un chiffre connu. Regrouper, c'est répondre à « combien **par** quoi ? » : `groupby` + `agg` (pandas), `group_by` + `summarise` (dplyr), `transform` ou `mutate` pour les parts. Une jointure gauche **ajoute** des informations ; vérifiez avec `validate` / `relationship` qu'elle ne **multiplie** pas les lignes. Le format large se lit, le format long se calcule. Pour comparer des semaines, utilisez les **semaines ISO** et l'**année ISO**, et ne livrez jamais un pourcentage sans le montant qui le porte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.4 à 4.7, exercices 4.7 à 4.10 et 4.12.


## 4.4 Notebooks d'analyse

Jusqu'ici, nous avons écrit des morceaux de programme. Reste à les **ranger** quelque part, avec leur explication et leurs résultats, de façon qu'un collègue (ou vous dans six mois) puisse les relire, les relancer et en tirer le même chiffre. L'outil le plus répandu pour cela est le **notebook**. Cette section en explique le principe, son principal piège, et les habitudes qui rendent un notebook fiable.

### 4.4.1 Qu'est-ce qu'un notebook ?

Un **notebook** est un document fait d'une suite de **cellules**. Une cellule de **texte** (en Markdown) contient une explication, un titre, une conclusion. Une cellule de **code** contient quelques lignes de programme ; quand on l'exécute, son **résultat** (un nombre, un tableau, un graphique) s'affiche juste en dessous et est conservé dans le document. Le tout forme un récit : question, méthode, résultat, commentaire. Le notebook de **Jupyter** est le format standard pour Python (il sait aussi exécuter R) ; **R Markdown** et **Quarto** sont les équivalents côté R, avec des documents texte qui se « tricotent » en rapport (nous les voyons en 4.4.4).

Derrière un notebook Jupyter se cache un **noyau** (*kernel*) : un programme Python qui reste allumé et **garde en mémoire** les variables au fil des cellules. C'est ce qui rend l'outil si agréable pour explorer (on charge les données une fois, on les interroge dix fois) ; c'est aussi la source de son principal piège.

### 4.4.2 Le piège de l'état caché

Le noyau se souvient de ce que vous avez exécuté, **dans l'ordre où vous l'avez exécuté**, pas dans l'ordre où les cellules sont écrites. Rien ne vous empêche d'exécuter la cellule 5, puis la 2, puis de modifier la 3 sans la relancer. À la fin, l'écran montre des résultats qui ne correspondent plus au code affiché : on parle d'**état caché**. Le notebook semble marcher, mais un collègue qui l'exécute de haut en bas obtient un autre résultat, ou une erreur.

Pour le montrer sans rien exagérer, construisons des notebooks **par programme** et exécutons-les pour de bon dans un noyau neuf, avec la bibliothèque `nbformat` (qui construit le fichier) et `nbclient` (qui l'exécute). Une fonction d'aide fait ce travail ; elle prend une liste de cellules et renvoie le notebook exécuté.

```python
cellules = [
    ("md", "# Chiffre d'affaires 2025"),
    ("code", "import pandas as pd\nl = pd.read_csv('donnees/lignes_commande.csv')\nc = pd.read_csv('donnees/commandes.csv', parse_dates=['date_commande'])"),
    ("code", "v = l.merge(c, on='id_commande')\nca = v.loc[v['date_commande'].dt.year == 2025, 'montant'].sum()"),
    ("code", "print(round(ca, 2))"),
]
nb, erreur = O.executer_notebook(cellules, os.getcwd())
print(O.sorties_texte(nb)[-1], erreur)
```
<!--sortie-->
```text
1324763.72 None
```

Exécuté **de haut en bas** dans un noyau neuf, le notebook donne le chiffre d'affaires de 2025 que nous avions calculé en 4.0, au centime près : c'est le test de reproductibilité de base. Voyons maintenant ce que donne l'ordre d'exécution. Trois cellules : A fixe une remise de 10 %, B calcule le prix après remise, C change la remise à 20 %.

```python
A, B, C = ("code", "remise = 0.10"), ("code", "print(round(100 * (1 - remise), 2))"), ("code", "remise = 0.20")
nb1, _ = O.executer_notebook([A, B, C], os.getcwd())
nb2, _ = O.executer_notebook([A, C, B], os.getcwd())
print("ordre A, B, C :", O.sorties_texte(nb1)[1], "| ordre A, C, B :", O.sorties_texte(nb2)[2])
```
<!--sortie-->
```text
ordre A, B, C : 90.0 | ordre A, C, B : 80.0
```

Le même code, deux ordres d'exécution, deux résultats : 90 et 80. Si vous avez exécuté C avant B sans y penser, l'écran affiche 80 alors que le document, relu de haut en bas, donne 90. Un autre scénario courant est la **variable disparue** : on supprime la cellule qui la définissait, mais le noyau la garde en mémoire, et tout continue de fonctionner… jusqu'au jour où quelqu'un d'autre ouvre le fichier.

```python
nb3, erreur = O.executer_notebook([("code", "print(taux_tva)"), ("code", "taux_tva = 0.2")], os.getcwd())
print(erreur)
```
<!--sortie-->
```text
NameError: name 'taux_tva' is not defined
```

> ⚠️ **Piège : un notebook n'est reproductible que s'il s'exécute de haut en bas, dans un noyau neuf.** C'est le seul test qui compte. Avant de partager ou d'utiliser un notebook, faites toujours **« Redémarrer le noyau et tout exécuter »** (*Restart and Run All*). Si une erreur apparaît, ou si un chiffre change, c'est qu'un état caché vous cachait un défaut.

### 4.4.3 Les habitudes d'un notebook fiable

Quelques règles simples évitent la plupart des ennuis. Elles valent aussi pour les scripts, mais le notebook, plus souple, a besoin qu'on se les impose.

| À faire | À éviter |
|---|---|
| **Une question par notebook**, annoncée en tête, avec la conclusion écrite en clair | Un notebook fourre-tout où l'on a empilé trois ans d'explorations |
| Les données **en entrée** (un chemin relatif, `donnees/ventes.csv`) et les résultats **en sortie** (un fichier écrit) | Un chemin absolu qui n'existe que sur votre poste (`C:\Users\...`) |
| **Importer** toutes les bibliothèques et lire toutes les données **en haut** | Un `import` caché au milieu, qui plante pour qui n'a pas la bibliothèque |
| Fixer les **graines** aléatoires et noter les **versions** des bibliothèques | Un résultat qui change à chaque exécution sans que personne ne sache pourquoi |
| Sortir les fonctions **réutilisables** dans un fichier `.py` que le notebook importe | Copier-coller la même fonction dans dix notebooks |
| **Aucun secret** dans un notebook (mot de passe, clé d'accès) : variables d'environnement | Un mot de passe écrit dans une cellule, puis partagé par courriel |
| **Effacer les sorties** avant de partager si elles contiennent des données sensibles | Envoyer un notebook dont les sorties montrent les noms de clients |

Un dernier point pratique : un notebook est, en dessous, un fichier au format JSON, mélange de code et de résultats. Deux versions d'un même notebook se **comparent mal** avec un outil de gestion de versions comme Git. Une bonne pratique est de n'archiver que la version avec les sorties effacées, ou d'utiliser un outil qui tient le notebook synchronisé avec un script texte (par exemple Jupytext, non installé ici : à vérifier selon votre environnement).

### 4.4.4 R Markdown et Quarto : écrire le rapport comme un programme

Côté R, la tradition est différente : on écrit un **document texte** (Markdown) où l'on insère des morceaux de code R, et un programme (`knitr`, ou Quarto qui le généralise) **exécute** le document et fabrique le rapport final : le code est exécuté, ses résultats sont inclus. Le document est **toujours** exécuté de haut en bas dans une session neuve : le piège de l'état caché disparaît. Voici à quoi ressemble un tel document (le texte entre accolades, `{r}`, ouvre un bloc de code R) :

    ---
    title: "Ventes 2025"
    ---
    Le chiffre d'affaires de 2025 vaut `r round(ca, 2)` €.

    ```{r}
    ventes |> filter(year(date_commande) == 2025) |> count(canal)
    ```

Nous pouvons faire fabriquer un tel rapport par `knitr`. Le bloc suivant construit le document dans un dossier temporaire, le fait « tricoter », et nous montre le texte obtenu.


```text
Le chiffre d'affaires de 2025 vaut 1324763.72 €.
## # A tibble: 3 × 2
##   canal        n
##   <chr>    <int>
## 1 Boutique 12611
## 2 Réseaux   3288
## 3 Site     13928
```

Le texte est devenu un rapport (nous n'en montrons que les lignes utiles : la mise en forme du code et des tableaux a été retirée) : la phrase d'ouverture contient le chiffre d'affaires **calculé**, 1 324 763,72 €, et le tableau des commandes de 2025 par canal est celui que produit le code (12 611 commandes en boutique, 3 288 sur les réseaux, 13 928 sur le Site). Si les données changent, il suffit de relancer : le rapport se met à jour tout seul, sans recopier un seul nombre. C'est la forme la plus aboutie de la **reproductibilité** : le rapport **est** le programme. **Quarto** (`quarto render rapport.qmd`) offre le même principe pour Python, R et d'autres langages, avec des sorties en HTML, PDF ou Word ; il n'est pas installé sur la machine qui a produit ce livre, et la commande n'est donc pas exécutée ici.

```bash
quarto render rapport.qmd --to html      # non exécuté ici : Quarto n'est pas installé
```

### 4.4.5 Quand quitter le notebook ?

Le notebook est le bon outil pour **explorer** et pour **raconter** une analyse. Il est moins bon pour **automatiser** : une tâche qui doit tourner chaque lundi sans personne devant l'écran s'écrit plutôt en **script** (un fichier `.py` ou `.R`) que l'on appelle depuis un planificateur, comme au 4.3.6. La démarche classique : on explore dans un notebook, on **extrait** les parties stables dans des fonctions (un fichier de code), puis on garde le notebook pour la narration. Garder cette séparation évite les deux écueils : le script illisible et le notebook fragile.

> ✅ **À retenir.** Un notebook mêle texte, code et résultats ; son noyau garde les variables **dans l'ordre d'exécution**, pas dans l'ordre d'écriture : c'est l'**état caché**. Le seul test de fiabilité est **« redémarrer et tout exécuter »**. Un bon notebook répond à **une** question, lit ses données en entrée par un chemin relatif, n'embarque aucun secret et sort ses fonctions réutilisables. Côté R, R Markdown et Quarto exécutent le document **de haut en bas** et font du rapport le programme lui-même.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.8, exercice 4.11.


## 4.5 ➕ R : ggplot2 et Shiny

> 🧭 **Section complémentaire.** Elle présente les deux paquets R qui font la réputation du langage pour la communication : **ggplot2** pour les graphiques et **Shiny** pour les applications interactives. Rien de ce qui suit n'est nécessaire à la suite du volume. Le volume IV de cette série est consacré à la visualisation et à la communication ; cette section en donne un avant-goût côté R.

### 4.5.1 La grammaire des graphiques

`ggplot2` repose sur une idée : un graphique n'est pas un « type » à choisir dans un menu (histogramme, courbe, camembert), c'est un **assemblage de couches**, que l'on décrit avec les mêmes briques à chaque fois.

| Brique | Rôle | Exemple |
|---|---|---|
| **Données** | la table à représenter (idéalement en format **long**, voir 4.3.4) | `ggplot(mensuel, ...)` |
| **Esthétiques** (`aes`) | relier des colonnes à des propriétés visuelles : position, couleur, taille | `aes(x = mois, y = ca, colour = canal)` |
| **Géométries** (`geom_*`) | la forme dessinée : ligne, barre, point | `geom_line()`, `geom_col()` |
| **Échelles** (`scale_*`) | comment traduire une valeur en couleur ou en position | `scale_colour_manual(values = ...)` |
| **Facettes** (`facet_*`) | découper en petits graphiques, un par modalité | `facet_wrap(~categorie)` |
| **Thème** (`theme_*`) | l'habillage : fond, grille, police | `theme_minimal()` |

On assemble les couches avec le signe `+`. Représentons le chiffre d'affaires mensuel de chaque canal. Les données sont en format long (une ligne par mois et par canal), et la couleur est reliée à la colonne `canal`.

```r
mensuel <- ventes_r |> mutate(mois = floor_date(date_commande, "month")) |>
  group_by(mois, canal) |> summarise(ca = sum(montant) / 1000, .groups = "drop")
palette <- c(Boutique = "#2a78d6", Réseaux = "#4a3aa7", Site = "#eb6834")
g <- ggplot(mensuel, aes(x = mois, y = ca, colour = canal)) +
  geom_line(linewidth = 1) +
  scale_colour_manual(values = palette) +
  labs(x = NULL, y = "chiffre d'affaires (milliers d'€)", colour = NULL) +
  theme_minimal(base_size = 11) + theme(legend.position = "top")
ggsave("figures/ch04-ggplot-mensuel.png", g, width = 8, height = 3.6, dpi = 200)
```

![Chiffre d'affaires mensuel (milliers d'€) par canal, de 2023 à 2025, tracé avec ggplot2. Le pic de fin d'année est visible chaque année ; le Site rattrape puis dépasse la boutique.](figures/ch04-ggplot-mensuel.png)

Chaque ligne du code correspond à une décision lisible : `aes` relie le mois à l'axe horizontal, le montant à l'axe vertical, le canal à la couleur ; `geom_line` dessine des lignes ; `scale_colour_manual` impose notre palette ; `labs` nomme les axes ; `theme_minimal` allège le fond. Le graphique se lit en quelques secondes : une saison très marquée, avec un pic chaque fin d'année, et un Site qui rejoint la boutique. Vérifions ce dernier point par le calcul plutôt que par l'œil : en quel mois le Site a-t-il dépassé la boutique pour la première fois, et combien de mois sur 36 est-il devant ?

```r
devant <- mensuel |> pivot_wider(names_from = canal, values_from = ca) |> filter(Site > Boutique)
cat(format(devant$mois[1], "%Y-%m"), nrow(devant), "\n")
```
<!--sortie-->
```text
2024-09 13 
```

Le Site passe devant en septembre 2024 pour la première fois, et il est en tête 13 mois sur 36. Un graphique ne remplace pas le chiffre : il **oriente** vers celui qu'il faut vérifier.

### 4.5.2 Facettes : plusieurs petits graphiques

Quand on veut comparer plusieurs groupes, plutôt que d'empiler six courbes sur le même graphique, on les sépare en **petits multiples** : une facette par catégorie, tous à la même échelle. Le code ne change presque pas : une couche `facet_wrap` suffit. Nous représentons le chiffre d'affaires de chaque catégorie en 2025, mois par mois.

```r
par_cat <- ventes_r |> filter(annee == 2025) |> mutate(mois = month(date_commande)) |>
  group_by(categorie, mois) |> summarise(ca = sum(montant) / 1000, .groups = "drop")
g2 <- ggplot(par_cat, aes(x = mois, y = ca)) +
  geom_col(fill = "#2a78d6", width = 0.8) +
  facet_wrap(~categorie, ncol = 3) +
  scale_x_continuous(breaks = c(1, 4, 7, 10)) +
  labs(x = "mois de 2025", y = "milliers d'€") +
  theme_minimal(base_size = 10)
ggsave("figures/ch04-ggplot-facettes.png", g2, width = 8, height = 4.2, dpi = 200)
```

![Chiffre d'affaires mensuel de 2025 par catégorie (milliers d'€), une facette par catégorie, tracé avec ggplot2.](figures/ch04-ggplot-facettes.png)

On voit, d'un coup d'œil, des profils différents : le jardin culmine en été (juillet), toutes les autres catégories culminent en décembre, et la décoration avec un pic particulièrement marqué. Cette comparaison par petits multiples est l'un des gestes les plus utiles de la visualisation : elle garde la même échelle partout, et évite à l'œil de comparer des couleurs.

> 💡 **Intuition.** La grammaire des graphiques ressemble à la grammaire d'une langue : une fois les briques apprises (données, esthétiques, géométries, échelles, facettes, thème), on peut dire des choses nouvelles sans apprendre de nouveaux mots. C'est ce qui fait la force de `ggplot2`, et la raison pour laquelle des équivalents ont été écrits en Python (`plotnine`, `altair`). En Python, la voie habituelle passe par `matplotlib` et `seaborn`, dont le fonctionnement est plus **impératif** (on dessine étape par étape).

### 4.5.3 Shiny : une application interactive

Un graphique figé répond à une question. Une **application** laisse l'utilisateur poser lui-même ses questions : choisir un canal, une période, une catégorie, et voir le résultat changer. **Shiny** permet de construire ces applications en R, sans connaître le web. Une application Shiny a deux parties : une **interface** (`ui`), qui décrit ce que l'utilisateur voit (une liste déroulante, un texte), et un **serveur** (`server`), qui décrit comment les résultats se calculent à partir de ce que l'utilisateur choisit. Entre les deux, la **réactivité** : quand l'utilisateur change son choix, seuls les résultats qui en dépendent sont recalculés.

```r
library(shiny)
app <- shinyApp(
  ui = fluidPage(selectInput("canal", "Canal", c("Boutique", "Site", "Réseaux")), textOutput("ca")),
  server = function(input, output, session) {
    ca <- reactive(sum(ventes_r$montant[ventes_r$canal == input$canal & ventes_r$annee == 2025]))
    output$ca <- renderText(paste0("CA 2025 : ", format(round(ca()), big.mark = " "), " €"))
  })
class(app)
```
<!--sortie-->
```text
[1] "shiny.appobj"
```

La dernière ligne confirme que l'on a bien construit un objet « application », qui n'est pas lancé. L'interface déclare une liste déroulante `canal` et une zone de texte `ca`. Le serveur déclare un calcul **réactif** (`ca`, qui dépend de `input$canal`) et une sortie (`output$ca`) qui l'affiche. La commande `runApp(app)` démarrerait un serveur local et ouvrirait l'application dans un navigateur ; nous ne le faisons pas ici. Mais la **logique** de l'application peut se tester sans navigateur, avec `testServer`, qui joue le rôle de l'utilisateur : il choisit un canal, puis lit ce qui s'affiche.

```r
testServer(app, {
  session$setInputs(canal = "Site");     cat(output$ca, "\n")
  session$setInputs(canal = "Boutique"); cat(output$ca, "\n")
})
```
<!--sortie-->
```text
CA 2025 : 617 715 € 
CA 2025 : 560 974 € 
```

Les deux chiffres sont ceux de 4.3.4 : 617 715 € pour le Site et 560 974 € pour la boutique. Tester la logique d'une application sans l'ouvrir est une bonne habitude : on y vérifie les **calculs**, qui sont l'essentiel de la responsabilité de l'analyste. Ce test ne voit pas l'**aspect** de l'application ni sa rapidité perçue, qui se jugent à l'œil.

> 🧭 **En pratique.** Pour partager une application Shiny, il faut l'héberger sur un serveur (service payant ou serveur de l'entreprise : à vérifier selon votre organisation). Si le besoin est seulement de **montrer** des résultats, un rapport HTML (section 4.4.4) ou un tableau de bord (volume IV) suffit souvent. Pour une application en Python, des outils comme Streamlit jouent le même rôle ; le volume IV de la série 1 (chapitre 7) en détaille le fonctionnement.

> ✅ **À retenir.** `ggplot2` décrit un graphique comme un **assemblage de couches** (données, esthétiques, géométries, échelles, facettes, thème) reliées par `+` ; les données doivent être en **format long**. Les **facettes** comparent des groupes à la même échelle. Shiny sépare l'**interface** et le **serveur** et recalcule uniquement ce qui dépend d'un choix de l'utilisateur ; la logique se teste sans navigateur avec `testServer`. Un graphique **oriente** vers un chiffre, mais ne le remplace pas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.9.


## 4.6 ➕ Python : NumPy, polars, rapports avec Jupyter

> 🧭 **Section complémentaire.** Elle regarde sous le capot de pandas (NumPy, le moteur de calcul), présente une alternative plus rapide (polars) et montre comment un notebook devient un rapport automatique. Rien de ce qui suit n'est nécessaire à la suite du volume.

### 4.6.1 NumPy : les tableaux et la vectorisation

Chaque colonne d'un DataFrame pandas repose sur un **tableau NumPy** : une suite de nombres de même type, rangée de façon compacte en mémoire. NumPy est la bibliothèque de base du calcul scientifique en Python, et on l'utilise directement pour des calculs numériques purs. Son idée-clé est la **vectorisation** : une opération s'applique à **tout le tableau d'un coup**, sans écrire de boucle.

```python
q = lignes["quantite"].to_numpy()
p = lignes["prix_unitaire"].to_numpy()
r = lignes["remise_pct"].to_numpy()
montants = q * p * (1 - r / 100)
print(montants.shape, round(montants.sum(), 2), round(lignes["montant"].sum(), 2))
```
<!--sortie-->
```text
(83905,) 3653161.35 3653157.28
```

Les trois colonnes sont multipliées **ligne par ligne** en une seule expression, et le résultat est un nouveau tableau de 83 905 valeurs. La somme obtenue (3 653 161,35 €) est celle des montants du fichier (3 653 157,28 €) à 4 € près, soit un millionième : l'effet cumulé de l'arrondi au centime de chaque montant dans le fichier. Pourquoi la vectorisation compte-t-elle ? Parce qu'une boucle Python traite les nombres **un par un**, alors qu'une opération vectorisée délègue le travail à du code compilé, beaucoup plus rapide. Comparons, sur un million de nombres, une boucle et son équivalent vectorisé ; nous ne citons pas de durées (elles dépendent de la machine), seulement un test.

```python
import time
x = np.random.default_rng(0).random(1_000_000)
def meilleur_temps(f, n=3):
    essais = []
    for _ in range(n):
        t = time.perf_counter(); f(); essais.append(time.perf_counter() - t)
    return min(essais)
somme_boucle, somme_vect = sum(v * 2 for v in x), (x * 2).sum()
print(np.isclose(somme_boucle, somme_vect), meilleur_temps(lambda: sum(v * 2 for v in x)) > 5 * meilleur_temps(lambda: (x * 2).sum()))
```
<!--sortie-->
```text
True True
```

Les deux sommes sont égales, et la version vectorisée est plus de cinq fois plus rapide (en pratique, de l'ordre de vingt à cent fois). Le message pratique est simple : **quand vous écrivez une boucle sur les lignes d'une table, cherchez l'opération vectorisée équivalente**. pandas et NumPy en ont pour presque tous les besoins.

NumPy fournit aussi des fonctions statistiques directes (`mean`, `std`, `percentile`, `corrcoef`) et `where`, qui est le « si » vectorisé. Utilisons-le pour repérer les **jours exceptionnels** : ceux dont le chiffre d'affaires dépasse la moyenne d'un écart-type.

```python
ca = jours["chiffre_affaires"].to_numpy()
seuil = ca.mean() + ca.std()
fort = np.where(ca > seuil, "fort", "normal")
print(round(ca.mean(), 1), round(ca.std(), 1), round(seuil, 1), (fort == "fort").sum())
print(round(jours.loc[fort == "fort", "date"].dt.month.isin([11, 12]).mean() * 100))
```
<!--sortie-->
```text
3333.2 1329.2 4662.4 172
58
```

Le chiffre d'affaires moyen d'un jour est de 3 333,2 €, avec un écart-type de 1 329,2 € ; 172 jours sur 1 096 dépassent 4 662,4 €. Plus de la moitié d'entre eux (58 %) tombent en novembre et en décembre : c'est la saison de fin d'année que la courbe hebdomadaire de la section 4.3.6 faisait déjà apparaître. (Le volume suivant de cette série, sur la préparation des données, reprend la question : un jour « exceptionnel » est-il une **erreur** ou un **événement** ?)

> ⚠️ **Piège : `random` sans graine.** Tout calcul qui tire des nombres au hasard doit fixer une **graine** (`np.random.default_rng(0)`) si l'on veut retrouver le même résultat à la prochaine exécution. Sans graine, deux exécutions du même notebook donneraient deux chiffres différents, et personne ne saurait lequel croire.

### 4.6.2 polars : une alternative rapide à pandas

**polars** est une bibliothèque plus récente que pandas, écrite pour la vitesse : elle utilise tous les cœurs du processeur, et peut optimiser un calcul **avant** de l'exécuter. Elle se distingue par une syntaxe fondée sur des **expressions** : on décrit ce que l'on veut calculer avec `pl.col("nom")`, et polars décide comment l'exécuter. Voici le calcul du chiffre d'affaires par année et par canal, qui est celui de 4.3.2.

```python
import polars as pl
pl.Config.set_tbl_formatting("MARKDOWN")
pl.Config.set_tbl_hide_dataframe_shape(True)
lig_pl = pl.read_csv("donnees/lignes_commande.csv")
cmd_pl = pl.read_csv("donnees/commandes.csv", try_parse_dates=True)
res_pl = (lig_pl.join(cmd_pl, on="id_commande")
          .with_columns(annee=pl.col("date_commande").dt.year())
          .group_by("annee", "canal").agg(ca=pl.col("montant").sum().round(0))
          .sort("annee", "canal"))
print(res_pl.head(4))
```
<!--sortie-->
```text
| annee | canal    | ca       |
| ---   | ---      | ---      |
| i32   | str      | f64      |
|-------|----------|----------|
| 2023  | Boutique | 593612.0 |
| 2023  | Réseaux  | 122880.0 |
| 2023  | Site     | 422440.0 |
| 2024  | Boutique | 558143.0 |
```

On reconnaît chaque étape : jointure (`join`), colonne calculée (`with_columns`), regroupement (`group_by` puis `agg`), tri (`sort`). Contrairement à pandas, polars n'a **pas d'index** de ligne, et affiche le **type** de chaque colonne sous son nom. Les chiffres sont ceux de pandas, ce que l'on peut vérifier plutôt que d'en croire la parole :

```python
pd_ca = large.reset_index().melt(id_vars="annee", var_name="canal", value_name="ca").sort_values(["annee", "canal"])
print(np.allclose(res_pl["ca"].to_numpy(), pd_ca["ca"].to_numpy()))
```
<!--sortie-->
```text
True
```

Le grand intérêt de polars est le mode **paresseux** (*lazy*). Au lieu de lire le fichier et de calculer tout de suite, `scan_csv` ne fait que **décrire** le calcul : rien n'est exécuté avant l'appel à `collect`. Polars peut alors regarder tout le plan, n'en lire que les colonnes utiles et supprimer les étapes inutiles. Sur un fichier de plusieurs gigaoctets, cette optimisation fait la différence entre un calcul qui tient en mémoire et un qui n'y tient pas.

```python
plan = (pl.scan_csv("donnees/lignes_commande.csv")
        .group_by("id_produit").agg(ca=pl.col("montant").sum().round(2))
        .sort("ca", descending=True).head(3))
print(plan.collect())
```
<!--sortie-->
```text
| id_produit | ca        |
| ---        | ---       |
| i64        | f64       |
|------------|-----------|
| 86         | 175236.24 |
| 87         | 128420.16 |
| 82         | 127162.57 |
```

Les trois produits qui rapportent le plus (les numéros 86, 87 et 82) sont obtenus sans avoir chargé les colonnes dont le calcul n'a pas besoin. Les deux bibliothèques ont leur place : pandas est partout, très bien documenté, et suffit pour la grande majorité des analyses ; polars brille sur de **gros volumes** ou quand la vitesse compte. Savoir les lire toutes deux est un atout.

| Geste | pandas | polars |
|---|---|---|
| Lire | `pd.read_csv("f.csv")` | `pl.read_csv("f.csv")`, `pl.scan_csv` (paresseux) |
| Filtrer | `df[df["a"] > 3]` | `df.filter(pl.col("a") > 3)` |
| Créer une colonne | `df.assign(c=...)` | `df.with_columns(c=...)` |
| Regrouper | `df.groupby("g").agg(...)` | `df.group_by("g").agg(...)` |
| Trier | `df.sort_values("a")` | `df.sort("a")` |
| Exécuter un plan paresseux | (sans objet) | `.collect()` |

### 4.6.3 Des rapports avec Jupyter

Un notebook exécuté contient déjà le texte, le code et les résultats : il suffit de le **convertir** pour obtenir un rapport lisible par quelqu'un qui n'a ni Python ni Jupyter. La bibliothèque `nbconvert` transforme un notebook en page HTML. Reprenons le notebook de 4.4.2, exécuté, et fabriquons son rapport.

```python
from nbconvert import HTMLExporter
nb_rapport, _ = O.executer_notebook(cellules, os.getcwd())
html, _ = HTMLExporter().from_notebook_node(nb_rapport)
print(len(html) > 10_000, "Chiffre d'affaires 2025" in html, "1324763.72" in html)
```
<!--sortie-->
```text
True True True
```

La page HTML produite contient le titre du notebook, et le chiffre calculé par la cellule de code. En ligne de commande, la même opération s'écrit en une ligne, qui exécute le notebook **puis** le convertit. Associée à un planificateur de tâches (voir 4.3.6), elle produit un rapport à jour chaque lundi sans que personne n'ouvre Jupyter.

```bash
jupyter nbconvert --to html --execute rapport.ipynb      # non exécuté ici : l'écriture du fichier se fait hors du livre
```

Pour qu'un même notebook serve à plusieurs semaines ou plusieurs canaux, on lui donne des **paramètres** : une cellule de tête fixe la semaine et l'année, qu'un outil (par exemple `papermill`, non installé ici : à vérifier selon votre environnement) remplace avant l'exécution. C'est le principe du tableau du lundi : une seule recette, des paramètres qui changent, des rapports qui se fabriquent seuls.

> ✅ **À retenir.** NumPy est le moteur de calcul de pandas : une opération **vectorisée** s'applique à tout un tableau d'un coup, bien plus vite qu'une boucle ; fixez toujours une **graine** pour les tirages au hasard. polars est une alternative rapide, fondée sur des **expressions** et un mode **paresseux** qui optimise le calcul avant de l'exécuter. `nbconvert` transforme un notebook exécuté en rapport HTML, que l'on peut automatiser.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.10, exercice 4.13.


## Bilan du chapitre 4

Vous savez maintenant :

- **lire** un fichier avec le bon séparateur, la bonne décimale, le bon encodage et les bonnes dates, en Python (`read_csv`) comme en R (`read_csv`, `read_delim`) ; **remettre en état** un export désordonné (titres, total, en-têtes répétés, manquants, textes) et **réconcilier** le résultat avec un total connu ;
- **sélectionner**, **filtrer**, **calculer**, **trier** et **compter** avec pandas (`[]`, `.loc`, `.iloc`, `query`, `assign`, `value_counts`) et avec le tidyverse (`select`, `filter`, `mutate`, `arrange`, `count`), et traduire un langage dans l'autre ;
- **regrouper** (`groupby` et `agg`, `group_by` et `summarise`, `transform` pour les parts), **joindre** sans multiplier les lignes (`validate`, `relationship`) et **restructurer** entre format large et format long (`pivot_table`, `melt`, `pivot_wider`, `pivot_longer`) ;
- **comparer** des périodes avec des moyennes glissantes et des semaines ISO, et **écrire une fonction** qui produit le tableau du lundi ;
- **ranger** une analyse dans un notebook **reproductible** (état caché, « tout exécuter »), produire un rapport avec R Markdown ou Quarto, et reconnaître le moment où passer du notebook au script ;
- (en option) **dessiner** avec `ggplot2` (couches, facettes), tester la logique d'une application Shiny, **vectoriser** un calcul avec NumPy, lire un fichier avec polars, convertir un notebook en rapport HTML.

Le chapitre a mis des chiffres sur la boutique, et chacun a été **obtenu de deux façons** :

| Question | Ce que nous avons mesuré |
|---|---|
| Chiffre d'affaires de 2025 | 1 324 763,72 €, identique en pandas et en R |
| Export de caisse | 285 lignes lues, 280 ventes retenues, 8 montants à reconstituer ; écart de 2,62 € avec le total, expliqué par une remise de 5 % |
| Panier moyen par canal | 100,9 € (boutique), 100,5 € (réseaux), 99,8 € (Site) ; le montant moyen **d'une ligne** est de 43,5 € |
| Part du Site dans le chiffre d'affaires | de 37,1 % en 2023 à 46,6 % en 2025 ; le Site passe devant la boutique en septembre 2024 |
| Taux de retour par canal | 3,1 % (boutique), 6,7 % (réseaux), 9,0 % (Site) ; 221 010 € remboursés, soit 6,05 % du chiffre d'affaires |
| Tableau du lundi, semaine 45 de 2025 | 30 240,0 € contre 27 729,4 € (+9,1 %) ; boutique −9,6 %, Site +16,6 %, réseaux +60,4 % sur une petite base |
| Notebook | le même code donne 90 ou 80 selon l'ordre d'exécution des cellules |

Trois idées dépassent ce chapitre. **D'abord, écrire une analyse comme un programme la rend refaisable** : la gérante obtient son tableau chaque lundi, vous gagnez une heure, et l'erreur de ligne de la collègue disparaît. **Ensuite, la vérification croisée est un réflexe** : un chiffre obtenu par deux outils indépendants (pandas et R, la base et l'export de caisse) mérite confiance ; un écart est une information. **Enfin, un pourcentage sans le montant qui le porte, ou une moyenne sans la précision de ce qui est moyenné, trompe** : la moyenne d'une ligne n'est pas celle d'une commande, et +60 % sur une petite base n'est pas une tendance.

> 🧭 **En pratique : liste de contrôle avant de livrer un chiffre.**
> 1. Les données ont été **lues avec les bons arguments**, et on les a **regardées** (`head`, `dtypes`, `glimpse`).
> 2. Les **manquants** ont été comptés, et l'on sait pourquoi ils manquent.
> 3. Chaque **jointure** a été validée (`validate`, `relationship`) : le nombre de lignes n'a pas bougé sans raison.
> 4. Un **total connu** a été retrouvé (un export, un tableau de bord, un autre outil).
> 5. Le calcul a été **refait** dans un second outil, ou par une seconde méthode.
> 6. Le notebook ou le script s'exécute **de haut en bas** dans une session neuve.
> 7. Le chiffre est accompagné de **ce qu'il mesure** (moyenne de quoi, sur quelle période, avec quelle base).

Le chapitre 5 clôt ce volume en remontant à la source : **d'où viennent les données** ? Il décrit les types de données et leurs niveaux de mesure, les grandes familles de sources, et la conception d'une enquête, de l'enquête de satisfaction de la boutique à ses biais.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.10 (premier contact avec pandas, filtres, traduction en tidyverse, export de caisse, jointure et marge, restructuration, tableau du lundi, notebook reproductible, ggplot2, polars et NumPy) et exercices 4.1 à 4.13.
