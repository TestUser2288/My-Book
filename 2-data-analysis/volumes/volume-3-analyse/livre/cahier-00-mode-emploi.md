# Mode d'emploi

> « On ne mesure bien que ce que l'on a défini avant de regarder. »

Ce cahier est le **compagnon du livre** du volume III (*Analyse*). Le livre explique les méthodes ; le cahier les fait travailler. Il contient, chapitre par chapitre, des **applications guidées**, des **exercices** et leurs **corrigés**, puis le **projet du volume** (répondre de bout en bout à une vraie question métier) et l'auto-évaluation.

## Comment utiliser ce cahier

1. **Lisez d'abord la section du livre.** Chaque section qui a un prolongement ici se termine par une ligne de ce genre :
   > 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.1, exercices 2.1 à 2.4.
2. **Formulez la question avant de calculer.** Avant tout code, écrivez en une phrase : quelle décision cette analyse éclaire-t-elle, et de quel **type** est la question (décrire, comparer, expliquer, prévoir, décider) ? C'est l'habitude centrale du volume.
3. **Écrivez votre hypothèse, puis regardez les données.** Une hypothèse écrite à l'avance protège de la tentation de « trouver ce qui sort ».
4. **Essayez avant de regarder le corrigé.** Les énoncés sont regroupés dans la partie *Exercices*, les corrigés dans la partie *Corrigés* du même chapitre.
5. **Donnez toujours l'incertitude.** Un résultat se rend sous la forme *estimation, intervalle, ce que cela permet de conclure, ce que cela ne permet pas de conclure*.
6. **Recoupez.** Un chiffre obtenu par pandas se recoupe par SQL, par R ou par un calcul à la main ; un écart est un signal.
7. **N'ouvrez pas les fichiers de vérité pour décider.** Ce sont des corrigés : on les consulte après son analyse.

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
| ⭐ | application directe d'une idée ou d'un geste vu dans la section |
| ⭐⭐ | demande de combiner deux idées, ou un petit raisonnement |
| ⭐⭐⭐ | demande de la réflexion, un choix de méthode ou une petite expérience |

Un exercice cite la section du livre qu'il exerce, par exemple « (section 2.2) ».

## Données et environnement

Les données sont celles du livre, dans le dossier `donnees/`. Elles sont toutes **simulées**, avec des graines fixes (script `build/donnees_a3.py`) : vos résultats seront identiques à ceux du livre. Le catalogue complet figure dans la section « Carte du volume, données et environnement » du livre ; en voici l'essentiel.

| Fichier | Contenu | Chapitres |
|---|---|---|
| `clients.csv`, `produits.csv`, `commandes.csv`, `lignes_commande.csv`, `retours.csv` | la base de la boutique (volumes I et II) | 1, 3, 4, 7, 8 |
| `jours_exploitation.csv`, `jours_incidents.csv` | une ligne par jour (et la même série avec des incidents injectés) | 1, 3, 5 |
| `ab_email.csv`, `ab_site.csv` | deux tests A/B | 2 |
| `sessions_web.csv`, `campagnes.csv` | trafic du site et dépenses publicitaires | 4, 6, 10 |
| `budget_reel_2025.csv`, `benchmark_secteur.csv` | budget contre réalisé ; indicateurs d'un secteur fictif | 6, 7, 8 |
| `compte_resultat_mensuel.csv`, `bilan_annuel.csv` | comptes de la boutique | 9, 13 |
| `livraisons.csv`, `reappro_fournisseur.csv`, `stock_quotidien.csv` | logistique | 11 |
| `employes.csv`, `employes_annees.csv`, `departs.csv` | ressources humaines (petits effectifs) | 12 |
| `verite_incidents.csv` | **corrigé** des incidents injectés | à la fin |

> ⚠️ **Les chiffres sont fictifs.** La boutique, ses clients et ses résultats sont inventés. Ne tirez de ces données aucune conclusion sur le monde réel : elles servent à apprendre une méthode.

Chaque chapitre du cahier est **autonome** : il commence par ses imports et recharge ses données. Les applications sont dimensionnées pour s'exécuter en **quelques secondes à quelques dizaines de secondes** sur un ordinateur ordinaire, sans réseau.

## Lancer le code

Placez-vous dans le dossier du volume (celui qui contient `donnees/`), car les chemins sont relatifs (`donnees/commandes.csv`). Vous pouvez travailler dans un notebook Jupyter, dans un éditeur avec la commande `python`, dans RStudio pour R, ou dans un outil de bases de données pour SQL.

> ⚠️ **Les chemins.** Si Python répond `FileNotFoundError`, c'est presque toujours que vous n'êtes pas dans le bon dossier : vérifiez avec `import os; print(os.getcwd())`.

> ⚠️ **Le hasard.** Les exercices qui tirent au sort (simulations, rééchantillonnages) fixent une **graine** (`np.random.default_rng(0)`) : si vous la changez, vos nombres changeront un peu, et c'est normal ; ce qu'il faut retrouver, c'est l'ordre de grandeur et la conclusion.

> ⚠️ **Excel.** Les exercices qui demandent un tableur se font dans Excel ou dans LibreOffice Calc (gratuit), qui lit les mêmes fichiers ; quand un menu ou une fonction diffère, la documentation de votre version fait foi.

## Vérifier son installation

Quatre courts blocs vérifient que les bibliothèques sont installées et que les données se chargent, en Python, en SQL puis en R.

**1. Les bibliothèques Python** (le volume utilise celles des volumes précédents) :

```python
import sys
from importlib import import_module
from importlib.metadata import version
print("python", sys.version.split()[0])
for p in ["numpy", "pandas", "scipy", "statsmodels", "sklearn", "matplotlib"]:
    import_module(p)                              # échoue si la bibliothèque est absente
    print(f"{p:12s}", version("scikit-learn" if p == "sklearn" else p))
```
<!--sortie-->
```text
python 3.13.3
numpy        2.5.3
pandas       3.0.6
scipy        1.18.1
statsmodels  0.15.0
sklearn      1.9.1
matplotlib   3.11.2
```

**2. Les données.** Nous chargeons les commandes et les jours d'exploitation :

```python
import pandas as pd

commandes = pd.read_csv("donnees/commandes.csv")
jours = pd.read_csv("donnees/jours_exploitation.csv", parse_dates=["date"])
print("commandes :", len(commandes), "| jours d'exploitation :", len(jours), "du", jours["date"].min().date(), "au", jours["date"].max().date())
```
<!--sortie-->
```text
commandes : 36395 | jours d'exploitation : 1096 du 2023-01-01 au 2025-12-31
```

**3. Une requête SQL.** Nous copions les commandes dans une base SQLite en mémoire, puis interrogeons-la :

```python
import sqlite3
con = sqlite3.connect(":memory:")
commandes.to_sql("commandes", con, index=False)
```

```sql
SELECT canal, COUNT(*) AS commandes
FROM commandes
GROUP BY canal
ORDER BY commandes DESC;
```
<!--sortie-->
```text
   canal  commandes
Boutique      16975
    Site      15463
 Réseaux       3957
```

**4. Le même comptage en R**, pour vérifier que R et le tidyverse sont là :

```r
suppressPackageStartupMessages({library(readr); library(dplyr)})
commandes <- read_csv(file.path(Sys.getenv("DONNEES"), "commandes.csv"), show_col_types = FALSE)
print(count(commandes, canal, sort = TRUE))
```
<!--sortie-->
```text
# A tibble: 3 × 2
  canal        n
  <chr>    <int>
1 Boutique 16975
2 Site     15463
3 Réseaux   3957
```

Vous devez lire une version pour chaque bibliothèque, **36 395 commandes** et **1 096 jours** d'exploitation, et **le même tableau** par canal en SQL et en R. Si tout concorde, vous êtes prêt.

## Mini-diagnostic de départ

Huit questions pour vérifier que les réflexes de base de l'analyse sont en place. Répondez par écrit, puis comparez avec les corrigés plus bas ; chaque corrigé indique le chapitre à relire si la réponse vous a échappé.

1. Pour chacune de ces questions de la gérante, dites de quel **type** elle relève (décrire, comparer, expliquer, prévoir, décider) : (a) « Combien de commandes avons-nous eues en novembre ? » (b) « Le nouveau transporteur livre-t-il plus vite que l'ancien ? » (c) « Qu'est-ce qui pousse les clients à partir ? » (d) « Combien vendrons-nous en décembre ? » (e) « Faut-il refaire la promotion en juillet ? »
2. Un test A/B sur l'objet d'un e-mail donne un taux d'achat de 2,92 % pour A et 3,38 % pour B, avec 6 000 contacts par groupe. L'écart est-il « significatif » ? Que peut-on conclure ?
3. La dépense publicitaire et le chiffre d'affaires quotidiens sont corrélés (coefficient de 0,42). Peut-on en conclure que la publicité fait vendre ? Que regarder ?
4. Les ventes de sept jours consécutifs valent 20, 22, 19, 25, 40, 21 et 23. Calculez la **moyenne mobile sur trois jours** (là où elle est définie) et dites ce que le 40 devient.
5. Le « taux de conversion » du site est-il un bon indicateur ? Comment le définir sans ambiguïté, et quelle est sa valeur sur nos sessions ?
6. Le panier moyen est de 100,4 € mais la médiane est plus basse. Que cela indique-t-il, et lequel annoncer ?
7. Dans une régression de `log(nombre de commandes)` sur la promotion, le coefficient de la promotion vaut 0,177. Que signifie-t-il en pourcentage ?
8. Un effet réel de +0,4 point sur un taux d'achat de 3 % existe, mais le test ne le détecte pas avec 6 000 contacts par groupe. Pourquoi, et que faire ?

Les **corrigés** s'appuient sur des calculs : le code est ci-dessous.

```python
import numpy as np
import statsmodels.api as sm
from scipy import stats
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize, proportions_ztest

ab = pd.read_csv("donnees/ab_email.csv")
n = ab.groupby("groupe").size(); s = ab.groupby("groupe")["achat_7j"].sum()
stat, p = proportions_ztest([s["B"], s["A"]], [n["B"], n["A"]])
ecart = s["B"] / n["B"] - s["A"] / n["A"]
se = np.sqrt((s["A"] / n["A"]) * (1 - s["A"] / n["A"]) / n["A"] + (s["B"] / n["B"]) * (1 - s["B"] / n["B"]) / n["B"])
print("Q2 achats :", s.to_dict(), "| écart :", round(ecart * 100, 2), "points | p =", round(p, 3), "| IC 95 % :", round((ecart - 1.96 * se) * 100, 2), "à", round((ecart + 1.96 * se) * 100, 2), "points")
puissance = NormalIndPower().power(effect_size=proportion_effectsize(0.0338, 0.0292), nobs1=6000, alpha=0.05)
n_necessaire = NormalIndPower().solve_power(effect_size=proportion_effectsize(0.034, 0.030), power=0.8, alpha=0.05)
print("Q8 puissance observée :", round(puissance, 2), "| contacts par groupe pour +0,4 point (3,0 % -> 3,4 %) à 80 % de puissance :", round(n_necessaire))
```
<!--sortie-->
```text
Q2 achats : {'A': 175, 'B': 203} | écart : 0.47 points | p = 0.143 | IC 95 % : -0.16 à 1.09 points
Q8 puissance observée : 0.3 | contacts par groupe pour +0,4 point (3,0 % -> 3,4 %) à 80 % de puissance : 30362
```

```python
pub = jours["depense_pub"].corr(jours["chiffre_affaires"])
jours["mois"] = jours["date"].dt.to_period("M")
a_mois_egal = (jours["depense_pub"] - jours.groupby("mois")["depense_pub"].transform("mean")).corr(jours["chiffre_affaires"] - jours.groupby("mois")["chiffre_affaires"].transform("mean"))
print("Q3 corrélation brute :", round(pub, 2), "| à mois égal (écarts à la moyenne du mois) :", round(a_mois_egal, 2))
ventes = pd.Series([20, 22, 19, 25, 40, 21, 23])
print("Q4 moyenne mobile sur 3 jours :", ventes.rolling(3).mean().dropna().round(2).tolist(), "| moyenne :", round(ventes.mean(), 2))
ses = pd.read_csv("donnees/sessions_web.csv")
print("Q5 conversion :", int(ses["commande"].sum()), "commandes /", len(ses), "sessions =", round(ses["commande"].mean() * 100, 2), "%")
lig = pd.read_csv("donnees/lignes_commande.csv")
paniers = lig.groupby("id_commande")["montant"].sum()
print("Q6 panier moyen :", round(paniers.mean(), 1), "| médiane :", round(paniers.median(), 1))
print("Q7 exp(0,177) - 1 =", round(np.exp(0.177) - 1, 3))
```
<!--sortie-->
```text
Q3 corrélation brute : 0.42 | à mois égal (écarts à la moyenne du mois) : 0.05
Q4 moyenne mobile sur 3 jours : [20.33, 22.0, 28.0, 28.67, 28.0] | moyenne : 24.29
Q5 conversion : 6078 commandes / 127022 sessions = 4.78 %
Q6 panier moyen : 100.4 | médiane : 79.8
Q7 exp(0,177) - 1 = 0.194
```

**1.** (a) **Décrire** ; (b) **comparer** ; (c) **expliquer** ; (d) **prévoir** ; (e) **décider**. Les chapitres associés : 1 et 6 pour décrire, 2 pour comparer, 3 et 4 pour expliquer, 5 pour prévoir, 6 et les chapitres complémentaires pour décider (introduction).

**2.** L'écart observé est de **+0,47 point** (203 achats sur 6 000 contre 175, soit 3,38 % contre 2,92 %), mais le test donne **p = 0,14** et l'intervalle de confiance à 95 % de l'écart va de **−0,16 à +1,09 point** : il contient zéro. On **ne peut pas conclure** que B est meilleur, ni qu'il ne l'est pas : le test n'a pas assez de données. Une p-valeur supérieure à 0,05 signifie « données compatibles avec l'absence d'effet », pas « absence d'effet » (chapitre 2, sections 2.1 et 2.2).

**3.** Non, pas sur cette seule corrélation. La dépense publicitaire est **plus forte en novembre-décembre et au printemps**, les mêmes périodes où les ventes sont fortes : la **saison** (variable de confusion) explique une grande part du lien. À mois égal (en comparant chaque jour à la moyenne de son mois), la corrélation tombe à presque rien. Il faut une comparaison à saison égale, une régression ou, mieux, une expérience (chapitres 1, 2 et 3).

**4.** La moyenne mobile sur trois jours vaut 20,33 ; 22,0 ; 28,0 ; 28,67 ; 28,0 (cinq valeurs, centrées sur les jours 2 à 6). Le 40 est « étalé » sur trois valeurs, qui montent toutes à 28 environ (la moyenne de la série est de 24,29) : la moyenne mobile **lisse** le pic, au prix d'un retard et d'une perte de netteté (chapitre 5, section 5.2).

**5.** Oui, **à condition d'une définition sans ambiguïté** : nombre de commandes divisé par le nombre de sessions, sur la même période et le même périmètre (ici, le site). Sur nos sessions, 6 078 commandes pour 127 022 sessions donnent **4,78 %**. Un bon indicateur est défini, mesurable, comparable dans le temps et relié à une action (chapitre 6, section 6.1).

**6.** Le panier moyen (100,4 €) est tiré vers le haut par quelques gros paniers (médiane de 79,8 €) : la distribution est **asymétrique**. La **médiane**, de 79,8 €, décrit mieux le panier « typique » (la moitié des commandes en dessous) ; on annonce l'une et l'autre, avec leur définition, ou la médiane seule pour parler d'une commande ordinaire (chapitre 1, section 1.1 ; volume I, section 1.1).

**7.** Un coefficient $b$ sur le logarithme du nombre de commandes se lit comme une variation **relative** : $e^{0{,}177}-1\approx+19{,}4\ \%$. Les jours de promotion, il y a environ 19 % de commandes de plus, **toutes choses égales par ailleurs** (chapitre 3, section 3.2).

**8.** Parce qu'un petit effet demande de **gros échantillons** : avec 6 000 contacts par groupe, la puissance du test pour distinguer 2,92 % de 3,38 % est d'environ **30 %** (code ci-dessus), loin des 80 % visés. Pour détecter un écart de 0,4 point (de 3,0 % à 3,4 %), il faudrait environ **30 000 contacts par groupe**, soit cinq fois plus que la liste. On peut augmenter l'échantillon, allonger la durée, regrouper des tests, ou accepter qu'un effet de cette taille ne vaille pas le coût de le mesurer (chapitre 2, section 2.5).

> 🧭 **Comment vous situer.** Six bonnes réponses sur huit indiquent que vous pouvez aborder le volume directement. Si les questions 2, 3 et 8 vous ont posé problème, lisez d'abord le chapitre 2 (tests et A/B) avant les chapitres 3 à 6.
