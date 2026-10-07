# Chapitre 13 : ➕ Analyse de sensibilité, simulations « et si » et scénarios

> « Toute prévision se trompe ; la seule question est de combien, et dans quel sens. »

> 🧭 **Chapitre complémentaire.** Il est entièrement facultatif : le reste du volume ne le suppose pas. Il rassemble les outils que l'on sort quand la gérante demande **ce qui arriverait si**. Il suppose le chapitre 3 (régression, pour lire une élasticité) et le chapitre 6 (indicateurs, pour savoir quel résultat on regarde), et il s'appuie sur les comptes de la boutique du chapitre 9, résumés ici.

La gérante de la boutique vous écrit un vendredi soir, avant de boucler le budget de l'an prochain. « *Les fournisseurs annoncent des hausses, la publicité en ligne devient plus chère, et je me demande si je ne devrais pas baisser mes prix de 5 % pour faire venir du monde. Si je baisse mes prix de 5 %, ou si la publicité devient plus chère, ou si les retours augmentent, que devient mon résultat ? Je n'ai pas besoin d'une prévision exacte, juste de savoir ce qui compte vraiment et ce qui peut mal tourner.* »

La demande est typique : elle ne porte pas sur le passé (les chapitres précédents ont décrit, testé, expliqué) mais sur un **avenir incertain**. Trois outils permettent d'y répondre honnêtement, du plus simple au plus riche.

- L'**analyse de sensibilité** (section 13.1) fait varier **un paramètre à la fois** autour de la situation connue et mesure l'effet sur le résultat : elle dit **ce qui compte**.
- La **simulation de Monte-Carlo** (section 13.2) fait varier **tous les paramètres ensemble**, chacun selon une loi plausible : elle dit **jusqu'où le résultat peut aller**, avec quelle probabilité.
- Les **scénarios** (section 13.3) racontent **quelques futurs cohérents** et les confrontent aux décisions possibles : ils disent **que faire**, et à partir de quel seuil on changerait d'avis.

Un fil traverse ces trois sections : un modèle de résultat est une **fabrique de réponses conditionnelles**. Il ne dit jamais « le résultat sera de X € », il dit « *si* les hypothèses sont celles-ci, le résultat est de X € ». Tout le travail de l'analyste consiste à rendre ces « si » **visibles, chiffrés et discutables**.

> ⚠️ **Ce que ce chapitre n'est pas.** Ce n'est pas un cours de prévision (le chapitre 5 en donne les bases) ni un outil pour prendre une décision à la place de la gérante. Le modèle est **volontairement petit** ; il simplifie la boutique à la manière d'un plan de ville, utile pour s'orienter, trompeur si on le prend pour le territoire.

## Le chemin de ce chapitre

| Section | Question | Idée centrale |
|---|---|---|
| 13.1 | Qu'est-ce qui pèse le plus sur le résultat ? | Un modèle petit, calibré et **vérifié** ; la tornade ; les plages choisies décident du classement ; deux paramètres à la fois |
| 13.2 | Jusqu'où le résultat peut-il varier ? | On tire les paramètres selon des lois justifiées par les données (ou déclarées hypothèses) ; probabilité de perte ; nombre de simulations ; dépendance |
| 13.3 | Que faire, et quand changer d'avis ? | Des scénarios qui sont des récits, des « et si » chiffrés, des options comparées sous incertitude, des seuils de bascule, une page pour la gérante |

## Les données du chapitre

> 📦 **Données simulées.** Tous les fichiers sont **simulés** (graines fixes, générateurs `build/donnees_a1.py` et `build/donnees_a3.py`) : la boutique est fictive, et la **TVA est fixée à 20 % pour l'illustration**. Les paramètres du modèle sont estimés sur **l'année 2025** ; les hypothèses qui ne viennent pas des données sont signalées comme telles.

- `compte_resultat_mensuel.csv` : les comptes de 36 mois (chiffre d'affaires hors taxe, achats, charges), pour calibrer et **vérifier** le modèle (section 13.1).
- `commandes.csv`, `lignes_commande.csv`, `produits.csv`, `retours.csv` : les ventes de 2025 par canal, les paniers, les coûts d'achat et les remboursements.
- `sessions_web.csv` et `campagnes.csv` : le trafic du site par source, la conversion, les dépenses publicitaires (le coût d'une session payante).
- `livraisons.csv` et `jours_exploitation.csv` : les transporteurs (section 13.3) et l'effet d'une promotion sur les commandes quotidiennes.

```python hide
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from style import setup, save, BLEU, ORANGE, AQUA, VIOLET, ROUGE, MUET, ENCRE2, GRILLE
import outils_ch13 as O
setup()
T = O.charger()
b = O.calibrer(T)
R = lambda **k: O.resultat(b, **k)
base = R()
```
