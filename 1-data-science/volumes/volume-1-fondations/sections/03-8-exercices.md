## 3.8 Exercices du chapitre 3

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse.

### Énoncés

**Exercice 1 ⭐ (descriptif).** Huit commandes en € : $12,\,15,\,15,\,18,\,20,\,22,\,25,\,60$. Calculez la moyenne, la médiane, le mode, l'écart-type (avec $n-1$) et l'écart interquartile. Quelle mesure de position est la plus représentative, et pourquoi ?

**Exercice 2 ⭐ (variance sans biais).** Un échantillon de 5 délais de livraison : $4,\,8,\,6,\,5,\,7$ jours. Calculez la variance en divisant par $n$ puis par $n-1$. Laquelle utiliser pour estimer la variance de **tous** les délais ?

**Exercice 3 ⭐⭐ (maximum de vraisemblance).** Le nombre de commandes par heure a été relevé 8 fois : $2,\,3,\,1,\,4,\,0,\,3,\,2,\,5$. On modélise par une loi de Poisson$(\lambda)$. (a) Écrivez la log-vraisemblance et trouvez $\hat\lambda$ en dérivant. (b) Avec cette estimation, quelle est la probabilité de ne recevoir aucune commande pendant une heure ?

**Exercice 4 ⭐ (IC d'une moyenne).** Sur $n=36$ commandes : $\bar x=52$ €, $s=12$ €. Donnez un intervalle de confiance à 95 % de la moyenne, puis à 99 %. Quelle est la signification du « 95 % » ?

**Exercice 5 ⭐⭐ (IC d'une proportion).** Un questionnaire envoyé à 60 clients donne 18 « très satisfaits ». Calculez l'IC à 95 % de la vraie proportion par la méthode de Wald et par celle de Wilson. Pourquoi sont-ils différents ?

**Exercice 6 ⭐⭐ (test sur une moyenne).** Le transporteur promet un délai moyen de 3 jours. Sur 25 colis, on mesure en moyenne 3,6 jours avec un écart-type de 1,5 jour. (a) Testez $H_0:\mu=3$ contre $H_1:\mu\neq3$ à 5 %. (b) Que change un test unilatéral $H_1:\mu>3$ ? (c) Peut-on dire que le transporteur respecte sa promesse ?

**Exercice 7 ⭐⭐ (test A/B).** Version A : 45 achats sur 500 visiteurs. Version B : 66 achats sur 500 visiteurs. (a) B est-elle meilleure, à 5 % ? (b) Donnez un IC de la différence. (c) Quelle était la puissance de ce test si le vrai écart est celui observé ?

**Exercice 8 ⭐⭐ (khi-deux).** Parmi 100 clients ayant reçu un code promo, 30 ont acheté ; parmi 100 clients sans code, 45 ont acheté. Le code a-t-il un effet ? Construisez le tableau, calculez les effectifs attendus et le test du khi-deux. Comparez avec le test de deux proportions.

**Exercice 9 ⭐⭐⭐ (taille d'échantillon).** Le taux de conversion actuel est de 20 %. La gérante veut détecter une hausse à 24 % avec une puissance de 80 % et $\alpha=5\,\%$. (a) Combien de visiteurs par version ? (b) Et pour détecter 22 % ? (c) Expliquez le rapport entre les deux résultats.

**Exercice 10 ⭐⭐⭐ (tests multiples).** Un analyste teste 8 hypothèses et obtient les p-valeurs $0{,}001;\ 0{,}008;\ 0{,}012;\ 0{,}030;\ 0{,}040;\ 0{,}200;\ 0{,}500;\ 0{,}700$. Lesquelles sont rejetées à 5 % (a) sans correction, (b) avec Bonferroni, (c) avec Holm, (d) avec Benjamini-Hochberg ?

### Corrigés

**Corrigé 1.** Moyenne : $187/8=23{,}375$. Triées : $12,15,15,18,20,22,25,60$ : la médiane est $(18+20)/2=19$. Mode : 15. Écart-type ($n-1$) : voir le code (≈ 15,4). Les quartiles (méthode de NumPy) donnent un IQR de 7,75. La **médiane** (19) est la plus représentative : la moyenne (23,4) est tirée vers le haut par la commande de 60 € (valeur extrême), qui est supérieure de plus du double au reste.

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
