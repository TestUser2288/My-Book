## 3.3 Intervalles de confiance

> 💡 **Intuition.** Dire « le panier moyen est de 60,25 € » est trompeur : cela suggère une précision que l'on n'a pas. Un meilleur énoncé est : « le panier moyen se situe, avec une confiance de 95 %, entre 56,5 et 64,0 € ». L'**intervalle de confiance** (IC) transforme une estimation ponctuelle en une **fourchette honnête**, dont la largeur reflète l'incertitude.

### 3.3.1 Construire un intervalle pour une moyenne

Rappelons ce que nous savons (2.4) : par le théorème central limite, $\bar X_n\approx\mathcal N(\mu,\ \sigma^2/n)$. Donc le score centré réduit $\dfrac{\bar X_n-\mu}{\sigma/\sqrt n}$ suit à peu près $\mathcal N(0,1)$, et comme $P(-1{,}96\le Z\le1{,}96)=0{,}95$ :

> 📐 **Construction.**
>
> $$P\Bigl(-1{,}96\le\frac{\bar X_n-\mu}{\sigma/\sqrt n}\le1{,}96\Bigr)=0{,}95.$$
>
> On isole $\mu$ au milieu de l'encadrement : multiplier par $\sigma/\sqrt n$, puis soustraire $\bar X_n$ et multiplier par $-1$ (ce qui renverse les inégalités) :
>
> $$P\Bigl(\bar X_n-1{,}96\frac{\sigma}{\sqrt n}\ \le\ \mu\ \le\ \bar X_n+1{,}96\frac{\sigma}{\sqrt n}\Bigr)=0{,}95.$$
>
> L'**intervalle de confiance à 95 %** est donc $\bar x\pm1{,}96\,\dfrac{\sigma}{\sqrt n}$. $\blacksquare$

Il a une structure à retenir absolument, qui se retrouvera partout :

$$\text{estimation}\ \pm\ \text{(valeur critique)}\times\text{(erreur-type)}.$$

**Exemple à la main.** Sur 400 commandes, $\bar x=60{,}25$ € et $s=38{,}02$. L'erreur-type est $38{,}02/\sqrt{400}=1{,}90$. L'IC à 95 % est $60{,}25\pm1{,}96\times1{,}90=60{,}25\pm3{,}73$, soit **[56,5 ; 64,0]** €.

### 3.3.2 Que veut dire « 95 % de confiance » ?

C'est la phrase la plus mal comprise de la statistique. Elle ne signifie **pas** « il y a 95 % de chances que la vraie moyenne soit dans cet intervalle-ci ». La vraie moyenne $\mu$ est un nombre **fixe** (inconnu) : elle y est ou elle n'y est pas. Ce qui est aléatoire, c'est l'**intervalle** (il change à chaque échantillon).

> 💡 **La bonne lecture :** *si l'on répétait l'expérience un très grand nombre de fois, avec un nouvel échantillon à chaque fois, 95 % des intervalles ainsi construits contiendraient la vraie valeur.* La confiance porte sur la **méthode**, pas sur un intervalle particulier.

Voyons-le. Soixante échantillons de 40 commandes, un intervalle à 95 % pour chacun, et la vraie moyenne (connue ici car on traite nos 400 commandes comme la population) en pointillés :

![60 intervalles de confiance à 95 % construits sur 60 échantillons différents de 40 commandes. Les intervalles en rouge n'atteignent pas la vraie moyenne : environ 1 sur 20 en moyenne (5 sur 60 ici, une fluctuation normale).](figures/ch03-couverture.png)

Mesurons-le précisément : sur 20 000 échantillons de 40 commandes, **94,5 %** des intervalles contiennent la vraie moyenne, avec une largeur moyenne de 23,9 €.

```python hide
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(21)
population = df["montant"].to_numpy()
mu = population.mean()
n_ech, essais = 40, 20_000
t_crit = stats.t.ppf(0.975, n_ech - 1)

couvre = 0
largeurs = []
for _ in range(essais):
    e = rng.choice(population, size=n_ech, replace=False)
    se = e.std(ddof=1) / np.sqrt(n_ech)
    lo, hi = e.mean() - t_crit * se, e.mean() + t_crit * se
    couvre += (lo <= mu <= hi)
    largeurs.append(hi - lo)
print("part des intervalles contenant la vraie moyenne :", round(couvre / essais, 4))
print("largeur moyenne :", round(np.mean(largeurs), 2), "€")
```
<!--sortie-->
```text
part des intervalles contenant la vraie moyenne : 0.9451
largeur moyenne : 23.88 €
```

Cette couverture est proche de 95 % (un peu moins : la loi des montants est asymétrique et $n=40$ est modeste ; nous reviendrons sur ces limites). L'idée est donc validée.

> ⚠️ **Deux erreurs d'interprétation à éviter.**
> 1. « La vraie valeur a 95 % de chances d'être dans [56,5 ; 64,0] » : formulation courante, rigoureusement fausse dans l'approche fréquentiste (dans l'approche bayésienne, elle est correcte pour un *intervalle de crédibilité*).
> 2. « 95 % des **commandes** sont dans cet intervalle » : confusion entre la précision de la **moyenne** et la dispersion des **données**. L'IC de la moyenne est étroit ([56,5 ; 64,0]), alors que 95 % des commandes sont entre 19 et 129 € (3.1.3).

### 3.3.3 Quand l'écart-type est inconnu : la loi de Student

En pratique, on ne connaît **pas** $\sigma$ ; on le remplace par son estimation $s$. Mais $s$ est elle-même aléatoire, ce qui ajoute de l'incertitude : pour de petits échantillons, on tomberait trop souvent à côté avec la valeur 1,96. William Gosset (qui signait « Student » en 1908, alors qu'il travaillait pour une grande brasserie) a montré que la bonne loi pour $\dfrac{\bar X-\mu}{S/\sqrt n}$ est la **loi de Student à $n-1$ degrés de liberté** (si les données sont à peu près normales).

C'est une cloche comme la normale, mais avec des **queues plus lourdes** (plus de prudence), qui tend vers $\mathcal N(0,1)$ quand $n$ augmente. La valeur critique à 95 % :

| Degrés de liberté | 2 | 5 | 10 | 30 | 100 | 1 000 | loi normale |
|-----------------|-----|-----|-----|-----|-----|-----|-----------|
| Valeur critique | 4,303 | 2,571 | 2,228 | 2,042 | 1,984 | 1,962 | 1,960 |

```python hide
for ddl in (2, 5, 10, 30, 100, 1000):
    print(f"degrés de liberté = {ddl:>4} : valeur critique à 95 % = {stats.t.ppf(0.975, ddl):.3f}")
print("loi normale                      :", round(stats.norm.ppf(0.975), 3))
```
<!--sortie-->
```text
degrés de liberté =    2 : valeur critique à 95 % = 4.303
degrés de liberté =    5 : valeur critique à 95 % = 2.571
degrés de liberté =   10 : valeur critique à 95 % = 2.228
degrés de liberté =   30 : valeur critique à 95 % = 2.042
degrés de liberté =  100 : valeur critique à 95 % = 1.984
degrés de liberté = 1000 : valeur critique à 95 % = 1.962
loi normale                      : 1.96
```

Avec 2 degrés de liberté (3 observations), la valeur critique est 4,30 : l'intervalle est plus de deux fois plus large qu'avec 1,96. Dès 30 degrés de liberté, on est proche de 2,04 ; avec 400 observations, la différence avec 1,96 est imperceptible.

L'intervalle devient $\bar x\pm t_{n-1,\,0{,}975}\dfrac{s}{\sqrt n}$. Pour nos 400 commandes : $\bar x=60{,}25$, erreur-type $=1{,}90$, $t_{399,\,0{,}975}=1{,}966$, d'où $60{,}25\pm1{,}966\times1{,}90$, soit **[56,51 ; 63,98]** €. Une ligne de `scipy` donne le même résultat :

```python hide
m = df["montant"]
n = len(m)
xbar, s = m.mean(), m.std(ddof=1)
se = s / np.sqrt(n)
t_crit = stats.t.ppf(0.975, n - 1)
print(f"moyenne = {xbar:.2f}   erreur-type = {se:.2f}   t critique = {t_crit:.3f}")
print(f"IC à 95 % (à la main) : [{xbar - t_crit * se:.2f} ; {xbar + t_crit * se:.2f}]")
print("IC à 95 % (scipy)     :", np.round(stats.t.interval(0.95, n - 1, loc=xbar, scale=se), 2))
```
<!--sortie-->
```text
moyenne = 60.25   erreur-type = 1.90   t critique = 1.966
IC à 95 % (à la main) : [56.51 ; 63.98]
IC à 95 % (scipy)     : [56.51 63.98]
```

```python
xbar, s, n = m.mean(), m.std(ddof=1), len(m)
print(np.round(stats.t.interval(0.95, n - 1, loc=xbar, scale=s / np.sqrt(n)), 2))
```
<!--sortie-->
```text
[56.51 63.98]
```

**Et pour chaque canal ?** On répète le calcul par groupe :

| Canal | $n$ | Moyenne | IC à 95 % |
|---|---|---|---|
| Réseaux | 138 | 49,0 € | [43,8 ; 54,2] |
| Site | 148 | 59,5 € | [53,3 ; 65,7] |
| Boutique | 114 | 74,8 € | [67,3 ; 82,4] |

```python hide
def ic_moyenne(x, niveau=0.95):
    x = np.asarray(x)
    se = x.std(ddof=1) / np.sqrt(len(x))
    return stats.t.interval(niveau, len(x) - 1, loc=x.mean(), scale=se)

for canal in ["Réseaux", "Site", "Boutique"]:
    x = df.loc[df["canal"] == canal, "montant"]
    lo, hi = ic_moyenne(x)
    print(f"{canal:<10} n = {len(x):>3}   moyenne = {x.mean():5.1f}   IC95 % = [{lo:5.1f} ; {hi:5.1f}]")
```
<!--sortie-->
```text
Réseaux    n = 138   moyenne =  49.0   IC95 % = [ 43.8 ;  54.2]
Site       n = 148   moyenne =  59.5   IC95 % = [ 53.3 ;  65.7]
Boutique   n = 114   moyenne =  74.8   IC95 % = [ 67.3 ;  82.4]
```

Les intervalles du canal Réseaux ([43,8 ; 54,2]) et de la boutique ([67,3 ; 82,4]) **sont très éloignés** : c'est un indice sérieux que ces deux canaux diffèrent vraiment. L'intervalle du site ([53,3 ; 65,7]) chevauche légèrement celui de Réseaux mais pas celui de la boutique. Attention : « les intervalles se chevauchent » ne prouve **pas** que les moyennes sont égales, et même des intervalles qui se touchent peuvent cacher une différence significative. La bonne méthode est de construire un intervalle (ou un test) pour la **différence** elle-même, ce que nous ferons au 3.4.

> 💡 **Ce qui fait varier la largeur.** La demi-largeur est $t\times s/\sqrt n$. Elle **diminue** quand $n$ augmente (en $1/\sqrt n$), **augmente** quand la dispersion $s$ augmente, et **augmente** quand on exige plus de confiance (99 % donne un intervalle plus large que 95 %). Il n'y a pas de gratuité : plus de certitude coûte en précision. Pour les 400 commandes :

| Confiance | 80 % | 90 % | 95 % | 99 % |
|---|---|---|---|---|
| Intervalle (€) | [57,81 ; 62,69] | [57,11 ; 63,38] | [56,51 ; 63,98] | [55,33 ; 65,17] |
| Largeur (€) | 4,88 | 6,27 | 7,47 | 9,84 |

```python hide
for niveau in (0.80, 0.90, 0.95, 0.99):
    lo, hi = ic_moyenne(m, niveau)
    print(f"confiance {niveau:.0%} : [{lo:.2f} ; {hi:.2f}]   largeur = {hi - lo:.2f}")
```
<!--sortie-->
```text
confiance 80% : [57.81 ; 62.69]   largeur = 4.88
confiance 90% : [57.11 ; 63.38]   largeur = 6.27
confiance 95% : [56.51 ; 63.98]   largeur = 7.47
confiance 99% : [55.33 ; 65.17]   largeur = 9.84
```

### 3.3.4 Intervalle pour une proportion

Pour un taux de conversion $\hat p=k/n$, l'erreur-type vue au 3.2.6 est $\sqrt{\hat p(1-\hat p)/n}$, et l'intervalle approché (dit de **Wald**) est

$$\hat p\pm1{,}96\sqrt{\frac{\hat p(1-\hat p)}n}.$$

Sur 1 000 visiteurs dont 205 achètent : $0{,}205\pm1{,}96\times0{,}0128=0{,}205\pm0{,}025$, soit **[18,0 % ; 23,0 %]**.

Mais cet intervalle devient **mauvais** pour de petits échantillons ou des proportions proches de 0 ou 1. Par exemple, avec 0 achat sur 20 visiteurs, $\hat p=0$ et l'intervalle de Wald est $[0\,;\,0]$ : « on est certain que le taux de conversion est exactement nul » ! Absurde. L'**intervalle de Wilson** corrige cela : il est centré non pas sur $\hat p$ mais sur une valeur légèrement « tirée vers 1/2 », et ne sort jamais de $[0,1]$. Comparaison sur quatre cas :

| Observé | $\hat p$ | Wald | Wilson |
|---|---|---|---|
| 205 sur 1 000 | 0,205 | [0,180 ; 0,230] | [0,181 ; 0,231] |
| 7 sur 20 | 0,350 | [0,141 ; 0,559] | [0,181 ; 0,567] |
| 0 sur 20 | 0,000 | [0,000 ; 0,000] | [0,000 ; 0,161] |
| 2 sur 15 | 0,133 | [0,000 ; 0,305] | [0,037 ; 0,379] |

```python hide
def ic_wald(k, n, niveau=0.95):
    p = k / n
    z = stats.norm.ppf(1 - (1 - niveau) / 2)
    d = z * np.sqrt(p * (1 - p) / n)
    return max(0, p - d), min(1, p + d)

def ic_wilson(k, n, niveau=0.95):
    return stats.binomtest(k, n).proportion_ci(confidence_level=niveau, method="wilson")[:2]

for k, n_obs in [(205, 1000), (7, 20), (0, 20), (2, 15)]:
    wald, wilson = ic_wald(k, n_obs), ic_wilson(k, n_obs)
    print(f"{k:>3}/{n_obs:<5} p = {k / n_obs:.3f}   Wald = [{wald[0]:.3f} ; {wald[1]:.3f}]   Wilson = [{wilson[0]:.3f} ; {wilson[1]:.3f}]")
```
<!--sortie-->
```text
205/1000  p = 0.205   Wald = [0.180 ; 0.230]   Wilson = [0.181 ; 0.231]
  7/20    p = 0.350   Wald = [0.141 ; 0.559]   Wilson = [0.181 ; 0.567]
  0/20    p = 0.000   Wald = [0.000 ; 0.000]   Wilson = [0.000 ; 0.161]
  2/15    p = 0.133   Wald = [0.000 ; 0.305]   Wilson = [0.037 ; 0.379]
```

Pour 1 000 visiteurs, les deux méthodes coïncident. Pour 7/20, l'intervalle est très large : **[0,18 ; 0,57]** pour Wilson, c'est-à-dire que 20 visiteurs ne permettent quasiment rien de conclure. Pour 0/20, Wilson dit que le taux réel peut aller jusqu'à environ 16 % (la fameuse « règle de trois » : avec 0 événement sur $n$, la borne haute à 95 % est environ $3/n=15\,\%$).

> ✅ **Conseil pratique.** Pour une proportion, utilisez **Wilson** (ou une méthode exacte) plutôt que Wald, sauf si $n$ est très grand et $p$ loin de 0 et 1.

### 3.3.5 Quand il n'y a pas de formule : le bootstrap

Et si l'on veut un intervalle pour la **médiane**, un quantile, un rapport, ou toute autre statistique pour laquelle on ne connaît pas de formule d'erreur-type ? Le **bootstrap** (Efron, 1979) offre une solution étonnamment simple et générale.

> 💡 **Idée.** On ne peut pas retirer de nouveaux échantillons dans la vraie population, mais on peut **rééchantillonner dans l'échantillon lui-même**. On tire $n$ valeurs **avec remise** dans nos $n$ observations (certaines apparaissent plusieurs fois, d'autres pas), on recalcule la statistique, et on recommence des milliers de fois. La dispersion des valeurs obtenues imite la dispersion qu'on aurait observée en échantillonnant la vraie population.

**L'algorithme (intervalle « percentile »).** Il se programme en quelques lignes, mais l'idée suffit :

1. Répéter $B$ fois (par exemple 10 000) : tirer un échantillon de taille $n$ avec remise ; calculer la statistique.
2. L'intervalle à 95 % est formé des percentiles 2,5 % et 97,5 % des $B$ valeurs obtenues.

```python hide
rng = np.random.default_rng(42)
x = df["montant"].to_numpy()
B = 10_000

meds = np.array([np.median(rng.choice(x, size=len(x), replace=True)) for _ in range(B)])
moys = np.array([rng.choice(x, size=len(x), replace=True).mean() for _ in range(B)])

print("médiane observée :", np.median(x))
print("IC bootstrap 95 % de la médiane :", np.percentile(meds, [2.5, 97.5]).round(1))
print("IC bootstrap 95 % de la moyenne :", np.percentile(moys, [2.5, 97.5]).round(1))
print("(à comparer à l'IC de Student de la moyenne :", np.round(stats.t.interval(0.95, len(x) - 1, loc=x.mean(), scale=x.std(ddof=1) / np.sqrt(len(x))), 1), ")")
```
<!--sortie-->
```text
médiane observée : 51.0
IC bootstrap 95 % de la médiane : [47.3 55.1]
IC bootstrap 95 % de la moyenne : [56.7 64. ]
(à comparer à l'IC de Student de la moyenne : [56.5 64. ] )
```

Sur nos 400 commandes (10 000 rééchantillonnages), le bootstrap donne pour la moyenne l'intervalle [56,7 ; 64,0], pratiquement celui de la formule de Student ([56,5 ; 64,0]) : rassurant. Pour la **médiane**, qui n'a pas de formule simple, il fournit un intervalle (la médiane observée est 51,0 € ; IC à 95 % : [47,3 ; 55,1] €) que l'on n'aurait pas pu obtenir à la main.

> 🧪 **Limites.** Le bootstrap suppose que l'échantillon est représentatif de la population ; il marche mal pour des statistiques « extrêmes » (le maximum), avec de très petits échantillons, ou en présence de très fortes dépendances entre observations. Il reste un outil de base du data scientist, car il généralise à **n'importe quelle** statistique sans calcul mathématique.

### 3.3.6 Dimensionner un échantillon

On peut renverser le raisonnement : *quelle précision veut-on ?* Si la gérante veut estimer le panier moyen à ±2 € près, avec une confiance de 95 % et en supposant $s\approx38$ €, il faut $1{,}96\times38/\sqrt n\le2$, soit

$$n\ge\Bigl(\frac{1{,}96\,s}{\varepsilon}\Bigr)^2=\Bigl(\frac{1{,}96\times38}2\Bigr)^2\approx1\,387\ \text{commandes}.$$

Pour une marge de ±1 €, le même calcul donne 5 548 commandes.

```python hide
s, eps = 38, 2
print("n pour une marge de ±2 € :", int(np.ceil((1.96 * s / eps) ** 2)))
print("n pour une marge de ±1 € :", int(np.ceil((1.96 * s / 1) ** 2)))
```
<!--sortie-->
```text
n pour une marge de ±2 € : 1387
n pour une marge de ±1 € : 5548
```

Diviser la marge par 2 demande **4 fois plus de données** (la loi en $1/\sqrt n$ du 2.4). C'est pourquoi gagner de la précision devient vite très coûteux.

> ✅ **À retenir (intervalles de confiance).**
>
> - Structure universelle : **estimation ± valeur critique × erreur-type**.
> - IC de la moyenne : $\bar x\pm t_{n-1}\,s/\sqrt n$ (Student). IC d'une proportion : préférez **Wilson** à Wald.
> - « Confiance à 95 % » signifie : **la méthode** capture la vraie valeur dans 95 % des échantillons possibles. Ce n'est pas une probabilité sur la vraie valeur.
> - Largeur : $\downarrow$ avec $n$ (en $1/\sqrt n$) ; $\uparrow$ avec la dispersion et avec le niveau de confiance.
> - **Bootstrap** : rééchantillonner avec remise pour obtenir un IC de n'importe quelle statistique.
> - $n\ge(z\,s/\varepsilon)^2$ pour viser une marge $\varepsilon$.
>
> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.3, exercices 3.4 et 3.5.
