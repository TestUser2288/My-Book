## 6.1 Inférence bayésienne et lois a priori

> 💡 **Intuition.** Un détective arrive sur une scène de crime avec des **soupçons** (« le jardinier a déjà été condamné »). Chaque indice (une empreinte, un alibi) **déplace** ses soupçons : certains suspects deviennent plus probables, d'autres moins. À la fin, il a des soupçons *mis à jour*. L'inférence bayésienne est exactement cela, avec des nombres : on part d'une loi *a priori* (les soupçons), on observe des données (les indices), on obtient une loi *a posteriori* (les soupçons mis à jour). Et la **règle de mise à jour** est la formule de Bayes que vous connaissez depuis le volume I (section 2.1).

### 6.1.1 La formule de Bayes, version « paramètre »

Au volume I, la formule de Bayes disait : $P(A\mid B)=\dfrac{P(B\mid A)\,P(A)}{P(B)}$. Remplaçons $A$ par « le paramètre vaut $\theta$ » et $B$ par « nous avons observé les données $y$ » :

$$\underbrace{p(\theta\mid y)}_{\text{a posteriori}}\;=\;\frac{\overbrace{p(y\mid\theta)}^{\text{vraisemblance}}\;\overbrace{p(\theta)}^{\text{a priori}}}{\underbrace{p(y)}_{\text{constante de normalisation}}}\;\propto\;p(y\mid\theta)\,p(\theta).$$

Trois ingrédients, trois noms à retenir :

- la **vraisemblance** $p(y\mid\theta)$ : *la même fonction* que celle du maximum de vraisemblance du volume I (section 3.2). Elle dit à quel point les données observées sont plausibles pour chaque valeur de $\theta$ ;
- la loi **a priori** $p(\theta)$ : ce que l'on croit de $\theta$ **avant** de voir les données ;
- la loi **a posteriori** $p(\theta\mid y)$ : ce que l'on croit **après**. C'est *le* résultat d'une analyse bayésienne : toute l'information sur $\theta$ tient dans cette loi.

Le symbole $\propto$ se lit « proportionnel à » : le dénominateur $p(y)=\int p(y\mid\theta)p(\theta)\,d\theta$ ne dépend pas de $\theta$, il sert seulement à ce que l'aire sous la courbe vaille 1. **Tout le travail bayésien tient dans cette phrase : a posteriori = vraisemblance × a priori, puis on normalise.**

> ⚠️ **Le point qui divise.** Pour un fréquentiste, $\theta$ est une constante inconnue : dire « $P(\theta>0{,}5)=0{,}98$ » n'a pas de sens, car $\theta$ est soit plus grand que 0,5, soit non. Pour un bayésien, la probabilité mesure **notre degré de connaissance**, donc elle s'applique aussi à $\theta$. Ce n'est pas une querelle de mots : cela change les phrases qu'on a le droit de prononcer (6.1.4). Dans ce livre, nous adoptons une position pragmatique : les deux approches sont des outils, et les chiffres qu'elles donnent coïncident souvent quand les données sont abondantes.

### 6.1.2 Un exemple minuscule, calculé à la main

La gérante envoie une offre de bienvenue à **10 nouveaux clients**. Sept d'entre eux repassent commande dans l'année. Appelons $\theta$ la probabilité qu'un client avec offre rachète. Que sait-on de $\theta$ ?

**Vraisemblance.** Si les clients sont indépendants, le nombre $y$ de rachats suit une loi binomiale $\mathrm{Bin}(10,\theta)$ (volume I, section 2.2) :
$$p(y=7\mid\theta)=\binom{10}{7}\theta^{7}(1-\theta)^{3}.$$

**A priori.** La gérante n'a aucune idée précise : elle juge que toutes les valeurs de $\theta$ entre 0 et 1 sont également plausibles ($p(\theta)=1$ sur $[0,1]$).

Pour calculer à la main sans intégrale, regardons seulement **onze valeurs** possibles : $\theta\in\{0;\,0{,}1;\,0{,}2;\dots;1\}$, chacune avec la probabilité *a priori* $1/11$. C'est l'**approximation sur grille**. Il suffit de multiplier, puis de diviser par la somme.

Par exemple pour $\theta=0{,}7$ : $\theta^{7}(1-\theta)^{3}=0{,}7^{7}\times0{,}3^{3}=0{,}0823543\times0{,}027=0{,}0022236$. (On peut ignorer le coefficient binomial $\binom{10}{7}$, qui est le même pour toutes les valeurs de $\theta$ et disparaît à la normalisation.) Un tableur (ou quelques lignes de code) fait les onze calculs. Voici le résultat :

| $\theta$ | a priori | vraisemblance (sans le coefficient binomial) | a posteriori |
|---:|---:|---:|---:|
| 0,0 | 0,091 | 0 | 0,000 |
| 0,1 | 0,091 | 0,00000 | 0,000 |
| 0,2 | 0,091 | 0,00001 | 0,001 |
| 0,3 | 0,091 | 0,00008 | 0,010 |
| 0,4 | 0,091 | 0,00035 | 0,047 |
| 0,5 | 0,091 | 0,00098 | 0,129 |
| 0,6 | 0,091 | 0,00179 | 0,236 |
| **0,7** | 0,091 | **0,00222** | **0,293** |
| 0,8 | 0,091 | 0,00168 | 0,221 |
| 0,9 | 0,091 | 0,00048 | 0,063 |
| 1,0 | 0,091 | 0 | 0,000 |

Les probabilités a posteriori somment bien à 1 (c'est le rôle de la normalisation), la valeur la plus probable est $\theta=0{,}7$ et l'espérance a posteriori vaut $0{,}667$.

```python hide
import numpy as np
import pandas as pd

theta = np.round(np.arange(0, 1.01, 0.1), 1)            # les 11 valeurs possibles
prior = np.full(11, 1 / 11)                              # a priori : toutes aussi plausibles
vraisemblance = theta**7 * (1 - theta)**3                # sans le coefficient binomial
produit = prior * vraisemblance
posterieur = produit / produit.sum()                     # normalisation : la somme vaut 1

tab = pd.DataFrame({"theta": theta, "a priori": prior.round(3),
                    "vraisemblance": vraisemblance.round(5), "a posteriori": posterieur.round(3)})
print(tab.to_string(index=False))
print("\nsomme des probabilités a posteriori :", posterieur.sum().round(6))
print("valeur la plus probable :", theta[posterieur.argmax()])
print("espérance a posteriori  :", round((theta * posterieur).sum(), 3))
```
<!--sortie-->
```text
 theta  a priori  vraisemblance  a posteriori
   0.0     0.091        0.00000         0.000
   0.1     0.091        0.00000         0.000
   0.2     0.091        0.00001         0.001
   0.3     0.091        0.00008         0.010
   0.4     0.091        0.00035         0.047
   0.5     0.091        0.00098         0.129
   0.6     0.091        0.00179         0.236
   0.7     0.091        0.00222         0.293
   0.8     0.091        0.00168         0.221
   0.9     0.091        0.00048         0.063
   1.0     0.091        0.00000         0.000

somme des probabilités a posteriori : 1.0
valeur la plus probable : 0.7
espérance a posteriori  : 0.667
```

On lit le résultat : avant les données, les onze valeurs sont à égalité ; après, la probabilité se concentre autour de 0,7. Les valeurs extrêmes (0, 1) sont **exclues** : 0 est impossible puisque nous avons vu des rachats, 1 est impossible puisque nous avons vu des non-rachats. La valeur la plus plausible est celle du maximum de vraisemblance, $\hat\theta=7/10$, mais l'**espérance a posteriori** est un peu plus basse (la loi est étalée plus du côté bas que du côté haut). Nous allons voir pourquoi.

### 6.1.3 La loi Bêta : le coup de génie de la conjugaison

Onze valeurs de $\theta$, c'est grossier. Avec un continuum de valeurs, il faut une intégrale. Heureusement, ici, elle se calcule **exactement**, grâce à un choix d'*a priori* bien assorti à la vraisemblance.

**Définition.** La loi **Bêta**$(a,b)$ a pour densité sur $[0,1]$
$$p(\theta)=\frac{\theta^{a-1}(1-\theta)^{b-1}}{B(a,b)},\qquad B(a,b)=\int_0^1\theta^{a-1}(1-\theta)^{b-1}d\theta .$$
Sa moyenne est $\dfrac{a}{a+b}$. Quand $a=b=1$, c'est la loi uniforme ; quand $a$ et $b$ grandissent, elle se resserre autour de sa moyenne.

> 📐 **Théorème (conjugaison bêta-binomiale).** Si $\theta\sim\mathrm{Beta}(a,b)$ et si, sachant $\theta$, $y\sim\mathrm{Bin}(n,\theta)$, alors
> $$\theta\mid y\;\sim\;\mathrm{Beta}(a+y,\;b+n-y).$$
>
> *Démonstration.* D'après la formule de Bayes, $p(\theta\mid y)\propto p(y\mid\theta)\,p(\theta)$, donc
> $$p(\theta\mid y)\;\propto\;\theta^{y}(1-\theta)^{n-y}\cdot\theta^{a-1}(1-\theta)^{b-1}\;=\;\theta^{(a+y)-1}(1-\theta)^{(b+n-y)-1}.$$
> On reconnaît, **à une constante près**, la densité d'une loi $\mathrm{Beta}(a+y,\,b+n-y)$. Comme une densité est entièrement déterminée par sa forme et par la condition « l'aire vaut 1 », la constante manquante ne peut être que $1/B(a+y,b+n-y)$. $\square$

Les statisticiens disent que la loi Bêta est **conjuguée** à la loi binomiale : l'*a posteriori* reste dans la même famille que l'*a priori*, seuls les paramètres changent. La mise à jour se résume à une **addition** :

$$\boxed{a_{\text{post}}=a+\underbrace{y}_{\text{succès}},\qquad b_{\text{post}}=b+\underbrace{n-y}_{\text{échecs}}.}$$

On peut donc voir $a$ et $b$ comme des **pseudo-observations** : $\mathrm{Beta}(a,b)$ est l'a priori qu'aurait quelqu'un qui aurait déjà vu $a-1$ succès et $b-1$ échecs. Notre exemple : $\mathrm{Beta}(1,1)$ puis $y=7,\ n=10$, donc $\theta\mid y\sim\mathrm{Beta}(8,4)$, de moyenne $8/12\approx0{,}667$.

> 📐 **L'espérance a posteriori est une moyenne pondérée.** La moyenne a posteriori vaut
> $$\mathbb E[\theta\mid y]=\frac{a+y}{a+b+n}=\underbrace{\frac{a+b}{a+b+n}}_{w}\cdot\underbrace{\frac{a}{a+b}}_{\text{moyenne a priori}}+\underbrace{\frac{n}{a+b+n}}_{1-w}\cdot\underbrace{\frac{y}{n}}_{\hat\theta_{\text{EMV}}}.$$
> C'est un **compromis** entre ce que l'on croyait (moyenne a priori) et ce que disent les données (la fréquence observée), et le poids de l'a priori, $w=\frac{a+b}{a+b+n}$, **diminue** quand $n$ augmente. Avec 10 observations et un a priori uniforme ($a+b=2$), $w=2/12\approx0{,}17$ : 17 % de l'a priori, 83 % des données. C'est la raison pour laquelle $0{,}667<0{,}7$ : l'a priori uniforme tire un peu l'estimation vers 0,5. Avec 1 000 observations, $w\approx0{,}002$ : l'a priori a disparu.

Traçons les trois lois (a priori, vraisemblance normalisée, a posteriori), et vérifions au passage que la formule exacte et la grille de onze points donnent les mêmes probabilités :

```python hide
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy import stats

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.facecolor": "#fcfcfb",
                     "figure.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
                     "legend.frameon": False, "font.size": 10})

# 1) la grille et la loi exacte donnent-elles la même chose ?
exact = stats.beta(8, 4)
grille_fine = exact.pdf(theta) / exact.pdf(theta).sum()
print("probabilités de grille  :", posterieur.round(3))
print("Beta(8,4) renormalisée  :", grille_fine.round(3))
print("écart maximal           :", np.abs(posterieur - grille_fine).max().round(4))
print("moyenne exacte          :", round(exact.mean(), 4), "=  8/12 =", round(8 / 12, 4))

# 2) le dessin : a priori plat, vraisemblance, a posteriori ; et un a posteriori avec un a priori informatif
x = np.linspace(0, 1, 500)
fig, ax = plt.subplots(figsize=(7.2, 3.8))
vrais = x**7 * (1 - x)**3
vrais = vrais / np.trapezoid(vrais, x)                       # vraisemblance normalisée (aire = 1)
ax.plot(x, vrais, color=ORANGE, lw=6, alpha=0.45, solid_capstyle="butt")
ax.plot(x, exact.pdf(x), color=BLEU, lw=2.0)
ax.plot(x, stats.beta(1, 1).pdf(x), color="#898781", lw=1.6, ls="--")
ax.plot(x, stats.beta(12, 8).pdf(x), color=VIOLET, lw=1.8, ls="-.")
ax.text(0.02, 1.12, "a priori plat Beta(1, 1)", color="#52514e")
ax.text(0.995, 4.2, "a posteriori Beta(8, 4)\n= vraisemblance\nnormalisée\n(superposées)", color=BLEU, ha="right", va="top")
ax.annotate("avec un a priori Beta(5, 5) :\na posteriori Beta(12, 8)", xy=(0.50, stats.beta(12, 8).pdf(0.50)), xytext=(0.02, 3.0),
            color=VIOLET, arrowprops={"arrowstyle": "-", "color": VIOLET, "lw": 0.8})
ax.set_xlabel(r"probabilité de rachat $\theta$")
ax.set_ylabel("densité")
ax.set_ylim(0, 4.3)
plt.savefig("figures/ch06-bayes-10-clients.png", dpi=200, bbox_inches="tight")
plt.close()
```
<!--sortie-->
```text
probabilités de grille  : [0.    0.    0.001 0.01  0.047 0.129 0.236 0.293 0.221 0.063 0.   ]
Beta(8,4) renormalisée  : [0.    0.    0.001 0.01  0.047 0.129 0.236 0.293 0.221 0.063 0.   ]
écart maximal           : 0.0
moyenne exacte          : 0.6667 =  8/12 = 0.6667
```

![Avec 7 rachats sur 10 : l'a priori plat (tirets gris), la vraisemblance normalisée (orange épais) et l'a posteriori Beta(8, 4) (bleu) sont superposés ; avec un a priori informatif Beta(5, 5), l'a posteriori Beta(12, 8) (violet, tirets-points) est tiré vers 0,5.](figures/ch06-bayes-10-clients.png)

L'écart maximal entre la grille et la loi exacte est nul à trois décimales près (et la moyenne exacte vaut bien $8/12=0{,}6667$) : la grille de onze points n'était pas si mauvaise. Remarquez, sur le dessin, que l'*a posteriori* et la vraisemblance normalisée sont **exactement superposés** : avec un a priori plat, **les données parlent seules** (c'est évident dans la formule : multiplier par une constante ne change pas la forme). Avec un a priori informatif $\mathrm{Beta}(5,5)$ (celui d'une personne qui croit déjà à un taux proche de 50 %), l'a posteriori $\mathrm{Beta}(12,8)$ a pour moyenne $12/20=0{,}60$ : il est **tiré vers 0,5**, c'est le compromis de la formule ci-dessus.

> ✅ **À retenir (6.1.1 à 6.1.3).** A posteriori $\propto$ vraisemblance $\times$ a priori. Avec un a priori bêta et des données binomiales, l'a posteriori est une bêta dont les paramètres s'obtiennent en **ajoutant les succès et les échecs observés**. La moyenne a posteriori est un compromis entre a priori et données, où l'a priori pèse de moins en moins quand les données s'accumulent.

### 6.1.4 Comparer deux groupes : la loi de la différence

Passons aux 2 000 clients. L'offre de bienvenue a été attribuée **au hasard** à une moitié d'entre eux : la comparaison des deux groupes est donc une vraie expérience (nous y reviendrons dans le chapitre ➕ 7). Sans offre, 441 des 985 clients ont racheté (44,77 %) ; avec offre, 578 des 1 015 (56,95 %).

```python hide
clients = pd.read_csv("donnees/clients.csv")
bilan = clients.groupby("offre_bienvenue")["rachat_12m"].agg(clients="size", rachats="sum")
bilan["frequence"] = (bilan["rachats"] / bilan["clients"]).round(4)
print(bilan)
```
<!--sortie-->
```text
                 clients  rachats  frequence
offre_bienvenue                             
0                    985      441     0.4477
1                   1015      578     0.5695
```

Avec un a priori $\mathrm{Beta}(1,1)$ pour chaque groupe, les deux lois a posteriori sont $\mathrm{Beta}(1+y,\,1+n-y)$, soit :

| Groupe | A posteriori | Moyenne | Intervalle de crédibilité à 95 % |
|---|---|---:|---|
| sans offre | $\mathrm{Beta}(442,\,545)$ | 0,4478 | [0,4169 ; 0,4789] |
| avec offre | $\mathrm{Beta}(579,\,438)$ | 0,5693 | [0,5388 ; 0,5996] |


```python hide
post = {}
for groupe, ligne in bilan.iterrows():
    a_post = 1 + ligne["rachats"]
    b_post = 1 + ligne["clients"] - ligne["rachats"]
    post[groupe] = stats.beta(a_post, b_post)
    bas, haut = post[groupe].ppf([0.025, 0.975])
    print(f"offre = {groupe} : a posteriori Beta({a_post:.0f}, {b_post:.0f}) | moyenne {post[groupe].mean():.4f} | "
          f"intervalle de crédibilité à 95 % : [{bas:.4f} ; {haut:.4f}]")
```
<!--sortie-->
```text
offre = 0 : a posteriori Beta(442, 545) | moyenne 0.4478 | intervalle de crédibilité à 95 % : [0.4169 ; 0.4789]
offre = 1 : a posteriori Beta(579, 438) | moyenne 0.5693 | intervalle de crédibilité à 95 % : [0.5388 ; 0.5996]
```

Pour répondre à *la* question (« l'offre augmente-t-elle le taux de rachat ? »), il faut la loi de la **différence** $\delta=\theta_1-\theta_0$. Elle n'est pas une bêta, mais on peut la **simuler** : on tire de nombreuses valeurs de $\theta_1$ et de $\theta_0$ dans leurs lois a posteriori, et on calcule leur différence. C'est la première apparition du Monte-Carlo, que nous étudions à fond en 6.2.

```python
import numpy as np
from scipy import stats

rng = np.random.default_rng(61)
S = 200_000
theta1 = stats.beta(579, 438).rvs(S, random_state=rng)   # avec offre
theta0 = stats.beta(442, 545).rvs(S, random_state=rng)   # sans offre
delta = theta1 - theta0

print(f"moyenne de la différence       : {delta.mean():.4f}")
print(f"IC de crédibilité à 95 %       : [{np.percentile(delta, 2.5):.4f} ; {np.percentile(delta, 97.5):.4f}]")
print(f"P(l'offre augmente le rachat)  : {(delta > 0).mean():.5f}")
print(f"P(l'effet dépasse 5 points)    : {(delta > 0.05).mean():.4f}")
print(f"P(l'effet dépasse 10 points)   : {(delta > 0.10).mean():.4f}")
```
<!--sortie-->
```text
moyenne de la différence       : 0.1214
IC de crédibilité à 95 %       : [0.0778 ; 0.1647]
P(l'offre augmente le rachat)  : 1.00000
P(l'effet dépasse 5 points)    : 0.9993
P(l'effet dépasse 10 points)   : 0.8346
```

On peut maintenant prononcer des phrases que le volume I interdisait : « *sachant les données, l'offre augmente le rachat avec une probabilité quasi certaine* » (aucun de nos 200 000 tirages ne donne une différence négative ; l'approximation normale de la différence donne une probabilité d'erreur de l'ordre de $2\times10^{-8}$), « *la probabilité que l'effet dépasse 5 points de pourcentage est de 99,9 %, et qu'il dépasse 10 points de 83 %* ». Pour comparer avec l'approche fréquentiste, l'intervalle de confiance de Wald de la différence de proportions (volume I, section 3.4.5) est [0,0782 ; 0,1652], pour une différence observée de 0,1217.

```python hide
n1, y1 = bilan.loc[1, "clients"], bilan.loc[1, "rachats"]
n0, y0 = bilan.loc[0, "clients"], bilan.loc[0, "rachats"]
p1, p0 = y1 / n1, y0 / n0
se = np.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
print(f"différence observée       : {p1 - p0:.4f}")
print(f"IC de confiance à 95 %    : [{p1 - p0 - 1.96 * se:.4f} ; {p1 - p0 + 1.96 * se:.4f}]")
```
<!--sortie-->
```text
différence observée       : 0.1217
IC de confiance à 95 %    : [0.0782 ; 0.1652]
```

Les deux intervalles ([0,0778 ; 0,1647] pour la crédibilité, [0,0782 ; 0,1652] pour la confiance) sont **presque identiques** (à la troisième décimale). C'est normal : avec 1 000 observations par groupe, l'a priori uniforme ne pèse presque rien. Mais l'**interprétation** diffère profondément :

| | Intervalle de confiance (fréquentiste) | Intervalle de crédibilité (bayésien) |
|---|---|---|
| Ce qui est aléatoire | l'intervalle (il change d'un échantillon à l'autre) | le paramètre $\theta$ (notre connaissance) |
| Phrase correcte | « la *méthode* encadre la vraie valeur dans 95 % des échantillons » | « sachant les données, $\delta$ est dans l'intervalle avec la probabilité 0,95 » |
| Peut-on dire « $P(\delta>0)=\dots$ » ? | non | **oui** |
| Dépend d'un a priori ? | non | oui (mais l'effet s'efface quand $n$ grandit) |

> 💡 **Ce que la gérante veut entendre.** « L'offre est presque certainement utile, et le gain est de l'ordre de 12 points de pourcentage de rachat (entre 8 et 16 avec 95 % de probabilité). » C'est une phrase bayésienne. Elle est parfaitement naturelle, et la plupart des gens interprètent d'ailleurs *intuitivement* les intervalles de confiance de cette façon (à tort, nous l'avons vu au volume I, section 3.3.2).

### 6.1.5 Intervalle de crédibilité : équi-queue ou HPD ?

Il existe plusieurs façons de fabriquer un intervalle contenant 95 % de la probabilité a posteriori. Les deux principales :

- l'intervalle **à queues égales** : il laisse 2,5 % de probabilité de chaque côté (c'est ce que fait `ppf([0.025, 0.975])`) ;
- l'intervalle de **plus haute densité** (HPD, *highest posterior density*) : le **plus court** intervalle de probabilité 95 %. Tous ses points ont une densité supérieure à ceux qui sont en dehors.

Pour une loi symétrique, ils coïncident. Pour une loi asymétrique (proche de 0 ou de 1, par exemple), ils diffèrent. Prenons un nouveau canal testé auprès de 20 clients, dont un seul a racheté : l'a posteriori est $\mathrm{Beta}(2,20)$, de moyenne 0,0909. L'intervalle à queues égales est [0,0117 ; 0,2382] (largeur 0,2264) ; le HPD, qu'on obtient en faisant glisser une fenêtre de probabilité 95 % le long de la loi et en gardant la plus étroite, est [0,0026 ; 0,2080] (largeur 0,2054).

```python hide
def hpd(loi, masse=0.95, pas=2000):
    """Plus court intervalle de probabilité `masse` : on fait glisser une fenêtre de quantiles."""
    bas = np.linspace(0, 1 - masse, pas)
    largeurs = loi.ppf(bas + masse) - loi.ppf(bas)
    i = largeurs.argmin()
    return loi.ppf(bas[i]), loi.ppf(bas[i] + masse)

# Un cas asymétrique : un nouveau canal testé auprès de 20 clients, 1 seul rachat
asym = stats.beta(1 + 1, 1 + 19)
print("Beta(2, 20)  moyenne :", round(asym.mean(), 4))
print("à queues égales : [%.4f ; %.4f]  largeur %.4f" % (*asym.ppf([0.025, 0.975]), np.diff(asym.ppf([0.025, 0.975]))[0]))
h = hpd(asym)
print("HPD             : [%.4f ; %.4f]  largeur %.4f" % (*h, h[1] - h[0]))
```
<!--sortie-->
```text
Beta(2, 20)  moyenne : 0.0909
à queues égales : [0.0117 ; 0.2382]  largeur 0.2264
HPD             : [0.0026 ; 0.2080]  largeur 0.2054
```

Le HPD est donc plus court et plus proche de zéro, ce qui correspond mieux à l'idée intuitive d'un intervalle qui « suit » la densité. Pour les lois à peu près symétriques de ce chapitre, la différence est mineure ; l'intervalle à queues égales est le plus répandu.

### 6.1.6 Le choix de l'a priori : liberté, responsabilité, et sensibilité

C'est la grande critique adressée à la méthode : « *l'a priori est subjectif* ». Voyons concrètement ce qu'il change.

**Quatre a priori pour une probabilité de rachat $\theta$.**

| A priori | Paramètres | Ce qu'il dit | Pseudo-observations |
|---|---|---|---|
| Uniforme | $\mathrm{Beta}(1,1)$ | « je n'ai aucune idée » | 2 |
| Jeffreys | $\mathrm{Beta}(\tfrac12,\tfrac12)$ | invariant par reparamétrisation (plus de poids aux bords) | 1 |
| Informatif réaliste | $\mathrm{Beta}(20,20)$ | « d'après mon expérience, autour de 50 %, à quelques points près » | 40 |
| Informatif **faux** | $\mathrm{Beta}(2,18)$ | « je suis sûre que très peu de clients rachètent » (≈ 10 %) | 20 |

Comparons les lois a posteriori pour des données de plus en plus abondantes : les **10** premiers clients avec offre (3 rachats), puis les **100** premiers (55 rachats), puis les **1 015** (578 rachats). Voici la moyenne a posteriori et l'intervalle de crédibilité à 95 % :

| $n$ | Uniforme Beta(1,1) | Jeffreys Beta(½,½) | Informatif Beta(20,20) | Informatif faux Beta(2,18) |
|---:|---|---|---|---|
| 10 | 0,333 [0,109 ; 0,610] | 0,318 [0,093 ; 0,606] | 0,460 [0,325 ; 0,598] | **0,167** [0,058 ; 0,317] |
| 100 | 0,549 [0,452 ; 0,644] | 0,550 [0,452 ; 0,645] | 0,536 [0,453 ; 0,617] | 0,475 [0,387 ; 0,564] |
| 1 015 | 0,569 [0,539 ; 0,600] | 0,569 [0,539 ; 0,600] | 0,567 [0,537 ; 0,597] | 0,560 [0,530 ; 0,590] |

Les fréquences observées sont respectivement 0,30, 0,55 et 0,569.

```python hide
avec_offre = clients.loc[clients["offre_bienvenue"] == 1, "rachat_12m"].to_numpy()
priors = {"Uniforme Beta(1,1)": (1, 1), "Jeffreys Beta(.5,.5)": (0.5, 0.5),
          "Informatif Beta(20,20)": (20, 20), "Informatif faux Beta(2,18)": (2, 18)}

lignes = []
for n in (10, 100, len(avec_offre)):
    y = avec_offre[:n].sum()
    for nom, (a, b) in priors.items():
        loi = stats.beta(a + y, b + n - y)
        bas, haut = loi.ppf([0.025, 0.975])
        lignes.append({"n": n, "rachats": int(y), "a priori": nom,
                       "moyenne a posteriori": round(loi.mean(), 3),
                       "IC95 bas": round(bas, 3), "IC95 haut": round(haut, 3)})
sens = pd.DataFrame(lignes)
print(sens.to_string(index=False))
print("\nfréquence observée sur les 10 premiers :", avec_offre[:10].mean(), "| sur les 100 :", avec_offre[:100].mean(),
      "| sur les", len(avec_offre), ":", round(avec_offre.mean(), 3))
```
<!--sortie-->
```text
   n  rachats                   a priori  moyenne a posteriori  IC95 bas  IC95 haut
  10        3         Uniforme Beta(1,1)                 0.333     0.109      0.610
  10        3       Jeffreys Beta(.5,.5)                 0.318     0.093      0.606
  10        3     Informatif Beta(20,20)                 0.460     0.325      0.598
  10        3 Informatif faux Beta(2,18)                 0.167     0.058      0.317
 100       55         Uniforme Beta(1,1)                 0.549     0.452      0.644
 100       55       Jeffreys Beta(.5,.5)                 0.550     0.452      0.645
 100       55     Informatif Beta(20,20)                 0.536     0.453      0.617
 100       55 Informatif faux Beta(2,18)                 0.475     0.387      0.564
1015      578         Uniforme Beta(1,1)                 0.569     0.539      0.600
1015      578       Jeffreys Beta(.5,.5)                 0.569     0.539      0.600
1015      578     Informatif Beta(20,20)                 0.567     0.537      0.597
1015      578 Informatif faux Beta(2,18)                 0.560     0.530      0.590

fréquence observée sur les 10 premiers : 0.3 | sur les 100 : 0.55 | sur les 1015 : 0.569
```

Lisons ce tableau par bloc :

- **$n=10$** : les a priori comptent *beaucoup*. Les quatre résultats diffèrent nettement, et l'a priori « faux » (qui croit à 10 %) tire fortement la moyenne vers le bas.
- **$n=100$** : les écarts se réduisent, mais l'a priori faux pèse encore.
- **$n=1\,015$** : les quatre moyennes a posteriori sont **quasiment égales** (à moins d'un point de pourcentage près : 0,560 à 0,569), même celle de l'a priori faux. L'a priori a été « oublié ».

> 🧪 **C'est un théorème, pas seulement une observation.** Quand $n\to\infty$, tant que l'a priori n'attribue pas une probabilité nulle à la vraie valeur de $\theta$, la loi a posteriori se concentre autour de la vraie valeur, et sa forme devient celle d'une loi normale (théorème de Bernstein-von Mises). Autrement dit : **avec assez de données, des personnes aux a priori différents finissent par être d'accord**. C'est l'argument le plus fort en faveur de la méthode. L'argument le plus fort contre : avec *peu* de données, la conclusion dépend de l'a priori, et il faut alors **le dire**.

> ⚠️ **Trois règles d'hygiène.**
> 1. **Toujours dire quel a priori a été utilisé**, et le justifier en une phrase.
> 2. **Faire une analyse de sensibilité** : refaire le calcul avec deux ou trois a priori raisonnables. Si la conclusion ne change pas, tant mieux ; sinon, c'est une information importante pour le lecteur (« nos données sont insuffisantes pour trancher »).
> 3. **Ne jamais mettre une probabilité nulle** sur une valeur possible : aucune donnée ne pourrait la réhabiliter (c'est la « règle de Cromwell » : « *je vous en conjure, songez que vous puissiez vous tromper* »).

**Les a priori « faiblement informatifs ».** En pratique, ni l'uniforme total ni l'a priori très précis ne sont idéaux. On préfère souvent des lois larges mais qui **excluent l'absurde** : par exemple, pour un coefficient de régression logistique, une loi normale centrée en 0 avec un écart-type de 1,5 ou 2,5 écarte les rapports de cotes de $e^{10}$ tout en laissant passer toutes les valeurs plausibles. Nous les utiliserons en 6.3, et nous verrons en 6.4.3 comment *vérifier* qu'un a priori est raisonnable.

### 6.1.7 Intervalle de crédibilité contre intervalle de confiance : une expérience

Un intervalle de crédibilité à 95 % est-il « bon » au sens fréquentiste ? Faisons l'expérience : fixons une vraie valeur $\theta$, simulons 20 000 échantillons de taille $n=30$, et comptons dans combien de cas chaque intervalle contient $\theta$ (la **couverture**). Nous comparons l'intervalle de Wald (volume I, section 3.3.4), l'intervalle de Wilson et l'intervalle de crédibilité $\mathrm{Beta}(1,1)$ à queues égales. Voici la couverture obtenue (la valeur visée est 0,95) :

| vrai $\theta$ | Wald | Wilson | crédibilité |
|---:|---:|---:|---:|
| 0,05 | 0,781 | 0,940 | 0,940 |
| 0,10 | 0,806 | 0,974 | 0,974 |
| 0,30 | 0,954 | 0,930 | 0,930 |
| 0,50 | 0,958 | 0,958 | 0,958 |

```python hide
from statsmodels.stats.proportion import proportion_confint

def couverture(theta_vrai, n=30, reps=20_000, graine=62):
    rng = np.random.default_rng(graine)
    y = rng.binomial(n, theta_vrai, reps)
    res = {}
    for methode in ("normal", "wilson"):
        bas, haut = proportion_confint(y, n, alpha=0.05, method=methode)
        res[methode] = np.mean((bas <= theta_vrai) & (theta_vrai <= haut))
    loi = stats.beta(1 + y, 1 + n - y)
    bas, haut = loi.ppf(0.025), loi.ppf(0.975)
    res["crédibilité Beta(1,1)"] = np.mean((bas <= theta_vrai) & (theta_vrai <= haut))
    return res

lignes = []
for th in (0.05, 0.10, 0.30, 0.50):
    r = couverture(th)
    lignes.append({"vrai θ": th, "Wald": round(r["normal"], 3), "Wilson": round(r["wilson"], 3),
                   "crédibilité": round(r["crédibilité Beta(1,1)"], 3)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 vrai θ  Wald  Wilson  crédibilité
   0.05 0.781   0.940        0.940
   0.10 0.806   0.974        0.974
   0.30 0.954   0.930        0.930
   0.50 0.958   0.958        0.958
```

Pour $\theta$ proche de 0 (5 % ou 10 %), l'intervalle de Wald est très en dessous de 95 % : il ne couvre la vraie valeur que dans 78 % à 81 % des cas (c'est le défaut connu qu'on avait signalé au volume I). L'intervalle de crédibilité à a priori uniforme, lui, reste dans une fourchette de 93 % à 97 %, ce qui n'a rien d'évident : *il a été construit sans aucun souci de couverture*. Remarquez aussi que sa couverture est **identique** à celle de l'intervalle de Wilson, dans les quatre lignes : ce n'est pas un hasard, les deux intervalles ne diffèrent que de 0,002 au plus pour $n=30$ et décident de la même façon pour chaque valeur possible du nombre de succès. L'approche bayésienne et le meilleur intervalle fréquentiste se rejoignent. C'est un résultat général : sous des hypothèses douces, les intervalles de crédibilité des modèles réguliers ont une bonne couverture fréquentiste quand $n$ est assez grand.

### 6.1.8 Autres couples conjugués : Poisson-Gamma et Normal-Normal

L'idée de conjugaison dépasse le cas bêta-binomial. Voici deux autres couples très utiles ; leurs démonstrations ont **exactement la même structure** (multiplier, reconnaître une forme, normaliser).

**Poisson-Gamma (comptages).** On observe des comptages $y_1,\dots,y_n$ indépendants de loi $\mathrm{Poisson}(\lambda)$, avec $\lambda\sim\mathrm{Gamma}(a,\text{taux }b)$ de densité $\propto\lambda^{a-1}e^{-b\lambda}$.

> 📐 **Théorème.** $\lambda\mid y\;\sim\;\mathrm{Gamma}\!\left(a+\sum_i y_i,\;\; b+n\right)$.
>
> *Démonstration.* $p(y\mid\lambda)\propto\prod_i\lambda^{y_i}e^{-\lambda}=\lambda^{\sum y_i}e^{-n\lambda}$. En multipliant par l'a priori : $p(\lambda\mid y)\propto\lambda^{a+\sum y_i-1}e^{-(b+n)\lambda}$, qui est la densité d'une $\mathrm{Gamma}(a+\sum y_i,\,b+n)$. $\square$

*Exemple à la main.* Cinq semaines, 3, 5, 4, 6, 2 commandes sur le site. A priori $\mathrm{Gamma}(a=2,\ b=0{,}5)$ (moyenne $a/b=4$ commandes par semaine, très vague). $\sum y_i=20$, $n=5$ : a posteriori $\mathrm{Gamma}(22,\ 5{,}5)$, de moyenne $22/5{,}5=4$. (Coïncidence : l'a priori et les données étaient d'accord sur 4.)

Appliquons cela aux **clients acquis par le canal Boutique** : nombre de commandes par an (`nb_commandes_an`), modélisé par $\mathrm{Poisson}(\lambda)$ avec le même $\lambda$ pour tous. Ils sont 504, pour 2 085 commandes au total (moyenne 4,137). Avec l'a priori $\mathrm{Gamma}(2;\,0{,}5)$ (moyenne 4, très vague), l'a posteriori est $\mathrm{Gamma}(2\,087;\ 504{,}5)$, de moyenne 4,137 et d'intervalle de crédibilité à 95 % [3,961 ; 4,316].

```python hide
boutique = clients.loc[clients["canal_acquisition"] == "Boutique", "nb_commandes_an"].to_numpy()
n_b, s_b = len(boutique), boutique.sum()
a0, b0 = 2.0, 0.5                                   # a priori Gamma(2, taux 0,5) : moyenne 4, très vague
post_lam = stats.gamma(a=a0 + s_b, scale=1 / (b0 + n_b))
print(f"clients de la boutique : n = {n_b}, total de commandes = {s_b}, moyenne = {boutique.mean():.3f}")
print(f"a posteriori Gamma({a0 + s_b:.0f}, taux {b0 + n_b:.1f}) : moyenne {post_lam.mean():.3f}, "
      f"IC95 [{post_lam.ppf(0.025):.3f} ; {post_lam.ppf(0.975):.3f}]")
print(f"variance observée / moyenne observée = {boutique.var(ddof=1) / boutique.mean():.2f}   (vaudrait 1 pour une vraie loi de Poisson)")
```
<!--sortie-->
```text
clients de la boutique : n = 504, total de commandes = 2085, moyenne = 4.137
a posteriori Gamma(2087, taux 504.5) : moyenne 4.137, IC95 [3.961 ; 4.316]
variance observée / moyenne observée = 3.32   (vaudrait 1 pour une vraie loi de Poisson)
```

L'intervalle est étroit : on est « sûr » de $\lambda$ à 0,18 près environ. Mais regardons la dispersion : pour une vraie loi de Poisson, variance et moyenne sont égales (volume I, section 2.2) ; ici le rapport variance/moyenne vaut 3,32, soit **plus de trois fois** la valeur attendue. Les clients sont *hétérogènes* (certains commandent beaucoup, d'autres peu), et le modèle de Poisson, qui suppose le même $\lambda$ pour tous, est **faux**. L'intervalle est donc trop étroit, **et le calcul bayésien ne nous l'a pas dit**. Il ne le dit jamais tout seul : un a posteriori est toujours *conditionnel à la validité du modèle*. Nous verrons en 6.4.2 comment vérifier un modèle et en réparer un (c'est aussi le sujet de la section 2.6 pour les modèles surdispersés).

> ⚠️ **Le piège le plus fréquent de la modélisation bayésienne.** Un a posteriori très étroit ne prouve **pas** qu'on est sûr de soi : il prouve qu'on est sûr *si le modèle est juste*. Un modèle faux produit des intervalles étroits et faux, avec la même élégance.

**Normal-Normal (moyenne d'une loi normale, variance connue).** Si $y_i\sim\mathcal N(\mu,\sigma^2)$ avec $\sigma$ connu et $\mu\sim\mathcal N(\mu_0,\tau_0^2)$, alors $\mu\mid y\sim\mathcal N(\mu_n,\tau_n^2)$ avec
$$\frac1{\tau_n^2}=\frac1{\tau_0^2}+\frac n{\sigma^2},\qquad \mu_n=\tau_n^2\left(\frac{\mu_0}{\tau_0^2}+\frac{n\bar y}{\sigma^2}\right).$$
On additionne des **précisions** (l'inverse des variances) et on fait une moyenne **pondérée par les précisions**.

> 📐 **Démonstration.** On écrit les logarithmes : $\log p(\mu\mid y)=\text{cte}-\frac{(\mu-\mu_0)^2}{2\tau_0^2}-\frac{\sum(y_i-\mu)^2}{2\sigma^2}$. Or $\sum(y_i-\mu)^2=\sum(y_i-\bar y)^2+n(\bar y-\mu)^2$ ; le premier terme ne dépend pas de $\mu$. Il reste un polynôme du second degré en $\mu$ :
> $$-\tfrac12\left[\mu^2\left(\tfrac1{\tau_0^2}+\tfrac n{\sigma^2}\right)-2\mu\left(\tfrac{\mu_0}{\tau_0^2}+\tfrac{n\bar y}{\sigma^2}\right)\right]+\text{cte}.$$
> Un polynôme du second degré en $\mu$ dans l'exponentielle est une densité normale ; en « complétant le carré », on lit sa précision $\frac1{\tau_n^2}$ (le coefficient de $\mu^2$) et sa moyenne $\mu_n$ (le rapport entre le coefficient de $\mu$ et celui de $\mu^2$). $\square$

*Exemple à la main.* On s'intéresse à $\mu$ = logarithme du panier moyen d'un client. Supposons $\sigma=0{,}35$ connu (hypothèse de confort, qu'on lèvera en 6.3), un a priori $\mathcal N(4{,}0;\ 0{,}5^2)$, et $n=5$ clients de moyenne $\bar y=4{,}4$. Les précisions valent $1/0{,}5^2=4$ pour l'a priori et $5/0{,}35^2=40{,}82$ pour les données. Précision totale : $44{,}82$, donc $\tau_n=1/\sqrt{44{,}82}=0{,}149$. Moyenne : $\mu_n=\dfrac{4\times4{,}0+40{,}82\times4{,}4}{44{,}82}=\dfrac{16+179{,}6}{44{,}82}=4{,}364$. Les données (91 % du poids) l'emportent largement.

Sur les 449 acheteurs du canal Boutique, la moyenne du log-panier est 4,2183 ; avec les mêmes hypothèses, l'a posteriori de $\mu$ est $\mathcal N(4{,}2181;\ 0{,}0165^2)$, d'intervalle à 95 % [4,1857 ; 4,2504].

```python hide
# Vérification du calcul à la main, puis application aux 504 clients de la boutique
def normal_normal(mu0, tau0, sigma, ybar, n):
    prec = 1 / tau0**2 + n / sigma**2
    return (mu0 / tau0**2 + n * ybar / sigma**2) / prec, 1 / np.sqrt(prec)

mu_n, tau_n = normal_normal(4.0, 0.5, 0.35, 4.4, 5)
print(f"exemple à la main : mu_n = {mu_n:.3f}, tau_n = {tau_n:.3f}   (poids des données : {(5 / 0.35**2) / (1 / 0.5**2 + 5 / 0.35**2):.3f})")

acheteurs = clients[(clients["canal_acquisition"] == "Boutique") & (clients["panier_moyen"] > 0)]
ly = np.log(acheteurs["panier_moyen"])
mu_n, tau_n = normal_normal(4.0, 0.5, 0.35, ly.mean(), len(ly))
print(f"{len(ly)} acheteurs de la boutique : moyenne du log-panier = {ly.mean():.4f}")
print(f"a posteriori de mu : N({mu_n:.4f}, {tau_n:.4f}²) | IC95 [{mu_n - 1.96 * tau_n:.4f} ; {mu_n + 1.96 * tau_n:.4f}]")
print(f"soit un panier « typique » (médiane) de {np.exp(mu_n):.1f} €, IC95 [{np.exp(mu_n - 1.96 * tau_n):.1f} ; {np.exp(mu_n + 1.96 * tau_n):.1f}] €")
```
<!--sortie-->
```text
exemple à la main : mu_n = 4.364, tau_n = 0.149   (poids des données : 0.911)
449 acheteurs de la boutique : moyenne du log-panier = 4.2183
a posteriori de mu : N(4.2181, 0.0165²) | IC95 [4.1857 ; 4.2504]
soit un panier « typique » (médiane) de 67.9 €, IC95 [65.7 ; 70.1] €
```

Le panier « typique » (médiane, puisque $\mu$ est le logarithme) d'un acheteur du canal Boutique est d'environ 67,9 €, intervalle à 95 % [65,7 ; 70,1] €. Les données étant simulées, nous connaissons la vérité : le générateur a programmé un log-panier moyen de $4{,}00+0{,}22=4{,}22$ pour la boutique, soit $e^{4{,}22}\approx68{,}0$ €. L'intervalle de crédibilité contient bien cette valeur.

### 6.1.9 La loi prédictive : prédire du nouveau

Un estimateur de $\theta$ n'est pas un but en soi. La gérante veut des **prédictions** : « *sur les 100 prochains clients avec offre, combien rachèteront ?* » Deux façons de répondre :

- **Plug-in** : on remplace $\theta$ par son estimation $\hat\theta=0{,}5695$ et on prend $\mathrm{Bin}(100,\hat\theta)$. Cela **ignore** l'incertitude sur $\theta$.
- **Prédictive a posteriori** : on **moyenne** la loi binomiale sur toutes les valeurs plausibles de $\theta$, pondérées par leur probabilité a posteriori :
$$p(\tilde y\mid y)=\int p(\tilde y\mid\theta)\,p(\theta\mid y)\,d\theta.$$
Pour un a posteriori bêta, cette intégrale est connue : c'est la loi **bêta-binomiale**. Pour 100 nouveaux clients avec offre, on obtient :

| Méthode | Moyenne | Écart-type | Intervalle à 95 % |
|---|---:|---:|---|
| plug-in $\mathrm{Bin}(100,\hat\theta)$ | 56,95 | 4,95 | [47 ; 67] |
| prédictive bêta-binomiale | 56,93 | 5,19 | [47 ; 67] |
| simulation ($\theta$ puis $y$) | 56,94 | 5,20 | [47 ; 67] |

```python hide
post1 = post[1]
n_nouv = 100
plug = stats.binom(n_nouv, avec_offre.mean())
pred = stats.betabinom(n_nouv, post1.args[0], post1.args[1])

for nom, loi in (("plug-in  Bin(100, θ̂)", plug), ("prédictive bêta-binomiale", pred)):
    print(f"{nom:28s} moyenne {loi.mean():6.2f} | écart-type {loi.std():5.2f} | "
          f"intervalle à 95 % [{loi.ppf(0.025):.0f} ; {loi.ppf(0.975):.0f}]")

# Même chose par simulation : on tire θ dans l'a posteriori, puis y dans Bin(100, θ)
rng = np.random.default_rng(63)
theta_s = post1.rvs(100_000, random_state=rng)
y_s = rng.binomial(n_nouv, theta_s)
print(f"simulation : moyenne {y_s.mean():.2f}, écart-type {y_s.std():.2f}, "
      f"intervalle à 95 % [{np.percentile(y_s, 2.5):.0f} ; {np.percentile(y_s, 97.5):.0f}]")
```
<!--sortie-->
```text
plug-in  Bin(100, θ̂)        moyenne  56.95 | écart-type  4.95 | intervalle à 95 % [47 ; 67]
prédictive bêta-binomiale    moyenne  56.93 | écart-type  5.19 | intervalle à 95 % [47 ; 67]
simulation : moyenne 56.94, écart-type 5.20, intervalle à 95 % [47 ; 67]
```

La loi prédictive est **un peu plus large** que le plug-in (écart-type 5,19 contre 4,95) : elle ajoute à la variabilité du tirage binomial l'incertitude sur $\theta$. Les intervalles à 95 % sont ici identiques ([47 ; 67]) car, avec 1 015 clients dans l'échantillon, l'incertitude sur $\theta$ est faible ; avec 10 clients, l'écart serait énorme. La simulation (tirer $\theta$, puis $y$) retrouve la loi exacte : 56,94 contre 56,93 pour la moyenne. Retenez le principe, car il est général : **une prédiction honnête incorpore l'incertitude sur les paramètres**. C'est un avantage naturel de l'approche bayésienne : la loi prédictive s'obtient sans effort supplémentaire, simplement en simulant (*simuler $\theta$, puis simuler les données sachant $\theta$*), ce que nous ferons systématiquement pour vérifier les modèles en 6.4.

> ✅ **À retenir (6.1).**
> - A posteriori $\propto$ vraisemblance $\times$ a priori. La vraisemblance est celle du volume I.
> - Les **lois conjuguées** (bêta-binomiale, gamma-Poisson, normale-normale) donnent l'a posteriori **exactement**, par simple addition de paramètres ou de précisions.
> - Un **intervalle de crédibilité** autorise la phrase « $\theta$ est dans l'intervalle avec la probabilité 95 % » ; il coïncide numériquement avec l'intervalle de confiance quand l'a priori est plat et les données abondantes.
> - L'a priori compte beaucoup avec peu de données et presque pas avec beaucoup. **Dites-le, justifiez-le, testez-en plusieurs.**
> - Un a posteriori étroit n'est valable que si le **modèle** est juste (le cas du modèle de Poisson ci-dessus).
> - La loi **prédictive** incorpore l'incertitude sur les paramètres.
> - Quand l'a posteriori n'est pas une loi connue (régression logistique, modèles hiérarchiques…), il faut **simuler** : c'est l'objet des sections 6.2 et 6.3.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.1, exercices 6.1 à 6.4.
