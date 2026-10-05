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
