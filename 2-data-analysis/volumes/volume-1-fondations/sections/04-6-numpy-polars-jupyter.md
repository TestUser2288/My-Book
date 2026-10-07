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

```bash noexec
jupyter nbconvert --to html --execute rapport.ipynb      # non exécuté ici : l'écriture du fichier se fait hors du livre
```

Pour qu'un même notebook serve à plusieurs semaines ou plusieurs canaux, on lui donne des **paramètres** : une cellule de tête fixe la semaine et l'année, qu'un outil (par exemple `papermill`, non installé ici : à vérifier selon votre environnement) remplace avant l'exécution. C'est le principe du tableau du lundi : une seule recette, des paramètres qui changent, des rapports qui se fabriquent seuls.

> ✅ **À retenir.** NumPy est le moteur de calcul de pandas : une opération **vectorisée** s'applique à tout un tableau d'un coup, bien plus vite qu'une boucle ; fixez toujours une **graine** pour les tirages au hasard. polars est une alternative rapide, fondée sur des **expressions** et un mode **paresseux** qui optimise le calcul avant de l'exécuter. `nbconvert` transforme un notebook exécuté en rapport HTML, que l'on peut automatiser.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : application 4.10, exercice 4.13.
