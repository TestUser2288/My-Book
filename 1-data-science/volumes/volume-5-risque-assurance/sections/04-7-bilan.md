## Bilan du chapitre 4

Vous savez maintenant :

- **expliquer pourquoi on réglemente** les banques et les assureurs, et distinguer la **perte attendue** (provisionnée, facturée) de la **perte inattendue** (couverte par le capital) ;
- **lire un cadre prudentiel** : les trois piliers (exigences quantitatives, surveillance, transparence), les **ratios** (fonds propres sur actifs pondérés, levier, liquidité), les **niveaux** de fonds propres et les coussins ;
- **démontrer la formule IRB** à partir d'un modèle à un facteur ($K=\text{LGD}\,[\Phi((\Phi^{-1}(\mathrm{PD})+\sqrt\rho\,\Phi^{-1}(0{,}999))/\sqrt{1-\rho})-\mathrm{PD}]$), la **vérifier par simulation**, l'**appliquer** à un portefeuille de prêts (capital 5,5 % de l'exposition, poids de risque moyen 68,6 % contre 75 % en approche standard) et dire ce qu'elle suppose ;
- **construire un bilan économique d'assureur** : meilleure estimation, marge de risque par le coût du capital, **SCR agrégé** par une matrice de corrélation (345 M€ de somme, 241,8 M€ agrégés, 253,8 M€ avec le risque opérationnel), ratio de solvabilité et chocs, en sachant que l'agrégation est **exacte pour des pertes normales** et peut être prudente ou imprudente sinon ;
- **décrire le Takaful** (contribution à un fonds commun, deux fonds, opérateur rémunéré, prêt sans intérêt, supervision charia) et **ce qu'il change pour le modélisateur** ;
- (en option) **lire IFRS 17** (CSM libérée avec le service, perte immédiate sur contrat déficitaire, écart futur contre écart passé) et situer IFRS 9, le **plancher de 72,5 %** de Bâle III finalisé, et **aborder un cadre national** par des questions ;
- (en option) **comparer les modèles wakala, moudaraba et hybride** sur des données (le wakala à 20 % rémunère l'opérateur, la moudaraba pure le ruine, l'hybride équilibre) et situer les contrats de finance islamique ;
- (en option) **détecter des opérations suspectes** : variables par compte, règles avec fenêtre de temps, cycles dans un graphe, anomalies, apprentissage supervisé, et juger par le **rappel à capacité fixée**.

Le tableau suivant résume les **cadres** vus dans ce chapitre, avec ce qu'ils mesurent et d'où ils tirent leurs entrées.

| Cadre | Pour qui | Ce qu'il fixe | Mesure de risque | Entrées de vos modèles | Où |
|---|---|---|---|---|---|
| **Bâle** (IRB) | banques | fonds propres ≥ 8 % des RWA, plus coussins ; levier ; liquidité | perte au quantile 99,9 % sur un an, moins la perte attendue | PD, LGD, EAD (ch. 1) | 4.1 |
| **Solvabilité** | assureurs | SCR (fonds propres éligibles ≥ SCR), MCR | valeur en risque à 99,5 % sur un an des fonds propres | provisions (ch. 2), mesures de risque (ch. 3) | 4.2 |
| **Takaful** | opérateurs et participants | structure à deux fonds, prêt sans intérêt, supervision charia | les mêmes que l'assurance (technique identique) | fréquence, sévérité, provisions (ch. 2) | 4.3, 4.5 |
| **IFRS 17 / IFRS 9** | comptes d'assureurs / de banques | quand et comment reconnaître marges et pertes | espérance actualisée plus ajustement pour risque ; perte de crédit attendue | flux, PD/LGD (ch. 1 et 2) | 4.4 |
| **Lutte contre le blanchiment** | banques, assureurs | vigilance, surveillance, déclaration de soupçon | pas de mesure unique : charge d'alertes, rappel | transactions, graphes, étiquettes | 4.6 |

Quatre idées dépassent ce chapitre.

**D'abord, un capital réglementaire est un quantile, donc une convention.** Le 99,9 % des banques et le 99,5 % des assureurs ne sont pas des vérités mais des **niveaux de confiance choisis**, que chaque formule entoure d'hypothèses (un seul facteur, des corrélations imposées, une granularité infinie, des modules agrégés linéairement). Lire un ratio de capital, c'est lire ses hypothèses.

**Ensuite, la mesure est toujours un calcul sur des estimations.** PD, LGD, CCF, meilleure estimation, ajustement pour risque : chacun est estimé avec une incertitude qui se propage au capital (une LGD trop optimiste de 20 % donne un capital trop faible de 20 %). Le cadre répond par des **planchers**, des exigences de **validation** (section 3.4), un **ratio de levier** indépendant des modèles, et la **documentation**.

**Puis, le même risque se lit à plusieurs niveaux.** Perte attendue comptable (IFRS 9), perte attendue réglementaire (IRB), meilleure estimation d'assureur, CSM d'IFRS 17 : des conventions différentes, pour des objectifs différents (information financière, protection des déposants, protection des assurés). Dire laquelle on utilise est une partie du travail.

**Enfin, la détection d'opérations suspectes se juge sur la charge humaine.** Une règle sans fenêtre de temps, ou un modèle sans graphe, coûte des centaines d'examens inutiles ou des relations ratées ; le critère est le **rappel à capacité fixée**, et nos performances simulées sont toujours **optimistes**.

> ⚠️ **Rappel d'honnêteté.** Ce chapitre ne nomme ni pays ni autorité ; il présente la **logique** de cadres internationaux, d'après l'état des textes connu à la rédaction (2026), avec des paramètres d'illustration (coefficients, matrice de corrélation, taux de frais, seuils). **Rien n'y est un conseil juridique, comptable ou financier** : pour une décision réelle, lisez le texte en vigueur dans votre juridiction. Les données sont simulées et leurs schémas programmés ; les performances de détection sont donc **bien plus élevées** que dans la réalité.

Les chapitres complémentaires suivants prolongent ce chapitre : le chapitre 5 construit les **tables de mortalité** qui nourrissent l'assurance vie et son provisionnement ; le chapitre 6 explique comment une mutuelle **se protège** par la réassurance (ce que le module de défaut des contreparties de la section 4.2 mesure) ; le chapitre 7 traite de la **gestion actif-passif**, qui relie le bilan économique de la section 4.2 aux placements.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.8 (le capital IRB d'un portefeuille, la simulation du quantile à 99,9 %, la procyclicité, l'agrégation du SCR, la marge de risque et les chocs, la CSM d'IFRS 17, les modèles de Takaful, la détection d'opérations suspectes) et exercices 4.1 à 4.12.
