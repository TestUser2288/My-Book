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

```python hide
import outils_ch03 as F3
F3.schema()
```
<!--sortie-->
```text
figure : ch03-schema.png
```

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

```sql hide
DROP TABLE demo_commandes;
DROP TABLE demo_clients
```

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

```python hide
F3.ordre()
```
<!--sortie-->
```text
figure : ch03-ordre-execution.png
```

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
