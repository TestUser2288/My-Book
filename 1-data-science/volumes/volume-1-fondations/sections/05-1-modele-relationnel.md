## 5.1 Modèle relationnel et conception de bases de données

> 💡 **Intuition.** Une base de données relationnelle, c'est **un classeur de tableaux bien rangés** (les *tables*) **qui se parlent entre eux** grâce à des numéros d'identification (les *clés*). Au lieu de tout recopier dans un seul gros tableau, on range chaque chose à **un seul endroit** : les clients dans un tableau, les produits dans un autre, les commandes dans un troisième, et on les relie par des numéros.

### 5.1.1 Pourquoi pas simplement un fichier CSV ?

La gérante a commencé avec un fichier Excel. Un jour, elle s'est retrouvée avec `commandes_v3_FINAL.xlsx`, `commandes_v3_FINAL_corrige.xlsx` et `commandes_v3_VRAIMENT_FINAL.xlsx`. Dans l'un, la cliente « Amel Ben Salah » habite Ville F, dans l'autre Ville G : laquelle est la bonne ? Personne ne sait. Les problèmes d'un fichier à plat sont toujours les mêmes :

| Problème | Exemple chez la boutique | Ce que fait une base de données |
|---|---|---|
| **Redondance** | l'adresse d'un client est recopiée sur chacune de ses 28 commandes | elle est stockée **une seule fois** |
| **Incohérence** | deux lignes du même client donnent deux villes différentes | impossible : une seule ligne client, référencée par un numéro |
| **Données invalides** | une note de satisfaction de 7, un canal « TikTok » qui n'existe pas | des **contraintes** refusent la saisie |
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
| 1 | Yassine | Lahmar | Ville C |
| 2 | Sami | Dridi | Ville A |
| 3 | Aymen | Hamdi | Ville F |

> 📐 **Définition rigoureuse.** Soient $D_1,\dots,D_p$ des ensembles appelés **domaines** (par exemple $D_1=\mathbb N$ pour les numéros, $D_2=$ les chaînes de caractères). Une **relation** $R$ de **schéma** $R(A_1:D_1,\dots,A_p:D_p)$ est un **sous-ensemble fini** du produit cartésien
> $$R\ \subseteq\ D_1\times D_2\times\cdots\times D_p .$$
> Deux conséquences importantes, souvent oubliées : (1) $R$ étant un **ensemble**, il n'y a **ni doublons ni ordre** entre les lignes : demander « la première ligne » n'a pas de sens sans préciser un critère de tri ; (2) chaque case contient **une seule valeur** de son domaine (nous y reviendrons avec la première forme normale, 5.4).

**Les clés.** C'est là que la magie opère.

- Une **clé candidate** est un ensemble minimal de colonnes qui identifie **sans ambiguïté** une ligne. Dans `clients`, `id_client` en est une. Le couple (`prenom`, `nom`) n'en est pas une : nous verrons au 5.2.4 que notre propre base contient trois « Ines Dridi » dans trois villes différentes, et même deux « Emna Sassi » qui habitent toutes deux Ville B. Un nom n'est **jamais** un bon identifiant.
- La **clé primaire** (*primary key*, PK) est la clé candidate choisie comme identifiant officiel. Elle ne peut être ni vide (`NULL`) ni répétée. Par convention, on utilise un **numéro** sans signification (une *clé de substitution*, ou *surrogate key*) : il ne change jamais, même si la personne déménage ou change de nom.
- Une **clé étrangère** (*foreign key*, FK) est une colonne qui **référence la clé primaire d'une autre table**. Dans `commandes`, la colonne `id_client` désigne le client qui a passé la commande. C'est ainsi que les tables « se parlent ».
- L'**intégrité référentielle** est la règle qui en découle : une clé étrangère ne peut contenir que des valeurs qui **existent** dans la table référencée. Impossible d'enregistrer une commande du client n° 9999 s'il n'existe pas.

> 💡 **L'analogie du carnet d'adresses.** Dans votre téléphone, vous ne recopiez pas toutes les informations d'Amel dans chaque SMS ; vous gardez une fiche « Amel » et vous écrivez à « Amel ». La fiche est la ligne de `clients`, son numéro est la clé primaire, et chaque SMS porte une clé étrangère vers elle.

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

### 5.1.3 Construire la base de la boutique

Voici maintenant le code qui fabrique la base. Vous n'avez **pas besoin** de le comprendre ligne à ligne : il joue le rôle de l'« import de données » que, dans la vraie vie, quelqu'un d'autre aurait fait pour vous. Trois choses à remarquer.

1. Il **lit** le fichier `donnees/commandes.csv` du chapitre 3 : les 400 commandes, avec leur canal, leur montant, leur délai de livraison et leur satisfaction, sont **exactement** les mêmes qu'avant.
2. Il **invente** autour de ces commandes tout ce qu'un CSV ne contient pas : une date et un client pour chaque commande, la liste des clients (ceux qui commandent souvent, ceux qui ne commandent jamais), et le **détail** de chaque commande, produit par produit. La graine est fixée (`default_rng(2025)`), donc tout est reproductible.
3. Les lignes de commande sont construites pour que la **somme** (quantité × prix) de chaque commande retombe **exactement** sur son montant. Le prix payé peut différer de quelques pour cent du prix du catalogue : promotions, variation des prix dans l'année. Nous verrons au 5.4 pourquoi il est essentiel de **recopier** le prix dans la ligne de commande au lieu de le relire dans le catalogue.

Le cœur du code est la création des tables, en SQL (`CREATE TABLE`). Lisez-la attentivement : c'est la traduction exacte du schéma ci-dessus.

```python
import sqlite3

import numpy as np
import pandas as pd


def construire(chemin_csv="donnees/commandes.csv"):
    rng = np.random.default_rng(2025)
    cmd = pd.read_csv(chemin_csv)                       # les 400 commandes du chapitre 3
    n = len(cmd)

    # ---- catalogue : 4 catégories, 16 produits (prix en €) --------------------------
    categories = ["Poterie", "Textile", "Bijoux", "Cosmétiques"]
    produits = [
        ("Tajine décoratif", 1, 45), ("Bol en céramique de Ville E", 1, 18),
        ("Vase peint à la main", 1, 65), ("Plat à couscous", 1, 38),
        ("Foutah en coton", 2, 28), ("Margoum (petit tapis)", 2, 120),
        ("Écharpe en soie", 2, 55), ("Pochette brodée", 2, 22),
        ("Bague en argent", 3, 48), ("Pendentif khamsa", 3, 35),
        ("Bracelet de perles", 3, 15), ("Boucles d'oreilles filigrane", 3, 42),
        ("Savon à l'huile d'olive", 4, 6), ("Eau de jasmin", 4, 14),
        ("Huile de nigelle", 4, 24), ("Bougie parfumée au jasmin", 4, 20),
    ]
    prix = np.array([p[2] for p in produits], dtype=float)

    # ---- dates : 400 commandes sur 2025, plus nombreuses en été et en fin d'année ------
    jours = pd.date_range("2025-01-01", "2025-12-31")
    poids_mois = np.array([0.8, 0.7, 0.9, 1.0, 1.0, 1.2, 1.4, 1.4, 1.0, 0.9, 1.3, 1.9])
    p_jour = poids_mois[jours.month - 1]
    dates = np.sort(rng.choice(jours, size=n, p=p_jour / p_jour.sum()))   # id croissant = chronologique

    # ---- clients : 80 inscrits (dont 8 qui n'ont jamais commandé) ---------------------
    prenoms = ["Amel", "Sami", "Ines", "Walid", "Rim", "Hatem", "Salma", "Karim", "Nour", "Fares",
               "Mariem", "Oussama", "Lina", "Aymen", "Sarra", "Yassine", "Dorra", "Bilel", "Emna", "Zied"]
    noms = ["Ben Salah", "Trabelsi", "Gharbi", "Jlassi", "Mansour", "Chaabane", "Hamdi", "Ayari",
            "Bouazizi", "Khelifi", "Dridi", "Mejri", "Sassi", "Zouari", "Ben Ammar", "Lahmar"]
    villes = ["Ville H", "Ville C", "Ville A", "Ville F", "Ville G", "Ville E", "Ville B", "Ville D"]
    ville = rng.choice(villes, size=80, p=[0.22, 0.12, 0.10, 0.14, 0.12, 0.10, 0.10, 0.10])
    local = np.isin(ville, ["Ville H", "Ville C", "Ville A"])            # le magasin est à Ville H
    poids = rng.gamma(1.5, 1.0, size=80)                               # quelques clients plus fidèles
    poids[rng.choice(80, size=8, replace=False)] = 0                   # inscrits dormants à vie
    client = np.empty(n, dtype=int)
    for i, c in enumerate(cmd["canal"]):
        w = poids * (local if c == "Boutique" else 1)
        client[i] = rng.choice(80, p=w / w.sum())
    premiere = pd.Series(dates).groupby(client).min()                  # première commande de chaque client
    inscr = np.array([premiere[k] - pd.Timedelta(days=int(rng.integers(0, 25))) if k in premiere.index
                      else rng.choice(jours) for k in range(80)], dtype="datetime64[ns]")
    ordre = np.argsort(inscr, kind="stable")                           # on renumérote : id croissant = inscription
    nouveau = np.empty(80, dtype=int); nouveau[ordre] = np.arange(80)
    client = nouveau[client]
    clients = []
    for rang, k in enumerate(ordre):
        pren, nom = rng.choice(prenoms), rng.choice(noms)
        tel = None if rng.random() < 0.2 else f"{rng.choice([20, 22, 24, 50, 52, 55, 98, 99])}{rng.integers(100000, 999999)}"
        parrain = int(rng.integers(1, rang + 1)) if rang >= 3 and rng.random() < 0.35 else None
        clients.append((rang + 1, pren, nom, ville[k], str(inscr[k])[:10], tel, parrain))

    # ---- lignes de commande : le total de chaque commande doit retomber sur son montant -
    lignes = []
    for i in range(n):
        cible, meilleur = cmd["montant"][i], None
        for _ in range(150):                                           # on cherche une composition plausible
            k = int(rng.choice([1, 2, 3], p=[0.55, 0.3, 0.15]))
            prod = rng.choice(16, size=k, replace=False)
            qte = rng.choice([1, 2, 3], size=k, p=[0.7, 0.22, 0.08])
            qte[-1] = 1                                                # la dernière ligne absorbera les arrondis
            f = cible / (prix[prod] * qte).sum()                       # facteur prix payé / prix catalogue
            if meilleur is None or abs(np.log(f)) < abs(np.log(meilleur[0])):
                meilleur = (f, prod, qte)
        f, prod, qte = meilleur
        pu = np.round(prix[prod] * f, 2)                               # prix payé : promos, évolution des prix
        pu[-1] = np.round((cible - (pu[:-1] * qte[:-1]).sum()) / qte[-1], 2)
        for p_, q_, u_ in zip(prod, qte, pu):
            lignes.append((i + 1, int(p_) + 1, int(q_), float(u_)))

    # ---- création de la base (en mémoire) ---------------------------------------------
    con = sqlite3.connect(":memory:")
    con.execute("PRAGMA foreign_keys = ON")
    con.executescript("""
    CREATE TABLE categories (id_categorie INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE);
    CREATE TABLE produits (
        id_produit INTEGER PRIMARY KEY, nom TEXT NOT NULL,
        id_categorie INTEGER NOT NULL REFERENCES categories(id_categorie),
        prix_catalogue REAL NOT NULL CHECK (prix_catalogue > 0));
    CREATE TABLE clients (
        id_client INTEGER PRIMARY KEY, prenom TEXT NOT NULL, nom TEXT NOT NULL, ville TEXT NOT NULL,
        date_inscription TEXT NOT NULL, telephone TEXT,
        id_parrain INTEGER REFERENCES clients(id_client));
    CREATE TABLE commandes (
        id_commande INTEGER PRIMARY KEY,
        id_client INTEGER NOT NULL REFERENCES clients(id_client),
        date_commande TEXT NOT NULL,
        canal TEXT NOT NULL CHECK (canal IN ('Réseaux', 'Site', 'Boutique')),
        montant REAL NOT NULL, delai_livraison INTEGER NOT NULL,
        satisfaction INTEGER CHECK (satisfaction BETWEEN 1 AND 5));
    CREATE TABLE lignes_commande (
        id_commande INTEGER NOT NULL REFERENCES commandes(id_commande),
        id_produit INTEGER NOT NULL REFERENCES produits(id_produit),
        quantite INTEGER NOT NULL CHECK (quantite > 0), prix_unitaire REAL NOT NULL,
        PRIMARY KEY (id_commande, id_produit));
    """)
    con.executemany("INSERT INTO categories VALUES (?, ?)", list(enumerate(categories, 1)))
    con.executemany("INSERT INTO produits VALUES (?, ?, ?, ?)", [(i + 1, *p) for i, p in enumerate(produits)])
    con.executemany("INSERT INTO clients VALUES (?, ?, ?, ?, ?, ?, ?)", clients)
    con.executemany("INSERT INTO commandes VALUES (?, ?, ?, ?, ?, ?, ?)",
                    [(i + 1, int(client[i]) + 1, str(dates[i])[:10], cmd.canal[i], float(cmd.montant[i]),
                      int(cmd.livraison[i]), int(cmd.satisfaction[i])) for i in range(n)])
    con.executemany("INSERT INTO lignes_commande VALUES (?, ?, ?, ?)", lignes)
    con.commit()
    return con
```

On crée maintenant la base et on la **sauvegarde dans un fichier** (c'est ce fichier `donnees/boutique.db` qui est fourni avec le livre) :

```python
con = construire()                       # base en mémoire
fichier = sqlite3.connect("donnees/boutique.db")
con.backup(fichier)                      # copie vers le fichier
fichier.close()
print("base construite et enregistrée dans donnees/boutique.db")
```
<!--sortie-->
```text
base construite et enregistrée dans donnees/boutique.db
```

Vérifions ce qu'elle contient. Chaque base SQLite possède une table spéciale, `sqlite_master`, qui décrit toutes les autres :

```sql
SELECT name AS "table", type
FROM sqlite_master
WHERE type = 'table'
ORDER BY name;
```
<!--sortie-->
```text
          table  type
     categories table
        clients table
      commandes table
lignes_commande table
       produits table
```

Combien de lignes dans chaque table ? (Le mot-clé `UNION ALL` empile les résultats de plusieurs requêtes ; nous y reviendrons.)

```sql
SELECT 'categories' AS "table", COUNT(*) AS lignes FROM categories
UNION ALL SELECT 'produits', COUNT(*) FROM produits
UNION ALL SELECT 'clients', COUNT(*) FROM clients
UNION ALL SELECT 'commandes', COUNT(*) FROM commandes
UNION ALL SELECT 'lignes_commande', COUNT(*) FROM lignes_commande;
```
<!--sortie-->
```text
          table  lignes
     categories       4
       produits      16
        clients      80
      commandes     400
lignes_commande     693
```

Un aperçu de chaque table. `SELECT *` signifie « toutes les colonnes » et `LIMIT 5` « seulement 5 lignes » :

```sql
SELECT * FROM clients LIMIT 5;
```
<!--sortie-->
```text
 id_client  prenom    nom    ville date_inscription telephone id_parrain
         1 Yassine Lahmar Ville C       2024-12-14  98725588       None
         2    Sami  Dridi   Ville A       2024-12-16       NaN       None
         3   Aymen  Hamdi     Ville F       2024-12-16       NaN       None
         4    Emna Zouari   Ville A       2024-12-18       NaN       None
         5    Emna  Hamdi   Ville A       2024-12-30  98402250       None
```

Remarquez la colonne `id_parrain` : vide pour la plupart des clients (pandas affiche `None` ou `NaN` selon la colonne : c'est sa façon de montrer un `NULL`), mais quand elle est remplie, elle contient le numéro d'un autre client. Et le `telephone` vide de certains clients ? Ce « vide » a un nom en SQL : `NULL`. Il nous réservera quelques surprises au 5.2.7.

```sql
SELECT * FROM commandes LIMIT 5;
```
<!--sortie-->
```text
 id_commande  id_client date_commande     canal  montant  delai_livraison  satisfaction
           1          2    2025-01-03  Boutique     44.8                0             4
           2          6    2025-01-04      Site     34.5                2             4
           3          3    2025-01-04 Réseaux     88.2                5             4
           4          1    2025-01-05 Réseaux     30.1                4             4
           5          5    2025-01-08  Boutique    110.1                0             5
```

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

Lisons ensemble cette dernière table, car elle est le cœur de la base. La commande n° 1 (dans la table `commandes`) a un montant de 44,80 € : une seule ligne ici, le produit n° 1, en un exemplaire à 44,80 €. La commande n° 3, elle, a un montant de 88,20 € : trois lignes, trois produits différents, chacun en un exemplaire (17,84 + 64,42 + 5,94 = 88,20). La table `commandes` ne dit **pas** ce qu'il y a dans le panier ; c'est `lignes_commande` qui le dit. Ce découpage est le propre d'une bonne base de données.

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
    "canal inconnu":     "INSERT INTO commandes VALUES (9002, 1, '2025-06-01', 'TikTok', 50, 2, 4)",
    "note de 7 sur 5":   "INSERT INTO commandes VALUES (9003, 1, '2025-06-01', 'Site', 50, 2, 7)",
    "numéro déjà pris":  "INSERT INTO categories VALUES (1, 'Autre')",
    "prénom manquant":   "INSERT INTO clients VALUES (500, NULL, 'Test', 'Ville H', '2025-06-01', NULL, NULL)",
}
for nom, requete in essais.items():
    try:
        con.execute(requete)
        print(f"{nom:18s} -> accepté (!)")
    except sqlite3.IntegrityError as erreur:
        print(f"{nom:18s} -> refusé : {erreur}")
print("commandes dans la base :", con.execute("SELECT COUNT(*) FROM commandes").fetchone()[0])
```
<!--sortie-->
```text
client inexistant  -> refusé : FOREIGN KEY constraint failed
canal inconnu      -> refusé : CHECK constraint failed: canal IN ('Réseaux', 'Site', 'Boutique')
note de 7 sur 5    -> refusé : CHECK constraint failed: satisfaction BETWEEN 1 AND 5
numéro déjà pris   -> refusé : UNIQUE constraint failed: categories.id_categorie
prénom manquant    -> refusé : NOT NULL constraint failed: clients.prenom
commandes dans la base : 400
```

Chaque donnée absurde est **refusée avec un message clair**, et la table reste intacte. C'est la grande différence avec une feuille Excel, où rien n'empêche de taper « sept » dans la colonne des notes. Une base bien conçue rend les erreurs de saisie **impossibles** au lieu de les laisser se glisser puis fausser silencieusement une analyse.

> ⚠️ **Particularités de SQLite (à savoir).** (1) SQLite n'applique les clés étrangères que si on le demande par `PRAGMA foreign_keys = ON` (c'est la deuxième ligne de notre code). Les autres SGBD les appliquent toujours. (2) SQLite est « souple » avec les types : il accepterait du texte dans une colonne d'entiers. PostgreSQL, lui, est strict. (3) SQLite n'a **pas de type date** : on stocke les dates en texte au format **ISO 8601** (`'2025-06-01'`, année-mois-jour). Ce format a l'avantage que **l'ordre alphabétique est l'ordre chronologique**, ce qui permet de comparer et de trier correctement les dates comme des textes. N'utilisez jamais `'01/06/2025'` : le tri alphabétique donnerait n'importe quoi.

> ⚠️ **Et l'argent ?** Nous stockons les montants en `REAL` (nombres à virgule flottante) par simplicité. En production, c'est une **mauvaise idée** : au chapitre 1 (analyse numérique, 1.5), nous avons vu que $0{,}1+0{,}2\neq0{,}3$ en binaire. Les bons choix sont un type décimal exact (`NUMERIC` / `DECIMAL`), ou bien des **entiers** exprimés dans la plus petite unité : en Tunisie, le euro se divise en **1 000 millimes**, donc 44,800 € s'enregistre `44800`. Les comptables vous remercieront.

### 5.1.5 SQL sur un fichier CSV : l'import en cinq lignes

Une dernière remarque pratique. Vous n'aurez pas toujours une base toute faite : souvent, vous recevrez un CSV. La bibliothèque pandas sait le charger dans SQLite d'un trait, et vous pouvez alors utiliser SQL dessus : très pratique pour des agrégations compliquées ou pour s'entraîner.

```python
con_csv = sqlite3.connect(":memory:")                           # une base temporaire, vide
pd.read_csv("donnees/commandes.csv").to_sql("commandes_csv", con_csv, index=False)

# SQLite a deviné les types des colonnes :
print(pd.read_sql_query("SELECT sql FROM sqlite_master", con_csv).iloc[0, 0])
print()
requete = """SELECT canal, COUNT(*) AS commandes, ROUND(AVG(montant), 2) AS panier_moyen
             FROM commandes_csv GROUP BY canal ORDER BY panier_moyen DESC"""
print(pd.read_sql_query(requete, con_csv))
```
<!--sortie-->
```text
CREATE TABLE "commandes_csv" (
"canal" TEXT,
  "montant" REAL,
  "livraison" INTEGER,
  "satisfaction" INTEGER
)

       canal  commandes  panier_moyen
0   Boutique        114         74.81
1       Site        148         59.50
2  Réseaux        138         49.01
```

On retrouve les effectifs par canal du chapitre 3 (114 commandes en boutique, 148 sur le site, 138 sur Réseaux) et, en prime, les paniers moyens : la boutique est la plus généreuse. Remarquez la différence avec la vraie base : ici la table a été **devinée** (aucune clé, aucune contrainte), alors que notre base de la boutique a été **conçue**. Un import rapide convient pour explorer ; une base conçue est indispensable pour travailler à plusieurs et dans la durée.

> ✅ **À retenir**
>
> - Une base relationnelle range chaque information **à un seul endroit** dans des **tables**, reliées par des **clés** (primaires, étrangères).
> - Les **contraintes** (`NOT NULL`, `CHECK`, `REFERENCES`...) font respecter les règles métier **automatiquement**.
> - Une relation **plusieurs à plusieurs** passe par une **table d'association** (`lignes_commande`).
> - Les requêtes SQL traduisent l'**algèbre relationnelle** : sélection, projection, produit cartésien, jointure (= produit filtré), union.
> - Dates : format ISO 8601 en texte. Argent : décimaux exacts ou entiers (millimes), jamais de flottants en production.
