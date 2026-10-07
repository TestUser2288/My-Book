## 2.1 Création et dérivation de variables

Les tables que l'on reçoit contiennent rarement **les colonnes dont on a besoin** : la caisse note un prix et une quantité, mais pas la marge ; la table des commandes porte une date, mais ni le trimestre ni le jour de la semaine ; le fichier clients a une année de naissance, mais pas la tranche d'âge. Une **variable dérivée** est une colonne que l'on **calcule** à partir des autres. Cette section apprend à en fabriquer de cinq sortes (des calculs, des morceaux de date, des classes, des indicateurs et des délais), à les **documenter**, et à éviter les trois pièges qui les abîment : la division par zéro, la valeur manquante qui se propage et la fuite d'information.

### 2.1.1 Une variable dérivée est une décision

Calculer « la marge d'une ligne de vente » paraît mécanique. Pourtant, avant d'écrire la première formule, **quatre décisions** sont déjà prises, et elles changent le chiffre :

1. **Quelle définition ?** La marge est-elle calculée avant ou après remise ? Sur le prix toutes taxes comprises, ou hors taxe ? Avec le coût d'achat seul, ou avec les frais de transport ?
2. **Quelle unité ?** Des euros, un pourcentage du prix de vente (le **taux de marge**) ou du coût d'achat (le **taux de marque**) ? Les trois se confondent souvent à l'oral, et ne valent pas la même chose (volume I, section 1.5.4).
3. **Quelle date de référence ?** Le coût d'achat d'aujourd'hui, ou celui de la date de la vente ?
4. **Que faire des cas limites ?** Une vente à zéro euro, un produit sans coût d'achat, un retour.

Chacune de ces décisions est un **choix de métier**, pas de technique. C'est pourquoi on **écrit** la définition de chaque variable créée (nous y reviendrons en 2.1.7), et pourquoi deux analystes qui calculent « la marge » sans s'être parlé obtiennent deux chiffres. Par convention, dans ce chapitre : la **marge brute** d'une ligne est son **chiffre d'affaires hors taxe** moins sa **quantité multipliée par le coût d'achat** ; la **TVA** est fixée à 20 % **pour l'illustration**, et le **taux de marge** est la marge divisée par le chiffre d'affaires hors taxe.

> 💡 **Intuition.** Une variable dérivée est une **phrase** qu'on a figée dans une colonne. Si la phrase est ambiguë (« la marge »), la colonne l'est aussi, et personne ne s'en apercevra avant qu'un chiffre ne soit contesté en réunion.

### 2.1.2 Calculs simples : marges, ratios, montants

Commençons par la demande de la gérante : une marge par ligne de vente. La table des lignes contient le **montant payé** (toutes taxes comprises, après remise) ; le coût d'achat est dans la table des produits. Il faut donc d'abord **relier** les deux tables (nous détaillerons la jointure en 2.2), puis calculer.

```python
lig = pd.read_csv("donnees/lignes_commande.csv")
prod = pd.read_csv("donnees/produits.csv")
x = lig.merge(prod[["id_produit", "nom_produit", "categorie", "cout_achat"]], on="id_produit", validate="m:1")
x["ca_ht"] = x["montant"] / 1.20
x["marge_ht"] = x["ca_ht"] - x["quantite"] * x["cout_achat"]
x["taux_marge"] = x["marge_ht"] / x["ca_ht"]
cols = ["id_ligne", "nom_produit", "quantite", "montant", "marge_ht", "taux_marge"]
print(x[cols].head(4).round(3).to_string(index=False))
```
<!--sortie-->
```text
 id_ligne           nom_produit  quantite  montant  marge_ht  taux_marge
        1       Étagère compact         1     33.9    13.040       0.462
        2 Set de table rustique         1     49.9    18.523       0.445
        3       Bougie nordique         1     28.9    11.203       0.465
        4       Miroir rustique         2     51.8    18.627       0.432
```
<!--sortie-->

Vérifions la première ligne **à la main**, comme on le ferait avant de faire confiance à une colonne. Un article payé 33,90 € toutes taxes comprises vaut 33,90 / 1,20 = 28,25 € hors taxe ; son coût d'achat est de 15,21 € ; la marge est donc 28,25 − 15,21 = 13,04 €, soit 46,2 % du chiffre d'affaires hors taxe. Le code a donné la même valeur : on peut généraliser.

```python hide
l1 = x.iloc[0]
NUM("l1_montant", l1["montant"]); NUM("l1_ca_ht", l1["ca_ht"]); NUM("l1_cout", l1["quantite"] * l1["cout_achat"])
NUM("l1_marge", l1["marge_ht"]); NUM("l1_taux", l1["taux_marge"] * 100)
NUM("n_lignes_x", len(x)); NUM("n_lignes_lig", len(lig))
```
<!--sortie-->
```text
NUM l1_montant 33.9
NUM l1_ca_ht 28.25
NUM l1_cout 15.21
NUM l1_marge 13.04
NUM l1_taux 46.159292035398224
NUM n_lignes_x 83905
NUM n_lignes_lig 83905
```

Le contrôle essentiel d'une jointure est visible dans ce que **le code vérifie lui-même** : `validate="m:1"` demande à pandas de s'arrêter si un produit apparaissait deux fois dans la table des produits, ce qui multiplierait les lignes. Ici la jointure est sans histoire : on part de 83 905 lignes et l'on en retrouve 83 905. Passons à ce que la gérante demande vraiment, une vue par catégorie.

```python
par_cat = x.groupby("categorie").agg(ca_ht=("ca_ht", "sum"), marge=("marge_ht", "sum"), taux_moyen_des_lignes=("taux_marge", "mean"))
par_cat["taux_marge"] = par_cat["marge"] / par_cat["ca_ht"]
print(par_cat.round(3).to_string())
```
<!--sortie-->
```text
                 ca_ht       marge  taux_moyen_des_lignes  taux_marge
categorie                                                            
Bien-être   270031.033   91815.643                  0.344       0.340
Cuisine     549163.400  199010.450                  0.359       0.362
Décoration  593853.075  230078.385                  0.374       0.387
Jardin      808649.508  299547.988                  0.375       0.370
Maison      690389.717  254326.397                  0.373       0.368
Papeterie   132211.000   47060.550                  0.364       0.356
```
<!--sortie-->

```python hide
dec = par_cat.loc["Décoration"]
NUM("dec_taux", dec["taux_marge"] * 100); NUM("dec_taux_moyen", dec["taux_moyen_des_lignes"] * 100)
NUM("taux_bien_etre", par_cat.loc["Bien-être", "taux_marge"] * 100); NUM("taux_deco", dec["taux_marge"] * 100)
NUM("taux_global", x["marge_ht"].sum() / x["ca_ht"].sum() * 100)
```
<!--sortie-->
```text
NUM dec_taux 38.74331794947765
NUM dec_taux_moyen 37.386376710636924
NUM taux_bien_etre 34.00188570918578
NUM taux_deco 38.74331794947765
NUM taux_global 36.850515672295394
```

Deux colonnes se ressemblent mais ne disent pas la même chose. Le **taux de marge** d'un groupe est le rapport des **sommes** (la marge totale divisée par le chiffre d'affaires hors taxe total) ; la **moyenne des taux** des lignes donne à une ligne de 5 € le même poids qu'une ligne de 150 €. Pour la décoration, la première vaut 38,7 % et la seconde 37,4 %. **Un ratio d'agrégat se calcule toujours à partir des sommes**, jamais en faisant la moyenne de ratios ; c'est la même règle que pour le panier moyen du volume I. Sur l'ensemble des ventes, le taux de marge brute est de 36,9 %, avec des écarts d'une catégorie à l'autre : de 34,0 % pour le bien-être à 38,7 % pour la décoration.

> ⚠️ **Piège : la remise grignote la marge.** Une remise de 20 % ne coûte pas 20 % **de marge**, mais 20 % **du prix**, c'est-à-dire une part bien plus grande de la marge. Sur nos données, le taux de marge tombe de 38,2 % pour les lignes sans remise à 22,7 % pour celles qui bénéficient de 20 % de remise. Une variable `marge` calculée **avant** remise aurait caché cette érosion.

```python hide
t = x.groupby("remise_pct")["marge_ht"].sum() / x.groupby("remise_pct")["ca_ht"].sum()
NUM("tm_0", t.loc[0] * 100); NUM("tm_20", t.loc[20] * 100)
```
<!--sortie-->
```text
NUM tm_0 38.17077439043137
NUM tm_20 22.657098415138275
```

### 2.1.3 Les dates : en extraire des morceaux

Une date contient plusieurs informations utiles que l'on ne peut pas exploiter tant qu'elles ne sont pas **séparées** : l'année, le trimestre, le mois, la semaine, le jour de la semaine, le week-end. On les extrait avec l'accesseur `.dt`, après avoir **vérifié que la colonne est bien une date** (et non du texte : volume I, section 4.1.3).

```python
cmd = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
d = cmd["date_commande"].dt
cmd["annee"], cmd["trimestre"], cmd["mois"] = d.year, d.quarter, d.month
cmd["semaine_iso"], cmd["jour_semaine"] = d.isocalendar().week, d.dayofweek + 1
cmd["week_end"] = d.dayofweek >= 5
cols = ["id_commande", "date_commande", "annee", "trimestre", "semaine_iso", "jour_semaine", "week_end"]
print(cmd[cols].head(4).to_string(index=False))
```
<!--sortie-->
```text
 id_commande date_commande  annee  trimestre  semaine_iso  jour_semaine  week_end
           1    2023-01-01   2023          1           52             7      True
           2    2023-01-01   2023          1           52             7      True
           3    2023-01-01   2023          1           52             7      True
           4    2023-01-01   2023          1           52             7      True
```
<!--sortie-->

Regardez la première ligne du tableau ci-dessus : le 1er janvier 2023 est rangé dans la **semaine 52**, alors que l'année civile affiche 2023 (c'est la semaine 52 de l'année ISO 2022). Deux conventions méritent d'être **écrites** : `dayofweek` numérote les jours de 0 (lundi) à 6 (dimanche), d'où le `+ 1` pour obtenir 1 à 7 ; et la **semaine ISO** commence le lundi, la semaine 1 étant celle qui contient le premier jeudi de l'année. Cette dernière règle crée un piège redoutable : **les derniers jours de décembre peuvent appartenir à la semaine 1 de l'année suivante**. Le 29 décembre 2025 est un lundi ; il est dans la semaine 1 de l'année **2026**.

```python
jour = pd.Timestamp("2025-12-29")
print(jour.year, jour.isocalendar().year, jour.isocalendar().week)
```
<!--sortie-->
```text
2025 2026 1
```
<!--sortie-->

```python hide
j = pd.Timestamp("2025-12-29").isocalendar()
NUM("iso_an", j.year); NUM("iso_sem", j.week)
NUM("n_cmd_an_iso_diff", (d.isocalendar().year != d.year).sum()); NUM("n_cmd", len(cmd))
```
<!--sortie-->
```text
NUM iso_an 2026
NUM iso_sem 1
NUM n_cmd_an_iso_diff 254
NUM n_cmd 36395
```

Sur nos 36 395 commandes, 254 ont une année ISO différente de leur année civile. Un tableau « chiffre d'affaires par année et par semaine » construit avec `semaine_iso` et `annee` mettrait donc les derniers jours de décembre dans la semaine 1 de **l'année précédente** si l'on n'y prend garde. **Règle** : quand on parle de semaines, on garde **l'année ISO avec la semaine ISO** (`isocalendar().year`), jamais l'année civile.

Les morceaux de date servent ensuite à regrouper. Voici le chiffre d'affaires par jour de la semaine : il suffit de relier les lignes à leur date, puis de regrouper.

```python
x = x.merge(cmd[["id_commande", "date_commande", "id_client", "canal", "jour_semaine"]], on="id_commande", validate="m:1")
ca_jour = x.groupby("jour_semaine")["montant"].sum().round(0)
print(ca_jour.to_string())
```
<!--sortie-->
```text
jour_semaine
1    508828.0
2    461784.0
3    487038.0
4    517374.0
5    611017.0
6    722969.0
7    344146.0
```
<!--sortie-->

```python hide
NUM("ca_samedi", ca_jour.loc[6] / 1000); NUM("ca_dimanche", ca_jour.loc[7] / 1000); NUM("ca_mardi", ca_jour.loc[2] / 1000)
NUM("rapport_sam_dim", ca_jour.loc[6] / ca_jour.loc[7])
```
<!--sortie-->
```text
NUM ca_samedi 722.969
NUM ca_dimanche 344.146
NUM ca_mardi 461.784
NUM rapport_sam_dim 2.100762467092455
```

Le samedi (jour 6) est le jour le plus fort (723 k€ sur trois ans) et le dimanche (jour 7) le plus faible (344 k€) : un rapport de 2,1 entre les deux. Ce motif de semaine, invisible dans la colonne de dates, apparaît dès que l'on a dérivé le jour.

On obtient les mêmes morceaux de date en **SQL**, ce qui est utile quand les données restent dans une base. Voici le comptage des commandes par jour de la semaine avec **DuckDB**, un moteur SQL qui lit directement les fichiers CSV et qui parle un dialecte très proche de PostgreSQL ; on vérifie ensuite qu'il donne le même résultat que pandas.

```python
import duckdb
q = "select date_part('isodow', date_commande) as jour, count(*) as n from 'donnees/commandes.csv' group by 1 order by 1"
n_sql = duckdb.sql(q).df().set_index("jour")["n"]
n_pd = cmd["jour_semaine"].value_counts().sort_index()
print("même résultat que pandas :", (n_sql.values == n_pd.values).all())
```
<!--sortie-->
```text
même résultat que pandas : True
```
<!--sortie-->

### 2.1.4 Les classes : découper une variable continue

Un montant de panier est une variable **continue** : il en existe des milliers de valeurs différentes. Pour un tableau de bord, une segmentation commerciale ou un tableau croisé, on le découpe en **classes** (volume I, section 5.1). Deux outils, deux philosophies :

- **`pd.cut`** découpe selon des **bornes que l'on choisit** (0, 50, 100, 200…) : les classes ont un sens **métier** (« petit panier », « gros panier »), mais des effectifs inégaux ;
- **`pd.qcut`** découpe selon des **quantiles** : chaque classe contient autant de lignes (dix déciles de 3 640 commandes environ), mais les bornes sont des nombres peu parlants.

```python
paniers = x.groupby("id_commande", as_index=False).agg(panier=("montant", "sum"), id_client=("id_client", "first"), date=("date_commande", "first"))
bornes = [0, 50, 100, 200, np.inf]
paniers["classe"] = pd.cut(paniers["panier"], bornes, right=False, labels=["< 50", "50 à 100", "100 à 200", "200 et +"])
paniers["decile"] = pd.qcut(paniers["panier"], 10, labels=False) + 1
print(paniers["classe"].value_counts().sort_index().to_string())
print(paniers.groupby("decile")["panier"].agg(["min", "max"]).round(0).head(3).to_string())
```
<!--sortie-->
```text
classe
< 50         10874
50 à 100     11261
100 à 200    10445
200 et +      3815
         min   max
decile            
1        2.0  22.0
2       22.0  36.0
3       36.0  50.0
```
<!--sortie-->

```python hide
NUM("taille_decile", len(paniers) / 10)
vc = paniers["classe"].value_counts().sort_index()
NUM("n_moins50", vc.iloc[0]); NUM("n_200plus", vc.iloc[3]); NUM("part_200plus", vc.iloc[3] / len(paniers) * 100)
NUM("borne_d1", paniers["panier"].quantile(0.1)); NUM("borne_d5", paniers["panier"].quantile(0.5))
```
<!--sortie-->
```text
NUM taille_decile 3639.5
NUM n_moins50 10874
NUM n_200plus 3815
NUM part_200plus 10.48220909465586
NUM borne_d1 21.53
NUM borne_d5 79.8
```

Le paramètre `right=False` mérite attention : il rend chaque classe **fermée à gauche et ouverte à droite** (`[50 ; 100[`). Sans lui, un panier de **exactement** 100 € irait dans la classe « 50 à 100 » ; avec lui, dans « 100 à 200 ». Les deux conventions sont défendables ; l'important est **d'en choisir une et de l'écrire**, sinon deux tableaux du même fichier ne tombent pas d'accord pour quelques lignes. Les classes obtenues donnent 10 874 paniers de moins de 50 € et 3 815 de 200 € et plus, soit 10 % des commandes. Quant aux déciles, le premier décile s'arrête à 22 € et le cinquième à 80 € : la médiane des paniers.

L'équivalent en SQL s'écrit avec `CASE`, qui évalue les conditions **dans l'ordre** et s'arrête à la première vraie. On vérifie que les deux méthodes classent les paniers de la même façon.

```python
con = duckdb.connect(); con.register("paniers", paniers)
q = "select case when panier < 50 then '< 50' when panier < 100 then '50 à 100' when panier < 200 then '100 à 200' else '200 et +' end as classe, count(*) as n from paniers group by 1"
n_case = con.sql(q).df().set_index("classe")["n"]
print("CASE = cut :", (n_case.reindex(vc.index.astype(str)).values == vc.values).all())
```
<!--sortie-->
```text
CASE = cut : True
```
<!--sortie-->

> 🧭 **En pratique : choisir les bornes.** Partez de l'usage : si les classes servent à une décision (« remise à partir de 200 € »), les bornes viennent du métier. Si elles servent à comparer des groupes de taille comparable, prenez des quantiles. Dans les deux cas, **gardez la variable continue d'origine** à côté de la classe : on peut toujours reclasser, on ne peut pas « déclasser ».

### 2.1.5 Indicateurs, rangs et variables retardées

Un **indicateur** (ou variable binaire) vaut vrai ou faux : « la commande a eu lieu un week-end », « le panier dépasse 200 € », « la ligne a bénéficié d'une remise ». C'est la variable dérivée la plus simple, et l'une des plus utiles, parce qu'une moyenne d'indicateur **est une proportion** : la moyenne de `week_end` est la part des commandes passées le week-end.

Les variables les plus délicates sont celles qui **regardent une autre ligne** : « le délai depuis la commande précédente du même client », « le rang de la commande dans la vie du client ». Elles demandent deux gestes : **trier** (le « précédent » n'a de sens que dans un ordre) et **regrouper** (le précédent d'une commande est une commande **du même client**). En pandas, `groupby` puis `shift` décale chaque groupe d'une ligne ; `cumcount` numérote les lignes d'un groupe.

```python
paniers = paniers.sort_values(["id_client", "date", "id_commande"]).reset_index(drop=True)
g = paniers.groupby("id_client")
paniers["rang_commande"] = g.cumcount() + 1
paniers["delai_jours"] = (paniers["date"] - g["date"].shift()).dt.days
paniers["dormant_180"] = paniers["delai_jours"] > 180
un = paniers[paniers["id_client"] == 2]
print(un[["id_commande", "date", "panier", "rang_commande", "delai_jours", "dormant_180"]].to_string(index=False))
```
<!--sortie-->
```text
 id_commande       date  panier  rang_commande  delai_jours  dormant_180
         434 2023-01-18    7.90              1          NaN        False
        2517 2023-04-11   18.90              2         83.0        False
        7304 2023-09-27  310.20              3        169.0        False
       17755 2024-08-05  135.70              4        313.0         True
       19508 2024-10-05  159.40              5         61.0        False
       29212 2025-07-05   24.62              6        273.0         True
       30003 2025-08-01   75.82              7         27.0        False
       35090 2025-12-09   21.43              8        130.0        False
       35460 2025-12-16   89.31              9          7.0        False
```
<!--sortie-->

```python hide
NUM("n_clients_cmd", paniers["id_client"].nunique()); NUM("n_delai_nan", paniers["delai_jours"].isna().sum())
NUM("delai_median", paniers["delai_jours"].median()); NUM("part_dormant", paniers["dormant_180"].mean() * 100)
NUM("part_dormant_hors_premiere", (paniers["delai_jours"] > 180).sum() / paniers["delai_jours"].notna().sum() * 100)
NUM("d2_a", un.iloc[1]["delai_jours"]); NUM("d2_b", un.iloc[2]["delai_jours"]); NUM("d2_c", un.iloc[3]["delai_jours"])
```
<!--sortie-->
```text
NUM n_clients_cmd 4806
NUM n_delai_nan 4806
NUM delai_median 47.0
NUM part_dormant 11.427393872784723
NUM part_dormant_hors_premiere 13.165975497799867
NUM d2_a 83.0
NUM d2_b 169.0
NUM d2_c 313.0
```

La première commande du client n°2 a un délai **vide** (`NaN`), et c'est exact : elle n'a pas de précédente. Une erreur fréquente consisterait à remplacer ce vide par zéro, ce qui dirait « ce client a recommandé le jour même ». Sur nos 4 806 clients, 4 806 commandes n'ont pas de précédente (une par client), et le délai **médian** entre deux commandes consécutives d'un même client est de 47 jours. L'indicateur `dormant_180` marque les commandes passées plus de six mois après la précédente : 13,2 % des commandes qui **ont** une précédente. Notez que `NaN > 180` vaut `False` : l'indicateur, calculé sur toutes les lignes, dilue cette proportion à 11,4 %. **Le choix du dénominateur est une décision** : on documente « sur les commandes qui ont une précédente ».

Le décalage fait aussi apparaître la forme du comportement d'achat. Un client qui revient 83 jours, puis 169 jours, puis 313 jours après sa commande précédente s'éloigne ; la variable `delai_jours`, que la colonne `date` ne contenait pas, le rend **visible** et **mesurable**.

> 🧪 **Expérience : le même délai en SQL.** En SQL, la fonction fenêtre `LAG(date) OVER (PARTITION BY id_client ORDER BY date)` joue le rôle de `groupby` + `shift` (volume I, section 3.3.4). Retenez l'équivalence : `partition by` ↔ `groupby`, `order by` ↔ `sort_values`, `lag` ↔ `shift`.

### 2.1.6 Du texte à la clé

Pour relier deux sources, il faut une **clé** qui s'écrive de la même façon des deux côtés. Or le texte est la matière la moins fiable : la caisse écrit « BOÎTE RUSTIQUE », le catalogue « Boîte rustique », le CRM « boite rustique ». Trois écritures, un seul objet. La première transformation, avant toute jointure sur du texte, est de **normaliser** : tout passer en minuscules, retirer les accents, remplacer la ponctuation par des espaces, compresser les espaces multiples.

```python
import unicodedata, re
def cle_texte(s):
    s = "".join(c for c in unicodedata.normalize("NFD", str(s)) if unicodedata.category(c) != "Mn")
    return re.sub(r"\s+", " ", re.sub(r"[^a-z0-9 ]", " ", s.lower())).strip()
exemples = ["BOÎTE RUSTIQUE", "Boîte rustique", " boite  rustique ", "Boîte-rustique."]
print([cle_texte(e) for e in exemples])
```
<!--sortie-->
```text
['boite rustique', 'boite rustique', 'boite rustique', 'boite rustique']
```
<!--sortie-->

```python hide
NUM("n_cles_distinctes", len({cle_texte(e) for e in exemples}))
NUM("n_noms_bruts", prod["nom_produit"].nunique()); NUM("n_produits", len(prod))
NUM("n_noms_cles", prod["nom_produit"].map(cle_texte).nunique())
```
<!--sortie-->
```text
NUM n_cles_distinctes 1
NUM n_noms_bruts 60
NUM n_produits 120
NUM n_noms_cles 60
```

La décomposition en Unicode « NFD » sépare chaque lettre accentuée en une lettre et un **accent combinant** ; on supprime ensuite les accents. Les quatre écritures donnent 1 seule clé. Mais attention : **normaliser n'est pas dédoublonner**. Dans notre catalogue de 120 produits, il n'y a que 60 noms distincts, et la normalisation n'en retire aucun (60 clés) : **chaque nom est porté par deux produits** différents. Une clé de texte rend deux écritures comparables ; elle ne dit pas si deux objets distincts portent le même nom. Cette ambiguïté est l'un des fils de la section suivante.

### 2.1.7 Trois pièges, et comment documenter

**Piège 1 : la division par zéro.** Un ratio dont le dénominateur peut valoir zéro doit prévoir ce cas. En pandas, `x / 0` donne `inf` (l'infini) et `0 / 0` donne `NaN`, sans erreur : un `inf` dans une moyenne la rend infinie, et personne n'est prévenu. Calculons le panier moyen par client sur 2025. Les clients qui n'ont pas commandé cette année-là n'ont ni chiffre d'affaires ni commande : leur panier moyen n'est **pas défini**.

```python
x25 = x[x["date_commande"].dt.year == 2025]
cl = pd.read_csv("donnees/clients.csv")[["id_client"]]
cl = cl.merge(x25.groupby("id_client").agg(ca=("montant", "sum"), nb=("id_commande", "nunique")), on="id_client", how="left")
cl["panier_moyen"] = cl["ca"] / cl["nb"]
print("clients sans commande en 2025 :", int(cl["nb"].isna().sum()), "| paniers moyens indéfinis :", int(cl["panier_moyen"].isna().sum()))
print("moyenne des paniers moyens (acheteurs) :", round(cl["panier_moyen"].mean(), 2), "| avec des zéros :", round(cl["panier_moyen"].fillna(0).mean(), 2))
```
<!--sortie-->
```text
clients sans commande en 2025 : 2125 | paniers moyens indéfinis : 2125
moyenne des paniers moyens (acheteurs) : 101.14 | avec des zéros : 65.32
```
<!--sortie-->

```python hide
NUM("n_sans_cmd", cl["nb"].isna().sum()); NUM("pm_acheteurs", cl["panier_moyen"].mean()); NUM("pm_zeros", cl["panier_moyen"].fillna(0).mean())
NUM("n_clients_total", len(cl))
```
<!--sortie-->
```text
NUM n_sans_cmd 2125
NUM pm_acheteurs 101.14262156631318
NUM pm_zeros 65.32127642824393
NUM n_clients_total 6000
```

Sur 6 000 clients, 2 125 n'ont rien acheté en 2025. Les laisser en `NaN` donne un panier moyen de **101,14 €** (celui des acheteurs) ; les remplacer par zéro l'écrase à 65,32 €. Aucun des deux calculs n'est « faux » : ils répondent à deux questions différentes. Ce qui serait faux serait de **ne pas savoir lequel on a fait**.

**Piège 2 : la valeur manquante qui se propage.** Une opération arithmétique avec un `NaN` donne un `NaN`. Si l'on calcule le chiffre d'affaires total d'un client en **additionnant** ses chiffres par canal, tous ceux qui n'ont pas acheté dans l'un des trois canaux ont un total vide.

```python
par_canal = x25.pivot_table(index="id_client", columns="canal", values="montant", aggfunc="sum")
mauvais = par_canal["Boutique"] + par_canal["Site"] + par_canal["Réseaux"]
bon = par_canal.sum(axis=1)
print("totaux vides avec + :", int(mauvais.isna().sum()), "sur", len(par_canal), "| avec sum(axis=1) :", int(bon.isna().sum()))
```
<!--sortie-->
```text
totaux vides avec + : 3224 sur 3875 | avec sum(axis=1) : 0
```
<!--sortie-->

```python hide
NUM("tot_vides_plus", mauvais.isna().sum()); NUM("n_acheteurs", len(par_canal)); NUM("part_vides_plus", mauvais.isna().mean() * 100)
```
<!--sortie-->
```text
NUM tot_vides_plus 3224
NUM n_acheteurs 3875
NUM part_vides_plus 83.2
```

Avec l'opérateur `+`, 3 224 totaux sur 3 875 (soit 83 %) sont perdus, alors qu'`axis=1` avec `sum` **ignore** les vides. Retenez la règle : **`sum` ignore les manquants, `+` les propage**. L'une n'est pas meilleure que l'autre, mais il faut choisir en connaissance de cause.

**Piège 3 : la fuite d'information.** Une variable dérivée **fuit** quand elle utilise une information qui n'était pas connue à la date où l'on veut s'en servir. Imaginons que la gérante veuille repérer, au 30 juin 2025, les clients qui commanderont encore au second semestre. Parmi les clients qui avaient déjà commandé, nous calculons deux versions de « nombre de commandes » : l'une **avant** le 30 juin, l'autre **au total**, futur compris.

```python
coupure = pd.Timestamp("2025-06-30")
avant = paniers[paniers["date"] <= coupure].groupby("id_client").size().rename("avant")
total = paniers.groupby("id_client").size().rename("total")
cible = paniers[(paniers["date"] > coupure) & (paniers["date"].dt.year == 2025)].groupby("id_client").size().rename("s2")
t = pd.concat([avant, total, cible], axis=1).dropna(subset=["avant"]).fillna(0)
from sklearn.metrics import roc_auc_score
y = (t["s2"] > 0).astype(int)
print("AUC avec 'avant' :", round(roc_auc_score(y, t["avant"]), 3), "| avec 'total' :", round(roc_auc_score(y, t["total"]), 3))
```
<!--sortie-->
```text
AUC avec 'avant' : 0.776 | avec 'total' : 0.875
```
<!--sortie-->

```python hide
NUM("auc_avant", roc_auc_score(y, t["avant"])); NUM("auc_total", roc_auc_score(y, t["total"])); NUM("n_t", len(t)); NUM("part_y", y.mean() * 100)
```
<!--sortie-->
```text
NUM auc_avant 0.775681131723176
NUM auc_total 0.8745505068810614
NUM n_t 4409
NUM part_y 62.576547970061235
```

Sur 4 409 clients ayant déjà commandé au 30 juin, 63 % commandent au second semestre. La variable honnête (`avant`) a un pouvoir de classement modeste (une AUC de 0,78 : 0,5 correspondrait au hasard, 1 à un classement parfait), alors que la version qui regarde le futur (`total`, qui **contient** les commandes du second semestre) paraît bien meilleure : 0,87. Cette différence n'a aucune valeur : c'est la **cible** qui se glisse dans la prédiction. Règle : **toute variable qui sert à prévoir doit être calculée avec les seules données antérieures à la date de prévision**. Quand on dérive une variable, on se demande donc : « *à quelle date aurais-je pu la calculer ?* ». (Le volume III revient en détail sur la fuite d'information et l'évaluation des modèles.)

**Documenter chaque variable créée.** Une variable dérivée sans définition est une dette. Une **fiche** de quelques lignes suffit ; le chapitre 4 de ce volume en fait un dictionnaire de données complet.

| Champ | Exemple pour `marge_ht` |
|---|---|
| Nom | `marge_ht` |
| Définition | chiffre d'affaires hors taxe de la ligne moins quantité × coût d'achat |
| Unité | euros |
| Formule | `montant / 1,20 − quantite × cout_achat` |
| Hypothèses | TVA de 20 % (fictive) ; coût d'achat actuel du catalogue, sans frais de transport |
| Cas particuliers | un produit sans coût d'achat donne une marge vide (jamais zéro) |
| Auteur, date | l'analyste, date de création |

> ✅ **À retenir.**
> - Une variable dérivée est une **décision de définition** : unité, base de calcul, cas limites. On l'**écrit**.
> - Un **ratio d'agrégat** se calcule à partir des **sommes**, jamais en faisant la moyenne de ratios.
> - Pour les dates : on extrait année, trimestre, mois, jour ; on garde **l'année ISO avec la semaine ISO**.
> - Les classes se choisissent (`cut`, bornes du métier) ou se calculent (`qcut`, quantiles) ; on **écrit la convention des bornes** et l'on garde la variable d'origine.
> - Un délai ou un rang demande de **trier** puis de **regrouper** ; le vide d'un premier délai n'est **pas** un zéro.
> - Trois pièges : la division par zéro, le `NaN` qui se propage (`sum` ≠ `+`), la **fuite d'information**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 et 2.2, exercices 2.1 à 2.4.
