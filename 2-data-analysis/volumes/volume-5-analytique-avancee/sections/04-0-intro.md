# Chapitre 4 : Analytique du risque et de l'assurance

> « Un assureur vend une promesse dont il ne connaît le coût qu'après coup. »

```python hide
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch04 as O
D = os.environ["DONNEES"]
d = O.charger(D)
bil = O.bilan_annuel(d)
assert {k: len(v) for k, v in d.items()} == {"pol": 30000, "ex": 84875, "sin": 5113, "pay": 7093, "ver": 5227, "prets": 12000, "suivi": 229747, "vp": 12000}
print({k: len(v) for k, v in d.items()})
```
<!--sortie-->
```text
{'pol': 30000, 'ex': 84875, 'sin': 5113, 'pay': 7093, 'ver': 5227, 'prets': 12000, 'suivi': 229747, 'vp': 12000}
```

Votre travail à la boutique se passe bien. Un matin, la directrice générale du groupe vous annonce que, pour un trimestre, la direction des risques de deux sociétés voisines (un **petit assureur automobile** et une **petite banque** qui finance des particuliers et des commerces) a besoin d'un analyste. Vous n'y connaissez ni le vocabulaire de l'assurance ni celui du crédit. Dès la première réunion, la directrice des risques pose deux questions :

> « *Nos comptes disent que 2025 a été une bonne année pour l'assurance. Est-ce vrai ? Et à la banque, où se cache le prochain problème, avant qu'il n'apparaisse dans les comptes ?* »

Ce sont des questions de **risque** : on cherche à mesurer ce qui peut coûter de l'argent dans l'avenir, à partir de ce que l'on voit dans le passé. Les deux métiers semblent éloignés, mais ils partagent un point de départ : **on a déjà vendu le produit** (un contrat d'assurance, un prêt) **et l'on ne connaît pas encore son coût final**. Un sinistre déclaré aujourd'hui sera payé dans trois ans ; un prêt octroyé il y a six mois fera peut-être défaut l'an prochain. L'analyse du risque consiste à **estimer ce coût final avant qu'il ne soit connu**, et à **surveiller** que l'estimation ne dérive pas.

> 💡 **Intuition.** Vous avez déjà rencontré cette situation sans la nommer. Un **triangle de développement** (section 4.1) est une **analyse de cohortes** (volume III, chapitre 4) : on suit des groupes d'âge différent et l'on compare à âge égal. Un **ratio sinistres/primes** est un **KPI** (volume III, chapitre 6) dont le numérateur est incomplet. Un **suivi de portefeuille** est un **tableau de bord** (volume IV, chapitre 2) dont chaque chiffre doit se rapprocher de la comptabilité. Ce chapitre applique des outils que vous connaissez à un domaine où les erreurs coûtent cher.

## Le chemin de ce chapitre

Nous suivons la directrice des risques, d'abord à l'assurance, puis à la banque, puis dans l'art de produire des états fiables.

- **4.1 Analyse des sinistres.** Exposition, fréquence, coût moyen, **ratio sinistres/primes** ; pourquoi la dernière année est toujours incomplète ; le **triangle de développement** et la **méthode chain ladder** pour estimer ce qui reste à payer, jugée ensuite avec la vérité ; les **gros sinistres**, qui faussent les comparaisons par segment.
- **4.2 Suivi de portefeuille.** À l'assurance, le mix et la rentabilité par segment ; au crédit, les **tranches de retard**, les **créances douteuses**, les **cohortes d'octroi** comparées à âge égal, la **matrice de transition** des retards, la **concentration**, et une dérive sectorielle qui apparaît en 2025.
- **4.3 Reporting de gestion et réglementaire.** Ce qui distingue les deux familles de rapports ; la **définition unique** de chaque indicateur ; le **rapprochement avec la comptabilité** ; la validation à quatre yeux, les versions et le journal.
- **4.4 ➕ Fréquence, sévérité, ratio sinistres/primes et ratio combiné.** Un **modèle linéaire généralisé** de Poisson (avec exposition) et de Gamma pour comprendre **pourquoi** certains segments perdent de l'argent, et de combien le tarif devrait bouger.
- **4.5 ➕ Indicateurs d'alerte précoce.** Quels signaux précèdent un défaut, comment construire une alerte **sans tricher avec le futur**, et comment l'évaluer au regard de la **charge de travail** du comité de crédit.
- **4.6 ➕ Reporting réglementaire et de gestion pour banques et assureurs.** Des **maquettes génériques d'états** avec leurs **contrôles de cohérence**, leurs rapprochements et la justification des écarts. Aucun format officiel n'est reproduit.

## Les données du chapitre

> 📦 **Les données.** Deux portefeuilles **simulés** (graine fixe, aucune donnée réelle), décrits dans la docstring de `build/donnees_a5.py`. **Assurance automobile** (2021-2025, situation au 31 décembre 2025) : `polices.csv` (30 000 contrats), `expositions.csv` (une ligne par police et par année, avec la prime acquise), `sinistres.csv` (5 113 sinistres déclarés), `paiements.csv` (7 093 règlements). **Crédit** (prêts octroyés de janvier 2022 à juin 2025, suivi mensuel jusqu'en décembre 2025) : `prets.csv` (12 000 prêts), `suivi_mensuel.csv` (environ 230 000 lignes prêt-mois : encours, jours de retard, incidents de paiement, utilisation du découvert). Deux fichiers de **vérité** (`verite_sinistres.csv`, `verite_prets.csv`) donnent le coût final de chaque sinistre et le mois de défaut de chaque prêt : ils **n'existeraient pas dans la vie réelle** et ne servent qu'à **juger a posteriori** nos estimations. Deux petits fichiers du chapitre (`ch04-compta-primes.csv`, `ch04-regularisations.csv`) représentent le « grand livre » comptable fictif de l'assureur.

Un mot sur le cadre. L'assureur et la banque sont **fictifs** : aucun nom, aucun pays, aucune autorité de contrôle, aucune loi réelle n'apparaît. Quand nous parlons de règles « internationales » (Bâle pour les banques, IFRS 9 et IFRS 17 pour les provisions et les contrats d'assurance, Solvabilité pour les assureurs), c'est **à titre d'exemples de familles de règles**, sans reproduire leurs seuils ni leurs formats : les seuils de ce chapitre sont **inventés** et dits tels. Vos calculs de ce chapitre ne sont donc pas des calculs réglementaires.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.7 et exercices 4.1 à 4.12 ; chacun renvoie à la section du livre qui l'éclaire.
