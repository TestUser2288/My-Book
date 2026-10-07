## Bilan du chapitre 13

Vous savez maintenant :

- **construire un petit modèle de résultat** (sessions, conversion, panier, prix, coût d'achat, charges, marketing, retours), le **calibrer** sur une année de données et le **vérifier** sur un chiffre qu'il n'a pas reçu (écart de 4,7 % avec les comptes, expliqué à 2 € près par la variation de stock) ;
- **lire une tornade** et savoir qu'elle classe les paramètres **pour des plages données** : avec des plages tirées des données, le coût d'achat passe devant le trafic, la conversion et le panier ;
- **exprimer la sensibilité en euros par point** (un point de coût d'achat : −6 478 € ; un point de prix : +6 145 € ; un point de retours : −5 218 €), et traiter un paramètre que les données ne donnent pas, l'**élasticité**, par un **seuil** (3,6 pour la baisse de prix de 5 %) ;
- **croiser deux paramètres** (prix × volume), et reconnaître trois pièges : plages arbitraires, linéarité supposée, paramètres supposés indépendants ;
- **simuler** par Monte-Carlo : choisir et **justifier** chaque loi (données ou hypothèse déclarée), annoncer médiane, intervalle et probabilité de perte, **fixer la graine** et vérifier la stabilité, mesurer l'effet d'une **dépendance** entre paramètres ;
- **construire des scénarios** comme des récits cohérents, chiffrer des « et si » (dont certains tirés des données : transporteur, promotion), **comparer des options** sur les mêmes tirages, lire un **regret**, et trouver les **seuils de bascule** ;
- **présenter** le tout sur une page : une réponse, une preuve, des réserves.

Le tableau suivant résume **ce que nous avons mesuré** sur les comptes simulés de la boutique (résultat d'exploitation après retours ; TVA fictive à 20 %).

| Question | Résultat mesuré |
|---|---|
| Résultat de 2025 selon les comptes, selon le modèle avant retours, après retours | 39 879 €, 41 769 €, **8 501 €** (les retours ne sont pas dans le compte simulé) |
| Paramètre qui pèse le plus (plages de la tornade) | le prix (−33 176 € à +29 260 € pour ±5 %), puis le coût d'achat (±32 391 €) |
| Part de la variance de l'année prochaine due au coût d'achat | 66,4 % |
| Année prochaine avec prix indexés de 3 % : médiane, intervalle à 80 %, probabilité de perte | 17 834 €, de −11 755 € à 49 067 €, 22,6 % |
| Stabilité de la médiane selon le nombre de tirages (étendue sur 20 graines) | 7 912 € (100 tirages), 1 205 € (10 000 tirages) |
| Trois scénarios (central, pessimiste, optimiste) | 17 979 €, −53 287 €, 64 901 € |
| Baisse de prix de 5 % (élasticité 1,2) : effet par rapport à l'indexation | −54 203 € ; seuil d'élasticité 3,6 |
| Publicité +20 % par session : budget constant, sessions maintenues | −2 929 € ; −12 981 € |
| Une semaine de promotion en plus : marge | −929 € (il faudrait +40,2 % de commandes pour la neutraliser, l'effet mesuré est de +19,4 %) |
| Hausse du coût d'achat qui annule le résultat de 2025 | +1,31 % |

Le fil conducteur du chapitre tient en une phrase : **un modèle ne donne pas une réponse, il donne une réponse conditionnelle, et le travail de l'analyste est de rendre les conditions visibles, chiffrées et discutables**. Trois habitudes en découlent : **vérifier** le modèle avant de le faire varier ; **justifier** chaque hypothèse (et dire lesquelles ne sont pas mesurées) ; **chercher le seuil** où la décision changerait, plutôt que d'asséner une probabilité.

> ⚠️ **Rappel d'honnêteté.** Le modèle est petit et les comptes sont **simulés**. Six des neuf lois de la simulation sont des hypothèses d'analyste ; l'élasticité de la demande n'a pas été mesurée ; le compte de résultat simulé ne contient pas les remboursements, que le modèle ajoute. Les chiffres montrent une **méthode**, pas un avenir.

> 📒 **Pour s'entraîner.** Cahier, chapitre 13 : applications 13.1 à 13.6 (construire et vérifier le modèle, tornade et seuil d'élasticité, lois de la simulation et stabilité, dépendance entre paramètres, scénarios et « et si », options, regret et seuils) et exercices 13.1 à 13.10.

Ce chapitre complémentaire prolonge ceux de ce volume : le chapitre 3 (régression) pour estimer une élasticité à partir de données, le chapitre 6 pour choisir le résultat que l'on regarde, le chapitre 2 pour **tester** une hypothèse avant de décider (un test A/B sur quelques produits). Le chapitre 9 (analyse financière) lit ces mêmes comptes sous un autre angle : ratios, rentabilité et seuil de rentabilité.
