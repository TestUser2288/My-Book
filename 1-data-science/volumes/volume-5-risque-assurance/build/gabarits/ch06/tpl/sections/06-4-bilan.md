## Bilan du chapitre 6

Vous savez maintenant :

- **expliquer** pourquoi une cédante réassure : non pour réduire son coût moyen, mais pour **stabiliser** son résultat, gagner de la **capacité** et **économiser du capital** ; et pourquoi la variance de la charge annuelle vient des gros sinistres, que la mutualisation ne diminue pas ({{cv_s|pc1}} % de coefficient de variation brut, {{cv_sn|pc1}} % une fois les sinistres plafonnés à 500 000 €) ;
- **distinguer** les traités **proportionnels** (quote-part, excédent de plénitude : mêmes proportions de primes et de sinistres) des traités **non proportionnels** (excédent de sinistre « portée xs priorité », par événement, stop-loss), calculer à la main ce que chacun cède sur huit sinistres (1 207,5, 2 560 et 1 000 sur 4 025), et lire les **réintégrations**, le **plafond annuel**, le **taux de prime** et le **ROL** ;
- **estimer** la prime pure d'une tranche par le *burning cost* (à **ajuster de l'exposition et de l'inflation**), par une loi de queue **GPD** (avec sa formule fermée) et par l'**exposition** (courbe $G(d)$) ;
- **mesurer l'incertitude** par le bootstrap par années, et savoir que l'erreur typique d'un tarif à quinze ans d'historique est de {{rep_cv1|pc0}} %, {{rep_cv2|pc0}} % et {{rep_cv3|pc0}} % pour trois tranches de plus en plus hautes ;
- **traiter** les catastrophes avec peu de données (une loi de Pareto ajustée sur {{cat_ev|int}} événements, des tranches dont l'espérance est incertaine à un facteur deux), et passer de la prime pure à la **prime technique** (écart-type, coût du capital) ;
- **comparer** des programmes sur quatre axes (coût, volatilité, capital, ruine) par le **coût d'un euro de capital économisé**, évaluer l'effet d'une tour de catastrophe selon la vue que l'on a de la queue, et chiffrer le **risque de contrepartie** et l'**épuisement** d'une garantie.

Le chapitre a mis des chiffres sur des idées souvent qualitatives.

| Ce que l'on a vu | Résultat mesuré |
|---|---|
| *Burning cost* brut contre ajusté de l'exposition | sous-estimation de {{err_raw1|pc0}} à {{err_raw3|pc0}} % sans ajustement |
| Indexation de 4 % par habitude, alors que la sévérité est stable | tranches surestimées de {{err_inf1|pc0}} à {{err_inf3|pc0}} % |
| GPD sur le seuil de 1 M€ | $\hat\xi={{xi10|2}}$ (vérité 0,55) : seuil trop haut, trop peu de points |
| Bootstrap sur la tranche 2 M€ xs 2 M€ | intervalle à 95 % de {{lo3|M2}} à {{hi3|M2}} M€ (vérité {{vrai3|M2}}) |
| Catastrophes : $\hat\alpha$ sur 17 événements | {{alpha_hat|2}} contre 1,11 en vérité |
| Coût par euro de capital économisé | stop-loss {{rat_sl|3}} ; quote-part {{rat_qp|2}} ; excédents de sinistre de {{rat_xl2|2}} à {{rat_xl05|2}} |
| Défaut du réassureur lié aux gros sinistres | probabilité de ruine multipliée par {{mult_ww|1}} |

Le fil conducteur du chapitre tient en une phrase : **le prix d'une protection est une estimation incertaine d'un risque rare, et sa valeur dépend de ce qui contraint la cédante**. L'incertitude du tarif est de l'ordre de grandeur du chargement que l'on négocie ; les données courtes sous-estiment la queue ; la couverture n'est jamais plus solide que le contrat et que le réassureur.

> ⚠️ **Rappel d'honnêteté.** Les sinistres et les catastrophes sont **simulés** : nous avons pu comparer les estimations à la vérité, ce que personne ne peut faire en pratique. Les chargements, le coût du capital (8 %), la structure de frais (25 %) et les prix des programmes sont des **hypothèses d'exemple**, pas des conditions de marché. Les modèles de catastrophe, la modélisation de la dépendance entre branches, et le traitement comptable et prudentiel de la réassurance dépassent ce chapitre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.1 à 6.10 (répartir huit sinistres entre trois traités, coefficient de variation selon la rétention, *burning cost*, courbe d'exposition, GPD, bootstrap, tranche de catastrophe, prime de risque, comparaison de programmes, contrepartie et épuisement) et exercices 6.1 à 6.12.

Le chapitre 7 change de sujet : il relie ce que l'on **doit** (le passif d'un assureur) à ce que l'on **détient** (ses placements), avec la gestion actif-passif et la théorie du portefeuille.
