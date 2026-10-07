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

```python hide
O.fig_panier()
```
<!--sortie-->
```text
figure : ch01-panier.png
```

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

```python hide
O.fig_classes()
```
<!--sortie-->
```text
figure : ch01-classes.png
```

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

```python hide
O.fig_delais()
```
<!--sortie-->
```text
figure : ch01-delais.png
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

```python hide
O.fig_barres()
```
<!--sortie-->
```text
figure : ch01-barres.png
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

```python hide
O.fig_serie_mensuelle()
```
<!--sortie-->
```text
figure : ch01-serie-mensuelle.png
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

```python hide
O.fig_axe_tronque()
```
<!--sortie-->
```text
figure : ch01-axe-tronque.png
```

![Le même panier moyen par année, avec un axe tronqué à 97 € puis un axe à zéro.](figures/ch01-axe-tronque.png)

À gauche, la barre de 2025 semble **presque trois fois** plus haute que celle de 2024 ; à droite, on voit une hausse de 3,5 %. Les deux dessins utilisent les mêmes nombres. Règle : **un diagramme en barres commence à zéro**. Pour une courbe, où l'on regarde la forme et non la hauteur, on peut resserrer l'axe, à condition de le dire.

**Le piège des trop nombreuses classes.** Un histogramme à 177 classes ou un diagramme à 30 barres ne montre plus une forme : il montre un bruit. Regroupez.

> ✅ **À retenir.** Une variable se **résume** (centre, dispersion, forme), se **dessine** (selon son type) et se **dit en une phrase**. La médiane, les quartiles et les centiles sont les résumés les plus sûrs d'une variable asymétrique ; le logarithme est l'outil des montants ; une barre commence à zéro ; une série se lit dans l'ordre.

> 📒 **Pour s'entraîner.** Cahier, chapitre 1 : applications 1.1 et 1.2, exercices 1.1 à 1.4.
