# Chapitre 3 : Statistique

> « Les probabilités vont de la **cause** vers les **données**.
> La statistique fait le chemin inverse : des **données** vers la cause. »

Au chapitre 2, nous *connaissions* la loi (par exemple « le taux de conversion est 20,5 % ») et nous calculions la probabilité d'observer certaines données. Dans la vie réelle, c'est l'inverse : on **observe** des données (400 commandes) et on veut deviner la loi (« quel est le vrai panier moyen ? Le canal Instagram est-il vraiment moins rentable que la boutique ? »). C'est le travail de la **statistique**.

## Le chemin de ce chapitre

- **3.1 Statistique descriptive** : résumer et regarder les données (moyenne, médiane, quantiles, graphiques) avant toute chose.
- **3.2 Estimation** : déduire un paramètre inconnu d'un échantillon (méthode des moments, maximum de vraisemblance), et juger la qualité d'un estimateur.
- **3.3 Intervalles de confiance** : ne pas donner un seul chiffre, mais une **fourchette** honnête.
- **3.4 Tests d'hypothèses** : décider, avec un risque maîtrisé, si un effet observé est réel ou dû au hasard (tests de moyenne, de proportion, du khi-deux, A/B).
- **3.5 p-valeurs, puissance et tests multiples** : bien interpréter les résultats, dimensionner une expérience, éviter les faux positifs.
- ➕ **Pour aller plus loin** : les sondages (comment échantillonner), et les méthodes non paramétriques (quand on ne veut pas supposer de loi).
- **3.8 Exercices corrigés**.

> 💡 **Le fil conducteur : un jeu de 400 commandes.** Tout au long du chapitre nous travaillons sur un même tableau de 400 commandes de Dar Jasmin (canal, montant, délai de livraison, satisfaction). Il est **simulé** (graine fixe) pour que vous puissiez reproduire chaque calcul, et vous verrez qu'on y retrouve des phénomènes tout à fait réalistes : montants asymétriques, différences entre canaux, lien entre délai et satisfaction.

> 🛠️ **Outils.** Nous utilisons `pandas` pour les tableaux (étudié en détail à la section 4.4 : ici on n'utilise que les gestes de base, expliqués au passage) et `scipy.stats` pour les calculs statistiques.


## 3.1 Statistique descriptive

> 💡 **Intuition.** Avant de modéliser, de tester ou de prédire quoi que ce soit, on **regarde** les données. La statistique descriptive, c'est l'art de résumer un tableau de centaines de lignes en quelques nombres et quelques graphiques *fidèles*. C'est aussi la meilleure façon de repérer des erreurs de saisie, des valeurs aberrantes et des surprises, **avant** qu'elles ne faussent une analyse.

### 3.1.1 Population, échantillon, variables

Deux mots que nous utiliserons constamment :

- La **population** est l'ensemble complet qui nous intéresse (*toutes* les commandes passées et à venir de Dar Jasmin).
- L'**échantillon** est la partie que l'on a effectivement observée (nos 400 commandes).

On calcule des **statistiques** sur l'échantillon pour apprendre des choses sur les **paramètres** de la population, qui eux restent inconnus. (On notera $\bar x$ la moyenne de l'échantillon et $\mu$ celle de la population.)

Chaque colonne d'un tableau est une **variable**. Son type décide des calculs et des graphiques qui ont un sens :

| Type | Exemple | Résumés adaptés |
|---|---|---|
| **Quantitative continue** | montant (DT) | moyenne, médiane, écart-type, histogramme |
| **Quantitative discrète** | nombre d'articles, délai en jours | idem, ou fréquences de chaque valeur |
| **Qualitative nominale** | canal (Instagram / Site / Boutique) | effectifs, proportions, diagramme en barres |
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
canal = rng.choice(["Instagram", "Site", "Boutique"], size=n, p=[0.4, 0.35, 0.25])
base = {"Instagram": 3.7, "Site": 3.9, "Boutique": 4.1}
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
2  Instagram     88.2          5             4
3  Instagram     30.1          4             4
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

`describe()` donne d'un coup : effectif (`count`), moyenne (`mean`), écart-type (`std`), minimum, quartiles (25 %, 50 %, 75 %) et maximum. Aucune valeur manquante. Le montant moyen est d'environ 60 DT, mais le **maximum dépasse 250 DT** alors que la **médiane** (50 %) est d'environ 51 DT : la distribution est probablement **asymétrique**. Regardons cela de plus près.

### 3.1.3 Mesures de position : où est le centre ?

**La moyenne** $\bar x=\frac1n\sum x_i$ est le centre de gravité. **La médiane** est la valeur qui partage l'échantillon en deux moitiés égales : 50 % des commandes sont en dessous. **Le mode** est la valeur la plus fréquente.

Voici un petit exemple à la main pour sentir la différence. Cinq commandes : $20,\ 25,\ 30,\ 35,\ 400$ DT (la dernière est un gros achat professionnel). La moyenne vaut $(20+25+30+35+400)/5=102$ DT : aucune commande n'est proche de ce chiffre ! La médiane (la valeur du milieu après tri) vaut 30 DT, bien plus représentative d'une commande « typique ».

> 💡 **Règle de base.** La moyenne est sensible aux valeurs extrêmes ; la médiane est **robuste**. Quand la distribution est asymétrique, la moyenne est tirée vers la queue longue : **moyenne > médiane** pour une asymétrie à droite (cas des montants, revenus, durées).

```python
m = df["montant"]
print("moyenne :", round(m.mean(), 2))
print("médiane :", round(m.median(), 2))
print("moyenne tronquée (10 % de chaque côté) :", round(stats.trim_mean(m, 0.10), 2))
print("mode approximatif (classes de 10 DT) :", int(m.round(-1).mode()[0]), "DT")
```
<!--sortie-->
```text
moyenne : 60.25
médiane : 51.0
moyenne tronquée (10 % de chaque côté) : 54.9
mode approximatif (classes de 10 DT) : 40 DT
```

La moyenne (60 DT) dépasse nettement la médiane (51 DT) : quelques grosses commandes tirent la moyenne vers le haut. La **moyenne tronquée**, qui écarte les 10 % de valeurs les plus extrêmes de chaque côté, se situe entre les deux.

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

On lit par exemple : « 95 % des commandes font moins de ~130 DT », une information très utile pour dimensionner un seuil de livraison gratuite.

### 3.1.4 Mesures de dispersion : de combien ça varie ?

Deux boutiques dont le panier moyen est de 60 DT peuvent être très différentes si l'une a des paniers tous compris entre 55 et 65 et l'autre entre 5 et 300.

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

Un écart-type de 38 DT pour une moyenne de 60 DT : un coefficient de variation de 63 %, ce qui est **très dispersé** (typique des montants).

### 3.1.5 La forme : histogrammes, asymétrie, boîtes à moustaches

Les nombres ne disent pas tout. **L'histogramme** découpe l'axe en classes et compte les observations dans chacune. La **boîte à moustaches** (*boxplot*) résume la distribution en cinq nombres : la boîte va du premier au troisième quartile, le trait central est la médiane, et les « moustaches » s'étendent jusqu'aux dernières valeurs situées à moins de $1{,}5\times\text{IQR}$ de la boîte ; les points au-delà sont signalés comme **valeurs atypiques** (*outliers*).

![À gauche : histogramme des 400 montants, avec la moyenne (orange) tirée vers la droite de la médiane (violet). À droite : boîtes à moustaches du montant selon le canal.](figures/ch03-distribution-montants.png)

On lit sur l'histogramme une **asymétrie à droite** : beaucoup de petites commandes, quelques très grosses. Sur le boxplot, la boutique a des commandes plus élevées que le site, lui-même plus élevé qu'Instagram. (Est-ce une vraie différence ou du hasard d'échantillonnage ? C'est la question du 3.4.)

L'**asymétrie** (*skewness*) se mesure par un nombre : nulle pour une courbe symétrique, positive à droite.

```python
print("asymétrie :", round(stats.skew(m), 2))
q1, q3 = m.quantile([0.25, 0.75])
borne_haute = q3 + 1.5 * (q3 - q1)
print("seuil haut des valeurs atypiques :", round(borne_haute, 1), "DT")
print("nombre de commandes au-dessus    :", int((m > borne_haute).sum()))
```
<!--sortie-->
```text
asymétrie : 1.75
seuil haut des valeurs atypiques : 138.3 DT
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
Instagram    138
Boutique     114
Name: count, dtype: int64

canal
Site         0.370
Instagram    0.345
Boutique     0.285
Name: proportion, dtype: float64

           count  mean  median   std
canal                               
Boutique     114  74.8    64.8  40.6
Instagram    138  49.0    41.5  31.1
Site         148  59.5    49.5  38.3
```

Les trois canaux apportent respectivement 138, 148 et 114 commandes (Instagram, Site, Boutique). Les paniers moyens sont d'environ 49, 60 et 75 DT : la boutique domine en valeur par commande. Mais attention :

> ⚠️ **Une différence observée n'est pas forcément une différence réelle.** Avec 114 à 148 commandes par canal, le hasard seul peut créer des écarts de quelques dinars. Pour savoir si l'écart entre 49 et 75 DT est « assez grand » pour être crédible, il faut un **test** (3.4) ou un **intervalle de confiance** (3.3). La statistique descriptive décrit ; elle ne *conclut* pas.

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


## 3.2 Estimation

> 💡 **Intuition.** La population a des paramètres (un panier moyen $\mu$, un taux de conversion $p$, un taux d'arrivée $\lambda$) que personne ne connaît. À partir d'un **échantillon**, on fabrique une **estimation**. La formule qui transforme l'échantillon en estimation s'appelle un **estimateur**. Il y a toujours plusieurs estimateurs possibles ; la question est : **lequel choisir, et à quel point peut-on lui faire confiance ?**

### 3.2.1 Un estimateur est une variable aléatoire

Notons $\theta$ un paramètre inconnu (n'importe lequel) et $\hat\theta$ (« thêta chapeau ») son estimateur. Comme l'échantillon est aléatoire, $\hat\theta$ **l'est aussi** : un autre échantillon donnerait une autre estimation. C'est exactement l'idée de la moyenne d'échantillon $\bar X_n$ au 2.4.1.

On peut le **voir** en jouant à Dieu : traitons nos 400 commandes comme *toute* la population (de moyenne connue) et tirons dedans des échantillons de 30 commandes, en recalculant la moyenne à chaque fois.

```python
import numpy as np
import pandas as pd
from scipy import stats
from scipy import optimize

rng = np.random.default_rng(11)
population = df["montant"].to_numpy()
print("moyenne de la 'population' :", round(population.mean(), 2))

moyennes = np.array([rng.choice(population, size=30, replace=False).mean() for _ in range(10_000)])
print("moyenne des 10 000 moyennes d'échantillons :", round(moyennes.mean(), 2))
print("écart-type de ces moyennes (erreur-type)    :", round(moyennes.std(), 2))
print("théorie sigma/sqrt(n)                       :", round(population.std() / np.sqrt(30), 2))
print("3 échantillons au hasard :", [round(float(rng.choice(population, 30).mean()), 1) for _ in range(3)])
```
<!--sortie-->
```text
moyenne de la 'population' : 60.25
moyenne des 10 000 moyennes d'échantillons : 60.3
écart-type de ces moyennes (erreur-type)    : 6.59
théorie sigma/sqrt(n)                       : 6.93
3 échantillons au hasard : [54.2, 59.5, 60.3]
```

Chaque échantillon de 30 commandes donne une moyenne différente (ci-dessus : 54,2 ; 59,5 ; 60,3), mais **en moyenne** ces moyennes tombent sur la vraie valeur (60,25), avec une dispersion de l'ordre de 7 DT. Cette dispersion est l'**erreur-type** : elle mesure la précision de l'estimateur. (Le petit écart avec la théorie vient du tirage **sans remise** dans une population finie.)

### 3.2.2 Qu'est-ce qu'un bon estimateur ?

On juge un estimateur sur trois critères, que l'on comprend très bien avec l'image d'un tir à la cible :

- **Le biais** : $\operatorname{Biais}(\hat\theta)=E[\hat\theta]-\theta$. Les tirs sont-ils centrés sur la cible, ou systématiquement décalés ? Un estimateur est **sans biais** si ce biais vaut 0.
- **La variance** : $\operatorname{Var}(\hat\theta)$. Les tirs sont-ils groupés ou dispersés ?
- **La cohérence** (ou *consistance*) : l'estimateur converge-t-il vers $\theta$ quand $n\to\infty$ ? (La loi des grands nombres l'assure pour la moyenne.)

Un bon estimateur est à la fois **peu biaisé** et **peu variable**. On les combine dans l'**erreur quadratique moyenne** :

> 📐 **Décomposition biais–variance.**
> $$\operatorname{EQM}(\hat\theta)=E\bigl[(\hat\theta-\theta)^2\bigr]=\operatorname{Var}(\hat\theta)+\operatorname{Biais}(\hat\theta)^2.$$
>
> *Preuve.* Notons $m=E[\hat\theta]$. On écrit $\hat\theta-\theta=(\hat\theta-m)+(m-\theta)$ et on développe le carré :
> $$E[(\hat\theta-\theta)^2]=E[(\hat\theta-m)^2]+2(m-\theta)\,E[\hat\theta-m]+(m-\theta)^2.$$
> Le terme du milieu est nul car $E[\hat\theta-m]=0$. Il reste $\operatorname{Var}(\hat\theta)+(m-\theta)^2$. $\blacksquare$

Cette formule a une conséquence profonde, qui reviendra tout au long du volume II : **accepter un petit biais peut réduire l'erreur totale si cela réduit beaucoup la variance**. C'est le principe de la régularisation en apprentissage automatique.

### 3.2.3 Pourquoi divise-t-on par $n-1$ pour la variance ?

Nous avons promis cette démonstration (3.1.4 et 2.3.3). Soit $X_1,\dots,X_n$ i.i.d. de moyenne $\mu$ et de variance $\sigma^2$. L'estimateur « naturel » de $\sigma^2$ est $\hat\sigma^2_n=\frac1n\sum(X_i-\bar X)^2$. Est-il sans biais ?

> 📐 **Calcul.** On insère $\mu$ : $X_i-\bar X=(X_i-\mu)-(\bar X-\mu)$. Alors
>
> $$\sum_i(X_i-\bar X)^2=\sum_i(X_i-\mu)^2-n(\bar X-\mu)^2.$$
>
> (En développant : $\sum(X_i-\mu)^2-2(\bar X-\mu)\sum(X_i-\mu)+n(\bar X-\mu)^2$ et $\sum(X_i-\mu)=n(\bar X-\mu)$, d'où le résultat.) Prenons l'espérance : $E[(X_i-\mu)^2]=\sigma^2$ et $E[(\bar X-\mu)^2]=\operatorname{Var}(\bar X)=\sigma^2/n$. Donc
>
> $$E\Bigl[\sum_i(X_i-\bar X)^2\Bigr]=n\sigma^2-n\cdot\frac{\sigma^2}n=(n-1)\,\sigma^2.$$
>
> Par conséquent $E[\hat\sigma^2_n]=\dfrac{n-1}n\sigma^2<\sigma^2$ : l'estimateur « divisé par $n$ » **sous-estime** la variance. Pour corriger, on divise par $n-1$ :
> $$S^2=\frac1{n-1}\sum_i(X_i-\bar X)^2,\qquad E[S^2]=\sigma^2.\ \blacksquare$$

> 💡 **Pourquoi intuitivement ?** Les données sont toujours plus proches de **leur propre** moyenne $\bar X$ que de la vraie moyenne $\mu$ (car $\bar X$ est justement construite pour être au centre des données). Mesurer les écarts à $\bar X$ sous-estime donc légèrement les écarts à $\mu$. L'échantillon a aussi « perdu un degré de liberté » : une fois $\bar X$ calculée, seules $n-1$ valeurs sont libres, la dernière est imposée.

Voyons-le sur ordinateur pour de **tout petits** échantillons ($n=5$), où l'effet est maximal (vraie variance = 1) :

```python
rng = np.random.default_rng(3)
x = rng.normal(0, 1, size=(100_000, 5))                 # 100 000 échantillons de taille 5
v_n = x.var(axis=1, ddof=0).mean()                      # divisé par n
v_n1 = x.var(axis=1, ddof=1).mean()                     # divisé par n-1
print("moyenne des estimations, division par n   :", round(v_n, 3), "  (théorie (n-1)/n = 0.8)")
print("moyenne des estimations, division par n-1 :", round(v_n1, 3))
```
<!--sortie-->
```text
moyenne des estimations, division par n   : 0.801   (théorie (n-1)/n = 0.8)
moyenne des estimations, division par n-1 : 1.001
```

![Distribution des estimations de la variance sur 100 000 échantillons de taille 5 : en divisant par n, on sous-estime en moyenne (0,80) ; en divisant par n−1, on est centré sur la vraie valeur (1).](figures/ch03-biais-variance.png)

> ⚠️ **Subtilité.** $S^2$ est sans biais pour la **variance**, mais $S=\sqrt{S^2}$ reste (très légèrement) biaisé pour l'écart-type, car la racine carrée n'est pas linéaire. Ce biais est négligeable en pratique.

### 3.2.4 La méthode des moments

> 💡 **Idée.** Les paramètres d'une loi s'expriment à l'aide de ses moments (espérance, variance…). La **méthode des moments** consiste à **égaler les moments théoriques aux moments observés** et à résoudre. C'est simple et intuitif.

**Exemple 1 : le taux d'arrivée.** Les temps (en minutes) séparant 25 commandes successives suivent une loi exponentielle de paramètre $\lambda$ inconnu. On sait que $E[T]=1/\lambda$. On égale à la moyenne observée $\bar t$ : $1/\hat\lambda=\bar t$, donc $\hat\lambda=1/\bar t$.

```python
rng = np.random.default_rng(7)
attentes = rng.exponential(scale=2.0, size=25)          # vraie valeur : lambda = 0.5 par minute (moyenne 2 min)
print("moyenne observée   :", round(attentes.mean(), 3), "minutes")
print("lambda estimé (1/moyenne) :", round(1 / attentes.mean(), 3), "(vraie valeur : 0.5)")
```
<!--sortie-->
```text
moyenne observée   : 1.988 minutes
lambda estimé (1/moyenne) : 0.503 (vraie valeur : 0.5)
```

**Exemple 2 : une loi à deux paramètres.** Les montants sont modélisés par une loi **Gamma** de forme $k$ et d'échelle $\theta$, avec $E[X]=k\theta$ et $\operatorname{Var}(X)=k\theta^2$. En égalant à la moyenne $\bar x$ et à la variance $s^2$ observées, on obtient deux équations : $\hat\theta=s^2/\bar x$ et $\hat k=\bar x^2/s^2$.

```python
xbar, s2 = m.mean(), m.var()
theta_mom = s2 / xbar
k_mom = xbar**2 / s2
print("Gamma par les moments : k =", round(k_mom, 3), "  theta =", round(theta_mom, 2))
```
<!--sortie-->
```text
Gamma par les moments : k = 2.511   theta = 23.99
```

La méthode des moments est rapide, mais elle n'est pas toujours la plus précise. La suivante est la référence.

### 3.2.5 Le maximum de vraisemblance

> 💡 **Intuition.** Yasmine lance une nouvelle promotion et observe 7 achats sur 20 visiteurs. Quelle valeur du taux de conversion $p$ rend ces données **les plus plausibles** ? Si $p$ valait 0,05, observer 7 acheteurs sur 20 serait très improbable ; si $p$ valait 0,9, tout autant. Il existe une valeur intermédiaire pour laquelle ce résultat est **le moins surprenant possible** : c'est l'estimation du maximum de vraisemblance.

**La vraisemblance** $L(\theta)$ est la probabilité (ou la densité) d'observer **les données effectivement observées**, vue comme une fonction du paramètre $\theta$. Pour des observations indépendantes $x_1,\dots,x_n$ :

$$L(\theta)=\prod_{i=1}^n f(x_i;\theta).$$

L'estimateur du maximum de vraisemblance (EMV, *MLE*) est la valeur $\hat\theta$ qui **maximise** $L(\theta)$. Comme les produits sont pénibles à dériver et numériquement instables (le produit de nombreuses probabilités minuscules s'écrase vers 0), on maximise plutôt le **logarithme** de la vraisemblance, qui transforme le produit en somme et a le même maximum (le logarithme est croissant) :

$$\ell(\theta)=\ln L(\theta)=\sum_{i=1}^n\ln f(x_i;\theta).$$

C'est de l'optimisation (section 1.3) : on dérive et on annule.

> 📐 **Exemple complet : le taux de conversion.** On observe $k$ achats sur $n$ visiteurs. Le modèle est binomial : $L(p)=\binom nk p^k(1-p)^{n-k}$, donc
>
> $$\ell(p)=\ln\tbinom nk+k\ln p+(n-k)\ln(1-p).$$
>
> On dérive : $\ell'(p)=\dfrac kp-\dfrac{n-k}{1-p}$. En annulant : $k(1-p)=(n-k)p\iff k=np$, d'où
>
> $$\hat p=\frac kn.$$
>
> La dérivée seconde $\ell''(p)=-\frac k{p^2}-\frac{n-k}{(1-p)^2}<0$ : c'est bien un **maximum**. $\blacksquare$
>
> L'estimateur du maximum de vraisemblance est donc tout simplement la **proportion observée**, ce qui rassure : la méthode retrouve le bon sens.

Pour $k=7$, $n=20$ : $\hat p=0{,}35$. La figure montre la vraisemblance et la log-vraisemblance en fonction de $p$ ; le maximum est atteint en $0{,}35$, et la log-vraisemblance est une courbe en cloche inversée, bien plus facile à optimiser.

![Vraisemblance (à gauche) et log-vraisemblance (à droite) pour 7 achats sur 20 visiteurs. Le maximum est en p = 0,35.](figures/ch03-vraisemblance.png)

Vérifions par calcul numérique : on cherche le maximum sur une grille, puis avec un optimiseur (la méthode générale quand il n'y a pas de formule).

```python
k, n_obs = 7, 20
grille = np.linspace(0.001, 0.999, 999)
loglik = stats.binom.logpmf(k, n_obs, grille)
print("maximum sur une grille :", round(grille[np.argmax(loglik)], 3))

# optimiseur : on minimise la log-vraisemblance NÉGATIVE
res = optimize.minimize_scalar(lambda p: -stats.binom.logpmf(k, n_obs, p), bounds=(0.001, 0.999), method="bounded")
print("optimiseur             :", round(res.x, 4))
```
<!--sortie-->
```text
maximum sur une grille : 0.35
optimiseur             : 0.35
```

**D'autres exemples classiques** (mêmes calculs, à faire en exercice) :

| Modèle | Estimateur du maximum de vraisemblance |
|---|---|
| Bernoulli / binomiale | $\hat p=\bar x$ (proportion observée) |
| Poisson$(\lambda)$ | $\hat\lambda=\bar x$ |
| Exponentielle$(\lambda)$ | $\hat\lambda=1/\bar x$ |
| Normale$(\mu,\sigma^2)$ | $\hat\mu=\bar x$ ; $\hat\sigma^2=\frac1n\sum(x_i-\bar x)^2$ (⚠️ divisé par $n$ : biaisé !) |

On retrouve pour l'exponentielle la même formule qu'avec les moments. Remarquez la dernière ligne : l'EMV de la variance divise par $n$, donc est **légèrement biaisé**. Le maximum de vraisemblance n'est pas toujours sans biais ; il a d'autres qualités.

**Quand il n'y a pas de formule : l'optimisation numérique.** Pour la loi Gamma des montants, on ne peut pas résoudre à la main. On confie la log-vraisemblance à un optimiseur, exactement comme au chapitre 1 (la descente de gradient en est l'ancêtre) :

```python
def neg_loglik_gamma(params, x):
    k, theta = params
    if k <= 0 or theta <= 0:
        return np.inf
    return -stats.gamma.logpdf(x, a=k, scale=theta).sum()

res = optimize.minimize(neg_loglik_gamma, x0=[k_mom, theta_mom], args=(m.to_numpy(),), method="Nelder-Mead")
k_mle, theta_mle = res.x
print("Gamma par maximum de vraisemblance : k =", round(k_mle, 3), " theta =", round(theta_mle, 2))
print("Gamma par moments                  : k =", round(k_mom, 3), " theta =", round(theta_mom, 2))
print("log-vraisemblance maximale :", round(-res.fun, 1))
print("log-vraisemblance (moments):", round(-neg_loglik_gamma([k_mom, theta_mom], m.to_numpy()), 1))
```
<!--sortie-->
```text
Gamma par maximum de vraisemblance : k = 3.001  theta = 20.07
Gamma par moments                  : k = 2.511  theta = 23.99
log-vraisemblance maximale : -1938.9
log-vraisemblance (moments): -1942.2
```

Le maximum de vraisemblance trouve des paramètres de log-vraisemblance **plus élevée** que ceux des moments (c'est sa définition : il est le meilleur *pour les données observées*). Ici les deux approches donnent des valeurs du même ordre (la forme passe de 2,5 à 3,0). N'oubliez pas qu'une loi Gamma n'est qu'un **modèle** des montants parmi d'autres (on a vu au 3.1.5 qu'une loi log-normale convient aussi bien) : estimer les paramètres ne dit pas si le modèle est juste. Notez aussi que la bibliothèque sait faire tout cela d'un coup :

```python
k_sp, loc_sp, theta_sp = stats.gamma.fit(m, floc=0)       # floc=0 : on impose une borne inférieure à 0
print("scipy.stats.gamma.fit :", round(k_sp, 3), round(theta_sp, 2))
```
<!--sortie-->
```text
scipy.stats.gamma.fit : 3.001 20.07
```

### 3.2.6 Pourquoi le maximum de vraisemblance est la référence

Sous des conditions de régularité raisonnables, l'EMV a quatre propriétés remarquables, que l'on admettra :

1. **Cohérent** : $\hat\theta\to\theta$ quand $n\to\infty$.
2. **Asymptotiquement normal** : $\hat\theta\approx\mathcal N\bigl(\theta,\ 1/(nI(\theta))\bigr)$ pour $n$ grand, où $I(\theta)$ est l'**information de Fisher** (la courbure moyenne de la log-vraisemblance autour du maximum : plus le pic est pointu, plus on est précis).
3. **Asymptotiquement efficace** : parmi les estimateurs cohérents, il a (presque) la plus petite variance possible.
4. **Invariant par reparamétrisation** : si $\hat\theta$ est l'EMV de $\theta$, alors $g(\hat\theta)$ est l'EMV de $g(\theta)$.

Le point 2 donne directement l'**erreur-type** : pour la proportion, $I(p)=\frac1{p(1-p)}$, donc

$$\operatorname{SE}(\hat p)=\sqrt{\frac{\hat p(1-\hat p)}n}.$$

```python
p_hat, n_obs = 7 / 20, 20
se = np.sqrt(p_hat * (1 - p_hat) / n_obs)
print("p chapeau =", p_hat, "  erreur-type =", round(se, 3))
print("avec 10 fois plus de données (70/200) :", round(np.sqrt(0.35 * 0.65 / 200), 3))
```
<!--sortie-->
```text
p chapeau = 0.35   erreur-type = 0.107
avec 10 fois plus de données (70/200) : 0.034
```

Avec 20 visiteurs, l'erreur-type est de 0,107 (près de 11 points !) : $\hat p=0{,}35$ est très imprécis. Avec 200 visiteurs, elle tombe à 0,034. Estimer, c'est bien ; **chiffrer l'incertitude de l'estimation** est mieux : c'est l'objet de la section suivante.

> ✅ **À retenir (estimation).**
>
> - Un **estimateur** est une formule appliquée à l'échantillon ; c'est une variable aléatoire dont on étudie le **biais**, la **variance**, la **cohérence**. $\operatorname{EQM}=\operatorname{Var}+\operatorname{Biais}^2$.
> - $\bar X$ est sans biais pour $\mu$, et **$S^2$ (divisé par $n-1$)** est sans biais pour $\sigma^2$ (preuve en 3.2.3).
> - **Moments** : on égale moments théoriques et observés. **Maximum de vraisemblance** : on maximise $\ell(\theta)=\sum\ln f(x_i;\theta)$ ; formule fermée si possible, optimiseur sinon.
> - Pour une proportion, l'EMV est la fréquence observée, d'erreur-type $\sqrt{\hat p(1-\hat p)/n}$.
> - L'EMV est cohérent, asymptotiquement normal et efficace : c'est l'outil standard.


## 3.3 Intervalles de confiance

> 💡 **Intuition.** Dire « le panier moyen est de 60,25 DT » est trompeur : cela suggère une précision que l'on n'a pas. Un meilleur énoncé est : « le panier moyen se situe, avec une confiance de 95 %, entre 56,5 et 64,0 DT ». L'**intervalle de confiance** (IC) transforme une estimation ponctuelle en une **fourchette honnête**, dont la largeur reflète l'incertitude.

### 3.3.1 Construire un intervalle pour une moyenne

Rappelons ce que nous savons (2.4) : par le théorème central limite, $\bar X_n\approx\mathcal N(\mu,\ \sigma^2/n)$. Donc le score centré réduit $\dfrac{\bar X_n-\mu}{\sigma/\sqrt n}$ suit à peu près $\mathcal N(0,1)$, et comme $P(-1{,}96\le Z\le1{,}96)=0{,}95$ :

> 📐 **Construction.**
>
> $$P\Bigl(-1{,}96\le\frac{\bar X_n-\mu}{\sigma/\sqrt n}\le1{,}96\Bigr)=0{,}95.$$
>
> On isole $\mu$ au milieu de l'encadrement : multiplier par $\sigma/\sqrt n$, puis soustraire $\bar X_n$ et multiplier par $-1$ (ce qui renverse les inégalités) :
>
> $$P\Bigl(\bar X_n-1{,}96\frac{\sigma}{\sqrt n}\ \le\ \mu\ \le\ \bar X_n+1{,}96\frac{\sigma}{\sqrt n}\Bigr)=0{,}95.$$
>
> L'**intervalle de confiance à 95 %** est donc $\bar x\pm1{,}96\,\dfrac{\sigma}{\sqrt n}$. $\blacksquare$

Il a une structure à retenir absolument, qui se retrouvera partout :

$$\text{estimation}\ \pm\ \text{(valeur critique)}\times\text{(erreur-type)}.$$

**Exemple à la main.** Sur 400 commandes, $\bar x=60{,}25$ DT et $s=38{,}02$. L'erreur-type est $38{,}02/\sqrt{400}=1{,}90$. L'IC à 95 % est $60{,}25\pm1{,}96\times1{,}90=60{,}25\pm3{,}73$, soit **[56,5 ; 64,0]** DT.

### 3.3.2 Que veut dire « 95 % de confiance » ?

C'est la phrase la plus mal comprise de la statistique. Elle ne signifie **pas** « il y a 95 % de chances que la vraie moyenne soit dans cet intervalle-ci ». La vraie moyenne $\mu$ est un nombre **fixe** (inconnu) : elle y est ou elle n'y est pas. Ce qui est aléatoire, c'est l'**intervalle** (il change à chaque échantillon).

> 💡 **La bonne lecture :** *si l'on répétait l'expérience un très grand nombre de fois, avec un nouvel échantillon à chaque fois, 95 % des intervalles ainsi construits contiendraient la vraie valeur.* La confiance porte sur la **méthode**, pas sur un intervalle particulier.

Voyons-le. Soixante échantillons de 40 commandes, un intervalle à 95 % pour chacun, et la vraie moyenne (connue ici car on traite nos 400 commandes comme la population) en pointillés :

![60 intervalles de confiance à 95 % construits sur 60 échantillons différents de 40 commandes. Les intervalles en rouge n'atteignent pas la vraie moyenne : environ 1 sur 20 en moyenne (5 sur 60 ici, une fluctuation normale).](figures/ch03-couverture.png)

Mesurons-le précisément, sur 20 000 échantillons :

```python
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(21)
population = df["montant"].to_numpy()
mu = population.mean()
n_ech, essais = 40, 20_000
t_crit = stats.t.ppf(0.975, n_ech - 1)

couvre = 0
largeurs = []
for _ in range(essais):
    e = rng.choice(population, size=n_ech, replace=False)
    se = e.std(ddof=1) / np.sqrt(n_ech)
    lo, hi = e.mean() - t_crit * se, e.mean() + t_crit * se
    couvre += (lo <= mu <= hi)
    largeurs.append(hi - lo)
print("part des intervalles contenant la vraie moyenne :", round(couvre / essais, 4))
print("largeur moyenne :", round(np.mean(largeurs), 2), "DT")
```
<!--sortie-->
```text
part des intervalles contenant la vraie moyenne : 0.9451
largeur moyenne : 23.88 DT
```

La couverture est proche de 95 % (un peu moins : la loi des montants est asymétrique et $n=40$ est modeste ; nous reviendrons sur ces limites). L'idée est donc validée.

> ⚠️ **Deux erreurs d'interprétation à éviter.**
> 1. « La vraie valeur a 95 % de chances d'être dans [56,5 ; 64,0] » : formulation courante, rigoureusement fausse dans l'approche fréquentiste (dans l'approche bayésienne, elle est correcte pour un *intervalle de crédibilité*).
> 2. « 95 % des **commandes** sont dans cet intervalle » : confusion entre la précision de la **moyenne** et la dispersion des **données**. L'IC de la moyenne est étroit ([56,5 ; 64,0]), alors que 95 % des commandes sont entre 19 et 129 DT (3.1.3).

### 3.3.3 Quand l'écart-type est inconnu : la loi de Student

En pratique, on ne connaît **pas** $\sigma$ ; on le remplace par son estimation $s$. Mais $s$ est elle-même aléatoire, ce qui ajoute de l'incertitude : pour de petits échantillons, on tomberait trop souvent à côté avec la valeur 1,96. William Gosset (qui signait « Student » en 1908, alors qu'il travaillait dans une brasserie Guinness) a montré que la bonne loi pour $\dfrac{\bar X-\mu}{S/\sqrt n}$ est la **loi de Student à $n-1$ degrés de liberté** (si les données sont à peu près normales).

C'est une cloche comme la normale, mais avec des **queues plus lourdes** (plus de prudence), qui tend vers $\mathcal N(0,1)$ quand $n$ augmente :

```python
for ddl in (2, 5, 10, 30, 100, 1000):
    print(f"degrés de liberté = {ddl:>4} : valeur critique à 95 % = {stats.t.ppf(0.975, ddl):.3f}")
print("loi normale                      :", round(stats.norm.ppf(0.975), 3))
```
<!--sortie-->
```text
degrés de liberté =    2 : valeur critique à 95 % = 4.303
degrés de liberté =    5 : valeur critique à 95 % = 2.571
degrés de liberté =   10 : valeur critique à 95 % = 2.228
degrés de liberté =   30 : valeur critique à 95 % = 2.042
degrés de liberté =  100 : valeur critique à 95 % = 1.984
degrés de liberté = 1000 : valeur critique à 95 % = 1.962
loi normale                      : 1.96
```

Avec 2 degrés de liberté (3 observations), la valeur critique est 4,30 : l'intervalle est plus de deux fois plus large qu'avec 1,96. Dès 30 degrés de liberté, on est proche de 2,04 ; avec 400 observations, la différence avec 1,96 est imperceptible.

L'intervalle devient $\bar x\pm t_{n-1,\,0{,}975}\dfrac{s}{\sqrt n}$. Voici le calcul pour nos 400 commandes, à la main puis avec `scipy` :

```python
m = df["montant"]
n = len(m)
xbar, s = m.mean(), m.std(ddof=1)
se = s / np.sqrt(n)
t_crit = stats.t.ppf(0.975, n - 1)
print(f"moyenne = {xbar:.2f}   erreur-type = {se:.2f}   t critique = {t_crit:.3f}")
print(f"IC à 95 % (à la main) : [{xbar - t_crit * se:.2f} ; {xbar + t_crit * se:.2f}]")
print("IC à 95 % (scipy)     :", np.round(stats.t.interval(0.95, n - 1, loc=xbar, scale=se), 2))
```
<!--sortie-->
```text
moyenne = 60.25   erreur-type = 1.90   t critique = 1.966
IC à 95 % (à la main) : [56.51 ; 63.98]
IC à 95 % (scipy)     : [56.51 63.98]
```

**Et pour chaque canal ?** On répète le calcul par groupe :

```python
def ic_moyenne(x, niveau=0.95):
    x = np.asarray(x)
    se = x.std(ddof=1) / np.sqrt(len(x))
    return stats.t.interval(niveau, len(x) - 1, loc=x.mean(), scale=se)

for canal in ["Instagram", "Site", "Boutique"]:
    x = df.loc[df["canal"] == canal, "montant"]
    lo, hi = ic_moyenne(x)
    print(f"{canal:<10} n = {len(x):>3}   moyenne = {x.mean():5.1f}   IC95 % = [{lo:5.1f} ; {hi:5.1f}]")
```
<!--sortie-->
```text
Instagram  n = 138   moyenne =  49.0   IC95 % = [ 43.8 ;  54.2]
Site       n = 148   moyenne =  59.5   IC95 % = [ 53.3 ;  65.7]
Boutique   n = 114   moyenne =  74.8   IC95 % = [ 67.3 ;  82.4]
```

Les intervalles d'Instagram ([43,8 ; 54,2]) et de la boutique ([67,3 ; 82,4]) **sont très éloignés** : c'est un indice sérieux que ces deux canaux diffèrent vraiment. L'intervalle du site ([53,3 ; 65,7]) chevauche légèrement celui d'Instagram mais pas celui de la boutique. Attention : « les intervalles se chevauchent » ne prouve **pas** que les moyennes sont égales, et même des intervalles qui se touchent peuvent cacher une différence significative. La bonne méthode est de construire un intervalle (ou un test) pour la **différence** elle-même, ce que nous ferons au 3.4.

> 💡 **Ce qui fait varier la largeur.** La demi-largeur est $t\times s/\sqrt n$. Elle **diminue** quand $n$ augmente (en $1/\sqrt n$), **augmente** quand la dispersion $s$ augmente, et **augmente** quand on exige plus de confiance (99 % donne un intervalle plus large que 95 %). Il n'y a pas de gratuité : plus de certitude coûte en précision.

```python
for niveau in (0.80, 0.90, 0.95, 0.99):
    lo, hi = ic_moyenne(m, niveau)
    print(f"confiance {niveau:.0%} : [{lo:.2f} ; {hi:.2f}]   largeur = {hi - lo:.2f}")
```
<!--sortie-->
```text
confiance 80% : [57.81 ; 62.69]   largeur = 4.88
confiance 90% : [57.11 ; 63.38]   largeur = 6.27
confiance 95% : [56.51 ; 63.98]   largeur = 7.47
confiance 99% : [55.33 ; 65.17]   largeur = 9.84
```

### 3.3.4 Intervalle pour une proportion

Pour un taux de conversion $\hat p=k/n$, l'erreur-type vue au 3.2.6 est $\sqrt{\hat p(1-\hat p)/n}$, et l'intervalle approché (dit de **Wald**) est

$$\hat p\pm1{,}96\sqrt{\frac{\hat p(1-\hat p)}n}.$$

Sur 1 000 visiteurs dont 205 achètent : $0{,}205\pm1{,}96\times0{,}0128=0{,}205\pm0{,}025$, soit **[18,0 % ; 23,0 %]**.

Mais cet intervalle devient **mauvais** pour de petits échantillons ou des proportions proches de 0 ou 1. Par exemple, avec 0 achat sur 20 visiteurs, $\hat p=0$ et l'intervalle de Wald est $[0\,;\,0]$ : « on est certain que le taux de conversion est exactement nul » ! Absurde. L'**intervalle de Wilson** corrige cela : il est centré non pas sur $\hat p$ mais sur une valeur légèrement « tirée vers 1/2 », et ne sort jamais de $[0,1]$.

```python
def ic_wald(k, n, niveau=0.95):
    p = k / n
    z = stats.norm.ppf(1 - (1 - niveau) / 2)
    d = z * np.sqrt(p * (1 - p) / n)
    return max(0, p - d), min(1, p + d)

def ic_wilson(k, n, niveau=0.95):
    return stats.binomtest(k, n).proportion_ci(confidence_level=niveau, method="wilson")[:2]

for k, n_obs in [(205, 1000), (7, 20), (0, 20), (2, 15)]:
    wald, wilson = ic_wald(k, n_obs), ic_wilson(k, n_obs)
    print(f"{k:>3}/{n_obs:<5} p = {k / n_obs:.3f}   Wald = [{wald[0]:.3f} ; {wald[1]:.3f}]   Wilson = [{wilson[0]:.3f} ; {wilson[1]:.3f}]")
```
<!--sortie-->
```text
205/1000  p = 0.205   Wald = [0.180 ; 0.230]   Wilson = [0.181 ; 0.231]
  7/20    p = 0.350   Wald = [0.141 ; 0.559]   Wilson = [0.181 ; 0.567]
  0/20    p = 0.000   Wald = [0.000 ; 0.000]   Wilson = [0.000 ; 0.161]
  2/15    p = 0.133   Wald = [0.000 ; 0.305]   Wilson = [0.037 ; 0.379]
```

Pour 1 000 visiteurs, les deux méthodes coïncident. Pour 7/20, l'intervalle est très large : **[0,18 ; 0,57]** pour Wilson, c'est-à-dire que 20 visiteurs ne permettent quasiment rien de conclure. Pour 0/20, Wilson dit que le taux réel peut aller jusqu'à environ 16 % (la fameuse « règle de trois » : avec 0 événement sur $n$, la borne haute à 95 % est environ $3/n=15\,\%$).

> ✅ **Conseil pratique.** Pour une proportion, utilisez **Wilson** (ou une méthode exacte) plutôt que Wald, sauf si $n$ est très grand et $p$ loin de 0 et 1.

### 3.3.5 Quand il n'y a pas de formule : le bootstrap

Et si l'on veut un intervalle pour la **médiane**, un quantile, un rapport, ou toute autre statistique pour laquelle on ne connaît pas de formule d'erreur-type ? Le **bootstrap** (Efron, 1979) offre une solution étonnamment simple et générale.

> 💡 **Idée.** On ne peut pas retirer de nouveaux échantillons dans la vraie population, mais on peut **rééchantillonner dans l'échantillon lui-même**. On tire $n$ valeurs **avec remise** dans nos $n$ observations (certaines apparaissent plusieurs fois, d'autres pas), on recalcule la statistique, et on recommence des milliers de fois. La dispersion des valeurs obtenues imite la dispersion qu'on aurait observée en échantillonnant la vraie population.

**L'algorithme (intervalle « percentile »).**

1. Répéter $B$ fois (par exemple 10 000) : tirer un échantillon de taille $n$ avec remise ; calculer la statistique.
2. L'intervalle à 95 % est formé des percentiles 2,5 % et 97,5 % des $B$ valeurs obtenues.

```python
rng = np.random.default_rng(42)
x = df["montant"].to_numpy()
B = 10_000

meds = np.array([np.median(rng.choice(x, size=len(x), replace=True)) for _ in range(B)])
moys = np.array([rng.choice(x, size=len(x), replace=True).mean() for _ in range(B)])

print("médiane observée :", np.median(x))
print("IC bootstrap 95 % de la médiane :", np.percentile(meds, [2.5, 97.5]).round(1))
print("IC bootstrap 95 % de la moyenne :", np.percentile(moys, [2.5, 97.5]).round(1))
print("(à comparer à l'IC de Student de la moyenne :", np.round(stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=x.std(ddof=1) / np.sqrt(len(x))), 1), ")")
```
<!--sortie-->
```text
médiane observée : 51.0
IC bootstrap 95 % de la médiane : [47.3 55.1]
IC bootstrap 95 % de la moyenne : [56.7 64. ]
(à comparer à l'IC de Student de la moyenne : [56.5 64. ] )
```

Pour la moyenne, le bootstrap donne pratiquement le même résultat que la formule de Student : rassurant. Pour la **médiane**, qui n'a pas de formule simple, il fournit un intervalle ([environ 47 ; 55] DT) que l'on n'aurait pas pu obtenir à la main.

> 🧪 **Limites.** Le bootstrap suppose que l'échantillon est représentatif de la population ; il marche mal pour des statistiques « extrêmes » (le maximum), avec de très petits échantillons, ou en présence de très fortes dépendances entre observations. Il reste un outil de base du data scientist, car il généralise à **n'importe quelle** statistique sans calcul mathématique.

### 3.3.6 Dimensionner un échantillon

On peut renverser le raisonnement : *quelle précision veut-on ?* Si Yasmine veut estimer le panier moyen à ±2 DT près, avec une confiance de 95 % et en supposant $s\approx38$ DT, il faut $1{,}96\times38/\sqrt n\le2$, soit

$$n\ge\Bigl(\frac{1{,}96\,s}{\varepsilon}\Bigr)^2=\Bigl(\frac{1{,}96\times38}2\Bigr)^2\approx1\,387\ \text{commandes}.$$

```python
s, eps = 38, 2
print("n pour une marge de ±2 DT :", int(np.ceil((1.96 * s / eps) ** 2)))
print("n pour une marge de ±1 DT :", int(np.ceil((1.96 * s / 1) ** 2)))
```
<!--sortie-->
```text
n pour une marge de ±2 DT : 1387
n pour une marge de ±1 DT : 5548
```

Diviser la marge par 2 demande **4 fois plus de données** (la loi en $1/\sqrt n$ du 2.4). C'est pourquoi gagner de la précision devient vite très coûteux.

> ✅ **À retenir (intervalles de confiance).**
>
> - Structure universelle : **estimation ± valeur critique × erreur-type**.
> - IC de la moyenne : $\bar x\pm t_{n-1}\,s/\sqrt n$ (Student). IC d'une proportion : préférez **Wilson** à Wald.
> - « Confiance à 95 % » signifie : **la méthode** capture la vraie valeur dans 95 % des échantillons possibles. Ce n'est pas une probabilité sur la vraie valeur.
> - Largeur : $\downarrow$ avec $n$ (en $1/\sqrt n$) ; $\uparrow$ avec la dispersion et avec le niveau de confiance.
> - **Bootstrap** : rééchantillonner avec remise pour obtenir un IC de n'importe quelle statistique.
> - $n\ge(z\,s/\varepsilon)^2$ pour viser une marge $\varepsilon$.


## 3.4 Tests d'hypothèses

> 💡 **Intuition : le tribunal.** Un test d'hypothèses fonctionne comme un procès. On part de la **présomption d'innocence** (l'hypothèse « il ne se passe rien », appelée $H_0$). On examine les **preuves** (les données). Si les preuves sont **très improbables** dans un monde où l'accusé est innocent, on le **condamne** (on rejette $H_0$). Sinon, on **acquitte** : cela ne prouve pas son innocence, cela veut seulement dire que les preuves sont insuffisantes.

### 3.4.1 Le vocabulaire et la méthode

- **Hypothèse nulle $H_0$** : l'état de référence, « pas d'effet, pas de différence ». Par exemple : « le panier moyen vaut 55 DT ».
- **Hypothèse alternative $H_1$** : ce que l'on cherche à montrer. « Le panier moyen est différent de 55 DT » (test **bilatéral**), ou « supérieur à 55 DT » (test **unilatéral**).
- **Statistique de test** $T$ : un nombre calculé sur l'échantillon qui mesure l'écart entre les données et ce que prédit $H_0$.
- **Niveau de signification $\alpha$** (souvent 5 %) : le risque que l'on accepte de se tromper en rejetant $H_0$ alors qu'elle est vraie.
- **p-valeur** : la probabilité, **si $H_0$ est vraie**, d'obtenir un résultat **au moins aussi extrême** que celui observé. Petite p-valeur = les données sont surprenantes sous $H_0$.

**Les deux erreurs possibles.**

| | $H_0$ est vraie | $H_0$ est fausse |
|---|---|---|
| **On rejette $H_0$** | ❌ **Erreur de type I** (faux positif), probabilité $\alpha$ | ✅ bonne décision (probabilité $1-\beta$ = **puissance**) |
| **On ne rejette pas $H_0$** | ✅ bonne décision | ❌ **Erreur de type II** (faux négatif), probabilité $\beta$ |

On **fixe** $\alpha$ à l'avance, et on cherche à garder $\beta$ petit (c'est la question de la puissance, 3.5).

**La recette en 5 étapes**, valable pour tous les tests de ce chapitre :

1. Poser $H_0$ et $H_1$.
2. Choisir $\alpha$ (avant de regarder les données !).
3. Calculer la statistique de test.
4. Calculer la p-valeur (ou comparer à la valeur critique).
5. Conclure : si $p<\alpha$, **rejeter** $H_0$ ; sinon, **ne pas rejeter** (et jamais « accepter »).

### 3.4.2 Test de Student sur une moyenne

> 🛠️ **Question de Yasmine.** Son objectif de panier moyen était de 55 DT. Les 400 commandes confirment-elles que le panier moyen **diffère** de 55 DT ?

1. $H_0:\mu=55$ ; $H_1:\mu\neq55$.
2. $\alpha=0{,}05$.
3. Statistique de test (la même construction qu'au 3.3.3, centrée sur la valeur de $H_0$) :

$$t=\frac{\bar x-\mu_0}{s/\sqrt n}=\frac{60{,}25-55}{38{,}02/\sqrt{400}}=\frac{5{,}25}{1{,}90}\approx2{,}76.$$

Sous $H_0$, $t$ suit une loi de Student à $n-1=399$ degrés de liberté. 4. La p-valeur est la probabilité qu'une telle loi donne une valeur **au moins aussi éloignée de 0** que 2,76, des deux côtés : $p=2\,P(T_{399}>2{,}76)$.

```python
import numpy as np
import pandas as pd
from scipy import stats

m = df["montant"]
mu0 = 55
n = len(m)
t_obs = (m.mean() - mu0) / (m.std(ddof=1) / np.sqrt(n))
p_val = 2 * stats.t.sf(abs(t_obs), df=n - 1)
print("t observé :", round(t_obs, 3))
print("p-valeur  :", round(p_val, 4))
print("valeur critique à 5 % :", round(stats.t.ppf(0.975, n - 1), 3))
res = stats.ttest_1samp(m, popmean=mu0)           # la fonction toute faite
print("scipy     : t =", round(res.statistic, 3), "  p =", round(res.pvalue, 4))
```
<!--sortie-->
```text
t observé : 2.76
p-valeur  : 0.0061
valeur critique à 5 % : 1.966
scipy     : t = 2.76   p = 0.0061
```

5. **Conclusion.** $p=0{,}006<0{,}05$ : on rejette $H_0$. Le panier moyen est significativement supérieur à 55 DT (il est en fait de 60,25 ; l'IC à 95 % du 3.3.3 était [56,5 ; 64,0], qui n'inclut pas 55 : **un test bilatéral à 5 % et un IC à 95 % disent la même chose**).

![Statistique de test sous H₀. Gauche : la valeur observée (2,76) tombe dans la zone de rejet (queues orange, 5 % au total). Droite : une valeur de 1,10 tomberait dans la zone de non-rejet.](figures/ch03-test-rejet.png)

> ⚠️ **« Ne pas rejeter » n'est pas « accepter ».** Si $p$ avait été de 0,30, on aurait dit « les données ne permettent pas de conclure que $\mu\neq55$ », pas « $\mu=55$ ». L'absence de preuve n'est pas la preuve de l'absence. (Un petit échantillon peut échouer à détecter un grand effet : c'est le problème de la puissance.)

### 3.4.3 Comparer deux groupes : le test de Welch

> 🛠️ **Question de Yasmine.** Les clients de la **boutique** dépensent-ils plus que ceux d'**Instagram** ? Les moyennes observées sont 74,8 et 49,0 DT, soit un écart de 25,8 DT. Cet écart est-il crédible ou dû au hasard ?

On teste $H_0:\mu_B=\mu_I$ contre $H_1:\mu_B\neq\mu_I$. On compare la différence des moyennes à son erreur-type. Comme les deux échantillons sont indépendants, les variances **s'additionnent** (2.3.3) :

$$t=\frac{\bar x_B-\bar x_I}{\sqrt{\dfrac{s_B^2}{n_B}+\dfrac{s_I^2}{n_I}}}.$$

C'est le **test de Welch**, qui n'exige pas que les deux groupes aient la même variance (c'est la version à utiliser par défaut ; l'ancien test de Student à variances égales est moins sûr).

```python
b = df.loc[df["canal"] == "Boutique", "montant"]
i = df.loc[df["canal"] == "Instagram", "montant"]

diff = b.mean() - i.mean()
se_diff = np.sqrt(b.var(ddof=1) / len(b) + i.var(ddof=1) / len(i))
print("différence des moyennes :", round(diff, 2), "DT")
print("erreur-type de la différence :", round(se_diff, 2))
print("t à la main :", round(diff / se_diff, 3))

res = stats.ttest_ind(b, i, equal_var=False)         # equal_var=False -> test de Welch
print("scipy (Welch) : t =", round(res.statistic, 3), "  p =", res.pvalue, "  ddl =", round(res.df, 1))
```
<!--sortie-->
```text
différence des moyennes : 25.8 DT
erreur-type de la différence : 4.64
t à la main : 5.565
scipy (Welch) : t = 5.565   p = 8.016365853327231e-08   ddl = 208.4
```

La statistique est $t\approx5{,}56$ et la p-valeur est de l'ordre de $10^{-7}$ : si les deux canaux avaient la même dépense moyenne, observer un écart aussi grand serait **quasi impossible**. On rejette $H_0$.

**Un test ne dit pas « de combien ».** Une p-valeur minuscule dit que l'effet est *réel*, pas qu'il est *grand*. Il faut toujours accompagner un test d'un **intervalle de confiance de la différence** et d'une **taille d'effet** :

```python
t_c = stats.t.ppf(0.975, res.df)
print(f"IC95 % de la différence : [{diff - t_c * se_diff:.1f} ; {diff + t_c * se_diff:.1f}] DT")

s_pooled = np.sqrt(((len(b) - 1) * b.var(ddof=1) + (len(i) - 1) * i.var(ddof=1)) / (len(b) + len(i) - 2))
print("d de Cohen :", round(diff / s_pooled, 2))
```
<!--sortie-->
```text
IC95 % de la différence : [16.7 ; 34.9] DT
d de Cohen : 0.72
```

Le client de la boutique dépense en moyenne entre 17 et 35 DT de plus (IC à 95 %). Le **d de Cohen** (la différence en nombre d'écarts-types) vaut environ 0,7 : un effet « moyen à grand » selon les conventions usuelles (0,2 petit, 0,5 moyen, 0,8 grand).

> 🧪 **Et la distribution asymétrique ?** Le test de Student suppose des moyennes à peu près normales (ce que le TCL assure pour des groupes de plus d'une centaine d'observations) ; il reste correct ici. Pour de petits groupes très asymétriques, on teste plutôt $\log(\text{montant})$, ou on utilise un test non paramétrique (➕ 3.7). Vérifions que la conclusion tient sur l'échelle logarithmique :

```python
res_log = stats.ttest_ind(np.log(b), np.log(i), equal_var=False)
print("test sur log(montant) : t =", round(res_log.statistic, 2), "  p =", res_log.pvalue)
res_si = stats.ttest_ind(df.loc[df["canal"] == "Site", "montant"], i, equal_var=False)
print("Site contre Instagram  : t =", round(res_si.statistic, 2), "  p =", round(res_si.pvalue, 4))
```
<!--sortie-->
```text
test sur log(montant) : t = 6.46   p = 5.400582683884821e-10
Site contre Instagram  : t = 2.55   p = 0.0113
```

Même conclusion. Pour Site contre Instagram, $p\approx0{,}011$ : l'écart (10,5 DT) est aussi significatif au seuil de 5 %, mais bien moins fortement.

**Le test apparié.** Quand les deux séries concernent **les mêmes individus** (avant/après), on ne compare pas deux groupes indépendants : on calcule la **différence pour chaque individu** et on teste que sa moyenne est nulle. Exemple : 8 colis dont on a mesuré le délai avant et après un changement de transporteur.

```python
avant = np.array([5, 4, 6, 7, 5, 6, 8, 5])
apres = np.array([4, 4, 5, 6, 5, 5, 6, 4])
d = avant - apres
print("différences :", d, "  moyenne :", d.mean())
res = stats.ttest_rel(avant, apres)
print("test apparié : t =", round(res.statistic, 2), "  p =", round(res.pvalue, 4))
print("(ttest_1samp sur les différences donne la même chose :", round(stats.ttest_1samp(d, 0).pvalue, 4), ")")
```
<!--sortie-->
```text
différences : [1 0 1 1 0 1 2 1]   moyenne : 0.875
test apparié : t = 3.86   p = 0.0062
(ttest_1samp sur les différences donne la même chose : 0.0062 )
```

Le nouveau transporteur fait gagner en moyenne 0,875 jour ($p\approx0{,}006$). Ignorer l'appariement (comme si les groupes étaient indépendants) donnerait un test beaucoup moins sensible, car on gaspillerait l'information que chaque colis est comparé à lui-même :

```python
print("(à tort, test non apparié : p =", round(stats.ttest_ind(avant, apres).pvalue, 3), ")")
```
<!--sortie-->
```text
(à tort, test non apparié : p = 0.128 )
```

### 3.4.4 Test sur une proportion

> 🛠️ **Question de Yasmine.** Historiquement, le taux de conversion était de 18 %. Sur les 1 000 dernières visites, 205 ont acheté (20,5 %). Y a-t-il une amélioration réelle ?

$H_0:p=0{,}18$ contre $H_1:p\neq0{,}18$. Sous $H_0$, l'erreur-type est $\sqrt{p_0(1-p_0)/n}$ (on utilise la valeur de $H_0$, pas l'estimation) et la statistique

$$z=\frac{\hat p-p_0}{\sqrt{p_0(1-p_0)/n}}=\frac{0{,}205-0{,}18}{\sqrt{0{,}18\times0{,}82/1000}}=\frac{0{,}025}{0{,}01215}\approx2{,}06.$$

On compare à la loi normale (TCL). Il existe aussi un test **exact** basé sur la loi binomiale, sans approximation :

```python
k, n_v, p0 = 205, 1000, 0.18
z = (k / n_v - p0) / np.sqrt(p0 * (1 - p0) / n_v)
print("z =", round(z, 3), "  p-valeur (approx. normale) =", round(2 * stats.norm.sf(abs(z)), 4))
print("test exact binomial : p-valeur =", round(stats.binomtest(k, n_v, p0).pvalue, 4))
```
<!--sortie-->
```text
z = 2.058   p-valeur (approx. normale) = 0.0396
test exact binomial : p-valeur = 0.0436
```

Les deux p-valeurs (0,040 et 0,044) sont **juste en dessous** de 0,05. On rejette $H_0$, mais de peu : c'est une preuve **modérée**, pas écrasante. Un intervalle de Wilson pour $p$, [18,1 % ; 23,1 %], inclut à peine 18 %. Lecture honnête : « il y a des indices d'amélioration, à confirmer avec davantage de données ».

### 3.4.5 Le test A/B : comparer deux proportions

C'est le test le plus utilisé en pratique dans le web et le marketing. Yasmine essaie deux versions de sa page produit. La version A (1 000 visiteurs) donne 120 achats (12 %), la version B (1 000 visiteurs) donne 150 achats (15 %). B est-elle meilleure ?

$H_0:p_A=p_B$. Sous $H_0$, les deux groupes ont le même taux, estimé en **regroupant** les données : $\hat p=\frac{120+150}{2000}=0{,}135$. L'erreur-type de la différence est $\sqrt{\hat p(1-\hat p)\bigl(\frac1{n_A}+\frac1{n_B}\bigr)}$ et

$$z=\frac{\hat p_B-\hat p_A}{\sqrt{\hat p(1-\hat p)\bigl(\frac1{n_A}+\frac1{n_B}\bigr)}}=\frac{0{,}03}{0{,}01528}\approx1{,}96.$$

```python
kA, nA, kB, nB = 120, 1000, 150, 1000
p_pool = (kA + kB) / (nA + nB)
se = np.sqrt(p_pool * (1 - p_pool) * (1 / nA + 1 / nB))
z = (kB / nB - kA / nA) / se
print("z =", round(z, 3), "  p-valeur =", round(2 * stats.norm.sf(abs(z)), 4))

# IC de la différence (erreur-type non regroupée)
se_nr = np.sqrt((kA / nA) * (1 - kA / nA) / nA + (kB / nB) * (1 - kB / nB) / nB)
d = kB / nB - kA / nA
print(f"différence = {d:.3f}   IC95 % = [{d - 1.96 * se_nr:.4f} ; {d + 1.96 * se_nr:.4f}]")
```
<!--sortie-->
```text
z = 1.963   p-valeur = 0.0496
différence = 0.030   IC95 % = [0.0001 ; 0.0599]
```

$p\approx0{,}0496$ : **tout juste** sous le seuil de 5 %, et l'intervalle de la différence ([0,0 ; 6 points]) frôle zéro. La conclusion « B est meilleure » est **fragile**. Ce cas, très courant, illustre pourquoi le seuil de 0,05 n'est pas une frontière magique : 0,0496 et 0,0504 ne sont pas deux mondes différents (nous y revenons en 3.5).

### 3.4.6 Le test du khi-deux : deux variables qualitatives sont-elles liées ?

> 🛠️ **Question de Yasmine.** La proportion de clients **satisfaits** (note ≥ 4) dépend-elle du canal de vente ?

On range les données dans un **tableau de contingence** :

```python
df["satisfait"] = df["satisfaction"] >= 4
tableau = pd.crosstab(df["canal"], df["satisfait"])
print(tableau)
print()
print(pd.crosstab(df["canal"], df["satisfait"], normalize="index").round(3))
```
<!--sortie-->
```text
satisfait  False  True 
canal                  
Boutique       5    109
Instagram     51     87
Site          45    103

satisfait  False  True 
canal                  
Boutique   0.044  0.956
Instagram  0.370  0.630
Site       0.304  0.696
```

$H_0$ : le canal et la satisfaction sont **indépendants**. Si c'était vrai, la proportion de satisfaits serait la même dans chaque canal (et égale à la proportion globale). On calcule alors, pour chaque case, l'**effectif attendu sous $H_0$** :

$$E_{ij}=\frac{(\text{total de la ligne }i)\times(\text{total de la colonne }j)}{\text{total général}}.$$

La statistique du khi-deux mesure l'écart entre effectifs observés ($O_{ij}$) et attendus :

$$\chi^2=\sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}.$$

Sous $H_0$, elle suit une loi du khi-deux à $(\text{lignes}-1)(\text{colonnes}-1)$ degrés de liberté. Plus les écarts sont grands, plus $\chi^2$ est grand.

```python
from scipy.stats import chi2_contingency
chi2, p, ddl, attendus = chi2_contingency(tableau)
print("effectifs attendus sous H0 :")
print(pd.DataFrame(attendus, index=tableau.index, columns=tableau.columns).round(1))
print(f"\nkhi-deux = {chi2:.2f}   ddl = {ddl}   p-valeur = {p:.2e}")

n_tot = tableau.values.sum()
cramer_v = np.sqrt(chi2 / (n_tot * (min(tableau.shape) - 1)))
print("V de Cramér :", round(cramer_v, 2))
```
<!--sortie-->
```text
effectifs attendus sous H0 :
satisfait  False  True 
canal                  
Boutique    28.8   85.2
Instagram   34.8  103.2
Site        37.4  110.6

khi-deux = 38.40   ddl = 2   p-valeur = 4.60e-09
V de Cramér : 0.31
```

Dans la boutique, il y a **109 satisfaits sur 114** (96 %), alors que l'on en attendrait environ 85 si le canal n'avait aucun effet (soit 24 de plus) ; sur Instagram, 63 % seulement (87 sur 138). La statistique est $\chi^2\approx38$ pour 2 degrés de liberté : $p\approx5\times10^{-9}$. On rejette l'indépendance. Le **V de Cramér** (0 = indépendance, 1 = lien parfait) vaut 0,31 : un lien d'intensité moyenne. (Attention : la boutique n'a pas de délai de livraison, ce qui explique sans doute en grande partie l'écart ; l'association n'est pas une causalité.)

> ⚠️ **Condition de validité.** L'approximation du khi-deux est fiable si **tous les effectifs attendus sont au moins 5**. Sinon, on utilise le test exact de Fisher (`scipy.stats.fisher_exact` pour un tableau 2×2).

### 3.4.7 Comment choisir son test ?

| Question | Données | Test |
|---|---|---|
| La moyenne vaut-elle $\mu_0$ ? | 1 variable quantitative | Student à un échantillon |
| Deux groupes indépendants ont-ils la même moyenne ? | quantitative × 2 groupes | **Welch** |
| Avant/après sur les mêmes individus ? | quantitatives appariées | Student apparié |
| Plus de 2 groupes ? | quantitative × $k$ groupes | ANOVA (`f_oneway`) ou Kruskal-Wallis (➕ 3.7) |
| La proportion vaut-elle $p_0$ ? | 1 variable binaire | z (ou binomial exact) |
| Deux proportions égales ? (A/B) | binaire × 2 groupes | z à deux proportions, ou khi-deux |
| Deux variables qualitatives liées ? | catégorielle × catégorielle | **khi-deux** (ou Fisher) |
| Deux variables quantitatives liées ? | quantitative × quantitative | test de corrélation (`pearsonr`, `spearmanr`) |

> ✅ **À retenir (tests d'hypothèses).**
>
> - On fixe $H_0$ (« rien ne se passe »), $H_1$, $\alpha$ ; on calcule une statistique de test et sa **p-valeur** ; on rejette si $p<\alpha$.
> - Deux erreurs : **type I** (faux positif, probabilité $\alpha$) et **type II** (faux négatif, probabilité $\beta$). Puissance $=1-\beta$.
> - « Ne pas rejeter » ≠ « accepter ». Une p-valeur faible dit que l'effet est *réel*, pas qu'il est *grand* : donnez toujours l'**IC** de l'effet et une **taille d'effet**.
> - Student (une moyenne), **Welch** (deux moyennes), apparié, z (proportions), **khi-deux** (deux variables qualitatives).
> - Un test bilatéral à 5 % équivaut à regarder si 0 (ou la valeur de $H_0$) est dans l'IC à 95 %.


## 3.5 p-valeurs, puissance et tests multiples

Au 3.4, nous avons *utilisé* la p-valeur. Voici maintenant comment ne pas s'en servir de travers. Cette section est celle qui vous évitera le plus d'erreurs concrètes : une bonne partie des « découvertes » publiées qui ne se reproduisent pas viennent de ce que nous allons voir.

### 3.5.1 Ce que la p-valeur est vraiment

> 📐 **Définition.** La **p-valeur** est la probabilité, calculée **en supposant $H_0$ vraie**, d'obtenir une statistique de test **au moins aussi extrême** que celle observée.

$$p=P\bigl(\text{résultat aussi extrême ou plus}\ \big|\ H_0\bigr).$$

Observez la direction du conditionnement : c'est $P(\text{données}\mid H_0)$ et **non** $P(H_0\mid\text{données})$. Nous avons vu au 2.1 que **inverser un conditionnement est l'erreur classique**.

Pour la sentir, rien de mieux que de fabriquer un monde où $H_0$ est vraie et de regarder les p-valeurs qu'on obtient. Simulons 10 000 tests de Student de deux groupes de 30 individus **tirés dans la même loi** (donc aucune vraie différence) :

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(1)
pvals_h0 = np.array([stats.ttest_ind(rng.normal(0, 1, 30), rng.normal(0, 1, 30)).pvalue for _ in range(10_000)])

print("proportion de p < 0,05 quand H0 est vraie :", round((pvals_h0 < 0.05).mean(), 4))
print("proportion de p < 0,01                     :", round((pvals_h0 < 0.01).mean(), 4))
print("proportion de p < 0,50                     :", round((pvals_h0 < 0.50).mean(), 4))
print("moyenne des p-valeurs                      :", round(pvals_h0.mean(), 3))
```
<!--sortie-->
```text
proportion de p < 0,05 quand H0 est vraie : 0.0486
proportion de p < 0,01                     : 0.0103
proportion de p < 0,50                     : 0.5013
moyenne des p-valeurs                      : 0.499
```

Quand $H_0$ est vraie, **la p-valeur suit une loi uniforme sur $[0,1]$** : 5 % des tests donnent $p<0{,}05$, 1 % donnent $p<0{,}01$, etc. C'est exactement ce que signifie « niveau $\alpha=5\,\%$ » : **un test sur vingt crie au loup à tort** quand il n'y a rien. Ce n'est pas un défaut du test, c'est sa définition.

Et quand $H_0$ est **fausse** ? Les p-valeurs se tassent vers 0 :

```python
pvals_h1 = np.array([stats.ttest_ind(rng.normal(0.8, 1, 30), rng.normal(0, 1, 30)).pvalue for _ in range(10_000)])
print("avec un vrai effet (d = 0,8) : proportion de p < 0,05 :", round((pvals_h1 < 0.05).mean(), 3))
print("histogramme (10 classes) sous H0 :", np.histogram(pvals_h0, bins=10, range=(0, 1))[0])
print("histogramme (10 classes) sous H1 :", np.histogram(pvals_h1, bins=10, range=(0, 1))[0])
```
<!--sortie-->
```text
avec un vrai effet (d = 0,8) : proportion de p < 0,05 : 0.865
histogramme (10 classes) sous H0 : [ 980 1008 1028 1006  991  985 1036  964 1024  978]
histogramme (10 classes) sous H1 : [9248  419  160   62   47   25   16    9    7    7]
```

Sous $H_0$, l'histogramme est **plat** ; sous $H_1$, il est entassé à gauche. C'est un outil de diagnostic précieux : si vous testez des milliers de variables et que l'histogramme de vos p-valeurs est plat, il n'y a probablement **rien** à trouver.

### 3.5.2 Ce que la p-valeur n'est pas

> ⚠️ **Cinq contresens fréquents.** Une p-valeur de 0,03 ne signifie **pas** :
>
> 1. que $H_0$ a 3 % de chances d'être vraie ;
> 2. que $H_1$ a 97 % de chances d'être vraie ;
> 3. que l'effet est **grand** ou **important** ;
> 4. que l'on obtiendrait de nouveau $p<0{,}05$ en refaisant l'étude (la **reproductibilité** dépend de la puissance) ;
> 5. qu'on a 3 % de chances de se tromper en rejetant $H_0$.

**Le point 5 mérite une démonstration**, car il est lourd de conséquences. Le risque réel de se tromper quand on rejette dépend de la **proportion d'hypothèses qui sont vraies** au départ : on retrouve la formule de Bayes de la section 2.1 et l'erreur du taux de base !

> 💡 **Exemple.** Yasmine teste 1 000 idées d'amélioration (couleur d'un bouton, texte d'une promotion, ordre des produits…). Réalistement, **10 %** seulement ont un vrai effet (100 vraies idées, 900 inutiles). Son test a un niveau $\alpha=5\,\%$ et une puissance de 80 %.
>
> - Vraies idées détectées : $100\times0{,}80=80$.
> - Idées inutiles « détectées » à tort : $900\times0{,}05=45$.
> - Au total, 125 résultats « significatifs », dont **45 sont des faux positifs**.

$$P(\text{fausse découverte}\mid\text{significatif})=\frac{45}{125}=36\,\%.$$

Plus d'un résultat « significatif » sur trois est faux, alors que $\alpha$ n'est que de 5 % ! Même mécanisme que l'alerte antifraude du 2.1.6. C'est pourquoi on exige des preuves plus fortes pour des hypothèses peu plausibles a priori (« des affirmations extraordinaires exigent des preuves extraordinaires »).

```python
alpha, puissance, part_vraies = 0.05, 0.80, 0.10
vrais_positifs = part_vraies * puissance
faux_positifs = (1 - part_vraies) * alpha
print("proportion de faux parmi les significatifs :", round(faux_positifs / (vrais_positifs + faux_positifs), 3))
```
<!--sortie-->
```text
proportion de faux parmi les significatifs : 0.36
```

### 3.5.3 Signification statistique ≠ importance pratique

Avec assez de données, **n'importe quelle** différence, même ridicule, devient « significative ». Un exemple extrême : deux versions d'une page ont des taux de conversion de 20,00 % et 20,10 %, mesurés sur 10 millions de visiteurs chacune.

```python
nA = nB = 10_000_000
pA, pB = 0.2000, 0.2010
p_pool = (pA + pB) / 2
z = (pB - pA) / np.sqrt(p_pool * (1 - p_pool) * (2 / nA))
print("z =", round(z, 2), "   p-valeur =", f"{2 * stats.norm.sf(z):.1e}")
print("gain absolu :", round((pB - pA) * 100, 2), "point de pourcentage")
```
<!--sortie-->
```text
z = 5.58    p-valeur = 2.3e-08
gain absolu : 0.1 point de pourcentage
```

La p-valeur est inférieure à 0,001 (hautement « significatif »), mais le gain est de **0,1 point** de conversion. Est-il utile ? Cela dépend du coût du changement, pas de la p-valeur. **Toujours rapporter la taille de l'effet et son intervalle de confiance**, jamais seulement « $p<0{,}05$ ».

### 3.5.4 La puissance : savoir si l'on peut voir ce qu'on cherche

> 💡 **Intuition.** Un test est comme un détecteur de métaux. Un détecteur peu sensible ne signale pas un petit objet enterré profondément : **l'absence de signal ne prouve pas l'absence d'objet**. La **puissance** $1-\beta$ est la probabilité que le test détecte un effet **s'il existe vraiment** (de taille donnée).

La puissance dépend de quatre choses liées entre elles :

| Facteur | Si... | ...alors la puissance |
|---|---|---|
| **Taille de l'effet** | grandit | augmente |
| **Taille d'échantillon** $n$ | grandit | augmente |
| **Dispersion** des données | diminue | augmente |
| **Niveau** $\alpha$ | on l'assouplit (0,10 au lieu de 0,05) | augmente (au prix de plus de faux positifs) |

**Retour sur notre test A/B du 3.4.5** (12 % contre 15 %, 1 000 visiteurs par version). Quelle était la puissance de cette expérience ? Sous $H_1$ avec $p_A=0{,}12$ et $p_B=0{,}15$, l'erreur-type de la différence est $\sqrt{\frac{0{,}12\times0{,}88}{1000}+\frac{0{,}15\times0{,}85}{1000}}=0{,}0154$, et la statistique de test est centrée sur $0{,}03/0{,}0154=1{,}95$. La puissance est donc la probabilité que cette statistique dépasse 1,96 :

$$\text{puissance}=P\bigl(Z>1{,}96-1{,}95\bigr)\approx0{,}50.$$

```python
def puissance_ab(p1, p2, n, alpha=0.05):
    se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    return stats.norm.cdf(abs(p2 - p1) / se - stats.norm.ppf(1 - alpha / 2))

print("puissance de l'expérience A/B du 3.4.5 :", round(puissance_ab(0.12, 0.15, 1000), 3))

# vérification par simulation
rng = np.random.default_rng(2)
rejets = 0
for _ in range(10_000):
    a, b = rng.binomial(1000, 0.12), rng.binomial(1000, 0.15)
    pp = (a + b) / 2000
    z = (b / 1000 - a / 1000) / np.sqrt(pp * (1 - pp) * 2 / 1000)
    rejets += abs(z) > 1.96
print("puissance simulée                     :", rejets / 10_000)
```
<!--sortie-->
```text
puissance de l'expérience A/B du 3.4.5 : 0.502
puissance simulée                     : 0.4954
```

La puissance n'était que de **50 %** : même si B est réellement meilleure de 3 points, l'expérience n'avait qu'**une chance sur deux** de le détecter. Le résultat « tout juste significatif » obtenu était donc de la chance autant que de l'information. Un test sous-dimensionné est un pari.

**Dimensionner l'expérience avant de la lancer.** On fixe l'effet minimal intéressant (ici +3 points), $\alpha=5\,\%$ et la puissance voulue (80 % est l'usage), puis on calcule $n$ :

$$n\ \text{par groupe}=\frac{(z_{1-\alpha/2}+z_{1-\beta})^2\,\bigl[p_1(1-p_1)+p_2(1-p_2)\bigr]}{(p_2-p_1)^2}.$$

```python
za, zb = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
def n_par_groupe(p1, p2):
    return (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2

for delta in (0.05, 0.03, 0.02, 0.01):
    print(f"détecter 12 % -> {12 + delta * 100:.0f} % : {int(np.ceil(n_par_groupe(0.12, 0.12 + delta))):>6} visiteurs par version")
```
<!--sortie-->
```text
détecter 12 % -> 17 % :    775 visiteurs par version
détecter 12 % -> 15 % :   2033 visiteurs par version
détecter 12 % -> 14 % :   4435 visiteurs par version
détecter 12 % -> 13 % :  17166 visiteurs par version
```

Pour détecter 3 points avec 80 % de puissance, il faut **environ 2 000 visiteurs par version**, soit le double de ce que Yasmine avait. Pour détecter 1 point, il en faut **près de 18 000**. La loi en $1/\text{effet}^2$ est impitoyable : diviser l'effet par 3 multiplie les besoins par 9.

![À gauche : puissance d'un test A/B en fonction du nombre de visiteurs, pour trois tailles d'effet. À droite : si l'on « jette un œil » aux résultats de plus en plus souvent et que l'on s'arrête dès que p < 0,05, le taux de faux positifs explose (sous H₀).](figures/ch03-puissance.png)

> ⚠️ **L'arrêt prématuré (*peeking*).** Dans une expérience en ligne, la tentation est forte de regarder les résultats chaque jour et de s'arrêter dès que $p<0{,}05$. La figure de droite montre le résultat : en regardant 20 fois, **le taux de faux positifs passe de 5 % à environ 25 %**, alors qu'il n'y a *aucun* effet réel. Règle : **fixer la taille d'échantillon à l'avance et ne conclure qu'à la fin** (ou utiliser des méthodes séquentielles conçues pour cela).

### 3.5.5 Les tests multiples : le piège du « fouillis de comparaisons »

> 💡 **Intuition.** Si vous lancez un dé 20 fois, vous obtiendrez presque sûrement un 6 quelque part. Si vous effectuez 20 tests à 5 %, il est presque sûr que l'un d'eux sera « significatif » par pur hasard.

Raisonnons comme au 2.1.4 (« au moins un ») : si les 20 tests sont indépendants et que toutes les hypothèses nulles sont vraies, la probabilité d'avoir **au moins un faux positif** est

$$1-(1-\alpha)^m=1-0{,}95^{20}\approx0{,}64.$$

```python
for m_tests in (1, 5, 10, 20, 50, 100):
    print(f"{m_tests:>3} tests : P(au moins un faux positif) = {1 - 0.95 ** m_tests:.3f}")
```
<!--sortie-->
```text
  1 tests : P(au moins un faux positif) = 0.050
  5 tests : P(au moins un faux positif) = 0.226
 10 tests : P(au moins un faux positif) = 0.401
 20 tests : P(au moins un faux positif) = 0.642
 50 tests : P(au moins un faux positif) = 0.923
100 tests : P(au moins un faux positif) = 0.994
```

Avec 100 tests, c'est quasi certain (99,4 %). Dès que l'on teste plusieurs variables, segments ou métriques, il faut en tenir compte. C'est exactement ce qui arrive quand on « fouille » un jeu de données : on regarde 40 sous-groupes et on rapporte celui qui sort (« les femmes de 25 à 34 ans achètent plus le jeudi »).

**Les corrections classiques.** On teste $m$ hypothèses nulles, avec les p-valeurs $p_1,\dots,p_m$.

- **Bonferroni** : on rejette $H_i$ si $p_i<\alpha/m$. Simple, très prudent (le **FWER**, probabilité d'au moins un faux positif, reste ≤ $\alpha$) mais il perd beaucoup de puissance quand $m$ est grand.
- **Holm** : trie les p-valeurs et applique des seuils $\alpha/m,\ \alpha/(m-1),\dots$ ; **toujours** au moins aussi puissant que Bonferroni, avec la même garantie. À préférer.
- **Benjamini–Hochberg (BH)** : contrôle non plus le risque d'*un seul* faux positif, mais la **proportion de fausses découvertes** parmi les rejets (le **FDR**, *false discovery rate*). Moins strict, beaucoup plus puissant. Idéal en exploration (criblage de centaines de variables).

> 📐 **Procédure de Benjamini–Hochberg.** Trier les p-valeurs : $p_{(1)}\le\dots\le p_{(m)}$. Trouver le plus grand $k$ tel que $p_{(k)}\le\dfrac km\,\alpha$. Rejeter les hypothèses correspondant à $p_{(1)},\dots,p_{(k)}$.

Mettons-les à l'épreuve dans une simulation réaliste : Yasmine compare 100 catégories de produits entre deux périodes. Parmi elles, **10** ont vraiment changé (effet $d=1$) et **90** n'ont pas bougé. Chaque comparaison utilise 40 observations par période.

```python
rng = np.random.default_rng(5)
m_tests, n_vrais, n_obs = 100, 10, 40
vraie_diff = np.array([1.0] * n_vrais + [0.0] * (m_tests - n_vrais))
pvals = np.array([stats.ttest_ind(rng.normal(d, 1, n_obs), rng.normal(0, 1, n_obs)).pvalue for d in vraie_diff])

def bonferroni(p, alpha=0.05):
    return p < alpha / len(p)

def holm(p, alpha=0.05):
    ordre = np.argsort(p)
    rejet = np.zeros(len(p), dtype=bool)
    for rang, idx in enumerate(ordre):
        if p[idx] < alpha / (len(p) - rang):
            rejet[idx] = True
        else:
            break
    return rejet

def benjamini_hochberg(p, alpha=0.05):
    m = len(p)
    ordre = np.argsort(p)
    seuils = (np.arange(1, m + 1) / m) * alpha
    ok = p[ordre] <= seuils
    rejet = np.zeros(m, dtype=bool)
    if ok.any():
        k = np.max(np.where(ok)[0])
        rejet[ordre[: k + 1]] = True
    return rejet

vrai = vraie_diff > 0
for nom, rejet in [("aucune correction (p < 0,05)", pvals < 0.05), ("Bonferroni", bonferroni(pvals)),
                   ("Holm", holm(pvals)), ("Benjamini-Hochberg", benjamini_hochberg(pvals))]:
    tp, fp = int((rejet & vrai).sum()), int((rejet & ~vrai).sum())
    print(f"{nom:<30} découvertes = {tp + fp:>2}   vraies = {tp:>2}   fausses = {fp:>2}")
```
<!--sortie-->
```text
aucune correction (p < 0,05)   découvertes = 12   vraies =  9   fausses =  3
Bonferroni                     découvertes =  7   vraies =  7   fausses =  0
Holm                           découvertes =  7   vraies =  7   fausses =  0
Benjamini-Hochberg             découvertes =  9   vraies =  9   fausses =  0
```

Lecture (pour cette graine) : sans correction, on « découvre » 12 effets, dont **3 sont de fausses alertes** (sur 90 hypothèses nulles, on s'attend à environ 4,5 faux positifs à 5 %). Bonferroni et Holm n'en gardent que 7, **tous vrais**, mais au prix d'avoir **raté** 3 vrais effets. Benjamini-Hochberg en retrouve 9 vrais sans aucun faux ici ; par construction, il garantit seulement qu'en moyenne la part de fausses découvertes reste sous 5 %. Le compromis est net : plus on corrige strictement, moins on se trompe, mais plus on rate de vrais effets.

> ✅ **Quel choix pratique ?**
> - Décision importante, peu d'hypothèses, un faux positif coûteux (lancer un produit, un traitement) : **Holm** (ou Bonferroni).
> - Exploration de nombreuses hypothèses, où l'on vérifiera ensuite les candidats : **Benjamini-Hochberg**.
> - Le mieux de tout : **décider à l'avance** de la ou des questions testées. Une analyse exploratoire est une source d'hypothèses, pas une preuve.

### 3.5.6 Les bonnes pratiques, en dix lignes

1. Écrire $H_0$, $H_1$, $\alpha$ et le plan d'analyse **avant** de regarder les données.
2. Dimensionner l'échantillon pour une puissance d'au moins 80 %.
3. Ne pas s'arrêter dès que $p<0{,}05$ (*peeking*).
4. Compter **tous** les tests effectués, pas seulement ceux qui « marchent », et corriger si nécessaire.
5. Rapporter la **taille d'effet** et un **intervalle de confiance**, pas seulement la p-valeur.
6. Distinguer significativité statistique et importance pratique.
7. Ne pas dire « accepter $H_0$ » : dire « pas de preuve suffisante ».
8. Se méfier d'un résultat « juste significatif » (0,04) : il est fragile.
9. Marquer clairement ce qui est **exploratoire** et ce qui est **confirmatoire**.
10. Refaire l'expérience si la décision est importante : la **réplication** est la meilleure preuve.

> ✅ **À retenir (p-valeurs, puissance, tests multiples).**
>
> - $p=P(\text{données aussi extrêmes}\mid H_0)$. Sous $H_0$, elle est **uniforme** sur $[0,1]$ ; 5 % des tests donnent $p<0{,}05$ par hasard.
> - Ce n'est ni $P(H_0\mid\text{données})$, ni la taille de l'effet. Le taux de fausses découvertes dépend de la proportion d'hypothèses vraies (Bayes).
> - **Puissance** $=1-\beta$ : dépend de l'effet, de $n$, de la dispersion et de $\alpha$. Dimensionner avant l'expérience : $n\propto1/\text{effet}^2$.
> - **Tests multiples** : $1-(1-\alpha)^m$ ; corriger par **Holm** (FWER) ou **Benjamini-Hochberg** (FDR). Pas de *peeking*, pas de *p-hacking*.


## 3.6 ➕ Pour aller plus loin : les sondages et l'échantillonnage

> 🧭 **Section optionnelle.** Tout ce chapitre suppose que l'échantillon est « tiré au hasard dans la population ». Mais **comment** l'obtient-on, et que se passe-t-il quand ce n'est pas le cas ? La théorie des sondages répond à ces questions, essentielles pour une enquête de satisfaction, une étude de marché, ou tout jeu de données dont on ne maîtrise pas la collecte.

### 3.6.1 Le biais de sélection : le pire ennemi

> 💡 **Une leçon historique.** En 1936, le magazine *Literary Digest* prédit la défaite de Roosevelt à l'élection américaine, d'après plus de **2 millions** de réponses reçues à son questionnaire. Roosevelt a été réélu largement. Au même moment, le tout jeune institut Gallup, avec un échantillon de quelques milliers de personnes seulement mais mieux choisi, avait prévu la victoire. Le magazine avait sollicité ses abonnés, des annuaires et des propriétaires de voitures : des personnes **plus aisées que la moyenne** des électeurs. Aucune quantité de données ne corrige un échantillon qui **ne représente pas** la population.

C'est la leçon centrale de cette section : **la taille de l'échantillon réduit la variance, pas le biais.** Un million d'observations mal choisies donne un résultat précis… et faux.

Les formes de biais les plus courantes :

| Biais | Mécanisme | Exemple chez Dar Jasmin |
|---|---|---|
| **Sélection** | la méthode de recrutement favorise certains profils | enquête par e-mail : seuls les clients déjà inscrits à la newsletter répondent |
| **Non-réponse** | les répondants diffèrent des non-répondants | seuls les clients très contents (ou très fâchés) répondent |
| **Survie** | on n'observe que ceux « qui restent » | analyser uniquement les clients encore actifs surestime la satisfaction |
| **Couverture** | une partie de la population n'est pas dans la base | un sondage en ligne ignore les clients sans accès à Internet |

### 3.6.2 L'échantillonnage aléatoire simple

Dans un **échantillon aléatoire simple** (EAS), chaque individu de la base de sondage a la **même probabilité** d'être choisi, et tous les groupes de $n$ individus sont également probables. C'est le modèle de tout ce que nous avons fait. L'estimateur de la moyenne est $\bar x$ ; quand on tire **sans remise** dans une population de taille finie $N$, l'erreur-type est corrigée par le **facteur de population finie** :

$$\operatorname{SE}(\bar x)=\frac{\sigma}{\sqrt n}\sqrt{1-\frac nN}.$$

Si l'on interroge une grande part de la population ($n/N$ non négligeable), l'incertitude diminue plus vite. Si $n\ll N$ (le cas habituel), le facteur vaut presque 1 : **ce qui compte, c'est $n$, pas la fraction interrogée**. Voilà pourquoi sonder 1 000 personnes suffit autant pour un pays de 10 millions d'habitants que pour une ville de 100 000.

**La marge d'erreur d'un sondage.** Pour une proportion estimée à $\hat p$ avec $n$ personnes, la marge d'erreur à 95 % est $1{,}96\sqrt{\hat p(1-\hat p)/n}$. Son maximum est atteint pour $\hat p=0{,}5$, ce qui donne la **règle à retenir** : $\text{marge}\approx\dfrac{1}{\sqrt n}$.

```python
import numpy as np
from scipy import stats

for n_s in (100, 400, 1000, 2500, 10000):
    marge = 1.96 * np.sqrt(0.25 / n_s)
    print(f"n = {n_s:>6} : marge d'erreur maximale = ±{marge * 100:.1f} points   (règle 1/sqrt(n) = ±{100 / np.sqrt(n_s):.1f})")
```
<!--sortie-->
```text
n =    100 : marge d'erreur maximale = ±9.8 points   (règle 1/sqrt(n) = ±10.0)
n =    400 : marge d'erreur maximale = ±4.9 points   (règle 1/sqrt(n) = ±5.0)
n =   1000 : marge d'erreur maximale = ±3.1 points   (règle 1/sqrt(n) = ±3.2)
n =   2500 : marge d'erreur maximale = ±2.0 points   (règle 1/sqrt(n) = ±2.0)
n =  10000 : marge d'erreur maximale = ±1.0 points   (règle 1/sqrt(n) = ±1.0)
```

Avec 1 000 personnes : ±3,1 points. Pour obtenir ±1 point, il en faut près de 10 000. C'est pourquoi les sondages nationaux s'arrêtent le plus souvent autour de 1 000 à 2 000 personnes. Et cette marge ne couvre que **l'erreur d'échantillonnage** : elle ne dit rien du biais de sélection ou de non-réponse, qui sont souvent plus grands.

### 3.6.3 L'échantillonnage stratifié

> 💡 **Intuition.** Si la population est composée de groupes **homogènes en eux-mêmes mais différents entre eux** (les canaux de vente !), il est dommage de laisser le hasard décider combien de chaque groupe tombera dans l'échantillon. On **découpe** la population en **strates** et on tire un échantillon aléatoire **dans chaque strate**, en proportion de sa taille. On garantit ainsi une représentation fidèle, et l'on gagne en précision.

**L'estimateur stratifié** pondère les moyennes de strates par leur poids dans la population : $\bar x_{\text{strat}}=\sum_h W_h\bar x_h$ avec $W_h=N_h/N$.

Montrons le gain par simulation. La base clients de Dar Jasmin compte 10 000 personnes réparties en trois canaux, dont les dépenses moyennes diffèrent nettement :

```python
rng = np.random.default_rng(50)
tailles = {"Instagram": 4000, "Site": 3500, "Boutique": 2500}
base = {"Instagram": 3.7, "Site": 3.9, "Boutique": 4.1}
canaux_pop = np.concatenate([[c] * n for c, n in tailles.items()])
depenses_pop = np.concatenate([np.exp(rng.normal(base[c], 0.55, size=n)) for c, n in tailles.items()])
N = len(depenses_pop)
vraie_moyenne = depenses_pop.mean()
print("taille de la population :", N, "   vraie dépense moyenne :", round(vraie_moyenne, 2), "DT")

n_ech, essais = 200, 5000
est_eas, est_strat = [], []
masques = {c: canaux_pop == c for c in tailles}
poids = {c: tailles[c] / N for c in tailles}
for _ in range(essais):
    # EAS : 200 clients au hasard dans toute la base
    est_eas.append(rng.choice(depenses_pop, size=n_ech, replace=False).mean())
    # stratifié proportionnel : 80 Instagram, 70 Site, 50 Boutique
    moy = 0
    for c in tailles:
        n_h = int(round(n_ech * poids[c]))
        moy += poids[c] * rng.choice(depenses_pop[masques[c]], size=n_h, replace=False).mean()
    est_strat.append(moy)

print("EAS         : moyenne =", round(np.mean(est_eas), 2), "  erreur-type =", round(np.std(est_eas), 2))
print("Stratifié   : moyenne =", round(np.mean(est_strat), 2), "  erreur-type =", round(np.std(est_strat), 2))
print("gain de variance :", round(1 - np.var(est_strat) / np.var(est_eas), 3))
```
<!--sortie-->
```text
taille de la population : 10000    vraie dépense moyenne : 56.4 DT
EAS         : moyenne = 56.39   erreur-type = 2.46
Stratifié   : moyenne = 56.39   erreur-type = 2.36
gain de variance : 0.081
```

Les deux estimateurs sont **sans biais** (leur moyenne tombe sur la vraie valeur), mais l'estimateur stratifié est **plus précis** : son erreur-type (2,36 DT) est inférieure d'environ 4 % à celle de l'EAS (2,46 DT), soit 8 % de variance en moins. Le gain est modeste ici car les différences entre canaux, bien que réelles, restent petites comparées à la dispersion *à l'intérieur* de chaque canal. Il serait bien plus grand si les strates étaient très différentes entre elles.

> 📐 **Pourquoi ça marche : décomposition de la variance.** La variance totale se décompose en variance **entre** strates et variance **à l'intérieur** des strates : $\sigma^2=\sigma^2_{\text{entre}}+\sigma^2_{\text{intra}}$. Dans un EAS, le hasard de la composition de l'échantillon introduit l'incertitude liée à la variance *entre* strates. La stratification **fixe** cette composition, et seule la variance *intra* demeure : l'erreur-type diminue exactement de la part « entre ».

**L'allocation de Neyman.** On peut aller plus loin : au lieu d'allouer proportionnellement à la taille, on interroge **davantage** les strates **plus hétérogènes** (de grand écart-type) : $n_h\propto N_h\sigma_h$. Ici, la boutique est la plus dispersée (écart-type de ses dépenses plus élevé en valeur absolue) : on gagnerait à en sur-échantillonner un peu.

### 3.6.4 Autres plans de sondage

| Plan | Principe | Avantage | Inconvénient |
|---|---|---|---|
| **Systématique** | un individu tous les $k$ dans la liste | simple | biais si la liste a une périodicité |
| **Par grappes** | on tire des groupes entiers (magasins, classes) puis on interroge tout le groupe | peu coûteux (déplacements) | moins précis (individus d'une grappe se ressemblent) |
| **À plusieurs degrés** | tirage de grappes puis d'individus dans les grappes | pratique pour de vastes populations | calcul d'erreur plus complexe |
| **Par quotas** | on remplit des quotas (âge, sexe…) sans tirage aléatoire | rapide, peu coûteux | pas de théorie d'erreur rigoureuse |
| **De convenance** | on prend ceux qui sont disponibles | très facile | **biais incontrôlable** |

Les plans aléatoires (EAS, stratifié, grappes) permettent de **quantifier** l'incertitude ; les plans de quotas ou de convenance non. C'est une raison de plus de se méfier des « sondages » de réseaux sociaux.

### 3.6.5 Redresser un échantillon biaisé : la pondération

On ne choisit pas toujours son échantillon. Yasmine envoie un questionnaire de satisfaction à tous ses clients ; les **réponses sont inégalement réparties** : les clients de la boutique répondent très peu (ils ne laissent pas d'e-mail), ceux d'Instagram beaucoup. Parmi les 300 réponses : 150 d'Instagram, 120 du site et 30 de la boutique, alors que la clientèle réelle est répartie en 40 % / 35 % / 25 %.

Si l'on moyenne naïvement les 300 réponses, la boutique est **sous-représentée** (10 % au lieu de 25 %). Or les clients de la boutique sont aussi les plus satisfaits : on **sous-estime** donc la satisfaction globale. La solution est de **pondérer** chaque réponse par $w=\dfrac{\text{part dans la population}}{\text{part dans l'échantillon}}$ (une *post-stratification*).

```python
satisf_vraie = {"Instagram": 0.63, "Site": 0.70, "Boutique": 0.96}   # taux de satisfaits par canal (3.4.6)
pop_part = {"Instagram": 0.40, "Site": 0.35, "Boutique": 0.25}
rep = {"Instagram": 150, "Site": 120, "Boutique": 30}
n_rep = sum(rep.values())

naif = sum(rep[c] * satisf_vraie[c] for c in rep) / n_rep
poids_c = {c: pop_part[c] / (rep[c] / n_rep) for c in rep}
pondere = sum(rep[c] * poids_c[c] * satisf_vraie[c] for c in rep) / sum(rep[c] * poids_c[c] for c in rep)
vrai = sum(pop_part[c] * satisf_vraie[c] for c in pop_part)

print("poids :", {c: round(w, 2) for c, w in poids_c.items()})
print("satisfaction vraie (population) :", round(vrai, 3))
print("estimation naïve                :", round(naif, 3))
print("estimation pondérée             :", round(pondere, 3))
```
<!--sortie-->
```text
poids : {'Instagram': 0.8, 'Site': 0.87, 'Boutique': 2.5}
satisfaction vraie (population) : 0.737
estimation naïve                : 0.691
estimation pondérée             : 0.737
```

La moyenne naïve (environ 69 %) sous-estime la vraie valeur (73,7 %) ; la pondération corrige l'erreur. Chaque réponse de la boutique « compte pour » 2,5 réponses (poids 2,5) et chaque réponse d'Instagram pour 0,8. (Cette correction n'est valable que si, **à l'intérieur de chaque canal**, répondants et non-répondants sont comparables : la pondération redresse les déséquilibres **observables**, pas ceux que l'on ne mesure pas.)

> ✅ **À retenir (sondages).**
>
> - **La taille ne corrige pas le biais** (*Literary Digest*) ; ce qui compte, c'est la qualité du tirage.
> - EAS : marge d'erreur $\approx1/\sqrt n$ (±3 points pour 1 000 personnes), indépendante de la taille de la population si elle est grande.
> - **Stratification** : on tire dans chaque groupe, en proportion ; estimateur $\sum W_h\bar x_h$, plus précis que l'EAS quand les strates diffèrent.
> - Plans par grappes, de quotas, de convenance : moins précis ou sans théorie d'erreur.
> - On redresse un échantillon déséquilibré par **pondération** ($w=$ part population / part échantillon), sous réserve de comparabilité à l'intérieur des groupes.


## 3.7 ➕ Pour aller plus loin : les méthodes non paramétriques

> 🧭 **Section optionnelle.** Les tests du 3.4 (Student, Welch) supposent, au moins approximativement, une loi normale des moyennes. Les méthodes **non paramétriques** (ou *sans loi*) évitent de postuler une forme de distribution. Elles sont précieuses pour de petits échantillons, des variables ordinales (notes de 1 à 5) ou des données très asymétriques et pleines de valeurs extrêmes.

### 3.7.1 Remplacer les valeurs par leurs rangs

> 💡 **Intuition.** Au lieu de travailler sur les valeurs, on les **range** du plus petit au plus grand et l'on travaille sur leurs **rangs** (1er, 2e, 3e…). Une valeur extrême de 1 000 000 n'a que le rang « dernier » : elle ne peut plus fausser le résultat. Les rangs perdent un peu d'information (l'ampleur des écarts), mais gagnent une **robustesse** considérable.

```python
import numpy as np
import pandas as pd
from scipy import stats

x = np.array([12, 15, 14, 10, 13, 40])     # un client a dépensé 40 : valeur extrême
print("valeurs :", x)
print("rangs   :", stats.rankdata(x))
```
<!--sortie-->
```text
valeurs : [12 15 14 10 13 40]
rangs   : [2. 5. 4. 1. 3. 6.]
```

L'extrême (40) reçoit simplement le rang 6, le même qu'il aurait eu en valant 16.

### 3.7.2 Le test de Mann-Whitney (deux groupes indépendants)

C'est l'équivalent non paramétrique du test de Welch. On mélange les deux groupes, on range toutes les valeurs, puis on regarde si les rangs d'un groupe sont systématiquement plus élevés que ceux de l'autre.

> 💡 **Interprétation très parlante.** La statistique $U/(n_1n_2)$ est la probabilité qu'une observation tirée au hasard dans le groupe A **dépasse** une observation tirée au hasard dans le groupe B. Valeur 0,5 : aucune différence ; proche de 1 : A domine B. (C'est aussi l'**AUC** du volume II.)

**Un cas où le test de Student se trompe.** Deux petits groupes de 6 commandes. Dans le premier, un client dépense une somme exceptionnelle :

```python
ga = np.array([12, 15, 14, 10, 13, 40])
gb = np.array([9, 8, 11, 10, 7, 12])
print("moyennes :", ga.mean().round(1), gb.mean().round(1))
print("Welch          : p =", round(stats.ttest_ind(ga, gb, equal_var=False).pvalue, 3))
print("Mann-Whitney   : p =", round(stats.mannwhitneyu(ga, gb).pvalue, 3))
```
<!--sortie-->
```text
moyennes : 17.3 9.5
Welch          : p = 0.15
Mann-Whitney   : p = 0.02
```

Presque **tous** les clients du premier groupe dépensent plus que ceux du second ; seul le cas de 40 gonfle la variance et noie l'effet dans le test de Student ($p\approx0{,}15$, non significatif). Le test de Mann-Whitney, lui, voit la domination systématique du groupe A ($p\approx0{,}02$, significatif). C'est le gain de puissance de la robustesse quand les données sont « sales ».

**Sur nos 400 commandes** (boutique contre Instagram) :

```python
b = df.loc[df["canal"] == "Boutique", "montant"]
i = df.loc[df["canal"] == "Instagram", "montant"]
u = stats.mannwhitneyu(b, i, alternative="two-sided")
print("U =", u.statistic, "  p-valeur =", u.pvalue)
print("P(commande boutique > commande Instagram) =", round(u.statistic / (len(b) * len(i)), 3))
```
<!--sortie-->
```text
U = 11246.0   p-valeur = 4.410098845865466e-09
P(commande boutique > commande Instagram) = 0.715
```

Une commande de la boutique dépasse une commande d'Instagram dans 71 % des paires comparées ($p\approx4\times10^{-9}$). Conclusion identique à celle du test de Welch, avec une interprétation plus intuitive.

### 3.7.3 Autres tests de rangs

| Situation | Test paramétrique | Équivalent non paramétrique |
|---|---|---|
| 2 groupes indépendants | Welch | **Mann-Whitney** (`mannwhitneyu`) |
| 2 séries appariées | Student apparié | **Wilcoxon** des rangs signés (`wilcoxon`) |
| $k>2$ groupes | ANOVA (`f_oneway`) | **Kruskal-Wallis** (`kruskal`) |
| Corrélation | Pearson | **Spearman** / **Kendall** (`spearmanr`, `kendalltau`) |

```python
# Wilcoxon : les 8 colis avant/après du 3.4.3
avant = np.array([5, 4, 6, 7, 5, 6, 8, 5])
apres = np.array([4, 4, 5, 6, 5, 5, 6, 4])
print("Wilcoxon apparié :", round(stats.wilcoxon(avant, apres).pvalue, 4))

# Kruskal-Wallis : les trois canaux ensemble
groupes = [df.loc[df["canal"] == c, "montant"] for c in ["Instagram", "Site", "Boutique"]]
print("ANOVA          : p =", f"{stats.f_oneway(*groupes).pvalue:.1e}")
print("Kruskal-Wallis : p =", f"{stats.kruskal(*groupes).pvalue:.1e}")

# Corrélation entre le délai et la satisfaction (variable ordinale)
print("Pearson  :", np.round(stats.pearsonr(df["livraison"], df["satisfaction"]), 3))
print("Spearman :", np.round(stats.spearmanr(df["livraison"], df["satisfaction"]), 3))
print("Kendall  :", np.round(stats.kendalltau(df["livraison"], df["satisfaction"]), 3))
```
<!--sortie-->
```text
Wilcoxon apparié : 0.0312
ANOVA          : p = 3.4e-07
Kruskal-Wallis : p = 9.4e-09
Pearson  : [-0.532  0.   ]
Spearman : [-0.511  0.   ]
Kendall  : [-0.437  0.   ]
```

Les lignes de corrélation donnent (coefficient, p-valeur) ; la p-valeur arrondie vaut 0. Pour la satisfaction (note de 1 à 5, **ordinale**), Spearman et Kendall sont plus appropriés que Pearson. Dans les trois cas, le lien entre délai et satisfaction est très significatif.

> ✅ **Quand choisir le non paramétrique ?** Données ordinales ; petits échantillons ($n<20$) d'allure non normale ; valeurs extrêmes qu'on ne veut pas supprimer. Si les données sont vraiment normales, le test de Student est un peu plus puissant (de l'ordre de 5 %) : le non paramétrique est une **assurance bon marché**.

### 3.7.4 Les tests de permutation : l'idée la plus simple de la statistique

> 💡 **Intuition.** $H_0$ dit : « le canal n'a aucun effet sur le montant ». Si c'est vrai, l'étiquette « boutique » ou « Instagram » collée sur une commande est **arbitraire** : on aurait pu l'échanger avec n'importe quelle autre. Alors **mélangeons** les étiquettes au hasard, recalculons la différence de moyennes, et recommençons des milliers de fois. On obtient ainsi la **distribution de la différence quand $H_0$ est vraie**, sans aucune hypothèse de loi. La p-valeur est la fréquence des mélanges qui donnent une différence au moins aussi grande que celle observée.

```python
rng = np.random.default_rng(12)
valeurs = np.concatenate([b.to_numpy(), i.to_numpy()])
n_b = len(b)
diff_obs = b.mean() - i.mean()

n_perm = 20_000
diffs = np.empty(n_perm)
for k in range(n_perm):
    melange = rng.permutation(valeurs)
    diffs[k] = melange[:n_b].mean() - melange[n_b:].mean()

p_perm = (np.sum(np.abs(diffs) >= abs(diff_obs)) + 1) / (n_perm + 1)
print("différence observée :", round(diff_obs, 2), "DT")
print("plus grande différence parmi les 20 000 mélanges :", round(np.abs(diffs).max(), 2), "DT")
print("p-valeur de permutation :", p_perm)
```
<!--sortie-->
```text
différence observée : 25.8 DT
plus grande différence parmi les 20 000 mélanges : 20.58 DT
p-valeur de permutation : 4.999750012499375e-05
```

Aucun des 20 000 mélanges n'atteint la différence observée de 25,8 DT : la différence maximale obtenue par hasard est bien plus petite. On majore donc la p-valeur par $1/20\,001\approx5\times10^{-5}$ (le « +1 » évite de déclarer p = 0). Faisons maintenant la même chose sur la petite expérience à 6 + 6 commandes, où l'on peut même énumérer toutes les permutations possibles :

```python
from itertools import combinations
tout = np.concatenate([ga, gb])
obs = tout[:6].mean() - tout[6:].mean()
n_plus_extreme, total = 0, 0
for idx in combinations(range(12), 6):                 # les 924 façons de choisir 6 commandes sur 12
    masque = np.zeros(12, dtype=bool)
    masque[list(idx)] = True
    d = tout[masque].mean() - tout[~masque].mean()
    n_plus_extreme += abs(d) >= abs(obs) - 1e-12
    total += 1
print("nombre de permutations :", total)
print("p-valeur exacte de permutation :", round(n_plus_extreme / total, 4))
```
<!--sortie-->
```text
nombre de permutations : 924
p-valeur exacte de permutation : 0.0173
```

Il y a $\binom{12}{6}=924$ manières de répartir les 12 valeurs en deux groupes (clin d'œil au 1.6 !) ; la p-valeur est la proportion de ces 924 répartitions dont l'écart de moyennes est au moins aussi grand que celui observé. Le test est **exact** et n'a besoin d'aucune hypothèse. Il est très souple : on peut l'appliquer à **n'importe quelle statistique** (médiane, rapport, corrélation), comme le bootstrap.

### 3.7.5 Tester la normalité

Comment savoir si l'hypothèse de normalité du test de Student est raisonnable ? Deux outils.

**Le diagramme quantile-quantile (QQ-plot)** : on compare les quantiles des données à ceux d'une loi normale ; si les points suivent la droite, c'est normal. **Le test de Shapiro-Wilk** : $H_0$ = « les données sont normales ».

```python
print("Shapiro-Wilk sur le montant      : p =", f"{stats.shapiro(df['montant']).pvalue:.1e}")
print("Shapiro-Wilk sur log(montant)    : p =", round(stats.shapiro(np.log(df["montant"])).pvalue, 3))
z = stats.zscore(np.log(df["montant"]))
print("Kolmogorov-Smirnov (log, normal) : p =", round(stats.kstest(z, "norm").pvalue, 3))
```
<!--sortie-->
```text
Shapiro-Wilk sur le montant      : p = 3.0e-18
Shapiro-Wilk sur log(montant)    : p = 0.846
Kolmogorov-Smirnov (log, normal) : p = 0.879
```

Le montant brut est **clairement non normal** ($p\approx10^{-18}$), alors que son logarithme est tout à fait compatible avec la normalité (pas de rejet : $p\approx0{,}85$), ce qui confirme la structure **log-normale** vue au 3.1.5. Le **test de Kolmogorov-Smirnov** compare la fonction de répartition observée à celle d'une loi donnée (ou deux échantillons entre eux).

> ⚠️ **Piège : tester la normalité n'est pas toujours utile.** Avec beaucoup de données, ces tests rejettent la normalité pour des écarts infimes sans conséquence ; avec peu de données, ils ne détectent rien. On s'appuie surtout sur les **graphiques** et sur le **TCL** : la normalité de la **moyenne** (ce qui compte pour Student) est assurée dès que $n$ est grand, même si les données ne sont pas normales.

> ✅ **À retenir (non paramétrique).**
>
> - Travailler sur les **rangs** rend robuste aux valeurs extrêmes et applicable aux données ordinales.
> - **Mann-Whitney** (2 groupes), **Wilcoxon** (apparié), **Kruskal-Wallis** ($k$ groupes), **Spearman/Kendall** (corrélation).
> - **Test de permutation** : on mélange les étiquettes pour fabriquer la loi de la statistique sous $H_0$ ; valable pour toute statistique.
> - **Shapiro-Wilk** et **Kolmogorov-Smirnov** testent une loi, mais préférez les graphiques et le TCL.


## 3.8 Exercices du chapitre 3

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse.

### Énoncés

**Exercice 1 ⭐ (descriptif).** Huit commandes en DT : $12,\,15,\,15,\,18,\,20,\,22,\,25,\,60$. Calculez la moyenne, la médiane, le mode, l'écart-type (avec $n-1$) et l'écart interquartile. Quelle mesure de position est la plus représentative, et pourquoi ?

**Exercice 2 ⭐ (variance sans biais).** Un échantillon de 5 délais de livraison : $4,\,8,\,6,\,5,\,7$ jours. Calculez la variance en divisant par $n$ puis par $n-1$. Laquelle utiliser pour estimer la variance de **tous** les délais ?

**Exercice 3 ⭐⭐ (maximum de vraisemblance).** Le nombre de commandes par heure a été relevé 8 fois : $2,\,3,\,1,\,4,\,0,\,3,\,2,\,5$. On modélise par une loi de Poisson$(\lambda)$. (a) Écrivez la log-vraisemblance et trouvez $\hat\lambda$ en dérivant. (b) Avec cette estimation, quelle est la probabilité de ne recevoir aucune commande pendant une heure ?

**Exercice 4 ⭐ (IC d'une moyenne).** Sur $n=36$ commandes : $\bar x=52$ DT, $s=12$ DT. Donnez un intervalle de confiance à 95 % de la moyenne, puis à 99 %. Quelle est la signification du « 95 % » ?

**Exercice 5 ⭐⭐ (IC d'une proportion).** Un questionnaire envoyé à 60 clients donne 18 « très satisfaits ». Calculez l'IC à 95 % de la vraie proportion par la méthode de Wald et par celle de Wilson. Pourquoi sont-ils différents ?

**Exercice 6 ⭐⭐ (test sur une moyenne).** Le transporteur promet un délai moyen de 3 jours. Sur 25 colis, on mesure en moyenne 3,6 jours avec un écart-type de 1,5 jour. (a) Testez $H_0:\mu=3$ contre $H_1:\mu\neq3$ à 5 %. (b) Que change un test unilatéral $H_1:\mu>3$ ? (c) Peut-on dire que le transporteur respecte sa promesse ?

**Exercice 7 ⭐⭐ (test A/B).** Version A : 45 achats sur 500 visiteurs. Version B : 66 achats sur 500 visiteurs. (a) B est-elle meilleure, à 5 % ? (b) Donnez un IC de la différence. (c) Quelle était la puissance de ce test si le vrai écart est celui observé ?

**Exercice 8 ⭐⭐ (khi-deux).** Parmi 100 clients ayant reçu un code promo, 30 ont acheté ; parmi 100 clients sans code, 45 ont acheté. Le code a-t-il un effet ? Construisez le tableau, calculez les effectifs attendus et le test du khi-deux. Comparez avec le test de deux proportions.

**Exercice 9 ⭐⭐⭐ (taille d'échantillon).** Le taux de conversion actuel est de 20 %. Yasmine veut détecter une hausse à 24 % avec une puissance de 80 % et $\alpha=5\,\%$. (a) Combien de visiteurs par version ? (b) Et pour détecter 22 % ? (c) Expliquez le rapport entre les deux résultats.

**Exercice 10 ⭐⭐⭐ (tests multiples).** Un analyste teste 8 hypothèses et obtient les p-valeurs $0{,}001;\ 0{,}008;\ 0{,}012;\ 0{,}030;\ 0{,}040;\ 0{,}200;\ 0{,}500;\ 0{,}700$. Lesquelles sont rejetées à 5 % (a) sans correction, (b) avec Bonferroni, (c) avec Holm, (d) avec Benjamini-Hochberg ?

### Corrigés

**Corrigé 1.** Moyenne : $187/8=23{,}375$. Triées : $12,15,15,18,20,22,25,60$ : la médiane est $(18+20)/2=19$. Mode : 15. Écart-type ($n-1$) : voir le code (≈ 15,4). Les quartiles (méthode de NumPy) donnent un IQR de 7,75. La **médiane** (19) est la plus représentative : la moyenne (23,4) est tirée vers le haut par la commande de 60 DT (valeur extrême), qui est supérieure de plus du double au reste.

```python
import numpy as np
from scipy import stats
x = np.array([12, 15, 15, 18, 20, 22, 25, 60])
print("moyenne :", x.mean(), " médiane :", np.median(x), " mode :", stats.mode(x).mode)
print("écart-type (n-1) :", round(x.std(ddof=1), 2))
print("IQR :", np.percentile(x, 75) - np.percentile(x, 25))
```
<!--sortie-->
```text
moyenne : 23.375  médiane : 19.0  mode : 15
écart-type (n-1) : 15.38
IQR : 7.75
```

**Corrigé 2.** $\bar x=6$ ; écarts : $-2,2,0,-1,1$ ; carrés : $4,4,0,1,1$ ; somme $=10$. Division par $n$ : $10/5=2$. Division par $n-1$ : $10/4=2{,}5$. Pour estimer la variance de la **population**, on utilise $n-1$ (estimateur sans biais, 3.2.3).

```python
d = np.array([4, 8, 6, 5, 7])
print("var (n)   :", d.var(ddof=0), "   var (n-1) :", d.var(ddof=1))
```
<!--sortie-->
```text
var (n)   : 2.0    var (n-1) : 2.5
```

**Corrigé 3.** (a) $\ell(\lambda)=\sum_i\bigl(-\lambda+x_i\ln\lambda-\ln x_i!\bigr)=-n\lambda+\ln\lambda\sum x_i-\sum\ln x_i!$. $\ell'(\lambda)=-n+\dfrac{\sum x_i}{\lambda}=0\Rightarrow\hat\lambda=\bar x=\dfrac{20}8=2{,}5$ (c'est un maximum car $\ell''=-\sum x_i/\lambda^2<0$). (b) $P(N=0)=e^{-2{,}5}\approx0{,}082$.

```python
x = np.array([2, 3, 1, 4, 0, 3, 2, 5])
lam = x.mean()
print("lambda chapeau =", lam, "  P(0 commande) =", round(np.exp(-lam), 4))
grille = np.linspace(0.5, 6, 1101)
print("maximum sur grille :", round(grille[np.argmax([stats.poisson.logpmf(x, g).sum() for g in grille])], 2))
```
<!--sortie-->
```text
lambda chapeau = 2.5   P(0 commande) = 0.0821
maximum sur grille : 2.5
```

**Corrigé 4.** Erreur-type : $12/\sqrt{36}=2$. Valeur critique de Student à 35 ddl : 2,030 (95 %) et 2,724 (99 %). IC 95 % : $52\pm2{,}030\times2=[47{,}9\,;\,56{,}1]$. IC 99 % : $52\pm2{,}724\times2=[46{,}6\,;\,57{,}4]$ (plus large : plus de confiance coûte en précision). « 95 % » : si l'on répétait l'enquête de nombreuses fois, environ 95 % des intervalles ainsi construits contiendraient la vraie moyenne.

```python
n, xbar, s = 36, 52, 12
se = s / np.sqrt(n)
for niveau in (0.95, 0.99):
    t = stats.t.ppf(1 - (1 - niveau) / 2, n - 1)
    print(f"{niveau:.0%} : t = {t:.3f}   IC = [{xbar - t * se:.1f} ; {xbar + t * se:.1f}]")
```
<!--sortie-->
```text
95% : t = 2.030   IC = [47.9 ; 56.1]
99% : t = 2.724   IC = [46.6 ; 57.4]
```

**Corrigé 5.** $\hat p=18/60=0{,}30$. Wald : erreur-type $\sqrt{0{,}3\times0{,}7/60}=0{,}0592$, IC $0{,}30\pm0{,}116=[0{,}184\,;\,0{,}416]$. Wilson (voir le code) donne environ $[0{,}199\,;\,0{,}425]$ : légèrement décalé vers le centre et plus large à droite. Wilson est plus fiable car il tient compte du fait que l'erreur-type dépend de $p$ lui-même, d'où une meilleure couverture pour $n$ modeste.

```python
k, n = 18, 60
p = k / n
d = 1.96 * np.sqrt(p * (1 - p) / n)
print("Wald   : [", round(p - d, 3), ";", round(p + d, 3), "]")
w = stats.binomtest(k, n).proportion_ci(confidence_level=0.95, method="wilson")
print("Wilson : [", round(w.low, 3), ";", round(w.high, 3), "]")
```
<!--sortie-->
```text
Wald   : [ 0.184 ; 0.416 ]
Wilson : [ 0.199 ; 0.425 ]
```

**Corrigé 6.** (a) $t=\dfrac{3{,}6-3}{1{,}5/\sqrt{25}}=\dfrac{0{,}6}{0{,}3}=2{,}0$ avec 24 ddl. Valeur critique bilatérale à 5 % : 2,064. Comme $2{,}0<2{,}064$ (et $p\approx0{,}057$), on **ne rejette pas** $H_0$ de justesse. (b) En unilatéral, $p\approx0{,}028<0{,}05$ : on rejette. Mais on ne peut choisir le sens du test **qu'avant** de voir les données et si l'on n'est vraiment intéressé que par un dépassement ; décider après coup serait tricher. (c) Honnêtement : les données sont **à la limite** : le retard moyen estimé est de 0,6 jour, l'IC à 95 % ($3{,}6\pm2{,}064\times0{,}3=[2{,}98\,;\,4{,}22]$) inclut 3 de justesse. On ne peut ni affirmer que la promesse est tenue, ni qu'elle ne l'est pas ; il faut davantage de colis.

```python
n, xbar, s, mu0 = 25, 3.6, 1.5, 3
t = (xbar - mu0) / (s / np.sqrt(n))
print("t =", t, "  p bilatérale =", round(2 * stats.t.sf(t, n - 1), 4), "  p unilatérale =", round(stats.t.sf(t, n - 1), 4))
tc = stats.t.ppf(0.975, n - 1)
print("IC95 % : [", round(xbar - tc * s / np.sqrt(n), 2), ";", round(xbar + tc * s / np.sqrt(n), 2), "]")
```
<!--sortie-->
```text
t = 2.0000000000000004   p bilatérale = 0.0569   p unilatérale = 0.0285
IC95 % : [ 2.98 ; 4.22 ]
```

**Corrigé 7.** (a) $\hat p_A=0{,}09$, $\hat p_B=0{,}132$, $\hat p=\frac{111}{1000}=0{,}111$. $z=\dfrac{0{,}042}{\sqrt{0{,}111\times0{,}889\times(2/500)}}=\dfrac{0{,}042}{0{,}01987}\approx2{,}11$, $p\approx0{,}035$ : significatif à 5 %. (b) Erreur-type non regroupée $\approx0{,}0194$, donc IC $=0{,}042\pm0{,}039=[0{,}003\,;\,0{,}081]$ : l'écart est positif, mais très imprécis (de 0,3 à 8 points !). (c) La puissance, si le vrai écart est celui observé, est d'environ 56 % : l'expérience était sous-dimensionnée (voir le code).

```python
kA, kB, n = 45, 66, 500
pA, pB = kA / n, kB / n
pp = (kA + kB) / (2 * n)
z = (pB - pA) / np.sqrt(pp * (1 - pp) * 2 / n)
print("z =", round(z, 3), "  p =", round(2 * stats.norm.sf(z), 4))
se = np.sqrt(pA * (1 - pA) / n + pB * (1 - pB) / n)
print("IC95 % de la différence : [", round(pB - pA - 1.96 * se, 4), ";", round(pB - pA + 1.96 * se, 4), "]")
print("puissance :", round(stats.norm.cdf((pB - pA) / se - 1.96), 3))
```
<!--sortie-->
```text
z = 2.114   p = 0.0345
IC95 % de la différence : [ 0.0031 ; 0.0809 ]
puissance : 0.563
```

**Corrigé 8.** Tableau : code promo : 30 achats, 70 non ; sans code : 45 achats, 55 non. Totaux : colonnes 75 et 125 ; lignes 100 et 100. Effectifs attendus (sous indépendance) : achats $100\times75/200=37{,}5$ dans chaque ligne ; non-achats $62{,}5$. Chaque case s'écarte de son attendu de $7{,}5$, donc $\chi^2=\sum\frac{(O-E)^2}{E}=2\times\dfrac{7{,}5^2}{37{,}5}+2\times\dfrac{7{,}5^2}{62{,}5}=3{,}0+1{,}8=4{,}8$ (sans correction de continuité), 1 ddl, $p\approx0{,}029$ (0,041 avec la correction de Yates, plus prudente). **Attention : le code promo est associé à *moins* d'achats** (30 % contre 45 %) : le test signale une différence, pas son sens. (Et le test à deux proportions donne $z^2=\chi^2$ : même $p$.)

```python
from scipy.stats import chi2_contingency
tab = np.array([[30, 70], [45, 55]])
chi2, p, ddl, att = chi2_contingency(tab, correction=False)
print("attendus :\n", att)
print("khi-deux =", round(chi2, 3), " p =", round(p, 4), " (avec correction de Yates :", round(chi2_contingency(tab)[1], 4), ")")
pp = 75 / 200
z = (0.45 - 0.30) / np.sqrt(pp * (1 - pp) * 2 / 100)
print("z =", round(z, 3), " z^2 =", round(z**2, 3), " p =", round(2 * stats.norm.sf(abs(z)), 4))
```
<!--sortie-->
```text
attendus :
 [[37.5 62.5]
 [37.5 62.5]]
khi-deux = 4.8  p = 0.0285  (avec correction de Yates : 0.0409 )
z = 2.191  z^2 = 4.8  p = 0.0285
```

**Corrigé 9.** (a) $n=\dfrac{(1{,}96+0{,}8416)^2\,[0{,}2\times0{,}8+0{,}24\times0{,}76]}{0{,}04^2}\approx1\,680$ par version. (b) Pour 22 %, l'effet est deux fois plus petit : $n\approx6\,500$. (c) Diviser l'effet par 2 multiplie $n$ par **environ 4** : $n\propto1/\text{effet}^2$.

```python
za, zb = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
def n_groupe(p1, p2):
    return (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2
print("20 -> 24 % :", int(np.ceil(n_groupe(0.20, 0.24))), "  20 -> 22 % :", int(np.ceil(n_groupe(0.20, 0.22))))
print("rapport :", round(n_groupe(0.20, 0.22) / n_groupe(0.20, 0.24), 2))
```
<!--sortie-->
```text
20 -> 24 % : 1680   20 -> 22 % : 6507
rapport : 3.87
```

**Corrigé 10.** (a) Sans correction : $p<0{,}05$ pour les 5 premières. (b) Bonferroni : seuil $0{,}05/8=0{,}00625$ : seule 0,001 est rejetée. (c) Holm : seuils $0{,}05/8=0{,}00625$, $0{,}05/7=0{,}00714$, $0{,}05/6=0{,}00833$, … : $0{,}001<0{,}00625$ ✓ ; $0{,}008>0{,}00714$ ✗ : on s'arrête. Un seul rejet, comme Bonferroni. (d) BH : seuils $\frac k8\times0{,}05$ : $0{,}00625;\ 0{,}0125;\ 0{,}01875;\ 0{,}025;\ 0{,}03125;\dots$ ; $p_{(1)}=0{,}001\le0{,}00625$ ✓, $p_{(2)}=0{,}008\le0{,}0125$ ✓, $p_{(3)}=0{,}012\le0{,}01875$ ✓, $p_{(4)}=0{,}030>0{,}025$ ✗, $p_{(5)}=0{,}040>0{,}03125$ ✗. Le plus grand $k$ qui convient est 3 : les **trois** premières sont rejetées.

```python
p = np.array([0.001, 0.008, 0.012, 0.030, 0.040, 0.200, 0.500, 0.700])
m = len(p)
print("sans correction :", int((p < 0.05).sum()), "rejets")
print("Bonferroni      :", int((p < 0.05 / m).sum()), "rejets")
rang = np.arange(1, m + 1)
holm = np.cumprod(p < 0.05 / (m - rang + 1))     # on s'arrête au premier échec
print("Holm            :", int(holm.sum()), "rejets")
ok = p <= rang / m * 0.05
print("Benjamini-Hochberg :", int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0, "rejets")
```
<!--sortie-->
```text
sans correction : 5 rejets
Bonferroni      : 1 rejets
Holm            : 1 rejets
Benjamini-Hochberg : 3 rejets
```

---

## Bilan du chapitre 3

Vous savez maintenant :

- **décrire** un jeu de données (position, dispersion, forme, relations) et **toujours dessiner avant de calculer** ;
- **estimer** un paramètre (moments, maximum de vraisemblance), juger un estimateur par son biais et sa variance, et savoir pourquoi on divise par $n-1$ ;
- **quantifier l'incertitude** par des intervalles de confiance (Student, Wilson, bootstrap), sans en faire une mauvaise lecture ;
- **tester** une hypothèse (Student, Welch, proportions, A/B, khi-deux) en distinguant significativité et importance pratique ;
- **dimensionner** une expérience (puissance), et **éviter les faux positifs** (tests multiples, *peeking*) ;
- (en option) **échantillonner** correctement et employer des méthodes **sans hypothèse de loi**.

Le chapitre 4 change de registre : après la théorie, la **pratique du code**. Python, R, algorithmes, NumPy, pandas, visualisations : ce sont les outils qui permettront d'appliquer tout ce que vous venez d'apprendre sur de vraies données.
