# Chapitre 5 : ➕ Assurance vie

> « Assurer une vie, c'est mettre un prix sur une date que personne ne connaît, en comptant sur ce que l'on sait de toutes les autres. »

> 🧭 **Chapitre complémentaire.** Ce chapitre est facultatif : le reste du volume ne le suppose pas. Il montre comment les outils des chapitres précédents (modèle de comptage de Poisson, vraisemblance, validation hors période, quantiles d'une distribution simulée) servent un autre métier de l'actuariat : celui où l'on promet de payer **dans vingt, quarante ou soixante ans**. Il se lit mieux après le chapitre 2 (fréquence, sévérité, tarification) et le chapitre 3 (mesures de risque).

En assurance dommages (chapitre 2), un contrat dure un an et l'on peut se corriger chaque année : si la sinistralité monte, on augmente le tarif à l'échéance. En assurance **vie**, la promesse est de long terme : une rente versée jusqu'au décès, un capital garanti à un âge lointain, une prime fixée **aujourd'hui** pour des décennies. Le prix d'un tel contrat repose donc sur trois ingrédients : **une table de mortalité** (quelle est la probabilité de décéder à chaque âge ?), **un taux d'actualisation** (que vaut aujourd'hui un euro payé dans trente ans ?) et **une projection** (la mortalité de demain ressemblera-t-elle à celle d'aujourd'hui ?). Ce chapitre suit exactement cet ordre.

## Le chemin de ce chapitre

- **5.1 Tables de mortalité.** On passe des décès et des expositions observés aux taux, puis aux probabilités de décès, puis à la table ($\ell_x$, $d_x$, $e_x$). On compare table de période et table de génération, on lisse par la loi de Gompertz–Makeham, et l'on mesure par un **rapport réel/attendu** si les assurés meurent moins que la population.
- **5.2 Mathématiques actuarielles de la vie.** On actualise : capital décès $A_x$, rente viagère $\ddot a_x$, la relation $A_x = 1 - d\,\ddot a_x$, les primes nivelées par le principe d'équivalence, les provisions mathématiques, et la sensibilité au taux technique et à la table.
- **5.3 Le modèle de Lee–Carter.** On modélise la **tendance** : $\ln m_{x,t} = a_x + b_x k_t$. On l'ajuste par décomposition en valeurs singulières, on projette l'indice $k_t$, on **compare à la vérité programmée**, et l'on quantifie le **risque de longévité** d'un portefeuille de rentes.

Le fil conducteur est celui du volume : **chiffrer un risque, puis prouver que le chiffre tient**. Ici, la réponse a une particularité heureuse : les données sont simulées à partir d'un modèle connu, de sorte que l'on peut comparer chaque estimation à la vérité, ce que la réalité ne permet jamais.

## Les données du chapitre

> 📦 **Données.** Deux jeux, tous deux **simulés** (graines fixes ; générateur `build/donnees5.py`).
> - `mortalite_population.csv` : les décès et les expositions au risque d'une **population fictive**, par sexe (F, M), âge (0 à 99 ans) et année (1980 à 2019), soit 8 000 lignes. La mortalité y suit **exactement** un modèle de Lee–Carter (section 5.3), avec une vérité connue : `mortalite_verite.csv` ($a_x$, $b_x$) et `mortalite_kt_vrai.csv` ($k_t$).
> - `portefeuille_vie.csv` : 20 000 contrats d'une mutuelle fictive (temporaire 10 ou 20 ans, vie entière), observés de 2015 à 2019, avec pour chacun l'âge à l'émission, le capital, l'exposition observée et l'indicateur de décès. La mortalité des assurés a été programmée à **75 % de celle de la population**.
>
> Aucune donnée n'est réelle : les ordres de grandeur sont plausibles, mais l'espérance de vie à la naissance (environ 74 ans pour les femmes de cette population fictive) n'est pas celle d'un pays donné.

```python hide
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import style
from style import BLEU, ORANGE, AQUA, VIOLET, ROUGE, ENCRE, ENCRE2, MUET
from outils_ch05 import *
style.setup()


def NUM(cle, valeur):
    """imprime un nombre cité dans la prose (relu à la main lors de la vérification)"""
    print("NUM", cle, valeur)


pop = charger()
M = {s: surface(pop, s) for s in "FM"}
E = {s: surface(pop, s, "exposition") for s in "FM"}
D = {s: surface(pop, s, "deces") for s in "FM"}
AX, BX, KT = verite()
pv = pd.read_csv(os.path.join(DONNEES, "portefeuille_vie.csv"))
NUM("n_pop", len(pop)); NUM("deces_pop", int(pop["deces"].sum()))
NUM("n_contrats", len(pv)); NUM("deces_pv", int(pv["deces"].sum())); NUM("expo_pv", round(pv["exposition_2015_2019"].sum()))
```
<!--sortie-->
```text
NUM n_pop 8000
NUM deces_pop 6596675
NUM n_contrats 20000
NUM deces_pv 832
NUM expo_pv 84909
```

Un coup d'œil aux premières lignes du jeu de population suffit à fixer le vocabulaire : une ligne par année, âge et sexe, avec l'**exposition** (le nombre d'années-personnes vécues dans la cellule) et les **décès** observés.

```python
print(pop[(pop["annee"] == 2019) & (pop["sexe"] == "F")].iloc[[0, 30, 60, 90]].to_string(index=False))
```
<!--sortie-->
```text
 annee  age sexe  exposition  deces        m
  2019    0    F     98750.0    332 0.003362
  2019   30    F     51759.3     37 0.000715
  2019   60    F     25642.5    340 0.013259
  2019   90    F     14196.2   4154 0.292614
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 5 : applications 5.1 à 5.8 (tables de période, lissage et graduation, rapport réel/attendu, valeurs actuarielles, provisions, Lee–Carter, risque de longévité, validation hors période) et exercices 5.1 à 5.12.
