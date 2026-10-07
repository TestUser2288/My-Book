# Points clés

> « Une analyse n'est pas finie quand on a un résultat, mais quand on sait ce qu'il permet de conclure. »

Ce court chapitre fixe l'essentiel du volume, chapitre par chapitre, puis les idées qui les relient. Le **projet du volume** (répondre de bout en bout à la question « les promotions nous font-elles gagner de l'argent ? ») et une **auto-évaluation** de quarante questions se trouvent dans le cahier d'exercices.

> 📒 **Pour s'entraîner.** Cahier, projet du volume et auto-évaluation : huit étapes, de la reformulation de la question à la recommandation chiffrée, une variante sur un test d'e-mail, puis quarante questions avec corrigés.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. Exploration** | Regarder avant de modéliser : chaque variable seule (distribution, asymétrie : **médiane** plutôt que moyenne), puis par deux et par trois (nuages, groupes, tableaux croisés). Le **paradoxe de Simpson** existe dans de vraies données : on compare à période égale. Une **anomalie** n'est pas une **erreur** ni un **événement** ; une règle globale prend la saison pour une anomalie, une **référence locale** non. ➕ Une liste de contrôle réutilisable. |
| **2. Tests, A/B, corrélation** | La **p-valeur** n'est ni la probabilité que l'hypothèse soit vraie ni la taille de l'effet ; on préfère l'**intervalle de confiance**. Un test A/B se conçoit **avant** : répartition aléatoire, métrique, durée ; on vérifie le **ratio d'échantillon** d'abord, on se méfie des sous-groupes, des comparaisons multiples et de l'arrêt anticipé (27 % de faux positifs si l'on regarde chaque jour). Une corrélation n'est pas une cause : la saison explique l'essentiel de celle entre publicité et commandes. ➕ **Puissance** : un effet de 0,4 point exige des dizaines de milliers de personnes. |
| **3. Régression** | « Toutes choses égales par ailleurs » : la régression multiple **sépare** les effets que la comparaison brute confond ; le logarithme donne des effets en **pourcentage**. On diagnostique (résidus, autocorrélation, colinéarité) et on distingue **expliquer** de **prédire**. Un coefficient se traduit pour un non-spécialiste en une phrase avec son intervalle, jamais en « cause ». ➕ Régression logistique : **rapports de cotes**, seuil de décision selon les coûts. |
| **4. Segmentation et cohortes** | Un segment sert si l'on agit **différemment** sur lui ; les règles métier battent souvent les k-moyennes, qui demandent des variables standardisées et se valident (stabilité, comportement). Une **cohorte** se lit à **âge égal** ; l'observation est **tronquée à droite** et les petits effectifs trompent. ➕ RFM, valeur vie client (une fourchette, pas un chiffre), churn, entonnoirs. |
| **5. Séries temporelles** | Tendance, **saison**, résidu ; on compare au **même mois de l'an dernier** ; les indices saisonniers se calculent à la main. Une prévision se juge **hors échantillon** contre la **référence naïve saisonnière**, avec un intervalle, et il existe un plancher de hasard qu'aucun modèle ne franchit. ➕ Régression à indicatrices, ARIMA saisonnier, scénarios, stock et personnel. |
| **6. KPI** | Un bon KPI éclaire **une décision**, a une **définition écrite** et se calcule **une seule fois**. L'**arbre d'indicateurs** (sessions × conversion × panier) localise un écart. Une cible suppose une référence ; **bruit ou signal ?** se juge par la variabilité (cartes de contrôle). Un KPI devenu cible se déforme (**loi de Goodhart**). |
| **➕ 7. Écarts et causes** | Budget contre réalisé : décomposer en **volume, prix, mix** (les effets somment à l'écart) ; remonter aux causes par **hypothèses testables**, en écrivant « cause probable » quand on n'a pas démontré. |
| **➕ 8. Pareto, ABC, benchmarking** | La règle des 80/20 est un ordre de grandeur (ici 51 %) ; l'ABC aide à adapter la gestion ; un écart avec le secteur est d'abord une **question de définition**. |
| **➕ 9. Analyse financière** | Compte de résultat et bilan (cohérents avec la base), ratios, **seuil de rentabilité** : chaque euro de chiffre d'affaires en plus ne rapporte qu'une fraction de marge d'exploitation. |
| **➕ 10. Marketing et web** | Conversion par **source** (le mix change la conversion globale), **CAC**, **ROAS** et marge : un ROAS inférieur au seuil de bascule perd de l'argent ; un outil d'analyse web ne voit qu'une partie des commandes (consentement). |
| **➕ 11. Opérations** | Délais et retards par **centile** et par transporteur, stock de sécurité et point de commande, **fiabilité** des fournisseurs avec intervalles. |
| **➕ 12. RH** | Turnover et absentéisme avec intervalles larges, **écart salarial brut et ajusté** avec précaution, prédire les départs et **ne pas surveiller** les personnes. |
| **➕ 13. Sensibilité et scénarios** | Un modèle simple calibré, une **tornade**, un **Monte-Carlo** (médiane, intervalle, probabilité de perte), des **scénarios** et un **seuil de bascule** : on compare des options sous incertitude. |
| **Projet (cahier)** | Reformuler (« gagner de l'argent » n'est pas « vendre plus ») → explorer → régression avec contrôles (+19 % de commandes) → contrefactuel de **marge** (perte) → incertitude → **seuil de bascule** (+36 % nécessaires) → plan de mesure → recommandation et limites. |

## Six idées qui traversent tout le volume

> 💡 **Les six idées.**
> 1. **La question avant la méthode.** « Gagner de l'argent » n'est pas « vendre plus » : on reformule en une question testable avant tout calcul.
> 2. **À situation égale.** Saison, jour, tendance, canal : presque toutes les erreurs viennent de comparer des choses qui ne sont pas comparables.
> 3. **Un chiffre sans intervalle est un chiffre sans humilité.** Une estimation s'écrit avec son incertitude ; un test non significatif ne prouve pas l'absence d'effet.
> 4. **Le contrefactuel ne s'observe pas.** Quand on ne peut pas expérimenter, on l'estime et on le dit ; quand on peut, on expérimente.
> 5. **Un indicateur se définit, se calcule une fois et se lit avec son bruit.** Sans définition, deux personnes donnent deux chiffres ; sans bruit, on réagit à du hasard.
> 6. **Décider, c'est aussi connaître le seuil.** Le seuil de bascule, le scénario pessimiste et la probabilité de perte servent mieux la décision qu'une moyenne.

## Et maintenant ?

Vous savez maintenant **explorer, tester, modéliser, segmenter, prévoir, mesurer et simuler**, et surtout dire **ce que l'on peut conclure**. Le **volume IV** est consacré à la **visualisation et à la communication** : choisir un graphique, construire un tableau de bord, raconter une analyse et la présenter. Pour vous entraîner d'ici là, reprenez le projet avec les soldes d'été seules, ou avec le Vendredi noir.

> ✅ **À retenir, tout simplement.** Un bon analyste ne livre pas un résultat : il livre une **réponse conditionnelle** (« voici ce que montrent les données, voici l'incertitude, voici ce qu'il faudrait pour trancher »).
