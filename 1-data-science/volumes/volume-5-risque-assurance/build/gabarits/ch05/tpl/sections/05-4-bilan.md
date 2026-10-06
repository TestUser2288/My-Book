## Bilan du chapitre 5

Vous savez maintenant :

- **passer des décès aux taux et aux probabilités** : $m_x=D_x/E_x$ (estimateur de Poisson, précision relative $1/\sqrt{D}$), $q_x=1-e^{-m_x}$, et construire une **table** ($\ell_x$, $d_x$, $L_x$, $e_x$) ; distinguer **table de période** et **table de génération**, et savoir pourquoi la première sous-estime la durée de vie quand la mortalité baisse ;
- **lisser et prolonger** une table par la loi de **Gompertz–Makeham** (doublement de la mortalité tous les $\ln 2/c$ ans), en sachant que l'extrapolation est une hypothèse ;
- **mesurer la sélection** par un **rapport réel/attendu** avec son intervalle exact de Poisson ({{ae}} avec [{{ae_bas}} ; {{ae_haut}}] sur ce portefeuille, pour une valeur programmée de 0,75), et savoir qu'un découpage trop fin ne produit que du bruit ;
- **actualiser** des flux incertains : capital décès $A_x$, rente viagère $\ddot a_x$, relation $A_x=1-d\,\ddot a_x$, **prime pure** par le principe d'équivalence, **provision mathématique** prospective et rétrospective, récurrence de Thiele ;
- **mesurer la sensibilité** d'un contrat à la table et au taux technique, et comprendre que **la baisse de la mortalité aide les contrats de décès et pénalise les rentes** ;
- **ajuster un modèle de Lee–Carter** ($\ln m_{x,t}=a_x+b_xk_t$) par SVD, recaler $k_t$, **projeter** $k_t$ par une marche aléatoire avec dérive, le **valider hors période**, et reconnaître ce qui gonfle l'écart-type estimé (chocs transitoires, erreur d'estimation) ;
- **chiffrer un risque de longévité** : coût d'une rente selon la table de période ou de génération, quantile à 99,5 %, et différence entre **risque individuel** (qui se mutualise) et **risque de tendance** (qui ne se mutualise pas).

Le tableau suivant résume **ce que nous avons mesuré** sur les femmes de la population simulée (données simulées, taux technique de 2 % pris pour l'illustration) :

| Question | Résultat |
|---|---|
| Espérance de vie à la naissance / à 65 ans, table de 2019 | {{e0F}} ans / {{e65F}} ans |
| Années vécues de 60 à 100 ans : période 1980, cohorte 1920, période 2019 | {{e_p80:.2f}} / {{e_coh:.2f}} / {{e_p19:.2f}} |
| Mortalité des assurés par rapport à la population (A/E) | {{ae}} |
| Prime annuelle pour 1 000 € : temporaire de 20 ans à 40 ans | {{p40_mille:.2f}} € |
| Coût d'une rente de 1 € par an à 65 ans : période, génération projetée | {{a_per:.2f}} €, {{a_gen:.2f}} € |
| Rente à 65 ans : effet d'une mortalité de 20 % plus basse | + {{choc20}} % |
| Dérive de $k_t$ estimée / vraie | {{delta_hat}} / −1,2 |
| Espérance de vie à 65 ans en 2049 (médiane projetée) | {{e65_2049:.2f}} ans |

Le fil conducteur du chapitre tient en une phrase : **une table de mortalité est une hypothèse sur l'avenir déguisée en tableau de chiffres**. On peut estimer le niveau d'une mortalité avec une précision remarquable (une population de centaines de milliers de personnes), mais le prix d'un contrat à long terme dépend de **la tendance**, qu'aucune observation ne garantit, et le risque qui en résulte ne se diversifie pas. Le chapitre 6 présente le transfert d'un tel risque (la réassurance) et le chapitre 7 la manière dont un assureur ajuste ses placements à ses engagements.

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.8 (table de période, lissage et graduation, rapport réel/attendu, valeurs actuarielles, provisions, Lee–Carter, risque de longévité, validation hors période) et exercices 5.1 à 5.12.
