## 3.6 ➕ Pour aller plus loin : PostgreSQL, MySQL, SQL Server, Oracle

> 🧭 **Section complémentaire.** Le SQL que vous avez appris est un langage **normalisé**, mais chaque éditeur y a ajouté ses habitudes. Un analyste change souvent d'entreprise, de projet ou d'entrepôt de données : cette section vous donne la carte des principales différences, pour que vous sachiez quoi vérifier avant de recopier une requête d'un système à l'autre.
>
> **Honnêteté.** Seul SQLite (et DuckDB, un moteur voisin de PostgreSQL) est installé sur la machine qui a produit ce livre. **Les exemples PostgreSQL, MySQL, SQL Server et Oracle sont donc écrits de mémoire et non exécutés**, et signalés comme tels. Les détails varient avec la version : **vérifiez toujours dans la documentation de votre produit.**

### 3.6.1 Un standard, plusieurs dialectes

Le langage SQL est normalisé par l'ISO depuis 1986, et la norme s'est enrichie par étapes (jointures explicites, requêtes récursives, fonctions fenêtres, types temporels…). En pratique, chaque système suit la norme **à sa façon** : il ne l'implémente jamais en entier, et il ajoute ses propres fonctions. Ce que vous avez appris dans ce chapitre (`SELECT … FROM … WHERE … GROUP BY`, les jointures, `CASE`, `COALESCE`, les fonctions fenêtres, les CTE) fonctionne, **à quelques détails près**, dans les quatre systèmes ; c'est tout ce qui touche aux **dates**, au **texte**, à la **limitation des lignes** et aux **types** qui diffère.

| Système | Où on le rencontre | Particularités à connaître |
|---|---|---|
| **PostgreSQL** | base libre, très répandue pour l'analyse et les entrepôts | proche de la norme ; types riches (dates, tableaux, JSON) ; `ILIKE` ; `DISTINCT ON` ; `GENERATE_SERIES` |
| **MySQL** (et MariaDB) | sites web, applications | fonctions fenêtres et CTE seulement depuis la version 8 ; pas de `FULL JOIN` ; comportements historiquement permissifs |
| **SQL Server** | entreprises utilisant l'écosystème Microsoft | dialecte **T-SQL** : `TOP n`, crochets pour les noms, `+` pour concaténer, `GETDATE()`, `DATEADD` |
| **Oracle** | grandes entreprises, banques, assurances | `FETCH FIRST`, table fictive `DUAL`, `NVL`, `SYSDATE` ; une chaîne vide y est traitée comme `NULL` |
| **SQLite** | applications embarquées, fichiers de travail (ce chapitre) | typage souple ; pas de procédures stockées ; une seule écriture à la fois |

### 3.6.2 La table de correspondance

Voici les différences que l'analyste rencontre le plus souvent, une ligne par besoin. Elles sont données **de mémoire, à vérifier** pour votre version.

| Besoin | SQLite | PostgreSQL | MySQL | SQL Server | Oracle |
|---|---|---|---|---|---|
| Limiter à n lignes | `LIMIT n` | `LIMIT n` | `LIMIT n` | `SELECT TOP n …` | `FETCH FIRST n ROWS ONLY` |
| Concaténer du texte | `a \|\| b` | `a \|\| b` | `CONCAT(a, b)` | `a + b` ou `CONCAT` | `a \|\| b` |
| Date du jour | `date('now')` | `CURRENT_DATE` | `CURDATE()` | `CAST(GETDATE() AS date)` | `TRUNC(SYSDATE)` |
| Année d'une date | `strftime('%Y', d)` | `EXTRACT(YEAR FROM d)` | `YEAR(d)` | `YEAR(d)` | `EXTRACT(YEAR FROM d)` |
| Premier jour du mois | `strftime('%Y-%m-01', d)` | `DATE_TRUNC('month', d)` | `DATE_FORMAT(d, '%Y-%m-01')` | `DATEFROMPARTS(YEAR(d), MONTH(d), 1)` | `TRUNC(d, 'MM')` |
| Ajouter 7 jours | `date(d, '+7 day')` | `d + INTERVAL '7 days'` | `DATE_ADD(d, INTERVAL 7 DAY)` | `DATEADD(day, 7, d)` | `d + 7` |
| Texte sans casse | `LIKE` (insensible pour l'ASCII) | `ILIKE` | `LIKE` (selon le jeu de caractères) | `LIKE` (selon la collation) | `LIKE` (sensible) |
| Nom entre guillemets | `"nom"` | `"nom"` | `` `nom` `` | `[nom]` ou `"nom"` | `"nom"` |
| `7 / 2` | `3` | `3` | `3,5` | `3` | `3,5` |
| `FULL JOIN` | oui (≥ 3.39) | oui | **non** | oui | oui |
| Série de nombres ou de dates | CTE récursive | `GENERATE_SERIES` | CTE récursive | CTE récursive (ou `GENERATE_SERIES` récent) | `CONNECT BY LEVEL` |
| Colonne non agrégée dans `GROUP BY` | tolérée | refusée | selon la configuration | refusée | refusée |

Deux lignes méritent un commentaire. La **division entière** d'abord : le même `7 / 2` vaut 3 ou 3,5 selon le système, ce qui est exactement le piège de la section 3.1.9, avec une raison de plus de **forcer le type décimal** (`7 / 2.0`) pour être portable. Ensuite la **chaîne vide** d'Oracle, qui la traite comme `NULL` : `code_promo = ''` n'y a pas de sens, et la différence entre « vide » et « absent » que nous avons vue en 3.1.8 y disparaît.

### 3.6.3 Les mêmes requêtes, ailleurs

Prenons deux requêtes de ce chapitre et écrivons-les dans d'autres dialectes. Les **cinq articles les plus chers** (section 3.1.4) :

```sql noexec
-- SQL Server — non exécuté
SELECT TOP 5 nom_produit, categorie, prix_vente FROM produits ORDER BY prix_vente DESC;

-- Oracle — non exécuté
SELECT nom_produit, categorie, prix_vente FROM produits ORDER BY prix_vente DESC FETCH FIRST 5 ROWS ONLY;

-- MySQL et PostgreSQL : identique à SQLite (LIMIT 5)
```

Le **nombre de commandes par mois** (section 3.1.5), où se voit la différence de traitement des dates :

```sql noexec
-- PostgreSQL — non exécuté
SELECT DATE_TRUNC('month', date_commande) AS mois, COUNT(*) AS nb_commandes
FROM commandes WHERE date_commande >= DATE '2025-07-01' GROUP BY 1 ORDER BY 1;
```

Dans SQL Server, il faudrait remplacer `DATE_TRUNC` par `DATEFROMPARTS(YEAR(date_commande), MONTH(date_commande), 1)` et **répéter cette expression** dans le `GROUP BY` : ce système n'accepte pas l'alias à cet endroit, conséquence de l'ordre d'exécution étudié en 3.1.7 (l'alias n'existe pas encore à l'étape du regroupement) ; PostgreSQL et MySQL, eux, l'acceptent par tolérance. Enfin, une même logique de **jointure à gauche avec recherche d'absence** s'écrit identiquement dans les quatre systèmes : c'est le cœur portable du langage.

### 3.6.4 DuckDB : un dialecte voisin de PostgreSQL, que l'on peut exécuter

Puisque nous ne disposons pas d'un serveur PostgreSQL, nous utilisons **DuckDB** pour montrer quelques constructions de ce dialecte. DuckDB est un moteur analytique qui s'exécute dans votre session, comme SQLite, mais dont la syntaxe est très proche de celle de PostgreSQL ; il sait lire **directement des fichiers CSV**. Branchons-le sur nos fichiers :

```python
import duckdb
DONN = os.environ["DONNEES"]
dk = duckdb.connect()
dk.sql(f"CREATE VIEW commandes AS SELECT * FROM read_csv('{DONN}/commandes.csv', header=true)")
dk.sql(f"CREATE VIEW produits AS SELECT * FROM read_csv('{DONN}/produits.csv')")
print(dk.sql("SELECT canal, COUNT(*) AS n FROM commandes GROUP BY canal ORDER BY n DESC").df().to_string(index=False))
```
<!--sortie-->
```text
   canal     n
Boutique 16975
    Site 15463
 Réseaux  3957
```

Le comptage par canal est identique à celui obtenu avec SQLite (16 975, 15 463 et 3 957 commandes) : le **même résultat**, par un autre moteur, depuis les fichiers d'origine et non plus depuis la base. C'est un contrôle de plus. Voyons trois fonctions du dialecte PostgreSQL : `DATE_TRUNC` (début de période), `ILIKE` (recherche sans casse) et `GENERATE_SERIES` (série de dates).

```python
print(dk.sql("SELECT date_trunc('month', date_commande) AS mois, COUNT(*) AS n FROM commandes WHERE date_commande >= DATE '2025-11-01' GROUP BY 1 ORDER BY 1").df().to_string(index=False))
print(dk.sql("SELECT nom_produit, prix_vente FROM produits WHERE nom_produit ILIKE 'bougie%' ORDER BY prix_vente LIMIT 3").df().to_string(index=False))
print(dk.sql("SELECT * FROM generate_series(DATE '2025-01-01', DATE '2025-01-03', INTERVAL 1 DAY) AS t(jour)").df().to_string(index=False))
```
<!--sortie-->
```text
      mois    n
2025-11-01 1509
2025-12-01 1853
            nom_produit  prix_vente
        Bougie nordique        16.9
Bougie parfumée compact        27.9
        Bougie nordique        28.9
      jour
2025-01-01
2025-01-02
2025-01-03
```

`DATE_TRUNC('month', …)` ramène chaque date au premier jour de son mois (on retrouve 1 509 commandes en novembre et 1 853 en décembre) ; `ILIKE` retrouve les bougies **sans se soucier de la casse** (alors que `LIKE` n'y suffirait pas dans PostgreSQL) ; `GENERATE_SERIES` produit en une ligne le calendrier que nous avions fabriqué avec une CTE récursive en 3.4.5. DuckDB offre même des raccourcis que PostgreSQL n'a pas, comme `QUALIFY`, qui filtre sur le résultat d'une fonction fenêtre sans passer par une requête extérieure :

```python
print(dk.sql("""SELECT categorie, nom_produit, prix_vente FROM produits
                QUALIFY ROW_NUMBER() OVER (PARTITION BY categorie ORDER BY prix_vente DESC) = 1
                ORDER BY categorie""").df().to_string(index=False))
print(dk.sql("SELECT 7 / 2 AS division, 7 // 2 AS division_entiere").df().to_string(index=False))
```
<!--sortie-->
```text
 categorie        nom_produit  prix_vente
 Bien-être    Tisane nordique        68.9
   Cuisine Casserole nordique        57.9
Décoration   Horloge nordique        96.9
    Jardin   Transat nordique       152.9
    Maison       Lampe design       126.9
 Papeterie        Trousse mat        21.9
 division  division_entiere
      3.5                 3
```

Le premier résultat reprend le produit le plus cher de chaque catégorie, comme en 3.5.1 mais en **une seule requête** sans sous-requête. Le second illustre la différence de division : DuckDB renvoie **3,5** pour `7 / 2` (il réserve `//` à la division entière), tandis que SQLite renvoie 3. Un même texte SQL, deux résultats : c'est exactement le genre de piège dont ce chapitre vous protège.

### 3.6.5 Écrire du SQL portable

Si votre requête doit tourner sur plusieurs systèmes, ou si vous changerez de base d'ici un an, quelques règles limitent les dégâts :

- **Rester dans le cœur du langage** : `CASE`, `COALESCE`, `CAST`, jointures explicites, `GROUP BY`, CTE, fonctions fenêtres. Ces constructions sont partout.
- **Isoler les fonctions de dialecte** (dates, texte) dans **une seule étape** (une CTE ou une vue) : le jour où l'on change de système, on ne corrige qu'à un endroit.
- **Forcer les types** : `CAST(x AS DECIMAL(12, 2))`, `100.0 * a / b`, pour que les divisions donnent partout le même résultat.
- **Écrire les dates au format ISO** `AAAA-MM-JJ`, que tous les systèmes comprennent, avec le mot-clé `DATE` quand le type existe.
- **Tester sur le système cible** avec un jeu de données connu, puis comparer les totaux avec ceux de l'ancien système avant de faire confiance au résultat.

> ✅ **À retenir.**
> - Le SQL est un standard, mais chaque produit a ses dialectes ; les différences touchent surtout les **dates**, le **texte**, la **limitation du nombre de lignes** (`LIMIT`, `TOP`, `FETCH FIRST`) et les **types** (la division !).
> - Le cœur (jointures, agrégats, `CASE`, CTE, fonctions fenêtres) est portable ; isolez le reste.
> - **Ce chapitre n'a exécuté que SQLite et DuckDB** : les exemples PostgreSQL, MySQL, SQL Server et Oracle sont à **vérifier dans la documentation** de votre version.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.13 (traduire des requêtes d'un dialecte à l'autre).
