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

```python hide
O.pont_ecrire(pd.DataFrame({"n": [len(caisse), round(caisse["Montant"].sum(), 2), caisse["Catégorie"].nunique(), caisse["Article"].nunique()]}), "caisse")
```

```r hide-code
verifier(tibble(n = c(nrow(caisse_r), round(sum(caisse_r$Montant), 2), n_distinct(caisse_r$Catégorie), n_distinct(caisse_r$Article))), "caisse", nd = 2)
```
<!--sortie-->
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

```python hide
O.pont_ecrire(resume.reset_index(), "resume_canal")
```

```r hide-code
verifier(resume_r, "resume_canal", nd = 1)
```
<!--sortie-->
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

```python hide
O.pont_ecrire(cat_tab.reset_index(), "cat_tab")
```

```r hide-code
verifier(cat_tab_r, "cat_tab", nd = 1)
```
<!--sortie-->
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

```python hide
import fig_ch04 as F
F.fig_large_long()
```
<!--sortie-->
```text
figure : ch04-large-long.png
```

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

```python hide
O.pont_ecrire(lundi.reset_index(), "lundi")
```

```r hide-code
verifier(lundi_r, "lundi", nd = 1)
```
<!--sortie-->
```text
identique au résultat de pandas : TRUE 
```

Les deux langages produisent le même tableau. Une dernière vérification croisée, d'une autre nature : le chiffre d'affaires de la boutique en semaine 45 de 2025 est de **11 561,47 €** dans la table `sem`, et c'est **exactement** le total que l'export de caisse de la section 4.3.1 annonçait. Le fichier désordonné, remis en état à la main, et les données de la base racontent la même histoire : les chiffres sont fiables.

```python hide
import fig_ch04 as F
F.fig_semaines(sem)
```
<!--sortie-->
```text
figure : ch04-semaines.png
```

![Chiffre d'affaires hebdomadaire total (milliers d'€) par semaine ISO, 2025 contre 2024. Le point orange est la semaine 45, celle du tableau du lundi.](figures/ch04-semaines.png)

Il reste à « automatiser » : rendre la fonction capable de produire, sans intervention, le tableau de la **semaine qui vient de s'achever**. À partir de la date du jour, `isocalendar()` donne l'année et le numéro de la semaine ISO ; on retranche une semaine pour avoir la semaine **terminée**, puis on appelle la fonction. Le programme complet tient dans un fichier de script, que l'ordinateur lance de lui-même chaque lundi matin grâce à un planificateur de tâches (`cron` sur Linux, le Planificateur de tâches de Windows).

```bash noexec
# crontab : chaque lundi à 7 h, exécuter le script qui écrit le tableau dans le dossier partagé
0 7 * * 1  cd /chemin/vers/le/projet && python tableau_du_lundi.py
```

> ✅ **À retenir.** Un fichier étranger se lit en trois temps : **regarder**, **lire avec les bons arguments**, **nettoyer** ; et toute transformation se **réconcilie** avec un chiffre connu. Regrouper, c'est répondre à « combien **par** quoi ? » : `groupby` + `agg` (pandas), `group_by` + `summarise` (dplyr), `transform` ou `mutate` pour les parts. Une jointure gauche **ajoute** des informations ; vérifiez avec `validate` / `relationship` qu'elle ne **multiplie** pas les lignes. Le format large se lit, le format long se calcule. Pour comparer des semaines, utilisez les **semaines ISO** et l'**année ISO**, et ne livrez jamais un pourcentage sans le montant qui le porte.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.4 à 4.7, exercices 4.7 à 4.10 et 4.12.
