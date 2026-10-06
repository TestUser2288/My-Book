# Chapitre 2 : Modélisation actuarielle

> « Vendre une promesse avant d'en connaître le coût : voilà le métier. »

Une mutuelle d'assurance vend, aujourd'hui, une garantie dont le coût ne sera connu que dans plusieurs mois, parfois dans plusieurs années. Elle doit pourtant fixer **le prix** de cette garantie (la tarification), puis **mettre de côté l'argent** que les sinistres déjà survenus coûteront encore (le provisionnement). Ces deux décisions reposent sur des modèles statistiques, et ce sont celles dont la banque, dans le chapitre précédent, n'a pas d'équivalent exact : l'assureur *inverse le cycle de production*. Il encaisse d'abord, il paie ensuite, et l'écart entre les deux est un **risque** qu'il lui revient de mesurer.

Ce chapitre est le cœur technique du volume pour qui travaille en assurance. Il reprend des outils que vous connaissez déjà (modèles linéaires généralisés du volume II, validation hors période du volume III) et leur donne leur vocabulaire de métier : fréquence, sévérité, prime pure, chargements, triangle de développement, provision. Il repose sur une idée directrice : **un modèle d'assurance n'est jamais jugé sur sa vraisemblance, mais sur ce qui se passe l'année suivante**. Les données étant simulées, nous aurons même le luxe, rare, de comparer nos estimations à la **vérité programmée**.

## Le chemin de ce chapitre

- **2.1 Modèles de fréquence et de sévérité** : on sépare le coût d'un contrat en un *nombre* de sinistres et un *montant* par sinistre ; on apprend à compter (Poisson, binomiale négative), à décrire des montants à queue lourde (Gamma, Pareto généralisée) et à reconstituer la charge annuelle d'un portefeuille (modèle collectif).
- **2.2 Tarification et construction du tarif** : de la prime pure au tarif commercial ; deux modèles (fréquence × sévérité) ou un seul (Tweedie) ; validation sur une année qu'on n'a pas utilisée ; ce que coûte un tarif trop grossier (antisélection).
- **2.3 Provisionnement des sinistres** : le triangle de développement, la méthode *chain ladder*, la queue, et comment juger une provision *a posteriori*.
- **➕ 2.4 GLM tarifaires et théorie de la crédibilité** : sous le capot du GLM (déviance, tests, splines, régularisation), crédibilité de Bühlmann–Straub, comparaison avec un boosting.
- **➕ 2.5 Chain ladder, Bornhuetter–Ferguson, Mack, bootstrap** : quatre façons d'estimer une provision *et son incertitude*, et ce qui les met en défaut.
- **➕ 2.6 Assurance santé** : coûts, sélection adverse, aléa moral, table de morbidité.

Les sections 2.4 à 2.6 sont **facultatives** : elles approfondissent sans conditionner la suite. Le chapitre 6 (réassurance) reprend la sévérité à queue lourde de la section 2.1 ; le chapitre 3 (mesures de risque) et le chapitre 4 (Solvabilité) reprennent les quantiles de la charge annuelle.

## Les données du chapitre

> 📦 **Données (simulées).** Quatre jeux, fabriqués par `build/donnees5.py` avec des graines fixes. **Rien n'est réel** : la mutuelle, ses assurés et leurs sinistres sont fictifs, et c'est ce qui permet de révéler, en fin d'étude, les paramètres programmés.
> - `polices_auto.csv` : {{n_pol|int}} lignes *police-année* (2022 à 2024), avec l'exposition (fraction d'année couverte), le conducteur (âge), le véhicule (âge, puissance), la zone (« Zone A » à « Zone F »), le bonus-malus, l'usage, le carburant et le nombre de sinistres.
> - `sinistres_auto.csv` : les {{n_sin|int}} sinistres correspondants, matériels (90 %) ou corporels (10 %), avec leur montant.
> - `triangle_rc.csv`, `triangle_dommages.csv`, `triangle_choc.csv` : trois triangles de paiements (dix années de survenance), avec leurs fichiers `*_verite.csv` qui contiennent les paiements **futurs** réels.
> - `sante_assures.csv` : {{n_sante|int}} lignes *assuré-année* avec les coûts par poste (section 2.6).

Nous suivrons une règle simple pour la tarification : **on estime sur 2022 et 2023, on juge sur 2024**. Les montants sont **revalorisés en euros de 2024** quand on compare des années entre elles (l'inflation des coûts est de l'ordre de 4 % par an).

```python hide
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET
from outils_ch02 import *
style.setup()


def NUM(cle, valeur):
    """Imprime un nombre cité dans la prose : le texte le relit dans cette sortie."""
    print("NUM", cle, valeur)


pol, sin = charger_polices()
INFL = 1.04
sin = sin.merge(pol[["id_police", "puissance", "zone", "classe_age"]], on="id_police")
sin["rev"] = sin["montant"] * INFL ** (2024 - sin["annee"])      # montants en euros de 2024
sante = pd.read_csv("donnees/sante_assures.csv")
NUM("n_pol", len(pol)); NUM("n_sin", len(sin)); NUM("n_sante", len(sante))
```

## Une règle de lecture pour tout le chapitre

Dans ce volume, **un chiffre de modèle n'est jamais donné seul** : on l'accompagne de son incertitude, ou d'une comparaison avec la vérité quand on l'a. C'est le fil rouge de la série depuis le volume III (« la rigueur d'évaluation »), et il est plus important encore ici : un tarif ou une provision engage de l'argent, et l'écart entre un chiffre *précis* et un chiffre *juste* se paie.
