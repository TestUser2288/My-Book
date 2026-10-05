## 6.6 ➕ Pour aller plus loin : les copules et la modélisation de la dépendance

> 🧭 **Section optionnelle.** Elle suppose les lois jointes et la corrélation (volume I, chapitre 2), la simulation par inversion (6.2.4) et, pour la fin, l'estimation par maximum de vraisemblance. Elle ne dépend pas des sections 6.3 à 6.5.

> 💡 **Intuition.** Deux transporteurs livrent les colis de la boutique. Chacun a ses propres retards, parfois très longs. Mais le vrai risque pour la gérante n'est pas qu'*un* transporteur ait un mauvais jour : c'est que **les deux aient un très mauvais jour en même temps** (un jour de grève, de tempête, de veille de fête), car alors elle n'a plus de solution de repli. Ce risque ne dépend pas seulement de la loi de chaque transporteur (les « lois marginales »), mais de la façon dont ils sont **liés** : de la **structure de dépendance**. La corrélation ne la résume pas : deux paires de variables peuvent avoir la même corrélation et des comportements extrêmes opposés. Une **copule** isole cette structure de dépendance, séparément des marginales, et permet de la modéliser.

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

**Le vrai problème : deux transporteurs en même temps.** Revenons à notre inquiétude. La gérante observe depuis 1 500 jours les retards moyens de ses deux transporteurs (simulés ici ; graine 683). Le transporteur A a des retards (en jours) de marginale Pareto généralisée décalée de 1, $\xi=0{,}25$, $\sigma=1{,}5$ ; le B de $\xi=0{,}20$, $\sigma=2$. **La vraie dépendance** (que la gérante ignore) est une copule de Clayton **retournée** de $\theta=1{,}5$ : les deux transporteurs sont **simultanément très en retard** bien plus souvent que ne le laisserait croire une dépendance gaussienne. Elle ajuste les deux familles et calcule la probabilité qu'*un même jour*, les deux retards dépassent leur propre 99ᵉ centile.

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

C'est la leçon centrale de cette section. À marginales identiques et à dépendance **globale** identique (même tau), la copule gaussienne ajustée prévoit des doubles retards extrêmes **3,3 fois moins fréquents** que la vérité : un jour sur 518 contre un jour sur 159. Pour la gérante, c'est la différence entre « un tel jour tous les 17 mois » et « un tel jour tous les 5 mois ». Et par rapport à l'indépendance (un jour sur 10 000), les deux modèles de dépendance annoncent un risque 19 à 63 fois plus grand : ignorer la dépendance serait bien pire encore. La Clayton retournée ajustée (un jour sur 163) est quasiment sur la vérité (un jour sur 159). Ce calcul est essentiellement un calcul de **queue conjointe**, et il dépend presque entièrement du **choix de la copule**, pas des marginales. (L'observation directe sur 1 500 jours ne contient que 8 jours de ce type, soit une fréquence de 0,53 % : le modèle de Clayton en prévoyait 9,2, la copule gaussienne 2,9. Huit événements, c'est peu pour trancher à eux seuls, ce qui illustre pourquoi on **modélise** la dépendance plutôt que de compter les événements rares.)

> ⚠️ **Limites.** (1) **La dépendance de queue est très difficile à estimer** : elle repose sur les quelques points extrêmes. Choisir une famille par la vraisemblance globale (qui est dominée par le centre des données) n'est pas une garantie sur les queues. (2) Les copules à un paramètre ont une forme de dépendance rigide ; pour **plus de deux variables**, on utilise des « vines » (lianes de copules à deux variables), et des modèles plus riches. (3) La dépendance peut **changer avec le temps** (les périodes de crise ont leur propre structure) : le modèle estimé sur une période calme est silencieux sur la crise. (4) Les copules décrivent une **association**, pas une causalité (volume III).

> ✅ **À retenir (6.6).**
> - La corrélation de Pearson ne capture que la dépendance linéaire ; le **tau de Kendall** et le **rho de Spearman** sont des mesures de **rang**, invariantes par transformation croissante.
> - **Théorème de Sklar** : toute loi jointe $=$ des **marginales** $+$ une **copule** ($H=C(F,G)$). On modélise séparément les deux.
> - La copule est la loi jointe des **rangs normalisés** $U=F(X)$ (transformation intégrale de probabilité).
> - **Gaussienne** : pas de dépendance de queue. **Clayton** : dépendance de queue inférieure ($\lambda_L=2^{-1/\theta}$) ; sa version **retournée** donne une dépendance de queue supérieure.
> - On estime une copule sur des **pseudo-observations** (rangs divisés par $n+1$), par inversion du tau ou maximum de vraisemblance ; on **valide la procédure sur des données simulées** de copule connue.
> - **À même tau, des copules différentes ont des comportements extrêmes très différents** : la probabilité d'événements simultanément rares dépend presque uniquement de la copule. C'est le risque principal d'un choix par défaut (gaussien).
