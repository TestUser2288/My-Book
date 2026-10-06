# Mode d'emploi

> « On comprend en lisant, on retient en calculant. »

Ce cahier est le **compagnon du livre** du volume V (*Risque et assurance*). Le livre explique les idées ; le cahier les fait travailler. Il contient, chapitre par chapitre, des **applications guidées**, des **exercices** et leurs **corrigés**, puis le **projet du volume** (construire un modèle de tarification avec validation et notes réglementaires) et l'auto-évaluation.

## Comment utiliser ce cahier

1. **Lisez d'abord la section du livre.** Chaque section qui a un prolongement ici se termine par une ligne de ce genre :
   > 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.
2. **Essayez avant de regarder le corrigé.** Les énoncés sont regroupés dans la partie *Exercices*, les corrigés dans la partie *Corrigés* du même chapitre : on peut chercher sans voir la réponse.
3. **Calculez d'abord à la main.** Dans ce volume, presque chaque formule se vérifie sur trois ou quatre contrats : faites-le avec un crayon avant d'écrire du code. Le code confirme, il ne remplace pas la compréhension.
4. **Faites les applications dans l'ordre** : chacune raconte une petite étude, avec une question, des étapes, du code et une lecture des résultats.
5. **Comparez à la vérité programmée.** Les données du volume sont simulées : quand le cahier le propose, relisez l'estimation à la lumière du mécanisme qui a produit les données. En pratique, vous n'aurez jamais cette chance : c'est précisément ce qui rend la validation indispensable.
6. **Dites l'incertitude.** Un chiffre de risque sans intervalle, sans hypothèse ni période n'est pas un résultat.

## Numérotation et niveaux

Chaque chapitre du cahier correspond au chapitre du livre de même numéro.

| Élément | Numérotation | Exemple |
|---|---|---|
| Application | `Application N.k` | Application 2.1 : première application du chapitre 2 |
| Exercice | `Exercice N.k` | Exercice 2.3 : troisième exercice du chapitre 2 |
| Corrigé | `Corrigé N.k` | Corrigé 2.3 : correction de l'exercice 2.3 |

La difficulté des exercices est indiquée par des étoiles :

| Niveau | Signification |
|---|---|
| ⭐ | application directe d'une formule ou d'une idée vue dans la section |
| ⭐⭐ | demande de combiner deux idées, ou un petit raisonnement |
| ⭐⭐⭐ | demande de la réflexion, une démonstration ou une petite expérience |

Un exercice cite la section du livre qu'il exerce, par exemple « (section 1.2) ».

## Données et environnement

Les données sont celles du livre, dans le dossier `donnees/`. Tous les jeux sont **simulés** avec des graines fixes (script `build/donnees5.py`), sauf `credit_defaut.csv` (jeu réel, UCI, licence CC0) : vos résultats seront identiques à ceux du livre. Le catalogue complet, avec les colonnes de chaque fichier, figure dans la section « Carte du volume, données et environnement » du livre ; en voici l'essentiel.

| Famille | Fichiers | Chapitres |
|---|---|---|
| Crédit | `credit_defaut`, `credits_conso`, `recouvrements`, `revolving_defauts`, `portefeuille_ifrs9`, `notations_panel`, `taux_defaut_macro` | 1, 3, 4 |
| Assurance dommages et santé | `polices_auto`, `sinistres_auto`, `triangle_rc`, `triangle_dommages`, `triangle_choc`, `sante_assures` | 2, projet |
| Marchés et pertes | `rendements_marche`, `courbe_taux`, `pertes_operationnelles` | 3, 7 |
| Vie et réassurance | `mortalite_population`, `portefeuille_vie`, `sinistres_gros`, `cat_annuel` | 5, 6, 7 |
| Fraude et Takaful | `transactions_lab`, `comptes_lab`, `takaful_fonds` | 4 |

> ⚠️ **Les fichiers de vérité ne sont pas des entrées.** `triangle_*_verite`, `marche_verite`, `mortalite_verite`, `mortalite_kt_vrai` et `verite_lab` contiennent la bonne réponse que le modèle est censé retrouver ou la réalité à venir. Ils servent à **juger** un résultat après coup, jamais à l'obtenir. Les utiliser comme variables d'entrée serait une fuite d'information (volume III, section 1.1).

Chaque chapitre du cahier est **autonome** : il commence par ses imports et recharge ses données. Les applications sont dimensionnées pour tourner en **quelques dizaines de secondes** sur un ordinateur ordinaire, sans carte graphique ni réseau.

## Lancer le code

Placez-vous dans le dossier du volume (celui qui contient `donnees/`), car les chemins sont relatifs (`donnees/credits_conso.csv`). Vous pouvez travailler dans un notebook Jupyter, dans un éditeur avec la commande `python`, ou dans un terminal interactif.

> ⚠️ **Les chemins.** Si Python répond `FileNotFoundError`, c'est presque toujours que vous n'êtes pas dans le bon dossier : vérifiez avec `import os; print(os.getcwd())`.

> ⚠️ **Les graines.** Les simulations du cahier fixent leur graine (`np.random.default_rng(42)`, par exemple). Si vous changez la graine, vos chiffres changeront un peu : c'est une excellente façon de **voir l'incertitude** d'une estimation de queue, mais ne comparez pas alors vos résultats à ceux du corrigé à la décimale.

## Vérifier son installation

Deux courts blocs vérifient que les bibliothèques sont installées et que les données se chargent. Les numéros de version peuvent différer des nôtres (voir le livre), à condition que tout s'exécute.

**1. Les bibliothèques.**

```python
import sys
from importlib import import_module
from importlib.metadata import version
print("python", sys.version.split()[0])
for p in ["numpy", "pandas", "scipy", "sklearn", "statsmodels", "arch", "lifelines", "matplotlib"]:
    import_module(p)                              # échoue si la bibliothèque est absente
    print(f"{p:12s}", version("scikit-learn" if p == "sklearn" else p))
```
<!--sortie-->
```text
python 3.13.3
numpy        2.5.3
pandas       3.0.6
scipy        1.18.1
sklearn      1.9.1
statsmodels  0.15.0
arch         8.0.0
lifelines    0.30.3
matplotlib   3.11.2
```

**2. Les données et un premier modèle.** Nous chargeons le portefeuille de prêts, vérifions le taux de défaut, puis ajustons le modèle de fréquence le plus simple de l'assurance (un seul coefficient, avec l'exposition comme décalage) :

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm

prets = pd.read_csv("donnees/credits_conso.csv")
auto = pd.read_csv("donnees/polices_auto.csv")
print("prêts :", len(prets), "| taux de défaut à 12 mois :", round(prets["defaut_12m"].mean(), 4))

X = np.ones((len(auto), 1))
modele = sm.GLM(auto["nb_sinistres"], X, family=sm.families.Poisson(), offset=np.log(auto["exposition"])).fit()
print("fréquence annuelle estimée :", round(float(np.exp(modele.params.iloc[0])), 4))
```
<!--sortie-->
```text
prêts : 40000 | taux de défaut à 12 mois : 0.0597
fréquence annuelle estimée : 0.0661
```

Vous devez lire une version pour chaque bibliothèque, **40 000 prêts avec un taux de défaut d'environ 6 %**, et une **fréquence annuelle d'environ 6,6 %** (c'est le nombre de sinistres divisé par l'exposition totale, ce que le GLM retrouve).

## Mini-diagnostic de départ

Huit questions pour vérifier que les outils des volumes précédents sont en place. Répondez par écrit, puis comparez avec les corrigés plus bas ; chaque corrigé indique le volume à relire en cas d'hésitation. Il n'y a pas de note : l'objectif est de savoir **où revenir** avant de commencer.

1. Un prêt a une probabilité de défaut de 2 %. Sur 100 prêts **indépendants**, quelle est la probabilité qu'au moins un fasse défaut ?
2. Sur 10 000 prêts indépendants de probabilité de défaut 2 %, quels sont l'espérance et l'écart-type du nombre de défauts ?
3. Un contrat a une fréquence annuelle de sinistres de 0,065 et a été en vigueur pendant une demi-année. Dans le modèle de Poisson, quelle est la probabilité qu'il n'ait eu aucun sinistre ?
4. Dans une régression logistique, $\text{logit}(p) = -3 + 0{,}5\,x$. Quelle est la probabilité de défaut pour $x=2$, et de quel facteur l'**odds** est-il multiplié quand $x$ augmente d'une unité ?
5. Dans un GLM de Poisson à lien logarithmique, le coefficient d'une zone vaut 0,20 par rapport à la zone de référence. De quel facteur la fréquence est-elle multipliée ?
6. Pourquoi un découpage **aléatoire** entre apprentissage et test est-il trompeur quand les contrats sont observés sur trois années successives ?
7. Un modèle annonce « aucun défaut » pour tous les prêts d'un portefeuille où 6 % des prêts font défaut. Quelle est son exactitude ? Que vaut l'AUC d'un modèle qui classe au hasard ?
8. Les sinistres matériels ont un écart-type d'environ 1 800 €. Quel est l'écart-type de la **moyenne** de 5 000 sinistres indépendants ?

```python
from math import exp, sqrt

print("Q1 :", round(1 - 0.98**100, 4))
print("Q2 :", 10000 * 0.02, "et", round(sqrt(10000 * 0.02 * 0.98), 2))
print("Q3 :", round(exp(-0.065 * 0.5), 4))
p = 1 / (1 + exp(-(-3 + 0.5 * 2)))
print("Q4 :", round(p, 4), "et", round(exp(0.5), 3))
print("Q5 :", round(exp(0.20), 3))
print("Q7 :", 1 - 0.06)
print("Q8 :", round(1800 / sqrt(5000), 1))
```
<!--sortie-->
```text
Q1 : 0.8674
Q2 : 200.0 et 14.0
Q3 : 0.968
Q4 : 0.1192 et 1.649
Q5 : 1.221
Q7 : 0.94
Q8 : 25.5
```

**Corrigés du diagnostic.**

1. $1-0{,}98^{100}\approx 0{,}8674$ : presque sûr malgré une probabilité individuelle faible (volume I, section 2.1).
2. Binomiale : espérance $10\,000\times 0{,}02=200$, écart-type $\sqrt{10\,000\times0{,}02\times0{,}98}\approx 14{,}0$ (volume I, section 2.2).
3. $e^{-0{,}065\times0{,}5}\approx 0{,}968$ : le nombre de sinistres suit une loi de Poisson de moyenne $\lambda\times\text{exposition}$ (volume II, section 2.3).
4. $\text{logit}(p)=-2$, donc $p=1/(1+e^{2})\approx 0{,}119$ ; l'odds est multiplié par $e^{0{,}5}\approx 1{,}649$ (volume II, section 2.2).
5. $e^{0{,}20}\approx 1{,}221$ : un coefficient dans un GLM à lien logarithmique est un **logarithme de facteur multiplicatif** (volume II, section 2.3).
6. Un découpage aléatoire place dans l'apprentissage des contrats **postérieurs** à ceux du test : le modèle « voit le futur », et la performance est surestimée. On valide **hors période** (apprendre sur 2022-2023, tester sur 2024) (volume III, section 1.1).
7. L'exactitude est de $94\ \%$, et pourtant le modèle ne détecte rien : l'exactitude est trompeuse quand l'événement est rare. Un classement au hasard a une **AUC de 0,5** (volume III, section 5.1).
8. $1800/\sqrt{5000}\approx 25{,}5$ € : l'écart-type de la moyenne décroît en $1/\sqrt n$ (volume I, section 2.4).

Si plus de deux questions vous ont gêné, relisez d'abord les sections de volume I et II indiquées : elles sont le socle de ce volume.

## Plan du cahier

| Chapitre | Contenu |
|---|---|
| 1. Risque de crédit et scoring | construire et évaluer une grille de score, comparer modèles de défaut, mesurer Gini et KS ; ➕ WOE et IV, perte attendue IFRS 9, matrices de transition |
| 2. Modélisation actuarielle | fréquence et sévérité, construction d'un tarif, provisionnement par triangles ; ➕ GLM tarifaires et crédibilité, *chain ladder* et Mack, assurance santé |
| 3. Mesures de risque et stress tests | VaR et ES par trois méthodes, scénarios de crise ; ➕ risque opérationnel, rétro-test |
| 4. Cadre réglementaire | capital de Bâle, SCR de Solvabilité, répartition de l'excédent d'un fonds de Takaful ; ➕ fraude et lutte contre le blanchiment |
| ➕ 5. Assurance vie | table de mortalité, primes et réserves, modèle de Lee-Carter |
| ➕ 6. Réassurance | tarifer un excédent de sinistre, comparer des couvertures |
| ➕ 7. Actif-passif et portefeuille | duration et adossement, frontière efficiente |
| Projet et auto-évaluation | un modèle de tarification avec validation hors période et notes réglementaires, puis des questions pour vérifier ses acquis |
