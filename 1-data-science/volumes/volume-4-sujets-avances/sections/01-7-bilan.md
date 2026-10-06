## Bilan du chapitre 1

Vous savez maintenant :

- **calculer à la main** un neurone, une couche et une **rétropropagation** complète sur un petit réseau (et vérifier le résultat par la différentiation automatique et par différences finies) ; **compter** les paramètres d'un réseau ;
- **choisir** une activation et une perte selon la sortie voulue (sigmoïde, softmax, linéaire), **reconnaître** les gradients qui disparaissent et y remédier (ReLU, initialisation de He), **régler** un optimiseur (le pas d'apprentissage reste décisif) et **régulariser** (poids, dropout, arrêt précoce) en jugeant sur plusieurs graines ;
- **expliquer** pourquoi un réseau **convolutif** convient aux images (filtres locaux et partagés, pooling, champ réceptif), **suivre les formes** couche par couche, et **augmenter** les données en respectant l'étiquette ;
- **expliquer** un réseau **récurrent**, la disparition du gradient dans le temps, les **portes** d'un LSTM (avec un pas calculé à la main), et **prévoir** une série en la comparant à un naïf saisonnier et à un boosting à retards, avec un découpage temporel ;
- (en option) **écrire** une boucle d'entraînement PyTorch, fixer les graines, sauvegarder un modèle ; **réutiliser** un réseau pré-entraîné ; **mesurer** une lecture OCR par le taux d'erreur par caractère ; **comparer** un réseau à un boosting sur un tableau avec un test apparié corrigé.

Le tableau suivant résume **ce que nous avons mesuré**, et pas ce que l'on lit dans les articles enthousiastes :

| Problème | Référence simple | Réseau | Verdict mesuré |
|---|---|---|---|
| Chiffres MNIST (8 000 images) | boosting : 95,0 % | réseau dense : 94,5 % ; **réseau convolutif : 96,2 %** | le convolutif fait un peu mieux, avec 5 258 paramètres contre 109 386 |
| Chiffres décalés de 3 pixels | — | convolutif : 72,2 % ; dense : 49,0 % | le convolutif est plus tolérant, sans être invariant |
| Ventes quotidiennes | naïf saisonnier : 27,86 € ; boosting : 21,76 € | LSTM : 20,50 € | le LSTM gagne, sur des données simulées régulières ; plancher de bruit : 17,55 € |
| Résiliation de clients (AUC) | boosting : 0,8959 | réseau : 0,8694 | le boosting fait mieux |
| Chiffres, 2 000 images | régression sur pixels : 87,2 % | ResNet gelé : 92,5 % ; petit CNN : 94,3 % | le transfert aide, mais n'égale pas un petit CNN adapté |

Le fil conducteur du chapitre tient en une phrase : **le deep learning est la bonne réponse quand les données ont une structure** (pixels voisins, suites ordonnées) que l'architecture sait exploiter, et pas nécessairement ailleurs. Dans tous les cas, **la discipline du volume III reste la même** : une référence à battre, un découpage honnête, plusieurs graines, une incertitude annoncée.

Le chapitre 2 aborde le **texte** : comment un réseau représente les mots par des plongements (l'idée vue en 1.6), le mécanisme d'**attention** et les modèles de langage ; le chapitre 4 reprend l'**export** et la **mise en production** d'un modèle comme ceux de ce chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (rétropropagation en `numpy`, optimiseurs, régularisation, convolution à la main, augmentation de données, LSTM contre GRU, OCR de factures inclinées, réseau contre boosting selon la taille des données) et exercices 1.1 à 1.12.
