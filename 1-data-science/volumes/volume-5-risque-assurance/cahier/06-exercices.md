# Chapitre 6 : ➕ Réassurance — exercices et applications

> 🧭 **Orientation.** Ce chapitre du cahier accompagne le chapitre 6 du livre (réassurance et tarification). Les **applications** reprennent, en petites étapes commentées, les études du livre sur les données `sinistres_gros.csv` et `cat_annuel.csv` (simulées : nous connaissons la vérité). Les **exercices** (⭐ direct, ⭐⭐ demande un raisonnement, ⭐⭐⭐ petite étude) sont corrigés à la fin, avec le calcul à la main quand il est faisable. Une seule cellule charge les bibliothèques et les données ; chaque bloc suivant s'appuie dessus.

```python
import sys
import numpy as np, pandas as pd
from scipy import stats, integrate, optimize
sys.path.insert(0, "build")
import outils_ch06 as O          # tranche(), burning_cost(), prix_gpd(), simuler()…
sg, cat = O.charger()
x = sg["montant"].values         # 2 898 sinistres, 2010-2024
c = cat["perte_cat"].values      # 40 années de pertes de catastrophe
```

```python hide
def NUM(cle, valeur):
    print(f"NUM {cle} {valeur}")
```

## Applications

### Application 6.1 — Répartir huit sinistres entre trois traités (sections 6.1.2 et 6.1.3)

**Objectif.** Reproduire le tableau du livre, puis chercher quelle plénitude cède autant que l'excédent de sinistre.

**Étape 1 — Les trois partages.** On reprend huit sinistres (k€) et leurs capitaux assurés.

```python
X = np.array([30, 45, 80, 120, 250, 600, 900, 2000.])        # sinistres
V = np.array([200, 300, 500, 800, 1000, 2500, 3000, 5000.])  # capitaux assurés
t = pd.DataFrame({"sinistre": X, "capital": V})
t["quote_part_30"] = 0.3 * X                                  # 30 % de chaque sinistre
t["plenitude_1000"] = np.maximum(0, 1 - 1000 / V) * X         # cession proportionnelle au dépassement de 1 000
t["xl_500_xs_500"] = O.tranche(X, 500, 500)                   # tranche par risque
print(t.sum().round(1).to_string())
```
<!--sortie-->
```text
sinistre           4025.0
capital           13300.0
quote_part_30      1207.5
plenitude_1000     2560.0
xl_500_xs_500      1000.0
```

**Étape 2 — Une plénitude qui cède autant que l'excédent de sinistre.** On cherche $R$ tel que la plénitude cède 1 000.

```python
cede = lambda R: (np.maximum(0, 1 - R / V) * X).sum()
R_eq = optimize.brentq(lambda R: cede(R) - 1000, 1000, 5000)
print(f"plénitude équivalente : {R_eq:,.0f}  (cède {cede(R_eq):.0f})")
```
<!--sortie-->
```text
plénitude équivalente : 2,714  (cède 1000)
```

**Lecture.** La plénitude qui cède autant que la tranche « 500 xs 500 » est de 2 714 k€, c'est-à-dire que la cédante devrait **garder** près de 2 714 k€ par risque pour ne céder que 1 000 : la tranche, qui n'intervient qu'au-delà de 500 sur chaque sinistre, est une façon **bien plus précise** de couper la queue. À cession égale, les deux traités ne protègent pas des mêmes années : la plénitude cède aussi des parts de petits sinistres de gros risques.

```python hide
Rr = optimize.brentq(lambda R: (np.maximum(0, 1 - R / V) * X).sum() - 1000, 1000, 5000)
NUM("R_eq", Rr)
assert t["quote_part_30"].sum() == 1207.5 and abs(t["plenitude_1000"].sum() - 2560) < 1e-9 and t["xl_500_xs_500"].sum() == 1000
```
<!--sortie-->
```text
NUM R_eq 2714.2857142857147
```

### Application 6.2 — Le coefficient de variation selon la rétention (section 6.1.1)

**Objectif.** Mesurer ce que gagne la cédante en plafonnant chaque sinistre.

**Étape 1 — CV d'un sinistre plafonné.** On plafonne chaque sinistre à une rétention $r$ et l'on calcule le CV du sinistre net, puis celui de la charge annuelle $\sqrt{(1+\mathrm{CV}^2)/\lambda}$.

```python
lam = O.LAMBDA_2025
lignes = []
for r in [1e5, 2.5e5, 5e5, 1e6, 2e6, np.inf]:
    xn = np.minimum(x, r)
    cv = xn.std() / xn.mean()
    lignes.append({"retention": r, "cv_sinistre": cv, "cv_annuel": np.sqrt((1 + cv ** 2) / lam)})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
 retention  cv_sinistre  cv_annuel
  100000.0        0.851      0.083
  250000.0        1.202      0.099
  500000.0        1.547      0.117
 1000000.0        1.902      0.136
 2000000.0        2.258      0.156
       inf        2.508      0.171
```

**Étape 2 — Taille de portefeuille équivalente.** Quel portefeuille (nombre de sinistres) donnerait, sans réassurance, le CV annuel obtenu avec une rétention de 500 000 € ?

```python
cv0 = x.std() / x.mean(); cv5 = np.minimum(x, 5e5).std() / np.minimum(x, 5e5).mean()
lam_equiv = lam * (1 + cv0 ** 2) / (1 + cv5 ** 2)
print(f"{lam_equiv:,.0f} sinistres par an, soit {lam_equiv / lam:.1f} fois le portefeuille")
```
<!--sortie-->
```text
535 sinistres par an, soit 2.1 fois le portefeuille
```

**Lecture.** Plafonner à 500 000 € ramène le CV d'un sinistre de 2,51 à 1,55 et celui de la charge annuelle à 11,7 % ; obtenir la même régularité sans réassurance demanderait un portefeuille **2,1 fois plus gros**. Aller plus bas (100 000 €) abaisse encore le CV, mais au prix d'une prime cédée bien plus élevée : c'est le même arbitrage qu'en section 6.3.

```python hide
xn5 = np.minimum(x, 5e5); xn1 = np.minimum(x, 1e5)
NUM("cv0", cv0); NUM("cv5", cv5); NUM("cva5", np.sqrt((1 + cv5 ** 2) / lam)); NUM("k_ratio", (1 + cv0 ** 2) / (1 + cv5 ** 2))
assert xn1.std() / xn1.mean() < cv5 < cv0
```
<!--sortie-->
```text
NUM cv0 2.507895989003917
NUM cv5 1.5472716674533313
NUM cva5 0.11668631277113
NUM k_ratio 2.1477418196681266
```

### Application 6.3 — Le *burning cost* d'une tranche (section 6.2.1)

**Objectif.** Calculer à la main (avec pandas) le *burning cost* de la tranche « 1 M€ xs 1 M€ », puis mesurer l'effet de chaque correction.

**Étape 1 — Charge annuelle de la tranche.** On applique la tranche à chaque sinistre, puis on somme par année.

```python
a, L = 1e6, 1e6
par_an = sg.assign(charge=O.tranche(sg["montant"], a, L)).groupby("annee_survenance")["charge"].sum()
t = pd.DataFrame({"brut": par_an, "facteur": O.facteur_2025(par_an.index.values)})
t["ajuste"] = t["brut"] * t["facteur"]
print((t / 1e6).round(2).head(6).to_string())
```
<!--sortie-->
```text
                  brut  facteur  ajuste
annee_survenance                       
2010              1.56      0.0    2.43
2011              3.18      0.0    4.81
2012              2.25      0.0    3.31
2013              2.10      0.0    2.99
2014              3.00      0.0    4.15
2015              0.84      0.0    1.13
```

**Étape 2 — Moyennes et comparaison à la vérité.**

```python
vrai = O.prix_vrai(a, L)
for nom in ["brut", "ajuste"]:
    print(f"{nom:7s} {t[nom].mean()/1e6:.2f} M€  ({t[nom].mean()/vrai - 1:+.0%} par rapport à la vérité {vrai/1e6:.2f} M€)")
```
<!--sortie-->
```text
brut    1.95 M€  (-26% par rapport à la vérité 2.63 M€)
ajuste  2.50 M€  (-5% par rapport à la vérité 2.63 M€)
```

**Étape 3 — Une indexation à 4 % par habitude.** On recommence en gonflant chaque sinistre de $1{,}04^{2025-t}$ avant la tranche.

```python
infl = np.array([O.tranche(sg.loc[sg["annee_survenance"] == y, "montant"].values * 1.04 ** (2025 - y), a, L).sum() for y in t.index])
print(f"avec inflation 4 % : {(infl * t['facteur']).mean()/1e6:.2f} M€")
```
<!--sortie-->
```text
avec inflation 4 % : 4.55 M€
```

**Lecture.** Le brut donne 1,95 M€, l'ajusté 2,50 M€, la vérité 2,63 M€ : l'ajustement d'exposition corrige un biais de 26 %. L'indexation inutile à 4 % donne 4,55 M€, **73 % de trop** : la tranche amplifie les hypothèses d'inflation.

```python hide
NUM("bc_b", t["brut"].mean()); NUM("bc_a", t["ajuste"].mean()); NUM("bc_v", vrai); NUM("bc_i", (infl * t["facteur"]).mean())
NUM("b_err", 1 - t["brut"].mean() / vrai); NUM("i_err", (infl * t["facteur"]).mean() / vrai - 1)
assert t["brut"].mean() < t["ajuste"].mean() < (infl * t["facteur"]).mean()
```
<!--sortie-->
```text
NUM bc_b 1951204.4666666666
NUM bc_a 2498983.149580004
NUM bc_v 2628092.0358020714
NUM bc_i 4552745.988571543
NUM b_err 0.25755854814606005
NUM i_err 0.7323388703859011
```

### Application 6.4 — La courbe d'exposition (section 6.2.2)

**Objectif.** Estimer $G(d)=E[\min(X,d)]/E[X]$ et en déduire le prix de tranches.

**Étape 1 — La courbe.**

```python
G = lambda d: O.lev_empirique(x, d) / x.mean()
for d in [1e5, 2.5e5, 5e5, 1e6, 2e6, 3e6]:
    print(f"G({d/1e6:g} M€) = {G(d):.3f}")
```
<!--sortie-->
```text
G(0.1 M€) = 0.378
G(0.25 M€) = 0.569
G(0.5 M€) = 0.735
G(1 M€) = 0.877
G(2 M€) = 0.964
G(3 M€) = 0.993
```

**Étape 2 — Prix par fréquence × sévérité.** La charge de « $L$ xs $a$ » vaut $\lambda\,E[X]\,(G(a+L)-G(a))$.

```python
for a, L in O.COUCHES:
    prix = O.LAMBDA_2025 * x.mean() * (G(a + L) - G(a))
    print(f"{L/1e6:g} xs {a/1e6:g} : {prix/1e6:.2f} M€  (vérité {O.prix_vrai(a, L)/1e6:.2f} M€)")
```
<!--sortie-->
```text
0.5 xs 0.5 : 4.11 M€  (vérité 4.47 M€)
1 xs 1 : 2.52 M€  (vérité 2.63 M€)
2 xs 2 : 1.00 M€  (vérité 1.42 M€)
```

**Lecture.** L'approche par la courbe donne 4,11, 2,52 et 1,00 M€ pour les trois tranches, contre 4,47, 2,63 et 1,42 M€ en vérité : les écarts sont du même ordre que ceux du *burning cost* ajusté, car les deux utilisent les mêmes sinistres. 3,6 % de la charge attendue se situe au-delà de 2 M€ de sinistre, mais ces sinistres sont **15 sur 2 898** : la précision de $G$ aux grandes valeurs est faible.

```python hide
ps = [O.LAMBDA_2025 * x.mean() * (G(a + L) - G(a)) for a, L in O.COUCHES]
for i in range(3):
    NUM(f"p{i+1}", ps[i]); NUM(f"v{i+1}", O.prix_vrai(*O.COUCHES[i]))
NUM("au2", 1 - G(2e6)); NUM("n2", (x > 2e6).sum()); NUM("ntot", len(x))
```
<!--sortie-->
```text
NUM p1 4113631.361949321
NUM v1 4465085.120343618
NUM p2 2517526.2792484807
NUM v2 2628092.0358020714
NUM p3 1003665.2750282789
NUM v3 1422932.271331718
NUM au2 0.03563794688089872
NUM n2 15
NUM ntot 2898
```

### Application 6.5 — Ajuster une GPD : stabilité selon le seuil (section 6.2.3)

**Objectif.** Voir comment l'indice de queue et le prix d'une tranche varient avec le seuil.

**Étape 1 — Ajustements.**

```python
lignes = []
for u in [2e5, 3e5, 5e5, 7.5e5, 1e6]:
    xi, beta, n = O.ajuster_gpd(sg, u)
    lam_u = O.taux_depassement(sg, u)
    lignes.append({"seuil": u, "n": n, "xi": xi, "beta": beta, "prix_1xs1": O.prix_gpd(1e6, 1e6, u, xi, beta, lam_u)})
print(pd.DataFrame(lignes).round(3).to_string(index=False))
```
<!--sortie-->
```text
    seuil   n     xi       beta   prix_1xs1
 200000.0 366  0.318 306656.347 2329996.465
 300000.0 259  0.217 397435.465 2403833.599
 500000.0 177  0.416 312974.734 2208253.719
 750000.0  87  0.205 539176.465 2440414.159
1000000.0  49 -0.153 973149.529 2529452.430
```

**Étape 2 — Intervalle de confiance de $\xi$.** L'écart-type approché de l'estimateur est $(1+\xi)/\sqrt n$.

```python
for r in lignes:
    se = (1 + r["xi"]) / np.sqrt(r["n"])
    print(f"u = {r['seuil']:>9,.0f}  xi = {r['xi']:+.2f}  [{r['xi'] - 1.96*se:+.2f} ; {r['xi'] + 1.96*se:+.2f}]")
```
<!--sortie-->
```text
u =   200,000  xi = +0.32  [+0.18 ; +0.45]
u =   300,000  xi = +0.22  [+0.07 ; +0.37]
u =   500,000  xi = +0.42  [+0.21 ; +0.62]
u =   750,000  xi = +0.20  [-0.05 ; +0.46]
u = 1,000,000  xi = -0.15  [-0.39 ; +0.08]
```

**Lecture.** $\hat\xi$ varie de -0,15 à 0,42 selon le seuil, et le prix de « 1 M€ xs 1 M€ » de 2,21 à 2,53 M€ (vérité 2,63 M€). L'intervalle de $\hat\xi$ au seuil de 1 M€ (49 dépassements) contient **zéro** : on ne sait même pas si la queue est lourde ou légère. Aucun seuil ne donne un résultat « stable » ; il faut le dire dans le rapport.

```python hide
xis = [r["xi"] for r in lignes]; prs = [r["prix_1xs1"] for r in lignes]
NUM("xi_min", min(xis)); NUM("xi_max", max(xis)); NUM("pr_min", min(prs)); NUM("pr_max", max(prs)); NUM("pr_v", O.prix_vrai(1e6, 1e6))
NUM("n_hi", lignes[-1]["n"])
se_hi = (1 + lignes[-1]["xi"]) / np.sqrt(lignes[-1]["n"])
assert lignes[-1]["xi"] - 1.96 * se_hi < 0 < lignes[-1]["xi"] + 1.96 * se_hi
```
<!--sortie-->
```text
NUM xi_min -0.15275742739559262
NUM xi_max 0.4157030990878338
NUM pr_min 2208253.7187681845
NUM pr_max 2529452.429735458
NUM pr_v 2628092.0358020714
NUM n_hi 49
```

### Application 6.6 — Bootstrap : par années ou par sinistres ? (section 6.2.4)

**Objectif.** Comparer deux façons de rééchantillonner et comprendre laquelle sous-estime l'incertitude.

**Étape 1 — Par années (celle du livre).**

```python
a, L = 2e6, 2e6
b_ans = O.bootstrap_annees(sg, a, L, B=1000)
print(f"par années : [{np.percentile(b_ans, 2.5)/1e6:.2f} ; {np.percentile(b_ans, 97.5)/1e6:.2f}] M€")
```
<!--sortie-->
```text
par années : [0.54 ; 1.53] M€
```

**Étape 2 — Par sinistres.** On tire 2 898 sinistres avec remise, indépendamment de leur année, et l'on calcule la charge moyenne ajustée de la tranche en gardant la répartition des années.

```python
rng = np.random.default_rng(3)
an = sg["annee_survenance"].values; w = O.facteur_2025(an)
b_sin = []
for _ in range(1000):
    i = rng.integers(0, len(x), len(x))
    b_sin.append((O.tranche(x[i], a, L) * w[i]).sum() / 15)
print(f"par sinistres : [{np.percentile(b_sin, 2.5)/1e6:.2f} ; {np.percentile(b_sin, 97.5)/1e6:.2f}] M€")
```
<!--sortie-->
```text
par sinistres : [0.45 ; 1.66] M€
```

**Lecture.** Les deux intervalles ont des largeurs de 0,99 et 1,21 M€. Le bootstrap par sinistres fixe le nombre total de sinistres et **ignore la variabilité du nombre de sinistres d'une année à l'autre** ; il traite comme interchangeables des sinistres d'années différentes. Ses hypothèses diffèrent de celles du bootstrap par années, et son résultat aussi : un intervalle égal à 123 % de celui par années. Aucun des deux n'est « le bon » : on choisit celui dont les hypothèses correspondent à la façon dont les données sont produites (ici, des années d'exposition différentes). Dans les deux cas, la vérité (1,42 M€) tombe dans l'intervalle.

```python hide
w_a = np.percentile(b_ans, 97.5) - np.percentile(b_ans, 2.5); w_s = np.percentile(b_sin, 97.5) - np.percentile(b_sin, 2.5)
NUM("w_an", w_a); NUM("w_sin", w_s); NUM("ratio_w", w_s / w_a); NUM("vrai3", O.prix_vrai(a, L))
assert np.percentile(b_sin, 2.5) < O.prix_vrai(a, L) < np.percentile(b_sin, 97.5) and np.percentile(b_ans, 2.5) < O.prix_vrai(a, L) < np.percentile(b_ans, 97.5)
```
<!--sortie-->
```text
NUM w_an 988569.8428153803
NUM w_sin 1211341.1533306157
NUM ratio_w 1.2253470628648733
NUM vrai3 1422932.271331718
```

### Application 6.7 — Une tranche de catastrophe (section 6.2.5)

**Objectif.** Estimer une tranche de catastrophe avec 40 ans de données, et mesurer ce que l'on ignore.

**Étape 1 — Loi de Pareto ajustée.**

```python
alpha, p = O.pareto_cat(cat)
print(f"alpha = {alpha:.2f}  fréquence des années à événement = {p:.1%}  ({(c > 0).sum()} années)")
```
<!--sortie-->
```text
alpha = 1.33  fréquence des années à événement = 42.5%  (17 années)
```

**Étape 2 — La tranche « 10 M€ xs 10 M€ ».**

```python
a, L = 1e7, 1e7
emp = O.tranche(c, a, L).mean()
par = O.prix_pareto(a, L, p, alpha)
print(f"empirique {emp/1e6:.2f} M€ | Pareto {par/1e6:.2f} M€ | vérité {O.prix_vrai_cat(a, L)/1e6:.2f} M€")
print(f"années touchées dans l'historique : {(c > a).sum()} sur {len(c)}")
```
<!--sortie-->
```text
empirique 0.26 M€ | Pareto 0.31 M€ | vérité 0.50 M€
années touchées dans l'historique : 2 sur 40
```

**Lecture.** Dans l'historique, la tranche n'est touchée que 2 années sur 40 ; l'espérance empirique est de 0,26 M€ et ne repose que sur ces années-là. Le prix vrai de 0,50 M€ correspond à un ROL de 5,0 % et à une période de retour de 20 ans : **40 ans d'historique ne permettent pas de la vérifier**.

```python hide
NUM("touch", (c > 1e7).sum()); NUM("emp", emp); NUM("v10", O.prix_vrai_cat(a, L)); NUM("rol", O.prix_vrai_cat(a, L) / L); NUM("pb", L / O.prix_vrai_cat(a, L))
```
<!--sortie-->
```text
NUM touch 2
NUM emp 261668.25
NUM v10 502097.5209808956
NUM rol 0.05020975209808956
NUM pb 19.916449657954978
```

### Application 6.8 — La prime de risque (section 6.2.6)

**Objectif.** Calculer la prime technique d'une tranche selon deux principes, et mesurer la sensibilité à leurs paramètres.

**Étape 1 — La distribution de la charge annuelle de la tranche « 1 M€ xs 1 M€ ».**

```python
ch = O.charge_annuelle_vraie(1e6, 1e6, N=20000, seed=5)
E, sd, var995 = ch.mean(), ch.std(), np.percentile(ch, 99.5)
K = var995 - E
print(f"E = {E/1e6:.2f}  écart-type = {sd/1e6:.2f}  VaR 99,5 % = {var995/1e6:.2f}  K = {K/1e6:.2f} (M€)")
```
<!--sortie-->
```text
E = 2.61  écart-type = 1.43  VaR 99,5 % = 7.04  K = 4.43 (M€)
```

**Étape 2 — Grilles de paramètres.**

```python
print("Principe de l'écart-type : chargement relatif selon k")
print({k: f"{k*sd/E:.0%}" for k in [0.05, 0.10, 0.15, 0.20, 0.30]})
print("Coût du capital : chargement relatif selon i")
print({i: f"{i*K/E:.0%}" for i in [0.04, 0.06, 0.08, 0.10, 0.12]})
```
<!--sortie-->
```text
Principe de l'écart-type : chargement relatif selon k
{0.05: '3%', 0.1: '5%', 0.15: '8%', 0.2: '11%', 0.3: '16%'}
Coût du capital : chargement relatif selon i
{0.04: '7%', 0.06: '10%', 0.08: '14%', 0.1: '17%', 0.12: '20%'}
```

**Lecture.** L'espérance vaut 2,61 M€, l'écart-type 1,43 M€, la perte inattendue $K=4,43$ M€. Le chargement relatif va de 3 % à 16 % avec le principe de l'écart-type ($k$ de 0,05 à 0,30), de 7 % à 20 % avec le coût du capital (de 4 % à 12 %) : **les paramètres comptent autant que le principe**.

```python hide
NUM("e", E); NUM("sd", sd); NUM("k", K); NUM("c_lo", 0.05 * sd / E); NUM("c_hi", 0.30 * sd / E); NUM("i_lo", 0.04 * K / E); NUM("i_hi", 0.12 * K / E)
```
<!--sortie-->
```text
NUM e 2607840.6791623537
NUM sd 1434151.3677700786
NUM k 4430343.652755003
NUM c_lo 0.027496913044372257
NUM c_hi 0.16498147826623352
NUM i_lo 0.06795420729732682
NUM i_hi 0.20386262189198046
```

### Application 6.9 — Comparer des programmes (section 6.3.2)

**Objectif.** Refaire la comparaison du livre avec vos propres paramètres.

**Étape 1 — Le résultat brut.**

```python
simu = O.simuler(N=10000, seed=11)
brute = simu["brute"]
prime = brute.mean() / 0.70
resultat = 0.75 * prime - brute
q = lambda r: np.percentile(r, 0.5)
K0 = resultat.mean() - q(resultat)
print(f"K sans réassurance : {K0/1e6:.2f} M€  ruine à 8 M€ : {(resultat < -8e6).mean():.2%}")
```
<!--sortie-->
```text
K sans réassurance : 13.94 M€  ruine à 8 M€ : 3.03%
```

**Étape 2 — Une fonction qui évalue un programme.**

```python
def bilan(recup, prime_cedee):
    r = resultat + recup - prime_cedee
    K = r.mean() - q(r)
    return {"cout": prime_cedee - recup.mean(), "K": K, "economie": K0 - K, "ruine": (r < -8e6).mean()}
```

**Étape 3 — Quote-part : quelle part céder ?** Avec une commission de 25 %, on fait varier $\alpha$.

```python
for alpha in [0.1, 0.2, 0.3, 0.4]:
    b = bilan(alpha * brute + 0.25 * alpha * prime, alpha * prime)
    print(f"alpha {alpha:.0%} : coût {b['cout']/1e6:.2f} M€  K {b['K']/1e6:.1f} M€  coût par € économisé {b['cout']/b['economie']:.3f}")
```
<!--sortie-->
```text
alpha 10% : coût 0.21 M€  K 12.5 M€  coût par € économisé 0.148
alpha 20% : coût 0.41 M€  K 11.2 M€  coût par € économisé 0.148
alpha 30% : coût 0.62 M€  K 9.8 M€  coût par € économisé 0.148
alpha 40% : coût 0.82 M€  K 8.4 M€  coût par € économisé 0.148
```

**Étape 4 — Excédent de sinistre : quelle priorité ?** Même chargement de 35 % pour une tranche de portée 1 M€.

```python
for a in [2.5e5, 5e5, 1e6, 2e6]:
    rec = O.agreger(simu, O.tranche(simu["sinistres"], a, 1e6))
    b = bilan(rec, 1.35 * rec.mean())
    print(f"priorité {a/1e6:g} M€ : coût {b['cout']/1e6:.2f}  économie de capital {b['economie']/1e6:.2f}  par € {b['cout']/b['economie']:.2f}")
```
<!--sortie-->
```text
priorité 0.25 M€ : coût 3.43  économie de capital 5.49  par € 0.63
priorité 0.5 M€ : coût 1.99  économie de capital 4.53  par € 0.44
priorité 1 M€ : coût 0.88  économie de capital 2.96  par € 0.30
priorité 2 M€ : coût 0.29  économie de capital 1.38  par € 0.21
```

**Lecture.** La quote-part coûte 0,41 M€ pour 20 % et 0,82 M€ pour 40 % : son coût et son effet sur $K$ sont **proportionnels** à $\alpha$, donc le coût par euro reste constant (0,148). Pour l'excédent de sinistre, la priorité change tout : à 250 000 € de priorité la cédante paie une prime de 13,24 M€ pour récupérer 34 % de sa sinistralité moyenne ; à 2 M€ de priorité elle paie 1,10 M€ pour une protection qui n'intervient presque jamais.

```python hide
b20 = bilan(0.2 * brute + 0.25 * 0.2 * prime, 0.2 * prime); b40 = bilan(0.4 * brute + 0.25 * 0.4 * prime, 0.4 * prime)
NUM("qp_cout", b20["cout"]); NUM("qp_cout4", b40["cout"]); NUM("qp_ratio", b20["cout"] / b20["economie"])
assert abs(b20["cout"] / b20["economie"] - b40["cout"] / b40["economie"]) < 0.02
r_bas = O.agreger(simu, O.tranche(simu["sinistres"], 2.5e5, 1e6)); r_haut = O.agreger(simu, O.tranche(simu["sinistres"], 2e6, 1e6))
NUM("xl_part_bas", r_bas.mean() / brute.mean()); NUM("xl_prem_bas", 1.35 * r_bas.mean()); NUM("xl_prem_haut", 1.35 * r_haut.mean())
```
<!--sortie-->
```text
NUM qp_cout 412259.6244171439
NUM qp_cout4 824519.2488342877
NUM qp_ratio 0.1478540526394266
NUM xl_part_bas 0.33983809022791656
NUM xl_prem_bas 13239593.96508
NUM xl_prem_haut 1099912.9279500002
```

### Application 6.10 — Contrepartie et épuisement (section 6.3.4)

**Objectif.** Faire varier la probabilité de défaut du réassureur, puis le nombre de réintégrations.

**Étape 1 — Défaut du réassureur sur un stop-loss.**

```python
rec = O.tranche(brute, 38e6, 10e6); cout_sl = 1.4 * rec.mean()
rng = np.random.default_rng(5)
rus = {}
for pd_def in [0.0, 0.005, 0.02, 0.05]:
    d = rng.random(len(brute)) < pd_def
    r = resultat + np.where(d, 0.5 * rec, rec) - cout_sl
    rus[pd_def] = (r < -8e6).mean()
    print(f"défaut {pd_def:.1%} (indépendant) : ruine {rus[pd_def]:.3%}")
```
<!--sortie-->
```text
défaut 0.0% (indépendant) : ruine 0.020%
défaut 0.5% (indépendant) : ruine 0.020%
défaut 2.0% (indépendant) : ruine 0.040%
défaut 5.0% (indépendant) : ruine 0.140%
```

**Étape 2 — Plafond annuel d'une tranche « 2 M€ xs 2 M€ ».** La charge annuelle `ch2` est celle de la vérité ; on fait varier le nombre de réintégrations $k$ (plafond $(1+k)\times2$ M€).

```python
ch2 = O.charge_annuelle_vraie(2e6, 2e6)
for k in [0, 1, 2, 3]:
    plafond = (1 + k) * 2e6
    print(f"{k} réintégration(s) : plafond atteint dans {(ch2 >= plafond).mean():.1%} des années ; couvre {np.minimum(ch2, plafond).mean() / ch2.mean():.1%} de l'espérance")
```
<!--sortie-->
```text
0 réintégration(s) : plafond atteint dans 36.6% des années ; couvre 73.7% de l'espérance
1 réintégration(s) : plafond atteint dans 7.7% des années ; couvre 95.3% de l'espérance
2 réintégration(s) : plafond atteint dans 1.1% des années ; couvre 99.4% de l'espérance
3 réintégration(s) : plafond atteint dans 0.1% des années ; couvre 99.9% de l'espérance
```

**Lecture.** Un défaut **indépendant** à 5 % par an fait passer la probabilité de ruine de 0,02 % à 0,14 % : peu en points de pourcentage, mais bien plus en proportion (ces probabilités reposent sur quelques années simulées seulement : lisez-les comme des ordres de grandeur). Le plafond annuel est plus décisif : sans réintégration, la garantie n'**honore que 74 % de l'espérance**, avec une réintégration 95 %, avec trois 100 %.

```python hide
NUM("ru0", rus[0.0]); NUM("ru5", rus[0.05])
for k in [0, 1, 3]:
    NUM(f"cov{k}", np.minimum(ch2, (1 + k) * 2e6).mean() / ch2.mean())
assert rus[0.0] <= rus[0.05]
```
<!--sortie-->
```text
NUM ru0 0.0002
NUM ru5 0.0014
NUM cov0 0.7370814539100338
NUM cov1 0.9531587245707825
NUM cov3 0.9991250438543366
```

## Exercices

### Exercice 6.1 ⭐ — Quote-part avec commission (section 6.1.2)

Une cédante encaisse 10 M€ de primes, a 3 M€ de frais (30 %) et subit 7 M€ de sinistres. Elle cède **40 %** en quote-part avec une commission de cession de **30 %** de la prime cédée. Calculez la prime cédée, les sinistres cédés, la commission, puis le résultat de la cédante et du réassureur avant et après. Que se passe-t-il si les sinistres valent 8 M€ ?

### Exercice 6.2 ⭐ — Excédent de plénitude (section 6.1.2)

Une plénitude de 500 000 € est fixée. Un risque de capital assuré 2 M€ subit un sinistre de 1,2 M€ ; sa prime est de 20 000 €. Un second risque de 400 000 € subit un sinistre de 300 000 €. Calculez les parts cédées de sinistre et de prime.

### Exercice 6.3 ⭐ — Une tranche par risque (section 6.1.3)

La tranche « 300 xs 200 » (en k€) s'applique aux sinistres 150, 250, 400 et 700. Calculez les récupérations et le net. Même question avec un plafond annuel de 400.

### Exercice 6.4 ⭐⭐ — Réintégrations (section 6.1.3)

Une tranche « 1 000 xs 1 000 » (k€) coûte 400 par an. Elle a **deux** réintégrations : la première à 100 % pro rata du montant, la seconde à 50 %. Les sinistres de l'année touchent la tranche pour 600, 1 000, 1 000 puis 500. Calculez les paiements du réassureur (plafond annuel $3\times1\,000$), les primes de réintégration et le coût net.

### Exercice 6.5 ⭐⭐ — Plafonner vaut mieux que grossir (section 6.1.1)

Un portefeuille compte $\lambda=100$ sinistres par an, de coefficient de variation $\mathrm{CV}(X)=3$. Calculez le CV de la charge annuelle. Quel serait-il avec un portefeuille quatre fois plus grand ? Avec un plafonnement qui ramène le CV d'un sinistre à 1 ? Conclusion ?

### Exercice 6.6 ⭐ — *Burning cost* à la main (section 6.2.1)

Les charges annuelles (M€) d'une tranche sur cinq ans sont $0{,}8$ ; $0$ ; $2{,}4$ ; $0{,}5$ ; $1{,}2$, pour des expositions respectives de 100, 110, 120, 130 et 140. Quelle est la prime pure pour une exposition de 150 ? Quel est l'écart avec la moyenne brute ?

### Exercice 6.7 ⭐⭐ — Le levier de l'inflation (section 6.2.1)

Quatre sinistres de 0,9 ; 1,2 ; 1,5 et 2,5 M€ traversent la tranche « 1 M€ xs 1 M€ ». Avec 5 % d'inflation par an pendant trois ans, de combien augmente le coût de la tranche ? Comparez à l'augmentation des sinistres.

### Exercice 6.8 ⭐⭐ — Pareto et prix de tranche (section 6.2.2)

Les dépassements de 1 M€ sont au nombre de 10 par an et suivent une loi de Pareto de paramètre $\alpha$ : $P(X>x\mid X>1\,\text{M€})=(10^6/x)^{\alpha}$. Calculez la charge annuelle de « 2 M€ xs 1 M€ » pour $\alpha=2{,}5$ puis $\alpha=1{,}5$. Commentez.

### Exercice 6.9 ⭐⭐ — La formule GPD (section 6.2.3)

Avec $u=500\,000$, $\xi=0{,}3$, $\beta=400\,000$ et $\lambda_u=12$ par an, calculez la charge annuelle de « 1 M€ xs 1 M€ » par la formule fermée, puis par intégration numérique de la survie. Que devient le prix si $\xi$ passe à 0,5 ?

### Exercice 6.10 ⭐⭐⭐ — Les intervalles bootstrap couvrent-ils la vérité ? (section 6.2.4)

Rejouez 200 fois « quinze années d'observation » sous la vérité, calculez pour la tranche « 2 M€ xs 2 M€ » l'intervalle bootstrap par années, et mesurez la **part des intervalles qui contiennent la vérité**. Est-ce 95 % ?

### Exercice 6.11 ⭐⭐⭐ — Quote-part ou excédent de sinistre ? (section 6.3.2)

Dans l'étude de l'application 6.9 (commission de 25 %), quelle part $\alpha$ de quote-part économise autant de capital que l'excédent « 1 M€ xs 1 M€ » à 35 % de chargement ? Que coûte-t-elle ? À partir de quelle commission la quote-part coûterait-elle autant que l'excédent ?

### Exercice 6.12 ⭐⭐⭐ — Dimensionner un stop-loss (section 6.3.4)

Avec la portée de 10 M€ et le chargement de 40 % du livre, quelle est la **priorité la plus haute** (donc la moins chère) qui maintient la probabilité de ruine à 8 M€ sous 1 % ? Donnez le coût correspondant.

## Corrigés

### Corrigé 6.1

Prime cédée $0{,}4\times10=4$ ; sinistres cédés $0{,}4\times7=2{,}8$ ; commission $0{,}3\times4=1{,}2$. **Avant** : $10-3-7=0$. **Après**, la cédante garde une prime de 6, des sinistres de $4{,}2$ et des frais de $3-1{,}2=1{,}8$ : $6-4{,}2-1{,}8=0$. Le réassureur : $4-2{,}8-1{,}2=0$. La commission couvre exactement les frais : à 70 % de sinistralité, tout le monde est à l'équilibre. Avec 8 M€ de sinistres : avant, $10-3-8=-1$ ; après, la cédante $6-4{,}8-1{,}8=-0{,}6$ et le réassureur $4-3{,}2-1{,}2=-0{,}4$ : la perte se **partage 60/40**, comme la prime.

```python hide
assert abs((10 - 3 - 7)) < 1e-9 and abs((6 - 4.2 - 1.8)) < 1e-9 and abs(4 - 2.8 - 1.2) < 1e-9
assert abs((6 - 4.8 - 1.8) + 0.6) < 1e-9 and abs((4 - 3.2 - 1.2) + 0.4) < 1e-9
```

### Corrigé 6.2

Premier risque : taux de cession $\tau=1-500\,000/2\,000\,000=75\,\%$ ; sinistre cédé $0{,}75\times1{,}2=0{,}9$ M€, gardé $0{,}3$ M€ ; prime cédée $0{,}75\times20\,000=15\,000$ €. Second risque : le capital (400 000) est inférieur à la plénitude : $\tau=0$ ; rien n'est cédé, le sinistre de 300 000 € reste chez la cédante.

### Corrigé 6.3

Paiements : $150\to0$ ; $250\to50$ ; $400\to200$ (le sinistre dépasse 200 de 200, portée 300) ; $700\to300$ (dépasse de 500, plafonné à 300). Total **550**, net $1\,500-550=950$. Avec un plafond annuel de 400, le réassureur paie $\min(550,400)=400$ et le net vaut $1\,100$.

```python hide
pay = O.tranche([150, 250, 400, 700], 200, 300)
assert list(pay) == [0, 50, 200, 300] and pay.sum() == 550 and min(pay.sum(), 400) == 400
```

### Corrigé 6.4

Plafond annuel $3\,000$. Premier sinistre sur la tranche : 600 payés ; reconstitution de 600 à 100 % : prime $400\times600/1000=240$ (il reste 400 de capacité à 100 %). Deuxième : 1 000 payés (cumul 1 600) ; 400 reconstitués à 100 % ($400\times400/1000=160$) puis 600 à 50 % ($0{,}5\times400\times600/1000=120$). Troisième : 1 000 payés (cumul 2 600) ; la capacité restante de la seconde réintégration est de 400 à 50 % : $0{,}5\times400\times400/1000=80$. Quatrième : 500 demandés, mais il ne reste que $3\,000-2\,600=400$ de plafond : 400 payés, aucune reconstitution. **Paiements : $600+1\,000+1\,000+400=3\,000$ ; primes de réintégration : $240+160+120+80=600$** ; coût net $400+600-3\,000=-2\,000$, soit un gain de 2 000.

```python
def reintegrations(pertes, L, prime, taux_reint, plafond):
    """taux_reint : liste des taux (un par réintégration) ; la capacité de chacune vaut L"""
    reste = [L] * len(taux_reint); paye = prime_reint = 0.0
    for p in pertes:
        p = min(p, L, plafond - paye)
        paye += p; a_reconstituer = p
        for j, t in enumerate(taux_reint):
            r = min(a_reconstituer, reste[j]); prime_reint += t * prime * r / L; reste[j] -= r; a_reconstituer -= r
    return paye, prime_reint
print(reintegrations([600, 1000, 1000, 500], 1000, 400, [1.0, 0.5], 3000))
```
<!--sortie-->
```text
(3000.0, 600.0)
```

```python hide
assert reintegrations([600, 1000, 1000, 500], 1000, 400, [1.0, 0.5], 3000) == (3000.0, 600.0)
```

### Corrigé 6.5

$\mathrm{CV}(S)=\sqrt{(1+9)/100}=0{,}316$. Avec quatre fois plus de sinistres : $\sqrt{10/400}=0{,}158$, la moitié. Avec un plafonnement qui ramène le CV d'un sinistre à 1 : $\sqrt{(1+1)/100}=0{,}141$, **mieux** que le portefeuille quadruplé. Le rapport des tailles équivalentes est $(1+9)/(1+1)=5$ : plafonner équivaut à multiplier le portefeuille par 5. Conclusion : la réassurance non proportionnelle apporte une régularité que la mutualisation seule ne peut pas donner.

```python hide
assert abs(np.sqrt(10 / 100) - 0.3162) < 1e-3 and abs(np.sqrt(10 / 400) - 0.1581) < 1e-3 and abs(np.sqrt(2 / 100) - 0.1414) < 1e-3
```

### Corrigé 6.6

Facteurs $150/E_t$ : $1{,}5$ ; $1{,}364$ ; $1{,}25$ ; $1{,}154$ ; $1{,}071$. Charges ajustées : $0{,}8\times1{,}5=1{,}2$ ; $0$ ; $2{,}4\times1{,}25=3{,}0$ ; $0{,}5\times1{,}154=0{,}577$ ; $1{,}2\times1{,}071=1{,}286$. Somme $6{,}063$, **moyenne $1{,}213$ M€**. La moyenne brute vaut $4{,}9/5=0{,}98$ M€ : l'écart (+24 %) vient de l'exposition qui croît.

```python hide
E_t = np.array([100, 110, 120, 130, 140.]); ch_ = np.array([0.8, 0, 2.4, 0.5, 1.2])
assert abs((ch_ * 150 / E_t).mean() - 1.2125) < 5e-4 and abs(ch_.mean() - 0.98) < 1e-9
```

### Corrigé 6.7

Coefficient d'inflation : $1{,}05^3=1{,}1576$. Sinistres : $0{,}9\to1{,}042$ ; $1{,}2\to1{,}389$ ; $1{,}5\to1{,}736$ ; $2{,}5\to2{,}894$. Charges de la tranche (portée 1 M€) : avant $0+0{,}2+0{,}5+1=1{,}7$ M€ ; après $0{,}042+0{,}389+0{,}736+1=2{,}167$ M€. Le coût de la tranche monte de **27,5 %**, alors que les sinistres montent de 15,8 % : c'est l'effet de levier (le dernier sinistre était déjà plafonné, et le premier entre dans la tranche).

```python hide
cl = np.array([0.9, 1.2, 1.5, 2.5]) * 1e6
avant, apres = O.tranche(cl, 1e6, 1e6).sum(), O.tranche(cl * 1.05 ** 3, 1e6, 1e6).sum()
assert abs(avant - 1.7e6) < 1 and abs(apres - 2.16745e6) < 10
NUM("lev", apres / avant - 1)
```
<!--sortie-->
```text
NUM lev 0.2749705882352944
```

### Corrigé 6.8

Avec $\lambda_u=10$, $u=10^6$ : charge $=10\int_{10^6}^{3\times10^6}(10^6/x)^\alpha dx=10\cdot\dfrac{10^{6\alpha}}{\alpha-1}\bigl[(10^6)^{1-\alpha}-(3\cdot10^6)^{1-\alpha}\bigr]$. Pour $\alpha=2{,}5$ : 5,38 M€. Pour $\alpha=1{,}5$ : 8,45 M€, soit **1,6 fois plus** : pour une queue un peu plus lourde, le prix de la même tranche augmente de plus de moitié, d'où l'importance de $\alpha$.

```python hide
pareto = lambda lam_u, u, al, a, L: lam_u * u ** al / (al - 1) * (a ** (1 - al) - (a + L) ** (1 - al))
p25, p15 = pareto(10, 1e6, 2.5, 1e6, 2e6), pareto(10, 1e6, 1.5, 1e6, 2e6)
assert abs(integrate.quad(lambda t: 10 * (1e6 / t) ** 2.5, 1e6, 3e6)[0] - p25) < 1
NUM("pa25", p25); NUM("pa15", p15); NUM("ratio_pa", p15 / p25)
```
<!--sortie-->
```text
NUM pa25 5383666.068467499
NUM pa15 8452994.616207484
NUM ratio_pa 1.5701186716830846
```

### Corrigé 6.9

La formule donne $\lambda_u\frac{\beta}{1-\xi}\bigl[(1+\xi\tfrac{a-u}{\beta})^{1-1/\xi}-(1+\xi\tfrac{a+L-u}{\beta})^{1-1/\xi}\bigr]$ avec $a=10^6$, $L=10^6$.

```python
u, beta, lam_u = 5e5, 4e5, 12
for xi in [0.3, 0.5]:
    formule = O.prix_gpd(1e6, 1e6, u, xi, beta, lam_u)
    numerique = integrate.quad(lambda t: lam_u * (1 + xi * (t - u) / beta) ** (-1 / xi), 1e6, 2e6)[0]
    print(f"xi = {xi} : formule {formule/1e6:.4f} M€  intégration {numerique/1e6:.4f} M€")
```
<!--sortie-->
```text
xi = 0.3 : formule 2.0805 M€  intégration 2.0805 M€
xi = 0.5 : formule 2.5686 M€  intégration 2.5686 M€
```

Les deux calculs coïncident (2,080 M€ pour $\xi=0{,}3$) ; en passant à $\xi=0{,}5$, le prix devient 2,569 M€, soit **23 % de plus** pour un changement de 0,2 sur l'indice de queue.

```python hide
f03, f05 = O.prix_gpd(1e6, 1e6, 5e5, 0.3, 4e5, 12), O.prix_gpd(1e6, 1e6, 5e5, 0.5, 4e5, 12)
assert abs(integrate.quad(lambda t: 12 * (1 + 0.3 * (t - 5e5) / 4e5) ** (-1 / 0.3), 1e6, 2e6)[0] - f03) < 1
NUM("g03", f03); NUM("g05", f05); NUM("g_ratio", f05 / f03 - 1)
```
<!--sortie-->
```text
NUM g03 2080494.874967318
NUM g05 2568561.8729096996
NUM g_ratio 0.23459178093387445
```

### Corrigé 6.10

```python
rng = np.random.default_rng(2026)
a, L, B_out, vrai = 2e6, 2e6, 200, O.prix_vrai(2e6, 2e6)
dedans = 0
for _ in range(B_out):
    par_an = np.array([O.tranche(O.tirer_sinistres_vrais(rng, rng.poisson(160 * 1.03 ** i)), a, L).sum() * 1.03 ** (14 - i) * 1.03 for i in range(15)])
    boot = par_an[rng.integers(0, 15, (300, 15))].mean(axis=1)
    dedans += np.percentile(boot, 2.5) <= vrai <= np.percentile(boot, 97.5)
print(f"couverture empirique : {dedans / B_out:.1%}")
```
<!--sortie-->
```text
couverture empirique : 91.0%
```

La couverture est de 91 %, **inférieure aux 95 % annoncés** : avec quinze observations d'une variable à queue lourde, le bootstrap par années sous-estime l'incertitude (un rééchantillonnage ne peut pas inventer une année pire que celles observées). Un intervalle de bootstrap est un **minimum** d'incertitude.

```python hide
NUM("couv", dedans / B_out)
assert 0.6 < dedans / B_out < 0.97
```
<!--sortie-->
```text
NUM couv 0.91
```

### Corrigé 6.11

Sans réassurance, $K$ est proportionnel à la part gardée : une quote-part $\alpha$ économise $\alpha K_0$. L'excédent « 1 M€ xs 1 M€ » économise 2,96 M€, d'où $\alpha^\star=21,2$ %. Le coût de la quote-part vaut $\alpha(0{,}75\,P\,-E[S])$ avec $P=E[S]/0{,}7$, soit 0,44 M€, contre 0,88 M€ pour l'excédent. La commission qui rendrait le coût de la quote-part égal à celui de l'excédent est de 20,0 % (au lieu de 25 %) : **la quote-part n'est moins chère que parce que la commission rembourse les frais**.

```python hide
xl1m = O.agreger(simu, O.tranche(simu["sinistres"], 1e6, 1e6))
bx = bilan(xl1m, 1.35 * xl1m.mean())
a_star = bx["economie"] / K0
cost_qp = lambda comm: a_star * prime * (1 - comm) - a_star * brute.mean()
comm_eq = optimize.brentq(lambda cm: cost_qp(cm) - bx["cout"], 0, 0.9)
NUM("x_dk", bx["economie"]); NUM("a_star", a_star); NUM("c_qp", cost_qp(0.25)); NUM("c_xl", bx["cout"]); NUM("comm", comm_eq)
b_chk = bilan(a_star * brute + 0.25 * a_star * prime, a_star * prime)
assert abs(b_chk["economie"] / bx["economie"] - 1) < 0.05 and abs(b_chk["cout"] / cost_qp(0.25) - 1) < 0.05
```
<!--sortie-->
```text
NUM x_dk 2955755.5482
NUM a_star 0.21201224205775812
NUM c_qp 437020.4364128392
NUM c_xl 877657.48588
NUM comm 0.19958621922992809
```

### Corrigé 6.12

On balaie la priorité d'un stop-loss de portée 10 M€ et on garde la plus haute pour laquelle la ruine reste sous 1 %.

```python
res = []
for a in np.arange(34, 42, 0.5):
    rec = O.tranche(brute, a * 1e6, 10e6)
    b = bilan(rec, 1.4 * rec.mean()); res.append((a, b["cout"], b["ruine"]))
ok = [r for r in res if r[2] < 0.01]
print(ok[-1] if ok else "aucune priorité ne suffit")
```
<!--sortie-->
```text
(np.float64(38.5), np.float64(31785.67775999999), np.float64(0.0002))
```

La priorité maximale est de 38,5 M€, pour un coût de 0,032 M€ par an et une ruine de 0,02 %. Au-dessus, une partie des années où le capital de 8 M€ est consommé (charge brute au-delà de 38,9 M€) n'est plus couverte : **la priorité doit rester inférieure au point où le capital est épuisé**.

```python hide
res = []
for a_ in np.arange(34, 42, 0.5):
    rec_ = O.tranche(brute, a_ * 1e6, 10e6)
    b_ = bilan(rec_, 1.4 * rec_.mean()); res.append((a_, b_["cout"], b_["ruine"]))
ok_ = [r for r in res if r[2] < 0.01]
NUM("pmax", ok_[-1][0]); NUM("cmax", ok_[-1][1]); NUM("rmax", ok_[-1][2]); NUM("seuil_ruine", 0.75 * prime + 8e6)
assert ok_ and ok_[-1][0] < 41
```
<!--sortie-->
```text
NUM pmax 38.5
NUM cmax 31785.67775999999
NUM rmax 0.0002
NUM seuil_ruine 38919471.831285715
```
