# Chapitre 6 : Statistique bayésienne et simulation

> « Toute connaissance est une croyance qu'on a promis de réviser à la lumière des faits. »

Dans le volume I, nous avons mesuré l'incertitude avec des **intervalles de confiance** et des **p-valeurs**. Cette façon de faire, dite *fréquentiste*, répond à la question : « *si je refaisais mon étude des milliers de fois, quelle serait la fréquence de telle ou telle erreur de ma méthode ?* » C'est une réponse rigoureuse… mais ce n'est pas celle que Yasmine attend. Yasmine demande plutôt : « *vu ce que j'ai observé, quelle est la probabilité que l'offre de bienvenue fonctionne ?* ». Une **probabilité sur le paramètre lui-même**.

La statistique **bayésienne** répond directement à cette question, en appliquant la formule de Bayes (volume I, section 2.1) non plus à des événements, mais à des **paramètres inconnus**. Elle y ajoute un ingrédient que le fréquentisme refuse : **ce que l'on sait avant de regarder les données** (la loi *a priori*). En contrepartie, elle exige souvent des calculs d'intégrales que personne ne sait faire à la main : c'est là qu'intervient la **simulation** (Monte-Carlo, MCMC), qui est devenue l'outil central de la modélisation moderne, bayésienne ou non.

## Le chemin de ce chapitre

- **6.1 Inférence bayésienne et lois a priori** : la formule de Bayes pour un paramètre, des exemples à la main, les lois conjuguées, le choix de l'a priori, la loi prédictive.
- **6.2 Méthodes de Monte-Carlo** : estimer une espérance ou une probabilité en **simulant**, vitesse de convergence en $1/\sqrt n$, échantillonnage préférentiel, réduction de variance.
- **6.3 MCMC** : quand on ne sait pas simuler directement, on fabrique une **chaîne de Markov** dont la loi limite est celle qu'on veut. Metropolis-Hastings et Gibbs, écrits en quelques lignes de NumPy.
- **6.4 Vérification des modèles bayésiens** : savoir si la chaîne a convergé, si le modèle est plausible, comment comparer deux modèles.
- ➕ **Pour aller plus loin** : la théorie des **valeurs extrêmes** (6.5) et les **copules** (6.6), qui modélisent les événements rares et la dépendance.
- **6.7 Exercices corrigés**.

> 🧭 **Comment lire ce chapitre.** Les sections 6.1 et 6.2 sont indépendantes l'une de l'autre et se lisent bien d'un trait. La section 6.3 suppose 6.1 (pour le sens de la loi *a posteriori*) et 6.2 (pour le sens d'« échantillon simulé »). La section 6.4 suppose 6.3. Les sections ➕ 6.5 et 6.6 demandent seulement le chapitre 2 du volume I (et, pour la simulation par inversion, la section 6.2.4) ; elles peuvent être lues à part.

> 📦 **Les données utilisées.** Principalement `donnees/clients.csv` (2 000 clients de Dar Jasmin, simulés ; voir l'introduction du volume). Nous nous intéressons surtout à `rachat_12m` (le client a-t-il recommandé dans les 12 mois ?), à `offre_bienvenue` (une offre attribuée **au hasard** à la moitié des clients), à `canal_acquisition` et à `nb_commandes_an`. Comme les données sont **simulées**, nous connaîtrons à la fin la vraie valeur de plusieurs paramètres : ce sera l'occasion de vérifier que la méthode les retrouve.

> ⚠️ **Honnêteté sur les outils.** Les bibliothèques bayésiennes professionnelles (PyMC, Stan) **ne sont pas installées** dans l'environnement qui a servi à produire ce livre. Leur code est montré dans la section 6.3.7, marqué « non exécuté ». Tous les algorithmes dont nous donnons les résultats sont **écrits à la main en NumPy** : c'est aussi la meilleure façon de comprendre ce que ces bibliothèques font à votre place.

> 🛠️ **Matériel.** Tout le code est en Python (NumPy, SciPy, pandas, matplotlib, statsmodels). Les graines sont fixées : vous retrouverez les mêmes nombres que dans le livre, à de très légères variations près selon les versions des bibliothèques.


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

Yasmine envoie une offre de bienvenue à **10 nouveaux clients**. Sept d'entre eux repassent commande dans l'année. Appelons $\theta$ la probabilité qu'un client avec offre rachète. Que sait-on de $\theta$ ?

**Vraisemblance.** Si les clients sont indépendants, le nombre $y$ de rachats suit une loi binomiale $\mathrm{Bin}(10,\theta)$ (volume I, section 2.2) :
$$p(y=7\mid\theta)=\binom{10}{7}\theta^{7}(1-\theta)^{3}.$$

**A priori.** Yasmine n'a aucune idée précise : elle juge que toutes les valeurs de $\theta$ entre 0 et 1 sont également plausibles ($p(\theta)=1$ sur $[0,1]$).

Pour calculer à la main sans intégrale, regardons seulement **onze valeurs** possibles : $\theta\in\{0;\,0{,}1;\,0{,}2;\dots;1\}$, chacune avec la probabilité *a priori* $1/11$. C'est l'**approximation sur grille**. Il suffit de multiplier, puis de diviser par la somme.

Par exemple pour $\theta=0{,}7$ : $\theta^{7}(1-\theta)^{3}=0{,}7^{7}\times0{,}3^{3}=0{,}0823543\times0{,}027=0{,}0022236$. (On peut ignorer le coefficient binomial $\binom{10}{7}$, qui est le même pour toutes les valeurs de $\theta$ et disparaît à la normalisation.) Le code fait les onze calculs :

```python
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

Vérifions que la formule exacte et la grille donnent la même chose, et traçons les trois lois (a priori, vraisemblance normalisée, a posteriori) :

```python
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

L'écart maximal est de l'ordre de la précision d'arrondi : la grille de onze points n'était pas si mauvaise. Remarquez, sur le dessin, que l'*a posteriori* et la vraisemblance normalisée sont **exactement superposés** : avec un a priori plat, **les données parlent seules** (c'est évident dans la formule : multiplier par une constante ne change pas la forme). Avec un a priori informatif $\mathrm{Beta}(5,5)$ (celui d'une personne qui croit déjà à un taux proche de 50 %), l'a posteriori $\mathrm{Beta}(12,8)$ a pour moyenne $12/20=0{,}60$ : il est **tiré vers 0,5**, c'est le compromis de la formule ci-dessus.

> ✅ **À retenir (6.1.1 à 6.1.3).** A posteriori $\propto$ vraisemblance $\times$ a priori. Avec un a priori bêta et des données binomiales, l'a posteriori est une bêta dont les paramètres s'obtiennent en **ajoutant les succès et les échecs observés**. La moyenne a posteriori est un compromis entre a priori et données, où l'a priori pèse de moins en moins quand les données s'accumulent.

### 6.1.4 Application : l'offre de bienvenue fonctionne-t-elle ?

Passons aux 2 000 clients. L'offre de bienvenue a été attribuée **au hasard** à une moitié d'entre eux : la comparaison des deux groupes est donc une vraie expérience (nous y reviendrons dans le chapitre ➕ 7). Les effectifs :

```python
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

Avec un a priori $\mathrm{Beta}(1,1)$ pour chaque groupe, les deux lois a posteriori sont $\mathrm{Beta}(1+y,\,1+n-y)$ :

```python
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
rng = np.random.default_rng(61)
S = 200_000
theta1 = post[1].rvs(S, random_state=rng)
theta0 = post[0].rvs(S, random_state=rng)
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

On peut maintenant prononcer des phrases que le volume I interdisait : « *sachant les données, l'offre augmente le rachat avec une probabilité quasi certaine* » (aucun de nos 200 000 tirages ne donne une différence négative ; l'approximation normale de la différence donne une probabilité d'erreur de l'ordre de $2\times10^{-8}$), « *la probabilité que l'effet dépasse 5 points de pourcentage est de 99,9 %, et qu'il dépasse 10 points de 83 %* ». Pour comparer avec l'approche fréquentiste, calculons l'intervalle de confiance de Wald de la différence de proportions (volume I, section 3.4.5) :

```python
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

Les deux intervalles sont **presque identiques** (à la troisième décimale). C'est normal : avec 1 000 observations par groupe, l'a priori uniforme ne pèse presque rien. Mais l'**interprétation** diffère profondément :

| | Intervalle de confiance (fréquentiste) | Intervalle de crédibilité (bayésien) |
|---|---|---|
| Ce qui est aléatoire | l'intervalle (il change d'un échantillon à l'autre) | le paramètre $\theta$ (notre connaissance) |
| Phrase correcte | « la *méthode* encadre la vraie valeur dans 95 % des échantillons » | « sachant les données, $\delta$ est dans l'intervalle avec la probabilité 0,95 » |
| Peut-on dire « $P(\delta>0)=\dots$ » ? | non | **oui** |
| Dépend d'un a priori ? | non | oui (mais l'effet s'efface quand $n$ grandit) |

> 💡 **Ce que Yasmine veut entendre.** « L'offre est presque certainement utile, et le gain est de l'ordre de 12 points de pourcentage de rachat (entre 8 et 16 avec 95 % de probabilité). » C'est une phrase bayésienne. Elle est parfaitement naturelle, et la plupart des gens interprètent d'ailleurs *intuitivement* les intervalles de confiance de cette façon (à tort, nous l'avons vu au volume I, section 3.3.2).

### 6.1.5 Intervalle de crédibilité : équi-queue ou HPD ?

Il existe plusieurs façons de fabriquer un intervalle contenant 95 % de la probabilité a posteriori. Les deux principales :

- l'intervalle **à queues égales** : il laisse 2,5 % de probabilité de chaque côté (c'est ce que fait `ppf([0.025, 0.975])`) ;
- l'intervalle de **plus haute densité** (HPD, *highest posterior density*) : le **plus court** intervalle de probabilité 95 %. Tous ses points ont une densité supérieure à ceux qui sont en dehors.

Pour une loi symétrique, ils coïncident. Pour une loi asymétrique (proche de 0 ou de 1, par exemple), ils diffèrent :

```python
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

Le HPD est plus court et plus proche de zéro, ce qui correspond mieux à l'idée intuitive d'un intervalle qui « suit » la densité. Pour les lois à peu près symétriques de ce chapitre, la différence est mineure ; l'intervalle à queues égales est le plus répandu.

### 6.1.6 Le choix de l'a priori : liberté, responsabilité, et sensibilité

C'est la grande critique adressée à la méthode : « *l'a priori est subjectif* ». Voyons concrètement ce qu'il change.

**Quatre a priori pour une probabilité de rachat $\theta$.**

| A priori | Paramètres | Ce qu'il dit | Pseudo-observations |
|---|---|---|---|
| Uniforme | $\mathrm{Beta}(1,1)$ | « je n'ai aucune idée » | 2 |
| Jeffreys | $\mathrm{Beta}(\tfrac12,\tfrac12)$ | invariant par reparamétrisation (plus de poids aux bords) | 1 |
| Informatif réaliste | $\mathrm{Beta}(20,20)$ | « d'après mon expérience, autour de 50 %, à quelques points près » | 40 |
| Informatif **faux** | $\mathrm{Beta}(2,18)$ | « je suis sûre que très peu de clients rachètent » (≈ 10 %) | 20 |

Comparons les lois a posteriori pour des données de plus en plus abondantes : les **10** premiers clients avec offre, puis les **100** premiers, puis les **1 015**.

```python
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

Un intervalle de crédibilité à 95 % est-il « bon » au sens fréquentiste ? Faisons l'expérience : fixons une vraie valeur $\theta$, simulons 20 000 échantillons de taille $n=30$, et comptons dans combien de cas chaque intervalle contient $\theta$ (la **couverture**). Nous comparons l'intervalle de Wald (volume I, section 3.3.4), l'intervalle de Wilson et l'intervalle de crédibilité $\mathrm{Beta}(1,1)$ à queues égales.

```python
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

Appliquons cela aux **clients de la boutique** : nombre de commandes par an `nb_commandes_an`, modélisé par $\mathrm{Poisson}(\lambda)$ avec le même $\lambda$ pour tous.

```python
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

L'intervalle est étroit : on est « sûr » de $\lambda$ à 0,18 près environ. Mais regardez la dernière ligne : pour une vraie loi de Poisson, variance et moyenne sont égales (volume I, section 2.2) ; ici la variance est **plusieurs fois supérieure** à la moyenne. Les clients sont *hétérogènes* (certains commandent beaucoup, d'autres peu), et le modèle de Poisson, qui suppose le même $\lambda$ pour tous, est **faux**. L'intervalle est donc trop étroit, **et le calcul bayésien ne nous l'a pas dit**. Il ne le dit jamais tout seul : un a posteriori est toujours *conditionnel à la validité du modèle*. Nous verrons en 6.4.2 comment vérifier un modèle et en réparer un (c'est aussi le sujet de la section 2.6 pour les modèles surdispersés).

> ⚠️ **Le piège le plus fréquent de la modélisation bayésienne.** Un a posteriori très étroit ne prouve **pas** qu'on est sûr de soi : il prouve qu'on est sûr *si le modèle est juste*. Un modèle faux produit des intervalles étroits et faux, avec la même élégance.

**Normal-Normal (moyenne d'une loi normale, variance connue).** Si $y_i\sim\mathcal N(\mu,\sigma^2)$ avec $\sigma$ connu et $\mu\sim\mathcal N(\mu_0,\tau_0^2)$, alors $\mu\mid y\sim\mathcal N(\mu_n,\tau_n^2)$ avec
$$\frac1{\tau_n^2}=\frac1{\tau_0^2}+\frac n{\sigma^2},\qquad \mu_n=\tau_n^2\left(\frac{\mu_0}{\tau_0^2}+\frac{n\bar y}{\sigma^2}\right).$$
On additionne des **précisions** (l'inverse des variances) et on fait une moyenne **pondérée par les précisions**.

> 📐 **Démonstration.** On écrit les logarithmes : $\log p(\mu\mid y)=\text{cte}-\frac{(\mu-\mu_0)^2}{2\tau_0^2}-\frac{\sum(y_i-\mu)^2}{2\sigma^2}$. Or $\sum(y_i-\mu)^2=\sum(y_i-\bar y)^2+n(\bar y-\mu)^2$ ; le premier terme ne dépend pas de $\mu$. Il reste un polynôme du second degré en $\mu$ :
> $$-\tfrac12\left[\mu^2\left(\tfrac1{\tau_0^2}+\tfrac n{\sigma^2}\right)-2\mu\left(\tfrac{\mu_0}{\tau_0^2}+\tfrac{n\bar y}{\sigma^2}\right)\right]+\text{cte}.$$
> Un polynôme du second degré en $\mu$ dans l'exponentielle est une densité normale ; en « complétant le carré », on lit sa précision $\frac1{\tau_n^2}$ (le coefficient de $\mu^2$) et sa moyenne $\mu_n$ (le rapport entre le coefficient de $\mu$ et celui de $\mu^2$). $\square$

*Exemple à la main.* On s'intéresse à $\mu$ = logarithme du panier moyen d'un client de la boutique. Supposons $\sigma=0{,}35$ connu (hypothèse de confort, qu'on lèvera en 6.3), un a priori $\mathcal N(4{,}0;\ 0{,}5^2)$, et $n=5$ clients de moyenne $\bar y=4{,}4$. Les précisions valent $1/0{,}5^2=4$ pour l'a priori et $5/0{,}35^2=40{,}82$ pour les données. Précision totale : $44{,}82$, donc $\tau_n=1/\sqrt{44{,}82}=0{,}149$. Moyenne : $\mu_n=\dfrac{4\times4{,}0+40{,}82\times4{,}4}{44{,}82}=\dfrac{16+179{,}6}{44{,}82}=4{,}364$. Les données (91 % du poids) l'emportent largement.

```python
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
print(f"soit un panier « typique » (médiane) de {np.exp(mu_n):.1f} DT, IC95 [{np.exp(mu_n - 1.96 * tau_n):.1f} ; {np.exp(mu_n + 1.96 * tau_n):.1f}] DT")
```
<!--sortie-->
```text
exemple à la main : mu_n = 4.364, tau_n = 0.149   (poids des données : 0.911)
449 acheteurs de la boutique : moyenne du log-panier = 4.2183
a posteriori de mu : N(4.2181, 0.0165²) | IC95 [4.1857 ; 4.2504]
soit un panier « typique » (médiane) de 67.9 DT, IC95 [65.7 ; 70.1] DT
```

Le panier « typique » (médiane, puisque $\mu$ est le logarithme) d'un acheteur de la boutique est d'environ 68 DT, avec une incertitude d'environ $\pm2$ DT. Les données étant simulées, nous connaissons la vérité : le générateur a programmé un log-panier moyen de $4{,}00+0{,}22=4{,}22$ pour la boutique, soit $e^{4{,}22}\approx68{,}0$ DT. L'intervalle de crédibilité contient bien cette valeur.

### 6.1.9 La loi prédictive : prédire du nouveau

Un estimateur de $\theta$ n'est pas un but en soi. Yasmine veut des **prédictions** : « *sur les 100 prochains clients avec offre, combien rachèteront ?* » Deux façons de répondre :

- **Plug-in** : on remplace $\theta$ par son estimation $\hat\theta=0{,}5695$ et on prend $\mathrm{Bin}(100,\hat\theta)$. Cela **ignore** l'incertitude sur $\theta$.
- **Prédictive a posteriori** : on **moyenne** la loi binomiale sur toutes les valeurs plausibles de $\theta$, pondérées par leur probabilité a posteriori :
$$p(\tilde y\mid y)=\int p(\tilde y\mid\theta)\,p(\theta\mid y)\,d\theta.$$
Pour un a posteriori bêta, cette intégrale est connue : c'est la loi **bêta-binomiale**.

```python
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


## 6.2 Méthodes de Monte-Carlo

> 💡 **Intuition.** Comment connaître la probabilité de faire un « double six » avec deux dés ? On peut raisonner ($1/36$). Ou bien… **lancer les dés** dix mille fois et compter. La seconde méthode est moins élégante, mais elle a une qualité inestimable : elle marche **aussi** quand le raisonnement est impossible. Tout le monde ne sait pas calculer la probabilité qu'un portefeuille perde plus de 10 %, ou la probabilité qu'une loi *a posteriori* complexe dépasse un seuil. Mais tout le monde peut **simuler** et compter. Le nom vient du casino de Monte-Carlo, où le hasard est le métier. La méthode a été mise au point à Los Alamos dans les années 1940.

### 6.2.1 Le principe : une espérance se calcule en moyennant des simulations

Presque tout ce que l'on veut calculer en probabilités et en statistique est une **espérance** :
- une probabilité est l'espérance d'un indicateur : $P(X\in A)=\mathbb E[\mathbf 1_{A}(X)]$ ;
- une intégrale $\int g(x)f(x)\,dx$ est l'espérance $\mathbb E[g(X)]$ pour $X$ de densité $f$ ;
- une moyenne a posteriori, un risque, un prix, une probabilité de ruine…

La loi des grands nombres (volume I, section 2.4) dit que la moyenne empirique converge vers l'espérance. D'où l'idée :

> **Estimateur de Monte-Carlo.** Pour estimer $\theta=\mathbb E[g(X)]$, on simule $X_1,\dots,X_n$ indépendants de même loi que $X$, et on prend
> $$\hat\theta_n=\frac1n\sum_{i=1}^n g(X_i).$$

**Exemple à la main : estimer $\pi$ avec des fléchettes.** On lance des fléchettes uniformément dans le carré $[0,1]^2$. La probabilité de tomber dans le quart de disque $x^2+y^2<1$ est son aire, $\pi/4$. Donc $\pi=4\,\mathbb E[\mathbf 1\{X^2+Y^2<1\}]$. Voici dix fléchettes (choisies une fois pour toutes) ; on vérifie à la main pour chacune si $x^2+y^2<1$ :

| fléchette | $(x,y)$ | $x^2+y^2$ | dedans ? |
|---|---|---|---|
| 1 | (0,10 ; 0,90) | 0,82 | oui |
| 2 | (0,80 ; 0,70) | 1,13 | non |
| 3 | (0,35 ; 0,20) | 0,1625 | oui |
| 4 | (0,95 ; 0,30) | 0,9925 | oui |
| 5 | (0,60 ; 0,55) | 0,6625 | oui |
| 6 | (0,05 ; 0,15) | 0,025 | oui |
| 7 | (0,90 ; 0,90) | 1,62 | non |
| 8 | (0,45 ; 0,85) | 0,925 | oui |
| 9 | (0,70 ; 0,10) | 0,50 | oui |
| 10 | (0,25 ; 0,65) | 0,485 | oui |

Huit fléchettes sur dix sont dedans : $\hat\pi=4\times0{,}8=3{,}2$. Pas très précis, mais l'idée est là. Laissons maintenant l'ordinateur lancer plus de fléchettes :

```python
import numpy as np
import pandas as pd
from scipy import stats

pts = np.array([(0.10, 0.90), (0.80, 0.70), (0.35, 0.20), (0.95, 0.30), (0.60, 0.55),
                (0.05, 0.15), (0.90, 0.90), (0.45, 0.85), (0.70, 0.10), (0.25, 0.65)])
dedans = (pts**2).sum(axis=1) < 1
print("dix fléchettes à la main : dedans =", int(dedans.sum()), "-> pi estimé =", 4 * dedans.mean())

rng = np.random.default_rng(620)
lignes = []
for n in (100, 1_000, 10_000, 100_000, 1_000_000):
    xy = rng.random((n, 2))
    indic = ((xy**2).sum(axis=1) < 1)
    est = 4 * indic.mean()
    se_th = np.sqrt(np.pi * (4 - np.pi) / n)           # écart-type théorique de l'estimateur (voir plus bas)
    lignes.append({"n": n, "estimation": round(est, 5), "erreur": round(est - np.pi, 5), "écart-type théorique": round(se_th, 5)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
dix fléchettes à la main : dedans = 8 -> pi estimé = 3.2
      n  estimation   erreur  écart-type théorique
    100     3.12000 -0.02159               0.16422
   1000     3.15200  0.01041               0.05193
  10000     3.13000 -0.01159               0.01642
 100000     3.13760 -0.00399               0.00519
1000000     3.14366  0.00207               0.00164
```

L'estimation s'approche de $\pi$ quand $n$ grandit, **sans jamais être exacte**. Mais à quelle vitesse ? C'est la question suivante.

### 6.2.2 La vitesse de convergence : $1/\sqrt n$

Chaque terme $g(X_i)$ est une variable aléatoire de variance $\sigma^2=\mathrm{Var}(g(X))$. L'estimateur $\hat\theta_n$ est sans biais, et, puisque les $X_i$ sont indépendants (volume I, section 2.3) :
$$\mathrm{Var}(\hat\theta_n)=\frac{\sigma^2}{n},\qquad\text{donc}\qquad \text{erreur type}=\frac{\sigma}{\sqrt n}.$$
Le théorème central limite (volume I, section 2.4) dit en plus que, pour $n$ grand, $\hat\theta_n\approx\mathcal N(\theta,\sigma^2/n)$ : on obtient donc un **intervalle de confiance** de Monte-Carlo, $\hat\theta_n\pm1{,}96\,\hat\sigma/\sqrt n$, où $\hat\sigma$ est l'écart-type empirique des $g(X_i)$. Pour $\pi$, $g=4\cdot\mathbf 1\{\dots\}$ est une variable qui vaut 4 avec la probabilité $p=\pi/4$ et 0 sinon, d'où $\sigma^2=16\,p(1-p)=\pi(4-\pi)$ : c'est la formule utilisée dans le code ci-dessus.

**Conséquence pratique.** Pour **diviser l'erreur par 10**, il faut **100 fois plus de simulations**. Pour gagner une décimale de précision, 100 fois plus de calcul. C'est lent. Vérifions-le par une expérience : pour chaque $n$, on répète 300 fois l'estimation de $\pi$ et on mesure l'écart-type observé des estimations.

```python
rng = np.random.default_rng(621)
tailles = [100, 1_000, 10_000, 100_000]
reps = 300
ecarts = []
for n in tailles:
    estimations = np.array([4 * ((rng.random((n, 2))**2).sum(axis=1) < 1).mean() for _ in range(reps)])
    ecarts.append(estimations.std(ddof=1))
ecarts = np.array(ecarts)
th = np.sqrt(np.pi * (4 - np.pi) / np.array(tailles))
pente = np.polyfit(np.log10(tailles), np.log10(ecarts), 1)[0]

print(pd.DataFrame({"n": tailles, "écart-type observé": ecarts.round(5), "théorie σ/√n": th.round(5)}).to_string(index=False))
print(f"\npente de log(écart-type) en fonction de log(n) : {pente:.3f}   (théorie : -0.5)")
```
<!--sortie-->
```text
     n  écart-type observé  théorie σ/√n
   100             0.16832       0.16422
  1000             0.05164       0.05193
 10000             0.01591       0.01642
100000             0.00503       0.00519

pente de log(écart-type) en fonction de log(n) : -0.508   (théorie : -0.5)
```

La pente vaut presque exactement $-1/2$ : doubler le nombre de chiffres décimaux coûte un facteur $10^4$ en simulations.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.facecolor": "#fcfcfb",
                     "figure.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
                     "legend.frameon": False, "font.size": 10})

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.0), gridspec_kw={"width_ratios": [1, 1.1]})

# Panneau de gauche : 1 000 fléchettes
rng = np.random.default_rng(622)
xy = rng.random((1000, 2))
in_ = (xy**2).sum(axis=1) < 1
ax1.scatter(xy[in_, 0], xy[in_, 1], s=7, color=BLEU, alpha=0.8, label="dedans")
ax1.scatter(xy[~in_, 0], xy[~in_, 1], s=7, color=ORANGE, alpha=0.8, label="dehors")
t = np.linspace(0, np.pi / 2, 200)
ax1.plot(np.cos(t), np.sin(t), color="#0b0b0b", lw=1.0)
ax1.set_aspect("equal")
ax1.set_xlim(0, 1)
ax1.set_ylim(0, 1)
ax1.grid(False)
ax1.set_title(f"1 000 fléchettes : {in_.sum()} dedans, soit π ≈ {4 * in_.mean():.3f}")
ax1.legend(loc="upper center", bbox_to_anchor=(0.5, -0.06), ncol=2, markerscale=2.5)

# Panneau de droite : écart-type en fonction de n (échelles log-log)
ax2.loglog(tailles, ecarts, "o-", color=BLEU, lw=1.8)
ax2.loglog(tailles, th, "--", color="#898781", lw=1.4)
ax2.text(110, 0.0075, "points bleus : écart-type observé\ntirets gris : théorie σ/√n (pente −1/2)", color="#52514e", va="center")
ax2.set_xlabel("nombre de simulations n")
ax2.set_ylabel("écart-type de l'estimateur de π")
ax2.set_title("Erreur de l'estimateur selon n")
plt.tight_layout()
plt.savefig("figures/ch06-monte-carlo-pi.png", dpi=200, bbox_inches="tight")
plt.close()
```

![À gauche : 1 000 fléchettes dans le carré, bleues si elles tombent dans le quart de disque, orange sinon. À droite : l'écart-type de l'estimateur de π en fonction du nombre de simulations, en échelles logarithmiques ; il suit la droite de pente −1/2.](figures/ch06-monte-carlo-pi.png)

> 💡 **Pourquoi utiliser une méthode si lente ?** En dimension 1, une méthode déterministe (les rectangles du volume I, section 1.2) est bien plus efficace : l'erreur de la règle des trapèzes décroît comme $1/n^2$. Mais la vitesse $1/\sqrt n$ de Monte-Carlo a une propriété extraordinaire : **elle ne dépend pas de la dimension**. Un quadrillage de 10 points par axe demande $10^{d}$ évaluations en dimension $d$ ; Monte-Carlo, lui, garde le même rythme. Illustration : le volume de la boule unité en dimension 10, dont la valeur exacte est $\pi^{5}/5!\approx2{,}5502$.

```python
from math import gamma, pi

d = 10
rng = np.random.default_rng(624)
n = 1_000_000
pts_d = rng.uniform(-1, 1, size=(n, d))                  # points dans le cube [-1, 1]^10 (volume 2^10)
dans_boule = (pts_d**2).sum(axis=1) < 1
vol_est = 2**d * dans_boule.mean()
se = 2**d * dans_boule.std(ddof=1) / np.sqrt(n)
vol_exact = pi**(d / 2) / gamma(d / 2 + 1)
print(f"boule unité, dimension {d}")
print(f"estimation Monte-Carlo : {vol_est:.4f}  ± {1.96 * se:.4f} (IC à 95 %)   | valeur exacte : {vol_exact:.4f}")
print(f"fraction de points tombés dans la boule : {dans_boule.mean():.5f}  ({dans_boule.sum()} sur {n})")
print(f"un quadrillage de 10 points par axe aurait demandé {10**d:,} évaluations".replace(",", " "))
```
<!--sortie-->
```text
boule unité, dimension 10
estimation Monte-Carlo : 2.6020  ± 0.1010 (IC à 95 %)   | valeur exacte : 2.5502
fraction de points tombés dans la boule : 0.00254  (2541 sur 1000000)
un quadrillage de 10 points par axe aurait demandé 10 000 000 000 évaluations
```

> ⚠️ **Le revers de la médaille.** Remarquez que seule une fraction minuscule des points tombe dans la boule en dimension 10 (2 541 sur un million, soit 0,25 %) : le cube est « presque vide de boule ». Cette inefficacité s'aggrave avec la dimension. Les sections 6.2.5 (échantillonnage préférentiel) et 6.3 (MCMC) sont les réponses à ce problème : mettre les points **là où ils comptent**.

### 6.2.3 Application : faut-il envoyer l'offre de bienvenue à tout le monde ?

En 6.1.4, nous avons montré que l'offre de bienvenue augmente la probabilité de rachat d'environ 12 points. Mais elle **coûte** quelque chose : la remise accordée. Faut-il l'offrir à tous les futurs clients ?

Posons les hypothèses de l'étude (inventées pour l'exercice, à remplacer par les vraies valeurs de Dar Jasmin) :
- la marge de Yasmine est de **30 %** du panier ;
- l'offre coûte **1,50 DT par client** (la remise, quel que soit le client) ;
- un client qui rachète génère un panier tiré au hasard parmi les paniers des acheteurs observés (la distribution empirique, qui est notre meilleure image de la loi des paniers).

Le gain net **par client** de la politique « envoyer l'offre » vaut donc
$$G=(\theta_1-\theta_0)\times m-c,\qquad m=0{,}30\times\text{panier moyen d'un acheteur},\quad c=1{,}50.$$
Les inconnues sont $\theta_1,\theta_0$ (nous avons leurs lois a posteriori, 6.1.4) et $m$ (nous le « simulons » par rééchantillonnage des paniers observés, c'est un bootstrap). Monte-Carlo permet de propager **toute** l'incertitude jusqu'au résultat, ce qu'aucune formule simple ne ferait :

```python
clients = pd.read_csv("donnees/clients.csv")
# Rappel de 6.1.4 : lois a posteriori Beta(1 + succès, 1 + échecs) pour chaque groupe
resume = clients.groupby("offre_bienvenue")["rachat_12m"].agg(["size", "sum"])
post0 = stats.beta(1 + resume.loc[0, "sum"], 1 + resume.loc[0, "size"] - resume.loc[0, "sum"])
post1 = stats.beta(1 + resume.loc[1, "sum"], 1 + resume.loc[1, "size"] - resume.loc[1, "sum"])

paniers = clients.loc[clients["panier_moyen"] > 0, "panier_moyen"].to_numpy()
marge, cout = 0.30, 1.50

rng = np.random.default_rng(625)
S = 100_000
theta1 = post1.rvs(S, random_state=rng)
theta0 = post0.rvs(S, random_state=rng)
# incertitude sur la marge moyenne : bootstrap de la moyenne des paniers
m_boot = marge * np.array([rng.choice(paniers, len(paniers)).mean() for _ in range(S // 20)])
m = rng.choice(m_boot, S)                                  # on en tire S valeurs
G = (theta1 - theta0) * m - cout                           # gain net par client, S scénarios

print(f"marge moyenne par rachat : {marge * paniers.mean():.2f} DT (panier moyen des acheteurs : {paniers.mean():.2f} DT)")
print(f"gain net moyen par client : {G.mean():+.3f} DT")
print(f"intervalle à 90 %         : [{np.percentile(G, 5):+.3f} ; {np.percentile(G, 95):+.3f}] DT")
print(f"P(l'offre est rentable)   : {(G > 0).mean():.3f}")
print(f"pour 5 000 nouveaux clients : gain attendu {5000 * G.mean():+.0f} DT ; "
      f"dans 95 % des scénarios le gain dépasse {5000 * np.percentile(G, 5):+.0f} DT")
```
<!--sortie-->
```text
marge moyenne par rachat : 18.37 DT (panier moyen des acheteurs : 61.23 DT)
gain net moyen par client : +0.731 DT
intervalle à 90 %         : [+0.062 ; +1.400] DT
P(l'offre est rentable)   : 0.964
pour 5 000 nouveaux clients : gain attendu +3656 DT ; dans 95 % des scénarios le gain dépasse +312 DT
```

C'est le genre de réponse qu'attend vraiment une décisionnaire : pas « l'effet est significatif » mais « *l'offre est très probablement rentable (environ 96 % de chances), le gain attendu est de 0,73 DT par client, soit 3 700 DT pour 5 000 clients, et dans 95 % des scénarios on gagne au moins 300 DT* ». Remarquez que le gain par client reste **modeste** et que l'intervalle à 90 % ([+0,06 ; +1,40] DT) s'approche de zéro : l'offre n'est pas une mine d'or, et un coût de 2 DT (au lieu de 1,50) la rendrait douteuse. Les chiffres de coût et de marge étant inventés, la bonne pratique est de refaire le calcul pour plusieurs valeurs. Observez aussi que **toutes** les sources d'incertitude (les deux taux, la marge) sont propagées d'un seul mouvement, simplement en les simulant ensemble.

> 🧪 **Point de rigueur.** Le calcul suppose que l'effet de l'offre sur le rachat se traduit, pour chaque client qui rachète en plus, par un panier « moyen ». Dans les données simulées, l'offre agit sur la *probabilité* de rachat (c'est vrai par construction) ; une vraie étude vérifierait aussi si les clients « incités » dépensent autant que les autres. Un modèle ne répond qu'à la question qu'on lui a posée.

### 6.2.4 Fabriquer des tirages : l'inversion et le rejet

Jusqu'ici, nous avons utilisé `rng.random`, `stats.beta.rvs`, etc., comme des boîtes noires. Comment un ordinateur fabrique-t-il un tirage dans une loi donnée ? Voici les deux méthodes de base, qui expliquent aussi pourquoi les lois *a posteriori* compliquées posent problème.

**Méthode 1 : l'inversion.** On part d'une loi uniforme $U\sim\mathcal U(0,1)$, que l'ordinateur sait fabriquer.

> 📐 **Théorème (inversion).** Soit $F$ une fonction de répartition continue et strictement croissante, d'inverse $F^{-1}$. Alors $X=F^{-1}(U)$ a pour fonction de répartition $F$.
>
> *Démonstration.* Pour tout $x$, $P(X\le x)=P(F^{-1}(U)\le x)=P(U\le F(x))=F(x)$, car $F$ est croissante et $P(U\le u)=u$ pour $u\in[0,1]$. $\square$

*Exemple.* Le délai d'attente d'un colis suit une loi exponentielle de moyenne 3 jours, $F(x)=1-e^{-x/3}$. En résolvant $u=1-e^{-x/3}$ : $x=-3\ln(1-u)$. On simule donc des délais avec `-3 * np.log(1 - u)`.

```python
rng = np.random.default_rng(626)
u = rng.random(100_000)
delais = -3 * np.log(1 - u)                       # inversion : F^{-1}(u) pour F(x) = 1 - exp(-x/3)
print(f"moyenne simulée : {delais.mean():.3f} (théorie : 3)   écart-type : {delais.std():.3f} (théorie : 3)")
for x in (1, 3, 6, 9):
    print(f"P(délai ≤ {x}) : simulé {np.mean(delais <= x):.4f} | exact {1 - np.exp(-x / 3):.4f}")
```
<!--sortie-->
```text
moyenne simulée : 3.007 (théorie : 3)   écart-type : 3.001 (théorie : 3)
P(délai ≤ 1) : simulé 0.2832 | exact 0.2835
P(délai ≤ 3) : simulé 0.6311 | exact 0.6321
P(délai ≤ 6) : simulé 0.8642 | exact 0.8647
P(délai ≤ 9) : simulé 0.9499 | exact 0.9502
```

L'inversion est parfaite quand on connaît $F^{-1}$ (exponentielle, Weibull, Cauchy…), mais ce n'est **presque jamais** le cas pour une loi *a posteriori* : on ne sait même pas calculer $F$.

**Méthode 2 : le rejet.** Supposons qu'on connaisse la densité cible $f$ (même à une constante près) et qu'on sache simuler selon une loi plus simple de densité $g$, avec $f(x)\le M\,g(x)$ pour tout $x$. L'algorithme :

1. tirer $X\sim g$ et $U\sim\mathcal U(0,1)$ indépendants ;
2. **accepter** $X$ si $U\le \dfrac{f(X)}{M\,g(X)}$, sinon recommencer.

> 📐 **Théorème.** Les valeurs acceptées ont pour densité $f$, et la probabilité d'acceptation est $1/M$.
>
> *Démonstration.* La probabilité d'accepter un tirage $X\in dx$ est $g(x)\,dx\cdot\dfrac{f(x)}{Mg(x)}=\dfrac{f(x)}{M}dx$. Sommée sur $x$, elle vaut $\int\dfrac{f}{M}=\dfrac1M$ : c'est la probabilité d'acceptation. La densité de $X$ **sachant qu'il est accepté** est donc $\dfrac{f(x)/M}{1/M}=f(x)$. $\square$

*Exemple.* Simulons la loi a posteriori $\mathrm{Beta}(8,4)$ de 6.1 avec une proposition uniforme sur $[0,1]$ ($g=1$). Il faut $M\ge\max f$ : le maximum de la densité est atteint en $\theta=(8-1)/(8+4-2)=0{,}7$ et vaut environ 2,94.

```python
cible = stats.beta(8, 4)
M = cible.pdf(0.7)
print(f"maximum de la densité Beta(8,4) : M = {M:.4f}   -> probabilité d'acceptation théorique 1/M = {1 / M:.4f}")

rng = np.random.default_rng(627)
n_essais = 200_000
x = rng.random(n_essais)                              # proposition : uniforme, g = 1
accepte = rng.random(n_essais) <= cible.pdf(x) / M    # test d'acceptation
echantillon = x[accepte]
print(f"taux d'acceptation observé : {accepte.mean():.4f}   |  tirages conservés : {len(echantillon)}")
print(f"moyenne : {echantillon.mean():.4f} (exacte {cible.mean():.4f})  |  écart-type : {echantillon.std():.4f} (exact {cible.std():.4f})")
print("quantiles 5 %, 50 %, 95 % :", np.percentile(echantillon, [5, 50, 95]).round(4), "| exacts :", cible.ppf([0.05, 0.5, 0.95]).round(4))
```
<!--sortie-->
```text
maximum de la densité Beta(8,4) : M = 2.9351   -> probabilité d'acceptation théorique 1/M = 0.3407
taux d'acceptation observé : 0.3428   |  tirages conservés : 68564
moyenne : 0.6665 (exacte 0.6667)  |  écart-type : 0.1305 (exact 0.1307)
quantiles 5 %, 50 %, 95 % : [0.4361 0.6763 0.8641] | exacts : [0.4356 0.6762 0.8649]
```

Le rejet marche, mais gaspille : environ deux tirages sur trois sont jetés. En dimension 10 ou 100, la constante $M$ devient astronomique et l'acceptation tombe à presque zéro : c'est la **malédiction de la dimension** (ce que le volume de la boule laissait deviner). Il faut une autre idée : celle des chaînes de Markov, en 6.3.

### 6.2.5 L'échantillonnage préférentiel (*importance sampling*)

Quand on cherche la probabilité d'un événement **rare**, simuler naïvement est désespérant : on attend longtemps un seul succès. Exemple : $P(Z>4)$ pour $Z\sim\mathcal N(0,1)$, qui vaut $3{,}17\times10^{-5}$ (environ une chance sur 31 600). Avec 10 000 tirages, on s'attend à $0{,}3$ succès : le plus souvent, l'estimateur naïf vaut 0.

L'idée de l'échantillonnage préférentiel : **tirer là où l'événement se produit**, puis **corriger** le biais par des poids. Pour estimer $\mathbb E_f[g(X)]=\int g(x)f(x)dx$, on tire $X_i\sim h$ (une autre densité, qui charge davantage la zone d'intérêt) et on écrit
$$\int g(x)f(x)dx=\int g(x)\frac{f(x)}{h(x)}h(x)dx=\mathbb E_h\!\left[g(X)\,w(X)\right],\qquad w=\frac fh .$$
L'estimateur $\hat\theta=\frac1n\sum g(X_i)w(X_i)$ est donc **sans biais** (même démonstration : un changement de variable dans l'intégrale), pourvu que $h>0$ partout où $gf\ne0$. Pour $P(Z>4)$, on choisit $h=\mathcal N(4,1)$ : la moitié des tirages dépasse 4.

```python
def naif(n, rng):
    return (rng.standard_normal(n) > 4).mean()

def preferentiel(n, rng):
    x = rng.normal(4, 1, n)                                    # on tire autour de 4
    w = stats.norm.pdf(x) / stats.norm.pdf(x, loc=4, scale=1)  # poids f/h
    return np.mean((x > 4) * w)

exact = stats.norm.sf(4)
rng = np.random.default_rng(628)
n, reps = 10_000, 300
a = np.array([naif(n, rng) for _ in range(reps)])
b = np.array([preferentiel(n, rng) for _ in range(reps)])
print(f"valeur exacte P(Z>4)       : {exact:.3e}")
print(f"estimateur naïf            : moyenne {a.mean():.3e} | écart-type {a.std():.3e} | estimations nulles : {(a == 0).mean():.0%}")
print(f"échantillonnage préférentiel: moyenne {b.mean():.3e} | écart-type {b.std():.3e}")
print(f"gain en écart-type : facteur {a.std() / b.std():.0f}  ->  gain en nombre de tirages : facteur {(a.std() / b.std())**2:,.0f}".replace(",", " "))
```
<!--sortie-->
```text
valeur exacte P(Z>4)       : 3.167e-05
estimateur naïf            : moyenne 3.567e-05 | écart-type 5.798e-05 | estimations nulles : 69%
échantillonnage préférentiel: moyenne 3.172e-05 | écart-type 6.752e-07
gain en écart-type : facteur 86  ->  gain en nombre de tirages : facteur 7 372
```

L'écart-type de l'estimateur naïf (5,8 $\times10^{-5}$) est plus grand que la quantité à estimer elle-même ($3{,}2\times10^{-5}$), et 69 % des estimations naïves valent exactement 0. Celui de l'échantillonnage préférentiel (6,8 $\times10^{-7}$) est 86 fois plus petit, ce qui équivaut à $86^2\approx7\,400$ fois plus de tirages pour la même précision. Quand on connaît la forme de la zone d'intérêt, c'est un gain colossal.

> ⚠️ **Choisir $h$ avec soin.** Une proposition mal placée peut être aussi mauvaise que la méthode naïve : trop loin de la zone d'intérêt, quelques tirages portent presque tout le poids et l'estimation devient instable. On mesure cette dégénérescence par la **taille d'échantillon effective** (*effective sample size*), calculée sur les contributions $c_i=g(X_i)\,w(X_i)$ :
> $$\mathrm{ESS}=\frac{\left(\sum_i c_i\right)^2}{\sum_i c_i^{2}},$$
> qui vaut $n$ si toutes les contributions sont égales et 1 si un seul tirage porte tout. Nous retrouverons cette idée d'ESS en 6.4. Faisons varier le centre $c$ de la proposition $h=\mathcal N(c,1)$ (le cas $c=0$ est la méthode naïve) :

```python
def ess(v):
    return v.sum()**2 / (v**2).sum() if v.sum() > 0 else 0.0

rng = np.random.default_rng(629)
lignes = []
for centre in (0, 2, 3, 4, 5, 6, 8):
    estim, ess_, touche = [], [], []
    for _ in range(300):
        x = rng.normal(centre, 1, 10_000)
        contrib = (x > 4) * stats.norm.pdf(x) / stats.norm.pdf(x, loc=centre, scale=1)
        estim.append(contrib.mean()); ess_.append(ess(contrib)); touche.append((x > 4).mean())
    estim = np.array(estim)
    lignes.append({"centre c": centre, "part de tirages > 4": round(np.mean(touche), 4), "ESS moyenne": round(np.mean(ess_), 1),
                   "écart-type de l'estimateur": f"{estim.std():.2e}", "erreur relative": round(estim.std() / exact, 3)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 centre c  part de tirages > 4  ESS moyenne écart-type de l'estimateur  erreur relative
        0               0.0000          0.3                   6.16e-05            1.946
        2               0.0228        187.1                   2.34e-06            0.074
        3               0.1584        965.9                   1.04e-06            0.033
        4               0.4996       1814.0                   6.81e-07            0.022
        5               0.8413       1235.0                   8.03e-07            0.025
        6               0.9771        304.9                   1.68e-06            0.053
        8               1.0000          3.2                   3.53e-05            1.114
```

Le tableau raconte toute l'histoire. Avec $c=0$ (méthode naïve), pratiquement aucun tirage ne dépasse 4 : l'ESS est inférieure à 1 et l'erreur relative est de l'ordre de 200 %. En se rapprochant de 4, la part de tirages utiles croît, l'ESS atteint **son maximum autour de $c=4$** (environ 1 800 tirages « effectifs » sur 10 000) et l'erreur relative tombe à environ 2 %. Mais si l'on place la proposition **trop loin** ($c=8$), tous les tirages dépassent 4 et pourtant l'estimateur redevient mauvais : les poids $f/h$ sont minuscules pour presque tous les tirages et énormes pour de rares valeurs proches de 4. L'ESS s'effondre (environ 3), et l'erreur relative remonte à plus de 100 %. **Centrer la proposition juste sur la zone d'intérêt**, ni trop près ni trop loin, c'est tout l'art.

### 6.2.6 Réduire la variance : faire mieux avec les mêmes tirages

L'erreur est $\sigma/\sqrt n$ ; plutôt que de multiplier $n$, on peut **réduire $\sigma$**. Prenons une intégrale que l'on sait calculer autrement (pour avoir une référence) : $I=\int_0^1e^{-x^2}dx\approx0{,}746824$. Estimateur naïf : $f(U)=e^{-U^2}$ avec $U\sim\mathcal U(0,1)$.

**Variables antithétiques.** À chaque tirage $U$, on utilise aussi $1-U$ (qui suit aussi la loi uniforme) et on moyenne les deux : $\frac12[f(U)+f(1-U)]$.

> 📐 **Pourquoi ça marche.** Si $\rho=\mathrm{Corr}(f(U),f(1-U))$, la variance de la moyenne de ces deux valeurs est $\frac{\sigma^2}{2}(1+\rho)$ (volume I, section 2.3). Pour une fonction **monotone** (ici décroissante), $f(U)$ et $f(1-U)$ varient en sens contraire : $\rho<0$, et la variance diminue (elle serait même nulle si $\rho=-1$). Mais attention : on a utilisé **deux** évaluations de $f$ ; la comparaison honnête se fait à nombre d'évaluations égal.

**Variable de contrôle.** On connaît l'espérance exacte d'une variable $h(U)$ corrélée à $f(U)$ (ici $h(U)=U$, d'espérance $1/2$). On corrige l'estimateur :
$$\hat I_c=\frac1n\sum\Big[f(U_i)-c\,\big(h(U_i)-\mathbb E[h]\big)\Big].$$
Il reste sans biais pour tout $c$, et sa variance est minimale pour $c^{*}=\mathrm{Cov}(f,h)/\mathrm{Var}(h)$, où elle vaut $(1-\rho^2)\,\sigma^2/n$ avec $\rho=\mathrm{Corr}(f(U),h(U))$ : plus $h$ ressemble à $f$, plus on gagne.

**Stratification.** On découpe $[0,1]$ en $K$ tranches égales et on tire le même nombre de points dans chaque, ce qui garantit une couverture régulière de l'intervalle.

On compare les quatre méthodes à budget égal ($n=1\,000$ évaluations de $f$), en répétant 500 fois l'expérience :

```python
f = lambda x: np.exp(-x**2)
I_exact = 0.7468241328124270                                       # valeur de référence (fonction erreur)
rng = np.random.default_rng(630)
n, reps, K = 1000, 500, 10

def naif(rng):
    return f(rng.random(n)).mean()

def antithetique(rng):
    u = rng.random(n // 2)                                         # n/2 tirages -> n évaluations
    return 0.5 * (f(u) + f(1 - u)).mean()

def controle(rng):
    u = rng.random(n)
    fu = f(u)
    c = np.cov(fu, u)[0, 1] / u.var(ddof=1)                        # coefficient optimal estimé
    return (fu - c * (u - 0.5)).mean()

def stratifie(rng):
    m = n // K
    u = (np.arange(K)[:, None] + rng.random((K, m))) / K           # m points dans chacune des K tranches
    return f(u).mean()

res = {}
for nom, fct in (("naïf", naif), ("antithétique", antithetique), ("variable de contrôle", controle), ("stratifié", stratifie)):
    est = np.array([fct(rng) for _ in range(reps)])
    res[nom] = {"moyenne": est.mean(), "biais": est.mean() - I_exact, "écart-type": est.std(ddof=1)}
tab = pd.DataFrame(res).T
tab["gain de variance"] = (tab.loc["naïf", "écart-type"] / tab["écart-type"])**2
with pd.option_context("display.float_format", "{:.6f}".format):
    print(tab.to_string())
```
<!--sortie-->
```text
                      moyenne     biais  écart-type  gain de variance
naïf                 0.747244  0.000420    0.006639          1.000000
antithétique         0.746821 -0.000003    0.001311         25.626675
variable de contrôle 0.746816 -0.000008    0.000942         49.671695
stratifié            0.746838  0.000013    0.000645        105.946234
```

Les quatre méthodes sont (à peu près) **sans biais** (la colonne `biais` est de l'ordre de l'erreur de simulation : l'écart-type d'une moyenne de 500 répétitions est d'environ 0,0003), mais leurs écarts-types diffèrent : la colonne `gain de variance` dit combien de fois moins de tirages on aurait pu faire pour la même précision. Les antithétiques gagnent un facteur 26 (écart-type divisé par 5), la variable de contrôle un facteur 50, et la stratification un facteur 106 (écart-type divisé par 10). Elles sont ici très efficaces parce que la fonction est lisse et monotone. Dans des problèmes réels à haute dimension, le gain est plus modeste, mais jamais négligeable : **un peu de réflexion avant de simuler vaut souvent mieux qu'un facteur 100 de calcul**.

### 6.2.7 Le bootstrap et le bootstrap bayésien : deux Monte-Carlo que vous connaissez déjà

Le bootstrap du volume I (section 3.3.5) *est* une méthode de Monte-Carlo : au lieu de simuler à partir d'une loi théorique, on simule à partir de la **loi empirique** (on rééchantillonne les données avec remise). Il existe une version « bayésienne » : plutôt que de tirer des entiers (nombre de fois que chaque observation apparaît), on tire des **poids continus** $w\sim\mathrm{Dirichlet}(1,\dots,1)$ et on calcule la statistique pondérée. Les deux donnent des résultats très proches ; le bootstrap bayésien a l'avantage d'une interprétation directe : c'est la loi *a posteriori* d'un modèle sans forme paramétrique, avec un a priori très diffus.

Application : la **médiane** du panier des acheteurs de la boutique (une statistique sans formule d'erreur simple).

```python
boutique = clients[(clients["canal_acquisition"] == "Boutique") & (clients["panier_moyen"] > 0)]["panier_moyen"].to_numpy()
n_b = len(boutique)
rng = np.random.default_rng(631)
B = 5000

med_boot = np.array([np.median(rng.choice(boutique, n_b)) for _ in range(B)])

def mediane_ponderee(x, w):
    ordre = np.argsort(x)
    cw = np.cumsum(w[ordre]) / w.sum()
    return x[ordre][np.searchsorted(cw, 0.5)]

med_bayes = np.array([mediane_ponderee(boutique, rng.dirichlet(np.ones(n_b))) for _ in range(B)])

print(f"{n_b} acheteurs de la boutique ; médiane observée : {np.median(boutique):.2f} DT")
print(f"bootstrap classique : IC95 [{np.percentile(med_boot, 2.5):.2f} ; {np.percentile(med_boot, 97.5):.2f}]  (écart-type {med_boot.std():.2f})")
print(f"bootstrap bayésien  : IC95 [{np.percentile(med_bayes, 2.5):.2f} ; {np.percentile(med_bayes, 97.5):.2f}]  (écart-type {med_bayes.std():.2f})")
```
<!--sortie-->
```text
449 acheteurs de la boutique ; médiane observée : 67.92 DT
bootstrap classique : IC95 [64.62 ; 70.61]  (écart-type 1.56)
bootstrap bayésien  : IC95 [64.66 ; 70.61]  (écart-type 1.55)
```

> ✅ **À retenir (6.2).**
> - Une espérance se calcule en **moyennant des simulations** : $\hat\theta=\frac1n\sum g(X_i)$. Les probabilités, intégrales et moyennes a posteriori sont toutes des espérances.
> - L'erreur décroît en $\sigma/\sqrt n$ : **100 fois plus de tirages pour 10 fois moins d'erreur**. Cette vitesse ne dépend pas de la dimension, d'où l'intérêt de la méthode pour les problèmes complexes.
> - Pour simuler une loi donnée : **inversion** ($F^{-1}(U)$) si on connaît $F^{-1}$ ; **rejet** sinon (efficace seulement en petite dimension).
> - L'**échantillonnage préférentiel** estime les événements rares en tirant là où ils se produisent et en corrigeant par des poids $f/h$ ; l'**ESS** détecte les poids dégénérés.
> - Les **variables antithétiques, de contrôle et la stratification** réduisent la variance à nombre de tirages égal.
> - Le **bootstrap** est un Monte-Carlo sur la loi empirique ; sa version bayésienne tire des poids de Dirichlet.
> - Quand ni l'inversion ni le rejet ne marchent (cas général d'une loi a posteriori), il reste les **chaînes de Markov** : section 6.3.


## 6.3 MCMC : Metropolis-Hastings et échantillonnage de Gibbs

> 💡 **Intuition.** Imaginez un randonneur aveugle lâché dans une chaîne de montagnes, avec pour consigne de **passer plus de temps dans les hautes vallées que dans les basses**, exactement en proportion de l'altitude. Il ne voit pas la carte : il peut seulement, à chaque pas, tâter un point voisin et comparer son altitude à celle de sa position. Règle : *si le point voisin est plus haut, j'y vais toujours ; s'il est plus bas, j'y vais avec une probabilité égale au rapport des altitudes.* Au bout de très longtemps, la proportion du temps passé en chaque lieu est proportionnelle à l'altitude. C'est **Metropolis**. L'« altitude » est la densité a posteriori ; la proportion du temps passé, c'est l'échantillon qu'on cherche.

### 6.3.1 Pourquoi les chaînes de Markov ?

Considérons la régression logistique de `rachat_12m` sur l'offre, le canal et l'âge (nous la ferons en 6.3.5). L'a posteriori est
$$p(\beta\mid y)\;\propto\;\underbrace{\prod_{i}\sigma(x_i^\top\beta)^{y_i}\bigl(1-\sigma(x_i^\top\beta)\bigr)^{1-y_i}}_{\text{vraisemblance}}\;\times\;\underbrace{\prod_j\mathcal N(\beta_j;\,0,\,s^2)}_{\text{a priori}}.$$
Ce n'est **aucune loi connue** : pas de conjugaison, pas de fonction de répartition inversible, et le rejet de 6.2.4 serait inapplicable en dimension 5. Pire : nous ne connaissons même pas la **constante de normalisation** $p(y)$, qui est une intégrale en dimension 5. Mais nous savons calculer, pour tout $\beta$, la quantité **non normalisée** ci-dessus. Les méthodes MCMC (*Markov chain Monte Carlo*) n'ont besoin que de cela : elles ne s'intéressent qu'aux **rapports** $p(\beta')/p(\beta)$, dans lesquels la constante s'annule.

L'idée générale : au lieu de tirer des points *indépendants*, construire une **chaîne de Markov** $\theta^{(1)},\theta^{(2)},\dots$ (chaque point dépend seulement du précédent, volume I, section 2.6.2), conçue pour que sa **loi stationnaire** soit exactement la loi cible. Après un temps de chauffe, les points de la chaîne sont (corrélés) des tirages de la cible.

### 6.3.2 Les chaînes de Markov : loi stationnaire et réversibilité

Rappel (volume I, 2.6.2) : une chaîne à états finis de matrice de transition $P$ ($P_{ij}=P(\text{aller de }i\text{ à }j)$) admet une **loi stationnaire** $\pi$ si $\pi P=\pi$ : si la chaîne a la loi $\pi$ à un instant, elle l'a encore à l'instant suivant. Sous de bonnes conditions (la chaîne peut aller de tout état à tout état, et n'est pas périodique : on dit qu'elle est *ergodique*), la chaîne **converge** vers $\pi$ quelle que soit sa position de départ, et la proportion du temps passé dans chaque état tend vers $\pi$ (théorème ergodique, admis).

Comment fabriquer une chaîne dont la loi stationnaire est une loi $\pi$ donnée ? Par une condition suffisante simple.

> 📐 **Théorème (réversibilité ⇒ stationnarité).** Si une matrice de transition $P$ vérifie l'**équation de bilan détaillé**
> $$\pi_i\,P_{ij}=\pi_j\,P_{ji}\qquad\text{pour tous }i,j,$$
> alors $\pi P=\pi$.
>
> *Démonstration.* La $j$-ième composante de $\pi P$ est $\sum_i\pi_iP_{ij}=\sum_i\pi_jP_{ji}=\pi_j\sum_iP_{ji}=\pi_j$, car chaque ligne de $P$ somme à 1. $\square$

L'équation dit : « *en régime stationnaire, le flux de $i$ vers $j$ égale le flux de $j$ vers $i$* ». Si les flux sont équilibrés pour chaque paire d'états, la population de chaque état est stable.

**Exemple à la main : trois canaux.** Yasmine choisit chaque semaine un canal à mettre en avant parmi 1 = Boutique, 2 = Site, 3 = Instagram, et elle voudrait que ses choix, sur le long terme, suivent des poids $(2,5,3)$, c'est-à-dire la loi $\pi=(0{,}2;\,0{,}5;\,0{,}3)$. Elle applique la règle de Metropolis : **proposer** l'un des deux autres canaux au hasard (probabilité $\tfrac12$ chacun), puis **accepter** avec la probabilité $\alpha=\min\bigl(1,\ \pi_j/\pi_i\bigr)$, et sinon rester sur place. Construisons la matrice :

- depuis 1 (poids 2) : vers 2, $\tfrac12\min(1,5/2)=\tfrac12$ ; vers 3, $\tfrac12\min(1,3/2)=\tfrac12$ ; rester : $0$ ;
- depuis 2 (poids 5) : vers 1, $\tfrac12\cdot\tfrac25=0{,}2$ ; vers 3, $\tfrac12\cdot\tfrac35=0{,}3$ ; rester : $0{,}5$ ;
- depuis 3 (poids 3) : vers 1, $\tfrac12\cdot\tfrac23=\tfrac13$ ; vers 2, $\tfrac12\cdot1=0{,}5$ ; rester : $\tfrac16$.

Vérifions le bilan détaillé à la main : $\pi_1P_{12}=0{,}2\times0{,}5=0{,}1=\pi_2P_{21}=0{,}5\times0{,}2$ ✓ ; $\pi_1P_{13}=0{,}2\times0{,}5=0{,}1=\pi_3P_{31}=0{,}3\times\tfrac13$ ✓ ; $\pi_2P_{23}=0{,}5\times0{,}3=0{,}15=\pi_3P_{32}=0{,}3\times0{,}5$ ✓. Le code confirme, trouve la loi stationnaire par un calcul d'algèbre linéaire (volume I, section 1.1.3 : vecteur propre associé à la valeur propre 1), et simule la chaîne :

```python
import numpy as np
import pandas as pd

poids = np.array([2.0, 5.0, 3.0])
pi = poids / poids.sum()
k = len(poids)

# matrice de transition de Metropolis (proposition : l'un des deux autres états, probabilité 1/2)
P = np.zeros((k, k))
for i in range(k):
    for j in range(k):
        if i != j:
            P[i, j] = 0.5 * min(1.0, poids[j] / poids[i])
    P[i, i] = 1 - P[i].sum()
print("matrice de transition P :\n", P.round(4))

bilan = np.array([[pi[i] * P[i, j] - pi[j] * P[j, i] for j in range(k)] for i in range(k)])
print("\nbilan détaillé : plus grand |pi_i P_ij - pi_j P_ji| =", np.abs(bilan).max())

# loi stationnaire par algèbre linéaire : vecteur propre à gauche de valeur propre 1
valeurs, vecteurs = np.linalg.eig(P.T)
stat = np.real(vecteurs[:, np.argmin(np.abs(valeurs - 1))])
stat = stat / stat.sum()
print("loi stationnaire (vecteur propre) :", stat.round(4), "| cible pi :", pi)

# simulation de la chaîne, départ dans l'état 1
rng = np.random.default_rng(630)
etat, compte = 0, np.zeros(k)
n_pas = 100_000
for _ in range(n_pas):
    etat = rng.choice(k, p=P[etat])
    compte[etat] += 1
print("fréquences observées sur", n_pas, "pas :", (compte / n_pas).round(4))
```
<!--sortie-->
```text
matrice de transition P :
 [[0.     0.5    0.5   ]
 [0.2    0.5    0.3   ]
 [0.3333 0.5    0.1667]]

bilan détaillé : plus grand |pi_i P_ij - pi_j P_ji| = 1.3877787807814457e-17
loi stationnaire (vecteur propre) : [0.2 0.5 0.3] | cible pi : [0.2 0.5 0.3]
fréquences observées sur 100000 pas : [0.2009 0.5005 0.2986]
```

Les trois méthodes (vecteur propre, bilan détaillé, simulation) s'accordent : la chaîne visite chaque canal en proportion de son poids. Remarquez que nous n'avons utilisé que les **rapports** de poids $\pi_j/\pi_i$ : le calcul aurait été le même avec des poids $(20,50,30)$. C'est exactement ce qui nous servira quand la constante de normalisation sera inconnue.

### 6.3.3 L'algorithme de Metropolis-Hastings

Généralisons à une loi continue de densité cible $\pi(\theta)$ (connue à une constante près), en dimension quelconque.

> **Metropolis-Hastings.** On se donne une loi de **proposition** $q(\theta'\mid\theta)$ dont on sait simuler. Partant de $\theta^{(t)}$ :
> 1. tirer une **proposition** $\theta'\sim q(\cdot\mid\theta^{(t)})$ ;
> 2. calculer la probabilité d'acceptation $$\alpha(\theta,\theta')=\min\left(1,\ \frac{\pi(\theta')\,q(\theta\mid\theta')}{\pi(\theta)\,q(\theta'\mid\theta)}\right);$$
> 3. tirer $U\sim\mathcal U(0,1)$ ; si $U\le\alpha$ : $\theta^{(t+1)}=\theta'$ (on **accepte**), sinon $\theta^{(t+1)}=\theta^{(t)}$ (on **reste**, et on **recompte** la valeur).

Quand la proposition est **symétrique** ($q(\theta'\mid\theta)=q(\theta\mid\theta')$, par exemple $\theta'=\theta+\text{bruit gaussien}$, la « marche aléatoire »), le rapport des $q$ disparaît et on retrouve la règle de Metropolis de l'exemple précédent : $\alpha=\min(1,\pi(\theta')/\pi(\theta))$.

> 📐 **Théorème.** La chaîne de Metropolis-Hastings vérifie le bilan détaillé par rapport à $\pi$ ; donc $\pi$ est sa loi stationnaire.
>
> *Démonstration.* Pour $\theta\neq\theta'$, la densité de transition est $K(\theta,\theta')=q(\theta'\mid\theta)\,\alpha(\theta,\theta')$. Alors
> $$\pi(\theta)K(\theta,\theta')=\pi(\theta)\,q(\theta'\mid\theta)\,\min\!\left(1,\frac{\pi(\theta')q(\theta\mid\theta')}{\pi(\theta)q(\theta'\mid\theta)}\right)=\min\bigl(\pi(\theta)q(\theta'\mid\theta),\ \pi(\theta')q(\theta\mid\theta')\bigr).$$
> L'expression de droite est **symétrique** en $(\theta,\theta')$ : elle est égale à $\pi(\theta')K(\theta',\theta)$. C'est le bilan détaillé. Il reste à vérifier la stationnarité : pour tout ensemble $A$, $\int\pi(\theta)K(\theta,A)\,d\theta=\int_A\left[\int\pi(\theta)K(\theta,\theta')d\theta\right]d\theta'+(\text{mass du rejet})$. Grâce au bilan détaillé, le crochet vaut $\pi(\theta')\int K(\theta',\theta)d\theta=\pi(\theta')\bigl(1-r(\theta')\bigr)$, où $r(\theta')$ est la probabilité de rejet en $\theta'$ ; la part de la chaîne qui reste sur place (probabilité $r(\theta)$ en chaque $\theta$) apporte exactement $\int_A\pi(\theta')r(\theta')d\theta'$. La somme redonne $\int_A\pi$. $\square$
>
> Pour que la chaîne **converge** effectivement vers $\pi$ depuis n'importe quel point de départ, il faut en plus qu'elle soit irréductible (elle peut atteindre toute région de probabilité positive) et apériodique ; c'est le cas dès que la proposition gaussienne de la marche aléatoire est utilisée sur un espace continu (théorème admis, voir les références en fin de volume).

**La constante de normalisation disparaît.** Dans $\alpha$, $\pi$ n'intervient que par le rapport $\pi(\theta')/\pi(\theta)$ : on peut remplacer $\pi$ par n'importe quelle fonction proportionnelle (vraisemblance × a priori, sans la constante $p(y)$). Pour éviter les dépassements numériques, on travaille toujours avec les **logarithmes** : on accepte si $\log U<\log\pi(\theta')-\log\pi(\theta)$.

**Premier test : retrouver la loi $\mathrm{Beta}(8,4)$ de 6.1.** Nous connaissons la bonne réponse (moyenne $2/3$, écart-type $0{,}1307$) : nous pouvons donc juger l'algorithme.

```python
from scipy import stats

def metropolis_1d(logp, x0, n, pas, rng):
    """Marche aléatoire de Metropolis en dimension 1 : proposition x' = x + pas * N(0, 1)."""
    x, lp = x0, logp(x0)
    chaine = np.empty(n)
    acceptes = 0
    for i in range(n):
        prop = x + pas * rng.standard_normal()
        lpp = logp(prop)
        if np.log(rng.random()) < lpp - lp:               # critère d'acceptation, en logarithmes
            x, lp = prop, lpp
            acceptes += 1
        chaine[i] = x                                     # on recompte la valeur même si on a refusé
    return chaine, acceptes / n

def log_beta84(x):                                        # log de la densité NON normalisée de Beta(8, 4)
    return 7 * np.log(x) + 3 * np.log(1 - x) if 0 < x < 1 else -np.inf

rng = np.random.default_rng(631)
chaine, taux = metropolis_1d(log_beta84, x0=0.5, n=20_000, pas=0.2, rng=rng)
exacte = stats.beta(8, 4)
apres = chaine[1000:]                                     # on jette les 1 000 premiers points (« chauffe »)
print(f"taux d'acceptation : {taux:.3f}")
print(f"moyenne {apres.mean():.4f} (exacte {exacte.mean():.4f}) | écart-type {apres.std():.4f} (exact {exacte.std():.4f})")
print("quantiles 5 %, 50 %, 95 % :", np.percentile(apres, [5, 50, 95]).round(4), "| exacts :", exacte.ppf([0.05, 0.5, 0.95]).round(4))
print(f"test de Kolmogorov-Smirnov contre la loi exacte : statistique {stats.kstest(apres, exacte.cdf).statistic:.4f}")
```
<!--sortie-->
```text
taux d'acceptation : 0.589
moyenne 0.6674 (exacte 0.6667) | écart-type 0.1334 (exact 0.1307)
quantiles 5 %, 50 %, 95 % : [0.4321 0.6779 0.8656] | exacts : [0.4356 0.6762 0.8649]
test de Kolmogorov-Smirnov contre la loi exacte : statistique 0.0139
```

La chaîne reproduit la loi cible : moyenne, écart-type et quantiles coïncident à environ le centième. (Le test de Kolmogorov-Smirnov fournit une statistique faible ; sa p-valeur serait trompeuse ici, car les points d'une chaîne sont **corrélés** : le test suppose des observations indépendantes.) Regardons maintenant ce que la chaîne a fait, et, pour comprendre le rôle du **pas**, comparons trois pas.

### 6.3.4 Régler l'algorithme : le pas de la marche aléatoire

Le seul réglage de la marche aléatoire est le **pas** (l'écart-type de la proposition). Il faut le choisir avec soin :

- **pas trop petit** : presque toutes les propositions sont acceptées, mais elles sont minuscules ; la chaîne rampe et met un temps énorme à explorer la loi ;
- **pas trop grand** : presque toutes les propositions tombent dans des zones de faible densité et sont rejetées ; la chaîne reste bloquée sur place ;
- **pas intermédiaire** : un bon compromis.

Pour *mesurer* la qualité de l'exploration, on utilise la **taille d'échantillon effective** (ESS), que nous reverrons en 6.4 : $n$ points **corrélés** d'une chaîne valent seulement $\mathrm{ESS}=\dfrac{n}{1+2\sum_{k\ge1}\rho_k}$ points indépendants, où $\rho_k$ est l'autocorrélation de la chaîne au décalage $k$ (volume II, chapitre 4, pour la notion d'autocorrélation). Voici deux petites fonctions pour la calculer (l'autocorrélation par transformée de Fourier rapide ; la somme s'arrête à la première autocorrélation négative) :

```python
def autocorr(x, max_lag):
    x = np.asarray(x, dtype=float) - np.mean(x)
    n = len(x)
    f = np.fft.rfft(x, 2 * n)                               # transformée de Fourier avec remplissage de zéros
    ac = np.fft.irfft(f * np.conj(f))[:n]
    return (ac / ac[0])[: max_lag + 1]

def ess(x):
    rho = autocorr(x, max_lag=min(len(x) // 2, 1000))
    somme = 0.0
    for r in rho[1:]:
        if r < 0:
            break
        somme += r
    return len(x) / (1 + 2 * somme)

lignes = []
traces = {}
for pas in (0.01, 0.05, 0.2, 0.5, 2.0, 10.0):
    rng = np.random.default_rng(632)
    ch, taux = metropolis_1d(log_beta84, x0=0.5, n=20_000, pas=pas, rng=rng)
    traces[pas] = ch
    apres = ch[1000:]
    lignes.append({"pas": pas, "taux d'acceptation": round(taux, 3), "ESS": round(ess(apres)),
                   "ESS / n": round(ess(apres) / len(apres), 3), "autocorr. lag 1": round(autocorr(apres, 1)[1], 3),
                   "moyenne": round(apres.mean(), 4)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
  pas  taux d'acceptation  ESS  ESS / n  autocorr. lag 1  moyenne
 0.01               0.970   25    0.001            0.997   0.6900
 0.05               0.876  444    0.023            0.944   0.6773
 0.20               0.594 3731    0.196            0.675   0.6662
 0.50               0.307 3593    0.189            0.686   0.6649
 2.00               0.083  870    0.046            0.909   0.6612
10.00               0.017  217    0.011            0.978   0.6751
```

On lit : avec un pas de 0,01, le taux d'acceptation est proche de 1 mais l'ESS est minuscule (la chaîne ne bouge presque pas) ; avec un pas de 10, le taux d'acceptation s'effondre (1,7 % des propositions seulement tombent dans une zone de densité raisonnable) et l'ESS est de 217, dix-sept fois plus faible qu'à l'optimum ; l'optimum est autour d'un pas de 0,2 à 0,5 (ESS d'environ 3 600 à 3 700, soit 19 % de $n$), avec un taux d'acceptation de 30 à 60 %. Noter que **le taux d'acceptation seul ne suffit pas à juger un réglage** : il vaut 97 % avec le pas de 0,01 (mauvais) et 59 % avec le pas de 0,2 (bon). L'ESS est le vrai juge. Voici les traces correspondantes.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.facecolor": "#fcfcfb",
                     "figure.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
                     "legend.frameon": False, "font.size": 10})

fig, axes = plt.subplots(3, 1, figsize=(8.6, 6.6), sharex=True)
for ax, (pas, couleur, etiquette) in zip(axes, [(0.01, ORANGE, "pas trop petit (0,01)"), (0.2, BLEU, "bon pas (0,2)"), (10.0, VIOLET, "pas trop grand (10)")]):
    ch = traces[pas][:600]
    ax.plot(ch, color=couleur, lw=0.9)
    ax.set_ylim(0, 1)
    ax.set_ylabel(r"$\theta$")
    ax.set_title(etiquette, loc="left", color=couleur, fontsize=10)
axes[-1].set_xlabel("itération (les 600 premières)")
plt.tight_layout()
plt.savefig("figures/ch06-mh-pas.png", dpi=200, bbox_inches="tight")
plt.close()
```

![Trois traces de la marche aléatoire de Metropolis pour la loi Beta(8, 4), avec trois pas différents. Pas trop petit : la chaîne rampe lentement. Bon pas : la chaîne explore toute la zone de forte densité. Pas trop grand : la chaîne reste longtemps bloquée sur des paliers.](figures/ch06-mh-pas.png)

> 💡 **Lire une trace.** Une bonne trace ressemble à une **« chenille velue »** : un nuage de points qui oscille de façon irrégulière autour d'une valeur centrale, sans tendance. Une trace **rampante** (trop petit) ressemble à une courbe lisse qui dérive lentement ; une trace **à paliers** (trop grand) a de longs segments plats (la chaîne reste bloquée sur ses refus). Nous verrons en 6.4 comment objectiver cette impression.

> 📐 **Règles pratiques.** En dimension 1, un taux d'acceptation d'environ 44 % est optimal ; en dimension élevée, des résultats théoriques (Roberts, Gelman et Gilks, 1997) donnent un taux optimal d'environ **23 %**, obtenu avec une proposition gaussienne de covariance $\dfrac{2{,}38^2}{d}\,\hat\Sigma$, où $d$ est la dimension et $\hat\Sigma$ une estimation de la covariance de la loi cible. Nous utiliserons cette règle pour la régression logistique.

### 6.3.5 Application : la régression logistique bayésienne du rachat

Passons au problème réel. Nous modélisons le rachat dans les 12 mois par
$$y_i\sim\mathrm{Bernoulli}\bigl(\sigma(\eta_i)\bigr),\qquad \eta_i=\beta_0+\beta_1\,\text{offre}_i+\beta_2\,\text{Instagram}_i+\beta_3\,\text{Site}_i+\beta_4\,\text{âge}_i,$$
où $\sigma(u)=1/(1+e^{-u})$, la Boutique est le canal de référence et l'âge est **standardisé** (centré, divisé par son écart-type : une unité = un écart-type). (La régression logistique est étudiée au chapitre 2, section 2.2 ; ici, on s'intéresse à la façon de **l'estimer** par une méthode bayésienne.) A priori : $\beta_j\sim\mathcal N(0,\,2{,}5^2)$ pour tous les coefficients, un a priori « faiblement informatif » (6.1.6) : il écarte les rapports de cotes extrêmes ($e^{\pm 5}$) sans trop contraindre.

```python
import statsmodels.api as sm

clients = pd.read_csv("donnees/clients.csv")
d = clients.copy()
d["age_c"] = (d["age"] - d["age"].mean()) / d["age"].std()
X = pd.get_dummies(d[["offre_bienvenue", "canal_acquisition", "age_c"]], columns=["canal_acquisition"], drop_first=True, dtype=float)
X = X.rename(columns={"canal_acquisition_Instagram": "Instagram", "canal_acquisition_Site": "Site", "offre_bienvenue": "offre"})
X = sm.add_constant(X)
noms = list(X.columns)
Xm, y = X.to_numpy(), d["rachat_12m"].to_numpy()
print("colonnes :", noms, "| n =", len(y), "| rachat moyen :", y.mean().round(3))

S_PRIOR = 2.5
def log_post(beta):
    eta = Xm @ beta
    log_vrais = np.sum(y * eta - np.logaddexp(0, eta))              # somme de y*eta - log(1 + exp(eta))
    log_prior = -0.5 * np.sum(beta**2) / S_PRIOR**2                 # normale centrée (constante omise)
    return log_vrais + log_prior

# Point de repère : l'estimation du maximum de vraisemblance (statsmodels)
emv = sm.Logit(y, Xm).fit(disp=0)
print("\nlog-posterior en l'EMV :", round(log_post(emv.params), 2))
```
<!--sortie-->
```text
colonnes : ['const', 'offre', 'age_c', 'Instagram', 'Site'] | n = 2000 | rachat moyen : 0.509

log-posterior en l'EMV : -1355.46
```

Le **log-posterior** est écrit en quelques lignes : c'est toute la modélisation. Il reste à fabriquer la chaîne. Nous prenons une marche aléatoire à **proposition gaussienne multivariée** de covariance $\frac{2{,}38^2}{d}\hat\Sigma$, où $\hat\Sigma$ est la covariance estimée des coefficients par le maximum de vraisemblance (l'inverse de la hessienne, que statsmodels fournit) : c'est un bon « premier dessin » de la forme de l'a posteriori. Pour pouvoir diagnostiquer la convergence en 6.4, nous lançons **quatre chaînes** de points de départ dispersés.

```python
def metropolis_multi(logp, x0, n, cov_prop, rng):
    L = np.linalg.cholesky(cov_prop)
    dim = len(x0)
    x, lp = x0.copy(), logp(x0)
    chaine = np.empty((n, dim))
    acceptes = 0
    for i in range(n):
        prop = x + L @ rng.standard_normal(dim)
        lpp = logp(prop)
        if np.log(rng.random()) < lpp - lp:
            x, lp = prop, lpp
            acceptes += 1
        chaine[i] = x
    return chaine, acceptes / n

dim = len(noms)
cov_prop = (2.38**2 / dim) * emv.cov_params()
rng = np.random.default_rng(633)
chaines, taux = [], []
for c in range(4):
    depart = emv.params + rng.normal(0, 1.0, dim)                     # points de départ dispersés
    ch, tx = metropolis_multi(log_post, depart, n=6000, cov_prop=cov_prop, rng=rng)
    chaines.append(ch)
    taux.append(tx)
chaines = np.array(chaines)                                           # forme (4 chaînes, 6000 itérations, 5 paramètres)
print("taux d'acceptation des 4 chaînes :", np.round(taux, 3), "(cible théorique ≈ 0,23 à 0,30)")
print("forme du tableau de tirages :", chaines.shape)
```
<!--sortie-->
```text
taux d'acceptation des 4 chaînes : [0.284 0.297 0.293 0.274] (cible théorique ≈ 0,23 à 0,30)
forme du tableau de tirages : (4, 6000, 5)
```

Les taux d'acceptation sont proches de la valeur théorique. Les 1 000 premières itérations de chaque chaîne (la « chauffe ») sont écartées. Voici le résumé a posteriori, à côté du maximum de vraisemblance :

```python
apres = chaines[:, 1000:, :]                                          # on écarte la chauffe
tirages = apres.reshape(-1, dim)                                      # 4 x 5000 = 20 000 tirages
resume = pd.DataFrame({
    "EMV": emv.params, "écart-type EMV": emv.bse,
    "moyenne a posteriori": tirages.mean(axis=0), "écart-type a posteriori": tirages.std(axis=0),
    "crédib. 2,5 %": np.percentile(tirages, 2.5, axis=0), "crédib. 97,5 %": np.percentile(tirages, 97.5, axis=0),
    "ESS": [sum(ess(apres[c, :, j]) for c in range(4)) for j in range(dim)]}, index=noms)
with pd.option_context("display.float_format", "{:.3f}".format, "display.width", 200):
    print(resume.round(3).to_string())
```
<!--sortie-->
```text
             EMV  écart-type EMV  moyenne a posteriori  écart-type a posteriori  crédib. 2,5 %  crédib. 97,5 %      ESS
const      0.034           0.100                 0.033                    0.098         -0.162           0.227 1280.705
offre      0.493           0.091                 0.493                    0.089          0.316           0.663 1276.029
age_c     -0.163           0.046                -0.163                    0.045         -0.256          -0.076 1114.281
Instagram -0.463           0.116                -0.459                    0.113         -0.681          -0.232 1158.399
Site      -0.168           0.120                -0.163                    0.118         -0.393           0.073 1205.256
```

Les moyennes a posteriori sont **presque identiques** aux estimations du maximum de vraisemblance, et les écarts-types a posteriori sont presque ceux de l'EMV (c'est le théorème de Bernstein-von Mises du 6.1.6 à l'œuvre : avec 2 000 observations et un a priori large, a posteriori et vraisemblance se confondent). Les ESS sont d'environ 1 100 à 1 300 sur 20 000 tirages (l'ESS ne représente qu'environ 6 % du nombre de tirages : les points d'une marche aléatoire sont fortement corrélés). C'est suffisant : l'erreur de simulation sur une moyenne a posteriori vaut $\sigma/\sqrt{\mathrm{ESS}}\approx0{,}089/\sqrt{1\,276}\approx0{,}0025$ pour le coefficient de l'offre, soit moins de 3 % de son incertitude a posteriori. (Nous reviendrons en 6.4 sur ce qui rend un ESS « suffisant ».)

Le point clé de l'approche bayésienne est que nous **possédons maintenant des tirages de la loi jointe a posteriori** des cinq coefficients : tout ce que l'on veut calculer devient une moyenne sur ces tirages, sans formule. Par exemple, le **rapport de cotes** de l'offre, et surtout l'**effet de l'offre sur la probabilité de rachat** pour un client de référence (acquis en Boutique, d'âge moyen) :

```python
b0, b1 = tirages[:, 0], tirages[:, 1]
rc = np.exp(b1)
print(f"rapport de cotes de l'offre : médiane {np.median(rc):.3f}, IC de crédibilité à 95 % [{np.percentile(rc, 2.5):.3f} ; {np.percentile(rc, 97.5):.3f}]")
print(f"P(rapport de cotes > 1)  = {(rc > 1).mean():.4f}   |   P(rapport de cotes > 1,5) = {(rc > 1.5).mean():.4f}")

sigmoide = lambda u: 1 / (1 + np.exp(-u))
effet = sigmoide(b0 + b1) - sigmoide(b0)                              # variation de probabilité de rachat (Boutique, âge moyen)
print(f"effet de l'offre sur la probabilité de rachat d'un client Boutique d'âge moyen : "
      f"{effet.mean():+.3f}  IC95 [{np.percentile(effet, 2.5):+.3f} ; {np.percentile(effet, 97.5):+.3f}]")

# Comparaison à l'effet brut de 6.1.4 (différence de fréquences)
brut = clients.groupby("offre_bienvenue")["rachat_12m"].mean()
print(f"rappel : différence brute des fréquences (6.1.4) = {brut[1] - brut[0]:+.3f}")
```
<!--sortie-->
```text
rapport de cotes de l'offre : médiane 1.639, IC de crédibilité à 95 % [1.372 ; 1.940]
P(rapport de cotes > 1)  = 1.0000   |   P(rapport de cotes > 1,5) = 0.8357
effet de l'offre sur la probabilité de rachat d'un client Boutique d'âge moyen : +0.120  IC95 [+0.078 ; +0.161]
rappel : différence brute des fréquences (6.1.4) = +0.122
```

Quatre phrases que l'on peut maintenant écrire, avec leur chiffre : le rapport de cotes de l'offre est de l'ordre de 1,6 ; la probabilité qu'il dépasse 1 est quasi certaine ; la probabilité qu'il dépasse 1,5 est d'environ 84 % ; et l'effet de l'offre sur la probabilité de rachat d'un client moyen est de l'ordre de 12 points, en cohérence avec l'estimation brute de 6.1.4 (l'offre ayant été attribuée au hasard, ajuster sur le canal et l'âge ne change presque rien, comme on l'attend). Pour finir, un graphique : pour chaque coefficient, l'intervalle de crédibilité et l'intervalle de confiance du maximum de vraisemblance.

```python
fig, ax = plt.subplots(figsize=(7.6, 3.9))
y_pos = np.arange(dim)[::-1]
bas = resume["crédib. 2,5 %"].to_numpy(); haut = resume["crédib. 97,5 %"].to_numpy()
ax.hlines(y_pos + 0.12, bas, haut, color=BLEU, lw=2.4)
ax.plot(resume["moyenne a posteriori"], y_pos + 0.12, "o", color=BLEU, ms=6)
ic = emv.conf_int()
ax.hlines(y_pos - 0.12, ic[:, 0], ic[:, 1], color=ORANGE, lw=2.4)
ax.plot(emv.params, y_pos - 0.12, "s", color=ORANGE, ms=5)
ax.axvline(0, color="#898781", lw=0.8)
ax.set_yticks(y_pos)
ax.set_yticklabels(noms)
ax.set_xlabel("coefficient (échelle du logit)")
ax.text(-1.95, 5.15, "bleu : a posteriori (MCMC), moyenne et intervalle de crédibilité à 95 %", color=BLEU, fontsize=9, va="center")
ax.text(-1.95, 4.80, "orange : maximum de vraisemblance et intervalle de confiance à 95 %", color=ORANGE, fontsize=9, va="center")
ax.set_ylim(-0.6, 5.4)
ax.set_xlim(-2.0, 1.2)
plt.savefig("figures/ch06-logit-bayes.png", dpi=200, bbox_inches="tight")
plt.close()
```

![Pour chacun des cinq coefficients de la régression logistique du rachat, l'intervalle de crédibilité à 95 % obtenu par MCMC (bleu) et l'intervalle de confiance à 95 % du maximum de vraisemblance (orange). Les deux approches coïncident presque exactement.](figures/ch06-logit-bayes.png)

> 🧪 **Que valent ces estimations ? Réponse de la simulation.** Les données étant simulées, nous connaissons les vrais paramètres du générateur : un effet de l'offre de **+0,55** sur le logit, un avantage de la Boutique de +0,3 par rapport aux deux autres canaux (donc −0,3 pour Instagram et pour le Site), un effet de l'âge de −0,015 par an. Notre estimation de l'offre (0,49) est **inférieure à 0,55** mais compatible avec elle (l'intervalle de crédibilité est d'environ ±0,17). L'effet de l'âge (−0,163 par écart-type, soit $-0{,}163/10{,}5\approx-0{,}0155$ par an) retrouve le −0,015 programmé, et les intervalles des canaux contiennent les valeurs programmées ($-0{,}3$ pour Instagram comme pour le Site). Mais il y a une raison **systématique**, et pas seulement le hasard, pour laquelle l'effet de l'offre est un peu sous-estimé : le générateur utilise deux facteurs latents (goût pour les produits, sensibilité au service) qui influencent aussi le rachat, et que notre modèle **n'observe pas**. Omettre des variables explicatives *atténue* les coefficients d'une régression logistique, même quand ces variables sont indépendantes de l'offre (c'est la « non-collapsibilité » du rapport de cotes). Vérifions-le sur un très grand échantillon simulé avec la même formule :

```python
rng = np.random.default_rng(636)
N = 400_000
F1 = rng.normal(size=N)
F2 = 0.3 * F1 + np.sqrt(1 - 0.3**2) * rng.normal(size=N)         # deux facteurs latents corrélés
offre = rng.integers(0, 2, N).astype(float)
eta = -0.35 + 0.45 * F1 + 0.35 * F2 + 0.55 * offre              # vrai modèle : l'offre vaut 0,55
yy = rng.binomial(1, 1 / (1 + np.exp(-eta)))
marginal = sm.Logit(yy, sm.add_constant(offre)).fit(disp=0).params[1]
condit = sm.Logit(yy, sm.add_constant(np.c_[offre, F1, F2])).fit(disp=0).params[1]
print(f"coefficient de l'offre sans les facteurs latents : {marginal:.3f}")
print(f"coefficient de l'offre avec les facteurs latents : {condit:.3f}   (vrai : 0.55)")
```
<!--sortie-->
```text
coefficient de l'offre sans les facteurs latents : 0.499
coefficient de l'offre avec les facteurs latents : 0.548   (vrai : 0.55)
```

Sans les facteurs latents, le coefficient attendu est d'environ 0,50 : notre estimation de 0,49 est exactement ce que la théorie prédit. Voilà un bel exemple de modèle bien estimé mais **mal spécifié** : l'estimation est correcte pour la question posée au modèle, qui n'est pas exactement celle du générateur.

### 6.3.6 L'échantillonnage de Gibbs

Quand le paramètre a plusieurs composantes, $\theta=(\theta_1,\dots,\theta_d)$, il est parfois facile de simuler chaque composante **sachant toutes les autres** (on dit : selon sa **loi conditionnelle complète**), même si la loi jointe est compliquée. L'échantillonneur de Gibbs en fait un algorithme : à chaque itération, on met à jour les composantes l'une après l'autre.

> **Gibbs.** Partant de $\theta^{(t)}$ : tirer $\theta_1^{(t+1)}\sim p(\theta_1\mid\theta_2^{(t)},\dots,\theta_d^{(t)})$, puis $\theta_2^{(t+1)}\sim p(\theta_2\mid\theta_1^{(t+1)},\theta_3^{(t)},\dots)$, et ainsi de suite jusqu'à $\theta_d$.

> 📐 **Gibbs est un cas particulier de Metropolis-Hastings, avec acceptation 1.** Mettons à jour la composante $j$ avec la proposition $q(\theta'\mid\theta)=\pi(\theta'_j\mid\theta_{-j})$ (les autres composantes inchangées). Le rapport d'acceptation est
> $$\frac{\pi(\theta')q(\theta\mid\theta')}{\pi(\theta)q(\theta'\mid\theta)}=\frac{\pi(\theta'_j\mid\theta_{-j})\,\pi(\theta_{-j})\;\pi(\theta_j\mid\theta_{-j})}{\pi(\theta_j\mid\theta_{-j})\,\pi(\theta_{-j})\;\pi(\theta'_j\mid\theta_{-j})}=1,$$
> puisque $\pi(\theta)=\pi(\theta_j\mid\theta_{-j})\pi(\theta_{-j})$. La proposition est donc **toujours acceptée**, et le théorème de 6.3.3 garantit que $\pi$ est stationnaire.

**Exemple 1 : la loi normale bivariée.** Simulons $(X,Y)$ de corrélation $\rho$ (lois marginales $\mathcal N(0,1)$). Les lois conditionnelles sont connues : $X\mid Y=y\sim\mathcal N(\rho y,\,1-\rho^2)$, et symétriquement. Gibbs alterne les deux. C'est aussi l'occasion de voir son **point faible** : si les composantes sont fortement corrélées, chaque pas ne peut bouger que dans la direction d'un axe, et la chaîne progresse en zigzag minuscule.

```python
def gibbs_binormale(rho, n, rng):
    x = y = 0.0
    s = np.sqrt(1 - rho**2)
    out = np.empty((n, 2))
    for i in range(n):
        x = rng.normal(rho * y, s)                            # X | Y
        y = rng.normal(rho * x, s)                            # Y | X
        out[i] = (x, y)
    return out

rng = np.random.default_rng(634)
lignes = []
for rho in (0.0, 0.5, 0.9, 0.99):
    ch = gibbs_binormale(rho, 20_000, rng)[1000:]
    lignes.append({"rho vrai": rho, "corrélation estimée": round(np.corrcoef(ch.T)[0, 1], 3),
                   "écart-type de X": round(ch[:, 0].std(), 3), "autocorr. lag 1 de X": round(autocorr(ch[:, 0], 1)[1], 3),
                   "ESS de X (sur 19 000)": round(ess(ch[:, 0]))})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 rho vrai  corrélation estimée  écart-type de X  autocorr. lag 1 de X  ESS de X (sur 19 000)
     0.00               -0.003            0.997                -0.006                  19000
     0.50                0.493            1.001                 0.246                  11638
     0.90                0.902            1.003                 0.816                   1966
     0.99                0.990            1.011                 0.980                    177
```

Les corrélations estimées retrouvent les $\rho$ et les écarts-types valent 1, comme prévu. Mais regardez l'ESS : avec $\rho=0$ la chaîne est indépendante (ESS proche de $n$), tandis qu'avec $\rho=0{,}9$ elle tombe à environ 2 000 et qu'avec $\rho=0{,}99$ elle s'effondre à moins de 200 tirages efficaces sur 19 000 (1 % du total) : **la corrélation entre composantes ruine Gibbs**. C'est la raison pour laquelle on **reparamétrise** (on décorrèle les paramètres) ou on utilise des méthodes plus sophistiquées comme l'HMC (6.3.7).

**Exemple 2 : une loi normale à moyenne et variance inconnues.** En 6.1.8, nous avons fait l'hypothèse (de confort) que l'écart-type $\sigma$ du logarithme du panier était *connu*. Levons-la. Les données : les logarithmes des paniers des 449 acheteurs de la boutique. Le modèle : $y_i\sim\mathcal N(\mu,\sigma^2)$, avec les a priori **indépendants** $\mu\sim\mathcal N(4{,}\,10^2)$ (très large) et la **précision** $\tau=1/\sigma^2\sim\mathrm{Gamma}(a_0=0{,}01,\ b_0=0{,}01)$ (très diffuse). Les lois conditionnelles complètes sont connues :

- $\mu\mid\tau,y\sim\mathcal N(\mu_n,v_n)$ avec $\dfrac1{v_n}=\dfrac1{\tau_0^2}+n\tau$ et $\mu_n=v_n\left(\dfrac{\mu_0}{\tau_0^2}+\tau\,n\bar y\right)$ (c'est la formule normale-normale de 6.1.8, avec $\sigma^2=1/\tau$) ;
- $\tau\mid\mu,y\sim\mathrm{Gamma}\!\left(a_0+\dfrac n2,\ b_0+\dfrac12\sum_i(y_i-\mu)^2\right)$ (même calcul que gamma-Poisson : multiplier les formes en $\tau^{\cdot}e^{-\cdot\tau}$).

Il n'y a **pas de formule fermée** pour la loi jointe de $(\mu,\sigma)$ avec ces a priori indépendants ; Gibbs nous en donne des tirages.

```python
acheteurs = clients[(clients["canal_acquisition"] == "Boutique") & (clients["panier_moyen"] > 0)]
ly = np.log(acheteurs["panier_moyen"].to_numpy())
n_l, ybar = len(ly), ly.mean()
mu0, tau0sq, a0, b0 = 4.0, 10.0**2, 0.01, 0.01

def gibbs_normale(n_iter, rng, mu_init, prec_init):
    mu, prec = mu_init, prec_init
    out = np.empty((n_iter, 2))
    for i in range(n_iter):
        v = 1 / (1 / tau0sq + n_l * prec)
        m = v * (mu0 / tau0sq + prec * n_l * ybar)
        mu = rng.normal(m, np.sqrt(v))
        prec = rng.gamma(a0 + n_l / 2, 1 / (b0 + 0.5 * np.sum((ly - mu) ** 2)))
        out[i] = (mu, 1 / np.sqrt(prec))                          # on garde mu et sigma
    return out

rng = np.random.default_rng(635)
g = gibbs_normale(11_000, rng, mu_init=0.0, prec_init=1.0)[1000:]   # départ volontairement très mauvais
mu_s, sig_s = g[:, 0], g[:, 1]

h = stats.t.ppf(0.975, n_l - 1) * ly.std(ddof=1) / np.sqrt(n_l)
print(f"{n_l} acheteurs ; moyenne du log-panier {ybar:.4f} ; écart-type empirique {ly.std(ddof=1):.4f}")
print(f"Gibbs : mu    moyenne {mu_s.mean():.4f}  IC95 [{np.percentile(mu_s, 2.5):.4f} ; {np.percentile(mu_s, 97.5):.4f}]")
print(f"        sigma moyenne {sig_s.mean():.4f}  IC95 [{np.percentile(sig_s, 2.5):.4f} ; {np.percentile(sig_s, 97.5):.4f}]")
print(f"classique (Student) : IC95 de mu [{ybar - h:.4f} ; {ybar + h:.4f}]")
print(f"corrélation a posteriori entre mu et sigma : {np.corrcoef(mu_s, sig_s)[0, 1]:.3f}")
print(f"ESS de mu : {ess(mu_s):.0f}, ESS de sigma : {ess(sig_s):.0f}  (sur {len(mu_s)} tirages)")
```
<!--sortie-->
```text
449 acheteurs ; moyenne du log-panier 4.2183 ; écart-type empirique 0.3758
Gibbs : mu    moyenne 4.2182  IC95 [4.1838 ; 4.2529]
        sigma moyenne 0.3766  IC95 [0.3525 ; 0.4023]
classique (Student) : IC95 de mu [4.1834 ; 4.2532]
corrélation a posteriori entre mu et sigma : -0.001
ESS de mu : 10000, ESS de sigma : 9629  (sur 10000 tirages)
```

Les résultats concordent avec le calcul classique. Les ESS sont très proches du nombre de tirages : ici $\mu$ et $\sigma$ sont presque indépendants a posteriori (corrélation proche de 0), donc Gibbs est quasi parfait. Et on peut enfin comparer à la vérité : le générateur combine un bruit de 0,35 et l'effet du facteur latent $F_1$ (écart-type 0,12), soit un écart-type total de $\sqrt{0{,}35^2+0{,}12^2}\approx0{,}370$, et un log-panier moyen de 4,22 pour la Boutique. L'a posteriori contient les deux.

### 6.3.7 En pratique : PyMC, Stan et l'HMC (non exécuté)

Dans les projets réels, on n'écrit pas ses échantillonneurs à la main. Les bibliothèques **PyMC** (Python) et **Stan** (langage dédié, accessible depuis Python, R, etc.) permettent de décrire le modèle et se chargent de l'inférence. Elles utilisent une méthode bien plus puissante que la marche aléatoire : le **Monte-Carlo hamiltonien** (HMC), et sa variante adaptative NUTS. L'idée : au lieu de proposer un pas au hasard, on **simule le mouvement d'une bille** qui roule sur la surface $-\log\pi(\theta)$ en utilisant le **gradient** de $\log\pi$ (volume I, section 1.2) ; elle se déplace loin, dans la bonne direction, et les propositions sont presque toujours acceptées. En grande dimension, l'écart d'efficacité avec la marche aléatoire est considérable.

> ⚠️ **Non exécuté.** PyMC et Stan **ne sont pas installés** dans l'environnement qui a servi à écrire ce livre. Les deux blocs de code ci-dessous sont donc **montrés sans avoir été exécutés** ; leur résultat attendu est celui de la section 6.3.5 (même modèle, mêmes a priori), mais nous n'avons pas pu le vérifier ici.

```python noexec
import pymc as pm

with pm.Model() as modele:
    beta = pm.Normal("beta", mu=0, sigma=2.5, shape=5)           # le même a priori que dans 6.3.5
    eta = pm.math.dot(Xm, beta)
    pm.Bernoulli("rachat", logit_p=eta, observed=y)
    trace = pm.sample(2000, tune=1000, chains=4, random_seed=1)  # NUTS par défaut
```

```text noexec
data { int<lower=0> n; matrix[n, 5] X; array[n] int<lower=0, upper=1> y; }
parameters { vector[5] beta; }
model {
  beta ~ normal(0, 2.5);
  y ~ bernoulli_logit(X * beta);
}
```

Comprendre ce que PyMC et Stan font à votre place, c'est comprendre ce chapitre : un log-posterior (que vous venez d'écrire en trois lignes), un algorithme qui explore sa surface, des diagnostics pour savoir s'il a bien exploré (6.4).

> ✅ **À retenir (6.3).**
> - Quand l'a posteriori n'est pas une loi connue, on le **simule avec une chaîne de Markov** dont la loi stationnaire est la cible. Seul le rapport $\pi(\theta')/\pi(\theta)$ est nécessaire : la constante de normalisation disparaît.
> - **Metropolis-Hastings** : proposer, calculer $\alpha=\min\!\bigl(1,\frac{\pi(\theta')q(\theta|\theta')}{\pi(\theta)q(\theta'|\theta)}\bigr)$, accepter ou rester. Il vérifie le **bilan détaillé**, donc $\pi$ est stationnaire.
> - Le **pas** de la marche aléatoire se règle : trop petit, on rampe ; trop grand, on reste bloqué ; en dimension élevée, viser 23 % d'acceptation avec une covariance $2{,}38^2\hat\Sigma/d$.
> - Les points d'une chaîne sont **corrélés** : on les juge par l'**ESS**, pas par leur nombre. On écarte une période de **chauffe**.
> - **Gibbs** met à jour une composante à la fois selon sa loi conditionnelle (acceptation 1) ; il souffre quand les composantes sont très corrélées.
> - Une fois les tirages obtenus, **tout** se calcule par moyenne : rapports de cotes, effets sur les probabilités, probabilités de seuils, prédictions.
> - PyMC et Stan (HMC/NUTS) font cela mieux et plus vite, mais ne dispensent pas de **vérifier** le résultat (6.4).


## 6.4 Vérification des modèles bayésiens

> 💡 **Intuition.** Un pilote ne décolle pas sans sa liste de contrôle : carburant, volets, instruments. Un analyste bayésien devrait faire de même, car **deux choses peuvent tourner mal**, et elles sont indépendantes : (1) *l'algorithme* peut avoir mal exploré la loi a posteriori (la chaîne n'a pas convergé), et (2) *le modèle* peut être faux (la loi a posteriori, même parfaitement calculée, répond à une question mal posée). Nous avons vu un exemple de la seconde en 6.1.8 : un modèle de Poisson aux intervalles trop étroits. Cette section donne les outils pour détecter l'une et l'autre.

Dans tout ce qui suit, un échantillon MCMC n'est jamais « bon par nature » : on **démontre** qu'il est bon, ou du moins qu'il ne manifeste aucun signe de mauvaise santé. Un diagnostic qui passe ne prouve pas la convergence (on ne peut jamais prouver qu'une chaîne a tout exploré), mais un diagnostic qui échoue prouve un problème.

### 6.4.1 L'algorithme a-t-il convergé ? Les diagnostics de convergence

Nous reprenons les quatre chaînes de la régression logistique de 6.3.5, lancées depuis des points de départ **dispersés**. Le premier diagnostic, et le plus parlant, est le dessin : la **trace** de chaque chaîne, et la distribution des valeurs prises, chaîne par chaîne.

```python
import numpy as np
import pandas as pd
from scipy import stats
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.facecolor": "#fcfcfb",
                     "figure.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
                     "legend.frameon": False, "font.size": 10})

j = noms.index("offre")                                           # coefficient de l'offre (chaînes de 6.3.5)
couleurs = [BLEU, ORANGE, AQUA, VIOLET]
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 3.8), gridspec_kw={"width_ratios": [2.2, 1]})
for c in range(4):
    ax1.plot(chaines[c, :, j], color=couleurs[c], lw=0.6, alpha=0.85)
ax1.axvspan(0, 1000, color="#c3c2b7", alpha=0.35)
ax1.text(500, ax1.get_ylim()[1] - 0.04, "chauffe\n(écartée)", ha="center", va="top", color="#52514e", fontsize=9)
ax1.set_xlabel("itération")
ax1.set_ylabel(r"$\beta_{\mathrm{offre}}$")
ax1.set_title("Quatre chaînes, quatre points de départ")
for c in range(4):
    ax2.hist(apres[c, :, j], bins=40, density=True, histtype="step", color=couleurs[c], lw=1.4)
ax2.set_xlabel(r"$\beta_{\mathrm{offre}}$ (après chauffe)")
ax2.set_yticks([])
ax2.set_title("Les quatre distributions")
plt.tight_layout()
plt.savefig("figures/ch06-traces-quatre-chaines.png", dpi=200, bbox_inches="tight")
plt.close()
```

![À gauche : la trace du coefficient de l'offre pour les quatre chaînes lancées de points de départ dispersés. La zone grise correspond à la chauffe, écartée. À droite : après la chauffe, les histogrammes des quatre chaînes se superposent.](figures/ch06-traces-quatre-chaines.png)

Ce qu'on cherche (et ce que l'on voit ici) : (i) **les quatre chaînes, parties de points très différents, se retrouvent dans la même zone** après quelques dizaines ou centaines d'itérations (c'est la « chauffe », en anglais *burn-in* ou *warm-up*, que l'on écarte) ; (ii) **elles se mélangent** : on ne distingue plus de quelle chaîne provient chaque point ; (iii) les histogrammes des quatre chaînes **coïncident**. Le dessin ne suffit pourtant pas : une trace peut sembler « stationnaire » à l'œil alors que la chaîne explore à peine un coin de la loi. On quantifie avec le **$\widehat R$ de Gelman-Rubin**.

> 📐 **L'idée du $\widehat R$ (R-chapeau).** Si $m$ chaînes de longueur $n$ ont convergé vers la même loi, la variabilité **entre** les chaînes ne doit pas dépasser la variabilité **à l'intérieur** de chaque chaîne. Soient $\bar\theta_j$ et $s_j^2$ la moyenne et la variance de la chaîne $j$, et $\bar\theta$ la moyenne générale. On calcule
> $$W=\frac1m\sum_j s_j^2\quad(\text{variance intra}),\qquad B=\frac{n}{m-1}\sum_j(\bar\theta_j-\bar\theta)^2\quad(\text{variance inter}),$$
> puis la meilleure estimation de la variance de la loi cible, $\widehat{\mathrm{var}}^+=\dfrac{n-1}{n}W+\dfrac Bn$, qui **surestime** cette variance tant que les chaînes n'ont pas convergé. On pose
> $$\widehat R=\sqrt{\frac{\widehat{\mathrm{var}}^+}{W}}\ \ge\ 1\ \text{(approximativement)}.$$
> Si les chaînes sont bien mélangées, $B\approx W$ et $\widehat R\approx1$ ; si elles sont chacune bloquées dans un coin différent, $B\gg W$ et $\widehat R\gg1$. On utilise aujourd'hui la version **« découpée »** (*split*-$\widehat R$) : on coupe chaque chaîne en deux moitiés avant de calculer, ce qui permet de détecter aussi une chaîne qui dérive lentement (ses deux moitiés ne se ressemblent pas). La recommandation actuelle est $\widehat R<1{,}01$ (l'ancien seuil de 1,1 est jugé trop laxiste).

```python
def split_rhat(ch):
    """ch : tableau (m chaînes, n itérations). Split-R-chapeau de Gelman-Rubin."""
    m, n = ch.shape
    moitie = n // 2
    parts = np.concatenate([ch[:, :moitie], ch[:, moitie:2 * moitie]], axis=0)     # 2m chaînes de longueur n/2
    M, N = parts.shape
    W = parts.var(axis=1, ddof=1).mean()
    B = N * parts.mean(axis=1).var(ddof=1)
    var_plus = (N - 1) / N * W + B / N
    return np.sqrt(var_plus / W)

def ess_total(ch):
    return sum(ess(ch[c]) for c in range(ch.shape[0]))                              # somme des ESS de chaque chaîne

lignes = []
for jj, nom in enumerate(noms):
    lignes.append({"paramètre": nom, "R-chapeau (chauffe incluse)": round(split_rhat(chaines[:, :, jj]), 4),
                   "R-chapeau (chauffe écartée)": round(split_rhat(apres[:, :, jj]), 4),
                   "ESS": round(ess_total(apres[:, :, jj]))})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
paramètre  R-chapeau (chauffe incluse)  R-chapeau (chauffe écartée)  ESS
    const                       1.0037                       1.0010 1281
    offre                       1.0064                       1.0023 1276
    age_c                       1.0163                       1.0009 1114
Instagram                       1.0022                       1.0037 1158
     Site                       1.0043                       1.0024 1205
```

Deux enseignements. D'abord, **écarter la chauffe améliore le diagnostic** : en gardant les 1 000 premières itérations, le $\widehat R$ de l'âge est de 1,016 (au-dessus du seuil de 1,01) ; une fois la chauffe retirée, les cinq $\widehat R$ sont inférieurs à 1,004 : les quatre chaînes disent la même chose. (L'effet est modeste ici parce que la loi est presque gaussienne et que la chaîne s'y installe vite ; dans un modèle plus difficile, la chauffe peut faire la différence entre $\widehat R=1{,}5$ et $\widehat R=1{,}00$.) Ensuite, les **ESS** sont de l'ordre de 1 100 à 1 300 : pour estimer une moyenne ou un intervalle de crédibilité à 95 %, la règle usuelle est de viser au moins 400 à 1 000 ; nous sommes dans la fourchette. (Pour des quantiles extrêmes, il en faut davantage.)

> ⚠️ **Ce que l'ESS que nous calculons simplifie.** Nous additionnons les ESS de chaque chaîne. Les logiciels (Stan, ArviZ) utilisent une version qui combine les autocorrélations de toutes les chaînes et des transformations par rangs : elle est plus fiable pour les lois à queues lourdes. Pour nos besoins, l'ordre de grandeur est le même.

**Que se passe-t-il quand la convergence échoue ?** Un diagnostic n'a de valeur que si on a vu au moins une fois à quoi il ressemble quand il détecte quelque chose. Prenons une loi cible à **deux bosses**, mélange à parts égales de $\mathcal N(-4,1)$ et $\mathcal N(4,1)$ (moyenne exacte : 0), et lançons quatre chaînes de Metropolis de points de départ $-6,-2,2,6$, avec un pas petit (0,5) puis grand (6).

```python
def log_bimodale(x):
    return np.logaddexp(stats.norm.logpdf(x, -4, 1), stats.norm.logpdf(x, 4, 1))

lignes, traces_b = [], {}
for pas in (0.5, 6.0):
    rng = np.random.default_rng(641)
    ch = np.array([metropolis_1d(log_bimodale, x0, n=5000, pas=pas, rng=rng)[0] for x0 in (-6, -2, 2, 6)])
    traces_b[pas] = ch
    lignes.append({"pas": pas, "moyennes des 4 chaînes": np.round(ch[:, 1000:].mean(axis=1), 2),
                   "moyenne globale": round(ch[:, 1000:].mean(), 2),
                   "R-chapeau": round(split_rhat(ch[:, 1000:]), 3), "ESS": round(ess_total(ch[:, 1000:]))})
print(pd.DataFrame(lignes).to_string(index=False))
print("moyenne exacte de la loi cible : 0.00")
```
<!--sortie-->
```text
 pas     moyennes des 4 chaînes  moyenne globale  R-chapeau  ESS
 0.5  [-4.08, 3.71, 4.06, 3.92]             1.90      3.072  546
 6.0 [-0.16, 0.16, -0.28, 0.17]            -0.03      1.002 1430
moyenne exacte de la loi cible : 0.00
```

Avec le petit pas, chaque chaîne reste **piégée dans sa bosse** : une chaîne est restée autour de $-4$, les trois autres autour de $+4$ ; la moyenne globale vaut 1,90 au lieu de 0 ; et le $\widehat R$ vaut 3,07, très loin de 1. Remarquez que l'ESS (546) a l'air honorable : elle est calculée chaîne par chaîne et ne voit pas qu'il manque une bosse. **Seule la comparaison entre chaînes (le $\widehat R$) donne l'alerte.** Fait plus grave : si on n'avait lancé *qu'une seule chaîne*, on aurait trouvé une moyenne proche de $-4$ ou de $+4$ avec un bel intervalle de crédibilité étroit, **tout à fait faux** : rien dans une chaîne unique ne signale qu'il manque une bosse. C'est la raison pour laquelle on lance toujours **plusieurs chaînes depuis des points de départ dispersés**. Avec le grand pas, les chaînes sautent d'une bosse à l'autre : $\widehat R=1{,}002$ et la moyenne globale (−0,03) est proche de 0.

> 💡 **Le diagnostic le plus important : plusieurs chaînes dispersées.** Presque tous les problèmes de convergence se voient en comparant des chaînes parties de points différents. **Ne jamais se contenter d'une seule chaîne.**

### 6.4.2 Le modèle est-il plausible ? Les vérifications prédictives a posteriori

Même si la chaîne est parfaite, le modèle peut être faux. Le test de bon sens est le suivant : **si le modèle était vrai, les données qu'il simulerait ressembleraient-elles aux données réelles ?** C'est la **vérification prédictive a posteriori** (*posterior predictive check*).

> **Procédure.** (1) Tirer un jeu de paramètres $\theta^{(s)}$ dans la loi a posteriori. (2) Simuler un **jeu de données répliqué** $y^{\mathrm{rep},(s)}$ avec ce $\theta^{(s)}$, de la même taille que les données observées. (3) Calculer une **statistique-test** $T$ (une caractéristique qui nous inquiète : variance, maximum, proportion de zéros…) sur chaque jeu répliqué. (4) Comparer $T(y)$ observé à la distribution des $T(y^{\mathrm{rep}})$. Le **p-value bayésien** $p_B=P\bigl(T(y^{\mathrm{rep}})\ge T(y)\mid y\bigr)$ est la fraction de répliques au-dessus de l'observé : une valeur proche de 0 ou de 1 signale un désaccord.

*Remarque :* il ne s'agit pas d'un test au sens du volume I : le $p_B$ n'est pas uniforme sous le modèle vrai (il est conservateur, car les données servent deux fois : à ajuster le modèle et à le tester). On l'utilise comme **indicateur de désaccord**, pas comme un seuil de décision.

**Retour sur le modèle de Poisson de 6.1.8.** Nous avions modélisé le nombre de commandes annuelles `nb_commandes_an` des 504 clients de la boutique par une loi de Poisson de paramètre $\lambda$ commun, et obtenu l'a posteriori $\mathrm{Gamma}(2087;\ 504{,}5)$. Il avait l'air parfait : un intervalle étroit. Soumettons-le à la vérification.

```python
clients = pd.read_csv("donnees/clients.csv")
b = clients.loc[clients["canal_acquisition"] == "Boutique", "nb_commandes_an"].to_numpy()
n_b = len(b)

def stats_test(yrep):
    """Trois statistiques sur chaque jeu (lignes) : variance/moyenne, part de zéros, maximum."""
    return np.c_[yrep.var(axis=1, ddof=1) / yrep.mean(axis=1), (yrep == 0).mean(axis=1), yrep.max(axis=1)]

T_obs = stats_test(b[None, :])[0]
noms_T = ["variance / moyenne", "part de zéros", "maximum"]

rng = np.random.default_rng(642)
lam = stats.gamma(a=2 + b.sum(), scale=1 / (0.5 + n_b)).rvs(2000, random_state=rng)      # a posteriori de 6.1.8
yrep_pois = rng.poisson(lam[:, None], size=(2000, n_b))                                    # 2000 jeux répliqués
T_pois = stats_test(yrep_pois)

lignes = []
for k_, nom in enumerate(noms_T):
    lignes.append({"statistique": nom, "observée": round(T_obs[k_], 3), "répliques : moyenne": round(T_pois[:, k_].mean(), 3),
                   "répliques : 2,5 %": round(np.percentile(T_pois[:, k_], 2.5), 3),
                   "répliques : 97,5 %": round(np.percentile(T_pois[:, k_], 97.5), 3),
                   "p bayésien": round((T_pois[:, k_] >= T_obs[k_]).mean(), 3)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
       statistique  observée  répliques : moyenne  répliques : 2,5 %  répliques : 97,5 %  p bayésien
variance / moyenne     3.324                1.000              0.879               1.127         0.0
     part de zéros     0.109                0.016              0.006               0.030         0.0
           maximum    21.000               11.541             10.000              14.000         0.0
```

Le verdict est sans appel. La variance observée est **3,3 fois la moyenne**, alors que les jeux répliqués par le modèle de Poisson ont un rapport proche de 1. Le modèle ne simule **ni autant de zéros** (11 % observés, environ 1,6 % répliqués), **ni de valeurs aussi grandes** (maximum observé de 21, contre 11,5 en moyenne dans les répliques, avec un intervalle à 95 % de [10 ; 14]). Les trois $p_B$ valent 0 : aucune réplique sur 2 000 n'atteint les données. **Le modèle de Poisson est rejeté**, et la raison est celle qu'on soupçonnait : les clients sont hétérogènes.

**Réparation : la loi binomiale négative.** On suppose que le paramètre de Poisson **varie d'un client à l'autre** selon une loi gamma ; en intégrant cette variation (la marginalisation d'un mélange gamma-Poisson, que nous retrouverons au chapitre 2, section 2.6), le nombre de commandes suit une loi **binomiale négative** de moyenne $\mu$ et de paramètre de dispersion $k$ : $\mathrm{Var}=\mu+\mu^2/k$. Quand $k\to\infty$, on retrouve Poisson ; plus $k$ est petit, plus la surdispersion est forte. Il n'y a plus de conjugaison, donc… on utilise notre MCMC. Paramétrons $\theta=(\log\mu,\log k)$ pour travailler sur des réels, avec des a priori $\log\mu\sim\mathcal N(1,2^2)$ et $\log k\sim\mathcal N(0,2^2)$, larges.

```python
def log_post_nb(theta):
    mu, k = np.exp(theta[0]), np.exp(theta[1])
    log_vrais = stats.nbinom.logpmf(b, k, k / (k + mu)).sum()
    log_prior = -0.5 * ((theta[0] - 1) / 2) ** 2 - 0.5 * ((theta[1] - 0) / 2) ** 2
    return log_vrais + log_prior

rng = np.random.default_rng(643)
pilote, _ = metropolis_multi(log_post_nb, np.array([np.log(b.mean()), 0.0]), 3000, np.diag([0.003, 0.02]), rng)
cov_nb = np.cov(pilote[500:].T) * (2.38**2 / 2)                       # covariance estimée sur une course pilote

chaines_nb, taux_nb = [], []
for c in range(4):
    depart = np.array([np.log(b.mean()) + rng.normal(0, 0.3), rng.normal(0, 1.0)])
    ch, tx = metropolis_multi(log_post_nb, depart, 5000, cov_nb, rng)
    chaines_nb.append(ch[1000:]); taux_nb.append(tx)
chaines_nb = np.array(chaines_nb)
print("taux d'acceptation :", np.round(taux_nb, 3))
print("R-chapeau (log mu, log k) :", [round(float(split_rhat(chaines_nb[:, :, i])), 4) for i in range(2)],
      "| ESS :", [int(round(ess_total(chaines_nb[:, :, i]))) for i in range(2)])

mu_s, k_s = np.exp(chaines_nb[:, :, 0].ravel()), np.exp(chaines_nb[:, :, 1].ravel())
print(f"mu : moyenne {mu_s.mean():.3f}  IC95 [{np.percentile(mu_s, 2.5):.3f} ; {np.percentile(mu_s, 97.5):.3f}]")
print(f"k  : médiane {np.median(k_s):.3f}  IC95 [{np.percentile(k_s, 2.5):.3f} ; {np.percentile(k_s, 97.5):.3f}]")
print(f"rappel Poisson (6.1.8) : IC95 de lambda [3.961 ; 4.316], largeur {4.316 - 3.961:.3f} | binomiale négative : largeur de mu {np.diff(np.percentile(mu_s, [2.5, 97.5]))[0]:.3f}")
```
<!--sortie-->
```text
taux d'acceptation : [0.365 0.352 0.357 0.354]
R-chapeau (log mu, log k) : [1.0029, 1.0019] | ESS : [1951, 2241]
mu : moyenne 4.134  IC95 [3.817 ; 4.457]
k  : médiane 1.817  IC95 [1.513 ; 2.199]
rappel Poisson (6.1.8) : IC95 de lambda [3.961 ; 4.316], largeur 0.355 | binomiale négative : largeur de mu 0.639
```

Les chaînes sont saines ($\widehat R$ proche de 1, ESS élevées). La dispersion $k$ est estimée à environ 1,8 (intervalle environ [1,5 ; 2,2]), loin de l'infini de Poisson. Notez surtout que **l'intervalle de crédibilité de la moyenne est plus large que celui du modèle de Poisson** (largeur 0,64 contre 0,36) : le modèle de Poisson **sous-estimait l'incertitude** en la faisant porter par une moyenne unique, alors que les clients varient. C'est l'effet typique d'un modèle trop simple : intervalles trop étroits. Les données étant simulées, la vérité est connue : le générateur utilise justement une dispersion $k=2$ (avec, en plus, d'autres sources d'hétérogénéité : le goût pour les produits et l'âge) : le $k$ estimé est cohérent. Revérifions le modèle réparé avec les mêmes statistiques :

```python
idx = rng.choice(len(mu_s), 2000, replace=False)
p_nb = k_s[idx] / (k_s[idx] + mu_s[idx])
yrep_nb = rng.negative_binomial(k_s[idx][:, None], p_nb[:, None], size=(2000, n_b))
T_nb = stats_test(yrep_nb)

lignes = []
for k_, nom in enumerate(noms_T):
    lignes.append({"statistique": nom, "observée": round(T_obs[k_], 3), "répliques : moyenne": round(T_nb[:, k_].mean(), 3),
                   "répliques : 2,5 %": round(np.percentile(T_nb[:, k_], 2.5), 3),
                   "répliques : 97,5 %": round(np.percentile(T_nb[:, k_], 97.5), 3),
                   "p bayésien": round((T_nb[:, k_] >= T_obs[k_]).mean(), 3)})
print(pd.DataFrame(lignes).to_string(index=False))

fig, axes = plt.subplots(2, 3, figsize=(10.5, 5.2))
for ligne, (T_rep, titre, couleur) in enumerate([(T_pois, "Poisson", ORANGE), (T_nb, "binomiale négative", BLEU)]):
    for col in range(3):
        ax = axes[ligne, col]
        ax.hist(T_rep[:, col], bins=30, color=couleur, alpha=0.75)
        ax.axvline(T_obs[col], color=ROUGE, lw=2.0)
        if ligne == 0:
            ax.set_title(noms_T[col])
        ax.set_yticks([])
        if col == 0:
            ax.set_ylabel(titre, color=couleur, fontsize=11)
        ax.grid(False)
for ligne in range(2):
    axes[ligne, 0].text(0.97, 0.95, "trait rouge :\nobservé", transform=axes[ligne, 0].transAxes, ha="right", va="top", color=ROUGE, fontsize=9)
plt.tight_layout()
plt.savefig("figures/ch06-ppc-poisson-binneg.png", dpi=200, bbox_inches="tight")
plt.close()
```
<!--sortie-->
```text
       statistique  observée  répliques : moyenne  répliques : 2,5 %  répliques : 97,5 %  p bayésien
variance / moyenne     3.324                3.287              2.653               4.049       0.434
     part de zéros     0.109                0.117              0.083               0.155       0.667
           maximum    21.000               22.964             17.000              32.000       0.714
```

![Vérification prédictive a posteriori de deux modèles pour le nombre de commandes annuelles des clients de la boutique. En haut, le modèle de Poisson : les histogrammes des trois statistiques répliquées (variance sur moyenne, part de zéros, maximum) sont loin de la valeur observée (trait rouge). En bas, la binomiale négative : la valeur observée est au milieu des répliques.](figures/ch06-ppc-poisson-binneg.png)

Cette fois, les trois statistiques observées tombent **au milieu** des répliques (les $p_B$ sont loin de 0 et de 1). Le dessin résume la morale : en haut, les données (trait rouge) sont à l'extérieur du nuage des répliques de Poisson ; en bas, elles sont à l'intérieur de celui de la binomiale négative. **Le modèle n'est pas « prouvé vrai »** (aucun ne l'est), mais il a passé trois épreuves que l'autre a échouées.

> ⚠️ **Choisir ses statistiques-test.** Une vérification prédictive ne détecte que les défauts que l'on a pensé à tester. Choisissez des statistiques qui **ne sont pas directement ajustées** par le modèle (la moyenne, que le modèle reproduit par construction, ne révélerait rien) et qui correspondent à vos **soucis** : queues, zéros, asymétrie, dépendance dans le temps, etc.

### 6.4.3 L'a priori est-il raisonnable ? La vérification prédictive *a priori*

Avant même de regarder les données, on peut se demander ce que **l'a priori seul implique**. On simule des paramètres dans l'a priori, puis des données dans le modèle : on obtient la loi **prédictive a priori**. Si elle attribue des probabilités énormes à des scénarios absurdes, l'a priori est mal choisi.

Pour la régression logistique du rachat, regardons ce que signifient des a priori $\beta_j\sim\mathcal N(0,s^2)$ de plus en plus larges, en calculant, pour chaque tirage de $\beta$, la **proportion prédite de clients qui rachètent** :

```python
rng = np.random.default_rng(644)
sigmoide = lambda u: 1 / (1 + np.exp(-u))
resultats, lignes = {}, []
for s in (0.5, 1.5, 2.5, 10.0):
    betas = rng.normal(0, s, size=(3000, Xm.shape[1]))
    p_ind = sigmoide(betas @ Xm.T)                                    # (3000 tirages, 2000 clients)
    taux = p_ind.mean(axis=1)                                         # taux de rachat prédit pour chaque tirage
    resultats[s] = taux
    lignes.append({"écart-type de l'a priori s": s, "taux prédit : 5 %-95 %": f"[{np.percentile(taux, 5):.2f} ; {np.percentile(taux, 95):.2f}]",
                   "tirages avec taux < 5 % ou > 95 %": f"{np.mean((taux < 0.05) | (taux > 0.95)):.1%}",
                   "clients avec p < 1 % ou > 99 % (en moyenne)": f"{np.mean((p_ind < 0.01) | (p_ind > 0.99)):.1%}"})
print(pd.DataFrame(lignes).to_string(index=False))
print("\ntaux de rachat réel observé :", y.mean().round(3))
```
<!--sortie-->
```text
 écart-type de l'a priori s taux prédit : 5 %-95 % tirages avec taux < 5 % ou > 95 % clients avec p < 1 % ou > 99 % (en moyenne)
                        0.5          [0.28 ; 0.71]                              0.0%                                        0.0%
                        1.5          [0.12 ; 0.90]                              2.8%                                        8.6%
                        2.5          [0.05 ; 0.94]                              9.2%                                       28.7%
                       10.0          [0.01 ; 0.99]                             19.3%                                       79.2%

taux de rachat réel observé : 0.509
```

Lecture : avec $s=0{,}5$, l'a priori est **trop serré** : il n'autorise pratiquement que des taux entre 30 % et 70 %, alors que nous ne savons pas à l'avance qu'ils sont dans cette fourchette. Avec $s=10$, l'a priori est **absurde** : en moyenne, **79 % des clients** y ont une probabilité individuelle de rachat inférieure à 1 % ou supérieure à 99 %, et dans un tirage sur cinq le taux global est inférieur à 5 % ou supérieur à 95 %. Cela n'a rien d'une « ignorance » : c'est une opinion très tranchée, que nous n'avons aucune raison d'avoir. Le choix $s=2{,}5$ de la section 6.3.5 est déjà **généreux** (29 % des clients à probabilité individuelle extrême), $s=1{,}5$ plus prudent (9 %). Les deux autorisent une **large gamme de taux globaux** sans verser dans l'extrême ; nous vérifierons en 6.4.4 que le choix entre eux n'influence pas nos conclusions. Voici le dessin :

```python
fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), sharey=True)
for ax, s, coul in zip(axes, (0.5, 2.5, 10.0), (ORANGE, BLEU, VIOLET)):
    ax.hist(resultats[s], bins=np.linspace(0, 1, 41), color=coul, alpha=0.8)
    ax.axvline(y.mean(), color="#0b0b0b", lw=1.0, ls="--")
    sf = f"{s:g}".replace(".", "{,}")
    ax.set_title(f"a priori $\\mathcal{{N}}(0, {sf}^2)$", color=coul)
    ax.set_xlabel("taux de rachat prédit (tirage de l'a priori)")
    ax.set_yticks([])
    ax.grid(False)
axes[0].text(0.03, 0.97, "pointillés :\ntaux observé (0,51)", transform=axes[0].transAxes, ha="left", va="top", fontsize=9)
plt.tight_layout()
plt.savefig("figures/ch06-prior-predictive.png", dpi=200, bbox_inches="tight")
plt.close()
```

![Taux de rachat global prédit par l'a priori seul, pour trois largeurs d'a priori sur les coefficients de la régression logistique. Trop serré (à gauche) : tous les modèles prédisent à peu près le même taux. Raisonnable (au milieu) : une gamme étendue de taux plausibles. Trop large (à droite) : la masse s'accumule près de 0 et de 1, des scénarios absurdes.](figures/ch06-prior-predictive.png)

> 💡 **Règle pratique.** On ne peut pas vérifier un a priori par les données (ce serait les utiliser deux fois), mais on peut vérifier ses **conséquences** sur des quantités que l'on comprend (un taux, une moyenne, une durée). Si l'a priori produit des scénarios que vous jugeriez ridicules, resserrez-le.

### 6.4.4 Comparer des modèles : facteur de Bayes et WAIC

**Le facteur de Bayes.** Comparons deux modèles (ou deux hypothèses) $H_0$ et $H_1$ par la formule de Bayes appliquée aux modèles : $\dfrac{P(H_1\mid y)}{P(H_0\mid y)}=\underbrace{\dfrac{p(y\mid H_1)}{p(y\mid H_0)}}_{\text{facteur de Bayes }\mathrm{BF}_{10}}\times\dfrac{P(H_1)}{P(H_0)}$, où $p(y\mid H)=\int p(y\mid\theta,H)\,p(\theta\mid H)\,d\theta$ est la **vraisemblance marginale** (la moyenne de la vraisemblance sur l'a priori). Le $\mathrm{BF}_{10}$ mesure de combien les données déplacent la cote en faveur de $H_1$.

*Exemple à la main.* Une pièce (ou une offre) donne $y$ succès sur $n$ essais. $H_0$ : $\theta=0{,}5$ exactement. $H_1$ : $\theta$ est inconnu avec un a priori uniforme sur $[0,1]$. Alors $p(y\mid H_0)=\binom ny0{,}5^n$ et
$$p(y\mid H_1)=\binom ny\int_0^1\theta^y(1-\theta)^{n-y}d\theta=\binom ny B(y+1,n-y+1)=\frac1{n+1}.$$
(Résultat remarquable : avec un a priori uniforme, **chaque** valeur de $y$ entre 0 et $n$ est également probable a priori.) Pour $n=10,\ y=7$ : $p(y\mid H_0)=120/1024=0{,}1172$ et $p(y\mid H_1)=1/11=0{,}0909$. Donc $\mathrm{BF}_{10}=0{,}0909/0{,}1172=0{,}776$ : les données sont **un peu plus probables sous $H_0$** que sous $H_1$. Sept succès sur dix ne suffisent pas à abandonner la pièce équilibrée ! Le p-value fréquentiste bilatéral est 0,34 : le même message. Le code reproduit ce calcul et l'applique à nos données d'offre.

```python
from scipy.special import gammaln

def log_bf10(y_, n_):
    """log du facteur de Bayes de H1 (theta ~ U(0,1)) contre H0 (theta = 0,5)."""
    log_m1 = -np.log(n_ + 1)
    log_m0 = gammaln(n_ + 1) - gammaln(y_ + 1) - gammaln(n_ - y_ + 1) + n_ * np.log(0.5)
    return log_m1 - log_m0

cas = [("7 rachats sur 10", 7, 10), ("offre : 578 sur 1 015", 578, 1015), ("50 400 sur 100 000", 50_400, 100_000)]
lignes = []
for nom, yy_, nn in cas:
    bf = np.exp(log_bf10(yy_, nn))
    lignes.append({"cas": nom, "fréquence": round(yy_ / nn, 4), "p-valeur (bilatérale)": f"{stats.binomtest(yy_, nn, 0.5).pvalue:.2g}",
                   "BF10": f"{bf:.3g}", "P(H1 | données) si a priori 50/50": f"{bf / (1 + bf):.3f}"})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
                  cas  fréquence p-valeur (bilatérale)   BF10 P(H1 | données) si a priori 50/50
     7 rachats sur 10     0.7000                  0.34  0.776                             0.437
offre : 578 sur 1 015     0.5695               1.1e-05    720                             0.999
   50 400 sur 100 000     0.5040                 0.012 0.0972                             0.089
```

Trois cas, trois leçons. (1) *Peu de données* : le facteur de Bayes de 0,78 et la p-valeur de 0,34 s'accordent : on ne peut pas conclure. (2) *Beaucoup de données et un grand écart* (578 sur 1 015) : les deux approches rejettent fermement $H_0$. (3) Le dernier cas est le **paradoxe de Lindley** : avec 100 000 observations et une fréquence de 50,4 %, la p-valeur fréquentiste est petite (0,012 : « significatif au seuil de 5 % », voire de 2 %), alors que le facteur de Bayes ($0{,}097$) **favorise $H_0$ d'un facteur 10** : un écart de 0,4 point est ridicule comparé à ce que prédit l'hypothèse $H_1$ (qui étale sa probabilité sur tout l'intervalle $[0,1]$). La p-valeur se laisse impressionner par la taille de l'échantillon ; le facteur de Bayes pénalise l'hypothèse qui « dilue » sa probabilité inutilement. C'est aussi le **point faible** du facteur de Bayes : il **dépend fortement de l'a priori** (ici, de l'étalement uniforme sous $H_1$). Un a priori plus concentré autour de 0,5 donnerait un autre résultat.

> ⚠️ **Prudence.** Le facteur de Bayes est très sensible au choix de l'a priori sur les paramètres. Il est difficile à calculer pour des modèles complexes (une intégrale en grande dimension). Beaucoup de praticiens bayésiens lui préfèrent des outils prédictifs comme le WAIC ci-dessous.

**Le WAIC : juger un modèle par ses prédictions.** L'idée : un bon modèle est celui qui **prédit bien des données nouvelles**. Le critère **WAIC** (*widely applicable information criterion*) estime la qualité prédictive hors échantillon à partir des seuls tirages a posteriori :
$$\mathrm{lppd}=\sum_{i=1}^n\log\!\Big(\frac1S\sum_{s=1}^S p(y_i\mid\theta^{(s)})\Big),\qquad p_{\mathrm{WAIC}}=\sum_{i=1}^n\mathrm{Var}_s\big[\log p(y_i\mid\theta^{(s)})\big],\qquad \mathrm{WAIC}=-2\,(\mathrm{lppd}-p_{\mathrm{WAIC}}).$$
Le premier terme mesure l'ajustement aux données (plus il est grand, mieux le modèle colle) ; $p_{\mathrm{WAIC}}$ est le **nombre effectif de paramètres**, une pénalité qui punit la complexité (c'est l'analogue bayésien de la pénalité de l'AIC, section 1.4). **Plus le WAIC est petit, meilleur est le modèle.** Comparons quatre modèles du rachat, du plus simple au plus complet, en les estimant tous par notre MCMC :

```python
def fit_mcmc_logit(colonnes, graine, n_chaines=4, n_iter=3000, chauffe=500, s=2.5):
    Xs = X[colonnes].to_numpy()
    emv_ = sm.Logit(y, Xs).fit(disp=0)
    dim_ = Xs.shape[1]
    cov_ = (2.38**2 / dim_) * np.atleast_2d(emv_.cov_params())
    def lp(beta):
        eta = Xs @ beta
        return np.sum(y * eta - np.logaddexp(0, eta)) - 0.5 * np.sum(beta**2) / s**2
    rng_ = np.random.default_rng(graine)
    tir = []
    for _ in range(n_chaines):
        depart = emv_.params + rng_.normal(0, 0.5, dim_)
        ch, _ = metropolis_multi(lp, depart, n_iter, cov_, rng_)
        tir.append(ch[chauffe:])
    return np.concatenate(tir)[::5], Xs, emv_                          # on éclaircit : 1 tirage sur 5

def waic(tir, Xs):
    eta = tir @ Xs.T                                                  # (S tirages, n clients)
    ll = y * eta - np.logaddexp(0, eta)                               # log p(y_i | theta_s)
    S = ll.shape[0]
    lppd_i = np.logaddexp.reduce(ll, axis=0) - np.log(S)
    pw_i = ll.var(axis=0, ddof=1)
    elpd_i = lppd_i - pw_i
    return -2 * elpd_i.sum(), pw_i.sum(), -2 * elpd_i

modeles = {"M0 : constante": ["const"], "M1 : + offre": ["const", "offre"],
           "M2 : + canal": ["const", "offre", "Instagram", "Site"], "M3 : + âge": ["const", "offre", "Instagram", "Site", "age_c"]}
res, pointwise = [], {}
for i, (nom, cols) in enumerate(modeles.items()):
    tir, Xs, emv_ = fit_mcmc_logit(cols, graine=650 + i)
    w, pw, pt = waic(tir, Xs)
    pointwise[nom] = pt
    res.append({"modèle": nom, "paramètres": len(cols), "p_WAIC": round(pw, 2), "WAIC": round(w, 1), "AIC (EMV)": round(emv_.aic, 1)})
tab = pd.DataFrame(res)
tab["WAIC - min"] = (tab["WAIC"] - tab["WAIC"].min()).round(1)
print(tab.to_string(index=False))

noms_m = list(modeles)
for a, b_ in (("M0 : constante", "M1 : + offre"), ("M1 : + offre", "M2 : + canal"), ("M2 : + canal", "M3 : + âge")):
    diff = pointwise[a] - pointwise[b_]
    print(f"{a[:2]} - {b_[:2]} : différence de WAIC = {diff.sum():6.1f}, erreur-type = {np.sqrt(len(diff) * diff.var(ddof=1)):.1f}")
```
<!--sortie-->
```text
        modèle  paramètres  p_WAIC   WAIC  AIC (EMV)  WAIC - min
M0 : constante           1    1.00 2773.9     2773.9        53.1
  M1 : + offre           2    1.89 2745.9     2746.1        25.1
  M2 : + canal           4    4.26 2732.1     2731.6        11.3
    M3 : + âge           5    4.95 2720.8     2720.8         0.0
M0 - M1 : différence de WAIC =   27.9, erreur-type = 10.9
M1 - M2 : différence de WAIC =   13.8, erreur-type = 8.5
M2 - M3 : différence de WAIC =   11.4, erreur-type = 7.0
```

Le WAIC **décroît** à mesure que l'on ajoute l'offre, puis le canal, puis l'âge. Le $p_{\mathrm{WAIC}}$ est très proche du nombre de paramètres (comme il se doit pour un modèle régulier avec beaucoup de données), et le WAIC est quasiment égal à l'AIC calculé par le maximum de vraisemblance : avec un a priori diffus et beaucoup de données, les deux critères racontent la même histoire. Les dernières lignes comparent les gains avec leur **incertitude** (un WAIC isolé ne signifie rien : seules les **différences entre modèles** comptent, et leur erreur-type). Une différence est jugée « claire » si elle dépasse environ deux erreurs-types. Ici, l'offre apporte un gain net (27,9 ± 10,9, soit 2,6 erreurs-types) ; le canal (13,8 ± 8,5) et l'âge (11,4 ± 7,0) apportent des gains d'environ 1,6 erreur-type : **plausibles mais non tranchés** par le WAIC seul. Cela ne contredit pas la section 6.3.5, où les intervalles de crédibilité de l'âge et du canal Instagram excluent 0 : le WAIC répond à la question « *ce coefficient améliore-t-il la prédiction de clients nouveaux ?* », pas à « *ce coefficient est-il différent de zéro ?* ».

**Sensibilité à l'a priori (6.1.6, enfin faite).** Terminons par l'analyse de sensibilité promise : le coefficient de l'offre change-t-il si l'on modifie l'écart-type $s$ de l'a priori ?

```python
lignes = []
for i, s_ in enumerate((0.5, 1.5, 2.5, 10.0)):
    tir, Xs, emv_ = fit_mcmc_logit(["const", "offre", "Instagram", "Site", "age_c"], graine=660 + i, s=s_)
    bo = tir[:, 1]
    lignes.append({"s de l'a priori": s_, "moyenne a posteriori de beta_offre": round(bo.mean(), 3),
                   "IC95 bas": round(np.percentile(bo, 2.5), 3), "IC95 haut": round(np.percentile(bo, 97.5), 3)})
print(pd.DataFrame(lignes).to_string(index=False))
print("rappel : EMV de beta_offre =", round(emv.params[1], 3))
```
<!--sortie-->
```text
 s de l'a priori  moyenne a posteriori de beta_offre  IC95 bas  IC95 haut
             0.5                               0.476     0.291      0.653
             1.5                               0.488     0.296      0.672
             2.5                               0.492     0.314      0.665
            10.0                               0.494     0.321      0.658
rappel : EMV de beta_offre = 0.493
```

Les résultats sont presque identiques pour les quatre a priori (moyenne a posteriori de 0,476 à 0,494, contre 0,493 pour le maximum de vraisemblance), y compris pour l'a priori très serré ($s=0{,}5$, qui ramène un peu le coefficient vers 0) et l'a priori très large ($s=10$) : **nos conclusions ne dépendent pas de l'a priori**, parce que 2 000 observations suffisent à dominer. C'est la situation confortable décrite en 6.1.6, mais elle ne se serait pas produite avec 20 clients.

### 6.4.5 Le flux de travail bayésien, en une page

Voici la liste de contrôle qui résume cette section. Elle est le prolongement bayésien de la démarche du volume I (« décrire, dessiner, contrôler »).

1. **Écrire le modèle** : vraisemblance et a priori. Dire pourquoi.
2. **Vérifier l'a priori** (6.4.3) : la loi prédictive a priori produit-elle des scénarios plausibles ?
3. **Ajuster** avec plusieurs chaînes dispersées (6.3), chauffe écartée.
4. **Diagnostiquer l'algorithme** (6.4.1) : traces en « chenille velue », $\widehat R<1{,}01$, ESS d'au moins quelques centaines pour chaque paramètre d'intérêt. En cas d'échec : changer le pas, reparamétriser, allonger.
5. **Vérifier le modèle** (6.4.2) : jeux répliqués comparables aux données sur des statistiques qui vous inquiètent. En cas d'échec : enrichir le modèle (comme la binomiale négative).
6. **Analyser la sensibilité** (6.1.6) : refaire avec d'autres a priori raisonnables ; la conclusion change-t-elle ?
7. **Comparer** éventuellement des modèles (WAIC, facteur de Bayes en connaissance de cause).
8. **Rapporter** : le modèle, les a priori, les diagnostics, les intervalles de crédibilité, les limites.

> ✅ **À retenir (6.4).**
> - Deux risques indépendants : **l'algorithme** n'a pas convergé, ou **le modèle** est faux. Un diagnostic qui passe ne prouve rien ; un diagnostic qui échoue signale un problème.
> - **Convergence** : plusieurs chaînes dispersées, chauffe écartée, traces en « chenille velue », $\widehat R<1{,}01$, ESS suffisante. Une chaîne unique piégée dans un mode ne signale rien : c'est la comparaison entre chaînes qui détecte le problème.
> - **Vérification prédictive a posteriori** : simuler des données répliquées avec le modèle ajusté et les comparer aux données sur des statistiques ciblées. Le modèle de Poisson échoue (surdispersion), la binomiale négative passe.
> - **Vérification prédictive a priori** : examiner ce que l'a priori implique. Un a priori « vague » mal choisi (écart-type 10 sur un logit) est tout sauf neutre.
> - **Facteur de Bayes** (rapport des vraisemblances marginales) : mesure intuitive mais très sensible à l'a priori (paradoxe de Lindley). **WAIC** : qualité prédictive estimée à partir des tirages ; comparer des modèles par leurs **différences** et leurs erreurs-types.
> - Un a posteriori n'est valide que **conditionnellement au modèle** : la vérification du modèle est une étape à part entière, jamais facultative.


## 6.5 ➕ Pour aller plus loin : la théorie des valeurs extrêmes

> 🧭 **Section optionnelle.** Elle ne suppose que le chapitre 2 du volume I (lois, fonction de répartition, loi des grands nombres) et le maximum de vraisemblance du chapitre 3. Elle peut se lire indépendamment des sections 6.1 à 6.4. Elle prolonge cependant leur esprit : **simuler** pour comprendre, et **vérifier** par rapport à une vérité connue.

> 💡 **Intuition.** La plupart de la statistique s'intéresse au **centre** d'une distribution : la moyenne, la médiane, l'écart-type. Mais certaines décisions se jouent dans les **queues** : « *quel est le plus long retard de livraison que je risque une fois par an ? une fois tous les dix ans ?* », « *quelle est la plus grosse commande à prévoir ?* », « *quel niveau de crue une digue doit-elle supporter ?* ». Ce sont des événements **rares**, que l'on n'a souvent jamais observés. Or **la queue d'une loi n'est pas bien décrite par son centre** : ajuster une loi normale à des données et en extrapoler la queue est l'une des erreurs les plus coûteuses de l'histoire de la gestion du risque. La théorie des valeurs extrêmes fournit des modèles **faits pour la queue**.

### 6.5.1 Le problème : la queue d'une loi normale est trompeuse

Un exemple simple pour fixer les idées. Yasmine suit la **durée de livraison** de chaque colis (en jours). Elle veut savoir quel retard est « tellement long qu'on ne le voit qu'une fois en dix ans ». Elle n'a que dix ans de données : l'événement qu'elle cherche est, au mieux, **à la limite de ce qu'elle a observé**, et souvent au-delà. Il faut donc **extrapoler** hors des données, et la forme de la queue décide du résultat.

**Trois comportements de queue.**

| Type de queue | La probabilité de dépasser $x$ décroît comme… | Exemples | Indice $\xi$ |
|---|---|---|---|
| **Légère, bornée** | s'annule au-delà d'un maximum fini | temps de trajet maximal physique | $\xi<0$ (Weibull) |
| **Exponentielle** | $e^{-x}$ : très vite | lois normale, exponentielle, gamma | $\xi=0$ (Gumbel) |
| **Lourde** | $x^{-1/\xi}$ : lentement, comme une puissance | retards logistiques, pertes d'assurance, crues, montants | $\xi>0$ (Fréchet) |

Pour une queue lourde, des valeurs **énormes** surviennent bien plus souvent que ce que la loi normale ne laisse imaginer. L'indice $\xi$ (« indice de queue » ou *shape*) est le paramètre-clé de la théorie.

### 6.5.2 Le théorème fondamental : la loi du maximum

Soit $X_1,\dots,X_n$ indépendantes de même loi, et $M_n=\max(X_1,\dots,X_n)$. Combien vaut sa loi ? Facile : $P(M_n\le x)=F(x)^n$, où $F$ est la fonction de répartition de chaque $X_i$. Mais cela dépend de $F$ et tend vers 0 ou 1. On cherche une loi **limite** après normalisation.

> 📐 **Exemple à la main (lois exponentielles).** Soient $X_i\sim\mathrm{Exp}(1)$ de fonction de répartition $F(x)=1-e^{-x}$. Normalisons le maximum en le décalant de $\ln n$ : pour tout réel $x$,
> $$P\bigl(M_n-\ln n\le x\bigr)=F(x+\ln n)^n=\left(1-\frac{e^{-x}}{n}\right)^{n}\ \xrightarrow[n\to\infty]{}\ \exp\!\left(-e^{-x}\right),$$
> car $(1-a/n)^n\to e^{-a}$. La loi limite, de fonction de répartition $\exp(-e^{-x})$, s'appelle la loi de **Gumbel**. On vient de démontrer que le maximum de $n$ exponentielles, décalé de $\ln n$, suit approximativement une loi de Gumbel.

> 📐 **Théorème de Fisher-Tippett-Gnedenko (admis).** Si, après un changement d'échelle $M_n\mapsto(M_n-b_n)/a_n$, le maximum converge en loi vers une loi non dégénérée, celle-ci est nécessairement de la forme **GEV** (*Generalized Extreme Value*) :
> $$G(z)=\exp\left\{-\left[1+\xi\,\frac{z-\mu}{\sigma}\right]^{-1/\xi}\right\},\qquad 1+\xi\frac{z-\mu}\sigma>0,$$
> avec trois paramètres : **position** $\mu$, **échelle** $\sigma>0$, **forme** $\xi$ (le cas $\xi=0$ se lit comme la limite $\exp\{-e^{-(z-\mu)/\sigma}\}$, la loi de Gumbel).

Autrement dit, comme le théorème central limite pour les moyennes (volume I, section 2.4), il existe un **résultat universel pour les maxima** : quelle que soit la loi d'origine (ou presque), le maximum d'un grand nombre de valeurs suit une loi GEV. Vérifions-le par simulation sur l'exemple exponentiel :

```python
import numpy as np
import pandas as pd
from scipy import stats

rng = np.random.default_rng(670)
n, reps = 1000, 20_000
maxima = rng.exponential(1.0, size=(reps, n)).max(axis=1) - np.log(n)       # maximum de 1 000 exponentielles, décalé de ln n
print(f"{reps} maxima de {n} lois exponentielles, décalés de ln({n}) = {np.log(n):.3f}")
for x in (-1, 0, 1, 2, 3):
    print(f"P(M - ln n <= {x:2d}) : simulé {np.mean(maxima <= x):.4f} | Gumbel exp(-exp(-x)) = {np.exp(-np.exp(-x)):.4f}")
print("test de Kolmogorov-Smirnov contre la loi de Gumbel :", f"statistique {stats.kstest(maxima, stats.gumbel_r.cdf).statistic:.4f}")
```
<!--sortie-->
```text
20000 maxima de 1000 lois exponentielles, décalés de ln(1000) = 6.908
P(M - ln n <= -1) : simulé 0.0650 | Gumbel exp(-exp(-x)) = 0.0660
P(M - ln n <=  0) : simulé 0.3685 | Gumbel exp(-exp(-x)) = 0.3679
P(M - ln n <=  1) : simulé 0.6922 | Gumbel exp(-exp(-x)) = 0.6922
P(M - ln n <=  2) : simulé 0.8711 | Gumbel exp(-exp(-x)) = 0.8734
P(M - ln n <=  3) : simulé 0.9496 | Gumbel exp(-exp(-x)) = 0.9514
test de Kolmogorov-Smirnov contre la loi de Gumbel : statistique 0.0044
```

La loi de Gumbel colle presque parfaitement. Pour un **autre type de queue**, le résultat est différent : le maximum de variables à queue lourde (loi de Pareto) converge vers une loi de Fréchet, de $\xi>0$. Le type de la loi limite est dicté par la **queue** de la loi d'origine : c'est précisément pourquoi on peut modéliser un maximum sans connaître la loi des observations.

### 6.5.3 Les données : des retards de livraison simulés, à queue lourde

Pour que nous puissions **comparer à la vérité**, nous simulons un jeu de données de colis (il s'agit bien d'une **simulation**, de graine 671 ; ce ne sont pas des données réelles de Dar Jasmin). Dix ans (2016-2025) de livraisons : environ 3 colis par jour en moyenne (loi de Poisson), chacun avec une durée de livraison en jours qui suit une loi de **Pareto généralisée** décalée de 1 jour (la durée minimale) :
$$P(\text{durée}>x)=\Bigl(1+\xi\,\frac{x-1}{\sigma}\Bigr)^{-1/\xi},\qquad x\ge1,$$
avec $\xi=0{,}25$ (queue lourde modérée : la variance est finie, mais pas le moment d'ordre 4) et $\sigma=1{,}5$ jour. Nous garderons ces valeurs **cachées** de nos calculs : nous les utiliserons à la fin pour juger les estimations.

```python
rng = np.random.default_rng(671)
XI0, SIGMA0, COLIS_PAR_JOUR, JOURS = 0.25, 1.5, 3.0, 3652
n_j = rng.poisson(COLIS_PAR_JOUR, JOURS)
n_tot = n_j.sum()
u = rng.random(n_tot)
duree = 1 + SIGMA0 / XI0 * (u ** (-XI0) - 1)                      # inversion de la fonction de survie (6.2.4)
date = pd.Timestamp("2016-01-01") + pd.to_timedelta(np.repeat(np.arange(JOURS), n_j), unit="D")
colis = pd.DataFrame({"date": date, "duree": duree})

print(f"{n_tot} colis sur {JOURS} jours ({n_tot / JOURS:.2f} par jour en moyenne)")
print(colis["duree"].describe().round(2).to_string())
print(f"proportion de colis livrés en plus de 5 jours : {(duree > 5).mean():.3%}   en plus de 10 jours : {(duree > 10).mean():.3%}   en plus de 20 jours : {(duree > 20).mean():.3%}")
```
<!--sortie-->
```text
10981 colis sur 3652 jours (3.01 par jour en moyenne)
count    10981.00
mean         3.04
std          2.89
min          1.00
25%          1.46
50%          2.14
75%          3.53
max         56.32
proportion de colis livrés en plus de 5 jours : 13.114%   en plus de 10 jours : 2.723%   en plus de 20 jours : 0.373%
```

La médiane est d'environ 2 jours, mais la queue est longue : 13 % des colis dépassent 5 jours, 2,7 % dépassent 10 jours, et 0,37 % (environ un colis sur 270) dépassent 20 jours. Le plus long retard de la décennie est de 56 jours. Voyons comment la forme de cette queue se lit dans les données, puis comment extrapoler.

### 6.5.4 Première approche : les maxima par blocs

On découpe les dix ans en **blocs** (ici : les mois) et on garde le **plus long retard de chaque mois**, ce qui donne 120 maxima. D'après le théorème de la section 6.5.2, ces maxima suivent approximativement une loi GEV, dont on estime les paramètres par **maximum de vraisemblance** (volume I, section 3.2). (Attention : `scipy` paramètre la GEV par $c=-\xi$, signe opposé à la convention de ce livre.)

```python
maxima_m = colis.groupby(colis["date"].dt.to_period("M"))["duree"].max().to_numpy()
print(f"{len(maxima_m)} maxima mensuels : min {maxima_m.min():.2f}, médiane {np.median(maxima_m):.2f}, max {maxima_m.max():.2f} jours")

c_hat, mu_hat, sig_hat = stats.genextreme.fit(maxima_m)
xi_hat = -c_hat
print(f"GEV ajustée par maximum de vraisemblance : mu = {mu_hat:.3f}, sigma = {sig_hat:.3f}, xi = {xi_hat:.3f}")

# Incertitude : bootstrap (on rééchantillonne les 120 maxima, on réajuste)
rng = np.random.default_rng(672)
boot = np.array([stats.genextreme.fit(rng.choice(maxima_m, len(maxima_m))) for _ in range(300)])
xi_boot = -boot[:, 0]
print(f"xi : IC95 bootstrap [{np.percentile(xi_boot, 2.5):.3f} ; {np.percentile(xi_boot, 97.5):.3f}]  (écart-type {xi_boot.std():.3f})")
```
<!--sortie-->
```text
120 maxima mensuels : min 7.68, médiane 15.54, max 56.32 jours
GEV ajustée par maximum de vraisemblance : mu = 13.741, sigma = 4.772, xi = 0.324
xi : IC95 bootstrap [0.213 ; 0.459]  (écart-type 0.066)
```

L'estimation de $\xi$ est positive, ce qui indique une queue lourde, mais son **intervalle d'incertitude est large** : avec seulement 120 maxima, la forme de la queue est difficile à préciser. C'est la caractéristique majeure de la théorie des extrêmes : **on dispose de très peu de données par construction** (les extrêmes sont rares), et donc l'incertitude est grande.

**Les niveaux de retour.** La quantité que Yasmine veut vraiment est le **niveau de retour** $z_T$ : la valeur dépassée en moyenne **une fois toutes les $T$ périodes** (ici, $T$ mois). Autrement dit, la valeur telle que $P(\text{max mensuel}>z_T)=1/T$, soit $G(z_T)=1-1/T$. En résolvant l'équation avec la forme de la GEV, on trouve
$$z_T=\mu-\frac\sigma\xi\Bigl[1-\bigl(-\ln(1-1/T)\bigr)^{-\xi}\Bigr].$$
(*Démonstration* : $G(z)=1-1/T\iff\bigl[1+\xi\frac{z-\mu}\sigma\bigr]^{-1/\xi}=-\ln(1-1/T)$, car $\exp(-y)=1-1/T\iff y=-\ln(1-1/T)$ ; on élève à la puissance $-\xi$ et on isole $z$.) Un niveau de retour à **10 ans**, c'est $T=120$ mois ; à **100 ans**, $T=1\,200$ mois.

Pour montrer le danger de la loi normale, nous comparons trois estimations : (i) la GEV ajustée ; (ii) une loi **normale** ajustée aux mêmes 120 maxima ; (iii) la **vérité** (calculable car nous connaissons le générateur : le maximum mensuel d'un nombre de colis de moyenne $\lambda_m=3\times30{,}4375$ suit exactement une GEV de paramètres $\xi=\xi_0$, $\sigma=\sigma_0\lambda_m^{\xi_0}$, $\mu=1+\sigma_0(\lambda_m^{\xi_0}-1)/\xi_0$).

```python
lam_m = COLIS_PAR_JOUR * 30.4375                                   # colis par mois, en moyenne
sig_vrai = SIGMA0 * lam_m ** XI0
mu_vrai = 1 + SIGMA0 * (lam_m ** XI0 - 1) / XI0
print(f"vérité : GEV(mu = {mu_vrai:.3f}, sigma = {sig_vrai:.3f}, xi = {XI0})")

def niveau_gev(T, mu, sigma, xi):
    return mu - sigma / xi * (1 - (-np.log(1 - 1 / T)) ** (-xi))

m_norm, s_norm = maxima_m.mean(), maxima_m.std(ddof=1)
lignes = []
for T, nom in ((12, "1 an"), (120, "10 ans"), (1200, "100 ans")):
    ni_boot = np.array([niveau_gev(T, b[1], b[2], -b[0]) for b in boot])
    lignes.append({"retour": nom, "vérité": round(niveau_gev(T, mu_vrai, sig_vrai, XI0), 1),
                   "GEV ajustée": round(niveau_gev(T, mu_hat, sig_hat, xi_hat), 1),
                   "IC95 bootstrap GEV": f"[{np.percentile(ni_boot, 2.5):.0f} ; {np.percentile(ni_boot, 97.5):.0f}]",
                   "loi normale ajustée": round(stats.norm.ppf(1 - 1 / T, m_norm, s_norm), 1)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
vérité : GEV(mu = 13.547, sigma = 4.637, xi = 0.25)
 retour  vérité  GEV ajustée IC95 bootstrap GEV  loi normale ajustée
   1 an    29.1         31.5          [27 ; 37]                 31.5
 10 ans    56.3         68.5         [51 ; 101]                 41.1
100 ans   104.2        145.8         [89 ; 289]                 48.2
```

Le tableau livre le message central. À 1 an, les deux ajustements donnent la même valeur (31,5 jours, pour une vérité de 29,1) : on est **dans** le domaine des données. Mais à 10 ans puis à 100 ans, **la loi normale s'effondre** : elle prédit 41 puis 48 jours, quand la vérité est de 56 puis 104 jours. Elle se trompe de plus de moitié à 100 ans, et dans le sens **rassurant**. La GEV, elle, se trompe plutôt par excès : 68 jours à 10 ans (vérité 56) et 146 à 100 ans (vérité 104), parce que son $\hat\xi=0{,}32$ est un peu supérieur au vrai $0{,}25$ (une petite erreur sur $\xi$ est amplifiée par l'extrapolation). Mais **son intervalle de confiance contient la vérité** ([51 ; 101] à 10 ans, [89 ; 289] à 100 ans), et il est **très large** à 100 ans : c'est honnête, car on extrapole dix fois au-delà de la durée des données. Retenons : la loi normale ne produit pas seulement des erreurs, elle produit des erreurs **rassurantes** et **sans avertissement** (elle n'a pas d'intervalle qui s'élargisse).

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.facecolor": "#fcfcfb",
                     "figure.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
                     "legend.frameon": False, "font.size": 10})

n_m = len(maxima_m)
tri = np.sort(maxima_m)
T_emp = (n_m + 1) / (n_m + 1 - np.arange(1, n_m + 1))                 # période de retour empirique (positions de Weibull)
Tg = np.logspace(np.log10(1.2), np.log10(3000), 200)

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10.5, 4.2), gridspec_kw={"width_ratios": [1.25, 1]})
ax1.semilogx(Tg, niveau_gev(Tg, mu_vrai, sig_vrai, XI0), color="#0b0b0b", lw=1.4, ls="--")
ax1.semilogx(Tg, niveau_gev(Tg, mu_hat, sig_hat, xi_hat), color=BLEU, lw=2.0)
ax1.semilogx(Tg, stats.norm.ppf(1 - 1 / Tg, m_norm, s_norm), color=ORANGE, lw=2.0)
ax1.semilogx(T_emp, tri, "o", color="#52514e", ms=3.5)
ax1.axvline(120, color="#898781", lw=0.8, ls=":")
ax1.text(125, 5, "10 ans", color="#52514e", fontsize=9)
ax1.text(1.3, 66, "GEV ajustée", color=BLEU, fontsize=10)
ax1.text(1.3, 60, "loi normale ajustée", color=ORANGE, fontsize=10)
ax1.text(1.3, 54, "vérité (tirets)", color="#0b0b0b", fontsize=10)
ax1.text(1.3, 48, "points : maxima observés", color="#52514e", fontsize=9)
ax1.set_xlabel("période de retour (en mois, échelle logarithmique)")
ax1.set_ylabel("retard maximal (jours)")
ax1.set_title("Niveaux de retour")
ax1.set_ylim(0, 70)

# Panneau de droite : fonction d'excès moyen (choix du seuil, voir 6.5.5)
x_all = colis["duree"].to_numpy()
seuils = np.quantile(x_all, np.linspace(0.70, 0.995, 60))
exces_moy = np.array([x_all[x_all > s_].mean() - s_ for s_ in seuils])
ax2.plot(seuils, exces_moy, color=BLEU, lw=1.8)
ax2.set_xlabel("seuil $u$ (jours)")
ax2.set_ylabel("excès moyen au-dessus de $u$ (jours)")
ax2.set_title("Excès moyen : quasi linéaire si la queue est GPD")
plt.tight_layout()
plt.savefig("figures/ch06-extremes-retour.png", dpi=200, bbox_inches="tight")
plt.close()
```

![À gauche : niveaux de retour estimés à partir des 120 maxima mensuels de retards de livraison (simulés). La loi normale ajustée (orange) sous-estime fortement les niveaux de retour, alors que la GEV (bleue) reste du bon ordre de grandeur, avec une légère tendance à surestimer, et à intervalle de confiance qui contient la vérité (tirets noirs). À droite : l'excès moyen des retards au-dessus d'un seuil, en fonction du seuil ; une relation à peu près linéaire indique une queue de type GPD.](figures/ch06-extremes-retour.png)

### 6.5.5 Seconde approche : les excès au-dessus d'un seuil (POT)

Garder un seul maximum par mois, c'est **jeter** beaucoup d'information : le deuxième plus long retard d'un mois est peut-être supérieur au maximum d'un autre mois. L'approche **POT** (*peaks over threshold*) exploite **toutes les valeurs qui dépassent un seuil élevé $u$**.

> 📐 **Théorème de Pickands-Balkema-de Haan (admis).** Pour un seuil $u$ assez élevé, la loi des **excès** $X-u$ sachant $X>u$ est approximativement une loi de **Pareto généralisée** (GPD) :
> $$P(X-u>y\mid X>u)\approx\Bigl(1+\xi\,\frac y{\sigma_u}\Bigr)^{-1/\xi},\qquad y>0,$$
> **avec le même indice $\xi$ que la GEV des maxima** (le paramètre d'échelle $\sigma_u$ dépend du seuil).

Un seuil trop bas rend l'approximation GPD fausse (biais) ; un seuil trop haut laisse trop peu de points (variance). C'est le compromis habituel. Deux outils guident le choix :

- le **graphique de l'excès moyen** (*mean residual life plot*, panneau de droite ci-dessus) : pour une GPD, l'excès moyen au-dessus de $u$ vaut $\dfrac{\sigma_u}{1-\xi}$ et croît **linéairement** avec $u$. On choisit le plus petit seuil à partir duquel la courbe est à peu près une droite ;
- la **stabilité de $\hat\xi$** : on estime $\xi$ pour plusieurs seuils ; au-delà du bon seuil, l'estimation doit se stabiliser.

```python
def ajuste_gpd(x, seuil):
    exces = x[x > seuil] - seuil
    xi_, loc_, sc_ = stats.genpareto.fit(exces, floc=0)             # on fixe loc = 0 : les excès sont comptés depuis le seuil
    return xi_, sc_, len(exces)

lignes = []
for q in (0.80, 0.90, 0.93, 0.95, 0.97, 0.98):
    u_ = np.quantile(x_all, q)
    xi_, sc_, k_ = ajuste_gpd(x_all, u_)
    lignes.append({"quantile du seuil": q, "seuil u (jours)": round(u_, 2), "excès": k_, "xi estimé": round(xi_, 3), "sigma_u estimé": round(sc_, 3)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 quantile du seuil  seuil u (jours)  excès  xi estimé  sigma_u estimé
              0.80             4.02   2196      0.273           2.237
              0.90             5.69   1098      0.252           2.795
              0.93             6.76    769      0.265           2.990
              0.95             7.73    549      0.239           3.440
              0.97             9.62    330      0.301           3.550
              0.98            11.16    220      0.289           4.073
```

L'estimation de $\xi$ reste entre 0,24 et 0,30 pour tous les seuils raisonnables (la vraie valeur est 0,25) : le choix d'un seuil au 95ᵉ centile, qui laisse environ 550 excès, est un bon compromis. Passons maintenant à l'estimation du niveau de retour. Si $\zeta_u=P(X>u)$ est la probabilité d'un dépassement du seuil, la loi de $X$ au-dessus de $u$ s'écrit $P(X>x)=\zeta_u\bigl(1+\xi(x-u)/\sigma_u\bigr)^{-1/\xi}$. Le niveau $x_m$ dépassé **en moyenne une fois tous les $m$ colis** vérifie $P(X>x_m)=1/m$, d'où
$$x_m=u+\frac{\sigma_u}{\xi}\Bigl[(m\,\zeta_u)^{\xi}-1\Bigr].$$
Une période de retour de 10 ans correspond à $m=$ nombre de colis en 10 ans (environ 11 000), de 100 ans à dix fois plus.

```python
u_ = np.quantile(x_all, 0.95)
xi_p, sc_p, k_p = ajuste_gpd(x_all, u_)
zeta = (x_all > u_).mean()

def niveau_pot(m, xi_, sc_, u_, zeta_):
    return u_ + sc_ / xi_ * ((m * zeta_) ** xi_ - 1)

# Incertitude : bootstrap sur les colis (on rééchantillonne l'ensemble des colis, on refait l'ajustement)
rng = np.random.default_rng(673)
boot_pot = []
for _ in range(300):
    xb = rng.choice(x_all, len(x_all))
    ub = np.quantile(xb, 0.95)
    xib, scb, _ = ajuste_gpd(xb, ub)
    boot_pot.append((xib, scb, ub, (xb > ub).mean()))
boot_pot = np.array(boot_pot)

print(f"POT : seuil u = {u_:.2f} j ({k_p} excès, {zeta:.3f} des colis) ; GPD : xi = {xi_p:.3f}, sigma_u = {sc_p:.3f}")
print(f"xi : IC95 bootstrap [{np.percentile(boot_pot[:, 0], 2.5):.3f} ; {np.percentile(boot_pot[:, 0], 97.5):.3f}]  (GEV par blocs : [{np.percentile(xi_boot, 2.5):.3f} ; {np.percentile(xi_boot, 97.5):.3f}])")

def niveau_vrai_colis(m):
    return 1 + SIGMA0 / XI0 * (m ** XI0 - 1)                       # S(x) = 1/m pour la vraie GPD décalée

lignes = []
for ans, nom in ((1, "1 an"), (10, "10 ans"), (100, "100 ans")):
    m = n_tot * ans / 10.0                                         # nombre de colis dans la période de retour
    lv = np.array([niveau_pot(m, b[0], b[1], b[2], b[3]) for b in boot_pot])
    lignes.append({"retour": nom, "vérité": round(niveau_vrai_colis(m), 1), "POT (GPD)": round(niveau_pot(m, xi_p, sc_p, u_, zeta), 1),
                   "IC95 bootstrap POT": f"[{np.percentile(lv, 2.5):.0f} ; {np.percentile(lv, 97.5):.0f}]"})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
POT : seuil u = 7.73 j (549 excès, 0.050 des colis) ; GPD : xi = 0.239, sigma_u = 3.440
xi : IC95 bootstrap [0.148 ; 0.330]  (GEV par blocs : [0.213 ; 0.459])
 retour  vérité  POT (GPD) IC95 bootstrap POT
   1 an    29.5       30.8          [27 ; 35]
 10 ans    56.4       58.3          [45 ; 73]
100 ans   104.2      105.9         [71 ; 159]
```

La méthode POT donne des estimations très proches de la vérité (58 jours à 10 ans pour une vérité de 56 ; 106 à 100 ans pour 104) et des intervalles d'incertitude **plus étroits** que ceux des maxima par blocs (à 100 ans : [71 ; 159] contre [89 ; 289]), parce qu'elle utilise 549 valeurs au lieu de 120. L'intervalle de $\xi$ est aussi plus étroit ([0,15 ; 0,33] contre [0,21 ; 0,46]). Une remarque sur les deux colonnes « vérité » : elles diffèrent à peine (56,3 contre 56,4 à 10 ans), car elles mesurent deux choses voisines : l'une, le *maximum mensuel* dépassé une fois tous les 120 mois ; l'autre, le *colis individuel* dépassé une fois tous les 11 000 colis environ. Pour un grand nombre de colis, ces deux notions sont presque identiques.

> ⚠️ **Les pièges de l'extrapolation.**
> 1. **Le seuil** : toujours examiner la sensibilité à son choix. Une conclusion qui change radicalement avec le seuil n'est pas fiable.
> 2. **L'indépendance** : les théorèmes supposent des observations (à peu près) indépendantes. Des extrêmes **regroupés** (une tempête qui donne dix journées d'extrêmes consécutives) doivent être « dégroupés » : on ne garde que le plus grand de chaque grappe.
> 3. **La stationnarité** : si la loi change avec le temps (saison, tendance), les niveaux de retour d'hier ne valent plus pour demain. On peut faire dépendre $\mu$ ou $\sigma$ du temps (tendance, covariables).
> 4. **L'extrapolation reste une extrapolation** : un niveau de retour à 100 ans estimé sur 10 ans de données est une **projection**, avec une incertitude énorme. L'intervalle, bien plus que l'estimation ponctuelle, est le résultat à communiquer.
> 5. **Les moments** : pour $\xi\ge1/2$ la variance est infinie ; pour $\xi\ge1$ la moyenne l'est. Les résumés habituels deviennent alors trompeurs, et « la moyenne des retards » n'a plus de sens statistique stable.

> 💡 **Lien avec le bayésien.** Quand les données sont rares, les extrêmes se prêtent très bien à l'approche bayésienne : un a priori informatif sur $\xi$ (« les queues de retards logistiques ont typiquement $0<\xi<0{,}5$ ») stabilise l'estimation, et le Monte-Carlo (6.2) fournit directement une **loi a posteriori des niveaux de retour**. C'est l'approche standard en hydrologie.

> ✅ **À retenir (6.5).**
> - Les décisions de **risque** dépendent de la **queue** de la distribution, et la loi normale en donne une image **dangereusement optimiste**.
> - **Théorème de Fisher-Tippett-Gnedenko** : le maximum de $n$ observations (normalisé) suit une loi **GEV**, de paramètres position $\mu$, échelle $\sigma$ et forme $\xi$ ; $\xi>0$ signale une queue lourde.
> - **Deux approches** : maxima par blocs (GEV) ou excès au-dessus d'un seuil (**POT**, loi de Pareto généralisée). POT utilise davantage de données ; il demande de choisir un seuil.
> - Le **niveau de retour** $z_T$ est la valeur dépassée en moyenne une fois toutes les $T$ périodes ; on l'estime par une formule explicite dans les paramètres.
> - **L'incertitude est grande par construction** : toujours donner un intervalle (bootstrap, vraisemblance profilée, ou a posteriori bayésien).


## 6.6 ➕ Pour aller plus loin : les copules et la modélisation de la dépendance

> 🧭 **Section optionnelle.** Elle suppose les lois jointes et la corrélation (volume I, chapitre 2), la simulation par inversion (6.2.4) et, pour la fin, l'estimation par maximum de vraisemblance. Elle ne dépend pas des sections 6.3 à 6.5.

> 💡 **Intuition.** Deux transporteurs livrent les colis de Dar Jasmin. Chacun a ses propres retards, parfois très longs. Mais le vrai risque pour Yasmine n'est pas qu'*un* transporteur ait un mauvais jour : c'est que **les deux aient un très mauvais jour en même temps** (un jour de grève, de tempête, de veille de fête), car alors elle n'a plus de solution de repli. Ce risque ne dépend pas seulement de la loi de chaque transporteur (les « lois marginales »), mais de la façon dont ils sont **liés** : de la **structure de dépendance**. La corrélation ne la résume pas : deux paires de variables peuvent avoir la même corrélation et des comportements extrêmes opposés. Une **copule** isole cette structure de dépendance, séparément des marginales, et permet de la modéliser.

### 6.6.1 La corrélation ne dit pas tout

Rappelons (volume I, section 3.1.7) que le coefficient de corrélation de Pearson ne mesure que la dépendance **linéaire**, et qu'il est sensible aux marginales. On lui préfère souvent des mesures **de rang**, qui ne changent pas quand on applique une transformation croissante à l'une des variables :

- le **tau de Kendall** $\tau$ : la probabilité que deux observations soient « concordantes » (l'une est plus grande dans les deux variables) moins la probabilité qu'elles soient « discordantes » ;
- le **rho de Spearman** : la corrélation de Pearson des **rangs**.

*Exemple à la main.* Quatre clients, avec (panier, nombre de commandes) = $(10,1),(20,3),(30,2),(40,4)$. Il y a $\binom42=6$ paires. Paires concordantes (les deux variables vont dans le même sens) : $\{1,2\},\{1,3\},\{1,4\},\{2,4\},\{3,4\}$ : 5. Paire discordante : $\{2,3\}$ (le panier monte de 20 à 30 mais les commandes passent de 3 à 2) : 1. Donc $\tau=(5-1)/6=0{,}667$.

```python
import numpy as np
import pandas as pd
from scipy import stats

panier = [10, 20, 30, 40]
nb = [1, 3, 2, 4]
print("tau de Kendall :", round(stats.kendalltau(panier, nb).statistic, 4), "(à la main : 4/6 =", round(4 / 6, 4), ")")
print("rho de Spearman :", round(stats.spearmanr(panier, nb).statistic, 4))
# invariance par transformation croissante : on passe au logarithme et au carré
print("tau après log et carré :", round(stats.kendalltau(np.log(panier), np.square(nb)).statistic, 4), "(inchangé)")
print("Pearson avant :", round(np.corrcoef(panier, nb)[0, 1], 4), "| après :", round(np.corrcoef(np.log(panier), np.square(nb))[0, 1], 4), "(change)")
```
<!--sortie-->
```text
tau de Kendall : 0.6667 (à la main : 4/6 = 0.6667 )
rho de Spearman : 0.8
tau après log et carré : 0.6667 (inchangé)
Pearson avant : 0.8 | après : 0.7592 (change)
```

Le tau de Kendall est inchangé par toute transformation croissante des variables ; la corrélation de Pearson, elle, change. **Ce qui ne bouge pas quand on transforme les marginales, c'est précisément la structure de dépendance.** La copule est l'objet mathématique qui la capture.

### 6.6.2 Le théorème de Sklar

> 📐 **Le principe : la transformation intégrale de probabilité.** Si $X$ a une fonction de répartition $F$ continue, alors $U=F(X)$ suit la loi uniforme sur $[0,1]$.
>
> *Démonstration.* Pour $u\in[0,1]$, $P(F(X)\le u)=P(X\le F^{-1}(u))=F(F^{-1}(u))=u$. C'est la réciproque du théorème d'inversion de 6.2.4. $\square$

Passer de $X$ à $U=F(X)$ efface la marginale (toute variable continue devient uniforme) mais **garde le rang**, donc la dépendance.

> 📐 **Définition.** Une **copule** est la fonction de répartition jointe d'un couple $(U,V)$ dont les deux marginales sont uniformes sur $[0,1]$ : $C(u,v)=P(U\le u,\,V\le v)$.
>
> **Théorème de Sklar.** Pour tout couple $(X,Y)$ de fonction de répartition jointe $H$ et de marginales $F,G$, il existe une copule $C$ telle que
> $$H(x,y)=C\bigl(F(x),\,G(y)\bigr),$$
> unique si $F$ et $G$ sont continues. Réciproquement, toute copule $C$ combinée à des marginales $F,G$ quelconques définit une loi jointe.

Le théorème sépare l'énoncé « loi jointe » en deux : **(1) les marginales** (le comportement de chaque variable seule) et **(2) la copule** (la dépendance). On peut modéliser l'une et l'autre **séparément**, puis les assembler. C'est ce qui rend l'outil si commode : on choisit une marginale réaliste pour chaque variable (par exemple, une loi de Pareto généralisée pour des retards, comme en 6.5) et une copule pour les relier.

**Trois copules extrêmes (bornes de Fréchet).** *Indépendance* : $C(u,v)=uv$. *Dépendance parfaite positive* (comonotonie : $V=U$) : $C(u,v)=\min(u,v)$. *Dépendance parfaite négative* ($V=1-U$) : $C(u,v)=\max(u+v-1,\,0)$. Toute copule est coincée entre les deux dernières : $\max(u+v-1,0)\le C(u,v)\le\min(u,v)$.

### 6.6.3 La copule gaussienne

Idée : prendre le couple normal bivarié, **effacer ses marginales normales** (en les transformant en uniformes), **garder sa dépendance**. Soient $(Z_1,Z_2)$ normaux standard de corrélation $\rho$ et $\Phi$ la fonction de répartition de $\mathcal N(0,1)$. Alors $(U,V)=(\Phi(Z_1),\Phi(Z_2))$ a des marginales uniformes ; sa fonction de répartition est la **copule gaussienne**
$$C_\rho(u,v)=\Phi_2\bigl(\Phi^{-1}(u),\Phi^{-1}(v);\,\rho\bigr).$$
Pour simuler un couple $(X,Y)$ de marginales $F$ et $G$ et de dépendance gaussienne : tirer $(Z_1,Z_2)$, poser $U_i=\Phi(Z_i)$, puis $X=F^{-1}(U_1)$ et $Y=G^{-1}(U_2)$ (**inversion**, 6.2.4). Le tau de Kendall d'une copule gaussienne vaut
$$\tau=\frac2\pi\arcsin\rho\qquad\Longleftrightarrow\qquad\rho=\sin\!\left(\frac{\pi\tau}2\right)\quad(\text{formule admise}).$$

La copule gaussienne est simple et très utilisée, mais elle a un défaut majeur : elle n'a **aucune dépendance de queue**. Quand $\rho<1$, la probabilité que les deux variables soient *simultanément* extrêmes devient négligeable plus vite que ne le ferait une vraie dépendance. En deux mots : un modèle gaussien suppose que « quand ça va très mal, ça va très mal *séparément* ».

### 6.6.4 La copule de Clayton : la dépendance dans les queues

La **copule de Clayton** de paramètre $\theta>0$ est
$$C_\theta(u,v)=\bigl(u^{-\theta}+v^{-\theta}-1\bigr)^{-1/\theta}.$$
Elle vérifie $\tau=\dfrac{\theta}{\theta+2}$ (formule admise) : $\theta\to0$ donne l'indépendance, $\theta\to\infty$ la dépendance parfaite. Sa particularité est la **dépendance de queue inférieure** : $\lambda_L=\lim_{q\to0}P(V\le q\mid U\le q)=2^{-1/\theta}>0$. Quand l'une des variables est très petite, l'autre l'est aussi avec une probabilité non négligeable, même à l'extrême.

> 📐 **Comment la simuler ? L'algorithme de Marshall-Olkin.** Soit $V\sim\mathrm{Gamma}(1/\theta,\,\text{taux }1)$ et $E_1,E_2\sim\mathrm{Exp}(1)$ indépendantes de $V$ et entre elles. Alors
> $$U_i=\Bigl(1+\frac{E_i}{V}\Bigr)^{-1/\theta},\quad i=1,2,$$
> est un couple de loi de Clayton.
>
> *Démonstration.* Posons $\psi(t)=(1+t)^{-1/\theta}$. C'est la transformée de Laplace de la loi $\mathrm{Gamma}(1/\theta,1)$ : $\mathbb E[e^{-tV}]=\psi(t)$. Son inverse est $\psi^{-1}(u)=u^{-\theta}-1$. On a $U_i=\psi(E_i/V)$ et $\psi$ est décroissante, donc $U_i\le u\iff E_i\ge V\,\psi^{-1}(u)$, d'où, **sachant $V$**, $P(U_i\le u\mid V)=\exp(-V\psi^{-1}(u))$. Les $E_i$ étant indépendantes sachant $V$,
> $$P(U_1\le u_1,U_2\le u_2)=\mathbb E\Bigl[e^{-V\psi^{-1}(u_1)}\,e^{-V\psi^{-1}(u_2)}\Bigr]=\psi\bigl(\psi^{-1}(u_1)+\psi^{-1}(u_2)\bigr)=\bigl(u_1^{-\theta}+u_2^{-\theta}-1\bigr)^{-1/\theta}.\ \square$$
> (Le facteur $V$ est un « facteur commun » : quand $V$ est petit, les deux $U_i$ sont petits **ensemble**. C'est exactement l'idée d'un événement qui touche les deux transporteurs à la fois.)

Pour obtenir une dépendance dans la queue **supérieure** (les deux variables sont grandes ensemble), on **retourne** la copule : si $(U,V)$ suit Clayton, alors $(1-U,\,1-V)$ suit la **copule de Clayton retournée** (ou « de survie »), de dépendance de queue supérieure $\lambda_U=2^{-1/\theta}$.

### 6.6.5 Deux copules, même tau, comportements extrêmes opposés

Fixons $\tau=0{,}5$ (une dépendance modérément forte). Alors $\rho=\sin(\pi/4)=0{,}7071$ pour la copule gaussienne et $\theta=2\tau/(1-\tau)=2$ pour Clayton. Nous simulons 200 000 couples de chacune, et nous comparons à la formule exacte la probabilité que les deux variables soient simultanément parmi les 1 %, 5 % ou 10 % **les plus petites**.

```python
from scipy.stats import norm, kendalltau, multivariate_normal

def sim_gauss(rho, n, rng):
    z = rng.multivariate_normal([0, 0], [[1, rho], [rho, 1]], n)
    return norm.cdf(z)

def sim_clayton(theta, n, rng):
    v = rng.gamma(1 / theta, 1.0, n)                      # facteur commun
    e = rng.exponential(size=(n, 2))
    return (1 + e / v[:, None]) ** (-1 / theta)

tau = 0.5
rho = np.sin(np.pi * tau / 2)
theta = 2 * tau / (1 - tau)
rng = np.random.default_rng(680)
n = 200_000
ug, uc = sim_gauss(rho, n, rng), sim_clayton(theta, n, rng)
print(f"rho = {rho:.4f}, theta = {theta:.1f}")
print(f"tau de Kendall simulé (sur 5 000 points) : gaussienne {kendalltau(ug[:5000, 0], ug[:5000, 1]).statistic:.3f} | Clayton {kendalltau(uc[:5000, 0], uc[:5000, 1]).statistic:.3f}")

lignes = []
for q in (0.10, 0.05, 0.01):
    z = norm.ppf(q)
    exact_g = multivariate_normal([0, 0], [[1, rho], [rho, 1]]).cdf([z, z])         # C_rho(q, q)
    exact_c = (2 * q ** (-theta) - 1) ** (-1 / theta)                                # C_theta(q, q)
    lignes.append({"q": q, "indépendance q²": f"{q**2:.5f}",
                   "gaussienne : exact": f"{exact_g:.5f}", "gaussienne : simulé": f"{np.mean((ug < q).all(axis=1)):.5f}",
                   "Clayton : exact": f"{exact_c:.5f}", "Clayton : simulé": f"{np.mean((uc < q).all(axis=1)):.5f}",
                   "Clayton / gaussienne": round(exact_c / exact_g, 2)})
print(pd.DataFrame(lignes).to_string(index=False))
print(f"\ndépendance de queue : lambda_L de Clayton = 2^(-1/theta) = {2 ** (-1 / theta):.3f} ; celle de la gaussienne = 0")
```
<!--sortie-->
```text
rho = 0.7071, theta = 2.0
tau de Kendall simulé (sur 5 000 points) : gaussienne 0.500 | Clayton 0.506
   q indépendance q² gaussienne : exact gaussienne : simulé Clayton : exact Clayton : simulé  Clayton / gaussienne
0.10         0.01000            0.04739             0.04682         0.07089          0.07184                  1.50
0.05         0.00250            0.01992             0.01959         0.03538          0.03565                  1.78
0.01         0.00010            0.00273             0.00281         0.00707          0.00681                  2.59

dépendance de queue : lambda_L de Clayton = 2^(-1/theta) = 0.707 ; celle de la gaussienne = 0
```

Les formules exactes et les simulations s'accordent. Lecture : avec le **même tau** de 0,5, la probabilité que les deux variables soient *simultanément* parmi les 1 % les plus petites est de 0,71 % avec Clayton contre 0,27 % avec la gaussienne, soit **2,6 fois plus** (dernière colonne), et le rapport **augmente à mesure que l'événement devient plus rare** (1,5 à 10 %, 1,8 à 5 %, 2,6 à 1 %). Pour référence, sous indépendance, cette probabilité serait de 0,01 %. Voici le dessin des deux nuages de points : même dépendance « moyenne », des queues très différentes.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False, "axes.grid": True,
                     "grid.color": "#e1e0d9", "grid.linewidth": 0.6, "axes.facecolor": "#fcfcfb",
                     "figure.facecolor": "#fcfcfb", "savefig.facecolor": "#fcfcfb",
                     "legend.frameon": False, "font.size": 10})

fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.6))
for ax, u_, titre, coul in zip(axes, (ug[:2500], uc[:2500]), ("copule gaussienne ($\\rho=0{,}71$)", "copule de Clayton ($\\theta=2$)"), (BLEU, ORANGE)):
    ax.scatter(u_[:, 0], u_[:, 1], s=5, color=coul, alpha=0.55)
    coin = (u_ < 0.05).all(axis=1)
    ax.scatter(u_[coin, 0], u_[coin, 1], s=11, color=ROUGE)
    ax.plot([0.05, 0.05, 0], [0, 0.05, 0.05], color=ROUGE, lw=0.8)
    ax.set_title(f"{titre}\n{coin.sum()} points dans le coin inférieur (rouge)", fontsize=10)
    ax.set_xlabel("$U$ (rang de la première variable)")
    ax.set_aspect("equal")
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.grid(False)
axes[0].set_ylabel("$V$ (rang de la seconde)")
plt.tight_layout()
plt.savefig("figures/ch06-copules-gauss-clayton.png", dpi=200, bbox_inches="tight")
plt.close()
```

![Deux copules de même tau de Kendall (0,5), 2 500 points chacune, dans l'échelle des rangs. À gauche : la copule gaussienne. À droite : la copule de Clayton, dont les points se concentrent dans le coin inférieur gauche (les deux variables très petites ensemble). Les points rouges sont ceux dont les deux coordonnées sont inférieures à 5 %.](figures/ch06-copules-gauss-clayton.png)

> ⚠️ **L'enseignement de la crise de 2008.** Avant 2008, de nombreux produits financiers (les « CDO ») évaluaient le risque de défaut simultané de nombreux emprunteurs avec une **copule gaussienne**, calibrée sur des corrélations. En période de crise, les défauts se sont produits **ensemble** (dépendance de queue) bien plus souvent que le modèle ne le prévoyait. Le choix de la copule n'est pas un détail technique : c'est une hypothèse sur la dépendance **dans les extrêmes**, précisément là où les données sont les plus rares.

### 6.6.6 Estimer une copule à partir de données

Procédure standard (« semi-paramétrique ») : 

1. transformer chaque variable en **pseudo-observations** $\hat U_i=\mathrm{rang}(X_i)/(n+1)$ (une estimation de $F(X_i)$ par le rang, qui efface la marginale sans la modéliser) ;
2. estimer le paramètre de la copule, soit par **inversion du tau de Kendall** (calculer $\hat\tau$ puis résoudre $\tau(\theta)=\hat\tau$ : $\hat\rho=\sin(\pi\hat\tau/2)$, $\hat\theta=2\hat\tau/(1-\hat\tau)$), soit par **maximum de vraisemblance** sur les pseudo-observations ;
3. **choisir** entre familles par la vraisemblance (comme en 1.4 : l'AIC compte les paramètres ; ici une famille à un paramètre contre une autre à un paramètre : la comparaison directe des log-vraisemblances suffit).

La vraisemblance fait appel à la **densité de copule** $c(u,v)=\partial^2C/\partial u\,\partial v$, que voici : pour Clayton, $c_\theta(u,v)=(1+\theta)(uv)^{-\theta-1}(u^{-\theta}+v^{-\theta}-1)^{-2-1/\theta}$ ; pour la gaussienne, avec $x=\Phi^{-1}(u)$ et $y=\Phi^{-1}(v)$, $c_\rho(u,v)=\dfrac1{\sqrt{1-\rho^2}}\exp\!\Bigl(-\dfrac{\rho^2(x^2+y^2)-2\rho xy}{2(1-\rho^2)}\Bigr)$. Avant d'attaquer un cas réel, **testons la procédure sur des données simulées dont on connaît la copule** : nous simulons 500 couples gaussiens, puis 500 couples de Clayton (avec des marginales quelconques, exponentielle et log-normale : le rang les efface), et nous demandons à la procédure de retrouver la bonne copule.

```python
from scipy.optimize import minimize_scalar

def pseudo_obs(x, y):
    n_ = len(x)
    return stats.rankdata(x) / (n_ + 1), stats.rankdata(y) / (n_ + 1)

def ll_gauss(u, v, rho_):
    x, y = norm.ppf(u), norm.ppf(v)
    return np.sum(-0.5 * np.log(1 - rho_**2) - (rho_**2 * (x**2 + y**2) - 2 * rho_ * x * y) / (2 * (1 - rho_**2)))

def ll_clayton(u, v, th):
    return np.sum(np.log1p(th) - (th + 1) * (np.log(u) + np.log(v)) - (2 + 1 / th) * np.log(u**-th + v**-th - 1))

def ajuste(x, y):
    u, v = pseudo_obs(x, y)
    tau_ = kendalltau(x, y).statistic
    rho_h, th_h = np.sin(np.pi * tau_ / 2), 2 * tau_ / (1 - tau_)
    th_mv = minimize_scalar(lambda t: -ll_clayton(u, v, t), bounds=(0.01, 30), method="bounded").x       # maximum de vraisemblance
    return {"tau": tau_, "rho (inversion)": rho_h, "theta (inversion)": th_h, "theta (max. vraisemblance)": th_mv,
            "logvrais. gaussienne": ll_gauss(u, v, rho_h), "logvrais. Clayton": ll_clayton(u, v, th_h)}

rng = np.random.default_rng(681)
lignes = []
for nom, u_ in (("données gaussiennes (rho = 0,71)", sim_gauss(rho, 500, rng)), ("données Clayton (theta = 2)", sim_clayton(theta, 500, rng))):
    x = -np.log(1 - u_[:, 0])                         # marginale exponentielle
    y = np.exp(0.5 * norm.ppf(u_[:, 1]))              # marginale log-normale
    r = ajuste(x, y)
    lignes.append({"données": nom, "tau estimé": round(r["tau"], 3), "rho": round(r["rho (inversion)"], 3),
                   "theta (inversion)": round(r["theta (inversion)"], 2), "theta (MV)": round(r["theta (max. vraisemblance)"], 2),
                   "logvrais. gaussienne": round(r["logvrais. gaussienne"], 1), "logvrais. Clayton": round(r["logvrais. Clayton"], 1)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
                         données  tau estimé   rho  theta (inversion)  theta (MV)  logvrais. gaussienne  logvrais. Clayton
données gaussiennes (rho = 0,71)       0.452 0.652               1.65        1.08                 137.0               85.6
     données Clayton (theta = 2)       0.564 0.774               2.58        2.34                 203.4              251.5
```

Dans chaque cas, la famille qui a engendré les données obtient la **plus grande log-vraisemblance** (137,0 contre 85,6 pour les données gaussiennes ; 251,5 contre 203,4 pour les données de Clayton) : la procédure sait distinguer. Pour les données de Clayton, les deux estimations de $\theta$ (2,58 par inversion du tau, 2,34 par maximum de vraisemblance) sont voisines du vrai $\theta=2$, à l'erreur d'échantillonnage près (cet échantillon de 500 points a un tau empirique de 0,56 au lieu de 0,50). Notez qu'en cas de mauvaise famille (Clayton ajustée sur données gaussiennes) les deux méthodes d'estimation de $\theta$ divergent (1,65 contre 1,08) : c'est un signal de mauvaise spécification. (Avec 500 points, la différence de log-vraisemblance est nette ; avec 50, elle ne le serait pas.)

### 6.6.7 Applications

**Un cas réel (simulé) de dépendance faible.** Dans le fichier `clients.csv`, le panier moyen et le nombre de commandes par an des acheteurs sont-ils liés ? Les clients qui achètent souvent sont-ils aussi ceux qui dépensent plus par commande ? Le nombre de commandes est un entier : de nombreuses égalités rendent les rangs ambigus (la copule n'est pas unique pour des marginales discrètes). Nous **départageons les égalités au hasard**, par une petite astuce standard.

```python
clients = pd.read_csv("donnees/clients.csv")
ach = clients[clients["nb_commandes_an"] > 0]
rng = np.random.default_rng(682)
x = ach["panier_moyen"].to_numpy()
y = ach["nb_commandes_an"].to_numpy() + rng.uniform(-0.5, 0.5, len(ach))      # départage aléatoire des égalités (variable entière)
u, v = pseudo_obs(x, y)
r = ajuste(x, y)
print(f"{len(ach)} acheteurs ; tau de Kendall = {r['tau']:.3f} ; rho de Spearman = {stats.spearmanr(x, y).statistic:.3f}")
print(f"log-vraisemblance : gaussienne {r['logvrais. gaussienne']:.1f}, Clayton {r['logvrais. Clayton']:.1f}")
q = 0.9
obs = np.mean((u > q) & (v > q))
rho_h = r["rho (inversion)"]
modele = multivariate_normal([0, 0], [[1, rho_h], [rho_h, 1]]).cdf([-norm.ppf(q), -norm.ppf(q)])   # P(U > q, V > q), symétrie
print(f"part de clients dans les 10 % supérieurs pour LES DEUX variables : observée {obs:.4f} | indépendance {(1 - q)**2:.4f} | copule gaussienne {modele:.4f}")
```
<!--sortie-->
```text
1740 acheteurs ; tau de Kendall = 0.079 ; rho de Spearman = 0.118
log-vraisemblance : gaussienne 12.8, Clayton 3.4
part de clients dans les 10 % supérieurs pour LES DEUX variables : observée 0.0121 | indépendance 0.0100 | copule gaussienne 0.0142
```

La dépendance est **réelle mais faible** (tau de Kendall de 0,079) : la copule gaussienne prédit 1,42 % de clients dans le décile supérieur des deux variables à la fois, contre 1,00 % sous indépendance ; la fréquence observée (1,21 %, soit 21 clients sur 1 740) se situe entre les deux, et un si petit effectif ne permet pas de trancher. Rien d'alarmant et rien d'exploitable : il est tout aussi important de savoir quand une dépendance est **négligeable**. (Dans le générateur de données, le goût pour les produits, facteur latent, influence légèrement les deux variables.)

**Le vrai problème : deux transporteurs en même temps.** Revenons à notre inquiétude. Yasmine observe depuis 1 500 jours les retards moyens de ses deux transporteurs (simulés ici ; graine 683). Le transporteur A a des retards (en jours) de marginale Pareto généralisée décalée de 1, $\xi=0{,}25$, $\sigma=1{,}5$ ; le B de $\xi=0{,}20$, $\sigma=2$. **La vraie dépendance** (que Yasmine ignore) est une copule de Clayton **retournée** de $\theta=1{,}5$ : les deux transporteurs sont **simultanément très en retard** bien plus souvent que ne le laisserait croire une dépendance gaussienne. Elle ajuste les deux familles et calcule la probabilité qu'*un même jour*, les deux retards dépassent leur propre 99ᵉ centile.

```python
def gpd_inv(u_, xi_, sg):                                  # fonction de répartition inverse de la GPD décalée de 1 (6.5)
    return 1 + sg / xi_ * ((1 - u_) ** (-xi_) - 1)

theta_v = 1.5
rng = np.random.default_rng(683)
n_j = 1500
u_vrai = 1 - sim_clayton(theta_v, n_j, rng)                 # Clayton retournée : dépendance dans la queue supérieure
A = gpd_inv(u_vrai[:, 0], 0.25, 1.5)
B = gpd_inv(u_vrai[:, 1], 0.20, 2.0)
print(f"{n_j} jours ; retard moyen A : {A.mean():.2f} j, B : {B.mean():.2f} j ; retard maximal A : {A.max():.1f} j, B : {B.max():.1f} j")

u, v = pseudo_obs(A, B)
tau_h = kendalltau(A, B).statistic
rho_h, th_h = np.sin(np.pi * tau_h / 2), 2 * tau_h / (1 - tau_h)
ll_g = ll_gauss(u, v, rho_h)
ll_cr = ll_clayton(1 - u, 1 - v, th_h)                     # Clayton retournée : on applique la densité de Clayton à (1 - u, 1 - v)
ll_c = ll_clayton(u, v, th_h)                               # Clayton non retournée, pour comparaison
print(f"tau de Kendall estimé : {tau_h:.3f}  ->  rho = {rho_h:.3f} (gaussienne) ; theta = {th_h:.2f} (Clayton)")
print(f"log-vraisemblance : gaussienne {ll_g:.1f} | Clayton (queue inférieure) {ll_c:.1f} | Clayton retournée (queue supérieure) {ll_cr:.1f}")
```
<!--sortie-->
```text
1500 jours ; retard moyen A : 2.94 j, B : 3.39 j ; retard maximal A : 23.1 j, B : 31.4 j
tau de Kendall estimé : 0.416  ->  rho = 0.608 (gaussienne) ; theta = 1.42 (Clayton)
log-vraisemblance : gaussienne 332.6 | Clayton (queue inférieure) 11.0 | Clayton retournée (queue supérieure) 431.7
```

La comparaison des log-vraisemblances désigne sans ambiguïté la **Clayton retournée**, la bonne famille : elle dépasse la gaussienne d'une centaine d'unités de log-vraisemblance (431,7 contre 332,6), alors que la Clayton « classique » (dépendance dans la queue inférieure, ce qui est le mauvais côté) est de loin la pire des trois (11,0). Le $\hat\theta=1{,}42$ obtenu est proche du vrai 1,5. Maintenant, le calcul qui compte :

```python
qq = 0.99
# P(les deux retards dépassent leur 99e centile) sous chaque modèle (marginales identiques : seules les copules diffèrent)
p_indep = (1 - qq) ** 2
p_gauss = multivariate_normal([0, 0], [[1, rho_h], [rho_h, 1]]).cdf([-norm.ppf(qq), -norm.ppf(qq)])
p_clay_ret = (2 * (1 - qq) ** (-th_h) - 1) ** (-1 / th_h)               # modèle ajusté : P(U>q,V>q) = C_theta(1-q, 1-q) pour la Clayton retournée
p_vrai = (2 * (1 - qq) ** (-theta_v) - 1) ** (-1 / theta_v)             # vérité
p_emp = np.mean((u > qq) & (v > qq))

lignes = [("indépendance", p_indep), ("copule gaussienne ajustée", p_gauss), ("Clayton retournée ajustée", p_clay_ret),
          ("VÉRITÉ (theta = 1,5)", p_vrai), ("observé sur les 1 500 jours", p_emp)]
tab = pd.DataFrame({"modèle": [l[0] for l in lignes], "P(2 retards extrêmes le même jour)": [f"{l[1]:.5f}" for l in lignes],
                    "fois plus que l'indépendance": [round(l[1] / p_indep, 1) for l in lignes],
                    "soit une fois tous les… (jours)": [round(1 / l[1]) for l in lignes]})
print(tab.to_string(index=False))
```
<!--sortie-->
```text
                     modèle P(2 retards extrêmes le même jour)  fois plus que l'indépendance  soit une fois tous les… (jours)
               indépendance                            0.00010                           1.0                            10000
  copule gaussienne ajustée                            0.00193                          19.3                              518
  Clayton retournée ajustée                            0.00615                          61.5                              163
       VÉRITÉ (theta = 1,5)                            0.00630                          63.0                              159
observé sur les 1 500 jours                            0.00533                          53.3                              188
```

C'est la leçon centrale de cette section. À marginales identiques et à dépendance **globale** identique (même tau), la copule gaussienne ajustée prévoit des doubles retards extrêmes **3,3 fois moins fréquents** que la vérité : un jour sur 518 contre un jour sur 159. Pour Yasmine, c'est la différence entre « un tel jour tous les 17 mois » et « un tel jour tous les 5 mois ». Et par rapport à l'indépendance (un jour sur 10 000), les deux modèles de dépendance annoncent un risque 19 à 63 fois plus grand : ignorer la dépendance serait bien pire encore. La Clayton retournée ajustée (un jour sur 163) est quasiment sur la vérité (un jour sur 159). Ce calcul est essentiellement un calcul de **queue conjointe**, et il dépend presque entièrement du **choix de la copule**, pas des marginales. (L'observation directe sur 1 500 jours ne contient que 8 jours de ce type, soit une fréquence de 0,53 % : le modèle de Clayton en prévoyait 9,2, la copule gaussienne 2,9. Huit événements, c'est peu pour trancher à eux seuls, ce qui illustre pourquoi on **modélise** la dépendance plutôt que de compter les événements rares.)

> ⚠️ **Limites.** (1) **La dépendance de queue est très difficile à estimer** : elle repose sur les quelques points extrêmes. Choisir une famille par la vraisemblance globale (qui est dominée par le centre des données) n'est pas une garantie sur les queues. (2) Les copules à un paramètre ont une forme de dépendance rigide ; pour **plus de deux variables**, on utilise des « vines » (lianes de copules à deux variables), et des modèles plus riches. (3) La dépendance peut **changer avec le temps** (les périodes de crise ont leur propre structure) : le modèle estimé sur une période calme est silencieux sur la crise. (4) Les copules décrivent une **association**, pas une causalité (volume III).

> ✅ **À retenir (6.6).**
> - La corrélation de Pearson ne capture que la dépendance linéaire ; le **tau de Kendall** et le **rho de Spearman** sont des mesures de **rang**, invariantes par transformation croissante.
> - **Théorème de Sklar** : toute loi jointe $=$ des **marginales** $+$ une **copule** ($H=C(F,G)$). On modélise séparément les deux.
> - La copule est la loi jointe des **rangs normalisés** $U=F(X)$ (transformation intégrale de probabilité).
> - **Gaussienne** : pas de dépendance de queue. **Clayton** : dépendance de queue inférieure ($\lambda_L=2^{-1/\theta}$) ; sa version **retournée** donne une dépendance de queue supérieure.
> - On estime une copule sur des **pseudo-observations** (rangs divisés par $n+1$), par inversion du tau ou maximum de vraisemblance ; on **valide la procédure sur des données simulées** de copule connue.
> - **À même tau, des copules différentes ont des comportements extrêmes très différents** : la probabilité d'événements simultanément rares dépend presque uniquement de la copule. C'est le risque principal d'un choix par défaut (gaussien).


## 6.7 Exercices du chapitre 6

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 8, 9 et 10 réutilisent les fonctions `metropolis_1d` et `ess` définies en 6.3. Les exercices 13 et 14 se rapportent aux sections optionnelles 6.5 et 6.6.

### Énoncés

**Exercice 1 ⭐ (bêta-binomial).** Yasmine teste un nouvel emballage : 3 clients sur 8 le jugent « excellent ». Avec l'a priori $\mathrm{Beta}(2,2)$ (« je pense plutôt autour de 50 % »), donnez (a) la loi a posteriori, (b) sa moyenne, (c) le poids de l'a priori dans cette moyenne, (d) la comparaison avec l'estimation du maximum de vraisemblance.

**Exercice 2 ⭐ (gamma-Poisson).** Le site reçoit 2, 4 et 1 commandes lors de trois soirées. A priori $\lambda\sim\mathrm{Gamma}(3;\ \text{taux }1)$ (moyenne 3 commandes par soirée). Donnez la loi a posteriori de $\lambda$, sa moyenne, et un intervalle de crédibilité à 95 %.

**Exercice 3 ⭐⭐ (normal-normal).** On modélise le log du panier avec $\sigma=0{,}35$ connu et l'a priori $\mathcal N(4{,}0;\ 0{,}5^2)$. À partir de combien d'observations le poids des données dans la moyenne a posteriori dépasse-t-il 90 % ? Calculez-le à la main, puis vérifiez avec le code.

**Exercice 4 ⭐⭐ (test A/B bayésien).** La version A d'une page convertit 30 visiteurs sur 100, la version B 42 sur 110. Avec des a priori $\mathrm{Beta}(1,1)$, calculez par simulation la probabilité que B soit meilleure que A, le gain attendu en points de pourcentage, et la probabilité que le gain dépasse 5 points. Comparez avec le test de proportions fréquentiste.

**Exercice 5 ⭐ (Monte-Carlo).** Soient $U_1,U_2$ uniformes indépendantes sur $[0,1]$. (a) Calculez à la main $\mathbb E[\max(U_1,U_2)]$. (b) Estimez-la par Monte-Carlo avec 100 000 tirages, avec son erreur type et son intervalle de confiance. (c) Estimez $P(U_1+U_2>1{,}5)$ et comparez avec la valeur exacte $1/8$.

**Exercice 6 ⭐⭐ (échantillonnage préférentiel).** Soit $X\sim\mathrm{Exp}(1)$. On veut $P(X>5)=e^{-5}$. (a) Estimez-la naïvement avec $n=10\,000$ tirages. (b) Utilisez la proposition « $5+\mathrm{Exp}(1)$ ». Que valent les poids ? Que remarquez-vous sur la variance de l'estimateur ?

**Exercice 7 ⭐⭐ (inversion).** La durée de vie $T$ (en mois) d'un abonnement suit une loi de Weibull de fonction de répartition $F(t)=1-\exp\bigl(-(t/\lambda)^k\bigr)$, avec $\lambda=24$ et $k=1{,}5$. (a) Déterminez $F^{-1}$. (b) Simulez 100 000 durées. (c) Vérifiez la médiane théorique et la moyenne théorique $\lambda\,\Gamma(1+1/k)$.

**Exercice 8 ⭐⭐ (Metropolis à la main).** On veut une chaîne sur trois états $\{1,2,3\}$ de loi stationnaire proportionnelle à $(1,2,1)$. La proposition choisit l'un des deux autres états avec probabilité $\tfrac12$. (a) Écrivez la matrice de transition de Metropolis. (b) Vérifiez le bilan détaillé. (c) Vérifiez par le code, et par simulation.

**Exercice 9 ⭐⭐ (Metropolis sur une échelle logarithmique).** Six semaines de commandes : 3, 5, 4, 6, 2, 5. Modèle : Poisson$(\lambda)$, a priori $\mathrm{Gamma}(2;\ \text{taux }0{,}5)$. (a) Donnez la loi a posteriori exacte. (b) Écrivez un Metropolis sur $\theta=\log\lambda$ (attention à la transformation de la densité) et comparez avec la loi exacte.

**Exercice 10 ⭐⭐ (diagnostics).** Une chaîne autorégressive $x_t=\varphi\,x_{t-1}+\sqrt{1-\varphi^2}\,\varepsilon_t$ ($\varepsilon_t\sim\mathcal N(0,1)$) a pour loi stationnaire $\mathcal N(0,1)$ et pour autocorrélation $\rho_k=\varphi^k$. (a) Montrez que son ESS théorique vaut environ $n\,\dfrac{1-\varphi}{1+\varphi}$. (b) Pour $\varphi=0{,}9$ et $n=20\,000$, comparez avec l'ESS calculée. (c) Quatre chaînes de $\varphi=0{,}99$ lancées de $-10,-3,3,10$ : calculez le $\widehat R$ avec et sans élimination des 300 premiers points.

**Exercice 11 ⭐⭐ (vérification prédictive).** Modélisez les paniers des acheteurs de la boutique (a) par une loi normale sur le panier en DT, (b) par une loi normale sur le **logarithme** du panier. Avec la statistique-test « asymétrie » (skewness) et le plus petit panier, quel modèle passe la vérification prédictive a posteriori ?

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

for nom, donnees in (("normale sur le panier (DT)", pan), ("normale sur le log du panier", np.log(pan))):
    To, Tr, pb = ppc_normal(donnees, 697)
    print(f"{nom:32s} asymétrie : observée {To[0]:6.3f}, répliques {Tr[:, 0].mean():6.3f} (p bayésien {pb[0]:.3f}) | "
          f"minimum : observé {To[1]:7.3f}, répliques {Tr[:, 1].mean():7.3f} (p bayésien {pb[1]:.3f})")
```
<!--sortie-->
```text
normale sur le panier (DT)       asymétrie : observée  1.037, répliques  0.003 (p bayésien 0.000) | minimum : observé  25.530, répliques -11.756 (p bayésien 0.000)
normale sur le log du panier     asymétrie : observée  0.046, répliques  0.003 (p bayésien 0.360) | minimum : observé   3.240, répliques   3.094 (p bayésien 0.144)
```

Le modèle sur le panier brut échoue : les données ont une asymétrie de 1,04 (queue à droite) que le modèle symétrique ne reproduit jamais (asymétrie répliquée : 0,00 ; $p_B=0$), et il prédit des **paniers négatifs** (le minimum répliqué vaut en moyenne −11,8 DT, ce qui est absurde), alors que le plus petit panier observé est de 25,5 DT. Le modèle sur le logarithme (c'est-à-dire une loi log-normale pour le panier) passe les deux vérifications ($p_B=0{,}36$ pour l'asymétrie et $0{,}14$ pour le minimum). C'est la raison pour laquelle on modélise les montants positifs sur une échelle logarithmique.

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
