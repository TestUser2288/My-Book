# Chapitre 13 : ➕ Analyse de sensibilité, simulations « et si » et scénarios — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 13 du livre (complémentaire). Il comprend **six applications guidées** (le modèle de résultat de la boutique, de sa construction aux scénarios) puis **dix exercices** ⭐ à ⭐⭐⭐, tous corrigés. Les données sont **simulées** (la TVA est fictive, à 20 %). Les applications utilisent les fonctions de `build/outils_ch13.py` (`calibrer`, `resultat`, `tirages`…) : lisez-les, elles tiennent en une page.

```python
import sys, os, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
from scipy.optimize import brentq
import outils_ch13 as O

T = O.charger()                    # comptes mensuels, commandes, sessions, retours, livraisons…
b = O.calibrer(T)                  # paramètres de base de 2025
R = lambda **k: O.resultat(b, **k)   # le modèle : résultat après retours, en €, selon des variations de paramètres
base = R()
print("résultat de référence (2025, après retours) :", round(base), "€")
```
<!--sortie-->
```text
résultat de référence (2025, après retours) : 8501 €
```

## Applications

### Application 13.1 — Construire et vérifier le modèle (sections 13.1.1 et 13.1.2 du livre)

**Objectif.** Refaire à la main une version simplifiée du modèle, la comparer aux comptes, puis ajouter les retours.

**Étape 1 — Les paramètres de base.** On part des chiffres de 2025 : sessions, conversions, paniers, coût d'achat, personnel.

```python
for k in ["sessions_pay", "sessions_aut", "conv_pay", "conv_aut", "panier_site", "n_bou", "panier_bou", "n_res", "panier_res", "cout_unitaire", "pers_fixe", "pers_var", "cout_par_colis"]:
    print(f"{k:16s}", round(b[k], 4) if b[k] < 10 else round(b[k], 1))
```
<!--sortie-->
```text
sessions_pay     33026
sessions_aut     93996
conv_pay         0.0262
conv_aut         0.0555
panier_site      101.6
n_bou            5442
panier_bou       103.1
n_res            1426
panier_res       102.4
cout_unitaire    19.1
pers_fixe        92603.8
pers_var         0.0439
cout_par_colis   4.2001
```

**Étape 2 — Le chiffre d'affaires par la chaîne.** Commandes du site = sessions × conversion ; CA TTC = Σ commandes × panier. On le compare au CA des commandes de 2025.

```python
n_site = b["sessions_pay"] * b["conv_pay"] + b["sessions_aut"] * b["conv_aut"]
ca_ttc = n_site * b["panier_site"] + b["n_bou"] * b["panier_bou"] + b["n_res"] * b["panier_res"]
print("commandes du site :", round(n_site), "(observé :", b["n_site"], ")")
print("CA TTC modèle :", round(ca_ttc), "| CA TTC mesuré :", round(b["ca_ttc"]))
```
<!--sortie-->
```text
commandes du site : 6078 (observé : 6078 )
CA TTC modèle : 1324764 | CA TTC mesuré : 1324764
```

**Étape 3 — Du chiffre d'affaires au résultat, sans retours.** Complétez la formule avec les achats (articles × coût unitaire), le personnel, la livraison, les frais bancaires, le marketing et les charges fixes, puis comparez au résultat des comptes.

```python
d = O.resultat(b, detail=True)
print("résultat avant retours (modèle) :", round(d["resultat_avant_retours"]), "| comptes :", round(b["resultat_comptes"]))
stock = T["cr"].loc[T["cr"]["mois"].str.startswith("2025"), "variation_stock"].sum()
print("écart :", round(d["resultat_avant_retours"] - b["resultat_comptes"]), "| variation de stock :", round(stock))
```
<!--sortie-->
```text
résultat avant retours (modèle) : 41769 | comptes : 39879
écart : 1890 | variation de stock : -1888
```

**Étape 4 — Ajouter les retours.** Le coût net est le remboursement hors taxe moins le coût d'achat récupéré sur les articles remis en vente (85 %).

```python
print("remboursements TTC (part du CA) :", round(b["taux_retour_ca"] * 100, 2), "%")
print("coût net des retours :", round(d["cout_retours"]), "| résultat après retours :", round(d["resultat"]))
```
<!--sortie-->
```text
remboursements TTC (part du CA) : 6.38 %
coût net des retours : 33268 | résultat après retours : 8501
```

**À vous.** Changez la part d'articles remis en vente (`O.PART_REMISE_EN_STOCK`, 85 % par défaut) à 60 %, puis à 100 %. Quel est le résultat de référence dans chaque cas ? Que vous apprend cet écart sur la fiabilité d'un modèle qui dépend d'une hypothèse non mesurée ?

### Application 13.2 — Tornade et seuil d'élasticité (sections 13.1.3 et 13.1.4 du livre)

**Objectif.** Classer les paramètres par leur effet, d'abord avec des plages uniformes, puis avec des plages réalistes ; trouver l'élasticité-seuil.

**Étape 1 — La tornade.**

```python
tor, _ = O.tornade(b, O.PLAGES_UNIFORMES)
print(tor[["libelle", "effet_bas", "effet_haut"]].round(0).to_string(index=False))
```
<!--sortie-->
```text
                               libelle  effet_bas  effet_haut
                         Prix de vente   -33176.0     29260.0
             Coût d'achat des produits    32391.0    -32391.0
                 Articles par commande   -15868.0     15868.0
          Fréquentation de la boutique   -13639.0     13639.0
             Trafic du site (sessions)   -12038.0     12038.0
            Taux de conversion du site   -12038.0     12038.0
               Taux de retour (points)    10435.0    -10435.0
Charges fixes (loyer, personnel fixe…)    10210.0    -10210.0
           Coût de livraison par colis     6304.0     -6304.0
            Coût d'une session payante     4278.0     -2852.0
```

**Étape 2 — Les mêmes paramètres, avec des plages tirées des données.**

```python
tor2, _ = O.tornade(b, O.PLAGES_DONNEES)
print(tor2[["libelle", "plage", "amplitude"]].round(3).to_string(index=False))
print("classement uniforme :", list(tor["parametre"][:4]), "| classement réaliste :", list(tor2["parametre"][:4]))
```
<!--sortie-->
```text
                               libelle  plage  amplitude
                         Prix de vente  0.050  33176.337
             Coût d'achat des produits  0.030  19434.885
             Trafic du site (sessions)  0.060   7222.519
                 Articles par commande  0.021   6664.568
          Fréquentation de la boutique  0.040   5455.562
            Taux de conversion du site  0.044   5296.514
               Taux de retour (points)  0.400   2087.042
Charges fixes (loyer, personnel fixe…)  0.010   2041.988
            Coût d'une session payante  0.100   1901.288
           Coût de livraison par colis  0.050   1575.876
classement uniforme : ['prix', 'cout_achat', 'panier', 'frequentation'] | classement réaliste : ['prix', 'cout_achat', 'trafic', 'panier']
```

**Étape 3 — Combien vaut un point ?** L'effet de +1 % de chaque paramètre, en euros.

```python
un = {k: round(R(**{k: 0.01}) - base) for k in ["prix", "cout_achat", "panier", "trafic", "conv", "frequentation", "fixes", "livraison", "cout_pub"]}
un["retours_pts (1 point)"] = round(R(retours_pts=1.0) - base)
print(un)
```
<!--sortie-->
```text
{'prix': 6145, 'cout_achat': -6478, 'panier': 3174, 'trafic': 1204, 'conv': 1204, 'frequentation': 1364, 'fixes': -2042, 'livraison': -315, 'cout_pub': -169, 'retours_pts (1 point)': -5218}
```

**Étape 4 — L'élasticité-seuil.** À partir de quelle élasticité une baisse de prix de 5 % cesse-t-elle de dégrader le résultat ?

```python
seuil = brentq(lambda e: R(prix=-0.05, elasticite=e) - base, 0.1, 15)
print("élasticité-seuil :", round(seuil, 2))
print({e: round(R(prix=-0.05, elasticite=e) - base) for e in (0.6, 1.2, 1.8, 3.0, 4.0)})
```
<!--sortie-->
```text
élasticité-seuil : 3.61
{0.6: -40834, 1.2: -33176, 1.8: -25279, 3.0: -8737, 4.0: 5847}
```

**À vous.** Ajoutez à `PLAGES_DONNEES` un paramètre de votre choix (par exemple `prix` à ±2 %) et relisez le classement. Que dit-il de la différence entre une **décision** (le prix) et une **incertitude** (le trafic) ?

### Application 13.3 — Les lois de la simulation et un premier Monte-Carlo (sections 13.2.1 à 13.2.3 du livre)

**Objectif.** Justifier les lois par les données, puis simuler l'année prochaine.

**Étape 1 — La variabilité mensuelle de la conversion, du panier et des retours.**

```python
x = T["lig"].merge(T["cmd"][["id_commande", "date_commande", "canal"]], on="id_commande")
x = x[x["date_commande"] >= "2025-01-01"]
w = T["ses"].assign(m=lambda d: d["date"].str[:7])
cs = x[x["canal"] == "Site"].assign(m=lambda d: d["date_commande"].str[:7]).groupby("m").agg(ca=("montant", "sum"), n=("id_commande", "nunique"))
cs["conv"] = cs["n"] / w.groupby("m").size(); cs["panier"] = cs["ca"] / cs["n"]
for nom in ["conv", "panier"]:
    mensuel = cs[nom].std() / cs[nom].mean()
    print(nom, "variation mensuelle :", round(mensuel * 100, 1), "% | de la moyenne annuelle :", round(mensuel / np.sqrt(12) * 100, 1), "%")
```
<!--sortie-->
```text
conv variation mensuelle : 15.4 % | de la moyenne annuelle : 4.4 %
panier variation mensuelle : 7.2 % | de la moyenne annuelle : 2.1 %
```

**Étape 2 — 2 000 tirages de l'année prochaine, prix indexés de 3 %.**

```python
P = O.PARAMS_ANNEE_PROCHAINE
tir = O.tirages(2000, seed=7, params=P)
res = O.resultat_rapide(b, tir, prix=0.03)
print("médiane :", round(np.median(res)), "| 10 % :", round(np.quantile(res, 0.1)), "| 90 % :", round(np.quantile(res, 0.9)), "| perte :", round((res < 0).mean() * 100, 1), "%")
```
<!--sortie-->
```text
médiane : 17480 | 10 % : -12044 | 90 % : 47433 | perte : 22.2 %
```

**Étape 3 — Quels paramètres expliquent la variance ?** Régression du résultat centré-réduit sur les paramètres centrés-réduits.

```python
noms = list(P)
X = np.column_stack([tir[k] for k in noms]); Xs = (X - X.mean(0)) / X.std(0); rs = (res - res.mean()) / res.std()
beta = np.linalg.lstsq(Xs, rs, rcond=None)[0]
print((pd.Series(beta ** 2, index=noms).sort_values(ascending=False) * 100).round(1).to_string())
```
<!--sortie-->
```text
cout_achat       66.9
trafic           10.3
panier            8.9
frequentation     5.4
conv              5.3
retours_pts       0.9
fixes             0.8
cout_pub          0.5
livraison         0.4
```

**À vous.** Remplacez l'écart-type du coût d'achat (3 %) par 5 %, puis par 1 %. Que devient la probabilité de perte ? Quelle conclusion en tirez-vous pour la gérante : faut-il discuter de la loi du coût d'achat ou de celle du trafic ?

### Application 13.4 — Stabilité et dépendance (sections 13.2.4 et 13.2.5 du livre)

**Objectif.** Mesurer combien de tirages suffisent, puis l'effet d'une corrélation entre trafic et conversion.

**Étape 1 — Étendue de la médiane selon le nombre de tirages (10 graines).**

```python
for n in (100, 1000, 10000):
    med = [np.median(O.resultat_rapide(b, O.tirages(n, seed=s, params=P), prix=0.03)) for s in range(10)]
    print(n, "tirages : étendue de la médiane =", round(max(med) - min(med)), "€")
```
<!--sortie-->
```text
100 tirages : étendue de la médiane = 7912 €
1000 tirages : étendue de la médiane = 3090 €
10000 tirages : étendue de la médiane = 1205 €
```

**Étape 2 — Corrélation entre trafic et conversion.**

```python
for rho in (-0.5, 0.0, 0.5):
    r = O.resultat_rapide(b, O.tirages(10000, seed=1, rho=rho, params=P), prix=0.03)
    print(f"rho = {rho:+.1f} : écart-type {r.std():8.0f} € | perte {100 * (r < 0).mean():.1f} %")
```
<!--sortie-->
```text
rho = -0.5 : écart-type    23018 € | perte 22.1 %
rho = +0.0 : écart-type    23926 € | perte 22.6 %
rho = +0.5 : écart-type    24816 € | perte 23.1 %
```

**Étape 3 — Une dépendance forte, pour voir.** On force une corrélation de −0,9 : que devient l'écart-type ? Et avec +0,9 ?

```python
for rho in (-0.9, 0.9):
    r = O.resultat_rapide(b, O.tirages(10000, seed=1, rho=rho, params=P), prix=0.03)
    print(f"rho = {rho:+.1f} : écart-type {r.std():8.0f} €")
```
<!--sortie-->
```text
rho = -0.9 : écart-type    22277 €
rho = +0.9 : écart-type    25527 €
```

**À vous.** Pourquoi l'effet de la corrélation est-il si modeste dans ce modèle ? (Indice : regardez la part de variance du coût d'achat dans l'application 13.3.)

### Application 13.5 — Scénarios et « et si » (sections 13.3.1 et 13.3.2 du livre)

**Objectif.** Calculer trois scénarios, les situer dans la distribution simulée, puis chiffrer deux « et si » à partir des données.

**Étape 1 — Trois scénarios cohérents.**

```python
res_sc = {k: O.resultat(b, detail=True, **p) for k, p in O.SCENARIOS.items()}
for k, d in res_sc.items():
    print(f"{k:11s} commandes {d['commandes']:8.0f} | CA HT {d['ca_ht']:10.0f} | résultat {d['resultat']:9.0f} | centile dans la simulation {100 * (res < d['resultat']).mean():5.1f}")
```
<!--sortie-->
```text
central     commandes    12793 | CA HT    1134860 | résultat     17979 | centile dans la simulation  51.4
pessimiste  commandes    11161 | CA HT     961002 | résultat    -53287 | centile dans la simulation   0.2
optimiste   commandes    13724 | CA HT    1241183 | résultat     64901 | centile dans la simulation  97.9
```

**Étape 2 — L'effet d'une promotion plus longue, tiré des données.** Une régression donne l'effet sur les commandes ; les marges par commande viennent des lignes de commande.

```python
promo = O.promo_longue(T)
print({k: round(v, 3) if isinstance(v, float) else v for k, v in promo.items()})
```
<!--sortie-->
```text
{'uplift': 0.194, 'uplift_bas': 0.148, 'uplift_haut': 0.242, 'commandes_base': 193, 'part_soldes': 0.555, 'marge_normale': 32.542, 'marge_soldes': 15.737, 'marge_promo': 23.218, 'delta': -929.054, 'seuil_uplift': 0.402}
```

**Étape 3 — La perte d'un transporteur.**

```python
t = O.transporteurs(T)
c = t.loc["Transporteur C"]
print(t.round(3).to_string())
print("surcoût de remplacement (+8 %) :", round(c["colis"] * b["cout_par_colis"] * 0.08), "€")
```
<!--sortie-->
```text
                colis  abimes  retards
transporteur                          
Transporteur A   3363   0.010    0.153
Transporteur B   2663   0.015    0.264
Transporteur C   1478   0.042    0.522
surcoût de remplacement (+8 %) : 497 €
```

**À vous.** Dans l'étape 1, quel est le **scénario du milieu de la simulation** ? Dans quel centile se trouve le scénario pessimiste, et que concluez-vous de la différence entre un scénario de crise et un mauvais dixième d'années ?

### Application 13.6 — Options, regret et seuils (sections 13.3.3 et 13.3.4 du livre)

**Objectif.** Comparer des options sur les mêmes tirages, calculer le regret, trouver les seuils de bascule.

**Étape 1 — Cinq options sur les mêmes tirages.**

```python
sim = {nom: O.resultat_rapide(b, tir, **opt) for nom, opt in O.OPTIONS.items()}
ref = sim["Indexation de 3 %"]
for nom, v in sim.items():
    print(f"{nom:40s} moyenne {v.mean():9.0f} | perte {100 * (v < 0).mean():5.1f} % | meilleure que l'indexation dans {100 * ((v - ref) > 0).mean():5.1f} % des tirages")
```
<!--sortie-->
```text
Prix inchangé                            moyenne     -1308 | perte  52.8 % | meilleure que l'indexation dans   0.0 % des tirages
Indexation de 3 %                        moyenne     17654 | perte  22.2 % | meilleure que l'indexation dans   0.0 % des tirages
Hausse de 5 %                            moyenne     29552 | perte  10.5 % | meilleure que l'indexation dans 100.0 % des tirages
Baisse de 5 %                            moyenne    -36254 | perte  93.8 % | meilleure que l'indexation dans   0.0 % des tirages
Indexation de 3 % et publicité +20 %     moyenne      8213 | perte  36.1 % | meilleure que l'indexation dans   0.0 % des tirages
```

**Étape 2 — La table de regret sur les trois scénarios.**

```python
M = pd.DataFrame({nom: {s: O.resultat(b, **{**O.SCENARIOS[s], **{k: v for k, v in opt.items() if k == "prix"}, **({"budget_pub": 0.2} if "publicité" in nom else {})}) for s in O.SCENARIOS} for nom, opt in O.OPTIONS.items()})
regret = M.rsub(M.max(axis=1), axis=0)
print(regret.max().round(0).to_string())
```
<!--sortie-->
```text
Prix inchangé                           33237.0
Indexation de 3 %                       12807.0
Hausse de 5 %                               0.0
Baisse de 5 %                           70924.0
Indexation de 3 % et publicité +20 %    21415.0
```

**Étape 3 — Les seuils de bascule.**

```python
cen = lambda **k: {**O.SCENARIOS["central"], **k}
print("hausse du coût d'achat qui annule le résultat 2025 :", round(brentq(lambda x: R(cout_achat=x), -0.05, 0.2) * 100, 2), "%")
print("élasticité où +5 % cesse de battre +3 % :", round(brentq(lambda e: R(**cen(prix=0.05, elasticite=e)) - R(**cen(prix=0.03, elasticite=e)), 0.5, 10), 2))
```
<!--sortie-->
```text
hausse du coût d'achat qui annule le résultat 2025 : 1.31 %
élasticité où +5 % cesse de battre +3 % : 3.22
```

**À vous.** Rédigez en trois phrases ce que vous diriez à la gérante sur la politique de prix, en incluant un seuil. Relisez-vous : une personne qui ne connaît pas le modèle comprend-elle chaque chiffre ?

## Exercices

### Exercice 13.1 ⭐ — Un modèle de poche, à la main (section 13.1.1 du livre)

Un site reçoit 20 000 sessions par mois, converties à 4 %. Le panier moyen est de 100 € TTC (TVA 20 %), le coût d'achat représente 50 % du chiffre d'affaires hors taxe, la livraison coûte 4 € par commande et les charges fixes sont de 15 000 € par mois. (a) Calculez le résultat mensuel. (b) Que devient-il si la conversion passe à 4,4 % (+10 %) ?

### Exercice 13.2 ⭐ — Un écart à expliquer (section 13.1.2 du livre)

Un modèle donne un résultat de 41 769 € quand les comptes disent 39 879 €. Quel est l'écart, en euros et en pourcentage ? Quelle composante des comptes pourrait l'expliquer ? Que feriez-vous si l'écart n'avait **aucune** explication ?

### Exercice 13.3 ⭐⭐ — La marge de contribution d'une commande (section 13.1.4 du livre)

Mesurez l'effet sur le résultat d'une hausse de 1 % du trafic, comptez le nombre de commandes du site supplémentaires, et déduisez ce que **rapporte une commande du site de plus**. Vérifiez l'ordre de grandeur par un raisonnement à la main (prix hors taxe, coût d'achat, livraison, frais bancaires, personnel variable, coût net des retours).

### Exercice 13.4 ⭐⭐ — Quelle plage pour que le trafic passe devant ? (section 13.1.6 du livre)

Avec les plages réalistes, le coût d'achat (±3 %) a une amplitude de 19 435 € et le trafic (±6 %) de 7 223 €. De combien devrait varier le trafic pour avoir la même amplitude que le coût d'achat ? Cette plage est-elle plausible compte tenu de ce que vous savez des sessions mensuelles ?

### Exercice 13.5 ⭐ — Une loi normale pour un coût (section 13.2.2 du livre)

Le coût d'achat varie de +2 % en moyenne avec un écart-type de 3 %, suivant une loi normale. Quelle est la probabilité que le coût **baisse** ? Cela vous semble-t-il plausible ? Proposez une loi qui évite le problème.

### Exercice 13.6 ⭐⭐ — Combien de tirages pour 500 € près ? (section 13.2.4 du livre)

L'écart-type du résultat simulé est d'environ 23 900 €. Combien de tirages faut-il pour connaître le **résultat moyen** à ±500 € près, avec 95 % de confiance ? Vérifiez par simulation avec 40 graines.

### Exercice 13.7 ⭐⭐⭐ — Répercuter les hausses de coût (sections 13.2.5 et 13.3.3 du livre)

La gérante propose une règle : si le coût d'achat dépasse de 1 point l'hypothèse (+2 %), elle augmente ses prix de 0,5 point en plus des 3 %. Simulez cette règle et comparez le résultat moyen, l'écart-type et la probabilité de perte à ceux d'un prix fixé à +3 %. Que montre cet exemple sur la différence entre **une décision fixe** et **une règle de décision** ?

### Exercice 13.8 ⭐⭐ — Un autre scénario de transporteur (section 13.3.2 du livre)

On remplace le transporteur C par un transporteur dont le coût par colis est supérieur de **20 %** et qui abîme 1,5 % des colis. Calculez le surcoût, l'économie sur les colis abîmés (même hypothèse de remboursement qu'au livre) et le gain net. À partir de quel surcoût de remplacement l'opération devient-elle perdante ?

### Exercice 13.9 ⭐⭐ — Le regret selon l'élasticité (section 13.3.3 du livre)

Calculez le résultat de quatre options de prix (inchangé, +3 %, +5 %, −5 %) dans le scénario central pour des élasticités de 0,6, 1,2, 3,0 et 4,0. Quelle option est la meilleure pour chaque élasticité ? Laquelle minimise le plus grand regret ?

### Exercice 13.10 ⭐⭐⭐ — La note à la gérante (sections 13.3.4 et 13.3.5 du livre)

Rédigez la note d'une page : réponse, preuve (un tableau), réserves. Imposez-vous trois chiffres : la **probabilité de perte** avec indexation, le **seuil de hausse du coût d'achat** qui annule le résultat de 2025, et l'**élasticité-seuil** de la baisse de prix. Dites clairement quelles hypothèses ne sont pas mesurées.

## Corrigés

### Corrigé 13.1

```python
def mini(s=20000, c=0.04, p=100, tva=0.2, cout=0.5, fixes=15000, liv=4):
    n = s * c
    ca_ht = n * p / (1 + tva)
    return ca_ht - cout * ca_ht - liv * n - fixes

print("résultat de base :", round(mini()), "€ | avec conversion +10 % :", round(mini(c=0.044)), "€ | écart :", round(mini(c=0.044) - mini()), "€")
```
<!--sortie-->
```text
résultat de base : 15133 € | avec conversion +10 % : 18147 € | écart : 3013 €
```

(a) 800 commandes ; chiffre d'affaires TTC 80 000 €, soit 66 667 € hors taxe ; achats 33 333 € ; livraison 3 200 € ; charges fixes 15 000 € : **résultat de 15 133 €**. (b) Avec 4,4 % de conversion, 880 commandes : le résultat monte à **18 147 €**, soit **+3 013 €**. Un point de vue utile : dix pour cent de conversion en plus fournissent 20 % de résultat en plus, parce que les charges fixes ne bougent pas (**levier opérationnel**).

### Corrigé 13.2

```python
d = O.resultat(b, detail=True)
ecart = d["resultat_avant_retours"] - b["resultat_comptes"]
print(round(ecart), "€,", round(ecart / b["resultat_comptes"] * 100, 1), "% | variation de stock des comptes :", round(T["cr"].loc[T["cr"]["mois"].str.startswith("2025"), "variation_stock"].sum()), "€")
```
<!--sortie-->
```text
1890 €, 4.7 % | variation de stock des comptes : -1888 €
```

L'écart est de **1 890 €**, soit **4,7 %**. Il correspond, à 2 € près, à la **variation de stock** de l'année (−1 888 €) que le modèle ne représente pas. Si l'écart n'avait eu **aucune** explication, il aurait fallu **chercher avant d'utiliser le modèle** : un paramètre mal estimé, un poste de coût oublié, une période mal alignée. Un modèle dont on ne sait pas expliquer l'écart ne doit pas servir à décider.

### Corrigé 13.3

```python
d_orders = (b["sessions_pay"] * b["conv_pay"] + b["sessions_aut"] * b["conv_aut"]) * 0.01
effet = R(trafic=0.01) - base
print("effet de +1 % de trafic :", round(effet), "€ | commandes en plus :", round(d_orders, 2), "| résultat par commande de plus :", round(effet / d_orders, 2), "€")
```
<!--sortie-->
```text
effet de +1 % de trafic : 1204 € | commandes en plus : 60.78 | résultat par commande de plus : 19.81 €
```

+1 % de trafic donne **+1 204 €** pour **60,8 commandes** de plus : une commande du site de plus rapporte environ **19,81 €**. À la main : un panier de 101,63 € TTC fait 84,69 € hors taxe ; le coût d'achat de ses 2,77 articles vaut environ 52,9 € ; la livraison coûte 4,20 € ; les frais bancaires et le personnel variable environ 1,5 € + 3,7 € ; le coût net moyen des retours environ 2,5 €. Il reste de l'ordre de 20 €, ce que donne le modèle : la **marge de contribution** d'une commande est de près d'**un quart de son chiffre d'affaires hors taxe**.

### Corrigé 13.4

Il faut une amplitude de 19 435 € pour 7 223 € à ±6 %, soit **un facteur 2,7** : le trafic devrait varier d'environ **±16 %** (19 435 / 1 204 € par point). Sur les sessions mensuelles, l'écart d'un mois à l'autre atteint 18 % (mais en grande partie par saison) : un écart annuel de ±16 % est **peu plausible** pour une année sans événement exceptionnel. Le classement « coût d'achat avant trafic » est donc robuste pour la boutique, ce qui n'est pas vrai de toutes les plages.

### Corrigé 13.5

```python
from scipy.stats import norm
print("P(baisse) =", round(norm.cdf(-0.02 / 0.03), 4))
```
<!--sortie-->
```text
P(baisse) = 0.2525
```

$P(X<0)=\Phi\!\left(\frac{0-0{,}02}{0{,}03}\right)=\Phi(-0{,}667)\approx25{,}25\ \%$ : une chance sur quatre que le coût d'achat **baisse**, ce qui n'est guère plausible quand les fournisseurs annoncent des hausses. On corrige en choisissant une loi qui ne prend que des valeurs positives pour le **facteur** de variation (par exemple une loi **log-normale** sur $1+\Delta$), ou en tronquant la normale à zéro ; l'essentiel est d'**écrire** pourquoi.

### Corrigé 13.6

```python
sigma = 23926
print("n =", round((1.96 * sigma / 500) ** 2))
P = O.PARAMS_ANNEE_PROCHAINE
moy = [O.resultat_rapide(b, O.tirages(8800, seed=s, params=P), prix=0.03).mean() for s in range(40)]
print("écart-type de la moyenne sur 40 graines :", round(np.std(moy)), "€ | demi-largeur à 95 % :", round(1.96 * np.std(moy)), "€")
```
<!--sortie-->
```text
n = 8797
écart-type de la moyenne sur 40 graines : 274 € | demi-largeur à 95 % : 537 €
```

L'erreur de la moyenne de $n$ tirages est $\sigma/\sqrt n$ ; pour qu'elle soit de $500/1{,}96$, il faut $n=(1{,}96\sigma/500)^2\approx$ **8 797 tirages**. La simulation avec 8 800 tirages et 40 graines donne un écart-type de la moyenne de 274 €, donc une demi-largeur à 95 % d'environ 537 € : de l'ordre de la précision visée (les 40 graines ne donnent qu'une estimation de cet écart-type).

### Corrigé 13.7

```python
P = O.PARAMS_ANNEE_PROCHAINE
tir = O.tirages(10000, seed=1, params=P)
fixe = O.resultat_rapide(b, tir, prix=0.03)
regle = O.resultat_rapide(b, tir, prix=0.03 + 0.5 * (tir["cout_achat"] - 0.02))
for nom, v in (("prix fixé à +3 %", fixe), ("règle de répercussion", regle)):
    print(f"{nom:24s} moyenne {v.mean():7.0f} | écart-type {v.std():7.0f} | perte {100 * (v < 0).mean():.1f} %")
```
<!--sortie-->
```text
prix fixé à +3 %         moyenne   18213 | écart-type   23926 | perte 22.6 %
règle de répercussion    moyenne   18302 | écart-type   17204 | perte 14.2 %
```

Le résultat moyen est quasiment le même (18 213 € contre 18 302 €), mais l'**écart-type tombe de 23 926 € à 17 204 €** et la probabilité de perte de **22,6 % à 14,2 %**. Une **règle de décision** (« je répercute la moitié des hausses ») **réduit le risque** sans coûter d'espérance, parce qu'elle fait varier le prix **en sens contraire** du coût : c'est une corrélation voulue entre un paramètre incertain et une décision. Un prix fixé ne profite pas de cette information. (Le modèle suppose que l'élasticité reste la même : une règle de prix qui bouge peut aussi perturber la clientèle, ce que le modèle ignore.)

### Corrigé 13.8

```python
t = O.transporteurs(T); c = t.loc["Transporteur C"]
surcout = c["colis"] * b["cout_par_colis"] * 0.20
evites = c["colis"] * (c["abimes"] - 0.015)
eco = evites * b["panier_site"] / (1 + O.TVA)
print("surcoût :", round(surcout), "| colis abîmés évités :", round(evites, 1), "| économie :", round(eco), "| gain net :", round(eco - surcout))
print("surcoût de remplacement maximal :", round(eco / (c["colis"] * b["cout_par_colis"]) * 100, 1), "%")
```
<!--sortie-->
```text
surcoût : 1242 | colis abîmés évités : 39.8 | économie : 3373 | gain net : 2132
surcoût de remplacement maximal : 54.3 %
```

Surcoût de 20 % : **1 242 €** ; colis abîmés évités : 1 478 × (4,2 % − 1,5 %) ≈ **39,8** ; économie (remboursement HT d'un panier moyen) : **3 373 €** ; **gain net : 2 132 €**. L'opération reste gagnante tant que le surcoût de remplacement est inférieur à environ **54 %** (3 373 / 6 208 €, le coût actuel de livraison des colis du transporteur C). C'est un **seuil de bascule** que l'on peut présenter à la gérante, avec le rappel que l'hypothèse « chaque colis abîmé est remboursé en totalité » est discutable.

### Corrigé 13.9

```python
opts = {"Prix inchangé": 0.0, "Indexation de 3 %": 0.03, "Hausse de 5 %": 0.05, "Baisse de 5 %": -0.05}
tab = pd.DataFrame({e: pd.Series({k: R(**{**O.SCENARIOS["central"], "prix": v, "elasticite": e}) for k, v in opts.items()}) for e in (0.6, 1.2, 3.0, 4.0)})
print(tab.round(0).astype(int).to_string())
regret = tab.rsub(tab.max(axis=0), axis=1)
print("meilleure option par élasticité :", tab.idxmax().to_dict())
print("plus grand regret par option :", regret.max(axis=1).round(0).astype(int).to_dict())
```
<!--sortie-->
```text
                     0.6    1.2    3.0    4.0
Prix inchangé      -1079  -1079  -1079  -1079
Indexation de 3 %  23373  17979   2359  -5966
Hausse de 5 %      39238  29928   3579 -10090
Baisse de 5 %     -43717 -36224 -12309   1962
meilleure option par élasticité : {0.6: 'Hausse de 5 %', 1.2: 'Hausse de 5 %', 3.0: 'Hausse de 5 %', 4.0: 'Baisse de 5 %'}
plus grand regret par option : {'Prix inchangé': 40317, 'Indexation de 3 %': 15865, 'Hausse de 5 %': 12052, 'Baisse de 5 %': 82955}
```

La **hausse de 5 %** est la meilleure pour les élasticités de 0,6, 1,2 et 3,0 ; pour 4,0 (au-delà de tous les seuils), c'est la **baisse de 5 %**. Le plus grand regret est de **12 052 €** pour la hausse de 5 %, **15 865 €** pour l'indexation, 40 317 € pour le prix inchangé et 82 955 € pour la baisse : la hausse de 5 % **minimise le regret maximal** même en couvrant des élasticités élevées. On voit aussi que la **recommandation ne change qu'au-delà d'une élasticité de 3,2** : tant que l'on n'y croit pas, la hausse domine.

### Corrigé 13.10

Éléments de réponse (une note acceptable contient ces trois chiffres, chacun avec sa phrase).

- **Probabilité de perte avec indexation de 3 % : 22,6 %** (10 000 tirages, médiane 17 834 €, intervalle à 80 % de −11 755 € à 49 067 €). « Une année sur quatre environ, on perd de l'argent. »
- **Seuil de coût d'achat : +1,31 %.** « Une hausse de 1,3 % non répercutée annule le résultat de 2025. »
- **Élasticité-seuil de la baisse de 5 % : 3,6.** « Baisser les prix ne rapporte que si chaque 1 % de baisse fait gagner plus de 3,6 % de commandes. »
- **Réserves** : le modèle suppose une élasticité constante (non mesurée), six lois sur neuf sont des hypothèses, les retours ne figurent pas dans le compte de résultat simulé et sont ajoutés par le modèle, les chiffres sont des ordres de grandeur.
- **Recommandation** : indexer les prix, tester une hausse plus forte sur quelques produits (test A/B), sécuriser le coût d'achat.

Une bonne note met la **réponse en tête**, le **tableau** en milieu de page et les **réserves** en bas, et n'utilise aucun mot que la gérante ne comprendrait pas (pas de « tirage », « centile » sans explication).
