# Chapitre 7 : ➕ Inférence causale — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 7 du livre (inférence causale, entièrement facultatif). Les **applications** refont, avec leur code complet, les analyses dont le livre ne donne que le raisonnement et les résultats : elles utilisent `clients.csv` (l'expérience randomisée) et les fichiers simulés `ch07-*.csv` produits par `build/sim_ch07.py`. Les **exercices** (12, notés ⭐ à ⭐⭐⭐) se font d'abord à la main ; les corrigés suivent. Comme les données sont simulées, nous connaissons la vérité et pouvons juger chaque méthode.

## Applications

### Préparation commune

Tous les blocs de ce chapitre du cahier partagent le même espace de noms : exécutez-les dans l'ordre.

```python
import numpy as np
import pandas as pd
import statsmodels.api as sm
import statsmodels.formula.api as smf
from scipy import stats
from scipy.special import expit
```

### Application 7.1 — Les résultats potentiels sur huit clients (section 7.1.2)

**Objectif.** Voir le « problème fondamental » sur un petit tableau où l'on connaît, exceptionnellement, les deux dépenses potentielles de chaque client, puis calculer l'ATE, l'ATT, l'ATU et la décomposition de la différence naïve.

**Étape 1 — le tableau et les trois effets moyens.**

```python
import itertools
import numpy as np
import pandas as pd

clients = pd.DataFrame({
    "client": list("ABCDEFGH"),
    "y0": [100, 150, 180, 130, 50, 80, 60, 90],      # dépense SANS offre (€)
    "y1": [120, 165, 190, 145, 60, 85, 75, 100],     # dépense AVEC offre (€)
    "offre": [1, 1, 1, 1, 0, 0, 0, 0],               # ce que la gérante a décidé
})
clients["effet"] = clients["y1"] - clients["y0"]
print("Le tableau vu par Dieu :")
print(clients.to_string(index=False))
print()
print("Le tableau vu par la gérante (une moitié du tableau manque toujours) :")
vu = clients.assign(y0=clients["y0"].where(clients["offre"] == 0),
                    y1=clients["y1"].where(clients["offre"] == 1))
print(vu[["client", "offre", "y0", "y1"]].to_string(index=False))
```
<!--sortie-->
```text
Le tableau vu par Dieu :
client  y0  y1  offre  effet
     A 100 120      1     20
     B 150 165      1     15
     C 180 190      1     10
     D 130 145      1     15
     E  50  60      0     10
     F  80  85      0      5
     G  60  75      0     15
     H  90 100      0     10

Le tableau vu par la gérante (une moitié du tableau manque toujours) :
client  offre   y0    y1
     A      1  NaN 120.0
     B      1  NaN 165.0
     C      1  NaN 190.0
     D      1  NaN 145.0
     E      0 50.0   NaN
     F      0 80.0   NaN
     G      0 60.0   NaN
     H      0 90.0   NaN
```

**Étape 2 — ATE, ATT, ATU, différence naïve.** Les effets individuels sont connus ici ; la gérante, elle, n'observe qu'une colonne par client.

```python
ate = clients["effet"].mean()
att = clients.loc[clients["offre"] == 1, "effet"].mean()
atu = clients.loc[clients["offre"] == 0, "effet"].mean()
print(f"ATE = {ate}   ATT = {att}   ATU = {atu}")

observe = np.where(clients["offre"] == 1, clients["y1"], clients["y0"])
moy_offre = observe[clients["offre"] == 1].mean()
moy_sans = observe[clients["offre"] == 0].mean()
print(f"\nDépense moyenne observée avec offre : {moy_offre}   sans offre : {moy_sans}")
print(f"Différence naïve (ce que calcule la gérante) : {moy_offre - moy_sans}")
```
<!--sortie-->
```text
ATE = 12.5   ATT = 15.0   ATU = 10.0

Dépense moyenne observée avec offre : 155.0   sans offre : 70.0
Différence naïve (ce que calcule la gérante) : 85.0
```

**Étape 3 — le biais de sélection.** On vérifie que « différence naïve = ATT + biais de sélection » (section 7.1.2).

```python
y0_traites = clients.loc[clients["offre"] == 1, "y0"].mean()
y0_non_traites = clients.loc[clients["offre"] == 0, "y0"].mean()
print("Sans offre, les traités auraient dépensé :", y0_traites, "| les non-traités dépensent :", y0_non_traites)
print("Biais de sélection :", y0_traites - y0_non_traites)
print("ATT + biais =", att + (y0_traites - y0_non_traites), "= différence naïve", moy_offre - moy_sans)
```
<!--sortie-->
```text
Sans offre, les traités auraient dépensé : 140.0 | les non-traités dépensent : 70.0
Biais de sélection : 70.0
ATT + biais = 85.0 = différence naïve 85.0
```

*Lecture.* L'ATT vaut 15, l'ATU 10, l'ATE 12,5 ; la différence naïve vaut 85 parce que les clients choisis auraient dépensé 70 € de plus que les autres **même sans offre** : 15 + 70 = 85.

**Pour aller plus loin.** Modifiez la colonne `offre` (par exemple en donnant l'offre aux clients A, C, E, G) : quel est le nouveau biais de sélection ?

### Application 7.2 — La randomisation, exhaustivement puis sur 4 000 clients (section 7.1.3)

**Objectif.** Vérifier que la différence naïve est sans biais quand l'attribution est tirée au sort, d'abord en énumérant les 70 attributions possibles sur les huit clients, puis par simulation sur l'étude observationnelle (`ch07-observationnel.csv`, offre **ciblée**).

**Étape 1 — les 70 attributions possibles** (on reprend le tableau de l'application 7.1).

```python
estimations = []
for groupe_offre in itertools.combinations(range(8), 4):
    T = np.zeros(8, dtype=int)
    T[list(groupe_offre)] = 1
    y = np.where(T == 1, clients["y1"], clients["y0"])
    estimations.append(y[T == 1].mean() - y[T == 0].mean())
estimations = np.array(estimations)
print(len(estimations), "attributions possibles")
print("moyenne des 70 différences naïves :", estimations.mean(), "  | ATE réel :", ate)
print("plus petite / plus grande :", estimations.min(), "/", estimations.max())
```
<!--sortie-->
```text
70 attributions possibles
moyenne des 70 différences naïves : 12.5   | ATE réel : 12.5
plus petite / plus grande : -60.0 / 85.0
```

**Étape 2 — l'étude observationnelle : ciblage de la gérante contre attributions aléatoires.** Le fichier `ch07-observationnel-verite.csv` contient les deux dépenses potentielles (information inaccessible en pratique).

```python
obs = pd.read_csv("donnees/ch07-observationnel.csv")
verite = pd.read_csv("donnees/ch07-observationnel-verite.csv")
d = obs.merge(verite, on="id_client")
ate_vrai = (d["y1"] - d["y0"]).mean()
att_vrai = (d["y1"] - d["y0"])[d["offre"] == 1].mean()
print(f"{len(d)} clients ; {d['offre'].mean():.1%} ont reçu l'offre")
print(f"ATE vrai = {ate_vrai:.2f} €   ATT vrai = {att_vrai:.2f} €")

naif = d.loc[d["offre"] == 1, "depense"].mean() - d.loc[d["offre"] == 0, "depense"].mean()
print(f"Différence naïve avec le ciblage de la gérante : {naif:.2f} €")

rng = np.random.default_rng(1)
diffs_alea = []
for _ in range(2000):
    T = rng.permutation(d["offre"].to_numpy())           # même proportion de traités, mais tirés au sort
    y = np.where(T == 1, d["y1"], d["y0"])
    diffs_alea.append(y[T == 1].mean() - y[T == 0].mean())
diffs_alea = np.array(diffs_alea)
print(f"Avec attribution aléatoire : moyenne {diffs_alea.mean():.2f}, écart-type {diffs_alea.std():.2f}")
print(f"  95 % des tirages entre {np.percentile(diffs_alea, 2.5):.1f} et {np.percentile(diffs_alea, 97.5):.1f}")
```
<!--sortie-->
```text
4000 clients ; 46.2% ont reçu l'offre
ATE vrai = 15.53 €   ATT vrai = 16.64 €
Différence naïve avec le ciblage de la gérante : 50.50 €
Avec attribution aléatoire : moyenne 15.46, écart-type 2.26
  95 % des tirages entre 11.1 et 19.9
```

*Lecture.* Avec le ciblage de la gérante, la différence naïve est de 50,5 € alors que l'ATE vrai vaut 15,5 € ; avec des attributions tirées au sort, elle se répartit autour de 15,5 (écart-type 2,3). Le tableau `d` ainsi construit sert aux applications 7.5 à 7.7.

### Application 7.3 — Analyser l'expérience de l'offre de bienvenue (section 7.1.4)

**Objectif.** Analyser une expérience randomisée comme le ferait un data scientist : vérifier l'équilibre, estimer l'effet sur le rachat et sur la dépense, avec intervalle de confiance, puis comparer à la vérité.

**Étape 1 — la randomisation a-t-elle « marché » ?** Tableau d'équilibre (différences moyennes standardisées, SMD) et tests.

```python
from scipy import stats

c = pd.read_csv("donnees/clients.csv")
traite = c[c["offre_bienvenue"] == 1]
temoin = c[c["offre_bienvenue"] == 0]
print("effectifs : offre =", len(traite), "| pas d'offre =", len(temoin))

def smd(x1, x0):
    return (x1.mean() - x0.mean()) / np.sqrt((x1.var(ddof=1) + x0.var(ddof=1)) / 2)

lignes = [("age", smd(traite["age"], temoin["age"]), traite["age"].mean(), temoin["age"].mean())]
for modalite in ["Réseaux", "Site", "Boutique"]:
    u1 = (traite["canal_acquisition"] == modalite).astype(float)
    u0 = (temoin["canal_acquisition"] == modalite).astype(float)
    lignes.append((f"canal = {modalite}", smd(u1, u0), u1.mean(), u0.mean()))
for v in sorted(c["ville"].unique()):
    u1 = (traite["ville"] == v).astype(float)
    u0 = (temoin["ville"] == v).astype(float)
    lignes.append((f"ville = {v}", smd(u1, u0), u1.mean(), u0.mean()))
equilibre = pd.DataFrame(lignes, columns=["variable", "SMD", "moy. offre", "moy. témoin"]).round(3)
print(equilibre.to_string(index=False))
print()
print("p-valeur (Welch) pour l'âge :", round(stats.ttest_ind(traite["age"], temoin["age"], equal_var=False).pvalue, 3))
print("p-valeur (khi-deux) pour le canal :", round(stats.chi2_contingency(pd.crosstab(c["canal_acquisition"], c["offre_bienvenue"]))[1], 3))
print("p-valeur (khi-deux) pour la ville :", round(stats.chi2_contingency(pd.crosstab(c["ville"], c["offre_bienvenue"]))[1], 3))
```
<!--sortie-->
```text
effectifs : offre = 1015 | pas d'offre = 985
        variable    SMD  moy. offre  moy. témoin
             age -0.068      35.397       36.114
 canal = Réseaux  0.020       0.413        0.403
    canal = Site  0.029       0.347        0.333
canal = Boutique -0.054       0.240        0.264
   ville = Autre -0.021       0.147        0.154
 ville = Ville A  0.016       0.106        0.102
 ville = Ville B -0.011       0.124        0.128
 ville = Ville C -0.012       0.139        0.143
 ville = Ville D -0.011       0.167        0.171
 ville = Ville E  0.032       0.317        0.303

p-valeur (Welch) pour l'âge : 0.128
p-valeur (khi-deux) pour le canal : 0.473
p-valeur (khi-deux) pour la ville : 0.976
```

**Étape 2 — l'effet sur le rachat à 12 mois** (différence de proportions et intervalle de Wald).

```python
n1, n0 = len(traite), len(temoin)
p1, p0 = traite["rachat_12m"].mean(), temoin["rachat_12m"].mean()
ate_rachat = p1 - p0
se = np.sqrt(p1 * (1 - p1) / n1 + p0 * (1 - p0) / n0)
print(f"rachat avec offre : {p1:.3f}   sans offre : {p0:.3f}")
print(f"effet moyen : {ate_rachat:.3f}  (IC 95 % : {ate_rachat - 1.96 * se:.3f} ; {ate_rachat + 1.96 * se:.3f})")
print(f"effet relatif : {ate_rachat / p0:+.1%}   | une offre de plus = {ate_rachat:.3f} rachat de plus en moyenne,")
print(f"soit environ 1 client de plus qui rachète pour {1 / ate_rachat:.1f} offres envoyées")
```
<!--sortie-->
```text
rachat avec offre : 0.569   sans offre : 0.448
effet moyen : 0.122  (IC 95 % : 0.078 ; 0.165)
effet relatif : +27.2%   | une offre de plus = 0.122 rachat de plus en moyenne,
soit environ 1 client de plus qui rachète pour 8.2 offres envoyées
```

**Étape 3 — le même effet par régression logistique**, en passant du rapport de cotes à une différence de probabilités (effet marginal moyen).

```python
import statsmodels.formula.api as smf

logit = smf.logit("rachat_12m ~ offre_bienvenue", data=c).fit(disp=0)
print("coefficient (log-cote) :", round(logit.params["offre_bienvenue"], 3), "| rapport de cotes :", round(np.exp(logit.params["offre_bienvenue"]), 2))
marg = logit.get_margeff(dummy=True).summary_frame().iloc[0]      # dummy=True : vraie différence de probabilités 1 - 0
print(f"effet marginal moyen : {marg['dy/dx']:.3f}  (IC 95 % : {marg['Conf. Int. Low']:.3f} ; {marg['Cont. Int. Hi.']:.3f})")
```
<!--sortie-->
```text
coefficient (log-cote) : 0.49 | rapport de cotes : 1.63
effet marginal moyen : 0.122  (IC 95 % : 0.078 ; 0.165)
```

**Étape 4 — l'effet sur la dépense annuelle** (test de Welch), puis **l'ajustement sur covariables**, qui n'améliore ici que la précision.

```python
d1, d0 = traite["depense_annuelle"], temoin["depense_annuelle"]
res = stats.ttest_ind(d1, d0, equal_var=False)
ic = res.confidence_interval(0.95)
print(f"dépense moyenne avec offre : {d1.mean():.1f} €   sans offre : {d0.mean():.1f} €")
print(f"effet moyen : {d1.mean() - d0.mean():+.1f} €  (IC 95 % : {ic.low:.1f} ; {ic.high:.1f})   p = {res.pvalue:.2f}")
```
<!--sortie-->
```text
dépense moyenne avec offre : 243.5 €   sans offre : 250.5 €
effet moyen : -7.0 €  (IC 95 % : -33.1 ; 19.0)   p = 0.60
```

```python
simple = smf.ols("rachat_12m ~ offre_bienvenue", data=c).fit(cov_type="HC1")
ajuste = smf.ols("rachat_12m ~ offre_bienvenue + age + C(canal_acquisition) + C(ville)", data=c).fit(cov_type="HC1")
for nom, m in [("sans covariables", simple), ("avec covariables ", ajuste)]:
    b, s = m.params["offre_bienvenue"], m.bse["offre_bienvenue"]
    print(f"{nom} : effet = {b:.3f}   erreur-type = {s:.4f}   IC 95 % = [{b - 1.96 * s:.3f} ; {b + 1.96 * s:.3f}]")
```
<!--sortie-->
```text
sans covariables : effet = 0.122   erreur-type = 0.0222   IC 95 % = [0.078 ; 0.165]
avec covariables  : effet = 0.121   erreur-type = 0.0221   IC 95 % = [0.077 ; 0.164]
```

**Étape 5 — la vérité.** Dans le simulateur, l'offre ajoute 0,55 à la log-cote du rachat et n'a aucun effet sur la dépense. On calcule l'effet moyen vrai en probabilité sur une grande population simulée.

```python
rng = np.random.default_rng(1)
N = 400_000
age = np.clip(np.round(rng.normal(36, 11, N)), 18, 75)
canal = rng.choice(["Réseaux", "Site", "Boutique"], N, p=[0.40, 0.35, 0.25])
z = rng.normal(size=(N, 2))
F1 = z[:, 0]                                    # facteurs latents du simulateur (corrélation 0,3)
F2 = 0.3 * z[:, 0] + np.sqrt(1 - 0.3 ** 2) * z[:, 1]
eta = -0.35 + 0.45 * F1 + 0.35 * F2 - 0.015 * (age - 36) + 0.3 * (canal == "Boutique")
expit = lambda x: 1 / (1 + np.exp(-x))
print(f"effet moyen vrai sur la probabilité de rachat : {(expit(eta + 0.55) - expit(eta)).mean():.4f}")
print("effet vrai sur la dépense annuelle : 0 (par construction du simulateur)")
```
<!--sortie-->
```text
effet moyen vrai sur la probabilité de rachat : 0.1239
effet vrai sur la dépense annuelle : 0 (par construction du simulateur)
```

*Lecture.* L'estimation expérimentale (0,122) est très proche de la vérité (0,124) ; l'effet sur la dépense (−7,0 €, intervalle de −33,1 à +19,0) est compatible avec zéro, et l'on sait ici qu'il est nul.

**Pour aller plus loin.** Estimez l'effet de l'offre sur le rachat dans chaque canal (c'est l'exercice 7.2) et demandez-vous ce que vaut la comparaison entre canaux.

### Application 7.4 — Simpson, médiateur et collision : simuler les trois pièges (sections 7.1.6 à 7.1.8)

**Objectif.** Voir à l'œuvre, sur des données simulées, les trois structures élémentaires d'un graphe causal et ce que fait (ou ne fait pas) un ajustement par régression.

**Étape 1 — la fourche (paradoxe de Simpson).** Le tableau de la section 7.1.6 (240 clients), analysé avec et sans ajustement sur le canal.

```python
simpson = pd.DataFrame({
    "canal": ["Boutique", "Boutique", "Réseaux", "Réseaux"],
    "offre": [1, 0, 1, 0],
    "clients": [20, 100, 100, 20],
    "rachats": [18, 80, 40, 6],
})
simpson["taux"] = simpson["rachats"] / simpson["clients"]
glob = simpson.groupby("offre")[["clients", "rachats"]].sum()
print("global :", (glob["rachats"] / glob["clients"]).round(3).to_dict())

par_canal = simpson.pivot(index="canal", columns="offre", values="taux")
par_canal["effet"] = par_canal[1] - par_canal[0]
poids = simpson.groupby("canal")["clients"].sum() / simpson["clients"].sum()
print(par_canal.round(3))
print("poids des canaux :", poids.round(2).to_dict())
print("effet standardisé :", round((par_canal["effet"] * poids).sum(), 3))

# La même chose avec une régression logistique sur les 240 clients (une ligne par client)
lignes = pd.DataFrame([{"canal": r.canal, "offre": r.offre, "rachat": int(k < r.rachats)}
                       for r in simpson.itertuples() for k in range(r.clients)])
print(len(lignes), "clients, taux de rachat global :", round(lignes["rachat"].mean(), 3))
m_brut = smf.logit("rachat ~ offre", lignes).fit(disp=0)
m_ajuste = smf.logit("rachat ~ offre + C(canal)", lignes).fit(disp=0)
print(f"\ncoefficient de l'offre SANS ajustement sur le canal : {m_brut.params['offre']:+.2f}")
print(f"coefficient de l'offre AVEC ajustement sur le canal : {m_ajuste.params['offre']:+.2f}")
```
<!--sortie-->
```text
global : {0: 0.717, 1: 0.483}
offre       0    1  effet
canal                    
Boutique  0.8  0.9    0.1
Réseaux   0.3  0.4    0.1
poids des canaux : {'Boutique': 0.5, 'Réseaux': 0.5}
effet standardisé : 0.1
240 clients, taux de rachat global : 0.6

coefficient de l'offre SANS ajustement sur le canal : -0.99
coefficient de l'offre AVEC ajustement sur le canal : +0.56
```

**Étape 2 — la chaîne : ne pas ajuster sur un médiateur.** L'offre est randomisée ; elle agit par un code promotionnel (30 €) et directement (8 €).

```python
rng = np.random.default_rng(71)
n = 100_000
motivation = rng.normal(size=n)                               # inobservée dans la vie réelle
offre = rng.integers(0, 2, n)                                 # randomisée
p_code = expit(0.4 + 0.9 * motivation)                        # un code n'existe que si l'on a reçu l'offre
code_si_offre = rng.random(n) < p_code
code = offre * code_si_offre                                  # médiateur : 1 si offre ET code utilisé
bruit = rng.normal(0, 25, n)
depense = 100 + 8 * offre + 30 * code + 20 * motivation + bruit

y1 = 100 + 8 + 30 * code_si_offre + 20 * motivation + bruit
y0 = 100 + 20 * motivation + bruit
print(f"effet total vrai : {(y1 - y0).mean():.2f} €   (= 8 + 30 x {code_si_offre.mean():.2f}, où {code_si_offre.mean():.0%} des clients utilisent le code s'ils reçoivent l'offre)")

df_m = pd.DataFrame({"depense": depense, "offre": offre, "code": code})
total = smf.ols("depense ~ offre", df_m).fit()
sur_ajuste = smf.ols("depense ~ offre + code", df_m).fit()
print(f"sans ajuster sur le médiateur : effet de l'offre = {total.params['offre']:.2f}  (erreur-type {total.bse['offre']:.2f})")
print(f"en ajustant sur le médiateur  : effet de l'offre = {sur_ajuste.params['offre']:.2f}  (erreur-type {sur_ajuste.bse['offre']:.2f})")

# Pourquoi ? Parmi les clients SANS code, les traités et les non-traités n'ont pas la même motivation :
m_traites_sans_code = motivation[(offre == 1) & (code == 0)].mean()
m_temoins = motivation[offre == 0].mean()
print(f"motivation moyenne, offre reçue mais code non utilisé : {m_traites_sans_code:+.2f}   | pas d'offre : {m_temoins:+.2f}")
print(f"écart de dépense dû à cette seule différence de motivation : {20 * (m_traites_sans_code - m_temoins):+.1f} €")
```
<!--sortie-->
```text
effet total vrai : 25.47 €   (= 8 + 30 x 0.58, où 58% des clients utilisent le code s'ils reçoivent l'offre)
sans ajuster sur le médiateur : effet de l'offre = 25.62  (erreur-type 0.22)
en ajustant sur le médiateur  : effet de l'offre = -0.80  (erreur-type 0.26)
motivation moyenne, offre reçue mais code non utilisé : -0.45   | pas d'offre : -0.00
écart de dépense dû à cette seule différence de motivation : -9.0 €
```

**Étape 3 — la collision : ne pas conditionner sur un effet commun.** Qualité et attrait sont indépendants, mais seuls les prototypes réussis sont gardés au catalogue.

```python
rng = np.random.default_rng(72)
n = 6000
qualite = rng.normal(size=n)
attrait = rng.normal(size=n)                                  # indépendants par construction
score = qualite + attrait + rng.normal(0, 0.5, n)
retenu = score > 0.8                                          # seuls les prototypes réussis sont gardés

print(f"corrélation qualité-attrait, tous les prototypes : {np.corrcoef(qualite, attrait)[0, 1]:+.3f}")
print(f"corrélation qualité-attrait, produits retenus     : {np.corrcoef(qualite[retenu], attrait[retenu])[0, 1]:+.3f}")
print(f"({retenu.sum()} produits retenus sur {n})")

# Ce que ferait un analyste qui n'observe QUE le catalogue :
cat = pd.DataFrame({"qualite": qualite, "attrait": attrait, "retenu": retenu})
brut = smf.ols("qualite ~ attrait", cat).fit()
dans_catalogue = smf.ols("qualite ~ attrait", cat[cat.retenu]).fit()
print(f"pente de la qualité sur l'attrait, tous : {brut.params['attrait']:+.3f} | catalogue seulement : {dans_catalogue.params['attrait']:+.3f}")
```
<!--sortie-->
```text
corrélation qualité-attrait, tous les prototypes : +0.011
corrélation qualité-attrait, produits retenus     : -0.479
(1811 produits retenus sur 6000)
pente de la qualité sur l'attrait, tous : +0.012 | catalogue seulement : -0.494
```

*Lecture.* Sans ajustement sur le canal, le coefficient de l'offre est −0,99 ; avec le canal, +0,56. En ajustant sur le médiateur, l'estimation tombe à −0,8 € alors que l'effet total est de 25,5 € et l'effet direct de 8 €. Sur les seuls produits retenus, la corrélation qualité-attrait passe de +0,01 à −0,48.

### Application 7.5 — L'échelle d'ajustement sur l'étude observationnelle (section 7.1.9)

**Objectif.** Montrer par une suite de régressions que seul l'ensemble d'ajustement qui bloque tous les chemins de confusion (âge, canal **et** engagement) retrouve la vérité. On réutilise le tableau `d` de l'application 7.2.

```python
modeles = [
    ("aucun ajustement", "depense ~ offre"),
    ("+ âge", "depense ~ offre + age"),
    ("+ âge + canal", "depense ~ offre + age + C(canal)"),
    ("+ âge + canal + engagement", "depense ~ offre + age + C(canal) + engagement"),
]
lignes = []
for nom, formule in modeles:
    m = smf.ols(formule, d).fit()
    b, s = m.params["offre"], m.bse["offre"]
    lignes.append({"ensemble d'ajustement": nom, "effet estimé": b, "IC95 bas": b - 1.96 * s, "IC95 haut": b + 1.96 * s})
tab = pd.DataFrame(lignes).round(1)
print(tab.to_string(index=False))
print(f"\nvérité : ATE = {ate_vrai:.1f}   ATT = {att_vrai:.1f}")
```
<!--sortie-->
```text
     ensemble d'ajustement  effet estimé  IC95 bas  IC95 haut
          aucun ajustement          50.5      46.3       54.7
                     + âge          46.1      41.9       50.3
             + âge + canal          47.0      42.8       51.2
+ âge + canal + engagement          14.8      11.0       18.7

vérité : ATE = 15.5   ATT = 16.6
```

*Lecture.* Tant que l'engagement manque, l'estimation reste entre 46 et 51 € (vérité : ATE = 15,5 €) ; avec les trois variables, elle tombe à 14,8 € avec un intervalle de 11,0 à 18,7.

### Application 7.6 — Le score de propension : estimation, chevauchement, appariement (sections 7.2.1 à 7.2.3)

**Objectif.** Estimer l'effet de l'offre ciblée avec un score de propension : malédiction de la dimension, estimation du score, diagnostic de chevauchement, appariement au plus proche voisin avec calibre, bootstrap et équilibre des covariables.

**Étape 1 — pourquoi un score ?** Avec trois covariables seulement, combien de clients ont un « jumeau » de l'autre groupe ?

```python
cellules = d.groupby(["age", "canal", "engagement"])["offre"].agg(["size", "sum"])
mixtes = cellules[(cellules["sum"] > 0) & (cellules["sum"] < cellules["size"])]
print(f"{len(d)} clients répartis en {len(cellules)} cellules (âge x canal x engagement)")
print(f"cellules où l'on trouve à la fois un client avec offre et un sans : {len(mixtes)}")
print(f"clients se trouvant dans une telle cellule : {int(mixtes['size'].sum())} sur {len(d)}")
```
<!--sortie-->
```text
4000 clients répartis en 2923 cellules (âge x canal x engagement)
cellules où l'on trouve à la fois un client avec offre et un sans : 413
clients se trouvant dans une telle cellule : 1035 sur 4000
```

**Étape 2 — estimer le score et regarder le chevauchement.**

```python
from sklearn.metrics import roc_auc_score

modele_ps = smf.logit("offre ~ age + C(canal) + engagement", data=d).fit(disp=0)
print(modele_ps.params.round(3).to_string())
d["ps"] = modele_ps.predict(d)
print(f"\nAUC du modèle d'attribution : {roc_auc_score(d['offre'], d['ps']):.3f}")
print(d.groupby("offre")["ps"].describe().round(3).to_string())
```
<!--sortie-->
```text
Intercept             -2.462
C(canal)[T.Réseaux]    0.454
C(canal)[T.Site]      -0.060
age                   -0.032
engagement             0.063

AUC du modèle d'attribution : 0.761
        count   mean    std    min    25%    50%    75%    max
offre                                                         
0      2150.0  0.368  0.198  0.021  0.207  0.342  0.502  0.966
1      1850.0  0.572  0.204  0.049  0.423  0.582  0.731  0.969
```

```python
bas_commun = max(d.loc[d.offre == 1, "ps"].min(), d.loc[d.offre == 0, "ps"].min())
haut_commun = min(d.loc[d.offre == 1, "ps"].max(), d.loc[d.offre == 0, "ps"].max())
hors = ((d["ps"] < bas_commun) | (d["ps"] > haut_commun)).sum()
print(f"support commun : [{bas_commun:.3f} ; {haut_commun:.3f}]  -> {hors} clients en dehors")
```
<!--sortie-->
```text
support commun : [0.049 ; 0.966]  -> 22 clients en dehors
```

**Étape 3 — l'appariement** (au plus proche voisin sur le logit du score, avec remise et calibre de 0,2 écart-type).

```python
from sklearn.neighbors import NearestNeighbors

def apparier(df, calibre=0.2):
    """Renvoie (effet ATT, nombre de traités appariés, indices des témoins appariés)."""
    logit_ps = np.log(df["ps"] / (1 - df["ps"])).to_numpy()
    T = df["offre"].to_numpy()
    traites, temoins = np.where(T == 1)[0], np.where(T == 0)[0]
    nn = NearestNeighbors(n_neighbors=1).fit(logit_ps[temoins].reshape(-1, 1))
    dist, pos = nn.kneighbors(logit_ps[traites].reshape(-1, 1))
    ok = dist[:, 0] <= calibre * logit_ps.std()
    appar_t = traites[ok]
    appar_c = temoins[pos[ok, 0]]
    y = df["depense"].to_numpy()
    return (y[appar_t] - y[appar_c]).mean(), ok.sum(), appar_t, appar_c

att_appar, n_appar, idx_t, idx_c = apparier(d)
print(f"{n_appar} traités appariés sur {int(d['offre'].sum())}")
print(f"témoins distincts utilisés : {len(np.unique(idx_c))} (un même témoin sert en moyenne {len(idx_c) / len(np.unique(idx_c)):.1f} fois)")
print(f"effet estimé par appariement (ATT) : {att_appar:.2f} €   | ATT vrai : {att_vrai:.2f}")
```
<!--sortie-->
```text
1843 traités appariés sur 1850
témoins distincts utilisés : 814 (un même témoin sert en moyenne 2.3 fois)
effet estimé par appariement (ATT) : 14.41 €   | ATT vrai : 16.64
```

**Étape 4 — l'incertitude par bootstrap** : on refait *toute* la procédure (estimation du score comprise) sur chaque échantillon rééchantillonné.

```python
def ps_et_appariement(df):
    m = smf.logit("offre ~ age + C(canal) + engagement", data=df).fit(disp=0)
    df = df.assign(ps=m.predict(df))
    return apparier(df)[0]

rng = np.random.default_rng(2)
boot = []
for _ in range(200):
    echantillon = d.sample(len(d), replace=True, random_state=int(rng.integers(1_000_000_000))).reset_index(drop=True)
    boot.append(ps_et_appariement(echantillon))
boot = np.array(boot)
print(f"erreur-type bootstrap : {boot.std():.2f}   IC 95 % (percentiles) : [{np.percentile(boot, 2.5):.1f} ; {np.percentile(boot, 97.5):.1f}]")
```
<!--sortie-->
```text
erreur-type bootstrap : 3.66   IC 95 % (percentiles) : [6.6 ; 20.2]
```

**Étape 5 — l'équilibre avant/après appariement** (différences moyennes standardisées pondérées).

```python
def smd_pondere(x, T, w):
    """Différence moyenne standardisée entre traités (T=1) et témoins (T=0), avec poids w."""
    x, T, w = np.asarray(x, float), np.asarray(T), np.asarray(w, float)
    m1 = np.average(x[T == 1], weights=w[T == 1])
    m0 = np.average(x[T == 0], weights=w[T == 0])
    v1 = np.average((x[T == 1] - m1) ** 2, weights=w[T == 1])
    v0 = np.average((x[T == 0] - m0) ** 2, weights=w[T == 0])
    return (m1 - m0) / np.sqrt((v1 + v0) / 2)

covariables = pd.DataFrame({
    "âge": d["age"], "engagement": d["engagement"],
    "canal = Réseaux": (d["canal"] == "Réseaux").astype(float),
    "canal = Site": (d["canal"] == "Site").astype(float),
    "canal = Boutique": (d["canal"] == "Boutique").astype(float)})

poids_appar = np.zeros(len(d))
poids_appar[idx_t] += 1                                   # chaque traité apparié compte une fois
np.add.at(poids_appar, idx_c, 1)                          # chaque témoin compte autant de fois qu'il est utilisé
avant = {c: smd_pondere(covariables[c], d["offre"], np.ones(len(d))) for c in covariables}
apres_appar = {c: smd_pondere(covariables[c], d["offre"], poids_appar) for c in covariables}
print(pd.DataFrame({"SMD avant": avant, "SMD après appariement": apres_appar}).round(3).to_string())
```
<!--sortie-->
```text
                  SMD avant  SMD après appariement
âge                  -0.336                  0.003
engagement            0.915                  0.006
canal = Réseaux       0.306                 -0.013
canal = Site         -0.204                  0.041
canal = Boutique     -0.118                 -0.028
```

*Lecture.* 1 843 traités sur 1 850 sont appariés ; l'ATT estimé est de 14,4 € (vrai : 16,6 €) avec un intervalle bootstrap de 6,6 à 20,2 € ; après appariement, toutes les SMD sont inférieures à 0,05.

### Application 7.7 — Pondération, estimateur doublement robuste et confusion mal mesurée (sections 7.2.4 à 7.2.6)

**Objectif.** Estimer l'ATE et l'ATT par pondération par l'inverse du score (IPW), vérifier les poids, construire l'estimateur doublement robuste, le mettre à l'épreuve en rendant l'un des deux modèles faux, et mesurer l'effet d'un facteur de confusion mal mesuré. On réutilise les objets des applications 7.2 et 7.6.

**Étape 1 — IPW : ATE (Horvitz-Thompson et version normalisée) et ATT.**

```python
e = d["ps"].to_numpy()
T = d["offre"].to_numpy()
Y = d["depense"].to_numpy()

w_ate = np.where(T == 1, 1 / e, 1 / (1 - e))
ht = np.mean(T * Y / e - (1 - T) * Y / (1 - e))                                  # Horvitz-Thompson
hajek = np.average(Y[T == 1], weights=w_ate[T == 1]) - np.average(Y[T == 0], weights=w_ate[T == 0])
w_att = np.where(T == 1, 1.0, e / (1 - e))
att_ipw = np.average(Y[T == 1]) - np.average(Y[T == 0], weights=w_att[T == 0])

print(f"ATE par IPW (Horvitz-Thompson) : {ht:.2f}")
print(f"ATE par IPW (normalisé)        : {hajek:.2f}   | ATE vrai : {ate_vrai:.2f}")
print(f"ATT par IPW                    : {att_ipw:.2f}   | ATT vrai : {att_vrai:.2f}")
```
<!--sortie-->
```text
ATE par IPW (Horvitz-Thompson) : 13.44
ATE par IPW (normalisé)        : 14.36   | ATE vrai : 15.53
ATT par IPW                    : 11.84   | ATT vrai : 16.64
```

**Étape 2 — les poids sont-ils raisonnables ?** Effectif effectif et troncature des poids.

```python
def effectif_effectif(w):
    return w.sum() ** 2 / (w ** 2).sum()

for nom, mask in [("avec offre", T == 1), ("sans offre", T == 0)]:
    w = w_ate[mask]
    print(f"{nom} : n = {mask.sum()}, poids min/médian/max = {w.min():.2f} / {np.median(w):.2f} / {w.max():.1f}, effectif effectif = {effectif_effectif(w):.0f}")

# Troncature : on borne les poids aux percentiles 1 et 99
bas, haut = np.percentile(w_ate, [1, 99])
w_tronque = np.clip(w_ate, bas, haut)
hajek_tronque = np.average(Y[T == 1], weights=w_tronque[T == 1]) - np.average(Y[T == 0], weights=w_tronque[T == 0])
print(f"\nATE par IPW avec poids tronqués à [{bas:.2f} ; {haut:.1f}] : {hajek_tronque:.2f}")
```
<!--sortie-->
```text
avec offre : n = 1850, poids min/médian/max = 1.03 / 1.72 / 20.5, effectif effectif = 1261
sans offre : n = 2150, poids min/médian/max = 1.02 / 1.52 / 29.3, effectif effectif = 1508

ATE par IPW avec poids tronqués à [1.06 ; 7.4] : 17.52
```

**Étape 3 — l'incertitude par bootstrap, puis l'équilibre après pondération.**

```python
def ipw_ate_att(df):
    e_b = smf.logit("offre ~ age + C(canal) + engagement", data=df).fit(disp=0).predict(df).to_numpy()
    Tb, Yb = df["offre"].to_numpy(), df["depense"].to_numpy()
    w = np.where(Tb == 1, 1 / e_b, 1 / (1 - e_b))
    ate_b = np.average(Yb[Tb == 1], weights=w[Tb == 1]) - np.average(Yb[Tb == 0], weights=w[Tb == 0])
    att_b = Yb[Tb == 1].mean() - np.average(Yb[Tb == 0], weights=(e_b / (1 - e_b))[Tb == 0])
    return ate_b, att_b

rng = np.random.default_rng(4)
boot_ipw = np.array([ipw_ate_att(d.sample(len(d), replace=True, random_state=int(rng.integers(1_000_000_000))).reset_index(drop=True))
                     for _ in range(200)])
for nom, i, vrai in [("ATE", 0, ate_vrai), ("ATT", 1, att_vrai)]:
    b = boot_ipw[:, i]
    print(f"IPW {nom} : erreur-type bootstrap {b.std():.2f}   IC 95 % : [{np.percentile(b, 2.5):.1f} ; {np.percentile(b, 97.5):.1f}]   (vérité {vrai:.1f})")
```
<!--sortie-->
```text
IPW ATE : erreur-type bootstrap 2.50   IC 95 % : [9.6 ; 19.1]   (vérité 15.5)
IPW ATT : erreur-type bootstrap 3.37   IC 95 % : [4.7 ; 17.8]   (vérité 16.6)
```

```python
apres_ipw = {c: smd_pondere(covariables[c], T, w_ate) for c in covariables}
print(pd.DataFrame({"SMD avant": avant, "SMD après IPW": apres_ipw}).round(3).to_string())
```
<!--sortie-->
```text
                  SMD avant  SMD après IPW
âge                  -0.336         -0.030
engagement            0.915         -0.022
canal = Réseaux       0.306         -0.003
canal = Site         -0.204         -0.001
canal = Boutique     -0.118          0.004
```

**Étape 4 — l'estimateur doublement robuste, mis à l'épreuve.** On rend volontairement faux l'un des deux modèles (résultat sans covariables, ou score constant).

```python
X = np.column_stack([np.ones(len(d)), d["age"], (d["canal"] == "Réseaux"), (d["canal"] == "Site"), d["engagement"]]).astype(float)

def mu_hat(X, Y, T, bon_modele):
    """Prédictions de E[Y | X, T=t] pour t = 0 et 1, par moindres carrés séparés dans chaque groupe."""
    sorties = []
    for t in (0, 1):
        cols = slice(None) if bon_modele else slice(0, 1)          # mauvais modèle = constante seule
        beta, *_ = np.linalg.lstsq(X[T == t][:, cols], Y[T == t], rcond=None)
        sorties.append(X[:, cols] @ beta)
    return sorties

def e_hat(X, T, bon_modele):
    if not bon_modele:
        return np.full(len(T), T.mean())
    m = smf.logit("offre ~ age + C(canal) + engagement", data=d).fit(disp=0)
    return m.predict(d).to_numpy()

```

```python
def estimateurs(bon_resultat, bon_score):
    mu0, mu1 = mu_hat(X, Y, T, bon_resultat)
    e = e_hat(X, T, bon_score)
    regression = np.mean(mu1 - mu0)
    ipw = np.average(Y[T == 1], weights=1 / e[T == 1]) - np.average(Y[T == 0], weights=1 / (1 - e[T == 0]))
    aipw = np.mean(mu1 - mu0 + T * (Y - mu1) / e - (1 - T) * (Y - mu0) / (1 - e))
    return regression, ipw, aipw

lignes = []
for br in (True, False):
    for bs in (True, False):
        reg, ipw, aipw = estimateurs(br, bs)
        lignes.append({"modèle de résultat": "correct" if br else "faux", "modèle d'attribution": "correct" if bs else "faux",
                       "régression": reg, "IPW": ipw, "doublement robuste": aipw})
print(pd.DataFrame(lignes).round(1).to_string(index=False))
print(f"\nATE vrai : {ate_vrai:.1f}   (différence naïve : {Y[T == 1].mean() - Y[T == 0].mean():.1f})")
```
<!--sortie-->
```text
modèle de résultat modèle d'attribution  régression  IPW  doublement robuste
           correct              correct        15.0 14.4                14.9
           correct                 faux        15.0 50.5                15.0
              faux              correct        50.5 14.4                14.3
              faux                 faux        50.5 50.5                50.5

ATE vrai : 15.5   (différence naïve : 50.5)
```

**Étape 5 — l'estimation principale par AIPW, avec son bootstrap.**

```python
def aipw_complet(df):
    Xb = np.column_stack([np.ones(len(df)), df["age"], (df["canal"] == "Réseaux"), (df["canal"] == "Site"), df["engagement"]]).astype(float)
    Tb, Yb = df["offre"].to_numpy(), df["depense"].to_numpy()
    mu0, mu1 = mu_hat(Xb, Yb, Tb, True)
    eb = smf.logit("offre ~ age + C(canal) + engagement", data=df).fit(disp=0).predict(df).to_numpy()
    return np.mean(mu1 - mu0 + Tb * (Yb - mu1) / eb - (1 - Tb) * (Yb - mu0) / (1 - eb))

est = aipw_complet(d)
rng = np.random.default_rng(3)
boot = np.array([aipw_complet(d.sample(len(d), replace=True, random_state=int(rng.integers(1_000_000_000))).reset_index(drop=True))
                 for _ in range(200)])
print(f"ATE doublement robuste : {est:.2f}   erreur-type bootstrap : {boot.std():.2f}   IC 95 % : [{est - 1.96 * boot.std():.1f} ; {est + 1.96 * boot.std():.1f}]")
print(f"ATE vrai : {ate_vrai:.2f}")
```
<!--sortie-->
```text
ATE doublement robuste : 14.89   erreur-type bootstrap : 2.44   IC 95 % : [10.1 ; 19.7]
ATE vrai : 15.53
```

**Étape 6 — récapitulatif, puis confusion mal mesurée.** On cache l'engagement, ou on ne le mesure qu'avec du bruit.

```python
recap = pd.DataFrame({
    "méthode": ["différence naïve", "régression (7.1.9)", "IPW (ATE)", "doublement robuste (ATE)", "appariement (ATT)", "IPW (ATT)"],
    "estimation": [Y[T == 1].mean() - Y[T == 0].mean(),
                   smf.ols("depense ~ offre + age + C(canal) + engagement", d).fit().params["offre"],
                   hajek, est, att_appar, att_ipw],
    "vérité": [ate_vrai, ate_vrai, ate_vrai, ate_vrai, att_vrai, att_vrai]}).round(1)
print(recap.to_string(index=False))
```
<!--sortie-->
```text
                 méthode  estimation  vérité
        différence naïve        50.5    15.5
      régression (7.1.9)        14.8    15.5
               IPW (ATE)        14.4    15.5
doublement robuste (ATE)        14.9    15.5
       appariement (ATT)        14.4    16.6
               IPW (ATT)        11.8    16.6
```

```python
def estimation_aipw_avec_engagement(bruit_sd, graine=5):
    """AIPW quand l'engagement n'est connu qu'avec un bruit gaussien d'écart-type bruit_sd (None = engagement caché)."""
    df = d.copy()
    if bruit_sd is None:
        formule_ps = "offre ~ age + C(canal)"
        cols = [np.ones(len(df)), df["age"], (df["canal"] == "Réseaux"), (df["canal"] == "Site")]
    else:
        r = np.random.default_rng(graine)
        df["eng_mesure"] = df["engagement"] + r.normal(0, bruit_sd, len(df))
        formule_ps = "offre ~ age + C(canal) + eng_mesure"
        cols = [np.ones(len(df)), df["age"], (df["canal"] == "Réseaux"), (df["canal"] == "Site"), df["eng_mesure"]]
    Xb = np.column_stack(cols).astype(float)
    Tb, Yb = df["offre"].to_numpy(), df["depense"].to_numpy()
    mu0, mu1 = mu_hat(Xb, Yb, Tb, True)
    eb = smf.logit(formule_ps, data=df).fit(disp=0).predict(df).to_numpy()
    return np.mean(mu1 - mu0 + Tb * (Yb - mu1) / eb - (1 - Tb) * (Yb - mu0) / (1 - eb))

resultats = [("engagement parfaitement mesuré", estimation_aipw_avec_engagement(0.0))]
for sd in (15, 30, 60):
    resultats.append((f"engagement mesuré avec du bruit (écart-type {sd})", estimation_aipw_avec_engagement(sd)))
resultats.append(("engagement non observé", estimation_aipw_avec_engagement(None)))
print(pd.DataFrame(resultats, columns=["situation", "ATE doublement robuste"]).round(1).to_string(index=False))
print(f"\nATE vrai : {ate_vrai:.1f}")
print(f"écart-type de l'engagement lui-même : {d['engagement'].std():.1f}")
```
<!--sortie-->
```text
                                      situation  ATE doublement robuste
                 engagement parfaitement mesuré                    14.9
engagement mesuré avec du bruit (écart-type 15)                    32.5
engagement mesuré avec du bruit (écart-type 30)                    41.8
engagement mesuré avec du bruit (écart-type 60)                    45.6
                         engagement non observé                    46.9

ATE vrai : 15.5
écart-type de l'engagement lui-même : 15.5
```

*Lecture.* Les estimations de l'ATE se situent entre 14,4 et 14,9 € (vérité : 15,5), contre 50,5 € pour la différence naïve. Quand le modèle de résultat et le score sont tous deux faux, l'AIPW échoue aussi ; et quand l'engagement est mesuré avec un bruit de 15 (autant que son propre écart-type), l'estimation « doublement robuste » est déjà à 32,5 €.

### Application 7.8 — La différence de différences sur le panel de villes (section 7.3)

**Objectif.** Estimer l'effet d'une campagne lancée dans 8 villes sur 20, avec la DiD à la main, en logarithme, par régression à effets fixes (erreurs-types groupées), puis diagnostiquer l'hypothèse de tendances parallèles (étude d'événement, test placebo) et en voir la violation.

**Étape 1 — les données.** Le simulateur `panel_villes` est dans `build/sim_ch07.py` ; le fichier est chargé et vérifié.

```python
import sys
sys.path.insert(0, "build")
from sim_ch07 import panel_villes, iv                       # simulateurs du chapitre (graines fixes)

p = pd.read_csv("donnees/ch07-panel-villes.csv", parse_dates=["mois"])
regen = panel_villes()
regen["mois"] = pd.to_datetime(regen["mois"])
print("le simulateur reproduit exactement le fichier :", p.equals(regen))
p["apres"] = (p["t"] >= 18).astype(int)
p["vid"] = pd.factorize(p["ville"])[0]                       # identifiant numérique de ville (erreurs-types groupées)
print(f"{p['ville'].nunique()} villes, {p['t'].nunique()} mois, {len(p)} lignes ; {p.groupby('ville')['groupe_traite'].first().sum()} villes traitées")
```
<!--sortie-->
```text
le simulateur reproduit exactement le fichier : True
20 villes, 24 mois, 480 lignes ; 8 villes traitées
```

**Étape 2 — la DiD à la main** : moyennes avant/après dans chaque groupe, en niveau puis en logarithme, et le diagnostic de l'échelle.

```python
moy = p.groupby(["groupe_traite", "apres"])["commandes"].mean().unstack().round(1)
moy.index = ["témoins (12 villes)", "traitées (8 villes)"]
moy.columns = ["avant", "après"]
print(moy)
```
<!--sortie-->
```text
                     avant  après
témoins (12 villes)   30.6   36.1
traitées (8 villes)   46.9   63.0
```

```python
moyenne_mois = p.groupby(["groupe_traite", "mois"])["commandes"].mean().unstack(0)
moyenne_mois.columns = ["témoins", "traitées"]
debut = pd.Timestamp("2025-07-01")
```

```python
avant_lancement = moyenne_mois[moyenne_mois.index < debut]
ecart = avant_lancement["traitées"] - avant_lancement["témoins"]
rapport = avant_lancement["traitées"] / avant_lancement["témoins"]
print(f"écart de niveau entre les groupes : de {ecart.min():.1f} à {ecart.max():.1f} commandes selon le mois (moyenne {ecart.mean():.1f})")
print(f"rapport traitées / témoins        : de {rapport.min():.2f} à {rapport.max():.2f} selon le mois (moyenne {rapport.mean():.2f})")
print(f"variabilité relative (écart-type / moyenne) : écart {ecart.std() / ecart.mean():.0%}, rapport {rapport.std() / rapport.mean():.0%}")
```
<!--sortie-->
```text
écart de niveau entre les groupes : de 5.7 à 24.5 commandes selon le mois (moyenne 16.3)
rapport traitées / témoins        : de 1.25 à 1.77 selon le mois (moyenne 1.54)
variabilité relative (écart-type / moyenne) : écart 30%, rapport 9%
```

```python
lm = p.assign(log_cmd=np.log(p["commandes"])).groupby(["groupe_traite", "apres"])["log_cmd"].mean().unstack()
did_log = (lm.loc[1, 1] - lm.loc[1, 0]) - (lm.loc[0, 1] - lm.loc[0, 0])
print("moyennes du logarithme des commandes :")
print(lm.round(3).rename(index={0: "témoins", 1: "traitées"}, columns={0: "avant", 1: "après"}))
print(f"\nDiD en logarithme : {did_log:.3f}   soit un effet relatif de {np.exp(did_log) - 1:+.1%}")
print(f"(rappel : DiD en niveau = {(moy.iloc[1, 1] - moy.iloc[1, 0]) - (moy.iloc[0, 1] - moy.iloc[0, 0]):.1f} commandes par mois)")
```
<!--sortie-->
```text
moyennes du logarithme des commandes :
apres          avant  après
groupe_traite              
témoins        3.369  3.537
traitées       3.784  4.089

DiD en logarithme : 0.138   soit un effet relatif de +14.8%
(rappel : DiD en niveau = 10.6 commandes par mois)
```

**Étape 3 — la régression à effets fixes (TWFE)**, en logarithme et en modèle de Poisson, avec erreurs-types groupées par ville.

```python
def twfe(df, debut=18, fin=None, tendance_groupe=False, poisson=False):
    """DiD par régression à effets fixes ville + mois ; erreurs-types groupées par ville."""
    d = df if fin is None else df[df["t"] < fin]
    d = d.assign(camp=((d["groupe_traite"] == 1) & (d["t"] >= debut)).astype(int))
    formule = "commandes ~ camp + C(ville) + C(t)" + (" + groupe_traite:t" if tendance_groupe else "")
    if poisson:
        m = smf.glm(formule, d, family=sm.families.Poisson()).fit(cov_type="cluster", cov_kwds={"groups": d["vid"]})
    else:
        m = smf.ols(formule.replace("commandes", "np.log(commandes)"), d).fit(cov_type="cluster", cov_kwds={"groups": d["vid"]})
    return m.params["camp"], m.bse["camp"]

b, se = twfe(p)
print(f"TWFE (log) : effet = {b:.3f}  erreur-type = {se:.3f}  IC 95 % = [{b - 1.96 * se:.3f} ; {b + 1.96 * se:.3f}]   ({np.exp(b) - 1:+.1%})")
b_p, se_p = twfe(p, poisson=True)
print(f"Poisson    : effet = {b_p:.3f}  erreur-type = {se_p:.3f}  IC 95 % = [{b_p - 1.96 * se_p:.3f} ; {b_p + 1.96 * se_p:.3f}]   ({np.exp(b_p) - 1:+.1%})")
print(f"(rappel du calcul à la main : {did_log:.3f})")
```
<!--sortie-->
```text
TWFE (log) : effet = 0.138  erreur-type = 0.032  IC 95 % = [0.076 ; 0.200]   (+14.8%)
Poisson    : effet = 0.131  erreur-type = 0.028  IC 95 % = [0.076 ; 0.186]   (+14.0%)
(rappel du calcul à la main : 0.138)
```

**Étape 4 — l'étude d'événement** : un coefficient par mois relatif au lancement (référence : le mois précédent).

```python
def etude_evenement(df, ref=-1):
    """Coefficient mois par mois (traitées vs témoins), relatif au mois de lancement (t = 18) ; référence : k = -1."""
    d = df.copy()
    d["rel"] = d["t"] - 18
    termes = []
    for k in sorted(d["rel"].unique()):
        if k == ref:
            continue
        nom = f"ev_{'m' if k < 0 else 'p'}{abs(k)}"
        d[nom] = ((d["groupe_traite"] == 1) & (d["rel"] == k)).astype(int)
        termes.append((k, nom))
    formule = "np.log(commandes) ~ " + " + ".join(n for _, n in termes) + " + C(ville) + C(t)"
    m = smf.ols(formule, d).fit(cov_type="cluster", cov_kwds={"groups": d["vid"]})
    return pd.DataFrame({"k": [k for k, _ in termes], "coef": [m.params[n] for _, n in termes],
                         "se": [m.bse[n] for _, n in termes]})

ee = etude_evenement(p)
avant = ee[ee["k"] < 0]
apres = ee[ee["k"] >= 0]
print(f"avant le lancement : coefficient moyen = {avant['coef'].mean():+.3f} ; plus grand écart en valeur absolue = {avant['coef'].abs().max():.3f}")
print(f"nombre de mois « avant » dont l'IC à 95 % exclut 0 : {int(((avant['coef'].abs() - 1.96 * avant['se']) > 0).sum())} sur {len(avant)}")
print(f"après le lancement : coefficient moyen = {apres['coef'].mean():+.3f}   (effet vrai : 0.150)")
```
<!--sortie-->
```text
avant le lancement : coefficient moyen = +0.054 ; plus grand écart en valeur absolue = 0.188
nombre de mois « avant » dont l'IC à 95 % exclut 0 : 0 sur 17
après le lancement : coefficient moyen = +0.189   (effet vrai : 0.150)
```

**Étape 5 — quand les tendances ne sont pas parallèles** : les grandes villes croissent 1 % plus vite par mois, hors campagne. On regarde l'estimation, le placebo, puis le remède de la tendance de groupe.

```python
q = panel_villes(tendance_diff=0.01)
q["vid"] = pd.factorize(q["ville"])[0]

b_q, se_q = twfe(q)
print(f"Effet estimé par DiD avec tendances NON parallèles : {b_q:.3f}  (erreur-type {se_q:.3f})   | effet vrai : 0.150")
ee_q = etude_evenement(q)
avant_q = ee_q[ee_q["k"] < 0]
print(f"mois « avant » dont l'IC à 95 % exclut 0 : {int(((avant_q['coef'].abs() - 1.96 * avant_q['se']) > 0).sum())} sur {len(avant_q)}")
```
<!--sortie-->
```text
Effet estimé par DiD avec tendances NON parallèles : 0.315  (erreur-type 0.031)   | effet vrai : 0.150
mois « avant » dont l'IC à 95 % exclut 0 : 2 sur 17
```

```python
for nom, df in [("tendances parallèles", p), ("tendances non parallèles", q)]:
    b_pl, se_pl = twfe(df, debut=9, fin=18)
    print(f"placebo ({nom}) : effet « fictif » = {b_pl:+.3f}  (erreur-type {se_pl:.3f}, rapport {b_pl / se_pl:+.1f})")
```
<!--sortie-->
```text
placebo (tendances parallèles) : effet « fictif » = -0.062  (erreur-type 0.038, rapport -1.6)
placebo (tendances non parallèles) : effet « fictif » = +0.097  (erreur-type 0.042, rapport +2.3)
```

```python
b_t, se_t = twfe(q, tendance_groupe=True)
print(f"avec tendance linéaire propre au groupe traité : effet = {b_t:.3f}  (erreur-type {se_t:.3f})   | vrai : 0.150")
b_t2, se_t2 = twfe(p, tendance_groupe=True)
print(f"(le même modèle sur les données initiales, où il n'était pas nécessaire : effet = {b_t2:.3f}, erreur-type {se_t2:.3f})")
```
<!--sortie-->
```text
avec tendance linéaire propre au groupe traité : effet = 0.185  (erreur-type 0.063)   | vrai : 0.150
(le même modèle sur les données initiales, où il n'était pas nécessaire : effet = 0.181, erreur-type 0.062)
```

*Lecture.* La DiD en logarithme vaut 0,138 (+14,8 % ; vérité : 0,15 soit +16,2 %). Avec des tendances non parallèles, l'estimation passe à 0,315, le double de la vérité, alors que son erreur-type reste de 0,031 : c'est l'étude d'événement (2 mois « avant » sur 17 déjà significatifs) et le placebo (rapport +2,3) qui donnent l'alerte.

### Application 7.9 — La variable instrumentale : Wald, 2SLS, complaisants, instrument faible (section 7.4)

**Objectif.** Estimer l'effet de « suivre le compte de la boutique » sur la dépense malgré un facteur de confusion non observé (la passion), avec un rappel envoyé au hasard comme instrument : première étape, estimateur de Wald, moindres carrés en deux étapes, effet pour les complaisants, instrument faible et exclusion violée.

**Étape 1 — les données et la comparaison naïve** (`ch07-iv.csv`, simulateur `iv` de `build/sim_ch07.py`).

```python
from statsmodels.sandbox.regression.gmm import IV2SLS

d = pd.read_csv("donnees/ch07-iv.csv")
print("le simulateur reproduit exactement le fichier :", d.equals(iv()))
print(d.head(5).to_string(index=False))
print(f"\n{len(d)} clients ; {d['suit_compte'].mean():.1%} suivent le compte ; {d['rappel'].mean():.1%} ont reçu le rappel")
print(d.groupby("suit_compte")["depense"].agg(["count", "mean"]).round(1).rename(index={0: "ne suit pas", 1: "suit"}))
```
<!--sortie-->
```text
le simulateur reproduit exactement le fichier : True
 id_client  age  rappel  suit_compte  depense
         1   39       1            1     5.76
         2   40       0            0   124.21
         3   37       1            1   142.74
         4   35       0            1    69.39
         5   58       1            1    51.32

5000 clients ; 62.3% suivent le compte ; 48.8% ont reçu le rappel
             count   mean
suit_compte              
ne suit pas   1886   68.7
suit          3114  109.8
```

```python
ols = smf.ols("depense ~ suit_compte + age", d).fit(cov_type="HC1")
b_ols, se_ols = ols.params["suit_compte"], ols.bse["suit_compte"]
print(f"MCO : effet de suivre le compte = {b_ols:.1f} €  (erreur-type {se_ols:.1f}, IC 95 % : [{b_ols - 1.96 * se_ols:.1f} ; {b_ols + 1.96 * se_ols:.1f}])")
```
<!--sortie-->
```text
MCO : effet de suivre le compte = 41.9 €  (erreur-type 1.4, IC 95 % : [39.1 ; 44.7])
```

**Étape 2 — l'instrument : indépendance (équilibre) et pertinence (première étape, statistique F).**

```python
print("âge moyen avec rappel :", round(d.loc[d.rappel == 1, "age"].mean(), 2), "| sans rappel :", round(d.loc[d.rappel == 0, "age"].mean(), 2))
print(f"SMD de l'âge : {(d.loc[d.rappel == 1, 'age'].mean() - d.loc[d.rappel == 0, 'age'].mean()) / np.sqrt((d.loc[d.rappel == 1, 'age'].var() + d.loc[d.rappel == 0, 'age'].var()) / 2):+.3f}")
```
<!--sortie-->
```text
âge moyen avec rappel : 36.47 | sans rappel : 36.38
SMD de l'âge : +0.008
```

```python
etape1 = smf.ols("suit_compte ~ rappel + age", d).fit(cov_type="HC1")
print("part de clients qui suivent le compte, sans rappel :", round(d.loc[d.rappel == 0, "suit_compte"].mean(), 3),
      "| avec rappel :", round(d.loc[d.rappel == 1, "suit_compte"].mean(), 3))
print(f"première étape : effet du rappel sur la probabilité de suivre = {etape1.params['rappel']:.3f}  (erreur-type {etape1.bse['rappel']:.3f})")
print(f"statistique F de l'instrument : {etape1.tvalues['rappel'] ** 2:.0f}")
```
<!--sortie-->
```text
part de clients qui suivent le compte, sans rappel : 0.441 | avec rappel : 0.813
première étape : effet du rappel sur la probabilité de suivre = 0.372  (erreur-type 0.013)
statistique F de l'instrument : 874
```

**Étape 3 — l'estimateur de Wald** : le rapport de deux différences de moyennes.

```python
moy = d.groupby("rappel")[["suit_compte", "depense"]].mean().round(3)
moy.index = ["sans rappel", "avec rappel"]
print(moy)
pi_hat = moy.loc["avec rappel", "suit_compte"] - moy.loc["sans rappel", "suit_compte"]
rho_hat = moy.loc["avec rappel", "depense"] - moy.loc["sans rappel", "depense"]
print(f"\npremière étape  pi  = {pi_hat:.3f}")
print(f"forme réduite   rho = {rho_hat:.2f} €")
print(f"estimateur de Wald  rho / pi = {rho_hat / pi_hat:.1f} €")
```
<!--sortie-->
```text
             suit_compte  depense
sans rappel        0.441   90.020
avec rappel        0.813   98.825

première étape  pi  = 0.372
forme réduite   rho = 8.81 €
estimateur de Wald  rho / pi = 23.7 €
```

**Étape 4 — les moindres carrés en deux étapes**, écrits trois fois (deux régressions, formule matricielle, estimateur IV), puis les bonnes erreurs-types et la vérification avec `statsmodels`.

```python
n = len(d)
y = d["depense"].to_numpy()
X = np.column_stack([np.ones(n), d["suit_compte"], d["age"]]).astype(float)       # régresseurs, dont le traitement
Z = np.column_stack([np.ones(n), d["rappel"], d["age"]]).astype(float)               # instruments + covariables exogènes

# Étape 1 : traitement expliqué par l'instrument
pi = np.linalg.lstsq(Z, X[:, 1], rcond=None)[0]
T_chapeau = Z @ pi
X_chapeau = X.copy()
X_chapeau[:, 1] = T_chapeau
# Étape 2 : régression de Y sur le traitement « prédit »
beta = np.linalg.lstsq(X_chapeau, y, rcond=None)[0]

# Même résultat avec la formule matricielle (X' Pz X)^-1 X' Pz y
PzX = Z @ np.linalg.solve(Z.T @ Z, Z.T @ X)
beta_matrice = np.linalg.solve(PzX.T @ X, PzX.T @ y)
# Cas « juste identifié » (un instrument pour un traitement) : (Z' X)^-1 Z' y
beta_iv = np.linalg.solve(Z.T @ X, Z.T @ y)
print("2SLS en deux régressions :", beta.round(3))
print("2SLS, formule matricielle:", beta_matrice.round(3))
print("estimateur IV (Z'X)^-1 Z'y :", beta_iv.round(3))
```
<!--sortie-->
```text
2SLS en deux régressions : [107.609  23.839  -0.773]
2SLS, formule matricielle: [107.609  23.839  -0.773]
estimateur IV (Z'X)^-1 Z'y : [107.609  23.839  -0.773]
```

```python
k = X.shape[1]
sigma2_correct = np.sum((y - X @ beta) ** 2) / (n - k)               # résidus avec le VRAI traitement
sigma2_naif = np.sum((y - X_chapeau @ beta) ** 2) / (n - k)          # résidus avec le traitement « prédit » (faux)
var = np.linalg.inv(X_chapeau.T @ X_chapeau)
se_correct = np.sqrt(sigma2_correct * var[1, 1])
se_naif = np.sqrt(sigma2_naif * var[1, 1])
print(f"effet du suivi (2SLS) : {beta[1]:.2f} €")
print(f"erreur-type correcte : {se_correct:.2f}   | erreur-type « naïve » de la seconde régression : {se_naif:.2f}")

# Vérification avec l'implémentation de statsmodels
res = IV2SLS(y, X, Z).fit()
print(f"statsmodels IV2SLS : coefficient = {res.params[1]:.2f}  erreur-type = {res.bse[1]:.2f}")
print(f"IC 95 % : [{beta[1] - 1.96 * se_correct:.1f} ; {beta[1] + 1.96 * se_correct:.1f}]")
```
<!--sortie-->
```text
effet du suivi (2SLS) : 23.84 €
erreur-type correcte : 3.80   | erreur-type « naïve » de la seconde régression : 4.03
statsmodels IV2SLS : coefficient = 23.84  erreur-type = 3.80
IC 95 % : [16.4 ; 31.3]
```

**Étape 5 — ce que l'on estime vraiment : l'effet pour les complaisants.**

```python
rng = np.random.default_rng(74)
n = 400_000
u = rng.normal(size=n)                                        # passion
z = rng.integers(0, 2, n)                                     # rappel aléatoire
v = rng.logistic(size=n)                                      # même « bruit » individuel dans les deux mondes
d0 = (-0.3 + 0.8 * u + v > 0).astype(int)                     # suivrait-il SANS rappel ?
d1 = (-0.3 + 2.0 + 0.8 * u + v > 0).astype(int)               # suivrait-il AVEC rappel ?
tau = 25 + 20 * u                                             # effet individuel : plus fort chez les passionnés
T = np.where(z == 1, d1, d0)
Y = 80 + tau * T + 30 * u + rng.normal(0, 40, n)

complaisants = (d0 == 0) & (d1 == 1)
print(f"toujours-abonnés : {(d0 == 1).mean():.1%} | jamais-abonnés : {(d1 == 0).mean():.1%} | complaisants : {complaisants.mean():.1%}")
print(f"effet moyen sur tous les clients (ATE)        : {tau.mean():.2f} €")
print(f"effet moyen sur les complaisants (LATE vrai)  : {tau[complaisants].mean():.2f} €")
print(f"estimateur de Wald                            : {(Y[z == 1].mean() - Y[z == 0].mean()) / (T[z == 1].mean() - T[z == 0].mean()):.2f} €")
print(f"passion moyenne : complaisants {u[complaisants].mean():+.2f}, toujours-abonnés {u[d0 == 1].mean():+.2f}, jamais-abonnés {u[d1 == 0].mean():+.2f}")
```
<!--sortie-->
```text
toujours-abonnés : 43.4% | jamais-abonnés : 18.1% | complaisants : 38.4%
effet moyen sur tous les clients (ATE)        : 24.99 €
effet moyen sur les complaisants (LATE vrai)  : 21.64 €
estimateur de Wald                            : 21.75 €
passion moyenne : complaisants -0.17, toujours-abonnés +0.40, jamais-abonnés -0.60
```

**Étape 6 — instrument faible, puis exclusion violée.**

```python
dw = iv(force=0.25)
et1 = smf.ols("suit_compte ~ rappel + age", dw).fit(cov_type="HC1")
Xw = np.column_stack([np.ones(len(dw)), dw["suit_compte"], dw["age"]]).astype(float)
Zw = np.column_stack([np.ones(len(dw)), dw["rappel"], dw["age"]]).astype(float)
rw = IV2SLS(dw["depense"].to_numpy(), Xw, Zw).fit()
print(f"part d'abonnés sans rappel : {dw.loc[dw.rappel == 0, 'suit_compte'].mean():.3f}   avec rappel : {dw.loc[dw.rappel == 1, 'suit_compte'].mean():.3f}")
print(f"statistique F de l'instrument : {et1.tvalues['rappel'] ** 2:.1f}")
print(f"IV : effet = {rw.params[1]:.1f} €   erreur-type = {rw.bse[1]:.1f}   IC 95 % : [{rw.params[1] - 1.96 * rw.bse[1]:.0f} ; {rw.params[1] + 1.96 * rw.bse[1]:.0f}]")
```
<!--sortie-->
```text
part d'abonnés sans rappel : 0.441   avec rappel : 0.484
statistique F de l'instrument : 9.2
IV : effet = 14.9 €   erreur-type = 33.8   IC 95 % : [-51 ; 81]
```

```python
def estimation_iv_simple(df):
    """Estimateur IV (Wald) et son erreur-type robuste, sans covariable. Renvoie (estimation, erreur-type, statistique F)."""
    zc = df["rappel"].to_numpy(float) - df["rappel"].mean()
    xc = df["suit_compte"].to_numpy(float) - df["suit_compte"].mean()
    yc = df["depense"].to_numpy(float) - df["depense"].mean()
    b = (zc @ yc) / (zc @ xc)
    e = yc - b * xc
    se = np.sqrt(np.sum(zc ** 2 * e ** 2)) / abs(zc @ xc)
    r = np.corrcoef(zc, xc)[0, 1]
    F = r ** 2 * (len(df) - 2) / (1 - r ** 2)
    return b, se, F

cas = [("forte (force 2,0, n = 5000)", 5000, 2.0), ("moyenne (force 0,25, n = 5000)", 5000, 0.25), ("faible (force 0,25, n = 1000)", 1000, 0.25)]
resultats = {}
for nom, n_mc, force in cas:
    est = np.array([estimation_iv_simple(iv(n=n_mc, seed=10_000 + k, force=force)) for k in range(500)])
    couverture = np.mean(np.abs(est[:, 0] - 25) <= 1.96 * est[:, 1])
    resultats[nom] = est[:, 0]
    q5, q25, q50, q75, q95 = np.percentile(est[:, 0], [5, 25, 50, 75, 95])
    print(f"{nom:32s} F médian {np.median(est[:, 2]):6.1f} | estimation médiane {q50:5.1f}, 5%-95% : [{q5:7.1f} ; {q95:6.1f}] | l'IC contient 25 dans {couverture:.0%} des cas")
```
<!--sortie-->
```text
forte (force 2,0, n = 5000)      F médian  936.7 | estimation médiane  25.1, 5%-95% : [   19.3 ;   31.1] | l'IC contient 25 dans 97% des cas
moyenne (force 0,25, n = 5000)   F médian   14.7 | estimation médiane  25.5, 5%-95% : [  -24.7 ;   67.5] | l'IC contient 25 dans 98% des cas
faible (force 0,25, n = 1000)    F médian    3.0 | estimation médiane  30.8, 5%-95% : [ -185.0 ;  159.1] | l'IC contient 25 dans 99% des cas
```

```python
dv = iv()
dv["depense"] = dv["depense"] + 15 * dv["rappel"]                # effet direct du rappel sur la dépense : viole l'exclusion
Xv = np.column_stack([np.ones(len(dv)), dv["suit_compte"], dv["age"]]).astype(float)
Zv = np.column_stack([np.ones(len(dv)), dv["rappel"], dv["age"]]).astype(float)
rv = IV2SLS(dv["depense"].to_numpy(), Xv, Zv).fit()
print(f"IV avec exclusion violée : effet = {rv.params[1]:.1f} €  (erreur-type {rv.bse[1]:.1f}, IC 95 % : [{rv.params[1] - 1.96 * rv.bse[1]:.0f} ; {rv.params[1] + 1.96 * rv.bse[1]:.0f}])   | vérité : 25")
print(f"biais théorique : effet direct / première étape = 15 / {pi_hat:.3f} = {15 / pi_hat:.1f} €")
```
<!--sortie-->
```text
IV avec exclusion violée : effet = 64.2 €  (erreur-type 3.8, IC 95 % : [57 ; 72])   | vérité : 25
biais théorique : effet direct / première étape = 15 / 0.372 = 40.3 €
```

*Lecture.* La régression ordinaire donne 41,9 € (biaisée par la passion) ; Wald et 2SLS donnent 23,7 et 23,8 € (vérité : 25 €) avec une erreur-type de 3,8 € contre 1,4 €. Avec un instrument faible (F = 9,2), l'intervalle va de −51 à +81 € ; si le rappel contenait un bon de réduction (exclusion violée), l'estimation passe à 64,2 € pour une vérité de 25 €.

**Pour aller plus loin.** Faites varier `force` dans `iv(force=...)` et tracez la largeur de l'intervalle en fonction de la statistique F.

## Exercices

> 🧭 **Comment s'y prendre.** Faites d'abord l'exercice **à la main**, puis vérifiez avec le code. Les exercices sont notés ⭐ (application directe), ⭐⭐ (il faut combiner deux idées) et ⭐⭐⭐ (démonstration ou analyse critique). Les corrigés suivent tous les énoncés.

```python
clients = pd.read_csv("donnees/clients.csv")
panel = pd.read_csv("donnees/ch07-panel-villes.csv")
panel["vid"] = pd.factorize(panel["ville"])[0]
print(clients.shape, panel.shape)
```
<!--sortie-->
```text
(2000, 12) (480, 7)
```

### Exercice 7.1 ⭐ — résultats potentiels (section 7.1.2 du livre)

Six clients ont les dépenses potentielles suivantes (en €) : A ($Y(0)=60$, $Y(1)=75$), B (40, 50), C (100, 105), D (80, 100), E (30, 40), F (90, 95). Les trois premiers ont reçu l'offre, les trois derniers non. (a) Calculez à la main l'ATE, l'ATT et l'ATU. (b) Quelle est la différence naïve des moyennes observées ? (c) Décomposez-la en ATT plus biais de sélection.

### Exercice 7.2 ⭐ — sous-groupes (section 7.1.4 du livre)

Dans l'expérience de `clients.csv`, calculez l'effet de l'offre sur le rachat (`rachat_12m`) **dans chaque canal d'acquisition**, avec intervalle de confiance à 95 %. La gérante remarque : « l'offre marche presque cinq fois mieux sur Réseaux que sur le site ». (a) Testez cette différence. (b) Que devez-vous répondre à la gérante ?

### Exercice 7.3 ⭐ — Simpson (section 7.1.6 du livre)

Une campagne d'e-mails a été envoyée à des clients en ville (1 000 clients dont 600 destinataires) et à la campagne (1 000 clients dont 200 destinataires). En ville, le rachat vaut 50 % chez les destinataires et 40 % chez les autres ; à la campagne, 30 % chez les destinataires et 20 % chez les autres. (a) Calculez le rachat global chez les destinataires et chez les non-destinataires. (b) Que dit la différence globale ? Que dit la différence par zone ? (c) Laquelle croire si la zone est une cause commune de la décision d'envoi et du rachat ? Et si la zone était une conséquence de l'e-mail ?

### Exercice 7.4 ⭐⭐ — choisir l'ensemble d'ajustement (sections 7.1.7 à 7.1.9 du livre)

On simule : un facteur de confusion $C$ ; un traitement $T$ qui en dépend ; un médiateur $M$ affecté par $T$ ; un résultat $Y=5T+3M+4C+\varepsilon$ ; et un effet commun $K=T+Y+\varepsilon'$. (a) Quel est l'effet **total** de $T$ sur $Y$ ? (b) Estimez l'effet par régression avec quatre ensembles d'ajustement : $\varnothing$, $\{C\}$, $\{C,M\}$, $\{C,K\}$. (c) Lequel est correct, et que mesurent les autres ?

### Exercice 7.5 ⭐⭐ — stratification sur le score (section 7.2.4 du livre)

Les clients ont été classés en trois strates de score de propension. Strate A : 400 clients, probabilité d'offre 0,2, dépense moyenne 130 (avec offre) et 100 (sans). Strate B : 400 clients, probabilité 0,5, moyennes 150 et 115. Strate C : 200 clients, probabilité 0,8, moyennes 190 et 150. (a) Calculez la différence naïve. (b) Calculez l'ATE en pondérant les effets par strate. (c) Retrouvez-le par IPW.

### Exercice 7.6 ⭐⭐ — chevauchement (section 7.2.2 du livre)

Reprenez l'étude observationnelle de 7.2 (`ch07-observationnel.csv`). (a) Restreignez l'analyse aux clients dont le score de propension est compris entre 0,1 et 0,9 : combien en reste-t-il ? (b) Réestimez l'ATE par IPW sur cet échantillon, et comparez avec l'estimation sur tous les clients. (c) Quelle quantité estime-t-on désormais ?

### Exercice 7.7 ⭐⭐ — DiD à la main (section 7.3.1 du livre)

Chiffre d'affaires moyen par ville (en milliers de €) : villes traitées 120 avant, 150 après ; villes témoins 80 avant, 92 après. (a) Calculez la DiD en niveau. (b) Calculez-la en logarithme et interprétez en pourcentage. (c) Laquelle des deux hypothèses de tendances parallèles est la plus plausible si le chiffre d'affaires évolue en pourcentage ?

### Exercice 7.8 ⭐⭐ — inférence avec peu de groupes (section 7.3.3 du livre)

Dans le panel, ne gardez que les 12 villes témoins, et attribuez **au hasard** à 4 d'entre elles une « fausse campagne » à partir de `t = 18` : il n'y a **aucun effet** à trouver. Répétez 300 fois (graine 81) et comptez à quelle fréquence la DiD avec erreurs-types groupées paraît « significative » à 5 %. (a) Avec le seuil normal $|t|>1{,}96$. (b) Avec le seuil de Student à 11 degrés de liberté. (c) Que concluez-vous ?

### Exercice 7.9 ⭐⭐ — instrument à la main (section 7.4.3 du livre)

Dans une étude, on observe : avec l'instrument ($Z=1$), 60 % des clients suivent le compte et la dépense moyenne est de 52 € ; sans ($Z=0$), 30 % le suivent et la dépense moyenne est de 46 €. (a) Calculez l'estimateur de Wald. (b) Quelle proportion de complaisants peut-on au mieux estimer ? (c) Si l'instrument avait en réalité un effet direct de 1,5 € sur la dépense, de combien l'estimation serait-elle faussée ?

### Exercice 7.10 ⭐⭐⭐ — démonstration (section 7.4.3 du livre)

Soit $Z$ binaire de probabilité $q=\mathbb P(Z=1)$. (a) Montrez que $\operatorname{Cov}(Z,Y)=q(1-q)\big(\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]\big)$. (b) Déduisez que $\operatorname{Cov}(Z,Y)/\operatorname{Cov}(Z,T)$ est égal au rapport de Wald. (c) Vérifiez-le numériquement sur `ch07-iv.csv`.

### Exercice 7.11 ⭐⭐⭐ — médiation (section 7.1.7 du livre)

Reprenez la simulation de 7.1.7 (offre randomisée ; médiateur « code utilisé » ; motivation qui influence à la fois l'utilisation du code et la dépense). Cette fois, **supposez la motivation observée**. (a) Estimez l'effet direct de l'offre en ajustant sur le code **et** la motivation. (b) Déduisez l'effet indirect (par le code), et comparez avec la valeur vraie $30\times\mathbb P(\text{code}\mid\text{offre})$. (c) Pourquoi l'ajustement sur le médiateur marche-t-il ici et pas en 7.1.7 ?

### Exercice 7.12 ⭐⭐⭐ — critique d'une étude (section 7.4.7 du livre)

Une collègue veut estimer l'effet de « venir en boutique » (traitement) sur la dépense annuelle (résultat). Elle propose comme instrument la **distance** entre le domicile du client et la boutique. Discutez chacune des trois conditions d'un instrument, proposez une vérification ou un ajustement pour chacune, et dites ce que l'on estimerait si l'instrument était valide.

## Corrigés

### Corrigé 7.1

(a) Effets individuels : A $+15$, B $+10$, C $+5$, D $+20$, E $+10$, F $+5$. ATT $=(15+10+5)/3=10$ ; ATU $=(20+10+5)/3=11{,}67$ ; ATE $=65/6=10{,}83$. (b) Observé : traités (les $Y(1)$ des trois premiers) $75,50,105$, moyenne $76{,}67$ ; non traités (les $Y(0)$ des trois derniers) $80,30,90$, moyenne $66{,}67$ ; différence naïve $=10$. (c) $\mathbb E[Y(0)\mid T=1]=(60+40+100)/3=66{,}67$ et $\mathbb E[Y(0)\mid T=0]=66{,}67$ : le biais de sélection est **nul** (par hasard dans ce petit exemple), donc la différence naïve égale l'ATT (10). Vérifions :

```python
ex1 = pd.DataFrame({"client": ["A", "B", "C", "D", "E", "F"],
                    "y0": [60, 40, 100, 80, 30, 90], "y1": [75, 50, 105, 100, 40, 95], "offre": [1, 1, 1, 0, 0, 0]})
ex1["effet"] = ex1["y1"] - ex1["y0"]
obs = np.where(ex1.offre == 1, ex1.y1, ex1.y0)
print(f"ATE = {ex1.effet.mean():.2f}  ATT = {ex1.effet[ex1.offre == 1].mean():.2f}  ATU = {ex1.effet[ex1.offre == 0].mean():.2f}")
print(f"différence naïve = {obs[ex1.offre == 1].mean() - obs[ex1.offre == 0].mean():.2f}")
print(f"biais de sélection = {ex1.y0[ex1.offre == 1].mean() - ex1.y0[ex1.offre == 0].mean():.2f}")
```
<!--sortie-->
```text
ATE = 10.83  ATT = 10.00  ATU = 11.67
différence naïve = 10.00
biais de sélection = 0.00
```


Moralité : un biais de sélection **nul** n'est pas impossible, mais on ne peut jamais le savoir sans connaître les $Y(0)$ des traités ; la différence naïve n'est donc fiable que si l'on a une raison de croire que la sélection est ignorable.

### Corrigé 7.2

(a) Dans chaque canal, la différence de proportions et son intervalle de Wald :

```python
lignes = []
for canal, g in clients.groupby("canal_acquisition"):
    t, u = g[g.offre_bienvenue == 1]["rachat_12m"], g[g.offre_bienvenue == 0]["rachat_12m"]
    diff = t.mean() - u.mean()
    se = np.sqrt(t.var() / len(t) + u.var() / len(u))
    lignes.append({"canal": canal, "clients": len(g), "effet": diff, "IC95 bas": diff - 1.96 * se, "IC95 haut": diff + 1.96 * se})
print(pd.DataFrame(lignes).round(3).to_string(index=False))

complet = smf.logit("rachat_12m ~ offre_bienvenue * C(canal_acquisition)", clients).fit(disp=0)
reduit = smf.logit("rachat_12m ~ offre_bienvenue + C(canal_acquisition)", clients).fit(disp=0)
lr = 2 * (complet.llf - reduit.llf)
print(f"\ntest de l'interaction offre x canal (rapport de vraisemblance, 2 ddl) : p = {stats.chi2.sf(lr, 2):.4f}")
```
<!--sortie-->
```text
   canal  clients  effet  IC95 bas  IC95 haut
Boutique      504  0.116     0.029      0.202
 Réseaux      816  0.196     0.129      0.263
    Site      680  0.042    -0.033      0.117

test de l'interaction offre x canal (rapport de vraisemblance, 2 ddl) : p = 0.0105
```


L'effet est de $+19{,}6$ points sur Réseaux contre $+4{,}2$ sur le site, avec des intervalles larges ; le test d'interaction (rapport de vraisemblance, chapitre 2) donne $p\approx0{,}01$. (b) Que répondre ? **Prudence.** Cette analyse par sous-groupe est *exploratoire* : si la gérante avait regardé cinq découpages différents (canal, ville, âge, année d'inscription…), le seuil de Bonferroni serait $0{,}05/5=0{,}01$, que $p=0{,}0105$ ne franchit pas (volume I, section 3.5.5). Et l'expérience n'était **pas dimensionnée** pour détecter des différences entre sous-groupes (chaque canal n'a que quelques centaines de clients par bras). **Vérité révélée** : dans le simulateur, l'effet de l'offre est **le même** dans les trois canaux (12,3 à 12,4 points, comme on peut le vérifier par la même intégration qu'en 7.1.4) ; l'écart observé n'est qu'une fluctuation d'échantillonnage, de celles qui arrivent environ une fois sur cent. La bonne réponse : « c'est une piste, pas une conclusion ; on peut la **confirmer** par une nouvelle expérience prévue pour cela ».

### Corrigé 7.3

(a) Destinataires : $600\times0{,}5+200\times0{,}3=300+60=360$ rachats sur $800$, soit $45\,\%$. Non-destinataires : $400\times0{,}4+800\times0{,}2=160+160=320$ rachats sur $1200$, soit $26{,}7\,\%$. (b) Globalement l'e-mail est associé à **+18,3 points** ; par zone, à **+10 points** dans chaque zone. L'écart global **surestime** l'effet, car les destinataires sont surtout des citadins, qui rachètent davantage de toute façon (ici le sens est l'inverse du paradoxe de 7.1.6, mais le mécanisme est le même). (c) Si la zone est une cause commune de l'envoi et du rachat, il faut **ajuster** : l'effet standardisé est $0{,}5\times10+0{,}5\times10=10$ points. Si la zone était une **conséquence** de l'e-mail (l'e-mail pousserait les clients à déménager en ville !), ajuster sur elle serait une erreur : la différence globale deviendrait l'effet total.

```python
ex3 = pd.DataFrame({"zone": ["ville", "ville", "campagne", "campagne"], "mail": [1, 0, 1, 0],
                    "n": [600, 400, 200, 800], "taux": [0.5, 0.4, 0.3, 0.2]})
ex3["rachats"] = ex3["n"] * ex3["taux"]
glob = ex3.groupby("mail")[["n", "rachats"]].sum()
print("taux global :", (glob.rachats / glob.n).round(3).to_dict())
par_zone = ex3.pivot(index="zone", columns="mail", values="taux")
poids = ex3.groupby("zone")["n"].sum() / ex3["n"].sum()
print("effet par zone :", (par_zone[1] - par_zone[0]).round(2).to_dict(), "| poids :", poids.round(2).to_dict())
print("effet standardisé :", round(((par_zone[1] - par_zone[0]) * poids).sum(), 3))
```
<!--sortie-->
```text
taux global : {0: 0.267, 1: 0.45}
effet par zone : {'campagne': 0.1, 'ville': 0.1} | poids : {'campagne': 0.5, 'ville': 0.5}
effet standardisé : 0.1
```


### Corrigé 7.4

(a) $T$ agit directement (5) et par $M$ (qui vaut $2T$ en moyenne, et pèse 3 dans $Y$) : effet total $=5+3\times2=11$. (b) et (c) :

```python
rng = np.random.default_rng(401)
n = 50_000
conf = rng.normal(size=n)                                      # facteur de confusion (nommé « conf » pour ne pas masquer C() de patsy)
T = (conf + rng.normal(size=n) > 0).astype(int)
M = 2 * T + rng.normal(size=n)
Y = 5 * T + 3 * M + 4 * conf + rng.normal(size=n)
K = T + Y + rng.normal(size=n)
df4 = pd.DataFrame({"Y": Y, "T": T, "M": M, "conf": conf, "K": K})
for nom, f in [("∅", "Y ~ T"), ("{C}", "Y ~ T + conf"), ("{C, M}", "Y ~ T + conf + M"), ("{C, K}", "Y ~ T + conf + K")]:
    print(f"ensemble {nom:7s} : effet estimé de T = {smf.ols(f, df4).fit().params['T']:.2f}")
```
<!--sortie-->
```text
ensemble ∅       : effet estimé de T = 15.50
ensemble {C}     : effet estimé de T = 11.00
ensemble {C, M}  : effet estimé de T = 5.01
ensemble {C, K}  : effet estimé de T = 0.08
```


Seul $\{C\}$ donne l'effet **total** (11). Sans ajustement, on garde la **confusion** (15,5 : $C$ pousse à la fois $T$ et $Y$) ; avec $\{C,M\}$, on retire la voie par le médiateur et on mesure l'effet **direct** (5), ce qui peut être voulu mais ne répond pas à la question « que fait $T$ ? » ; avec $\{C,K\}$, on conditionne sur un effet commun : l'estimation s'effondre vers 0, **en créant un biais**, alors que $K$ semble une covariable « utile ».

### Corrigé 7.5

(a) Nombres de traités par strate : $0{,}2\times400=80$, $0{,}5\times400=200$, $0{,}8\times200=160$ (total 440) ; de témoins : $320$, $200$, $40$ (total 560). Moyenne des traités $=(80\times130+200\times150+160\times190)/440=160{,}9$ ; moyenne des témoins $=(320\times100+200\times115+40\times150)/560=108{,}9$ ; différence naïve $=52{,}0$. (b) Effets par strate : $30,35,40$ ; ATE $=(400\times30+400\times35+200\times40)/1000=34{,}0$. (c) IPW : poids $1/e$ pour les traités, $1/(1-e)$ pour les témoins. Dans chaque strate, le poids total des traités est $n$ et celui des témoins aussi ; la pseudo-population a donc la même composition dans les deux groupes. L'ATE par IPW coïncide avec 34.

```python
ex5 = pd.DataFrame({"strate": ["A", "B", "C"], "n": [400, 400, 200], "e": [0.2, 0.5, 0.8],
                    "m1": [130, 150, 190], "m0": [100, 115, 150]})
ex5["n1"], ex5["n0"] = ex5.n * ex5.e, ex5.n * (1 - ex5.e)
naif = (ex5.n1 * ex5.m1).sum() / ex5.n1.sum() - (ex5.n0 * ex5.m0).sum() / ex5.n0.sum()
ate = ((ex5.m1 - ex5.m0) * ex5.n).sum() / ex5.n.sum()
m1_ipw = (ex5.n1 * ex5.m1 / ex5.e).sum() / (ex5.n1 / ex5.e).sum()
m0_ipw = (ex5.n0 * ex5.m0 / (1 - ex5.e)).sum() / (ex5.n0 / (1 - ex5.e)).sum()
print(f"différence naïve = {naif:.1f} | ATE par strate = {ate:.1f} | ATE par IPW = {m1_ipw - m0_ipw:.1f}")
```
<!--sortie-->
```text
différence naïve = 52.0 | ATE par strate = 34.0 | ATE par IPW = 34.0
```


### Corrigé 7.6

(a)-(b) On refait l'estimation du score, puis on restreint :

```python
obs = pd.read_csv("donnees/ch07-observationnel.csv")
verite = pd.read_csv("donnees/ch07-observationnel-verite.csv")
d6 = obs.merge(verite, on="id_client")
d6["ps"] = smf.logit("offre ~ age + C(canal) + engagement", d6).fit(disp=0).predict(d6)
ate_vrai = (d6.y1 - d6.y0).mean()

def ipw_ate(df):
    w = np.where(df.offre == 1, 1 / df.ps, 1 / (1 - df.ps))
    return (np.average(df.depense[df.offre == 1], weights=w[df.offre == 1])
            - np.average(df.depense[df.offre == 0], weights=w[df.offre == 0]))

restreint = d6[(d6.ps >= 0.1) & (d6.ps <= 0.9)]
ate_restreint_vrai = (restreint.y1 - restreint.y0).mean()
print(f"clients conservés : {len(restreint)} sur {len(d6)} ({len(restreint) / len(d6):.1%})")
print(f"IPW, tous les clients     : {ipw_ate(d6):.2f}   (ATE vrai de la population : {ate_vrai:.2f})")
print(f"IPW, scores dans [0,1 ; 0,9] : {ipw_ate(restreint):.2f}   (ATE vrai de ce sous-échantillon : {ate_restreint_vrai:.2f})")
```
<!--sortie-->
```text
clients conservés : 3778 sur 4000 (94.5%)
IPW, tous les clients     : 14.36   (ATE vrai de la population : 15.53)
IPW, scores dans [0,1 ; 0,9] : 14.73   (ATE vrai de ce sous-échantillon : 15.59)
```


(c) En restreignant, on change la **population cible** : on estime l'effet pour les clients dont la probabilité d'offre n'est ni très faible ni très forte (la population de « chevauchement »), et non plus pour tous. Ici, la différence est **minime** : 94,5 % des clients restent, et l'ATE vrai du sous-échantillon (15,59) est presque celui de la population (15,53), parce que le chevauchement était déjà bon ; l'estimation passe de 14,36 à 14,73. Elle serait beaucoup plus importante si l'on devait écarter une grande partie des clients : l'ATE vrai du sous-échantillon pourrait alors différer sensiblement de celui de la population dès que l'effet varie avec le score (ici, il varie avec le canal, et le canal influence le score). Dans tous les cas, l'estimation répond à une question légèrement différente (celle de la population de chevauchement), à **dire explicitement** dans le rapport.

### Corrigé 7.7

(a) En niveau : $(150-120)-(92-80)=30-12=18$ milliers de €. (b) En logarithme : $\ln(150/120)-\ln(92/80)=\ln1{,}25-\ln1{,}15=0{,}2231-0{,}1398=0{,}0833$ (le code donne 0,0834, sans l'arrondi intermédiaire), soit un effet relatif d'environ $+8{,}7\,\%$ ($e^{0{,}0833}-1$). Les villes traitées auraient crû de $25\,\%$ ; les témoins de $15\,\%$ ; sans campagne, les traitées auraient crû de $15\,\%$ aussi, soit $138$, ce qui donne un effet de $150-138=12$ milliers, et non 18. (c) Si le chiffre d'affaires évolue en **pourcentage**, les tendances parallèles sont plausibles **en logarithme** : l'effet de 18 milliers en niveau surestime l'effet réel (il suppose que la ville traitée, plus grosse, aurait crû de $12$ milliers comme la petite, alors qu'une croissance de $15\,\%$ sur 120 fait $18$ : la hausse « naturelle » des grandes villes est plus grande en niveau).

```python
a_b, a_a, t_b, t_a = 80, 92, 120, 150
print(f"DiD en niveau : {(t_a - t_b) - (a_a - a_b)} | DiD en log : {np.log(t_a / t_b) - np.log(a_a / a_b):.4f} (soit {np.exp(np.log(t_a / t_b) - np.log(a_a / a_b)) - 1:+.1%})")
print(f"contrefactuel multiplicatif pour les villes traitées : {t_b * a_a / a_b:.0f}  -> effet {t_a - t_b * a_a / a_b:.0f}")
```
<!--sortie-->
```text
DiD en niveau : 18 | DiD en log : 0.0834 (soit +8.7%)
contrefactuel multiplicatif pour les villes traitées : 138  -> effet 12
```


### Corrigé 7.8

```python
temoins = panel[panel["groupe_traite"] == 0]
villes = temoins["ville"].unique()
rng = np.random.default_rng(81)
t_stats = []
for _ in range(300):
    faux = set(rng.choice(villes, 4, replace=False))
    d8 = temoins.assign(camp=(temoins["ville"].isin(faux) & (temoins["t"] >= 18)).astype(int))
    m = smf.ols("np.log(commandes) ~ camp + C(ville) + C(t)", d8).fit(cov_type="cluster", cov_kwds={"groups": d8["vid"]})
    t_stats.append(m.params["camp"] / m.bse["camp"])
t_stats = np.array(t_stats)
print(f"seuil normal 1,96            : {np.mean(np.abs(t_stats) > 1.96):.1%} de « découvertes »")
print(f"seuil de Student (11 ddl)    : {np.mean(np.abs(t_stats) > stats.t.ppf(0.975, 11)):.1%} de « découvertes »")
```
<!--sortie-->
```text
seuil normal 1,96            : 8.0% de « découvertes »
seuil de Student (11 ddl)    : 4.7% de « découvertes »
```


(a)-(b) Avec le seuil normal, le test « découvre » un effet là où il n'y en a aucun dans environ 8 % des simulations au lieu des 5 % annoncés ; avec le seuil de Student à 11 degrés de liberté, le taux retombe à près de 5 % (4,7 %). (c) Quand le nombre de groupes (ici 12 villes, dont 4 « traitées ») est petit, les erreurs-types groupées sont **trop optimistes** et le seuil normal est trop laxiste : on obtient des faux positifs en excès. Remèdes : seuil de Student avec peu de degrés de liberté, bootstrap par groupes, ou tests de permutation (volume I, section 3.7) : c'est exactement ce que nous venons de faire, puisque la distribution de l'effet « fictif » est la distribution de référence d'un test de permutation.

### Corrigé 7.9

(a) $\hat\beta=\dfrac{52-46}{0{,}60-0{,}30}=\dfrac{6}{0{,}3}=20$ €. (b) La part de **complaisants** est $\pi=0{,}60-0{,}30=30\,\%$ (sous la monotonie) : l'effet de 20 € est l'effet **pour ces 30 %** de clients. (c) Un effet direct $\gamma_Z=1{,}5$ ajouterait $1{,}5$ à la forme réduite ($6\to7{,}5$) sans changer la première étape : l'estimation deviendrait $7{,}5/0{,}3=25$, soit un biais de $\gamma_Z/\pi=1{,}5/0{,}3=5$ €.

```python
pi, rho = 0.60 - 0.30, 52 - 46
print(f"Wald = {rho / pi:.1f} | avec effet direct de 1,5 : {(rho + 1.5) / pi:.1f} | biais = {1.5 / pi:.1f}")
```
<!--sortie-->
```text
Wald = 20.0 | avec effet direct de 1,5 : 25.0 | biais = 5.0
```


### Corrigé 7.10

(a) Comme $Z\in\{0,1\}$ : $\operatorname{Cov}(Z,Y)=\mathbb E[ZY]-\mathbb E[Z]\,\mathbb E[Y]$. On a $\mathbb E[ZY]=q\,\mathbb E[Y\mid Z=1]$ et $\mathbb E[Y]=q\,\mathbb E[Y\mid Z=1]+(1-q)\,\mathbb E[Y\mid Z=0]$. Donc $\operatorname{Cov}(Z,Y)=q\,\mu_1-q\big(q\mu_1+(1-q)\mu_0\big)=q(1-q)(\mu_1-\mu_0)$ avec $\mu_z=\mathbb E[Y\mid Z=z]$. (b) La même formule vaut pour $T$ à la place de $Y$ ; dans le rapport, le facteur $q(1-q)$ se **simplifie**, et il reste $\dfrac{\mathbb E[Y\mid Z=1]-\mathbb E[Y\mid Z=0]}{\mathbb E[T\mid Z=1]-\mathbb E[T\mid Z=0]}$, le rapport de Wald. (c) Vérification :

```python
iv_data = pd.read_csv("donnees/ch07-iv.csv")
z, tt, yy = iv_data["rappel"].to_numpy(float), iv_data["suit_compte"].to_numpy(float), iv_data["depense"].to_numpy()
q = z.mean()
cov_zy, cov_zt = np.cov(z, yy, ddof=0)[0, 1], np.cov(z, tt, ddof=0)[0, 1]
rho = yy[z == 1].mean() - yy[z == 0].mean()
pi = tt[z == 1].mean() - tt[z == 0].mean()
print(f"Cov(Z,Y) = {cov_zy:.4f}  vs  q(1-q) x rho = {q * (1 - q) * rho:.4f}")
print(f"Cov(Z,Y)/Cov(Z,T) = {cov_zy / cov_zt:.4f}  |  rapport de Wald rho/pi = {rho / pi:.4f}")
```
<!--sortie-->
```text
Cov(Z,Y) = 2.2000  vs  q(1-q) x rho = 2.2000
Cov(Z,Y)/Cov(Z,T) = 23.6563  |  rapport de Wald rho/pi = 23.6563
```


### Corrigé 7.11

(a)-(b) On réutilise la simulation de 7.1.7 (même graine), mais avec la motivation dans la régression :

```python
rng = np.random.default_rng(71)
n = 100_000
motivation = rng.normal(size=n)
offre = rng.integers(0, 2, n)
code_si_offre = rng.random(n) < 1 / (1 + np.exp(-(0.4 + 0.9 * motivation)))
code = offre * code_si_offre
depense = 100 + 8 * offre + 30 * code + 20 * motivation + rng.normal(0, 25, n)
d11 = pd.DataFrame({"depense": depense, "offre": offre, "code": code, "motivation": motivation})

total = smf.ols("depense ~ offre", d11).fit().params["offre"]
direct = smf.ols("depense ~ offre + code + motivation", d11).fit().params["offre"]
print(f"effet total estimé (offre seule)            : {total:.2f}")
print(f"effet direct estimé (offre + code + motivation) : {direct:.2f}   (vrai : 8)")
print(f"effet indirect = total - direct = {total - direct:.2f}   (vrai : 30 x {code_si_offre.mean():.2f} = {30 * code_si_offre.mean():.2f})")
```
<!--sortie-->
```text
effet total estimé (offre seule)            : 25.62
effet direct estimé (offre + code + motivation) : 8.27   (vrai : 8)
effet indirect = total - direct = 17.35   (vrai : 30 x 0.58 = 17.47)
```


(c) En 7.1.7, la motivation était **cachée** : conditionner sur le médiateur ouvrait un chemin biaisé $\text{offre}\to\text{code}\leftarrow\text{motivation}\to\text{dépense}$ (le code est un effet commun de l'offre et de la motivation). Quand la motivation est **observée et incluse**, ce chemin est bloqué, et le coefficient de l'offre redevient l'effet **direct**. Moralité : l'analyse de médiation exige de contrôler **tous** les facteurs de confusion entre le médiateur et le résultat, une hypothèse supplémentaire, plus exigeante que celle de l'effet total (qui n'en demande aucune dans une expérience randomisée).

### Corrigé 7.12

Il n'y a pas de code ici : c'est une analyse critique. *Pertinence* : la distance doit réellement influencer la fréquentation (plausible : plus on habite loin, moins on vient) ; on le **vérifie** avec la première étape et sa statistique $F$. *Indépendance* : les clients **choisissent** où habiter, et ce choix dépend du revenu, du mode de vie, de l'âge : la distance n'est pas tirée au sort. Les citadins aisés habitent peut-être près du centre, où se trouve la boutique, et dépensent plus pour cette raison : l'instrument est corrélé à un facteur de confusion. On peut atténuer en **ajustant** sur les variables socio-économiques observées et sur la ville, mais jamais complètement. *Exclusion* : la distance ne doit affecter la dépense **que** via la fréquentation de la boutique ; or elle peut affecter la dépense par d'autres voies (un client éloigné achète davantage en ligne, ou fait de plus gros achats par déplacement). On peut chercher des **tests de plausibilité** (l'effet de la distance sur la dépense en ligne devrait être nul chez ceux qui ne viennent jamais en boutique) sans pouvoir prouver l'exclusion. *Ce qu'on estimerait si l'instrument était valide* : l'effet moyen de venir en boutique pour les **complaisants**, c'est-à-dire les clients dont la fréquentation **dépend** de la distance (ceux qui viendraient s'ils habitaient près et ne viendraient pas s'ils habitaient loin) : pas pour les habitués, ni pour ceux qui ne viendraient jamais. Pour une variable continue comme la distance, l'interprétation est une moyenne pondérée de tels effets, plus difficile à énoncer.
