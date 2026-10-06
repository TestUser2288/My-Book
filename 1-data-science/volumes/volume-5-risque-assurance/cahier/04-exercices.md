# Chapitre 4 : Cadre réglementaire — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 4 du livre. Les **applications** refont pas à pas ce que le livre a résumé : le capital IRB d'un portefeuille de prêts, la simulation de la perte au quantile 99,9 %, la procyclicité du capital, l'agrégation du capital de solvabilité d'un assureur, sa marge de risque et sa résistance aux chocs, la marge sur services contractuels d'IFRS 17, la comparaison de modèles de Takaful, et la détection d'opérations suspectes. Les **exercices** (⭐ à ⭐⭐⭐) s'appuient sur les sections du livre ; chacun a son corrigé en fin de fichier. Tous les paramètres (coefficients, matrice de corrélation, taux de frais, seuils d'alerte) sont des **valeurs d'illustration** ; rien ici n'est un conseil juridique, comptable ou financier, et les textes réglementaires en vigueur dans votre juridiction priment.

## Préparation

Une seule cellule recharge les données et refait le modèle de probabilité de défaut du livre (régression logistique estimée sur une moitié de l'échantillon, appliquée à l'autre moitié) ainsi que les fonctions du chapitre, rangées dans `build/outils_ch04.py` : formule IRB, agrégation du capital de solvabilité, simulation d'un fonds de Takaful, variables par compte pour la lutte contre le blanchiment. Toutes les données sont **simulées** (graines fixes).

```python
import os, sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np
import pandas as pd
from scipy.stats import norm
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from outils_ch04 import *

credits = charger("credits_conso.csv")
recouv = charger("recouvrements.csv")
Xc = pd.get_dummies(credits.drop(columns=["id_credit", "defaut_12m"]), drop_first=True).astype(float)
Xc = Xc.fillna(Xc.median())
Xa, Xb, ya, yb = train_test_split(Xc, credits["defaut_12m"], test_size=0.5, random_state=0)
mu_c, sd_c = Xa.mean(), Xa.std()
pd_hat = LogisticRegression(max_iter=3000).fit((Xa - mu_c) / sd_c, ya).predict_proba((Xb - mu_c) / sd_c)[:, 1]
LGD = round(recouv["lgd_realisee"].mean(), 2)
pf = pd.DataFrame({"pd": np.clip(pd_hat, 0.0003, 0.60), "ead": credits.loc[Xb.index, "montant"].values * 0.7, "defaut": yb.values})
EAD = pf["ead"].sum()
print("prêts :", len(pf), "| exposition (M€) :", round(EAD / 1e6, 1), "| LGD :", LGD, "| PD moyenne :", round(pf["pd"].mean(), 4))
```
<!--sortie-->
```text
prêts : 20000 | exposition (M€) : 135.5 | LGD : 0.46 | PD moyenne : 0.0582
```

## Applications

### Application 4.1 — Le capital IRB d'un portefeuille, de la PD au poids de risque

*Sections du livre : 4.1.4, 4.1.5.* **Objectif :** calculer la perte attendue, le capital et les actifs pondérés d'un portefeuille de prêts, puis regarder **où** se concentre le capital.

**Étape 1 — Le capital de chaque prêt.** `k_detail` applique la formule « autres expositions de détail » : corrélation d'actifs fonction de la PD, pas d'ajustement d'échéance, plancher de PD à 0,03 %.

```python
pf["k"] = k_detail(pf["pd"], LGD)                 # capital par euro d'exposition
pf["rwa"] = 12.5 * pf["k"] * pf["ead"]            # actifs pondérés
EL = (pf["pd"] * LGD * pf["ead"]).sum()
print("perte attendue : %.2f M€ (%.2f %%)" % (EL / 1e6, 100 * EL / EAD))
print("capital IRB    : %.2f M€ (%.2f %%)" % ((pf["k"] * pf["ead"]).sum() / 1e6, 100 * (pf["k"] * pf["ead"]).sum() / EAD))
print("RWA IRB        : %.1f M€ (poids moyen %.1f %%) contre %.1f M€ en standard à 75 %%" % (
    pf["rwa"].sum() / 1e6, 100 * pf["rwa"].sum() / EAD, 0.75 * EAD / 1e6))
```
<!--sortie-->
```text
perte attendue : 4.47 M€ (3.30 %)
capital IRB    : 7.44 M€ (5.49 %)
RWA IRB        : 93.0 M€ (poids moyen 68.6 %) contre 101.6 M€ en standard à 75 %
```

**Étape 2 — Où est le capital ?** On découpe le portefeuille en cinq classes de PD de même effectif (quintiles) et on regarde, par classe, la PD moyenne, le poids de risque IRB et la part du capital total.

```python
pf["classe"] = pd.qcut(pf["pd"], 5, labels=["C1 (sûrs)", "C2", "C3", "C4", "C5 (risqués)"])
g = pf.groupby("classe", observed=True)
tab = pd.DataFrame({"PD moyenne (%)": 100 * g["pd"].mean(), "exposition (M€)": g["ead"].sum() / 1e6,
                    "poids IRB (%)": 100 * g["rwa"].sum() / g["ead"].sum(),
                    "part du capital (%)": 100 * g["rwa"].sum() / pf["rwa"].sum(),
                    "défauts observés (%)": 100 * g["defaut"].mean()})
print(tab.round(1).to_string())
```
<!--sortie-->
```text
              PD moyenne (%)  exposition (M€)  poids IRB (%)  part du capital (%)  défauts observés (%)
classe                                                                                                 
C1 (sûrs)                1.0             22.7           44.3                 10.8                   1.0
C2                       2.2             24.2           60.3                 15.7                   2.7
C3                       3.6             25.5           65.7                 18.0                   4.0
C4                       6.0             27.6           69.4                 20.6                   6.2
C5 (risqués)            16.3             35.5           91.3                 34.9                  16.2
```

**Étape 3 — IRB contre standard, classe par classe.** Le poids standard (75 %) ne dépend pas de la classe : en quelles classes le modèle interne est-il plus favorable, et dans lesquelles plus sévère ?

```python
tab["gain IRB vs standard (points de poids)"] = 75 - tab["poids IRB (%)"]
print(tab[["poids IRB (%)", "gain IRB vs standard (points de poids)"]].round(1).to_string())
```
<!--sortie-->
```text
              poids IRB (%)  gain IRB vs standard (points de poids)
classe                                                             
C1 (sûrs)              44.3                                    30.7
C2                     60.3                                    14.7
C3                     65.7                                     9.3
C4                     69.4                                     5.6
C5 (risqués)           91.3                                   -16.3
```

**Lecture.** La perte attendue est de 4,47 M€ (3,3 % de l'exposition) et le capital de 7,44 M€ (5,5 %), soit un poids de risque moyen de 68,6 % contre 75 % en standard. **Le capital se concentre sur les mauvais emprunteurs** : la classe la plus risquée (C5, PD moyenne 16 %) ne pèse que 26 % de l'exposition mais porte **35 % du capital** ; son poids de risque (91 %) est le seul à dépasser les 75 % du standard (16 points de plus), alors que la classe la plus sûre (C1, PD 1 %) est à 44 %, soit 31 points de moins. Le modèle interne est donc **plus favorable sur les bons emprunteurs et plus sévère sur les mauvais** : c'est ce que fait un cadre sensible au risque. Les défauts observés par classe (1,0 % ; 2,7 % ; 4,0 % ; 6,2 % ; 16,2 %) suivent la PD moyenne : le modèle de PD est bien calibré, ce que le capital suppose.

**Pour aller plus loin.** (1) Remplacez la LGD moyenne par une LGD par garantie (`recouvrements.csv`) : que devient le capital ? (2) Appliquez la formule « entreprises » (`k_entreprise`, échéance 2,5 ans) au même portefeuille : de combien le capital augmente-t-il ? Est-ce pertinent pour des prêts à des particuliers ? (3) Les PD dépassent 0,5 pour quelques prêts : plafonnez-les à 0,30 et mesurez l'effet.

### Application 4.2 — Simuler la perte au quantile 99,9 % : granularité et corrélation

*Sections du livre : 4.1.4, 4.1.6.* **Objectif :** retrouver la formule IRB par simulation, mesurer l'effet de la taille du portefeuille et de la corrélation d'actifs.

**Étape 1 — Une simulation.** On tire 200 000 « années » pour un portefeuille de 20 000 prêts de PD 6 % et de corrélation d'actifs 4,6 %.

```python
p0, rho0 = 0.06, float(rho_detail_autre(0.06))
pertes = perte_portefeuille_vasicek(p0, rho0, 20000, 200000, seed=3)
q_sim = np.quantile(pertes, 0.999)
q_for = float(k_vasicek(p0, 1.0, rho0)) + p0
print("rho = %.4f | perte moyenne simulée = %.4f | quantile simulé = %.4f | formule = %.4f" % (rho0, pertes.mean(), q_sim, q_for))
```
<!--sortie-->
```text
rho = 0.0459 | perte moyenne simulée = 0.0600 | quantile simulé = 0.1811 | formule = 0.1804
```

**Étape 2 — La granularité.** La formule suppose une infinité de petits prêts. Que devient le quantile avec 50, 200, 1 000 ou 20 000 prêts ?

```python
res = {}
for n in (50, 200, 1000, 20000):
    L = perte_portefeuille_vasicek(p0, rho0, n, 200000, seed=4)
    res[n] = round(float(np.quantile(L, 0.999)), 4)
print("quantile 99,9 % selon le nombre de prêts :", res, "| formule :", round(q_for, 4))
```
<!--sortie-->
```text
quantile 99,9 % selon le nombre de prêts : {50: 0.24, 200: 0.2, 1000: 0.183, 20000: 0.1795} | formule : 0.1804
```

**Étape 3 — La corrélation.** La corrélation est imposée par le texte ; que se passe-t-il si la vraie vaut le double ?

```python
for r in (0.02, rho0, 0.09, 0.18):
    L = perte_portefeuille_vasicek(p0, r, 20000, 200000, seed=5)
    print("rho = %.3f : quantile 99,9 %% simulé = %.4f | par la formule = %.4f" % (r, np.quantile(L, 0.999), float(k_vasicek(p0, 1.0, r)) + p0))
```
<!--sortie-->
```text
rho = 0.020 : quantile 99,9 % simulé = 0.1287 | par la formule = 0.1294
rho = 0.046 : quantile 99,9 % simulé = 0.1793 | par la formule = 0.1804
rho = 0.090 : quantile 99,9 % simulé = 0.2529 | par la formule = 0.2553
rho = 0.180 : quantile 99,9 % simulé = 0.3897 | par la formule = 0.3939
```

**Lecture.** Pour 20 000 prêts, le quantile simulé (0,1811) est à 0,4 % de la formule (0,1804) : l'écart est celui de la simulation. La **granularité** pèse bien davantage : avec 50 prêts le quantile à 99,9 % vaut 0,24, avec 200 prêts 0,20, avec 1 000 prêts 0,183 ; il ne rejoint la formule (0,1795 pour 20 000 prêts, 0,1804 par la formule) qu'avec beaucoup de prêts. Un portefeuille de quelques dizaines de gros prêts ne peut donc pas être traité par la formule IRB sans ajustement de concentration : c'est l'objet du pilier 2. Quant à la **corrélation**, elle est le paramètre le plus influent : le quantile passe de 0,129 pour $\rho=0{,}02$ à 0,390 pour $\rho=0{,}18$, soit un facteur 3. La simulation confirme la formule pour chacune des valeurs.

**Pour aller plus loin.** Tracez l'histogramme de `pertes` et placez-y la perte attendue et le quantile ; calculez le **quantile à 99 %** et à **99,99 %** : de combien le capital changerait-il si le régulateur changeait le niveau de confiance ?

### Application 4.3 — La procyclicité du capital

*Section du livre : 4.1.6.* **Objectif :** mesurer ce qui se passe quand la PD utilisée est celle de l'instant (*point in time*) plutôt que la moyenne du cycle (*through the cycle*).

**Étape 1 — Les données.** `taux_defaut_macro.csv` donne, pour 80 trimestres, le taux de défaut d'un portefeuille. On le prend comme PD de l'instant.

```python
macro = charger("taux_defaut_macro.csv")
macro["pd_pit"] = macro["taux_defaut"]
macro["pd_ttc"] = macro["pd_pit"].mean()
print("taux de défaut : moyenne %.2f %% | minimum %.2f %% | maximum %.2f %% (trimestre %d)" % (
    100 * macro["pd_pit"].mean(), 100 * macro["pd_pit"].min(), 100 * macro["pd_pit"].max(), macro.loc[macro["pd_pit"].idxmax(), "trimestre"]))
```
<!--sortie-->
```text
taux de défaut : moyenne 3.06 % | minimum 0.99 % | maximum 12.83 % (trimestre 52)
```

**Étape 2 — Le capital selon la PD.** Pour une LGD de 46 %, on calcule le capital par euro d'exposition avec la PD de l'instant, avec la PD moyenne, et avec une PD **lissée** (moyenne mobile sur 16 trimestres).

```python
macro["k_pit"] = k_detail(macro["pd_pit"], LGD)
macro["k_ttc"] = k_detail(macro["pd_ttc"], LGD)
macro["pd_lisse"] = macro["pd_pit"].rolling(16, min_periods=1).mean()
macro["k_lisse"] = k_detail(macro["pd_lisse"], LGD)
pic = macro["pd_pit"].idxmax()
print("capital au pic de la crise : instant %.2f %% | moyenne du cycle %.2f %% | lissé %.2f %%" % (
    100 * macro.loc[pic, "k_pit"], 100 * macro.loc[pic, "k_ttc"], 100 * macro.loc[pic, "k_lisse"]))
print("capital minimum / maximum (instant) : %.2f %% / %.2f %%" % (100 * macro["k_pit"].min(), 100 * macro["k_pit"].max()))
```
<!--sortie-->
```text
capital au pic de la crise : instant 6.78 % | moyenne du cycle 5.15 % | lissé 5.04 %
capital minimum / maximum (instant) : 3.73 % / 6.78 %
```

**Étape 3 — Le ratio de la banque.** Supposons que la banque détienne des fonds propres égaux à 1,3 fois le capital IRB **moyen** (calculé avec la PD moyenne) et ne les augmente pas. Quel ratio « fonds propres / capital exigé » obtient-elle trimestre après trimestre ?

```python
fonds = 1.3 * macro["k_ttc"].iloc[0]
for nom in ("k_pit", "k_lisse"):
    ratio = fonds / macro[nom]
    print("%-8s : ratio minimum %.2f (trimestre %d) | trimestres sous 1,00 : %d" % (nom, ratio.min(), macro.loc[ratio.idxmin(), "trimestre"], int((ratio < 1).sum())))
```
<!--sortie-->
```text
k_pit    : ratio minimum 0.99 (trimestre 52) | trimestres sous 1,00 : 1
k_lisse  : ratio minimum 1.23 (trimestre 65) | trimestres sous 1,00 : 0
```

**Lecture.** Au pic de la crise (trimestre 52, taux de défaut de 12,8 %), le capital calculé avec la PD de l'instant est de 6,78 % de l'exposition, contre 5,15 % avec la PD moyenne du cycle : **+32 %** en pleine crise ; du creux (3,73 %) au sommet (6,78 %), il augmente de **82 %**. Une banque qui détiendrait des fonds propres égaux à 1,3 fois le capital moyen verrait son ratio tomber à 0,99 : elle passe, pour un trimestre, **sous l'exigence**, alors que ses fonds propres n'ont pas bougé. Avec une PD lissée sur 16 trimestres, le ratio ne descend pas sous 1,23, mais l'exigence **réagit tardivement** (le minimum se produit au trimestre 65, après la crise) : le lissage supprime la procyclicité au prix d'un capital sous-estimé quand la crise éclate. Aucune des deux solutions n'est gratuite : d'où les coussins contracycliques, qui demandent plus de capital **avant** la crise.

**Pour aller plus loin.** Un **coussin contracyclique** consiste à exiger plus de capital quand le crédit croît vite. Définissez un coussin proportionnel à l'écart de la PD lissée à sa moyenne et regardez s'il aplatit le ratio.

### Application 4.4 — Agréger les modules du capital de solvabilité

*Sections du livre : 4.2.4, 4.2.5.* **Objectif :** calculer le capital de solvabilité requis d'un assureur par agrégation de modules, mesurer la diversification et tester la sensibilité à la matrice de corrélation.

**Étape 1 — Le calcul de référence.** Les modules sont ceux du livre (en M€) : marché 110, défaut des contreparties 20, vie 30, santé 45, non-vie 140.

```python
modules = ["marché", "défaut", "vie", "santé", "non-vie"]
charges = np.array([110, 20, 30, 45, 140.])
corr = np.array([[1, .25, .25, .25, .25], [.25, 1, .25, .25, .5], [.25, .25, 1, .25, 0],
                 [.25, .25, .25, 1, .5], [.25, .5, 0, .5, 1]])
bscr = agreger(charges, corr)
print("somme %.0f | SCR de base %.1f | diversification %.1f (%.1f %%)" % (charges.sum(), bscr, charges.sum() - bscr, 100 * (charges.sum() - bscr) / charges.sum()))
```
<!--sortie-->
```text
somme 345 | SCR de base 241.8 | diversification 103.2 (29.9 %)
```

**Étape 2 — Trois cas extrêmes et une variante.** Corrélation 1 partout (aucune diversification), 0 partout (diversification maximale), la matrice de référence, et la même matrice avec une corrélation de 0,5 entre marché et non-vie (une grande tempête qui fait aussi chuter les marchés).

```python
R1 = np.ones((5, 5))
R0 = np.eye(5)
Rv = corr.copy(); Rv[0, 4] = Rv[4, 0] = 0.5
for nom, R in (("corrélation 1", R1), ("référence", corr), ("marché–non-vie à 0,5", Rv), ("corrélation 0", R0)):
    print("%-22s SCR de base %.1f" % (nom, agreger(charges, R)))
```
<!--sortie-->
```text
corrélation 1          SCR de base 345.0
référence              SCR de base 241.8
marché–non-vie à 0,5   SCR de base 257.2
corrélation 0          SCR de base 187.1
```

**Étape 3 — La contribution de chaque module.** La dérivée du SCR de base par rapport à une charge s'appelle sa **contribution marginale** ; la somme des contributions (charge × dérivée) redonne le SCR de base (théorème d'Euler).

```python
contrib = charges * (corr @ charges) / bscr
print(pd.DataFrame({"module": modules, "charge": charges, "contribution": contrib.round(1), "part (%)": (100 * contrib / bscr).round(1)}).to_string(index=False))
print("somme des contributions :", round(contrib.sum(), 1), "= SCR de base", round(bscr, 1))
```
<!--sortie-->
```text
 module  charge  contribution  part (%)
 marché   110.0          76.8      31.7
 défaut    20.0          11.3       4.7
    vie    30.0           9.1       3.8
  santé    45.0          28.8      11.9
non-vie   140.0         115.8      47.9
somme des contributions : 241.8 = SCR de base 241.8
```

**Lecture.** La diversification est considérable mais **dépend de la matrice** : le SCR de base vaut 345 M€ si tout est parfaitement corrélé, 241,8 M€ avec la matrice de référence, 187,1 M€ si les modules étaient indépendants. Une **seule** corrélation changée (marché–non-vie de 0,25 à 0,5) le fait passer à 257,2 M€ (+15,4 M€, +6 %). Les contributions montrent que **les deux plus gros modules portent 80 % du SCR de base** (non-vie 47,9 %, marché 31,7 %) alors qu'ils représentent 72,5 % de la somme des charges : les petits modules profitent davantage de la diversification, les gros en profitent moins. La somme des contributions redonne exactement le SCR de base (propriété d'homogénéité de degré 1).

**Pour aller plus loin.** Le module non-vie lui-même agrège des sous-modules (primes et réserves, catastrophes) : décomposez les 140 M€ en 120 et 60 avec une corrélation de 0,25, et vérifiez que le total d'ensemble reste cohérent.

### Application 4.5 — Marge de risque et résistance aux chocs

*Sections du livre : 4.2.3, 4.2.6.* **Objectif :** calculer la marge de risque par la méthode du coût du capital, voir comment elle dépend du rythme d'écoulement, puis tester le ratio de solvabilité après des chocs de marché.

**Étape 1 — La marge de risque.** On reprend le SCR du livre (253,8 M€), un coût du capital de 6 % et une actualisation à 2 %. Trois profils d'écoulement des engagements : rapide, central, lent.

```python
scr = bscr + 12.0                                       # avec 12 M€ de risque opérationnel
def marge_risque(scr0, motif, taux=0.02, c=0.06):
    return c * sum(scr0 * m / (1 + taux) ** (t + 1) for t, m in enumerate(motif))
profils = {"rapide": [1, .5, .2, .05], "central": [1, .7, .45, .25, .1], "lent": [1, .85, .7, .55, .4, .28, .18, .1, .05]}
RM = {nom: marge_risque(scr, m) for nom, m in profils.items()}
print({nom: round(v, 1) for nom, v in RM.items()})
```
<!--sortie-->
```text
{'rapide': 25.8, 'central': 36.5, 'lent': 58.8}
```

**Étape 2 — Le ratio après un choc.** Avec 1 270 M€ d'actifs et 900 M€ de meilleure estimation, les fonds propres valent actifs − meilleure estimation − marge de risque. Un choc de marché fait baisser les actifs ; on suppose aussi (hypothèse simple) que le SCR monte de 10 % pour chaque tranche de 50 M€ de choc, car le portefeuille de placements devient plus concentré.

```python
FP0 = 1270 - 900 - RM["central"]
lignes = []
for choc in (0, 50, 100, 150, 200):
    fp = FP0 - choc
    scr_c = scr * (1 + 0.10 * choc / 50)
    lignes.append({"choc (M€)": choc, "fonds propres": round(fp, 1), "ratio, SCR fixe (%)": round(100 * fp / scr, 1),
                   "ratio, SCR en hausse (%)": round(100 * fp / scr_c, 1)})
print(pd.DataFrame(lignes).to_string(index=False))
```
<!--sortie-->
```text
 choc (M€)  fonds propres  ratio, SCR fixe (%)  ratio, SCR en hausse (%)
         0          333.5                131.4                     131.4
        50          283.5                111.7                     101.5
       100          233.5                 92.0                      76.7
       150          183.5                 72.3                      55.6
       200          133.5                 52.6                      37.6
```

**Lecture.** La marge de risque dépend du **rythme d'écoulement** : 25,8 M€ pour un portefeuille qui s'éteint en quatre ans, 36,5 M€ pour le profil central (cinq ans), 58,8 M€ pour un profil lent (neuf ans), soit **2,3 fois** celle du profil rapide : les branches à queue longue immobilisent plus longtemps du capital. Pour le ratio, avec un SCR constant, la mutuelle supporte un choc de 79,7 M€ avant de passer sous 100 % ; si le SCR monte aussi (ici +10 % par tranche de 50 M€), la limite tombe à **environ 53 M€**, et à 100 M€ de choc le ratio est de 76,7 % au lieu de 92 %. **Le ratio baisse par le haut et par le bas à la fois** : les fonds propres diminuent et le capital requis augmente.

**Pour aller plus loin.** Quel choc maximal la mutuelle supporte-t-elle sans passer sous 100 % ? Trouvez-le par une recherche (dichotomie) dans les deux hypothèses.

### Application 4.6 — La marge sur services contractuels, année par année

*Section du livre : 4.4.1.* **Objectif :** programmer le déroulement de la CSM d'un groupe de contrats sur trois ans, avec un écart d'expérience et une révision d'hypothèses.

**Étape 1 — La fonction.** Elle prend la prime, la valeur actuelle des sinistres attendus, l'ajustement pour risque, la durée de couverture, les sinistres réellement observés chaque année et les révisions de la valeur actuelle des **sinistres futurs** (positives = plus de sinistres). Taux d'actualisation nul, comme dans le livre.

```python
def ifrs17(prime, vp_sin, ra, annees, sin_obs=None, revisions=None):
    csm = prime - (vp_sin + ra)
    if csm < 0:                                          # contrat déficitaire : perte immédiate
        return pd.DataFrame([{"année": 0, "CSM ouverture": 0.0, "libération": 0.0, "produit": 0.0, "charge de sinistres": 0.0, "résultat des services": csm}])
    sin_att, ra_ann, lignes = vp_sin / annees, ra / annees, []
    for a in range(1, annees + 1):
        csm += -(revisions or {}).get(a, 0.0)            # une hausse des sinistres futurs diminue la CSM
        lib = csm / (annees - a + 1)
        obs = (sin_obs or {}).get(a, sin_att)
        lignes.append({"année": a, "CSM ouverture": round(csm, 2), "libération": round(lib, 2), "produit": round(sin_att + ra_ann + lib, 2),
                       "charge de sinistres": round(obs, 2), "résultat des services": round(sin_att + ra_ann + lib - obs, 2)})
        csm -= lib
    return pd.DataFrame(lignes)
print(ifrs17(100, 70, 8, 3).to_string(index=False))
```
<!--sortie-->
```text
 année  CSM ouverture  libération  produit  charge de sinistres  résultat des services
     1          22.00        7.33    33.33                23.33                   10.0
     2          14.67        7.33    33.33                23.33                   10.0
     3           7.33        7.33    33.33                23.33                   10.0
```

**Étape 2 — Une mauvaise surprise.** Les sinistres de l'année 1 sont de 28 (au lieu de 23,33) et, au début de l'année 2, on révise de +6 la valeur actuelle des sinistres futurs.

```python
print(ifrs17(100, 70, 8, 3, sin_obs={1: 28.0}, revisions={2: 6.0}).to_string(index=False))
```
<!--sortie-->
```text
 année  CSM ouverture  libération  produit  charge de sinistres  résultat des services
     1          22.00        7.33    33.33                28.00                   5.33
     2           8.67        4.33    30.33                23.33                   7.00
     3           4.33        4.33    30.33                23.33                   7.00
```

**Étape 3 — Contrat déficitaire.** Sinistres attendus de 95.

```python
print(ifrs17(100, 95, 8, 3).to_string(index=False))
```
<!--sortie-->
```text
 année  CSM ouverture  libération  produit  charge de sinistres  résultat des services
     0            0.0         0.0      0.0                  0.0                     -3
```

**Lecture.** Sans surprise, le résultat des services est de 10 par an et le produit de 33,33 (le tiers de la prime). Avec la mauvaise surprise de l'année 1, le résultat de cette année tombe à 5,33 (l'écart d'expérience de 4,67 passe **immédiatement** en résultat) ; la révision de +6 des sinistres futurs, elle, **réduit la CSM** et fait baisser la libération des années 2 et 3 de 7,33 à 4,33 : le résultat de ces deux années est de 7 (10 moins 3) au lieu de 10. Sur trois ans, le résultat cumulé est de $19{,}33=30-4{,}67-6$ : **l'écart passé et l'écart futur sont tous deux payés, mais à des dates différentes**. Le contrat déficitaire, enfin, déclenche une perte de 3 **dès la souscription** et n'a pas de CSM à libérer.

**Pour aller plus loin.** Ajoutez un taux d'actualisation de 3 % sur les flux d'exécution et la **désactualisation** de la CSM au taux fixé à la souscription : de combien la CSM libérée change-t-elle ?

### Application 4.7 — Comparer des modèles de Takaful : où les deux parties s'y retrouvent

*Sections du livre : 4.3.2, 4.5.2 à 4.5.5.* **Objectif :** explorer les paramètres du modèle hybride pour le fonds auto, et trouver ceux pour lesquels ni l'opérateur ni les participants ne sont systématiquement perdants.

**Étape 1 — Un fonds, un modèle.** `simuler_fonds` fait tourner les quinze années d'un fonds et rend une table annuelle : excédent, prêt sans intérêt, remboursement, distribution, réserve, résultat de l'opérateur.

```python
tk = charger("takaful_fonds.csv")
auto = tk[tk["fonds"] == "auto"]
r = simuler_fonds(auto, "hybride", wakala=0.12, part_mudaraba=0.30)
print((r.set_index("annee")[["excedent", "qard_nouveau", "distribue", "reserve_fin", "resultat_operateur"]].tail(5) / 1e6).round(2).to_string())
```
<!--sortie-->
```text
       excedent  qard_nouveau  distribue  reserve_fin  resultat_operateur
annee                                                                    
2020       4.68           0.0       3.28        14.91                1.40
2021       6.07           0.0       4.25        16.73                1.30
2022       7.28           0.0       5.10        18.91                1.43
2023      11.51           0.0       8.06        22.36                1.62
2024       4.96           0.0       3.48        23.85                1.76
```

**Étape 2 — Une grille de paramètres.** On fait varier le taux de wakala (de 10 % à 22 %) et la part de moudaraba (0, 30 %, 60 %) et on retient, pour chaque couple, le résultat cumulé de l'opérateur, les années en déficit et les sommes distribuées.

```python
lignes = []
for w in (0.10, 0.12, 0.14, 0.16, 0.18, 0.20, 0.22):
    for m in (0.0, 0.30, 0.60):
        r = simuler_fonds(auto, "hybride", wakala=w, part_mudaraba=m)
        lignes.append({"wakala (%)": round(100 * w), "moudaraba (%)": round(100 * m), "opérateur (M€)": r["resultat_operateur"].sum() / 1e6,
                       "années en déficit": int((r["excedent"] < 0).sum()), "distribué (M€)": r["distribue"].sum() / 1e6})
grille = pd.DataFrame(lignes)
print(grille.pivot(index="wakala (%)", columns="moudaraba (%)", values="opérateur (M€)").round(1).to_string())
```
<!--sortie-->
```text
moudaraba (%)    0     30    60
wakala (%)                     
10             -0.0   2.3   4.5
12             15.1  17.0  18.9
14             30.2  31.7  33.2
16             45.3  46.4  47.5
18             60.4  61.0  61.6
20             75.5  75.7  75.9
22             90.6  90.6  90.7
```

**Étape 3 — La région viable.** On cherche les couples où l'opérateur gagne au moins 5 M€ sur quinze ans, où le fonds a au plus 2 années en déficit et où les participants reçoivent au moins 40 M€.

```python
viable = grille[(grille["opérateur (M€)"] >= 5) & (grille["années en déficit"] <= 2) & (grille["distribué (M€)"] >= 40)]
print(viable.round(1).to_string(index=False) if len(viable) else "aucun couple viable")
print(grille[grille["moudaraba (%)"] == 30][["wakala (%)", "années en déficit", "distribué (M€)"]].round(1).to_string(index=False))
```
<!--sortie-->
```text
 wakala (%)  moudaraba (%)  opérateur (M€)  années en déficit  distribué (M€)
         12              0            15.1                  0            57.1
         12             30            17.0                  0            55.7
         12             60            18.9                  0            54.3
         14              0            30.2                  0            45.6
         14             30            31.7                  0            44.5
         14             60            33.2                  0            43.4
 wakala (%)  années en déficit  distribué (M€)
         10                  0            66.9
         12                  0            55.7
         14                  0            44.5
         16                  1            33.4
         18                  2            23.1
         20                  6            13.9
         22                  8             2.4
```

**Lecture.** Le résultat de l'opérateur est **presque linéaire** dans le taux de wakala : 15 M€ de plus tous les deux points (de 0 à 10 % de frais, l'opérateur ne fait que couvrir ses frais réels), alors que la part de moudaraba n'ajoute guère (moins de 4,5 M€ pour 60 points). Du côté des participants, la distribution baisse d'environ 11 M€ à chaque hausse de 2 points du wakala (de 67 M€ à 10 % à 2 M€ à 22 %, pour une moudaraba de 30 %), et les années déficitaires apparaissent à partir de 16 % (une année), 18 % (deux), 20 % (six), 22 % (huit). La **région viable** (opérateur ≥ 5 M€, au plus 2 années en déficit, participants ≥ 40 M€) est étroite : elle se réduit à des taux de wakala de **12 % à 14 %** (avec n'importe quelle part de moudaraba testée). Au-delà, la condition sur les participants est violée ; en deçà, l'opérateur ne couvre pas ses frais. **Le taux d'un contrat de Takaful est donc une négociation entre deux contraintes, et le ratio sinistres/cotisations du fonds en fixe la fenêtre.**

**Pour aller plus loin.** Ajoutez une commission de performance de 10 % de l'excédent positif pour l'opérateur et regardez si elle élargit la région viable. Ne tirez aucune conclusion d'**un seul** tirage de quinze années : simulez les sinistres (loi gamma de moyenne 78 % des cotisations et d'écart-type 4,5 points) et regardez la **distribution** du résultat de l'opérateur.

### Application 4.8 — Détecter des opérations suspectes, de bout en bout

*Sections du livre : 4.6.2 à 4.6.7.* **Objectif :** enchaîner variables par compte, règles, graphe, anomalies et apprentissage supervisé, puis choisir le nombre d'alertes à examiner par un calcul de coût.

**Étape 1 — Variables par compte et règles.**

```python
tx, comptes, verite = charger("transactions_lab.csv"), charger("comptes_lab.csv"), charger("verite_lab.csv")
F = variables_comptes(tx, comptes).merge(verite, on="id_compte")
y = F["suspect"].values
regle = (F["max_depots_sous_seuil_14j"] >= 5) | ((F["max_virements_entrants_3j"] >= 8) & (F["part_sortie_risque"] >= 0.5)) | (F["n_sorties_pays_risque"] >= 4)
print("comptes :", len(F), "| suspects :", int(y.sum()), "| alertes par règles :", int(regle.sum()), "| vrais cas trouvés :", int((regle & (y == 1)).sum()))
```
<!--sortie-->
```text
comptes : 3000 | suspects : 57 | alertes par règles : 42 | vrais cas trouvés : 42
```

**Étape 2 — Le graphe.** Virements d'au moins 2 000 €, cycles de longueur au plus 4.

```python
import networkx as nx
gros = tx[(tx["type"] == "virement") & (tx["sens"] == "debit") & (tx["contrepartie"] > 0) & (tx["montant"] >= 2000)]
G = nx.DiGraph(); G.add_edges_from(zip(gros["id_compte"], gros["contrepartie"]))
F["dans_cycle"] = F["id_compte"].isin(set(c for cyc in nx.simple_cycles(G, length_bound=4) for c in cyc)).astype(int)
print("comptes dans un cycle :", int(F["dans_cycle"].sum()), "| dont suspects :", int(F.loc[F["dans_cycle"] == 1, "suspect"].sum()))
```
<!--sortie-->
```text
comptes dans un cycle : 12 | dont suspects : 12
```

**Étape 3 — Anomalies et supervisé.** Forêt d'isolement (sans étiquettes) et boosting (étiquettes, validation croisée stratifiée), avec la variable de graphe.

```python
from sklearn.ensemble import IsolationForest
from sklearn.model_selection import StratifiedKFold, cross_val_predict
import lightgbm as lgb
cols = ["n_tx", "montant_total", "n_depots_sous_seuil", "max_depots_sous_seuil_14j", "max_virements_entrants_3j", "n_sorties_pays_risque", "montant_pays_risque", "part_sortie_risque"]
Xl = np.log1p(F[cols].values)
score_if = -IsolationForest(n_estimators=200, random_state=0, contamination=0.02).fit(Xl).score_samples(Xl)
gbm = lgb.LGBMClassifier(n_estimators=150, learning_rate=0.05, num_leaves=8, min_child_samples=5, verbose=-1, random_state=0, n_jobs=1)
score_gbm = cross_val_predict(gbm, np.column_stack([Xl, F["dans_cycle"]]), y, cv=StratifiedKFold(5, shuffle=True, random_state=0), method="predict_proba")[:, 1]
```

**Étape 4 — Choisir le nombre d'alertes.** Un examen coûte 200 € ; un cas manqué coûte 15 000 € (valeurs d'illustration). Le coût total de $k$ alertes examinées est $200k+15\,000\times(\text{cas non trouvés})$.

```python
def cout(score, k):
    trouves = y[np.argsort(-score)[:k]].sum()
    return 200 * k + 15000 * (y.sum() - trouves)
for nom, s in (("forêt d'isolement", score_if), ("boosting + cycle", score_gbm)):
    ks = np.arange(0, 601)
    c = np.array([cout(s, k) for k in ks])
    print("%-20s k optimal = %3d | coût minimal = %6.0f € | coût sans aucune alerte = %6.0f €" % (nom, ks[c.argmin()], c.min(), c[0]))
```
<!--sortie-->
```text
forêt d'isolement    k optimal = 292 | coût minimal =  58400 € | coût sans aucune alerte = 855000 €
boosting + cycle     k optimal =  61 | coût minimal =  12200 € | coût sans aucune alerte = 855000 €
```

**Lecture.** Les règles lèvent 42 alertes, toutes exactes (rappel de 74 %), et le graphe désigne 12 comptes dans des cycles, tous suspects : les deux méthodes se complètent. Pour le choix du nombre d'alertes, le **boosting enrichi du graphe** a un coût minimal de 12 200 € en examinant 61 comptes (à peine plus que les 57 cas réels), contre 855 000 € sans aucune alerte (57 cas manqués × 15 000 €). La **forêt d'isolement** a besoin de 292 alertes pour son optimum, et son coût minimal est de 58 400 €, près de cinq fois plus : ses alertes sont moins précises, il faut en examiner davantage pour trouver les mêmes cas. Le **seuil optimal** dépend directement du rapport entre le coût d'un cas manqué et celui d'un examen (ici 75 contre 1) : plus le cas manqué coûte cher, plus on accepte d'alertes inutiles.

**Pour aller plus loin.** Faites varier le coût d'un cas manqué (1 000 €, 15 000 €, 150 000 €) : comment le nombre optimal d'alertes évolue-t-il ? Que vous apprend la comparaison avec la capacité réelle de l'équipe ?

## Exercices

### Exercice 4.1 ⭐ — La formule IRB à la main (section 4.1.4)

Une exposition de détail a une PD de 1 %, une LGD de 45 % et une corrélation d'actifs de 12 %. Calculez le capital par euro d'exposition $K$ et le poids de risque. On donne $\Phi^{-1}(0{,}01)=-2{,}3263$, $\Phi^{-1}(0{,}999)=3{,}0902$ et $\Phi(-1{,}34)\approx 0{,}0901$.

### Exercice 4.2 ⭐ — Ratios et coussins (section 4.1.2)

Une banque a 200 M€ d'actifs pondérés, 12 M€ de fonds propres de base (CET1), 2 M€ d'instruments hybrides de catégorie 1 et 4 M€ de catégorie 2. Avec les minimums de 4,5 %, 6 % et 8 % et un coussin de conservation de 2,5 %, quelles sont les exigences et le déficit éventuel ? Combien de CET1 faut-il lever pour tout satisfaire ?

### Exercice 4.3 ⭐⭐ — La perte attendue du modèle de Vasicek (section 4.1.4)

Vérifiez numériquement que l'espérance de la PD conditionnelle $p(Z)$ vaut la PD, pour deux couples (PD, $\rho$) de votre choix. Pourquoi cette propriété justifie-t-elle de retrancher la perte attendue pour obtenir le capital ?

### Exercice 4.4 ⭐⭐ — À partir de quelle PD l'IRB devient-il plus sévère que le standard ? (section 4.1.5)

Avec une LGD de 46 %, pour quelle PD le poids de risque de la formule « autres expositions de détail » dépasse-t-il 75 % ? Comparez avec le poids de la formule des entreprises (échéance 2,5 ans) à cette PD.

### Exercice 4.5 ⭐⭐ — Sensibilités du capital (sections 4.1.5, 4.1.6)

Pour un portefeuille homogène (PD 6 %, LGD 46 %), calculez le capital par euro d'exposition : (a) avec la corrélation de la formule ; (b) avec une corrélation doublée ; (c) avec une LGD de ralentissement de 56 % ; (d) avec les deux changements. Quel paramètre pèse le plus ?

### Exercice 4.6 ⭐⭐ — Un SCR à trois modules, à la main (section 4.2.4)

Modules : marché 100, non-vie 60, vie 40 (M€). Corrélations : marché–non-vie 0,25, marché–vie 0,25, non-vie–vie 0. Calculez le SCR de base et la diversification.

### Exercice 4.7 ⭐⭐ — Une marge de risque, à la main (section 4.2.3)

Le capital requis futur d'un portefeuille en extinction est de 60, 30 et 10 M€ aux trois prochaines dates ; le taux d'actualisation est de 3 % et le coût du capital de 6 %. Calculez la marge de risque. Que devient-elle si l'écoulement est deux fois plus lent (60, 60, 30, 30, 10, 10) ?

### Exercice 4.8 ⭐⭐⭐ — Queues et agrégation (section 4.2.5)

Reprenez les cinq modules de l'application 4.4. Simulez le quantile à 99,5 % de la perte totale avec une copule de Student à 3, 4, 8 et 30 degrés de liberté, marginales normales calibrées sur les mêmes charges isolées. Que constatez-vous quand le nombre de degrés de liberté augmente ?

### Exercice 4.9 ⭐ — Une CSM à la main (section 4.4.1)

Un groupe de contrats de quatre ans encaisse 200 de primes ; les sinistres attendus valent 130 en valeur actuelle, l'ajustement pour risque 20. Taux d'actualisation nul, couverture constante. Calculez la CSM initiale, sa libération annuelle et le produit annuel. Puis : à la fin de l'année 2, la valeur actuelle des sinistres futurs est révisée de +10 ; que devient la libération des années 3 et 4 ?

### Exercice 4.10 ⭐⭐ — Le taux de wakala qui convient aux deux parties (section 4.5.2)

Pour chacun des trois fonds, calculez l'intervalle de taux de wakala compris entre les frais réels de l'opérateur (10 % des cotisations) et le taux qui annule l'excédent moyen des participants. Que dire du fonds dont l'intervalle est le plus étroit ?

### Exercice 4.11 ⭐⭐ — Régler une règle de fractionnement (section 4.6.3)

Pour la règle « au moins $n$ dépôts d'espèces entre 9 000 et 10 000 € dans une fenêtre de $w$ jours », faites varier $n$ (3 à 8) et $w$ (7, 14, 30). Quel couple choisiriez-vous si l'équipe ne peut pas examiner plus de 30 comptes ?

### Exercice 4.12 ⭐⭐⭐ — Le graphe complet ne désigne personne (section 4.6.4)

Construisez le graphe de **tous** les virements entre comptes et mesurez la taille de sa plus grande composante fortement connexe. Puis ne gardez que les virements d'au moins 500, 1 000, 2 000 et 3 000 € et indiquez pour chaque seuil le nombre de cycles de longueur au plus 4 et la part des comptes trouvés qui sont de vrais allers-retours.

## Corrigés

### Corrigé 4.1

On calcule d'abord $\sqrt{\rho}=\sqrt{0{,}12}=0{,}3464$ et $\sqrt{1-\rho}=\sqrt{0{,}88}=0{,}9381$. Le numérateur de l'argument de $\Phi$ est $-2{,}3263+0{,}3464\times3{,}0902=-1{,}2558$ ; divisé par $0{,}9381$, il vaut $-1{,}3386$, et $\Phi(-1{,}3386)\approx0{,}0904$. Donc $K=0{,}45\times(0{,}0904-0{,}01)=0{,}45\times0{,}0804\approx0{,}0362$ : environ **3,6 % de l'exposition** (le calcul exact donne 3,61 %, l'écart venant des arrondis de $\Phi$), soit un poids de risque d'environ **45 %** ($12{,}5\times0{,}0361\approx45{,}2$ %). Vérification :

```python
print(round(float(k_vasicek(0.01, 0.45, 0.12)), 4), "| poids de risque :", round(12.5 * float(k_vasicek(0.01, 0.45, 0.12)), 3))
```
<!--sortie-->
```text
0.0361 | poids de risque : 0.452
```

### Corrigé 4.2

Exigences en M€ pour 200 M€ de RWA : CET1 $= (4{,}5+2{,}5)\,\%=7\,\%\to14$ ; catégorie 1 $=(6+2{,}5)\,\%=8{,}5\,\%\to17$ ; total $=(8+2{,}5)\,\%=10{,}5\,\%\to21$. Disponible : CET1 12, catégorie 1 $12+2=14$, total $14+4=18$. Déficits : $14-12=2$, $17-14=3$, $21-18=3$. Lever **3 M€ de CET1** résout tout : CET1 15 (≥ 14), catégorie 1 17 (≥ 17), total 21 (≥ 21). Un déficit en CET1 de 2 M€ ne suffirait pas, car la catégorie 1 et le total restent à 1 M€ du but : une levée de CET1 compte **dans les trois ratios à la fois**.

### Corrigé 4.3

```python
rng = np.random.default_rng(0)
Z = rng.standard_normal(2_000_000)
for p_, r_ in ((0.02, 0.10), (0.15, 0.04)):
    pc = norm.cdf((norm.ppf(p_) - np.sqrt(r_) * Z) / np.sqrt(1 - r_))
    print("PD = %.2f, rho = %.2f : moyenne de p(Z) = %.4f" % (p_, r_, pc.mean()))
```
<!--sortie-->
```text
PD = 0.02, rho = 0.10 : moyenne de p(Z) = 0.0200
PD = 0.15, rho = 0.04 : moyenne de p(Z) = 0.1500
```

L'espérance de $p(Z)$ vaut la PD : c'est l'**identité** $E[\Phi((c-\sqrt\rho Z)/\sqrt{1-\rho})]=\Phi(c)$, qui exprime que la probabilité inconditionnelle de défaut est la PD. Comme le taux de perte moyen vaut donc LGD × PD, c'est la **perte attendue** ; le quantile de $p(Z)$ moins cette moyenne est l'excédent de perte, la **perte inattendue**.

### Corrigé 4.4

```python
from scipy.optimize import brentq
pd_crit = brentq(lambda p_: 12.5 * float(k_detail(p_, 0.46)) - 0.75, 0.001, 0.5)
print("PD critique (détail) : %.4f | poids des entreprises à cette PD : %.3f" % (pd_crit, 12.5 * float(k_entreprise(pd_crit, 0.46))))
```
<!--sortie-->
```text
PD critique (détail) : 0.0908 | poids des entreprises à cette PD : 1.904
```

La formule de détail devient plus sévère que les 75 % du standard pour une PD d'environ **9 %** ; en dessous, elle est plus favorable. Pour la même PD, la formule des entreprises donne un poids bien plus élevé (corrélation plus forte, ajustement d'échéance) : **la catégorie de l'exposition compte autant que sa PD**, d'où l'importance de classer correctement les expositions.

### Corrigé 4.5

```python
rho_h = float(rho_detail_autre(0.06))
for nom, r_, l_ in (("référence", rho_h, 0.46), ("corrélation doublée", 2 * rho_h, 0.46), ("LGD de ralentissement 56 %", rho_h, 0.56), ("les deux", 2 * rho_h, 0.56)):
    print("%-28s K = %.4f" % (nom, float(k_vasicek(0.06, l_, r_))))
```
<!--sortie-->
```text
référence                    K = 0.0554
corrélation doublée          K = 0.0912
LGD de ralentissement 56 %   K = 0.0674
les deux                     K = 0.1110
```

Une LGD relevée de 10 points (+22 %) augmente le capital **dans la même proportion** (+22 %) ; doubler la corrélation l'augmente d'environ **65 %** (de 5,54 % à 9,12 %). Le capital est donc plus sensible à la corrélation qu'à la LGD dans cette plage, ce qui explique que le régulateur **impose** la corrélation : laissée au choix des banques, elle serait la variable d'ajustement la plus tentante. Les deux effets se multiplient (le dernier cas).

### Corrigé 4.6

$\text{BSCR}^2=100^2+60^2+40^2+2(0{,}25)(100)(60)+2(0{,}25)(100)(40)+2(0)(60)(40)=10\,000+3\,600+1\,600+3\,000+2\,000=20\,200$ ; $\text{BSCR}=\sqrt{20\,200}\approx142{,}1$ M€. La somme des charges est de 200 : la **diversification** retire $200-142{,}1\approx57{,}9$ M€ (29 %).

```python
print(round(agreger([100, 60, 40], [[1, .25, .25], [.25, 1, 0], [.25, 0, 1]]), 1))
```
<!--sortie-->
```text
142.1
```

### Corrigé 4.7

$\text{RM}=0{,}06\,(60/1{,}03+30/1{,}03^2+10/1{,}03^3)=0{,}06\,(58{,}25+28{,}28+9{,}15)=0{,}06\times95{,}68\approx5{,}74$ M€. Avec un écoulement deux fois plus lent, la somme actualisée vaut $60/1{,}03+60/1{,}03^2+30/1{,}03^3+30/1{,}03^4+10/1{,}03^5+10/1{,}03^6$ et la marge est de **11,16 M€**, presque le double (×1,9).

```python
def rm_(srs, taux=0.03, c=0.06):
    return c * sum(s / (1 + taux) ** (t + 1) for t, s in enumerate(srs))
print(round(rm_([60, 30, 10]), 2), round(rm_([60, 60, 30, 30, 10, 10]), 2))
```
<!--sortie-->
```text
5.74 11.16
```

### Corrigé 4.8

```python
from scipy.stats import t as loi_t
corr5 = np.array([[1, .25, .25, .25, .25], [.25, 1, .25, .25, .5], [.25, .25, 1, .25, 0], [.25, .25, .25, 1, .5], [.25, .5, 0, .5, 1]])
c5 = np.array([110, 20, 30, 45, 140.])
rng = np.random.default_rng(0)
Z = rng.standard_normal((300000, 5)) @ np.linalg.cholesky(corr5).T
for ddl in (3, 4, 8, 30):
    W = rng.chisquare(ddl, 300000) / ddl
    T = Z / np.sqrt(W)[:, None]
    tot = (norm.ppf(loi_t.cdf(T, ddl)) * c5 / norm.ppf(0.995)).sum(axis=1)
    print("copule de Student, %2d ddl : quantile 99,5 %% = %.1f" % (ddl, np.quantile(tot, 0.995)))
print("formule standard :", round(agreger(c5, corr5), 1))
```
<!--sortie-->
```text
copule de Student,  3 ddl : quantile 99,5 % = 266.5
copule de Student,  4 ddl : quantile 99,5 % = 258.5
copule de Student,  8 ddl : quantile 99,5 % = 252.0
copule de Student, 30 ddl : quantile 99,5 % = 243.9
formule standard : 241.8
```

Plus le nombre de degrés de liberté est **faible**, plus la dépendance de queue est forte et plus la perte au quantile 99,5 % dépasse la formule standard. À 30 degrés de liberté la copule de Student est presque gaussienne et le quantile redevient proche de la formule : **c'est la dépendance dans les queues, non la corrélation linéaire, qui fait l'écart** (section 4.2.5).

### Corrigé 4.9

CSM initiale : $200-(130+20)=50$. Libération annuelle : $50/4=12{,}5$. Produit annuel : sinistres attendus $130/4=32{,}5$, plus ajustement $20/4=5$, plus CSM $12{,}5$ : **50** par an, le quart de la prime. Après l'année 2, la CSM restante est $50-2\times12{,}5=25$ ; la révision de +10 des sinistres futurs la ramène à 15, libérée par moitié sur les années 3 et 4 : **7,5 par an** au lieu de 12,5. Vérification :

```python
print(ifrs17(200, 130, 20, 4, revisions={3: 10.0}).to_string(index=False))
```
<!--sortie-->
```text
 année  CSM ouverture  libération  produit  charge de sinistres  résultat des services
     1           50.0        12.5     50.0                 32.5                   17.5
     2           37.5        12.5     50.0                 32.5                   17.5
     3           15.0         7.5     45.0                 32.5                   12.5
     4            7.5         7.5     45.0                 32.5                   12.5
```

### Corrigé 4.10

```python
for fonds in ("famille", "auto", "sante"):
    d = tk[tk["fonds"] == fonds]
    lr = (d["sinistres"] / d["cotisations"]).mean()
    fr = (d["frais_gestion"] / d["cotisations"]).mean()
    print("%-8s frais réels %.1f %% | taux qui annule l'excédent moyen %.1f %% | largeur de l'intervalle %.1f points" % (fonds, 100 * fr, 100 * (1 - lr), 100 * (1 - lr - fr)))
```
<!--sortie-->
```text
famille  frais réels 10.0 % | taux qui annule l'excédent moyen 26.4 % | largeur de l'intervalle 16.4 points
auto     frais réels 10.0 % | taux qui annule l'excédent moyen 21.9 % | largeur de l'intervalle 11.9 points
sante    frais réels 10.0 % | taux qui annule l'excédent moyen 24.3 % | largeur de l'intervalle 14.3 points
```

L'intervalle est le plus étroit pour le **fonds auto** (de 10 % à 21,9 %, soit 11,9 points) : son ratio sinistres/cotisations est le plus élevé. Un taux de wakala dans cet intervalle fait gagner l'opérateur mais laisse peu de marge pour les écarts annuels de sinistralité (écart-type de 4,5 points) : **plus l'intervalle est étroit, plus la fixation du taux est sensible**, et plus le fonds dépendra d'un prêt sans intérêt de l'opérateur.

### Corrigé 4.11

```python
tx, comptes, verite = charger("transactions_lab.csv"), charger("comptes_lab.csv"), charger("verite_lab.csv")
dep = tx[(tx["type"] == "especes") & (tx["sens"] == "credit") & (tx["montant"] >= 9000) & (tx["montant"] < 10000)].copy()
dep["jour"] = (pd.to_datetime(dep["date"]) - pd.to_datetime("2024-01-01")).dt.days
susp = set(verite.loc[verite["suspect"] == 1, "id_compte"])
lignes = []
for w in (7, 14, 30):
    mx = dep.groupby("id_compte")["jour"].apply(lambda s: max_fenetre(np.sort(s.values), w))
    for n in range(3, 9):
        al = set(mx[mx >= n].index)
        lignes.append({"fenêtre (j)": w, "n": n, "alertes": len(al), "vrais cas": len(al & susp), "précision": round(len(al & susp) / max(len(al), 1), 2)})
res = pd.DataFrame(lignes)
print(res[res["n"].isin([3, 5, 8])].to_string(index=False))
```
<!--sortie-->
```text
 fenêtre (j)  n  alertes  vrais cas  précision
           7  3       23         15       0.65
           7  5       15         15       1.00
           7  8        9          9       1.00
          14  3       40         15       0.38
          14  5       15         15       1.00
          14  8       15         15       1.00
          30  3       46         15       0.33
          30  5       19         15       0.79
          30  8       15         15       1.00
```

Pour une capacité de 30 comptes, la règle **(14 jours, au moins 5 dépôts)** lève 15 alertes, toutes de vrais cas (les 15 fractionneurs) : précision et rappel de 100 % **sur ce schéma**. Un seuil plus bas (3 dépôts) lève 40 alertes à précision de 38 % (au-delà de la capacité), une fenêtre plus large (30 jours) fait entrer les commerces légitimes (19 alertes, précision de 79 % pour $n=5$), une fenêtre de 7 jours convient pour $n=5$ (15 cas sur 15) mais perd 6 cas sur 15 pour $n=8$. Le meilleur couple est donc celui qui est **le plus sélectif sans perdre de cas**.

### Corrigé 4.12

```python
import networkx as nx
vir = tx[(tx["type"] == "virement") & (tx["sens"] == "debit") & (tx["contrepartie"] > 0)]
Gtot = nx.DiGraph(); Gtot.add_edges_from(zip(vir["id_compte"], vir["contrepartie"]))
cc = max(nx.strongly_connected_components(Gtot), key=len)
print("graphe complet : %d virements distincts, plus grande composante fortement connexe : %d comptes" % (Gtot.number_of_edges(), len(cc)))
anneaux = set(verite.loc[verite["schema"] == "aller_retour", "id_compte"])
for seuil in (500, 1000, 2000, 3000):
    e = vir[vir["montant"] >= seuil]
    Gs = nx.DiGraph(); Gs.add_edges_from(zip(e["id_compte"], e["contrepartie"]))
    cyc = list(nx.simple_cycles(Gs, length_bound=4))
    cs = set(c for cy in cyc for c in cy)
    print("seuil %4d € : %4d virements | %2d cycles | %3d comptes | part de vrais anneaux %.2f" % (seuil, Gs.number_of_edges(), len(cyc), len(cs), len(cs & anneaux) / max(len(cs), 1)))
```
<!--sortie-->
```text
graphe complet : 17652 virements distincts, plus grande composante fortement connexe : 2969 comptes
seuil  500 € : 2669 virements |  4 cycles |  13 comptes | part de vrais anneaux 0.92
seuil 1000 € :  904 virements |  3 cycles |  12 comptes | part de vrais anneaux 1.00
seuil 2000 € :  226 virements |  3 cycles |  12 comptes | part de vrais anneaux 1.00
seuil 3000 € :   80 virements |  3 cycles |  12 comptes | part de vrais anneaux 1.00
```

Le graphe complet compte 17 652 virements distincts et une composante fortement connexe de **2 969 comptes sur 3 000** : presque chaque compte est atteignable depuis tous les autres, et chercher des cycles dans ce graphe n'identifie personne. Avec un seuil de 500 €, on trouve 4 cycles et 13 comptes dont 92 % sont de vrais allers-retours (un cycle fortuit s'ajoute) ; dès 1 000 €, les 12 comptes trouvés sont tous des allers-retours. **Restreindre le graphe** (au montant, à la période, à la longueur des cycles) est la condition pour que la détection de motifs veuille dire quelque chose.
