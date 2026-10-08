## 1.4 ➕ Pour aller plus loin : modélisation dimensionnelle

> 🧭 Section optionnelle. Elle répond à une question que le parcours essentiel laisse ouverte : **que devient une dimension quand ses attributs changent ?** Elle présente ensuite la matrice des processus et les data marts, qui organisent un entrepôt quand il grandit.

```python hide
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as O

D = os.environ["DONNEES"]
con.executescript(f"CREATE TABLE src.hist_clients AS SELECT * FROM read_csv_auto('{D}/ch01-historique-clients.csv')")
con.executescript(f"CREATE TABLE src.hist_produits AS SELECT * FROM read_csv_auto('{D}/ch01-historique-produits.csv')")
```

### 1.4.1 Quand les attributs changent

Un client déménage. Un produit change de catégorie. Un fournisseur est racheté. La dimension, elle, a une ligne par client, par produit, par fournisseur : **que faire de l'ancienne valeur ?** La question n'est pas technique : elle décide de ce que dira l'histoire.

Un client de la boutique, qui a changé de ville en cours de période, tel que le décrit l'historique **simulé** de ce chapitre (10 % des clients déménagent, et 8 produits sont reclassés au 1er juillet 2024) :

```sql
SELECT id_client, ville, date_debut, date_fin, courant FROM src.hist_clients
WHERE id_client = (SELECT MIN(id_client) FROM src.hist_clients WHERE courant = 0)
ORDER BY date_debut;
```
<!--sortie-->
```text
 id_client   ville date_debut   date_fin  courant
         5 Ville G 2018-01-03 2024-05-04        0
         5 Ville N 2024-05-05 9999-12-31        1
```

Ce client a acheté dans les deux villes. Si nous ne gardons que la ville **actuelle**, ses achats d'avant le déménagement seront attribués à sa nouvelle ville : le chiffre d'affaires de la Ville A **n'aura pas été fait par des clients de la Ville A** quand il l'a été. Voilà un chiffre faux **sans qu'aucune donnée soit fausse**.

### 1.4.2 Trois traitements classiques

On appelle ces choix des **dimensions à évolution lente** (*slowly changing dimensions*, SCD). Trois sont les plus courants.

- **Type 1 : écraser.** On remplace l'ancienne valeur par la nouvelle. Simple, sans historique : l'ancienne ville est perdue. Convient aux **corrections** (une faute de frappe dans un nom) et aux attributs dont l'histoire n'importe pas.
- **Type 2 : ajouter une ligne.** On **conserve** l'ancienne ligne, qu'on **ferme** (date de fin), et l'on **ajoute** une nouvelle ligne, avec sa propre clé de substitution et sa période de validité. Chaque fait pointe vers la **version valide au moment où il s'est produit**. C'est le traitement qui préserve l'histoire.
- **Type 3 : ajouter une colonne.** On garde l'ancienne valeur dans une colonne à côté (`categorie`, `categorie_precedente`). L'historique est limité à **un** changement, mais les requêtes restent simples : utile pour comparer « avant » et « après » un seul reclassement.

| | Type 1 | Type 2 | Type 3 |
|---|---|---|---|
| **Ancienne valeur** | perdue | conservée (ligne fermée) | conservée (une colonne) |
| **Combien de changements** | — | autant que l'on veut | un seul |
| **Taille de la dimension** | constante | **croît** | constante |
| **Les faits anciens voient…** | la valeur actuelle | la valeur **de leur époque** | la valeur actuelle (ou la précédente) |
| **À choisir pour** | corrections | **analyse historique** | comparaison avant/après d'un reclassement |

Il existe d'autres types (le type 0 ne change jamais ; le type 6 combine 1, 2 et 3). Le point à retenir est que **le choix se fait attribut par attribut, avec les utilisateurs**, en leur posant la question : « Quand ce client déménage, ses achats d'hier doivent-ils rester dans son ancienne ville ? » La réponse est une règle de gestion, pas une préférence technique.

Le type 3 pour nos huit produits reclassés :

```sql
SELECT id_produit, MAX(categorie) FILTER (WHERE courant = 1) AS categorie,
       MAX(categorie) FILTER (WHERE courant = 0) AS categorie_precedente
FROM src.hist_produits GROUP BY 1 HAVING COUNT(*) > 1 ORDER BY 1 LIMIT 4;
```
<!--sortie-->
```text
 id_produit categorie categorie_precedente
          3   Cuisine               Maison
          5   Cuisine               Jardin
         11   Cuisine           Décoration
         27    Maison               Jardin
```

### 1.4.3 Le type 2 en SQL

Une dimension de type 2 a **une ligne par version**. La clé de substitution identifie la version (et non plus le client) ; la clé naturelle `id_client` est répétée ; deux dates donnent la période de validité.

```sql
CREATE TABLE dwh.dim_client_hist AS
SELECT row_number() OVER (ORDER BY id_client, date_debut) AS client_hist_key, id_client, ville,
       CAST(date_debut AS DATE) AS valide_du, CAST(date_fin AS DATE) AS valide_au,
       courant = 1 AS est_courant
FROM src.hist_clients;
```

La **date de fin des versions courantes** est fixée à une date lointaine (31 décembre 9999) plutôt qu'à une valeur vide : les comparaisons de période (`BETWEEN`) fonctionnent alors sans traitement particulier. Le plus important est de **rattacher chaque fait à la bonne version**. Au chargement, on joint le fait à la version dont la période **contient la date de la vente** :

```sql
CREATE TABLE dwh.fait_ventes_hist AS
SELECT v.id_ligne, v.date_key, v.montant_ttc, h.client_hist_key
FROM dwh.fait_ventes v
JOIN dwh.dim_client c USING (client_key)
JOIN dwh.dim_date d USING (date_key)
JOIN dwh.dim_client_hist h
  ON h.id_client = c.id_client AND d.date BETWEEN h.valide_du AND h.valide_au;
```

Une jointure sur une **période** est dangereuse : si deux versions se **chevauchent**, la vente est comptée **deux fois** ; s'il y a un **trou**, elle **disparaît**. Les deux se contrôlent :

```sql
SELECT (SELECT COUNT(*) FROM dwh.dim_client_hist a JOIN dwh.dim_client_hist b
        ON a.id_client = b.id_client AND a.valide_du < b.valide_du AND a.valide_au >= b.valide_du) AS chevauchements,
       (SELECT COUNT(*) FROM dwh.dim_client_hist a JOIN dwh.dim_client_hist b
        ON a.id_client = b.id_client AND NOT a.est_courant AND b.est_courant
        AND b.valide_du <> a.valide_au + 1) AS trous,
       (SELECT COUNT(*) FROM dwh.fait_ventes) - (SELECT COUNT(*) FROM dwh.fait_ventes_hist) AS lignes_ecart,
       (SELECT ROUND(SUM(montant_ttc) - (SELECT SUM(montant_ttc) FROM dwh.fait_ventes_hist), 2) FROM dwh.fait_ventes) AS ca_ecart;
```
<!--sortie-->
```text
 chevauchements  trous  lignes_ecart  ca_ecart
              0      0             0       0.0
```

Aucun chevauchement, aucun trou, **mêmes lignes et même chiffre d'affaires** : la table historisée ne perd ni ne duplique rien. Reste à voir **ce que cela change**. Pour 2024, le chiffre d'affaires par ville selon la ville **actuelle** (type 1) et selon la ville **à la date de l'achat** (type 2), pour les villes où l'écart est le plus grand :

```sql
WITH t1 AS (SELECT c.ville, SUM(v.montant_ttc) AS ca FROM dwh.fait_ventes v
            JOIN dwh.dim_client c USING (client_key) JOIN dwh.dim_date d USING (date_key)
            WHERE d.annee = 2024 GROUP BY 1),
     t2 AS (SELECT h.ville, SUM(v.montant_ttc) AS ca FROM dwh.fait_ventes_hist v
            JOIN dwh.dim_client_hist h USING (client_hist_key) JOIN dwh.dim_date d USING (date_key)
            WHERE d.annee = 2024 GROUP BY 1)
SELECT ville, ROUND(t1.ca) AS type1, ROUND(t2.ca) AS type2, ROUND(100 * (t1.ca / t2.ca - 1), 1) AS ecart_pct
FROM t1 JOIN t2 USING (ville) ORDER BY ABS(t1.ca - t2.ca) DESC LIMIT 5;
```
<!--sortie-->
```text
  ville    type1    type2  ecart_pct
Ville A 160981.0 152103.0        5.8
Ville K  38162.0  42106.0       -9.4
Ville F  76959.0  79282.0       -2.9
Ville C 119335.0 121602.0       -1.9
Ville H  69830.0  71607.0       -2.5
```

![Un client qui déménage : en type 1 (haut), toute son histoire est attribuée à sa ville actuelle ; en type 2 (bas), chaque achat rejoint la version valide ce jour-là.](figures/ch01-scd2.png)

```python hide
O.fig_scd2()
```
<!--sortie-->
```text
figure : ch01-scd2.png
```

Les écarts vont de 2 à 9 %. La Ville A, la plus peuplée, a reçu des clients qui y ont déménagé : le type 1 lui attribue **5,8 %** de chiffre d'affaires de trop en 2024. La petite Ville K en a perdu : le type 1 lui en attribue **9,4 %** de moins que ce qu'elle a réellement fait. Le total, lui, est **identique** : seule la **répartition** change. C'est la nature de l'erreur : une série par ville qui a l'air bonne, un total correct, et une analyse géographique **faussée**.

```python hide
t = con.df("""WITH t1 AS (SELECT c.ville, SUM(v.montant_ttc) AS type1 FROM dwh.fait_ventes v JOIN dwh.dim_client c USING (client_key) JOIN dwh.dim_date d USING (date_key) WHERE d.annee = 2024 GROUP BY 1),
                   t2 AS (SELECT h.ville, SUM(v.montant_ttc) AS type2 FROM dwh.fait_ventes_hist v JOIN dwh.dim_client_hist h USING (client_hist_key) JOIN dwh.dim_date d USING (date_key) WHERE d.annee = 2024 GROUP BY 1)
              SELECT * FROM t1 JOIN t2 USING (ville)""").set_index("ville")
fa = t.loc["Ville A"]
assert round(100 * (fa["type1"] / fa["type2"] - 1), 1) == 5.8 and abs(t["type1"].sum() - t["type2"].sum()) < 1e-6
O.fig_scd_effet(t.reindex((t["type1"] - t["type2"]).abs().sort_values(ascending=False).index[:8]))
```
<!--sortie-->
```text
figure : ch01-scd-effet.png
```

![Chiffre d'affaires 2024 par ville, selon que l'on garde la ville actuelle de chaque client (type 1) ou sa ville au moment de l'achat (type 2), pour les huit villes où l'écart est le plus grand.](figures/ch01-scd-effet.png)

Le même mécanisme vaut pour les **produits**. Les huit reclassements du 1er juillet 2024 changent le chiffre d'affaires **par catégorie** du premier semestre 2024 : avec la catégorie actuelle (type 1), des ventes sont attribuées à des catégories où elles ne se faisaient pas encore.

```sql
CREATE TABLE dwh.dim_produit_hist AS
SELECT row_number() OVER (ORDER BY id_produit, date_debut) AS produit_hist_key, id_produit, categorie,
       CAST(date_debut AS DATE) AS valide_du, CAST(date_fin AS DATE) AS valide_au
FROM src.hist_produits;
```

```sql
WITH t1 AS (SELECT p.categorie, SUM(v.montant_ht) AS ca FROM dwh.fait_ventes v
            JOIN dwh.dim_produit p USING (produit_key) JOIN dwh.dim_date d USING (date_key)
            WHERE d.date BETWEEN '2024-01-01' AND '2024-06-30' GROUP BY 1),
     t2 AS (SELECT h.categorie, SUM(v.montant_ht) AS ca FROM dwh.fait_ventes v
            JOIN dwh.dim_produit p USING (produit_key) JOIN dwh.dim_date d USING (date_key)
            JOIN dwh.dim_produit_hist h ON h.id_produit = p.id_produit AND d.date BETWEEN h.valide_du AND h.valide_au
            WHERE d.date BETWEEN '2024-01-01' AND '2024-06-30' GROUP BY 1)
SELECT categorie, ROUND(t1.ca) AS type1, ROUND(t2.ca) AS type2, ROUND(100 * (t1.ca / t2.ca - 1), 1) AS ecart_pct
FROM t1 JOIN t2 USING (categorie) ORDER BY categorie;
```
<!--sortie-->
```text
 categorie    type1    type2  ecart_pct
 Bien-être  42306.0  43410.0       -2.5
   Cuisine  84027.0  63874.0       31.6
Décoration  82928.0  86271.0       -3.9
    Jardin 104218.0 125416.0      -16.9
    Maison 102136.0  97760.0        4.5
 Papeterie  19687.0  18572.0        6.0
```

Sur le premier semestre 2024, avec la catégorie actuelle, la cuisine paraît **32 % plus grande** qu'elle ne l'était et le jardin **17 % plus petit** : trois des huit produits reclassés sont passés à la cuisine (un venait de la maison, un du jardin, un de la décoration). Un reclassement ne change pas le chiffre d'affaires de la boutique, mais il **déplace** de l'argent d'une catégorie à l'autre : une personne qui lit « la décoration a baissé » doit savoir si c'est un fait commercial ou **un changement de rangement**. On l'écrit dans la documentation de la dimension.

### 1.4.4 Charger une dimension de type 2

Au chargement, on reçoit chaque jour un **instantané** de la source (« voici les produits tels qu'ils sont aujourd'hui »). Il faut le comparer à la dimension, **fermer** les versions qui ont changé et **ajouter** les nouvelles. Un petit exemple, sur trois produits existants et un produit nouveau, tient en deux instructions :

```sql hide
CREATE TABLE dwh.demo_dim AS
SELECT id_produit, categorie, DATE '2023-01-01' AS valide_du, DATE '9999-12-31' AS valide_au
FROM src.produits WHERE id_produit IN (1, 2, 3);
CREATE TABLE dwh.demo_arrivee AS
SELECT 1 AS id_produit, 'Cuisine' AS categorie UNION ALL SELECT 2, 'Jardin'
UNION ALL SELECT 3, 'Cuisine' UNION ALL SELECT 121, 'Maison';
```

Première instruction : **fermer** les versions courantes dont l'attribut a changé (ici le produit 2, passé de la cuisine au jardin) ; seconde : **insérer** une version courante pour tout produit qui n'en a plus (le produit fermé, et le produit 121, nouveau).

```sql
UPDATE dwh.demo_dim d SET valide_au = DATE '2025-06-30'
FROM dwh.demo_arrivee a
WHERE a.id_produit = d.id_produit AND d.valide_au = DATE '9999-12-31' AND a.categorie <> d.categorie;

INSERT INTO dwh.demo_dim
SELECT a.id_produit, a.categorie, DATE '2025-07-01', DATE '9999-12-31'
FROM dwh.demo_arrivee a
LEFT JOIN dwh.demo_dim d ON d.id_produit = a.id_produit AND d.valide_au = DATE '9999-12-31'
WHERE d.id_produit IS NULL;

SELECT * FROM dwh.demo_dim ORDER BY id_produit, valide_du;
```
<!--sortie-->
```text
 id_produit categorie  valide_du  valide_au
          1   Cuisine 2023-01-01 9999-12-31
          2   Cuisine 2023-01-01 2025-06-30
          2    Jardin 2025-07-01 9999-12-31
          3   Cuisine 2023-01-01 9999-12-31
        121    Maison 2025-07-01 9999-12-31
```

Le produit 2 a maintenant deux lignes (l'ancienne fermée au 30 juin, la nouvelle ouverte au 1er juillet), le produit 121 une, et les produits 1 et 3, **inchangés, n'ont pas bougé**. Cet algorithme a une propriété précieuse : on peut le **relancer sans danger**. Si le chargement est interrompu puis rejoué, la seconde passe ne trouve **rien à fermer et rien à ajouter**. On appelle cela l'**idempotence** : c'est la qualité centrale d'un chargement fiable, que le chapitre 2 développe.

```python hide
n1 = con.df("SELECT COUNT(*) AS n FROM dwh.demo_dim")["n"][0]
con.executescript("""UPDATE dwh.demo_dim d SET valide_au = DATE '2025-06-30' FROM dwh.demo_arrivee a WHERE a.id_produit = d.id_produit AND d.valide_au = DATE '9999-12-31' AND a.categorie <> d.categorie;
INSERT INTO dwh.demo_dim SELECT a.id_produit, a.categorie, DATE '2025-07-01', DATE '9999-12-31' FROM dwh.demo_arrivee a LEFT JOIN dwh.demo_dim d ON d.id_produit = a.id_produit AND d.valide_au = DATE '9999-12-31' WHERE d.id_produit IS NULL""")
assert n1 == 5 and con.df("SELECT COUNT(*) AS n FROM dwh.demo_dim")["n"][0] == 5
```

> ⚠️ **Piège : historiser ce qui change tout le temps.** Un attribut qui change souvent (le « nombre d'achats du client », un score recalculé chaque jour) donnerait, en type 2, **une nouvelle ligne par client et par jour** : pour nos 6 000 clients, plus de deux millions de lignes par an, pour une dimension qui devrait en compter 6 000. Ces valeurs **n'appartiennent pas à une dimension** : on les range dans un **fait** (un instantané périodique) ou dans une **mini-dimension** de quelques tranches (« 0-2 achats », « 3-9 », « 10 et plus »). On ne fait du type 2 que sur des attributs qui changent **rarement** et dont l'historique **sert** à des analyses.

### 1.4.5 Matrice des processus et data marts

Quand l'entrepôt compte plusieurs tables de faits, il faut un **plan d'ensemble**. La **matrice des processus** (*bus matrix*) croise, en lignes, les **processus** que l'on mesure et, en colonnes, les **dimensions** qu'ils utilisent. Un point noir signifie « ce fait utilise cette dimension ».

![La matrice des processus de la boutique : les lignes sont les tables de faits, les colonnes les dimensions conformes. Une colonne remplie sur plusieurs lignes est une dimension partagée.](figures/ch01-bus.png)

```python hide
O.fig_bus()
```
<!--sortie-->
```text
figure : ch01-bus.png
```

Elle sert à trois choses. Elle montre **les dimensions à bâtir en premier** : la date, le produit, le canal sont utilisés par presque tous les faits, donc **leur définition doit être commune** et validée une fois. Elle indique les **comparaisons possibles** : deux processus peuvent se comparer (« taux de retour par catégorie ») s'ils partagent une dimension conforme. Enfin elle sert de **feuille de route** : on construit l'entrepôt processus par processus, en réutilisant les dimensions, plutôt que d'un bloc.

Les **data marts** sont la couche que consomment les utilisateurs. Un mart reprend une partie de l'entrepôt, **taillée pour un sujet et un public** :

- le mart **ventes** pour l'équipe commerciale (chiffre d'affaires, marge, par catégorie, canal, mois) ;
- le mart **logistique** pour la responsable des livraisons (délais, retards, par transporteur et par mois) ;
- le mart **finance** pour le comptable (chiffre d'affaires hors taxe mensuel, à rapprocher des comptes).

Un mart peut être une **table** (calculée au chargement, rapide à lire) ou une **vue** (une requête enregistrée, toujours à jour). Voici les deux :

```sql
CREATE SCHEMA mart;
CREATE TABLE mart.ca_mensuel AS
SELECT d.annee_mois, p.categorie, ca.canal, SUM(v.montant_ht) AS ca_ht,
       SUM(v.montant_ht - v.cout_achat) AS marge_ht, SUM(v.quantite) AS unites
FROM dwh.fait_ventes v JOIN dwh.dim_date d USING (date_key)
JOIN dwh.dim_produit p USING (produit_key) JOIN dwh.dim_canal ca USING (canal_key)
GROUP BY ALL;
```

```sql
CREATE VIEW mart.service_transporteur AS
SELECT d.annee_mois, t.transporteur, COUNT(*) AS commandes, SUM(f.retard) AS retards,
       SUM(f.delai_total_j) AS somme_delais_j
FROM dwh.fait_livraisons f JOIN dwh.dim_date d ON d.date_key = f.date_commande_key
JOIN dwh.dim_transporteur t USING (transporteur_key)
GROUP BY ALL;
```

Remarquez que le mart de logistique stocke des **sommes et des comptes** (`retards`, `somme_delais_j`, `commandes`), jamais un taux ni une moyenne : un tableau de bord qui regroupera les mois en trimestres pourra ainsi **recalculer** le bon taux, selon la règle de 1.3.2. Un mart ne contient jamais de chiffre qu'on ne puisse **réagréger**.

Le mart des ventes se rapproche, comme l'étoile, de la comptabilité : le contrôle est le même, fait **à partir du mart**.

```sql
WITH m AS (SELECT annee_mois AS mois, SUM(ca_ht) AS ca FROM mart.ca_mensuel GROUP BY 1)
SELECT COUNT(*) AS mois, ROUND(MAX(ABS(m.ca - c.ca_ht)), 2) AS ecart_max
FROM m JOIN src.compte_resultat c ON c.mois = m.mois;
```
<!--sortie-->
```text
 mois  ecart_max
   36       0.49
```

> 💡 **Intuition.** L'entrepôt est la **cuisine**, les marts sont les **assiettes** : chaque public reçoit ce qu'il peut manger, préparé avec les mêmes ingrédients. Si chaque service refait sa propre cuisine à partir des sources (des marts **indépendants**, chacun avec ses définitions), on retrouve exactement la situation d'ouverture du chapitre : quatre chiffres d'affaires.

> ⚠️ **Piège : les silos.** Des marts qui ne partagent pas les dimensions conformes finissent par se contredire. La matrice des processus est le garde-fou : toute nouvelle dimension s'y inscrit **avant** d'être créée, pour vérifier qu'elle n'existe pas déjà sous un autre nom.

> ✅ **À retenir.**
> - Quand un attribut change, on choisit **par attribut** : **type 1** (écraser : corrections), **type 2** (nouvelle ligne et période de validité : histoire), **type 3** (colonne « précédent » : un seul changement).
> - En type 2, chaque fait rejoint la **version valide à sa date** ; on contrôle l'absence de **chevauchements** et de **trous**, et que le total ne bouge pas.
> - Un chargement de type 2 **ferme puis insère**, et doit être **idempotent** (le relancer ne change rien). On n'historise pas ce qui change tous les jours.
> - La **matrice des processus** organise l'entrepôt (dimensions conformes) ; les **data marts** servent chaque public, avec des sommes et des comptes plutôt que des taux.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.6 et exercices 1.10 et 1.11.
