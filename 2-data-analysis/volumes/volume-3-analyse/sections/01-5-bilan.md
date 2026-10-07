## Bilan du chapitre 1

Vous savez maintenant :

- **explorer** une variable seule avec la méthode en trois gestes (résumer, dessiner, écrire une phrase) : médiane, quartiles et centiles pour une variable asymétrique, **échelle logarithmique** pour les montants, **bâtons** pour une variable discrète, **barres ordonnées** pour une qualitative, **courbe** pour une série ;
- **choisir les classes** d'un histogramme (règles de Sturges et de Freedman-Diaconis, essai de deux ou trois valeurs) et éviter trois pièges de lecture : la moyenne, l'axe tronqué, les trop nombreuses classes ;
- **explorer des relations** selon le type des deux variables (nuage et corrélation, boîtes et moyennes avec intervalle, tableaux croisés et profils, matrice de corrélation), et lire un **indicateur de force** comme le V de Cramér ;
- **reconnaître un facteur de confusion** (la saison) en comparant « à saison égale », et un **paradoxe de Simpson** (les jours de promotion rapportent moins en moyenne, mais plus à mois égal) ;
- **mesurer les motifs réguliers** (indice par jour de la semaine et par mois) et un **changement de niveau** à composition constante (la hausse de prix de 3 %) ;
- **détecter des incidents** avec une référence locale, un écart relatif et un score z robuste (MAD), **évaluer** la méthode par précision et rappel, et **distinguer** erreur, événement et régularité mal connue ;
- (en option) **dérouler une liste de contrôle** d'exploration, en automatiser le premier tour et rédiger le compte rendu d'une page.

Le tableau suivant résume **ce que nous avons mesuré** sur les données de la boutique, avec, quand elle est connue, la **vérité programmée**.

| Question | Résultat mesuré | Ce qu'il faut en retenir |
|---|---|---|
| Panier : moyenne et médiane | 100,4 € et 79,8 € ; asymétrie 1,85 | six commandes sur dix sont sous la moyenne ; annoncer la médiane |
| Règle des « 68 % » sur le panier | 78,2 % à moins d'un écart-type | l'écart-type ne se lit pas comme pour une cloche |
| Le panier, en logarithme | asymétrie −0,71 | l'échelle logarithmique ramène la forme vers une cloche |
| Classes d'un histogramme | 17 (Sturges) contre 177 (Freedman-Diaconis) | essayer deux ou trois valeurs |
| Délais de livraison | médiane 6 jours ; 96,2 % en 8 jours ou moins | pour un niveau de service, utiliser des centiles |
| Chiffre d'affaires annuel | 1 139, 1 189 puis 1 325 k€ (+4,4 % puis +11,4 %) | saison forte (février à décembre) et tendance |
| Corrélation publicité - commandes | 0,53 au total, 0,10 à mois égal | la saison explique l'essentiel du lien |
| Panier selon le canal | 100,9 ; 99,8 ; 100,5 € (intervalles qui se recouvrent) | pas de différence détectable entre canaux |
| Délai selon le transporteur | 5,2 ; 5,8 ; 6,7 jours (intervalles disjoints) | le transporteur C est nettement plus lent |
| Taux de retour par canal | 3,1 % ; 6,7 % ; 9,0 % (V de Cramér 0,118) | le canal compte pour les retours, pas pour les codes promo (0,010) |
| Promotion et chiffre d'affaires | 3 300 € contre 3 339 € au total, mais plus dans chaque mois comparable | paradoxe de Simpson : comparer à saison égale |
| Rythme hebdomadaire | samedi 1,39 fois la moyenne, dimanche 0,67 | une « journée typique » n'existe pas |
| Hausse de prix de 2025 | invisible dans le panier mensuel ; indice 1,000 puis 1,030 à produits constants | comparer à composition constante |
| Règle des 1,5 écart interquartile sur le chiffre d'affaires | 29 jours signalés, 90 % en novembre ou décembre | la saison fait de fausses alertes |
| Détection d'incidents (seuil 4) | 11 jours signalés, 6 vrais sur 8 : précision 55 %, rappel 75 % | un seuil est un arbitrage entre fausses alertes et incidents ratés |

Le fil conducteur du chapitre tient en une phrase : **avant de modéliser, regardez, dessinez et comparez des choses comparables**. Chaque résultat de l'exploration est une **question mieux posée** : *la publicité fait-elle vendre à saison égale ? Le transporteur C explique-t-il les retards ? La promotion augmente-t-elle les commandes de combien ?* Les chapitres suivants y répondent avec des outils qui mesurent l'incertitude : tests et A/B (chapitre 2), régression (chapitre 3), segmentation (chapitre 4), séries temporelles (chapitre 5).

> 🧭 **En pratique : liste de contrôle avant de passer à la suite.**
> 1. On sait ce que représente **une ligne** et ce qui l'identifie (1.0, 1.4).
> 2. Chaque variable importante a **sa phrase** (1.1) ; les montants ont été regardés en échelle logarithmique.
> 3. Les comparaisons de groupes ont des **intervalles**, et l'on a cherché la variable de confusion (1.2).
> 4. Les **rythmes** (semaine, saison) sont connus, les anomalies datées et **qualifiées** (erreur, événement, régularité) (1.3).
> 5. Le **compte rendu d'une page** est écrit (1.4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.7 (résumer le panier, choisir les classes, nuages et saison, comparer les groupes, profils hebdomadaires et indice de prix, détecter des incidents, rapport automatique) et exercices 1.1 à 1.14.

Le chapitre 2 aborde la question qui suit naturellement l'exploration : **cette différence est-elle réelle, ou due au hasard ?** C'est le sujet des tests d'hypothèses et des tests A/B.
