## 1.2 Schéma en étoile

Le schéma en **étoile** est la forme que prennent presque tous les entrepôts pour l'analyse. L'idée est simple : au centre, **ce que l'on mesure** (des ventes) ; autour, **les points de vue** selon lesquels on veut le regarder (par date, par client, par produit). Cette section le construit pour la boutique, **en SQL**, l'interroge, et le **vérifie** contre la comptabilité.

```python hide
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as O
```

### 1.2.1 Une table de faits au centre, des dimensions autour

Prenons six lignes de vente, telles qu'on les trouverait dans un classeur à plat :

| ligne | date | client | ville | produit | catégorie | montant |
|---|---|---|---|---|---|---|
| 1 | 3 janv. | Cl. 17 | Ville B | Bol design | Cuisine | 19,90 |
| 2 | 3 janv. | Cl. 17 | Ville B | Plaid doux | Maison | 45,00 |
| 3 | 3 janv. | Cl. 52 | Ville A | Bol design | Cuisine | 19,90 |
| 4 | 4 janv. | Cl. 17 | Ville B | Bol design | Cuisine | 19,90 |
| 5 | 4 janv. | Cl. 80 | Ville A | Plaid doux | Maison | 45,00 |
| 6 | 5 janv. | Cl. 52 | Ville A | Plaid doux | Maison | 45,00 |

Trois colonnes (`ville`, `produit`, `catégorie`) **répètent** des descriptions. Si une catégorie est renommée, il faudrait corriger vingt mille lignes. On sépare donc **ce qui est mesuré** de **ce qui décrit** :

| **fait_ventes** | date_key | client_key | produit_key | montant |
|---|---|---|---|---|
| 1 | 20250103 | 17 | 1 | 19,90 |
| 2 | 20250103 | 17 | 2 | 45,00 |
| 3 | 20250103 | 52 | 1 | 19,90 |
| … | … | … | … | … |

| **dim_produit** | produit_key | nom | catégorie |
|---|---|---|---|
| | 1 | Bol design | Cuisine |
| | 2 | Plaid doux | Maison |

La table du milieu est la **table de faits** : une ligne par événement mesuré, des **mesures** numériques (le montant) et des **clés** qui pointent vers les dimensions. Les petites tables autour sont les **dimensions** : une ligne par client, par produit, par jour, avec des attributs descriptifs. Dessinées autour de la table de faits, elles forment une **étoile**.

> 💡 **Intuition.** Une question d'analyse a presque toujours la forme « **mesure** par **dimension** » : le *chiffre d'affaires* par *catégorie* et par *mois*. Le schéma en étoile range les données **comme la question est posée** : la mesure au centre, les « par » autour.

### 1.2.2 Construire l'étoile de la boutique

Nous allons créer, dans le schéma `dwh`, cinq dimensions et une table de faits. Commençons par la **dimension de date**, qui n'existe dans aucune source : on la **fabrique**, une ligne par jour, avec les attributs dont les analyses ont besoin (année, trimestre, mois, week-end).

```sql
CREATE SCHEMA dwh;
CREATE MACRO cle_date(d) AS CAST(strftime(CAST(d AS DATE), '%Y%m%d') AS INTEGER);
CREATE TABLE dwh.dim_date AS
SELECT cle_date(d) AS date_key, CAST(d AS DATE) AS date,
       year(d) AS annee, quarter(d) AS trimestre, month(d) AS mois,
       strftime(d, '%Y-%m') AS annee_mois, isodow(d) AS jour_semaine, isodow(d) >= 6 AS est_weekend
FROM generate_series(DATE '2023-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d);
```

La clé de la dimension est un **entier lisible** (`20250103` pour le 3 janvier 2025) : la petite fonction SQL `cle_date`, définie juste avant, la calcule à partir de n'importe quelle date, de façon que la **même règle** serve à la dimension et à toutes les tables de faits.

Puis la **dimension des produits**, copiée de la source, avec une **clé de substitution** (`produit_key`) et une ligne **« inconnu »** de clé 0 :

```sql
CREATE TABLE dwh.dim_produit AS
SELECT 0 AS produit_key, -1 AS id_produit, 'inconnu' AS nom_produit,
       'inconnu' AS categorie, 'inconnu' AS fournisseur, NULL AS prix_catalogue
UNION ALL
SELECT row_number() OVER (ORDER BY id_produit), id_produit, nom_produit,
       categorie, fournisseur, prix_vente
FROM src.produits;
```

Trois choix méritent d'être expliqués.

- **La clé de substitution** (`produit_key`) est un entier **sans signification métier**, créé par l'entrepôt. L'identifiant de la source (`id_produit`) reste dans la table comme **clé naturelle**, mais **les faits ne pointent jamais dessus** : si la source réutilise un jour un identifiant, ou si deux sources se rencontrent, l'entrepôt n'est pas perturbé ; et, nous le verrons en 1.4, une même clé naturelle pourra correspondre à **plusieurs versions** d'un produit.
- **La ligne « inconnu »** (clé 0) reçoit les ventes dont le produit n'existe pas (encore) dans la dimension. Sans elle, ces ventes **disparaîtraient** d'une jointure interne, et le chiffre d'affaires serait faux sans que rien ne le signale (section 1.3.5).
- **Les dimensions client, canal, promotion** se construisent de la même façon (voir le cahier). La dimension du **canal** regroupe deux colonnes de la commande (le canal de vente et le mode de livraison) en une seule ligne : c'est une dimension « fourre-tout » (*junk dimension*) qui évite de multiplier les petites tables.

```sql hide
CREATE TABLE dwh.dim_client AS
SELECT 0 AS client_key, -1 AS id_client, 'inconnue' AS ville, 'inconnu' AS canal_acquisition, 'inconnu' AS carte_fidelite, NULL AS annee_inscription, 'inconnue' AS tranche_age
UNION ALL
SELECT row_number() OVER (ORDER BY id_client), id_client, ville, canal_acquisition, CASE WHEN fidelite = 1 THEN 'Carte fidélité' ELSE 'Sans carte' END, year(date_inscription),
       CASE WHEN 2025 - annee_naissance < 30 THEN '< 30 ans' WHEN 2025 - annee_naissance < 45 THEN '30-44 ans' WHEN 2025 - annee_naissance < 60 THEN '45-59 ans' ELSE '60 ans et +' END
FROM src.clients;
CREATE TABLE dwh.dim_canal AS
SELECT row_number() OVER (ORDER BY canal, mode_livraison) AS canal_key, canal, mode_livraison FROM (SELECT DISTINCT canal, mode_livraison FROM src.commandes);
CREATE TABLE dwh.dim_promotion AS
SELECT 1 AS promo_key, 'Aucune' AS code_promo, 'Sans promotion' AS famille_promo
UNION ALL SELECT 2, 'SOLDES', 'Saisonnière' UNION ALL SELECT 3, 'FIDELITE', 'Fidélisation' UNION ALL SELECT 4, 'BIENVENUE', 'Acquisition';
```

Enfin la **table de faits**. Le **grain** (ce que représente une ligne) est déclaré d'abord : **une ligne de commande**. Chaque ligne reçoit les clés des cinq dimensions, ses mesures telles que la source les donne, et deux mesures **calculées une fois pour toutes** : le montant hors taxe et le coût d'achat. Aucune n'est **arrondie** : on arrondit à l'affichage, jamais au stockage (voir plus bas).

```sql
CREATE TABLE dwh.fait_ventes AS
SELECT l.id_ligne, l.id_commande,
       cle_date(c.date_commande) AS date_key,
       k.client_key, p.produit_key, ca.canal_key, pr.promo_key,
       l.quantite, l.prix_unitaire, l.remise_pct,
       l.montant AS montant_ttc, l.montant / 1.2 AS montant_ht,
       l.quantite * sp.cout_achat AS cout_achat
FROM src.lignes_commande l
JOIN src.commandes c USING (id_commande)
JOIN src.produits sp USING (id_produit)
JOIN dwh.dim_client k ON k.id_client = c.id_client
JOIN dwh.dim_produit p ON p.id_produit = l.id_produit
JOIN dwh.dim_canal ca ON ca.canal = c.canal AND ca.mode_livraison = c.mode_livraison
JOIN dwh.dim_promotion pr ON pr.code_promo = COALESCE(c.code_promo, 'Aucune');
```

La table de faits a **le même nombre de lignes que la source** : on n'a rien perdu, rien dupliqué. C'est la première vérification, et elle est systématique :

```sql
SELECT (SELECT COUNT(*) FROM src.lignes_commande) AS source,
       (SELECT COUNT(*) FROM dwh.fait_ventes) AS entrepot,
       (SELECT ROUND(SUM(montant), 2) FROM src.lignes_commande) AS ttc_source,
       (SELECT ROUND(SUM(montant_ttc), 2) FROM dwh.fait_ventes) AS ttc_entrepot;
```
<!--sortie-->
```text
 source  entrepot  ttc_source  ttc_entrepot
  83905     83905  3653157.28    3653157.28
```

```python hide
ref = O.construire_etoile(O.ouvrir(os.environ["DONNEES"]))
for t in ["dim_produit", "dim_client", "dim_canal", "dim_promotion", "dim_date", "fait_ventes"]:
    a, b = con.df(f"SELECT * FROM dwh.{t} ORDER BY 1"), ref.df(f"SELECT * FROM dwh.{t} ORDER BY 1")
    assert a.equals(b), t
print("le SQL du livre produit exactement les tables de référence de build/outils_ch01.py")
```
<!--sortie-->
```text
le SQL du livre produit exactement les tables de référence de build/outils_ch01.py
```

La dimension des produits, avec sa ligne « inconnu », ressemble à ceci :

```sql
SELECT produit_key, id_produit, nom_produit, categorie FROM dwh.dim_produit
ORDER BY produit_key LIMIT 4;
```
<!--sortie-->
```text
 produit_key  id_produit        nom_produit categorie
           0          -1            inconnu   inconnu
           1           1 Casserole nordique   Cuisine
           2           2          Poêle mat   Cuisine
           3           3         Bol design   Cuisine
```

Voici l'étoile complète de ce qu'on vient de bâtir :

![Le schéma en étoile de la boutique : la table de faits fait_ventes au centre, cinq dimensions autour. Les clés (date_key, client_key, produit_key, canal_key, promo_key) sont des clés de substitution.](figures/ch01-etoile.png)

```python hide
O.fig_etoile()
```
<!--sortie-->
```text
figure : ch01-etoile.png
```

> ⚠️ **Piège : mettre les clés naturelles dans la table de faits.** Si `fait_ventes` contenait `id_produit` au lieu de `produit_key`, la première réutilisation d'un identifiant ou la première fusion de deux sources casserait **toutes les jointures historiques** sans erreur visible. On joint toujours sur la **clé de substitution**.

### 1.2.3 Interroger l'étoile, et vérifier

Une question d'analyse se pose maintenant **toujours de la même façon** : une jointure de la table de faits avec les dimensions utiles, un filtre, un regroupement. Le chiffre d'affaires hors taxe par catégorie, en janvier 2025 :

```sql
SELECT p.categorie, ROUND(SUM(v.montant_ht)) AS ca_ht
FROM dwh.fait_ventes v
JOIN dwh.dim_date d USING (date_key)
JOIN dwh.dim_produit p USING (produit_key)
WHERE d.annee_mois = '2025-01'
GROUP BY 1 ORDER BY 1;
```
<!--sortie-->
```text
 categorie   ca_ht
 Bien-être  9013.0
   Cuisine 16229.0
Décoration 16377.0
    Jardin  6213.0
    Maison 23040.0
 Papeterie  3444.0
```

Que gagne-t-on, par rapport à la même question posée sur la base d'exploitation ? **Honnêtement, pas moins de jointures** : la requête sur la source en compte aussi trois (lignes, commandes, produits). Le gain est ailleurs :

- les attributs de date (**trimestre, mois, week-end**) sont **déjà là**, écrits **une fois**, au lieu d'être recalculés par chaque requête avec chacune sa petite variante (la semaine commence-t-elle le lundi ou le dimanche ?) ;
- le **montant hors taxe** est une colonne, pas une division par 1,2 recopiée dans quarante requêtes (et oubliée dans la quarante et unième) ;
- les jointures sont **toutes du même type** (fait vers dimension, sur une clé entière) : on ne peut pas dupliquer des lignes en se trompant de clé ;
- tous les tableaux de bord et tous les rapports **parlent de la même colonne** : c'est la réponse à la question de la gérante.

On ne se fie pourtant pas à un résultat parce qu'il a l'air plausible. Première vérification croisée : **pandas, depuis les fichiers d'origine**, retrouve-t-il les mêmes 216 chiffres (36 mois × 6 catégories) ?

```python hide-code
cmd = pd.read_csv(os.environ["DONNEES"] + "/commandes.csv", usecols=["id_commande", "date_commande"])
lig = pd.read_csv(os.environ["DONNEES"] + "/lignes_commande.csv")
prod = pd.read_csv(os.environ["DONNEES"] + "/produits.csv", usecols=["id_produit", "categorie"])
x = lig.merge(cmd, on="id_commande").merge(prod, on="id_produit")
x["mois"] = x["date_commande"].str[:7]
pd_ht = (x.groupby(["mois", "categorie"])["montant"].sum() / 1.2).rename("pandas")
et_ht = con.df("""SELECT d.annee_mois AS mois, p.categorie, SUM(v.montant_ht) AS etoile FROM dwh.fait_ventes v
                  JOIN dwh.dim_date d USING (date_key) JOIN dwh.dim_produit p USING (produit_key) GROUP BY 1, 2""").set_index(["mois", "categorie"])["etoile"]
cmp = pd.concat([pd_ht, et_ht], axis=1)
ecart = (cmp["pandas"] - cmp["etoile"]).abs().max()
print(f"{len(cmp)} cellules mois x catégorie comparées ; écart absolu maximal : {ecart:.2f} €")
assert len(cmp) == 216 and ecart < 1e-6
```
<!--sortie-->
```text
216 cellules mois x catégorie comparées ; écart absolu maximal : 0.00 €
```

L'écart n'est que du bruit de calcul en virgule flottante : les deux outils trouvent **les mêmes 216 chiffres**. Deuxième vérification, plus exigeante : **la comptabilité**. Le compte de résultat mensuel de la boutique donne un chiffre d'affaires hors taxe, arrondi à l'euro. L'étoile le retrouve-t-elle ?

```sql
WITH e AS (SELECT d.annee_mois AS mois, SUM(v.montant_ht) AS ca
           FROM dwh.fait_ventes v JOIN dwh.dim_date d USING (date_key) GROUP BY 1)
SELECT COUNT(*) AS mois, ROUND(MAX(ABS(e.ca - c.ca_ht)), 2) AS ecart_max,
       ROUND(SUM(e.ca) - SUM(c.ca_ht), 2) AS ecart_total
FROM e JOIN src.compte_resultat c ON c.mois = e.mois;
```
<!--sortie-->
```text
 mois  ecart_max  ecart_total
   36       0.49        -0.27
```

Sur les **trente-six mois**, l'écart maximal est inférieur à un euro : c'est l'arrondi à l'euro de la comptabilité. C'est ce que l'on appelle un **rapprochement** : l'entrepôt n'est digne de confiance que s'il retrouve un chiffre qu'une autre source, indépendante, établit. Nous reviendrons sur ce contrôle au chapitre 2 (il devient une étape du chargement) et au chapitre 4 (reporting de gestion).

```python hide
arr = con.df("""WITH e AS (SELECT d.annee_mois AS mois, SUM(ROUND(v.montant_ttc / 1.2, 2)) AS ca FROM dwh.fait_ventes v JOIN dwh.dim_date d USING (date_key) GROUP BY 1)
                SELECT MAX(ABS(e.ca - c.ca_ht)) AS m FROM e JOIN src.compte_resultat c ON c.mois = e.mois""")["m"][0]
ex = con.df("""WITH e AS (SELECT d.annee_mois AS mois, SUM(v.montant_ht) AS ca FROM dwh.fait_ventes v JOIN dwh.dim_date d USING (date_key) GROUP BY 1)
                SELECT MAX(ABS(e.ca - c.ca_ht)) AS m FROM e JOIN src.compte_resultat c ON c.mois = e.mois""")["m"][0]
assert round(arr, 2) == 2.80 and round(ex, 2) == 0.49
```

> ⚠️ **Piège : arrondir au stockage.** Nous avons gardé `montant_ht` **sans arrondi**. Si l'on avait arrondi chaque ligne à deux décimales, l'écart maximal avec la comptabilité serait monté de **0,49 €** à **2,80 €** sur un mois : les montants TTC de la boutique sont souvent en dixièmes d'euro, leur division par 1,2 tombe sur des décimales du type 0,91666…, et l'arrondi les pousse **presque toujours dans le même sens**. Sur 80 000 lignes, ces petits écarts **ne se compensent pas**. Règle : on **stocke** avec toute la précision (type décimal ou flottant), on **arrondit à l'affichage**.

Voici le résultat de la requête « chiffre d'affaires par catégorie et par mois » sur trois ans, lu depuis l'étoile :

![Chiffre d'affaires hors taxe mensuel par catégorie, 2023-2025, lu dans l'étoile : la saisonnalité de fin d'année est visible dans toutes les catégories.](figures/ch01-ca-categorie.png)

```python hide
pv = con.df("""SELECT d.annee_mois, p.categorie, SUM(v.montant_ht) AS ca FROM dwh.fait_ventes v
               JOIN dwh.dim_date d USING (date_key) JOIN dwh.dim_produit p USING (produit_key) GROUP BY 1, 2""").pivot(index="annee_mois", columns="categorie", values="ca")
O.fig_ca_categorie(pv[["Jardin", "Maison", "Décoration", "Cuisine", "Bien-être", "Papeterie"]])
```
<!--sortie-->
```text
figure : ch01-ca-categorie.png
```

### 1.2.4 Le flocon : normaliser une dimension

Dans une étoile, les dimensions sont **à plat** : la dimension des produits contient le nom, la catégorie, le fournisseur dans la même table, avec des répétitions (la catégorie « Cuisine » est écrite vingt fois). On peut au contraire **normaliser** la dimension en la découpant, par exemple en isolant les catégories dans leur propre table. On obtient un **schéma en flocon** (*snowflake*).

![Étoile (à gauche) et flocon (à droite) : le flocon normalise la dimension des produits en une table de catégories, au prix d'une jointure de plus.](figures/ch01-flocon.png)

```python hide
O.fig_flocon()
```
<!--sortie-->
```text
figure : ch01-flocon.png
```

Pour regrouper les catégories en **familles** (un regroupement défini ici pour l'exemple), le flocon crée une table de catégories ; la dimension des produits n'en garde que la clé :

```sql
CREATE TABLE dwh.dim_categorie AS
SELECT row_number() OVER (ORDER BY categorie) AS categorie_key, categorie,
       CASE WHEN categorie = 'Jardin' THEN 'Extérieur'
            WHEN categorie IN ('Cuisine', 'Maison', 'Décoration') THEN 'Intérieur'
            ELSE 'Loisirs et bien-être' END AS famille
FROM (SELECT DISTINCT categorie FROM src.produits);
CREATE VIEW dwh.dim_produit_flocon AS
SELECT p.produit_key, p.nom_produit, c.categorie_key
FROM dwh.dim_produit p LEFT JOIN dwh.dim_categorie c USING (categorie);
```

Le chiffre d'affaires par famille exige maintenant **une jointure de plus** (fait, produit, catégorie), mais donne bien le même total :

```sql
SELECT c.famille, ROUND(SUM(v.montant_ht)) AS ca_ht
FROM dwh.fait_ventes v
JOIN dwh.dim_produit_flocon p USING (produit_key)
JOIN dwh.dim_categorie c USING (categorie_key)
GROUP BY 1 ORDER BY 1;
```
<!--sortie-->
```text
             famille     ca_ht
           Extérieur  808650.0
           Intérieur 1833406.0
Loisirs et bien-être  402242.0
```

Quand préférer l'un ou l'autre ?

| | Étoile | Flocon |
|---|---|---|
| **Jointures par requête** | le moins possible | une de plus par niveau |
| **Redondance** | oui (texte répété) | non |
| **Lisibilité pour l'analyste** | une table par « point de vue » | plusieurs tables à connaître |
| **Mise à jour d'un libellé** | à modifier dans la dimension, en une fois | idem, dans une table plus petite |
| **Quand le choisir** | **par défaut**, surtout avec les outils de tableau de bord | dimension énorme et très hiérarchique, ou sous-dimension **partagée** par plusieurs dimensions |

Avec des moteurs en colonnes qui compressent très bien le texte répété (section 1.5), l'économie de place du flocon est **négligeable** ; c'est la **simplicité de lecture** de l'étoile qui l'emporte presque toujours.

> 🧭 **En pratique : étoile par défaut.** On part d'une étoile. On ne normalise une dimension que si l'on peut citer la raison (une sous-dimension commune à plusieurs dimensions, par exemple une table de villes utilisée à la fois par les clients et les magasins).

### 1.2.5 Ce que l'étoile facilite, et ce qu'elle coûte

L'étoile facilite trois choses : les **requêtes** (même forme à chaque fois), les **outils** (un tableau de bord s'y branche directement ; le « modèle de données » du volume IV, section 2.1, est exactement une étoile) et la **gouvernance** (une colonne, une définition, un propriétaire).

Elle a un coût. Les **dimensions** sont **dénormalisées**, donc redondantes ; il faut **les reconstruire** quand la source change ; et chaque nouvelle question qui exige un nouvel attribut (« le jour de la semaine de la livraison ») demande de le **modéliser** d'abord. Cette discipline est le prix de chiffres qui ne divergent plus. Pour une petite boutique, le calcul est vite fait : l'étoile entière tient en mémoire, se reconstruit en un instant, et rend le débat « quel chiffre est le bon ? » **sans objet**.

> ✅ **À retenir.**
> - L'**étoile** : une table de **faits** (mesures + clés) au centre, des **dimensions** (descriptions) autour. Les questions s'écrivent « mesure par dimension ».
> - On joint toujours sur des **clés de substitution** ; une ligne **« inconnu »** (clé 0) évite de perdre des ventes ; la **dimension de date** se fabrique.
> - On **vérifie** : mêmes effectifs et mêmes totaux que la source, même résultat par un second outil (pandas), même chiffre que la **comptabilité** (rapprochement).
> - Le **flocon** normalise une dimension ; on part d'une étoile et l'on ne normalise que pour une raison précise.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.2 et 1.3, exercices 1.2 à 1.4.
