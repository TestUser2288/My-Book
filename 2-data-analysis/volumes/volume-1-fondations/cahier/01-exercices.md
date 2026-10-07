# Chapitre 1 : Les essentiels de la statistique — exercices et applications

> 🧭 **Ce chapitre du cahier** accompagne le chapitre 1 du livre. Il contient **huit applications guidées** (de petites études que vous refaites sur les données de la boutique) et **quatorze exercices** de difficulté croissante (⭐ calcul à la main, ⭐⭐ calcul et interprétation, ⭐⭐⭐ réflexion de méthode), tous **corrigés**. Les applications se font devant l'ordinateur, étape par étape ; les exercices se font d'abord **sur papier**. Chaque exercice renvoie à la section du livre qui donne les outils.

Une seule cellule charge les bibliothèques et les données. Elle est reprise telle quelle au début de chaque application : si vous travaillez sur un notebook, exécutez-la une fois.

```python
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
from scipy import stats
import outils_ch01 as O

d = O.charger()                         # commandes (avec leur panier), lignes, clients, retours, jours
cmd, lig, jours, cli = d.commandes, d.lignes, d.jours, d.clients
panier = cmd["panier"]
print(len(cmd), "commandes ;", len(lig), "lignes ;", len(jours), "jours ;", len(cli), "clients")
```
<!--sortie-->
```text
36395 commandes ; 83905 lignes ; 1096 jours ; 6000 clients
```

```python hide
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
def NUM(cle, valeur):
    print("NUM", cle, valeur)
```

## Applications

### Application 1.1 — Résumer un panier (section 1.1)

**Objectif.** Décrire les paniers de la boutique **par canal**, repérer les valeurs inhabituelles, et refaire à la machine le calcul à la main du livre sur neuf commandes.

**Étape 1 — Un tableau de résumés.** On calcule, pour chaque canal, l'effectif, la moyenne, la médiane et l'écart-type.

```python
r = cmd.groupby("canal")["panier"].agg(["count", "mean", "median", "std"]).round(2)
r["cv"] = (r["std"] / r["mean"]).round(2)
print(r)
```
<!--sortie-->
```text
          count    mean  median    std    cv
canal                                       
Boutique  16975  100.90   79.80  80.87  0.80
Réseaux    3957  100.52   79.70  81.48  0.81
Site      15463   99.77   79.76  80.39  0.81
```

**Étape 2 — Les valeurs inhabituelles.** On applique la règle de Tukey (1,5 écart interquartile) à chaque canal, puis on regarde les cinq plus grosses commandes.

```python
def bornes(x):
    q1, q3 = x.quantile([0.25, 0.75])
    return q3 + 1.5 * (q3 - q1)
haut = cmd.groupby("canal")["panier"].apply(bornes).round(1)
n_ab = cmd.assign(h=cmd["canal"].map(haut)).query("panier > h").groupby("canal").size()
print(pd.DataFrame({"borne haute": haut, "valeurs au-delà": n_ab}))
nl = lig.groupby("id_commande").size()
print(cmd.nlargest(5, "panier")[["id_commande", "canal", "panier"]].assign(lignes=lambda t: t["id_commande"].map(nl)).to_string(index=False))
```
<!--sortie-->
```text
          borne haute  valeurs au-delà
canal                                 
Boutique        276.9              635
Réseaux         277.0              147
Site            270.7              610
 id_commande    canal  panier  lignes
       27558  Réseaux  987.90       5
       24157 Boutique  787.05       5
       33982 Boutique  783.96       6
       30123  Réseaux  772.53       6
       31685 Boutique  752.96       6
```

**Étape 3 — Concentration du chiffre d'affaires.** Quelle part du chiffre d'affaires représentent les 10 % de commandes les plus importantes ?

```python
tri = panier.sort_values(ascending=False).values
part = tri[: int(0.1 * len(tri))].sum() / tri.sum()
print("part des 10 % de commandes les plus grosses :", round(100 * part, 1), "%")
```
<!--sortie-->
```text
part des 10 % de commandes les plus grosses : 27.9 %
```

**Étape 4 — Le calcul à la main, vérifié.** Reprenez les neuf commandes du 15 avril 2025 en boutique et retrouvez les résultats du livre (moyenne 102,78 ; médiane 66,75 ; écart-type 85,83).

```python
x9 = cmd[(cmd["date_commande"] == "2025-04-15") & (cmd["canal"] == "Boutique")]["panier"].head(9).round(2)
print(sorted(x9), "| moyenne", round(x9.mean(), 2), "| médiane", x9.median(), "| écart-type", round(x9.std(), 2))
```
<!--sortie-->
```text
[9.69, 22.56, 48.74, 50.27, 66.75, 128.25, 132.37, 207.56, 258.83] | moyenne 102.78 | médiane 66.75 | écart-type 85.83
```

```python hide
NUM("cv_B", (cmd[cmd["canal"] == "Boutique"]["panier"].std() / cmd[cmd["canal"] == "Boutique"]["panier"].mean()))
NUM("n_ab_tot", int(n_ab.sum())); NUM("part10", part * 100)
NUM("max_lignes", int(cmd.nlargest(5, "panier")["id_commande"].map(nl).min()))
assert round(x9.mean(), 2) == 102.78 and x9.median() == 66.75 and round(x9.std(), 2) == 85.83
```
<!--sortie-->
```text
NUM cv_B 0.8015356927214824
NUM n_ab_tot 1392
NUM part10 27.933476217591153
NUM max_lignes 5
```

**Lecture.** Les trois canaux se ressemblent beaucoup (même moyenne, même médiane, même dispersion, coefficient de variation voisin de 0,80) : le canal ne différencie pas les paniers. Au total, 1 392 commandes dépassent la borne de Tukey de leur canal ; les cinq plus grosses comptent au moins 5 lignes chacune : elles sont **légitimes** (de grosses commandes), pas des erreurs. Les 10 % de commandes les plus importantes pèsent 28 % du chiffre d'affaires.

**À vous.** Refaites l'étape 2 avec la règle de 3 écarts-types autour de la moyenne au lieu de 1,5 EIQ : combien de commandes sont signalées, et pourquoi la règle est-elle moins adaptée ici ? *Piste : la moyenne et l'écart-type sont eux-mêmes tirés par les grosses commandes ; la règle de Tukey s'appuie sur les quartiles, qui ne le sont pas.*

### Application 1.2 — Moyennes qui trompent (section 1.1.4)

**Objectif.** Constater que la moyenne de moyennes diffère de la moyenne globale, et fabriquer un paradoxe de Simpson.

**Étape 1 — Taux de retour : moyenne simple ou taux global ?** Calculez le taux de retour par canal, puis par catégorie, et comparez la moyenne simple des taux au taux global.

```python
res = {}
for cle in ("canal", "categorie"):
    g = lig.groupby(cle)["retournee"].agg(["sum", "count"])
    g["taux_%"] = (100 * g["sum"] / g["count"]).round(2)
    res[cle] = g["taux_%"].mean()
    print(g["taux_%"].to_dict(), "| moyenne simple :", round(g["taux_%"].mean(), 2), "| global :", round(100 * lig["retournee"].mean(), 2))
```
<!--sortie-->
```text
{'Boutique': 3.08, 'Réseaux': 6.67, 'Site': 8.98} | moyenne simple : 6.24 | global : 5.96
{'Bien-être': 6.08, 'Cuisine': 6.15, 'Décoration': 6.04, 'Jardin': 6.16, 'Maison': 5.86, 'Papeterie': 5.43} | moyenne simple : 5.95 | global : 5.96
```

**Étape 2 — Moyenne des paniers moyens mensuels.** Faites la moyenne des 36 paniers moyens mensuels, puis comparez au panier moyen global.

```python
mens = cmd.groupby(["annee", "mois"])["panier"].agg(["mean", "size"])
print("moyenne des moyennes mensuelles :", round(mens["mean"].mean(), 2), "| moyenne pondérée :", round((mens["mean"] * mens["size"]).sum() / mens["size"].sum(), 2), "| global :", round(panier.mean(), 2))
```
<!--sortie-->
```text
moyenne des moyennes mensuelles : 100.99 | moyenne pondérée : 100.38 | global : 100.38
```

**Étape 3 — Fabriquer un paradoxe de Simpson.** Dans le fichier réel, on ne trouve pas de renversement. On le fabrique : deux offres P et Q, deux groupes de clients, des envois répartis différemment.

```python
env = pd.DataFrame({"offre": ["P", "P", "Q", "Q"], "groupe": ["facile", "difficile"] * 2, "envois": [300, 100, 100, 300], "achats": [180, 20, 65, 75]})
env["taux"] = env["achats"] / env["envois"]
print(env)
tot = env.groupby("offre")[["envois", "achats"]].sum(); tot["taux"] = tot["achats"] / tot["envois"]
print(tot)
```
<!--sortie-->
```text
  offre     groupe  envois  achats  taux
0     P     facile     300     180  0.60
1     P  difficile     100      20  0.20
2     Q     facile     100      65  0.65
3     Q  difficile     300      75  0.25
       envois  achats  taux
offre                      
P         400     200  0.50
Q         400     140  0.35
```

```python hide
NUM("tm_canal", res["canal"]); NUM("tm_cat", res["categorie"]); NUM("tm_global", 100 * lig["retournee"].mean())
NUM("sim_P", tot.loc["P", "taux"] * 100); NUM("sim_Q", tot.loc["Q", "taux"] * 100)
```
<!--sortie-->
```text
NUM tm_canal 6.243333333333333
NUM tm_cat 5.953333333333333
NUM tm_global 5.961504081997497
NUM sim_P 50.0
NUM sim_Q 35.0
```

**Lecture.** Sur les retours par catégorie, la moyenne simple (5,95 %) et le taux global (5,96 %) sont voisins parce que les catégories ont des poids et des taux proches ; par canal, ils diffèrent (6,24 % contre 5,96 %), parce que les canaux ont des poids très inégaux et des taux très différents. La moyenne simple des paniers mensuels s'écarte légèrement de la moyenne pondérée, qui retrouve exactement le panier moyen global. Enfin, l'offre Q convertit mieux dans les **deux** groupes (65 % contre 60 %, 25 % contre 20 %) mais moins bien **au total** (35 % contre 50 %), parce qu'elle a été envoyée surtout au groupe difficile.

**À vous.** Choisissez d'autres effectifs pour qu'un renversement apparaisse avec **trois** groupes. *Piste : un renversement exige que la répartition des envois entre groupes diffère fortement d'une offre à l'autre, et que les groupes aient des taux de base très différents.*

### Application 1.3 — Excel contre pandas (section 1.1.5)

**Objectif.** Faire calculer les mêmes résumés par un classeur Excel (recalculé par LibreOffice Calc) et par pandas, et comprendre les écarts de convention.

**Étape 1 — Écrire un classeur avec des formules.** On y met les paniers de 2025, une formule par statistique (noms anglais du fichier ; Excel en français les affiche traduits).

```python
import tempfile, os
X = O.X
p25 = cmd[cmd["annee"] == 2025]["panier"].round(2)
n = len(p25)
formules = {"moyenne": f"=AVERAGE(A2:A{n+1})", "médiane": f"=MEDIAN(A2:A{n+1})", "Q1": f"=QUARTILE.INC(A2:A{n+1},1)",
            "Q3": f"=QUARTILE.INC(A2:A{n+1},3)", "écart-type": f"=STDEV.S(A2:A{n+1})", "asymétrie": f"=SKEW(A2:A{n+1})", "aplatissement": f"=KURT(A2:A{n+1})"}
dossier = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
lignes_xl = [["panier", None, "statistique", "formule"]] + [[float(v)] for v in p25]
for i, (k, f) in enumerate(formules.items()):
    lignes_xl[i + 1] += [None, k, f]
chemin = X.classeur(os.path.join(dossier, "paniers2025.xlsx"), {"Feuil1": lignes_xl})
```

**Étape 2 — Faire recalculer et comparer.** LibreOffice ouvre le classeur, recalcule toutes les formules, et l'on lit les résultats.

```python
val = X.valeurs(X.recalculer(chemin, dossier))
excel = {k: val[i + 1][3] for i, k in enumerate(formules)}
pandas_ = {"moyenne": p25.mean(), "médiane": p25.median(), "Q1": p25.quantile(.25), "Q3": p25.quantile(.75),
           "écart-type": p25.std(), "asymétrie": p25.skew(), "aplatissement": p25.kurt()}
cmp_ = pd.DataFrame({"Excel (LibreOffice)": excel, "pandas": pandas_})
cmp_["écart"] = (cmp_["Excel (LibreOffice)"] - cmp_["pandas"]).abs()
print(cmp_.round(4))
```
<!--sortie-->
```text
               Excel (LibreOffice)    pandas  écart
moyenne                   102.3300  102.3300    0.0
médiane                    81.6150   81.6150    0.0
Q1                         44.0900   44.0900    0.0
Q3                        137.7200  137.7200    0.0
écart-type                 82.3264   82.3264    0.0
asymétrie                   1.9478    1.9478    0.0
aplatissement               7.0136    7.0136    0.0
```

**Étape 3 — Les conventions qui diffèrent.** `QUARTILE.EXC` et `STDEV.P` ne donnent pas les mêmes valeurs que `QUARTILE.INC` et `STDEV.S`. Voyons-le sur nos neuf commandes.

```python
x9 = np.array([9.69, 207.56, 132.37, 258.83, 66.75, 22.56, 50.27, 48.74, 128.25])
f9 = [["=QUARTILE.INC(A1:A9,1)", "=QUARTILE.EXC(A1:A9,1)", "=STDEV.S(A1:A9)", "=STDEV.P(A1:A9)"]]
c9 = X.classeur(os.path.join(dossier, "neuf.xlsx"), {"F": [[float(v)] + (f9[0] if i == 0 else []) for i, v in enumerate(x9)]})
v9 = X.valeurs(X.recalculer(c9, dossier))[0][1:5]
print(dict(zip(["Q1 inclusif", "Q1 exclusif", "écart-type n-1", "écart-type n"], [round(float(v), 2) for v in v9])))
import shutil; shutil.rmtree(dossier, ignore_errors=True)
```
<!--sortie-->
```text
{'Q1 inclusif': 48.74, 'Q1 exclusif': 35.65, 'écart-type n-1': 85.83, 'écart-type n': 80.92}
```

```python hide
NUM("ecart_max_xl", cmp_["écart"].max())
NUM("q1_exc", v9[1]); NUM("q1_inc", v9[0]); NUM("sd_n", v9[3]); NUM("sd_n1", v9[2])
assert cmp_["écart"].max() < 1e-6 and abs(v9[0] - 48.74) < 1e-9
```
<!--sortie-->
```text
NUM ecart_max_xl 2.8421709430404007e-13
NUM q1_exc 35.65
NUM q1_inc 48.74
NUM sd_n 80.9193830646005
NUM sd_n1 85.8279667416163
```

**Lecture.** Les deux outils concordent à mieux que $10^{-6}$ (écart maximal 2,8e-13) pour les sept statistiques : les formules d'Excel et celles de pandas sont les **mêmes**. Les écarts viennent des **conventions** : sur neuf valeurs, le premier quartile « exclusif » (35,65) diffère du quartile « inclusif » (48,74), et l'écart-type avec $n$ (80,92) est plus petit que celui avec $n-1$ (85,83).

**À vous.** Ajoutez une formule `TRIMMEAN` à 10 % et comparez avec `scipy.stats.trim_mean(p25, 0.05)`. *Piste : `TRIMMEAN(…; 0,1)` retire 10 % **au total**, donc 5 % de chaque côté.*

### Application 1.4 — Quelle loi pour quoi ? (section 1.2)

**Objectif.** Confronter trois lois aux données : binomiale (retours), Poisson (commandes par heure), log-normale (paniers).

**Étape 1 — Binomiale : les retours en Boutique.** Pour 30 lignes vendues en Boutique, combien de retours ? Comparez la loi binomiale à 20 000 tirages.

```python
from scipy.stats import binom
p_b = lig[lig["canal"] == "Boutique"]["retournee"].mean()
rng = np.random.default_rng(11)
bout = lig[lig["canal"] == "Boutique"]["retournee"].values
tir = np.array([rng.choice(bout, 30, replace=False).sum() for _ in range(20000)])
print("p :", round(p_b, 4), "| P(≥ 3) théorique :", round(binom.sf(2, 30, p_b), 4), "| observé :", round((tir >= 3).mean(), 4))
```
<!--sortie-->
```text
p : 0.0308 | P(≥ 3) théorique : 0.0638 | observé : 0.0633
```

**Étape 2 — Poisson : les commandes de la Boutique par heure.** On compte les commandes de la Boutique par heure d'arrivée, pour les samedis de décembre 2025, et l'on compare la variance et la moyenne.

```python
h = cmd[(cmd["canal"] == "Boutique") & (cmd["date_commande"].dt.dayofweek == 5) & (cmd["date_commande"].dt.month == 12) & (cmd["annee"] == 2025)].copy()
h["heure_h"] = h["heure"].str[:2].astype(int)
cpt = h.groupby(["date_commande", "heure_h"]).size().unstack(fill_value=0).stack()   # une valeur par (samedi, heure)
cpt = cpt[cpt.index.get_level_values(1).isin(range(11, 19))]                         # heures pleines
print("moyenne :", round(cpt.mean(), 2), "| variance :", round(cpt.var(), 2), "| variance/moyenne :", round(cpt.var() / cpt.mean(), 2))
```
<!--sortie-->
```text
moyenne : 3.22 | variance : 2.95 | variance/moyenne : 0.92
```

**Étape 3 — Log-normale : les paniers.** On ajuste une loi log-normale (moyenne et écart-type du logarithme) et l'on compare la part de paniers supérieurs à 300 € prévue et observée.

```python
mu, sg = np.log(panier).mean(), np.log(panier).std()
prevu = 1 - stats.norm.cdf((np.log(300) - mu) / sg)
print("part prévue de paniers > 300 € :", round(prevu * 100, 2), "% | observée :", round((panier > 300).mean() * 100, 2), "%")
```
<!--sortie-->
```text
part prévue de paniers > 300 € : 5.54 % | observée : 2.76 %
```

```python hide
NUM("bin_th", binom.sf(2, 30, p_b) * 100); NUM("bin_ob", (tir >= 3).mean() * 100)
NUM("poi_rap", cpt.var() / cpt.mean()); NUM("poi_n", len(cpt))
NUM("ln_prev", prevu * 100); NUM("ln_obs", (panier > 300).mean() * 100)
```
<!--sortie-->
```text
NUM bin_th 6.3811667759166895
NUM bin_ob 6.329999999999999
NUM poi_rap 0.9166927654243658
NUM poi_n 32
NUM ln_prev 5.53763351648181
NUM ln_obs 2.7613683198241517
```

**Lecture.** La binomiale prévoit 6,38 % de lots de 30 lignes avec au moins 3 retours ; on en observe 6,33 %. Pour les arrivées horaires (32 couples samedi-heure), le rapport variance/moyenne vaut 0,92 : proche de 1, mais sur peu de données ; l'écart reste de l'ordre de l'erreur d'estimation. Enfin, la log-normale prévoit 5,5 % de paniers supérieurs à 300 € contre 2,8 % observés : la log-normale **surestime d'un facteur deux** la part des gros paniers : sa queue haute est trop épaisse, comme le montrait le diagramme quantile-quantile du livre (les points se placent sous la droite à droite).

**À vous.** Refaites l'étape 2 sur **tous** les jours de l'année (pas seulement les samedis de décembre) : que devient le rapport variance/moyenne, et pourquoi ?

### Application 1.5 — Simuler un échantillonnage (section 1.3.2)

**Objectif.** Voir l'erreur type, le théorème central limite et la correction de population finie à l'œuvre.

**Étape 1 — L'erreur type selon la taille.** Pour $n$ = 25, 100, 400, tirez 1 000 échantillons de paniers de 2025 et comparez l'écart-type observé des moyennes à $\sigma/\sqrt n$.

```python
pop = cmd[cmd["annee"] == 2025]["panier"].values
rng = np.random.default_rng(21)
lignes_t = []
for n in (25, 100, 400):
    mm = [rng.choice(pop, n, replace=False).mean() for _ in range(1000)]
    lignes_t.append((n, round(np.std(mm), 2), round(pop.std() / np.sqrt(n), 2)))
print(pd.DataFrame(lignes_t, columns=["n", "erreur type observée", "σ/√n"]))
```
<!--sortie-->
```text
     n  erreur type observée   σ/√n
0   25                 16.39  16.46
1  100                  7.84   8.23
2  400                  4.11   4.12
```

**Étape 2 — La forme de la distribution des moyennes.** Mesurez l'asymétrie des moyennes de $n$ paniers pour $n$ = 2, 10, 50, 250.

```python
for n in (2, 10, 50, 250):
    mm = np.array([rng.choice(pop, n, replace=False).mean() for _ in range(2000)])
    print(n, "asymétrie des moyennes :", round(stats.skew(mm), 2))
```
<!--sortie-->
```text
2 asymétrie des moyennes : 1.38
10 asymétrie des moyennes : 0.65
50 asymétrie des moyennes : 0.36
250 asymétrie des moyennes : 0.12
```

**Étape 3 — Population finie.** Avec $n$ = 5 000 sur une population de 12 946, comparez l'erreur type observée à $\sigma/\sqrt n$ et à la formule corrigée.

```python
N, n = len(pop), 5000
mm = [rng.choice(pop, n, replace=False).mean() for _ in range(500)]
print("observée :", round(np.std(mm), 2), "| σ/√n :", round(pop.std() / np.sqrt(n), 2), "| corrigée :", round(pop.std() / np.sqrt(n) * np.sqrt((N - n) / (N - 1)), 2))
```
<!--sortie-->
```text
observée : 0.88 | σ/√n : 1.16 | corrigée : 0.91
```

**Étape 4 — La moyenne contre la médiane.** Quelle est l'erreur type de la médiane d'un échantillon de 100 paniers, comparée à celle de la moyenne ?

```python
med = [np.median(rng.choice(pop, 100, replace=False)) for _ in range(1000)]
moy = [rng.choice(pop, 100, replace=False).mean() for _ in range(1000)]
print("erreur type de la médiane :", round(np.std(med), 2), "| de la moyenne :", round(np.std(moy), 2))
```
<!--sortie-->
```text
erreur type de la médiane : 8.1 | de la moyenne : 8.0
```

```python hide
NUM("n_pop", len(pop))
NUM("se_med", np.std(med)); NUM("se_moy", np.std(moy))
NUM("se_corr_obs", np.std(mm)); NUM("se_corr_f", pop.std() / np.sqrt(5000) * np.sqrt((N - 5000) / (N - 1))); NUM("se_corr_nc", pop.std() / np.sqrt(5000))
```
<!--sortie-->
```text
NUM n_pop 12946
NUM se_med 8.095820657790044
NUM se_moy 7.998472095439353
NUM se_corr_obs 0.8776121986126666
NUM se_corr_f 0.9121386073374633
NUM se_corr_nc 1.1642267807776656
```

**Lecture.** L'erreur type observée colle à $\sigma/\sqrt n$ pour les trois tailles (étape 1). L'asymétrie des moyennes s'efface avec $n$ : le théorème central limite est à l'œuvre (étape 2). Quand l'échantillon est une grande fraction de la population, l'erreur observée (0,88) est plus proche de la formule corrigée (0,91) que de $\sigma/\sqrt n$ (1,16). Enfin, la médiane est à peine **moins précise** que la moyenne pour estimer un centre sur ces données (8,10 contre 8,00) : la robustesse aux valeurs extrêmes coûte ici très peu.

**À vous.** Répétez l'étape 1 avec la population des **clients** (dépense annuelle par client) au lieu des commandes. *Piste : la distribution est encore plus asymétrique ; il faut davantage d'observations pour que la moyenne soit proche d'une normale.*

### Application 1.6 — Intervalles de confiance et biais (sections 1.3.3 à 1.3.6)

**Objectif.** Mesurer la couverture réelle d'intervalles de confiance, comparer deux intervalles de proportion, dimensionner une enquête, puis corriger un biais de sélection.

**Étape 1 — Couverture : $t$ contre 1,96, sur 30 observations.** On construit 2 000 intervalles à 95 % avec des échantillons de 30 paniers, avec le coefficient de Student puis avec 1,96.

```python
pop = cmd[cmd["annee"] == 2025]["panier"].values
mu = pop.mean()
rng = np.random.default_rng(31)
cov_t = cov_z = 0
for _ in range(2000):
    e = rng.choice(pop, 30, replace=False); m, se = e.mean(), e.std(ddof=1) / np.sqrt(30)
    cov_t += abs(m - mu) <= stats.t.ppf(0.975, 29) * se
    cov_z += abs(m - mu) <= 1.96 * se
print("couverture avec t :", cov_t / 2000, "| avec 1,96 :", cov_z / 2000)
```
<!--sortie-->
```text
couverture avec t : 0.925 | avec 1,96 : 0.915
```

**Étape 2 — Wald contre Wilson pour un petit taux.** Le taux de retour de la Boutique est d'environ 3 %. Avec des échantillons de 50 lignes, quelle est la couverture des deux intervalles ?

```python
bout = lig[lig["canal"] == "Boutique"]["retournee"].values
p_v = bout.mean(); cw = cwi = 0
for _ in range(2000):
    k = rng.choice(bout, 50, replace=False).sum()
    w, wi = O.ic_proportion(k, 50), O.ic_proportion(k, 50, methode="wilson")
    cw += w[0] <= p_v <= w[1]; cwi += wi[0] <= p_v <= wi[1]
print("couverture de Wald :", cw / 2000, "| de Wilson :", cwi / 2000)
```
<!--sortie-->
```text
couverture de Wald : 0.785 | de Wilson : 0.931
```

**Étape 3 — Dimensionner une enquête.** Combien de lignes du Site faut-il pour connaître le taux de retour à ±1 point ? Et à ±0,5 point ?

```python
p_s = lig[lig["canal"] == "Site"]["retournee"].mean()
for e in (0.01, 0.005):
    print("marge ±", e * 100, "points :", int(np.ceil(1.96 ** 2 * p_s * (1 - p_s) / e ** 2)), "lignes")
```
<!--sortie-->
```text
marge ± 1.0 points : 3141 lignes
marge ± 0.5 points : 12563 lignes
```

**Étape 4 — Corriger un biais de sélection.** On tire 300 commandes (méthode « croisés à la caisse ») et l'on compte les commandes de leur client ; on corrige ensuite en pondérant chaque observation par l'**inverse** de la probabilité de l'avoir tirée, proportionnelle au nombre de commandes du client.

```python
cpt = cmd.groupby("id_client").size()                       # commandes par client (clients ayant commandé)
ech = rng.choice(cmd["id_client"].values, 300)               # on croise des commandes
brut = cpt.loc[ech].mean()
corrige = len(ech) / (1 / cpt.loc[ech]).sum()               # moyenne pondérée par 1/n_i : moyenne harmonique
print("brut :", round(brut, 2), "| corrigé :", round(corrige, 2), "| vérité (clients ayant commandé) :", round(cpt.mean(), 2))
```
<!--sortie-->
```text
brut : 16.33 | corrigé : 7.61 | vérité (clients ayant commandé) : 7.57
```

```python hide
NUM("cov_t", cov_t / 2000 * 100); NUM("cov_z", cov_z / 2000 * 100)
NUM("cov_w", cw / 2000 * 100); NUM("cov_wi", cwi / 2000 * 100)
NUM("n_site1", np.ceil(1.96 ** 2 * p_s * (1 - p_s) / 0.01 ** 2)); NUM("n_site05", np.ceil(1.96 ** 2 * p_s * (1 - p_s) / 0.005 ** 2))
NUM("brut", brut); NUM("corrige", corrige); NUM("vrai_actifs", cpt.mean())
```
<!--sortie-->
```text
NUM cov_t 92.5
NUM cov_z 91.5
NUM cov_w 78.5
NUM cov_wi 93.10000000000001
NUM n_site1 3141.0
NUM n_site05 12563.0
NUM brut 16.33
NUM corrige 7.611277806743095
NUM vrai_actifs 7.5728256346233875
```

**Lecture.** Avec 30 observations, l'intervalle de Student couvre 92,5 % des fois, contre 91,5 % pour 1,96 : le coefficient de Student corrige, un peu, le petit échantillon (et l'asymétrie des paniers empêche d'atteindre 95 %). Pour un taux de 3 % mesuré sur 50 lignes, l'intervalle de Wald couvre 78,5 % des fois seulement, celui de Wilson 93,1 % : Wilson est nettement meilleur. Pour connaître le taux de retour du Site à ±1 point, il faut 3 141 lignes, et 12 563 à ±0,5 point (quatre fois plus). Enfin, la pondération par l'inverse du nombre de commandes ramène l'estimation à 7,6, tout près de la vérité des clients ayant commandé (7,6) alors que l'estimation brute valait 16,3 ; mais elle ne peut rien pour les clients **qui n'ont jamais commandé** : une fois exclus du tirage, ils ne reviennent pas.

**À vous.** Refaites l'étape 4 avec 3 000 commandes : le biais brut change-t-il ? *Piste : non, c'est l'intérêt de l'exemple : un biais de sélection ne diminue pas avec la taille de l'échantillon.*

### Application 1.7 — Corrélation, confusion et saison (section 1.4)

**Objectif.** Refaire l'enquête sur la publicité et les ventes : corrélation brute, corrélation à mois égal, effet ajusté, comparaison avec la vérité programmée.

**Étape 1 — La corrélation brute.** Pearson et Spearman entre la dépense publicitaire du jour et le chiffre d'affaires du jour.

```python
j = jours.copy()
print("Pearson :", round(j["depense_pub"].corr(j["chiffre_affaires"]), 3), "| Spearman :", round(j["depense_pub"].corr(j["chiffre_affaires"], method="spearman"), 3))
```
<!--sortie-->
```text
Pearson : 0.415 | Spearman : 0.286
```

**Étape 2 — À mois égal.** On retire la moyenne de chaque mois, puis on corrèle les écarts.

```python
for c in ("depense_pub", "chiffre_affaires"):
    j[c + "_ecart"] = j[c] - j.groupby("mois")[c].transform("mean")
print("corrélation à mois égal :", round(j["depense_pub_ecart"].corr(j["chiffre_affaires_ecart"]), 3))
```
<!--sortie-->
```text
corrélation à mois égal : 0.049
```

**Étape 3 — Effet ajusté.** Une régression du logarithme du nombre de commandes sur la dépense hebdomadaire, avec ou sans neutralisation du calendrier.

```python
import statsmodels.formula.api as smf
j["pub7k"] = j["depense_pub"].rolling(7, min_periods=1).sum() / 1000
j["pluvieux"] = (j["pluie_mm"] > 1).astype(int); j["t"] = np.arange(len(j)) / 365.25; j["lc"] = np.log(j["nb_commandes"])
m0 = smf.ols("lc ~ pub7k", data=j).fit()
m1 = smf.ols("lc ~ pub7k + C(mois) + C(jour_sem) + promo_active + t + pluvieux", data=j).fit()
for nom, m in (("naïf", m0), ("ajusté", m1)):
    lo, hi = m.conf_int().loc["pub7k"]
    print(nom, ": +", round((np.exp(m.params["pub7k"]) - 1) * 100, 1), "% (", round((np.exp(lo) - 1) * 100, 1), "à", round((np.exp(hi) - 1) * 100, 1), ")")
print("promotion : +", round((np.exp(m1.params["promo_active"]) - 1) * 100, 1), "% | tendance annuelle : +", round((np.exp(m1.params["t"]) - 1) * 100, 1), "%")
```
<!--sortie-->
```text
naïf : + 31.9 % ( 28.2 à 35.7 )
ajusté : + 0.7 % ( -3.7 à 5.4 )
promotion : + 19.2 % | tendance annuelle : + 6.5 %
```

**Étape 4 — Des corrélations fortuites.** Avec 50 variables aléatoires de 30 observations, combien de paires dépassent 0,36 en valeur absolue ?

```python
rng = np.random.default_rng(5)
rr = np.corrcoef(rng.normal(size=(30, 50)).T)[np.triu_indices(50, 1)]
print("paires :", len(rr), "| |r| > 0,36 :", int((abs(rr) > 0.36).sum()), "| attendu sous l'indépendance : environ", round(0.05 * len(rr)))
```
<!--sortie-->
```text
paires : 1225 | |r| > 0,36 : 55 | attendu sous l'indépendance : environ 61
```

```python hide
NUM("a_pearson", j["depense_pub"].corr(j["chiffre_affaires"])); NUM("a_intra", j["depense_pub_ecart"].corr(j["chiffre_affaires_ecart"]))
NUM("a_naif", (np.exp(m0.params["pub7k"]) - 1) * 100); NUM("a_adj", (np.exp(m1.params["pub7k"]) - 1) * 100)
NUM("a_promo", (np.exp(m1.params["promo_active"]) - 1) * 100); NUM("a_fortuit", (abs(rr) > 0.36).sum()); NUM("a_pairs", len(rr))
```
<!--sortie-->
```text
NUM a_pearson 0.41517601017459865
NUM a_intra 0.04898908594976713
NUM a_naif 31.908406760730635
NUM a_adj 0.7315144144337093
NUM a_promo 19.175378725848002
NUM a_fortuit 55
NUM a_pairs 1225
```

**Lecture.** La corrélation brute (0,42) tombe à 0,05 une fois comparés des jours du **même mois**. L'effet « naïf » de 1 000 € de dépense hebdomadaire est de +32 % des commandes, l'effet ajusté de +0,7 % (vérité programmée : +1,5 %, mais l'intervalle est trop large pour conclure). L'effet de la promotion, lui, est retrouvé : +19 % (vérité : +18 %). Enfin, sur 1 225 paires de variables sans lien, 55 dépassent 0,36.

**À vous.** Estimez l'effet de la **pluie** sur les commandes du canal Boutique seul (comptez les commandes de la Boutique par jour). *Piste : la vérité programmée est −8 % pour la Boutique et +5 % pour le Site ; sur le total les deux effets se compensent presque.*

### Application 1.8 — Mathématiques du quotidien (section 1.5)

**Objectif.** Calculer des croissances, décomposer prix et volume par catégorie, mesurer les marges, et chiffrer l'effet d'une règle d'arrondi.

**Étape 1 — Croissance par canal.** Chiffre d'affaires annuel de chaque canal, taux annuel et TCAM 2023-2025.

```python
ca = lig.groupby(["canal", "annee"])["montant"].sum().unstack()
tab = pd.DataFrame({"2024/2023 %": (ca[2024] / ca[2023] - 1) * 100, "2025/2024 %": (ca[2025] / ca[2024] - 1) * 100,
                    "TCAM %": ((ca[2025] / ca[2023]) ** 0.5 - 1) * 100}).round(2)
print(tab)
```
<!--sortie-->
```text
          2024/2023 %  2025/2024 %  TCAM %
canal                                     
Boutique        -5.98         0.51   -2.79
Réseaux          4.81        13.42    9.03
Site            18.96        22.92   20.92
```

**Étape 2 — Prix et volume par catégorie (2025 contre 2024).** Pour chaque catégorie : croissance des unités, du chiffre d'affaires moyen par unité, et du chiffre d'affaires.

```python
g = lig[lig["annee"].isin([2024, 2025])].groupby(["categorie", "annee"]).agg(ca=("montant", "sum"), u=("quantite", "sum")).unstack()
dec = pd.DataFrame({"volume %": (g["u"][2025] / g["u"][2024] - 1) * 100,
                    "prix-mix %": ((g["ca"][2025] / g["u"][2025]) / (g["ca"][2024] / g["u"][2024]) - 1) * 100,
                    "CA %": (g["ca"][2025] / g["ca"][2024] - 1) * 100}).round(1)
print(dec)
```
<!--sortie-->
```text
            volume %  prix-mix %  CA %
categorie                             
Bien-être        6.2         3.1   9.5
Cuisine          4.2         3.1   7.4
Décoration       7.3         2.5  10.1
Jardin           9.7         4.2  14.3
Maison          10.1         3.0  13.4
Papeterie        6.6         3.0   9.8
```

**Étape 3 — Marque par canal.** Taux de marque 2025 (CA HT = montant / 1,2) de chaque canal : moyenne pondérée et moyenne simple des catégories.

```python
l25 = lig[lig["annee"] == 2025].assign(ca_ht=lambda t: t["montant"] / 1.2, cout=lambda t: t["quantite"] * t["cout_achat"])
par = l25.groupby("canal")[["ca_ht", "cout"]].sum()
print(((par["ca_ht"] - par["cout"]) / par["ca_ht"] * 100).round(2).to_dict())
```
<!--sortie-->
```text
{'Boutique': 38.0, 'Réseaux': 38.11, 'Site': 37.88}
```

**Étape 4 — L'effet d'une règle d'arrondi.** La TVA incluse dans chaque ligne de 2025 est $\text{montant}-\text{montant}/1{,}2$. Comparez la somme des TVA **arrondies ligne par ligne** à la TVA calculée sur le total.

```python
l25["tva"] = l25["montant"] - l25["montant"] / 1.2
ligne = l25["tva"].round(2).sum()                       # arrondi (au pair) ligne par ligne
total = round(l25["tva"].sum(), 2)
print("TVA arrondie ligne par ligne :", round(ligne, 2), "| TVA sur le total :", total, "| écart :", round(ligne - total, 2), "€ sur", len(l25), "lignes")
```
<!--sortie-->
```text
TVA arrondie ligne par ligne : 220785.54 | TVA sur le total : 220793.95 | écart : -8.41 € sur 29827 lignes
```

```python hide
NUM("tcam_site", tab.loc["Site", "TCAM %"]); NUM("tcam_bout", tab.loc["Boutique", "TCAM %"])
NUM("vol_min", dec["volume %"].min()); NUM("vol_max", dec["volume %"].max()); NUM("pm_min", dec["prix-mix %"].min()); NUM("pm_max", dec["prix-mix %"].max())
NUM("marque_c_min", ((par["ca_ht"] - par["cout"]) / par["ca_ht"] * 100).min()); NUM("marque_c_max", ((par["ca_ht"] - par["cout"]) / par["ca_ht"] * 100).max())
NUM("ecart_tva", ligne - total); NUM("nl25", len(l25))
```
<!--sortie-->
```text
NUM tcam_site 20.92
NUM tcam_bout -2.79
NUM vol_min 4.2
NUM vol_max 10.1
NUM pm_min 2.5
NUM pm_max 4.2
NUM marque_c_min 37.88208211402192
NUM marque_c_max 38.11122499526953
NUM ecart_tva -8.410000000003492
NUM nl25 29827
```

**Lecture.** Le Site croît de 20,9 % par an, la Boutique de -2,8 % (elle recule) : le déplacement vers le Site se lit dans les TCAM. Par catégorie, la croissance en volume va de 4,2 % à 10,1 % et l'effet prix-mix de 2,5 % à 4,2 % : la hausse de 3 % du catalogue est partout, mais le mix et les remises la modulent. Les taux de marque des canaux ne diffèrent presque pas (37,9 à 38,1 %). Enfin, la règle d'arrondi ligne par ligne produit un écart de -8,41 € sur 29 827 lignes : faible en valeur relative, mais **à documenter**.

**À vous.** Refaites l'étape 4 en arrondissant **par commande** (somme des montants de chaque commande, puis TVA arrondie). *Piste : trois règles, trois totaux ; aucune n'est « fausse », mais il faut en choisir une et la noter.*

## Exercices

### Exercice 1.1 ⭐ — Moyenne et médiane à la main (section 1.1.1)

Sept paniers (en €) : 12 ; 45 ; 38 ; 60 ; 22 ; 51 ; 340. Calculez la moyenne et la médiane. Que deviennent-elles si l'on retire 340 ? Quel résumé annonceriez-vous pour décrire une commande « typique » ?

### Exercice 1.2 ⭐ — Écart-type d'un petit échantillon (section 1.1.2)

Cinq délais de livraison (jours) : 2 ; 3 ; 3 ; 4 ; 8. Calculez la moyenne, la variance (avec $n-1$), l'écart-type et le coefficient de variation.

### Exercice 1.3 ⭐⭐ — La règle de 1,5 écart interquartile (section 1.1.3)

Onze paniers (en €) : 18 ; 22 ; 25 ; 27 ; 30 ; 31 ; 35 ; 38 ; 42 ; 47 ; 190. (a) Calculez $Q_1$, $Q_3$ et l'EIQ (méthode inclusive). (b) Quelles valeurs la règle de Tukey signale-t-elle ? (c) Que feriez-vous de cette valeur avant de calculer la moyenne ?

### Exercice 1.4 ⭐ — Moyenne des moyennes (section 1.1.4)

Une enquête de satisfaction a eu trois groupes de répondants : 400 clients de la Boutique (85 % de satisfaits), 100 clients des Réseaux (60 %), 500 clients du Site (70 %). Calculez le taux de satisfaits de l'ensemble, puis la moyenne simple des trois taux. Expliquez l'écart.

### Exercice 1.5 ⭐⭐ — Un renversement de Simpson (section 1.1.4)

Deux offres sont envoyées à deux groupes de clients. Offre P : 300 envois au groupe « facile » (180 achats) et 100 au groupe « difficile » (20 achats). Offre Q : 100 envois au groupe facile (65 achats) et 300 au groupe difficile (75 achats). Calculez les taux par groupe puis au total. Quelle offre est la meilleure ? Quel conseil donneriez-vous ?

### Exercice 1.6 ⭐ — Score $z$ et normale (section 1.2.3)

L'âge des clients a une moyenne de 43,3 ans et un écart-type de 13,7 ans. Calculez le score $z$ d'une cliente de 25 ans et d'un client de 65 ans, puis la part approximative des clients entre 30 et 56 ans si l'âge était exactement normal.

### Exercice 1.7 ⭐⭐ — Binomiale et Poisson à la main (section 1.2.2)

(a) En Boutique, le taux de retour est de 3 %. Sur un lot de 30 lignes, quelle est la probabilité qu'aucune ne soit retournée ? Qu'au moins deux le soient ? (b) La Boutique reçoit en moyenne 4 commandes par heure creuse. Quelle est la probabilité de n'en recevoir **aucune** pendant une heure ? D'en recevoir 8 ou plus ?

### Exercice 1.8 ⭐ — Erreur type (section 1.3.2)

L'écart-type des paniers est de 80 €. Quelle est l'erreur type de la moyenne pour $n=64$ ? Pour $n=256$ ? Quelle taille d'échantillon donne une erreur type de 2,5 € ?

### Exercice 1.9 ⭐⭐ — Intervalle de confiance d'une proportion (section 1.3.4)

Sur 400 avis, 120 déclarent être « très satisfaits ». Donnez le taux observé et l'intervalle de confiance à 95 % de Wald. Pouvez-vous affirmer que le vrai taux dépasse 25 % ? Que dit l'intervalle de Wilson ?

### Exercice 1.10 ⭐⭐ — Taille d'échantillon (section 1.3.5)

(a) Combien de paniers faut-il pour estimer le panier moyen à ±4 € près, avec un écart-type supposé de 80 € ? (b) Combien de répondants pour estimer une proportion proche de 30 % à ±3 points ? (c) Si la population ne compte que 2 000 clients, de combien cet effectif se réduit-il (formule corrigée $n'=n/(1+(n-1)/N)$) ?

### Exercice 1.11 ⭐ — Corrélation à la main (section 1.4.1)

Cinq jours : dépense publicitaire (centaines d'euros) $x=1;2;3;4;5$ et nombre de commandes $y=2;4;5;4;5$. Calculez $r$ à la main (tableau des écarts). Que dire de $r^2$ ?

### Exercice 1.12 ⭐⭐⭐ — Concevoir une expérience (section 1.4.6)

La gérante constate que les clients qui **ouvrent** les e-mails de la boutique achètent plus que ceux qui ne les ouvrent pas, et conclut : « les e-mails font vendre ». (a) Donnez trois explications **non causales** de cette corrélation. (b) Décrivez une expérience aléatoire qui permettrait de trancher. (c) Si le taux d'achat de référence est de 10 % et que vous voulez détecter une hausse de 2 points, la formule indicative $n=2\,(1{,}96+0{,}84)^2\,\bar p(1-\bar p)/\delta^2$ (avec $\bar p$ proche de 0,11 et $\delta=0{,}02$) donne combien de clients **par groupe** ?

### Exercice 1.13 ⭐ — Pourcentages en cascade (section 1.5.1)

(a) Un prix de 80 € augmente de 25 %, puis baisse de 20 %. Quel est le prix final, quelle est la variation totale ? (b) Un prix TTC est de 96 € avec une TVA de 20 % : quel est le prix HT ? (c) La part du Site passe de 35 % à 45 % des commandes : exprimez l'évolution en points et en pourcentage.

### Exercice 1.14 ⭐⭐ — Marge, marque, TVA (section 1.5.4)

Un produit est acheté 18 € HT. (a) On veut un taux de **marque** de 35 % : quel prix HT, quel prix TTC (TVA à 20 %) ? (b) Quel est alors le taux de **marge** ? (c) Si l'on avait appliqué à tort 35 % au coût d'achat, quel taux de marque aurait-on obtenu ?

## Corrigés

### Corrigé 1.1

Total $=568$, donc moyenne $=568/7\approx81{,}1$ €. Rangés : 12 ; 22 ; 38 ; 45 ; 51 ; 60 ; 340, la médiane est la quatrième valeur : **45 €**. Sans 340 : moyenne $228/6=38$ €, médiane $(38+45)/2=41{,}5$ €. La moyenne chute de 81,1 à 38 €, la médiane de 45 à 41,5 € : la médiane est robuste. Pour une commande « typique », on annonce la **médiane** (45 €), en précisant qu'une commande atypique de 340 € tire la moyenne.

```python
v = np.array([12, 45, 38, 60, 22, 51, 340]); w = np.delete(v, 6)
print(round(v.mean(), 1), np.median(v), round(w.mean(), 1), np.median(w))
```
<!--sortie-->
```text
81.1 45.0 38.0 41.5
```

### Corrigé 1.2

Moyenne $=20/5=4$ jours. Écarts : −2 ; −1 ; −1 ; 0 ; 4, carrés : 4 ; 1 ; 1 ; 0 ; 16, somme 22. Variance $=22/4=5{,}5$, écart-type $\sqrt{5{,}5}\approx2{,}35$ jours, coefficient de variation $2{,}35/4\approx0{,}59$. La valeur 8 contribue à elle seule à 16/22 de la somme : un seul retard pèse lourd dans la dispersion.

```python
v = np.array([2, 3, 3, 4, 8]); print(v.mean(), v.var(ddof=1), round(v.std(ddof=1), 3), round(v.std(ddof=1) / v.mean(), 2))
```
<!--sortie-->
```text
4.0 5.5 2.345 0.59
```

### Corrigé 1.3

(a) Avec $n=11$, $Q_1$ est à la position $1+0{,}25\times10=3{,}5$ : entre 25 et 27, soit **26** ; $Q_3$ à la position $8{,}5$ : entre 38 et 42, soit **40**. EIQ $=14$. (b) Bornes : $26-21=5$ et $40+21=61$. La valeur **190** dépasse 61 : elle est signalée ; les autres sont dans l'intervalle. (c) On vérifie d'abord si c'est une erreur (virgule décalée : 19,0 ? ), un client professionnel, ou une grosse commande légitime ; on **ne la supprime pas** sans raison, on annonce la médiane en plus de la moyenne, ou l'on calcule la moyenne avec et sans cette valeur.

```python
v = np.array([18, 22, 25, 27, 30, 31, 35, 38, 42, 47, 190]); q1, q3 = np.quantile(v, [.25, .75]); print(q1, q3, q1 - 1.5 * (q3 - q1), q3 + 1.5 * (q3 - q1))
```
<!--sortie-->
```text
26.0 40.0 5.0 61.0
```

### Corrigé 1.4

Satisfaits : $0{,}85\times400+0{,}60\times100+0{,}70\times500=340+60+350=750$ sur 1 000, soit **75 %**. Moyenne simple : $(85+60+70)/3\approx71{,}7$ %. L'écart (3,3 points) vient de ce que la moyenne simple donne au groupe de 100 clients (le plus faible taux) le même poids qu'aux autres. La bonne moyenne est la moyenne **pondérée par les effectifs**.

```python
print((0.85 * 400 + 0.6 * 100 + 0.7 * 500) / 1000, np.mean([0.85, 0.6, 0.7]))
```
<!--sortie-->
```text
0.75 0.7166666666666667
```

### Corrigé 1.5

Offre P : groupe facile $180/300=60\ \%$, difficile $20/100=20\ \%$, total $200/400=50\ \%$. Offre Q : facile $65/100=65\ \%$, difficile $75/300=25\ \%$, total $140/400=35\ \%$. Q est meilleure **dans chaque groupe** (65 > 60 et 25 > 20) mais P l'est **au total** (50 > 35) : c'est le paradoxe de Simpson, dû à la composition différente des envois (P a visé surtout le groupe facile, Q surtout le groupe difficile). Conseil : comparer les offres **à groupe égal** (ou envoyer les deux offres, au hasard, à la même population), et conclure que Q est la meilleure offre.

```python
print(180 / 300, 20 / 100, 200 / 400, 65 / 100, 75 / 300, 140 / 400)
```
<!--sortie-->
```text
0.6 0.2 0.5 0.65 0.25 0.35
```

### Corrigé 1.6

$z_{25}=(25-43{,}3)/13{,}7\approx-1{,}34$ ; $z_{65}=(65-43{,}3)/13{,}7\approx+1{,}58$. Entre 30 et 56 ans : $z$ de $-0{,}97$ à $+0{,}93$ ; la part vaut $\Phi(0{,}93)-\Phi(-0{,}97)\approx0{,}824-0{,}166=0{,}658$, soit environ **66 %** (proche des 68 % de la règle à ±1 écart-type, puisque 30 et 56 ans sont à peu près à ±1 écart-type).

```python
print(round((25 - 43.3) / 13.7, 2), round((65 - 43.3) / 13.7, 2), round(stats.norm.cdf((56 - 43.3) / 13.7) - stats.norm.cdf((30 - 43.3) / 13.7), 3))
```
<!--sortie-->
```text
-1.34 1.58 0.657
```

### Corrigé 1.7

(a) $P(K=0)=0{,}97^{30}\approx0{,}401$. $P(K\ge2)=1-P(0)-P(1)$, avec $P(1)=30\times0{,}03\times0{,}97^{29}\approx0{,}372$ : donc $1-0{,}401-0{,}372\approx\mathbf{0{,}227}$. (b) $P(N=0)=e^{-4}\approx\mathbf{0{,}0183}$ ; $P(N\ge8)=1-P(N\le7)\approx\mathbf{0{,}051}$ (le calcul exige la somme des huit premiers termes ; voir le code).

```python
from scipy.stats import binom, poisson
print(round(binom.pmf(0, 30, 0.03), 3), round(binom.sf(1, 30, 0.03), 3), round(poisson.pmf(0, 4), 4), round(poisson.sf(7, 4), 3))
```
<!--sortie-->
```text
0.401 0.227 0.0183 0.051
```

### Corrigé 1.8

Erreur type $=\sigma/\sqrt n$ : $80/8=10$ € pour $n=64$, $80/16=5$ € pour $n=256$ (quadrupler $n$ divise par 2). Pour 2,5 € : $\sqrt n=80/2{,}5=32$, donc $n=1\,024$.

```python
print(80 / np.sqrt(64), 80 / np.sqrt(256), (80 / 2.5) ** 2)
```
<!--sortie-->
```text
10.0 5.0 1024.0
```

### Corrigé 1.9

$\hat p=120/400=30\ \%$. Erreur type $\sqrt{0{,}3\times0{,}7/400}\approx0{,}0229$ ; marge $1{,}96\times0{,}0229\approx0{,}045$ ; intervalle de Wald **[25,5 % ; 34,5 %]**. Il exclut (de peu) 25 % : on peut dire que le taux dépasse 25 % avec une confiance de 95 %, mais « de peu ». L'intervalle de Wilson, [25,7 % ; 34,7 %], est un peu décalé vers le centre et conduit à la même conclusion.

```python
print(np.round(O.ic_proportion(120, 400), 4), np.round(O.ic_proportion(120, 400, methode="wilson"), 4))
```
<!--sortie-->
```text
[0.2551 0.3449] [0.2572 0.3466]
```

### Corrigé 1.10

(a) $n=(1{,}96\times80/4)^2=39{,}2^2\approx1\,536{,}6$, soit **1 537** paniers (on arrondit à l'entier supérieur). (b) $n=1{,}96^2\times0{,}3\times0{,}7/0{,}03^2\approx896{,}4$, soit **897** répondants. (c) $n'=897/(1+896/2000)=897/1{,}448\approx619$ : la population finie réduit l'effectif nécessaire d'environ 30 %.

```python
print(int(np.ceil((1.96 * 80 / 4) ** 2)), int(np.ceil(1.96 ** 2 * 0.21 / 0.03 ** 2)), round(897 / (1 + 896 / 2000)))
```
<!--sortie-->
```text
1537 897 619
```

### Corrigé 1.11

$\bar x=3$, $\bar y=4$. Écarts $x$ : −2 ; −1 ; 0 ; 1 ; 2 ; écarts $y$ : −2 ; 0 ; 1 ; 0 ; 1. Produits : 4 ; 0 ; 0 ; 0 ; 2, somme 6. $\sum(x-\bar x)^2=10$, $\sum(y-\bar y)^2=6$. $r=6/\sqrt{10\times6}=6/7{,}746\approx\mathbf{0{,}775}$ et $r^2\approx0{,}6$ : environ 60 % de la variation des commandes est « partagée » avec celle de la dépense le long d'une droite. Avec **cinq** points, ce chiffre est très instable.

```python
x = np.array([1, 2, 3, 4, 5]); y = np.array([2, 4, 5, 4, 5]); print(round(np.corrcoef(x, y)[0, 1], 3), round(np.corrcoef(x, y)[0, 1] ** 2, 2))
```
<!--sortie-->
```text
0.775 0.6
```

### Corrigé 1.12

(a) Explications non causales : (1) les clients qui ouvrent les e-mails sont déjà **plus engagés** (ils aiment la boutique, ils achetaient déjà beaucoup) : confusion ; (2) un client qui vient d'acheter **ouvre** davantage les e-mails de suivi (causalité inverse) ; (3) ouvrir est plus fréquent chez les clients avec carte et adresse valide, qui achètent plus (confusion par le profil). (b) Tirer **au hasard** la moitié des clients (parmi ceux qui ont consenti) qui recevront l'e-mail, l'autre moitié ne le recevant pas, et comparer le taux d'achat sur une période fixée à l'avance. (c) $n=2\times2{,}8^2\times0{,}11\times0{,}89/0{,}02^2\approx\mathbf{3\,838}$ clients par groupe.

```python
print(round(2 * (1.96 + 0.84) ** 2 * 0.11 * 0.89 / 0.02 ** 2))
```
<!--sortie-->
```text
3838
```

### Corrigé 1.13

(a) $80\times1{,}25=100$ puis $100\times0{,}80=80$ : le prix final est **80 €**, la variation totale **0 %** (+25 % puis −20 % se compensent exactement : $1{,}25\times0{,}8=1$). (b) Prix HT $=96/1{,}2=80$ €. (c) En **points** : +10 points. En **pourcentage** : $(45-35)/35\approx+28{,}6\ \%$.

```python
print(80 * 1.25 * 0.8, 96 / 1.2, 45 - 35, round((45 / 35 - 1) * 100, 1))
```
<!--sortie-->
```text
80.0 80.0 10 28.6
```

### Corrigé 1.14

(a) Prix HT $=18/(1-0{,}35)\approx27{,}69$ €, prix TTC $=27{,}69\times1{,}2\approx33{,}23$ €. (b) Marge $=27{,}69-18=9{,}69$ €, taux de marge $=9{,}69/18\approx53{,}8\ \%$ (on retrouve $0{,}35/0{,}65=0{,}538$). (c) Avec +35 % sur le coût, prix HT $=18\times1{,}35=24{,}30$ €, marge $6{,}30$ €, taux de marque $6{,}30/24{,}30\approx25{,}9\ \%$, bien moins que les 35 % voulus.

```python
ht = 18 / (1 - 0.35); print(round(ht, 2), round(ht * 1.2, 2), round((ht - 18) / 18 * 100, 1), round((18 * 1.35 - 18) / (18 * 1.35) * 100, 1))
```
<!--sortie-->
```text
27.69 33.23 53.8 25.9
```
