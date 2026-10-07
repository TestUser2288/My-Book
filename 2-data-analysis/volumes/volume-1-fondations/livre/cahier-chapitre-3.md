# Chapitre 3 : SQL — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 3 du livre. Les **applications** sont de petites études guidées sur la base `boutique.db`, à refaire pas à pas ; les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ plus long) vous demandent d'écrire vos propres requêtes ; les **corrigés** suivent. Une règle d'or : **avant** de lire un corrigé, écrivez votre requête, exécutez-la, et vérifiez au moins **un total** par un autre chemin. Le cahier est autonome : la cellule suivante ouvre une **copie jetable** de la base (vous pouvez y créer des index et des vues sans rien abîmer).

```python
import os, shutil, sqlite3, tempfile
import pandas as pd

TMP3C = tempfile.mkdtemp(prefix="sql3c_", dir=os.environ.get("TMPDIR"))
shutil.copy(os.path.join(os.environ["DONNEES"], "boutique.db"), os.path.join(TMP3C, "boutique.db"))
con = sqlite3.connect(os.path.join(TMP3C, "boutique.db"))
```

## Applications

### Application 3.1 — Découvrir la base (section 3.1)

**Objectif.** Avant toute analyse, on **inspecte** la base : que contient-elle, sur quelle période, avec quelles valeurs, et les données sont-elles saines ? Cette application est le rituel d'ouverture de n'importe quelle étude.

**Étape 1 — Les tables et leurs colonnes.** Une petite boucle Python interroge le catalogue de la base :

```python
for t in ("clients", "produits", "commandes", "lignes_commande", "retours", "jours_exploitation"):
    nb = con.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
    cols = [r[1] for r in con.execute(f"PRAGMA table_info({t})")]
    print(f"{t:19s} {nb:>6d} lignes, {len(cols)} colonnes : {', '.join(cols[:4])}…")
```
<!--sortie-->
```text
clients               6000 lignes, 8 colonnes : id_client, date_inscription, annee_naissance, ville…
produits               120 lignes, 7 colonnes : id_produit, nom_produit, categorie, prix_vente…
commandes            36395 lignes, 7 colonnes : id_commande, date_commande, heure, id_client…
lignes_commande      83905 lignes, 7 colonnes : id_ligne, id_commande, id_produit, quantite…
retours               5002 lignes, 5 colonnes : id_retour, id_ligne, date_retour, motif…
jours_exploitation    1096 lignes, 8 colonnes : date, jour_semaine, nb_commandes, chiffre_affaires…
```

**Étape 2 — La période couverte.** Les trois dates à connaître : première et dernière commande, première et dernière inscription.

```sql
SELECT (SELECT MIN(date_commande) FROM commandes) AS premiere_commande,
       (SELECT MAX(date_commande) FROM commandes) AS derniere_commande,
       (SELECT MIN(date_inscription) FROM clients) AS premiere_inscription,
       (SELECT MAX(date_inscription) FROM clients) AS derniere_inscription
```
<!--sortie-->
```text
premiere_commande derniere_commande premiere_inscription derniere_inscription
       2023-01-01        2025-12-31           2018-01-01           2025-12-30
```

**Étape 3 — Les modalités des variables qualitatives.** `GROUP BY` + `COUNT(*)` donne la distribution de chaque colonne de texte ; on regarde si les libellés sont cohérents (casse, fautes, valeurs inattendues) :

```sql
SELECT 'canal' AS variable, canal AS modalite, COUNT(*) AS nb FROM commandes GROUP BY canal
UNION ALL SELECT 'code_promo', CASE WHEN code_promo = '' THEN '(aucun)' ELSE code_promo END, COUNT(*) FROM commandes GROUP BY code_promo
UNION ALL SELECT 'motif de retour', motif, COUNT(*) FROM retours GROUP BY motif
ORDER BY variable, nb DESC
```
<!--sortie-->
```text
       variable          modalite    nb
          canal          Boutique 16975
          canal              Site 15463
          canal           Réseaux  3957
     code_promo           (aucun) 30652
     code_promo            SOLDES  3006
     code_promo          FIDELITE  2423
     code_promo         BIENVENUE   314
motif de retour     Mauvais choix  1571
motif de retour Changement d'avis  1518
motif de retour            Défaut   908
motif de retour Livraison tardive   605
motif de retour             Autre   400
```

**Étape 4 — Les contrôles de santé.** Trois contrôles qui ne doivent rien renvoyer : une clé en double, une quantité ou un montant qui n'est pas strictement positif, un retour **antérieur** à la commande.

```sql
SELECT 'clés de commande en double' AS controle, COUNT(*) - COUNT(DISTINCT id_commande) AS anomalies FROM commandes
UNION ALL SELECT 'lignes avec quantité ou montant <= 0', COUNT(*) FROM lignes_commande WHERE quantite <= 0 OR montant <= 0
UNION ALL SELECT 'retours avant la commande', COUNT(*)
          FROM retours r JOIN lignes_commande l USING (id_ligne) JOIN commandes c USING (id_commande)
          WHERE r.date_retour < c.date_commande
```
<!--sortie-->
```text
                            controle  anomalies
          clés de commande en double          0
lignes avec quantité ou montant <= 0          0
           retours avant la commande          0
```

> **Lecture.** La base couvre les commandes du **1er janvier 2023 au 31 décembre 2025**, et les inscriptions de 2018 à 2025 (4 000 clients étaient déjà inscrits en 2023). Les canaux sont bien trois, sans variante d'écriture ; **84 % des commandes n'ont aucun code promo** (enregistré par un texte vide : voir 3.1.8). Les trois contrôles renvoient 0 : on peut travailler. Sur une vraie base, un contrôle non nul n'est pas un échec mais une **découverte** à documenter.
>
> **À vous.** Ajoutez deux contrôles de votre choix (une date de commande postérieure à la date du jour, un prix de vente inférieur au coût d'achat).

### Application 3.2 — Les ventes par canal et par année (sections 3.1 et 3.2)

**Objectif.** Construire le tableau que la gérante réclame depuis des mois : le chiffre d'affaires de chaque canal, année par année, et la part du site.

**Étape 1 — Un tableau croisé en SQL.** Pour mettre les canaux en **colonnes**, on utilise un `SUM(CASE WHEN …)` par canal :

```sql
SELECT strftime('%Y', c.date_commande) AS annee,
       ROUND(SUM(CASE WHEN c.canal = 'Boutique' THEN l.montant END)) AS boutique,
       ROUND(SUM(CASE WHEN c.canal = 'Site' THEN l.montant END)) AS site,
       ROUND(SUM(CASE WHEN c.canal = 'Réseaux' THEN l.montant END)) AS reseaux,
       ROUND(SUM(l.montant)) AS total
FROM commandes c JOIN lignes_commande l USING (id_commande)
GROUP BY annee
ORDER BY annee
```
<!--sortie-->
```text
annee  boutique     site  reseaux     total
 2023  593612.0 422440.0 122880.0 1138932.0
 2024  558143.0 502531.0 128787.0 1189461.0
 2025  560974.0 617715.0 146074.0 1324764.0
```

**Étape 2 — La part du site et la croissance.** Le même calcul, exprimé en pourcentages :

```sql
WITH t AS (
  SELECT strftime('%Y', c.date_commande) AS annee,
         SUM(CASE WHEN c.canal = 'Site' THEN l.montant END) AS site, SUM(l.montant) AS total
  FROM commandes c JOIN lignes_commande l USING (id_commande) GROUP BY annee)
SELECT annee, ROUND(100.0 * site / total, 1) AS part_site_pct,
       ROUND(100.0 * (total / LAG(total) OVER (ORDER BY annee) - 1), 1) AS croissance_totale_pct
FROM t ORDER BY annee
```
<!--sortie-->
```text
annee  part_site_pct  croissance_totale_pct
 2023           37.1                    NaN
 2024           42.2                    4.4
 2025           46.6                   11.4
```

> **Lecture.** Le chiffre d'affaires passe de 1,14 million d'euros en 2023 à **1,32 million en 2025**. La **boutique** recule légèrement (593 612 € puis 558 143 €, 560 974 €) tandis que le **site** progresse très fortement (422 440 € puis 502 531 €, 617 715 €) : sa part passe de 37,1 % à 46,6 %, et il dépasse la boutique en 2025. Le site ne « mange » pas (seulement) la boutique : la croissance totale est positive chaque année (+4,4 % puis +11,4 %). C'est l'élément de réponse à la question que la gérante se pose ; il ne la tranche pas (les clients du site sont-ils les mêmes ?), ce que l'application 3.7 permet d'examiner.
>
> **À vous.** Ajoutez une colonne « part des réseaux » et reproduisez le tableau par **catégorie de produit** au lieu du canal (il faudra joindre `produits`).

### Application 3.3 — Les meilleurs clients (sections 3.2 et 3.4)

**Objectif.** Aller plus loin que « les dix premiers » du livre : qui sont les meilleurs clients, d'où viennent-ils, et le sont-ils d'une année sur l'autre ?

**Étape 1 — Le chiffre d'affaires par client et par ville.** On part d'une CTE du chiffre d'affaires 2025 par client, puis on joint les clients pour récupérer leur ville :

```sql
WITH ca AS (
  SELECT c.id_client, SUM(l.montant) AS ca
  FROM commandes c JOIN lignes_commande l USING (id_commande)
  WHERE c.date_commande >= '2025-01-01' GROUP BY c.id_client)
SELECT cl.ville, COUNT(*) AS clients, ROUND(SUM(ca.ca)) AS ca, ROUND(AVG(ca.ca), 1) AS ca_moyen
FROM ca JOIN clients cl USING (id_client)
GROUP BY cl.ville ORDER BY ca DESC LIMIT 5
```
<!--sortie-->
```text
  ville  clients       ca  ca_moyen
Ville A      532 184324.0     346.5
Ville B      471 164880.0     350.1
Ville C      401 121696.0     303.5
Ville D      364 116870.0     321.1
Ville E      330 102757.0     311.4
```

**Étape 2 — La persistance du top 100.** Combien des cent meilleurs clients de 2025 étaient déjà dans les cent meilleurs de 2024 ? `INTERSECT` répond :

```sql
WITH ca25 AS (
  SELECT c.id_client, SUM(l.montant) AS ca FROM commandes c JOIN lignes_commande l USING (id_commande)
  WHERE c.date_commande >= '2025-01-01' GROUP BY c.id_client ORDER BY ca DESC LIMIT 100),
ca24 AS (
  SELECT c.id_client, SUM(l.montant) AS ca FROM commandes c JOIN lignes_commande l USING (id_commande)
  WHERE c.date_commande >= '2024-01-01' AND c.date_commande < '2025-01-01' GROUP BY c.id_client ORDER BY ca DESC LIMIT 100)
SELECT COUNT(*) AS dans_les_deux_top100 FROM (SELECT id_client FROM ca25 INTERSECT SELECT id_client FROM ca24)
```
<!--sortie-->
```text
 dans_les_deux_top100
                   28
```

> **Lecture.** Les villes A et B concentrent à elles deux un quart du chiffre d'affaires de 2025 (184 324 € et 164 880 €), avec un chiffre d'affaires moyen par client voisin de 350 € ; les autres villes tournent autour de 300 €. Et **28 clients seulement** sur 100 figurent dans le top 100 des deux années : le « meilleur client » d'une année **n'est pas** celui de l'année suivante. Un top de clients est donc une photographie, pas une caste : **72 clients sur 100 changent** d'une année à l'autre, et bâtir un programme de fidélité sur la liste d'une seule année serait coûteux et peu efficace (c'est ce que l'on appelle la **régression vers la moyenne** : un client exceptionnel une année l'est moins l'année suivante).
>
> **À vous.** Calculez la part de chaque ville dans le chiffre d'affaires **total** avec une fonction fenêtre (`SUM(ca) OVER ()`).

### Application 3.4 — Panier moyen et double comptage (section 3.2.6)

**Objectif.** Mettre en pratique le **test des trois comptes** et mesurer précisément les dégâts d'un grain mal compris.

**Étape 1 — Combien de commandes ?** Trois façons de « compter les commandes » donnent trois résultats différents :

```sql
SELECT (SELECT COUNT(*) FROM commandes) AS dans_commandes,
       (SELECT COUNT(*) FROM commandes c JOIN lignes_commande l USING (id_commande)) AS apres_jointure,
       (SELECT COUNT(DISTINCT c.id_commande) FROM commandes c JOIN lignes_commande l USING (id_commande)) AS apres_jointure_distinct
```
<!--sortie-->
```text
 dans_commandes  apres_jointure  apres_jointure_distinct
          36395           83905                    36395
```

**Étape 2 — Panier moyen, par canal et par année.** On construit d'abord le grain « une ligne par commande » dans une CTE, puis on moyenne :

```sql
WITH par_commande AS (
  SELECT c.id_commande, c.canal, strftime('%Y', c.date_commande) AS annee, SUM(l.montant) AS panier
  FROM commandes c JOIN lignes_commande l USING (id_commande) GROUP BY c.id_commande)
SELECT annee, canal, COUNT(*) AS nb_commandes, ROUND(AVG(panier), 2) AS panier_moyen
FROM par_commande GROUP BY annee, canal ORDER BY annee, canal
```
<!--sortie-->
```text
annee    canal  nb_commandes  panier_moyen
 2023 Boutique          5916        100.34
 2023  Réseaux          1230         99.90
 2023     Site          4272         98.89
 2024 Boutique          5617         99.37
 2024  Réseaux          1301         98.99
 2024     Site          5113         98.28
 2025 Boutique          5442        103.08
 2025  Réseaux          1426        102.44
 2025     Site          6078        101.63
```

**Étape 3 — Le même calcul, faux.** Moyenner directement les lignes donne un tout autre nombre :

```sql
SELECT ROUND(AVG(l.montant), 2) AS montant_moyen_par_ligne,
       ROUND(SUM(l.montant) / COUNT(DISTINCT c.id_commande), 2) AS panier_moyen
FROM commandes c JOIN lignes_commande l USING (id_commande)
```
<!--sortie-->
```text
 montant_moyen_par_ligne  panier_moyen
                   43.54        100.38
```

> **Lecture.** Les trois comptes sont **36 395** (commandes), **83 905** (après jointure : des lignes) et **36 395** (après jointure, en comptant des commandes distinctes) : la jointure multiplie par 2,3 le nombre de lignes, et seul le `DISTINCT` rend le bon résultat. Le panier moyen est remarquablement **stable** : entre 98 € et 103 € dans les neuf combinaisons année × canal. Le seul saut visible est celui de 2025 (environ +3 %, de 99 € à 102 € en moyenne), qui correspond à la **hausse de prix de 3 % du 1er janvier 2025** (une vérité programmée dans les données) : hors hausse de prix, la croissance du chiffre d'affaires vient du **nombre de commandes**, pas du panier. L'étape 3 oppose le **montant moyen par ligne** (43,54 €) au panier moyen (100,38 €) : la première moyenne répond à « combien coûte un article acheté », la seconde à « combien dépense un client à chaque passage ». Les deux sont justes, à condition de savoir laquelle on cite.
>
> **À vous.** Pourquoi le panier moyen par ligne est-il plus faible que le prix catalogue moyen ? (Indice : regardez `remise_pct` et le poids des petits prix.)

### Application 3.5 — Les retours : combien, d'où, pourquoi (sections 3.2 et 3.4)

**Objectif.** Quantifier les retours pour la gérante : quels motifs, quels canaux, quelles catégories ?

**Étape 1 — Les motifs de retour par canal** (les six premiers) :

```sql
SELECT r.motif, c.canal, COUNT(*) AS nb
FROM retours r JOIN lignes_commande l USING (id_ligne) JOIN commandes c USING (id_commande)
GROUP BY r.motif, c.canal ORDER BY nb DESC LIMIT 6
```
<!--sortie-->
```text
            motif    canal   nb
    Mauvais choix     Site 1000
Changement d'avis     Site  970
           Défaut     Site  572
    Mauvais choix Boutique  382
Livraison tardive     Site  377
Changement d'avis Boutique  373
```

**Étape 2 — Le taux de retour par canal puis par catégorie**, sur les trois années (la jointure à gauche garde les lignes sans retour) :

```sql
SELECT 'canal' AS axe, c.canal AS modalite, COUNT(*) AS lignes, COUNT(r.id_retour) AS retours,
       ROUND(100.0 * COUNT(r.id_retour) / COUNT(*), 1) AS taux_pct
FROM lignes_commande l JOIN commandes c USING (id_commande) LEFT JOIN retours r ON r.id_ligne = l.id_ligne
GROUP BY c.canal
UNION ALL
SELECT 'catégorie', p.categorie, COUNT(*), COUNT(r.id_retour), ROUND(100.0 * COUNT(r.id_retour) / COUNT(*), 1)
FROM lignes_commande l JOIN produits p USING (id_produit) LEFT JOIN retours r ON r.id_ligne = l.id_ligne
GROUP BY p.categorie
```
<!--sortie-->
```text
      axe   modalite  lignes  retours  taux_pct
    canal   Boutique   39362     1211       3.1
    canal    Réseaux    9071      605       6.7
    canal       Site   35472     3186       9.0
catégorie  Bien-être   10347      629       6.1
catégorie    Cuisine   14750      907       6.1
catégorie Décoration   16575     1001       6.0
catégorie     Jardin   14977      922       6.2
catégorie     Maison   14596      855       5.9
catégorie  Papeterie   12660      688       5.4
```

> **Lecture.** Les trois premiers motifs sont tous sur le **site** : « mauvais choix » (1 000 retours), « changement d'avis » (970) et « défaut » (572). Le taux de retour **varie très peu d'une catégorie à l'autre** (de 5,4 % pour la papeterie à 6,2 % pour le jardin) mais **beaucoup d'un canal à l'autre** (3,1 % pour la boutique, 6,7 % pour les réseaux, **9,0 % pour le site**, sur les trois années). Le problème des retours est donc un problème de **canal** (vente à distance, impossibilité d'essayer), non de produit. Le tableau le montre avec des chiffres, ce qui évite d'accuser à tort les fournisseurs.
>
> **À vous.** Calculez le montant remboursé par catégorie et le rapport entre ce montant et le chiffre d'affaires de la catégorie.

### Application 3.6 — Évolution mensuelle, cumul et comparaison à l'an dernier (section 3.3)

**Objectif.** Produire le tableau de bord mensuel que la gérante lira chaque début de mois : le chiffre d'affaires du mois, le même mois un an plus tôt et l'évolution.

**Étape 1 — Comparer à l'an dernier avec `LAG(…, 12)`.** Les mois étant consécutifs, le même mois de l'année précédente est 12 lignes plus haut :

```sql
WITH m AS (
  SELECT strftime('%Y-%m', c.date_commande) AS mois, SUM(l.montant) AS ca
  FROM commandes c JOIN lignes_commande l USING (id_commande) GROUP BY mois)
SELECT mois, ROUND(ca) AS ca, ROUND(LAG(ca, 12) OVER (ORDER BY mois)) AS ca_an_dernier,
       ROUND(100.0 * (ca / LAG(ca, 12) OVER (ORDER BY mois) - 1), 1) AS evol_an_pct
FROM m ORDER BY mois DESC LIMIT 6
```
<!--sortie-->
```text
   mois       ca  ca_an_dernier  evol_an_pct
2025-12 183845.0       157304.0         16.9
2025-11 143892.0       131726.0          9.2
2025-10 120064.0       101693.0         18.1
2025-09 113453.0       101340.0         12.0
2025-08  89898.0        81188.0         10.7
2025-07 111221.0        93847.0         18.5
```

**Étape 2 — Le cumul depuis janvier, recommencé chaque année.** `PARTITION BY` sur l'année recommence le cumul. Le cumul est calculé sur **tous** les mois dans une première étape, et le filtre sur juin et décembre n'intervient qu'ensuite (le piège de la section 3.3.2 : un `WHERE` placé au même niveau que la fenêtre priverait le cumul de ses mois) :

```sql
WITH m AS (
  SELECT strftime('%Y', c.date_commande) AS annee, strftime('%m', c.date_commande) AS mois, SUM(l.montant) AS ca
  FROM commandes c JOIN lignes_commande l USING (id_commande) GROUP BY annee, mois),
cumul AS (SELECT *, SUM(ca) OVER (PARTITION BY annee ORDER BY mois) AS cumul FROM m)
SELECT annee, mois, ROUND(ca) AS ca, ROUND(cumul) AS cumul
FROM cumul WHERE mois IN ('06', '12') ORDER BY mois, annee
```
<!--sortie-->
```text
annee mois       ca     cumul
 2023   06  91604.0  490269.0
 2024   06 103445.0  522363.0
 2025   06 106930.0  562391.0
 2023   12 157052.0 1138932.0
 2024   12 157304.0 1189461.0
 2025   12 183845.0 1324764.0
```

> **Lecture.** Sur les six derniers mois de 2025, le chiffre d'affaires est **supérieur à celui de l'année précédente de 9,2 % à 18,5 %** selon le mois (+16,9 % en décembre). Le cumul à fin juin et à fin décembre de chaque année (le cumul de décembre est le total annuel : 1 138 932 €, 1 189 461 € puis 1 324 764 €) montre que le **second semestre pèse plus que le premier** (en 2025, 562 391 € à fin juin contre 762 373 € pour les six mois suivants), en raison de la saisonnalité. Comparer des mois à l'an dernier (et non au mois précédent) est la bonne façon de **neutraliser la saisonnalité**.
>
> **À vous.** Ajoutez une colonne « rang du mois dans l'année » avec `RANK()` et repérez le meilleur mois de chaque année.

### Application 3.7 — Fidélité et cohortes (sections 3.3 et 3.4)

**Objectif.** Une **cohorte** regroupe les clients selon l'année de leur **première commande** ; on suit ensuite combien de clients de chaque cohorte restent actifs. C'est l'outil de base de l'analyse de fidélité.

```sql
WITH premiere AS (SELECT id_client, MIN(date_commande) AS d1 FROM commandes GROUP BY id_client),
actif AS (SELECT DISTINCT id_client, strftime('%Y', date_commande) AS an FROM commandes)
SELECT strftime('%Y', p.d1) AS cohorte, COUNT(DISTINCT p.id_client) AS clients,
       SUM(a.an = '2023') AS actifs_2023, SUM(a.an = '2024') AS actifs_2024, SUM(a.an = '2025') AS actifs_2025
FROM premiere p JOIN actif a USING (id_client)
GROUP BY cohorte ORDER BY cohorte
```
<!--sortie-->
```text
cohorte  clients  actifs_2023  actifs_2024  actifs_2025
   2023     3112         3112         2527         2502
   2024      952            0          952          631
   2025      742            0            0          742
```

> **Lecture.** La cohorte « 2023 » (3 112 clients dont la première commande tombe en 2023) compte **2 527 clients actifs en 2024** et **2 502 en 2025** : environ **81 % et 80 %** de rétention, remarquablement stable d'une année à l'autre. La cohorte 2024 (952 clients) en garde 631 en 2025, soit **66 %**. Deux précautions : (1) la cohorte « 2023 » contient aussi les clients **déjà inscrits avant 2023**, dont la vraie première commande est antérieure à la base : on parle de **troncature à gauche**, et leur fidélité est probablement surestimée ; (2) la cohorte 2025 n'a pas encore pu être revue. Ces limites sont la règle en analyse de cohortes : **toujours se demander depuis quand on observe**.
>
> **À vous.** Exprimez les taux de rétention en pourcentage de la taille de la cohorte, et ajoutez le canal d'acquisition comme deuxième axe.

### Application 3.8 — Une segmentation RFM en SQL (sections 3.3 et 3.4)

**Objectif.** La segmentation **RFM** note chaque client sur la **R**écence (jours depuis la dernière commande), la **F**réquence (nombre de commandes) et le **M**ontant (chiffre d'affaires cumulé), puis regroupe les clients dans des segments parlants. Nous la calculons sur toute la période, au 31 décembre 2025.

**Étape 1 — Les trois mesures par client**, dans une CTE :

```sql
CREATE VIEW v_rfm AS
SELECT c.id_client,
       CAST(julianday('2025-12-31') - julianday(MAX(c.date_commande)) AS INTEGER) AS recence_jours,
       COUNT(DISTINCT c.id_commande) AS frequence,
       ROUND(SUM(l.montant), 2) AS montant
FROM commandes c JOIN lignes_commande l USING (id_commande)
GROUP BY c.id_client
```

**Étape 2 — Des segments définis par des seuils lisibles.** Les seuils (90 et 365 jours, 8 commandes) sont des **choix métier**, que l'on écrit en clair :

```sql
SELECT CASE WHEN recence_jours <= 90 AND frequence >= 8 THEN '1 champions'
            WHEN recence_jours <= 90 THEN '2 actifs'
            WHEN recence_jours <= 365 THEN '3 à relancer'
            ELSE '4 dormants' END AS segment,
       COUNT(*) AS clients, ROUND(AVG(frequence), 1) AS frequence_moy, ROUND(SUM(montant)) AS ca_total
FROM v_rfm GROUP BY segment ORDER BY segment
```
<!--sortie-->
```text
     segment  clients  frequence_moy  ca_total
 1 champions     1326           16.8 2240226.0
    2 actifs     1148            3.9  445610.0
3 à relancer     1407            5.3  751237.0
  4 dormants      925            2.3  216084.0
```


> **Lecture.** Les **1 326 « champions »** (28 % des clients) réalisent **2,24 millions d'euros**, soit **61 %** du chiffre d'affaires cumulé des trois ans ; les **925 « dormants »** (sans commande depuis plus d'un an) n'en représentent que 6 %. La **vérification** est ici très simple : les quatre segments totalisent **4 806 clients** (tous ceux de la vue) et **3 653 157 €**, c'est-à-dire exactement le chiffre d'affaires de la base : aucun client n'est perdu ni compté deux fois. Les seuils sont des choix : un autre découpage (par exemple des quantiles avec `NTILE`) donnerait de seuils d'autres segments : une segmentation est un **outil de décision**, pas une vérité.
>
> **À vous.** Remplacez les seuils par `NTILE(3)` sur chaque mesure, et observez pourquoi `NTILE` appliqué à la fréquence (très peu de valeurs distinctes) coupe des clients **identiques** dans des tranches différentes.

### Application 3.9 — Index et plan d'exécution (section 3.5)

**Objectif.** Voir un index changer un plan d'exécution, puis constater qu'il ne sert à rien quand on écrit mal sa condition.

```python
def plan(requete):
    return [ligne[3] for ligne in con.execute("EXPLAIN QUERY PLAN " + requete)]

q_ville = "SELECT COUNT(*) FROM clients WHERE ville = 'Ville C'"
print("avant :", plan(q_ville))
con.execute("CREATE INDEX idx_clients_ville ON clients(ville)")
print("après :", plan(q_ville))
print("avec une fonction :", plan("SELECT COUNT(*) FROM clients WHERE UPPER(ville) = 'VILLE C'"))
print("recherche en tête de motif :", plan("SELECT COUNT(*) FROM clients WHERE ville LIKE 'Ville C%'"))
```
<!--sortie-->
```text
avant : ['SCAN clients']
après : ['SEARCH clients USING COVERING INDEX idx_clients_ville (ville=?)']
avec une fonction : ['SCAN clients USING COVERING INDEX idx_clients_ville']
recherche en tête de motif : ['SCAN clients USING COVERING INDEX idx_clients_ville']
```

> **Lecture.** Avant l'index, la base lit toute la table `clients` (`SCAN`). Après, elle fait une **recherche par l'index** (`SEARCH … USING COVERING INDEX`). En revanche, appliquer `UPPER()` à la colonne indexée **empêche** l'index de servir : on retombe sur un balayage complet, même si l'index existe. Pour `LIKE 'Ville C%'`, SQLite ne fait pas non plus de recherche directe dans l'index : son `LIKE` ignore la casse alors que l'index la respecte, ce qui l'empêche de s'en servir pour une recherche par préfixe. **Lisez toujours le plan**, ne le supposez pas.
>
> **À vous.** Créez un index sur `commandes(canal, date_commande)` et comparez le plan de la requête « commandes du site en décembre 2025 » avant et après.

## Exercices

### Exercice 3.1 ⭐ — Les produits à forte marge (section 3.1.2)

Listez les produits de la catégorie « Maison » dont le **taux de marge** (marge divisée par le prix de vente) dépasse 55 %, triés par taux décroissant, avec leur prix, leur coût et leur taux arrondi à un chiffre après la virgule. Combien y en a-t-il ?

### Exercice 3.2 ⭐ — Une condition composée (section 3.1.3)

Combien de commandes du canal « Réseaux » ont utilisé le code `FIDELITE` en décembre 2025 ? Écrivez la condition de date **sans** `BETWEEN`.

### Exercice 3.3 ⭐⭐ — Les heures de pointe (section 3.1.5)

Classez les commandes en quatre tranches horaires (matin avant 12 h, midi de 12 h à 14 h, après-midi de 14 h à 18 h, soir à partir de 18 h) avec `CASE`, et comptez-les. Quelle tranche concentre le plus de commandes ? (L'heure est un texte `HH:MM` : `substr(heure, 1, 2)` donne les deux premiers caractères.)

### Exercice 3.4 ⭐⭐ — Pourquoi 0 ? (section 3.1.9)

Un collègue écrit, pour calculer la part des commandes avec un code promo, `SELECT SUM(CASE WHEN code_promo <> '' THEN 1 ELSE 0 END) / COUNT(*) FROM commandes` et obtient 0. Expliquez, corrigez, et donnez la part en pourcentage.

### Exercice 3.5 ⭐ — Le chiffre d'affaires par ville (section 3.2.2)

Calculez le chiffre d'affaires **2025** des cinq villes les plus rentables (il faut recoller `clients`, `commandes` et `lignes_commande`). Vérifiez que la somme des chiffres d'affaires de **toutes** les villes retombe sur le total de 2025.

### Exercice 3.6 ⭐⭐ — Les inscrits sans commande (section 3.2.3)

Combien de clients inscrits en **2024** n'ont **jamais** passé de commande ? Donnez la réponse par une anti-jointure, puis par `NOT EXISTS`, et vérifiez que les deux comptes coïncident.

### Exercice 3.7 ⭐⭐ — Un chiffre d'affaires trop beau (section 3.2.6)

Un stagiaire rapproche le chiffre d'affaires journalier de la table `jours_exploitation` des commandes : `SELECT SUM(j.chiffre_affaires) FROM jours_exploitation j JOIN commandes c ON c.date_commande = j.date`. Que calcule réellement sa requête ? Comparez-la au chiffre d'affaires réel (`SELECT SUM(chiffre_affaires) FROM jours_exploitation`), expliquez l'écart, puis corrigez la requête pour le rapprochement qu'il voulait faire : comparer, **jour par jour**, le chiffre d'affaires de `jours_exploitation` à celui recalculé depuis les lignes de commande. Quel est l'écart maximal ?

### Exercice 3.8 ⭐⭐⭐ — Les clients perdus, par canal d'acquisition (section 3.2.7)

Parmi les clients actifs en 2024, combien n'ont pas commandé en 2025, selon leur **canal d'acquisition** ? Exprimez ce nombre en pourcentage des clients actifs en 2024 de chaque canal d'acquisition. Quel canal fidélise le mieux ?

### Exercice 3.9 ⭐⭐ — Les trois meilleurs produits par catégorie (section 3.3.3)

Pour chaque catégorie, donnez les **trois produits au plus fort chiffre d'affaires en 2025** avec `RANK()`. Pourquoi peut-il y avoir plus de trois lignes pour une catégorie ? Que deviendrait le résultat avec `ROW_NUMBER()` ?

### Exercice 3.10 ⭐⭐ — Le délai de la deuxième commande (section 3.3.4)

Pour les clients qui ont passé au moins deux commandes, calculez le délai moyen **entre la première et la deuxième commande**, selon leur canal d'acquisition. Les clients acquis par la boutique recommandent-ils plus vite ?

### Exercice 3.11 ⭐⭐⭐ — La meilleure semaine (section 3.3.5)

Avec les données de `jours_exploitation`, calculez le **nombre de commandes sur sept jours glissants** et repérez les trois semaines glissantes les plus chargées. À quelle période de l'année correspondent-elles ?

### Exercice 3.12 ⭐⭐ — Un organigramme (section 3.4.5)

Soit une équipe de six personnes : la gérante (sans chef), deux responsables (boutique et site, dont le chef est la gérante), deux vendeuses (chef : responsable boutique) et un préparateur (chef : responsable site). Avec une CTE récursive, affichez pour chaque personne son **niveau** hiérarchique et son **chemin** complet, par exemple « Gérante > Responsable boutique > Vendeuse A ».

### Exercice 3.13 ⭐⭐ — Changer de dialecte (section 3.6)

Traduisez en SQL Server, puis en Oracle, la requête « les cinq produits les plus chers » et la requête « date de la commande + 7 jours » (la colonne `date_commande` est un `DATE`). Vérifiez ensuite la première dans DuckDB, qui est exécutable ici, en lisant le fichier `produits.csv`.

### Exercice 3.14 ⭐⭐⭐ — Sous-requête ou fenêtre ? (sections 3.5.1 et 3.5.2)

Pour chaque catégorie, listez le produit le plus cher avec une **sous-requête corrélée**, puis avec une **fonction fenêtre**. Vérifiez que les deux écritures donnent le même résultat, et comparez leurs plans d'exécution (`EXPLAIN QUERY PLAN`). Laquelle préférez-vous, et pourquoi ?

## Corrigés

### Corrigé 3.1

```sql
SELECT nom_produit, prix_vente, cout_achat,
       ROUND(100.0 * (prix_vente - cout_achat) / prix_vente, 1) AS taux_marge
FROM produits
WHERE categorie = 'Maison' AND 100.0 * (prix_vente - cout_achat) / prix_vente > 55
ORDER BY taux_marge DESC
```
<!--sortie-->
```text
    nom_produit  prix_vente  cout_achat  taux_marge
  Rideau design        31.9       12.84        59.7
 Boîte rustique        50.9       21.14        58.5
   Lampe design       126.9       53.39        57.9
    Coussin mat        50.9       21.55        57.7
Étagère compact        33.9       15.21        55.1
```

Cinq produits de la maison dépassent 55 % de marge. Comme SQLite tolère l'alias dans le `WHERE`, on aurait pu écrire `taux_marge > 55`, mais c'est **non portable** (section 3.1.7) : on répète l'expression. La division par `100.0` (et non `100`) n'est pas nécessaire ici, car `prix_vente` est décimal ; c'est un réflexe de prudence.

### Corrigé 3.2

```sql
SELECT COUNT(*) AS commandes
FROM commandes
WHERE canal = 'Réseaux' AND code_promo = 'FIDELITE'
  AND date_commande >= '2025-12-01' AND date_commande < '2026-01-01'
```
<!--sortie-->
```text
 commandes
        13
```

Treize commandes. La borne supérieure **stricte** (`< '2026-01-01'`) vaut mieux qu'un `BETWEEN … AND '2025-12-31'` : elle reste correcte si la colonne contient un jour une heure (piège 3 de la section 3.1.9).

### Corrigé 3.3

```sql
SELECT CASE WHEN CAST(substr(heure, 1, 2) AS INTEGER) < 12 THEN '1 matin'
            WHEN CAST(substr(heure, 1, 2) AS INTEGER) < 14 THEN '2 midi'
            WHEN CAST(substr(heure, 1, 2) AS INTEGER) < 18 THEN '3 après-midi'
            ELSE '4 soir' END AS tranche, COUNT(*) AS nb
FROM commandes GROUP BY tranche ORDER BY tranche
```
<!--sortie-->
```text
     tranche    nb
     1 matin  3830
      2 midi  5819
3 après-midi 17012
      4 soir  9734
```

L'**après-midi** concentre le plus de commandes (17 012 sur 36 395, soit 47 %), devant le soir (9 734) ; le matin est la tranche la plus creuse (3 830). On a numéroté les tranches (« 1 matin », « 2 midi »…) pour que l'`ORDER BY` alphabétique donne l'ordre de la journée. Attention : les tranches n'ont pas la même durée (quatre heures d'après-midi, deux heures de midi), la comparaison brute surévalue donc les tranches longues.

### Corrigé 3.4

La somme `SUM(CASE … THEN 1 ELSE 0 END)` est un **entier**, `COUNT(*)` aussi : SQLite fait une **division entière** (5 743 / 36 395 = 0,157…, tronqué à 0). La correction force la division décimale :

```sql
SELECT ROUND(100.0 * SUM(CASE WHEN code_promo <> '' THEN 1 ELSE 0 END) / COUNT(*), 1) AS part_avec_code_pct
FROM commandes
```
<!--sortie-->
```text
 part_avec_code_pct
               15.8
```

La part des commandes avec un code promo est de **15,8 %**. Remarquez que ce chiffre est le même que celui des **lignes** remisées vu en 3.1.9 : c'est normal, la remise s'applique à toute la commande.

### Corrigé 3.5

```sql
WITH ca AS (
  SELECT cl.ville, SUM(l.montant) AS ca
  FROM clients cl JOIN commandes c USING (id_client) JOIN lignes_commande l USING (id_commande)
  WHERE c.date_commande >= '2025-01-01' GROUP BY cl.ville)
SELECT ville, ROUND(ca) AS ca_2025, (SELECT ROUND(SUM(ca)) FROM ca) AS total_toutes_villes
FROM ca ORDER BY ca DESC LIMIT 5
```
<!--sortie-->
```text
  ville  ca_2025  total_toutes_villes
Ville A 184324.0            1324764.0
Ville B 164880.0            1324764.0
Ville C 121696.0            1324764.0
Ville D 116870.0            1324764.0
Ville E 102757.0            1324764.0
```

Les cinq villes sont A, B, C, D et E (184 324 €, 164 880 €, 121 696 €, 116 870 € et 102 757 €), et le total de toutes les villes est de **1 324 764 €**, c'est-à-dire exactement le chiffre d'affaires 2025 des autres sections : la jointure n'a ni perdu ni dupliqué de lignes.

### Corrigé 3.6

```sql
SELECT COUNT(*) AS par_anti_jointure
FROM clients c LEFT JOIN commandes o ON o.id_client = c.id_client
WHERE strftime('%Y', c.date_inscription) = '2024' AND o.id_commande IS NULL;

SELECT COUNT(*) AS par_not_exists
FROM clients c
WHERE strftime('%Y', c.date_inscription) = '2024'
  AND NOT EXISTS (SELECT 1 FROM commandes o WHERE o.id_client = c.id_client)
```
<!--sortie-->
```text
 par_anti_jointure
               154

 par_not_exists
            154
```

Les deux requêtes renvoient **154 clients** : sur les **666 clients inscrits en 2024**, 154 (23 %, près d'un sur quatre) n'ont jamais commandé. Ici le filtre sur l'inscription porte sur la table **de gauche**, il peut donc rester dans le `WHERE` sans piège (c'est un filtre sur les lignes finales, pas sur les correspondances).

### Corrigé 3.7

La requête du stagiaire **joint** `jours_exploitation` (un jour = une ligne) à `commandes` (plusieurs lignes par jour) : le chiffre d'affaires de chaque jour est recopié autant de fois que le jour compte de commandes. Pour comparer :

```sql
SELECT (SELECT ROUND(SUM(chiffre_affaires)) FROM jours_exploitation) AS ca_reel,
       (SELECT ROUND(SUM(j.chiffre_affaires)) FROM jours_exploitation j JOIN commandes c ON c.date_commande = j.date) AS ca_apres_jointure
```
<!--sortie-->
```text
  ca_reel  ca_apres_jointure
3653157.0        138730005.0
```

Le chiffre d'affaires réel est de 3 653 157 € ; la jointure en annonce **138 730 005 €**, soit **38 fois** trop, puisque chaque jour compte plus de trente commandes en moyenne. Pour rapprocher correctement les deux sources, on **agrège avant de joindre**, au grain du jour :

```sql
WITH calcule AS (
  SELECT c.date_commande AS jour, SUM(l.montant) AS ca_lignes
  FROM commandes c JOIN lignes_commande l USING (id_commande) GROUP BY c.date_commande)
SELECT COUNT(*) AS jours, ROUND(MAX(ABS(j.chiffre_affaires - calcule.ca_lignes)), 2) AS ecart_max
FROM jours_exploitation j JOIN calcule ON calcule.jour = j.date
```
<!--sortie-->
```text
 jours  ecart_max
  1096        0.0
```

L'écart maximal est **nul** (0,0 €) sur les 1 096 jours : la table de synthèse `jours_exploitation` est parfaitement cohérente avec le détail des lignes. C'est exactement le contrôle de réconciliation que l'on fait entre un tableau de bord et ses sources.

### Corrigé 3.8

```sql
WITH actifs24 AS (SELECT DISTINCT id_client FROM commandes WHERE date_commande >= '2024-01-01' AND date_commande < '2025-01-01'),
perdus AS (SELECT id_client FROM actifs24 EXCEPT SELECT id_client FROM commandes WHERE date_commande >= '2025-01-01')
SELECT cl.canal_acquisition, COUNT(*) AS actifs_2024,
       SUM(p.id_client IS NOT NULL) AS perdus,
       ROUND(100.0 * SUM(p.id_client IS NOT NULL) / COUNT(*), 1) AS taux_perte_pct
FROM actifs24 a JOIN clients cl USING (id_client) LEFT JOIN perdus p USING (id_client)
GROUP BY cl.canal_acquisition ORDER BY taux_perte_pct
```
<!--sortie-->
```text
canal_acquisition  actifs_2024  perdus  taux_perte_pct
          Réseaux          412      66            16.0
         Boutique         1720     328            19.1
             Site         1347     257            19.1
```

Les clients acquis par les **réseaux** sont les mieux fidélisés : **16,0 %** d'entre eux (66 sur 412) n'ont pas recommandé en 2025, contre **19,1 %** pour la boutique (328 sur 1 720) et pour le site (257 sur 1 347). L'écart est de trois points ; or, sur 412 clients, l'incertitude statistique d'un taux d'environ 17 % est de l'ordre de **± 3,6 points** (à 95 %) : la différence n'est donc **pas démontrée**. Une conclusion prudente : le canal d'acquisition ne prédit guère la fidélité (les tests statistiques du volume III de cette série donnent le moyen de trancher). Remarquez l'astuce `SUM(p.id_client IS NOT NULL)` : après une jointure à gauche, un `id_client` non nul signifie « client perdu ».

### Corrigé 3.9

```sql
WITH ca AS (
  SELECT p.categorie, p.nom_produit, SUM(l.montant) AS ca
  FROM lignes_commande l JOIN commandes c USING (id_commande) JOIN produits p USING (id_produit)
  WHERE c.date_commande >= '2025-01-01' GROUP BY p.id_produit),
r AS (SELECT *, RANK() OVER (PARTITION BY categorie ORDER BY ca DESC) AS rang FROM ca)
SELECT categorie, nom_produit, ROUND(ca) AS ca, rang FROM r WHERE rang <= 3 ORDER BY categorie, rang
```
<!--sortie-->
```text
 categorie        nom_produit      ca  rang
 Bien-être    Tisane nordique 12433.0     1
 Bien-être     Encens compact 11279.0     2
 Bien-être    Peignoir design 10527.0     3
   Cuisine Casserole nordique 25842.0     1
   Cuisine         Bol design 21628.0     2
   Cuisine   Théière rustique 20885.0     3
Décoration Statuette rustique 31316.0     1
Décoration  Bougeoir rustique 24527.0     2
Décoration           Vase mat 20436.0     3
    Jardin   Transat nordique 66012.0     1
    Jardin       Lanterne mat 47447.0     2
    Jardin            Pot mat 46421.0     3
    Maison         Panier mat 43955.0     1
    Maison        Coussin mat 29856.0     2
    Maison       Lampe design 28665.0     3
 Papeterie  Classeur rustique  7274.0     1
 Papeterie  Calendrier design  5968.0     2
 Papeterie    Cahier nordique  5595.0     3
```

Le résultat compte autant de lignes que de produits classés dans les trois premiers rangs : **plus de trois** si deux produits ont **exactement** le même chiffre d'affaires (c'est le propre de `RANK`, qui garde les ex æquo). Ici, les chiffres d'affaires en euros sont des nombres décimaux quasi uniques et l'on obtient **trois lignes par catégorie**, soit 18 au total (la situation de la section 3.3.3, où des ex æquo apparaissaient pour des **quantités entières**, ne se reproduit pas). Avec `ROW_NUMBER()`, on aurait **toujours** trois lignes par catégorie, en départageant arbitrairement les ex æquo éventuels : bon pour « exactement trois », mauvais pour « tous les gagnants ». Les classements en euros et en quantités ne coïncident pas toujours : le meilleur produit en quantités n'est pas forcément celui qui rapporte le plus (un article cher se vend moins).

### Corrigé 3.10

```sql
WITH rang AS (
  SELECT cl.canal_acquisition, c.id_client, c.date_commande,
         ROW_NUMBER() OVER (PARTITION BY c.id_client ORDER BY c.date_commande, c.id_commande) AS n
  FROM commandes c JOIN clients cl USING (id_client)),
paire AS (
  SELECT a.canal_acquisition, julianday(b.date_commande) - julianday(a.date_commande) AS delai
  FROM rang a JOIN rang b ON a.id_client = b.id_client AND a.n = 1 AND b.n = 2)
SELECT canal_acquisition, COUNT(*) AS clients, ROUND(AVG(delai), 1) AS delai_moyen_jours
FROM paire GROUP BY canal_acquisition
```
<!--sortie-->
```text
canal_acquisition  clients  delai_moyen_jours
         Boutique     1958              146.2
          Réseaux      460              145.6
             Site     1555              151.1
```

Les clients acquis par la boutique recommandent après **146 jours** en moyenne, ceux des réseaux après 146 jours, ceux du site après **151 jours** : l'écart est faible (cinq jours sur près de cinq mois). On a numéroté les commandes de chaque client par `ROW_NUMBER`, puis **auto-joint** le rang 1 au rang 2. Ce délai est calculé uniquement sur les clients qui ont **recommandé** (3 973 clients sur 4 806) : les autres, qui n'ont pas recommandé, sont exclus (**biais de survie** : le vrai délai moyen est plus long).

### Corrigé 3.11

```sql
WITH j AS (
  SELECT date, SUM(nb_commandes) OVER (ORDER BY date ROWS BETWEEN 6 PRECEDING AND CURRENT ROW) AS sur_7_jours,
         ROW_NUMBER() OVER (ORDER BY date) AS rn
  FROM jours_exploitation)
SELECT date AS fin_de_la_fenetre, sur_7_jours FROM j WHERE rn >= 7 ORDER BY sur_7_jours DESC LIMIT 3
```
<!--sortie-->
```text
fin_de_la_fenetre  sur_7_jours
       2025-12-04          451
       2025-12-02          450
       2025-12-26          446
```

Les trois fenêtres de sept jours les plus chargées se terminent **les 4 et 2 décembre et le 26 décembre 2025** (451, 450 et 446 commandes) : toutes en **décembre**, au pic des fêtes de fin d'année et des promotions. Le filtre `rn >= 7` écarte les six premiers jours, pour lesquels la fenêtre est incomplète (piège de la section 3.3.5).

### Corrigé 3.12

```sql
WITH RECURSIVE equipe(id, nom, chef) AS (VALUES
       (1, 'Gérante', NULL), (2, 'Responsable boutique', 1), (3, 'Vendeuse A', 2),
       (4, 'Vendeuse B', 2), (5, 'Responsable site', 1), (6, 'Préparateur', 5)),
chaine(id, nom, niveau, chemin) AS (
  SELECT id, nom, 0, nom FROM equipe WHERE chef IS NULL
  UNION ALL
  SELECT e.id, e.nom, c.niveau + 1, c.chemin || ' > ' || e.nom FROM equipe e JOIN chaine c ON e.chef = c.id)
SELECT niveau, chemin FROM chaine ORDER BY chemin
```
<!--sortie-->
```text
 niveau                                      chemin
      0                                     Gérante
      1              Gérante > Responsable boutique
      2 Gérante > Responsable boutique > Vendeuse A
      2 Gérante > Responsable boutique > Vendeuse B
      1                  Gérante > Responsable site
      2    Gérante > Responsable site > Préparateur
```

La partie initiale sélectionne la racine (la gérante, au niveau 0) ; la partie récursive ajoute à chaque tour les personnes dont le chef vient d'être trouvé, en augmentant le niveau et en prolongeant le chemin par une concaténation (`||`). On trie par `chemin` pour obtenir l'ordre de lecture de l'organigramme. La récursion s'arrête d'elle-même, quand plus personne n'a pour chef une personne déjà trouvée.

### Corrigé 3.13

```sql
-- SQL Server — non exécuté
SELECT TOP 5 nom_produit, prix_vente FROM produits ORDER BY prix_vente DESC;
SELECT DATEADD(day, 7, date_commande) AS date_plus_7 FROM commandes;

-- Oracle — non exécuté
SELECT nom_produit, prix_vente FROM produits ORDER BY prix_vente DESC FETCH FIRST 5 ROWS ONLY;
SELECT date_commande + 7 AS date_plus_7 FROM commandes;
```

Et la vérification de la première dans DuckDB, depuis le fichier d'origine :

```python
import duckdb
res = duckdb.sql(f"SELECT nom_produit, prix_vente FROM read_csv('{os.environ['DONNEES']}/produits.csv') ORDER BY prix_vente DESC LIMIT 5").df()
print(res.to_string(index=False))
```
<!--sortie-->
```text
     nom_produit  prix_vente
Transat nordique       152.9
    Lampe design       126.9
    Lanterne mat       117.9
 Étagère compact       105.9
      Panier mat       104.9
```

DuckDB renvoie les mêmes cinq produits que la requête SQLite de la section 3.1.4 (le transat à 152,90 € en tête). Les écritures SQL Server et Oracle sont données **de mémoire** : à vérifier dans la documentation de votre version.

### Corrigé 3.14

```sql
SELECT p.categorie, p.nom_produit, p.prix_vente FROM produits p
WHERE p.prix_vente = (SELECT MAX(q.prix_vente) FROM produits q WHERE q.categorie = p.categorie)
ORDER BY p.categorie;

SELECT categorie, nom_produit, prix_vente FROM (
  SELECT categorie, nom_produit, prix_vente, RANK() OVER (PARTITION BY categorie ORDER BY prix_vente DESC) AS rang
  FROM produits) WHERE rang = 1 ORDER BY categorie
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

 categorie        nom_produit  prix_vente
 Bien-être    Tisane nordique        68.9
   Cuisine Casserole nordique        57.9
Décoration   Horloge nordique        96.9
    Jardin   Transat nordique       152.9
    Maison       Lampe design       126.9
 Papeterie        Trousse mat        21.9
```

Les deux requêtes renvoient les mêmes six lignes (on peut le vérifier en les comparant avec `EXCEPT` dans les deux sens : aucun écart). Voici les plans :

```python
corr = "SELECT p.categorie FROM produits p WHERE p.prix_vente = (SELECT MAX(q.prix_vente) FROM produits q WHERE q.categorie = p.categorie)"
fen = "SELECT categorie FROM (SELECT categorie, RANK() OVER (PARTITION BY categorie ORDER BY prix_vente DESC) AS rang FROM produits) WHERE rang = 1"
for nom, q in (("corrélée", corr), ("fenêtre", fen)):
    print(nom, plan(q))
```
<!--sortie-->
```text
corrélée ['SCAN p', 'CORRELATED SCALAR SUBQUERY 1', 'SEARCH q']
fenêtre ['CO-ROUTINE (subquery-1)', 'CO-ROUTINE (subquery-3)', 'SCAN produits', 'USE TEMP B-TREE FOR ORDER BY', 'SCAN (subquery-3)', 'SCAN (subquery-1)']
```

La version corrélée **relit** la table `produits` pour chaque produit (on voit une sous-requête `CORRELATED SCALAR SUBQUERY` dans le plan) ; la version fenêtre fait **un seul passage** avec un tri. Sur 120 produits la différence est invisible ; sur des millions de lignes, elle est considérable. Je préfère la fenêtre : elle est plus **lisible** (la logique « classer dans la catégorie, garder le rang 1 » se lit), plus **rapide** à grande échelle, et plus **souple** (garder les trois premiers, comparer à la médiane, etc.).

