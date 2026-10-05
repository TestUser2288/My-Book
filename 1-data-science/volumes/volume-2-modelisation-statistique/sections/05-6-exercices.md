## 5.6 Exercices corrigés

Les exercices sont classés par difficulté : ⭐ (application directe), ⭐⭐ (demande de réfléchir), ⭐⭐⭐ (synthèse). **Cherchez d'abord seul(e)**, à la main quand c'est demandé, avant de lire le corrigé. Les fonctions écrites dans le chapitre (`kaplan_meier`, `logrank`, `cox_ph`, `test_ph`, `ajuster`, `incidence_cumulee`…) sont réutilisées dans les corrigés.

**Exercice 1 ⭐ (censure et Kaplan-Meier à la main).** Yasmine suit six clients : $(4;\text{parti})$, $(7;\text{censuré})$, $(9;\text{parti})$, $(12;\text{parti})$, $(15;\text{censuré})$, $(20;\text{censuré})$ (durées en mois). (a) Calculez la moyenne de toutes les durées, puis celle des seuls clients partis. (b) Calculez la courbe de Kaplan-Meier à la main. (c) Donnez la médiane de survie. (d) Calculez la durée moyenne restreinte jusqu'à 20 mois.

**Exercice 2 ⭐ (relations entre les fonctions).** Un client a, à l'âge $t$ de la relation (en mois), un risque instantané $h(t)=0{,}0008\,t$. (a) Déduisez $H(t)$ et $S(t)$. (b) Calculez $S(24)$ et la médiane. (c) De quelle loi de Weibull s'agit-il ? Donnez sa durée moyenne.

**Exercice 3 ⭐ (taux constant).** Sur un échantillon, on observe 40 départs pour un total de 1 600 mois-clients d'exposition. (a) Estimez le taux de départ mensuel $\lambda$ (exponentielle), son écart-type et un intervalle de confiance à 95 %. (b) Estimez $S(24)$ et la durée moyenne. (c) Testez $H_0:\lambda=0{,}03$ par le test de Wald et par le rapport de vraisemblance.

**Exercice 4 ⭐⭐ (Greenwood).** Huit clients : $(2;1)$, $(3;1)$, $(3;1)$, $(5;0)$, $(6;1)$, $(8;0)$, $(9;1)$, $(11;0)$ (durée ; 1 = parti, 0 = censuré). Construisez le tableau de Kaplan-Meier (avec les ex aequo), puis donnez $\hat S(6)$, son erreur standard de Greenwood et son intervalle de confiance log-log à 95 %.

**Exercice 5 ⭐⭐ (log-rank).** Deux groupes de cinq clients. Groupe A : $(3;1)$, $(6;1)$, $(8;0)$, $(10;1)$, $(12;0)$. Groupe B : $(5;1)$, $(7;1)$, $(9;1)$, $(11;0)$, $(13;0)$. Calculez à la main le test du log-rank (tableau aux instants de départ : ensembles à risque, départs attendus, variances), concluez, puis vérifiez avec `statsmodels`.

**Exercice 6 ⭐⭐ (durée moyenne restreinte).** Les courbes de survie de deux campagnes sont des escaliers. Campagne A : $S=1$ jusqu'à 6 mois, $0{,}8$ sur $[6,12[$, $0{,}5$ sur $[12,18[$, $0{,}3$ ensuite. Campagne B : $S=1$ jusqu'à 9 mois, $0{,}9$ sur $[9,15[$, $0{,}7$ sur $[15,21[$, $0{,}6$ ensuite. Calculez la durée moyenne restreinte à 24 mois de chaque campagne et leur différence. Que signifie ce nombre ?

**Exercice 7 ⭐⭐ (lire une sortie de Cox).** Un modèle de Cox donne : offre de bienvenue $\hat\beta=-0{,}40$ (ET $0{,}065$), âge $\hat\beta=-0{,}0136$ (ET $0{,}0030$), canal Instagram (contre Boutique) $\hat\beta=0{,}635$ (ET $0{,}084$). (a) Donnez pour chaque variable le rapport de risques, son IC95 et le $z$ de Wald. (b) Quel est l'effet de dix années d'âge de plus ? (c) Quel est le rapport de risques d'un client Instagram *avec* offre contre un client Boutique *sans* offre, à âge égal ? (d) La survie à 24 mois d'un client de référence est de 0,80 : quelle est celle du même client avec l'offre ? (e) Un AFT Weibull donne $\hat\gamma_{\text{offre}}=0{,}35$ avec $\hat\sigma=0{,}74$ : quel rapport de risques équivalent ?

**Exercice 8 ⭐⭐ (le biais d'immortalité).** Simulez 2 000 clients dont les durées sont exponentielles de taux 2 % par mois (graine 8), censurées uniformément entre 18 et 48 mois. Un cadeau est remis au mois 6 à la moitié des clients encore présents. Estimez l'effet du cadeau (qui n'en a aucun) (a) en traitant « a reçu le cadeau » comme une variable fixe, (b) correctement, avec une variable dépendant du temps. Commentez.

**Exercice 9 ⭐⭐ (estimer la forme de Weibull de deux façons).** Pour l'ensemble des 2 000 clients (sans covariables), estimez la forme $k$ de la loi de Weibull (a) par le graphique de Weibull : régression de $\ln(-\ln\hat S_{KM})$ sur $\ln t$ entre 6 et 60 mois ; (b) par maximum de vraisemblance. Comparez, et expliquez l'écart avec la valeur $k=1{,}35$ utilisée pour simuler.

**Exercice 10 ⭐⭐⭐ (log-rank et Cox).** (a) Montrez que le score du modèle de Cox à une variable binaire en $\beta=0$ vaut $O_1-E_1$. (b) Vérifiez numériquement, sur les 2 000 clients (variable `offre_bienvenue`), que la statistique de score $U^2/I$ est très proche du $\chi^2$ du log-rank. Pourquoi n'est-elle pas *exactement* égale ?

**Exercice 11 ⭐⭐⭐ (décider : le seuil de rentabilité).** Reprenez les survies moyennes avec et sans offre du 5.4.5. L'offre de bienvenue coûte maintenant 25 DT par client. À partir de quelle **marge mensuelle** par client actif est-elle rentable, pour un taux d'actualisation de 1 % par mois ? Et pour 2 % ?

**Exercice 12 ⭐⭐⭐ (risques concurrents à la main).** Huit clients, durées et causes de sortie (0 = censuré, 1 = départ volontaire, 2 = fermeture forcée) : $(1;1)$, $(2;2)$, $(3;1)$, $(4;0)$, $(5;2)$, $(6;1)$, $(7;0)$, $(9;2)$. Calculez à la main les incidences cumulées $\hat F_1$ et $\hat F_2$ (estimateur d'Aalen-Johansen) et la survie totale. Vérifiez que $\hat S+\hat F_1+\hat F_2=1$. Comparez $\hat F_1$ à « $1-\mathrm{KM}$ » où la cause 2 est traitée comme une censure.

**Exercice 13 ⭐⭐⭐ (proportionnalité des risques sur des données réelles).** Reprenez les données de récidive de Rossi (5.3.9). Appliquez le test de score de proportionnalité des risques du 5.3.5 à chacune des sept covariables. Quelles variables posent problème ? Que feriez-vous ?

---

### Corrigés

**Corrigé 1.** (a) Moyenne de toutes les durées : $(4+7+9+12+15+20)/6\approx11{,}17$ mois ; moyenne des seuls clients partis : $(4+9+12)/3\approx8{,}33$ mois. Les deux sont biaisées (5.1.1). (b) Départs aux mois 4, 9 et 12. À 4 mois, 6 clients à risque : $5/6=0{,}833$. À 9 mois (le client censuré à 7 est sorti), 4 clients à risque : $0{,}833\times3/4=0{,}625$. À 12 mois, 3 clients à risque : $0{,}625\times2/3=0{,}417$. (c) La courbe passe sous 0,5 au mois 12 : **médiane = 12 mois**. (d) $\mathrm{RMST}(20)=4\times1+5\times0{,}833+3\times0{,}625+8\times0{,}417=4+4{,}167+1{,}875+3{,}333=13{,}375$ mois.

```python
import numpy as np
import pandas as pd
from scipy import stats

y1 = np.array([4, 7, 9, 12, 15, 20.]); d1 = np.array([1, 0, 1, 1, 0, 0])
tj1, n1, dj1, S1_, gw1 = kaplan_meier(y1, d1)
print("moyenne de toutes les durées :", round(y1.mean(), 2), "| des seuls partis :", round(y1[d1 == 1].mean(), 2))
print("S aux instants de départ", tj1, ":", S1_.round(4), "| à risque :", n1)
print("médiane :", tj1[S1_ <= 0.5][0], "| RMST(20) :", round(rmst(tj1, S1_, 20), 3))
```
<!--sortie-->
```text
moyenne de toutes les durées : 11.17 | des seuls partis : 8.33
S aux instants de départ [ 4.  9. 12.] : [0.8333 0.625  0.4167] | à risque : [6 4 3]
médiane : 12.0 | RMST(20) : 13.375
```

**Corrigé 2.** (a) $H(t)=\int_0^t0{,}0008u\,du=0{,}0004\,t^2$, donc $S(t)=\exp(-0{,}0004\,t^2)$. (b) $S(24)=\exp(-0{,}0004\times576)=e^{-0{,}2304}\approx0{,}794$ ; la médiane vérifie $0{,}0004\,t^2=\ln2$, donc $t=\sqrt{\ln2/0{,}0004}\approx41{,}6$ mois. (c) Une Weibull a $H(t)=(t/\sigma)^k$ : on lit $k=2$ et $\sigma^{-2}=0{,}0004$, soit $\sigma=50$ mois. La durée moyenne vaut $\sigma\,\Gamma(1+1/k)=50\,\Gamma(1{,}5)\approx44{,}3$ mois.

```python
from math import gamma, log
from scipy.integrate import quad
print("S(24) =", round(np.exp(-0.0004 * 24 ** 2), 4), "| médiane =", round(np.sqrt(log(2) / 0.0004), 2))
print("moyenne par la formule :", round(50 * gamma(1.5), 2), "| par intégration de S :", round(quad(lambda t: np.exp(-0.0004 * t ** 2), 0, np.inf)[0], 2))
```
<!--sortie-->
```text
S(24) = 0.7942 | médiane = 41.63
moyenne par la formule : 44.31 | par intégration de S : 44.31
```

**Corrigé 3.** (a) $\hat\lambda=D/E=40/1600=0{,}025$ par mois ; $\widehat{se}=\hat\lambda/\sqrt D=0{,}025/\sqrt{40}\approx0{,}00395$ ; IC95 : $0{,}025\pm1{,}96\times0{,}00395$, soit $[0{,}0173\ ;\ 0{,}0327]$. (b) $\hat S(24)=e^{-0{,}025\times24}=e^{-0{,}6}\approx0{,}549$ ; durée moyenne $1/\hat\lambda=40$ mois. (c) Wald : $z=(0{,}025-0{,}03)/0{,}00395\approx-1{,}26$, $p\approx0{,}21$. Rapport de vraisemblance : $2[\ell(\hat\lambda)-\ell(0{,}03)]=2[D\ln(\hat\lambda/0{,}03)-(\hat\lambda-0{,}03)E]=2[40\ln(0{,}8333)+8]\approx1{,}41$, $p\approx0{,}23$. Les deux tests concluent de la même façon : **on ne rejette pas** $\lambda=0{,}03$ (les données sont compatibles aussi avec ce taux).

```python
D, E = 40, 1600
lam = D / E; se = lam / np.sqrt(D)
print(f"lambda = {lam:.4f}, ET = {se:.5f}, IC95 = [{lam - 1.96 * se:.4f} ; {lam + 1.96 * se:.4f}]")
print(f"S(24) = {np.exp(-lam * 24):.4f}, durée moyenne = {1 / lam:.1f} mois")
z = (lam - 0.03) / se
lr = 2 * (D * np.log(lam / 0.03) - (lam - 0.03) * E)
print(f"Wald : z = {z:.3f}, p = {2 * stats.norm.sf(abs(z)):.3f} | rapport de vraisemblance : chi2 = {lr:.3f}, p = {stats.chi2.sf(lr, 1):.3f}")
```
<!--sortie-->
```text
lambda = 0.0250, ET = 0.00395, IC95 = [0.0173 ; 0.0327]
S(24) = 0.5488, durée moyenne = 40.0 mois
Wald : z = -1.265, p = 0.206 | rapport de vraisemblance : chi2 = 1.414, p = 0.234
```

**Corrigé 4.** Départs : mois 2 (1 départ, 8 à risque : $7/8$), mois 3 (2 départs, 7 à risque : $5/7$), mois 6 (1 départ, 4 à risque, car le client censuré à 5 est sorti : $3/4$), mois 9 (1 départ, 2 à risque : $1/2$). D'où $\hat S(2)=0{,}875$, $\hat S(3)=0{,}875\times5/7=0{,}625$, $\hat S(6)=0{,}625\times3/4=0{,}469$, $\hat S(9)=0{,}234$. Greenwood : $\sum\frac{d_j}{n_j(n_j-d_j)}=\frac1{8\times7}+\frac2{7\times5}+\frac1{4\times3}=0{,}0179+0{,}0571+0{,}0833=0{,}1583$ ; l'erreur standard de $\hat S(6)$ vaut $0{,}469\times\sqrt{0{,}1583}\approx0{,}187$. Intervalle log-log : $\hat S^{\exp(\pm1{,}96\sqrt{G}/|\ln\hat S|)}$ avec $1{,}96\times\sqrt{0{,}1583}/|\ln0{,}469|=0{,}780/0{,}757=1{,}03$, d'où $[0{,}469^{2{,}80}\ ;\ 0{,}469^{1/2{,}80}]\approx[0{,}12\ ;\ 0{,}76]$ : un intervalle immense, faute de données.

```python
y4 = np.array([2, 3, 3, 5, 6, 8, 9, 11.]); d4 = np.array([1, 1, 1, 0, 1, 0, 1, 0])
tj4, n4, dj4, S4, gw4 = kaplan_meier(y4, d4)
print(pd.DataFrame({"t_j": tj4, "à risque": n4, "départs": dj4, "S": S4.round(4), "somme Greenwood": gw4.round(4)}).to_string(index=False))
s, plan, log_, loglog = intervalles(6, tj4, S4, gw4)
print(f"S(6) = {s:.4f} ; ET = {s * np.sqrt(surv_at(6, tj4, gw4)):.4f} ; IC log-log = [{loglog[0]:.3f} ; {loglog[1]:.3f}]")
```
<!--sortie-->
```text
 t_j  à risque  départs      S  somme Greenwood
 2.0         8        1 0.8750           0.0179
 3.0         7        2 0.6250           0.0750
 6.0         4        1 0.4688           0.1583
 9.0         2        1 0.2344           0.6583
S(6) = 0.4688 ; ET = 0.1865 ; IC log-log = [0.120 ; 0.763]
```

**Corrigé 5.** Aux instants de départ 3, 5, 6, 7, 9 et 10, on a respectivement $n_j=10,9,8,7,5,4$ clients à risque, dont $n_{Aj}=5,4,4,3,2,2$ dans le groupe A. Chaque instant compte un seul départ : $E_{Aj}=n_{Aj}/n_j$ et $V_j=\frac{n_{Aj}}{n_j}(1-\frac{n_{Aj}}{n_j})$. Le code donne le détail :

```python
y5 = np.array([3, 6, 8, 10, 12, 5, 7, 9, 11, 13.]); d5 = np.array([1, 1, 0, 1, 0, 1, 1, 1, 0, 0])
g5 = np.array(["A"] * 5 + ["B"] * 5)
lignes, O1, E1, V1 = [], 0, 0.0, 0.0
for t in np.unique(y5[d5 == 1]):
    n_ = int(np.sum(y5 >= t)); nA = int(np.sum((y5 >= t) & (g5 == "A")))
    dd = int(np.sum((y5 == t) & (d5 == 1))); dA = int(np.sum((y5 == t) & (d5 == 1) & (g5 == "A")))
    e = dd * nA / n_; v = dd * (nA / n_) * (1 - nA / n_) * (n_ - dd) / (n_ - 1)
    lignes.append((t, n_, nA, dd, dA, round(e, 4), round(v, 4))); O1 += dA; E1 += e; V1 += v
print(pd.DataFrame(lignes, columns=["t_j", "n_j", "n_Aj", "d_j", "départ en A", "E_Aj", "V_j"]).to_string(index=False))
chi5 = (O1 - E1) ** 2 / V1
print(f"O_A = {O1}, E_A = {E1:.3f}, V = {V1:.3f}, chi2 = {chi5:.3f}, p = {stats.chi2.sf(chi5, 1):.3f}")
from statsmodels.duration.survfunc import survdiff
print("statsmodels : chi2 = %.3f, p = %.3f" % survdiff(y5, d5, g5))
```
<!--sortie-->
```text
 t_j  n_j  n_Aj  d_j  départ en A   E_Aj    V_j
 3.0   10     5    1            1 0.5000 0.2500
 5.0    9     4    1            0 0.4444 0.2469
 6.0    8     4    1            1 0.5000 0.2500
 7.0    7     3    1            0 0.4286 0.2449
 9.0    5     2    1            0 0.4000 0.2400
10.0    4     2    1            1 0.5000 0.2500
O_A = 3, E_A = 2.773, V = 1.482, chi2 = 0.035, p = 0.852
statsmodels : chi2 = 0.035, p = 0.852
```

Le groupe A a 3 départs pour 2,77 attendus : $\chi^2\approx0{,}03$, $p\approx0{,}85$. Avec dix clients, on ne peut rien conclure ; c'est tout à fait normal, et c'est la raison pour laquelle on ne compare pas des groupes aussi petits.

**Corrigé 6.** $\mathrm{RMST}_A(24)=6\times1+6\times0{,}8+6\times0{,}5+6\times0{,}3=6+4{,}8+3+1{,}8=15{,}6$ mois ; $\mathrm{RMST}_B(24)=9\times1+6\times0{,}9+6\times0{,}7+3\times0{,}6=9+5{,}4+4{,}2+1{,}8=20{,}4$ mois. La différence est de **4,8 mois** : en moyenne, sur les 24 premiers mois, un client de la campagne B reste 4,8 mois de plus dans la clientèle qu'un client de la campagne A. Contrairement au rapport de risques, cette quantité s'interprète sans hypothèse de proportionnalité et se lit directement en unités de temps (ou, multipliée par la marge mensuelle, en dinars).

```python
tjA, SA = np.array([6, 12, 18.]), np.array([0.8, 0.5, 0.3])
tjB, SB = np.array([9, 15, 21.]), np.array([0.9, 0.7, 0.6])
print("RMST(24) A :", round(rmst(tjA, SA, 24), 2), "| B :", round(rmst(tjB, SB, 24), 2), "| différence :", round(rmst(tjB, SB, 24) - rmst(tjA, SA, 24), 2))
```
<!--sortie-->
```text
RMST(24) A : 15.6 | B : 20.4 | différence : 4.8
```

**Corrigé 7.** (a) $\mathrm{HR}=e^{\hat\beta}$, IC $=e^{\hat\beta\pm1{,}96\,se}$, $z=\hat\beta/se$ : offre $0{,}670$ ($[0{,}590\ ;\ 0{,}761]$, $z=-6{,}15$) ; âge $0{,}986$ ($[0{,}981\ ;\ 0{,}992]$, $z=-4{,}53$) ; Instagram $1{,}887$ ($[1{,}60\ ;\ 2{,}22]$, $z=7{,}56$). (b) $e^{10\times(-0{,}0136)}\approx0{,}873$ : dix ans de plus réduisent le risque d'environ 13 %. (c) Les effets se multiplient : $e^{-0{,}40+0{,}635}=e^{0{,}235}\approx1{,}26$ (le canal Instagram l'emporte sur l'offre). (d) $S(t\mid x)=S_0(t)^{\exp(x^\top\beta)}$ : $0{,}80^{0{,}670}\approx0{,}861$. (e) $\hat\beta=-\hat\gamma/\hat\sigma=-0{,}35/0{,}74\approx-0{,}473$, soit $\mathrm{HR}=e^{-0{,}473}\approx0{,}623$.

```python
b = np.array([-0.40, -0.0136, 0.635]); se_ = np.array([0.065, 0.0030, 0.084])
print(pd.DataFrame({"HR": np.exp(b), "IC bas": np.exp(b - 1.96 * se_), "IC haut": np.exp(b + 1.96 * se_), "z": b / se_}, index=["offre", "age", "Instagram"]).round(3).to_string())
print("+10 ans :", round(np.exp(10 * b[1]), 3), "| Instagram avec offre / Boutique sans offre :", round(np.exp(b[0] + b[2]), 3))
print("S(24) avec offre :", round(0.80 ** np.exp(b[0]), 3), "| HR depuis AFT :", round(np.exp(-0.35 / 0.74), 3))
```
<!--sortie-->
```text
              HR  IC bas  IC haut      z
offre      0.670   0.590    0.761 -6.154
age        0.986   0.981    0.992 -4.533
Instagram  1.887   1.601    2.225  7.560
+10 ans : 0.873 | Instagram avec offre / Boutique sans offre : 1.265
S(24) avec offre : 0.861 | HR depuis AFT : 0.623
```

**Corrigé 8.** Dans l'analyse (a), le cadeau n'est donné qu'à ceux qui ont **survécu** jusqu'au mois 6 : ils ont une avance garantie, et le modèle y voit un effet protecteur qui n'existe pas. Dans l'analyse (b), le cadeau est une variable qui passe de 0 à 1 au mois 6 (deux épisodes pour les clients concernés), et seuls les clients **présents au mois 6** sont comparés entre eux.

```python
from statsmodels.duration.hazard_regression import PHReg

rng = np.random.default_rng(8)
N = 2000
T = rng.exponential(1 / 0.02, N)
C = rng.uniform(18, 48, N)
Y, D = np.minimum(T, C), (T <= C).astype(int)
cadeau = (Y > 6) & (rng.random(N) < 0.5)
naif = PHReg(Y, cadeau.astype(float)[:, None], status=D, ties="efron").fit()
porteurs = np.where(cadeau)[0]
debut = np.concatenate([np.zeros(N), np.full(len(porteurs), 6.0)])
fin = np.concatenate([np.where(cadeau, 6.0, Y), Y[porteurs]])
statut = np.concatenate([np.where(cadeau, 0, D), D[porteurs]])
x_tv = np.concatenate([np.zeros(N), np.ones(len(porteurs))])
juste = PHReg(fin, x_tv[:, None], status=statut, entry=debut, ties="efron").fit()
for nom, m in (("naïve (variable fixe)", naif), ("correcte (dépend du temps)", juste)):
    print(f"{nom:<28} HR = {np.exp(m.params[0]):.2f}  IC95 [{np.exp(m.params[0] - 1.96 * m.bse[0]):.2f} ; {np.exp(m.params[0] + 1.96 * m.bse[0]):.2f}]")
```
<!--sortie-->
```text
naïve (variable fixe)        HR = 0.64  IC95 [0.56 ; 0.74]
correcte (dépend du temps)   HR = 1.00  IC95 [0.86 ; 1.16]
```

L'analyse naïve conclut à un effet protecteur net (un HR bien inférieur à 1), l'analyse correcte à un effet nul (HR proche de 1, intervalle contenant 1) : c'est le **biais d'immortalité**.

**Corrigé 9.** (a) Si $S(t)=\exp[-(t/\sigma)^k]$, alors $\ln(-\ln S)=k\ln t-k\ln\sigma$ : la pente de la droite est $k$. (b) Le maximum de vraisemblance sans covariable est l'estimation de $k=1/\hat\sigma$ dans `ajuster` avec une seule colonne de 1.

```python
c = pd.read_csv("donnees/clients.csv")
y, d = c["duree_mois"].to_numpy(), c["churn"].to_numpy()
tj_, _, _, S_, _ = kaplan_meier(y, d)
garde = (tj_ >= 6) & (tj_ <= 60)
pente, ord_, r, _, _ = stats.linregress(np.log(tj_[garde]), np.log(-np.log(S_[garde])))
mv = ajuster("weibull", y, d, np.ones((len(y), 1)))
print(f"forme par le graphique de Weibull : k = {pente:.3f} (r = {r:.3f}) | forme par maximum de vraisemblance : k = {1 / np.exp(mv['theta'][-1]):.3f}")
```
<!--sortie-->
```text
forme par le graphique de Weibull : k = 1.296 (r = 1.000) | forme par maximum de vraisemblance : k = 1.281
```

Les deux méthodes donnent une forme voisine de 1,3 (1,30 et 1,28) et légèrement inférieure à la vraie valeur 1,35. La raison est celle du 5.4.7 : en **ignorant les covariables** (offre, canal, âge, facteur de service non observé), le risque de la population est un mélange de risques individuels, dont la croissance apparente est plus lente. L'ajout des covariables mesurées dans le modèle du 5.4.3 faisait passer la forme à 1,32, et l'ajout du facteur non observé (modèle « oracle » du 5.4.7) à 1,40 : la vraie valeur (1,35) n'est approchée, à l'erreur d'échantillonnage près, que si l'on tient compte de *toutes* les covariables, y compris celles qu'on ne mesure pas. Les deux méthodes d'estimation (graphique, maximum de vraisemblance) s'accordent entre elles ; c'est le *modèle* qui est incomplet, pas la méthode.

**Corrigé 10.** (a) En $\beta=0$, $e^{\beta x_k}=1$ : la moyenne pondérée de $x$ dans l'ensemble à risque $R_j$ est la proportion $n_{1j}/n_j$ de clients du groupe 1. Le score est $\sum_j\sum_{i\text{ parti en }t_j}\big(x_i-n_{1j}/n_j\big)=\sum_j\big(d_{1j}-d_j\,n_{1j}/n_j\big)=O_1-E_1$. (b) L'information en $\beta=0$ est $\sum_{i}\mathrm{Var}_{R_i}(x)=\sum_i\frac{n_{1}}{n}(1-\frac{n_{1}}{n})$ (somme sur *chaque* départ), alors que le log-rank utilise la variance hypergéométrique, avec le facteur $\frac{n_j-d_j}{n_j-1}$ qui corrige les départs simultanés. Les deux coïncident exactement quand il n'y a **jamais** d'ex aequo.

```python
off = c["offre_bienvenue"].to_numpy().astype(float)
U0, I0 = score_info(0.0, y, d, off)                       # fonction du 5.3.2 : boucle sur chaque départ (ex aequo à la Breslow)
O, E, chi_lr, _, _ = logrank(y, d, off)
print(f"Cox : score U = {U0:.3f}, information I = {I0:.3f}, U²/I = {U0 ** 2 / I0:.3f}")
print(f"log-rank : O1 - E1 = {O[1] - E[1]:.3f}, chi2 = {chi_lr:.3f}")
```
<!--sortie-->
```text
Cox : score U = -92.383, information I = 240.231, U²/I = 35.527
log-rank : O1 - E1 = -92.383, chi2 = 35.535
```

Le score est exactement $O_1-E_1$ (même valeur, signe compris, puisque $x=1$ désigne le groupe avec offre), et les deux statistiques ne diffèrent que de 0,008 sur 35,5 : la différence vient de la correction des ex aequo dans la variance.

**Corrigé 11.** Le gain actualisé de l'offre vaut $\Delta=\sum_t(S_1(t)-S_0(t))(1+r)^{-t}$ « mois de présence actualisés » ; l'offre est rentable si $m\,\Delta>25$, c'est-à-dire $m>m^\star=25/\Delta$.

```python
cout = 25.0
for r in (0.01, 0.02):
    v = (1 + r) ** (-mois)                                # `mois`, S0 et S1 viennent du 5.4.5
    delta = np.sum((S1 - S0) * v)
    print(f"taux {100 * r:.0f} %/mois : gain en mois de présence actualisés = {delta:.3f} -> marge de rentabilité m* = {cout / delta:.2f} DT/mois")
```
<!--sortie-->
```text
taux 1 %/mois : gain en mois de présence actualisés = 6.663 -> marge de rentabilité m* = 3.75 DT/mois
taux 2 %/mois : gain en mois de présence actualisés = 4.124 -> marge de rentabilité m* = 6.06 DT/mois
```

Avec une actualisation de 1 % par mois, l'offre devient rentable dès que la marge mensuelle par client actif dépasse environ **3,75 DT** ; avec 2 %, il faut environ **6 DT**. L'offre est donc beaucoup moins coûteuse à justifier si la marge est élevée : c'est la lecture pratique du tableau de sensibilité du 5.4.5.

**Corrigé 12.** Instants de sortie : 1, 2, 3, 5, 6, 9 (les censures aux mois 4 et 7 réduisent seulement les ensembles à risque). Aux mois 1 ($n=8$) : $d_1=1$ ; 2 ($n=7$) : $d_2=1$ ; 3 ($n=6$) : $d_1=1$ ; 5 ($n=4$) : $d_2=1$ ; 6 ($n=3$) : $d_1=1$ ; 9 ($n=1$) : $d_2=1$. On applique $\hat F_k(t)=\sum\hat S(t_j^-)\,d_{kj}/n_j$.

```python
y12 = np.array([1, 2, 3, 4, 5, 6, 7, 9.]); c12 = np.array([1, 2, 1, 0, 2, 1, 0, 2])
tj12, S12, (F1_12, F2_12) = incidence_cumulee(y12, c12)
print(pd.DataFrame({"t_j": tj12, "S": S12, "F1": F1_12, "F2": F2_12, "S + F1 + F2": S12 + F1_12 + F2_12}).round(4).to_string(index=False))
tj_n12, S_n12, (F1_naif12,) = incidence_cumulee(y12, np.where(c12 == 1, 1, 0))
print("1 - KM (cause 2 traitée comme censure), aux instants de la cause 1 :", (1 - S_n12).round(4), "| F1 correcte au dernier instant de cause 1 :", round(F1_12[-2], 4))
```
<!--sortie-->
```text
 t_j      S     F1     F2  S + F1 + F2
 1.0 0.8750 0.1250 0.0000          1.0
 2.0 0.7500 0.1250 0.1250          1.0
 3.0 0.6250 0.2500 0.1250          1.0
 5.0 0.4688 0.2500 0.2812          1.0
 6.0 0.3125 0.4062 0.2812          1.0
 9.0 0.0000 0.4062 0.5938          1.0
1 - KM (cause 2 traitée comme censure), aux instants de la cause 1 : [0.125  0.2708 0.5139] | F1 correcte au dernier instant de cause 1 : 0.4062
```

La somme $\hat S+\hat F_1+\hat F_2$ vaut 1 à chaque instant. À 6 mois, la probabilité de départ volontaire est $\hat F_1(6)=0{,}406$ ; en traitant la cause 2 comme une censure, on obtiendrait « $1-\mathrm{KM}$ » $=0{,}514$, soit 11 points de trop : la compétition des fermetures forcées (aux mois 2, 5 et 9) est ignorée.

**Corrigé 13.** On applique `test_ph` à l'ajustement de Cox des données de Rossi (la fonction `cox_ph` du 5.3.3 accepte n'importe quelle matrice de covariables).

```python
from lifelines.datasets import load_rossi

rossi = load_rossi()
Xr = rossi.drop(columns=["week", "arrest"])
fit_r = cox_ph(rossi["week"].to_numpy(), rossi["arrest"].to_numpy(), Xr.to_numpy())
chi_r, chi_glob_r = test_ph(rossi["week"].to_numpy(), rossi["arrest"].to_numpy(), Xr.to_numpy(), fit_r)
out = pd.DataFrame({"HR (Breslow)": np.exp(fit_r["beta"]), "chi2 PH": chi_r, "p": stats.chi2.sf(chi_r, 1)}, index=Xr.columns)
print(out.round(3).to_string())
print(f"test global : chi2 = {chi_glob_r:.2f} (7 ddl), p = {stats.chi2.sf(chi_glob_r, 7):.3f}")
```
<!--sortie-->
```text
      HR (Breslow)  chi2 PH      p
fin          0.685    1.371  0.242
age          0.944    0.893  0.345
race         1.369    2.245  0.134
wexp         0.860    4.128  0.042
mar          0.649    0.089  0.765
paro         0.919    0.021  0.886
prio         1.095    1.618  0.203
test global : chi2 = 10.93 (7 ddl), p = 0.142
```

La proportionnalité est plausible pour six des sept covariables. Seule l'expérience professionnelle (`wexp`) a une p-valeur inférieure à 0,05 ($p=0{,}042$), et le test **global** ne rejette rien ($p=0{,}14$). Avec sept tests, obtenir une p-valeur à 0,04 arrive souvent par hasard (volume I, section 3.5.5) : ce n'est pas une preuve de violation. La démarche prudente : tracer le graphique log-log de `wexp`, et si un doute subsiste, **stratifier** sur cette variable (elle est binaire) ou ajouter un effet qui dépend du temps, puis voir si les autres coefficients, en particulier celui de l'aide financière, bougent. S'ils ne bougent pas, la conclusion principale est robuste.

---

## Bilan du chapitre 5

Vous savez maintenant :

- **reconnaître la censure** et expliquer pourquoi la moyenne des durées, la moyenne des seuls événements et la proportion d'événements sont toutes **biaisées** ; distinguer censure à droite, à gauche, par intervalle et **troncature** (entrée tardive) ; énoncer l'hypothèse de **censure non informative** ;
- manier les trois fonctions d'une durée, **survie** $S(t)$, **risque instantané** $h(t)$ et **risque cumulé** $H(t)$, reliées par $S=e^{-H}$, et la formule $E[T]=\int_0^\infty S(t)\,dt$ ;
- écrire la **vraisemblance avec censure** $\ell=\sum[\delta_i\ln h(y_i)-H(y_i)]$ et en tirer le taux constant $\hat\lambda=D/\sum y_i$ ;
- calculer l'**estimateur de Kaplan-Meier** à la main et par code, ses intervalles de confiance (**Greenwood**, log-log), la **médiane** et la **durée moyenne restreinte** ; comparer des groupes par le **log-rank** et ses variantes ;
- ajuster et interpréter un **modèle de Cox** : vraisemblance partielle, rapports de risques, **ex aequo** (Breslow, Efron), **vérification de la proportionnalité** (graphique log-log, test de score de Grambsch-Therneau), **covariables dépendant du temps** et **biais d'immortalité**, courbes de survie prédites, **indice de concordance** ;
- ajuster des **modèles paramétriques** (Weibull, log-normal, log-logistique) par maximum de vraisemblance, lire un **facteur d'accélération**, passer de l'AFT aux risques proportionnels ($\beta=-\gamma/\sigma$ pour la Weibull), choisir par l'**AIC** et les **résidus de Cox-Snell**, **extrapoler** et calculer une **valeur vie client** avec une analyse de sensibilité ;
- (en option) traiter des **risques concurrents** : incidences cumulées d'**Aalen-Johansen**, pourquoi « 1 − KM » est faux, **modèle par cause** contre **Fine et Gray**.

Deux messages à garder en mémoire. **Un chiffre de survie n'a de sens qu'avec son traitement de la censure et ses hypothèses** (non informative, proportionnalité, forme de la loi) : on les énonce, on les vérifie quand c'est possible, on mesure leur influence sinon. Et **la randomisation reste l'arme la plus solide** : l'offre de bienvenue a un effet causal mesurable parce qu'elle a été attribuée au hasard ; pour les variables non randomisées (le canal, l'âge), les résultats sont des **associations**.

Le chapitre 6 change de perspective : au lieu de chercher *une* estimation et son incertitude, la **statistique bayésienne** attribue une **loi de probabilité** aux paramètres eux-mêmes, et la **simulation** (Monte-Carlo, MCMC) permet de calculer ce que l'algèbre ne sait pas faire.
