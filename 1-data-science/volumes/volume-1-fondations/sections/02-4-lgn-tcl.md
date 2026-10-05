## 2.4 Loi des grands nombres et théorème central limite

Ces deux résultats sont la **raison d'être de la statistique**. Le premier dit : *avec assez de données, la moyenne observée se rapproche de la vraie valeur.* Le second dit : *et l'erreur qui reste suit presque toujours la même courbe en cloche.* Ensemble, ils permettent de transformer un échantillon en conclusion chiffrée avec une marge d'erreur.

### 2.4.1 La moyenne d'échantillon est elle-même une variable aléatoire

Observons $n$ clients et notons $X_1,\dots,X_n$ leurs paniers. Ces variables sont **indépendantes et identiquement distribuées** (on écrit **i.i.d.**) : indépendantes entre elles, et issues de la même loi, d'espérance $\mu$ et de variance $\sigma^2$. Leur **moyenne d'échantillon** est

$$\bar X_n=\frac{X_1+\dots+X_n}{n}.$$

Un point capital, que beaucoup de débutants manquent : **$\bar X_n$ est elle-même aléatoire**. Si on reprend un autre échantillon de $n$ clients, on obtient une autre moyenne. Quelle est sa loi ? Par les propriétés de la section 2.3 :

$$E[\bar X_n]=\frac1n\sum E[X_i]=\mu,\qquad \operatorname{Var}(\bar X_n)=\frac1{n^2}\sum\operatorname{Var}(X_i)=\frac{n\sigma^2}{n^2}=\frac{\sigma^2}{n}.$$

- La moyenne d'échantillon est **centrée sur la vraie moyenne** $\mu$ (on dit qu'elle est **sans biais**).
- Sa dispersion vaut $\sigma/\sqrt n$, appelée **erreur-type** (*standard error*). Elle **diminue** quand $n$ augmente, mais seulement comme $1/\sqrt n$ : pour diviser l'erreur par 2, il faut **4 fois** plus de données ; par 10, il en faut 100 fois plus.

> 💡 **Pourquoi la variance se divise par $n$ ?** Quand on moyenne, les écarts positifs d'un client compensent partiellement les écarts négatifs d'un autre. L'aléa « se dilue » : c'est le même phénomène que la diversification vue en 2.3.3.

### 2.4.2 La loi des grands nombres

> 📐 **Énoncé (loi faible des grands nombres).** Si $X_1,X_2,\dots$ sont i.i.d. d'espérance $\mu$ et de variance finie, alors pour tout $\varepsilon>0$,
>
> $$P\bigl(|\bar X_n-\mu|\ge\varepsilon\bigr)\xrightarrow[n\to\infty]{}0.$$
>
> En mots : la probabilité que la moyenne observée s'écarte de $\mu$ de plus de $\varepsilon$ **tend vers 0**.

Voyons-le en action sur le taux de conversion de la boutique (vraie valeur $p=0{,}205$). Quatre « expériences » indépendantes observent les visiteurs un à un et notent la proportion d'acheteurs au fil du temps :

![À gauche : la proportion observée se stabilise sur la vraie valeur, quel que soit le départ. À droite : avec une loi de Cauchy, la moyenne ne converge jamais.](figures/ch02-lgn.png)

Au début, les courbes sont chaotiques (avec 3 visiteurs, la proportion vaut 0, 33 % ou 67 %…) ; puis elles s'**écrasent** autour de 0,205. C'est la loi des grands nombres.

> 📐 **Démonstration.** Elle repose sur une inégalité très utile.
>
> **Inégalité de Markov.** Pour une variable $Y\ge0$ et $a>0$ : $P(Y\ge a)\le E[Y]/a$.
> *Preuve.* $E[Y]\ge E[Y\cdot\mathbb 1_{Y\ge a}]\ge a\,P(Y\ge a)$. $\blacksquare$
>
> **Inégalité de Tchebychev.** On applique Markov à $Y=(X-\mu)^2$ avec $a=\varepsilon^2$ :
> $$P(|X-\mu|\ge\varepsilon)\le\frac{\operatorname{Var}(X)}{\varepsilon^2}.$$
>
> **Conclusion.** Appliquée à $\bar X_n$, dont la variance vaut $\sigma^2/n$ :
> $$P\bigl(|\bar X_n-\mu|\ge\varepsilon\bigr)\le\frac{\sigma^2}{n\,\varepsilon^2}\xrightarrow[n\to\infty]{}0.\ \blacksquare$$

La preuve donne même une information **quantitative** : la borne décroît comme $1/n$. Appliquons-la. Combien de visiteurs faut-il observer pour que la proportion mesurée soit à **±2 points** de la vérité avec une probabilité d'au moins 95 % ? Ici $\sigma^2=p(1-p)=0{,}163$ et $\varepsilon=0{,}02$ ; on veut $\dfrac{0{,}163}{n\times0{,}0004}\le0{,}05$, soit

$$n\ \ge\ \frac{0{,}163}{0{,}05\times0{,}0004}\approx8\,149.$$

Tchebychev garantit donc le résultat à partir d'environ **8 150 visiteurs**. C'est une borne **sûre mais très pessimiste** (elle marche pour *n'importe quelle* loi). Le théorème central limite, ci-dessous, donnera beaucoup mieux.

> ⚠️ **L'erreur du joueur.** « La roulette est tombée 5 fois sur rouge, le noir est *dû*. » Faux : la loi des grands nombres ne dit **pas** que le hasard « compense » le passé. Chaque tirage est indépendant. Elle dit que la **proportion** se stabilise parce que les premiers tirages sont **dilués** dans une masse de tirages futurs, pas parce que le futur corrige le passé.

> 🧪 **Quand elle échoue : la loi de Cauchy.** Le graphique de droite montre la moyenne cumulée de tirages d'une loi de Cauchy, une loi aux queues si lourdes qu'elle **n'a pas d'espérance** : des valeurs gigantesques surviennent régulièrement et ruinent la moyenne. La moyenne ne se stabilise *jamais*. Moralité : les hypothèses d'un théorème comptent. Dans les données réelles (revenus, tailles de fichiers, populations de villes), les **valeurs extrêmes** peuvent rendre la moyenne instable ; on utilise alors la **médiane**, plus robuste.

### 2.4.3 Le théorème central limite

La loi des grands nombres dit *où* va la moyenne ; le **théorème central limite** (TCL) dit *comment elle fluctue autour*.

> 📐 **Énoncé.** Soient $X_1,\dots,X_n$ i.i.d. d'espérance $\mu$ et de variance $\sigma^2$ finie. Alors, quand $n$ est grand,
>
> $$\frac{\bar X_n-\mu}{\sigma/\sqrt n}\ \approx\ \mathcal N(0,1),\qquad\text{c'est-à-dire}\qquad \bar X_n\approx\mathcal N\!\Bigl(\mu,\ \frac{\sigma^2}n\Bigr).$$

La portée est stupéfiante : **quelle que soit la loi d'origine** (asymétrique, discrète, bizarre), la moyenne d'un grand nombre d'observations est **approximativement normale**. C'est la raison pour laquelle la courbe en cloche est partout : *beaucoup de phénomènes sont la somme de nombreux petits effets indépendants.*

**Voyons-le.** Partons de la loi exponentielle (très asymétrique, voir 2.2.5) et regardons la distribution de la moyenne de $n=1,2,10,50$ observations, sur 20 000 échantillons. La courbe orange est la loi normale prédite par le TCL.

![Distribution de la moyenne d'échantillon pour des tirages exponentiels. À n = 1 on voit la loi d'origine ; dès n = 10 la cloche apparaît ; à n = 50 elle est quasi parfaite. La courbe orange est la loi normale prédite par le TCL.](figures/ch02-tcl.png)

Le même résultat se mesure avec un seul chiffre, l'**asymétrie** (*skewness*) de la distribution, qui vaut 0 pour une cloche parfaite. Sur les mêmes simulations (exponentielle de moyenne 1, donc d'écart-type 1) :

| $n$ | 1 | 2 | 10 | 50 | 500 |
|---|---:|---:|---:|---:|---:|
| Moyenne des moyennes | 0,997 | 1,005 | 0,999 | 1,000 | 0,999 |
| Écart-type des moyennes | 1,004 | 0,706 | 0,316 | 0,141 | 0,045 |
| Théorie $1/\sqrt n$ | 1,000 | 0,707 | 0,316 | 0,141 | 0,045 |
| Asymétrie | +2,02 | +1,41 | +0,59 | +0,29 | +0,12 |

On observe trois choses : la moyenne reste à 1 (sans biais) ; l'écart-type suit la loi $1/\sqrt n$ ; l'asymétrie s'efface (de 2 pour $n=1$ vers 0).

> 📐 **Idée de la preuve (esquisse).** On étudie la **fonction génératrice des moments** $M(t)=E[e^{tZ}]$ de la variable centrée réduite $Z_n=\sqrt n(\bar X_n-\mu)/\sigma$. Par indépendance, $M_{Z_n}(t)=\bigl[M(t/\sqrt n)\bigr]^n$ où $M$ est celle d'une variable centrée réduite. Un développement de Taylor donne $M(s)=1+\tfrac{s^2}2+o(s^2)$ (le terme en $s$ disparaît car l'espérance est nulle, et le coefficient de $s^2$ est $\operatorname{Var}/2=\tfrac12$). Donc $M_{Z_n}(t)=\bigl(1+\tfrac{t^2}{2n}+o(1/n)\bigr)^n\to e^{t^2/2}$, qui est précisément la fonction génératrice de $\mathcal N(0,1)$. Une démonstration complète, avec fonctions caractéristiques, relève de la ➕ théorie de la mesure (section 2.5).

### 2.4.4 Trois usages du théorème central limite

**Usage 1 : la probabilité sur une moyenne.** Les paniers de la boutique sont très asymétriques (beaucoup de petits achats, quelques gros) ; supposons-les exponentiels de moyenne 60 €, donc d'écart-type 60 €. La gérante regarde les 40 prochains paniers. Quelle est la probabilité que leur **moyenne dépasse 70 €** ?

Par le TCL, $\bar X_{40}\approx\mathcal N\bigl(60,\ 60^2/40\bigr)$, d'erreur-type $60/\sqrt{40}\approx9{,}49$. Le score $z$ est $(70-60)/9{,}49\approx1{,}05$, d'où $P\approx0{,}146$. Une simulation de 200 000 échantillons de 40 paniers donne 0,148 : l'approximation normale est très proche (elle sous-estime très légèrement la queue de droite, à cause de l'asymétrie de la loi d'origine). Observez ce que le TCL a fait : **sans connaître la loi des paniers**, seulement leur moyenne et leur écart-type, on a répondu à une question de probabilité.

**Usage 2 : de combien de visiteurs a-t-on besoin ?** Reprenons la question du 2.4.2 avec le TCL. La proportion observée $\hat p\approx\mathcal N\bigl(p,\ p(1-p)/n\bigr)$. Avec probabilité 95 %, $\hat p$ est à moins de $1{,}96$ erreurs-types de $p$ (le fameux 1,96 du 2.2.5). On veut donc

$$1{,}96\sqrt{\frac{p(1-p)}n}\le\varepsilon\iff n\ge\Bigl(\frac{1{,}96}{\varepsilon}\Bigr)^2p(1-p)=\Bigl(\frac{1{,}96}{0{,}02}\Bigr)^2\times0{,}163\approx1\,565.$$

Le TCL demande environ **1 565 visiteurs** au lieu de 8 150 : **5 fois moins**. Cette formule est celle des **tailles d'échantillon** des sondages et des tests A/B (chapitre 3). Une simulation vérifie que 1 570 visiteurs suffisent bien : la proportion observée tombe à moins de 2 points de la vérité dans 95,1 % des échantillons.

**Usage 3 : la normale approche la binomiale.** Une binomiale est une somme de $n$ Bernoulli ; le TCL dit donc que pour $n$ grand, $\text{Bin}(n,p)\approx\mathcal N\bigl(np,\ np(1-p)\bigr)$. Sur 100 visiteurs à 20 % de conversion, quelle est la probabilité d'avoir **au moins 30 acheteurs** ? La binomiale donne exactement $0{,}0112$. L'approximation normale $\mathcal N(20,\,4^2)$ donne $0{,}0062$ si l'on coupe à 30, mais $0{,}0088$ avec la **correction de continuité** (couper à 29,5 plutôt qu'à 30) : on remplace des barres discrètes par une courbe continue, et la barre « 30 » occupe l'intervalle $[29{,}5\,;\,30{,}5]$, ce qui améliore sensiblement l'approximation.

### 2.4.5 Un mot de prudence

Le TCL est un résultat **asymptotique** : « $\approx$ » devient exact quand $n\to\infty$. À partir de quelle taille est-ce valable ? Cela dépend de la loi d'origine :

| Loi d'origine | $n$ suffisant (règle empirique) |
|---|---|
| symétrique (uniforme, normale) | quelques unités à 10 |
| modérément asymétrique (exponentielle) | une trentaine |
| très asymétrique, queues lourdes | des centaines, voire jamais (si la variance est infinie) |

> ✅ **À retenir (LGN et TCL).**
>
> - $\bar X_n$ est une variable aléatoire : $E[\bar X_n]=\mu$, $\operatorname{Var}(\bar X_n)=\sigma^2/n$, **erreur-type** $=\sigma/\sqrt n$. L'erreur diminue en $1/\sqrt n$ : quatre fois plus de données pour deux fois moins d'erreur.
> - **LGN** : $\bar X_n\to\mu$ (preuve par Tchebychev). Elle ne dit rien d'un « rattrapage » du hasard.
> - **TCL** : $\dfrac{\bar X_n-\mu}{\sigma/\sqrt n}\approx\mathcal N(0,1)$ pour *toute* loi de variance finie. C'est le pont entre les probabilités et la statistique.
> - Utilisations : probabilités sur des moyennes, taille d'échantillon $n\ge(1{,}96/\varepsilon)^2p(1-p)$, approximation normale de la binomiale.
> - Les hypothèses comptent : avec des queues très lourdes (Cauchy), rien de tout cela ne marche.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.3 (dimensionner un échantillon), exercice 2.9.

```python hide
# Vérifie tous les nombres cités dans la section 2.4.
import numpy as np
from scipy import stats
p = 0.205; sigma2 = p * (1 - p); eps = 0.02
n_tcheb = sigma2 / (0.05 * eps**2)
print("sigma2 =", round(sigma2, 4), "| n Tchebychev =", round(n_tcheb), "| 0,163/(0,05*0,0004) =", round(0.163 / (0.05 * 0.0004)))
rng = np.random.default_rng(4)
for n in (1, 2, 10, 50, 500):
    m = rng.exponential(1.0, size=(20_000, n)).mean(axis=1)
    print(f"n={n:>3} moyenne {m.mean():.3f} ecart-type {m.std():.3f} theorie {1/np.sqrt(n):.3f} asymetrie {stats.skew(m):+.2f}")
mu, sigma, n = 60, 60, 40
se = sigma / np.sqrt(n)
print("erreur-type =", round(se, 2), "| z =", round(10 / se, 2), "| TCL P(>70) =", round(stats.norm(mu, se).sf(70), 4))
rng = np.random.default_rng(5)
print("simulée :", round((rng.exponential(60, size=(200_000, n)).mean(axis=1) > 70).mean(), 4))
n_tcl = (1.96 / eps) ** 2 * p * (1 - p)
print("n TCL =", round(n_tcl), "| rapport =", round(n_tcheb / n_tcl, 2))
rng = np.random.default_rng(6)
taux = rng.binomial(1570, p, size=100_000) / 1570
print("part à moins de 2 points avec n=1570 :", round((np.abs(taux - p) <= eps).mean(), 4))
b = stats.binom(100, 0.2)
print("P(X>=30) exact", round(b.sf(29), 4), "| normale avec correction", round(stats.norm(20, 4).sf(29.5), 4), "| sans", round(stats.norm(20, 4).sf(30), 4))
```
<!--sortie-->
```text
sigma2 = 0.163 | n Tchebychev = 8149 | 0,163/(0,05*0,0004) = 8150
n=  1 moyenne 0.997 ecart-type 1.004 theorie 1.000 asymetrie +2.02
n=  2 moyenne 1.005 ecart-type 0.706 theorie 0.707 asymetrie +1.41
n= 10 moyenne 0.999 ecart-type 0.316 theorie 0.316 asymetrie +0.59
n= 50 moyenne 1.000 ecart-type 0.141 theorie 0.141 asymetrie +0.29
n=500 moyenne 0.999 ecart-type 0.045 theorie 0.045 asymetrie +0.12
erreur-type = 9.49 | z = 1.05 | TCL P(>70) = 0.1459
simulée : 0.1477
n TCL = 1565 | rapport = 5.21
part à moins de 2 points avec n=1570 : 0.9514
P(X>=30) exact 0.0112 | normale avec correction 0.0088 | sans 0.0062
```
