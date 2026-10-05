## 4.7 ➕ Pour aller plus loin : d'autres langages (SAS, MATLAB, Julia)

> 🧭 **Section optionnelle.** Python et R vous couvriront dans la grande majorité des cas. Mais vous croiserez peut-être, dans une offre d'emploi, un stage ou le code d'un collègue, **SAS**, **MATLAB** ou **Julia**. Cette section ne vous apprend pas ces langages : elle vous donne le **vocabulaire** pour les lire sans panique, en refaisant *la même petite analyse* dans chacun.

> ⚠️ **Honnêteté sur ce qui a été exécuté.** Python et R sont installés sur la machine qui a produit ce livre : leurs sorties ci-dessous sont **réelles**. SAS, MATLAB et Julia ne le sont pas : leurs blocs de code sont marqués « **non exécuté** » et ne sont accompagnés d'aucune sortie. Ils sont écrits à partir de leur documentation, avec les conventions habituelles de chaque langage ; **vérifiez-les chez vous** avant de les utiliser dans un travail important. Le résultat attendu est celui de Python et R (section 3.1 : il est le même partout, car le calcul est le même).

### 4.7.1 La tâche : un résumé par canal

La gérante demande : *« Pour chaque canal de vente, combien de commandes, quel montant moyen, et quel écart-type ? »* C'est le calcul du 3.1, appliqué au fichier `donnees/commandes.csv` : lire, regrouper, résumer. Cinq lignes dans chaque langage.

**En Python** (pandas, section 4.4) :

```python
import pandas as pd

commandes = pd.read_csv("donnees/commandes.csv")
resume = (commandes.groupby("canal")["montant"]
          .agg(n="count", moyenne="mean", ecart_type="std")
          .round(1))
print(resume)
```
<!--sortie-->
```text
             n  moyenne  ecart_type
canal                              
Boutique   114     74.8        40.6
Réseaux  138     49.0        31.1
Site       148     59.5        38.3
```

**En R** (le même calcul avec le paquet `dplyr`, section 4.2) :

```r
suppressPackageStartupMessages(library(dplyr))

commandes <- read.csv("donnees/commandes.csv")
commandes |>
  group_by(canal) |>
  summarise(n = n(), moyenne = round(mean(montant), 1), ecart_type = round(sd(montant), 1))
```
<!--sortie-->
```text
# A tibble: 3 × 4
  canal         n moyenne ecart_type
  <chr>     <int>   <dbl>      <dbl>
1 Boutique    114    74.8       40.6
2 Réseaux   138    49         31.1
3 Site        148    59.5       38.3
```

Les deux langages donnent exactement les mêmes nombres : 114 commandes en boutique pour un montant moyen d'environ 75 €, comme au 3.1. (Le tri alphabétique des canaux est le même ; seule la présentation du tableau diffère.)

### 4.7.2 SAS : le langage des grandes organisations

> 💡 **Intuition.** **SAS** (*Statistical Analysis System*) est un logiciel commercial né dans les années 1970. Il est resté très présent dans les **banques, les assurances, l'industrie pharmaceutique et les administrations**, où l'on valorise la stabilité, la traçabilité et le fait que les résultats d'un programme écrit il y a vingt ans soient toujours identiques. C'est souvent le cas dans les métiers de l'actuariat et du risque (le thème du volume V de cette série). Pour vous former gratuitement, SAS propose une version en ligne destinée à l'enseignement (*SAS OnDemand for Academics*).

Un programme SAS est une suite d'**étapes** : les étapes `DATA` fabriquent ou transforment des tables, les étapes `PROC` (procédures) appliquent un traitement statistique prêt à l'emploi. Chaque instruction se termine par un point-virgule, et un bloc par `run;`.

```sas noexec
/* SAS — non exécuté dans ce livre */
proc import datafile="donnees/commandes.csv"
            out=commandes dbms=csv replace;
    guessingrows=max;
run;

proc means data=commandes n mean std maxdec=1;
    class canal;          /* un résumé par canal */
    var montant;          /* la variable à résumer */
run;
```

On lit : « importer le CSV dans une table `commandes` » puis « *procédure MEANS* : pour chaque `canal` (`class`), donner l'effectif (`n`), la moyenne et l'écart-type de `montant` ». Aucune boucle explicite : SAS parcourt lui-même les lignes.

### 4.7.3 MATLAB : le calcul numérique des ingénieurs

> 💡 **Intuition.** **MATLAB** (*Matrix Laboratory*) est un environnement commercial centré sur les **matrices**, très utilisé en ingénierie, en traitement du signal et en automatique, souvent enseigné dans les écoles d'ingénieurs. Tout y est une matrice, même un nombre seul (une matrice $1\times1$). Si vous avez aimé le chapitre 1 (algèbre linéaire), vous serez chez vous. Une alternative libre, **GNU Octave**, exécute une grande partie du même code.

Deux particularités à connaître : les indices **commencent à 1**, et les fichiers de données se lisent dans une `table`.

```matlab noexec
% MATLAB — non exécuté dans ce livre
T = readtable("donnees/commandes.csv");

G = groupsummary(T, "canal", ["mean" "std"], "montant");
disp(G)
```

`groupsummary` regroupe les lignes par `canal` et calcule la moyenne et l'écart-type de `montant`. Le résultat est une nouvelle table avec les colonnes `mean_montant` et `std_montant`.

### 4.7.4 Julia : la promesse « rapide comme C, simple comme Python »

> 💡 **Intuition.** **Julia** (libre, créé en 2012) vise un compromis : une syntaxe lisible proche de Python et de MATLAB, mais un code **compilé à la volée** presque aussi rapide qu'un programme en C. Il est apprécié pour le calcul scientifique, les simulations lourdes et l'optimisation. Son écosystème de science des données est plus jeune que celui de Python ; une particularité est le temps d'attente à la première exécution (la compilation).

```julia noexec
# Julia — non exécuté dans ce livre
using CSV, DataFrames, Statistics

commandes = CSV.read("donnees/commandes.csv", DataFrame)

resume = combine(groupby(commandes, :canal),
                 nrow => :n,
                 :montant => mean => :moyenne,
                 :montant => std => :ecart_type)
println(resume)
```

On retrouve la logique de pandas : `groupby` puis `combine` (on lit `colonne => fonction => nom_du_résultat`). Les colonnes se désignent par des *symboles* (`:canal`).

### 4.7.5 Le même calcul, vu de près : un dictionnaire de traduction

Voici de quoi passer d'un langage à l'autre. (Les cases SAS, MATLAB et Julia sont **non exécutées**, comme les blocs ci-dessus.)

| Idée | Python | R | MATLAB | Julia | SAS |
|---|---|---|---|---|---|
| Affecter | `x = 5` | `x <- 5` | `x = 5;` | `x = 5` | `x = 5;` (étape DATA) |
| Premier élément d'une liste | `x[0]` | `x[1]` | `x(1)` | `x[1]` | — |
| Moyenne | `np.mean(x)` | `mean(x)` | `mean(x)` | `mean(x)` | `proc means` |
| Écart-type | `np.std(x, ddof=1)` | `sd(x)` | `std(x)` | `std(x)` | `proc means std` |
| Lire un CSV | `pd.read_csv(f)` | `read.csv(f)` | `readtable(f)` | `CSV.read(f, DataFrame)` | `proc import` |
| Résumé par groupe | `groupby().agg()` | `group_by()` puis `summarise()` | `groupsummary` | `proc means; class` |
| Blocs | indentation | `{ }` | `end` | `end` | `run;` |

> ⚠️ **Le piège des indices : 0 ou 1 ?** Python (comme C, Java) compte à partir de **0** ; R, MATLAB et Julia à partir de **1**. De plus, les *tranches* ne se comportent pas pareil, et l'indice négatif signifie des choses opposées. Voyez la différence entre Python et R, tous les deux exécutés :

```python
x = [10, 20, 30, 40, 50]
print("x[0]    =", x[0])
print("x[0:2]  =", x[0:2], "  (la borne de droite est exclue)")
print("x[-1]   =", x[-1], "  (le dernier élément)")
```
<!--sortie-->
```text
x[0]    = 10
x[0:2]  = [10, 20]   (la borne de droite est exclue)
x[-1]   = 50   (le dernier élément)
```

```r
x <- c(10, 20, 30, 40, 50)
cat("x[1]    =", x[1], "\n")
cat("x[1:2]  =", x[1:2], "  (la borne de droite est incluse)\n")
cat("x[-1]   =", x[-1], "  (tout sauf le premier élément !)\n")
```
<!--sortie-->
```text
x[1]    = 10 
x[1:2]  = 10 20   (la borne de droite est incluse)
x[-1]   = 20 30 40 50   (tout sauf le premier élément !)
```

Même symbole `x[-1]`, **deux sens opposés** : le dernier élément en Python, « tout sauf le premier » en R. Si vous traduisez du code d'un langage à l'autre, c'est la première chose à vérifier.

> 📐 **Un point commun rassurant : $n-1$.** Les écarts-types par défaut de pandas, R (`sd`), MATLAB (`std`) et Julia (`std`) divisent par $n-1$ (l'estimateur sans biais démontré au 3.2) ; seul `np.std` de NumPy divise par $n$ si on ne précise pas `ddof=1`. Même formule, mêmes nombres : le fait que vos résultats concordent d'un langage à l'autre est d'ailleurs une excellente manière de **vérifier** un calcul.

### 4.7.6 Alors, lequel choisir ?

| Langage | Atouts | Limites | À privilégier si… |
|---|---|---|---|
| **Python** | généraliste, immense écosystème, apprentissage automatique, mise en production | graphiques statistiques moins « clés en main » que R | vous voulez **un seul langage** pour tout (ce livre) |
| **R** | statistique de référence, `ggplot2`, rapports reproductibles | moins à l'aise pour le développement logiciel | votre travail est surtout statistique ou académique |
| **SAS** | stabilité, validation réglementaire, très robuste sur de gros fichiers | licence payante, communauté plus fermée | votre employeur (banque, assurance, pharma) l'impose |
| **MATLAB** | calcul matriciel, boîtes à outils d'ingénierie | licence payante, moins utilisé en science des données | vous venez de l'ingénierie ou du signal |
| **Julia** | très rapide, syntaxe claire, calcul scientifique | écosystème plus jeune, compilation au premier appel | vous faites des **simulations lourdes** ou de l'optimisation |

> 💡 **Le conseil pratique.** On n'apprend pas un langage par collection, on l'apprend par **projet**. Maîtrisez Python (et un peu de R pour lire du code de statisticien). Le jour où un poste exige SAS, MATLAB ou Julia, la bonne nouvelle est que *les idées sont les mêmes* : tableau, regroupement, résumé, graphique. Il ne reste qu'à apprendre la syntaxe, avec ce dictionnaire sous la main. Regardez les offres d'emploi de votre domaine et de votre pays pour savoir quels langages y sont demandés avant d'investir du temps.

> ✅ **À retenir (autres langages).**
>
> - **SAS** : étapes `DATA` et `PROC`, point-virgule partout, très répandu en banque, assurance et pharma ; version d'apprentissage gratuite en ligne.
> - **MATLAB** : tout est matrice, indices à partir de 1 ; **Octave** en est une alternative libre.
> - **Julia** : rapide et lisible, compilé à la volée ; écosystème plus jeune.
> - Python et R ont été exécutés ici ; **SAS, MATLAB et Julia ne l'ont pas été** (blocs « non exécuté »).
> - Pièges de traduction : indices à partir de 0 ou de 1, signification de `x[-1]`, bornes des tranches ; l'écart-type par défaut divise par $n-1$ presque partout.
> - Quel que soit le langage, le raisonnement est le même : **lire → regrouper → résumer → vérifier**.
