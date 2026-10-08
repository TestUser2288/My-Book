# Introduction : un enseignement que personne ne comprend n'a aucune valeur

> « Une analyse juste que personne ne comprend est une analyse perdue. »

## Un résultat juste, trois présentations

Les trois volumes précédents vous ont appris à **trouver** des réponses : lire des données, les préparer, les analyser. Il reste l'étape que beaucoup oublient et qui décide de tout : **faire comprendre**. Un résultat reste sans effet tant que la personne qui doit décider ne l'a pas compris, ne s'en souvient pas ou n'y croit pas.

Un vendredi, la gérante vous écrit :

> « *Lundi, je décide si nous refaisons la promotion de janvier telle quelle. Qu'est-ce que je dois savoir ? Je n'aurai que dix minutes.* »

Vous avez fait l'analyse au volume III : sur les 153 jours de promotion de ces trois ans, la promotion a fait monter les commandes, mais baissé la marge. Reste à **montrer** ce résultat. Voici les quatre chiffres que vous avez en main.


```python
tableau = pd.DataFrame({"jours ordinaires": normal[["nb_commandes", "chiffre_affaires", "marge"]].mean(), "jours de promotion": promo[["nb_commandes", "chiffre_affaires", "marge"]].mean()}).round(1)
tableau.loc["marge par commande"] = [round(marge_ordre["normal"], 1), round(marge_ordre["promo"], 1)]
print(tableau)
```
<!--sortie-->
```text
                    jours ordinaires  jours de promotion
nb_commandes                    32.8                35.4
chiffre_affaires              3338.5              3300.1
marge                         1053.9               836.4
marge par commande              32.1                23.6
```

Ces quatre lignes disent tout, mais **ne disent rien à quelqu'un qui a dix minutes**. Il faut les comparer de tête, deviner lesquelles comptent, et deviner que l'écart de commandes (32,8 contre 35,4) est **sous-estimé** par la comparaison brute (la saison est creuse quand on fait des promotions : voir le volume III, chapitre 3). C'est la **première présentation** : le tableau brut. Le résultat est exact et ne sert à personne.

Deuxième présentation : vous faites un graphique, vite, dans le premier format venu.

Troisième présentation : vous partez de la **décision** (« refaire ou non ? ») et de ce que la gérante doit retenir (« plus de commandes, mais moins de marge »), et vous construisez le graphique et la phrase pour cela.


![Deux présentations du même résultat. À gauche, des barres dont l'axe commence à 32 commandes : la promotion semble quadrupler les ventes. À droite, la même analyse présentée à partir de la décision, avec un titre qui énonce la conclusion.](figures/ch00-trois-versions.png)

Regardez ce que chaque présentation fait faire à la gérante.

| Présentation | Ce qu'elle retient | Ce qu'elle décide |
|---|---|---|
| **1. Le tableau brut** | rien de précis : « les chiffres sont proches » | refaire comme chaque année, faute de signal |
| **2. Le graphique à axe tronqué** | la barre de la promotion est **4 fois plus haute** que l'autre, alors que l'écart réel n'est que de 7,8 % | prolonger la promotion : elle « quadruple les ventes » |
| **3. Le graphique construit pour décider** | « plus de commandes, mais moins de marge » | refaire la promotion **avec des remises moins fortes**, ou la tester |

Le résultat est le **même** dans les trois cas ; la décision, non. Le graphique de gauche n'est pas fautif par maladresse seule : un axe qui commence à 32 au lieu de 0 **fabrique** une impression (une promotion qui quadruple les ventes) que les données ne soutiennent pas. Celui de droite ne contient aucun artifice : un zéro au centre, des barres qui partent de ce zéro, des couleurs qui disent le signe de l'écart, un titre qui énonce la conclusion, des valeurs écrites. C'est tout le propos de ce volume : **la visualisation est un argument, et un argument se construit pour un lecteur**.

## Explorer ou expliquer

On fait des graphiques pour deux raisons très différentes, et le même graphique ne sert presque jamais les deux.

| | **Explorer** | **Expliquer** |
|---|---|---|
| **Pour qui ?** | vous | quelqu'un d'autre |
| **Question** | « Que contiennent ces données ? » | « Que dois-je retenir, et que décider ? » |
| **Quantité** | des dizaines de graphiques, vite faits | un ou deux, longuement soignés |
| **Soin** | aucun : des défauts, des axes automatiques | titre-conclusion, couleurs choisies, annotations |
| **Durée de vie** | quelques minutes | un rapport, une réunion, un tableau de bord |

Les volumes précédents (surtout le volume III, chapitre 1) ont enseigné l'**exploration**. Ce volume enseigne l'**explication** : choisir, **simplifier**, **mettre en page**, puis **raconter**. Le geste le plus important de l'explication est de **retirer** : retirer les graphiques qui ne servent pas la décision, les éléments qui encombrent, les chiffres que personne ne lira.

## Le lecteur et la décision d'abord

Avant de tracer quoi que ce soit, on répond à trois questions, dans cet ordre.

1. **Qui lit ?** La gérante n'a pas le même temps, la même culture statistique ni les mêmes inquiétudes que la responsable logistique ou qu'un comptable.
2. **Quelle décision cela doit-il éclairer ?** « Refaire la promotion ? », « changer de transporteur ? », « embaucher ? ». Un graphique sans décision en vue décore.
3. **Quelle est la seule chose à retenir ?** Si elle ne tient pas en une phrase, il y a **deux** graphiques, ou aucun.

La réponse à ces trois questions fixe presque tout le reste : le type de graphique (chapitre 1), l'outil, statique ou interactif (chapitres 2 et 3), la structure du récit (chapitre 4) et la manière de présenter (chapitre 5).

> 💡 **Intuition.** Un bon graphique est une phrase dessinée. Si vous ne pouvez pas dire la phrase, vous ne savez pas encore ce que le graphique doit montrer.

## De l'analyse à la décision : cinq maillons

Le travail de l'analyste est une chaîne. Un maillon faible suffit à perdre le résultat.


![La chaîne de l'analyse à la décision : analyse, figure, récit, présentation, décision. Les volumes précédents couvrent le premier maillon ; ce volume couvre les quatre suivants.](figures/ch00-chaine.png)

Les trois premiers maillons se préparent seul, devant un écran. Le quatrième, la **présentation**, se joue à plusieurs : on y découvre que la question posée n'était pas tout à fait celle qu'on croyait. D'où l'importance, en amont, du **recueil des besoins** (chapitre 5, section ➕ 5.3) : une grande partie des analyses ratées ne le sont pas par erreur de calcul, mais parce qu'elles répondent à une question que personne n'avait posée.

## Ne pas tromper

La visualisation a un pouvoir particulier : **un graphique se croit**. Un tableau de chiffres invite à lire ; un graphique donne une impression avant même qu'on le lise. Cette puissance impose trois règles que ce volume applique à chaque figure.

1. **Montrer ce que disent les données, pas ce que l'on souhaiterait.** Un axe tronqué, une échelle choisie pour faire monter une courbe, un titre qui affirme plus que la figure ne montre sont des **choix**, et des choix qui trompent (chapitre 1, section ➕ 1.4).
2. **Montrer l'incertitude.** Un chiffre sans intervalle ni contexte laisse croire à une précision qui n'existe pas ; le volume III l'a répété, il faut le **dessiner** (barres d'erreur, bandes, fourchettes).
3. **Dire ce que l'on ne sait pas.** Une annotation « hors période de promotion » ou « données incomplètes avant mars » est plus utile qu'une belle courbe muette.

Ces règles ne sont pas morales seulement : elles sont **pratiques**. Un décideur trompé une fois ne fait plus confiance à l'analyste, et la confiance est le capital de ce métier.

## Comment lire ce volume

Le volume compte cinq chapitres, tous autour de la même idée : **partir du lecteur et de la décision**.

| Chapitre | Question de fond | Ce que vous saurez faire |
|---|---|---|
| **1. Principes de visualisation** | « Quel graphique, et comment le rendre lisible ? » | choisir un type de graphique, simplifier, mettre en page ; ➕ couleurs et accessibilité, graphiques trompeurs |
| **2. Tableaux de bord** | « Comment suivre l'activité sans se noyer ? » | concevoir un tableau de bord pour ses utilisateurs ; situer Power BI, Tableau et leurs équivalents |
| **3. Visualisation avec Python** | « Comment produire ces figures de façon reproductible ? » | matplotlib, seaborn, plotly ; ➕ tableaux de bord Dash, Streamlit, Shiny ; ➕ cartes |
| **4. Storytelling et rapports** | « Comment raconter une analyse ? » | structurer un récit, rédiger un rapport ; ➕ synthèse d'une page, rapports automatisés |
| **5. Présenter à des non-techniciens** | « Comment faire adopter une recommandation ? » | comprendre son public, présenter ; ➕ recueil des besoins, compétences transversales |

Les chapitres se lisent dans l'ordre, les sections ➕ sont facultatives. Chaque chapitre s'ouvre sur une situation de la gérante et se termine sur un bilan ; les exercices et le projet du volume (un **tableau de bord** et une **courte présentation** pour un décideur) se trouvent dans le **cahier d'exercices**.

> 🧭 **Une remarque sur les outils.** Ce volume ne vous demande pas de maîtriser tous les outils cités. Les principes (chapitres 1, 4 et 5) valent pour n'importe lequel d'entre eux ; les outils du chapitre 3 sont ceux que le livre exécute. Les outils commerciaux de tableau de bord sont **décrits, non exécutés** (voir « Carte du volume, données et environnement »).

> ✅ **À retenir.** Une analyse n'a de valeur que si elle est **comprise** et **utilisée**. On part du **lecteur** et de la **décision**, on construit **un** message, on choisit la forme qui le porte, et l'on ne trompe jamais : ni par l'échelle, ni par le titre, ni par le silence sur l'incertitude.


# Carte du volume, données et environnement

Cette section ouvre le volume par cinq choses : la **carte des chapitres**, le **catalogue des jeux de données**, l'**environnement** nécessaire pour refaire les figures, la **politique de captures d'écran** et le **style visuel** du livre. Elle se lit en dix minutes et sert ensuite de référence.

## Carte du volume

Chaque chapitre répond à une situation de la gérante. Les cinq chapitres forment le parcours essentiel et se lisent dans l'ordre ; les sections marquées ➕ sont facultatives.

| Chapitre | Situation de départ | Contenu |
|---|---|---|
| **1. Principes de visualisation** | « Ce graphique ne dit rien : refais-le. » | choisir le bon graphique, clarté et mise en page ; ➕ couleurs, accessibilité, systèmes de design ; ➕ erreurs courantes et graphiques trompeurs |
| **2. Tableaux de bord** | « Je veux voir l'essentiel de la semaine sur une seule page. » | Power BI, Tableau (décrits, non exécutés), conception selon les besoins des utilisateurs ; ➕ Power BI avancé ; ➕ Looker, Metabase, Superset, Qlik |
| **3. Visualisation avec Python** | « Chaque lundi, je veux les mêmes figures, sans les refaire à la main. » | matplotlib et seaborn, plotly et l'interactif ; ➕ Dash, Streamlit, Shiny ; ➕ cartes |
| **4. Storytelling et rapports** | « Raconte-moi l'année en deux pages. » | structurer un récit, rédiger un rapport ; ➕ synthèse de direction, présentations ; ➕ rapports automatisés |
| **5. Présenter à des non-techniciens** | « Tu présentes ça au comité jeudi. » | comprendre son public, présenter résultats et recommandations ; ➕ recueil des besoins ; ➕ compétences transversales |
| **Projet du volume (cahier)** | « Un tableau de bord et dix minutes pour convaincre » | un tableau de bord et une courte présentation pour un décideur |

## Les jeux de données

Tout est **simulé**, avec des graines fixes. Le volume reprend **sans les modifier** les jeux du volume III (`build/donnees_a3.py`, lui-même construit sur la base de la boutique des volumes I et II) et y ajoute un seul fichier, `villes.csv`, produit par `build/donnees_a4.py`. Les analyses sont donc **déjà faites** : ici, on les **montre**. La docstring de `donnees_a3.py` donne la vérité programmée de chaque jeu.


| Fichier | Contenu | Lignes | Usage principal (indicatif) |
|---|---|---|---|
| `clients.csv` | clients (inscription, naissance, ville, canal d'acquisition, carte de fidélité) | 6 000 | chapitres 1 et 3 (cartes, répartitions) |
| `produits.csv` | catalogue (catégorie, prix, coût d'achat, fournisseur) | 120 | chapitres 1 et 3 |
| `commandes.csv` | une ligne par commande (date, client, canal, livraison, code promo) | 36 395 | chapitres 1 à 4 |
| `lignes_commande.csv` | une ligne par article de commande | 83 905 | chapitres 1 à 4 |
| `retours.csv` | lignes retournées | 5 002 | chapitre 1 |
| `jours_exploitation.csv` | une ligne par jour : commandes, chiffre d'affaires, météo, promotion, publicité | 1 096 | chapitres 1 à 4 (séries, promotion) |
| `jours_incidents.csv` | la même série avec des incidents injectés | 1 097 | chapitre 1 (annoter une anomalie) |
| `ab_email.csv`, `ab_site.csv` | deux tests A/B | 12 000 ; 38 622 | chapitres 1 et 4 (incertitude, résultat non significatif) |
| `sessions_web.csv` | sessions du site en 2025 : source, appareil, entonnoir | 127 022 | chapitres 2 et 3 (tableau de bord marketing) |
| `campagnes.csv` | dépenses publicitaires mensuelles par source | 36 | chapitres 2 et 4 |
| `budget_reel_2025.csv` | budget et réalisé par mois, catégorie et canal | 216 | chapitres 2 et 4 (écarts) |
| `benchmark_secteur.csv` | médiane et quartiles **fictifs** d'un secteur | 12 | chapitres 1 et 5 |
| `compte_resultat_mensuel.csv`, `bilan_annuel.csv` | comptes de la boutique | 36 ; 3 | chapitres 2 et 4 |
| `livraisons.csv` | livraisons des commandes Site et Réseaux | 19 420 | chapitres 1, 2 et 5 |
| `reappro_fournisseur.csv`, `stock_quotidien.csv` | achats et stocks | 1 500 ; 7 300 | chapitre 2 (tableau de bord d'exploitation) |
| `employes.csv`, `employes_annees.csv`, `departs.csv` | ressources humaines (petits effectifs) | 64 ; 245 ; 20 | chapitre 5 (sujets sensibles) |
| `villes.csv` | **nouveau** : 20 villes fictives, coordonnées dans un plan fictif, région fictive, habitants | 20 | chapitre 3 (cartes) |


### Le fichier des villes

`villes.csv` est le seul jeu nouveau. Il sert aux cartes de la section ➕ 3.4, **sans aucune géographie réelle** : les villes sont posées dans un **plan fictif** de 120 km sur 90 km, mesuré par deux coordonnées `x_km` et `y_km`.

```python
print(tables["villes"].head(4).to_string(index=False))
```
<!--sortie-->
```text
  ville  x_km  y_km   region  habitants
Ville A  10.1   4.6 Région 1      43700
Ville B  32.5  20.3 Région 1     170000
Ville C  57.9   7.7 Région 3      11300
Ville D  84.5   7.3 Région 3      17000
```

Les habitants et les régions sont inventés ; les villes sont les mêmes que celles de la colonne `ville` des clients. Il n'y a **ni fond de carte du monde réel, ni tuiles téléchargées** : une carte est ici un nuage de points, de cercles proportionnels et de polygones calculés (section ➕ 3.4).

## Les fichiers de vérité

Les jeux du volume III embarquent leur vérité programmée dans la docstring de `donnees_a3.py` et, pour les incidents, dans `verite_incidents.csv`. Ce volume en fait un usage particulier : **un graphique peut être jugé par rapport à ce qu'il aurait dû montrer**. Quand un exemple compare un bon et un mauvais graphique des mêmes données, la vérité sert à dire lequel est fidèle.

## Régénérer les données

Les données se régénèrent en quelques secondes (`python build/donnees_a4.py`) et sont identiques à chaque fois (graines fixes). Il faut le lancer depuis le dossier du volume.

```bash
python build/donnees_a4.py        # réécrit donnees/*.csv (jeux du volume III + villes.csv)
```

## L'environnement

Le volume utilise les outils des volumes précédents, plus ceux de la visualisation. Voici ce qui sert à quoi.

| Besoin | Outil | Chapitres |
|---|---|---|
| Manipuler les données | **pandas**, SQL (SQLite, DuckDB) | tous |
| Figures statiques | **matplotlib** (style du livre), **seaborn** | 1, 3, 4 |
| Figures interactives | **plotly** (HTML), photographié avec un navigateur sans interface | 3 |
| Tableaux de bord programmés | **Dash**, **Streamlit** (Python), **Shiny** (R) | 3 |
| Graphiques en R | **ggplot2** (blocs `r`, quand utile) | 1, 3 |
| Tableur | Excel (non installé ici), **LibreOffice Calc** pour recalculer des formules | 2 |
| Outils de BI commerciaux | Power BI, Tableau, Looker, Qlik : **décrits, non exécutés** | 2 |
| Outils de BI libres | Metabase, Superset : **décrits, non exécutés** | 2 |

```python
from importlib.metadata import version
print({p: version(p) for p in ["pandas", "matplotlib", "seaborn", "plotly", "dash", "streamlit"]})
```
<!--sortie-->
```text
{'pandas': '3.0.6', 'matplotlib': '3.11.2', 'seaborn': '0.13.2', 'plotly': '7.1.0', 'dash': '4.4.1', 'streamlit': '1.65.0'}
```

```r
cat(R.version.string, "| ggplot2", as.character(packageVersion("ggplot2")), "| shiny", as.character(packageVersion("shiny")), "\n")
```
<!--sortie-->
```text
R version 4.4.3 (2025-02-28) | ggplot2 3.5.1 | shiny 1.10.0 
```

Les versions exactes importent peu : elles sont données pour que les chiffres et les figures du livre soient reproductibles.

## Les captures d'écran : ce que ce livre montre, et ce qu'il ne montre pas

Ce livre parle d'outils, mais il ne **reproduit aucune interface de produit commercial**. Voici la règle suivie, parce qu'elle importe pour la confiance que vous pouvez accorder aux figures.

- **Les figures de graphiques** sont produites par le code du livre : ce sont de vrais résultats, reproductibles.
- **Les outils libres que l'on exécute ici** (Dash, Streamlit, Shiny, plotly) sont photographiés pour de vrai, avec un navigateur sans interface : ce sont de **vraies captures** de ce qu'ils affichent.
- **Les outils commerciaux** (Power BI, Tableau, Looker, Qlik) ne sont **pas installés** sur la machine qui produit le livre et leurs écrans sont protégés : on les **décrit**, on explique leurs notions (modèle de données, visuel, filtre, publication) avec la mention « non exécuté », et l'on montre des **maquettes dessinées** (rectangles génériques, sans logo ni identité de produit) pour situer les zones d'un tableau de bord. Leurs menus changent d'une version à l'autre : *à vérifier dans la documentation de votre version*.
- **Les images d'Internet** ne sont utilisées que si leur licence autorise la réutilisation, avec crédit et source dans la légende ; ce volume n'en utilise pas dans cette section.

> 🧭 **Pourquoi ne pas simplement copier une capture ?** Parce que l'on ne peut pas redistribuer librement les écrans d'un produit commercial, et parce qu'une capture vieillit vite. Une maquette honnête et une explication des **concepts** durent plus longtemps que l'aspect d'une interface.

## Le style visuel du livre

Toutes les figures du livre partagent un style, défini dans `build/style.py`. Il obéit à quatre choix, qui sont **les principes du chapitre 1 mis en pratique**.

1. **Un fond clair et neutre**, des **grilles discrètes** : le contenu passe avant le décor.
2. **Une palette courte, dans un ordre fixe** (bleu, orange, aqua, violet, rouge) : la même couleur désigne la même chose d'un graphique à l'autre ; on n'en utilise **jamais plus qu'on ne peut nommer**.
3. **Des étiquettes écrites sur les données** plutôt qu'une légende à décoder, chaque fois que c'est possible.
4. **Une police sans empattement** (DejaVu Sans), lisible à toutes les tailles.

La question du contraste est mesurable : le **rapport de contraste** entre une couleur et son fond se calcule (formule de luminance relative des recommandations d'accessibilité du web) et les recommandations demandent au moins **4,5 : 1** pour un texte courant et **3 : 1** pour des éléments graphiques.


![Les couleurs de la palette du livre avec leur rapport de contraste calculé sur le fond. Seul l'aqua n'atteint pas le seuil de 3 : 1 recommandé pour des éléments graphiques.](figures/ch00-palette.png)

On lit un résultat **honnête** : le bleu (4,3 : 1), l'orange (3,1 : 1) et le rouge (3,9 : 1) dépassent le seuil de 3 : 1 pour des éléments graphiques, le violet et l'encre le dépassent largement, et le **gris secondaire** (3,5 : 1) convient à des éléments, **pas à un texte courant**. L'**aqua** (2,7 : 1) **n'atteint pas** le seuil : la palette l'utilise pour des surfaces et des courbes épaisses, **toujours doublées d'une étiquette ou d'une forme**, jamais seul. La règle dont dépend l'accessibilité (chapitre 1, section ➕ 1.3) est précisément celle-là : **ne jamais faire porter l'information par la couleur seule**.

## Conventions

- **Monnaie et noms** : les montants sont en euros, les villes s'appellent « Ville A » à « Ville T », les régions « Région 1 » à « Région 4 », les noms de personnes n'existent pas (on parle de « la gérante », « la responsable logistique », par leur fonction) ; la TVA est fictive (20 %).
- **Dates** : on analyse l'année 2025 (et 2023–2024 pour les tendances), la photographie étant prise au 31 décembre 2025.
- **Graines** : toute simulation fixe sa graine, pour que les résultats se reproduisent.
- **Figures** : chaque figure du livre a une légende qui dit **ce qu'il faut y lire**, et un texte alternatif implicite : la phrase qui l'accompagne énonce son message.
- **Vérité programmée** : quand elle existe, elle est révélée **après** l'analyse.

> ✅ **À retenir.** Les données sont fictives, propres, et leur vérité est connue : elles servent à apprendre à **montrer** une analyse, pas à la faire. Le livre ne montre que ce qu'il exécute ou qu'il dessine honnêtement, et il applique à ses propres figures les principes qu'il enseigne.
