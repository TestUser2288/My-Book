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
