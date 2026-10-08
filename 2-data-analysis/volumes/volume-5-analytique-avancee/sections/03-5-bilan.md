## Bilan du chapitre 3

Le chapitre est parti de deux questions de la gérante (« combien de commandes en janvier ? », « quels clients ne reviendront probablement plus ? ») et a construit, pour chacune, un modèle simple, jugé honnêtement, relié à une décision.

| Section | Ce que vous devez emporter |
|---|---|
| **3.1 Ce qu'apporte l'analytique prédictive** | Il y a quatre sortes de questions (décrire, diagnostiquer, **prédire**, prescrire). **Prédire, expliquer, décider** sont trois usages distincts. La **valeur** d'une prévision est la décision qu'elle change, **chiffrée en euros** ; elle se décide avec sa **fourchette**. On n'utilise que ce qui est **connu à la date de la prévision** et l'on bat une **référence naïve saisonnière**. |
| **3.2 Modèles prédictifs simples** | **Cas A** : références (naïf, saisonnier, saisonnier × croissance, Holt-Winters) puis régression de **Poisson** qui connaît le calendrier ; jugement par **origine glissante** (MAE, MAPE, biais, à plusieurs horizons) ; une prévision de janvier 2026 avec fourchette et deux scénarios. **Cas B** : une **cible datée**, des variables **du passé** et **stables**, une séparation **dans le temps**, régression logistique et arbre ; **AUC, calibration, gain** ; la **fuite d'information** (+7 points d'AUC pour rien) ; le choix de qui contacter **selon les coûts** et **le consentement**, sans confondre « qui rachètera » et « qui rachètera grâce au message ». |
| **3.3 Quand passer la main** | Six signes pour passer la main, trois pour ne pas ; un **test honnête** (modèle simple contre boosting, avec intervalle) ; le **dossier de passation** ; la **dérive** (l'AUC tient, les probabilités décrochent avec la saison) ; la surveillance à deux vitesses ; le **risque de modèle**, la **validation à quatre yeux**, l'**audit par groupes**. |
| **3.4 ➕ AutoML et sans code** | L'AutoML automatise le **réglage**, pas la formulation ni l'évaluation. Un **mini-AutoML** en dix lignes ; les premiers du classement sont **à égalité** ; **plus on essaie, plus le gagnant est flatté** ; test scellé, validation temporelle, règle de l'écart-type ; huit questions à poser à un outil. |

## Cinq idées à garder

> 💡 **Les cinq idées.**
> 1. **La décision d'abord.** Une prévision se juge à ce qu'elle change, en euros, avec ses fourchettes.
> 2. **Ne connaître que le passé.** Variables calculées à la date de coupure, séparation dans le temps, chasse à la fuite : c'est la discipline qui rend une prévision crédible.
> 3. **Toujours une référence.** Un modèle ne vaut que par ce qu'il gagne sur une règle simple, avec son incertitude.
> 4. **Prédire n'est pas décider.** Un score dit qui rachètera, pas qui rachètera grâce à un message : seul un essai mesure l'effet.
> 5. **Un modèle se surveille.** Il a un propriétaire, un dossier, des indicateurs de dérive ; et quand il touche des personnes, leur consentement et un regard par groupes.

## Vers le chapitre 4

Le chapitre 4 retrouve ces idées dans deux secteurs qui vivent de la prédiction du risque, **l'assurance** et le **crédit** : des sinistres à provisionner, des prêts à suivre, des alertes à déclencher. Les mêmes réflexes (cible datée, référence, séparation dans le temps, calibration, surveillance, validation à quatre yeux) y sont **obligatoires** plutôt que recommandés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.8, exercices 3.1 à 3.12.
