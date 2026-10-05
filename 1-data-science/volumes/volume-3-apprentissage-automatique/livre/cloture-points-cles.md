# Points clés

> « Un modèle vaut ce que vaut la façon dont on l'a évalué. »

Ce court chapitre fixe l'essentiel du volume, chapitre par chapitre, puis les idées qui les relient. Le **projet du volume** (un pipeline complet sur un jeu de données réel) et une **auto-évaluation** de quarante questions se trouvent dans le cahier.

> 📒 **Pour s'entraîner.** Cahier, projet du volume et auto-évaluation : onze étapes, du cadrage à l'équité, puis quarante questions avec corrigés.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. La démarche** | Un problème d'apprentissage se formule par la **ligne du tableau**, la **date de prédiction** et la **cible**. On sépare **entraînement, validation et test** ; on évite la **fuite d'information** (une variable connue après la prédiction, un prétraitement hors pipeline). La **validation croisée** estime la performance, mais l'écart-type entre plis n'est pas une barre d'erreur. L'erreur se décompose en **bruit, biais² et variance** ; on se compare à une **référence**, avec des **différences appariées**, et on n'ouvre le test qu'**une fois**. ➕ Le réglage des hyperparamètres demande une validation croisée **imbriquée**. |
| **2. Apprentissage supervisé** | Un modèle = une **famille de fonctions**, une **perte**, un **algorithme**. Un **arbre** écrit des seuils et des interactions mais il est instable ; une **forêt** moyenne des arbres décorrélés (variance $\rho\sigma^2+\frac{1-\rho}B\sigma^2$) ; le **gradient boosting** est une descente de gradient dans l'espace des fonctions. Sur nos données, les modèles à arbres battent la logistique parce que le problème contient des seuils et des interactions : **pas parce qu'ils sont plus sophistiqués**. |
| **3. Non supervisé** | Une méthode non supervisée **rend toujours un résultat**. On le valide par **plusieurs épreuves** (critères internes, référence sans structure, stabilité, vérité externe si elle existe). L'échelle et le choix des variables décident des groupes. **Réduire n'est pas neutre** : l'erreur de reconstruction se mesure. ➕ t-SNE et UMAP préservent le voisinage, pas les distances globales. |
| **4. Variables et déséquilibre** | **Ce qui apprend, apprend sur l'entraînement, et rien que lui** : encodage par la cible, imputation, mise à l'échelle, sélection, rééchantillonnage vivent dans un `Pipeline`. Un modèle simple muni de bonnes variables peut égaler un modèle flexible. Face au déséquilibre, **poids et rééchantillonnage déplacent les probabilités sans améliorer le classement** ; le **seuil se choisit par les coûts**. |
| **5. Évaluation, calibration, interprétabilité** | Une métrique ne vaut que par la **décision** qu'elle sert : AUC pour classer, **précision moyenne** quand la classe est rare, **Brier** pour les probabilités, **coûts** pour décider. On **vérifie la calibration** et on la répare sur un jeu séparé. On **explique** (permutation, PDP/ICE, LIME, SHAP) sans confondre description du modèle et causalité. ➕ L'équité obéit à des critères qui ne peuvent pas tous être satisfaits ; la prédiction conforme donne une garantie de couverture. |
| **➕ 6. Anomalies** | Sous déséquilibre extrême, **l'exactitude ne veut rien dire** ; on évalue par précision moyenne et budget d'alertes. Distances, densités, forêt d'isolement, autoencodeurs détectent des fraudes différentes ; un détecteur supervisé reste le meilleur quand les étiquettes existent. |
| **➕ 7. Recommandation** | On **classe** plus qu'on ne prédit des notes. La **popularité** est une référence redoutable ; la personnalisation (voisinage, factorisation) ajoute quelques points. Protocole d'évaluation, démarrage à froid et boucles de rétroaction comptent plus que l'algorithme. |
| **➕ 8. Semi-supervisé et actif** | Ni l'un ni l'autre n'est une baguette magique : chaque méthode repose sur une **hypothèse sur les données** qu'il faut **mesurer** à budget d'étiquettes égal. Un jeu étiqueté par apprentissage actif **n'est pas représentatif**. |
| **➕ 9. Renforcement** | Agir et apprendre sont indissociables : les données dépendent des décisions. **Explorer a un prix** (le regret) ; la **récompense est le cahier des charges** de l'agent. |
| **Projet (cahier)** | Cadrer → auditer → séparer et fixer des références → variables → comparer avec incertitude → régler → décider par les coûts → calibrer → évaluer **une fois** → expliquer et auditer l'équité → rapporter ses limites. |

## Six idées qui traversent tout le volume

> 💡 **Les six idées.**
> 1. **L'erreur d'entraînement est optimiste.** Seule l'erreur sur des données que le modèle n'a jamais vues dit quelque chose de l'avenir.
> 2. **Le jeu de test est sacré.** Chaque fois qu'il influence une décision, il devient un jeu de validation.
> 3. **La fuite d'information est l'erreur la plus fréquente et la plus coûteuse.** Elle se détecte par la question : « *quand cette valeur est-elle connue ?* »
> 4. **On bat d'abord une référence simple.** Un modèle plus riche doit justifier son surcroît de complexité par un gain *mesuré, avec son incertitude*.
> 5. **La métrique doit correspondre à la décision.** L'AUC, l'exactitude et le seuil de 0,5 répondent à trois questions différentes ; la bonne est souvent en euros.
> 6. **Interprétabilité et équité font partie de l'évaluation.** Un modèle que l'on ne sait pas expliquer, ou qui traite mal certains groupes, n'est pas terminé.

## Et maintenant ?

Vous savez maintenant **construire, évaluer et expliquer** un modèle prédictif de façon rigoureuse. Le **volume IV : sujets avancés et modernes** prolonge ce travail vers les réseaux de neurones profonds, le traitement du langage et les modèles de langage, et le calcul distribué sur de gros volumes de données. Ces méthodes changent d'échelle et de matière première, pas d'exigence : tout ce que vous avez appris ici sur la **validation**, la **fuite d'information**, la **calibration** et l'**interprétabilité** y reste indispensable, souvent plus difficile à appliquer.

> ✅ **À retenir, tout simplement.** Le modèle n'est qu'une étape. Ce qui fait la qualité d'un projet d'apprentissage automatique, c'est la rigueur avec laquelle on a posé la question, séparé les données, mesuré l'erreur et dit honnêtement ce que l'on ne sait pas.
