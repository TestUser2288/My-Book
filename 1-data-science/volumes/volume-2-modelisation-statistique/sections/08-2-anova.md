## 8.2 L'analyse de la variance (ANOVA)

> 💡 **Intuition.** Pour comparer deux groupes, on utilisait un test de Student. Pour en comparer **quatre**, on pourrait faire les six tests deux à deux, mais cela multiplie les risques de fausse alerte (volume I, section 3.5.5). L'ANOVA pose une seule question globale : **« les moyennes des groupes diffèrent-elles plus que ne le ferait le seul hasard ? »** Et elle y répond en comparant **deux sources de variabilité** : celle **entre** les groupes (l'effet du traitement, s'il existe) et celle **à l'intérieur** des groupes (le bruit). Si la première dépasse nettement la seconde, les groupes ne sont pas interchangeables.

### 8.2.1 Le problème : quatre agencements de vitrine

La gérante a testé quatre agencements de vitrine (« Classique », « Par couleur », « Par thème », « Vedette »). Pendant 48 jours d'ouverture, elle a tiré au sort l'agencement de chaque journée (12 jours par agencement) et relevé les ventes du jour. Les unités expérimentales sont les journées, comme nous l'avons discuté en 8.1.

```python
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("donnees/ch08-vitrines.csv")
print(df.head(6).to_string(index=False))
print()
resume = df.groupby("agencement")["ventes"].agg(n="count", moyenne="mean", ecart_type="std").round(1)
print(resume.sort_values("moyenne").to_string())
print("\nmoyenne générale :", round(df["ventes"].mean(), 1))
```
<!--sortie-->
```text
 jour  agencement  ventes
    1 Par couleur   226.7
    2     Vedette   249.3
    3   Par thème   259.0
    4     Vedette   272.2
    5   Par thème   269.0
    6   Par thème   243.2

              n  moyenne  ecart_type
agencement                          
Classique    12    196.2        38.1
Vedette      12    215.4        28.3
Par couleur  12    224.6        40.7
Par thème    12    237.0        25.5

moyenne générale : 218.3
```

Les moyennes diffèrent, mais les écarts-types sont du même ordre que ces différences : difficile de juger à l'œil. Dessinons les données **avant** de calculer quoi que ce soit (volume I, section 3.1).

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb",
                     "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb", "legend.frameon": False})

ordre = list(resume.sort_values("moyenne").index)
rng = np.random.default_rng(1)
fig, ax = plt.subplots(figsize=(7, 4))
for i, a in enumerate(ordre):
    y = df.loc[df["agencement"] == a, "ventes"]
    ax.scatter(i + rng.uniform(-0.12, 0.12, len(y)), y, s=22, color=BLEU, alpha=0.6, zorder=3)
    ax.hlines(y.mean(), i - 0.3, i + 0.3, color=ORANGE, lw=3, zorder=4)
ax.axhline(df["ventes"].mean(), color="#898781", ls="--", lw=1)
ax.text(len(ordre) - 0.5, df["ventes"].mean() + 3, "moyenne générale", ha="right", color="#52514e", fontsize=8)
ax.set_xticks(range(len(ordre)))
ax.set_xticklabels(ordre)
ax.set_ylabel("ventes du jour (€)")
ax.set_title("Ventes selon l'agencement (un point = une journée, trait orange = moyenne)")
plt.savefig("figures/ch08-vitrines.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Ventes journalières selon l'agencement de la vitrine : chaque point est une journée, le trait orange est la moyenne du groupe, la ligne en pointillés la moyenne générale.](figures/ch08-vitrines.png)

Les nuages se chevauchent beaucoup, mais ils sont ordonnés : « Classique » est en bas, « Par thème » en haut. La différence est-elle réelle ou due au hasard de la répartition des jours ?

### 8.2.2 Décomposer la variabilité : un exemple de neuf nombres

Commençons par un exemple minuscule. Trois agencements, trois journées chacun :

| | journée 1 | journée 2 | journée 3 | moyenne |
|---|---|---|---|---|
| Classique | 190 | 200 | 210 | 200 |
| Par couleur | 205 | 215 | 225 | 215 |
| Par thème | 230 | 240 | 250 | 240 |

La moyenne des neuf valeurs est $\bar y=(200+215+240)/3\approx 218{,}33$. Deux sortes d'écarts :

- l'écart **entre** les groupes : chaque moyenne de groupe s'écarte de la moyenne générale ($-18{,}33$ ; $-3{,}33$ ; $+21{,}67$) ;
- l'écart **à l'intérieur** de chaque groupe : chaque valeur s'écarte de la moyenne de *son* groupe ($-10$, $0$, $+10$, dans les trois groupes).

On mesure chaque sorte d'écart par une **somme de carrés** (volume I, section 3.1.4 pour la variance) :

$$SS_{\text{entre}}=3\left[(-18{,}33)^2+(-3{,}33)^2+(21{,}67)^2\right]=2450,\qquad SS_{\text{dans}}=3\times(100+0+100)=600.$$

Et la variabilité **totale** de l'ensemble des neuf valeurs, $\sum(y-\bar y)^2$, vaut $3050=2450+600$. Ce n'est pas un hasard.

```python
y = np.array([[190, 200, 210], [205, 215, 225], [230, 240, 250]], dtype=float)   # une ligne par groupe
k, n = y.shape
moy_gen, moy_groupes = y.mean(), y.mean(axis=1)

SS_entre = n * ((moy_groupes - moy_gen) ** 2).sum()
SS_dans = ((y - moy_groupes[:, None]) ** 2).sum()
SS_total = ((y - moy_gen) ** 2).sum()
print(f"SS entre = {SS_entre:.0f}, SS dans = {SS_dans:.0f}, somme = {SS_entre + SS_dans:.0f}, SS total = {SS_total:.0f}")

MS_entre, MS_dans = SS_entre / (k - 1), SS_dans / (k * n - k)
F = MS_entre / MS_dans
print(f"F = ({SS_entre:.0f}/{k - 1}) / ({SS_dans:.0f}/{k * n - k}) = {MS_entre:.0f} / {MS_dans:.0f} = {F:.2f}")
print(f"p-valeur = {stats.f.sf(F, k - 1, k * n - k):.4f}   (scipy f_oneway : {stats.f_oneway(*y).pvalue:.4f})")
```
<!--sortie-->
```text
SS entre = 2450, SS dans = 600, somme = 3050, SS total = 3050
F = (2450/2) / (600/6) = 1225 / 100 = 12.25
p-valeur = 0.0076   (scipy f_oneway : 0.0076)
```

> 📐 **Théorème (décomposition de la variance).** Soit $y_{ij}$ la $j$-ième observation du groupe $i$ ($i=1,\dots,k$ ; $j=1,\dots,n_i$), $N=\sum n_i$, $\bar y_i$ la moyenne du groupe et $\bar y$ la moyenne générale. Alors
> $$\underbrace{\sum_{i,j}(y_{ij}-\bar y)^2}_{SS_T}=\underbrace{\sum_i n_i(\bar y_i-\bar y)^2}_{SS_B\ (\text{entre})}+\underbrace{\sum_{i,j}(y_{ij}-\bar y_i)^2}_{SS_W\ (\text{dans})}.$$
> *Démonstration.* On écrit $y_{ij}-\bar y=(y_{ij}-\bar y_i)+(\bar y_i-\bar y)$ et on développe le carré :
> $$\sum_{i,j}(y_{ij}-\bar y)^2=\sum_{i,j}(y_{ij}-\bar y_i)^2+\sum_{i,j}(\bar y_i-\bar y)^2+2\sum_{i}(\bar y_i-\bar y)\underbrace{\sum_{j}(y_{ij}-\bar y_i)}_{=\,0}.$$
> Le double produit s'annule, car la somme des écarts d'un groupe à sa propre moyenne est nulle. Et $\sum_{i,j}(\bar y_i-\bar y)^2=\sum_i n_i(\bar y_i-\bar y)^2$ puisque le terme ne dépend pas de $j$. $\square$

La décomposition est exacte, quelles que soient les données : elle n'a rien de statistique. C'est son **interprétation** qui l'est. Pour en tirer un test, il faut un modèle.

### 8.2.3 Le modèle et le test F

Le **modèle à un facteur** suppose que

$$y_{ij}=\mu+\tau_i+\varepsilon_{ij},\qquad \varepsilon_{ij}\ \text{indépendants},\ \varepsilon_{ij}\sim\mathcal N(0,\sigma^2),\qquad \sum_i n_i\tau_i=0.$$

$\mu$ est la moyenne générale, $\tau_i$ l'**effet** du niveau $i$ (l'écart de sa moyenne vraie à $\mu$) et $\varepsilon_{ij}$ le bruit. L'hypothèse nulle « tous les agencements se valent » s'écrit $H_0:\tau_1=\dots=\tau_k=0$.

On compare maintenant les sommes de carrés **ramenées à leurs degrés de liberté** : $MS_B=SS_B/(k-1)$ et $MS_W=SS_W/(N-k)$ (*mean squares*, « carrés moyens »). Pourquoi ces diviseurs ?

> 📐 **Ce que valent les carrés moyens.**
> 1. **$MS_W$ estime toujours $\sigma^2$**, effet ou non. En effet, dans le groupe $i$, $\sum_j(y_{ij}-\bar y_i)^2/\sigma^2\sim\chi^2_{n_i-1}$ (résultat classique pour des observations gaussiennes, que nous admettons ; la loi du khi-deux a été rencontrée au volume I, section 3.4.6, dans un autre rôle) ; les $k$ groupes étant indépendants, la somme $SS_W/\sigma^2$ suit une loi $\chi^2_{N-k}$, d'espérance $N-k$. Donc $\mathbb E[MS_W]=\sigma^2$.
> 2. **$MS_B$ estime $\sigma^2$ plus un terme dû aux effets** : un calcul direct donne
> $$\mathbb E[MS_B]=\sigma^2+\frac{\sum_i n_i\tau_i^2}{k-1}.$$
> Sous $H_0$ (tous les $\tau_i=0$), $\mathbb E[MS_B]=\sigma^2$ aussi ; sinon $MS_B$ est plus grand.
> 3. Sous $H_0$, $SS_B/\sigma^2\sim\chi^2_{k-1}$ et **$SS_B$ est indépendant de $SS_W$** (théorème de Cochran : la décomposition en sommes de carrés orthogonales donne des $\chi^2$ indépendants).
>
> Le quotient de deux $\chi^2$ indépendants divisés par leurs degrés de liberté suit une **loi de Fisher** :
> $$F=\frac{MS_B}{MS_W}\ \underset{H_0}{\sim}\ \mathcal F(k-1,\;N-k).$$
> Sous $H_0$, $F$ vaut environ 1 ; si les effets existent, $F$ est tiré vers le haut. On rejette donc $H_0$ quand $F$ est **grand** (test unilatéral à droite).

Appliquons cela aux données de la gérante, d'abord à la main, ensuite avec les bibliothèques :

```python
from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm

k, N = df["agencement"].nunique(), len(df)
g = df.groupby("agencement")["ventes"]
moy_gen = df["ventes"].mean()
SSB = (g.size() * (g.mean() - moy_gen) ** 2).sum()
SSW = ((df["ventes"] - g.transform("mean")) ** 2).sum()
SST = ((df["ventes"] - moy_gen) ** 2).sum()
MSB, MSW = SSB / (k - 1), SSW / (N - k)
F = MSB / MSW
print(f"SSB = {SSB:.0f}  SSW = {SSW:.0f}  SST = {SST:.0f}  (SSB + SSW = {SSB + SSW:.0f})")
print(f"MSB = {MSB:.0f}  MSW = {MSW:.0f}  F = {F:.3f}  p = {stats.f.sf(F, k - 1, N - k):.4f}  (ddl : {k - 1} et {N - k})")
print()
modele = ols("ventes ~ C(agencement)", data=df).fit()
print(anova_lm(modele).round(3).to_string())
print("\nscipy f_oneway :", stats.f_oneway(*[x.to_numpy() for _, x in g]))
```
<!--sortie-->
```text
SSB = 10595  SSW = 50168  SST = 60763  (SSB + SSW = 60763)
MSB = 3532  MSW = 1140  F = 3.097  p = 0.0363  (ddl : 3 et 44)

                 df     sum_sq   mean_sq      F  PR(>F)
C(agencement)   3.0  10595.062  3531.687  3.097   0.036
Residual       44.0  50168.171  1140.186    NaN     NaN

scipy f_oneway : F_onewayResult(statistic=np.float64(3.097466867203288), pvalue=np.float64(0.03633773429167083))
```

Les trois calculs coïncident. Le test rejette l'hypothèse « tous les agencements se valent » à 5 %, sans que la preuve soit écrasante : $p\approx0{,}036$ est proche du seuil de 5 %. Nous reviendrons en 8.2.10 sur la puissance de cette expérience.

> ⚠️ **Ce que l'ANOVA ne dit pas.** Un $F$ significatif dit que **au moins un** agencement diffère des autres ; il ne dit pas **lesquels**. Pour cela, il faut des comparaisons deux à deux *corrigées* (8.2.6).

### 8.2.4 L'ANOVA, le test de Student et la régression sont le même outil

**Avec deux groupes**, l'ANOVA redonne le test de Student à variances égales : $F=t^2$, avec la même p-valeur.

```python
deux = df[df["agencement"].isin(["Classique", "Par thème"])]
t = stats.ttest_ind(deux.loc[deux["agencement"] == "Par thème", "ventes"],
                    deux.loc[deux["agencement"] == "Classique", "ventes"], equal_var=True)
F2 = stats.f_oneway(*[x["ventes"].to_numpy() for _, x in deux.groupby("agencement")])
print(f"Student : t = {t.statistic:.4f}, t² = {t.statistic ** 2:.4f}, p = {t.pvalue:.5f}")
print(f"ANOVA   : F = {F2.statistic:.4f},              p = {F2.pvalue:.5f}")
```
<!--sortie-->
```text
Student : t = 3.0796, t² = 9.4837, p = 0.00548
ANOVA   : F = 9.4837,              p = 0.00548
```

**Avec $k$ groupes**, c'est une **régression linéaire** (chapitre 1) sur des variables indicatrices : on prend un groupe de référence et on code les autres par $0/1$. La constante est alors la moyenne du groupe de référence et chaque coefficient est l'écart de moyenne par rapport à lui. Le test $F$ global de la régression (section 1.2) *est* le test $F$ de l'ANOVA, et le $R^2$ de la régression vaut $SS_B/SS_T$.

```python
print(modele.params.round(2).to_string())
print(f"\nF global de la régression = {modele.fvalue:.3f}, p = {modele.f_pvalue:.4f}")
print(f"R² = {modele.rsquared:.4f}  et  SSB/SST = {SSB / SST:.4f}")
```
<!--sortie-->
```text
Intercept                       196.25
C(agencement)[T.Par couleur]     28.36
C(agencement)[T.Par thème]       40.72
C(agencement)[T.Vedette]         19.19

F global de la régression = 3.097, p = 0.0363
R² = 0.1744  et  SSB/SST = 0.1744
```

La constante est la moyenne du groupe de référence (le premier par ordre alphabétique, « Classique »), et les autres coefficients sont les écarts à ce groupe. L'ANOVA n'est donc pas un outil à part : c'est un **cas particulier du modèle linéaire** dont les variables explicatives sont qualitatives. Cette vue unifiée sera précieuse pour les plans factoriels (8.3), où les « effets » seront exactement des coefficients.

### 8.2.5 Vérifier les hypothèses

Le test $F$ suppose des erreurs **indépendantes** (garanti par la randomisation et le bon choix de l'unité, 8.1), **gaussiennes** et de **même variance** dans tous les groupes. On les vérifie sur les **résidus** $e_{ij}=y_{ij}-\bar y_i$.

```python
residus = modele.resid
groupes = [x["ventes"].to_numpy() for _, x in df.groupby("agencement")]

print("Shapiro-Wilk (normalité des résidus)    : p =", round(stats.shapiro(residus).pvalue, 3))
print("Levene/Brown-Forsythe (variances égales) : p =", round(stats.levene(*groupes, center="median").pvalue, 3))
print("Bartlett (variances égales, sensible à la non-normalité) : p =", round(stats.bartlett(*groupes).pvalue, 3))
sd = df.groupby("agencement")["ventes"].std()
print(f"rapport plus grand / plus petit écart-type : {sd.max() / sd.min():.2f}")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(9, 3.6))
(osm, osr), (pente, ordonnee, _) = stats.probplot(residus, dist="norm")
ax1.scatter(osm, osr, s=20, color=BLEU)
ax1.plot(osm, pente * np.asarray(osm) + ordonnee, color=ORANGE, lw=1.5)
ax1.set_xlabel("quantiles théoriques de la loi normale")
ax1.set_ylabel("résidus (€)")
ax1.set_title("Diagramme quantile-quantile")
ax2.scatter(modele.fittedvalues, residus, s=20, color=BLEU)
ax2.axhline(0, color="#898781", lw=1)
ax2.set_xlabel("valeur ajustée = moyenne du groupe (€)")
ax2.set_ylabel("résidus (€)")
ax2.set_title("Résidus selon la valeur ajustée")
plt.tight_layout()
plt.savefig("figures/ch08-anova-diagnostics.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
Shapiro-Wilk (normalité des résidus)    : p = 0.521
Levene/Brown-Forsythe (variances égales) : p = 0.276
Bartlett (variances égales, sensible à la non-normalité) : p = 0.369
rapport plus grand / plus petit écart-type : 1.60
figure enregistrée
```

![À gauche : diagramme quantile-quantile des résidus de l'ANOVA, qui suivent à peu près la droite. À droite : résidus selon la moyenne du groupe, sans structure visible ni dispersion qui varie nettement d'un groupe à l'autre.](figures/ch08-anova-diagnostics.png)

Aucun signal inquiétant : le diagramme quantile-quantile suit la droite et la dispersion des résidus est comparable d'un groupe à l'autre. Si ce n'était pas le cas :

- **variances inégales** : utiliser l'ANOVA de **Welch** (qui n'impose pas l'égalité des variances) ;
- **résidus très non gaussiens** : transformer la réponse (logarithme pour des montants, volume I, section 3.1.5) ou utiliser le test de **Kruskal-Wallis** (volume I, section 3.7.3) ;
- **dépendance** entre unités : c'est un défaut du **plan**, et aucune correction après coup ne le répare.

```python
from statsmodels.stats.oneway import anova_oneway

welch = anova_oneway(groupes, use_var="unequal", welch_correction=True)
print(f"ANOVA de Welch  : F = {welch.statistic:.3f}, p = {welch.pvalue:.4f}")
print(f"Kruskal-Wallis  : H = {stats.kruskal(*groupes).statistic:.3f}, p = {stats.kruskal(*groupes).pvalue:.4f}")
```
<!--sortie-->
```text
ANOVA de Welch  : F = 3.259, p = 0.0390
Kruskal-Wallis  : H = 7.009, p = 0.0716
```

Les ANOVA classique et de Welch concluent de la même façon ($p=0{,}036$ et $p=0{,}039$). Le test de Kruskal-Wallis, qui travaille sur les rangs, est un peu moins tranché ($p=0{,}072$) : il passe juste au-dessus du seuil de 5 %. Il n'y a pas de contradiction, mais un **avertissement honnête** : la preuve est **limite**, et la conclusion « au moins un agencement diffère » ne doit pas être présentée comme acquise au-delà de tout doute. C'est le genre de nuance qu'une p-valeur isolée ferait oublier.

### 8.2.6 Quels groupes diffèrent ? Les comparaisons multiples

Avec $k=4$ niveaux, il y a $\binom42=6$ paires. Si l'on faisait six tests à 5 %, la probabilité d'au moins une fausse alerte n'est plus 5 % mais proche de $1-0{,}95^6\approx26\,\%$ (volume I, section 3.5.5). Il faut un procédé qui contrôle le risque **global** (*familywise*). Deux classiques :

- **Bonferroni** : rejeter si $p<\alpha/m$ ($m$ = nombre de comparaisons). Simple mais conservateur.
- **Tukey HSD** (*Honestly Significant Difference*), conçu exactement pour comparer **toutes les paires de moyennes** : deux moyennes diffèrent si leur écart dépasse
$$\text{HSD}=q_{1-\alpha;\,k,\,N-k}\sqrt{\frac{MS_W}{n}}\qquad(\text{groupes de même taille } n),$$
où $q$ est le quantile de la **loi de l'étendue studentisée** (la loi du plus grand écart entre $k$ moyennes, divisé par son écart-type estimé). Plus on compare de groupes, plus ce seuil monte.

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd

n_par = N // k
q = stats.studentized_range.ppf(0.95, k, N - k)
hsd = q * np.sqrt(MSW / n_par)
print(f"q(0.95 ; k={k}, ddl={N - k}) = {q:.3f}  ->  HSD = {q:.3f} x sqrt({MSW:.0f}/{n_par}) = {hsd:.1f} €")
lsd = stats.t.ppf(0.975, N - k) * np.sqrt(2 * MSW / n_par)
print(f"(seuil d'un test de Student non corrigé, pour une seule paire : {lsd:.1f} €)\n")

moy = g.mean()
paires = [(a, b) for i, a in enumerate(moy.index) for b in moy.index[i + 1:]]
for a, b in paires:
    ecart = moy[b] - moy[a]
    print(f"{b:12s} - {a:12s} : écart = {ecart:6.1f} €   {'> HSD : significatif' if abs(ecart) > hsd else '<= HSD'}")

tukey = pairwise_tukeyhsd(df["ventes"], df["agencement"], alpha=0.05)
tab = pd.DataFrame(tukey._results_table.data[1:], columns=tukey._results_table.data[0])
print()
print(tab.round(3).to_string(index=False))
```
<!--sortie-->
```text
q(0.95 ; k=4, ddl=44) = 3.776  ->  HSD = 3.776 x sqrt(1140/12) = 36.8 €
(seuil d'un test de Student non corrigé, pour une seule paire : 27.8 €)

Par couleur  - Classique    : écart =   28.4 €   <= HSD
Par thème    - Classique    : écart =   40.7 €   > HSD : significatif
Vedette      - Classique    : écart =   19.2 €   <= HSD
Par thème    - Par couleur  : écart =   12.4 €   <= HSD
Vedette      - Par couleur  : écart =   -9.2 €   <= HSD
Vedette      - Par thème    : écart =  -21.5 €   <= HSD

     group1      group2  meandiff  p-adj   lower  upper  reject
  Classique Par couleur    28.358  0.183  -8.448 65.165   False
  Classique   Par thème    40.725  0.025   3.918 77.532    True
  Classique     Vedette    19.192  0.511 -17.615 55.998   False
Par couleur   Par thème    12.367  0.806 -24.440 49.173   False
Par couleur     Vedette    -9.167  0.910 -45.973 27.640   False
  Par thème     Vedette   -21.533  0.410 -58.340 15.273   False
```

La partie « à la main » et la bibliothèque donnent les mêmes décisions. On voit aussi le prix de la prudence : avec 6 comparaisons, il faut un écart d'environ 37 € pour conclure, alors qu'un test non corrigé se contenterait d'environ 28 € (deux écarts, 28,4 et 40,7, l'auraient franchi). Après correction, un seul écart franchit la barre : le plus grand, « Par thème » contre « Classique » (écart de 40,7 €, $p$ ajustée $=0{,}025$, intervalle de confiance simultané de 3,9 à 77,5 € : l'effet est détecté, mais **très imprécis**). Avec la correction de Bonferroni (ici sur des tests de Student séparés), on arrive à la même conclusion : seul « Par thème » contre « Classique » reste significatif ($p$ brute $0{,}0055$, multipliée par 6 : $0{,}033$).

```python
brut = {}
for a, b in paires:
    brut[(a, b)] = stats.ttest_ind(g.get_group(b), g.get_group(a), equal_var=True).pvalue
for (a, b), p in brut.items():
    print(f"{b:12s} - {a:12s} : p brute = {p:.4f} ; p Bonferroni (x6) = {min(1, 6 * p):.4f}")
```
<!--sortie-->
```text
Par couleur  - Classique    : p brute = 0.0919 ; p Bonferroni (x6) = 0.5514
Par thème    - Classique    : p brute = 0.0055 ; p Bonferroni (x6) = 0.0329
Vedette      - Classique    : p brute = 0.1752 ; p Bonferroni (x6) = 1.0000
Par thème    - Par couleur  : p brute = 0.3823 ; p Bonferroni (x6) = 1.0000
Vedette      - Par couleur  : p brute = 0.5288 ; p Bonferroni (x6) = 1.0000
Vedette      - Par thème    : p brute = 0.0632 ; p Bonferroni (x6) = 0.3794
```

> 💡 **Un contraste planifié, pour une question précise.** Si, **avant** l'expérience, la gérante s'était demandé « l'agencement *Par thème* fait-il mieux que la moyenne des trois autres ? », elle pouvait tester **un seul** contraste $c=\bar y_{\text{thème}}-\tfrac13(\bar y_{\text{classique}}+\bar y_{\text{couleur}}+\bar y_{\text{vedette}})$, avec un seul test. Un contraste est une combinaison linéaire des moyennes dont les poids somment à 0 ; son écart-type estimé est $\sqrt{MS_W\sum_i c_i^2/n_i}$, et sa statistique suit une loi de Student à $N-k$ degrés de liberté. Poser la question **avant** évite d'avoir à corriger des dizaines de comparaisons possibles.

```python
poids = pd.Series({"Classique": -1 / 3, "Par couleur": -1 / 3, "Par thème": 1.0, "Vedette": -1 / 3})
estim = (poids * moy).sum()
se = np.sqrt(MSW * (poids ** 2 / g.size()).sum())
t_c = estim / se
ic = (estim - stats.t.ppf(0.975, N - k) * se, estim + stats.t.ppf(0.975, N - k) * se)
print(f"contraste thème - moyenne des autres = {estim:.1f} €  (écart-type {se:.1f})")
print(f"t = {t_c:.2f}, p = {2 * stats.t.sf(abs(t_c), N - k):.4f}, IC95 = [{ic[0]:.1f} ; {ic[1]:.1f}]")
```
<!--sortie-->
```text
contraste thème - moyenne des autres = 24.9 €  (écart-type 11.3)
t = 2.21, p = 0.0324, IC95 = [2.2 ; 47.6]
```

Le thème l'emporte d'environ 25 € sur la moyenne des trois autres ($p=0{,}032$, intervalle de 2 à 48 €). Une **seule** question posée à l'avance, donc **un seul** test, sans correction : la conclusion est plus nette que celle des six comparaisons deux à deux, mais elle n'est honnête que parce que la question a été choisie **avant** de voir les données.

```python
x = np.arange(len(tab))
fig, ax = plt.subplots(figsize=(7, 3.8))
for i, r in tab.iterrows():
    couleur = ORANGE if r["reject"] else BLEU
    ax.hlines(i, r["lower"], r["upper"], color=couleur, lw=3)
    ax.scatter(r["meandiff"], i, color=couleur, zorder=3)
ax.axvline(0, color="#898781", lw=1)
ax.set_yticks(x)
ax.set_yticklabels([f"{r['group2']} - {r['group1']}" for _, r in tab.iterrows()])
ax.set_xlabel("écart de moyennes (€) avec intervalle de confiance simultané à 95 % (Tukey)")
ax.set_title("Comparaisons deux à deux : en orange, celles dont l'intervalle exclut 0")
plt.savefig("figures/ch08-tukey.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Intervalles de confiance simultanés de Tukey pour les six écarts de moyennes ; seul l'écart Par thème - Classique est entièrement à droite de zéro.](figures/ch08-tukey.png)

### 8.2.7 La taille de l'effet

Une p-valeur dit si l'effet est **détectable**, pas s'il est **important** (volume I, section 3.5.3). Pour l'ANOVA, la mesure usuelle est la part de variance expliquée par le facteur :

$$\eta^2=\frac{SS_B}{SS_T}\quad(\text{c'est le }R^2\text{ de la régression}),\qquad \omega^2=\frac{SS_B-(k-1)MS_W}{SS_T+MS_W},\qquad f=\sqrt{\frac{\eta^2}{1-\eta^2}}.$$

$\eta^2$ est **biaisé vers le haut** dans les petits échantillons ; $\omega^2$ en est une version corrigée. Le $f$ de Cohen est l'écart-type des moyennes des groupes divisé par $\sigma$ ; ses repères habituels sont 0,10 (petit), 0,25 (moyen), 0,40 (grand).

```python
eta2 = SSB / SST
omega2 = (SSB - (k - 1) * MSW) / (SST + MSW)
f_cohen = np.sqrt(eta2 / (1 - eta2))
print(f"eta² = {eta2:.3f}   omega² = {omega2:.3f}   f de Cohen = {f_cohen:.3f}")
```
<!--sortie-->
```text
eta² = 0.174   omega² = 0.116   f de Cohen = 0.460
```

L'agencement explique donc environ 17 % de la variance des ventes journalières ($\eta^2=0{,}174$), ou 12 % après correction du biais ($\omega^2=0{,}116$) : avec $f=0{,}46$, un effet **grand** selon les repères de Cohen, mais noyé dans un bruit important (les ventes d'une journée varient beaucoup, quel que soit l'agencement). Le $\omega^2$ est la valeur à retenir : le $\eta^2$ flatte toujours un peu un petit échantillon.

### 8.2.8 Les blocs : retirer du bruit connu

La gérante refait l'expérience autrement. Elle sait que les semaines diffèrent beaucoup (soldes, fêtes, météo) : elle découpe l'expérience en **8 semaines** (les **blocs**), et chaque semaine elle teste **chacun des quatre agencements une fois**, dans un ordre tiré au hasard. Soit 32 journées. C'est un **plan en blocs complets randomisés**.

Le modèle ajoute un effet de bloc :

$$y_{ij}=\mu+\tau_i+\beta_j+\varepsilon_{ij},\qquad i=1..k\ (\text{traitements}),\ j=1..b\ (\text{blocs}),$$

et la décomposition devient $SS_T=SS_{\text{trait}}+SS_{\text{blocs}}+SS_E$, avec $k-1$, $b-1$ et $(k-1)(b-1)$ degrés de liberté. La démonstration est la même qu'en 8.2.2, avec trois sortes d'écarts au lieu de deux. Vérifions-la sur un exemple de neuf nombres, trois traitements et trois semaines :

```python
Y = np.array([[10, 12, 14],      # semaine 1 : traitements A, B, C
              [20, 22, 27],      # semaine 2
              [30, 31, 35]], dtype=float)
b_, k_ = Y.shape
mg = Y.mean()
SS_blocs = k_ * ((Y.mean(axis=1) - mg) ** 2).sum()
SS_trait = b_ * ((Y.mean(axis=0) - mg) ** 2).sum()
SS_err = ((Y - Y.mean(axis=1, keepdims=True) - Y.mean(axis=0, keepdims=True) + mg) ** 2).sum()
SS_tot = ((Y - mg) ** 2).sum()
print(f"blocs : {SS_blocs:.2f}   traitements : {SS_trait:.2f}   erreur : {SS_err:.2f}")
print(f"somme = {SS_blocs + SS_trait + SS_err:.2f}   total = {SS_tot:.2f}")
print(f"ddl : blocs {b_ - 1}, traitements {k_ - 1}, erreur {(b_ - 1) * (k_ - 1)}")
```
<!--sortie-->
```text
blocs : 602.00   traitements : 44.67   erreur : 3.33
somme = 650.00   total = 650.00
ddl : blocs 2, traitements 2, erreur 4
```

Ici, presque toute la variabilité vient des blocs (les semaines diffèrent beaucoup) ; le résidu, une fois les blocs retirés, est minuscule. Voyons ce que cela change sur les vraies données de l'expérience en blocs :

```python
bl = pd.read_csv("donnees/ch08-vitrines-blocs.csv")
print(bl.pivot(index="semaine", columns="agencement", values="ventes").round(0).astype(int).to_string())

sans_bloc = anova_lm(ols("ventes ~ C(agencement)", bl).fit())
avec_bloc = anova_lm(ols("ventes ~ C(agencement) + C(semaine)", bl).fit())
print("\n--- en ignorant les semaines (ANOVA à un facteur) ---")
print(sans_bloc.round(3).to_string())
print("\n--- en tenant compte des semaines (blocs) ---")
print(avec_bloc.round(3).to_string())
```
<!--sortie-->
```text
agencement  Classique  Par couleur  Par thème  Vedette
semaine                                               
1                 202          191        236      208
2                 130          167        192      162
3                 226          256        276      219
4                 142          114        164      134
5                 234          261        272      231
6                 184          220        230      195
7                 132          153        191      174
8                 185          210        217      203

--- en ignorant les semaines (ANOVA à un facteur) ---
                 df     sum_sq   mean_sq      F  PR(>F)
C(agencement)   3.0   7932.631  2644.210  1.542   0.225
Residual       28.0  48007.159  1714.541    NaN     NaN

--- en tenant compte des semaines (blocs) ---
                 df     sum_sq   mean_sq       F  PR(>F)
C(agencement)   3.0   7932.631  2644.210  15.228     0.0
C(semaine)      7.0  44360.712  6337.245  36.496     0.0
Residual       21.0   3646.447   173.640     NaN     NaN
```

C'est la même mesure, les mêmes 32 ventes, et pourtant la conclusion change du tout au tout. Sans les blocs, l'effet de l'agencement est noyé dans la variabilité entre semaines (qui se retrouve dans le résidu) : le test ne détecte rien ($F=1{,}54$, $p=0{,}225$). Avec les blocs, la variabilité entre semaines est **isolée** dans sa propre ligne : le carré moyen de l'erreur s'effondre (d'environ 1 715 à 174), et l'effet de l'agencement devient très significatif ($F=15{,}2$). Le numérateur, lui, n'a pas bougé (même $SS_{\text{trait}}$) : **seul le bruit a diminué**. On quantifie le gain par l'**efficacité relative** du plan en blocs : le facteur par lequel il aurait fallu multiplier le nombre de répétitions d'un plan sans blocs pour avoir la même précision.

```python
b, kk = bl["semaine"].nunique(), bl["agencement"].nunique()
MSE_bloc = avec_bloc.loc["Residual", "mean_sq"]
MS_blocs = avec_bloc.loc["C(semaine)", "mean_sq"]
ER = ((b - 1) * MS_blocs + b * (kk - 1) * MSE_bloc) / ((b * kk - 1) * MSE_bloc)
print(f"efficacité relative du plan en blocs = {ER:.1f}")

# comparaison des agencements à l'intérieur des blocs (Tukey avec le carré moyen de l'erreur du modèle à blocs)
moyennes = bl.groupby("agencement")["ventes"].mean()
hsd_bloc = stats.studentized_range.ppf(0.95, kk, (b - 1) * (kk - 1)) * np.sqrt(MSE_bloc / b)
print(f"HSD (blocs) = {hsd_bloc:.1f} €")
print((moyennes - moyennes["Classique"]).round(1).to_string())
```
<!--sortie-->
```text
efficacité relative du plan en blocs = 9.0
HSD (blocs) = 18.4 €
agencement
Classique       0.0
Par couleur    17.1
Par thème      42.9
Vedette        11.3
```

Ici l'efficacité relative est d'environ **9** : un plan sans blocs aurait demandé à peu près neuf fois plus de journées par agencement (de l'ordre de 70 semaines au lieu de 8) pour atteindre la même précision. Et le seuil de Tukey n'est plus que de 18 € (contre 37 € dans l'expérience sans blocs) : avec les mêmes quatre agencements, on distingue maintenant des écarts deux fois plus petits. « Par thème » dépasse « Classique » de 43 €, « Par couleur » de 17 €, juste sous le seuil, et « Vedette » de 11 €.

> ⚠️ **Deux précautions.**
> 1. Les blocs se **choisissent avant** l'expérience, parce qu'ils sont *connus* comme source de variabilité. On bloque sur ce qui varie beaucoup (la semaine), pas sur n'importe quoi : chaque bloc coûte des degrés de liberté à l'erreur.
> 2. Le modèle suppose que **l'effet du traitement est le même dans tous les blocs** (pas d'interaction traitement × bloc, d'ailleurs non estimable avec une seule observation par case). Si les semaines réagissaient différemment aux agencements, cette hypothèse serait fausse. Avec deux traitements seulement, le plan en blocs est exactement le **test de Student apparié**. Quand les blocs sont des échantillons tirés au sein d'une population plus large, on les traite comme des effets **aléatoires** (modèles mixtes, section 1.7).

### 8.2.9 Deux facteurs et leur interaction

La gérante s'intéresse maintenant à l'**emballage** (Kraft, Tissu, Coffret) et au **canal** de la commande (Site, Réseaux). Pour chacune des 6 combinaisons, elle observe 10 commandes (60 au total) et relève le **panier** en €. On obtient un plan **factoriel $3\times2$ avec répétitions**.

Le modèle à deux facteurs avec interaction s'écrit

$$y_{ijr}=\mu+\alpha_i+\beta_j+(\alpha\beta)_{ij}+\varepsilon_{ijr},$$

où $\alpha_i$ est l'effet de l'emballage $i$, $\beta_j$ celui du canal $j$, et $(\alpha\beta)_{ij}$ l'**interaction** : ce qu'il faut ajouter à la somme des deux effets principaux pour retrouver la moyenne de la case $(i,j)$. S'il n'y a pas d'interaction, les effets s'**additionnent** ; sinon, l'effet de l'emballage dépend du canal. Les sommes de carrés se décomposent comme en 8.2.2 : $SS_T=SS_A+SS_B+SS_{AB}+SS_E$.

```python
ec = pd.read_csv("donnees/ch08-emballage-canal.csv")
table = ec.pivot_table(index="emballage", columns="canal", values="panier", aggfunc="mean").loc[["Kraft", "Tissu", "Coffret"]]
table["moyenne ligne"] = table.mean(axis=1)
table.loc["moyenne colonne"] = table.mean()
print(table.round(1).to_string())
```
<!--sortie-->
```text
canal            Réseaux  Site  moyenne ligne
emballage                                      
Kraft                 43.5  48.0           45.7
Tissu                 48.0  50.3           49.2
Coffret               69.8  60.3           65.0
moyenne colonne       53.8  52.9           53.3
```

Lisez les moyennes des cases. Sur le **Site**, passer du Kraft au Coffret fait gagner une dizaine de euros ; sur **Réseaux**, le gain est environ **deux fois plus grand**. L'effet de l'emballage dépend du canal : c'est une interaction. Représentons-la, avant de la tester.

```python
fig, ax = plt.subplots(figsize=(6.2, 3.8))
for canal, couleur in [("Site", BLEU), ("Réseaux", ORANGE)]:
    m = ec[ec["canal"] == canal].groupby("emballage")["panier"].mean().loc[["Kraft", "Tissu", "Coffret"]]
    ax.plot(m.index, m.values, "o-", color=couleur, lw=2)
    ax.text(2.05, m.values[-1], canal, color=couleur, va="center")
ax.set_xlim(-0.2, 2.6)
ax.set_ylabel("panier moyen (€)")
ax.set_title("Graphique d'interaction : les courbes ne sont pas parallèles")
plt.savefig("figures/ch08-interaction.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Graphique d'interaction : panier moyen selon l'emballage, une courbe par canal. Les deux courbes montent avec le niveau d'emballage mais celle d'Réseaux monte plus fort, donc elles ne sont pas parallèles.](figures/ch08-interaction.png)

> 💡 **Lire un graphique d'interaction.** Des courbes **parallèles** signifient pas d'interaction (les effets s'additionnent). Des courbes qui **s'écartent** ou **se croisent** signalent une interaction. Ce graphique est le premier outil à regarder pour deux facteurs.

Le test :

```python
mod2 = ols("panier ~ C(emballage) * C(canal)", data=ec).fit()
aov2 = anova_lm(mod2)
print(aov2.round(3).to_string())

# vérification à la main de SS_emballage = r * b * somme des (moyenne de l'emballage - moyenne générale)²
r, nb_canaux = 10, 2
mg = ec["panier"].mean()
ss_emb = r * nb_canaux * ((ec.groupby("emballage")["panier"].mean() - mg) ** 2).sum()
print(f"\nSS emballage à la main = {ss_emb:.1f}  (tableau : {aov2.loc['C(emballage)', 'sum_sq']:.1f})")
```
<!--sortie-->
```text
                         df    sum_sq   mean_sq       F  PR(>F)
C(emballage)            2.0  4248.196  2124.098  39.749   0.000
C(canal)                1.0    12.513    12.513   0.234   0.630
C(emballage):C(canal)   2.0   569.809   284.905   5.331   0.008
Residual               54.0  2885.656    53.438     NaN     NaN

SS emballage à la main = 4248.2  (tableau : 4248.2)
```

On lit le tableau **de bas en haut** : on teste d'abord l'**interaction**. Si elle est significative, l'interprétation des effets principaux devient **trompeuse**, car un effet principal est une moyenne sur l'autre facteur, qui peut cacher des effets de signes ou d'ampleurs différents. Ici, l'interaction est significative ; l'effet de l'emballage est très fort. En revanche, l'effet principal du **canal** est quasiment nul : ce n'est pas que le canal n'a aucune importance (il joue sur l'effet du coffret), c'est que, **en moyenne sur les emballages**, les deux canaux se compensent. C'est le piège classique. Quand il y a interaction, on étudie les **effets simples** : l'effet d'un facteur **à chaque niveau** de l'autre.

```python
for canal in ["Site", "Réseaux"]:
    sous = ec[ec["canal"] == canal]
    a = anova_lm(ols("panier ~ C(emballage)", sous).fit())
    m = sous.groupby("emballage")["panier"].mean()
    print(f"{canal:10s}: F emballage = {a.loc['C(emballage)', 'F']:.1f}, p = {a.loc['C(emballage)', 'PR(>F)']:.4f} ; "
          f"gain Coffret - Kraft = {m['Coffret'] - m['Kraft']:.1f} €")
```
<!--sortie-->
```text
Site      : F emballage = 7.1, p = 0.0032 ; gain Coffret - Kraft = 12.3 €
Réseaux : F emballage = 42.1, p = 0.0000 ; gain Coffret - Kraft = 26.3 €
```

> ⚠️ **Plans déséquilibrés.** Ici, chaque case contient 10 observations (plan **équilibré**) : les sommes de carrés sont uniques et les facteurs « orthogonaux ». Quand les effectifs diffèrent selon les cases, la décomposition dépend de l'ordre des facteurs (sommes de carrés de type I, II ou III). Préférez alors l'interprétation par les **coefficients du modèle** et des tests ciblés plutôt que la lecture mécanique du tableau d'ANOVA. C'est une raison de plus de **planifier des plans équilibrés**.

### 8.2.10 Combien d'observations ? La puissance d'une ANOVA

Avant l'expérience, on doit se demander : *si l'effet que je cherche existe vraiment, aurai-je de bonnes chances de le voir ?* C'est la **puissance** (volume I, section 3.5.4). Pour l'ANOVA, sous une hypothèse alternative donnée, la statistique $F$ suit une loi de Fisher **non centrale**, de paramètre de non-centralité

$$\lambda=\frac{\sum_i n_i\tau_i^2}{\sigma^2}=N f^2,$$

où $f=\sqrt{\sum_i\tau_i^2/k}\,/\,\sigma$ est l'effet de Cohen (8.2.7). La puissance est $\mathbb P\left(F>F_{1-\alpha}\right)$ sous cette loi.

Reprenons l'expérience de la vitrine **telle qu'elle a été planifiée** : moyennes vraies 200, 215, 240 et 205 €, écart-type $\sigma=30$ €, 12 jours par agencement.

```python
from statsmodels.stats.power import FTestAnovaPower

mu_vrai = np.array([200, 215, 240, 205])
sigma = 30
f_plan = np.sqrt(((mu_vrai - mu_vrai.mean()) ** 2).mean()) / sigma
print(f"effet de Cohen prévu : f = {f_plan:.3f}")

def puissance(n_par_groupe, f=f_plan, k=4, alpha=0.05):
    N = n_par_groupe * k
    ddl1, ddl2 = k - 1, N - k
    seuil = stats.f.ppf(1 - alpha, ddl1, ddl2)
    return stats.ncf.sf(seuil, ddl1, ddl2, N * f ** 2)       # lambda = N f²

print(f"puissance avec 12 jours par agencement : {puissance(12):.3f}")
print(f"(statsmodels : {FTestAnovaPower().power(effect_size=f_plan, nobs=48, alpha=0.05, k_groups=4):.3f})")

# vérification par simulation : on rejoue l'expérience 5000 fois
rng = np.random.default_rng(85)
rejets = 0
for _ in range(5000):
    echantillons = [m + rng.normal(0, sigma, 12) for m in mu_vrai]
    rejets += stats.f_oneway(*echantillons).pvalue < 0.05
print(f"fréquence de rejet simulée : {rejets / 5000:.3f}")
```
<!--sortie-->
```text
effet de Cohen prévu : f = 0.514
puissance avec 12 jours par agencement : 0.826
(statsmodels : 0.826)
fréquence de rejet simulée : 0.820
```

La puissance **prévue** était d'environ **83 %** : la formule (loi de Fisher non centrale), `statsmodels` et la simulation (5 000 expériences rejouées) s'accordent à quelques millièmes près. Avec l'effet que la gérante espérait, l'expérience de 12 jours par agencement était donc **bien dimensionnée**. Le $p=0{,}036$ observé, proche du seuil, n'a rien de contradictoire : le $F$ observé (3,10) est simplement inférieur à celui qu'on attend en moyenne avec l'effet espéré (environ $1+\lambda/(k-1)\approx5{,}2$, avec $\lambda=Nf^2\approx12{,}7$) : une fluctuation d'échantillonnage ordinaire, qui arrive environ une fois sur cinq. Et si l'effet réel n'était que **moitié moindre** que celui espéré ?

```python
f_moitie = f_plan / 2
print(f"effet moitié moindre : f = {f_moitie:.3f} -> puissance avec 12 jours par agencement = {puissance(12, f_moitie):.3f}")

def jours_pour_80(f):
    for n_g in range(3, 400):
        if puissance(n_g, f) >= 0.80:
            return n_g

for f, nom in [(f_plan, "effet prévu"), (f_moitie, "effet moitié moindre")]:
    n_req = jours_pour_80(f)
    print(f"{nom:22s} (f = {f:.3f}) : {n_req} jours par agencement pour 80 % de puissance, soit {4 * n_req} jours au total")
print("statsmodels (N total, avant arrondi à des groupes égaux) :",
      int(np.ceil(FTestAnovaPower().solve_power(effect_size=f_plan, power=0.8, alpha=0.05, k_groups=4))))
```
<!--sortie-->
```text
effet moitié moindre : f = 0.257 -> puissance avec 12 jours par agencement = 0.266
effet prévu            (f = 0.514) : 12 jours par agencement pour 80 % de puissance, soit 48 jours au total
effet moitié moindre   (f = 0.257) : 43 jours par agencement pour 80 % de puissance, soit 172 jours au total
statsmodels (N total, avant arrondi à des groupes égaux) : 46
```

Dessinons la puissance en fonction du nombre de jours, pour plusieurs tailles d'effet :

```python
ns = np.arange(4, 45)
fig, ax = plt.subplots(figsize=(6.5, 3.8))
for f, nom, couleur in [(0.10, "petit effet (f = 0,10)", "#898781"), (0.25, "effet moyen (f = 0,25)", VIOLET),
                        (f_plan, f"effet prévu (f = {f_plan:.2f})".replace(".", ","), ORANGE), (0.40, "grand effet (f = 0,40)", BLEU)]:
    ax.plot(ns, [puissance(n, f) for n in ns], color=couleur, lw=2, label=nom)
ax.axhline(0.8, color="#c3c2b7", ls="--", lw=1)
ax.axvline(12, color="#c3c2b7", ls=":", lw=1)
ax.set_xlabel("jours par agencement")
ax.set_ylabel("puissance du test F (4 groupes, α = 5 %)")
ax.set_ylim(0, 1.02)
ax.legend(loc="center right", bbox_to_anchor=(1.0, 0.38), fontsize=8)
ax.set_title("La puissance croît avec n, et décroît quand l'effet rétrécit")
plt.savefig("figures/ch08-puissance.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

Avec un effet moitié moindre, la puissance de la même expérience tombe à **27 %** : plus de deux fois sur trois, elle passerait à côté de l'effet. Pour retrouver 80 %, il faudrait **43 jours par agencement**, soit 172 jours (près de six mois d'ouverture) : diviser l'effet par deux multiplie par environ **quatre** le nombre d'essais nécessaires, car la taille d'échantillon varie comme $1/f^2$. C'est la raison pour laquelle on dimensionne l'expérience sur le **plus petit effet qui vaille la peine d'être détecté**.

![Courbes de puissance du test F à 4 groupes selon le nombre de jours par agencement, pour quatre tailles d'effet ; la ligne pointillée horizontale marque 80 %, la verticale 12 jours.](figures/ch08-puissance.png)

> 💡 **La leçon.** On calcule la puissance **avant** de lancer l'expérience, avec l'effet qu'on juge **utile** de détecter (pas celui qu'on espère). Une expérience sous-dimensionnée est pire qu'inutile : elle produit des résultats instables, et quand elle « réussit », elle tend à **surestimer** l'effet (l'effet significatif d'une expérience peu puissante est en moyenne exagéré).

### 8.2.11 La même chose en R

Les statisticiens utilisent souvent R pour l'ANOVA. Voici le même calcul, sur le même fichier, avec `aov` et `TukeyHSD`.

```r
d <- read.csv("donnees/ch08-vitrines.csv", fileEncoding = "UTF-8")
d$agencement <- factor(d$agencement)
fit <- aov(ventes ~ agencement, data = d)
print(summary(fit))
print(TukeyHSD(fit))
```
<!--sortie-->
```text
            Df Sum Sq Mean Sq F value Pr(>F)  
agencement   3  10595    3532   3.097 0.0363 *
Residuals   44  50168    1140                 
---
Signif. codes:  0 ‘***’ 0.001 ‘**’ 0.01 ‘*’ 0.05 ‘.’ 0.1 ‘ ’ 1
  Tukey multiple comparisons of means
    95% family-wise confidence level

Fit: aov(formula = ventes ~ agencement, data = d)

$agencement
                            diff        lwr      upr     p adj
Par couleur-Classique  28.358333  -8.448152 65.16482 0.1832471
Par thème-Classique    40.725000   3.918514 77.53149 0.0249275
Vedette-Classique      19.191667 -17.614819 55.99815 0.5108611
Par thème-Par couleur  12.366667 -24.439819 49.17315 0.8063634
Vedette-Par couleur    -9.166667 -45.973152 27.63982 0.9096634
Vedette-Par thème     -21.533333 -58.339819 15.27315 0.4103807
```

Même tableau d'analyse de variance, mêmes comparaisons de Tukey (au détail d'arrondi près). Changer d'outil ne change pas les mathématiques.

### 8.2.12 Ce que cachaient les données

Les données étant simulées, nous connaissons la vérité (script `build/donnees_ch08.py`). Pour la vitrine, les moyennes vraies étaient **200, 215, 240 et 205 €** pour Classique, Par couleur, Par thème et Vedette, avec un bruit de 30 €. Les écarts **observés** par rapport à « Classique » dans l'expérience à 48 jours (+28, +41 et +19 € pour Par couleur, Par thème et Vedette) en sont proches mais pas identiques à ceux qui étaient programmés (+15, +40 et +5) : l'erreur d'estimation d'un écart est ici d'environ 14 € (un écart-type), et le hasard a fait **sur-estimer** l'avantage de « Par couleur » et de « Vedette ». Avec 12 jours par groupe, on ne peut espérer que des ordres de grandeur. Dans l'expérience en blocs, les effets vrais étaient $0,\ 15,\ 40,\ 5$ € et les écarts estimés sont +17, +43 et +11 €, avec une erreur d'estimation d'environ 7 €, deux fois plus petite : c'est le gain de précision apporté par les blocs. Pour l'emballage, l'interaction était programmée : le coffret apporte $+10$ € au site mais $+22$ € sur Réseaux.

> ✅ **À retenir.**
> - L'ANOVA **décompose la variabilité** : $SS_T=SS_B+SS_W$, exactement ; le test $F=MS_B/MS_W\sim\mathcal F(k-1,N-k)$ sous $H_0$ compare variabilité entre et à l'intérieur des groupes.
> - Avec deux groupes, $F=t^2$ ; avec $k$ groupes, l'ANOVA est une **régression sur des indicatrices** ($R^2=\eta^2$).
> - On **vérifie les hypothèses** sur les résidus (normalité, variances égales) ; alternatives : Welch, transformation, Kruskal-Wallis.
> - Un $F$ significatif ne dit pas **quels** groupes diffèrent : utiliser **Tukey** (ou Bonferroni), ou un **contraste planifié** posé *avant* l'expérience.
> - **Taille d'effet** : $\eta^2$, $\omega^2$, $f$ ; une p-valeur n'est pas une mesure d'importance.
> - Les **blocs** retirent du bruit connu : à nombre d'essais égal, l'effet peut passer de « invisible » à « très net ».
> - À **deux facteurs**, regardez d'abord l'**interaction** ; si elle existe, étudiez les **effets simples**, pas les effets principaux.
> - **Calculez la puissance avant** l'expérience : une expérience sous-dimensionnée n'est pas fiable.
