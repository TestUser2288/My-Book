## 1.1 Concepts d'entrepôt de données

Avant de dessiner la moindre table, il faut comprendre **pourquoi** on ne répond pas aux questions d'analyse directement sur la base qui sert à encaisser les commandes. Cette section pose le vocabulaire (OLTP, OLAP, couches, ETL, ELT, lac) et les raisons de séparer l'exploitation de l'analyse.

```python hide
import os, sys
import numpy as np
import pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as O

nb = {t: con.df(f"SELECT COUNT(*) AS n FROM src.{t}")["n"][0] for t in ["commandes", "lignes_commande", "produits", "clients"]}
assert nb == {"commandes": 36395, "lignes_commande": 83905, "produits": 120, "clients": 6000}
```

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

```python hide
O.fig_couches()
```
<!--sortie-->
```text
figure : ch01-couches.png
```

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
