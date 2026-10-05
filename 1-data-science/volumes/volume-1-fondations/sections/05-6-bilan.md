## Bilan du chapitre 5

Vous savez maintenant :

- **expliquer pourquoi** une base relationnelle vaut mieux qu'un fichier (redondance, incohérence, contraintes, volume, accès simultanés), et lire un schéma : tables, **clés primaires et étrangères**, relations 1–N et N–N ;
- **écrire des requêtes SQL** complètes : `SELECT`, `WHERE`, `ORDER BY`, `GROUP BY`/`HAVING`, **jointures** (`INNER`, `LEFT`, auto-jointure), sous-requêtes, opérations ensemblistes ;
- **éviter les pièges classiques** : priorité de `AND`/`OR`, `NULL` (trois valeurs de vérité, `NOT IN`), dates et `date('now')`, `WHERE` contre `HAVING` ;
- **calculer sans écraser les lignes** grâce aux **fonctions fenêtres** (classements, cumuls, moyennes mobiles, `LAG`/`LEAD`), structurer une requête en **CTE**, et parcourir des hiérarchies par **récursion** ;
- **concevoir un schéma** : dépendances fonctionnelles, 1FN/2FN/3FN, décomposition sans perte, et savoir quand dénormaliser (OLTP contre OLAP, vues, schéma en étoile) ;
- comprendre ce que font les **index** (`EXPLAIN QUERY PLAN`) et les **transactions** (ACID) ;
- (en option) situer les bases **NoSQL** (documents, clé–valeur) et le théorème **CAP**.

> 📒 **Pour s'entraîner.** Le cahier du volume consacre son chapitre 5 à ce chapitre : onze applications guidées (reconstruire la base, importer un CSV, les meilleurs clients, tableaux croisés, clients dormants, segmentation RFM, calendrier, réseaux de parrainage, mesure d'un index, documents JSON et cache) et onze exercices corrigés.

Le chapitre 6 clôt la partie « boîte à outils » avec les habitudes de travail du professionnel : **Git** pour garder l'historique de vos analyses (y compris vos requêtes SQL, qui sont du code comme les autres), les **notebooks Jupyter** pour mélanger code, résultats et explications, et la **ligne de commande** pour tout automatiser. Ensuite, le projet de clôture du volume, proposé dans le cahier, réunira tout ce que vous avez appris, des mathématiques au SQL, dans une seule étude de bout en bout.
