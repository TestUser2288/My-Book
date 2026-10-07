## 2.6 ➕ Pour aller plus loin : Google Sheets et Looker Studio

> 🧭 **Section complémentaire.** Beaucoup d'équipes travaillent dans le nuage plutôt que dans un fichier : **Google Sheets** pour le tableur, **Looker Studio** pour les tableaux de bord. Cette section en présente l'esprit, les fonctions qui n'existent pas dans Excel, et les équivalences avec ce que vous avez appris. **Rien ici n'a pu être exécuté** (nous n'avons pas de compte ni d'accès à ces services) : tous les exemples de formules sont **non exécutés** et à vérifier dans votre environnement ; nous recalculons en SQL ou en pandas les résultats qu'ils doivent donner.

```python hide
import os, sys, sqlite3, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import outils_ch02 as O

L, P, C = O.charger_2025()
```

### 2.6.1 Google Sheets : ce qui ressemble, ce qui diffère

Google Sheets reprend l'essentiel du vocabulaire d'Excel : cellules, plages, références relatives et absolues, tableaux croisés dynamiques, la plupart des fonctions de la section 2.1 (`SUM`, `SUMIFS`, `IF`, `VLOOKUP`, `XLOOKUP`, `FILTER`, `SORT`, `UNIQUE`…). Un classeur Excel s'importe, un classeur Sheets s'exporte au format `.xlsx`, avec des différences possibles sur les fonctions propres à chacun et la mise en forme. Dans l'interface en français, les noms de fonctions sont traduits comme dans Excel (avec quelques écarts : à vérifier).

Les différences qui comptent pour un analyste :

- **La collaboration en temps réel** est native : plusieurs personnes éditent le même document, avec commentaires, suggestions, historique des versions. C'est le grand avantage, et le risque (modifications non contrôlées : section 2.4).
- **Les formules sur toute une colonne** s'écrivent avec `ARRAYFORMULA` : `=ARRAYFORMULA(J2:J * K2:K * (1 - L2:L / 100))` applique le calcul à chaque ligne sans recopier la formule.
- **`QUERY`** interroge une plage avec un langage proche de SQL (voir ci-dessous) : c'est la fonction la plus puissante de Sheets, et elle n'a pas d'équivalent direct dans Excel.
- **`IMPORTRANGE`** lit une plage d'**un autre document** Sheets : `=IMPORTRANGE("adresse_du_document" ; "Lignes!A1:M")`, après autorisation d'accès. Pratique, mais fragile (le document source peut être déplacé, supprimé, ou son accès retiré).
- Des fonctions utiles propres à Sheets : `SPLIT` (découper un texte), `IMAGE`, `GOOGLEFINANCE` (cours de bourse), `REGEXEXTRACT` (expressions régulières).
- **La puissance de calcul est limitée** : un document Sheets accepte un nombre maximal de cellules (de l'ordre de dix millions, **à vérifier**), et devient lent bien avant. Pour des volumes importants, la même conclusion qu'avec Excel s'impose (2.5.4).
- L'automatisation se fait avec **Google Apps Script**, un langage dérivé de JavaScript, comparable aux macros VBA (non exécuté ici).

#### QUERY : du SQL dans une cellule

La fonction `QUERY(données ; requête ; en-têtes)` prend une plage et une requête écrite dans un petit langage inspiré de SQL. Les colonnes sont désignées par leur **lettre** (`Col1`, `Col2`… si la plage est une formule). Pour lister le chiffre d'affaires du Site par catégorie, du plus grand au plus petit :

```text
=QUERY(Lignes!A1:M ; "select I, sum(M) where E = 'Site' group by I order by sum(M) desc label sum(M) 'CA'" ; 1)
```

(Non exécuté ; `I` est la colonne `categorie`, `M` la colonne `montant`, `E` la colonne `canal`.) Cette requête est exactement une requête SQL de regroupement : `SELECT`, `WHERE`, `GROUP BY`, `ORDER BY`. Nous pouvons donc **vérifier le résultat attendu** en SQL, avec SQLite, sur les mêmes données.

```python
con = sqlite3.connect(":memory:")
L.to_sql("lignes", con, index=False)
req = "SELECT categorie, ROUND(SUM(montant), 2) AS CA FROM lignes WHERE canal = 'Site' GROUP BY categorie ORDER BY CA DESC"
res_sql = pd.read_sql(req, con)
print(res_sql.head(4).to_string(index=False))
```
<!--sortie-->
```text
 categorie        CA
    Jardin 166201.16
    Maison 140788.49
Décoration 118835.74
   Cuisine 109609.91
```

```python hide-code
tcd_site = L[L["canal"] == "Site"].groupby("categorie")["montant"].sum().round(2)
print("écart maximal entre la requête SQL et la colonne « Site » du tableau croisé de la section 2.2 :", round(float((res_sql.set_index("categorie")["CA"] - tcd_site).abs().max()), 6))
print("total des six catégories :", O.fr(float(res_sql["CA"].sum())))
```
<!--sortie-->
```text
écart maximal entre la requête SQL et la colonne « Site » du tableau croisé de la section 2.2 : 0.0
total des six catégories : 617 715,45
```

La requête SQL, et donc la fonction `QUERY` qui en est le miroir, donne le **Jardin en tête (166 201,16 €)**, devant la Maison (140 788,49 €), la Décoration (118 835,74 €) et la Cuisine (109 609,91 €). Elle retombe exactement sur la colonne « Site » du tableau croisé de la section 2.2, et le total des six catégories (617 715,45 €) est le chiffre d'affaires du Site. Apprendre SQL (chapitre 3) est donc aussi la meilleure façon d'apprendre `QUERY`.

### 2.6.2 Looker Studio : des tableaux de bord reliés à des sources

**Looker Studio** est un outil de tableaux de bord en ligne (anciennement « Data Studio »). Il ne stocke pas les données : il se **connecte** à des sources (feuilles Google Sheets, fichiers CSV, bases de données, services d'analyse du web…) et affiche des graphiques, des tableaux et des indicateurs qui se mettent à jour quand la source change. Trois notions suffisent pour démarrer :

- une **dimension** est un champ qui décrit (catégorie, canal, mois) ; une **métrique** est un champ que l'on agrège (montant, quantité). C'est la distinction « lignes et colonnes » contre « valeurs » d'un tableau croisé ;
- un **champ calculé** se définit par une formule sur les champs de la source : `SUM(montant) / COUNT_DISTINCT(id_commande)` donne le **panier moyen**, un ratio de sommes (2.2.4), dont nous avons calculé la valeur attendue en 2.5.2 : 102,33 € ;
- les **filtres** et **contrôles** (liste déroulante, sélecteur de dates) laissent le lecteur explorer le tableau de bord seul.

Les points de vigilance sont ceux de tout tableau de bord relié à des données vivantes. **La fraîcheur** : le tableau de bord peut afficher des données mises en cache (une actualisation manuelle ou programmée peut être nécessaire). **L'accès** : celui qui voit le tableau de bord voit-il les données de la source ? Les identifiants de connexion et les droits sont à régler. **La responsabilité** : si la source change (une colonne renommée), le tableau de bord casse, et le lecteur ne le sait pas toujours. **La confidentialité** : relier des données personnelles de clients à un service en ligne demande de savoir où elles sont hébergées et qui y a accès (volume II, chapitre complémentaire sur la confidentialité). Le volume IV de la série (visualisation et communication) reviendra sur la conception de tableaux de bord.

### 2.6.3 Tableau d'équivalences

Ce tableau rassemble les opérations du chapitre dans les cinq outils que vous rencontrerez. Il sert de **pense-bête** quand vous passez de l'un à l'autre.

| Opération | Excel | Google Sheets | SQL | pandas |
|---|---|---|---|---|
| Somme conditionnelle | `SOMME.SI.ENS` | `SUMIFS` | `SELECT SUM(…) … WHERE …` | `df.loc[cond, "col"].sum()` |
| Compter sous condition | `NB.SI.ENS` | `COUNTIFS` | `SELECT COUNT(*) … WHERE …` | `(cond).sum()` |
| Recherche | `RECHERCHEX` | `XLOOKUP`, `VLOOKUP` | `JOIN` | `merge` |
| Valeurs distinctes | `UNIQUE` | `UNIQUE` | `SELECT DISTINCT` | `drop_duplicates`, `unique` |
| Filtrer | `FILTRE` | `FILTER` | `WHERE` | masque booléen |
| Trier | `TRIER` | `SORT` | `ORDER BY` | `sort_values` |
| Regrouper et agréger | tableau croisé dynamique | tableau croisé, `QUERY` | `GROUP BY` | `groupby`, `pivot_table` |
| Requête dans une cellule | — | `QUERY` | — | — |
| Découper un texte | `FRACTIONNER.TEXTE`, assistant | `SPLIT` | `SUBSTR`, `INSTR` | `str.split` |
| Dépivoter | Power Query | formules, `QUERY` | `UNION ALL` | `melt` |
| Calcul sur toute une colonne | formule recopiée, tableaux dynamiques | `ARRAYFORMULA` | expression dans `SELECT` | vectorisation |

> ✅ **À retenir.**
> - **Google Sheets** ressemble à Excel pour les fonctions et les tableaux croisés ; il se distingue par la **collaboration**, `QUERY`, `IMPORTRANGE` et `ARRAYFORMULA`. Ses limites de volume sont les mêmes qu'Excel, en plus strictes.
> - **`QUERY` est du SQL** : le résultat attendu se vérifie par une requête SQL (ici, 617 715,45 € répartis sur 6 catégories, Jardin en tête).
> - **Looker Studio** relie des tableaux de bord à des sources vivantes : pensez **fraîcheur, droits d'accès, confidentialité**.
> - Un **tableau d'équivalences** entre Excel, Sheets, SQL et pandas évite de réapprendre chaque fois.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.8, exercice 2.12.
