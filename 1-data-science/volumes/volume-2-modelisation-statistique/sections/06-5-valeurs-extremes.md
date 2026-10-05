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
