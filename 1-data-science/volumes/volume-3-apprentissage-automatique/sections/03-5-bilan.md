## Bilan du chapitre 3

Vous savez maintenant :

- **juger un découpage sans bonne réponse** : critères internes (inertie, silhouette, Calinski–Harabasz, Davies–Bouldin), comparaison à une **référence sans structure** (silhouette comparée, statistique de l'écart, avec l'importance du choix de la référence), **stabilité** par sous-échantillonnage, **indice de Rand ajusté** et information mutuelle normalisée quand une vérité existe, et surtout **utilité** des groupes pour une décision ;
- repérer ce qui décide du résultat avant l'algorithme : l'**échelle** des variables (un ARI de $0{,}49$ tombe à $0{,}08$ sans standardisation) et le **choix des variables** ;
- expliquer la **malédiction de la dimension** (les distances se resserrent en $1/\sqrt d$) et choisir une méthode de réduction : **ACP** (erreur de reconstruction = un moins la variance gardée, théorème d'Eckart–Young), **ACP à noyau** pour le non-linéaire, **SVD tronquée** pour le parcimonieux, **NMF** pour des parties lisibles, **projections aléatoires** et lemme de **Johnson–Lindenstrauss** ;
- fixer le nombre de dimensions par l'**utilité en aval**, validée par validation croisée ;
- (en option) utiliser **DBSCAN** (groupes denses, bruit explicite, rayon $\varepsilon$ unique), les **liens** de la classification hiérarchique (le lien simple retrouve des formes allongées), et les **mélanges gaussiens** estimés par **EM** (appartenances probabilistes, BIC) ;
- (en option) dessiner des données en haute dimension avec **t-SNE** et **UMAP**, mesurer leur **fiabilité**, et **ne pas lire** distances entre groupes, tailles et formes fines.

Trois messages à garder en mémoire. **Un résultat non supervisé se valide par plusieurs épreuves qui se rejoignent**, jamais par un seul chiffre. **Une méthode rend toujours un résultat** : la référence sans structure est votre meilleur garde-fou. Et **réduire n'est pas neutre** : son effet se mesure, il ne se suppose pas.

Le chapitre 4 revient aux **modèles supervisés** par l'angle le plus concret : les variables. Avant d'entraîner un modèle, il faut les encoder, les mettre à l'échelle, les fabriquer, les sélectionner, et composer avec des classes déséquilibrées. Beaucoup de gains en apprentissage automatique se jouent là.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.8, exercices 3.1 à 3.12.
