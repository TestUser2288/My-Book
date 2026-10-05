## 3.4 Tests d'hypothèses

> 💡 **Intuition : le tribunal.** Un test d'hypothèses fonctionne comme un procès. On part de la **présomption d'innocence** (l'hypothèse « il ne se passe rien », appelée $H_0$). On examine les **preuves** (les données). Si les preuves sont **très improbables** dans un monde où l'accusé est innocent, on le **condamne** (on rejette $H_0$). Sinon, on **acquitte** : cela ne prouve pas son innocence, cela veut seulement dire que les preuves sont insuffisantes.

### 3.4.1 Le vocabulaire et la méthode

- **Hypothèse nulle $H_0$** : l'état de référence, « pas d'effet, pas de différence ». Par exemple : « le panier moyen vaut 55 € ».
- **Hypothèse alternative $H_1$** : ce que l'on cherche à montrer. « Le panier moyen est différent de 55 € » (test **bilatéral**), ou « supérieur à 55 € » (test **unilatéral**).
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

> 💡 **Question de la gérante.** Son objectif de panier moyen était de 55 €. Les 400 commandes confirment-elles que le panier moyen **diffère** de 55 € ?

1. $H_0:\mu=55$ ; $H_1:\mu\neq55$.
2. $\alpha=0{,}05$.
3. Statistique de test (la même construction qu'au 3.3.3, centrée sur la valeur de $H_0$) :

$$t=\frac{\bar x-\mu_0}{s/\sqrt n}=\frac{60{,}25-55}{38{,}02/\sqrt{400}}=\frac{5{,}25}{1{,}90}\approx2{,}76.$$

Sous $H_0$, $t$ suit une loi de Student à $n-1=399$ degrés de liberté. 4. La p-valeur est la probabilité qu'une telle loi donne une valeur **au moins aussi éloignée de 0** que 2,76, des deux côtés : $p=2\,P(T_{399}>2{,}76)$.

```python hide
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

Le calcul (`scipy.stats.ttest_1samp` le fait en une ligne) donne $t=2{,}76$ et $p=0{,}0061$, la valeur critique bilatérale à 5 % étant 1,966.

5. **Conclusion.** $p=0{,}006<0{,}05$ : on rejette $H_0$. Le panier moyen est significativement supérieur à 55 € (il est en fait de 60,25 ; l'IC à 95 % du 3.3.3 était [56,5 ; 64,0], qui n'inclut pas 55 : **un test bilatéral à 5 % et un IC à 95 % disent la même chose**).

![Statistique de test sous H₀. Gauche : la valeur observée (2,76) tombe dans la zone de rejet (queues orange, 5 % au total). Droite : une valeur de 1,10 tomberait dans la zone de non-rejet.](figures/ch03-test-rejet.png)

> ⚠️ **« Ne pas rejeter » n'est pas « accepter ».** Si $p$ avait été de 0,30, on aurait dit « les données ne permettent pas de conclure que $\mu\neq55$ », pas « $\mu=55$ ». L'absence de preuve n'est pas la preuve de l'absence. (Un petit échantillon peut échouer à détecter un grand effet : c'est le problème de la puissance.)

### 3.4.3 Comparer deux groupes : le test de Welch

> 💡 **Question de la gérante.** Les clients de la **boutique** dépensent-ils plus que ceux du canal **Réseaux** ? Les moyennes observées sont 74,8 et 49,0 €, soit un écart de 25,8 €. Cet écart est-il crédible ou dû au hasard ?

On teste $H_0:\mu_B=\mu_I$ contre $H_1:\mu_B\neq\mu_I$. On compare la différence des moyennes à son erreur-type. Comme les deux échantillons sont indépendants, les variances **s'additionnent** (2.3.3) :

$$t=\frac{\bar x_B-\bar x_I}{\sqrt{\dfrac{s_B^2}{n_B}+\dfrac{s_I^2}{n_I}}}.$$

C'est le **test de Welch**, qui n'exige pas que les deux groupes aient la même variance (c'est la version à utiliser par défaut ; l'ancien test de Student à variances égales est moins sûr). Ici, la différence des moyennes est 25,8 € et son erreur-type 4,64 €, d'où $t=25{,}8/4{,}64\approx5{,}565$. En pratique, une seule instruction de `scipy` fait le calcul :

```python hide
b = df.loc[df["canal"] == "Boutique", "montant"]
i = df.loc[df["canal"] == "Réseaux", "montant"]

diff = b.mean() - i.mean()
se_diff = np.sqrt(b.var(ddof=1) / len(b) + i.var(ddof=1) / len(i))
print("différence des moyennes :", round(diff, 2), "€")
print("erreur-type de la différence :", round(se_diff, 2))
print("t à la main :", round(diff / se_diff, 3))

res = stats.ttest_ind(b, i, equal_var=False)         # equal_var=False -> test de Welch
print("scipy (Welch) : t =", round(res.statistic, 3), "  p =", res.pvalue, "  ddl =", round(res.df, 1))
```
<!--sortie-->
```text
différence des moyennes : 25.8 €
erreur-type de la différence : 4.64
t à la main : 5.565
scipy (Welch) : t = 5.565   p = 8.016365853327231e-08   ddl = 208.4
```

```python
b = df.loc[df["canal"] == "Boutique", "montant"]
i = df.loc[df["canal"] == "Réseaux", "montant"]
res = stats.ttest_ind(b, i, equal_var=False)     # equal_var=False : test de Welch
print(round(res.statistic, 3), f"{res.pvalue:.1e}", round(res.df, 1))
```
<!--sortie-->
```text
5.565 8.0e-08 208.4
```

La statistique est $t\approx5{,}56$ et la p-valeur est de l'ordre de $10^{-7}$ : si les deux canaux avaient la même dépense moyenne, observer un écart aussi grand serait **quasi impossible**. On rejette $H_0$.

**Un test ne dit pas « de combien ».** Une p-valeur minuscule dit que l'effet est *réel*, pas qu'il est *grand*. Il faut toujours accompagner un test d'un **intervalle de confiance de la différence** et d'une **taille d'effet**. Ici, l'IC à 95 % de la différence est $[16{,}7\,;\,34{,}9]$ € et le $d$ de Cohen (écart divisé par l'écart-type commun) vaut 0,72.

```python hide
t_c = stats.t.ppf(0.975, res.df)
print(f"IC95 % de la différence : [{diff - t_c * se_diff:.1f} ; {diff + t_c * se_diff:.1f}] €")

s_pooled = np.sqrt(((len(b) - 1) * b.var(ddof=1) + (len(i) - 1) * i.var(ddof=1)) / (len(b) + len(i) - 2))
print("d de Cohen :", round(diff / s_pooled, 2))
```
<!--sortie-->
```text
IC95 % de la différence : [16.7 ; 34.9] €
d de Cohen : 0.72
```

Le client de la boutique dépense en moyenne entre 17 et 35 € de plus (IC à 95 %). Le **d de Cohen** (la différence en nombre d'écarts-types) vaut environ 0,7 : un effet « moyen à grand » selon les conventions usuelles (0,2 petit, 0,5 moyen, 0,8 grand).

> 🧪 **Et la distribution asymétrique ?** Le test de Student suppose des moyennes à peu près normales (ce que le TCL assure pour des groupes de plus d'une centaine d'observations) ; il reste correct ici. Pour de petits groupes très asymétriques, on teste plutôt $\log(\text{montant})$, ou on utilise un test non paramétrique (➕ 3.7). Sur l'échelle logarithmique, le test de Welch donne $t=6{,}46$ ($p\approx5\times10^{-10}$) : la conclusion tient.

```python hide
res_log = stats.ttest_ind(np.log(b), np.log(i), equal_var=False)
print("test sur log(montant) : t =", round(res_log.statistic, 2), "  p =", res_log.pvalue)
res_si = stats.ttest_ind(df.loc[df["canal"] == "Site", "montant"], i, equal_var=False)
print("Site contre Réseaux  : t =", round(res_si.statistic, 2), "  p =", round(res_si.pvalue, 4))
```
<!--sortie-->
```text
test sur log(montant) : t = 6.46   p = 5.400582683884821e-10
Site contre Réseaux  : t = 2.55   p = 0.0113
```

Même conclusion. Pour Site contre Réseaux, $p\approx0{,}011$ : l'écart (10,5 €) est aussi significatif au seuil de 5 %, mais bien moins fortement.

**Le test apparié.** Quand les deux séries concernent **les mêmes individus** (avant/après), on ne compare pas deux groupes indépendants : on calcule la **différence pour chaque individu** et on teste que sa moyenne est nulle. Exemple : 8 colis dont on a mesuré le délai avant (5, 4, 6, 7, 5, 6, 8, 5 jours) et après (4, 4, 5, 6, 5, 5, 6, 4 jours) un changement de transporteur. Les différences sont 1, 0, 1, 1, 0, 1, 2, 1 (moyenne 0,875) et le test apparié donne $t=3{,}86$, $p=0{,}0062$.

```python hide
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

Le nouveau transporteur fait gagner en moyenne 0,875 jour ($p\approx0{,}006$). Ignorer l'appariement (comme si les groupes étaient indépendants) donnerait un test beaucoup moins sensible, car on gaspillerait l'information que chaque colis est comparé à lui-même : le test non apparié donnerait ici $p=0{,}128$, non significatif, au lieu de 0,006.

```python hide
print("(à tort, test non apparié : p =", round(stats.ttest_ind(avant, apres).pvalue, 3), ")")
```
<!--sortie-->
```text
(à tort, test non apparié : p = 0.128 )
```

### 3.4.4 Test sur une proportion

> 💡 **Question de la gérante.** Historiquement, le taux de conversion était de 18 %. Sur les 1 000 dernières visites, 205 ont acheté (20,5 %). Y a-t-il une amélioration réelle ?

$H_0:p=0{,}18$ contre $H_1:p\neq0{,}18$. Sous $H_0$, l'erreur-type est $\sqrt{p_0(1-p_0)/n}$ (on utilise la valeur de $H_0$, pas l'estimation) et la statistique

$$z=\frac{\hat p-p_0}{\sqrt{p_0(1-p_0)/n}}=\frac{0{,}205-0{,}18}{\sqrt{0{,}18\times0{,}82/1000}}=\frac{0{,}025}{0{,}01215}\approx2{,}06.$$

On compare à la loi normale (TCL). Il existe aussi un test **exact** basé sur la loi binomiale, sans approximation. Le calcul donne $z=2{,}058$ et $p=0{,}0396$ avec l'approximation normale, $p=0{,}0436$ avec le test exact.

```python hide
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

C'est le test le plus utilisé en pratique dans le web et le marketing. La gérante essaie deux versions de sa page produit. La version A (1 000 visiteurs) donne 120 achats (12 %), la version B (1 000 visiteurs) donne 150 achats (15 %). B est-elle meilleure ?

$H_0:p_A=p_B$. Sous $H_0$, les deux groupes ont le même taux, estimé en **regroupant** les données : $\hat p=\frac{120+150}{2000}=0{,}135$. L'erreur-type de la différence est $\sqrt{\hat p(1-\hat p)\bigl(\frac1{n_A}+\frac1{n_B}\bigr)}$ et

$$z=\frac{\hat p_B-\hat p_A}{\sqrt{\hat p(1-\hat p)\bigl(\frac1{n_A}+\frac1{n_B}\bigr)}}=\frac{0{,}03}{0{,}01528}\approx1{,}96,\qquad p=0{,}0496.$$

L'intervalle de confiance de la différence, calculé avec l'erreur-type non regroupée, est $[0{,}0001\,;\,0{,}0599]$.

```python hide
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

> 💡 **Question de la gérante.** La proportion de clients **satisfaits** (note ≥ 4) dépend-elle du canal de vente ?

On range les données dans un **tableau de contingence** (effectifs par canal et par satisfaction) :

```python hide
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
Réseaux       51     87
Site          45    103

satisfait  False  True 
canal                  
Boutique   0.044  0.956
Réseaux    0.370  0.630
Site       0.304  0.696
```

```python
df["satisfait"] = df["satisfaction"] >= 4
tableau = pd.crosstab(df["canal"], df["satisfait"])
print(tableau)
```
<!--sortie-->
```text
satisfait  False  True 
canal                  
Boutique       5    109
Réseaux       51     87
Site          45    103
```

$H_0$ : le canal et la satisfaction sont **indépendants**. Si c'était vrai, la proportion de satisfaits serait la même dans chaque canal (et égale à la proportion globale). On calcule alors, pour chaque case, l'**effectif attendu sous $H_0$** :

$$E_{ij}=\frac{(\text{total de la ligne }i)\times(\text{total de la colonne }j)}{\text{total général}}.$$

La statistique du khi-deux mesure l'écart entre effectifs observés ($O_{ij}$) et attendus :

$$\chi^2=\sum_{i,j}\frac{(O_{ij}-E_{ij})^2}{E_{ij}}.$$

Sous $H_0$, elle suit une loi du khi-deux à $(\text{lignes}-1)(\text{colonnes}-1)$ degrés de liberté. Plus les écarts sont grands, plus $\chi^2$ est grand.

```python hide
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
Réseaux     34.8  103.2
Site        37.4  110.6

khi-deux = 38.40   ddl = 2   p-valeur = 4.60e-09
V de Cramér : 0.31
```

```python
from scipy.stats import chi2_contingency

chi2, p, ddl, attendus = chi2_contingency(tableau)
print(round(chi2, 2), ddl, f"{p:.1e}")
```
<!--sortie-->
```text
38.4 2 4.6e-09
```

Les proportions de satisfaits sont de 95,6 % en boutique, 63,0 % sur Réseaux et 69,6 % sur le site. Dans la boutique, il y a **109 satisfaits sur 114** (96 %), alors que l'on en attendrait environ 85 si le canal n'avait aucun effet (soit 24 de plus) ; sur Réseaux, 63 % seulement (87 sur 138). La statistique est $\chi^2\approx38$ pour 2 degrés de liberté : $p\approx5\times10^{-9}$. On rejette l'indépendance. Le **V de Cramér** (0 = indépendance, 1 = lien parfait) vaut 0,31 : un lien d'intensité moyenne. (Attention : la boutique n'a pas de délai de livraison, ce qui explique sans doute en grande partie l'écart ; l'association n'est pas une causalité.)

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
>
> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.4, exercices 3.6 à 3.8.
