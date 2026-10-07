## Bilan du chapitre 3

Vous savez maintenant :

- **ajuster une droite par les moindres carrés** (la pente est la covariance divisée par la variance de $x$, le $R^2$ la part de variabilité expliquée), et **lire un tableau de résultats** : coefficient, erreur type, $t$, p-valeur, intervalle de confiance, $R^2$ ajusté ;
- **passer à plusieurs variables** et lire un coefficient « toutes choses égales par ailleurs », en sachant qu'il **change avec les variables de contrôle** (la publicité passe de {{mA_pub:+.0f}} % à {{pub_pct:+.1f}} % quand on contrôle la saison) ;
- **traiter les catégories** par des indicatrices et une référence, **lire des effets en pourcentage** ($e^{\beta}-1$) et des élasticités, et **tester une interaction** plutôt que la supposer ;
- **inspecter un modèle** : résidus, erreurs types robustes (HAC), colinéarité (VIF), distance de Cook ;
- **distinguer expliquer et prédire** : un modèle jugé sur des jours mis de côté ;
- **traduire en langage clair** : phrases avec effet, incertitude et conditions ; relatif et absolu ; commandes et chiffre d'affaires ; graphiques d'effets ; mises en garde sur l'importance relative ;
- (en option) **modéliser un oui/non** : cotes, rapports de cotes, effets marginaux, matrice de confusion, AUC, calibration, et un **seuil** déduit d'un calcul de coûts.

Le tableau suivant résume **ce que nous avons mesuré**, avec la vérité programmée :

| Question | Résultat | Vérité programmée |
|---|---|---|
| Effet d'un jour de promotion sur les commandes | {{promo_pct:+.1f}} % ({{promo_lo:+.1f}} ; {{promo_hi:+.1f}}) | +18 % |
| Effet sur le chiffre d'affaires | {{promo_ca:+.1f}} % | (remises de 5 à 20 %) |
| Effet de 1 000 € de publicité hebdomadaire | {{pub_pct:+.1f}} % ({{pub_lo:+.1f}} ; {{pub_hi:+.1f}}) : non détecté | +1,5 % |
| Pluie | {{pluie_pct:+.1f}} % | environ −1,7 % |
| Prévision 2025 (erreur moyenne par jour) | {{mae:.1f}} commandes ({{mape:.0f}} %) | référence naïve : {{mae_364:.1f}} |
| Rapport de cotes de retour, Site contre Boutique | {{or_site:.1f}} ({{or_site_lo:.1f}} ; {{or_site_hi:.1f}}) | ≈ 3,1 (9 % contre 3 %) |
| Autres variables (prix, catégorie, remise, quantité) | aucun effet net | aucun effet |

Le fil conducteur du chapitre tient en une phrase : **un coefficient n'est pas un fait de la nature, c'est la réponse d'un modèle à une question précise, avec une incertitude.** La promotion est mesurée avec précision parce que l'effet est grand et que les jours de promotion sont nombreux ; la publicité ne l'est pas, parce que l'effet est petit et noyé dans la saison. Dans les deux cas, la bonne conduite est la même : **contrôler ce qui trompe, montrer l'intervalle, et dire ce que les données ne permettent pas de dire.**

La régression explique des effets **moyens** sur l'ensemble des jours ou des clients. Le chapitre 4 s'intéresse aux **différences entre groupes** de clients (segmentation) et à leur **évolution dans le temps** (cohortes) ; le chapitre 5 revient sur le temps pour **prévoir** avec des méthodes spécialisées.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.7 (droite à la main, lire un tableau, modèle de promotion et de publicité, diagnostic, prévision, présentation à la gérante, retours) et exercices 3.1 à 3.14.
