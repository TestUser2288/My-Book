## Bilan du chapitre 5

Vous savez maintenant :

- **reconnaître la censure** et expliquer pourquoi la moyenne des durées, la moyenne des seuls événements et la proportion d'événements sont toutes **biaisées** ; distinguer censure à droite, à gauche, par intervalle et **troncature** (entrée tardive) ; énoncer l'hypothèse de **censure non informative** ;
- manier les trois fonctions d'une durée, **survie** $S(t)$, **risque instantané** $h(t)$ et **risque cumulé** $H(t)$, reliées par $S=e^{-H}$, et la formule $E[T]=\int_0^\infty S(t)\,dt$ ;
- écrire la **vraisemblance avec censure** $\ell=\sum[\delta_i\ln h(y_i)-H(y_i)]$ et en tirer le taux constant $\hat\lambda=D/\sum y_i$ ;
- calculer l'**estimateur de Kaplan-Meier** à la main et par code, ses intervalles de confiance (**Greenwood**, log-log), la **médiane** et la **durée moyenne restreinte** ; comparer des groupes par le **log-rank** et ses variantes ;
- ajuster et interpréter un **modèle de Cox** : vraisemblance partielle, rapports de risques, **ex aequo** (Breslow, Efron), **vérification de la proportionnalité** (graphique log-log, test de score de Grambsch-Therneau), **covariables dépendant du temps** et **biais d'immortalité**, courbes de survie prédites, **indice de concordance** ;
- ajuster des **modèles paramétriques** (Weibull, log-normal, log-logistique) par maximum de vraisemblance, lire un **facteur d'accélération**, passer de l'AFT aux risques proportionnels ($\beta=-\gamma/\sigma$ pour la Weibull), choisir par l'**AIC** et les **résidus de Cox-Snell**, **extrapoler** et calculer une **valeur vie client** avec une analyse de sensibilité ;
- (en option) traiter des **risques concurrents** : incidences cumulées d'**Aalen-Johansen**, pourquoi « 1 − KM » est faux, **modèle par cause** contre **Fine et Gray**.

Deux messages à garder en mémoire. **Un chiffre de survie n'a de sens qu'avec son traitement de la censure et ses hypothèses** (non informative, proportionnalité, forme de la loi) : on les énonce, on les vérifie quand c'est possible, on mesure leur influence sinon. Et **la randomisation reste l'arme la plus solide** : l'offre de bienvenue a un effet causal mesurable parce qu'elle a été attribuée au hasard ; pour les variables non randomisées (le canal, l'âge), les résultats sont des **associations**.

> 📒 **Pour s'entraîner.** Le cahier (chapitre 5) rassemble six applications guidées et treize exercices corrigés.

Le chapitre 6 change de perspective : au lieu de chercher *une* estimation et son incertitude, la **statistique bayésienne** attribue une **loi de probabilité** aux paramètres eux-mêmes, et la **simulation** (Monte-Carlo, MCMC) permet de calculer ce que l'algèbre ne sait pas faire.
