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

Exemple à la main : pour $n=250$ jours, un niveau de 99 % ($p=0{,}01$) et $x=6$ dépassements (alors que 2,5 sont attendus), la statistique vaut {{kup_ex_lr}}, soit une probabilité critique de {{kup_ex_p}} : à 5 %, on ne rejette pas, de peu. Avec 7 dépassements, la statistique monterait à {{kup_ex7_lr}} et l'on rejetterait. La frontière est étroite : un jour de plus ou de moins change le verdict.

```python hide
lr6, p6 = O.kupiec(6, 250, 0.01)
lr7, p7 = O.kupiec(7, 250, 0.01)
O.num("kup_ex_lr", lr6, ".2f")
O.num("kup_ex_p", p6, ".3f")
O.num("kup_ex7_lr", lr7, ".2f")
```
<!--sortie-->

### 3.4.3 Le test de Christoffersen

Le test d'**indépendance** de Christoffersen regarde les enchaînements : après un jour sans dépassement, quelle est la probabilité $\pi_{01}$ d'en avoir un le lendemain ? Après un jour avec dépassement, quelle est la probabilité $\pi_{11}$ d'en avoir un autre ? Sous l'indépendance, $\pi_{01}=\pi_{11}$. On compte les quatre types de transitions $n_{00},n_{01},n_{10},n_{11}$, on estime $\hat\pi_{01}=\dfrac{n_{01}}{n_{00}+n_{01}}$ et $\hat\pi_{11}=\dfrac{n_{11}}{n_{10}+n_{11}}$, et la statistique du rapport de vraisemblance suit un $\chi^2$ à un degré de liberté. Additionner les deux statistiques donne un test **conjoint** de couverture conditionnelle, de loi $\chi^2$ à deux degrés de liberté : $\mathrm{LR}_{\mathrm{CC}}=\mathrm{LR}_{\mathrm{POF}}+\mathrm{LR}_{\mathrm{IND}}$.

### 3.4.4 Le backtest de quatre méthodes

Passons à des données. À chaque jour à partir du 1 001ᵉ, quatre méthodes prévoient la VaR à 99 % du lendemain : la **historique** (fenêtre de 500 jours), la **normale** (moyenne et écart-type de la même fenêtre), l'**EWMA** ($\lambda=0{,}94$) et le **GARCH-Student** (paramètres réestimés tous les 250 jours sur les 1 000 derniers jours). Les 3 000 jours de test donnent, pour chaque méthode, le nombre de dépassements (1 % attendu, soit 30), les probabilités critiques des deux tests, la fréquence de dépassement par régime (invisible à l'analyste mais connue du simulateur) et la **perte d'étalonnage** moyenne (voir plus bas).

| Méthode | Dépassements | Fréquence | Kupiec (p) | Christoffersen (p) | Fréquence en calme | Fréquence en stress | Perte d'étalonnage |
|---|---|---|---|---|---|---|---|
| Historique (500 j) | {{bt_hist_k}} | {{bt_hist_rate}} % | {{bt_hist_kp}} | {{bt_hist_ip}} | {{bt_hist_cc}} % | {{bt_hist_cs}} % | {{bt_hist_ql}} |
| Normale (500 j) | {{bt_norm_k}} | {{bt_norm_rate}} % | {{bt_norm_kp}} | {{bt_norm_ip}} | {{bt_norm_cc}} % | {{bt_norm_cs}} % | {{bt_norm_ql}} |
| EWMA | {{bt_ewma_k}} | {{bt_ewma_rate}} % | {{bt_ewma_kp}} | {{bt_ewma_ip}} | {{bt_ewma_cc}} % | {{bt_ewma_cs}} % | {{bt_ewma_ql}} |
| GARCH-Student | {{bt_garch_k}} | {{bt_garch_rate}} % | {{bt_garch_kp}} | {{bt_garch_ip}} | {{bt_garch_cc}} % | {{bt_garch_cs}} % | {{bt_garch_ql}} |

![Perte quotidienne du portefeuille (points gris), VaR à 99 % de la méthode historique (orange) et du GARCH-Student (bleu), avec les dépassements de chaque méthode marqués (croix) sur les 3 000 jours de test. Les bandes grisées sont les périodes de stress.](figures/ch03-backtest.png)

La lecture est instructive. La méthode **normale** et l'**EWMA** dépassent nettement trop souvent ({{bt_norm_k}} et {{bt_ewma_k}} dépassements pour 30 attendus) : le test de Kupiec les rejette sans hésitation. La méthode **historique** est plus proche mais encore rejetée ({{bt_hist_k}} dépassements, probabilité critique de Kupiec {{bt_hist_kp}}) et elle dépasse presque {{ratio_hs_hc}} fois plus souvent en stress qu'en calme. Le **GARCH-Student** est la seule des quatre dont la fréquence globale ({{bt_garch_rate}} %) est compatible avec 1 % au sens du test (probabilité critique de {{bt_garch_kp}}), et c'est aussi celle dont la perte d'étalonnage est la plus faible. Mais regardons la colonne du stress : même le meilleur modèle dépasse **{{bt_garch_cs}} %** du temps en régime de stress (au lieu de 1 %). Les dépassements du GARCH se concentrent dans les basculements : le modèle suit la volatilité, il ne **prévoit** pas qu'elle va changer.

Quant à l'indépendance, aucune méthode n'est rejetée au seuil de 1 % ; la méthode historique l'est à 5 % (probabilité critique de {{bt_hist_ip}}) : ses dépassements arrivent en grappes, comme on pouvait s'y attendre d'une fenêtre qui oublie lentement la volatilité récente.

```python hide
res = O.var_glissantes(L)
te_bt = L[1000:]
rt_bt = rg[1000:]
n_bt = len(te_bt)
tags = {"historique": "hist", "normale": "norm", "EWMA": "ewma", "GARCH-Student": "garch"}
pf = lambda p: "< 0,001" if p < 0.001 else f"{p:.3f}"
for nom, (v, es) in res.items():
    tg = tags[nom]
    e = (te_bt > v).astype(int)
    k = int(e.sum())
    O.num(f"bt_{tg}_k", k, "d")
    O.num(f"bt_{tg}_rate", 100 * k / n_bt, ".2f")
    O.num(f"bt_{tg}_kp", pf(O.kupiec(k, n_bt, 0.01)[1]), "s")
    O.num(f"bt_{tg}_ip", pf(O.christoffersen_ind(e)[1]), "s")
    O.num(f"bt_{tg}_cc", 100 * e[rt_bt == "calme"].mean(), ".1f")
    O.num(f"bt_{tg}_cs", 100 * e[rt_bt == "stress"].mean(), ".1f")
    O.num(f"bt_{tg}_ql", 100 * O.perte_quantile(te_bt, v), ".2f")
    O.num(f"bt_{tg}_espred", es[e == 1].mean(), ".2f")
    O.num(f"bt_{tg}_esreal", te_bt[e == 1].mean(), ".2f")
    O.num(f"bt_{tg}_varmoy", v.mean(), ".2f")
eh = (te_bt > res["historique"][0])
O.num("ratio_hs_hc", eh[rt_bt == "stress"].mean() / eh[rt_bt == "calme"].mean(), ".0f")
vmoy = np.array([res[k][0].mean() for k in res])
O.num("spread_var", 100 * (vmoy.max() - vmoy.min()) / vmoy.mean(), ".0f")
fig, ax = plt.subplots(figsize=(9, 3.8))
dates = r.index[1000:]
ax.plot(dates, te_bt, ".", color=MUET, ms=1.6, alpha=0.7)
ax.plot(dates, res["historique"][0], color=ORANGE, lw=1.1, label="VaR historique")
ax.plot(dates, res["GARCH-Student"][0], color=BLEU, lw=1.1, label="VaR GARCH-Student")
for (nom, couleur, marque) in (("historique", ORANGE, "x"), ("GARCH-Student", BLEU, "+")):
    v = res[nom][0]
    ex = te_bt > v
    ax.plot(dates[ex], te_bt[ex], marque, color=couleur, ms=5)
st = (rt_bt == "stress").astype(int)
for a, b in zip(np.where(np.diff(np.r_[0, st]) == 1)[0], np.where(np.diff(np.r_[st, 0]) == -1)[0]):
    ax.axvspan(dates[a], dates[b], color=MUET, alpha=0.18, lw=0)
ax.set_ylim(-3, 7)
ax.set_ylabel("perte quotidienne (M€)")
ax.legend(loc="upper left", ncol=2)
style.save(fig, "ch03-backtest.png")
```
<!--sortie-->

> ⚠️ **Piège.** « Le modèle a passé le backtest » ne veut pas dire « le modèle est juste ». Cela veut dire « sur cette période, avec ce niveau, on n'a pas pu prouver qu'il avait tort ». La section suivante montre à quel point un test à 250 jours est myope.

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : application 3.8, exercice 3.11.

### 3.4.5 Un test qui voit mal : la puissance

Un test statistique a un **niveau** (la probabilité de rejeter à tort un bon modèle) et une **puissance** (la probabilité de rejeter un mauvais modèle). Calculons-la exactement pour le test de Kupiec, en sommant la loi binomiale sur les nombres de dépassements qui conduisent au rejet. Supposons un modèle dont la vraie fréquence de dépassement serait de 2 % au lieu de 1 %, c'est-à-dire une VaR qui **sous-estime d'un facteur deux** la probabilité de la queue.

| Taille de l'échantillon | Puissance pour une vraie fréquence de 1,5 % | Puissance pour 2 % |
|---|---|---|
| 250 jours (un an) | {{pw_250_15}} % | {{pw_250_20}} % |
| 1 000 jours | {{pw_1000_15}} % | {{pw_1000_20}} % |
| 3 000 jours | {{pw_3000_15}} % | {{pw_3000_20}} % |

Sur un an, un modèle dont la fréquence réelle de dépassement est le **double** de celle annoncée n'est détecté que {{pw_250_20}} fois sur 100. Même après trois ans de données, une fréquence de 1,5 % n'est repérée qu'environ {{pw_3000_15}} fois sur 100. **Un backtest de 250 jours ne distingue presque rien** : c'est la raison pour laquelle les cadres prudentiels se contentent de seuils larges (le « feu tricolore » ci-dessous) et pourquoi un modèle ne se valide pas sur le seul backtest.

```python hide
def puissance(n, p_vraie, p0=0.01):
    k = np.arange(n + 1)
    rejet = np.array([O.kupiec(int(x), n, p0)[0] for x in k]) > 3.841
    return stats.binom.pmf(k, n, p_vraie)[rejet].sum()

for n_, tg in ((250, "250"), (1000, "1000"), (3000, "3000")):
    O.num(f"pw_{tg}_15", 100 * puissance(n_, 0.015), ".0f")
    O.num(f"pw_{tg}_20", 100 * puissance(n_, 0.02), ".0f")
```
<!--sortie-->

### 3.4.6 Le feu tricolore

Plutôt que de tester, on peut **classer**. La zone dans laquelle tombe le nombre de dépassements sur 250 jours pour une VaR à 99 % se détermine par la loi binomiale $B(250;\,0{,}01)$ : on est en zone **verte** tant que la probabilité cumulée du nombre observé reste inférieure à 95 %, en zone **orange** (ou jaune) jusqu'à 99,99 %, en zone **rouge** au-delà. En calculant ces probabilités on retrouve les seuils usuels, 4 dépassements au plus pour le vert, 5 à 9 pour l'orange, 10 et plus pour le rouge.

| Dépassements sur 250 jours | 0 | 2 | 4 | 5 | 7 | 9 | 10 |
|---|---|---|---|---|---|---|---|
| Probabilité cumulée | {{z_0}} | {{z_2}} | {{z_4}} | {{z_5}} | {{z_7}} | {{z_9}} | {{z_10}} |
| Zone | verte | verte | verte | orange | orange | orange | rouge |

Dans le cadre réglementaire de marché de la fin des années 1990, la zone orange ou rouge entraîne une majoration du facteur multiplicatif appliqué à la VaR pour déterminer le capital (de quelques dixièmes à un point entier, valeurs **à vérifier dans les textes en vigueur**). Sur les 250 derniers jours de notre échantillon, la VaR historique a connu {{tl_hist}} dépassements et la VaR GARCH {{tl_garch}} : toutes deux en zone verte, alors que la VaR historique a été rejetée par le test de Kupiec sur les 3 000 jours. **Sur la fenêtre d'un an, rien ne distingue le bon modèle du mauvais.**

```python hide
zt = O.zones_tricolores()
for k in (0, 2, 4, 5, 7, 9, 10):
    O.num(f"z_{k}", 100 * zt.loc[k, "proba_cumulee"], ".2f")
for tg, nom in (("hist", "historique"), ("garch", "GARCH-Student")):
    O.num(f"tl_{tg}", int((te_bt[-250:] > res[nom][0][-250:]).sum()), "d")
assert list(zt.loc[[4, 5, 9, 10], "zone"]) == ["verte", "orange", "orange", "rouge"]
```
<!--sortie-->

### 3.4.7 Backtester l'expected shortfall

Un backtest de VaR ne regarde que la **fréquence** des dépassements ; il ignore leur **ampleur**. Or l'ES a pour rôle de dire de combien on dépasse. Contrôler une ES est plus difficile que contrôler une VaR : il y a peu de dépassements (30 attendus sur 3 000 jours), et la grandeur à comparer est une moyenne conditionnelle. Plusieurs tests existent (le principe est dû, entre autres, à Acerbi et Székely) ; nous nous contentons ici d'un **contrôle de bon sens** : sur les jours où la VaR est dépassée, comparer la perte **moyenne réalisée** à l'ES **moyenne prévue** ces jours-là.

| Méthode | ES prévue les jours de dépassement (M€) | Perte moyenne réalisée (M€) | Écart |
|---|---|---|---|
| Historique | {{bt_hist_espred}} | {{bt_hist_esreal}} | {{es_gap_hist}} % |
| Normale | {{bt_norm_espred}} | {{bt_norm_esreal}} | {{es_gap_norm}} % |
| EWMA | {{bt_ewma_espred}} | {{bt_ewma_esreal}} | {{es_gap_ewma}} % |
| GARCH-Student | {{bt_garch_espred}} | {{bt_garch_esreal}} | {{es_gap_garch}} % |

Toutes les méthodes **sous-estiment** la perte moyenne des jours difficiles, mais pas de la même façon : la normale et l'EWMA sont loin de la réalité (par construction, une queue normale ne voit pas les pertes extrêmes), le GARCH-Student s'en approche de {{es_gap_garch}} %. Ce contrôle est approximatif (le nombre de dépassements diffère d'une méthode à l'autre, et un petit nombre de très grosses pertes domine la moyenne), mais il illustre l'idée essentielle : **on peut valider la fréquence tout en ignorant l'ampleur**.

```python hide
vals = {tg: (res[nom][1][te_bt > res[nom][0]].mean(), te_bt[te_bt > res[nom][0]].mean()) for nom, tg in tags.items()}
for tg, (pr, rl) in vals.items():
    O.num(f"es_gap_{tg}", 100 * (rl - pr) / rl, ".0f")
```
<!--sortie-->

> 📒 **Pour s'entraîner.** Cahier, chapitre 3 : exercice 3.12.

### 3.4.8 La validation d'un modèle

Le backtest n'est qu'une pièce de la **validation**, c'est-à-dire de l'évaluation indépendante d'un modèle avant et pendant son usage. Les institutions la confient à une équipe **distincte** de celle qui l'a construit, pour la même raison qu'on ne corrige pas sa propre copie. Les cinq questions classiques structurent l'examen.

| Question | Ce que l'on vérifie | Exemple dans ce chapitre |
|---|---|---|
| **Le concept est-il solide ?** | Les hypothèses sont-elles défendables, la théorie adaptée à l'usage ? | La normalité est-elle raisonnable pour un portefeuille dont le kurtosis vaut {{kurt}} ? |
| **Les données sont-elles fiables ?** | Qualité, représentativité, période d'estimation | Une fenêtre calme sous-estime la VaR ; un seul épisode de stress dans l'échantillon |
| **L'implémentation est-elle correcte ?** | Le code fait-il ce que la documentation annonce ? On réexécute indépendamment. | Convention de signe, définition du quantile (rang $\lceil\alpha n\rceil$), unité (M€) |
| **Les résultats tiennent-ils ?** | Backtest, comparaison à un modèle concurrent (*challenger*), analyse de sensibilité | Le tableau de 3.4.4, la puissance de 3.4.5 |
| **L'usage est-il encadré ?** | Domaine de validité, limites, plan de surveillance, revue périodique | Les chiffres au-delà de 99 % sont des extrapolations (3.1.9, 3.3.3) |

Une validation conclut par un **niveau de confiance** et des **limitations** ou des **conditions d'usage** (un coefficient de prudence, une revue plus fréquente, l'interdiction de l'utiliser pour tel produit), jamais par un simple « validé » ou « rejeté ».

### 3.4.9 Le risque de modèle

Tout modèle simplifie, donc se trompe. Le **risque de modèle** est le risque de pertes ou de mauvaises décisions dues à l'utilisation d'un modèle erroné ou mal utilisé. Ce chapitre en a offert quatre visages. **La spécification** : avec les mêmes données, les quatre méthodes donnent des VaR à 99 % moyennes qui diffèrent de {{spread_var}} % entre la plus basse et la plus haute. **L'estimation** : un chiffre de queue vient avec un intervalle de confiance large (3.1.9), et un paramètre comme $\xi$ peut faire basculer la conclusion (3.3.3). **L'implémentation** : un signe inversé, une unité confondue, une fenêtre mal alignée donnent un chiffre faux mais plausible. **L'usage** : un modèle de défaut estimé sur des périodes calmes utilisé pour un scénario sévère (3.2.4).

On ne supprime pas le risque de modèle, on le **gère** : par un **inventaire** de tous les modèles avec leur propriétaire, leur finalité et leur niveau d'importance ; par une validation plus approfondie pour les modèles à fort enjeu ; par des modèles **concurrents** (si deux modèles raisonnables divergent, l'écart est une mesure du risque de modèle) ; par des **marges de prudence** explicites ; et par une documentation qui permet à un tiers de refaire le calcul. La première défense contre le risque de modèle reste la lucidité : **un chiffre de risque est toujours conditionnel à un modèle**.

> ✅ **À retenir.**
> - Le backtest de VaR vérifie deux propriétés des dépassements : leur **fréquence** (Kupiec) et leur **indépendance** (Christoffersen).
> - Sur nos données, seul le GARCH-Student passe les deux tests ; même lui échoue en stress (dépasse trop souvent dans les basculements).
> - La **puissance** des tests est faible : un an de données ne distingue pas 1 % de 2 % ; le feu tricolore classe, il ne prouve pas.
> - Le backtest de l'ES est plus délicat que celui de la VaR ; un contrôle élémentaire montre que toutes les méthodes sous-estiment les pertes extrêmes.
> - La **validation** est une démarche indépendante en cinq questions (concept, données, implémentation, résultats, usage) ; le **risque de modèle** se gère par inventaire, modèles concurrents, marges de prudence et documentation.
