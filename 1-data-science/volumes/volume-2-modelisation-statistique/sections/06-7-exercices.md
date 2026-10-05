## 6.7 Exercices du chapitre 6

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 8, 9 et 10 réutilisent les fonctions `metropolis_1d` et `ess` définies en 6.3. Les exercices 13 et 14 se rapportent aux sections optionnelles 6.5 et 6.6.

### Énoncés

**Exercice 1 ⭐ (bêta-binomial).** la gérante teste un nouvel emballage : 3 clients sur 8 le jugent « excellent ». Avec l'a priori $\mathrm{Beta}(2,2)$ (« je pense plutôt autour de 50 % »), donnez (a) la loi a posteriori, (b) sa moyenne, (c) le poids de l'a priori dans cette moyenne, (d) la comparaison avec l'estimation du maximum de vraisemblance.

**Exercice 2 ⭐ (gamma-Poisson).** Le site reçoit 2, 4 et 1 commandes lors de trois soirées. A priori $\lambda\sim\mathrm{Gamma}(3;\ \text{taux }1)$ (moyenne 3 commandes par soirée). Donnez la loi a posteriori de $\lambda$, sa moyenne, et un intervalle de crédibilité à 95 %.

**Exercice 3 ⭐⭐ (normal-normal).** On modélise le log du panier avec $\sigma=0{,}35$ connu et l'a priori $\mathcal N(4{,}0;\ 0{,}5^2)$. À partir de combien d'observations le poids des données dans la moyenne a posteriori dépasse-t-il 90 % ? Calculez-le à la main, puis vérifiez avec le code.

**Exercice 4 ⭐⭐ (test A/B bayésien).** La version A d'une page convertit 30 visiteurs sur 100, la version B 42 sur 110. Avec des a priori $\mathrm{Beta}(1,1)$, calculez par simulation la probabilité que B soit meilleure que A, le gain attendu en points de pourcentage, et la probabilité que le gain dépasse 5 points. Comparez avec le test de proportions fréquentiste.

**Exercice 5 ⭐ (Monte-Carlo).** Soient $U_1,U_2$ uniformes indépendantes sur $[0,1]$. (a) Calculez à la main $\mathbb E[\max(U_1,U_2)]$. (b) Estimez-la par Monte-Carlo avec 100 000 tirages, avec son erreur type et son intervalle de confiance. (c) Estimez $P(U_1+U_2>1{,}5)$ et comparez avec la valeur exacte $1/8$.

**Exercice 6 ⭐⭐ (échantillonnage préférentiel).** Soit $X\sim\mathrm{Exp}(1)$. On veut $P(X>5)=e^{-5}$. (a) Estimez-la naïvement avec $n=10\,000$ tirages. (b) Utilisez la proposition « $5+\mathrm{Exp}(1)$ ». Que valent les poids ? Que remarquez-vous sur la variance de l'estimateur ?

**Exercice 7 ⭐⭐ (inversion).** La durée de vie $T$ (en mois) d'un abonnement suit une loi de Weibull de fonction de répartition $F(t)=1-\exp\bigl(-(t/\lambda)^k\bigr)$, avec $\lambda=24$ et $k=1{,}5$. (a) Déterminez $F^{-1}$. (b) Simulez 100 000 durées. (c) Vérifiez la médiane théorique et la moyenne théorique $\lambda\,\Gamma(1+1/k)$.

**Exercice 8 ⭐⭐ (Metropolis à la main).** On veut une chaîne sur trois états $\{1,2,3\}$ de loi stationnaire proportionnelle à $(1,2,1)$. La proposition choisit l'un des deux autres états avec probabilité $\tfrac12$. (a) Écrivez la matrice de transition de Metropolis. (b) Vérifiez le bilan détaillé. (c) Vérifiez par le code, et par simulation.

**Exercice 9 ⭐⭐ (Metropolis sur une échelle logarithmique).** Six semaines de commandes : 3, 5, 4, 6, 2, 5. Modèle : Poisson$(\lambda)$, a priori $\mathrm{Gamma}(2;\ \text{taux }0{,}5)$. (a) Donnez la loi a posteriori exacte. (b) Écrivez un Metropolis sur $\theta=\log\lambda$ (attention à la transformation de la densité) et comparez avec la loi exacte.

**Exercice 10 ⭐⭐ (diagnostics).** Une chaîne autorégressive $x_t=\varphi\,x_{t-1}+\sqrt{1-\varphi^2}\,\varepsilon_t$ ($\varepsilon_t\sim\mathcal N(0,1)$) a pour loi stationnaire $\mathcal N(0,1)$ et pour autocorrélation $\rho_k=\varphi^k$. (a) Montrez que son ESS théorique vaut environ $n\,\dfrac{1-\varphi}{1+\varphi}$. (b) Pour $\varphi=0{,}9$ et $n=20\,000$, comparez avec l'ESS calculée. (c) Quatre chaînes de $\varphi=0{,}99$ lancées de $-10,-3,3,10$ : calculez le $\widehat R$ avec et sans élimination des 300 premiers points.

**Exercice 11 ⭐⭐ (vérification prédictive).** Modélisez les paniers des acheteurs de la boutique (a) par une loi normale sur le panier en €, (b) par une loi normale sur le **logarithme** du panier. Avec la statistique-test « asymétrie » (skewness) et le plus petit panier, quel modèle passe la vérification prédictive a posteriori ?

**Exercice 12 ⭐⭐ (facteur de Bayes).** Neuf clients sur dix préfèrent le nouvel emballage. $H_0$ : $\theta=0{,}5$ ; $H_1$ : $\theta\sim\mathcal U(0,1)$. Calculez à la main $\mathrm{BF}_{10}$, comparez à la p-valeur exacte bilatérale, puis calculez la probabilité a posteriori de $H_1$ si l'on pense au départ qu'il y a 1 chance sur 4 que l'emballage ait un effet.

**Exercice 13 ⭐⭐ (valeurs extrêmes).** Pour des retards de colis, on a choisi le seuil $u=5$ jours ; 5 % des colis le dépassent ($\zeta_u=0{,}05$) et la loi des excès est GPD de $\xi=0{,}2$ et $\sigma_u=2$ jours. (a) Calculez à la main le retard dépassé en moyenne une fois tous les 1 000 colis. (b) Et tous les 10 000 colis ? (c) Que devient (b) si $\xi=0{,}4$ au lieu de 0,2 ? Qu'en concluez-vous ?

**Exercice 14 ⭐⭐⭐ (dépendance de queue de Clayton).** (a) Démontrez que, pour la copule de Clayton, $P(V\le q\mid U\le q)=(2-q^{\theta})^{-1/\theta}$, puis que cette quantité tend vers $2^{-1/\theta}$ quand $q\to0$. (b) Vérifiez numériquement avec $\theta=2$ pour $q=0{,}1;\,0{,}01;\,0{,}001$. (c) Par la formule de survie, que vaut $P(U>1-q,\,V>1-q)$ pour la copule de Clayton *retournée* ? Comparez avec une copule gaussienne de même tau.

### Corrigés

**Corrigé 1.** (a) Succès $y=3$, échecs $n-y=5$ : $\mathrm{Beta}(2+3,\,2+5)=\mathrm{Beta}(5,7)$. (b) Moyenne $5/12=0{,}4167$. (c) Le poids de l'a priori est $\dfrac{a+b}{a+b+n}=\dfrac4{4+8}=\dfrac13$ : un tiers de l'a priori (moyenne 0,5), deux tiers des données (fréquence 0,375) : $\tfrac13\times0{,}5+\tfrac23\times0{,}375=0{,}4167$ ✓. (d) Le maximum de vraisemblance est $3/8=0{,}375$ ; l'a posteriori est **tiré vers 0,5**. Avec 8 observations seulement, l'a priori compte beaucoup (voir 6.1.6).

```python
import numpy as np
import pandas as pd
from scipy import stats

post = stats.beta(2 + 3, 2 + 5)
print(f"a posteriori Beta(5, 7) : moyenne {post.mean():.4f} | IC95 [{post.ppf(0.025):.3f} ; {post.ppf(0.975):.3f}]")
print(f"poids de l'a priori : {4 / 12:.3f} | EMV : {3 / 8:.3f} | moyenne pondérée : {4 / 12 * 0.5 + 8 / 12 * 3 / 8:.4f}")
```
<!--sortie-->
```text
a posteriori Beta(5, 7) : moyenne 0.4167 | IC95 [0.167 ; 0.692]
poids de l'a priori : 0.333 | EMV : 0.375 | moyenne pondérée : 0.4167
```

**Corrigé 2.** $\sum y_i=7$, $n=3$ : $\lambda\mid y\sim\mathrm{Gamma}(3+7;\ 1+3)=\mathrm{Gamma}(10;\ \text{taux }4)$, de moyenne $10/4=2{,}5$ commandes par soirée. Elle est **comprise entre la moyenne a priori (3) et celle des données ($7/3=2{,}33$)**, comme il se doit pour un compromis ; elle est plus proche des données car celles-ci pèsent $3/4$ (3 observations contre un a priori valant « 1 observation » : le taux de l'a priori est 1).

```python
post = stats.gamma(a=10, scale=1 / 4)
print(f"Gamma(10, taux 4) : moyenne {post.mean():.3f} | IC95 [{post.ppf(0.025):.3f} ; {post.ppf(0.975):.3f}]")
```
<!--sortie-->
```text
Gamma(10, taux 4) : moyenne 2.500 | IC95 [1.199 ; 4.271]
```

**Corrigé 3.** Le poids des données est $w=\dfrac{n/\sigma^2}{1/\tau_0^2+n/\sigma^2}$. On veut $w>0{,}9\iff n/\sigma^2>9/\tau_0^2\iff n>9\sigma^2/\tau_0^2=9\times0{,}1225/0{,}25=4{,}41$. Il faut donc **$n\ge5$** observations (avec $n=5$ : $w=0{,}911$, comme en 6.1.8). L'a priori est donc déjà « oublié » à 90 % avec cinq clients seulement : il est assez large par rapport à $\sigma$.

```python
sigma, tau0 = 0.35, 0.5
for n in range(1, 8):
    w = (n / sigma**2) / (1 / tau0**2 + n / sigma**2)
    print(f"n = {n} : poids des données = {w:.3f}" + ("   <- premier n au-dessus de 90 %" if w > 0.9 and (n == 1 or (((n - 1) / sigma**2) / (1 / tau0**2 + (n - 1) / sigma**2)) <= 0.9) else ""))
```
<!--sortie-->
```text
n = 1 : poids des données = 0.671
n = 2 : poids des données = 0.803
n = 3 : poids des données = 0.860
n = 4 : poids des données = 0.891
n = 5 : poids des données = 0.911   <- premier n au-dessus de 90 %
n = 6 : poids des données = 0.924
n = 7 : poids des données = 0.935
```

**Corrigé 4.** A : $\mathrm{Beta}(31,71)$, B : $\mathrm{Beta}(43,69)$. On tire dans chaque loi et on compare.

```python
rng = np.random.default_rng(690)
S = 400_000
pA = stats.beta(1 + 30, 1 + 70).rvs(S, random_state=rng)
pB = stats.beta(1 + 42, 1 + 68).rvs(S, random_state=rng)
gain = pB - pA
print(f"P(B > A) = {(gain > 0).mean():.4f} | gain moyen = {100 * gain.mean():.1f} points | P(gain > 5 points) = {(gain > 0.05).mean():.4f}")
print(f"IC de crédibilité à 95 % du gain : [{100 * np.percentile(gain, 2.5):.1f} ; {100 * np.percentile(gain, 97.5):.1f}] points")

from statsmodels.stats.proportion import proportions_ztest
z, p = proportions_ztest([42, 30], [110, 100])
print(f"test fréquentiste : z = {z:.3f}, p-valeur bilatérale = {p:.4f} (unilatérale : {p / 2:.4f})")
```
<!--sortie-->
```text
P(B > A) = 0.8925 | gain moyen = 8.0 points | P(gain > 5 points) = 0.6800
IC de crédibilité à 95 % du gain : [-4.7 ; 20.6] points
test fréquentiste : z = 1.248, p-valeur bilatérale = 0.2122 (unilatérale : 0.1061)
```

La probabilité bayésienne que B soit meilleure est de 89 % ; le test fréquentiste donne une p-valeur bilatérale de 0,21 (unilatérale 0,106), **non significative** à 5 %. Remarquez que $1-0{,}106=0{,}894$ est presque égal à la probabilité bayésienne de 0,8925 : avec un a priori plat et des données assez abondantes, la p-valeur unilatérale et la probabilité a posteriori de l'hypothèse « opposée » **coïncident presque** (c'est un résultat classique pour les proportions). Mais **la p-valeur ne dit pas « la probabilité que B soit meilleure »** (volume I, section 3.5.2), alors que la probabilité bayésienne le dit : « 89 % de chances que B soit meilleure, gain probable de 8 points, avec une probabilité de 68 % que le gain dépasse 5 points ». L'intervalle de crédibilité à 95 % du gain, [−4,7 ; +20,6] points, est très large : avec une centaine de visiteurs par version, on ne sait pas grand-chose, et c'est exactement ce que dit le test non significatif.

**Corrigé 5.** (a) $P(\max\le x)=x^2$, de densité $2x$ : $\mathbb E[\max]=\int_0^1x\cdot2x\,dx=2/3$. (b), (c) :

```python
rng = np.random.default_rng(691)
n = 100_000
u = rng.random((n, 2))
g = u.max(axis=1)
est, se = g.mean(), g.std(ddof=1) / np.sqrt(n)
print(f"E[max] estimée : {est:.4f}  ± {1.96 * se:.4f} (IC95) | exacte : {2 / 3:.4f}")
h = (u.sum(axis=1) > 1.5)
est, se = h.mean(), h.std(ddof=1) / np.sqrt(n)
print(f"P(U1 + U2 > 1,5) estimée : {est:.4f} ± {1.96 * se:.4f} | exacte : {1 / 8:.4f}")
```
<!--sortie-->
```text
E[max] estimée : 0.6682  ± 0.0015 (IC95) | exacte : 0.6667
P(U1 + U2 > 1,5) estimée : 0.1265 ± 0.0021 | exacte : 0.1250
```

L'intervalle de confiance de Monte-Carlo contient la valeur exacte dans chaque cas (dans 95 % des répétitions de l'expérience, en moyenne).

**Corrigé 6.** (a) L'estimateur naïf a une variance $p(1-p)/n\approx6{,}7\times10^{-7}$, soit un écart-type de $8{,}2\times10^{-4}$ pour une valeur de $6{,}7\times10^{-3}$ : environ 12 % d'erreur relative. (b) Tirons $Y=5+E$, $E\sim\mathrm{Exp}(1)$ (densité $h(y)=e^{-(y-5)}$ pour $y>5$). Alors $f(y)/h(y)=e^{-y}/e^{-(y-5)}=e^{-5}$ **pour tout $y>5$** : tous les tirages sont dans la zone d'intérêt (indicatrice égale à 1) et **tous les poids valent $e^{-5}$**. L'estimateur vaut donc $e^{-5}$ **exactement**, avec une **variance nulle** : c'est la proposition idéale, qui est *proportionnelle à $g\times f$*. En pratique, on ne la connaît pas (sinon on ne simulerait pas), mais on s'en approche.

```python
rng = np.random.default_rng(692)
n = 10_000
naif = (rng.exponential(1, n) > 5).mean()
y = 5 + rng.exponential(1, n)
poids = np.exp(-y) / np.exp(-(y - 5))                      # f / h
pref = np.mean((y > 5) * poids)
print(f"exact : {np.exp(-5):.6f} | naïf : {naif:.6f} | préférentiel : {pref:.6f} | poids min / max : {poids.min():.6f} / {poids.max():.6f}")
```
<!--sortie-->
```text
exact : 0.006738 | naïf : 0.006700 | préférentiel : 0.006738 | poids min / max : 0.006738 / 0.006738
```

**Corrigé 7.** (a) On résout $u=1-\exp(-(t/\lambda)^k)$ : $t=\lambda\bigl[-\ln(1-u)\bigr]^{1/k}$. (b) et (c) : la médiane théorique est $\lambda(\ln2)^{1/k}$.

```python
from math import gamma, log
lam, k = 24, 1.5
rng = np.random.default_rng(693)
u = rng.random(100_000)
t = lam * (-np.log(1 - u)) ** (1 / k)
print(f"médiane simulée {np.median(t):.3f} | théorique {lam * log(2) ** (1 / k):.3f}")
print(f"moyenne simulée {t.mean():.3f} | théorique {lam * gamma(1 + 1 / k):.3f}")
print(f"P(T > 36) simulée {np.mean(t > 36):.4f} | théorique {np.exp(-(36 / lam) ** k):.4f}")
```
<!--sortie-->
```text
médiane simulée 18.892 | théorique 18.797
moyenne simulée 21.713 | théorique 21.666
P(T > 36) simulée 0.1587 | théorique 0.1593
```

**Corrigé 8.** Cible $\pi=(0{,}25;\,0{,}5;\,0{,}25)$. (a) $P_{12}=\tfrac12\min(1,2)=\tfrac12$ ; $P_{13}=\tfrac12\min(1,1)=\tfrac12$ ; $P_{11}=0$. Depuis 2 : $P_{21}=\tfrac12\cdot\tfrac12=\tfrac14$, $P_{23}=\tfrac14$, $P_{22}=\tfrac12$. Depuis 3 : $P_{31}=\tfrac12$, $P_{32}=\tfrac12\min(1,2)=\tfrac12$, $P_{33}=0$. (b) $\pi_1P_{12}=0{,}25\times\tfrac12=0{,}125=\pi_2P_{21}=0{,}5\times\tfrac14$ ✓ ; $\pi_1P_{13}=0{,}125=\pi_3P_{31}$ ✓ ; $\pi_2P_{23}=0{,}5\times\tfrac14=0{,}125=\pi_3P_{32}=0{,}25\times\tfrac12$ ✓.

```python
poids = np.array([1.0, 2.0, 1.0]); pi = poids / poids.sum(); k3 = 3
P = np.zeros((k3, k3))
for i in range(k3):
    for j in range(k3):
        if i != j:
            P[i, j] = 0.5 * min(1, poids[j] / poids[i])
    P[i, i] = 1 - P[i].sum()
print(P)
print("bilan détaillé (écart max) :", np.abs(pi[:, None] * P - (pi[:, None] * P).T).max())
rng = np.random.default_rng(694)
etat, compte = 0, np.zeros(3)
for _ in range(60_000):
    etat = rng.choice(3, p=P[etat]); compte[etat] += 1
print("fréquences simulées :", (compte / 60_000).round(3), "| cible :", pi)
```
<!--sortie-->
```text
[[0.   0.5  0.5 ]
 [0.25 0.5  0.25]
 [0.5  0.5  0.  ]]
bilan détaillé (écart max) : 0.0
fréquences simulées : [0.251 0.5   0.249] | cible : [0.25 0.5  0.25]
```

**Corrigé 9.** (a) $\sum y=25$, $n=6$ : $\lambda\mid y\sim\mathrm{Gamma}(2+25;\ 0{,}5+6)=\mathrm{Gamma}(27;\ \text{taux }6{,}5)$, de moyenne $27/6{,}5=4{,}154$. (b) Si $\theta=\log\lambda$, la densité de $\theta$ est celle de $\lambda$ multipliée par le jacobien $|d\lambda/d\theta|=\lambda=e^\theta$. L'a posteriori **non normalisé** de $\theta$ est donc $\propto e^{(27-1)\theta}e^{-6{,}5e^{\theta}}\cdot e^{\theta}=e^{27\theta-6{,}5e^\theta}$ : $\log\pi(\theta)=27\theta-6{,}5\,e^\theta$. **Oublier le jacobien est l'erreur classique** : on échantillonnerait alors une autre loi.

```python
def log_cible(theta):
    return 27 * theta - 6.5 * np.exp(theta)

rng = np.random.default_rng(695)
chaine, taux = metropolis_1d(log_cible, x0=np.log(4.0), n=30_000, pas=0.5, rng=rng)
lam_s = np.exp(chaine[2000:])
exacte = stats.gamma(a=27, scale=1 / 6.5)
print(f"taux d'acceptation {taux:.3f}")
print(f"MH : moyenne {lam_s.mean():.4f}, écart-type {lam_s.std():.4f}, quantiles 2,5 / 50 / 97,5 % {np.percentile(lam_s, [2.5, 50, 97.5]).round(3)}")
print(f"exact : moyenne {exacte.mean():.4f}, écart-type {exacte.std():.4f}, quantiles {exacte.ppf([0.025, 0.5, 0.975]).round(3)}")
```
<!--sortie-->
```text
taux d'acceptation 0.420
MH : moyenne 4.1457, écart-type 0.8114, quantiles 2,5 / 50 / 97,5 % [2.712 4.076 5.874]
exact : moyenne 4.1538, écart-type 0.7994, quantiles [2.737 4.103 5.861]
```

**Corrigé 10.** (a) $\mathrm{ESS}=n/\bigl(1+2\sum_{k\ge1}\rho_k\bigr)$ et $\sum_{k\ge1}\varphi^k=\dfrac\varphi{1-\varphi}$, donc $1+2\dfrac\varphi{1-\varphi}=\dfrac{1+\varphi}{1-\varphi}$ et $\mathrm{ESS}=n\dfrac{1-\varphi}{1+\varphi}$. Pour $\varphi=0{,}9$ : $n/19$, soit environ 1 053 sur 20 000. (b), (c) :

```python
def ar1(phi, n, x0, rng):
    x = np.empty(n); x[0] = x0
    for t in range(1, n):
        x[t] = phi * x[t - 1] + np.sqrt(1 - phi**2) * rng.standard_normal()
    return x

rng = np.random.default_rng(696)
x = ar1(0.9, 20_000, 0.0, rng)
print(f"ESS théorique {20_000 * (1 - 0.9) / (1 + 0.9):.0f} | ESS calculée {ess(x):.0f}")

chaines4 = np.array([ar1(0.99, 1500, x0, rng) for x0 in (-10, -3, 3, 10)])
print(f"R-chapeau avec les 1 500 points : {split_rhat(chaines4):.3f} | sans les 300 premiers : {split_rhat(chaines4[:, 300:]):.3f}")
print(f"ESS théorique par chaîne (phi = 0,99) : {1200 * (1 - 0.99) / (1 + 0.99):.0f} sur 1 200 points")
```
<!--sortie-->
```text
ESS théorique 1053 | ESS calculée 1111
R-chapeau avec les 1 500 points : 1.142 | sans les 300 premiers : 1.063
ESS théorique par chaîne (phi = 0,99) : 6 sur 1 200 points
```

L'ESS calculée est proche de la théorie. Pour $\varphi=0{,}99$, la chaîne est si lente que l'ESS d'une chaîne de 1 200 points est de l'ordre de 6 seulement : le $\widehat R$ **détecte le problème** (valeur nettement supérieure à 1,01, quoi qu'on fasse), parce que chaque chaîne n'a pas eu le temps de quitter son voisinage de départ. C'est exactement la situation où il faut **allonger** ou **reparamétriser**.

**Corrigé 11.** Données : les paniers des 449 acheteurs de la boutique. Sous le modèle normal avec a priori $p(\mu,\sigma^2)\propto1/\sigma^2$, la loi a posteriori est : $\sigma^2\mid y\sim(n-1)s^2/\chi^2_{n-1}$, puis $\mu\mid\sigma^2,y\sim\mathcal N(\bar y,\sigma^2/n)$, ce qui donne directement des tirages (sans MCMC).

```python
clients = pd.read_csv("donnees/clients.csv")
pan = clients[(clients["canal_acquisition"] == "Boutique") & (clients["panier_moyen"] > 0)]["panier_moyen"].to_numpy()

def ppc_normal(y_, graine, S=2000):
    rng = np.random.default_rng(graine)
    n_, ybar, s2 = len(y_), y_.mean(), y_.var(ddof=1)
    sig2 = (n_ - 1) * s2 / rng.chisquare(n_ - 1, S)
    mu = rng.normal(ybar, np.sqrt(sig2 / n_))
    yrep = rng.normal(mu[:, None], np.sqrt(sig2)[:, None], size=(S, n_))
    T = lambda a: np.c_[stats.skew(a, axis=-1), a.min(axis=-1)]
    To, Tr = T(y_[None, :])[0], T(yrep)
    return To, Tr, (Tr >= To).mean(axis=0)

for nom, donnees in (("normale sur le panier (€)", pan), ("normale sur le log du panier", np.log(pan))):
    To, Tr, pb = ppc_normal(donnees, 697)
    print(f"{nom:32s} asymétrie : observée {To[0]:6.3f}, répliques {Tr[:, 0].mean():6.3f} (p bayésien {pb[0]:.3f}) | "
          f"minimum : observé {To[1]:7.3f}, répliques {Tr[:, 1].mean():7.3f} (p bayésien {pb[1]:.3f})")
```
<!--sortie-->
```text
normale sur le panier (€)       asymétrie : observée  1.037, répliques  0.003 (p bayésien 0.000) | minimum : observé  25.530, répliques -11.756 (p bayésien 0.000)
normale sur le log du panier     asymétrie : observée  0.046, répliques  0.003 (p bayésien 0.360) | minimum : observé   3.240, répliques   3.094 (p bayésien 0.144)
```

Le modèle sur le panier brut échoue : les données ont une asymétrie de 1,04 (queue à droite) que le modèle symétrique ne reproduit jamais (asymétrie répliquée : 0,00 ; $p_B=0$), et il prédit des **paniers négatifs** (le minimum répliqué vaut en moyenne −11,8 €, ce qui est absurde), alors que le plus petit panier observé est de 25,5 €. Le modèle sur le logarithme (c'est-à-dire une loi log-normale pour le panier) passe les deux vérifications ($p_B=0{,}36$ pour l'asymétrie et $0{,}14$ pour le minimum). C'est la raison pour laquelle on modélise les montants positifs sur une échelle logarithmique.

**Corrigé 12.** $n=10$, $y=9$. $p(y\mid H_0)=\binom{10}9\,0{,}5^{10}=10/1024=0{,}00977$ ; $p(y\mid H_1)=1/11=0{,}0909$. $\mathrm{BF}_{10}=\dfrac{1/11}{10/1024}=\dfrac{1024}{110}=9{,}31$ : des données environ 9 fois plus probables sous $H_1$. La p-valeur exacte bilatérale est $2\bigl[\binom{10}9+\binom{10}{10}\bigr]/1024=22/1024=0{,}0215$. Avec une cote a priori de $\dfrac{1/4}{3/4}=\dfrac13$ en faveur de $H_1$, la cote a posteriori est $9{,}31\times\tfrac13=3{,}10$, soit une probabilité $3{,}10/4{,}10=0{,}756$ pour $H_1$ : on a gagné en crédibilité mais on est loin de la certitude, alors que la p-valeur de 0,02 « rejette $H_0$ au seuil de 5 % ». C'est la différence de langage entre « rejeter » et « mettre à jour ses croyances ».

```python
from scipy.special import comb
m0 = comb(10, 9) * 0.5**10
m1 = 1 / 11
bf = m1 / m0
print(f"p(y|H0) = {m0:.5f} | p(y|H1) = {m1:.5f} | BF10 = {bf:.3f} (à la main : 1024/110 = {1024 / 110:.3f})")
print(f"p-valeur exacte bilatérale : {stats.binomtest(9, 10, 0.5).pvalue:.4f} (à la main : 22/1024 = {22 / 1024:.4f})")
cote_post = bf * (0.25 / 0.75)
print(f"cote a posteriori {cote_post:.3f} -> P(H1 | données) = {cote_post / (1 + cote_post):.3f}")
```
<!--sortie-->
```text
p(y|H0) = 0.00977 | p(y|H1) = 0.09091 | BF10 = 9.309 (à la main : 1024/110 = 9.309)
p-valeur exacte bilatérale : 0.0215 (à la main : 22/1024 = 0.0215)
cote a posteriori 3.103 -> P(H1 | données) = 0.756
```

**Corrigé 13.** On utilise $x_m=u+\dfrac{\sigma_u}\xi\bigl[(m\zeta_u)^\xi-1\bigr]$. (a) $m=1\,000$ : $m\zeta_u=50$, $50^{0{,}2}=e^{0{,}2\ln50}=e^{0{,}7824}=2{,}187$ ; $x=5+\dfrac2{0{,}2}(2{,}187-1)=5+10\times1{,}187=16{,}87$ jours. (b) $m=10\,000$ : $m\zeta_u=500$, $500^{0{,}2}=e^{0{,}2\ln500}=3{,}466$, donc $x=5+10\times2{,}466=29{,}66$ jours. (c) Avec $\xi=0{,}4$ : $x_{10\,000}=5+\dfrac2{0{,}4}\bigl(500^{0{,}4}-1\bigr)=5+5\times(12{,}01-1)=60{,}1$ jours. **Doubler $\xi$ double (à peu près) le niveau de retour à 10 000 colis** : une petite erreur sur l'indice de queue a une conséquence énorme sur l'extrapolation.

```python
def niveau_pot(m, xi, sc, u, zeta):
    return u + sc / xi * ((m * zeta) ** xi - 1)

for xi_ in (0.2, 0.4):
    print(f"xi = {xi_} : " + " | ".join(f"1 colis sur {m:>6,}: {niveau_pot(m, xi_, 2.0, 5.0, 0.05):6.2f} jours".replace(",", " ") for m in (1_000, 10_000)))
```
<!--sortie-->
```text
xi = 0.2 : 1 colis sur  1 000:  16.87 jours | 1 colis sur 10 000:  29.66 jours
xi = 0.4 : 1 colis sur  1 000:  23.91 jours | 1 colis sur 10 000:  60.06 jours
```

**Corrigé 14.** (a) $P(V\le q\mid U\le q)=\dfrac{C_\theta(q,q)}{q}=\dfrac{(2q^{-\theta}-1)^{-1/\theta}}q$. Or $(2q^{-\theta}-1)^{-1/\theta}=\bigl[q^{-\theta}(2-q^{\theta})\bigr]^{-1/\theta}=q\,(2-q^\theta)^{-1/\theta}$ ; en divisant par $q$ : $(2-q^\theta)^{-1/\theta}$. Quand $q\to0$, $q^\theta\to0$ (car $\theta>0$) et l'on obtient $2^{-1/\theta}$. $\square$ (c) Pour la Clayton retournée, $(U,V)=(1-U',1-V')$ avec $(U',V')$ de Clayton : $P(U>1-q,V>1-q)=P(U'<q,V'<q)=C_\theta(q,q)=(2q^{-\theta}-1)^{-1/\theta}$. Avec $\theta=2$ ($\tau=0{,}5$, $\rho=\sin(\pi/4)=0{,}7071$ pour la gaussienne), on compare.

```python
from scipy.stats import norm, multivariate_normal
theta, rho = 2.0, np.sin(np.pi / 4)
lignes = []
for q in (0.1, 0.01, 0.001):
    cond = (2 - q**theta) ** (-1 / theta)
    c_qq = (2 * q ** (-theta) - 1) ** (-1 / theta)
    gauss = multivariate_normal([0, 0], [[1, rho], [rho, 1]]).cdf([norm.ppf(q), norm.ppf(q)])
    lignes.append({"q": q, "P(V<=q | U<=q) Clayton": round(cond, 4), "limite 2^(-1/theta)": round(2 ** (-1 / theta), 4),
                   "P(U>1-q, V>1-q) Clayton retournée": f"{c_qq:.3e}", "gaussienne (même tau)": f"{gauss:.3e}",
                   "rapport": round(c_qq / gauss, 1)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
    q  P(V<=q | U<=q) Clayton  limite 2^(-1/theta) P(U>1-q, V>1-q) Clayton retournée gaussienne (même tau)  rapport
0.100                  0.7089               0.7071                         7.089e-02             4.739e-02      1.5
0.010                  0.7071               0.7071                         7.071e-03             2.735e-03      2.6
0.001                  0.7071               0.7071                         7.071e-04             1.654e-04      4.3
```

La probabilité conditionnelle de Clayton converge vers $2^{-1/2}=0{,}707$ (la limite $\lambda$), tandis que celle de la copule gaussienne tend vers 0 quand $q\to0$. Le rapport entre les probabilités conjointes de la Clayton retournée et de la gaussienne **croît sans cesse** à mesure que $q$ diminue : c'est la signature de la dépendance de queue.

---

## Bilan du chapitre 6

Vous savez maintenant :

- **raisonner à la bayésienne** : a posteriori $\propto$ vraisemblance $\times$ a priori ; utiliser les **lois conjuguées** (bêta-binomiale, gamma-Poisson, normale-normale) pour obtenir des résultats exacts par simple addition ; lire et interpréter un **intervalle de crédibilité** ; formuler des phrases comme « *la probabilité que l'offre soit utile est de…* » ;
- **choisir et justifier un a priori**, mesurer son influence par une **analyse de sensibilité**, et savoir qu'il s'efface quand les données sont abondantes (Bernstein-von Mises) ;
- **estimer par simulation** (Monte-Carlo) : une espérance, une probabilité, une intégrale ; connaître la vitesse en $1/\sqrt n$ ; fabriquer des tirages par **inversion** ou **rejet** ; utiliser l'**échantillonnage préférentiel** pour les événements rares, avec son **ESS**, et les **techniques de réduction de variance** ;
- **simuler une loi a posteriori** non conjuguée avec une chaîne de Markov : **Metropolis-Hastings** (bilan détaillé, réglage du pas, taux d'acceptation) et **Gibbs** (lois conditionnelles complètes), puis calculer *tout* (rapports de cotes, effets sur les probabilités, prédictions) par de simples moyennes ;
- **vérifier ses modèles** : plusieurs chaînes dispersées, traces, $\widehat R$, ESS ; vérifications prédictives **a priori** et **a posteriori** ; comparaison par facteur de Bayes (et ses limites : sensibilité à l'a priori, paradoxe de Lindley) et par WAIC ;
- (en option) **modéliser les extrêmes** par la loi GEV et les excès au-delà d'un seuil (GPD), estimer des **niveaux de retour** avec leur incertitude ;
- (en option) **modéliser la dépendance** par les **copules**, comprendre la différence entre corrélation et dépendance de queue, et pourquoi le choix de la copule décide du risque de **catastrophes simultanées**.

Les deux fils conducteurs de ce chapitre sont **l'incertitude** (qu'il faut quantifier et propager jusqu'à la décision) et **la vérification** (un modèle, un a priori ou un algorithme ne sont jamais acceptés sur parole). Ces deux idées ne s'arrêtent pas aux méthodes bayésiennes : elles guident tout le reste du métier.

Le prochain chapitre, optionnel, aborde l'**inférence causale** : comment passer de « *deux variables varient ensemble* » à « *agir sur l'une changera l'autre* », et ce qu'il faut pour que cette inférence soit légitime. Les sections 6.1 et 6.4 (a priori, vérification de modèle) en seront un outil précieux.
