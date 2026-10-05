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

```sql hide
SELECT COUNT(*) AS nb FROM clients cl LEFT JOIN commandes c ON c.id_client = cl.id_client WHERE c.id_commande IS NULL;
```
<!--sortie-->
```text
 nb
 14
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
