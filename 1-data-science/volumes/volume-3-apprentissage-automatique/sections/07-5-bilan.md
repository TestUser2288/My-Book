## Bilan du chapitre 7

Vous savez maintenant :

- **formuler** un problème de recommandation comme un problème de **classement** (et non de prédiction de notes), distinguer retours **explicites** et **implicites**, et ne pas confondre une case vide avec un refus ;
- manier la **matrice d'interactions creuse** et la **similarité cosinus** (pour des achats binaires, $\cos(i,j)=n_{ij}/\sqrt{n_in_j}$) ;
- construire deux **références** à battre, la **popularité** et le **filtrage par contenu**, et expliquer pourquoi la première est si difficile à dépasser ;
- écrire un **filtrage collaboratif de voisinage** (clients ou produits), le **centrer** quand on dispose de notes, le protéger par **rétrécissement** et en régler le voisinage sur la validation ;
- expliquer la **factorisation matricielle** $R\approx PQ^\top$, son objectif de moindres carrés **régularisés**, les algorithmes **SGD** et **ALS**, la **pondération par la confiance** des retours implicites et la place de la **SVD tronquée** comme référence ;
- **évaluer un classement** avec précision@k, rappel@k, succès@k, MAP@k et NDCG@k, comparer des méthodes avec des **intervalles de confiance appariés**, et regarder au-delà de la précision (**couverture**, **nouveauté**, **diversité**) ;
- reconnaître les pièges propres à la recommandation : le **découpage aléatoire** qui gonfle les résultats quand les données sont datées, le **démarrage à froid** (nouveau client, nouveau produit) et la **boucle de rétroaction** entre recommandations et achats.

Un message à retenir : **sur ce catalogue, une méthode très simple (la popularité) fait déjà presque tout, et la personnalisation n'ajoute que quelques points**, mesurables seulement avec un protocole rigoureux. Le plus souvent, l'essentiel du travail d'un système de recommandation n'est pas l'algorithme, mais la qualité de l'évaluation, la gestion du démarrage à froid et l'exploration qui entretient les données dont il se nourrit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.9 et exercices 7.1 à 7.12.

Le chapitre suivant du volume (chapitre 8, également facultatif) retourne le problème : quand les **étiquettes** manquent ou coûtent cher à obtenir, comment apprendre avec peu d'exemples étiquetés, et lesquels demander en priorité ?
