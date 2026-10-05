## 5.5 ➕ Pour aller plus loin : les risques concurrents

> 🧭 **Section optionnelle.** Elle prolonge le chapitre quand **plusieurs événements** peuvent mettre fin à la durée et s'excluent mutuellement. Les sections 5.1 à 5.4 se lisent sans elle.

> 💡 **Intuition.** Jusqu'ici, il n'y avait qu'une façon de « sortir » : le client partait, ou on ne l'avait pas encore vu partir. Mais dans la vie d'une boutique, un compte peut aussi être **fermé de force** (impayés, soupçon de fraude, adresse invalide). Dès qu'une sortie de ce type survient, le client **ne peut plus partir volontairement** : les deux événements sont en **compétition**, et le premier qui arrive élimine l'autre. Si l'on oublie cette compétition, on surestime les probabilités de chaque cause.

### 5.5.1 Deux façons de sortir

Reprenons le fil de Dar Jasmin. Un client peut :

- **cause 1 : partir volontairement** (il ne commande plus et se désinscrit) ;
- **cause 2 : voir son compte fermé de force** (un incident de paiement, par exemple).

On observe un seul de ces événements, **le premier**. Notons $T_1$ et $T_2$ les durées « potentielles » jusqu'à chaque cause (la seconde n'est jamais observée si la première survient avant) ; la durée observée est $T=\min(T_1,T_2)$ (ou la durée de censure, comme avant) et la **cause** est celle qui l'emporte.

Les objets du 5.1 se généralisent :

- le **risque propre à la cause $k$** (*cause-specific hazard*) :
$$h_k(t)=\lim_{\Delta t\to0}\frac{P(t\le T<t+\Delta t,\ \text{cause}=k\mid T\ge t)}{\Delta t}\quad\text{: le taux de sortie par la cause }k\text{ parmi ceux encore là} ;$$
- le risque total $h(t)=h_1(t)+h_2(t)$ : les risques **s'additionnent**, et la survie (« rester client, quelle que soit la cause de départ ») est donc
$$S(t)=\exp\!\Big[-\int_0^t\big(h_1(u)+h_2(u)\big)du\Big]=\exp\big[-H_1(t)-H_2(t)\big] ;$$
- la **fonction d'incidence cumulée** (CIF) de la cause $k$ : la **probabilité** d'être sorti *par la cause $k$* avant $t$,
$$\boxed{\ F_k(t)=P(T\le t,\ \text{cause}=k)=\int_0^t h_k(u)\,S(u)\,du\ }$$

> 📐 **Pourquoi cette formule ?** Pour sortir par la cause $k$ **entre** $u$ et $u+du$, il faut deux choses : être encore là en $u$ (probabilité $S(u)$), puis sortir par la cause $k$ à cet instant (probabilité $h_k(u)\,du$). On additionne sur tous les instants. Le point crucial est que **$S(u)$ est la survie *totale*** : elle dépend des *deux* risques. La probabilité d'une cause dépend donc de l'autre. De plus, comme tout client finit dans l'un des trois états (encore là, sorti par 1, sorti par 2),
> $$S(t)+F_1(t)+F_2(t)=1\quad\text{à tout instant.}$$

### 5.5.2 Pourquoi « 1 − Kaplan-Meier » trompe

La tentation est de traiter la cause 2 comme une simple *censure* : « pour estimer le départ volontaire, on compte les fermetures forcées comme des clients perdus de vue ». Et d'estimer la probabilité de partir volontairement par $1-\hat S_{KM}(t)$. C'est **faux** : on estime ainsi la probabilité de départ volontaire *dans un monde imaginaire où aucune fermeture forcée n'existerait*, que l'on n'a jamais observé. Voyons-le sur dix clients.

| Client | 1 | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 |
|---|---|---|---|---|---|---|---|---|---|---|
| Mois | 2 | 3 | 4 | 5 | 6 | 7 | 8 | 9 | 10 | 12 |
| Issue | départ (1) | fermé (2) | départ (1) | censuré | fermé (2) | départ (1) | censuré | départ (1) | fermé (2) | censuré |

**L'estimateur d'Aalen-Johansen** de la CIF de la cause $k$ applique la formule précédente en version « escalier » :
$$\hat F_k(t)=\sum_{j:\,t_j\le t}\hat S(t_{j}^{-})\,\frac{d_{kj}}{n_j}$$
où $n_j$ est l'ensemble à risque en $t_j$, $d_{kj}$ le nombre de sorties par la cause $k$ en $t_j$, et $\hat S(t_j^-)$ la survie **totale** de Kaplan-Meier (toutes causes confondues) juste avant $t_j$. Calculons à la main :

| $t_j$ | $n_j$ | $d_{1j}$ | $d_{2j}$ | $\hat S(t_j^-)$ | ajout à $\hat F_1$ | $\hat F_1$ | ajout à $\hat F_2$ | $\hat F_2$ | $\hat S(t_j)$ |
|---|---|---|---|---|---|---|---|---|---|
| 2 | 10 | 1 | 0 | 1,000 | $1/10=0{,}100$ | 0,100 | 0 | 0 | 0,900 |
| 3 | 9 | 0 | 1 | 0,900 | 0 | 0,100 | $0{,}9/9=0{,}100$ | 0,100 | 0,800 |
| 4 | 8 | 1 | 0 | 0,800 | $0{,}8/8=0{,}100$ | 0,200 | 0 | 0,100 | 0,700 |
| 6 | 6 | 0 | 1 | 0,700 | 0 | 0,200 | $0{,}7/6=0{,}117$ | 0,217 | 0,583 |
| 7 | 5 | 1 | 0 | 0,583 | $0{,}583/5=0{,}117$ | 0,317 | 0 | 0,217 | 0,467 |
| 9 | 3 | 1 | 0 | 0,467 | $0{,}467/3=0{,}156$ | 0,472 | 0 | 0,217 | 0,311 |
| 10 | 2 | 0 | 1 | 0,311 | 0 | 0,472 | $0{,}311/2=0{,}156$ | 0,372 | 0,156 |

(Les censures des mois 5, 8 et 12 réduisent $n_j$ sans produire de ligne.) À la fin, $0{,}156+0{,}472+0{,}372=1$ : la propriété $S+F_1+F_2=1$ est respectée. Comparons avec « 1 − KM » obtenu en traitant les fermetures comme des censures :

```python
import numpy as np
import pandas as pd

def incidence_cumulee(t, cause):
    """Aalen-Johansen. t : durées, cause : 0 = censuré, 1, 2, ... Retourne (instants, survie totale, [CIF des causes])."""
    t, cause = np.asarray(t, float), np.asarray(cause, int)
    tj = np.unique(t[cause > 0])
    ys = np.sort(t)
    n_ = len(t) - np.searchsorted(ys, tj, side="left")                          # ensemble à risque
    causes = sorted(set(cause[cause > 0]))
    dk = [np.array([np.sum((t == u) & (cause == k)) for u in tj]) for k in causes]
    S = np.cumprod(1 - sum(dk) / n_)                                            # survie totale (Kaplan-Meier toutes causes)
    S_avant = np.concatenate([[1.0], S[:-1]])                                   # S(t_j^-)
    return tj, S, [np.cumsum(S_avant * d_ / n_) for d_ in dk]

t10 = np.array([2, 3, 4, 5, 6, 7, 8, 9, 10, 12.])
c10 = np.array([1, 2, 1, 0, 2, 1, 0, 1, 2, 0])
tj10, S10, (F1_10, F2_10) = incidence_cumulee(t10, c10)
print(pd.DataFrame({"t_j": tj10, "S": S10, "F1": F1_10, "F2": F2_10, "S + F1 + F2": S10 + F1_10 + F2_10}).round(3).to_string(index=False))

# « 1 - KM » naïf : on traite la cause 2 comme une censure
tj_n, S_n, (F1_naif,) = incidence_cumulee(t10, np.where(c10 == 1, 1, 0))
print(f"\n1 - KM (cause 2 traitée comme censure) à t = 9 : {1 - S_n[-1]:.3f}   |   incidence cumulée correcte F1(9) = {F1_10[5]:.3f}")
```
<!--sortie-->
```text
 t_j     S    F1    F2  S + F1 + F2
 2.0 0.900 0.100 0.000          1.0
 3.0 0.800 0.100 0.100          1.0
 4.0 0.700 0.200 0.100          1.0
 6.0 0.583 0.200 0.217          1.0
 7.0 0.467 0.317 0.217          1.0
 9.0 0.311 0.472 0.217          1.0
10.0 0.156 0.472 0.372          1.0

1 - KM (cause 2 traitée comme censure) à t = 9 : 0.580   |   incidence cumulée correcte F1(9) = 0.472
```

Le « 1 − KM » donne 0,58 pour la probabilité de départ volontaire à 9 mois, alors que la vraie incidence cumulée est de 0,47. Il est **trop grand** : il fait comme si les trois clients dont le compte a été fermé (aux mois 3, 6, 10) étaient restés exposés au départ volontaire.

> ⚠️ **Les risques concurrents ne s'additionnent pas comme les 1 − KM.** Avec la méthode erronée, la somme des deux « probabilités » de sortie peut dépasser 1, ce qui est absurde. Avec les incidences cumulées, la somme $F_1+F_2$ est toujours $1-S\le1$.

### 5.5.3 Une simulation avec une vérité connue

Pour voir tout cela à l'échelle, simulons 6 000 clients avec deux causes. Nous choisissons les risques de sorte que :

- **cause 1 (départ volontaire)** : durée de loi de Weibull (forme 1,3), allongée par l'offre de bienvenue (offre tirée au hasard) ;
- **cause 2 (fermeture forcée)** : risque **constant** de 0,6 % par mois, multiplié par 2,2 pour les clients arrivés par Instagram, et **sans effet de l'offre** ;
- une censure uniforme entre 12 et 72 mois.

```python
rng = np.random.default_rng(55)
n = 6000
offre = rng.integers(0, 2, n)
insta = (rng.random(n) < 0.45).astype(int)
k1 = 1.3
echelle1 = 40 * np.exp(0.40 * offre)                       # l'offre allonge de 49 % le départ volontaire (exp(0.40))
T1 = echelle1 * rng.weibull(k1, n)                         # durée potentielle de départ volontaire
taux2 = 0.006 * np.exp(0.8 * insta)                        # fermeture forcée : taux constant, x 2.2 pour Instagram
T2 = rng.exponential(1 / taux2)
C = rng.uniform(12, 72, n)
t_obs = np.minimum.reduce([T1, T2, C])
cause = np.where(C <= np.minimum(T1, T2), 0, np.where(T1 <= T2, 1, 2))
rc = pd.DataFrame({"duree": t_obs, "cause": cause, "offre": offre, "instagram": insta})
rc.to_csv("donnees/ch05-risques-concurrents.csv", index=False)          # fichier relu par R plus bas
print("effectifs par issue (0 = censuré) :", rc["cause"].value_counts().sort_index().to_dict())

tj, S, (F1, F2) = incidence_cumulee(rc["duree"], rc["cause"])
def a(t, tab): return tab[np.searchsorted(tj, t, side="right") - 1]
horizons = (12, 24, 36, 48)
tj_1, S_1, (F1_naif,) = incidence_cumulee(rc["duree"], np.where(rc["cause"] == 1, 1, 0))     # cause 2 traitée comme censure
print(pd.DataFrame({"S (encore client)": [a(t, S) for t in horizons],
                    "F1 (départ volontaire)": [a(t, F1) for t in horizons],
                    "F2 (fermeture forcée)": [a(t, F2) for t in horizons],
                    "1 - KM naïf (cause 1)": [F1_naif[np.searchsorted(tj_1, t, side='right') - 1] for t in horizons]},
                   index=[f"{t} mois" for t in horizons]).round(3).to_string())
```
<!--sortie-->
```text
effectifs par issue (0 = censuré) : {0: 2079, 1: 2655, 2: 1266}
         S (encore client)  F1 (départ volontaire)  F2 (fermeture forcée)  1 - KM naïf (cause 1)
12 mois              0.762                   0.143                  0.095                  0.151
24 mois              0.538                   0.299                  0.163                  0.335
36 mois              0.367                   0.422                  0.211                  0.494
48 mois              0.251                   0.514                  0.235                  0.627
```

Comparons à **R** (`cmprsk::cuminc`) et à `lifelines`. Nous avons déposé la table dans un fichier précisément pour que R puisse la relire :

```r
library(cmprsk)
rc <- read.csv("donnees/ch05-risques-concurrents.csv")
ci <- cuminc(rc$duree, rc$cause)
print(round(timepoints(ci, c(12, 24, 36, 48))$est, 4))
```
<!--sortie-->
```text
        12     24     36     48
1 1 0.1428 0.2993 0.4217 0.5141
1 2 0.0948 0.1629 0.2109 0.2350
```

```python
from lifelines import AalenJohansenFitter

aj1 = AalenJohansenFitter(calculate_variance=False, seed=1).fit(rc["duree"], rc["cause"], event_of_interest=1)
print("lifelines, F1 aux horizons :", [round(float(aj1.cumulative_density_.loc[:t].iloc[-1, 0]), 4) for t in horizons])
print("à la main,  F1 aux horizons :", [round(float(a(t, F1)), 4) for t in horizons])
```
<!--sortie-->
```text
lifelines, F1 aux horizons : [0.1428, 0.2993, 0.4217, 0.5141]
à la main,  F1 aux horizons : [0.1428, 0.2993, 0.4217, 0.5141]
```

Les trois méthodes donnent les mêmes incidences. Remarquez la dernière colonne du premier tableau : le « 1 − KM » naïf **surestime** systématiquement la probabilité de départ volontaire (par exemple 0,49 contre 0,42 à 36 mois, et 0,63 contre 0,51 à 48 mois). La simulation nous permet même de comparer à la **vérité** : pour un groupe donné, $F_k(t)=\int_0^th_k(u)S(u)\,du$ s'évalue par une intégrale numérique, en mélangeant les clients d'Instagram (45 %) et des autres canaux.

```python
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

BLEU, ORANGE, AQUA, VIOLET, ROUGE = "#2a78d6", "#eb6834", "#1baf7a", "#4a3aa7", "#e34948"
u = np.linspace(0, 100, 20001)
du = u[1] - u[0]

def vraies_cif(off):
    """CIF vraies des deux causes pour le groupe 'off', en moyennant sur la part d'Instagram (45 %)."""
    echelle = 40 * np.exp(0.40 * off)
    h1 = (k1 / echelle) * (u / echelle) ** (k1 - 1)
    H1 = (u / echelle) ** k1
    F1_v = np.zeros_like(u); F2_v = np.zeros_like(u)
    for ins, poids in ((0, 0.55), (1, 0.45)):
        l2 = 0.006 * np.exp(0.8 * ins)
        S_v = np.exp(-H1 - l2 * u)
        F1_v += poids * np.cumsum(h1 * S_v) * du
        F2_v += poids * np.cumsum(l2 * S_v) * du
    return F1_v, F2_v

fig, axes = plt.subplots(1, 2, figsize=(11, 4.2), sharey=True)
for off, couleur, nom in [(0, VIOLET, "sans offre"), (1, AQUA, "avec offre")]:
    g = rc[rc["offre"] == off]
    tj_g, S_g, (F1_g, F2_g) = incidence_cumulee(g["duree"], g["cause"])
    v1, v2 = vraies_cif(off)
    for ax, F_g, v in ((axes[0], F1_g, v1), (axes[1], F2_g, v2)):
        ax.step(np.concatenate([[0], tj_g]), np.concatenate([[0], F_g]), where="post", color=couleur, lw=2, label=nom + " (estimée)")
        ax.plot(u, v, color=couleur, lw=1.2, ls=":", label=nom + " (vraie)")
axes[0].set_title("Cause 1 : départ volontaire")
axes[1].set_title("Cause 2 : fermeture forcée")
for ax in axes:
    ax.set_xlim(0, 70); ax.set_xlabel("mois depuis l'inscription")
    ax.legend(frameon=False, fontsize=8, loc="upper left")
axes[0].set_ylabel("probabilité cumulée (incidence)")
axes[0].set_ylim(0, 0.8)
plt.tight_layout()
plt.savefig("figures/ch05-risques-concurrents.png", dpi=200, bbox_inches="tight")
print("figure enregistrée")
```
<!--sortie-->
```text
figure enregistrée
```

![Incidences cumulées estimées (traits pleins) et vraies (pointillés) des deux causes de sortie, selon l'offre de bienvenue : à gauche le départ volontaire, à droite la fermeture forcée.](figures/ch05-risques-concurrents.png)

Observons la **cause 2**, à droite. L'offre n'a *aucun effet sur le risque de fermeture* (nous l'avons simulée ainsi). Pourtant, les deux courbes ne sont pas superposées : les clients avec offre ont une incidence de fermeture **plus élevée** (le test de Gray, plus bas, rejette l'égalité des deux courbes avec $p\approx3\times10^{-4}$). Pourquoi ? Parce qu'ils partent moins volontairement, donc **restent plus longtemps exposés** au risque de fermeture. La probabilité d'une cause dépend de l'autre : c'est la compétition.

### 5.5.4 Modéliser : deux questions, deux modèles

On peut régresser sur chaque cause de deux façons, qui répondent à **deux questions différentes**.

**Le modèle de Cox par cause.** On ajuste un modèle de Cox pour la cause $k$ en traitant les sorties par les *autres* causes comme des censures. Les coefficients sont des rapports de **risques propres à la cause** : *« parmi les clients encore là, comment la variable change-t-elle le taux de sortie par la cause $k$ ? »*. C'est la bonne question pour **comprendre le mécanisme** (l'offre diminue-t-elle le départ volontaire ?).

**Le modèle de Fine et Gray.** Il modélise directement le **risque de sous-distribution** : le taux de sortie par la cause $k$ parmi ceux qui *n'ont pas encore connu la cause $k$* (ceux qui ont eu l'autre cause restent dans l'ensemble à risque, avec un poids qui décroît). Le coefficient décrit alors l'effet de la variable **sur la CIF** elle-même. C'est la bonne question pour **prédire des probabilités** (quelle part de nos clients quittera volontairement d'ici trois ans ?).

```python
from statsmodels.duration.hazard_regression import PHReg

covariables = rc[["offre", "instagram"]]
for k in (1, 2):
    m = PHReg(rc["duree"], covariables, status=(rc["cause"] == k).astype(int), ties="efron").fit()
    tab = pd.DataFrame({"HR propre à la cause": np.exp(m.params), "IC95 bas": np.exp(m.params - 1.96 * m.bse),
                        "IC95 haut": np.exp(m.params + 1.96 * m.bse), "p": m.pvalues}, index=["offre", "instagram"])
    print(f"Modèle de Cox par cause : cause {k}")
    print(tab.round(3).to_string(), "\n")
```
<!--sortie-->
```text
Modèle de Cox par cause : cause 1
           HR propre à la cause  IC95 bas  IC95 haut      p
offre                     0.584     0.540      0.631  0.000
instagram                 0.974     0.901      1.053  0.504 

Modèle de Cox par cause : cause 2
           HR propre à la cause  IC95 bas  IC95 haut      p
offre                     1.033     0.925      1.154  0.565
instagram                 2.316     2.066      2.595  0.000 
```

```r
cov <- cbind(offre = rc$offre, instagram = rc$instagram)
for (k in 1:2) {
  f <- crr(rc$duree, rc$cause, cov, failcode = k, cencode = 0)
  cat("Fine-Gray, cause", k, "\n")
  print(round(summary(f)$conf.int[, c(1, 3, 4)], 3))      # exp(coef) et son IC95
  cat("\n")
}
print(cuminc(rc$duree, rc$cause, group = rc$offre)$Tests)
```
<!--sortie-->
```text
Fine-Gray, cause 1 
          exp(coef)  2.5% 97.5%
offre         0.604 0.560 0.652
instagram     0.792 0.733 0.855

Fine-Gray, cause 2 
          exp(coef)  2.5% 97.5%
offre         1.219 1.091 1.361
instagram     2.280 2.036 2.554

      stat           pv df
1 170.5141 0.0000000000  1
2  12.9234 0.0003244992  1
```

Lisons ces deux familles de résultats ensemble.

- **Cause 1 (départ volontaire).** L'offre réduit le risque propre à la cause 1 : $\widehat{\mathrm{HR}}\approx0{,}58$ (IC95 : 0,54 à 0,63), ce qui retrouve l'effet programmé ($e^{-0{,}40\times1{,}3}\approx0{,}59$ ; voir la conversion AFT ↔ risques proportionnels au 5.4.2). Le modèle de Fine et Gray donne un rapport de sous-distribution du même ordre (environ 0,60) : la réduction du risque se traduit en réduction de l'incidence.
- **Cause 2 (fermeture forcée).** Les clients d'**Instagram** ont un risque propre multiplié par **2,3** environ (IC95 : 2,07 à 2,60 ; la valeur programmée est $e^{0{,}8}\approx2{,}2$). Et l'**offre** n'a **aucun effet sur le risque** de fermeture : HR $=1{,}03$ (IC95 : 0,93 à 1,15). Mais, dans le modèle de Fine et Gray, l'offre **augmente significativement l'incidence** de la cause 2 : rapport de sous-distribution d'environ **1,22** (IC95 : 1,09 à 1,36). C'est exactement l'effet de compétition que montrait la figure : l'offre ne change pas le risque de fermeture, mais, en retenant plus longtemps les clients, elle les expose plus longtemps à ce risque.
- **Instagram et la cause 1 : le piège.** Dans le modèle par cause, Instagram n'a **aucun effet** sur le départ volontaire : HR $=0{,}97$ (IC95 : 0,90 à 1,05), et c'est la vérité. Mais dans le modèle de Fine et Gray, son rapport de sous-distribution est de **0,79** (IC95 : 0,73 à 0,86), **significativement inférieur à 1** : les clients d'Instagram ont une *incidence cumulée de départ volontaire plus faible*. Ce n'est pas qu'ils soient plus fidèles : ils sont **plus souvent éliminés avant** par la fermeture forcée, qui les empêche de partir volontairement. Le coefficient de Fine et Gray mélange l'effet direct sur la cause et l'effet de la compétition.

> 💡 **Quelle question posez-vous ?**
> - *« Pourquoi les clients partent-ils ? »* (étiologie, mécanisme) : **modèles par cause**. On y lit l'effet de chaque variable sur chaque cause, toutes choses égales.
> - *« Combien de clients seront perdus par chaque cause ? »* (pronostic, planification) : **incidences cumulées** (Aalen-Johansen) et **modèle de Fine et Gray**.
> - En cas de doute, présentez **les deux**, avec leurs interprétations.

### 5.5.5 Pièges

> ⚠️ **L'indépendance des causes ne se teste pas.** On ne peut observer que la première des deux durées $T_1,T_2$ : leur loi **jointe** n'est pas identifiable à partir des données. Le modèle par cause n'a pas besoin de cette hypothèse pour estimer les *risques propres* ; mais toute phrase du type « que se passerait-il si l'on supprimait la fermeture forcée ? » en a besoin, et elle est invérifiable. C'est la raison profonde pour laquelle « $1-\mathrm{KM}$ » n'a pas de sens ici.

> ⚠️ **Ne déclarez pas la cause 2 « censure » pour calculer une probabilité.** C'est valable pour estimer un *risque*, jamais pour estimer une *probabilité cumulée*. Si l'on veut une probabilité, on utilise l'incidence cumulée.

> ⚠️ **Événement composite.** Une autre option est de regrouper les causes (« tout départ, volontaire ou forcé ») et d'appliquer les méthodes des sections 5.1 à 5.4 : c'est licite si la question porte sur « rester client » et non sur le mécanisme. Il est alors plus sûr de **le dire**.

> ✅ **À retenir**
> - Avec plusieurs causes de sortie **concurrentes**, on observe la première seulement. Les risques propres $h_k$ s'additionnent ; $S=e^{-H_1-H_2}$ ; la **CIF** de la cause $k$ est $F_k(t)=\int_0^th_k(u)S(u)\,du$ et $S+F_1+F_2=1$.
> - **1 − Kaplan-Meier** (autres causes traitées en censure) **surestime** la probabilité d'une cause. Utilisez l'estimateur d'**Aalen-Johansen** $\hat F_k(t)=\sum_{t_j\le t}\hat S(t_j^-)\,d_{kj}/n_j$.
> - Le **modèle de Cox par cause** estime l'effet sur le **risque** (mécanisme) ; le modèle de **Fine et Gray** estime l'effet sur l'**incidence cumulée** (pronostic). Les deux peuvent diverger : une variable sans effet direct sur une cause peut modifier son incidence par la compétition.
> - La dépendance entre causes n'est pas identifiable : on évite les phrases « si l'autre cause n'existait pas ».
