# Points clés

> « Une équation ne devient une compétence que le jour où l'on sait dire, sans notes, à quoi elle sert et quand elle ment. »

Ce dernier chapitre fixe **l'essentiel** de chaque chapitre du volume, pour pouvoir y revenir.

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. Régression linéaire** | $\hat{\boldsymbol\beta}=(\mathbf X^\top\mathbf X)^{-1}\mathbf X^\top\mathbf y$ est une **projection orthogonale** ; Gauss-Markov dit pourquoi c'est le meilleur estimateur linéaire sans biais. Un coefficient se lit « toutes choses égales par ailleurs ». On **vérifie** (résidus, levier, Cook, VIF) avant de **croire** les tests. Choisir un modèle : AIC, BIC, validation croisée, jamais le seul $R^2$. Régulariser (Ridge, Lasso), résister aux aberrations (Huber), tenir compte des groupes (effets mixtes). |
| **2. GLM** | Une **loi** de la famille exponentielle, un **prédicteur linéaire**, un **lien** : trois choix, un cadre. Estimation par **maximum de vraisemblance** (IRLS). Logistique pour 0/1 (rapport de cotes ≠ risque relatif), Poisson et binomiale négative pour les comptages, Gamma pour les montants, Tweedie pour les montants avec zéros. On vérifie : déviance, résidus, calibration. |
| **3. Analyse multivariée** | L'**ACP** diagonalise la matrice de covariance : elle *résume*. L'**analyse factorielle** *modélise* des facteurs cachés. **K-means** et classification hiérarchique regroupent sans étiquettes, mais **rendent toujours un résultat, même sur du bruit** : on vérifie par silhouette, stabilité, analyse parallèle. |
| **4. Séries temporelles** | L'ordre des observations compte. **Stationnarité** et **autocorrélation** sont le langage de base ; ARIMA et SARIMA modélisent la mémoire du passé et la saisonnalité. On évalue en **prévoyant des données non vues** (rétro-test), contre un repère naïf. |
| **5. Survie** | La **censure** rend biaisées les moyennes naïves. $S(t)=e^{-H(t)}$ relie survie, risque et risque cumulé. **Kaplan-Meier** estime la survie sans loi ; **Cox** mesure l'effet de variables sur le risque (hypothèse : risques proportionnels) ; les modèles paramétriques extrapolent. |
| **6. Bayésien et simulation** | **A posteriori ∝ vraisemblance × a priori.** Monte-Carlo remplace l'intégrale par une moyenne (erreur en $1/\sqrt n$) ; **MCMC** simule les lois qu'on ne sait pas calculer. Un échantillonneur se **diagnostique** ($\hat R$, ESS, traces) ; un modèle se **vérifie** (prédictive a posteriori). |
| **➕ 7. Causal** | Un effet causal est une différence entre deux mondes dont un seul est observé. La **randomisation** élimine le biais de sélection. En observationnel : DAG, score de propension, différence de différences, variable instrumentale. Chacune remplace l'information manquante par une **hypothèse**. |
| **➕ 8. Plans d'expériences** | Un bon plan (randomisation, répétition, blocs, facteurs variés **ensemble**) simplifie l'analyse. ANOVA, plans factoriels $2^k$, fractionnaires (alias, résolution), surfaces de réponse. |
| **➕ 9. Spatial** | Des observations voisines ne sont pas indépendantes. **Moran**, **variogramme**, **krigeage**, **fonction $K$** : un voisinage, une fonction de dépendance, une comparaison à un hasard bien défini. |
| **Projet** | Contrôler → regarder → modéliser → vérifier hors échantillon → quantifier l'incertitude → décider → reconnaître les limites. |

> 💡 **Cinq idées qui traversent tout le volume** (reprises de l'introduction).
>
> 1. Un modèle = un **signal** et un **bruit** explicitement séparés.
> 2. **Maximum de vraisemblance** : choisir les paramètres qui rendent les données les plus plausibles. Régression, GLM, ARIMA, survie en sont des cas ; le bayésien en est le prolongement.
> 3. **Un modèle s'évalue sur ce qu'il n'a pas vu.**
> 4. **Les hypothèses se vérifient.**
> 5. **Association n'est pas causalité.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 10 : le projet du volume (le plan 2026 de la boutique : prévision, régression logistique, modèle de Tweedie, modèle de Cox, valeur d'un client) et les quarante-deux questions d'auto-évaluation, avec leurs réponses et une grille pour savoir quelles sections relire.

## Et maintenant ?

Vous savez maintenant **construire, vérifier et interpréter** des modèles statistiques. Le **volume III : Apprentissage automatique** reprend le même cycle (données → modèle → évaluation hors échantillon → décision) avec des modèles plus flexibles (arbres, forêts, boosting, réseaux), dont l'objectif premier est la **prédiction**. Tout ce que vous avez appris ici ne devient pas inutile : la validation croisée, la régularisation, la vérification de modèles, la différence entre prédire et expliquer en sont le fondement.

> ✅ **À retenir, tout simplement.** Un modèle est une carte : il simplifie pour servir. Votre métier, désormais, consiste à savoir **ce que la carte montre**, **ce qu'elle cache**, et **comment vérifier** que vous n'avez pas oublié le fleuve.
