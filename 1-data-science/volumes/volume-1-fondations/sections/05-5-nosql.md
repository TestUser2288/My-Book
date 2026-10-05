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

```python hide
import json

lignes_par_commande = {}
requete_lignes = """
    SELECT l.id_commande, p.nom, ca.nom, l.quantite, l.prix_unitaire
    FROM lignes_commande AS l
    JOIN produits AS p ON p.id_produit = l.id_produit
    JOIN categories AS ca ON ca.id_categorie = p.id_categorie
    ORDER BY l.id_commande, l.id_produit"""
for id_commande, produit, categorie, quantite, prix in con.execute(requete_lignes):
    lignes_par_commande.setdefault(id_commande, []).append(
        {"produit": produit, "categorie": categorie, "quantite": quantite, "prix": prix})
requete_commandes = """
    SELECT c.id_commande, c.date_commande, c.canal, c.montant, cl.id_client, cl.prenom, cl.nom, cl.ville
    FROM commandes AS c JOIN clients AS cl ON cl.id_client = c.id_client
    ORDER BY c.id_commande"""
documents = [
    {"_id": i, "date": date, "canal": canal, "montant": montant,
     "client": {"id": id_client, "nom": f"{prenom} {nom}", "ville": ville},
     "lignes": lignes_par_commande[i]}
    for i, date, canal, montant, id_client, prenom, nom, ville in con.execute(requete_commandes)
]
```

```python hide-code
d = documents[2]                                      # la commande n° 3 du 5.1.3
dump = lambda x: json.dumps(x, ensure_ascii=False)
print(len(documents), "documents ; le troisième :")
print('{"_id": %d, "date": %s, "canal": %s, "montant": %s,' % (d["_id"], dump(d["date"]), dump(d["canal"]), d["montant"]))
print(' "client": %s,' % dump(d["client"]))
print(' "lignes": [' + ",\n            ".join(dump(l) for l in d["lignes"]) + "]}")
```
<!--sortie-->
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

```python hide-code
avec_bijou = [d["_id"] for d in documents
              if d["montant"] >= 100 and any(l["categorie"] == "Bijoux" for l in d["lignes"])]

sql = """SELECT COUNT(DISTINCT c.id_commande)
         FROM commandes AS c
         JOIN lignes_commande AS l ON l.id_commande = c.id_commande
         JOIN produits AS p ON p.id_produit = l.id_produit
         WHERE c.montant >= 100 AND p.id_categorie = 3"""
print("version documents (Python) :", len(avec_bijou))
print("version relationnelle (SQL):", con.execute(sql).fetchone()[0])
```
<!--sortie-->
```text
version documents (Python) : 27
version relationnelle (SQL): 27
```

Même résultat, deux philosophies : dans l'une, on **reconstruit** les liens à la lecture (jointure) ; dans l'autre, on les a **pré-assemblés** à l'écriture (imbrication).

Notez qu'il n'est même pas nécessaire de quitter SQLite pour jouer avec des documents : il sait stocker du JSON dans une colonne de texte et l'interroger avec les fonctions `json_extract` et `json_each`. C'est aussi le cas de PostgreSQL (type `jsonb`), ce qui permet un mélange des deux mondes. Plaçons les 400 documents dans une table `ex_docs` (une colonne de texte JSON) et interrogeons-la.

```python hide
con.execute("CREATE TABLE ex_docs (doc TEXT)")
con.executemany("INSERT INTO ex_docs VALUES (?)", [(json.dumps(d, ensure_ascii=False),) for d in documents])
con.commit()
```

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

```python hide
a_modifier = sum(1 for d in documents if d["client"]["id"] == 2)
print("documents à modifier pour un seul déménagement :", a_modifier)
con.execute("DROP TABLE ex_docs")
con.commit()
```
<!--sortie-->
```text
documents à modifier pour un seul déménagement : 23
```

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
