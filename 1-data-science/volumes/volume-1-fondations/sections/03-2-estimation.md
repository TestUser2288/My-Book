## 3.2 Estimation

> 💡 **Intuition.** La population a des paramètres (un panier moyen $\mu$, un taux de conversion $p$, un taux d'arrivée $\lambda$) que personne ne connaît. À partir d'un **échantillon**, on fabrique une **estimation**. La formule qui transforme l'échantillon en estimation s'appelle un **estimateur**. Il y a toujours plusieurs estimateurs possibles ; la question est : **lequel choisir, et à quel point peut-on lui faire confiance ?**

### 3.2.1 Un estimateur est une variable aléatoire

Notons $\theta$ un paramètre inconnu (n'importe lequel) et $\hat\theta$ (« thêta chapeau ») son estimateur. Comme l'échantillon est aléatoire, $\hat\theta$ **l'est aussi** : un autre échantillon donnerait une autre estimation. C'est exactement l'idée de la moyenne d'échantillon $\bar X_n$ au 2.4.1.

On peut le **voir** en jouant à Dieu : traitons nos 400 commandes comme *toute* la population (de moyenne connue) et tirons dedans des échantillons de 30 commandes, en recalculant la moyenne à chaque fois.

```python
import numpy as np
import pandas as pd
from scipy import stats
from scipy import optimize

rng = np.random.default_rng(11)
population = df["montant"].to_numpy()
print("moyenne de la 'population' :", round(population.mean(), 2))

moyennes = np.array([rng.choice(population, size=30, replace=False).mean() for _ in range(10_000)])
print("moyenne des 10 000 moyennes d'échantillons :", round(moyennes.mean(), 2))
print("écart-type de ces moyennes (erreur-type)    :", round(moyennes.std(), 2))
print("théorie sigma/sqrt(n)                       :", round(population.std() / np.sqrt(30), 2))
print("3 échantillons au hasard :", [round(float(rng.choice(population, 30).mean()), 1) for _ in range(3)])
```
<!--sortie-->
```text
moyenne de la 'population' : 60.25
moyenne des 10 000 moyennes d'échantillons : 60.3
écart-type de ces moyennes (erreur-type)    : 6.59
théorie sigma/sqrt(n)                       : 6.93
3 échantillons au hasard : [54.2, 59.5, 60.3]
```

Chaque échantillon de 30 commandes donne une moyenne différente (ci-dessus : 54,2 ; 59,5 ; 60,3), mais **en moyenne** ces moyennes tombent sur la vraie valeur (60,25), avec une dispersion de l'ordre de 7 DT. Cette dispersion est l'**erreur-type** : elle mesure la précision de l'estimateur. (Le petit écart avec la théorie vient du tirage **sans remise** dans une population finie.)

### 3.2.2 Qu'est-ce qu'un bon estimateur ?

On juge un estimateur sur trois critères, que l'on comprend très bien avec l'image d'un tir à la cible :

- **Le biais** : $\operatorname{Biais}(\hat\theta)=E[\hat\theta]-\theta$. Les tirs sont-ils centrés sur la cible, ou systématiquement décalés ? Un estimateur est **sans biais** si ce biais vaut 0.
- **La variance** : $\operatorname{Var}(\hat\theta)$. Les tirs sont-ils groupés ou dispersés ?
- **La cohérence** (ou *consistance*) : l'estimateur converge-t-il vers $\theta$ quand $n\to\infty$ ? (La loi des grands nombres l'assure pour la moyenne.)

Un bon estimateur est à la fois **peu biaisé** et **peu variable**. On les combine dans l'**erreur quadratique moyenne** :

> 📐 **Décomposition biais–variance.**
> $$\operatorname{EQM}(\hat\theta)=E\bigl[(\hat\theta-\theta)^2\bigr]=\operatorname{Var}(\hat\theta)+\operatorname{Biais}(\hat\theta)^2.$$
>
> *Preuve.* Notons $m=E[\hat\theta]$. On écrit $\hat\theta-\theta=(\hat\theta-m)+(m-\theta)$ et on développe le carré :
> $$E[(\hat\theta-\theta)^2]=E[(\hat\theta-m)^2]+2(m-\theta)\,E[\hat\theta-m]+(m-\theta)^2.$$
> Le terme du milieu est nul car $E[\hat\theta-m]=0$. Il reste $\operatorname{Var}(\hat\theta)+(m-\theta)^2$. $\blacksquare$

Cette formule a une conséquence profonde, qui reviendra tout au long du volume II : **accepter un petit biais peut réduire l'erreur totale si cela réduit beaucoup la variance**. C'est le principe de la régularisation en apprentissage automatique.

### 3.2.3 Pourquoi divise-t-on par $n-1$ pour la variance ?

Nous avons promis cette démonstration (3.1.4 et 2.3.3). Soit $X_1,\dots,X_n$ i.i.d. de moyenne $\mu$ et de variance $\sigma^2$. L'estimateur « naturel » de $\sigma^2$ est $\hat\sigma^2_n=\frac1n\sum(X_i-\bar X)^2$. Est-il sans biais ?

> 📐 **Calcul.** On insère $\mu$ : $X_i-\bar X=(X_i-\mu)-(\bar X-\mu)$. Alors
>
> $$\sum_i(X_i-\bar X)^2=\sum_i(X_i-\mu)^2-n(\bar X-\mu)^2.$$
>
> (En développant : $\sum(X_i-\mu)^2-2(\bar X-\mu)\sum(X_i-\mu)+n(\bar X-\mu)^2$ et $\sum(X_i-\mu)=n(\bar X-\mu)$, d'où le résultat.) Prenons l'espérance : $E[(X_i-\mu)^2]=\sigma^2$ et $E[(\bar X-\mu)^2]=\operatorname{Var}(\bar X)=\sigma^2/n$. Donc
>
> $$E\Bigl[\sum_i(X_i-\bar X)^2\Bigr]=n\sigma^2-n\cdot\frac{\sigma^2}n=(n-1)\,\sigma^2.$$
>
> Par conséquent $E[\hat\sigma^2_n]=\dfrac{n-1}n\sigma^2<\sigma^2$ : l'estimateur « divisé par $n$ » **sous-estime** la variance. Pour corriger, on divise par $n-1$ :
> $$S^2=\frac1{n-1}\sum_i(X_i-\bar X)^2,\qquad E[S^2]=\sigma^2.\ \blacksquare$$

> 💡 **Pourquoi intuitivement ?** Les données sont toujours plus proches de **leur propre** moyenne $\bar X$ que de la vraie moyenne $\mu$ (car $\bar X$ est justement construite pour être au centre des données). Mesurer les écarts à $\bar X$ sous-estime donc légèrement les écarts à $\mu$. L'échantillon a aussi « perdu un degré de liberté » : une fois $\bar X$ calculée, seules $n-1$ valeurs sont libres, la dernière est imposée.

Voyons-le sur ordinateur pour de **tout petits** échantillons ($n=5$), où l'effet est maximal (vraie variance = 1) :

```python
rng = np.random.default_rng(3)
x = rng.normal(0, 1, size=(100_000, 5))                 # 100 000 échantillons de taille 5
v_n = x.var(axis=1, ddof=0).mean()                      # divisé par n
v_n1 = x.var(axis=1, ddof=1).mean()                     # divisé par n-1
print("moyenne des estimations, division par n   :", round(v_n, 3), "  (théorie (n-1)/n = 0.8)")
print("moyenne des estimations, division par n-1 :", round(v_n1, 3))
```
<!--sortie-->
```text
moyenne des estimations, division par n   : 0.801   (théorie (n-1)/n = 0.8)
moyenne des estimations, division par n-1 : 1.001
```

![Distribution des estimations de la variance sur 100 000 échantillons de taille 5 : en divisant par n, on sous-estime en moyenne (0,80) ; en divisant par n−1, on est centré sur la vraie valeur (1).](figures/ch03-biais-variance.png)

> ⚠️ **Subtilité.** $S^2$ est sans biais pour la **variance**, mais $S=\sqrt{S^2}$ reste (très légèrement) biaisé pour l'écart-type, car la racine carrée n'est pas linéaire. Ce biais est négligeable en pratique.

### 3.2.4 La méthode des moments

> 💡 **Idée.** Les paramètres d'une loi s'expriment à l'aide de ses moments (espérance, variance…). La **méthode des moments** consiste à **égaler les moments théoriques aux moments observés** et à résoudre. C'est simple et intuitif.

**Exemple 1 : le taux d'arrivée.** Les temps (en minutes) séparant 25 commandes successives suivent une loi exponentielle de paramètre $\lambda$ inconnu. On sait que $E[T]=1/\lambda$. On égale à la moyenne observée $\bar t$ : $1/\hat\lambda=\bar t$, donc $\hat\lambda=1/\bar t$.

```python
rng = np.random.default_rng(7)
attentes = rng.exponential(scale=2.0, size=25)          # vraie valeur : lambda = 0.5 par minute (moyenne 2 min)
print("moyenne observée   :", round(attentes.mean(), 3), "minutes")
print("lambda estimé (1/moyenne) :", round(1 / attentes.mean(), 3), "(vraie valeur : 0.5)")
```
<!--sortie-->
```text
moyenne observée   : 1.988 minutes
lambda estimé (1/moyenne) : 0.503 (vraie valeur : 0.5)
```

**Exemple 2 : une loi à deux paramètres.** Les montants sont modélisés par une loi **Gamma** de forme $k$ et d'échelle $\theta$, avec $E[X]=k\theta$ et $\operatorname{Var}(X)=k\theta^2$. En égalant à la moyenne $\bar x$ et à la variance $s^2$ observées, on obtient deux équations : $\hat\theta=s^2/\bar x$ et $\hat k=\bar x^2/s^2$.

```python
xbar, s2 = m.mean(), m.var()
theta_mom = s2 / xbar
k_mom = xbar**2 / s2
print("Gamma par les moments : k =", round(k_mom, 3), "  theta =", round(theta_mom, 2))
```
<!--sortie-->
```text
Gamma par les moments : k = 2.511   theta = 23.99
```

La méthode des moments est rapide, mais elle n'est pas toujours la plus précise. La suivante est la référence.

### 3.2.5 Le maximum de vraisemblance

> 💡 **Intuition.** Yasmine lance une nouvelle promotion et observe 7 achats sur 20 visiteurs. Quelle valeur du taux de conversion $p$ rend ces données **les plus plausibles** ? Si $p$ valait 0,05, observer 7 acheteurs sur 20 serait très improbable ; si $p$ valait 0,9, tout autant. Il existe une valeur intermédiaire pour laquelle ce résultat est **le moins surprenant possible** : c'est l'estimation du maximum de vraisemblance.

**La vraisemblance** $L(\theta)$ est la probabilité (ou la densité) d'observer **les données effectivement observées**, vue comme une fonction du paramètre $\theta$. Pour des observations indépendantes $x_1,\dots,x_n$ :

$$L(\theta)=\prod_{i=1}^n f(x_i;\theta).$$

L'estimateur du maximum de vraisemblance (EMV, *MLE*) est la valeur $\hat\theta$ qui **maximise** $L(\theta)$. Comme les produits sont pénibles à dériver et numériquement instables (le produit de nombreuses probabilités minuscules s'écrase vers 0), on maximise plutôt le **logarithme** de la vraisemblance, qui transforme le produit en somme et a le même maximum (le logarithme est croissant) :

$$\ell(\theta)=\ln L(\theta)=\sum_{i=1}^n\ln f(x_i;\theta).$$

C'est de l'optimisation (section 1.3) : on dérive et on annule.

> 📐 **Exemple complet : le taux de conversion.** On observe $k$ achats sur $n$ visiteurs. Le modèle est binomial : $L(p)=\binom nk p^k(1-p)^{n-k}$, donc
>
> $$\ell(p)=\ln\tbinom nk+k\ln p+(n-k)\ln(1-p).$$
>
> On dérive : $\ell'(p)=\dfrac kp-\dfrac{n-k}{1-p}$. En annulant : $k(1-p)=(n-k)p\iff k=np$, d'où
>
> $$\hat p=\frac kn.$$
>
> La dérivée seconde $\ell''(p)=-\frac k{p^2}-\frac{n-k}{(1-p)^2}<0$ : c'est bien un **maximum**. $\blacksquare$
>
> L'estimateur du maximum de vraisemblance est donc tout simplement la **proportion observée**, ce qui rassure : la méthode retrouve le bon sens.

Pour $k=7$, $n=20$ : $\hat p=0{,}35$. La figure montre la vraisemblance et la log-vraisemblance en fonction de $p$ ; le maximum est atteint en $0{,}35$, et la log-vraisemblance est une courbe en cloche inversée, bien plus facile à optimiser.

![Vraisemblance (à gauche) et log-vraisemblance (à droite) pour 7 achats sur 20 visiteurs. Le maximum est en p = 0,35.](figures/ch03-vraisemblance.png)

Vérifions par calcul numérique : on cherche le maximum sur une grille, puis avec un optimiseur (la méthode générale quand il n'y a pas de formule).

```python
k, n_obs = 7, 20
grille = np.linspace(0.001, 0.999, 999)
loglik = stats.binom.logpmf(k, n_obs, grille)
print("maximum sur une grille :", round(grille[np.argmax(loglik)], 3))

# optimiseur : on minimise la log-vraisemblance NÉGATIVE
res = optimize.minimize_scalar(lambda p: -stats.binom.logpmf(k, n_obs, p), bounds=(0.001, 0.999), method="bounded")
print("optimiseur             :", round(res.x, 4))
```
<!--sortie-->
```text
maximum sur une grille : 0.35
optimiseur             : 0.35
```

**D'autres exemples classiques** (mêmes calculs, à faire en exercice) :

| Modèle | Estimateur du maximum de vraisemblance |
|---|---|
| Bernoulli / binomiale | $\hat p=\bar x$ (proportion observée) |
| Poisson$(\lambda)$ | $\hat\lambda=\bar x$ |
| Exponentielle$(\lambda)$ | $\hat\lambda=1/\bar x$ |
| Normale$(\mu,\sigma^2)$ | $\hat\mu=\bar x$ ; $\hat\sigma^2=\frac1n\sum(x_i-\bar x)^2$ (⚠️ divisé par $n$ : biaisé !) |

On retrouve pour l'exponentielle la même formule qu'avec les moments. Remarquez la dernière ligne : l'EMV de la variance divise par $n$, donc est **légèrement biaisé**. Le maximum de vraisemblance n'est pas toujours sans biais ; il a d'autres qualités.

**Quand il n'y a pas de formule : l'optimisation numérique.** Pour la loi Gamma des montants, on ne peut pas résoudre à la main. On confie la log-vraisemblance à un optimiseur, exactement comme au chapitre 1 (la descente de gradient en est l'ancêtre) :

```python
def neg_loglik_gamma(params, x):
    k, theta = params
    if k <= 0 or theta <= 0:
        return np.inf
    return -stats.gamma.logpdf(x, a=k, scale=theta).sum()

res = optimize.minimize(neg_loglik_gamma, x0=[k_mom, theta_mom], args=(m.to_numpy(),), method="Nelder-Mead")
k_mle, theta_mle = res.x
print("Gamma par maximum de vraisemblance : k =", round(k_mle, 3), " theta =", round(theta_mle, 2))
print("Gamma par moments                  : k =", round(k_mom, 3), " theta =", round(theta_mom, 2))
print("log-vraisemblance maximale :", round(-res.fun, 1))
print("log-vraisemblance (moments):", round(-neg_loglik_gamma([k_mom, theta_mom], m.to_numpy()), 1))
```
<!--sortie-->
```text
Gamma par maximum de vraisemblance : k = 3.001  theta = 20.07
Gamma par moments                  : k = 2.511  theta = 23.99
log-vraisemblance maximale : -1938.9
log-vraisemblance (moments): -1942.2
```

Le maximum de vraisemblance trouve des paramètres de log-vraisemblance **plus élevée** que ceux des moments (c'est sa définition : il est le meilleur *pour les données observées*). Ici les deux approches donnent des valeurs du même ordre (la forme passe de 2,5 à 3,0). N'oubliez pas qu'une loi Gamma n'est qu'un **modèle** des montants parmi d'autres (on a vu au 3.1.5 qu'une loi log-normale convient aussi bien) : estimer les paramètres ne dit pas si le modèle est juste. Notez aussi que la bibliothèque sait faire tout cela d'un coup :

```python
k_sp, loc_sp, theta_sp = stats.gamma.fit(m, floc=0)       # floc=0 : on impose une borne inférieure à 0
print("scipy.stats.gamma.fit :", round(k_sp, 3), round(theta_sp, 2))
```
<!--sortie-->
```text
scipy.stats.gamma.fit : 3.001 20.07
```

### 3.2.6 Pourquoi le maximum de vraisemblance est la référence

Sous des conditions de régularité raisonnables, l'EMV a quatre propriétés remarquables, que l'on admettra :

1. **Cohérent** : $\hat\theta\to\theta$ quand $n\to\infty$.
2. **Asymptotiquement normal** : $\hat\theta\approx\mathcal N\bigl(\theta,\ 1/(nI(\theta))\bigr)$ pour $n$ grand, où $I(\theta)$ est l'**information de Fisher** (la courbure moyenne de la log-vraisemblance autour du maximum : plus le pic est pointu, plus on est précis).
3. **Asymptotiquement efficace** : parmi les estimateurs cohérents, il a (presque) la plus petite variance possible.
4. **Invariant par reparamétrisation** : si $\hat\theta$ est l'EMV de $\theta$, alors $g(\hat\theta)$ est l'EMV de $g(\theta)$.

Le point 2 donne directement l'**erreur-type** : pour la proportion, $I(p)=\frac1{p(1-p)}$, donc

$$\operatorname{SE}(\hat p)=\sqrt{\frac{\hat p(1-\hat p)}n}.$$

```python
p_hat, n_obs = 7 / 20, 20
se = np.sqrt(p_hat * (1 - p_hat) / n_obs)
print("p chapeau =", p_hat, "  erreur-type =", round(se, 3))
print("avec 10 fois plus de données (70/200) :", round(np.sqrt(0.35 * 0.65 / 200), 3))
```
<!--sortie-->
```text
p chapeau = 0.35   erreur-type = 0.107
avec 10 fois plus de données (70/200) : 0.034
```

Avec 20 visiteurs, l'erreur-type est de 0,107 (près de 11 points !) : $\hat p=0{,}35$ est très imprécis. Avec 200 visiteurs, elle tombe à 0,034. Estimer, c'est bien ; **chiffrer l'incertitude de l'estimation** est mieux : c'est l'objet de la section suivante.

> ✅ **À retenir (estimation).**
>
> - Un **estimateur** est une formule appliquée à l'échantillon ; c'est une variable aléatoire dont on étudie le **biais**, la **variance**, la **cohérence**. $\operatorname{EQM}=\operatorname{Var}+\operatorname{Biais}^2$.
> - $\bar X$ est sans biais pour $\mu$, et **$S^2$ (divisé par $n-1$)** est sans biais pour $\sigma^2$ (preuve en 3.2.3).
> - **Moments** : on égale moments théoriques et observés. **Maximum de vraisemblance** : on maximise $\ell(\theta)=\sum\ln f(x_i;\theta)$ ; formule fermée si possible, optimiseur sinon.
> - Pour une proportion, l'EMV est la fréquence observée, d'erreur-type $\sqrt{\hat p(1-\hat p)/n}$.
> - L'EMV est cohérent, asymptotiquement normal et efficace : c'est l'outil standard.
