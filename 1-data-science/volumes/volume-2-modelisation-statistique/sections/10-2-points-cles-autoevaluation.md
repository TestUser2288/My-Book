# Points clés et auto-évaluation

> « Une équation ne devient une compétence que le jour où l'on sait dire, sans notes, à quoi elle sert et quand elle ment. »

Ce dernier chapitre a deux rôles : **fixer l'essentiel** de chaque chapitre, et vous donner un moyen **honnête** de savoir si le volume a fait son travail : quarante-deux questions (trente-six sur les chapitres principaux, six sur les chapitres facultatifs), leurs réponses, et une grille d'auto-évaluation.

## Les points clés, chapitre par chapitre

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
> 1. Un modèle = un **signal** et un **bruit** explicitement séparés.
> 2. **Maximum de vraisemblance** : choisir les paramètres qui rendent les données les plus plausibles. Régression, GLM, ARIMA, survie en sont des cas ; le bayésien en est le prolongement.
> 3. **Un modèle s'évalue sur ce qu'il n'a pas vu.**
> 4. **Les hypothèses se vérifient.**
> 5. **Association n'est pas causalité.**

## Quarante-deux questions

**Mode d'emploi.** Répondez à voix haute ou par écrit **avant** de lire le corrigé, en une ou deux phrases. Les sections à relire sont indiquées dans le corrigé. Trente bonnes réponses sur les trente-six premières signalent un volume bien assimilé.

### Régression linéaire (chapitre 1)

1. Que sont les équations normales, et que représente géométriquement la solution des moindres carrés ?
2. Dans une régression de $\ln(\text{panier})$ sur le canal, le coefficient de « Boutique » (par rapport à « Instagram ») vaut $0{,}22$. De combien de pourcents le panier est-il plus élevé en boutique ?
3. Quelle est la différence entre un intervalle de confiance pour la **réponse moyenne** et un intervalle de **prédiction** ? Lequel est le plus large, et pourquoi ?
4. Deux variables explicatives ont une corrélation de $0{,}95$. Quel est le facteur d'inflation de la variance (VIF) de chacune, et que cela signifie-t-il ?
5. Pourquoi ne faut-il pas choisir le modèle qui a le plus grand $R^2$ ?
6. Lequel de Ridge et de Lasso peut annuler exactement des coefficients, et pourquoi ?

### Modèles linéaires généralisés (chapitre 2)

7. Quels sont les trois ingrédients d'un GLM ?
8. Une régression logistique donne, pour l'offre de bienvenue, un coefficient de $0{,}49$. Le taux de rachat sans offre est de $44{,}8\ \%$. Quel est le taux avec offre, selon le modèle ?
9. Qu'est-ce que la surdispersion d'un comptage, et que faire ?
10. Pourquoi une régression Gamma à lien logarithmique convient-elle à des montants positifs ?
11. Que mesure la déviance, et comment compare-t-on deux modèles emboîtés ?
12. Vos dépenses annuelles contiennent 13 % de zéros exacts et une partie positive asymétrique. Citez deux modèles adaptés.

### Analyse multivariée (chapitre 3)

13. Les valeurs propres de la matrice de corrélation de quatre variables sont $2{,}4$, $1$, $0{,}4$ et $0{,}2$. Quelle part de la variance la première composante résume-t-elle ?
14. Quand faut-il standardiser les variables avant une ACP ?
15. Quelle différence de nature entre l'ACP et l'analyse factorielle ?
16. Comment choisir le nombre de composantes ou de facteurs ?
17. Que minimise l'algorithme des k-means, et pourquoi le lance-t-on plusieurs fois ?
18. Pourquoi une silhouette élevée ne suffit-elle pas à prouver qu'il y a des groupes ?

### Séries temporelles (chapitre 4)

19. Qu'est-ce qu'une série faiblement stationnaire ?
20. Quelle est l'allure de l'ACF d'un AR(1) avec $\varphi=0{,}8$ ? Quelle est sa valeur au retard 3 ?
21. Dans un test de Dickey-Fuller augmenté, quelle est l'hypothèse nulle, et que conclut-on d'une p-valeur de $0{,}40$ ?
22. Pourquoi ne peut-on pas comparer par l'AIC un modèle différencié et un modèle qui ne l'est pas ?
23. Qu'est-ce qu'un rétro-test (*rolling origin*) et pourquoi compare-t-on toujours à un repère naïf ?
24. Un modèle SARIMA a des résidus dont la statistique de Ljung-Box donne $p=0{,}002$. Que faire ?

### Analyse de survie (chapitre 5)

25. Pourquoi la durée moyenne calculée sur les seuls clients partis est-elle biaisée ?
26. Un client part à taux constant de $0{,}05$ par mois. Quelle est la durée médiane de la relation ?
27. Cinq clients ont les durées observées $2,\ 3^+,\ 5,\ 7,\ 8^+$ mois ($^+$ : censuré). Calculez à la main l'estimateur de Kaplan-Meier à 2, 5 et 7 mois.
28. Un rapport de risques de $0{,}67$ pour l'offre de bienvenue : que signifie-t-il, et quelle hypothèse suppose le modèle de Cox ?
29. Quelle est l'hypothèse nulle du test du log-rank ?
30. Pourquoi « $1-$ Kaplan-Meier » surestime-t-il l'incidence d'une cause en présence de risques concurrents ?

### Statistique bayésienne et simulation (chapitre 6)

31. Prior Beta(1, 1), puis 12 rachats sur 20 clients : quelle est la loi a posteriori, et sa moyenne ?
32. Différence entre un intervalle de crédibilité à 95 % et un intervalle de confiance à 95 % ?
33. Un écart-type de simulation de $0{,}5$ : combien de tirages Monte-Carlo pour que l'erreur-type de la moyenne soit de $0{,}001$ ?
34. Dans Metropolis-Hastings, avec une proposition symétrique, quelle est la probabilité d'accepter un candidat $x'$ depuis $x$ ? Pourquoi la constante de normalisation de la loi cible n'est-elle pas nécessaire ?
35. Quatre chaînes MCMC donnent un $\hat R$ de $1{,}4$. Que faire ?
36. Qu'est-ce qu'une vérification prédictive a posteriori ?

### Chapitres facultatifs (7, 8, 9)

37. Faut-il ajuster sur une cause commune ? Sur un effet commun (collision) ? Pourquoi ?
38. Pourquoi la randomisation permet-elle une lecture causale de l'écart de moyennes ?
39. Une variable instrumentale (un rappel envoyé au hasard) augmente la dépense moyenne de $3$ DT et la probabilité d'ouvrir le courriel de $0{,}6$. Quel est l'estimateur de Wald ?
40. Trois groupes de 10 observations : $SC_{\text{inter}}=24$ et $SC_{\text{intra}}=60$. Quelle est la statistique $F$ de l'ANOVA ?
41. Combien d'essais faut-il pour un plan factoriel complet à trois facteurs à deux niveaux, et que calcule-t-on pour l'effet principal d'un facteur ?
42. Un indice de Moran de $+0{,}4$ avec $n=50$ : que cela indique-t-il, et quelle est son espérance sous l'indépendance spatiale ?

## Vérifier les réponses chiffrées

Pour les questions numériques, **calculons** plutôt que de nous fier à la mémoire.

```python
import numpy as np
from scipy import stats

# Q2 : coefficient d'un modèle en logarithme
print(f"Q2  exp(0,22) - 1 = {100 * (np.exp(0.22) - 1):.1f} %")

# Q4 : VIF pour deux variables de corrélation 0,95
r = 0.95
print(f"Q4  VIF = 1 / (1 - r^2) = {1 / (1 - r**2):.2f}")

# Q8 : rapport de cotes -> probabilité
p0, coef = 0.448, 0.49
cotes = p0 / (1 - p0) * np.exp(coef)
print(f"Q8  rapport de cotes = {np.exp(coef):.3f} ; probabilité avec offre = {cotes / (1 + cotes):.3f}")

# Q13 : part de variance de la première composante (matrice de corrélation : somme des valeurs propres = nombre de variables)
vp = np.array([2.4, 1.0, 0.4, 0.2])
print(f"Q13 {vp[0] / vp.sum():.0%} de la variance")

# Q20 : ACF de l'AR(1)
print("Q20 ACF aux retards 1, 2, 3 :", [round(0.8**k, 3) for k in (1, 2, 3)])

# Q26 : médiane d'une durée exponentielle
print(f"Q26 ln(2) / 0,05 = {np.log(2) / 0.05:.2f} mois")

# Q27 : Kaplan-Meier à la main
durees = np.array([2, 3, 5, 7, 8]); evenements = np.array([1, 0, 1, 1, 0])
S = 1.0
for t in sorted(durees[evenements == 1]):
    a_risque = np.sum(durees >= t)
    S *= 1 - 1 / a_risque
    print(f"Q27 t = {t} : {a_risque} à risque, S = {S:.4f}")

# Q31 : bêta-binomiale
a, b = 1 + 12, 1 + 8
print(f"Q31 posteriori Beta({a}, {b}), moyenne = {a / (a + b):.3f}, IC crédible 95 % = [{stats.beta.ppf(0.025, a, b):.3f} ; {stats.beta.ppf(0.975, a, b):.3f}]")

# Q33 : taille de simulation
print(f"Q33 n = (0,5 / 0,001)^2 = {(0.5 / 0.001) ** 2:,.0f}")

# Q39 : Wald
print(f"Q39 3 / 0,6 = {3 / 0.6:.1f} DT")

# Q40 : F de l'ANOVA
k, n = 3, 30
F = (24 / (k - 1)) / (60 / (n - k))
print(f"Q40 F = {F:.2f}, p = {stats.f.sf(F, k - 1, n - k):.4f}")

# Q42 : espérance de l'indice de Moran
print(f"Q42 E[I] = -1/(n-1) = {-1 / 49:.4f}")
```
<!--sortie-->
```text
Q2  exp(0,22) - 1 = 24.6 %
Q4  VIF = 1 / (1 - r^2) = 10.26
Q8  rapport de cotes = 1.632 ; probabilité avec offre = 0.570
Q13 60% de la variance
Q20 ACF aux retards 1, 2, 3 : [0.8, 0.64, 0.512]
Q26 ln(2) / 0,05 = 13.86 mois
Q27 t = 2 : 5 à risque, S = 0.8000
Q27 t = 5 : 3 à risque, S = 0.5333
Q27 t = 7 : 2 à risque, S = 0.2667
Q31 posteriori Beta(13, 9), moyenne = 0.591, IC crédible 95 % = [0.384 ; 0.782]
Q33 n = (0,5 / 0,001)^2 = 250,000
Q39 3 / 0,6 = 5.0 DT
Q40 F = 5.40, p = 0.0106
Q42 E[I] = -1/(n-1) = -0.0204
```

## Corrigé

**1.** Les **équations normales** $\mathbf X^\top\mathbf X\,\boldsymbol\beta=\mathbf X^\top\mathbf y$ expriment que le résidu est **orthogonal** à toutes les colonnes de $\mathbf X$. Géométriquement, $\mathbf X\hat{\boldsymbol\beta}$ est la **projection orthogonale** de $\mathbf y$ sur le sous-espace engendré par les colonnes de $\mathbf X$. (1.1)

**2.** $e^{0{,}22}-1\approx 24{,}6\ \%$ : en boutique, le panier est environ **un quart plus élevé**, toutes choses égales par ailleurs. Dans un modèle en logarithme, un coefficient $\beta$ se lit comme un effet **multiplicatif** $e^\beta$, et non comme une différence en dinars. (1.1)

**3.** L'intervalle sur la **réponse moyenne** encadre la valeur moyenne de $y$ pour des valeurs données de $x$ ; l'intervalle de **prédiction** encadre une **nouvelle observation** individuelle. Le second est plus large : il ajoute la variance du bruit individuel $\sigma^2$ à l'incertitude sur la moyenne. (1.2)

**4.** $\text{VIF}=1/(1-r^2)\approx10{,}26$ : la variance du coefficient est multipliée par plus de dix à cause de la colinéarité. On interprète mal chaque coefficient séparément, même si les prédictions restent correctes. (1.3)

**5.** Le $R^2$ **ne peut qu'augmenter** quand on ajoute des variables, même du bruit pur : il récompense le sur-ajustement. On choisit avec l'AIC, le BIC, le $R^2$ ajusté, ou, mieux, une **validation croisée** sur des données non utilisées pour l'ajustement. (1.4)

**6.** Le **Lasso** (pénalité $\ell_1$), parce que la géométrie de la contrainte $\sum|\beta_j|\le t$ a des **coins** sur les axes : la solution tombe souvent dessus. Ridge (pénalité $\ell_2$, contrainte sphérique) rétrécit tous les coefficients sans jamais les annuler exactement. (1.5)

**7.** Une **loi** de la famille exponentielle pour la réponse, un **prédicteur linéaire** $\eta=\mathbf x^\top\boldsymbol\beta$, et une **fonction de lien** $g$ qui relie la moyenne au prédicteur : $g(\mu)=\eta$. (2.1)

**8.** Environ **57 %** : les cotes sans offre valent $0{,}448/0{,}552\approx0{,}81$, multipliées par $e^{0{,}49}\approx1{,}63$, puis reconverties en probabilité. Le rapport de cotes de $1{,}63$ n'est **pas** un rapport de probabilités : une cote multipliée par $1{,}63$ ne multiplie pas la probabilité par $1{,}63$. (2.2)

**9.** Il y a **surdispersion** quand la variance observée dépasse la moyenne, alors que la loi de Poisson impose variance = moyenne. Les erreurs-types sont alors trop optimistes. On passe à une loi **binomiale négative**, ou à un Poisson avec erreurs-types robustes (quasi-vraisemblance). (2.3)

**10.** Les montants sont **strictement positifs** et leur variabilité **croît avec le niveau** (écart-type proportionnel à la moyenne), ce que fait la loi Gamma ($\operatorname{Var}=\phi\mu^2$). Le lien logarithmique garantit des moyennes positives et donne des effets **multiplicatifs**. (2.3)

**11.** La **déviance** est $2(\ell_{\text{saturé}}-\ell_{\text{modèle}})$ : l'écart de vraisemblance au modèle parfait. Pour deux modèles **emboîtés**, la différence de déviances suit approximativement une loi du $\chi^2$ dont les degrés de liberté valent le nombre de paramètres en plus (test du rapport de vraisemblance). (2.4)

**12.** Un modèle de **Tweedie** (avec $1<p<2$), qui mêle masse en zéro et partie positive continue ; ou un **modèle en deux parties** (logistique pour « dépense nulle ou non », puis Gamma sur les dépenses positives). (2.6)

**13.** $2{,}4/4=60\ \%$ (la somme des valeurs propres d'une matrice de corrélation vaut le nombre de variables). (3.1)

**14.** Quand les variables ont des **unités ou des échelles différentes** (dinars, âges, notes) : sans standardisation, la variable de plus grande variance domine l'ACP. Avec des variables de même nature et de même échelle, on peut travailler sur la matrice de covariance. (3.1)

**15.** L'ACP **résume** : elle cherche les combinaisons de variables de variance maximale, sans modèle. L'analyse factorielle **modélise** : elle suppose que les corrélations viennent de facteurs cachés, avec une part de bruit propre à chaque variable ($\Sigma=\Lambda\Lambda^\top+\Psi$). (3.2)

**16.** Éboulis des valeurs propres (le coude), critère de Kaiser (valeurs propres $>1$, à manier avec prudence), et surtout **analyse parallèle** (comparaison à des données sans structure), ajoutés à l'interprétabilité. En analyse factorielle, on dispose en plus d'un **test d'ajustement**. (3.1 et 3.2)

**17.** La **somme des carrés intra-classes** (inertie intra). L'algorithme converge vers un **minimum local** qui dépend de l'initialisation : on le lance plusieurs fois (avec k-means++) et on garde le meilleur. (3.3)

**18.** Parce qu'un nuage **sans structure** mais asymétrique peut aussi obtenir une silhouette élevée : une méthode de classification rend toujours des groupes. Il faut comparer à une référence sans groupes et tester la **stabilité** (rééchantillonnage, indice de Rand ajusté). (3.3)

**19.** Une série dont l'**espérance** est constante, la **variance** constante et dont l'**autocovariance** ne dépend que du décalage entre les dates, pas des dates elles-mêmes. (4.1)

**20.** Une décroissance **géométrique** : $\rho(k)=\varphi^k$, soit $0{,}8$, $0{,}64$ et $0{,}512$ aux retards 1, 2 et 3. (4.1 et 4.2)

**21.** L'hypothèse nulle est la **présence d'une racine unitaire** (non-stationnarité). Une p-valeur de $0{,}40$ ne permet pas de la rejeter : la série est compatible avec une marche aléatoire ; on la différencie. (« Ne pas rejeter » n'est pas « prouver ».) (4.1)

**22.** Parce que la vraisemblance porte sur **des données différentes** : la série différenciée a moins d'observations et une autre échelle. L'AIC ne se compare qu'entre modèles ajustés **à la même série**. Pour arbitrer entre ordres de différenciation, on compare des **prévisions hors échantillon**. (4.2 et 4.3)

**23.** On prévoit à plusieurs **origines successives** : on ajuste sur le passé jusqu'à $t$, on prévoit $t+1,\dots,t+h$, on avance $t$ et on recommence, pour mesurer des erreurs sur des données jamais vues. Le **repère naïf** (la dernière valeur, ou la même saison l'an passé) fixe le seuil à battre : un modèle sophistiqué qui ne le bat pas ne sert à rien. (4.3)

**24.** Une p-valeur de $0{,}002$ signale une **autocorrélation résiduelle** : le modèle a laissé du signal. On ajoute des termes AR/MA ou saisonniers, on traite une rupture ou un choc non modélisé, puis on relance les diagnostics. (4.2)

**25.** Parce qu'on ne regarde que les clients **partis tôt** : les clients fidèles, qui restent encore au moment de l'analyse, sont exclus alors que ce sont eux qui ont les durées les plus longues. La moyenne est donc sous-estimée. (5.1)

**26.** Pour un risque constant $\lambda$, $S(t)=e^{-\lambda t}$, et la médiane vaut $\ln 2/\lambda\approx13{,}86$ mois. (5.1)

**27.** À 2 mois, 5 clients à risque, 1 départ : $S=0{,}8$. À 5 mois, il reste 3 clients à risque (5, 7 et $8^+$), 1 départ : $S=0{,}8\times\tfrac23\approx0{,}5333$. À 7 mois, il en reste 2 à risque, 1 départ : $S=0{,}5333\times\tfrac12\approx0{,}2667$. Le client censuré à 3 mois n'est plus à risque après, mais **il a compté** dans le dénominateur jusqu'à sa sortie. (5.2)

**28.** Le risque instantané de départ des clients avec offre vaut **67 % de celui** des clients sans offre, à chaque instant, soit **33 % de moins**. Le modèle de Cox suppose les **risques proportionnels** : ce rapport est le même à toutes les dates. On le vérifie (graphique log-log, test de Grambsch-Therneau). (5.3)

**29.** Que les **fonctions de survie des groupes sont égales** à toutes les dates. (5.2)

**30.** Parce que « $1-$ Kaplan-Meier » traite les départs pour les **autres causes** comme des censures, comme si ces clients allaient encore pouvoir partir pour la cause étudiée. Or ils ne le peuvent plus : l'incidence est donc surestimée. On utilise l'estimateur d'**Aalen-Johansen** de l'incidence cumulée. (5.5)

**31.** $\text{Beta}(13,\,9)$ : on ajoute les succès à $a$ et les échecs à $b$. La moyenne vaut $13/22\approx0{,}591$ ; l'intervalle de crédibilité à 95 % est donné par le code ci-dessus. (6.1)

**32.** L'intervalle de **crédibilité** dit : « *étant donné les données et l'a priori*, le paramètre a 95 % de chances d'être dans cet intervalle ». L'intervalle de **confiance** dit : « la *méthode* encadre la vraie valeur dans 95 % des échantillons possibles ». Le premier est une probabilité sur le paramètre, le second une propriété de la procédure. (6.1)

**33.** $(0{,}5/0{,}001)^2=250\,000$ tirages : l'erreur décroît en $1/\sqrt n$, donc pour la diviser par dix il faut cent fois plus de tirages. (6.2)

**34.** On accepte avec la probabilité $\min\!\left(1,\ \pi(x')/\pi(x)\right)$. Le rapport $\pi(x')/\pi(x)$ **simplifie la constante de normalisation**, inconnue en général (c'est l'intégrale du produit vraisemblance × a priori) : elle apparaît au numérateur et au dénominateur. (6.3)

**35.** Un $\hat R$ de $1{,}4$ (bien supérieur à $1{,}01$) indique que les chaînes **n'ont pas convergé vers la même loi**. Ne pas utiliser les résultats : allonger les chaînes, revoir la paramétrisation, le pas de la proposition, les valeurs initiales, ou le modèle lui-même (multimodalité). (6.4)

**36.** On **simule des jeux de données** à partir du modèle ajusté (en tirant les paramètres dans leur loi a posteriori), et on regarde si les données observées ressemblent à ces répliques sur une statistique bien choisie (variance, nombre de zéros, maximum). Si les données réelles sortent de la distribution des répliques, le modèle ne reproduit pas un aspect important. (6.4)

**37.** Sur une **cause commune** (variable de confusion) : oui, on ajuste, pour bloquer le chemin de confusion. Sur un **effet commun** (collision) : **non**, car conditionner sur un effet commun **ouvre** un chemin artificiel entre ses deux causes et crée une association qui n'existe pas. (7.1)

**38.** Parce que, l'affectation étant faite au hasard, les groupes sont **comparables en moyenne sur tout**, y compris sur ce qu'on n'observe pas. L'écart de moyennes mesure alors uniquement l'effet du traitement : le **biais de sélection** est nul en espérance. (7.1)

**39.** $3/0{,}6=5$ DT : l'effet du rappel sur la dépense (forme réduite) divisé par son effet sur l'ouverture du courriel (première étape). C'est l'effet moyen **pour les « complaisants »**, c'est-à-dire ceux dont le comportement change à cause du rappel. (7.4)

**40.** $F=\dfrac{24/2}{60/27}=5{,}40$, avec 2 et 27 degrés de liberté ; la p-valeur est donnée par le code. (8.2)

**41.** $2^3=8$ essais. L'effet principal d'un facteur est la **différence entre la moyenne des réponses au niveau haut et la moyenne au niveau bas**, calculée sur les 4 essais de chaque niveau. (8.3)

**42.** Un indice **positif** indique une **autocorrélation spatiale positive** : des zones voisines se ressemblent plus que ne le voudrait le hasard. Son espérance sous indépendance est $-1/(n-1)=-1/49\approx-0{,}0204$. On teste ensuite l'écart par **permutations**. (9.2)

## Votre grille d'auto-évaluation

Pour chaque ligne : **je sais l'expliquer** / **je sais le faire** / **à revoir**.

| Compétence | Où la retravailler |
|---|---|
| Écrire un modèle linéaire, l'estimer et démontrer ses propriétés | 1.1 |
| Interpréter les coefficients (indicatrices, logarithmes) | 1.1 |
| Tester, calculer intervalles de confiance et de prédiction | 1.2 |
| Diagnostiquer un modèle (résidus, levier, colinéarité) | 1.3 |
| Choisir un modèle sans tricher | 1.4 |
| Régulariser, résister aux aberrations, modéliser des groupes | 1.5, 1.6, 1.7 |
| Choisir loi et lien d'un GLM, estimer et vérifier | 2.1 à 2.4 |
| Modéliser des zéros en excès, assouplir un effet | 2.5, 2.6 |
| Réduire la dimension (ACP, analyse factorielle) | 3.1, 3.2 |
| Classer sans étiquettes et vérifier qu'il y a des groupes | 3.3 |
| Diagnostiquer la stationnarité, lire une ACF | 4.1 |
| Ajuster un SARIMA et évaluer des prévisions | 4.2, 4.3 |
| Traiter des durées censurées (Kaplan-Meier, Cox) | 5.1, 5.2, 5.3 |
| Ajuster des modèles de durée paramétriques | 5.4 |
| Raisonner à la Bayes, choisir un a priori | 6.1 |
| Simuler (Monte-Carlo, MCMC) et diagnostiquer | 6.2, 6.3, 6.4 |
| Formuler une question causale et choisir une méthode | 7.1 à 7.4 |
| Concevoir une expérience, analyser un plan | 8.1 à 8.4 |
| Mesurer l'autocorrélation spatiale, krigeage | 9.2, 9.3 |
| Mener une étude de modélisation de bout en bout | Projet du volume |

## Et maintenant ?

Vous savez maintenant **construire, vérifier et interpréter** des modèles statistiques. Le **volume III : Apprentissage automatique** reprend le même cycle (données → modèle → évaluation hors échantillon → décision) avec des modèles plus flexibles (arbres, forêts, boosting, réseaux), dont l'objectif premier est la **prédiction**. Tout ce que vous avez appris ici ne devient pas inutile : la validation croisée, la régularisation, la vérification de modèles, la différence entre prédire et expliquer en sont le fondement.

> ✅ **À retenir, tout simplement.** Un modèle est une carte : il simplifie pour servir. Votre métier, désormais, consiste à savoir **ce que la carte montre**, **ce qu'elle cache**, et **comment vérifier** que vous n'avez pas oublié le fleuve.
