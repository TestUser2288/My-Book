# Chapitre 5 : Bases de données et SQL

> « Les données ne vivent presque jamais dans un fichier CSV.
> Elles vivent dans une **base de données**, et pour leur parler il faut connaître **SQL**. »

Jusqu'ici, nous avons travaillé sur un tableau déjà prêt, chargé en mémoire dans un notebook. Dans une vraie entreprise, ce n'est presque jamais le cas : les commandes, les clients, les stocks sont enregistrés dans une **base de données**, souvent plusieurs millions de lignes réparties dans des dizaines de tables liées entre elles. Avant de calculer la moindre moyenne, il faut donc **aller chercher** l'information, la **croiser**, la **résumer**. Le langage de cette étape s'appelle **SQL** (*Structured Query Language*). Il a plus de cinquante ans, il est partout, et c'est l'une des compétences les plus demandées dans les offres d'emploi de data scientist et de data analyst.

La bonne nouvelle : SQL se lit presque comme de l'anglais (ou, ici, du français traduit), et un petit nombre d'idées suffisent pour répondre à 90 % des questions réelles.

## Le chemin de ce chapitre

- **5.1 Modèle relationnel et conception de bases de données** : pourquoi une base plutôt qu'un fichier ? Tables, clés, relations. Nous découvrons la base de la boutique (clients, produits, commandes, lignes de commande).
- **5.2 Requêtes SQL** : sélectionner, filtrer, trier, agréger, **joindre** plusieurs tables, imbriquer des requêtes, et éviter les pièges du `NULL` et des dates.
- **5.3 Fonctions fenêtres et CTE** : les outils des analystes expérimentés : classements, cumuls, moyennes mobiles, comparaison avec la ligne précédente, requêtes lisibles par étapes, requêtes récursives.
- **5.4 Normalisation et conception de schémas** : pourquoi on découpe les données en plusieurs tables, comment le faire proprement (formes normales), puis les index et les transactions.
- ➕ **5.5 Pour aller plus loin : bases NoSQL** (MongoDB, Redis) : quand et pourquoi sortir du modèle relationnel.

> 💡 **Le fil conducteur : la base de données de la boutique.** Au chapitre 3, nous avions un seul tableau de 400 commandes. Ici, la gérante passe à la vitesse supérieure : ses **400 commandes** (le fichier `donnees/commandes.csv`, inchangé) sont rangées dans une vraie base, à côté de la liste de ses **80 clients**, de ses **16 produits** et du **détail de chaque commande**. Tout est simulé avec une graine fixe : vous retrouverez exactement les mêmes résultats que dans le livre.

> 🛠️ **Rien à installer.** Nous utilisons **SQLite**, une base de données complète qui tient dans un simple fichier et qui est déjà fournie avec Python (module `sqlite3`). Pas de serveur à configurer, pas de mot de passe. Le SQL que vous apprendrez ici fonctionne, à de petites différences près (nous les signalons), sur PostgreSQL, MySQL, SQL Server, Oracle ou BigQuery. Le fichier `donnees/boutique.db`, fourni avec le livre, contient la base toute faite : vous pouvez aussi l'ouvrir avec n'importe quel outil graphique (DB Browser for SQLite, DBeaver...) ou avec la commande `sqlite3 donnees/boutique.db`.

> 🧭 **Comment lire les blocs `sql`.** Chaque requête est suivie de **sa sortie réelle** (raccourcie à quelques lignes, avec `LIMIT`). Pour exécuter une requête depuis Python et récupérer le résultat dans un tableau pandas (section 4.4), on écrit `pd.read_sql_query("SELECT ...", con)`, où `con` est la connexion à la base : c'est ce que fait l'outil de fabrication de ce livre en coulisses.

> 📒 **Le cahier.** Les applications guidées et les exercices corrigés de ce chapitre se trouvent dans le **cahier d'exercices et d'applications** du volume, chapitre 5 ; le livre y renvoie à la fin des sections.


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


## 5.2 Requêtes SQL : sélection, jointures, agrégation

> 💡 **Intuition.** SQL est un langage **déclaratif** : on ne dit pas *comment* trouver le résultat (« parcours la table, compare, recopie... »), on décrit *ce qu'on veut* (« les commandes de plus de 100 € passées par le canal Réseaux »), et la base choisit seule la meilleure méthode. C'est comme commander au restaurant : on dit « le plat du jour, sans oignons », pas la recette.

### 5.2.1 Anatomie d'une requête : `SELECT ... FROM ...`

La requête de base a deux morceaux obligatoires : **quoi** (`SELECT`, les colonnes) et **où** (`FROM`, la table).

```sql
SELECT id_commande, canal, montant
FROM commandes
LIMIT 4;
```
<!--sortie-->
```text
 id_commande    canal  montant
           1 Boutique     44.8
           2     Site     34.5
           3  Réseaux     88.2
           4  Réseaux     30.1
```

On peut **calculer** de nouvelles colonnes et les **renommer** avec `AS` (un *alias*). Les montants de la boutique sont TTC, avec une TVA de 19 % ; calculons le hors taxe et la TVA :

```sql
SELECT id_commande,
       montant                          AS ttc,
       ROUND(montant / 1.19, 2)         AS ht,
       ROUND(montant - montant / 1.19, 2) AS tva
FROM commandes
LIMIT 4;
```
<!--sortie-->
```text
 id_commande  ttc    ht   tva
           1 44.8 37.65  7.15
           2 34.5 28.99  5.51
           3 88.2 74.12 14.08
           4 30.1 25.29  4.81
```

Voici la requête complète « tout-en-un », avec toutes les clauses possibles, **dans l'ordre où on les écrit** :

```text
SELECT   colonnes ou calculs        -- quoi afficher
FROM     table                      -- d'où ça vient
JOIN     autre_table ON ...         -- relier d'autres tables
WHERE    condition sur les lignes   -- quelles lignes garder
GROUP BY colonnes                   -- regrouper
HAVING   condition sur les groupes  -- quels groupes garder
ORDER BY colonnes                   -- trier
LIMIT    n                          -- n lignes au maximum
```

> ⚠️ **L'ordre d'écriture n'est pas l'ordre d'exécution.** Logiquement, la base procède ainsi : (1) `FROM` / `JOIN` (assembler les lignes), (2) `WHERE` (filtrer les lignes), (3) `GROUP BY` (regrouper), (4) `HAVING` (filtrer les groupes), (5) `SELECT` (calculer les colonnes demandées), (6) `ORDER BY` (trier), (7) `LIMIT` (couper). Conséquence classique : un alias défini dans le `SELECT` n'existe **pas encore** quand le `WHERE` s'exécute (certains SGBD tolèrent l'alias dans `ORDER BY` ou `GROUP BY`, pas dans `WHERE`). Si une requête refuse votre alias dans un `WHERE`, c'est pour cette raison.

> 📐 **Lien avec l'algèbre relationnelle (5.1.2).** Une requête `SELECT a, b FROM T WHERE c` se lit : $\pi_{a,b}\bigl(\sigma_c(T)\bigr)$ : d'abord la **sélection** (les lignes), puis la **projection** (les colonnes). Le vocabulaire est trompeur : le `SELECT` de SQL correspond à la *projection* de l'algèbre, pas à sa *sélection* ! Le `WHERE` est la vraie sélection.

### 5.2.2 Filtrer avec `WHERE`

`WHERE` garde les lignes pour lesquelles la condition est **vraie**. Les comparaisons sont `=` (un seul signe égal, contrairement à Python), `<>` (différent), `<`, `<=`, `>`, `>=`. On combine avec `AND`, `OR`, `NOT`.

```sql
SELECT COUNT(*) AS nb
FROM commandes
WHERE canal = 'Réseaux' AND montant > 100;
```
<!--sortie-->
```text
 nb
 11
```

(Les textes se mettent entre **apostrophes simples** : `'Réseaux'`. Les guillemets doubles servent aux noms de colonnes.) Il y a donc peu de grosses commandes par le canal Réseaux. Pour tester une liste de valeurs, `IN` ; pour un intervalle (**bornes incluses**), `BETWEEN` ; pour une recherche de motif dans un texte, `LIKE` (`%` remplace n'importe quelle suite de caractères, `_` un seul caractère) :

```sql
SELECT COUNT(*) AS commandes_de_decembre
FROM commandes
WHERE date_commande BETWEEN '2025-12-01' AND '2025-12-31';
```
<!--sortie-->
```text
 commandes_de_decembre
                    57
```

```sql
SELECT id_produit, nom, prix_catalogue
FROM produits
WHERE nom LIKE '%parfum%';
```
<!--sortie-->
```text
 id_produit             nom  prix_catalogue
         14    Eau parfumée            14.0
         16 Bougie parfumée            20.0
```

**Attention aux priorités.** `AND` passe **avant** `OR`, comme la multiplication passe avant l'addition. L'expression `A OR B AND C` se lit donc `A OR (B AND C)`, ce qui n'est pas du tout `(A OR B) AND C`. Mesurons l'écart sur un exemple. On veut compter « les commandes de plus de 100 € passées par le canal Réseaux ou par le site » :

```sql
SELECT 'sans parenthèses' AS version, COUNT(*) AS nb
FROM commandes
WHERE canal = 'Réseaux' OR canal = 'Site' AND montant > 100
UNION ALL
SELECT 'avec parenthèses', COUNT(*)
FROM commandes
WHERE (canal = 'Réseaux' OR canal = 'Site') AND montant > 100;
```
<!--sortie-->
```text
         version  nb
sans parenthèses 152
avec parenthèses  25
```

Sans parenthèses, la requête compte **toutes** les commandes du canal Réseaux (quel que soit le montant) *plus* les commandes du site de plus de 100 € : 152 lignes. Avec parenthèses, elle compte les grosses commandes (plus de 100 €) venues des réseaux sociaux *ou* du site : 25 lignes. Un écart de 1 à 6 dans le résultat, à cause de deux caractères.

> ⚠️ **Règle d'or.** Dès qu'on mélange `AND` et `OR`, **mettez des parenthèses**, même quand elles sont techniquement inutiles. Votre lecteur (et vous dans six mois) vous en sera reconnaissant.

### 5.2.3 Trier, limiter, dédoublonner

`ORDER BY` trie (`ASC` croissant par défaut, `DESC` décroissant). Rappelez-vous (5.1.2) que sans `ORDER BY`, **l'ordre des lignes n'est pas garanti**. `LIMIT n` ne garde que les `n` premières : indispensable pour des « top 5 ».

```sql
SELECT id_commande, date_commande, canal, montant
FROM commandes
ORDER BY montant DESC
LIMIT 5;
```
<!--sortie-->
```text
 id_commande date_commande    canal  montant
         157    2025-06-23     Site    255.7
          61    2025-03-28     Site    243.8
         208    2025-07-31     Site    217.1
         243    2025-08-26 Boutique    212.4
         362    2025-12-16 Boutique    208.8
```

On peut trier sur plusieurs colonnes (`ORDER BY canal, montant DESC` : d'abord par canal, puis, à canal égal, du plus gros au plus petit montant). `DISTINCT` supprime les doublons :

```sql
SELECT DISTINCT ville
FROM clients
ORDER BY ville;
```
<!--sortie-->
```text
  ville
Ville A
Ville B
Ville C
Ville D
Ville E
Ville F
Ville G
Ville H
```

Trois précisions utiles sur ces clauses. **(1)** On peut trier sur un **alias** défini dans le `SELECT` (`ORDER BY chiffre_affaires`) ou sur la **position** de la colonne (`ORDER BY 2`), mais la première forme est bien plus lisible. **(2)** Les `NULL` (5.2.7) sont placés **en premier** par SQLite dans un tri croissant, et en dernier dans un tri décroissant ; d'autres SGBD font l'inverse, et la plupart acceptent `NULLS FIRST` / `NULLS LAST` pour le préciser. **(3)** `LIMIT n OFFSET m` saute les `m` premières lignes avant d'en garder `n` : c'est la façon classique de **paginer** un résultat (page 3 de 10 lignes : `LIMIT 10 OFFSET 20`). Rappelez-vous enfin que `LIMIT` sans `ORDER BY` donne un résultat **arbitraire** : pour un « top 5 », le tri est obligatoire.

### 5.2.4 Agréger : `COUNT`, `SUM`, `AVG`, `GROUP BY`

Jusqu'ici, chaque ligne du résultat correspondait à une ligne de la table. Le cœur de l'analyse de données, c'est l'inverse : **résumer** beaucoup de lignes en peu de chiffres. Les **fonctions d'agrégation** sont `COUNT` (nombre de lignes), `SUM` (somme), `AVG` (moyenne), `MIN`, `MAX`.

```sql
SELECT COUNT(*)                    AS nb_commandes,
       COUNT(DISTINCT id_client)   AS nb_clients_distincts,
       ROUND(SUM(montant), 2)      AS chiffre_affaires,
       ROUND(AVG(montant), 2)      AS panier_moyen,
       MIN(montant)                AS plus_petite,
       MAX(montant)                AS plus_grande
FROM commandes;
```
<!--sortie-->
```text
 nb_commandes  nb_clients_distincts  chiffre_affaires  panier_moyen  plus_petite  plus_grande
          400                    66           24098.3         60.25          8.6        255.7
```

Les 400 commandes totalisent environ 24 098 €, soit un panier moyen de **60,25 €** : c'est exactement la moyenne du chapitre 3. SQL et pandas calculent la même chose ; seule la syntaxe change. Autre information intéressante : sur les 80 clients inscrits, **66 seulement** ont passé au moins une commande.

> 💡 **Une table de correspondance pandas ↔ SQL** (que vous retrouverez en 4.4) : `df[df.canal == "Site"]` ↔ `WHERE canal = 'Site'` ; `df.groupby("canal")["montant"].mean()` ↔ `SELECT canal, AVG(montant) ... GROUP BY canal` ; `df.sort_values("montant")` ↔ `ORDER BY montant`.

**`GROUP BY`** découpe la table en **groupes** (un par valeur de la colonne) et applique les agrégations **dans chaque groupe**. Voici, par canal, le nombre de commandes, le panier moyen, le chiffre d'affaires, la satisfaction moyenne et le délai de livraison moyen :

```sql
SELECT canal,
       COUNT(*)                        AS commandes,
       ROUND(AVG(montant), 2)          AS panier_moyen,
       ROUND(SUM(montant))             AS chiffre_affaires,
       ROUND(AVG(satisfaction), 2)     AS satisfaction,
       ROUND(AVG(delai_livraison), 2)  AS delai_moyen
FROM commandes
GROUP BY canal
ORDER BY chiffre_affaires DESC;
```
<!--sortie-->
```text
   canal  commandes  panier_moyen  chiffre_affaires  satisfaction  delai_moyen
    Site        148         59.50            8807.0          3.79         4.70
Boutique        114         74.81            8528.0          4.49         0.00
 Réseaux        138         49.01            6764.0          3.72         4.49
```

En une requête de six lignes, nous avons la photographie de l'activité. Le **site** fait le plus de chiffre d'affaires parce qu'il a le plus de commandes ; la **boutique**, avec moins de commandes, a le panier moyen et la satisfaction les plus élevés (le délai de livraison y est nul : les clients repartent avec leur achat). Le canal **Réseaux** a les paniers les plus modestes.

> ⚠️ **La règle du `GROUP BY`.** Dans un `SELECT` avec `GROUP BY`, chaque colonne affichée doit être **soit dans le `GROUP BY`, soit à l'intérieur d'une fonction d'agrégation**. Demander `SELECT canal, montant ... GROUP BY canal` n'a pas de sens : quelle valeur de `montant` choisir parmi les 148 lignes du groupe « Site » ? (SQLite en choisit une, arbitrairement, sans protester ; PostgreSQL refuse avec une erreur : c'est plus prudent.)

**`WHERE` contre `HAVING`.** `WHERE` filtre les **lignes avant** le regroupement ; `HAVING` filtre les **groupes après** l'agrégation. On ne peut pas écrire `WHERE COUNT(*) > 10`, car le décompte n'existe pas encore à ce moment-là.

```sql
SELECT ville, COUNT(*) AS clients
FROM clients
GROUP BY ville
HAVING COUNT(*) >= 11
ORDER BY clients DESC, ville;
```
<!--sortie-->
```text
  ville  clients
Ville A       13
Ville B       11
Ville G       11
Ville H       11
```

Un usage très pratique de `GROUP BY ... HAVING` : **détecter les doublons**. Reprenons notre remarque du 5.1.2 : peut-on identifier un client par son prénom et son nom ? Cherchons les couples qui apparaissent plus d'une fois (`GROUP_CONCAT` recolle les villes en un seul texte) :

```sql
SELECT prenom, nom, COUNT(*) AS homonymes, GROUP_CONCAT(ville, ' / ') AS villes
FROM clients
GROUP BY prenom, nom
HAVING COUNT(*) > 1
ORDER BY homonymes DESC, nom;
```
<!--sortie-->
```text
prenom      nom  homonymes                      villes
   Léa Fontaine          3 Ville A / Ville H / Ville E
  Théo    Simon          3 Ville A / Ville C / Ville F
  Anna    Faure          2           Ville B / Ville B
   Zoé   Garcia          2           Ville G / Ville F
  Elsa   Girard          2           Ville D / Ville H
  Yann  Lambert          2           Ville C / Ville A
   Lou   Michel          2           Ville H / Ville G
   Zoé   Moreau          2           Ville E / Ville B
```

Huit couples de prénom et nom apparaissent plusieurs fois, dont trois « Léa Fontaine » ! Et deux « Anna Faure » habitent la même ville : sans le numéro `id_client`, il serait **impossible** de les distinguer. La clé primaire n'est pas un luxe.

> 💡 **`COUNT(*)` ou `COUNT(colonne)` ?** `COUNT(*)` compte les **lignes**. `COUNT(colonne)` compte les lignes où la colonne **n'est pas vide** (`NULL`) : nous y reviendrons au 5.2.7, c'est un grand classique des erreurs de comptage.

### 5.2.5 Les jointures : relier les tables

Le problème : la table `commandes` dit *quel numéro de client* a passé chaque commande, mais pas son nom ni sa ville. Pour les afficher ensemble, il faut **joindre** les deux tables.

**Une jointure est un produit cartésien filtré.** Reprenons l'algèbre relationnelle du 5.1.2 : $R\bowtie_{\text{cond}}S=\sigma_{\text{cond}}(R\times S)$. Voyons-le concrètement. Le produit cartésien « clients × commandes » forme **toutes les paires possibles** (une cliente, une commande), même absurdes :

```sql
SELECT COUNT(*) AS paires_possibles
FROM clients CROSS JOIN commandes;
```
<!--sortie-->
```text
 paires_possibles
            32000
```

Il y a bien 80 × 400 = 32 000 paires. Mais seules **400** sont « les bonnes » : celles où le numéro de client de la commande est celui de la cliente. En filtrant, on obtient la jointure :

```sql
SELECT COUNT(*) AS paires_valides
FROM clients CROSS JOIN commandes
WHERE clients.id_client = commandes.id_client;
```
<!--sortie-->
```text
 paires_valides
            400
```

C'est exactement ce que fait `JOIN ... ON` (qu'on écrit ainsi pour la lisibilité, et parce que le moteur l'exécute beaucoup plus finement que de fabriquer les 32 000 paires). L'équivalent :

```sql
SELECT cl.prenom, cl.nom, cl.ville, c.date_commande, c.montant
FROM commandes AS c
JOIN clients   AS cl ON cl.id_client = c.id_client
ORDER BY c.montant DESC
LIMIT 5;
```
<!--sortie-->
```text
prenom      nom   ville date_commande  montant
 Jules   Garcia Ville G    2025-06-23    255.7
   Lou    Simon Ville F    2025-03-28    243.8
  Nina    Faure Ville H    2025-07-31    217.1
   Sam Fontaine Ville A    2025-08-26    212.4
   Sam Fontaine Ville A    2025-12-16    208.8
```

Deux détails de lisibilité : on donne des **alias courts aux tables** (`c`, `cl`), et on **préfixe** chaque colonne par la table d'où elle vient (`cl.nom`), ce qui évite les ambiguïtés quand deux tables ont une colonne du même nom (comme `id_client`).

> 💡 **Lire une jointure.** `JOIN clients AS cl ON cl.id_client = c.id_client` se lit : « pour chaque commande `c`, va chercher la ligne de `clients` dont le numéro est `c.id_client` et accole ses colonnes ». Toujours : **clé étrangère = clé primaire**.

**Joindre plus de deux tables** se fait en enchaînant les `JOIN`. Quel est le chiffre d'affaires par **catégorie de produit** ? Il faut aller de `lignes_commande` à `produits`, puis à `categories` :

```sql
SELECT ca.nom                                    AS categorie,
       SUM(l.quantite)                           AS unites_vendues,
       ROUND(SUM(l.quantite * l.prix_unitaire))  AS chiffre_affaires
FROM lignes_commande AS l
JOIN produits        AS p  ON p.id_produit   = l.id_produit
JOIN categories      AS ca ON ca.id_categorie = p.id_categorie
GROUP BY ca.nom
ORDER BY chiffre_affaires DESC;
```
<!--sortie-->
```text
  categorie  unites_vendues  chiffre_affaires
     Bijoux             200            7006.0
    Textile             184            6994.0
    Poterie             180            6950.0
Cosmétiques             196            3148.0
```

Les trois premières catégories sont presque à égalité (les **bijoux** devancent de justesse le **textile** et la **poterie**, autour de 7 000 € chacun) ; les **cosmétiques** se vendent en grand nombre (196 unités, presque autant que les bijoux avec 200) mais à petits prix, donc leur total est bien plus faible. Ce genre d'écart entre « ce qui se vend le plus » et « ce qui rapporte le plus » est exactement le type d'information qu'on cherche.

Souvenez-vous aussi de la promesse faite en 5.1.3 : les lignes de commande devaient avoir été construites pour que chaque commande « retombe » sur son montant. Vérifions-le, avec une requête qui compte les commandes **incohérentes** (dont le montant diffère de la somme de leurs lignes) :

```sql
SELECT COUNT(*) AS commandes_incoherentes
FROM (
    SELECT c.id_commande
    FROM commandes AS c
    JOIN lignes_commande AS l ON l.id_commande = c.id_commande
    GROUP BY c.id_commande
    HAVING ABS(c.montant - SUM(l.quantite * l.prix_unitaire)) > 0.005
);
```
<!--sortie-->
```text
 commandes_incoherentes
                      0
```

Zéro : tout est cohérent. Ce type de **contrôle de cohérence** (on appelle cela un test de qualité de données) est un réflexe à avoir à chaque fois qu'on reçoit une base. Vous avez aussi vu une **sous-requête** (la requête entre parenthèses dans le `FROM`) ; nous y revenons au 5.2.6.

**`INNER JOIN` contre `LEFT JOIN`.** Le `JOIN` simple (en réalité `INNER JOIN`) ne garde que les lignes qui **ont une correspondance des deux côtés**. Un client qui n'a jamais commandé **disparaît** du résultat ! Si l'on veut garder *tous* les clients, même sans commande, on utilise `LEFT JOIN` : toutes les lignes de la table de **gauche** sont conservées, et les colonnes de la table de droite sont remplies de `NULL` quand il n'y a pas de correspondance.

```sql
SELECT cl.id_client, cl.prenom, cl.nom, cl.ville
FROM clients AS cl
LEFT JOIN commandes AS c ON c.id_client = cl.id_client
WHERE c.id_commande IS NULL
ORDER BY cl.id_client
LIMIT 6;
```
<!--sortie-->
```text
 id_client prenom      nom   ville
        10    Lou   Michel Ville H
        23   Hugo   Girard Ville G
        31   Yann    Simon Ville E
        38   Théo    Faure Ville D
        42   Hugo   Garcia Ville B
        56   Lina Fontaine Ville B
```


Les six premières lignes ci-dessus sont les premiers des quatorze clients qui se sont inscrits mais n'ont jamais acheté : une liste précieuse pour une campagne de relance (« votre premier achat à -10 % »). Le motif **`LEFT JOIN ... WHERE droite IS NULL`** (« les lignes de gauche sans correspondance à droite ») est l'un des plus utiles de tout SQL. Avec un `INNER JOIN`, ces quatorze clients n'auraient jamais été trouvés, puisqu'ils n'ont aucune commande à joindre.

> 📐 **Les quatre jointures, en une phrase.** `INNER` : l'intersection (couples valides seulement). `LEFT` : tous les couples valides, plus les lignes de gauche sans partenaire (complétées par `NULL`). `RIGHT` : l'inverse (rarement utilisé : on échange simplement les deux tables). `FULL` : les deux. SQLite gère `INNER`, `LEFT`, `CROSS` et, depuis la version 3.39, `RIGHT` et `FULL`.

**L'auto-jointure.** Rien n'interdit de joindre une table **avec elle-même** (en lui donnant deux alias différents). C'est ce qu'il faut pour afficher, pour chaque client parrainé, le nom de son parrain :

```sql
SELECT f.prenom || ' ' || f.nom AS filleul,
       p.prenom || ' ' || p.nom AS parrain
FROM clients AS f
JOIN clients AS p ON p.id_client = f.id_parrain
ORDER BY f.id_client
LIMIT 5;
```
<!--sortie-->
```text
      filleul       parrain
   Luc Garcia   Paul Martin
  Zoé Laurent Hugo Lefebvre
  Théo Garcia   Paul Martin
 Jules Garcia    Lou Michel
Alex Lefebvre   Anna Michel
```

(L'opérateur `||` recolle deux textes.) Imaginez la même table lue deux fois : une fois dans le rôle des filleuls (`f`), une fois dans celui des parrains (`p`).

**Les opérations ensemblistes** `UNION` (réunion sans doublon), `UNION ALL` (réunion en gardant les doublons), `INTERSECT` (intersection) et `EXCEPT` (différence) combinent **deux requêtes de même forme**. Combien de clients ont acheté à la fois en boutique et sur le site ?

```sql
SELECT COUNT(*) AS clients_boutique_et_site
FROM (
    SELECT id_client FROM commandes WHERE canal = 'Boutique'
    INTERSECT
    SELECT id_client FROM commandes WHERE canal = 'Site'
);
```
<!--sortie-->
```text
 clients_boutique_et_site
                       21
```

### 5.2.6 Les sous-requêtes : une requête dans une requête

Une **sous-requête** est une requête placée entre parenthèses à l'intérieur d'une autre. Trois usages courants.

**(a) Une valeur unique**, utilisable comme un nombre : « les commandes dont le montant dépasse la moyenne ».

```sql
SELECT COUNT(*) AS commandes_au_dessus_de_la_moyenne,
       ROUND(AVG(montant), 2) AS leur_montant_moyen
FROM commandes
WHERE montant > (SELECT AVG(montant) FROM commandes);
```
<!--sortie-->
```text
 commandes_au_dessus_de_la_moyenne  leur_montant_moyen
                               160               95.12
```

La sous-requête `(SELECT AVG(montant) FROM commandes)` vaut 60,25 ; la requête externe garde donc les commandes au-dessus de ce seuil. Il y en a **160 sur 400** : 40 %, bien moins que la moitié, signe d'une distribution asymétrique à droite (la moyenne dépasse la médiane, 3.1.3).

**(b) Une liste de valeurs**, avec `IN` : « les clients qui ont passé au moins une commande de plus de 200 € ».

```sql
SELECT cl.id_client, cl.prenom, cl.nom
FROM clients AS cl
WHERE cl.id_client IN (SELECT id_client FROM commandes WHERE montant > 200);
```
<!--sortie-->
```text
 id_client prenom      nom
         2    Sam Fontaine
        14  Jules   Garcia
        39    Lou    Simon
        71   Nina    Faure
```

**(c) Une condition d'existence**, avec `EXISTS` : « les clients ayant déjà acheté en boutique ». La sous-requête est ici **corrélée** : elle fait référence à la ligne courante de la requête externe (`clients.id_client`).

```sql
SELECT COUNT(*) AS clients_deja_venus_en_boutique
FROM clients
WHERE EXISTS (SELECT 1 FROM commandes AS c
              WHERE c.id_client = clients.id_client AND c.canal = 'Boutique');
```
<!--sortie-->
```text
 clients_deja_venus_en_boutique
                             26
```

> 💡 **Quand préférer une jointure à une sous-requête ?** Les deux marchent souvent. Une règle simple : si vous avez besoin des colonnes de l'autre table dans le résultat, **jointure**. Si l'autre table ne sert que de **filtre** (existence, appartenance), **`EXISTS` / `IN`**. Les CTE (5.3) rendront les requêtes imbriquées beaucoup plus lisibles.

### 5.2.7 Les pièges : `NULL` et dates

Deux sources d'erreurs reviennent sans cesse dans les requêtes des débutants (et des autres) : les valeurs **absentes** (`NULL`), qui suivent une logique à trois valeurs que l'intuition ne devine pas, et les **dates**, qui sont des textes déguisés. Cette sous-section les traite l'une après l'autre.

#### Le `NULL` : ni zéro, ni texte vide, mais « **inconnu** »

`NULL` signifie « **valeur absente ou inconnue** ». Ce n'est pas zéro, ce n'est pas le texte vide. Et il suit une logique à **trois valeurs** : vrai, faux et *inconnu*. Toute comparaison avec `NULL` donne *inconnu* : `NULL = NULL` n'est pas vrai (deux inconnues sont-elles égales ? On ne sait pas !), `NULL <> 5` n'est pas vrai non plus. Et `WHERE` ne garde que les lignes **vraies**.

Dans notre base, la colonne `telephone` contient des `NULL` (le client n'a pas donné son numéro). Dénombrons :

```sql
SELECT COUNT(*)                         AS clients,
       COUNT(telephone)                 AS avec_telephone,
       SUM(telephone IS NULL)           AS sans_telephone
FROM clients;
```
<!--sortie-->
```text
 clients  avec_telephone  sans_telephone
      80              65              15
```

`COUNT(*)` compte les 80 lignes ; `COUNT(telephone)` ignore les `NULL` et n'en compte que 65. (Dans SQLite, `telephone IS NULL` vaut 1 ou 0, d'où la somme.) La **bonne** façon de tester l'absence de valeur est `IS NULL` (ou `IS NOT NULL`). Voici ce qui arrive si l'on écrit naïvement `= NULL` :

```sql
SELECT COUNT(*) AS avec_egal_null
FROM clients
WHERE telephone = NULL;
```
<!--sortie-->
```text
 avec_egal_null
              0
```

Résultat : **zéro**, alors qu'il y a des clients sans téléphone, et aucun message d'erreur. Un deuxième piège, plus sournois : le **filtre « différent de »** qui oublie les inconnus.

```sql
SELECT (SELECT COUNT(*) FROM clients WHERE telephone <> '7725588')                       AS differents,
       (SELECT COUNT(*) FROM clients WHERE telephone <> '7725588' OR telephone IS NULL)  AS differents_ou_inconnus;
```
<!--sortie-->
```text
 differents  differents_ou_inconnus
         64                      79
```

Parmi les 80 clients, un seul a le numéro `7725588` ; on s'attendrait donc à 79 « autres » clients. Le filtre `<>` n'en trouve que **64** : les quinze clients sans téléphone ont disparu, car pour eux la condition n'est pas « vraie » mais « inconnue ». Il faut ajouter explicitement `OR telephone IS NULL`.

Les fonctions d'agrégation, elles, **ignorent** les `NULL` : `AVG(id_parrain)` ne moyennise que les clients parrainés (ce qui d'ailleurs n'a aucun sens, un numéro n'est pas une quantité). Pour remplacer un `NULL` par une valeur par défaut, on utilise **`COALESCE`**, qui renvoie son premier argument non vide :

```sql
SELECT id_client, prenom, COALESCE(telephone, '(non renseigné)') AS telephone
FROM clients
LIMIT 4;
```
<!--sortie-->
```text
 id_client prenom       telephone
         1   Yann         7725588
         2    Sam (non renseigné)
         3   Adam (non renseigné)
         4   Anna (non renseigné)
```

Enfin, le piège **le plus dangereux** du chapitre : `NOT IN` avec une sous-requête qui contient un `NULL`. Cherchons les clients qui **n'ont parrainé personne**, c'est-à-dire dont le numéro n'apparaît jamais dans la colonne `id_parrain` :

```sql
SELECT (SELECT COUNT(*) FROM clients
        WHERE id_client NOT IN (SELECT id_parrain FROM clients))                          AS naif,
       (SELECT COUNT(*) FROM clients
        WHERE id_client NOT IN (SELECT id_parrain FROM clients WHERE id_parrain IS NOT NULL)) AS corrige,
       (SELECT COUNT(*) FROM clients AS c
        WHERE NOT EXISTS (SELECT 1 FROM clients AS f WHERE f.id_parrain = c.id_client))   AS avec_not_exists;
```
<!--sortie-->
```text
 naif  corrige  avec_not_exists
    0       55               55
```

La version naïve donne **zéro** (aucun client n'est « sans filleul » ? C'est absurde) ; les deux autres donnent 55. Pourquoi ? La liste `(SELECT id_parrain FROM clients)` contient des `NULL` (tous les clients non parrainés). Or `x NOT IN (a, b, NULL)` se lit `x <> a AND x <> b AND x <> NULL` ; le dernier terme est *inconnu*, donc le tout n'est jamais vrai, quelle que soit la valeur de `x`. Le filtre élimine toutes les lignes sans le moindre avertissement.

> ⚠️ **Règle pratique.** Pour exprimer « n'est pas dans l'autre table », utilisez **`NOT EXISTS`** (insensible aux `NULL`) ou `LEFT JOIN ... IS NULL`, ou à défaut ajoutez `WHERE col IS NOT NULL` dans la sous-requête. Évitez `NOT IN (sous-requête)` sur une colonne qui peut contenir des `NULL`.

#### Les dates

Comme dit en 5.1.4, SQLite stocke les dates en texte ISO 8601 ; on les manipule avec les fonctions `strftime`, `date` et `julianday`. Le premier réflexe de l'analyste : **regrouper par mois**.

```sql
SELECT strftime('%Y-%m', date_commande)  AS mois,
       COUNT(*)                          AS commandes,
       ROUND(SUM(montant))               AS chiffre_affaires
FROM commandes
GROUP BY mois
ORDER BY mois;
```
<!--sortie-->
```text
   mois  commandes  chiffre_affaires
2025-01         16             996.0
2025-02         20            1168.0
2025-03         25            1687.0
2025-04         36            1843.0
2025-05         36            2314.0
2025-06         33            2491.0
2025-07         42            2571.0
2025-08         44            2435.0
2025-09         31            1713.0
2025-10         20            1272.0
2025-11         40            2284.0
2025-12         57            3325.0
```

`strftime('%Y-%m', ...)` extrait « année-mois » (`%Y` année, `%m` mois, `%d` jour, `%w` jour de la semaine, 0 = dimanche). On voit la saisonnalité : un creux en janvier-février, une belle période estivale, un petit creux en octobre, et le pic des fêtes en **décembre** (57 commandes, 3 325 €).

Autres opérations utiles : `date('2025-12-31', '-90 days')` (soustraire une durée), `julianday(d2) - julianday(d1)` (nombre de jours entre deux dates).

```sql
SELECT date('2025-12-31', '-90 days')          AS il_y_a_90_jours,
       date('2025-03-15', 'start of month')    AS debut_du_mois,
       CAST(julianday('2025-12-31') - julianday('2025-01-01') AS INTEGER) AS jours_ecoules;
```
<!--sortie-->
```text
il_y_a_90_jours debut_du_mois  jours_ecoules
     2025-10-02    2025-03-01            364
```

> ⚠️ **N'utilisez jamais `date('now')` dans une analyse censée être reproductible.** `'now'` change tous les jours : votre requête donnera un résultat différent demain, et nul ne pourra la rejouer. Dans ce livre, la « date du jour » est **fixée** au **31 décembre 2025** (date d'arrêté de la base). En entreprise, on passe la date d'arrêté en paramètre.

### 5.2.8 `CASE WHEN` : classer et croiser

`CASE WHEN` est le « si... alors... sinon » de SQL. Il sert à créer des **classes** à partir d'une variable numérique, et, combiné avec `SUM`, à fabriquer des **tableaux croisés**. Voici la première utilisation : répartir les commandes selon leur délai de livraison, pour voir si les clients en retard sont moins satisfaits.

```sql
SELECT CASE WHEN delai_livraison = 0 THEN '0 j (retrait)'
            WHEN delai_livraison <= 3 THEN '1 à 3 j'
            WHEN delai_livraison <= 6 THEN '4 à 6 j'
            ELSE '7 j et plus' END      AS delai,
       COUNT(*)                         AS commandes,
       ROUND(AVG(satisfaction), 2)      AS satisfaction_moyenne
FROM commandes
GROUP BY delai
ORDER BY MIN(delai_livraison);
```
<!--sortie-->
```text
        delai  commandes  satisfaction_moyenne
0 j (retrait)        114                  4.49
      1 à 3 j         88                  4.03
      4 à 6 j        156                  3.76
  7 j et plus         42                  3.17
```

La satisfaction **baisse régulièrement** avec le délai : de 4,49 pour un retrait en boutique à 3,17 au-delà d'une semaine. C'est exactement la relation que nous avions mise en évidence par la corrélation au chapitre 3, retrouvée ici avec de simples agrégations SQL. (Attention, comme toujours, à ne pas conclure trop vite à la causalité : le retrait en boutique diffère des commandes en ligne à bien d'autres égards.)

La seconde utilisation, `SUM(CASE WHEN canal = 'Site' THEN montant ELSE 0 END)`, place chaque canal dans sa propre colonne : c'est un **tableau croisé** (*pivot*). SQL n'en a pas de commande universelle, et cette astuce suffit presque toujours.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.3 (les dix meilleurs clients), 5.4 (chiffre d'affaires par mois et par canal) et 5.5 (clients dormants), exercices 5.2 à 5.7.

> ✅ **À retenir**
>
> - Ordre d'écriture : `SELECT, FROM, JOIN, WHERE, GROUP BY, HAVING, ORDER BY, LIMIT`. Ordre d'exécution : `FROM/JOIN → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`.
> - `WHERE` filtre les **lignes** (avant regroupement) ; `HAVING` filtre les **groupes** (après).
> - Une **jointure** est un produit cartésien filtré par `clé étrangère = clé primaire`. `LEFT JOIN` conserve les lignes sans correspondance : c'est l'outil pour trouver « ceux qui n'ont jamais... ».
> - `NULL` = « inconnu » : on le teste avec `IS NULL`, jamais avec `=`. `COUNT(col)` ignore les `NULL`. Méfiez-vous de `NOT IN` quand la liste peut contenir un `NULL`.
> - Dates en ISO 8601, `strftime` pour regrouper, jamais de `date('now')` dans une analyse reproductible.
> - Mettez des **parenthèses** dès que `AND` et `OR` se mélangent.


## 5.3 Fonctions fenêtres et CTE

> 💡 **Intuition.** Avec `GROUP BY` (5.2.4), on **écrase** les lignes : cent commandes deviennent une seule ligne « total ». Mais souvent on veut garder chaque commande **et**, à côté, la comparer au reste : « cette commande est-elle au-dessus du panier moyen de son canal ? », « quel est son rang ? », « combien de jours depuis la commande précédente du même client ? ». Une **fonction fenêtre** calcule un résultat sur un *groupe de lignes voisines*, **sans réduire le nombre de lignes**. C'est l'outil qui distingue l'analyste débutant de l'analyste expérimenté.

### 5.3.1 Le principe : `fonction(...) OVER (...)`

Reprenons les commandes. On aimerait voir, pour chaque commande, **le panier moyen de son canal** et l'écart entre les deux. Avec `GROUP BY`, on obtiendrait 3 lignes (une par canal) et on perdrait les commandes. Avec une fenêtre :

```sql
SELECT id_commande, canal, montant,
       ROUND(AVG(montant) OVER (PARTITION BY canal), 2)           AS moyenne_du_canal,
       ROUND(montant - AVG(montant) OVER (PARTITION BY canal), 2) AS ecart
FROM commandes
ORDER BY id_commande
LIMIT 6;
```
<!--sortie-->
```text
 id_commande    canal  montant  moyenne_du_canal  ecart
           1 Boutique     44.8             74.81 -30.01
           2     Site     34.5             59.50 -25.00
           3  Réseaux     88.2             49.01  39.19
           4  Réseaux     30.1             49.01 -18.91
           5 Boutique    110.1             74.81  35.29
           6     Site     39.8             59.50 -19.70
```

Chaque commande est toujours là, et trois colonnes se sont ajoutées. Par exemple, la commande n° 1 (boutique, 44,80 €) est 30,01 € **en dessous** du panier moyen de la boutique (74,81 €), alors que la commande n° 3 (Réseaux, 88,20 €) est 39,19 € **au-dessus** de celui du canal Réseaux (49,01 €). Une commande de 88 € est « grosse » sur le canal Réseaux mais « moyenne » en boutique : l'écart à son propre canal est plus parlant que le montant brut.

La syntaxe est toujours : **`fonction(...) OVER ( PARTITION BY ... ORDER BY ... cadre )`**.

| Morceau | Rôle | Analogie |
|---|---|---|
| `fonction(...)` | le calcul (`AVG`, `SUM`, `RANK`, `LAG`...) | ce qu'on mesure |
| `PARTITION BY` | découpe en **groupes indépendants** (facultatif ; sans lui, une seule partition = toute la table) | « à l'intérieur de chaque canal » |
| `ORDER BY` | **ordonne** les lignes dans chaque partition | « du plus ancien au plus récent » |
| cadre (`ROWS BETWEEN ...`) | quelles lignes voisines sont prises en compte pour la ligne courante | « les 3 dernières lignes » |

> 📐 **Définition précise.** Pour **chaque ligne** $r$, la base détermine sa **partition** $P(r)$ (les lignes qui ont la même valeur de `PARTITION BY`), les trie selon `ORDER BY`, puis retient un **cadre** $F(r)\subseteq P(r)$ (par exemple « de la première ligne de la partition jusqu'à $r$ »). Le résultat de la ligne $r$ est $f\bigl(F(r)\bigr)$ : la fonction appliquée à ce sous-ensemble. `GROUP BY` est le cas dégénéré où toutes les lignes d'une partition reçoivent **le même** résultat, qu'on réduit alors à une ligne. Le nombre de lignes du résultat d'une fenêtre, lui, est **le même** qu'en entrée.

### 5.3.2 Les classements : `ROW_NUMBER`, `RANK`, `DENSE_RANK`

Trois fonctions numérotent les lignes d'une partition, selon l'ordre demandé. Elles diffèrent **seulement** par leur façon de traiter les **ex æquo**. Un exemple minimal, avec un classement de cinq clients selon leur note de satisfaction (deux notes à 5, deux à 3), construit directement avec `VALUES` :

```sql
WITH notes(client, note) AS (
    VALUES ('Léa', 5), ('Noé', 5), ('Mia', 4), ('Hugo', 3), ('Zoé', 3)
)
SELECT client, note,
       ROW_NUMBER() OVER (ORDER BY note DESC) AS row_number,
       RANK()       OVER (ORDER BY note DESC) AS rank,
       DENSE_RANK() OVER (ORDER BY note DESC) AS dense_rank
FROM notes;
```
<!--sortie-->
```text
client  note  row_number  rank  dense_rank
   Léa     5           1     1           1
   Noé     5           2     1           1
   Mia     4           3     3           2
  Hugo     3           4     4           3
   Zoé     3           5     4           3
```

Lisez-le colonne par colonne :

- `ROW_NUMBER` : 1, 2, 3, 4, 5. Aucun ex æquo n'est reconnu : le départage entre Léa et Noé est **arbitraire** (si vous voulez un résultat reproductible, ajoutez un second critère d'ordre).
- `RANK` : 1, 1, 3, 4, 4. Les ex æquo partagent le même rang, et **le rang suivant saute** (comme aux Jeux olympiques : deux médailles d'or, pas d'argent, puis le bronze).
- `DENSE_RANK` : 1, 1, 2, 3, 3. Les rangs sont **consécutifs**, sans trou.

(Au passage : `WITH notes(...) AS (...)` est une **CTE**, nous l'étudions au 5.3.5.) Voici un cas réel : le classement des **trois plus grosses commandes de chaque canal**. Le plus naturel serait d'écrire `WHERE ROW_NUMBER() OVER (...) <= 3`, mais c'est **interdit** : le `WHERE` s'exécute *avant* le calcul des fenêtres (voir l'ordre d'exécution au 5.2.1). On calcule donc le rang dans une requête intérieure, et on filtre dans la requête extérieure :

```sql
SELECT canal, rang, id_commande, date_commande, montant
FROM (
    SELECT canal, id_commande, date_commande, montant,
           ROW_NUMBER() OVER (PARTITION BY canal ORDER BY montant DESC) AS rang
    FROM commandes
)
WHERE rang <= 3
ORDER BY canal, rang;
```
<!--sortie-->
```text
   canal  rang  id_commande date_commande  montant
Boutique     1          243    2025-08-26    212.4
Boutique     2          362    2025-12-16    208.8
Boutique     3          115    2025-05-15    189.2
 Réseaux     1          140    2025-06-10    166.1
 Réseaux     2           59    2025-03-27    159.9
 Réseaux     3          125    2025-05-23    127.3
    Site     1          157    2025-06-23    255.7
    Site     2           61    2025-03-28    243.8
    Site     3          208    2025-07-31    217.1
```

Ce motif (**« top N par groupe »**) est l'un des plus fréquents en entretien d'embauche comme en entreprise : « les 3 meilleurs vendeurs par région », « le dernier achat de chaque client » (`ROW_NUMBER() ... ORDER BY date DESC`, puis `rang = 1`).

### 5.3.3 Cumuls et moyennes mobiles : le cadre de la fenêtre

Ajoutons `ORDER BY` dans la fenêtre d'une somme : on obtient une **somme cumulée**. Voici l'évolution du chiffre d'affaires mensuel : le total mois par mois, le **cumul depuis janvier**, et une **moyenne mobile sur trois mois** (le mois courant et les deux précédents), qui lisse les fluctuations pour mieux voir la tendance.

```sql
WITH mensuel AS (
    SELECT strftime('%Y-%m', date_commande) AS mois,
           ROUND(SUM(montant))              AS ca
    FROM commandes
    GROUP BY mois
)
SELECT mois, ca,
       SUM(ca) OVER (ORDER BY mois)                                        AS cumul,
       ROUND(AVG(ca) OVER (ORDER BY mois ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)) AS moyenne_mobile_3_mois
FROM mensuel
ORDER BY mois;
```
<!--sortie-->
```text
   mois     ca   cumul  moyenne_mobile_3_mois
2025-01  996.0   996.0                  996.0
2025-02 1168.0  2164.0                 1082.0
2025-03 1687.0  3851.0                 1284.0
2025-04 1843.0  5694.0                 1566.0
2025-05 2314.0  8008.0                 1948.0
2025-06 2491.0 10499.0                 2216.0
2025-07 2571.0 13070.0                 2459.0
2025-08 2435.0 15505.0                 2499.0
2025-09 1713.0 17218.0                 2240.0
2025-10 1272.0 18490.0                 1807.0
2025-11 2284.0 20774.0                 1756.0
2025-12 3325.0 24099.0                 2294.0
```

La clause **`ROWS BETWEEN 2 PRECEDING AND CURRENT ROW`** définit le cadre : « les deux lignes précédentes plus la ligne courante ». En janvier, il n'y a pas de ligne précédente : la « moyenne sur trois mois » n'utilise qu'une valeur (996), puis deux en février. Dans un rapport sérieux, on masquerait ces deux premières valeurs.

![À gauche : chiffre d'affaires mensuel de la boutique en 2025 (barres) et sa moyenne mobile sur trois mois (courbe orange). À droite : chiffre d'affaires cumulé depuis janvier. Les données sont celles de la requête précédente.](figures/ch05-ca-mensuel.png)

Le graphique fait apparaître ce que les chiffres cachent : la moyenne mobile (courbe orange) gomme le creux d'octobre et la remontée de décembre, mais montre bien la **tendance** : une montée jusqu'à l'été, un repli à l'automne, puis un rebond de fin d'année. Le cumul atteint 24 099 € en décembre (à l'arrondi près : chaque mois a été arrondi au euro avant d'être additionné ; le vrai total est 24 098,30 €, comme le montre le graphique de droite).

> ⚠️ **Piège des ex æquo avec `ORDER BY`.** Quand on écrit `SUM(...) OVER (ORDER BY ...)` **sans** préciser de cadre, le cadre par défaut est `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW`, et `RANGE` regroupe toutes les lignes **ex æquo** sur la colonne de tri : elles reçoivent le **même** cumul. Illustration sur les six premières commandes, dont deux (n° 2 et n° 3) sont du même jour :

```sql
SELECT id_commande, date_commande, montant,
       SUM(montant) OVER (ORDER BY date_commande)                                         AS cumul_range,
       SUM(montant) OVER (ORDER BY date_commande, id_commande ROWS UNBOUNDED PRECEDING)  AS cumul_ligne_a_ligne
FROM commandes
WHERE id_commande <= 6
ORDER BY date_commande, id_commande;
```
<!--sortie-->
```text
 id_commande date_commande  montant  cumul_range  cumul_ligne_a_ligne
           1    2025-01-03     44.8         44.8                 44.8
           2    2025-01-04     34.5        167.5                 79.3
           3    2025-01-04     88.2        167.5                167.5
           4    2025-01-05     30.1        197.6                197.6
           5    2025-01-08    110.1        307.7                307.7
           6    2025-01-09     39.8        347.5                347.5
```

Les commandes 2 et 3 (même jour) affichent le **même** `cumul_range` : la somme des deux d'un coup, ce qui n'est pas un « cumul ligne à ligne ». Pour un cumul ligne à ligne, précisez toujours **`ROWS`** et un ordre complet (qui départage les ex æquo, ici par `id_commande`). C'est une des rares occasions où une fenêtre sans cadre explicite donne un résultat inattendu.

### 5.3.4 Comparer avec la ligne précédente : `LAG` et `LEAD`

`LAG(colonne)` renvoie la valeur de la ligne **précédente** (dans l'ordre de la fenêtre) ; `LEAD(colonne)`, de la ligne **suivante**. C'est l'outil des évolutions : « par rapport au mois dernier », « depuis la dernière commande ». Commençons par la **croissance mensuelle du chiffre d'affaires**, en pourcentage :

```sql
WITH mensuel AS (
    SELECT strftime('%Y-%m', date_commande) AS mois,
           ROUND(SUM(montant))              AS ca
    FROM commandes
    GROUP BY mois
)
SELECT mois, ca,
       LAG(ca) OVER (ORDER BY mois)                                              AS mois_precedent,
       ROUND(100.0 * (ca - LAG(ca) OVER (ORDER BY mois)) / LAG(ca) OVER (ORDER BY mois), 1) AS evolution_pct
FROM mensuel
ORDER BY mois;
```
<!--sortie-->
```text
   mois     ca  mois_precedent  evolution_pct
2025-01  996.0             NaN            NaN
2025-02 1168.0           996.0           17.3
2025-03 1687.0          1168.0           44.4
2025-04 1843.0          1687.0            9.2
2025-05 2314.0          1843.0           25.6
2025-06 2491.0          2314.0            7.6
2025-07 2571.0          2491.0            3.2
2025-08 2435.0          2571.0           -5.3
2025-09 1713.0          2435.0          -29.7
2025-10 1272.0          1713.0          -25.7
2025-11 2284.0          1272.0           79.6
2025-12 3325.0          2284.0           45.6
```

La première ligne n'a pas de précédent : `LAG` renvoie `NULL` (que pandas affiche `NaN`). Les plus fortes hausses sont en novembre (+79,6 %), en décembre (+45,6 %) et en mars (+44,4 %), la plus forte baisse en septembre (−29,7 %).

Une deuxième utilisation, plus riche : **le délai entre deux commandes successives du même client**. `LAG(date_commande)` calculé *dans la partition du client* donne la date de sa commande précédente (les dates sont en texte ISO, `julianday` les convertit en nombres de jours). Combien de jours séparent en moyenne deux achats successifs d'un même client ? Nous calculons d'abord les intervalles, puis nous les résumons :

```sql
WITH achats AS (
    SELECT id_client, date_commande,
           LAG(date_commande) OVER (PARTITION BY id_client ORDER BY date_commande, id_commande) AS precedente
    FROM commandes
)
SELECT COUNT(*)                                                      AS intervalles,
       ROUND(AVG(julianday(date_commande) - julianday(precedente)), 1) AS delai_moyen_jours,
       MIN(julianday(date_commande) - julianday(precedente))         AS minimum,
       MAX(julianday(date_commande) - julianday(precedente))         AS maximum
FROM achats
WHERE precedente IS NOT NULL;
```
<!--sortie-->
```text
 intervalles  delai_moyen_jours  minimum  maximum
         334               40.2      0.0    320.0
```

334 intervalles : 400 commandes moins 66 « premières commandes » (une par client actif, qui n'ont pas de précédente). En moyenne, **40 jours** séparent deux achats d'un même client, avec des extrêmes allant de 0 (deux commandes le même jour) à 320 jours. C'est exactement l'ingrédient d'un indicateur classique du commerce : le **cycle de réachat**. Il guide, par exemple, la date idéale d'un courriel de relance : passé 40 jours sans achat, un client est déjà « en retard » par rapport à la normale.

### 5.3.5 Les CTE : donner un nom à une étape

Vous les avez déjà croisées dans ce chapitre. Une **CTE** (*Common Table Expression*) est une requête **nommée**, déclarée en tête avec `WITH nom AS ( ... )`, que l'on utilise ensuite comme si c'était une table. Elle ne change **rien** au résultat par rapport à une sous-requête imbriquée (5.2.6) : elle change la **lisibilité**. Comparez, pour la même question, l'imbrication :

```text
SELECT ... FROM (SELECT ... FROM (SELECT ... FROM commandes GROUP BY ...) GROUP BY ...) WHERE ...
```

et le découpage en étapes nommées :

```text
WITH etape1 AS (SELECT ... FROM commandes GROUP BY ...),
     etape2 AS (SELECT ... FROM etape1 ...)
SELECT ... FROM etape2 WHERE ...
```

La deuxième forme se lit **de haut en bas**, comme un script : on peut vérifier chaque étape isolément, ce qui est précieux pour le débogage. On peut enchaîner plusieurs CTE (séparées par des virgules) ; chacune peut utiliser celles qui précèdent.

Deux remarques pratiques. **(1)** Une CTE n'est visible que **dans la requête** qui la déclare : elle n'est pas enregistrée dans la base (pour cela, il existe les vues, 5.4.4). **(2)** Rien n'oblige à découper : une requête simple n'a pas besoin de CTE. La règle est celle de la lisibilité : dès que vous imbriquez deux niveaux de sous-requêtes, ou que vous avez besoin d'utiliser le même résultat intermédiaire à deux endroits, nommez l'étape.

### 5.3.6 Les CTE récursives : des requêtes qui se rappellent elles-mêmes

Une CTE peut **se référencer elle-même** : c'est une CTE **récursive** (`WITH RECURSIVE`). Elle comporte toujours deux parties reliées par `UNION ALL` : un **cas de base** (le point de départ) et un **pas récursif** (comment passer de la ligne précédente à la suivante), avec une condition d'arrêt. Comme en Python, il faut un cas de base *et* une condition d'arrêt, faute de quoi la requête tourne sans fin.

L'exemple le plus simple : générer les carrés des entiers de 1 à 5.

```sql
WITH RECURSIVE n(i) AS (
    SELECT 1                                  -- cas de base : on part de 1
    UNION ALL
    SELECT i + 1 FROM n WHERE i < 5           -- pas : on ajoute 1, tant que i < 5
)
SELECT i, i * i AS carre FROM n;
```
<!--sortie-->
```text
 i  carre
 1      1
 2      4
 3      9
 4     16
 5     25
```

La base procède ainsi : elle écrit la ligne `1` ; pour chaque ligne nouvellement produite, elle applique le pas (`1` donne `2`, `2` donne `3`...) jusqu'à ce que `WHERE i < 5` bloque la production.

**Premier usage, fabriquer un calendrier :** on génère *tous* les jours de l'année, puis on les joint aux commandes par un `LEFT JOIN` pour ne pas oublier les jours sans vente (sans lui, les moyennes quotidiennes seraient surestimées) ; c'est l'application 5.7 du cahier.

**Second usage : parcourir une hiérarchie.** La table `clients` contient le parrainage : un client peut avoir été parrainé par un autre, lui-même parrainé... C'est un **arbre**. À quelle profondeur ? Combien de filleuls (directs ou non) a chaque ambassadeur ? Une jointure ne peut parcourir qu'un nombre fixe de niveaux ; une CTE récursive les parcourt tous. Cas de base : les clients **sans parrain** (les « racines »). Pas : on ajoute leurs filleuls, puis les filleuls de leurs filleuls...

```sql
WITH RECURSIVE reseau(id_client, racine, profondeur) AS (
    SELECT id_client, id_client, 0 FROM clients WHERE id_parrain IS NULL
    UNION ALL
    SELECT c.id_client, r.racine, r.profondeur + 1
    FROM clients AS c JOIN reseau AS r ON c.id_parrain = r.id_client
)
SELECT r.racine, cl.prenom || ' ' || cl.nom AS ambassadeur,
       COUNT(*) - 1 AS filleuls, MAX(r.profondeur) AS generations
FROM reseau AS r JOIN clients AS cl ON cl.id_client = r.racine
GROUP BY r.racine ORDER BY filleuls DESC LIMIT 4;
```
<!--sortie-->
```text
 racine  ambassadeur  filleuls  generations
     10   Lou Michel         5            4
      7  Paul Martin         4            3
      1 Yann Lambert         4            3
      5  Anna Michel         3            3
```

Le premier réseau est celui du client n° 10 : **5 filleuls répartis sur 4 générations**. (`COUNT(*) - 1` : on ne compte pas la racine elle-même.) L'application 5.8 du cahier affiche la chaîne complète de parrainage de chaque membre (un « chemin » recollé le long de l'arbre) et calcule le chiffre d'affaires généré par un réseau, base d'une prime au parrainage.

> ⚠️ **Récursion et sécurité.** Si le parrainage contenait un **cycle** (A parraine B qui parraine A), la récursion tournerait indéfiniment. Ici c'est impossible, puisqu'un parrain a toujours un numéro plus petit, donc une inscription plus ancienne, que son filleul (nous l'avons garanti à la construction de la base, 5.1.3), mais, sur des données réelles, ajoutez toujours une **condition d'arrêt** (profondeur maximale, par exemple `WHERE profondeur < 10`). C'est l'équivalent du `while` qui ne se termine jamais.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.6 (segmentation RFM avec `NTILE`), 5.7 (un calendrier complet) et 5.8 (réseau de parrainage), exercices 5.8 à 5.10.

> ✅ **À retenir**
>
> - Une fonction **fenêtre** (`... OVER (PARTITION BY ... ORDER BY ...)`) calcule sur un groupe de lignes **sans réduire** leur nombre ; `GROUP BY` les réduit.
> - **Classements** : `ROW_NUMBER` (jamais d'ex æquo), `RANK` (ex æquo et trous), `DENSE_RANK` (ex æquo sans trous). Le **top N par groupe** passe par une requête intérieure ou une CTE.
> - **Cumuls, moyennes mobiles** : `SUM/AVG(...) OVER (ORDER BY ... ROWS BETWEEN ...)`. Précisez `ROWS` pour éviter le piège des ex æquo.
> - **`LAG` / `LEAD`** donnent la valeur de la ligne précédente / suivante : évolutions et délais entre événements.
> - Une **CTE** (`WITH nom AS (...)`) nomme une étape et rend la requête lisible de haut en bas. Une CTE **récursive** (`WITH RECURSIVE`) génère des suites (calendriers) et parcourt des hiérarchies (parrainage, organigrammes).


## 5.4 Normalisation et conception de schémas

> 💡 **Intuition.** Pourquoi avoir découpé les données de la boutique en cinq tables, au lieu d'un seul grand tableau, comme dans Excel ? Parce qu'un tableau unique **répète** les mêmes informations (la ville d'une cliente apparaît sur chacune de ses commandes), et que **tout ce qui est répété finit par se contredire**. La **normalisation** est la méthode qui consiste à ranger chaque fait **une seule fois**, à sa place. Cette section explique *pourquoi* le schéma du 5.1 est bon, et vous donne la méthode pour en concevoir un vous-même. Nous terminerons par deux sujets de **performance et de fiabilité** : les index et les transactions.

### 5.4.1 Le problème : la grande feuille unique

Imaginons que la gérante ait gardé son habitude du tableur : **une seule feuille** avec une ligne par article vendu, contenant tout ce qu'on sait sur la commande, la cliente et le produit. Fabriquons cette feuille pour les **huit premières commandes**, en recollant par jointures les cinq tables du 5.1 (nous créons pour cela dans la base des tables de travail préfixées `ex_`, supprimées à la fin de la section).


Voici un extrait de la feuille : les lignes des clients n° 3 et n° 5 (quelques colonnes seulement pour tenir en largeur).

```sql
SELECT id_commande, id_produit, id_client, prenom, ville, nom_produit, nom_categorie, quantite
FROM ex_feuille
WHERE id_client IN (3, 5)
ORDER BY id_commande, id_produit;
```
<!--sortie-->
```text
 id_commande  id_produit  id_client prenom   ville             nom_produit nom_categorie  quantite
           3           2          3   Adam Ville F        Bol en céramique       Poterie         1
           3           3          3   Adam Ville F    Vase peint à la main       Poterie         1
           3          13          3   Adam Ville F Savon à l'huile d'olive   Cosmétiques         1
           5           8          5   Anna Ville A         Pochette brodée       Textile         2
           5           9          5   Anna Ville A         Bague en argent        Bijoux         1
           5          15          5   Anna Ville A           Huile de soin   Cosmétiques         1
           8           4          5   Anna Ville A   Grand plat de service       Poterie         2
           8           5          5   Anna Ville A          Plaid en coton       Textile         1
```

Regardez la cliente n° 5, Anna Michel : elle apparaît sur **cinq lignes**, et sa ville « Ville A » est écrite cinq fois. Même chose pour le produit n° 9 (Bague en argent) et sa catégorie « Bijoux ». Cette redondance cause trois catégories de problèmes, appelées **anomalies**.

**1. Anomalie de mise à jour.** Anna déménage à Ville G. L'employé de la gérante ne corrige qu'**une** ligne sur cinq (il a oublié les autres) :

```sql
UPDATE ex_feuille SET ville = 'Ville G'
WHERE id_client = 5 AND id_commande = 8 AND id_produit = 5;
```

```sql
SELECT id_client, prenom, nom, ville, COUNT(*) AS lignes
FROM ex_feuille
WHERE id_client = 5
GROUP BY id_client, prenom, nom, ville;
```
<!--sortie-->
```text
 id_client prenom    nom   ville  lignes
         5   Anna Michel Ville A       4
         5   Anna Michel Ville G       1
```

Deux villes pour la même personne : on ne sait plus laquelle est vraie. C'est exactement l'histoire de « Léa Martin » du 5.1.1. Dans notre vraie base, cette erreur est **impossible** : la ville d'une cliente n'est écrite qu'à un seul endroit.

> ⚠️ **Une incohérence ne se résorbe pas toute seule.** Même un `SELECT DISTINCT id_client, ville` ne sait pas « choisir » la bonne ville : il renvoie les deux. Les doublons contradictoires sont de la **vraie** information fausse, que seul un humain peut trancher. Remettons la ville d'origine pour la suite, par un `UPDATE` inverse.


**2. Anomalie d'insertion.** La gérante veut ajouter au catalogue un nouveau produit, pas encore vendu. Impossible : la feuille n'a de place que pour des *lignes de commande*, et la clé primaire exige un numéro de commande. La base répond : `NOT NULL constraint failed: ex_feuille.id_commande`.


(Et en supprimant la contrainte, on aurait une ligne avec des trous partout.)

**3. Anomalie de suppression.** Quels produits n'apparaissent que sur **une seule** ligne de la feuille ? Pour ceux-là, supprimer cette ligne (par exemple parce que la commande est annulée) effacerait **toute trace du produit** : son nom, sa catégorie, son prix catalogue.

```sql
SELECT id_produit, nom_produit, prix_catalogue, MIN(id_commande) AS seule_commande
FROM ex_feuille
GROUP BY id_produit
HAVING COUNT(*) = 1
ORDER BY id_produit;
```
<!--sortie-->
```text
 id_produit             nom_produit  prix_catalogue  seule_commande
          1          Plat décoratif            45.0               1
          3    Vase peint à la main            65.0               3
          4   Grand plat de service            38.0               8
         10               Pendentif            35.0               2
         11      Bracelet de perles            15.0               4
         13 Savon à l'huile d'olive             6.0               3
         14            Eau parfumée            14.0               4
         15           Huile de soin            24.0               5
```

Annuler la commande n° 5 ferait disparaître l'huile de soin du catalogue : on a voulu supprimer *une vente* et on a perdu *un produit*.

Résumé : dans une table, **tout fait doit être associé à un seul sujet**. Un client, un produit, une commande et une vente sont quatre sujets différents ; les mélanger dans une même table provoque ces trois anomalies.

### 5.4.2 Dépendances fonctionnelles : la théorie derrière la normalisation

> 📐 **Définition.** Dans une table $R$ d'attributs $A$, on dit que $X$ **détermine fonctionnellement** $Y$, noté $X\to Y$ (avec $X,Y\subseteq A$), si deux lignes qui ont la **même valeur de $X$** ont **forcément la même valeur de $Y$** :
> $$\forall\,t_1,t_2\in R,\quad t_1[X]=t_2[X]\ \Longrightarrow\ t_1[Y]=t_2[Y].$$
> Exemples dans notre feuille : `id_client` $\to$ `ville` (un client n'a qu'une ville) ; `id_produit` $\to$ `prix_catalogue` ; mais **pas** `ville` $\to$ `id_client` (plusieurs clientes habitent Ville A).

Une clé primaire est un cas particulier : $K$ est une **clé** de $R$ si $K\to A$ (elle détermine *toutes* les colonnes) et si aucun sous-ensemble strict de $K$ n'en fait autant (minimalité).

Les dépendances fonctionnelles obéissent à trois règles, les **axiomes d'Armstrong** (1974), qui permettent d'en déduire d'autres :

1. **Réflexivité** : si $Y\subseteq X$, alors $X\to Y$ (trivial).
2. **Augmentation** : si $X\to Y$, alors $XZ\to YZ$ pour tout $Z$.
3. **Transitivité** : si $X\to Y$ et $Y\to Z$, alors $X\to Z$.

La **fermeture** $X^+$ d'un ensemble d'attributs est l'ensemble de tout ce qu'il détermine, directement ou par transitivité. On la calcule en partant de $X$ et en ajoutant les attributs déterminés tant que c'est possible. Appliquons-le à notre feuille. Les dépendances que nous croyons vraies (règles de gestion de la boutique) sont les cinq suivantes :

| Dépendance | Signification |
|---|---|
| `id_commande` → `date_commande`, `id_client` | une commande a une date et un client |
| `id_client` → `prenom`, `nom`, `ville` | un client a un nom et une ville |
| `id_produit` → `nom_produit`, `id_categorie`, `prix_catalogue` | un produit a un nom, une catégorie, un prix |
| `id_categorie` → `nom_categorie` | une catégorie a un nom |
| (`id_commande`, `id_produit`) → `quantite`, `prix_unitaire` | une ligne est identifiée par le couple |

Pour la fermeture, l'algorithme est celui du point fixe : on part de $X$, et tant qu'une dépendance dont le membre gauche est déjà inclus apporte de nouveaux attributs, on les ajoute. (Un court programme l'exécute en coulisses sur la feuille.)


Avant de s'en servir, vérifions que ces dépendances sont **respectées par les données** de la feuille : pour chaque dépendance $X\to Y$, aucun groupe de lignes de même $X$ ne doit contenir deux valeurs différentes de $Y$.


Le test confirme que les cinq dépendances sont respectées ; les deux « fausses » dépendances (`ville` $\to$ `id_client`, `id_commande` $\to$ `prix_unitaire`) sont **contredites** par les données, comme prévu. Attention à la nuance logique : un jeu de données peut seulement **réfuter** une dépendance (une paire de lignes suffit), jamais la **démontrer** ; seule la connaissance du métier (« un client n'a qu'une ville de livraison par défaut ») l'affirme.

Calculons maintenant des fermetures et cherchons la clé de la feuille. La fermeture de {`id_client`} est {`id_client`, `prenom`, `nom`, `ville`} ; celle de {`id_commande`} ajoute la date et le client (`date_commande`, `id_client`) et, par transitivité, ses `prenom`, `nom` et `ville`. La seule clé candidate est le couple (`id_commande`, `id_produit`) :


La seule clé est le couple (`id_commande`, `id_produit`) : c'est la clé primaire que nous avions déclarée. Le calcul explique aussi l'origine des anomalies : beaucoup d'attributs dépendent seulement d'**une partie** de la clé (`prenom`, `ville`... dépendent de `id_commande` seul ; `nom_produit`, `prix_catalogue`... de `id_produit` seul), ou d'un attribut qui n'est pas la clé (`ville` dépend de `id_client`, qui dépend de `id_commande`). On a trouvé la source du mal. Il reste à la soigner.

### 5.4.3 Les trois premières formes normales

Les **formes normales** sont des niveaux de « propreté » d'un schéma, chaque niveau supprimant un type de redondance. Retenez la formule qui résume les trois premières, dans l'esprit du serment d'un témoin au tribunal : *chaque attribut dépend de **la clé, de toute la clé, et rien que de la clé*** (« so help me Codd »).

| Forme | Exigence | Anomalie évitée |
|---|---|---|
| **1FN** | chaque case contient **une seule valeur** (atomique) ; pas de listes ni de colonnes répétées | cases du type « Plat ; Plaid » |
| **2FN** | 1FN **et** aucun attribut ne dépend d'une **partie** de la clé (utile quand la clé est composite) | informations sur le produit répétées sur chaque vente |
| **3FN** | 2FN **et** aucun attribut non-clé ne dépend d'un **autre attribut non-clé** (pas de dépendance transitive) | ville du client recopiée parce que `id_client` détermine `ville` |

**1FN.** Si la gérante avait noté le panier dans une seule case (`articles = "Plaid en coton ; Pochette brodée"`), elle n'aurait pu ni compter les ventes par produit, ni les joindre au catalogue : on ne sait pas jointer un morceau de texte. La solution est **une ligne par article** : c'est ce que fait notre feuille, qui est donc déjà en 1FN (et nous aurions eu le même problème avec des colonnes `produit1`, `produit2`, `produit3`).

**2FN.** La clé de la feuille est composite (`id_commande`, `id_produit`). Or les infos du produit ne dépendent que de `id_produit`, et celles de la commande que de `id_commande` : ce sont des **dépendances partielles**. On découpe : chaque groupe d'attributs va dans une table dont la clé est l'attribut qui le détermine.

```sql
CREATE TABLE ex_lignes AS
SELECT id_commande, id_produit, quantite, prix_unitaire FROM ex_feuille;

CREATE TABLE ex_commandes AS
SELECT DISTINCT id_commande, date_commande, id_client, prenom, nom, ville FROM ex_feuille;

CREATE TABLE ex_produits AS
SELECT DISTINCT id_produit, nom_produit, id_categorie, nom_categorie, prix_catalogue FROM ex_feuille;
```

(`DISTINCT` supprime les doublons : chaque commande et chaque produit n'est plus écrit qu'une fois.) La redondance a déjà fortement baissé, mais elle n'a pas disparu : dans `ex_commandes`, la ville d'Anna est encore écrite pour **chacune** de ses commandes (n° 5 et n° 8). Cause : `id_commande` $\to$ `id_client` $\to$ `ville` : c'est une **dépendance transitive**.

**3FN.** On extrait ce qui dépend d'un attribut non-clé dans sa propre table : les clients (clé `id_client`) d'un côté, les catégories (clé `id_categorie`) de l'autre.

```sql
CREATE TABLE ex_clients AS
SELECT DISTINCT id_client, prenom, nom, ville FROM ex_commandes;

CREATE TABLE ex_categories AS
SELECT DISTINCT id_categorie, nom_categorie FROM ex_produits;

CREATE TABLE ex_commandes3 AS
SELECT DISTINCT id_commande, date_commande, id_client FROM ex_commandes;

CREATE TABLE ex_produits3 AS
SELECT DISTINCT id_produit, nom_produit, id_categorie, prix_catalogue FROM ex_produits;
```

Comptons les lignes de chaque table pour voir la différence (un comptage fait en coulisses) : la grande feuille de 16 lignes devient cinq tables : 16 lignes de commande, 8 commandes, 7 clients, 12 produits et 4 catégories.


La grande feuille est devenue cinq petites tables : exactement la structure du 5.1 ! La normalisation est ce qui a conduit à notre schéma, et un dessin préalable des entités (5.1.2) aurait donné le même résultat plus vite. Les anomalies ont disparu : changer la ville d'Anna se fait par **un seul** `UPDATE` sur **une seule** ligne ; ajouter un produit au catalogue est un simple `INSERT` dans `produits` ; supprimer une vente laisse produit et client intacts.

> 💡 **Le test de sécurité : « décomposer sans rien perdre ».** Découper une table en plusieurs ne doit pas **perdre d'information**. Vérifions que, si l'on recolle les morceaux par des jointures, on retrouve **exactement** la feuille d'origine, ni plus ni moins. On recolle les cinq petites tables par des jointures (5.2.5) et on compare dans les deux sens avec `EXCEPT` : les lignes reconstituées absentes de la feuille, puis l'inverse (le contrôle est exécuté en coulisses).


Le contrôle renvoie zéro et zéro : la décomposition est **sans perte**. (Et grâce à la remarque du 5.4.1 sur la ville d'Anna, nous avons pris soin de remettre la feuille en état avant de la découper : normaliser des données **déjà contradictoires** aurait recopié fidèlement la contradiction dans la table `ex_clients`, avec deux lignes pour la même cliente. Un schéma normalisé rend les *nouvelles* incohérences impossibles, par exemple en déclarant `id_client` clé primaire de `clients`, mais ne répare pas les anciennes.)

> 📐 **Pourquoi la décomposition sans perte fonctionne (théorème de Heath).** Soit $R(X,Y,Z)$ une table avec la dépendance $X\to Y$. Alors $R=\pi_{X,Y}(R)\bowtie\pi_{X,Z}(R)$. *Preuve.* L'inclusion $R\subseteq\pi_{XY}(R)\bowtie\pi_{XZ}(R)$ est évidente (toute ligne se retrouve en recollant ses propres morceaux). Réciproquement, soit $(x,y,z)$ dans la jointure : $(x,y)$ vient d'une ligne $(x,y,z')\in R$ et $(x,z)$ d'une ligne $(x,y',z)\in R$. Ces deux lignes ont la **même valeur $x$**, donc, comme $X\to Y$, la **même valeur $y=y'$**. La ligne $(x,y',z)=(x,y,z)$ est donc dans $R$. $\square$ Sans la dépendance, la jointure pourrait fabriquer de **fausses lignes** : c'est le piège de la décomposition faite « au feeling ».

Pour finir proprement, nos tables de travail sont supprimées en coulisses (pour que la base redevienne celle du 5.1).


### 5.4.4 Aller plus loin, ou s'arrêter plus tôt ?

**La forme normale de Boyce-Codd (BCNF)** renforce la 3FN : pour *toute* dépendance $X\to Y$ non triviale, $X$ doit être une clé. Dans la pratique, la 3FN suffit presque toujours, et un schéma en 3FN est souvent déjà en BCNF. Il existe des formes supérieures (4FN, 5FN) pour des cas plus rares.

**Mais attention : « plus normalisé » n'est pas toujours « mieux ».** Un schéma normalisé est idéal pour **enregistrer** des données (les systèmes *transactionnels*, dits **OLTP** : caisse, site de vente, réservations) : peu de redondance, mises à jour sûres. Pour **analyser** (les systèmes **OLAP** : entrepôts de données, tableaux de bord), l'analyste doit en revanche joindre cinq tables pour la moindre question, ce qui est lent et fastidieux. On **dénormalise** donc volontairement dans les entrepôts, par exemple avec un **schéma en étoile** : au centre, une grosse table de **faits** (les ventes : une ligne par article vendu, avec des montants et des clés), autour d'elle de petites tables de **dimensions** (client, produit, date) qui décrivent le contexte. Notre `lignes_commande` entourée de `commandes`, `produits`, `clients` ressemble déjà à une étoile.

Règle pratique : **normalisez pour écrire, dénormalisez pour lire**. En attendant de construire un entrepôt, une **vue** donne à l'analyste une « grande table » toute prête, sans dupliquer les données : une vue est une **requête enregistrée sous un nom**, qu'on interroge comme une table.

```sql
CREATE VIEW v_ventes AS
SELECT l.id_commande, c.date_commande, c.canal, c.satisfaction,
       cl.id_client, cl.ville,
       ca.nom AS categorie, p.nom AS produit,
       l.quantite, l.prix_unitaire, l.quantite * l.prix_unitaire AS montant_ligne
FROM lignes_commande AS l
JOIN commandes  AS c  ON c.id_commande  = l.id_commande
JOIN clients    AS cl ON cl.id_client   = c.id_client
JOIN produits   AS p  ON p.id_produit   = l.id_produit
JOIN categories AS ca ON ca.id_categorie = p.id_categorie;
```

```sql
SELECT categorie, canal, ROUND(SUM(montant_ligne)) AS chiffre_affaires
FROM v_ventes
GROUP BY categorie, canal
ORDER BY categorie, canal;
```
<!--sortie-->
```text
  categorie    canal  chiffre_affaires
     Bijoux Boutique            2256.0
     Bijoux  Réseaux            1914.0
     Bijoux     Site            2836.0
Cosmétiques Boutique             878.0
Cosmétiques  Réseaux            1099.0
Cosmétiques     Site            1170.0
    Poterie Boutique            2397.0
    Poterie  Réseaux            2143.0
    Poterie     Site            2410.0
    Textile Boutique            2997.0
    Textile  Réseaux            1607.0
    Textile     Site            2390.0
```

Une requête qui exigeait quatre jointures tient maintenant en trois lignes, et la vue peut évoluer (changer de définition) sans que les analystes changent leurs requêtes.

### 5.4.5 Les index : retrouver une ligne sans tout lire

Quand on écrit `WHERE id_client = 2`, comment la base trouve-t-elle les commandes du client ? Sans aide, elle doit **lire toutes les lignes** de la table, une par une (un *balayage complet*, ou *full scan*). Avec 400 lignes, c'est instantané ; avec 100 millions, c'est insupportable. Un **index** est une structure annexe, triée, comparable à l'**index alphabétique à la fin d'un livre** : au lieu de feuilleter tout l'ouvrage pour trouver « Khi-deux », on consulte l'index qui renvoie à la bonne page. Techniquement c'est le plus souvent un **arbre B** (*B-tree*) : on trouve une valeur parmi $N$ en environ $\log_2 N$ comparaisons au lieu de $N$.

Pour $N=500\,000$, c'est $\log_2 N\approx19$ comparaisons contre 500 000 : un facteur **plus de 25 000**. On peut demander à la base **comment elle compte exécuter** une requête, avec `EXPLAIN QUERY PLAN` (c'est le premier outil de l'analyste qui s'occupe de performance) :

```sql noexec
-- On demande à la base comment elle compte exécuter la requête, puis on crée l'index :
EXPLAIN QUERY PLAN SELECT * FROM commandes WHERE id_client = 2;
CREATE INDEX idx_commandes_client ON commandes(id_client);
```

```text
Avant l'index :
   SCAN commandes
Après CREATE INDEX :
   SEARCH commandes USING INDEX idx_commandes_client (id_client=?)
Recherche par la clé primaire (index automatique) :
   SEARCH commandes USING INTEGER PRIMARY KEY (rowid=?)
Filtre sur une colonne non indexée :
   SCAN commandes
```

`SCAN` signifie « lire toute la table » ; `SEARCH ... USING INDEX` signifie « chercher via l'arbre ». La clé primaire est **toujours** indexée automatiquement ; c'est aussi pourquoi les clés étrangères mal indexées sont une cause classique de lenteur. Le filtre sur `montant` reste un `SCAN` : aucun index ne l'aide.

Pour mesurer le gain « pour de vrai », nous construisons en coulisses une table de **500 000 lignes** (par une CTE récursive, 5.3.6) et chronométrons la même recherche avant et après un index (l'application 5.9 du cahier refait l'expérience pas à pas). Les durées exactes dépendent de votre machine ; nous n'affichons donc que le **facteur de gain**, arrondi à la puissance de dix inférieure, pour que le résultat reste le même d'une exécution à l'autre.

```text
lignes dans la table : 500000
gain au moins égal à : 100 fois
```

Chez nous, le gain dépasse un facteur cent (et la précision de l'affichage est volontairement grossière, pour rester reproductible) : voilà pourquoi les index sont **la** première optimisation. Mais ils ne sont pas gratuits : un index occupe de la place, et il doit être **mis à jour à chaque insertion ou modification**, ce qui ralentit l'écriture. Règle d'usage : indexer les colonnes **souvent utilisées dans un `WHERE` ou un `JOIN`** (surtout les clés étrangères) et ne pas indexer à tout va. Notez enfin que les index peuvent changer le **temps** d'une requête, **jamais son résultat**.

### 5.4.6 Les transactions : tout ou rien

Enregistrer une commande, c'est plusieurs écritures : une ligne dans `commandes`, puis une ligne par article dans `lignes_commande` (et, dans un vrai système, la mise à jour du stock). Que se passe-t-il si le courant saute **entre** deux de ces écritures ? On aurait une commande **sans** articles : une base incohérente. Une **transaction** regroupe plusieurs opérations en un bloc **indivisible** : soit toutes réussissent (`COMMIT`), soit aucune n'a d'effet (`ROLLBACK`). On résume les garanties d'une transaction par l'acronyme **ACID** :

| Lettre | Garantie | Signification |
|---|---|---|
| **A**tomicité | tout ou rien | si une étape échoue, tout est annulé |
| **C**ohérence | les règles tiennent toujours | les contraintes (clés, `CHECK`) sont respectées avant et après |
| **I**solation | pas d'interférence | deux transactions simultanées ne voient pas les états intermédiaires l'une de l'autre |
| **D**urabilité | c'est définitif | une fois validée, la modification survit à une panne |

Voyons l'atomicité en action. On tente d'enregistrer une commande dont la **deuxième** étape échoue (un produit n° 999 qui n'existe pas) :

```python
def nb_commandes():
    return con.execute("SELECT COUNT(*) FROM commandes").fetchone()[0]

print("avant :", nb_commandes(), "commandes")
try:
    with con:                                   # ouvre une transaction ; ROLLBACK automatique si exception
        con.execute("INSERT INTO commandes VALUES (9001, 1, '2025-12-31', 'Site', 80, 3, 5)")
        print("pendant la transaction :", nb_commandes(), "commandes (la nouvelle est visible pour nous)")
        con.execute("INSERT INTO lignes_commande VALUES (9001, 999, 1, 80)")   # produit inexistant : échec
except sqlite3.IntegrityError as erreur:
    print("échec :", erreur)
print("après  :", nb_commandes(), "commandes")
```
<!--sortie-->
```text
avant : 400 commandes
pendant la transaction : 401 commandes (la nouvelle est visible pour nous)
échec : FOREIGN KEY constraint failed
après  : 400 commandes
```

La commande n° 9001, pourtant bien insérée à l'étape 1, a **disparu** : l'échec de l'étape 2 a annulé toute la transaction. Sans transaction, on aurait gardé une commande fantôme sans article. Dans le bloc `with con:`, Python déclenche un `COMMIT` si tout se passe bien, un `ROLLBACK` à la première exception.

> 🧪 **Pourquoi l'isolation compte.** Deux caissiers enregistrent en même temps la vente du dernier exemplaire d'un vase. Sans isolation, chacun lit « stock = 1 », chacun vend, et le stock tombe à −1. Avec une transaction isolée, la seconde attend (ou échoue) et lit « stock = 0 ». Les SGBD offrent plusieurs **niveaux d'isolation**, du plus laxiste au plus strict, avec un compromis entre sécurité et vitesse ; le détail dépasse ce chapitre, mais retenez que les bases relationnelles gèrent pour vous un problème que les fichiers CSV ignorent complètement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : application 5.9 (mesurer le gain d'un index), exercice 5.11 (dépendances fonctionnelles et décomposition en 3FN).

> ✅ **À retenir**
>
> - Une table qui mélange plusieurs sujets provoque des **anomalies** de mise à jour, d'insertion et de suppression.
> - Une **dépendance fonctionnelle** $X\to Y$ dit que $X$ détermine $Y$. La fermeture $X^+$ permet de trouver les **clés**. Les données peuvent **réfuter** une dépendance, pas la prouver.
> - **1FN** : cases atomiques. **2FN** : rien ne dépend d'une partie de la clé. **3FN** : rien ne dépend d'un non-clé. Formule : « la clé, toute la clé, et rien que la clé ».
> - Une décomposition doit être **sans perte** (théorème de Heath). Normaliser ne répare pas des données déjà contradictoires.
> - **Normalisez pour écrire, dénormalisez pour lire** (OLTP contre OLAP, schéma en étoile, vues).
> - Un **index** accélère les recherches (de $N$ à $\log N$ comparaisons) au prix de l'espace et de l'écriture ; `EXPLAIN QUERY PLAN` montre si la base lit tout (`SCAN`) ou utilise l'index (`SEARCH`).
> - Une **transaction** est un bloc « tout ou rien » (ACID).


## 5.5 ➕ Pour aller plus loin : les bases NoSQL (MongoDB, Redis)

> 🧭 **Section optionnelle.** Le reste du livre ne dépend pas de cette section. Elle vous donne la carte du territoire « au-delà du relationnel », utile si vous lisez des offres d'emploi (MongoDB, Redis, Cassandra, Neo4j y sont souvent cités) ou si un projet vous met un jour devant l'une de ces bases.

> ⚠️ **Honnêteté sur l'exécution.** MongoDB et Redis sont des **serveurs** qui ne sont pas installés dans l'environnement qui a servi à fabriquer ce livre. Les commandes qui leur sont destinées sont donc marquées **non exécutées** : elles n'ont pas de sortie, et nous ne prétendons pas en avoir vu une. À la place, nous reproduisons leur **logique** avec du Python et du JSON, exécutés, de sorte que vous puissiez voir *à quoi ressemblent* les données et les requêtes.

> 💡 **Intuition.** « NoSQL » signifie « *Not only SQL* » (« pas seulement SQL »). Ce n'est pas *un* modèle, mais une famille de bases nées dans les années 2000 chez des géants du web (Google, Amazon, Facebook), qui avaient des besoins pour lesquels les bases relationnelles étaient mal adaptées : des **milliards** d'enregistrements répartis sur des **centaines de machines**, des données de **formes variées** qui changent sans cesse, des temps de réponse de **quelques millisecondes**.

### 5.5.1 Pourquoi sortir du relationnel ?

Le modèle relationnel est excellent, mais il a des prix : le **schéma est rigide** (ajouter un champ à une table de 10 milliards de lignes est lourd), les **jointures coûtent cher** quand les données sont réparties sur plusieurs machines, et les **garanties ACID** (5.4.6) ralentissent. Les bases NoSQL font des compromis différents. Il en existe quatre familles principales :

| Famille | Idée | Exemples | Cas d'usage typique |
|---|---|---|---|
| **Clé–valeur** | un énorme dictionnaire : on retrouve une valeur par sa clé, très vite | **Redis**, DynamoDB | cache, paniers, sessions, compteurs, classements |
| **Documents** | des documents JSON imbriqués, de forme libre | **MongoDB**, CouchDB | catalogues, profils, contenus, données semi-structurées |
| **Colonnes larges** | tables géantes réparties, écritures très rapides | Cassandra, HBase | journaux, mesures de capteurs, historiques |
| **Graphes** | nœuds et relations en première classe | Neo4j | réseaux sociaux, recommandations, détection de fraude |

> 📐 **Le théorème CAP (Brewer, 2000 ; démontré par Gilbert et Lynch, 2002).** Dans un système de données **réparti** sur plusieurs machines, on ne peut pas garantir en même temps les trois propriétés suivantes : **C**ohérence (tous les lecteurs voient la dernière écriture), **A**vailability, la **disponibilité** (chaque requête reçoit une réponse), et la **P**artition tolérance (le système continue de fonctionner quand le réseau entre machines est coupé). Comme les coupures réseau **arrivent** (on ne peut pas les exclure), il faut choisir en cas de coupure : **cohérence** (on refuse de répondre pour ne pas donner une donnée périmée) ou **disponibilité** (on répond, quitte à donner une donnée un peu ancienne : on parle de *cohérence à terme*). Les bases relationnelles classiques penchent vers la cohérence ; beaucoup de bases NoSQL, vers la disponibilité. Ce n'est pas « meilleur » ou « moins bon » : c'est un **choix de conception** selon l'application (un virement bancaire exige la cohérence ; le nombre de « j'aime » d'une publication peut être approximatif quelques secondes).

### 5.5.2 Les bases de documents : l'exemple de MongoDB

Dans une base de documents, une commande n'est pas répartie sur plusieurs tables : c'est **un seul document JSON** qui contient tout (le client, les lignes) **imbriqué**. Voici, construit à partir de notre base relationnelle (par un court programme exécuté en coulisses ; l'application 5.10 du cahier le détaille), le document de la commande n° 3, celle du 5.1.3 aux trois lignes :


```text
400 documents ; le troisième :
{"_id": 3, "date": "2025-01-04", "canal": "Réseaux", "montant": 88.2,
 "client": {"id": 3, "nom": "Adam Michel", "ville": "Ville F"},
 "lignes": [{"produit": "Bol en céramique", "categorie": "Poterie", "quantite": 1, "prix": 17.84},
            {"produit": "Vase peint à la main", "categorie": "Poterie", "quantite": 1, "prix": 64.42},
            {"produit": "Savon à l'huile d'olive", "categorie": "Cosmétiques", "quantite": 1, "prix": 5.94}]}
```

Ce document **contient tout ce qu'il faut** pour afficher la commande : pas de jointure à faire, une seule lecture suffit. C'est l'argument central des bases de documents : ce qu'on lit ensemble est rangé ensemble. On les interroge avec des filtres sur les champs, y compris dans les listes imbriquées. Voici « les commandes d'au moins 100 € qui contiennent un bijou », d'abord à la manière de MongoDB (les filtres se décrivent avec des documents) :

```javascript noexec
// Non exécuté : nécessite un serveur MongoDB.
db.commandes.countDocuments({
  montant: { $gte: 100 },
  "lignes.categorie": "Bijoux"
})
```

Un court programme Python (exécuté en coulisses) applique la même logique, un filtre sur les champs imbriqués, à nos documents ; comparons son résultat avec la réponse **relationnelle** (jointure SQL du 5.2) pour vérifier qu'on obtient bien la même chose :

```text
version documents (Python) : 27
version relationnelle (SQL): 27
```

Même résultat, deux philosophies : dans l'une, on **reconstruit** les liens à la lecture (jointure) ; dans l'autre, on les a **pré-assemblés** à l'écriture (imbrication).

Notez qu'il n'est même pas nécessaire de quitter SQLite pour jouer avec des documents : il sait stocker du JSON dans une colonne de texte et l'interroger avec les fonctions `json_extract` et `json_each`. C'est aussi le cas de PostgreSQL (type `jsonb`), ce qui permet un mélange des deux mondes. Plaçons les 400 documents dans une table `ex_docs` (une colonne de texte JSON) et interrogeons-la.


```sql
SELECT json_extract(doc, '$.canal')                        AS canal,
       COUNT(*)                                            AS commandes,
       ROUND(AVG(json_extract(doc, '$.montant')), 2)       AS panier_moyen
FROM ex_docs
GROUP BY canal
ORDER BY canal;
```
<!--sortie-->
```text
   canal  commandes  panier_moyen
Boutique        114         74.81
 Réseaux        138         49.01
    Site        148         59.50
```

On retrouve les paniers moyens par canal du 5.2.4. (`'$.canal'` est un *chemin* dans le document ; `$.client.ville` atteindrait un champ imbriqué.) La même question du bijou, avec `json_each` qui « déplie » la liste des lignes :

```sql
SELECT COUNT(*) AS commandes_avec_bijou_100
FROM ex_docs
WHERE json_extract(doc, '$.montant') >= 100
  AND EXISTS (SELECT 1 FROM json_each(ex_docs.doc, '$.lignes') AS l
              WHERE json_extract(l.value, '$.categorie') = 'Bijoux');
```
<!--sortie-->
```text
 commandes_avec_bijou_100
                       27
```

Pour un agrégat complet, MongoDB utilise un **pipeline** d'étapes qui s'enchaînent (le même esprit que les CTE du 5.3) :

```javascript noexec
// Non exécuté : chiffre d'affaires et nombre de commandes par canal, pour les commandes de 100 € et plus.
db.commandes.aggregate([
  { $match: { montant: { $gte: 100 } } },
  { $group: { _id: "$canal", ca: { $sum: "$montant" }, commandes: { $sum: 1 } } },
  { $sort: { ca: -1 } }
])
```

**Le revers de la médaille : la redondance.** Chaque document contient la ville du client. Combien de documents faudrait-il modifier si Sam Fontaine (client n° 2) déménageait ? Un comptage exécuté en coulisses répond :


**Vingt-trois documents** (autant que de commandes de ce client) ! C'est exactement l'anomalie de mise à jour du 5.4.1 : en choisissant l'**imbrication**, on assume la **redondance**, et c'est à l'application de la gérer. Dans le monde des documents, on décide au cas par cas ce qu'on imbrique (ce qui est lu ensemble, qui change rarement) et ce qu'on référence (ce qui change souvent). Aucun modèle n'est gratuit.

### 5.5.3 Les bases clé–valeur : l'exemple de Redis

**Redis** est le plus simple des modèles : un dictionnaire géant **en mémoire** (donc extrêmement rapide : des centaines de milliers d'opérations par seconde). On y range des valeurs sous une clé : `SET cle valeur`, `GET cle`. Il propose aussi des types pratiques : compteurs, listes, ensembles, **ensembles triés** (classements). Voici quelques commandes typiques pour une boutique en ligne :

```bash noexec
# Non exécuté : nécessite un serveur Redis.
redis-cli SET panier:2 '{"articles": 3, "total": 88.2}' EX 3600   # panier du client 2, expire dans 1 heure
redis-cli GET panier:2
redis-cli INCR visites:page_accueil                                # compteur atomique
redis-cli ZADD classement_clients 1874.3 "Sam Fontaine" 1701.7 "Yann Lambert"   # ensemble trié par score
redis-cli ZREVRANGE classement_clients 0 2 WITHSCORES              # les 3 meilleurs
```

Le cas d'usage numéro un est le **cache** : stocker le résultat d'une requête lente (par exemple le tableau de bord du chiffre d'affaires) pour ne pas la recalculer à chaque visite. Imaginons sept demandes successives (Site, Site, Boutique, Site, Boutique, Réseaux, Site) : la première fois qu'un canal est demandé, la requête SQL est exécutée (*cache miss*) et son résultat est rangé dans un dictionnaire ; les fois suivantes, la réponse vient directement du « cache » (*cache hit*). Résultat : sept demandes, **trois** requêtes SQL seulement (l'application 5.11 du cahier programme ce petit cache). Il reste le problème classique : **quand périme le cache ?** (si une nouvelle commande arrive, la valeur en cache devient fausse). Redis résout cela avec une **durée de vie** (`EX 3600`, comme ci-dessus) : la clé s'efface toute seule. Un mot célèbre résume la difficulté : « *il n'y a que deux choses difficiles en informatique : invalider un cache et nommer les choses.* »

### 5.5.4 Alors, que choisir ?

| Critère | Relationnel (SQL) | NoSQL |
|---|---|---|
| Structure des données | stable, bien définie | variable, évolutive |
| Relations entre données | nombreuses (jointures) | peu, ou imbriquées |
| Cohérence | forte (ACID) | souvent « à terme » |
| Requêtes | très riches (SQL) | plus limitées, spécialisées |
| Volume | de petit à très grand | pensé pour le très grand, réparti |
| Analyse de données | **excellent** | souvent à exporter d'abord |

Pour un data scientist, la réponse pratique est la suivante. **Commencez par le relationnel** (PostgreSQL en particulier : fiable, gratuit, et capable de stocker du JSON) : il répond à l'immense majorité des besoins, et l'analyse y est la plus confortable. N'allez vers le NoSQL que lorsqu'un besoin précis l'impose (cache ultra-rapide, volume réparti, données de forme libre, graphes). Dans les grandes entreprises, on trouve d'ailleurs souvent **plusieurs bases à la fois** (on parle de *persistance polyglotte*) : un SGBD relationnel pour les commandes, Redis pour le cache, un moteur de documents pour le catalogue, un entrepôt de données pour l'analyse. En tant qu'analyste, vous serez souvent celui qui les **réunit**, d'où l'intérêt de connaître chacune de ces familles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.10 (documents JSON) et 5.11 (un cache en Python).

> ✅ **À retenir**
>
> - **NoSQL** = « pas seulement SQL » : quatre familles (clé–valeur, documents, colonnes, graphes), nées pour le **très gros volume**, la **souplesse** du schéma et la **répartition**.
> - Le **théorème CAP** impose un choix, en cas de coupure réseau, entre cohérence et disponibilité.
> - Une base de **documents** imbrique ce qui est lu ensemble : lecture sans jointure, mais **redondance** à gérer (anomalie de mise à jour du 5.4.1).
> - Une base **clé–valeur** (Redis) est un dictionnaire ultra-rapide, idéal comme **cache** ; tout l'art est de savoir quand le périmer.
> - En pratique : **commencez par le relationnel**, choisissez le NoSQL quand un besoin précis l'exige.
> - Les commandes MongoDB et Redis de cette section n'ont **pas** été exécutées ; leur logique a été reproduite et vérifiée en Python/SQLite.


## Bilan du chapitre 5

Vous savez maintenant :

- **expliquer pourquoi** une base relationnelle vaut mieux qu'un fichier (redondance, incohérence, contraintes, volume, accès simultanés), et lire un schéma : tables, **clés primaires et étrangères**, relations 1–N et N–N ;
- **écrire des requêtes SQL** complètes : `SELECT`, `WHERE`, `ORDER BY`, `GROUP BY`/`HAVING`, **jointures** (`INNER`, `LEFT`, auto-jointure), sous-requêtes, opérations ensemblistes ;
- **éviter les pièges classiques** : priorité de `AND`/`OR`, `NULL` (trois valeurs de vérité, `NOT IN`), dates et `date('now')`, `WHERE` contre `HAVING` ;
- **calculer sans écraser les lignes** grâce aux **fonctions fenêtres** (classements, cumuls, moyennes mobiles, `LAG`/`LEAD`), structurer une requête en **CTE**, et parcourir des hiérarchies par **récursion** ;
- **concevoir un schéma** : dépendances fonctionnelles, 1FN/2FN/3FN, décomposition sans perte, et savoir quand dénormaliser (OLTP contre OLAP, vues, schéma en étoile) ;
- comprendre ce que font les **index** (`EXPLAIN QUERY PLAN`) et les **transactions** (ACID) ;
- (en option) situer les bases **NoSQL** (documents, clé–valeur) et le théorème **CAP**.

> 📒 **Pour s'entraîner.** Le cahier du volume consacre son chapitre 5 à ce chapitre : onze applications guidées (reconstruire la base, importer un CSV, les meilleurs clients, tableaux croisés, clients dormants, segmentation RFM, calendrier, réseaux de parrainage, mesure d'un index, documents JSON et cache) et onze exercices corrigés.

Le chapitre 6 clôt la partie « boîte à outils » avec les habitudes de travail du professionnel : **Git** pour garder l'historique de vos analyses (y compris vos requêtes SQL, qui sont du code comme les autres), les **notebooks Jupyter** pour mélanger code, résultats et explications, et la **ligne de commande** pour tout automatiser. Ensuite, le projet de clôture du volume, proposé dans le cahier, réunira tout ce que vous avez appris, des mathématiques au SQL, dans une seule étude de bout en bout.
