## Bilan du chapitre 6

Vous savez maintenant :

- **raisonner à la bayésienne** : a posteriori $\propto$ vraisemblance $\times$ a priori ; utiliser les **lois conjuguées** (bêta-binomiale, gamma-Poisson, normale-normale) pour obtenir des résultats exacts par simple addition ; lire et interpréter un **intervalle de crédibilité** ; formuler des phrases comme « *la probabilité que l'offre soit utile est de…* » ;
- **choisir et justifier un a priori**, mesurer son influence par une **analyse de sensibilité**, et savoir qu'il s'efface quand les données sont abondantes (Bernstein-von Mises) ;
- **estimer par simulation** (Monte-Carlo) : une espérance, une probabilité, une intégrale ; connaître la vitesse en $1/\sqrt n$ ; fabriquer des tirages par **inversion** ou **rejet** ; utiliser l'**échantillonnage préférentiel** pour les événements rares, avec son **ESS**, et les **techniques de réduction de variance** ;
- **simuler une loi a posteriori** non conjuguée avec une chaîne de Markov : **Metropolis-Hastings** (bilan détaillé, réglage du pas, taux d'acceptation) et **Gibbs** (lois conditionnelles complètes), puis calculer *tout* (rapports de cotes, effets sur les probabilités, prédictions) par de simples moyennes ;
- **vérifier ses modèles** : plusieurs chaînes dispersées, traces, $\widehat R$, ESS ; vérifications prédictives **a priori** et **a posteriori** ; comparaison par facteur de Bayes (et ses limites : sensibilité à l'a priori, paradoxe de Lindley) et par WAIC ;
- (en option) **modéliser les extrêmes** par la loi GEV et les excès au-delà d'un seuil (GPD), estimer des **niveaux de retour** avec leur incertitude ;
- (en option) **modéliser la dépendance** par les **copules**, comprendre la différence entre corrélation et dépendance de queue, et pourquoi le choix de la copule décide du risque de **catastrophes simultanées**.

Les deux fils conducteurs de ce chapitre sont **l'incertitude** (qu'il faut quantifier et propager jusqu'à la décision) et **la vérification** (un modèle, un a priori ou un algorithme ne sont jamais acceptés sur parole). Ces deux idées ne s'arrêtent pas aux méthodes bayésiennes : elles guident tout le reste du métier.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.6 et exercices 6.1 à 6.14.

Le prochain chapitre, optionnel, aborde l'**inférence causale** : comment passer de « *deux variables varient ensemble* » à « *agir sur l'une changera l'autre* », et ce qu'il faut pour que cette inférence soit légitime. Les sections 6.1 et 6.4 (a priori, vérification de modèle) en seront un outil précieux.
