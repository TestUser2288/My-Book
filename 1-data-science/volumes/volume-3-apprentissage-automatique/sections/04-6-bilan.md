## Bilan du chapitre 4

Vous savez maintenant :

- **préparer les variables selon le modèle** : encoder une variable qualitative (disjonctif, ordinal, fréquence, cible), mettre à l'échelle (standardisation, min-max, robuste, quantile) quand le modèle compare des distances ou pénalise des coefficients, corriger l'asymétrie (logarithme, Box-Cox, Yeo-Johnson) quand cela aide vraiment, et **savoir que les arbres n'en ont pas besoin** ;
- **encoder par la cible sans fuite** : calcul hors pli et lissage, et pourquoi le calcul naïf transforme du bruit en « signal » (AUC de 0,678 à l'entraînement, 0,510 au test) ;
- **traiter les valeurs manquantes** en comprenant leur mécanisme (MCAR, MAR, MNAR, structurel), ajouter un **indicateur d'absence** quand l'absence est informative, et ne jamais imputer avant la séparation ;
- **assembler un `Pipeline`** avec `ColumnTransformer`, pour que tout ce qui est appris le soit sur les plis d'entraînement seulement ;
- **fabriquer des variables métier** (ratios, taux, RFM, indicateurs de situation, interactions, variables cycliques), **découvrir des seuils sur l'entraînement**, et comprendre qu'un modèle simple muni des bonnes variables peut égaler un modèle flexible (0,900 d'AUC pour la logistique enrichie, comme pour le boosting) ;
- **repérer la fuite d'information** par la question « quand cette valeur est-elle connue ? » : aucune statistique ne la détecte à coup sûr ;
- **traiter des classes déséquilibrées** : ne jamais juger sur l'exactitude, lire précision, rappel et PR-AUC, comprendre que **poids et rééchantillonnage déplacent les probabilités et le seuil** sans améliorer le classement, et choisir le **seuil par les coûts** ($s^\star=\frac{c_{FP}}{c_{FP}+c_{FN}}$) sur des prédictions hors pli ;
- (en option) **comparer les méthodes de sélection** (filtre, enveloppe, intégrée), préférer l'importance par **permutation**, et **mettre la sélection dans la validation croisée** ; **utiliser SMOTE et ses variantes** dans un pipeline, en sachant qu'il n'améliore pas toujours, et qu'appliqué avant la validation il produit des scores absurdes.

Le fil rouge du chapitre tient en une phrase : **ce qui apprend, apprend sur l'entraînement, et rien que lui**. Encodage par la cible, imputation, mise à l'échelle, choix de seuils, sélection de variables, rééchantillonnage : cinq façons de tricher par inadvertance, que le `Pipeline` et la validation croisée rendent impossibles quand on les utilise correctement.

Le chapitre 5 aborde la question qui conclut toute modélisation : **comment juger un modèle, lui faire confiance et l'expliquer ?** Métriques adaptées au problème, calibration des probabilités, interprétabilité (importance par permutation, SHAP, LIME), puis équité et incertitude.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.8 et exercices 4.1 à 4.14.
