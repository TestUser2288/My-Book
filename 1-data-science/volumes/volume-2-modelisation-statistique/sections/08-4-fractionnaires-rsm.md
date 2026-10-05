## 8.4 Plans fractionnaires et surfaces de réponse

> 💡 **Intuition.** Le plan factoriel complet est généreux : $2^k$ essais pour $k$ facteurs. Mais le nombre d'essais double à chaque facteur ajouté, alors que la plupart des interactions d'ordre élevé sont négligeables. Un **plan fractionnaire** n'exécute qu'une **fraction** ($\tfrac12$, $\tfrac14$…) des combinaisons, bien choisie, en **acceptant de confondre** certains effets entre eux : on économise des essais en renonçant à distinguer des effets que l'on juge de toute façon petits. La seconde moitié de la section est consacrée à un autre but : non plus *repérer les facteurs qui comptent*, mais **trouver le meilleur réglage** de deux facteurs continus, avec les **surfaces de réponse**.

### 8.4.1 Le problème : $2^k$ explose

Combien d'effets contient un plan complet, et de quel ordre ?

```python
import numpy as np
import pandas as pd
from math import comb
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

lignes = []
for k in (3, 4, 5, 7):
    ordres = [comb(k, j) for j in range(1, k + 1)]
    lignes.append({"facteurs k": k, "essais 2^k": 2 ** k, "principaux": ordres[0], "interactions d'ordre 2": ordres[1],
                   "d'ordre 3": ordres[2], "d'ordre 4 et plus": sum(ordres[3:]), "total d'effets": sum(ordres)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 facteurs k  essais 2^k  principaux  interactions d'ordre 2  d'ordre 3  d'ordre 4 et plus  total d'effets
          3           8           3                       3          1                  0               7
          4          16           4                       6          4                  1              15
          5          32           5                      10         10                  6              31
          7         128           7                      21         35                 64             127
```

Avec 7 facteurs, un plan complet demande **128 essais** pour estimer 127 effets, dont **7 seulement** sont des effets principaux et **21** des interactions d'ordre 2 : les $99$ autres sont des interactions d'ordre 3 ou plus, presque toujours négligeables en pratique. C'est un énorme gaspillage. Le **principe de hiérarchie** dit que les effets principaux sont plus importants que les interactions d'ordre 2, elles-mêmes plus importantes que celles d'ordre 3, etc. Joint au principe de parcimonie (8.3.6), il justifie de **sacrifier les interactions d'ordre élevé**.

### 8.4.2 Une demi-fraction : le plan $2^{4-1}$

Reprenons les quatre facteurs de l'expérience $2^4$ de 8.3.6 (A emballage, B prix, C relance, D message personnalisé), mais supposons que la gérante n'ait pu faire que **8 essais** au lieu de 16. Comment choisir 8 combinaisons parmi 16 ?

Construisons un plan complet $2^3$ sur A, B, C, et **définissons D comme le produit** $D=ABC$ : la colonne de D n'est plus libre, elle est **imposée** par les trois autres. C'est le **générateur** de la fraction. Multiplier les deux membres par $D$ donne la **relation de définition** :
$$D=ABC\ \Longrightarrow\ D\cdot D=ABC\cdot D\ \Longrightarrow\ I=ABCD,$$
puisque $D\cdot D=I$ (le produit d'une colonne $\pm1$ par elle-même vaut $+1$). Toute la structure de confusion découle de cette seule relation.

> 📐 **Confusion (alias).** Si $I=ABCD$, alors multiplier un effet par $ABCD$ donne l'effet confondu avec lui : $A=A\cdot ABCD=BCD$, $B=ACD$, $C=ABD$, $D=ABC$, et pour les interactions d'ordre 2, $AB=CD$, $AC=BD$, $AD=BC$. Les colonnes du tableau des signes de ces effets sont **identiques** dans les 8 essais : il est mathématiquement impossible de les distinguer. Le contraste calculé sur la colonne de A estime donc **la somme** $A+BCD$ ; si l'interaction d'ordre 3 $BCD$ est négligeable (c'est l'hypothèse de hiérarchie), c'est bien l'effet de A.

Vérifions-le numériquement, puis utilisons la **vraie** expérience : parmi les 16 essais de 8.3.6, ne gardons que les 8 pour lesquels $ABCD=+1$ (c'est exactement la fraction définie par $I=ABCD$) et comparons les effets estimés avec ceux du plan complet.

```python
def plan_2k(k):
    return np.array([[(1 if (i >> j) & 1 else -1) for j in range(k)] for i in range(2 ** k)])

X = plan_2k(3)
A, B, C = X.T
D = A * B * C
print("colonne A = colonne BCD :", np.array_equal(A, B * C * D), "| AB = CD :", np.array_equal(A * B, C * D),
      "| AC = BD :", np.array_equal(A * C, B * D), "| AD = BC :", np.array_equal(A * D, B * C))

g = pd.read_csv("donnees/ch08-factoriel-2p4.csv")
complet = (2 * smf.ols("commandes ~ A * B * C * D", data=g).fit().params).drop("Intercept")
demi = g[g.A * g.B * g.C * g.D == 1]                       # la demi-fraction I = ABCD : 8 essais sur 16
mod_demi = smf.ols("commandes ~ A * B * C", data=demi).fit()        # 8 essais, 8 paramètres : modèle saturé
eff_demi = (2 * mod_demi.params).drop("Intercept")
somme_alias = {"A": ["A", "B:C:D"], "B": ["B", "A:C:D"], "C": ["C", "A:B:D"], "A:B": ["A:B", "C:D"],
               "A:C": ["A:C", "B:D"], "B:C": ["B:C", "A:D"], "A:B:C": ["A:B:C", "D"]}
noms_alias = {"A": "A + BCD", "B": "B + ACD", "C": "C + ABD", "A:B": "AB + CD", "A:C": "AC + BD", "B:C": "BC + AD", "A:B:C": "ABC + D"}
tab = pd.DataFrame({"contraste estime": [noms_alias[i] for i in eff_demi.index],
                    "demi-fraction (8 essais)": eff_demi.round(2).to_numpy(),
                    "somme des 2 effets du plan complet": [round(sum(complet[e] for e in somme_alias[i]), 2) for i in eff_demi.index]},
                   index=eff_demi.index)
print()
print(len(demi), "essais retenus sur", len(g))
print(tab.to_string())
print("\nEffets du plan complet (16 essais) pour mémoire :", complet[["A", "B", "A:B", "D"]].round(2).to_dict())
```
<!--sortie-->
```text
colonne A = colonne BCD : True | AB = CD : True | AC = BD : True | AD = BC : True

8 essais retenus sur 16
      contraste estime  demi-fraction (8 essais)  somme des 2 effets du plan complet
A              A + BCD                      9.00                                9.00
B              B + ACD                     11.10                               11.10
A:B            AB + CD                     -6.35                               -6.35
C              C + ABD                     -1.20                               -1.20
A:C            AC + BD                     -0.45                               -0.45
B:C            BC + AD                      0.15                                0.15
A:B:C          ABC + D                      6.50                                6.50

Effets du plan complet (16 essais) pour mémoire : {'A': 9.53, 'B': 12.2, 'A:B': -5.68, 'D': 5.2}
```

Chaque ligne de la demi-fraction estime **la somme** de deux effets, et la comparaison le confirme **exactement** : l'estimation obtenue avec 8 essais est égale, au centième près, à la somme des deux effets correspondants du plan complet. (On peut le démontrer : sur la fraction, $A=BCD$, donc $\sum_{\text{moitié}}A\,y=\tfrac12\left(\sum_{\text{tous}}A\,y+\sum_{\text{tous}}BCD\,y\right)$, ce qui donne $\hat\ell_A=\hat A+\widehat{BCD}$.) Comme les interactions d'ordre 3 sont presque nulles, les estimations de A, B et de D (ligne « ABC + D ») sont proches de celles du plan complet : avec 8 essais au lieu de 16, on aurait tiré les mêmes conclusions. (Le contraste « AB + CD » ne permet pas de dire à lui seul que c'est AB plutôt que CD : c'est la **connaissance du domaine**, ou une expérience complémentaire, qui tranche.)

### 8.4.3 Résolution : mesurer la qualité d'une fraction

Dans $I=ABCD$, le seul « mot » a **4 lettres**. On appelle **résolution** d'un plan fractionnaire la **longueur du plus court mot** de sa relation de définition, notée en chiffres romains. Elle résume ce qui est confondu avec quoi :

| Résolution | Plus court mot | Les effets principaux sont confondus avec… | Les interactions d'ordre 2 sont confondues avec… |
|---|---|---|---|
| **III** | 3 lettres | des interactions d'ordre 2 | des effets principaux |
| **IV** | 4 lettres | des interactions d'ordre 3 | **entre elles** |
| **V** | 5 lettres | des interactions d'ordre 4 | des interactions d'ordre 3 |

> 📐 **Pourquoi la longueur du plus court mot ?** Un effet de $j$ lettres est confondu avec le produit de cet effet par chaque mot $w$ de la relation. Ce produit a $|j - \ell|$ lettres au moins, où $\ell$ est la longueur de $w$, et au plus $j+\ell$. Avec un mot de $\ell$ lettres, un effet principal ($j=1$) est donc confondu avec un effet d'ordre au moins $\ell-1$, et une interaction d'ordre 2 avec un effet d'ordre au moins $\ell-2$. Plus $\ell$ est grand, plus la confusion est entre des effets d'ordre élevé, donc négligeables. D'où la règle de choix : **à nombre d'essais donné, on cherche la résolution la plus élevée**.

Une demi-fraction de résolution IV ($2^{4-1}$ avec $I=ABCD$) est un excellent compromis : les effets principaux sont libres de toute interaction d'ordre 2.

### 8.4.4 Plus fractionnaire encore : le plan $2^{5-2}$ et le piège de la confusion

Pour cinq facteurs, un plan complet demande 32 essais. Un plan à **8 essais** seulement est possible : on part du plan complet $2^3$ en A, B, C et on **définit deux facteurs de plus** par $D=AB$ et $E=AC$. C'est un plan $2^{5-2}$ (un quart de fraction). Les relations de définition sont $I=ABD$ et $I=ACE$, et **leur produit** $ABD\cdot ACE=A^2BCDE=BCDE$ est aussi une relation :
$$I=ABD=ACE=BCDE.$$
Le plus court mot a 3 lettres : **résolution III**. Calculons toute la structure de confusion par programme : un effet est confondu avec son produit par chaque mot, et le produit de deux ensembles de lettres est la **différence symétrique** (les lettres communes s'annulent car $L^2=I$).

```python
def produit(u, v):
    return "".join(sorted(set(u) ^ set(v)))          # lettres communes éliminées

mots = ["ABD", "ACE", "BCDE"]
tous = ["A", "B", "C", "D", "E", "AB", "AC", "AD", "AE", "BC", "BD", "BE", "CD", "CE", "DE", "ABC", "ABD", "ABE",
        "ACD", "ACE", "ADE", "BCD", "BCE", "BDE", "CDE", "ABCD", "ABCE", "ABDE", "ACDE", "BCDE", "ABCDE"]
classes = {}
for e in tous:
    classe = tuple(sorted({e} | {produit(e, w) for w in mots}, key=lambda s: (len(s), s)))
    classes[classe] = classes.get(classe, 0) + 1
print(len(tous), "effets possibles, répartis en", len(classes), "classes de confusion (8 essais = 7 contrastes + la moyenne) :\n")
for c in sorted(classes, key=lambda c: (len(c[0]), c[0])):
    print("  " + " = ".join(x or "I" for x in c))
```
<!--sortie-->
```text
31 effets possibles, répartis en 8 classes de confusion (8 essais = 7 contrastes + la moyenne) :

  I = ABD = ACE = BCDE
  A = BD = CE = ABCDE
  B = AD = CDE = ABCE
  C = AE = BDE = ABCD
  D = AB = BCE = ACDE
  E = AC = BCD = ABDE
  BC = DE = ABE = ACD
  BE = CD = ABC = ADE
```

Chaque ligne est une **classe de confusion** : les effets d'une même ligne ne peuvent pas être distingués. La première ligne regroupe les trois mots de la relation de définition avec la **moyenne générale** $I$ : ces trois interactions sont indiscernables de la constante. Remarquez que les effets principaux sont confondus avec des interactions d'ordre 2 (par exemple $D=AB$ : le facteur D est parfaitement confondu avec l'interaction de A et B). C'est le défaut de la résolution III, et voici ce que cela donne en pratique.

> ⚠️ **Une simulation instructive.** Supposons que la vérité soit la suivante : A a un effet de $+6$, B de $+4$, **A et B ont une interaction de $+8$**, et **D n'a aucun effet**. (Nous le savons parce que nous simulons ; dans la vraie vie, on l'ignore.) On exécute les 8 essais du plan $2^{5-2}$.

```python
rng = np.random.default_rng(87)
A, B, C = plan_2k(3).T
D, E = A * B, A * C                                           # générateurs de la fraction
vrai = lambda A, B, C, D, E: 50 + 3 * A + 2 * B + 4 * A * B           # effets : A = 6, B = 4, AB = 8, tout le reste 0
y = vrai(A, B, C, D, E) + rng.normal(0, 0.8, 8)

contrastes = {"A": A, "B": B, "C": C, "D (= AB)": D, "E (= AC)": E, "BC (= DE)": B * C, "ABC (= CD = BE)": A * B * C}
estimes = {nom: (col * y).sum() / 4 for nom, col in contrastes.items()}
print(pd.Series(estimes).round(2).to_string())
```
<!--sortie-->
```text
A                  5.95
B                  4.76
C                 -0.56
D (= AB)           8.17
E (= AC)          -0.23
BC (= DE)          0.09
ABC (= CD = BE)   -0.51
```

Le tableau annonce un « effet de D » d'environ **8** (la colonne D, qui est aussi la colonne AB, capte l'interaction réelle) alors que **D n'a aucun effet** ! Un analyste qui suppose les interactions négligeables conclurait « le message personnalisé fait gagner 8 commandes », et se tromperait. C'est le danger de la résolution III : on ne peut s'y fier que si l'on est certain que les interactions d'ordre 2 sont absentes.

**Le remède : le repliement (*fold-over*).** On exécute une **seconde série de 8 essais** en **inversant tous les signes** du plan ($A\to-A$, etc.). Les relations de définition de longueur impaire changent de signe d'un bloc à l'autre et disparaissent du plan combiné ; il ne reste que $I=BCDE$ : on obtient un plan de **résolution IV à 16 essais**, dans lequel les effets principaux sont séparés de toutes les interactions d'ordre 2.

```python
X1 = plan_2k(3)
bloc1 = pd.DataFrame({"A": X1[:, 0], "B": X1[:, 1], "C": X1[:, 2]})
bloc2 = -bloc1                                                # repliement : tous les signes inversés
plan = pd.concat([bloc1.assign(bloc=1), bloc2.assign(bloc=2)], ignore_index=True)
plan["D"] = np.where(plan.bloc == 1, plan.A * plan.B, -plan.A * plan.B)
plan["E"] = np.where(plan.bloc == 1, plan.A * plan.C, -plan.A * plan.C)
# vérification : sur les 16 essais, seule la relation BCDE = + 1 subsiste
print("BCDE = +1 sur tous les essais :", bool((plan.B * plan.C * plan.D * plan.E == 1).all()),
      "| ABD = +1 :", bool((plan.A * plan.B * plan.D == 1).all()), "| ACE = +1 :", bool((plan.A * plan.C * plan.E == 1).all()))

plan["y"] = vrai(plan.A, plan.B, plan.C, plan.D, plan.E) + rng.normal(0, 0.8, 16)
formule = "y ~ A + B + C + D + E + A:B + A:C + A:D + A:E + B:C + B:D + B:E"        # BC=DE, BD=CE, BE=CD restent confondus deux à deux
fo = smf.ols(formule, data=plan).fit()
t = pd.DataFrame({"effet": 2 * fo.params, "p": fo.pvalues}).drop("Intercept")
print()
print(t.round(3).to_string())
print(f"\n(ddl de l'erreur : {int(fo.df_resid)} ; s = {np.sqrt(fo.mse_resid):.2f})")
```
<!--sortie-->
```text
BCDE = +1 sur tous les essais : True | ABD = +1 : False | ACE = +1 : False

     effet      p
A    6.157  0.001
B    3.624  0.004
C    0.337  0.490
D   -0.098  0.834
E   -0.107  0.820
A:B  8.082  0.000
A:C  0.686  0.209
A:D -0.381  0.441
A:E -0.223  0.640
B:C -0.329  0.500
B:D -0.281  0.560
B:E -0.780  0.167

(ddl de l'erreur : 3 ; s = 0.86)
```

Après le repliement, l'effet de **D** est proche de zéro et celui de l'interaction **AB** réapparaît (environ 8) : les deux, qui étaient confondus dans le plan à 8 essais, sont maintenant distincts. On a payé 8 essais supplémentaires pour lever l'ambiguïté. Dans la pratique, on n'exécute le repliement **que si** la première série laisse un doute sur un effet important.

### 8.4.5 Optimiser un réglage : les surfaces de réponse

Jusqu'ici, nous cherchions *quels* facteurs comptent. Voici une autre question : **quel réglage donne la meilleure réponse ?** la gérante cuit ses céramiques de Ville B au four et veut maximiser le **pourcentage de pièces sans défaut**. Deux réglages continus : la **température** (autour de 1 000 °C) et la **durée** (autour de 6 heures). La **méthodologie des surfaces de réponse** (*response surface methodology*) procède par étapes :

1. un plan factoriel à deux niveaux **avec points au centre** pour détecter si la réponse est une surface **plane** (modèle du premier ordre) ou **courbe** ;
2. si la surface est plane, on suit le **chemin de plus forte pente** (la direction du gradient) jusqu'à ce que la réponse cesse de monter ;
3. au voisinage de l'optimum, la surface est **courbe** : on ajuste un modèle du **second ordre** (quadratique) avec un plan adapté, le **plan composite centré**, puis on cherche son sommet.

On travaille en **unités codées** : $x_1=(\text{température}-1000)/40$ et $x_2=\text{durée}-6$, de sorte que le centre est $(0,0)$ et le cube vaut $\pm1$. Voici le plan composite centré réalisé : 4 points **factoriels** $(\pm1,\pm1)$, 4 points **axiaux** $(\pm\sqrt2,0)$ et $(0,\pm\sqrt2)$, et **5 répétitions du point central**, soit 13 essais.

```python
cc = pd.read_csv("donnees/ch08-ccd-cuisson.csv")
print(cc.sort_values("ordre").to_string(index=False))
```
<!--sortie-->
```text
 ordre      x1      x2  temperature_C  duree_h  reussite
     1  0.0000  0.0000         1000.0     6.00      85.5
     2 -1.0000 -1.0000          960.0     5.00      73.8
     3  1.0000 -1.0000         1040.0     5.00      73.0
     4 -1.0000  1.0000          960.0     7.00      69.9
     5  0.0000  0.0000         1000.0     6.00      84.0
     6 -1.4142  0.0000          943.4     6.00      71.4
     7  1.0000  1.0000         1040.0     7.00      79.8
     8  1.4142  0.0000         1056.6     6.00      81.2
     9  0.0000  0.0000         1000.0     6.00      83.0
    10  0.0000  0.0000         1000.0     6.00      84.0
    11  0.0000  1.4142         1000.0     7.41      72.1
    12  0.0000 -1.4142         1000.0     4.59      70.9
    13  0.0000  0.0000         1000.0     6.00      82.5
```

> 💡 **Pourquoi ces points ?** Un plan à deux niveaux ne peut pas estimer les termes **quadratiques** $x_1^2$ et $x_2^2$ : $(\pm1)^2=1$ pour tous les points, la colonne est constante. Les **points axiaux** ($\pm\sqrt2$) et **centraux** (0) donnent trois niveaux de chaque facteur, ce qui permet de les estimer. Les **répétitions au centre** servent à estimer l'**erreur pure**, donc à tester la qualité de l'ajustement. Le choix $\alpha=\sqrt2=\sqrt[4]{n_{\text{fact}}}$ rend le plan **rotatable** : la précision de la prédiction ne dépend que de la distance au centre, pas de la direction.

**Étape 1 : y a-t-il de la courbure ?** Avec les seuls points factoriels et centraux, on compare la moyenne des points factoriels à celle du centre : si la surface était plane, elles seraient égales en moyenne. L'écart-type est estimé par les 5 répétitions du centre.

```python
centre = cc[(cc.x1 == 0) & (cc.x2 == 0)]
fact = cc[(cc.x1.abs() == 1) & (cc.x2.abs() == 1)]
ss_pe = ((centre.reussite - centre.reussite.mean()) ** 2).sum()
df_pe = len(centre) - 1
s_pe = np.sqrt(ss_pe / df_pe)
courbure = fact.reussite.mean() - centre.reussite.mean()
se_c = s_pe * np.sqrt(1 / len(fact) + 1 / len(centre))
t_c = courbure / se_c
print(f"moyenne factoriels = {fact.reussite.mean():.2f} ; moyenne au centre = {centre.reussite.mean():.2f} ; écart = {courbure:.2f}")
print(f"erreur pure : s = {s_pe:.2f} ({df_pe} ddl) ; t = {t_c:.2f} ; p = {2 * stats.t.sf(abs(t_c), df_pe):.4f}")
b1 = (fact.x1 * fact.reussite).sum() / len(fact)
b2 = (fact.x2 * fact.reussite).sum() / len(fact)
print(f"pentes du premier ordre (points factoriels) : b1 = {b1:.2f}, b2 = {b2:.2f}")
```
<!--sortie-->
```text
moyenne factoriels = 74.12 ; moyenne au centre = 83.80 ; écart = -9.67
erreur pure : s = 1.15 (4 ddl) ; t = -12.53 ; p = 0.0002
pentes du premier ordre (points factoriels) : b1 = 2.27, b2 = 0.72
```

Le centre est **nettement au-dessus** de la moyenne des coins : la réponse a un **sommet** à l'intérieur du carré, et un modèle plan serait faux. Inutile de suivre un chemin de plus forte pente : nous sommes déjà près de l'optimum, et il faut un modèle courbe.

### 8.4.6 Ajuster le modèle quadratique

Le modèle du second ordre pour deux facteurs s'écrit
$$y=\beta_0+\beta_1x_1+\beta_2x_2+\beta_{11}x_1^2+\beta_{22}x_2^2+\beta_{12}x_1x_2+\varepsilon.$$
C'est une **régression linéaire** (linéaire en les $\beta$) sur six colonnes : les moindres carrés du chapitre 1 s'appliquent tels quels.

```python
q = smf.ols("reussite ~ x1 + x2 + I(x1**2) + I(x2**2) + x1:x2", data=cc).fit()
noms = {"Intercept": "β0", "x1": "β1 (x1)", "x2": "β2 (x2)", "I(x1 ** 2)": "β11 (x1²)", "I(x2 ** 2)": "β22 (x2²)", "x1:x2": "β12 (x1 x2)"}
coef = pd.DataFrame({"estimation": q.params, "ET": q.bse, "t": q.tvalues, "p": q.pvalues}).rename(index=noms)
print(coef.round(3).to_string())
print(f"\nR² = {q.rsquared:.3f} ; R² ajusté = {q.rsquared_adj:.3f} ; s = {np.sqrt(q.mse_resid):.2f} ({int(q.df_resid)} ddl)")
```
<!--sortie-->
```text
             estimation     ET        t      p
β0               83.800  0.490  170.916  0.000
β1 (x1)           2.870  0.388    7.404  0.000
β2 (x2)           0.575  0.388    1.482  0.182
β11 (x1²)        -3.694  0.416   -8.886  0.000
β22 (x2²)        -6.094  0.416  -14.660  0.000
β12 (x1 x2)       2.675  0.548    4.880  0.002

R² = 0.980 ; R² ajusté = 0.966 ; s = 1.10 (7 ddl)
```

Les termes quadratiques et le produit $x_1x_2$ sont significatifs ; l'effet linéaire de $x_2$ ne l'est pas. On le **garde** quand même : par le principe de hiérarchie, on ne retire pas un terme d'ordre 1 si des termes d'ordre supérieur qui le contiennent ($x_2^2$, $x_1x_2$) sont dans le modèle (retirer $\beta_2$ reviendrait à imposer que le sommet soit au centre en $x_2$, ce qui dépend du choix d'origine du codage).

**Le modèle est-il adapté ?** Avec les répétitions au centre, on peut séparer le résidu en **erreur pure** (variabilité entre répétitions) et **défaut d'ajustement** (écart systématique entre le modèle et les moyennes des points) :
$$SS_{\text{résidu}}=SS_{\text{pur}}+SS_{\text{défaut}},\qquad F=\frac{SS_{\text{défaut}}/(\text{ddl}_{\text{res}}-\text{ddl}_{\text{pur}})}{SS_{\text{pur}}/\text{ddl}_{\text{pur}}}.$$
Si $F$ est grand, le modèle quadratique est insuffisant (il faudrait un ordre supérieur ou une autre échelle).

```python
ss_def, df_def = q.ssr - ss_pe, q.df_resid - df_pe
F_def = (ss_def / df_def) / (ss_pe / df_pe)
print(f"SS résidu = {q.ssr:.2f} = SS erreur pure {ss_pe:.2f} ({df_pe} ddl) + SS défaut d'ajustement {ss_def:.2f} ({int(df_def)} ddl)")
print(f"F de défaut d'ajustement = {F_def:.2f} ; p = {stats.f.sf(F_def, df_def, df_pe):.3f}")
```
<!--sortie-->
```text
SS résidu = 8.41 = SS erreur pure 5.30 (4 ddl) + SS défaut d'ajustement 3.11 (3 ddl)
F de défaut d'ajustement = 0.78 ; p = 0.562
```

Pas de défaut d'ajustement détectable ($F=0{,}78$, $p=0{,}56$) : le modèle quadratique décrit correctement la surface sur le domaine étudié. (Attention : avec seulement 4 degrés de liberté d'erreur pure, ce test a peu de puissance ; c'est un garde-fou, pas une preuve.)

### 8.4.7 Trouver l'optimum : point stationnaire et analyse canonique

Écrivons le modèle ajusté sous forme matricielle, avec $x=(x_1,x_2)^\top$, $b=(\beta_1,\beta_2)^\top$ et la matrice symétrique des termes quadratiques :
$$\hat y=\beta_0+b^\top x+x^\top Bx,\qquad B=\begin{pmatrix}\beta_{11}&\beta_{12}/2\\ \beta_{12}/2&\beta_{22}\end{pmatrix}.$$

> 📐 **Point stationnaire.** Le gradient de $\hat y$ est $b+2Bx$ (volume I, section 1.2 pour le gradient, et section 1.3 pour l'optimisation). Il s'annule au point
> $$x_s=-\tfrac12B^{-1}b,\qquad \hat y_s=\beta_0+\tfrac12\,b^\top x_s.$$
> (En effet, $Bx_s=-b/2$ donc $x_s^\top Bx_s=-b^\top x_s/2$, et $\hat y_s=\beta_0+b^\top x_s-b^\top x_s/2$.) La nature de ce point se lit sur les **valeurs propres** de $B$ (volume I, section 1.1.3) : le hessien de $\hat y$ vaut $2B$. Si **toutes** les valeurs propres sont **négatives**, $x_s$ est un **maximum** ; toutes **positives**, un minimum ; de signes **mixtes**, un **col** (point selle), qui n'est pas un optimum. Les **vecteurs propres** donnent les axes de la surface : le long de l'axe de plus petite valeur propre en valeur absolue, la réponse varie peu (une « **crête** » : plusieurs réglages donnent presque le même résultat).

```python
p = q.params
b = np.array([p["x1"], p["x2"]])
B = np.array([[p["I(x1 ** 2)"], p["x1:x2"] / 2], [p["x1:x2"] / 2, p["I(x2 ** 2)"]]])
xs = -0.5 * np.linalg.solve(B, b)
ys = p["Intercept"] + 0.5 * b @ xs
lam, vecs = np.linalg.eigh(B)

print(f"point stationnaire (codé) : x1 = {xs[0]:.3f}, x2 = {xs[1]:.3f} ; distance au centre = {np.linalg.norm(xs):.2f} (domaine : jusqu'à {np.sqrt(2):.2f})")
print(f"en unités naturelles : température = {1000 + 40 * xs[0]:.0f} °C, durée = {6 + xs[1]:.2f} h")
print(f"réponse prédite au sommet : {ys:.2f} %")
print(f"valeurs propres de B : {lam.round(2)} -> {'maximum' if (lam < 0).all() else 'minimum' if (lam > 0).all() else 'col'}")
for l, v in zip(lam, vecs.T):
    print(f"  valeur propre {l:6.2f} : axe ({v[0]:+.2f}, {v[1]:+.2f}) ; "
          f"perte de {abs(l):.2f} points par unité² d'écart au sommet le long de cet axe")

nouveau = pd.DataFrame({"x1": [xs[0]], "x2": [xs[1]]})
pred = q.get_prediction(nouveau).summary_frame(alpha=0.05)
print(f"\nIC95 de la réponse moyenne au sommet : [{pred['mean_ci_lower'][0]:.1f} ; {pred['mean_ci_upper'][0]:.1f}]")
print(f"intervalle de prédiction à 95 % pour un nouvel essai : [{pred['obs_ci_lower'][0]:.1f} ; {pred['obs_ci_upper'][0]:.1f}]")
```
<!--sortie-->
```text
point stationnaire (codé) : x1 = 0.441, x2 = 0.144 ; distance au centre = 0.46 (domaine : jusqu'à 1.41)
en unités naturelles : température = 1018 °C, durée = 6.14 h
réponse prédite au sommet : 84.47 %
valeurs propres de B : [-6.69 -3.1 ] -> maximum
  valeur propre  -6.69 : axe (-0.41, +0.91) ; perte de 6.69 points par unité² d'écart au sommet le long de cet axe
  valeur propre  -3.10 : axe (-0.91, -0.41) ; perte de 3.10 points par unité² d'écart au sommet le long de cet axe

IC95 de la réponse moyenne au sommet : [83.3 ; 85.6]
intervalle de prédiction à 95 % pour un nouvel essai : [81.6 ; 87.3]
```

Les deux valeurs propres sont négatives ($-6{,}7$ et $-3{,}1$) : le point stationnaire est bien un **maximum**, à environ **1 018 °C et 6,14 h**, avec un taux prédit de **84,5 %** (intervalle de confiance de la moyenne : 83,3 à 85,6 %). La surface retombe deux fois plus vite le long du premier axe (direction $(-0{,}41;\,+0{,}91)$, surtout la durée) que le long du second (direction $(-0{,}91;\,-0{,}41)$, surtout la température) : une durée mal réglée coûte plus cher qu'une température un peu décalée. Le sommet se trouve à l'intérieur du domaine expérimental (distance au centre de 0,46, bien inférieure au rayon $\sqrt2$ des points axiaux) : c'est une **interpolation**, ce qui est crucial ; extrapoler un modèle quadratique au-delà des essais est dangereux, car un polynôme du second degré n'a aucune raison de bien décrire la surface loin des données.

![Surface ajustée du taux de pièces sans défaut en fonction de la température et de la durée (unités codées), avec les 13 points du plan composite centré et l'optimum estimé. Les courbes de niveau sont des ellipses allongées et inclinées autour du sommet.](figures/ch08-rsm-contours.png)

La figure (code dans `build/fig_ch08.py`) montre les courbes de niveau : des **ellipses** centrées sur le sommet, inclinées à cause du terme croisé $\beta_{12}$ (température et durée **interagissent** : la meilleure durée dépend de la température). La différence entre les deux valeurs propres se voit dans la forme des ellipses : plus étroites dans la direction de forte courbure.

**Confirmer.** Un optimum prédit par un modèle est une **hypothèse** : on la teste par quelques **essais de confirmation** au réglage proposé. Nous simulons ici trois fournées au sommet estimé (avec le vrai processus, que nous connaissons, et son bruit de 0,9) :

```python
def vrai_taux(x1, x2):
    return 84 + 3 * x1 + 1 * x2 - 4 * x1 ** 2 - 6 * x2 ** 2 + 2.5 * x1 * x2

rng = np.random.default_rng(88)
confirm = vrai_taux(xs[0], xs[1]) + rng.normal(0, 0.9, 3)
print("trois fournées de confirmation :", confirm.round(1))
print(f"moyenne = {confirm.mean():.1f} %, dans l'intervalle de prédiction : {bool(((confirm >= pred['obs_ci_lower'][0]) & (confirm <= pred['obs_ci_upper'][0])).all())}")
```
<!--sortie-->
```text
trois fournées de confirmation : [84.1 84.2 83.8]
moyenne = 84.0 %, dans l'intervalle de prédiction : True
```

> ⚠️ **Les pièges de l'optimisation.**
> - Un **col** ou une **crête** (valeur propre presque nulle) ne désigne pas un optimum unique : il faut se demander quel réglage de la crête est le plus **économique** ou le plus **robuste** (par exemple, moins sensible aux variations de température du four).
> - L'optimum n'est valable que **dans le domaine étudié** et pour **la réponse mesurée** : avec **plusieurs réponses** (taux de réussite, coût énergétique, durée), on cherche un compromis (fonctions de désirabilité, courbes de niveau superposées).
> - Le modèle quadratique est une **approximation locale** : si l'optimum prédit tombe en dehors du domaine, on déplace le plan dans cette direction et on recommence plutôt que d'extrapoler.

### 8.4.8 ➕ Pour aller plus loin : les plans optimaux

> 🧭 **Section optionnelle.** Les plans classiques (factoriels, composites) supposent un domaine régulier (un cube) et un nombre d'essais « rond ». Quand le domaine est irrégulier (combinaisons **impossibles**), ou quand le budget impose un nombre d'essais particulier, on peut **calculer** un plan par ordinateur.

L'idée de la **$D$-optimalité** : la variance des coefficients estimés est proportionnelle à $(X^\top X)^{-1}$ (chapitre 1, section 1.2) ; on cherche les essais qui rendent cette matrice « la plus petite », c'est-à-dire qui **maximisent $\det(X^\top X)$**. Le **volume** de l'ellipsoïde de confiance de $\hat\beta$ est en effet proportionnel à $\det(X^\top X)^{-1/2}$. On le fait par un **algorithme d'échange** : on part de $n$ points tirés dans un ensemble de **candidats**, et on remplace un point par un candidat tant que cela augmente le déterminant.

```python
def info(points):
    x1, x2 = points[:, 0], points[:, 1]
    Xm = np.column_stack([np.ones(len(points)), x1, x2, x1 ** 2, x2 ** 2, x1 * x2])      # modèle quadratique
    return np.linalg.det(Xm.T @ Xm)

def echange(candidats, n, rng, departs=20):
    meilleur = (-1, None)
    for _ in range(departs):
        idx = list(rng.choice(len(candidats), n, replace=True))
        change = True
        while change:
            change = False
            for pos in range(n):
                best_j, best_d = idx[pos], info(candidats[idx])
                for j in range(len(candidats)):
                    essai = idx.copy()
                    essai[pos] = j
                    d = info(candidats[essai])
                    if d > best_d * (1 + 1e-9):
                        best_j, best_d, change = j, d, True
                idx[pos] = best_j
        d = info(candidats[idx])
        if d > meilleur[0]:
            meilleur = (d, idx.copy())
    return meilleur

rng = np.random.default_rng(89)
grille = np.array([(a, b) for a in np.linspace(-1, 1, 5) for b in np.linspace(-1, 1, 5)])
d_opt, idx = echange(grille, 9, rng)
factoriel_3x3 = np.array([(a, b) for a in (-1, 0, 1) for b in (-1, 0, 1)])
au_hasard = np.median([info(grille[rng.choice(25, 9, replace=False)]) for _ in range(2000)])
print("9 essais choisis parmi la grille 5 x 5 :")
print(pd.Series([tuple(grille[i]) for i in idx]).value_counts().sort_index().to_string())
print(f"\ndet(X'X) : D-optimal = {d_opt:.0f} ; factoriel 3x3 = {info(factoriel_3x3):.0f} ; "
      f"9 points au hasard (médiane sur 2000 tirages) = {au_hasard:.0f}")

# avec une contrainte : la combinaison « tout haut » (x1 + x2 > 1) est impossible (le four ne le permet pas)
possible = grille[grille.sum(axis=1) <= 1.0]
d_c, idx_c = echange(possible, 9, rng)
print(f"\nSous la contrainte x1 + x2 <= 1 ({len(possible)} candidats), plan D-optimal à 9 essais (det = {d_c:.0f}) :")
print(pd.Series([tuple(possible[i]) for i in idx_c]).value_counts().sort_index().to_string())
```
<!--sortie-->
```text
9 essais choisis parmi la grille 5 x 5 :
(-1.0, -1.0)    1
(-1.0, 0.0)     1
(-1.0, 1.0)     1
(0.0, -1.0)     1
(0.0, 0.0)      1
(0.0, 1.0)      1
(1.0, -1.0)     1
(1.0, 0.0)      1
(1.0, 1.0)      1

det(X'X) : D-optimal = 5184 ; factoriel 3x3 = 5184 ; 9 points au hasard (médiane sur 2000 tirages) = 94

Sous la contrainte x1 + x2 <= 1 (22 candidats), plan D-optimal à 9 essais (det = 1920) :
(-1.0, -1.0)    2
(-1.0, 0.0)     1
(-1.0, 1.0)     1
(0.0, -1.0)     1
(0.0, 0.0)      1
(0.0, 1.0)      1
(1.0, -1.0)     1
(1.0, 0.0)      1
```

Sur le domaine carré, l'algorithme retrouve **exactement** la grille $3\times3$ classique (le plan factoriel à trois niveaux, de même déterminant, 5 184) : les plans classiques ne sont pas arbitraires, ils sont souvent optimaux. Pour mémoire, 9 points tirés au hasard font en médiane 55 fois moins bien (déterminant de 94). L'intérêt de l'optimisation numérique apparaît dès que le domaine est **contraint** : le plan composite centré serait inutilisable tel quel (le coin $(1,1)$ est impossible), alors que l'algorithme propose immédiatement un plan adapté : la grille $3\times3$ privée du coin impossible, avec le coin opposé $(-1,-1)$ **répété**. Il faut toutefois rester prudent : un plan $D$-optimal dépend **du modèle supposé** (ici un quadratique) ; si le modèle est faux, l'optimalité ne signifie plus grand-chose.

### 8.4.9 Ce que cachaient les données

- **Plan $2^{4-1}$** : les effets de la demi-fraction (A, B, AB, D) sont proches de ceux du plan complet de 8.3.6, ce qui était attendu car la vérité (effets de $8$, $12$, $-6$, $5$ ; le reste nul) respecte la parcimonie. Les confusions A+BCD, etc. n'ont gêné que parce que les interactions d'ordre 3 sont réellement nulles.
- **Plan $2^{5-2}$** : nous avions programmé $A=6$, $B=4$, $AB=8$ et $D=0$. La fraction à 8 essais a attribué **à tort** un effet d'environ 8 à D ; le repliement l'a corrigé. La confusion n'est pas un défaut de calcul, c'est une **conséquence logique** du choix des générateurs.
- **Surface de réponse** : le vrai modèle était $y=84+3x_1+x_2-4x_1^2-6x_2^2+2{,}5x_1x_2$, dont le sommet exact est en $(x_1,x_2)=(0{,}429;\,0{,}173)$, soit environ **1 017 °C** et **6,17 h**, avec un taux maximal de 84,7 %. Le plan à 13 essais a estimé le sommet en $(0{,}441;\,0{,}144)$, soit 1 018 °C et 6,14 h, avec un taux de 84,5 % : à environ 1 °C et 0,03 h de la vérité (1 017 °C, 6,17 h, 84,7 %). Les trois fournées de confirmation (84,1 ; 84,2 ; 83,8) tombent dans l'intervalle de prédiction. Ce niveau de précision est celui d'une expérience **bien conçue et peu bruitée** ($\sigma=0{,}9$) ; avec un bruit plus fort ou moins de répétitions au centre, le sommet estimé aurait été moins précis.

> ✅ **À retenir.**
> - Un plan **fractionnaire** $2^{k-p}$ n'exécute qu'une fraction $2^{-p}$ des combinaisons, définie par des **générateurs** ; les effets sont alors **confondus** (alias) en classes, déterminées par la **relation de définition**.
> - La **résolution** (longueur du plus court mot) dit ce qui est confondu avec quoi : **III** (principaux/interactions d'ordre 2), **IV** (principaux libres, interactions d'ordre 2 entre elles), **V** (tout propre jusqu'à l'ordre 2). À nombre d'essais donné, cherchez la résolution la plus élevée.
> - La confusion peut **tromper** (résolution III) : un **repliement** (inversion de tous les signes) lève l'ambiguïté au prix d'essais supplémentaires.
> - Les **surfaces de réponse** cherchent le meilleur réglage : détecter la **courbure** (points au centre), puis ajuster un **modèle quadratique** avec un **plan composite centré** (points factoriels, axiaux, centraux).
> - Le **point stationnaire** $x_s=-\tfrac12B^{-1}b$ est un maximum si les valeurs propres de $B$ sont négatives ; vérifiez qu'il est **dans le domaine**, testez le **défaut d'ajustement**, **confirmez** par des essais.
> - Les **plans optimaux** ($D$-optimalité) calculent un plan quand le domaine ou le budget sortent des cadres classiques ; ils dépendent du modèle supposé.
