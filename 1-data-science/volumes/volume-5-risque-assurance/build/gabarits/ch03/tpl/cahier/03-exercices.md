# Chapitre 3 : Mesures de risque et stress tests — exercices et applications

> 🧭 **Comment utiliser ce chapitre.** Les **applications** sont de petites études guidées sur les données du chapitre (rendements de marché, macroéconomie et défauts, courbe de taux, incidents opérationnels) : lisez l'énoncé, essayez, puis exécutez les blocs. Les **exercices** sont notés ⭐ (direct), ⭐⭐ (demande un raisonnement) ou ⭐⭐⭐ (étude plus longue) ; chacun renvoie à la section du livre qui l'éclaire, et tous sont **corrigés** en fin de chapitre. Les données sont **simulées** (`build/donnees5.py`) ; les montants sont en M€ et les pertes comptées positivement.

Une seule cellule charge ce dont les applications ont besoin.

```python
import sys
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
from scipy import stats
import outils_ch03 as O

r, regime = O.charger_marche()          # rendements journaliers de cinq actifs, régime vrai (calme / stress)
L = O.pertes_portefeuille(r)            # perte du portefeuille de 100 M€ (35 % A, 15 % B, 30 % obligations, 10 % immo, 10 % matières)
rg = regime.values
print(len(L), "jours ;", round((rg == "stress").mean() * 100, 1), "% de jours de stress")
```
<!--sortie-->

## Applications

### Application 3.1 — La VaR et l'ES du portefeuille, trois façons (sections 3.1.3 à 3.1.7)

**Objectif.** Calculer la VaR et l'ES à 95 %, 99 % et 99,9 % par la méthode historique, la loi normale et une simulation de Student, et comparer.

**Étape 1 — Historique.** On lit le quantile empirique et la moyenne des pertes au-delà.

```python
for a in (0.95, 0.99, 0.999):
    print(a, "VaR", round(O.var_hist(L, a), 2), "ES", round(O.es_hist(L, a), 2))
```
<!--sortie-->

**Étape 2 — Loi normale.** Avec la moyenne et l'écart-type observés, on applique $\mu+\sigma z_\alpha$ et $\mu+\sigma\varphi(z_\alpha)/(1-\alpha)$.

```python
mu, sd = L.mean(), L.std()
for a in (0.95, 0.99, 0.999):
    print(a, "VaR", round(O.var_normale(mu, sd, a), 2), "ES", round(O.es_normale(mu, sd, a), 2))
```
<!--sortie-->

**Étape 3 — Student.** On ajuste une loi de Student à la perte du portefeuille (`stats.t.fit`) et l'on en déduit les mêmes quantités.

```python
nu, loc, echelle = stats.t.fit(L)
print("degrés de liberté ajustés :", round(nu, 1))
for a in (0.95, 0.99, 0.999):
    q = stats.t.ppf(a, nu, loc, echelle)
    print(a, "VaR", round(q, 2))
```
<!--sortie-->

```python hide
nu_a, loc_a, ech_a = stats.t.fit(L)
O.num("a1_nu", nu_a, ".1f")
O.num("a1_t999", stats.t.ppf(0.999, nu_a, loc_a, ech_a), ".2f")
O.num("a1_h999", O.var_hist(L, 0.999), ".2f")
O.num("a1_n999", O.var_normale(L.mean(), L.std(), 0.999), ".2f")
```
<!--sortie-->

**Lecture.** La loi de Student ajustée a {{a1_nu}} degrés de liberté, c'est-à-dire des queues bien plus lourdes que la normale ; à 99,9 %, elle donne {{a1_t999}} M€ contre {{a1_h999}} M€ pour l'historique et {{a1_n999}} M€ pour la normale. **Pour aller plus loin :** quelle méthode vous paraît la plus fiable à 99,9 % avec 4 000 jours ? Relisez la section 3.1.9 avant de répondre.

### Application 3.2 — EWMA et GARCH filtré : la couverture selon le régime (section 3.1.5)

**Objectif.** Reproduire la comparaison du livre et la prolonger à d'autres niveaux de confiance.

**Étape 1 — Découper.** On calibre sur les 2 000 premiers jours, on évalue sur les 2 000 suivants.

```python
apprentissage, test = L[:2000], L[2000:]
rt = rg[2000:]
v_fixe = O.var_hist(apprentissage, 0.99)
sig, nu_g, _ = O.garch_filtre(apprentissage, test)       # paramètres figés, volatilité filtrée jour après jour
v_garch = np.array([O.var_student(0, s, nu_g, 0.99) for s in sig])
print("VaR fixe :", round(v_fixe, 2), "| VaR GARCH min / médiane / max :", np.round(np.quantile(v_garch, [0, .5, 1]), 2))
```
<!--sortie-->

**Étape 2 — Fréquences de dépassement.** On compte les jours où la perte dépasse la VaR, par régime.

```python
for nom, v in (("fixe", v_fixe), ("GARCH", v_garch)):
    e = test > v
    print(nom, "| total", round(100 * e.mean(), 2), "% | calme", round(100 * e[rt == "calme"].mean(), 2), "% | stress", round(100 * e[rt == "stress"].mean(), 2), "%")
```
<!--sortie-->

**Étape 3 — EWMA.** La variance du jour est $\lambda\sigma_{t-1}^2+(1-\lambda)L_{t-1}^2$ avec $\lambda=0{,}94$ ; la fonction `O.var_ewma` renvoie l'écart-type prévu pour chaque lendemain.

```python
sig_ew = O.var_ewma(L)[1999:-1]                          # prévisions pour les jours 2000 à 3999
v_ew = 2.326 * sig_ew
e = test > v_ew
print("EWMA | total", round(100 * e.mean(), 2), "% | stress", round(100 * e[rt == "stress"].mean(), 2), "%")
```
<!--sortie-->

**Pour aller plus loin.** Refaites l'étape 2 avec la VaR à 95 % ($z=1{,}645$) : la couverture est-elle meilleure ou moins bonne qu'à 99 % ? Que dit-on de la queue quand l'écart est plus grand à 99 % qu'à 95 % ?

### Application 3.3 — Simulation de Monte-Carlo : la loi change la queue (section 3.1.4)

**Objectif.** Mesurer à quel point la VaR simulée dépend de la loi supposée, à matrice de covariance donnée.

**Étape 1 — Paramètres.** Les moyennes et la covariance des cinq rendements.

```python
Sigma = np.cov(r[O.ACTIFS].values.T)
mu_v = r[O.ACTIFS].values.mean(axis=0)
rng = np.random.default_rng(1)
N = 200000
Z = rng.multivariate_normal(np.zeros(5), Sigma, N)       # chocs normaux de covariance Sigma
```

**Étape 2 — Simuler pour plusieurs lois.** Pour une Student à $\nu$ degrés de liberté de même covariance, on divise les chocs par $\sqrt{W/\nu}$ avec $W\sim\chi^2_\nu$ et l'on multiplie par $\sqrt{(\nu-2)/\nu}$.

```python
def var_simulee(nu, a=0.99):
    X = mu_v + (Z if nu is None else Z * np.sqrt((nu - 2) / nu) / np.sqrt(rng.chisquare(nu, N) / nu)[:, None])
    return O.var_hist(-(X @ O.POIDS) * O.VALEUR, a)

for nu in (None, 30, 10, 6, 4):
    print("normale" if nu is None else f"Student {nu:>2}", "| VaR 99 % :", round(var_simulee(nu), 2), "| VaR 99,9 % :", round(var_simulee(nu, 0.999), 2))
```
<!--sortie-->

**Lecture.** À covariance identique, plus les degrés de liberté sont faibles, plus la VaR à 99,9 % grimpe, et c'est à ce niveau que la loi compte le plus. À 99 %, l'écart est beaucoup plus modeste. **Pour aller plus loin :** pourquoi la normale et la Student à 30 degrés de liberté donnent-elles presque le même résultat ?

### Application 3.4 — Bootstrap d'un chiffre de queue (section 3.1.9)

**Objectif.** Voir comment l'incertitude sur la VaR dépend de la taille de l'échantillon et du niveau.

**Étape 1 — Une fonction qui rééchantillonne.** On tire avec remise, on recalcule la VaR, on prend l'intervalle à 95 %.

```python
rng = np.random.default_rng(5)

def intervalle(x, a, B=600):
    est = [O.var_hist(rng.choice(x, len(x)), a) for _ in range(B)]
    return np.quantile(est, [0.025, 0.975])
```

**Étape 2 — Faire varier la taille.** On répète sur les 500, 1 000, 2 000 et 4 000 derniers jours.

```python
for n in (500, 1000, 2000, 4000):
    x = L[-n:]
    lo, hi = intervalle(x, 0.99)
    print(f"n = {n:>4} | VaR 99 % = {O.var_hist(x, 0.99):.2f} | intervalle [{lo:.2f} ; {hi:.2f}] | largeur relative {100 * (hi - lo) / O.var_hist(x, 0.99):.0f} %")
```
<!--sortie-->

**Lecture.** L'intervalle se resserre avec la taille de l'échantillon, mais lentement (comme la racine de $n$). **Pour aller plus loin :** refaites l'étape 2 pour la VaR à 99,9 % ; combien de jours faudrait-il pour que la largeur relative soit de 10 % ?

### Application 3.5 — Un stress macroéconomique de crédit (sections 3.2.4 à 3.2.7)

**Objectif.** Estimer le modèle macro-défaut, construire un scénario et chiffrer la perte.

**Étape 1 — Estimer.** Régression du logit du taux de défaut sur la croissance, le chômage et la variation de l'immobilier.

```python
import statsmodels.api as sm
t = pd.read_csv("donnees/taux_defaut_macro.csv")
y = np.log(t["taux_defaut"] / (1 - t["taux_defaut"]))
X = sm.add_constant(t[["croissance_pib", "chomage", "variation_immo"]])
macro = sm.OLS(y, X).fit()
print(macro.params.round(3).to_dict())
print("R2 =", round(macro.rsquared, 3), "| écart-type résiduel du logit :", round(macro.resid.std(), 3))
```
<!--sortie-->

**Étape 2 — Un scénario et sa perte.** On suppose, pendant un an, une croissance de −1 %, un chômage de 9,5 % et une variation de l'immobilier de −3 % par trimestre. La perte est le taux de défaut multiplié par l'encours (300 M€) et la LGD (45 %).

```python
x_scen = np.array([1.0, -1.0, 9.5, -3.0])                # constante, croissance, chômage, immobilier
taux = 1 / (1 + np.exp(-x_scen @ macro.params.values))
print("taux de défaut :", round(100 * taux, 1), "% | perte :", round(taux * 300 * 0.45, 1), "M€")
```
<!--sortie-->

**Étape 3 — Tester la robustesse.** Réestimez le modèle sur les quarts 1 à 40 seulement et comparez la prédiction du même scénario.

```python
tr = t["trimestre"] <= 40
m40 = sm.OLS(y[tr], X[tr]).fit()
taux40 = 1 / (1 + np.exp(-x_scen @ m40.params.values))
print("prédiction du scénario avec les 40 premiers trimestres :", round(100 * taux40, 1), "%")
```
<!--sortie-->

**Lecture.** Les deux estimations du même scénario sont proches, parce que la relation simulée est stable. Imaginez qu'elle ne le soit pas : que feriez-vous pour mesurer cette fragilité en pratique ? (Indice : estimer sur des sous-périodes décalées, et comparer les coefficients.)

### Application 3.6 — Un choc de taux sur un petit portefeuille d'obligations (section 3.2.6)

**Objectif.** Comparer un choc parallèle, un choc de pentification et le scénario historique de 3.2.6 sur trois obligations de 10 M€.

**Étape 1 — Les obligations et la courbe.** Le mois 120 est la courbe « actuelle ».

```python
cb = pd.read_csv("donnees/courbe_taux.csv")
f = O.courbe_a(120, cb)
bonds = [(2, 0.02), (5, 0.03), (10, 0.035)]
P0 = [O.prix_obligation(c, m, f) for m, c in bonds]
print("prix initiaux :", np.round(P0, 2))
```
<!--sortie-->

**Étape 2 — Trois chocs.** Parallèle de +100 pb ; pentification (+0 pb à 1 an, +150 pb à 30 ans, interpolés) ; historique (variation observée entre les mois 60 et 90).

```python
chg_hist = cb[cb["mois"] == 90].iloc[0, 1:].values.astype(float) - cb[cb["mois"] == 60].iloc[0, 1:].values.astype(float)
chocs = {"parallèle +100 pb": lambda tt: 0.01,
         "pentification": lambda tt: np.interp(tt, [1, 30], [0.0, 0.015]),
         "historique 60→90": lambda tt: np.interp(tt, O.MATS, chg_hist)}
for nom, choc in chocs.items():
    pertes = [10 * (1 - O.prix_obligation(c, m, f, choc=choc) / p0) for (m, c), p0 in zip(bonds, P0)]
    print(f"{nom:20s} perte totale : {sum(pertes):.2f} M€ | par obligation :", np.round(pertes, 2))
```
<!--sortie-->

**Lecture.** Quelle obligation concentre la perte dans chaque scénario ? Une pentification coûte-t-elle plus ou moins qu'un choc parallèle ? **Pour aller plus loin :** refaites l'étape 2 avec un aplatissement ($+150$ pb à 1 an, $0$ à 30 ans).

### Application 3.7 — Perte opérationnelle agrégée : avec et sans queue lourde (sections 3.3.1 à 3.3.3)

**Objectif.** Mesurer l'effet du choix de la loi de sévérité sur la VaR à 99 % de la perte annuelle.

**Étape 1 — Les données.**

```python
op = pd.read_csv("donnees/pertes_operationnelles.csv")
net = op["perte_nette"].values
lam = len(op) / 10
print("incidents par an :", round(lam, 1), "| perte nette moyenne :", round(net.mean()), "€")
```
<!--sortie-->

**Étape 2 — Sévérité log-normale seule.** On ajuste $\ln X$ par une loi normale sur toutes les pertes et l'on simule 20 000 années.

```python
mu_l, sg_l = np.log(net).mean(), np.log(net).std()
sev_ln = lambda rng, k: np.exp(rng.normal(mu_l, sg_l, k))
tot_ln = O.perte_agregee_mc(lam, sev_ln, n_sim=20000, seed=1)
print("log-normale seule | moyenne", round(tot_ln.mean() / 1e6, 2), "M€ | VaR 99 %", round(np.quantile(tot_ln, 0.99) / 1e6, 2), "M€")
```
<!--sortie-->

**Étape 3 — Corps log-normal et queue GPD.** On utilise l'ajustement du livre (seuil de 100 000 €).

```python
par = O.ajuster_lda(net)
tot_gpd = O.perte_agregee_mc(lam, lambda rng, k: O.tirer_lda(rng, k, par), n_sim=20000, seed=1)
print("corps + GPD       | moyenne", round(tot_gpd.mean() / 1e6, 2), "M€ | VaR 99 %", round(np.quantile(tot_gpd, 0.99) / 1e6, 2), "M€")
print("pire année observée :", round(op.groupby(op["date_evenement"].str[:4])["perte_nette"].sum().max() / 1e6, 2), "M€")
```
<!--sortie-->

**Lecture.** La log-normale seule donne une VaR bien plus basse : elle ne voit pas la queue. La GPD la relève fortement, mais au prix d'une forte incertitude (section 3.3.3). **Pour aller plus loin :** plafonnez chaque perte à 20 M€ (`plafond=20e6` dans `O.tirer_lda`) et observez l'effet sur la VaR à 99 %.

### Application 3.8 — Un backtest complet (sections 3.4.1 à 3.4.6)

**Objectif.** Dérouler tout le contrôle d'une VaR : dépassements, Kupiec, Christoffersen, feu tricolore.

**Étape 1 — Les prévisions glissantes.** `O.var_glissantes` calcule, à partir du 1 001ᵉ jour, la VaR du lendemain pour quatre méthodes.

```python
res = O.var_glissantes(L)
te = L[1000:]
for nom, (v, es) in res.items():
    print(f"{nom:14s} VaR moyenne : {v.mean():.2f} M€ | dépassements : {int((te > v).sum())} sur {len(te)}")
```
<!--sortie-->

**Étape 2 — Les tests.** Kupiec sur le nombre, Christoffersen sur l'enchaînement.

```python
n = len(te)
for nom, (v, es) in res.items():
    e = (te > v).astype(int)
    print(f"{nom:14s} Kupiec p = {O.kupiec(int(e.sum()), n, 0.01)[1]:.4f} | Christoffersen p = {O.christoffersen_ind(e)[1]:.4f}")
```
<!--sortie-->

**Étape 3 — Le feu tricolore sur la dernière année.** On compte les dépassements sur les 250 derniers jours et on lit la zone.

```python
zones = O.zones_tricolores()
for nom, (v, es) in res.items():
    k = int((te[-250:] > v[-250:]).sum())
    print(f"{nom:14s} {k} dépassements sur 250 jours → zone {zones.loc[k, 'zone']}")
```
<!--sortie-->

**Lecture.** Les tests sur 3 000 jours et le feu tricolore sur 250 jours concluent-ils pareil ? Pourquoi la fenêtre d'un an est-elle moins discriminante (section 3.4.5) ? **Pour aller plus loin :** calculez le backtest d'une VaR à 95 % ($z=1{,}645$, EWMA) ; combien de dépassements attend-on ?

## Exercices

### Exercice 3.1 ⭐ — VaR et ES sur vingt pertes (sections 3.1.2 et 3.1.7)

On observe vingt pertes journalières (en M€) : 0,3 ; −0,5 ; 1,2 ; 0,8 ; −0,2 ; 2,9 ; 0,1 ; 0,6 ; −0,9 ; 1,7 ; 0,4 ; 3,8 ; −0,3 ; 0,9 ; 1,1 ; 0,2 ; −0,6 ; 0,7 ; 5,2 ; 1,5. Calculez à la main la VaR à 90 %, à 95 % et à 99 %, puis l'ES à 90 % et à 95 %.

### Exercice 3.2 ⭐ — VaR normale d'un portefeuille de deux actifs (section 3.1.3)

Un portefeuille de 50 M€ est investi à 60 % dans l'actif 1 (volatilité journalière de 1,2 %) et à 40 % dans l'actif 2 (0,8 %), avec une corrélation de 0,3. En supposant des pertes normales de moyenne nulle, calculez la VaR à 99 % sur un jour, puis la somme des VaR de chaque actif pris seul : quel est le gain de diversification ?

### Exercice 3.3 ⭐⭐ — Vérifier numériquement l'ES normale (section 3.1.7)

Pour une loi normale centrée réduite, calculez $\varphi(z_\alpha)/(1-\alpha)$ pour $\alpha=97{,}5\ \%$ et $99\ \%$, vérifiez-le par simulation (deux millions de tirages) et comparez l'ES à 97,5 % avec la VaR à 99 %.

### Exercice 3.4 ⭐⭐ — Sous-additivité avec trois prêts (section 3.1.8)

Deux prêts indépendants de 1 M€ ont une probabilité de défaut de 3 % chacun, avec une perte de 1 M€ en cas de défaut. Calculez à la main, au niveau de 95 %, la VaR et l'ES de chaque prêt, puis de leur somme. La VaR est-elle sous-additive ? L'ES l'est-elle ?

### Exercice 3.5 ⭐⭐ — La règle de la racine avec de la mémoire (section 3.1.6)

Des pertes journalières suivent $L_t=\varphi L_{t-1}+\varepsilon_t$ avec $\varphi=0{,}2$ et $\varepsilon_t$ normal d'écart-type 1. Calculez l'écart-type de la perte sur dix jours par la formule exacte, comparez-le à $\sqrt{10}$ fois l'écart-type quotidien, et vérifiez par simulation. Que devient la VaR à dix jours par la règle de la racine ?

### Exercice 3.6 ⭐ — Taux de défaut et perte d'un scénario (section 3.2.5)

Le modèle $\ln\dfrac{p}{1-p}=-5{,}03-0{,}401\,\text{croissance}+0{,}245\,\text{chômage}-0{,}063\,\text{immo}$ est estimé sur nos données. Pour une croissance de −1 %, un chômage de 9 % et une variation de l'immobilier de −2 %, calculez le taux de défaut, puis la perte annuelle sur un encours de 200 M€ avec une LGD de 45 %.

### Exercice 3.7 ⭐⭐ — Duration et convexité d'une obligation (section 3.2.6)

Une obligation de 5 ans, de coupon annuel de 4 % et de nominal 100, est actualisée sur une courbe plate à 3 %. Calculez son prix, sa duration modifiée et sa convexité (par dérivation numérique), puis comparez, pour un choc parallèle de +100 pb et de +300 pb, la variation exacte du prix aux approximations par la duration seule et par la duration avec la convexité.

### Exercice 3.8 ⭐⭐⭐ — Stress inversé et sensibilité à la LGD (section 3.2.7)

En reprenant la famille de scénarios de 3.2.7 (de la base $s=0$ au scénario sévère $s=1$), trouvez l'intensité $s^\star$ qui épuise un coussin de 30 M€ sur un encours de 500 M€, pour des LGD de 40 %, 46 % et 55 %. Comment varient la croissance et le chômage du scénario fatal ? Commentez le rôle de la LGD, qui n'est pas observée au moment du stress.

### Exercice 3.9 ⭐⭐ — Contributions au risque (section 3.3.4)

Trois actifs de poids 50 %, 30 % et 20 % ont pour volatilités journalières 1,0 %, 1,5 % et 0,5 %, avec des corrélations de 0,6 (actifs 1–2), 0,1 (1–3) et 0 (2–3). Calculez la volatilité du portefeuille et la contribution de chaque actif (en part du total). Quel actif contribue le plus, et comment cela se compare-t-il à son poids ?

### Exercice 3.10 ⭐⭐ — Perte agrégée d'un modèle fréquence-sévérité (sections 3.3.1 et 3.3.3)

Les incidents d'une ligne métier arrivent selon une loi de Poisson de paramètre 20 par an, avec des pertes log-normales de paramètres $\mu=9$ et $\sigma=1{,}5$ (en €). Calculez l'espérance et l'écart-type de la perte annuelle par les formules exactes, puis simulez 200 000 années pour estimer la VaR à 99,9 %. Comparez avec l'approximation normale $\mathbb E+z_{99{,}9\%}\,\sigma$.

### Exercice 3.11 ⭐ — Kupiec et feu tricolore (sections 3.4.2 et 3.4.6)

Un modèle de VaR à 99 % a produit 10 dépassements en 500 jours. Calculez la statistique de Kupiec et sa probabilité critique. Sur une autre fenêtre de 250 jours, il a produit 7 dépassements : dans quelle zone du feu tricolore se trouve-t-il, et avec quelle probabilité cumulée ?

### Exercice 3.12 ⭐⭐⭐ — Contrôler une expected shortfall (section 3.4.7)

Avec les prévisions glissantes de la section 3.4.4, calculez, pour la méthode historique et pour le GARCH-Student, l'écart moyen entre la perte réalisée et l'ES prévue les jours de dépassement. Donnez un intervalle de confiance par bootstrap et dites si l'ES est compatible avec les pertes réalisées.

## Corrigés

### Corrigé 3.1

Triées : −0,9 ; −0,6 ; −0,5 ; −0,3 ; −0,2 ; 0,1 ; 0,2 ; 0,3 ; 0,4 ; 0,6 ; 0,7 ; 0,8 ; 0,9 ; 1,1 ; 1,2 ; 1,5 ; 1,7 ; 2,9 ; 3,8 ; 5,2. Le rang de la VaR est $\lceil\alpha n\rceil$ avec $n=20$ : rang 18 à 90 %, 19 à 95 %, 20 à 99 %.

```python
x = np.array([0.3, -0.5, 1.2, 0.8, -0.2, 2.9, 0.1, 0.6, -0.9, 1.7, 0.4, 3.8, -0.3, 0.9, 1.1, 0.2, -0.6, 0.7, 5.2, 1.5])
for a in (0.90, 0.95, 0.99):
    print(a, "rang", int(np.ceil(a * 20)), "VaR", O.var_hist(x, a), "ES", round(O.es_hist(x, a), 3))
```
<!--sortie-->

La VaR vaut 2,9 (90 %), 3,8 (95 %) et 5,2 (99 %). L'ES à 90 % est la moyenne des trois plus grandes pertes, $(2{,}9+3{,}8+5{,}2)/3=3{,}967$ ; à 95 %, la moyenne des deux plus grandes, $(3{,}8+5{,}2)/2=4{,}5$. À 99 %, la VaR et l'ES coïncident (5,2) : avec vingt observations, la queue à 1 % ne contient qu'une valeur. Moralité : on ne peut pas parler de quantile à 99 % sans assez de données.

### Corrigé 3.2

Avec $w=(0{,}6;0{,}4)$ et $V=50$ : $\sigma_p^2=0{,}36\times1{,}44\times10^{-4}+0{,}16\times0{,}64\times10^{-4}+2\times0{,}6\times0{,}4\times0{,}3\times(0{,}012\times0{,}008)=7{,}59\times10^{-5}$, donc $\sigma_p=0{,}871\ \%$ et la perte journalière a pour écart-type $0{,}871\ \%\times50=0{,}436$ M€. La VaR à 99 % est $2{,}326\times0{,}436\approx1{,}01$ M€.

```python
w, vol, rho, V = np.array([0.6, 0.4]), np.array([0.012, 0.008]), 0.3, 50.0
S = np.array([[vol[0] ** 2, rho * vol[0] * vol[1]], [rho * vol[0] * vol[1], vol[1] ** 2]])
sp = np.sqrt(w @ S @ w) * V
z = stats.norm.ppf(0.99)
somme = z * (w * vol).sum() * V
print("écart-type", round(sp, 4), "| VaR 99 %", round(z * sp, 3), "| somme des VaR", round(somme, 3), "| gain", round(somme - z * sp, 3))
```
<!--sortie-->

La VaR du portefeuille (1,01 M€) est inférieure à la somme des VaR individuelles (1,21 M€) : le gain de diversification est d'environ 0,2 M€, soit 16 % de la somme. Il disparaîtrait si la corrélation valait 1.

### Corrigé 3.3

```python
for a in (0.975, 0.99):
    z = stats.norm.ppf(a)
    print(a, "z =", round(z, 4), "| phi(z)/(1-a) =", round(stats.norm.pdf(z) / (1 - a), 4))
rng = np.random.default_rng(0)
Z = rng.standard_normal(2_000_000)
for a in (0.975, 0.99):
    q = np.quantile(Z, a)
    print(a, "ES simulée :", round(Z[Z >= q].mean(), 4))
```
<!--sortie-->

La formule et la simulation concordent (2,338 à 97,5 % ; 2,665 à 99 %). La VaR à 99 % de la loi normale réduite est $z=2{,}326$ : l'ES à 97,5 % (2,338) est presque identique. **Interprétation.** Pour des pertes normales, passer de la VaR 99 % à l'ES 97,5 % ne change presque rien ; pour des queues lourdes, l'ES est plus grande, parce qu'elle moyenne les pertes extrêmes que la VaR ignore.

### Corrigé 3.4

À 95 %, pour un prêt : $P(L=0)=0{,}97\ge0{,}95$ donc $\mathrm{VaR}=0$ ; la somme des VaR vaut 0. Pour les deux prêts : $P(L=0)=0{,}97^2=0{,}9409<0{,}95$ donc $\mathrm{VaR}=1$ : la VaR du total (1) **dépasse** la somme (0) : elle n'est **pas** sous-additive. Pour l'ES : un prêt, $\mathrm{ES}=(0{,}03\times1)/0{,}05=0{,}6$, soit 1,2 pour deux ; le total, $P(L=1)=0{,}0582$ et $P(L=2)=0{,}0009$, donne $\mathrm{ES}=[(0{,}9991-0{,}95)\times1+0{,}0009\times2]/0{,}05=1{,}018\le1{,}2$ : l'ES **est** sous-additive ici.

```python
p = 0.03
pr = {0: (1 - p) ** 2, 1: 2 * p * (1 - p), 2: p ** 2}
print("P(L=0), P(L=1), P(L=2) :", {k: round(v, 4) for k, v in pr.items()})
es_somme = 2 * (p * 1) / 0.05
es_total = ((0.9991 - 0.95) * 1 + 0.0009 * 2) / 0.05
print("ES chacun", round(p / 0.05, 3), "| somme des ES", es_somme, "| ES du total", round(es_total, 3))
```
<!--sortie-->

### Corrigé 3.5

Pour un AR(1), $\mathrm{Var}(L_t)=\sigma_\varepsilon^2/(1-\varphi^2)$ et $\mathrm{Var}(S_h)=\mathrm{Var}(L)\left[h+2\sum_{k=1}^{h-1}(h-k)\varphi^k\right]$.

```python
phi, h = 0.2, 10
var_L = 1 / (1 - phi ** 2)
facteur = h + 2 * sum((h - k) * phi ** k for k in range(1, h))
print("écart-type à 10 jours (exact) :", round(np.sqrt(var_L * facteur), 4), "| racine de 10 fois l'écart-type quotidien :", round(np.sqrt(h * var_L), 4))
rng = np.random.default_rng(2)
eps = rng.standard_normal((100000, 60))
x = np.zeros_like(eps)
for t_ in range(1, 60):
    x[:, t_] = phi * x[:, t_ - 1] + eps[:, t_]
S = x[:, 49:59].sum(axis=1)
print("écart-type simulé :", round(S.std(), 4))
```
<!--sortie-->

```python hide
O.num("c5_exact", np.sqrt(var_L * facteur), ".2f")
O.num("c5_racine", np.sqrt(h * var_L), ".2f")
O.num("c5_ecart", 100 * (np.sqrt(var_L * facteur) / np.sqrt(h * var_L) - 1), ".0f")
```
<!--sortie-->

L'écart-type exact à dix jours est {{c5_exact}}, contre {{c5_racine}} par la règle de la racine : la règle **sous-estime** le risque de {{c5_ecart}} % et la VaR à dix jours (normale) est donc, elle aussi, sous-estimée dans la même proportion. L'autocorrélation positive fait que les pertes se cumulent. Avec $\varphi<0$ (retour à la moyenne), la règle surestimerait au contraire.

### Corrigé 3.6

Logit $=-5{,}03+0{,}401+0{,}245\times9+0{,}063\times2=-2{,}298$ ; le taux vaut $1/(1+e^{2{,}298})\approx9{,}1\ \%$ ; la perte annuelle est $0{,}091\times200\times0{,}45\approx8{,}2$ M€.

```python
logit = -5.03 - 0.401 * (-1) + 0.245 * 9 - 0.063 * (-2)
p = 1 / (1 + np.exp(-logit))
print("logit", round(logit, 3), "| taux", round(100 * p, 2), "% | perte", round(p * 200 * 0.45, 2), "M€")
```
<!--sortie-->

### Corrigé 3.7

```python
y0 = 0.03
flat = lambda tt: y0
prix = lambda ch=0.0: O.prix_obligation(0.04, 5, flat, choc=lambda tt: ch)
P, h = prix(), 1e-4
D = -(prix(h) - prix(-h)) / (2 * h * P)
C = (prix(h) + prix(-h) - 2 * P) / (h * h * P)
print("prix", round(P, 3), "| duration modifiée", round(D, 3), "| convexité", round(C, 2))
for ch in (0.01, 0.03):
    print(f"+{int(ch * 1e4)} pb | exact {100 * (prix(ch) / P - 1):.2f} % | duration {100 * (-D * ch):.2f} % | duration + convexité {100 * (-D * ch + 0.5 * C * ch ** 2):.2f} %")
```
<!--sortie-->

La duration seule surestime la baisse ; l'ajout de la convexité réduit nettement l'écart, qui reste petit pour +100 pb et plus visible pour +300 pb (le développement de Taylor est un développement local). Avec un nominal de 100, un coupon de 4 % et un taux de 3 %, le prix est au-dessus du pair, ce qui est cohérent avec un coupon supérieur au rendement.

### Corrigé 3.8

```python
from scipy import optimize
import statsmodels.api as sm
t = pd.read_csv("donnees/taux_defaut_macro.csv")
y = np.log(t["taux_defaut"] / (1 - t["taux_defaut"]))
macro = sm.OLS(y, sm.add_constant(t[["croissance_pib", "chomage", "variation_immo"]])).fit()
base = t.iloc[-4:][["croissance_pib", "chomage", "variation_immo"]].mean().values
sev = np.array([-3.0, 11.0, -6.0])

def perte(s, lgd, ead=500.0):
    pib, cho_fin, immo = base + s * (sev - base)
    cho = np.linspace(base[1], cho_fin, 5)[1:]
    Xs = np.column_stack([np.ones(4), np.full(4, pib), cho, np.full(4, immo)])
    return (1 / (1 + np.exp(-Xs @ macro.params.values))).mean() * ead * lgd

for lgd in (0.40, 0.46, 0.55):
    s = optimize.brentq(lambda s: perte(s, lgd) - 30.0, 0, 1.5)
    pib, cho_fin, immo = base + s * (sev - base)
    print(f"LGD {lgd:.2f} | s* = {s:.2f} | croissance {pib:.2f} % | chômage {cho_fin:.2f} %")
```
<!--sortie-->

Plus la LGD est élevée, moins il faut de défaut pour épuiser le coussin : le scénario fatal se rapproche de la base, c'est-à-dire qu'une récession **plus douce** suffit. La LGD, elle, n'est pas observée au moment d'une crise (les recouvrements s'étalent sur plusieurs années) et **elle augmente en récession** (les garanties perdent de la valeur) : un stress qui fixe la LGD à sa moyenne de période calme sous-estime la perte. C'est pourquoi on teste aussi des LGD « de crise ».

### Corrigé 3.9

```python
w = np.array([0.5, 0.3, 0.2])
vol = np.array([0.010, 0.015, 0.005])
corr = np.array([[1, 0.6, 0.1], [0.6, 1, 0.0], [0.1, 0.0, 1]])
S = corr * np.outer(vol, vol)
sp = np.sqrt(w @ S @ w)
contrib = w * (S @ w) / sp ** 2
print("volatilité du portefeuille :", round(100 * sp, 4), "% | contributions :", np.round(100 * contrib, 1), "| somme :", round(contrib.sum(), 6))
```
<!--sortie-->

L'actif 1 pèse 50 % et fournit environ 52 % du risque ; l'actif 2, qui ne pèse que 30 %, en fournit environ 45 % parce qu'il est le plus volatil et corrélé à l'actif 1 ; l'actif 3 pèse 20 % mais ne contribue que pour 2 % (très faible volatilité, corrélations quasi nulles) : **le poids n'est pas la contribution**. La somme des contributions vaut 1 par construction (théorème d'Euler).

### Corrigé 3.10

Pour une loi de Poisson composée, $\mathbb E[S]=\lambda\,\mathbb E[X]$ et $\mathrm{Var}(S)=\lambda\,\mathbb E[X^2]$, avec $\mathbb E[X]=e^{\mu+\sigma^2/2}$ et $\mathbb E[X^2]=e^{2\mu+2\sigma^2}$.

```python
lam_, mu_, sg_ = 20, 9.0, 1.5
esp = lam_ * np.exp(mu_ + sg_ ** 2 / 2)
ecart = np.sqrt(lam_ * np.exp(2 * mu_ + 2 * sg_ ** 2))
tot = O.perte_agregee_mc(lam_, lambda rng, k: np.exp(rng.normal(mu_, sg_, k)), n_sim=200000, seed=4)
print("espérance exacte", round(esp), "| simulée", round(tot.mean()), "| écart-type exact", round(ecart), "| simulé", round(tot.std()))
print("VaR 99,9 % simulée :", round(np.quantile(tot, 0.999)), "| approximation normale :", round(esp + 3.0902 * ecart))
```
<!--sortie-->

```python hide
O.num("c10_ratio", np.quantile(tot, 0.999) / (esp + 3.0902 * ecart), ".2f")
```
<!--sortie-->

La simulation retrouve les valeurs exactes de l'espérance et de l'écart-type. La VaR à 99,9 % simulée vaut {{c10_ratio}} fois l'approximation normale : la perte annuelle est très asymétrique, et une cloche de Gauss de même moyenne et de même écart-type ne la décrit pas.

### Corrigé 3.11

```python
lr, p = O.kupiec(10, 500, 0.01)
print("Kupiec : LR =", round(lr, 3), "| probabilité critique =", round(p, 4))
zt = O.zones_tricolores()
print("7 dépassements sur 250 jours :", zt.loc[7, "zone"], "| probabilité cumulée", round(zt.loc[7, "proba_cumulee"], 4))
```
<!--sortie-->

Avec 10 dépassements pour 5 attendus, la statistique dépasse 3,84 et le test rejette l'hypothèse d'une fréquence de 1 % au seuil de 5 % (la probabilité critique est inférieure à 0,05). Sur 250 jours, 7 dépassements placent le modèle en **zone orange** (la probabilité cumulée de 7 ou moins sous le bon modèle est d'environ 99,6 %, au-dessus de 95 % mais sous 99,99 %).

### Corrigé 3.12

```python
res = O.var_glissantes(L)
te = L[1000:]
rng = np.random.default_rng(8)
for nom in ("historique", "GARCH-Student"):
    v, es = res[nom]
    exc = te > v
    ecart = te[exc] - es[exc]
    moy = ecart.mean()
    b = [rng.choice(ecart, len(ecart)).mean() for _ in range(2000)]
    lo, hi = np.quantile(b, [0.025, 0.975])
    print(f"{nom:14s} | {exc.sum()} dépassements | écart moyen {moy:.2f} M€ | intervalle à 95 % [{lo:.2f} ; {hi:.2f}]")
```
<!--sortie-->

Si l'ES était parfaite, l'écart moyen entre la perte réalisée et l'ES prévue les jours de dépassement serait voisin de zéro. Un intervalle qui contient zéro ne permet pas de rejeter la prévision, un intervalle strictement positif indique que l'ES **sous-estime** la perte. Avec une trentaine de dépassements, la précision est faible : on ne peut conclure que sur des écarts importants, ce qui rappelle pourquoi le contrôle d'une ES est plus délicat que celui d'une VaR (section 3.4.7).
