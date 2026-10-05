## Bilan du chapitre 8

Vous savez maintenant :

- **situer** les deux familles de méthodes qui répondent au problème de l'**étiquette chère** : le **semi-supervisé**, qui exploite les données déjà disponibles mais sans étiquette, et l'**apprentissage actif**, qui choisit quelles étiquettes acheter ;
- **énoncer** les hypothèses qui permettent aux points sans étiquette d'aider (lissage, groupes, basse densité, variété), voir sur un exemple à la main comment un déplacement de frontière en résulte, et **reconnaître les cas où elles nuisent** (classes qui se chevauchent, étiquettes déséquilibrées, variables hétérogènes) ;
- **évaluer honnêtement** une méthode par une **courbe d'apprentissage selon le budget d'étiquettes** : jeu de test aléatoire et fixe, tirages répétés, **mêmes étiquettes** pour toutes les méthodes, comparaison au supervisé seul ;
- **expliquer** l'**auto-apprentissage** et son biais de confirmation, le **co-apprentissage** et ses conditions, et la **propagation d'étiquettes** (diffusion sur un graphe, solution fermée $F^*=(1-\alpha)(I-\alpha S)^{-1}Y$, minimisation d'un critère de lissage et de fidélité), la calculer **à la main** sur six nœuds ;
- **diagnostiquer** par l'**homophilie** (part de voisins de même étiquette) si un graphe a des chances d'aider : oui sur les chiffres (97 %), non sur les clients de la boutique (80,5 % contre 75,9 % au hasard) ;
- **écrire** la boucle d'apprentissage actif, **calculer** les critères d'incertitude (confiance minimale, **marge**, entropie), le **comité** et la pondération par la **densité**, et mesurer lequel est le meilleur *sur votre problème* (chiffres : la marge, 80 étiquettes pour 0,90 au lieu de 130) ;
- **éviter** les pièges de l'apprentissage actif : jeu étiqueté non représentatif et probabilités faussées (0,078 prédit pour 0,14 réel), jeu de test à tirer au hasard, **démarrage à froid** ;
- **raisonner en coût** : économie d'étiquettes contre coût de recalibrage, et règle d'arrêt « continuer tant que le gain attendu vaut plus que le coût ».

Deux messages à garder. **Le semi-supervisé et l'actif ne sont pas des baguettes magiques** : chacun repose sur une hypothèse sur les données, et la seule façon de savoir si elle tient est de **mesurer** à budget d'étiquettes égal. Et **les données ne sont pas des étiquettes** : tout le travail de ce chapitre vient de ce qu'on sait *faire* de ce qu'on possède (la structure) et de ce qu'on *décide d'acheter* (les étiquettes).

> 📒 **Pour s'entraîner.** Cahier, chapitre 8 : applications 8.1 à 8.8 et exercices 8.1 à 8.12.

Le chapitre 9, également facultatif, change de décor : au lieu d'apprendre à partir d'exemples étiquetés, un agent apprend à **décider** en interagissant avec un environnement, c'est l'apprentissage par renforcement. Les bandits manchots y retrouvent une idée de ce chapitre : choisir *quoi essayer* pour apprendre le plus vite.
