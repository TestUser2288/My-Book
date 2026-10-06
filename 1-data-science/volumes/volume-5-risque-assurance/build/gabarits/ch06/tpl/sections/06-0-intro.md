# Chapitre 6 : ➕ Bases de la réassurance et de sa tarification

> « Réassurer, c'est acheter de la tranquillité. Son prix se calcule, et surtout il se discute. »

> 🧭 **Chapitre complémentaire.** Il peut être lu sans le reste du volume, mais il suppose les notions de sévérité à queue lourde (volume II, section 6.5), de VaR et d'*expected shortfall* (section 3.1) et de capital réglementaire (section 4.2). Le chapitre 7 en est indépendant.

Une mutuelle d'assurance a un métier simple à énoncer : mettre en commun des risques pour que chacun supporte une part prévisible d'un aléa que, seul, il ne pourrait pas porter. Mais la mutuelle est elle-même exposée à un aléa qu'elle ne peut pas diluer indéfiniment : **quelques sinistres très gros** (un incendie qui détruit un entrepôt, une tempête qui touche tout un territoire le même jour) peuvent à eux seuls faire basculer un exercice, voire menacer sa solvabilité. La **réassurance** est l'assurance de l'assureur : la mutuelle (la **cédante**) transfère à un **réassureur** une partie de ses risques, contre une prime.

Ce chapitre répond à trois questions, dans l'ordre où une cédante se les pose.

## Le chemin de ce chapitre

| Section | Question | Ce que vous saurez faire |
|---|---|---|
| **6.1 Principes et formes** | Comment un traité partage-t-il les sinistres entre cédante et réassureur ? | Distinguer **proportionnel** et **non proportionnel**, calculer à la main ce que cède chaque forme, lire une clause (priorité, portée, réintégration). |
| **6.2 Tarifer un traité** | Combien vaut une tranche de sinistres gros ? | Estimer une prime pure par le *burning cost*, par une loi de queue (GPD) et par l'exposition ; **chiffrer l'incertitude** ; passer de la prime pure à la prime technique. |
| **6.3 Choisir une couverture** | Que gagne-t-on à réassurer, et à quel prix ? | Simuler la charge annuelle, comparer des programmes par le **coût d'un euro de capital économisé**, regarder le risque de contrepartie et l'épuisement des garanties. |

Le fil conducteur est celui du volume : **chiffrer un risque, puis prouver que le chiffre tient**. Ici, la preuve est difficile, parce que le risque réassuré est précisément celui dont on a **le moins d'observations** : on parle de sinistres qui arrivent une fois en cinq ans, une fois en vingt ans. Vous verrez qu'une estimation correcte peut se tromper de 10 %, de 30 %, ou de beaucoup plus sur une tranche haute, **sans qu'aucun calcul n'ait été faux**.

## Les données du chapitre

> 📦 **Données.** Deux fichiers **simulés**, sans lien avec une entreprise réelle.
> - `sinistres_gros.csv` : {{n_sin|int}} sinistres « incendie » de la mutuelle sur {{n_ans|int}} ans (2010 à 2024), avec l'année de survenance et le montant en €. Le nombre de sinistres croît d'environ 3 % par an, parce que le portefeuille grandit.
> - `cat_annuel.csv` : la perte annuelle due à des **événements catastrophiques** sur 40 ans (1985 à 2024), en €, avec beaucoup d'années à zéro.
>
> Comme toujours, les données sont fabriquées par un programme : nous **connaissons la vérité** (la loi des sinistres, la loi des catastrophes, le taux de croissance), et nous la révélerons au fil des études pour juger les estimations. En pratique, elle n'est jamais connue.

```python hide
import os, sys
import numpy as np, pandas as pd
from scipy import stats
sys.path.insert(0, "build")
import outils_ch06 as O

def NUM(cle, valeur):
    print(f"NUM {cle} {valeur}")

sg, cat = O.charger()
x = sg["montant"].values
c = cat["perte_cat"].values
NUM("n_sin", len(sg)); NUM("n_ans", sg["annee_survenance"].nunique())
NUM("med", np.median(x)); NUM("moy", x.mean()); NUM("ecart", x.std())
NUM("q90", np.quantile(x, 0.90)); NUM("q99", np.quantile(x, 0.99)); NUM("vmax", x.max())
NUM("n500", (x > 5e5).sum()); NUM("n1m", (x > 1e6).sum()); NUM("n2m", (x > 2e6).sum())
NUM("part500", (x > 5e5).mean()); NUM("cat_ev", (c > 0).sum()); NUM("cat_max", c.max()); NUM("cat_moy", c.mean())
NUM("part_gros", x[x > 5e5].sum() / x.sum())
NUM("lam25", O.LAMBDA_2025)
```

Les sinistres se résument en quelques lignes :

```python
sg, cat = O.charger()
print(sg["montant"].describe().round(0))
```

Le sinistre médian vaut {{med|int}} €, le sinistre moyen {{moy|int}} € : **la moyenne vaut près de quatre fois la médiane**, signe d'une distribution très asymétrique. Les {{n500|int}} sinistres de plus de 500 000 € ({{part500|pc1}} % des sinistres) pèsent {{part_gros|pc0}} % du montant total ; le plus gros atteint {{vmax|int}} €. Les catastrophes sont encore plus rares : {{cat_ev|int}} années sur 40 ont connu un événement, et la pire a coûté {{cat_max|int}} €. Ce sont ces queues que la réassurance vient couvrir, et ce sont elles qui rendent leur prix incertain.

> ⚠️ **Deux conventions de lecture.** Les tranches s'écrivent « **portée xs priorité** » : « 1 M€ xs 1 M€ » désigne la tranche qui paie la part d'un sinistre comprise **entre 1 M€ et 2 M€**. Et tous les montants « au niveau 2025 » désignent l'**exposition attendue de l'année 2025** (environ {{lam25|0}} sinistres par an, contre 160 en 2010).
