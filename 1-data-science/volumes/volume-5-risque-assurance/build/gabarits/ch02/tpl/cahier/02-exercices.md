# Chapitre 2 : Modélisation actuarielle — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 2 du livre. Les **applications** refont, étape par étape et avec le code, les études du livre (comptage, queue, modèle collectif, GLM de tarification, validation, provisionnement, crédibilité, santé) ; les **exercices** se travaillent d'abord à la main, puis se vérifient par le calcul. Données : `polices_auto.csv`, `sinistres_auto.csv`, les triangles et `sante_assures.csv`, toutes **simulées**. Le cahier est autonome : il recharge ses données.

## Applications

### Préparation commune

À exécuter une fois : elle charge les données, revalorise les montants en euros de 2024 et sépare **estimation (2022-2023)** et **test (2024)**.

```python
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from outils_ch02 import *

pol, sin = charger_polices()
sin = sin.merge(pol[["id_police", "puissance", "zone", "classe_age"]], on="id_police")
sin["rev"] = sin["montant"] * 1.04 ** (2024 - sin["annee"])          # euros de 2024
tr, te = pol[pol["annee"] <= 2023].copy(), pol[pol["annee"] == 2024].copy()
print(len(pol), "lignes police-année ;", len(sin), "sinistres ; exposition 2024 :", round(te["exposition"].sum()))
```

```python hide
def NUM(cle, valeur):
    print("NUM", cle, valeur)
NUM("n_pol", len(pol)); NUM("n_sin", len(sin))
```

### Application 2.1 — Compter les sinistres : exposition et Poisson (section 2.1.2)

**Objectif.** Estimer la fréquence annuelle par année d'exposition, mesurer son incertitude, et mesurer le biais d'une estimation « par contrat ».

**Étape 1 — le taux et son erreur-type.** Le taux estimé est $\hat\lambda=\sum N_i/\sum e_i$ et son erreur-type $\sqrt{\hat\lambda/\sum e_i}$.

```python
N, E = pol["nb_sinistres"].sum(), pol["exposition"].sum()
lam = N / E
print(f"taux = {lam:.4f} ± {np.sqrt(lam / E):.4f}  (par contrat : {N / len(pol):.4f})")
```

**Étape 2 — par année et par zone.** On calcule le taux de chaque année et de chaque zone, avec l'intervalle de confiance exact à 95 % de Garwood pour une moyenne de Poisson, déduit de la loi du $\chi^2$ : de $\chi^2_{0{,}025}(2n)/2$ à $\chi^2_{0{,}975}(2n+2)/2$ pour $n$ sinistres, divisé par l'exposition.

```python
g = pol.groupby("zone").agg(n=("nb_sinistres", "sum"), e=("exposition", "sum"))
bas, haut = stats.chi2.ppf(0.025, 2 * g["n"]) / 2, stats.chi2.ppf(0.975, 2 * g["n"] + 2) / 2
g["taux %"] = 100 * g["n"] / g["e"]
g["bas %"], g["haut %"] = 100 * bas / g["e"], 100 * haut / g["e"]
print(g[["e", "n", "taux %", "bas %", "haut %"]].round(2))
```

**Lecture.** Le taux global vaut {{a1_lam|pc2}} %, avec une erreur-type de {{a1_se|pc2}} point ; l'estimation « par contrat » ({{a1_par_contrat|pc2}} %) le sous-estime de {{a1_biais|pc0}} %. Les intervalles par zone se recouvrent beaucoup (la zone A va de {{a1_zA_bas|1}} % à {{a1_zA_haut|1}} %, la zone F de {{a1_zF_bas|1}} % à {{a1_zF_haut|1}} %) : les écarts de fréquence entre zones **existent**, mais une comparaison zone par zone, sans modèle, manque de précision.

```python hide
NUM("a1_lam", lam); NUM("a1_se", np.sqrt(lam / E)); NUM("a1_par_contrat", N / len(pol)); NUM("a1_biais", 1 - (N / len(pol)) / lam)
NUM("a1_zA_bas", g.loc["Zone A", "bas %"]); NUM("a1_zA_haut", g.loc["Zone A", "haut %"]); NUM("a1_zF_bas", g.loc["Zone F", "bas %"]); NUM("a1_zF_haut", g.loc["Zone F", "haut %"])
```

**Pour aller plus loin.** Refaites le calcul sur 2022 seul puis sur 2024 seul : comparez l'erreur-type à l'écart entre les deux taux (est-il statistiquement significatif ?).

### Application 2.2 — Sur-dispersion et binomiale négative (section 2.1.3)

**Objectif.** Montrer, par simulation puis sur les données, que l'hétérogénéité non observée produit une variance supérieure à la moyenne.

**Étape 1 — Poisson–Gamma par simulation.** On tire $\Theta\sim\mathrm{Gamma}$ de moyenne 1 et de variance $\alpha$, puis $N\mid\Theta\sim\mathrm{Poisson}(\mu\Theta)$.

```python
rng = np.random.default_rng(0)
mu, alpha = 0.2, 0.8
theta = rng.gamma(1 / alpha, alpha, 1_000_000)         # forme 1/alpha, échelle alpha : moyenne 1, variance alpha
n_sim = rng.poisson(mu * theta)
print("moyenne", n_sim.mean().round(4), "; variance", n_sim.var().round(4), "; théorie :", mu + alpha * mu ** 2)
```

**Étape 2 — la même chose sur les données.** On ajuste un modèle de Poisson puis un modèle binomial négatif avec les mêmes variables et l'exposition en décalage.

```python
F = "nb_sinistres ~ C(classe_age) + puissance + C(zone) + bonus_malus + C(usage) + C(carburant) + age_vehicule"
poi = smf.glm(F, pol, family=sm.families.Poisson(), offset=np.log(pol["exposition"])).fit()
nbm = smf.negativebinomial(F, pol, offset=np.log(pol["exposition"])).fit(disp=0)
print("dispersion de Pearson :", round(poi.pearson_chi2 / poi.df_resid, 3))
print("alpha =", round(nbm.params["alpha"], 3), "± ", round(nbm.bse["alpha"], 3))
```

**Lecture.** La simulation donne une variance de {{a2_var|3}} pour une valeur théorique de {{a2_var_th|3}}. Sur les données, la dispersion de Pearson est de {{a2_phi|3}} et $\hat\alpha={{a2_alpha|2}}$ ({{a2_se|2}}) : la sur-dispersion est discrète (le taux est faible) mais **significative** ({{a2_t|1}} erreurs-types de zéro). Comparez avec la vérité programmée, 0,4.

```python hide
NUM("a2_var", n_sim.var()); NUM("a2_var_th", mu + alpha * mu ** 2)
NUM("a2_phi", poi.pearson_chi2 / poi.df_resid); NUM("a2_alpha", nbm.params["alpha"]); NUM("a2_se", nbm.bse["alpha"]); NUM("a2_t", nbm.params["alpha"] / nbm.bse["alpha"])
```

### Application 2.3 — La queue et la charge annuelle (sections 2.1.5 et 2.1.6)

**Objectif.** Ajuster une loi de Pareto généralisée, écrêter, ajouter une charge pour gros sinistres, puis simuler la charge d'une année.

**Étape 1 — la GPD à 100 000 €.** Les excès au-delà du seuil sont ajustés par `genpareto` avec une position fixée à zéro.

```python
u = 100_000
exces = sin.loc[sin["rev"] > u, "rev"] - u
xi, _, echelle = stats.genpareto.fit(exces, floc=0)
print(len(exces), "excès ; xi =", round(xi, 3), "; échelle =", round(echelle))
print("part du coût au-delà du seuil :", round((sin["rev"] - u).clip(lower=0).sum() / sin["rev"].sum(), 3))
```

**Étape 2 — écrêtement et charge.** On plafonne chaque sinistre à 100 000 € et l'on calcule la charge commune des gros sinistres par année d'exposition.

```python
ecrete = sin["rev"].clip(upper=u)
charge = (sin["rev"] - u).clip(lower=0).sum() / pol["exposition"].sum()
print("moyenne écrêtée :", round(ecrete.mean()), "; moyenne brute :", round(sin["rev"].mean()), "; charge :", round(charge, 1), "€ par année d'exposition")
```

**Étape 3 — la charge annuelle d'un portefeuille de 2024.** Le nombre de sinistres est de Poisson de moyenne $\hat\lambda\times$ exposition 2024 ; les montants sont rééchantillonnés dans l'historique (revalorisé).

```python
rng = np.random.default_rng(1)
lam24 = pol["nb_sinistres"].sum() / pol["exposition"].sum() * te["exposition"].sum()
x = sin["rev"].values
S = np.array([rng.choice(x, n).sum() for n in rng.poisson(lam24, 2000)])
print("moyenne", round(S.mean() / 1e6, 2), "M€ ; écart-type", round(S.std() / 1e6, 2), "M€ ; quantile 99,5 %", round(np.quantile(S, 0.995) / 1e6, 2), "M€")
```

**Lecture.** À 100 000 €, $\hat\xi={{a3_xi|2}}$ sur {{a3_k|int}} excès : une valeur supérieure à 0,5 (variance infinie), mais très incertaine. La part du coût située **au-delà** de 100 000 € (l'excès) représente {{a3_part|pc0}} % du coût total. L'écrêtement ramène la moyenne de {{a3_moy|int}} € à {{a3_moy_e|int}} € et laisse une charge de {{a3_charge|int}} € par année d'exposition. La charge annuelle simulée a pour moyenne {{a3_S|1}} M€, pour écart-type {{a3_Ssd|2}} M€ et pour quantile à 99,5 % {{a3_q|1}} M€.

```python hide
NUM("a3_xi", xi); NUM("a3_k", len(exces)); NUM("a3_part", (sin["rev"] - u).clip(lower=0).sum() / sin["rev"].sum())
NUM("a3_moy", sin["rev"].mean()); NUM("a3_moy_e", ecrete.mean()); NUM("a3_charge", charge)
NUM("a3_S", S.mean() / 1e6); NUM("a3_Ssd", S.std() / 1e6); NUM("a3_q", np.quantile(S, 0.995) / 1e6)
```

**Pour aller plus loin.** Refaites l'étape 3 en remplaçant le rééchantillonnage par une simulation où les montants dépassant 100 000 € sont tirés dans la GPD ajustée : le quantile à 99,5 % change-t-il ? De combien ?

### Application 2.4 — Un tarif par deux GLM (section 2.2.2)

**Objectif.** Estimer un GLM de fréquence (2022-2023), un GLM de sévérité des sinistres matériels, puis calculer une prime pure pour trois profils.

**Étape 1 — la fréquence.**

```python
F = ("nb_sinistres ~ C(classe_age, Treatment('40-49')) + puissance + C(zone, Treatment('Zone C'))"
     " + bonus_malus + C(usage) + C(carburant) + age_vehicule")
freq = smf.glm(F, tr, family=sm.families.Poisson(), offset=np.log(tr["exposition"])).fit()
rel = np.exp(freq.params).round(3)
print(rel[["puissance", "bonus_malus", "C(usage)[T.professionnel]"]])
```

**Étape 2 — la sévérité, par type.** Matériel : GLM Gamma ; corporel : moyenne unique après écrêtement à 100 000 € ; plus la charge pour gros sinistres.

```python
st = sin[sin["annee"] <= 2023]
sev = smf.glm("rev ~ puissance + C(zone, Treatment('Zone C'))", st[st["type"] == "materiel"],
              family=sm.families.Gamma(sm.families.links.Log())).fit(scale="X2")
q = (st["type"] == "corporel").mean(); m_cor = st.loc[st["type"] == "corporel", "rev"].clip(upper=100_000).mean()
charge = (st["rev"] - 100_000).clip(lower=0).sum() / tr["exposition"].sum()
print("part corporelle", round(q, 3), "; moyenne écrêtée", round(m_cor), "; charge", round(charge, 1))
```

**Étape 3 — trois profils.** Prime pure $=\hat\lambda(x)\,[(1-q)\hat\mu_{\text{mat}}(x)+q\,m_{\text{cor}}]+$ charge.

```python
prof = pd.DataFrame({"classe_age": ["18-24", "40-49", "70+"], "puissance": [7, 5, 3], "zone": ["Zone F", "Zone C", "Zone A"],
                     "bonus_malus": [100, 70, 60], "usage": ["prive"] * 3, "carburant": ["essence", "diesel", "hybride_electrique"],
                     "age_vehicule": [3.0, 6.0, 2.0]})
lam_p = freq.predict(prof, offset=np.zeros(3)); sev_p = (1 - q) * sev.predict(prof) + q * m_cor
prof["prime pure"] = (lam_p * sev_p + charge).round(0)
print(prof[["classe_age", "zone", "prime pure"]])
```

**Lecture.** Les relativités estimées pour la puissance ({{a4_puiss|3}} par niveau), le bonus-malus ({{a4_bm|3}} par point) et l'usage professionnel ({{a4_pro|3}}) se comparent à leurs valeurs programmées (1,041 ; 1,006 ; 1,105). Les trois profils sont tarifés {{a4_p1|int}} €, {{a4_p2|int}} € et {{a4_p3|int}} € : le premier coûte {{a4_rapport|1}} fois le troisième.

```python hide
NUM("a4_puiss", rel["puissance"]); NUM("a4_bm", rel["bonus_malus"]); NUM("a4_pro", rel["C(usage)[T.professionnel]"])
NUM("a4_p1", prof.loc[0, "prime pure"]); NUM("a4_p2", prof.loc[1, "prime pure"]); NUM("a4_p3", prof.loc[2, "prime pure"]); NUM("a4_rapport", prof.loc[0, "prime pure"] / prof.loc[2, "prime pure"])
```

### Application 2.5 — Valider hors période et mesurer l'antisélection (sections 2.2.5 et 2.2.6)

**Objectif.** Calculer le Gini de tarification de 2024 pour un tarif plat et le tarif de l'application 2.4, puis simuler un concurrent mieux segmenté.

**Étape 1 — les primes de 2024 et les coûts observés (écrêtés).**

```python
te["lam"] = freq.predict(te, offset=np.zeros(len(te)))
te["pp"] = te["lam"] * ((1 - q) * sev.predict(te) + q * m_cor) + charge
s24 = sin[sin["annee"] == 2024]
c24 = cout_par_police(te, s24[["id_police"]].assign(montant=s24["rev"].clip(upper=100_000).values))
e24, y24 = te["exposition"].values, c24["cout"].values
base = st["rev"].clip(upper=100_000).sum() / tr["exposition"].sum() + charge
print("prime moyenne du tarif :", round((te["pp"] * e24).sum() / e24.sum()), "; tarif plat :", round(base))
```

**Étape 2 — le Gini de chaque tarif, avec un intervalle.** Le tarif plat n'a aucun pouvoir de classement ; un tarif aléatoire sert de repère du bruit.

```python
tarifs = {"plat": np.full(len(te), base) * e24, "complet": te["pp"].values * e24}
gini = {k: lorenz_gini(v, y24, e24)[2] for k, v in tarifs.items()}
rng = np.random.default_rng(0)
bruit = np.std([lorenz_gini(rng.random(len(y24)) * e24, y24, e24)[2] for _ in range(50)])
print({k: round(v, 3) for k, v in gini.items()}, "; bruit d'un tarif aléatoire :", round(bruit, 3))
```

**Étape 3 — l'antisélection.** Un concurrent applique le tarif complet ; nous appliquons un tarif plat. Nos assurés restent s'ils sont moins chers chez nous ; la charge des gros sinistres est fixée à son niveau prévu.

```python
reste = tarifs["plat"] <= tarifs["complet"]
sp0 = (y24.sum() + charge * e24.sum()) / tarifs["plat"].sum()
sp1 = (y24[reste].sum() + charge * e24[reste].sum()) / tarifs["plat"][reste].sum()
print("part conservée", round(reste.mean(), 3), "; sinistres/primes :", round(sp0, 3), "->", round(sp1, 3))
```

**Lecture.** Le Gini est de {{a5_gp|2}} pour le tarif plat (le bruit d'un tarif aléatoire est de {{a5_bruit|3}}) et de {{a5_gc|2}} pour le tarif complet. Après antisélection, la mutuelle ne garde que {{a5_part|pc0}} % de son exposition et son ratio sinistres sur primes passe de {{a5_sp0|pc0}} % à {{a5_sp1|pc0}} %.

```python hide
NUM("a5_gp", gini["plat"]); NUM("a5_gc", gini["complet"]); NUM("a5_bruit", bruit); NUM("a5_part", reste.mean()); NUM("a5_sp0", sp0); NUM("a5_sp1", sp1)
```

**Pour aller plus loin.** Remplacez la règle « on part si le concurrent est moins cher » par une probabilité de départ qui croît avec l'écart de prix (par exemple une logistique de pente 10 sur l'écart relatif) : l'antisélection est-elle aussi forte ?

### Application 2.6 — Chain ladder, de la main au code (section 2.3)

**Objectif.** Refaire le chain ladder du livre sur le triangle de responsabilité civile, estimer une queue et comparer aux paiements réels.

```python
tri = pd.read_csv("donnees/triangle_rc.csv"); ver = pd.read_csv("donnees/triangle_rc_verite.csv")
Cum = triangle_cumule(tri).values
V = ver.pivot(index="annee_survenance", columns="delai", values="paiement_cumule").values
f = facteurs_chain_ladder(Cum)
paye = dernier_cumul(Cum)
print("facteurs :", f.round(3))
```

```python
queue, taux = facteur_queue(f, depuis=4)
res = {}
for nom, fq in (("sans queue", 1.0), ("queue extrapolée", queue)):
    _, ult = projeter(Cum, f, fq); res[nom] = (ult - paye).sum() / 1e6
res["réel"] = (V[:, -1] - paye).sum() / 1e6
print(round(queue, 4), {k: round(float(v), 1) for k, v in res.items()})
```

**Lecture.** Les facteurs vont de {{a6_f0|2}} à {{a6_f8|3}}. Le facteur de queue extrapolé vaut {{a6_queue|3}} (la décroissance des $f_j-1$ est de {{a6_taux|2}} par délai). Les provisions sont de {{a6_sans|1}} M€ sans queue, {{a6_avec|1}} M€ avec la queue extrapolée, pour {{a6_reel|1}} M€ réellement payés ensuite.

```python hide
NUM("a6_f0", f[0]); NUM("a6_f8", f[8]); NUM("a6_queue", queue); NUM("a6_taux", taux)
NUM("a6_sans", res["sans queue"]); NUM("a6_avec", res["queue extrapolée"]); NUM("a6_reel", res["réel"])
```

**Pour aller plus loin.** Recommencez avec `facteur_queue(f, depuis=6)` : de combien la provision bouge-t-elle ? Que conclure sur le choix de la queue ?

### Application 2.7 — Déviance et crédibilité (section 2.4)

**Objectif.** Tester l'apport d'une variable par le rapport de vraisemblance, puis estimer une crédibilité de Bühlmann–Straub sur des cellules tarifaires.

**Étape 1 — le test de la zone.**

```python
F0 = "nb_sinistres ~ C(classe_age, Treatment('40-49')) + puissance + bonus_malus + C(usage) + C(carburant) + age_vehicule"
m0 = smf.glm(F0, tr, family=sm.families.Poisson(), offset=np.log(tr["exposition"])).fit()
dd = m0.deviance - freq.deviance
print("baisse de déviance :", round(dd, 1), "pour 5 paramètres ; p =", stats.chi2.sf(dd, 5))
```

**Étape 2 — la crédibilité sur 108 cellules** (zone × puissance × usage), estimée sur 2022-2023 et jugée sur 2024.

```python
pol["cellule"] = pol["zone"] + "|" + pol["puissance"].astype(str) + "|" + pol["usage"]
g = pol[pol["annee"] <= 2023].groupby(["cellule", "annee"]).agg(n=("nb_sinistres", "sum"), e=("exposition", "sum")).reset_index()
fr = g.pivot(index="cellule", columns="annee", values="n") / g.pivot(index="cellule", columns="annee", values="e")
w = g.pivot(index="cellule", columns="annee", values="e").fillna(0)
cs = buhlmann_straub(fr.values, w.values)
print({k: round(cs[k], 4) for k in ("mu", "s2", "a", "k")}, "; Z médian", round(np.median(cs["Z"]), 3))
```

**Étape 3 — le jugement sur 2024.**

```python
t24 = pol[pol["annee"] == 2024].groupby("cellule").agg(n=("nb_sinistres", "sum"), e=("exposition", "sum"))
d = pd.DataFrame({"brute": cs["xi"], "crédibilité": cs["Z"] * cs["xi"] + (1 - cs["Z"]) * cs["mu"], "moyenne": cs["mu"]}, index=fr.index).join(t24, how="inner")
print({k: round(deviance_poisson(d["n"], (d[k] * d["e"]).clip(lower=1e-6)), 1) for k in ("brute", "crédibilité", "moyenne")})
```

**Lecture.** Ajouter la zone fait baisser la déviance de {{a7_dd|1}} pour 5 paramètres : le test la retient sans hésitation ($p={{a7_p|sci}}$ environ). Le point de crédibilité est de {{a7_k|int}} années d'exposition ; sur 2024, la déviance des cellules est de {{a7_brute|1}} pour l'expérience brute, {{a7_moy|1}} pour la moyenne et {{a7_cred|1}} pour la crédibilité : la crédibilité est la meilleure des trois.

```python hide
NUM("a7_dd", dd); NUM("a7_p", stats.chi2.sf(dd, 5)); NUM("a7_k", cs["k"])
dv = {k: deviance_poisson(d["n"], (d[k] * d["e"]).clip(lower=1e-6)) for k in ("brute", "crédibilité", "moyenne")}
NUM("a7_brute", dv["brute"]); NUM("a7_moy", dv["moyenne"]); NUM("a7_cred", dv["crédibilité"])
```

### Application 2.8 — Bornhuetter–Ferguson, Mack et bootstrap (section 2.5)

**Objectif.** Appliquer BF et Cape Cod, calculer l'erreur de Mack et simuler le bootstrap sur le triangle de responsabilité civile.

**Étape 1 — BF et Cape Cod.**

```python
prime = tri.groupby("annee_survenance")["prime_acquise"].first().values
ders = [int(np.max(np.where(~np.isnan(Cum[i]))[0])) for i in range(Cum.shape[0])]
pct = np.array([1 / (np.prod(f[d:]) * queue) for d in ders])             # part déjà payée attendue
rho_cc = paye.sum() / (prime * pct).sum()                                # Cape Cod : a priori appris dans les données
bf = bornhuetter_ferguson(Cum, f, prime, 0.80, queue); cc = bornhuetter_ferguson(Cum, f, prime, rho_cc, queue)
print("a priori Cape Cod :", round(rho_cc, 3), "; provisions BF / CC (M€) :", round((bf - paye).sum() / 1e6, 1), round((cc - paye).sum() / 1e6, 1))
```

**Étape 2 — l'erreur de Mack.**

```python
mk, se, sig2 = mack(Cum)
print("provision CL :", round(mk["reserve"].sum() / 1e6, 1), "M€ ; erreur-type de Mack :", round(se / 1e6, 2), "M€")
```

**Étape 3 — le bootstrap ODP (500 simulations).**

```python
inc = triangle_cumule(tri, "paiement_incremental").values
sims, centrale, phi = bootstrap_odp(inc, n_boot=500, graine=1)
print("centrale :", round(centrale / 1e6, 1), "; écart-type :", round(sims.std() / 1e6, 2), "; quantile 99,5 % :", round(np.quantile(sims, 0.995) / 1e6, 1))
```

**Lecture.** L'a priori Cape Cod est de {{a8_rho|pc0}} % (le ratio programmé moyen est de l'ordre de {{a8_vrai|pc0}} %) ; BF avec 80 % donne {{a8_bf|1}} M€, Cape Cod {{a8_cc|1}} M€, pour une provision réelle de {{a6_reel|1}} M€. L'erreur de Mack est de {{a8_se|1}} M€ ; le bootstrap donne {{a8_sd|1}} M€ et une provision centrale de {{a8_centrale|1}} M€, **identique** à celle du chain ladder ({{a8_cl|1}} M€).

```python hide
NUM("a8_rho", rho_cc); NUM("a8_vrai", V[:, -1].sum() / prime.sum()); NUM("a8_bf", (bf - paye).sum() / 1e6); NUM("a8_cc", (cc - paye).sum() / 1e6)
NUM("a8_se", se / 1e6); NUM("a8_sd", sims.std() / 1e6); NUM("a8_centrale", centrale / 1e6); NUM("a8_cl", mk["reserve"].sum() / 1e6)
```

### Application 2.9 — Un portefeuille de santé (section 2.6)

**Objectif.** Mesurer la concentration du coût, séparer sélection adverse et aléa moral, et estimer l'effet d'une prime unique.

**Étape 1 — concentration et facteurs.**

```python
sante = pd.read_csv("donnees/sante_assures.csv")
sante["cpe"] = sante["cout_total"] / sante["exposition"]
cs = np.sort(sante["cout_total"].values)[::-1]
print("5 % les plus coûteux :", round(cs[: int(0.05 * len(cs))].sum() / cs.sum(), 3), "du coût")
print(sante.groupby("ald").apply(lambda g: g["cout_total"].sum() / g["exposition"].sum()).round(0).to_dict())
```

**Étape 2 — ajuster l'effet du niveau.**

```python
fo = "cpe ~ age + I(age ** 2) + ald + C(niveau, Treatment('basique')) + C(sexe)"
mg = smf.glm(fo, sante, family=sm.families.Gamma(sm.families.links.Log()), freq_weights=sante["exposition"]).fit()
brut = sante.groupby("niveau").apply(lambda g: g["cout_total"].sum() / g["exposition"].sum())
print("brut premium/basique :", round(brut["premium"] / brut["basique"], 2), "; ajusté :",
      round(float(np.exp(mg.params["C(niveau, Treatment('basique'))[T.premium]"])), 2))
```

**Lecture.** Les 5 % les plus coûteux portent {{a9_top5|pc0}} % du coût ; l'ALD multiplie le coût par {{a9_ald|1}}. Le rapport brut entre « premium » et « basique » est de {{a9_brut|2}}, le rapport ajusté de {{a9_adj|2}} : une partie seulement de l'écart brut vient du comportement ; le reste est de la **sélection**.

```python hide
NUM("a9_top5", cs[: int(0.05 * len(cs))].sum() / cs.sum())
alds = sante.groupby("ald").apply(lambda g: g["cout_total"].sum() / g["exposition"].sum())
NUM("a9_ald", alds[1] / alds[0]); NUM("a9_brut", brut["premium"] / brut["basique"]); NUM("a9_adj", np.exp(mg.params["C(niveau, Treatment('basique'))[T.premium]"]))
```

## Exercices

### Exercice 2.1 ⭐ — Moyenne et variance de la charge (section 2.1.6)

Le nombre annuel de sinistres d'un portefeuille suit une loi de Poisson de moyenne 0,5 par contrat, et un sinistre coûte 1 000 € avec la probabilité 0,7 ou 3 000 € avec la probabilité 0,3. Calculez $E[S]$, $\mathrm{Var}(S)$ et l'écart-type de la charge d'un contrat, puis vérifiez par simulation.

### Exercice 2.2 ⭐⭐ — Estimer une fréquence avec exposition (section 2.1.2)

Quatre contrats ont pour expositions $(1\,;0{,}5\,;0{,}25\,;1)$ et pour nombres de sinistres $(0\,;1\,;0\,;1)$. Calculez l'estimateur $\hat\lambda$ du taux annuel, son erreur-type approchée, et comparez-le à l'estimation « par contrat ». Quel est l'intervalle de confiance exact à 95 % (Garwood) pour le nombre moyen de sinistres, puis pour le taux annuel ?

### Exercice 2.3 ⭐⭐ — Poisson contre binomiale négative (section 2.1.3)

Pour un contrat de moyenne $\mu=0{,}1$ et une sur-dispersion $\alpha=0{,}5$, calculez, sous une loi de Poisson puis sous une binomiale négative de même moyenne, $P(N=0)$ et $P(N=2)$, et le rapport variance sur moyenne. Que concluez-vous sur la prévision des contrats à plusieurs sinistres ?

### Exercice 2.4 ⭐ — De la prime pure au prix (section 2.2.1 et 2.2.4)

Un segment a une fréquence de 8 % et une sévérité moyenne de 2 500 €. Les frais fixes sont de 40 € par contrat, les frais proportionnels (commissions, taxes) de 14 % du prix, la marge de 5 %. Calculez la prime pure, le prix commercial, et le ratio sinistres sur primes attendu. De combien le prix doit-il augmenter si la sévérité augmente de 4 % ?

### Exercice 2.5 ⭐⭐ — Lire des relativités (section 2.2.2)

Un GLM de fréquence a pour coefficients (référence : zone C, 40-49 ans) : constante $-3{,}00$ ; zone F $+0{,}30$ ; 18-24 ans $+0{,}60$ ; usage professionnel $+0{,}10$. Calculez la fréquence d'un conducteur de 20 ans, en zone F, à usage professionnel, puis la même avec une exposition de 0,5 an. Quelle est la relativité de la zone F par rapport à la zone C ? Que devient-elle si l'on prend la zone F comme référence ?

### Exercice 2.6 ⭐⭐⭐ — Un Gini à la main (section 2.2.5)

Six contrats d'exposition 1 ont pour primes prédites $(100,\,200,\,150,\,300,\,250,\,120)$ et pour coûts observés $(0,\,500,\,0,\,400,\,100,\,0)$. Classez-les, tracez la courbe de Lorenz ordonnée, calculez le Gini par la méthode des trapèzes. Comparez à la courbe de la diagonale et commentez.

### Exercice 2.7 ⭐ — Chain ladder sur un petit triangle (section 2.3.3)

Soit le triangle cumulé (en k€) : année 1 : 120, 180, 198 ; année 2 : 130, 195 ; année 3 : 140. Calculez les facteurs $\hat f_0$, $\hat f_1$ puis les ultimes et la provision totale. Refaites le calcul avec la **moyenne simple** des rapports individuels au lieu de la moyenne pondérée. Les résultats diffèrent-ils ?

### Exercice 2.8 ⭐⭐ — Le facteur de queue (section 2.3.4)

Les derniers facteurs d'un triangle sont $\hat f_5=1{,}120$, $\hat f_6=1{,}060$, $\hat f_7=1{,}030$. En supposant que $\hat f_j-1$ décroît géométriquement de raison $r$ estimée sur ces trois valeurs, calculez $r$, puis le facteur de queue (produit infini). Que devient-il si $r$ passe de 0,5 à 0,6 ? Commentez la sensibilité.

### Exercice 2.9 ⭐⭐ — Test du rapport de vraisemblance (section 2.4.1)

Deux modèles emboîtés ont pour déviances 1 250,0 (8 paramètres) et 1 238,5 (11 paramètres) sur le même jeu. Calculez la baisse de déviance, la p-valeur du test, et dites si les trois paramètres supplémentaires sont justifiés. Comparez avec le critère AIC (qui ajoute $2\times$ le nombre de paramètres à la déviance, à une constante près).

### Exercice 2.10 ⭐⭐⭐ — Crédibilité de Bühlmann–Straub (section 2.4.4)

La variance de processus est $s^2=0{,}07$ (pour une fréquence par année d'exposition) et la variance entre groupes $a=0{,}00014$. Calculez $k$. Trois groupes ont pour expositions 100, 600 et 4 000 années, et pour fréquences observées 9 %, 5 % et 6,4 %, la moyenne générale étant 6,6 %. Calculez les facteurs de crédibilité et les estimations. Vérifiez ensuite, numériquement, l'exactitude de la crédibilité dans le modèle Poisson–Gamma ($\alpha=0{,}4$, $\lambda=0{,}066$).

### Exercice 2.11 ⭐ — Bornhuetter–Ferguson et chain ladder (section 2.5.2)

Une année de survenance a déjà payé 20 M€, la part payée attendue est de 40 %, la prime acquise est de 100 M€ et le ratio a priori est de 80 %. Calculez l'ultime par chain ladder, l'ultime par BF, et vérifiez la relation de moyenne pondérée entre les deux.

### Exercice 2.12 ⭐⭐ — La variance de développement de Mack (section 2.5.3)

Trois années ont, au délai 0, des cumuls $(100,\,120,\,110)$ et au délai 1 des cumuls $(160,\,170,\,180)$. Calculez $\hat f_0$, les rapports individuels, puis $\hat\sigma_0^2=\frac{1}{n-1}\sum_iC_{i,0}(r_i-\hat f_0)^2$. Comment ce paramètre intervient-il dans l'erreur d'une provision ?

### Exercice 2.13 ⭐⭐⭐ — Diagnostiquer un choc calendaire (section 2.5.5)

Reprenez le diagnostic des résidus de Pearson par année calendaire **sur le triangle `triangle_dommages.csv`** (qui n'a pas de choc) puis sur `triangle_choc.csv`. Comparez la plus grande moyenne de diagonale. Le diagnostic est-il utilisable sur un triangle court de six délais ?

### Exercice 2.14 ⭐⭐ — Sélection et comportement en santé (section 2.6.3)

Dans le niveau « basique », 10 % des assurés ont une ALD (coût annuel moyen 3 000 €) et 90 % n'en ont pas (900 €). Dans le niveau « premium », 36 % ont une ALD et 64 % n'en ont pas, et la garantie premium augmente de 40 % la consommation de tous. Calculez le coût moyen de chaque niveau, le rapport brut, puis décomposez-le en un effet de **sélection** (composition) et un effet de **comportement** (+40 %).

## Corrigés

### Corrigé 2.1

$E[X]=0{,}7\times1\,000+0{,}3\times3\,000=1\,600$ €, $E[X^2]=0{,}7\times10^6+0{,}3\times9\times10^6=3{,}4\times10^6$. Pour un Poisson de moyenne $\lambda=0{,}5$, $E[S]=\lambda E[X]=800$ € et $\mathrm{Var}(S)=\lambda E[X^2]=1{,}7\times10^6$, soit un écart-type de {{c1_sd|int}} €. La simulation de 1 000 000 de contrats le confirme.

```python
rng = np.random.default_rng(0)
n = rng.poisson(0.5, 1_000_000)
tot = np.zeros(len(n)); k = n.max()
for j in range(1, k + 1):
    tot += np.where(n >= j, rng.choice([1000, 3000], len(n), p=[0.7, 0.3]), 0)
print(tot.mean().round(1), tot.std().round(1))
```

```python hide
NUM("c1_sd", np.sqrt(0.5 * 3.4e6)); NUM("c1_moy_sim", tot.mean()); NUM("c1_sd_sim", tot.std())
```

La moyenne simulée est de {{c1_moy_sim|1}} € et l'écart-type de {{c1_sd_sim|1}} €, en accord avec la théorie.

### Corrigé 2.2

$\hat\lambda=\sum N_i/\sum e_i=2/2{,}75={{c2_lam|3}}$ par an. L'erreur-type est $\sqrt{\hat\lambda/\sum e_i}=\sqrt{0{,}727/2{,}75}={{c2_se|3}}$ : l'incertitude est énorme avec deux sinistres seulement. L'estimation « par contrat » donne $2/4=0{,}5$ : elle sous-estime de {{c2_biais|pc0}} %, parce que deux contrats ne sont pas des années entières. L'intervalle exact de Garwood à 95 % pour 2 sinistres observés va de {{c2_ic_bas|2}} à {{c2_ic_haut|2}} sinistres, soit, par année d'exposition, de {{c2_ic_bas_t|2}} à {{c2_ic_haut_t|2}} : un facteur de près de 30 entre les deux bornes.

```python
N, E = 2, 2.75
bas, haut = stats.chi2.ppf(0.025, 2 * N) / 2, stats.chi2.ppf(0.975, 2 * N + 2) / 2
print(round(N / E, 3), round(np.sqrt(N / E / E), 3), round(bas, 2), round(haut, 2))
```

```python hide
bas2, haut2 = stats.chi2.ppf(0.025, 4) / 2, stats.chi2.ppf(0.975, 6) / 2
NUM("c2_lam", 2 / 2.75); NUM("c2_se", np.sqrt(2 / 2.75 / 2.75)); NUM("c2_biais", 1 - 0.5 / (2 / 2.75))
NUM("c2_ic_bas", bas2); NUM("c2_ic_haut", haut2); NUM("c2_ic_bas_t", bas2 / 2.75); NUM("c2_ic_haut_t", haut2 / 2.75)
```

### Corrigé 2.3

Avec $r=1/\alpha=2$ et $p=r/(r+\mu)=2/2{,}1$, la binomiale négative donne $P(N=0)=p^r=(2/2{,}1)^2={{c3_nb0|4}}$ ; la loi de Poisson, $e^{-0{,}1}={{c3_p0|4}}$ : les zéros sont presque identiques. Pour $N=2$ : binomiale négative $\frac{\Gamma(4)}{2!\,\Gamma(2)}p^2(1-p)^2={{c3_nb2|5}}$ ; Poisson $\frac{0{,}1^2}{2}e^{-0{,}1}={{c3_p2|5}}$, soit {{c3_rap|1}} fois moins. Le rapport variance sur moyenne est $1+\alpha\mu=1{,}05$. **Poisson sous-estime nettement les contrats à plusieurs sinistres**, bien que les zéros soient presque identiques : la différence est dans la queue.

```python
mu, alpha = 0.1, 0.5; r = 1 / alpha
print(stats.nbinom.pmf([0, 2], r, r / (r + mu)).round(5), stats.poisson.pmf([0, 2], mu).round(5))
```

```python hide
nb = stats.nbinom.pmf([0, 2], r, r / (r + mu)); po = stats.poisson.pmf([0, 2], mu)
NUM("c3_nb0", nb[0]); NUM("c3_p0", po[0]); NUM("c3_nb2", nb[1]); NUM("c3_p2", po[1]); NUM("c3_rap", nb[1] / po[1])
```

### Corrigé 2.4

Prime pure : $\pi=0{,}08\times2\,500=200$ €. Prix : $P=(\pi+F)/(1-\tau-m)=(200+40)/(1-0{,}14-0{,}05)=240/0{,}81={{c4_prix|1}}$ €. Ratio sinistres sur primes attendu : $200/{{c4_prix|1}}={{c4_sp|pc1}}$ %. Si la sévérité augmente de 4 %, $\pi'=208$ et $P'=248/0{,}81={{c4_prix2|1}}$ €, soit {{c4_hausse|pc1}} % de hausse : **moins de 4 %**, parce que les frais fixes (40 €) n'augmentent pas avec la sévérité.

```python hide
pi_ = 0.08 * 2500; P = (pi_ + 40) / 0.81; P2 = (pi_ * 1.04 + 40) / 0.81
NUM("c4_prix", P); NUM("c4_sp", pi_ / P); NUM("c4_prix2", P2); NUM("c4_hausse", P2 / P - 1)
```

### Corrigé 2.5

Conducteur de 20 ans, zone F, professionnel : $\ln\lambda=-3{,}00+0{,}30+0{,}60+0{,}10=-2{,}00$, soit $\lambda=e^{-2}={{c5_lam|4}}$ sinistre par an ; avec une exposition de 0,5 an, $\mu=0{,}5\lambda={{c5_mu|4}}$ (on ajoute $\ln 0{,}5$ au prédicteur). La relativité de la zone F par rapport à C est $e^{0{,}30}={{c5_rel|3}}$. Avec F pour référence, la relativité de C devient $e^{-0{,}30}={{c5_inv|3}}$ ($=1/{{c5_rel|3}}$) : **changer de référence inverse la relativité** mais ne change aucune prime. Les valeurs de la constante changent aussi : la constante est la fréquence de la modalité de référence.

```python hide
NUM("c5_lam", np.exp(-2.0)); NUM("c5_mu", 0.5 * np.exp(-2.0)); NUM("c5_rel", np.exp(0.3)); NUM("c5_inv", np.exp(-0.3))
```

### Corrigé 2.6

On classe par prime croissante : 100 (coût 0), 120 (0), 150 (0), 200 (500), 250 (100), 300 (400). Le coût total est de 1 000 ; les parts cumulées de coût après chaque contrat sont 0, 0, 0, 0,5, 0,6, 1,0 pour des parts cumulées d'exposition de 1/6, 2/6, …, 1. L'aire sous la courbe par trapèzes vaut $\frac16\bigl[\tfrac{0+0}{2}+\tfrac{0+0}{2}+\tfrac{0+0}{2}+\tfrac{0+0{,}5}{2}+\tfrac{0{,}5+0{,}6}{2}+\tfrac{0{,}6+1}{2}\bigr]=\frac16(0{,}25+0{,}55+0{,}8)={{c6_aire|4}}$. Le Gini est $1-2\times{{c6_aire|4}}={{c6_gini|3}}$ : la courbe est nettement sous la diagonale (aire 0,5 pour un tarif aveugle), car les trois contrats les moins chers n'ont rien coûté. Avec six contrats le chiffre est très bruité.

```python
prime = np.array([100, 200, 150, 300, 250, 120.]); cout = np.array([0, 500, 0, 400, 100, 0.])
print(round(lorenz_gini(prime, cout, np.ones(6))[2], 3))
```

```python hide
NUM("c6_aire", (0.25 + 0.55 + 0.8) / 6); NUM("c6_gini", 1 - 2 * (0.25 + 0.55 + 0.8) / 6); NUM("c6_verif", lorenz_gini(prime, cout, np.ones(6))[2])
```

Le code redonne {{c6_verif|3}}.

### Corrigé 2.7

Moyenne pondérée : $\hat f_0=(180+195)/(120+130)=1{,}5$ ; $\hat f_1=198/180=1{,}1$. Ultimes : année 1 = 198 ; année 2 = $195\times1{,}1=214{,}5$ ; année 3 = $140\times1{,}5\times1{,}1=231$. Provision : $0+19{,}5+91={{c7_res|1}}$ k€. Avec la **moyenne simple** : rapports individuels du délai 0 : $180/120=1{,}5$ et $195/130=1{,}5$ ; leur moyenne vaut 1,5 aussi ; pour le délai 1, un seul rapport, $1{,}1$. Les résultats sont **identiques** parce que les deux rapports individuels du délai 0 sont égaux (les deux moyennes ne diffèrent que si les rapports diffèrent). Sur le triangle du livre, où ils diffèrent, la moyenne pondérée donne plus de poids aux grandes années.

```python
Ct = np.array([[120, 180, 198], [130, 195, np.nan], [140, np.nan, np.nan]])
f = facteurs_chain_ladder(Ct); _, u = projeter(Ct, f); print(f.round(3), (u - dernier_cumul(Ct)).sum())
```

```python hide
NUM("c7_res", (u - dernier_cumul(Ct)).sum())
```

### Corrigé 2.8

Les écarts à 1 sont $0{,}120$, $0{,}060$, $0{,}030$ : les rapports successifs valent $0{,}5$ et $0{,}5$, donc $r=0{,}5$. Le facteur de queue est $\prod_{k\ge1}\bigl(1+0{,}030\,r^{k}\bigr)\approx\exp\bigl(\sum_k0{,}030\,r^k\bigr)=\exp\bigl(0{,}030\,r/(1-r)\bigr)$ ; pour $r=0{,}5$, $\exp(0{,}030)={{c8_t5|4}}$ (valeur exacte du produit : {{c8_t5e|4}}). Pour $r=0{,}6$, $\exp(0{,}030\times1{,}5)={{c8_t6|4}}$ (exact : {{c8_t6e|4}}). **Passer de 0,5 à 0,6 déplace le facteur de queue de {{c8_diff|pc1}} point, soit environ {{c8_prov|int}} M€ sur une provision d'ultimes de 650 M€** : la queue est à la fois petite et déterminante.

```python hide
def q_(r, e0=0.03, n=200): return float(np.prod(1 + e0 * r ** np.arange(1, n)))
NUM("c8_t5", np.exp(0.03 * 0.5 / 0.5)); NUM("c8_t6", np.exp(0.03 * 0.6 / 0.4)); NUM("c8_t5e", q_(0.5)); NUM("c8_t6e", q_(0.6))
NUM("c8_diff", q_(0.6) - q_(0.5)); NUM("c8_prov", (q_(0.6) - q_(0.5)) * 650)
```

### Corrigé 2.9

Baisse de déviance : $1\,250{,}0-1\,238{,}5=11{,}5$ pour 3 paramètres. $P(\chi^2_3>11{,}5)={{c9_p|sci}}$ : **on rejette** le modèle simple au seuil de 1 %, les trois paramètres sont justifiés. L'AIC augmente de $2\times3=6$ pour la pénalité et baisse de 11,5 pour la déviance : le gain net est de $11{,}5-6=5{,}5$ en faveur du grand modèle. Les deux critères concluent dans le même sens ; si la baisse avait été de 5 par exemple, l'AIC aurait préféré le petit modèle (gain net $-1$) et le test, avec $p\approx0{,}17$, n'aurait pas rejeté non plus : les deux critères se rejoignent presque toujours, mais pas par construction.

```python hide
NUM("c9_p", stats.chi2.sf(11.5, 3))
```

### Corrigé 2.10

$k=s^2/a=0{,}07/0{,}00014={{c10_k|int}}$ années. Facteurs : $Z_1=100/600={{c10_z1|3}}$, $Z_2=600/1\,100={{c10_z2|3}}$, $Z_3=4\,000/4\,500={{c10_z3|3}}$. Estimations : $0{,}167\times9+0{,}833\times6{,}6={{c10_e1|2}}$ %, $0{,}545\times5+0{,}455\times6{,}6={{c10_e2|2}}$ %, $0{,}889\times6{,}4+0{,}111\times6{,}6={{c10_e3|2}}$ %. Le petit groupe est ramené presque au niveau de la moyenne (de 9 % à {{c10_e1|1}} %), le gros est quasiment cru. Pour l'exactitude Poisson–Gamma, $k=1/(\alpha\lambda)={{c10_kpg|1}}$ ; vérifions que $Z\,(N/e)+(1-Z)\lambda=\lambda(r+N)/(r+\lambda e)$ pour $e=100$ et $N=9$ ($r=1/\alpha=2{,}5$) : les deux membres valent {{c10_pg|4}} (écart de {{c10_ecart|sci}}).

```python
r, lam, e, N = 2.5, 0.066, 100, 9
k = r / lam; Z = e / (e + k)
print(round(Z * N / e + (1 - Z) * lam, 5), round(lam * (r + N) / (r + lam * e), 5))
```

```python hide
k10 = 0.07 / 0.00014; zs = [100 / (100 + k10), 600 / (600 + k10), 4000 / (4000 + k10)]
NUM("c10_k", k10); NUM("c10_z1", zs[0]); NUM("c10_z2", zs[1]); NUM("c10_z3", zs[2])
for i, (obs, cle) in enumerate(((9, "c10_e1"), (5, "c10_e2"), (6.4, "c10_e3"))): NUM(cle, zs[i] * obs + (1 - zs[i]) * 6.6)
NUM("c10_kpg", 1 / (0.4 * 0.066))
a_ = Z * N / e + (1 - Z) * lam; b_ = lam * (r + N) / (r + lam * e)
NUM("c10_pg", a_); NUM("c10_ecart", abs(a_ - b_) + 1e-15)
```

### Corrigé 2.11

Chain ladder : ultime $=20/0{,}4={{c11_cl|1}}$ M€. BF : $20+100\times0{,}8\times(1-0{,}4)={{c11_bf|1}}$ M€. Relation : $\hat p\,\hat U^{\text{CL}}+(1-\hat p)P\rho=0{,}4\times50+0{,}6\times80={{c11_mix|1}}$ M€, identique à BF. BF est **plus proche de l'a priori** (80) que de l'extrapolation (50) parce que l'année n'est payée qu'à 40 % : on fait confiance à l'information a priori pour les 60 % restants.

```python hide
NUM("c11_cl", 20 / 0.4); NUM("c11_bf", 20 + 100 * 0.8 * 0.6); NUM("c11_mix", 0.4 * 50 + 0.6 * 80)
```

### Corrigé 2.12

$\hat f_0=(160+170+180)/(100+120+110)=510/330={{c12_f|4}}$. Rapports individuels : $1{,}6$ ; $1{,}4167$ ; $1{,}6364$. Écarts à $\hat f_0$ : {{c12_e1|4}}, {{c12_e2|4}}, {{c12_e3|4}}. $\hat\sigma_0^2=\frac12\bigl[100\,e_1^2+120\,e_2^2+110\,e_3^2\bigr]={{c12_s2|3}}$. Ce paramètre mesure la **variabilité résiduelle** des rapports de développement autour de $\hat f_0$ : il entre dans la variance de processus ($\hat\sigma_0^2/(\hat f_0^2\hat C_{i,0})$) et dans la variance d'estimation ($\hat\sigma_0^2/(\hat f_0^2\sum_jC_{j,0})$) de la formule de Mack, pour toutes les années qui doivent encore traverser ce délai.

```python hide
c0 = np.array([100, 120, 110.]); c1 = np.array([160, 170, 180.])
f0 = c1.sum() / c0.sum(); r_ = c1 / c0; es = r_ - f0
s2 = np.sum(c0 * es ** 2) / 2
NUM("c12_f", f0); NUM("c12_e1", es[0]); NUM("c12_e2", es[1]); NUM("c12_e3", es[2]); NUM("c12_s2", s2)
```

### Corrigé 2.13

Le diagnostic se programme en quelques lignes : on ajuste le GLM de Poisson à effets ligne et colonne, on calcule les résidus de Pearson standardisés, on les moyenne par année calendaire $i+j$.

```python
def residus_diag(I):
    n, m = I.shape; ii, jj = np.indices((n, m)); obs = ~np.isnan(I)
    X = np.zeros((obs.sum(), n + m - 1)); X[np.arange(obs.sum()), ii[obs]] = 1
    mc = jj[obs] > 0; X[np.arange(obs.sum())[mc], n + jj[obs][mc] - 1] = 1
    y = I[obs]; mod = sm.GLM(y, X, family=sm.families.Poisson()).fit(); mu = mod.fittedvalues
    phi = np.sum((y - mu) ** 2 / mu) / (len(y) - len(mod.params))
    r = (y - mu) / np.sqrt(phi * mu); d = (ii + jj)[obs]
    return pd.Series(r).groupby(d).mean()
for nom in ("dommages", "choc"):
    t_ = pd.read_csv(f"donnees/triangle_{nom}.csv")
    rd = residus_diag(triangle_cumule(t_, "paiement_incremental").values)
    print(nom, rd.round(2).to_dict())
```

```python hide
rd_d = residus_diag(triangle_cumule(pd.read_csv("donnees/triangle_dommages.csv"), "paiement_incremental").values)
rd_c = residus_diag(triangle_cumule(pd.read_csv("donnees/triangle_choc.csv"), "paiement_incremental").values)
NUM("c13_d_max", rd_d.iloc[1:].abs().max()); NUM("c13_c_max", rd_c.iloc[1:].abs().max()); NUM("c13_c_arg", int(rd_c.iloc[1:].abs().idxmax()))
NUM("c13_c_7", rd_c.loc[7])
```

Sur le triangle de dommages, la plus grande moyenne de diagonale en valeur absolue est de {{c13_d_max|2}} ; sur le triangle « choc », elle atteint {{c13_c_max|2}} (diagonale {{c13_c_arg|int}}, celle du choc). Le diagnostic **fonctionne**, mais sur un triangle de six délais les diagonales les plus courtes ne contiennent que quelques cellules et leurs moyennes sont bruitées : on ne regarde que les diagonales qui ont assez de cellules, et l'on s'appuie aussi sur des graphiques de résidus (livre, section 2.5.5).

### Corrigé 2.14

Coût moyen en basique : $0{,}10\times3\,000+0{,}90\times900=1\,110$ €. En premium : les coûts de consommation sont majorés de 40 % : $1{,}4\times(0{,}36\times3\,000+0{,}64\times900)=1{,}4\times1\,656={{c14_prem|1}}$ €. Rapport brut : ${{c14_prem|1}}/1\,110={{c14_brut|2}}$. **Sélection** : le coût des assurés premium s'ils avaient le comportement basique, comparé au coût des assurés basique : $1\,656/1\,110={{c14_sel|3}}$. **Comportement** : $1{,}4$. Et ${{c14_sel|3}}\times1{,}4={{c14_brut|2}}$, la décomposition multiplicative du livre. Environ {{c14_part_sel|pc0}} % du log de l'écart brut vient de la sélection et {{c14_part_comp|pc0}} % du comportement : **tarifer sur le rapport brut reviendrait à faire payer à tous un comportement qui, en partie, est une différence de santé.**

```python hide
bas = 0.10 * 3000 + 0.90 * 900; prem = 0.36 * 3000 + 0.64 * 900
NUM("c14_prem", 1.4 * prem); NUM("c14_brut", 1.4 * prem / bas); NUM("c14_sel", prem / bas)
NUM("c14_part_sel", np.log(prem / bas) / np.log(1.4 * prem / bas)); NUM("c14_part_comp", np.log(1.4) / np.log(1.4 * prem / bas))
```
