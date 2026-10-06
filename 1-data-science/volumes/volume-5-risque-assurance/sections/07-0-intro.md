# Chapitre 7 : ➕ Gestion actif-passif et théorie du portefeuille

> « Une assurance vendue aujourd'hui est une promesse payable dans vingt ans. Le risque n'est pas dans la promesse, ni dans les placements : il est dans l'écart entre les deux. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est facultatif : les chapitres 1 à 4 se lisent sans lui. Il s'adresse à celles et ceux qui devront **décider comment placer les primes encaissées** (en assurance) ou **comment financer des prêts avec des dépôts** (en banque). Il suppose les notions de rendement, de variance et de covariance (volume I) et reprend les mesures de risque du chapitre 3 (VaR et expected shortfall, section 3.1).

Les chapitres précédents ont chiffré des risques **un par un** : la probabilité de défaut d'un emprunteur (chapitre 1), le coût des sinistres d'un portefeuille (chapitre 2), la perte maximale d'un jeu de positions (chapitre 3), le capital que le régulateur exige (chapitre 4), la mortalité d'une génération (chapitre 5), le coût d'une protection (chapitre 6). Reste la question que se pose la direction financière une fois tous ces chiffres posés : **avec quoi la mutuelle (ou la banque) paiera-t-elle ce qu'elle a promis, et que se passe-t-il si les marchés bougent ?**

Cette question a deux visages. Le premier est celui de l'**actif-passif** (*asset-liability management*, ALM) : les promesses faites aux assurés ou aux déposants forment un **passif**, c'est-à-dire un échéancier de paiements futurs ; les placements forment l'**actif**. Quand les taux d'intérêt changent, les deux ne se déplacent pas de la même quantité, et c'est leur **différence**, le surplus, qui absorbe le choc. Le second visage est celui de la **théorie du portefeuille** : étant donné des actifs aux rendements incertains et corrélés, comment répartir un capital entre eux pour obtenir le meilleur compromis entre rendement attendu et risque ? Le chapitre commence par le premier, puis passe au second, puis les réunit.

## Le chemin de ce chapitre

- **7.1 Gestion actif-passif** : le bilan comme deux échéanciers, la valeur actuelle, la **duration** et la **convexité** (avec leur démonstration), la construction du **passif d'un portefeuille d'assurance vie** à partir de tables de mortalité, l'**écart de duration**, l'**immunisation** et ses conditions, les chocs de courbe qui ne sont pas parallèles, l'échéancier de refixation d'une banque, et ce que l'histoire (simulée) des taux aurait fait au surplus.
- **7.2 Théorie du portefeuille** : rendement et risque d'un portefeuille (formules matricielles), la **frontière efficiente** à deux puis à cinq actifs, le portefeuille de variance minimale, le ratio de Sharpe, les **contributions au risque**, l'idée du CAPM, la fragilité des estimations (rendements, covariances, rétrécissement) et ce que devient la diversification **en période de stress**.
- **7.3 De la frontière efficiente à l'actif-passif** : le **surplus** comme objet à optimiser, l'allocation sous contrainte de duration, la **VaR et l'expected shortfall du surplus**, une simulation sur dix ans du taux de couverture, et les limites de tout ce qui précède.
- **Bilan du chapitre.**

> 📒 **Pour s'entraîner.** Cahier, chapitre 7 : huit applications (prix et duration d'une obligation, passif d'un portefeuille vie, appariement, chocs de courbe, frontière efficiente, contributions au risque, estimation et rétrécissement, surplus et simulation) et douze exercices corrigés.

## Les données du chapitre

> 📦 **Données (toutes simulées).** `courbe_taux.csv` : 120 mois de courbes des taux zéro-coupon à neuf maturités (de 3 mois à 30 ans). `rendements_marche.csv` : 4 000 jours de rendements de cinq classes d'actifs (deux actions, obligations, immobilier, matières premières) et `marche_verite.csv`, le régime vrai (calme ou stress) de chaque jour, que l'on **ne connaît pas** dans la réalité. `portefeuille_vie.csv` : 20 000 contrats d'assurance vie observés de 2015 à 2019, et `mortalite_population.csv`, la mortalité de la population par sexe et par âge, qui sert à bâtir la table de mortalité.

Trois précautions, à garder à l'esprit tout au long du chapitre.

> ⚠️ **Honnêteté.** (1) Les données sont **simulées**, et les deux jeux de marché (`courbe_taux.csv` et `rendements_marche.csv`) ont été simulés **indépendamment** : les taux et les actions n'y sont donc pas corrélés, alors qu'ils le sont dans la réalité (et que cette corrélation compte beaucoup pour un assureur). (2) Le « bilan » construit dans ce chapitre est un **jouet** : passif à prestations fixes, sans rachats, sans amélioration future de la mortalité, sans frais, sans écart de crédit. Il sert à comprendre des mécanismes, pas à calibrer un portefeuille. (3) Ce chapitre n'est **pas un conseil en placement** : les allocations obtenues dépendent d'un historique simulé et d'hypothèses qui sont écrites à chaque fois.

Le bloc caché ci-dessous charge les outils du chapitre (un module écrit à la main, `build/outils_ch07.py`) et construit le **bilan jouet** de la mutuelle : le passif est l'échéancier attendu des prestations de décès des contrats en vigueur au 1er janvier 2020, l'actif vaut 10 % de plus que la valeur actuelle de ce passif.

```python hide
import os, sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

sys.path.insert(0, "build")
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2
style.setup()
import outils_ch07 as O

def NUM(k, v):
    print("NUM", k, v)

b = O.Bilan(surplus=0.10)
NUM("surplus_init_pct", 100 * (b.A0 / b.L0 - 1))
NUM("nb_contrats", b.nb_contrats)
NUM("L0_M", b.L0 / 1e6)
NUM("A0_M", b.A0 / 1e6)
```
<!--sortie-->
```text
NUM surplus_init_pct 10.000000000000009
NUM nb_contrats 16908
NUM L0_M 460.2259525825695
NUM A0_M 506.24854784082646
```
