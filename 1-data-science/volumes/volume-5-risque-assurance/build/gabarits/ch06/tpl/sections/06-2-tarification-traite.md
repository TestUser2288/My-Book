## 6.2 Tarifer un traité

Combien doit coûter la tranche « 1 M€ xs 1 M€ » ? Le réassureur répond par une **prime pure** (la charge annuelle attendue de la tranche), puis par un **chargement** pour le risque et les frais. Cette section estime la prime pure de trois façons (l'expérience, la loi de queue, l'exposition), les compare à la **vérité programmée**, mesure l'incertitude de chacune, traite à part le cas des catastrophes, et passe enfin de la prime pure à la prime technique.

### 6.2.1 L'expérience : le *burning cost* et le piège de l'exposition

La méthode la plus naturelle demande : « **combien la tranche aurait-elle coûté, chaque année passée ?** ». On rejoue l'historique des sinistres à travers la tranche, année par année, et l'on fait la moyenne. C'est le **burning cost** (coût de la « combustion » passée de la tranche).

Pour que cette moyenne ait un sens, il faut ramener chaque année passée **à la situation de l'année couverte**. Trois corrections s'imposent :

1. **Développer** les sinistres récents, dont le montant final n'est pas connu (chapitre 2, sections 2.3 et 2.5). Dans nos données, les montants sont finaux ; en pratique, c'est une étape à part entière.
2. **Indexer** les montants passés au niveau de coût actuel (inflation des sinistres), **avant** d'appliquer la tranche, puisque la tranche s'applique à chaque sinistre au prix d'aujourd'hui.
3. **Ajuster l'exposition** : une année où le portefeuille était plus petit aurait produit plus de sinistres avec le portefeuille d'aujourd'hui.

Avec $C_t$ la charge de la tranche sur l'année $t$ et $E_t$ l'exposition de cette année (nombre de risques, primes, capitaux assurés…), le *burning cost* de l'année couverte $T$ est
$$\mathrm{BC}=\frac1n\sum_{t=1}^{n}C_t\cdot\frac{E_T}{E_t}.$$

Ici, le portefeuille croît de 3 % par an : l'exposition de 2025 vaut $1{,}03^{15}\approx{{croiss15|2}}$ fois celle de 2010. Comparons le *burning cost* **brut** (sans correction) et **ajusté** de l'exposition, aux trois tranches « par risque » suivantes.

```python
for a, L in O.COUCHES:
    brut, _ = O.burning_cost(sg, a, L, ajuste=False)
    ajuste, _ = O.burning_cost(sg, a, L)
    print(f"{L/1e6:g} xs {a/1e6:g} : brut {brut/1e6:.2f} M€  ajusté {ajuste/1e6:.2f} M€  vérité {O.prix_vrai(a, L)/1e6:.2f} M€")
```

Le *burning cost* brut sous-estime de {{err_raw1|pc0}}, {{err_raw2|pc0}} et {{err_raw3|pc0}} % les trois tranches : il traite 2010 et 2024 comme si le portefeuille avait toujours eu la même taille. L'ajustement d'exposition supprime ce **biais** (il reste des écarts de {{err_adj1|pc0}} %, {{err_adj2|pc0}} % et {{err_adj3|pc0}} %, signes compris, qui relèvent du **bruit d'échantillonnage** que nous mesurerons en 6.2.4).

![Charge annuelle de chaque tranche, brute (gris) et ramenée à l'exposition 2025 (bleu). La ligne orange est la charge annuelle attendue réelle.](figures/ch06-burning.png)

La figure montre ce que cache la moyenne : la tranche haute (« 2 M€ xs 2 M€ ») a coûté **moins de {{calme_max|M2}} M€ par an de 2015 à 2021**, puis jusqu'à {{pic24|M1}} M€ en 2024. Une tarification fondée sur la seule période calme aurait donné un prix dérisoire.

> ⚠️ **L'indexation est une hypothèse, pas une formalité.** L'inflation des sinistres s'**applique avant la tranche**, et la tranche **l'amplifie** : si tous les sinistres augmentent de 4 % par an, un sinistre de 900 000 € passe en dix ans à environ 1,33 M€, c'est-à-dire qu'il **entre** dans la tranche « 1 M€ xs 1 M€ » qu'il ne touchait pas. C'est l'**effet de levier de l'inflation sur les tranches**. Dans nos données, il n'y a **aucune** inflation de la sévérité : sur les sinistres de plus de 500 000 €, la pente du logarithme du montant selon l'année est de {{pente|pc2}} % par an (statistiquement nulle). Si l'on avait indexé à 4 % par habitude, les trois tranches auraient été surestimées de {{err_inf1|pc0}}, {{err_inf2|pc0}} et {{err_inf3|pc0}} % : une erreur de **+{{err_inf3|pc0}} %** sur la tranche la plus haute. Le taux d'indexation doit être **estimé et justifié**, pas hérité.

```python hide
brut_ = np.array([O.burning_cost(sg, a, L, ajuste=False)[0] for a, L in O.COUCHES])
adj_ = np.array([O.burning_cost(sg, a, L)[0] for a, L in O.COUCHES])
vrai_ = np.array([O.prix_vrai(a, L) for a, L in O.COUCHES])
for i in range(3):
    NUM(f"bc_raw{i+1}", brut_[i]); NUM(f"bc_adj{i+1}", adj_[i]); NUM(f"vrai{i+1}", vrai_[i])
    NUM(f"err_raw{i+1}", 1 - brut_[i] / vrai_[i]); NUM(f"err_adj{i+1}", adj_[i] / vrai_[i] - 1)
assert (brut_ < vrai_).all()
NUM("croiss15", 1.03 ** 15)
adj_par_an = O.burning_cost(sg, 2e6, 2e6)[1] * O.facteur_2025(O.ANNEES)
calme = adj_par_an[(O.ANNEES >= 2015) & (O.ANNEES <= 2021)].max()
NUM("calme_max", calme); NUM("pic24", adj_par_an[-1])
assert calme < 1.5e5 and adj_par_an[-1] > 1.5e6
gros = sg[sg["montant"] > 5e5]
pente = np.polyfit(gros["annee_survenance"], np.log(gros["montant"]), 1)[0]
res_pente = stats.linregress(gros["annee_survenance"], np.log(gros["montant"]))
assert res_pente.pvalue > 0.1
NUM("pente", pente)
# indexation erronée à 4 % par an
infl = []
for a, L in O.COUCHES:
    par_an = np.array([O.tranche(sg.loc[sg["annee_survenance"] == y, "montant"].values * 1.04 ** (2025 - y), a, L).sum() for y in O.ANNEES])
    infl.append((par_an * O.facteur_2025(O.ANNEES)).mean())
infl = np.array(infl)
assert (infl > vrai_).all()
for i in range(3):
    NUM(f"err_inf{i+1}", infl[i] / vrai_[i] - 1)
O.fig_burning(sg)
```

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.3 et exercices 6.6 et 6.7.

### 6.2.2 La tarification par l'exposition

Le *burning cost* exige un historique. Pour un **nouveau traité**, ou une tranche qui n'a jamais été touchée, on ne peut pas s'y fier. La **tarification par l'exposition** part d'une autre idée : au lieu d'observer ce que la tranche a coûté, on **décrit la répartition des sinistres** à l'aide d'une **courbe d'exposition**, et l'on en déduit la part de la charge totale qui tombe dans la tranche.

Soit $X$ un sinistre. La **courbe d'exposition** (ou *limited expected value* normalisée) est
$$G(d)=\frac{E[\min(X,d)]}{E[X]},$$
la **part de la charge attendue qui se situe sous le plafond $d$**. La charge attendue d'une tranche « $L$ xs $a$ » est alors
$$E\bigl[\min(\max(X-a,0),L)\bigr]=E[X]\,\bigl(G(a+L)-G(a)\bigr),$$
puisque $\min(\max(X-a,0),L)=\min(X,a+L)-\min(X,a)$. Multipliée par le nombre attendu de sinistres $\lambda$, elle donne la prime pure de la tranche. En pratique, on applique la courbe à **chaque risque de capital assuré $V_i$** (le plafond relatif est $d/V_i$), à l'aide de courbes publiées pour chaque type de risque : c'est ce qu'on fait pour les risques industriels, quand l'historique est mince.

Notre jeu de données n'a pas de capitaux assurés ; nous pouvons toutefois **estimer la courbe d'exposition à partir des sinistres eux-mêmes**, en euros.

| Plafond $d$ | 100 000 | 250 000 | 500 000 | 1 000 000 | 2 000 000 | 3 000 000 |
|---|---:|---:|---:|---:|---:|---:|
| $G(d)$ | {{g1|pc1}} % | {{g2|pc1}} % | {{g3|pc1}} % | {{g4|pc1}} % | {{g5|pc1}} % | {{g6|pc1}} % |

Lecture : {{g3|pc1}} % de la charge attendue se situe sous 500 000 € par sinistre ; les **{{au500|pc1}} % restants** viennent des parties de sinistres au-delà de 500 000 €, et {{au1m|pc1}} % au-delà de 1 M€. La tranche « 1 M€ xs 1 M€ » reçoit donc $G(2\,\mathrm{M€})-G(1\,\mathrm{M€})={{part2|pc1}}$ % de la charge : en multipliant par la charge annuelle attendue ({{lam25|0}} sinistres de moyenne {{moy|int}} €), on trouve {{fs2|M2}} M€, contre {{vrai2|M2}} M€ en vérité. Pour les trois tranches, cette approche « **fréquence × sévérité empirique** » donne {{fs1|M2}}, {{fs2|M2}} et {{fs3|M2}} M€.

#### Un exemple à la main avec une loi de Pareto

Supposons que les sinistres au-delà de 500 000 € soient au nombre de 15 par an et suivent une loi de Pareto de paramètre 2 : $P(X>x\mid X>u)=(u/x)^2$ avec $u=500\,000$. La charge annuelle attendue de la tranche « 1 M€ xs 1 M€ » est
$$15\int_{1\,000\,000}^{2\,000\,000}\Bigl(\frac{500\,000}{x}\Bigr)^2dx=15\times(500\,000)^2\Bigl(\frac1{1\,000\,000}-\frac1{2\,000\,000}\Bigr)=15\times125\,000=1\,875\,000\ \text{€}.$$
On voit le mécanisme : **tout repose sur la forme supposée de la queue**. Avec un exposant de 1,5 (queue plus lourde) la même tranche coûterait {{pareto15|M2}} M€ ; avec 3 (queue plus légère), {{pareto3|M2}} M€.

```python hide
xs_ = sg["montant"].values
G = lambda d: O.lev_empirique(xs_, d) / xs_.mean()
for i, d in enumerate([1e5, 2.5e5, 5e5, 1e6, 2e6, 3e6]):
    NUM(f"g{i+1}", G(d))
NUM("au500", 1 - G(5e5)); NUM("au1m", 1 - G(1e6)); NUM("part2", G(2e6) - G(1e6))
fs = np.array([O.LAMBDA_2025 * (O.lev_empirique(xs_, a + L) - O.lev_empirique(xs_, a)) for a, L in O.COUCHES])
for i in range(3):
    NUM(f"fs{i+1}", fs[i])
def pareto_tranche(lam_u, u, alpha, a, L):
    return lam_u * u ** alpha / (1 - alpha) * ((a + L) ** (1 - alpha) - a ** (1 - alpha))
from scipy import integrate
assert abs(pareto_tranche(15, 5e5, 2, 1e6, 1e6) - 1.875e6) < 1e-3
assert abs(integrate.quad(lambda t: 15 * (5e5 / t) ** 2, 1e6, 2e6)[0] - 1.875e6) < 1
NUM("pareto15", pareto_tranche(15, 5e5, 1.5, 1e6, 1e6)); NUM("pareto3", pareto_tranche(15, 5e5, 3, 1e6, 1e6))
```

> 💡 **Deux méthodes, deux informations.** Le *burning cost* dit ce que la tranche **a coûté** ; l'exposition dit ce que la tranche **devrait coûter** si les sinistres se répartissent comme le suppose la courbe. Quand l'historique est riche, la première est plus honnête ; quand il est mince, la seconde est la seule disponible, et sa validité dépend de la courbe choisie.

### 6.2.3 Ajuster une loi de queue : la GPD

Le *burning cost* de la tranche haute repose sur très peu de sinistres. Pour mieux utiliser l'information, on **ajuste une loi** à la queue et l'on calcule la prime par une formule. La théorie des valeurs extrêmes (volume II, section 6.5) assure que les dépassements d'un seuil élevé $u$ suivent, sous des conditions générales, une **loi de Pareto généralisée** (GPD) :
$$P(X-u>y\mid X>u)=\Bigl(1+\xi\,\frac{y}{\beta}\Bigr)^{-1/\xi},\qquad y\ge0,$$
où $\xi$ est l'**indice de queue** (plus il est grand, plus la queue est lourde ; $\xi\ge1$ rend la moyenne infinie) et $\beta$ un paramètre d'échelle.

Pour un seuil $u$ et un nombre annuel $\lambda_u$ de dépassements, la prime pure d'une tranche « $L$ xs $a$ » avec $a\ge u$ est
$$\lambda_u\int_a^{a+L}\Bigl(1+\xi\,\frac{x-u}{\beta}\Bigr)^{-1/\xi}dx=\lambda_u\,\frac{\beta}{1-\xi}\Bigl[\Bigl(1+\xi\frac{a-u}{\beta}\Bigr)^{1-1/\xi}-\Bigl(1+\xi\frac{a+L-u}{\beta}\Bigr)^{1-1/\xi}\Bigr].$$

> 📐 **Pourquoi cette formule.** Pour un sinistre $X$, $\min(\max(X-a,0),L)=\int_a^{a+L}\mathbf 1\{X>x\}\,dx$. En prenant l'espérance (échange de l'intégrale et de l'espérance, théorème de Fubini) et en multipliant par le nombre annuel $\lambda$ de sinistres, la charge annuelle attendue vaut $\int_a^{a+L}\lambda P(X>x)\,dx$. Or, pour $x\ge u$, $\lambda P(X>x)=\lambda_u\,P(X>x\mid X>u)$, la survie de la GPD. Une primitive de $\bigl(1+\xi\frac{x-u}{\beta}\bigr)^{-1/\xi}$ est $-\frac{\beta}{1-\xi}\bigl(1+\xi\frac{x-u}{\beta}\bigr)^{1-1/\xi}$, d'où la formule.

Ajustons-la au seuil de 500 000 €, avec le nombre annuel de dépassements ramené à l'exposition de 2025.

```python
u = 5e5
exces = sg["montant"].values[sg["montant"].values > u] - u
xi, _, beta = stats.genpareto.fit(exces, floc=0)
lam_u = O.taux_depassement(sg, u)
print(f"n = {len(exces)}  xi = {xi:.3f}  beta = {beta:,.0f}  lambda_u = {lam_u:.1f} par an")
```

On obtient $\hat\xi={{xi5|3}}$ et $\hat\beta={{beta5|int}}$ € sur {{n5|int}} dépassements, soit {{lam5|1}} par an au niveau 2025. Les prix de la formule sont de {{gpd1|M2}}, {{gpd2|M2}} et {{gpd3|M2}} M€ pour les trois tranches.

> ⚠️ **Le choix du seuil est un choix de modèle.** Si $u$ est trop bas, la loi ne suit plus la GPD (on y mêle le corps de la distribution) ; trop haut, il reste trop peu de points. On regarde la **stabilité** de $\hat\xi$ quand $u$ varie. La figure ci-dessous le montre : $\hat\xi$ vaut {{xi3|2}} au seuil de 300 000 €, {{xi5|2}} à 500 000 €, et {{xi10|2}} à 1 M€, où il devient **négatif** (une queue qui « s'arrête ») alors que nous savons que la vraie queue est très lourde ($\xi=0{,}55$). À ce seuil, il ne reste que {{n10|int}} dépassements : la bande d'incertitude de $\hat\xi$ est large, et le résultat n'est pas fiable.

![À gauche, l'excès moyen au-delà d'un seuil ; à droite, l'estimation de l'indice de queue selon le seuil, avec sa bande d'incertitude.](figures/ch06-gpd.png)

Le prix de la tranche la plus haute dépend de ce choix. Avec les seuils de 300 000 €, de 500 000 € et de 1 M€, le prix de « 2 M€ xs 2 M€ » vaut respectivement {{thr1|M2}}, {{thr2|M2}} et {{thr3|M2}} M€, alors que la vérité est de {{vrai3|M2}} M€. **Aucun** de ces chiffres n'est faux au sens du calcul : ils reflètent l'incertitude du modèle, qu'il faut annoncer plutôt que cacher.

```python hide
u = 5e5
exces = sg["montant"].values[sg["montant"].values > u] - u
xi, _, beta = stats.genpareto.fit(exces, floc=0)
lam_u = O.taux_depassement(sg, u)
NUM("xi5", xi); NUM("beta5", beta); NUM("n5", len(exces)); NUM("lam5", lam_u)
gp = np.array([O.prix_gpd(a, L, u, xi, beta, lam_u) for a, L in O.COUCHES])
for i in range(3):
    NUM(f"gpd{i+1}", gp[i])
# vérification numérique de la formule fermée
S_ = lambda t: lam_u * (1 + xi * (t - u) / beta) ** (-1 / xi)
assert abs(integrate.quad(S_, 1e6, 2e6)[0] - O.prix_gpd(1e6, 1e6, u, xi, beta, lam_u)) < 1.0
thr = []
for k, uu in enumerate([3e5, 5e5, 1e6]):
    xi_u, b_u, n_u = O.ajuster_gpd(sg, uu)
    lam_uu = O.taux_depassement(sg, uu)
    thr.append(O.prix_gpd(2e6, 2e6, uu, xi_u, b_u, lam_uu))
    if uu == 3e5: NUM("xi3", xi_u)
    if uu == 1e6: NUM("xi10", xi_u); NUM("n10", n_u)
    NUM(f"thr{k+1}", thr[-1])
assert O.ajuster_gpd(sg, 1e6)[0] < 0
O.fig_gpd(sg)
```

Mettons toutes les estimations côte à côte, en M€ par an au niveau de 2025.

| Tranche | *Burning cost* brut | *Burning cost* ajusté | Fréquence × sévérité | GPD (seuil 500 000) | **Vérité** |
|---|---:|---:|---:|---:|---:|
| 0,5 M€ xs 0,5 M€ | {{bc_raw1|M2}} | {{bc_adj1|M2}} | {{fs1|M2}} | {{gpd1|M2}} | **{{vrai1|M2}}** |
| 1 M€ xs 1 M€ | {{bc_raw2|M2}} | {{bc_adj2|M2}} | {{fs2|M2}} | {{gpd2|M2}} | **{{vrai2|M2}}** |
| 2 M€ xs 2 M€ | {{bc_raw3|M2}} | {{bc_adj3|M2}} | {{fs3|M2}} | {{gpd3|M2}} | **{{vrai3|M2}}** |

Trois remarques. La correction d'exposition est **indispensable** : le brut est loin de tout le reste. Les trois estimations corrigées sont **voisines** entre elles : elles utilisent les mêmes données, donc partagent les mêmes aléas. Et elles sont **toutes en dessous** de la vérité sur la tranche haute. Est-ce un biais de méthode ou la malchance de ces quinze années ? C'est la question de la section suivante.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.4 et 6.5 et exercices 6.8 à 6.10.

### 6.2.4 Mesurer l'incertitude : le même tarif aurait pu être très différent

Nos quinze années d'observation sont **un tirage parmi beaucoup d'autres possibles**. Pour mesurer l'incertitude d'une estimation, on veut savoir ce qu'elle serait sur d'autres tirages. On en a deux moyens.

**Le bootstrap par années.** On rééchantillonne les **années** (avec remise) : chaque année est une observation de la charge annuelle de la tranche. On refait le calcul du *burning cost* sur chaque rééchantillon, et l'on lit un intervalle de 2,5 % à 97,5 %. On rééchantillonne des années entières et non des sinistres, parce que les sinistres d'une même année partagent la même exposition. Voici l'intervalle pour les trois tranches :

| Tranche | Estimation ajustée | Intervalle à 95 % (bootstrap) | Largeur relative |
|---|---:|---|---:|
| 0,5 M€ xs 0,5 M€ | {{bc_adj1|M2}} M€ | de {{lo1|M2}} à {{hi1|M2}} | ± {{lar1|pc0}} % |
| 1 M€ xs 1 M€ | {{bc_adj2|M2}} M€ | de {{lo2|M2}} à {{hi2|M2}} | ± {{lar2|pc0}} % |
| 2 M€ xs 2 M€ | {{bc_adj3|M2}} M€ | de {{lo3|M2}} à {{hi3|M2}} | ± {{lar3|pc0}} % |

L'incertitude **grandit à mesure que l'on monte**, parce que la tranche haute est touchée par peu de sinistres : dans l'historique, seuls {{n2m|int}} sinistres dépassent 2 M€. La vérité, qui reste dans les trois intervalles ici, n'y serait pas **forcément** : « 95 % » n'est pas « toujours ».

**Rejouer l'expérience sous la vérité.** Puisque nous connaissons la loi qui a produit les données, nous pouvons refaire **300 fois** l'aventure « quinze années d'observation », calculer chaque fois le *burning cost* ajusté, et regarder la dispersion. C'est un luxe de simulation : en vrai, on n'a qu'une histoire.

| Tranche | Moyenne des 300 estimations | Coefficient de variation | Part des estimations sous la vérité |
|---|---:|---:|---:|
| 0,5 M€ xs 0,5 M€ | {{rep_m1|M2}} M€ | {{rep_cv1|pc0}} % | {{rep_b1|pc0}} % |
| 1 M€ xs 1 M€ | {{rep_m2|M2}} M€ | {{rep_cv2|pc0}} % | {{rep_b2|pc0}} % |
| 2 M€ xs 2 M€ | {{rep_m3|M2}} M€ | {{rep_cv3|pc0}} % | {{rep_b3|pc0}} % |

La moyenne des estimations est **voisine de la vérité** : la méthode corrigée de l'exposition n'est pas biaisée. Mais son **erreur typique** est de {{rep_cv1|pc0}} %, {{rep_cv2|pc0}} % et {{rep_cv3|pc0}} % : une erreur de {{err_adj3|pc0}} % sur la tranche haute (celle de notre échantillon) est donc banale, de l'ordre d'un écart-type. Le réassureur et la cédante qui s'accordent sur le prix de la tranche haute se mettent d'accord sur un chiffre dont l'incertitude est **du même ordre que le chargement qu'ils négocient**.

![Estimations de la charge annuelle de chaque tranche : *burning cost* brut (gris), ajusté avec son intervalle bootstrap (bleu), GPD (violet). La ligne orange est la vérité.](figures/ch06-tranches.png)

```python hide
bo = {}
for i, (a, L) in enumerate(O.COUCHES):
    b = O.bootstrap_annees(sg, a, L)
    lo, hi = np.percentile(b, [2.5, 97.5])
    bo[i] = (lo, hi)
    NUM(f"lo{i+1}", lo); NUM(f"hi{i+1}", hi); NUM(f"lar{i+1}", (hi - lo) / 2 / adj_[i])
    assert lo < vrai_[i] < hi
adj_rep, brut_rep = O.rejouer_experience(B=300, seed=99)
for i in range(3):
    NUM(f"rep_m{i+1}", adj_rep[:, i].mean()); NUM(f"rep_cv{i+1}", adj_rep[:, i].std() / adj_rep[:, i].mean())
    NUM(f"rep_b{i+1}", (adj_rep[:, i] < vrai_[i]).mean())
    assert abs(adj_rep[:, i].mean() / vrai_[i] - 1) < 0.05
assert (brut_rep.mean(axis=0) < 0.9 * vrai_).all()
O.fig_tranches(sg)
```

> 💡 **Une prime est une estimation.** Le « prix » d'une tranche haute est, avec 15 ans de données, une fourchette large. Les réassureurs le savent : c'est pourquoi les tranches hautes se tarifient avec des **modèles**, des **hypothèses prudentes** et des **chargements**, et pas avec la seule moyenne observée.

### 6.2.5 Les catastrophes : peu de données, beaucoup d'incertitude

Pour les catastrophes, l'historique est encore plus mince : **{{cat_ev|int}} événements en 40 ans**. Le tarif d'une tranche de catastrophe repose sur le **modèle de queue** presque seul.

Nous ajustons une loi de Pareto $P(X>x)=(x_m/x)^{\alpha}$ aux pertes des années à événement, avec un minimum $x_m=2$ M€ (la plus petite perte observée vaut {{cat_min|M2}} M€). L'estimateur du maximum de vraisemblance de $\alpha$ est $\hat\alpha=n/\sum\ln(x_i/x_m)$, soit ici {{alpha_hat|2}}, et la fréquence des années à événement vaut {{p_hat|pc1}} %. Le tableau compare l'estimation empirique, la loi ajustée et la vérité, pour trois tranches.

| Tranche | Empirique | Pareto ajusté | Vérité | Intervalle bootstrap |
|---|---:|---:|---:|---|
| 5 M€ xs 5 M€ | {{c_emp1|M2}} | {{c_par1|M2}} | **{{c_vrai1|M2}}** | {{c_lo1|M2}} à {{c_hi1|M2}} |
| 10 M€ xs 10 M€ | {{c_emp2|M2}} | {{c_par2|M2}} | **{{c_vrai2|M2}}** | {{c_lo2|M2}} à {{c_hi2|M2}} |
| 20 M€ xs 20 M€ | {{c_emp3|M2}} | {{c_par3|M2}} | **{{c_vrai3|M2}}** | {{c_lo3|M2}} à {{c_hi3|M2}} |

L'intervalle de la tranche « 10 M€ xs 10 M€ » commence à **zéro** : certains rééchantillonnages de 40 ans n'ont aucune perte dans la tranche. Sur 40 ans, la loi ajustée sous-estime la queue ($\hat\alpha={{alpha_hat|2}}$ contre une vérité de 1,11) : l'exposant est surestimé, la queue paraît plus légère, les tranches hautes sont sous-tarifées, et la méthode empirique se trompe dans le même sens. Avec {{cat_ev|int}} points, un écart de cette taille est banal : **les observations de pertes extrêmes sont rares par nature**, et un échantillon court ne contient en général pas la pire perte possible.

![À gauche, la queue des pertes d'événement (échelle logarithmique) : observations, loi ajustée et vérité. À droite, la charge annuelle de trois tranches de catastrophe selon la méthode.](figures/ch06-cat.png)

Pour une tranche de catastrophe, on parle plutôt en **ROL** qu'en pourcentage de prime. Si la tranche « 10 M€ xs 10 M€ » est vendue à son prix pur de {{c_vrai2|M2}} M€, son ROL est de {{rol10|pc1}} %, soit une période de retour de {{pb10|0}} ans : pendant ce temps, la cédante paie chaque année, et ne récupère l'équivalent d'une portée entière, en moyenne, qu'une fois en {{pb10|0}} ans. Le réassureur n'a guère plus d'information que nous : il s'appuie sur des **modèles de catastrophe** (physiques ou statistiques), hors du champ de cet ouvrage.

```python hide
alpha_hat, p_hat = O.pareto_cat(cat)
NUM("alpha_hat", alpha_hat); NUM("p_hat", p_hat); NUM("cat_min", c[c > 0].min())
tc, _, _ = O.calcul_cat(cat)
for i, r in tc.iterrows():
    for k, nom in [("empirique", "c_emp"), ("pareto", "c_par"), ("vrai", "c_vrai"), ("ic_bas", "c_lo"), ("ic_haut", "c_hi")]:
        NUM(f"{nom}{i+1}", r[k] * 1e6)
assert tc.loc[1, "ic_bas"] < 0.01 and alpha_hat > 1 / 0.9
NUM("rol10", O.prix_vrai_cat(1e7, 1e7) / 1e7); NUM("pb10", 1e7 / O.prix_vrai_cat(1e7, 1e7))
O.fig_cat(cat)
```

> ⚠️ **Quand les données manquent, le chargement n'est pas un luxe.** Une tranche de catastrophe dont l'espérance est connue à un facteur deux près se vend nécessairement avec un chargement important : il rémunère l'incertitude du réassureur autant que son risque.

### 6.2.6 De la prime pure à la prime technique

La prime pure est l'espérance de la charge. Le prix facturé par le réassureur, la **prime technique**, ajoute un **chargement** qui couvre les frais, le coût du capital et la marge. Deux principes classiques, tous deux **illustratifs** ici (les paramètres sont ceux d'un exemple, pas ceux d'un marché) :

- **Le principe de l'écart-type** : $\pi=E[S]+k\,\sigma(S)$, où $S$ est la charge annuelle de la tranche et $k$ un coefficient d'aversion (nous prenons $k=0{,}15$).
- **Le principe du coût du capital** : le réassureur immobilise un capital $K$ pour porter le risque (la perte inattendue à 99,5 %, $K=\mathrm{VaR}_{99{,}5\,\%}(S)-E[S]$, voir section 3.1) et exige un rendement de $i$ sur ce capital : $\pi=E[S]+i\,K$ (nous prenons $i=8\,\%$).

Pour les calculer, il faut la **distribution** de la charge annuelle de la tranche, pas seulement sa moyenne. Nous la simulons (20 000 années, nombre de sinistres de Poisson, montants tirés sous la loi des sinistres) :

| Tranche | Espérance | Écart-type | VaR à 99,5 % | Capital $K$ | Prime (écart-type) | Prime (coût du capital) |
|---|---:|---:|---:|---:|---:|---:|
| 1 M€ xs 1 M€ | {{l_e1|M2}} M€ | {{l_s1|M2}} M€ | {{l_v1|M2}} M€ | {{l_k1|M2}} M€ | {{l_ps1|M2}} M€ (+{{l_cs1|pc0}} %) | {{l_pc1|M2}} M€ (+{{l_cc1|pc0}} %) |
| 2 M€ xs 2 M€ | {{l_e2|M2}} M€ | {{l_s2|M2}} M€ | {{l_v2|M2}} M€ | {{l_k2|M2}} M€ | {{l_ps2|M2}} M€ (+{{l_cs2|pc0}} %) | {{l_pc2|M2}} M€ (+{{l_cc2|pc0}} %) |

Plus la tranche est haute, plus le **risque relatif** est grand (l'écart-type est supérieur à l'espérance pour la tranche « 2 M€ xs 2 M€ »), donc plus le chargement relatif l'est aussi. Un chargement unique, exprimé en pourcentage de la prime pure, ne peut pas convenir aux deux tranches : il faut ajouter {{l_cs1|pc0}} % à la première et {{l_cs2|pc0}} % à la seconde avec le principe de l'écart-type, ou {{l_cc1|pc0}} % et {{l_cc2|pc0}} % avec le coût du capital. Le chargement suit le **risque**, pas la prime.

Reste le coût des **réintégrations** et d'éventuelles **commissions** de courtage, qui s'ajoutent à la prime technique. Le prix final n'est donc pas une simple « moyenne plus dix pour cent » : c'est un compromis entre le modèle du réassureur, son appétit, son capital disponible et la concurrence du moment.

```python hide
for i, (a, L) in enumerate(O.COUCHES[1:], start=1):
    ch = O.charge_annuelle_vraie(a, L)
    E, sd, v = ch.mean(), ch.std(), np.percentile(ch, 99.5)
    K = v - E
    ps, pc_ = E + 0.15 * sd, E + 0.08 * K
    for nom, val in [("l_e", E), ("l_s", sd), ("l_v", v), ("l_k", K), ("l_ps", ps), ("l_pc", pc_), ("l_cs", ps / E - 1), ("l_cc", pc_ / E - 1)]:
        NUM(f"{nom}{i}", val)
    assert abs(E / O.prix_vrai(a, L) - 1) < 0.05
    if i == 2: assert sd > E
```

> ✅ **À retenir.** La prime pure d'une tranche s'estime par l'expérience (*burning cost*, **à ajuster de l'exposition et de l'inflation**, qui s'amplifie dans les tranches), par une loi de queue (GPD), ou par l'exposition (courbe d'exposition) ; ces méthodes se comparent mais partagent les mêmes données. Pour les tranches hautes et les catastrophes, l'incertitude est **du même ordre que le chargement** : il faut la mesurer (bootstrap) et l'annoncer. La prime technique ajoute un chargement proportionnel au **risque** (écart-type, coût du capital), pas à la prime pure.

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : applications 6.3 à 6.8, exercices 6.6 à 6.12.
