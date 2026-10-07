# Chapitre 2 : Transformation et fusion des données

> « Une analyse commence le jour où toutes les données tiennent dans une seule table, et où l'on sait ce que chaque ligne représente. »


Un matin, la gérante de la boutique vous apporte une demande qui a l'air simple : « **Je voudrais une seule table de toutes les ventes de l'année, la caisse et le site ensemble, avec le nom du produit et la marge sur chaque ligne.** Ensuite, je pourrai répondre moi-même à mes questions avec un tableau croisé. » Elle ajoute, un peu gênée, que la caisse lui envoie un fichier par mois, que le site web fournit « un export », et qu'elle ne sait plus très bien quand le format a changé.

Vous ouvrez les fichiers. Les douze exports de la caisse n'ont pas tous les mêmes colonnes ni le même codage ; l'export du site exprime ses montants en texte, avec un symbole monétaire, et, à partir de la mi-septembre, **en centimes** ; aucun des deux ne contient le coût d'achat des produits, qui est dans une autre table, ni de numéro de produit utilisable pour la caisse. Tout est là pour répondre à la gérante, mais **rien n'est prêt** : avant l'analyse, il faut **transformer** (créer des variables), **fusionner** (relier des tables), **empiler** (mettre des fichiers bout à bout) et **agréger** (changer le niveau de détail).

Ce chapitre vous apprend ces quatre gestes, et surtout **comment s'assurer qu'on ne s'est pas trompé**. Car chacun de ces gestes peut faire perdre des lignes, en inventer, ou fausser un total **sans qu'aucune erreur ne s'affiche**. Une jointure qui double les lignes donne un chiffre d'affaires deux fois trop grand ; un fichier lu avec la mauvaise décimale divise les montants par cent ; une agrégation faite au mauvais niveau compte deux fois la même commande. La méthode qui traverse tout le chapitre tient en une phrase : **à chaque étape, comparer les effectifs et les totaux avant et après, et expliquer chaque écart**.

> 💡 **Intuition.** Préparer des données, c'est comme **monter un meuble** à partir de plusieurs cartons : chaque pièce est correcte, mais l'ensemble n'est utilisable qu'une fois les pièces assemblées dans le bon ordre. Et, comme pour un meuble, il vaut mieux **vérifier à chaque vissage** que la pièce est bien droite plutôt que de s'en apercevoir à la fin, quand l'étagère penche.

## Quatre gestes, un vocabulaire

Pour que la suite soit lisible, fixons le vocabulaire. Les quatre gestes se distinguent par ce qu'ils font du **nombre de lignes** et du **nombre de colonnes**.

| Geste | Ce qu'il fait | Lignes | Colonnes | Exemple de la boutique |
|---|---|---|---|---|
| **Dériver** | calculer de nouvelles variables à partir des colonnes existantes | inchangées | augmentent | la marge d'une ligne de vente, le trimestre d'une date |
| **Joindre** | relier deux tables par une clé commune | ne devraient pas changer (en cas de 1–n) | augmentent | ajouter le coût d'achat à chaque ligne de vente |
| **Empiler** | mettre bout à bout des tables de même structure | s'additionnent | inchangées | les douze fichiers mensuels de la caisse |
| **Agréger** | résumer par groupes, en changeant le niveau de détail | diminuent | changent | le chiffre d'affaires par mois et par canal |

Un cinquième geste, le **pivot** (passer d'un tableau « large » à un tableau « long » et inversement), est traité dans une section facultative, ainsi que le **rapprochement approximatif** (relier deux enregistrements qui désignent la même chose sans être écrits de la même façon).

## Le chemin de ce chapitre

Le parcours essentiel suit les trois premiers gestes, dans l'ordre où la gérante en a besoin.

- **2.1 Création et dérivation de variables** : calculer une marge, extraire des morceaux de date, fabriquer des classes et des indicateurs, mesurer un délai entre deux commandes, normaliser du texte pour en faire une clé ; et repérer les pièges (division par zéro, valeurs manquantes qui se propagent, fuite d'information).
- **2.2 Fusion et jointure de jeux de données** : comprendre les types de jointure et la **cardinalité**, contrôler les effectifs avant et après, empiler les douze fichiers de la caisse, lire l'export du site, **harmoniser** les deux sources en une table de ventes unique, et chercher ce qui manque.
- **2.3 Agrégation et restructuration** : changer de niveau de détail (ligne, commande, client), distinguer table de faits et dimensions, calculer des parts, des cumuls et des fenêtres, et vérifier par une **somme de contrôle** que rien n'a été perdu.

Deux sections facultatives prolongent ce parcours : **➕ 2.4 Restructuration : pivot et dépivot** (le tableur de stocks de la boutique, saisi à la main) et **➕ 2.5 Appariement approximatif et rapprochement d'enregistrements** (dédoublonner le fichier clients, rapprocher le catalogue du fournisseur).

## Les données du chapitre

Les fichiers de ce chapitre sont **simulés** : ils ont été fabriqués à partir de la base propre du volume I, puis abîmés de façon contrôlée. Des fichiers de **vérité** (`verite_*.csv`) disent ce qui a été injecté : nous ne les ouvrirons qu'en fin d'étude, pour **juger** notre travail, comme on corrige un exercice. Dans la vie réelle, on ne dispose jamais de cette vérité : c'est précisément pourquoi les contrôles de ce chapitre sont indispensables.

| Fichier | Contenu | Particularités |
|---|---|---|
| `caisse/caisse_2025-01.csv` … `caisse_2025-12.csv` | ventes du canal **Boutique** en 2025, un fichier par mois | le format change trois fois dans l'année (codage, séparateur, décimale, noms de colonnes, format des dates) ; lignes de titre, en-têtes répétés, ligne de total, montants vides, lignes doublées |
| `site_commandes.csv`, `site_lignes.csv` | commandes du canal **Site** en 2025 (en-têtes puis lignes) | montants en texte, statuts écrits de plusieurs façons, doublons d'export, commandes de test, commandes annulées, changement de format et d'unité à la mi-septembre |
| `catalogue_fournisseur.csv` | catalogue d'un fournisseur : code, désignation, prix d'achat | désignations réécrites ; certains produits manquent ; d'autres n'existent pas à la boutique |
| `crm_clients.csv` | le fichier clients du CRM | plusieurs lignes pour un même client, noms et e-mails mal écrits |
| `stocks_tableur.xlsx` | stock mensuel saisi à la main dans un tableur | cellules fusionnées, sous-totaux, valeurs textuelles |
| `clients.csv`, `produits.csv`, `commandes.csv`, `lignes_commande.csv` | la base propre du volume I | servent de référence (produits, coût d'achat) et de contrôle |


Pour fixer les idées : les douze fichiers de la caisse contiennent 12 678 lignes de vente (une fois retirés les titres et les en-têtes répétés), l'export du site compte 6 259 lignes d'en-têtes de commande et 13 928 lignes de détail, et la base propre du volume I contient 36 395 commandes et 83 905 lignes de commande sur trois ans. Retenez ces ordres de grandeur : vous les retrouverez en fil de chapitre, sous forme de **contrôles**.

> 📦 **Ce que ce chapitre suppose.** Vous savez lire un fichier CSV avec pandas, filtrer, regrouper et faire une jointure simple (volume I, chapitres 3 et 4). Nous reprendrons ces notions en les mettant à l'épreuve de données réelles dans leur désordre. Les tables sont reliées par des clés (`id_commande`, `id_produit`, `id_client`) : le schéma de la base est rappelé dans le volume I, section 3.1.1.


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


Deux colonnes se ressemblent mais ne disent pas la même chose. Le **taux de marge** d'un groupe est le rapport des **sommes** (la marge totale divisée par le chiffre d'affaires hors taxe total) ; la **moyenne des taux** des lignes donne à une ligne de 5 € le même poids qu'une ligne de 150 €. Pour la décoration, la première vaut 38,7 % et la seconde 37,4 %. **Un ratio d'agrégat se calcule toujours à partir des sommes**, jamais en faisant la moyenne de ratios ; c'est la même règle que pour le panier moyen du volume I. Sur l'ensemble des ventes, le taux de marge brute est de 36,9 %, avec des écarts d'une catégorie à l'autre : de 34,0 % pour le bien-être à 38,7 % pour la décoration.

> ⚠️ **Piège : la remise grignote la marge.** Une remise de 20 % ne coûte pas 20 % **de marge**, mais 20 % **du prix**, c'est-à-dire une part bien plus grande de la marge. Sur nos données, le taux de marge tombe de 38,2 % pour les lignes sans remise à 22,7 % pour celles qui bénéficient de 20 % de remise. Une variable `marge` calculée **avant** remise aurait caché cette érosion.


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


## 2.2 Fusion et jointure de jeux de données

La demande de la gérante tient en une table, et les données arrivent en pièces détachées : douze fichiers de caisse, un export du site, une table de produits. Cette section apprend à **recoller** ces pièces sans en perdre ni en inventer : comprendre les types de jointure et la **cardinalité**, **contrôler** les effectifs avant et après chaque opération, **empiler** les fichiers de la caisse malgré leurs formats changeants, **lire** l'export du site et **harmoniser** les deux sources en une table de ventes unique, puis **chercher ce qui manque**. À la fin, on retrouve le même résultat avec trois outils (pandas, SQL, R), et l'on ouvre enfin le fichier de vérité pour juger le travail.

### 2.2.1 Quatre manières de recoller

Il existe deux familles d'opérations, qui ne répondent pas à la même question :

- **Joindre** (*merge*, *join*) relie deux tables **côte à côte** : chaque ligne de la première reçoit, de la seconde, les colonnes qui lui correspondent, selon une **clé**. On ajoute des **colonnes**.
- **Empiler** (*concat*, *union*) met deux tables **l'une sous l'autre** : elles doivent avoir la même structure. On ajoute des **lignes**.

Pour une jointure, la question qui change tout est : **que faire des lignes sans correspondance ?** Quatre réponses, que l'on retrouve sous le même nom en SQL, en R et dans Power Query.

| Type (`how=`) | Garde… | Lignes sans correspondance |
|---|---|---|
| `inner` | seulement les lignes présentes **des deux côtés** | perdues |
| `left` | **toutes** les lignes de la table de gauche | à droite : colonnes vides (`NaN`) |
| `right` | toutes celles de la table de droite | à gauche : colonnes vides |
| `outer` | **toutes** les lignes des deux tables | colonnes vides de l'un ou l'autre côté |

Sur trois lignes de produits et trois lignes de stocks, l'option `indicator=True` ajoute une colonne qui dit **d'où vient chaque ligne** : c'est le meilleur outil de diagnostic d'une jointure.

```python
a = pd.DataFrame({"id_produit": [1, 2, 3], "nom": ["Bol", "Vase", "Plaid"]})
b = pd.DataFrame({"id_produit": [2, 3, 4], "stock": [10, 0, 7]})
print(a.merge(b, on="id_produit", how="outer", indicator=True).to_string(index=False))
```
<!--sortie-->
```text
 id_produit   nom  stock     _merge
          1   Bol    NaN  left_only
          2  Vase   10.0       both
          3 Plaid    0.0       both
          4   NaN    7.0 right_only
```
<!--sortie-->

Le produit 1 n'a pas de stock (`left_only`), le produit 4 n'a pas de nom (`right_only`), les produits 2 et 3 sont présents des deux côtés (`both`). Une jointure `inner` n'aurait gardé que ces deux derniers ; une jointure `left`, les produits 1, 2 et 3. **Le choix du type de jointure est un choix d'analyse** : si l'on veut le chiffre d'affaires de **tous** les produits du catalogue, y compris ceux qui n'ont rien vendu, il faut un `left` depuis le catalogue ; un `inner` ferait **disparaître** ces produits sans le moindre message.

> ⚠️ **Piège : la jointure `inner` qui fait disparaître des lignes.** Par défaut, `merge` fait une jointure `inner`. Si la clé est mal écrite d'un côté (une majuscule, un espace), les lignes concernées **disparaissent** sans erreur. On vérifie donc toujours le nombre de lignes avant et après.

### 2.2.2 La cardinalité et le contrôle des effectifs

La **cardinalité** d'une jointure dit combien de lignes de droite correspondent à une ligne de gauche.

- **1–1** : chaque clé apparaît au plus une fois des deux côtés (un client, sa fiche d'identité).
- **1–n** (ou **n–1** vu de l'autre côté) : une clé de la table « un » correspond à plusieurs lignes de l'autre (un produit, ses lignes de vente). C'est le cas le plus courant, et le plus sain : on **ajoute des colonnes** sans changer le nombre de lignes de la table « n ».
- **n–n** : la clé est répétée **des deux côtés**. Chaque ligne de gauche est associée à **toutes** les lignes de droite de même clé : le nombre de lignes **se multiplie**. C'est presque toujours un accident.

On teste la cardinalité avec le paramètre `validate` (`"1:1"`, `"1:m"`, `"m:1"`, `"m:m"`) : pandas lève une erreur si la réalité ne correspond pas à ce que l'on a **déclaré**. C'est la façon la plus simple de transformer une hypothèse tacite en vérification. Et quatre contrôles, à faire après **chaque** jointure, résument la méthode du chapitre :

1. le **nombre de lignes** avant et après (un 1–n ne doit rien changer) ;
2. la **somme** d'une colonne de la table « n » avant et après ;
3. le **nombre de lignes sans correspondance** (`indicator`) ;
4. l'**unicité** de la clé du côté « un ».

```python
def controler(gauche, droite, cle, how="left"):
    r = gauche.merge(droite, on=cle, how=how, indicator=True)
    return {"lignes avant": len(gauche), "lignes après": len(r),
            "clé dupliquée à droite": int(droite.duplicated(cle).sum()),
            "sans correspondance": int((r["_merge"] == "left_only").sum())}
print(controler(lig, prod[["id_produit", "cout_achat"]], "id_produit"))
```
<!--sortie-->
```text
{'lignes avant': 83905, 'lignes après': 83905, 'clé dupliquée à droite': 0, 'sans correspondance': 0}
```
<!--sortie-->


Pour la jointure des lignes de vente avec les produits, les quatre contrôles passent : 83 905 lignes avant et 83 905 après, aucune clé dupliquée du côté des produits (0), aucune ligne sans correspondance (0). **On peut avancer.** Gardez cette petite fonction : vous allez voir, dans la suite, des jointures qui ne passent pas.

### 2.2.3 Empiler les douze fichiers de la caisse

La caisse de la boutique envoie **un fichier par mois**. Pour répondre à la gérante, il faut les mettre bout à bout, et c'est là que les ennuis commencent : **le format a changé en cours d'année**. Ce phénomène porte un nom, la **dérive de schéma** : la source a évolué (mise à jour du logiciel, changement de paramètres régionaux) et n'a prévenu personne.

| Mois | Codage du fichier | Séparateur | Décimale | Nom de la colonne des quantités | Date | Autres différences |
|---|---|---|---|---|---|---|
| janvier à juin | `cp1252` (ancien Windows) | `;` | `,` | « Qté » | `jj/mm/aaaa` | |
| juillet à septembre | UTF-8 avec « BOM » | `;` | `,` | « Quantité » | `jj/mm/aa` (année sur 2 chiffres) | |
| octobre à décembre | UTF-8 avec « BOM » | `,` | `.` | « Qté » | `jj/mm/aaaa` | colonne « Remise (%) » en plus, champs entre guillemets |

Chaque fichier commence par **trois lignes de titre** (dont une vide), répète son **en-tête** toutes les soixante lignes environ (comme à chaque « page » imprimée), et se termine par une **ligne de total**. Aucune de ces particularités n'est une erreur ; ce sont des **conventions d'édition** qu'un programme doit connaître. L'approche la plus robuste est de ne **rien deviner à la main** : on **détecte** le format de chaque fichier, puis on applique les mêmes étapes. D'abord, ouvrir le fichier en octets et choisir le codage : on essaie UTF-8, et l'on retombe sur `cp1252` si le décodage échoue.

```python
import io, glob, os
def lire_brut(chemin):
    brut = open(chemin, "rb").read()
    try:
        texte = brut.decode("utf-8-sig")        # « sig » : retire le BOM, marque d'ordre des octets
    except UnicodeDecodeError:
        texte = brut.decode("cp1252")
    lignes = texte.splitlines()
    sep = ";" if lignes[3].count(";") > lignes[3].count(",") else ","
    return lignes, sep
```

Le séparateur se devine sur la ligne d'en-tête (la quatrième) : il y en a plus de points-virgules que de virgules dans un fichier à points-virgules, et réciproquement (les décimales à virgule n'apparaissent pas dans l'en-tête). Ensuite, lire le corps en **texte** (jamais de conversion automatique : on convertit explicitement), retirer le total et les en-têtes répétés, et harmoniser le nom des colonnes.

```python
RENOM = {"N° ticket": "ticket", "Ticket": "ticket", "Qté": "quantite", "Quantité": "quantite", "Date": "date", "Heure": "heure",
         "Article": "article", "Catégorie": "categorie", "Prix unitaire": "prix_unitaire", "Remise (%)": "remise_pct", "Montant": "montant"}
def ouvrir_caisse(chemin):
    lignes, sep = lire_brut(chemin)
    dec = "," if sep == ";" else "."
    total = float(lignes[-1].split(sep)[-1].replace(dec, "."))
    df = pd.read_csv(io.StringIO("\n".join(lignes[3:-1])), sep=sep, dtype=str, keep_default_na=False).rename(columns=RENOM)
    return df[~df["ticket"].isin(["N° ticket", "Ticket"])].copy(), total, dec
```

Reste à **typer** : nombres (en remplaçant la décimale locale par le point), quantité entière, date (le format dépend de la longueur du texte : dix caractères pour l'année sur quatre chiffres, huit pour l'année sur deux).

```python
def typer_caisse(df, dec, nom):
    for c in ["prix_unitaire", "montant", "remise_pct"]:
        df[c] = pd.to_numeric(df[c].str.replace(dec, "."), errors="coerce") if c in df else np.nan
    df["quantite"] = df["quantite"].astype(int)
    df["date"] = pd.to_datetime(df["date"], format="%d/%m/%Y" if len(df["date"].iloc[0]) == 10 else "%d/%m/%y")
    df["fichier"] = nom
    df["id_commande"] = df["ticket"].str.lstrip("T").astype(int)
    return df
```

On applique alors la même fonction aux douze fichiers, on empile avec `pd.concat`, et l'on construit **en même temps** un tableau de contrôle : pour chaque fichier, le **total affiché en pied** et la **somme des montants lus**. C'est la ligne de total du fichier qui sert de **somme de contrôle**.

```python
morceaux, ctrl = [], []
for f in sorted(glob.glob("donnees/caisse/caisse_2025-*.csv")):
    df, total, dec = ouvrir_caisse(f)
    df = typer_caisse(df, dec, os.path.basename(f))
    morceaux.append(df)
    ctrl.append((os.path.basename(f), len(df), total, round(df["montant"].sum(), 2), int(df["montant"].isna().sum())))
caisse = pd.concat(morceaux, ignore_index=True)
ctrl = pd.DataFrame(ctrl, columns=["fichier", "lignes", "total_affiche", "somme_lue", "montants_vides"])
ctrl["ecart"] = (ctrl["total_affiche"] - ctrl["somme_lue"]).round(2)
print(len(caisse), "lignes |", caisse["fichier"].nunique(), "fichiers")
print(ctrl.iloc[[0, 3, 6, 9, 11]].to_string(index=False))
```
<!--sortie-->
```text
12678 lignes | 12 fichiers
           fichier  lignes  total_affiche  somme_lue  montants_vides   ecart
caisse_2025-01.csv     955       38882.41   37826.31              36 1056.10
caisse_2025-04.csv    1013       45832.57   45426.14              31  406.43
caisse_2025-07.csv     877       41595.82   41035.68              21  560.14
caisse_2025-10.csv    1138       51321.48   49839.95              38 1481.53
caisse_2025-12.csv    1694       73384.87   70924.34              63 2460.53
```
<!--sortie-->


Les douze fichiers, empilés, donnent 12 678 lignes de vente. Mais le tableau de contrôle est **net** : pour chaque fichier, la somme des montants lus est **inférieure** au total affiché par la caisse, d'un écart qui va de 406 € à 2 461 € selon les mois. Sur l'année, la caisse annonce 560 973,91 €, et notre table n'en contient que 547 896,42 €, soit **13 077,49 € de moins**. Une jointure ou une lecture qui « marche » sans erreur peut ainsi perdre de l'argent, et c'est la **ligne de total du fichier**, que l'on aurait pu jeter avec les titres, qui l'a révélé.

D'où vient l'écart ? La colonne `montants_vides` donne la piste : **399 lignes (3,1 %) n'ont pas de montant** (cellule vide dans l'export). Une ligne de caisse contient pourtant de quoi **reconstituer** son montant : quantité × prix unitaire, moins la remise. La remise n'est écrite que dans les fichiers d'octobre à décembre ; avant, on ne la connaît pas, et l'on suppose zéro (c'est une **hypothèse** à documenter, que nous testerons plus loin). Les montants reconstitués sont **marqués**, jamais mélangés en silence avec les montants lus.

```python
caisse["montant_vide"] = caisse["montant"].isna()
remise = caisse["remise_pct"].fillna(0)
caisse["montant_corrige"] = caisse["montant"].fillna((caisse["quantite"] * caisse["prix_unitaire"] * (1 - remise / 100)).round(2))
caisse["identique_precedente"] = caisse.duplicated(["ticket", "date", "heure", "article", "categorie", "quantite", "prix_unitaire", "montant"])
par_fichier = caisse.groupby("fichier")["montant_corrige"].sum().round(2).values
print("écart restant sur l'année :", round(par_fichier.sum() - ctrl["total_affiche"].sum(), 2), "€")
print("lignes strictement identiques à une ligne précédente :", int(caisse["identique_precedente"].sum()))
```
<!--sortie-->
```text
écart restant sur l'année : 3498.68 €
lignes strictement identiques à une ligne précédente : 154
```
<!--sortie-->


Après reconstitution, l'écart ne disparaît pas : il **change de signe**. Au lieu de 13 077 € **manquants**, il y a maintenant 3 499 € **en trop** (0,62 % du total). La cause est la seconde anomalie du fichier : des lignes **strictement identiques** à une ligne précédente, au nombre de 154, pour 7 009 € : probablement des **doubles scans** à la caisse.

Faut-il les supprimer ? Le total de contrôle dit **combien** d'euros sont en trop, pas **lesquelles** des lignes le sont, car deux lignes identiques peuvent aussi être **légitimes** : un client qui achète deux fois le même article, enregistré en deux passages. Voici l'arithmétique des deux décisions possibles.

| Décision | Écart au total de la caisse |
|---|---|
| garder toutes les lignes (et les signaler) | +3 499 € (+0,62 %) |
| supprimer toutes les lignes identiques | -3 511 € (-0,63 %) |

Les deux erreurs sont du même ordre de grandeur et de signe opposé : aucune décision n'est exacte, et la bonne réponse est de **ne rien supprimer sans preuve** : on **garde** les lignes, on les **marque** (`identique_precedente`), et l'on **écrit** l'incertitude résiduelle (de l'ordre de 0,6 % du chiffre d'affaires de la caisse). En fin de section, nous ouvrirons le fichier de vérité pour savoir ce qu'il en était vraiment.


![Écart mensuel entre le total affiché en pied de chaque fichier de la caisse et la somme des montants lus : avant correction, les montants vides font « manquer » de l'argent (barres orange, positives) ; après reconstitution, les lignes doublées en font apparaître en trop (barres bleues, négatives).](figures/ch02-ecarts-caisse.png)

### 2.2.4 Lire l'export du site

L'export du site est d'une autre nature : un seul fichier d'en-têtes de commande (`site_commandes.csv`), un fichier de lignes (`site_lignes.csv`), liés par la référence `order_ref`. Tout est écrit **en texte**, et la méthode est la même : ne rien convertir automatiquement, **regarder** d'abord.

```python
site = pd.read_csv("donnees/site_commandes.csv", dtype=str, keep_default_na=False)
lignes_site = pd.read_csv("donnees/site_lignes.csv")
print(site[["order_ref", "created_at", "status", "total", "currency"]].head(4).to_string(index=False))
print(site["status"].value_counts().to_dict())
print(site["currency"].value_counts().to_dict())
```
<!--sortie-->
```text
 order_ref          created_at status    total currency
WEB-023473 2025-01-01 09:27:00   PAID  34,92 €      EUR
WEB-023450 2025-01-01 11:44:00   paid  63,66 €      eur
WEB-023464 2025-01-01 13:14:00   paid 195,40 €      EUR
WEB-023465 2025-01-01 14:22:00   paid  81,07 €      EUR
{'paid': 3629, 'PAID': 1537, 'Paid': 907, 'cancelled': 186}
{'EUR': 4987, 'eur': 643, '€': 629}
```
<!--sortie-->

Trois remarques s'imposent. Le **statut** est écrit de trois façons (`paid`, `PAID`, `Paid`) : une comparaison avec `== "paid"` laisserait de côté 40 % des commandes payées. La **devise** est écrite de trois façons aussi (`EUR`, `eur`, `€`) : une seule devise en réalité, mais un `groupby` sur la colonne brute en ferait trois groupes. Et le **montant** est un texte, avec un symbole, une virgule ou un point selon la ligne : `"34,92 €"`, `"158.42"`. Le plus sournois est ailleurs : regardons l'ordre de grandeur du montant mois par mois, après une conversion qui ignore pour l'instant tout format exotique.

```python
site["brut"] = pd.to_numeric(site["total"].str.replace("€", "").str.replace(" ", "").str.replace(",", "."), errors="coerce")
site["date_heure"] = pd.to_datetime(site["created_at"].str.replace("Z", "", regex=False), format="ISO8601")
site["mois"] = site["date_heure"].dt.month
mediane = site[site["customer_email"].str.lower() != "test@example.com"].groupby("mois")["brut"].median().round(0)
print(mediane.loc[7:11].to_string())
```
<!--sortie-->
```text
mois
7       91.0
8       87.0
9     1741.0
10    8426.0
11    7190.0
```
<!--sortie-->


Voilà une anomalie que **seul un contrôle d'ordre de grandeur** détecte : la **médiane du montant** vaut 87 € en août, 1 741 € en septembre et 8 426 € en octobre. Personne n'a vendu pour 8 000 € de bougies : à partir d'une certaine date, la plateforme exporte les montants **en centimes**. La rupture coïncide avec un autre changement, discret : à partir du 15 septembre, le texte de la date se termine par un `Z` (ISO 8601, heure UTC), alors qu'il n'en avait pas auparavant. Une mise à jour du site a changé **deux choses à la fois**, et n'en a annoncé aucune. L'hypothèse à tester : *les montants sont en centimes exactement quand la date porte le `Z`*. La médiane brute vaut 83 € sans `Z` et 7 901 € avec `Z`.

On **teste l'hypothèse** de la seule manière convaincante : on corrige, puis on **compare avec une autre source**, ici la somme des lignes de détail de chaque commande, qui est indépendante du montant total de l'en-tête.

```python
site["en_utc"] = site["created_at"].str.endswith("Z")
site["total_num"] = np.where(site["en_utc"], site["brut"] / 100, site["brut"])
lignes_site["montant"] = (lignes_site["qty"] * lignes_site["unit_price"] * (1 - lignes_site["discount_pct"] / 100)).round(2)
somme_lignes = lignes_site.groupby("order_ref")["montant"].sum().rename("somme_lignes")
test = site[site["customer_email"].str.lower() != "test@example.com"].drop_duplicates("order_ref").merge(somme_lignes, on="order_ref", how="left")
print("commandes dont le total égale la somme des lignes :", round(((test["total_num"] - test["somme_lignes"]).abs() < 0.011).mean() * 100, 1), "%")
```
<!--sortie-->
```text
commandes dont le total égale la somme des lignes : 100.0 %
```
<!--sortie-->


Sur 6 078 commandes, **100 %** ont un total égal à la somme de leurs lignes : l'hypothèse « centimes si et seulement si `Z` » est confirmée, au centime près. Reste à regarder la **date** elle-même. Un `Z` signifie « heure UTC » : si elle l'était vraiment, les heures de commande devraient se décaler d'une ou deux heures par rapport à celles d'avant la mise à jour, puisque la boutique n'est pas à l'heure UTC. Comparons l'heure moyenne de commande avant et après.

```python
heure_moyenne = site.assign(h=site["date_heure"].dt.hour).groupby("en_utc")["h"].mean().round(2)
print(heure_moyenne.to_dict())
```
<!--sortie-->
```text
{False: 15.45, True: 15.37}
```
<!--sortie-->


L'heure moyenne est de 15,45 avant et de 15,37 après : **aucun décalage**. Le `Z` est donc une étiquette sans effet sur les heures, ou les horodatages sont restés locaux malgré l'étiquette : nous les traiterons comme des heures locales, en **documentant** l'hypothèse (et en la signalant au responsable du site). Ce raisonnement, tester une hypothèse sur la distribution plutôt que de la croire, vaut mieux que n'importe quelle conversion de fuseau faite « au cas où ».

Il reste à **filtrer**. Trois catégories de lignes ne sont pas des ventes : les **commandes de test** (adresse `test@example.com`), les **doublons d'export** (même référence deux fois : l'export a été relancé) et les **commandes annulées**. On les retire **dans cet ordre, en comptant ce que l'on retire**, pour pouvoir en rendre compte.

```python
site["email_norm"] = site["customer_email"].str.strip().str.lower()
n0 = len(site)
s1 = site[site["email_norm"] != "test@example.com"]
s2 = s1.drop_duplicates("order_ref")
s3 = s2[s2["status"].str.lower() != "cancelled"]
print("export brut :", n0, "| sans tests :", len(s1), "| sans doublons :", len(s2), "| sans annulées :", len(s3))
cmd_site = site.assign(est_test=site["email_norm"] == "test@example.com", est_double=site.duplicated("order_ref"), statut=site["status"].str.lower())
```
<!--sortie-->
```text
export brut : 6259 | sans tests : 6199 | sans doublons : 6078 | sans annulées : 5897
```
<!--sortie-->


L'export contient 6 259 lignes ; on en retire 60 de test, 121 doublons et 181 annulées, pour **5 897 commandes** (600 164,13 € de chiffre d'affaires). Les commandes annulées pesaient 17 551,32 € : elles n'ont pas été vendues, et les compter gonflerait le chiffre d'affaires.

> 💡 **Intuition.** Un export n'est pas un fait, c'est un **document** produit par un logiciel, avec ses conventions et ses accidents. Avant de calculer avec lui, on le **lit comme on lirait un rapport** : que contient-il, que signifie chaque ligne, qu'est-ce qui a changé ? Les deux accidents de cet export (les centimes, les doublons) se détectent par **l'ordre de grandeur** et par le **comptage**, pas par la lecture ligne à ligne.

### 2.2.5 Relier les ventes aux produits : la jointure qui multiplie

La caisse ne note ni numéro de produit ni coût d'achat, seulement le **nom de l'article** et son prix unitaire. Pour calculer une marge, il faut retrouver le produit dans la table des produits. La première idée est de joindre **sur le nom**, normalisé avec la fonction `cle_texte` de la section 2.1.6.

```python
produits = pd.read_csv("donnees/produits.csv")
caisse["nom_cle"] = caisse["article"].map(cle_texte)
produits["nom_cle"] = produits["nom_produit"].map(cle_texte)
par_nom = caisse.merge(produits[["nom_cle", "id_produit", "cout_achat"]], on="nom_cle", how="left")
print("lignes avant :", len(caisse), "| après la jointure sur le nom :", len(par_nom))
try:
    caisse.merge(produits[["nom_cle", "id_produit"]], on="nom_cle", validate="m:1")
except Exception as e:
    print(type(e).__name__, ":", str(e).splitlines()[0])
```
<!--sortie-->
```text
lignes avant : 12678 | après la jointure sur le nom : 25356
MergeError : Merge keys are not unique in right dataset; not a many-to-one merge
```
<!--sortie-->


Le nombre de lignes **double** : de 12 678 à 25 356. La cause, vue en 2.1.6 : **chaque nom de produit est porté par deux produits**, donc chaque ligne de caisse se retrouve associée aux deux. Le chiffre d'affaires, recalculé sur cette table, passerait de 547 896 € à 1 095 793 €. C'est le piège classique de la jointure **n–n** : aucune erreur, un résultat **doublement faux**. Le paramètre `validate="m:1"` l'attrape, avec un message clair (le dernier affichage ci-dessus) ; c'est pourquoi il faut **toujours** le déclarer.

Que faire ? Chercher un **second élément de clé**. Les deux produits qui partagent un nom ont des **prix différents** (sauf exception, voir ci-dessous) : le prix de la ligne de caisse doit égaler le prix du catalogue majoré de la hausse de 3 % du 1er janvier 2025, ce qui permet de départager. Joindre sur un **prix** pose un problème technique : des nombres décimaux ne s'égalent pas toujours exactement (arrondis). On joint donc sur le nom, puis l'on **filtre** les candidats dont le prix est « assez proche » (à un demi-centime près).

```python
produits["prix_2025"] = (produits["prix_vente"] * 1.03).round(2)
c = caisse.reset_index().merge(produits[["nom_cle", "id_produit", "prix_2025", "cout_achat"]], on="nom_cle")
c = c[(c["prix_unitaire"] - c["prix_2025"]).abs() < 0.011]
n = c.groupby("index").size()
print("lignes appariées de façon unique :", int((n == 1).sum()), "| ambiguës :", int((n > 1).sum()), "| sans candidat :", len(caisse) - len(n))
```
<!--sortie-->
```text
lignes appariées de façon unique : 12452 | ambiguës : 226 | sans candidat : 0
```
<!--sortie-->


Avec le prix, **12 452 lignes** trouvent un produit **unique**, aucune n'est sans candidat, et 226 restent **ambiguës**. Ces dernières correspondent à une seule paire de produits, les numéros 62 et 72 (le même nom), qui ont **exactement le même prix** (2,90 €) **et le même coût d'achat** (1,53 € et 1,53 €) : **aucun** élément de la ligne de caisse ne permet de dire de quel produit il s'agit. Deux conséquences :

- l'identité du produit reste **inconnue** pour ces 226 lignes : on laisse `id_produit` **vide** plutôt que de tirer au sort ;
- mais la **marge n'est pas affectée**, puisque les deux produits ont le même coût : on peut y mettre la moyenne des coûts candidats. C'est une **ambiguïté sans conséquence pour la question posée**, et c'est ce qu'il faut écrire (elle en aurait pour une question sur le stock par produit).

On range ce résultat dans la table de caisse : l'identifiant du produit quand il est unique, le coût d'achat dans tous les cas.

```python
unique = n[n == 1].index
caisse["id_produit"] = np.nan
caisse.loc[unique, "id_produit"] = c[c["index"].isin(unique)].set_index("index")["id_produit"]
caisse["cout_achat"] = c.groupby("index")["cout_achat"].mean()
print(caisse[["article", "prix_unitaire", "id_produit", "cout_achat"]].head(3).to_string(index=False))
print("lignes sans id_produit :", int(caisse["id_produit"].isna().sum()), "| sans coût :", int(caisse["cout_achat"].isna().sum()))
```
<!--sortie-->
```text
         article  prix_unitaire  id_produit  cout_achat
       Poêle mat          40.07         2.0       21.47
  Tapis nordique          64.79        26.0       28.56
Théière rustique          52.43         5.0       24.65
lignes sans id_produit : 226 | sans coût : 0
```
<!--sortie-->


Pour le site, la question ne se pose pas : les lignes portent une **référence produit** (`sku`, comme `P043`) qui contient directement le numéro du produit. Une vraie clé vaut mieux que la meilleure reconstitution : si l'on peut obtenir de la source un identifiant plutôt qu'un libellé, **on le demande**.

> ⚠️ **Piège : les homonymes.** Dans nos données, c'est un artefact de fabrication ; dans la vie réelle, c'est courant (deux clients nommés « Martin », deux articles « Coussin bleu » de tailles différentes). **Un nom n'est jamais une clé.** Quand on est forcé de joindre sur un libellé, on teste l'unicité de la clé (`validate=`), on lui adjoint un second critère, et l'on **compte** ce qui reste ambigu.


![Nombre de lignes de la caisse avant et après jointure avec les produits : la jointure sur le nom seul double les lignes ; ajouter le prix à la clé rétablit un produit unique, sauf pour une paire de produits indiscernables.](figures/ch02-jointure-effectifs.png)

### 2.2.6 Harmoniser et empiler : la table des ventes

Les deux sources sont maintenant propres. Pour les empiler, il faut qu'elles aient le **même schéma** : mêmes noms de colonnes, mêmes types, mêmes unités. On le **conçoit d'abord**, comme un contrat.

| Colonne commune | Définition | Caisse | Site |
|---|---|---|---|
| `source`, `canal` | d'où vient la ligne | `caisse`, `Boutique` | `site`, `Site` |
| `id_commande` | numéro de commande | numéro du ticket sans le `T` | référence sans `WEB-` |
| `date` | jour de la vente | date du ticket | date de l'horodatage |
| `id_produit`, `nom_produit`, `categorie` | produit, en écriture normalisée | reconstitués (2.2.5) ; nom et catégorie pris dans le catalogue | `sku` converti ; nom et catégorie pris dans le catalogue |
| `quantite`, `prix_unitaire`, `remise_pct` | comme dans la source | remise connue seulement au dernier trimestre | `qty`, `unit_price`, `discount_pct` |
| `montant` | montant TTC payé, **en euros** | lu, ou reconstitué | quantité × prix × (1 − remise) |
| `cout_achat` | coût d'achat unitaire | du catalogue | du catalogue |
| `montant_reconstitue`, `identique_precedente` | **indicateurs de qualité** | oui / ligne identique à la précédente | non |

Le schéma est le **contrat** entre les sources et l'analyse : si une colonne ne peut pas être alimentée honnêtement, on la laisse **vide** plutôt que de lui donner une valeur plausible. Construisons d'abord la partie caisse. Le nom et la catégorie viennent du **catalogue** (une seule écriture normalisée au lieu des cinq de la caisse).

```python
ref_nom = produits.drop_duplicates("nom_cle").set_index("nom_cle")[["nom_produit", "categorie"]]
v_caisse = caisse.drop(columns=["categorie"]).join(ref_nom, on="nom_cle")
v_caisse = v_caisse.assign(source="caisse", canal="Boutique", montant=v_caisse["montant_corrige"], montant_reconstitue=v_caisse["montant_vide"])
print(v_caisse[["id_commande", "nom_produit", "categorie", "quantite", "montant", "montant_reconstitue"]].head(3).to_string(index=False))
```
<!--sortie-->
```text
 id_commande      nom_produit categorie  quantite  montant  montant_reconstitue
       23468        Poêle mat   Cuisine         1    40.07                False
       23468   Tapis nordique    Maison         1    64.79                False
       23458 Théière rustique   Cuisine         1    52.43                False
```
<!--sortie-->

Puis la partie site : on ne garde que les commandes valides, on relie les lignes à leur commande, on convertit la référence produit, on calcule le montant, et l'on ajoute le nom, la catégorie et le coût du catalogue par une jointure **m:1** (vérifiée).

```python
ok = cmd_site[~cmd_site["est_test"] & ~cmd_site["est_double"] & (cmd_site["statut"] != "cancelled")]
ls = lignes_site.merge(ok[["order_ref", "date_heure"]].assign(id_commande=ok["order_ref"].str[4:].astype(int)), on="order_ref", validate="m:1")
ls = ls.assign(id_produit=ls["sku"].str[1:].astype(int), quantite=ls["qty"], prix_unitaire=ls["unit_price"], remise_pct=ls["discount_pct"])
v_site = ls.merge(produits[["id_produit", "nom_produit", "categorie", "cout_achat"]], on="id_produit", validate="m:1")
v_site = v_site.assign(source="site", canal="Site", date=v_site["date_heure"].dt.normalize(), montant_reconstitue=False, identique_precedente=False)
print("lignes de commandes valides :", len(ls), "| lignes après jointure produits :", len(v_site))
```
<!--sortie-->
```text
lignes de commandes valides : 13510 | lignes après jointure produits : 13510
```
<!--sortie-->

Il ne reste qu'à **empiler** les deux parties, en ne gardant que les colonnes du contrat et dans le même ordre, puis à calculer la marge (2.1.2).

```python
cols = ["source", "canal", "id_commande", "date", "id_produit", "nom_produit", "categorie", "quantite", "prix_unitaire", "remise_pct", "montant",
        "cout_achat", "montant_reconstitue", "identique_precedente"]
ventes = pd.concat([v_caisse[cols], v_site[cols]], ignore_index=True)
ventes["marge_ht"] = ventes["montant"] / 1.20 - ventes["quantite"] * ventes["cout_achat"]
resume = ventes.groupby("canal").agg(lignes=("montant", "size"), commandes=("id_commande", "nunique"), ca=("montant", "sum"), marge=("marge_ht", "sum"))
print(resume.round(0).to_string())
```
<!--sortie-->
```text
          lignes  commandes        ca     marge
canal                                          
Boutique   12678       5442  564473.0  178813.0
Site       13510       5897  600164.0  189431.0
```
<!--sortie-->


**La table demandée par la gérante existe** : 26 188 lignes de vente pour l'année 2025, avec le produit, la catégorie, le montant, le coût d'achat et la marge (37,9 % du chiffre d'affaires hors taxe sur l'ensemble). La caisse a 5 442 commandes pour 564 473 € et le site 5 897 commandes pour 600 164 €. Mais **une table n'est pas fiable parce qu'elle a été construite sans erreur** : il faut maintenant la contrôler.

![Chaîne de préparation des ventes de 2025.](figures/ch02-chaine.png)


### 2.2.7 Contrôler : comparer à la base, puis ouvrir la vérité

Pour contrôler la table des ventes, il faut un **point de comparaison indépendant**. Ici, nous en avons un : la base du volume I (`commandes` et `lignes_commande`), qui contient les mêmes ventes telles que le système de gestion les a enregistrées. On compare, **canal par canal**, le chiffre d'affaires de notre table avec celui de la base.

```python
cmd_b = pd.read_csv("donnees/commandes.csv", parse_dates=["date_commande"])
base = lig.merge(cmd_b[["id_commande", "date_commande", "canal"]], on="id_commande", validate="m:1")
base = base[base["date_commande"].dt.year == 2025]
comp = pd.DataFrame({"table_ventes": ventes.groupby("canal")["montant"].sum(), "base": base.groupby("canal")["montant"].sum()}).dropna()
comp["ecart"] = comp["table_ventes"] - comp["base"]
comp["ecart_pct"] = comp["ecart"] / comp["base"] * 100
print(comp.round(2).to_string())
```
<!--sortie-->
```text
          table_ventes       base     ecart  ecart_pct
canal                                                 
Boutique     564472.59  560973.91   3498.68       0.62
Site         600164.13  617715.45 -17551.32      -2.84
```
<!--sortie-->


Deux écarts, **deux explications** à produire. Pour la **Boutique**, la table dépasse la base de 3 498,68 € (+0,62 %) : on retrouve exactement l'écart du total de contrôle de 2.2.3, c'est-à-dire les lignes identiques **et** la reconstitution approximative des montants. Pour le **Site**, la table est **inférieure** à la base de 17 551,32 € (2,8 %) : c'est la somme des commandes annulées retirées en 2.2.4 (17 551,32 €), qui existent dans la base mais ne sont pas des ventes. Un écart n'est « bon » ou « mauvais » que **s'il est expliqué**.

Ouvrons maintenant la **vérité**. Le fichier `verite_caisse.csv` indique, pour chaque ligne de chaque fichier, le numéro de la ligne de commande d'origine et si c'est un vrai double scan. Cela permet de savoir **ce que valaient nos décisions**, une chose impossible dans la vie réelle.

```python
verite = pd.read_csv("donnees/verite_caisse.csv")
caisse["rang"] = caisse.groupby("fichier").cumcount(); verite["rang"] = verite.groupby("fichier").cumcount()
cv = caisse.merge(verite[["fichier", "rang", "id_ligne", "est_doublon"]], on=["fichier", "rang"], validate="1:1")
cv["montant_vrai"] = cv["id_ligne"].map(lig.set_index("id_ligne")["montant"])
ident = cv[cv["identique_precedente"]]
print("lignes identiques :", len(ident), "| vrais doubles scans :", int(ident["est_doublon"].sum()), "| répétitions légitimes :", int((ident["est_doublon"] == 0).sum()))
vides = cv[cv["montant_vide"] & (cv["est_doublon"] == 0)]
print("montants vides : reconstitués", round(vides["montant_corrige"].sum(), 2), "€ | vrais", round(vides["montant_vrai"].sum(), 2), "€")
```
<!--sortie-->
```text
lignes identiques : 154 | vrais doubles scans : 67 | répétitions légitimes : 87
montants vides : reconstitués 16445.46 € | vrais 16203.78 €
```
<!--sortie-->


La vérité éclaire notre choix. Sur les 154 lignes identiques, **67** seulement sont de vrais doubles scans ; **87** sont des répétitions légitimes. Supprimer toutes les lignes identiques aurait donc retiré 87 ventes réelles. En ne supprimant rien, nous avons conservé 67 lignes en trop, pour 3 257 € : c'est le gros de l'écart de 3 499 € de la Boutique. Le reste, 242 €, vient de la reconstitution des montants vides : nous avons supposé une remise nulle avant octobre, et le montant reconstitué (16 445,46 €) dépasse un peu le vrai (16 203,78 €), parce que des remises existaient. **Aucune de nos deux hypothèses n'était parfaite, et l'erreur totale reste à 0,62 %** : c'est ce que l'on écrit dans la note de méthode, et c'est suffisant pour la question de la gérante (la marge par catégorie), mais ce ne serait pas acceptable pour un rapprochement comptable au centime (chapitre 3).

### 2.2.8 Chercher ce qui manque : les anti-jointures

Une jointure ne dit pas seulement ce qui se **retrouve**, mais aussi ce qui **ne se retrouve pas**. L'**anti-jointure** (les lignes d'une table qui n'ont **aucune** correspondance dans l'autre) est l'outil de recherche des manques. On l'obtient avec `indicator=True` puis un filtre sur `left_only`. Quatre questions, quatre anti-jointures.

**Les références du site existent-elles toutes dans la base ?** On joint les références de l'export à celles de la base (qui s'écrivent `WEB-` suivi du numéro sur six chiffres).

```python
refs_base = "WEB-" + cmd_b["id_commande"].astype(str).str.zfill(6)
anti = site[["order_ref"]].drop_duplicates().merge(refs_base.rename("order_ref"), on="order_ref", how="left", indicator=True)
print("références de l'export absentes de la base :", int((anti["_merge"] == "left_only").sum()), "| exemples :", anti.loc[anti["_merge"] == "left_only", "order_ref"].head(3).tolist())
sens_inverse = cmd_b[(cmd_b["canal"] == "Site") & (cmd_b["date_commande"].dt.year == 2025)]
print("commandes Site 2025 de la base absentes de l'export :", int((~("WEB-" + sens_inverse["id_commande"].astype(str).str.zfill(6)).isin(site["order_ref"])).sum()))
```
<!--sortie-->
```text
références de l'export absentes de la base : 60 | exemples : ['WEB-T0011', 'WEB-T0015', 'WEB-T0014']
commandes Site 2025 de la base absentes de l'export : 0
```
<!--sortie-->


Les 60 références absentes de la base sont des **commandes de test** (leur numéro commence par `WEB-T`) : l'anti-jointure les aurait retrouvées même sans l'adresse électronique. Dans l'autre sens, **aucune** commande de la base n'est absente de l'export : rien n'a été perdu à l'extraction.

**Quelle part de l'activité n'est dans aucun des deux fichiers ?** La gérante a demandé « la caisse et le site ». Or la boutique vend aussi par un troisième canal, les réseaux : la base le montre.

```python
ca_canaux = base.groupby("canal")["montant"].sum()
couvert = ca_canaux[["Boutique", "Site"]].sum()
print("part du chiffre d'affaires 2025 couverte par la caisse et le site :", round(couvert / ca_canaux.sum() * 100, 1), "%")
print("chiffre d'affaires du canal Réseaux, absent des deux sources :", round(ca_canaux["Réseaux"], 0), "€")
```
<!--sortie-->
```text
part du chiffre d'affaires 2025 couverte par la caisse et le site : 89.0 %
chiffre d'affaires du canal Réseaux, absent des deux sources : 146074.0 €
```
<!--sortie-->


La table construite couvre **89 %** du chiffre d'affaires de 2025 : le canal Réseaux, soit 146 074 € (11 %), n'a **aucune source** dans les fichiers que l'on nous a remis. C'est une information à **rendre à la gérante** avant qu'elle ne présente la table comme « toutes les ventes ».

**Les adresses électroniques du site retrouvent-elles les clients du CRM ?** Joindre les commandes du site aux clients du CRM se fait par l'adresse électronique. Essayons d'abord sur l'écriture **brute**, puis sur une écriture **normalisée** (espaces retirés, minuscules).

```python
crm = pd.read_csv("donnees/crm_clients.csv", dtype=str, keep_default_na=False)
valides = site[site["email_norm"] != "test@example.com"].drop_duplicates("order_ref")
brut_ok = valides["customer_email"].isin(set(crm["email"]))
norm_ok = valides["email_norm"].isin(set(crm["email"].str.strip().str.lower()))
print("e-mails retrouvés dans le CRM : brut", round(brut_ok.mean() * 100, 1), "% | normalisé", round(norm_ok.mean() * 100, 1), "%")
```
<!--sortie-->
```text
e-mails retrouvés dans le CRM : brut 87.7 % | normalisé 100.0 %
```
<!--sortie-->


Sur l'écriture brute, **750 commandes** sur 6 078 ne retrouvent pas leur client (87,7 % de succès) : des majuscules, des espaces superflus. Après une normalisation de deux lignes, tout se retrouve (100 %). Cette différence illustre le principe de toute jointure sur du texte : **normaliser avant de joindre**, puis mesurer le taux de correspondance.

> ✅ **À retenir.** Une **anti-jointure** n'est pas un accessoire : c'est le moyen de répondre à « *qu'est-ce qui manque ?* », celui que la gérante n'a pas pensé à poser (le canal Réseaux), et à « *qu'est-ce qui ne devrait pas être là ?* » (les commandes de test).

### 2.2.9 Le même résultat avec trois outils

Une table de ventes de cette importance se recoupe avec **un autre outil**, pas avec le même code relancé. On écrit la table dans un fichier, puis on calcule le même résumé (lignes et chiffre d'affaires par canal et par mois) avec **DuckDB** (SQL) et avec **R**, et l'on compare à pandas.

```python
ventes["mois"] = ventes["date"].dt.strftime("%Y-%m")
ventes.to_csv(os.path.join(TMP2, "ventes.csv"), index=False)
os.environ["TMP2"] = TMP2
q = f"select canal, strftime(date, '%Y-%m') as mois, count(*) as lignes, round(sum(montant), 2) as ca from '{TMP2}/ventes.csv' group by 1, 2 order by 1, 2"
sql = duckdb.sql(q).df()
pdm = ventes.groupby(["canal", "mois"]).agg(lignes=("montant", "size"), ca=("montant", "sum")).round(2).reset_index()
print("DuckDB = pandas :", bool((sql["lignes"].values == pdm["lignes"].values).all() and np.allclose(sql["ca"].values, pdm["ca"].values)))
```
<!--sortie-->
```text
DuckDB = pandas : True
```
<!--sortie-->

Et le même calcul en **R**, avec `dplyr` (la jointure ou le regroupement s'écrivent à peu près comme en pandas : volume I, section 4.2) ; R écrit son résultat dans un fichier, que Python relit pour le comparer.

```r
library(dplyr, warn.conflicts = FALSE)
v <- read.csv(file.path(Sys.getenv("TMP2"), "ventes.csv"))
r <- v |> group_by(canal, mois) |> summarise(lignes = n(), ca = round(sum(montant), 2), .groups = "drop")
write.csv(r, file.path(Sys.getenv("TMP2"), "ventes_r.csv"), row.names = FALSE)
print(as.data.frame(r |> group_by(canal) |> summarise(lignes = sum(lignes), ca = round(sum(ca), 0))))
```
<!--sortie-->
```text
     canal lignes     ca
1 Boutique  12678 564473
2     Site  13510 600164
```
<!--sortie-->

```python
r = pd.read_csv(os.path.join(TMP2, "ventes_r.csv"))
print("R = pandas :", bool((r["lignes"].values == pdm["lignes"].values).all() and np.allclose(r["ca"].values, pdm["ca"].values)))
```
<!--sortie-->
```text
R = pandas : True
```
<!--sortie-->


Trois outils, un même résultat à l'euro près. Si DuckDB ou R avaient donné un écart, la première hypothèse n'aurait pas été « l'outil se trompe », mais « *je n'ai pas demandé la même chose aux deux* » : un filtre de dates différent, une jointure qui duplique, un arrondi. C'est cette recherche de la **différence de question** qui fait la valeur de la vérification croisée.

> ✅ **À retenir.**
> - **Joindre** ajoute des colonnes, **empiler** ajoute des lignes ; le **type** de jointure est un choix d'analyse, et `indicator=True` en est le diagnostic.
> - À chaque jointure, **quatre contrôles** : lignes avant et après, somme avant et après, lignes sans correspondance, unicité de la clé. `validate=` transforme l'hypothèse de cardinalité en **vérification**.
> - Une jointure **n–n** multiplie les lignes **sans erreur** : un nom n'est jamais une clé ; on ajoute un critère et l'on **compte** les ambiguïtés restantes.
> - Une source qui **dérive** (codage, séparateur, décimale, unité) se lit en **détectant** son format, pas en le devinant ; la **ligne de total** d'un fichier est une somme de contrôle gratuite.
> - On **ne supprime rien sans preuve** : on garde, on marque, on documente l'incertitude résiduelle (ici moins de 1 %).
> - Un écart n'est acceptable que **expliqué** ; une **anti-jointure** cherche ce qui manque (un canal entier, des commandes de test).
> - Deux outils valent mieux qu'un : DuckDB et R ont retrouvé les chiffres de pandas.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.3 à 2.6, exercices 2.5 à 2.8.


## 2.3 Agrégation et restructuration

La table des ventes compte plus de vingt-six mille lignes, et la gérante n'en lira aucune. Ce qu'elle veut, ce sont des chiffres **à un autre niveau de détail** : par mois, par canal, par catégorie, par client. **Agréger**, c'est passer d'un niveau fin à un niveau plus grossier en **résumant** : sommer, compter, moyenner. C'est le geste le plus fréquent de l'analyste, et celui qui cache le plus de pièges, parce que **chaque niveau de détail a sa propre définition du « nombre de… »**. Cette section apprend à raisonner sur le **grain** d'une table, à agréger sans compter deux fois, à calculer des parts, des rangs et des cumuls, à organiser les tables en **faits et dimensions**, et à vérifier par une **somme de contrôle** que rien n'a bougé.

### 2.3.1 Le grain d'une table et le changement de grain

Le **grain** d'une table est ce que représente **une ligne**. Dans notre table des ventes, une ligne est une **ligne de vente** (un article, dans une commande). Une commande compte plusieurs lignes ; un client passe plusieurs commandes. Trois niveaux, donc trois grains :

| Grain | Une ligne représente… | Exemple de colonnes | Nombre de lignes en 2025 (sources du chapitre) |
|---|---|---|---|
| **ligne** | un article vendu | produit, quantité, montant | 26 188 (caisse et site) |
| **commande** | un panier | date, canal, montant total, nombre d'articles | 11 339 |
| **client** | une personne | nombre de commandes, chiffre d'affaires, dernière date | 3 875 clients acheteurs (base) |

Passer d'un grain fin à un grain grossier est **l'agrégation** ; passer dans l'autre sens est impossible (on ne retrouve pas les lignes à partir des totaux). Il faut donc **garder la table la plus fine** et fabriquer les autres, jamais l'inverse. Et à chaque changement de grain, les mêmes mots ne désignent plus les mêmes choses : « nombre de commandes » est un **comptage de lignes distinctes** au grain ligne, et un simple **comptage de lignes** au grain commande.


Une remarque honnête : la table `ventes` (caisse et site) **ne contient pas le client**. La caisse n'enregistre pas qui achète, et le site fournit une adresse électronique que l'on peut relier au CRM, mais pas avec certitude (section 2.5). Pour le niveau « client », nous repartirons donc de la **base** du volume I, qui porte `id_client` sur chaque commande. C'est un exemple de la règle : **on ne peut agréger que selon ce que la table contient**.

### 2.3.2 `groupby` et `agg` : compter sans compter deux fois

L'outil est `groupby` suivi de `agg`, avec des **agrégats nommés** : `nom_de_la_colonne_résultat=("colonne_source", "fonction")`. Voici, par canal et par mois, le chiffre d'affaires, le nombre de lignes, le nombre de **commandes distinctes**, le panier moyen et le taux de marge.

```python
par_mois = ventes.groupby(["canal", "mois"]).agg(ca=("montant", "sum"), lignes=("montant", "size"),
                                                commandes=("id_commande", "nunique"), marge=("marge_ht", "sum"))
par_mois["panier_moyen"] = par_mois["ca"] / par_mois["commandes"]
par_mois["taux_marge"] = par_mois["marge"] / (par_mois["ca"] / 1.20)
print(par_mois.loc["Site"].tail(3).round(2).to_string())
```
<!--sortie-->
```text
               ca  lignes  commandes     marge  panier_moyen  taux_marge
mois                                                                    
2025-10  54999.72    1214        514  17848.28        107.00        0.39
2025-11  62884.28    1552        693  19364.05         90.74        0.37
2025-12  87496.07    1995        882  28616.09         99.20        0.39
```
<!--sortie-->


Trois définitions à ne pas confondre. Le **nombre de lignes** (`size`) est un comptage d'articles : 1 995 en décembre pour le site. Le **nombre de commandes** (`nunique` sur `id_commande`) est un comptage de paniers : 882. Le **panier moyen** est le **chiffre d'affaires divisé par le nombre de commandes** (87 496 € / 882 = 99,20 €), et **non** le montant moyen d'une ligne, qui serait environ deux fois plus petit. Le taux de marge de décembre (39,2 %) est, comme en 2.1.2, un rapport de sommes.

Il y a pourtant un piège plus subtil que le choix de la fonction : certains comptages **ne s'additionnent pas**. Une commande appartient à **un seul** mois, donc le nombre de commandes distinctes d'une année est bien la somme des nombres mensuels. Un client, lui, peut acheter plusieurs mois. Comparons, avec la base, la somme des clients distincts mois par mois et le nombre de clients distincts de l'année.

```python
v25["mois"] = v25["date_commande"].dt.month
mensuel = v25.groupby("mois")["id_client"].nunique()
print("somme des clients distincts de chaque mois :", int(mensuel.sum()))
print("clients distincts de l'année :", v25["id_client"].nunique())
print("somme des commandes distinctes par mois :", int(v25.groupby("mois")["id_commande"].nunique().sum()), "| commandes distinctes de l'année :", v25["id_commande"].nunique())
```
<!--sortie-->
```text
somme des clients distincts de chaque mois : 10621
clients distincts de l'année : 3875
somme des commandes distinctes par mois : 12946 | commandes distinctes de l'année : 12946
```
<!--sortie-->


La somme des clients mensuels (10 621) est **2,7 fois** le nombre réel de clients (3 875) : les clients qui reviennent sont comptés autant de fois qu'ils achètent de mois différents. **Un comptage distinct n'est additif que si les groupes ne se recouvrent pas.** Règle pratique : un total « tous mois » d'un nombre de clients se recalcule **sur les données**, il ne se déduit **jamais** d'une colonne de totaux mensuels.

> ⚠️ **Piège : additionner des moyennes, des taux, des comptages distincts.** Les **sommes** s'additionnent ; les **moyennes**, les **ratios** et les **comptages distincts** non. Pour recomposer un niveau supérieur à partir d'un niveau inférieur, on garde les **composantes** (somme et effectif, numérateur et dénominateur) et l'on refait le ratio.

### 2.3.3 `transform` : un agrégat sans perdre les lignes

`agg` **réduit** : une ligne par groupe. `transform` calcule le même agrégat, mais le **recopie sur chaque ligne** du groupe : le nombre de lignes ne change pas. C'est l'outil de tout ce qui compare une ligne à son groupe : une **part du total**, un **écart à la moyenne**, un **rang**.

```python
n_avant = len(ventes)
ventes["ca_mois"] = ventes.groupby("mois")["montant"].transform("sum")
ventes["part_du_mois"] = ventes["montant"] / ventes["ca_mois"]
ventes["rang_dans_categorie"] = ventes.groupby("categorie")["montant"].rank(method="dense", ascending=False)
t = ventes.groupby(["mois", "canal"])["part_du_mois"].sum().unstack()
print(t.tail(3).round(3).to_string())
print("lignes avant / après transform :", n_avant, len(ventes))
```
<!--sortie-->
```text
canal    Boutique   Site
mois                    
2025-10     0.483  0.517
2025-11     0.492  0.508
2025-12     0.457  0.543
lignes avant / après transform : 26188 26188
```
<!--sortie-->


Chaque ligne porte désormais la part qu'elle représente dans son mois ; en les resommant par canal, on retrouve la part de chacun : en décembre, la Boutique pèse 45,7 % et le Site 54,3 % du chiffre d'affaires des deux sources (la somme des parts fait 1, ce qui est **un contrôle**). La dernière ligne affichée montre, avant et après, que `transform` **conserve toutes les lignes**, contrairement à `agg`.

Le **rang** (`rank`) réclame une décision de présentation : `method="dense"` donne 1, 2, 2, 3 en cas d'égalité (pas de « trou »), alors que `method="min"` donnerait 1, 2, 2, 4. On choisit selon l'usage et l'on **l'écrit**.

### 2.3.4 Du grain ligne au grain commande, puis au grain client

Fabriquer la table des commandes, puis celle des clients, se fait par deux agrégations successives. Chaque ligne de la table des clients **résume** ce que le client a fait : combien de commandes, quel chiffre d'affaires, quand pour la dernière fois (la **récence**), dans quel canal il achète le plus souvent.

```python
fin = pd.Timestamp("2025-12-31")
clients_2025 = v25.groupby("id_client").agg(nb_commandes=("id_commande", "nunique"), ca=("montant", "sum"),
                                            premiere=("date_commande", "min"), derniere=("date_commande", "max"))
clients_2025["recence_jours"] = (fin - clients_2025["derniere"]).dt.days
clients_2025["canal_principal"] = v25.groupby("id_client")["canal"].agg(lambda s: s.mode().iloc[0])
print(clients_2025.describe().loc[["mean", "50%", "max"], ["nb_commandes", "ca", "recence_jours"]].round(1).to_string())
```
<!--sortie-->
```text
      nb_commandes      ca  recence_jours
mean           3.3   341.9           91.5
50%            2.0   233.2           53.0
max           25.0  3382.3          364.0
```
<!--sortie-->


La moyenne du nombre de commandes (3,3) est supérieure à la médiane (2) : quelques gros clients (jusqu'à 25 commandes) tirent la moyenne, et 32 % des clients n'ont acheté **qu'une fois** en 2025. Le client médian a dépensé 233 € et sa dernière commande date de 53 jours : tout ce qu'une **segmentation** de clientèle (volume III de cette série) saura exploiter.

Chaque changement de grain se **contrôle**. Les trois tables doivent porter le **même chiffre d'affaires** et le **même nombre de commandes**.

```python
v25_cmd = v25.groupby("id_commande", as_index=False).agg(ca=("montant", "sum"), id_client=("id_client", "first"))
print("CA des lignes :", round(v25["montant"].sum(), 2), "| des commandes :", round(v25_cmd["ca"].sum(), 2), "| des clients :", round(clients_2025["ca"].sum(), 2))
print("commandes :", v25["id_commande"].nunique(), "=", len(v25_cmd), "=", int(clients_2025["nb_commandes"].sum()))
```
<!--sortie-->
```text
CA des lignes : 1324763.72 | des commandes : 1324763.72 | des clients : 1324763.72
commandes : 12946 = 12946 = 12946
```
<!--sortie-->

Un dernier point : la table des clients ne contient que les **acheteurs de 2025**. Si l'on veut parler **de tous** les clients (par exemple « quelle part est inactive ? »), il faut partir de la table complète des clients et faire une jointure **à gauche** : les clients sans achat auront des vides, qu'il faudra **remplacer par zéro pour les compteurs** (nombre de commandes, chiffre d'affaires), mais **pas** pour la récence (un client qui n'a jamais acheté n'a pas une récence de zéro jour). Cela rejoint le piège de 2.1.7 : le sens d'un vide dépend de la colonne.

### 2.3.5 Table de faits et dimensions

Une organisation des tables, très répandue en analyse, évite de tout recopier partout : le **schéma en étoile**. Au centre, une **table de faits** : ce qui se produit et se mesure (une ligne de vente, avec ses montants et ses quantités). Autour, des **dimensions** : les « axes » selon lesquels on regarde les faits (le produit, la date, le canal, le client). Chaque fait porte, pour chaque dimension, une **clé** qui renvoie à une ligne de la dimension.


![Schéma en étoile : une table de faits (les lignes de vente) entourée de dimensions (date, produit, canal, client), reliées par des clés.](figures/ch02-etoile.png)

Pourquoi cette organisation ? Parce qu'elle **sépare ce qui change souvent** (les ventes, qui s'ajoutent chaque jour) de **ce qui change rarement** (le catalogue, le calendrier), et parce qu'elle règle la question du grain : la table de faits a **un** grain, les dimensions ont **le leur**. Une jointure entre faits et dimension est par construction **n–1** : la clé de la dimension est unique, donc le nombre de lignes de faits ne change pas, et l'on peut le **vérifier**. Voici la dimension de date de 2025, un calendrier avec une ligne par jour, joint à la table de faits.

```python
dim_date = pd.DataFrame({"date": pd.date_range("2025-01-01", "2025-12-31")})
dim_date["trimestre"] = dim_date["date"].dt.quarter
dim_date["semaine_iso"] = dim_date["date"].dt.isocalendar().week
dim_date["week_end"] = dim_date["date"].dt.dayofweek >= 5
f = ventes.merge(dim_date, on="date", how="left", validate="m:1")
print("lignes avant / après :", len(ventes), len(f), "| dates sans correspondance :", int(f["trimestre"].isna().sum()))
print(f.groupby("trimestre")["montant"].sum().round(0).to_dict())
```
<!--sortie-->
```text
lignes avant / après : 26188 26188 | dates sans correspondance : 0
{1: 225285.0, 2: 273107.0, 3: 274942.0, 4: 391302.0}
```
<!--sortie-->


La jointure conserve les 26 188 lignes, sans date orpheline : le trimestre est ajouté à chaque ligne en un seul geste (le quatrième trimestre pèse 391 302 € contre 225 285 € pour le premier). Le **calendrier** offre autre chose : il liste **tous** les jours, y compris ceux où rien ne s'est vendu. Ici la Boutique a des ventes sur 365 jours sur 365, et le Site sur 365 : aucune journée creuse. Mais dans une série où un jour manquerait, c'est **la dimension de date qui le ferait voir**, alors qu'un `groupby` sur la table de faits ne produirait simplement **pas de ligne** pour ce jour (et un graphique le raccorderait sans rien dire).

> 💡 **Intuition.** Une table de faits répond à « *combien ?* », une dimension à « *selon quoi ?* ». Quand une question commence par « par… » (par mois, par catégorie, par canal), elle désigne une dimension.

### 2.3.6 Cumuls, moyennes mobiles et comparaisons dans le temps

Une série quotidienne est bruitée (les samedis sont forts, les dimanches faibles) ; deux outils la lissent ou la **cumulent**. Le **cumul** (`cumsum`) donne le chiffre d'affaires depuis le début de l'année, utile pour comparer à un objectif. La **moyenne mobile** (`rolling`) remplace chaque jour par la moyenne des sept derniers jours : une fenêtre de **sept** jours contient exactement un exemplaire de chaque jour de la semaine, ce qui efface l'effet de la semaine.

```python
jour = ventes.groupby(["canal", "date"])["montant"].sum().unstack("canal").fillna(0)
jour["total"] = jour.sum(axis=1)
jour["cumul"] = jour["total"].cumsum()
jour["moy7"] = jour["total"].rolling(7, min_periods=7).mean()
print(jour[["total", "cumul", "moy7"]].iloc[[0, 6, 7, -1]].round(0).to_string())
```
<!--sortie-->
```text
canal        total      cumul    moy7
date                                 
2025-01-01  2086.0     2086.0     NaN
2025-01-07  1969.0    17511.0  2502.0
2025-01-08  2552.0    20063.0  2568.0
2025-12-31  2838.0  1164637.0  4778.0
```
<!--sortie-->


Le chiffre d'affaires cumulé atteint 1 164 637 € au 31 décembre (c'est exactement la somme de la table : un cumul **se termine par le total**, autre contrôle). La moyenne mobile ne commence qu'au septième jour : les six premières valeurs sont **vides** (6 jours), parce que `min_periods=7` refuse de calculer sur une fenêtre incomplète ; on préfère un vide à une valeur trompeuse. Elle vaut 3 208 € par jour à la mi-juin et 4 860 € à la mi-décembre. Le même cumul s'écrit en SQL par une **fonction fenêtre** (`sum(...) over (order by date)`, volume I, section 3.3.5) ; calculé avec DuckDB sur le fichier écrit en 2.2.9, il donne la même série.


![À gauche, chiffre d'affaires cumulé de 2025 (caisse et site) ; à droite, chiffre d'affaires quotidien et sa moyenne mobile sur sept jours, qui efface l'effet du jour de la semaine.](figures/ch02-cumul.png)

### 2.3.7 La somme de contrôle : rien n'a bougé

Agréger, c'est résumer, donc **perdre** du détail ; mais il ne faut perdre **ni argent ni lignes**. Un jeu de **contrôles d'invariants** vérifie que les quantités qui doivent se conserver se conservent : le chiffre d'affaires est le même à tous les niveaux (ligne, mois, canal, commande), le nombre de commandes aussi, et les cumuls finissent sur le total. On en fait une petite fonction, que l'on **relance à chaque modification** de la chaîne.

```python
def controles(table):
    total = table["montant"].sum()
    return {"CA par canal = CA total": np.isclose(table.groupby("canal")["montant"].sum().sum(), total),
            "CA par mois = CA total": np.isclose(table.groupby("mois")["montant"].sum().sum(), total),
            "CA par commande = CA total": np.isclose(table.groupby(["canal", "id_commande"])["montant"].sum().sum(), total),
            "aucun montant vide": table["montant"].notna().all(),
            "aucune commande sans date": table["date"].notna().all()}
print(pd.Series(controles(ventes)).to_string())
```
<!--sortie-->
```text
CA par canal = CA total       True
CA par mois = CA total        True
CA par commande = CA total    True
aucun montant vide            True
aucune commande sans date     True
```
<!--sortie-->

Tous les contrôles passent. Leur valeur apparaît quand quelque chose **casse**. Refaisons, volontairement, la faute de 2.2.5 : joindre les ventes aux produits **sur le nom seul**, puis relancer les contrôles sur la table obtenue.

```python
fautive = ventes.merge(prod[["nom_produit", "cout_achat"]], on="nom_produit", suffixes=("", "_cat"))
print("lignes :", len(ventes), "->", len(fautive), "| CA :", round(ventes["montant"].sum()), "->", round(fautive["montant"].sum()))
print("contrôle « CA par canal = CA total » sur la table fautive : ", bool(controles(fautive)["CA par canal = CA total"]))
```
<!--sortie-->
```text
lignes : 26188 -> 52376 | CA : 1164637 -> 2329273
contrôle « CA par canal = CA total » sur la table fautive :  True
```
<!--sortie-->


Les contrôles de **cohérence interne** (ligne, mois, canal) passent même sur la table fautive : ils comparent la table **à elle-même**, et une jointure qui duplique des lignes duplique aussi ses totaux. Ce que la faute change, c'est la **comparaison à l'extérieur** : le chiffre d'affaires est multiplié par 2,0 (2 329 273 € au lieu de 1 164 637 €), ce que révélerait la comparaison avec la base ou avec le total des fichiers de la caisse. **Il faut donc les deux** : des contrôles internes (les invariants entre niveaux de détail) et des contrôles **externes** (un total qui vient d'ailleurs). C'est ce que le chapitre 3 systématise.

> ✅ **À retenir.**
> - Le **grain** dit ce que représente une ligne ; on **garde la table la plus fine** et l'on en dérive les autres, jamais l'inverse.
> - Un **ratio d'agrégat** se refait à partir des **sommes** ; un **comptage distinct** n'est additif que si les groupes ne se recouvrent pas (clients par mois).
> - `agg` réduit, **`transform`** conserve les lignes : parts, écarts à la moyenne, rangs.
> - Une jointure entre faits et dimension est **n–1** par construction : le nombre de lignes de faits ne doit pas changer ; un calendrier fait voir les **jours manquants**.
> - Un cumul se termine par le **total** ; une moyenne mobile a des vides au début (`min_periods`).
> - On contrôle par **invariants internes** (mêmes totaux à chaque niveau) **et** par une comparaison **externe** : les premiers ne voient pas une jointure qui duplique tout.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.7, exercices 2.9 à 2.10.


## 2.4 ➕ Pour aller plus loin : restructuration, pivot et dépivot

> 🧭 **Section complémentaire.** Elle traite d'un geste que l'on rencontre dès qu'un tableur « fait main » entre dans l'analyse : passer d'une table **large** (un mois par colonne) à une table **longue** (un mois par ligne) et inversement. La gérante tient le stock de la boutique dans un tableur de ce genre ; c'est notre terrain d'essai. Rien de ce qui suit n'est nécessaire à la suite du volume.

Une même information peut s'écrire de deux façons. Le **format large** place chaque valeur d'une variable dans une colonne différente (une colonne par mois) : c'est celui que l'on aime lire, parce que l'œil compare les colonnes, et celui que produisent les tableurs. Le **format long** a **une ligne par observation** et une colonne par variable (une colonne `mois`, une colonne `stock`) : c'est celui que veulent les outils d'analyse, de tracé et de jointure (volume I, section 5.1.4 sur le « tableau propre »). Passer de l'un à l'autre est un **changement de grain**, avec le même contenu.


![Le même contenu en format large (une colonne par mois) et en format long (une ligne par produit et par mois) ; `melt` passe du premier au second, `pivot` fait l'inverse.](figures/ch02-large-long.png)

### 2.4.1 Trois fonctions à connaître

- **`melt`** (en R : `pivot_longer`) **dépivote** : il garde quelques colonnes d'identifiant et transforme **toutes les autres colonnes** en deux colonnes, `variable` et `valeur`. Il ne **calcule** rien.
- **`pivot`** (en R : `pivot_wider`) fait l'inverse, mais **ne sait pas agréger** : si deux lignes ont la même combinaison d'identifiants, il s'arrête.
- **`pivot_table`** pivote **et** agrège (`aggfunc`) : c'est l'équivalent d'un tableau croisé dynamique de tableur, avec des totaux optionnels (`margins=True`).

Reprenons la table des ventes. Un `pivot_table` donne le chiffre d'affaires par canal (en lignes) et par mois (en colonnes), avec les totaux.

```python
large = ventes.pivot_table(index="canal", columns="mois", values="montant", aggfunc="sum", margins=True, margins_name="Total").round(0)
print(large.iloc[:, [0, 1, -2, -1]].to_string())
```
<!--sortie-->
```text
mois      2025-01  2025-02   2025-12      Total
canal                                          
Boutique  39234.0  33079.0   73688.0   564473.0
Site      40221.0  32746.0   87496.0   600164.0
Total     79455.0  65825.0  161184.0  1164637.0
```
<!--sortie-->

On le **redresse** en format long avec `melt` (après avoir retiré la ligne et la colonne de totaux, qui sont des **résumés**, pas des observations), puis on retourne au format large avec `pivot` : si tout va bien, on retombe sur le tableau de départ.

```python
corps = large.drop(columns="Total").drop(index="Total")
long = corps.reset_index().melt(id_vars="canal", var_name="mois", value_name="ca")
retour = long.pivot(index="canal", columns="mois", values="ca")
print(len(long), "lignes en format long | aller-retour identique :", bool(retour.equals(corps)))
print(long.head(3).to_string(index=False))
```
<!--sortie-->
```text
24 lignes en format long | aller-retour identique : True
   canal    mois      ca
Boutique 2025-01 39234.0
    Site 2025-01 40221.0
Boutique 2025-02 33079.0
```
<!--sortie-->


Deux canaux et douze mois donnent 24 lignes en format long : le **nombre de cellules** est conservé, c'est le contrôle de base. Le total du tableau large (1 164 637 €) est celui de la table des ventes, et le passage au format long n'a rien changé. Voyons maintenant ce qui se passe quand `pivot` rencontre deux lignes pour la même case.

```python
try:
    ventes.pivot(index="canal", columns="mois", values="montant")
except ValueError as e:
    print(e)
```
<!--sortie-->
```text
Index contains duplicate entries, cannot reshape
```
<!--sortie-->

Le message est clair : la table des ventes compte des milliers de lignes par couple (canal, mois) ; `pivot` ne sait pas **choisir** laquelle garder, donc il refuse. C'est une **protection** : `pivot_table` accepte, mais **à condition de dire comment agréger** (`aggfunc="sum"`), et l'on est obligé d'y penser. Dans un tableur, un tableau croisé dynamique fait la même chose sans prévenir : il somme par défaut, ce qui est faux si la colonne contient des prix unitaires ou des moyennes.

> 💡 **Intuition.** `melt` et `pivot` **déplacent** de l'information sans la changer (comme tourner un tableau d'un quart de tour) ; `pivot_table` **résume**. Un aller-retour qui ne retombe pas sur ses pieds trahit une clé en double ou une perte de lignes.

### 2.4.2 Le tableur de stocks : lire, nettoyer, dépivoter

Le fichier `stocks_tableur.xlsx` ressemble à ce que l'on trouve dans toutes les entreprises : saisi à la main, lisible pour un humain, **hostile à une machine**. Ouvrons-le sans rien présumer, en lisant les cellules telles quelles avec `openpyxl` (la lecture d'un tableur avec pandas est vue au volume I, chapitre 4).

```python
import openpyxl
ws = openpyxl.load_workbook("donnees/stocks_tableur.xlsx")["Stock 2025"]
brut = pd.DataFrame(list(ws.iter_rows(min_row=5, values_only=True))).iloc[:, :14]
brut.columns = ["ref", "designation"] + list(range(1, 13))
print(brut.iloc[[0, 1, 2, 21, 22]].iloc[:, :6].to_string(index=False))
```
<!--sortie-->
```text
    ref        designation            1            2            3            4
CUISINE                NaN         None         None         None         None
   P001 Casserole nordique           49           41          28           26 
   P002          Poêle mat           11      rupture           10      rupture
    NaN Sous-total Cuisine =SUM(C6:C25) =SUM(D6:D25) =SUM(E6:E25) =SUM(F6:F25)
    NaN                NaN         None         None         None         None
```
<!--sortie-->

On y voit, en quelques lignes, les obstacles : une ligne **de catégorie** (`CUISINE`, cellule fusionnée, seule la première cellule porte la valeur), des lignes **de produits**, une ligne de **sous-total** (dont les cellules contiennent des **formules** ; le fichier n'ayant jamais été recalculé, `openpyxl` donne le texte de la formule et non son résultat), des lignes **vides**, et des **valeurs en texte**. Les lignes de produits se repèrent par un critère **sûr** : la référence suit le motif `P` suivi de trois chiffres. Les autres lignes (catégories, sous-totaux, vides) ne sont pas des observations et sont **écartées** (un sous-total lu comme une donnée ferait compter deux fois le stock). Regardons maintenant ce que contiennent les cellules textuelles.

```python
est_produit = brut["ref"].astype(str).str.fullmatch(r"P\d{3}")
cellules = brut.loc[est_produit].iloc[:, 2:].stack()
textes = cellules[cellules.map(lambda v: isinstance(v, str))].str.strip().str.replace(r"^\d+$", "<nombre>", regex=True)
print(textes.value_counts().to_string())
```
<!--sortie-->
```text
<nombre>    131
rupture     120
ND           49
—            22
```
<!--sortie-->


Sur 1 440 cellules de stock, quatre catégories de **texte** : **131** nombres écrits comme du texte avec un espace en fin (`"28 "`) ; **120** mentions « rupture » ; **49** « ND » (non disponible) ; **22** tirets « — ». Il faut une **décision par catégorie**, et elle est de métier :

- un nombre écrit en texte **est** un nombre : on retire l'espace et l'on convertit ;
- « rupture » signifie **zéro** en stock : c'est une information (on peut compter les ruptures), pas un manquant ;
- « ND » et « — » signifient **inconnu** : on met un **vide** (`NaN`), jamais zéro. Le zéro dirait « en rupture », ce qui est faux et ferait croire à des ruptures qui n'existent pas.

```python
def vers_nombre(v):
    if isinstance(v, (int, float)):
        return v
    s = str(v).strip()
    if s == "rupture":
        return 0
    return int(s) if s.isdigit() else np.nan
produits_stock = brut[est_produit].copy()
mois_cols = list(range(1, 13))
produits_stock[mois_cols] = produits_stock[mois_cols].apply(lambda col: col.map(vers_nombre))
stock = produits_stock.melt(id_vars=["ref", "designation"], var_name="mois", value_name="stock")
stock["id_produit"] = stock["ref"].str[1:].astype(int)
print(len(stock), "lignes | vides :", int(stock["stock"].isna().sum()), "| ruptures :", int((stock["stock"] == 0).sum()))
```
<!--sortie-->
```text
1440 lignes | vides : 71 | ruptures : 120
```
<!--sortie-->

Cent vingt produits et douze mois font **1 440 lignes** en format long, ce que l'on attendait : le nombre de cellules est conservé, aucune n'a été perdue. Comme pour la caisse, on peut maintenant **juger le travail** avec le fichier de vérité, ce qui n'est possible qu'ici.

```python
verite_stock = pd.read_csv("donnees/verite_stocks.csv")
m = stock.merge(verite_stock, on=["id_produit", "mois"], suffixes=("", "_vrai"), validate="1:1")
egal = (m["stock"] == m["stock_vrai"]) | (m["stock"].isna() & m["stock_vrai"].isna())
print("cellules identiques à la vérité :", int(egal.sum()), "sur", len(m))
```
<!--sortie-->
```text
cellules identiques à la vérité : 1440 sur 1440
```
<!--sortie-->


Toutes les 1 440 cellules coïncident avec la vérité, valeurs manquantes comprises. Ce n'est pas un exploit : les règles de lecture étaient simples et **chaque catégorie de cellule avait été examinée avant de convertir**. Le contrôle de fond reste le même que pour la caisse : **compter** (1 440 cellules avant et après), **classer** ce qui est inhabituel, **décider** par catégorie et **documenter**.

> ⚠️ **Piège : `read_excel` qui « devine ».** Avec `pandas.read_excel`, la colonne qui contient des nombres **et** des mentions comme « rupture » serait lue en texte, ou convertie avec des surprises. Lire les cellules **brutes**, puis décider, est plus long mais ne laisse rien au hasard.

### 2.4.3 Joindre deux tables du même grain

Les stocks sont mensuels, par produit. Pour savoir **combien de mois de ventes** couvre un stock, il faut les rapprocher des ventes, qui sont au grain de la ligne de vente. Si l'on joignait telles quelles, chaque ligne de stock serait associée à **toutes** les lignes de vente du produit et du mois : une jointure 1–n qui multiplierait le stock. La bonne méthode est de **ramener d'abord les ventes au grain du stock** (produit × mois), puis de joindre deux tables dont la clé est unique des deux côtés.

```python
q = ventes.dropna(subset=["id_produit"]).assign(mois=lambda d: d["date"].dt.month, id_produit=lambda d: d["id_produit"].astype(int))
unites = q.groupby(["id_produit", "mois"], as_index=False)["quantite"].sum().rename(columns={"quantite": "vendu"})
couv = stock.dropna(subset=["stock"]).merge(unites, on=["id_produit", "mois"], how="left", validate="1:1")
couv["vendu"] = couv["vendu"].fillna(0)
couv["stock_inferieur_aux_ventes"] = couv["stock"] < couv["vendu"]
print(len(couv), "lignes produit-mois | stock < ventes du mois :", int(couv["stock_inferieur_aux_ventes"].sum()))
```
<!--sortie-->
```text
1369 lignes produit-mois | stock < ventes du mois : 392
```
<!--sortie-->


Sur 1 369 couples (produit, mois) dont le stock est connu, **29 %** (392) ont un stock de fin de mois **inférieur** aux ventes du mois : c'est la couverture inférieure à un mois, un signal de réassort à surveiller. Remarquez aussi que, parmi les 120 couples en rupture, 100 % ont **des ventes dans le mois** : une rupture de **fin** de mois n'interdit pas d'avoir vendu avant, et il ne faut pas confondre les deux.

> ⚠️ **Ce que ce calcul ne prouve pas.** Dans nos données, les stocks et les ventes ont été **simulés indépendamment l'un de l'autre** : la couverture calculée ici montre la **mécanique** de la jointure (même grain, clé unique, vides conservés), pas une réalité de la boutique. Dans de vraies données, on s'attendrait à ce qu'un produit en rupture vende moins le mois suivant : on le **vérifierait**, on ne le supposerait pas.

Deux précautions de méthode s'imposent : les ventes de la caisse dont le produit est ambigu (la paire de produits indiscernables de 2.2.5) ont été **écartées** de ce calcul, donc les ventes de ces deux produits sont **sous-estimées** ; et les stocks « inconnus » sont **exclus** plutôt que traités comme zéro.

### 2.4.4 Le même geste dans les autres outils

Dans **DuckDB**, `UNPIVOT` fait ce que fait `melt` ; on vérifie qu'il donne le même nombre de lignes.

```python
con2 = duckdb.connect(); con2.register("stock_large", produits_stock.rename(columns=str))
n_sql = con2.sql("select count(*) from (unpivot stock_large on columns(* exclude (ref, designation)) into name mois value stock)").fetchone()[0]
print("lignes après UNPIVOT en SQL :", n_sql)
```
<!--sortie-->
```text
lignes après UNPIVOT en SQL : 1369
```
<!--sortie-->

Dans **Power Query** (Excel), la même opération s'appelle « dépivoter les autres colonnes » ; on la lit dans le langage M de l'éditeur avancé. Ce qui suit n'est **pas exécuté** ici (Power Query n'est pas disponible sur la machine qui a produit ce livre) ; le résultat attendu est celui que pandas vient de donner : 1 440 lignes. Les noms des étapes et des fonctions sont à vérifier dans la documentation de votre version.

```python
// Power Query (langage M), non exécuté
let
    Source   = Excel.Workbook(File.Contents("stocks_tableur.xlsx"), null, true),
    Feuille  = Source{[Item = "Stock 2025", Kind = "Sheet"]}[Data],
    Entetes  = Table.PromoteHeaders(Table.Skip(Feuille, 3)),
    Produits = Table.SelectRows(Entetes, each Text.StartsWith([#"Réf."], "P")),
    Long     = Table.UnpivotOtherColumns(Produits, {"Réf.", "Désignation"}, "Mois", "Stock")
in
    Long
```

En R, ce serait `pivot_longer(cols = -c(ref, designation), names_to = "mois", values_to = "stock")`, après `filter(grepl("^P[0-9]{3}$", ref))`.

> ✅ **À retenir.**
> - **Large** pour lire, **long** pour calculer, tracer et joindre ; `melt` et `pivot` déplacent sans modifier, `pivot_table` **résume**.
> - Un **aller-retour** large → long → large qui ne retombe pas sur ses pieds trahit un doublon ou une perte ; le **nombre de cellules** est conservé.
> - Un tableur « fait main » se lit en **cellules brutes** : repérer les lignes utiles par un motif sûr, écarter titres et sous-totaux, **classer** les valeurs textuelles et décider **par catégorie** (nombre, zéro, inconnu).
> - **« Inconnu » n'est pas zéro** : un `NaN` dit « on ne sait pas », un zéro dit « rupture ».
> - Avant de joindre, on ramène les deux tables au **même grain** (produit × mois), clé unique des deux côtés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercices 2.11 à 2.12.


## 2.5 ➕ Pour aller plus loin : appariement approximatif et rapprochement d'enregistrements

> 🧭 **Section complémentaire.** Elle traite d'un problème qui fait suite à tout ce qui précède : **relier deux enregistrements qui désignent la même chose sans être écrits de la même façon**. La gérante a un fichier clients (le CRM) où **les mêmes personnes apparaissent plusieurs fois**, et un catalogue de fournisseur qui nomme ses produits à sa manière. Rien de ce qui suit n'est nécessaire à la suite du volume ; le chapitre 3 reprend la **réconciliation** de sources avec ses seuils et ses rapports d'exceptions.

Jusqu'ici, nous avons joint des tables par des clés **exactes** : un numéro de produit, une référence de commande. Mais beaucoup de données n'ont **pas de clé commune**. Le CRM a enregistré la même cliente trois fois, une fois en majuscules, une fois sans accent, une fois avec une faute de frappe ; le fournisseur écrit « CASSEROLE NORDIQUE » là où la boutique écrit « Casserole nordique ». On parle de **rapprochement d'enregistrements** (*record linkage*) ou de **dédoublonnage** (*deduplication*) quand les deux fichiers sont le même. La méthode combine quatre idées : **normaliser**, **mesurer une ressemblance**, **limiter les comparaisons** (le *blocage*) et **décider** avec un seuil.

### 2.5.1 Pourquoi les clés exactes échouent

Le CRM contient 7 000 lignes une fois retirées les 140 lignes de test, pour 6 000 clients distincts : près de **mille lignes sont des doublons**. Pour **juger** les méthodes de cette section, nous avons besoin de savoir quelles lignes désignent la même personne. Dans la vie réelle, on étiquette à la main un **échantillon** et l'on évalue sur lui ; ici, le fichier de vérité nous donne **toutes** les paires, ce qui permet de mesurer exactement. Une **paire vraie** est un couple de lignes du CRM qui désignent le même client.

```python
import itertools
crm = pd.read_csv("donnees/crm_clients.csv", dtype=str, keep_default_na=False)
n_total = len(crm)
crm = crm[crm["email"] != "test@example.com"].copy()
crm["id_crm"] = crm["id_crm"].astype(int)
verite_crm = pd.read_csv("donnees/verite_crm.csv")
groupes = crm.merge(verite_crm[["id_crm", "id_client"]], on="id_crm").groupby("id_client")["id_crm"].apply(sorted)
vraies = {p for g in groupes for p in itertools.combinations(g, 2)}
print(len(crm), "lignes |", len(vraies), "paires de lignes qui désignent le même client")
```
<!--sortie-->
```text
7000 lignes | 1050 paires de lignes qui désignent le même client
```
<!--sortie-->


Il y a donc 1 050 paires vraies à retrouver. Les deux fonctions suivantes sont l'outil de mesure de toute la section : `paires` construit toutes les paires de lignes qui partagent une valeur de clé, et `juger` compare cet ensemble aux paires vraies. Deux mesures s'y lisent : la **précision** (parmi les paires proposées, quelle part est vraie ?) et le **rappel** (parmi les paires vraies, quelle part a été trouvée ?).

```python
def paires(df, cles):
    sortie = set()
    for _, g in df.dropna(subset=cles).groupby(cles)["id_crm"]:
        ids = sorted(g)
        if 1 < len(ids) < 100:
            sortie.update(itertools.combinations(ids, 2))
    return sortie
def juger(trouvees):
    ok = len(trouvees & vraies)
    return {"paires": len(trouvees), "précision": round(ok / max(1, len(trouvees)), 3), "rappel": round(ok / len(vraies), 3)}
```

Essayons trois clés **exactes**, sur le texte tel quel : l'adresse électronique, le téléphone, le couple prénom et nom.

```python
crm["mail_brut"] = crm["email"].replace("", np.nan)
crm["nom_brut"] = crm["prenom"] + "|" + crm["nom"]
for cle in ["mail_brut", "telephone", "nom_brut"]:
    print(f"{cle:10s}", juger(paires(crm, [cle])))
```
<!--sortie-->
```text
mail_brut  {'paires': 425, 'précision': 0.993, 'rappel': 0.402}
telephone  {'paires': 211, 'précision': 1.0, 'rappel': 0.201}
nom_brut   {'paires': 192, 'précision': 0.979, 'rappel': 0.179}
```
<!--sortie-->


Les clés exactes sont **très précises** (presque toutes les paires proposées sont vraies : 99,3 % pour l'e-mail) mais leur **rappel est mauvais** : 40 % des paires vraies pour l'e-mail, 20 % pour le téléphone, 18 % pour le nom. L'égalité stricte rate tout ce qui est écrit **un peu** différemment. C'est la première leçon : une clé exacte donne peu de **faux positifs**, beaucoup de **faux négatifs**.

### 2.5.2 Normaliser d'abord

La première amélioration est la moins glorieuse et la plus rentable : **ramener chaque champ à une forme canonique** avant de comparer. Pour le texte, nous avons déjà `cle_texte` (2.1.6). Il faut y ajouter quelques particularités du fichier : le **mojibake** (un texte UTF-8 lu avec le mauvais codage, `SorbertÃ©` au lieu de `Sorberté`), que la bibliothèque `ftfy` répare ; les **villes** écrites de six façons dont l'une **en arabe** (`المدينة أ` signifie « la ville A ») ; le **téléphone**, que l'on réduit aux neuf derniers chiffres (les préfixes et séparateurs varient) ; l'**année de naissance**, extraite d'une date écrite en quatre formats (et ignorée si elle est impossible).

```python
import ftfy
LETTRES = "أبتثجحخدذرزسشصضطظعغف"
def ville_cle(s):
    s = s.strip()
    if s.startswith("المدينة"):
        return "ville " + chr(97 + LETTRES.index(s.split()[-1]))
    return re.sub(r"^vile", "ville", cle_texte(s))
crm["mail_norm"] = crm["email"].str.strip().str.lower().replace("", np.nan)
crm["tel_norm"] = crm["telephone"].str.replace(r"\D", "", regex=True).str[-9:]
crm["nom_complet"] = (crm["prenom"] + " " + crm["nom"]).map(lambda s: cle_texte(ftfy.fix_text(s)))
crm["nom_tri"] = crm["nom_complet"].str.split().map(lambda t: " ".join(sorted(t)))
crm["ville_norm"] = crm["ville"].map(ville_cle)
crm["annee_naiss"] = pd.to_numeric(crm["date_naissance"].str.extract(r"(\d{4})")[0]).where(lambda a: a.between(1920, 2010))
print("villes distinctes :", crm["ville"].nunique(), "->", crm["ville_norm"].nunique(), "| années de naissance utilisables :", int(crm["annee_naiss"].notna().sum()))
```
<!--sortie-->
```text
villes distinctes : 119 -> 20 | années de naissance utilisables : 6960
```
<!--sortie-->


Les 119 écritures de villes se ramènent à 20 villes, celles du fichier ; 99,4 % des lignes ont une année de naissance utilisable. Voyons l'effet sur les clés exactes.

```python
for cle in ["mail_norm", "tel_norm"]:
    print(f"{cle:10s}", juger(paires(crm, [cle])))
```
<!--sortie-->
```text
mail_norm  {'paires': 698, 'précision': 0.994, 'rappel': 0.661}
tel_norm   {'paires': 1050, 'précision': 1.0, 'rappel': 1.0}
```
<!--sortie-->

Le gain est spectaculaire pour le téléphone : une fois réduit à neuf chiffres, il retrouve **100 %** des paires vraies avec une précision de 100 %, alors que l'e-mail normalisé n'en retrouve que 66 % (les lignes dont l'e-mail est absent, ou mal écrit, lui échappent). Voilà un cas où la **normalisation suffit** et où l'appariement approximatif serait superflu : c'est même la première chose à essayer. Notre téléphone a été fabriqué intact (il n'a subi que des changements de **forme**) ; **dans la vie réelle, un numéro change, manque ou est partagé par un foyer**, et l'on ne s'y fie pas à lui seul.

Pour apprendre la méthode générale, plaçons-nous donc dans un cas **fréquent** : le téléphone n'est **pas disponible** (le fichier que l'on rapproche n'en contient pas, ou la minimisation des données l'interdit : chapitre 5). Il ne reste que le nom, l'e-mail, la ville et l'année de naissance, et il faut une **mesure de ressemblance**. Le numéro de téléphone nous servira de **second avis indépendant** pour contrôler le résultat (2.5.5).

### 2.5.3 Mesurer une ressemblance

Deux textes **se ressemblent** s'il faut peu de modifications pour passer de l'un à l'autre. La mesure de base est la **distance de Levenshtein** : le nombre minimal d'opérations élémentaires (insérer, supprimer ou remplacer **une lettre**) pour transformer un mot en l'autre. On la calcule par une petite table : la case `(i, j)` contient la distance entre les `i` premières lettres du premier mot et les `j` premières du second, avec la règle

$$d(i,j)=\min\big(d(i-1,j)+1,\;d(i,j-1)+1,\;d(i-1,j-1)+c\big),\qquad c=\begin{cases}0&\text{si les lettres sont égales}\\1&\text{sinon.}\end{cases}$$

Prenons deux écritures d'un nom inventé, `tavel` et `tavle` (deux lettres permutées).

```text
   ∅  t  a  v  l  e
∅  0  1  2  3  4  5
t  1  0  1  2  3  4
a  2  1  0  1  2  3
v  3  2  1  0  1  2
e  4  3  2  1  1  1
l  5  4  3  2  1  2
```
<!--sortie-->


La dernière case donne la distance : 2. Permuter deux lettres coûte **deux** opérations (deux remplacements), alors qu'un humain y voit **une** seule faute de frappe : certaines variantes de la distance (Damerau-Levenshtein) comptent la permutation pour un. On transforme la distance en **similarité** entre 0 et 100 en la rapportant à la longueur : similarité = 100 × (1 − distance / longueur maximale).

Trois autres mesures complètent la boîte à outils, car aucune ne convient à tout :

- la similarité de **Jaro-Winkler** : pense aux **fautes de frappe dans un nom** ; elle récompense les **lettres communes à peu près au même endroit** et donne un **bonus aux débuts identiques** (une faute au milieu d'un nom coûte moins qu'une au début) ;
- le **`token_set_ratio`** de `rapidfuzz` : compare des **ensembles de mots**, **sans tenir compte de l'ordre** ni des mots en plus : adapté aux noms inversés et aux désignations qui ajoutent un mot ;
- la comparaison d'**initiales** : « M. Dormar » désigne probablement « Mirelo Dormar ».

```python
from rapidfuzz import fuzz
import jellyfish
cas = [("mirelo dormar", "mirelo dormra"), ("mirelo dormar", "dormar mirelo"), ("mirelo dormar", "m dormar"), ("mirelo dormar", "talina kelmar")]
tab = pd.DataFrame([(x, y, round(fuzz.ratio(x, y)), round(jellyfish.jaro_winkler_similarity(x, y) * 100), round(fuzz.token_set_ratio(x, y))) for x, y in cas],
                   columns=["texte 1", "texte 2", "ratio", "jaro-winkler", "token_set"])
print(tab.to_string(index=False))
```
<!--sortie-->
```text
      texte 1       texte 2  ratio  jaro-winkler  token_set
mirelo dormar mirelo dormra     92            98         92
mirelo dormar dormar mirelo     46            62        100
mirelo dormar      m dormar     76            77         86
mirelo dormar talina kelmar     46            55         38
```
<!--sortie-->


Le tableau montre pourquoi on choisit la mesure **selon le défaut que l'on attend** : une faute de frappe garde une similarité élevée avec toutes les mesures (92 pour le simple ratio) ; l'**inversion** du nom et du prénom est invisible pour le ratio (46) mais **parfaite** pour `token_set_ratio` (100) ; l'initiale donne 86, un peu moins ; deux personnes différentes sont à 38. Pour nos données, où les défauts sont de ces quatre sortes, nous prendrons `token_set_ratio` sur les mots **triés** du nom.

### 2.5.4 Limiter les comparaisons : le blocage

Comparer toutes les lignes du CRM deux à deux est impossible à grande échelle : pour 7 000 lignes, il y a **24 496 500 paires**. Même à un millier de comparaisons par seconde, c'est une journée entière. Le **blocage** consiste à ne comparer que des paires **plausibles** : celles qui partagent une valeur **grossière** et **fiable** (une clé de blocage). Ici, la **ville normalisée** et l'**année de naissance** : deux lignes qui désignent la même personne ont presque toujours ces deux valeurs identiques.

```python
bloc = paires(crm, ["ville_norm", "annee_naiss"])
n_paires = len(crm) * (len(crm) - 1) // 2
print("paires à comparer :", len(bloc), "sur", n_paires, "| part gardée :", round(len(bloc) / n_paires * 100, 2), "%")
print("blocage :", juger(bloc))
```
<!--sortie-->
```text
paires à comparer : 42538 sur 24496500 | part gardée : 0.17 %
blocage : {'paires': 42538, 'précision': 0.024, 'rappel': 0.984}
```
<!--sortie-->


Le blocage réduit le nombre de comparaisons de **576 fois** : de 24 496 500 à 42 538 paires (0,17 % du total). Il y a un prix : le **rappel** du blocage, 98,4 %, est une **limite supérieure** de tout ce qui suivra ; une paire vraie qui ne partage ni ville ni année de naissance n'est jamais comparée (par exemple si l'année est absente ou impossible). Le choix de la clé est un arbitrage entre vitesse et rappel ; on le **mesure**, on ne le devine pas. Dans la pratique, on fait souvent **plusieurs passes** avec des clés de blocage différentes (ville et année ; puis e-mail ; puis premières lettres du nom) et l'on réunit les paires trouvées.

### 2.5.5 Un score, trois zones

Pour chaque paire du blocage, on calcule un **score** qui combine les indices disponibles : la ressemblance des noms (pondérée 60 %) et celle de la partie locale de l'e-mail, avant le `@` (40 %), quand les deux e-mails sont présents. Si l'un des deux manque, on ne peut s'appuyer que sur le nom, et l'on **pénalise** légèrement le score (90 % de la similarité du nom) : moins d'indices, moins de certitude. Ces poids sont des **choix**, que l'on réglera sur les résultats.

```python
rec = crm.set_index("id_crm")[["nom_tri", "mail_norm"]].to_dict("index")
def local(m): return m.split("@")[0] if isinstance(m, str) else None
def score_paire(a, b):
    nom = fuzz.token_set_ratio(rec[a]["nom_tri"], rec[b]["nom_tri"])
    lx, ly = local(rec[a]["mail_norm"]), local(rec[b]["mail_norm"])
    if lx is None or ly is None:
        return nom, np.nan, 0.9 * nom
    mail = fuzz.ratio(lx, ly)
    return nom, mail, 0.6 * nom + 0.4 * mail
S = pd.DataFrame([(a, b, *score_paire(a, b)) for a, b in sorted(bloc)], columns=["a", "b", "nom", "mail", "score"])
S["vrai"] = [(a, b) in vraies for a, b in zip(S["a"], S["b"])]
print(S.groupby("vrai")["score"].describe()[["count", "mean", "min", "50%", "max"]].round(1).to_string())
```
<!--sortie-->
```text
         count  mean   min   50%    max
vrai                                   
False  41505.0  36.5   6.9  35.7   92.9
True    1033.0  95.3  60.0  97.9  100.0
```
<!--sortie-->


Les deux populations sont **bien séparées** : les paires vraies ont un score médian de 98 et une moyenne de 95 ; les fausses paires (deux personnes différentes de la même ville et de la même année de naissance) ont une moyenne de 36. Elles se **chevauchent** pourtant dans une zone intermédiaire : la pire fausse paire atteint 93, la moins bonne paire vraie 60. C'est ce chevauchement qui rend inévitable une décision **à trois zones** plutôt qu'à deux : **accepter** automatiquement au-dessus d'un seuil haut, **rejeter** en dessous d'un seuil bas, et envoyer la **zone grise** à une **revue manuelle**.


![À gauche, distribution du score des paires comparées après blocage (échelle logarithmique) : les fausses paires sont des dizaines de milliers, avec des scores faibles ; les paires vraies forment un petit groupe à score élevé. À droite, précision et rappel en fonction du seuil. Les traits marquent les seuils 70 et 85.](figures/ch02-scores-appariement.png)

Choisissons deux seuils : **85** pour l'acceptation automatique et **70** pour la limite basse de la revue manuelle. On compte ce que produit chaque zone, et l'on juge par rapport aux paires vraies.

```python
auto = S[S["score"] >= 85]
grise = S[(S["score"] >= 70) & (S["score"] < 85)]
print("acceptées :", len(auto), "| précision :", round(auto["vrai"].mean(), 3), "| rappel global :", round(auto["vrai"].sum() / len(vraies), 3))
print("à revoir  :", len(grise), "| part de vraies paires :", round(grise["vrai"].mean(), 3))
print("rappel si la revue manuelle tranche juste :", round((auto["vrai"].sum() + grise["vrai"].sum()) / len(vraies), 3))
```
<!--sortie-->
```text
acceptées : 975 | précision : 0.998 | rappel global : 0.927
à revoir  : 136 | part de vraies paires : 0.397
rappel si la revue manuelle tranche juste : 0.978
```
<!--sortie-->


La zone **automatique** ne propose que 975 paires, dont **99,8 %** sont vraies (seulement 2 fausses) : on peut fusionner sans relire. Elle retrouve 93 % des paires vraies. La **zone grise** compte 136 paires dont 54 sont vraies et 82 fausses : à la limite du jugement humain, et c'est justement pour cela qu'on les **soumet à un humain** plutôt qu'à un seuil. Si la revue manuelle tranche juste, le rappel monte à 98 % : le reste est hors de portée du blocage.

Dans la vie réelle, on ne dispose pas des paires vraies. Mais on peut **auditer** avec un **second indice indépendant**, ici le téléphone que nous avons gardé de côté : parmi les paires acceptées, combien partagent aussi le même numéro ?

```python
tel = crm.set_index("id_crm")["tel_norm"]
S["meme_tel"] = [tel[a] == tel[b] for a, b in zip(S["a"], S["b"])]
print(pd.crosstab(S["score"] >= 80, S["meme_tel"], rownames=["score ≥ 80"], colnames=["même téléphone"]).to_string())
```
<!--sortie-->
```text
même téléphone  False  True 
score ≥ 80                  
False           41496     39
True                9    994
```
<!--sortie-->


Parmi les paires au score d'au moins 80, **994 sur 1003** partagent le même numéro (99,1 %), alors que seulement 39 paires de **plus bas** score le partagent aussi. Les deux avis **concordent** presque toujours, ce qui renforce la confiance sans jamais la prouver : c'est ce que l'on appelle une **validation croisée par un indice indépendant**.

> 💡 **Intuition.** Un score d'appariement n'est **pas une probabilité** : un 85 ne veut pas dire « 85 % de chances d'être le même client ». C'est un **classement** des paires, de la plus probable à la moins probable. Le **seuil** transforme ce classement en décision, et c'est **la décision, pas le score, qu'il faut mesurer** (précision, rappel, charge de revue).

### 2.5.6 Le coût des erreurs décide du seuil

Un seuil n'est ni bon ni mauvais : il dépend de **ce que coûte chaque erreur**. Deux erreurs sont possibles : fusionner deux personnes **différentes** (un **faux positif** : on mélange deux historiques d'achats, on écrit à quelqu'un sous le nom d'un autre) et **rater** un doublon (un **faux négatif** : la même personne est comptée deux fois, reçoit deux courriers). Leur gravité n'est pas la même, et elle dépend de l'usage. Calculons le **coût total** pour trois hypothèses de coût, en balayant le seuil (le calcul, une simple somme de faux positifs et de faux négatifs pondérés, est refait dans l'exercice 2.14 du cahier).

```text
coûts égaux                         seuil optimal : 75 (coût 55)
fusion erronée 10 fois plus grave   seuil optimal : 85 (coût 97)
doublon raté 10 fois plus grave     seuil optimal : 75 (coût 262)
```
<!--sortie-->


Avec des coûts égaux, le seuil optimal est **75** ; quand une **fusion erronée est dix fois plus grave** qu'un doublon raté (par exemple parce que la fusion supprime l'historique), il monte à **85** : on accepte moins, on laisse plus de doublons ; quand c'est un **doublon raté qui est dix fois plus grave** (envoi en double d'un courrier coûteux), il est de **75** (sur une grille de seuils de cinq en cinq : un balayage plus fin déplacerait un peu ces optimums). La conclusion pratique : **on ne choisit pas un seuil « en soi »**, on le choisit **avec la personne qui supporte les conséquences**, et l'on **écrit** pourquoi.

Dernière règle, la plus importante : **ne jamais écraser les données d'origine**. On ne fusionne pas en supprimant des lignes : on construit une **table de correspondance** (`id_crm` → `id_client_unique`) avec le score et la décision, que l'on peut relire, corriger et **annuler**. Une fusion erronée sans trace est irréparable ; une fusion tracée se défait en une ligne.

### 2.5.7 Rapprocher le catalogue du fournisseur

Le même raisonnement s'applique au catalogue du fournisseur : relier chacune de ses lignes au produit correspondant de la boutique. Ici l'information la plus fiable n'est pas dans le texte : c'est le **prix d'achat** (à quelques pour cent près). Pour chaque ligne du catalogue, on cherche, **dans la même famille de produits**, le produit dont le nom ressemble le plus et dont le coût d'achat est proche, en combinant les deux indices : on retranche à la similarité de nom une **pénalité proportionnelle à l'écart de prix**. Le code (une boucle sur les lignes du catalogue, une similarité de nom par candidat, un écart de prix par candidat) est rangé dans `build/outils_ch02.py` et refait pas à pas dans le cahier (application 2.10) ; seul son résultat nous intéresse ici.

```text
lignes du catalogue : 118 | acceptées : 108 | rejetées : 10
```
<!--sortie-->

On accepte un appariement si la similarité de nom est d'**au moins 70** **et** si l'écart de prix ne dépasse pas **3,5 %** (le catalogue a été fabriqué avec ±3 % d'écart sur le coût d'achat : le seuil a été choisi **avec** cette information, comme on choisit une tolérance avec le fournisseur). Jugeons le résultat avec la vérité.

```python
vp = pd.read_csv("donnees/verite_produits.csv").rename(columns={"id_produit": "id_vrai"})
J = R.merge(vp, on="code_fournisseur", validate="1:1")
vrais_produits = J[J["id_vrai"] != -1]
print("produits du catalogue qui existent à la boutique :", len(vrais_produits), "| nouveautés :", int((J["id_vrai"] == -1).sum()))
print("nouveautés correctement rejetées :", int((~J.loc[J["id_vrai"] == -1, "accepte"]).sum()))
print("bons appariements avec le nom et le prix :", int((vrais_produits["id_produit"] == vrais_produits["id_vrai"]).sum()), "| avec le nom seul :", int((vrais_produits["id_nom_seul"] == vrais_produits["id_vrai"]).sum()))
```
<!--sortie-->
```text
produits du catalogue qui existent à la boutique : 108 | nouveautés : 10
nouveautés correctement rejetées : 10
bons appariements avec le nom et le prix : 107 | avec le nom seul : 58
```
<!--sortie-->


Les 108 lignes acceptées sont exactement les 108 produits qui existent à la boutique ; les 10 **nouveautés** du fournisseur (qui n'ont aucun équivalent) sont toutes **rejetées** (10 sur 10) : aucun faux appariement. Le prix a fait la différence : avec le **nom seul**, seuls 58 appariements sur 108 (54 %) sont bons, parce que chaque nom est porté par deux produits ; avec le **nom et le prix**, 107 sur 108 (99 %). Le seul échec (1 ligne) est le produit 62 apparié à la place du 72 : **les deux produits sont indiscernables** (même nom, même coût d'achat), comme nous l'avions vu en 2.2.5. Aucune méthode, humaine ou automatique, ne pourrait trancher sans une information de plus (un numéro d'article, une date d'entrée au catalogue). **Savoir qu'on ne peut pas décider est un résultat.**

> ✅ **À retenir.**
> - Une clé **exacte** a une bonne précision et un mauvais rappel ; **normaliser** (casse, accents, espaces, mojibake, chiffres seuls) est le premier gain, souvent suffisant.
> - Une **ressemblance** se mesure par une distance (Levenshtein), une similarité (Jaro-Winkler) ou une comparaison d'**ensembles de mots** (`token_set_ratio`) : on choisit selon le **défaut attendu** (faute, inversion, initiale).
> - Le **blocage** réduit les comparaisons de plusieurs ordres de grandeur ; son rappel borne celui de tout le reste.
> - On décide à **trois zones** : accepter, **revue manuelle**, rejeter ; le seuil se choisit selon le **coût des deux erreurs**, avec ceux qui en supportent les conséquences.
> - Un score n'est pas une probabilité ; on mesure la **décision** (précision, rappel) et l'on **audite** avec un indice indépendant.
> - On **ne supprime pas** : on garde une table de correspondance tracée. Et quand deux objets sont **indiscernables**, on l'écrit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.9 et 2.10, exercices 2.13 et 2.14.


## Bilan du chapitre 2

Vous savez maintenant :

- **créer des variables dérivées** en connaissant les décisions qu'elles cachent : une **marge** (hors taxe, après remise, rapport de sommes), des **morceaux de date** (en gardant l'année ISO avec la semaine ISO), des **classes** (`cut`, `qcut`, bornes écrites), des **indicateurs** et des **délais** entre lignes (trier, regrouper, décaler), des **clés de texte** normalisées ; et les **documenter** par une fiche ;
- repérer les trois pièges des variables dérivées : la **division par zéro**, le **`NaN` qui se propage** (`sum` ignore, `+` propage) et la **fuite d'information** (un calcul qui utilise le futur) ;
- **joindre** des tables en choisissant le **type** de jointure, en déclarant la **cardinalité** (`validate=`), en appliquant les **quatre contrôles** (lignes, somme, lignes sans correspondance, unicité de la clé) et en reconnaissant la jointure **n–n** qui multiplie les lignes (un nom n'est jamais une clé) ;
- **empiler** douze fichiers dont le **format dérive** (codage, séparateur, décimale, noms de colonnes, date), en **détectant** le format de chacun et en utilisant la **ligne de total** comme somme de contrôle ;
- lire un **export** comme un document : statuts et devises en plusieurs écritures, **changement d'unité** (centimes) repéré par l'ordre de grandeur et confirmé par une autre source, commandes de **test**, **doublons** et **annulations** retirés en comptant ;
- **harmoniser** deux sources en une **table de ventes** au schéma commun, **la contrôler** contre une référence indépendante et **expliquer chaque écart** ; **chercher ce qui manque** par des anti-jointures (un canal entier absent des sources) ;
- **agréger** en raisonnant sur le **grain** : agrégats nommés, `transform` pour les parts et les rangs, comptages distincts **non additifs**, cumuls et moyennes mobiles, schéma **en étoile** (faits et dimensions), et **contrôler par invariants** internes **et** par une comparaison externe ;
- (en option) **passer du format large au format long** (`melt`, `pivot`, `pivot_table`), lire un **tableur saisi à la main** et décider par catégorie de cellule (nombre, zéro, inconnu), joindre deux tables **du même grain** ;
- (en option) **rapprocher des enregistrements sans clé commune** : normaliser, mesurer une ressemblance, **bloquer**, noter, décider à **trois zones** selon le **coût des erreurs**, auditer par un indice indépendant, et ne jamais écraser les données d'origine.

Le chapitre a mis des chiffres sur des idées que l'on retient souvent comme des conseils :

| Ce que l'on a vu | Ce que l'on a mesuré |
|---|---|
| Fichiers de la caisse lus sans reconstitution | 13 077 € de moins que le total affiché en pied de fichier |
| Après reconstitution des montants vides | 3 499 € de plus (0,62 %) : les lignes identiques |
| Jointure sur le nom seul | de 12 678 à 25 356 lignes, chiffre d'affaires doublé |
| Montants du site | médiane de 87 € en août, 8 426 € en octobre : changement d'unité |
| Canal absent des deux sources | 11 % du chiffre d'affaires de l'année |
| Comptage de clients mois par mois, sommé | 2,7 fois le nombre réel de clients |
| Clés exactes sur le CRM, e-mail brut | 40 % des doublons retrouvés ; téléphone normalisé : 100 % |
| Blocage (ville, année de naissance) | 576 fois moins de comparaisons pour 98 % des paires vraies conservées |
| Catalogue : nom seul contre nom et prix | 54 % contre 99 % de bons appariements |

Trois leçons dépassent ce chapitre. **D'abord, aucune erreur ne s'affiche** : une jointure qui double les lignes, une décimale mal lue, une unité qui change, un comptage non additif donnent des chiffres plausibles ; seules la comparaison **avant et après**, la **somme de contrôle** et la **référence extérieure** les révèlent. **Ensuite, ne rien supprimer sans preuve** : on garde, on marque, on documente l'incertitude résiduelle, car deux lignes identiques peuvent être légitimes et deux noms identiques peuvent désigner deux choses. **Enfin, chaque correction est une décision de métier** (que faire d'un montant vide, d'un « ND », d'une fusion douteuse) : on l'écrit, on la mesure et on la fait valider par celui qui en supporte les conséquences.

> 🧭 **En pratique : la liste de contrôle d'une préparation.**
> 1. Compter les lignes **avant et après** chaque opération (jointure, empilement, filtre) et expliquer l'écart.
> 2. Comparer un **total** avec une source **indépendante** (ligne de total, base, autre outil).
> 3. Déclarer la **cardinalité** de chaque jointure (`validate=`) et vérifier l'**unicité** des clés.
> 4. **Détecter** le format de chaque source (codage, séparateur, décimale, unité) plutôt que le deviner.
> 5. Ne jamais traiter « inconnu » comme « zéro » ; marquer les valeurs reconstituées.
> 6. Garder la table **la plus fine** et en dériver les agrégats ; rappeler le **grain** de chaque table.
> 7. **Documenter** chaque variable créée et chaque décision (chapitre 4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.10 (variables dérivées, délais et fuite d'information, contrôle d'une jointure, lecture de la caisse, nettoyage du site, table des ventes, agrégation et contrôles, stocks, dédoublonnage du CRM, catalogue du fournisseur) et exercices 2.1 à 2.14.

Le chapitre 3 fait de ces contrôles une démarche : les **dimensions de la qualité** (exactitude, complétude, cohérence, actualité), les **contrôles de validation** que l'on écrit une fois pour toutes, et la **réconciliation** de sources, avec ses seuils de tolérance et ses rapports d'exceptions.

