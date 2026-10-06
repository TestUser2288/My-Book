## Bilan du chapitre 7

Vous savez maintenant :

- **lire un bilan comme deux échéanciers** et distinguer la **valeur économique** (A − L) du résultat courant, et expliquer pourquoi le risque dominant d'un assureur vie est la **baisse** des taux et celui d'une banque de détail la **hausse** ;
- **calculer à la main** la valeur actuelle, la **duration** (Macaulay et modifiée) et la **convexité** d'un échéancier, démontrer ΔP/P ≈ −D_mod Δy + ½ C Δy², et savoir quand l'approximation cesse de valoir (chocs larges, courbe déformée) ;
- **construire le passif d'un portefeuille d'assurance vie** à partir d'une table de mortalité et d'un rapport décès observés / attendus, l'actualiser sur une courbe de taux et en lire la duration (16,2 ans) ;
- **apparier un actif à un passif** en euros (D_A · A = D_L · L), voir pourquoi l'égalité des durations seule est un piège quand A ≠ L, énoncer et vérifier les **conditions de Redington** et comprendre le rôle d'un **haltère** ;
- **mesurer l'exposition à la forme de la courbe** (durations par maturité, pentification, aplatissement) et **rejouer** un historique de taux sur un bilan ; **lire un échéancier de refixation** de banque ;
- **calculer le rendement et le risque d'un portefeuille** (formules matricielles), tracer la **frontière efficiente** à deux puis à cinq actifs, trouver les portefeuilles de **variance minimale** et **tangent**, et décomposer le risque en **contributions d'Euler** ;
- **expliquer le CAPM** comme un langage (bêta, risque systématique) et **douter des estimations** : erreur type des rendements, instabilité des poids, rétrécissement de la covariance (utile à n grand, inutile à n petit) ;
- **montrer que la diversification faiblit en stress** (corrélations qui montent, queues épaisses) ;
- **optimiser pour le surplus plutôt que pour l'actif** (réplication, frontière du surplus), estimer sa **VaR et son expected shortfall** avec leur incertitude, et **simuler** le taux de couverture sur dix ans.

Quelques chiffres à garder de ce chapitre (bilan jouet de la mutuelle, données simulées) :

| Question | Résultat mesuré |
|---|---|
| Duration modifiée du passif | 16,2 ans (convexité 408) |
| Surplus après +1 point de taux, portefeuille de maturité 5 ans | 42 M€ (gain) ; -59 M€ pour −1 point |
| Surplus après ±3 points, haltère apparié en euros | de -1,2 à 0,8 M€ |
| Volatilité du portefeuille de variance minimale (5 actifs) | 4,1 % en moyenne, 3,6 % en calme, 7,9 % en stress |
| Poids des obligations dans le portefeuille tangent selon l'année | de 0 % à 100 % |
| VaR à 99,5 % du surplus : allocation « Marché » contre « Apparié » | 134 M€ contre 5,1 M€ |
| Probabilité de passer sous 1 un jour (10 ans) : « Marché » contre « Apparié » | 48 % contre 0,2 % |

Le fil conducteur du chapitre tient en une phrase : **le risque d'une institution financière est celui de l'écart entre ses promesses et ses placements, et on ne le gère qu'en regardant les deux à la fois**. Un portefeuille « optimal » pour l'actif peut être le pire pour le surplus ; un portefeuille apparié aujourd'hui ne l'est plus quand la courbe se déforme ; une frontière estimée sur dix ans se lit avec ses barres d'erreur. Les mesures de risque du chapitre 3, les exigences de capital du chapitre 4, la mortalité du chapitre 5 et la réassurance du chapitre 6 sont les briques d'un même édifice : ce chapitre en a montré le **plan**.

> ⚠️ **Rappel d'honnêteté.** Toutes les données de ce chapitre sont simulées, les taux et les actions sont indépendants par construction, le passif est un échéancier fixe sans option et les scénarios sont tirés dans un historique court. Les résultats illustrent des **mécanismes** ; ils ne calibrent aucun portefeuille réel et ne constituent pas un conseil en placement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.8 (prix et duration d'une obligation, passif d'un portefeuille vie, appariement, chocs de courbe, frontière efficiente, contributions au risque, estimation et rétrécissement, surplus et simulation) et exercices 7.1 à 7.12.
