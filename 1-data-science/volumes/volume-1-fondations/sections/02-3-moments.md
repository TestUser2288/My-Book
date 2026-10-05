## 2.3 Espérance, variance, covariance

Une loi complète (une courbe, un tableau) est riche mais encombrante. Dans la pratique, on la résume par **quelques nombres** : où est son centre ? De combien s'étale-t-elle ? Comment deux variables évoluent-elles ensemble ? Cette section définit ces trois résumés, démontre leurs propriétés et les applique à des décisions chiffrées.

### 2.3.1 L'espérance : la moyenne « à long terme »

> 💡 **Intuition.** L'**espérance** $E[X]$ est la valeur moyenne que prendrait $X$ si on répétait l'expérience un très grand nombre de fois. C'est une **moyenne pondérée** : chaque valeur est comptée proportionnellement à sa probabilité.

Pour une variable discrète et pour une variable continue (de densité $f$) :

$$E[X]=\sum_k k\,P(X=k)\qquad\text{et}\qquad E[X]=\int_{-\infty}^{+\infty}x\,f(x)\,dx.$$

**Exemple 1 : le dé.** $E[X]=1\cdot\tfrac16+2\cdot\tfrac16+\dots+6\cdot\tfrac16=\tfrac{21}6=3{,}5$. Remarquez que l'espérance n'est **pas** une valeur possible : on n'obtiendra jamais 3,5. C'est un centre de gravité, pas un résultat.

**Exemple 2 : une décision.** La gérante hésite à lancer une nouvelle lampe. Elle envisage trois scénarios pour le bénéfice du premier trimestre :

| Scénario | Probabilité | Bénéfice (€) |
|---|---:|---:|
| Grand succès | 0,3 | +5 000 |
| Succès moyen | 0,5 | +1 000 |
| Échec | 0,2 | −3 000 |

$$E[X]=0{,}3\times5000+0{,}5\times1000+0{,}2\times(-3000)=1500+500-600=1400.$$

Le lancement rapporte **en moyenne** 1 400 €. Une option alternative sûre rapporterait 1 200 €. Faut-il lancer ? L'espérance seule dit oui, mais elle ne dit rien du **risque** : il y a 20 % de chances de perdre de l'argent. C'est exactement le rôle de la variance, ci-dessous.

#### Propriétés de l'espérance

> 📐 **Linéarité.** Pour toutes variables $X$, $Y$ et constantes $a$, $b$ :
>
> $$E[aX+b]=aE[X]+b,\qquad E[X+Y]=E[X]+E[Y].$$
>
> *Preuve de la première (cas discret).* $E[aX+b]=\sum_k(ak+b)P(X=k)=a\sum_k kP(X=k)+b\sum_kP(X=k)=aE[X]+b\cdot1$. $\blacksquare$
>
> La seconde se démontre de la même façon avec une somme double. Elle est **toujours vraie, même si $X$ et $Y$ sont dépendantes** : c'est ce qui la rend si puissante.

**Exemple d'usage.** Si les ventes du jour ont une espérance de 120 articles à 25 € l'unité, les recettes $25X$ ont pour espérance $25\times120=3000$ € : on multiplie simplement.

**Application élégante : l'espérance d'une binomiale.** Une binomiale $X\sim\text{Bin}(n,p)$ est la somme de $n$ Bernoulli : $X=B_1+\dots+B_n$, avec $E[B_i]=1\cdot p+0\cdot(1-p)=p$. Par linéarité,

$$E[X]=E[B_1]+\dots+E[B_n]=np.$$

Sans aucun calcul avec $\binom nk$ ! Pour nos 20 visiteurs à 20 % : $E[X]=4$, ce qu'on avait deviné.

| Loi | Espérance |
|---|---|
| Bernoulli$(p)$ | $p$ |
| Binomiale$(n,p)$ | $np$ |
| Poisson$(\lambda)$ | $\lambda$ |
| Exponentielle$(\lambda)$ | $1/\lambda$ |
| Uniforme$(a,b)$ | $(a+b)/2$ |
| Normale$(\mu,\sigma^2)$ | $\mu$ |

> ⚠️ **Attention : $E[XY]\neq E[X]E[Y]$ en général**, et $E[f(X)]\neq f(E[X])$ en général. Exemple : pour le dé, $E[X^2]=\tfrac{91}6\approx15{,}17$, alors que $(E[X])^2=12{,}25$. L'écart entre ces deux nombres est justement la **variance**.

### 2.3.2 La variance : mesurer l'étalement

Deux commerçants ont chacun un bénéfice moyen de 1 000 € par mois. Chez l'un, c'est toujours entre 950 et 1 050. Chez l'autre, ça varie de −2 000 à +4 000. Même espérance, risques très différents. La **variance** mesure l'écart typique au centre :

$$\operatorname{Var}(X)=E\bigl[(X-\mu)^2\bigr],\qquad \mu=E[X].$$

On prend le **carré** de l'écart pour que les écarts positifs et négatifs ne se compensent pas. L'**écart-type** $\sigma=\sqrt{\operatorname{Var}(X)}$ ramène le résultat à l'unité d'origine (des euros, et non des euros²).

> 📐 **Formule de calcul (« moyenne des carrés moins carré de la moyenne »).**
>
> $$\operatorname{Var}(X)=E[X^2]-\bigl(E[X]\bigr)^2.$$
>
> *Preuve.* On développe le carré : $(X-\mu)^2=X^2-2\mu X+\mu^2$. Par linéarité, $E[(X-\mu)^2]=E[X^2]-2\mu E[X]+\mu^2=E[X^2]-2\mu^2+\mu^2=E[X^2]-\mu^2$. $\blacksquare$

*(Rappel de la section ➕ analyse numérique : cette formule est parfaite sur le papier, mais dangereuse sur ordinateur si $\mu$ est grand devant $\sigma$.)*

**Retour à la lampe.** Calculons $E[X^2]$ puis la variance :

$$E[X^2]=0{,}3\times5000^2+0{,}5\times1000^2+0{,}2\times3000^2=7{,}5\cdot10^6+0{,}5\cdot10^6+1{,}8\cdot10^6=9{,}8\cdot10^6,$$

$$\operatorname{Var}(X)=9{,}8\cdot10^6-1400^2=9{,}8\cdot10^6-1{,}96\cdot10^6=7{,}84\cdot10^6,\qquad\sigma=2800\ \text{€}.$$

L'écart-type (2 800 €) est **deux fois plus grand** que l'espérance (1 400 €) : l'option est très risquée. Face à l'option sûre à 1 200 €, le gain moyen n'est supérieur que de 200 € alors que le risque est considérable. Beaucoup de gens (et de gérants) préféreraient l'option sûre. Il n'y a pas de « bonne » réponse mathématique : la variance **quantifie** le risque pour que la décision soit éclairée.

#### Propriétés de la variance

> 📐 **Effet d'un changement d'échelle.** $\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X)$.
>
> *Preuve.* $E[aX+b]=a\mu+b$, donc $(aX+b)-E[aX+b]=a(X-\mu)$ et $\operatorname{Var}(aX+b)=E[a^2(X-\mu)^2]=a^2\operatorname{Var}(X)$. $\blacksquare$
>
> Conséquences : ajouter une constante ($+b$) ne change pas l'étalement ; multiplier par $a$ multiplie l'écart-type par $|a|$. Convertir des euros dans une autre monnaie multiplie l'écart-type par le taux de change, et c'est tout.

> 📐 **Somme de variables indépendantes.** Si $X$ et $Y$ sont **indépendantes**, $\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)$. (Nous démontrons le cas général au 2.3.3.)

**Variance d'une binomiale.** $B_i$ de Bernoulli : $E[B_i^2]=p$ (car $B_i^2=B_i$), donc $\operatorname{Var}(B_i)=p-p^2=p(1-p)$. Pour $X=\sum B_i$ avec des $B_i$ indépendantes : $\operatorname{Var}(X)=np(1-p)$.

| Loi | Variance |
|---|---|
| Bernoulli$(p)$ | $p(1-p)$ |
| Binomiale$(n,p)$ | $np(1-p)$ |
| Poisson$(\lambda)$ | $\lambda$ (variance = espérance !) |
| Exponentielle$(\lambda)$ | $1/\lambda^2$ |
| Uniforme$(a,b)$ | $(b-a)^2/12$ |
| Normale$(\mu,\sigma^2)$ | $\sigma^2$ |

Une simulation de 200 000 tirages pour chacune de ces lois retrouve les valeurs de ces deux tableaux à moins de 1 % près (par exemple, 4,004 pour l'espérance d'une binomiale$(20\,;0{,}2)$ contre 4 en théorie, et 3,209 pour sa variance contre 3,2).

La **loi de Poisson** a la propriété particulière que sa variance est égale à son espérance. Si les commandes de la gérante varient *beaucoup plus* que leur moyenne (on parle de **sur-dispersion**), c'est un signe que le modèle de Poisson est trop simple.

### 2.3.3 Covariance et corrélation : bouger ensemble

> 💡 **Intuition.** Les jours où la gérante dépense plus en publicité, vend-elle plus ? On cherche à mesurer si deux variables **varient dans le même sens**. Chaque jour, on regarde si $X$ est au-dessus de sa moyenne et si $Y$ l'est aussi : si les deux écarts ont **le même signe** la plupart du temps, la covariance est positive.

$$\operatorname{Cov}(X,Y)=E\bigl[(X-\mu_X)(Y-\mu_Y)\bigr]=E[XY]-E[X]E[Y].$$

**Exemple à la main.** Quatre semaines : dépenses publicitaires $x=(10,20,30,40)$ € et ventes $y=(12,18,26,32)$.

- Moyennes : $\bar x=25$, $\bar y=22$.
- Écarts à la moyenne : $x-\bar x=(-15,-5,5,15)$ et $y-\bar y=(-10,-4,4,10)$.
- Produits : $(150,\ 20,\ 20,\ 150)$, de somme 340, donc covariance $=340/4=85$.

Un piège de programmation guette ici : les bibliothèques ne divisent pas toutes par le même nombre.

```python
import numpy as np
x = np.array([10, 20, 30, 40.0]); y = np.array([12, 18, 26, 32.0])
print("à la main (÷ n) :", ((x - x.mean()) * (y - y.mean())).mean())
print("np.cov    (÷ n-1):", np.cov(x, y)[0, 1].round(2))
```
<!--sortie-->
```text
à la main (÷ n) : 85.0
np.cov    (÷ n-1): 113.33
```

> ⚠️ **$n$ ou $n-1$ ?** `np.cov` divise par $n-1$ (estimateur sans biais, section 3.2) et donne 113,33 ; la formule de la **loi** divise par $n$. Pour de grands échantillons la différence disparaît ; ici avec $n=4$ elle est visible. On y reviendra.

**Problème : la covariance dépend des unités.** Si on mesure les dépenses en centimes, la covariance est multipliée par 100 sans que la relation change ! On **normalise** en divisant par les écarts-types, ce qui donne la **corrélation** de Pearson :

$$\rho_{XY}=\frac{\operatorname{Cov}(X,Y)}{\sigma_X\,\sigma_Y}\in[-1,\ 1].$$

> 📐 **Pourquoi $\rho$ est toujours entre −1 et 1.** C'est exactement l'inégalité de Cauchy–Schwarz du chapitre 1 ! Rangez les écarts à la moyenne $(x_i-\bar x)$ dans un vecteur $\mathbf{u}$ et $(y_i-\bar y)$ dans $\mathbf{v}$. Alors $\operatorname{Cov}\propto\mathbf{u}\cdot\mathbf{v}$, $\sigma_X\propto\lVert\mathbf{u}\rVert$, $\sigma_Y\propto\lVert\mathbf{v}\rVert$ (avec le même facteur $1/n$), et
>
> $$\rho=\frac{\mathbf{u}\cdot\mathbf{v}}{\lVert\mathbf{u}\rVert\,\lVert\mathbf{v}\rVert}=\cos\theta\in[-1,1].$$
>
> **La corrélation est le cosinus de l'angle entre les deux vecteurs d'écarts.** $\rho=1$ : même direction ; $\rho=-1$ : directions opposées ; $\rho=0$ : vecteurs perpendiculaires (orthogonaux). $\blacksquare$

Ici : $\rho=\dfrac{85}{\sqrt{125\times58}}\approx0{,}998$, une relation presque parfaitement linéaire.

![Quatre nuages de points et leur corrélation. Le dernier montre qu'une corrélation nulle n'implique pas l'indépendance.](figures/ch02-correlations.png)

> ⚠️ **Trois mises en garde essentielles.**
>
> 1. **Corrélation n'est pas causalité.** Les glaces et les coups de soleil sont corrélés ; ni l'un ne cause l'autre : c'est la chaleur qui explique les deux. (Le volume II y consacre un chapitre facultatif, l'inférence causale.)
> 2. **Indépendantes ⇒ non corrélées, mais pas l'inverse.** Le dernier nuage de la figure est une parabole : $Y$ est une **fonction exacte** de $X$ (à un peu de bruit près), donc très dépendante, pourtant $\rho\approx0$. Cela arrive parce que $\rho$ ne détecte que les relations **linéaires**.
> 3. **Regardez toujours le nuage de points.** Un chiffre unique peut cacher une structure très différente (nous le montrerons avec les « quartets » de la section 3.1).

> 📐 **Variance d'une somme (cas général).** $\operatorname{Var}(X+Y)=\operatorname{Var}(X)+\operatorname{Var}(Y)+2\operatorname{Cov}(X,Y)$.
>
> *Preuve.* Posons $\tilde X=X-\mu_X$ et $\tilde Y=Y-\mu_Y$. Alors $\operatorname{Var}(X+Y)=E[(\tilde X+\tilde Y)^2]=E[\tilde X^2]+2E[\tilde X\tilde Y]+E[\tilde Y^2]$, ce qui est bien $\operatorname{Var}X+2\operatorname{Cov}(X,Y)+\operatorname{Var}Y$. $\blacksquare$
>
> Si $X$ et $Y$ sont indépendantes, $\operatorname{Cov}=0$ et on retrouve l'additivité des variances.

**Exemple : la diversification.** Les ventes quotidiennes de deux produits, $X$ et $Y$, ont chacune une moyenne de 50 et un écart-type de 10. Quelle est la variabilité des ventes **totales** $X+Y$ ?

- Si les deux produits sont **corrélés positivement** ($\rho=+0{,}5$) : $\operatorname{Var}=100+100+2\times0{,}5\times100=300$, soit $\sigma\approx17{,}3$.
- Si les deux produits sont **corrélés négativement** ($\rho=-0{,}5$ : quand l'un se vend mal, l'autre se vend bien) : $\operatorname{Var}=100+100-100=100$, soit $\sigma=10$.

Mêmes moyennes, mêmes écarts-types individuels, mais un total **bien moins variable** (écart-type de 10 au lieu de 17) quand les produits se compensent. C'est le principe de la **diversification** : on réunit des produits (ou des placements) dont les hauts et les bas ne coïncident pas, pour stabiliser le tout. Une simulation de 100 000 jours confirme ces deux valeurs (17,29 et 9,97).

#### La matrice de covariance

Avec plusieurs variables, on range toutes les variances et covariances dans une **matrice de covariance** $\boldsymbol\Sigma$ : variances sur la diagonale, covariances ailleurs. Elle est **symétrique** et ses valeurs propres sont **positives** ; c'est celle dont nous avions calculé les vecteurs propres au 1.1.3 (aperçu de l'ACP).

La matrice de **corrélation** en est la version « normalisée » : diagonale de 1 et tout entre −1 et 1. Prenons trois variables mesurées sur 365 jours : la température, le nombre de visites et les ventes. On obtient des corrélations de 0,76 entre température et visites, 0,84 entre visites et ventes, et 0,67 entre température et ventes. La corrélation température–ventes, un peu plus faible, est un effet **indirect** : la température agit sur les visites, qui agissent sur les ventes.

> ✅ **À retenir (espérance, variance, covariance).**
>
> - $E[X]$ = moyenne pondérée à long terme ; **linéaire** : $E[aX+b]=aE[X]+b$, $E[X+Y]=E[X]+E[Y]$ toujours.
> - $\operatorname{Var}(X)=E[(X-\mu)^2]=E[X^2]-\mu^2$ ; $\sigma=\sqrt{\operatorname{Var}}$ ; $\operatorname{Var}(aX+b)=a^2\operatorname{Var}(X)$.
> - $\operatorname{Var}(X+Y)=\operatorname{Var}X+\operatorname{Var}Y+2\operatorname{Cov}(X,Y)$ : la covariance mesure comment les variables se combinent.
> - $\rho=\operatorname{Cov}/(\sigma_X\sigma_Y)$ est un **cosinus** : entre −1 et 1, sans unité. Il ne mesure que le lien **linéaire**, et ne prouve jamais une causalité.
> - La matrice de covariance range toutes les covariances ; c'est l'objet central de l'ACP.

> 📒 **Pour s'entraîner.** Cahier, chapitre 2 : application 2.5 (diversification et matrice de covariance), exercices 2.7 et 2.8.

```python hide
# Vérifie tous les nombres cités dans la section 2.3.
import numpy as np
from scipy import stats
benefices = np.array([5000, 1000, -3000]); probas = np.array([0.3, 0.5, 0.2])
e = (benefices * probas).sum(); e2 = (benefices**2 * probas).sum()
print("lampe : E =", e, "| E[X^2] =", e2, "| Var =", e2 - e**2, "| sigma =", np.sqrt(e2 - e**2), "| P(perte) =", probas[benefices < 0].sum())
des = np.arange(1, 7); print("dé : E =", des.mean(), "| E[X^2] =", round((des**2).mean(), 2), "| E^2 =", des.mean()**2)
rng = np.random.default_rng(21)
lois = {"Binomiale(20; 0,2)": (stats.binom(20, 0.2), rng.binomial(20, 0.2, 200_000)),
        "Poisson(3)": (stats.poisson(3), rng.poisson(3, 200_000)),
        "Exponentielle(0,5)": (stats.expon(scale=2), rng.exponential(2, 200_000)),
        "Normale(120; 15)": (stats.norm(120, 15), rng.normal(120, 15, 200_000))}
for nom, (loi, ech) in lois.items():
    print(f"{nom:<20} E {loi.mean():.3f} vs {ech.mean():.3f} | Var {loi.var():.3f} vs {ech.var():.3f}")
x = np.array([10, 20, 30, 40.0]); y = np.array([12, 18, 26, 32.0])
print("cov =", ((x - x.mean()) * (y - y.mean())).mean(), "| np.cov =", np.cov(x, y)[0, 1].round(2), "| rho =", np.corrcoef(x, y)[0, 1].round(4), "| 85/sqrt(125*58) =", round(85 / np.sqrt(125 * 58), 4))
rng = np.random.default_rng(8)
for rho in (0.5, -0.5):
    cov = [[100, rho * 100], [rho * 100, 100]]
    total = rng.multivariate_normal([50, 50], cov, size=100_000).sum(axis=1)
    print(f"diversification rho={rho:+.1f} : sigma simulé {total.std():.2f} | théorie {np.sqrt(200 + 2 * rho * 100):.2f}")
rng = np.random.default_rng(2)
n = 365
temperature = rng.normal(25, 6, n); visites = 80 + 3 * temperature + rng.normal(0, 15, n); ventes = 0.2 * visites + rng.normal(0, 3, n)
print("corrélations température-visites, visites-ventes, température-ventes :", np.corrcoef(np.column_stack([temperature, visites, ventes]).T).round(2)[[0, 1, 0], [1, 2, 2]])
```
<!--sortie-->
```text
lampe : E = 1400.0 | E[X^2] = 9800000.0 | Var = 7840000.0 | sigma = 2800.0 | P(perte) = 0.2
dé : E = 3.5 | E[X^2] = 15.17 | E^2 = 12.25
Binomiale(20; 0,2)   E 4.000 vs 4.004 | Var 3.200 vs 3.209
Poisson(3)           E 3.000 vs 3.005 | Var 3.000 vs 3.006
Exponentielle(0,5)   E 2.000 vs 2.001 | Var 4.000 vs 3.968
Normale(120; 15)     E 120.000 vs 120.001 | Var 225.000 vs 225.467
cov = 85.0 | np.cov = 113.33 | rho = 0.9983 | 85/sqrt(125*58) = 0.9983
diversification rho=+0.5 : sigma simulé 17.29 | théorie 17.32
diversification rho=-0.5 : sigma simulé 9.97 | théorie 10.00
corrélations température-visites, visites-ventes, température-ventes : [0.76 0.84 0.67]
```
