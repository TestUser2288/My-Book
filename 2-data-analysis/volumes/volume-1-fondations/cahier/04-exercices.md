# Chapitre 4 : Python et R pour l'analyse — exercices et applications

> 🧭 **Comment utiliser ce chapitre.** Les **applications** sont de petites études guidées sur les données de la boutique : lisez l'énoncé, essayez, puis comparez avec le code et la lecture proposés. Les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ difficile) renvoient chacun à une section du livre ; leurs **corrigés** sont à la fin. Chaque bloc de code est court et peut être exécuté tel quel. Tout est **simulé** : la boutique n'existe pas. Le chapitre est **autonome** : il recharge ses données et ses bibliothèques.

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
options(tidyverse.quiet = TRUE, width = 100, pillar.width = 100, pillar.sigfig = 7)
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

## Applications

### Application 4.1 — Premier contact avec les commandes (sections 4.1.2 à 4.1.4)

**Objectif.** Lire une table avec pandas, la regarder, la découper. **Question.** Sur quelle période les commandes s'étalent-elles, combien de clients différents ont commandé, et combien de commandes par an ?

**Étape 1 — Lire et regarder.** On lit `commandes.csv` en précisant la colonne de dates.

```python
commandes = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
print(commandes.shape)
print(commandes["date_commande"].min().date(), commandes["date_commande"].max().date())
print(commandes["id_client"].nunique())
```
<!--sortie-->
```text
(36395, 7)
2023-01-01 2025-12-31
4806
```

**Étape 2 — Compter par année.** On extrait l'année de la date avec `dt.year`, puis on compte et on trie par année.

```python
print(commandes["date_commande"].dt.year.value_counts().sort_index())
```
<!--sortie-->
```text
date_commande
2023    11418
2024    12031
2025    12946
Name: count, dtype: int64
```

**Étape 3 — Sélectionner.** Les trois premières commandes du Site, avec trois colonnes seulement.

```python
print(commandes.loc[commandes["canal"] == "Site", ["id_commande", "date_commande", "code_promo"]].head(3))
```
<!--sortie-->
```text
    id_commande date_commande code_promo
0             1    2023-01-01        NaN
8             9    2023-01-01   FIDELITE
10           11    2023-01-01        NaN
```

**Lecture.** La table compte 36 395 commandes, du 1er janvier 2023 au 31 décembre 2025, passées par 4 806 clients différents (sur 6 000 inscrits : tous n'ont pas commandé pendant la période). Le nombre de commandes par an passe de 11 418 à 12 031 puis 12 946, soit environ +5 % puis +8 %. Les numéros de ligne 0, 8 et 10 affichés à gauche des commandes du Site rappellent que `.loc` conserve les **étiquettes** de la table d'origine.

### Application 4.2 — Les retours (sections 4.1.5 à 4.1.7)

**Objectif.** Filtrer, compter, repérer les manquants. **Question.** Quels sont les motifs de retour, et combien de retours dépassent 100 € ?

**Étape 1 — Lire et résumer.** `describe` donne les statistiques de la colonne des montants remboursés.

```python
retours = pd.read_csv("donnees/retours.csv", parse_dates=["date_retour"])
print(retours["montant_rembourse"].describe().round(1))
print(retours.isna().sum().sum())
```
<!--sortie-->
```text
count    5002.0
mean       44.2
std        39.9
min         2.3
25%        18.9
50%        32.9
75%        56.6
max       472.5
Name: montant_rembourse, dtype: float64
0
```

**Étape 2 — Les motifs.** Les proportions de chaque motif, en pourcentage.

```python
print((retours["motif"].value_counts(normalize=True) * 100).round(1))
```
<!--sortie-->
```text
motif
Mauvais choix        31.4
Changement d'avis    30.3
Défaut               18.2
Livraison tardive    12.1
Autre                 8.0
Name: proportion, dtype: float64
```

**Étape 3 — Filtrer.** Les retours de 100 € ou plus, puis ceux de 100 € ou plus **et** motivés par un défaut.

```python
gros = retours[retours["montant_rembourse"] >= 100]
print(len(gros), len(gros[gros["motif"] == "Défaut"]))
```
<!--sortie-->
```text
437 83
```

**Lecture.** Les 5 002 retours n'ont aucune valeur manquante. Un retour rembourse en moyenne 44,2 €, mais la **médiane** est de 32,9 € et le maximum de 472,5 € : quelques gros remboursements tirent la moyenne vers le haut (c'est le signe d'une distribution asymétrique, vue en 1.1). « Mauvais choix » (31,4 %) et « Changement d'avis » (30,3 %) représentent six retours sur dix ; les défauts de produit n'en sont que 18,2 %. Au total, 437 retours dépassent 100 €, dont 83 pour un défaut.

### Application 4.3 — Le même travail en R (section 4.2)

**Objectif.** Traduire les applications 4.1 et 4.2 en tidyverse, et vérifier que les chiffres coïncident. **Étape 1 — Les commandes.** Le nombre de lignes, le nombre de clients distincts, les commandes par année.

```r
commandes <- read_csv("donnees/commandes.csv", show_col_types = FALSE)
cat(nrow(commandes), n_distinct(commandes$id_client), "\n")
par_annee <- commandes |> count(annee = year(date_commande))
par_annee
```
<!--sortie-->
```text
36395 4806 
# A tibble: 3 × 2
  annee     n
  <dbl> <int>
1  2023 11418
2  2024 12031
3  2025 12946
```

**Étape 2 — Les retours.** Les motifs en pourcentage, et le nombre de retours d'au moins 100 €.

```r
retours <- read_csv("donnees/retours.csv", show_col_types = FALSE)
motifs <- retours |> count(motif, sort = TRUE) |> mutate(pct = round(100 * n / sum(n), 1))
motifs
cat(sum(retours$montant_rembourse >= 100), "\n")
```
<!--sortie-->
```text
# A tibble: 5 × 3
  motif                 n   pct
  <chr>             <int> <dbl>
1 Mauvais choix      1571  31.4
2 Changement d'avis  1518  30.3
3 Défaut              908  18.2
4 Livraison tardive   605  12.1
5 Autre               400   8  
437 
```

**Étape 3 — Vérifier.** Les deux langages donnent-ils les mêmes comptes ? Le bloc caché écrit les résultats de pandas et les compare ; son verdict s'affiche ci-dessous.

```python hide
O.pont_ecrire(commandes["date_commande"].dt.year.value_counts().sort_index().rename_axis("annee").reset_index(name="n"), "par_annee")
O.pont_ecrire(pd.DataFrame({"n": [len(gros)]}), "gros")
```

```r hide-code
verifier(par_annee, "par_annee", nd = 0)
verifier(tibble(n = sum(retours$montant_rembourse >= 100)), "gros", nd = 0)
```
<!--sortie-->
```text
identique au résultat de pandas : TRUE 
identique au résultat de pandas : TRUE 
```

**Lecture.** Les deux langages donnent les mêmes comptes (36 395 lignes, 4 806 clients, les mêmes effectifs par année, 437 retours d'au moins 100 €). Notez deux différences de forme : `count(annee = year(date_commande))` crée la variable **à l'intérieur** de `count`, et R appelle `n` la colonne des effectifs.

### Application 4.4 — Remettre en état l'export de caisse (section 4.3.1)

**Objectif.** Transformer un fichier fait pour être lu par un humain en une table exploitable, et le **réconcilier**. **Question.** Quel est le chiffre d'affaires de la semaine par catégorie, et quels sont les cinq articles les plus vendus ?

**Étape 1 — Lire en sautant les titres.** Tout est lu en texte (les lignes parasites empêchent toute conversion).

```python
brut = pd.read_csv("donnees/export_caisse_brut.csv", sep=";", encoding="cp1252", skiprows=3)
print(brut.shape)
```
<!--sortie-->
```text
(285, 8)
```

**Étape 2 — Écarter les lignes parasites et convertir.**

```python
caisse = brut[brut["N° ticket"].notna() & (brut["N° ticket"] != "N° ticket")].copy()
caisse["Date"] = pd.to_datetime(caisse["Date"], format="%d/%m/%Y")
for col in ["Qté", "Prix unitaire", "Montant"]:
    caisse[col] = pd.to_numeric(caisse[col].str.replace(",", "."))
caisse["Montant"] = caisse["Montant"].fillna((caisse["Qté"] * caisse["Prix unitaire"]).round(2))
caisse["Catégorie"] = caisse["Catégorie"].str.capitalize()
caisse["Article"] = caisse["Article"].str.capitalize()
print(len(caisse), round(caisse["Montant"].sum(), 2))
```
<!--sortie-->
```text
280 11564.09
```

**Étape 3 — Répondre à la question.**

```python
print(caisse.groupby("Catégorie")["Montant"].sum().round(2).sort_values(ascending=False))
print(caisse.groupby("Article")["Qté"].sum().sort_values(ascending=False).head(5))
```
<!--sortie-->
```text
Catégorie
Maison        3033.93
Décoration    2882.50
Cuisine       2441.00
Jardin        1482.25
Bien-être     1114.11
Papeterie      610.30
Name: Montant, dtype: float64
Article
Bougie nordique    16
Huile mat          15
Cadre design       11
Bol design         11
Lampe design       11
Name: Qté, dtype: int64
```

**Étape 4 — Réconcilier.** Le total du fichier est de 11 561,47 € : où se situe l'écart ?

```python
total_fichier = float(brut.iloc[-1]["Montant"].replace(",", "."))
print(round(caisse["Montant"].sum() - total_fichier, 2))
```
<!--sortie-->
```text
2.62
```

**Lecture.** Sur les 280 ventes retenues, le chiffre d'affaires reconstitué est de 11 564,09 €, soit 2,62 € de plus que le total du fichier : c'est la remise de 5 % d'une ligne dont le montant manquait (voir 4.3.1). Par catégorie, la maison arrive en tête (3 033,93 €), devant la décoration (2 882,50 €) et la cuisine (2 441,00 €) ; la papeterie ferme la marche (610,30 €). L'article le plus vendu est la bougie nordique (16 pièces), devant l'huile mat (15).

### Application 4.5 — Jointures et marge par produit (sections 4.3.2 et 4.3.3)

**Objectif.** Relier trois tables et calculer des marges. **Question.** Quels sont les cinq produits qui rapportent la plus grande **marge** totale, et la marge dépend-elle du canal ?

**Étape 1 — Construire la table de ventes.** Lignes, commandes et produits, avec `validate` pour garantir qu'aucune ligne n'est multipliée.

```python
lignes = pd.read_csv("donnees/lignes_commande.csv")
produits = pd.read_csv("donnees/produits.csv")
ventes = (lignes.merge(commandes, on="id_commande", validate="m:1")
                .merge(produits[["id_produit", "nom_produit", "categorie", "cout_achat"]], on="id_produit", validate="m:1"))
print(len(lignes), len(ventes))
```
<!--sortie-->
```text
83905 83905
```

**Étape 2 — La marge de chaque ligne.** Marge = montant payé − quantité × coût d'achat.

```python
ventes["marge"] = ventes["montant"] - ventes["quantite"] * ventes["cout_achat"]
top = ventes.groupby("nom_produit")["marge"].sum().sort_values(ascending=False).head(5)
print(top.round(0))
```
<!--sortie-->
```text
nom_produit
Transat nordique      96041.0
Jardinière design     73806.0
Statuette rustique    68237.0
Lanterne mat          59265.0
Lampe design          58435.0
Name: marge, dtype: float64
```

**Étape 3 — La marge par canal.**

```python
par_canal = ventes.groupby("canal")[["marge", "montant"]].sum()
print((par_canal["marge"] / par_canal["montant"] * 100).round(1))
```
<!--sortie-->
```text
canal
Boutique    47.4
Réseaux     47.3
Site        47.4
dtype: float64
```

**Lecture.** La jointure garde les 83 905 lignes : aucune n'a été multipliée. Les cinq produits à la plus grande marge totale sont le transat nordique (96 041 €), la jardinière design (73 806 €), la statuette rustique (68 237 €), la lanterne mat (59 265 €) et la lampe design (58 435 €) ; trois d'entre eux sont des articles de jardin. Le **taux** de marge est le même dans les trois canaux (47,3 à 47,4 %) : le canal change le volume, pas la marge unitaire.

### Application 4.6 — Restructurer : le chiffre d'affaires de chaque canal, mois par mois (section 4.3.4)

**Objectif.** Passer du format long au format large et inversement, puis calculer une part. **Question.** Quelle part du chiffre d'affaires mensuel de 2025 le Site représente-t-il, et en quel mois est-elle la plus élevée ?

**Étape 1 — Le format large.** Un tableau mois × canal pour 2025.

```python
v25 = ventes[ventes["date_commande"].dt.year == 2025].assign(mois=lambda d: d["date_commande"].dt.month)
large = v25.pivot_table(index="mois", columns="canal", values="montant", aggfunc="sum").round(0)
print(large.head(3))
```
<!--sortie-->
```text
canal  Boutique  Réseaux     Site
mois                             
1       38882.0   8938.0  41358.0
2       33079.0   5479.0  34084.0
3       39039.0   8440.0  42308.0
```

**Étape 2 — La part du Site.**

```python
part_site = (large["Site"] / large.sum(axis=1) * 100).round(1)
print(part_site.idxmax(), part_site.max(), part_site.idxmin(), part_site.min())
```
<!--sortie-->
```text
9 49.0 8 41.5
```

**Étape 3 — Revenir au format long**, comme le demanderait un graphique.

```python
long = large.reset_index().melt(id_vars="mois", var_name="canal", value_name="ca")
print(long.shape, long.head(2))
```
<!--sortie-->
```text
(36, 3)    mois     canal       ca
0     1  Boutique  38882.0
1     2  Boutique  33079.0
```

**Étape 4 — En R**, avec `pivot_wider` puis `pivot_longer`.

```r
ventes_r <- read_csv("donnees/lignes_commande.csv", show_col_types = FALSE) |>
  left_join(read_csv("donnees/commandes.csv", show_col_types = FALSE), by = "id_commande")
large_r <- ventes_r |> filter(year(date_commande) == 2025) |> group_by(mois = month(date_commande), canal) |>
  summarise(ca = round(sum(montant)), .groups = "drop") |> pivot_wider(names_from = canal, values_from = ca)
long_r <- pivot_longer(large_r, -mois, names_to = "canal", values_to = "ca")
cat(dim(long_r), "\n")
```
<!--sortie-->
```text
36 3 
```

```python hide
O.pont_ecrire(large.reset_index(), "large_mois")
```

```r hide-code
verifier(large_r, "large_mois", nd = 0)
```
<!--sortie-->
```text
identique au résultat de pandas : TRUE 
```

**Lecture.** En janvier 2025, la boutique réalise 38 882 €, les réseaux 8 938 € et le Site 41 358 €. La part du Site est la plus élevée en septembre (49,0 %) et la plus basse en août (41,5 %). Le format long compte 36 lignes (12 mois × 3 canaux), et la version R, avec `pivot_wider` puis `pivot_longer`, donne un tableau identique.

### Application 4.7 — Le tableau du lundi, en fonction (sections 4.3.5 et 4.3.6)

**Objectif.** Écrire une fonction qui, à partir d'une **date du jour**, produit le tableau de la semaine **qui vient de s'achever**, et qui refuse de répondre si la semaine n'est pas complète. **Question.** Que renvoie-t-elle le lundi 10 novembre 2025 ? Et le lundi 5 janvier 2026 ?

**Étape 1 — Les ventes par semaine ISO.**

```python
iso = ventes["date_commande"].dt.isocalendar()
ventes = ventes.assign(annee_iso=iso["year"].astype(int), semaine=iso["week"].astype(int))
sem = ventes.groupby(["annee_iso", "semaine", "canal"], as_index=False)["montant"].sum()
```

**Étape 2 — La semaine terminée, pour une date donnée.** On retranche sept jours, on lit l'année et la semaine ISO, et on vérifie que les données vont jusqu'au dimanche.

```python
def semaine_terminee(date):
    d = pd.Timestamp(date) - pd.Timedelta(days=7)
    iso = d.isocalendar()
    dimanche = d + pd.Timedelta(days=6 - d.weekday())
    if ventes["date_commande"].max() < dimanche:
        raise ValueError(f"semaine {iso.year}-S{iso.week:02d} incomplète : les données s'arrêtent au {ventes['date_commande'].max().date()}")
    return int(iso.year), int(iso.week)
```

**Étape 3 — Le tableau.** On réutilise la fonction `tableau_du_lundi` du livre (4.3.6), reprise ici.

```python
def tableau_du_lundi(semaine, annee):
    cur = sem[(sem.annee_iso == annee) & (sem.semaine == semaine)].set_index("canal")["montant"]
    pre = sem[(sem.annee_iso == annee - 1) & (sem.semaine == semaine)].set_index("canal")["montant"]
    t = pd.DataFrame({"cette_semaine": cur, "meme_semaine_an_dernier": pre})
    t.loc["Total"] = t.sum()
    t["evolution_pct"] = (t["cette_semaine"] / t["meme_semaine_an_dernier"] - 1) * 100
    return t.round(1)

annee, semaine = semaine_terminee("2025-11-10")
print(annee, semaine)
print(tableau_du_lundi(semaine, annee))
```
<!--sortie-->
```text
2025 45
          cette_semaine  meme_semaine_an_dernier  evolution_pct
canal                                                          
Boutique        11561.5                  12783.9           -9.6
Réseaux          4581.9                   2856.3           60.4
Site            14096.7                  12089.2           16.6
Total           30240.0                  27729.4            9.1
```

**Étape 4 — Le cas limite.**

```python
try:
    semaine_terminee("2026-01-05")
except ValueError as e:
    print("refus :", e)
```
<!--sortie-->
```text
refus : semaine 2026-S01 incomplète : les données s'arrêtent au 2025-12-31
```

**Lecture.** Le lundi 10 novembre 2025, la fonction renvoie la semaine 45 de 2025 et le même tableau que celui du livre. Le lundi 5 janvier 2026, elle **refuse** : la semaine ISO 2026-S01, du 29 décembre au 4 janvier, n'est connue que jusqu'au 31 décembre. Une fonction qui refuse vaut mieux qu'une fonction qui livre, sans le dire, un tableau fondé sur une semaine incomplète.

### Application 4.8 — Un notebook reproductible (section 4.4)

**Objectif.** Construire un notebook par programme, l'exécuter dans un noyau neuf, vérifier qu'il se reproduit, puis y introduire un état caché et le détecter. **Question.** Le notebook « ventes par canal » donne-t-il le même résultat deux fois de suite ?

**Étape 1 — Les cellules.**

```python
cellules = [
    ("md", "# Commandes par canal"),
    ("code", "import pandas as pd\nc = pd.read_csv('donnees/commandes.csv')"),
    ("code", "res = c['canal'].value_counts().sort_index()\nprint(res.to_dict())"),
]
```

**Étape 2 — Exécuter deux fois, comparer.**

```python
nb_a, err_a = O.executer_notebook(cellules, os.getcwd())
nb_b, err_b = O.executer_notebook(cellules, os.getcwd())
print(O.sorties_texte(nb_a)[-1])
print(O.sorties_texte(nb_a) == O.sorties_texte(nb_b), err_a, err_b)
```
<!--sortie-->
```text
{'Boutique': 16975, 'Réseaux': 3957, 'Site': 15463}
True None None
```

**Étape 3 — Un état caché.** On ajoute une cellule qui utilise une variable définie **plus bas**. Exécutée de haut en bas dans un noyau neuf, elle échoue.

```python
cellules_bug = cellules[:2] + [("code", "print(len(c) * coefficient)"), ("code", "coefficient = 2")]
_, erreur = O.executer_notebook(cellules_bug, os.getcwd())
print(erreur)
```
<!--sortie-->
```text
NameError: name 'coefficient' is not defined
```

**Lecture.** Le notebook donne deux fois le même résultat (`{'Boutique': 16975, 'Réseaux': 3957, 'Site': 15463}`) et sans erreur : c'est le test de reproductibilité de base. La version avec la variable définie **après** son usage échoue avec une `NameError` dans un noyau neuf. Dans une session où la dernière cellule avait déjà été exécutée, l'erreur serait passée inaperçue : c'est l'état caché de 4.4.2.

### Application 4.9 — Un graphique avec ggplot2 (section 4.5)

**Objectif.** Produire un graphique lisible avec trois couches. **Question.** Comment les commandes hebdomadaires de 2025 se comparent-elles à celles de 2024, canal par canal ?

**Étape 1 — Préparer les données (format long).**

```r
hebdo <- ventes_r |> mutate(annee_iso = isoyear(date_commande), semaine = isoweek(date_commande)) |>
  filter(annee_iso %in% c(2024, 2025), semaine <= 52) |>
  group_by(annee_iso, semaine, canal) |> summarise(ca = sum(montant) / 1000, .groups = "drop")
cat(nrow(hebdo), "\n")
```
<!--sortie-->
```text
312 
```

**Étape 2 — Le graphique.** Une facette par canal, une couleur par année.

```r
g <- ggplot(hebdo, aes(x = semaine, y = ca, colour = factor(annee_iso))) +
  geom_line(linewidth = 0.8) +
  facet_wrap(~canal, ncol = 1, scales = "free_y") +
  scale_colour_manual(values = c("2024" = "#898781", "2025" = "#2a78d6")) +
  labs(x = "semaine ISO", y = "milliers d'€", colour = NULL) +
  theme_minimal(base_size = 10) + theme(legend.position = "top")
ggsave("figures/ch04-c-hebdo.png", g, width = 7.5, height = 5.2, dpi = 200)
```

![Chiffre d'affaires hebdomadaire par canal (milliers d'€), 2025 contre 2024. Attention : l'échelle verticale diffère d'une facette à l'autre.](figures/ch04-c-hebdo.png)

**Étape 3 — Compter les semaines gagnantes.** Dans combien de semaines sur 52 l'année 2025 devance-t-elle 2024, canal par canal ?

```r
hebdo |> pivot_wider(names_from = annee_iso, values_from = ca) |>
  group_by(canal) |> summarise(semaines_2025_devant = sum(`2025` > `2024`))
```
<!--sortie-->
```text
# A tibble: 3 × 2
  canal    semaines_2025_devant
  <chr>                   <int>
1 Boutique                   22
2 Réseaux                    28
3 Site                       44
```

**Lecture.** L'année 2025 devance 2024 pendant 44 semaines sur 52 sur le Site, 28 sur les réseaux et seulement 22 en boutique : on retrouve, semaine par semaine, le diagnostic annuel de 4.3.2 (le Site gagne, la boutique recule). L'échelle verticale est libre (`scales = "free_y"`) : elle laisse voir la forme de chaque courbe, mais interdit de comparer la hauteur d'une facette à celle d'une autre.

### Application 4.10 — polars et NumPy (section 4.6)

**Objectif.** Refaire un calcul avec polars (en mode paresseux) et un autre avec NumPy, et les confronter à pandas. **Question.** Combien de commandes tombent dans chaque tranche de montant (moins de 50 €, de 50 à 150 €, plus de 150 €) ?

**Étape 1 — Avec polars, en mode paresseux.**

```python
import polars as pl
pl.Config.set_tbl_formatting("MARKDOWN")
pl.Config.set_tbl_hide_dataframe_shape(True)
paniers_pl = (pl.scan_csv("donnees/lignes_commande.csv").group_by("id_commande").agg(panier=pl.col("montant").sum())
              .with_columns(tranche=pl.when(pl.col("panier") < 50).then(pl.lit("1 : moins de 50 €"))
                            .when(pl.col("panier") <= 150).then(pl.lit("2 : de 50 à 150 €")).otherwise(pl.lit("3 : plus de 150 €")))
              .group_by("tranche").agg(commandes=pl.len()).sort("tranche").collect())
print(paniers_pl)
```
<!--sortie-->
```text
| tranche           | commandes |
| ---               | ---       |
| str               | u32       |
|-------------------|-----------|
| 1 : moins de 50 € | 10874     |
| 2 : de 50 à 150 € | 17990     |
| 3 : plus de 150 € | 7531      |
```

**Étape 2 — Avec NumPy et pandas**, par le « si » vectorisé.

```python
panier = lignes.groupby("id_commande")["montant"].sum().to_numpy()
tranche = np.where(panier < 50, "1", np.where(panier <= 150, "2", "3"))
comptes = pd.Series(tranche).value_counts().sort_index()
print(comptes.to_dict(), (comptes.to_numpy() == paniers_pl["commandes"].to_numpy()).all())
```
<!--sortie-->
```text
{'1': 10874, '2': 17990, '3': 7531} True
```

**Lecture.** Les deux calculs donnent les mêmes effectifs : 10 874 commandes de moins de 50 € (30 %), 17 990 de 50 à 150 € (49 %) et 7 531 de plus de 150 € (21 %). Le mode paresseux de polars n'a rien exécuté avant `collect()` ; le « si » vectorisé de NumPy remplace une boucle sur 36 395 commandes.

## Exercices

### Exercice 4.1 ⭐ — Types et lecture (section 4.1.3)

Lisez `clients.csv` **sans** puis **avec** l'argument `parse_dates=["date_inscription"]`. Quel est le type de `date_inscription` dans chaque cas ? Combien de clients se sont inscrits en 2024 ? Quelle est l'année de naissance médiane ?

### Exercice 4.2 ⭐ — `.loc` contre `.iloc` (section 4.1.4)

Sur la table `commandes`, combien de lignes renvoient `commandes.loc[0:4]` et `commandes.iloc[0:4]` ? Expliquez la différence. Que renvoie `commandes.loc[commandes["canal"] == "Site"].iloc[0]["id_commande"]` ?

### Exercice 4.3 ⭐ — Filtres combinés (section 4.1.5)

Combien de commandes ont été passées **sur le Site**, **en 2024**, avec une livraison **à domicile** **et** un code promotionnel renseigné ? Écrivez le filtre avec des booléens, puis avec `query`, et vérifiez que les deux comptes sont égaux.

### Exercice 4.4 ⭐⭐ — Colonnes calculées (section 4.1.6)

Dans `lignes_commande.csv`, ajoutez la colonne `remise_eur` (le montant de la remise de chaque ligne, en euros). Quelle part des lignes a une remise ? Quel est le montant total des remises accordées sur trois ans ?

### Exercice 4.5 ⭐ — Manquants et comptages (section 4.1.7)

Dans `commandes`, quelle proportion de commandes n'a **aucun** code promotionnel, canal par canal ? Remplacez les manquants par « aucun » et vérifiez que la somme des effectifs par code égale le nombre de commandes.

### Exercice 4.6 ⭐ — Traduire en tidyverse (section 4.2)

Écrivez en R, avec le tube : les **trois villes** qui comptent le plus de clients inscrits **avant 2023** (utilisez `clients.csv`). Écrivez ensuite la version pandas et comparez.

### Exercice 4.7 ⭐⭐ — Panier moyen par canal et par année (section 4.3.2)

Calculez le **panier moyen** (chiffre d'affaires divisé par le nombre de commandes) pour chaque canal et chaque année, puis la **variation** du panier moyen entre 2023 et 2025. Le panier moyen a-t-il changé de manière notable ?

### Exercice 4.8 ⭐⭐ — Taux de retour par mode de livraison (section 4.3.3)

En reliant `lignes_commande`, `commandes` et `retours`, calculez le **taux de retour** (part des lignes retournées) par **mode de livraison**. Comment l'expliquez-vous ? Vérifiez que les jointures n'ont pas modifié le nombre de lignes.

### Exercice 4.9 ⭐⭐ — Large et long (section 4.3.4)

Construisez le tableau **catégorie × trimestre** du chiffre d'affaires de 2025 (format large), puis son format long, et calculez la **part de chaque trimestre** dans le chiffre d'affaires annuel de chaque catégorie. Quelle catégorie est la plus concentrée sur le quatrième trimestre ?

### Exercice 4.10 ⭐⭐ — Moyenne glissante (section 4.3.5)

Dans `jours_exploitation.csv`, calculez une moyenne glissante du nombre de commandes sur **28 jours**. À quelle date est-elle maximale ? En quoi la moyenne glissante sur 7 jours donne-t-elle une date différente ?

### Exercice 4.11 ⭐⭐⭐ — L'état caché (section 4.4)

Un notebook contient trois cellules : (1) `x = 10`, (2) `y = x * 2`, (3) `x = 100` suivie de `print(y)`. Quelle valeur affiche la dernière cellule quand le notebook est exécuté **de haut en bas** ? Et si l'on exécute (1), (2), (3), puis qu'on **réexécute (2) seule** avant de relire l'écran ? Vérifiez avec `executer_notebook`.

### Exercice 4.12 ⭐⭐⭐ — Année du calendrier contre année ISO (sections 4.3.5 et 4.3.6)

Combien de commandes ont une **année ISO différente** de leur année du calendrier ? Donnez les dates concernées et leur chiffre d'affaires. Que se passerait-il si l'on regroupait par (année du calendrier, semaine ISO) pour construire le tableau du lundi ?

### Exercice 4.13 ⭐⭐ — polars (section 4.6)

Avec polars en mode paresseux, calculez, pour chaque canal, le **nombre de clients distincts** ayant commandé en 2025, et comparez avec pandas.

## Corrigés

### Corrigé 4.1

```python
cl_texte = pd.read_csv("donnees/clients.csv")
cl_dates = pd.read_csv("donnees/clients.csv", parse_dates=["date_inscription"])
print(cl_texte["date_inscription"].dtype, cl_dates["date_inscription"].dtype)
print((cl_dates["date_inscription"].dt.year == 2024).sum(), cl_dates["annee_naissance"].median())
```
<!--sortie-->
```text
str datetime64[us]
666 1982.0
```

Sans `parse_dates`, `date_inscription` est du texte (`str`) ; avec, c'est une date (`datetime64`). 666 clients se sont inscrits en 2024 : ce comptage est direct avec une vraie date (`dt.year`). L'année de naissance médiane est 1982, soit un âge médian d'environ 43 ans en 2025.

### Corrigé 4.2

```python
cmd = pd.read_csv("donnees/commandes.csv")
print(len(cmd.loc[0:4]), len(cmd.iloc[0:4]))
print(cmd.loc[cmd["canal"] == "Site"].iloc[0]["id_commande"])
```
<!--sortie-->
```text
5 4
1
```

`loc[0:4]` renvoie **5** lignes (étiquettes 0 à 4, fin incluse), `iloc[0:4]` en renvoie **4** (positions 0 à 3, fin exclue). La première commande du Site est la numéro 1 : `.iloc[0]` compte à partir de la première ligne **du résultat filtré**, pas de la table d'origine.

### Corrigé 4.3

```python
cm = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
c1 = cm[(cm["canal"] == "Site") & (cm["date_commande"].dt.year == 2024) & (cm["mode_livraison"] == "Domicile") & cm["code_promo"].notna()]
c2 = cm.query("canal == 'Site' and date_commande.dt.year == 2024 and mode_livraison == 'Domicile' and code_promo.notna()")
print(len(c1), len(c2))
```
<!--sortie-->
```text
463 463
```

Les deux écritures donnent 463 commandes. La version booléenne est plus verbeuse mais fonctionne partout ; `query` est plus lisible quand les conditions sont nombreuses.

### Corrigé 4.4

```python
lg = pd.read_csv("donnees/lignes_commande.csv")
lg["remise_eur"] = lg["quantite"] * lg["prix_unitaire"] * lg["remise_pct"] / 100
print(round((lg["remise_eur"] > 0).mean() * 100, 1), round(lg["remise_eur"].sum(), 2))
```
<!--sortie-->
```text
15.8 78316.07
```

15,8 % des lignes ont une remise, pour un total de 78 316,07 € sur trois ans, soit un peu plus de 2 % du chiffre d'affaires (3 653 157 €, vu en 4.6.1).

### Corrigé 4.5

```python
codes = cm["code_promo"].fillna("aucun")
print((cm.assign(sans=cm["code_promo"].isna()).groupby("canal")["sans"].mean() * 100).round(1).to_dict())
print(codes.value_counts().sum() == len(cm))
```
<!--sortie-->
```text
{'Boutique': 84.4, 'Réseaux': 83.9, 'Site': 84.1}
True
```

La part de commandes sans code est de 84,4 % en boutique, 83,9 % sur les réseaux et 84,1 % sur le Site : elle ne dépend pas du canal. La somme des effectifs par code égale bien le nombre de commandes (`True`) : `fillna` n'a perdu aucune ligne.

### Corrigé 4.6

```r
cl <- read_csv("donnees/clients.csv", show_col_types = FALSE)
top_villes <- cl |> filter(date_inscription < as.Date("2023-01-01")) |> count(ville, sort = TRUE) |> head(3)
top_villes
```
<!--sortie-->
```text
# A tibble: 3 × 2
  ville       n
  <chr>   <int>
1 Ville A   579
2 Ville B   497
3 Ville C   417
```

```python
cl_py = pd.read_csv("donnees/clients.csv", parse_dates=["date_inscription"])
print(cl_py[cl_py["date_inscription"] < "2023-01-01"]["ville"].value_counts().head(3).reset_index())
```
<!--sortie-->
```text
     ville  count
0  Ville A    579
1  Ville B    497
2  Ville C    417
```

```python hide
O.pont_ecrire(cl_py[cl_py["date_inscription"] < "2023-01-01"]["ville"].value_counts().head(3).reset_index().rename(columns={"count": "n"}), "top_villes")
```

```r hide-code
verifier(top_villes, "top_villes", nd = 0)
```
<!--sortie-->
```text
identique au résultat de pandas : TRUE 
```

Les trois villes sont la Ville A (579 clients), la Ville B (497) et la Ville C (417), en R comme en pandas ; seul le nom de la colonne de comptage diffère (`n` en R, `count` en pandas).

### Corrigé 4.7

```python
lg2 = pd.read_csv("donnees/lignes_commande.csv")
v = lg2.merge(cm, on="id_commande", validate="m:1").assign(annee=lambda d: d["date_commande"].dt.year)
t = v.groupby(["canal", "annee"]).agg(ca=("montant", "sum"), n=("id_commande", "nunique"))
panier = (t["ca"] / t["n"]).unstack().round(1)
print(panier)
print(((panier[2025] / panier[2023] - 1) * 100).round(1).to_dict())
```
<!--sortie-->
```text
annee      2023  2024   2025
canal                       
Boutique  100.3  99.4  103.1
Réseaux    99.9  99.0  102.4
Site       98.9  98.3  101.6
{'Boutique': 2.8, 'Réseaux': 2.5, 'Site': 2.7}
```

Le panier moyen est d'environ 98 à 100 € dans les trois canaux en 2023 et 2024, et de 101,6 à 103,1 € en 2025 : +2,8 % en boutique, +2,5 % sur les réseaux, +2,7 % sur le Site. La variation est modeste, et correspond à la hausse de prix de 3 % du 1er janvier 2025 (vérité programmée) : le panier n'a pas changé de nature, les prix ont monté.

### Corrigé 4.8

```python
rt = pd.read_csv("donnees/retours.csv")
w = lg2.merge(cm[["id_commande", "mode_livraison", "canal"]], on="id_commande", validate="m:1").assign(retourne=lambda d: d["id_ligne"].isin(rt["id_ligne"]))
print(len(lg2) == len(w))
print((w.groupby("mode_livraison")["retourne"].mean() * 100).round(1).to_dict())
print(pd.crosstab(w["mode_livraison"], w["canal"]).to_string())
```
<!--sortie-->
```text
True
{'Domicile': 8.5, 'Point relais': 8.7, 'Retrait magasin': 3.4}
canal            Boutique  Réseaux   Site
mode_livraison                           
Domicile                0     4949  19728
Point relais            0     3483  13249
Retrait magasin     39362      639   2495
```

Le nombre de lignes est inchangé (`True`). Le taux de retour est de 8,5 % pour la livraison à domicile, 8,7 % en point relais et 3,4 % en retrait magasin. Attention à ne pas conclure que le retrait magasin « évite » les retours : le retrait magasin est presque exclusivement un achat **en boutique** (39 362 lignes sur 42 496), et c'est le **canal** qui explique l'écart (3,1 % en boutique, voir 4.3.3). À canal égal, les modes de livraison se ressemblent. C'est un exemple d'effet de **composition**.

### Corrigé 4.9

```python
pr = pd.read_csv("donnees/produits.csv")
v25 = v[v["annee"] == 2025].merge(pr[["id_produit", "categorie"]], on="id_produit", validate="m:1")
v25 = v25.assign(trimestre=v25["date_commande"].dt.quarter)
large9 = v25.pivot_table(index="categorie", columns="trimestre", values="montant", aggfunc="sum")
part = (large9.div(large9.sum(axis=1), axis=0) * 100).round(1)
print(part)
print(part[4].idxmax(), part[4].max())
```
<!--sortie-->
```text
trimestre      1     2     3     4
categorie                         
Bien-être   23.4  22.1  17.7  36.8
Cuisine     23.0  22.5  18.1  36.3
Décoration  21.3  19.7  17.0  42.0
Jardin       8.4  29.0  40.5  22.0
Maison      24.0  21.6  17.2  37.2
Papeterie   21.6  22.3  20.9  35.2
Décoration 42.0
```

```python
long9 = large9.reset_index().melt(id_vars="categorie", var_name="trimestre", value_name="ca")
print(long9.shape, long9.groupby("trimestre")["ca"].sum().round(0).to_dict())
```
<!--sortie-->
```text
(24, 3) {1: 251609.0, 2: 310783.0, 3: 314572.0, 4: 447800.0}
```

La décoration est la catégorie la plus concentrée sur le quatrième trimestre (42,0 % de son chiffre d'affaires annuel), contre 35 à 37 % pour les autres catégories hors jardin ; le jardin fait exception : 40,5 % au troisième trimestre et seulement 22,0 % au quatrième. Le format long compte 24 lignes (6 catégories × 4 trimestres) et les totaux par trimestre sont de 251 609 €, 310 783 €, 314 572 € et 447 800 €.

### Corrigé 4.10

```python
jr = pd.read_csv("donnees/jours_exploitation.csv", parse_dates=["date"])
jr["g28"] = jr["nb_commandes"].rolling(28).mean()
jr["g7"] = jr["nb_commandes"].rolling(7).mean()
print(jr.loc[jr["g28"].idxmax(), "date"].date(), round(jr["g28"].max(), 1))
print(jr.loc[jr["g7"].idxmax(), "date"].date(), round(jr["g7"].max(), 1))
```
<!--sortie-->
```text
2025-12-25 61.4
2025-12-04 64.4
```

La moyenne glissante sur 28 jours est maximale le 25 décembre 2025 (61,4 commandes par jour sur les 28 derniers jours), celle sur 7 jours le 4 décembre 2025 (64,4). Plus la fenêtre est courte, plus son maximum est sensible à un pic isolé ; la fenêtre longue mesure la tendance de fond.

### Corrigé 4.11

```python
A, B, C, D = ("code", "x = 10"), ("code", "y = x * 2"), ("code", "x = 100"), ("code", "print(y)")
haut_bas, _ = O.executer_notebook([A, B, C, D], os.getcwd())
desordre, _ = O.executer_notebook([A, B, C, B, D], os.getcwd())
print(O.sorties_texte(haut_bas)[-1], O.sorties_texte(desordre)[-1])
```
<!--sortie-->
```text
20 200
```

De haut en bas, la dernière cellule affiche **20** : `y` a été calculé quand `x` valait 10, et ne se met pas à jour quand `x` change. Si l'on réexécute (2) après (3), `y` est recalculé avec `x = 100` et la dernière cellule affiche **200**. Le même document donne donc 20 ou 200 selon l'ordre dans lequel on a cliqué : c'est l'état caché.

### Corrigé 4.12

```python
cmd_iso = cm.assign(iso_an=cm["date_commande"].dt.isocalendar()["year"].astype(int), an=cm["date_commande"].dt.year)
ecart = cmd_iso[cmd_iso["iso_an"] != cmd_iso["an"]]
print(len(ecart), sorted(ecart["date_commande"].dt.date.astype(str).unique()))
ca_ecart = lg2[lg2["id_commande"].isin(ecart["id_commande"])]["montant"].sum()
print(round(ca_ecart, 2))
```
<!--sortie-->
```text
254 ['2023-01-01', '2024-12-30', '2024-12-31', '2025-12-29', '2025-12-30', '2025-12-31']
22186.07
```

254 commandes ont une année ISO différente de leur année du calendrier : celles du 1er janvier 2023 (un dimanche, qui appartient à la semaine 52 de 2022), des 30 et 31 décembre 2024 (semaine 1 de 2025) et des 29, 30 et 31 décembre 2025 (semaine 1 de 2026), pour 22 186,07 € de chiffre d'affaires. Si l'on regroupait par (année du calendrier, semaine ISO), les 30 et 31 décembre 2024 seraient rangés dans « 2024, semaine 1 » avec les premiers jours de janvier **2024** : un même groupe réunirait des jours distants d'un an, et le tableau du lundi de la semaine 1 serait faux.

### Corrigé 4.13

```python
res13 = (pl.scan_csv("donnees/commandes.csv", try_parse_dates=True)
         .filter(pl.col("date_commande").dt.year() == 2025)
         .group_by("canal").agg(clients=pl.col("id_client").n_unique()).sort("canal").collect())
pd13 = cm[cm["date_commande"].dt.year == 2025].groupby("canal")["id_client"].nunique().sort_index()
print(res13)
print((res13["clients"].to_numpy() == pd13.to_numpy()).all())
```
<!--sortie-->
```text
| canal    | clients |
| ---      | ---     |
| str      | u32     |
|----------|---------|
| Boutique | 2731    |
| Réseaux  | 1139    |
| Site     | 2844    |
True
```

En 2025, 2 731 clients distincts ont commandé en boutique, 1 139 sur les réseaux et 2 844 sur le Site ; polars et pandas coïncident (`True`). La somme (6 714) dépasse les 6 000 clients de la base : un même client peut commander dans plusieurs canaux, ce qui interdit d'additionner des clients distincts de canaux différents.
