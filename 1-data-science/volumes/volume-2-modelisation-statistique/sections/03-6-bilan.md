## Bilan du chapitre 3

Vous savez maintenant :

- **résumer** un tableau de variables numériques par une **ACP** : l'écrire comme la diagonalisation de la matrice de covariance (ou la SVD du tableau centré), choisir entre covariance et corrélation (**standardiser** quand les unités diffèrent), choisir le nombre de composantes (éboulis, Kaiser, **analyse parallèle**), lire saturations, scores et biplot, et mesurer ce que l'on perd (somme des valeurs propres jetées) ;
- distinguer l'ACP, qui **résume**, de l'**analyse factorielle**, qui **modélise** les corrélations par des facteurs cachés ($\Sigma=\Lambda\Lambda^\top+\Psi$) ; estimer, **tester l'ajustement**, choisir le nombre de facteurs, **faire tourner** les axes (varimax) sans changer l'ajustement, et construire des échelles de mesure (alpha de Cronbach) ;
- **classer sans étiquettes** : les **k-means** (algorithme de Lloyd, k-means++, minimum local), la **classification hiérarchique** (critères d'agrégation, dendrogramme) ; **choisir $k$** (coude, silhouette) et surtout **vérifier qu'il y a des groupes** (silhouette, stabilité par bootstrap et ARI) ;
- (en option) étendre l'idée aux **variables qualitatives** par l'**analyse des correspondances** (SVD des résidus standardisés, inertie $=\chi^2/n$) et l'**ACM** ;
- (en option) passer des groupes inconnus aux groupes connus avec l'**analyse discriminante** : règle de Bayes avec des classes gaussiennes, LDA (frontières linéaires) et QDA, lien avec la **régression logistique**, projection de Fisher.

Un fil rouge traverse le chapitre : **une méthode descriptive rend toujours un résultat**, même sur du bruit. Un axe, un facteur, un groupe, une carte n'ont de valeur qu'accompagnés de leurs **diagnostics** (parts d'inertie et analyse parallèle, test d'ajustement, silhouette et stabilité, khi-deux avant de lire une carte).

Le chapitre 4 change d'horizon : après les données « en coupe » (un instantané de clientes), les **séries temporelles**, où l'ordre des observations compte et où la mémoire du passé devient l'information principale. Les ventes mensuelles de la boutique, de 2016 à 2025, nous y attendent.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.5 et exercices 3.1 à 3.14, tous corrigés.
