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
