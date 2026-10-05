## 8.5 Exercices du chapitre 8

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 2 à 4 se font avec les mêmes trois groupes ; 7, 9 et 10 se font entièrement à la main.

### Énoncés

**Exercice 1 ⭐ (concevoir une expérience).** Yasmine veut comparer deux présentations de la page d'accueil de son site, A et B. Elle propose : « affichage A la semaine prochaine, affichage B la semaine suivante, et je compare les commandes ». (a) Quelle est l'unité expérimentale ? (b) Citez deux raisons pour lesquelles la comparaison sera biaisée. (c) Proposez un plan qui applique les trois principes de Fisher (randomisation, répétition, blocage).

**Exercice 2 ⭐ (ANOVA à la main).** Trois fournisseurs de papier d'emballage, quatre lots chacun ; on mesure la résistance à la déchirure (en newtons) :
Fournisseur 1 : $52,\,48,\,50,\,50$ ; Fournisseur 2 : $56,\,58,\,54,\,56$ ; Fournisseur 3 : $62,\,60,\,64,\,62$.
Calculez les moyennes, $SS_B$, $SS_W$, les carrés moyens et la statistique $F$. Combien de degrés de liberté ? Que conclure ?

**Exercice 3 ⭐⭐ (taille d'effet).** Avec les données de l'exercice 2, calculez $\eta^2$ et $\omega^2$. Pourquoi $\omega^2<\eta^2$ ? Vérifiez ensuite que la régression sur indicatrices redonne le même $F$ et le même $R^2$.

**Exercice 4 ⭐⭐ (comparaisons multiples).** Toujours avec les données de l'exercice 2, calculez le seuil HSD de Tukey (utilisez $q_{0{,}95;\,3,\,9}\approx3{,}95$) et dites quelles paires de fournisseurs diffèrent. Pourquoi ne pas simplement faire trois tests de Student à 5 % ?

**Exercice 5 ⭐⭐ (blocs).** Quatre traitements sont testés dans trois blocs (trois semaines) ; ventes en dizaines de DT :

| | traitement 1 | traitement 2 | traitement 3 | traitement 4 |
|---|---|---|---|---|
| semaine 1 | 10 | 14 | 12 | 16 |
| semaine 2 | 20 | 25 | 22 | 27 |
| semaine 3 | 31 | 33 | 32 | 36 |

(a) Calculez $SS_{\text{blocs}}$, $SS_{\text{traitements}}$, $SS_E$ et leurs degrés de liberté. (b) Comparez le $F$ des traitements avec et sans les blocs. (c) Que s'est-il passé ?

**Exercice 6 ⭐⭐ (interaction).** On teste deux facteurs, A et B, à deux niveaux ; les moyennes de réponse sont $\bar y_{A-B-}=20$, $\bar y_{A+B-}=30$, $\bar y_{A-B+}=25$, $\bar y_{A+B+}=15$. Calculez l'effet principal de A, celui de B et l'interaction AB. L'effet principal de A est nul : A n'a-t-il donc aucune influence ? Quel est le meilleur réglage ?

**Exercice 7 ⭐⭐ (algorithme de Yates).** Plan $2^3$ sans répétition, essais en ordre standard : $(1)=10$, $a=14$, $b=12$, $ab=20$, $c=11$, $ac=15$, $bc=13$, $abc=21$. Calculez les sept effets et la moyenne par l'algorithme de Yates, puis par les contrastes. Quels effets sont non nuls ?

**Exercice 8 ⭐⭐⭐ (puissance d'un plan factoriel).** Dans un plan $2^3$ répliqué $r$ fois, l'écart-type du bruit est $\sigma=3$. On veut détecter un effet de $\Delta=4$ avec une puissance d'au moins 80 %, au seuil de 5 %. (a) Donnez l'écart-type d'un effet en fonction de $r$. (b) Estimez à la main un ordre de grandeur de $r$ avec l'approximation normale. (c) Calculez la valeur exacte avec la loi de Student non centrale.

**Exercice 9 ⭐⭐ (confusion).** On veut un plan $2^{4-1}$ (8 essais, 4 facteurs). (a) Avec le générateur $D=ABC$, donnez la relation de définition, la résolution et les alias de $AB$. (b) Avec $D=AB$, mêmes questions. (c) Lequel choisir et pourquoi ?

**Exercice 10 ⭐⭐⭐ (un plan $2^{6-2}$).** On construit 6 facteurs en 16 essais avec les générateurs $E=ABC$ et $F=BCD$. (a) Donnez la relation de définition complète. (b) Quelle est la résolution ? (c) Donnez les alias de $A$ et de $AB$. (d) Peut-on séparer les interactions $AB$ et $CE$ ?

**Exercice 11 ⭐⭐ (surface de réponse).** Un modèle du second ordre ajusté sur un plan composite centré à 2 facteurs ($\alpha=\sqrt2$) est $\hat y=70+4x_1+2x_2-3x_1^2-x_2^2+x_1x_2$. (a) Trouvez le point stationnaire et la réponse prédite. (b) Est-ce un maximum ? (c) Peut-on faire confiance à ce point ?

**Exercice 12 ⭐⭐⭐ (simuler l'effet des blocs).** On compare deux traitements avec 12 unités. L'effet vrai du traitement est de $+15$, l'écart-type du bruit de $10$ et l'écart-type entre blocs (les semaines) de $30$. Simulez 3 000 expériences et comparez la puissance (a) d'un plan **complètement randomisé** (12 unités issues de 12 blocs différents, 6 par traitement, analysées par un test de Student à deux échantillons) et (b) d'un plan **en blocs** (6 blocs, chacun contenant une unité de chaque traitement, analysé par un test de Student apparié).

**Exercice 13 ⭐⭐ (méthode de Lenth).** Un plan $2^3$ non répliqué donne les sept effets $12{,}0\ ;\ -1{,}0\ ;\ 0{,}5\ ;\ 8{,}0\ ;\ -0{,}8\ ;\ 0{,}4\ ;\ 0{,}6$. Calculez $s_0$ et le PSE de Lenth, et dites quels effets sont actifs (marge d'erreur $ME=t_{0{,}975;\,7/3}\times\text{PSE}$).

### Corrigés

**Corrigé 1.** (a) L'unité expérimentale est **la semaine** (tous les visiteurs d'une même semaine voient le même affichage) : elle n'a ici que **deux unités**, une par traitement. (b) D'abord, l'affichage est **confondu avec la semaine** : si la semaine 1 contient une fête ou une promotion, on attribuera à A ce qui vient de la période ; ensuite, il n'y a **aucune répétition** : on ne peut pas estimer le bruit entre semaines, donc aucun test n'est possible. (c) Plan en **blocs** : prendre par exemple 8 semaines ; **dans chaque semaine** (le bloc), afficher A trois ou quatre jours et B les autres, avec un **tirage au sort** des jours ; si l'on peut, afficher A et B en même temps à des visiteurs tirés au hasard (l'unité devient alors le visiteur, plus fine, et la répétition immédiate). On compare A et B **à l'intérieur de chaque semaine** (test apparié), ce qui élimine l'effet de semaine, et on dispose de plusieurs répétitions pour estimer le bruit.

**Corrigé 2.** Moyennes : $50$, $56$, $62$ ; moyenne générale $56$. $SS_B=4\left[(50-56)^2+0+(62-56)^2\right]=4\times72=288$. Dans chaque groupe, la somme des carrés des écarts vaut $4+4+0+0=8$ (groupe 1), $0+4+4+0=8$ (groupe 2), $0+4+4+0=8$ (groupe 3) : $SS_W=24$. Degrés de liberté : $k-1=2$ et $N-k=12-3=9$. $MS_B=144$, $MS_W=24/9\approx2{,}667$ et $F=144/2{,}667=54$. C'est très au-dessus du seuil de la loi $\mathcal F(2,9)$ (4,26 à 5 %, et $p\approx10^{-5}$) : les fournisseurs diffèrent nettement.

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

**Corrigé 3.** $\eta^2=SS_B/SS_T=288/312\approx0{,}923$ : le fournisseur explique 92 % de la variance. $\omega^2=(SS_B-(k-1)MS_W)/(SS_T+MS_W)=(288-2\times2{,}667)/(312+2{,}667)\approx0{,}898$. $\omega^2<\eta^2$ parce que $\eta^2$ attribue au facteur une part du **bruit d'échantillonnage** (même sans effet réel, $SS_B>0$ en général) ; $\omega^2$ retranche cette part attendue, $(k-1)MS_W$, et est donc moins optimiste.

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

**Corrigé 4.** $MS_W=2{,}667$, $n=4$ : $\sqrt{MS_W/n}=\sqrt{0{,}667}\approx0{,}816$, donc $\text{HSD}=3{,}95\times0{,}816\approx3{,}22$ N. Les écarts de moyennes sont $|56-50|=6$, $|62-56|=6$ et $|62-50|=12$, tous supérieurs à 3,22 : **les trois fournisseurs diffèrent deux à deux**, le troisième étant le plus résistant. Trois tests de Student à 5 % donneraient un risque global de fausse alerte proche de $1-0{,}95^3\approx14\,\%$ ; Tukey contrôle ce risque à 5 % pour l'**ensemble** des comparaisons.

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

**Corrigé 5.** Moyennes des blocs : $13$, $23{,}5$, $33$ ; des traitements : $20{,}33$, $24$, $22{,}0$, $26{,}33$ ; moyenne générale $23{,}17$. (a) $SS_{\text{blocs}}=4\sum(\bar y_{j}-\bar y)^2$, $SS_{\text{trait}}=3\sum(\bar y_i-\bar y)^2$, et $SS_E$ par différence, avec $2$, $3$ et $(2)(3)=6$ degrés de liberté ; on obtient $SS_{\text{blocs}}\approx800{,}7$, $SS_{\text{trait}}\approx60{,}3$ et $SS_E\approx2{,}67$ (leur somme est la somme totale des carrés, vérifiez-le). (b) Avec les blocs : $F=\dfrac{60{,}3/3}{2{,}67/6}\approx45{,}3$, très significatif ($p=0{,}0002$). Sans les blocs, le résidu absorbe la variabilité entre semaines : $F=\dfrac{60{,}3/3}{(800{,}7+2{,}67)/8}\approx0{,}20$ ($p=0{,}89$), aucun effet visible. (c) Les semaines diffèrent énormément (13, 23,5, 33), alors que les traitements diffèrent peu : le facteur « semaine » domine, et sans le bloc, l'effet des traitements est invisible.

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

**Corrigé 6.** $\text{effet}(A)=\frac{(30+15)-(20+25)}{2}=0$ ; $\text{effet}(B)=\frac{(25+15)-(20+30)}{2}=-5$ ; $\text{AB}=\frac{(15-25)-(30-20)}{2}=-10$. L'effet principal de A est nul **parce que deux effets de signes opposés se compensent** : A fait **monter** la réponse de $+10$ quand B est bas ($20\to30$) et la fait **baisser** de $10$ quand B est haut ($25\to15$). A a donc une influence majeure, mais elle **dépend** de B : c'est exactement le piège de l'interaction qui annule un effet principal. Le meilleur réglage est $(A+,B-)$ avec $30$.

```python
m = {("-", "-"): 20, ("+", "-"): 30, ("-", "+"): 25, ("+", "+"): 15}
A = ((m[("+", "-")] + m[("+", "+")]) - (m[("-", "-")] + m[("-", "+")])) / 2
B = ((m[("-", "+")] + m[("+", "+")]) - (m[("-", "-")] + m[("+", "-")])) / 2
AB = ((m[("+", "+")] - m[("-", "+")]) - (m[("+", "-")] - m[("-", "-")])) / 2
print("A =", A, "; B =", B, "; AB =", AB, "; meilleur réglage :", max(m, key=m.get))
```
<!--sortie-->
```text
A = 0.0 ; B = -5.0 ; AB = -10.0 ; meilleur réglage : ('+', '-')
```

**Corrigé 7.** Moyenne $=116/8=14{,}5$. Effets (contraste / 4) : $A=(14+20+15+21-10-12-11-13)/4=24/4=6$ ; $B=(12+20+13+21-10-14-11-15)/4=16/4=4$ ; $C=(11+15+13+21-10-14-12-20)/4=4/4=1$ ; $AB$ : signes $+$ pour $(1),ab,c,abc$ : $(10+20+11+21-14-12-15-13)/4=8/4=2$ ; $AC=BC=ABC=0$. Les effets non nuls sont donc A, B, C et AB, avec $A>B>AB>C$.

```python
def yates(y):
    col = np.array(y, float)
    for _ in range(int(np.log2(len(y)))):
        col = np.concatenate([col[0::2] + col[1::2], col[1::2] - col[0::2]])
    return col

y = [10, 14, 12, 20, 11, 15, 13, 21]
contr = yates(y)
noms = ["I", "A", "B", "AB", "C", "AC", "BC", "ABC"]
print(dict(zip(noms, np.round(np.r_[contr[0] / 8, contr[1:] / 4], 2))))
```
<!--sortie-->
```text
{'I': np.float64(14.5), 'A': np.float64(6.0), 'B': np.float64(4.0), 'AB': np.float64(2.0), 'C': np.float64(1.0), 'AC': np.float64(0.0), 'BC': np.float64(0.0), 'ABC': np.float64(0.0)}
```

**Corrigé 8.** (a) $N=8r$, donc l'écart-type d'un effet vaut $\text{ET}=2\sigma/\sqrt{8r}=6/\sqrt{8r}$. (b) Avec l'approximation normale, la puissance de 80 % exige $\Delta/\text{ET}\approx1{,}96+0{,}84=2{,}8$, soit $\text{ET}\le4/2{,}8=1{,}43$ et $8r\ge(6/1{,}43)^2\approx17{,}6$, donc $r\ge2{,}2$ : environ **3 répétitions**. (c) Avec la loi de Student, qui a peu de degrés de liberté quand $r$ est petit (8 pour $r=2$), il faut un peu plus de marge. Le calcul exact confirme ce qu'annonce l'approximation :

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

**Corrigé 9.** (a) $D=ABC\Rightarrow I=ABCD$. Un seul mot de 4 lettres : **résolution IV**. $AB=AB\cdot ABCD=CD$. (b) $D=AB\Rightarrow I=ABD$ (mot de 3 lettres) : **résolution III** ; $AB=AB\cdot ABD=D$ : l'interaction AB est confondue avec le **facteur principal D**, ce qui est le pire cas ; de plus, $A=BD$, $B=AD$. (c) Le premier : à nombre d'essais égal, la résolution IV garantit que les effets principaux ne sont confondus qu'avec des interactions d'ordre 3 ; la résolution III les confond avec des interactions d'ordre 2, souvent non négligeables.

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

**Corrigé 10.** (a) Les mots générateurs : $E=ABC\Rightarrow I=ABCE$ ; $F=BCD\Rightarrow I=BCDF$. Leur produit est aussi un mot : $ABCE\cdot BCDF=A\,D\,E\,F$ (les lettres B et C, communes, s'éliminent). Relation complète : $I=ABCE=BCDF=ADEF$. (b) Mots de longueurs 4, 4 et 4 : **résolution IV**. (c) $A=A\cdot ABCE=BCE$ ; $A\cdot BCDF=ABCDF$ ; $A\cdot ADEF=DEF$ : $A=BCE=ABCDF=DEF$ (effets d'ordre 3 ou plus : **A est propre**). $AB=CE=ACDF=BDEF$. (d) Non : $AB$ est confondue avec $CE$ (elle l'est par le mot $ABCE$) : en résolution IV, certaines interactions d'ordre 2 sont confondues entre elles ; pour les séparer, il faudrait un plan de résolution V (plus d'essais) ou un repliement bien choisi.

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

**Corrigé 11.** (a) $b=(4,2)^\top$, $B=\begin{pmatrix}-3&0{,}5\\0{,}5&-1\end{pmatrix}$ (le terme croisé $1\cdot x_1x_2$ se répartit en $0{,}5+0{,}5$). $\det B=3-0{,}25=2{,}75$ et $B^{-1}=\frac1{2{,}75}\begin{pmatrix}-1&-0{,}5\\-0{,}5&-3\end{pmatrix}$, donc $B^{-1}b=\frac1{2{,}75}(-5,-8)^\top$ et $x_s=-\tfrac12B^{-1}b\approx(0{,}909;\ 1{,}455)$. La réponse prédite est $\hat y_s=70+\tfrac12b^\top x_s=70+\tfrac12(4\times0{,}909+2\times1{,}455)\approx73{,}27$. (b) La trace de $B$ vaut $-4$ et son déterminant $2{,}75>0$ : les valeurs propres sont $\frac{-4\pm\sqrt{16-11}}{2}\approx-0{,}88$ et $-3{,}12$, **toutes deux négatives** : c'est un **maximum**. (c) La distance au centre est $\sqrt{0{,}909^2+1{,}455^2}\approx1{,}72$, **supérieure** au rayon $\sqrt2\approx1{,}41$ des points axiaux : le sommet est **en dehors du domaine expérimental**. C'est une extrapolation : on ne doit pas lui faire confiance, mais déplacer le plan dans cette direction et recommencer.

```python
b = np.array([4.0, 2.0])
B = np.array([[-3.0, 0.5], [0.5, -1.0]])
xs = -0.5 * np.linalg.solve(B, b)
print("point stationnaire :", xs.round(3), "; réponse :", round(70 + 0.5 * b @ xs, 2))
print("valeurs propres de B :", np.linalg.eigvalsh(B).round(2))
print(f"distance au centre = {np.linalg.norm(xs):.2f} ; rayon du domaine (points axiaux) = {np.sqrt(2):.2f}")
```
<!--sortie-->
```text
point stationnaire : [0.909 1.455] ; réponse : 73.27
valeurs propres de B : [-3.12 -0.88]
distance au centre = 1.72 ; rayon du domaine (points axiaux) = 1.41
```

**Corrigé 12.** Dans un plan complètement randomisé, chaque unité vient d'un bloc différent : la variabilité entre blocs (écart-type 30) s'ajoute au bruit (10), soit un écart-type de $\sqrt{30^2+10^2}\approx31{,}6$ par unité. L'écart-type de la différence de deux moyennes de 6 unités vaut $31{,}6\sqrt{2/6}\approx18{,}3$, pour un effet de $15$ : le rapport signal/bruit est d'environ $0{,}8$ et le test est peu puissant. Dans le plan en blocs, la **différence** entre les deux traitements au sein d'un même bloc élimine l'effet de bloc : l'écart-type d'une différence est de $10\sqrt2\approx14{,}1$, celui de la moyenne des 6 différences $14{,}1/\sqrt6\approx5{,}8$, soit un rapport signal/bruit de $2{,}6$ : bien meilleur. La simulation le chiffre.

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

**Corrigé 13.** Valeurs absolues triées : $0{,}4;\ 0{,}5;\ 0{,}6;\ 0{,}8;\ 1{,}0;\ 8{,}0;\ 12{,}0$ ; médiane $=0{,}8$, donc $s_0=1{,}5\times0{,}8=1{,}2$ et le seuil $2{,}5\,s_0=3{,}0$. On ne garde que les $|c|<3$ : $0{,}4;\ 0{,}5;\ 0{,}6;\ 0{,}8;\ 1{,}0$, de médiane $0{,}6$ : $\text{PSE}=1{,}5\times0{,}6=0{,}9$. Avec $d=7/3\approx2{,}33$ degrés de liberté, $t_{0{,}975}\approx3{,}76$ (très grand, faute de degrés de liberté) : $ME\approx3{,}39$. Les effets $12$ et $8$ dépassent largement la marge ; les cinq autres n'en approchent pas : **deux effets actifs**.

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

---

## Bilan du chapitre 8

Vous savez maintenant :

- **concevoir** une expérience : identifier les facteurs, les niveaux, l'**unité expérimentale** et la réponse ; appliquer la **randomisation** (contre la confusion), la **répétition** (contre le bruit, sans pseudo-réplication) et le **blocage** (contre la variabilité connue) ;
- expliquer pourquoi **changer un facteur à la fois** est moins précis et **aveugle aux interactions** ;
- mener et **démontrer** une **ANOVA** : décomposition $SS_T=SS_B+SS_W$, test $F$, lien avec le test de Student et la **régression**, vérification des hypothèses, **Tukey** et **contrastes**, **tailles d'effet** ($\eta^2$, $\omega^2$, $f$) ;
- analyser un plan **en blocs** et un plan à **deux facteurs** avec **interaction** (lire d'abord le graphique d'interaction, étudier les effets simples) ;
- calculer la **puissance** d'une ANOVA ou d'un plan factoriel *avant* l'expérience, et dimensionner le nombre de répétitions ;
- construire un **plan factoriel $2^k$** et calculer ses **effets à la main** (contrastes, algorithme de Yates), les relier aux coefficients de la régression, et repérer les effets actifs d'un plan non répliqué (diagramme demi-normal, **méthode de Lenth**) ;
- construire un **plan fractionnaire**, déterminer ses **alias** et sa **résolution**, repérer le danger de la confusion et le lever par un **repliement** ;
- optimiser un réglage par la **méthodologie des surfaces de réponse** : test de courbure, **plan composite centré**, modèle quadratique, test de défaut d'ajustement, **point stationnaire** et analyse canonique, essais de confirmation ;
- (en option) situer les **plans optimaux** ($D$-optimalité) pour les domaines contraints.

Ce chapitre a montré qu'un bon plan **simplifie l'analyse** et qu'il détermine, avant la première mesure, ce que l'on pourra conclure. Le chapitre 7 (inférence causale) aborde le problème inverse : que conclure quand on **n'a pas pu** randomiser, comme dans la plupart des données observationnelles de ce livre.
