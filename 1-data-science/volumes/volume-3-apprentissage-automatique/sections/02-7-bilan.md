## Bilan du chapitre 2

Vous savez maintenant :

- **décrire** un modèle supervisé par ses trois ingrédients (famille de fonctions, perte, algorithme), comprendre pourquoi on remplace le coût 0-1 par un substitut convexe (logistique, charnière), et **calculer à la main** un pas de descente de gradient ;
- expliquer pourquoi la descente de gradient et les pénalités exigent des variables **à l'échelle**, et voir la pénalité $\ell_2$ ou $\ell_1$ comme une **contrainte** (disque ou losange) ;
- **construire un arbre** à la main (impureté de Gini ou entropie, meilleur seuil, gain), le régler (profondeur, taille des feuilles, élagage par coût-complexité) et dire **ce qu'il sait écrire** (seuils, interactions) et **ce qui le fragilise** (l'instabilité) ;
- démontrer que la **variance d'une moyenne** de prédictions corrélées vaut $\rho\sigma^2+\frac{1-\rho}B\sigma^2$, en déduire le **bagging** et les **forêts aléatoires**, utiliser l'erreur **hors sac**, et **se méfier de l'importance par impureté** ;
- voir le **gradient boosting** comme une descente de gradient dans l'espace des fonctions (pseudo-résidu $-\partial\ell/\partial F$), calculer à la main une valeur de feuille et un gain de coupe **XGBoost**, régler le pas et le nombre d'arbres par **arrêt précoce**, et profiter des valeurs manquantes et des catégories natives de **LightGBM** ;
- **comparer** plusieurs familles sur les mêmes données avec une **différence appariée** et son incertitude, en gardant un modèle de référence simple ;
- (en option) comprendre la **marge** et l'astuce du **noyau** des SVM, le **fléau de la dimension** des k-NN, l'indépendance du **Bayes naïf**, l'**encodage ordonné** de CatBoost et le **stacking sans fuite**.

Sur la résiliation, la hiérarchie obtenue est la suivante, en AUC sur le jeu de test :

| Modèle | AUC |
|---|---|
| Régression logistique (référence) | 0,866 |
| Arbre de décision réglé | 0,885 |
| Forêt aléatoire | 0,896 |
| Gradient boosting | 0,903 |

Trois leçons dépassent ce chapitre. **Un modèle plus riche n'est pas toujours meilleur** : l'avantage des arbres ici vient des seuils et des interactions du problème, et ne serait pas apparu sur des données lisses. **L'évaluation prime sur l'algorithme** : jeu de test intact, validation croisée dans l'entraînement, comparaisons appariées, modèle de référence. Enfin, **chaque fois que l'on réutilise des étiquettes** (encodage par la cible, empilement), la fuite d'information guette.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.10 et exercices 2.1 à 2.12.

Le chapitre 3 quitte le monde des étiquettes : que peut-on apprendre des clients quand on ne sait pas ce que l'on cherche ? Le chapitre 4 reviendra sur la préparation des variables (encodage, échelle, déséquilibre), et le chapitre 5 sur l'évaluation fine des modèles (calibration, interprétabilité) que nous avons ici seulement effleurée.
