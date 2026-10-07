# Chapitre 1 : Analyse exploratoire des données

> « Avant de chercher pourquoi, regardez à quoi ça ressemble. »

La gérante passe la tête dans la porte de votre bureau, une tasse de café à la main :

— Avant de me dire *pourquoi* les ventes bougent, dis-moi à quoi elles **ressemblent**. Je ne sais même pas ce qu'est une journée normale, chez nous.

Vous aviez prévu de lancer un modèle, un test, une régression. Elle a raison de vous arrêter : on ne choisit pas une méthode d'analyse avant d'avoir **regardé** les données. Les volumes précédents vous ont appris à les lire (volume I), puis à les rendre fiables (volume II). Ce chapitre ouvre le volume III par l'étape que tous les analystes expérimentés font en premier, et qu'ils ne sautent jamais : l'**analyse exploratoire des données**, ou *EDA* (*exploratory data analysis*).

L'exploration n'a pas pour but de **prouver** quelque chose. Elle sert à quatre choses, et seulement à celles-là :

1. **Comprendre la forme** de chaque variable (où se trouve le centre, jusqu'où va la queue, combien de modalités) pour savoir quels résumés ont un sens ;
2. **Repérer les relations** entre variables, pour formuler des questions précises que les chapitres suivants testeront ;
3. **Découvrir les surprises** : des motifs que l'on attendait (la saison, le week-end) et des anomalies que l'on n'attendait pas (une panne, une erreur de saisie) ;
4. **Décider** de la suite : quelle méthode, sur quelles données, avec quelles précautions.

Une exploration réussie se reconnaît à un livrable simple : une page où l'on peut écrire, pour chaque variable importante, **une phrase** qui la décrit et **une action** qu'elle entraîne.

## Le chemin de ce chapitre

Le **parcours essentiel** compte trois sections, qui vont de la plus simple des questions à la plus fine :

- **1.1 Analyse univariée** : *à quoi ressemble chaque variable, prise seule ?* Les histogrammes et leurs classes, la boîte à moustaches, les quantiles, l'échelle logarithmique ; les barres ordonnées pour les catégories ; la série dans le temps. Trois pièges de lecture.
- **1.2 Analyse bivariée et multivariée** : *comment deux variables, puis trois, varient-elles ensemble ?* Nuages et lissage, comparaisons de groupes, tableaux croisés, matrice de corrélation, et un phénomène qui fait peur à tous les analystes : le **paradoxe de Simpson**, que nous retrouverons dans les vraies données de la boutique.
- **1.3 Repérer les motifs et les anomalies** : *qu'est-ce qui est régulier, qu'est-ce qui sort du lot ?* Jour de la semaine, saison, changement de niveau ; puis une méthode simple et robuste pour détecter des **incidents** dans les ventes, évaluée contre la vérité programmée. Une anomalie n'est pas une erreur, et une erreur n'est pas un événement : la différence décide de ce que l'on fait.

Une section facultative (➕) complète le tout : **1.4 Une liste de contrôle EDA réutilisable**, avec une fonction qui produit automatiquement un premier rapport d'exploration sur n'importe quel tableau.

> 🧭 **Comment lire ce chapitre.** Chaque section part d'une **question** de la gérante, regarde les **données** de la boutique, et finit par **ce que l'on peut dire** (et ce que l'on ne peut pas dire). Le code est court : l'essentiel est de savoir **quoi regarder**, pas de savoir écrire le graphique. Les figures sont produites par du code caché, que vous retrouverez dans le cahier. Ce chapitre suppose le volume I (statistique descriptive : médiane, quartiles, écart-type, section 1.1 ; corrélation, section 1.4) et le volume II (données propres).

## Les données du chapitre

> 📦 **Les données.** Tout le volume s'appuie sur les données **simulées** de la boutique (le générateur est dans `build/donnees_a3.py`) :
>
> - `commandes.csv` et `lignes_commande.csv` : 36 395 commandes et 83 905 lignes entre janvier 2023 et décembre 2025 ;
> - `clients.csv`, `produits.csv` (120 produits, 6 catégories) et `retours.csv` ;
> - `jours_exploitation.csv` : une ligne par jour (commandes, chiffre d'affaires, température, pluie, promotion, dépense publicitaire) ;
> - `livraisons.csv` : les commandes livrées (Site et Réseaux), avec le transporteur et les dates ;
> - `jours_incidents.csv` : les mêmes jours d'exploitation, mais avec **des incidents injectés**, dont la liste exacte est dans `verite_incidents.csv`. Nous n'ouvrirons ce dernier fichier qu'à la fin de la section 1.3, comme on ouvre une correction.
>
> Comme les données sont fabriquées, nous connaissons la **vérité** qui les a générées ; nous la révélerons quand elle est instructive.

On commence par charger les tableaux. Une commande est composée d'une ou plusieurs **lignes** ; son **panier** est la somme de ses lignes.

```python
import sys, warnings
sys.path.insert(0, "build")
warnings.filterwarnings("ignore")
import numpy as np, pandas as pd
import outils_ch01 as O

donnees = O.charger()
cmd, lig, prod, ret, j, cli, liv, ji, vi = (donnees[k] for k in ["cmd", "lig", "prod", "ret", "j", "cli", "liv", "ji", "vi"])
print(len(cmd), "commandes,", len(lig), "lignes,", len(prod), "produits,", len(cli), "clients,", len(j), "jours")
print(cmd[["id_commande", "date_commande", "canal", "mode_livraison", "code_promo", "panier"]].head(3).to_string(index=False))
```
<!--sortie-->
```text
36395 commandes, 83905 lignes, 120 produits, 6000 clients, 1096 jours
 id_commande date_commande    canal  mode_livraison code_promo  panier
           1    2023-01-01     Site        Domicile               83.8
           2    2023-01-01 Boutique Retrait magasin               80.7
           3    2023-01-01 Boutique Retrait magasin               60.8
```

Avant de calculer quoi que ce soit, on se pose la question que se pose tout bon analyste devant un tableau : **que représente une ligne, et quelles sont les colonnes ?** Ici, une ligne de `cmd` est une commande, une ligne de `j` est un jour, une ligne de `liv` est une livraison. Nous verrons au fil du chapitre que choisir le bon tableau, c'est déjà choisir la bonne question.


## 1.1 Analyse univariée

> **La question de la gérante.** « Le panier moyen est de 100 €. Mais est-ce que *tous* mes paniers ressemblent à ça ? »

L'analyse **univariée** regarde **une variable à la fois**. C'est la première étape de toute exploration, et la plus souvent bâclée : on se précipite sur les relations entre variables avant d'avoir compris chacune d'elles. Or une variable mal comprise fausse tout le reste. Une moyenne calculée sur une distribution très asymétrique, une catégorie rare traitée comme les autres, une série dont on n'a pas regardé la saison : ces erreurs se paient plus tard, dans les modèles.

La méthode est toujours la même et tient en trois gestes : **résumer** par quelques nombres, **dessiner** la répartition, **écrire une phrase** qui dit ce que l'on a vu. Le type de la variable décide du résumé et du dessin.

| Type de variable | Exemple dans la boutique | Résumés | Dessins |
|---|---|---|---|
| Quantitative continue | panier d'une commande (€) | médiane, quartiles, moyenne, écart-type, asymétrie | histogramme, boîte à moustaches |
| Quantitative discrète | délai de livraison (jours) | fréquences de chaque valeur, médiane, centiles | diagramme en bâtons |
| Qualitative | canal, code promo, motif de retour | fréquences, part de la modalité principale | barres ordonnées |
| Temporelle | chiffre d'affaires par mois | niveau, tendance, saison | courbe |

### 1.1.1 Une variable quantitative : le panier

Commençons par le panier des 36 395 commandes. Le volume I a présenté les résumés (centre, dispersion, forme) ; on les regroupe ici en un seul coup d'œil.

```python
x = cmd["panier"]
print("quantiles (€) :", x.quantile([0.01, 0.05, 0.25, 0.5, 0.75, 0.95, 0.99]).round(1).to_dict())
print("moyenne", round(x.mean(), 1), "| écart-type", round(x.std(), 1), "| asymétrie", round(x.skew(), 2), "| minimum", x.min(), "| maximum", x.max())
print("part des commandes sous la moyenne :", round((x < x.mean()).mean() * 100, 1), "%")
print("part des paniers à moins d'un écart-type de la moyenne :", round(((x - x.mean()).abs() < x.std()).mean() * 100, 1), "%")
```
<!--sortie-->
```text
quantiles (€) : {0.01: 4.0, 0.05: 13.9, 0.25: 42.9, 0.5: 79.8, 0.75: 135.4, 0.95: 254.5, 0.99: 383.7}
moyenne 100.4 | écart-type 80.7 | asymétrie 1.85 | minimum 2.32 | maximum 987.9
part des commandes sous la moyenne : 60.8 %
part des paniers à moins d'un écart-type de la moyenne : 78.2 %
```

La médiane (79,8 €) est nettement sous la moyenne (100,4 €) : **six commandes sur dix valent moins que la moyenne**. Le 99ᵉ centile est à 383,7 €, soit près de quatre fois la moyenne, et le maximum à 987,9 €. L'asymétrie de 1,85 confirme ce que ces chiffres suggéraient : une distribution étalée **vers la droite**, avec beaucoup de petits paniers et quelques gros. Dessinons-la.


![Le panier de 36 395 commandes : histogramme à l'échelle ordinaire (avec moyenne et médiane), histogramme à l'échelle logarithmique, boîte à moustaches.](figures/ch01-panier.png)

Trois lectures du même panier, chacune répond à une question différente :

- **L'histogramme ordinaire** (à gauche) montre la forme : un pic vers 30 à 60 €, puis une longue queue. La moyenne (trait plein) est tirée vers la droite par la queue, la médiane (trait pointillé) reste au pied du pic.
- **L'échelle logarithmique** (au milieu) étire les petits montants et comprime les grands. Chaque graduation multiplie par deux ou par cinq au lieu d'ajouter une quantité fixe. La forme devient presque une cloche : c'est le signe que les paniers se comportent par **multiples** plus que par **ajouts**. Elle montre aussi ce que l'échelle ordinaire cachait : un petit bloc de paniers de quelques euros, à gauche (les commandes d'un seul petit article).
- **La boîte à moustaches** (à droite) résume la distribution en cinq nombres : la boîte va du premier au troisième quartile (42,9 € à 135,4 €), le trait orange est la médiane, les moustaches s'étendent jusqu'aux valeurs les plus éloignées qui ne sont pas jugées extrêmes. Elle ne montre pas la forme, mais elle permet de **comparer** facilement plusieurs groupes côte à côte, ce que l'on fera en 1.2.

```python
lx = np.log(x)
print("asymétrie du panier :", round(x.skew(), 2), "| asymétrie du logarithme :", round(lx.skew(), 2))
print("rapport entre le centile 99 et la médiane :", round(x.quantile(0.99) / x.median(), 1))
```
<!--sortie-->
```text
asymétrie du panier : 1.85 | asymétrie du logarithme : -0.71
rapport entre le centile 99 et la médiane : 4.8
```

> 💡 **Quand passer au logarithme ?** Quand la variable est positive, très asymétrique à droite, et que **les écarts relatifs** (« deux fois plus ») ont plus de sens que les écarts absolus (« 50 € de plus »). C'est le cas des montants, des durées, des tailles. Le logarithme ne change pas les données, seulement l'échelle de lecture. Ici, il ramène l'asymétrie de 1,85 à −0,71 : la queue a disparu, remplacée par une légère traîne à gauche (les petits paniers). Les modèles du chapitre 3 en tireront parti.

> ⚠️ **Piège : l'écart-type d'une variable asymétrique.** L'écart-type du panier (80,7 €) est presque égal à sa moyenne (100,4 €). Pour une cloche, 68 % des valeurs seraient à moins d'un écart-type de la moyenne, donc entre 20 € et 181 €. Ici, 78,2 % des paniers s'y trouvent : la règle ne tient pas, puisque la distribution n'a pas la forme d'une cloche. Pour décrire la dispersion d'une variable asymétrique, **préférez les quartiles et les centiles**, qui ne supposent aucune forme.

### 1.1.2 Choisir les classes d'un histogramme

Un histogramme dépend d'un choix que beaucoup d'analystes font sans y penser : le **nombre de classes**. Trop peu, et l'on aplatit la forme ; trop, et l'on dessine du bruit.

```python
for regle in ["sturges", "fd"]:
    print(f"règle de {regle} : {len(np.histogram_bin_edges(x, bins=regle)) - 1} classes")
```
<!--sortie-->
```text
règle de sturges : 17 classes
règle de fd : 177 classes
```

La règle de **Sturges** (qui ne dépend que du nombre d'observations) propose 17 classes. La règle de **Freedman-Diaconis** (qui tient compte de la dispersion) en propose 177 : elle trouve que, avec 36 395 observations, on peut se permettre un dessin très fin. Voici trois choix côte à côte.


![Le même panier avec 5, 17 et 177 classes.](figures/ch01-classes.png)

Avec **5 classes**, l'histogramme est lisible mais trompeur : la première classe (0 à 200 €) concentre presque tout, on ne voit plus le pic. Avec **177 classes**, on voit le pic et la queue, mais aussi des irrégularités qui ne sont que du hasard d'échantillonnage. Les **17 classes** sont un bon compromis pour une présentation. Pour une exploration, **essayez deux ou trois valeurs** et gardez le dessin qui montre la forme sans les dents de scie. La règle n'est pas sacrée : elle sert à ne pas partir d'un mauvais choix.

> 🧭 **En pratique.** Pour un petit nombre de classes, choisissez des **bornes lisibles** (0, 50, 100, 150… plutôt que 0, 47,3, 94,6…). Ce qui se lit mal ne se retient pas.

### 1.1.3 Une variable discrète : le délai de livraison

Le délai de livraison est mesuré en jours entiers : c'est une variable **discrète**. On la représente par un diagramme en bâtons (une barre par valeur), pas par un histogramme à classes.

```python
d = liv["delai"]
print("commandes livrées :", len(d), "| médiane", d.median(), "jours | moyenne", round(d.mean(), 2), "| centile 90 :", d.quantile(0.9), "jours | maximum", d.max())
print("part livrée en 8 jours ou moins :", round((d <= 8).mean() * 100, 1), "% | en 10 jours ou plus :", round((d >= 10).mean() * 100, 2), "%")
```
<!--sortie-->
```text
commandes livrées : 19420 | médiane 6.0 jours | moyenne 5.71 | centile 90 : 8.0 jours | maximum 14
part livrée en 8 jours ou moins : 96.2 % | en 10 jours ou plus : 1.07 %
```


![Les délais de livraison : un diagramme en bâtons, avec la médiane et le centile 90.](figures/ch01-delais.png)

La médiane est de 6 jours et le centile 90 de 8 jours. On en tire une phrase utile pour la gérante : « **plus de 9 commandes sur 10 (96,2 %) sont livrées en 8 jours ou moins** ». C'est plus parlant que « le délai moyen est de 5,71 jours », car un client ne vit pas une moyenne : il vit **son** délai. Les centiles élevés (90, 95, 99) sont les bons résumés d'un **niveau de service**. Remarquez aussi la queue à droite : quelques commandes mettent 10 jours ou davantage. Nous chercherons au chapitre 11 d'où elles viennent.

### 1.1.4 Une variable qualitative : fréquences et barres ordonnées

Pour une variable qualitative, le résumé est une **table de fréquences** : combien de lignes par modalité, en nombre et en pourcentage. Le dessin est une **barre horizontale par modalité**, **triée par fréquence**. Un camembert est presque toujours une mauvaise idée : l'œil compare mal des angles, alors qu'il compare bien des longueurs alignées.

```python
print(cmd["code_promo"].replace("", "aucun").value_counts(normalize=True).mul(100).round(1).to_dict())
print(ret["motif"].value_counts(normalize=True).mul(100).round(1).to_dict())
print(cmd["canal"].value_counts(normalize=True).mul(100).round(1).to_dict())
```
<!--sortie-->
```text
{'aucun': 84.2, 'SOLDES': 8.3, 'FIDELITE': 6.7, 'BIENVENUE': 0.9}
{'Mauvais choix': 31.4, "Changement d'avis": 30.3, 'Défaut': 18.2, 'Livraison tardive': 12.1, 'Autre': 8.0}
{'Boutique': 46.6, 'Site': 42.5, 'Réseaux': 10.9}
```


![Fréquences de trois variables qualitatives : code promo des commandes, motif des retours, catégorie des lignes vendues.](figures/ch01-barres.png)

Trois phrases se lisent immédiatement. **Codes promo** : 84,2 % des commandes n'utilisent aucun code ; parmi les codes, `SOLDES` (8,3 %) domine. **Motifs de retour** : « mauvais choix » et « changement d'avis » représentent ensemble 61,7 % des retours, alors que « défaut » n'en représente que 18,2 % : la majorité des retours n'est pas un problème de qualité du produit. **Catégories** : les six catégories pèsent de 12,3 % à 19,8 % des lignes vendues, sans domination écrasante.

Deux précautions concernent les **modalités rares**. Le code `BIENVENUE` n'apparaît que dans 0,9 % des commandes. Une modalité aussi rare est **fragile** : toute statistique calculée sur elle (un panier moyen, un taux de retour) reposera sur peu de lignes. On peut la regrouper avec d'autres dans une classe « Autres », à condition de le dire, ou la garder en sachant qu'on lira ses chiffres avec prudence. Et quand une variable compte **beaucoup de modalités**, on ne dessine que les plus fréquentes et on regroupe le reste.

> ⚠️ **Piège : les modalités qui n'en font qu'une.** Une variable qualitative propre n'a pas `Ville A`, `VILLE A` et `Vile A` : c'est le travail du volume II. Mais l'exploration est aussi le moment où l'on **s'en aperçoit**. Si votre table de fréquences montre 119 écritures pour 20 villes, ne passez pas à la suite : nettoyez.

### 1.1.5 Une variable de temps : la série mensuelle

Une variable mesurée au fil du temps se représente par une **courbe**, avec le temps en abscisse. Regardons le chiffre d'affaires mensuel de trois années.

```python
mensuel = cmd.groupby(cmd["date_commande"].dt.to_period("M"))["panier"].sum()
annuel = cmd.groupby(cmd["date_commande"].dt.year)["panier"].sum()
print("chiffre d'affaires annuel TTC (k€) :", (annuel / 1000).round(0).to_dict())
print("évolution d'une année à l'autre (%) :", (annuel.pct_change() * 100).round(1).dropna().to_dict())
print("mois le plus faible :", str(mensuel.idxmin()), round(mensuel.min() / 1000, 1), "k€ | mois le plus fort :", str(mensuel.idxmax()), round(mensuel.max() / 1000, 1), "k€")
print("août / juillet :", {a: round(float(mensuel[f"{a}-08"] / mensuel[f"{a}-07"]), 2) for a in (2023, 2024, 2025)})
```
<!--sortie-->
```text
chiffre d'affaires annuel TTC (k€) : {2023: 1139.0, 2024: 1189.0, 2025: 1325.0}
évolution d'une année à l'autre (%) : {2024: 4.4, 2025: 11.4}
mois le plus faible : 2023-02 62.7 k€ | mois le plus fort : 2025-12 183.8 k€
août / juillet : {2023: 0.88, 2024: 0.87, 2025: 0.81}
```


![Chiffre d'affaires mensuel TTC, janvier 2023 à décembre 2025.](figures/ch01-serie-mensuelle.png)

La courbe raconte trois choses que ni la moyenne ni la médiane ne diraient :

1. **Une saison** : chaque année, un creux en janvier-février, une montée au printemps, un pic en novembre-décembre. Le mois le plus faible est février 2023 (62,7 k€), le plus fort décembre 2025 (183,8 k€).
2. **Une tendance** : le chiffre d'affaires annuel passe de 1 139 k€ (2023) à 1 189 k€ (2024) puis 1 325 k€ (2025), soit +4,4 % puis +11,4 %. D'une année à l'autre, la saison se répète, mais le niveau monte.
3. **Un creux d'été** : août est plus bas que juillet chaque année (0,88, 0,87 puis 0,81 de son niveau). Ce genre de détail se mesure mieux avec un outil de décomposition (chapitre 5) qu'à l'œil.

> 🧭 **Une série n'est pas une distribution.** Un histogramme du chiffre d'affaires mensuel sur trois ans mélangerait février et décembre, la saison et la tendance : il ne dirait rien. Pour une variable de temps, on regarde **l'ordre**. Le test est simple : si mélanger les lignes ne change pas le dessin, c'est une distribution ; sinon, c'est une série.

### 1.1.6 Résumer en une phrase, et trois pièges de lecture

Toute exploration univariée doit s'achever par une phrase. Cela force à décider ce que l'on a vraiment appris. Voici ce que l'on peut écrire de nos cinq variables.

| Variable | La phrase |
|---|---|
| Panier | « Le panier typique est de 80 € (médiane) ; six commandes sur dix sont sous la moyenne de 100 € ; une commande sur vingt dépasse environ 255 €. » |
| Délai de livraison | « Plus de neuf commandes sur dix sont livrées en 8 jours ou moins. » |
| Code promo | « Plus de huit commandes sur dix n'utilisent aucun code ; `SOLDES` est le code dominant. » |
| Motif de retour | « Six retours sur dix viennent d'un mauvais choix ou d'un changement d'avis, pas d'un défaut. » |
| Chiffre d'affaires | « Saisonnier (creux en février, pic en décembre) et en hausse : +4,4 % puis +11,4 %. » |

Trois pièges guettent la lecture de ces graphiques.

**Le piège de la moyenne.** Nous l'avons vu : sur une distribution asymétrique, la moyenne n'est pas le panier « typique ». Annoncez les deux, ou la médiane.

**Le piège de l'axe tronqué.** Un diagramme en barres dont l'axe vertical ne commence pas à zéro exagère les écarts : la hauteur des barres cesse d'être proportionnelle aux valeurs.

```python
par_an = cmd.groupby(cmd["date_commande"].dt.year)["panier"].mean()
print("panier moyen par année :", par_an.round(1).to_dict(), "| hausse 2025 contre 2024 :", round((par_an[2025] / par_an[2024] - 1) * 100, 1), "%")
```
<!--sortie-->
```text
panier moyen par année : {2023: 99.7, 2024: 98.9, 2025: 102.3} | hausse 2025 contre 2024 : 3.5 %
```


![Le même panier moyen par année, avec un axe tronqué à 97 € puis un axe à zéro.](figures/ch01-axe-tronque.png)

À gauche, la barre de 2025 semble **presque trois fois** plus haute que celle de 2024 ; à droite, on voit une hausse de 3,5 %. Les deux dessins utilisent les mêmes nombres. Règle : **un diagramme en barres commence à zéro**. Pour une courbe, où l'on regarde la forme et non la hauteur, on peut resserrer l'axe, à condition de le dire.

**Le piège des trop nombreuses classes.** Un histogramme à 177 classes ou un diagramme à 30 barres ne montre plus une forme : il montre un bruit. Regroupez.

> ✅ **À retenir.** Une variable se **résume** (centre, dispersion, forme), se **dessine** (selon son type) et se **dit en une phrase**. La médiane, les quartiles et les centiles sont les résumés les plus sûrs d'une variable asymétrique ; le logarithme est l'outil des montants ; une barre commence à zéro ; une série se lit dans l'ordre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 et 1.2, exercices 1.1 à 1.4.


## 1.2 Analyse bivariée et multivariée

> **La question de la gérante.** « Les jours où je dépense plus en publicité, je vends plus. Et mes clients du site n'achètent pas comme ceux de la boutique, non ? »

Une fois chaque variable comprise seule, on les regarde **deux à deux** (analyse **bivariée**), puis **trois ou plus** (analyse **multivariée**). Le but n'est pas encore de prouver une cause, mais de repérer les **relations** et de formuler des questions précises. La méthode dépend, encore, du type des deux variables.

| Variable 1 | Variable 2 | Dessin | Résumé |
|---|---|---|---|
| Quantitative | Quantitative | nuage de points, courbe lissée | corrélation (Pearson, Spearman) |
| Quantitative | Qualitative | boîtes par groupe, moyennes avec intervalle | moyenne et médiane par groupe |
| Qualitative | Qualitative | tableau croisé, barres empilées | profils lignes, taux par groupe |

### 1.2.1 Deux variables quantitatives : nuage et corrélation

Reprenons la remarque de la gérante : les commandes du jour dépendent-elles de la dépense publicitaire du jour ? Chaque jour est un point.

```python
print("corrélation commandes - publicité :", round(j["depense_pub"].corr(j["nb_commandes"]), 2), "(Pearson),", round(j["depense_pub"].corr(j["nb_commandes"], method="spearman"), 2), "(Spearman)")
print("corrélation commandes - température :", round(j["temperature_moy"].corr(j["nb_commandes"]), 2), "(Pearson),", round(j["temperature_moy"].corr(j["nb_commandes"], method="spearman"), 2), "(Spearman)")
```
<!--sortie-->
```text
corrélation commandes - publicité : 0.53 (Pearson), 0.38 (Spearman)
corrélation commandes - température : -0.21 (Pearson), -0.15 (Spearman)
```


![Commandes du jour contre la dépense publicitaire du jour (à gauche) et contre la température (à droite), avec une courbe lissée.](figures/ch01-nuages.png)

À gauche, le nuage est incliné vers le haut : la corrélation de Pearson est de 0,53. La **courbe lissée** (une régression locale, qui suit la tendance sans imposer de droite) montre que la relation n'est pas une droite parfaite : presque plate sous 200 € de dépense, puis montante. À droite, la température donne un nuage en forme de « montagne » : peu de commandes quand il fait très froid ou très chaud, un maximum vers 10 °C. La corrélation vaut −0,21 : un seul nombre résume mal une relation qui monte puis redescend.

> 💡 **Pearson, Spearman, et un dessin.** Le coefficient de **Pearson** mesure à quel point les points s'alignent sur une **droite**. Celui de **Spearman** utilise seulement les **rangs** : il mesure si la relation est **monotone** (toujours croissante ou toujours décroissante), droite ou non, et il est moins sensible aux valeurs extrêmes. Quand les deux diffèrent beaucoup (ici 0,53 et 0,38 pour la publicité), c'est un signal : la relation n'est pas une droite, ou quelques jours extrêmes pèsent lourd. **Dessinez toujours le nuage avant de croire un coefficient** : le volume I l'a montré avec les jeux d'Anscombe.

Voici le point le plus important de cette section. La corrélation de 0,53 entre dépense publicitaire et commandes **ne dit pas** que la publicité fait vendre. Les deux variables dépendent peut-être d'une troisième : **la saison**. La gérante dépense davantage en novembre et décembre, et c'est aussi quand on vend le plus. Vérifions en comparant « à mois égal » : on retire de chaque variable la moyenne de son mois.

```python
j2 = j.assign(mois=j["date"].dt.month)
for c in ["depense_pub", "nb_commandes", "temperature_moy"]:
    j2[c + "_ecart"] = j2[c] - j2.groupby("mois")[c].transform("mean")
print("commandes - publicité, à mois égal :", round(j2["depense_pub_ecart"].corr(j2["nb_commandes_ecart"]), 2))
print("commandes - température, à mois égal :", round(j2["temperature_moy_ecart"].corr(j2["nb_commandes_ecart"]), 2))
```
<!--sortie-->
```text
commandes - publicité, à mois égal : 0.1
commandes - température, à mois égal : -0.04
```

La corrélation avec la publicité tombe de 0,53 à 0,10 ; celle avec la température de −0,21 à −0,04. **La plus grande partie du lien venait de la saison.** Il reste un faible lien résiduel (0,10) pour la publicité. Est-il causal ? Le volume I a posé la question ; nous y reviendrons avec les outils du chapitre 3. L'exploration, elle, a fait son travail : elle a transformé la question (« la publicité fait-elle vendre ? ») en une autre, plus précise (« **à saison égale**, quel est l'effet d'une dépense supplémentaire ? »).

### 1.2.2 Une variable quantitative et une variable qualitative : comparer des groupes

Comparer un montant selon une catégorie est la question la plus courante d'un analyste : le panier selon le canal, le délai selon le transporteur, la dépense selon le segment. On dessine une **boîte par groupe**, côte à côte, sur le même axe, et l'on résume par la **moyenne avec son intervalle de confiance**.

```python
g = cmd.groupby("canal")["panier"].agg(["mean", "median", "std", "count"])
g["demi_intervalle"] = 1.96 * g["std"] / np.sqrt(g["count"])
print(g.round(2).to_string())
t = liv.groupby("transporteur")["delai"].agg(["mean", "median", "std", "count"])
t["demi_intervalle"] = 1.96 * t["std"] / np.sqrt(t["count"])
print(t.round(2).to_string())
```
<!--sortie-->
```text
            mean  median    std  count  demi_intervalle
canal                                                  
Boutique  100.90   79.80  80.87  16975             1.22
Réseaux   100.52   79.70  81.48   3957             2.54
Site       99.77   79.76  80.39  15463             1.27
                mean  median   std  count  demi_intervalle
transporteur                                              
Transporteur A  5.21     5.0  1.35   8734             0.03
Transporteur B  5.82     6.0  1.32   6915             0.03
Transporteur C  6.68     7.0  1.33   3771             0.04
```


![Panier par canal (à gauche) et délai de livraison par transporteur (à droite) : deux comparaisons de groupes.](figures/ch01-groupes.png)

Deux comparaisons, deux conclusions opposées.

- **Le panier selon le canal.** Les trois boîtes sont presque identiques. Les moyennes (100,9 € en boutique, 99,8 € sur le site, 100,5 € pour les réseaux) diffèrent de moins de 1,2 €, et leurs intervalles (±1,2 €, ±1,3 € et ±2,5 €) se **recouvrent largement** : on ne peut pas dire que les trois canaux ont des paniers différents. Une absence de différence est un résultat : la gérante peut cesser de se demander si « les clients du site dépensent moins ».
- **Le délai selon le transporteur.** Les moyennes (5,2 ; 5,8 et 6,7 jours) sont séparées de plus de 0,5 jour, et les intervalles (±0,03 à ±0,04 jour) ne se recouvrent pas du tout : la différence est **nette**. Le transporteur C livre en moyenne un jour et demi après le transporteur A, et 9,1 % de ses livraisons dépassent 8 jours, contre 1,7 % pour A. Voilà une vraie piste, que le chapitre 11 poursuivra.

> 🧭 **En pratique : lire un intervalle.** Quand deux intervalles de confiance **ne se recouvrent pas**, la différence est probablement réelle. Quand ils se recouvrent largement, on ne peut rien affirmer (c'est la logique des tests du chapitre 2). Le cas intermédiaire (léger recouvrement) demande un test : ne concluez pas à l'œil.

### 1.2.3 Deux variables qualitatives : tableaux croisés et profils

Pour deux variables qualitatives, on construit un **tableau croisé**, puis on le lit en **pourcentages par ligne** (le profil de chaque groupe), pas en effectifs bruts. Les effectifs dépendent de la taille des groupes ; les profils les comparent à armes égales.

```python
print((pd.crosstab(cmd["canal"], cmd["mode_livraison"], normalize="index") * 100).round(1).to_string())
```
<!--sortie-->
```text
mode_livraison  Domicile  Point relais  Retrait magasin
canal                                                  
Boutique             0.0           0.0            100.0
Réseaux             54.7          38.4              6.9
Site                55.4          37.5              7.1
```


![Mode de livraison selon le canal, en pourcentage des commandes de chaque canal.](figures/ch01-profils.png)

Le tableau est très contrasté : **toutes** les commandes de la boutique sont en retrait magasin (c'est la définition du canal), alors que le site et les réseaux ont des profils presque identiques (55 % à domicile, 37 à 38 % en point relais, 7 % en retrait). Cette relation est **structurelle** : elle ne nous apprend rien, elle vérifie que les données respectent une règle de l'entreprise. C'est aussi un rôle de l'exploration.

Deux autres tableaux croisés sont plus instructifs.

```python
lc = lig.merge(cmd[["id_commande", "canal"]], on="id_commande")
lc["retourne"] = lc["id_ligne"].isin(ret["id_ligne"])
print((lc.groupby("canal")["retourne"].mean() * 100).round(1).to_dict())
print((pd.crosstab(cmd["canal"], cmd["code_promo"].replace("", "aucun"), normalize="index") * 100).round(1).to_string())
```
<!--sortie-->
```text
{'Boutique': 3.1, 'Réseaux': 6.7, 'Site': 9.0}
code_promo  BIENVENUE  FIDELITE  SOLDES  aucun
canal                                         
Boutique          0.9       6.4     8.3   84.4
Réseaux           0.7       6.6     8.8   83.9
Site              0.9       7.0     8.1   84.1
```

Le **taux de retour** (part des lignes renvoyées) dépend fortement du canal : 3,1 % en boutique, 6,7 % pour les réseaux, 9,0 % sur le site. Le **code promo**, en revanche, est utilisé de la même façon partout : 84 % sans code dans chaque canal, `SOLDES` entre 8,1 % et 8,8 %. Comment dire, sans test, si un écart est « grand » ? On résume la **force** de la liaison entre deux qualitatives par un indicateur qui varie de 0 (indépendance) à 1 (liaison parfaite), le *V de Cramér*, construit à partir du **khi-deux** :

```python
from scipy.stats import chi2_contingency
def cramer(t):
    chi2 = chi2_contingency(t)[0]
    return (chi2 / (t.values.sum() * (min(t.shape) - 1))) ** 0.5
print("canal et retour :", round(cramer(pd.crosstab(lc["canal"], lc["retourne"])), 3), "| canal et code promo :", round(cramer(pd.crosstab(cmd["canal"], cmd["code_promo"])), 3))
```
<!--sortie-->
```text
canal et retour : 0.118 | canal et code promo : 0.01
```

La liaison canal-retour (0,118) est **plus de dix fois** plus forte que la liaison canal-promo (0,010) : le canal compte pour comprendre les retours, pas pour comprendre l'usage des codes. Le test du khi-deux, qui dit si une liaison est plus grande que ce que le hasard produirait, est présenté au chapitre 2 ; retenez pour l'instant que **plus l'effectif est grand, plus le test détecte de petites liaisons** : un indicateur de force comme le V de Cramér se lit mieux qu'une probabilité.

### 1.2.4 Trois variables ou plus

Dès que l'on croise trois variables, deux outils prennent le relais : les **couleurs et les facettes** (des petits graphiques côte à côte, un par groupe) pour **voir** ; la **matrice de corrélation** pour **balayer** beaucoup de variables d'un coup.

```python
cols = ["nb_commandes", "chiffre_affaires", "temperature_moy", "pluie_mm", "promo_active", "depense_pub"]
print(j[cols].corr().round(2).to_string())
```
<!--sortie-->
```text
                  nb_commandes  chiffre_affaires  temperature_moy  pluie_mm  promo_active  depense_pub
nb_commandes              1.00              0.92            -0.21     -0.03          0.07         0.53
chiffre_affaires          0.92              1.00            -0.07     -0.04         -0.01         0.42
temperature_moy          -0.21             -0.07             1.00     -0.03         -0.08        -0.36
pluie_mm                 -0.03             -0.04            -0.03      1.00          0.03         0.03
promo_active              0.07             -0.01            -0.08      0.03          1.00         0.14
depense_pub               0.53              0.42            -0.36      0.03          0.14         1.00
```


![Matrice de corrélation des indicateurs journaliers.](figures/ch01-correlations.png)

La matrice se lit en cherchant les cases **foncées**, et en se méfiant de chacune. Ici :

- `nb_commandes` et `chiffre_affaires` sont presque redondants (0,92) : l'un s'explique par l'autre, inutile de les mettre ensemble dans une analyse.
- La **publicité** est liée aux commandes (0,53) et à la **température** (−0,36) : la gérante dépense davantage quand il fait froid, c'est-à-dire en fin d'année. Voilà le chemin de la confusion : la température n'agit pas sur la publicité, c'est la **saison** qui agit sur les deux.
- La **pluie** n'est liée à rien (de −0,04 à 0,03) : à cette échelle (le jour, toutes catégories), elle ne se voit pas.
- La **promotion** semble sans lien avec le chiffre d'affaires (−0,01) ; la section suivante montre que cette absence est trompeuse.

> ⚠️ **Piège : une matrice de corrélation ne dit pas les non-linéarités.** Une relation en « montagne » (la température) peut donner un coefficient proche de zéro. Une matrice **balaie**, elle ne **conclut** pas : chaque case qui intéresse mérite son nuage de points.

### 1.2.5 Le paradoxe de Simpson dans les vraies données

Voici le piège le plus déroutant de l'analyse bivariée. Comparons le chiffre d'affaires journalier moyen les jours **avec** et **sans** promotion.

```python
print("CA moyen par jour (€) :", j.groupby("promo_active")["chiffre_affaires"].mean().round(0).to_dict(), "| part des jours en promotion :", round(j["promo_active"].mean() * 100, 1), "%")
m = j2[j2["mois"].isin([1, 6, 7, 11])].groupby(["mois", "promo_active"])["chiffre_affaires"].mean().unstack().round(0)
m["écart (€)"] = m[1] - m[0]
print(m.rename(columns={0: "sans promotion", 1: "avec promotion"}).to_string())
```
<!--sortie-->
```text
CA moyen par jour (€) : {0: 3339.0, 1: 3300.0} | part des jours en promotion : 14.0 %
promo_active  sans promotion  avec promotion  écart (€)
mois                                                   
1                     2253.0          2601.0      348.0
6                     3338.0          3411.0       73.0
7                     3078.0          3283.0      205.0
11                    4224.0          4872.0      648.0
```


![Chiffre d'affaires journalier moyen avec et sans promotion : tous les jours confondus (à gauche), puis à mois égal (à droite).](figures/ch01-simpson.png)

Tous jours confondus, les jours de promotion rapportent **moins** (3 300 €) que les autres (3 339 €). On serait tenté de conclure que la promotion **détruit** du chiffre d'affaires. Mais regardez mois par mois : dans **chacun** des quatre mois qui contiennent à la fois des jours de promotion et des jours sans promotion (janvier, juin, juillet, novembre), les jours de promotion rapportent **plus** : +348 €, +73 €, +205 € et +648 €.

Comment les deux lectures peuvent-elles être vraies à la fois ? Parce que **la promotion n'est pas répartie au hasard dans l'année**. Elle tombe surtout en janvier et en juillet (soldes), deux mois creux, et seulement une semaine en novembre. Les jours « sans promotion » comprennent décembre, le meilleur mois de l'année, qui n'a **aucun** jour de promotion. Comparer des jours de promotion (plutôt en saison basse) à des jours sans promotion (dont la haute saison) compare des **populations différentes**. C'est le **paradoxe de Simpson** : une relation observée sur l'ensemble s'inverse (ou disparaît) quand on la regarde **dans chaque sous-groupe**.

> 💡 **Quel chiffre croire ?** Pour répondre à « la promotion fait-elle vendre ? », il faut comparer des jours **comparables** : ici, à mois égal, car la saison est la variable qui pèse sur tout le reste. Le chiffre agrégé est exact, mais il répond à une autre question (« en moyenne, les jours de promotion sont-ils meilleurs ? ») et c'est une **mauvaise** réponse à la première. La règle générale : quand un groupe n'est pas formé au hasard, **cherchez la variable qui détermine à la fois l'appartenance au groupe et le résultat**. On l'appelle une **variable de confusion**.

La **vérité programmée** de ces données est que la promotion augmente de 18 % le nombre de commandes d'un jour donné. Sur les quatre mois comparables, l'exploration retrouve une hausse du même sens (par exemple de 24 à 30 commandes en janvier, de 44 à 55 en novembre), mais pas encore son ampleur exacte : isoler un effet demande un modèle de régression, qui fait l'objet du chapitre 3.

### 1.2.6 Ce que l'exploration multivariée permet, et ce qu'elle ne permet pas

À l'issue de cette section, trois habitudes sont à retenir.

1. **Un coefficient ne remplace pas un dessin.** Dessinez le nuage, la boîte, le profil.
2. **Une relation n'est pas une cause.** Avant d'interpréter, demandez-vous quelle troisième variable peut agir sur les deux (la saison, le canal, la taille).
3. **Comparer, c'est comparer des comparables.** Quand les groupes ne sont pas formés au hasard, comparez **à variable de confusion égale** (à mois égal, à canal égal…), ou ajustez par un modèle.

> ✅ **À retenir.** Le type des deux variables décide du dessin et du résumé : nuage et corrélation (deux quantitatives), boîtes et moyennes avec intervalle (une de chaque), tableaux croisés et profils (deux qualitatives). Trois variables : facettes et matrice de corrélation. La saison explique l'essentiel du lien entre publicité et ventes ; le paradoxe de Simpson montre qu'un chiffre agrégé peut dire l'inverse de chaque sous-groupe.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.3 et 1.4, exercices 1.5 à 1.8.


## 1.3 Repérer les motifs et les anomalies

> **La question de la gérante.** « Il y a eu des jours bizarres l'an dernier : je me souviens d'une panne du site, mais je ne sais plus quand. Peux-tu les retrouver, et me dire si c'est grave ? »

Une série de ventes est faite de **motifs réguliers** (la saison, le jour de la semaine, la tendance) et de **sorties de route** (une panne, une erreur, un événement). Les distinguer est le cœur de l'exploration d'une série : **on ne peut repérer ce qui est anormal qu'une fois que l'on sait ce qui est normal**. Cette section commence donc par les motifs, puis cherche les anomalies, et finit par la question qui décide de ce que l'on fait d'une anomalie : qu'est-elle ?

### 1.3.1 Les motifs réguliers : la semaine et l'année

Deux rythmes se superposent dans les ventes : la **semaine** (le samedi n'est pas un mardi) et l'**année** (décembre n'est pas février). On les mesure par un **profil** : la moyenne par jour de la semaine, par mois, rapportée à la moyenne générale.

```python
jx = j.assign(jour=j["date"].dt.dayofweek, mois=j["date"].dt.month)
moy = jx["nb_commandes"].mean()
semaine = (jx.groupby("jour")["nb_commandes"].mean() / moy).round(2)
annee = (jx.groupby("mois")["nb_commandes"].mean() / moy).round(2)
print("moyenne quotidienne :", round(moy, 1), "commandes")
print("indice par jour de la semaine (lun. à dim.) :", semaine.tolist())
print("indice par mois (janv. à déc.) :", annee.tolist())
```
<!--sortie-->
```text
moyenne quotidienne : 33.2 commandes
indice par jour de la semaine (lun. à dim.) : [0.95, 0.9, 0.94, 0.99, 1.15, 1.39, 0.67]
indice par mois (janv. à déc.) : [0.85, 0.74, 0.84, 0.91, 0.98, 0.93, 0.87, 0.71, 1.03, 1.03, 1.42, 1.68]
```


![Commandes moyennes par jour de la semaine (à gauche) et par mois (à droite).](figures/ch01-saisonnalite.png)

La moyenne est de 33,2 commandes par jour, mais la **journée typique n'existe pas** : un samedi vaut 1,39 fois la moyenne, un dimanche 0,67 fois ; décembre vaut 1,68 fois la moyenne, février 0,74. Ces deux rythmes ont une conséquence pratique immédiate pour la détection d'anomalies : **comparer un dimanche de février à la moyenne générale n'a aucun sens**. La référence d'un jour doit être un jour **semblable**.

### 1.3.2 Un changement de niveau

Un autre motif est le **changement de niveau** : à partir d'une date, la série se met à fonctionner autour d'une autre valeur. Il peut venir d'une décision (un changement de prix), d'un événement (ouverture d'un canal) ou d'une erreur (changement d'unité, volume II).

Le panier moyen mensuel a-t-il changé de niveau ? Regardons-le d'abord brutalement, puis à produits constants.

```python
cc = cmd.assign(annee=cmd["date_commande"].dt.year, mois=cmd["date_commande"].dt.month)
pm = cc.groupby(["annee", "mois"])["panier"].mean().unstack(0)
print("panier moyen 2025 / 2024, mois par mois :", (pm[2025] / pm[2024]).round(2).tolist())
l2 = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "prix_vente"]], on="id_produit")
indice = (l2["prix_unitaire"] / l2["prix_vente"]).groupby(l2["date_commande"].dt.year).mean()
print("prix payé / prix catalogue, par année :", indice.round(3).to_dict())
```
<!--sortie-->
```text
panier moyen 2025 / 2024, mois par mois : [1.08, 1.09, 1.05, 1.02, 1.01, 0.96, 1.08, 1.01, 1.01, 1.04, 1.02, 1.07]
prix payé / prix catalogue, par année : {2023: 1.0, 2024: 1.0, 2025: 1.03}
```


![Panier moyen mensuel (à gauche), où la saison masque tout, et prix payé rapporté au prix catalogue 2023-2024 (à droite), où une marche de 3 % apparaît.](figures/ch01-rupture-prix.png)

Le panier moyen **mois par mois** oscille entre 85 et 117 € : la saison (le mix des produits change au fil de l'année) masque complètement un changement de prix de 3 %. Le rapport 2025 sur 2024, mois par mois, ne l'affiche pas non plus de façon claire (de 0,96 à 1,09 selon les mois : la hausse de 3 % se mêle à la variation naturelle). Mais, **à produits constants** (le prix payé divisé par le prix catalogue, ligne par ligne), la marche est parfaitement nette : l'indice vaut 1,000 en 2023 et 2024, puis 1,030 en 2025. Voilà la vérité programmée : une hausse de prix de 3 % au 1ᵉʳ janvier 2025.

> 💡 **Détecter un changement de niveau.** Un indicateur agrégé (le panier moyen) mélange des **effets de composition** (quels produits, quels mois) et des **effets de niveau** (le prix). Pour isoler un changement de niveau, comparez **à composition constante** : même produit, même mois, même canal. C'est la même logique que « à mois égal » en 1.2.

### 1.3.3 Les valeurs extrêmes : une première méthode, et ses limites

Une méthode classique pour repérer les valeurs extrêmes est la règle des **1,5 écart interquartile** : on signale toute valeur supérieure à Q3 + 1,5 × EIQ ou inférieure à Q1 − 1,5 × EIQ. Essayons-la sur le chiffre d'affaires **journalier** de la série qui contient des incidents injectés (`jours_incidents.csv`).

```python
ji1 = ji.drop_duplicates("date")
q1, q3 = ji1["chiffre_affaires"].quantile([0.25, 0.75])
haut = ji1[ji1["chiffre_affaires"] > q3 + 1.5 * (q3 - q1)]
print("jours d'exploitation :", len(ji1), "| seuil haut :", round(q3 + 1.5 * (q3 - q1)), "€ | jours signalés :", len(haut))
print("part de ces jours en décembre :", round((haut["date"].dt.month == 12).mean() * 100), "% | en novembre ou décembre :", round(haut["date"].dt.month.isin([11, 12]).mean() * 100), "%")
```
<!--sortie-->
```text
jours d'exploitation : 1096 | seuil haut : 6535 € | jours signalés : 29
part de ces jours en décembre : 69 % | en novembre ou décembre : 90 %
```

La règle signale 29 jours, dont 69 % en décembre et 90 % en novembre ou décembre : ce ne sont pas des anomalies, c'est **la saison**. La règle compare chaque jour à **tous** les jours de trois ans, alors que la bonne référence est « les jours semblables » (même jour de la semaine, même période de l'année). Elle rate en plus les anomalies à la **baisse** dans une saison haute : une panne en décembre ne descendrait même pas sous le seuil bas.

### 1.3.4 Détecter des incidents : une méthode simple et robuste

Voici une méthode qui respecte la saison et la semaine, en trois étapes.

1. **Référence locale.** Pour chaque jour, on prend la **médiane** des jours de la même sorte (le même jour de la semaine) dans les quatre semaines avant et les quatre semaines après, **en excluant le jour lui-même**.
2. **Écart relatif.** On compare le jour à sa référence **en logarithme** (un écart de −50 % et un de +100 % sont alors symétriques).
3. **Score z robuste.** On divise l'écart par un **écart-type robuste** calculé avec le *MAD* (l'écart médian absolu : la médiane des écarts à la médiane, multipliée par 1,4826 pour être comparable à un écart-type). Un jour est signalé si son score dépasse un **seuil**.

L'avantage du MAD sur l'écart-type est qu'il **ne se laisse pas gonfler par les anomalies que l'on cherche** : un jour ×10 ne change pas la médiane.

On applique cette méthode à **deux signaux** : le **nombre de commandes** (une panne ou une fermeture le fait chuter) et le **panier du jour**, c'est-à-dire le chiffre d'affaires divisé par le nombre de commandes (une commande géante ou une erreur de saisie le fait bondir). On ajoute une règle d'**unicité** pour les dates en double.

```python
jz, doublons = O.incidents_jours(ji)
print("dates en double :", sorted(d.strftime("%Y-%m-%d") for d in doublons))
js = jz["date"].dt.dayofweek.values
_, mad = O.z_robuste(jz["chiffre_affaires"], O.reference_locale(jz["chiffre_affaires"], js, 4))
print("écart relatif typique d'un jour à sa référence (MAD, en logarithme) :", round(mad, 2))
signaux = O.signaler(jz, doublons, 4)
print("jours signalés au seuil 4 :", len(signaux))
```
<!--sortie-->
```text
dates en double : ['2025-10-20']
écart relatif typique d'un jour à sa référence (MAD, en logarithme) : 0.27
jours signalés au seuil 4 : 11
```

On évalue maintenant la méthode contre la vérité (le fichier des incidents injectés). Ouvrons-le seulement maintenant, comme une correction.

```python
vrais = set(vi["date"])
print(vi[["date", "type"]].assign(date=vi["date"].dt.strftime("%Y-%m-%d")).to_string(index=False))
lignes = []
for seuil in (3, 3.5, 4, 5):
    s = O.signaler(jz, doublons, seuil)
    p, r = O.precision_rappel(s, vrais)
    lignes.append((seuil, len(s), len(s & vrais), round(p * 100), round(r * 100)))
print(pd.DataFrame(lignes, columns=["seuil", "signalés", "dont vrais", "précision %", "rappel %"]).to_string(index=False))
```
<!--sortie-->
```text
      date               type
2025-03-12         panne_site
2025-03-13         panne_site
2025-03-14         panne_site
2025-06-18       commande_b2b
2025-09-09      erreur_saisie
2025-04-28 fermeture_boutique
2025-04-29 fermeture_boutique
2025-10-20    doublon_journee
 seuil  signalés  dont vrais  précision %  rappel %
   3.0        25           6           24        75
   3.5        13           6           46        75
   4.0        11           6           55        75
   5.0         4           3           75        38
```


![Chiffre d'affaires journalier de 2025 (échelle logarithmique) : jours signalés au seuil 4 et incidents réellement injectés.](figures/ch01-incidents.png)

Deux mesures, déjà rencontrées au volume II (sections 1.2 et 2.5) : la **précision** est la part des jours signalés qui sont de vrais incidents (« quand l'alarme sonne, a-t-elle raison ? ») ; le **rappel** est la part des vrais incidents qui ont été signalés (« les incidents sont-ils tous attrapés ? »). Aucun seuil ne donne 100 % aux deux.

![Précision et rappel de la méthode selon le seuil du score z.](figures/ch01-seuils.png)

Lisons les résultats. **L'erreur de saisie** (le chiffre d'affaires ×10, le 9 septembre) est repérée par tous les seuils : son panier du jour est dix fois plus élevé que d'habitude, le score atteint 15. **La commande B2B** (+4 200 €, le 18 juin) est signalée à son tour, grâce au panier du jour, jusqu'à un seuil d'environ 4,5. **Les jours de panne** (12 à 14 mars) et **de fermeture** (28 et 29 avril), qui font perdre environ 45 % des ventes, sont plus **difficiles** : une journée ordinaire fluctue déjà de ±30 % autour de sa référence à cause du simple hasard (peu de commandes par jour). Au seuil 4, on en attrape trois sur cinq ; au seuil 5, une seule. **Le doublon** (20 octobre) est attrapé par la règle d'unicité, indépendamment de tout seuil.

Le seuil est un **arbitrage** : un seuil bas attrape presque tous les incidents mais signale de nombreux jours ordinaires ; un seuil haut ne signale que des certitudes mais rate les incidents modestes. Le bon réglage dépend du **coût** de chaque erreur : une fausse alerte coûte quelques minutes d'investigation ; un incident raté peut fausser un budget.

### 1.3.5 Anomalie, erreur, événement : trois choses différentes

La méthode signale des **jours inhabituels** ; elle ne dit pas **pourquoi** ils le sont. Regardons les jours signalés qui ne sont pas des incidents injectés.

```python
s4 = O.signaler(jz, doublons, 4)
faux = sorted(d for d in s4 if d not in vrais)
print("jours signalés au seuil 4 qui ne sont pas des incidents injectés :", [d.strftime("%Y-%m-%d") for d in faux])
```
<!--sortie-->
```text
jours signalés au seuil 4 qui ne sont pas des incidents injectés : ['2023-01-29', '2024-01-01', '2024-01-02', '2024-01-05', '2024-01-07']
```

Ces jours ne sont pas pour autant des erreurs : ils tombent tous en **janvier**, surtout au tout début de l'année, au moment où la série plonge du pic de décembre vers le creux de janvier. La référence locale (les quatre semaines avant et après) y mélange deux régimes, ce qui rend le jour « anormalement bas » par rapport à elle. Ce sont de **vraies** journées de faible activité, sans cause à corriger : un **événement du calendrier** que la méthode ne connaissait pas.

Il faut donc **distinguer trois choses**, car on ne fait pas la même chose de chacune :

| Nature | Exemple | Que fait-on ? |
|---|---|---|
| **Erreur de données** | chiffre d'affaires ×10 (saisie), journée en double | on **corrige** ou on **exclut**, et on le documente (volume II) |
| **Événement réel exceptionnel** | commande B2B, panne du site, fermeture | on **garde** la valeur, on l'**annote**, et l'on décide si elle doit entrer dans les moyennes et les prévisions |
| **Régularité mal connue** | creux du début de janvier, jours fériés | on **améliore la référence** (calendrier des événements connus), on ne corrige pas les données |

> ⚠️ **Piège : supprimer une anomalie « parce qu'elle gêne ».** Retirer d'une série une panne de site parce qu'elle fausse la moyenne revient à dire que la boutique n'a jamais de panne. La décision (exclure, annoter, conserver) dépend de la **question posée** : pour estimer la demande « normale », on peut exclure la panne ; pour estimer le chiffre d'affaires **réel**, on la garde.

Le meilleur remède à long terme n'est pas un meilleur algorithme, mais un **calendrier d'événements** tenu à jour (soldes, fermetures, pannes, campagnes, jours fériés). Avec lui, une anomalie signalée se confronte tout de suite à une explication connue ; sans lui, on réinvestigue à chaque fois.

> ✅ **À retenir.** Pour repérer une anomalie, **comparez à une référence locale** (jour semblable, période proche), pas à la moyenne générale ; mesurez l'écart relatif ; réduisez-le par un **score robuste** (MAD) ; **fixez le seuil selon le coût des erreurs** ; évaluez précision et rappel quand vous avez une vérité. Un jour signalé est une **question**, pas une réponse : erreur, événement ou régularité méconnue, on n'en fait pas la même chose.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.5 et 1.6, exercices 1.9 à 1.12.


## 1.4 ➕ Pour aller plus loin : une liste de contrôle EDA réutilisable

> **La question de la gérante.** « La prochaine fois que j'ouvre un nouveau fichier, je veux que tu fasses toujours les mêmes vérifications. Tu peux me les écrire ? »

Les trois sections précédentes ont déroulé une démarche : regarder chaque variable, puis les relations, puis les motifs et les anomalies. Un analyste expérimenté ne la redécouvre pas à chaque fichier : il la suit comme une **liste de contrôle** (comme un pilote avant le décollage). Elle protège des oublis, surtout les jours de presse.

### 1.4.1 La liste, en six temps

| Temps | Questions à se poser | Réflexes | Alerte à lever |
|---|---|---|---|
| **1. Le tableau** | Que représente une ligne (le **grain**) ? Quelle colonne l'identifie ? Combien de lignes, de colonnes, quelle période ? | `shape`, `info`, `head`, clé unique | clé qui se répète, ligne qui n'est pas ce qu'on croyait |
| **2. Les types** | Chaque colonne a-t-elle le bon type (nombre, date, catégorie, texte) ? | `dtypes`, conversions explicites | dates en texte, nombres en texte, identifiants lus comme des nombres |
| **3. Les manques** | Quelle part de valeurs manque, et **où** ? | `isna().mean()`, manquants par groupe | plus de 5 % de manquants, manquants concentrés dans un groupe |
| **4. Chaque variable** | Centre, dispersion, forme, modalités ? | quantiles, histogramme, barres ordonnées | asymétrie forte, modalité dominante, modalités rares, colonne constante |
| **5. Les relations** | Quelles variables varient ensemble ? Quelle troisième variable pourrait tout expliquer ? | matrice de corrélation, boîtes par groupe, tableaux croisés, « à saison égale » | corrélation très forte (variables redondantes), Simpson |
| **6. Le temps et les anomalies** | Quels rythmes (semaine, saison, tendance) ? Quels jours sortent du lot, et sont-ils des erreurs, des événements, des régularités mal connues ? | profils, référence locale, score robuste, calendrier d'événements | rupture de niveau, valeur isolée, doublon de date |

Chaque ligne se vérifie en quelques minutes ; on **note** ce que l'on trouve, même quand tout va bien, car l'absence d'anomalie est une information.

### 1.4.2 Automatiser le premier tour

Une partie de cette liste se programme. La fonction `rapport_eda` du chapitre calcule, pour n'importe quel tableau, les types, les manques, un résumé des variables quantitatives et qualitatives, les corrélations fortes, et lève des **alertes** en langage clair. Appliquons-la au fichier des clients.

```python
r = O.rapport_eda(cli, cle="id_client")
print(r["lignes"], "lignes,", r["colonnes"], "colonnes")
print(r["types"].to_string())
print(*r["alertes"], sep="\n")
```
<!--sortie-->
```text
6000 lignes, 8 colonnes
                         type  manquants_pct  distincts
id_client               int64            0.0       6000
date_inscription          str            0.0       2541
annee_naissance         int64            0.0         68
ville                     str            0.0         20
canal_acquisition         str            0.0          3
fidelite                int64            0.0          2
email_valide            int64            0.0          2
consentement_marketing  int64            0.0          2
id_client : une valeur différente par ligne (identifiant ?)
date_inscription : des dates stockées en texte (convertir)
ville : 2 modalité(s) rare(s) (moins de 1 %)
```

Le rapport lève trois alertes. `id_client` a une valeur différente par ligne : c'est bien un **identifiant** (aucune alerte de doublon de clé), ce qui est rassurant. `date_inscription` est stockée en **texte** : il faut la convertir en date avant de calculer une ancienneté. Enfin, `ville` compte deux modalités rares (moins de 1 % des clients chacune) : les chiffres sur ces villes reposeront sur peu de clients. Aucune valeur manquante n'est signalée : le fichier est complet.

Essayons sur les données journalières, qui contiennent des mesures continues.

```python
r2 = O.rapport_eda(j, cle="date")
print(r2["quantitatives"].to_string())
print(*r2["alertes"], sep="\n")
```
<!--sortie-->
```text
                    min  mediane  moyenne      max  asymetrie
jour_semaine        1.0     4.00     4.00     7.00       0.00
nb_commandes        9.0    30.50    33.21    97.00       1.24
chiffre_affaires  736.8  3100.66  3333.17  9982.99       0.96
temperature_moy    -2.6    13.20    13.09    27.70      -0.01
pluie_mm            0.0     0.00     1.72    27.00       2.70
promo_active        0.0     0.00     0.14     1.00        NaN
depense_pub        50.5   174.45   208.06   781.60       1.37
date : une valeur différente par ligne (identifiant ?)
chiffre_affaires : une valeur différente par ligne (identifiant ?)
pluie_mm : très asymétrique (2.70) : regarder la médiane et l'échelle logarithmique
nb_commandes et chiffre_affaires : corrélation forte (0.92)
```

Les alertes sont différentes : la colonne `pluie_mm` est **très asymétrique** (de nombreux jours sans pluie, quelques jours de forte pluie) ; `nb_commandes` et `chiffre_affaires` sont **redondantes** (corrélation de 0,92). La fonction signale aussi `date` et `chiffre_affaires` comme « une valeur différente par ligne » : pour `date`, c'est ce que l'on attend d'une clé ; pour un montant, c'est une fausse alerte, sans conséquence.

> ⚠️ **Piège : croire une alerte, ou croire son absence.** Une alerte est une **question** (voulue ? sans importance ? à corriger ?), jamais une conclusion. Et l'absence d'alerte ne prouve rien : la fonction ne voit pas qu'un chiffre d'affaires est ×10 un jour donné, ni qu'une catégorie est mal orthographiée, ni que le mois de décembre domine tout. **Un rapport automatique remplace la saisie, pas le regard.**

### 1.4.3 Ce que le rapport ne fait pas, et comment le compléter

La fonction ne remplace pas trois choses, que l'analyste ajoute à la main :

1. **Les dessins.** Un histogramme, un nuage ou une série montrent ce qu'un tableau de nombres cache. On les produit pour les variables que le rapport a signalées.
2. **Les règles du métier.** Un montant doit valoir quantité × prix, une date de livraison suit la date de commande : ces règles s'écrivent comme des **contrôles** (volume II, section 3.2) et s'ajoutent à la liste.
3. **Le calendrier des événements.** Soldes, fermetures, pannes, campagnes : sans lui, chaque anomalie est une enquête.

### 1.4.4 Écrire le compte rendu d'une exploration

L'exploration se termine par un **court écrit**. Voici une trame réutilisable, qui tient sur une page.

> **Fichier exploré :** nom, grain, période, nombre de lignes, source.
> **Qualité :** types corrigés, manques (où, combien), doublons, colonnes inutiles.
> **Ce que l'on a appris sur chaque variable** (une phrase par variable importante).
> **Relations notables**, avec la troisième variable envisagée.
> **Rythmes** (semaine, saison, tendance) et **anomalies** (date, nature : erreur, événement, régularité), avec l'action décidée.
> **Questions ouvertes** et **méthode proposée** pour la suite (test, régression, segmentation, série).

Cette page est le **livrable** de l'exploration : c'est elle que lira la gérante, et c'est elle qui décide de la suite.

> ✅ **À retenir.** Une exploration suit toujours le même fil : tableau, types, manques, variables, relations, temps et anomalies. On automatise le premier tour, on garde le regard pour le reste, et l'on **écrit** ce que l'on a trouvé, y compris que tout va bien.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : application 1.7, exercices 1.13 et 1.14.


## Bilan du chapitre 1

Vous savez maintenant :

- **explorer** une variable seule avec la méthode en trois gestes (résumer, dessiner, écrire une phrase) : médiane, quartiles et centiles pour une variable asymétrique, **échelle logarithmique** pour les montants, **bâtons** pour une variable discrète, **barres ordonnées** pour une qualitative, **courbe** pour une série ;
- **choisir les classes** d'un histogramme (règles de Sturges et de Freedman-Diaconis, essai de deux ou trois valeurs) et éviter trois pièges de lecture : la moyenne, l'axe tronqué, les trop nombreuses classes ;
- **explorer des relations** selon le type des deux variables (nuage et corrélation, boîtes et moyennes avec intervalle, tableaux croisés et profils, matrice de corrélation), et lire un **indicateur de force** comme le V de Cramér ;
- **reconnaître un facteur de confusion** (la saison) en comparant « à saison égale », et un **paradoxe de Simpson** (les jours de promotion rapportent moins en moyenne, mais plus à mois égal) ;
- **mesurer les motifs réguliers** (indice par jour de la semaine et par mois) et un **changement de niveau** à composition constante (la hausse de prix de 3 %) ;
- **détecter des incidents** avec une référence locale, un écart relatif et un score z robuste (MAD), **évaluer** la méthode par précision et rappel, et **distinguer** erreur, événement et régularité mal connue ;
- (en option) **dérouler une liste de contrôle** d'exploration, en automatiser le premier tour et rédiger le compte rendu d'une page.

Le tableau suivant résume **ce que nous avons mesuré** sur les données de la boutique, avec, quand elle est connue, la **vérité programmée**.

| Question | Résultat mesuré | Ce qu'il faut en retenir |
|---|---|---|
| Panier : moyenne et médiane | 100,4 € et 79,8 € ; asymétrie 1,85 | six commandes sur dix sont sous la moyenne ; annoncer la médiane |
| Règle des « 68 % » sur le panier | 78,2 % à moins d'un écart-type | l'écart-type ne se lit pas comme pour une cloche |
| Le panier, en logarithme | asymétrie −0,71 | l'échelle logarithmique ramène la forme vers une cloche |
| Classes d'un histogramme | 17 (Sturges) contre 177 (Freedman-Diaconis) | essayer deux ou trois valeurs |
| Délais de livraison | médiane 6 jours ; 96,2 % en 8 jours ou moins | pour un niveau de service, utiliser des centiles |
| Chiffre d'affaires annuel | 1 139, 1 189 puis 1 325 k€ (+4,4 % puis +11,4 %) | saison forte (février à décembre) et tendance |
| Corrélation publicité - commandes | 0,53 au total, 0,10 à mois égal | la saison explique l'essentiel du lien |
| Panier selon le canal | 100,9 ; 99,8 ; 100,5 € (intervalles qui se recouvrent) | pas de différence détectable entre canaux |
| Délai selon le transporteur | 5,2 ; 5,8 ; 6,7 jours (intervalles disjoints) | le transporteur C est nettement plus lent |
| Taux de retour par canal | 3,1 % ; 6,7 % ; 9,0 % (V de Cramér 0,118) | le canal compte pour les retours, pas pour les codes promo (0,010) |
| Promotion et chiffre d'affaires | 3 300 € contre 3 339 € au total, mais plus dans chaque mois comparable | paradoxe de Simpson : comparer à saison égale |
| Rythme hebdomadaire | samedi 1,39 fois la moyenne, dimanche 0,67 | une « journée typique » n'existe pas |
| Hausse de prix de 2025 | invisible dans le panier mensuel ; indice 1,000 puis 1,030 à produits constants | comparer à composition constante |
| Règle des 1,5 écart interquartile sur le chiffre d'affaires | 29 jours signalés, 90 % en novembre ou décembre | la saison fait de fausses alertes |
| Détection d'incidents (seuil 4) | 11 jours signalés, 6 vrais sur 8 : précision 55 %, rappel 75 % | un seuil est un arbitrage entre fausses alertes et incidents ratés |

Le fil conducteur du chapitre tient en une phrase : **avant de modéliser, regardez, dessinez et comparez des choses comparables**. Chaque résultat de l'exploration est une **question mieux posée** : *la publicité fait-elle vendre à saison égale ? Le transporteur C explique-t-il les retards ? La promotion augmente-t-elle les commandes de combien ?* Les chapitres suivants y répondent avec des outils qui mesurent l'incertitude : tests et A/B (chapitre 2), régression (chapitre 3), segmentation (chapitre 4), séries temporelles (chapitre 5).

> 🧭 **En pratique : liste de contrôle avant de passer à la suite.**
> 1. On sait ce que représente **une ligne** et ce qui l'identifie (1.0, 1.4).
> 2. Chaque variable importante a **sa phrase** (1.1) ; les montants ont été regardés en échelle logarithmique.
> 3. Les comparaisons de groupes ont des **intervalles**, et l'on a cherché la variable de confusion (1.2).
> 4. Les **rythmes** (semaine, saison) sont connus, les anomalies datées et **qualifiées** (erreur, événement, régularité) (1.3).
> 5. Le **compte rendu d'une page** est écrit (1.4).

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 à 1.7 (résumer le panier, choisir les classes, nuages et saison, comparer les groupes, profils hebdomadaires et indice de prix, détecter des incidents, rapport automatique) et exercices 1.1 à 1.14.

Le chapitre 2 aborde la question qui suit naturellement l'exploration : **cette différence est-elle réelle, ou due au hasard ?** C'est le sujet des tests d'hypothèses et des tests A/B.
