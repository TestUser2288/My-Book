## Bilan du chapitre 4

Vous savez maintenant :

- **décrire** une série temporelle (tendance, saison, bruit, accident) et la **décomposer** (classique, STL robuste), en travaillant sur le **logarithme** quand la saison est proportionnelle au niveau ;
- définir la **stationnarité**, mesurer la mémoire par l'**autocorrélation** et l'**autocorrélation partielle**, tester le bruit blanc (**Ljung-Box**) et la racine unitaire (**ADF**, **KPSS**) en connaissant leurs limites (peu de puissance, loi de Dickey-Fuller non normale) ;
- distinguer **tendance déterministe** et **tendance stochastique**, et éviter la **sur-différenciation** ;
- construire des modèles **AR, MA, ARMA, ARIMA, SARIMA** et **SARIMAX**, connaître leurs conditions de stationnarité et d'inversibilité, suivre la méthode de **Box-Jenkins** (identification, estimation, diagnostic, prévision) et lire un diagnostic de résidus ;
- **prévoir** avec ses intervalles, passer du logarithme aux euros, et **évaluer honnêtement** : découpage temporel, références simples, MAE, RMSE, MAPE, **MASE**, bootstrap par blocs, **validation à origine glissante**, combinaison de prévisions ;
- comprendre qu'un seul jeu de test est **bruité** : le meilleur modèle en espérance ne gagne pas toujours (4.3.8) ;
- (en option) modéliser **plusieurs séries** (VAR, causalité de Granger, **cointégration**, régression fallacieuse), la **volatilité** (GARCH), les **modèles d'espace d'états** et le **filtre de Kalman** (lissage exponentiel, données manquantes), et situer **Prophet** et les bibliothèques modernes.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.4 et exercices 4.1 à 4.13.

Le chapitre 5 change d'univers : il ne s'agit plus d'une série qui évolue **dans le temps calendaire**, mais d'un événement dont on mesure **la durée d'attente**, avec le défi particulier de la **censure** : combien de temps un client reste-t-il fidèle, quand certains sont encore clients aujourd'hui ?
