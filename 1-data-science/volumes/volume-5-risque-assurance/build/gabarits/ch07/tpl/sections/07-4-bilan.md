## Bilan du chapitre 7

Vous savez maintenant :

- **lire un bilan comme deux échéanciers** et distinguer la **valeur économique** (A − L) du résultat courant, et expliquer pourquoi le risque dominant d'un assureur vie est la **baisse** des taux et celui d'une banque de détail la **hausse** ;
- **calculer à la main** la valeur actuelle, la **duration** (Macaulay et modifiée) et la **convexité** d'un échéancier, démontrer ΔP/P ≈ −D_mod Δy + ½ C Δy², et savoir quand l'approximation cesse de valoir (chocs larges, courbe déformée) ;
- **construire le passif d'un portefeuille d'assurance vie** à partir d'une table de mortalité et d'un rapport décès observés / attendus, l'actualiser sur une courbe de taux et en lire la duration ({{D_mod:.1f}} ans) ;
- **apparier un actif à un passif** en euros (D_A · A = D_L · L), voir pourquoi l'égalité des durations seule est un piège quand A ≠ L, énoncer et vérifier les **conditions de Redington** et comprendre le rôle d'un **haltère** ;
- **mesurer l'exposition à la forme de la courbe** (durations par maturité, pentification, aplatissement) et **rejouer** un historique de taux sur un bilan ; **lire un échéancier de refixation** de banque ;
- **calculer le rendement et le risque d'un portefeuille** (formules matricielles), tracer la **frontière efficiente** à deux puis à cinq actifs, trouver les portefeuilles de **variance minimale** et **tangent**, et décomposer le risque en **contributions d'Euler** ;
- **expliquer le CAPM** comme un langage (bêta, risque systématique) et **douter des estimations** : erreur type des rendements, instabilité des poids, rétrécissement de la covariance (utile à n grand, inutile à n petit) ;
- **montrer que la diversification faiblit en stress** (corrélations qui montent, queues épaisses) ;
- **optimiser pour le surplus plutôt que pour l'actif** (réplication, frontière du surplus), estimer sa **VaR et son expected shortfall** avec leur incertitude, et **simuler** le taux de couverture sur dix ans.

Quelques chiffres à garder de ce chapitre (bilan jouet de la mutuelle, données simulées) :

| Question | Résultat mesuré |
|---|---|
| Duration modifiée du passif | {{D_mod:.1f}} ans (convexité {{conv_L:.0f}}) |
| Surplus après +1 point de taux, portefeuille de maturité 5 ans | {{dS_a_p1:.0f}} M€ (gain) ; {{dS_a_m1:.0f}} M€ pour −1 point |
| Surplus après ±3 points, haltère apparié en euros | de {{dS_d_m3:.1f}} à {{dS_d_p3:.1f}} M€ |
| Volatilité du portefeuille de variance minimale (5 actifs) | {{vol_min:.1f}} % en moyenne, {{vol_min_calme:.1f}} % en calme, {{vol_min_stress:.1f}} % en stress |
| Poids des obligations dans le portefeuille tangent selon l'année | de {{tan_obl_min:.0f}} % à {{tan_obl_max:.0f}} % |
| VaR à 99,5 % du surplus : allocation « Marché » contre « Apparié » | {{var_mar:.0f}} M€ contre {{var_app:.1f}} M€ |
| Probabilité de passer sous 1 un jour (10 ans) : « Marché » contre « Apparié » | {{pjam_mar:.0f}} % contre {{pjam_app:.1f}} % |

Le fil conducteur du chapitre tient en une phrase : **le risque d'une institution financière est celui de l'écart entre ses promesses et ses placements, et on ne le gère qu'en regardant les deux à la fois**. Un portefeuille « optimal » pour l'actif peut être le pire pour le surplus ; un portefeuille apparié aujourd'hui ne l'est plus quand la courbe se déforme ; une frontière estimée sur dix ans se lit avec ses barres d'erreur. Les mesures de risque du chapitre 3, les exigences de capital du chapitre 4, la mortalité du chapitre 5 et la réassurance du chapitre 6 sont les briques d'un même édifice : ce chapitre en a montré le **plan**.

> ⚠️ **Rappel d'honnêteté.** Toutes les données de ce chapitre sont simulées, les taux et les actions sont indépendants par construction, le passif est un échéancier fixe sans option et les scénarios sont tirés dans un historique court. Les résultats illustrent des **mécanismes** ; ils ne calibrent aucun portefeuille réel et ne constituent pas un conseil en placement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : applications 7.1 à 7.8 (prix et duration d'une obligation, passif d'un portefeuille vie, appariement, chocs de courbe, frontière efficiente, contributions au risque, estimation et rétrécissement, surplus et simulation) et exercices 7.1 à 7.12.
