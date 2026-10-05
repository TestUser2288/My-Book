## Bilan du chapitre 5

Vous savez maintenant :

- **choisir la bonne mesure** : exactitude comparée au modèle « classe majoritaire », précision, rappel, $F_\beta$ et MCC pour une décision à seuil ; **AUC** (probabilité qu'un positif soit mieux classé qu'un négatif) et **précision moyenne** pour juger un score, la seconde étant la seule à voir la prévalence ; **log-loss** et **Brier** pour juger des probabilités ; MAE, RMSE, $R^2$ et perte pinball en régression, en évitant le MAPE quand la cible contient des zéros ;
- **transformer un score en décision** par les coûts, avec le seuil $t^\star=c/(sV)$, et lire le **gain** et le **lift** quand on raisonne en budget ;
- **vérifier la calibration** d'un modèle par un diagramme de fiabilité, comprendre pourquoi les forêts sont sous-confiantes, le boosting surajusté sur-confiant et les poids de classes décalent la prévalence, et **réparer** par la méthode de Platt, la régression isotonique ou la correction exacte d'un décalage de prévalence, sur un jeu séparé ;
- **expliquer un modèle** : importance par permutation (et son piège avec les variables corrélées), PDP et ICE, LIME (et son instabilité), **valeurs de Shapley** et SHAP, avec la propriété d'efficacité qui décompose exactement chaque prédiction ; et utiliser l'interprétabilité pour **débusquer une fuite d'information** ;
- (en option) **auditer l'équité** d'un modèle par groupe, comprendre qu'on ne peut pas égaliser à la fois rappel, précision et fausses alertes quand les taux de base diffèrent, et ne pas confondre retirer une variable sensible et supprimer le biais ;
- (en option) **quantifier l'incertitude** par la prédiction conforme : une garantie de couverture valable à distance finie pour n'importe quel modèle, mais marginale, et non conditionnelle.

Un fil conducteur traverse le chapitre : **une métrique, un seuil ou une explication ne valent que par la question à laquelle on les rattache**. L'AUC qui satisfait le data scientist, l'exactitude qui rassure le client et le seuil de 0,5 que l'on a toujours utilisé répondent à trois questions différentes ; aucune n'est « la » question de la gérante, qui est en euros.

Les chapitres complémentaires qui suivent appliquent ces outils à des problèmes particuliers : la détection d'anomalies et de fraude (chapitre 6, où la classe positive est extrêmement rare, donc où la courbe précision-rappel est reine), les systèmes de recommandation (chapitre 7), l'apprentissage semi-supervisé et actif (chapitre 8) et l'apprentissage par renforcement (chapitre 9).

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.10 et exercices 5.1 à 5.14.
