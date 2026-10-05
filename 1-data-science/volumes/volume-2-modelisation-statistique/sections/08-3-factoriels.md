## 8.3 Les plans factoriels

> 💡 **Intuition.** En 8.1, nous avons vu que changer un facteur à la fois gaspille des essais et rate les interactions. Un plan **factoriel complet** à $k$ facteurs, chacun à **deux niveaux**, fait l'inverse : on teste **toutes** les $2^k$ combinaisons. Chaque essai sert ensuite à estimer **tous** les effets à la fois (les effets principaux comme les interactions), et chaque effet est mesuré sur **tous** les essais, en comparant « la moitié haute » à « la moitié basse ». C'est le plan le plus efficace que l'on puisse imaginer pour un nombre de facteurs modéré.

### 8.3.1 L'expérience de la gérante : trois facteurs, huit combinaisons

La gérante veut booster les commandes hebdomadaires de sa boutique en ligne. Trois leviers l'intéressent, chacun à deux niveaux :

| Facteur | Niveau « − » (−1) | Niveau « + » (+1) |
|---|---|---|
| **A** : emballage | standard | cadeau |
| **B** : prix | normal | promotion de 10 % |
| **C** : relance | e-mail | stories Réseaux |

Il y a $2^3=8$ combinaisons. Chaque combinaison est testée sur **deux semaines** (deux **répétitions**), tirées au hasard dans le calendrier : $16$ semaines au total. La réponse est le nombre de commandes de la semaine.

> 💡 **Le codage $-1/+1$.** On code les niveaux « bas » et « haut » par $-1$ et $+1$ (plutôt que 0 et 1). C'est plus qu'une convention : ce codage symétrique rend les colonnes du plan **orthogonales**, ce qui simplifie tous les calculs, comme nous allons le voir.

Voici le plan, avec le tableau des signes de tous les effets possibles. Les colonnes d'interaction sont les **produits** des colonnes des facteurs concernés : si A et B valent $-1$ et $+1$, l'interaction AB vaut $-1\times(+1)=-1$.

```python
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

def plan_2k(k):
    """Plan factoriel 2^k en ordre standard : A varie le plus vite, puis B, etc."""
    return np.array([[(1 if (i >> j) & 1 else -1) for j in range(k)] for i in range(2 ** k)])

X = plan_2k(3)
S = pd.DataFrame(X, columns=["A", "B", "C"])
S["AB"], S["AC"], S["BC"] = S.A * S.B, S.A * S.C, S.B * S.C
S["ABC"] = S.A * S.B * S.C
S.insert(0, "I", 1)
S.index = ["(1)", "a", "b", "ab", "c", "ac", "bc", "abc"]      # notation classique : on nomme les lettres « hautes »
print(S.to_string())
print("\nS' S (produit scalaire de chaque paire de colonnes) :")
print((S.T @ S).to_string())
```
<!--sortie-->
```text
     I  A  B  C  AB  AC  BC  ABC
(1)  1 -1 -1 -1   1   1   1   -1
a    1  1 -1 -1  -1  -1   1    1
b    1 -1  1 -1  -1   1  -1    1
ab   1  1  1 -1   1  -1  -1   -1
c    1 -1 -1  1   1  -1  -1    1
ac   1  1 -1  1  -1   1  -1   -1
bc   1 -1  1  1  -1  -1   1   -1
abc  1  1  1  1   1   1   1    1

S' S (produit scalaire de chaque paire de colonnes) :
     I  A  B  C  AB  AC  BC  ABC
I    8  0  0  0   0   0   0    0
A    0  8  0  0   0   0   0    0
B    0  0  8  0   0   0   0    0
C    0  0  0  8   0   0   0    0
AB   0  0  0  0   8   0   0    0
AC   0  0  0  0   0   8   0    0
BC   0  0  0  0   0   0   8    0
ABC  0  0  0  0   0   0   0    8
```

Les huit lignes sont les huit combinaisons (« a » signifie A haut, B et C bas ; « abc », tout haut ; « (1) », tout bas). Le produit $S^\top S$ vaut $8\times$ la matrice identité : **les huit colonnes sont orthogonales** (le produit scalaire de deux colonnes distinctes est nul) et chacune a une norme de $\sqrt8$. Tout ce chapitre repose sur cette propriété.

### 8.3.2 Les effets, à la main

Les données de l'expérience (ordre des essais tiré au hasard, puis rangées en ordre standard) :

```python
f3 = pd.read_csv("donnees/ch08-factoriel-2p3.csv")
print("Les 5 premières semaines dans l'ordre d'exécution (tiré au hasard) :")
print(f3.head(5)[["ordre", "A", "B", "C", "commandes"]].to_string(index=False))

cel = f3.pivot_table(index=["C", "B", "A"], columns="replicat", values="commandes")
cel["moyenne"] = cel.mean(axis=1)
cel.index = S.index                                          # même ordre standard que le tableau des signes
print("\nRésultats par combinaison :")
print(cel.round(2).to_string())
```
<!--sortie-->
```text
Les 5 premières semaines dans l'ordre d'exécution (tiré au hasard) :
 ordre  A  B  C  commandes
     1  1 -1 -1       57.1
     2  1  1 -1       56.9
     3  1  1  1       78.1
     4 -1 -1  1       45.8
     5  1  1 -1       68.4

Résultats par combinaison :
replicat     1     2  moyenne
(1)       49.9  45.9    47.90
a         57.1  65.3    61.20
b         69.4  64.6    67.00
ab        68.4  56.9    62.65
c         45.8  51.5    48.65
ac        62.1  59.8    60.95
bc        70.1  64.4    67.25
abc       73.2  78.1    75.65
```

On définit l'**effet principal** d'un facteur comme la **différence moyenne de réponse** quand ce facteur passe de son niveau bas à son niveau haut, **en moyennant sur les niveaux des autres facteurs**. Par exemple, l'effet de A est la moyenne des quatre combinaisons où A est haut, moins la moyenne des quatre où A est bas :

$$\text{effet}(A)=\bar y_{A+}-\bar y_{A-}.$$

L'**interaction** AB est la demi-différence entre l'effet de A quand B est haut et l'effet de A quand B est bas ; de façon équivalente, c'est la différence entre la moyenne des cellules où AB $=+1$ et celle où AB $=-1$. **La même règle s'applique à toutes les colonnes du tableau des signes** : l'effet d'une colonne est la moyenne des réponses là où elle vaut $+1$ moins la moyenne là où elle vaut $-1$. Avec $\bar y_i$ les huit moyennes de cellules et $s_i$ le signe de la colonne :

$$\text{effet}=\frac{1}{4}\sum_{i=1}^{8}s_i\,\bar y_i\qquad\left(\text{plus généralement }\frac{1}{2^{k-1}}\sum_i s_i\bar y_i\right).$$

```python
ybar = cel["moyenne"].to_numpy()
effets = {c: (S[c].to_numpy() * ybar).sum() / 4 for c in ["A", "B", "C", "AB", "AC", "BC", "ABC"]}
print("Détail pour A : moyenne des cellules A haut =", round(ybar[S.A.to_numpy() == 1].mean(), 2),
      "; A bas =", round(ybar[S.A.to_numpy() == -1].mean(), 2))
print(pd.Series(effets).round(2).to_string())
print("\nmoyenne générale :", round(ybar.mean(), 2))
```
<!--sortie-->
```text
Détail pour A : moyenne des cellules A haut = 65.11 ; A bas = 57.7
A       7.41
B      13.46
C       3.44
AB     -5.39
AC      2.94
BC      3.19
ABC     3.44

moyenne générale : 61.41
```

Lisez le résultat comme une phrase : « passer de l'emballage standard à l'emballage cadeau fait varier les commandes de $\ldots$ en moyenne », etc. L'effet du **prix** (B) est le plus grand ; l'interaction AB est négative : l'effet du cadeau est plus faible en promotion, ce qui rappelle exactement l'exemple de 8.1.5.

> 📐 **L'algorithme de Yates.** Avant les ordinateurs, on calculait tous les effets avec une procédure d'additions et de soustractions, qui reste élégante. On écrit les moyennes en ordre standard $(1),a,b,ab,c,ac,bc,abc$. À chaque étape, la nouvelle colonne contient d'abord les **sommes** de paires voisines, puis leurs **différences** (second moins premier). Après $k$ étapes, on obtient les « contrastes » dans l'ordre $I,A,B,AB,C,AC,BC,ABC$ ; il suffit de diviser par $2^{k-1}$ pour obtenir les effets (et par $2^k$ pour la moyenne).

```python
def yates(y):
    cols, col = [np.array(y, float)], np.array(y, float)
    for _ in range(int(np.log2(len(y)))):
        col = np.concatenate([col[0::2] + col[1::2], col[1::2] - col[0::2]])
        cols.append(col)
    return np.array(cols).T

Y = yates(ybar)
noms = ["I", "A", "B", "AB", "C", "AC", "BC", "ABC"]
tab = pd.DataFrame(Y, index=noms, columns=["moyennes", "étape 1", "étape 2", "contraste (étape 3)"])
tab["effet = contraste / 4"] = tab["contraste (étape 3)"] / 4
tab.loc["I", "effet = contraste / 4"] = tab.loc["I", "contraste (étape 3)"] / 8       # la moyenne se divise par 8
print(tab.round(2).to_string())
print("\nIdentique aux effets calculés plus haut :", all(np.isclose(tab.loc[c, "effet = contraste / 4"], effets[c]) for c in effets))
```
<!--sortie-->
```text
     moyennes  étape 1  étape 2  contraste (étape 3)  effet = contraste / 4
I       47.90   109.10   238.75               491.25                  61.41
A       61.20   129.65   252.50                29.65                   7.41
B       67.00   109.60     8.95                53.85                  13.46
AB      62.65   142.90    20.70               -21.55                  -5.39
C       48.65    13.30    20.55                13.75                   3.44
AC      60.95    -4.35    33.30                11.75                   2.94
BC      67.25    12.30   -17.65                12.75                   3.19
ABC     75.65     8.40    -3.90                13.75                   3.44

Identique aux effets calculés plus haut : True
```

### 8.3.3 Le lien avec la régression, et la précision des effets

Ces effets sont, à un facteur 2 près, les **coefficients de la régression** de la réponse sur les colonnes du tableau des signes (chapitre 1). C'est la clé pour **tester** et **mesurer l'incertitude**. Écrivons le modèle complet :

$$y=\beta_0+\beta_A x_A+\beta_B x_B+\beta_C x_C+\beta_{AB}x_Ax_B+\dots+\beta_{ABC}x_Ax_Bx_C+\varepsilon,\qquad x\in\{-1,+1\}.$$

> 📐 **Théorème (effets et coefficients).** Dans un plan factoriel complet $2^k$ avec $N$ essais au total, (i) $\widehat\beta_j=\dfrac1N\sum_i s_{ij}\,y_i$ ; (ii) l'effet estimé est $\widehat{\text{effet}}_j=2\widehat\beta_j$ ; (iii) les estimateurs sont **non corrélés** et $\operatorname{Var}(\widehat\beta_j)=\sigma^2/N$, donc
> $$\operatorname{Var}(\widehat{\text{effet}}_j)=\frac{4\sigma^2}{N},\qquad \text{écart-type d'un effet}=\frac{2\sigma}{\sqrt N}.$$
> *Démonstration.* Notons $X$ la matrice $N\times 2^k$ des colonnes du tableau des signes (répétées si l'on a plusieurs répétitions). Ses colonnes sont orthogonales et chacune a une norme au carré égale à $N$ : $X^\top X=N\,I$. Les moindres carrés (chapitre 1, section 1.1) donnent $\widehat\beta=(X^\top X)^{-1}X^\top y=\frac1N X^\top y$, d'où (i). Pour (ii) : quand $x_j$ passe de $-1$ à $+1$, la réponse prédite varie de $2\beta_j$ (les autres termes se compensent en moyenne grâce à l'orthogonalité). Enfin $\operatorname{Var}(\widehat\beta)=\sigma^2(X^\top X)^{-1}=\frac{\sigma^2}{N}I$ : variances égales, covariances nulles ; et $\operatorname{Var}(2\widehat\beta_j)=4\sigma^2/N$. $\square$

Deux conséquences remarquables. **La précision est la même pour tous les effets** et ne dépend que du nombre total d'essais $N$ : tous les essais servent à chaque effet. Et comme les estimateurs sont **non corrélés**, le fait de retirer un effet du modèle ne change pas les estimations des autres. Il reste à estimer $\sigma^2$ : avec des **répétitions**, on dispose de l'**erreur pure**, la variabilité entre les répétitions d'une même combinaison.

```python
mod = smf.ols("commandes ~ A * B * C", data=f3).fit()          # A*B*C = tous les effets principaux et interactions
N = len(f3)
res = pd.DataFrame({"effet": 2 * mod.params, "ET": 2 * mod.bse, "t": mod.tvalues, "p": mod.pvalues}).drop("Intercept")
print(res.round(3).to_string())

# erreur pure « à la main » : écarts des deux répétitions à la moyenne de leur combinaison
moy_cel = f3.groupby(["A", "B", "C"])["commandes"].transform("mean")
s2 = ((f3["commandes"] - moy_cel) ** 2).sum() / (N - 8)
print(f"\nerreur pure : s² = {s2:.2f} (ddl = {N - 8}) ; statsmodels : {mod.mse_resid:.2f}")
print(f"écart-type d'un effet = 2 s / sqrt(N) = 2 x {np.sqrt(s2):.2f} / {np.sqrt(N):.0f} = {2 * np.sqrt(s2 / N):.3f}")
```
<!--sortie-->
```text
        effet    ET      t      p
A       7.413  2.28  3.251  0.012
B      13.463  2.28  5.904  0.000
A:B    -5.388  2.28 -2.363  0.046
C       3.437  2.28  1.507  0.170
A:C     2.937  2.28  1.288  0.234
B:C     3.188  2.28  1.398  0.200
A:B:C   3.438  2.28  1.507  0.170

erreur pure : s² = 20.80 (ddl = 8) ; statsmodels : 20.80
écart-type d'un effet = 2 s / sqrt(N) = 2 x 4.56 / 4 = 2.280
```

La colonne « effet » redonne les effets du calcul à la main (au facteur de moyenne près pour $I$). Les écarts-types des effets sont **tous identiques**, comme le prédit le théorème, et valent environ 2,3 commandes. Chaque effet a **1 degré de liberté** et la même statistique $t=\text{effet}/\text{ET}$, à $N-8=8$ degrés de liberté (erreur pure). Dans un plan factoriel, la décomposition de la variance de 8.2 devient limpide : la somme de carrés de l'effet $j$ vaut $N\widehat\beta_j^{\,2}=N\cdot(\text{effet}_j/2)^2$.

```python
aov = anova_lm(mod)
ss = (N * (res["effet"] / 2) ** 2).round(1)
verif = pd.DataFrame({"SS (tableau d'ANOVA)": aov["sum_sq"].drop("Residual").round(1).to_numpy(),
                      "SS = N x (effet/2)²": ss.to_numpy()}, index=res.index)
print(verif.to_string())
print(f"SS erreur pure = {aov.loc['Residual', 'sum_sq']:.1f} ; SS total = {((f3['commandes'] - f3['commandes'].mean()) ** 2).sum():.1f} ; "
      f"somme des SS des effets + erreur = {aov['sum_sq'].sum():.1f}")
```
<!--sortie-->
```text
       SS (tableau d'ANOVA)  SS = N x (effet/2)²
A                     219.8                219.8
B                     725.0                725.0
A:B                   116.1                116.1
C                      47.3                 47.3
A:C                    34.5                 34.5
B:C                    40.6                 40.6
A:B:C                  47.3                 47.3
SS erreur pure = 166.4 ; SS total = 1396.9 ; somme des SS des effets + erreur = 1396.9
```

### 8.3.4 Lire l'expérience : quels effets comptent ?

Au seuil de 5 %, trois effets ressortent : le **prix** (B), l'**emballage** (A) et leur **interaction** (AB). Les effets de la relance (C) et des autres interactions sont plus petits que le bruit ne permet de le distinguer ($p>0{,}15$ pour chacun). Représentons les résultats : le **cube des moyennes** (le code de ce dessin est dans `build/fig_ch08.py`) puis le graphique d'interaction AB.

![Les huit moyennes de cellules sur un cube dont les arêtes sont les trois facteurs : les valeurs les plus élevées se trouvent du côté « promotion » (haut du cube), et la plus élevée est « tout haut ».](figures/ch08-cube-2p3.png)

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, VIOLET = "#2a78d6", "#eb6834", "#4a3aa7"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "figure.facecolor": "#fcfcfb",
                     "axes.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb", "legend.frameon": False})

fig, ax = plt.subplots(figsize=(5.6, 3.8))
for b, nom, coul in [(-1, "prix normal", BLEU), (1, "promotion", ORANGE)]:
    m = f3[f3["B"] == b].groupby("A")["commandes"].mean()
    ax.plot([-1, 1], m.values, "o-", color=coul, lw=2)
    ax.text(1.06, m.values[1], nom, color=coul, va="center")
ax.set_xticks([-1, 1])
ax.set_xticklabels(["emballage standard", "emballage cadeau"])
ax.set_xlim(-1.2, 1.9)
ax.set_ylabel("commandes par semaine (moyenne)")
ax.set_title("Interaction emballage × prix (moyennes sur les deux relances)")
plt.savefig("figures/ch08-interaction-AB.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Graphique d'interaction emballage × prix : les deux courbes ne sont pas parallèles ; le cadeau fait nettement monter les commandes au prix normal, beaucoup moins en promotion.](figures/ch08-interaction-AB.png)

On retrouve la même histoire qu'en 8.1.5 : l'emballage cadeau aide **surtout quand le prix est normal** (il remplace en quelque sorte la promotion) ; en promotion, son apport est bien plus faible. Les deux leviers sont **partiellement substituables**. Un décideur qui n'aurait regardé que les effets principaux aurait conclu « faites les deux » sans voir qu'ils se gênent un peu.

**Modèle réduit et prédiction.** Puisque les effets non significatifs ne se distinguent pas du bruit, on peut les retirer du modèle. Comme les estimateurs sont non corrélés, les effets restants **ne changent pas**, mais l'erreur est estimée avec plus de degrés de liberté. On peut alors prédire la réponse aux huit réglages et choisir le meilleur.

```python
red = smf.ols("commandes ~ A + B + A:B", data=f3).fit()
print(red.params.round(3).to_string())
print(f"\nR² complet = {mod.rsquared:.3f} ; R² réduit = {red.rsquared:.3f} ; s (erreur) = {np.sqrt(red.mse_resid):.2f} (ddl {int(red.df_resid)})\n")

grille = pd.DataFrame([(a, b) for b in (-1, 1) for a in (-1, 1)], columns=["A", "B"])
pred = red.get_prediction(grille).summary_frame(alpha=0.05)
grille["prédiction"] = pred["mean"].round(1)
grille["IC95 de la moyenne"] = [f"[{lo:.1f} ; {hi:.1f}]" for lo, hi in zip(pred["mean_ci_lower"], pred["mean_ci_upper"])]
print(grille.to_string(index=False))
```
<!--sortie-->
```text
Intercept    61.406
A             3.706
B             6.731
A:B          -2.694

R² complet = 0.881 ; R² réduit = 0.759 ; s (erreur) = 5.29 (ddl 12)

 A  B  prédiction IC95 de la moyenne
-1 -1        48.3      [42.5 ; 54.0]
 1 -1        61.1      [55.3 ; 66.8]
-1  1        67.1      [61.4 ; 72.9]
 1  1        69.2      [63.4 ; 74.9]
```

Le meilleur réglage prédit est « emballage cadeau **et** promotion » (69,2 commandes), mais son gain sur « promotion seule » (67,1) n'est que de 2 commandes et les deux intervalles de confiance se chevauchent largement : compte tenu du coût d'un emballage cadeau, la décision n'est pas évidente. C'est précisément le genre de conclusion nuancée que seule la prise en compte de l'interaction permet. (Un détail instructif : l'écart-type résiduel passe de 4,56 dans le modèle complet à 5,29 dans le modèle réduit, parce que les effets retirés, C et BC, sont **réels** même s'ils sont non significatifs : ils rejoignent alors l'erreur. Simplifier un modèle n'est pas gratuit.)

### 8.3.5 Ce que l'expérience ne détecte pas : la leçon de la puissance

Le modèle programmé pour simuler ces données (que nous dévoilons maintenant) contenait aussi un effet de la relance C (+4 commandes en effet) et une interaction BC (+3). Le tableau ne les a **pas détectés** : $p=0{,}17$ et $p=0{,}20$. Absence de preuve n'est pas preuve d'absence. Calculons la puissance de ce plan pour un effet de 4 commandes, avec le vrai bruit $\sigma=3{,}5$ : l'écart-type d'un effet vaut $2\sigma/\sqrt N$ ; la statistique $t$ suit, sous l'alternative, une loi de Student **non centrale** de paramètre $\delta=\Delta/(2\sigma/\sqrt N)$.

```python
sigma, delta_effet = 3.5, 4.0
lignes = []
for r in (1, 2, 3, 4, 6):
    N_r = 8 * r
    ddl = N_r - 8 if r > 1 else None
    if ddl is None:                                    # pas de répétition : pas d'erreur pure ; voir 8.3.6
        lignes.append((r, N_r, None, 2 * sigma / np.sqrt(N_r), None))
        continue
    se = 2 * sigma / np.sqrt(N_r)
    seuil = stats.t.ppf(0.975, ddl)
    puissance = stats.nct.sf(seuil, ddl, delta_effet / se) + stats.nct.cdf(-seuil, ddl, delta_effet / se)
    lignes.append((r, N_r, ddl, se, puissance))
tab = pd.DataFrame(lignes, columns=["répétitions r", "essais N = 8 r", "ddl erreur pure", "ET d'un effet", "puissance (effet = 4)"])
print(tab.round(3).to_string(index=False))
```
<!--sortie-->
```text
 répétitions r  essais N = 8 r  ddl erreur pure  ET d'un effet  puissance (effet = 4)
             1               8              NaN          2.475                    NaN
             2              16              8.0          1.750                  0.520
             3              24             16.0          1.429                  0.748
             4              32             24.0          1.237                  0.873
             6              48             40.0          1.010                  0.971
```

Sans répétition ($r=1$), il n'y a pas d'erreur pure, donc pas de test du tout (la case reste vide). Avec deux répétitions, la puissance pour détecter un effet de 4 commandes n'est que de **52 %**, un peu plus de la moitié : l'expérience avait donc à peu près une chance sur deux de rater un effet pourtant réel et non négligeable. Il aurait fallu **quatre répétitions** (32 semaines) pour dépasser 80 % (87 %), trois ne donnant que 75 %. C'est l'arbitrage permanent de l'expérimentateur : *plus de facteurs et peu de répétitions* (on repère les gros effets) ou *moins de facteurs et plus de répétitions* (on repère les petits). La section suivante montre comment obtenir davantage avec moins d'essais.

### 8.3.6 Sans répétition : le plan $2^4$ et le diagramme demi-normal

Les répétitions coûtent cher. Quand on teste plus de facteurs (disons quatre : on ajoute **D**, un message personnalisé), le plan $2^4$ n'a que $16$ essais, **sans répétition**. Il estime $15$ effets (4 principaux, 6 interactions d'ordre 2, 4 d'ordre 3 et 1 d'ordre 4) avec $16$ essais : plus aucun degré de liberté pour l'erreur pure. Comment tester ? On s'appuie sur un principe d'expérience, observé dans une immense majorité d'études :

> 💡 **Le principe de parcimonie des effets.** Parmi de nombreux effets possibles, **peu sont réellement actifs**, et les interactions d'ordre élevé (trois facteurs ou plus) sont presque toujours négligeables. Les effets *inactifs* sont donc des **estimations du pur bruit** : ils se répartissent autour de 0 selon une loi normale de même écart-type. Il suffit de repérer ceux qui s'en écartent.

La première idée est le **diagramme demi-normal** (*half-normal plot*). On range les valeurs absolues des $m$ effets par ordre croissant $|c|_{(1)}\le\dots\le|c|_{(m)}$ et on les compare aux quantiles attendus pour la valeur absolue d'une loi normale : $z_i=\Phi^{-1}\left(0{,}5+0{,}5\,\dfrac{i-0{,}5}{m}\right)$. Si **tous** les effets étaient du bruit, les points s'aligneraient sur une droite passant par l'origine, de pente $\sigma_c$ (l'écart-type d'un effet). Les effets **actifs** sortent de la droite, vers le haut.

La seconde idée, **la méthode de Lenth**, chiffre cette intuition sans modèle d'erreur. Notons $c_j$ les $m$ effets estimés :

- $s_0=1{,}5\times\operatorname{médiane}|c_j|$, une première estimation de l'écart-type du bruit (robuste : la médiane ignore les quelques effets actifs) ;
- $\text{PSE}=1{,}5\times\operatorname{médiane}\{|c_j|:\ |c_j|<2{,}5\,s_0\}$, l'estimation « **pseudo-erreur standard** » obtenue après avoir écarté les effets manifestement actifs ;
- la **marge d'erreur** $\text{ME}=t_{0{,}975;\,d}\times\text{PSE}$ avec $d=m/3$, et la marge **simultanée** $\text{SME}=t_{\gamma;\,d}\times\text{PSE}$ avec $\gamma=\dfrac{1+0{,}95^{1/m}}{2}$, qui tient compte du fait qu'on teste $m$ effets à la fois.

Un effet dont la valeur absolue dépasse la SME est déclaré actif (la ME est plus permissive).

```python
g = pd.read_csv("donnees/ch08-factoriel-2p4.csv")
mod4 = smf.ols("commandes ~ A * B * C * D", data=g).fit()
eff = (2 * mod4.params).drop("Intercept")
eff.index = [c.replace(":", "") for c in eff.index]
print("Nombre d'effets estimés :", len(eff), "; ddl de l'erreur :", int(mod4.df_resid), "(aucun : modèle saturé)\n")

absolu = eff.abs().sort_values()
m = len(absolu)
s0 = 1.5 * np.median(absolu)
pse = 1.5 * np.median(absolu[absolu < 2.5 * s0])
d = m / 3
ME = stats.t.ppf(0.975, d) * pse
SME = stats.t.ppf((1 + 0.95 ** (1 / m)) / 2, d) * pse
print(f"s0 = {s0:.3f}   PSE = {pse:.3f}   ME = {ME:.2f}   SME = {SME:.2f}\n")
tab = pd.DataFrame({"effet": eff[absolu.index].round(2), "|effet|": absolu.round(2), "actif (|effet| > SME)": absolu > SME})
print(tab.iloc[::-1].head(8).to_string())
```
<!--sortie-->
```text
Nombre d'effets estimés : 15 ; ddl de l'erreur : 0 (aucun : modèle saturé)

s0 = 1.012   PSE = 0.900   ME = 2.31   SME = 4.70

     effet  |effet|  actif (|effet| > SME)
B    12.20    12.20                   True
A     9.53     9.53                   True
AB   -5.68     5.68                   True
D     5.20     5.20                   True
ABC   1.30     1.30                  False
ACD  -1.10     1.10                  False
ABD  -0.92     0.92                  False
CD   -0.67     0.67                  False
```

```python
z = stats.norm.ppf(0.5 + 0.5 * (np.arange(1, m + 1) - 0.5) / m)
fig, ax = plt.subplots(figsize=(6.4, 4.4))
actifs = absolu > SME
ax.scatter(z[~actifs], absolu[~actifs], color=BLEU, s=34, zorder=3, label="effets compatibles avec le bruit")
ax.scatter(z[actifs], absolu[actifs], color=ORANGE, s=44, zorder=4, label="effets actifs (> SME)")
ax.plot([0, z.max()], [0, pse * z.max()], color="#898781", lw=1.2, label="droite du bruit (pente = PSE)")
ax.axhline(SME, color=VIOLET, ls="--", lw=1)
ax.text(0.05, SME + 0.25, f"SME = {SME:.1f}", color=VIOLET, fontsize=8)
for zi, a, nom in zip(z[actifs], absolu[actifs], absolu.index[actifs]):
    ax.annotate(nom, (zi, a), xytext=(6, -2), textcoords="offset points", fontsize=9, color="#0b0b0b")
ax.set_xlabel("quantile demi-normal théorique")
ax.set_ylabel("|effet| estimé (commandes)")
ax.set_title("Diagramme demi-normal des 15 effets du plan 2⁴")
ax.legend(loc="upper left", fontsize=8)
plt.savefig("figures/ch08-demi-normal.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Diagramme demi-normal des 15 effets d'un plan 2⁴ non répliqué : onze points suivent la droite du bruit près de l'origine, quatre points actifs (B, A, AB et D) s'en détachent nettement et dépassent le seuil SME.](figures/ch08-demi-normal.png)

Onze points alignés sur la droite du bruit, quatre points qui s'en détachent : **B, A, AB et D** (effets de 12,2, 9,5, −5,7 et 5,2 contre une SME de 4,7). Remarquez que D, avec 5,2, ne dépasse la SME que de peu : avec un bruit un peu plus fort, il aurait pu passer inaperçu. Les onze autres, dont toutes les interactions d'ordre 3 et 4, sont indiscernables du bruit. Ce résultat se confirme par une régression sur les seuls effets actifs, en reversant les degrés de liberté « libérés » (les 11 effets retirés) à l'**erreur** :

```python
red4 = smf.ols("commandes ~ A + B + A:B + D", data=g).fit()
t4 = pd.DataFrame({"effet": 2 * red4.params, "ET": 2 * red4.bse, "p": red4.pvalues}).drop("Intercept")
print(t4.round(3).to_string())
print(f"s = {np.sqrt(red4.mse_resid):.2f} avec {int(red4.df_resid)} ddl ; R² = {red4.rsquared:.3f}")
```
<!--sortie-->
```text
      effet     ET    p
A     9.525  0.727  0.0
B    12.200  0.727  0.0
A:B  -5.675  0.727  0.0
D     5.200  0.727  0.0
s = 1.45 avec 11 ddl ; R² = 0.981
```

> ⚠️ **Prudence.** Cette démarche **cherche** les effets actifs dans les données : les tests qui suivent sont donc un peu optimistes (on a choisi les effets *parce qu'ils étaient grands*). La méthode de Lenth contrôle ce biais avec la SME, la régression finale non. Un plan non répliqué doit être **confirmé** par quelques essais supplémentaires au réglage retenu.

### 8.3.7 Ce que cachaient les données

Révélons la vérité (`build/donnees_ch08.py`).

- **Plan $2^3$** : en unités codées, $y=60+4A+6B+2C-2{,}5AB+1{,}5BC$, donc des **effets** de $8$ (A), $12$ (B), $4$ (C), $-5$ (AB), $3$ (BC) et $0$ pour AC et ABC, avec un écart-type du bruit $\sigma=3{,}5$. L'expérience a bien trouvé les trois effets les plus grands (A, B, AB), avec des estimations proches des vraies valeurs ($7{,}4$ pour 8, $13{,}5$ pour 12, $-5{,}4$ pour $-5$), et **manqué** C et BC, qui sont plus petits que le bruit ne permet de voir avec 16 essais. Elle a aussi produit deux « effets » (AC et ABC, à environ 3) qui n'existent pas : à environ 1,3 à 1,5 écart-type de zéro (l'écart-type d'un effet est de 2,3), ce sont des fluctuations d'échantillonnage ordinaires, qui n'ont d'ailleurs pas dépassé le seuil de significativité.
- **Plan $2^4$** : $y=60+4A+6B-3AB+2{,}5D$, soit des effets de $8$, $12$, $-6$ et $5$ ; les 11 autres effets valent 0. La méthode de Lenth a retrouvé **exactement** les quatre effets actifs, sans en inventer un seul, avec des estimations proches de la vérité ($9{,}5$, $12{,}2$, $-5{,}7$, $5{,}2$) et un bruit de $\sigma=1{,}5$ cette fois plus faible.

> ✅ **À retenir.**
> - Un plan factoriel complet $2^k$ teste toutes les combinaisons et estime **tous** les effets (principaux et interactions) avec **tous** les essais.
> - Codé en $\pm1$, le plan est **orthogonal** : $X^\top X=N\,I$ ; effet $=2\times$ coefficient de régression, **tous les effets ont le même écart-type** $2\sigma/\sqrt N$ et sont non corrélés.
> - Les effets se calculent à la main (**contrastes**, algorithme de **Yates**) et se testent par régression avec l'**erreur pure** des répétitions.
> - Les **interactions** sont lues sur le **graphique d'interaction** et le **cube** ; ne parlez pas d'un effet principal quand l'interaction domine.
> - Sans répétition, le **diagramme demi-normal** et la **méthode de Lenth** repèrent les effets actifs en s'appuyant sur la **parcimonie des effets**.
> - Un test non significatif ne prouve pas l'absence d'effet : calculez la **puissance** du plan pour l'effet qui compte.
