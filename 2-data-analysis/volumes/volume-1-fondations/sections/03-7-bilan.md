## Bilan du chapitre 3

Vous savez maintenant :

- **lire une base relationnelle** : tables, grain (ce que représente une ligne), clés primaires et étrangères, types, et pourquoi une base bien conçue **déclare** ses clés ;
- **interroger une table** avec `SELECT`, `WHERE` (comparaisons, `IN`, `LIKE`, `BETWEEN`, précédence de `AND` et `OR`), `ORDER BY`, `LIMIT` et `DISTINCT`, calculer des colonnes avec `CASE` et des fonctions de date ;
- **agréger** avec `COUNT`, `SUM`, `AVG`, `MIN`, `MAX`, `GROUP BY` et `HAVING`, connaître l'**ordre logique d'exécution** (`FROM`, `WHERE`, `GROUP BY`, `HAVING`, `SELECT`, `ORDER BY`, `LIMIT`) et la règle d'or du regroupement ;
- **gérer les valeurs absentes** (`NULL`, logique à trois valeurs, `COALESCE`, `NULLIF`) et éviter quatre pièges silencieux : la division entière, la moyenne des moyennes, `BETWEEN` sur des horodatages, `LIMIT` sans `ORDER BY` ;
- **joindre des tables** (`INNER`, `LEFT`, `FULL`, `CROSS`, auto-jointure), écrire une **anti-jointure** pour trouver ce qui manque, placer un filtre au bon endroit (`ON` ou `WHERE`), joindre sur une clé composée et **empiler ou comparer des ensembles** (`UNION ALL`, `INTERSECT`, `EXCEPT`) ;
- **repérer la multiplication des lignes** après une jointure un-à-plusieurs et l'éviter (agréger avant de joindre, compter des éléments distincts, appliquer le test des trois comptes) ;
- **calculer sans perdre le détail** avec les fonctions fenêtres : parts, classements (`ROW_NUMBER`, `RANK`, `DENSE_RANK`), comparaisons avec la ligne précédente (`LAG`, `LEAD`), cumuls, moyennes mobiles, tranches (`NTILE`) ;
- **structurer une requête complexe** en CTE nommées, par une méthode en six étapes (question, grain, sources, jointures, filtres et agrégats, vérification), fabriquer un calendrier par une CTE récursive, et **vérifier un résultat par un second outil** ;
- (en option) **utiliser sous-requêtes, index, vues, transactions, déclencheurs**, lire un plan d'exécution, se protéger de l'injection SQL, et **situer les dialectes** de PostgreSQL, MySQL, SQL Server et Oracle.

Le chapitre a mis des chiffres sur les questions que la gérante posait en passant dans le couloir. Tous viennent de requêtes réellement exécutées sur la base de la boutique :

| Question | Résultat mesuré |
|---|---|
| Quel chiffre d'affaires en 2025 ? | 1 324 764 € (retrouvé par quatre chemins : somme par catégorie, cumul d'une fenêtre, CTE, pandas) |
| Que pèsent nos dix meilleurs clients ? | 24 886 €, soit **1,88 %** du chiffre d'affaires de 2025 |
| La clientèle est-elle concentrée ? | les 10 % de clients qui dépensent le plus : 32,9 % du chiffre d'affaires ; les 20 % premiers : 51,9 % |
| Combien de clients n'ont jamais commandé ? | 1 194 sur 6 000 (un sur cinq) |
| Fidélité en 2025 | 3 133 clients fidèles, 742 nouveaux, 931 perdus depuis 2024 |
| Quel est l'écart typique entre deux commandes d'un client ? | 86,4 jours en moyenne |
| D'où viennent les retours ? | site : 8,8 % des lignes ; boutique : 3,3 % |
| Quand vend-on le plus ? | décembre (+27,8 % sur novembre) ; le samedi |
| Que coûte une jointure mal écrite ? | le budget publicitaire de 75 995 € devient 2 991 731 € après jointure sur la date : près de **quarante fois** trop |

Le fil conducteur du chapitre tient en une phrase : **une requête est une description précise du tableau que l'on veut, et la précision commence par le grain**. Toutes les erreurs sérieuses vues ici (doubles comptages, filtres qui disparaissent, divisions entières, jours manquants) sont des erreurs de grain : on croyait compter des commandes, on comptait des lignes ; on croyait garder tous les clients, on les filtrait ; on croyait moyenner des paniers, on moyennait des moyennes. Avant chaque requête, écrivez en une phrase ce que représentera **une ligne du résultat** ; après chaque requête, **vérifiez un total** par un autre chemin.

Le chapitre 4 reprend ces mêmes questions avec deux autres langages d'analyse, **Python (pandas)** et **R (tidyverse)**. Vous y retrouverez, sous une autre écriture, les filtres, les regroupements, les jointures et les fenêtres de ce chapitre ; le SQL reste l'outil de choix pour **extraire et résumer** les données à la source, et pandas ou R prennent le relais pour **explorer, modéliser et dessiner**.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.9 (découvrir la base, ventes par canal, meilleurs clients, paniers et doubles comptages, retours, évolution mensuelle, fidélité et cohortes, segmentation RFM, index et plans d'exécution) et exercices 3.1 à 3.14, tous corrigés.

```python hide
con.close()
shutil.rmtree(TMP3, ignore_errors=True)
```
