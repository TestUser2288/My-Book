# Chapitre 7 : Gestion actif-passif et théorie du portefeuille — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre 7 du livre (actif-passif, théorie du portefeuille, surplus). Il est, comme le chapitre, **facultatif**. Les **applications** reprennent en code, par petites étapes, les calculs du livre ; les **exercices** (⭐ direct, ⭐⭐ demande de réfléchir, ⭐⭐⭐ démonstration ou petite étude) se terminent par des **corrigés** : cherchez d'abord, regardez ensuite.

> ⚠️ **Données simulées, modèle jouet.** Les courbes de taux et les rendements de marché sont simulés et **indépendants** ; le passif est un échéancier fixe sans rachats ni options. Rien ici n'est un conseil en placement.

## Préparation

Tout le cahier repose sur un module écrit à la main, `build/outils_ch07.py` (table de mortalité, flux d'un passif vie, valeur actuelle, duration, frontière efficiente, scénarios de surplus). Les applications **n'en dépendent que pour charger les données** et pour les parties longues ; les calculs de base sont réécrits dans le cahier.

```python
import sys
import numpy as np, pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from scipy.optimize import minimize

sys.path.insert(0, "build")
import outils_ch07 as O

pd.set_option("display.width", 200)
b = O.Bilan(surplus=0.10)          # bilan jouet : passif d'un portefeuille vie, actif = 110 % du passif
c, rend, regimes, pv, mo = O.charger()
print(f"passif : {b.L0/1e6:.1f} M€ ; actif : {b.A0/1e6:.1f} M€ ; {b.nb_contrats} contrats")
```
<!--sortie-->
```text
passif : 460.2 M€ ; actif : 506.2 M€ ; 16908 contrats
```

```python hide
def NUM(k, v):
    print("NUM", k, v)
```

## Applications

### Application 7.1 — Prix, duration et convexité d'une obligation

*Sections du livre : 7.1.2.* **Objectif** : écrire soi-même le prix, la duration et la convexité, les vérifier par différences finies et mesurer l'erreur des approximations.

**Étape 1 — Le prix et la duration, à la main.** Une obligation à 10 ans, coupon de 5 %, nominal 100, taux 3 % (composition annuelle).

```python
def prix(flux, y):
    t = np.arange(1, len(flux) + 1)
    return float((flux / (1 + y) ** t).sum())

def duration_mac(flux, y):
    t = np.arange(1, len(flux) + 1)
    va = flux / (1 + y) ** t
    return float((t * va).sum() / va.sum())

flux = np.r_[np.full(9, 5.0), 105.0]
P0 = prix(flux, 0.03)
print(round(P0, 3), round(duration_mac(flux, 0.03), 3), round(duration_mac(flux, 0.03) / 1.03, 3))
```
<!--sortie-->
```text
117.06 8.272 8.031
```

**Étape 2 — Vérification par différences finies.** La duration modifiée est −(1/P) dP/dy, la convexité (1/P) d²P/dy².

```python
h = 1e-4
Pm, Pp = prix(flux, 0.03 - h), prix(flux, 0.03 + h)
dmod_num = -(Pp - Pm) / (2 * h) / P0
conv_num = (Pp - 2 * P0 + Pm) / h**2 / P0
print(round(dmod_num, 4), round(conv_num, 3))
```
<!--sortie-->
```text
8.0308 80.023
```

**Étape 3 — Erreur des approximations.** On compare le prix exact après un choc Δy aux approximations « duration seule » et « duration + convexité ».

```python
dm, cv = duration_mac(flux, 0.03) / 1.03, conv_num
lignes = []
for dy in (-0.03, -0.01, -0.005, 0.005, 0.01, 0.03):
    exact = prix(flux, 0.03 + dy) / P0 - 1
    lignes.append([100 * dy, 100 * exact, 100 * (-dm * dy), 100 * (-dm * dy + 0.5 * cv * dy**2)])
print(pd.DataFrame(lignes, columns=["choc (pt)", "exact (%)", "duration (%)", "avec convexité (%)"]).round(3).to_string(index=False))
```
<!--sortie-->
```text
 choc (pt)  exact (%)  duration (%)  avec convexité (%)
      -3.0     28.139        24.092              27.693
      -1.0      8.446         8.031               8.431
      -0.5      4.117         4.015               4.115
       0.5     -3.917        -4.015              -3.915
       1.0     -7.645        -8.031              -7.631
       3.0    -20.861       -24.092             -20.491
```

**Lecture.** Pour ±0,5 point, la duration seule est presque exacte ; à 3 points, elle se trompe de plusieurs points de pourcentage, et la convexité corrige l'essentiel. L'erreur de la duration seule est **toujours dans le même sens** (elle sous-estime le prix) : c'est le signe de la convexité positive.

```python hide
NUM("a1_P0", P0); NUM("a1_dmod", dm); NUM("a1_conv", cv)
e3 = prix(flux, 0.06) / P0 - 1
NUM("a1_err3", 100 * (e3 - (-dm * 0.03)))
NUM("a1_err3c", 100 * (e3 - (-dm * 0.03 + 0.5 * cv * 0.03**2)))
```
<!--sortie-->
```text
NUM a1_P0 117.06040567355164
NUM a1_dmod 8.030779348385579
NUM a1_conv 80.02320988797824
NUM a1_err3 3.230892550880704
NUM a1_err3c -0.37015189407831606
```

Ici P = 117,06, D_mod = 8,03 et C = 80,0 ; à +3 points, l'écart entre le prix exact et l'approximation de la duration seule est de 3,23 point de pourcentage, ramené à -0,37 avec la convexité.

**Pour aller plus loin.** Refaites le calcul pour un zéro-coupon à 10 ans (D_mod = 10/1,03) : sa convexité est plus grande que celle de l'obligation à coupons de même échéance, pourquoi ?

### Application 7.2 — Construire le passif d'un portefeuille d'assurance vie

*Sections du livre : 7.1.3.* **Objectif** : de la table de mortalité à la duration du passif, et mesurer la sensibilité du résultat aux hypothèses.

**Étape 1 — La table de mortalité.** Décès cumulés sur 2015–2019 divisés par les expositions, par sexe et par âge, puis q = 1 − exp(−m).

```python
d = mo[mo["annee"].between(2015, 2019)].groupby(["sexe", "age"])[["deces", "exposition"]].sum()
q = {s: 1 - np.exp(-(d.loc[s, "deces"] / d.loc[s, "exposition"]).clip(upper=0.9)) for s in ("F", "M")}
tab = pd.DataFrame(q)
print(tab.loc[[0, 30, 50, 70, 90]].round(5))
```
<!--sortie-->
```text
           F        M
age                  
0    0.00337  0.00439
30   0.00080  0.00105
50   0.00497  0.00610
70   0.03620  0.04804
90   0.25820  0.32794
```

**Étape 2 — Le rapport décès observés / décès attendus du portefeuille.** On applique la table à chaque contrat (âge atteint en 2017) et on compare au nombre de décès observés.

```python
age_mid = np.clip(pv["age_emission"] + (2017 - pv["annee_emission"]).clip(lower=0), 0, 99)
att = np.array([tab.loc[a, s] for a, s in zip(age_mid, pv["sexe"])]) * pv["exposition_2015_2019"]
ae = pv["deces"].sum() / att.sum()
print(pv["deces"].sum(), "décès observés ;", round(att.sum(), 1), "attendus ; A/E =", round(ae, 3))
```
<!--sortie-->
```text
832 décès observés ; 1061.9 attendus ; A/E = 0.783
```

**Étape 3 — Les flux, la valeur actuelle et la duration.** `O.flux_passif` construit l'échéancier des contrats en vigueur au 1er janvier 2020 (sans décès en 2015–2019, non échus).

```python
flux, n = O.flux_passif(pv, tab, ae)
y = O.taux_annuels(b.c0)
print(n, "contrats ; flux total", round(flux.sum() / 1e6, 1), "M€ ; VA", round(O.vp(flux, y) / 1e6, 1), "M€")
print("duration de Macaulay", round(O.duration_macaulay(flux, y), 2), "; modifiée", round(O.duration_modifiee(flux, y), 2))
```
<!--sortie-->
```text
16908 contrats ; flux total 716.4 M€ ; VA 460.2 M€
duration de Macaulay 16.57 ; modifiée 16.18
```

**Étape 4 — Sensibilité aux hypothèses.** On fait varier le rapport A/E (mortalité plus faible ou plus forte) et on ajoute des **rachats** (chaque année, 3 % des contrats encore en vigueur disparaissent).

```python
def passif(ratio, rachat=0.0):
    f, _ = O.flux_passif(pv, tab, ratio)
    f = f * (1 - rachat) ** np.arange(len(f))           # survie du contrat au rachat
    return f, O.vp(f, y), O.duration_modifiee(f, y)
lignes = {f"A/E = {r:.2f}, rachat {100*k:.0f} %": (passif(r, k)[1] / 1e6, passif(r, k)[2]) for r, k in ((ae, 0), (0.6, 0), (1.0, 0), (ae, 0.03))}
print(pd.DataFrame(lignes, index=["VA (M€)", "duration modifiée"]).T.round(2).to_string())
```
<!--sortie-->
```text
                        VA (M€)  duration modifiée
A/E = 0.78, rachat 0 %   460.23              16.18
A/E = 0.60, rachat 0 %   412.18              17.51
A/E = 1.00, rachat 0 %   507.14              14.96
A/E = 0.78, rachat 3 %   303.70              12.58
```

**Lecture.** Une mortalité plus forte avance les décès : la valeur actuelle monte et la duration baisse. Les rachats retirent les flux lointains : la duration baisse beaucoup. Une duration calculée sur un passif sans rachats **surestime** donc la sensibilité aux taux.

```python hide
f6, V6, D6 = passif(0.6); f1, V1, D1 = passif(1.0); fr, Vr, Dr = passif(ae, 0.03)
NUM("a2_ae", ae); NUM("a2_D", O.duration_modifiee(flux, y)); NUM("a2_D06", D6); NUM("a2_D10", D1); NUM("a2_Dr", Dr)
```
<!--sortie-->
```text
NUM a2_ae 0.7834922632458028
NUM a2_D 16.17581223089837
NUM a2_D06 17.510657380734905
NUM a2_D10 14.962602419408364
NUM a2_Dr 12.582741341934609
```

Ici, A/E = 0,783 et D_mod = 16,2 ; avec A/E = 0,6 elle vaut 17,5, avec A/E = 1 15,0, et avec des rachats de 3 % par an 12,6.

### Application 7.3 — Apparier l'actif au passif

*Sections du livre : 7.1.4.* **Objectif** : calculer l'écart de duration en euros, bâtir un portefeuille de zéro-coupons apparié, tester les conditions de Redington par revalorisation complète.

**Étape 1 — Fonctions de revalorisation.** On revalorise le passif et un portefeuille de zéro-coupons (poids par maturité, valeur initiale A₀) après un déplacement parallèle.

```python
y0 = b.y0
def val_actif(w, ys):
    return sum(b.A0 * wk * (1 + ys[m - 1]) ** (-m) / (1 + y0[m - 1]) ** (-m) for m, wk in w.items())
def dS(w, dy):
    ys = y0 + dy
    return (val_actif(w, ys) - b.A0 - (O.vp(b.flux, ys) - b.L0)) / 1e6
D_L = O.duration_modifiee(b.flux, y0)
D_cible = D_L * b.L0 / b.A0
print("D_L =", round(D_L, 2), "; durée cible de l'actif =", round(D_cible, 2))
```
<!--sortie-->
```text
D_L = 16.18 ; durée cible de l'actif = 14.71
```

**Étape 2 — Deux zéros-coupons à 10 et 20 ans.** On cherche les poids (w, 1 − w) qui donnent la duration cible.

```python
d10, d20 = 10 / (1 + y0[9]), 20 / (1 + y0[19])
w20 = (D_cible - d10) / (d20 - d10)
w_app = {10: 1 - w20, 20: w20}
print({k: round(float(v), 3) for k, v in w_app.items()})
print(pd.Series({f"{100*dy:+.0f} pt": round(dS(w_app, dy), 1) for dy in (-0.03, -0.01, 0.01, 0.03)}).to_string())
```
<!--sortie-->
```text
{10: 0.493, 20: 0.507}
-3 pt   -48.3
-1 pt    -3.6
+1 pt    -2.5
+3 pt   -15.6
```

**Étape 3 — Quelle paire de maturités protège le mieux ?** Pour chaque paire (m₁, m₂), on apparie la duration cible, puis on mesure la **pire perte de surplus** sur des chocs parallèles entre −3 et +3 points.

```python
chocs = np.linspace(-0.03, 0.03, 13)
res = []
for m1 in (2, 3, 5, 7, 10):
    for m2 in (15, 20, 25, 30, 40):
        d1, d2 = m1 / (1 + y0[m1 - 1]), m2 / (1 + y0[m2 - 1])
        w2 = (D_cible - d1) / (d2 - d1)
        if 0 <= w2 <= 1:
            w = {m1: 1 - w2, m2: w2}
            res.append((m1, m2, min(dS(w, dy) for dy in chocs)))
res = sorted(res, key=lambda r: -r[2])
print(pd.DataFrame(res[:5], columns=["m1", "m2", "pire variation du surplus (M€)"]).round(2).to_string(index=False))
print(pd.DataFrame(res[-3:], columns=["m1", "m2", "pire variation du surplus (M€)"]).round(2).to_string(index=False))
```
<!--sortie-->
```text
 m1  m2  pire variation du surplus (M€)
  2  30                             0.0
  2  40                             0.0
  3  40                             0.0
  5  40                             0.0
  7  40                             0.0
 m1  m2  pire variation du surplus (M€)
  5  20                          -40.47
  7  20                          -43.52
 10  20                          -48.31
```

**Lecture.** Les meilleures paires sont les plus **éloignées** (un haltère très court et très long) : c'est la condition de convexité de Redington (la convexité de l'actif doit entourer celle du passif). Les paires proches du passif (par exemple 10 et 20 ans, celle de l'étape 2) laissent une perte de plusieurs dizaines de M€ pour un choc de 3 points.

```python hide
NUM("a3_wcible", D_cible); NUM("a3_best_m1", res[0][0]); NUM("a3_best_m2", res[0][1]); NUM("a3_best", res[0][2])
NUM("a3_worst_m1", res[-1][0]); NUM("a3_worst_m2", res[-1][1]); NUM("a3_worst", res[-1][2])
```
<!--sortie-->
```text
NUM a3_wcible 14.705283846271243
NUM a3_best_m1 2
NUM a3_best_m2 30
NUM a3_best 5.960464477539062e-14
NUM a3_worst_m1 10
NUM a3_worst_m2 20
NUM a3_worst -48.31053162424678
```

Ici, la meilleure paire est (2 ; 30) ans, avec une pire variation de 0,00 M€ ; la moins bonne est (10 ; 20) ans, avec -48,3 M€.

### Application 7.4 — Chocs de courbe et durations par maturité

*Sections du livre : 7.1.5, 7.1.6.* **Objectif** : lire l'exposition du passif nœud par nœud et la tester sur des chocs non parallèles, puis sur les pires mouvements de l'historique.

**Étape 1 — Durations par maturité.** On déplace un nœud de la courbe à neuf points de 1 point de base et on mesure la variation de valeur du passif.

```python
noeuds = [0.25, 1, 2, 3, 5, 7, 10, 20, 30]
kr = {}
for k, m in enumerate(noeuds):
    cc = b.c0.copy(); cc[k] += 0.0001
    kr[m] = (O.vp(b.flux, O.taux_annuels(cc)) - b.L0) / 1e3
print(pd.Series(kr, name="Δ passif (k€) pour +1 pb").round(0).to_string())
```
<!--sortie-->
```text
0.25       0.0
1.00      -2.0
2.00      -4.0
3.00      -9.0
5.00     -19.0
7.00     -32.0
10.00   -111.0
20.00   -196.0
30.00   -373.0
```

**Étape 2 — Trois chocs.** Parallèle (+1 pt), pentification (courts −0,5 pt, longs +1 pt) et aplatissement. On mesure la variation du surplus du portefeuille apparié de l'application 7.3.

```python
def dS_courbe(w, ys):
    return (val_actif(w, ys) - b.A0 - (O.vp(b.flux, ys) - b.L0)) / 1e6
for nom, ys in (("parallèle +1", y0 + 0.01), ("pentification", O.choc_pente(y0, -0.005, 0.01)),
                ("aplatissement", O.choc_pente(y0, 0.01, -0.005))):
    print(f"{nom:15s} Δ surplus = {dS_courbe(w_app, ys):6.1f} M€")
```
<!--sortie-->
```text
parallèle +1    Δ surplus =   -2.5 M€
pentification   Δ surplus =   -7.2 M€
aplatissement   Δ surplus =    4.2 M€
```

**Étape 3 — Les pires mouvements de l'historique.** À partir de `courbe_taux.csv`, on calcule les variations de la courbe sur 12 mois glissants, puis on revalorise le bilan avec la variation la **pire** pour le surplus.

```python
C = b.courbe
var12 = C[12:] - C[:-12]
pertes = []
for v in var12:
    ys = O.taux_annuels(np.maximum(b.c0 + v, 0.0))
    pertes.append(dS_courbe(w_app, ys))
i = int(np.argmin(pertes))
print("pire variation sur 12 mois :", round(pertes[i], 1), "M€ ; variation du taux à 5 ans :", round(100 * var12[i][4], 2), "pt")
```
<!--sortie-->
```text
pire variation sur 12 mois : -11.2 M€ ; variation du taux à 5 ans : -1.28 pt
```

**Lecture.** La pentification coûte plusieurs fois plus que le parallèle de même amplitude, parce qu'elle frappe les maturités longues où le passif est concentré. Le pire mouvement sur 12 mois est une **baisse** des taux : c'est le risque identifié en 7.1.7.

```python hide
NUM("a4_kr30", -kr[30]); NUM("a4_kr10", -kr[10]); NUM("a4_pent", dS_courbe(w_app, O.choc_pente(y0, -0.005, 0.01)))
NUM("a4_para", dS_courbe(w_app, y0 + 0.01)); NUM("a4_pire", pertes[i]); NUM("a4_pire5", 100 * var12[i][4])
```
<!--sortie-->
```text
NUM a4_kr30 372.71548620176316
NUM a4_kr10 110.6460590569973
NUM a4_pent -7.202248812294125
NUM a4_para -2.4546971838560103
NUM a4_pire -11.24689786761397
NUM a4_pire5 -1.279
```

Ici, le nœud 30 ans porte 373 k€ par point de base contre 111 k€ pour le nœud 10 ans ; la pentification coûte -7,2 M€ contre -2,5 M€ pour le choc parallèle ; le pire mouvement sur 12 mois coûte -11,2 M€ (taux à 5 ans : -1,28 point).

### Application 7.5 — La frontière efficiente sur cinq actifs

*Sections du livre : 7.2.1 à 7.2.3.* **Objectif** : estimer μ et Σ, tracer la frontière, comparer les portefeuilles de variance minimale et tangent, avec et sans vente à découvert.

**Étape 1 — Paramètres annualisés.**

```python
ACT = list(rend.columns)
mu, S = O.stats_annuelles(rend)
sd = np.sqrt(np.diag(S))
print(pd.DataFrame({"rendement (%)": 100 * mu, "volatilité (%)": 100 * sd}, index=ACT).round(1).to_string())
```
<!--sortie-->
```text
             rendement (%)  volatilité (%)
actions_A              5.6            18.7
actions_B              4.3            22.8
obligations            4.0             4.4
immobilier             5.7            13.2
matieres              -2.9            22.0
```

**Étape 2 — Variance minimale : formule fermée et optimisation.** Sans contrainte de signe, w = Σ⁻¹1 / (1ᵀΣ⁻¹1). Avec la contrainte « poids positifs », on passe par l'optimiseur.

```python
un = np.ones(5)
w_libre = np.linalg.solve(S, un); w_libre /= w_libre.sum()
w_pos = O.min_variance(S)
print(pd.DataFrame({"sans contrainte": w_libre, "poids positifs": w_pos}, index=ACT).round(3).to_string())
print("volatilité :", round(100 * O.vol_ptf(w_libre, S), 3), "%", round(100 * O.vol_ptf(w_pos, S), 3), "%")
```
<!--sortie-->
```text
             sans contrainte  poids positifs
actions_A              0.019           0.019
actions_B              0.012           0.012
obligations            0.888           0.888
immobilier             0.062           0.062
matieres               0.019           0.019
volatilité : 4.09 % 4.09 %
```

**Étape 3 — La frontière.** Pour 30 rendements cibles, on cherche les poids de variance minimale (poids positifs) ; on trace la frontière avec les actifs.

```python
cibles = np.linspace(w_pos @ mu, mu.max(), 30)
W = O.frontiere(mu, S, cibles)
vols = np.sqrt(np.einsum("ij,jk,ik->i", W, S, W))
fig, ax = plt.subplots(figsize=(6, 3.6))
ax.plot(100 * vols, 100 * cibles); ax.scatter(100 * sd, 100 * mu, color="black")
for i, a in enumerate(ACT): ax.annotate(a, (100 * sd[i], 100 * mu[i]), fontsize=7)
ax.set_xlabel("écart-type (%)"); ax.set_ylabel("rendement (%)")
plt.close(fig)                     # dans un notebook : plt.show()
print("points de la frontière :", len(W), "; vol. min.", round(100 * vols[0], 2), "% ; vol. max.", round(100 * vols[-1], 2), "%")
```
<!--sortie-->
```text
points de la frontière : 30 ; vol. min. 4.09 % ; vol. max. 13.2 %
```

**Étape 4 — Le portefeuille tangent.** Sharpe maximal pour un taux sans risque de 1,5 %, avec et sans vente à découvert.

```python
w_t = O.tangent(mu, S, 0.015)
w_t_libre = np.linalg.solve(S, mu - 0.015); w_t_libre /= w_t_libre.sum()
print(pd.DataFrame({"poids positifs": w_t, "sans contrainte": w_t_libre}, index=ACT).round(3).to_string())
sh = lambda w: (w @ mu - 0.015) / O.vol_ptf(w, S)
print("Sharpe :", round(sh(w_t), 3), "(positifs),", round(sh(w_t_libre), 3), "(sans contrainte)")
```
<!--sortie-->
```text
             poids positifs  sans contrainte
actions_A             0.038            0.069
actions_B             0.000           -0.001
obligations           0.840            0.880
immobilier            0.122            0.151
matieres              0.000           -0.099
Sharpe : 0.666 (positifs), 0.734 (sans contrainte)
```

**Lecture.** Sans contrainte de signe, l'optimiseur vend à découvert des actifs au rendement estimé faible et lève de l'effet de levier sur ceux qu'il juge attractifs ; le Sharpe augmente, **sur l'historique**, au prix de poids extrêmes que personne ne tiendrait. L'interdiction de la vente à découvert est une **régularisation**.

```python hide
NUM("a5_vol_libre", 100 * O.vol_ptf(w_libre, S)); NUM("a5_vol_pos", 100 * O.vol_ptf(w_pos, S))
NUM("a5_wmin_libre", 100 * w_libre.min()); NUM("a5_wmax_libre", 100 * w_libre.max())
NUM("a5_sh_pos", sh(w_t)); NUM("a5_sh_libre", sh(w_t_libre)); NUM("a5_tlibre_min", 100 * w_t_libre.min()); NUM("a5_tlibre_max", 100 * w_t_libre.max())
```
<!--sortie-->
```text
NUM a5_vol_libre 4.089868238088254
NUM a5_vol_pos 4.089868238090334
NUM a5_wmin_libre 1.2054329219495883
NUM a5_wmax_libre 88.8416590103852
NUM a5_sh_pos 0.6656596636347749
NUM a5_sh_libre 0.7340739698341316
NUM a5_tlibre_min -9.874386963228163
NUM a5_tlibre_max 88.00048380101163
```

Ici, la variance minimale est **la même** avec ou sans contrainte de signe (4,09 % de volatilité), parce que tous les poids de la formule fermée sont positifs (1 % à 89 %). Le portefeuille tangent sans contrainte a un Sharpe de 0,73 contre 0,67 avec poids positifs, mais des poids de -10 % à 88 %.

### Application 7.6 — Contributions au risque et parité des risques

*Sections du livre : 7.2.4.* **Objectif** : calculer les contributions d'Euler, vérifier qu'elles s'additionnent, trouver le portefeuille de parité des risques par un algorithme simple.

**Étape 1 — Contributions d'un portefeuille égal pondéré.**

```python
we = np.full(5, 0.2)
def rc(w): return w * (S @ w) / np.sqrt(w @ S @ w)
r = rc(we)
print(pd.DataFrame({"contribution": r, "part (%)": 100 * r / r.sum()}, index=ACT).round(4).to_string())
print("somme =", round(r.sum(), 6), "; volatilité =", round(O.vol_ptf(we, S), 6))
```
<!--sortie-->
```text
             contribution  part (%)
actions_A          0.0305   26.1926
actions_B          0.0381   32.7021
obligations        0.0002    0.1310
immobilier         0.0186   15.9192
matieres           0.0292   25.0551
somme = 0.116558 ; volatilité = 0.116558
```

**Étape 2 — Parité des risques par itérations.** On rapproche chaque contribution de la cible σ/n en multipliant les poids par (cible / contribution)^0,5, puis on renormalise.

```python
w = np.full(5, 0.2)
for it in range(2000):
    r = rc(w)
    if np.abs(r / r.sum() - 0.2).max() < 1e-8:          # contributions égales à 1e-8 près : arrêt
        break
    w = w * (r.mean() / r) ** 0.5
    w /= w.sum()
print("itérations :", it, "; poids :", w.round(3))
print("contributions (%) :", (100 * rc(w) / rc(w).sum()).round(2))
```
<!--sortie-->
```text
itérations : 18 ; poids : [0.087 0.073 0.623 0.128 0.089]
contributions (%) : [20. 20. 20. 20. 20.]
```

**Étape 3 — Comparaison.** Rendement, volatilité et Sharpe des trois portefeuilles (égal pondéré, variance minimale, parité des risques).

```python
w_min = O.min_variance(S)
tab = {nom: [100 * (v @ mu), 100 * O.vol_ptf(v, S), (v @ mu - 0.015) / O.vol_ptf(v, S)] for nom, v in
       (("égal", we), ("variance min.", w_min), ("parité", w))}
print(pd.DataFrame(tab, index=["rendement (%)", "volatilité (%)", "Sharpe"]).T.round(2).to_string())
```
<!--sortie-->
```text
               rendement (%)  volatilité (%)  Sharpe
égal                    3.36           11.66    0.16
variance min.           4.03            4.09    0.62
parité                  3.78            5.78    0.40
```

**Lecture.** Le portefeuille de parité des risques est un compromis : plus de risque que la variance minimale, bien moins que l'égal pondéré, et il n'utilise aucune estimation de rendement (seulement Σ) : c'est son principal attrait.

```python hide
NUM("a6_wobl", 100 * w[2]); NUM("a6_vol", 100 * O.vol_ptf(w, S)); NUM("a6_it", it)
NUM("a6_eq_obl", 100 * rc(we)[2] / rc(we).sum())
```
<!--sortie-->
```text
NUM a6_wobl 62.29466908051376
NUM a6_vol 5.7800750893469734
NUM a6_it 18
NUM a6_eq_obl 0.13104321161395846
```

Ici, la parité demande 62 % d'obligations pour une volatilité de 5,8 %, en 18 itérations ; dans le portefeuille égal pondéré, les obligations produisent 0,1 % du risque.

### Application 7.7 — Estimation, instabilité et rétrécissement

*Sections du livre : 7.2.6.* **Objectif** : mesurer l'incertitude des poids optimaux par rééchantillonnage, puis l'effet du rétrécissement selon le nombre d'actifs.

**Étape 1 — Rééchantillonnage par blocs d'un an.** On tire 16 blocs de 250 jours (avec remise), on recalcule le portefeuille tangent, et on répète 100 fois.

```python
rng = np.random.default_rng(0)
blocs = [rend.iloc[s:s + 250] for s in range(0, len(rend) - 250, 250)]
W = []
for _ in range(100):
    echantillon = pd.concat([blocs[i] for i in rng.integers(0, len(blocs), len(blocs))])
    m_, S_ = O.stats_annuelles(echantillon)
    W.append(O.tangent(m_, S_, 0.015))
W = np.array(W)
print(pd.DataFrame({"moyenne": W.mean(axis=0), "écart-type": W.std(axis=0), "min": W.min(axis=0), "max": W.max(axis=0)}, index=ACT).round(2).to_string())
```
<!--sortie-->
```text
             moyenne  écart-type   min   max
actions_A       0.05        0.06  0.00  0.21
actions_B       0.02        0.03  0.00  0.12
obligations     0.81        0.12  0.36  1.00
immobilier      0.12        0.13  0.00  0.64
matieres        0.00        0.01  0.00  0.07
```

**Étape 2 — Même exercice pour la variance minimale.**

```python
Wm = np.array([O.min_variance(O.stats_annuelles(pd.concat([blocs[i] for i in rng.integers(0, len(blocs), len(blocs))]))[1]) for _ in range(100)])
print("écart-type des poids (variance min.) :", Wm.std(axis=0).round(3))
```
<!--sortie-->
```text
écart-type des poids (variance min.) : [0.011 0.007 0.015 0.01  0.006]
```

**Étape 3 — Rétrécissement selon le nombre d'actifs.** Volatilité vraie du portefeuille de variance minimale sans contrainte, construit sur 120 observations, pour n actifs simulés (modèle à facteurs) : covariance empirique, rétrécie (Ledoit–Wolf), poids égaux et optimum.

```python
lignes = {}
for n in (10, 30, 60, 100):
    lignes[n] = 100 * O.experience_retrecissement(n=n, T=120, reps=40, seed=1)
print(pd.DataFrame(lignes, index=["empirique", "Ledoit–Wolf", "poids égaux", "optimum"]).T.round(2).to_string())
```
<!--sortie-->
```text
     empirique  Ledoit–Wolf  poids égaux  optimum
10        1.98         1.98         5.39     1.91
30        1.35         1.30         9.92     1.18
60        1.03         0.90        10.28     0.73
100       1.60         0.80        11.25     0.64
```

**Lecture.** Les poids du portefeuille tangent varient énormément d'un rééchantillon à l'autre ; ceux de la variance minimale beaucoup moins. Quand n grandit avec T = 120 fixé, la covariance empirique se dégrade (au-delà de n = T elle n'est même plus inversible) et le rétrécissement devient très utile.

```python hide
NUM("a7_sd_tan_obl", W[:, 2].std()); NUM("a7_sd_min_obl", Wm[:, 2].std())
NUM("a7_lw10_e", lignes[10][0]); NUM("a7_lw10_l", lignes[10][1]); NUM("a7_lw100_e", lignes[100][0]); NUM("a7_lw100_l", lignes[100][1])
```
<!--sortie-->
```text
NUM a7_sd_tan_obl 0.12041583574478183
NUM a7_sd_min_obl 0.014603276669007847
NUM a7_lw10_e 1.9820608494856382
NUM a7_lw10_l 1.9832504071180737
NUM a7_lw100_e 1.602277654448308
NUM a7_lw100_l 0.8042975829687375
```

Ici, l'écart-type du poids des obligations est de 0,12 pour le tangent et de 0,01 pour la variance minimale. À n = 10, la covariance empirique et la covariance rétrécie sont proches (1,98 % et 1,98 %) ; à n = 100, l'écart est net (1,60 % contre 0,80 %).

### Application 7.8 — Surplus, VaR et simulation sur dix ans

*Sections du livre : 7.3.* **Objectif** : mesurer le risque du surplus de plusieurs allocations, optimiser sous un budget de risque, simuler le taux de couverture, puis tester l'effet d'une corrélation entre taux et actions.

**Étape 1 — Scénarios annuels.** Courbe et marchés tirés dans l'historique ; gain en euros de six instruments et variation du passif.

```python
dY, ann = O.tirages_annuels(b, 5000, 21)
X, dliab = O.pnl_instruments(b, dY, ann)
S0 = b.A0 - b.L0
w_app_v = O.poids_vecteur(w_app)
w_marche = O.poids_vecteur({5: 0.40, "act": 0.45, "imm": 0.15})
for nom, w in (("apparié", w_app_v), ("marché", w_marche)):
    dSs = X @ w - dliab
    v, e = O.var_es(dSs)
    print(f"{nom:8s} sd {dSs.std()/1e6:6.1f}  VaR 99,5 % {v/1e6:6.1f}  ES 99 % {e/1e6:6.1f}  S0/VaR {S0/v:5.2f}")
```
<!--sortie-->
```text
apparié  sd    2.0  VaR 99,5 %    5.1  ES 99 %    5.9  S0/VaR  8.94
marché   sd   58.2  VaR 99,5 %  134.1  ES 99 %  138.6  S0/VaR  0.34
```

**Étape 2 — Allocation optimale sous un budget de risque.** On cherche l'allocation de gain espéré maximal dont l'écart-type du surplus est de 15 M€.

```python
w_opt = O.surplus_frontiere(X, dliab, [15e6])[0]
d_opt = X @ w_opt - dliab
print({k: round(float(v), 2) for k, v in zip(O.NOMS_INSTR, w_opt)})
print("gain espéré", round(d_opt.mean() / 1e6, 1), "M€ ; sd", round(d_opt.std() / 1e6, 1), "M€ ; VaR", round(O.var_es(d_opt)[0] / 1e6, 1), "M€")
```
<!--sortie-->
```text
{'ZC 5 ans': 0.29, 'ZC 10 ans': 0.0, 'ZC 20 ans': 0.0, 'ZC 30 ans': 0.55, 'actions': 0.07, 'immobilier': 0.09}
gain espéré 5.0 M€ ; sd 15.0 M€ ; VaR 28.4 M€
```

**Étape 3 — Taux de couverture sur dix ans.** 1 000 trajectoires, trois allocations.

```python
w_marche_d = {5: 0.40, "act": 0.45, "imm": 0.15}
w_opt_d = {k: v for k, v in zip(O.INSTR, w_opt) if v > 1e-6}
lignes = {}
for nom, w in (("marché", w_marche_d), ("apparié", w_app), ("optimisé", w_opt_d)):
    FR = O.simuler_alm(b, w, N=1000, annees=10, seed=3)
    lignes[nom] = [np.median(FR[:, 10]), 100 * (FR.min(axis=1) < 1).mean()]
print(pd.DataFrame(lignes, index=["médiane A/L à 10 ans", "P(A/L < 1 un jour) %"]).T.round(2).to_string())
```
<!--sortie-->
```text
          médiane A/L à 10 ans  P(A/L < 1 un jour) %
marché                    1.43                  46.0
apparié                   1.14                   0.2
optimisé                  1.26                   6.0
```

**Étape 4 — Et si les taux et les actions étaient corrélés ?** Les tirages sont indépendants. On impose une corrélation de rang ρ entre la variation du **niveau** de la courbe (taux à 10 ans) et le rendement des actions, en réordonnant les scénarios d'actions (copule gaussienne), puis on recalcule la VaR de l'allocation « marché ».

```python
from scipy.stats import norm, rankdata
def avec_correlation(rho, seed=0):
    rng = np.random.default_rng(seed)
    u = norm.ppf(rankdata(dY[:, 6]) / (len(dY) + 1))                 # rang des variations du taux à 10 ans, en loi normale
    z = rho * u + np.sqrt(1 - rho**2) * rng.normal(size=len(dY))
    cible = np.argsort(np.argsort(z))                                # rang cible des rendements d'actions
    ann2 = ann.copy()
    ann2[:, :2] = np.sort(ann[:, :2], axis=0)[cible]
    ann2[:, 3] = np.sort(ann[:, 3])[cible]
    return O.pnl_instruments(b, dY, ann2)
for rho in (-0.5, 0.0, 0.5):
    X2, dl2 = avec_correlation(rho)
    print(f"corrélation {rho:+.1f} : VaR 99,5 % du portefeuille marché = {O.var_es(X2 @ w_marche - dl2)[0] / 1e6:6.1f} M€")
```
<!--sortie-->
```text
corrélation -0.5 : VaR 99,5 % du portefeuille marché =  110.0 M€
corrélation +0.0 : VaR 99,5 % du portefeuille marché =  144.8 M€
corrélation +0.5 : VaR 99,5 % du portefeuille marché =  166.5 M€
```

**Lecture.** L'allocation « apparié » a un risque de surplus minime, la « marché » un risque très supérieur au surplus initial. Dans l'étape 4, la corrélation entre les taux et les actions change la VaR : quand elle est **positive**, les baisses de taux (qui gonflent le passif) coïncident avec des baisses d'actions, ce qui cumule les mauvaises nouvelles du passif et de l'actif ; quand elle est négative, elles se compensent. L'hypothèse d'indépendance du livre n'est donc pas neutre.

```python hide
v_a = O.var_es(X @ w_app_v - dliab)[0]; v_m = O.var_es(X @ w_marche - dliab)[0]
NUM("a8_var_app", v_a / 1e6); NUM("a8_var_mar", v_m / 1e6); NUM("a8_S0", S0 / 1e6)
NUM("a8_gain_opt", d_opt.mean() / 1e6); NUM("a8_var_opt", O.var_es(d_opt)[0] / 1e6)
vr = {rho: O.var_es(X2 @ w_marche - dl2)[0] / 1e6 for rho in (-0.5, 0.5) for X2, dl2 in [avec_correlation(rho)]}
NUM("a8_var_m05", vr[-0.5]); NUM("a8_var_p05", vr[0.5])
```
<!--sortie-->
```text
NUM a8_var_app 5.149561246166238
NUM a8_var_mar 134.1491567818308
NUM a8_S0 46.02259525825697
NUM a8_gain_opt 4.970110434369783
NUM a8_var_opt 28.37760356984003
NUM a8_var_m05 110.00211015125527
NUM a8_var_p05 166.52259440792182
```

Ici, le surplus initial est de 46 M€ ; la VaR de l'allocation apparié est 5,1 M€, celle de l'allocation marché 134 M€. L'allocation optimisée à 15 M€ de risque a un gain espéré de 5,0 M€ et une VaR de 28 M€. Avec une corrélation de −0,5 la VaR « marché » vaut 110 M€, avec +0,5 167 M€.

## Exercices

### Exercice 7.1 ⭐ — Prix et duration à la main (section 7.1.2 du livre)

Une obligation de nominal 100 € à deux ans verse un coupon de 5 € par an. Le taux est 4 %. Calculez à la main son prix, sa duration de Macaulay et sa duration modifiée.

### Exercice 7.2 ⭐ — Variation du prix : duration et convexité (7.1.2)

Pour l'obligation de l'exercice 7.1, calculez la convexité, puis la variation relative du prix pour une hausse du taux de 1 point avec la duration seule, avec la duration et la convexité, et exactement.

### Exercice 7.3 ⭐⭐ — Durations remarquables (7.1.2, 7.1.3)

(a) Montrez que la duration de Macaulay d'un zéro-coupon de maturité m vaut m. (b) Montrez que celle d'une perpétuité de coupon annuel c, au taux y, vaut (1 + y)/y. (c) Que vaut-elle à 2 % ? Qu'en concluez-vous pour un passif de très longue durée ?

### Exercice 7.4 ⭐⭐ — L'écart de duration en euros (7.1.4)

Un assureur a un actif de 110 M€ et un passif de 100 M€, de duration modifiée 8 ans. (a) Quelle duration modifiée doit avoir l'actif pour que le surplus soit insensible à un déplacement parallèle des taux ? (b) Si l'on égalise les durations (8 et 8), de combien varie le surplus pour une hausse de 1 point ? Pour une baisse de 1 point ?

### Exercice 7.5 ⭐⭐ — Les conditions de Redington en chiffres (7.1.4)

Le passif est un paiement unique de 1 000 € dans 5 ans ; le taux plat est de 5 %. On le couvre avec des zéros-coupons de maturités 3 et 7 ans. (a) Quelles valeurs investir dans chacun pour égaler la valeur actuelle **et** la duration ? (b) Vérifiez la condition de convexité. (c) Calculez à la main la variation du surplus après un déplacement du taux de +2 points et de −2 points. Interprétez.

### Exercice 7.6 ⭐ — Rendement et risque d'un portefeuille (7.2.1)

Deux actifs : μ = (8 %, 4 %), σ = (25 %, 8 %), corrélation 0,3. Pour le portefeuille 40 %/60 %, calculez le rendement espéré et l'écart-type. Que vaudrait l'écart-type avec une corrélation de 1 ?

### Exercice 7.7 ⭐⭐ — Variance minimale à deux actifs (7.2.2)

Avec les chiffres de l'exercice 7.6, (a) calculez le poids de variance minimale de l'actif risqué par la formule du livre. (b) À partir de quelle corrélation ce poids devient-il négatif ? (c) Pour ρ = 0,5, quel est le portefeuille de variance minimale avec et sans vente à découvert, et quelles volatilités ?

### Exercice 7.8 ⭐⭐ — Contributions au risque à la main (7.2.4)

Trois actifs de volatilités 10 %, 20 %, 30 %, de corrélations ρ₁₂ = 0,5, ρ₁₃ = 0,2, ρ₂₃ = 0,1, détenus à 50 %, 30 % et 20 %. Calculez la volatilité du portefeuille et la contribution de chaque actif ; vérifiez que la somme des contributions est la volatilité.

### Exercice 7.9 ⭐⭐⭐ — Le portefeuille tangent (7.2.3)

(a) Montrez, en maximisant le ratio de Sharpe, que le portefeuille tangent sans contrainte de signe est proportionnel à Σ⁻¹(μ − r_f 1). (b) Vérifiez-le numériquement sur les cinq actifs (taux sans risque de 1,5 %) en comparant au résultat de l'optimiseur avec `long_only=False`.

### Exercice 7.10 ⭐⭐ — Combien d'années pour distinguer deux actifs ? (7.2.6)

Deux actifs ont la même volatilité de 15 % et une corrélation de 0,5. Leur rendement espéré diffère de 3 points. Combien d'années d'observation faut-il pour que cette différence dépasse deux erreurs types ? Comparez à la longueur de l'historique du chapitre et vérifiez par simulation la probabilité d'estimer le bon signe avec 16 ans.

### Exercice 7.11 ⭐⭐⭐ — Précision d'une VaR à 99,5 % (7.3.3)

Pour l'allocation « Mixte » (80 % apparié, 14 % d'actions, 6 % d'immobilier), estimez la VaR à 99,5 % du surplus avec N = 500, 2 000 et 8 000 scénarios, en répétant chaque estimation avec 8 graines. Calculez l'écart-type des estimations et commentez sa décroissance avec N.

### Exercice 7.12 ⭐⭐ — Échéancier de refixation d'une banque (7.1.5, 7.1.6)

Reprenez l'échéancier du livre (actifs 200, 150, 400, 250 M€ ; passifs 430, 250, 170, 100 M€ ; parts de l'année restante 0,875, 0,375, 0, 0). (a) Calculez la variation de marge nette d'intérêt pour −1 point et +1 point. (b) Quel montant supplémentaire d'actif à taux variable (tranche « moins de 3 mois ») annule la sensibilité à un déplacement parallèle ? (c) Quel est l'effet, pour cette banque, d'une pentification (taux courts +0,5 point, longs +1,5 point, la tranche « 3 à 12 mois » à +1 point) ?

## Corrigés

### Corrigé 7.1

Flux : 5 à t = 1, 105 à t = 2. Valeurs actuelles : 5/1,04 = 4,8077 et 105/1,04² = 97,0784, donc **P = 101,8861 €**. Duration de Macaulay : (1 × 4,8077 + 2 × 97,0784)/101,8861 = 198,9645/101,8861 ≈ **1,953 an**. Duration modifiée : 1,953/1,04 ≈ **1,878**.

```python
f = np.array([5.0, 105.0]); t = np.array([1, 2]); va = f / 1.04 ** t
P = va.sum(); D = (t * va).sum() / P
print(round(P, 4), round(D, 4), round(D / 1.04, 4))
```
<!--sortie-->
```text
101.8861 1.9528 1.8777
```

### Corrigé 7.2

Convexité : C = Σ t(t+1)·VA / ((1+y)² P) = (2 × 4,8077 + 6 × 97,0784)/(1,0816 × 101,8861) ≈ 5,373. Pour Δy = +0,01 :

- **duration seule** : −1,878 × 0,01 = −1,878 % ;
- **avec la convexité** : −1,878 % + ½ × 5,373 × 0,0001 = −1,851 % ;
- **exact** : à 5 %, le prix vaut 5/1,05 + 105/1,05² = 100 €, soit 100/101,8861 − 1 = **−1,851 %**.

À deux ans, la convexité suffit à retrouver le résultat exact au millième de point.

```python
D_mod = D / 1.04
C = (t * (t + 1) * va).sum() / (1.04 ** 2 * P)
exact = (f / 1.05 ** t).sum() / P - 1
print(round(C, 3), round(-D_mod * 0.01, 5), round(-D_mod * 0.01 + 0.5 * C * 0.01**2, 5), round(exact, 5))
```
<!--sortie-->
```text
5.373 -0.01878 -0.01851 -0.01851
```

### Corrigé 7.3

(a) Un seul flux F à la date m : D = m · F v^m / (F v^m) = m. (b) Avec v = 1/(1+y), P = c Σ v^t = c/y et Σ t v^t = v/(1−v)² = (1+y)/y². Donc D = c (1+y)/y² ÷ (c/y) = **(1+y)/y**. (c) À 2 % : 1,02/0,02 = **51 ans**. Un engagement qui n'a pas de terme (rente viagère, contrat vie entière) a une duration de plusieurs dizaines d'années quand les taux sont bas : une variation d'un point des taux modifie sa valeur de plus de 50 %. C'est ce qui rend le risque de taux des assureurs vie si sensible.

```python
y = 0.02
t = np.arange(1, 5000)
va = 1 / (1 + y) ** t
print(round((t * va).sum() / va.sum(), 3), round((1 + y) / y, 3))
```
<!--sortie-->
```text
51.0 51.0
```

### Corrigé 7.4

(a) D_A = D_L × L/A = 8 × 100/110 = **7,27 ans**. (b) Avec D_A = D_L = 8 : ΔA ≈ −8 × 110 × 0,01 = −8,8 M€ et ΔL ≈ −8 × 100 × 0,01 = −8,0 M€, donc ΔS ≈ **−0,8 M€** pour +1 point, et **+0,8 M€** pour −1 point (à l'ordre un). L'égalité des durations laisse une sensibilité de 0,8 M€ par point, soit 10 % de la sensibilité du passif.

```python
A, L, D = 110.0, 100.0, 8.0
print(round(D * L / A, 3), round(-D * A * 0.01 + D * L * 0.01, 3))
```
<!--sortie-->
```text
7.273 -0.8
```

### Corrigé 7.5

(a) VA du passif : 1 000/1,05⁵ = 783,53 €. Duration modifiée du passif : 5/1,05 = 4,762. Pour des zéros-coupons, la duration modifiée d'un titre de maturité m vaut m/1,05 : avec des valeurs x₃ et x₇, x₃ + x₇ = 783,53 et (3x₃ + 7x₇)/1,05 = 4,762 × 783,53, d'où 3x₃ + 7x₇ = 3 917,6 ; avec x₃ = 783,53 − x₇ : 2 350,6 + 4x₇ = 3 917,6, soit x₇ = 391,76 et x₃ = 391,76 : **moitié-moitié**. (b) Convexité : zéro-coupon de maturité m : m(m+1)/1,05² ; pour 3 et 7 ans : 10,884 et 50,794, moyenne à poids égaux 30,839 ; pour le passif, 5 × 6/1,05² = 27,211. L'actif est **plus convexe** : la condition (iii) est satisfaite. (c) Valeur de l'actif : x₃ (1,05/(1,05+Δy))³ + x₇ (1,05/(1,05+Δy))⁷, valeur du passif : 1 000/(1,05+Δy)⁵ — voir le code. Le surplus **augmente** dans les deux sens (+0,51 € pour +2 points et +0,64 € pour −2 points sur un passif de 783 €) : c'est exactement ce que promet Redington.

```python
y, dy = 0.05, 0.02
L0 = 1000 / (1 + y) ** 5
x3 = x7 = L0 / 2
for d_ in (-dy, dy):
    A1 = x3 * ((1 + y) / (1 + y + d_)) ** 3 + x7 * ((1 + y) / (1 + y + d_)) ** 7
    L1 = 1000 / (1 + y + d_) ** 5
    print(f"Δy = {d_:+.2f} : ΔS = {A1 - L1:+.3f} €")
```
<!--sortie-->
```text
Δy = -0.02 : ΔS = +0.638 €
Δy = +0.02 : ΔS = +0.508 €
```

```python hide
def _dS5(d_):
    return x3 * ((1 + y) / (1 + y + d_)) ** 3 + x7 * ((1 + y) / (1 + y + d_)) ** 7 - 1000 / (1 + y + d_) ** 5
NUM("c5_dp", _dS5(dy)); NUM("c5_dm", _dS5(-dy))
```
<!--sortie-->
```text
NUM c5_dp 0.5077345015737365
NUM c5_dm 0.6381422430247312
```

### Corrigé 7.6

Rendement espéré : 0,4 × 8 + 0,6 × 4 = **5,6 %**. Variance : 0,4² × 0,0625 + 0,6² × 0,0064 + 2 × 0,4 × 0,6 × 0,3 × 0,25 × 0,08 = 0,01 + 0,002304 + 0,00288 = 0,015184, soit un écart-type de **12,32 %**. Avec ρ = 1 : 0,4 × 25 + 0,6 × 8 = **14,8 %** : la diversification enlève 2,5 points de volatilité.

```python
w = np.array([0.4, 0.6]); s = np.array([0.25, 0.08])
for rho in (0.3, 1.0):
    Sg = np.array([[s[0]**2, rho * s[0] * s[1]], [rho * s[0] * s[1], s[1]**2]])
    print(rho, round(100 * np.sqrt(w @ Sg @ w), 2))
```
<!--sortie-->
```text
0.3 12.32
1.0 14.8
```

### Corrigé 7.7

(a) w* = (σ₂² − ρσ₁σ₂)/(σ₁² + σ₂² − 2ρσ₁σ₂) = (0,0064 − 0,006)/(0,0625 + 0,0064 − 0,012) = 0,0004/0,0569 ≈ **0,7 %**. (b) Le numérateur s'annule pour ρ = σ₂/σ₁ = 0,08/0,25 = **0,32** ; au-delà, w* < 0. (c) Pour ρ = 0,5 : numérateur 0,0064 − 0,01 = −0,0036 ; dénominateur 0,0625 + 0,0064 − 0,02 = 0,0489 ; w* = **−7,4 %** (vente à découvert de l'actif risqué) ; avec cette position, la volatilité est de 7,83 % contre 8 % pour 100 % d'obligations (sans vente à découvert, on garde 100 % d'obligations). Le gain de la vente à découvert est ici de 0,17 point de volatilité.

```python
s1, s2 = 0.25, 0.08
for rho in (0.3, 0.32, 0.5):
    w = (s2**2 - rho * s1 * s2) / (s1**2 + s2**2 - 2 * rho * s1 * s2)
    v = np.sqrt(w**2 * s1**2 + (1 - w)**2 * s2**2 + 2 * w * (1 - w) * rho * s1 * s2)
    print(rho, round(w, 4), round(100 * v, 3))
```
<!--sortie-->
```text
0.3 0.007 7.998
0.32 0.0 8.0
0.5 -0.0736 7.833
```

### Corrigé 7.8

Covariances : σ₁₂ = 0,5 × 0,1 × 0,2 = 0,01 ; σ₁₃ = 0,2 × 0,1 × 0,3 = 0,006 ; σ₂₃ = 0,1 × 0,2 × 0,3 = 0,006 ; variances 0,01, 0,04, 0,09. Σw = (0,0092 ; 0,0182 ; 0,0228). Variance : 0,5 × 0,0092 + 0,3 × 0,0182 + 0,2 × 0,0228 = 0,01462 ; écart-type **12,09 %**. Contributions w_i(Σw)_i/σ : 0,0046/0,1209 = **3,80 points**, 0,00546/0,1209 = **4,52 points**, 0,00456/0,1209 = **3,77 points** ; somme 12,09 points. Parts : 31,5 %, 37,3 %, 31,2 %. Les contributions sont presque égales alors que les poids ne le sont pas (50, 30, 20 %) : portefeuille proche de la parité des risques.

```python
sg = np.array([0.1, 0.2, 0.3]); R = np.array([[1, .5, .2], [.5, 1, .1], [.2, .1, 1]])
Sg = R * np.outer(sg, sg); w = np.array([0.5, 0.3, 0.2])
vol = np.sqrt(w @ Sg @ w); rcs = w * (Sg @ w) / vol
print(round(100 * vol, 3), (100 * rcs).round(3), round(100 * rcs.sum(), 3), (100 * rcs / rcs.sum()).round(1))
```
<!--sortie-->
```text
12.091 [3.804 4.516 3.771] 12.091 [31.5 37.3 31.2]
```

### Corrigé 7.9

(a) On maximise f(w) = (wᵀm)/√(wᵀΣw) avec m = μ − r_f 1 (le ratio est invariant par multiplication de w : la contrainte de somme 1 se réimpose ensuite). Le gradient s'annule quand m/(wᵀm) = Σw/(wᵀΣw), soit Σw = λm avec λ = (wᵀΣw)/(wᵀm) : donc **w ∝ Σ⁻¹m**, normalisé pour sommer à 1. (b) Le code compare les deux calculs ; l'optimiseur sans contrainte retrouve les poids de la formule (à la tolérance numérique).

```python
mu, S = O.stats_annuelles(rend)
w_f = np.linalg.solve(S, mu - 0.015); w_f /= w_f.sum()
w_o = O.tangent(mu, S, 0.015, long_only=False)
print(w_f.round(3)); print(w_o.round(3)); print("écart max :", float(np.abs(w_f - w_o).max()))
```
<!--sortie-->
```text
[ 0.069 -0.001  0.88   0.151 -0.099]
[ 0.069 -0.001  0.88   0.151 -0.099]
écart max : 1.0728843480301009e-08
```

### Corrigé 7.10

L'écart-type de la différence des deux rendements annuels est σ_d = σ√(2(1 − ρ)) = 0,15 × √(2 × 0,5) = **15 %**. L'erreur type de la différence moyenne sur T années est σ_d/√T. Elle dépasse deux fois l'erreur type quand 3 % ≥ 2 × 15 %/√T, soit √T ≥ 10 et **T ≥ 100 ans**. Avec 16 ans, l'erreur type vaut 15/4 = 3,75 points : la différence de 3 points est **plus petite qu'une erreur type**. Probabilité d'estimer le bon signe : P(N(3 ; 3,75) > 0) = Φ(0,8) ≈ **79 %** : on se trompe une fois sur cinq.

```python
rng = np.random.default_rng(0)
sim = rng.normal(0.03, 0.15 / np.sqrt(16), 200000)
print(round((sim > 0).mean(), 3), round(0.15 / 4, 4))
```
<!--sortie-->
```text
0.787 0.0375
```

### Corrigé 7.11

La VaR à 99,5 % repose sur la queue de l'échantillon (0,5 % des scénarios : 2,5 observations pour N = 500, 40 pour N = 8 000). L'écart-type des estimations diminue en 1/√N environ, donc **lentement** : multiplier N par 16 (de 500 à 8 000) divise l'écart-type par 4 environ (huit répétitions ne permettent pas de le dire plus finement). Le code ci-dessous le mesure (les valeurs exactes dépendent des graines).

```python
w_mix = O.poids_vecteur({k: 0.8 * v for k, v in w_app.items()} | {"act": 0.14, "imm": 0.06})
lignes = {}
for N in (500, 2000, 8000):
    v = []
    for graine in range(8):
        dY_, ann_ = O.tirages_annuels(b, N, 100 + graine)
        X_, dl_ = O.pnl_instruments(b, dY_, ann_)
        v.append(O.var_es(X_ @ w_mix - dl_)[0] / 1e6)
    lignes[N] = [np.mean(v), np.std(v)]
print(pd.DataFrame(lignes, index=["VaR moyenne (M€)", "écart-type (M€)"]).T.round(2).to_string())
```
<!--sortie-->
```text
      VaR moyenne (M€)  écart-type (M€)
500              38.87             3.65
2000             39.81             1.74
8000             40.33             0.59
```

```python hide
NUM("c11_sd500", lignes[500][1]); NUM("c11_sd8000", lignes[8000][1]); NUM("c11_mean", lignes[8000][0])
```
<!--sortie-->
```text
NUM c11_sd500 3.648015907662526
NUM c11_sd8000 0.5910276766725339
NUM c11_mean 40.32813856170351
```

Résultat : l'écart-type de l'estimation passe de 3,65 M€ (N = 500) à 0,59 M€ (N = 8 000) pour une VaR de l'ordre de 40 M€.

### Corrigé 7.12

(a) ΔMNI = Σ écart_i × part_i × Δy : pour +1 point, (−230 × 0,875 − 100 × 0,375) × 0,01 = **−2,39 M€** ; pour −1 point, **+2,39 M€**. (b) Un actif à taux variable de montant x dans la tranche « moins de 3 mois » ajoute x × 0,875 × 0,01 : pour annuler −2,39, x = 2,3875/(0,875 × 0,01) = **272,9 M€**. (Dans la pratique, on utilise un swap de taux plutôt qu'un actif au bilan.) (c) Chocs par tranche : +0,5 point (moins de 3 mois), +1 point (3 à 12 mois) : ΔMNI = −230 × 0,875 × 0,005 − 100 × 0,375 × 0,01 = −1,006 − 0,375 = **−1,38 M€** ; les taux longs (+1,5 point) n'affectent pas la marge de l'année (ils concernent des tranches qui ne se refixent pas dans l'année) mais affecteraient la valeur économique.

```python
ecart = np.array([200 - 430, 150 - 250, 400 - 170, 250 - 100]); part = np.array([0.875, 0.375, 0, 0])
print(round((ecart * part).sum() * 0.01, 4), round(-(ecart * part).sum() * 0.01 / (0.875 * 0.01), 1))
choc = np.array([0.005, 0.01, 0.015, 0.015])
print(round((ecart * part * choc).sum(), 4))
```
<!--sortie-->
```text
-2.3875 272.9
-1.3812
```
