# Chapitre 3 : Introduction à l'analytique prédictive — exercices et applications

> 🧭 Ce cahier prolonge le chapitre 3. On y **chiffre la valeur d'une prévision**, on **prévoit à la semaine**, on **mesure la couverture d'une fourchette**, on **change la fenêtre d'une cible**, on fait varier les **hypothèses d'une campagne**, on **compare un modèle simple et un modèle puissant**, on **surveille** un modèle et l'on **écrit son propre AutoML**. Le cahier est autonome : il recharge ses données. Les données sont **simulées** (celles de la boutique) ; les fonctions de `build/outils_ch03.py` fabriquent les tables du livre (série mensuelle, instantanés de clients, prévisions par origine glissante).

```python
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch03 as O
from sklearn.metrics import roc_auc_score, brier_score_loss

d = O.charger(os.environ["DONNEES"])
M, j, cmd = d["M"], d["j"], d["cmd"]
R = O.origines(d)                                            # origine glissante 2025 : 12 prévisions à 1 mois, 10 à 3 mois
inst_tr, inst_te = O.instantane(d, "2024-06-30"), O.instantane(d, "2025-06-30")
print("mois :", len(M), "| prévisions :", len(R), "| clients (2024, 2025) :", len(inst_tr), len(inst_te))
```
<!--sortie-->
```text
mois : 36 | prévisions : 22 | clients (2024, 2025) : 3605 4409
```

## Applications

### Application 3.1 — Le meilleur coefficient de sécurité (section 3.1.3)

**Objectif.** Retrouver par le calcul la règle de la section 3.1.3 : avec des coûts asymétriques, la bonne capacité est la prévision **plus une marge** égale à un quantile de l'erreur.

**Étape 1 — des coûts différents.** Une commande de capacité inutilisée coûte maintenant **6 €**, une commande sans capacité **10 €**. Calculez, pour la régression de Poisson à un mois (douze mois de 2025), le coût annuel avec une marge de 0 % à 8 % par pas de 1 point.

```python
r = R[R["h"] == 1]
def cout(capacite, reel, inactif=6, manque=10):
    return inactif * np.maximum(capacite - reel, 0) + manque * np.maximum(reel - capacite, 0)

marges = np.arange(0, 0.09, 0.01)
couts = [cout(r["régression de Poisson"] * (1 + m_), r["reel"]).sum() for m_ in marges]
print(pd.Series(couts, index=[f"{m_:.0%}" for m_ in marges]).round(0).to_string())
```
<!--sortie-->
```text
0%    3667.0
1%    2715.0
2%    2162.0
3%    2081.0
4%    2456.0
5%    2931.0
6%    3591.0
7%    4358.0
8%    5124.0
```

**Étape 2 — la règle théorique.** Le quantile visé vaut $10 / (10 + 6)$. Calculez le quantile correspondant des erreurs relatives de la régression et comparez-le à la marge qui minimise le coût.

```python
q = 10 / (10 + 6)
err = r["reel"] / r["régression de Poisson"] - 1
print("quantile visé :", round(q, 3), "| quantile de l'erreur relative :", round(err.quantile(q) * 100, 1), "%")
print("marge qui minimise le coût :", f"{marges[int(np.argmin(couts))]:.0%}")
```
<!--sortie-->
```text
quantile visé : 0.625 | quantile de l'erreur relative : 3.0 %
marge qui minimise le coût : 3%
```

**À interpréter.** Les deux nombres sont-ils proches ? Pourquoi la courbe des coûts est-elle plate près de son minimum ? (Pistes en fin de cahier.)

### Application 3.2 — Prévoir à la semaine (sections 3.2.1 à 3.2.4)

**Objectif.** Refaire le cas A avec **une prévision par semaine** à la place d'une par mois, et mesurer ce que cela change.

**Étape 1 — la série hebdomadaire.** On prend 156 semaines de sept jours à partir du premier jour de la série.

```python
jj = j.iloc[:156 * 7].copy()
jj["sem"] = np.arange(len(jj)) // 7
S_h = jj.groupby("sem")["nb_commandes"].sum()
print("semaines :", len(S_h), "| moyenne :", round(S_h.mean()), "commandes par semaine")
```
<!--sortie-->
```text
semaines : 156 | moyenne : 232 commandes par semaine
```

**Étape 2 — référence saisonnière et régression de Poisson.** Pour chaque semaine `o` de l'année 2025 (origines 104 à 154), on prévoit la semaine **suivante**. Référence : la semaine 52 semaines plus tôt, multipliée par la croissance des 52 dernières semaines sur les 52 précédentes. Régression : le modèle du livre, ajusté sur les jours connus, additionné sur les sept jours de la semaine.

```python
import statsmodels.api as sm
import statsmodels.formula.api as smf
lignes = []
for o in range(104, 155):
    g = S_h.iloc[o - 52:o].sum() / S_h.iloc[o - 104:o - 52].sum()
    ref = S_h.iloc[o - 52] * g
    mod = smf.glm("nb_commandes ~ C(mois) + C(dow) + promo_active + t", jj[jj["sem"] < o], family=sm.families.Poisson()).fit()
    lignes.append((S_h.iloc[o], ref, mod.predict(jj[jj["sem"] == o]).sum()))
H = pd.DataFrame(lignes, columns=["reel", "saison×croiss.", "poisson"])
for c in ["saison×croiss.", "poisson"]:
    e = H[c] - H["reel"]
    print(f"{c:15s} MAE {e.abs().mean():5.1f} | MAPE {(e.abs() / H['reel']).mean() * 100:4.1f} % | biais {e.mean():+5.1f}")
```
<!--sortie-->
```text
saison×croiss.  MAE  19.8 | MAPE  8.4 % | biais  -6.3
poisson         MAE  12.3 | MAPE  5.3 % | biais  -3.1
```

**À interpréter.** Comparez avec le cas mensuel : l'erreur **relative** est-elle plus grande ou plus petite à la semaine ? Pourquoi ? (Voir la granularité, section 3.1.4.)

### Application 3.3 — Une fourchette tient-elle ses promesses ? (section 3.2.5)

**Objectif.** Vérifier si la fourchette « 10e–90e centile des erreurs passées » couvre bien huit réalisations sur dix, **en la testant sur les erreurs qui ont servi à la fabriquer**, sans tricher.

**Étape 1 — la fourchette, hors échantillon.** Pour chacune des 22 prévisions passées, on construit la fourchette avec les **21 autres** erreurs relatives, puis on regarde si l'erreur de la prévision tombe dedans.

```python
e = (R["reel"] / R["régression de Poisson"] - 1).values
dedans = []
for i in range(len(e)):
    autres = np.delete(e, i)
    lo, hi = np.quantile(autres, [0.10, 0.90])
    dedans.append(lo <= e[i] <= hi)
print("couverture :", sum(dedans), "sur", len(e), "=", round(np.mean(dedans) * 100), "%")
```
<!--sortie-->
```text
couverture : 16 sur 22 = 73 %
```

**Étape 2 — la largeur.** Calculez la largeur relative de la fourchette pour une prévision de 1 000 commandes, et celle d'une fourchette à 95 % (2,5e–97,5e centile). Qu'ajoute-t-elle de fiable, qu'ajoute-t-elle de trompeur avec seulement 22 erreurs ?

```python
for niveau in (0.80, 0.95):
    lo, hi = np.quantile(e, [(1 - niveau) / 2, 1 - (1 - niveau) / 2])
    print(f"{niveau:.0%} : de {1000 * (1 + lo):.0f} à {1000 * (1 + hi):.0f}")
```
<!--sortie-->
```text
80% : de 965 à 1044
95% : de 918 à 1053
```

### Application 3.4 — Changer la fenêtre de la cible (section 3.2.6)

**Objectif.** Mesurer à quel point la **définition** de la cible change le problème : rachat à 60, 90, 120 ou 180 jours.

**Étape 1 — le taux et l'AUC pour chaque horizon.** Pour chaque horizon, on construit les instantanés de 2024 et de 2025, on ajuste la régression logistique sur le premier et l'on mesure l'AUC sur le second.

```python
lignes = []
for h in (60, 90, 120, 180):
    a, b = O.instantane(d, "2024-06-30", horizon=h), O.instantane(d, "2025-06-30", horizon=h)
    p = O.modele_log().fit(a[O.VARS], a["y"]).predict_proba(b[O.VARS])[:, 1]
    lignes.append((h, a["y"].mean(), b["y"].mean(), roc_auc_score(b["y"], p)))
print(pd.DataFrame(lignes, columns=["jours", "taux 2024", "taux 2025", "AUC 2025"]).round(3).to_string(index=False))
```
<!--sortie-->
```text
 jours  taux 2024  taux 2025  AUC 2025
    60      0.289      0.268     0.709
    90      0.408      0.374     0.724
   120      0.495      0.462     0.743
   180      0.655      0.620     0.771
```

**À interpréter.** Quand la fenêtre s'allonge, le taux de rachat monte et l'AUC bouge. Pourquoi ? Quelle fenêtre choisiriez-vous pour une campagne dont le délai de préparation est de trois semaines ?

### Application 3.5 — Les hypothèses d'une campagne (section 3.2.12)

**Objectif.** Faire varier le **coût du contact** et l'**effet** supposé du message, et voir quand la campagne cesse de valoir la peine.

**Étape 1 — la grille.** On reprend la régression du livre sur le test. Pour chaque couple (effet relatif, coût), on contacte les clients dont le gain attendu est positif et l'on somme la marge attendue.

```python
p = O.modele_log().fit(inst_tr[O.VARS], inst_tr["y"]).predict_proba(inst_te[O.VARS])[:, 1]
marge = cmd["marge"].mean()
grille = {}
for effet in (0.05, 0.10, 0.15, 0.20):
    ligne = {}
    for cout_c in (1.0, 1.5, 2.0, 3.0):
        g = effet * p * marge - cout_c
        ligne[f"{cout_c:.1f} €"] = round(g[g > 0].sum())
    grille[f"+{effet:.0%}"] = ligne
print(pd.DataFrame(grille).T.to_string())
```
<!--sortie-->
```text
      1.0 €  1.5 €  2.0 €  3.0 €
+5%      74      0      0      0
+10%   1513    592    148      0
+15%   3730   2270   1261    221
+20%   6306   4409   3026   1185
```

**Étape 2 — le nombre de contacts.** Pour l'effet de +10 % et le coût de 1,50 €, retrouvez le nombre de clients contactés et la marge attendue du livre, puis recalculez-les en ne gardant que les clients qui ont donné leur consentement.

```python
g = 0.10 * p * marge - 1.5
oui = g > 0
consent = inst_te["consentement"].values == 1
print("contactés :", oui.sum(), "| marge :", round(g[oui].sum()), "€ | avec consentement :", (oui & consent).sum(), "contacts,", round(g[oui & consent].sum()), "€")
```
<!--sortie-->
```text
contactés : 1322 | marge : 592 € | avec consentement : 806 contacts, 355 €
```

**À interpréter.** Dans quelle case de la grille la campagne perd-elle de l'argent ? Que dit la grille de la **valeur d'un essai** qui mesurerait l'effet réel du message ? (Voir la section 3.2.12.)

### Application 3.6 — Simple contre puissant, avec intervalle (section 3.3.2)

**Objectif.** Répéter le test honnête du livre sur une **autre paire de coupures** (31 mars 2024 pour apprendre, 31 mars 2025 pour tester) et comparer régression logistique, arbre peu profond et boosting.

**Étape 1 — les trois modèles sur la paire de mars.** Les trois sont ajustés sur l'instantané de mars 2024 et mesurés sur celui de mars 2025.

```python
a, b = O.instantane(d, "2024-03-31"), O.instantane(d, "2025-03-31")
yb = b["y"].values
modeles = {"logistique": (O.modele_log(), O.VARS), "arbre (prof. 3)": (O.modele_arbre(3, 100), O.VARS_BRUTES), "boosting": (O.modele_boost(), O.VARS)}
P = {nom: m.fit(a[v], a["y"]).predict_proba(b[v])[:, 1] for nom, (m, v) in modeles.items()}
for nom, p_ in P.items():
    print(f"{nom:16s} AUC {roc_auc_score(yb, p_):.3f}")
```
<!--sortie-->
```text
logistique       AUC 0.734
arbre (prof. 3)  AUC 0.719
boosting         AUC 0.727
```

**Étape 2 — l'écart avec son intervalle.** Calculez, par bootstrap (500 tirages), l'écart d'AUC entre la régression logistique et chacun des deux autres.

```python
rng = np.random.default_rng(0)
tirages = [rng.integers(0, len(yb), len(yb)) for _ in range(500)]
for nom in ("arbre (prof. 3)", "boosting"):
    ec = [roc_auc_score(yb[i], P["logistique"][i]) - roc_auc_score(yb[i], P[nom][i]) for i in tirages]
    print(f"logistique − {nom:16s} : {np.mean(ec):+.3f} [{np.percentile(ec, 2.5):+.3f} ; {np.percentile(ec, 97.5):+.3f}]")
```
<!--sortie-->
```text
logistique − arbre (prof. 3)  : +0.015 [+0.009 ; +0.021]
logistique − boosting         : +0.006 [-0.000 ; +0.012]
```

**À interpréter.** Les conclusions du livre se retrouvent-elles ? Que feriez-vous si le boosting gagnait de 0,003 avec un intervalle qui contient zéro ?

### Application 3.7 — Un tableau de surveillance (section 3.3.4)

**Objectif.** Construire le tableau de bord de surveillance de la section 3.3.4 pour le modèle entraîné en juin 2024 et en déclencher les alertes.

**Étape 1 — les indicateurs à chaque coupure.** Pour chaque coupure trimestrielle suivante, on calcule la dérive de trois variables (en écarts-types de l'entraînement), la probabilité moyenne annoncée, la part observée et l'AUC.

```python
S = O.panel(d)
modele = O.modele_log().fit(inst_tr[O.VARS], inst_tr["y"])
ref = inst_tr[["l_nb_12m", "l_recence", "rythme"]]
lignes = []
for c in ["2024-12-31", "2025-03-31", "2025-06-30", "2025-09-30"]:
    s = S[c]; p_ = modele.predict_proba(s[O.VARS])[:, 1]
    deriv = ((s[ref.columns].mean() - ref.mean()) / ref.std()).abs().max()
    lignes.append((c, round(deriv, 2), round(p_.mean(), 3), round(s["y"].mean(), 3), round(roc_auc_score(s["y"], p_), 3)))
T = pd.DataFrame(lignes, columns=["coupure", "dérive max (σ)", "annoncé", "observé", "AUC"])
T["écart (points)"] = ((T["observé"] - T["annoncé"]) * 100).round(1)
print(T.to_string(index=False))
```
<!--sortie-->
```text
   coupure  dérive max (σ)  annoncé  observé   AUC  écart (points)
2024-12-31            0.14    0.399    0.379 0.727            -2.0
2025-03-31            0.19    0.396    0.408 0.735             1.2
2025-06-30            0.23    0.394    0.374 0.724            -2.0
2025-09-30            0.27    0.392    0.486 0.747             9.4
```

**Étape 2 — les alertes.** Appliquez les seuils de la section 3.3.4 : dérive d'une variable de plus d'un écart-type ; écart de plus de 3 points entre annoncé et observé ; AUC en baisse de plus de 0,03 par rapport à 0,724.

```python
T["alerte entrées"] = T["dérive max (σ)"] > 1
T["alerte calibration"] = T["écart (points)"].abs() > 3
T["alerte AUC"] = T["AUC"] < 0.724 - 0.03
print(T[["coupure", "alerte entrées", "alerte calibration", "alerte AUC"]].to_string(index=False))
```
<!--sortie-->
```text
   coupure  alerte entrées  alerte calibration  alerte AUC
2024-12-31           False               False       False
2025-03-31           False               False       False
2025-06-30           False               False       False
2025-09-30           False                True       False
```

**À interpréter.** Quelles alertes se déclenchent, à quelle coupure ? Laquelle est **saisonnière** et laquelle est une vraie **dérive** ? Qu'écririez-vous au propriétaire du modèle ?

### Application 3.8 — Votre AutoML (section 3.4.2)

**Objectif.** Écrire une petite recherche, choisir par la règle de l'écart-type, et ouvrir le test **une seule fois**.

**Étape 1 — la recherche.** Douze configurations tirées au sort, validées par trois plis temporels, puis notées sur la coupure scellée de juin 2025.

```python
cfgs = O.configurations(12, graine=21)
res = O.recherche(S, cfgs)
print(res.sort_values("cv", ascending=False)[["id", "famille", "cv", "cv_sd", "test"]].round(4).to_string(index=False))
```
<!--sortie-->
```text
 id    famille     cv  cv_sd   test
 10   boosting 0.7341 0.0056 0.7321
  7      forêt 0.7340 0.0061 0.7290
  1   boosting 0.7338 0.0066 0.7318
  8   boosting 0.7336 0.0066 0.7317
  4   boosting 0.7331 0.0050 0.7317
  6   boosting 0.7329 0.0042 0.7312
  2   boosting 0.7324 0.0059 0.7303
  5 logistique 0.7291 0.0080 0.7273
  3 logistique 0.7291 0.0080 0.7273
 11   boosting 0.7254 0.0052 0.7230
 12      arbre 0.7216 0.0055 0.7227
  9      arbre 0.7160 0.0070 0.7189
```

**Étape 2 — la règle de l'écart-type.** Parmi les configurations à moins d'un écart-type du meilleur score de validation, gardez la plus simple (ordre de simplicité : logistique, arbre, boosting, forêt) et comparez-la au premier du classement.

```python
meilleur = res.loc[res["cv"].idxmax()]
ok = res[res["cv"] >= meilleur["cv"] - meilleur["cv_sd"]].copy()
ok["simplicité"] = ok["famille"].map({"logistique": 0, "arbre": 1, "boosting": 2, "forêt": 3})
choix = ok.sort_values(["simplicité", "cv"], ascending=[True, False]).iloc[0]
print("premier :", meilleur["famille"], round(meilleur["test"], 4), "| choisi :", choix["famille"], round(choix["test"], 4), "| candidats dans l'écart-type :", len(ok))
```
<!--sortie-->
```text
premier : boosting 0.7321 | choisi : logistique 0.7273 | candidats dans l'écart-type : 9
```

**À interpréter.** Que perd-on au test en choisissant le plus simple ? Que gagne-t-on, en dehors du score ?

## Exercices

### Exercice 3.1 ⭐ — Quatre natures de questions (section 3.1.1)

Classez chaque question comme **descriptive, diagnostique, prédictive ou prescriptive**, et dites en une phrase pourquoi.

1. « Quel a été notre chiffre d'affaires par canal en 2025 ? »
2. « Pourquoi le canal Réseaux convertit-il moins que l'e-mail ? »
3. « Combien de colis partiront en décembre 2026 ? »
4. « Quels clients dois-je appeler cette semaine ? »
5. « Ce client rachètera-t-il d'ici trois mois ? »
6. « La nouvelle page de paiement a-t-elle amélioré la conversion ? »
7. « Quel budget publicitaire maximise la marge de mars ? »
8. « Combien de retours avons-nous eus en 2025 ? »

### Exercice 3.2 ⭐ — Prédire, expliquer ou décider ? (section 3.1.2)

Pour chacune des trois phrases extraites d'un rapport, dites si elle **prédit**, **explique** ou **décide**, et ce qui manque pour qu'elle soit défendable.

- (a) « Le modèle prévoit 1 014 commandes en janvier 2026. »
- (b) « Les soldes font vendre 19 % de commandes en plus. »
- (c) « Le modèle montre que les soldes font vendre 19 % de plus, donc refaisons les soldes. »

### Exercice 3.3 ⭐⭐ — La référence naïve à la main (section 3.1.5)

Les ventes trimestrielles (en unités) d'un produit sont, en 2024 : 120, 90, 80, 210 ; en 2025 : 130, 95, 85, 225. On prévoit chaque trimestre de 2025 de deux façons : par **le trimestre précédent** et par **le même trimestre de l'an dernier**. Calculez l'erreur absolue moyenne de chaque méthode et le **gain relatif** de la seconde sur la première.

### Exercice 3.4 ⭐ — MAE, MAPE et biais (section 3.2.4)

Six mois réels : 900, 1 000, 800, 950, 1 100, 1 250. Six prévisions : 950, 980, 760, 1 000, 1 050, 1 200. Calculez à la main la MAE, la MAPE et le biais. Que dit le signe du biais ?

### Exercice 3.5 ⭐⭐ — Une fourchette avec dix erreurs (section 3.2.5)

Dix erreurs relatives passées d'une prévision : +3 %, −2 %, +7 %, 0 %, −4 %, +1 %, +5 %, −1 %, +2 %, +2 %. Calculez les 10e et 90e centiles (interpolation linéaire), puis la fourchette pour une prévision de 500. Pourquoi cette fourchette est-elle fragile ?

### Exercice 3.6 ⭐ — L'AUC et le gain à la main (section 3.2.10)

Six clients : P1 (score 0,8), P2 (0,55) et P3 (0,35) ont racheté ; N1 (0,6), N2 (0,4) et N3 (0,1) n'ont pas racheté. Calculez l'AUC (neuf couples) puis la part des acheteurs touchés en contactant la moitié des clients.

### Exercice 3.7 ⭐⭐ — Chasser la fuite (section 3.2.11)

On prédit le rachat à 90 jours pour une coupure au 30 juin 2024. Pour chaque variable candidate, dites **sûre**, **fuite** ou **à vérifier**, et ce que vous demanderiez.

- (a) le nombre de commandes des douze derniers mois ;
- (b) le statut « client actif », actualisé chaque nuit par l'outil de gestion de la relation client ;
- (c) le montant de la première commande ;
- (d) le nombre de retours, sans regarder la date du retour ;
- (e) la note de satisfaction de l'enquête menée en 2025 ;
- (f) le canal d'acquisition ;
- (g) « a reçu l'e-mail de relance du troisième trimestre ».

### Exercice 3.8 ⭐⭐ — Le seuil par les coûts (section 3.2.12)

Un contact coûte 2 €, une commande rapporte 40 € de marge, le message augmente la probabilité de rachat de 20 % de sa valeur. Quel est le **seuil de probabilité** ? Dix clients ont les scores 0,05 ; 0,12 ; 0,20 ; 0,24 ; 0,26 ; 0,31 ; 0,45 ; 0,52 ; 0,66 ; 0,80. Lesquels contacter, et quel gain total attendre ?

### Exercice 3.9 ⭐⭐ — Un dossier de passation pour le cas A (section 3.3.3)

Rédigez le dossier de passation de la **prévision mensuelle des commandes** : question et décision, population (ou série), cible et horizon, séparation, variables connues à l'avance, références et métriques, ce qui a été essayé, contraintes, critères de réussite, risques. Appuyez-vous sur les chiffres du chapitre.

### Exercice 3.10 ⭐⭐⭐ — Passer la main, ou non ? (section 3.3.1)

Pour chaque situation, décidez s'il faut **passer la main** à une équipe de science des données et justifiez avec les signes de la section 3.3.1 : (a) prévoir les ventes mensuelles par canal pour 2026 ; (b) classer 30 000 avis clients par thème et par sentiment ; (c) évaluer en temps réel chaque paiement du site pour détecter les fraudes ; (d) choisir les destinataires d'une lettre d'information trimestrielle.

### Exercice 3.11 ⭐⭐ — Lire un classement (section 3.4.3)

Un outil sans code classe six modèles par AUC de validation (moyenne ± écart-type des plis) : A boosting de 500 arbres 0,742 ± 0,010 ; B forêt 0,741 ± 0,012 ; C régression logistique 0,739 ± 0,006 ; D arbre de profondeur 3 0,735 ± 0,004 ; E empilement de cinq modèles 0,744 ± 0,015 ; F tri par récence seule 0,725 ± 0,003. Quel modèle choisissez-vous par la règle de l'écart-type, et quelles questions posez-vous à l'outil avant de vous fier à ce classement ?

### Exercice 3.12 ⭐⭐⭐ — Répondre à un fournisseur d'outil (section 3.4.4)

Un fournisseur propose un outil sans code pour « prédire le départ des clients » et annonce « 94 % de précision ». Rédigez la réponse que vous lui envoyez : quelles informations demandez-vous, et pourquoi « 94 % de précision » ne vous dit rien ?

## Corrigés

### Corrigé 3.1

1. **Descriptive** : un total passé. 2. **Diagnostique** : on cherche une cause. 3. **Prédictive** : un comptage futur. 4. **Prescriptive** : « à qui écrire » exige la prédiction **et** un coût **et** l'effet de l'appel. 5. **Prédictive** : une probabilité sur un événement daté. 6. **Diagnostique** : un effet causal, mesuré par un test A/B. 7. **Prescriptive** : on compare des actions (budgets) pour maximiser un résultat. 8. **Descriptive** : un décompte passé.

### Corrigé 3.2

(a) **Prédit** : il manque la fourchette, les hypothèses (soldes du 8 au 28 janvier) et la date où l'on vérifiera. (b) **Explique** : c'est un effet estimé, il manque son intervalle et la précision « à saison, jour et tendance égaux ». (c) **Décide** par un raccourci : on passe de l'effet sur les commandes à la décision sans regarder la **marge** (qui baisse malgré les commandes en plus, volume III) ni la fourchette ; de plus, « le modèle montre que les soldes font vendre » est une lecture causale d'un modèle construit pour prédire.

### Corrigé 3.3

```python
reel = np.array([130, 95, 85, 225]); naif = np.array([210, 130, 95, 85]); saison = np.array([120, 90, 80, 210])
mae_n, mae_s = np.abs(naif - reel).mean(), np.abs(saison - reel).mean()
print(mae_n, mae_s, round((1 - mae_s / mae_n) * 100, 1), "%")
```
<!--sortie-->
```text
66.25 8.75 86.8 %
```

Le « trimestre précédent » se trompe de 80, 35, 10 et 140 : MAE de **66,25**. Le « même trimestre de l'an dernier » se trompe de 10, 5, 5 et 15 : MAE de **8,75**. Le gain relatif est 1 − 8,75 / 66,25 = **87 %** : sur une série très saisonnière, la référence saisonnière est de loin la plus honnête.

### Corrigé 3.4

```python
reel = np.array([900, 1000, 800, 950, 1100, 1250]); prev = np.array([950, 980, 760, 1000, 1050, 1200])
e = prev - reel
print(np.abs(e).mean().round(1), (np.abs(e) / reel).mean().round(4), e.mean())
```
<!--sortie-->
```text
43.3 0.0439 -10.0
```

Les erreurs (prévu − réel) sont +50, −20, −40, +50, −50, −50 : MAE = 260 / 6 ≈ **43,3** ; MAPE = (5,56 + 2 + 5 + 5,26 + 4,55 + 4) / 6 ≈ **4,4 %** ; biais = −60 / 6 = **−10**. Le biais négatif signifie que, **en moyenne**, on sous-estime de dix commandes par mois ; il est petit devant la MAE (43), donc la prévision n'est pas systématiquement trop basse : ses erreurs se compensent presque.

### Corrigé 3.5

```python
e = np.array([0.03, -0.02, 0.07, 0.0, -0.04, 0.01, 0.05, -0.01, 0.02, 0.02])
lo, hi = np.quantile(e, [0.10, 0.90])
print(round(lo, 3), round(hi, 3), round(500 * (1 + lo)), round(500 * (1 + hi)))
```
<!--sortie-->
```text
-0.022 0.052 489 526
```

Triées : −4, −2, −1, 0, +1, +2, +2, +3, +5, +7 %. Le 10e centile est à la position 0,9 : −4 + 0,9 × 2 = **−2,2 %** ; le 90e à la position 8,1 : 5 + 0,1 × 2 = **+5,2 %**. La fourchette pour 500 est **489 à 526**. Elle est fragile parce qu'elle repose sur **dix** erreurs : un seul point (le +7 %) la déplace, et les extrêmes (qui sont ce que l'on craint) n'y figurent pas.

### Corrigé 3.6

```python
y = np.array([1, 1, 1, 0, 0, 0]); s = np.array([0.8, 0.55, 0.35, 0.6, 0.4, 0.1])
print(O.auc_main(y, s), O.gain(y, s, (0.5,)).round(3).to_string(index=False))
```
<!--sortie-->
```text
0.6666666666666666  contactés  acheteurs captés  lift
       0.5             0.667 1.333
```

Couples (acheteur, non-acheteur) bien classés : P1 bat N1, N2, N3 (3) ; P2 (0,55) bat N2 et N3 mais pas N1 (0,6) (2) ; P3 (0,35) ne bat que N3 (1) : **6 sur 9, AUC = 0,67**. En contactant la moitié (les trois meilleurs scores : P1, N1, P2), on touche P1 et P2 : **2 acheteurs sur 3, soit 67 %** (lift de 1,33).

### Corrigé 3.7

(a) **Sûre** si elle est calculée sur les commandes antérieures à la coupure (c'est le principe). (b) **Fuite probable** : le statut est actualisé chaque nuit, donc lu **après** la coupure ; il peut encoder « n'a pas acheté depuis longtemps » ou même « a racheté ». On demande l'historique daté des statuts. (c) **Sûre** : fixe dans le passé. (d) **À vérifier** : si l'on compte des retours dont la date est postérieure à la coupure, c'est une **fuite** ; il faut filtrer sur `date_retour <= coupure`. (e) **Fuite** : l'enquête de 2025 est postérieure à la coupure de 2024, et seuls les clients qui ont commandé en 2025 y répondent. (f) **Sûre** : fixé à l'acquisition. (g) **Fuite** : le courrier n'a pas été envoyé avant la coupure, et il est **déclenché par** l'inactivité : il contient une information sur la cible.

### Corrigé 3.8

```python
seuil = 2 / (0.20 * 40)
sc = np.array([0.05, 0.12, 0.20, 0.24, 0.26, 0.31, 0.45, 0.52, 0.66, 0.80])
g = 0.20 * sc * 40 - 2
print(seuil, sc[g > 0], g[g > 0].round(2), g[g > 0].sum().round(2))
```
<!--sortie-->
```text
0.25 [0.26 0.31 0.45 0.52 0.66 0.8 ] [0.08 0.48 1.6  2.16 3.28 4.4 ] 12.0
```

Le gain attendu d'un contact est $0{,}20 \times p \times 40 - 2 = 8p - 2$, positif pour $p > 2/8 = 0{,}25$. On contacte les **six** clients de scores 0,26 ; 0,31 ; 0,45 ; 0,52 ; 0,66 ; 0,80, avec des gains de 0,08 ; 0,48 ; 1,60 ; 2,16 ; 3,28 ; 4,40 € : **12 € au total**. Les quatre autres, dont le client à 0,24 (gain −0,08 €), ne sont pas contactés.

### Corrigé 3.9

Un dossier possible (les chiffres viennent de la section 3.2) :

| Rubrique | Contenu |
|---|---|
| Question et décision | Combien de commandes le mois prochain ? Décision : capacité des équipes d'emballage, fixée un mois à l'avance. |
| Série et horizon | Commandes mensuelles, 36 mois (2023-2025) ; horizons de 1 et 3 mois. |
| Séparation | Origine glissante sur 2025 : 12 prévisions à 1 mois, 10 à 3 mois, chacune faite avec les données antérieures seulement. |
| Variables | Connues à l'avance : mois, jour de la semaine, tendance, calendrier des soldes (8-28 janvier, 24 juin-14 juillet, 22-30 novembre). **Exclues** : météo et publicité (inconnues à l'avance). |
| Références et métriques | Naïf (MAE 211), saisonnier (81), saisonnier × croissance (47), Holt-Winters (40). Régression de Poisson : MAE 35, MAPE 3,4 %, biais −14. |
| Ce qui a été essayé | Cinq méthodes ; seule la régression qui connaît le calendrier garde son erreur à trois mois (MAPE 3,4 %). |
| Contraintes | Prévision recalculée chaque début de mois ; deux scénarios (avec et sans soldes). |
| Critères de réussite | MAPE à un mois inférieure à 4 % sur les douze mois suivants, biais inférieur à 2 %, fourchette à 80 % couvrant au moins sept réalisations sur dix. |
| Risques et limites | 22 erreurs seulement pour la fourchette ; événements rares non couverts (panne, fermeture) ; hypothèse que le calendrier promotionnel ne change pas. |

### Corrigé 3.10

(a) **Ne pas passer la main** : peu de séries, des méthodes simples et un calendrier suffisent ; le gain d'un modèle plus puissant serait faible (section 3.3.2). (b) **Passer la main** : données **textuelles**, volume élevé, besoin de méthodes spécialisées. (c) **Passer la main** : décision en **temps réel**, volume, contrôle, surveillance et responsabilité. (d) **Ne pas passer la main** : décision trimestrielle, régression ou règle de gestion, explicable ; l'effort ne se justifie pas.

### Corrigé 3.11

```python
t = pd.DataFrame({"m": [0.742, 0.741, 0.739, 0.735, 0.744, 0.725], "sd": [0.010, 0.012, 0.006, 0.004, 0.015, 0.003]}, index=list("ABCDEF"))
print((t["m"] >= 0.744 - 0.015).to_dict())
```
<!--sortie-->
```text
{'A': True, 'B': True, 'C': True, 'D': True, 'E': True, 'F': False}
```

Le meilleur est E (0,744) avec un écart-type de 0,015 : le seuil de la règle est 0,729. **A, B, C, D, E** y sont, F (0,725) non. Parmi les cinq, **C (régression logistique)** est le plus simple et le plus explicable : on le choisit, avec 0,005 de moins que E, bien en dessous du bruit (0,015). **F est exclu** : tri par récence seule, c'est la référence naïve que tous les autres battent. Questions à l'outil : comment les plis sont-ils formés (dans le temps ?), la date de coupure est-elle fixée, une variable fuit-elle (E, un empilement, peut en cacher une), les probabilités sont-elles calibrées, le test final a-t-il été utilisé pour choisir ?

### Corrigé 3.12

Un message possible : « Merci pour la démonstration. Avant toute décision, nous avons besoin de savoir : (1) ce que signifie « départ » (une fenêtre datée, laquelle ?) ; (2) le taux de départs de la population : si seulement 6 % des clients partent, un modèle qui annonce **« personne ne part »** a 94 % d'exactitude, donc « 94 % de précision » **ne dit rien sans la référence** ; (3) la métrique de décision (rappel à 20 %, gain en euros, AUC), avec un **intervalle** ; (4) la façon dont les données sont séparées (dans le temps, avec une coupure fixée) ; (5) les variables utilisées et les mesures contre la **fuite d'information** ; (6) la **calibration** des probabilités ; (7) l'endroit où partent nos données et le **consentement** des clients ; (8) la surveillance en service et la possibilité de reproduire le résultat. Nous comparerons votre modèle à un tri par récence et à une régression logistique sur les mêmes données. » L'idée centrale : une exactitude se lit **contre le taux de base** ; sur une cible rare, elle est presque toujours élevée.

## Pistes des applications

*Les nombres cités viennent des exécutions ci-dessus.*

**Application 3.1.** Le coût annuel passe de 3 667 € sans marge à **2 081 € avec 3 %**, puis remonte (2 456 € à 4 %, 5 124 € à 8 %). Le quantile visé est 10 / 16 = 0,625 ; le 62,5e centile des erreurs relatives vaut 3,0 % : la **marge qui minimise le coût (3 %) retrouve la règle** du livre. La courbe est plate près du minimum (2 162 €, 2 081 €, 2 456 € pour 2, 3 et 4 %) parce qu'autour de l'optimum, les coûts d'un manque et d'un surplus se compensent presque : **l'exactitude de la marge compte peu, son ordre de grandeur compte beaucoup**. Avec ces coûts-là, le meilleur niveau de sécurité est plus bas qu'avec 12 € et 4 € (3,2 %, section 3.1.3), parce que l'écart entre les deux coûts est plus faible.

**Application 3.2.** À la semaine, la référence saisonnière × croissance se trompe de **8,4 %** en moyenne (MAE de 19,8 commandes pour 232 par semaine), la régression de Poisson de **5,3 %** (MAE de 12,3), avec un biais faible (−3 commandes par semaine). L'erreur **relative** est plus grande qu'au mois (4,5 % et 3,4 %) : plus le découpage est fin, plus le **hasard** d'une semaine pèse (un petit nombre de commandes se compense moins). La régression garde son avantage (près de 40 % d'erreur en moins que la référence), toujours grâce au calendrier. Moralité : on prévoit **au niveau où l'on décide**.

**Application 3.3.** Testée hors échantillon, la fourchette à 80 % ne couvre que **16 prévisions sur 22 (73 %)** : elle est **un peu trop étroite**, ce qui est normal quand on la fabrique avec peu d'erreurs (les extrêmes manquent). Celle à 95 % est plus large (918 à 1 053 pour 1 000) mais ses bornes extrêmes reposent sur une ou deux erreurs seulement : elles sont **instables**. On retient qu'avec 22 erreurs, on dit « environ huit sur dix » et l'on élargit un peu par prudence.

**Application 3.4.** Plus la fenêtre est longue, plus le taux de rachat monte (de 27 % à 62 % en 2025 entre 60 et 180 jours) et plus l'AUC monte (de 0,709 à 0,771) : sur une longue fenêtre, l'événement reflète surtout le **tempérament du client** (un acheteur régulier rachète presque toujours en six mois), donc il est plus facile à prédire ; mais il est aussi **moins utile**, car il n'aide pas à choisir qui contacter ce mois-ci. Pour une campagne qui demande trois semaines de préparation, une fenêtre de 60 à 90 jours est la plus parlante ; **l'AUC n'est pas comparable entre des cibles différentes**.

**Application 3.5.** La campagne perd de l'argent (marge attendue nulle : personne n'est à contacter) dès que l'effet est de **+5 %** pour un contact à 1,50 € ou plus, ou de +10 % pour un contact à 3 €. Elle rapporte jusqu'à 6 306 € si l'effet vaut +20 % pour 1 € le contact. La **valeur d'un essai** qui mesurerait l'effet est lisible dans la grille : entre « +5 % » (zéro) et « +20 % » (4 409 € à 1,50 €), l'incertitude sur l'effet change la décision et plusieurs milliers d'euros ; mesurer l'effet avant de lancer vaut donc au moins le coût de l'essai.

**Application 3.6.** Sur la paire de mars, la logistique (0,734) bat l'arbre (0,719) de **0,015 [0,009 ; 0,021]**, et le boosting (0,727) de **0,006 [−0,000 ; 0,012]**, un écart dont l'intervalle touche zéro. Les conclusions du livre se retrouvent : la régression n'est pas battue. Si le boosting gagnait de 0,003 avec un intervalle qui contient zéro, on **ne passerait pas la main** pour cela : ce serait chercher du bruit ; on irait plutôt chercher de nouvelles variables.

**Application 3.7.** Les entrées dérivent peu (au plus 0,27 écart-type) et l'AUC reste entre 0,72 et 0,75 : **ni l'alerte des entrées ni celle de l'AUC ne se déclenchent**. Seule l'alerte de **calibration** se déclenche, à la coupure du 30 septembre 2025 (9,4 points d'écart : 39,2 % annoncés, 48,6 % observés). C'est une dérive **saisonnière** et **connue** (la hausse de fin d'année), pas une dégradation du modèle : on la traite en ajoutant le trimestre comme variable (section 3.3.4), pas en ré-entraînant d'urgence. Le message au propriétaire : « le classement des clients reste bon ; les probabilités sous-estiment les rachats d'octobre à décembre de près de dix points ; utiliser la version qui connaît la saison pour tout calcul de coût. »

**Application 3.8.** Le premier du classement est un boosting (validation 0,7341 ; test 0,7321) ; **neuf configurations sur douze** sont à moins d'un écart-type de lui (0,0056). La plus simple est une régression logistique (validation 0,7291, test 0,7273) : elle perd **0,005** au test sur le premier, un écart sans commune mesure avec ce que coûterait de maintenir un boosting. On y gagne l'**explicabilité** (des coefficients à lire), la **stabilité** et une **surveillance** plus simple. Un autre tirage au sort de douze configurations donnerait un autre premier : c'est le message de la section 3.4.3.
