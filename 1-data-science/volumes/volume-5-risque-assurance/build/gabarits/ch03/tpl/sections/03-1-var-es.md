## 3.1 VaR et expected shortfall

Cette section répond à une question qui paraît simple : *combien peut-on perdre ?* Elle montrera qu'il n'existe pas **un** chiffre mais une famille de chiffres, chacun avec une définition précise, des hypothèses et une incertitude. Nous partons de la perte d'un portefeuille, la résumons par la **valeur à risque** (VaR) et l'**expected shortfall** (ES), calculons ces deux mesures de quatre façons différentes, puis démontrons que la VaR a un défaut de fond que l'ES n'a pas.

### 3.1.1 De la position à la perte

Un risque de marché ou de portefeuille se mesure sur une **perte** : la variation de valeur, changée de signe pour qu'une perte soit positive. Si la valeur du portefeuille est $V$ et que son rendement sur la période est $R$, la perte est $L=-V\,R$. Un portefeuille de $n$ actifs de poids $w_1,\dots,w_n$ (positifs, de somme 1) a pour rendement $R=\sum_i w_iR_i$ : **la perte du portefeuille est une combinaison linéaire des pertes des actifs**, ce qui donnera plus loin une formule simple pour sa variance.

Notre portefeuille d'exemple vaut 100 M€ et se répartit comme suit.

| Actif | Poids | Montant |
|---|---|---|
| Actions A | 35 % | 35 M€ |
| Actions B | 15 % | 15 M€ |
| Obligations | 30 % | 30 M€ |
| Immobilier coté | 10 % | 10 M€ |
| Matières premières | 10 % | 10 M€ |

Sur les 4 000 jours observés, la perte journalière moyenne est de {{mu_L}} M€ (le portefeuille a plutôt gagné), son écart-type de {{sd_L}} M€, la pire journée a coûté {{pire}} M€ et la meilleure a rapporté {{meilleur_gain}} M€. Le coefficient d'aplatissement en excès (*kurtosis*) vaut {{kurt}}, alors qu'il serait nul pour une loi normale : les journées extrêmes sont **beaucoup plus fréquentes** que ne le prévoirait une cloche de Gauss de même écart-type. (Le plus gros mouvement observé est d'ailleurs un *gain* ; il tire le kurtosis vers le haut, mais la VaR ne regarde que le côté des pertes, où la queue est elle aussi épaisse, comme nous allons le voir.)

```python hide
mu, sd = L.mean(), L.std()
O.num("mu_L", mu, ".3f")
O.num("sd_L", sd, ".2f")
O.num("pire", L.max(), ".2f")
O.num("meilleur_gain", -L.min(), ".2f")
O.num("kurt", pd.Series(L).kurt(), ".1f")
O.num("n_sup3sd", int((L > mu + 3 * sd).sum()), "d")
O.num("n_sup3sd_norm", 4000 * (1 - stats.norm.cdf(3)), ".1f")
```
<!--sortie-->

Comptons les jours où la perte dépasse la moyenne de plus de trois écarts-types : il y en a {{n_sup3sd}} dans nos données, contre {{n_sup3sd_norm}} attendus si la loi était normale. Voilà le point de départ : nous allons chercher des nombres qui résument bien **ces** jours-là.

### 3.1.2 La valeur à risque : un quantile de la perte

> 📐 **Définition.** Soit $L$ la perte sur un horizon donné et $\alpha\in(0,1)$ un niveau de confiance (95 %, 99 %…). La **valeur à risque** de niveau $\alpha$ est
> $$\mathrm{VaR}_\alpha(L)=\inf\{x:\ P(L\le x)\ge\alpha\},$$
> c'est-à-dire le **quantile** d'ordre $\alpha$ de la perte : la perte n'est dépassée qu'avec la probabilité $1-\alpha$.

Une VaR n'a donc de sens qu'accompagnée de **trois précisions** : le niveau $\alpha$, l'**horizon** (un jour, dix jours, un an) et la **convention de signe** (ici : perte positive). « VaR à 99 % sur un jour de 2 M€ » signifie : *sur 99 jours sur 100, la perte du jour ne dépasse pas 2 M€*. Elle ne dit **ni** « la perte maximale » **ni** « ce que l'on perd les mauvais jours » : les jours où la VaR est dépassée peuvent coûter à peine plus ou bien trois fois plus, la VaR ne le saura jamais.

Un exemple à la main, sur dix pertes journalières fictives (en M€), classées de la plus petite à la plus grande : $-0{,}7$ ; $-0{,}4$ ; $-0{,}1$ ; $0{,}2$ ; $0{,}3$ ; $0{,}5$ ; $0{,}9$ ; $1{,}4$ ; $2{,}6$ ; $4{,}1$. Pour $\alpha=90\ \%$ et dix observations, le plus petit $x$ tel qu'au moins 90 % des pertes soient inférieures ou égales à $x$ est la **neuvième** valeur : la VaR à 90 % vaut {{ex_var90}} M€. Pour $\alpha=80\ \%$, c'est la huitième : {{ex_var80}} M€. Retenons la règle : avec $n$ observations, la VaR empirique est la valeur de rang $\lceil\alpha n\rceil$.

```python hide
x = np.array([-0.4, 0.3, 0.9, -0.1, 1.4, 0.2, -0.7, 2.6, 0.5, 4.1])
O.num("ex_var90", O.var_hist(x, 0.9), ".1f")
O.num("ex_var80", O.var_hist(x, 0.8), ".1f")
O.num("ex_es90", O.es_hist(x, 0.9), ".2f")
```
<!--sortie-->

Sur nos 4 000 jours, la VaR historique s'obtient en une ligne. L'option `method="inverted_cdf"` donne exactement la définition ci-dessus.

```python
niveaux = [0.95, 0.99, 0.999]
print(dict(zip(niveaux, np.quantile(L, niveaux, method="inverted_cdf").round(2).tolist())))
```
<!--sortie-->

```python hide
O.num("var_h95", O.var_hist(L, 0.95), ".2f")
O.num("var_h99", O.var_hist(L, 0.99), ".2f")
O.num("var_h999", O.var_hist(L, 0.999), ".2f")
assert abs(O.var_hist(L, 0.99) - np.quantile(L, 0.99, method="inverted_cdf")) < 1e-12
```
<!--sortie-->

Le portefeuille de 100 M€ a donc perdu plus de {{var_h95}} M€ un jour sur vingt, plus de {{var_h99}} M€ un jour sur cent et plus de {{var_h999}} M€ un jour sur mille. Ces trois nombres sont des **mesures** : ils dépendent de la période d'observation, du portefeuille et du niveau choisi.

> 🧭 **En pratique.** Le niveau de confiance est une convention d'usage et non une loi de la nature : les cadres prudentiels retiennent des niveaux élevés (99 %, 99,9 %) parce qu'ils visent la survie, alors que la gestion interne utilise souvent 95 % pour suivre le risque courant. Plus le niveau est élevé, **moins il y a d'observations pour l'estimer** : à 99,9 % sur 4 000 jours, il n'y en a que quatre (section 3.1.9).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.1.

### 3.1.3 La VaR normale en forme close

Si l'on suppose que la perte suit une loi normale $\mathcal N(\mu,\sigma^2)$, la VaR s'écrit sans simulation.

> 📐 **Démonstration.** $P(L\le x)=\Phi\!\left(\dfrac{x-\mu}{\sigma}\right)$, où $\Phi$ est la fonction de répartition de la loi normale centrée réduite. Elle est supérieure ou égale à $\alpha$ si et seulement si $\dfrac{x-\mu}{\sigma}\ge z_\alpha:=\Phi^{-1}(\alpha)$. La plus petite valeur de $x$ est donc
> $$\boxed{\mathrm{VaR}_\alpha=\mu+\sigma\,z_\alpha}.$$
> Les quantiles utiles sont $z_{95\%}\approx1{,}645$, $z_{99\%}\approx2{,}326$ et $z_{99{,}9\%}\approx3{,}090$.

Pour un portefeuille, $\mu=\sum_iw_i\mu_i\,V$ et la variance est celle d'une combinaison linéaire : $\sigma^2=V^2\,w^\top\Sigma w$, où $\Sigma$ est la matrice de covariance des rendements. C'est la **méthode variance-covariance**, historiquement la première utilisée en salle de marché parce qu'elle ne demande qu'une matrice $n\times n$. Elle met aussi en évidence l'effet de diversification : $\sigma\le V\sum_iw_i\sigma_i$, avec égalité si et seulement si tous les actifs sont parfaitement corrélés.

Appliquons-la à notre portefeuille avec la moyenne et l'écart-type observés ({{mu_L}} et {{sd_L}} M€). À 95 %, on trouve {{var_n95}} M€ (historique : {{var_h95}}), à 99 %, {{var_n99}} M€ (historique : {{var_h99}}), à 99,9 %, {{var_n999}} M€ (historique : {{var_h999}}).

```python hide
for a, k in ((0.95, "95"), (0.99, "99"), (0.999, "999")):
    O.num("var_n" + k, O.var_normale(mu, sd, a), ".2f")
```
<!--sortie-->

Le constat est net et central pour tout le chapitre : **à 95 %, la loi normale est un peu prudente, à 99 % elle sous-estime nettement la VaR historique, et à 99,9 % elle la divise presque par deux.** Une cloche de Gauss ajustée sur l'écart-type ne voit pas que notre portefeuille a des queues épaisses : l'écart-type est surtout fabriqué par les jours ordinaires, alors que la VaR à 99,9 % ne regarde que les jours exceptionnels.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.2, application 3.1.

### 3.1.4 La VaR historique et la VaR par simulation

La **VaR historique** n'invente aucune loi : elle prend les $N$ dernières pertes observées, les applique au portefeuille d'aujourd'hui et lit le quantile empirique, comme nous l'avons fait ci-dessus. Ses forces : aucune hypothèse de forme, les corrélations et les queues réelles sont préservées. Ses faiblesses : elle ne connaît que le passé (un type de crise jamais vu n'y figure pas) et elle dépend du **choix de la fenêtre**. Sur nos données, la VaR à 99 % calculée sur les {{w_250}} derniers jours vaut {{var_w250}} M€, sur les 500 derniers jours {{var_w500}} M€, sur les 1 000 derniers {{var_w1000}} M€ et sur les 4 000 jours {{var_h99}} M€. Une fenêtre courte réagit vite mais oublie les crises ; une fenêtre longue se souvient mais réagit tard.

Elle a aussi un défaut discret, l'**effet fantôme** : lorsqu'une journée extrême quitte la fenêtre, la VaR chute d'un coup sans que le risque ait changé. Sur une fenêtre glissante de 500 jours, la VaR à 99 % a déjà varié de {{saut_max}} M€ d'un jour à l'autre alors que le portefeuille était inchangé.

```python hide
v = {}
for f in (250, 500, 1000):
    v[f] = O.var_hist(L[-f:], 0.99)
O.num("w_250", 250, "d")
O.num("var_w250", v[250], ".2f")
O.num("var_w500", v[500], ".2f")
O.num("var_w1000", v[1000], ".2f")
roll = np.array([O.var_hist(L[t - 500:t], 0.99) for t in range(500, len(L))])
O.num("saut_max", np.abs(np.diff(roll)).max(), ".2f")
```
<!--sortie-->

La **VaR par simulation de Monte-Carlo** choisit un modèle, tire de nombreux scénarios de rendements conformes à ce modèle, revalorise le portefeuille dans chacun et lit le quantile. Elle a l'avantage de s'adapter à des portefeuilles non linéaires (options, produits complexes) que la matrice de covariance ne sait pas traiter. Mais son résultat n'est **jamais meilleur que le modèle** : avec une loi normale multivariée de mêmes moyennes et covariances, nos 200 000 scénarios redonnent la VaR à 99 % de la formule fermée, soit {{mc_n99}} M€ ; avec une loi de Student multivariée à {{nu_mc}} degrés de liberté, de même matrice de covariance, on obtient {{mc_t99}} M€. L'écart entre les deux ne vient pas de la simulation, il vient du **choix de la loi**.

```python hide
Sigma = np.cov(r[O.ACTIFS].values.T)
mu_v = r[O.ACTIFS].values.mean(axis=0)
rng = np.random.default_rng(7)
N = 200000
Zn = rng.multivariate_normal(mu_v, Sigma, N)
nu = 4
W = rng.chisquare(nu, N) / nu
Zt = mu_v + (rng.multivariate_normal(np.zeros(5), Sigma, N) * np.sqrt((nu - 2) / nu)) / np.sqrt(W)[:, None]
perte_n = -(Zn @ O.POIDS) * O.VALEUR
perte_t = -(Zt @ O.POIDS) * O.VALEUR
O.num("mc_n99", O.var_hist(perte_n, 0.99), ".2f")
O.num("mc_t99", O.var_hist(perte_t, 0.99), ".2f")
O.num("nu_mc", nu, "d")
O.num("mc_t999", O.var_hist(perte_t, 0.999), ".2f")
```
<!--sortie-->

> 💡 **Intuition.** Les trois méthodes ne sont pas concurrentes mais complémentaires : la formule fermée est rapide et lisible, la méthode historique est honnête sur ce qui s'est passé, la simulation est souple. Un risk manager les compare : un écart important entre elles est une **information** (la queue n'est pas normale, ou la fenêtre est trop courte), pas une erreur à corriger.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.3.

### 3.1.5 Quand la volatilité change : EWMA et GARCH

Jusqu'ici nous avons supposé que l'écart-type était constant. Or l'observation du début de chapitre montrait le contraire : les mauvais jours viennent **par grappes**. Le graphique suivant montre la volatilité glissante sur 60 jours ; les zones grisées sont les périodes de stress du marché (que le simulateur connaît, mais que l'analyste ne voit pas).

![Volatilité glissante de la perte du portefeuille sur 60 jours (M€). Les bandes grisées sont les périodes de régime de stress ; la volatilité s'y envole puis retombe.](figures/ch03-volatilite-regimes.png)

```python hide
sig60 = pd.Series(L, index=r.index).rolling(60).std()
fig, ax = plt.subplots(figsize=(8.4, 3.4))
ax.plot(sig60.index, sig60.values, color=BLEU, lw=1.4)
st = (rg == "stress").astype(int)
debut = np.where(np.diff(np.r_[0, st]) == 1)[0]
fin = np.where(np.diff(np.r_[st, 0]) == -1)[0]
for a, b in zip(debut, fin):
    ax.axvspan(r.index[a], r.index[b], color=MUET, alpha=0.25, lw=0)
ax.set_ylabel("écart-type sur 60 jours (M€)")
ax.set_xlabel("date")
style.save(fig, "ch03-volatilite-regimes.png")
O.num("nb_episodes", len(debut), "d")
O.num("duree_moy", np.mean(fin - debut + 1), ".0f")
```
<!--sortie-->

Le marché a traversé {{nb_episodes}} épisodes de stress, d'une durée moyenne de {{duree_moy}} jours ; on remarque que la volatilité continue de monter ou de retomber lentement après un épisode, et qu'elle connaît aussi des pics en dehors de tout régime de stress : c'est la signature d'un modèle de volatilité de type GARCH, dans lequel un choc en appelle d'autres. Une VaR calibrée sur toute l'histoire est trop basse pendant ces épisodes et trop haute le reste du temps : elle mesure un risque moyen qui n'existe jamais. Deux familles de modèles suivent la volatilité du moment.

**L'EWMA** (*exponentially weighted moving average*) met à jour la variance chaque jour en pondérant davantage le passé récent :
$$\sigma_t^2=\lambda\,\sigma_{t-1}^2+(1-\lambda)\,L_{t-1}^2 ,$$
avec $\lambda=0{,}94$ pour des données journalières, valeur popularisée par la méthodologie RiskMetrics. Elle a un seul paramètre fixé par convention et une mémoire d'environ $1/(1-\lambda)\approx17$ jours.

**Le GARCH(1,1)** (volume II, section 4.4) estime ses paramètres par maximum de vraisemblance :
$$\sigma_t^2=\omega+\alpha\,L_{t-1}^2+\beta\,\sigma_{t-1}^2 .$$
Il est stationnaire si $\alpha+\beta<1$, et sa variance de long terme est $\omega/(1-\alpha-\beta)$. La somme $\alpha+\beta$, appelée **persistance**, dit combien de temps un choc de volatilité se prolonge. Ajusté sur les 2 000 premiers jours avec des innovations de Student (pour les queues épaisses), il donne le résultat suivant.

```python
from arch import arch_model
apprentissage, test = L[:2000], L[2000:]
modele = arch_model(apprentissage, mean="Zero", vol="GARCH", p=1, q=1, dist="t").fit(disp="off")
print(modele.params.round(3))
```
<!--sortie-->

```python hide
O.num("g_alpha", modele.params["alpha[1]"], ".3f")
O.num("g_beta", modele.params["beta[1]"], ".3f")
O.num("g_pers", modele.params["alpha[1]"] + modele.params["beta[1]"], ".3f")
O.num("g_nu", modele.params["nu"], ".1f")
```
<!--sortie-->

On lit $\hat\alpha$ = {{g_alpha}} et $\hat\beta$ = {{g_beta}}, donc une persistance de {{g_pers}} (très proche de 1 : les chocs de volatilité s'éteignent lentement) et $\hat\nu$ = {{g_nu}} degrés de liberté (des queues bien plus épaisses que la normale ; le simulateur en utilisait 5). Pour que la comparaison soit honnête, **les paramètres sont figés sur les 2 000 premiers jours** et nous *filtrons* ensuite la volatilité sur les 2 000 jours suivants : chaque matin, le modèle ne connaît que ce qui s'est passé la veille. Trois VaR à 99 % sur un jour sont comparées : la VaR historique et la VaR normale calibrées une fois pour toutes sur les 2 000 premiers jours, et la VaR GARCH-Student qui s'ajuste chaque jour. Le tableau donne la **fréquence des dépassements** (jours où la perte excède la VaR) ; elle devrait valoir 1 %.

| Méthode | Tous les jours | Régime calme | Régime de stress |
|---|---|---|---|
| Historique (fixe) | {{exc_hist_tot}} % | {{exc_hist_calme}} % | {{exc_hist_stress}} % |
| Normale (fixe) | {{exc_norm_tot}} % | {{exc_norm_calme}} % | {{exc_norm_stress}} % |
| GARCH-Student (filtrée) | {{exc_garch_tot}} % | {{exc_garch_calme}} % | {{exc_garch_stress}} % |

```python hide
rt = rg[2000:]
sig_g, nu_g, _ = O.garch_filtre(apprentissage, test)
v_h = np.full(len(test), O.var_hist(apprentissage, 0.99))
v_n = np.full(len(test), O.var_normale(apprentissage.mean(), apprentissage.std(), 0.99))
v_g = np.array([O.var_student(0, s, nu_g, 0.99) for s in sig_g])
for nom, v in (("hist", v_h), ("norm", v_n), ("garch", v_g)):
    e = test > v
    O.num(f"exc_{nom}_tot", 100 * e.mean(), ".1f")
    O.num(f"exc_{nom}_calme", 100 * e[rt == "calme"].mean(), ".1f")
    O.num(f"exc_{nom}_stress", 100 * e[rt == "stress"].mean(), ".1f")
O.num("n_stress_test", int((rt == "stress").sum()), "d")
```
<!--sortie-->

Les deux méthodes figées dépassent trop souvent, et **presque tous les dépassements surviennent en régime de stress**, où la fréquence monte à plus de 10 % : le jour où l'on a le plus besoin de la VaR, elle est fausse d'un facteur dix. La VaR GARCH, qui s'adapte, reste bien plus proche de 1 %, sans l'atteindre en stress ({{exc_garch_stress}} % sur {{n_stress_test}} jours de stress) : le modèle réagit après coup, il ne **prévoit** pas les basculements de régime. Un modèle de volatilité améliore beaucoup la couverture, il ne la rend pas parfaite.

> ⚠️ **Piège.** Une VaR « historique » sur une fenêtre calme est la VaR d'une époque calme. Calculer sur une période sans crise puis annoncer que « le risque est faible » est l'erreur la plus fréquente, et la plus coûteuse.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.2.

### 3.1.6 Du jour à dix jours : la règle de la racine

Les cadres prudentiels demandent souvent un horizon de plusieurs jours (la période pendant laquelle on ne peut pas dénouer ses positions). Plutôt que de réestimer, on **met à l'échelle** par la règle de la racine carrée du temps.

> 📐 **Démonstration.** Si les pertes journalières $L_1,\dots,L_h$ sont indépendantes, de même loi, de moyenne nulle et d'écart-type $\sigma$, alors $\mathrm{Var}(L_1+\dots+L_h)=h\sigma^2$, donc l'écart-type à $h$ jours est $\sigma\sqrt h$. Si de plus la loi est normale, la somme l'est aussi et $\mathrm{VaR}_\alpha^{(h)}=\sqrt h\ \mathrm{VaR}_\alpha^{(1)}$. Avec une moyenne $\mu$ non nulle, le terme de moyenne croît en $h$ et non en $\sqrt h$.

Pour dix jours, la VaR à 99 % historique journalière de {{var_h99}} M€ donne {{var10_racine}} M€. Mesurons maintenant la VaR sur les **sommes de dix pertes consécutives sans chevauchement** (400 observations) : {{var10_emp}} M€, soit {{ecart10}} % d'écart seulement. Sur nos données, **la règle fonctionne remarquablement bien**, et pour une bonne raison : les pertes d'un jour à l'autre sont sans mémoire (leur corrélation est de {{acf_L}}), ce qui est la condition centrale de la démonstration. Elle fonctionne aussi à l'intérieur de chaque régime : le rapport entre la VaR à dix jours observée et $\sqrt{10}$ fois la VaR à un jour vaut {{ratio_calme10}} pour les fenêtres qui débutent en régime calme et {{ratio_stress10}} pour celles qui débutent en stress.

Ce bon résultat ne doit pas rassurer à l'excès : il tient à notre simulation, où les rendements sont sans autocorrélation. La règle se brise dès que les pertes ont de la **mémoire** : des portefeuilles de produits peu liquides dont les valorisations sont lissées (les pertes se propagent sur plusieurs jours, la corrélation est positive et le risque à dix jours dépasse nettement $\sqrt{10}$ fois celui d'un jour), ou des marchés qui changent de régime *pendant* la fenêtre (la corrélation entre les carrés des pertes de deux jours consécutifs vaut ici {{acf_sq}} : c'est la signature des grappes de volatilité).

```python hide
v1 = O.var_hist(L, 0.99)
S10 = L[: (len(L) // 10) * 10].reshape(-1, 10).sum(axis=1)
v10 = O.var_hist(S10, 0.99)
O.num("var10_racine", np.sqrt(10) * v1, ".2f")
O.num("var10_emp", v10, ".2f")
O.num("ecart10", 100 * abs(v10 / (np.sqrt(10) * v1) - 1), ".0f")
O.num("acf_L", np.corrcoef(L[:-1], L[1:])[0, 1], ".3f")
x2 = L ** 2
O.num("acf_sq", np.corrcoef(x2[:-1], x2[1:])[0, 1], ".2f")
fen10 = pd.Series(L).rolling(10).sum().shift(-9).values
for nom, g in (("calme", "calme"), ("stress", "stress")):
    m = ~np.isnan(fen10) & (rg == g)
    v1g = O.var_hist(L[rg == g], 0.99)
    O.num(f"ratio_{nom}10", O.var_hist(fen10[m], 0.99) / (np.sqrt(10) * v1g), ".2f")
```
<!--sortie-->

> ⚠️ **Piège.** La règle de la racine est une approximation commode, pas un théorème sur vos données : elle suppose des pertes **indépendantes** (et, pour passer à la VaR, normales). Vérifiez l'autocorrélation avant de l'appliquer, et rappelez-vous que l'horizon est une **hypothèse économique** (le temps qu'il faut pour sortir d'une position) avant d'être un paramètre statistique : les cadres prudentiels retiennent d'ailleurs des horizons différents selon la liquidité des positions (valeurs à vérifier dans les textes en vigueur).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.5.

### 3.1.7 L'expected shortfall

La VaR dit *à partir de quelle perte* on entre dans la queue, mais pas *combien* on y perd. L'**expected shortfall** (ES, ou *perte moyenne conditionnelle*, ou CVaR) répond à la seconde question.

> 📐 **Définition.** Pour une perte $L$ de moyenne finie,
> $$\mathrm{ES}_\alpha(L)=\frac{1}{1-\alpha}\int_\alpha^1\mathrm{VaR}_u(L)\,du ,$$
> et lorsque la loi est continue, $\mathrm{ES}_\alpha=\mathbb E\,[L\mid L\ge\mathrm{VaR}_\alpha]$ : la **perte moyenne les jours où la VaR est dépassée**.

Sur nos dix pertes fictives, à 90 %, la VaR est de {{ex_var90}} M€ et l'ES est la moyenne des pertes supérieures ou égales à elle, $(2{,}6+4{,}1)/2$, soit {{ex_es90}} M€. Sur le portefeuille réel, l'ES historique à 99 % est de {{es_h99}} M€, contre une VaR de {{var_h99}} M€ : le rapport ES/VaR vaut {{ratio_es}}. Pour une loi normale, l'ES à 99 % n'est que 1,15 fois la VaR ; un rapport nettement supérieur révèle une **queue épaisse** : lorsque la VaR est franchie, elle l'est de loin.

> 📐 **ES d'une loi normale.** Si $L\sim\mathcal N(\mu,\sigma^2)$, alors $L=\mu+\sigma Z$ avec $Z$ normale centrée réduite et $\mathrm{VaR}_\alpha=\mu+\sigma z_\alpha$. Comme $\int_z^\infty u\,\varphi(u)\,du=\varphi(z)$ (car $\varphi'(u)=-u\varphi(u)$),
> $$\mathrm{ES}_\alpha=\mu+\sigma\,\mathbb E[Z\mid Z\ge z_\alpha]=\mu+\sigma\,\frac{\varphi(z_\alpha)}{1-\alpha}.$$
> Pour $\alpha=99\ \%$ : $\varphi(2{,}326)/0{,}01\approx2{,}665$, donc $\mathrm{ES}_{99\%}\approx\mu+2{,}665\,\sigma$, à comparer à $\mu+2{,}326\,\sigma$ pour la VaR.

Avec les paramètres observés, l'ES normale à 99 % vaut {{es_n99}} M€, très en deçà de l'ES historique ({{es_h99}} M€) : comme la VaR, elle est trompée par la queue. Notons qu'une propriété utile relie les deux mesures : pour une loi normale, l'ES à **97,5 %** vaut $\mu+2{,}338\,\sigma$, presque la VaR à 99 % ($\mu+2{,}326\,\sigma$). C'est l'une des raisons pour lesquelles certains cadres prudentiels de marché ont remplacé la VaR à 99 % par l'ES à 97,5 % (niveau à vérifier dans les textes en vigueur) : sur des données normales cela ne change presque rien, sur des queues épaisses l'ES prend en compte ce que la VaR ignore.

```python hide
for a, k in ((0.95, "95"), (0.99, "99"), (0.999, "999")):
    O.num("es_h" + k, O.es_hist(L, a), ".2f")
O.num("es_n99", O.es_normale(mu, sd, 0.99), ".2f")
O.num("ratio_es", O.es_hist(L, 0.99) / O.var_hist(L, 0.99), ".2f")
assert abs(stats.norm.pdf(stats.norm.ppf(0.975)) / 0.025 - 2.338) < 0.001
assert abs(stats.norm.pdf(stats.norm.ppf(0.99)) / 0.01 - 2.665) < 0.001
```
<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.3.

### 3.1.8 Cohérence : pourquoi la VaR ne diversifie pas toujours

Artzner, Delbaen, Eber et Heath ont proposé en 1999 quatre propriétés qu'une mesure de risque $\rho$ « raisonnable » devrait avoir, et appelé **cohérentes** les mesures qui les vérifient toutes : la **monotonie** (une position qui perd toujours plus a un risque plus grand), l'**invariance par translation** (ajouter de la trésorerie réduit le risque d'autant), l'**homogénéité positive** (doubler la position double le risque) et la **sous-additivité**, $\rho(L_1+L_2)\le\rho(L_1)+\rho(L_2)$ : *fusionner deux portefeuilles ne crée pas de risque*, c'est la traduction mathématique de la diversification. L'ES vérifie les quatre. La VaR vérifie les trois premières mais **pas la sous-additivité** en général.

Un contre-exemple à la main suffit. Deux prêts indépendants de 1 M€ chacun ont une probabilité de défaut de 4 % et une perte de 1 M€ en cas de défaut (perte nulle sinon). On travaille au niveau de 95 %.

- **Chaque prêt seul.** La perte vaut 1 avec la probabilité 0,04 et 0 avec la probabilité 0,96. Comme $P(L\le0)=0{,}96\ge0{,}95$, on a $\mathrm{VaR}_{95\%}=0$. La somme des deux VaR est donc **0**.
- **Les deux prêts ensemble.** La probabilité qu'aucun ne fasse défaut est $0{,}96^2=0{,}9216<0{,}95$. La perte totale vaut donc 1 ou plus avec une probabilité de $1-0{,}9216=7{,}84\ \%>5\ \%$ : $\mathrm{VaR}_{95\%}=1$ M€.

La VaR du portefeuille (1) **dépasse** la somme des VaR (0) : selon la VaR, regrouper deux prêts *augmente* le risque, ce qui contredit toute intuition de diversification. Avec l'ES à 95 % : pour un prêt seul, $\mathrm{VaR}_u=0$ pour $u\le0{,}96$ et 1 au-delà, donc $\mathrm{ES}=(0{,}04\times1)/0{,}05$, soit {{es_each}} M€ pour chaque prêt, soit {{es_sum}} M€ pour les deux. Pour les deux ensemble, $P(L=0)=0{,}9216$, $P(L=1)=0{,}0768$, $P(L=2)=0{,}0016$ : l'ES vaut $[(0{,}9984-0{,}95)\times1+(1-0{,}9984)\times2]/0{,}05$, soit {{es_comb}} M€, **inférieure** à {{es_sum}} : l'ES respecte la diversification.

```python hide
p = 0.04
tot = {0: (1 - p) ** 2, 1: 2 * p * (1 - p), 2: p ** 2}
O.num("p_defaut_un", 100 * (1 - (1 - p) ** 2), ".2f")
O.num("es_each", (p * 1) / 0.05, ".2f")
O.num("es_sum", 2 * (p * 1) / 0.05, ".2f")
O.num("es_comb", ((0.9984 - 0.95) * 1 + (1 - 0.9984) * 2) / 0.05, ".3f")
# vérification par simulation
rng2 = np.random.default_rng(3)
d = rng2.random((1_000_000, 2)) < p
Ls = d.sum(axis=1)
assert O.var_hist(Ls, 0.95) == 1 and O.var_hist(d[:, 0].astype(int), 0.95) == 0
assert abs(O.es_hist(Ls, 0.95) - 1.032) < 0.02
```
<!--sortie-->

> ⚠️ **Piège.** La VaR est parfaitement acceptable pour des pertes de loi normale (elle est alors sous-additive), et c'est précisément ce qui la rend dangereuse : le contre-exemple ne se produit que quand les pertes sont **discontinues et concentrées**, comme dans le crédit, où l'on perd tout ou rien. Dans un portefeuille de prêts, la VaR peut décourager la diversification ; l'ES, non.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.4.

### 3.1.9 Combien vaut un chiffre de queue ?

Une VaR à 99 % sur 4 000 jours repose sur les **40 plus mauvais jours** ; à 99,9 %, sur **quatre**. Avant de discuter la méthode, demandons-nous à quel point le chiffre est *stable*. Le **bootstrap** réestime la VaR sur de nombreux échantillons tirés avec remise parmi les 4 000 pertes, et le quantile de ces estimations donne un intervalle de confiance. (Il suppose des pertes indépendantes, ce qui est faux ici à cause des grappes de volatilité : l'intervalle est donc *optimiste*.)

| Mesure | Estimation | Intervalle à 95 % | Largeur relative |
|---|---|---|---|
| VaR 99 % | {{var_h99}} M€ | [{{b_var99_lo}} ; {{b_var99_hi}}] | {{b_var99_w}} % |
| ES 99 % | {{es_h99}} M€ | [{{b_es99_lo}} ; {{b_es99_hi}}] | {{b_es99_w}} % |
| VaR 99,9 % | {{var_h999}} M€ | [{{b_var999_lo}} ; {{b_var999_hi}}] | {{b_var999_w}} % |

```python hide
rng3 = np.random.default_rng(11)
B = 1000
idx = rng3.integers(0, len(L), (B, len(L)))
bv99 = np.array([O.var_hist(L[i], 0.99) for i in idx])
bes99 = np.array([O.es_hist(L[i], 0.99) for i in idx])
bv999 = np.array([O.var_hist(L[i], 0.999) for i in idx])
for nom, b, est in (("var99", bv99, O.var_hist(L, 0.99)), ("es99", bes99, O.es_hist(L, 0.99)), ("var999", bv999, O.var_hist(L, 0.999))):
    lo, hi = np.quantile(b, [0.025, 0.975])
    O.num(f"b_{nom}_lo", lo, ".2f")
    O.num(f"b_{nom}_hi", hi, ".2f")
    O.num(f"b_{nom}_w", 100 * (hi - lo) / est, ".0f")
```
<!--sortie-->

Même avec cet intervalle optimiste, la VaR à 99 % n'est connue qu'à ±{{b_var99_half}} % près, et la VaR à 99,9 % à ±{{b_var999_half}} % : en valeur absolue, l'intervalle est {{ratio_wabs}} fois plus large au niveau de 99,9 %. L'ES à 99 % est ici un peu plus stable que la VaR au même niveau, parce qu'elle moyenne les 40 plus mauvais jours au lieu de lire un seul rang, mais elle reste sensible aux quelques plus grosses pertes de l'échantillon. **Un chiffre de queue donné sans intervalle est un chiffre dont on ignore la précision.** Les techniques de la théorie des valeurs extrêmes (volume II, section 6.5) ajustent une loi à la queue pour extrapoler au-delà des données, au prix d'hypothèses supplémentaires ; nous les retrouverons en 3.3 pour les pertes opérationnelles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.4.

```python hide
w99 = np.quantile(bv99, 0.975) - np.quantile(bv99, 0.025)
w999 = np.quantile(bv999, 0.975) - np.quantile(bv999, 0.025)
O.num("ratio_wabs", w999 / w99, ".1f")
O.num("b_var99_half", 50 * w99 / O.var_hist(L, 0.99), ".0f")
O.num("b_var999_half", 50 * w999 / O.var_hist(L, 0.999), ".0f")
```
<!--sortie-->

> ✅ **À retenir.**
> - La **VaR** de niveau $\alpha$ est le quantile $\alpha$ de la perte ; elle se lit avec son niveau, son horizon et sa convention de signe, et ne dit rien de ce qui se passe au-delà.
> - La **VaR normale** $\mu+\sigma z_\alpha$ est rapide mais sous-estime les queues épaisses ; la VaR **historique** est honnête mais dépend de la fenêtre ; la simulation n'est jamais meilleure que son modèle.
> - Une volatilité qui change (EWMA, GARCH) améliore beaucoup la couverture, surtout en stress, sans prévoir les basculements.
> - La règle de la racine carrée suppose des pertes indépendantes et normales ; elle sous-estime ici le risque à dix jours.
> - L'**ES** est la perte moyenne au-delà de la VaR ; elle est **cohérente** (sous-additive), alors que la VaR ne l'est pas en général.
> - Un chiffre de queue sans intervalle est un chiffre dont on ignore la précision.
