## Bilan du chapitre 6

Vous savez maintenant :

- **distinguer** anomalie ponctuelle, contextuelle et collective, et **ne pas confondre** anomalie (fait statistique) et fraude (fait métier) ;
- **expliquer** pourquoi l'apprentissage supervisé suffit rarement (déséquilibre extrême, délai des étiquettes, adversaire qui s'adapte, fraudes inédites, étiquettes biaisées) et quand il reste le meilleur choix ;
- **évaluer un détecteur sous déséquilibre extrême** : l'exactitude est trompeuse (99,19 % pour un détecteur inutile), la formule de Bayes explique pourquoi la précision est faible, la **courbe précision-rappel** et l'**AP** remplacent la ROC, et le **budget d'alertes** et le **coût** fixent le seuil ;
- **utiliser le z-score** et sa version **robuste** (médiane, MAD de constante 1,4826, piège du MAD nul), la **distance de Mahalanobis** (loi du $\chi^2$, masquage, MCD), la **distance aux plus proches voisins** et le **LOF** (densité locale) ;
- **comprendre la forêt d'isolement** : longueur de chemin, score $s=2^{-E[h]/c(n)}$, sous-échantillonnage, et pourquoi la contamination est un choix opérationnel ;
- **construire un autoencodeur** avec `scikit-learn`, savoir qu'**il est équivalent à l'ACP quand il est linéaire**, que sa capacité doit être contrainte, qu'un réseau isolé est instable et qu'un comité de réseaux stabilise ;
- **comparer honnêtement** plusieurs détecteurs : un jeu de validation étiqueté pour régler, le jeu de test seulement pour juger, et se méfier des combinaisons naïves, qui ne battent pas forcément leur meilleur membre.

Le fil rouge du chapitre est le même que celui du volume : **la rigueur d'évaluation compte plus que la sophistication du modèle**. Les distances et les densités de la section 6.2 sont des idées anciennes qui rivalisent avec des méthodes récentes ; l'autoencodeur, le plus moderne, n'a été meilleur que parce que nous l'avons réglé sur un jeu de validation et moyenné sur plusieurs graines. Sur un problème où les erreurs coûtent de l'argent, la bonne question n'est jamais « quel est le meilleur algorithme ? », mais « *combien d'argent économise-t-on pour un budget de vérification donné, et comment le sait-on sans se tromper soi-même ?* ».

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.6 et exercices 6.1 à 6.12.

Le chapitre 7 (complémentaire, lui aussi) change de problème : au lieu de signaler ce qui est étrange, il s'agit de **recommander** à chaque client les produits qu'il aimera, à partir des achats de tous les clients.
