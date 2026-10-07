## Bilan du chapitre 5

Vous savez maintenant :

- **décomposer** une série en **tendance, saison et résidu**, additif ou multiplicatif, et reconnaître que la saison est multiplicative quand son amplitude grandit avec le niveau (le rapport décembre/février reste proche de 2,5 alors que la différence en euros augmente) ;
- **comparer honnêtement** : à la même période de l'an dernier, ou en glissement sur douze mois, jamais de mois consécutifs sur une série saisonnière ; **somme** les montants avant de calculer un pourcentage ;
- **calculer des indices saisonniers** à la main (rapport à la moyenne mobile centrée, moyenné par position, normalisé), **désaisonnaliser**, et utiliser `seasonal_decompose` et STL ;
- **mesurer une tendance** par la pente du logarithme de la série désaisonnalisée, avec des erreurs robustes à l'autocorrélation, et la lire avec son intervalle ; séparer croissance de fond et **rupture** (le relèvement de prix de 2025) ;
- **tenir compte du calendrier** (jour de semaine, longueur et composition des mois) et **traiter les incidents** : les trouver (contrôles exacts, score z robuste), choisir un seuil selon le coût des erreurs, corriger ou signaler, et le documenter ;
- **lisser** (moyenne mobile simple, centrée, exponentielle) en connaissant le retard et la fausse régularité ;
- **prévoir** avec des références simples, **évaluer** sans fuite temporelle, avec une mesure adaptée et à plusieurs origines, **donner un intervalle** que l'on vérifie, et connaître le **plancher** du hasard ;
- (en option) **régresser** avec des indicatrices de calendrier et de décision, **comparer** à un ARIMA saisonnier, **prévoir par canal**, mesurer l'effet de l'**horizon**, bâtir des **scénarios** et en tirer des décisions de personnel et de stock.

Les chiffres du chapitre, qui répondent à la gérante :

| Question | Ce que nous avons mesuré |
|---|---|
| Les ventes progressent-elles vraiment ? | oui : 8,2 % par an en moyenne (intervalle 6,4 % à 10,0 %) ; en séparant le relèvement de prix de 2025, 6,5 % de croissance de fond (3,6 % à 9,6 %) et 3,5 % de saut de niveau |
| Comparaison à l'an dernier | +4,4 % en 2024, +11,4 % en 2025 ; glissement annuel de 4,4 % à fin 2024 à 11,4 % à fin 2025 |
| Saison | décembre 1,583 fois un mois moyen, février 0,677 ; samedi 1,390 fois un jour moyen, dimanche 0,657 |
| Incidents | au seuil 3,5, 4 incidents statistiques sur 7 trouvés (et 4 fausses alertes) ; au seuil 3, 7 sur 7 (et 11 fausses alertes) |
| Prévoir 2025 avec 2023-2024 | naïve saisonnière : MAPE 10,2 % ; avec croissance : 7,2 % ; tendance × indices : 7,0 % ; Holt-Winters : 7,1 % ; biais commun de -6,2 % (changement de régime) |
| Prévoir à 28 jours, jour par jour | MAE de 718 € par jour pour Holt-Winters, plancher du hasard d'environ 630 € ; sur le total des 28 jours, l'erreur est de 7,2 % pour la meilleure méthode |
| Décembre prochain | 191 934 € (prudent), 195 795 € (central), 201 669 € (avec hausse de prix de 3 %) ; modèle : 190 904 € |

**Le fil conducteur du chapitre tient en une phrase : une série temporelle se lit en séparant ce qui revient de ce qui change, et une prévision se juge à sa capacité à battre un chiffre simple, avec l'incertitude écrite à côté.** Les erreurs les plus coûteuses ne sont pas des erreurs de modèle ; ce sont des **changements de régime** (un prix, un canal) que personne ne pouvait voir dans l'historique, et que l'on doit nommer plutôt que de laisser un modèle les absorber.

> 🧭 **En pratique : liste de contrôle d'une analyse de série temporelle.**
> 1. Le pas est-il celui de la décision (jour, semaine, mois) ? Les mois sont-ils comparables (longueur, calendrier) ?
> 2. A-t-on cherché les incidents et les ruptures avant de décomposer, et consigné ce qu'on en a fait ?
> 3. La comparaison est-elle à la même période de l'an dernier (ou en glissement annuel) ?
> 4. Une référence naïve saisonnière a-t-elle été calculée, et la méthode retenue la bat-elle nettement ?
> 5. L'évaluation est-elle faite dans le temps (sans fuite), avec la mesure annoncée et, si possible, plusieurs origines ?
> 6. Chaque prévision est-elle accompagnée d'un intervalle ou de scénarios, et de ce qui les ferait changer ?

Le chapitre 6 traite d'un sujet qui touche tout ce qui précède : comment **choisir** les chiffres que l'on suit, c'est-à-dire concevoir des **indicateurs de performance** (KPI), les relier dans un **arbre**, et fixer des **cibles** et des **seuils** qui évitent de réagir au bruit.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.9 (composantes et comparaisons, indices saisonniers et décomposition, calendrier, incidents, moyennes mobiles, prévoir 2025, plusieurs origines, régression avec indicatrices, décembre prochain et planification) et exercices 5.1 à 5.12.
