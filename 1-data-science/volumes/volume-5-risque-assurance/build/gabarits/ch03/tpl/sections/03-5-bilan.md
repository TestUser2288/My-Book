## Bilan du chapitre 3

Vous savez maintenant :

- **définir** une perte de portefeuille, une **VaR** (quantile de niveau $\alpha$, avec son horizon et sa convention de signe) et une **expected shortfall** (perte moyenne au-delà de la VaR), les **calculer** par la loi normale ($\mu+\sigma z_\alpha$, démontrée), par l'histoire, par simulation et avec une volatilité qui change (EWMA, GARCH) ;
- **démontrer** que la VaR n'est pas sous-additive (deux prêts à 4 % de probabilité de défaut) alors que l'ES l'est, et **mesurer l'incertitude** d'un chiffre de queue par bootstrap ;
- **mettre à l'échelle** un horizon par la règle de la racine carrée en connaissant ses conditions (pertes indépendantes) ;
- **concevoir** un stress test : sensibilités, scénarios historiques et hypothétiques, scénario macroéconomique relié aux défauts par un modèle logit, choc de taux (duration, convexité, réévaluation complète), stress **inversé**, et **expliquer** pourquoi les corrélations montent en crise ;
- (en option) **chiffrer** un risque opérationnel par fréquence × sévérité, reconnaître l'instabilité d'un quantile à 99,9 %, **allouer** le risque d'un portefeuille (contributions d'Euler), et lire un **coussin de liquidité** ;
- (en option) **backtester** une VaR (Kupiec, Christoffersen, feu tricolore), connaître la faible puissance de ces tests, contrôler grossièrement une ES, et situer le backtest dans la **validation** et le **risque de modèle**.

Le tableau suivant résume **ce que nous avons mesuré** sur les données simulées de ce chapitre, portefeuille de 100 M€ :

| Question | Résultat | Ce qu'il faut en retenir |
|---|---|---|
| VaR à 99 % sur un jour | historique {{var_h99}} M€ ; normale {{var_n99}} M€ ; ES historique {{es_h99}} M€ | la loi normale sous-estime la queue ; l'ES est {{ratio_es}} fois la VaR |
| Fréquence de dépassement en stress (méthodes figées) | historique {{exc_hist_stress}} %, normale {{exc_norm_stress}} % | le jour où l'on a besoin de la VaR, elle est fausse d'un facteur dix |
| Diversification | corrélation actions A–B {{corr_AB_c}} (calme) puis {{corr_AB_s}} (stress) | elle s'érode quand on en a le plus besoin |
| Scénario macro adverse | perte de crédit de {{sc_adv_perte}} M€ contre {{sc_base_perte}} M€ en base | un facteur {{ratio_adv_base}} pour une récession déjà observée |
| Stress inversé | coussin de 25 M€ épuisé par une croissance de {{rv_pib}} % | moins sévère que la pire récession de l'échantillon |
| Opérationnel (➕) | VaR à 99,9 % de {{mc999_lo}} à {{mc999_hi}} M€ selon la graine | une queue à $\xi$ proche de 1 rend l'extrême instable |
| Backtest (➕) | seul le GARCH-Student passe Kupiec ({{bt_garch_k}} dépassements pour 30 attendus) | encore {{bt_garch_cs}} % de dépassements en stress |

Le fil conducteur du chapitre tient en une phrase : **un nombre de risque est une réponse conditionnelle**, à un niveau, à un horizon, à une méthode, à une période d'estimation, et il vient avec une incertitude qu'il faut lui rattacher. La VaR décrit les jours ordinaires, le stress test les jours qui ne le sont pas, le backtest vérifie que le modèle tient, la validation demande si l'on peut s'y fier ; **aucune de ces quatre démarches ne suffit seule**.

> 🧭 **En pratique : liste de questions devant tout chiffre de risque.**
> 1. À quel niveau, sur quel horizon, avec quelle convention de signe ?
> 2. Calculé comment (loi, fenêtre, volatilité) et sur quelle période : calme ou crise incluse ?
> 3. Avec quelle incertitude (intervalle, plage entre deux méthodes) ?
> 4. Qu'en dit un scénario de stress, y compris inversé ?
> 5. Le backtest a-t-il assez de puissance pour dire que c'est bon ?
> 6. Qui a validé le modèle, avec quelles limites d'usage ?

> ⚠️ **Rappel d'honnêteté.** Les données de ce chapitre sont **simulées** : le simulateur connaît le régime de marché, la relation macro-défaut et les lois des pertes, ce qui nous a permis de juger les méthodes ; en réalité on ne dispose jamais de cette vérité. Le modèle macro de 3.2 est stable par construction, les seuils réglementaires cités (zones du feu tricolore, niveau de l'ES) sont à vérifier dans les textes en vigueur, et rien ici n'est un conseil financier ou réglementaire.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.8 (VaR et ES sur le portefeuille, EWMA et GARCH filtré, simulation et loi de Student, incertitude par bootstrap, stress macro, choc de taux, perte opérationnelle agrégée, backtest complet) et exercices 3.1 à 3.12.

Le chapitre 4 change de point de vue : ces mesures de risque ne sont plus seulement des outils de gestion, elles sont **imposées** par des cadres réglementaires (Bâle pour les banques, Solvabilité pour les assureurs). Nous verrons comment ces textes transforment une PD, une LGD ou une VaR en **exigence de capital**, et ce que valent ces conventions.
