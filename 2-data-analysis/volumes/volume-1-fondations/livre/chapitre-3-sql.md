# Chapitre 3 : SQL

> « Une question bien posée à une base de données vaut mieux que dix tableaux copiés à la main. »


La gérante de la boutique vous arrête dans le couloir : « Je prépare mon bilan de l'année. **Quels sont nos dix meilleurs clients de 2025, et que représentent-ils dans notre chiffre d'affaires ?** » La question tient en une phrase. La réponse, elle, se cache dans deux tables de plusieurs dizaines de milliers de lignes : la liste des commandes, et le détail de chacune. Vous pourriez ouvrir un classeur, copier, trier, additionner à la main ; vous y passeriez la matinée, et personne ne saurait demain comment vous avez obtenu votre chiffre.

Ce chapitre vous apprend à poser cette question **à la base de données elle-même**, dans le langage prévu pour cela : le **SQL** (*Structured Query Language*, que l'on prononce « esse-ku-elle » ou « sicouèle »). À la fin du chapitre, vous répondrez à la question de la gérante en une requête de quelques lignes, **vous la vérifierez par un autre outil**, et vous pourrez la relancer l'an prochain en changeant une date.

## Pourquoi un analyste a besoin du SQL

Une grande partie des données d'une entreprise ne vit pas dans des fichiers, mais dans des **bases de données relationnelles** : la caisse, le site, la comptabilité, la logistique y écrivent en continu. Pour les lire, on ne copie pas les tables dans un tableur : on **interroge** la base. Trois raisons rendent cette compétence centrale pour une analyste.

- **L'échelle.** Un tableur se traîne à partir de quelques centaines de milliers de lignes ; une base répond en quelques instants à des questions sur des millions de lignes, parce qu'elle sait **filtrer, joindre et agréger près des données**, sans les déplacer.
- **La source unique.** Quand tout le monde interroge la même base, tout le monde parle du même chiffre d'affaires. Un classeur recopié, lui, devient vite un chiffre de plus.
- **La reproductibilité.** Une requête est un texte : on la relit, on la fait relire, on la rejoue le mois suivant, on la met sous contrôle de version. Un clic dans un tableur ne laisse aucune trace.

> 💡 **Intuition.** Une requête SQL ne dit pas **comment** calculer (quelles boucles, dans quel ordre), mais **ce que l'on veut** : quelles colonnes, de quelles tables, avec quelles conditions, regroupées comment. C'est le moteur de la base qui choisit la méthode. On parle d'un langage **déclaratif**. C'est ce qui rend le SQL à la fois court et exigeant : il faut savoir **décrire précisément le résultat attendu**, y compris la ligne qui, sur le tableau final, représente « une commande », « un client » ou « un mois ».

## Le chemin de ce chapitre

Le parcours essentiel suit les quatre idées qui font 90 % du travail quotidien d'une analyste.

- **3.1 SELECT, filtrage, tri, agrégation** : lire une table, garder les lignes qui comptent, les trier, les regrouper et les résumer ; comprendre l'ordre dans lequel le moteur exécute une requête, et la valeur absente (`NULL`).
- **3.2 Jointures** : recoller les tables entre elles (clients, commandes, produits), garder ou non les lignes sans correspondance, et éviter le piège le plus coûteux du métier : **la multiplication silencieuse des lignes**.
- **3.3 Fonctions fenêtres** : calculer un classement, un cumul, une moyenne mobile ou une évolution d'un mois sur l'autre **sans perdre le détail** des lignes.
- **3.4 CTE et structuration de requêtes complexes** : découper une longue requête en étapes nommées, la construire avec méthode, et la **vérifier** par un second outil.

Deux sections facultatives prolongent ce parcours : **➕ 3.5 SQL avancé** (sous-requêtes, index, vues, transactions, déclencheurs, sécurité) et **➕ 3.6 Différences entre PostgreSQL, MySQL, SQL Server et Oracle** (les dialectes que vous rencontrerez en entreprise).

## Les données du chapitre

> 📦 **La base `boutique.db`.** Tout le chapitre travaille sur une petite base **SQLite** (un fichier unique, sans serveur à installer) qui décrit **trois ans d'activité de la boutique** (2023 à 2025) : les clients, les produits, les commandes et leurs lignes, les retours, et un tableau de bord journalier. **Les données sont simulées**, avec des graines fixes : aucun client, aucun produit réel. La section 3.1.1 en dessine le schéma.

Les requêtes de ce chapitre sont **réellement exécutées** : les tableaux que vous verrez sous chaque bloc sont les résultats produits par SQLite (version 3.46) au moment où le livre a été fabriqué, pas des résultats imaginés. Deux précautions de lecture :

- le chapitre travaille sur une **copie jetable** de la base, ce qui nous autorise à créer des index ou des vues sans rien abîmer ;
- le SQL est un langage normalisé, mais **chaque produit a son dialecte**. Ce que vous lirez ici est du SQL courant, qui fonctionne tel quel sur la plupart des bases ; ce qui est propre à SQLite est signalé, et la section 3.6 dresse la liste des différences.

> 🧭 **En pratique : lire les résultats avec un œil d'analyste.** Après chaque requête, posez-vous toujours trois questions : *combien de lignes attendais-je ? quelle est la signification d'une ligne du résultat ? ce chiffre est-il plausible ?* Le chapitre vous y entraîne en comparant systématiquement les résultats à des ordres de grandeur connus (36 395 commandes, un chiffre d'affaires annuel de l'ordre du million d'euros…) et, quand c'est possible, à un second outil.

Les applications guidées et les exercices de ce chapitre sont dans le cahier : vous y trouverez une base prête à l'emploi et une trentaine de requêtes à écrire, corrigées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 et exercices 3.1 à 3.14 (chacun renvoie à la section du livre qu'il met en pratique).


## 3.1 SELECT, filtrage, tri, agrégation

Cette première section pose les fondations : lire une table, ne garder que les lignes utiles, les ordonner, calculer de nouvelles colonnes, puis **résumer** (compter, additionner, moyenner) par groupes. Presque toute requête d'analyse, même la plus longue, est une variation sur ces gestes. Nous les appliquons d'emblée aux données de la boutique, en gardant à l'esprit la question de la gérante : *qui sont nos meilleurs clients, et pèsent-ils lourd dans le chiffre d'affaires ?*

### 3.1.1 Une base, des tables, des clés

Une base de données relationnelle est un ensemble de **tables**. Une table ressemble à une feuille de tableur, avec deux différences essentielles : **chaque colonne a un type** (entier, décimal, texte, date…), et **chaque ligne décrit une chose du même genre**. Cette dernière idée est la plus importante du chapitre : le **grain** d'une table, c'est ce que représente **une ligne**.

| Table | Une ligne = | Clé de la table |
|---|---|---|
| `clients` | un client | `id_client` |
| `produits` | un article du catalogue | `id_produit` |
| `commandes` | une commande (un passage en caisse, un panier sur le site) | `id_commande` |
| `lignes_commande` | un produit dans une commande | `id_ligne` |
| `retours` | une ligne de commande retournée | `id_retour` |
| `jours_exploitation` | un jour d'activité de la boutique | `date` |

Une **clé primaire** identifie chaque ligne de façon unique. Une **clé étrangère** est une colonne qui contient la clé primaire d'une autre table : `commandes.id_client` désigne un client, `lignes_commande.id_commande` désigne la commande à laquelle appartient la ligne. Ces liens sont ce qui rend la base « relationnelle » ; la figure suivante les dessine.


![Les six tables de la base boutique.db et leurs liens : un client passe plusieurs commandes, une commande compte plusieurs lignes, une ligne désigne un produit et peut donner lieu à un retour.](figures/ch03-schema.png)

Demandons à la base ce qu'elle contient. La requête ci-dessous compte les lignes de chaque table ; nous en profitons pour découvrir `UNION ALL`, qui empile des résultats de même forme.

```sql
SELECT 'clients' AS table_, COUNT(*) AS nb_lignes FROM clients
UNION ALL SELECT 'produits', COUNT(*) FROM produits
UNION ALL SELECT 'commandes', COUNT(*) FROM commandes
UNION ALL SELECT 'lignes_commande', COUNT(*) FROM lignes_commande
UNION ALL SELECT 'retours', COUNT(*) FROM retours
UNION ALL SELECT 'jours_exploitation', COUNT(*) FROM jours_exploitation
```
<!--sortie-->
```text
            table_  nb_lignes
           clients       6000
          produits        120
         commandes      36395
   lignes_commande      83905
           retours       5002
jours_exploitation       1096
```

La boutique compte donc **6 000 clients**, **36 395 commandes** et **83 905 lignes de commande** sur trois ans, soit un peu plus de deux lignes par commande, et **1 096 jours** d'exploitation (trois ans, dont une année bissextile). Deux lectures s'imposent. D'abord, le rapport entre les tables : il y a plus de lignes que de commandes, **parce qu'une commande contient plusieurs lignes** ; nous y reviendrons en 3.2.6, car c'est la source de la plupart des erreurs de chiffres d'affaires. Ensuite, le type des colonnes. Interrogeons le catalogue de la base pour la table `commandes` :

```sql
SELECT name AS colonne, type AS type FROM pragma_table_info('commandes')
```
<!--sortie-->
```text
       colonne    type
   id_commande INTEGER
 date_commande    TEXT
         heure    TEXT
     id_client INTEGER
         canal    TEXT
mode_livraison    TEXT
    code_promo    TEXT
```

Les dates sont stockées en **texte**, au format ISO `AAAA-MM-JJ`. Ce n'est pas un détail : ce format a la propriété agréable que **l'ordre alphabétique est l'ordre chronologique**, ce qui permet de comparer et de trier des dates comme du texte. Dans une autre base (PostgreSQL, SQL Server…) les dates ont un vrai type `DATE`, mais les requêtes de ce chapitre s'écrivent presque de la même façon.

> ⚠️ **Piège : la base de la boutique ne déclare pas ses clés.** Les six tables ont été créées à partir de fichiers, sans contrainte : rien n'empêche, dans cette base, d'insérer une commande pour un client qui n'existe pas. Dans une base bien conçue, on **déclare** les clés pour que la base elle-même refuse les incohérences. Voici un exemple minimal, deux tables de démonstration :

```sql
CREATE TABLE demo_clients (id_client INTEGER PRIMARY KEY, ville TEXT NOT NULL);
CREATE TABLE demo_commandes (
  id_commande INTEGER PRIMARY KEY,
  id_client   INTEGER NOT NULL REFERENCES demo_clients(id_client),
  montant     REAL CHECK (montant >= 0));
PRAGMA foreign_keys = ON;
INSERT INTO demo_clients VALUES (1, 'Ville A'), (2, 'Ville B');
INSERT INTO demo_commandes VALUES (10, 1, 25.0);
```

La clause `REFERENCES` déclare la clé étrangère, `CHECK` impose une règle sur la valeur, `NOT NULL` interdit l'absence. Essayons maintenant d'insérer deux lignes incohérentes :

```python
for requete in ("INSERT INTO demo_commandes VALUES (11, 99, 10.0)", "INSERT INTO demo_commandes VALUES (12, 1, -5.0)"):
    try:
        con.execute(requete)
    except sqlite3.IntegrityError as erreur:
        print("refusé :", erreur)
```
<!--sortie-->
```text
refusé : FOREIGN KEY constraint failed
refusé : CHECK constraint failed: montant >= 0
```

La base refuse les deux, en nommant la règle violée. C'est l'intérêt d'un modèle déclaré : **les erreurs de saisie sont arrêtées à l'entrée**, et non découvertes six mois plus tard dans un rapport. Nous supprimons nos tables de démonstration avant de continuer.


### 3.1.2 SELECT et FROM : choisir des colonnes

Toute lecture commence par `SELECT` (quelles colonnes ?) et `FROM` (dans quelle table ?). La forme la plus simple affiche les premières lignes d'une table :

```sql
SELECT id_commande, date_commande, canal
FROM commandes
LIMIT 5
```
<!--sortie-->
```text
 id_commande date_commande    canal
           1    2023-01-01     Site
           2    2023-01-01 Boutique
           3    2023-01-01 Boutique
           4    2023-01-01 Boutique
           5    2023-01-01 Boutique
```

`LIMIT 5` borne le nombre de lignes renvoyées : c'est le bon réflexe pour **regarder** une table sans en afficher soixante mille lignes. On peut écrire `SELECT *` pour obtenir toutes les colonnes ; c'est pratique en exploration, mais à éviter dans une requête que l'on garde : si la table gagne une colonne demain, le résultat change à votre insu, et la base transporte inutilement des données.

Une requête ne se contente pas de **recopier** des colonnes : elle peut en **calculer**. On donne alors un nom au résultat avec `AS` (un **alias**). La marge d'un produit est la différence entre son prix de vente et son coût d'achat ; le taux de marge la rapporte au prix :

```sql
SELECT nom_produit, prix_vente, cout_achat,
       ROUND(prix_vente - cout_achat, 2) AS marge,
       ROUND(100 * (prix_vente - cout_achat) / prix_vente, 1) AS taux_marge
FROM produits
ORDER BY taux_marge DESC
LIMIT 5
```
<!--sortie-->
```text
      nom_produit  prix_vente  cout_achat  marge  taux_marge
 Pochette compact         7.9        3.16   4.74        60.0
 Transat nordique        11.9        4.76   7.14        60.0
  Tablier compact        29.9       12.01  17.89        59.8
    Rideau design        31.9       12.84  19.06        59.7
Guirlande compact        54.9       22.17  32.73        59.6
```

Nous avons ajouté `ORDER BY` (section suivante) pour afficher les cinq produits au taux de marge le plus élevé : ils se situent autour de **60 %**, ce qui est cohérent avec la façon dont les coûts d'achat de la boutique ont été fixés (entre 40 et 65 % du prix). **Tout calcul dans un `SELECT` se fait ligne par ligne** : la marge de chaque produit est calculée indépendamment des autres. Nous verrons en 3.1.6 comment calculer à l'échelle de **groupes** de lignes.

### 3.1.3 WHERE : ne garder que les lignes utiles

`WHERE` filtre les lignes **avant** tout calcul de groupe. Sa condition combine des comparaisons avec `AND`, `OR` et `NOT`. Voici les opérateurs que l'analyste utilise tous les jours :

| Besoin | Écriture | Exemple |
|---|---|---|
| égalité, différence | `=`, `<>` (ou `!=`) | `canal = 'Site'` |
| comparaison | `<`, `<=`, `>`, `>=` | `prix_vente >= 50` |
| intervalle (bornes **incluses**) | `BETWEEN a AND b` | `date_commande BETWEEN '2025-11-24' AND '2025-11-30'` |
| appartenance à une liste | `IN (…)` | `categorie IN ('Jardin', 'Cuisine')` |
| motif de texte | `LIKE` (`%` = n'importe quelle suite, `_` = un caractère) | `nom_produit LIKE 'Bougie%'` |
| valeur absente | `IS NULL`, `IS NOT NULL` | `date_retour IS NULL` |

Les textes s'écrivent entre **apostrophes simples** (`'Site'`) ; les guillemets servent aux noms de colonnes ou de tables. Pour isoler les commandes passées sur le site avec un code promo pendant la semaine du « Vendredi noir » de 2025 :

```sql
SELECT id_commande, date_commande, heure, canal, code_promo
FROM commandes
WHERE canal = 'Site'
  AND code_promo <> ''
  AND date_commande BETWEEN '2025-11-24' AND '2025-11-30'
ORDER BY date_commande, heure
LIMIT 6
```
<!--sortie-->
```text
 id_commande date_commande heure canal code_promo
       34177    2025-11-24 12:02  Site     SOLDES
       34176    2025-11-24 12:28  Site     SOLDES
       34138    2025-11-24 12:42  Site     SOLDES
       34141    2025-11-24 12:57  Site     SOLDES
       34167    2025-11-24 13:32  Site     SOLDES
       34147    2025-11-24 13:52  Site     SOLDES
```

Nous voyons les six premières de ces commandes, toutes avec le code `SOLDES`. Remarquez `code_promo <> ''` : dans cette base, l'absence de code promo est enregistrée par un **texte vide** `''`, et non par une valeur absente (`NULL`) ; nous reviendrons sur cette différence en 3.1.8.

Pour les motifs de texte et les listes, voici les bougies des catégories « Décoration » et « Bien-être » :

```sql
SELECT id_produit, nom_produit, categorie, prix_vente
FROM produits
WHERE nom_produit LIKE 'Bougie%' AND categorie IN ('Décoration', 'Bien-être')
ORDER BY prix_vente
```
<!--sortie-->
```text
 id_produit             nom_produit  categorie  prix_vente
         51         Bougie nordique Décoration        16.9
        109 Bougie parfumée compact  Bien-être        27.9
         41         Bougie nordique Décoration        28.9
        119 Bougie parfumée compact  Bien-être        56.9
```

Le résultat compte quatre lignes, et un détail doit vous alerter : **« Bougie nordique » apparaît deux fois**, avec deux identifiants et deux prix différents. Dans cette base, **le nom d'un produit n'est pas une clé** ; c'est `id_produit` qui l'est. Regrouper par nom dans une analyse fusionnerait à tort deux articles distincts. Un analyste se méfie toujours des colonnes « qui ressemblent » à une clé.

> ⚠️ **Piège : `AND` passe avant `OR`.** Comme en arithmétique où la multiplication précède l'addition, `AND` est évalué **avant** `OR`. La condition `canal = 'Site' OR canal = 'Réseaux' AND code_promo = 'SOLDES'` signifie « toutes les commandes du site, **plus** celles des réseaux avec un code `SOLDES` ». Écrivez toujours des **parenthèses** pour dire ce que vous pensez : `(canal = 'Site' OR canal = 'Réseaux') AND code_promo = 'SOLDES'`. Sur les données de la boutique, la première lecture renvoie 15 810 commandes, la seconde 1 593 : le même texte, écrit sans parenthèses, change le résultat d'un facteur dix.

Les deux chiffres de l'encadré proviennent des deux requêtes suivantes, que nous exécutons pour que vous puissiez les vérifier :

```sql
SELECT COUNT(*) AS sans_parentheses FROM commandes
WHERE canal = 'Site' OR canal = 'Réseaux' AND code_promo = 'SOLDES';

SELECT COUNT(*) AS avec_parentheses FROM commandes
WHERE (canal = 'Site' OR canal = 'Réseaux') AND code_promo = 'SOLDES'
```
<!--sortie-->
```text
 sans_parentheses
            15810

 avec_parentheses
             1593
```

### 3.1.4 ORDER BY, LIMIT, DISTINCT

`ORDER BY` trie le résultat, par ordre croissant (`ASC`, par défaut) ou décroissant (`DESC`), sur une ou plusieurs colonnes ; la seconde colonne départage les ex æquo de la première. `LIMIT n` ne garde que les `n` premières lignes **du résultat trié** : c'est la combinaison `ORDER BY … DESC LIMIT n` qui répond aux questions « les n meilleurs… ». Les cinq articles les plus chers du catalogue :

```sql
SELECT nom_produit, categorie, prix_vente
FROM produits
ORDER BY prix_vente DESC
LIMIT 5
```
<!--sortie-->
```text
     nom_produit categorie  prix_vente
Transat nordique    Jardin       152.9
    Lampe design    Maison       126.9
    Lanterne mat    Jardin       117.9
 Étagère compact    Maison       105.9
      Panier mat    Maison       104.9
```

> ⚠️ **Piège : `LIMIT` sans `ORDER BY`.** Sans tri, « les cinq premières lignes » n'ont aucune signification : l'ordre dans lequel une base renvoie ses lignes **n'est pas garanti**, et il peut changer d'un jour à l'autre (après la création d'un index, par exemple). Tout `LIMIT` qui compte doit être précédé d'un `ORDER BY`, et d'un critère de départage si des ex æquo sont possibles.

`DISTINCT` élimine les doublons du résultat. Quels canaux de vente apparaissent dans les commandes ?

```sql
SELECT DISTINCT canal FROM commandes
```
<!--sortie-->
```text
   canal
    Site
Boutique
 Réseaux
```

Le résultat liste les **trois canaux** `Boutique`, `Site` et `Réseaux`. `DISTINCT` est une excellente façon d'**explorer** une colonne qualitative ; nous verrons qu'on le retrouve aussi à l'intérieur d'un comptage, `COUNT(DISTINCT …)`, pour compter des éléments **différents**.

### 3.1.5 Calculer des colonnes : expressions, CASE et dates

Une colonne calculée peut combiner des colonnes, des constantes, des fonctions (`ROUND`, `LENGTH`, `UPPER`, `SUBSTR`…) et des conditions. L'expression `CASE` est le « si… alors… sinon » du SQL : elle range chaque ligne dans une catégorie. Classons les produits en trois gammes de prix et comptons-les :

```sql
SELECT CASE WHEN prix_vente < 20 THEN 'petit prix'
            WHEN prix_vente < 60 THEN 'moyen'
            ELSE 'haut de gamme' END AS gamme,
       COUNT(*) AS nb_produits
FROM produits
GROUP BY gamme
ORDER BY MIN(prix_vente)
```
<!--sortie-->
```text
        gamme  nb_produits
   petit prix           43
        moyen           56
haut de gamme           21
```

Le catalogue compte 43 produits « petit prix », 56 « moyen » et 21 « haut de gamme » : les conditions du `CASE` sont évaluées **dans l'ordre**, la première vraie l'emporte, et le `ELSE` ramasse tout le reste. (Nous avons utilisé `GROUP BY` avant de l'avoir présenté : le principe est expliqué en 3.1.6.)

Les **dates** méritent une attention particulière, car une analyse de ventes est presque toujours une analyse **dans le temps**. En SQLite, la fonction `strftime(format, date)` extrait une partie de la date : `'%Y'` l'année, `'%m'` le mois, `'%Y-%m'` le mois complet, `'%w'` le jour de la semaine (0 pour le dimanche). Comptons les commandes par mois sur la fin de l'année 2025 :

```sql
SELECT strftime('%Y-%m', date_commande) AS mois, COUNT(*) AS nb_commandes
FROM commandes
WHERE date_commande >= '2025-07-01'
GROUP BY mois
ORDER BY mois
```
<!--sortie-->
```text
   mois  nb_commandes
2025-07           963
2025-08           788
2025-09          1097
2025-10          1150
2025-11          1509
2025-12          1853
```

Le volume passe de 963 commandes en juillet à 788 en août (creux estival), puis grimpe jusqu'à **1 853 en décembre**, soit près du double de juillet : la saisonnalité de fin d'année est forte. Le même mécanisme donne le profil de la semaine :

```sql
SELECT strftime('%w', date_commande) AS jour_semaine, COUNT(*) AS nb_commandes
FROM commandes
GROUP BY jour_semaine
ORDER BY jour_semaine
```
<!--sortie-->
```text
jour_semaine  nb_commandes
           0          3496
           1          4976
           2          4706
           3          4893
           4          5122
           5          5979
           6          7223
```

Avec `0` pour le dimanche et `6` pour le samedi, on lit que **le samedi est le jour le plus chargé** (7 223 commandes sur trois ans) et le dimanche le plus calme (3 496). Une réponse comme celle-ci se traduit directement en décision : la gérante saura quand renforcer l'équipe.

> 🧭 **En pratique : stocker des dates comme des dates.** Dans les bases qui ont un vrai type `DATE`, on écrit `date_commande >= DATE '2025-07-01'` et l'on dispose de fonctions d'extraction (`EXTRACT(YEAR FROM …)`, `DATE_TRUNC('month', …)`). Le principe est identique ; seuls les noms de fonctions changent (voir 3.6).

### 3.1.6 Agréger : COUNT, SUM, AVG, MIN, MAX et GROUP BY

Jusqu'ici, chaque ligne du résultat correspondait à une ligne de la table. L'**agrégation** change le grain : elle **résume** plusieurs lignes en une seule. Les cinq fonctions d'agrégation de base sont :

| Fonction | Rôle |
|---|---|
| `COUNT(*)` | nombre de lignes |
| `COUNT(colonne)` | nombre de lignes où la colonne **n'est pas absente** |
| `COUNT(DISTINCT colonne)` | nombre de valeurs **différentes** |
| `SUM(colonne)`, `AVG(colonne)` | somme, moyenne |
| `MIN(colonne)`, `MAX(colonne)` | plus petite, plus grande valeur |

Sans `GROUP BY`, l'agrégat porte sur **toute la table** et la requête renvoie une seule ligne. Voici les chiffres globaux des lignes de commande :

```sql
SELECT COUNT(*) AS nb_lignes,
       ROUND(SUM(montant), 2) AS ca,
       ROUND(AVG(montant), 2) AS montant_moyen_par_ligne,
       COUNT(DISTINCT id_commande) AS nb_commandes,
       ROUND(SUM(montant) / COUNT(DISTINCT id_commande), 2) AS panier_moyen
FROM lignes_commande
```
<!--sortie-->
```text
 nb_lignes         ca  montant_moyen_par_ligne  nb_commandes  panier_moyen
     83905 3653157.28                    43.54         36395        100.38
```

Le chiffre d'affaires cumulé des trois ans est de **3 653 157,28 €**. Remarquez la différence entre deux moyennes que l'on confond souvent : le **montant moyen par ligne** (43,54 €) et le **panier moyen** (100,38 €), c'est-à-dire le montant moyen **par commande**. Le panier moyen se calcule en divisant la somme par le nombre de **commandes distinctes** ; `AVG(montant)` moyenne, lui, des **lignes**. Les deux sont corrects, ils répondent à des questions différentes, et c'est à vous de choisir celle que la gérante pose.

Avec `GROUP BY`, la table est d'abord découpée en **paquets** (un par valeur de la colonne de regroupement), puis chaque agrégat est calculé **paquet par paquet**. Le résultat compte une ligne par paquet. Les statistiques du catalogue par catégorie :

```sql
SELECT categorie, COUNT(*) AS nb_produits,
       ROUND(AVG(prix_vente), 2) AS prix_moyen,
       MIN(prix_vente) AS prix_min, MAX(prix_vente) AS prix_max
FROM produits
GROUP BY categorie
```
<!--sortie-->
```text
 categorie  nb_produits  prix_moyen  prix_min  prix_max
 Bien-être           20       27.50       9.9      68.9
   Cuisine           20       34.75       9.9      57.9
Décoration           20       38.05      11.9      96.9
    Jardin           20       51.75       7.9     152.9
    Maison           20       51.85      12.9     126.9
 Papeterie           20       11.35       2.9      21.9
```

Chaque catégorie compte 20 produits ; la papeterie a le prix moyen le plus bas (11,35 €), la maison (51,85 €) et le jardin (51,75 €) les plus hauts. On peut regrouper par **plusieurs** colonnes : un paquet par combinaison. Les commandes par année et par canal :

```sql
SELECT strftime('%Y', date_commande) AS annee, canal, COUNT(*) AS nb_commandes
FROM commandes
GROUP BY annee, canal
ORDER BY annee, canal
```
<!--sortie-->
```text
annee    canal  nb_commandes
 2023 Boutique          5916
 2023  Réseaux          1230
 2023     Site          4272
 2024 Boutique          5617
 2024  Réseaux          1301
 2024     Site          5113
 2025 Boutique          5442
 2025  Réseaux          1426
 2025     Site          6078
```

On lit deux tendances en même temps : le **Site** progresse chaque année (4 272, 5 113 puis 6 078 commandes) tandis que la **Boutique** recule (5 916, 5 617 puis 5 442). Voilà de quoi alimenter la question que la gérante se pose depuis longtemps : *le site fait-il perdre des clients à la boutique ?* Ce tableau ne prouve rien (les clients du site sont-ils les mêmes ?), mais il oriente l'analyse, et c'est ce qu'on attend d'un premier regard.

> 💡 **Règle d'or du `GROUP BY`.** Dans un `SELECT` qui regroupe, chaque colonne est soit **dans le `GROUP BY`**, soit **à l'intérieur d'une fonction d'agrégation**. Il n'y a pas de troisième possibilité raisonnable : si vous affichiez une autre colonne, la base ne saurait pas laquelle des lignes du paquet choisir. (SQLite tolère l'écart et choisit une ligne au hasard ; la plupart des autres bases refusent la requête. Ne vous appuyez jamais dessus.)

### 3.1.7 HAVING et l'ordre logique d'exécution

`WHERE` filtre les **lignes** avant le regroupement. Pour filtrer sur le **résultat d'un agrégat** (« les clients qui ont passé au moins quinze commandes »), il faut une condition **après** le regroupement : c'est le rôle de `HAVING`.

```sql
SELECT id_client, COUNT(*) AS nb_commandes
FROM commandes
WHERE date_commande >= '2025-01-01'
GROUP BY id_client
HAVING COUNT(*) >= 15
ORDER BY nb_commandes DESC
LIMIT 5
```
<!--sortie-->
```text
 id_client  nb_commandes
      1360            25
      2987            23
      2997            21
      4782            20
        90            19
```

Le client numéro 1360 a passé 25 commandes en 2025, le 2987 en a passé 23. Ces deux conditions ne sont pas interchangeables : `WHERE date_commande >= …` agit sur chaque commande **avant** de les compter ; `HAVING COUNT(*) >= 15` agit sur le compte **une fois les paquets formés**. Pour ne pas se tromper, il faut connaître l'ordre dans lequel le moteur **exécute** une requête, qui n'est **pas** l'ordre dans lequel on l'écrit :


![L'ordre d'écriture d'une requête SQL (en haut) n'est pas l'ordre de son exécution (en bas) : le moteur commence par FROM et les jointures, filtre, regroupe, filtre les groupes, et seulement alors calcule les colonnes du SELECT, trie et limite.](figures/ch03-ordre-execution.png)

Cet ordre explique beaucoup de messages d'erreur et de comportements surprenants :

- On ne peut pas utiliser dans le `WHERE` le résultat d'un agrégat, puisque les groupes n'existent pas encore à l'étape 2 : c'est le travail de `HAVING`.
- Les alias définis dans le `SELECT` (étape 5) n'existent pas encore au moment du `WHERE` (étape 2). Beaucoup de bases refusent donc `WHERE marge > 10` si `marge` est un alias ; **SQLite l'accepte par tolérance**, PostgreSQL le refuse. Pour rester portable, on répète l'expression ou l'on passe par une étape intermédiaire (3.4).
- `ORDER BY`, lui, s'exécute après le `SELECT` : on peut trier sur un alias.

Un dernier exemple combine agrégat, sous-requête et pourcentage. La part de chaque canal dans l'ensemble des commandes :

```sql
SELECT canal, COUNT(*) AS nb_commandes,
       ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM commandes), 1) AS part_pct
FROM commandes
GROUP BY canal
ORDER BY nb_commandes DESC
```
<!--sortie-->
```text
   canal  nb_commandes  part_pct
Boutique         16975      46.6
    Site         15463      42.5
 Réseaux          3957      10.9
```

La boutique physique réalise 46,6 % des commandes, le site 42,5 %, les réseaux 10,9 %. La sous-requête `(SELECT COUNT(*) FROM commandes)` renvoie un nombre unique, utilisé comme dénominateur ; nous reverrons ces sous-requêtes en 3.5.

### 3.1.8 NULL : la valeur absente

En SQL, une cellule peut contenir une valeur **absente** : `NULL`. Ce n'est ni zéro, ni un texte vide : c'est « on ne sait pas » (une date de retour pour un article jamais retourné, un âge non renseigné). Cette idée a des conséquences, car **toute opération avec une valeur inconnue donne un résultat inconnu**. Quelques expériences pures :

```sql
SELECT NULL = NULL AS egal, NULL IS NULL AS est_nul,
       1 + NULL AS somme, COALESCE(NULL, 0) AS avec_defaut
```
<!--sortie-->
```text
egal  est_nul somme  avec_defaut
None        1  None            0
```

Le résultat est parlant : `NULL = NULL` n'est **pas vrai** (on ne peut pas affirmer que deux inconnues sont égales : le résultat est lui-même inconnu), il faut écrire `IS NULL` ; `1 + NULL` donne `NULL` ; et `COALESCE(x, y)` renvoie la première valeur qui n'est pas absente, ce qui permet de **remplacer** une absence par une valeur par défaut. On dit que le SQL a une **logique à trois valeurs** : vrai, faux, inconnu. Une condition `WHERE` ne garde que les lignes **vraies** : les lignes dont la condition est « inconnue » sont éliminées comme les fausses.

Les fonctions d'agrégation **ignorent** les valeurs absentes, ce qui provoque des erreurs silencieuses si l'on n'y prend garde. Prenons une petite table à trois lignes, `1`, `NULL` et `3` :

```sql
WITH t(x) AS (VALUES (1), (NULL), (3))
SELECT COUNT(*) AS nb_lignes, COUNT(x) AS nb_valeurs, SUM(x) AS somme, AVG(x) AS moyenne
FROM t
```
<!--sortie-->
```text
 nb_lignes  nb_valeurs  somme  moyenne
         3           2      4      2.0
```

`COUNT(*)` compte les **3 lignes**, `COUNT(x)` seulement les **2 valeurs présentes**, et la moyenne vaut 2 (= 4/2) et non 1,33 (= 4/3) : l'absence n'est pas comptée comme un zéro. (`WITH t(x) AS (VALUES …)` est une façon de poser une mini-table sans la créer ; nous la détaillons en 3.4.) De même, `WHERE x <> 1` **élimine** la ligne `NULL` : elle n'est ni égale à 1, ni différente de 1, elle est inconnue.

Reste le cas de la boutique, où l'absence de code promo est un **texte vide**. Comparons trois façons de compter :

```sql
SELECT COUNT(*) AS toutes,
       COUNT(code_promo) AS non_nulles,
       COUNT(NULLIF(code_promo, '')) AS avec_code
FROM commandes
```
<!--sortie-->
```text
 toutes  non_nulles  avec_code
  36395       36395       5743
```

`COUNT(code_promo)` renvoie 36 395, soit **toutes** les commandes : aucune valeur n'est `NULL`, puisque l'absence est codée par `''`. La fonction `NULLIF(x, '')` transforme le texte vide en `NULL`, et le comptage tombe à **5 743 commandes avec un code promo réel**. Retenez-le : **deux données qui « ont l'air vides » (`NULL`, `''`, `0`, `'N/A'`) ne sont pas la même absence**, et chaque base a ses conventions. C'est le travail de l'analyste de les découvrir avant de calculer.

### 3.1.9 Quatre pièges classiques

Nous avons croisé plusieurs pièges ; en voici quatre autres, que tout analyste rencontre un jour.

**1. La division entière.** Dans la plupart des bases (dont SQLite), diviser un entier par un entier renvoie un **entier** : `7 / 2` donne 3. Pour calculer une part, on force une division décimale en multipliant par `100.0` ou en divisant par `2.0`. Voici la part de lignes vendues avec une remise, calculée de façon naïve puis correcte :

```sql
SELECT SUM(CASE WHEN remise_pct > 0 THEN 1 ELSE 0 END) / COUNT(*) AS part_naive,
       ROUND(100.0 * SUM(CASE WHEN remise_pct > 0 THEN 1 ELSE 0 END) / COUNT(*), 1) AS part_pct
FROM lignes_commande
```
<!--sortie-->
```text
 part_naive  part_pct
          0      15.8
```

La version naïve donne **0** ; la bonne, 15,8 %. Ce piège est vicieux parce qu'**aucune erreur ne s'affiche** : on lirait « 0 % de remises » sans sourciller.

**2. La moyenne des moyennes.** La moyenne de deux moyennes n'est la moyenne de l'ensemble que si les groupes ont **la même taille**. Prenons deux canaux fictifs : A, avec 2 commandes de panier moyen 100 €, et B, avec 8 commandes de panier moyen 50 € :

```sql
WITH paniers(canal, nb_commandes, panier_moyen) AS (VALUES ('A', 2, 100.0), ('B', 8, 50.0))
SELECT ROUND(AVG(panier_moyen), 1) AS moyenne_des_moyennes,
       ROUND(SUM(nb_commandes * panier_moyen) / SUM(nb_commandes), 1) AS moyenne_ponderee
FROM paniers
```
<!--sortie-->
```text
 moyenne_des_moyennes  moyenne_ponderee
                 75.0              60.0
```

La moyenne naïve donne 75 €, la bonne (pondérée par le nombre de commandes) **60 €**. Sur les trois vrais canaux de la boutique l'écart est minuscule (nous le verrons en 3.4) parce que les paniers y sont très semblables ; la règle, elle, ne change pas : **on agrège toujours à partir du détail**, jamais à partir de résumés.

**3. `BETWEEN` et les heures.** `BETWEEN '2025-11-01' AND '2025-11-30'` inclut le 30 novembre **si la colonne ne contient que des dates**. Si elle contient aussi l'heure, `'2025-11-30 14:20'` est plus grand que `'2025-11-30'` et la dernière journée disparaît. Reconstituons un horodatage en collant la date et l'heure :

```sql
SELECT COUNT(*) AS avec_between_sur_horodatage
FROM commandes
WHERE date_commande || ' ' || heure BETWEEN '2025-11-01' AND '2025-11-30'
```
<!--sortie-->
```text
 avec_between_sur_horodatage
                        1461
```

On obtient **1 461** commandes au lieu des 1 509 de novembre vues plus haut : **48 commandes ont disparu**, toutes celles du 30. La parade est de borner **par le haut avec une inégalité stricte** : `>= '2025-11-01' AND < '2025-12-01'`, qui fonctionne qu'il y ait une heure ou non.

**4. Le `NULL` dans une comparaison.** Nous l'avons vu en 3.1.8 : `WHERE canal <> 'Site'` n'inclut **pas** les lignes où `canal` est `NULL`. Quand une colonne peut être absente, **demandez-vous toujours ce que devient la ligne absente**.

> ✅ **À retenir.**
> - Une table a un **grain** : sachez toujours ce que représente une ligne.
> - `WHERE` filtre les **lignes**, `HAVING` filtre les **groupes** ; l'ordre d'exécution est `FROM → WHERE → GROUP BY → HAVING → SELECT → ORDER BY → LIMIT`.
> - Dans un `SELECT` qui regroupe, chaque colonne est dans le `GROUP BY` ou dans un agrégat.
> - `NULL` n'est pas zéro : `= NULL` ne marche pas, les agrégats ignorent les absences, `COALESCE` et `NULLIF` sont vos outils.
> - Méfiez-vous des divisions entières, des moyennes de moyennes, des bornes de dates et de `LIMIT` sans `ORDER BY`.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.1 (découvrir la base), application 3.2 (les ventes par canal et par année), exercices 3.1 à 3.4.


## 3.2 Jointures

Les données d'une entreprise sont **réparties** entre plusieurs tables : les clients d'un côté, les commandes de l'autre, les produits ailleurs. Cette organisation évite de répéter cent fois l'adresse d'un client dans chacune de ses commandes ; en contrepartie, presque toute question utile (« combien chaque catégorie rapporte-t-elle ? », « quels clients n'ont jamais commandé ? ») oblige à **recoller** les morceaux. C'est le rôle des **jointures**. Elles sont aussi la principale source d'erreurs de chiffres dans le métier : cette section vous apprend à les écrire, et surtout à les **vérifier**.

### 3.2.1 Pourquoi joindre

Reprenons la commande 34177, passée sur le site pendant la semaine du « Vendredi noir ». Dans la table `lignes_commande`, elle apparaît sous forme de numéros : `id_produit`, `quantite`, `montant`. Pour savoir **de quel produit** il s'agit, il faut aller chercher le nom dans `produits`. On écrit la correspondance dans une clause `ON` :

```sql
SELECT c.id_commande, c.canal, p.nom_produit, l.quantite,
       l.prix_unitaire, l.remise_pct, l.montant
FROM commandes c
JOIN lignes_commande l ON l.id_commande = c.id_commande
JOIN produits p ON p.id_produit = l.id_produit
WHERE c.id_commande = 34177
```
<!--sortie-->
```text
 id_commande canal  nom_produit  quantite  prix_unitaire  remise_pct  montant
       34177  Site Lanterne mat         2         121.44          20   194.30
       34177  Site Lanterne mat         1         121.44          20    97.15
```

La commande contient deux lignes du même article, une lanterne vendue 121,44 € l'unité avec 20 % de remise : 194,30 € pour deux, 97,15 € pour une seule. Trois tables, deux jointures, un seul `SELECT`. Quelques conventions de lecture :

- `commandes c` donne à la table un **alias court** (`c`) pour ne pas avoir à écrire son nom en entier ; `c.id_commande` se lit « la colonne `id_commande` de `c` ».
- **Préfixer chaque colonne par son alias** évite l'ambiguïté (deux tables ont une colonne `id_commande`) et rend la requête lisible : on voit d'où vient chaque information.
- `JOIN … ON a = b` dit comment recoller : les lignes dont les deux valeurs sont égales. Quand les deux colonnes portent le même nom, `USING (id_commande)` est un raccourci.

### 3.2.2 INNER JOIN : ne garder que les correspondances

`JOIN` seul est un raccourci de **`INNER JOIN`** : on ne garde que les lignes qui ont une correspondance **des deux côtés**. Pour voir ce que cela implique, utilisons de minuscules tables inventées, deux clients (Ana, Bao, Chloé) et quatre commandes :

```sql
WITH clients_mini(id, nom) AS (VALUES (1, 'Ana'), (2, 'Bao'), (3, 'Chloé')),
     cmd_mini(id_cmd, id_client, montant) AS
       (VALUES (10, 1, 30.0), (11, 1, 20.0), (12, 3, 50.0), (13, 4, 10.0))
SELECT c.nom, m.id_cmd, m.montant
FROM clients_mini c
JOIN cmd_mini m ON m.id_client = c.id
```
<!--sortie-->
```text
  nom  id_cmd  montant
  Ana      10     30.0
  Ana      11     20.0
Chloé      12     50.0
```

Le résultat compte trois lignes : Ana avec ses deux commandes, Chloé avec la sienne. **Bao a disparu** (elle n'a passé aucune commande) et **la commande 13 aussi** (son client, le numéro 4, n'existe pas dans la table des clients). C'est l'effet d'une jointure interne : toute ligne sans partenaire est écartée, silencieusement. La figure de la page suivante résume les quatre grandes jointures sur deux tables de trois lignes.


![Deux tables de trois lignes jointes sur leur clé : la jointure interne garde les correspondances, la jointure à gauche garde toutes les lignes de la première table, la jointure à droite toutes celles de la seconde, la jointure complète les deux ; les lignes sans correspondance sont complétées par des valeurs absentes.](figures/ch03-jointures.png)

Passons aux vraies données. Quel chiffre d'affaires chaque catégorie de produits a-t-elle réalisé en 2025 ? Il faut recoller **trois tables** : les lignes (qui portent le montant), les commandes (qui portent la date) et les produits (qui portent la catégorie).

```sql
SELECT p.categorie, COUNT(*) AS nb_lignes, ROUND(SUM(l.montant), 0) AS ca
FROM lignes_commande l
JOIN commandes c ON c.id_commande = l.id_commande
JOIN produits p ON p.id_produit = l.id_produit
WHERE c.date_commande >= '2025-01-01'
GROUP BY p.categorie
ORDER BY ca DESC
```
<!--sortie-->
```text
 categorie  nb_lignes       ca
    Jardin       5393 353955.0
    Maison       5300 304614.0
Décoration       5897 258742.0
   Cuisine       5141 233313.0
 Bien-être       3675 117511.0
 Papeterie       4421  56629.0
```

Le **jardin** arrive en tête (353 955 €), devant la maison (304 614 €) et la décoration (258 742 €) ; la papeterie ferme la marche (56 629 €). Pour vérifier le résultat, additionnez les six chiffres d'affaires : on retrouve **1 324 764 €**, le chiffre d'affaires total de 2025 que nous obtiendrons de façon indépendante en 3.4. Quand une jointure ne perd ni ne duplique de lignes, **les sous-totaux se recoupent avec le total**. Faire ce contrôle est un réflexe d'analyste.

### 3.2.3 LEFT JOIN : garder tout le monde

La jointure à gauche (`LEFT JOIN`) conserve **toutes les lignes de la table de gauche**, qu'elles aient ou non une correspondance à droite ; les colonnes de droite sont alors remplies de `NULL`. C'est l'outil des questions de type « quels sont ceux qui n'ont pas… ». Combien de clients inscrits n'ont **jamais** commandé, et d'où viennent-ils ?

```sql
SELECT c.canal_acquisition, COUNT(*) AS clients_sans_commande
FROM clients c
LEFT JOIN commandes o ON o.id_client = c.id_client
WHERE o.id_commande IS NULL
GROUP BY c.canal_acquisition
```
<!--sortie-->
```text
canal_acquisition  clients_sans_commande
         Boutique                    580
          Réseaux                    157
             Site                    457
```

Le motif est toujours le même : on joint à gauche, puis on garde les lignes où une colonne **de la table de droite** (idéalement sa clé) est `NULL`. On appelle cela une **anti-jointure**. Le résultat montre 580 clients de la boutique, 457 du site et 157 des réseaux, soit **1 194 clients** (un sur cinq) qui n'ont encore rien acheté : un public naturel pour une campagne de première commande. Il existe une autre écriture, souvent plus lisible, avec `NOT EXISTS` :

```sql
SELECT COUNT(*) AS clients_sans_commande
FROM clients c
WHERE NOT EXISTS (SELECT 1 FROM commandes o WHERE o.id_client = c.id_client)
```
<!--sortie-->
```text
 clients_sans_commande
                  1194
```

Elle renvoie bien les mêmes 1 194 clients. Les deux formulations sont équivalentes ; choisissez celle qui se lit le mieux (nous détaillons `EXISTS` en 3.5).

> ⚠️ **Piège : le filtre sur la table de droite, dans le `WHERE`.** Combien de clients n'ont **pas** commandé en 2025 ? L'écriture naturelle semble être : `LEFT JOIN commandes o ON … WHERE o.date_commande >= '2025-01-01' AND o.id_commande IS NULL`. Exécutons-la :

```sql
SELECT COUNT(*) AS clients_sans_commande_2025_faux
FROM clients c
LEFT JOIN commandes o ON o.id_client = c.id_client
WHERE o.date_commande >= '2025-01-01' AND o.id_commande IS NULL
```
<!--sortie-->
```text
 clients_sans_commande_2025_faux
                               0
```

Elle renvoie **0 ligne**, ce qui est absurde : la condition `o.date_commande >= …` est fausse quand `o` est absente (`NULL`), donc le `WHERE` **élimine** précisément les lignes que le `LEFT JOIN` voulait garder, et la jointure à gauche se comporte comme une jointure interne. La bonne écriture met le filtre **dans le `ON`** :

```sql
SELECT COUNT(*) AS clients_sans_commande_2025
FROM clients c
LEFT JOIN commandes o ON o.id_client = c.id_client AND o.date_commande >= '2025-01-01'
WHERE o.id_commande IS NULL
```
<!--sortie-->
```text
 clients_sans_commande_2025
                       2125
```

On obtient **2 125 clients** sans commande en 2025 (6 000 clients au total, 3 875 actifs en 2025 : 6 000 − 3 875 = 2 125). La règle : **une condition qui décrit *quelles lignes de droite peuvent correspondre* va dans le `ON` ; une condition qui décrit *quelles lignes finales on garde* va dans le `WHERE`.**

Les anti-jointures servent aussi à **contrôler l'intégrité** d'une base dont les clés ne sont pas déclarées, comme la nôtre. Combien de lignes de commande désignent un produit inexistant, de commandes sans aucune ligne, de commandes dont le client est inconnu ?

```sql
SELECT 'lignes sans produit' AS controle, COUNT(*) AS nb
FROM lignes_commande l LEFT JOIN produits p ON p.id_produit = l.id_produit WHERE p.id_produit IS NULL
UNION ALL
SELECT 'commandes sans ligne', COUNT(*)
FROM commandes c LEFT JOIN lignes_commande l ON l.id_commande = c.id_commande WHERE l.id_ligne IS NULL
UNION ALL
SELECT 'commandes de client inconnu', COUNT(*)
FROM commandes c LEFT JOIN clients cl ON cl.id_client = c.id_client WHERE cl.id_client IS NULL
```
<!--sortie-->
```text
                   controle  nb
        lignes sans produit   0
       commandes sans ligne   0
commandes de client inconnu   0
```

Les trois contrôles renvoient **0** : la base est cohérente. Sur un vrai système, ce genre de requête est lancé à chaque chargement de données ; un résultat non nul est un message à destination de l'équipe qui fournit les données.

### 3.2.4 RIGHT JOIN et FULL JOIN

La jointure à droite (`RIGHT JOIN`) est le symétrique de la jointure à gauche : elle garde toutes les lignes de la table de droite. En pratique, **on l'évite** : inverser l'ordre des tables et utiliser `LEFT JOIN` dit la même chose et se lit mieux. La jointure complète (`FULL JOIN`) garde **les deux** côtés : elle sert à **comparer deux sources** et à repérer à la fois ce qui manque d'un côté et de l'autre.

```sql
WITH a(k, v) AS (VALUES ('A', 'a1'), ('B', 'b1'), ('C', 'c1')),
     b(k, w) AS (VALUES ('B', 'b2'), ('C', 'c2'), ('D', 'd2'))
SELECT a.k AS k_a, b.k AS k_b, v, w
FROM a FULL JOIN b ON a.k = b.k
```
<!--sortie-->
```text
k_a k_b   v   w
  A NaN  a1 NaN
  B   B  b1  b2
  C   C  c1  c2
NaN   D NaN  d2
```

Les clés `B` et `C` sont communes ; `A` n'existe que dans la première table (les colonnes de `b` sont absentes), `D` que dans la seconde. Les versions récentes de SQLite (à partir de la 3.39), PostgreSQL, SQL Server et Oracle savent faire un `FULL JOIN`. **MySQL ne le connaît pas** : on l'émule alors en empilant deux jointures à gauche, la seconde limitée aux lignes qui n'ont pas de partenaire :

```sql
SELECT a.k AS k_a, b.k AS k_b, v, w FROM a LEFT JOIN b ON a.k = b.k
UNION ALL
SELECT a.k, b.k, v, w FROM b LEFT JOIN a ON a.k = b.k WHERE a.k IS NULL
```

Nous ne l'exécutons pas ici (les tables `a` et `b` n'existent que le temps de la requête précédente, et SQLite sait faire le `FULL JOIN`) ; c'est un schéma à retenir pour les moteurs qui n'en disposent pas.

### 3.2.5 CROSS JOIN et auto-jointure

Le **`CROSS JOIN`** associe **chaque ligne** de la première table à **chaque ligne** de la seconde, sans regarder aucune clé : trois lignes par trois lignes donnent neuf lignes. C'est un outil précieux pour fabriquer une **grille complète** de combinaisons, y compris celles qui n'existent pas dans les données. Quelles combinaisons canal × mode de livraison la boutique observe-t-elle ?

```sql
WITH canaux(canal) AS (VALUES ('Boutique'), ('Site'), ('Réseaux')),
     modes(mode_livraison) AS (VALUES ('Domicile'), ('Point relais'), ('Retrait magasin'))
SELECT k.canal, m.mode_livraison, COUNT(c.id_commande) AS nb_commandes
FROM canaux k CROSS JOIN modes m
LEFT JOIN commandes c ON c.canal = k.canal AND c.mode_livraison = m.mode_livraison
GROUP BY k.canal, m.mode_livraison
ORDER BY k.canal, m.mode_livraison
```
<!--sortie-->
```text
   canal  mode_livraison  nb_commandes
Boutique        Domicile             0
Boutique    Point relais             0
Boutique Retrait magasin         16975
 Réseaux        Domicile          2164
 Réseaux    Point relais          1519
 Réseaux Retrait magasin           274
    Site        Domicile          8573
    Site    Point relais          5791
    Site Retrait magasin          1099
```

Sans la grille, un simple `GROUP BY canal, mode_livraison` aurait renvoyé sept lignes seulement et **n'aurait jamais montré** que la boutique n'offre ni livraison à domicile ni point relais (deux lignes à 0). Avec elle, les combinaisons impossibles apparaissent explicitement. Notez le `COUNT(c.id_commande)`, et non `COUNT(*)` : il compte les commandes **réellement présentes** (zéro pour les lignes complétées), alors que `COUNT(*)` compterait la ligne de la grille elle-même et donnerait 1.

Une **auto-jointure** joint une table **avec elle-même**, sous deux alias différents. Elle sert à comparer des lignes entre elles. Un client a-t-il passé deux commandes le même jour (doublon de saisie, ou commande oubliée complétée après coup) ?

```sql
SELECT a.id_client, a.date_commande, a.id_commande AS cmd_1, b.id_commande AS cmd_2
FROM commandes a
JOIN commandes b ON a.id_client = b.id_client
                AND a.date_commande = b.date_commande
                AND a.id_commande < b.id_commande
WHERE a.date_commande >= '2025-12-01'
LIMIT 5
```
<!--sortie-->
```text
 id_client date_commande  cmd_1  cmd_2
      3330    2025-12-03  34699  34701
       487    2025-12-08  34988  35000
      3737    2025-12-09  35071  35085
      3937    2025-12-11  35192  35209
      2723    2025-12-16  35464  35483
```

La condition `a.id_commande < b.id_commande` est l'astuce standard : elle garde chaque **paire** une seule fois (sans elle, la paire (1, 2) apparaîtrait aussi sous la forme (2, 1), et chaque commande serait comparée à elle-même). La même requête, sans le filtre de décembre ni la limite, donne le total sur les trois ans :

```text
 nb_paires_sur_trois_ans
                     321
```

On compte **321 paires** de ce type : à étudier avant de conclure à une erreur, car un client peut très bien passer deux commandes dans la journée.

### 3.2.6 Le piège de la multiplication des lignes

C'est **la** source d'erreurs de chiffres du métier. Rappelons la règle : une jointure « un à plusieurs » **recopie** chaque ligne du côté « un » autant de fois qu'elle a de correspondances du côté « plusieurs ». Les colonnes du côté « un » se retrouvent alors **multipliées**, et toute somme sur ces colonnes est fausse.

Un exemple concret avec le budget publicitaire. La table `jours_exploitation` contient la dépense publicitaire de chaque **jour** ; la table `commandes` contient plusieurs commandes par jour. Si l'on joint les deux sur la date, la dépense d'un jour est recopiée **une fois par commande** de ce jour-là :


![Un jour de dépense publicitaire de 150 € joint aux trois commandes de ce jour : la dépense apparaît trois fois dans le résultat, et la somme passe de 150 € à 450 €.](figures/ch03-multiplication.png)

Voyons l'effet sur les vraies données. La dépense publicitaire de 2025, sommée directement, puis après la jointure :

```sql
SELECT ROUND(SUM(depense_pub), 0) AS pub_2025
FROM jours_exploitation WHERE date >= '2025-01-01';

SELECT ROUND(SUM(j.depense_pub), 0) AS pub_apres_jointure
FROM jours_exploitation j
JOIN commandes c ON c.date_commande = j.date
WHERE j.date >= '2025-01-01'
```
<!--sortie-->
```text
 pub_2025
  75995.0

 pub_apres_jointure
          2991731.0
```

Le budget réel est de **75 995 €**. La jointure en affiche **2 991 731 €**, soit près de **quarante fois trop** : chaque jour a été compté autant de fois qu'il comptait de commandes (une trentaine en moyenne). Ce genre d'erreur se produit **sans message d'erreur**, et le résultat n'a rien d'absurde au premier regard : un directeur marketing qui lirait trois millions d'euros de publicité aurait d'abord un doute sur les données, pas sur la requête.

Même phénomène, plus discret, pour un simple comptage. Combien de commandes y a-t-il après jointure avec leurs lignes ?

```sql
SELECT COUNT(*) AS nb_lignes_jointes, COUNT(DISTINCT c.id_commande) AS nb_commandes
FROM commandes c
JOIN lignes_commande l ON l.id_commande = c.id_commande
```
<!--sortie-->
```text
 nb_lignes_jointes  nb_commandes
             83905         36395
```

`COUNT(*)` renvoie **83 905** (le nombre de lignes de commande), alors que la base compte **36 395 commandes** ; seul `COUNT(DISTINCT id_commande)` rend la bonne réponse. La règle est donc de **toujours savoir le grain du résultat d'une jointure** : après avoir joint commandes et lignes, une ligne est une **ligne de commande**, pas une commande.

Trois parades, par ordre de préférence :

1. **Agréger avant de joindre.** Ramenez le côté « plusieurs » au grain du côté « un » (par exemple, un nombre de commandes **par jour**), puis joignez. La jointure devient « un à un » et plus rien n'est recopié :

```sql
SELECT ROUND(SUM(j.depense_pub), 0) AS pub_2025
FROM jours_exploitation j
LEFT JOIN (SELECT date_commande, COUNT(*) AS nb FROM commandes GROUP BY date_commande) c
       ON c.date_commande = j.date
WHERE j.date >= '2025-01-01'
```
<!--sortie-->
```text
 pub_2025
  75995.0
```

On retrouve les **75 995 €** : la jointure à un seul partenaire par jour ne multiplie rien.

2. **Compter des éléments distincts** (`COUNT(DISTINCT …)`) quand on ne peut pas éviter la jointure.
3. **Contrôler**, avant et après chaque jointure, **le nombre de lignes** et **une somme connue**. Si `SUM(montant)` change, ou si le nombre de lignes dépasse celui de la table « un », c'est qu'une multiplication a eu lieu.

> 🧭 **En pratique : le test des trois comptes.** Avant de livrer un chiffre issu d'une jointure, comparez : (1) le nombre de lignes de la table de départ, (2) le nombre de lignes après jointure, (3) un total de référence calculé sans jointure. Vous attrapez ainsi 90 % des erreurs de jointure en moins d'une minute.

### 3.2.7 Empiler et comparer des ensembles

Une jointure **élargit** une table en largeur ; les opérations ensemblistes **empilent** ou **comparent** des résultats de même forme (même nombre de colonnes, types compatibles).

| Opérateur | Résultat |
|---|---|
| `UNION ALL` | toutes les lignes des deux résultats, doublons compris |
| `UNION` | toutes les lignes, **sans doublons** (plus coûteux : la base doit chercher les doublons) |
| `INTERSECT` | les lignes présentes **dans les deux** |
| `EXCEPT` | les lignes du premier résultat **absentes du second** |

`INTERSECT` et `EXCEPT` répondent élégamment à des questions de **fidélisation**. Parmi les clients actifs, combien sont fidèles (déjà clients avant 2025), combien sont nouveaux, et combien a-t-on perdus ?

```sql
SELECT 'fidèles (avant et en 2025)' AS groupe, COUNT(*) AS nb_clients FROM (
  SELECT id_client FROM commandes WHERE date_commande >= '2025-01-01'
  INTERSECT SELECT id_client FROM commandes WHERE date_commande < '2025-01-01')
UNION ALL SELECT 'nouveaux en 2025', COUNT(*) FROM (
  SELECT id_client FROM commandes WHERE date_commande >= '2025-01-01'
  EXCEPT SELECT id_client FROM commandes WHERE date_commande < '2025-01-01')
UNION ALL SELECT 'perdus (avant, pas en 2025)', COUNT(*) FROM (
  SELECT id_client FROM commandes WHERE date_commande < '2025-01-01'
  EXCEPT SELECT id_client FROM commandes WHERE date_commande >= '2025-01-01')
```
<!--sortie-->
```text
                     groupe  nb_clients
 fidèles (avant et en 2025)        3133
           nouveaux en 2025         742
perdus (avant, pas en 2025)         931
```

On compte **3 133 clients fidèles**, **742 nouveaux** et **931 perdus**. Les deux premiers font **3 875** clients actifs en 2025, le chiffre de la section 3.1 : les groupes se recoupent, la requête est cohérente. Notez enfin que `INTERSECT` et `EXCEPT` **éliminent les doublons** d'eux-mêmes, ce qui évite d'avoir à écrire `DISTINCT` : un client est compté une fois, qu'il ait passé une ou vingt commandes.

> ⚠️ **Piège : `UNION` ou `UNION ALL` ?** `UNION` supprime les doublons, ce qui peut **effacer des lignes légitimes** (deux ventes identiques le même jour). Si vous empilez deux périodes sans chevauchement, utilisez `UNION ALL` : c'est plus rapide et ça ne perd rien.

### 3.2.8 Joindre sur plusieurs colonnes

Il arrive que la clé d'une table soit **composée** : une ligne d'objectifs est identifiée par un couple (année, canal). On joint alors sur **toutes** les colonnes de la clé, reliées par `AND`. Comparons les objectifs de chiffre d'affaires de la direction (valeurs inventées) à la réalité :

```sql
WITH objectifs(annee, canal, objectif) AS (VALUES
       ('2024', 'Boutique', 600000), ('2024', 'Site', 500000),
       ('2025', 'Boutique', 580000), ('2025', 'Site', 650000)),
     reel AS (SELECT strftime('%Y', c.date_commande) AS annee, c.canal, SUM(l.montant) AS ca
              FROM commandes c JOIN lignes_commande l USING (id_commande) GROUP BY 1, 2)
SELECT o.annee, o.canal, o.objectif, ROUND(r.ca, 0) AS reel,
       ROUND(100.0 * r.ca / o.objectif, 1) AS atteinte_pct
FROM objectifs o JOIN reel r ON r.annee = o.annee AND r.canal = o.canal
ORDER BY 1, 2
```
<!--sortie-->
```text
annee    canal  objectif     reel  atteinte_pct
 2024 Boutique    600000 558143.0          93.0
 2024     Site    500000 502531.0         100.5
 2025 Boutique    580000 560974.0          96.7
 2025     Site    650000 617715.0          95.0
```

Le site dépasse de peu son objectif de 2024 (100,5 %), mais manque celui de 2025 de cinq points (95,0 %) ; la boutique reste sous les siens (93,0 % en 2024, 96,7 % en 2025). Oublier **une** des deux colonnes de la clé (joindre seulement sur `canal`) aurait associé chaque objectif aux chiffres de **toutes** les années, et multiplié les lignes (retour au piège précédent). Une jointure sur clé composite se vérifie donc, elle aussi, par le **nombre de lignes** : ici, quatre lignes en entrée, quatre lignes en sortie.

> ✅ **À retenir.**
> - Une jointure recolle des tables sur une **clé** ; `INNER` garde les correspondances, `LEFT` garde tout le côté gauche, `FULL` garde les deux, `CROSS` fait toutes les combinaisons.
> - Une anti-jointure (`LEFT JOIN … WHERE droite.clé IS NULL`, ou `NOT EXISTS`) répond aux questions « qui n'a pas… ». Le filtre qui définit les correspondances possibles va dans le `ON`.
> - **Le grain du résultat est celui de la table « plusieurs »** : après une jointure un-à-plusieurs, toute somme sur une colonne du côté « un » est multipliée. Agrégez avant de joindre, ou comptez des éléments distincts.
> - Contrôlez toujours le **nombre de lignes** et **un total connu** avant et après une jointure.
> - `UNION ALL` empile, `INTERSECT` et `EXCEPT` comparent des ensembles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.3 (les meilleurs clients), application 3.4 (panier moyen et double comptage), exercices 3.5 à 3.8.


## 3.3 Fonctions fenêtres

Le `GROUP BY` écrase les lignes : une ligne par groupe, et le détail est perdu. Or beaucoup de questions d'analyse demandent **les deux à la fois** : garder chaque ligne **et** la situer par rapport à son groupe (sa part du total du client, son rang dans sa catégorie, l'écart avec le mois précédent, le cumul depuis janvier). Les **fonctions fenêtres** (*window functions*) répondent exactement à ce besoin. Elles sont l'outil le plus puissant que vous apprendrez dans ce chapitre : une fois maîtrisées, elles remplacent des dizaines de lignes de tableur ou de code.

### 3.3.1 Agréger sans perdre le détail

Voici un exemple simple. Pour un client donné (le numéro 2), on veut afficher chacune de ses lignes d'achat de 2025 **et** la part qu'elle représente dans ses achats de l'année :

```sql
SELECT c.id_commande, c.id_client, ROUND(l.montant, 2) AS montant,
       ROUND(SUM(l.montant) OVER (PARTITION BY c.id_client), 2) AS total_client,
       ROUND(100 * l.montant / SUM(l.montant) OVER (PARTITION BY c.id_client), 1) AS part_pct
FROM commandes c
JOIN lignes_commande l USING (id_commande)
WHERE c.id_client = 2 AND c.date_commande >= '2025-01-01'
ORDER BY c.id_commande
LIMIT 5
```
<!--sortie-->
```text
 id_commande  id_client  montant  total_client  part_pct
       29212          2    24.62        211.18      11.7
       30003          2    24.52        211.18      11.6
       30003          2    28.74        211.18      13.6
       30003          2    22.56        211.18      10.7
       35090          2    21.43        211.18      10.1
```

Chaque ligne d'achat est conservée, et deux colonnes nouvelles apparaissent : le **total du client** (211,18 €, répété sur chaque ligne) et la **part** de la ligne dans ce total (de 10,1 % à 13,6 % ici). L'expression `SUM(l.montant) OVER (PARTITION BY c.id_client)` se lit : « *la somme de `montant`, calculée sur la fenêtre formée par toutes les lignes du même client* ». La somme n'est **pas** un `GROUP BY` : aucune ligne n'a été réduite. Avec un `GROUP BY id_client`, le résultat aurait compté une seule ligne par client et la part de chaque ligne aurait été impossible à calculer.

> 💡 **Intuition.** Une fonction fenêtre fait deux choses. Pour **chaque ligne**, elle regarde un ensemble de lignes voisines (la **fenêtre**) et calcule un résultat sur cet ensemble, puis elle **attache** ce résultat à la ligne. La fenêtre est définie par la clause `OVER (…)`.

### 3.3.2 Anatomie d'une fonction fenêtre

Une fonction fenêtre a toujours la même forme : `fonction(…) OVER (PARTITION BY … ORDER BY … cadre)`. Chaque élément de la parenthèse est facultatif.

| Élément | Rôle | Exemple |
|---|---|---|
| `PARTITION BY` | découpe les lignes en **paquets** indépendants, comme `GROUP BY` mais sans les réduire | `PARTITION BY id_client` |
| `ORDER BY` | **ordonne** les lignes à l'intérieur du paquet (indispensable pour un classement ou un cumul) | `ORDER BY date_commande` |
| **cadre** (*frame*) | précise **quelles lignes** autour de la ligne courante entrent dans le calcul | `ROWS BETWEEN 2 PRECEDING AND CURRENT ROW` |

Trois familles de fonctions s'utilisent après `OVER` : les fonctions d'**agrégation** vues en 3.1 (`SUM`, `AVG`, `COUNT`, `MIN`, `MAX`), les fonctions de **classement** (`ROW_NUMBER`, `RANK`, `DENSE_RANK`, `NTILE`) et les fonctions de **décalage** (`LAG`, `LEAD`, `FIRST_VALUE`, `LAST_VALUE`).

Un point technique décide de la correction de vos requêtes : **les fonctions fenêtres sont calculées après `WHERE`, `GROUP BY` et `HAVING`**, à l'étape du `SELECT` (la figure de la section 3.1.7). Conséquence : un `WHERE` **supprime des lignes avant** que la fenêtre ne les voie. Prenons l'évolution mensuelle du chiffre d'affaires, calculée avec `LAG`, qui renvoie la valeur de la ligne précédente. Si l'on filtre sur 2025 dans le même niveau de requête que le `LAG`, le mois de décembre 2024 n'existe plus et janvier n'a pas de « mois précédent » :

```sql
WITH mensuel AS (
  SELECT strftime('%Y-%m', c.date_commande) AS mois, ROUND(SUM(l.montant), 0) AS ca
  FROM commandes c JOIN lignes_commande l USING (id_commande)
  GROUP BY mois)
SELECT mois, ca, LAG(ca) OVER (ORDER BY mois) AS ca_precedent
FROM mensuel
WHERE mois >= '2025-01'
ORDER BY mois
LIMIT 3
```
<!--sortie-->
```text
   mois      ca  ca_precedent
2025-01 89179.0           NaN
2025-02 72642.0       89179.0
2025-03 89787.0       72642.0
```

Le chiffre d'affaires de janvier 2025 (89 179 €) n'a pas de mois précédent (`NaN`, une valeur absente), alors que décembre 2024 existe bel et bien. **Le filtre a été appliqué avant la fenêtre.** La parade consiste à calculer la fenêtre dans une étape, puis à filtrer dans l'étape suivante (ici, deux niveaux avec `WITH`) :

```sql
WITH mensuel AS (
  SELECT strftime('%Y-%m', c.date_commande) AS mois, ROUND(SUM(l.montant), 0) AS ca
  FROM commandes c JOIN lignes_commande l USING (id_commande)
  GROUP BY mois),
evol AS (SELECT mois, ca, LAG(ca) OVER (ORDER BY mois) AS ca_precedent FROM mensuel)
SELECT mois, ca, ca_precedent,
       ROUND(100.0 * (ca - ca_precedent) / ca_precedent, 1) AS evolution_pct
FROM evol
WHERE mois >= '2025-07'
ORDER BY mois
```
<!--sortie-->
```text
   mois       ca  ca_precedent  evolution_pct
2025-07 111221.0      106930.0            4.0
2025-08  89898.0      111221.0          -19.2
2025-09 113453.0       89898.0           26.2
2025-10 120064.0      113453.0            5.8
2025-11 143892.0      120064.0           19.8
2025-12 183845.0      143892.0           27.8
```

(`WITH nom AS (requête)` met une requête de côté sous un nom ; nous le détaillons en 3.4.) Le tableau est précieux pour une analyste : août perd **19,2 %** (creux estival), septembre regagne 26,2 %, et la fin d'année accélère (+19,8 % en novembre, **+27,8 % en décembre**). La question « le chiffre d'affaires baisse-t-il en août ? » se règle par un décalage, sans copier une seule cellule.

### 3.3.3 Classer : ROW_NUMBER, RANK, DENSE_RANK

Les trois fonctions de classement numérotent les lignes selon un ordre. Elles diffèrent **sur les ex æquo** :

| Fonction | Ex æquo | Exemple de numérotation (valeurs 506, 506, 493, 467) |
|---|---|---|
| `ROW_NUMBER()` | numéros **tous différents** (l'un des ex æquo passe avant l'autre, arbitrairement) | 1, 2, 3, 4 |
| `RANK()` | **même rang**, puis un « trou » | 1, 1, 3, 4 |
| `DENSE_RANK()` | même rang, **sans trou** | 1, 1, 2, 3 |

Regardons-le sur les cinq produits de la papeterie les plus vendus en 2025 (en quantités), où deux articles sont à égalité :

```sql
WITH ventes AS (
  SELECT p.nom_produit, SUM(l.quantite) AS qte
  FROM lignes_commande l JOIN commandes c USING (id_commande) JOIN produits p USING (id_produit)
  WHERE c.date_commande >= '2025-01-01' AND p.categorie = 'Papeterie'
  GROUP BY p.id_produit)
SELECT nom_produit, qte,
       ROW_NUMBER() OVER (ORDER BY qte DESC) AS rn,
       RANK() OVER (ORDER BY qte DESC) AS rang,
       DENSE_RANK() OVER (ORDER BY qte DESC) AS rang_dense
FROM ventes ORDER BY qte DESC LIMIT 5
```
<!--sortie-->
```text
      nom_produit  qte  rn  rang  rang_dense
  Cahier nordique  506   1     1           1
     Stylo design  506   2     1           1
       Carnet mat  493   3     3           2
   Agenda compact  467   4     4           3
Classeur rustique  402   5     5           4
```

« Cahier nordique » et « Stylo design » ont vendu **506** unités chacun : `ROW_NUMBER` les départage arbitrairement (1 puis 2), `RANK` leur donne le rang 1 à tous les deux puis saute au rang 3, `DENSE_RANK` passe au rang 2 sans trou. Le choix dépend de la question : pour **garder exactement les n premiers**, utilisez `ROW_NUMBER` (et un critère de départage explicite) ; pour **garder tous les gagnants**, `RANK`.

L'usage le plus fréquent est le **top-N par groupe** : « *le produit le plus vendu de chaque catégorie* ». `PARTITION BY` recommence le classement à chaque catégorie. Comme on ne peut pas filtrer directement sur le résultat d'une fonction fenêtre (elle est calculée après le `WHERE`), on filtre dans une requête extérieure :

```sql
SELECT categorie, nom_produit, qte FROM (
  SELECT p.categorie, p.nom_produit, SUM(l.quantite) AS qte,
         RANK() OVER (PARTITION BY p.categorie ORDER BY SUM(l.quantite) DESC) AS rang
  FROM lignes_commande l JOIN commandes c USING (id_commande) JOIN produits p USING (id_produit)
  WHERE c.date_commande >= '2025-01-01'
  GROUP BY p.id_produit)
WHERE rang = 1
ORDER BY categorie
```
<!--sortie-->
```text
 categorie        nom_produit  qte
 Bien-être     Savon nordique  447
   Cuisine Casserole nordique  596
Décoration           Vase mat  698
    Jardin  Arrosoir nordique  675
    Maison     Plaid nordique  659
 Papeterie    Cahier nordique  506
 Papeterie       Stylo design  506
```

La « Casserole nordique » domine la cuisine (596 unités), le « Vase mat » la décoration (698), l'« Arrosoir nordique » le jardin (675). Dans la papeterie, **deux** produits sortent, puisque `RANK` conserve les ex æquo : le résultat compte sept lignes pour six catégories. Notez aussi qu'une fonction fenêtre peut s'appliquer **à un agrégat** (`SUM(l.quantite)` à l'intérieur de `RANK() OVER`) : le `GROUP BY` s'exécute d'abord, la fenêtre classe ensuite les groupes.

### 3.3.4 Comparer à la ligne précédente : LAG et LEAD

`LAG(colonne)` renvoie la valeur de la ligne **précédente** dans l'ordre de la fenêtre, `LEAD(colonne)` celle de la ligne **suivante** ; un second argument choisit le nombre de lignes (`LAG(x, 2)`). Elles servent à calculer des **écarts**, des **variations** (comme plus haut) et des **durées entre événements**. Combien de temps s'écoule-t-il entre deux commandes successives d'un même client ?

```sql
SELECT id_client, date_commande,
       LAG(date_commande) OVER (PARTITION BY id_client ORDER BY date_commande, id_commande) AS commande_precedente,
       CAST(julianday(date_commande) - julianday(LAG(date_commande)
            OVER (PARTITION BY id_client ORDER BY date_commande, id_commande)) AS INTEGER) AS ecart_jours
FROM commandes
WHERE id_client = 2
ORDER BY date_commande
```
<!--sortie-->
```text
 id_client date_commande commande_precedente  ecart_jours
         2    2023-01-18                 NaN          NaN
         2    2023-04-11          2023-01-18         83.0
         2    2023-09-27          2023-04-11        169.0
         2    2024-08-05          2023-09-27        313.0
         2    2024-10-05          2024-08-05         61.0
         2    2025-07-05          2024-10-05        273.0
         2    2025-08-01          2025-07-05         27.0
         2    2025-12-09          2025-08-01        130.0
         2    2025-12-16          2025-12-09          7.0
```

Pour le client 2, les écarts successifs sont de 83, 169, 313, 61, 273, 27, 130 et 7 jours : un rythme très irrégulier. La première commande n'a pas de précédente (valeur absente). Remarquez `PARTITION BY id_client` : sans lui, `LAG` comparerait la commande d'un client à celle du **client précédent** dans la table. Étendons maintenant le calcul à **tous** les clients, pour résumer ces écarts :

```sql
WITH ecarts AS (
  SELECT julianday(date_commande) - julianday(LAG(date_commande)
         OVER (PARTITION BY id_client ORDER BY date_commande, id_commande)) AS jours
  FROM commandes)
SELECT COUNT(jours) AS nb_ecarts, ROUND(AVG(jours), 1) AS moyenne, MIN(jours) AS minimum, MAX(jours) AS maximum
FROM ecarts
```
<!--sortie-->
```text
 nb_ecarts  moyenne  minimum  maximum
     31589     86.4      0.0   1014.0
```

On dispose de **31 589 écarts**, d'une moyenne de **86,4 jours** (un client recommande en moyenne tous les trois mois), avec un minimum de 0 (deux commandes le même jour, que nous avons repérées en 3.2.5) et un maximum de plus de mille jours. `COUNT(jours)` ignore les valeurs absentes (la première commande de chaque client), ce qui est exactement ce qu'on veut.

### 3.3.5 Cumuls, moyennes mobiles et cadres

Quand on ajoute un `ORDER BY` à une fonction d'agrégation fenêtre, elle devient **cumulative** : `SUM(ca) OVER (ORDER BY mois)` additionne le mois courant et tous les précédents, c'est-à-dire le **cumul depuis le début**. Pour une **moyenne mobile**, on précise le **cadre** : `AVG(ca) OVER (ORDER BY mois ROWS BETWEEN 2 PRECEDING AND CURRENT ROW)` moyenne la ligne courante et les deux précédentes, donc trois mois glissants. Enfin `SUM(ca) OVER ()`, sans rien dans la parenthèse, est le total général, utile pour calculer des parts.

Voici ces quatre indicateurs pour le second semestre de 2025. Les fenêtres sont calculées sur **toute l'année**, le filtre sur le semestre n'intervient qu'à l'extérieur (le piège de la section 3.3.2) :

```sql
WITH mensuel AS (
  SELECT strftime('%Y-%m', c.date_commande) AS mois, SUM(l.montant) AS ca
  FROM commandes c JOIN lignes_commande l USING (id_commande)
  WHERE c.date_commande >= '2025-01-01' GROUP BY mois),
calc AS (
  SELECT mois, ca, SUM(ca) OVER (ORDER BY mois) AS cumul,
         AVG(ca) OVER (ORDER BY mois ROWS BETWEEN 2 PRECEDING AND CURRENT ROW) AS moy3,
         100.0 * ca / SUM(ca) OVER () AS part
  FROM mensuel)
SELECT mois, ROUND(ca) AS ca, ROUND(cumul) AS cumul,
       ROUND(moy3) AS moyenne_mobile_3_mois, ROUND(part, 1) AS part_annee_pct
FROM calc WHERE mois >= '2025-07'
```
<!--sortie-->
```text
   mois       ca     cumul  moyenne_mobile_3_mois  part_annee_pct
2025-07 111221.0  673612.0               107808.0             8.4
2025-08  89898.0  763511.0               102683.0             6.8
2025-09 113453.0  876963.0               104857.0             8.6
2025-10 120064.0  997027.0               107805.0             9.1
2025-11 143892.0 1140919.0               125803.0            10.9
2025-12 183845.0 1324764.0               149267.0            13.9
```

Le cumul de décembre (**1 324 764 €**) est le chiffre d'affaires de l'année 2025 : on retrouve exactement le total de la section 3.2.2. La moyenne mobile lisse les accidents : en août, le chiffre d'affaires chute à 89 898 €, mais la moyenne des trois derniers mois ne baisse que de 107 808 € à 102 683 €. Enfin, décembre représente à lui seul **13,9 %** de l'année. La figure présente ces résultats sur l'année entière.


![Chiffre d'affaires mensuel de 2025 avec sa moyenne mobile sur trois mois (à gauche) et cumul depuis janvier (à droite) : la moyenne mobile atténue le creux d'août ; le cumul finit à 1,32 million d'euros.](figures/ch03-fenetres.png)

> ⚠️ **Piège : les premières lignes d'une moyenne mobile.** Pour janvier, il n'y a pas deux mois précédents : la moyenne mobile sur trois mois s'appuie sur **une** seule valeur (puis deux en février). Les premiers points ne sont pas comparables aux suivants ; en pratique, on supprime ou l'on signale les mois incomplets.

> 🧪 **Remarque : `ROWS` ou `RANGE` ?** Le cadre `ROWS` compte des **lignes** ; le cadre `RANGE` raisonne sur des **valeurs** (toutes les lignes dont la valeur de tri est égale à celle de la ligne courante forment un seul « pair »). Quand `ORDER BY` est présent et qu'aucun cadre n'est précisé, le cadre par défaut est `RANGE BETWEEN UNBOUNDED PRECEDING AND CURRENT ROW` : les ex æquo sont cumulés **ensemble**, ce qui surprend. Pour un cumul, précisez `ROWS` dès que votre ordre peut contenir des ex æquo.

### 3.3.6 Découper en tranches et mesurer la concentration : NTILE

`NTILE(n)` répartit les lignes ordonnées en **n tranches de taille presque égale** : `NTILE(10)` donne les déciles, `NTILE(4)` les quartiles. Combiné à un `GROUP BY`, il mesure la **concentration** du chiffre d'affaires, un classique de l'analyse client : *quelle part du chiffre d'affaires les meilleurs clients représentent-ils ?* Nous y répondons ici par déciles de clients (du plus dépensier au moins dépensier) :

```sql
WITH ca_client AS (
  SELECT c.id_client, SUM(l.montant) AS ca
  FROM commandes c JOIN lignes_commande l USING (id_commande)
  WHERE c.date_commande >= '2025-01-01' GROUP BY c.id_client),
deciles AS (SELECT id_client, ca, NTILE(10) OVER (ORDER BY ca DESC) AS decile FROM ca_client)
SELECT decile, COUNT(*) AS nb_clients, ROUND(SUM(ca)) AS ca,
       ROUND(100.0 * SUM(ca) / SUM(SUM(ca)) OVER (), 1) AS part_ca
FROM deciles GROUP BY decile ORDER BY decile
```
<!--sortie-->
```text
 decile  nb_clients       ca  part_ca
      1         388 435870.0     32.9
      2         388 251185.0     19.0
      3         388 181434.0     13.7
      4         388 134516.0     10.2
      5         388 103459.0      7.8
      6         387  79489.0      6.0
      7         387  60268.0      4.5
      8         387  42040.0      3.2
      9         387  26058.0      2.0
     10         387  10446.0      0.8
```

Les 3 875 clients actifs en 2025 sont répartis en dix tranches de 387 ou 388 clients (3 875 n'est pas divisible par dix : les premières tranches reçoivent un client de plus). Les 10 % de clients qui dépensent le plus réalisent **32,9 %** du chiffre d'affaires, les 20 % premiers **51,9 %** (32,9 + 19,0) ; la moitié la moins dépensière (les déciles 6 à 10) n'en apporte que **16,5 %**. La clientèle est donc **concentrée mais pas dramatiquement** : on est loin de la règle des « 80/20 » que l'on cite souvent. Remarquez l'expression `SUM(SUM(ca)) OVER ()` : le `SUM(ca)` interne est l'agrégat du groupe, le `SUM(…) OVER ()` externe additionne ces agrégats pour obtenir le total.


![Part du chiffre d'affaires 2025 réalisée par chaque décile de clients : les 10 % de clients qui dépensent le plus réalisent un tiers du chiffre d'affaires, la moitié la moins dépensière moins d'un cinquième.](figures/ch03-deciles.png)

### 3.3.7 Les clients qui ne reviennent plus

Un dernier exemple rassemble plusieurs idées. La gérante veut la liste des clients **dont la dernière commande date d'avant 2025** (donc inactifs depuis plus d'un an à la fin de 2025). La **dernière** commande de chaque client est celle de rang 1 quand on classe ses commandes de la plus récente à la plus ancienne :

```sql
WITH derniere AS (
  SELECT id_client, date_commande,
         ROW_NUMBER() OVER (PARTITION BY id_client ORDER BY date_commande DESC, id_commande DESC) AS rn
  FROM commandes)
SELECT COUNT(*) AS clients_inactifs_depuis_2025
FROM derniere
WHERE rn = 1 AND date_commande < '2025-01-01'
```
<!--sortie-->
```text
 clients_inactifs_depuis_2025
                          931
```

**931 clients** n'ont plus commandé depuis la fin de 2024. Ce chiffre n'est pas nouveau : en 3.2.7, la requête `EXCEPT` des « clients perdus » (clients d'avant 2025 absents en 2025) renvoyait **931** aussi. **Deux méthodes très différentes, le même résultat** : une jointure ensembliste d'un côté, une fonction fenêtre de l'autre. C'est le meilleur des contrôles : quand deux écritures indépendantes s'accordent, la probabilité que les deux soient fausses de la même façon est faible. Prenez l'habitude de le faire pour les chiffres que vous livrez.

> ✅ **À retenir.**
> - Une fonction fenêtre calcule un résultat **sur un groupe de lignes** mais **conserve chaque ligne** ; `PARTITION BY` définit les groupes, `ORDER BY` l'ordre, le **cadre** les lignes voisines retenues.
> - Elles sont calculées **après** `WHERE`, `GROUP BY` et `HAVING` : pour filtrer sur leur résultat, ou pour qu'un `WHERE` ne prive pas la fenêtre de ses voisines, on passe par deux niveaux (`WITH` ou sous-requête).
> - `ROW_NUMBER` numérote sans ex æquo, `RANK` laisse des trous, `DENSE_RANK` n'en laisse pas ; `LAG` et `LEAD` comparent à la ligne précédente ou suivante ; `SUM … OVER (ORDER BY …)` cumule ; `NTILE` découpe en tranches.
> - Contrôlez toujours un résultat de fenêtre par un total connu ou par une seconde méthode.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.6 (évolution mensuelle, cumul et comparaison à l'an dernier), application 3.8 (une segmentation RFM en SQL), exercices 3.9 à 3.11.


## 3.4 CTE et structuration de requêtes complexes

Une requête d'analyse réelle ne tient presque jamais en un seul `SELECT` : il faut d'abord calculer le chiffre d'affaires de chaque client, puis classer les clients, puis rapporter les dix premiers au total. On peut empiler ces étapes en sous-requêtes imbriquées, mais le résultat se lit comme une poupée russe, de l'intérieur vers l'extérieur. Les **expressions de table commune** (*Common Table Expressions*, **CTE**) offrent une alternative bien plus lisible : on **nomme** chaque étape, et on les enchaîne de haut en bas comme une recette. Cette section est aussi celle où nous répondons enfin à la question de la gérante.

### 3.4.1 Nommer ses étapes avec WITH

Une CTE se déclare avec `WITH nom AS (requête)`, **avant** la requête principale. Elle se comporte ensuite comme une table temporaire que l'on peut interroger autant de fois qu'on veut, **le temps de la requête seulement** (rien n'est stocké). On peut en déclarer plusieurs, séparées par des virgules ; chacune peut utiliser celles qui la précèdent.


![La requête qui répond à la gérante, vue comme une chaîne d'étapes : les tables sources, le chiffre d'affaires de chaque client en 2025, les dix premiers, puis le calcul final de leur part dans le total.](figures/ch03-cte.png)

Voici la requête qui répond à la question posée en introduction : *quels sont nos dix meilleurs clients de 2025, et que représentent-ils dans le chiffre d'affaires ?* Elle suit exactement la figure : une CTE `ca_client` (une ligne par client, avec son chiffre d'affaires de 2025), une CTE `top10` (les dix premiers), puis le calcul final.

```sql
WITH ca_client AS (
  SELECT c.id_client, SUM(l.montant) AS ca
  FROM commandes c JOIN lignes_commande l USING (id_commande)
  WHERE c.date_commande >= '2025-01-01'
  GROUP BY c.id_client),
top10 AS (SELECT id_client, ca FROM ca_client ORDER BY ca DESC LIMIT 10)
SELECT (SELECT COUNT(*) FROM ca_client) AS nb_clients,
       ROUND((SELECT SUM(ca) FROM top10), 0) AS ca_top10,
       ROUND((SELECT SUM(ca) FROM ca_client), 0) AS ca_total,
       ROUND(100.0 * (SELECT SUM(ca) FROM top10) / (SELECT SUM(ca) FROM ca_client), 2) AS part_pct
```
<!--sortie-->
```text
 nb_clients  ca_top10  ca_total  part_pct
       3875   24886.0 1324764.0      1.88
```

**La réponse :** parmi **3 875 clients actifs** en 2025, les dix meilleurs ont dépensé **24 886 €** sur un chiffre d'affaires total de **1 324 764 €**, soit **1,88 %**. Les dix premiers clients de la boutique ne pèsent donc même pas 2 % de l'activité. C'est une information utile pour la gérante : la boutique **ne dépend pas de quelques gros clients** (une perte de dix clients serait indolore), mais d'une large clientèle. Ce résultat est cohérent avec ce que nous avons vu en 3.3.6 : dix clients, c'est 0,26 % de la clientèle, loin du premier décile qui, lui, pèse 32,9 %. Regardons maintenant les dix clients eux-mêmes, en réutilisant la même CTE :

```sql
WITH ca_client AS (
  SELECT c.id_client, SUM(l.montant) AS ca
  FROM commandes c JOIN lignes_commande l USING (id_commande)
  WHERE c.date_commande >= '2025-01-01'
  GROUP BY c.id_client)
SELECT id_client, ROUND(ca, 2) AS ca_2025,
       ROUND(100.0 * ca / (SELECT SUM(ca) FROM ca_client), 2) AS part_pct
FROM ca_client
ORDER BY ca DESC
LIMIT 10
```
<!--sortie-->
```text
 id_client  ca_2025  part_pct
      1360  3382.33      0.26
      2987  2898.79      0.22
      1395  2675.71      0.20
      3126  2531.71      0.19
      3802  2402.11      0.18
      3737  2332.84      0.18
        68  2230.69      0.17
      4409  2226.18      0.17
      2953  2140.43      0.16
      5095  2065.63      0.16
```

Le meilleur client (le numéro 1360) a dépensé 3 382 € en 2025, soit 0,26 % du chiffre d'affaires ; le dixième, 2 066 €. L'écart entre le premier et le dixième est modeste : il n'y a **pas de « super-client »** dans cette clientèle. On notera une propriété de la CTE : dans la première requête, `ca_client` est utilisée **quatre fois** (dans `top10`, puis dans trois sous-requêtes du `SELECT` final), alors qu'on ne l'a écrite qu'une fois. Avec des sous-requêtes imbriquées, il aurait fallu copier quatre fois le même texte.

> 💡 **Intuition.** Une CTE n'est ni plus rapide ni plus lente qu'une sous-requête : c'est **la même requête, mieux écrite**. Son seul rôle est de rendre la lecture linéaire, étape après étape, et de **donner un nom à chaque idée** (`ca_client`, `top10`). Une requête que l'on comprend est une requête que l'on peut vérifier.

### 3.4.2 Vérifier par un autre outil

Un chiffre n'est vraiment acquis que lorsqu'**un second outil, indépendant, le confirme**. Recalculons la réponse avec pandas, la bibliothèque d'analyse de Python (que vous découvrirez au chapitre 4) : on charge les deux tables brutes, on les joint, on additionne par client, et l'on compare.

```python
cmd = pd.read_sql_query("SELECT id_commande, id_client FROM commandes WHERE date_commande >= '2025-01-01'", con)
lig = pd.read_sql_query("SELECT id_commande, montant FROM lignes_commande", con)
ca = cmd.merge(lig, on="id_commande").groupby("id_client")["montant"].sum().sort_values(ascending=False)
print(len(ca), round(ca.head(10).sum()), round(ca.sum()), round(100 * ca.head(10).sum() / ca.sum(), 2))
```
<!--sortie-->
```text
3875 24886 1324764 1.88
```

pandas renvoie **3 875 clients, 24 886 €, 1 324 764 € et 1,88 %** : exactement les mêmes chiffres. Le résultat vient donc de deux implémentations indépendantes (un moteur SQL, une bibliothèque Python), et la jointure n'a ni perdu ni dupliqué de lignes. Dans le chapitre 2, vous retrouverez le même chiffre d'affaires par un tableau croisé dynamique ; l'idée est la même : **un chiffre important se calcule au moins deux fois, par deux chemins**.

### 3.4.3 Enchaîner plusieurs étapes : le taux de retour

Prenons une question plus riche : *les retours coûtent-ils cher, et d'où viennent-ils ?* Le taux de retour (le nombre de lignes retournées rapporté au nombre de lignes vendues) et le montant remboursé se calculent par canal. Il faut trois étapes : isoler les lignes vendues en 2025, résumer les retours **par ligne**, puis recoller les deux avec une jointure à gauche (une ligne vendue n'a pas forcément de retour).

```sql
WITH lignes25 AS (
  SELECT l.id_ligne, c.canal, l.montant
  FROM lignes_commande l JOIN commandes c USING (id_commande)
  WHERE c.date_commande >= '2025-01-01'),
retournees AS (
  SELECT id_ligne, SUM(montant_rembourse) AS rembourse FROM retours GROUP BY id_ligne)
SELECT l.canal, COUNT(*) AS nb_lignes, COUNT(r.id_ligne) AS nb_retours,
       ROUND(100.0 * COUNT(r.id_ligne) / COUNT(*), 1) AS taux_retour_pct,
       ROUND(COALESCE(SUM(r.rembourse), 0), 0) AS rembourse
FROM lignes25 l LEFT JOIN retournees r ON r.id_ligne = l.id_ligne
GROUP BY l.canal
ORDER BY taux_retour_pct DESC
```
<!--sortie-->
```text
   canal  nb_lignes  nb_retours  taux_retour_pct  rembourse
    Site      13928        1229              8.8    56583.0
 Réseaux       3288         228              6.9     9429.0
Boutique      12611         419              3.3    18456.0
```

Les retours se concentrent sur le **site** : 8,8 % des lignes y sont retournées, contre 6,9 % pour les réseaux et seulement **3,3 % en boutique**, et le site rembourse près de **56 600 €** contre 18 500 € en boutique. Plusieurs choix de construction méritent d'être soulignés, car ils illustrent des idées du chapitre :

- La CTE `retournees` **agrège avant de joindre** : on ramène la table des retours au grain « une ligne par ligne vendue » (`GROUP BY id_ligne`). Si une ligne avait fait l'objet de deux retours, la jointure aurait sinon dupliqué la ligne vendue, et les montants avec elle (le piège de la section 3.2.6).
- La jointure est une jointure **à gauche** : sans elle, les lignes sans retour disparaîtraient et le taux serait de 100 %.
- `COUNT(r.id_ligne)` compte les retours **réels** (les absences ne comptent pas), alors que `COUNT(*)` compte toutes les lignes vendues : le rapport des deux est le taux de retour.
- `COALESCE(SUM(r.rembourse), 0)` remplace par zéro la somme d'un groupe sans aucun retour.

Ce tableau déclenche une vraie discussion de gestion : le site vend plus, mais **il rend près de trois fois plus que la boutique**. Faut-il revoir les fiches produits, les tailles, les délais de livraison ? Les motifs de retour (table `retours`) permettront d'aller plus loin ; c'est l'objet d'une application du cahier.

### 3.4.4 Une méthode pour construire une requête complexe

Devant une question compliquée, la tentation est d'écrire d'un coup une requête de cinquante lignes, puis de chercher pourquoi elle ne marche pas. Une méthode simple évite la plupart des erreurs. Elle tient en six étapes, que l'on applique **dans l'ordre**.

1. **Reformuler la question** en une phrase précise, avec la période et la mesure (« chiffre d'affaires TTC, remises déduites, 2025 »).
2. **Fixer le grain du résultat** : que représentera une ligne du tableau final ? Un client ? Un mois ? Un couple canal × catégorie ? C'est la décision la plus importante : elle détermine le `GROUP BY`.
3. **Repérer les tables sources** et la colonne qui porte la mesure (le montant est dans `lignes_commande`, la date dans `commandes`, la catégorie dans `produits`).
4. **Écrire les jointures une par une**, en vérifiant à chaque fois le nombre de lignes (le test des trois comptes de la section 3.2.6).
5. **Ajouter les filtres, puis les agrégats**, en les nommant dans des CTE s'ils sont nombreux.
6. **Vérifier** : un total connu, un ordre de grandeur, un second outil. Si le résultat est trop beau ou trop laid, doutez-en d'abord.

Appliquons-la à une question dont la réponse pourrait paraître évidente : *quel est le panier moyen, canal par canal, et que vaut la moyenne de ces trois paniers moyens ?* On l'a vu en 3.1.9 sur un exemple inventé : la moyenne des moyennes diffère de la vraie moyenne quand les groupes n'ont pas la même taille. Voyons ce que donne la réalité :

```sql
WITH par_commande AS (
  SELECT c.id_commande, c.canal, SUM(l.montant) AS panier
  FROM commandes c JOIN lignes_commande l USING (id_commande)
  GROUP BY c.id_commande, c.canal),
par_canal AS (
  SELECT canal, COUNT(*) AS n, AVG(panier) AS panier_moyen FROM par_commande GROUP BY canal)
SELECT ROUND((SELECT AVG(panier) FROM par_commande), 2) AS panier_global,
       ROUND(AVG(panier_moyen), 2) AS moyenne_des_moyennes
FROM par_canal
```
<!--sortie-->
```text
 panier_global  moyenne_des_moyennes
        100.38                100.39
```

Le **panier moyen global** vaut 100,38 € ; la **moyenne des trois paniers moyens de canal** vaut 100,39 €. L'écart est minuscule parce que les trois canaux ont des paniers presque identiques (autour de 100 €) ; il serait considérable si un petit groupe avait un panier très différent. La règle ne change pas pour autant : **on agrège toujours à partir du détail**, jamais à partir de résumés. Remarquez aussi le grain de `par_commande` : **une ligne par commande**, ce qui fait que le panier moyen est bien une moyenne **par commande** et non par ligne (la confusion de 3.1.6).

### 3.4.5 CTE récursives : fabriquer un calendrier

Une CTE peut s'**appeler elle-même** : on la déclare avec `WITH RECURSIVE`, on donne une ligne de départ, puis une règle qui produit la ligne suivante à partir de la précédente, jusqu'à une condition d'arrêt. L'usage le plus courant pour un analyste est de **fabriquer un calendrier**, c'est-à-dire une liste de tous les jours d'une période, y compris ceux où rien ne s'est passé :

```sql
WITH RECURSIVE jours(j) AS (
  SELECT '2025-01-01'
  UNION ALL
  SELECT date(j, '+1 day') FROM jours WHERE j < '2025-01-10'),
reseaux AS (
  SELECT date_commande AS j, COUNT(*) AS nb FROM commandes WHERE canal = 'Réseaux' GROUP BY date_commande)
SELECT jours.j, COALESCE(reseaux.nb, 0) AS commandes_reseaux
FROM jours LEFT JOIN reseaux ON reseaux.j = jours.j
```
<!--sortie-->
```text
         j  commandes_reseaux
2025-01-01                  3
2025-01-02                  1
2025-01-03                  3
2025-01-04                  8
2025-01-05                  3
2025-01-06                  3
2025-01-07                  1
2025-01-08                  3
2025-01-09                  4
2025-01-10                  5
```

La première ligne de `jours` est le 1er janvier ; à chaque tour, la partie récursive ajoute le jour suivant, tant que la date reste inférieure au 10 janvier. En joignant ce calendrier **à gauche** avec les commandes des réseaux sociaux, on obtient une ligne par jour, y compris les jours sans commande (0). Étendu à l'année entière, le même calendrier révèle :

```sql
WITH RECURSIVE jours(j) AS (
  SELECT '2025-01-01' UNION ALL SELECT date(j, '+1 day') FROM jours WHERE j < '2025-12-31'),
reseaux AS (SELECT date_commande AS j, COUNT(*) AS nb FROM commandes WHERE canal = 'Réseaux' GROUP BY date_commande)
SELECT COUNT(*) AS jours_total, SUM(reseaux.nb IS NULL) AS jours_sans_commande
FROM jours LEFT JOIN reseaux ON reseaux.j = jours.j
```
<!--sortie-->
```text
 jours_total  jours_sans_commande
         365                   13
```

**13 jours sur 365** n'ont enregistré aucune commande par les réseaux sociaux en 2025. Sans calendrier, ces jours n'existeraient tout simplement pas dans le résultat d'un `GROUP BY` : une moyenne par jour calculée sur les seuls jours « présents » serait **trop haute**. C'est l'une des erreurs les plus fréquentes dans les analyses de séries temporelles : les zéros qui manquent.

Les CTE récursives servent aussi à parcourir des **hiérarchies** (un organigramme où chaque ligne désigne son chef, des catégories à plusieurs niveaux). La ligne de départ est la **racine** (la personne sans chef) ; à chaque tour, la partie récursive ajoute les personnes dont le chef vient d'être trouvé, en incrémentant un compteur de niveau. Le cahier propose de l'écrire sur une équipe de six personnes (exercice 3.12). Une récursion s'arrête quand la partie récursive ne produit plus de ligne nouvelle ; **si l'on oublie la condition d'arrêt, la requête tourne indéfiniment**, ce qui fait de la CTE récursive l'un des rares endroits où le SQL peut « geler » votre session.

### 3.4.6 Écrire des requêtes que l'on relit

Une requête est lue bien plus souvent qu'elle n'est écrite : par vous dans six mois, par un collègue, par la personne qui reprendra l'analyse. Quelques habitudes les rendent relisibles :

- **Une clause par ligne**, mots-clés en majuscules, indentation qui montre la structure ; des alias **parlants** (`ca_client`, pas `t1`).
- **Des commentaires** qui disent **pourquoi** (`-- on exclut les retours internes`), pas ce que fait le code. En SQL, un commentaire de ligne commence par `--`.
- **Tester chaque CTE séparément** : sélectionnez-la seule, vérifiez son nombre de lignes et un total, puis passez à la suivante.
- **Nommer les colonnes** du résultat (`AS ca_2025`) et arrondir **à la fin**, pas dans les étapes intermédiaires.
- **Garder les requêtes sous contrôle de version** (Git) à côté des résultats : c'est ce qui rend l'analyse reproductible.
- **Éviter `SELECT *`** et les nombres « magiques » (un taux de TVA, une date) répétés dans la requête : mettez-les dans une CTE `parametres` ou dans un commentaire.

> ⚠️ **Piège : une CTE n'est pas un cache.** Selon la base, une CTE référencée plusieurs fois peut être **recalculée** à chaque référence (c'est le cas de `ca_client` dans la première requête de cette section). Si une étape est coûteuse et utilisée plusieurs fois, on peut la matérialiser dans une table temporaire. Pour l'analyste, la règle pratique est de **mesurer** avant de s'inquiéter : sur les volumes de la boutique, rien de tout cela ne se voit ; sur des centaines de millions de lignes, cela se voit tout de suite (la section 3.5 donne les outils).

> ✅ **À retenir.**
> - Une **CTE** (`WITH nom AS (…)`) donne un nom à une étape ; on enchaîne les étapes de haut en bas, chacune pouvant utiliser les précédentes.
> - Pour une requête complexe : **question → grain du résultat → tables sources → jointures une à une → filtres et agrégats → vérification**.
> - **Un chiffre important se vérifie par un second outil** : ici, SQL et pandas donnent 24 886 € pour les dix meilleurs clients, soit 1,88 % de 1 324 764 €.
> - Une **CTE récursive** fabrique un calendrier (pour ne pas oublier les jours vides) ou parcourt une hiérarchie.
> - Agrégez toujours **depuis le détail** ; commentez, nommez, testez étape par étape.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.5 (les retours), application 3.7 (fidélité et cohortes), exercice 3.12 (un organigramme par une CTE récursive).


## 3.5 ➕ Pour aller plus loin : SQL avancé

> 🧭 **Section complémentaire.** Elle prolonge le parcours essentiel par les notions que l'on rencontre dès que l'on travaille sur une vraie base d'entreprise : les sous-requêtes, les index et l'optimisation, les vues, les transactions, les déclencheurs et la sécurité. Rien ici n'est nécessaire pour la suite du volume.

### 3.5.1 Sous-requêtes : une requête dans une requête

Une **sous-requête** est un `SELECT` placé entre parenthèses à l'intérieur d'un autre. On en a déjà croisé (le dénominateur d'un pourcentage en 3.1.7). Il en existe trois usages principaux, selon ce que renvoie la sous-requête.

**Une valeur unique** (sous-requête *scalaire*), utilisée comme une constante dans une comparaison ou un calcul. Quels produits sont plus chers que le prix moyen du catalogue ?

```sql
SELECT COUNT(*) AS nb_produits_au_dessus_de_la_moyenne,
       (SELECT ROUND(AVG(prix_vente), 2) FROM produits) AS prix_moyen
FROM produits
WHERE prix_vente > (SELECT AVG(prix_vente) FROM produits)
```
<!--sortie-->
```text
 nb_produits_au_dessus_de_la_moyenne  prix_moyen
                                  47       35.88
```

La sous-requête `(SELECT AVG(prix_vente) FROM produits)` est évaluée une fois et remplacée par son résultat : **47 produits sur 120** dépassent le prix moyen de 35,88 €. On ne pourrait pas écrire `WHERE prix_vente > AVG(prix_vente)` : un agrégat n'est pas autorisé dans le `WHERE` (l'ordre d'exécution de la section 3.1.7).

**Une liste de valeurs** (sous-requête de liste), avec `IN`. Combien de produits ont donné lieu à au moins un retour de plus de 100 € ?

```sql
SELECT COUNT(*) AS produits_concernes
FROM produits
WHERE id_produit IN (SELECT l.id_produit
                     FROM lignes_commande l JOIN retours r USING (id_ligne)
                     WHERE r.montant_rembourse > 100)
```
<!--sortie-->
```text
 produits_concernes
                 55
```

La sous-requête renvoie la liste des identifiants de produits concernés, et la requête extérieure ne garde que ces produits : **55 produits** (près de la moitié du catalogue) ont déjà fait l'objet d'un remboursement de plus de 100 €, ce qui invite à regarder de près les articles chers.

**Une sous-requête corrélée** est une sous-requête qui **dépend de la ligne courante** de la requête extérieure : elle est « réévaluée » pour chaque ligne. Elle sert aux comparaisons avec le groupe de la ligne. Quel est, dans chaque catégorie, le produit le plus cher ?

```sql
SELECT p.categorie, p.nom_produit, p.prix_vente
FROM produits p
WHERE p.prix_vente = (SELECT MAX(q.prix_vente) FROM produits q WHERE q.categorie = p.categorie)
ORDER BY p.categorie
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
```

Pour chaque produit `p`, la sous-requête cherche le prix maximal des produits `q` **de la même catégorie** (`q.categorie = p.categorie`), et la condition ne garde que les produits qui atteignent ce maximum. Le résultat compte six lignes, une par catégorie, du transat à 152,90 € pour le jardin à la trousse à 21,90 € pour la papeterie. Cette écriture est correcte, mais un **classement avec fonction fenêtre** (section 3.3.3) fait la même chose plus lisiblement et, sur de gros volumes, bien plus vite : les sous-requêtes corrélées sont des **candidates à la réécriture**.

Enfin, `EXISTS (sous-requête)` ne demande pas **quoi**, seulement **s'il existe** au moins une ligne. C'est la forme préférée pour les tests de présence : elle s'arrête à la première correspondance trouvée. Combien de clients ont déjà fait au moins un retour ?

```sql
SELECT COUNT(*) AS clients_avec_retour
FROM clients cl
WHERE EXISTS (SELECT 1
              FROM commandes c
              JOIN lignes_commande l USING (id_commande)
              JOIN retours r USING (id_ligne)
              WHERE c.id_client = cl.id_client)
```
<!--sortie-->
```text
 clients_avec_retour
                2443
```

**2 443 clients** (sur 6 000) ont déjà renvoyé un article : un client sur quatre environ, une proportion qui pèsera sur la politique de reprise. Le `SELECT 1` de la sous-requête n'a pas d'importance : seule compte l'existence d'une ligne. `NOT EXISTS` en est le contraire, et c'est une anti-jointure (section 3.2.3).

> ⚠️ **Piège : `NOT IN` et les valeurs absentes.** `x NOT IN (liste)` renvoie un résultat **inconnu** dès que la liste contient une valeur absente (`NULL`), et donc **aucune ligne**. La même requête écrite avec `NOT EXISTS` ne souffre pas de ce défaut. Dans le doute, préférez `NOT EXISTS`.

### 3.5.2 Index et plans d'exécution

Quand on demande à la base les commandes d'un client, elle peut lire la table **ligne par ligne** jusqu'à la fin (un **balayage complet**, *full scan*), ou consulter un **index**, comme le fait un lecteur qui cherche un mot dans l'index d'un livre au lieu de relire tout l'ouvrage. Un index est une structure triée, maintenue par la base, qui permet de **retrouver des lignes sans tout lire**. En contrepartie, il occupe de la place et ralentit un peu les écritures, puisqu'il faut le mettre à jour.

La base propose d'**expliquer** le plan qu'elle a choisi : `EXPLAIN QUERY PLAN` en SQLite, `EXPLAIN` ailleurs. Le mot `SCAN` signale une lecture complète, `SEARCH` une recherche par index. Écrivons une petite fonction qui renvoie le plan d'une requête, et interrogeons trois requêtes :

```python
def plan(requete):
    return [ligne[3] for ligne in con.execute("EXPLAIN QUERY PLAN " + requete)]

print(plan("SELECT COUNT(*) FROM commandes WHERE canal = 'Site'"))
print(plan("SELECT COUNT(*) FROM commandes WHERE id_client = 2"))
print(plan("SELECT COUNT(*) FROM commandes WHERE strftime('%Y', date_commande) = '2025'"))
print(plan("SELECT COUNT(*) FROM commandes WHERE date_commande >= '2025-01-01' AND date_commande < '2026-01-01'"))
```
<!--sortie-->
```text
['SCAN commandes']
['SEARCH commandes USING COVERING INDEX idx_cmd_client (id_client=?)']
['SCAN commandes USING COVERING INDEX idx_cmd_date']
['SEARCH commandes USING COVERING INDEX idx_cmd_date (date_commande>? AND date_commande<?)']
```

Les quatre plans sont instructifs. Aucun index n'existe sur `canal` : la première requête fait un **balayage complet** de `commandes`. La deuxième utilise l'index de `id_client` (`SEARCH … USING INDEX`). La troisième et la quatrième portent sur la date, qui est indexée, **mais pas de la même façon** : quand on applique une **fonction** à la colonne (`strftime('%Y', date_commande)`), la base ne peut plus se servir de l'ordre de l'index et doit le **parcourir en entier** (`SCAN`) ; quand on exprime la même condition par un **intervalle** (`>= … AND < …`), elle fait une **recherche** directe (`SEARCH`). Les deux écritures donnent le même résultat, mais **pas le même effort**. Créons maintenant un index sur `canal` pour voir le plan changer :

```python
con.execute("CREATE INDEX idx_cmd_canal ON commandes(canal)")
print(plan("SELECT COUNT(*) FROM commandes WHERE canal = 'Site'"))
```
<!--sortie-->
```text
['SEARCH commandes USING COVERING INDEX idx_cmd_canal (canal=?)']
```

Le plan passe de `SCAN` à `SEARCH … USING COVERING INDEX idx_cmd_canal (canal=?)`. Un index n'est pourtant **pas toujours utile** : ici, la colonne ne contient que trois valeurs, et un index ne rend de grands services que si la condition **isole peu de lignes** (on dit qu'elle est *sélective*). Chercher les commandes d'un seul client sur 6 000 (sélectif) en profite largement ; chercher « toutes celles du site » (42 % de la table) beaucoup moins.

### 3.5.3 Quelques règles d'optimisation

Sur les volumes de la boutique, toutes les requêtes de ce chapitre répondent instantanément. Sur des millions de lignes, quelques règles font la différence :

- **Filtrer tôt** : placer les conditions `WHERE` le plus près possible des tables, pour réduire le nombre de lignes avant les jointures et les agrégats.
- **Ne sélectionner que les colonnes utiles** : éviter `SELECT *`, qui transporte des colonnes inutiles et empêche certains accès rapides par index.
- **Ne pas appliquer de fonction à une colonne indexée** dans un `WHERE` (le plan de 3.5.2) : exprimer la condition sur la colonne brute.
- **Agréger avant de joindre** quand on le peut : c'est plus rapide **et** cela évite la multiplication des lignes (section 3.2.6).
- **Éviter `LIKE '%mot'`** (joker en tête) : aucun index ne sait chercher « se termine par ». `LIKE 'mot%'` est, lui, efficace.
- **Lire le plan** avant d'accuser la base : un `SCAN` sur une grosse table dans une requête lente indique souvent l'index manquant.

> 🧭 **En pratique.** Un analyste ne crée pas, en général, les index d'une base de production : c'est le rôle de l'équipe qui la gère. Savoir **lire un plan** vous permet en revanche de lui faire une demande précise (« la requête X lit toute la table `commandes` ; un index sur `canal, date_commande` l'accélérerait »), ce que les administrateurs de bases apprécient.

### 3.5.4 Vues : donner un nom à une requête

Une **vue** est une requête enregistrée sous un nom : elle se comporte comme une table, mais ne contient aucune donnée propre, elle est recalculée à chaque utilisation. Les vues servent à **partager** une logique (« le chiffre d'affaires, c'est ceci ») pour que tous les rapports calculent la même chose, et à **simplifier** les requêtes. Créons une vue qui recolle les lignes, leurs commandes et leurs produits, c'est-à-dire la jointure que nous avons écrite en 3.2.2 :

```sql
CREATE VIEW v_ventes AS
SELECT l.id_ligne, c.id_commande, c.date_commande, c.canal, c.id_client,
       p.categorie, p.nom_produit, l.quantite, l.montant
FROM lignes_commande l
JOIN commandes c ON c.id_commande = l.id_commande
JOIN produits p ON p.id_produit = l.id_produit
```

Elle s'interroge ensuite comme n'importe quelle table, sans réécrire les jointures :

```sql
SELECT canal, ROUND(SUM(montant), 0) AS ca_2025, COUNT(DISTINCT id_client) AS clients
FROM v_ventes
WHERE date_commande >= '2025-01-01'
GROUP BY canal
ORDER BY ca_2025 DESC
```
<!--sortie-->
```text
   canal  ca_2025  clients
    Site 617715.0     2844
Boutique 560974.0     2731
 Réseaux 146074.0     1139
```

Le **site** réalise 617 715 € de chiffre d'affaires en 2025, devant la **boutique** (560 974 €) et les **réseaux** (146 074 €) ; les trois montants totalisent 1 324 763 €, soit les 1 324 764 € de la section 3.3 à l'arrondi près. Les nombres de clients (2 844, 2 731 et 1 139) **ne s'additionnent pas** : un même client peut acheter par plusieurs canaux, et `COUNT(DISTINCT id_client)` ne compte chacun qu'une fois **par canal**. L'intérêt de la vue est **organisationnel** : si l'on décide demain d'exclure les commandes de test, on corrige **la vue**, et tous les rapports sont corrigés d'un coup. Dans certaines bases (PostgreSQL, Oracle), une **vue matérialisée** stocke le résultat et le rafraîchit à la demande : on gagne en vitesse, on perd en fraîcheur.

> ⚠️ **Piège : une vue fige un grain.** `v_ventes` a le grain « une ligne de commande » : calculer un nombre de commandes dessus exige `COUNT(DISTINCT id_commande)`, comme dans l'exemple (`COUNT(DISTINCT id_client)` pour les clients). Documentez le grain de chaque vue en commentaire.

### 3.5.5 Transactions : tout ou rien

Une **transaction** regroupe plusieurs opérations en un bloc indivisible : soit **toutes** réussissent (`COMMIT`), soit **aucune** n'est appliquée (`ROLLBACK`). C'est la garantie qui évite, par exemple, de débiter un stock sans enregistrer la commande correspondante si la machine s'arrête entre les deux. On résume les propriétés d'une transaction par le sigle **ACID** : atomicité (tout ou rien), cohérence (les règles de la base sont respectées), isolation (deux transactions simultanées ne se voient pas à moitié faites), durabilité (ce qui est validé survit à une panne). Une démonstration sur une petite table de stock :

```python
con.execute("CREATE TABLE demo_stock (id_produit INTEGER PRIMARY KEY, quantite INTEGER)")
con.execute("INSERT INTO demo_stock VALUES (1, 10), (2, 5)")
con.commit()
con.execute("UPDATE demo_stock SET quantite = quantite - 3 WHERE id_produit = 1")
print("pendant la transaction :", con.execute("SELECT quantite FROM demo_stock WHERE id_produit = 1").fetchone()[0])
con.rollback()
print("après annulation       :", con.execute("SELECT quantite FROM demo_stock WHERE id_produit = 1").fetchone()[0])
```
<!--sortie-->
```text
pendant la transaction : 7
après annulation       : 10
```

Pendant la transaction, la quantité est de 7 ; après le `ROLLBACK`, elle est revenue à 10 : l'opération n'a jamais eu lieu. Un analyste, qui **lit** surtout, rencontre rarement les transactions, mais il doit savoir qu'elles existent : un chiffre lu **au milieu** d'un chargement de données peut être incohérent si la base n'isole pas bien les lectures, d'où l'intérêt de lire les données **après** la fin des traitements de nuit.

### 3.5.6 Déclencheurs et procédures stockées

Un **déclencheur** (*trigger*) est un morceau de SQL que la base exécute **automatiquement** quand un événement survient (insertion, modification, suppression). Il sert à tenir un **journal d'audit** : qui a changé quel prix, quand. Exemple minimal : à chaque modification d'un prix, une ligne est ajoutée à un journal.

```python
con.executescript("""
CREATE TABLE demo_prix (id_produit INTEGER PRIMARY KEY, prix REAL);
CREATE TABLE demo_journal (id_produit INTEGER, ancien REAL, nouveau REAL);
CREATE TRIGGER trg_prix AFTER UPDATE OF prix ON demo_prix
BEGIN INSERT INTO demo_journal VALUES (OLD.id_produit, OLD.prix, NEW.prix); END;
INSERT INTO demo_prix VALUES (1, 20.0);
UPDATE demo_prix SET prix = 22.0 WHERE id_produit = 1;""")
print(con.execute("SELECT * FROM demo_journal").fetchall())
```
<!--sortie-->
```text
[(1, 20.0, 22.0)]
```

Le journal contient une ligne : le produit 1, l'ancien prix 20, le nouveau 22. `OLD` et `NEW` désignent les valeurs avant et après la modification. Les déclencheurs ont un coût : ils rendent le comportement de la base **moins visible** (une modification déclenche des effets que l'on ne voit pas dans la requête), et il vaut mieux les réserver à l'audit et aux règles d'intégrité.

Une **procédure stockée** est un programme enregistré **dans** la base, appelé par son nom avec des paramètres. SQLite n'en possède pas ; PostgreSQL, SQL Server, MySQL et Oracle, si, chacun avec son propre langage. Voici, à titre d'illustration, la forme d'une fonction PostgreSQL qui renvoie le chiffre d'affaires d'une année :

```sql
-- PostgreSQL — non exécuté (SQLite n'a pas de procédures stockées)
CREATE FUNCTION ca_annee(annee integer) RETURNS numeric AS $$
  SELECT SUM(l.montant)
  FROM lignes_commande l JOIN commandes c USING (id_commande)
  WHERE EXTRACT(YEAR FROM c.date_commande) = annee;
$$ LANGUAGE sql;
-- appel : SELECT ca_annee(2025);
```

Pour un analyste, l'intérêt est de **réutiliser** une logique validée sans la recopier ; l'inconvénient est qu'elle vit dans la base et non dans votre dépôt de code : veillez à ce qu'elle soit **documentée et versionnée**.

### 3.5.7 Sécurité : l'injection SQL

Quand une application ou un script construit une requête **en collant du texte saisi par un utilisateur**, un malin peut y glisser du SQL. C'est l'**injection SQL**, l'une des failles les plus répandues et les plus coûteuses. Supposons qu'un formulaire demande « quel canal ? » et que le script colle la réponse dans la requête :

```python
saisie = "Site' OR '1'='1"
dangereux = f"SELECT COUNT(*) FROM commandes WHERE canal = '{saisie}'"
prudent = "SELECT COUNT(*) FROM commandes WHERE canal = ?"
print("collé dans le texte :", con.execute(dangereux).fetchone()[0])
print("paramètre           :", con.execute(prudent, (saisie,)).fetchone()[0])
```
<!--sortie-->
```text
collé dans le texte : 36395
paramètre           : 0
```

La saisie piégée transforme la condition en `canal = 'Site' OR '1'='1'`, **toujours vraie** : la requête renvoie **toutes** les commandes (36 395), alors que le canal demandé n'existe pas. Avec un **paramètre** (`?`), la base traite la saisie comme une **valeur** et non comme du SQL, et renvoie 0 ligne, ce qui est la bonne réponse. La règle est absolue : **ne jamais assembler une requête par concaténation avec une donnée extérieure** ; utiliser des requêtes paramétrées. Dans le même esprit, on donne à un analyste un compte en **lecture seule** et limité aux tables dont il a besoin (principe du moindre privilège) : une erreur de frappe ne doit pas pouvoir effacer une table.


> ✅ **À retenir.**
> - Une **sous-requête** renvoie une valeur, une liste, ou sert à tester l'existence (`EXISTS`) ; les sous-requêtes corrélées se réécrivent souvent avec une fonction fenêtre. Préférez `NOT EXISTS` à `NOT IN`.
> - Un **index** accélère les recherches **sélectives** ; une fonction appliquée à une colonne indexée l'empêche de servir. `EXPLAIN` montre le plan : `SCAN` (tout lire) ou `SEARCH` (par index).
> - Une **vue** nomme une requête pour que tous calculent la même chose ; une **transaction** est un bloc tout-ou-rien ; un **déclencheur** réagit automatiquement à un événement.
> - **Ne jamais coller** une saisie dans une requête : utilisez des **paramètres**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.9 (index et plan d'exécution), exercice 3.14.


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

```sql
-- SQL Server — non exécuté
SELECT TOP 5 nom_produit, categorie, prix_vente FROM produits ORDER BY prix_vente DESC;

-- Oracle — non exécuté
SELECT nom_produit, categorie, prix_vente FROM produits ORDER BY prix_vente DESC FETCH FIRST 5 ROWS ONLY;

-- MySQL et PostgreSQL : identique à SQLite (LIMIT 5)
```

Le **nombre de commandes par mois** (section 3.1.5), où se voit la différence de traitement des dates :

```sql
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


## Bilan du chapitre 3

Vous savez maintenant :

- **lire une base relationnelle** : tables, grain (ce que représente une ligne), clés primaires et étrangères, types, et pourquoi une base bien conçue **déclare** ses clés ;
- **interroger une table** avec `SELECT`, `WHERE` (comparaisons, `IN`, `LIKE`, `BETWEEN`, précédence de `AND` et `OR`), `ORDER BY`, `LIMIT` et `DISTINCT`, calculer des colonnes avec `CASE` et des fonctions de date ;
- **agréger** avec `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP BY` et `HAVING`, connaître l'**ordre logique d'exécution** (`FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `ORDER BY`, `LIMIT`) et la règle d'or du regroupement ;
- **gérer les valeurs absentes** (`NULL`, logique à trois valeurs, `COALESCE`, `NULLIF`) et éviter quatre pièges silencieux : la division entière, la moyenne des moyennes, `BETWEEN` sur des horodatages, `LIMIT` sans `ORDER BY` ;
- **joindre des tables** (`INNER`, `LEFT`, `FULL`, `CROSS`, auto-jointure), écrire une **anti-jointure** pour trouver ce qui manque, placer un filtre au bon endroit (`ON` ou `WHERE`), joindre sur une clé composée et **empiler ou comparer des ensembles** (`UNION ALL`, `INTERSECT`, `EXCEPT`) ;
- **repérer la multiplication des lignes** après une jointure un-à-plusieurs et l'éviter (agréger avant de joindre, compter des éléments distincts, appliquer le test des trois comptes) ;
- **calculer sans perdre le détail** avec les fonctions fenêtres : parts, classements (`ROW_NUMBER`, `RANK`, `DENSE_RANK`), comparaisons avec la ligne précédente (`LAG`, `LEAD`), cumuls, moyennes mobiles, tranches (`NTILE`) ;
- **structurer une requête complexe** en CTE nommées, par une méthode en six étapes (question, grain, sources, jointures, filtres et agrégats, vérification), fabriquer un calendrier par une CTE récursive, et **vérifier un résultat par un second outil** ;
- (en option) **utiliser sous-requêtes, index, vues, transactions, déclencheurs**, lire un plan d'exécution, se protéger de l'injection SQL, et **situer les dialectes** de PostgreSQL, MySQL, SQL Server et Oracle.

Le chapitre a mis des chiffres sur les questions que la gérante posait en passant dans le couloir. Tous viennent de requêtes réellement exécutées sur la base de la boutique :

| Question | Résultat mesuré |
|---|---|
| Quel chiffre d'affaires en 2025 ? | 1 324 764 € (retrouvé par quatre chemins : somme par catégorie, cumul d'une fenêtre, CTE, pandas) |
| Que pèsent nos dix meilleurs clients ? | 24 886 €, soit **1,88 %** du chiffre d'affaires de 2025 |
| La clientèle est-elle concentrée ? | les 10 % de clients qui dépensent le plus : 32,9 % du chiffre d'affaires ; les 20 % premiers : 51,9 % |
| Combien de clients n'ont jamais commandé ? | 1 194 sur 6 000 (un sur cinq) |
| Fidélité en 2025 | 3 133 clients fidèles, 742 nouveaux, 931 perdus depuis 2024 |
| Quel est l'écart typique entre deux commandes d'un client ? | 86,4 jours en moyenne |
| D'où viennent les retours ? | site : 8,8 % des lignes ; boutique : 3,3 % |
| Quand vend-on le plus ? | décembre (+27,8 % sur novembre) ; le samedi |
| Que coûte une jointure mal écrite ? | le budget publicitaire de 75 995 € devient 2 991 731 € après jointure sur la date : près de **quarante fois** trop |

Le fil conducteur du chapitre tient en une phrase : **une requête est une description précise du tableau que l'on veut, et la précision commence par le grain**. Toutes les erreurs sérieuses vues ici (doubles comptages, filtres qui disparaissent, divisions entières, jours manquants) sont des erreurs de grain : on croyait compter des commandes, on comptait des lignes ; on croyait garder tous les clients, on les filtrait ; on croyait moyenner des paniers, on moyennait des moyennes. Avant chaque requête, écrivez en une phrase ce que représentera **une ligne du résultat** ; après chaque requête, **vérifiez un total** par un autre chemin.

Le chapitre 4 reprend ces mêmes questions avec deux autres langages d'analyse, **Python (pandas)** et **R (tidyverse)**. Vous y retrouverez, sous une autre écriture, les filtres, les regroupements, les jointures et les fenêtres de ce chapitre ; le SQL reste l'outil de choix pour **extraire et résumer** les données à la source, et pandas ou R prennent le relais pour **explorer, modéliser et dessiner**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 (découvrir la base, ventes par canal, meilleurs clients, paniers et doubles comptages, retours, évolution mensuelle, fidélité et cohortes, segmentation RFM, index et plans d'exécution) et exercices 3.1 à 3.14, tous corrigés.

