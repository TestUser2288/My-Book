## 5.1 Modèle relationnel et conception de bases de données

> 💡 **Intuition.** Une base de données relationnelle, c'est **un classeur de tableaux bien rangés** (les *tables*) **qui se parlent entre eux** grâce à des numéros d'identification (les *clés*). Au lieu de tout recopier dans un seul gros tableau, on range chaque chose à **un seul endroit** : les clients dans un tableau, les produits dans un autre, les commandes dans un troisième, et on les relie par des numéros.

### 5.1.1 Pourquoi pas simplement un fichier CSV ?

La gérante a commencé avec un fichier Excel. Un jour, elle s'est retrouvée avec `commandes_v3_FINAL.xlsx`, `commandes_v3_FINAL_corrige.xlsx` et `commandes_v3_VRAIMENT_FINAL.xlsx`. Dans l'un, la cliente « Léa Martin » habite Ville F, dans l'autre Ville G : laquelle est la bonne ? Personne ne sait. Les problèmes d'un fichier à plat sont toujours les mêmes :

| Problème | Exemple chez la boutique | Ce que fait une base de données |
|---|---|---|
| **Redondance** | l'adresse d'un client est recopiée sur chacune de ses 28 commandes | elle est stockée **une seule fois** |
| **Incohérence** | deux lignes du même client donnent deux villes différentes | impossible : une seule ligne client, référencée par un numéro |
| **Données invalides** | une note de satisfaction de 7, un canal « Marché » qui n'existe pas | des **contraintes** refusent la saisie |
| **Volume** | 10 millions de lignes : le fichier ne s'ouvre plus | la base lit seulement ce dont elle a besoin (grâce aux *index*, 5.4) |
| **Accès simultané** | deux employés modifient le fichier en même temps : l'un écrase l'autre | des **transactions** gèrent les accès concurrents (5.4) |
| **Questions complexes** | « les clients de Ville F qui ont acheté des bijoux deux mois de suite » | un langage fait pour ça : **SQL** |

Un **SGBD** (*système de gestion de bases de données*) est le logiciel qui garantit tout cela. Les plus courants : **PostgreSQL** et **MySQL** (libres, très répandus sur le web), **SQL Server** et **Oracle** (grandes entreprises), **SQLite** (une base dans un simple fichier, présente dans votre téléphone, votre navigateur et Python), **BigQuery**, **Snowflake**, **Redshift** (entrepôts de données dans le *cloud*). Tous parlent SQL, avec de petits accents régionaux (*dialectes*).

### 5.1.2 Le modèle relationnel

Le modèle relationnel date de 1970 (Edgar F. Codd, chez IBM). Il tient en quelques mots.

- Une **table** (ou *relation*) représente un type de chose : les clients, les produits...
- Une **colonne** (ou *attribut*) est une propriété de cette chose : `prenom`, `ville`...
- Une **ligne** (ou *enregistrement*, ou *n-uplet*) est une chose précise : la cliente n° 1.
- Chaque colonne a un **type** (entier, texte, date...).

Voici trois clients de la boutique sous forme de table :

| id_client | prenom | nom | ville |
|---|---|---|---|
| 1 | Yann | Lambert | Ville C |
| 2 | Sam | Fontaine | Ville A |
| 3 | Adam | Michel | Ville F |

> 📐 **Définition rigoureuse.** Soient $D_1,\dots,D_p$ des ensembles appelés **domaines** (par exemple $D_1=\mathbb N$ pour les numéros, $D_2=$ les chaînes de caractères). Une **relation** $R$ de **schéma** $R(A_1:D_1,\dots,A_p:D_p)$ est un **sous-ensemble fini** du produit cartésien
> $$R\ \subseteq\ D_1\times D_2\times\cdots\times D_p .$$
> Deux conséquences importantes, souvent oubliées : (1) $R$ étant un **ensemble**, il n'y a **ni doublons ni ordre** entre les lignes : demander « la première ligne » n'a pas de sens sans préciser un critère de tri ; (2) chaque case contient **une seule valeur** de son domaine (nous y reviendrons avec la première forme normale, 5.4).

**Les clés.** C'est là que la magie opère.

- Une **clé candidate** est un ensemble minimal de colonnes qui identifie **sans ambiguïté** une ligne. Dans `clients`, `id_client` en est une. Le couple (`prenom`, `nom`) n'en est pas une : nous verrons au 5.2.4 que notre propre base contient trois « Léa Fontaine » dans trois villes différentes, et même deux « Anna Faure » qui habitent toutes deux Ville B. Un nom n'est **jamais** un bon identifiant.
- La **clé primaire** (*primary key*, PK) est la clé candidate choisie comme identifiant officiel. Elle ne peut être ni vide (`NULL`) ni répétée. Par convention, on utilise un **numéro** sans signification (une *clé de substitution*, ou *surrogate key*) : il ne change jamais, même si la personne déménage ou change de nom.
- Une **clé étrangère** (*foreign key*, FK) est une colonne qui **référence la clé primaire d'une autre table**. Dans `commandes`, la colonne `id_client` désigne le client qui a passé la commande. C'est ainsi que les tables « se parlent ».
- L'**intégrité référentielle** est la règle qui en découle : une clé étrangère ne peut contenir que des valeurs qui **existent** dans la table référencée. Impossible d'enregistrer une commande du client n° 9999 s'il n'existe pas.

> 💡 **L'analogie du carnet d'adresses.** Dans votre téléphone, vous ne recopiez pas toutes les informations d'un contact dans chaque SMS ; vous gardez une fiche « Camille » et vous écrivez à « Camille ». La fiche est la ligne de `clients`, son numéro est la clé primaire, et chaque SMS porte une clé étrangère vers elle.

**Les relations entre tables** se décrivent en trois types, selon le nombre de lignes de chaque côté :

- **Un à plusieurs (1–N)** : un client passe **plusieurs** commandes, mais chaque commande est passée par **un seul** client. La clé étrangère se place du côté « plusieurs » (`commandes.id_client`).
- **Plusieurs à plusieurs (N–N)** : une commande contient **plusieurs** produits, et un produit figure dans **plusieurs** commandes. Une clé étrangère ne suffit plus : on crée une **table d'association** (ou *de jonction*) qui contient une ligne par couple (commande, produit). C'est la table `lignes_commande`, qui porte aussi les attributs du lien : `quantite` et `prix_unitaire`.
- **Un à un (1–1)** : rare ; en pratique, on fusionne souvent les deux tables.

Un cas particulier amusant : la relation **réflexive**. La boutique a un programme de parrainage : un client peut avoir été **parrainé par un autre client**. La table `clients` se référence donc elle-même (`id_parrain` pointe vers `id_client`). Nous nous en servirons pour les requêtes récursives (5.3).

Voici le **schéma** complet de notre base. Chaque boîte est une table ; l'étiquette **PK** désigne une clé primaire, **FK** une clé étrangère. Un trait relie chaque clé étrangère (côté « N », plusieurs) à la clé primaire qu'elle référence (côté « 1 »).

![Schéma de la base de la boutique : cinq tables. Un trait relie chaque clé étrangère (N) à la clé primaire qu'elle référence (1). La table lignes_commande est la table d'association entre commandes et produits.](figures/ch05-schema-er.png)

> 📐 **L'algèbre relationnelle : les maths derrière SQL.** Les requêtes SQL sont la traduction de cinq opérations sur les ensembles, que Codd a décrites dès 1970. Les connaître donne une compréhension durable, qui dépasse les différences de syntaxe entre les SGBD :
>
> | Opération | Notation | Sens | Équivalent SQL |
> |---|---|---|---|
> | **Sélection** | $\sigma_{\text{condition}}(R)$ | garder certaines **lignes** | `WHERE` |
> | **Projection** | $\pi_{A_1,\dots,A_k}(R)$ | garder certaines **colonnes** | `SELECT col1, col2` |
> | **Produit cartésien** | $R\times S$ | **toutes les paires** (une ligne de $R$, une ligne de $S$) | `CROSS JOIN` |
> | **Jointure** | $R\bowtie_{\text{cond}}S=\sigma_{\text{cond}}(R\times S)$ | les paires qui vérifient une condition | `JOIN ... ON` |
> | **Union / différence** | $R\cup S$, $R\setminus S$ | ensembles de lignes | `UNION`, `EXCEPT` |
>
> La ligne la plus importante est celle de la **jointure** : c'est un produit cartésien **filtré**. Nous le verrons « en vrai » au 5.2.5 : 80 clients × 400 commandes = 32 000 paires, dont seules 400 sont les « bonnes ».


```python hide
import sqlite3
import sys

import numpy as np
import pandas as pd
sys.path.insert(0, "build")
from base_sql import construire

con = construire()                         # la base complète, en mémoire (graine fixée)
fichier = sqlite3.connect("donnees/boutique.db")
con.backup(fichier)                        # le fichier fourni avec le livre = la base en mémoire
fichier.close()
assert [con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0] for t in
        ("categories", "produits", "clients", "commandes", "lignes_commande")] == [4, 16, 80, 400, 693]
```

### 5.1.3 Créer des tables : un petit exemple, puis la base fournie

Une table se crée avec l'instruction `CREATE TABLE`, qui énumère les colonnes, leur type et leurs règles ; on la remplit avec `INSERT`. Voici, sur une base vide et temporaire, la création de deux tables du schéma ci-dessus, avec deux produits.

```python
import sqlite3

essai = sqlite3.connect(":memory:")                 # une base vide, en mémoire
essai.executescript("""
CREATE TABLE categories (id_categorie INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE);
CREATE TABLE produits (
    id_produit INTEGER PRIMARY KEY, nom TEXT NOT NULL,
    id_categorie INTEGER NOT NULL REFERENCES categories(id_categorie),
    prix_catalogue REAL NOT NULL CHECK (prix_catalogue > 0));
INSERT INTO categories VALUES (1, 'Poterie');
INSERT INTO produits VALUES (1, 'Plat décoratif', 1, 45.0), (2, 'Bol en céramique', 1, 18.0);
""")
print(essai.execute("SELECT nom, prix_catalogue FROM produits").fetchall())
```
<!--sortie-->
```text
[('Plat décoratif', 45.0), ('Bol en céramique', 18.0)]
```

Chaque ligne de `CREATE TABLE` est la traduction directe du schéma : `PRIMARY KEY` pour la clé primaire, `REFERENCES` pour la clé étrangère, `NOT NULL` et `CHECK` pour les règles (nous les détaillons au 5.1.4). Le fichier `donnees/boutique.db`, **fourni avec le livre**, contient la base complète construite de la même façon, avec ses cinq tables. Elle a été générée par le script `build/base_sql.py` à partir du fichier `donnees/commandes.csv` du chapitre 3, avec une graine fixée : vous retrouverez exactement les mêmes résultats que dans le livre. Reconstruire toute la base, étape par étape, est l'objet de l'application 5.1 du cahier.

| Table | Lignes | Contenu |
|---|---|---|
| `categories` | 4 | les familles de produits (poterie, textile, bijoux, cosmétiques) |
| `produits` | 16 | le catalogue, avec le prix catalogue |
| `clients` | 80 | les inscrits (dont 14 qui n'ont jamais commandé), avec leur éventuel parrain |
| `commandes` | 400 | les 400 commandes du chapitre 3, avec une date et un client ajoutés |
| `lignes_commande` | 693 | le détail de chaque commande, produit par produit |

Les lignes de commande sont construites pour que la **somme** (quantité × prix) de chaque commande retombe **exactement** sur son montant. Le prix payé peut différer de quelques pour cent du prix du catalogue (promotions, variations de prix dans l'année) ; nous verrons au 5.4 pourquoi il est essentiel de **recopier** le prix dans la ligne de commande au lieu de le relire dans le catalogue.

Un premier regard sur le contenu : combien de lignes par table, et un aperçu des clients. (`SELECT *` signifie « toutes les colonnes » et `LIMIT 5` « seulement 5 lignes » ; le mot-clé `UNION ALL` empile les résultats de plusieurs requêtes, nous y reviendrons.)

```sql
SELECT 'clients' AS "table", COUNT(*) AS lignes FROM clients
UNION ALL SELECT 'commandes', COUNT(*) FROM commandes
UNION ALL SELECT 'lignes_commande', COUNT(*) FROM lignes_commande;
```
<!--sortie-->
```text
          table  lignes
        clients      80
      commandes     400
lignes_commande     693
```

```sql
SELECT * FROM clients LIMIT 5;
```
<!--sortie-->
```text
 id_client prenom      nom   ville date_inscription telephone id_parrain
         1   Yann  Lambert Ville C       2024-12-14   7725588       None
         2    Sam Fontaine Ville A       2024-12-16       NaN       None
         3   Adam   Michel Ville F       2024-12-16       NaN       None
         4   Anna    Blanc Ville A       2024-12-18       NaN       None
         5   Anna   Michel Ville A       2024-12-30   7402250       None
```

Remarquez la colonne `id_parrain` : vide pour la plupart des clients (c'est un `NULL`), mais quand elle est remplie, elle contient le numéro d'un autre client. Le `telephone` vide de certains clients est lui aussi un `NULL` : il nous réservera quelques surprises au 5.2.7.

Lisons maintenant ensemble les lignes des quatre premières commandes, car cette table est le cœur de la base :

```sql
SELECT * FROM lignes_commande WHERE id_commande <= 4;
```
<!--sortie-->
```text
 id_commande  id_produit  quantite  prix_unitaire
           1           1         1          44.80
           2          10         1          34.50
           3           2         1          17.84
           3           3         1          64.42
           3          13         1           5.94
           4          11         1          15.57
           4          14         1          14.53
```

La commande n° 1 a un montant de 44,80 € dans la table `commandes` : une seule ligne ici, le produit n° 1, en un exemplaire à 44,80 €. La commande n° 3 a un montant de 88,20 € : trois lignes, trois produits différents, chacun en un exemplaire (17,84 + 64,42 + 5,94 = 88,20). La table `commandes` ne dit **pas** ce qu'il y a dans le panier ; c'est `lignes_commande` qui le dit. Ce découpage est le propre d'une bonne base de données.

> 🧪 **Pourquoi une clé primaire à deux colonnes ?** Dans `lignes_commande`, la clé primaire est le **couple** (`id_commande`, `id_produit`) : une même commande ne peut pas contenir deux fois le même produit sur deux lignes séparées ; si le client en prend trois, on écrit `quantite = 3`. C'est une **clé composite**.

### 5.1.4 Types, contraintes : la base se défend

Relisez les `CREATE TABLE`. Outre les noms et les types, on y trouve des **contraintes** : des règles que la base fait respecter **toute seule**.

| Contrainte | Exemple dans notre schéma | Effet |
|---|---|---|
| `PRIMARY KEY` | `id_client INTEGER PRIMARY KEY` | identifiant unique et non vide |
| `NOT NULL` | `prenom TEXT NOT NULL` | la valeur est obligatoire |
| `UNIQUE` | `nom TEXT NOT NULL UNIQUE` (catégories) | pas de doublon |
| `CHECK` | `satisfaction BETWEEN 1 AND 5` | la valeur doit vérifier une condition |
| `REFERENCES` | `id_client ... REFERENCES clients(id_client)` | clé étrangère (intégrité référentielle) |

Voyons-les à l'œuvre en essayant d'enregistrer des données **absurdes** :

```python
essais = {
    "client inexistant": "INSERT INTO commandes VALUES (9001, 9999, '2025-06-01', 'Site', 50, 2, 4)",
    "canal inconnu":     "INSERT INTO commandes VALUES (9002, 1, '2025-06-01', 'Marché', 50, 2, 4)",
    "note de 7 sur 5":   "INSERT INTO commandes VALUES (9003, 1, '2025-06-01', 'Site', 50, 2, 7)",
    "prénom manquant":   "INSERT INTO clients VALUES (500, NULL, 'Test', 'Ville H', '2025-06-01', NULL, NULL)",
}
for nom, requete in essais.items():
    try:
        con.execute(requete)
    except sqlite3.IntegrityError as erreur:
        print(f"{nom:18s} -> refusé : {erreur}")
```
<!--sortie-->
```text
client inexistant  -> refusé : FOREIGN KEY constraint failed
canal inconnu      -> refusé : CHECK constraint failed: canal IN ('Réseaux', 'Site', 'Boutique')
note de 7 sur 5    -> refusé : CHECK constraint failed: satisfaction BETWEEN 1 AND 5
prénom manquant    -> refusé : NOT NULL constraint failed: clients.prenom
```

Chaque donnée absurde est **refusée avec un message clair**, et les tables restent intactes (la base garde ses 400 commandes). C'est la grande différence avec une feuille Excel, où rien n'empêche de taper « sept » dans la colonne des notes. Une base bien conçue rend les erreurs de saisie **impossibles** au lieu de les laisser se glisser puis fausser silencieusement une analyse.

> ⚠️ **Particularités de SQLite (à savoir).** (1) SQLite n'applique les clés étrangères que si on le demande par `PRAGMA foreign_keys = ON` (le script de construction l'active ; avec le fichier fourni, il faut l'exécuter à chaque connexion, car ce réglage n'est pas mémorisé dans le fichier). Les autres SGBD les appliquent toujours. (2) SQLite est « souple » avec les types : il accepterait du texte dans une colonne d'entiers. PostgreSQL, lui, est strict. (3) SQLite n'a **pas de type date** : on stocke les dates en texte au format **ISO 8601** (`'2025-06-01'`, année-mois-jour). Ce format a l'avantage que **l'ordre alphabétique est l'ordre chronologique**, ce qui permet de comparer et de trier correctement les dates comme des textes. N'utilisez jamais `'01/06/2025'` : le tri alphabétique donnerait n'importe quoi.

> ⚠️ **Et l'argent ?** Nous stockons les montants en `REAL` (nombres à virgule flottante) par simplicité. En production, c'est une **mauvaise idée** : au chapitre 1 (analyse numérique, 1.5), nous avons vu que $0{,}1+0{,}2\neq0{,}3$ en binaire. Les bons choix sont un type décimal exact (`NUMERIC` / `DECIMAL`), ou bien des **entiers** exprimés dans la plus petite unité : en **centimes**, 44,80 € s'enregistre `4480`. Les comptables vous remercieront.

### 5.1.5 SQL sur un fichier CSV : l'import en cinq lignes

Une dernière remarque pratique. Vous n'aurez pas toujours une base toute faite : souvent, vous recevrez un CSV. La bibliothèque pandas sait le charger dans SQLite d'un trait, et vous pouvez alors utiliser SQL dessus : très pratique pour des agrégations compliquées ou pour s'entraîner.

```python
import pandas as pd

con_csv = sqlite3.connect(":memory:")                           # une base temporaire, vide
pd.read_csv("donnees/commandes.csv").to_sql("commandes_csv", con_csv, index=False)
requete = """SELECT canal, COUNT(*) AS commandes, ROUND(AVG(montant), 2) AS panier_moyen
             FROM commandes_csv GROUP BY canal ORDER BY panier_moyen DESC"""
print(pd.read_sql_query(requete, con_csv))
```
<!--sortie-->
```text
      canal  commandes  panier_moyen
0  Boutique        114         74.81
1      Site        148         59.50
2   Réseaux        138         49.01
```

On retrouve les effectifs par canal du chapitre 3 (114 commandes en boutique, 148 sur le site, 138 sur Réseaux) et, en prime, les paniers moyens : la boutique est la plus généreuse. Remarquez la différence avec la vraie base : ici la table a été **devinée** par pandas (aucune clé, aucune contrainte : l'application 5.2 du cahier l'examine), alors que notre base de la boutique a été **conçue**. Un import rapide convient pour explorer ; une base conçue est indispensable pour travailler à plusieurs et dans la durée.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 (reconstruire la base) et 5.2 (importer un CSV et lui donner un vrai schéma), exercice 5.1.

> ✅ **À retenir**
>
> - Une base relationnelle range chaque information **à un seul endroit** dans des **tables**, reliées par des **clés** (primaires, étrangères).
> - Les **contraintes** (`NOT NULL`, `CHECK`, `REFERENCES`...) font respecter les règles métier **automatiquement**.
> - Une relation **plusieurs à plusieurs** passe par une **table d'association** (`lignes_commande`).
> - Les requêtes SQL traduisent l'**algèbre relationnelle** : sélection, projection, produit cartésien, jointure (= produit filtré), union.
> - Dates : format ISO 8601 en texte. Argent : décimaux exacts ou entiers (millimes), jamais de flottants en production.
