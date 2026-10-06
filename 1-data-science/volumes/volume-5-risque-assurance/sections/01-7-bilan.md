## Bilan du chapitre 1

Vous savez maintenant :

- **cadrer** un score de crédit : population, définition du défaut, fenêtres d'observation et de performance, échantillons, et le garde-fou contre la fuite d'information (ne garder que ce que l'on sait à la date de la demande) ;
- **construire une grille de score** : découper en classes, calculer les **WOE** (à la main sur un exemple), estimer une régression logistique, écrire le résultat en **points** avec un score de base et un PDO, lire une carte et en expliquer un refus par ses **motifs** ;
- **mesurer l'effet des dossiers refusés** : une grille construite sur les seuls acceptés annonce 4,4 % de défaut alors que la population qui se présente en fait 6,0 % ;
- **comparer** une grille, une logistique brute et un boosting monotone sur un échantillon de test, avec des intervalles appariés, et comprendre **pourquoi** (la forme des effets, révélée par la vérité programmée) ;
- **mesurer** un score : AUC, **Gini = 2·AUC − 1** (démontré par la courbe CAP), **KS**, tableau de seuils, intervalle de bootstrap, **PSI**, calibration par note (test binomial, Hosmer–Lemeshow) et ses limites quand la conjoncture corrèle les défauts ;
- (en option) **juger un découpage** : IV (une divergence de Kullback–Leibler symétrisée), fusion monotone, classes rares, manquants informatifs, IV suspect ;
- (en option) **chiffrer une perte attendue** : PD à 12 mois et sur la vie, LGD (en U, peu prévisible individuellement), CCF et EAD, **trois étapes IFRS 9**, scénarios macroéconomiques pondérés et effet de convexité ;
- (en option) **estimer une matrice de migration**, voir la conjoncture la déformer, calculer une PD à plusieurs années par puissance de matrice, **tester** Markov et noter les limites de l'homogénéité et du temps continu.

Le chapitre a mis des chiffres sur des idées qui restent souvent des slogans :

| Question | Ce que nous avons mesuré |
|---|---|
| Performance de la grille (test) | AUC 0,771 [0,752 ; 0,791], Gini 0,542, KS 0,406 |
| Grille contre logistique brute | +0,010 d'AUC, intervalle apparié [+0,001 ; +0,018] |
| Grille contre boosting monotone | −0,002 d'AUC, dans le bruit ; plafond (vraies formes) : 0,777 |
| Politique d'acceptation à 560 points | 78 % de demandes acceptées, 3,1 % de défaut parmi les acceptés |
| Grille construite sur les acceptés seuls | AUC 0,716 au lieu de 0,771 ; PD annoncée 4,4 % pour 6,0 % réels |
| Afflux de jeunes emprunteurs | PSI du score 0,129, de l'âge 0,246 ; la grille reste calibrée (8,7 % annoncés, 8,9 % observés) |
| Test binomial, 80 trimestres | 65 rejets ; sous une corrélation d'actifs de 3 %, il rejette à tort 85 % du temps |
| Jeu réel (carte de crédit) | AUC 0,728 (tout en nombres), 0,768 (statut en modalités), 0,791 (boosting) |
| IV d'une variable de bruit | 0,055 en développement, −0,016 en test (100 classes) |
| Ancienneté dans l'emploi | IV 0,258 avec le manquant en classe à part, 0,163 après imputation |
| LGD | moyenne 46 % (61 % sans garantie, 27 % avec caution) ; $R^2$ de 0,22, plafond compris |
| EAD d'une ligne renouvelable | CCF moyen 0,40 ; EAD sous-estimée de 39 % si l'on ignore les tirages futurs |
| Perte attendue IFRS 9 | 7,6 M€ (2,5 % de 302 M€) ; 10,8 M€ en pondérant trois scénarios, soit 43 % de plus |
| Migration en récession | PD des notes intermédiaires multipliée par 2,5 à 3,9 |
| PD à 5 ans de la note 5 | 17,0 % (matrice estimée), 13,3 % (matrice neutre), 10,8 % (cohorte observée avant la récession) |

Le fil conducteur du chapitre tient en une phrase : **un score de crédit est une cote écrite en points, et sa valeur se mesure par des indicateurs qui répondent à des questions différentes** (classe-t-il bien, est-il calibré, est-il stable, avec quelle incertitude). Chaque fois que nous avons comparé des modèles, la sophistication a apporté moins que la **forme des effets** et la **qualité des données** ; chaque fois que nous avons traduit un score en euros, l'hypothèse sur la conjoncture a pesé davantage que le modèle.

> 🧭 **En pratique : liste de contrôle d'un score de crédit.**
> 1. La population, la définition du défaut et les fenêtres sont écrites (1.1.2).
> 2. Aucune variable n'est postérieure à la date de la demande ; aucun IV n'est anormalement élevé (1.4.4).
> 3. Les classes sont assez peuplées, justifiées, monotones quand l'économie l'exige (1.1.3, 1.4.3).
> 4. Les refusés sont discutés : l'échantillon est-il représentatif des demandeurs (1.1.7) ?
> 5. Gini, KS, AUC sont donnés **avec leur intervalle**, sur un échantillon de test (1.3.5).
> 6. La calibration est contrôlée par note, avec un test qui tient compte de la corrélation (1.3.7).
> 7. La stabilité est surveillée (PSI du score et des variables, 1.3.6).
> 8. Les motifs de refus se lisent dans la carte (1.2.6).
> 9. La PD alimente une perte attendue avec LGD, EAD et scénarios documentés (1.5).

Le chapitre suivant change de métier, pas de logique : l'**assurance**. Une mutuelle ne prête pas, elle **promet** de payer des sinistres ; son risque est la **fréquence** et le **coût** de ces sinistres, que l'on modélise séparément et que l'on transforme en **prix** (un tarif) et en **provisions**, un chemin parallèle à celui de la PD, de la LGD et de l'EAD.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.8 (grille complète, inférence des rejets, comparaison de modèles, performance et stabilité, WOE et fusion monotone, LGD et CCF, perte attendue IFRS 9, matrice de migration) et exercices 1.1 à 1.14.
