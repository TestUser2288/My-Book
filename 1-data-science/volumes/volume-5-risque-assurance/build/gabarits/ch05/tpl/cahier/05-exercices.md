# Chapitre 5 : ➕ Assurance vie — exercices et applications

> 🧭 **Orientation.** Ce fichier accompagne le chapitre 5 du livre (tables de mortalité, mathématiques actuarielles de la vie, modèle de Lee–Carter). Il contient **huit applications guidées** (petites études sur les données du volume) puis **douze exercices** gradués (⭐ direct, ⭐⭐ demande un raisonnement, ⭐⭐⭐ plus délicat), tous corrigés à la fin. Les données sont **simulées** (`build/donnees5.py`) : la vérité programmée est connue et sert de juge. Le fichier est **autonome** : il recharge ses données et ses outils (`build/outils_ch05.py`). Essayez chaque énoncé avant de lire le corrigé.

```python
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
from outils_ch05 import *

def NUM(cle, valeur):
    print("NUM", cle, valeur)       # nombre cité dans la prose, relu lors de la vérification

pop = charger()                                                   # décès et expositions (sexe, âge, année)
M = {s: surface(pop, s) for s in "FM"}; E = {s: surface(pop, s, "exposition") for s in "FM"}; D = {s: surface(pop, s, "deces") for s in "FM"}
AX, BX, KT = verite()                                            # vérité programmée (a_x, b_x, k_t)
pv = pd.read_csv(os.path.join(DONNEES, "portefeuille_vie.csv"))
ages = np.arange(100)
I = 0.02; V_, D_ = 1 / (1 + I), I / (1 + I)                       # taux technique d'illustration
a30 = np.arange(30, 100)
P_GM = {s: gm_ajuste(a30, D[s][2019].loc[a30].to_numpy(), E[s][2019].loc[a30].to_numpy()) for s in "FM"}   # Gompertz–Makeham 2019
Q = {s: prolonge(q_depuis_m(M[s][2019].to_numpy()), P_GM[s]) for s in "FM"}                             # q_x 2019 fermés à 120 ans
T = {s: table_vie(Q[s]) for s in "FM"}
print({s: (round(float(T[s].e[0]), 2), round(float(T[s].e[65]), 2)) for s in "FM"})
```

## Applications

### Application 5.1 — Table de période des hommes et comparaison à la vérité (section 5.1)

**Objectif.** Construire la table 2019 des hommes, comparer espérances de vie des deux sexes, et juger l'erreur d'estimation face à la vérité programmée.

**Étape 1 — la table.** La cellule d'amorçage a déjà construit `T["M"]` (et `T["F"]`) : taux observés, $q=1-e^{-m}$, fermeture à 120 ans par la loi de Gompertz–Makeham ajustée sur les âges 30 à 99.

**Étape 2 — comparer à la table vraie.** Calculez la table obtenue avec les taux vrais $m_x=\exp(a_x+b_xk_t)$ de 2019 (fonction `m_vrai`) et comparez $e_0$ et $e_{65}$ pour les deux sexes.

```python
vrai = {s: table_vie(prolonge(q_depuis_m(m_vrai(s, 2019)), P_GM[s])) for s in "FM"}
for s in "FM":
    print(s, "e0 estimé", round(T[s].e[0], 2), "vrai", round(vrai[s].e[0], 2), "| e65 estimé", round(T[s].e[65], 2), "vrai", round(vrai[s].e[65], 2))
```

**Étape 3 — la surmortalité masculine.** Le rapport des taux hommes/femmes varie-t-il avec l'âge ? Un rapport calculé âge par âge est très bruité (quelques dizaines de décès par cellule) : regroupez par dizaines d'âges, en divisant les décès totaux par les expositions totales de la dizaine.

```python
def taux_dizaine(s, a0):
    cols = slice(a0, a0 + 9)
    return D[s][2019].loc[cols].sum() / E[s][2019].loc[cols].sum()
rapports = {f"{a0}–{a0 + 9}": round(float(taux_dizaine("M", a0) / taux_dizaine("F", a0)), 2) for a0 in range(30, 90, 10)}
print(rapports)
print("écart d'espérance de vie à 65 ans (F − H) :", round(T["F"].e[65] - T["M"].e[65], 2), "ans")
```

**À conclure.** Les écarts entre estimé et vrai sont de quelques centièmes d'année (population de centaines de milliers de personnes). Le rapport hommes/femmes est **à peu près constant** autour de 1,3 : c'est une propriété de la simulation (mortalité masculine programmée à 1,35 fois la féminine, atténuée par une tendance plus favorable). Sur des données réelles, il varie nettement avec l'âge, avec un maximum aux âges de jeune adulte.

```python hide
NUM("e0H", round(T["M"].e[0], 2)); NUM("e65H", round(T["M"].e[65], 2)); NUM("e65H_v", round(vrai["M"].e[65], 2))
NUM("e0F", round(T["F"].e[0], 2)); NUM("e65F", round(T["F"].e[65], 2)); NUM("e65F_v", round(vrai["F"].e[65], 2))
NUM("ratio_min", min(rapports.values())); NUM("ratio_max", max(rapports.values()))
NUM("ecart65", round(T["F"].e[65] - T["M"].e[65], 2))
assert abs(T["M"].e[65] - vrai["M"].e[65]) < 0.1 and all(1.1 < r < 1.5 for r in rapports.values())
```

### Application 5.2 — Lisser les taux d'un portefeuille : bruts, Gompertz–Makeham, Whittaker–Henderson (section 5.1.4)

**Objectif.** Comparer trois estimations de la mortalité des assurés par âge et juger laquelle s'approche le mieux de la vérité programmée (0,75 × la population).

**Étape 1 — les taux bruts.** On reconstruit les lignes contrat-année, puis décès et expositions par âge.

```python
L = lignes_police_annee(pv)
L["m_ref"] = [M[s].loc[a, t] for s, a, t in zip(L["sexe"], L["age"], L["annee"])]
L["attendu"] = L["expo"] * L["m_ref"]
g = L.groupby("age").agg(D=("deces", "sum"), E=("expo", "sum"), att=("attendu", "sum")).reset_index()
g = g[(g["age"] >= 30) & (g["age"] <= 79) & (g["E"] > 0)].reset_index(drop=True)
g["brut"] = g["D"] / g["E"]
g["vrai"] = 0.75 * g["att"] / g["E"]           # taux attendu d'après la table de population × 0,75 (par âge, avec la composition réelle)
print(g[["age", "D", "E", "brut", "vrai"]].head(4).round(4).to_string(index=False))
```

**Étape 2 — Gompertz–Makeham.** Ajustez la loi par maximum de vraisemblance poissonien sur ces âges et évaluez-la.

```python
p_pf = gm_ajuste(g["age"], g["D"], g["E"])
g["gm"] = gm_mu(g["age"] + 0.5, p_pf)
print("doublement tous les", round(np.log(2) / np.exp(p_pf[2]), 2), "ans")
```

**Étape 3 — Whittaker–Henderson.** On cherche le vecteur $\hat g=\ln \hat m$ qui minimise la **vraisemblance de Poisson pénalisée** $\sum_x\big(E_xe^{g_x}-D_xg_x\big)+\tfrac{\lambda}{2}\sum_x(\Delta^3g_x)^2$ : fidélité aux données, plus une pénalité sur les différences troisièmes (une parabole n'est pas pénalisée). Le critère est convexe : on le résout par des itérations de Newton, avec pour gradient $E e^{g}-D+\lambda\Delta^{3\top}\Delta^3 g$ et pour hessien $\mathrm{diag}(Ee^{g})+\lambda\Delta^{3\top}\Delta^3$.

```python
def whittaker(D, E, lam, ordre=3, it=40):
    n = len(D)
    Dm = np.diff(np.eye(n), ordre, axis=0)                  # matrice des différences d'ordre 3
    P = lam * Dm.T @ Dm
    g = np.full(n, np.log(D.sum() / E.sum()))              # départ : taux constant
    for _ in range(it):
        mu = E * np.exp(g)
        g = g - np.linalg.solve(np.diag(mu) + P, mu - D + P @ g)
    return np.exp(g)
g["wh"] = whittaker(g["D"].to_numpy(float), g["E"].to_numpy(float), lam=100.0)
```

**Étape 4 — juger.** Pour chaque méthode, calculez l'erreur relative moyenne (valeur absolue) par rapport à `vrai`. Essayez ensuite $\lambda=1$, $10$, $100$, $10^4$.

```python
for col in ("brut", "gm", "wh"):
    print(col, round(float(np.mean(np.abs(g[col] / g["vrai"] - 1))), 3))
for lam in (1, 10, 100, 1e4):
    h = whittaker(g["D"].to_numpy(float), g["E"].to_numpy(float), lam)
    print("lambda", lam, round(float(np.mean(np.abs(h / g["vrai"] - 1))), 3))
```

**À conclure.** L'erreur relative moyenne par rapport à la vérité est de {{err_brut}} % pour les taux bruts, {{err_gm}} % pour Gompertz–Makeham et {{err_wh}} % pour Whittaker–Henderson ($\lambda=100$). Les deux lissages rapprochent nettement de la vérité. Whittaker–Henderson dépend de $\lambda$ ({{errlam_1}} % pour $\lambda=1$, {{errlam_10000}} % pour $\lambda=10^4$ : trop petit, il colle au bruit ; très grand, il tend vers une parabole du logarithme) alors que Gompertz–Makeham n'a aucun réglage mais **impose une forme** : ici cette forme est exactement celle qui a servi à simuler, ce qui la favorise.

```python hide
err = {c: float(np.mean(np.abs(g[c] / g["vrai"] - 1))) for c in ("brut", "gm", "wh")}
for c, v in err.items():
    NUM("err_" + c, round(100 * v))
NUM("dbl_pf", round(np.log(2) / np.exp(p_pf[2]), 2))
errs_lam = {lam: float(np.mean(np.abs(whittaker(g["D"].to_numpy(float), g["E"].to_numpy(float), lam) / g["vrai"] - 1))) for lam in (1, 10, 100, 1e4)}
for lam, v in errs_lam.items():
    NUM(f"errlam_{int(lam)}", round(100 * v))
assert err["gm"] < err["brut"] and err["wh"] < err["brut"]
```

### Application 5.3 — Rapport réel/attendu par sexe, contrat et capital (section 5.1.5)

**Objectif.** Décomposer le rapport réel/attendu et le **pondérer par le capital**.

**Étape 1 — par sexe et par contrat.** Calculez $D$, l'attendu et le rapport avec son intervalle de Poisson pour chaque sexe puis chaque type de contrat.

```python
L["attendu"] = L["expo"] * L["m_ref"]
def tableau(par):
    lignes = []
    for k, h in L.groupby(par):
        r, b, hi = ae_ic(int(h["deces"].sum()), h["attendu"].sum())
        lignes.append((k, int(h["deces"].sum()), round(h["attendu"].sum(), 1), round(r, 3), round(b, 3), round(hi, 3)))
    return pd.DataFrame(lignes, columns=[par, "décès", "attendus", "A/E", "bas", "haut"])
print(tableau("sexe").to_string(index=False)); print(tableau("contrat").to_string(index=False))
```

**Étape 2 — pondérer par le capital.** Le coût d'un décès est le capital assuré : le rapport pertinent pour le résultat est $\sum C_i\delta_i / \sum C_iE_i m^{\text{réf}}_i$. Calculez-le et comparez au rapport en nombre.

```python
ae_n = L["deces"].sum() / L["attendu"].sum()
ae_c = (L["capital"] * L["deces"]).sum() / (L["capital"] * L["attendu"]).sum()
print(f"A/E en nombre {ae_n:.3f}   A/E pondéré par le capital {ae_c:.3f}")
```

**Étape 3 — précision.** L'intervalle de Poisson ne s'applique plus tel quel au rapport pondéré. Proposez une méthode (indice : *bootstrap* sur les contrats) et appliquez-la avec 500 rééchantillonnages.

```python
rng = np.random.default_rng(1)
par_contrat = L.groupby("id_contrat").agg(dec=("deces", "sum"), att=("attendu", "sum"), cap=("capital", "first"))
n = len(par_contrat); vals = []
for _ in range(500):
    h = par_contrat.iloc[rng.integers(0, n, n)]
    vals.append((h["cap"] * h["dec"]).sum() / (h["cap"] * h["att"]).sum())
print("A/E pondéré : IC bootstrap à 95 % =", np.percentile(vals, [2.5, 97.5]).round(3))
```

**À conclure.** Par sexe ou par contrat, **aucun sous-groupe ne se détache** de 0,75 (la sélection programmée est la même partout) ; le rapport pondéré par le capital est très proche du rapport en nombre mais son intervalle est **plus large**, parce qu'un décès de gros capital pèse beaucoup.

```python hide
for c in ("sexe", "contrat"):
    tt = tableau(c)
    assert (tt["bas"] < 0.75).all() and (tt["haut"] > 0.75).all(), tt
NUM("ae_n", round(ae_n, 3)); NUM("ae_c", round(ae_c, 3))
lo, hi = np.percentile(vals, [2.5, 97.5]); NUM("ae_c_lo", round(lo, 3)); NUM("ae_c_hi", round(hi, 3))
ae_all, b_all, h_all = ae_ic(int(L["deces"].sum()), L["attendu"].sum())
NUM("larg_n", round(h_all - b_all, 3)); NUM("larg_c", round(hi - lo, 3))
```

### Application 5.4 — Grille de tarifs et coût d'une tarification unisexe (section 5.2)

**Objectif.** Construire une grille de primes pures et mesurer l'effet d'une prime unique pour les deux sexes.

**Étape 1 — la grille.** Pour des temporaires de 10, 20 et 30 ans souscrites à 30, 40, 50 ans, calculez la prime annuelle pure pour 1 000 € de capital, pour chaque sexe (table 2019, 2 %).

```python
def prime_mille(q, x, n):
    At, at = temporaire(q, I, x, n)
    return 1000 * At / at
lignes = [(x, n, round(prime_mille(Q["F"], x, n), 2), round(prime_mille(Q["M"], x, n), 2)) for x in (30, 40, 50) for n in (10, 20, 30)]
print(pd.DataFrame(lignes, columns=["âge", "durée", "femmes", "hommes"]).to_string(index=False))
```

**Étape 2 — la prime unisexe.** Si l'assureur propose **la même prime** aux deux sexes, l'équivalence se fait sur l'ensemble de la population assurée : la prime unisexe est $P_u=\dfrac{w_H A^H+w_F A^F}{w_H\,\ddot a^H+w_F\,\ddot a^F}$ où $w_H,w_F$ sont les parts de chaque sexe (on prend 55 % d'hommes comme dans le portefeuille). Calculez-la pour une temporaire de 20 ans à 40 ans, et le transfert implicite entre sexes.

```python
x, n, wH = 40, 20, 0.55
AF_, aF_ = temporaire(Q["F"], I, x, n); AM_, aM_ = temporaire(Q["M"], I, x, n)
Pu = 1000 * (wH * AM_ + (1 - wH) * AF_) / (wH * aM_ + (1 - wH) * aF_)
Pf, Pm = prime_mille(Q["F"], x, n), prime_mille(Q["M"], x, n)
print(f"F {Pf:.2f}  H {Pm:.2f}  unisexe {Pu:.2f}   → les femmes paient {100 * (Pu / Pf - 1):.0f} % de plus, les hommes {100 * (1 - Pu / Pm):.0f} % de moins")
```

**À conclure.** Une prime unique **redistribue** : les femmes subventionnent les hommes. Si la composition du portefeuille change (davantage de femmes, car les hommes trouvent l'offre moins chère…), la prime unisexe devient insuffisante : c'est une **anti-sélection**.

```python hide
NUM("Pf", round(Pf, 2)); NUM("Pm", round(Pm, 2)); NUM("Pu", round(Pu, 2)); NUM("sub_f", round(100 * (Pu / Pf - 1))); NUM("sub_h", round(100 * (1 - Pu / Pm)))
assert Pf < Pu < Pm
```

### Application 5.5 — Provisions : prospectif, rétrospectif, changement de base (section 5.2.4)

**Objectif.** Calculer la provision d'une vie entière et mesurer ce qui arrive quand la table change en cours de contrat.

**Étape 1 — vie entière à 40 ans.** Capital 100 000 €, prime annuelle pure payable à vie. Calculez la prime puis la provision aux durées 10, 20 et 30 ans.

```python
A_, a_ = valeurs(Q["F"], I)
x = 40; C = 100000.0
P = C * A_[x] / a_[x]
for t in (10, 20, 30):
    print(f"t = {t:2d}   provision = {C * A_[x + t] - P * a_[x + t]:9.0f} €   ({100 * (C * A_[x + t] - P * a_[x + t]) / C:.1f} % du capital)")
print("prime annuelle :", round(P, 1))
```

**Étape 2 — changement de base.** La prime a été fixée avec la table de **1980** (2 %). Dix ans plus tard, on évalue la provision avec la table de **2019** : c'est le **boni ou mali de changement de base**. Calculez-le pour une temporaire de 20 ans à 40 ans, capital 100 000 €, au bout de 10 ans.

```python
q80 = prolonge(q_depuis_m(M["F"][1980].to_numpy()), P_GM["F"])
At, at = temporaire(q80, I, 40, 20); P80 = 100000 * At / at
V80 = reserve_prospective(q80, I, 40, 20, 100000, P80, 10)           # provision selon l'ancienne base
V19 = reserve_prospective(Q["F"], I, 40, 20, 100000, P80, 10)         # même contrat, nouvelle base
print(f"prime {P80:.1f}   provision ancienne base {V80:.0f}   nouvelle base {V19:.0f}   écart {V19 - V80:.0f} €")
```

**À conclure.** La provision d'une vie entière grimpe jusqu'à {{Vp_10}} %, {{Vp_20}} % puis {{Vp_30}} % du capital aux durées 10, 20 et 30 ans. Pour la temporaire, la mortalité a baissé depuis 1980 : la provision de la même police est de {{V80}} € avec l'ancienne base et de {{V19}} € avec la nouvelle (un montant **négatif** : les primes futures valent plus que les sinistres futurs, la prime de 1980 surpaye le risque de 2019). En pratique, on ne comptabilise pas de provision négative (on plafonne à zéro) et l'on libère un boni ; pour une rente, ce serait l'inverse : un **mali** à financer.

```python hide
for t in (10, 20, 30):
    NUM(f"V_{t}", round(C * A_[x + t] - P * a_[x + t])); NUM(f"Vp_{t}", round(100 * (C * A_[x + t] - P * a_[x + t]) / C, 1))
NUM("P_vie", round(P, 1)); NUM("P80", round(P80, 1)); NUM("V80", round(V80)); NUM("V19", round(V19)); NUM("ecart_base", round(V19 - V80))
assert V19 < V80
```

### Application 5.6 — Lee–Carter pour les hommes : ajustement, vérité et projection (section 5.3)

**Objectif.** Refaire pour les hommes l'analyse du livre, de bout en bout.

**Étape 1 — ajustement.** Ajustez le modèle (SVD puis recalage) et mesurez l'écart à la vérité.

```python
M_, E_, D_m = M["M"], E["M"], D["M"]
ax_, bx_, kt_, sv = lc_ajuste(M_)
kt_r = lc_recale(ax_, bx_, kt_, D_m.to_numpy(), E_.to_numpy())
ktv = KT["kt_M"].to_numpy()
print(f"première composante : {100 * sv[0] ** 2 / (sv ** 2).sum():.1f} %   rmse k : SVD {np.sqrt(np.mean((kt_ - ktv) ** 2)):.2f}  recalé {np.sqrt(np.mean((kt_r - ktv) ** 2)):.2f}")
print("corrélation b estimé / vrai :", round(np.corrcoef(bx_, BX)[0, 1], 3), "   max |a_x − a_x vrai| :", round(np.abs(ax_ - AX["M"]).max(), 3))
```

**Étape 2 — dérive et écart-type.** Estimez la dérive et σ, avec et sans l'année 2018 traitée par interpolation.

```python
i18 = list(ANNEES).index(2018)
k_i = kt_r.copy(); k_i[i18] = (k_i[i18 - 1] + k_i[i18 + 1]) / 2
print("brut :", np.round(derive_sigma(kt_r), 3), "  2018 interpolée :", np.round(derive_sigma(k_i), 3))
```

**Étape 3 — projeter.** Simulez 1 000 trajectoires sur 30 ans et donnez l'espérance de vie à 65 ans en 2049 (médiane et intervalle à 90 %). L'espérance de vie se calcule à partir de $k$ avec $a_x+b_xk$ et la fermeture de Gompertz–Makeham ajustée sur les hommes.

```python
delta, sigma = derive_sigma(k_i)
sim = lc_projette(ax_, bx_, kt_r, 30, 1000, delta, sigma, np.random.default_rng(5))
e65 = lambda k: table_vie(prolonge(q_depuis_m(np.exp(ax_ + bx_ * k)), P_GM["M"])).e[65]
k49 = np.percentile(sim[:, -1], [5, 50, 95])
print("e65 2019 :", round(e65(kt_r[-1]), 2), "   e65 2049 (5 %, médiane, 95 %) :", [round(float(e65(k)), 2) for k in k49[::-1]])
```

**À conclure.** Pour les hommes comme pour les femmes, la dérive est bien estimée (vraie dérive : −1,2 × 1,1 = −1,32 pour les hommes, puisque $k^H=1{,}1\,k^F$ dans le jeu) et σ est gonflé par le choc de 2018 et par l'erreur d'estimation.

```python hide
dh, sh = derive_sigma(kt_r); di, si = derive_sigma(k_i)
NUM("part_H", round(100 * sv[0] ** 2 / (sv ** 2).sum(), 1)); NUM("rmse_H", round(np.sqrt(np.mean((kt_r - ktv) ** 2)), 2))
NUM("delta_H", round(dh, 2)); NUM("sig_H", round(sh, 2)); NUM("sig_Hi", round(si, 2)); NUM("e65_H19", round(e65(kt_r[-1]), 2)); NUM("e65_H49", round(e65(k49[1]), 2))
assert abs(dh - (-1.32)) < 0.3
```

### Application 5.7 — Rentes : risque de tendance contre risque individuel (section 5.3.4)

**Objectif.** Chiffrer le risque de longévité d'un portefeuille de rentiers de 65 ans (hommes), avec et sans incertitude de paramètre.

**Étape 1 — le coût d'une rente par trajectoire.** On calcule, pour chaque trajectoire de $k$, le coût d'une rente de 1 € par an payée d'avance à 65 ans (taux 2 %), en suivant la cohorte : la mortalité de l'année $2019+j$ s'applique à l'âge $65+j$.

```python
def cout_rente(chemins):
    n = chemins.shape[0]; pv = np.zeros(n); surv = np.ones(n)
    kk = np.column_stack([np.full(n, kt_r[-1]), chemins[:, :54]])
    for j in range(55):
        age = 65 + j; pv += V_ ** j * surv
        m = np.exp(ax_[age] + bx_[age] * kk[:, j]) if age < 100 else gm_mu(age + 0.5, P_GM["M"])
        surv = surv * np.exp(-m)
    return pv
rng = np.random.default_rng(3)
sim55 = lc_projette(ax_, bx_, kt_r, 55, 2000, delta, sigma, rng)
pv_sans = cout_rente(sim55)
print("sans incertitude de paramètre : moyenne", round(pv_sans.mean(), 2), " quantile 99,5 %", round(np.quantile(pv_sans, 0.995), 2))
```

**Étape 2 — avec incertitude de paramètre.** Tirez la dérive de chaque trajectoire dans $\mathcal N(\hat\delta,\ \sigma/\sqrt{T-1})$.

```python
sd_d = sigma / np.sqrt(len(kt_r) - 1)
paths = kt_r[-1] + np.cumsum(rng.normal(delta, sd_d, 2000)[:, None] + rng.normal(0, sigma, (2000, 55)), axis=1)
pv_avec = cout_rente(paths)
print("avec incertitude de paramètre : moyenne", round(pv_avec.mean(), 2), " quantile 99,5 %", round(np.quantile(pv_avec, 0.995), 2), " écart-type relatif", round(100 * pv_avec.std() / pv_avec.mean(), 2), "%")
```

**Étape 3 — le seuil de diversification.** Un rentier seul a un coefficient de variation de son coût (loi des durées de vie) d'environ 45 %. À partir de combien de rentiers le risque de tendance domine-t-il ? Utilisez $N^*=(cv_{\text{indiv}}/cv_{\text{tendance}})^2$.

```python
cv_t = pv_avec.std() / pv_avec.mean()
print("N* ≈", round((0.45 / cv_t) ** 2, -2))
```

**À conclure.** L'incertitude de paramètre élargit un peu la distribution, mais **ne change pas l'ordre de grandeur** du risque de tendance (de l'ordre de {{cv_a}} %), très inférieur à un choc forfaitaire de 20 % sur les taux de décès (qui augmente le coût de la rente de {{choc_H}} %). Au-delà de {{Nstar:,.0f}} rentiers environ, le risque restant est celui de la tendance : **il ne se mutualise pas**.

```python hide
NUM("pv_moy", round(pv_sans.mean(), 2)); NUM("pv_q", round(np.quantile(pv_sans, 0.995), 2)); NUM("pv_moy_a", round(pv_avec.mean(), 2)); NUM("pv_q_a", round(np.quantile(pv_avec, 0.995), 2))
NUM("cv_a", round(100 * cv_t, 2)); NUM("Nstar", round((0.45 / cv_t) ** 2, -2))
q19 = Q["M"]
a_per = valeurs(q19, I)[1][65]; a_ch = valeurs(np.minimum(0.8 * q19, 1), I)[1][65]
NUM("a_per_H", round(a_per, 2)); NUM("choc_H", round(100 * (a_ch / a_per - 1), 1)); NUM("gen_H", round(100 * (pv_avec.mean() / a_per - 1), 1))
assert pv_avec.std() >= pv_sans.std() * 0.95
```

### Application 5.8 — Validation hors période : plusieurs dates de coupure (section 5.3.4)

**Objectif.** Répéter l'épreuve du livre pour plusieurs dates de coupure, et juger si la projection de Lee–Carter bat de façon régulière la table figée.

**Étape 1 — la boucle.** Pour chaque date de coupure $c\in\{2004, 2009, 2014\}$, ajustez le modèle sur les années jusqu'à $c$, projetez la médiane jusqu'en 2019 et comparez l'espérance de vie à 65 ans prévue à celle de la table **observée** de 2019 ; comparez avec la table de l'année $c$ figée.

```python
e65_obs = T["F"].e[65]
e65_de = lambda a_, b_, k: table_vie(prolonge(q_depuis_m(np.exp(a_ + b_ * k)), P_GM["F"])).e[65]
lignes = []
for c in (2004, 2009, 2014):
    cols = [t for t in ANNEES if t <= c]
    Mc = M["F"].loc[:, cols]
    a_, b_, k_, _ = lc_ajuste(Mc)
    k_ = lc_recale(a_, b_, k_, D["F"].loc[:, cols].to_numpy(), E["F"].loc[:, cols].to_numpy())
    dl, sg = derive_sigma(k_)
    h = 2019 - c
    prev = e65_de(a_, b_, k_[-1] + h * dl); fige = e65_de(a_, b_, k_[-1])
    lignes.append((c, h, round(prev, 2), round(fige, 2), round(abs(prev - e65_obs), 2), round(abs(fige - e65_obs), 2)))
print(pd.DataFrame(lignes, columns=["coupure", "horizon", "e65 projeté", "e65 figé", "erreur projet.", "erreur figé"]).to_string(index=False))
```

**Étape 2 — conclure.** Calculez le rapport moyen des erreurs. Une seule date de coupure ne suffit pas à conclure : pourquoi ?

**À conclure.** Pour les trois dates, la projection a une erreur plus petite que la table figée (en moyenne {{rap_err}} fois plus petite), et l'avantage **croît avec l'horizon** : l'erreur de la table figée augmente avec l'horizon alors que celle de la projection reste faible. Mais les trois ajustements partagent les mêmes données de 2019 pour juger (et l'erreur de projection est elle-même incertaine, de l'ordre de la précision de l'espérance de vie observée) : la **robustesse** d'une conclusion se juge sur plusieurs dates.

```python hide
errs = np.array([[r[4], r[5]] for r in lignes])
NUM("rap_err", round(float((errs[:, 1] / errs[:, 0]).mean()), 1))
for r in lignes:
    NUM(f"err_proj_{r[0]}", r[4]); NUM(f"err_fige_{r[0]}", r[5])
assert (errs[:, 0] < errs[:, 1]).all()
```

## Exercices

### Exercice 5.1 ⭐ — Du taux à la probabilité (section 5.1.1)

Dans une cellule d'âge 70 ans, on observe 1 850 décès pour 63 000 années-personnes. (1) Calculez le taux central $m_{70}$ et la probabilité de décès $q_{70}$ avec les deux conventions (force constante, décès uniformes). (2) Donnez l'erreur relative de $\hat m$ et un intervalle approximatif à 95 % pour $m$. (3) À partir de quelle valeur de $m$ les deux conventions diffèrent-elles de plus de 1 % (en valeur relative) ? À quel âge cela correspond-il dans la table des femmes de 2019 ?

### Exercice 5.2 ⭐ — Une table à la main (section 5.1.2)

Soient $q_{60}=0{,}010$, $q_{61}=0{,}012$, $q_{62}=0{,}014$, $q_{63}=0{,}017$. À partir de $\ell_{60}=100\,000$, calculez $\ell_{61},\dots,\ell_{64}$, les décès $d_x$, la probabilité de survie à 4 ans ${}_4p_{60}$ et la probabilité de décéder **entre 62 et 64 ans** (c'est-à-dire ${}_{2|2}q_{60}$).

### Exercice 5.3 ⭐⭐ — Gompertz et doublement (section 5.1.4)

Avec la loi $\mu(x)=B\,e^{c\,x}$ (on néglige $A$), $c=0{,}10$ et $\mu(60)=0{,}012$. (1) Calculez $\mu(70)$ et $\mu(80)$. (2) Montrez que la mortalité double tous les $\ln 2/c$ ans et donnez ce nombre. (3) Calculez la probabilité de survivre de 60 à 70 ans, $\exp\!\big(-\int_{60}^{70}\mu\big)$, en forme close puis numériquement.

### Exercice 5.4 ⭐⭐ — Combien de décès pour un A/E précis ? (section 5.1.5)

Un portefeuille observe 120 décès pour 160 attendus. (1) Donnez le rapport réel/attendu et un intervalle approché à 95 % par la loi normale. (2) Calculez l'intervalle exact de Poisson avec `ae_ic`. (3) Combien de décès faudrait-il, à rapport égal, pour que la demi-largeur de l'intervalle soit de 5 % du rapport ? (4) Que concluez-vous sur la possibilité de produire des rapports par tranche d'âge et de capital pour ce portefeuille ?

### Exercice 5.5 ⭐ — Prime d'une temporaire de 3 ans (section 5.2.1)

Refaites à la main le calcul du livre avec $q_{60}=0{,}012$, $q_{61}=0{,}013$, $q_{62}=0{,}015$, $i=3\,\%$ et un capital de 50 000 €. Donnez la prime unique pure puis la prime annuelle nivelée payée d'avance.

### Exercice 5.6 ⭐⭐ — Capital et rente avec une mortalité constante (section 5.2.2)

On suppose $q_x=q$ constant pour tous les âges. (1) Montrez que $\ddot a=\dfrac{1}{1-v(1-q)}$ et $A=\dfrac{vq}{1-v(1-q)}$. (2) Vérifiez $A=1-d\,\ddot a$. (3) Application numérique : $q=0{,}02$ et $i=2\,\%$.

### Exercice 5.7 ⭐⭐ — Sensibilité de la rente au taux technique (section 5.2.5)

(1) Calculez le coût d'une rente viagère de 1 000 € par an à 65 ans (femmes, table 2019) pour les taux techniques 0 %, 1 %, 2 %, 3 %, 4 %. (2) Quel est le taux d'intérêt pour lequel la rente coûte exactement la durée moyenne restante de vie actualisée à 0 %, et que vaut cette durée ? (3) De combien baisse le coût quand le taux passe de 1 % à 2 % ? Comparez au changement de table de 2019 vers 1980.

### Exercice 5.8 ⭐⭐ — Provision après un an, deux méthodes (section 5.2.4)

Temporaire de 3 ans, 60 ans, $q=(0{,}013;\,0{,}014;\,0{,}015)$, $i=2\,\%$, capital 100 000 € et prime nivelée du livre (1 370,4 €). Calculez ${}_1V$ par la méthode prospective puis par la méthode rétrospective, et vérifiez la récurrence $(\,{}_0V+P)(1+i)=q_{60}C+p_{60}\,{}_1V$.

### Exercice 5.9 ⭐⭐⭐ — Identifiabilité et contraintes de Lee–Carter (section 5.3.1)

(1) Montrez que les deux transformations $(a_x,b_x,k_t)\mapsto(a_x+c\,b_x,\,b_x,\,k_t-c)$ et $(a_x,b_x,k_t)\mapsto(a_x,\,\lambda b_x,\,k_t/\lambda)$ laissent inchangés tous les taux. (2) Les contraintes $\sum_tk_t=0$ et $\sum_xb_x=1$ suffisent-elles à fixer une solution unique ? (3) Numériquement : prenez le $k_t$ estimé (femmes) du jeu, appliquez la transformation avec $c=5$ puis $\lambda=2$ et vérifiez que les taux ajustés ne changent pas ; que valent alors $\sum b_x$ et $\sum k_t$ ?

### Exercice 5.10 ⭐⭐ — Une SVD de rang 1 sur une petite matrice (section 5.3.2)

Soit la matrice des $\ln m$ centrés par ligne, pour 3 âges et 4 années : $Z=\begin{pmatrix}0{,}30&0{,}10&-0{,}10&-0{,}30\\0{,}15&0{,}05&-0{,}05&-0{,}15\\0{,}33&0{,}08&-0{,}12&-0{,}29\end{pmatrix}$. (1) Calculez la SVD avec `numpy`, donnez la part de variation de la première composante. (2) Déduisez $b_x$ (somme 1) et $k_t$ et vérifiez que $b_xk_t$ reproduit $Z$ à quelques centièmes. (3) Pourquoi cette matrice se factorise-t-elle presque parfaitement, contrairement aux données du chapitre ?

### Exercice 5.11 ⭐⭐ — Incertitude sur la dérive (section 5.3.3)

On estime $\hat\delta=(k_T-k_1)/(T-1)$ avec $T=40$ années et un écart-type d'accroissements $\sigma=1{,}57$. (1) Quel est l'écart-type de $\hat\delta$ si les $k_t$ étaient observés sans erreur ? (2) Donnez un intervalle à 95 % pour $\delta$ autour de $-1{,}29$. (3) Combien d'années faudrait-il pour réduire l'écart-type de $\hat\delta$ à 0,10 ? Qu'en pensez-vous ?

### Exercice 5.12 ⭐⭐⭐ — Diversification et tendance (section 5.3.4)

Un rentier isolé a un coefficient de variation $cv_1=0{,}45$ de son coût actualisé ; le risque de tendance a un coefficient de variation $cv_t=0{,}010$ pour tout portefeuille. (1) Écrivez le coefficient de variation du coût **moyen** d'un portefeuille de $N$ rentiers, en supposant les deux risques indépendants et en additionnant les variances. (2) Calculez-le pour $N=100$, $1\,000$, $10\,000$, $100\,000$. (3) À partir de quel $N$ le risque de tendance fournit-il plus de la moitié de la variance totale ? (4) Quelle décision de gestion cela inspire-t-il ?

## Corrigés

### Corrigé 5.1

```python
from scipy.optimize import brentq
D1, E1 = 1850, 63000
m1 = D1 / E1
print("m70 =", round(m1, 5), "  q (force constante) =", round(1 - np.exp(-m1), 5), "  q (uniforme) =", round(m1 / (1 + m1 / 2), 5))
print("erreur relative =", round(100 / np.sqrt(D1), 2), "%   IC 95 % pour m :", np.round([m1 * (1 - 1.96 / np.sqrt(D1)), m1 * (1 + 1.96 / np.sqrt(D1))], 5))
ecart = lambda m: (m / (1 + m / 2)) / (1 - np.exp(-m)) - 1
m_crit = brentq(lambda m: ecart(m) - 0.01, 0.01, 2.0)
age_crit = int(np.argmax(M["F"][2019].to_numpy() > m_crit))
print("écart relatif à m = 0,1 :", round(100 * ecart(0.1), 2), "%  à m = 0,2 :", round(100 * ecart(0.2), 2), "%  seuil de 1 % : m =", round(m_crit, 3), " atteint à", age_crit, "ans")
```

(1) $m_{70}={{m70}}$ ; $q^{\text{const}}={{q70c}}$ et $q^{\text{unif}}={{q70u}}$, quasi identiques. (2) L'erreur relative est $1/\sqrt{1850}\approx{{err_rel70}}$ %, soit un intervalle à 95 % de [{{m70_lo}} ; {{m70_hi}}]. (3) L'écart relatif entre les deux conventions est de {{ec01}} % à $m=0{,}1$ et de {{ec02}} % à $m=0{,}2$ ; il atteint 1 % pour $m\approx{{m_crit}}$, valeur que la table des femmes de 2019 franchit à {{age_crit}} ans. Les deux conventions ne se distinguent donc qu'aux âges très élevés.

```python hide
NUM("m70", round(m1, 5)); NUM("q70c", round(1 - np.exp(-m1), 5)); NUM("q70u", round(m1 / (1 + m1 / 2), 5))
NUM("err_rel70", round(100 / np.sqrt(D1), 2)); NUM("m70_lo", round(m1 * (1 - 1.96 / np.sqrt(D1)), 5)); NUM("m70_hi", round(m1 * (1 + 1.96 / np.sqrt(D1)), 5))
NUM("ec01", round(100 * ecart(0.1), 2)); NUM("ec02", round(100 * ecart(0.2), 2)); NUM("m_crit", round(m_crit, 2)); NUM("age_crit", age_crit)
```

### Corrigé 5.2

$\ell_{61}=100\,000\times0{,}990=99\,000$ ; $\ell_{62}=99\,000\times0{,}988=97\,812$ ; $\ell_{63}=97\,812\times0{,}986=96\,442{,}6$ ; $\ell_{64}=96\,442{,}6\times0{,}983=94\,803{,}1$. Décès : $d_{60}=1\,000$, $d_{61}=1\,188$, $d_{62}=1\,369{,}4$, $d_{63}=1\,639{,}5$. ${}_4p_{60}=0{,}99\times0{,}988\times0{,}986\times0{,}983=0{,}94803$. ${}_{2|2}q_{60}=({}_2p_{60})\,(1-{}_2p_{62})=\dfrac{\ell_{62}-\ell_{64}}{\ell_{60}}=0{,}97812-0{,}94803=0{,}03009$ : il y a environ 3 % de chances de décéder entre 62 et 64 ans pour une personne de 60 ans.

```python
q = np.array([0.010, 0.012, 0.014, 0.017]); l = 100000 * np.concatenate([[1], np.cumprod(1 - q)])
print(np.round(l, 1), np.round(l[:-1] * q, 1), round(l[4] / l[0], 5), round((l[2] - l[4]) / l[0], 5))
assert abs(l[3] - 96442.6) < 0.1 and abs(l[4] - 94803.1) < 0.1 and abs((l[2] - l[4]) / l[0] - 0.03009) < 1e-5
```

### Corrigé 5.3

(1) $\mu(70)=0{,}012\,e^{1}=0{,}03262$ et $\mu(80)=0{,}012\,e^{2}=0{,}08867$. (2) $\mu(x+h)/\mu(x)=e^{c h}=2\iff h=\ln2/c={{dbl_ex}}$ ans. (3) $\int_{60}^{70}\mu=\frac{\mu(60)}{c}(e^{c\cdot10}-1)=0{,}12\,(e-1)\approx{{int_mu}}$, donc la survie est $e^{-{{int_mu}}}={{surv_ex}}$.

```python
c, mu60 = 0.10, 0.012
from scipy.integrate import quad
I_ = quad(lambda x: mu60 * np.exp(c * (x - 60)), 60, 70)[0]
print(round(mu60 * np.exp(c * 10), 5), round(mu60 * np.exp(c * 20), 5), round(np.log(2) / c, 2), round(I_, 5), round(np.exp(-I_), 4))
```

```python hide
NUM("dbl_ex", round(np.log(2) / c, 2)); NUM("int_mu", round(I_, 4)); NUM("surv_ex", round(np.exp(-I_), 4))
assert abs(I_ - 0.12 * (np.e - 1)) < 1e-9
```

### Corrigé 5.4

```python
ae0, b0, h0 = ae_ic(120, 160)
print("A/E =", round(ae0, 3), " normal :", round(ae0 * (1 - 1.96 / np.sqrt(120)), 3), round(ae0 * (1 + 1.96 / np.sqrt(120)), 3), " exact :", round(b0, 3), round(h0, 3))
print("décès nécessaires pour ±5 % :", int(np.ceil((1.96 / 0.05) ** 2)))
```

(1) Le rapport est $120/160={{ae4}}$ ; l'intervalle normal est [{{ae4_nlo}} ; {{ae4_nhi}}]. (2) L'intervalle exact est [{{ae4_lo}} ; {{ae4_hi}}], un peu **dissymétrique** et plus large du côté supérieur (la loi de Poisson est asymétrique pour un petit nombre de décès). (3) $1{,}96/\sqrt{D}\le0{,}05\iff D\ge1\,537$. (4) Avec 120 décès, **aucune analyse par sous-groupe n'est possible** : en divisant en trois tranches d'âge, chacune aurait environ 40 décès, soit ±31 % de précision. Il faut grouper, ou renoncer à l'analyse fine.

```python hide
NUM("ae4", round(ae0, 3)); NUM("ae4_nlo", round(ae0 * (1 - 1.96 / np.sqrt(120)), 3)); NUM("ae4_nhi", round(ae0 * (1 + 1.96 / np.sqrt(120)), 3)); NUM("ae4_lo", round(b0, 3)); NUM("ae4_hi", round(h0, 3))
assert int(np.ceil((1.96 / 0.05) ** 2)) == 1537
```

### Corrigé 5.5

Avec $i=3\,\%$, $v=0{,}970874$ ; $v^2=0{,}942596$ ; $v^3=0{,}915142$. $p_{60}=0{,}988$, $p_{61}=0{,}987$. Décès : $q_{60}=0{,}012$ ; $p_{60}q_{61}=0{,}988\times0{,}013=0{,}012844$ ; $p_{60}p_{61}q_{62}=0{,}988\times0{,}987\times0{,}015=0{,}014627$. Donc $A^1=0{,}970874\times0{,}012+0{,}942596\times0{,}012844+0{,}915142\times0{,}014627=0{,}011650+0{,}012107+0{,}013386=0{,}037143$ ; **prime unique** $=50\,000\times0{,}037143=1\,857{,}2$ €. Rente temporaire : $\ddot a=1+0{,}970874\times0{,}988+0{,}942596\times0{,}988\times0{,}987=1+0{,}959223+0{,}919178=2{,}878401$ ; **prime annuelle** $=1\,857{,}2/2{,}8784=645{,}2$ €.

```python
qq = np.array([0.012, 0.013, 0.015]); v3 = 1 / 1.03
pp = np.cumprod(np.r_[1, 1 - qq[:-1]])
A1 = sum(v3 ** (k + 1) * pp[k] * qq[k] for k in range(3)); a1 = sum(v3 ** k * pp[k] for k in range(3))
print(round(A1, 6), round(50000 * A1, 1), round(a1, 6), round(50000 * A1 / a1, 1))
assert abs(50000 * A1 - 1857.2) < 0.1 and abs(a1 - 2.878401) < 1e-5 and abs(50000 * A1 / a1 - 645.2) < 0.1
```

### Corrigé 5.6

(1) Avec $q$ constant, ${}_kp=(1-q)^k$ et $\ddot a=\sum_{k\ge0}\big(v(1-q)\big)^k=\dfrac{1}{1-v(1-q)}$ ; $A=\sum_{k\ge0}v^{k+1}(1-q)^kq=vq\,\ddot a$. (2) $1-d\,\ddot a=\dfrac{1-v(1-q)-(1-v)}{1-v(1-q)}=\dfrac{vq}{1-v(1-q)}=A$ (car $d=1-v$). (3) Avec $q=0{,}02$, $v=1/1{,}02$ : $1-v(1-q)=1-0{,}960784=0{,}039216$, donc $\ddot a={{a_cte}}$ et $A={{A_cte}}$.

```python
q0, v0 = 0.02, 1 / 1.02
a0 = 1 / (1 - v0 * (1 - q0)); A0 = v0 * q0 * a0
print(round(a0, 4), round(A0, 4), round(1 - (1 - v0) * a0, 4))
```

```python hide
NUM("a_cte", round(a0, 3)); NUM("A_cte", round(A0, 4))
assert abs(A0 - (1 - (1 - v0) * a0)) < 1e-12
```

### Corrigé 5.7

```python
for ii in (0.0, 0.01, 0.02, 0.03, 0.04):
    print(ii, round(1000 * valeurs(Q["F"], ii)[1][65]))
a0_ = valeurs(Q["F"], 0.0)[1][65]
q80 = prolonge(q_depuis_m(M["F"][1980].to_numpy()), P_GM["F"])
print("durée moyenne (ä à 0 %) :", round(a0_, 2), "  1980 vs 2019 à 2 % :", round(valeurs(q80, 0.02)[1][65], 3), round(valeurs(Q["F"], 0.02)[1][65], 3))
```

(1) Les coûts sont de {{r0}}, {{r1}}, {{r2}}, {{r3}} et {{r4}} € pour 0, 1, 2, 3 et 4 %. (2) À 0 %, la rente coûte simplement le **nombre moyen de versements** (le premier étant payé d'avance) : {{dur_moy}}, soit $e_{65}+\tfrac12$ environ ; c'est la durée de vie résiduelle moyenne, à une demi-année près. (3) De 1 % à 2 %, le coût baisse de {{bais_12}} % ; passer de la table de 2019 à celle de 1980 à 2 % ferait baisser le coût de {{bais_tab}} % : **une table ancienne d'une quarantaine d'années pèse davantage qu'un point de taux technique**.

```python hide
cc = {ii: 1000 * valeurs(Q["F"], ii)[1][65] for ii in (0.0, 0.01, 0.02, 0.03, 0.04)}
for k, ii in enumerate((0.0, 0.01, 0.02, 0.03, 0.04)):
    NUM(f"r{k}", round(cc[ii]))
NUM("dur_moy", round(a0_, 2)); NUM("bais_12", round(100 * (1 - cc[0.02] / cc[0.01]), 1))
NUM("bais_tab", round(100 * (1 - valeurs(q80, 0.02)[1][65] / valeurs(Q["F"], 0.02)[1][65]), 1))
assert abs(a0_ - (1 + T["F"].e[65] - 0.5)) < 0.1, (a0_, T["F"].e[65])
```

### Corrigé 5.8

Prospective : ${}_1V=C\,A^1_{61:\overline2|}-P\,\ddot a_{61:\overline2|}$ avec $A^1_{61:\overline 2|}=vq_{61}+v^2p_{61}q_{62}=0{,}013725+0{,}014215=0{,}027941$ et $\ddot a_{61:\overline2|}=1+v\,p_{61}=1{,}966667$, donc ${}_1V=2\,794{,}1-1\,370{,}4\times1{,}966667\approx99$ €. Rétrospective : ${}_1V=\dfrac{P(1+i)-C\,q_{60}}{p_{60}}$ (une seule année écoulée). Récurrence de Thiele : $({}_0V+P)(1+i)=q_{60}C+p_{60}\,{}_1V$ avec ${}_0V=0$ : c'est exactement la formule rétrospective.

```python
qq3 = [0.013, 0.014, 0.015]; C3, P3 = 100000, 1370.4
Q3 = np.zeros(65); Q3[60:63] = qq3; Q3[63] = 1.0
V1_pro = reserve_prospective(Q3, I, 60, 3, C3, P3, 1)
V1_retro = (P3 * (1 + I) - C3 * qq3[0]) / (1 - qq3[0])
print(round(V1_pro, 2), round(V1_retro, 2), round((0 + P3) * (1 + I) - (qq3[0] * C3 + (1 - qq3[0]) * V1_pro), 3))
```

Les deux méthodes donnent ${}_1V={{V1_pro}}$ € (méthode prospective) et ${{V1_retro}}$ € (méthode rétrospective) ; l'écart de quelques centimes tient à l'arrondi de la prime à 1 370,4 € (la prime exacte est de l'ordre de 1 370,36 €).

```python hide
NUM("V1_pro", round(V1_pro, 1)); NUM("V1_retro", round(V1_retro, 1))
assert abs(V1_pro - V1_retro) < 0.5 and abs(V1_pro - 99.0) < 0.3, V1_pro
```

### Corrigé 5.9

(1) Pour la première transformation : $a_x+c\,b_x+b_x(k_t-c)=a_x+b_xk_t$ ; pour la seconde : $a_x+(\lambda b_x)(k_t/\lambda)=a_x+b_xk_t$. (2) La première liberté est supprimée par $\sum k_t=0$ (on ne peut plus déplacer une constante), la seconde par $\sum b_x=1$ (on ne peut plus échanger d'échelle) : **la solution est unique à l'exception d'un signe commun** ($b\to-b$, $k\to-k$, même taux), que l'on fixe en imposant que $b_x$ soit positif. (3) Vérification :

```python
ax_f, bx_f, kt_f, _ = lc_ajuste(M["F"])
base = np.exp(ax_f[:, None] + bx_f[:, None] * kt_f[None, :])
c_, lam = 5.0, 2.0
a2, b2, k2 = ax_f + c_ * bx_f, bx_f, kt_f - c_
a3, b3, k3 = a2, lam * b2, k2 / lam
print(np.abs(np.exp(a3[:, None] + b3[:, None] * k3[None, :]) / base - 1).max(), round(b3.sum(), 2), round(k3.sum(), 1))
```

Les taux sont identiques (écart relatif maximal de l'ordre de $10^{-15}$), mais $\sum b_x={{sb3}}$ et $\sum k_t={{sk3}}$ : on a quitté la normalisation. C'est pourquoi on **compare toujours des estimations à des valeurs normalisées de la même façon**.

```python hide
NUM("sb3", round(b3.sum(), 2)); NUM("sk3", round(k3.sum(), 1))
assert np.abs(np.exp(a3[:, None] + b3[:, None] * k3[None, :]) / base - 1).max() < 1e-12
```

### Corrigé 5.10

```python
Z = np.array([[0.30, 0.10, -0.10, -0.30], [0.15, 0.05, -0.05, -0.15], [0.33, 0.08, -0.12, -0.29]])
U, S, Vt = np.linalg.svd(Z, full_matrices=False)
b = U[:, 0] / U[:, 0].sum(); k = S[0] * Vt[0] * U[:, 0].sum()
print("part de la 1re composante :", round(S[0] ** 2 / (S ** 2).sum(), 4), " b =", b.round(3), " k =", k.round(3))
print("écart maximal |Z − b k| :", np.abs(Z - np.outer(b, k)).max().round(3))
```

(1) La première composante explique {{part10}} % de la variation. (2) On obtient $b=({{b10}})$ et $k=({{k10}})$, et le produit $b_xk_t$ reproduit $Z$ à {{ecart10}} près. (3) Cette matrice a été **construite** (presque exactement de rang 1, à de petits écarts près) : il n'y a pas de bruit de Poisson. Les données du chapitre, elles, contiennent des décès aléatoires : la première composante n'y explique que 64 %.

```python hide
NUM("part10", round(100 * S[0] ** 2 / (S ** 2).sum(), 2)); NUM("b10", "; ".join(f"{v:.3f}".replace(".", "{,}") for v in b)); NUM("k10", "; ".join(f"{v:.3f}".replace(".", "{,}") for v in k)); NUM("ecart10", round(float(np.abs(Z - np.outer(b, k)).max()), 3))
assert S[0] ** 2 / (S ** 2).sum() > 0.99
```

### Corrigé 5.11

(1) Les accroissements sont indépendants de variance $\sigma^2$, donc $\mathrm{Var}(\hat\delta)=\sigma^2(T-1)/(T-1)^2=\sigma^2/(T-1)$ et l'écart-type est $\sigma/\sqrt{T-1}={{sd11}}$. (2) Intervalle à 95 % : $-1{,}29\pm1{,}96\times{{sd11}}$, soit [{{lo11}} ; {{hi11}}] : la dérive est connue à environ ±{{pct11}} %. (3) Il faudrait $T-1=\sigma^2/0{,}10^2\approx{{T11}}$ années, soit près de deux siècles et demi de données annuelles : **on ne peut pas réduire cette incertitude par la collecte**, seulement la reconnaître et la propager dans les projections.

```python
sg, T_ = 1.57, 40
sd = sg / np.sqrt(T_ - 1)
print(round(sd, 3), np.round([-1.29 - 1.96 * sd, -1.29 + 1.96 * sd], 2), round(100 * 1.96 * sd / 1.29), "%", round(sg ** 2 / 0.10 ** 2))
```

```python hide
NUM("sd11", round(sd, 2)); NUM("lo11", round(-1.29 - 1.96 * sd, 2)); NUM("hi11", round(-1.29 + 1.96 * sd, 2)); NUM("pct11", round(100 * 1.96 * sd / 1.29)); NUM("T11", round(sg ** 2 / 0.10 ** 2))
```

### Corrigé 5.12

(1) Variances additives : $cv^2(N)=cv_1^2/N+cv_t^2$. (2) Le code donne les valeurs ci-dessous. (3) Le risque de tendance fournit plus de la moitié de la variance totale quand $cv_t^2>cv_1^2/N$, c'est-à-dire $N>(cv_1/cv_t)^2=2\,025$. (4) Passé quelques milliers de rentiers, **grossir ne réduit plus le risque** : il faut le transférer (réassurance de longévité, chapitre 6) ou le couvrir par une marge ou un capital, et non attendre que la mutualisation le fasse.

```python
cv1, cvt = 0.45, 0.010
for N in (100, 1000, 10000, 100000):
    print(N, round(100 * np.sqrt(cv1 ** 2 / N + cvt ** 2), 2), "%   part de la tendance :", round(100 * cvt ** 2 / (cv1 ** 2 / N + cvt ** 2)), "%")
print("N* =", round((cv1 / cvt) ** 2))
```

```python hide
for N in (100, 1000, 10000, 100000):
    NUM(f"cvN_{N}", round(100 * np.sqrt(cv1 ** 2 / N + cvt ** 2), 2))
assert round((cv1 / cvt) ** 2) == 2025
```
