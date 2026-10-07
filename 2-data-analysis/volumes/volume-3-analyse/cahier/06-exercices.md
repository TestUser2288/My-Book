# Chapitre 6 : Conception de KPI et cadres d'indicateurs — exercices et applications

> 🧭 Ce cahier prolonge le chapitre 6 : on y **écrit** des fiches d'indicateurs, on y **calcule** les pièges de définition, on **décompose** des chiffres en arbres, on **mesure** la précision d'un budget, et l'on trace des **cartes de contrôle**. Le cahier est autonome : chaque chapitre du cahier recharge ses données. Les données sont **simulées** et les références du secteur **fictives**.

```python
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch06 as O
d = O.charger(os.environ["DONNEES"])
x = d["x"]; x24, x25 = x[x["annee"] == 2024], x[x["annee"] == 2025]
print("lignes :", len(x), "| sessions :", len(d["sess"]), "| livraisons :", len(d["liv"]))
```
<!--sortie-->
```text
lignes : 83905 | sessions : 127022 | livraisons : 19420
```

## Applications

### Application 6.1 — Une fiche et un calcul unique (section 6.1)

**Objectif.** Écrire la fiche d'un indicateur, puis vérifier que trois outils donnent le même chiffre.

**Étape 1 — la fiche.** On la range dans un dictionnaire : c'est déjà un début de dictionnaire de KPI.

```python
fiche = {"nom": "Panier moyen", "formule": "CA TTC / commandes distinctes", "perimetre": "tous canaux, commandes de la période",
         "periode": "mois de la commande", "source": "lignes_commande, commandes", "proprietaire": "la gérante", "frequence": "mensuelle",
         "sens_favorable": "à la hausse", "contre_indicateur": "chiffre d'affaires", "limites": "sensible aux promotions et au mix de canaux"}
print(pd.Series(fiche).to_string())
```
<!--sortie-->
```text
nom                                                 Panier moyen
formule                            CA TTC / commandes distinctes
perimetre                   tous canaux, commandes de la période
periode                                      mois de la commande
source                                lignes_commande, commandes
proprietaire                                          la gérante
frequence                                              mensuelle
sens_favorable                                       à la hausse
contre_indicateur                             chiffre d'affaires
limites              sensible aux promotions et au mix de canaux
```

**Étape 2 — trois calculs.** pandas, DuckDB (SQL) et un calcul « à la main » sur les sommes.

```python
import duckdb
D = os.environ["DONNEES"]
pd_ = x25["montant"].sum() / x25["id_commande"].nunique()
sql = duckdb.sql(f"select sum(l.montant) / count(distinct c.id_commande) from read_csv_auto('{D}/lignes_commande.csv') l join read_csv_auto('{D}/commandes.csv') c using (id_commande) where c.date_commande >= '2025-01-01'").fetchone()[0]
print("pandas :", round(pd_, 2), "| SQL :", round(sql, 2), "| fonction du chapitre :", round(O.kpis(d, 2025)["Panier moyen (€)"], 2))
```
<!--sortie-->
```text
pandas : 102.33 | SQL : 102.33 | fonction du chapitre : 102.33
```

**À vous.** Écrivez la fiche du **taux de conversion du site** : quel est le dénominateur ? Une session qui ajoute un article au panier sans commander compte-t-elle ? Calculez-le avec pandas et avec DuckDB.

### Application 6.2 — Les pièges de définition (section 6.1)

**Objectif.** Constater qu'un même mot recouvre plusieurs chiffres.

**Étape 1 — le taux de retour, trois définitions, par canal.**

```python
def trois_taux(g):
    par_cmd = g.groupby("id_commande")["retourne"].max()
    return pd.Series({"lignes (%)": g["retourne"].mean() * 100, "commandes (%)": par_cmd.mean() * 100, "euros (%)": g.loc[g["retourne"], "montant"].sum() / g["montant"].sum() * 100})
print(x25.groupby("canal").apply(trois_taux).round(2).to_string())
```
<!--sortie-->
```text
          lignes (%)  commandes (%)  euros (%)
canal                                         
Boutique        3.32           7.44       3.29
Réseaux         6.93          15.01       6.46
Site            8.82          18.87       9.16
```

**Étape 2 — la moyenne des moyennes.** Comparez la moyenne simple des trois taux « lignes » au taux global.

```python
rc = x25.groupby("canal")["retourne"].agg(["mean", "size"])
print("moyenne simple :", round(rc["mean"].mean() * 100, 2), "| pondérée par les lignes :", round((rc["mean"] * rc["size"]).sum() / rc["size"].sum() * 100, 2))
```
<!--sortie-->
```text
moyenne simple : 6.36 | pondérée par les lignes : 6.29
```

**À vous.** Le taux de retour est-il plus élevé le Site que la Boutique **dans chaque catégorie** ? Calculez-le par canal et catégorie : un effet de mix est-il possible ?

### Application 6.3 — Un arbre pour la marge (section 6.2)

**Objectif.** Décomposer l'écart de marge entre deux années et voir l'effet d'une convention.

**Étape 1 — les facteurs.**

```python
def facteurs(g):
    n = g["id_commande"].nunique(); ca = g["montant"].sum()
    return n, ca / 1.2 / n, g["marge_ht"].sum() / (ca / 1.2)
(n0, h0, t0), (n1, h1, t1) = facteurs(x24), facteurs(x25)
print("2024 :", n0, round(h0, 2), round(t0 * 100, 2), "| 2025 :", n1, round(h1, 2), round(t1 * 100, 2))
```
<!--sortie-->
```text
2024 : 12031 82.39 36.17 | 2025 : 12946 85.27 37.96
```

**Étape 2 — deux conventions.** Valoriser les effets dans l'ordre (commandes, panier, taux) ou dans l'ordre inverse.

```python
ordre1 = ((n1 - n0) * h0 * t0, n1 * (h1 - h0) * t0, n1 * h1 * (t1 - t0))
ordre2 = ((n1 - n0) * h1 * t1, n0 * (h1 - h0) * t1, n0 * h0 * (t1 - t0))
print("ordre 1 :", [round(v) for v in ordre1], "| somme", round(sum(ordre1)))
print("ordre 2 :", [round(v) for v in ordre2], "| somme", round(sum(ordre2)))
```
<!--sortie-->
```text
ordre 1 : [27270, 13517, 19662] | somme 60450
ordre 2 : [29615, 13180, 17654] | somme 60450
```

**À vous.** Les deux conventions donnent la **même somme** mais des **parts différentes**. Pourquoi ? Quelle convention vous semble la plus naturelle pour un lecteur non spécialiste, et comment l'écririez-vous dans une note ?

### Application 6.4 — Entonnoir et cadre AARRR (section 6.2)

**Objectif.** Localiser l'étape du parcours où l'on perd le plus selon l'appareil et le type de visiteur.

```python
s = d["sess"]
for col in ["appareil", "nouveau_visiteur"]:
    f = s.groupby(col)[["ajout_panier", "debut_paiement", "commande"]].mean().mul(100).round(1)
    f["paiement → commande (%)"] = (f["commande"] / f["debut_paiement"] * 100).round(0)
    print(f.to_string(), "\n")
```
<!--sortie-->
```text
            ajout_panier  debut_paiement  commande  paiement → commande (%)
appareil                                                                   
mobile              14.3             8.2       4.8                     59.0
ordinateur          14.1             8.1       4.7                     58.0
tablette            14.4             8.0       4.8                     60.0 

                  ajout_panier  debut_paiement  commande  paiement → commande (%)
nouveau_visiteur                                                                 
0                         14.6             8.5       5.0                     59.0
1                         14.0             7.9       4.5                     57.0 
```

**À vous.** Y a-t-il un appareil ou un type de visiteur à traiter en priorité ? Que répondez-vous à la gérante si les écarts entre groupes sont de l'ordre du bruit (comparez-les à ce que le hasard produit sur de tels effectifs) ?

### Application 6.5 — Références et budget (section 6.3)

**Objectif.** Mesurer la précision du budget par catégorie et en déduire une tolérance.

```python
b = d["budget"]
cat = b.groupby("categorie")[["ca_budget", "ca_reel"]].sum()
cat["écart (%)"] = (cat["ca_reel"] / cat["ca_budget"] - 1) * 100
mois_cat = b.groupby(["mois", "categorie"])[["ca_budget", "ca_reel"]].sum()
ecart = (mois_cat["ca_reel"] / mois_cat["ca_budget"] - 1) * 100
cat["écart-type mensuel (pts)"] = ecart.groupby("categorie").std()
print(cat[["écart (%)", "écart-type mensuel (pts)"]].round(1).to_string())
print("tolérance proposée (2 écarts-types, toutes catégories) :", round(2 * ecart.std(), 1), "%")
```
<!--sortie-->
```text
            écart (%)  écart-type mensuel (pts)
categorie                                      
Bien-être         6.5                      11.2
Cuisine           3.7                       7.1
Décoration       -3.9                      10.5
Jardin            8.4                       9.8
Maison            3.7                      12.7
Papeterie         4.9                      10.8
tolérance proposée (2 écarts-types, toutes catégories) : 21.3 %
```

**À vous.** Une alerte « écart au budget supérieur à 5 % » sur une catégorie et un mois s'allumerait combien de fois sur 72 cases (12 mois × 6 catégories) ? Quelle tolérance retiendriez-vous pour une alerte qui s'allume environ une fois sur vingt ?

### Application 6.6 — Cartes de contrôle et tableau de bord (section 6.3)

**Objectif.** Appliquer la carte de contrôle à un autre indicateur et résumer l'état des indicateurs hebdomadaires.

```python
sh = O.seuils_hebdo(d)
print(pd.DataFrame(sh).T[["p", "orange", "rouge", "n"]].round(1).to_string())
```
<!--sortie-->
```text
                            p  orange  rouge       n
Taux de retour (lignes)   6.3     8.3    9.3   568.2
Livraisons à l'heure     78.2    71.1   67.5   134.0
Conversion du site        4.8     3.9    3.5  2396.6
Rupture de stock          7.2    11.6   13.8   139.2
```

Statut de la **dernière semaine complète** pour chaque indicateur (z calculé avec l'effectif de la semaine) :

```python
def dernier_statut(w, p, sens, k=(2, 3)):
    ligne = w.iloc[-1]; z = (ligne["mean"] - p) / np.sqrt(p * (1 - p) / ligne["size"]) * sens
    return round(float(ligne["mean"]) * 100, 1), round(float(z), 1), "vert" if z > -k[0] else ("orange" if z > -k[1] else "rouge")
liv = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].assign(ok=lambda t: 1 - t["retard"])
wl = O.semaines(liv, "date_commande", "ok"); wl = wl[wl["size"] >= 100]
print("livraisons à l'heure, dernière semaine retenue :", wl.index[-1].date(), dernier_statut(wl, sh["Livraisons à l'heure"]["p"] / 100, 1))
```
<!--sortie-->
```text
livraisons à l'heure, dernière semaine retenue : 2025-12-22 (44.7, -13.2, 'rouge')
```

**À vous.** Faites de même pour la **conversion du site** et la **rupture de stock** (elles figurent dans `sh`). Quelle semaine est la plus mal classée sur chacune ?

## Exercices

### Exercice 6.1 ⭐ — Quel chiffre garder ? (section 6.1.1)

Pour chacun des chiffres suivants, dites s'il s'agit d'un indicateur de **pilotage**, de **résultat**, de **contexte** ou **à supprimer**, et justifiez en une phrase : (a) le nombre de pages vues du site ; (b) le chiffre d'affaires du mois ; (c) le taux de livraisons à l'heure de la semaine ; (d) le nombre de clients inscrits à la lettre d'information ; (e) la marge brute du trimestre ; (f) le délai moyen d'expédition de la semaine.

### Exercice 6.2 ⭐ — Une fiche pour le taux de rupture (section 6.1.2)

Rédigez la fiche du **taux de rupture de stock** (nom, décision liée, formule, périmètre, période, source, propriétaire, fréquence, sens favorable, limite). La table `stock_quotidien.csv` suit 20 produits : quel est le **dénominateur** naturel ? Calculez le taux pour 2025 avec votre définition.

### Exercice 6.3 ⭐ — La moyenne des moyennes (section 6.1.5)

Deux canaux : le premier a 200 commandes et 5 % de retours, le second 800 commandes et 1 % de retours. (a) Quelle est la moyenne simple des deux taux ? (b) Quel est le taux global ? (c) Retrouvez-le avec `numpy.average` et des poids.

### Exercice 6.4 ⭐⭐ — Cibler un indicateur sans le casser (section 6.1.6)

La gérante veut « 90 % de livraisons à l'heure ». Un transporteur propose de passer le **délai promis** de 6 à 8 jours. Avec les dates de commande et de livraison de `livraisons.csv` (2025), calculez le taux de livraisons à l'heure pour des délais promis de 6, 7, 8, 9 et 10 jours. Que vaut l'objectif de 90 % dans ces conditions ? Quel contre-indicateur proposez-vous ?

### Exercice 6.5 ⭐⭐ — Le « client actif » (section 6.1.5)

Calculez, sur les 6 000 clients, la part de « clients actifs » selon trois définitions : au moins une commande dans les 12 derniers mois de 2025, au moins une commande dans les 6 derniers mois, au moins deux commandes dans l'année. Concluez sur le besoin d'une définition unique.

### Exercice 6.6 ⭐⭐ — Décomposer le panier moyen (section 6.2.2)

Le panier moyen est le produit du nombre moyen de **lignes par commande** par le **montant moyen d'une ligne**. Vérifiez l'égalité en 2024 et en 2025, puis répartissez la hausse du panier moyen entre ces deux facteurs.

### Exercice 6.7 ⭐⭐ — Prix, volume et mix par catégorie (section 6.2.3)

Pour chaque catégorie, calculez la variation de chiffre d'affaires entre 2024 et 2025 et séparez un **effet quantité** et un **effet prix moyen** (prix moyen = chiffre d'affaires ÷ quantités). Quelle catégorie a le plus augmenté ses prix moyens ? Quelle part de cette hausse vient d'un changement de **mix** à l'intérieur de la catégorie, plutôt que d'une hausse de prix catalogue (qui est de 3 % au 1er janvier 2025 pour tous les produits) ?

### Exercice 6.8 ⭐⭐⭐ — Un OKR sur les ruptures (sections 6.2.4 et 6.3.1)

Rédigez un objectif et deux résultats clés pour réduire les ruptures de stock. Avec `stock_quotidien.csv`, calculez le taux de rupture par produit : combien de produits expliquent la moitié des jours de rupture ? Si les cinq pires produits avaient le taux de la médiane des autres, quel serait le taux global ? Cette cible est-elle atteignable avec ce seul levier ?

### Exercice 6.9 ⭐ — Lire un benchmark (section 6.3.2)

À partir de `O.position_secteur(d)`, listez les indicateurs « meilleurs », « dans la norme » et « moins bons ». Pour deux d'entre eux, citez une raison pour laquelle la comparaison pourrait être **trompeuse** (définition, périmètre, saison).

### Exercice 6.10 ⭐⭐ — La précision du budget par canal (section 6.3.3)

Calculez l'écart mensuel au budget par canal (Boutique, Site, Réseaux) et son écart-type. Quel canal est le plus difficile à prévoir ? Quelle tolérance mensuelle proposez-vous pour chaque canal ?

### Exercice 6.11 ⭐⭐ — Bruit d'un taux de rupture (section 6.3.4)

Pour un taux de rupture hebdomadaire de 7,2 % sur 140 produit-jours, quel est l'écart-type du bruit ? Simulez 100 000 semaines à taux constant : quelle part s'écarte de plus de 2 points ? Comparez à l'écart-type observé des taux hebdomadaires de 2025.

### Exercice 6.12 ⭐⭐⭐ — Une carte de contrôle de la conversion (section 6.3.5)

Tracez (ou calculez) la carte de contrôle de la **conversion hebdomadaire** du site en 2025, avec des limites à ±3 écarts-types fondées sur les 40 premières semaines. Combien de semaines sortent des limites ? Si certaines sortent, proposez une explication à vérifier (saison, source de trafic) et dites si le signal serait **actionnable**.

## Corrigés

### Corrigé 6.1

(a) **À supprimer** ou à reléguer en contexte : aucune décision ne dépend d'un nombre de pages vues seul. (b) **Résultat** : à suivre chaque mois, il arrive tard. (c) **Pilotage** : une baisse déclenche un appel au transporteur. (d) **À supprimer** ou **à remplacer** par les clients actifs : un nombre d'inscrits cumulé ne baisse jamais. (e) **Résultat**. (f) **Pilotage** : un délai d'expédition qui s'allonge annonce des retards de livraison.

### Corrigé 6.2

```python
st = d["stock"]
print("produit-jours :", len(st), "| jours de rupture :", int(st["rupture"].sum()), "| taux :", round(st["rupture"].mean() * 100, 2), "%")
```
<!--sortie-->
```text
produit-jours : 7300 | jours de rupture : 537 | taux : 7.36 %
```

Fiche : **nom** : taux de rupture ; **décision** : passer commande plus tôt, changer de fournisseur ; **formule** : produit-jours où la demande dépasse le stock ÷ produit-jours ; **périmètre** : 20 produits principaux ; **période** : semaine ; **source** : `stock_quotidien` ; **propriétaire** : responsable des achats ; **fréquence** : hebdomadaire ; **sens favorable** : à la baisse ; **limite** : ne mesure pas la **demande perdue** (la quantité manquante) ni les produits hors des 20 principaux. Le dénominateur naturel est le nombre de **produit-jours** (20 × 365 = 7 300).

### Corrigé 6.3

```python
print("moyenne simple :", (5 + 1) / 2, "% | taux global :", round((200 * 0.05 + 800 * 0.01) / 1000 * 100, 2), "% | numpy :", round(float(np.average([5, 1], weights=[200, 800])), 2))
```
<!--sortie-->
```text
moyenne simple : 3.0 % | taux global : 1.8 % | numpy : 1.8
```

La moyenne simple (3 %) **surestime** le taux global (1,8 %) : le canal qui compte le plus a le taux le plus faible. On pondère par les dénominateurs.

### Corrigé 6.4

```python
l = d["liv"][d["liv"]["date_commande"] >= "2025-01-01"].copy()
duree = (pd.to_datetime(l["date_livraison"]) - pd.to_datetime(l["date_commande"])).dt.days
print({j: round(float((duree <= j).mean()) * 100, 1) for j in (6, 7, 8, 9, 10)})
```
<!--sortie-->
```text
{6: 73.5, 7: 89.1, 8: 96.3, 9: 98.9, 10: 99.7}
```

Avec 6 jours promis, 73,5 % des colis arrivent à l'heure ; avec 7 jours, 89,1 % ; avec 8 jours, 96,3 %. L'objectif de 90 % est donc « atteint » dès que l'on promet **un peu plus de sept jours**, sans qu'aucun colis n'arrive plus tôt. Le taux grimpe mécaniquement avec le délai promis : allonger la promesse fait « gagner » l'indicateur **sans que rien ne change pour le client**, qui attend davantage. C'est la loi de Goodhart. Un bon contre-indicateur : le **délai moyen réel** de livraison ou le taux de retours « livraison tardive ».

### Corrigé 6.5

```python
c = d["cmd"]; c25 = c[c["date_commande"] >= "2025-01-01"]
actifs12 = c25["id_client"].nunique()
actifs6 = c25[c25["date_commande"] >= "2025-07-01"]["id_client"].nunique()
deux = int((c25.groupby("id_client").size() >= 2).sum())
print("12 mois :", actifs12, round(actifs12 / 6000 * 100, 1), "% | 6 mois :", actifs6, round(actifs6 / 6000 * 100, 1), "% | au moins deux commandes :", deux, round(deux / 6000 * 100, 1), "%")
```
<!--sortie-->
```text
12 mois : 3875 64.6 % | 6 mois : 3156 52.6 % | au moins deux commandes : 2654 44.2 %
```

Trois définitions, trois chiffres très différents (64,6 %, 52,6 % et 44,2 %) : la définition doit être **écrite une fois** dans le glossaire et utilisée partout.

### Corrigé 6.6

```python
def lpc(g):
    n = g["id_commande"].nunique(); return len(g) / n, g["montant"].sum() / len(g), g["montant"].sum() / n
(l0, m0, p0), (l1, m1, p1) = lpc(x24), lpc(x25)
print("2024 :", round(l0, 3), "x", round(m0, 2), "=", round(l0 * m0, 2), "| 2025 :", round(l1, 3), "x", round(m1, 2), "=", round(l1 * m1, 2))
print("hausse du panier :", round(p1 - p0, 2), "€ = lignes", round((l1 - l0) * m0, 2), "+ montant par ligne", round(l1 * (m1 - m0), 2))
```
<!--sortie-->
```text
2024 : 2.3 x 42.98 = 98.87 | 2025 : 2.304 x 44.41 = 102.33
hausse du panier : 3.46 € = lignes 0.16 + montant par ligne 3.3
```

Les deux facteurs valent 2,300 lignes par commande et 42,98 € par ligne en 2024, 2,304 et 44,41 € en 2025 : leur produit redonne 98,87 € et 102,33 €. Sur les 3,46 € de hausse du panier, **0,16 € seulement** viennent d'un plus grand nombre de lignes par commande ; **3,30 € viennent du montant par ligne**. Les clients n'achètent pas plus d'articles, ils achètent des articles plus chers (prix catalogue en hausse de 3 % au 1er janvier 2025, et mix).

### Corrigé 6.7

```python
a = x24.groupby("categorie").agg(ca0=("montant", "sum"), q0=("quantite", "sum")); b = x25.groupby("categorie").agg(ca1=("montant", "sum"), q1=("quantite", "sum"))
t = a.join(b); t["p0"], t["p1"] = t["ca0"] / t["q0"], t["ca1"] / t["q1"]
t["effet quantité"] = (t["q1"] - t["q0"]) * t["p0"]; t["effet prix moyen"] = t["q1"] * (t["p1"] - t["p0"]); t["hausse prix moyen (%)"] = (t["p1"] / t["p0"] - 1) * 100
print(t[["effet quantité", "effet prix moyen", "hausse prix moyen (%)"]].round(1).to_string())
```
<!--sortie-->
```text
            effet quantité  effet prix moyen  hausse prix moyen (%)
categorie                                                          
Bien-être           6668.7            3524.8                    3.1
Cuisine             9130.7            6996.7                    3.1
Décoration         17268.1            6400.9                    2.5
Jardin             30096.1           14148.6                    4.2
Maison             27192.3            8822.2                    3.0
Papeterie           3417.8            1635.8                    3.0
```

Le **Jardin** a la plus forte hausse de prix moyen (+4,2 %) : comme le prix catalogue a augmenté de 3 %, environ **1,2 point** vient du **mix** (références plus chères au sein de la catégorie) ou de remises moindres. À l'inverse, la **Décoration** (+2,5 %) est en dessous des 3 % de prix catalogue : son mix s'est déplacé vers des références moins chères. Les autres catégories (entre +3,0 % et +3,1 %) suivent le prix catalogue : leur hausse est surtout un effet **prix**.

### Corrigé 6.8

```python
st = d["stock"]; r = st.groupby("id_produit")["rupture"].sum().sort_values(ascending=False)
moitie = int((r.cumsum() / r.sum() < 0.5).sum() + 1)
pires = r.index[:5]; med = st[~st["id_produit"].isin(pires)].groupby("id_produit")["rupture"].mean().median()
nouveau = (st[~st["id_produit"].isin(pires)]["rupture"].sum() + med * st[st["id_produit"].isin(pires)].shape[0]) / len(st)
print("produits expliquant la moitié des ruptures :", moitie, "| taux actuel :", round(st["rupture"].mean() * 100, 2), "% | si les 5 pires étaient à la médiane :", round(nouveau * 100, 2), "%")
```
<!--sortie-->
```text
produits expliquant la moitié des ruptures : 9 | taux actuel : 7.36 % | si les 5 pires étaient à la médiane : 6.86 %
```

Exemple d'OKR : **objectif** « Ne plus manquer nos produits phares » ; **RC1** taux de rupture de 7,4 % à 4 % (la médiane du secteur) ; **RC2** aucun produit à plus de 10 % de rupture. Neuf produits sur vingt expliquent la moitié des jours de rupture, mais ramener les cinq pires à la médiane des autres ne fait passer le taux global que de **7,4 % à 6,9 %** : ce levier **ne suffit pas** à atteindre 4 %. Il faut un second levier : délais des fournisseurs, point de commande (chapitre 11).

### Corrigé 6.9

```python
pos = O.position_secteur(d); print(pos.groupby("position")["indicateur"].apply(list).to_string())
```
<!--sortie-->
```text
position
dans la norme    [Taux de marge brute (HT, %), Taux de retour (...
meilleur         [Taux de conversion du site (%), Clients actif...
moins bon        [Taux de rupture de stock (%), Livraisons à l'...
à interpréter                     [Frais de personnel / CA HT (%)]
```

Quelques raisons de prudence : la **conversion** dépend de la définition d'une session et de la qualité du trafic ; le **coût d'acquisition** dépend de ce que l'on compte dans les dépenses et de ce qu'est un client « nouveau » ; la part du **site** dans le chiffre d'affaires dépend de l'activité des autres canaux. Les valeurs du secteur sont, de plus, **inventées**.

### Corrigé 6.10

```python
bc = d["budget"].groupby(["mois", "canal"])[["ca_budget", "ca_reel"]].sum()
ec = ((bc["ca_reel"] / bc["ca_budget"] - 1) * 100).groupby("canal")
print(pd.DataFrame({"moyenne (%)": ec.mean(), "écart-type (pts)": ec.std(), "tolérance 2 écarts-types (%)": 2 * ec.std()}).round(1).to_string())
```
<!--sortie-->
```text
          moyenne (%)  écart-type (pts)  tolérance 2 écarts-types (%)
canal                                                                
Boutique         -6.2               8.9                          17.9
Réseaux           4.3              19.3                          38.6
Site             16.0              12.8                          25.6
```

Le canal **Réseaux** est le plus difficile à prévoir (écart-type de 19,3 points, donc une tolérance de ±39 %), devant le Site (12,8 points, ±26 %) et la Boutique (8,9 points, ±18 %). Notez aussi les **moyennes** : le budget a **sous-estimé le Site de 16 %** et **surestimé la Boutique de 6 %** en moyenne, c'est-à-dire qu'il n'a pas anticipé le déplacement des ventes vers le site. Une tolérance symétrique autour d'un budget biaisé produit de fausses alertes d'un côté et en masque de l'autre : il faut d'abord **corriger le biais**.

### Corrigé 6.11

```python
rng = np.random.default_rng(11); n, p = 140, 0.072
sim = (rng.binomial(n, p, 100000) / n - p) * 100
print("écart-type du bruit :", round(float(np.sqrt(p * (1 - p) / n) * 100), 2), "pts | part à plus de 2 points :", round((abs(sim) > 2).mean() * 100, 1), "%")
sw = O.semaines(d["stock"].assign(date=d["stock"]["date"]), "date", "rupture"); sw = sw[sw["size"] >= 100]
print("écart-type observé :", round(sw["mean"].std() * 100, 2), "pts sur", len(sw), "semaines")
```
<!--sortie-->
```text
écart-type du bruit : 2.18 pts | part à plus de 2 points : 41.2 %
écart-type observé : 7.18 pts sur 52 semaines
```

Le bruit d'une semaine de 140 produit-jours vaut 2,2 points : **un voyant à ±2 points s'allumerait environ deux semaines sur cinq (41 %)** sans aucune cause. L'écart-type **observé** des taux hebdomadaires de 2025 est de **7,2 points**, plus de trois fois celui du bruit : la rupture n'est donc pas stable, elle monte nettement en fin d'année ; ici, la variabilité observée dépasse largement le hasard, il y a un **signal** à instruire.

### Corrigé 6.12

```python
cw = O.semaines(d["sess"], "date", "commande"); cw = cw[cw["size"] >= 500]
base = cw.iloc[:40]; pb = base["sum"].sum() / base["size"].sum()
lo, hi = O.limites_p(pb, cw["size"])
hors = cw[(cw["mean"] < lo) | (cw["mean"] > hi)]
print("centre :", round(pb * 100, 2), "% | semaines :", len(cw), "| hors limites :", len(hors), [str(i.date()) for i in hors.index][:6])
```
<!--sortie-->
```text
centre : 4.49 % | semaines : 53 | hors limites : 6 ['2025-09-29', '2025-11-24', '2025-12-01', '2025-12-08', '2025-12-15', '2025-12-22']
```

Le centre est à 4,5 % ; **6 semaines sur 53** sortent des limites : la semaine du 29 septembre et les **cinq dernières semaines de l'année** (24 novembre au 22 décembre). La conversion monte donc en fin d'année : c'est un **effet saisonnier** (les commandes sont portées par la saison et le vendredi noir) et non une dérive à corriger. Une carte de contrôle sur un indicateur saisonnier doit être **calculée par saison** ou sur la comparaison à l'an dernier ; un signal n'est actionnable que s'il est **recoupé** (par source de trafic, par période de promotion) avant toute décision.

## Pistes des applications

Quelques pistes pour les « À vous » des applications.

**Application 6.1 (conversion).** Le dénominateur est le nombre de **sessions** ; une session qui ajoute un article sans commander compte au dénominateur, pas au numérateur.

```python
sess = d["sess"]
print("pandas :", round(sess["commande"].mean() * 100, 3), "% | SQL :", round(duckdb.sql(f"select 100.0 * sum(commande) / count(*) from read_csv_auto('{D}/sessions_web.csv')").fetchone()[0], 3), "%")
```
<!--sortie-->
```text
pandas : 4.785 % | SQL : 4.785 %
```

**Application 6.2 (retours par canal et catégorie).** On cherche un effet de mix : si le Site vend plus de catégories à fort retour, son taux global est tiré vers le haut.

```python
t = x25.groupby(["categorie", "canal"])["retourne"].mean().unstack().mul(100).round(1)
t["Site - Boutique (pts)"] = (t["Site"] - t["Boutique"]).round(1)
print(t.to_string())
```
<!--sortie-->
```text
canal       Boutique  Réseaux  Site  Site - Boutique (pts)
categorie                                                 
Bien-être        3.4      9.1   8.2                    4.8
Cuisine          3.7      5.4   8.6                    4.9
Décoration       3.4      6.7   8.8                    5.4
Jardin           3.2      5.9  10.0                    6.8
Maison           3.2      7.4   8.9                    5.7
Papeterie        3.0      7.8   8.3                    5.3
```

Le Site est au-dessus de la Boutique **dans chaque catégorie** : l'écart global ne vient donc pas d'un effet de mix mais d'un comportement propre au canal (on ne peut pas essayer un produit commandé en ligne).

**Application 6.3 (conventions).** Les deux ordres donnent la même somme parce que la décomposition est **exhaustive** (chaque convention répartit exactement l'écart total), mais le « terme croisé » (l'effet simultané du volume et du prix) est attribué différemment : au volume ou au prix selon l'ordre. Convention la plus lisible : valoriser le **volume au prix de départ**, puis le prix au volume d'arrivée, et l'écrire en une phrase dans la note.

**Application 6.5 (alertes à 5 %).**

```python
mc = d["budget"].groupby(["mois", "categorie"])[["ca_budget", "ca_reel"]].sum(); e = (mc["ca_reel"] / mc["ca_budget"] - 1) * 100
print("cases hors ±5 % :", int((e.abs() > 5).sum()), "sur", len(e), "| écart absolu au 95e centile :", round(float(e.abs().quantile(0.95)), 1), "%")
```
<!--sortie-->
```text
cases hors ±5 % : 46 sur 72 | écart absolu au 95e centile : 20.1 %
```

Une alerte à ±5 % s'allume sur **46 cases sur 72 (64 %)** : autant dire en permanence. Pour qu'elle ne s'allume qu'**une fois sur vingt**, il faut une tolérance de l'ordre du 95e centile des écarts absolus, soit **20,1 %** : à cette échelle de détail (mois × catégorie), le budget n'est pas un instrument de pilotage fin.

**Application 6.6 (conversion et rupture).**

```python
st = d["stock"]; wr = O.semaines(st, "date", "rupture"); wr = wr[wr["size"] >= 100]
wc = O.semaines(d["sess"], "date", "commande"); wc = wc[wc["size"] >= 500]
for nom, w, sens in [("rupture", wr, -1), ("conversion", wc, 1)]:
    p = w["sum"].sum() / w["size"].sum(); z = (w["mean"] - p) / np.sqrt(p * (1 - p) / w["size"]) * sens
    print(nom, "| pire semaine :", w.index[z.argmin()].date(), "| z =", round(float(z.min()), 1), "| semaines rouges (z < -3) :", int((z < -3).sum()), "sur", len(w))
```
<!--sortie-->
```text
rupture | pire semaine : 2025-12-22 | z = -12.7 | semaines rouges (z < -3) : 6 sur 52
conversion | pire semaine : 2025-08-25 | z = -3.4 | semaines rouges (z < -3) : 2 sur 53
```

Pour ces deux indicateurs, la valeur centrale est calculée **sur toute l'année**, ce qui est une **faute de méthode** (6.3.5) quand une rupture de tendance existe en fin d'année : les limites sont déformées. Refaites le calcul en ne gardant que les semaines d'avant novembre pour la valeur centrale.
