# Points clés

> « Un risque chiffré n'est utile que si l'on sait de combien le chiffre peut se tromper. »

Ce court chapitre fixe l'essentiel du volume, chapitre par chapitre, puis les idées qui les relient. Le **projet du volume** (le tarif d'une assurance automobile, validé hors période, avec ses notes réglementaires) et une **auto-évaluation** de quarante questions se trouvent dans le cahier d'exercices.

> 📒 **Pour s'entraîner.** Cahier, projet du volume et auto-évaluation : neuf étapes, du cahier des charges au rapport, une variante de score de crédit, puis quarante questions avec corrigés.

## Les points clés, chapitre par chapitre

| Chapitre | Ce que vous devez emporter |
|---|---|
| **1. Risque de crédit et scoring** | Un score est une **cote écrite en points** : classes, poids de l'évidence, régression logistique, échelle (score de base, PDO). On le juge par le **classement** (AUC, **Gini = 2·AUC − 1**, KS), la **calibration** (la probabilité annoncée est-elle la bonne ?) et la **stabilité** (PSI), **hors période**. Les dossiers refusés biaisent la grille (4,4 % annoncés contre 6,0 % réels). ➕ WOE/IV ; **perte attendue = PD × LGD × EAD**, trois étapes IFRS 9, scénarios ; matrices de migration déformées par la conjoncture. |
| **2. Modélisation actuarielle** | Le coût d'un contrat est une **fréquence** (Poisson sur l'**exposition**, sur-dispersion) et une **sévérité** (Gamma, queue de Pareto généralisée) ; **prime pure = fréquence × sévérité**, puis chargements. Un tarif se **valide hors période** (Lorenz, Gini, calibration) et se lit avec le **bruit** : la queue est volatile. Provisionnement : triangle, **chain ladder**, queue, jugement a posteriori. ➕ GLM, crédibilité ; BF, Mack, bootstrap ; santé (sélection adverse, aléa moral). |
| **3. Mesures de risque et stress tests** | La **VaR** est un quantile, l'**expected shortfall** une moyenne de queue : la VaR n'est pas sous-additive, l'ES l'est. La loi normale **sous-estime** la queue, la règle de la racine suppose des pertes indépendantes. Un **stress test** relie un scénario à des pertes ; le stress **inversé** part de la perte inacceptable ; en crise, les **corrélations montent**. ➕ Un quantile à 99,9 % sur dix ans est **instable** ; backtests (Kupiec, Christoffersen, feu tricolore) de **faible puissance** ; la validation et le **risque de modèle**. |
| **4. Cadre réglementaire** | Le capital couvre la **perte inattendue**, la perte attendue se provisionne. **Bâle** : trois piliers, ratios, formule **IRB** (démontrée à partir d'un facteur systématique). **Solvabilité** : meilleure estimation, marge de risque, **SCR agrégé par corrélations** (exact pour des pertes normales seulement). **Takaful** : deux fonds, prêt sans intérêt, supervision charia. ➕ IFRS 17 et plancher de Bâle III ; excédent (wakala, moudaraba, hybride) ; **LAB** : règles à fenêtre de temps, graphes, anomalies, apprentissage supervisé. Les textes se **datent** et se vérifient. |
| **➕ 5. Assurance vie** | Taux de mortalité $m_x=D_x/E_x$, table ($\ell_x$, $d_x$, $e_x$), période ou génération, **Gompertz–Makeham**, rapport **réel/attendu** avec son intervalle. Valeurs actuelles actuarielles : $A_x=1-d\,\ddot a_x$, primes d'équivalence, provisions. **Lee–Carter** : $\ln m_{x,t}=a_x+b_xk_t$, projection de $k_t$ ; la baisse de mortalité **aide** les décès et **pénalise** les rentes ; risque individuel (mutualisable) et de tendance (non). |
| **➕ 6. Réassurance** | On réassure pour **stabiliser**, gagner de la **capacité** et économiser du **capital**, pas pour réduire le coût moyen. **Proportionnel** (quote-part) ou **non proportionnel** (excédent de sinistre). Tarifer une tranche : *burning cost* (ajusté de l'exposition et de l'inflation), **loi de queue**, tarification par l'exposition, avec une incertitude **élevée** sur les tranches hautes. |
| **➕ 7. Actif-passif et portefeuille** | Un bilan est deux échéanciers : **duration**, **convexité**, immunisation $D_A\,A=D_L\,L$ (en euros, pas en durations). **Markowitz** : frontière efficiente, contributions au risque, estimation fragile (rétrécissement), diversification qui **s'érode en stress**. Optimiser le **surplus** plutôt que l'actif ; VaR du surplus, simulation sur dix ans. |
| **Projet (cahier)** | Auditer et découper hors période → fréquence (GLM) → sévérité (écrêtée, mutualisée si le bruit l'emporte) → prime pure validée → tarif → scénarios, capital et réassurance → notes réglementaires → **rapport go / no-go** (critères fixés avant les résultats). |

## Six idées qui traversent tout le volume

> 💡 **Les six idées.**
> 1. **Un chiffre de risque est une convention.** VaR à 99 %, SCR à 99,5 %, formule IRB à 99,9 % : chacun se lit avec son niveau, son horizon et ses hypothèses.
> 2. **L'espérance se facture, la queue se capitalise.** La perte attendue entre dans le prix ou la provision ; la perte inattendue exige du capital, de la réassurance ou des limites.
> 3. **On valide hors période, et on dit l'incertitude.** Un écart entre prévu et réel est d'abord du bruit : on le simule avant de conclure (déciles, quantiles, intervalles).
> 4. **Les queues se trompent le plus, là où ça coûte le plus.** Normalité, quantiles extrêmes, corrélations calmes, tranches hautes : le modèle est moins fiable justement où l'enjeu est le plus grand.
> 5. **Les facteurs communs ne se diversifient pas.** Le hasard individuel s'éteint dans un grand portefeuille ; la conjoncture, l'inflation, la longévité, les corrélations de crise subsistent.
> 6. **Le modèle est une décision, donc un dossier.** Données, hypothèses, validation indépendante, limites, critères de décision écrits à l'avance, textes datés : sans cela, le meilleur modèle n'est pas défendable.

## Et maintenant ?

Vous savez maintenant **chiffrer un risque de crédit, de sinistre, de marché ou de longévité, et défendre ce chiffre** : mesure, validation, scénarios, capital, réassurance. Le **volume VI** (travaux appliqués et portfolio) demande de présenter des travaux réels ; en attendant, le meilleur entraînement est de reprendre **un portefeuille que vous connaissez** et de dérouler la démarche du projet : audit, modèle, validation hors période, scénarios, rapport.

> ✅ **À retenir, tout simplement.** Un modèle de risque ne vaut pas par son ajustement, mais par la **qualité de la décision qu'il éclaire** : un prix, une provision, un capital. Chiffrez, validez, doutez des queues, et écrivez ce que le chiffre ne sait pas.
