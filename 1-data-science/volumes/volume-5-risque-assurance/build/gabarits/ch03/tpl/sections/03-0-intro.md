# Chapitre 3 : Mesures de risque et stress tests

> « Un chiffre de risque est une réponse à une question. Avant de le lire, il faut retrouver la question. »

Les deux premiers chapitres ont chiffré des risques *individuels* : la probabilité qu'un emprunteur ne rembourse pas, la charge de sinistres d'un contrat d'assurance. Mais ni la banque ni la mutuelle ne vivent contrat par contrat. Elles vivent **en portefeuille**, c'est-à-dire avec des milliers de risques qui se compensent un jour et s'additionnent le lendemain, et c'est la **perte du portefeuille entier** qui décide de la solvabilité. Ce chapitre apprend à résumer cette perte par quelques nombres, à les calculer de plusieurs façons, à les **mettre à l'épreuve** par des scénarios extrêmes, puis à vérifier qu'ils tiennent face à la réalité.

Le fil conducteur est une phrase : **un nombre de risque n'a de sens qu'avec sa définition, son horizon, son niveau de confiance… et son incertitude**. La *valeur à risque* (VaR) à 99 % sur un jour et la VaR à 99 % sur dix jours ne répondent pas à la même question ; la VaR et la perte moyenne au-delà de la VaR (l'*expected shortfall*) ne disent pas la même chose de la queue de la distribution ; un modèle calibré en période calme se trompe précisément quand la période cesse de l'être. Nous le verrons sur des données simulées dont nous connaissons la vérité : nous pourrons donc, ce que la vie réelle ne permet presque jamais, **juger chaque méthode par rapport à ce qui s'est vraiment passé**.

## Le chemin de ce chapitre

- **3.1 VaR et expected shortfall.** Définir une perte, un quantile, un horizon. Calculer la VaR par la loi normale (formule démontrée), par l'histoire, par simulation, par un modèle de volatilité qui change (EWMA, GARCH). Comprendre l'expected shortfall, démontrer pourquoi la VaR n'est pas une mesure *cohérente*, et mesurer l'incertitude d'un chiffre de queue.
- **3.2 Stress tests et scénarios.** Répondre à la question « et si ? » : sensibilités, scénarios historiques et hypothétiques, scénario *macroéconomique* relié aux défauts de crédit par un modèle statistique, choc de taux d'intérêt, stress *inversé*, et pourquoi les corrélations montent quand tout va mal.
- **➕ 3.3 Risques opérationnel, de marché et de liquidité.** L'approche par distribution des pertes (fréquence × sévérité) appliquée à des incidents opérationnels, les contributions au risque d'un portefeuille de marché, et un aperçu de la liquidité.
- **➕ 3.4 Backtesting et validation des modèles.** Les tests de Kupiec et de Christoffersen, le « feu tricolore », le contrôle de l'expected shortfall, et la démarche de validation indépendante d'un modèle, avec son risque propre : le **risque de modèle**.
- **Bilan du chapitre**, puis, dans le **cahier**, huit applications et douze exercices corrigés.

Ce chapitre s'appuie sur le volume II (régression logistique, section 2.2 ; modèles GARCH, section 4.4 ; valeurs extrêmes, section 6.5) et sur le volume III (validation, chapitre 1 ; métriques et calibration, chapitre 5). Il prépare le chapitre 4 : les cadres réglementaires de Bâle et de Solvabilité *imposent* des mesures de risque, et nous saurons ce qu'elles valent.

## Les données du chapitre

> 📦 **Données (simulées, graines fixes).** Quatre jeux, tous fabriqués par `build/donnees5.py`, qui connaît donc la vérité.
> - `rendements_marche.csv` : 4 000 jours ouvrés de rendements journaliers de cinq actifs (deux paniers d'actions, des obligations, de l'immobilier coté, des matières premières). La volatilité change au fil du temps (modèle GARCH) et le marché alterne entre un régime **calme** et un régime de **stress** (volatilité doublée, corrélations en hausse) ; `marche_verite.csv` donne le régime vrai de chaque jour.
> - `taux_defaut_macro.csv` : 80 trimestres de variables macroéconomiques (croissance, chômage, variation de l'immobilier) et le taux de défaut annualisé d'un portefeuille de crédit, avec une récession aux trimestres 48 à 54.
> - `courbe_taux.csv` : 120 mois d'une courbe de taux sur neuf maturités, avec un cycle de hausse des taux entre les mois 60 et 90.
> - `pertes_operationnelles.csv` : dix ans d'incidents opérationnels (fraudes, erreurs de traitement, pannes, pratiques commerciales) avec perte brute, récupération et perte nette.
>
> Le portefeuille d'exemple est celui d'un investisseur institutionnel fictif : **100 M€** répartis ainsi : 35 % d'actions A, 15 % d'actions B, 30 % d'obligations, 10 % d'immobilier et 10 % de matières premières. Toutes les pertes sont exprimées en **millions d'euros**, comptées **positivement** (une perte de 2 signifie que le portefeuille a perdu 2 M€).

```python hide
import sys
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib.pyplot as plt
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE2, MUET
import outils_ch03 as O
style.setup()
r, regime = O.charger_marche()
rg = regime.values
L = O.pertes_portefeuille(r)
print("jours :", len(L), "| part de jours de stress :", round((rg == "stress").mean(), 3))
O.num("n_jours", len(L), "d")
O.num("part_stress", 100 * (rg == "stress").mean(), ".1f")
O.num("sd_calme", L[rg == "calme"].std(), ".2f")
O.num("sd_stress", L[rg == "stress"].std(), ".2f")
O.num("ratio_sd", L[rg == "stress"].std() / L[rg == "calme"].std(), ".1f")
```
<!--sortie-->

Un premier regard suffit à comprendre l'enjeu : l'écart-type de la perte journalière du portefeuille est de {{sd_calme}} M€ en régime calme et de {{sd_stress}} M€ en régime de stress, soit {{ratio_sd}} fois plus, alors que les jours de stress ne représentent que {{part_stress}} % des {{n_jours:,d}} jours observés. Presque toute la difficulté du chapitre tient dans cette asymétrie : **la queue de la distribution est fabriquée par une minorité de jours qui ne ressemblent pas aux autres**.
