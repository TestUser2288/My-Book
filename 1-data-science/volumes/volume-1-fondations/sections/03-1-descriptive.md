## 3.1 Statistique descriptive

> 💡 **Intuition.** Avant de modéliser, de tester ou de prédire quoi que ce soit, on **regarde** les données. La statistique descriptive, c'est l'art de résumer un tableau de centaines de lignes en quelques nombres et quelques graphiques *fidèles*. C'est aussi la meilleure façon de repérer des erreurs de saisie, des valeurs aberrantes et des surprises, **avant** qu'elles ne faussent une analyse.

### 3.1.1 Population, échantillon, variables

Deux mots que nous utiliserons constamment :

- La **population** est l'ensemble complet qui nous intéresse (*toutes* les commandes passées et à venir de la boutique).
- L'**échantillon** est la partie que l'on a effectivement observée (nos 400 commandes).

On calcule des **statistiques** sur l'échantillon pour apprendre des choses sur les **paramètres** de la population, qui eux restent inconnus. (On notera $\bar x$ la moyenne de l'échantillon et $\mu$ celle de la population.)

Chaque colonne d'un tableau est une **variable**. Son type décide des calculs et des graphiques qui ont un sens :

| Type | Exemple | Résumés adaptés |
|---|---|---|
| **Quantitative continue** | montant (€) | moyenne, médiane, écart-type, histogramme |
| **Quantitative discrète** | nombre d'articles, délai en jours | idem, ou fréquences de chaque valeur |
| **Qualitative nominale** | canal (Réseaux / Site / Boutique) | effectifs, proportions, diagramme en barres |
| **Qualitative ordinale** | satisfaction (1 à 5) | effectifs, médiane, quantiles (la moyenne est discutable) |

> ⚠️ **La moyenne d'une variable ordinale** (satisfaction de 1 à 5) est très répandue mais n'a pas de sens strict : l'écart entre 1 et 2 est-il le même qu'entre 4 et 5 ? On la calcule quand même par convention, mais en gardant ceci en tête.

### 3.1.2 Charger et regarder le jeu de données

Voici la construction du jeu de données utilisé dans tout le chapitre. Vous n'avez pas besoin de comprendre chaque ligne maintenant : l'important est le **résultat**, un tableau de 400 commandes.

```python
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(100)
n = 400
canal = rng.choice(["Réseaux", "Site", "Boutique"], size=n, p=[0.4, 0.35, 0.25])
base = {"Réseaux": 3.7, "Site": 3.9, "Boutique": 4.1}
montant = np.round(np.exp(rng.normal([base[c] for c in canal], 0.55)), 1)
livraison = np.where(canal == "Boutique", 0, np.round(rng.gamma(4, 0.9, size=n)) + 1).astype(int)
satisfaction = np.clip(np.round(4.6 - 0.18 * livraison + rng.normal(0, 0.7, size=n)), 1, 5).astype(int)

df = pd.DataFrame({"canal": canal, "montant": montant,
                   "livraison": livraison, "satisfaction": satisfaction})
print(df.head(8))
print()
print("dimensions :", df.shape)
```
<!--sortie-->
```text
       canal  montant  livraison  satisfaction
0   Boutique     44.8          0             4
1       Site     34.5          2             4
2  Réseaux     88.2          5             4
3  Réseaux     30.1          4             4
4   Boutique    110.1          0             5
5       Site     39.8          5             3
6   Boutique     74.7          0             5
7   Boutique    108.7          0             4

dimensions : (400, 4)
```

Chaque ligne est une commande. `livraison` est le délai en jours (0 pour un retrait en boutique) et `satisfaction` une note de 1 à 5. Les trois premiers gestes à faire sur n'importe quel tableau :

```python
print(df.dtypes)                       # le type de chaque colonne
print()
print(df.isna().sum())                 # valeurs manquantes par colonne
print()
print(df.describe().round(2))          # résumé numérique
```
<!--sortie-->
```text
canal               str
montant         float64
livraison         int64
satisfaction      int64
dtype: object

canal           0
montant         0
livraison       0
satisfaction    0
dtype: int64

       montant  livraison  satisfaction
count   400.00     400.00        400.00
mean     60.25       3.29          3.96
std      38.02       2.56          0.80
min       8.60       0.00          1.00
25%      34.18       0.00          3.00
50%      51.00       3.00          4.00
75%      75.82       5.00          5.00
max     255.70      13.00          5.00
```

`describe()` donne d'un coup : effectif (`count`), moyenne (`mean`), écart-type (`std`), minimum, quartiles (25 %, 50 %, 75 %) et maximum. Aucune valeur manquante. Le montant moyen est d'environ 60 €, mais le **maximum dépasse 250 €** alors que la **médiane** (50 %) est d'environ 51 € : la distribution est probablement **asymétrique**. Regardons cela de plus près.

### 3.1.3 Mesures de position : où est le centre ?

**La moyenne** $\bar x=\frac1n\sum x_i$ est le centre de gravité. **La médiane** est la valeur qui partage l'échantillon en deux moitiés égales : 50 % des commandes sont en dessous. **Le mode** est la valeur la plus fréquente.

Voici un petit exemple à la main pour sentir la différence. Cinq commandes : $20,\ 25,\ 30,\ 35,\ 400$ € (la dernière est un gros achat professionnel). La moyenne vaut $(20+25+30+35+400)/5=102$ € : aucune commande n'est proche de ce chiffre ! La médiane (la valeur du milieu après tri) vaut 30 €, bien plus représentative d'une commande « typique ».

> 💡 **Règle de base.** La moyenne est sensible aux valeurs extrêmes ; la médiane est **robuste**. Quand la distribution est asymétrique, la moyenne est tirée vers la queue longue : **moyenne > médiane** pour une asymétrie à droite (cas des montants, revenus, durées).

```python
m = df["montant"]
print("moyenne :", round(m.mean(), 2))
print("médiane :", round(m.median(), 2))
print("moyenne tronquée (10 % de chaque côté) :", round(stats.trim_mean(m, 0.10), 2))
print("mode approximatif (classes de 10 €) :", int(m.round(-1).mode()[0]), "€")
```
<!--sortie-->
```text
moyenne : 60.25
médiane : 51.0
moyenne tronquée (10 % de chaque côté) : 54.9
mode approximatif (classes de 10 €) : 40 €
```

La moyenne (60 €) dépasse nettement la médiane (51 €) : quelques grosses commandes tirent la moyenne vers le haut. La **moyenne tronquée**, qui écarte les 10 % de valeurs les plus extrêmes de chaque côté, se situe entre les deux.

**Les quantiles** généralisent la médiane : le quantile à $q$ % est la valeur sous laquelle se trouvent $q$ % des observations. Les **quartiles** (25 %, 50 %, 75 %) découpent l'échantillon en quatre parts égales.

```python
print(m.quantile([0.05, 0.25, 0.50, 0.75, 0.95]).round(1))
```
<!--sortie-->
```text
0.05     19.0
0.25     34.2
0.50     51.0
0.75     75.8
0.95    128.6
Name: montant, dtype: float64
```

On lit par exemple : « 95 % des commandes font moins de ~130 € », une information très utile pour dimensionner un seuil de livraison gratuite.

### 3.1.4 Mesures de dispersion : de combien ça varie ?

Deux boutiques dont le panier moyen est de 60 € peuvent être très différentes si l'une a des paniers tous compris entre 55 et 65 et l'autre entre 5 et 300.

- **L'étendue** : max − min. Simple, mais entièrement dictée par deux valeurs extrêmes.
- **La variance** $s^2=\dfrac1{n-1}\sum(x_i-\bar x)^2$ et l'**écart-type** $s=\sqrt{s^2}$.
- **L'écart interquartile** (IQR) : $Q_3-Q_1$, l'étalement des 50 % du milieu. Robuste.
- **Le coefficient de variation** $s/\bar x$ : l'écart-type en proportion de la moyenne, sans unité, utile pour comparer des échelles différentes.

> ⚠️ **Pourquoi $n-1$ et pas $n$ ?** Pandas et NumPy ne donnent pas toujours la même chose : `pandas` divise par $n-1$ par défaut, `np.var` par $n$. Nous démontrons au 3.2 que $n-1$ est la bonne version pour **estimer** la variance de la population à partir d'un échantillon. Pour $n=400$ la différence est minime, mais pour $n=5$ elle est de 25 %.

```python
print("écart-type (pandas, n-1) :", round(m.std(), 2))
print("écart-type (numpy,  n)   :", round(np.std(m), 2))
print("étendue                  :", round(m.max() - m.min(), 1))
q1, q3 = m.quantile(0.25), m.quantile(0.75)
print("IQR                      :", round(q3 - q1, 1))
print("coefficient de variation :", round(m.std() / m.mean(), 2))
```
<!--sortie-->
```text
écart-type (pandas, n-1) : 38.02
écart-type (numpy,  n)   : 37.97
étendue                  : 247.1
IQR                      : 41.6
coefficient de variation : 0.63
```

Un écart-type de 38 € pour une moyenne de 60 € : un coefficient de variation de 63 %, ce qui est **très dispersé** (typique des montants).

### 3.1.5 La forme : histogrammes, asymétrie, boîtes à moustaches

Les nombres ne disent pas tout. **L'histogramme** découpe l'axe en classes et compte les observations dans chacune. La **boîte à moustaches** (*boxplot*) résume la distribution en cinq nombres : la boîte va du premier au troisième quartile, le trait central est la médiane, et les « moustaches » s'étendent jusqu'aux dernières valeurs situées à moins de $1{,}5\times\text{IQR}$ de la boîte ; les points au-delà sont signalés comme **valeurs atypiques** (*outliers*).

![À gauche : histogramme des 400 montants, avec la moyenne (orange) tirée vers la droite de la médiane (violet). À droite : boîtes à moustaches du montant selon le canal.](figures/ch03-distribution-montants.png)

On lit sur l'histogramme une **asymétrie à droite** : beaucoup de petites commandes, quelques très grosses. Sur le boxplot, la boutique a des commandes plus élevées que le site, lui-même plus élevé qu'Réseaux. (Est-ce une vraie différence ou du hasard d'échantillonnage ? C'est la question du 3.4.)

L'**asymétrie** (*skewness*) se mesure par un nombre : nulle pour une courbe symétrique, positive à droite.

```python
print("asymétrie :", round(stats.skew(m), 2))
q1, q3 = m.quantile([0.25, 0.75])
borne_haute = q3 + 1.5 * (q3 - q1)
print("seuil haut des valeurs atypiques :", round(borne_haute, 1), "€")
print("nombre de commandes au-dessus    :", int((m > borne_haute).sum()))
```
<!--sortie-->
```text
asymétrie : 1.75
seuil haut des valeurs atypiques : 138.3 €
nombre de commandes au-dessus    : 17
```

> 💡 **Que faire d'une valeur atypique ?** Surtout **ne pas la supprimer automatiquement**. Se demander : est-ce une *erreur* (saisie : 2 500 au lieu de 25,00) ? Alors on corrige. Est-ce une valeur *légitime* mais rare (gros client professionnel) ? Alors on la garde et on utilise des résumés robustes. Les valeurs atypiques sont souvent l'information la plus intéressante : un fraudeur, une panne, une opportunité.

**Transformer pour symétriser.** Pour des variables positives très asymétriques, le **logarithme** rapproche la forme d'une cloche :

```python
lm = np.log(m)
print("asymétrie du montant            :", round(stats.skew(m), 2))
print("asymétrie du logarithme         :", round(stats.skew(lm), 2))
print("moyenne et médiane de log(montant) :", round(lm.mean(), 2), round(lm.median(), 2))
```
<!--sortie-->
```text
asymétrie du montant            : 1.75
asymétrie du logarithme         : -0.07
moyenne et médiane de log(montant) : 3.92 3.93
```

Après transformation, l'asymétrie est presque nulle et moyenne ≈ médiane : le montant suit approximativement une loi **log-normale** (le logarithme est normal). Beaucoup de grandeurs économiques sont dans ce cas, car elles résultent de **multiplications** d'effets (là où la loi normale vient d'additions, TCL du 2.4).

### 3.1.6 Variables qualitatives et comparaison de groupes

Pour une variable catégorielle, on compte (**effectifs**) et on calcule des **proportions** (fréquences). Pour comparer des groupes, on utilise `groupby`.

```python
print(df["canal"].value_counts())
print()
print(df["canal"].value_counts(normalize=True).round(3))
print()
print(df.groupby("canal")["montant"].agg(["count", "mean", "median", "std"]).round(1))
```
<!--sortie-->
```text
canal
Site         148
Réseaux    138
Boutique     114
Name: count, dtype: int64

canal
Site         0.370
Réseaux    0.345
Boutique     0.285
Name: proportion, dtype: float64

           count  mean  median   std
canal                               
Boutique     114  74.8    64.8  40.6
Réseaux    138  49.0    41.5  31.1
Site         148  59.5    49.5  38.3
```

Les trois canaux apportent respectivement 138, 148 et 114 commandes (Réseaux, Site, Boutique). Les paniers moyens sont d'environ 49, 60 et 75 € : la boutique domine en valeur par commande. Mais attention :

> ⚠️ **Une différence observée n'est pas forcément une différence réelle.** Avec 114 à 148 commandes par canal, le hasard seul peut créer des écarts de quelques euros. Pour savoir si l'écart entre 49 et 75 € est « assez grand » pour être crédible, il faut un **test** (3.4) ou un **intervalle de confiance** (3.3). La statistique descriptive décrit ; elle ne *conclut* pas.

### 3.1.7 Relier deux variables : corrélation, et pourquoi il faut toujours dessiner

La **corrélation de Pearson** (2.3.3), calculée sur l'échantillon, mesure le lien *linéaire* entre deux variables quantitatives.

```python
print(df[["montant", "livraison", "satisfaction"]].corr().round(2))
```
<!--sortie-->
```text
              montant  livraison  satisfaction
montant          1.00      -0.20          0.07
livraison       -0.20       1.00         -0.53
satisfaction     0.07      -0.53          1.00
```

La corrélation entre le délai de livraison et la satisfaction est d'environ −0,53 : plus la livraison est lente, moins les clients sont satisfaits ; c'est cohérent avec le bon sens. En revanche, le montant n'est que faiblement lié à la satisfaction (+0,07).

**La corrélation de Spearman** est la corrélation de Pearson calculée sur les **rangs** (1er, 2e, 3e…). Elle détecte toute relation **monotone** (pas seulement linéaire) et résiste aux valeurs extrêmes.

```python
rho_s, _ = stats.spearmanr(df["livraison"], df["satisfaction"])
print("Spearman (livraison, satisfaction) :", round(rho_s, 2))
```
<!--sortie-->
```text
Spearman (livraison, satisfaction) : -0.51
```

> 🧪 **Le quartet d'Anscombe : pourquoi on dessine toujours.** En 1973, le statisticien Francis Anscombe a construit **quatre jeux de données** qui ont exactement les mêmes moyennes, variances, corrélation et droite de régression… mais des formes totalement différentes.

```python
x = [10, 8, 13, 9, 11, 14, 6, 4, 12, 7, 5]
ys = [[8.04, 6.95, 7.58, 8.81, 8.33, 9.96, 7.24, 4.26, 10.84, 4.82, 5.68],
      [9.14, 8.14, 8.74, 8.77, 9.26, 8.10, 6.13, 3.10, 9.13, 7.26, 4.74],
      [7.46, 6.77, 12.74, 7.11, 7.81, 8.84, 6.08, 5.39, 8.15, 6.42, 5.73],
      [6.58, 5.76, 7.71, 8.84, 8.47, 7.04, 5.25, 12.50, 5.56, 7.91, 6.89]]
xs = [x, x, x, [8] * 7 + [19] + [8] * 3]

for nom, a, b in zip(["I", "II", "III", "IV"], xs, ys):
    pente, ordonnee = np.polyfit(a, b, 1)
    print(f"jeu {nom:<3}: moy x = {np.mean(a):.2f}  moy y = {np.mean(b):.2f}  "
          f"corr = {np.corrcoef(a, b)[0, 1]:.3f}  droite : y = {pente:.2f} x + {ordonnee:.2f}")
```
<!--sortie-->
```text
jeu I  : moy x = 9.00  moy y = 7.50  corr = 0.816  droite : y = 0.50 x + 3.00
jeu II : moy x = 9.00  moy y = 7.50  corr = 0.816  droite : y = 0.50 x + 3.00
jeu III: moy x = 9.00  moy y = 7.50  corr = 0.816  droite : y = 0.50 x + 3.00
jeu IV : moy x = 9.00  moy y = 7.50  corr = 0.817  droite : y = 0.50 x + 3.00
```

Les quatre lignes sont quasiment identiques. Voici pourtant les quatre jeux :

![Le quartet d'Anscombe : mêmes statistiques, formes radicalement différentes. I : relation linéaire ordinaire. II : relation courbe. III : une valeur atypique fausse la droite. IV : un seul point (à droite) crée toute la corrélation.](figures/ch03-anscombe.png)

> ✅ **Règle d'or : on dessine d'abord, on calcule ensuite.** Un résumé numérique est une compression de l'information, avec perte. Seul un graphique révèle ce qui a été perdu.

> ✅ **À retenir (statistique descriptive).**
>
> - Population (inconnue) vs échantillon (observé) ; paramètres vs statistiques.
> - Position : moyenne (sensible aux extrêmes), médiane (robuste), quantiles. Dispersion : écart-type ($n-1$), IQR, coefficient de variation.
> - Montants, revenus, durées : souvent asymétriques à droite ; le logarithme symétrise. Ne supprimez pas les valeurs atypiques sans réfléchir.
> - Histogramme et boxplot pour la forme ; `groupby` pour comparer des groupes ; Pearson (linéaire) et Spearman (monotone) pour deux variables.
> - **Toujours tracer** (Anscombe). Une différence observée n'est pas encore une différence prouvée.
