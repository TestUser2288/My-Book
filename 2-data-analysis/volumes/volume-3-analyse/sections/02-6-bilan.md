## Bilan du chapitre 2

Vous savez maintenant :

- **formuler un test** : une hypothèse nulle et une alternative, une statistique, une p-valeur lue correctement (la probabilité d'un écart au moins aussi grand **si rien ne se passait**), un seuil fixé à l'avance, deux erreurs possibles (type I, type II), et un **intervalle de confiance** pour dire la taille de l'effet ;
- **éviter les cinq contresens** sur la p-valeur, et ne jamais confondre **significatif** et **important**, ni **non significatif** et **absent** ;
- **choisir un test** selon la variable, le nombre de groupes et l'indépendance des observations : deux proportions ($z$, khi-deux, Fisher), deux moyennes (Welch), distributions asymétriques (Mann-Whitney, bootstrap), mesures appariées (t apparié, Wilcoxon), plusieurs groupes (ANOVA, Tukey, Kruskal-Wallis), répartitions (khi-deux) ;
- **concevoir un test A/B** : unité tirée au sort, métrique principale, garde-fous, taille et durée fixées à l'avance, règle de décision ; **lire** un test en commençant par la **répartition** (défaut de répartition), puis l'écart global et son intervalle, puis les sous-groupes **corrigés** (Holm) ;
- **repérer les pièges** : regarder en continu (un test sans effet « gagne » dans un cas sur quatre), comparer plusieurs sous-groupes, effet de nouveauté, interférences ;
- **mesurer une corrélation** (Pearson, Spearman, Kendall), son intervalle (transformation de Fisher), et la **neutraliser** quand une saison ou une tendance la fabrique ; ne pas conclure à la cause sans expérience ;
- (en option) **calculer la puissance** d'un test, la **taille d'échantillon** nécessaire, l'**effet minimal détectable** et la **durée** d'un test avec le trafic réel.

Voici ce que le chapitre a mesuré, avec la **vérité programmée** quand elle existe.

| Question | Ce que l'analyse a donné | Vérité programmée |
|---|---|---|
| E-mail : l'objet B augmente-t-il l'achat ? | +0,47 point (IC −0,16 à +1,09), $p=0{,}14$ : non conclusif | +0,4 point réel : **puissance de 24 %**, 30 400 par groupe auraient fallu |
| E-mail : ouverture, clic | +4,27 et +1,00 point, très significatifs | effet réel sur l'ouverture, répercuté sur le clic |
| Montant par contact | +0,37 € (IC −0,39 à +1,10 €) : pas de conclusion ; 1 % des contacts font 60 % des euros | pas d'effet sur le panier des acheteurs |
| Page de paiement : répartition 50/50 ? | 48,1 % de B, $\chi^2=56$ : **défaut de répartition** | filtre de robots appliqué au seul groupe B (−20 % d'ordinateurs) |
| Page de paiement : effet par appareil | mobile +0,57 pt, $p=0{,}025$, **0,075 après Holm** | +0,75 pt sur mobile, 0 ailleurs : effet réel, non démontrable |
| Regarder chaque jour un test A/A | environ 1 test sur 4 « gagne » au moins un jour | aucun effet |
| Publicité × commandes | corrélation 0,53, **0,11 à mois égal** ; coefficient contrôlé 0,006 (IC −0,0004 à +0,0124) | +1,5 % pour 1 000 € hebdomadaires, soit 0,0035 : dans l'intervalle |
| Promotion × commandes | corrélation brute avec le CA −0,01 ; effet contrôlé +19 % | +18 % |
| Séries temporelles indépendantes | 41 % des paires avec $|r|>0{,}5$ ; presque aucune sur les variations | aucun lien |

Quatre idées dépassent ce chapitre. **Un test se prépare avant de se lire** : l'effet qui compte, la taille nécessaire et la règle de décision s'écrivent avant le lancement. **L'intervalle de confiance est plus informatif que la p-valeur** : il donne la taille et l'incertitude. **Regarder souvent, comparer beaucoup, s'arrêter tôt** multiplient les faux positifs : fixez le plan d'analyse à l'avance. **Une corrélation est une question** : la saison, la tendance et la sélection la fabriquent facilement ; seule une expérience tranche. Le chapitre 3 prolonge la dernière idée : la **régression** permet de comparer « toutes choses égales par ailleurs » quand l'expérience est impossible.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : applications 2.1 à 2.8 (mélange des étiquettes, lecture d'un test d'e-mail, défaut de répartition et sous-groupes, arrêt prématuré, corrélation à saison égale, séries à tendance, choix d'un test, taille et durée d'un test) et exercices 2.1 à 2.14.
