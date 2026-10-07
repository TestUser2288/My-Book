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

```python hide
import itertools
m_ = pd.read_sql_query("""SELECT strftime('%Y-%m', c.date_commande) AS mois, SUM(l.montant) AS ca FROM commandes c
                          JOIN lignes_commande l USING (id_commande) WHERE c.date_commande >= '2025-01-01' GROUP BY mois ORDER BY mois""", con)
ca_ = list(m_["ca"]); cum_ = list(itertools.accumulate(ca_))
moy_ = [sum(ca_[max(0, i - 2):i + 1]) / len(ca_[max(0, i - 2):i + 1]) for i in range(len(ca_))]
F3.fenetres(list(m_["mois"]), ca_, cum_, moy_)
```
<!--sortie-->
```text
figure : ch03-fenetres.png
```

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

```python hide
dc_ = pd.read_sql_query("""WITH ca_client AS (SELECT c.id_client, SUM(l.montant) AS ca FROM commandes c JOIN lignes_commande l USING (id_commande)
   WHERE c.date_commande >= '2025-01-01' GROUP BY c.id_client), d AS (SELECT ca, NTILE(10) OVER (ORDER BY ca DESC) AS decile FROM ca_client)
   SELECT decile, 100.0 * SUM(ca) / SUM(SUM(ca)) OVER () AS part FROM d GROUP BY decile ORDER BY decile""", con)
F3.deciles(list(dc_["part"]))
```
<!--sortie-->
```text
figure : ch03-deciles.png
```

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
