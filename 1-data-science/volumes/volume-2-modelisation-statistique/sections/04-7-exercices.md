## 4.7 Exercices du chapitre 4

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 10 et 13 s'appuient sur des objets définis dans les sections précédentes (la fonction `kalman_niveau_local` de 4.5, la série `v` de 4.3).

### Énoncés

**Exercice 1 ⭐ (autocorrélation à la main).** Six chiffres d'affaires hebdomadaires (en centaines de €) : $8,\,6,\,9,\,5,\,7,\,4$. Calculez à la main les autocorrélations $r_1$ et $r_2$. Quel signe attendiez-vous pour $r_1$ en regardant la série, et pourquoi ?

**Exercice 2 ⭐ (stationnaire ou non ?).** Pour chaque processus ($\varepsilon_t$ est un bruit blanc), dites s'il est stationnaire, et si non, quel remède appliquer : (a) $Y_t=5+\varepsilon_t$ ; (b) $Y_t=Y_{t-1}+\varepsilon_t$ ; (c) $Y_t=0{,}9\,Y_{t-1}+\varepsilon_t$ ; (d) $Y_t=2t+\varepsilon_t$ ; (e) $Y_t=1{,}1\,Y_{t-1}+\varepsilon_t$.

**Exercice 3 ⭐ (prévoir avec un AR(1)).** Un processus suit $Y_t-10=0{,}8\,(Y_{t-1}-10)+\varepsilon_t$ avec $\sigma=2$. (a) Quelle est sa variance, et les autocorrélations $\rho(1),\rho(2),\rho(3)$ ? (b) On observe $Y_T=14$ : donnez les prévisions à 1, 2 et 3 pas, avec les demi-largeurs des intervalles à 95 %.

**Exercice 4 ⭐⭐ (MA(1) et inversibilité).** (a) Calculez $\rho(1)$ pour $\theta=0{,}8$, puis pour $\theta=1{,}25$. Que remarquez-vous ? (b) Montrez qu'un MA(1) ne peut jamais avoir $|\rho(1)|>0{,}5$. Si vous observez $r_1=0{,}6$ sur une longue série, que concluez-vous ?

**Exercice 5 ⭐⭐ (Ljung-Box à la main).** Sur $n=50$ résidus, on trouve $r_1=0{,}30$ et $r_2=0{,}20$. Calculez $Q(2)$ et sa p-valeur (indice : pour 2 degrés de liberté, $P(\chi^2_2>x)=e^{-x/2}$). Que concluez-vous ?

**Exercice 6 ⭐⭐ (du logarithme aux euros).** Un modèle prévoit $\log(\text{ca})=7{,}60$ pour décembre, avec une erreur type de prévision de $0{,}08$. Donnez la prévision **médiane** en euros, la prévision de la **moyenne**, et l'intervalle de prévision à 95 %.

**Exercice 7 ⭐⭐ (MASE et MAPE).** Sur l'apprentissage, le naïf saisonnier a une MAE de 150 €. Le modèle A a une MAE de 120 € sur le test et le modèle B de 160 €. (a) Calculez les MASE. (b) Pourquoi le MAPE est-il dangereux quand une valeur réelle est nulle ? (c) Pourquoi favorise-t-il les prévisions trop basses ?

**Exercice 8 ⭐⭐ (identifier un modèle).** Trois séries de 300 points, $X$, $Y$ et $Z$, ont été simulées avec des modèles ARMA différents. Voici leurs autocorrélations et autocorrélations partielles. **Identifiez** pour chacune le modèle le plus probable (type et ordre), puis vérifiez avec les critères d'information.

```python
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd
from scipy import stats
import statsmodels.api as sm
from statsmodels.tsa.arima_process import ArmaProcess
from statsmodels.tsa.arima.model import ARIMA
from statsmodels.tsa.stattools import acf, pacf

mystere = {"X": ([1, -0.75], [1]), "Y": ([1], [1, 0.7, 0.5]), "Z": ([1, -0.5, -0.3], [1])}
series = {nom: ArmaProcess(ar, ma).generate_sample(300, distrvs=np.random.default_rng(100 + j).standard_normal)
          for j, (nom, (ar, ma)) in enumerate(mystere.items())}
bande = 1.96 / np.sqrt(300)
print("bande de confiance : +/-", round(bande, 3))
for nom, s in series.items():
    print(f"série {nom} : ACF  décalages 1-6 :", acf(s, nlags=6, fft=False)[1:].round(2))
    print(f"          PACF décalages 1-6 :", pacf(s, nlags=6, method="ols")[1:].round(2))
```
<!--sortie-->
```text
bande de confiance : +/- 0.113
série X : ACF  décalages 1-6 : [0.73 0.58 0.43 0.28 0.2  0.12]
          PACF décalages 1-6 : [ 0.74  0.1  -0.05 -0.1   0.03 -0.03]
série Y : ACF  décalages 1-6 : [ 0.6   0.17 -0.19 -0.25 -0.23 -0.17]
          PACF décalages 1-6 : [ 0.6  -0.28 -0.27  0.1  -0.12 -0.12]
série Z : ACF  décalages 1-6 : [0.69 0.57 0.48 0.36 0.29 0.28]
          PACF décalages 1-6 : [ 0.69  0.19  0.08 -0.07 -0.    0.09]
```

**Exercice 9 ⭐⭐⭐ (la sur-différenciation, en théorie).** Soit $Y_t$ un AR(1) stationnaire de coefficient $\varphi$, et $W_t=Y_t-Y_{t-1}$. (a) Calculez $\operatorname{Var}(W_t)$ et $\operatorname{Cov}(W_t,W_{t-1})$ en fonction de $\gamma(0)$ et de $\varphi$, puis montrez que $\rho_W(1)=-\dfrac{1-\varphi}{2}$. (b) Que vaut ce résultat pour $\varphi=0$ ? pour $\varphi\to1$ ? Interprétez. (c) Vérifiez par simulation pour $\varphi=0{,}5$ et $\varphi=0{,}9$.

**Exercice 10 ⭐⭐⭐ (filtre de Kalman à la main).** Niveau local de variances $\sigma_\varepsilon^2=9$ (observation) et $\sigma_\eta^2=3$ (niveau), croyance initiale $\mathcal N(50,\,12)$ avant la première mesure. On observe $y_1=56$ puis $y_2=52$. (a) Calculez à la main les gains $K_1,K_2$, les niveaux filtrés $a_{1|1},a_{2|2}$ et leurs variances. (b) Quel est le gain en régime permanent ? (c) À quel paramètre de lissage exponentiel cela correspond-il ?

**Exercice 11 ⭐⭐⭐ (régression fallacieuse et remède).** Deux marches aléatoires indépendantes de 200 points sont régressées l'une sur l'autre. (a) Quelle part de régressions « significatives » à 5 % attendez-vous, en niveaux ? (b) Montrez par simulation que la régression **des différences** $\Delta a_t$ sur $\Delta b_t$ redonne le bon taux de 5 %. (c) Pourquoi ce remède fonctionne-t-il, et quelle information perd-on ?

**Exercice 12 ⭐⭐ (GARCH à la main).** Un GARCH(1,1) a pour paramètres $\omega=0{,}1$, $\alpha=0{,}2$, $\beta=0{,}7$. (a) Quelle est la variance de long terme ? (b) Hier, $\varepsilon_{t-1}=2$ et $\sigma_{t-1}^2=1{,}5$ : que vaut $\sigma_t^2$ ? (c) Quelle est la prévision de $\sigma_{t+1}^2$ ? (d) En combien de pas l'excès de variance (au-dessus de la variance de long terme) est-il divisé par deux ?

**Exercice 13 ⭐⭐⭐ (le concours complet sur une autre série).** Appliquez la démarche de 4.3 à la série `nb_commandes` (nombre de commandes par mois) : travaillez en logarithme, apprenez sur 2016-2023, prévoyez 2024-2025 avec (i) le naïf saisonnier avec dérive et (ii) un SARIMAX$(1,0,0)(0,1,1)_{12}$ avec tendance et variables `promo` et `covid`. Calculez la MASE (en nombre de commandes) de chacun. Le modèle bat-il la référence ? Que pensez-vous de la précision atteignable sur cette série, plus bruitée que le chiffre d'affaires ?

### Corrigés

**Corrigé 1.** Moyenne $=39/6=6{,}5$ ; écarts : $1{,}5;\,-0{,}5;\,2{,}5;\,-1{,}5;\,0{,}5;\,-2{,}5$ ; somme des carrés : $2{,}25+0{,}25+6{,}25+2{,}25+0{,}25+6{,}25=17{,}5$. **Décalage 1** : produits $(-0{,}5)(1{,}5)=-0{,}75$ ; $(2{,}5)(-0{,}5)=-1{,}25$ ; $(-1{,}5)(2{,}5)=-3{,}75$ ; $(0{,}5)(-1{,}5)=-0{,}75$ ; $(-2{,}5)(0{,}5)=-1{,}25$ ; somme $-7{,}75$, donc $r_1=-7{,}75/17{,}5\approx-0{,}443$. **Décalage 2** : $(2{,}5)(1{,}5)=3{,}75$ ; $(-1{,}5)(-0{,}5)=0{,}75$ ; $(0{,}5)(2{,}5)=1{,}25$ ; $(-2{,}5)(-1{,}5)=3{,}75$ ; somme $9{,}5$, donc $r_2\approx0{,}543$. On attendait un $r_1$ **négatif** : la série fait du « zigzag » (haut, bas, haut, bas) autour de sa moyenne, et un zigzag correspond à une corrélation négative entre deux mois consécutifs et positive à deux mois d'écart. Avec seulement six points, ces valeurs sont très incertaines (bande de $\pm0{,}8$).

```python
import warnings
warnings.filterwarnings("ignore")
import numpy as np
import pandas as pd

def acf_manuel(x, k):
    d = np.asarray(x, float) - np.mean(x)
    return (d[:len(d) - k] * d[k:]).sum() / (d ** 2).sum()

x = [8, 6, 9, 5, 7, 4]
print("r1 =", round(acf_manuel(x, 1), 4), "| r2 =", round(acf_manuel(x, 2), 4), "| bande 1,96/racine(6) =", round(1.96 / np.sqrt(6), 2))
```
<!--sortie-->
```text
r1 = -0.4429 | r2 = 0.5429 | bande 1,96/racine(6) = 0.8
```

**Corrigé 2.** (a) **Stationnaire** : moyenne 5, variance $\sigma^2$, pas de mémoire. (b) **Marche aléatoire** : non stationnaire ($\operatorname{Var}=t\sigma^2$) ; remède : **différencier**. (c) **Stationnaire** ($|\varphi|=0{,}9<1$), mais très persistant : la mémoire décroît lentement ($\rho(k)=0{,}9^k$), et sur un échantillon court elle se confond facilement avec une racine unitaire (c'est le manque de puissance de 4.1.6). (d) **Non stationnaire** : la moyenne $2t$ varie ; remède : **retirer la tendance** (régression sur $t$), car la tendance est déterministe, pas stochastique (différencier fonctionnerait aussi, mais sur-différencierait). (e) **Explosif** ($|\varphi|>1$) : non stationnaire, aucune transformation simple ne le « répare » ; c'est rare en pratique.

```python
rng = np.random.default_rng(3)
n = 400
e = rng.normal(size=n)
def generer(phi, tendance=0.0, depart=0.0):
    y = np.zeros(n); y[0] = depart
    for t in range(1, n):
        y[t] = phi * y[t - 1] + e[t] + tendance * t
    return y
cas = {"(a) 5 + bruit": 5 + e, "(b) marche aléatoire": generer(1.0), "(c) AR(1), phi = 0,9": generer(0.9),
       "(d) 2t + bruit": 2 * np.arange(n) + e}
lignes = [{"processus": k, "moyenne 1re moitié": s[:n // 2].mean(), "moyenne 2e moitié": s[n // 2:].mean(),
           "écart-type 1re moitié": s[:n // 2].std(), "écart-type 2e moitié": s[n // 2:].std()} for k, s in cas.items()]
print(pd.DataFrame(lignes).round(1).to_string(index=False))
```
<!--sortie-->
```text
           processus  moyenne 1re moitié  moyenne 2e moitié  écart-type 1re moitié  écart-type 2e moitié
       (a) 5 + bruit                 5.0                5.0                    1.0                   1.0
(b) marche aléatoire                -2.8                7.4                    4.3                   4.1
(c) AR(1), phi = 0,9                 0.3                0.2                    2.2                   2.3
      (d) 2t + bruit               199.0              599.0                  115.6                 115.5
```

La simulation montre que les moyennes diffèrent nettement d'une moitié à l'autre pour (b) et (d), alors que (a) et (c) se ressemblent. (Pour la marche aléatoire (b), c'est la variance **à travers les trajectoires** qui croît avec $t$ (4.1.3) ; sur une seule trajectoire, comparer les écarts-types de deux moitiés n'est pas probant, et le tableau ne le montre d'ailleurs pas. C'est le déplacement de la moyenne qui trahit la non-stationnarité.)

**Corrigé 3.** (a) $\gamma(0)=\dfrac{\sigma^2}{1-\varphi^2}=\dfrac4{1-0{,}64}=11{,}11$ (écart-type $3{,}33$) ; $\rho(1)=0{,}8$, $\rho(2)=0{,}64$, $\rho(3)=0{,}512$. (b) $\hat y_{T+h}=10+0{,}8^h\times(14-10)$ : $13{,}2$ ; $12{,}56$ ; $12{,}048$. Demi-largeurs : $1{,}96\,\sigma\sqrt{\sum_{j<h}\varphi^{2j}}$ : $h=1$ : $1{,}96\times2=3{,}92$ ; $h=2$ : $3{,}92\times\sqrt{1{,}64}=5{,}02$ ; $h=3$ : $3{,}92\times\sqrt{1{,}64+0{,}4096}=5{,}61$. Limite : $1{,}96\times3{,}33=6{,}53$.

```python
from statsmodels.tsa.arima.model import ARIMA
phi, mu, sigma, yT = 0.8, 10.0, 2.0, 14.0
print("variance :", round(sigma ** 2 / (1 - phi ** 2), 2), "| rho(1..3) :", [round(phi ** k, 3) for k in (1, 2, 3)])
print("prévisions :", [round(mu + phi ** h * (yT - mu), 3) for h in (1, 2, 3)])
print("demi-largeurs :", np.round([1.96 * sigma * np.sqrt(sum(phi ** (2 * j) for j in range(h))) for h in (1, 2, 3)], 2),
      "| limite :", round(1.96 * sigma / np.sqrt(1 - phi ** 2), 2))
# vérification avec statsmodels (paramètres fixés : constante, phi, sigma2)
fixe = ARIMA(np.r_[np.full(50, mu), yT], order=(1, 0, 0), trend="c").filter([mu, phi, sigma ** 2])
p = fixe.get_forecast(3)
print("statsmodels :", p.predicted_mean.round(3), ((p.conf_int()[:, 1] - p.conf_int()[:, 0]) / 2).round(2))
```
<!--sortie-->
```text
variance : 11.11 | rho(1..3) : [0.8, 0.64, 0.512]
prévisions : [13.2, 12.56, 12.048]
demi-largeurs : [3.92 5.02 5.61] | limite : 6.53
statsmodels : [13.2   12.56  12.048] [3.92 5.02 5.61]
```

**Corrigé 4.** (a) $\rho(1)=\dfrac{0{,}8}{1+0{,}64}=0{,}488$ et $\rho(1)=\dfrac{1{,}25}{1+1{,}5625}=0{,}488$ : **les deux valeurs donnent la même autocorrélation** ($\theta$ et $1/\theta$). On retient la valeur **inversible** $\theta=0{,}8$. (b) $1+\theta^2\ge2|\theta|$ (car $(1-|\theta|)^2\ge0$), donc $|\rho(1)|=\dfrac{|\theta|}{1+\theta^2}\le\dfrac12$, avec égalité pour $\theta=\pm1$. Si l'on observe $r_1=0{,}6$ sur une longue série (assez longue pour que $0{,}6$ ne soit pas du bruit d'échantillonnage), **ce n'est pas un MA(1)** : il faut un AR (dont la mémoire peut produire une autocorrélation d'ordre 1 proche de 1), ou un ARMA.

```python
from statsmodels.tsa.arima_process import arma_acf
for th in (0.8, 1.25):
    print(f"theta = {th} : rho(1) = {arma_acf([1], [1, th], 2)[1]:.4f}")
thetas = np.linspace(-5, 5, 100001)
rho1 = thetas / (1 + thetas ** 2)
print("maximum de |rho(1)| sur theta dans [-5, 5] :", round(np.abs(rho1).max(), 4), "atteint pour theta =", round(abs(thetas[np.abs(rho1).argmax()]), 3))
```
<!--sortie-->
```text
theta = 0.8 : rho(1) = 0.4878
theta = 1.25 : rho(1) = 0.4878
maximum de |rho(1)| sur theta dans [-5, 5] : 0.5 atteint pour theta = 1.0
```

**Corrigé 5.** $Q(2)=n(n+2)\left[\dfrac{r_1^2}{n-1}+\dfrac{r_2^2}{n-2}\right]=50\times52\times\left[\dfrac{0{,}09}{49}+\dfrac{0{,}04}{48}\right]=2600\times(0{,}001837+0{,}000833)=6{,}94$. Pour 2 degrés de liberté, $p=e^{-6{,}94/2}=e^{-3{,}47}\approx0{,}031$. **p < 0,05** : on rejette l'hypothèse « bruit blanc » ; le modèle n'a pas tout expliqué. (Si les résidus provenaient d'un modèle avec deux paramètres AR/MA estimés, il faudrait comparer à un khi-deux à $2-2=0$ degré de liberté : le test serait inutilisable à 2 retards ; on utiliserait plus de retards.)

```python
from scipy import stats
n, r = 50, np.array([0.30, 0.20])
Q = n * (n + 2) * np.sum(r ** 2 / (n - np.arange(1, 3)))
print("Q(2) =", round(Q, 3), "| p-valeur =", round(np.exp(-Q / 2), 4), "| via scipy :", round(1 - stats.chi2.cdf(Q, 2), 4))
```
<!--sortie-->
```text
Q(2) = 6.942 | p-valeur = 0.0311 | via scipy : 0.0311
```

**Corrigé 6.** La **médiane** est $e^{7{,}60}\approx1\,998$ €. La **moyenne** vaut $e^{7{,}60+0{,}08^2/2}=e^{7{,}6032}\approx2\,005$ € (un facteur $e^{0{,}0032}\approx1{,}003$ : négligeable). L'intervalle à 95 % : $\exp(7{,}60\pm1{,}96\times0{,}08)=\exp(7{,}60\pm0{,}1568)=[1\,708\,;\,2\,337]$ € : environ $\pm16\,\%$ autour de la médiane, de façon **asymétrique** en euros (l'intervalle est un peu plus étendu vers le haut : $+339$ € contre $-290$ €).

```python
m, s = 7.60, 0.08
print("médiane :", round(np.exp(m), 1), "| moyenne :", round(np.exp(m + s ** 2 / 2), 1))
print("IC95 % :", round(np.exp(m - 1.96 * s), 1), "à", round(np.exp(m + 1.96 * s), 1),
      "| écarts à la médiane :", round(np.exp(m - 1.96 * s) - np.exp(m), 1), "et +", round(np.exp(m + 1.96 * s) - np.exp(m), 1))
```
<!--sortie-->
```text
médiane : 1998.2 | moyenne : 2004.6
IC95 % : 1708.2 à 2337.4 | écarts à la médiane : -290.0 et + 339.2
```

**Corrigé 7.** (a) $\text{MASE}_A=120/150=0{,}80$ (le modèle fait **20 % mieux** que le naïf saisonnier de l'apprentissage) ; $\text{MASE}_B=160/150\approx1{,}07$ (**moins bien** que le naïf). (b) Le MAPE divise par $|y_t|$ : si $y_t=0$ (un mois sans vente), le terme est indéfini (division par zéro), et pour des valeurs réelles très petites il explose. (c) Une sous-prévision ne peut pas dépasser **100 %** d'erreur (prévoir 0 pour une valeur de 100 donne 100 %), alors qu'une surestimation est **illimitée** (prévoir 300 pour 100 donne 200 %). En minimisant le MAPE, un modèle est donc incité à prévoir **trop bas**.

```python
actuel = 100
for prevu in (0, 50, 150, 300):
    print(f"réel = {actuel}, prévu = {prevu:3d} -> erreur en % du réel = {100 * abs(actuel - prevu) / actuel:.0f} %")
print("MASE A =", 120 / 150, "| MASE B =", round(160 / 150, 3))
```
<!--sortie-->
```text
réel = 100, prévu =   0 -> erreur en % du réel = 100 %
réel = 100, prévu =  50 -> erreur en % du réel = 50 %
réel = 100, prévu = 150 -> erreur en % du réel = 50 %
réel = 100, prévu = 300 -> erreur en % du réel = 200 %
MASE A = 0.8 | MASE B = 1.067
```

**Corrigé 8.** **Règle** (4.2.1) : AR($p$) $\Rightarrow$ PACF qui s'arrête après $p$, ACF qui décroît ; MA($q$) $\Rightarrow$ ACF qui s'arrête après $q$, PACF qui décroît. Lecture des sorties de l'énoncé (bande de $\pm0{,}113$) :

- **$X$** : ACF qui décroît lentement (0,73 ; 0,58 ; 0,43 ; 0,28…), PACF avec **un seul** pic net, au décalage 1 (0,74), puis des valeurs dans la bande : un **AR(1)**, de coefficient voisin de 0,74.
- **$Z$** : ACF qui décroît, PACF de 0,69 puis 0,19 (au-dessus de la bande), puis dans la bande : un **AR(2)** est plausible (un AR(1) est possible : le deuxième pic est faible).
- **$Y$** : PACF qui décroît avec alternance de signes ($0{,}60$ ; $-0{,}28$ ; $-0{,}27$ ; puis dans la bande) : une signature de **MA** ; mais l'ACF ($0{,}60$ ; $0{,}17$ ; puis $-0{,}19$, $-0{,}25$, $-0{,}23$ au-delà de la bande) ne s'arrête **pas** proprement après le décalage 2. Cette série est **ambiguë** à l'œil : un MA(2), mais peut-être un MA plus long ou un ARMA.

Voilà la réalité de l'identification : avec 300 points, les autocorrélations estimées fluctuent d'environ $\pm0{,}11$, et les signatures théoriques de la figure de 4.2.1 se brouillent. D'où le rôle des critères d'information, qui comparent les modèles candidats **entre eux** :

```python
candidats = {"AR(1)": (1, 0, 0), "AR(2)": (2, 0, 0), "MA(1)": (0, 0, 1), "MA(2)": (0, 0, 2), "ARMA(1,1)": (1, 0, 1)}
ajustements = {nom: {c: ARIMA(s, order=o, trend="n").fit() for c, o in candidats.items()} for nom, s in series.items()}
aic = pd.DataFrame({nom: {c: m.aic for c, m in d.items()} for nom, d in ajustements.items()})
bic = pd.DataFrame({nom: {c: m.bic for c, m in d.items()} for nom, d in ajustements.items()})
print("AIC par modèle (une colonne par série) :")
print(aic.round(1).to_string())
print("\nBIC par modèle :")
print(bic.round(1).to_string())
print("\nmeilleur modèle par AIC :", aic.idxmin().to_dict())
print("meilleur modèle par BIC :", bic.idxmin().to_dict())
print("vérité : X = AR(1), phi = 0,75 | Y = MA(2), theta = (0,7 ; 0,5) | Z = AR(2), phi = (0,5 ; 0,3)")
```
<!--sortie-->
```text
AIC par modèle (une colonne par série) :
               X      Y      Z
AR(1)      850.5  906.2  882.7
AR(2)      849.5  883.7  873.3
MA(1)      944.1  929.2  964.5
MA(2)      897.8  864.3  930.8
ARMA(1,1)  850.0  896.0  871.9

BIC par modèle :
               X      Y      Z
AR(1)      858.0  913.6  890.2
AR(2)      860.6  894.8  884.4
MA(1)      951.5  936.6  971.9
MA(2)      908.9  875.4  941.9
ARMA(1,1)  861.1  907.1  883.0

meilleur modèle par AIC : {'X': 'AR(2)', 'Y': 'MA(2)', 'Z': 'ARMA(1,1)'}
meilleur modèle par BIC : {'X': 'AR(1)', 'Y': 'MA(2)', 'Z': 'ARMA(1,1)'}
vérité : X = AR(1), phi = 0,75 | Y = MA(2), theta = (0,7 ; 0,5) | Z = AR(2), phi = (0,5 ; 0,3)
```

**Lecture des critères.** Pour **$Y$**, le MA(2) l'emporte nettement, par l'AIC comme par le BIC : le critère résout l'ambiguïté que l'œil ne résolvait pas. Pour **$X$** et **$Z$**, ce sont des modèles **voisins** qui se disputent la première place avec un ou deux points d'écart : un AR(2) dont le second coefficient est petit ressemble à un AR(1), et un ARMA(1,1) imite un AR(2). **Un écart d'AIC de l'ordre de 1 à 2 ne permet pas de trancher** (la règle empirique est qu'il faut un écart de plus de 2 à 4 points pour préférer un modèle). Le BIC, plus sévère avec la complexité, retrouve la vérité pour $X$ (AR(1)) et pour $Y$ (MA(2)), mais préfère encore l'ARMA(1,1) à l'AR(2) pour $Z$, avec 1,4 point d'écart (883,0 contre 884,4) : pour ces deux modèles voisins, les données n'ont pas de quoi décider. En pratique, on retient alors le modèle **le plus simple** parmi les ex æquo, et on valide par les résidus et par la prévision.

**Corrigé 9.** (a) Soit $\gamma(k)=\varphi^k\gamma(0)$. $\operatorname{Var}(W_t)=2\gamma(0)-2\gamma(1)=2\gamma(0)(1-\varphi)$. $\operatorname{Cov}(W_t,W_{t-1})=\operatorname{Cov}(Y_t-Y_{t-1},Y_{t-1}-Y_{t-2})=\gamma(1)-\gamma(2)-\gamma(0)+\gamma(1)=\gamma(0)(2\varphi-\varphi^2-1)=-\gamma(0)(1-\varphi)^2$. Donc $\rho_W(1)=\dfrac{-\gamma(0)(1-\varphi)^2}{2\gamma(0)(1-\varphi)}=-\dfrac{1-\varphi}2$. (b) Pour $\varphi=0$ ($Y$ est un bruit blanc), on retrouve $-0{,}5$ (4.1.6). Pour $\varphi\to1$ (quasi-marche aléatoire), $\rho_W(1)\to0$ : la différence d'une marche aléatoire est un bruit blanc : **la différenciation est alors le bon remède**. Entre les deux, plus la série est « loin » d'une racine unitaire, plus la différenciation fabrique une autocorrélation négative artificielle. (c) Simulation :

```python
from statsmodels.tsa.arima_process import ArmaProcess
for phi in (0.0, 0.5, 0.9):
    x = ArmaProcess([1, -phi], [1]).generate_sample(300000, distrvs=np.random.default_rng(7).standard_normal)
    print(f"phi = {phi} : rho_W(1) simulé = {acf_manuel(np.diff(x), 1):+.3f}   | théorie -(1-phi)/2 = {-(1 - phi) / 2:+.3f}")
```
<!--sortie-->
```text
phi = 0.0 : rho_W(1) simulé = -0.502   | théorie -(1-phi)/2 = -0.500
phi = 0.5 : rho_W(1) simulé = -0.252   | théorie -(1-phi)/2 = -0.250
phi = 0.9 : rho_W(1) simulé = -0.052   | théorie -(1-phi)/2 = -0.050
```

**Corrigé 10.** (a) **Date 1.** $P_{1|0}=12$, $F_1=12+9=21$, $K_1=12/21=0{,}5714$, $v_1=56-50=6$, $a_{1|1}=50+0{,}5714\times6=53{,}43$, $P_{1|1}=12\times\dfrac{9}{21}=5{,}143$. **Date 2.** $P_{2|1}=5{,}143+3=8{,}143$, $F_2=17{,}143$, $K_2=8{,}143/17{,}143=0{,}475$, $v_2=52-53{,}43=-1{,}43$, $a_{2|2}=53{,}43+0{,}475\times(-1{,}43)=52{,}75$, $P_{2|2}=8{,}143\times\dfrac{9}{17{,}143}=4{,}275$. (b) En régime permanent, la variance prédite $p$ vérifie $p=\dfrac{p\sigma_\varepsilon^2}{p+\sigma_\varepsilon^2}+\sigma_\eta^2$, soit $p^2=\sigma_\eta^2\,p+\sigma_\eta^2\sigma_\varepsilon^2$, donc $p=\dfrac{3+\sqrt{9+4\times27}}2=\dfrac{3+\sqrt{117}}2\approx6{,}908$ et $K_\infty=\dfrac{p}{p+9}\approx0{,}434$. (c) Le lissage exponentiel simple de paramètre $\alpha=K_\infty\approx0{,}43$.

```python
r = kalman_niveau_local(np.array([56.0, 52.0]), s2_eps=9.0, s2_eta=3.0, a0=50.0, P0=12.0)     # fonction définie en 4.5.3
print(pd.DataFrame({k: r[k] for k in ["P_pred", "F", "K", "v", "a_filtre", "P_filtre"]}, index=[1, 2]).round(4).to_string())
p_inf = (3 + np.sqrt(9 + 4 * 27)) / 2
print("régime permanent : p =", round(p_inf, 4), "| K_inf =", round(p_inf / (p_inf + 9), 4))
longue = kalman_niveau_local(np.random.default_rng(1).normal(100, 3, 300), 9.0, 3.0, 100.0, 12.0)
print("gain après 300 observations :", round(longue["K"][-1], 4))
```
<!--sortie-->
```text
    P_pred        F       K       v  a_filtre  P_filtre
1  12.0000  21.0000  0.5714  6.0000   53.4286    5.1429
2   8.1429  17.1429  0.4750 -1.4286   52.7500    4.2750
régime permanent : p = 6.9083 | K_inf = 0.4343
gain après 300 observations : 0.4343
```

**Corrigé 11.** (a) En niveaux, la pente est « significative » dans **plus des trois quarts** des cas (77 % avec 100 points en 4.4.2 ; plus encore avec 200 points, voir la sortie : plus les séries sont longues, plus l'illusion est fréquente), pas 5 %. (b) Sur les différences (qui sont des bruits blancs indépendants), le taux retombe autour de 5 % (la sortie donne une valeur proche, à l'incertitude de la simulation près). (c) La différenciation rend les séries **stationnaires** : les hypothèses du chapitre 1 s'appliquent de nouveau, donc les p-valeurs sont justes. On **perd l'information de long terme** : si les séries sont cointégrées (4.4.2), une régression sur les différences ignore la relation d'équilibre ; il faut alors le modèle à correction d'erreur.

```python
import statsmodels.api as sm
rng = np.random.default_rng(55)
niveaux, differences = [], []
for _ in range(2000):
    a = np.cumsum(rng.normal(size=200))
    b = np.cumsum(rng.normal(size=200))
    niveaux.append(abs(sm.OLS(a, sm.add_constant(b)).fit().tvalues[1]) > 1.96)
    differences.append(abs(sm.OLS(np.diff(a), sm.add_constant(np.diff(b))).fit().tvalues[1]) > 1.96)
print("part de pentes « significatives » à 5 % : en niveaux =", np.mean(niveaux).round(3), "| sur les différences =", np.mean(differences).round(3))
```
<!--sortie-->
```text
part de pentes « significatives » à 5 % : en niveaux = 0.824 | sur les différences = 0.052
```

**Corrigé 12.** (a) $\sigma^2=\dfrac{0{,}1}{1-0{,}2-0{,}7}=1$. (b) $\sigma_t^2=0{,}1+0{,}2\times2^2+0{,}7\times1{,}5=0{,}1+0{,}8+1{,}05=1{,}95$. (c) $\mathbb E[\sigma_{t+1}^2]=\omega+(\alpha+\beta)\sigma_t^2=0{,}1+0{,}9\times1{,}95=1{,}855$ (car $\mathbb E[\varepsilon_t^2\mid\text{passé}]=\sigma_t^2$). (d) L'excès $\sigma^2_{t+h}-1$ est multiplié par $\alpha+\beta=0{,}9$ à chaque pas : il est divisé par deux quand $0{,}9^h=0{,}5$, soit $h=\ln0{,}5/\ln0{,}9\approx6{,}6$ : **environ 7 jours**.

```python
omega, alpha, beta = 0.1, 0.2, 0.7
var_lt = omega / (1 - alpha - beta)
sig2_t = omega + alpha * 2 ** 2 + beta * 1.5
prev = [omega + (alpha + beta) * sig2_t]
for _ in range(19):
    prev.append(omega + (alpha + beta) * prev[-1])
print("variance de long terme :", round(var_lt, 4), "| sigma_t^2 =", round(sig2_t, 3), "| prévision de sigma_{t+1}^2 =", round(prev[0], 3))
print("excès sur la variance de long terme aux pas 1, 5, 10, 20 :", np.round(np.array(prev)[[0, 4, 9, 19]] - var_lt, 3))
print("demi-vie de l'excès :", round(np.log(0.5) / np.log(alpha + beta), 2), "pas")
```
<!--sortie-->
```text
variance de long terme : 1.0 | sigma_t^2 = 1.95 | prévision de sigma_{t+1}^2 = 1.855
excès sur la variance de long terme aux pas 1, 5, 10, 20 : [0.855 0.561 0.331 0.115]
demi-vie de l'excès : 6.58 pas
```

**Corrigé 13.** On applique la démarche de 4.3 à $\log(\text{nb\_commandes})$ : même découpage, un naïf saisonnier avec dérive, un SARIMAX, et la MASE en **nombre de commandes** (échelle : MAE du naïf saisonnier sur l'apprentissage).

```python
from statsmodels.tsa.statespace.sarimax import SARIMAX
v = pd.read_csv("donnees/ventes_mensuelles.csv", parse_dates=["mois"]).set_index("mois")
v.index.freq = "MS"
z = np.log(v["nb_commandes"])
train_z, test_z = z[:"2023-12"], z["2024-01":]
Xe = v[["promo", "covid"]].astype(float)

g = (train_z - train_z.shift(12)).mean()
naif = pd.Series([train_z.iloc[-12 + (h % 12)] + g * (1 + h // 12) for h in range(24)], index=test_z.index)
modele = SARIMAX(train_z, exog=Xe[:"2023-12"], order=(1, 0, 0), seasonal_order=(0, 1, 1, 12), trend="ct").fit(disp=False, maxiter=300)
prevu = pd.Series(modele.get_forecast(24, exog=Xe["2024-01":]).predicted_mean.values, index=test_z.index)

nb_train = np.exp(train_z)
echelle = np.mean(np.abs(nb_train.values[12:] - nb_train.values[:-12]))
lignes = {}
for nom, f in [("naïf saisonnier + dérive", naif), ("SARIMAX(1,0,0)(0,1,1)12 + tendance", prevu)]:
    mae = np.mean(np.abs(np.exp(test_z) - np.exp(f)))
    lignes[nom] = {"MAE (commandes)": mae, "MASE": mae / echelle, "RMSE (log)": np.sqrt(np.mean((test_z - f) ** 2)), "biais (log)": float(np.mean(test_z - f))}
print("MAE du naïf saisonnier sur l'apprentissage :", round(echelle, 2), "commandes")
print(pd.DataFrame(lignes).T.round(3).to_string())
print("écart-type des résidus du SARIMAX (log) :", round(float(np.sqrt(modele.params['sigma2'])), 3), "| à comparer à celui du chiffre d'affaires (4.2) : environ 0,06 à 0,07")
```
<!--sortie-->
```text
MAE du naïf saisonnier sur l'apprentissage : 7.92 commandes
                                    MAE (commandes)   MASE  RMSE (log)  biais (log)
naïf saisonnier + dérive                      7.786  0.983       0.273       -0.139
SARIMAX(1,0,0)(0,1,1)12 + tendance            6.146  0.776       0.216        0.023
écart-type des résidus du SARIMAX (log) : 0.262 | à comparer à celui du chiffre d'affaires (4.2) : environ 0,06 à 0,07
```

Le résultat se lit en trois temps. (1) Le **bruit** de cette série est nettement plus grand que celui du chiffre d'affaires : un nombre de commandes est un **comptage** (de loi de Poisson, de variance égale à la moyenne), donc son erreur relative, de l'ordre de $1/\sqrt{\text{moyenne}}$ (environ 19 % pour 28 commandes par mois), est irréductible. L'écart-type des résidus du SARIMAX est d'environ 0,26 en logarithme, près de quatre fois celui du chiffre d'affaires. (2) Le SARIMAX fait **mieux que la référence simple** (MASE de 0,78 contre 0,98, soit environ 20 % d'erreur de moins ; sa MAE est de 6,1 commandes par mois), mais la référence est déjà **à peine meilleure que le naïf saisonnier de l'apprentissage** (MASE proche de 1) : à ce niveau de bruit, le gain d'un bon modèle se mesure en dizaines de pour cent d'une erreur de toute façon élevée, pas en précision. (3) La bonne conclusion est donc moins « quel modèle ? » que « quelle précision peut-on espérer ? » : une prévision de commandes mensuelles doit s'accompagner d'une **fourchette large**.

---

## Bilan du chapitre 4

Vous savez maintenant :

- **décrire** une série temporelle (tendance, saison, bruit, accident) et la **décomposer** (classique, STL robuste), en travaillant sur le **logarithme** quand la saison est proportionnelle au niveau ;
- définir la **stationnarité**, mesurer la mémoire par l'**autocorrélation** et l'**autocorrélation partielle**, tester le bruit blanc (**Ljung-Box**) et la racine unitaire (**ADF**, **KPSS**) en connaissant leurs limites (peu de puissance, loi de Dickey-Fuller non normale) ;
- distinguer **tendance déterministe** et **tendance stochastique**, et éviter la **sur-différenciation** ;
- construire des modèles **AR, MA, ARMA, ARIMA, SARIMA** et **SARIMAX**, connaître leurs conditions de stationnarité et d'inversibilité, suivre la méthode de **Box-Jenkins** (identification, estimation, diagnostic, prévision) et lire un diagnostic de résidus ;
- **prévoir** avec ses intervalles, passer du logarithme aux euros, et **évaluer honnêtement** : découpage temporel, références simples, MAE, RMSE, MAPE, **MASE**, bootstrap par blocs, **validation à origine glissante**, combinaison de prévisions ;
- comprendre qu'un seul jeu de test est **bruité** : le meilleur modèle en espérance ne gagne pas toujours (4.3.8) ;
- (en option) modéliser **plusieurs séries** (VAR, causalité de Granger, **cointégration**, régression fallacieuse), la **volatilité** (GARCH), les **modèles d'espace d'états** et le **filtre de Kalman** (lissage exponentiel, données manquantes), et situer **Prophet** et les bibliothèques modernes.

Le chapitre 5 change d'univers : il ne s'agit plus d'une série qui évolue **dans le temps calendaire**, mais d'un événement dont on mesure **la durée d'attente**, avec le défi particulier de la **censure** : combien de temps un client reste-t-il fidèle, quand certains sont encore clients aujourd'hui ?
