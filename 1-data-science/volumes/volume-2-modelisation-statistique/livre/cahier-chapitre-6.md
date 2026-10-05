# Chapitre 6 : Statistique bayésienne et simulation — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 6 du livre. Il contient six **applications** guidées (une par section du livre) et quatorze **exercices** corrigés. Les données sont celles du volume : `donnees/clients.csv` (2 000 clients simulés) ; certaines applications simulent leurs propres données avec une graine fixe. Prérequis : avoir lu la section correspondante du livre.

## Applications

### Préparation (à exécuter d'abord)

Toutes les applications et les corrigés partagent les outils ci-dessous : imports, données, et quatre petites fonctions (marche aléatoire de Metropolis en dimension 1 et en dimension quelconque, taille d'échantillon effective, $\widehat R$ découpé). Les algorithmes sont expliqués dans les sections 6.3 et 6.4 du livre.

```python
import numpy as np
import pandas as pd
from scipy import stats

clients = pd.read_csv("donnees/clients.csv")
print(clients.shape, "| canaux :", sorted(clients["canal_acquisition"].unique()))
```
<!--sortie-->
```text
(2000, 12) | canaux : ['Boutique', 'Réseaux', 'Site']
```

```python
def metropolis_1d(logp, x0, n, pas, rng):
    """Marche aléatoire de Metropolis en dimension 1 : proposition x' = x + pas * N(0, 1)."""
    x, lp = x0, logp(x0)
    chaine, acceptes = np.empty(n), 0
    for i in range(n):
        prop = x + pas * rng.standard_normal()
        lpp = logp(prop)
        if np.log(rng.random()) < lpp - lp:               # critère d'acceptation, en logarithmes
            x, lp = prop, lpp
            acceptes += 1
        chaine[i] = x                                     # on recompte la valeur même si on a refusé
    return chaine, acceptes / n

def metropolis_multi(logp, x0, n, cov_prop, rng):
    """Même algorithme en dimension quelconque : proposition gaussienne de covariance cov_prop."""
    L = np.linalg.cholesky(cov_prop)
    x, lp = x0.copy(), logp(x0)
    chaine, acceptes = np.empty((n, len(x0))), 0
    for i in range(n):
        prop = x + L @ rng.standard_normal(len(x0))
        lpp = logp(prop)
        if np.log(rng.random()) < lpp - lp:
            x, lp = prop, lpp
            acceptes += 1
        chaine[i] = x
    return chaine, acceptes / n
```

```python
def autocorr(x, max_lag):
    x = np.asarray(x, dtype=float) - np.mean(x)
    n = len(x)
    f = np.fft.rfft(x, 2 * n)                               # transformée de Fourier avec remplissage de zéros
    ac = np.fft.irfft(f * np.conj(f))[:n]
    return (ac / ac[0])[: max_lag + 1]

def ess(x):
    """Taille d'échantillon effective ; la somme des autocorrélations s'arrête à la première négative."""
    rho = autocorr(x, max_lag=min(len(x) // 2, 1000))
    somme = 0.0
    for r in rho[1:]:
        if r < 0:
            break
        somme += r
    return len(x) / (1 + 2 * somme)

def split_rhat(ch):
    """ch : tableau (m chaînes, n itérations). Split-R-chapeau de Gelman-Rubin."""
    m, n = ch.shape
    parts = np.concatenate([ch[:, : n // 2], ch[:, n // 2 : 2 * (n // 2)]], axis=0)   # 2m chaînes de longueur n/2
    N = parts.shape[1]
    W = parts.var(axis=1, ddof=1).mean()
    B = N * parts.mean(axis=1).var(ddof=1)
    return np.sqrt(((N - 1) / N * W + B / N) / W)
```

### Application 6.1 — L'offre de bienvenue fonctionne-t-elle ? (section 6.1)

**Objectif.** Quantifier, avec des lois a posteriori, l'effet de l'offre de bienvenue (attribuée au hasard) sur le rachat à 12 mois, puis tester la solidité de la conclusion (a priori différents) et faire une prédiction.

**Étape 1 — les effectifs.** Combien de clients et de rachats dans chaque groupe ?

```python
bilan = clients.groupby("offre_bienvenue")["rachat_12m"].agg(clients="size", rachats="sum")
bilan["frequence"] = (bilan["rachats"] / bilan["clients"]).round(4)
print(bilan)
```
<!--sortie-->
```text
                 clients  rachats  frequence
offre_bienvenue                             
0                    985      441     0.4477
1                   1015      578     0.5695
```

**Étape 2 — une loi a posteriori par groupe.** Avec un a priori $\mathrm{Beta}(1,1)$, chaque groupe a pour a posteriori $\mathrm{Beta}(1+y,\,1+n-y)$.

```python
post = {}
for groupe, ligne in bilan.iterrows():
    a_post = 1 + ligne["rachats"]
    b_post = 1 + ligne["clients"] - ligne["rachats"]
    post[groupe] = stats.beta(a_post, b_post)
    bas, haut = post[groupe].ppf([0.025, 0.975])
    print(f"offre = {groupe} : Beta({a_post:.0f}, {b_post:.0f}) | moyenne {post[groupe].mean():.4f} | "
          f"IC de crédibilité à 95 % : [{bas:.4f} ; {haut:.4f}]")
```
<!--sortie-->
```text
offre = 0 : Beta(442, 545) | moyenne 0.4478 | IC de crédibilité à 95 % : [0.4169 ; 0.4789]
offre = 1 : Beta(579, 438) | moyenne 0.5693 | IC de crédibilité à 95 % : [0.5388 ; 0.5996]
```

**Étape 3 — la loi de la différence.** On tire dans les deux lois et on soustrait.

```python
rng = np.random.default_rng(61)
S = 200_000
theta1 = post[1].rvs(S, random_state=rng)
theta0 = post[0].rvs(S, random_state=rng)
delta = theta1 - theta0
print(f"moyenne de la différence       : {delta.mean():.4f}")
print(f"IC de crédibilité à 95 %       : [{np.percentile(delta, 2.5):.4f} ; {np.percentile(delta, 97.5):.4f}]")
print(f"P(l'offre augmente le rachat)  : {(delta > 0).mean():.5f}")
print(f"P(l'effet dépasse 5 points)    : {(delta > 0.05).mean():.4f}")
print(f"P(l'effet dépasse 10 points)   : {(delta > 0.10).mean():.4f}")
```
<!--sortie-->
```text
moyenne de la différence       : 0.1214
IC de crédibilité à 95 %       : [0.0778 ; 0.1647]
P(l'offre augmente le rachat)  : 1.00000
P(l'effet dépasse 5 points)    : 0.9993
P(l'effet dépasse 10 points)   : 0.8346
```

*Lecture.* Aucun des 200 000 tirages ne donne une différence négative : l'offre augmente presque certainement le rachat, d'environ 12 points (entre 8 et 16 avec 95 % de probabilité). La probabilité que l'effet dépasse 10 points est de 83 %.

**Étape 4 — intervalle à queues égales ou HPD ?** Pour une loi asymétrique (un nouveau canal testé auprès de 20 clients, un seul rachat), les deux intervalles diffèrent.

```python
def hpd(loi, masse=0.95, pas=2000):
    """Plus court intervalle de probabilité `masse` : on fait glisser une fenêtre de quantiles."""
    bas = np.linspace(0, 1 - masse, pas)
    largeurs = loi.ppf(bas + masse) - loi.ppf(bas)
    i = largeurs.argmin()
    return loi.ppf(bas[i]), loi.ppf(bas[i] + masse)

asym = stats.beta(1 + 1, 1 + 19)
print("Beta(2, 20)  moyenne :", round(asym.mean(), 4))
print("à queues égales : [%.4f ; %.4f]  largeur %.4f" % (*asym.ppf([0.025, 0.975]), np.diff(asym.ppf([0.025, 0.975]))[0]))
h = hpd(asym)
print("HPD             : [%.4f ; %.4f]  largeur %.4f" % (*h, h[1] - h[0]))
```
<!--sortie-->
```text
Beta(2, 20)  moyenne : 0.0909
à queues égales : [0.0117 ; 0.2382]  largeur 0.2264
HPD             : [0.0026 ; 0.2080]  largeur 0.2054
```

**Étape 5 — sensibilité à l'a priori.** Refaites le calcul pour quatre a priori et trois tailles d'échantillon.

```python
avec_offre = clients.loc[clients["offre_bienvenue"] == 1, "rachat_12m"].to_numpy()
priors = {"Uniforme Beta(1,1)": (1, 1), "Jeffreys Beta(.5,.5)": (0.5, 0.5),
          "Informatif Beta(20,20)": (20, 20), "Informatif faux Beta(2,18)": (2, 18)}
lignes = []
for n in (10, 100, len(avec_offre)):
    y = avec_offre[:n].sum()
    for nom, (a, b) in priors.items():
        loi = stats.beta(a + y, b + n - y)
        bas, haut = loi.ppf([0.025, 0.975])
        lignes.append({"n": n, "a priori": nom, "moyenne": round(loi.mean(), 3), "IC95": f"[{bas:.3f} ; {haut:.3f}]"})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
   n                   a priori  moyenne            IC95
  10         Uniforme Beta(1,1)    0.333 [0.109 ; 0.610]
  10       Jeffreys Beta(.5,.5)    0.318 [0.093 ; 0.606]
  10     Informatif Beta(20,20)    0.460 [0.325 ; 0.598]
  10 Informatif faux Beta(2,18)    0.167 [0.058 ; 0.317]
 100         Uniforme Beta(1,1)    0.549 [0.452 ; 0.644]
 100       Jeffreys Beta(.5,.5)    0.550 [0.452 ; 0.645]
 100     Informatif Beta(20,20)    0.536 [0.453 ; 0.617]
 100 Informatif faux Beta(2,18)    0.475 [0.387 ; 0.564]
1015         Uniforme Beta(1,1)    0.569 [0.539 ; 0.600]
1015       Jeffreys Beta(.5,.5)    0.569 [0.539 ; 0.600]
1015     Informatif Beta(20,20)    0.567 [0.537 ; 0.597]
1015 Informatif faux Beta(2,18)    0.560 [0.530 ; 0.590]
```

*Lecture.* Avec $n=10$ les quatre a priori donnent des réponses très différentes (l'a priori faux ramène la moyenne à 0,167) ; avec $n=1\,015$ elles sont toutes comprises entre 0,560 et 0,569.

**Étape 6 — la loi prédictive.** Sur 100 nouveaux clients avec offre, combien rachèteront ? Comparez le plug-in, la loi bêta-binomiale exacte et la simulation.

```python
n_nouv = 100
plug = stats.binom(n_nouv, avec_offre.mean())
pred = stats.betabinom(n_nouv, post[1].args[0], post[1].args[1])
for nom, loi in (("plug-in  Bin(100, θ̂)", plug), ("prédictive bêta-binomiale", pred)):
    print(f"{nom:28s} moyenne {loi.mean():6.2f} | écart-type {loi.std():5.2f} | "
          f"intervalle à 95 % [{loi.ppf(0.025):.0f} ; {loi.ppf(0.975):.0f}]")
rng = np.random.default_rng(63)
theta_s = post[1].rvs(100_000, random_state=rng)
y_s = rng.binomial(n_nouv, theta_s)
print(f"simulation : moyenne {y_s.mean():.2f}, écart-type {y_s.std():.2f}, "
      f"intervalle à 95 % [{np.percentile(y_s, 2.5):.0f} ; {np.percentile(y_s, 97.5):.0f}]")
```
<!--sortie-->
```text
plug-in  Bin(100, θ̂)        moyenne  56.95 | écart-type  4.95 | intervalle à 95 % [47 ; 67]
prédictive bêta-binomiale    moyenne  56.93 | écart-type  5.19 | intervalle à 95 % [47 ; 67]
simulation : moyenne 56.94, écart-type 5.20, intervalle à 95 % [47 ; 67]
```

**Pour aller plus loin — la couverture.** Un intervalle de crédibilité à 95 % couvre-t-il la vraie valeur dans 95 % des échantillons ? Simulez 20 000 échantillons de taille 30 pour quatre vraies valeurs de $\theta$ et comparez Wald, Wilson et crédibilité.

```python
from statsmodels.stats.proportion import proportion_confint

def couverture(theta_vrai, n=30, reps=20_000, graine=62):
    rng = np.random.default_rng(graine)
    y = rng.binomial(n, theta_vrai, reps)
    res = {}
    for methode in ("normal", "wilson"):
        bas, haut = proportion_confint(y, n, alpha=0.05, method=methode)
        res[methode] = np.mean((bas <= theta_vrai) & (theta_vrai <= haut))
    loi = stats.beta(1 + y, 1 + n - y)
    res["crédibilité"] = np.mean((loi.ppf(0.025) <= theta_vrai) & (theta_vrai <= loi.ppf(0.975)))
    return res

print(pd.DataFrame([{"vrai θ": th, **{k: round(v, 3) for k, v in couverture(th).items()}} for th in (0.05, 0.10, 0.30, 0.50)]).to_string(index=False))
```
<!--sortie-->
```text
 vrai θ  normal  wilson  crédibilité
   0.05   0.781   0.940        0.940
   0.10   0.806   0.974        0.974
   0.30   0.954   0.930        0.930
   0.50   0.958   0.958        0.958
```

### Application 6.2 — Faut-il envoyer l'offre à tout le monde ? (section 6.2)

**Objectif.** Propager toute l'incertitude (deux taux de rachat, une marge) jusqu'à une décision, par Monte-Carlo. Hypothèses (inventées, à remplacer par les vraies valeurs) : marge de 30 % du panier, coût de l'offre de 1,50 € par client, un client qui rachète génère un panier tiré parmi les paniers observés.

**Étape 1 — les ingrédients.**

```python
resume = clients.groupby("offre_bienvenue")["rachat_12m"].agg(["size", "sum"])
post0 = stats.beta(1 + resume.loc[0, "sum"], 1 + resume.loc[0, "size"] - resume.loc[0, "sum"])
post1 = stats.beta(1 + resume.loc[1, "sum"], 1 + resume.loc[1, "size"] - resume.loc[1, "sum"])
paniers = clients.loc[clients["panier_moyen"] > 0, "panier_moyen"].to_numpy()
marge, cout = 0.30, 1.50
print(f"panier moyen des acheteurs : {paniers.mean():.2f} € ; marge moyenne par rachat : {marge * paniers.mean():.2f} €")
```
<!--sortie-->
```text
panier moyen des acheteurs : 61.23 € ; marge moyenne par rachat : 18.37 €
```

**Étape 2 — des scénarios.** Dans chacun des 100 000 scénarios, on tire les deux taux et une marge moyenne (bootstrap), puis on calcule $G=(\theta_1-\theta_0)\,m-c$.

```python
rng = np.random.default_rng(625)
S = 100_000
theta1 = post1.rvs(S, random_state=rng)
theta0 = post0.rvs(S, random_state=rng)
m_boot = marge * np.array([rng.choice(paniers, len(paniers)).mean() for _ in range(S // 20)])
m = rng.choice(m_boot, S)
G = (theta1 - theta0) * m - cout                           # gain net par client, S scénarios
print(f"gain net moyen par client : {G.mean():+.3f} €")
print(f"intervalle à 90 %         : [{np.percentile(G, 5):+.3f} ; {np.percentile(G, 95):+.3f}] €")
print(f"P(l'offre est rentable)   : {(G > 0).mean():.3f}")
print(f"pour 5 000 nouveaux clients : gain attendu {5000 * G.mean():+.0f} € ; "
      f"dans 95 % des scénarios le gain dépasse {5000 * np.percentile(G, 5):+.0f} €")
```
<!--sortie-->
```text
gain net moyen par client : +0.731 €
intervalle à 90 %         : [+0.062 ; +1.400] €
P(l'offre est rentable)   : 0.964
pour 5 000 nouveaux clients : gain attendu +3656 € ; dans 95 % des scénarios le gain dépasse +312 €
```

*Lecture.* L'offre est très probablement rentable (96 %), mais le gain par client reste modeste (0,73 €) et l'intervalle à 90 % s'approche de zéro. **À faire :** refaites le calcul avec un coût de 2 € et une marge de 25 % ; que devient la probabilité de rentabilité ?

**Étape 3 — les méthodes de simulation.** Trois variantes d'un même calcul, pour comparer leur précision.

```python
rng = np.random.default_rng(628)
n, reps = 10_000, 300
naif = np.array([(rng.standard_normal(n) > 4).mean() for _ in range(reps)])
def preferentiel(n, rng):
    x = rng.normal(4, 1, n)                                    # on tire autour de 4
    return np.mean((x > 4) * stats.norm.pdf(x) / stats.norm.pdf(x, loc=4, scale=1))
pref = np.array([preferentiel(n, rng) for _ in range(reps)])
print(f"exact : {stats.norm.sf(4):.3e} | naïf : écart-type {naif.std():.3e} ({(naif == 0).mean():.0%} d'estimations nulles) "
      f"| préférentiel : écart-type {pref.std():.3e}")
```
<!--sortie-->
```text
exact : 3.167e-05 | naïf : écart-type 5.798e-05 (69% d'estimations nulles) | préférentiel : écart-type 6.752e-07
```

### Application 6.3 — La régression logistique bayésienne du rachat (section 6.3)

**Objectif.** Estimer par Metropolis les cinq coefficients d'une régression logistique du rachat (offre, âge standardisé, canaux Réseaux et Site ; Boutique en référence), a priori $\mathcal N(0,2{,}5^2)$.

**Étape 1 — la matrice des variables.**

```python
import statsmodels.api as sm
d = clients.copy()
d["age_c"] = (d["age"] - d["age"].mean()) / d["age"].std()
X = pd.get_dummies(d[["offre_bienvenue", "canal_acquisition", "age_c"]], columns=["canal_acquisition"], drop_first=True, dtype=float)
X = X.rename(columns={"canal_acquisition_Réseaux": "Réseaux", "canal_acquisition_Site": "Site", "offre_bienvenue": "offre"})
X = sm.add_constant(X)
noms = list(X.columns)
Xm, y = X.to_numpy(), d["rachat_12m"].to_numpy()
print("colonnes :", noms, "| n =", len(y), "| rachat moyen :", y.mean().round(3))
```
<!--sortie-->
```text
colonnes : ['const', 'offre', 'age_c', 'Réseaux', 'Site'] | n = 2000 | rachat moyen : 0.509
```

**Étape 2 — le log-posterior** (toute la modélisation) et le maximum de vraisemblance comme point de repère.

```python
def log_post(beta):
    eta = Xm @ beta
    log_vrais = np.sum(y * eta - np.logaddexp(0, eta))     # somme de y*eta - log(1 + exp(eta))
    log_prior = -0.5 * np.sum(beta**2) / 2.5**2            # a priori normal centré, écart-type 2,5
    return log_vrais + log_prior

emv = sm.Logit(y, Xm).fit(disp=0)
print("log-posterior en l'EMV :", round(log_post(emv.params), 2))
```
<!--sortie-->
```text
log-posterior en l'EMV : -1355.46
```

**Étape 3 — quatre chaînes.** Proposition gaussienne de covariance $\frac{2{,}38^2}{d}\hat\Sigma$ ($\hat\Sigma$ : covariance de l'EMV), points de départ dispersés.

```python
dim = len(noms)
cov_prop = (2.38**2 / dim) * emv.cov_params()
rng = np.random.default_rng(633)
chaines, taux = [], []
for c in range(4):
    depart = emv.params + rng.normal(0, 1.0, dim)
    ch, tx = metropolis_multi(log_post, depart, n=6000, cov_prop=cov_prop, rng=rng)
    chaines.append(ch); taux.append(tx)
chaines = np.array(chaines)                                # forme (4 chaînes, 6000 itérations, 5 paramètres)
print("taux d'acceptation :", np.round(taux, 3), "| forme :", chaines.shape)
```
<!--sortie-->
```text
taux d'acceptation : [0.284 0.297 0.293 0.274] | forme : (4, 6000, 5)
```

**Étape 4 — résumé a posteriori** (chauffe de 1 000 itérations écartée), à côté du maximum de vraisemblance.

```python
apres = chaines[:, 1000:, :]
tirages = apres.reshape(-1, dim)
resume = pd.DataFrame({
    "EMV": emv.params, "moyenne post.": tirages.mean(axis=0), "écart-type post.": tirages.std(axis=0),
    "2,5 %": np.percentile(tirages, 2.5, axis=0), "97,5 %": np.percentile(tirages, 97.5, axis=0),
    "ESS": [sum(ess(apres[c, :, j]) for c in range(4)) for j in range(dim)]}, index=noms)
print(resume.round(3).to_string())
```
<!--sortie-->
```text
           EMV  moyenne post.  écart-type post.  2,5 %  97,5 %       ESS
const    0.034          0.033             0.098 -0.162   0.227  1280.705
offre    0.493          0.493             0.089  0.316   0.663  1276.029
age_c   -0.163         -0.163             0.045 -0.256  -0.076  1114.281
Réseaux -0.463         -0.459             0.113 -0.681  -0.232  1158.399
Site    -0.168         -0.163             0.118 -0.393   0.073  1205.256
```

**Étape 5 — tout devient une moyenne.** Rapport de cotes de l'offre et effet sur la probabilité de rachat d'un client de référence (Boutique, âge moyen).

```python
b0, b1 = tirages[:, 0], tirages[:, 1]
rc = np.exp(b1)
print(f"rapport de cotes de l'offre : médiane {np.median(rc):.3f}, IC95 [{np.percentile(rc, 2.5):.3f} ; {np.percentile(rc, 97.5):.3f}]")
print(f"P(rapport de cotes > 1) = {(rc > 1).mean():.4f} | P(rapport de cotes > 1,5) = {(rc > 1.5).mean():.4f}")
sigmoide = lambda u: 1 / (1 + np.exp(-u))
effet = sigmoide(b0 + b1) - sigmoide(b0)
print(f"effet de l'offre sur la probabilité de rachat : {effet.mean():+.3f}  IC95 [{np.percentile(effet, 2.5):+.3f} ; {np.percentile(effet, 97.5):+.3f}]")
brut = clients.groupby("offre_bienvenue")["rachat_12m"].mean()
print(f"rappel : différence brute des fréquences = {brut[1] - brut[0]:+.3f}")
```
<!--sortie-->
```text
rapport de cotes de l'offre : médiane 1.639, IC95 [1.372 ; 1.940]
P(rapport de cotes > 1) = 1.0000 | P(rapport de cotes > 1,5) = 0.8357
effet de l'offre sur la probabilité de rachat : +0.120  IC95 [+0.078 ; +0.161]
rappel : différence brute des fréquences = +0.122
```

**Étape 6 — pourquoi 0,49 et pas 0,55 ?** Le générateur de données utilise un effet de l'offre de 0,55 sur le logit, mais aussi deux facteurs latents que notre modèle ne voit pas. Vérifiez sur un très grand échantillon que l'omission de variables *atténue* le coefficient.

```python
rng = np.random.default_rng(636)
N = 400_000
F1 = rng.normal(size=N)
F2 = 0.3 * F1 + np.sqrt(1 - 0.3**2) * rng.normal(size=N)         # deux facteurs latents corrélés
offre = rng.integers(0, 2, N).astype(float)
eta = -0.35 + 0.45 * F1 + 0.35 * F2 + 0.55 * offre              # vrai modèle : l'offre vaut 0,55
yy = rng.binomial(1, 1 / (1 + np.exp(-eta)))
marginal = sm.Logit(yy, sm.add_constant(offre)).fit(disp=0).params[1]
condit = sm.Logit(yy, sm.add_constant(np.c_[offre, F1, F2])).fit(disp=0).params[1]
print(f"coefficient de l'offre sans les facteurs latents : {marginal:.3f}")
print(f"coefficient de l'offre avec les facteurs latents : {condit:.3f}   (vrai : 0.55)")
```
<!--sortie-->
```text
coefficient de l'offre sans les facteurs latents : 0.499
coefficient de l'offre avec les facteurs latents : 0.548   (vrai : 0.55)
```

### Application 6.4 — Vérifier un modèle : Poisson contre binomiale négative (section 6.4)

**Objectif.** Montrer par une vérification prédictive a posteriori que le modèle de Poisson est faux pour le nombre de commandes annuelles des clients du canal Boutique, le remplacer par une binomiale négative estimée par MCMC, et revérifier. (On réutilise `metropolis_multi`, `ess` et `split_rhat` de la préparation.)

**Étape 1 — le modèle de Poisson et ses répliques.** A posteriori $\mathrm{Gamma}(2+\sum y;\ 0{,}5+n)$ ; trois statistiques-test : variance/moyenne, part de zéros, maximum.

```python
b = clients.loc[clients["canal_acquisition"] == "Boutique", "nb_commandes_an"].to_numpy()
n_b = len(b)

def stats_test(yrep):
    """Trois statistiques sur chaque jeu (lignes) : variance/moyenne, part de zéros, maximum."""
    return np.c_[yrep.var(axis=1, ddof=1) / yrep.mean(axis=1), (yrep == 0).mean(axis=1), yrep.max(axis=1)]

T_obs = stats_test(b[None, :])[0]
noms_T = ["variance / moyenne", "part de zéros", "maximum"]
rng = np.random.default_rng(642)
lam = stats.gamma(a=2 + b.sum(), scale=1 / (0.5 + n_b)).rvs(2000, random_state=rng)
yrep_pois = rng.poisson(lam[:, None], size=(2000, n_b))
T_pois = stats_test(yrep_pois)

def tableau_ppc(T_rep):
    return pd.DataFrame({"statistique": noms_T, "observée": T_obs.round(3), "répliques : moyenne": T_rep.mean(axis=0).round(3),
                         "2,5 %": np.percentile(T_rep, 2.5, axis=0).round(3), "97,5 %": np.percentile(T_rep, 97.5, axis=0).round(3),
                         "p bayésien": (T_rep >= T_obs).mean(axis=0).round(3)})
print(tableau_ppc(T_pois).to_string(index=False))
```
<!--sortie-->
```text
       statistique  observée  répliques : moyenne  2,5 %  97,5 %  p bayésien
variance / moyenne     3.324                1.000  0.879   1.127         0.0
     part de zéros     0.109                0.016  0.006   0.030         0.0
           maximum    21.000               11.541 10.000  14.000         0.0
```

*Lecture.* Le modèle de Poisson est rejeté sur les trois statistiques ($p_B=0$) : les clients sont hétérogènes.

**Étape 2 — la binomiale négative par MCMC.** On paramètre $\theta=(\log\mu,\log k)$, a priori $\mathcal N(1,2^2)$ et $\mathcal N(0,2^2)$.

```python
def log_post_nb(theta):
    mu, k = np.exp(theta[0]), np.exp(theta[1])
    log_vrais = stats.nbinom.logpmf(b, k, k / (k + mu)).sum()
    log_prior = -0.5 * ((theta[0] - 1) / 2) ** 2 - 0.5 * ((theta[1] - 0) / 2) ** 2
    return log_vrais + log_prior

rng = np.random.default_rng(643)
pilote, _ = metropolis_multi(log_post_nb, np.array([np.log(b.mean()), 0.0]), 3000, np.diag([0.003, 0.02]), rng)
cov_nb = np.cov(pilote[500:].T) * (2.38**2 / 2)             # covariance estimée sur une course pilote
```

**Étape 3 — quatre chaînes et diagnostics.**

```python
chaines_nb, taux_nb = [], []
for c in range(4):
    depart = np.array([np.log(b.mean()) + rng.normal(0, 0.3), rng.normal(0, 1.0)])
    ch, tx = metropolis_multi(log_post_nb, depart, 5000, cov_nb, rng)
    chaines_nb.append(ch[1000:]); taux_nb.append(tx)
chaines_nb = np.array(chaines_nb)
print("taux d'acceptation :", np.round(taux_nb, 3))
print("R-chapeau (log mu, log k) :", [round(float(split_rhat(chaines_nb[:, :, i])), 4) for i in range(2)])
mu_s, k_s = np.exp(chaines_nb[:, :, 0].ravel()), np.exp(chaines_nb[:, :, 1].ravel())
print(f"mu : moyenne {mu_s.mean():.3f}  IC95 [{np.percentile(mu_s, 2.5):.3f} ; {np.percentile(mu_s, 97.5):.3f}]")
print(f"k  : médiane {np.median(k_s):.3f}  IC95 [{np.percentile(k_s, 2.5):.3f} ; {np.percentile(k_s, 97.5):.3f}]")
```
<!--sortie-->
```text
taux d'acceptation : [0.365 0.352 0.357 0.354]
R-chapeau (log mu, log k) : [1.0029, 1.0019]
mu : moyenne 4.134  IC95 [3.817 ; 4.457]
k  : médiane 1.817  IC95 [1.513 ; 2.199]
```

**Étape 4 — revérifier.** Le modèle réparé reproduit-il les trois statistiques ?

```python
idx = rng.choice(len(mu_s), 2000, replace=False)
p_nb = k_s[idx] / (k_s[idx] + mu_s[idx])
yrep_nb = rng.negative_binomial(k_s[idx][:, None], p_nb[:, None], size=(2000, n_b))
print(tableau_ppc(stats_test(yrep_nb)).to_string(index=False))
```
<!--sortie-->
```text
       statistique  observée  répliques : moyenne  2,5 %  97,5 %  p bayésien
variance / moyenne     3.324                3.287  2.653   4.049       0.434
     part de zéros     0.109                0.117  0.083   0.155       0.667
           maximum    21.000               22.964 17.000  32.000       0.714
```

**Pour aller plus loin — un cas où la convergence échoue.** Prenez la loi à deux bosses (mélange de $\mathcal N(-4,1)$ et $\mathcal N(4,1)$) et quatre chaînes de pas 0,5 puis 6 ; comparez les moyennes de chaque chaîne et le $\widehat R$.

```python
def log_bimodale(x):
    return np.logaddexp(stats.norm.logpdf(x, -4, 1), stats.norm.logpdf(x, 4, 1))

for pas in (0.5, 6.0):
    rng = np.random.default_rng(641)
    ch = np.array([metropolis_1d(log_bimodale, x0, n=5000, pas=pas, rng=rng)[0] for x0 in (-6, -2, 2, 6)])
    print(f"pas {pas} : moyennes {np.round(ch[:, 1000:].mean(axis=1), 2)} | R-chapeau {split_rhat(ch[:, 1000:]):.3f}")
```
<!--sortie-->
```text
pas 0.5 : moyennes [-4.08  3.71  4.06  3.92] | R-chapeau 3.072
pas 6.0 : moyennes [-0.16  0.16 -0.28  0.17] | R-chapeau 1.002
```

### Application 6.5 — Niveaux de retour des retards de livraison (section 6.5)

**Objectif.** Estimer des niveaux de retour par les maxima mensuels (GEV) et par les excès au-dessus d'un seuil (GPD), et comparer à la vérité, qu'on connaît car les données sont simulées (graine 671 ; colis en nombre de Poisson de moyenne 3 par jour sur 3 652 jours ; durée = Pareto généralisée décalée de 1 jour, $\xi=0{,}25$, $\sigma=1{,}5$).

**Étape 1 — générer les colis.**

```python
rng = np.random.default_rng(671)
XI0, SIGMA0, COLIS_PAR_JOUR, JOURS = 0.25, 1.5, 3.0, 3652
n_j = rng.poisson(COLIS_PAR_JOUR, JOURS)
n_tot = n_j.sum()
u = rng.random(n_tot)
duree = 1 + SIGMA0 / XI0 * (u ** (-XI0) - 1)                      # inversion de la fonction de survie
date = pd.Timestamp("2016-01-01") + pd.to_timedelta(np.repeat(np.arange(JOURS), n_j), unit="D")
colis = pd.DataFrame({"date": date, "duree": duree})
print(f"{n_tot} colis ; durée médiane {colis['duree'].median():.2f} j ; maximum {duree.max():.2f} j")
print(f"> 5 jours : {(duree > 5).mean():.3%} | > 10 jours : {(duree > 10).mean():.3%} | > 20 jours : {(duree > 20).mean():.3%}")
```
<!--sortie-->
```text
10981 colis ; durée médiane 2.14 j ; maximum 56.32 j
> 5 jours : 13.114% | > 10 jours : 2.723% | > 20 jours : 0.373%
```

**Étape 2 — maxima par blocs : GEV.** (`scipy` paramètre la GEV par $c=-\xi$.)

```python
maxima_m = colis.groupby(colis["date"].dt.to_period("M"))["duree"].max().to_numpy()
c_hat, mu_hat, sig_hat = stats.genextreme.fit(maxima_m)
xi_hat = -c_hat
print(f"{len(maxima_m)} maxima mensuels ; GEV : mu = {mu_hat:.3f}, sigma = {sig_hat:.3f}, xi = {xi_hat:.3f}")
rng = np.random.default_rng(672)
boot = np.array([stats.genextreme.fit(rng.choice(maxima_m, len(maxima_m))) for _ in range(300)])
xi_boot = -boot[:, 0]
print(f"xi : IC95 bootstrap [{np.percentile(xi_boot, 2.5):.3f} ; {np.percentile(xi_boot, 97.5):.3f}]")
```
<!--sortie-->
```text
120 maxima mensuels ; GEV : mu = 13.741, sigma = 4.772, xi = 0.324
xi : IC95 bootstrap [0.213 ; 0.459]
```

**Étape 3 — niveaux de retour** et comparaison à la loi normale et à la vérité.

```python
def niveau_gev(T, mu, sigma, xi):
    return mu - sigma / xi * (1 - (-np.log(1 - 1 / T)) ** (-xi))

lam_m = COLIS_PAR_JOUR * 30.4375
sig_vrai = SIGMA0 * lam_m ** XI0
mu_vrai = 1 + SIGMA0 * (lam_m ** XI0 - 1) / XI0
m_norm, s_norm = maxima_m.mean(), maxima_m.std(ddof=1)
lignes = []
for T, nom in ((12, "1 an"), (120, "10 ans"), (1200, "100 ans")):
    ni_boot = np.array([niveau_gev(T, bb[1], bb[2], -bb[0]) for bb in boot])
    lignes.append({"retour": nom, "vérité": round(niveau_gev(T, mu_vrai, sig_vrai, XI0), 1),
                   "GEV": round(niveau_gev(T, mu_hat, sig_hat, xi_hat), 1),
                   "IC95 GEV": f"[{np.percentile(ni_boot, 2.5):.0f} ; {np.percentile(ni_boot, 97.5):.0f}]",
                   "normale": round(stats.norm.ppf(1 - 1 / T, m_norm, s_norm), 1)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 retour  vérité   GEV   IC95 GEV  normale
   1 an    29.1  31.5  [27 ; 37]     31.5
 10 ans    56.3  68.5 [51 ; 101]     41.1
100 ans   104.2 145.8 [89 ; 289]     48.2
```

**Étape 4 — excès au-dessus d'un seuil : GPD.** Variation du seuil, puis niveaux de retour.

```python
x_all = colis["duree"].to_numpy()

def ajuste_gpd(x, seuil):
    exces = x[x > seuil] - seuil
    xi_, loc_, sc_ = stats.genpareto.fit(exces, floc=0)             # loc = 0 : excès comptés depuis le seuil
    return xi_, sc_, len(exces)

for q in (0.80, 0.90, 0.95, 0.98):
    u_ = np.quantile(x_all, q)
    xi_, sc_, k_ = ajuste_gpd(x_all, u_)
    print(f"seuil au centile {q:.0%} : u = {u_:5.2f} j, {k_:4d} excès, xi = {xi_:.3f}, sigma_u = {sc_:.3f}")
```
<!--sortie-->
```text
seuil au centile 80% : u =  4.02 j, 2196 excès, xi = 0.273, sigma_u = 2.237
seuil au centile 90% : u =  5.69 j, 1098 excès, xi = 0.252, sigma_u = 2.795
seuil au centile 95% : u =  7.73 j,  549 excès, xi = 0.239, sigma_u = 3.440
seuil au centile 98% : u = 11.16 j,  220 excès, xi = 0.289, sigma_u = 4.073
```

```python
u_ = np.quantile(x_all, 0.95)
xi_p, sc_p, k_p = ajuste_gpd(x_all, u_)
zeta = (x_all > u_).mean()
niveau_pot = lambda m, xi_, sc_, u_, zeta_: u_ + sc_ / xi_ * ((m * zeta_) ** xi_ - 1)
niveau_vrai = lambda m: 1 + SIGMA0 / XI0 * (m ** XI0 - 1)
for ans, nom in ((1, "1 an"), (10, "10 ans"), (100, "100 ans")):
    m = n_tot * ans / 10.0                                         # nombre de colis dans la période de retour
    print(f"{nom:8s} vérité {niveau_vrai(m):6.1f} j | POT {niveau_pot(m, xi_p, sc_p, u_, zeta):6.1f} j")
```
<!--sortie-->
```text
1 an     vérité   29.5 j | POT   30.8 j
10 ans   vérité   56.4 j | POT   58.3 j
100 ans  vérité  104.2 j | POT  105.9 j
```

*Lecture.* À 100 ans, la loi normale annonce moins de 50 jours quand la vérité est de 104 ; la GEV et surtout le POT s'en approchent, avec des intervalles larges. **À faire :** ajoutez un bootstrap au POT pour obtenir ses intervalles (300 rééchantillonnages des colis) et comparez-les à ceux de la GEV.

### Application 6.6 — Deux transporteurs en même temps (section 6.6)

**Objectif.** Montrer qu'à même tau de Kendall, la copule choisie change d'un facteur 3 la probabilité de deux retards extrêmes le même jour. Les retards de deux transporteurs sont simulés (graine 683) avec des marginales Pareto généralisées et une vraie dépendance de Clayton *retournée* ($\theta=1{,}5$).

**Étape 1 — les simulateurs de copules.**

```python
from scipy.stats import norm, kendalltau, multivariate_normal

def sim_gauss(rho, n, rng):
    z = rng.multivariate_normal([0, 0], [[1, rho], [rho, 1]], n)
    return norm.cdf(z)

def sim_clayton(theta, n, rng):
    v = rng.gamma(1 / theta, 1.0, n)                      # facteur commun
    e = rng.exponential(size=(n, 2))
    return (1 + e / v[:, None]) ** (-1 / theta)

tau = 0.5
rho, theta = np.sin(np.pi * tau / 2), 2 * tau / (1 - tau)
rng = np.random.default_rng(680)
ug, uc = sim_gauss(rho, 200_000, rng), sim_clayton(theta, 200_000, rng)
for q in (0.10, 0.05, 0.01):
    print(f"q = {q:.2f} : P(les deux sous q) gaussienne {np.mean((ug < q).all(axis=1)):.5f} | Clayton {np.mean((uc < q).all(axis=1)):.5f}")
```
<!--sortie-->
```text
q = 0.10 : P(les deux sous q) gaussienne 0.04682 | Clayton 0.07184
q = 0.05 : P(les deux sous q) gaussienne 0.01959 | Clayton 0.03565
q = 0.01 : P(les deux sous q) gaussienne 0.00281 | Clayton 0.00681
```

**Étape 2 — les données des transporteurs.**

```python
def gpd_inv(u_, xi_, sg):                                  # fonction de répartition inverse de la GPD décalée de 1
    return 1 + sg / xi_ * ((1 - u_) ** (-xi_) - 1)

theta_v = 1.5
rng = np.random.default_rng(683)
n_jours = 1500
u_vrai = 1 - sim_clayton(theta_v, n_jours, rng)             # Clayton retournée : dépendance dans la queue supérieure
A = gpd_inv(u_vrai[:, 0], 0.25, 1.5)
B = gpd_inv(u_vrai[:, 1], 0.20, 2.0)
print(f"retard moyen A : {A.mean():.2f} j, B : {B.mean():.2f} j ; retard maximal A : {A.max():.1f} j, B : {B.max():.1f} j")
```
<!--sortie-->
```text
retard moyen A : 2.94 j, B : 3.39 j ; retard maximal A : 23.1 j, B : 31.4 j
```

**Étape 3 — ajuster les copules** sur les pseudo-observations (rangs divisés par $n+1$).

```python
def pseudo_obs(x, y):
    n_ = len(x)
    return stats.rankdata(x) / (n_ + 1), stats.rankdata(y) / (n_ + 1)

def ll_gauss(u, v, rho_):
    x, y = norm.ppf(u), norm.ppf(v)
    return np.sum(-0.5 * np.log(1 - rho_**2) - (rho_**2 * (x**2 + y**2) - 2 * rho_ * x * y) / (2 * (1 - rho_**2)))

def ll_clayton(u, v, th):
    return np.sum(np.log1p(th) - (th + 1) * (np.log(u) + np.log(v)) - (2 + 1 / th) * np.log(u**-th + v**-th - 1))

u, v = pseudo_obs(A, B)
tau_h = kendalltau(A, B).statistic
rho_h, th_h = np.sin(np.pi * tau_h / 2), 2 * tau_h / (1 - tau_h)
print(f"tau estimé : {tau_h:.3f} -> rho = {rho_h:.3f} (gaussienne) ; theta = {th_h:.2f} (Clayton)")
print(f"log-vraisemblance : gaussienne {ll_gauss(u, v, rho_h):.1f} | Clayton {ll_clayton(u, v, th_h):.1f} | "
      f"Clayton retournée {ll_clayton(1 - u, 1 - v, th_h):.1f}")
```
<!--sortie-->
```text
tau estimé : 0.416 -> rho = 0.608 (gaussienne) ; theta = 1.42 (Clayton)
log-vraisemblance : gaussienne 332.6 | Clayton 11.0 | Clayton retournée 431.7
```

**Étape 4 — la probabilité qui compte.** Probabilité que les deux retards dépassent leur 99ᵉ centile le même jour.

```python
qq = 0.99
p_indep = (1 - qq) ** 2
p_gauss = multivariate_normal([0, 0], [[1, rho_h], [rho_h, 1]]).cdf([-norm.ppf(qq), -norm.ppf(qq)])
p_clay_ret = (2 * (1 - qq) ** (-th_h) - 1) ** (-1 / th_h)
p_vrai = (2 * (1 - qq) ** (-theta_v) - 1) ** (-1 / theta_v)
p_emp = np.mean((u > qq) & (v > qq))
for nom, p in (("indépendance", p_indep), ("copule gaussienne", p_gauss), ("Clayton retournée", p_clay_ret), ("vérité", p_vrai), ("observé", p_emp)):
    print(f"{nom:18s} {p:.5f}  ({p / p_indep:5.1f} fois l'indépendance ; une fois tous les {round(1 / p):6d} jours)")
```
<!--sortie-->
```text
indépendance       0.00010  (  1.0 fois l'indépendance ; une fois tous les  10000 jours)
copule gaussienne  0.00193  ( 19.3 fois l'indépendance ; une fois tous les    518 jours)
Clayton retournée  0.00615  ( 61.5 fois l'indépendance ; une fois tous les    163 jours)
vérité             0.00630  ( 63.0 fois l'indépendance ; une fois tous les    159 jours)
observé            0.00533  ( 53.3 fois l'indépendance ; une fois tous les    188 jours)
```

*Lecture.* La copule gaussienne prévoit des doubles retards extrêmes 3,3 fois moins fréquents que la vérité. **À faire :** reprenez l'étape 3 avec la dépendance faible de `clients.csv` (panier moyen et nombre de commandes des acheteurs, en départageant les égalités par un bruit uniforme sur $[-0{,}5;\,0{,}5]$) : la dépendance de queue est-elle un enjeu ici ?

## Exercices

> 🧭 Cherchez d'abord à la main (ou sur papier), vérifiez ensuite par le code, et seulement après lisez le corrigé. ⭐ = application directe, ⭐⭐ = raisonnement, ⭐⭐⭐ = synthèse. Les exercices 6.8 à 6.10 réutilisent les fonctions de la préparation (`metropolis_1d`, `ess`, `split_rhat`).

### Exercice 6.1 ⭐ — Bêta-binomial (section 6.1)

La gérante teste un nouvel emballage : 3 clients sur 8 le jugent « excellent ». Avec l'a priori $\mathrm{Beta}(2,2)$ (« je pense plutôt autour de 50 % »), donnez (a) la loi a posteriori, (b) sa moyenne, (c) le poids de l'a priori dans cette moyenne, (d) la comparaison avec l'estimation du maximum de vraisemblance.

### Exercice 6.2 ⭐ — Gamma-Poisson (section 6.1)

Le site reçoit 2, 4 et 1 commandes lors de trois soirées. A priori $\lambda\sim\mathrm{Gamma}(3;\ \text{taux }1)$ (moyenne 3 commandes par soirée). Donnez la loi a posteriori de $\lambda$, sa moyenne, et un intervalle de crédibilité à 95 %.

### Exercice 6.3 ⭐⭐ — Normal-normal (section 6.1)

On modélise le log du panier avec $\sigma=0{,}35$ connu et l'a priori $\mathcal N(4{,}0;\ 0{,}5^2)$. À partir de combien d'observations le poids des données dans la moyenne a posteriori dépasse-t-il 90 % ? Calculez-le à la main, puis vérifiez avec le code.

### Exercice 6.4 ⭐⭐ — Test A/B bayésien (section 6.1)

La version A d'une page convertit 30 visiteurs sur 100, la version B 42 sur 110. Avec des a priori $\mathrm{Beta}(1,1)$, calculez par simulation la probabilité que B soit meilleure que A, le gain attendu en points de pourcentage, et la probabilité que le gain dépasse 5 points. Comparez avec le test de proportions fréquentiste.

### Exercice 6.5 ⭐ — Monte-Carlo (section 6.2)

Soient $U_1,U_2$ uniformes indépendantes sur $[0,1]$. (a) Calculez à la main $\mathbb E[\max(U_1,U_2)]$. (b) Estimez-la par Monte-Carlo avec 100 000 tirages, avec son erreur type et son intervalle de confiance. (c) Estimez $P(U_1+U_2>1{,}5)$ et comparez avec la valeur exacte $1/8$.

### Exercice 6.6 ⭐⭐ — Échantillonnage préférentiel (section 6.2)

Soit $X\sim\mathrm{Exp}(1)$. On veut $P(X>5)=e^{-5}$. (a) Estimez-la naïvement avec $n=10\,000$ tirages. (b) Utilisez la proposition « $5+\mathrm{Exp}(1)$ ». Que valent les poids ? Que remarquez-vous sur la variance de l'estimateur ?

### Exercice 6.7 ⭐⭐ — Inversion (section 6.2)

La durée de vie $T$ (en mois) d'un abonnement suit une loi de Weibull de fonction de répartition $F(t)=1-\exp\bigl(-(t/\lambda)^k\bigr)$, avec $\lambda=24$ et $k=1{,}5$. (a) Déterminez $F^{-1}$. (b) Simulez 100 000 durées. (c) Vérifiez la médiane théorique et la moyenne théorique $\lambda\,\Gamma(1+1/k)$.

### Exercice 6.8 ⭐⭐ — Metropolis à la main (section 6.3)

On veut une chaîne sur trois états $\{1,2,3\}$ de loi stationnaire proportionnelle à $(1,2,1)$. La proposition choisit l'un des deux autres états avec probabilité $\tfrac12$. (a) Écrivez la matrice de transition de Metropolis. (b) Vérifiez le bilan détaillé. (c) Vérifiez par le code, et par simulation.

### Exercice 6.9 ⭐⭐ — Metropolis sur une échelle logarithmique (section 6.3)

Six semaines de commandes : 3, 5, 4, 6, 2, 5. Modèle : Poisson$(\lambda)$, a priori $\mathrm{Gamma}(2;\ \text{taux }0{,}5)$. (a) Donnez la loi a posteriori exacte. (b) Écrivez un Metropolis sur $\theta=\log\lambda$ (attention à la transformation de la densité) et comparez avec la loi exacte.

### Exercice 6.10 ⭐⭐ — Diagnostics (section 6.4)

Une chaîne autorégressive $x_t=\varphi\,x_{t-1}+\sqrt{1-\varphi^2}\,\varepsilon_t$ ($\varepsilon_t\sim\mathcal N(0,1)$) a pour loi stationnaire $\mathcal N(0,1)$ et pour autocorrélation $\rho_k=\varphi^k$. (a) Montrez que son ESS théorique vaut environ $n\,\dfrac{1-\varphi}{1+\varphi}$. (b) Pour $\varphi=0{,}9$ et $n=20\,000$, comparez avec l'ESS calculée. (c) Quatre chaînes de $\varphi=0{,}99$ lancées de $-10,-3,3,10$ : calculez le $\widehat R$ avec et sans élimination des 300 premiers points.

### Exercice 6.11 ⭐⭐ — Vérification prédictive (section 6.4)

Modélisez les paniers des acheteurs du canal Boutique (a) par une loi normale sur le panier en €, (b) par une loi normale sur le **logarithme** du panier. Avec la statistique-test « asymétrie » (skewness) et le plus petit panier, quel modèle passe la vérification prédictive a posteriori ?

### Exercice 6.12 ⭐⭐ — Facteur de Bayes (section 6.4)

Neuf clients sur dix préfèrent le nouvel emballage. $H_0$ : $\theta=0{,}5$ ; $H_1$ : $\theta\sim\mathcal U(0,1)$. Calculez à la main $\mathrm{BF}_{10}$, comparez à la p-valeur exacte bilatérale, puis calculez la probabilité a posteriori de $H_1$ si l'on pense au départ qu'il y a 1 chance sur 4 que l'emballage ait un effet.

### Exercice 6.13 ⭐⭐ — Valeurs extrêmes (section 6.5)

Pour des retards de colis, on a choisi le seuil $u=5$ jours ; 5 % des colis le dépassent ($\zeta_u=0{,}05$) et la loi des excès est GPD de $\xi=0{,}2$ et $\sigma_u=2$ jours. (a) Calculez à la main le retard dépassé en moyenne une fois tous les 1 000 colis. (b) Et tous les 10 000 colis ? (c) Que devient (b) si $\xi=0{,}4$ au lieu de 0,2 ? Qu'en concluez-vous ?

### Exercice 6.14 ⭐⭐⭐ — Dépendance de queue de Clayton (section 6.6)

(a) Démontrez que, pour la copule de Clayton, $P(V\le q\mid U\le q)=(2-q^{\theta})^{-1/\theta}$, puis que cette quantité tend vers $2^{-1/\theta}$ quand $q\to0$. (b) Vérifiez numériquement avec $\theta=2$ pour $q=0{,}1;\,0{,}01;\,0{,}001$. (c) Par la formule de survie, que vaut $P(U>1-q,\,V>1-q)$ pour la copule de Clayton *retournée* ? Comparez avec une copule gaussienne de même tau.

## Corrigés

### Corrigé 6.1

(a) Succès $y=3$, échecs $n-y=5$ : $\mathrm{Beta}(2+3,\,2+5)=\mathrm{Beta}(5,7)$. (b) Moyenne $5/12=0{,}4167$. (c) Le poids de l'a priori est $\dfrac{a+b}{a+b+n}=\dfrac4{4+8}=\dfrac13$ : un tiers de l'a priori (moyenne 0,5), deux tiers des données (fréquence 0,375) : $\tfrac13\times0{,}5+\tfrac23\times0{,}375=0{,}4167$ ✓. (d) Le maximum de vraisemblance est $3/8=0{,}375$ ; l'a posteriori est **tiré vers 0,5**. Avec 8 observations seulement, l'a priori compte beaucoup (voir 6.1.6).

```python
post = stats.beta(2 + 3, 2 + 5)
print(f"a posteriori Beta(5, 7) : moyenne {post.mean():.4f} | IC95 [{post.ppf(0.025):.3f} ; {post.ppf(0.975):.3f}]")
print(f"poids de l'a priori : {4 / 12:.3f} | EMV : {3 / 8:.3f} | moyenne pondérée : {4 / 12 * 0.5 + 8 / 12 * 3 / 8:.4f}")
```
<!--sortie-->
```text
a posteriori Beta(5, 7) : moyenne 0.4167 | IC95 [0.167 ; 0.692]
poids de l'a priori : 0.333 | EMV : 0.375 | moyenne pondérée : 0.4167
```

### Corrigé 6.2

$\sum y_i=7$, $n=3$ : $\lambda\mid y\sim\mathrm{Gamma}(3+7;\ 1+3)=\mathrm{Gamma}(10;\ \text{taux }4)$, de moyenne $10/4=2{,}5$ commandes par soirée. Elle est **comprise entre la moyenne a priori (3) et celle des données ($7/3=2{,}33$)**, comme il se doit pour un compromis ; elle est plus proche des données car celles-ci pèsent $3/4$ (3 observations contre un a priori valant « 1 observation » : le taux de l'a priori est 1).

```python
post = stats.gamma(a=10, scale=1 / 4)
print(f"Gamma(10, taux 4) : moyenne {post.mean():.3f} | IC95 [{post.ppf(0.025):.3f} ; {post.ppf(0.975):.3f}]")
```
<!--sortie-->
```text
Gamma(10, taux 4) : moyenne 2.500 | IC95 [1.199 ; 4.271]
```

### Corrigé 6.3

Le poids des données est $w=\dfrac{n/\sigma^2}{1/\tau_0^2+n/\sigma^2}$. On veut $w>0{,}9\iff n/\sigma^2>9/\tau_0^2\iff n>9\sigma^2/\tau_0^2=9\times0{,}1225/0{,}25=4{,}41$. Il faut donc **$n\ge5$** observations (avec $n=5$ : $w=0{,}911$). L'a priori est donc déjà « oublié » à 90 % avec cinq clients seulement : il est assez large par rapport à $\sigma$.

```python
sigma, tau0 = 0.35, 0.5
for n in range(1, 8):
    w = (n / sigma**2) / (1 / tau0**2 + n / sigma**2)
    print(f"n = {n} : poids des données = {w:.3f}" + ("   <- premier n au-dessus de 90 %" if w > 0.9 and (n == 1 or (((n - 1) / sigma**2) / (1 / tau0**2 + (n - 1) / sigma**2)) <= 0.9) else ""))
```
<!--sortie-->
```text
n = 1 : poids des données = 0.671
n = 2 : poids des données = 0.803
n = 3 : poids des données = 0.860
n = 4 : poids des données = 0.891
n = 5 : poids des données = 0.911   <- premier n au-dessus de 90 %
n = 6 : poids des données = 0.924
n = 7 : poids des données = 0.935
```

### Corrigé 6.4

A : $\mathrm{Beta}(31,71)$, B : $\mathrm{Beta}(43,69)$. On tire dans chaque loi et on compare.

```python
rng = np.random.default_rng(690)
S = 400_000
pA = stats.beta(1 + 30, 1 + 70).rvs(S, random_state=rng)
pB = stats.beta(1 + 42, 1 + 68).rvs(S, random_state=rng)
gain = pB - pA
print(f"P(B > A) = {(gain > 0).mean():.4f} | gain moyen = {100 * gain.mean():.1f} points | P(gain > 5 points) = {(gain > 0.05).mean():.4f}")
print(f"IC de crédibilité à 95 % du gain : [{100 * np.percentile(gain, 2.5):.1f} ; {100 * np.percentile(gain, 97.5):.1f}] points")

from statsmodels.stats.proportion import proportions_ztest
z, p = proportions_ztest([42, 30], [110, 100])
print(f"test fréquentiste : z = {z:.3f}, p-valeur bilatérale = {p:.4f} (unilatérale : {p / 2:.4f})")
```
<!--sortie-->
```text
P(B > A) = 0.8925 | gain moyen = 8.0 points | P(gain > 5 points) = 0.6800
IC de crédibilité à 95 % du gain : [-4.7 ; 20.6] points
test fréquentiste : z = 1.248, p-valeur bilatérale = 0.2122 (unilatérale : 0.1061)
```

La probabilité bayésienne que B soit meilleure est de 89 % ; le test fréquentiste donne une p-valeur bilatérale de 0,21 (unilatérale 0,106), **non significative** à 5 %. Remarquez que $1-0{,}106=0{,}894$ est presque égal à la probabilité bayésienne de 0,8925 : avec un a priori plat et des données assez abondantes, la p-valeur unilatérale et la probabilité a posteriori de l'hypothèse « opposée » **coïncident presque** (c'est un résultat classique pour les proportions). Mais **la p-valeur ne dit pas « la probabilité que B soit meilleure »** (volume I, section 3.5.2), alors que la probabilité bayésienne le dit : « 89 % de chances que B soit meilleure, gain probable de 8 points, avec une probabilité de 68 % que le gain dépasse 5 points ». L'intervalle de crédibilité à 95 % du gain, [−4,7 ; +20,6] points, est très large : avec une centaine de visiteurs par version, on ne sait pas grand-chose, et c'est exactement ce que dit le test non significatif.

### Corrigé 6.5

(a) $P(\max\le x)=x^2$, de densité $2x$ : $\mathbb E[\max]=\int_0^1x\cdot2x\,dx=2/3$. (b), (c) :

```python
rng = np.random.default_rng(691)
n = 100_000
u = rng.random((n, 2))
g = u.max(axis=1)
est, se = g.mean(), g.std(ddof=1) / np.sqrt(n)
print(f"E[max] estimée : {est:.4f}  ± {1.96 * se:.4f} (IC95) | exacte : {2 / 3:.4f}")
h = (u.sum(axis=1) > 1.5)
est, se = h.mean(), h.std(ddof=1) / np.sqrt(n)
print(f"P(U1 + U2 > 1,5) estimée : {est:.4f} ± {1.96 * se:.4f} | exacte : {1 / 8:.4f}")
```
<!--sortie-->
```text
E[max] estimée : 0.6682  ± 0.0015 (IC95) | exacte : 0.6667
P(U1 + U2 > 1,5) estimée : 0.1265 ± 0.0021 | exacte : 0.1250
```

L'intervalle de confiance de Monte-Carlo contient la valeur exacte dans chaque cas (dans 95 % des répétitions de l'expérience, en moyenne).

### Corrigé 6.6

(a) L'estimateur naïf a une variance $p(1-p)/n\approx6{,}7\times10^{-7}$, soit un écart-type de $8{,}2\times10^{-4}$ pour une valeur de $6{,}7\times10^{-3}$ : environ 12 % d'erreur relative. (b) Tirons $Y=5+E$, $E\sim\mathrm{Exp}(1)$ (densité $h(y)=e^{-(y-5)}$ pour $y>5$). Alors $f(y)/h(y)=e^{-y}/e^{-(y-5)}=e^{-5}$ **pour tout $y>5$** : tous les tirages sont dans la zone d'intérêt (indicatrice égale à 1) et **tous les poids valent $e^{-5}$**. L'estimateur vaut donc $e^{-5}$ **exactement**, avec une **variance nulle** : c'est la proposition idéale, qui est *proportionnelle à $g\times f$*. En pratique, on ne la connaît pas (sinon on ne simulerait pas), mais on s'en approche.

```python
rng = np.random.default_rng(692)
n = 10_000
naif = (rng.exponential(1, n) > 5).mean()
y = 5 + rng.exponential(1, n)
poids = np.exp(-y) / np.exp(-(y - 5))                      # f / h
pref = np.mean((y > 5) * poids)
print(f"exact : {np.exp(-5):.6f} | naïf : {naif:.6f} | préférentiel : {pref:.6f} | poids min / max : {poids.min():.6f} / {poids.max():.6f}")
```
<!--sortie-->
```text
exact : 0.006738 | naïf : 0.006700 | préférentiel : 0.006738 | poids min / max : 0.006738 / 0.006738
```

### Corrigé 6.7

(a) On résout $u=1-\exp(-(t/\lambda)^k)$ : $t=\lambda\bigl[-\ln(1-u)\bigr]^{1/k}$. (b) et (c) : la médiane théorique est $\lambda(\ln2)^{1/k}$.

```python
from math import gamma, log
lam, k = 24, 1.5
rng = np.random.default_rng(693)
u = rng.random(100_000)
t = lam * (-np.log(1 - u)) ** (1 / k)
print(f"médiane simulée {np.median(t):.3f} | théorique {lam * log(2) ** (1 / k):.3f}")
print(f"moyenne simulée {t.mean():.3f} | théorique {lam * gamma(1 + 1 / k):.3f}")
print(f"P(T > 36) simulée {np.mean(t > 36):.4f} | théorique {np.exp(-(36 / lam) ** k):.4f}")
```
<!--sortie-->
```text
médiane simulée 18.892 | théorique 18.797
moyenne simulée 21.713 | théorique 21.666
P(T > 36) simulée 0.1587 | théorique 0.1593
```

### Corrigé 6.8

Cible $\pi=(0{,}25;\,0{,}5;\,0{,}25)$. (a) $P_{12}=\tfrac12\min(1,2)=\tfrac12$ ; $P_{13}=\tfrac12\min(1,1)=\tfrac12$ ; $P_{11}=0$. Depuis 2 : $P_{21}=\tfrac12\cdot\tfrac12=\tfrac14$, $P_{23}=\tfrac14$, $P_{22}=\tfrac12$. Depuis 3 : $P_{31}=\tfrac12$, $P_{32}=\tfrac12\min(1,2)=\tfrac12$, $P_{33}=0$. (b) $\pi_1P_{12}=0{,}25\times\tfrac12=0{,}125=\pi_2P_{21}=0{,}5\times\tfrac14$ ✓ ; $\pi_1P_{13}=0{,}125=\pi_3P_{31}$ ✓ ; $\pi_2P_{23}=0{,}5\times\tfrac14=0{,}125=\pi_3P_{32}=0{,}25\times\tfrac12$ ✓.

```python
poids = np.array([1.0, 2.0, 1.0]); pi = poids / poids.sum(); k3 = 3
P = np.zeros((k3, k3))
for i in range(k3):
    for j in range(k3):
        if i != j:
            P[i, j] = 0.5 * min(1, poids[j] / poids[i])
    P[i, i] = 1 - P[i].sum()
print(P)
print("bilan détaillé (écart max) :", np.abs(pi[:, None] * P - (pi[:, None] * P).T).max())
rng = np.random.default_rng(694)
etat, compte = 0, np.zeros(3)
for _ in range(60_000):
    etat = rng.choice(3, p=P[etat]); compte[etat] += 1
print("fréquences simulées :", (compte / 60_000).round(3), "| cible :", pi)
```
<!--sortie-->
```text
[[0.   0.5  0.5 ]
 [0.25 0.5  0.25]
 [0.5  0.5  0.  ]]
bilan détaillé (écart max) : 0.0
fréquences simulées : [0.251 0.5   0.249] | cible : [0.25 0.5  0.25]
```

### Corrigé 6.9

(a) $\sum y=25$, $n=6$ : $\lambda\mid y\sim\mathrm{Gamma}(2+25;\ 0{,}5+6)=\mathrm{Gamma}(27;\ \text{taux }6{,}5)$, de moyenne $27/6{,}5=4{,}154$. (b) Si $\theta=\log\lambda$, la densité de $\theta$ est celle de $\lambda$ multipliée par le jacobien $|d\lambda/d\theta|=\lambda=e^\theta$. L'a posteriori **non normalisé** de $\theta$ est donc $\propto e^{(27-1)\theta}e^{-6{,}5e^{\theta}}\cdot e^{\theta}=e^{27\theta-6{,}5e^\theta}$ : $\log\pi(\theta)=27\theta-6{,}5\,e^\theta$. **Oublier le jacobien est l'erreur classique** : on échantillonnerait alors une autre loi.

```python
def log_cible(theta):
    return 27 * theta - 6.5 * np.exp(theta)

rng = np.random.default_rng(695)
chaine, taux = metropolis_1d(log_cible, x0=np.log(4.0), n=30_000, pas=0.5, rng=rng)
lam_s = np.exp(chaine[2000:])
exacte = stats.gamma(a=27, scale=1 / 6.5)
print(f"taux d'acceptation {taux:.3f}")
print(f"MH : moyenne {lam_s.mean():.4f}, écart-type {lam_s.std():.4f}, quantiles 2,5 / 50 / 97,5 % {np.percentile(lam_s, [2.5, 50, 97.5]).round(3)}")
print(f"exact : moyenne {exacte.mean():.4f}, écart-type {exacte.std():.4f}, quantiles {exacte.ppf([0.025, 0.5, 0.975]).round(3)}")
```
<!--sortie-->
```text
taux d'acceptation 0.420
MH : moyenne 4.1457, écart-type 0.8114, quantiles 2,5 / 50 / 97,5 % [2.712 4.076 5.874]
exact : moyenne 4.1538, écart-type 0.7994, quantiles [2.737 4.103 5.861]
```

### Corrigé 6.10

(a) $\mathrm{ESS}=n/\bigl(1+2\sum_{k\ge1}\rho_k\bigr)$ et $\sum_{k\ge1}\varphi^k=\dfrac\varphi{1-\varphi}$, donc $1+2\dfrac\varphi{1-\varphi}=\dfrac{1+\varphi}{1-\varphi}$ et $\mathrm{ESS}=n\dfrac{1-\varphi}{1+\varphi}$. Pour $\varphi=0{,}9$ : $n/19$, soit environ 1 053 sur 20 000. (b), (c) :

```python
def ar1(phi, n, x0, rng):
    x = np.empty(n); x[0] = x0
    for t in range(1, n):
        x[t] = phi * x[t - 1] + np.sqrt(1 - phi**2) * rng.standard_normal()
    return x

rng = np.random.default_rng(696)
x = ar1(0.9, 20_000, 0.0, rng)
print(f"ESS théorique {20_000 * (1 - 0.9) / (1 + 0.9):.0f} | ESS calculée {ess(x):.0f}")
chaines4 = np.array([ar1(0.99, 1500, x0, rng) for x0 in (-10, -3, 3, 10)])
print(f"R-chapeau avec les 1 500 points : {split_rhat(chaines4):.3f} | sans les 300 premiers : {split_rhat(chaines4[:, 300:]):.3f}")
print(f"ESS théorique par chaîne (phi = 0,99) : {1200 * (1 - 0.99) / (1 + 0.99):.0f} sur 1 200 points")
```
<!--sortie-->
```text
ESS théorique 1053 | ESS calculée 1111
R-chapeau avec les 1 500 points : 1.142 | sans les 300 premiers : 1.063
ESS théorique par chaîne (phi = 0,99) : 6 sur 1 200 points
```

L'ESS calculée est proche de la théorie. Pour $\varphi=0{,}99$, la chaîne est si lente que l'ESS d'une chaîne de 1 200 points est de l'ordre de 6 seulement : le $\widehat R$ **détecte le problème** (valeur nettement supérieure à 1,01, quoi qu'on fasse), parce que chaque chaîne n'a pas eu le temps de quitter son voisinage de départ. C'est exactement la situation où il faut **allonger** ou **reparamétriser**.

### Corrigé 6.11

Données : les paniers des 449 acheteurs du canal Boutique. Sous le modèle normal avec a priori $p(\mu,\sigma^2)\propto1/\sigma^2$, la loi a posteriori est : $\sigma^2\mid y\sim(n-1)s^2/\chi^2_{n-1}$, puis $\mu\mid\sigma^2,y\sim\mathcal N(\bar y,\sigma^2/n)$, ce qui donne directement des tirages (sans MCMC).

```python
pan = clients[(clients["canal_acquisition"] == "Boutique") & (clients["panier_moyen"] > 0)]["panier_moyen"].to_numpy()

def ppc_normal(y_, graine, S=2000):
    rng = np.random.default_rng(graine)
    n_, ybar, s2 = len(y_), y_.mean(), y_.var(ddof=1)
    sig2 = (n_ - 1) * s2 / rng.chisquare(n_ - 1, S)
    mu = rng.normal(ybar, np.sqrt(sig2 / n_))
    yrep = rng.normal(mu[:, None], np.sqrt(sig2)[:, None], size=(S, n_))
    T = lambda a: np.c_[stats.skew(a, axis=-1), a.min(axis=-1)]
    To, Tr = T(y_[None, :])[0], T(yrep)
    return To, Tr, (Tr >= To).mean(axis=0)

for nom, donnees in (("normale sur le panier (€)", pan), ("normale sur le log du panier", np.log(pan))):
    To, Tr, pb = ppc_normal(donnees, 697)
    print(f"{nom:30s} asymétrie : obs. {To[0]:6.3f}, rép. {Tr[:, 0].mean():6.3f} (p {pb[0]:.3f}) | "
          f"minimum : obs. {To[1]:7.3f}, rép. {Tr[:, 1].mean():7.3f} (p {pb[1]:.3f})")
```
<!--sortie-->
```text
normale sur le panier (€)      asymétrie : obs.  1.037, rép.  0.003 (p 0.000) | minimum : obs.  25.530, rép. -11.756 (p 0.000)
normale sur le log du panier   asymétrie : obs.  0.046, rép.  0.003 (p 0.360) | minimum : obs.   3.240, rép.   3.094 (p 0.144)
```

Le modèle sur le panier brut échoue : les données ont une asymétrie de 1,04 (queue à droite) que le modèle symétrique ne reproduit jamais (asymétrie répliquée : 0,00 ; $p_B=0$), et il prédit des **paniers négatifs** (le minimum répliqué vaut en moyenne −11,8 €, ce qui est absurde), alors que le plus petit panier observé est de 25,5 €. Le modèle sur le logarithme (c'est-à-dire une loi log-normale pour le panier) passe les deux vérifications ($p_B=0{,}36$ pour l'asymétrie et $0{,}14$ pour le minimum). C'est la raison pour laquelle on modélise les montants positifs sur une échelle logarithmique.

### Corrigé 6.12

$n=10$, $y=9$. $p(y\mid H_0)=\binom{10}9\,0{,}5^{10}=10/1024=0{,}00977$ ; $p(y\mid H_1)=1/11=0{,}0909$. $\mathrm{BF}_{10}=\dfrac{1/11}{10/1024}=\dfrac{1024}{110}=9{,}31$ : des données environ 9 fois plus probables sous $H_1$. La p-valeur exacte bilatérale est $2\bigl[\binom{10}9+\binom{10}{10}\bigr]/1024=22/1024=0{,}0215$. Avec une cote a priori de $\dfrac{1/4}{3/4}=\dfrac13$ en faveur de $H_1$, la cote a posteriori est $9{,}31\times\tfrac13=3{,}10$, soit une probabilité $3{,}10/4{,}10=0{,}756$ pour $H_1$ : on a gagné en crédibilité mais on est loin de la certitude, alors que la p-valeur de 0,02 « rejette $H_0$ au seuil de 5 % ». C'est la différence de langage entre « rejeter » et « mettre à jour ses croyances ».

```python
from scipy.special import comb
m0 = comb(10, 9) * 0.5**10
m1 = 1 / 11
bf = m1 / m0
print(f"p(y|H0) = {m0:.5f} | p(y|H1) = {m1:.5f} | BF10 = {bf:.3f} (à la main : 1024/110 = {1024 / 110:.3f})")
print(f"p-valeur exacte bilatérale : {stats.binomtest(9, 10, 0.5).pvalue:.4f} (à la main : 22/1024 = {22 / 1024:.4f})")
cote_post = bf * (0.25 / 0.75)
print(f"cote a posteriori {cote_post:.3f} -> P(H1 | données) = {cote_post / (1 + cote_post):.3f}")
```
<!--sortie-->
```text
p(y|H0) = 0.00977 | p(y|H1) = 0.09091 | BF10 = 9.309 (à la main : 1024/110 = 9.309)
p-valeur exacte bilatérale : 0.0215 (à la main : 22/1024 = 0.0215)
cote a posteriori 3.103 -> P(H1 | données) = 0.756
```

### Corrigé 6.13

On utilise $x_m=u+\dfrac{\sigma_u}\xi\bigl[(m\zeta_u)^\xi-1\bigr]$. (a) $m=1\,000$ : $m\zeta_u=50$, $50^{0{,}2}=e^{0{,}2\ln50}=e^{0{,}7824}=2{,}187$ ; $x=5+\dfrac2{0{,}2}(2{,}187-1)=5+10\times1{,}187=16{,}87$ jours. (b) $m=10\,000$ : $m\zeta_u=500$, $500^{0{,}2}=e^{0{,}2\ln500}=3{,}466$, donc $x=5+10\times2{,}466=29{,}66$ jours. (c) Avec $\xi=0{,}4$ : $x_{10\,000}=5+\dfrac2{0{,}4}\bigl(500^{0{,}4}-1\bigr)=5+5\times(12{,}01-1)=60{,}1$ jours. **Doubler $\xi$ double (à peu près) le niveau de retour à 10 000 colis** : une petite erreur sur l'indice de queue a une conséquence énorme sur l'extrapolation.

```python
def niveau_pot_ex(m, xi, sc, u, zeta):
    return u + sc / xi * ((m * zeta) ** xi - 1)

for xi_ in (0.2, 0.4):
    print(f"xi = {xi_} : " + " | ".join(f"1 colis sur {m:>6,}: {niveau_pot_ex(m, xi_, 2.0, 5.0, 0.05):6.2f} jours".replace(",", " ") for m in (1_000, 10_000)))
```
<!--sortie-->
```text
xi = 0.2 : 1 colis sur  1 000:  16.87 jours | 1 colis sur 10 000:  29.66 jours
xi = 0.4 : 1 colis sur  1 000:  23.91 jours | 1 colis sur 10 000:  60.06 jours
```

### Corrigé 6.14

(a) $P(V\le q\mid U\le q)=\dfrac{C_\theta(q,q)}{q}=\dfrac{(2q^{-\theta}-1)^{-1/\theta}}q$. Or $(2q^{-\theta}-1)^{-1/\theta}=\bigl[q^{-\theta}(2-q^{\theta})\bigr]^{-1/\theta}=q\,(2-q^\theta)^{-1/\theta}$ ; en divisant par $q$ : $(2-q^\theta)^{-1/\theta}$. Quand $q\to0$, $q^\theta\to0$ (car $\theta>0$) et l'on obtient $2^{-1/\theta}$. $\square$ (c) Pour la Clayton retournée, $(U,V)=(1-U',1-V')$ avec $(U',V')$ de Clayton : $P(U>1-q,V>1-q)=P(U'<q,V'<q)=C_\theta(q,q)=(2q^{-\theta}-1)^{-1/\theta}$. Avec $\theta=2$ ($\tau=0{,}5$, $\rho=\sin(\pi/4)=0{,}7071$ pour la gaussienne), on compare.

```python
theta, rho = 2.0, np.sin(np.pi / 4)
lignes = []
for q in (0.1, 0.01, 0.001):
    cond = (2 - q**theta) ** (-1 / theta)
    c_qq = (2 * q ** (-theta) - 1) ** (-1 / theta)
    gauss = multivariate_normal([0, 0], [[1, rho], [rho, 1]]).cdf([norm.ppf(q), norm.ppf(q)])
    lignes.append({"q": q, "P(V<=q | U<=q)": round(cond, 4), "limite": round(2 ** (-1 / theta), 4),
                   "Clayton retournée": f"{c_qq:.3e}", "gaussienne": f"{gauss:.3e}", "rapport": round(c_qq / gauss, 1)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
    q  P(V<=q | U<=q)  limite Clayton retournée gaussienne  rapport
0.100          0.7089  0.7071         7.089e-02  4.739e-02      1.5
0.010          0.7071  0.7071         7.071e-03  2.735e-03      2.6
0.001          0.7071  0.7071         7.071e-04  1.654e-04      4.3
```

La probabilité conditionnelle de Clayton converge vers $2^{-1/2}=0{,}707$ (la limite $\lambda$), tandis que celle de la copule gaussienne tend vers 0 quand $q\to0$. Le rapport entre les probabilités conjointes de la Clayton retournée et de la gaussienne **croît sans cesse** à mesure que $q$ diminue : c'est la signature de la dépendance de queue.
