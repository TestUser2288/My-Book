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

Huit fléchettes sur dix sont dedans : $\hat\pi=4\times0{,}8=3{,}2$. Pas très précis, mais l'idée est là. Laissons maintenant l'ordinateur lancer un million de fléchettes. L'estimateur de Monte-Carlo tient en trois lignes :

```python
rng = np.random.default_rng(640)
xy = rng.random((1_000_000, 2))                        # un million de fléchettes dans le carré
print(4 * ((xy**2).sum(axis=1) < 1).mean())            # 4 fois la proportion dans le quart de disque
```
<!--sortie-->
```text
3.140556
```
Avec un million de fléchettes, on trouve $3{,}1406$ : l'erreur est de l'ordre du millième (le chiffre exact dépend de la graine du générateur).

```python hide
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

En faisant varier le nombre de fléchettes $n$, l'estimation s'approche de $\pi$, **sans jamais être exacte** :

| $n$ | estimation | erreur | écart-type théorique de l'estimateur |
|---:|---:|---:|---:|
| 100 | 3,12000 | −0,02159 | 0,16422 |
| 1 000 | 3,15200 | 0,01041 | 0,05193 |
| 10 000 | 3,13000 | −0,01159 | 0,01642 |
| 100 000 | 3,13760 | −0,00399 | 0,00519 |
| 1 000 000 | 3,14366 | 0,00207 | 0,00164 |

Mais à quelle vitesse l'erreur décroît-elle ? C'est la question suivante.

### 6.2.2 La vitesse de convergence : $1/\sqrt n$

Chaque terme $g(X_i)$ est une variable aléatoire de variance $\sigma^2=\mathrm{Var}(g(X))$. L'estimateur $\hat\theta_n$ est sans biais, et, puisque les $X_i$ sont indépendants (volume I, section 2.3) :
$$\mathrm{Var}(\hat\theta_n)=\frac{\sigma^2}{n},\qquad\text{donc}\qquad \text{erreur type}=\frac{\sigma}{\sqrt n}.$$
Le théorème central limite (volume I, section 2.4) dit en plus que, pour $n$ grand, $\hat\theta_n\approx\mathcal N(\theta,\sigma^2/n)$ : on obtient donc un **intervalle de confiance** de Monte-Carlo, $\hat\theta_n\pm1{,}96\,\hat\sigma/\sqrt n$, où $\hat\sigma$ est l'écart-type empirique des $g(X_i)$. Pour $\pi$, $g=4\cdot\mathbf 1\{\dots\}$ est une variable qui vaut 4 avec la probabilité $p=\pi/4$ et 0 sinon, d'où $\sigma^2=16\,p(1-p)=\pi(4-\pi)$ : c'est la formule utilisée dans le code ci-dessus.

**Conséquence pratique.** Pour **diviser l'erreur par 10**, il faut **100 fois plus de simulations**. Pour gagner une décimale de précision, 100 fois plus de calcul. C'est lent. Vérifions-le par une expérience : pour chaque $n$, on répète 300 fois l'estimation de $\pi$ et on mesure l'écart-type observé des estimations. Résultat :

| $n$ | écart-type observé | théorie $\sigma/\sqrt n$ |
|---:|---:|---:|
| 100 | 0,16832 | 0,16422 |
| 1 000 | 0,05164 | 0,05193 |
| 10 000 | 0,01591 | 0,01642 |
| 100 000 | 0,00503 | 0,00519 |

```python hide
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

La pente de $\log(\text{écart-type})$ en fonction de $\log n$ vaut $-0{,}508$, presque exactement $-1/2$ : doubler le nombre de chiffres décimaux coûte un facteur $10^4$ en simulations.

```python hide
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

> 💡 **Pourquoi utiliser une méthode si lente ?** En dimension 1, une méthode déterministe (les rectangles du volume I, section 1.2) est bien plus efficace : l'erreur de la règle des trapèzes décroît comme $1/n^2$. Mais la vitesse $1/\sqrt n$ de Monte-Carlo a une propriété extraordinaire : **elle ne dépend pas de la dimension**. Un quadrillage de 10 points par axe demande $10^{d}$ évaluations en dimension $d$ ; Monte-Carlo, lui, garde le même rythme. Illustration : le volume de la boule unité en dimension 10, dont la valeur exacte est $\pi^{5}/5!\approx2{,}5502$. On tire un million de points dans le cube $[-1,1]^{10}$ (de volume $2^{10}$) et on compte ceux qui tombent dans la boule : l'estimation vaut $2{,}602\pm0{,}101$ (intervalle à 95 %), compatible avec la valeur exacte. Un quadrillage de 10 points par axe aurait demandé dix milliards d'évaluations.

```python hide
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

### 6.2.3 Propager toute l'incertitude jusqu'à une décision

En 6.1.4, nous avons montré que l'offre de bienvenue augmente la probabilité de rachat d'environ 12 points. Mais elle **coûte** quelque chose : la remise accordée. Faut-il l'offrir à tous les futurs clients ?

Posons les hypothèses de l'étude (inventées pour l'exercice, à remplacer par les vraies valeurs de la boutique) :
- la marge de la gérante est de **30 %** du panier ;
- l'offre coûte **1,50 € par client** (la remise, quel que soit le client) ;
- un client qui rachète génère un panier tiré au hasard parmi les paniers des acheteurs observés (la distribution empirique, qui est notre meilleure image de la loi des paniers).

Le gain net **par client** de la politique « envoyer l'offre » vaut donc
$$G=(\theta_1-\theta_0)\times m-c,\qquad m=0{,}30\times\text{panier moyen d'un acheteur},\quad c=1{,}50.$$
Les inconnues sont $\theta_1,\theta_0$ (nous avons leurs lois a posteriori, 6.1.4) et $m$ (nous le « simulons » par rééchantillonnage des paniers observés, c'est un bootstrap). Monte-Carlo permet de propager **toute** l'incertitude jusqu'au résultat, ce qu'aucune formule simple ne ferait. Concrètement, on fabrique 100 000 « scénarios » : dans chacun, on tire $\theta_1$ et $\theta_0$ dans leurs lois a posteriori, une marge moyenne $m$ par rééchantillonnage des paniers, et on calcule $G$. La distribution des $G$ est la réponse. Avec une marge moyenne de 18,37 € par rachat (panier moyen des acheteurs : 61,23 €) :

```python hide
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

print(f"marge moyenne par rachat : {marge * paniers.mean():.2f} € (panier moyen des acheteurs : {paniers.mean():.2f} €)")
print(f"gain net moyen par client : {G.mean():+.3f} €")
print(f"intervalle à 90 %         : [{np.percentile(G, 5):+.3f} ; {np.percentile(G, 95):+.3f}] €")
print(f"P(l'offre est rentable)   : {(G > 0).mean():.3f}")
print(f"pour 5 000 nouveaux clients : gain attendu {5000 * G.mean():+.0f} € ; "
      f"dans 95 % des scénarios le gain dépasse {5000 * np.percentile(G, 5):+.0f} €")
```
<!--sortie-->
```text
marge moyenne par rachat : 18.37 € (panier moyen des acheteurs : 61.23 €)
gain net moyen par client : +0.731 €
intervalle à 90 %         : [+0.062 ; +1.400] €
P(l'offre est rentable)   : 0.964
pour 5 000 nouveaux clients : gain attendu +3656 € ; dans 95 % des scénarios le gain dépasse +312 €
```

Le calcul donne un gain net moyen de $+0{,}731$ € par client (intervalle à 90 % : [+0,062 ; +1,400] €), une probabilité de 0,964 que l'offre soit rentable, et, pour 5 000 nouveaux clients, un gain attendu de +3 656 € (dépassant +312 € dans 95 % des scénarios). C'est le genre de réponse qu'attend vraiment une décisionnaire : pas « l'effet est significatif » mais « *l'offre est très probablement rentable (environ 96 % de chances), le gain attendu est de 0,73 € par client, soit 3 700 € pour 5 000 clients, et dans 95 % des scénarios on gagne au moins 300 €* ». Remarquez que le gain par client reste **modeste** et que l'intervalle à 90 % ([+0,06 ; +1,40] €) s'approche de zéro : l'offre n'est pas une mine d'or, et un coût de 2 € (au lieu de 1,50) la rendrait douteuse. Les chiffres de coût et de marge étant inventés, la bonne pratique est de refaire le calcul pour plusieurs valeurs. Observez aussi que **toutes** les sources d'incertitude (les deux taux, la marge) sont propagées d'un seul mouvement, simplement en les simulant ensemble.

> 🧪 **Point de rigueur.** Le calcul suppose que l'effet de l'offre sur le rachat se traduit, pour chaque client qui rachète en plus, par un panier « moyen ». Dans les données simulées, l'offre agit sur la *probabilité* de rachat (c'est vrai par construction) ; une vraie étude vérifierait aussi si les clients « incités » dépensent autant que les autres. Un modèle ne répond qu'à la question qu'on lui a posée.

### 6.2.4 Fabriquer des tirages : l'inversion et le rejet

Jusqu'ici, nous avons utilisé `rng.random`, `stats.beta.rvs`, etc., comme des boîtes noires. Comment un ordinateur fabrique-t-il un tirage dans une loi donnée ? Voici les deux méthodes de base, qui expliquent aussi pourquoi les lois *a posteriori* compliquées posent problème.

**Méthode 1 : l'inversion.** On part d'une loi uniforme $U\sim\mathcal U(0,1)$, que l'ordinateur sait fabriquer.

> 📐 **Théorème (inversion).** Soit $F$ une fonction de répartition continue et strictement croissante, d'inverse $F^{-1}$. Alors $X=F^{-1}(U)$ a pour fonction de répartition $F$.
>
> *Démonstration.* Pour tout $x$, $P(X\le x)=P(F^{-1}(U)\le x)=P(U\le F(x))=F(x)$, car $F$ est croissante et $P(U\le u)=u$ pour $u\in[0,1]$. $\square$

*Exemple.* Le délai d'attente d'un colis suit une loi exponentielle de moyenne 3 jours, $F(x)=1-e^{-x/3}$. En résolvant $u=1-e^{-x/3}$ : $x=-3\ln(1-u)$. On simule donc des délais avec `-3 * np.log(1 - u)`, où `u` est un tirage uniforme. Avec 100 000 tirages, la moyenne simulée est 3,007 (théorie : 3) et l'écart-type 3,001 (théorie : 3) ; la probabilité simulée d'un délai de 3 jours au plus est 0,6311, contre 0,6321 exactement.

```python hide
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

*Exemple.* Simulons la loi a posteriori $\mathrm{Beta}(8,4)$ de 6.1 avec une proposition uniforme sur $[0,1]$ ($g=1$). Il faut $M\ge\max f$ : le maximum de la densité est atteint en $\theta=(8-1)/(8+4-2)=0{,}7$ et vaut $M\approx2{,}9351$, d'où une probabilité d'acceptation théorique $1/M=0{,}3407$. Sur 200 000 essais, le taux d'acceptation observé est 0,3428 (68 564 tirages conservés), la moyenne des tirages conservés 0,6665 (exacte : 0,6667) et leur écart-type 0,1305 (exact : 0,1307).

```python hide
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

```python hide
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
> qui vaut $n$ si toutes les contributions sont égales et 1 si un seul tirage porte tout. Nous retrouverons cette idée d'ESS en 6.4. Faisons varier le centre $c$ de la proposition $h=\mathcal N(c,1)$ (le cas $c=0$ est la méthode naïve), avec 300 répétitions de 10 000 tirages :

| centre $c$ | part de tirages $>4$ | ESS moyenne | écart-type de l'estimateur | erreur relative |
|---:|---:|---:|---:|---:|
| 0 | 0,0000 | 0,3 | $6{,}16\times10^{-5}$ | 1,946 |
| 2 | 0,0228 | 187,1 | $2{,}34\times10^{-6}$ | 0,074 |
| 3 | 0,1584 | 965,9 | $1{,}04\times10^{-6}$ | 0,033 |
| **4** | 0,4996 | **1 814,0** | $6{,}81\times10^{-7}$ | **0,022** |
| 5 | 0,8413 | 1 235,0 | $8{,}03\times10^{-7}$ | 0,025 |
| 6 | 0,9771 | 304,9 | $1{,}68\times10^{-6}$ | 0,053 |
| 8 | 1,0000 | 3,2 | $3{,}53\times10^{-5}$ | 1,114 |

```python hide
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

| méthode | moyenne | biais | écart-type | gain de variance |
|---|---:|---:|---:|---:|
| naïf | 0,747244 | 0,000420 | 0,006639 | 1 |
| antithétique | 0,746821 | −0,000003 | 0,001311 | 25,6 |
| variable de contrôle | 0,746816 | −0,000008 | 0,000942 | 49,7 |
| stratifié | 0,746838 | 0,000013 | 0,000645 | 105,9 |

```python hide
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

Exemple : la **médiane** du panier des acheteurs acquis par le canal Boutique (une statistique sans formule d'erreur simple). Sur 449 acheteurs, la médiane observée est 67,92 € ; le bootstrap classique donne un intervalle à 95 % de [64,62 ; 70,61] (écart-type 1,56), le bootstrap bayésien [64,66 ; 70,61] (écart-type 1,55), pratiquement le même.

```python hide
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

print(f"{n_b} acheteurs de la boutique ; médiane observée : {np.median(boutique):.2f} €")
print(f"bootstrap classique : IC95 [{np.percentile(med_boot, 2.5):.2f} ; {np.percentile(med_boot, 97.5):.2f}]  (écart-type {med_boot.std():.2f})")
print(f"bootstrap bayésien  : IC95 [{np.percentile(med_bayes, 2.5):.2f} ; {np.percentile(med_bayes, 97.5):.2f}]  (écart-type {med_bayes.std():.2f})")
```
<!--sortie-->
```text
449 acheteurs de la boutique ; médiane observée : 67.92 €
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

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.2, exercices 6.5 à 6.7.
