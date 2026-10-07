# Chapitre 11 : ➕ Analytique des opérations et de la chaîne logistique — exercices et applications

> 🧭 Ce chapitre du cahier accompagne le chapitre complémentaire 11 du livre. Les **applications** reprennent, par petites étapes, les études des sections 11.1 à 11.3 sur les données de la boutique ; les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ difficile) demandent des calculs à la main puis du code ; les **corrigés** sont à la fin. Les données sont **simulées** (graines fixes), et tout le chapitre est **autonome** : la cellule suivante charge ce qu'il faut.

```python
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
from scipy import stats
import outils_ch11 as O

liv, rea, stk, prod = O.charger()
print(len(liv), "livraisons (hors retrait en magasin) |", len(rea), "commandes d'achat |", len(stk), "lignes de stock")
```
<!--sortie-->
```text
18047 livraisons (hors retrait en magasin) | 1500 commandes d'achat | 7300 lignes de stock
```

```python hide
def NUM(k, v, nd=None):
    if nd is not None:
        v = f"{v:,.{nd}f}".replace(",", " ")
    elif isinstance(v, (int, np.integer)):
        v = f"{int(v):,}".replace(",", " ")
    print("NUM", k, v)
```

## Applications

### Application 11.1 — Délais, centiles et taux à l'heure (sections 11.1.1 et 11.1.2)

**Objectif.** Mesurer le service rendu par année et voir comment le choix de la promesse change le taux à l'heure.

**Étape 1 — les délais par étape et par année.**

```python
par_an = liv.groupby("annee")[["preparation", "transport", "total"]].mean().round(2)
par_an["a_l_heure_%"] = (1 - liv.groupby("annee")["retard"].mean()).mul(100).round(1)
print(par_an)
```
<!--sortie-->
```text
       preparation  transport  total  a_l_heure_%
annee                                            
2023          1.61       4.12   5.74         72.6
2024          1.62       4.12   5.74         72.9
2025          1.60       4.14   5.74         73.0
```

```python hide
pa = liv.groupby("annee")[["preparation", "transport", "total"]].mean()
th = (1 - liv.groupby("annee")["retard"].mean()) * 100
NUM("a11_th_23", th.loc[2023], 1); NUM("a11_th_25", th.loc[2025], 1); NUM("a11_tot_23", pa.loc[2023, "total"], 2); NUM("a11_tot_25", pa.loc[2025, "total"], 2)
```
<!--sortie-->
```text
NUM a11_th_23 72.6
NUM a11_th_25 73.0
NUM a11_tot_23 5.74
NUM a11_tot_25 5.74
```

Le taux à l'heure est de 72,6 % en 2023 et de 73,0 % en 2025 ; le délai total moyen est de 5,74 jours en 2023 et de 5,74 jours en 2025 : la qualité de service est **stable** sur trois ans, pas en dégradation.

**Étape 2 — le taux à l'heure selon la promesse.** Pour une promesse de $p$ jours, le taux à l'heure est la part des commandes dont le délai total est au plus $p$.

```python
for promesse in (5, 6, 7, 8, 10):
    print("promesse de", promesse, "jours :", round((liv["total"] <= promesse).mean() * 100, 1), "% à l'heure")
```
<!--sortie-->
```text
promesse de 5 jours : 47.0 % à l'heure
promesse de 6 jours : 72.8 % à l'heure
promesse de 7 jours : 88.9 % à l'heure
promesse de 8 jours : 96.1 % à l'heure
promesse de 10 jours : 99.7 % à l'heure
```

**À vous.** Quel délai promettre pour que 95 % des commandes arrivent à l'heure ? (Piste : le 95e centile du délai total.) Quelle est la conséquence commerciale d'une promesse plus longue ?

**Piste.** Le 95e centile du délai total est 8 jours : on promet 8 jours pour tenir 95 % de livraisons à l'heure. Plus long, la promesse est plus fiable mais moins attractive ; plus court, elle séduit mais se rompt. C'est un choix commercial éclairé par la distribution, pas un calcul.

### Application 11.2 — Transporteurs, mode et décembre (sections 11.1.3 et 11.1.4)

**Objectif.** Comparer les transporteurs avec des intervalles, puis **standardiser** pour neutraliser décembre.

**Étape 1 — taux de retard et intervalles de Wilson.**

```python
for nom, g in liv.groupby("transporteur"):
    p, lo, hi = O.wilson(g["retard"].sum(), len(g))
    print(nom, len(g), round(p * 100, 1), round(lo * 100, 1), round(hi * 100, 1))
```
<!--sortie-->
```text
Transporteur A 8107 16.4 15.6 17.2
Transporteur B 6444 27.3 26.2 28.4
Transporteur C 3496 51.9 50.3 53.6
```

**Étape 2 — standardisation directe.** On calcule le taux de chaque transporteur dans chaque mois, puis on le pondère par la **répartition mensuelle de l'ensemble des envois** : c'est le taux qu'aurait chaque transporteur si tous avaient le même calendrier.

```python
poids = liv["mois"].value_counts(normalize=True).sort_index()
taux = liv.pivot_table(index="mois", columns="transporteur", values="retard", aggfunc="mean")
standardise = (taux.mul(poids, axis=0)).sum() * 100
brut = liv.groupby("transporteur")["retard"].mean() * 100
print(pd.DataFrame({"brut %": brut.round(1), "standardisé %": standardise.round(1)}))
```
<!--sortie-->
```text
                brut %  standardisé %
transporteur                         
Transporteur A    16.4           16.3
Transporteur B    27.3           27.5
Transporteur C    51.9           51.8
```

```python hide
for t, k in (("Transporteur A", "a"), ("Transporteur B", "b"), ("Transporteur C", "c")):
    NUM(f"a12_brut_{k}", brut[t], 1); NUM(f"a12_std_{k}", standardise[t], 1)
NUM("a12_ecart_max", (brut - standardise).abs().max(), 1)
pm = liv.pivot_table(index="mode_livraison", columns="transporteur", values="retard", aggfunc="mean") * 100
for t, k in (("Transporteur A", "a"), ("Transporteur B", "b"), ("Transporteur C", "c")):
    NUM(f"a12_dom_{k}", pm.loc["Domicile", t], 1); NUM(f"a12_rel_{k}", pm.loc["Point relais", t], 1)
```
<!--sortie-->
```text
NUM a12_brut_a 16.4
NUM a12_std_a 16.3
NUM a12_brut_b 27.3
NUM a12_std_b 27.5
NUM a12_brut_c 51.9
NUM a12_std_c 51.8
NUM a12_ecart_max 0.2
NUM a12_dom_a 11.4
NUM a12_rel_a 23.5
NUM a12_dom_b 20.2
NUM a12_rel_b 38.0
NUM a12_dom_c 42.0
NUM a12_rel_c 66.9
```

Les taux bruts (16,4 %, 27,3 %, 51,9 %) et standardisés (16,3 %, 27,5 %, 51,8 %) diffèrent d'au plus 0,2 point : le calendrier de chaque transporteur est le même, donc la standardisation ne change rien. Elle sera décisive quand les calendriers diffèrent (exercice 11.4).

**À vous.** Refaites la comparaison selon le **mode de livraison** (domicile ou point relais) au lieu du mois. Le classement des transporteurs tient-il ?

**Piste.** Pour le vérifier : `liv.pivot_table(index="mode_livraison", columns="transporteur", values="retard", aggfunc="mean")`. Les taux sont, à domicile, de 11,4 % (A), 20,2 % (B) et 42,0 % (C) ; en point relais, de 23,5 %, 38,0 % et 66,9 % : le classement tient dans les deux modes, car la répartition entre les modes est la même pour tous les transporteurs.

### Application 11.3 — Colis abîmés, retours et coût (section 11.1.5)

**Objectif.** Chiffrer la casse et tester si le retard fait renvoyer.

**Étape 1 — la casse par transporteur.**

```python
ab = liv.groupby("transporteur")["colis_abime"].agg(["sum", "count"])
ab["taux_%"] = (ab["sum"] / ab["count"] * 100).round(2)
print(ab)
```
<!--sortie-->
```text
                sum  count  taux_%
transporteur                      
Transporteur A   72   8107    0.89
Transporteur B   93   6444    1.44
Transporteur C  147   3496    4.20
```

**Étape 2 — le retard fait-il renvoyer ?** On relie chaque livraison à un éventuel retour et on teste l'égalité des taux avec un test du khi-deux.

```python
ret = pd.read_csv("donnees/retours.csv"); lig = pd.read_csv("donnees/lignes_commande.csv")
retourne = ret.merge(lig[["id_ligne", "id_commande"]], on="id_ligne")["id_commande"].unique()
liv["retour"] = liv["id_commande"].isin(retourne).astype(int)
tab = pd.crosstab(liv["retard"], liv["retour"])
chi2, p, _, _ = stats.chi2_contingency(tab, correction=False)
print(tab.assign(taux=(tab[1] / tab.sum(axis=1) * 100).round(1)))
print("p-valeur du khi-deux :", round(p, 3))
```
<!--sortie-->
```text
retour      0     1  taux
retard                   
0       10757  2387  18.2
1        4022   881  18.0
p-valeur du khi-deux : 0.766
```

```python hide
NUM("a13_p", p, 2); NUM("a13_t0", tab.loc[0, 1] / tab.loc[0].sum() * 100, 1); NUM("a13_t1", tab.loc[1, 1] / tab.loc[1].sum() * 100, 1)
```
<!--sortie-->
```text
NUM a13_p 0.77
NUM a13_t0 18.2
NUM a13_t1 18.0
```

Le taux de retour est de 18,2 % après une livraison à l'heure et de 18,0 % après une livraison tardive ; la p-valeur de 0,77 est grande : **aucune différence détectable**.

**À vous.** Estimez le coût annuel de la casse du transporteur C si l'on suppose un coût de 100 € par colis abîmé. Que valent 100 € si le colis contenait un produit de marge moyenne 10 € ?

**Piste.** Environ 49 colis abîmés par an pour C (147 en trois ans), soit 4 900 € de remplacement à 100 € le colis ; en marge, la perte est de 10 € par colis si le client est remboursé et le produit revendu, beaucoup plus s'il faut le remplacer : le coût dépend de la politique, ce qui doit être précisé avec la gérante.

### Application 11.4 — Ruptures et point de commande (sections 11.2.2 et 11.2.3)

**Objectif.** Calculer la couverture, les ruptures, et le point de commande pour trois niveaux de service.

**Étape 1 — couverture et ruptures par produit.**

```python
pp = stk.groupby("id_produit").agg(d=("demande", "mean"), s=("demande", "std"), stock=("stock_fin_jour", "mean"), rupt=("rupture", "mean"))
pp["couverture"] = pp["stock"] / pp["d"]
print(pp[["d", "couverture", "rupt"]].describe().loc[["mean", "min", "max"]].round(2))
```
<!--sortie-->
```text
         d  couverture  rupt
mean  1.54       16.11  0.07
min   1.28       15.14  0.05
max   1.91       17.29  0.10
```

**Étape 2 — le délai reconstitué et le point de commande.**

```python
L = O.delais_reconstitues(stk)
Lm, Ls = L.mean(), L.std(ddof=1)
resultats = {}
for niveau, z in (("90 %", 1.2816), ("95 %", 1.6449), ("99 %", 2.3263)):
    R = np.ceil(pp["d"] * Lm + z * np.sqrt(Lm * pp["s"] ** 2 + pp["d"] ** 2 * Ls ** 2))
    resultats[niveau] = float(R.mean().round(1))
print(round(Lm, 1), round(Ls, 1), resultats, "| actuel :", round(float(stk.groupby("id_produit")["point_de_commande"].first().mean()), 1))
```
<!--sortie-->
```text
11.1 3.7 {'90 %': 27.8, '95 %': 30.6, '99 %': 36.1} | actuel : 13.3
```

```python hide
NUM("a14_Lm", Lm, 1); NUM("a14_Ls", Ls, 1); NUM("a14_r90", resultats["90 %"], 1); NUM("a14_r95", resultats["95 %"], 1); NUM("a14_r99", resultats["99 %"], 1)
NUM("a14_act", stk.groupby("id_produit")["point_de_commande"].first().mean(), 1); NUM("a14_diff", resultats["99 %"] - resultats["95 %"], 1)
```
<!--sortie-->
```text
NUM a14_Lm 11.1
NUM a14_Ls 3.7
NUM a14_r90 27.8
NUM a14_r95 30.6
NUM a14_r99 36.1
NUM a14_act 13.3
NUM a14_diff 5.5
```

Le délai moyen est de 11,1 jours (écart-type de 3,7). Le point de commande moyen serait de **27,8**, **30,6** et **36,1** unités pour 90, 95 et 99 % de service, contre **13,3** actuellement : la règle actuelle est **en dessous même du niveau à 90 %**.

**À vous.** Le passage de 95 % à 99 % ajoute combien d'unités de stock de sécurité par produit ? Est-ce proportionnel au gain de service ?

**Piste.** Environ 5,5 unités de plus par produit (36,1 contre 30,6) pour passer de 95 à 99 %, alors que l'on gagne quatre points de service : le **dernier point coûte de plus en plus cher**, ce que la loi normale traduit par l'allongement des queues.

### Application 11.5 — Rejeu de la politique et quantité économique (sections 11.2.4 et 11.2.5)

**Objectif.** Rejouer deux niveaux de service et mesurer la sensibilité de la quantité économique à l'hypothèse de coût.

**Étape 1 — le rejeu.** On compare la règle actuelle et le point de commande à 95 % (`O.rejouer` rejoue la demande de 2025 avec des délais tirés dans les délais observés).

```python
actuel_rop = stk.groupby("id_produit")["point_de_commande"].first().to_dict()
R95 = np.ceil(pp["d"] * Lm + 1.6449 * np.sqrt(Lm * pp["s"] ** 2 + pp["d"] ** 2 * Ls ** 2)).astype(int).to_dict()
Q = {p: int(pp.loc[p, "d"] * 30) + 5 for p in pp.index}
for nom, regle in (("actuelle", actuel_rop), ("95 %", R95)):
    r = O.rejouer(stk, regle, Q, L, n_rep=10)
    print(nom, "| ruptures :", round(r[0] * 100, 1), "% | stock :", round(r[1], 1), "jours | commandes/an :", round(r[2], 1))
```
<!--sortie-->
```text
actuelle | ruptures : 7.1 % | stock : 16.1 jours | commandes/an : 9.9
95 % | ruptures : 1.4 % | stock : 26.1 jours | commandes/an : 11.0
```

```python hide
ra = O.rejouer(stk, actuel_rop, Q, L, n_rep=10); rb = O.rejouer(stk, R95, Q, L, n_rep=10)
NUM("a15_rupt_a", ra[0] * 100, 1); NUM("a15_rupt_b", rb[0] * 100, 1); NUM("a15_stock_a", ra[1], 1); NUM("a15_stock_b", rb[1], 1)
```
<!--sortie-->
```text
NUM a15_rupt_a 7.1
NUM a15_rupt_b 1.4
NUM a15_stock_a 16.1
NUM a15_stock_b 26.1
```

La règle actuelle donne 7,1 % de ruptures pour 16,1 jours de stock ; la règle à 95 % 1,4 % pour 26,1 jours.

**Étape 2 — sensibilité de la quantité économique au coût de commande.**

```python
cout_u = prod.set_index("id_produit")["cout_achat"].loc[pp.index]
D = pp["d"] * 365
for S in (10, 25, 50):
    qeco = np.sqrt(2 * D * S / (0.20 * cout_u))
    cout = (D / qeco * S + qeco / 2 * 0.20 * cout_u).sum()
    print("S =", S, "€ | quantité économique moyenne :", round(qeco.mean()), "unités | coût annuel :", round(cout), "€")
```
<!--sortie-->
```text
S = 10 € | quantité économique moyenne : 75 unités | coût annuel : 3574 €
S = 25 € | quantité économique moyenne : 119 unités | coût annuel : 5651 €
S = 50 € | quantité économique moyenne : 168 unités | coût annuel : 7992 €
```

**À vous.** Quand le coût d'une commande est multiplié par 5 (de 10 à 50 €), de combien la quantité économique est-elle multipliée ? (Piste : racine carrée.)

**Piste.** Par $\sqrt{5}\approx 2{,}2$ : la quantité économique varie comme la **racine** du coût de commande, ce qui la rend peu sensible à une erreur sur $S$.

### Application 11.6 — La carte de performance des fournisseurs (section 11.3)

**Objectif.** Construire la carte avec des intervalles par **bootstrap** (sans formule) et tester la stabilité du classement.

**Étape 1 — intervalle bootstrap de l'écart moyen.** On rééchantillonne les commandes de chaque fournisseur avec remise.

```python
rng = np.random.default_rng(3)
carte = {}
for f, g in rea.groupby("fournisseur"):
    ec = g["ecart_j"].values
    moyennes = [rng.choice(ec, len(ec)).mean() for _ in range(2000)]
    carte[f[-1]] = (ec.mean(), np.percentile(moyennes, 2.5), np.percentile(moyennes, 97.5))
print(pd.DataFrame(carte, index=["moyenne", "bas", "haut"]).T.round(2))
```
<!--sortie-->
```text
   moyenne   bas  haut
A     0.67  0.25  1.16
B     1.06  0.52  1.64
C     1.08  0.64  1.60
D     1.06  0.55  1.60
E     3.89  3.20  4.59
F     1.29  0.73  1.85
G     0.48  0.09  0.95
H     0.92  0.49  1.36
```

**Étape 2 — probabilité d'être le meilleur.** À chaque rééchantillonnage, on classe les fournisseurs ; on compte la fréquence où chacun est premier (écart moyen le plus faible).

```python
fr = {f[-1]: g["ecart_j"].values for f, g in rea.groupby("fournisseur")}
premiers = pd.Series([min(fr, key=lambda k: rng.choice(fr[k], len(fr[k])).mean()) for _ in range(2000)]).value_counts(normalize=True)
print(premiers.round(2).to_dict())
```
<!--sortie-->
```text
{'G': 0.65, 'A': 0.25, 'H': 0.04, 'B': 0.02, 'D': 0.02, 'C': 0.01, 'F': 0.0}
```

```python hide
NUM("a16_g", premiers.get("G", 0) * 100, 0); NUM("a16_a", premiers.get("A", 0) * 100, 0); NUM("a16_e", premiers.get("E", 0) * 100, 0)
fs = {f[-1]: g["taux_service"].values for f, g in rea.groupby("fournisseur")}
psv = pd.Series([max(fs, key=lambda k: rng.choice(fs[k], len(fs[k])).mean()) for _ in range(2000)]).value_counts(normalize=True)
NUM("a16_sv_max", psv.max() * 100, 0); NUM("a16_sv_e", psv.get("E", 0) * 100, 0); NUM("a16_sv_n", len(psv))
```
<!--sortie-->
```text
NUM a16_g 65
NUM a16_a 25
NUM a16_e 0
NUM a16_sv_max 50
NUM a16_sv_e 0
NUM a16_sv_n 7
```

Le fournisseur G est premier dans 65 % des rééchantillonnages, A dans 25 %, et E dans 0 % : **personne n'est « le meilleur » avec certitude**, sauf que E ne l'est jamais.

**À vous.** Même question avec le taux de service au lieu de l'écart de délai.

**Piste.** Avec le taux de service, la première place est répartie entre 7 fournisseurs, le plus fréquent n'étant premier que dans 50 % des rééchantillonnages (leurs taux de service ne diffèrent que de quelques dixièmes de point), et E est premier dans 0 % des cas : même conclusion, aucun « meilleur » certain parmi les sept ordinaires.

## Exercices

### Exercice 11.1 ⭐ — Le taux à l'heure selon la promesse (section 11.1.2)

Sur le fichier des livraisons, calculez le taux de livraison à l'heure si l'on promettait 7 jours, puis 8 jours. Comparez au taux observé pour 6 jours.

### Exercice 11.2 ⭐⭐ — Moyenne, médiane et 90e centile (section 11.1.2)

Neuf livraisons ont pris 4, 5, 5, 5, 6, 6, 6, 7 et 14 jours. Calculez à la main la moyenne, la médiane et le 90e centile (par interpolation linéaire), puis vérifiez avec NumPy. Lequel inscririez-vous dans un contrat de service ?

### Exercice 11.3 ⭐ — Un intervalle de Wilson à la main (section 11.1.3)

Un transporteur est en retard sur 50 envois sur 200. Calculez à la main l'intervalle de Wilson à 95 % de son taux de retard, puis vérifiez avec `O.wilson`.

### Exercice 11.4 ⭐⭐ — Un paradoxe de Simpson de transporteurs (section 11.1.4)

Le transporteur X assure 100 envois en décembre (80 en retard) et 400 les autres mois (100 en retard). Le transporteur Y assure 400 envois en décembre (300 en retard) et 100 les autres mois (20 en retard). Calculez les taux par strate et les taux globaux. Quel transporteur est meilleur ? Standardisez avec la répartition commune (500 envois en décembre, 500 les autres mois) pour conclure.

### Exercice 11.5 ⭐⭐ — Basculer les envois du transporteur C (section 11.1.5)

Si l'on confiait tous les envois du transporteur C au transporteur A, combien de colis abîmés et combien de livraisons tardives éviterait-on sur trois ans (en supposant que les taux de A ne changent pas) ? Quelle limite voyez-vous à ce calcul ?

### Exercice 11.6 ⭐ — Couverture et rotation à la main (section 11.2.1)

Un produit se vend 2 unités par jour et le stock moyen est de 36 unités. Calculez la couverture et la rotation. Que deviennent-elles si la demande double sans que le stock change ?

### Exercice 11.7 ⭐⭐ — Un point de commande à la main (section 11.2.3)

Un produit a une demande journalière de moyenne 2 et d'écart-type 1, un délai de moyenne 9 jours et d'écart-type 2 jours. Calculez le point de commande pour 90 % de service ($z=1{,}28$). Que devient-il si l'écart-type du délai est divisé par deux ?

### Exercice 11.8 ⭐⭐ — La quantité économique et l'erreur sur le coût (section 11.2.5)

Un produit se vend 1 200 unités par an ; une commande coûte 30 €, la détention 3 € par unité et par an. Calculez la quantité économique. Si le coût de commande est en réalité de 60 €, de combien la quantité optimale change-t-elle, et de combien augmente le coût total quand on garde la quantité calculée avec 30 € ?

### Exercice 11.9 ⭐⭐ — Deux fournisseurs, est-ce différent ? (section 11.3)

Le fournisseur X est en retard sur 30 de ses 100 commandes, le fournisseur Y sur 20 de ses 100. Les deux taux sont-ils significativement différents ? Combien de commandes par fournisseur faudrait-il pour détecter cet écart de 10 points avec une puissance de 80 % ?

### Exercice 11.10 ⭐⭐⭐ — Une note multicritère et sa sensibilité (section 11.3)

Construisez pour chaque fournisseur une note de 0 à 100 à partir du taux de retard de 3 jours ou plus, du taux de service et de l'écart-type du délai, avec les pondérations de votre choix (justifiez-les). Faites varier les pondérations de ±20 points : quels fournisseurs changent de rang ? Que recommandez-vous à la gérante ?

## Corrigés

### Corrigé 11.1

```python
for promesse in (6, 7, 8):
    print("promesse de", promesse, "jours :", round((liv["total"] <= promesse).mean() * 100, 1), "% à l'heure")
```
<!--sortie-->
```text
promesse de 6 jours : 72.8 % à l'heure
promesse de 7 jours : 88.9 % à l'heure
promesse de 8 jours : 96.1 % à l'heure
```

```python hide
for p in (6, 7, 8):
    NUM(f"c1_{p}", (liv["total"] <= p).mean() * 100, 1)
NUM("c1_gain1", (liv["total"] <= 7).mean() * 100 - (liv["total"] <= 6).mean() * 100, 1); NUM("c1_gain2", (liv["total"] <= 8).mean() * 100 - (liv["total"] <= 7).mean() * 100, 1)
```
<!--sortie-->
```text
NUM c1_6 72.8
NUM c1_7 88.9
NUM c1_8 96.1
NUM c1_gain1 16.0
NUM c1_gain2 7.2
```

Pour 6 jours, **72,8 %** ; pour 7 jours, **88,9 %** ; pour 8 jours, **96,1 %**. Allonger la promesse d'un jour ajoute 16,0 points de service, un deuxième jour n'en ajoute plus que 7,2 : la distribution est asymétrique et le gain **décroît**.

### Corrigé 11.2

À la main : somme $=4+5+5+5+6+6+6+7+14=58$, moyenne $58/9\approx6{,}44$ ; médiane (5e valeur ordonnée) $=6$ ; position du 90e centile $=0{,}9\times(9-1)=7{,}2$ entre la 8e valeur (7) et la 9e (14) : $7+0{,}2\times7=8{,}4$.

```python
d = np.array([4, 5, 5, 5, 6, 6, 6, 7, 14])
print(round(d.mean(), 2), np.median(d), round(np.percentile(d, 90), 1))
```
<!--sortie-->
```text
6.44 6.0 8.4
```

On inscrit dans un contrat un **centile** (par exemple le 90e : 8,4 jours, soit « neuf commandes sur dix en 9 jours ou moins »), pas la moyenne, que la livraison de 14 jours tire vers le haut.

### Corrigé 11.3

À la main, avec $p=0{,}25$, $n=200$, $z=1{,}96$ : centre $=\dfrac{0{,}25+1{,}96^2/400}{1+1{,}96^2/200}=\dfrac{0{,}25+0{,}0096}{1{,}0192}\approx0{,}2547$ ; demi-largeur $=\dfrac{1{,}96\sqrt{0{,}25\times0{,}75/200+1{,}96^2/(4\times200^2)}}{1{,}0192}\approx0{,}0596$. L'intervalle est donc d'environ 19,5 % à 31,4 %.

```python
p, lo, hi = O.wilson(50, 200)
print(round(p * 100, 1), round(lo * 100, 1), round(hi * 100, 1))
```
<!--sortie-->
```text
25.0 19.5 31.4
```

### Corrigé 11.4

```python
x = {"déc": (100, 80), "autres": (400, 100)}
y = {"déc": (400, 300), "autres": (100, 20)}
for nom, t in (("X", x), ("Y", y)):
    n = sum(v[0] for v in t.values()); k = sum(v[1] for v in t.values())
    print(nom, {s: round(v[1] / v[0] * 100) for s, v in t.items()}, "global :", round(k / n * 100), "% | standardisé :", round((0.5 * t["déc"][1] / t["déc"][0] + 0.5 * t["autres"][1] / t["autres"][0]) * 100, 1), "%")
```
<!--sortie-->
```text
X {'déc': 80, 'autres': 25} global : 36 % | standardisé : 52.5 %
Y {'déc': 75, 'autres': 20} global : 64 % | standardisé : 47.5 %
```

```python hide
tx = lambda t: (sum(v[1] for v in t.values()) / sum(v[0] for v in t.values()) * 100, (0.5 * t["déc"][1] / t["déc"][0] + 0.5 * t["autres"][1] / t["autres"][0]) * 100)
NUM("c4_gx", tx(x)[0], 0); NUM("c4_gy", tx(y)[0], 0); NUM("c4_sx", tx(x)[1], 1); NUM("c4_sy", tx(y)[1], 1)
```
<!--sortie-->
```text
NUM c4_gx 36
NUM c4_gy 64
NUM c4_sx 52.5
NUM c4_sy 47.5
```

Par strate, X est **moins bon** que Y (80 % contre 75 % en décembre, 25 % contre 20 % ailleurs). Pourtant, globalement, X paraît **bien meilleur** (36 % contre 64 %) : c'est un paradoxe de Simpson, parce que Y a assuré surtout les envois de décembre, mois difficile. Standardisés sur la même répartition, X vaut 52,5 % et Y 47,5 % : **Y est le meilleur transporteur**, et le classement global était trompeur.

### Corrigé 11.5

```python
n_c = int((liv["transporteur"] == "Transporteur C").sum())
a = liv[liv["transporteur"] == "Transporteur A"]; c = liv[liv["transporteur"] == "Transporteur C"]
abimes = c["colis_abime"].sum() - n_c * a["colis_abime"].mean()
tardifs = c["retard"].sum() - n_c * a["retard"].mean()
print(n_c, round(abimes), round(tardifs))
```
<!--sortie-->
```text
3496 116 1243
```

```python hide
NUM("c5_n", n_c); NUM("c5_ab", abimes, 0); NUM("c5_tard", tardifs, 0)
```
<!--sortie-->
```text
NUM c5_n 3 496
NUM c5_ab 116
NUM c5_tard 1 243
```

Sur 3 496 envois du transporteur C, on éviterait environ **116 colis abîmés** et **1 243 livraisons tardives**. Limites : le transporteur A **n'a peut-être pas la capacité** d'absorber ce volume (sa performance pourrait se dégrader) ; ses taux sont mesurés sur ses envois actuels ; et le tarif de A peut être plus élevé : il faudrait comparer le **coût complet** (transport, casse, service).

### Corrigé 11.6

Couverture $=36/2=18$ jours ; rotation $=365/18\approx20{,}3$ fois par an. Si la demande double sans que le stock change, la couverture tombe à $36/4=9$ jours et la rotation monte à environ 40,6 : le stock est « plus efficace », mais **deux fois plus exposé à la rupture**.

### Corrigé 11.7

À la main : $\sigma_{DL}=\sqrt{9\times1^2+2^2\times2^2}=\sqrt{9+16}=5$ ; stock de sécurité $=1{,}28\times5=6{,}4$ ; demande pendant le délai $=2\times9=18$ ; $R=18+6{,}4=24{,}4$, soit 25 unités. Avec $\sigma_L=1$ : $\sigma_{DL}=\sqrt{9+4}\approx3{,}61$, stock de sécurité $\approx4{,}6$, $R\approx22{,}6$.

```python
for sL in (2, 1):
    s = np.sqrt(9 * 1 + 2 ** 2 * sL ** 2)
    print(sL, round(s, 2), round(1.28 * s, 1), round(18 + 1.28 * s, 1))
```
<!--sortie-->
```text
2 5.0 6.4 24.4
1 3.61 4.6 22.6
```

Diviser par deux l'incertitude sur le **délai** réduit le stock de sécurité de $6{,}4$ à $4{,}6$, soit environ 28 % : la fiabilité du fournisseur se paie en stock.

### Corrigé 11.8

À la main : $Q^{*}=\sqrt{2\times1200\times30/3}=\sqrt{24\,000}\approx155$. Avec $S=60$ : $Q^{*}=\sqrt{2\times1200\times60/3}=\sqrt{48\,000}\approx219$, soit $\sqrt2$ fois plus. Garder $Q=155$ alors que l'optimum est 219 : coût $=\frac{1200}{155}\times60+\frac{155}{2}\times3\approx 464{,}5+232{,}5=697$ € contre $\sqrt{2\times1200\times60\times3}\approx657$ € à l'optimum : **6 % de plus** pour une erreur de 100 % sur le coût de commande.

```python
f = lambda q, S: 1200 / q * S + q / 2 * 3
print(round(np.sqrt(2 * 1200 * 30 / 3), 1), round(np.sqrt(2 * 1200 * 60 / 3), 1), round(f(155, 60)), round(f(np.sqrt(2 * 1200 * 60 / 3), 60)))
```
<!--sortie-->
```text
154.9 219.1 697 657
```

### Corrigé 11.9

```python
from statsmodels.stats.proportion import proportions_ztest, proportion_confint
from statsmodels.stats.power import NormalIndPower
from statsmodels.stats.proportion import proportion_effectsize
z, pv = proportions_ztest([30, 20], [100, 100])
taille = NormalIndPower().solve_power(proportion_effectsize(0.30, 0.20), power=0.8, alpha=0.05)
print(round(z, 2), round(pv, 3), [round(v, 3) for v in proportion_confint(30, 100, method="wilson")], [round(v, 3) for v in proportion_confint(20, 100, method="wilson")], round(taille))
```
<!--sortie-->
```text
1.63 0.102 [0.219, 0.396] [0.133, 0.289] 292
```

```python hide
NUM("c9_z", z, 2); NUM("c9_p", pv, 3); NUM("c9_n", taille, 0)
```
<!--sortie-->
```text
NUM c9_z 1.63
NUM c9_p 0.102
NUM c9_n 292
```

La statistique vaut 1,63 et la p-valeur 0,102 : **non significatif** à 5 %, et les deux intervalles de Wilson se chevauchent largement. Il faudrait environ **292 commandes par fournisseur** pour détecter un écart de 10 points avec 80 % de puissance : le triple de ce que l'on a. Moralité : avec cent commandes chacun, on ne départage pas deux fournisseurs qui diffèrent de dix points.

### Corrigé 11.10

```python
reg = rea.groupby("fournisseur")["delai_reel_j"].std()
rea["retard_3j"] = (rea["ecart_j"] >= 3).astype(int)
crit = pd.DataFrame({"retard": rea.groupby("fournisseur")["retard_3j"].mean(), "service": rea.groupby("fournisseur")["taux_service"].mean(), "reg": reg})
norm = pd.DataFrame({"retard": 1 - (crit["retard"] - crit["retard"].min()) / (crit["retard"].max() - crit["retard"].min()),
                     "service": (crit["service"] - crit["service"].min()) / (crit["service"].max() - crit["service"].min()),
                     "reg": 1 - (crit["reg"] - crit["reg"].min()) / (crit["reg"].max() - crit["reg"].min())})
rangs = {}
for w in ((0.4, 0.4, 0.2), (0.6, 0.2, 0.2), (0.2, 0.6, 0.2), (0.2, 0.2, 0.6)):
    rangs[str(w)] = (norm @ pd.Series(w, index=norm.columns) * 100).round(0).rank(ascending=False).astype(int)
print(pd.DataFrame(rangs).T.rename(columns=lambda f: f[-1]))
```
<!--sortie-->
```text
fournisseur      A  B  C  D  E  F  G  H
(0.4, 0.4, 0.2)  3  5  4  7  8  5  1  2
(0.6, 0.2, 0.2)  4  4  4  7  8  6  1  2
(0.2, 0.6, 0.2)  3  6  5  7  8  4  1  2
(0.2, 0.2, 0.6)  3  6  4  7  8  4  1  2
```

```python hide
tab = pd.DataFrame(rangs)
NUM("c10_e_min", int(tab.loc["Fournisseur E"].min())); NUM("c10_e_max", int(tab.loc["Fournisseur E"].max()))
NUM("c10_var_max", int((tab.max(axis=1) - tab.min(axis=1)).drop("Fournisseur E").max()))
```
<!--sortie-->
```text
NUM c10_e_min 8
NUM c10_e_max 8
NUM c10_var_max 2
```

Le fournisseur E est au rang 8 quelles que soient les pondérations : il est **toujours dernier**. Pour les autres, un même fournisseur peut changer de **2 rangs** selon les pondérations. Recommandation : **traiter E à part** (plan de redressement ou remplacement ; en attendant, un stock de sécurité adapté, section 11.2.3), et ne pas inventer de classement entre les sept autres, dont les écarts sont dans le bruit ; si la gérante veut une note, la lui donner avec les pondérations **qu'elle** choisit, et publier les intervalles.
