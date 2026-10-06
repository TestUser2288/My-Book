# Chapitre 3 : Mesures de risque et stress tests

> « Un chiffre de risque est une réponse à une question. Avant de le lire, il faut retrouver la question. »

Les deux premiers chapitres ont chiffré des risques *individuels* : la probabilité qu'un emprunteur ne rembourse pas, la charge de sinistres d'un contrat d'assurance. Mais ni la banque ni la mutuelle ne vivent contrat par contrat. Elles vivent **en portefeuille**, c'est-à-dire avec des milliers de risques qui se compensent un jour et s'additionnent le lendemain, et c'est la **perte du portefeuille entier** qui décide de la solvabilité. Ce chapitre apprend à résumer cette perte par quelques nombres, à les calculer de plusieurs façons, à les **mettre à l'épreuve** par des scénarios extrêmes, puis à vérifier qu'ils tiennent face à la réalité.

Le fil conducteur est une phrase : **un nombre de risque n'a de sens qu'avec sa définition, son horizon, son niveau de confiance… et son incertitude**. La *valeur à risque* (VaR) à 99 % sur un jour et la VaR à 99 % sur dix jours ne répondent pas à la même question ; la VaR et la perte moyenne au-delà de la VaR (l'*expected shortfall*) ne disent pas la même chose de la queue de la distribution ; un modèle calibré en période calme se trompe précisément quand la période cesse de l'être. Nous le verrons sur des données simulées dont nous connaissons la vérité : nous pourrons donc, ce que la vie réelle ne permet presque jamais, **juger chaque méthode par rapport à ce qui s'est vraiment passé**.

## Le chemin de ce chapitre

- **3.1 VaR et expected shortfall.** Définir une perte, un quantile, un horizon. Calculer la VaR par la loi normale (formule démontrée), par l'histoire, par simulation, par un modèle de volatilité qui change (EWMA, GARCH). Comprendre l'expected shortfall, démontrer pourquoi la VaR n'est pas une mesure *cohérente*, et mesurer l'incertitude d'un chiffre de queue.
- **3.2 Stress tests et scénarios.** Répondre à la question « et si ? » : sensibilités, scénarios historiques et hypothétiques, scénario *macroéconomique* relié aux défauts de crédit par un modèle statistique, choc de taux d'intérêt, stress *inversé*, et pourquoi les corrélations montent quand tout va mal.
- **➕ 3.3 Risques opérationnel, de marché et de liquidité.** L'approche par distribution des pertes (fréquence × sévérité) appliquée à des incidents opérationnels, les contributions au risque d'un portefeuille de marché, et un aperçu de la liquidité.
- **➕ 3.4 Backtesting et validation des modèles.** Les tests de Kupiec et de Christoffersen, le « feu tricolore », le contrôle de l'expected shortfall, et la démarche de validation indépendante d'un modèle, avec son risque propre : le **risque de modèle**.
- **Bilan du chapitre**, puis, dans le **cahier**, huit applications et douze exercices corrigés.

Ce chapitre s'appuie sur le volume II (régression logistique, section 2.2 ; modèles GARCH, section 4.4 ; valeurs extrêmes, section 6.5) et sur le volume III (validation, chapitre 1 ; métriques et calibration, chapitre 5). Il prépare le chapitre 4 : les cadres réglementaires de Bâle et de Solvabilité *imposent* des mesures de risque, et nous saurons ce qu'elles valent.

## Les données du chapitre

> 📦 **Données (simulées, graines fixes).** Quatre jeux, tous fabriqués par `build/donnees5.py`, qui connaît donc la vérité.
> - `rendements_marche.csv` : 4 000 jours ouvrés de rendements journaliers de cinq actifs (deux paniers d'actions, des obligations, de l'immobilier coté, des matières premières). La volatilité change au fil du temps (modèle GARCH) et le marché alterne entre un régime **calme** et un régime de **stress** (volatilité doublée, corrélations en hausse) ; `marche_verite.csv` donne le régime vrai de chaque jour.
> - `taux_defaut_macro.csv` : 80 trimestres de variables macroéconomiques (croissance, chômage, variation de l'immobilier) et le taux de défaut annualisé d'un portefeuille de crédit, avec une récession aux trimestres 48 à 54.
> - `courbe_taux.csv` : 120 mois d'une courbe de taux sur neuf maturités, avec un cycle de hausse des taux entre les mois 60 et 90.
> - `pertes_operationnelles.csv` : dix ans d'incidents opérationnels (fraudes, erreurs de traitement, pannes, pratiques commerciales) avec perte brute, récupération et perte nette.
>
> Le portefeuille d'exemple est celui d'un investisseur institutionnel fictif : **100 M€** répartis ainsi : 35 % d'actions A, 15 % d'actions B, 30 % d'obligations, 10 % d'immobilier et 10 % de matières premières. Toutes les pertes sont exprimées en **millions d'euros**, comptées **positivement** (une perte de 2 signifie que le portefeuille a perdu 2 M€).

<!--sortie-->

Un premier regard suffit à comprendre l'enjeu : l'écart-type de la perte journalière du portefeuille est de 0,57 M€ en régime calme et de 1,56 M€ en régime de stress, soit 2,7 fois plus, alors que les jours de stress ne représentent que 7,0 % des 4 000 jours observés. Presque toute la difficulté du chapitre tient dans cette asymétrie : **la queue de la distribution est fabriquée par une minorité de jours qui ne ressemblent pas aux autres**.


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

Sur les 4 000 jours observés, la perte journalière moyenne est de -0,016 M€ (le portefeuille a plutôt gagné), son écart-type de 0,69 M€, la pire journée a coûté 5,98 M€ et la meilleure a rapporté 10,45 M€. Le coefficient d'aplatissement en excès (*kurtosis*) vaut 20,3, alors qu'il serait nul pour une loi normale : les journées extrêmes sont **beaucoup plus fréquentes** que ne le prévoirait une cloche de Gauss de même écart-type. (Le plus gros mouvement observé est d'ailleurs un *gain* ; il tire le kurtosis vers le haut, mais la VaR ne regarde que le côté des pertes, où la queue est elle aussi épaisse, comme nous allons le voir.)

<!--sortie-->

Comptons les jours où la perte dépasse la moyenne de plus de trois écarts-types : il y en a 40 dans nos données, contre 5,4 attendus si la loi était normale. Voilà le point de départ : nous allons chercher des nombres qui résument bien **ces** jours-là.

### 3.1.2 La valeur à risque : un quantile de la perte

> 📐 **Définition.** Soit $L$ la perte sur un horizon donné et $\alpha\in(0,1)$ un niveau de confiance (95 %, 99 %…). La **valeur à risque** de niveau $\alpha$ est
> $$\mathrm{VaR}_\alpha(L)=\inf\{x:\ P(L\le x)\ge\alpha\},$$
> c'est-à-dire le **quantile** d'ordre $\alpha$ de la perte : la perte n'est dépassée qu'avec la probabilité $1-\alpha$.

Une VaR n'a donc de sens qu'accompagnée de **trois précisions** : le niveau $\alpha$, l'**horizon** (un jour, dix jours, un an) et la **convention de signe** (ici : perte positive). « VaR à 99 % sur un jour de 2 M€ » signifie : *sur 99 jours sur 100, la perte du jour ne dépasse pas 2 M€*. Elle ne dit **ni** « la perte maximale » **ni** « ce que l'on perd les mauvais jours » : les jours où la VaR est dépassée peuvent coûter à peine plus ou bien trois fois plus, la VaR ne le saura jamais.

Un exemple à la main, sur dix pertes journalières fictives (en M€), classées de la plus petite à la plus grande : $-0{,}7$ ; $-0{,}4$ ; $-0{,}1$ ; $0{,}2$ ; $0{,}3$ ; $0{,}5$ ; $0{,}9$ ; $1{,}4$ ; $2{,}6$ ; $4{,}1$. Pour $\alpha=90\ \%$ et dix observations, le plus petit $x$ tel qu'au moins 90 % des pertes soient inférieures ou égales à $x$ est la **neuvième** valeur : la VaR à 90 % vaut 2,6 M€. Pour $\alpha=80\ \%$, c'est la huitième : 1,4 M€. Retenons la règle : avec $n$ observations, la VaR empirique est la valeur de rang $\lceil\alpha n\rceil$.

<!--sortie-->

Sur nos 4 000 jours, la VaR historique s'obtient en une ligne. L'option `method="inverted_cdf"` donne exactement la définition ci-dessus.

```python
niveaux = [0.95, 0.99, 0.999]
print(dict(zip(niveaux, np.quantile(L, niveaux, method="inverted_cdf").round(2).tolist())))
```
<!--sortie-->
```text
{0.95: 0.92, 0.99: 2.04, 0.999: 3.87}
```
<!--sortie-->

<!--sortie-->

Le portefeuille de 100 M€ a donc perdu plus de 0,92 M€ un jour sur vingt, plus de 2,04 M€ un jour sur cent et plus de 3,87 M€ un jour sur mille. Ces trois nombres sont des **mesures** : ils dépendent de la période d'observation, du portefeuille et du niveau choisi.

> 🧭 **En pratique.** Le niveau de confiance est une convention d'usage et non une loi de la nature : les cadres prudentiels retiennent des niveaux élevés (99 %, 99,9 %) parce qu'ils visent la survie, alors que la gestion interne utilise souvent 95 % pour suivre le risque courant. Plus le niveau est élevé, **moins il y a d'observations pour l'estimer** : à 99,9 % sur 4 000 jours, il n'y en a que quatre (section 3.1.9).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.1.

### 3.1.3 La VaR normale en forme close

Si l'on suppose que la perte suit une loi normale $\mathcal N(\mu,\sigma^2)$, la VaR s'écrit sans simulation.

> 📐 **Démonstration.** $P(L\le x)=\Phi\!\left(\dfrac{x-\mu}{\sigma}\right)$, où $\Phi$ est la fonction de répartition de la loi normale centrée réduite. Elle est supérieure ou égale à $\alpha$ si et seulement si $\dfrac{x-\mu}{\sigma}\ge z_\alpha:=\Phi^{-1}(\alpha)$. La plus petite valeur de $x$ est donc
> $$\boxed{\mathrm{VaR}_\alpha=\mu+\sigma\,z_\alpha}.$$
> Les quantiles utiles sont $z_{95\%}\approx1{,}645$, $z_{99\%}\approx2{,}326$ et $z_{99{,}9\%}\approx3{,}090$.

Pour un portefeuille, $\mu=\sum_iw_i\mu_i\,V$ et la variance est celle d'une combinaison linéaire : $\sigma^2=V^2\,w^\top\Sigma w$, où $\Sigma$ est la matrice de covariance des rendements. C'est la **méthode variance-covariance**, historiquement la première utilisée en salle de marché parce qu'elle ne demande qu'une matrice $n\times n$. Elle met aussi en évidence l'effet de diversification : $\sigma\le V\sum_iw_i\sigma_i$, avec égalité si et seulement si tous les actifs sont parfaitement corrélés.

Appliquons-la à notre portefeuille avec la moyenne et l'écart-type observés (-0,016 et 0,69 M€). À 95 %, on trouve 1,12 M€ (historique : 0,92), à 99 %, 1,59 M€ (historique : 2,04), à 99,9 %, 2,12 M€ (historique : 3,87).

<!--sortie-->

Le constat est net et central pour tout le chapitre : **à 95 %, la loi normale est un peu prudente, à 99 % elle sous-estime nettement la VaR historique, et à 99,9 % elle la divise presque par deux.** Une cloche de Gauss ajustée sur l'écart-type ne voit pas que notre portefeuille a des queues épaisses : l'écart-type est surtout fabriqué par les jours ordinaires, alors que la VaR à 99,9 % ne regarde que les jours exceptionnels.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.2, application 3.1.

### 3.1.4 La VaR historique et la VaR par simulation

La **VaR historique** n'invente aucune loi : elle prend les $N$ dernières pertes observées, les applique au portefeuille d'aujourd'hui et lit le quantile empirique, comme nous l'avons fait ci-dessus. Ses forces : aucune hypothèse de forme, les corrélations et les queues réelles sont préservées. Ses faiblesses : elle ne connaît que le passé (un type de crise jamais vu n'y figure pas) et elle dépend du **choix de la fenêtre**. Sur nos données, la VaR à 99 % calculée sur les 250 derniers jours vaut 2,04 M€, sur les 500 derniers jours 2,23 M€, sur les 1 000 derniers 1,84 M€ et sur les 4 000 jours 2,04 M€. Une fenêtre courte réagit vite mais oublie les crises ; une fenêtre longue se souvient mais réagit tard.

Elle a aussi un défaut discret, l'**effet fantôme** : lorsqu'une journée extrême quitte la fenêtre, la VaR chute d'un coup sans que le risque ait changé. Sur une fenêtre glissante de 500 jours, la VaR à 99 % a déjà varié de 0,57 M€ d'un jour à l'autre alors que le portefeuille était inchangé.

<!--sortie-->

La **VaR par simulation de Monte-Carlo** choisit un modèle, tire de nombreux scénarios de rendements conformes à ce modèle, revalorise le portefeuille dans chacun et lit le quantile. Elle a l'avantage de s'adapter à des portefeuilles non linéaires (options, produits complexes) que la matrice de covariance ne sait pas traiter. Mais son résultat n'est **jamais meilleur que le modèle** : avec une loi normale multivariée de mêmes moyennes et covariances, nos 200 000 scénarios redonnent la VaR à 99 % de la formule fermée, soit 1,59 M€ ; avec une loi de Student multivariée à 4 degrés de liberté, de même matrice de covariance, on obtient 1,81 M€. L'écart entre les deux ne vient pas de la simulation, il vient du **choix de la loi**.

<!--sortie-->

> 💡 **Intuition.** Les trois méthodes ne sont pas concurrentes mais complémentaires : la formule fermée est rapide et lisible, la méthode historique est honnête sur ce qui s'est passé, la simulation est souple. Un risk manager les compare : un écart important entre elles est une **information** (la queue n'est pas normale, ou la fenêtre est trop courte), pas une erreur à corriger.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.3.

### 3.1.5 Quand la volatilité change : EWMA et GARCH

Jusqu'ici nous avons supposé que l'écart-type était constant. Or l'observation du début de chapitre montrait le contraire : les mauvais jours viennent **par grappes**. Le graphique suivant montre la volatilité glissante sur 60 jours ; les zones grisées sont les périodes de stress du marché (que le simulateur connaît, mais que l'analyste ne voit pas).

![Volatilité glissante de la perte du portefeuille sur 60 jours (M€). Les bandes grisées sont les périodes de régime de stress ; la volatilité s'y envole puis retombe.](figures/ch03-volatilite-regimes.png)

<!--sortie-->

Le marché a traversé 8 épisodes de stress, d'une durée moyenne de 35 jours ; on remarque que la volatilité continue de monter ou de retomber lentement après un épisode, et qu'elle connaît aussi des pics en dehors de tout régime de stress : c'est la signature d'un modèle de volatilité de type GARCH, dans lequel un choc en appelle d'autres. Une VaR calibrée sur toute l'histoire est trop basse pendant ces épisodes et trop haute le reste du temps : elle mesure un risque moyen qui n'existe jamais. Deux familles de modèles suivent la volatilité du moment.

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
```text
omega       0.012
alpha[1]    0.099
beta[1]     0.870
nu          5.054
Name: params, dtype: float64
```
<!--sortie-->

<!--sortie-->

On lit $\hat\alpha$ = 0,099 et $\hat\beta$ = 0,870, donc une persistance de 0,969 (très proche de 1 : les chocs de volatilité s'éteignent lentement) et $\hat\nu$ = 5,1 degrés de liberté (des queues bien plus épaisses que la normale ; le simulateur en utilisait 5). Pour que la comparaison soit honnête, **les paramètres sont figés sur les 2 000 premiers jours** et nous *filtrons* ensuite la volatilité sur les 2 000 jours suivants : chaque matin, le modèle ne connaît que ce qui s'est passé la veille. Trois VaR à 99 % sur un jour sont comparées : la VaR historique et la VaR normale calibrées une fois pour toutes sur les 2 000 premiers jours, et la VaR GARCH-Student qui s'ajuste chaque jour. Le tableau donne la **fréquence des dépassements** (jours où la perte excède la VaR) ; elle devrait valoir 1 %.

| Méthode | Tous les jours | Régime calme | Régime de stress |
|---|---|---|---|
| Historique (fixe) | 1,7 % | 0,6 % | 10,4 % |
| Normale (fixe) | 2,2 % | 1,0 % | 12,8 % |
| GARCH-Student (filtrée) | 1,1 % | 0,9 % | 3,3 % |

<!--sortie-->

Les deux méthodes figées dépassent trop souvent, et **presque tous les dépassements surviennent en régime de stress**, où la fréquence monte à plus de 10 % : le jour où l'on a le plus besoin de la VaR, elle est fausse d'un facteur dix. La VaR GARCH, qui s'adapte, reste bien plus proche de 1 %, sans l'atteindre en stress (3,3 % sur 211 jours de stress) : le modèle réagit après coup, il ne **prévoit** pas les basculements de régime. Un modèle de volatilité améliore beaucoup la couverture, il ne la rend pas parfaite.

> ⚠️ **Piège.** Une VaR « historique » sur une fenêtre calme est la VaR d'une époque calme. Calculer sur une période sans crise puis annoncer que « le risque est faible » est l'erreur la plus fréquente, et la plus coûteuse.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.2.

### 3.1.6 Du jour à dix jours : la règle de la racine

Les cadres prudentiels demandent souvent un horizon de plusieurs jours (la période pendant laquelle on ne peut pas dénouer ses positions). Plutôt que de réestimer, on **met à l'échelle** par la règle de la racine carrée du temps.

> 📐 **Démonstration.** Si les pertes journalières $L_1,\dots,L_h$ sont indépendantes, de même loi, de moyenne nulle et d'écart-type $\sigma$, alors $\mathrm{Var}(L_1+\dots+L_h)=h\sigma^2$, donc l'écart-type à $h$ jours est $\sigma\sqrt h$. Si de plus la loi est normale, la somme l'est aussi et $\mathrm{VaR}_\alpha^{(h)}=\sqrt h\ \mathrm{VaR}_\alpha^{(1)}$. Avec une moyenne $\mu$ non nulle, le terme de moyenne croît en $h$ et non en $\sqrt h$.

Pour dix jours, la VaR à 99 % historique journalière de 2,04 M€ donne 6,46 M€. Mesurons maintenant la VaR sur les **sommes de dix pertes consécutives sans chevauchement** (400 observations) : 6,56 M€, soit 2 % d'écart seulement. Sur nos données, **la règle fonctionne remarquablement bien**, et pour une bonne raison : les pertes d'un jour à l'autre sont sans mémoire (leur corrélation est de -0,005), ce qui est la condition centrale de la démonstration. Elle fonctionne aussi à l'intérieur de chaque régime : le rapport entre la VaR à dix jours observée et $\sqrt{10}$ fois la VaR à un jour vaut 0,93 pour les fenêtres qui débutent en régime calme et 1,09 pour celles qui débutent en stress.

Ce bon résultat ne doit pas rassurer à l'excès : il tient à notre simulation, où les rendements sont sans autocorrélation. La règle se brise dès que les pertes ont de la **mémoire** : des portefeuilles de produits peu liquides dont les valorisations sont lissées (les pertes se propagent sur plusieurs jours, la corrélation est positive et le risque à dix jours dépasse nettement $\sqrt{10}$ fois celui d'un jour), ou des marchés qui changent de régime *pendant* la fenêtre (la corrélation entre les carrés des pertes de deux jours consécutifs vaut ici 0,11 : c'est la signature des grappes de volatilité).

<!--sortie-->

> ⚠️ **Piège.** La règle de la racine est une approximation commode, pas un théorème sur vos données : elle suppose des pertes **indépendantes** (et, pour passer à la VaR, normales). Vérifiez l'autocorrélation avant de l'appliquer, et rappelez-vous que l'horizon est une **hypothèse économique** (le temps qu'il faut pour sortir d'une position) avant d'être un paramètre statistique : les cadres prudentiels retiennent d'ailleurs des horizons différents selon la liquidité des positions (valeurs à vérifier dans les textes en vigueur).

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.5.

### 3.1.7 L'expected shortfall

La VaR dit *à partir de quelle perte* on entre dans la queue, mais pas *combien* on y perd. L'**expected shortfall** (ES, ou *perte moyenne conditionnelle*, ou CVaR) répond à la seconde question.

> 📐 **Définition.** Pour une perte $L$ de moyenne finie,
> $$\mathrm{ES}_\alpha(L)=\frac{1}{1-\alpha}\int_\alpha^1\mathrm{VaR}_u(L)\,du ,$$
> et lorsque la loi est continue, $\mathrm{ES}_\alpha=\mathbb E\,[L\mid L\ge\mathrm{VaR}_\alpha]$ : la **perte moyenne les jours où la VaR est dépassée**.

Sur nos dix pertes fictives, à 90 %, la VaR est de 2,6 M€ et l'ES est la moyenne des pertes supérieures ou égales à elle, $(2{,}6+4{,}1)/2$, soit 3,35 M€. Sur le portefeuille réel, l'ES historique à 99 % est de 2,94 M€, contre une VaR de 2,04 M€ : le rapport ES/VaR vaut 1,44. Pour une loi normale, l'ES à 99 % n'est que 1,15 fois la VaR ; un rapport nettement supérieur révèle une **queue épaisse** : lorsque la VaR est franchie, elle l'est de loin.

> 📐 **ES d'une loi normale.** Si $L\sim\mathcal N(\mu,\sigma^2)$, alors $L=\mu+\sigma Z$ avec $Z$ normale centrée réduite et $\mathrm{VaR}_\alpha=\mu+\sigma z_\alpha$. Comme $\int_z^\infty u\,\varphi(u)\,du=\varphi(z)$ (car $\varphi'(u)=-u\varphi(u)$),
> $$\mathrm{ES}_\alpha=\mu+\sigma\,\mathbb E[Z\mid Z\ge z_\alpha]=\mu+\sigma\,\frac{\varphi(z_\alpha)}{1-\alpha}.$$
> Pour $\alpha=99\ \%$ : $\varphi(2{,}326)/0{,}01\approx2{,}665$, donc $\mathrm{ES}_{99\%}\approx\mu+2{,}665\,\sigma$, à comparer à $\mu+2{,}326\,\sigma$ pour la VaR.

Avec les paramètres observés, l'ES normale à 99 % vaut 1,82 M€, très en deçà de l'ES historique (2,94 M€) : comme la VaR, elle est trompée par la queue. Notons qu'une propriété utile relie les deux mesures : pour une loi normale, l'ES à **97,5 %** vaut $\mu+2{,}338\,\sigma$, presque la VaR à 99 % ($\mu+2{,}326\,\sigma$). C'est l'une des raisons pour lesquelles certains cadres prudentiels de marché ont remplacé la VaR à 99 % par l'ES à 97,5 % (niveau à vérifier dans les textes en vigueur) : sur des données normales cela ne change presque rien, sur des queues épaisses l'ES prend en compte ce que la VaR ignore.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.3.

### 3.1.8 Cohérence : pourquoi la VaR ne diversifie pas toujours

Artzner, Delbaen, Eber et Heath ont proposé en 1999 quatre propriétés qu'une mesure de risque $\rho$ « raisonnable » devrait avoir, et appelé **cohérentes** les mesures qui les vérifient toutes : la **monotonie** (une position qui perd toujours plus a un risque plus grand), l'**invariance par translation** (ajouter de la trésorerie réduit le risque d'autant), l'**homogénéité positive** (doubler la position double le risque) et la **sous-additivité**, $\rho(L_1+L_2)\le\rho(L_1)+\rho(L_2)$ : *fusionner deux portefeuilles ne crée pas de risque*, c'est la traduction mathématique de la diversification. L'ES vérifie les quatre. La VaR vérifie les trois premières mais **pas la sous-additivité** en général.

Un contre-exemple à la main suffit. Deux prêts indépendants de 1 M€ chacun ont une probabilité de défaut de 4 % et une perte de 1 M€ en cas de défaut (perte nulle sinon). On travaille au niveau de 95 %.

- **Chaque prêt seul.** La perte vaut 1 avec la probabilité 0,04 et 0 avec la probabilité 0,96. Comme $P(L\le0)=0{,}96\ge0{,}95$, on a $\mathrm{VaR}_{95\%}=0$. La somme des deux VaR est donc **0**.
- **Les deux prêts ensemble.** La probabilité qu'aucun ne fasse défaut est $0{,}96^2=0{,}9216<0{,}95$. La perte totale vaut donc 1 ou plus avec une probabilité de $1-0{,}9216=7{,}84\ \%>5\ \%$ : $\mathrm{VaR}_{95\%}=1$ M€.

La VaR du portefeuille (1) **dépasse** la somme des VaR (0) : selon la VaR, regrouper deux prêts *augmente* le risque, ce qui contredit toute intuition de diversification. Avec l'ES à 95 % : pour un prêt seul, $\mathrm{VaR}_u=0$ pour $u\le0{,}96$ et 1 au-delà, donc $\mathrm{ES}=(0{,}04\times1)/0{,}05$, soit 0,80 M€ pour chaque prêt, soit 1,60 M€ pour les deux. Pour les deux ensemble, $P(L=0)=0{,}9216$, $P(L=1)=0{,}0768$, $P(L=2)=0{,}0016$ : l'ES vaut $[(0{,}9984-0{,}95)\times1+(1-0{,}9984)\times2]/0{,}05$, soit 1,032 M€, **inférieure** à 1,60 : l'ES respecte la diversification.

<!--sortie-->

> ⚠️ **Piège.** La VaR est parfaitement acceptable pour des pertes de loi normale (elle est alors sous-additive), et c'est précisément ce qui la rend dangereuse : le contre-exemple ne se produit que quand les pertes sont **discontinues et concentrées**, comme dans le crédit, où l'on perd tout ou rien. Dans un portefeuille de prêts, la VaR peut décourager la diversification ; l'ES, non.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.4.

### 3.1.9 Combien vaut un chiffre de queue ?

Une VaR à 99 % sur 4 000 jours repose sur les **40 plus mauvais jours** ; à 99,9 %, sur **quatre**. Avant de discuter la méthode, demandons-nous à quel point le chiffre est *stable*. Le **bootstrap** réestime la VaR sur de nombreux échantillons tirés avec remise parmi les 4 000 pertes, et le quantile de ces estimations donne un intervalle de confiance. (Il suppose des pertes indépendantes, ce qui est faux ici à cause des grappes de volatilité : l'intervalle est donc *optimiste*.)

| Mesure | Estimation | Intervalle à 95 % | Largeur relative |
|---|---|---|---|
| VaR 99 % | 2,04 M€ | [1,74 ; 2,38] | 31 % |
| ES 99 % | 2,94 M€ | [2,57 ; 3,33] | 26 % |
| VaR 99,9 % | 3,87 M€ | [3,36 ; 4,84] | 38 % |

<!--sortie-->

Même avec cet intervalle optimiste, la VaR à 99 % n'est connue qu'à ±15 % près, et la VaR à 99,9 % à ±19 % : en valeur absolue, l'intervalle est 2,3 fois plus large au niveau de 99,9 %. L'ES à 99 % est ici un peu plus stable que la VaR au même niveau, parce qu'elle moyenne les 40 plus mauvais jours au lieu de lire un seul rang, mais elle reste sensible aux quelques plus grosses pertes de l'échantillon. **Un chiffre de queue donné sans intervalle est un chiffre dont on ignore la précision.** Les techniques de la théorie des valeurs extrêmes (volume II, section 6.5) ajustent une loi à la queue pour extrapoler au-delà des données, au prix d'hypothèses supplémentaires ; nous les retrouverons en 3.3 pour les pertes opérationnelles.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.4.

<!--sortie-->

> ✅ **À retenir.**
> - La **VaR** de niveau $\alpha$ est le quantile $\alpha$ de la perte ; elle se lit avec son niveau, son horizon et sa convention de signe, et ne dit rien de ce qui se passe au-delà.
> - La **VaR normale** $\mu+\sigma z_\alpha$ est rapide mais sous-estime les queues épaisses ; la VaR **historique** est honnête mais dépend de la fenêtre ; la simulation n'est jamais meilleure que son modèle.
> - Une volatilité qui change (EWMA, GARCH) améliore beaucoup la couverture, surtout en stress, sans prévoir les basculements.
> - La règle de la racine carrée suppose des pertes indépendantes et normales ; elle sous-estime ici le risque à dix jours.
> - L'**ES** est la perte moyenne au-delà de la VaR ; elle est **cohérente** (sous-additive), alors que la VaR ne l'est pas en général.
> - Un chiffre de queue sans intervalle est un chiffre dont on ignore la précision.


## 3.2 Stress tests et scénarios

La section précédente mesurait le risque **à partir de la distribution observée** des pertes. Un stress test pose une autre question : *que se passe-t-il si… ?* Si le chômage monte de deux points, si les taux gagnent deux points, si les marchés se comportent comme pendant le pire épisode connu. Un stress test ne donne **aucune probabilité** : il décrit une situation plausible mais sévère et en chiffre les conséquences. La VaR répond « quelle est la perte d'un mauvais jour ordinaire ? », le stress test répond « quelle serait la perte d'un jour qui ne l'est pas ? ».

### 3.2.1 Pourquoi stresser, quand on a une VaR ?

Trois raisons, toutes déjà entrevues. Premièrement, la VaR historique **ne connaît que ce qui s'est produit** : un événement absent de la fenêtre n'existe pas pour elle. Deuxièmement, la VaR est un chiffre de quantile : elle ne mesure rien au-delà, alors que la survie d'un établissement se joue justement au-delà. Troisièmement, les relations estimées en période calme (volatilités, corrélations) **changent** en période de crise, comme le montre le graphique de volatilité de la section précédente. Les superviseurs et les directions des risques demandent donc les deux : une mesure statistique pour le suivi courant, des scénarios pour la résistance aux chocs.

Un bon scénario obéit à quatre critères : il est **plausible** (on peut raconter comment il arriverait), **sévère** (il fait mal), **cohérent** (ses variables bougent ensemble de façon réaliste : un krach actions sans effet sur le crédit est suspect), et **pertinent** pour le portefeuille testé (un choc sur une matière première que l'on ne détient pas ne dit rien).

### 3.2.2 Les sensibilités : un choc, un facteur

La forme la plus simple de stress est l'**analyse de sensibilité** : on fait varier **un seul** facteur de risque et l'on mesure la perte. Pour notre portefeuille de 100 M€, la perte pour une baisse de 10 % de chaque actif pris isolément est proportionnelle à son poids : 3,5 M€ pour les actions A, 1,5 M€ pour les actions B, 3 M€ pour les obligations, 1 M€ pour l'immobilier et 1 M€ pour les matières premières. Le résultat se lit en une seconde, ce qui fait son intérêt, mais il est **incohérent** : dans la réalité, les actifs ne bougent pas un par un.

Un scénario *hypothétique* construit à la main fait bouger tous les facteurs ensemble. Prenons un « krach actions » : actions A −30 %, actions B −35 %, immobilier coté −20 %, matières premières −25 %, et des obligations qui **montent** de 3 % (fuite vers la qualité). La perte est la somme pondérée des chocs :

| Actif | Montant | Choc | Perte (M€) |
|---|---|---|---|
| Actions A | 35 M€ | −30 % | 10,50 |
| Actions B | 15 M€ | −35 % | 5,25 |
| Obligations | 30 M€ | +3 % | −0,90 |
| Immobilier coté | 10 M€ | −20 % | 2,00 |
| Matières premières | 10 M€ | −25 % | 2,50 |
| **Total** | **100 M€** | | **19,35** |

La perte totale est de 19,35 M€, soit 19,4 % du portefeuille : environ 9 fois la VaR historique à 99 % d'un jour (2,04 M€). Ce rapport n'a rien d'alarmant ou de rassurant en soi : il rappelle que la VaR et le scénario ne mesurent pas la même chose, l'une un jour ordinaire sévère, l'autre une crise.

<!--sortie-->

### 3.2.3 Les scénarios historiques

Un **scénario historique** rejoue un épisode réel sur le portefeuille actuel. Il a l'immense avantage de la cohérence (les chocs se sont réellement produits ensemble) et de la crédibilité (« cela est arrivé »). Dans nos données, l'épisode le pire est la fenêtre de **dix jours consécutifs** dont la perte cumulée est la plus forte : 17,8 M€, atteinte en fenêtre terminée le 30/06/2020. À titre de comparaison, la VaR à 99 % sur dix jours obtenue par la règle de la racine (section 3.1.6) est de 6,46 M€ : le pire épisode observé coûte **2,8 fois** plus. Rien d'anormal : cet épisode se situe en régime de stress, que la VaR calibrée sur toute l'histoire dilue.

<!--sortie-->

Un scénario historique a deux limites. Il suppose que le **portefeuille d'aujourd'hui** réagit comme celui d'hier (alors que sa composition a changé), et il est **prisonnier du passé** : la prochaine crise ne ressemblera pas à la précédente. D'où la complémentarité avec les scénarios hypothétiques, qui explorent des situations jamais observées.

### 3.2.4 Des variables macroéconomiques aux défauts de crédit

Pour la banque, le stress test le plus important relie l'**économie** aux **défauts** de son portefeuille de crédits. La démarche standard comporte trois étapes : estimer un modèle statistique entre les variables macroéconomiques et le taux de défaut, construire des trajectoires macroéconomiques (de base, adverse, sévère), puis en déduire des pertes.

Nos données donnent 80 trimestres de croissance du PIB, de chômage, de variation des prix de l'immobilier et de taux de défaut annualisé du portefeuille, avec une récession entre les trimestres 48 et 54. Un taux de défaut est une proportion, comprise entre 0 et 1 : on modélise donc sa **transformation logit**, $\ln\dfrac{p}{1-p}$, par une régression linéaire des trois variables (comme pour la régression logistique, volume II, section 2.2). Un appel suffit.

```python
import statsmodels.api as sm
t = pd.read_csv("donnees/taux_defaut_macro.csv")
y = np.log(t["taux_defaut"] / (1 - t["taux_defaut"]))
X = sm.add_constant(t[["croissance_pib", "chomage", "variation_immo"]])
macro = sm.OLS(y, X).fit()
print(macro.params.round(3).to_dict(), round(macro.rsquared, 3))
```
<!--sortie-->
```text
{'const': -5.03, 'croissance_pib': -0.401, 'chomage': 0.245, 'variation_immo': -0.063} 0.989
```
<!--sortie-->

<!--sortie-->

Chaque point de croissance en plus **multiplie** les chances de défaut par 0,67 (donc les réduit), chaque point de chômage en plus les multiplie par 1,28, et le modèle explique 0,989 de la variance du logit. L'ajustement est spectaculaire, trop pour être honnête : il tient à ce que les données sont simulées avec une relation de ce type. Il faut donc lui faire passer l'épreuve que la réalité imposerait : **a-t-il prévu la crise avant de la voir ?** Réestimons le modèle sur les seuls 44 premiers trimestres (calmes) et comparons sa prédiction au taux réellement observé pendant la récession.

![Taux de défaut observé (courbe pleine) et prédit par le modèle estimé sur les 44 premiers trimestres seulement (tirets). La zone grisée est la récession.](figures/ch03-modele-macro.png)

<!--sortie-->

Le modèle appris **avant** la crise en annonce un sommet de 12,0 % contre 12,8 % observé, avec une erreur quadratique moyenne de 0,23 point sur les 36 trimestres suivants. C'est un très bon résultat, et il faut l'interpréter avec méfiance : dans nos données la relation macro-défaut est **stable** par construction. Dans la réalité, trois obstacles se dressent : l'échantillon est court (quelques dizaines de trimestres, une ou deux récessions), les variables macroéconomiques sont corrélées entre elles (les coefficients individuels sont instables), et surtout la relation **change** quand le comportement des emprunteurs ou la politique d'octroi change. Un modèle qui a bien « prédit » une crise passée n'a pas démontré qu'il prédira la suivante.

> ⚠️ **Piège.** Un excellent $R^2$ sur 80 points et trois variables explicatives d'allure économique n'est pas une preuve de causalité ni de stabilité. Les modèles de stress test sont fréquemment estimés sur très peu de crises : on teste leur **robustesse** (changer la période, retirer une variable) plus qu'on ne célèbre leur ajustement.

### 3.2.5 Du scénario aux pertes de crédit

Reste à définir les scénarios et à traduire les taux de défaut en pertes. Nous prenons un portefeuille de crédits de **500 M€** d'encours (EAD) et une perte en cas de défaut (LGD) égale à la moyenne des pertes observées sur nos défauts passés, soit 45,9 % (fichier `recouvrements.csv`, chapitre 1). La perte annuelle attendue est le taux de défaut moyen de l'année multiplié par l'encours et par la LGD. Trois trajectoires de quatre trimestres sont comparées : le **scénario de base** prolonge la moyenne des quatre derniers trimestres (croissance de 1,3 %, chômage de 8,2 %) ; le **scénario adverse** reproduit une récession comparable à la pire observée (croissance de −1,5 %, chômage montant à 9,5 %, immobilier −3 % par trimestre) ; le **scénario sévère** va au-delà de tout ce que nos 80 trimestres ont connu (croissance de −3 %, chômage à 11 %, immobilier −6 %).

| Scénario | Croissance | Chômage (fin) | Immobilier | Taux de défaut moyen | Perte annuelle | En % de l'encours |
|---|---|---|---|---|---|---|
| Base | 1,3 % | 8,2 % | -0,2 % | 2,8 % | 6,5 M€ | 1,3 % |
| Adverse | −1,5 % | 9,5 % | −3,0 % | 11,7 % | 26,8 M€ | 5,4 % |
| Sévère | −3,0 % | 11,0 % | −6,0 % | 27,0 % | 61,8 M€ | 12,4 % |

<!--sortie-->

La perte annuelle passe de 6,5 M€ en base à 26,8 M€ en scénario adverse (un facteur 4,1) puis à 61,8 M€ en sévère. Deux remarques s'imposent. D'abord, la **non-linéarité** : une récession de l'ampleur de la pire observée multiplie la perte par 4,1, parce que le logit transforme une somme de petits effets en une explosion du taux. Ensuite, le scénario sévère aboutit à un taux de défaut de 27,0 %, plus du double du maximum jamais observé dans l'échantillon (12,8 %) : le modèle **extrapole** loin de ses données, et son résultat n'a plus la même fiabilité que celui du scénario adverse. Un chiffre de stress est d'autant moins sûr qu'il est extrême, ce que les superviseurs savent et c'est pourquoi les résultats sont toujours présentés avec leurs hypothèses.

Enfin, la perte de crédit n'est qu'une partie du tableau. Un vrai stress test fait aussi varier les **marges d'intérêt**, les **valeurs de garantie** (donc la LGD, qui augmente quand l'immobilier baisse), les **provisions** et le **coût du risque**, puis consolide le tout dans une évolution du **ratio de fonds propres** (chapitre 4). Retenons le principe : on enchaîne *scénario macro → variables de risque → pertes → capital*.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.5, exercice 3.6.

### 3.2.6 Le choc de taux d'intérêt

Une banque et surtout une mutuelle d'assurance détiennent beaucoup d'obligations : leur valeur dépend de la courbe des taux. Une obligation de coupon $c$, de nominal 100 et de maturité $T$ a pour prix $P=\sum_{t=1}^{T}\dfrac{\text{flux}_t}{(1+y_t)^t}$, où $y_t$ est le taux d'actualisation de l'échéance $t$ lu sur la courbe. Quand les taux montent, le prix baisse, d'autant plus que la maturité est longue.

> 📐 **Duration et convexité.** Par un développement de Taylor du prix en fonction d'un déplacement parallèle $\Delta y$ de la courbe, $\dfrac{\Delta P}{P}\approx-D\,\Delta y+\dfrac12\,C\,(\Delta y)^2$, où $D=-\dfrac{1}{P}\dfrac{dP}{dy}$ est la **duration modifiée** et $C=\dfrac1P\dfrac{d^2P}{dy^2}$ la **convexité**. La duration est la sensibilité de premier ordre ; la convexité corrige la courbure (le prix baisse moins que ne le prévoit la droite quand les taux montent, et monte plus quand ils baissent).

Prenons trois obligations (2 ans à 2 %, 5 ans à 3 %, 10 ans à 3,5 %) actualisées sur la courbe du dernier mois de nos données, et chiffrons l'effet d'un choc parallèle de +100, +200 et +300 points de base (pb) sur l'obligation à 10 ans, dont la duration est de 8,5 et la convexité de 86.

| Choc | Prix exact | Duration seule | Duration + convexité |
|---|---|---|---|
| +100 pb | -8,1 % | -8,5 % | -8,0 % |
| +200 pb | -15,3 % | -16,9 % | -15,2 % |
| +300 pb | -21,9 % | -25,4 % | -21,5 % |

La duration seule surestime la baisse (elle ne voit pas que la courbe du prix se redresse) et l'erreur grossit avec le choc ; l'ajout de la convexité ramène l'écart à 0,4 point sur +300 pb. Pour un choc de faible amplitude, l'approximation est excellente ; pour un stress, on **réévalue intégralement** le portefeuille (c'est ce que fait la colonne « prix exact »).

![Variation du prix de l'obligation à 10 ans selon le choc parallèle de taux : réévaluation exacte (trait plein), approximation par la duration (tirets) et par duration et convexité (pointillés).](figures/ch03-taux-duration.png)

<!--sortie-->

Un choc parallèle est trop simple : les courbes réelles **se déforment** (pentification, aplatissement). Un scénario *historique de taux* applique à la courbe actuelle la déformation observée entre deux dates. Entre les mois 60 et 90 de nos données (le cycle de hausse), les taux ont monté de 120 pb à 3 mois, de 127 pb à 1 an et jusqu'à 177 pb à 30 ans. Appliquée à trois obligations de 10 M€ chacune, cette déformation coûte 2,19 M€ (soit 7,3 % du portefeuille obligataire), contre 1,44 M€ pour un choc parallèle de +100 pb : la forme du choc compte autant que son ampleur.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.6, exercice 3.7.

### 3.2.7 Le stress test inversé

Un stress test classique part d'un scénario et calcule la perte. Le **stress test inversé** (*reverse stress test*) fait le chemin contraire : il part d'un **résultat inacceptable** (le capital est épuisé, le ratio passe sous le seuil) et cherche *quel scénario y conduit*, puis demande s'il est plausible. L'exercice est salutaire parce qu'il oblige à regarder les vulnérabilités que les scénarios « raisonnables » n'effleurent pas.

Supposons que les fonds propres disponibles pour absorber les pertes de crédit s'élèvent à **25 M€** (5 % de l'encours). Paramétrons une famille de scénarios qui va continûment du scénario de base ($s=0$) au scénario sévère ($s=1$), et cherchons l'intensité $s$ pour laquelle la perte annuelle atteint 25 M€. On trouve $s=$ 56 % de la distance entre base et sévère, ce qui correspond à une croissance de -1,1 % et à un chômage de 9,8 % en fin d'année. Ce scénario est **moins sévère que la récession déjà observée** dans l'échantillon (croissance minimale de -1,6 %, chômage maximal de 10,2 %) : le coussin de 25 M€ ne résisterait pas à une récession plus douce que celle que le portefeuille a déjà connue. C'est une conclusion que ni la VaR ni un scénario « raisonnable » n'auraient fait apparaître.

<!--sortie-->

Le raisonnement inversé est précieux justement parce qu'il évite le piège du scénario « confortable » : il ne dit pas si la banque est solide, il dit **ce qu'il faudrait pour qu'elle ne le soit plus**, et laisse la direction juger si c'est crédible.

### 3.2.8 Quand les corrélations montent

Dernier point, essentiel : la diversification **disparaît quand on en a le plus besoin**. Le graphique compare les corrélations estimées sur les jours calmes et sur les jours de stress de nos données.

![Corrélations des rendements journaliers entre actifs, estimées sur les jours calmes (à gauche) et sur les jours de stress (à droite). Les actions, l'immobilier et les matières premières se resserrent ; les obligations restent presque indépendantes.](figures/ch03-correlations-regimes.png)

<!--sortie-->

La corrélation entre les actions A et les actions B passe de 0,57 à 0,89, celle entre les actions A et l'immobilier de 0,43 à 0,87, alors que celle avec les obligations reste proche de zéro (-0,08 puis 0,01). Mesurons l'effet de diversification par le rapport entre l'écart-type du portefeuille et la somme des écarts-types pondérés des actifs (1 = aucune diversification, 0 = diversification totale) : il vaut 0,70 en jours calmes, mais 0,83 en jours de stress. **La diversification a perdu une part importante de son effet au moment où elle devait servir.** La VaR normale à 99 % vaut 1,33 M€ avec les caractéristiques des jours calmes, 3,63 M€ avec celles des jours de stress : le seul changement de régime multiplie le risque par 2,7.

<!--sortie-->

C'est la raison pour laquelle les scénarios de stress **n'utilisent pas les corrélations moyennes** : ils appliquent des corrélations de crise (souvent proches de 1 pour les actifs risqués), ou, comme dans notre scénario « krach » de 3.2.2, des chocs simultanés.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.8 (pour le stress inversé).

### 3.2.9 Gouvernance et limites des stress tests

Un stress test n'est utile que si l'on en tire une décision. Trois précautions résument la pratique. **Gouvernance** : les scénarios sont proposés par la fonction de gestion des risques, **discutés** par la direction, **révisés** régulièrement, et les résultats sont reliés à des **actions** (réduire une exposition, relever le capital, préparer un plan de financement). **Limites** : un scénario est une histoire parmi d'autres ; il y a un risque de se concentrer sur la crise passée (le « dernier conflit »), d'ignorer les effets de second tour (une vente forcée fait baisser les prix, qui déclenche d'autres ventes), et de croire à la précision des chiffres (voir le modèle macro, qui extrapole). **Complémentarité** : le stress test ne remplace pas la VaR, il la complète. La VaR dit comment le risque courant se répartit, le stress dit où l'on casse.

> ✅ **À retenir.**
> - Un stress test répond à « et si ? » ; il ne donne **aucune probabilité**, mais une perte conditionnelle à un scénario plausible et sévère.
> - On distingue sensibilités (un facteur), scénarios historiques (cohérents, mais prisonniers du passé) et scénarios hypothétiques (construits, plus libres).
> - Un scénario macroéconomique relie l'économie aux défauts par un modèle statistique : *macro → taux de défaut → perte → capital*. Les relations extrapolées au-delà des données sont moins fiables.
> - Un choc de taux se chiffre par duration et convexité pour les petits chocs, par réévaluation complète pour les grands ; la **forme** du choc compte.
> - Le stress test **inversé** part d'un résultat inacceptable et cherche le scénario qui y mène.
> - Les corrélations montent en crise : la diversification mesurée en période calme est un mirage au moment où l'on en a besoin.


## 3.3 ➕ Pour aller plus loin : risques opérationnel, de marché et de liquidité

> 🧭 **Section optionnelle.** Les sections 3.1 et 3.2 suffisent pour la suite du volume. Celle-ci applique les mêmes idées à trois autres familles de risques : les **incidents opérationnels** (où les queues épaisses dominent tout), les **contributions au risque** d'un portefeuille de marché, et la **liquidité** (où l'on ne manque pas de valeur, mais de temps).

### 3.3.1 Le risque opérationnel et la distribution des pertes

Le **risque opérationnel** est le risque de perte résultant de processus, de personnes ou de systèmes inadéquats ou défaillants, ou d'événements extérieurs : une fraude, une erreur de traitement, une panne informatique, une pratique commerciale défaillante. Les cadres prudentiels le répartissent classiquement en sept catégories d'événements ; notre jeu de données en retient cinq. Il se distingue des risques de marché et de crédit par un trait : on ne le **prend** pas pour gagner un rendement. On le subit.

La méthode de référence pour le chiffrer est l'**approche par distribution des pertes** (*loss distribution approach*, LDA). La perte annuelle est la somme d'un nombre aléatoire d'incidents, chacun de montant aléatoire :
$$S=\sum_{i=1}^{N}X_i ,\qquad N\sim\text{Poisson}(\lambda),\quad X_i\ \text{indépendantes, de même loi}.$$
On modélise donc séparément la **fréquence** $N$ et la **sévérité** $X$, comme en assurance (chapitre 2), puis on combine les deux par simulation. On en tire la **perte attendue** $\mathbb E[S]$ et la **perte inattendue** $\mathrm{VaR}_\alpha(S)-\mathbb E[S]$, celle que le capital est censé couvrir.

### 3.3.2 Ajuster la fréquence et la sévérité

Notre fichier contient 1802 incidents sur dix ans. Leur nombre annuel va de 158 à 214, avec une moyenne de 180,2. Pour une loi de Poisson, la variance égale la moyenne ; ici le rapport variance/moyenne vaut 2,4. L'écart vient surtout d'une **tendance** : le nombre d'incidents croît de 3,1 % par an en moyenne. On garde dans la suite une fréquence constante de 180,2 incidents par an pour ne pas surcharger l'exemple, en sachant qu'une estimation sérieuse la ferait croître.

La **sévérité** est le vrai sujet. La perte nette médiane est de 2 358 €, la moyenne de 14 238 € : la moyenne vaut plusieurs fois la médiane, signe d'une queue lourde. Le plus gros incident a coûté 1,8 M€. Un seul modèle ne s'ajuste pas bien à l'ensemble : on coupe en deux. Le **corps** (pertes inférieures à 100 000 €) est ajusté par une loi log-normale. La **queue** (les 53 incidents au-delà de 100 000 €, soit 2,9 % des cas) est ajustée par une **loi de Pareto généralisée** (GPD), que la théorie des valeurs extrêmes (volume II, section 6.5) désigne comme la loi limite des excès au-dessus d'un seuil élevé. Son paramètre $\xi$ décide de tout : il mesure l'épaisseur de la queue. Si $\xi<1$ la perte moyenne est finie ; si $\xi\ge1$, la moyenne **n'existe pas** (infinie), et plus on collecte de données, plus la moyenne observée grossit.

```python
from scipy import stats
net = pd.read_csv("donnees/pertes_operationnelles.csv")["perte_nette"].values
exces = net[net > 100000] - 100000
xi, _, echelle = stats.genpareto.fit(exces, floc=0)
print(len(exces), round(xi, 2), round(echelle))
```
<!--sortie-->
```text
53 0.99 57811
```
<!--sortie-->

<!--sortie-->

On lit $\hat\xi$ = 0,99 pour une échelle de 58 k€, avec seulement 53 observations. Un $\hat\xi$ proche de 1 signifie une queue extrêmement lourde ; mais **53 points ne permettent pas de trancher** : nous mesurerons plus bas l'incertitude de cette estimation. Notons aussi une subtilité de méthode : les pertes **nettes** (après récupérations, assurances) sont 5,7 % plus faibles que les pertes **brutes** (annuel : 2,57 M€ nets contre 2,72 M€ bruts). Selon les approches, on modélise les pertes brutes ou nettes ; la différence reflète ce que l'assurance et les recours couvrent, qui n'est jamais garanti à l'avance.

### 3.3.3 La perte agrégée et l'instabilité du 99,9 %

On simule 20 000 années : pour chacune, on tire le nombre d'incidents (loi de Poisson de moyenne 180,2) puis la perte de chaque incident dans le modèle ajusté (corps log-normal tronqué, queue GPD), et l'on somme. Voici ce que donne la même simulation avec trois graines différentes.

| Graine | Perte annuelle moyenne | VaR 99 % | VaR 99,9 % |
|---|---|---|---|
| 1 | 10,6 M€ | 32 M€ | 264 M€ |
| 2 | 4,8 M€ | 29 M€ | 206 M€ |
| 3 | 6,6 M€ | 33 M€ | 365 M€ |
| *Observé sur dix ans* | *2,57 M€* | *max annuel 6,7 M€* | |

Trois enseignements, du plus anodin au plus grave. **La VaR à 99 %** est assez stable d'une graine à l'autre (29 à 33 M€) mais reste très supérieure au pire exercice observé en dix ans (6,7 M€) : un modèle ajusté sur dix ans ne peut pas être contredit par dix ans de données au niveau 99 %. **La perte moyenne simulée** est de l'ordre de 5 à 11 M€ selon la graine, contre 2,57 M€ observés : avec $\hat\xi$ proche de 1, la moyenne est instable parce qu'une seule perte colossale fait basculer l'année. **La VaR à 99,9 %** varie de 206 à 365 M€ selon la graine : un facteur 1,8 entre la plus petite et la plus grande, sans que rien n'ait changé que le générateur aléatoire. Ce n'est pas un défaut de la simulation (on a déjà 20 000 années) : c'est la signature d'une queue à variance infinie.

Reste l'incertitude sur le **paramètre** lui-même. Rééchantillonnons les 1802 incidents avec remise, ré-ajustons la GPD et recalculons la VaR à 99,9 % (100 rééchantillons, 5 000 années simulées chacun). Le paramètre $\hat\xi$ varie de 0,49 à 1,55 (intervalle à 95 %) et dépasse 1 dans 31 % des cas ; la VaR à 99,9 % médiane vaut 179 M€, et sa borne basse 10 M€. **La borne haute n'a aucun sens économique** (plusieurs milliards d'euros) : quand $\hat\xi$ dépasse 1, le modèle prédit des pertes qu'aucune institution ne subirait sans disparaître.

![À gauche : probabilité qu'un incident dépasse un montant (échelles logarithmiques), observée (points) et ajustée par la GPD au-delà de 100 000 € (trait). À droite : VaR à 99,9 % (échelle logarithmique) pour 100 rééchantillonnages des données ; le trait vertical marque le pire exercice annuel observé en dix ans.](figures/ch03-operationnel.png)

<!--sortie-->

> ⚠️ **Piège.** Une VaR à 99,9 % calculée sur dix ans de données opérationnelles est une extrapolation à *mille* ans. Elle exige une queue modélisée, un seuil choisi, un paramètre estimé sur quelques dizaines de points : chacun de ces choix peut multiplier le résultat par dix. Les praticiens bornent donc les pertes (une perte maximale plausible par événement), combinent les données internes avec des données externes et des **scénarios d'experts**, et présentent le chiffre avec sa plage d'incertitude. Avec un plafond de 50 M€ par incident, la VaR à 99,9 % du même modèle tombe à 55 M€ : le plafond *est* l'hypothèse qui décide.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.7, exercice 3.10.

### 3.3.4 Risque de marché : sensibilités et contributions

Le risque de marché est celui que nous avons traité en 3.1 et 3.2 : la perte vient de la variation des prix des actifs, des taux, des changes. Deux outils complètent la VaR pour la gestion.

La **sensibilité** à un facteur est la perte pour une variation donnée de ce facteur (1 point de base de taux, 1 % d'un indice). Pour une position linéaire, c'est le produit du montant par la variation ; pour une option, il faut les « grecques » (*delta*, *gamma*, *vega*), qui sortent du cadre de ce volume.

La **période de détention** est le temps nécessaire pour dénouer ou couvrir une position ; elle fixe l'horizon de la mesure (section 3.1.6). Les actifs peu liquides (immobilier non coté, obligations d'émetteurs peu actifs) ont une période plus longue, donc un risque plus élevé *à mesure équivalente*.

La **contribution au risque** répond à la question « qui, dans mon portefeuille, fabrique le risque ? ». La réponse n'est pas le poids : l'écart-type du portefeuille $\sigma_p=\sqrt{w^\top\Sigma w}$ est une fonction homogène de degré 1 des poids, donc, par le théorème d'Euler,
$$\sigma_p=\sum_i w_i\,\frac{\partial\sigma_p}{\partial w_i},\qquad \frac{\partial\sigma_p}{\partial w_i}=\frac{(\Sigma w)_i}{\sigma_p},$$
et la **contribution** de l'actif $i$ est $w_i(\Sigma w)_i/\sigma_p$, dont la somme sur les actifs redonne $\sigma_p$. La part de chaque actif dans le risque total est alors son poids multiplié par sa covariance avec le portefeuille, divisé par la variance du portefeuille.

| Actif | Poids | Part du risque (jours calmes) | Part du risque (jours de stress) |
|---|---|---|---|
| Actions A | 35 % | 57,2 % | 51,8 % |
| Actions B | 15 % | 25,7 % | 25,6 % |
| Obligations | 30 % | 0,5 % | 1,0 % |
| Immobilier coté | 10 % | 7,5 % | 8,6 % |
| Matières premières | 10 % | 9,0 % | 12,9 % |

Les obligations pèsent 30 % du portefeuille et ne contribuent presque pas au risque (0,5 % en jours calmes) : elles sont peu volatiles et peu corrélées au reste. À l'inverse, les actions A (35 % du capital) fournissent plus de la moitié du risque. En régime de stress, la part des matières premières passe de 9,0 % à 12,9 %, parce que leur corrélation avec les actions augmente : **la structure du risque, pas seulement son niveau, dépend du régime**. Un gestionnaire qui réduit une position pour « réduire le risque » doit regarder sa contribution, pas son poids.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.9.

### 3.3.5 Risque de liquidité : le coussin et le temps

Le **risque de liquidité** est le risque de ne pas pouvoir honorer ses engagements à temps, même en étant solvable. Une banque finance des crédits à long terme avec des dépôts à vue : la **transformation d'échéances** est son métier et sa fragilité. On distingue le risque de **liquidité de financement** (les prêteurs ne renouvellent plus) et de **liquidité de marché** (on ne peut vendre un actif qu'avec une forte décote).

Un exemple chiffré. Une banque fictive a le bilan suivant (en M€) : à l'actif, 60 de réserves auprès de la banque centrale, 90 de titres publics, 700 de crédits, 50 d'autres actifs ; au passif, 540 de dépôts de particuliers, 220 de financements de marché à court terme, 80 de dettes longues, 60 de fonds propres. Un **ratio de liquidité simplifié** compare le coussin d'actifs liquides aux sorties de trésorerie sur trente jours dans un scénario de stress : $\text{ratio}=\dfrac{\text{actifs liquides de haute qualité}}{\text{sorties nettes à 30 jours}}$. (Les ratios réglementaires existent sous cette forme avec des taux de retrait et des décotes fixés par les textes ; les valeurs ci-dessous sont **illustratives**.)

- **Coussin** : 60 de réserves plus 90 de titres publics avec une décote de 10 % en cas de vente, soit 141 M€.
- **Scénario modéré** : 8 % des dépôts de particuliers et 40 % des financements de marché partent. Les sorties valent $540\times8\,\%+220\times40\,\%=131,2$ M€, le ratio 107 % : le coussin couvre tout juste.
- **Scénario sévère** : 15 % et 70 %. Les sorties atteignent 235 M€ et le ratio tombe à 60 % : il faudrait vendre des crédits (invendables en trente jours) ou s'adresser à la banque centrale.

Le raisonnement inversé s'applique encore : si une même fraction $f$ de tous les financements instables ($540+220=760$ M€) s'enfuyait, le coussin serait épuisé pour $f=141/760=18,6$ %. Ce chiffre dit **à quelle vitesse la confiance peut disparaître** avant que la banque ne puisse plus payer : une banque parfaitement solvable peut ainsi faire faillite par manque de liquidité, ce que la VaR de marché ne voit pas.

<!--sortie-->

> ✅ **À retenir.**
> - Le risque **opérationnel** se chiffre par fréquence × sévérité (LDA) ; sa queue est lourde, et un paramètre $\xi$ proche ou supérieur à 1 rend la moyenne et les quantiles extrêmes **instables**.
> - Un quantile à 99,9 % sur dix ans de données est une extrapolation : on le borne, on le complète par des scénarios d'experts, et on le publie avec sa plage d'incertitude.
> - La **contribution** d'un actif au risque (Euler) n'est pas son poids ; elle change avec le régime.
> - Une banque solvable peut manquer de **liquidité** : on compare un coussin à des sorties de stress, et l'on cherche le taux de retrait qui l'épuise.


## 3.4 ➕ Pour aller plus loin : backtesting et validation des modèles

> 🧭 **Section optionnelle.** Un modèle de risque est une promesse (« la perte dépassera ce montant un jour sur cent ») que l'on peut **vérifier** : chaque jour la réalité répond. Cette section apprend à lire la réponse avec les tests de Kupiec et de Christoffersen, à en voir les limites, puis à situer le backtest dans la démarche plus large de **validation** d'un modèle.

### 3.4.1 Le principe du backtest

Un **backtest** compare, jour après jour, la VaR prévue à la perte réalisée. À la date $t$, on connaît la prévision $\mathrm{VaR}_t$ (calculée avec l'information de la veille) et l'on observe la perte $L_t$. Le **dépassement** (*exception* ou *violation*) est l'indicateur $I_t=\mathbf 1\{L_t>\mathrm{VaR}_t\}$. Si le modèle est bon au niveau $\alpha$, la suite des $I_t$ doit avoir deux propriétés :

1. **La couverture inconditionnelle** : la probabilité d'un dépassement est $p=1-\alpha$ (1 % pour une VaR à 99 %). Sur $n$ jours, le nombre de dépassements suit une loi binomiale de paramètres $n$ et $p$.
2. **L'indépendance** : un dépassement aujourd'hui ne rend pas un dépassement demain plus probable. Des dépassements **groupés** signalent un modèle qui réagit trop lentement aux changements de régime : même si leur nombre total est correct, ils tombent justement les jours où il aurait fallu être prudent.

Les deux tests qui suivent vérifient chacune de ces propriétés. L'ensemble est la **couverture conditionnelle**.

> 💡 **Intuition.** Ce n'est pas un test sur l'ampleur des pertes mais sur la **fréquence et la répartition des surprises**. Une VaR peut passer parfaitement le backtest et être inutile : celle qui annonce toujours une perte immense dépasse rarement, mais coûte du capital pour rien. Le backtest mesure l'honnêteté, pas l'utilité.

### 3.4.2 Le test de Kupiec

Si $x$ est le nombre de dépassements sur $n$ jours, l'estimation naturelle de la probabilité de dépassement est $\hat\pi=x/n$. Le **test du rapport de vraisemblance de Kupiec** (test de la proportion de dépassements, POF) compare la vraisemblance binomiale sous l'hypothèse $\pi=p$ à celle obtenue avec $\hat\pi$.

> 📐 **Statistique de Kupiec.** La vraisemblance d'une série de $n$ épreuves de Bernoulli contenant $x$ succès est $\pi^x(1-\pi)^{n-x}$. La statistique
> $$\mathrm{LR}_{\mathrm{POF}}=-2\ln\frac{(1-p)^{\,n-x}\,p^{\,x}}{(1-x/n)^{\,n-x}\,(x/n)^{\,x}}$$
> suit asymptotiquement, sous l'hypothèse nulle, une loi du $\chi^2$ à **un** degré de liberté ; on rejette au seuil de 5 % si elle dépasse 3,84.

Exemple à la main : pour $n=250$ jours, un niveau de 99 % ($p=0{,}01$) et $x=6$ dépassements (alors que 2,5 sont attendus), la statistique vaut 3,56, soit une probabilité critique de 0,059 : à 5 %, on ne rejette pas, de peu. Avec 7 dépassements, la statistique monterait à 5,50 et l'on rejetterait. La frontière est étroite : un jour de plus ou de moins change le verdict.

<!--sortie-->

### 3.4.3 Le test de Christoffersen

Le test d'**indépendance** de Christoffersen regarde les enchaînements : après un jour sans dépassement, quelle est la probabilité $\pi_{01}$ d'en avoir un le lendemain ? Après un jour avec dépassement, quelle est la probabilité $\pi_{11}$ d'en avoir un autre ? Sous l'indépendance, $\pi_{01}=\pi_{11}$. On compte les quatre types de transitions $n_{00},n_{01},n_{10},n_{11}$, on estime $\hat\pi_{01}=\dfrac{n_{01}}{n_{00}+n_{01}}$ et $\hat\pi_{11}=\dfrac{n_{11}}{n_{10}+n_{11}}$, et la statistique du rapport de vraisemblance suit un $\chi^2$ à un degré de liberté. Additionner les deux statistiques donne un test **conjoint** de couverture conditionnelle, de loi $\chi^2$ à deux degrés de liberté : $\mathrm{LR}_{\mathrm{CC}}=\mathrm{LR}_{\mathrm{POF}}+\mathrm{LR}_{\mathrm{IND}}$.

### 3.4.4 Le backtest de quatre méthodes

Passons à des données. À chaque jour à partir du 1 001ᵉ, quatre méthodes prévoient la VaR à 99 % du lendemain : la **historique** (fenêtre de 500 jours), la **normale** (moyenne et écart-type de la même fenêtre), l'**EWMA** ($\lambda=0{,}94$) et le **GARCH-Student** (paramètres réestimés tous les 250 jours sur les 1 000 derniers jours). Les 3 000 jours de test donnent, pour chaque méthode, le nombre de dépassements (1 % attendu, soit 30), les probabilités critiques des deux tests, la fréquence de dépassement par régime (invisible à l'analyste mais connue du simulateur) et la **perte d'étalonnage** moyenne (voir plus bas).

| Méthode | Dépassements | Fréquence | Kupiec (p) | Christoffersen (p) | Fréquence en calme | Fréquence en stress | Perte d'étalonnage |
|---|---|---|---|---|---|---|---|
| Historique (500 j) | 44 | 1,47 % | 0,016 | 0,029 | 0,7 % | 9,8 % | 3,25 |
| Normale (500 j) | 62 | 2,07 % | < 0,001 | 0,184 | 1,1 % | 12,1 % | 3,20 |
| EWMA | 56 | 1,87 % | < 0,001 | 0,144 | 1,6 % | 4,5 % | 2,59 |
| GARCH-Student | 36 | 1,20 % | 0,286 | 0,350 | 1,0 % | 3,8 % | 2,50 |

![Perte quotidienne du portefeuille (points gris), VaR à 99 % de la méthode historique (orange) et du GARCH-Student (bleu), avec les dépassements de chaque méthode marqués (croix) sur les 3 000 jours de test. Les bandes grisées sont les périodes de stress.](figures/ch03-backtest.png)

La lecture est instructive. La méthode **normale** et l'**EWMA** dépassent nettement trop souvent (62 et 56 dépassements pour 30 attendus) : le test de Kupiec les rejette sans hésitation. La méthode **historique** est plus proche mais encore rejetée (44 dépassements, probabilité critique de Kupiec 0,016) et elle dépasse presque 15 fois plus souvent en stress qu'en calme. Le **GARCH-Student** est la seule des quatre dont la fréquence globale (1,20 %) est compatible avec 1 % au sens du test (probabilité critique de 0,286), et c'est aussi celle dont la perte d'étalonnage est la plus faible. Mais regardons la colonne du stress : même le meilleur modèle dépasse **3,8 %** du temps en régime de stress (au lieu de 1 %). Les dépassements du GARCH se concentrent dans les basculements : le modèle suit la volatilité, il ne **prévoit** pas qu'elle va changer.

Quant à l'indépendance, aucune méthode n'est rejetée au seuil de 1 % ; la méthode historique l'est à 5 % (probabilité critique de 0,029) : ses dépassements arrivent en grappes, comme on pouvait s'y attendre d'une fenêtre qui oublie lentement la volatilité récente.

<!--sortie-->

> ⚠️ **Piège.** « Le modèle a passé le backtest » ne veut pas dire « le modèle est juste ». Cela veut dire « sur cette période, avec ce niveau, on n'a pas pu prouver qu'il avait tort ». La section suivante montre à quel point un test à 250 jours est myope.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.8, exercice 3.11.

### 3.4.5 Un test qui voit mal : la puissance

Un test statistique a un **niveau** (la probabilité de rejeter à tort un bon modèle) et une **puissance** (la probabilité de rejeter un mauvais modèle). Calculons-la exactement pour le test de Kupiec, en sommant la loi binomiale sur les nombres de dépassements qui conduisent au rejet. Supposons un modèle dont la vraie fréquence de dépassement serait de 2 % au lieu de 1 %, c'est-à-dire une VaR qui **sous-estime d'un facteur deux** la probabilité de la queue.

| Taille de l'échantillon | Puissance pour une vraie fréquence de 1,5 % | Puissance pour 2 % |
|---|---|---|
| 250 jours (un an) | 11 % | 24 % |
| 1 000 jours | 34 % | 78 % |
| 3 000 jours | 69 % | 99 % |

Sur un an, un modèle dont la fréquence réelle de dépassement est le **double** de celle annoncée n'est détecté que 24 fois sur 100. Même après trois ans de données, une fréquence de 1,5 % n'est repérée qu'environ 69 fois sur 100. **Un backtest de 250 jours ne distingue presque rien** : c'est la raison pour laquelle les cadres prudentiels se contentent de seuils larges (le « feu tricolore » ci-dessous) et pourquoi un modèle ne se valide pas sur le seul backtest.

<!--sortie-->

### 3.4.6 Le feu tricolore

Plutôt que de tester, on peut **classer**. La zone dans laquelle tombe le nombre de dépassements sur 250 jours pour une VaR à 99 % se détermine par la loi binomiale $B(250;\,0{,}01)$ : on est en zone **verte** tant que la probabilité cumulée du nombre observé reste inférieure à 95 %, en zone **orange** (ou jaune) jusqu'à 99,99 %, en zone **rouge** au-delà. En calculant ces probabilités on retrouve les seuils usuels, 4 dépassements au plus pour le vert, 5 à 9 pour l'orange, 10 et plus pour le rouge.

| Dépassements sur 250 jours | 0 | 2 | 4 | 5 | 7 | 9 | 10 |
|---|---|---|---|---|---|---|---|
| Probabilité cumulée | 8,11 | 54,32 | 89,22 | 95,88 | 99,60 | 99,97 | 99,99 |
| Zone | verte | verte | verte | orange | orange | orange | rouge |

Dans le cadre réglementaire de marché de la fin des années 1990, la zone orange ou rouge entraîne une majoration du facteur multiplicatif appliqué à la VaR pour déterminer le capital (de quelques dixièmes à un point entier, valeurs **à vérifier dans les textes en vigueur**). Sur les 250 derniers jours de notre échantillon, la VaR historique a connu 2 dépassements et la VaR GARCH 4 : toutes deux en zone verte, alors que la VaR historique a été rejetée par le test de Kupiec sur les 3 000 jours. **Sur la fenêtre d'un an, rien ne distingue le bon modèle du mauvais.**

<!--sortie-->

### 3.4.7 Backtester l'expected shortfall

Un backtest de VaR ne regarde que la **fréquence** des dépassements ; il ignore leur **ampleur**. Or l'ES a pour rôle de dire de combien on dépasse. Contrôler une ES est plus difficile que contrôler une VaR : il y a peu de dépassements (30 attendus sur 3 000 jours), et la grandeur à comparer est une moyenne conditionnelle. Plusieurs tests existent (le principe est dû, entre autres, à Acerbi et Székely) ; nous nous contentons ici d'un **contrôle de bon sens** : sur les jours où la VaR est dépassée, comparer la perte **moyenne réalisée** à l'ES **moyenne prévue** ces jours-là.

| Méthode | ES prévue les jours de dépassement (M€) | Perte moyenne réalisée (M€) | Écart |
|---|---|---|---|
| Historique | 2,22 | 2,49 | 11 % |
| Normale | 1,69 | 2,24 | 25 % |
| EWMA | 1,48 | 1,88 | 21 % |
| GARCH-Student | 2,11 | 2,27 | 7 % |

Toutes les méthodes **sous-estiment** la perte moyenne des jours difficiles, mais pas de la même façon : la normale et l'EWMA sont loin de la réalité (par construction, une queue normale ne voit pas les pertes extrêmes), le GARCH-Student s'en approche de 7 %. Ce contrôle est approximatif (le nombre de dépassements diffère d'une méthode à l'autre, et un petit nombre de très grosses pertes domine la moyenne), mais il illustre l'idée essentielle : **on peut valider la fréquence tout en ignorant l'ampleur**.

<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.12.

### 3.4.8 La validation d'un modèle

Le backtest n'est qu'une pièce de la **validation**, c'est-à-dire de l'évaluation indépendante d'un modèle avant et pendant son usage. Les institutions la confient à une équipe **distincte** de celle qui l'a construit, pour la même raison qu'on ne corrige pas sa propre copie. Les cinq questions classiques structurent l'examen.

| Question | Ce que l'on vérifie | Exemple dans ce chapitre |
|---|---|---|
| **Le concept est-il solide ?** | Les hypothèses sont-elles défendables, la théorie adaptée à l'usage ? | La normalité est-elle raisonnable pour un portefeuille dont le kurtosis vaut 20,3 ? |
| **Les données sont-elles fiables ?** | Qualité, représentativité, période d'estimation | Une fenêtre calme sous-estime la VaR ; un seul épisode de stress dans l'échantillon |
| **L'implémentation est-elle correcte ?** | Le code fait-il ce que la documentation annonce ? On réexécute indépendamment. | Convention de signe, définition du quantile (rang $\lceil\alpha n\rceil$), unité (M€) |
| **Les résultats tiennent-ils ?** | Backtest, comparaison à un modèle concurrent (*challenger*), analyse de sensibilité | Le tableau de 3.4.4, la puissance de 3.4.5 |
| **L'usage est-il encadré ?** | Domaine de validité, limites, plan de surveillance, revue périodique | Les chiffres au-delà de 99 % sont des extrapolations (3.1.9, 3.3.3) |

Une validation conclut par un **niveau de confiance** et des **limitations** ou des **conditions d'usage** (un coefficient de prudence, une revue plus fréquente, l'interdiction de l'utiliser pour tel produit), jamais par un simple « validé » ou « rejeté ».

### 3.4.9 Le risque de modèle

Tout modèle simplifie, donc se trompe. Le **risque de modèle** est le risque de pertes ou de mauvaises décisions dues à l'utilisation d'un modèle erroné ou mal utilisé. Ce chapitre en a offert quatre visages. **La spécification** : avec les mêmes données, les quatre méthodes donnent des VaR à 99 % moyennes qui diffèrent de 30 % entre la plus basse et la plus haute. **L'estimation** : un chiffre de queue vient avec un intervalle de confiance large (3.1.9), et un paramètre comme $\xi$ peut faire basculer la conclusion (3.3.3). **L'implémentation** : un signe inversé, une unité confondue, une fenêtre mal alignée donnent un chiffre faux mais plausible. **L'usage** : un modèle de défaut estimé sur des périodes calmes utilisé pour un scénario sévère (3.2.4).

On ne supprime pas le risque de modèle, on le **gère** : par un **inventaire** de tous les modèles avec leur propriétaire, leur finalité et leur niveau d'importance ; par une validation plus approfondie pour les modèles à fort enjeu ; par des modèles **concurrents** (si deux modèles raisonnables divergent, l'écart est une mesure du risque de modèle) ; par des **marges de prudence** explicites ; et par une documentation qui permet à un tiers de refaire le calcul. La première défense contre le risque de modèle reste la lucidité : **un chiffre de risque est toujours conditionnel à un modèle**.

> ✅ **À retenir.**
> - Le backtest de VaR vérifie deux propriétés des dépassements : leur **fréquence** (Kupiec) et leur **indépendance** (Christoffersen).
> - Sur nos données, seul le GARCH-Student passe les deux tests ; même lui échoue en stress (dépasse trop souvent dans les basculements).
> - La **puissance** des tests est faible : un an de données ne distingue pas 1 % de 2 % ; le feu tricolore classe, il ne prouve pas.
> - Le backtest de l'ES est plus délicat que celui de la VaR ; un contrôle élémentaire montre que toutes les méthodes sous-estiment les pertes extrêmes.
> - La **validation** est une démarche indépendante en cinq questions (concept, données, implémentation, résultats, usage) ; le **risque de modèle** se gère par inventaire, modèles concurrents, marges de prudence et documentation.


## Bilan du chapitre 3

Vous savez maintenant :

- **définir** une perte de portefeuille, une **VaR** (quantile de niveau $\alpha$, avec son horizon et sa convention de signe) et une **expected shortfall** (perte moyenne au-delà de la VaR), les **calculer** par la loi normale ($\mu+\sigma z_\alpha$, démontrée), par l'histoire, par simulation et avec une volatilité qui change (EWMA, GARCH) ;
- **démontrer** que la VaR n'est pas sous-additive (deux prêts à 4 % de probabilité de défaut) alors que l'ES l'est, et **mesurer l'incertitude** d'un chiffre de queue par bootstrap ;
- **mettre à l'échelle** un horizon par la règle de la racine carrée en connaissant ses conditions (pertes indépendantes) ;
- **concevoir** un stress test : sensibilités, scénarios historiques et hypothétiques, scénario macroéconomique relié aux défauts par un modèle logit, choc de taux (duration, convexité, réévaluation complète), stress **inversé**, et **expliquer** pourquoi les corrélations montent en crise ;
- (en option) **chiffrer** un risque opérationnel par fréquence × sévérité, reconnaître l'instabilité d'un quantile à 99,9 %, **allouer** le risque d'un portefeuille (contributions d'Euler), et lire un **coussin de liquidité** ;
- (en option) **backtester** une VaR (Kupiec, Christoffersen, feu tricolore), connaître la faible puissance de ces tests, contrôler grossièrement une ES, et situer le backtest dans la **validation** et le **risque de modèle**.

Le tableau suivant résume **ce que nous avons mesuré** sur les données simulées de ce chapitre, portefeuille de 100 M€ :

| Question | Résultat | Ce qu'il faut en retenir |
|---|---|---|
| VaR à 99 % sur un jour | historique 2,04 M€ ; normale 1,59 M€ ; ES historique 2,94 M€ | la loi normale sous-estime la queue ; l'ES est 1,44 fois la VaR |
| Fréquence de dépassement en stress (méthodes figées) | historique 10,4 %, normale 12,8 % | le jour où l'on a besoin de la VaR, elle est fausse d'un facteur dix |
| Diversification | corrélation actions A–B 0,57 (calme) puis 0,89 (stress) | elle s'érode quand on en a le plus besoin |
| Scénario macro adverse | perte de crédit de 26,8 M€ contre 6,5 M€ en base | un facteur 4,1 pour une récession déjà observée |
| Stress inversé | coussin de 25 M€ épuisé par une croissance de -1,1 % | moins sévère que la pire récession de l'échantillon |
| Opérationnel (➕) | VaR à 99,9 % de 206 à 365 M€ selon la graine | une queue à $\xi$ proche de 1 rend l'extrême instable |
| Backtest (➕) | seul le GARCH-Student passe Kupiec (36 dépassements pour 30 attendus) | encore 3,8 % de dépassements en stress |

Le fil conducteur du chapitre tient en une phrase : **un nombre de risque est une réponse conditionnelle**, à un niveau, à un horizon, à une méthode, à une période d'estimation, et il vient avec une incertitude qu'il faut lui rattacher. La VaR décrit les jours ordinaires, le stress test les jours qui ne le sont pas, le backtest vérifie que le modèle tient, la validation demande si l'on peut s'y fier ; **aucune de ces quatre démarches ne suffit seule**.

> 🧭 **En pratique : liste de questions devant tout chiffre de risque.**
> 1. À quel niveau, sur quel horizon, avec quelle convention de signe ?
> 2. Calculé comment (loi, fenêtre, volatilité) et sur quelle période : calme ou crise incluse ?
> 3. Avec quelle incertitude (intervalle, plage entre deux méthodes) ?
> 4. Qu'en dit un scénario de stress, y compris inversé ?
> 5. Le backtest a-t-il assez de puissance pour dire que c'est bon ?
> 6. Qui a validé le modèle, avec quelles limites d'usage ?

> ⚠️ **Rappel d'honnêteté.** Les données de ce chapitre sont **simulées** : le simulateur connaît le régime de marché, la relation macro-défaut et les lois des pertes, ce qui nous a permis de juger les méthodes ; en réalité on ne dispose jamais de cette vérité. Le modèle macro de 3.2 est stable par construction, les seuils réglementaires cités (zones du feu tricolore, niveau de l'ES) sont à vérifier dans les textes en vigueur, et rien ici n'est un conseil financier ou réglementaire.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : applications 3.1 à 3.8 (VaR et ES sur le portefeuille, EWMA et GARCH filtré, simulation et loi de Student, incertitude par bootstrap, stress macro, choc de taux, perte opérationnelle agrégée, backtest complet) et exercices 3.1 à 3.12.

Le chapitre 4 change de point de vue : ces mesures de risque ne sont plus seulement des outils de gestion, elles sont **imposées** par des cadres réglementaires (Bâle pour les banques, Solvabilité pour les assureurs). Nous verrons comment ces textes transforment une PD, une LGD ou une VaR en **exigence de capital**, et ce que valent ces conventions.
