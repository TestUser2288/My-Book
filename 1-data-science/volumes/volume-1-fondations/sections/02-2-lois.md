## 2.2 Variables aléatoires et lois usuelles

### 2.2.1 Qu'est-ce qu'une variable aléatoire ?

> 💡 **Intuition.** Jusqu'ici nous parlions d'**événements** (« le client achète »). Mais les données sont des **nombres** : le montant du panier, le nombre de commandes, le temps d'attente. Une **variable aléatoire** (v.a.) est simplement **un nombre dont la valeur dépend du hasard**. On la note par une majuscule, $X$, et ses valeurs possibles par des minuscules, $x$.

Exemples chez la boutique :

- $X$ = nombre de commandes reçues entre 14 h et 15 h (0, 1, 2, 3, …) ;
- $Y$ = montant en euros du prochain panier (n'importe quel nombre positif) ;
- $B$ = 1 si le prochain visiteur achète, 0 sinon.

On distingue deux familles :

| | Variable **discrète** | Variable **continue** |
|---|---|---|
| Valeurs | une liste dénombrable : 0, 1, 2, … | tout un intervalle de réels |
| Exemple | nombre de commandes | temps d'attente, montant exact |
| Description | **fonction de masse** $P(X=k)$ | **densité** $f(x)$ |
| Probabilité d'un intervalle | somme des $P(X=k)$ | **aire** sous la densité (intégrale du chapitre 1) |

> ⚠️ **Piège à connaître dès maintenant.** Pour une variable continue, la probabilité d'une valeur **exacte** est **zéro** : $P(X=2{,}5\text{ min})=0$. Avez-vous déjà mesuré un temps d'attente de *exactement* 2,500000… minutes ? Seuls des **intervalles** ont une probabilité : $P(2\le X\le3)$. La densité $f(x)$ n'est donc *pas* une probabilité : c'est une probabilité *par unité de longueur* (comme une densité de population se mesure en habitants par km²).

**La fonction de répartition.** Pour les deux familles, on peut définir

$$F(x)=P(X\le x),$$

la probabilité de rester **sous** le seuil $x$. Elle croît de 0 à 1. Elle sert à tout : $P(a<X\le b)=F(b)-F(a)$, et la **probabilité d'excéder** un seuil est $P(X>x)=1-F(x)$. Pour une variable continue, $F(x)=\int_{-\infty}^x f(t)\,dt$, et inversement $f=F'$ : c'est le théorème fondamental du 1.2.4.

Dans tout le chapitre, nous utiliserons la bibliothèque **SciPy** (`scipy.stats`), qui fournit pour chaque loi les mêmes méthodes :

| Méthode | Rôle |
|---|---|
| `.pmf(k)` / `.pdf(x)` | masse (discret) ou densité (continu) |
| `.cdf(x)` | fonction de répartition $F(x)=P(X\le x)$ |
| `.sf(x)` | « survie » $P(X>x)=1-F(x)$ (plus précis que `1 - cdf`) |
| `.ppf(q)` | **quantile** : la valeur $x$ telle que $F(x)=q$ (inverse de `cdf`) |
| `.rvs(size, random_state)` | **simuler** des tirages |
| `.mean()`, `.var()`, `.std()` | espérance, variance, écart-type (section 2.3) |

### 2.2.2 Loi de Bernoulli : le oui/non

C'est la plus simple : une expérience à **deux issues**, « succès » (1) avec probabilité $p$, « échec » (0) avec probabilité $1-p$.

$$P(B=1)=p,\qquad P(B=0)=1-p.$$

Le visiteur d'Réseaux qui achète avec probabilité $p=0{,}15$ est une Bernoulli(0,15). On la note $B\sim\text{Bern}(p)$ (le symbole $\sim$ se lit « suit la loi »). C'est la brique de base de toutes les prédictions « oui/non » (clic, achat, fraude, désabonnement).

### 2.2.3 Loi binomiale : compter les succès

> 💡 **Intuition.** Vous répétez **$n$ fois** la même expérience de Bernoulli, **indépendamment** ; la loi binomiale décrit le **nombre de succès**.

La gérante reçoit 20 visiteurs venant de la publicité ; chacun achète avec la probabilité $p=0{,}2$, indépendamment des autres. Soit $X$ le nombre d'acheteurs. Quelle est la probabilité d'avoir **exactement 4 acheteurs** ?

> 📐 **Construction de la formule.** Prenons une configuration précise, par exemple : les 4 premiers visiteurs achètent, les 16 suivants non. Par indépendance, sa probabilité est $p^4(1-p)^{16}$. Mais il y a d'autres configurations avec 4 acheteurs : on choisit **lesquels** des 20 visiteurs achètent, soit $\binom{20}{4}$ façons (section 1.6). Chacune a **la même** probabilité $p^4(1-p)^{16}$, et les configurations sont incompatibles : on additionne.
>
> $$P(X=k)=\binom{n}{k}\,p^k\,(1-p)^{n-k},\qquad k=0,1,\dots,n.$$

Pour $k=4$ : $\binom{20}{4}=4845$, donc $P(X=4)=4845\times0{,}2^4\times0{,}8^{16}\approx0{,}218$.

```python
from scipy import stats
import numpy as np
import math

n, p = 20, 0.2
# à la main, avec la formule
print("à la main :", round(math.comb(n, 4) * p**4 * (1 - p)**(n - 4), 4))
# avec scipy
X = stats.binom(n, p)
print("scipy     :", round(X.pmf(4), 4))
print("P(X >= 6) :", round(X.sf(5), 4), "  (sf(5) = P(X > 5))")
print("P(X <= 2) :", round(X.cdf(2), 4))
```
<!--sortie-->
```text
à la main : 0.2182
scipy     : 0.2182
P(X >= 6) : 0.1958   (sf(5) = P(X > 5))
P(X <= 2) : 0.2061
```

Quatre acheteurs est le résultat le plus fréquent (21,8 %), ce qui est logique car $20\times0{,}2=4$. Mais **six acheteurs ou plus** arrive avec une probabilité de presque 20 % : un jour « exceptionnel » n'est pas si exceptionnel. Voyez la forme complète :

![Loi binomiale et loi de Poisson : les probabilités de chaque valeur.](figures/ch02-lois-discretes.png)

**Vérification par simulation.** Simulons 100 000 journées de 20 visiteurs :

```python
rng = np.random.default_rng(10)
jours = rng.binomial(n=20, p=0.2, size=100_000)       # un nombre d'acheteurs par jour
print("fréquence de X = 4 :", round((jours == 4).mean(), 4))
print("fréquence de X >= 6:", round((jours >= 6).mean(), 4))
```
<!--sortie-->
```text
fréquence de X = 4 : 0.2195
fréquence de X >= 6: 0.1956
```

Les fréquences simulées retombent sur les valeurs théoriques, à quelques millièmes près.

### 2.2.4 Loi de Poisson : compter des événements rares

> 💡 **Intuition.** On compte les **événements qui surviennent au hasard dans le temps ou l'espace** : appels à un standard, commandes par heure, fautes de frappe par page, pannes par mois. On connaît seulement la **cadence moyenne** $\lambda$ (« en moyenne 3 commandes par heure »).

$$P(X=k)=e^{-\lambda}\frac{\lambda^k}{k!},\qquad k=0,1,2,\dots$$

Si la gérante reçoit en moyenne **3 commandes par heure**, la probabilité de ne **recevoir aucune** commande pendant une heure est $e^{-3}\approx0{,}0498$, soit 5 % : environ une heure sur vingt est complètement vide. La probabilité d'en recevoir **exactement 3** est $e^{-3}\cdot3^3/3!\approx0{,}224$.

```python
Y = stats.poisson(mu=3)                      # scipy appelle λ « mu »
print("P(0 commande)  =", round(Y.pmf(0), 4))
print("P(3 commandes) =", round(Y.pmf(3), 4))
print("P(>= 6)        =", round(Y.sf(5), 4))
print("P(>= 10)       =", round(Y.sf(9), 5))
```
<!--sortie-->
```text
P(0 commande)  = 0.0498
P(3 commandes) = 0.224
P(>= 6)        = 0.0839
P(>= 10)       = 0.0011
```

Six commandes ou plus en une heure arrive environ 8 % du temps : utile pour dimensionner le personnel d'emballage.

> 📐 **D'où vient cette formule : Poisson comme limite de la binomiale.** Découpons l'heure en $n$ très petits intervalles (disons $n=3600$ secondes). Dans chacun, une commande arrive avec une probabilité minuscule $p=\lambda/n$ (pour que la moyenne $np$ reste égale à $\lambda$). Le nombre de commandes est alors binomial$(n,\lambda/n)$ et

> $$P(X=k)=\binom nk\Bigl(\frac\lambda n\Bigr)^k\Bigl(1-\frac\lambda n\Bigr)^{n-k}
> =\frac{\lambda^k}{k!}\cdot\frac{n(n-1)\cdots(n-k+1)}{n^k}\cdot\Bigl(1-\frac\lambda n\Bigr)^{n}\Bigl(1-\frac\lambda n\Bigr)^{-k}.$$
>
> Quand $n\to\infty$ : la fraction $\frac{n(n-1)\cdots(n-k+1)}{n^k}\to1$ (il y a $k$ facteurs, chacun tend vers 1) ; $(1-\lambda/n)^n\to e^{-\lambda}$ (la définition de l'exponentielle) ; $(1-\lambda/n)^{-k}\to1$. Il reste $e^{-\lambda}\lambda^k/k!$. $\blacksquare$

Vérifions-le numériquement : binomiale$(1000;\,0{,}003)$ contre Poisson$(3)$ :

```python
for k in range(0, 6):
    b = stats.binom(1000, 0.003).pmf(k)
    q = stats.poisson(3).pmf(k)
    print(f"k = {k} : binomiale = {b:.5f}   Poisson = {q:.5f}")
```
<!--sortie-->
```text
k = 0 : binomiale = 0.04956   Poisson = 0.04979
k = 1 : binomiale = 0.14914   Poisson = 0.14936
k = 2 : binomiale = 0.22415   Poisson = 0.22404
k = 3 : binomiale = 0.22438   Poisson = 0.22404
k = 4 : binomiale = 0.16828   Poisson = 0.16803
k = 5 : binomiale = 0.10087   Poisson = 0.10082
```

Les deux colonnes sont presque identiques. **Règle pratique** : quand $n$ est grand et $p$ petit, on peut remplacer Binomiale$(n,p)$ par Poisson$(np)$.

### 2.2.5 Les variables continues : la densité

Pour une variable continue, la loi est donnée par une **densité** $f$ : une fonction positive dont l'aire totale vaut 1, avec

$$P(a\le X\le b)=\int_a^b f(x)\,dx.$$

C'est ici que l'intégrale du chapitre 1 trouve son usage : une probabilité est une **aire**. Trois lois continues essentielles :

![Trois lois continues : uniforme, exponentielle, normale.](figures/ch02-lois-continues.png)

#### Loi uniforme : « aucune préférence »

$X\sim\mathcal{U}(a,b)$ : toutes les valeurs de $[a,b]$ sont également probables, de densité $\frac1{b-a}$. Un client appelle à une heure uniformément répartie entre 0 et 10 minutes après le début de l'heure : $P(X\le3)=3/10$. Le générateur aléatoire de l'ordinateur produit des $\mathcal{U}(0,1)$ ; toutes les autres lois en sont fabriquées.

#### Loi exponentielle : le temps d'attente

$X\sim\text{Exp}(\lambda)$ avec densité $f(x)=\lambda e^{-\lambda x}$ pour $x\ge0$. C'est le **temps d'attente** entre deux événements d'un processus de Poisson (nous l'avions rencontrée en 1.2.4). Sa fonction de répartition est $F(x)=1-e^{-\lambda x}$, donc

$$P(X>x)=e^{-\lambda x}.$$

Si les clients arrivent à la cadence de $\lambda=0{,}5$ par minute (un toutes les 2 minutes en moyenne), la probabilité d'attendre **plus de 3 minutes** le prochain client est $e^{-0{,}5\times3}=e^{-1{,}5}\approx0{,}223$.

```python
T = stats.expon(scale=1 / 0.5)         # scipy utilise scale = 1/λ
print("P(attendre > 3 min) =", round(T.sf(3), 4), " (formule : exp(-1.5) =", round(math.exp(-1.5), 4), ")")
print("médiane du temps d'attente :", round(T.ppf(0.5), 3), "min")
print("90 % des attentes sont < ", round(T.ppf(0.90), 2), "min")
```
<!--sortie-->
```text
P(attendre > 3 min) = 0.2231  (formule : exp(-1.5) = 0.2231 )
médiane du temps d'attente : 1.386 min
90 % des attentes sont <  4.61 min
```

La **médiane** (1,39 min) est inférieure à la moyenne (2 min) : la loi exponentielle est **asymétrique**, avec quelques attentes très longues qui tirent la moyenne vers le haut.

> 📐 **La propriété d'absence de mémoire.** Si vous avez déjà attendu 2 minutes sans voir de client, la probabilité d'attendre encore 3 minutes est **la même** que si vous veniez d'arriver. Preuve :
>
> $$P(X>s+t\mid X>s)=\frac{P(X>s+t)}{P(X>s)}=\frac{e^{-\lambda(s+t)}}{e^{-\lambda s}}=e^{-\lambda t}=P(X>t).\ \blacksquare$$
>
> La première égalité est la définition du conditionnel (car $\{X>s+t\}\subset\{X>s\}$). Le processus « ne se souvient pas » de ce qui s'est passé : il n'y a pas de « retard » à rattraper. (Contre-intuitif pour un bus supposé passer toutes les 10 minutes, mais exact pour des arrivées vraiment aléatoires.)

```python
# vérification numérique : P(X > 5 | X > 2)  ==  P(X > 3)
print(round(T.sf(5) / T.sf(2), 6), round(T.sf(3), 6))
```
<!--sortie-->
```text
0.22313 0.22313
```

#### Loi normale : la courbe en cloche

$X\sim\mathcal{N}(\mu,\sigma^2)$, de densité

$$f(x)=\frac1{\sigma\sqrt{2\pi}}\exp\Bigl(-\frac{(x-\mu)^2}{2\sigma^2}\Bigr).$$

Deux paramètres : $\mu$ **centre** la cloche, $\sigma$ (l'écart-type) mesure son **étalement**. On la rencontre partout : tailles, erreurs de mesure, moyennes d'échantillons (on verra pourquoi en 2.4).

Les ventes quotidiennes de la boutique suivent à peu près $\mathcal{N}(\mu=120,\ \sigma=15)$. Aucune formule fermée n'existe pour la fonction de répartition : on utilise l'ordinateur.

```python
V = stats.norm(loc=120, scale=15)
print("P(X > 150)             =", round(V.sf(150), 4))
print("P(105 < X < 135)       =", round(V.cdf(135) - V.cdf(105), 4))
print("jour 'exceptionnel' : 95 % des jours sont sous", round(V.ppf(0.95), 1), "ventes")
```
<!--sortie-->
```text
P(X > 150)             = 0.0228
P(105 < X < 135)       = 0.6827
jour 'exceptionnel' : 95 % des jours sont sous 144.7 ventes
```

![Les ventes quotidiennes suivent N(120 ; 15²). Un jour à plus de 150 ventes survient environ 2 fois sur 100.](figures/ch02-normale-zones.png)

**Centrer et réduire : le score $z$.** Comment comparer des valeurs de lois différentes ? On mesure **combien d'écarts-types** on est du centre :

$$z=\frac{x-\mu}{\sigma}.$$

Si $X\sim\mathcal{N}(\mu,\sigma^2)$, alors $Z=(X-\mu)/\sigma\sim\mathcal{N}(0,1)$, la **loi normale centrée réduite**. Un jour à 150 ventes correspond à $z=(150-120)/15=2$ : deux écarts-types au-dessus de la moyenne. Toutes les probabilités normales se ramènent à celles de $\mathcal{N}(0,1)$, dont on retient trois repères :

| Intervalle | Probabilité |
|---|---|
| $\mu\pm1\sigma$ | environ **68 %** |
| $\mu\pm2\sigma$ | environ **95 %** |
| $\mu\pm3\sigma$ | environ **99,7 %** |

```python
for k in (1, 2, 3):
    print(f"P(|Z| < {k}) = {stats.norm.cdf(k) - stats.norm.cdf(-k):.4f}")
print("z tel que P(Z < z) = 0.975 :", round(stats.norm.ppf(0.975), 3))
```
<!--sortie-->
```text
P(|Z| < 1) = 0.6827
P(|Z| < 2) = 0.9545
P(|Z| < 3) = 0.9973
z tel que P(Z < z) = 0.975 : 1.96
```

Ce dernier nombre, **1,96**, apparaîtra sans cesse dans les intervalles de confiance du chapitre 3.

> 🧪 **Test express « est-ce normal ? ».** Un jour à 190 ventes ($z=4{,}67$) serait extraordinairement rare si la loi était vraiment normale (environ 1 chance sur 700 000 d'être aussi haut). Si cela arrive, la loi n'est probablement pas la bonne ou un événement particulier s'est produit (promotion, fête). Détecter les valeurs avec $|z|$ très grand est la méthode de base de détection d'anomalies.

### 2.2.6 Quelle loi choisir ?

| Situation | Loi | Paramètres |
|---|---|---|
| un oui/non | Bernoulli | $p$ |
| nombre de succès sur $n$ essais indépendants | Binomiale | $n,\ p$ |
| nombre d'événements dans un intervalle, cadence $\lambda$ | Poisson | $\lambda$ |
| temps d'attente entre deux événements | Exponentielle | $\lambda$ |
| aucune préférence sur un intervalle | Uniforme | $a,\ b$ |
| somme de nombreux petits effets, mesures | Normale | $\mu,\ \sigma$ |

> ✅ **À retenir (variables aléatoires et lois).**
>
> - Une variable aléatoire est un nombre issu du hasard. Discrète : on décrit $P(X=k)$. Continue : on décrit une densité, et les probabilités sont des **aires**.
> - La fonction de répartition $F(x)=P(X\le x)$ ; avec `scipy.stats` : `pmf/pdf`, `cdf`, `sf`, `ppf`, `rvs`.
> - Bernoulli (oui/non), binomiale (compter les succès, $\binom nk p^k(1-p)^{n-k}$), Poisson (événements rares, $e^{-\lambda}\lambda^k/k!$).
> - Exponentielle : temps d'attente, sans mémoire. Normale : cloche, score $z$, règle 68-95-99,7.
> - Simulez toujours pour vérifier vos formules.
