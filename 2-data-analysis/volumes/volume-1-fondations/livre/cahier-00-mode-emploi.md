# Mode d'emploi

> « On comprend en lisant, on retient en calculant. »

Ce cahier est le **compagnon du livre** du volume I (*Fondations*). Le livre explique les idées ; le cahier les fait travailler. Il contient, chapitre par chapitre, des **applications guidées**, des **exercices** et leurs **corrigés**, puis le **projet du volume** (une première analyse, du fichier brut au tableau de synthèse) et l'auto-évaluation.

## Comment utiliser ce cahier

1. **Lisez d'abord la section du livre.** Chaque section qui a un prolongement ici se termine par une ligne de ce genre :
   > 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.1, exercices 1.1 à 1.4.
2. **Essayez avant de regarder le corrigé.** Les énoncés sont regroupés dans la partie *Exercices*, les corrigés dans la partie *Corrigés* du même chapitre : on peut chercher sans voir la réponse.
3. **Calculez d'abord à la main.** Presque chaque notion de ce volume se vérifie sur quatre ou cinq lignes d'un tableau : faites-le avec un crayon avant d'écrire du code. Le code confirme ; il ne remplace pas la compréhension.
4. **Faites les applications dans l'ordre.** Chacune raconte une petite étude de la boutique : une question de la gérante, des étapes, du code, puis une lecture des résultats.
5. **Vérifiez par un second chemin.** Quand c'est possible, obtenez le même chiffre avec un autre outil (tableur, SQL, Python, R). C'est le meilleur détecteur d'erreurs.
6. **Dites ce que le chiffre ne dit pas.** Un résultat sans période, sans source, sans limite n'est pas un résultat.

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

Un exercice cite la section du livre qu'il exerce, par exemple « (section 1.2) ».

## Données et environnement

Les données sont celles du livre, dans le dossier `donnees/`. Elles sont toutes **simulées**, avec des graines fixes (script `build/donnees_a1.py`) : vos résultats seront identiques à ceux du livre. Le catalogue complet, avec les colonnes de chaque fichier, figure dans la section « Carte du volume, données et environnement » du livre ; en voici l'essentiel.

| Fichier | Contenu | Chapitres |
|---|---|---|
| `clients.csv`, `produits.csv` | 6 000 clients ; 120 produits en six catégories | tous |
| `commandes.csv`, `lignes_commande.csv`, `retours.csv` | commandes 2023-2025, leurs lignes, les retours | 1 à 4 |
| `jours_exploitation.csv` | un jour par ligne : commandes, chiffre d'affaires, météo, promotion, publicité | 1, 2, 4 |
| `enquete_satisfaction.csv` | enquête de satisfaction (958 réponses) | 1, 5, projet |
| `ventes_2025.xlsx` | classeur Excel de 2025 (feuilles `Lignes`, `Produits`, `Clients`) | 2 |
| `export_caisse_brut.csv` | export de caisse désordonné (une semaine) | 2, 4, projet |
| `boutique.db` | base SQLite avec les six premières tables | 3, 4 |

> ⚠️ **Les chiffres sont fictifs.** La boutique, ses clients et ses ventes sont inventés. Ne tirez de ces données aucune conclusion sur le monde réel : elles servent à apprendre une méthode.

Chaque chapitre du cahier est **autonome** : il commence par ses imports et recharge ses données. Les applications sont dimensionnées pour s'exécuter en **quelques secondes à quelques dizaines de secondes** sur un ordinateur ordinaire, sans réseau.

## Lancer le code

Placez-vous dans le dossier du volume (celui qui contient `donnees/`), car les chemins sont relatifs (`donnees/commandes.csv`). Vous pouvez travailler dans un notebook Jupyter, dans un éditeur avec la commande `python`, dans RStudio pour R, ou dans un outil de bases de données pour SQL.

> ⚠️ **Les chemins.** Si Python répond `FileNotFoundError`, c'est presque toujours que vous n'êtes pas dans le bon dossier : vérifiez avec `import os; print(os.getcwd())`.

> ⚠️ **Les graines.** Les simulations du cahier fixent leur graine (`np.random.default_rng(42)`, par exemple). Si vous la changez, vos chiffres changeront un peu : c'est une excellente façon de **voir l'incertitude** d'une estimation, mais ne comparez pas alors vos résultats à ceux du corrigé à la décimale.

> ⚠️ **Excel.** Les exercices du chapitre 2 se font dans votre tableur. Si vous n'avez pas Excel, LibreOffice Calc (gratuit) lit le même fichier `ventes_2025.xlsx` et accepte presque toutes les formules du livre ; quand un menu ou une fonction diffère, la documentation de votre version fait foi.

## Vérifier son installation

Quatre courts blocs vérifient que les bibliothèques sont installées et que les données se chargent, en Python, en SQL puis en R. Les numéros de version peuvent différer des nôtres, à condition que tout s'exécute.

**1. Les bibliothèques Python.**

```python
import sys
from importlib import import_module
from importlib.metadata import version
print("python", sys.version.split()[0])
for p in ["numpy", "pandas", "scipy", "statsmodels", "matplotlib", "openpyxl", "polars", "duckdb"]:
    import_module(p)                              # échoue si la bibliothèque est absente
    print(f"{p:12s}", version(p))
```
<!--sortie-->
```text
python 3.13.3
numpy        2.5.3
pandas       3.0.6
scipy        1.18.1
statsmodels  0.15.0
matplotlib   3.11.2
openpyxl     3.1.5
polars       2.0.0
duckdb       1.5.6
```

**2. Les données et la base.** Nous chargeons les commandes, ouvrons la base SQLite et comparons les deux comptes.

```python
import sqlite3
import pandas as pd

commandes = pd.read_csv("donnees/commandes.csv")
con = sqlite3.connect("donnees/boutique.db")
print("fichier CSV :", len(commandes), "commandes,", commandes["id_client"].nunique(), "clients différents")
```
<!--sortie-->
```text
fichier CSV : 36395 commandes, 4806 clients différents
```

**3. Une requête SQL** sur la même connexion `con` :

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

**4. Le même calcul en R**, pour vérifier que R et le tidyverse sont là :

```r
suppressPackageStartupMessages({library(readr); library(dplyr)})
commandes <- read_csv("donnees/commandes.csv", show_col_types = FALSE)
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

Vous devez lire une version pour chaque bibliothèque, **36 395 commandes** pour **4 806 clients différents** (sur les 6 000 inscrits : tous n'ont pas commandé), et **le même tableau** par canal en SQL et en R : la boutique en tête avec 16 975 commandes, puis le Site avec 15 463 et les réseaux avec 3 957. Si les trois comptes concordent, votre installation est prête.

## Mini-diagnostic de départ

Huit questions pour vérifier que les gestes de base sont en place. Répondez par écrit, puis comparez avec les corrigés plus bas ; chaque corrigé indique le chapitre à lire en cas d'hésitation. Il n'y a pas de note : l'objectif est de savoir **où revenir** avant de commencer.

1. Un article à 40 € est soldé de 20 %. Une carte de fidélité accorde ensuite 10 % de remise **sur le prix déjà soldé**. Quel est le prix final, et quelle est la remise totale en pourcentage du prix de départ ?
2. Cinq jours de commandes : 12, 15, 23, 11 et 19. Calculez la moyenne et la médiane. Le sixième jour, jour de promotion, compte 60 commandes : que deviennent la moyenne et la médiane ?
3. La boutique a reçu 100 commandes au panier moyen de 80 € et 300 commandes au panier moyen de 120 €. Quel est le panier moyen de l'ensemble ?
4. Dans `commandes.csv`, combien de commandes du canal `Site` passées en **2025** portent un code promo ? Quelle part cela représente-t-il des commandes du Site de 2025 ?
5. Trois tableaux. **Produits** : P1 « Bougie » (Décoration, 10 €), P2 « Plaid » (Maison, 30 €), P3 « Cahier » (Papeterie, 5 €). **Lignes** : (L1, P1, quantité 2), (L2, P2, 1), (L3, P1, 1), (L4, P3, 3). Quel est le chiffre d'affaires de chaque catégorie ? De quelle opération avez-vous eu besoin ?
6. Le tableau ci-dessous donne les commandes de 2025 selon le canal et le mode de livraison. Quelle part des commandes du Site est livrée à domicile ?

```text
mode_livraison  Domicile  Point relais  Retrait magasin  Total
canal                                                         
Boutique               0             0             5442   5442
Réseaux              776           551               99   1426
Site                3374          2272              432   6078
Total               4150          2823             5973  12946
```

7. Le chiffre d'affaires de la boutique est de 1 138 932 € en 2023 et de 1 324 764 € en 2025. Quelle est la croissance sur les deux ans ? Quel est le taux de croissance **annuel moyen** ?
8. L'enquête de satisfaction a été envoyée à 3 875 clients ; 958 ont répondu, et 55 % des répondants donnent une note de 4 ou 5. La gérante en conclut : « 55 % de nos clients sont satisfaits ». Cette conclusion est-elle justifiée ?

## Corrigés du mini-diagnostic

**1.** La remise de 20 % ramène le prix à $40\times0{,}80=32$ €. Les 10 % s'appliquent à 32 € : $32\times0{,}90=28{,}80$ €. La remise totale est $(40-28{,}80)/40=28\ \%$, et **non 30 %** : les pourcentages de remises successives ne s'additionnent pas, ils se **multiplient** ($0{,}80\times0{,}90=0{,}72$). À relire : section 1.5 (pourcentages).

**2.** Moyenne : $(12+15+23+11+19)/5=80/5=16$ ; médiane : on trie (11, 12, 15, 19, 23), la valeur du milieu est **15**. Avec 60 commandes le sixième jour : la moyenne devient $140/6\approx23{,}3$, la médiane (11, 12, 15, 19, 23, 60 : moyenne des deux valeurs du milieu) $(15+19)/2=17$. La moyenne a bondi de 46 %, la médiane de 13 % : la **médiane résiste aux valeurs extrêmes**. À relire : section 1.1.

**3.** Il ne faut pas faire $(80+120)/2=100$ : les deux canaux n'ont pas le même poids. La **moyenne pondérée** donne $(100\times80+300\times120)/400=44\,000/400=110$ €. À relire : section 1.5 (moyennes pondérées).

**4.** On filtre sur l'année, le canal et la présence d'un code promo. Les valeurs vides de `code_promo` signifient « pas de promotion » :

```python
site25 = c25[c25["canal"] == "Site"]
avec_code = site25["code_promo"].notna().sum()
print(avec_code, "sur", len(site25), "soit", round(100 * avec_code / len(site25), 1), "%")
```
<!--sortie-->
```text
960 sur 6078 soit 15.8 %
```

**960 commandes sur 6 078, soit 15,8 %**. Le même calcul en SQL serait `SELECT COUNT(code_promo) FROM commandes WHERE canal = 'Site' AND date_commande >= '2025-01-01'` (le comptage d'une colonne ignore les valeurs vides). À relire : sections 3.1 et 4.3.

**5.** Il faut **joindre** les lignes aux produits (par `id_produit`), calculer le montant de chaque ligne (quantité × prix), puis **agréger** par catégorie : L1 et L3 donnent $2\times10+1\times10=30$ € pour la Décoration ; L2 donne $1\times30=30$ € pour la Maison ; L4 donne $3\times5=15$ € pour la Papeterie. L'opération clé est la **jointure** (sans elle, on ne connaît pas la catégorie des lignes). À relire : section 3.2.

**6.** Les commandes du Site en 2025 sont au nombre de 6 078 (colonne `Total`). Le tableau ci-dessus donne le nombre de commandes livrées à domicile ; la part s'obtient en divisant cette cellule par le total de la ligne `Site` :

```python
t = pd.crosstab(c25["canal"], c25["mode_livraison"])
print((t.loc["Site"] / t.loc["Site"].sum()).round(3).to_dict())
```
<!--sortie-->
```text
{'Domicile': 0.555, 'Point relais': 0.374, 'Retrait magasin': 0.071}
```

La part des commandes du Site livrée à domicile est de **55,5 %** environ, contre 37,4 % en point relais et 7,1 % en retrait en magasin. Notez qu'il faut diviser par le total de la **ligne** (le canal), pas par le total général ; ce sont deux proportions différentes. À relire : sections 2.2 (tableaux croisés) et 1.1.


**7.** La croissance sur deux ans est $1\,324\,764/1\,138\,932-1\approx16{,}3\ \%$. Le taux annuel moyen n'est **pas** la moitié de 16,3 % : chaque année s'applique au résultat de la précédente. On cherche $g$ tel que $(1+g)^2=1{,}163$, soit $g=\sqrt{1{,}163}-1\approx7{,}85\ \%$ par an (la moitié, 8,2 %, surestimerait). À relire : section 1.5 (taux de croissance).

```python
ca23, ca25 = 1_138_932, 1_324_764
print(round(100 * (ca25 / ca23 - 1), 1), "% en deux ans |", round(100 * ((ca25 / ca23) ** 0.5 - 1), 2), "% par an")
```
<!--sortie-->
```text
16.3 % en deux ans | 7.85 % par an
```

**8.** **Non, pas sans précaution.** Deux raisons. D'abord, seulement **24,7 %** des clients invités ont répondu (958 sur 3 875) : on ne sait rien des trois quarts restants. Ensuite, ceux qui répondent **ne ressemblent pas** à ceux qui ne répondent pas ; par exemple, les clients avec carte de fidélité y sont surreprésentés (35,6 % des invités, 40,1 % des répondants identifiés) :

```python
enq = lire("enquete_satisfaction")
clients = lire("clients")
inv = c25.drop_duplicates("id_client", keep="last").merge(clients[["id_client", "fidelite"]], on="id_client")
rep = enq.merge(clients[["id_client", "fidelite"]], on="id_client")
print("cartes parmi les invités :", round(100 * inv["fidelite"].mean(), 1), "% | parmi les répondants identifiés :", round(100 * rep["fidelite"].mean(), 1), "%")
print("réponses :", len(enq), "| invitations :", len(inv), "| notes 4 ou 5 :", round(100 * (enq["satisfaction_globale"] >= 4).mean(), 1), "%")
```
<!--sortie-->
```text
cartes parmi les invités : 35.6 % | parmi les répondants identifiés : 40.1 %
réponses : 958 | invitations : 3875 | notes 4 ou 5 : 55.2 %
```

Les 55 % décrivent **les répondants**, pas la clientèle ; on peut tout au plus dire « parmi les clients qui ont répondu, 55 % ont donné 4 ou 5 », et chercher comment corriger le biais de réponse. À relire : sections 1.3 (échantillonnage), 5.3 et 5.4 (enquêtes et biais).

> ✅ **À retenir.** Si vous avez répondu juste aux questions 1 à 3, les calculs de base (pourcentages, moyennes) sont en place. Les questions 4 à 6 testent la lecture et la manipulation de tableaux (filtrer, joindre, croiser) : les chapitres 2 à 4 s'en chargent. Les questions 7 et 8 testent le **raisonnement** (croissance, biais) : le chapitre 1 et le chapitre 5 les approfondissent.
