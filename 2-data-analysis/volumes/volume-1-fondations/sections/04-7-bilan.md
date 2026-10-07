## Bilan du chapitre 4

Vous savez maintenant :

- **lire** un fichier avec le bon séparateur, la bonne décimale, le bon encodage et les bonnes dates, en Python (`read_csv`) comme en R (`read_csv`, `read_delim`) ; **remettre en état** un export désordonné (titres, total, en-têtes répétés, manquants, textes) et **réconcilier** le résultat avec un total connu ;
- **sélectionner**, **filtrer**, **calculer**, **trier** et **compter** avec pandas (`[]`, `.loc`, `.iloc`, `query`, `assign`, `value_counts`) et avec le tidyverse (`select`, `filter`, `mutate`, `arrange`, `count`), et traduire un langage dans l'autre ;
- **regrouper** (`groupby` et `agg`, `group_by` et `summarise`, `transform` pour les parts), **joindre** sans multiplier les lignes (`validate`, `relationship`) et **restructurer** entre format large et format long (`pivot_table`, `melt`, `pivot_wider`, `pivot_longer`) ;
- **comparer** des périodes avec des moyennes glissantes et des semaines ISO, et **écrire une fonction** qui produit le tableau du lundi ;
- **ranger** une analyse dans un notebook **reproductible** (état caché, « tout exécuter »), produire un rapport avec R Markdown ou Quarto, et reconnaître le moment où passer du notebook au script ;
- (en option) **dessiner** avec `ggplot2` (couches, facettes), tester la logique d'une application Shiny, **vectoriser** un calcul avec NumPy, lire un fichier avec polars, convertir un notebook en rapport HTML.

Le chapitre a mis des chiffres sur la boutique, et chacun a été **obtenu de deux façons** :

| Question | Ce que nous avons mesuré |
|---|---|
| Chiffre d'affaires de 2025 | 1 324 763,72 €, identique en pandas et en R |
| Export de caisse | 285 lignes lues, 280 ventes retenues, 8 montants à reconstituer ; écart de 2,62 € avec le total, expliqué par une remise de 5 % |
| Panier moyen par canal | 100,9 € (boutique), 100,5 € (réseaux), 99,8 € (Site) ; le montant moyen **d'une ligne** est de 43,5 € |
| Part du Site dans le chiffre d'affaires | de 37,1 % en 2023 à 46,6 % en 2025 ; le Site passe devant la boutique en septembre 2024 |
| Taux de retour par canal | 3,1 % (boutique), 6,7 % (réseaux), 9,0 % (Site) ; 221 010 € remboursés, soit 6,05 % du chiffre d'affaires |
| Tableau du lundi, semaine 45 de 2025 | 30 240,0 € contre 27 729,4 € (+9,1 %) ; boutique −9,6 %, Site +16,6 %, réseaux +60,4 % sur une petite base |
| Notebook | le même code donne 90 ou 80 selon l'ordre d'exécution des cellules |

Trois idées dépassent ce chapitre. **D'abord, écrire une analyse comme un programme la rend refaisable** : la gérante obtient son tableau chaque lundi, vous gagnez une heure, et l'erreur de ligne de la collègue disparaît. **Ensuite, la vérification croisée est un réflexe** : un chiffre obtenu par deux outils indépendants (pandas et R, la base et l'export de caisse) mérite confiance ; un écart est une information. **Enfin, un pourcentage sans le montant qui le porte, ou une moyenne sans la précision de ce qui est moyenné, trompe** : la moyenne d'une ligne n'est pas celle d'une commande, et +60 % sur une petite base n'est pas une tendance.

> 🧭 **En pratique : liste de contrôle avant de livrer un chiffre.**
> 1. Les données ont été **lues avec les bons arguments**, et on les a **regardées** (`head`, `dtypes`, `glimpse`).
> 2. Les **manquants** ont été comptés, et l'on sait pourquoi ils manquent.
> 3. Chaque **jointure** a été validée (`validate`, `relationship`) : le nombre de lignes n'a pas bougé sans raison.
> 4. Un **total connu** a été retrouvé (un export, un tableau de bord, un autre outil).
> 5. Le calcul a été **refait** dans un second outil, ou par une seconde méthode.
> 6. Le notebook ou le script s'exécute **de haut en bas** dans une session neuve.
> 7. Le chiffre est accompagné de **ce qu'il mesure** (moyenne de quoi, sur quelle période, avec quelle base).

Le chapitre 5 clôt ce volume en remontant à la source : **d'où viennent les données** ? Il décrit les types de données et leurs niveaux de mesure, les grandes familles de sources, et la conception d'une enquête, de l'enquête de satisfaction de la boutique à ses biais.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.10 (premier contact avec pandas, filtres, traduction en tidyverse, export de caisse, jointure et marge, restructuration, tableau du lundi, notebook reproductible, ggplot2, polars et NumPy) et exercices 4.1 à 4.13.
