# Chapitre 5 : Bases de données et SQL — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 5 du livre. Les **applications** sont de petites études guidées (reconstruire la base, repérer les meilleurs clients, segmenter la clientèle…) ; les **exercices** sont à chercher seul(e) avant de lire les **corrigés**. Tout s'appuie sur la base de la boutique du livre (`donnees/boutique.db` : 80 clients, 16 produits, 400 commandes, 693 lignes de commande). **La date « du jour » est le 31 décembre 2025.** Prérequis : les sections 5.1 à 5.4 du livre.

## Préparation

Le cahier est autonome : nous ouvrons une **copie en mémoire** de la base fournie, pour pouvoir y créer et supprimer des tables d'essai sans jamais modifier le fichier d'origine. Les blocs `sql` s'exécutent sur cette connexion `con`.

```python
import sqlite3
import pandas as pd

con = sqlite3.connect(":memory:")
sqlite3.connect("donnees/boutique.db").backup(con)     # copie de la base fournie
con.execute("PRAGMA foreign_keys = ON")                # SQLite n'applique les clés étrangères que sur demande
print([r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")])
```
<!--sortie-->
```text
['categories', 'clients', 'commandes', 'lignes_commande', 'produits']
```

## Applications

### Application 5.1 — Reconstruire la base de la boutique

**Objectif.** Comprendre comment la base du livre a été fabriquée : écrire son squelette, puis la régénérer avec le script fourni et vérifier qu'elle est identique au fichier.

**Étape 1 : le squelette.** Les trois premières tables (la **catégorie**, le **produit** et le **client**) ne dépendent que d'elles-mêmes ou de tables déjà créées. Créons-les dans une base vide.

```python
squelette = sqlite3.connect(":memory:")
squelette.execute("PRAGMA foreign_keys = ON")
squelette.executescript("""
CREATE TABLE categories (id_categorie INTEGER PRIMARY KEY, nom TEXT NOT NULL UNIQUE);
CREATE TABLE produits (
    id_produit INTEGER PRIMARY KEY, nom TEXT NOT NULL,
    id_categorie INTEGER NOT NULL REFERENCES categories(id_categorie),
    prix_catalogue REAL NOT NULL CHECK (prix_catalogue > 0));
CREATE TABLE clients (
    id_client INTEGER PRIMARY KEY, prenom TEXT NOT NULL, nom TEXT NOT NULL, ville TEXT NOT NULL,
    date_inscription TEXT NOT NULL, telephone TEXT,
    id_parrain INTEGER REFERENCES clients(id_client));
""")
```

**Étape 2 : les tables qui référencent les précédentes.** Une commande référence un client ; une ligne de commande référence une commande et un produit, et sa clé primaire est le couple (commande, produit).

```python
squelette.executescript("""
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
print([r[0] for r in squelette.execute("SELECT name FROM sqlite_master WHERE type = 'table' ORDER BY name")])
```
<!--sortie-->
```text
['categories', 'clients', 'commandes', 'lignes_commande', 'produits']
```

**Étape 3 : le remplissage.** Les lignes de cette base ne sont pas tapées à la main : elles sont **simulées** par la fonction `construire()` du script `build/base_sql.py`, avec une graine fixée. Elle lit les 400 commandes du fichier `donnees/commandes.csv`, leur attribue une date et un client, invente la liste des clients (dont quelques-uns qui ne commandent jamais) et compose chaque commande de un à trois produits, de sorte que la somme (quantité × prix) retombe sur le montant. Régénérons la base et comparons-la au fichier fourni, table par table.

```python
import sys
sys.path.insert(0, "build")
from base_sql import construire

neuve = construire()
for table in ["categories", "produits", "clients", "commandes", "lignes_commande"]:
    a = neuve.execute(f"SELECT * FROM {table} ORDER BY 1, 2").fetchall()
    b = con.execute(f"SELECT * FROM {table} ORDER BY 1, 2").fetchall()
    print(f"{table:16s} {len(a):4d} lignes ; identique au fichier fourni : {a == b}")
```
<!--sortie-->
```text
categories          4 lignes ; identique au fichier fourni : True
produits           16 lignes ; identique au fichier fourni : True
clients            80 lignes ; identique au fichier fourni : True
commandes         400 lignes ; identique au fichier fourni : True
lignes_commande   693 lignes ; identique au fichier fourni : True
```

**Étape 4 : contrôler la cohérence.** Une base fabriquée doit être **vérifiée**. Trois contrôles : chaque commande retombe sur son montant ; chaque client référencé existe ; toutes les dates sont dans l'année 2025.

```sql
SELECT
  (SELECT COUNT(*) FROM commandes AS c
    WHERE ABS(c.montant - (SELECT SUM(quantite * prix_unitaire) FROM lignes_commande AS l
                           WHERE l.id_commande = c.id_commande)) > 0.005)               AS commandes_incoherentes,
  (SELECT COUNT(*) FROM commandes WHERE id_client NOT IN (SELECT id_client FROM clients)) AS clients_inconnus,
  (SELECT COUNT(*) FROM commandes WHERE date_commande NOT BETWEEN '2025-01-01' AND '2025-12-31') AS dates_hors_2025;
```
<!--sortie-->
```text
 commandes_incoherentes  clients_inconnus  dates_hors_2025
                      0                 0                0
```

**Pour aller plus loin.** Changez la graine dans `build/base_sql.py` (copie de travail !) et relancez : quelles statistiques de la boutique restent stables (le nombre de commandes ? le panier moyen ?) et lesquelles bougent (les noms ? les clients dormants ?) ?

### Application 5.2 — Importer un CSV et lui donner un vrai schéma

**Objectif.** Partir d'un fichier CSV brut, comme on en reçoit en pratique, et en faire une table **conçue**, avec clé primaire et contraintes.

**Étape 1 : l'import rapide.** `pandas` charge le CSV dans SQLite d'un trait ; SQLite devine les types, mais ne pose aucune règle.

```python
brut = sqlite3.connect(":memory:")
pd.read_csv("donnees/commandes.csv").to_sql("commandes_csv", brut, index=False)
print(brut.execute("SELECT sql FROM sqlite_master").fetchone()[0])
```
<!--sortie-->
```text
CREATE TABLE "commandes_csv" (
"canal" TEXT,
  "montant" REAL,
  "livraison" INTEGER,
  "satisfaction" INTEGER
)
```

**Étape 2 : la table conçue.** On crée une vraie table avec un numéro, des types, et des règles de gestion, puis on y copie les données du CSV avec `INSERT ... SELECT`.

```python
brut.executescript("""
CREATE TABLE commandes_propres (
    id_commande INTEGER PRIMARY KEY,
    canal TEXT NOT NULL CHECK (canal IN ('Réseaux', 'Site', 'Boutique')),
    montant REAL NOT NULL CHECK (montant > 0),
    livraison INTEGER NOT NULL CHECK (livraison >= 0),
    satisfaction INTEGER CHECK (satisfaction BETWEEN 1 AND 5));
INSERT INTO commandes_propres (canal, montant, livraison, satisfaction)
SELECT canal, montant, livraison, satisfaction FROM commandes_csv;
""")
print(brut.execute("SELECT COUNT(*), ROUND(AVG(montant), 2) FROM commandes_propres").fetchone())
```
<!--sortie-->
```text
(400, 60.25)
```

**Étape 3 : la table se défend.** Essayons d'y glisser des lignes absurdes : un montant négatif, une note de 9, un canal inconnu.

```python
for ligne in ["('Site', -5, 2, 4)", "('Site', 50, 2, 9)", "('Marché', 50, 2, 4)"]:
    try:
        brut.execute(f"INSERT INTO commandes_propres (canal, montant, livraison, satisfaction) VALUES {ligne}")
        print(ligne, "-> accepté (!)")
    except sqlite3.IntegrityError as erreur:
        print(ligne, "-> refusé :", erreur)
```
<!--sortie-->
```text
('Site', -5, 2, 4) -> refusé : CHECK constraint failed: montant > 0
('Site', 50, 2, 9) -> refusé : CHECK constraint failed: satisfaction BETWEEN 1 AND 5
('Marché', 50, 2, 4) -> refusé : CHECK constraint failed: canal IN ('Réseaux', 'Site', 'Boutique')
```

**Questions.** (1) Quelle contrainte a refusé chacune des trois lignes ? (2) Quels autres contrôles ajouteriez-vous (une borne haute pour le montant ? une date ?) ? (3) Pourquoi la table du CSV ne pouvait-elle pas refuser ces lignes ?

### Application 5.3 — Les dix meilleurs clients

**Contexte.** La gérante veut connaître ses dix meilleurs clients. On joint clients et commandes, on regroupe par client, on trie par chiffre d'affaires décroissant.

```sql
SELECT cl.id_client,
       cl.prenom || ' ' || cl.nom   AS client,
       cl.ville,
       COUNT(*)                     AS commandes,
       ROUND(SUM(c.montant), 2)     AS chiffre_affaires,
       ROUND(AVG(c.montant), 2)     AS panier_moyen,
       MAX(c.date_commande)         AS derniere_commande
FROM clients AS cl
JOIN commandes AS c ON c.id_client = cl.id_client
GROUP BY cl.id_client
ORDER BY chiffre_affaires DESC
LIMIT 10;
```
<!--sortie-->
```text
 id_client       client   ville  commandes  chiffre_affaires  panier_moyen derniere_commande
         2 Sam Fontaine Ville A         23            1874.3         81.49        2025-12-24
         1 Yann Lambert Ville C         28            1701.7         60.77        2025-12-20
        47  Inès Michel Ville C         22            1317.3         59.88        2025-12-17
        11   Luc Garcia Ville H         18            1218.9         67.72        2025-12-29
        45 Anna Bernard Ville A         15            1009.3         67.29        2025-12-25
        17 Léa Fontaine Ville A         15             937.6         62.51        2025-12-22
        39    Lou Simon Ville F         10             833.1         83.31        2025-12-10
        27   Zoé Garcia Ville G         13             808.9         62.22        2025-12-28
        14 Jules Garcia Ville G          5             566.0        113.20        2025-11-09
        51  Elsa Girard Ville D         12             552.0         46.00        2025-12-10
```

**Lecture.** Le meilleur client par le chiffre d'affaires est Sam Fontaine (1 874 €, panier moyen de 81 €) ; le plus fidèle est Yann Lambert (28 commandes). Le dixième (Elsa Girard) a un chiffre d'affaires de 552 €, **plus de trois fois moins** que le premier : la clientèle est très inégale. Remarquez le `GROUP BY cl.id_client` et non `GROUP BY cl.nom` : regrouper par nom aurait fusionné les homonymes.

**À faire.** (1) Ajoutez la part de chaque client dans le chiffre d'affaires total (utilisez une sous-requête, 5.2.6). (2) Ajoutez le canal le plus utilisé par le client (indice : une fonction fenêtre ou une sous-requête corrélée).

### Application 5.4 — Chiffre d'affaires par mois et par canal

**Contexte.** On veut un tableau avec un canal par colonne : un **tableau croisé** (*pivot*). L'astuce `SUM(CASE WHEN … THEN … ELSE 0 END)` place chaque canal dans sa propre colonne.

```sql
SELECT strftime('%Y-%m', date_commande) AS mois,
       ROUND(SUM(CASE WHEN canal = 'Réseaux'  THEN montant ELSE 0 END)) AS reseaux,
       ROUND(SUM(CASE WHEN canal = 'Site'     THEN montant ELSE 0 END)) AS site,
       ROUND(SUM(CASE WHEN canal = 'Boutique' THEN montant ELSE 0 END)) AS boutique,
       ROUND(SUM(montant))                                              AS total
FROM commandes
GROUP BY mois
ORDER BY mois;
```
<!--sortie-->
```text
   mois  reseaux   site  boutique  total
2025-01    262.0  379.0     356.0  996.0
2025-02    382.0  203.0     582.0 1168.0
2025-03    737.0  824.0     126.0 1687.0
2025-04    367.0  919.0     557.0 1843.0
2025-05    693.0  679.0     942.0 2314.0
2025-06    816.0  723.0     951.0 2491.0
2025-07    647.0  992.0     932.0 2571.0
2025-08    601.0 1161.0     672.0 2435.0
2025-09    454.0  675.0     584.0 1713.0
2025-10    324.0  531.0     416.0 1272.0
2025-11    551.0  759.0     974.0 2284.0
2025-12    928.0  960.0    1437.0 3325.0
```

**Lecture.** Le site est en tête sept mois sur douze, la boutique cinq mois (février, mai, juin, novembre et décembre, où elle réalise 1 437 € sur 3 325 €), le canal Réseaux jamais ; son meilleur mois est décembre (928 €). Les trois colonnes se somment à la colonne `total` : c'est un contrôle de bon sens.

**À faire.** Ajoutez une colonne « part du canal Réseaux » en pourcentage du total du mois, puis repérez le mois où elle est la plus forte.

### Application 5.5 — Repérer les clients « dormants »

**Contexte.** Une cliente qui achetait régulièrement et ne revient plus est un signe d'alerte (on parle de *churn* quand elle part pour de bon). Un client **dormant** a passé **au moins 3 commandes** mais **aucune depuis plus de 90 jours** avant la date d'arrêté (le 31 décembre 2025). Le seuil se calcule : `date('2025-12-31', '-90 days')` donne le 2 octobre 2025.

```sql
SELECT cl.id_client,
       cl.prenom || ' ' || cl.nom   AS client,
       COUNT(*)                     AS commandes,
       MAX(c.date_commande)         AS derniere_commande,
       CAST(julianday('2025-12-31') - julianday(MAX(c.date_commande)) AS INTEGER) AS jours_sans_achat
FROM clients AS cl
JOIN commandes AS c ON c.id_client = cl.id_client
GROUP BY cl.id_client
HAVING COUNT(*) >= 3 AND MAX(c.date_commande) < '2025-10-02'
ORDER BY jours_sans_achat DESC;
```
<!--sortie-->
```text
 id_client        client  commandes derniere_commande  jours_sans_achat
        20   Adam Garcia          3        2025-05-07               238
        62    Anna Faure          3        2025-06-16               198
        37  Elsa Lambert          3        2025-07-21               163
        16 Alex Lefebvre          5        2025-07-26               158
        40    Inès Faure          3        2025-08-14               139
        50    Lina Faure          4        2025-08-17               136
         8   Théo Michel          6        2025-08-30               123
         6 Hugo Lefebvre          6        2025-09-24                98
        29  Noé Lefebvre          7        2025-09-26                96
```

**Lecture.** Neuf clients répondent à ces critères : voilà la liste de relance de la gérante. Le plus ancien (Adam Garcia, dernière commande le 7 mai) n'est pas revenu depuis 238 jours. Notez l'emploi de `HAVING` avec **deux conditions sur le groupe** : le nombre de commandes **et** la date de la dernière.

**À faire.** Ajoutez le chiffre d'affaires passé de chaque client dormant et classez la liste de relance par valeur décroissante : à qui écrire en premier ?

### Application 5.6 — Segmenter la clientèle par quartiles de dépenses

**Contexte.** Les marketeurs aiment les segmentations de type **RFM** : **R**écence (depuis combien de temps le client n'a-t-il pas acheté ?), **F**réquence (combien de fois a-t-il acheté ?), **M**ontant (combien a-t-il dépensé ?). Deux étapes : une première CTE calcule les trois indicateurs par client ; la seconde utilise `NTILE(4)`, qui découpe les clients, triés par montant décroissant, en **4 groupes d'effectifs égaux** (quartiles).

```sql
WITH rfm AS (
    SELECT id_client,
           CAST(julianday('2025-12-31') - julianday(MAX(date_commande)) AS INTEGER) AS recence_jours,
           COUNT(*)                     AS frequence,
           ROUND(SUM(montant), 2)       AS montant
    FROM commandes
    GROUP BY id_client
),
segments AS (
    SELECT *, NTILE(4) OVER (ORDER BY montant DESC) AS quartile
    FROM rfm
)
SELECT quartile,
       COUNT(*)                          AS clients,
       ROUND(MIN(montant))               AS depense_min,
       ROUND(MAX(montant))               AS depense_max,
       ROUND(SUM(montant))               AS depense_totale,
       ROUND(AVG(frequence), 1)          AS achats_moyens,
       ROUND(AVG(recence_jours))         AS jours_depuis_dernier_achat
FROM segments
GROUP BY quartile
ORDER BY quartile;
```
<!--sortie-->
```text
 quartile  clients  depense_min  depense_max  depense_totale  achats_moyens  jours_depuis_dernier_achat
        1       17        427.0       1874.0         14063.0           12.6                        20.0
        2       17        270.0        427.0          5678.0            5.8                        49.0
        3       16        122.0        270.0          3086.0            3.6                        66.0
        4       16         33.0        122.0          1270.0            1.8                       153.0
```

**Lecture.** Le quartile 1 (les 17 plus gros clients) dépense **14 063 € sur 24 098**, soit **58 %** du chiffre d'affaires, et ces clients sont revenus il y a 20 jours en moyenne. Le quartile 4 (16 clients) ne pèse que 5 % et n'est pas revenu depuis 153 jours en moyenne. On retrouve la loi de **Pareto** (« 80-20 », ici plutôt « 25-58 ») : une minorité de clients fait une majorité du chiffre d'affaires. Cette information change la stratégie : chouchouter le quartile 1, relancer le quartile 3, ne pas s'acharner sur le quartile 4.

**À faire.** Remplacez `NTILE(4)` par `NTILE(10)` : quelle part du chiffre d'affaires fait le meilleur décile ?

### Application 5.7 — Le temps dans les données : un calendrier complet, et le délai entre commandes

**Contexte.** Une table de ventes ne contient que les jours où il y a eu des ventes : les jours **sans** vente n'apparaissent pas, ce qui fausse les moyennes quotidiennes. La parade classique : générer **tous les jours** de l'année avec une CTE récursive, puis les joindre aux commandes par un `LEFT JOIN`.

```sql
WITH RECURSIVE jours(d) AS (
    SELECT '2025-01-01'
    UNION ALL
    SELECT date(d, '+1 day') FROM jours WHERE d < '2025-12-31'
),
ventes_par_jour AS (
    SELECT j.d, COUNT(c.id_commande) AS commandes
    FROM jours AS j
    LEFT JOIN commandes AS c ON c.date_commande = j.d
    GROUP BY j.d
)
SELECT strftime('%Y-%m', d)          AS mois,
       COUNT(*)                      AS jours,
       SUM(commandes = 0)            AS jours_sans_commande,
       ROUND(AVG(commandes), 2)      AS commandes_par_jour
FROM ventes_par_jour
GROUP BY mois
ORDER BY mois;
```
<!--sortie-->
```text
   mois  jours  jours_sans_commande  commandes_par_jour
2025-01     31                   19                0.52
2025-02     28                   15                0.71
2025-03     31                   15                0.81
2025-04     30                    7                1.20
2025-05     31                    9                1.16
2025-06     30                   10                1.10
2025-07     31                    7                1.35
2025-08     31                    7                1.42
2025-09     30                    8                1.03
2025-10     31                   18                0.65
2025-11     30                    7                1.33
2025-12     31                   10                1.84
```

**Lecture.** En janvier, **19 jours sur 31** se sont passés sans la moindre commande, et ils n'apparaissent dans aucune table de ventes. Sans le calendrier, la « moyenne par jour » de décembre serait calculée seulement sur les jours où l'on a vendu (donc **surestimée**) ; avec lui, elle l'est sur les 31 jours. C'est un exemple concret de **biais de sélection** dans une requête : les jours sans vente sont absents du tableau, donc invisibles.

**Deuxième partie : le délai entre deux commandes d'un même client.** Pour chaque commande, `LAG(date_commande)` calculé *dans la partition du client* donne la date de sa commande précédente. Voici ce que cela donne pour le client n° 1.

```sql
SELECT id_client, date_commande,
       LAG(date_commande) OVER (PARTITION BY id_client ORDER BY date_commande, id_commande) AS commande_precedente,
       CAST(julianday(date_commande)
            - julianday(LAG(date_commande) OVER (PARTITION BY id_client ORDER BY date_commande, id_commande))
            AS INTEGER)                                                                    AS jours_ecoules
FROM commandes
WHERE id_client = 1
ORDER BY date_commande, id_commande
LIMIT 6;
```
<!--sortie-->
```text
 id_client date_commande commande_precedente  jours_ecoules
         1    2025-01-05                 NaN            NaN
         1    2025-02-01          2025-01-05           27.0
         1    2025-02-11          2025-02-01           10.0
         1    2025-02-14          2025-02-11            3.0
         1    2025-03-08          2025-02-14           22.0
         1    2025-03-09          2025-03-08            1.0
```

**À faire.** Combien de jours sans commande y a-t-il au total sur l'année ? Quel mois a la plus longue série de jours consécutifs sans commande (indice : numérotez les jours, 5.3.2) ?

### Application 5.8 — Le réseau de parrainage : chaînes et chiffre d'affaires généré

**Contexte.** Le livre a compté les filleuls de chaque ambassadeur. On veut maintenant voir **la chaîne complète** de parrainage de chaque membre d'un réseau, et chiffrer ce que le réseau rapporte. Le texte `chemin` recolle les prénoms le long de la branche (il permet aussi de trier dans l'ordre de parcours d'un arbre).

```sql
WITH RECURSIVE arbre(id_client, profondeur, chemin) AS (
    SELECT id_client, 0, prenom || ' ' || nom
    FROM clients
    WHERE id_client = 10
    UNION ALL
    SELECT c.id_client, a.profondeur + 1, a.chemin || ' > ' || c.prenom || ' ' || c.nom
    FROM clients AS c
    JOIN arbre   AS a ON c.id_parrain = a.id_client
)
SELECT id_client, profondeur, chemin
FROM arbre
ORDER BY chemin;
```
<!--sortie-->
```text
 id_client  profondeur                                                              chemin
        10           0                                                          Lou Michel
        14           1                                           Lou Michel > Jules Garcia
        23           2                             Lou Michel > Jules Garcia > Hugo Girard
        28           3               Lou Michel > Jules Garcia > Hugo Girard > Anna Martin
        55           4 Lou Michel > Jules Garcia > Hugo Girard > Anna Martin > Théo Girard
        18           1                                             Lou Michel > Sam Michel
```

**Lecture.** Le `chemin` de chaque client donne **toute sa chaîne de parrainage** depuis l'ambassadeur : Théo Girard (profondeur 4) est arrivé par Anna Martin, venue par Hugo Girard, venu par Jules Garcia, venu par Lou Michel. Remarquez que Lou Michel (client n° 10) **n'a jamais passé de commande** : elle figure parmi les quatorze clients inscrits sans achat. Pourtant elle a amené cinq clients : une requête qui ne regarderait que les achats la jugerait sans valeur.

**À faire.** Calculez le chiffre d'affaires **généré** par ce réseau (la somme des commandes de ses membres, sans la racine) : c'est la base d'une prime au parrainage. (Le corrigé de l'exercice 5.10 fait ce calcul pour les trois plus gros réseaux.)

### Application 5.9 — Mesurer le gain d'un index

**Contexte.** Sur 400 lignes, un index ne change rien. Pour **le voir**, on construit une table de 500 000 lignes avec une CTE récursive, puis on chronomètre la même recherche avant et après la création d'un index.

```python
import time

con.executescript("""
CREATE TABLE ex_gros (id INTEGER PRIMARY KEY, id_client INTEGER, montant REAL);
WITH RECURSIVE s(i) AS (SELECT 1 UNION ALL SELECT i + 1 FROM s WHERE i < 500000)
INSERT INTO ex_gros SELECT i, (i * 7919) % 50000, ROUND(10 + (i * 31) % 190, 2) FROM s;
""")

def duree(repetitions=20):
    debut = time.perf_counter()
    for k in range(repetitions):
        con.execute("SELECT COUNT(*), SUM(montant) FROM ex_gros WHERE id_client = ?", (123 + k,)).fetchone()
    return (time.perf_counter() - debut) / repetitions

sans_index = duree()
con.execute("CREATE INDEX idx_gros_client ON ex_gros(id_client)")
avec_index = duree()
print("lignes dans la table :", con.execute("SELECT COUNT(*) FROM ex_gros").fetchone()[0])
print("l'index accélère la recherche :", sans_index > 10 * avec_index)
con.execute("DROP TABLE ex_gros")
```
<!--sortie-->
```text
lignes dans la table : 500000
l'index accélère la recherche : True
```

**Lecture.** Les durées exactes dépendent de votre machine ; le programme n'affiche donc qu'un **verdict** robuste (le gain dépasse un facteur dix). Affichez `sans_index / avec_index` chez vous pour connaître le facteur exact sur votre machine. Vérifiez aussi, avec `EXPLAIN QUERY PLAN`, que la requête passe de `SCAN` à `SEARCH`.

**À faire.** Mesurez l'effet inverse : combien de temps prend l'insertion de 100 000 lignes avec et sans index ? (L'index n'est pas gratuit : voir 5.4.5.)

### Application 5.10 — De la base relationnelle aux documents JSON

**Contexte.** Une base de documents range une commande dans **un seul document**. On reconstruit ces documents à partir de nos cinq tables, on les interroge en Python, et on compare avec la réponse SQL.

```python
import json

lignes = {}
for i, produit, categorie, quantite, prix in con.execute("""
        SELECT l.id_commande, p.nom, ca.nom, l.quantite, l.prix_unitaire
        FROM lignes_commande AS l
        JOIN produits AS p ON p.id_produit = l.id_produit
        JOIN categories AS ca ON ca.id_categorie = p.id_categorie
        ORDER BY l.id_commande, l.id_produit"""):
    lignes.setdefault(i, []).append({"produit": produit, "categorie": categorie, "quantite": quantite, "prix": prix})

documents = [
    {"_id": i, "date": date, "canal": canal, "montant": montant,
     "client": {"id": id_client, "nom": f"{prenom} {nom}", "ville": ville}, "lignes": lignes[i]}
    for i, date, canal, montant, id_client, prenom, nom, ville in con.execute("""
        SELECT c.id_commande, c.date_commande, c.canal, c.montant, cl.id_client, cl.prenom, cl.nom, cl.ville
        FROM commandes AS c JOIN clients AS cl ON cl.id_client = c.id_client ORDER BY c.id_commande""")
]
print(len(documents), "documents")
print(json.dumps(documents[2], ensure_ascii=False))
```
<!--sortie-->
```text
400 documents
{"_id": 3, "date": "2025-01-04", "canal": "Réseaux", "montant": 88.2, "client": {"id": 3, "nom": "Adam Michel", "ville": "Ville F"}, "lignes": [{"produit": "Bol en céramique", "categorie": "Poterie", "quantite": 1, "prix": 17.84}, {"produit": "Vase peint à la main", "categorie": "Poterie", "quantite": 1, "prix": 64.42}, {"produit": "Savon à l'huile d'olive", "categorie": "Cosmétiques", "quantite": 1, "prix": 5.94}]}
```

**Interroger les documents.** Les commandes d'au moins 100 € qui contiennent un bijou, en Python sur les documents, puis en SQL sur les tables : les deux réponses doivent coïncider.

```python
avec_bijou = [d["_id"] for d in documents
              if d["montant"] >= 100 and any(l["categorie"] == "Bijoux" for l in d["lignes"])]
sql = """SELECT COUNT(DISTINCT c.id_commande) FROM commandes AS c
         JOIN lignes_commande AS l ON l.id_commande = c.id_commande
         JOIN produits AS p ON p.id_produit = l.id_produit
         WHERE c.montant >= 100 AND p.id_categorie = 3"""
print("version documents (Python) :", len(avec_bijou))
print("version relationnelle (SQL):", con.execute(sql).fetchone()[0])
print("documents à modifier si le client n° 2 déménage :", sum(1 for d in documents if d["client"]["id"] == 2))
```
<!--sortie-->
```text
version documents (Python) : 27
version relationnelle (SQL): 27
documents à modifier si le client n° 2 déménage : 23
```

**Lecture.** Même résultat, deux philosophies : l'une **reconstruit** les liens à la lecture (jointure), l'autre les a **pré-assemblés** à l'écriture (imbrication). Mais l'imbrication a un prix : la ville du client est recopiée dans chacun de ses 23 documents, et il faudrait les modifier tous : c'est l'anomalie de mise à jour du 5.4.1.

**À faire.** Stockez ces documents dans une table SQLite (`CREATE TABLE ex_docs (doc TEXT)`) et calculez le panier moyen par canal avec `json_extract`.

### Application 5.11 — Un cache en Python

**Contexte.** Le cas d'usage numéro un des bases clé–valeur comme Redis est le **cache** : stocker le résultat d'une requête lente pour ne pas la recalculer à chaque visite. Voici le mécanisme avec un simple dictionnaire.

```python
cache = {}
nb_requetes_sql = 0

def chiffre_affaires_du_canal(canal):
    global nb_requetes_sql
    cle = f"ca:{canal}"
    if cle in cache:                                   # « cache hit » : réponse immédiate
        return cache[cle]
    nb_requetes_sql += 1                               # « cache miss » : on interroge la vraie base
    cache[cle] = con.execute("SELECT ROUND(SUM(montant)) FROM commandes WHERE canal = ?", (canal,)).fetchone()[0]
    return cache[cle]

for canal in ["Site", "Site", "Boutique", "Site", "Boutique", "Réseaux", "Site"]:
    print(f"{canal:10s}", chiffre_affaires_du_canal(canal))
print("7 demandes, requêtes SQL réellement exécutées :", nb_requetes_sql)
```
<!--sortie-->
```text
Site       8807.0
Site       8807.0
Boutique   8528.0
Site       8807.0
Boutique   8528.0
Réseaux    6764.0
Site       8807.0
7 demandes, requêtes SQL réellement exécutées : 3
```

**Lecture.** Sept demandes, trois requêtes seulement. Reste le problème classique : **quand périme le cache ?** Si une nouvelle commande arrive, la valeur en cache devient fausse.

**À faire.** Ajoutez une durée de vie à chaque entrée (stockez l'instant d'écriture avec la valeur et refusez les valeurs plus vieilles que *n* secondes). Qu'avez-vous réimplémenté ? (Réponse : le paramètre `EX` de Redis.)

## Exercices

> 🧭 Cherchez d'abord seul(e) (sur papier, ou en écrivant la requête dans votre éditeur), vérifiez ensuite en exécutant, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse.

### Exercice 5.1 ⭐ — Clés et contraintes (section 5.1 du livre)

La gérante veut enregistrer les **avis** des clients sur les produits. Un avis a un numéro, est écrit par **un** client sur **un** produit, à une date, avec une note de 1 à 5 et un commentaire facultatif. Un client ne peut laisser **qu'un seul avis par produit**. (a) Quelle est la clé primaire, quelles sont les clés étrangères ? (b) Écrivez le `CREATE TABLE` avec toutes les contraintes. (c) Vérifiez qu'un avis valide est accepté, et que trois avis invalides (note 6, doublon client/produit, produit inexistant) sont refusés.

### Exercice 5.2 ⭐ — Filtrer (section 5.2 du livre)

Combien de commandes de **plus de 100 €** ont été passées **en boutique** en **décembre 2025** ? Affichez les trois plus grosses.

### Exercice 5.3 ⭐ — Agréger et joindre (section 5.2 du livre)

Pour chaque **ville de client**, donnez le nombre de clients ayant commandé, le nombre de commandes, le chiffre d'affaires et le panier moyen, classées par chiffre d'affaires décroissant. Quelle ville a le meilleur panier moyen ? Est-ce aussi celle qui a le plus gros chiffre d'affaires ?

### Exercice 5.4 ⭐⭐ — `HAVING`, jointure externe (section 5.2 du livre)

Quels produits se sont vendus à **moins de 40 unités** sur l'année ? Pour chacun, donnez les unités vendues et le chiffre d'affaires. Faut-il arrêter de vendre tous ces produits ?

### Exercice 5.5 ⭐⭐ — Anti-jointure (section 5.2 du livre)

Les clients qui habitent près de la boutique (**Ville H, Ville C, Ville A**) mais n'y ont **jamais acheté** sont une cible de choix pour une invitation. Listez-les, de deux façons différentes (`NOT EXISTS` et `LEFT JOIN ... IS NULL`), et vérifiez que les deux donnent le même nombre.

### Exercice 5.6 ⭐⭐ — `NULL` (section 5.2.7 du livre)

(a) Pour chaque ville, quel est le **pourcentage de clients dont le téléphone est renseigné** ? (b) Un stagiaire écrit `WHERE id_parrain != 3` pour compter les clients **qui n'ont pas été parrainés par le client n° 3**. Combien de lignes obtient-il ? Combien devrait-il en obtenir ? Corrigez.

### Exercice 5.7 ⭐⭐ — Dates, et regard statistique (sections 5.2.7 et 3.4 du livre)

Quel est le **jour de la semaine** le plus chargé (en nombre de commandes et en chiffre d'affaires) ? Cette différence entre jours est-elle significative, ou du bruit ? (Utilisez un test du khi-deux d'adéquation, chapitre 3.)

### Exercice 5.8 ⭐⭐⭐ — Fenêtre (section 5.3 du livre)

Pour **chaque catégorie**, quel est le produit au **plus gros chiffre d'affaires** ?

### Exercice 5.9 ⭐⭐⭐ — Cte et fenêtres (section 5.3 du livre)

(a) Quelle proportion des clients actifs a commandé **au moins deux fois** (taux de réachat) ? (b) Pour ces clients, comparez le montant de leur **première** commande à celui de leur **dernière** : combien dépensent plus à la fin qu'au début ?

### Exercice 5.10 ⭐⭐⭐ — Récursivité (section 5.3.6 du livre)

Pour les trois clients ayant le plus de filleuls (directs ou non), calculez le **nombre de membres** de leur réseau (sans eux-mêmes) et le **chiffre d'affaires cumulé de ces membres**. Qui est l'ambassadeur le plus rentable ?

### Exercice 5.11 ⭐⭐⭐ — Dépendances fonctionnelles (section 5.4 du livre)

La boutique enregistre ses livraisons dans une seule table : `livraisons(id_livraison, id_commande, transporteur, tel_transporteur, ville_livraison, frais)`. Règles de gestion : une livraison concerne une commande, est assurée par un transporteur et part vers une ville ; un transporteur n'a qu'un seul numéro de téléphone ; les **frais ne dépendent que de la ville** de livraison (barème par ville). (a) Écrivez les dépendances fonctionnelles. (b) Déterminez la clé. (c) La table est-elle en 2FN ? en 3FN ? (d) Proposez une décomposition en 3FN, et vérifiez-la avec la fonction `fermeture` du 5.4.2.

## Corrigés

### Corrigé 5.1

(a) La clé primaire est `id_avis`. Les clés étrangères sont `id_client` (vers `clients`) et `id_produit` (vers `produits`). La règle « un avis par client et par produit » se traduit par une contrainte `UNIQUE (id_client, id_produit)` : le couple est une **clé candidate** en plus de `id_avis`. (b) et (c) :

```sql
CREATE TABLE ex_avis (
    id_avis      INTEGER PRIMARY KEY,
    id_client    INTEGER NOT NULL REFERENCES clients(id_client),
    id_produit   INTEGER NOT NULL REFERENCES produits(id_produit),
    date_avis    TEXT    NOT NULL,
    note         INTEGER NOT NULL CHECK (note BETWEEN 1 AND 5),
    commentaire  TEXT,
    UNIQUE (id_client, id_produit)
);
INSERT INTO ex_avis VALUES (1, 2, 8, '2025-12-02', 5, 'Magnifique broderie');
```

```python
essais = {
    "note de 6":              "INSERT INTO ex_avis VALUES (2, 3, 8, '2025-12-03', 6, NULL)",
    "doublon client/produit": "INSERT INTO ex_avis VALUES (3, 2, 8, '2025-12-04', 4, NULL)",
    "produit inexistant":     "INSERT INTO ex_avis VALUES (4, 2, 99, '2025-12-05', 4, NULL)",
}
for nom, requete in essais.items():
    try:
        con.execute(requete)
        print(f"{nom:24s} -> accepté (!)")
    except sqlite3.IntegrityError as erreur:
        print(f"{nom:24s} -> refusé : {erreur}")
print("avis enregistrés :", con.execute("SELECT COUNT(*) FROM ex_avis").fetchone()[0])
con.execute("DROP TABLE ex_avis")
```
<!--sortie-->
```text
note de 6                -> refusé : CHECK constraint failed: note BETWEEN 1 AND 5
doublon client/produit   -> refusé : UNIQUE constraint failed: ex_avis.id_client, ex_avis.id_produit
produit inexistant       -> refusé : FOREIGN KEY constraint failed
avis enregistrés : 1
```

L'avis valide est enregistré, les trois autres sont refusés chacun par une contrainte différente (`CHECK`, `UNIQUE`, clé étrangère). Le commentaire est facultatif : c'est la seule colonne sans `NOT NULL`.

### Corrigé 5.2

On filtre sur trois conditions (`AND`) ; les dates ISO se comparent comme du texte (5.1.4) : « à partir du 1er décembre » suffit, puisque la base s'arrête au 31.

```sql
SELECT COUNT(*) AS nb_commandes
FROM commandes
WHERE canal = 'Boutique' AND date_commande >= '2025-12-01' AND montant > 100;
```
<!--sortie-->
```text
 nb_commandes
            6
```

```sql
SELECT id_commande, date_commande, montant
FROM commandes
WHERE canal = 'Boutique' AND date_commande >= '2025-12-01' AND montant > 100
ORDER BY montant DESC
LIMIT 3;
```
<!--sortie-->
```text
 id_commande date_commande  montant
         362    2025-12-16    208.8
         376    2025-12-22    147.6
         391    2025-12-29    128.5
```

### Corrigé 5.3

Il faut joindre `clients` (la ville) et `commandes` (les montants). Pour compter les *clients distincts*, `COUNT(DISTINCT ...)`.

```sql
SELECT cl.ville,
       COUNT(DISTINCT cl.id_client)  AS clients_actifs,
       COUNT(*)                      AS commandes,
       ROUND(SUM(c.montant))         AS chiffre_affaires,
       ROUND(AVG(c.montant), 2)      AS panier_moyen
FROM clients AS cl
JOIN commandes AS c ON c.id_client = cl.id_client
GROUP BY cl.ville
ORDER BY chiffre_affaires DESC;
```
<!--sortie-->
```text
  ville  clients_actifs  commandes  chiffre_affaires  panier_moyen
Ville A              13        100            6456.0         64.56
Ville C               9         80            4619.0         57.73
Ville H               9         49            3407.0         69.53
Ville G               7         38            2200.0         57.89
Ville D               6         41            2101.0         51.25
Ville F               6         34            2043.0         60.09
Ville B               8         31            1735.0         55.95
Ville E               8         27            1538.0         56.96
```

Ville A est en tête pour le chiffre d'affaires (6 456 €) mais pas pour le panier : c'est **Ville H** qui a le meilleur panier moyen (69,53 €), avec un nombre de commandes beaucoup plus faible (49 contre 100). Le chiffre d'affaires est le produit *nombre de commandes × panier moyen* : un fort volume de petits paniers peut battre un faible volume de gros paniers.

### Corrigé 5.4

`LEFT JOIN` pour ne pas perdre un éventuel produit **jamais vendu** (il aurait 0 unité, ou `NULL` : voir `COALESCE`). Le filtre sur une valeur agrégée s'écrit avec `HAVING`.

```sql
SELECT p.nom                                          AS produit,
       COALESCE(SUM(l.quantite), 0)                   AS unites,
       ROUND(COALESCE(SUM(l.quantite * l.prix_unitaire), 0)) AS chiffre_affaires
FROM produits AS p
LEFT JOIN lignes_commande AS l ON l.id_produit = p.id_produit
GROUP BY p.id_produit
HAVING COALESCE(SUM(l.quantite), 0) < 40
ORDER BY unites;
```
<!--sortie-->
```text
             produit  unites  chiffre_affaires
         Petit tapis      13            1593.0
Vase peint à la main      37            2411.0
     Écharpe en soie      37            2031.0
```

Trois produits. Mais **faible volume ne veut pas dire faible intérêt** : le petit tapis, à 120 € l'unité, ne s'est vendu qu'à 13 exemplaires et rapporte pourtant 1 593 €, plus que bien des produits très vendus. Le vase peint et l'écharpe en soie (37 unités chacun) sont même parmi les produits au plus gros chiffre d'affaires du magasin. Arrêter de les vendre serait une erreur : le bon indicateur dépend de la question (rotation, chiffre d'affaires, marge). Aucun de nos produits n'est resté invendu.

### Corrigé 5.5

Version `NOT EXISTS` : on garde les clients de ces villes pour lesquels il n'existe **aucune** commande en boutique. Version `LEFT JOIN` : on joint **seulement** les commandes de boutique (la condition sur le canal va dans le `ON`, pas dans le `WHERE` !), puis on garde ceux qui n'ont aucun partenaire.

```sql
SELECT cl.id_client, cl.prenom, cl.nom, cl.ville
FROM clients AS cl
WHERE cl.ville IN ('Ville H', 'Ville C', 'Ville A')
  AND NOT EXISTS (SELECT 1 FROM commandes AS c
                  WHERE c.id_client = cl.id_client AND c.canal = 'Boutique')
ORDER BY cl.id_client;
```
<!--sortie-->
```text
 id_client prenom      nom   ville
        10    Lou   Michel Ville H
        20   Adam   Garcia Ville H
        28   Anna   Martin Ville A
        32   Théo     Roux Ville C
        55   Théo   Girard Ville C
        65   Elsa   Girard Ville H
        75   Lina   Girard Ville C
        78    Léa Lefebvre Ville H
```

```sql
SELECT COUNT(*) AS avec_left_join
FROM clients AS cl
LEFT JOIN commandes AS c ON c.id_client = cl.id_client AND c.canal = 'Boutique'
WHERE cl.ville IN ('Ville H', 'Ville C', 'Ville A')
  AND c.id_commande IS NULL;
```
<!--sortie-->
```text
 avec_left_join
              8
```

Huit clients, quelle que soit la méthode. Si l'on avait placé `c.canal = 'Boutique'` dans le `WHERE`, la requête aurait éliminé justement les lignes « sans partenaire » (dont `c.canal` est `NULL`), et le résultat aurait été vide : un cas d'école du 5.2.7. Parmi ces huit clients, certains n'ont **jamais** acheté du tout (comme Lou Michel, la grande ambassadrice du 5.3.6) : l'invitation à la boutique serait pour eux un premier achat.

### Corrigé 5.6

(a) `telephone IS NOT NULL` vaut 1 ou 0 : sa moyenne est la proportion de numéros renseignés.

```sql
SELECT ville,
       COUNT(*)                                      AS clients,
       SUM(telephone IS NOT NULL)                    AS avec_telephone,
       ROUND(100.0 * AVG(telephone IS NOT NULL), 1)  AS pourcentage
FROM clients
GROUP BY ville
ORDER BY pourcentage DESC;
```
<!--sortie-->
```text
  ville  clients  avec_telephone  pourcentage
Ville D        7               7        100.0
Ville B       11              11        100.0
Ville G       11              10         90.9
Ville F        7               6         85.7
Ville E       10               8         80.0
Ville H       11               8         72.7
Ville A       13               9         69.2
Ville C       10               6         60.0
```

Les numéros sont toujours renseignés à Ville D et à Ville B, mais seulement à 60 % à Ville C. (b) Le comparatif `!=` renvoie *inconnu* quand `id_parrain` est `NULL` : les 49 clients **sans parrain** sont éliminés, alors qu'ils ne sont évidemment pas parrainés par le client n° 3.

```sql
SELECT (SELECT COUNT(*) FROM clients WHERE id_parrain != 3)                      AS naif,
       (SELECT COUNT(*) FROM clients WHERE id_parrain != 3 OR id_parrain IS NULL) AS corrige,
       (SELECT COUNT(*) FROM clients WHERE id_parrain = 3)                       AS parraines_par_3,
       (SELECT COUNT(*) FROM clients WHERE id_parrain IS NULL)                   AS sans_parrain;
```
<!--sortie-->
```text
 naif  corrige  parraines_par_3  sans_parrain
   30       79                1            49
```

Le stagiaire obtient 30 lignes, alors qu'il en faut 79 (80 clients moins l'unique filleul du client n° 3). Les 49 sans parrain manquent à l'appel ; 30 + 49 = 79. On peut aussi écrire `WHERE id_parrain IS NOT 3` (opérateur de SQLite qui traite proprement `NULL`) ou `COALESCE(id_parrain, 0) != 3`.

### Corrigé 5.7

`strftime('%w', ...)` donne 0 pour dimanche... 6 pour samedi ; un `CASE` donne des noms lisibles.

```sql
SELECT CASE strftime('%w', date_commande)
            WHEN '0' THEN 'dimanche' WHEN '1' THEN 'lundi'    WHEN '2' THEN 'mardi'
            WHEN '3' THEN 'mercredi' WHEN '4' THEN 'jeudi'    WHEN '5' THEN 'vendredi'
            ELSE 'samedi' END                  AS jour,
       COUNT(*)                                AS commandes,
       ROUND(SUM(montant))                     AS chiffre_affaires
FROM commandes
GROUP BY strftime('%w', date_commande)
ORDER BY commandes DESC, chiffre_affaires DESC;
```
<!--sortie-->
```text
    jour  commandes  chiffre_affaires
mercredi         66            3722.0
   lundi         63            4071.0
vendredi         61            3794.0
dimanche         56            3350.0
   mardi         54            3203.0
   jeudi         50            3319.0
  samedi         50            2641.0
```

Le mercredi est en tête pour le nombre de commandes (66), le lundi pour le chiffre d'affaires. Mais l'écart est-il autre chose que du bruit ? Test du khi-deux d'adéquation (3.4) de l'hypothèse « les commandes se répartissent **uniformément** sur les sept jours » :

```python
from scipy import stats
effectifs = [r[0] for r in con.execute(
    "SELECT COUNT(*) FROM commandes GROUP BY strftime('%w', date_commande) ORDER BY strftime('%w', date_commande)")]
khi2, p = stats.chisquare(effectifs)
print("effectifs (dimanche ... samedi) :", effectifs)
print(f"khi-deux = {khi2:.2f}, p-valeur = {p:.3f}")
```
<!--sortie-->
```text
effectifs (dimanche ... samedi) : [56, 63, 54, 66, 50, 61, 50]
khi-deux = 4.21, p-valeur = 0.648
```

Avec une p-valeur largement supérieure à 5 %, on **ne peut pas rejeter** l'uniformité : les différences entre jours sont compatibles avec le simple hasard. (C'est d'ailleurs normal : ces dates ont été simulées sans aucun effet de jour de semaine.) Leçon : un classement (« le mercredi est le meilleur jour ») n'est pas une découverte tant qu'on ne l'a pas confronté au hasard.

### Corrigé 5.8

On calcule d'abord le chiffre d'affaires par produit (CTE `par_produit`), puis un `RANK` par catégorie, et l'on ne garde que le rang 1 (5.3.2).

```sql
WITH par_produit AS (
    SELECT cat.nom AS categorie, p.nom AS produit,
           ROUND(SUM(l.quantite * l.prix_unitaire)) AS chiffre_affaires
    FROM lignes_commande AS l
    JOIN produits   AS p   ON p.id_produit = l.id_produit
    JOIN categories AS cat ON cat.id_categorie = p.id_categorie
    GROUP BY p.id_produit
)
SELECT categorie, produit, chiffre_affaires
FROM (
    SELECT *, RANK() OVER (PARTITION BY categorie ORDER BY chiffre_affaires DESC) AS rang
    FROM par_produit
)
WHERE rang = 1
ORDER BY categorie;
```
<!--sortie-->
```text
  categorie              produit  chiffre_affaires
     Bijoux      Bague en argent            2638.0
Cosmétiques        Huile de soin            1128.0
    Poterie Vase peint à la main            2411.0
    Textile      Écharpe en soie            2031.0
```

La bague en argent domine les bijoux, le vase peint la poterie, l'écharpe en soie le textile et l'huile de soin les cosmétiques. (`RANK` laisserait apparaître deux lignes en cas d'égalité parfaite ; ici il n'y en a pas.)

### Corrigé 5.9

(a) Un client « actif » est un client qui a au moins une commande. (b) On numérote les commandes de chaque client dans les deux sens (`ROW_NUMBER` croissant et décroissant) : la première a le rang 1 dans l'ordre croissant, la dernière a le rang 1 dans l'ordre décroissant.

```sql
SELECT COUNT(*)                                         AS clients_actifs,
       SUM(n >= 2)                                      AS reachetent,
       ROUND(100.0 * SUM(n >= 2) / COUNT(*), 1)         AS taux_de_reachat_pct
FROM (SELECT id_client, COUNT(*) AS n FROM commandes GROUP BY id_client);
```
<!--sortie-->
```text
 clients_actifs  reachetent  taux_de_reachat_pct
             66          58                 87.9
```

```sql
WITH numerotees AS (
    SELECT id_client, montant,
           ROW_NUMBER() OVER (PARTITION BY id_client ORDER BY date_commande, id_commande)           AS depuis_le_debut,
           ROW_NUMBER() OVER (PARTITION BY id_client ORDER BY date_commande DESC, id_commande DESC) AS depuis_la_fin,
           COUNT(*)     OVER (PARTITION BY id_client)                                               AS nb_commandes
    FROM commandes
),
premiere_et_derniere AS (
    SELECT id_client,
           MAX(CASE WHEN depuis_le_debut = 1 THEN montant END) AS premiere,
           MAX(CASE WHEN depuis_la_fin   = 1 THEN montant END) AS derniere
    FROM numerotees
    WHERE nb_commandes >= 2
    GROUP BY id_client
)
SELECT COUNT(*)                         AS clients,
       SUM(derniere > premiere)         AS depensent_plus_a_la_fin,
       ROUND(AVG(premiere), 2)          AS premiere_moyenne,
       ROUND(AVG(derniere), 2)          AS derniere_moyenne
FROM premiere_et_derniere;
```
<!--sortie-->
```text
 clients  depensent_plus_a_la_fin  premiere_moyenne  derniere_moyenne
      58                       29             61.91              57.4
```

Sur 66 clients actifs, 58 ont recommandé au moins une fois : un **taux de réachat de 87,9 %**, excellent. Parmi eux, la moitié exactement (29 sur 58) dépense davantage lors de la dernière commande que lors de la première, et les montants moyens sont proches (61,91 € contre 57,40 €) : **pas de tendance** à dépenser plus avec le temps dans ces données (là encore, un test de comparaison de moyennes au sens du chapitre 3 serait à faire avant de conclure à autre chose que du hasard).

### Corrigé 5.10

Une CTE récursive parcourt les réseaux, en gardant la **racine** de chacun comme au 5.3.6. On retire la racine elle-même (profondeur 0) du décompte et du chiffre d'affaires.

```sql
WITH RECURSIVE reseau(id_client, racine, profondeur) AS (
    SELECT id_client, id_client, 0 FROM clients WHERE id_parrain IS NULL
    UNION ALL
    SELECT c.id_client, r.racine, r.profondeur + 1
    FROM clients AS c JOIN reseau AS r ON c.id_parrain = r.id_client
),
ca_client AS (
    SELECT id_client, SUM(montant) AS ca FROM commandes GROUP BY id_client
)
SELECT r.racine,
       cl.prenom || ' ' || cl.nom        AS ambassadeur,
       COUNT(*)                          AS membres,
       ROUND(COALESCE(SUM(ca.ca), 0), 2) AS ca_des_membres
FROM reseau AS r
JOIN clients AS cl ON cl.id_client = r.racine
LEFT JOIN ca_client AS ca ON ca.id_client = r.id_client
WHERE r.profondeur > 0
GROUP BY r.racine
ORDER BY membres DESC, ca_des_membres DESC
LIMIT 3;
```
<!--sortie-->
```text
 racine  ambassadeur  membres  ca_des_membres
     10   Lou Michel        5           808.2
      7  Paul Martin        4          2048.7
      1 Yann Lambert        4          1117.0
```

Le `LEFT JOIN` est indispensable : un membre qui n'a jamais commandé n'a pas de ligne dans `ca_client` ; avec un `JOIN` ordinaire, il disparaîtrait du décompte des membres. Les trois plus gros réseaux sont ceux de Lou Michel (n° 10, 5 membres), de Paul Martin (n° 7, 4 membres) et de Yann Lambert (n° 1, 4 membres ; il est classé après Paul car on départage les ex æquo par le chiffre d'affaires). L'ambassadeur le plus **rentable** est **Paul Martin** : ses quatre filleuls ont dépensé 2 048,70 €, contre 1 117,00 € pour ceux de Yann Lambert et 808,20 € seulement pour les cinq membres du plus grand réseau, celui de Lou Michel. Le réseau le plus **grand** n'est donc pas le plus **rentable** : il faut mesurer ce qu'on veut optimiser.

### Corrigé 5.11

(a) Dépendances :
- `id_livraison` $\to$ `id_commande`, `transporteur`, `ville_livraison` (une livraison fixe sa commande, son transporteur et sa destination) ;
- `transporteur` $\to$ `tel_transporteur` ;
- `ville_livraison` $\to$ `frais`.

(b) La fermeture de `id_livraison` contient tous les attributs (elle atteint `tel_transporteur` par `transporteur` et `frais` par `ville_livraison`), et c'est un attribut seul : c'est donc **la clé**. (c) **2FN** : oui, trivialement, car la clé est formée d'**un seul** attribut (il ne peut pas y avoir de dépendance partielle). **3FN** : **non**, car deux dépendances sont **transitives** : `id_livraison` $\to$ `transporteur` $\to$ `tel_transporteur`, et `id_livraison` $\to$ `ville_livraison` $\to$ `frais`. Conséquence concrète : le téléphone d'un transporteur est répété sur toutes ses livraisons, et le barème d'une ville sur chaque livraison vers elle (anomalies du 5.4.1). (d) Décomposition : `livraisons(id_livraison, id_commande, transporteur, ville_livraison)`, `transporteurs(transporteur, tel_transporteur)`, `tarifs(ville_livraison, frais)`. Vérification par le calcul :

```python
def fermeture(X, deps):
    """Attributs déterminés par X (algorithme de point fixe)."""
    res, change = set(X), True
    while change:
        change = False
        for gauche, droite in deps:
            if set(gauche) <= res and not set(droite) <= res:
                res |= set(droite)
                change = True
    return res

deps = [
    (["id_livraison"],     ["id_commande", "transporteur", "ville_livraison"]),
    (["transporteur"],     ["tel_transporteur"]),
    (["ville_livraison"],  ["frais"]),
]
tous = {"id_livraison", "id_commande", "transporteur", "tel_transporteur", "ville_livraison", "frais"}
print("fermeture de {id_livraison} :", sorted(fermeture(["id_livraison"], deps)))
print("c'est une clé :", fermeture(["id_livraison"], deps) == tous)
```
<!--sortie-->
```text
fermeture de {id_livraison} : ['frais', 'id_commande', 'id_livraison', 'tel_transporteur', 'transporteur', 'ville_livraison']
c'est une clé : True
```

```python
# Dans chaque table de la décomposition, la clé détermine bien toutes les colonnes de la table.
decomposition = {
    "livraisons":    ({"id_livraison", "id_commande", "transporteur", "ville_livraison"}, {"id_livraison"}),
    "transporteurs": ({"transporteur", "tel_transporteur"}, {"transporteur"}),
    "tarifs":        ({"ville_livraison", "frais"}, {"ville_livraison"}),
}
for nom, (attributs, cle) in decomposition.items():
    print(f"{nom:14s} clé {sorted(cle)} détermine toute la table : {fermeture(cle, deps) >= attributs}")
```
<!--sortie-->
```text
livraisons     clé ['id_livraison'] détermine toute la table : True
transporteurs  clé ['transporteur'] détermine toute la table : True
tarifs         clé ['ville_livraison'] détermine toute la table : True
```

Dans chaque table, la clé détermine toutes les autres colonnes, et les deux dépendances transitives ont été isolées chacune dans sa propre table (aucune dépendance entre colonnes non-clés ne subsiste) : le schéma est en 3FN, et même en BCNF puisque le seul déterminant de chaque table est sa clé. La décomposition est **sans perte** (théorème de Heath, 5.4.3) : chaque découpage sépare un attribut déterminant (`transporteur`, `ville_livraison`) de ce qu'il détermine, et le garde dans la table de gauche comme clé étrangère.
