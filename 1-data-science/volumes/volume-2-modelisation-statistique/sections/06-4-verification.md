## 6.4 Vérification des modèles bayésiens

> 💡 **Intuition.** Un pilote ne décolle pas sans sa liste de contrôle : carburant, volets, instruments. Un analyste bayésien devrait faire de même, car **deux choses peuvent tourner mal**, et elles sont indépendantes : (1) *l'algorithme* peut avoir mal exploré la loi a posteriori (la chaîne n'a pas convergé), et (2) *le modèle* peut être faux (la loi a posteriori, même parfaitement calculée, répond à une question mal posée). Nous avons vu un exemple de la seconde en 6.1.8 : un modèle de Poisson aux intervalles trop étroits. Cette section donne les outils pour détecter l'une et l'autre.

Dans tout ce qui suit, un échantillon MCMC n'est jamais « bon par nature » : on **démontre** qu'il est bon, ou du moins qu'il ne manifeste aucun signe de mauvaise santé. Un diagnostic qui passe ne prouve pas la convergence (on ne peut jamais prouver qu'une chaîne a tout exploré), mais un diagnostic qui échoue prouve un problème.

### 6.4.1 L'algorithme a-t-il convergé ? Les diagnostics de convergence

Nous reprenons les quatre chaînes de la régression logistique de 6.3.5, lancées depuis des points de départ **dispersés**. Le premier diagnostic, et le plus parlant, est le dessin : la **trace** de chaque chaîne, et la distribution des valeurs prises, chaîne par chaîne.

```python hide
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

```python hide
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
  Réseaux                       1.0022                       1.0037 1158
     Site                       1.0043                       1.0024 1205
```

Le tableau suivant donne le $\widehat R$ de chaque coefficient, avec et sans la chauffe, et l'ESS totale :

| coefficient | $\widehat R$ (chauffe incluse) | $\widehat R$ (chauffe écartée) | ESS |
|---|---:|---:|---:|
| constante | 1,0037 | 1,0010 | 1 281 |
| offre | 1,0064 | 1,0023 | 1 276 |
| âge | **1,0163** | 1,0009 | 1 114 |
| Réseaux | 1,0022 | 1,0037 | 1 158 |
| Site | 1,0043 | 1,0024 | 1 205 |

Deux enseignements. D'abord, **écarter la chauffe améliore le diagnostic** : en gardant les 1 000 premières itérations, le $\widehat R$ de l'âge est de 1,016 (au-dessus du seuil de 1,01) ; une fois la chauffe retirée, les cinq $\widehat R$ sont inférieurs à 1,004 : les quatre chaînes disent la même chose. (L'effet est modeste ici parce que la loi est presque gaussienne et que la chaîne s'y installe vite ; dans un modèle plus difficile, la chauffe peut faire la différence entre $\widehat R=1{,}5$ et $\widehat R=1{,}00$.) Ensuite, les **ESS** sont de l'ordre de 1 100 à 1 300 : pour estimer une moyenne ou un intervalle de crédibilité à 95 %, la règle usuelle est de viser au moins 400 à 1 000 ; nous sommes dans la fourchette. (Pour des quantiles extrêmes, il en faut davantage.)

> ⚠️ **Ce que l'ESS que nous calculons simplifie.** Nous additionnons les ESS de chaque chaîne. Les logiciels (Stan, ArviZ) utilisent une version qui combine les autocorrélations de toutes les chaînes et des transformations par rangs : elle est plus fiable pour les lois à queues lourdes. Pour nos besoins, l'ordre de grandeur est le même.

**Que se passe-t-il quand la convergence échoue ?** Un diagnostic n'a de valeur que si on a vu au moins une fois à quoi il ressemble quand il détecte quelque chose. Prenons une loi cible à **deux bosses**, mélange à parts égales de $\mathcal N(-4,1)$ et $\mathcal N(4,1)$ (moyenne exacte : 0), et lançons quatre chaînes de Metropolis de points de départ $-6,-2,2,6$, avec un pas petit (0,5) puis grand (6) :

| pas | moyennes des 4 chaînes | moyenne globale | $\widehat R$ | ESS |
|---:|---|---:|---:|---:|
| 0,5 | −4,08 ; 3,71 ; 4,06 ; 3,92 | 1,90 | **3,072** | 546 |
| 6,0 | −0,16 ; 0,16 ; −0,28 ; 0,17 | −0,03 | 1,002 | 1 430 |

```python hide
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

**Retour sur le modèle de Poisson de 6.1.8.** Nous avions modélisé le nombre de commandes annuelles `nb_commandes_an` des 504 clients acquis par le canal Boutique par une loi de Poisson de paramètre $\lambda$ commun, et obtenu l'a posteriori $\mathrm{Gamma}(2087;\ 504{,}5)$. Il avait l'air parfait : un intervalle étroit. Soumettons-le à la vérification : on tire 2 000 valeurs de $\lambda$ dans cet a posteriori, on simule pour chacune un jeu de 504 comptages de Poisson, et on compare trois statistiques de ces jeux répliqués aux valeurs observées.

| statistique | observée | répliques : moyenne | répliques : 2,5 % – 97,5 % | $p$ bayésien |
|---|---:|---:|---|---:|
| variance / moyenne | 3,324 | 1,000 | [0,879 ; 1,127] | 0,0 |
| part de zéros | 0,109 | 0,016 | [0,006 ; 0,030] | 0,0 |
| maximum | 21 | 11,541 | [10 ; 14] | 0,0 |

```python hide
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

```python hide
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

Les chaînes sont saines (taux d'acceptation de 0,35 à 0,37 ; $\widehat R$ de 1,0029 pour $\log\mu$ et 1,0019 pour $\log k$ ; ESS de 1 951 et 2 241). L'a posteriori de la moyenne est de 4,134 (intervalle à 95 % [3,817 ; 4,457]) ; la dispersion $k$ a pour médiane 1,817 (intervalle [1,513 ; 2,199]), loin de l'infini de Poisson. Notez surtout que **l'intervalle de crédibilité de la moyenne est plus large que celui du modèle de Poisson** (largeur 0,639 contre 0,355) : le modèle de Poisson **sous-estimait l'incertitude** en la faisant porter par une moyenne unique, alors que les clients varient. C'est l'effet typique d'un modèle trop simple : intervalles trop étroits. Les données étant simulées, la vérité est connue : le générateur utilise justement une dispersion $k=2$ (avec, en plus, d'autres sources d'hétérogénéité : le goût pour les produits et l'âge) : le $k$ estimé est cohérent. Revérifions le modèle réparé avec les mêmes statistiques :

| statistique | observée | répliques : moyenne | répliques : 2,5 % – 97,5 % | $p$ bayésien |
|---|---:|---:|---|---:|
| variance / moyenne | 3,324 | 3,287 | [2,653 ; 4,049] | 0,434 |
| part de zéros | 0,109 | 0,117 | [0,083 ; 0,155] | 0,667 |
| maximum | 21 | 22,964 | [17 ; 32] | 0,714 |

```python hide
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

![Vérification prédictive a posteriori de deux modèles pour le nombre de commandes annuelles des clients du canal Boutique. En haut, le modèle de Poisson : les histogrammes des trois statistiques répliquées (variance sur moyenne, part de zéros, maximum) sont loin de la valeur observée (trait rouge). En bas, la binomiale négative : la valeur observée est au milieu des répliques.](figures/ch06-ppc-poisson-binneg.png)

Cette fois, les trois statistiques observées tombent **au milieu** des répliques (les $p_B$ sont loin de 0 et de 1). Le dessin résume la morale : en haut, les données (trait rouge) sont à l'extérieur du nuage des répliques de Poisson ; en bas, elles sont à l'intérieur de celui de la binomiale négative. **Le modèle n'est pas « prouvé vrai »** (aucun ne l'est), mais il a passé trois épreuves que l'autre a échouées.

> ⚠️ **Choisir ses statistiques-test.** Une vérification prédictive ne détecte que les défauts que l'on a pensé à tester. Choisissez des statistiques qui **ne sont pas directement ajustées** par le modèle (la moyenne, que le modèle reproduit par construction, ne révélerait rien) et qui correspondent à vos **soucis** : queues, zéros, asymétrie, dépendance dans le temps, etc.

### 6.4.3 L'a priori est-il raisonnable ? La vérification prédictive *a priori*

Avant même de regarder les données, on peut se demander ce que **l'a priori seul implique**. On simule des paramètres dans l'a priori, puis des données dans le modèle : on obtient la loi **prédictive a priori**. Si elle attribue des probabilités énormes à des scénarios absurdes, l'a priori est mal choisi.

Pour la régression logistique du rachat, regardons ce que signifient des a priori $\beta_j\sim\mathcal N(0,s^2)$ de plus en plus larges, en calculant, pour chaque tirage de $\beta$, la **proportion prédite de clients qui rachètent** (le taux de rachat réel observé est 0,509) :

| écart-type $s$ de l'a priori | taux prédit (5 % – 95 %) | tirages avec taux $<5$ % ou $>95$ % | clients avec $p<1$ % ou $>99$ % (en moyenne) |
|---:|---|---:|---:|
| 0,5 | [0,28 ; 0,71] | 0,0 % | 0,0 % |
| 1,5 | [0,12 ; 0,90] | 2,8 % | 8,6 % |
| 2,5 | [0,05 ; 0,94] | 9,2 % | 28,7 % |
| 10 | [0,01 ; 0,99] | 19,3 % | 79,2 % |

```python hide
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

```python hide
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
(Résultat remarquable : avec un a priori uniforme, **chaque** valeur de $y$ entre 0 et $n$ est également probable a priori.) Pour $n=10,\ y=7$ : $p(y\mid H_0)=120/1024=0{,}1172$ et $p(y\mid H_1)=1/11=0{,}0909$. Donc $\mathrm{BF}_{10}=0{,}0909/0{,}1172=0{,}776$ : les données sont **un peu plus probables sous $H_0$** que sous $H_1$. Sept succès sur dix ne suffisent pas à abandonner la pièce équilibrée ! Le p-value fréquentiste bilatéral est 0,34 : le même message. Appliqué à trois cas (a priori uniforme sous $H_1$, probabilités 50/50 a priori) :

| cas | fréquence | p-valeur (bilatérale) | $\mathrm{BF}_{10}$ | $P(H_1\mid\text{données})$ |
|---|---:|---:|---:|---:|
| 7 rachats sur 10 | 0,7000 | 0,34 | 0,776 | 0,437 |
| offre : 578 sur 1 015 | 0,5695 | $1{,}1\times10^{-5}$ | 720 | 0,999 |
| 50 400 sur 100 000 | 0,5040 | 0,012 | 0,0972 | 0,089 |

```python hide
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
Le premier terme mesure l'ajustement aux données (plus il est grand, mieux le modèle colle) ; $p_{\mathrm{WAIC}}$ est le **nombre effectif de paramètres**, une pénalité qui punit la complexité (c'est l'analogue bayésien de la pénalité de l'AIC, section 1.4). **Plus le WAIC est petit, meilleur est le modèle.** Comparons quatre modèles du rachat, du plus simple au plus complet, en les estimant tous par notre MCMC (le critère est calculé à partir des tirages a posteriori, sans aucun ajustement supplémentaire) :

| modèle | paramètres | $p_{\mathrm{WAIC}}$ | WAIC | AIC (maximum de vraisemblance) |
|---|---:|---:|---:|---:|
| M0 : constante | 1 | 1,00 | 2 773,9 | 2 773,9 |
| M1 : + offre | 2 | 1,89 | 2 745,9 | 2 746,1 |
| M2 : + canal | 4 | 4,26 | 2 732,1 | 2 731,6 |
| M3 : + âge | 5 | 4,95 | **2 720,8** | 2 720,8 |

```python hide
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
           "M2 : + canal": ["const", "offre", "Réseaux", "Site"], "M3 : + âge": ["const", "offre", "Réseaux", "Site", "age_c"]}
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

Le WAIC **décroît** à mesure que l'on ajoute l'offre, puis le canal, puis l'âge. Le $p_{\mathrm{WAIC}}$ est très proche du nombre de paramètres (comme il se doit pour un modèle régulier avec beaucoup de données), et le WAIC est quasiment égal à l'AIC calculé par le maximum de vraisemblance : avec un a priori diffus et beaucoup de données, les deux critères racontent la même histoire. Les dernières lignes comparent les gains avec leur **incertitude** (un WAIC isolé ne signifie rien : seules les **différences entre modèles** comptent, et leur erreur-type). Une différence est jugée « claire » si elle dépasse environ deux erreurs-types. Ici, l'offre apporte un gain net (27,9 ± 10,9, soit 2,6 erreurs-types) ; le canal (13,8 ± 8,5) et l'âge (11,4 ± 7,0) apportent des gains d'environ 1,6 erreur-type : **plausibles mais non tranchés** par le WAIC seul. Cela ne contredit pas la section 6.3.5, où les intervalles de crédibilité de l'âge et du canal Réseaux excluent 0 : le WAIC répond à la question « *ce coefficient améliore-t-il la prédiction de clients nouveaux ?* », pas à « *ce coefficient est-il différent de zéro ?* ».

**Sensibilité à l'a priori (6.1.6, enfin faite).** Terminons par l'analyse de sensibilité promise : le coefficient de l'offre change-t-il si l'on modifie l'écart-type $s$ de l'a priori ? (Moyenne a posteriori et intervalle de crédibilité à 95 % ; le maximum de vraisemblance donne 0,493.)

| $s$ | moyenne a posteriori de $\beta_{\text{offre}}$ | intervalle à 95 % |
|---:|---:|---|
| 0,5 | 0,476 | [0,291 ; 0,653] |
| 1,5 | 0,488 | [0,296 ; 0,672] |
| 2,5 | 0,492 | [0,314 ; 0,665] |
| 10 | 0,494 | [0,321 ; 0,658] |

```python hide
lignes = []
for i, s_ in enumerate((0.5, 1.5, 2.5, 10.0)):
    tir, Xs, emv_ = fit_mcmc_logit(["const", "offre", "Réseaux", "Site", "age_c"], graine=660 + i, s=s_)
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

> 📒 **Pour s'entraîner.** Cahier, chapitre 6 : application 6.4, exercices 6.10 à 6.12.
