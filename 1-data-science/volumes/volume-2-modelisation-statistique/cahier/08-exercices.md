# Chapitre 8 : Plans d'expériences — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 8 du livre (**➕ Plans d'expériences**, entièrement optionnel). Vous y trouverez onze **applications guidées**, avec le code complet des simulations et des analyses que le livre ne fait que résumer, puis treize **exercices corrigés**. Il faut avoir lu les sections correspondantes ; les données sont celles du livre : des fichiers simulés `donnees/ch08-*.csv` (graines fixes, script `build/donnees_ch08.py`), dont nous connaissons la vérité. Les applications 8.2 et 8.3 se suivent (exécutez-les dans l'ordre) ; les autres sont indépendantes.

Préparation commune : les bibliothèques utilisées dans tout le chapitre.

```python
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm
```

## Applications

### Application 8.1 — Randomiser, répéter, comparer avec un plan « un facteur à la fois »

*Section 8.1 du livre.* Trois résultats du livre sont des simulations : l'affectation naïve contre l'affectation aléatoire, la pseudo-réplication, et la comparaison d'un plan « un facteur à la fois » (OFAT) avec un plan factoriel. Refaites-les, puis changez les paramètres (écart-type du bruit, nombre de jours) pour voir comment les conclusions bougent.

**Étape 1 : affectation naïve contre affectation aléatoire.** Deux vitrines A et B sont *équivalentes* ; le week-end vend 60 € de plus. La version naïve met A du lundi au jeudi et B du vendredi au dimanche ; la version aléatoire tire 14 jours pour A et 14 pour B.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(81)
jours = np.arange(28)                      # 4 semaines ; le jour 0 est un lundi
jour_semaine = jours % 7                   # 0 = lundi ... 6 = dimanche
effet_jour = np.where(jour_semaine >= 4, 60, 0)    # vendredi, samedi, dimanche : +60 €

naif_A = jour_semaine <= 3                 # A : lundi-jeudi (16 jours) ; B : vendredi-dimanche (12 jours)
ecarts = {"naïve": [], "aléatoire": []}
rejets = {"naïve": 0, "aléatoire": 0}
n_sim = 2000
for _ in range(n_sim):
    y = 200 + effet_jour + rng.normal(0, 25, 28)     # AUCUN effet de la vitrine : A = B
    lab_A = {"naïve": naif_A, "aléatoire": rng.permutation(np.r_[np.ones(14, bool), np.zeros(14, bool)])}
    for nom, A in lab_A.items():
        ecarts[nom].append(y[~A].mean() - y[A].mean())
        rejets[nom] += stats.ttest_ind(y[~A], y[A], equal_var=False).pvalue < 0.05

for nom in ecarts:
    e = np.array(ecarts[nom])
    print(f"affectation {nom:9s}: écart moyen B - A = {e.mean():6.1f} € ; écart-type = {e.std():5.1f} ; "
          f"'effet significatif' dans {100 * rejets[nom] / n_sim:5.1f} % des expériences")
```
<!--sortie-->
```text
affectation naïve    : écart moyen B - A =   60.3 € ; écart-type =   9.4 ; 'effet significatif' dans 100.0 % des expériences
affectation aléatoire: écart moyen B - A =   -0.1 € ; écart-type =  14.8 ; 'effet significatif' dans   5.2 % des expériences
```

On attend un écart moyen B − A d'environ 60 € avec l'affectation naïve (et un « effet significatif » presque à chaque expérience), et d'environ 0 avec le tirage au sort (un test qui se trompe dans 5 % des cas, comme son niveau l'annonce). Vérifiez ces ordres de grandeur sur votre sortie.

**Étape 2 : la pseudo-réplication.** Deux vitrines sans aucune différence, 5 jours chacune, 40 clients par jour, avec un aléa propre à chaque jour. On compare le test « 200 clients contre 200 clients » (faux : les clients d'un même jour ne sont pas indépendants) au test « 5 jours contre 5 jours » (juste).

```python
rng = np.random.default_rng(83)

faux, bon = 0, 0
n_sim = 3000
for _ in range(n_sim):
    aleas_jour = rng.normal(0, 25, (2, 5))                           # un aléa par (vitrine, jour)
    y = 200 + aleas_jour[:, :, None] + rng.normal(0, 40, (2, 5, 40))  # forme : (vitrine, jour, client)
    # (a) on traite les 200 clients de chaque vitrine comme indépendants : FAUX
    faux += stats.ttest_ind(y[0].ravel(), y[1].ravel()).pvalue < 0.05
    # (b) on résume chaque journée par sa moyenne : l'unité expérimentale est le jour (5 contre 5)
    bon += stats.ttest_ind(y[0].mean(axis=1), y[1].mean(axis=1)).pvalue < 0.05

print(f"Test sur 200 clients contre 200 clients : 'effet' trouvé dans {100 * faux / n_sim:.1f} % des cas")
print(f"Test sur 5 jours contre 5 jours         : 'effet' trouvé dans {100 * bon / n_sim:.1f} % des cas")
```
<!--sortie-->
```text
Test sur 200 clients contre 200 clients : 'effet' trouvé dans 56.9 % des cas
Test sur 5 jours contre 5 jours         : 'effet' trouvé dans 5.1 % des cas
```

Le premier test voit un effet qui n'existe pas dans plus de la moitié des cas ; le second respecte son niveau de 5 %. *Pour aller plus loin :* passez à 20 jours par vitrine : que devient la puissance du test juste si l'on ajoute un vrai effet de 20 € ?

**Étape 3 : un facteur à la fois contre plan factoriel.** Le tableau des quatre moyennes sans bruit, puis la comparaison, à nombre d'essais égal, de la variance de l'estimation de l'effet du cadeau.

```python
import pandas as pd

vrai = pd.DataFrame({"prix normal": [50, 55], "promo -10 %": [62, 60]}, index=["standard", "cadeau"])
print(vrai)

effet_A_prix_normal = vrai.loc["cadeau", "prix normal"] - vrai.loc["standard", "prix normal"]
effet_A_promo = vrai.loc["cadeau", "promo -10 %"] - vrai.loc["standard", "promo -10 %"]
effet_B_standard = vrai.loc["standard", "promo -10 %"] - vrai.loc["standard", "prix normal"]
effet_B_cadeau = vrai.loc["cadeau", "promo -10 %"] - vrai.loc["cadeau", "prix normal"]
print()
print("effet du cadeau au prix normal :", effet_A_prix_normal, "| avec la promo :", effet_A_promo)
print("effet de la promo en standard   :", effet_B_standard, "| en cadeau       :", effet_B_cadeau)

# effets « principaux » et interaction (définitions précisées en 8.3)
eff_A = (effet_A_prix_normal + effet_A_promo) / 2
eff_B = (effet_B_standard + effet_B_cadeau) / 2
eff_AB = (effet_A_promo - effet_A_prix_normal) / 2
print(f"effet principal du cadeau A = {eff_A}, de la promo B = {eff_B}, interaction AB = {eff_AB}")
```
<!--sortie-->
```text
          prix normal  promo -10 %
standard           50           62
cadeau             55           60

effet du cadeau au prix normal : 5 | avec la promo : -2
effet de la promo en standard   : 12 | en cadeau       : 5
effet principal du cadeau A = 1.5, de la promo B = 8.5, interaction AB = -3.5
```

```python
rng = np.random.default_rng(84)
sigma, n_sim = 4.0, 100000
mu = {"std_normal": 50, "cadeau_normal": 55, "std_promo": 62, "cadeau_promo": 60}

# plan factoriel : 4 essais, un par case
y = {k: v + rng.normal(0, sigma, n_sim) for k, v in mu.items()}
A_fact = ((y["cadeau_normal"] + y["cadeau_promo"]) - (y["std_normal"] + y["std_promo"])) / 2

# OFAT : 4 essais aussi (départ répété 2 fois, puis A changé, puis B changé)
depart = (mu["std_normal"] + rng.normal(0, sigma, n_sim) + mu["std_normal"] + rng.normal(0, sigma, n_sim)) / 2
A_ofat = (mu["cadeau_normal"] + rng.normal(0, sigma, n_sim)) - depart

print(f"variance de l'estimation de A : factoriel = {A_fact.var():.1f}  (théorie {sigma**2:.1f})")
print(f"                                OFAT      = {A_ofat.var():.1f}  (théorie {1.5 * sigma**2:.1f})")
print(f"moyenne estimée de A          : factoriel = {A_fact.mean():.2f} (effet principal vrai 1.5) ; "
      f"OFAT = {A_ofat.mean():.2f} (effet de A au prix normal : 5)")
```
<!--sortie-->
```text
variance de l'estimation de A : factoriel = 16.1  (théorie 16.0)
                                OFAT      = 24.0  (théorie 24.0)
moyenne estimée de A          : factoriel = 1.48 (effet principal vrai 1.5) ; OFAT = 5.01 (effet de A au prix normal : 5)
```

La variance vaut $\sigma^2=16$ pour le plan factoriel et $1{,}5\,\sigma^2=24$ pour l'OFAT. Vérifiez aussi que l'OFAT estime l'effet du cadeau *au prix normal* (5), alors que le factoriel estime son effet *moyen* (1,5).

### Application 8.2 — ANOVA à un facteur sur les vitrines

*Sections 8.2.1 à 8.2.4.* On analyse l'expérience des quatre agencements de vitrine (48 journées tirées au hasard, 12 par agencement) : de la décomposition de la variance au test $F$, puis le lien avec le test de Student et la régression.

**Étape 1 : les données.**

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

**Étape 2 : la décomposition sur un exemple de neuf nombres.** Trois agencements, trois journées chacun. Les sommes de carrés doivent valoir $SS_B=2450$ et $SS_W=600$, et leur somme doit retomber sur la variabilité totale (3050).

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

**Étape 3 : le test $F$ sur les données de la gérante**, à la main puis avec `statsmodels` et `scipy`. Les trois calculs doivent coïncider : $F=3{,}10$ avec 3 et 44 degrés de liberté, $p=0{,}036$.

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

**Étape 4 : l'ANOVA est un test de Student, et une régression.**

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

Avec deux groupes, $F=t^2$. Avec quatre, le test $F$ global de la régression sur indicatrices est celui de l'ANOVA, et $R^2=SS_B/SS_T$.

### Application 8.3 — Vérifier les hypothèses, comparer les groupes, mesurer l'effet

*Sections 8.2.5 à 8.2.7.* Cette application prolonge la précédente (mêmes variables).

**Étape 1 : les hypothèses.** Normalité des résidus (Shapiro-Wilk), égalité des variances (Levene, Bartlett), puis les deux solutions de repli (ANOVA de Welch, Kruskal-Wallis).

```python
residus = modele.resid
groupes = [x["ventes"].to_numpy() for _, x in df.groupby("agencement")]

print("Shapiro-Wilk (normalité des résidus)    : p =", round(stats.shapiro(residus).pvalue, 3))
print("Levene/Brown-Forsythe (variances égales) : p =", round(stats.levene(*groupes, center="median").pvalue, 3))
print("Bartlett (variances égales, sensible à la non-normalité) : p =", round(stats.bartlett(*groupes).pvalue, 3))
sd = df.groupby("agencement")["ventes"].std()
print(f"rapport plus grand / plus petit écart-type : {sd.max() / sd.min():.2f}")
```
<!--sortie-->
```text
Shapiro-Wilk (normalité des résidus)    : p = 0.521
Levene/Brown-Forsythe (variances égales) : p = 0.276
Bartlett (variances égales, sensible à la non-normalité) : p = 0.369
rapport plus grand / plus petit écart-type : 1.60
```

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

Le Kruskal-Wallis ($p=0{,}072$) est un peu moins tranché que l'ANOVA ($p=0{,}036$) : la preuve est limite, et il faut le dire.

**Étape 2 : les comparaisons deux à deux.** On calcule le seuil de Tukey à la main, puis avec la bibliothèque ; on compare avec Bonferroni.

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

**Étape 3 : un contraste planifié et la taille d'effet.** « Par thème » contre la moyenne des trois autres, puis $\eta^2$, $\omega^2$ et $f$ de Cohen.

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

*Pour aller plus loin :* quel est le plus petit nombre de jours par agencement pour lequel Tukey détecterait l'écart « Par thème − Classique » observé (40,7 €) ?

### Application 8.4 — Les blocs : combien de bruit retire-t-on ?

*Section 8.2.8.* L'expérience refaite en 8 semaines (les blocs), chaque agencement testé une fois par semaine.

**Étape 1 : la décomposition en blocs sur neuf nombres.**

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

**Étape 2 : les vraies données, avec et sans blocs.** Même mesure, mêmes 32 ventes, deux analyses.

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

**Étape 3 : l'efficacité relative et le seuil de Tukey.**

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

On doit trouver un carré moyen d'erreur divisé par dix (1 715 puis 174), un $F$ de 1,5 puis 15,2, une efficacité relative d'environ 9 et un seuil de Tukey de 18 € (contre 37 € sans blocs).

### Application 8.5 — Deux facteurs et leur interaction

*Section 8.2.9.* L'emballage (Kraft, Tissu, Coffret) et le canal (Site, Réseaux), 10 commandes par combinaison.

**Étape 1 : le tableau des moyennes et la lecture de l'interaction.**

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
Kraft               43.5  48.0           45.7
Tissu               48.0  50.3           49.2
Coffret             69.8  60.3           65.0
moyenne colonne     53.8  52.9           53.3
```

**Étape 2 : le tableau d'analyse de variance**, et la vérification à la main d'une somme de carrés.

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

**Étape 3 : les effets simples**, c'est-à-dire l'effet de l'emballage à chaque niveau du canal.

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
Réseaux   : F emballage = 42.1, p = 0.0000 ; gain Coffret - Kraft = 26.3 €
```

Interprétez : pourquoi l'effet principal du canal est-il presque nul alors que le canal modifie nettement l'effet du Coffret ?

### Application 8.6 — Dimensionner une expérience : la puissance d'une ANOVA

*Section 8.2.10.* Moyennes vraies prévues : 200, 215, 240 et 205 €, écart-type 30 €, 12 jours par agencement.

**Étape 1 : la puissance par la loi de Fisher non centrale**, par `statsmodels`, et par simulation.

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

**Étape 2 : et si l'effet était deux fois plus petit ?** Puissance de la même expérience, puis nombre de jours nécessaire pour atteindre 80 %.

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

On doit trouver 83 % de puissance prévue, 27 % si l'effet est moitié moindre, et 43 jours par agencement (172 au total) pour retrouver 80 %.

### Application 8.7 — Un plan factoriel $2^3$ de A à Z

*Section 8.3.* Trois facteurs (emballage A, prix B, relance C), huit combinaisons, deux répétitions : 16 semaines.

**Étape 1 : le tableau des signes et l'orthogonalité.**

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

**Étape 2 : les données et les effets à la main.**

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

**Étape 3 : l'algorithme de Yates.** On doit retrouver exactement les mêmes effets.

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

**Étape 4 : tout par régression**, avec l'erreur pure des répétitions ; puis la décomposition de la variance.

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

**Étape 5 : le modèle réduit et la prédiction des quatre réglages.**

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

**Étape 6 : la puissance du plan pour un effet de 4 commandes.**

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

### Application 8.8 — Un plan $2^4$ sans répétition : Lenth et le diagramme demi-normal

*Section 8.3.6.* Quatre facteurs (on ajoute D, un message personnalisé), seize essais, aucune répétition : quinze effets, zéro degré de liberté pour l'erreur.

**Étape 1 : la méthode de Lenth.** On estime l'écart-type du bruit à partir des effets eux-mêmes (le principe de parcimonie), puis on déclare « actifs » ceux qui dépassent la marge simultanée.

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

**Étape 2 : confirmer sur les seuls effets actifs.**

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

Quatre effets actifs doivent ressortir : B, A, AB et D.

### Application 8.9 — Plans fractionnaires : alias, résolution, repliement

*Section 8.4.1 à 8.4.4.*

**Étape 1 : combien d'effets, de quel ordre ?**

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

**Étape 2 : la demi-fraction $2^{4-1}$ avec $D=ABC$.** On prend, parmi les 16 essais de l'application précédente, les 8 qui vérifient $ABCD=+1$, et on compare à ce que donne le plan complet : chaque contraste estime la *somme* de deux effets confondus.

```python
def plan_2k(k):
    return np.array([[(1 if (i >> j) & 1 else -1) for j in range(k)] for i in range(2 ** k)])

xa, xb, xc = plan_2k(3).T
xd = xa * xb * xc                                       # générateur : D = ABC
print("A = BCD :", np.array_equal(xa, xb * xc * xd), "| AB = CD :", np.array_equal(xa * xb, xc * xd))

g4 = pd.read_csv("donnees/ch08-factoriel-2p4.csv")
complet = (2 * smf.ols("commandes ~ A * B * C * D", data=g4).fit().params).drop("Intercept")
demi = g4[g4.A * g4.B * g4.C * g4.D == 1]               # la demi-fraction I = ABCD : 8 essais sur 16
eff_demi = (2 * smf.ols("commandes ~ A * B * C", data=demi).fit().params).drop("Intercept")
alias = {"A": ["A", "B:C:D"], "B": ["B", "A:C:D"], "C": ["C", "A:B:D"], "A:B": ["A:B", "C:D"],
         "A:C": ["A:C", "B:D"], "B:C": ["B:C", "A:D"], "A:B:C": ["A:B:C", "D"]}
tab = pd.DataFrame({"demi-fraction": eff_demi.round(2),
                    "somme des alias (plan complet)": [round(sum(complet[e] for e in alias[i]), 2) for i in eff_demi.index]})
print(tab)
```
<!--sortie-->
```text
A = BCD : True | AB = CD : True
       demi-fraction  somme des alias (plan complet)
A               9.00                            9.00
B              11.10                           11.10
A:B            -6.35                           -6.35
C              -1.20                           -1.20
A:C            -0.45                           -0.45
B:C             0.15                            0.15
A:B:C           6.50                            6.50
```

Les deux colonnes doivent être égales au centième près.

**Étape 3 : les classes de confusion du plan $2^{5-2}$** ($D=AB$, $E=AC$), calculées par programme : le produit de deux ensembles de lettres est leur différence symétrique.

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

**Étape 4 : le piège de la résolution III, puis le repliement.** On suppose A = +6, B = +4, AB = +8 et *aucun* effet de D. Les 8 essais attribuent à tort un effet d'environ 8 à D (= AB) ; le repliement (tous les signes inversés) le corrige.

```python
rng = np.random.default_rng(87)
xa, xb, xc = plan_2k(3).T
xd, xe = xa * xb, xa * xc                                # générateurs D = AB et E = AC
vrai = lambda a, b, c, d, e: 50 + 3 * a + 2 * b + 4 * a * b          # effets : A = 6, B = 4, AB = 8, le reste 0
y = vrai(xa, xb, xc, xd, xe) + rng.normal(0, 0.8, 8)
contrastes = {"A": xa, "B": xb, "C": xc, "D (= AB)": xd, "E (= AC)": xe, "BC (= DE)": xb * xc, "ABC (= CD = BE)": xa * xb * xc}
print(pd.Series({nom: (col * y).sum() / 4 for nom, col in contrastes.items()}).round(2))
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
dtype: float64
```

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

L'effet de D tombe près de zéro et l'interaction A:B réapparaît à environ 8 : les deux, confondus dans le plan à 8 essais, sont maintenant séparés.

### Application 8.10 — Surface de réponse : trouver le meilleur réglage du four

*Section 8.4.5 à 8.4.7.* Température (autour de 1 000 °C) et durée (autour de 6 h) ; réponse : pourcentage de pièces sans défaut. Plan composite centré à 13 essais : 4 points factoriels, 4 axiaux, 5 répétitions du centre.

**Étape 1 : y a-t-il de la courbure ?**

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

**Étape 2 : le modèle quadratique et le défaut d'ajustement.**

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

**Étape 3 : le point stationnaire, sa nature, sa précision.**

```python
pq = q.params
bq = np.array([pq["x1"], pq["x2"]])
Bq = np.array([[pq["I(x1 ** 2)"], pq["x1:x2"] / 2], [pq["x1:x2"] / 2, pq["I(x2 ** 2)"]]])
xs = -0.5 * np.linalg.solve(Bq, bq)
ys = pq["Intercept"] + 0.5 * bq @ xs
lam, vecs = np.linalg.eigh(Bq)
print(f"point stationnaire (codé) : x1 = {xs[0]:.3f}, x2 = {xs[1]:.3f} ; distance au centre = {np.linalg.norm(xs):.2f}")
print(f"en unités naturelles : température = {1000 + 40 * xs[0]:.0f} °C, durée = {6 + xs[1]:.2f} h ; réponse prédite : {ys:.2f} %")
print(f"valeurs propres de B : {lam.round(2)} -> {'maximum' if (lam < 0).all() else 'minimum' if (lam > 0).all() else 'col'}")
pred = q.get_prediction(pd.DataFrame({"x1": [xs[0]], "x2": [xs[1]]})).summary_frame(alpha=0.05)
print(f"IC95 de la réponse moyenne : [{pred['mean_ci_lower'][0]:.1f} ; {pred['mean_ci_upper'][0]:.1f}]")
print(f"intervalle de prédiction à 95 % : [{pred['obs_ci_lower'][0]:.1f} ; {pred['obs_ci_upper'][0]:.1f}]")
```
<!--sortie-->
```text
point stationnaire (codé) : x1 = 0.441, x2 = 0.144 ; distance au centre = 0.46
en unités naturelles : température = 1018 °C, durée = 6.14 h ; réponse prédite : 84.47 %
valeurs propres de B : [-6.69 -3.1 ] -> maximum
IC95 de la réponse moyenne : [83.3 ; 85.6]
intervalle de prédiction à 95 % : [81.6 ; 87.3]
```

**Étape 4 : confirmer par de nouveaux essais.** Trois fournées simulées au sommet estimé, avec le vrai processus (que nous connaissons).

```python
def vrai_taux(x1, x2):
    return 84 + 3 * x1 + 1 * x2 - 4 * x1 ** 2 - 6 * x2 ** 2 + 2.5 * x1 * x2

rng = np.random.default_rng(88)
confirm = vrai_taux(xs[0], xs[1]) + rng.normal(0, 0.9, 3)
dans = ((confirm >= pred["obs_ci_lower"][0]) & (confirm <= pred["obs_ci_upper"][0])).all()
print("trois fournées de confirmation :", confirm.round(1), "| toutes dans l'intervalle de prédiction :", bool(dans))
```
<!--sortie-->
```text
trois fournées de confirmation : [84.1 84.2 83.8] | toutes dans l'intervalle de prédiction : True
```

Le sommet attendu est à environ 1 018 °C et 6,14 h, avec 84,5 % de pièces sans défaut ; le vrai optimum est à 1 017 °C et 6,17 h (84,7 %).

### Application 8.11 — Un plan D-optimal par algorithme d'échange

*Section 8.4.8 (optionnelle).* On cherche les 9 essais qui maximisent $\det(X^\top X)$ pour le modèle quadratique, d'abord sur le carré, puis sous une contrainte qui rend un coin impossible.

**Étape 1 : le critère et l'algorithme d'échange.**

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
```

**Étape 2 : sur le carré, puis avec la contrainte** $x_1+x_2\le 1$.

```python
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

Sur le carré, l'algorithme retrouve la grille $3\times3$ classique (même déterminant, 5 184) ; avec la contrainte, il propose la grille privée du coin impossible, avec le coin opposé répété.

## Exercices

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 2 à 4 se font avec les mêmes trois groupes ; 7, 9 et 10 se font entièrement à la main.

### Exercice 8.1 ⭐ — Concevoir une expérience (section 8.1 du livre)

La gérante veut comparer deux présentations de la page d'accueil de son site, A et B. Elle propose : « affichage A la semaine prochaine, affichage B la semaine suivante, et je compare les commandes ». (a) Quelle est l'unité expérimentale ? (b) Citez deux raisons pour lesquelles la comparaison sera biaisée. (c) Proposez un plan qui applique les trois principes de Fisher (randomisation, répétition, blocage).

### Exercice 8.2 ⭐ — ANOVA à la main (section 8.2 du livre)

Trois fournisseurs de papier d'emballage, quatre lots chacun ; on mesure la résistance à la déchirure (en newtons) :
Fournisseur 1 : $52,\,48,\,50,\,50$ ; Fournisseur 2 : $56,\,58,\,54,\,56$ ; Fournisseur 3 : $62,\,60,\,64,\,62$.
Calculez les moyennes, $SS_B$, $SS_W$, les carrés moyens et la statistique $F$. Combien de degrés de liberté ? Que conclure ?

### Exercice 8.3 ⭐⭐ — Taille d'effet (section 8.2 du livre)

Avec les données de l'exercice 2, calculez $\eta^2$ et $\omega^2$. Pourquoi $\omega^2<\eta^2$ ? Vérifiez ensuite que la régression sur indicatrices redonne le même $F$ et le même $R^2$.

### Exercice 8.4 ⭐⭐ — Comparaisons multiples (section 8.2 du livre)

Toujours avec les données de l'exercice 2, calculez le seuil HSD de Tukey (utilisez $q_{0{,}95;\,3,\,9}\approx3{,}95$) et dites quelles paires de fournisseurs diffèrent. Pourquoi ne pas simplement faire trois tests de Student à 5 % ?

### Exercice 8.5 ⭐⭐ — Blocs (section 8.2 du livre)

Quatre traitements sont testés dans trois blocs (trois semaines) ; ventes en dizaines de € :

| | traitement 1 | traitement 2 | traitement 3 | traitement 4 |
|---|---|---|---|---|
| semaine 1 | 10 | 14 | 12 | 16 |
| semaine 2 | 20 | 25 | 22 | 27 |
| semaine 3 | 31 | 33 | 32 | 36 |

(a) Calculez $SS_{\text{blocs}}$, $SS_{\text{traitements}}$, $SS_E$ et leurs degrés de liberté. (b) Comparez le $F$ des traitements avec et sans les blocs. (c) Que s'est-il passé ?

### Exercice 8.6 ⭐⭐ — Interaction (section 8.3 du livre)

On teste deux facteurs, A et B, à deux niveaux ; les moyennes de réponse sont $\bar y_{A-B-}=20$, $\bar y_{A+B-}=30$, $\bar y_{A-B+}=25$, $\bar y_{A+B+}=15$. Calculez l'effet principal de A, celui de B et l'interaction AB. L'effet principal de A est nul : A n'a-t-il donc aucune influence ? Quel est le meilleur réglage ?

### Exercice 8.7 ⭐⭐ — Algorithme de Yates (section 8.3 du livre)

Plan $2^3$ sans répétition, essais en ordre standard : $(1)=10$, $a=14$, $b=12$, $ab=20$, $c=11$, $ac=15$, $bc=13$, $abc=21$. Calculez les sept effets et la moyenne par l'algorithme de Yates, puis par les contrastes. Quels effets sont non nuls ?

### Exercice 8.8 ⭐⭐⭐ — Puissance d'un plan factoriel (section 8.3 du livre)

Dans un plan $2^3$ répliqué $r$ fois, l'écart-type du bruit est $\sigma=3$. On veut détecter un effet de $\Delta=4$ avec une puissance d'au moins 80 %, au seuil de 5 %. (a) Donnez l'écart-type d'un effet en fonction de $r$. (b) Estimez à la main un ordre de grandeur de $r$ avec l'approximation normale. (c) Calculez la valeur exacte avec la loi de Student non centrale.

### Exercice 8.9 ⭐⭐ — Confusion (section 8.4 du livre)

On veut un plan $2^{4-1}$ (8 essais, 4 facteurs). (a) Avec le générateur $D=ABC$, donnez la relation de définition, la résolution et les alias de $AB$. (b) Avec $D=AB$, mêmes questions. (c) Lequel choisir et pourquoi ?

### Exercice 8.10 ⭐⭐⭐ — Un plan $2^{6-2}$ (section 8.4 du livre)

On construit 6 facteurs en 16 essais avec les générateurs $E=ABC$ et $F=BCD$. (a) Donnez la relation de définition complète. (b) Quelle est la résolution ? (c) Donnez les alias de $A$ et de $AB$. (d) Peut-on séparer les interactions $AB$ et $CE$ ?

### Exercice 8.11 ⭐⭐ — Surface de réponse (section 8.4 du livre)

Un modèle du second ordre ajusté sur un plan composite centré à 2 facteurs ($\alpha=\sqrt2$) est $\hat y=70+4x_1+2x_2-3x_1^2-x_2^2+x_1x_2$. (a) Trouvez le point stationnaire et la réponse prédite. (b) Est-ce un maximum ? (c) Peut-on faire confiance à ce point ?

### Exercice 8.12 ⭐⭐⭐ — Simuler l'effet des blocs (section 8.2 du livre)

On compare deux traitements avec 12 unités. L'effet vrai du traitement est de $+15$, l'écart-type du bruit de $10$ et l'écart-type entre blocs (les semaines) de $30$. Simulez 3 000 expériences et comparez la puissance (a) d'un plan **complètement randomisé** (12 unités issues de 12 blocs différents, 6 par traitement, analysées par un test de Student à deux échantillons) et (b) d'un plan **en blocs** (6 blocs, chacun contenant une unité de chaque traitement, analysé par un test de Student apparié).

### Exercice 8.13 ⭐⭐ — Méthode de Lenth (section 8.3 du livre)

Un plan $2^3$ non répliqué donne les sept effets $12{,}0\ ;\ -1{,}0\ ;\ 0{,}5\ ;\ 8{,}0\ ;\ -0{,}8\ ;\ 0{,}4\ ;\ 0{,}6$. Calculez $s_0$ et le PSE de Lenth, et dites quels effets sont actifs (marge d'erreur $ME=t_{0{,}975;\,7/3}\times\text{PSE}$).

## Corrigés

### Corrigé 8.1

(a) L'unité expérimentale est **la semaine** (tous les visiteurs d'une même semaine voient le même affichage) : elle n'a ici que **deux unités**, une par traitement. (b) D'abord, l'affichage est **confondu avec la semaine** : si la semaine 1 contient une fête ou une promotion, on attribuera à A ce qui vient de la période ; ensuite, il n'y a **aucune répétition** : on ne peut pas estimer le bruit entre semaines, donc aucun test n'est possible. (c) Plan en **blocs** : prendre par exemple 8 semaines ; **dans chaque semaine** (le bloc), afficher A trois ou quatre jours et B les autres, avec un **tirage au sort** des jours ; si l'on peut, afficher A et B en même temps à des visiteurs tirés au hasard (l'unité devient alors le visiteur, plus fine, et la répétition immédiate). On compare A et B **à l'intérieur de chaque semaine** (test apparié), ce qui élimine l'effet de semaine, et on dispose de plusieurs répétitions pour estimer le bruit.

### Corrigé 8.2

Moyennes : $50$, $56$, $62$ ; moyenne générale $56$. $SS_B=4\left[(50-56)^2+0+(62-56)^2\right]=4\times72=288$. Dans chaque groupe, la somme des carrés des écarts vaut $4+4+0+0=8$ (groupe 1), $0+4+4+0=8$ (groupe 2), $0+4+4+0=8$ (groupe 3) : $SS_W=24$. Degrés de liberté : $k-1=2$ et $N-k=12-3=9$. $MS_B=144$, $MS_W=24/9\approx2{,}667$ et $F=144/2{,}667=54$. C'est très au-dessus du seuil de la loi $\mathcal F(2,9)$ (4,26 à 5 %, et $p\approx10^{-5}$) : les fournisseurs diffèrent nettement.

```python
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.formula.api as smf
from statsmodels.stats.anova import anova_lm

dat = {"F1": [52, 48, 50, 50], "F2": [56, 58, 54, 56], "F3": [62, 60, 64, 62]}
y = np.array(list(dat.values()), dtype=float)
k, n = y.shape
mg = y.mean()
SSB = n * ((y.mean(axis=1) - mg) ** 2).sum()
SSW = ((y - y.mean(axis=1, keepdims=True)) ** 2).sum()
MSB, MSW = SSB / (k - 1), SSW / (k * n - k)
print("moyennes :", y.mean(axis=1), "; moyenne générale :", mg)
print(f"SSB = {SSB:.0f}, SSW = {SSW:.0f}, MSB = {MSB:.0f}, MSW = {MSW:.3f}, F = {MSB / MSW:.1f}")
print(f"seuil F(2, 9) à 5 % = {stats.f.ppf(0.95, k - 1, k * n - k):.2f} ; p = {stats.f.sf(MSB / MSW, k - 1, k * n - k):.1e}")
```
<!--sortie-->
```text
moyennes : [50. 56. 62.] ; moyenne générale : 56.0
SSB = 288, SSW = 24, MSB = 144, MSW = 2.667, F = 54.0
seuil F(2, 9) à 5 % = 4.26 ; p = 9.7e-06
```

### Corrigé 8.3

$\eta^2=SS_B/SS_T=288/312\approx0{,}923$ : le fournisseur explique 92 % de la variance. $\omega^2=(SS_B-(k-1)MS_W)/(SS_T+MS_W)=(288-2\times2{,}667)/(312+2{,}667)\approx0{,}898$. $\omega^2<\eta^2$ parce que $\eta^2$ attribue au facteur une part du **bruit d'échantillonnage** (même sans effet réel, $SS_B>0$ en général) ; $\omega^2$ retranche cette part attendue, $(k-1)MS_W$, et est donc moins optimiste.

```python
SST = SSB + SSW
print(f"eta² = {SSB / SST:.4f} ; omega² = {(SSB - (k - 1) * MSW) / (SST + MSW):.4f}")
long = pd.DataFrame({"fournisseur": np.repeat(list(dat), n), "resistance": y.ravel()})
mod = smf.ols("resistance ~ fournisseur", data=long).fit()          # (la colonne de texte est traitée comme un facteur)
print(f"régression : F = {mod.fvalue:.1f}, R² = {mod.rsquared:.4f} (= eta²)")
```
<!--sortie-->
```text
eta² = 0.9231 ; omega² = 0.8983
régression : F = 54.0, R² = 0.9231 (= eta²)
```

### Corrigé 8.4

$MS_W=2{,}667$, $n=4$ : $\sqrt{MS_W/n}=\sqrt{0{,}667}\approx0{,}816$, donc $\text{HSD}=3{,}95\times0{,}816\approx3{,}22$ N. Les écarts de moyennes sont $|56-50|=6$, $|62-56|=6$ et $|62-50|=12$, tous supérieurs à 3,22 : **les trois fournisseurs diffèrent deux à deux**, le troisième étant le plus résistant. Trois tests de Student à 5 % donneraient un risque global de fausse alerte proche de $1-0{,}95^3\approx14\,\%$ ; Tukey contrôle ce risque à 5 % pour l'**ensemble** des comparaisons.

```python
from statsmodels.stats.multicomp import pairwise_tukeyhsd
q = stats.studentized_range.ppf(0.95, k, k * n - k)
print(f"q = {q:.3f} ; HSD = {q * np.sqrt(MSW / n):.2f}")
res = pairwise_tukeyhsd(long["resistance"], long["fournisseur"])
print(pd.DataFrame(res._results_table.data[1:], columns=res._results_table.data[0]).round(3).to_string(index=False))
```
<!--sortie-->
```text
q = 3.948 ; HSD = 3.22
group1 group2  meandiff  p-adj  lower  upper  reject
    F1     F2       6.0  0.002  2.776  9.224    True
    F1     F3      12.0  0.000  8.776 15.224    True
    F2     F3       6.0  0.002  2.776  9.224    True
```

### Corrigé 8.5

Moyennes des blocs : $13$, $23{,}5$, $33$ ; des traitements : $20{,}33$, $24$, $22{,}0$, $26{,}33$ ; moyenne générale $23{,}17$. (a) $SS_{\text{blocs}}=4\sum(\bar y_{j}-\bar y)^2$, $SS_{\text{trait}}=3\sum(\bar y_i-\bar y)^2$, et $SS_E$ par différence, avec $2$, $3$ et $(2)(3)=6$ degrés de liberté ; on obtient $SS_{\text{blocs}}\approx800{,}7$, $SS_{\text{trait}}\approx60{,}3$ et $SS_E\approx2{,}67$ (leur somme est la somme totale des carrés, vérifiez-le). (b) Avec les blocs : $F=\dfrac{60{,}3/3}{2{,}67/6}\approx45{,}3$, très significatif ($p=0{,}0002$). Sans les blocs, le résidu absorbe la variabilité entre semaines : $F=\dfrac{60{,}3/3}{(800{,}7+2{,}67)/8}\approx0{,}20$ ($p=0{,}89$), aucun effet visible. (c) Les semaines diffèrent énormément (13, 23,5, 33), alors que les traitements diffèrent peu : le facteur « semaine » domine, et sans le bloc, l'effet des traitements est invisible.

```python
Y = np.array([[10, 14, 12, 16], [20, 25, 22, 27], [31, 33, 32, 36]], dtype=float)     # lignes = blocs
b, t = Y.shape
mg = Y.mean()
SSbl = t * ((Y.mean(axis=1) - mg) ** 2).sum()
SStr = b * ((Y.mean(axis=0) - mg) ** 2).sum()
SSe = ((Y - Y.mean(axis=1, keepdims=True) - Y.mean(axis=0, keepdims=True) + mg) ** 2).sum()
print(f"SS blocs = {SSbl:.1f} (ddl {b - 1}) ; SS traitements = {SStr:.1f} (ddl {t - 1}) ; SS erreur = {SSe:.2f} (ddl {(b - 1) * (t - 1)})")
F_avec = (SStr / (t - 1)) / (SSe / ((b - 1) * (t - 1)))
F_sans = (SStr / (t - 1)) / ((SSbl + SSe) / (b * t - t))
print(f"F traitements avec blocs = {F_avec:.2f} (p = {stats.f.sf(F_avec, t - 1, (b - 1) * (t - 1)):.4f})")
print(f"F traitements sans blocs = {F_sans:.2f} (p = {stats.f.sf(F_sans, t - 1, b * t - t):.4f})")
```
<!--sortie-->
```text
SS blocs = 800.7 (ddl 2) ; SS traitements = 60.3 (ddl 3) ; SS erreur = 2.67 (ddl 6)
F traitements avec blocs = 45.25 (p = 0.0002)
F traitements sans blocs = 0.20 (p = 0.8933)
```

### Corrigé 8.6

$\text{effet}(A)=\frac{(30+15)-(20+25)}{2}=0$ ; $\text{effet}(B)=\frac{(25+15)-(20+30)}{2}=-5$ ; $\text{AB}=\frac{(15-25)-(30-20)}{2}=-10$. L'effet principal de A est nul **parce que deux effets de signes opposés se compensent** : A fait **monter** la réponse de $+10$ quand B est bas ($20\to30$) et la fait **baisser** de $10$ quand B est haut ($25\to15$). A a donc une influence majeure, mais elle **dépend** de B : c'est exactement le piège de l'interaction qui annule un effet principal. Le meilleur réglage est $(A+,B-)$ avec $30$.

```python
m = {("-", "-"): 20, ("+", "-"): 30, ("-", "+"): 25, ("+", "+"): 15}
eff_A = ((m[("+", "-")] + m[("+", "+")]) - (m[("-", "-")] + m[("-", "+")])) / 2
eff_B = ((m[("-", "+")] + m[("+", "+")]) - (m[("-", "-")] + m[("+", "-")])) / 2
Aeff_B = ((m[("+", "+")] - m[("-", "+")]) - (m[("+", "-")] - m[("-", "-")])) / 2
print("A =", eff_A, "; B =", eff_B, "; AB =", eff_AB, "; meilleur réglage :", max(m, key=m.get))
```
<!--sortie-->
```text
A = 0.0 ; B = -5.0 ; AB = -3.5 ; meilleur réglage : ('+', '-')
```

### Corrigé 8.7

Moyenne $=116/8=14{,}5$. Effets (contraste / 4) : $A=(14+20+15+21-10-12-11-13)/4=24/4=6$ ; $B=(12+20+13+21-10-14-11-15)/4=16/4=4$ ; $C=(11+15+13+21-10-14-12-20)/4=4/4=1$ ; $AB$ : signes $+$ pour $(1),ab,c,abc$ : $(10+20+11+21-14-12-15-13)/4=8/4=2$ ; $AC=BC=ABC=0$. Les effets non nuls sont donc A, B, C et AB, avec $A>B>AB>C$.

```python
def yates(y):
    col = np.array(y, float)
    for _ in range(int(np.log2(len(y)))):
        col = np.concatenate([col[0::2] + col[1::2], col[1::2] - col[0::2]])
    return col

y = [10, 14, 12, 20, 11, 15, 13, 21]
contr = yates(y)
noms = ["I", "A", "B", "AB", "C", "AC", "BC", "ABC"]
print({nom: float(v) for nom, v in zip(noms, np.round(np.r_[contr[0] / 8, contr[1:] / 4], 2))})
```
<!--sortie-->
```text
{'I': 14.5, 'A': 6.0, 'B': 4.0, 'AB': 2.0, 'C': 1.0, 'AC': 0.0, 'BC': 0.0, 'ABC': 0.0}
```

### Corrigé 8.8

(a) $N=8r$, donc l'écart-type d'un effet vaut $\text{ET}=2\sigma/\sqrt{8r}=6/\sqrt{8r}$. (b) Avec l'approximation normale, la puissance de 80 % exige $\Delta/\text{ET}\approx1{,}96+0{,}84=2{,}8$, soit $\text{ET}\le4/2{,}8=1{,}43$ et $8r\ge(6/1{,}43)^2\approx17{,}6$, donc $r\ge2{,}2$ : environ **3 répétitions**. (c) Avec la loi de Student, qui a peu de degrés de liberté quand $r$ est petit (8 pour $r=2$), il faut un peu plus de marge. Le calcul exact confirme ce qu'annonce l'approximation :

```python
sigma, delta = 3.0, 4.0
for r in (2, 3, 4):
    N = 8 * r
    ddl = N - 8
    se = 2 * sigma / np.sqrt(N)
    seuil = stats.t.ppf(0.975, ddl)
    puissance = stats.nct.sf(seuil, ddl, delta / se) + stats.nct.cdf(-seuil, ddl, delta / se)
    print(f"r = {r} : N = {N}, ET = {se:.3f}, ddl = {ddl}, puissance = {puissance:.3f}")
```
<!--sortie-->
```text
r = 2 : N = 16, ET = 1.500, ddl = 8, puissance = 0.648
r = 3 : N = 24, ET = 1.225, ddl = 16, puissance = 0.865
r = 4 : N = 32, ET = 1.061, ddl = 24, puissance = 0.951
```

La puissance est de $65\,\%$ pour $r=2$, de $86{,}5\,\%$ pour $r=3$ et de $95\,\%$ pour $r=4$ : le seuil de 80 % est atteint à partir de $r=3$ (24 essais), comme l'annonçait l'approximation normale. La loi de Student, qui tient compte du petit nombre de degrés de liberté de l'erreur pure, rend le calcul exact un peu plus exigeant pour les petites valeurs de $r$.

### Corrigé 8.9

(a) $D=ABC\Rightarrow I=ABCD$. Un seul mot de 4 lettres : **résolution IV**. $AB=AB\cdot ABCD=CD$. (b) $D=AB\Rightarrow I=ABD$ (mot de 3 lettres) : **résolution III** ; $AB=AB\cdot ABD=D$ : l'interaction AB est confondue avec le **facteur principal D**, ce qui est le pire cas ; de plus, $A=BD$, $B=AD$. (c) Le premier : à nombre d'essais égal, la résolution IV garantit que les effets principaux ne sont confondus qu'avec des interactions d'ordre 3 ; la résolution III les confond avec des interactions d'ordre 2, souvent non négligeables.

```python
def produit(u, v):
    return "".join(sorted(set(u) ^ set(v)))
for gen, mots in [("D = ABC", ["ABCD"]), ("D = AB", ["ABD"])]:
    print(f"{gen} : I = {' = '.join(mots)} ; résolution {min(len(w) for w in mots)} ; "
          f"AB = {' = '.join(produit('AB', w) for w in mots)} ; A = {' = '.join(produit('A', w) for w in mots)}")
```
<!--sortie-->
```text
D = ABC : I = ABCD ; résolution 4 ; AB = CD ; A = BCD
D = AB : I = ABD ; résolution 3 ; AB = D ; A = BD
```

### Corrigé 8.10

(a) Les mots générateurs : $E=ABC\Rightarrow I=ABCE$ ; $F=BCD\Rightarrow I=BCDF$. Leur produit est aussi un mot : $ABCE\cdot BCDF=A\,D\,E\,F$ (les lettres B et C, communes, s'éliminent). Relation complète : $I=ABCE=BCDF=ADEF$. (b) Mots de longueurs 4, 4 et 4 : **résolution IV**. (c) $A=A\cdot ABCE=BCE$ ; $A\cdot BCDF=ABCDF$ ; $A\cdot ADEF=DEF$ : $A=BCE=ABCDF=DEF$ (effets d'ordre 3 ou plus : **A est propre**). $AB=CE=ACDF=BDEF$. (d) Non : $AB$ est confondue avec $CE$ (elle l'est par le mot $ABCE$) : en résolution IV, certaines interactions d'ordre 2 sont confondues entre elles ; pour les séparer, il faudrait un plan de résolution V (plus d'essais) ou un repliement bien choisi.

```python
mots = ["ABCE", "BCDF", produit("ABCE", "BCDF")]
print("relation de définition : I = " + " = ".join(mots))
for e in ["A", "AB"]:
    print(f"{e} = " + " = ".join(produit(e, w) for w in mots))
```
<!--sortie-->
```text
relation de définition : I = ABCE = BCDF = ADEF
A = BCE = ABCDF = DEF
AB = CE = ACDF = BDEF
```

### Corrigé 8.11

(a) $b=(4,2)^\top$, $B=\begin{pmatrix}-3&0{,}5\\0{,}5&-1\end{pmatrix}$ (le terme croisé $1\cdot x_1x_2$ se répartit en $0{,}5+0{,}5$). $\det B=3-0{,}25=2{,}75$ et $B^{-1}=\frac1{2{,}75}\begin{pmatrix}-1&-0{,}5\\-0{,}5&-3\end{pmatrix}$, donc $B^{-1}b=\frac1{2{,}75}(-5,-8)^\top$ et $x_s=-\tfrac12B^{-1}b\approx(0{,}909;\ 1{,}455)$. La réponse prédite est $\hat y_s=70+\tfrac12b^\top x_s=70+\tfrac12(4\times0{,}909+2\times1{,}455)\approx73{,}27$. (b) La trace de $B$ vaut $-4$ et son déterminant $2{,}75>0$ : les valeurs propres sont $\frac{-4\pm\sqrt{16-11}}{2}\approx-0{,}88$ et $-3{,}12$, **toutes deux négatives** : c'est un **maximum**. (c) La distance au centre est $\sqrt{0{,}909^2+1{,}455^2}\approx1{,}72$, **supérieure** au rayon $\sqrt2\approx1{,}41$ des points axiaux : le sommet est **en dehors du domaine expérimental**. C'est une extrapolation : on ne doit pas lui faire confiance, mais déplacer le plan dans cette direction et recommencer.

```python
b2 = np.array([4.0, 2.0])
B2 = np.array([[-3.0, 0.5], [0.5, -1.0]])
xs = -0.5 * np.linalg.solve(B2, b2)
print("point stationnaire :", xs.round(3), "; réponse :", round(70 + 0.5 * b2 @ xs, 2))
print("valeurs propres de B :", np.linalg.eigvalsh(B2).round(2))
print(f"distance au centre = {np.linalg.norm(xs):.2f} ; rayon du domaine (points axiaux) = {np.sqrt(2):.2f}")
```
<!--sortie-->
```text
point stationnaire : [0.909 1.455] ; réponse : 73.27
valeurs propres de B : [-3.12 -0.88]
distance au centre = 1.72 ; rayon du domaine (points axiaux) = 1.41
```

### Corrigé 8.12

Dans un plan complètement randomisé, chaque unité vient d'un bloc différent : la variabilité entre blocs (écart-type 30) s'ajoute au bruit (10), soit un écart-type de $\sqrt{30^2+10^2}\approx31{,}6$ par unité. L'écart-type de la différence de deux moyennes de 6 unités vaut $31{,}6\sqrt{2/6}\approx18{,}3$, pour un effet de $15$ : le rapport signal/bruit est d'environ $0{,}8$ et le test est peu puissant. Dans le plan en blocs, la **différence** entre les deux traitements au sein d'un même bloc élimine l'effet de bloc : l'écart-type d'une différence est de $10\sqrt2\approx14{,}1$, celui de la moyenne des 6 différences $14{,}1/\sqrt6\approx5{,}8$, soit un rapport signal/bruit de $2{,}6$ : bien meilleur. La simulation le chiffre.

```python
rng = np.random.default_rng(90)
effet, sig, sig_bloc, n_par_trait, n_sim = 15.0, 10.0, 30.0, 6, 3000
rej_crd, rej_blocs = 0, 0
for _ in range(n_sim):
    # (a) plan complètement randomisé : 12 unités, chacune avec SON propre effet de bloc (indépendants)
    y1 = rng.normal(0, sig_bloc, n_par_trait) + rng.normal(0, sig, n_par_trait)
    y2 = effet + rng.normal(0, sig_bloc, n_par_trait) + rng.normal(0, sig, n_par_trait)
    rej_crd += stats.ttest_ind(y2, y1).pvalue < 0.05
    # (b) plan en blocs : 6 blocs, une unité de chaque traitement par bloc (l'effet de bloc est PARTAGÉ)
    blocs = rng.normal(0, sig_bloc, n_par_trait)
    z1 = blocs + rng.normal(0, sig, n_par_trait)
    z2 = blocs + effet + rng.normal(0, sig, n_par_trait)
    rej_blocs += stats.ttest_rel(z2, z1).pvalue < 0.05
print(f"puissance, plan complètement randomisé (Student, 6 contre 6) : {rej_crd / n_sim:.3f}")
print(f"puissance, plan en blocs (Student apparié, 6 blocs)           : {rej_blocs / n_sim:.3f}")
```
<!--sortie-->
```text
puissance, plan complètement randomisé (Student, 6 contre 6) : 0.112
puissance, plan en blocs (Student apparié, 6 blocs)           : 0.552
```

Les deux plans utilisent **le même nombre d'unités** (12) et le même effet, mais le plan en blocs le détecte dans environ 55 % des expériences, contre environ 11 % pour le plan complètement randomisé : un facteur 5 de puissance obtenu **sans une unité de plus**, simplement en organisant l'expérience. (Un piège à éviter : si l'on appliquait un test de Student à deux échantillons à des données **appariées par un bloc partagé**, on traiterait comme indépendantes des mesures corrélées ; le test deviendrait trop conservateur, avec une puissance inférieure même à son seuil de 5 %. C'est une erreur d'analyse, pas un plan complètement randomisé.)

### Corrigé 8.13

Valeurs absolues triées : $0{,}4;\ 0{,}5;\ 0{,}6;\ 0{,}8;\ 1{,}0;\ 8{,}0;\ 12{,}0$ ; médiane $=0{,}8$, donc $s_0=1{,}5\times0{,}8=1{,}2$ et le seuil $2{,}5\,s_0=3{,}0$. On ne garde que les $|c|<3$ : $0{,}4;\ 0{,}5;\ 0{,}6;\ 0{,}8;\ 1{,}0$, de médiane $0{,}6$ : $\text{PSE}=1{,}5\times0{,}6=0{,}9$. Avec $d=7/3\approx2{,}33$ degrés de liberté, $t_{0{,}975}\approx3{,}76$ (très grand, faute de degrés de liberté) : $ME\approx3{,}39$. Les effets $12$ et $8$ dépassent largement la marge ; les cinq autres n'en approchent pas : **deux effets actifs**.

```python
c = np.array([12.0, -1.0, 0.5, 8.0, -0.8, 0.4, 0.6])
a = np.abs(c)
s0 = 1.5 * np.median(a)
pse = 1.5 * np.median(a[a < 2.5 * s0])
d = len(c) / 3
ME = stats.t.ppf(0.975, d) * pse
print(f"s0 = {s0:.2f} ; PSE = {pse:.2f} ; d = {d:.2f} ; t = {stats.t.ppf(0.975, d):.2f} ; ME = {ME:.2f}")
print("effets actifs (|c| > ME) :", c[a > ME])
```
<!--sortie-->
```text
s0 = 1.20 ; PSE = 0.90 ; d = 2.33 ; t = 3.76 ; ME = 3.39
effets actifs (|c| > ME) : [12.  8.]
```
