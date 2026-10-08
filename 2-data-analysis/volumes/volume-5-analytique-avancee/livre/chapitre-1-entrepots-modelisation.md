# Chapitre 1 : Entrepôts de données et modélisation

> « Une donnée ne sert que si tout le monde, en la lisant, comprend la même chose. »


## Un chiffre d'affaires, quatre réponses

Un mercredi, la gérante pose devant vous trois documents. Le classeur Excel que lui envoie chaque mois la personne qui prépare la comptabilité dit : **1 324 764 €** de chiffre d'affaires en 2025. Le tableau de bord de la boutique dit : **1 103 970 €**. Le rapport trimestriel, rédigé par un ancien stagiaire, dit : **1 034 230 €**. Elle ne demande pas lequel est faux. Elle demande : « **Je voudrais le même chiffre partout. Pourquoi est-ce si difficile ?** »

Vous cherchez, et vous trouvez que **personne ne s'est trompé en calculant**. Les trois documents partent de la même base, mais chacun a, sans le dire, **sa propre définition** du chiffre d'affaires :

- le classeur additionne les montants des lignes de commande **toutes taxes comprises** (TTC) ;
- le tableau de bord les divise par 1,2 pour obtenir le chiffre **hors taxe** (la TVA de la boutique fictive est de 20 %) ;
- le rapport retranche en plus les **remboursements** de l'année, calculés à la date du retour, et non à la date de la vente.

Et ce n'est pas tout. Un collègue du service informatique a écrit une requête qui donne **1 352 838 €**, plus que le classeur. Il a joint les lignes de commande aux commandes pour récupérer les **frais de port**, qui sont enregistrés une seule fois par commande, et il les a donc **additionnés autant de fois que la commande a de lignes**. Ce quatrième chiffre n'est pas une définition différente : c'est une **erreur**, et elle est silencieuse, parce que le résultat a l'air raisonnable.

![Quatre « chiffres d'affaires 2025 » calculés à partir de la même base : trois définitions (TTC, hors taxe, net des retours) et une erreur de jointure (frais de port comptés plusieurs fois, en orange).](figures/ch01-trois-chiffres.png)

Voilà le problème que résout un **entrepôt de données**. Ce n'est pas un logiciel plus rapide. C'est un **lieu**, avec des **règles**, où l'on décide une fois pour toutes :

1. ce que **représente une ligne** de chaque table (une ligne de commande, une commande, un retour, un jour de stock) ;
2. ce que **signifie chaque chiffre** (hors taxe, brut des retours, sans les frais de port) et à partir de **quelle colonne** on l'obtient ;
3. comment **ces tables se relient** entre elles, de façon que personne n'ait à deviner une jointure.

> 💡 **Intuition.** Une base opérationnelle est organisée pour **enregistrer** correctement (une commande, une fois). Un entrepôt est organisé pour **comparer et additionner** correctement (le chiffre d'affaires, toujours le même, quelle que soit la personne qui le demande). Ce sont deux métiers différents, donc deux organisations différentes.

Dans ce volume, vous passez des **analyses ponctuelles** (un chiffre, un jour, un notebook) aux **systèmes reproductibles** (un chiffre qui se recalcule seul, se contrôle et s'explique). Ce chapitre pose la première pierre : **où et comment ranger les données** pour qu'elles se laissent additionner sans pièges. Le chapitre 2 apprendra à **les y amener** automatiquement.

## Le chemin de ce chapitre

Le chapitre suit la question de la gérante, de la source de la confusion à la conception d'un entrepôt.

- **1.1 Concepts d'entrepôt de données.** Deux manières d'utiliser les données (enregistrer ou analyser), les **couches** (arrivée, entrepôt, marts), **ETL ou ELT**, entrepôt ou lac de données, et ce qu'un entrepôt ne fait pas.
- **1.2 Schéma en étoile.** Une table de **faits** au centre, des **dimensions** autour. Nous construisons l'étoile de la boutique **en SQL**, nous l'interrogeons, et nous **vérifions** qu'elle retrouve à l'euro près le chiffre d'affaires de la comptabilité.
- **1.3 Faits, dimensions et granularité.** **Déclarer le grain**, distinguer les mesures **additives**, **semi-additives** et **non additives**, traiter les frais de port, choisir entre trois types de tables de faits, et éviter le piège de la jointure entre deux faits.
- **1.4 ➕ Modélisation dimensionnelle.** Quand les attributs **changent** (un client déménage, un produit change de catégorie) : les dimensions à évolution lente, la **matrice des processus** et les **data marts**.
- **1.5 ➕ BigQuery, Snowflake, Redshift, Azure Synapse.** Ce que les entrepôts infonuagiques changent et ne changent pas ; le stockage **en colonnes** et le **partitionnement**, démontrés **en local** avec Parquet.

## Les données du chapitre

> 📦 **Les données.** La base de la boutique des volumes précédents, **simulée** : `clients`, `produits`, `commandes`, `lignes_commande`, `retours`, `livraisons`, `stock_quotidien` et `compte_resultat_mensuel`. Comme le jeu du volume III ne contient pas de **frais de port**, nous en ajoutons une version **calculée par une règle simple** (gratuits en retrait en magasin ou à partir de 80 € de commande, 5,90 € à domicile, 3,90 € en point relais) : c'est ce qui nous permet d'illustrer les mesures d'en-tête. Deux petits fichiers **simulés** (`donnees/ch01-historique-clients.csv` et `ch01-historique-produits.csv`, générés par `build/outils_ch01.py`) donnent l'historique des changements de ville et de catégorie utilisé en 1.4.

L'« entrepôt » de ce chapitre est une base **DuckDB** en mémoire : un moteur SQL gratuit, installé en une ligne, qui lit directement les fichiers CSV et Parquet. Il joue le même rôle que les entrepôts infonuagiques de la section 1.5 pour ce qui est du **modèle** (les tables, les clés, les jointures), à une échelle que votre ordinateur supporte. **Aucun service infonuagique n'est exécuté ici.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.7 et exercices 1.1 à 1.12 ; chacun renvoie à la section du livre qui l'éclaire.


## 1.1 Concepts d'entrepôt de données

Avant de dessiner la moindre table, il faut comprendre **pourquoi** on ne répond pas aux questions d'analyse directement sur la base qui sert à encaisser les commandes. Cette section pose le vocabulaire (OLTP, OLAP, couches, ETL, ELT, lac) et les raisons de séparer l'exploitation de l'analyse.


### 1.1.1 Deux manières d'utiliser les mêmes données

Dans la boutique, les données servent à deux choses très différentes.

La **première** est d'**enregistrer** ce qui se passe : un client passe commande, on crée une commande et trois lignes, on décrémente le stock, on encaisse. Chaque opération touche **quelques lignes**, doit être **immédiate**, et ne doit **jamais** laisser la base dans un état incohérent (une commande sans ses lignes). On parle de traitement **transactionnel**, en anglais **OLTP** (*online transaction processing*).

La **seconde** est d'**analyser** : « combien de chiffre d'affaires par catégorie et par mois depuis trois ans ? ». Chaque opération **lit des milliers ou des millions de lignes**, les additionne, et personne n'attend le résultat à la milliseconde. On parle de traitement **analytique**, en anglais **OLAP** (*online analytical processing*).

Voici les deux, côte à côte, sur la base de la boutique. D'abord une opération d'enregistrement ou de consultation, qui retrouve **une** commande :

```sql
SELECT c.id_commande, c.date_commande, l.id_produit, l.quantite, l.montant
FROM src.commandes c JOIN src.lignes_commande l USING (id_commande)
WHERE c.id_commande = 12345;
```
<!--sortie-->
```text
 id_commande date_commande  id_produit  quantite  montant
       12345    2024-02-02          49         1     29.9
       12345    2024-02-02         101         1     18.9
       12345    2024-02-02          20         1     27.9
```

Puis une question d'analyse, qui **lit toute la table** des lignes :

```sql
SELECT year(c.date_commande) AS annee, c.canal, ROUND(SUM(l.montant)) AS ca_ttc
FROM src.commandes c JOIN src.lignes_commande l USING (id_commande)
GROUP BY 1, 2 ORDER BY 1, 2;
```
<!--sortie-->
```text
 annee    canal   ca_ttc
  2023 Boutique 593612.0
  2023  Réseaux 122880.0
  2023     Site 422440.0
  2024 Boutique 558143.0
  2024  Réseaux 128787.0
  2024     Site 502531.0
  2025 Boutique 560974.0
  2025  Réseaux 146074.0
  2025     Site 617715.0
```

La première requête touche trois lignes sur 83 905 ; la seconde les lit **toutes**. Les deux métiers n'ont pas les mêmes besoins, et ce qui rend l'un efficace gêne l'autre.

| | Exploitation (OLTP) | Analyse (OLAP) |
|---|---|---|
| **Objectif** | enregistrer, corriger, consulter une opération | comparer, additionner, suivre dans le temps |
| **Requête type** | « la commande 12345 » | « le chiffre d'affaires par catégorie et par mois » |
| **Lignes lues par requête** | quelques-unes | des milliers à des millions |
| **Écritures** | nombreuses, petites, immédiates | rares, par lots (chargement) |
| **Organisation** | **normalisée** : chaque fait écrit **une seule fois** | **dénormalisée** : tables larges, redondance voulue |
| **Historique** | l'état **actuel** (on écrase) | **toute l'histoire** (on conserve) |
| **Qui l'utilise** | caisse, site, équipe logistique | analystes, direction, tableaux de bord |
| **Qualité attendue** | cohérence de chaque opération | **cohérence entre les chiffres** |

> 💡 **Intuition.** La base d'exploitation est une **caisse enregistreuse** : parfaite pour encaisser, mal faite pour répondre à « comment ont évolué nos ventes ? ». L'entrepôt est le **registre des ventes** que l'on range une fois par jour, pour pouvoir le feuilleter.

### 1.1.2 Pourquoi séparer l'analyse de l'exploitation

On pourrait être tenté d'analyser directement dans la base d'exploitation : elle contient déjà tout. Six raisons plaident pour une séparation.

1. **La charge.** Une requête qui lit trois ans de ventes peut ralentir la caisse un samedi après-midi. On ne fait pas travailler la caisse et le comptable sur le même appareil.
2. **L'historique.** La base d'exploitation écrase : un client change de ville, l'ancienne ville disparaît. Pour comprendre le passé, il faut **conserver** les anciennes valeurs (section 1.4).
3. **L'intégration de plusieurs sources.** La boutique a une caisse, un site, des réseaux sociaux, une comptabilité, un transporteur. Chacun a ses identifiants, ses formats, ses retards. L'entrepôt est le seul endroit où elles se **rencontrent**.
4. **Les définitions communes.** Le chiffre d'affaires se définit **une fois** (hors taxe, brut des retours, sans les frais de port) ; toutes les questions l'utilisent.
5. **La qualité.** Les contrôles (« pas de ligne de commande sans produit connu ») se font à l'arrivée, **avant** que les erreurs ne se répandent dans les rapports.
6. **Les droits d'accès.** On peut ne pas montrer l'e-mail des clients à qui n'analyse que des ventes ; l'entrepôt ne les contient simplement pas.

La troisième raison est la plus visible dans nos données. La boutique a **120 produits mais seulement 60 noms** : deux produits distincts portent le même nom, avec des prix différents.

```sql
SELECT nom_produit, COUNT(*) AS nb_id, MIN(prix_vente) AS prix_min, MAX(prix_vente) AS prix_max
FROM src.produits GROUP BY nom_produit HAVING COUNT(*) > 1
ORDER BY nom_produit LIMIT 5;
```
<!--sortie-->
```text
          nom_produit  nb_id  prix_min  prix_max
       Affiche design      2      27.9      35.9
       Agenda compact      2       9.9      20.9
    Arrosoir nordique      2      15.9      86.9
Autocollants rustique      2      13.9      18.9
          Bac compact      2      61.9      66.9
```

Un rapport qui regroupe « par nom de produit » fusionne deux produits en un seul. Un entrepôt **ne résout pas** cette ambiguïté à la place de l'entreprise, mais il force à la **voir** et à la **traiter** une fois : la dimension des produits aura pour clé l'**identifiant**, jamais le nom (section 1.3.5).

> ⚠️ **Piège : confondre copie et entrepôt.** Copier la base d'exploitation sur un autre serveur donne un « miroir », utile pour ne pas ralentir la caisse, mais **pas un entrepôt** : les tables sont encore normalisées pour l'enregistrement, il n'y a pas d'historique, et chaque question exige de redeviner les jointures et les définitions.

### 1.1.3 Les couches d'un entrepôt

Un entrepôt n'est pas une seule base mais une **suite d'étapes**, chacune dans son propre espace (un *schéma* dans une base SQL) :

![Les couches d'un entrepôt : sources, zone d'arrivée (src), entrepôt (dwh), data marts (mart), usages.](figures/ch01-couches.png)


- **Les sources** sont les systèmes d'origine : la base de la caisse, les exports du site, les fichiers du transporteur. On n'y touche pas.
- **La zone d'arrivée** (*staging*, schéma `src` dans ce chapitre) reçoit une **copie brute et datée** des sources, sans règle métier. Si le chargement du lendemain échoue, on peut rejouer à partir d'ici sans réinterroger la caisse.
- **L'entrepôt** (schéma `dwh`) contient les données **nettoyées, typées et modélisées** : les tables de faits et de dimensions des sections suivantes. C'est la **source de vérité** des chiffres.
- **Les data marts** (schéma `mart`) sont des vues ou des tables **dérivées de l'entrepôt**, taillées pour un sujet et un public : un mart « ventes » pour le marketing, un mart « logistique » pour la responsable des livraisons, un mart « finance » pour le comptable (section 1.4).
- **Les usages** (tableau de bord, classeur, rapport, API) ne lisent **que** les marts ou l'entrepôt, jamais les sources.

Dans notre base DuckDB, la zone d'arrivée contient déjà les tables de la boutique :

```sql
SELECT table_name, estimated_size AS lignes
FROM duckdb_tables() WHERE schema_name = 'src' ORDER BY table_name;
```
<!--sortie-->
```text
     table_name  lignes
        clients    6000
      commandes   36395
compte_resultat      36
lignes_commande   83905
     livraisons   19420
       produits     120
        retours    5002
stock_quotidien    7300
```

> 🧭 **En pratique : une règle de couches.** On ne **corrige jamais une donnée à la main** dans l'entrepôt. Si une valeur est fausse, on corrige **la règle qui la fabrique** (ou la source), puis on **rejoue** le chargement. C'est ce qui rend l'entrepôt **reproductible** : le chapitre 2 apprendra à l'automatiser, et tout le volume repose sur ce principe.

### 1.1.4 ETL ou ELT ?

Amener les données de la source à l'entrepôt s'appelle **charger**, et l'on distingue deux ordres d'opérations.

- **ETL** (*extract, transform, load*) : on **extrait** les données, on les **transforme** dans un programme extérieur (Python, par exemple), puis on **charge** le résultat dans l'entrepôt. L'entrepôt ne reçoit que du propre.
- **ELT** (*extract, load, transform*) : on **extrait**, on **charge tel quel** dans la zone d'arrivée, puis on **transforme dans l'entrepôt** avec du SQL. Le moteur de l'entrepôt fait le gros du travail.

| | ETL | ELT |
|---|---|---|
| **Où se transforme la donnée** | dans un programme extérieur | dans le moteur de l'entrepôt (SQL) |
| **Ce qui est conservé** | seulement le résultat transformé | la copie brute **et** le résultat |
| **Rejouer une transformation** | il faut ré-extraire la source | on relit la copie brute |
| **Convient quand** | le moteur est faible, ou les données sensibles doivent être masquées avant d'entrer | le moteur est puissant (c'est le cas des entrepôts modernes) |

Dans ce volume nous pratiquons surtout l'**ELT** : la zone `src` reçoit une copie des fichiers, et le SQL de la section 1.2 fabrique l'étoile. Les deux ordres ne s'opposent pas : un chargement réel mélange les deux (masquer d'abord une donnée personnelle, transformer ensuite dans l'entrepôt). Le chapitre 2 détaille les chargements complets et incrémentaux, la reprise sur erreur et l'automatisation.

### 1.1.5 Entrepôt, lac de données et « lakehouse »

Un **lac de données** (*data lake*) est un grand espace de **fichiers** (CSV, JSON, images, journaux, Parquet) rangés tels quels, **sans schéma imposé à l'écriture** ; on décide de leur structure **à la lecture**. Un entrepôt, à l'inverse, **impose** un schéma à l'écriture : une table, des colonnes typées, des clés.

| | Entrepôt | Lac de données |
|---|---|---|
| **Données** | structurées, modélisées | tous formats, bruts |
| **Schéma** | à l'écriture | à la lecture |
| **Public** | analystes, direction | data scientists, ingénieurs |
| **Force** | cohérence, chiffres de référence | flexibilité, faible coût de stockage |
| **Risque** | rigidité, coût de modélisation | **marécage** : des fichiers que personne ne sait plus lire |

On entend aussi parler de **lakehouse** : des fichiers dans un lac, mais avec une couche de gestion qui apporte des tables, des transactions et un schéma, pour que l'on puisse faire de l'analyse dessus comme sur un entrepôt. C'est une tendance des outils ; elle ne change pas le travail de **modélisation** que ce chapitre enseigne. Les produits changent vite : **vérifiez dans la documentation de votre version** ce que chacun garantit réellement.

> 💡 **Intuition.** Un lac sans entrepôt est une **cave pleine de cartons non étiquetés** ; un entrepôt sans lac est un **rayonnage rangé qui ne contient que ce qu'on avait prévu**. La plupart des organisations ont les deux, et ce qui compte est de savoir ce qui est dans quel espace.

### 1.1.6 Ce qu'un entrepôt ne fait pas

Un entrepôt est un outil, pas une solution.

- **Il ne rend pas les données exactes.** Si la caisse enregistre un prix faux, l'entrepôt le conserve fidèlement. Les **contrôles** (chapitre 2) détectent ; ils ne devinent pas.
- **Il ne choisit pas les définitions.** Hors taxe ou TTC, brut ou net des retours : c'est une **décision de l'entreprise**, que l'analyste fait écrire et valider (volume III, chapitre 6, sur la définition des indicateurs).
- **Il ne remplace pas le tableau de bord.** Il l'alimente : le modèle en étoile est précisément celui que les outils de visualisation attendent (volume IV, section 2.1).
- **Il a un coût** : du temps de modélisation, de la maintenance, et la discipline de passer par lui. Pour une petite boutique, un simple fichier DuckDB suffit ; l'important est la **méthode**, pas la taille de l'infrastructure.

> ✅ **À retenir.**
> - L'exploitation **enregistre** (peu de lignes, état actuel, normalisé) ; l'analyse **compare** (beaucoup de lignes, historique, dénormalisé). On les sépare pour la charge, l'historique, l'intégration, les définitions, la qualité et les droits.
> - Un entrepôt a des **couches** : arrivée (copie brute), entrepôt (modélisé, source de vérité), marts (par sujet), usages. On ne corrige jamais à la main : on corrige la règle et on rejoue.
> - **ELT** : charger d'abord, transformer ensuite en SQL ; **ETL** : transformer avant de charger. Les deux se mélangent.
> - Un **lac** stocke des fichiers bruts, un **entrepôt** des tables modélisées ; sans méthode, un lac devient un marécage.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1 et exercice 1.1.


## 1.2 Schéma en étoile

Le schéma en **étoile** est la forme que prennent presque tous les entrepôts pour l'analyse. L'idée est simple : au centre, **ce que l'on mesure** (des ventes) ; autour, **les points de vue** selon lesquels on veut le regarder (par date, par client, par produit). Cette section le construit pour la boutique, **en SQL**, l'interroge, et le **vérifie** contre la comptabilité.


### 1.2.1 Une table de faits au centre, des dimensions autour

Prenons six lignes de vente, telles qu'on les trouverait dans un classeur à plat :

| ligne | date | client | ville | produit | catégorie | montant |
|---|---|---|---|---|---|---|
| 1 | 3 janv. | Cl. 17 | Ville B | Bol design | Cuisine | 19,90 |
| 2 | 3 janv. | Cl. 17 | Ville B | Plaid doux | Maison | 45,00 |
| 3 | 3 janv. | Cl. 52 | Ville A | Bol design | Cuisine | 19,90 |
| 4 | 4 janv. | Cl. 17 | Ville B | Bol design | Cuisine | 19,90 |
| 5 | 4 janv. | Cl. 80 | Ville A | Plaid doux | Maison | 45,00 |
| 6 | 5 janv. | Cl. 52 | Ville A | Plaid doux | Maison | 45,00 |

Trois colonnes (`ville`, `produit`, `catégorie`) **répètent** des descriptions. Si une catégorie est renommée, il faudrait corriger vingt mille lignes. On sépare donc **ce qui est mesuré** de **ce qui décrit** :

| **fait_ventes** | date_key | client_key | produit_key | montant |
|---|---|---|---|---|
| 1 | 20250103 | 17 | 1 | 19,90 |
| 2 | 20250103 | 17 | 2 | 45,00 |
| 3 | 20250103 | 52 | 1 | 19,90 |
| … | … | … | … | … |

| **dim_produit** | produit_key | nom | catégorie |
|---|---|---|---|
| | 1 | Bol design | Cuisine |
| | 2 | Plaid doux | Maison |

La table du milieu est la **table de faits** : une ligne par événement mesuré, des **mesures** numériques (le montant) et des **clés** qui pointent vers les dimensions. Les petites tables autour sont les **dimensions** : une ligne par client, par produit, par jour, avec des attributs descriptifs. Dessinées autour de la table de faits, elles forment une **étoile**.

> 💡 **Intuition.** Une question d'analyse a presque toujours la forme « **mesure** par **dimension** » : le *chiffre d'affaires* par *catégorie* et par *mois*. Le schéma en étoile range les données **comme la question est posée** : la mesure au centre, les « par » autour.

### 1.2.2 Construire l'étoile de la boutique

Nous allons créer, dans le schéma `dwh`, cinq dimensions et une table de faits. Commençons par la **dimension de date**, qui n'existe dans aucune source : on la **fabrique**, une ligne par jour, avec les attributs dont les analyses ont besoin (année, trimestre, mois, week-end).

```sql
CREATE SCHEMA dwh;
CREATE MACRO cle_date(d) AS CAST(strftime(CAST(d AS DATE), '%Y%m%d') AS INTEGER);
CREATE TABLE dwh.dim_date AS
SELECT cle_date(d) AS date_key, CAST(d AS DATE) AS date,
       year(d) AS annee, quarter(d) AS trimestre, month(d) AS mois,
       strftime(d, '%Y-%m') AS annee_mois, isodow(d) AS jour_semaine, isodow(d) >= 6 AS est_weekend
FROM generate_series(DATE '2023-01-01', DATE '2025-12-31', INTERVAL 1 DAY) AS t(d);
```

La clé de la dimension est un **entier lisible** (`20250103` pour le 3 janvier 2025) : la petite fonction SQL `cle_date`, définie juste avant, la calcule à partir de n'importe quelle date, de façon que la **même règle** serve à la dimension et à toutes les tables de faits.

Puis la **dimension des produits**, copiée de la source, avec une **clé de substitution** (`produit_key`) et une ligne **« inconnu »** de clé 0 :

```sql
CREATE TABLE dwh.dim_produit AS
SELECT 0 AS produit_key, -1 AS id_produit, 'inconnu' AS nom_produit,
       'inconnu' AS categorie, 'inconnu' AS fournisseur, NULL AS prix_catalogue
UNION ALL
SELECT row_number() OVER (ORDER BY id_produit), id_produit, nom_produit,
       categorie, fournisseur, prix_vente
FROM src.produits;
```

Trois choix méritent d'être expliqués.

- **La clé de substitution** (`produit_key`) est un entier **sans signification métier**, créé par l'entrepôt. L'identifiant de la source (`id_produit`) reste dans la table comme **clé naturelle**, mais **les faits ne pointent jamais dessus** : si la source réutilise un jour un identifiant, ou si deux sources se rencontrent, l'entrepôt n'est pas perturbé ; et, nous le verrons en 1.4, une même clé naturelle pourra correspondre à **plusieurs versions** d'un produit.
- **La ligne « inconnu »** (clé 0) reçoit les ventes dont le produit n'existe pas (encore) dans la dimension. Sans elle, ces ventes **disparaîtraient** d'une jointure interne, et le chiffre d'affaires serait faux sans que rien ne le signale (section 1.3.5).
- **Les dimensions client, canal, promotion** se construisent de la même façon (voir le cahier). La dimension du **canal** regroupe deux colonnes de la commande (le canal de vente et le mode de livraison) en une seule ligne : c'est une dimension « fourre-tout » (*junk dimension*) qui évite de multiplier les petites tables.


Enfin la **table de faits**. Le **grain** (ce que représente une ligne) est déclaré d'abord : **une ligne de commande**. Chaque ligne reçoit les clés des cinq dimensions, ses mesures telles que la source les donne, et deux mesures **calculées une fois pour toutes** : le montant hors taxe et le coût d'achat. Aucune n'est **arrondie** : on arrondit à l'affichage, jamais au stockage (voir plus bas).

```sql
CREATE TABLE dwh.fait_ventes AS
SELECT l.id_ligne, l.id_commande,
       cle_date(c.date_commande) AS date_key,
       k.client_key, p.produit_key, ca.canal_key, pr.promo_key,
       l.quantite, l.prix_unitaire, l.remise_pct,
       l.montant AS montant_ttc, l.montant / 1.2 AS montant_ht,
       l.quantite * sp.cout_achat AS cout_achat
FROM src.lignes_commande l
JOIN src.commandes c USING (id_commande)
JOIN src.produits sp USING (id_produit)
JOIN dwh.dim_client k ON k.id_client = c.id_client
JOIN dwh.dim_produit p ON p.id_produit = l.id_produit
JOIN dwh.dim_canal ca ON ca.canal = c.canal AND ca.mode_livraison = c.mode_livraison
JOIN dwh.dim_promotion pr ON pr.code_promo = COALESCE(c.code_promo, 'Aucune');
```

La table de faits a **le même nombre de lignes que la source** : on n'a rien perdu, rien dupliqué. C'est la première vérification, et elle est systématique :

```sql
SELECT (SELECT COUNT(*) FROM src.lignes_commande) AS source,
       (SELECT COUNT(*) FROM dwh.fait_ventes) AS entrepot,
       (SELECT ROUND(SUM(montant), 2) FROM src.lignes_commande) AS ttc_source,
       (SELECT ROUND(SUM(montant_ttc), 2) FROM dwh.fait_ventes) AS ttc_entrepot;
```
<!--sortie-->
```text
 source  entrepot  ttc_source  ttc_entrepot
  83905     83905  3653157.28    3653157.28
```


La dimension des produits, avec sa ligne « inconnu », ressemble à ceci :

```sql
SELECT produit_key, id_produit, nom_produit, categorie FROM dwh.dim_produit
ORDER BY produit_key LIMIT 4;
```
<!--sortie-->
```text
 produit_key  id_produit        nom_produit categorie
           0          -1            inconnu   inconnu
           1           1 Casserole nordique   Cuisine
           2           2          Poêle mat   Cuisine
           3           3         Bol design   Cuisine
```

Voici l'étoile complète de ce qu'on vient de bâtir :

![Le schéma en étoile de la boutique : la table de faits fait_ventes au centre, cinq dimensions autour. Les clés (date_key, client_key, produit_key, canal_key, promo_key) sont des clés de substitution.](figures/ch01-etoile.png)


> ⚠️ **Piège : mettre les clés naturelles dans la table de faits.** Si `fait_ventes` contenait `id_produit` au lieu de `produit_key`, la première réutilisation d'un identifiant ou la première fusion de deux sources casserait **toutes les jointures historiques** sans erreur visible. On joint toujours sur la **clé de substitution**.

### 1.2.3 Interroger l'étoile, et vérifier

Une question d'analyse se pose maintenant **toujours de la même façon** : une jointure de la table de faits avec les dimensions utiles, un filtre, un regroupement. Le chiffre d'affaires hors taxe par catégorie, en janvier 2025 :

```sql
SELECT p.categorie, ROUND(SUM(v.montant_ht)) AS ca_ht
FROM dwh.fait_ventes v
JOIN dwh.dim_date d USING (date_key)
JOIN dwh.dim_produit p USING (produit_key)
WHERE d.annee_mois = '2025-01'
GROUP BY 1 ORDER BY 1;
```
<!--sortie-->
```text
 categorie   ca_ht
 Bien-être  9013.0
   Cuisine 16229.0
Décoration 16377.0
    Jardin  6213.0
    Maison 23040.0
 Papeterie  3444.0
```

Que gagne-t-on, par rapport à la même question posée sur la base d'exploitation ? **Honnêtement, pas moins de jointures** : la requête sur la source en compte aussi trois (lignes, commandes, produits). Le gain est ailleurs :

- les attributs de date (**trimestre, mois, week-end**) sont **déjà là**, écrits **une fois**, au lieu d'être recalculés par chaque requête avec chacune sa petite variante (la semaine commence-t-elle le lundi ou le dimanche ?) ;
- le **montant hors taxe** est une colonne, pas une division par 1,2 recopiée dans quarante requêtes (et oubliée dans la quarante et unième) ;
- les jointures sont **toutes du même type** (fait vers dimension, sur une clé entière) : on ne peut pas dupliquer des lignes en se trompant de clé ;
- tous les tableaux de bord et tous les rapports **parlent de la même colonne** : c'est la réponse à la question de la gérante.

On ne se fie pourtant pas à un résultat parce qu'il a l'air plausible. Première vérification croisée : **pandas, depuis les fichiers d'origine**, retrouve-t-il les mêmes 216 chiffres (36 mois × 6 catégories) ?

```text
216 cellules mois x catégorie comparées ; écart absolu maximal : 0.00 €
```

L'écart n'est que du bruit de calcul en virgule flottante : les deux outils trouvent **les mêmes 216 chiffres**. Deuxième vérification, plus exigeante : **la comptabilité**. Le compte de résultat mensuel de la boutique donne un chiffre d'affaires hors taxe, arrondi à l'euro. L'étoile le retrouve-t-elle ?

```sql
WITH e AS (SELECT d.annee_mois AS mois, SUM(v.montant_ht) AS ca
           FROM dwh.fait_ventes v JOIN dwh.dim_date d USING (date_key) GROUP BY 1)
SELECT COUNT(*) AS mois, ROUND(MAX(ABS(e.ca - c.ca_ht)), 2) AS ecart_max,
       ROUND(SUM(e.ca) - SUM(c.ca_ht), 2) AS ecart_total
FROM e JOIN src.compte_resultat c ON c.mois = e.mois;
```
<!--sortie-->
```text
 mois  ecart_max  ecart_total
   36       0.49        -0.27
```

Sur les **trente-six mois**, l'écart maximal est inférieur à un euro : c'est l'arrondi à l'euro de la comptabilité. C'est ce que l'on appelle un **rapprochement** : l'entrepôt n'est digne de confiance que s'il retrouve un chiffre qu'une autre source, indépendante, établit. Nous reviendrons sur ce contrôle au chapitre 2 (il devient une étape du chargement) et au chapitre 4 (reporting de gestion).


> ⚠️ **Piège : arrondir au stockage.** Nous avons gardé `montant_ht` **sans arrondi**. Si l'on avait arrondi chaque ligne à deux décimales, l'écart maximal avec la comptabilité serait monté de **0,49 €** à **2,80 €** sur un mois : les montants TTC de la boutique sont souvent en dixièmes d'euro, leur division par 1,2 tombe sur des décimales du type 0,91666…, et l'arrondi les pousse **presque toujours dans le même sens**. Sur 80 000 lignes, ces petits écarts **ne se compensent pas**. Règle : on **stocke** avec toute la précision (type décimal ou flottant), on **arrondit à l'affichage**.

Voici le résultat de la requête « chiffre d'affaires par catégorie et par mois » sur trois ans, lu depuis l'étoile :

![Chiffre d'affaires hors taxe mensuel par catégorie, 2023-2025, lu dans l'étoile : la saisonnalité de fin d'année est visible dans toutes les catégories.](figures/ch01-ca-categorie.png)


### 1.2.4 Le flocon : normaliser une dimension

Dans une étoile, les dimensions sont **à plat** : la dimension des produits contient le nom, la catégorie, le fournisseur dans la même table, avec des répétitions (la catégorie « Cuisine » est écrite vingt fois). On peut au contraire **normaliser** la dimension en la découpant, par exemple en isolant les catégories dans leur propre table. On obtient un **schéma en flocon** (*snowflake*).

![Étoile (à gauche) et flocon (à droite) : le flocon normalise la dimension des produits en une table de catégories, au prix d'une jointure de plus.](figures/ch01-flocon.png)


Pour regrouper les catégories en **familles** (un regroupement défini ici pour l'exemple), le flocon crée une table de catégories ; la dimension des produits n'en garde que la clé :

```sql
CREATE TABLE dwh.dim_categorie AS
SELECT row_number() OVER (ORDER BY categorie) AS categorie_key, categorie,
       CASE WHEN categorie = 'Jardin' THEN 'Extérieur'
            WHEN categorie IN ('Cuisine', 'Maison', 'Décoration') THEN 'Intérieur'
            ELSE 'Loisirs et bien-être' END AS famille
FROM (SELECT DISTINCT categorie FROM src.produits);
CREATE VIEW dwh.dim_produit_flocon AS
SELECT p.produit_key, p.nom_produit, c.categorie_key
FROM dwh.dim_produit p LEFT JOIN dwh.dim_categorie c USING (categorie);
```

Le chiffre d'affaires par famille exige maintenant **une jointure de plus** (fait, produit, catégorie), mais donne bien le même total :

```sql
SELECT c.famille, ROUND(SUM(v.montant_ht)) AS ca_ht
FROM dwh.fait_ventes v
JOIN dwh.dim_produit_flocon p USING (produit_key)
JOIN dwh.dim_categorie c USING (categorie_key)
GROUP BY 1 ORDER BY 1;
```
<!--sortie-->
```text
             famille     ca_ht
           Extérieur  808650.0
           Intérieur 1833406.0
Loisirs et bien-être  402242.0
```

Quand préférer l'un ou l'autre ?

| | Étoile | Flocon |
|---|---|---|
| **Jointures par requête** | le moins possible | une de plus par niveau |
| **Redondance** | oui (texte répété) | non |
| **Lisibilité pour l'analyste** | une table par « point de vue » | plusieurs tables à connaître |
| **Mise à jour d'un libellé** | à modifier dans la dimension, en une fois | idem, dans une table plus petite |
| **Quand le choisir** | **par défaut**, surtout avec les outils de tableau de bord | dimension énorme et très hiérarchique, ou sous-dimension **partagée** par plusieurs dimensions |

Avec des moteurs en colonnes qui compressent très bien le texte répété (section 1.5), l'économie de place du flocon est **négligeable** ; c'est la **simplicité de lecture** de l'étoile qui l'emporte presque toujours.

> 🧭 **En pratique : étoile par défaut.** On part d'une étoile. On ne normalise une dimension que si l'on peut citer la raison (une sous-dimension commune à plusieurs dimensions, par exemple une table de villes utilisée à la fois par les clients et les magasins).

### 1.2.5 Ce que l'étoile facilite, et ce qu'elle coûte

L'étoile facilite trois choses : les **requêtes** (même forme à chaque fois), les **outils** (un tableau de bord s'y branche directement ; le « modèle de données » du volume IV, section 2.1, est exactement une étoile) et la **gouvernance** (une colonne, une définition, un propriétaire).

Elle a un coût. Les **dimensions** sont **dénormalisées**, donc redondantes ; il faut **les reconstruire** quand la source change ; et chaque nouvelle question qui exige un nouvel attribut (« le jour de la semaine de la livraison ») demande de le **modéliser** d'abord. Cette discipline est le prix de chiffres qui ne divergent plus. Pour une petite boutique, le calcul est vite fait : l'étoile entière tient en mémoire, se reconstruit en un instant, et rend le débat « quel chiffre est le bon ? » **sans objet**.

> ✅ **À retenir.**
> - L'**étoile** : une table de **faits** (mesures + clés) au centre, des **dimensions** (descriptions) autour. Les questions s'écrivent « mesure par dimension ».
> - On joint toujours sur des **clés de substitution** ; une ligne **« inconnu »** (clé 0) évite de perdre des ventes ; la **dimension de date** se fabrique.
> - On **vérifie** : mêmes effectifs et mêmes totaux que la source, même résultat par un second outil (pandas), même chiffre que la **comptabilité** (rapprochement).
> - Le **flocon** normalise une dimension ; on part d'une étoile et l'on ne normalise que pour une raison précise.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.2 et 1.3, exercices 1.2 à 1.4.


## 1.3 Faits, dimensions et granularité

Dessiner une étoile est facile. La **dessiner juste** demande de répondre, pour chaque table de faits, à une question que l'on esquive trop souvent : **que représente exactement une ligne ?** Cette section pose la règle du **grain**, distingue les mesures qu'on peut additionner de celles qu'on ne peut pas, règle le cas des frais de port, présente trois types de tables de faits, et montre le piège le plus coûteux de l'analyse : **joindre deux tables de faits entre elles**.


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


## 1.4 ➕ Pour aller plus loin : modélisation dimensionnelle

> 🧭 Section optionnelle. Elle répond à une question que le parcours essentiel laisse ouverte : **que devient une dimension quand ses attributs changent ?** Elle présente ensuite la matrice des processus et les data marts, qui organisent un entrepôt quand il grandit.


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


Les écarts vont de 2 à 9 %. La Ville A, la plus peuplée, a reçu des clients qui y ont déménagé : le type 1 lui attribue **5,8 %** de chiffre d'affaires de trop en 2024. La petite Ville K en a perdu : le type 1 lui en attribue **9,4 %** de moins que ce qu'elle a réellement fait. Le total, lui, est **identique** : seule la **répartition** change. C'est la nature de l'erreur : une série par ville qui a l'air bonne, un total correct, et une analyse géographique **faussée**.


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


> ⚠️ **Piège : historiser ce qui change tout le temps.** Un attribut qui change souvent (le « nombre d'achats du client », un score recalculé chaque jour) donnerait, en type 2, **une nouvelle ligne par client et par jour** : pour nos 6 000 clients, plus de deux millions de lignes par an, pour une dimension qui devrait en compter 6 000. Ces valeurs **n'appartiennent pas à une dimension** : on les range dans un **fait** (un instantané périodique) ou dans une **mini-dimension** de quelques tranches (« 0-2 achats », « 3-9 », « 10 et plus »). On ne fait du type 2 que sur des attributs qui changent **rarement** et dont l'historique **sert** à des analyses.

### 1.4.5 Matrice des processus et data marts

Quand l'entrepôt compte plusieurs tables de faits, il faut un **plan d'ensemble**. La **matrice des processus** (*bus matrix*) croise, en lignes, les **processus** que l'on mesure et, en colonnes, les **dimensions** qu'ils utilisent. Un point noir signifie « ce fait utilise cette dimension ».

![La matrice des processus de la boutique : les lignes sont les tables de faits, les colonnes les dimensions conformes. Une colonne remplie sur plusieurs lignes est une dimension partagée.](figures/ch01-bus.png)


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


## 1.5 ➕ Pour aller plus loin : BigQuery, Snowflake, Redshift, Azure Synapse

> 🧭 Section optionnelle. Aucun des quatre services nommés ici n'est exécuté dans ce livre. Ce que nous montrons **en local**, avec des fichiers Parquet et DuckDB, ce sont les **mécanismes** sur lesquels ils reposent : le stockage en colonnes et le partitionnement.


### 1.5.1 Ce que change un entrepôt infonuagique, et ce qui ne change pas

Un entrepôt infonuagique est un entrepôt **loué** : on n'installe rien, on ne gère pas les serveurs, on envoie des données et des requêtes SQL à un service, et l'on paie ce que l'on utilise. Quatre services sont très connus : **BigQuery**, **Snowflake**, **Redshift** et **Azure Synapse**. Ils diffèrent par bien des détails, mais ils partagent des idées.

- **Stockage et calcul séparés.** Les données vivent dans un stockage partagé, bon marché et durable ; la puissance de calcul se **démarre, s'arrête et se dimensionne** indépendamment. Plusieurs équipes peuvent interroger les mêmes données avec des calculs différents, sans se gêner.
- **Stockage en colonnes.** Les données sont rangées **colonne par colonne** et compressées. Une requête qui ne lit que trois colonnes sur trente ne lit que ces trois-là.
- **Élasticité.** On peut disposer de beaucoup de puissance pour une heure, puis plus du tout. Ce qui coûtait un serveur acheté coûte une durée d'utilisation.
- **Facturation à l'usage**, sous des formes qui varient : au volume de données **lues**, au **temps** de calcul, ou à une **capacité** réservée.

![Stockage et calcul séparés : plusieurs calculs, démarrés et arrêtés indépendamment, lisent le même stockage partagé (schéma générique, sans identité d'un produit).](figures/ch01-stockage-calcul.png)


Ce qui **ne change pas** est tout ce que ce chapitre a enseigné : l'**étoile**, le **grain**, les mesures additives, les dimensions conformes, les dimensions à évolution lente, les contrôles de rapprochement. Un entrepôt infonuagique mal modélisé donne, à plus grande échelle et plus cher, les mêmes quatre chiffres d'affaires. **La modélisation est indépendante de l'outil.**

> ⚠️ **Piège : croire que le service règle la méthode.** Un service puissant exécute vite une requête fausse. La puissance accélère la **réponse**, pas la **justesse**.

### 1.5.2 Le stockage en colonnes, démontré en local

Un fichier CSV range les données **ligne par ligne** : pour lire une colonne, il faut parcourir toutes les lignes en entier. **Parquet**, format de fichier ouvert très répandu (et lisible par DuckDB comme par les entrepôts infonuagiques), les range **colonne par colonne**, les compresse, et note dans un pied de fichier ce que contient chaque colonne.

Écrivons la table de faits de la boutique dans les deux formats, dans un dossier temporaire :

```python
TMP = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"), prefix="ch01_")
con.executescript("CREATE TABLE dwh.vf AS SELECT v.*, d.annee FROM dwh.fait_ventes v "
                  "JOIN dwh.dim_date d USING (date_key) ORDER BY id_ligne")
con.executescript(f"COPY dwh.vf TO '{TMP}/ventes.csv' (HEADER)")
con.executescript(f"COPY dwh.vf TO '{TMP}/ventes.parquet' (FORMAT parquet, COMPRESSION zstd)")
ko = lambda f: os.path.getsize(f"{TMP}/{f}") / 1024
print(f"CSV : {ko('ventes.csv'):.0f} ko ; Parquet : {ko('ventes.parquet'):.0f} ko ; "
      f"rapport : {ko('ventes.csv') / ko('ventes.parquet'):.1f}")
```
<!--sortie-->
```text
CSV : 5959 ko ; Parquet : 818 ko ; rapport : 7.3
```

Le même contenu pèse **7,3 fois moins** en Parquet, parce que chaque colonne se compresse bien (les valeurs d'une colonne se ressemblent : un canal parmi sept, une quantité de un à cinq). Le pied du fichier dit de plus **combien d'octets occupe chaque colonne** :

```python
m = con.df(f"""SELECT path_in_schema AS colonne, SUM(total_compressed_size) AS octets
               FROM parquet_metadata('{TMP}/ventes.parquet') GROUP BY 1 ORDER BY 2 DESC""")
m["part_pct"] = (100 * m["octets"] / m["octets"].sum()).round(1)
print(m.head(5).to_string(index=False))
```
<!--sortie-->
```text
    colonne   octets  part_pct
 client_key 127203.0      15.5
   id_ligne 121672.0      14.8
 montant_ht 113165.0      13.8
montant_ttc 113067.0      13.8
 cout_achat  92996.0      11.3
```

Une requête qui additionne **seulement** `montant_ttc` ne lit donc que **13,8 %** du fichier, et ignore le reste. (Les colonnes d'identifiants, dont presque toutes les valeurs sont différentes, sont celles qui se compressent le moins.)

![À gauche, l'espace que chaque colonne occupe dans le fichier Parquet de la table de faits : lire montant_ttc seul, c'est lire la barre orange. À droite, un fichier par année : filtrer sur l'année évite d'ouvrir les autres.](figures/ch01-parquet.png)


> 💡 **Intuition.** Un CSV est un **registre relié** : pour connaître la somme d'une colonne, il faut tourner toutes les pages. Un fichier en colonnes est un **classeur à onglets** : on ouvre l'onglet voulu. Plus la table est large (quarante colonnes dans une vraie table de faits), plus l'avantage grandit.

### 1.5.3 Partitionner, et ce que cela change au coût

Seconde idée : **découper** la table en plusieurs fichiers selon une colonne (la date, le plus souvent), de sorte qu'une requête qui filtre sur cette colonne **n'ouvre que les fichiers concernés**. C'est le **partitionnement**. DuckDB sait l'écrire en une instruction, et le relire en n'ouvrant que ce qu'il faut :

```python
con.executescript(f"COPY dwh.vf TO '{TMP}/ventes_part' (FORMAT parquet, COMPRESSION zstd, PARTITION_BY (annee))")
print(sorted(os.path.relpath(f, f"{TMP}/ventes_part") for f in glob.glob(f"{TMP}/ventes_part/*/*")))
lire = f"read_parquet('{TMP}/ventes_part/*/*.parquet', hive_partitioning = true)"
plan = con.df(f"EXPLAIN SELECT SUM(montant_ttc) FROM {lire} WHERE annee = 2025").iloc[0, 1]
print("fichiers ouverts :", re.search(r"Scanning Files: (\d+/\d+)", plan).group(1))
```
<!--sortie-->
```text
['annee=2023/data_0.parquet', 'annee=2024/data_0.parquet', 'annee=2025/data_0.parquet']
fichiers ouverts : 1/3
```

Sur les trois années, **un seul fichier** est ouvert pour la requête de 2025 : c'est l'**élagage des partitions** (*partition pruning*). Le résultat est le même qu'en lisant tout, avec deux tiers de données en moins à lire.

Dans les entrepôts infonuagiques, cette idée a une conséquence **financière**. Selon le service et l'offre, on est facturé en partie ou en totalité au **volume de données lues**. Les bonnes pratiques qui en découlent sont les mêmes partout :

- **ne sélectionner que les colonnes utiles** (`SELECT *` lit toutes les colonnes ; certains services le facturent comme tel) ;
- **filtrer sur la colonne de partition**, pour que les autres partitions ne soient pas lues ;
- **agréger dans des marts** les requêtes répétées par les tableaux de bord, plutôt que de relire chaque fois la table de faits ;
- **vérifier ce qu'une limite de lignes change vraiment** : dans certains services, ajouter `LIMIT 10` n'allège pas la lecture ; c'est à vérifier dans la documentation de votre version.

Les services offrent aussi un **regroupement** (*clustering*) à l'intérieur des partitions (par produit, par exemple), ou des **clés de tri et de distribution**, qui jouent le même rôle : faire en sorte que les lignes qu'une requête cherche soient **voisines**. Voici à quoi ressemble une telle déclaration, à titre **indicatif** (syntaxe d'un dialecte, qui varie d'un service à l'autre ; non exécutée, non vérifiée ici) :

```sql
-- Syntaxe indicative, de type « entrepôt infonuagique » : table partitionnée par date, regroupée par produit
CREATE TABLE ventes (
  id_ligne INT64, date_commande DATE, produit_key INT64, montant_ttc NUMERIC
)
PARTITION BY date_commande
CLUSTER BY produit_key;
```

### 1.5.4 Les quatre services nommés : une comparaison prudente

Le tableau suivant situe les quatre services **par les idées qu'ils partagent et la façon dont ils les organisent**. Il repose sur l'état des connaissances de l'auteur à l'**automne 2026**, **sans exécution** ; les offres, les noms et les tarifs évoluent vite. **À vérifier dans la documentation de votre version avant toute décision.**

| | BigQuery | Snowflake | Redshift | Azure Synapse |
|---|---|---|---|---|
| **Calcul** | sans serveur : la puissance est allouée par le service | entrepôts de calcul **virtuels**, démarrés et arrêtés à la demande | **cluster** de nœuds (une variante sans serveur existe) | pools dédiés (capacité réservée) et pool sans serveur |
| **Facturation (grandes lignes)** | au volume lu, ou à une capacité réservée | au temps d'activité des calculs, selon leur taille | à la taille et à la durée du cluster, ou à l'usage en version sans serveur | à la capacité réservée, ou au volume lu pour le pool sans serveur |
| **Organisation physique** | partitions et regroupement (*clustering*) | découpage automatique, clés de regroupement facultatives | clés de **distribution** et de **tri** | **distribution** (par hachage, tourniquet ou répliquée) |
| **Langage** | SQL, avec des extensions propres | SQL, avec des extensions propres | SQL, très proche de PostgreSQL | SQL (famille T-SQL) |
| **Ce qu'il faut surveiller** | le volume lu par requête | la durée pendant laquelle les calculs restent allumés | le dimensionnement du cluster, le choix des clés | la capacité réservée, le choix de la distribution |

### 1.5.5 Choisir, et choisir à la bonne échelle

Choisir un service ne se fait pas sur une comparaison de fonctions. Les critères réels sont d'autres :

- **l'écosystème existant** : où sont déjà les données, les outils de tableau de bord, les compétences ?
- **le volume et la concurrence** : combien de données, combien de personnes interrogent en même temps ?
- **la gouvernance** : droits d'accès, localisation des données, chiffrement, traçabilité ;
- **la maîtrise du coût** : quelle facturation, quelles alertes, qui surveille ?
- **la réversibilité** : dans quel format sont les données, comment en sortir ?

Et surtout **la bonne échelle**. Notre table de faits de **83 905 lignes** tient dans un fichier de moins d'un mégaoctet (en Parquet) ; un fichier DuckDB, ou une base relationnelle ordinaire, suffit largement à la boutique. Un entrepôt infonuagique se justifie quand le **volume**, le **nombre d'utilisateurs** ou le besoin de **partage** dépassent ce qu'une machine unique sait faire, pas avant. Une organisation peut très bien avoir un entrepôt **bien modélisé** sur un petit outil, et **mal modélisé** sur le plus gros service du marché.


> ✅ **À retenir.**
> - Un entrepôt infonuagique **sépare le stockage du calcul**, range les données **en colonnes** et se facture **à l'usage** (volume lu, temps ou capacité). La **modélisation**, elle, ne change pas.
> - Le **stockage en colonnes** (Parquet) compresse et ne lit que les colonnes demandées ; le **partitionnement** n'ouvre que les fichiers concernés. Cela se démontre en local.
> - On maîtrise le coût en **choisissant les colonnes**, en **filtrant sur la partition**, en **agrégeant dans des marts**.
> - On choisit un service sur l'écosystème, la gouvernance, le coût et la réversibilité ; **la bonne échelle** pour la boutique est un simple fichier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7 et exercice 1.12.


## Bilan du chapitre 1


Vous savez maintenant :

- **expliquer pourquoi on sépare l'analyse de l'exploitation** : charge, historique, intégration des sources, définitions communes, qualité, droits ; et **distinguer** OLTP et OLAP, **ETL** et **ELT**, entrepôt et lac ;
- **organiser un entrepôt en couches** (arrivée, entrepôt, marts, usages) et **ne jamais corriger à la main** : on corrige la règle et l'on rejoue ;
- **construire un schéma en étoile en SQL** : une table de **faits** au centre (une ligne par ligne de commande, 83 905 lignes), des **dimensions** autour (date, client, produit, canal, promotion), des **clés de substitution**, une ligne **« inconnu »** ;
- **vérifier** une construction : mêmes effectifs et mêmes totaux que la source, même résultat par un second outil, même chiffre que la **comptabilité** (écart maximal de 0,49 € sur trente-six mois, à condition de **ne pas arrondir au stockage**) ;
- **déclarer et tester le grain** de chaque table de faits, et **choisir** parmi les trois types : transaction, instantané périodique, cumulative ;
- **reconnaître les mesures additives, semi-additives et non additives** (un stock ne s'additionne pas dans le temps ; un taux ne se moyenne pas) et **stocker des composantes**, pas des rapports ;
- **traiter une mesure d'en-tête** : les frais de port comptés à chaque ligne donnent 75 458 € au lieu de 46 085 € (+ 64 %) ; la solution est une table de faits à son propre grain ;
- **ne jamais joindre deux tables de faits** (le chiffre d'affaires des jardins passe de 295 k€ à 18 millions) : on agrège d'abord, on joint ensuite (*drill-across*), grâce aux **dimensions conformes** ;
- **éviter de perdre des lignes** par une jointure interne (1 571 lignes et 66 521 € d'un coup) : clé 0 et jointure externe ;
- ➕ **choisir un traitement des attributs qui changent** (type 1, 2 ou 3) et le **charger** de façon idempotente ; mesurer ce que le type 1 fausse (jusqu'à 9,4 % par ville, 32 % pour une catégorie reclassée) ;
- ➕ **lire une matrice des processus** et **bâtir des data marts** qui stockent des sommes et des comptes ;
- ➕ **comprendre ce que changent les entrepôts infonuagiques** (stockage et calcul séparés, colonnes, partitions, facturation à l'usage), le démontrer en local avec Parquet, et **choisir à la bonne échelle**.

Le tableau suivant résume les chiffres que nous avons mesurés.

| Question | Résultat |
|---|---|
| Quatre « chiffres d'affaires 2025 » | 1 324 764 € (TTC), 1 103 970 € (hors taxe), 1 034 230 € (net des retours), 1 352 838 € (erreur de jointure) |
| Étoile contre comptabilité | écart maximal de 0,49 € par mois sur 36 mois (2,80 € si l'on arrondit chaque ligne) |
| Frais de port sur trois ans | 46 085 € contre 75 458 € comptés à la ligne |
| Livraisons par transporteur (A, B, C) | 16,0 %, 26,6 % et 51,0 % de retards ; moyenne simple des taux 31,2 %, taux global 26,6 % |
| Jointure interne avec dimension incomplète | 1 571 lignes et 66 521 € perdus |
| Commandes 2025 : somme par catégorie, distinctes | 25 163 contre 12 946 |
| Chiffre d'affaires 2024, Ville A, type 1 contre type 2 | + 5,8 % |
| Fichier Parquet contre CSV | 7,3 fois plus petit ; lire `montant_ttc` seul = 13,8 % du fichier ; un fichier sur trois ouvert pour 2025 |

Le fil conducteur du chapitre tient en une phrase : **un entrepôt est moins une technologie qu'un accord** sur ce que représente chaque ligne, sur ce que mesure chaque chiffre et sur la façon dont les tables se relient. Trois habitudes à retenir :

> 🧭 **En pratique : trois habitudes.**
> 1. **Écrire le grain avant de dessiner la table**, et le tester par une requête.
> 2. **Vérifier toute construction par un total** (source, second outil, comptabilité) : un entrepôt qui n'a pas été rapproché n'est qu'une opinion.
> 3. **Agréger d'abord, joindre ensuite** ; stocker des sommes, recalculer les rapports.

> ⚠️ **Rappel d'honnêteté.** Les données sont **simulées** ; les frais de port sont **calculés** par une règle que nous avons choisie, faute de colonne dans la base d'origine ; l'historique des déménagements et des reclassements est **fabriqué** pour l'exemple. DuckDB joue le rôle de l'entrepôt : aucun service infonuagique n'a été exécuté, et le tableau comparatif de 1.5.4 repose sur des connaissances à vérifier dans la documentation de votre version.

Le chapitre 2 s'intéresse au **trajet** des données : comment les amener dans cet entrepôt **automatiquement, sans doublons et en sachant ce qui s'est passé** quand quelque chose casse. Les idées d'**idempotence**, de **rapprochement** et de **contrôle de chargement** qui ont affleuré ici y deviennent le sujet principal.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.7 (de la définition d'un chiffre d'affaires à un data mart et à un format en colonnes) et exercices 1.1 à 1.12.
