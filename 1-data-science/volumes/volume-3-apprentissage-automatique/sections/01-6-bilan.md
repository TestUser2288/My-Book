## Bilan du chapitre 1

Vous savez maintenant :

- **formuler** un problème d'apprentissage : la ligne du tableau, la **date de prédiction**, la cible et le moment où elle est connue ; distinguer la **perte** que l'algorithme minimise de la **métrique** qui guide la décision ;
- **démontrer** pourquoi l'erreur d'entraînement est optimiste, et **séparer les données** en trois rôles (entraînement, validation, test) selon un schéma adapté (aléatoire, stratifié, groupé, temporel) ;
- **repérer et éviter la fuite d'information** : variable connue après la date de prédiction (le mirage de 0,89 à 0,92 d'AUC), prétraitement ou sélection de variables hors du pipeline (0,88 d'AUC sur du pur bruit) ;
- **estimer** une performance par **validation croisée** : choisir $k$ (5 ou 10), la stratifier, la grouper ou la rendre temporelle, et savoir que l'**écart-type entre plis n'est pas une barre d'erreur** ;
- **décomposer** l'erreur en bruit, biais carré et variance, **diagnostiquer** sous-apprentissage et surapprentissage sur une courbe de complexité et une **courbe d'apprentissage**, et en tirer les remèdes ;
- **se comparer à une référence** (naïve, règle métier, modèle simple), **comparer deux modèles avec un intervalle** (test $t$ corrigé, McNemar, bootstrap), tenir compte de la variabilité des graines, et n'ouvrir le jeu de test qu'**une fois** ;
- (en option) **régler des hyperparamètres** (grille, recherche aléatoire, TPE avec Optuna, arrêt précoce) **sans s'auto-persuader**, grâce à la validation croisée imbriquée.

Le fil conducteur du chapitre tient en une phrase : **un modèle vaut ce que vaut la façon dont on l'a évalué**. Sur un même jeu de données, on peut annoncer 0,92 ou 0,89 d'AUC (fuite ou pas), 3,5 ou 7 d'erreur (validation aléatoire ou temporelle), 0,66 ou 0,53 (réglage optimiste ou honnête) : la différence n'est pas dans le modèle, mais dans la **discipline**.

Le chapitre 2 apporte les modèles : de la régression logistique revue comme un problème d'optimisation aux **arbres**, aux **forêts aléatoires** et au **gradient boosting**, qui s'est imposé comme la référence sur les tableaux de données. Chacun sera évalué avec les règles de ce chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.9 (fuite d'information, loterie du découpage, choix de $k$, série temporelle, biais-variance, courbes d'apprentissage, comparaison rigoureuse, recherche d'hyperparamètres, validation imbriquée) et exercices 1.1 à 1.12.
