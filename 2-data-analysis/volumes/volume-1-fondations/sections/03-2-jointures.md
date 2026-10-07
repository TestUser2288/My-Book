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

```python hide
F3.jointures()
```
<!--sortie-->
```text
figure : ch03-jointures.png
```

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

```sql noexec
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

```sql hide-code
SELECT COUNT(*) AS nb_paires_sur_trois_ans
FROM commandes a
JOIN commandes b ON a.id_client = b.id_client AND a.date_commande = b.date_commande AND a.id_commande < b.id_commande
```
<!--sortie-->
```text
 nb_paires_sur_trois_ans
                     321
```

On compte **321 paires** de ce type : à étudier avant de conclure à une erreur, car un client peut très bien passer deux commandes dans la journée.

### 3.2.6 Le piège de la multiplication des lignes

C'est **la** source d'erreurs de chiffres du métier. Rappelons la règle : une jointure « un à plusieurs » **recopie** chaque ligne du côté « un » autant de fois qu'elle a de correspondances du côté « plusieurs ». Les colonnes du côté « un » se retrouvent alors **multipliées**, et toute somme sur ces colonnes est fausse.

Un exemple concret avec le budget publicitaire. La table `jours_exploitation` contient la dépense publicitaire de chaque **jour** ; la table `commandes` contient plusieurs commandes par jour. Si l'on joint les deux sur la date, la dépense d'un jour est recopiée **une fois par commande** de ce jour-là :

```python hide
F3.multiplication()
```
<!--sortie-->
```text
figure : ch03-multiplication.png
```

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
