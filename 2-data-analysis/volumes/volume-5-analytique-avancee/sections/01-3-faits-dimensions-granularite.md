## 1.3 Faits, dimensions et granularité

Dessiner une étoile est facile. La **dessiner juste** demande de répondre, pour chaque table de faits, à une question que l'on esquive trop souvent : **que représente exactement une ligne ?** Cette section pose la règle du **grain**, distingue les mesures qu'on peut additionner de celles qu'on ne peut pas, règle le cas des frais de port, présente trois types de tables de faits, et montre le piège le plus coûteux de l'analyse : **joindre deux tables de faits entre elles**.

```python hide
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as O

for t in ["dim_transporteur", "fait_stock", "fait_retours"]:
    con.executescript(O.sql_de(t))
```

### 1.3.1 Déclarer le grain

Le **grain** d'une table de faits est la phrase qui complète « **une ligne = …** ». Pour `fait_ventes`, c'est « une ligne de commande » : un produit, dans une commande, avec sa quantité. On l'écrit **avant** de choisir les dimensions et les mesures, parce que tout en découle :

- les **dimensions** utilisables sont celles qui ont **une seule valeur** à ce grain (une ligne de commande a un produit et une date, pas deux) ;
- les **mesures** sont celles qui ont un sens **à ce grain** (la quantité d'une ligne, pas le nombre de colis d'une commande) ;
- et l'on peut **tester** le grain : si la clé naturelle est unique, la déclaration tient.

Le test est une requête, qu'on **garde** dans les contrôles du chargement (chapitre 2) :

```sql
SELECT COUNT(*) AS lignes, COUNT(DISTINCT id_ligne) AS id_distincts,
       COUNT(DISTINCT id_commande) AS commandes, COUNT(DISTINCT date_key) AS jours
FROM dwh.fait_ventes;
```
<!--sortie-->
```text
 lignes  id_distincts  commandes  jours
  83905         83905      36395   1096
```

Il y a autant de lignes que d'identifiants distincts : le grain est tenu. Les 83 905 lignes appartiennent à 36 395 commandes, passées sur 1 096 jours.

![Les mêmes ventes à trois grains : de la ligne de commande à la commande, puis au jour. On peut agréger vers un grain plus grossier, jamais l'inverse.](figures/ch01-grain.png)

```python hide
g = con.df("SELECT COUNT(*) AS l, COUNT(DISTINCT id_commande) AS c, COUNT(DISTINCT date_key) AS j FROM dwh.fait_ventes").iloc[0]
O.fig_grain((int(g["l"]), int(g["c"]), int(g["j"])))
assert (int(g["l"]), int(g["c"]), int(g["j"])) == (83905, 36395, 1096)
```
<!--sortie-->
```text
figure : ch01-grain.png
```

> 💡 **Intuition.** Choisir le grain, c'est choisir **le niveau de détail que l'on gardera pour toujours**. Un grain trop fin coûte de la place ; un grain trop grossier **interdit des questions** (« quel produit s'est le mieux vendu le samedi ? » est impossible si l'on n'a gardé que les totaux journaliers). **Dans le doute, on prend le grain le plus fin que la source fournisse.**

> ⚠️ **Piège : mélanger deux grains dans une même table.** Une table qui contient à la fois des lignes de commande et des totaux de commande double tout ce qu'elle additionne. **Un grain par table de faits, sans exception.**

### 1.3.2 Mesures additives, semi-additives, non additives

Toutes les mesures ne s'additionnent pas de la même façon, et se tromper est l'une des erreurs les plus fréquentes.

- Une mesure **additive** peut être additionnée **selon toutes les dimensions** : le montant d'une vente, la quantité. Le chiffre d'affaires du mois est la somme des jours, des produits, des canaux.
- Une mesure **semi-additive** peut être additionnée selon **certaines** dimensions, pas toutes : le **stock** s'additionne d'un produit à l'autre (le stock total du magasin), **mais pas d'un jour à l'autre** (le stock de lundi et celui de mardi sont les **mêmes** articles).
- Une mesure **non additive** ne s'additionne selon **aucune** dimension : un **prix unitaire**, un **pourcentage de remise**, un **taux**. On stocke ses **composantes** (le numérateur et le dénominateur) et l'on recalcule le rapport à la demande.

Un exemple de mesure semi-additive : le stock d'un produit, jour après jour, dans la table `fait_stock` (une ligne par produit et par jour).

```sql
SELECT SUM(stock_fin_jour) AS somme_des_jours, ROUND(AVG(stock_fin_jour), 1) AS moyenne,
       MAX(stock_fin_jour) FILTER (WHERE date_key = 20251231) AS fin_decembre
FROM dwh.fait_stock JOIN dwh.dim_produit USING (produit_key)
WHERE id_produit = 42;
```
<!--sortie-->
```text
 somme_des_jours  moyenne  fin_decembre
           10837     29.7            57
```

Additionner les 365 jours donne « 10 837 articles » pour un produit qui en a **57 en rayon** à la fin de l'année : le chiffre n'a aucun sens. Deux agrégations sont valables : la **moyenne** sur la période (29,7 articles en moyenne) ou la **valeur à une date** (57 au 31 décembre). Ce qui est vrai du stock l'est de tout **solde** : trésorerie, encours, nombre de clients actifs.

Une mesure non additive : le **prix moyen**. La moyenne des prix moyens des six catégories n'est **pas** le prix moyen de l'ensemble des articles vendus, parce que les catégories ne pèsent pas le même nombre d'articles :

```sql
WITH c AS (SELECT p.categorie, SUM(v.montant_ttc) / SUM(v.quantite) AS prix_moyen, SUM(v.quantite) AS q
           FROM dwh.fait_ventes v JOIN dwh.dim_produit p USING (produit_key) GROUP BY 1)
SELECT ROUND(AVG(prix_moyen), 2) AS moyenne_des_prix_moyens,
       ROUND(SUM(prix_moyen * q) / SUM(q), 2) AS prix_moyen_global
FROM c;
```
<!--sortie-->
```text
 moyenne_des_prix_moyens  prix_moyen_global
                   35.11              36.23
```

Le premier chiffre donne le même poids à une catégorie de petits articles (la papeterie, 10 € l'article) et à une catégorie de gros articles (le jardin, 54 €) ; le second est le **vrai** prix moyen (le total d'argent divisé par le total d'articles). C'est pour cela que `fait_ventes` conserve `quantite` et `montant_ttc` : à partir de ces **composantes**, on reconstruit n'importe quel rapport correctement. (`prix_unitaire` et `remise_pct` restent pour l'étude des remises ; on ne les additionne jamais.)

| Mesure | Exemple dans la boutique | Additive ? | Comment l'agréger |
|---|---|---|---|
| quantité vendue | `quantite` | oui | somme |
| montant de la ligne | `montant_ttc`, `montant_ht` | oui | somme |
| coût d'achat de la ligne | `cout_achat` | oui | somme (marge = différence de deux sommes) |
| prix unitaire | `prix_unitaire` | **non** | somme(montant) / somme(quantité) |
| pourcentage de remise | `remise_pct` | **non** | 1 − somme(montant) / somme(prix catalogue × quantité) |
| stock en fin de jour | `stock_fin_jour` | **semi** | somme entre produits ; moyenne ou dernière valeur dans le temps |
| indicateur de retard (0/1) | `retard` | oui, **mais** | le taux est somme(retards) / nombre de livraisons |
| nombre de commandes | `COUNT(DISTINCT id_commande)` | **non** | à recompter à chaque regroupement (voir 1.3.5) |

> ✅ **Règle de conception.** On stocke dans la table de faits des mesures **additives** (montants, quantités, indicateurs 0/1). Tout rapport, taux ou moyenne se **calcule à la demande** à partir de sommes. Ainsi un tableau de bord qui regroupe par mois, par catégorie ou par canal obtient **le même résultat** quel que soit le regroupement.

### 1.3.3 Les mesures de l'en-tête : le cas des frais de port

Une commande a **un** montant de frais de port, et plusieurs lignes. Où ranger cette mesure ? C'est exactement le piège qui a donné un chiffre faux au collègue du service informatique. Si l'on recopie les frais de port sur **chaque ligne** de `fait_ventes`, toute somme les compte autant de fois qu'il y a de lignes.

La bonne solution consiste à créer une **seconde table de faits** au grain de la commande :

```sql
CREATE TABLE dwh.fait_commandes AS
SELECT c.id_commande, cle_date(c.date_commande) AS date_key, k.client_key, ca.canal_key,
       pr.promo_key, COUNT(*) AS nb_lignes, SUM(l.montant) AS montant_ttc,
       MAX(c.frais_port) AS frais_port
FROM src.commandes c JOIN src.lignes_commande l USING (id_commande)
JOIN dwh.dim_client k ON k.id_client = c.id_client
JOIN dwh.dim_canal ca ON ca.canal = c.canal AND ca.mode_livraison = c.mode_livraison
JOIN dwh.dim_promotion pr ON pr.code_promo = COALESCE(c.code_promo, 'Aucune')
GROUP BY ALL;
```

La table a une ligne par commande (`GROUP BY ALL` regroupe par toutes les colonnes qui ne sont pas des agrégats). Le grain est **déclaré** (une commande) ; les frais de port y sont **additifs**. Voyons l'écart entre les deux façons de les compter, sur les trois années :

```sql
SELECT (SELECT ROUND(SUM(frais_port), 1) FROM dwh.fait_commandes) AS frais_port_vrai,
       (SELECT ROUND(SUM(c.frais_port), 1) FROM src.commandes c
        JOIN src.lignes_commande l USING (id_commande)) AS frais_port_repete;
```
<!--sortie-->
```text
 frais_port_vrai  frais_port_repete
         46084.6            75458.3
```

La version « répétée » est **64 % trop haute** (75 458 € au lieu de 46 085 €), et rien dans la requête ne le signale.

Que faire si l'on a **vraiment besoin** des frais de port au niveau de la ligne (par exemple pour calculer une marge par produit nette des frais de livraison) ? On **répartit** : chaque ligne reçoit une part, proportionnelle à son montant, **et la somme des parts doit retrouver le total**.

```sql
SELECT ROUND(SUM(c.frais_port * v.montant_ttc / c.montant_ttc), 1) AS total_reparti,
       ROUND((SELECT SUM(frais_port) FROM dwh.fait_commandes), 1) AS total_commandes
FROM dwh.fait_ventes v JOIN dwh.fait_commandes c ON c.id_commande = v.id_commande;
```
<!--sortie-->
```text
 total_reparti  total_commandes
       46084.6          46084.6
```

La répartition est une **règle de gestion** (au prorata du montant, de la quantité, du poids…), pas un fait : elle doit être **écrite, validée et conservée** à part, et son contrôle (« la somme des parts égale le total ») fait partie du chargement.

> ⚠️ **Piège : les mesures de l'en-tête.** Tout ce qui est décrit **une fois par document** (frais de port, remise globale de commande, acompte, nombre de colis) et qu'on recopie à la ligne est un doublon en puissance. Trois solutions, par ordre de préférence : une table de faits **à son propre grain** ; une **répartition** contrôlée ; ne pas la stocker à la ligne.

### 1.3.4 Trois types de tables de faits

Selon ce que l'on mesure, la table de faits prend l'une de trois formes.

![Trois types de tables de faits : transaction (une ligne par événement), instantané périodique (une ligne par entité et par période), cumulative (une ligne par processus, complétée au fil des jalons).](figures/ch01-types-faits.png)

```python hide
O.fig_types_faits()
```
<!--sortie-->
```text
figure : ch01-types-faits.png
```

- **La table de transactions** a une ligne par **événement**, au moment où il se produit : une vente, un retour, un paiement. C'est la plus simple et la plus courante ; c'est `fait_ventes`.
- **L'instantané périodique** a une ligne par **entité et par période**, qu'il se passe quelque chose ou non : le stock de chaque produit chaque jour (`fait_stock`), le solde de chaque compte chaque mois. Elle permet de répondre à « quel était l'état un jour donné ? », ce qu'une table de transactions ne donne qu'au prix d'un recalcul.
- **La table cumulative** (*accumulating snapshot*) a une ligne par **processus** qui a un début, une fin et des **jalons** : une livraison (commande, expédition, livraison). La ligne est créée à la commande, puis **mise à jour** à chaque jalon. Ses mesures sont des **durées entre jalons**.

Construisons la table cumulative des livraisons de la boutique : **trois dates** (trois clés vers la même dimension de date) et les durées calculées une fois.

```sql
CREATE TABLE dwh.fait_livraisons AS
SELECT l.id_commande, ca.canal_key, t.transporteur_key,
       cle_date(l.date_commande) AS date_commande_key,
       cle_date(l.date_expedition) AS date_expedition_key,
       cle_date(l.date_livraison) AS date_livraison_key,
       date_diff('day', l.date_commande, l.date_expedition) AS delai_preparation_j,
       date_diff('day', l.date_expedition, l.date_livraison) AS delai_transport_j,
       date_diff('day', l.date_commande, l.date_livraison) AS delai_total_j,
       l.delai_promis_j, l.retard, l.colis_abime
FROM src.livraisons l
JOIN dwh.dim_canal ca ON ca.canal = l.canal AND ca.mode_livraison = l.mode_livraison
JOIN dwh.dim_transporteur t ON t.transporteur = l.transporteur;
```

Les trois clés de date s'appellent « **dimension jouant plusieurs rôles** » : la **même** dimension de date sert à la commande, à l'expédition et à la livraison. On la joint **trois fois**, sous trois alias, selon la question posée.

La table cumulative sait aussi dire **où en est** chaque processus à une date donnée : un jalon n'est « rempli » à une date que s'il lui est antérieur. Dans nos données, toutes les livraisons sont terminées ; en remontant le temps au 29 décembre 2025, on reconstitue ce que l'on aurait vu ce jour-là :

```sql
SELECT CASE WHEN date_livraison_key <= 20251229 THEN '3 livrée'
            WHEN date_expedition_key <= 20251229 THEN '2 expédiée, en transit'
            ELSE '1 commandée, non expédiée' END AS etat, COUNT(*) AS commandes
FROM dwh.fait_livraisons WHERE date_commande_key <= 20251229
GROUP BY 1 ORDER BY 1;
```
<!--sortie-->
```text
                     etat  commandes
1 commandée, non expédiée         67
   2 expédiée, en transit        168
                 3 livrée      19127
```

Enfin, l'intérêt de cette table : les **durées** s'agrègent proprement par transporteur (on retrouve le résultat du volume III, section 11.1.3 : le transporteur C est le plus lent et le moins ponctuel).

```sql
SELECT t.transporteur, COUNT(*) AS commandes, ROUND(AVG(delai_total_j), 2) AS delai_moyen_j,
       ROUND(100 * AVG(retard), 1) AS retard_pct
FROM dwh.fait_livraisons f JOIN dwh.dim_transporteur t USING (transporteur_key)
GROUP BY 1 ORDER BY 1;
```
<!--sortie-->
```text
  transporteur  commandes  delai_moyen_j  retard_pct
Transporteur A       8734           5.21        16.0
Transporteur B       6915           5.82        26.6
Transporteur C       3771           6.68        51.0
```

Le « taux de retard » est ici la **moyenne d'un indicateur 0/1** : on stocke le 0/1 (additif), le pourcentage s'obtient en divisant la somme par le nombre de lignes. Et un taux ne se « moyenne » pas : la moyenne simple des trois taux est de 31,2 %, alors que le taux global, pondéré par le nombre de commandes de chaque transporteur, est de 26,6 %.

```python hide
tt = con.df("SELECT transporteur_key, AVG(retard) AS taux, COUNT(*) AS n FROM dwh.fait_livraisons GROUP BY 1")
assert round(100 * tt["taux"].mean(), 1) == 31.2 and round(100 * (tt["taux"] * tt["n"]).sum() / tt["n"].sum(), 1) == 26.6
```

| Type | Une ligne = | Mises à jour | Exemple | Pour répondre à… |
|---|---|---|---|---|
| **Transaction** | un événement | jamais (on ajoute) | vente, retour | « combien, quand, à qui ? » |
| **Instantané périodique** | une entité × une période | jamais (on ajoute une période) | stock quotidien | « quel était l'état à telle date ? » |
| **Cumulative** | un processus avec jalons | **oui**, à chaque jalon | livraison | « combien de temps entre les étapes ? » |

### 1.3.5 Dimensions : clés, hiérarchies, rôles, valeurs inconnues

Une bonne dimension est **large** (beaucoup d'attributs descriptifs, de quoi grouper et filtrer), **lisible** (« Carte fidélité » plutôt que `1`) et **stable** (on ne la reconstruit pas à chaque question). Quelques notions complètent ce que nous avons vu.

- **Hiérarchies.** Une dimension contient souvent des niveaux emboîtés : jour → mois → trimestre → année pour la date ; produit → catégorie pour les produits. Ils permettent de **descendre** (de l'année aux mois) ou de **remonter** dans l'analyse sans nouvelle table.
- **Dimension dégénérée.** Un identifiant qui n'a **pas d'attributs** (ici `id_commande`) reste **dans la table de faits** : il sert à regrouper des lignes (retrouver toutes les lignes d'une commande) sans créer une dimension vide.
- **Dimension fourre-tout.** Quelques indicateurs de faible cardinalité (canal de vente, mode de livraison) se regroupent en **une** dimension, comme `dim_canal` (7 lignes).
- **Clé naturelle et clé de substitution.** Le produit de l'exemple d'ouverture a **120 identifiants pour 60 noms**. La dimension a une ligne par **identifiant** : regrouper par nom revient à **fusionner deux produits**, et c'est un choix métier, pas un accident de jointure.
- **Valeur inconnue.** Un fait peut arriver **avant** sa dimension (une vente d'un client créé à la caisse mais pas encore chargé). Si l'on perd ces lignes à la jointure, le chiffre d'affaires est **faux sans erreur**. La règle : le chargement attribue la clé **0** (« inconnu ») et la ligne est conservée, **corrigée plus tard** quand la dimension se complète.

Simulons l'incident sur une copie de la dimension où l'on retire, de façon arbitraire, un client sur cinquante :

```sql hide
CREATE TABLE dwh.dim_client_incomplet AS SELECT * FROM dwh.dim_client WHERE client_key = 0 OR client_key % 50 <> 0;
```

```sql
SELECT 'jointure interne' AS methode, COUNT(*) AS lignes, ROUND(SUM(v.montant_ttc)) AS ca_ttc
FROM dwh.fait_ventes v JOIN dwh.dim_client_incomplet k USING (client_key)
UNION ALL
SELECT 'jointure externe (inconnu = 0)', COUNT(*), ROUND(SUM(v.montant_ttc))
FROM dwh.fait_ventes v LEFT JOIN dwh.dim_client_incomplet k USING (client_key);
```
<!--sortie-->
```text
                       methode  lignes    ca_ttc
              jointure interne   82334 3586636.0
jointure externe (inconnu = 0)   83905 3653157.0
```

Avec la jointure interne, **1 571 lignes et 66 521 € de chiffre d'affaires disparaissent silencieusement** (1,8 %) ; la jointure externe les conserve, rattachées au client « inconnu ». Un contrôle simple, à placer dans chaque chargement : **le total de la table de faits doit être égal à celui de la source** (nous l'avons fait en 1.2.2).

La valeur inconnue illustre aussi pourquoi un **nombre de commandes** ne s'additionne pas : une commande qui comprend des produits de deux catégories est comptée **dans chaque catégorie**.

```sql
SELECT SUM(n) AS somme_des_categories, (SELECT COUNT(DISTINCT id_commande) FROM dwh.fait_ventes
       WHERE date_key BETWEEN 20250101 AND 20251231) AS commandes_distinctes
FROM (SELECT p.categorie, COUNT(DISTINCT v.id_commande) AS n
      FROM dwh.fait_ventes v JOIN dwh.dim_produit p USING (produit_key)
      WHERE v.date_key BETWEEN 20250101 AND 20251231 GROUP BY 1);
```
<!--sortie-->
```text
 somme_des_categories  commandes_distinctes
                25163                 12946
```

La somme des commandes par catégorie (25 163) dépasse presque du double le nombre de commandes **distinctes** (12 946). On ne stocke donc pas « le nombre de commandes » comme une mesure : on **recompte** les identifiants distincts à chaque regroupement.

### 1.3.6 Plusieurs faits, dimensions conformes, et le piège du fan-out

Une boutique a plusieurs processus (ventes, retours, livraisons, stock) donc **plusieurs tables de faits**. Elles se **rejoignent** par des dimensions **communes** : la même `dim_date`, la même `dim_produit`, la même `dim_canal`. On les appelle des **dimensions conformes** : définies **une fois**, avec les mêmes clés et les mêmes attributs, utilisées partout. C'est ce qui permet de dire « le taux de retour par catégorie » : la catégorie des ventes et celle des retours sont **la même colonne**.

La tentation est alors de **joindre directement** les deux tables de faits sur la dimension commune. **C'est l'erreur la plus coûteuse de l'analyse.** Voici ce que donne la jointure de `fait_ventes` et `fait_retours` sur le produit, pour le chiffre d'affaires 2025 :

```sql
SELECT p.categorie, ROUND(SUM(v.montant_ht)) AS ca_ht_faux
FROM dwh.fait_ventes v
JOIN dwh.fait_retours r ON r.produit_key = v.produit_key
JOIN dwh.dim_produit p ON p.produit_key = v.produit_key
JOIN dwh.dim_date d ON d.date_key = v.date_key
WHERE d.annee = 2025 GROUP BY 1 ORDER BY 1;
```
<!--sortie-->
```text
 categorie  ca_ht_faux
 Bien-être   3608814.0
   Cuisine  11152068.0
Décoration  12339746.0
    Jardin  18045451.0
    Maison  11936142.0
 Papeterie   1818971.0
```

Le chiffre d'affaires des jardins passe de 295 k€ à **18 millions d'euros**. Chaque vente a été dupliquée **autant de fois que le produit a de retours** : la jointure fabrique le produit cartésien, produit par produit. La requête a l'air correcte, tourne sans erreur, et donne un résultat absurde ; un résultat **légèrement** faux (un facteur 1,3) ne se verrait pas.

La règle est de **ne jamais joindre deux tables de faits entre elles**. On **agrège chacune** à la maille commune (ici le produit), **puis** on joint les résultats : c'est ce qu'on appelle le **drill-across**.

```sql
WITH v AS (SELECT produit_key, SUM(montant_ht) AS ca FROM dwh.fait_ventes
           JOIN dwh.dim_date USING (date_key) WHERE annee = 2025 GROUP BY 1),
     r AS (SELECT produit_key, SUM(montant_rembourse) / 1.2 AS retours FROM dwh.fait_retours
           JOIN dwh.dim_date USING (date_key) WHERE annee = 2025 GROUP BY 1)
SELECT p.categorie, ROUND(SUM(ca)) AS ca_ht, ROUND(SUM(COALESCE(retours, 0))) AS retours_ht,
       ROUND(100 * SUM(COALESCE(retours, 0)) / SUM(ca), 1) AS taux_pct
FROM v LEFT JOIN r USING (produit_key) JOIN dwh.dim_produit p USING (produit_key)
GROUP BY 1 ORDER BY 1;
```
<!--sortie-->
```text
 categorie    ca_ht  retours_ht  taux_pct
 Bien-être  97926.0      6201.0       6.3
   Cuisine 194427.0     12160.0       6.3
Décoration 215619.0     13292.0       6.2
    Jardin 294962.0     20023.0       6.8
    Maison 253845.0     15287.0       6.0
 Papeterie  47191.0      2776.0       5.9
```

Les chiffres sont maintenant cohérents : le chiffre d'affaires par catégorie est celui de 1.2, et le taux de retour se situe entre 5,9 % et 6,8 %, quelle que soit la catégorie. (Les retours de 2025 sont rapportés aux ventes de 2025 ; ils concernent en partie des ventes de la fin de 2024, et le taux est donc approché.) On a utilisé une **jointure externe** (`LEFT JOIN`) pour ne pas perdre un produit sans retour : la même erreur de perte silencieuse, sous une autre forme.

> ⚠️ **Piège : le fan-out.** Joindre deux tables de faits sur une dimension commune **multiplie** les lignes (chaque ligne de l'une est appariée à toutes celles de l'autre qui ont la même clé). Symptôme : un total qui **grossit** après une jointure. Contrôle : comparer le total avant et après. Remède : **agréger d'abord, joindre ensuite**.

> 🧭 **En pratique : cinq questions avant de créer une table de faits.**
> 1. Quel **processus** mesure-t-elle (vendre, retourner, livrer, stocker) ?
> 2. Quel est son **grain** (« une ligne = … ») ? Peut-on le **tester** ?
> 3. Quelles **dimensions** ont **une seule valeur** à ce grain, et lesquelles sont **conformes** avec les autres faits ?
> 4. Quelles **mesures**, et sont-elles **additives** (sinon : quelles composantes stocker) ?
> 5. De quel **type** est-elle (transaction, instantané, cumulative) et comment la **contrôle**-t-on (effectifs, totaux, clés inconnues) ?

> ✅ **À retenir.**
> - Un **grain par table de faits**, déclaré par une phrase (« une ligne = … ») et **testé**.
> - On stocke des mesures **additives** ; les taux, prix et pourcentages se recalculent à partir de **sommes** ; un **solde** (stock) ne s'additionne pas dans le temps.
> - Une mesure de l'**en-tête** (frais de port) ne se recopie pas à la ligne : table à son grain, ou répartition contrôlée.
> - Trois types : **transaction**, **instantané périodique**, **cumulative** (jalons, dimension de date à plusieurs rôles).
> - **Valeur inconnue** (clé 0) plutôt que ligne perdue ; **dimensions conformes** pour comparer des processus ; **jamais de jointure entre deux faits** : agréger d'abord, joindre ensuite.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.4 et 1.5, exercices 1.5 à 1.9.
