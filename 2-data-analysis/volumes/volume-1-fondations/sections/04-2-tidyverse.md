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

```python hide
O.pont_ecrire(pd.DataFrame({"n": [len(commandes), len(lignes), len(clients), len(retours)]}), "dims")
O.pont_ecrire(pd.DataFrame({"n": [n_query, int(n_isin), int(n_nov)]}), "comptes")
O.pont_ecrire(part_promo.reset_index().rename(columns={"avec_code": "part_promo"}), "part_promo")
```

```r hide-code
verifier(tibble(n = c(nrow(commandes), nrow(lignes), nrow(clients), nrow(retours))), "dims", nd = 0)
```
<!--sortie-->
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

```r hide-code
verifier(tibble(n = c(n1, n2, n3)), "comptes", nd = 0)
```
<!--sortie-->
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

```r hide-code
verifier(part_promo_r, "part_promo", nd = 1)
```
<!--sortie-->
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
