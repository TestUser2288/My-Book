## Bilan du chapitre 1

Vous savez maintenant :

- **écrire et résoudre** un modèle linéaire $\mathbf y=\mathbf X\boldsymbol\beta+\boldsymbol\varepsilon$ par les équations normales, comprendre pourquoi la solution est une **projection orthogonale** et démontrer le théorème de **Gauss-Markov** ;
- **interpréter** les coefficients (variables qualitatives par indicatrices, « toutes choses égales par ailleurs », modèles en logarithmes, rétro-transformation pour prédire une moyenne) ;
- **faire de l'inférence** : erreurs standard, tests $t$ et $F$ de modèles emboîtés, intervalles de confiance et de **prédiction**, bootstrap des couples, en sachant sous quelles hypothèses ils sont valables ;
- **poser un diagnostic** : graphiques de résidus, tests de Breusch-Pagan et de Durbin-Watson, **levier** et **distance de Cook**, **VIF**, erreurs standard robustes, et savoir remédier aux défauts (transformer, centrer, changer de modèle) ;
- **choisir un modèle** sans tricher : AIC, BIC, validation croisée (PRESS), tests emboîtés, et se méfier de la sélection automatique ;
- (en option) **régulariser** (Ridge, Lasso, Elastic Net) quand les variables sont nombreuses, **résister** aux aberrations (Huber, régression quantile) et **modéliser des données groupées** (effets mixtes, rétrécissement).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : les applications 1.1 à 1.12 et les exercices corrigés 1.1 à 1.13 reprennent, dans l'ordre du chapitre, tout ce qui est à pratiquer.

Le chapitre 2 généralise la régression à des réponses qui ne sont **ni continues ni normales** : un client rachète-t-il (oui/non) ? combien de commandes passe-t-il (un entier) ? C'est le cadre des **modèles linéaires généralisés**, dont la régression linéaire de ce chapitre est le cas particulier le plus simple.
