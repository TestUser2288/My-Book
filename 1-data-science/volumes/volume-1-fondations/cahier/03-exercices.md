# Chapitre 3 : Statistique — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 3 du livre (statistique descriptive, estimation, intervalles de confiance, tests, puissance, sondages, méthodes non paramétriques). Il contient **sept applications guidées** (avec le code complet des simulations que le livre ne montre pas) et **douze exercices corrigés**. Toutes les applications travaillent sur le jeu de 400 commandes `donnees/commandes.csv` décrit au 3.1.2 du livre. Cherchez d'abord à la main, vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse.

**Préparation commune.** Le chargement ci-dessous sert à toutes les applications.

```python
import numpy as np
import pandas as pd
from scipy import stats

df = pd.read_csv("donnees/commandes.csv")      # canal, montant, livraison, satisfaction
m = df["montant"]
print(df.shape)
```
<!--sortie-->
```text
(400, 4)
```

## Applications

### Application 3.1 — Décrire un jeu de commandes

*Section 3.1 du livre.* La gérante vous remet 400 commandes et demande un portrait fidèle **avant** toute analyse. Vous allez résumer, regarder la forme, comparer les canaux, puis relier délai et satisfaction.

**Étape 1 : position et dispersion du montant.**

```python
resume = pd.DataFrame({"moyenne": m.mean(), "médiane": m.median(), "écart-type": m.std(),
                       "IQR": m.quantile(0.75) - m.quantile(0.25)}, index=["montant"])
print(resume.round(2))
print(m.quantile([0.05, 0.25, 0.5, 0.75, 0.95]).round(1).to_dict())
```
<!--sortie-->
```text
         moyenne  médiane  écart-type    IQR
montant    60.25     51.0       38.02  41.65
{0.05: 19.0, 0.25: 34.2, 0.5: 51.0, 0.75: 75.8, 0.95: 128.6}
```

La moyenne dépasse la médiane : c'est le signe d'une asymétrie à droite, que l'étape suivante quantifie.

**Étape 2 : la forme.** On mesure l'asymétrie, on compte les valeurs atypiques (règle de $1{,}5\times\text{IQR}$) et l'on regarde si le logarithme symétrise.

```python
q1, q3 = m.quantile([0.25, 0.75])
seuil = q3 + 1.5 * (q3 - q1)
print("asymétrie :", round(stats.skew(m), 2), "  asymétrie du logarithme :", round(stats.skew(np.log(m)), 2))
print(f"valeurs atypiques (> {seuil:.1f} €) :", int((m > seuil).sum()))
print(df.loc[m > seuil, "canal"].value_counts().to_dict())
```
<!--sortie-->
```text
asymétrie : 1.75   asymétrie du logarithme : -0.07
valeurs atypiques (> 138.3 €) : 17
{'Boutique': 9, 'Site': 6, 'Réseaux': 2}
```

**Étape 3 : comparer les canaux.**

```python
par_canal = df.groupby("canal").agg(commandes=("montant", "size"), panier_moyen=("montant", "mean"),
                                    panier_median=("montant", "median"), delai_moyen=("livraison", "mean"),
                                    satisfaction=("satisfaction", "mean")).round(2)
print(par_canal)
```
<!--sortie-->
```text
          commandes  panier_moyen  panier_median  delai_moyen  satisfaction
canal                                                                      
Boutique        114         74.81          64.85         0.00          4.49
Réseaux         138         49.01          41.50         4.49          3.72
Site            148         59.50          49.50         4.70          3.79
```

**Étape 4 : relier délai et satisfaction.**

```python
print("Pearson :", round(df["livraison"].corr(df["satisfaction"]), 2),
      " Spearman :", round(stats.spearmanr(df["livraison"], df["satisfaction"]).statistic, 2))
classes = pd.cut(df["livraison"], [-1, 0, 3, 6, 20], labels=["retrait", "1-3 j", "4-6 j", "7 j et +"])
print(df.groupby(classes, observed=True)["satisfaction"].agg(["size", "mean"]).round(2))
```
<!--sortie-->
```text
Pearson : -0.53  Spearman : -0.51
           size  mean
livraison            
retrait     114  4.49
1-3 j        88  4.03
4-6 j       156  3.76
7 j et +     42  3.17
```

**À vous.** Rédigez en cinq lignes, pour la gérante, le portrait des commandes (une phrase sur le centre, une sur la dispersion, une sur la forme, une sur les canaux, une sur le délai). Lequel des résumés n'est pas fiable si l'on garde la boutique dans le calcul du lien délai-satisfaction, et pourquoi ?

### Application 3.2 — Biais, variance et maximum de vraisemblance par simulation

*Section 3.2 du livre.* On vérifie par simulation ce que la théorie affirme, puis on compare deux lois pour les montants.

**Étape 1 : diviser par $n$ ou par $n-1$ ?** Cent mille échantillons de taille 5 d'une loi de variance 1.

```python
rng = np.random.default_rng(3)
x = rng.normal(0, 1, size=(100_000, 5))
v_n, v_n1 = x.var(axis=1, ddof=0), x.var(axis=1, ddof=1)
print("moyenne, division par n   :", round(v_n.mean(), 3), "  (théorie 0,8)")
print("moyenne, division par n-1 :", round(v_n1.mean(), 3))
```
<!--sortie-->
```text
moyenne, division par n   : 0.801   (théorie 0,8)
moyenne, division par n-1 : 1.001
```

**Étape 2 : l'erreur quadratique moyenne.** Le biais est un défaut, mais ce n'est pas le seul critère (3.2.2). Calculons l'EQM des deux estimateurs de la variance (la vraie valeur est 1) :

```python
print("EQM, division par n   :", round(((v_n - 1) ** 2).mean(), 3), "  (théorie 0,36)")
print("EQM, division par n-1 :", round(((v_n1 - 1) ** 2).mean(), 3), "  (théorie 0,50)")
```
<!--sortie-->
```text
EQM, division par n   : 0.358   (théorie 0,36)
EQM, division par n-1 : 0.497   (théorie 0,50)
```

L'estimateur **biaisé** a une EQM plus faible : il est un peu décentré mais bien moins variable. C'est l'illustration de la décomposition $\text{EQM}=\text{Var}+\text{Biais}^2$.

**Étape 3 : le maximum de vraisemblance numérique d'une loi Gamma.**

```python
from scipy import optimize

def neg_loglik(params, x):
    k, theta = params
    return np.inf if k <= 0 or theta <= 0 else -stats.gamma.logpdf(x, a=k, scale=theta).sum()

xbar, s2 = m.mean(), m.var()
depart = [xbar**2 / s2, s2 / xbar]                      # estimation par les moments
res = optimize.minimize(neg_loglik, depart, args=(m.to_numpy(),), method="Nelder-Mead")
print("moments :", np.round(depart, 3), "  log-vraisemblance =", round(-neg_loglik(depart, m.to_numpy()), 1))
print("EMV     :", np.round(res.x, 3), "  log-vraisemblance =", round(-res.fun, 1))
```
<!--sortie-->
```text
moments : [ 2.511 23.991]   log-vraisemblance = -1942.2
EMV     : [ 3.001 20.074]   log-vraisemblance = -1938.9
```

**Étape 4 : Gamma ou log-normale ?** Les deux lois ont deux paramètres : on peut comparer directement leurs log-vraisemblances maximales.

```python
k, _, theta = stats.gamma.fit(m, floc=0)
s, _, scale = stats.lognorm.fit(m, floc=0)
print("Gamma      :", round(stats.gamma.logpdf(m, k, 0, theta).sum(), 1))
print("Log-normale :", round(stats.lognorm.logpdf(m, s, 0, scale).sum(), 1))
```
<!--sortie-->
```text
Gamma      : -1938.9
Log-normale : -1931.0
```

**À vous.** Laquelle des deux lois décrit le mieux les montants ? L'écart est-il grand ? Comment trancheriez-vous si les deux modèles avaient un nombre de paramètres différent (critère d'Akaike) ?

### Application 3.3 — Intervalles de confiance : couverture et bootstrap

*Section 3.3 du livre.*

**Étape 1 : que veut dire « 95 % » ?** On traite les 400 commandes comme la population, on tire 20 000 échantillons de 40 commandes (sans remise) et l'on compte les intervalles de Student qui contiennent la vraie moyenne.

```python
rng = np.random.default_rng(21)
population, mu, n_ech = m.to_numpy(), m.mean(), 40
t_crit = stats.t.ppf(0.975, n_ech - 1)
couvre, largeurs = 0, []
for _ in range(20_000):
    e = rng.choice(population, size=n_ech, replace=False)
    demi = t_crit * e.std(ddof=1) / np.sqrt(n_ech)
    couvre += abs(e.mean() - mu) <= demi
    largeurs.append(2 * demi)
print("couverture :", round(couvre / 20_000, 4), "  largeur moyenne :", round(np.mean(largeurs), 2), "€")
```
<!--sortie-->
```text
couverture : 0.9451   largeur moyenne : 23.88 €
```

**Étape 2 : le bootstrap.** Intervalle « percentile » pour la médiane et pour le 90e centile des montants.

```python
rng = np.random.default_rng(42)
B = 10_000
tirages = rng.choice(population, size=(B, len(population)), replace=True)
for nom, stat in [("médiane", np.median), ("90e centile", lambda a, axis: np.percentile(a, 90, axis=axis))]:
    valeurs = stat(tirages, axis=1)
    print(f"{nom:12s} observée = {stat(population, axis=0):6.1f}   IC95 % = {np.percentile(valeurs, [2.5, 97.5]).round(1)}")
```
<!--sortie-->
```text
médiane      observée =   51.0   IC95 % = [47.3 55.1]
90e centile  observée =  107.4   IC95 % = [ 98.1 119.1]
```

**Étape 3 : Wald contre Wilson, couverture exacte.** Pour une vraie proportion $p$ et un échantillon de taille $n$, on peut calculer la couverture **sans simulation** : on additionne les probabilités binomiales des résultats $k$ dont l'intervalle contient $p$.

```python
def couverture(n, p, methode):
    k = np.arange(n + 1); ph = k / n; z = 1.96
    if methode == "Wald":
        demi = z * np.sqrt(ph * (1 - ph) / n); lo, hi = ph - demi, ph + demi
    else:
        centre = (k + z**2 / 2) / (n + z**2)
        demi = z / (n + z**2) * np.sqrt(k * (n - k) / n + z**2 / 4); lo, hi = centre - demi, centre + demi
    return float((stats.binom.pmf(k, n, p) * ((lo <= p) & (p <= hi))).sum())

for n, p in [(20, 0.05), (20, 0.30), (100, 0.05), (1000, 0.20)]:
    print(f"n = {n:>4}, p = {p:.2f} : Wald {couverture(n, p, 'Wald'):.3f}   Wilson {couverture(n, p, 'Wilson'):.3f}")
```
<!--sortie-->
```text
n =   20, p = 0.05 : Wald 0.639   Wilson 0.925
n =   20, p = 0.30 : Wald 0.947   Wilson 0.975
n =  100, p = 0.05 : Wald 0.877   Wilson 0.966
n = 1000, p = 0.20 : Wald 0.947   Wilson 0.947
```

**À vous.** Pour quels $(n,p)$ la méthode de Wald est-elle très en dessous de 95 % ? Est-ce cohérent avec le conseil du livre (3.3.4) ?

### Application 3.4 — Comparer les trois canaux

*Section 3.4 du livre.* Il y a trois comparaisons possibles entre canaux. Pour chacune : test de Welch, intervalle de confiance de la différence et $d$ de Cohen ; puis une correction de Holm pour tenir compte des trois tests (3.5.5).

```python
from itertools import combinations
groupes = {c: g["montant"].to_numpy() for c, g in df.groupby("canal")}
lignes = []
for a, b in combinations(["Boutique", "Site", "Réseaux"], 2):
    x, y = groupes[a], groupes[b]
    t = stats.ttest_ind(x, y, equal_var=False)
    ic = t.confidence_interval()
    s_commun = np.sqrt(((len(x) - 1) * x.var(ddof=1) + (len(y) - 1) * y.var(ddof=1)) / (len(x) + len(y) - 2))
    lignes.append({"comparaison": f"{a} - {b}", "écart": x.mean() - y.mean(), "IC_bas": ic.low,
                   "IC_haut": ic.high, "p": t.pvalue, "d_Cohen": (x.mean() - y.mean()) / s_commun})
tab = pd.DataFrame(lignes)
```

```python
# Holm : on trie les p, on multiplie la k-ième plus petite par (m - k + 1), puis on rend la suite croissante
ordre = tab["p"].argsort().to_numpy()
brut, ajuste, courant = tab["p"].to_numpy(), np.empty(3), 0.0
for rang, i in enumerate(ordre):
    courant = max(courant, min(1.0, (3 - rang) * brut[i]))
    ajuste[i] = courant
tab["p_Holm"] = ajuste
with pd.option_context("display.float_format", "{:.4g}".format, "display.width", 120):
    print(tab.to_string(index=False))
```
<!--sortie-->
```text
       comparaison  écart  IC_bas  IC_haut         p  d_Cohen    p_Holm
   Boutique - Site  15.31   5.571    25.04  0.002188   0.3889  0.004377
Boutique - Réseaux   25.8   16.66    34.94 8.016e-08   0.7222 2.405e-07
    Site - Réseaux  10.49   2.393    18.59    0.0113   0.2996    0.0113
```

**Un test d'indépendance.** La satisfaction (note $\ge4$) dépend-elle du canal ?

```python
df["satisfait"] = df["satisfaction"] >= 4
tableau = pd.crosstab(df["canal"], df["satisfait"])
chi2, p, ddl, attendus = stats.chi2_contingency(tableau)
v_cramer = np.sqrt(chi2 / (tableau.values.sum() * (min(tableau.shape) - 1)))
print(tableau, f"\nkhi-deux = {chi2:.2f}, ddl = {ddl}, p = {p:.1e}, V de Cramér = {v_cramer:.2f}", sep="")
```
<!--sortie-->
```text
satisfait  False  True 
canal                  
Boutique       5    109
Réseaux       51     87
Site          45    103
khi-deux = 38.40, ddl = 2, p = 4.6e-09, V de Cramér = 0.31
```

**À vous.** Les trois écarts restent-ils significatifs après correction de Holm ? Lequel est le plus important en pratique (regardez $d$ et l'intervalle) ? Pourquoi ne peut-on pas conclure que le canal *cause* la différence de satisfaction (rappel : la boutique n'a pas de délai de livraison) ?

### Application 3.5 — Puissance, arrêt prématuré et tests multiples

*Section 3.5 du livre.*

**Étape 1 : la p-valeur sous $H_0$ est uniforme.**

```python
rng = np.random.default_rng(1)
p0 = np.array([stats.ttest_ind(rng.normal(0, 1, 30), rng.normal(0, 1, 30)).pvalue for _ in range(5_000)])
print("part de p < 0,05 :", round((p0 < 0.05).mean(), 3), "  part de p < 0,50 :", round((p0 < 0.50).mean(), 3))
print("histogramme (10 classes) :", np.histogram(p0, bins=10, range=(0, 1))[0])
```
<!--sortie-->
```text
part de p < 0,05 : 0.05   part de p < 0,50 : 0.489
histogramme (10 classes) : [493 483 487 506 476 493 535 480 538 509]
```

**Étape 2 : la puissance du test A/B (12 % contre 15 %, 1 000 visiteurs par version)**, par la formule puis par simulation.

```python
def puissance(p1, p2, n, alpha=0.05):
    se = np.sqrt(p1 * (1 - p1) / n + p2 * (1 - p2) / n)
    return stats.norm.cdf(abs(p2 - p1) / se - stats.norm.ppf(1 - alpha / 2))

rng = np.random.default_rng(2)
a, b = rng.binomial(1000, 0.12, 10_000), rng.binomial(1000, 0.15, 10_000)
pp = (a + b) / 2000
z = (b - a) / 1000 / np.sqrt(pp * (1 - pp) * 2 / 1000)
print("formule :", round(puissance(0.12, 0.15, 1000), 3), "  simulation :", round((np.abs(z) > 1.96).mean(), 3))
n_requis = next(n for n in range(100, 20_000, 50) if puissance(0.12, 0.15, n) >= 0.80)
print("visiteurs par version pour 80 % de puissance :", n_requis)
```
<!--sortie-->
```text
formule : 0.502   simulation : 0.5
visiteurs par version pour 80 % de puissance : 2050
```

**Étape 3 : l'arrêt prématuré (*peeking*).** Aucune différence réelle (12 % des deux côtés). On regarde les résultats après chaque tranche de 100 visiteurs par version (20 regards au total) et l'on s'arrête dès que $p<0{,}05$.

```python
rng = np.random.default_rng(7)
essais, regards, pas = 4_000, 20, 100
a = rng.binomial(1, 0.12, (essais, regards * pas)).cumsum(axis=1)[:, pas - 1::pas]
b = rng.binomial(1, 0.12, (essais, regards * pas)).cumsum(axis=1)[:, pas - 1::pas]
n = pas * np.arange(1, regards + 1)
pp = (a + b) / (2 * n)
z = (b - a) / n / np.sqrt(np.maximum(pp * (1 - pp) * 2 / n, 1e-12))
print("faux positifs avec un seul regard final :", round((np.abs(z[:, -1]) > 1.96).mean(), 3))
print("faux positifs en s'arrêtant au premier p < 0,05 :", round((np.abs(z) > 1.96).any(axis=1).mean(), 3))
```
<!--sortie-->
```text
faux positifs avec un seul regard final : 0.054
faux positifs en s'arrêtant au premier p < 0,05 : 0.24
```

**Étape 4 : tests multiples.** Cent comparaisons dont dix vrais effets ($d=1$), 40 observations par groupe.

```python
rng = np.random.default_rng(5)
vrai = np.array([True] * 10 + [False] * 90)
p = np.array([stats.ttest_ind(rng.normal(float(v), 1, 40), rng.normal(0, 1, 40)).pvalue for v in vrai])
ordre = np.argsort(p); rangs = np.arange(1, 101)
holm = np.zeros(100, bool); holm[ordre[np.cumprod(p[ordre] < 0.05 / (101 - rangs)).astype(bool)]] = True
ok = p[ordre] <= rangs / 100 * 0.05
bh = np.zeros(100, bool)
if ok.any():
    bh[ordre[: np.max(np.where(ok)[0]) + 1]] = True
for nom, r in [("sans correction", p < 0.05), ("Bonferroni", p < 0.05 / 100), ("Holm", holm), ("Benjamini-Hochberg", bh)]:
    print(f"{nom:20s} découvertes = {r.sum():>2}   vraies = {(r & vrai).sum():>2}   fausses = {(r & ~vrai).sum():>2}")
```
<!--sortie-->
```text
sans correction      découvertes = 12   vraies =  9   fausses =  3
Bonferroni           découvertes =  7   vraies =  7   fausses =  0
Holm                 découvertes =  7   vraies =  7   fausses =  0
Benjamini-Hochberg   découvertes =  9   vraies =  9   fausses =  0
```

**À vous.** Combien de regards faut-il pour que le taux de faux positifs dépasse 20 % ? Que se passe-t-il pour Benjamini-Hochberg si l'on porte à 30 le nombre de vrais effets ?

### Application 3.6 — Stratifier et pondérer

*Section 3.6 du livre.*

**Étape 1 : le gain de la stratification.** Une base de 10 000 clients en trois canaux (4 000, 3 500 et 2 500) ; on estime la dépense moyenne avec 200 clients, au hasard ou par strates proportionnelles.

```python
rng = np.random.default_rng(50)
tailles = {"Réseaux": 4000, "Site": 3500, "Boutique": 2500}
base = {"Réseaux": 3.7, "Site": 3.9, "Boutique": 4.1}
strates = {c: np.exp(rng.normal(base[c], 0.55, size=n)) for c, n in tailles.items()}
pop = np.concatenate(list(strates.values())); N = len(pop)
n_h = {c: round(200 * n / N) for c, n in tailles.items()}          # 80, 70, 50
eas, strat = [], []
for _ in range(5_000):
    eas.append(rng.choice(pop, 200, replace=False).mean())
    strat.append(sum(tailles[c] / N * rng.choice(strates[c], n_h[c], replace=False).mean() for c in tailles))
print("vraie moyenne :", round(pop.mean(), 2))
print("EAS        : erreur-type =", round(np.std(eas), 2), "\nstratifié  : erreur-type =", round(np.std(strat), 2))
```
<!--sortie-->
```text
vraie moyenne : 56.4
EAS        : erreur-type = 2.46 
stratifié  : erreur-type = 2.36
```

**Étape 2 : corriger un échantillon déséquilibré.** Parmi 300 réponses à un questionnaire, 150 viennent de Réseaux, 120 du site et 30 de la boutique, alors que la clientèle est répartie en 40 %, 35 % et 25 %. Les taux de satisfaits par canal sont 63 %, 70 % et 96 %.

```python
taux = pd.Series({"Réseaux": 0.63, "Site": 0.70, "Boutique": 0.96})
reponses = pd.Series({"Réseaux": 150, "Site": 120, "Boutique": 30})
population = pd.Series({"Réseaux": 0.40, "Site": 0.35, "Boutique": 0.25})
poids = population / (reponses / reponses.sum())
print("poids :", poids.round(2).to_dict())
print("moyenne naïve :", round((reponses * taux).sum() / reponses.sum(), 3),
      "  pondérée :", round((reponses * poids * taux).sum() / (reponses * poids).sum(), 3))
```
<!--sortie-->
```text
poids : {'Réseaux': 0.8, 'Site': 0.87, 'Boutique': 2.5}
moyenne naïve : 0.691   pondérée : 0.737
```

**À vous.** Que devient l'erreur-type de l'estimateur stratifié si l'on interroge **autant** de clients dans chaque strate (allocation égale) ? Pourquoi la pondération ne peut-elle pas corriger un biais de non-réponse *à l'intérieur* d'un canal ?

### Application 3.7 — Tests sans hypothèse de loi : rangs et permutations

*Section 3.7 du livre.*

**Étape 1 : Welch ou Mann-Whitney ?** Deux petits groupes dont l'un contient une valeur extrême.

```python
ga = np.array([12, 15, 14, 10, 13, 40]); gb = np.array([9, 8, 11, 10, 7, 12])
print("Welch :", round(stats.ttest_ind(ga, gb, equal_var=False).pvalue, 3),
      "  Mann-Whitney :", round(stats.mannwhitneyu(ga, gb).pvalue, 3))
```
<!--sortie-->
```text
Welch : 0.15   Mann-Whitney : 0.02
```

**Étape 2 : un test de permutation sur la médiane**, statistique pour laquelle il n'y a pas de formule simple (boutique contre Réseaux).

```python
rng = np.random.default_rng(12)
b = df.loc[df["canal"] == "Boutique", "montant"].to_numpy()
r = df.loc[df["canal"] == "Réseaux", "montant"].to_numpy()
valeurs, n_b = np.concatenate([b, r]), len(b)
obs = np.median(b) - np.median(r)
diffs = np.empty(20_000)
for k in range(20_000):
    melange = rng.permutation(valeurs)
    diffs[k] = np.median(melange[:n_b]) - np.median(melange[n_b:])
print("différence de médianes observée :", round(obs, 2), "€")
print("p-valeur de permutation :", (np.sum(np.abs(diffs) >= abs(obs)) + 1) / (len(diffs) + 1))
```
<!--sortie-->
```text
différence de médianes observée : 23.35 €
p-valeur de permutation : 4.999750012499375e-05
```

**Étape 3 : la normalité, canal par canal.**

```python
for c, g in df.groupby("canal"):
    print(f"{c:9s} Shapiro (montant) p = {stats.shapiro(g['montant']).pvalue:.1e}   Shapiro (log) p = {stats.shapiro(np.log(g['montant'])).pvalue:.3f}")
```
<!--sortie-->
```text
Boutique  Shapiro (montant) p = 4.0e-07   Shapiro (log) p = 0.301
Réseaux   Shapiro (montant) p = 5.9e-09   Shapiro (log) p = 0.710
Site      Shapiro (montant) p = 2.0e-13   Shapiro (log) p = 0.243
```

**À vous.** La conclusion du test de permutation sur la médiane diffère-t-elle de celle du test de Welch sur la moyenne ? Pourquoi la p-valeur ne peut-elle pas valoir exactement zéro ?

## Exercices

### Exercice 3.1 ⭐ — Résumer huit commandes (section 3.1 du livre)

Huit commandes en € : $12,\,15,\,15,\,18,\,20,\,22,\,25,\,60$. Calculez la moyenne, la médiane, le mode, l'écart-type (avec $n-1$) et l'écart interquartile. Quelle mesure de position est la plus représentative, et pourquoi ?

### Exercice 3.2 ⭐ — La variance sans biais (section 3.2 du livre)

Un échantillon de 5 délais de livraison : $4,\,8,\,6,\,5,\,7$ jours. Calculez la variance en divisant par $n$ puis par $n-1$. Laquelle utiliser pour estimer la variance de **tous** les délais ?

### Exercice 3.3 ⭐⭐ — Maximum de vraisemblance d'un taux d'arrivée (section 3.2 du livre)

Le nombre de commandes par heure a été relevé 8 fois : $2,\,3,\,1,\,4,\,0,\,3,\,2,\,5$. On modélise par une loi de Poisson$(\lambda)$. (a) Écrivez la log-vraisemblance et trouvez $\hat\lambda$ en dérivant. (b) Avec cette estimation, quelle est la probabilité de ne recevoir aucune commande pendant une heure ?

### Exercice 3.4 ⭐ — Intervalle de confiance d'une moyenne (section 3.3 du livre)

Sur $n=36$ commandes : $\bar x=52$ €, $s=12$ €. Donnez un intervalle de confiance à 95 % de la moyenne, puis à 99 %. Quelle est la signification du « 95 % » ?

### Exercice 3.5 ⭐⭐ — Intervalle de confiance d'une proportion (section 3.3 du livre)

Un questionnaire envoyé à 60 clients donne 18 « très satisfaits ». Calculez l'IC à 95 % de la vraie proportion par la méthode de Wald et par celle de Wilson. Pourquoi sont-ils différents ?

### Exercice 3.6 ⭐⭐ — Le transporteur tient-il sa promesse ? (section 3.4 du livre)

Le transporteur promet un délai moyen de 3 jours. Sur 25 colis, on mesure en moyenne 3,6 jours avec un écart-type de 1,5 jour. (a) Testez $H_0:\mu=3$ contre $H_1:\mu\neq3$ à 5 %. (b) Que change un test unilatéral $H_1:\mu>3$ ? (c) Peut-on dire que le transporteur respecte sa promesse ?

### Exercice 3.7 ⭐⭐ — Un test A/B (section 3.4 et 3.5 du livre)

Version A : 45 achats sur 500 visiteurs. Version B : 66 achats sur 500 visiteurs. (a) B est-elle meilleure, à 5 % ? (b) Donnez un IC de la différence. (c) Quelle était la puissance de ce test si le vrai écart est celui observé ?

### Exercice 3.8 ⭐⭐ — Un code promo a-t-il un effet ? (section 3.4 du livre)

Parmi 100 clients ayant reçu un code promo, 30 ont acheté ; parmi 100 clients sans code, 45 ont acheté. Le code a-t-il un effet ? Construisez le tableau, calculez les effectifs attendus et le test du khi-deux. Comparez avec le test de deux proportions.

### Exercice 3.9 ⭐⭐⭐ — Dimensionner une expérience (section 3.5 du livre)

Le taux de conversion actuel est de 20 %. La gérante veut détecter une hausse à 24 % avec une puissance de 80 % et $\alpha=5\,\%$. (a) Combien de visiteurs par version ? (b) Et pour détecter 22 % ? (c) Expliquez le rapport entre les deux résultats.

### Exercice 3.10 ⭐⭐⭐ — Tests multiples (section 3.5 du livre)

Un analyste teste 8 hypothèses et obtient les p-valeurs $0{,}001;\ 0{,}008;\ 0{,}012;\ 0{,}030;\ 0{,}040;\ 0{,}200;\ 0{,}500;\ 0{,}700$. Lesquelles sont rejetées à 5 % (a) sans correction, (b) avec Bonferroni, (c) avec Holm, (d) avec Benjamini-Hochberg ?

### Exercice 3.11 ⭐ — Marge d'erreur d'un sondage (section 3.6 du livre)

Une enquête de satisfaction recueille 625 réponses tirées au hasard dans la clientèle. (a) Quelle est la marge d'erreur maximale à 95 % sur une proportion ? (b) Combien de réponses faut-il pour une marge de ±2 points ? (c) Que ne dit pas cette marge ?

### Exercice 3.12 ⭐⭐ — Mann-Whitney à la main (section 3.7 du livre)

Trois commandes du site : $12,\,15,\,14$ € ; trois commandes de la boutique : $9,\,8,\,11$ €. (a) Rangez les six valeurs et calculez la somme des rangs du premier groupe. (b) Quelle est la probabilité qu'une commande tirée au hasard dans le premier groupe dépasse une commande tirée dans le second ? (c) Parmi les $\binom{6}{3}=20$ répartitions possibles des six valeurs en deux groupes de trois, combien donnent un résultat au moins aussi extrême ? Quelle est la plus petite p-valeur bilatérale accessible avec des groupes de 3 ?

## Corrigés

### Corrigé 3.1

Moyenne : $187/8=23{,}375$. Triées : $12,15,15,18,20,22,25,60$ : la médiane est $(18+20)/2=19$. Mode : 15. Écart-type ($n-1$) : voir le code (≈ 15,4). Les quartiles (méthode de NumPy) donnent un IQR de 7,75. La **médiane** (19) est la plus représentative : la moyenne (23,4) est tirée vers le haut par la commande de 60 € (valeur extrême), qui est supérieure de plus du double au reste.

```python
import numpy as np
from scipy import stats
x = np.array([12, 15, 15, 18, 20, 22, 25, 60])
print("moyenne :", x.mean(), " médiane :", np.median(x), " mode :", stats.mode(x).mode)
print("écart-type (n-1) :", round(x.std(ddof=1), 2))
print("IQR :", np.percentile(x, 75) - np.percentile(x, 25))
```
<!--sortie-->
```text
moyenne : 23.375  médiane : 19.0  mode : 15
écart-type (n-1) : 15.38
IQR : 7.75
```

### Corrigé 3.2

$\bar x=6$ ; écarts : $-2,2,0,-1,1$ ; carrés : $4,4,0,1,1$ ; somme $=10$. Division par $n$ : $10/5=2$. Division par $n-1$ : $10/4=2{,}5$. Pour estimer la variance de la **population**, on utilise $n-1$ (estimateur sans biais, 3.2.3).

```python
d = np.array([4, 8, 6, 5, 7])
print("var (n)   :", d.var(ddof=0), "   var (n-1) :", d.var(ddof=1))
```
<!--sortie-->
```text
var (n)   : 2.0    var (n-1) : 2.5
```

### Corrigé 3.3

(a) $\ell(\lambda)=\sum_i\bigl(-\lambda+x_i\ln\lambda-\ln x_i!\bigr)=-n\lambda+\ln\lambda\sum x_i-\sum\ln x_i!$. $\ell'(\lambda)=-n+\dfrac{\sum x_i}{\lambda}=0\Rightarrow\hat\lambda=\bar x=\dfrac{20}8=2{,}5$ (c'est un maximum car $\ell''=-\sum x_i/\lambda^2<0$). (b) $P(N=0)=e^{-2{,}5}\approx0{,}082$.

```python
x = np.array([2, 3, 1, 4, 0, 3, 2, 5])
lam = x.mean()
print("lambda chapeau =", lam, "  P(0 commande) =", round(np.exp(-lam), 4))
grille = np.linspace(0.5, 6, 1101)
print("maximum sur grille :", round(grille[np.argmax([stats.poisson.logpmf(x, g).sum() for g in grille])], 2))
```
<!--sortie-->
```text
lambda chapeau = 2.5   P(0 commande) = 0.0821
maximum sur grille : 2.5
```

### Corrigé 3.4

Erreur-type : $12/\sqrt{36}=2$. Valeur critique de Student à 35 ddl : 2,030 (95 %) et 2,724 (99 %). IC 95 % : $52\pm2{,}030\times2=[47{,}9\,;\,56{,}1]$. IC 99 % : $52\pm2{,}724\times2=[46{,}6\,;\,57{,}4]$ (plus large : plus de confiance coûte en précision). « 95 % » : si l'on répétait l'enquête de nombreuses fois, environ 95 % des intervalles ainsi construits contiendraient la vraie moyenne.

```python
n, xbar, s = 36, 52, 12
se = s / np.sqrt(n)
for niveau in (0.95, 0.99):
    t = stats.t.ppf(1 - (1 - niveau) / 2, n - 1)
    print(f"{niveau:.0%} : t = {t:.3f}   IC = [{xbar - t * se:.1f} ; {xbar + t * se:.1f}]")
```
<!--sortie-->
```text
95% : t = 2.030   IC = [47.9 ; 56.1]
99% : t = 2.724   IC = [46.6 ; 57.4]
```

### Corrigé 3.5

$\hat p=18/60=0{,}30$. Wald : erreur-type $\sqrt{0{,}3\times0{,}7/60}=0{,}0592$, IC $0{,}30\pm0{,}116=[0{,}184\,;\,0{,}416]$. Wilson (voir le code) donne environ $[0{,}199\,;\,0{,}425]$ : légèrement décalé vers le centre et plus large à droite. Wilson est plus fiable car il tient compte du fait que l'erreur-type dépend de $p$ lui-même, d'où une meilleure couverture pour $n$ modeste.

```python
k, n = 18, 60
p = k / n
d = 1.96 * np.sqrt(p * (1 - p) / n)
print("Wald   : [", round(p - d, 3), ";", round(p + d, 3), "]")
w = stats.binomtest(k, n).proportion_ci(confidence_level=0.95, method="wilson")
print("Wilson : [", round(w.low, 3), ";", round(w.high, 3), "]")
```
<!--sortie-->
```text
Wald   : [ 0.184 ; 0.416 ]
Wilson : [ 0.199 ; 0.425 ]
```

### Corrigé 3.6

(a) $t=\dfrac{3{,}6-3}{1{,}5/\sqrt{25}}=\dfrac{0{,}6}{0{,}3}=2{,}0$ avec 24 ddl. Valeur critique bilatérale à 5 % : 2,064. Comme $2{,}0<2{,}064$ (et $p\approx0{,}057$), on **ne rejette pas** $H_0$ de justesse. (b) En unilatéral, $p\approx0{,}028<0{,}05$ : on rejette. Mais on ne peut choisir le sens du test **qu'avant** de voir les données et si l'on n'est vraiment intéressé que par un dépassement ; décider après coup serait tricher. (c) Honnêtement : les données sont **à la limite** : le retard moyen estimé est de 0,6 jour, l'IC à 95 % ($3{,}6\pm2{,}064\times0{,}3=[2{,}98\,;\,4{,}22]$) inclut 3 de justesse. On ne peut ni affirmer que la promesse est tenue, ni qu'elle ne l'est pas ; il faut davantage de colis.

```python
n, xbar, s, mu0 = 25, 3.6, 1.5, 3
t = (xbar - mu0) / (s / np.sqrt(n))
print("t =", t, "  p bilatérale =", round(2 * stats.t.sf(t, n - 1), 4), "  p unilatérale =", round(stats.t.sf(t, n - 1), 4))
tc = stats.t.ppf(0.975, n - 1)
print("IC95 % : [", round(xbar - tc * s / np.sqrt(n), 2), ";", round(xbar + tc * s / np.sqrt(n), 2), "]")
```
<!--sortie-->
```text
t = 2.0000000000000004   p bilatérale = 0.0569   p unilatérale = 0.0285
IC95 % : [ 2.98 ; 4.22 ]
```

### Corrigé 3.7

(a) $\hat p_A=0{,}09$, $\hat p_B=0{,}132$, $\hat p=\frac{111}{1000}=0{,}111$. $z=\dfrac{0{,}042}{\sqrt{0{,}111\times0{,}889\times(2/500)}}=\dfrac{0{,}042}{0{,}01987}\approx2{,}11$, $p\approx0{,}035$ : significatif à 5 %. (b) Erreur-type non regroupée $\approx0{,}0194$, donc IC $=0{,}042\pm0{,}039=[0{,}003\,;\,0{,}081]$ : l'écart est positif, mais très imprécis (de 0,3 à 8 points !). (c) La puissance, si le vrai écart est celui observé, est d'environ 56 % : l'expérience était sous-dimensionnée (voir le code).

```python
kA, kB, n = 45, 66, 500
pA, pB = kA / n, kB / n
pp = (kA + kB) / (2 * n)
z = (pB - pA) / np.sqrt(pp * (1 - pp) * 2 / n)
print("z =", round(z, 3), "  p =", round(2 * stats.norm.sf(z), 4))
se = np.sqrt(pA * (1 - pA) / n + pB * (1 - pB) / n)
print("IC95 % de la différence : [", round(pB - pA - 1.96 * se, 4), ";", round(pB - pA + 1.96 * se, 4), "]")
print("puissance :", round(stats.norm.cdf((pB - pA) / se - 1.96), 3))
```
<!--sortie-->
```text
z = 2.114   p = 0.0345
IC95 % de la différence : [ 0.0031 ; 0.0809 ]
puissance : 0.563
```

### Corrigé 3.8

Tableau : code promo : 30 achats, 70 non ; sans code : 45 achats, 55 non. Totaux : colonnes 75 et 125 ; lignes 100 et 100. Effectifs attendus (sous indépendance) : achats $100\times75/200=37{,}5$ dans chaque ligne ; non-achats $62{,}5$. Chaque case s'écarte de son attendu de $7{,}5$, donc $\chi^2=\sum\frac{(O-E)^2}{E}=2\times\dfrac{7{,}5^2}{37{,}5}+2\times\dfrac{7{,}5^2}{62{,}5}=3{,}0+1{,}8=4{,}8$ (sans correction de continuité), 1 ddl, $p\approx0{,}029$ (0,041 avec la correction de Yates, plus prudente). **Attention : le code promo est associé à *moins* d'achats** (30 % contre 45 %) : le test signale une différence, pas son sens. (Et le test à deux proportions donne $z^2=\chi^2$ : même $p$.)

```python
from scipy.stats import chi2_contingency
tab = np.array([[30, 70], [45, 55]])
chi2, p, ddl, att = chi2_contingency(tab, correction=False)
print("attendus :\n", att)
print("khi-deux =", round(chi2, 3), " p =", round(p, 4), " (avec correction de Yates :", round(chi2_contingency(tab)[1], 4), ")")
pp = 75 / 200
z = (0.45 - 0.30) / np.sqrt(pp * (1 - pp) * 2 / 100)
print("z =", round(z, 3), " z^2 =", round(z**2, 3), " p =", round(2 * stats.norm.sf(abs(z)), 4))
```
<!--sortie-->
```text
attendus :
 [[37.5 62.5]
 [37.5 62.5]]
khi-deux = 4.8  p = 0.0285  (avec correction de Yates : 0.0409 )
z = 2.191  z^2 = 4.8  p = 0.0285
```

### Corrigé 3.9

(a) $n=\dfrac{(1{,}96+0{,}8416)^2\,[0{,}2\times0{,}8+0{,}24\times0{,}76]}{0{,}04^2}\approx1\,680$ par version. (b) Pour 22 %, l'effet est deux fois plus petit : $n\approx6\,500$. (c) Diviser l'effet par 2 multiplie $n$ par **environ 4** : $n\propto1/\text{effet}^2$.

```python
za, zb = stats.norm.ppf(0.975), stats.norm.ppf(0.80)
def n_groupe(p1, p2):
    return (za + zb) ** 2 * (p1 * (1 - p1) + p2 * (1 - p2)) / (p2 - p1) ** 2
print("20 -> 24 % :", int(np.ceil(n_groupe(0.20, 0.24))), "  20 -> 22 % :", int(np.ceil(n_groupe(0.20, 0.22))))
print("rapport :", round(n_groupe(0.20, 0.22) / n_groupe(0.20, 0.24), 2))
```
<!--sortie-->
```text
20 -> 24 % : 1680   20 -> 22 % : 6507
rapport : 3.87
```

### Corrigé 3.10

(a) Sans correction : $p<0{,}05$ pour les 5 premières. (b) Bonferroni : seuil $0{,}05/8=0{,}00625$ : seule 0,001 est rejetée. (c) Holm : seuils $0{,}05/8=0{,}00625$, $0{,}05/7=0{,}00714$, $0{,}05/6=0{,}00833$, … : $0{,}001<0{,}00625$ ✓ ; $0{,}008>0{,}00714$ ✗ : on s'arrête. Un seul rejet, comme Bonferroni. (d) BH : seuils $\frac k8\times0{,}05$ : $0{,}00625;\ 0{,}0125;\ 0{,}01875;\ 0{,}025;\ 0{,}03125;\dots$ ; $p_{(1)}=0{,}001\le0{,}00625$ ✓, $p_{(2)}=0{,}008\le0{,}0125$ ✓, $p_{(3)}=0{,}012\le0{,}01875$ ✓, $p_{(4)}=0{,}030>0{,}025$ ✗, $p_{(5)}=0{,}040>0{,}03125$ ✗. Le plus grand $k$ qui convient est 3 : les **trois** premières sont rejetées.

```python
p = np.array([0.001, 0.008, 0.012, 0.030, 0.040, 0.200, 0.500, 0.700])
m = len(p)
print("sans correction :", int((p < 0.05).sum()), "rejets")
print("Bonferroni      :", int((p < 0.05 / m).sum()), "rejets")
rang = np.arange(1, m + 1)
holm = np.cumprod(p < 0.05 / (m - rang + 1))     # on s'arrête au premier échec
print("Holm            :", int(holm.sum()), "rejets")
ok = p <= rang / m * 0.05
print("Benjamini-Hochberg :", int(np.max(np.where(ok)[0]) + 1) if ok.any() else 0, "rejets")
```
<!--sortie-->
```text
sans correction : 5 rejets
Bonferroni      : 1 rejets
Holm            : 1 rejets
Benjamini-Hochberg : 3 rejets
```

### Corrigé 3.11

(a) $1{,}96\sqrt{0{,}25/625}=1{,}96\times0{,}02=0{,}0392$ : environ **±3,9 points**. (b) $n\ge(1{,}96/0{,}02)^2\times0{,}25\approx2\,401$ réponses. (c) Cette marge ne couvre que l'**erreur d'échantillonnage** ; elle ne dit rien du biais de sélection ni de la non-réponse (3.6.1), souvent plus grands.

```python
print("marge pour n = 625 :", round(1.96 * np.sqrt(0.25 / 625) * 100, 2), "points")
print("n pour ±2 points   :", int(np.ceil((1.96 / 0.02) ** 2 * 0.25)))
```
<!--sortie-->
```text
marge pour n = 625 : 3.92 points
n pour ±2 points   : 2401
```

### Corrigé 3.12

(a) Valeurs triées : $8,9,11,12,14,15$ ; rangs $1$ à $6$. Le premier groupe ($12,15,14$) occupe les rangs $4,6,5$ : somme $=15$. (b) Chaque commande du premier groupe dépasse chaque commande du second : $U=9$ sur $3\times3=9$ paires, donc probabilité $=1$. (c) Une seule répartition donne le premier groupe tout en haut, et une autre le met tout en bas : **2** répartitions sur 20 sont aussi extrêmes (dans les deux sens), d'où une p-valeur exacte bilatérale de $2/20=0{,}10$. Avec des groupes de 3, la plus petite p-valeur possible est donc 0,10 : **aucun test ne peut rejeter à 5 %**, même avec une séparation parfaite. Les petits échantillons manquent structurellement de puissance.

```python
A, B = np.array([12, 15, 14]), np.array([9, 8, 11])
print("somme des rangs du groupe A :", stats.rankdata(np.concatenate([A, B]))[:3].sum())
print("p exacte de Mann-Whitney :", stats.mannwhitneyu(A, B, method="exact").pvalue)
```
<!--sortie-->
```text
somme des rangs du groupe A : 15.0
p exacte de Mann-Whitney : 0.1
```
