## Bilan du chapitre 2

Vous savez maintenant :

- **décomposer** le coût d'un contrat en une fréquence et une sévérité, estimer une fréquence **sur l'exposition** (et non sur le nombre de contrats), reconnaître la **sur-dispersion** et la modéliser par une binomiale négative (Poisson–Gamma) ;
- **décrire** des montants asymétriques (Gamma pour le cœur, Pareto généralisée pour la queue), mesurer le poids des gros sinistres, **écrêter** et mutualiser leur charge, et reconstruire la **charge annuelle** d'un portefeuille par le modèle collectif ;
- **construire un tarif** : prime pure $=E[N\mid x]\,E[X\mid x]$ par deux GLM (ou un Tweedie), chargements $(\pi+F)/(1-\tau-m)$, relativités lisibles, puis le **valider hors période** (courbe de Lorenz ordonnée, Gini et son intervalle, lecture par dixièmes) et mesurer le prix d'un tarif trop grossier (**antisélection**) ;
- **provisionner** par triangle et *chain ladder*, choisir une **queue**, et **juger a posteriori** une provision contre les paiements réels ;
- (en option) lire la **déviance** et les tests d'un GLM, choisir la forme des variables, **régulariser**, doser expérience et a priori par la **crédibilité** de Bühlmann–Straub, comparer un GLM à un boosting ;
- (en option) estimer une provision **avec son incertitude** (Bornhuetter–Ferguson, Cape Cod, Mack, bootstrap ODP), diagnostiquer un **choc calendaire** par les résidus de diagonale ;
- (en option) analyser un portefeuille de **santé** : concentration des coûts, sélection adverse et aléa moral, table de morbidité, mutualisation.

Le tableau suivant résume **ce que nous avons mesuré**, avec la vérité programmée quand on la connaît :

| Question | Résultat mesuré | Vérité ou référence |
|---|---|---|
| Fréquence annuelle (automobile) | 6,61 % | environ 6,5 % |
| Hétérogénéité $\alpha$ (binomiale négative) | 0,47 ± 0,09 | 0,4 |
| Part du coût due aux sinistres > 100 000 € | 53 % pour 1,6 % des sinistres | queue de Pareto programmée |
| Quantile à 99,5 % de la charge annuelle | 23,9 M€ (moyenne 17,1 M€) | plancher plausible |
| Gini du tarif complet, 2024 | 0,18 (plat : 0,02) | bruit d'un tarif aléatoire : ± 0,04 |
| Ratio sinistres/primes d'un tarif plat après antisélection | 114 % | 97 % avant |
| Provision RC par chain ladder, sans queue | 230,2 M€ | réel : 242,1 M€ |
| Provision RC par chain ladder, avec queue extrapolée | 249,3 M€ | réel : 242,1 M€ |
| Erreur de Mack sur la provision totale (RC) | 5,4 M€ | l'erreur réelle est bien plus grande |
| Provision dommages (développement court) | 31,9 M€ | réel : 32,3 M€ |
| Niveau « premium » contre « basique » (santé) | brut ×2,1, ajusté ×1,48 | sélection et aléa moral à parts égales |

Trois idées dépassent ce chapitre. **D'abord, ce qui fait la qualité d'un modèle d'assurance se joue dans les queues et les hypothèses**, pas dans la vraisemblance : la charge annuelle dépend de quelques sinistres, la provision de la queue du triangle. **Ensuite, un chiffre de risque est toujours accompagné de son incertitude et d'une validation hors période** : un Gini sans intervalle, une provision sans erreur de prédiction, un quantile à 99,5 % sans mention de sa fragilité ne sont pas des résultats. **Enfin, un tarif et une provision sont des décisions** : ils engagent de l'argent, créent des subventions entre assurés, exposent à l'antisélection, et leur « juste » valeur ne se connaît que des années plus tard.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.9 (comptage et exposition, binomiale négative, queue de Pareto, modèle collectif, GLM de fréquence et de sévérité, validation et antisélection, chain ladder, Bornhuetter–Ferguson/Mack/bootstrap, santé) et exercices 2.1 à 2.14.

Le chapitre 3 reprend la **charge annuelle** et ses queues sous un autre angle : celui des **mesures de risque** (valeur à risque, perte attendue au-delà du seuil) et des **stress tests**, qui servent aussi bien à une banque qu'à une mutuelle.
