# Chapitre 4 : Segmentation et analyse de cohortes — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 4 du livre. Les **applications** sont de petites études guidées sur les clients de la boutique : chacune annonce un objectif, avance par étapes courtes (au plus vingt-cinq lignes par bloc) et se termine par une lecture et une invitation à aller plus loin. Les **exercices** vont de ⭐ (application directe) à ⭐⭐⭐ (à réfléchir) ; chacun renvoie à la section du livre qui l'éclaire. Les **corrigés** montrent un calcul à la main quand il est court, puis le code. Les données sont **simulées**.

Une seule cellule charge les bibliothèques et les tables ; les autres cellules en dépendent.

```python
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import outils_ch04 as O          # fonctions du livre, regroupées (voir build/outils_ch04.py)
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
T = O.charger()
cli, cmd, lig, prod, sess = T["cli"], T["cmd"], T["lig"], T["prod"], T["sess"]
g = O.table_clients(cmd, lig)            # une ligne par client ayant commandé (4 806 clients) au 31/12/2025
print(len(cli), "clients |", len(g), "ont commandé |", len(cmd), "commandes |", len(sess), "sessions")
```
<!--sortie-->
```text
6000 clients | 4806 ont commandé | 36395 commandes | 127022 sessions
```

## Applications

### Application 4.1 — Des segments par canal et fidélité (section 4.1)

**Objectif.** Construire des segments par règles à partir du canal dominant et de la carte de fidélité, puis comparer leur chiffre d'affaires par client, sans conclure trop vite.

**Étape 1 — le canal dominant.** Un client est « Site » si au moins 70 % de ses commandes passent par le site, « Boutique » si au plus 30 %, « Mixte » sinon.

```python
g["canal_dominant"] = np.select([g["site"] >= 0.7, g["site"] <= 0.3], ["Site", "Boutique"], "Mixte")
g["fidelite"] = g.index.map(cli.set_index("id_client")["fidelite"])
print(g["canal_dominant"].value_counts().to_dict())
```
<!--sortie-->
```text
{'Mixte': 2603, 'Boutique': 1499, 'Site': 704}
```

**Étape 2 — comparer.** Le chiffre d'affaires moyen par client et la part de clients, selon le canal dominant et la carte.

```python
t = g.groupby(["canal_dominant", "fidelite"]).agg(clients=("n", "size"), commandes=("n", "mean"), ca=("ca", "mean"))
print(t.round(1))
```
<!--sortie-->
```text
                         clients  commandes      ca
canal_dominant fidelite                            
Boutique       0             969        5.0   510.9
               1             530        4.9   487.7
Mixte          0            1676       10.3  1029.6
               1             927       10.5  1050.3
Site           0             462        2.9   280.8
               1             242        3.0   292.0
```

**À vous.** La carte de fidélité va-t-elle avec plus de commandes ? Peut-on dire que la carte les **fait** commander ? (Indice : la carte est proposée à des clients qui ne sont pas choisis au hasard.)

### Application 4.2 — Choisir k, un pas de plus (section 4.1)

**Objectif.** Comparer plusieurs nombres de segments non seulement par la silhouette mais par la **taille du plus petit segment** et l'**accord** entre solutions voisines.

```python
X = O.variables_kmeans(g)
Z = StandardScaler().fit_transform(X)
sol = {k: KMeans(k, n_init=10, random_state=0).fit(Z) for k in range(3, 7)}
for k, m in sol.items():
    print(k, "| silhouette", round(silhouette_score(Z, m.labels_, sample_size=3000, random_state=0), 3), "| plus petit segment :", int(np.bincount(m.labels_).min()))
```
<!--sortie-->
```text
3 | silhouette 0.264 | plus petit segment : 1189
4 | silhouette 0.276 | plus petit segment : 392
5 | silhouette 0.213 | plus petit segment : 343
6 | silhouette 0.224 | plus petit segment : 318
```

```python
print("accord k=4 / k=5 :", round(adjusted_rand_score(sol[4].labels_, sol[5].labels_), 2), "| k=4 / k=3 :", round(adjusted_rand_score(sol[4].labels_, sol[3].labels_), 2))
```
<!--sortie-->
```text
accord k=4 / k=5 : 0.5 | k=4 / k=3 : 0.82
```

**À vous.** Quel k retiendriez-vous si la gérante ne peut mener que trois actions distinctes ? Que gagne-t-on, que perd-on avec k = 3 ?

### Application 4.3 — Règles contre k-moyennes : qui prédit mieux ? (section 4.1)

**Objectif.** Se placer au 30 juin 2025 et comparer le **pouvoir de prédiction** des segments par règles (réguliers, occasionnels, endormis) et des segments k-moyennes sur la commande du second semestre.

**Étape 1 — les deux segmentations au 30 juin.**

```python
t0 = pd.Timestamp("2025-06-30")
c0 = cmd[cmd["date_commande"] <= t0]
g0 = O.table_clients(c0, lig[lig["id_commande"].isin(c0["id_commande"])], t0)
g0["k4"] = O.nommer_segments(g0, KMeans(4, n_init=10, random_state=0).fit(StandardScaler().fit_transform(O.variables_kmeans(g0))).labels_)
n12 = c0[c0["date_commande"] > t0 - pd.Timedelta(days=365)].groupby("id_client").size()
g0["n12"] = n12.reindex(g0.index).fillna(0)
g0["regle"] = np.select([g0["n12"] >= 3, g0["n12"] >= 1], ["Réguliers", "Occasionnels"], "Endormis")
```

**Étape 2 — la commande du semestre suivant.**

```python
h2 = set(cmd.loc[cmd["date_commande"] > t0, "id_client"])
g0["achat_h2"] = g0.index.isin(h2).astype(int)
for col in ["regle", "k4"]:
    print(g0.groupby(col)["achat_h2"].agg(["size", "mean"]).round(3), "\n")
```
<!--sortie-->
```text
              size   mean
regle                    
Endormis       763  0.362
Occasionnels  1897  0.521
Réguliers     1749  0.854 

                         size   mean
k4                                  
Chasseurs de promotions   431  0.492
Dormants de la Boutique  1064  0.435
Dormants du Site          896  0.450
Réguliers actifs         2018  0.833 
```

**À vous.** Quelle segmentation sépare le mieux les clients qui recommandent de ceux qui ne recommandent pas ? Mesurez cet écart par la **différence entre le meilleur et le moins bon segment**.

### Application 4.4 — Cohortes mensuelles contre trimestrielles (section 4.2)

**Objectif.** Voir le bruit d'une matrice mensuelle et le réduire en regroupant.

```python
effm, tm, _ = O.matrice_cohortes(cli, cmd, pas="M")
effq, tq, _ = O.matrice_cohortes(cli, cmd, pas="Q")
print("taille des cohortes mensuelles :", int(effm.min()), "à", int(effm.max()), "| trimestrielles :", int(effq.min()), "à", int(effq.max()))
```
<!--sortie-->
```text
taille des cohortes mensuelles : 42 à 66 | trimestrielles : 147 à 188
```

```python
age1m = tm[1].dropna() * 100
age1q = tq[1].dropna() * 100
print("taux d'activité à l'âge 1 : mensuel, de", round(age1m.min()), "% à", round(age1m.max()), "% | trimestriel, de", round(age1q.min()), "% à", round(age1q.max()), "%")
print("écart-type entre cohortes : mensuel", round(age1m.std(), 1), "| trimestriel", round(age1q.std(), 1))
```
<!--sortie-->
```text
taux d'activité à l'âge 1 : mensuel, de 5 % à 33 % | trimestriel, de 30 % à 41 %
écart-type entre cohortes : mensuel 7.2 | trimestriel 3.6
```

**À vous.** Les cohortes mensuelles varient beaucoup plus que les trimestrielles : est-ce un vrai écart de comportement ? Calculez l'écart-type attendu **par pur hasard** d'une proportion : celle d'une cohorte mensuelle à l'âge 1 (environ 16 %, 57 clients) puis celle d'une cohorte trimestrielle (environ 36 %, 170 clients). Les variations observées dépassent-elles ce bruit ?

### Application 4.5 — Revenu par client et concentration (section 4.2)

**Objectif.** Mesurer le revenu par client des cohortes annuelles, et regarder la **médiane** à côté de la moyenne.

```python
new = cli[cli["date_inscription"] >= "2023-01-01"].set_index("id_client")
c = cmd[cmd["id_client"].isin(new.index)].copy()
c["age_j"] = (c["date_commande"] - c["id_client"].map(new["date_inscription"])).dt.days
c12 = c[c["age_j"] < 365].groupby("id_client")["ca"].sum()
base = new[new["date_inscription"] <= "2024-12-31"].copy()           # observés au moins 12 mois
base["ca12"] = c12.reindex(base.index).fillna(0.0)
base["an"] = base["date_inscription"].dt.year
print(base.groupby("an")["ca12"].agg(["size", "mean", "median"]).round(1))
```
<!--sortie-->
```text
      size   mean  median
an                       
2023   700  252.0   129.9
2024   666  240.2   125.9
```

```python
srt = base["ca12"].sort_values(ascending=False)
print("part du CA des 10 % meilleurs :", round(srt.head(int(0.1 * len(srt))).sum() / srt.sum() * 100, 1), "% | clients à zéro :", round((base["ca12"] == 0).mean() * 100, 1), "%")
```
<!--sortie-->
```text
part du CA des 10 % meilleurs : 40.3 % | clients à zéro : 31.3 %
```

**À vous.** La moyenne annuelle de 12 mois est-elle un bon résumé du client « typique » ? Que diriez-vous à la gérante qui voudrait fixer un budget d'acquisition sur cette moyenne ?

### Application 4.6 — RFM : le piège des ex æquo (section 4.3)

**Objectif.** Voir pourquoi la fréquence se classe par **rang**, et comparer deux définitions de « client à risque ».

```python
print("clients n'ayant commandé qu'une fois :", round((g["n"] == 1).mean() * 100, 1), "%")
brut = pd.qcut(g["n"], 5, duplicates="drop")
print("quintiles sur les valeurs brutes :", brut.value_counts().sort_index().tolist())
rang = pd.qcut(g["n"].rank(method="first"), 5, labels=False)
print("quintiles sur les rangs          :", pd.Series(rang).value_counts().sort_index().tolist())
```
<!--sortie-->
```text
clients n'ayant commandé qu'une fois : 17.3 %
quintiles sur les valeurs brutes : [1410, 881, 596, 1035, 884]
quintiles sur les rangs          : [962, 961, 961, 961, 961]
```

```python
s = O.rfm(g)
a_risque = g[(s["R"] <= 2) & (s["F"] >= 4)]
print("clients à risque (R ≤ 2, F ≥ 4) :", len(a_risque), "| leur CA cumulé :", round(a_risque["ca"].sum()), "€ soit", round(a_risque["ca"].sum() / g["ca"].sum() * 100, 1), "% du total")
print(a_risque.sort_values("ca", ascending=False)[["n", "ca", "rec"]].head(5).round(0).astype(int))
```
<!--sortie-->
```text
clients à risque (R ≤ 2, F ≥ 4) : 257 | leur CA cumulé : 268151 € soit 7.3 % du total
            n    ca  rec
id_client               
4154       35  4162  181
12         32  3131  156
798        22  2690  164
3900       24  2519  147
2377       14  2494  418
```

**À vous.** Quels clients appelleriez-vous en premier parmi les clients à risque ? Quelles informations manquent pour décider ?

### Application 4.7 — Valeur vie client par segment (section 4.3)

**Objectif.** Appliquer la formule de la valeur vie client aux segments de k-moyennes, avec un taux d'actualisation fictif de 8 %. Piège à éviter : les segments doivent être construits **avant** la période où l'on mesure la rétention. Segmentés avec les données de 2025, les « réguliers actifs » auraient une rétention 2024-2025 de près de 100 % par construction (ils sont actifs *parce que* leur dernière commande est récente) : c'est un raisonnement circulaire.

**Étape 1 — segments au 31 décembre 2024.**

```python
t1 = pd.Timestamp("2024-12-31")
c1 = cmd[cmd["date_commande"] <= t1]
g1 = O.table_clients(c1, lig[lig["id_commande"].isin(c1["id_commande"])], t1)
g1["segment"] = O.nommer_segments(g1, KMeans(4, n_init=10, random_state=0).fit(StandardScaler().fit_transform(O.variables_kmeans(g1))).labels_)
x = lig.merge(cmd[["id_commande", "date_commande", "id_client"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
x["marge"] = x["montant"] / 1.2 - x["quantite"] * x["cout_achat"]
x["annee"] = x["date_commande"].dt.year
m25 = x[x["annee"] == 2025].groupby("id_client")["marge"].sum()
a24 = set(x.loc[x["annee"] == 2024, "id_client"]); a25 = set(x.loc[x["annee"] == 2025, "id_client"])
print(g1["segment"].value_counts().to_dict())
```
<!--sortie-->
```text
{'Réguliers actifs': 1813, 'Dormants de la Boutique': 981, 'Dormants du Site': 832, 'Chasseurs de promotions': 438}
```

**Étape 2 — rétention, marge par client actif et valeur vie, par segment.**

```python
lignes = []
for seg, d in g1.groupby("segment"):
    act24 = a24 & set(d.index)
    rho = len(act24 & a25) / len(act24)
    m = m25.reindex(list(act24 & a25)).mean()
    lignes.append((seg, len(act24), round(rho, 3), round(m, 1), round(m / (1 - rho / 1.08))))
print(pd.DataFrame(lignes, columns=["segment", "actifs_2024", "retention", "marge_par_actif", "CLV_8pct"]).to_string(index=False))
```
<!--sortie-->
```text
                segment  actifs_2024  retention  marge_par_actif  CLV_8pct
Chasseurs de promotions          345      0.713             80.0       235
Dormants de la Boutique          692      0.675             75.0       200
       Dormants du Site          630      0.678             73.9       198
       Réguliers actifs         1812      0.932            156.9      1142
```

**À vous.** Quel segment a la plus grande valeur vie, et à quel point la valeur d'un segment dont la rétention est proche de 100 % est-elle sensible à une petite erreur sur cette rétention ? (Indice : calculez la valeur vie avec une rétention de 0,92 et de 0,95.)

### Application 4.8 — L'entonnoir, source par appareil (section 4.4)

**Objectif.** Croiser source et appareil, puis chiffrer, par source, la **valeur perdue** aux deux étapes où l'intention d'achat est démontrée.

```python
ent = O.entonnoir(sess, ["source", "appareil"])
print((ent["conversion"] * 100).round(1).unstack())
```
<!--sortie-->
```text
appareil   mobile  ordinateur  tablette
source                                 
direct        7.1         6.7       7.0
email         8.7         8.8       7.3
organique     4.0         4.1       3.9
payant        3.0         2.7       4.3
referent      3.7         4.0       3.2
reseaux       2.1         2.2       2.3
```

```python
src = O.entonnoir(sess, "source")
src["paniers_perdus"] = src["ajout_panier"] - src["debut_paiement"]
src["paiements_perdus"] = src["debut_paiement"] - src["commande"]
print(src[["sessions", "commande", "paniers_perdus", "paiements_perdus"]].sort_values("paiements_perdus", ascending=False))
```
<!--sortie-->
```text
           sessions  commande  paniers_perdus  paiements_perdus
source                                                         
organique     43187      1736            2611              1455
direct        35566      2467            2205              1213
payant        17783       535            1121               579
reseaux       15243       329             971               508
email          8892       772             498               315
referent       6351       239             352               210
```

**À vous.** À quelle source un abandon de panier coûte-t-il le plus en nombre ? En proportion ? Les deux classements sont-ils les mêmes ?

## Exercices

### Exercice 4.1 ⭐ — Un seuil de plus (section 4.1.2)

Reprenez les segments par règles de la section 4.1.2, mais appelez « réguliers » les clients ayant **au moins deux** commandes sur douze mois (on ne retire pas ici les nouveaux inscrits, donc les effectifs diffèrent un peu de ceux du livre). Quelle part des clients et du chiffre d'affaires des douze derniers mois représentent-ils ? Comparez à la règle « au moins trois ».

### Exercice 4.2 ⭐⭐ — Une itération à la main, autres clients (section 4.1.3)

Six clients : commandes 1, 3, 4, 10, 12, 15 ; panier 50, 70, 55, 90, 120, 105. Standardisez, prenez les clients **B** et **E** comme centres de départ, calculez les distances, les affectations et les nouveaux centres. L'algorithme a-t-il convergé après une itération ? Vérifiez avec `KMeans`.

### Exercice 4.3 ⭐⭐ — Standardiser ou non (section 4.1.4)

Avec seulement deux variables, la récence (en jours) et le nombre de commandes, comparez les segments à k = 3 avec et sans standardisation. Quel est l'indice de Rand ajusté entre les deux solutions ? Quelle variable domine sans standardisation ?

### Exercice 4.4 ⭐⭐⭐ — Un critère extérieur pour les « chasseurs de promotions » (section 4.1.7)

Au 30 juin 2025, reconstruisez les segments de k-moyennes. Les « chasseurs de promotions » sont-ils réellement plus sensibles aux promotions **après** cette date ? Mesurez, pour chaque segment, la part des commandes du second semestre passées avec un code promotionnel. Que concluez-vous, et quelle réserve faut-il garder ?

### Exercice 4.5 ⭐ — Une rétention à la main (section 4.2.2)

Une cohorte de six clients : les trimestres avec commande sont (1) 0, 1 ; (2) 1, 2, 3 ; (3) aucun ; (4) 0, 3 ; (5) 2 ; (6) 0, 1, 2, 3. Calculez la rétention aux âges 0 à 3, puis la part de clients qui n'ont jamais commandé. Vérifiez avec pandas.

### Exercice 4.6 ⭐⭐ — Les anciens clients et la période (section 4.2.5)

Calculez le taux d'activité **par trimestre civil** des 4 000 clients inscrits **avant 2023** (les clients que l'on exclut des cohortes) et comparez-le à celui des clients inscrits depuis 2023. Que dit la comparaison de l'effet de la saison ?

### Exercice 4.7 ⭐⭐ — Quelles cases sont significatives ? (section 4.2.6)

Pour la cohorte trimestrielle de 2023T1 (167 clients), calculez l'intervalle de confiance à 95 % (Wilson) de la case d'âge 3 (50 %) et de la case d'âge 8 (26 %). Les deux intervalles se chevauchent-ils ? Que déduisez-vous de la lecture de cases isolées ?

### Exercice 4.8 ⭐⭐⭐ — Le code de bienvenue retient-il ? (section 4.2.8)

Parmi les 2 000 clients inscrits depuis 2023 observables 180 jours, comparez la part qui repasse commande en 180 jours selon que la **première commande** utilisait un code promotionnel ou non. Quelle est la différence, avec son intervalle ? Peut-on dire que le code fait revenir ?

### Exercice 4.9 ⭐⭐ — Les gros clients à risque (section 4.3.1)

Au 31 décembre 2025, listez les 10 clients de segment RFM « À risque (gros clients) » au plus fort chiffre d'affaires, avec leur récence. Combien d'euros de chiffre d'affaires annuel moyen (sur les trois ans) représentent-ils ensemble ? Que feriez-vous d'eux ?

### Exercice 4.10 ⭐⭐⭐ — Un seuil de relance (section 4.3.3)

Une relance coûte 3 € et le client qui revient rapporte en moyenne 30 € de marge. (1) De combien de **points** la relance doit-elle augmenter la probabilité de revenir pour être rentable ? (2) À partir de la table « récence au 30 juin → probabilité de recommander » de la section 4.3.3, quelle est, pour chaque tranche de récence, la **marge de manœuvre maximale** (1 − p) ? (3) Peut-on, avec ces données seules, dire quelles tranches relancer ? Qu'ajoutez-vous pour décider ?

### Exercice 4.11 ⭐⭐ — Où perd-on le plus d'argent ? (section 4.4.2)

Pour chaque source, la valeur d'un panier abandonné est le panier moyen des commandes de cette source multiplié par le nombre de paniers qui n'atteignent pas la commande. Classez les sources selon cette **valeur perdue**. Le classement est-il celui des taux d'abandon ?

### Exercice 4.12 ⭐ — Trois phrases sous le tableau (section 4.4.4)

Calculez la part de clients actifs au trimestre suivant l'inscription (âge 1) pour chaque année d'inscription (2023, 2024, 2025, pour les cohortes observées à cet âge). Rédigez les **trois phrases** (le fait, la lecture, la limite) qui accompagneraient ce petit tableau.

## Corrigés

### Corrigé 4.1

On refait la table des douze derniers mois, avec deux seuils.

```python
deb = O.FIN - pd.Timedelta(days=365)
c12 = cmd[cmd["date_commande"] > deb].groupby("id_client").agg(n12=("id_commande", "size"), ca12=("ca", "sum"))
for seuil in (2, 3):
    r = c12[c12["n12"] >= seuil]
    print(f"au moins {seuil} commandes :", len(r), "clients", round(len(r) / len(cli) * 100, 1), "% des 6 000 |", round(r["ca12"].sum() / c12["ca12"].sum() * 100, 1), "% du CA des 12 mois")
```
<!--sortie-->
```text
au moins 2 commandes : 2654 clients 44.2 % des 6 000 | 90.9 % du CA des 12 mois
au moins 3 commandes : 1848 clients 30.8 % des 6 000 | 78.6 % du CA des 12 mois
```

**Lecture.** Avec « au moins deux commandes », le groupe compte 2 654 clients (44,2 % des 6 000) et réalise 90,9 % du chiffre d'affaires des douze mois ; avec « au moins trois », 1 848 clients (30,8 %) et 78,6 %. Baisser le seuil ajoute 800 clients pour 12 points de chiffre d'affaires : le seuil est une **décision** (qui reçoit le traitement « fidèles » ?), pas une vérité. Les effectifs diffèrent de ceux du livre (1 726 réguliers) parce que les nouveaux inscrits ne sont pas retirés ici.

### Corrigé 4.2

Moyennes 7,5 et 81,67 ; écarts-types 5,12 et 25,60. Après standardisation, les distances aux centres B et E donnent les affectations ; on vérifie par le code (les calculs à la main s'écrivent comme à la section 4.1.3).

```python
P = pd.DataFrame({"commandes": [1, 3, 4, 10, 12, 15], "panier": [50, 70, 55, 90, 120, 105]}, index=list("ABCDEF"))
Zp = ((P - P.mean()) / P.std(ddof=0)).values
cen = Zp[[1, 4]]
for it in range(3):
    lab = np.linalg.norm(Zp[:, None, :] - cen[None], axis=2).argmin(1)
    cen_new = np.array([Zp[lab == k].mean(0) for k in range(2)])
    print("itération", it + 1, "| affectations", lab.tolist(), "| centres", cen_new.round(2).tolist())
    if np.allclose(cen, cen_new):
        break
    cen = cen_new
print("KMeans :", KMeans(2, n_init=10, random_state=0).fit(Zp).labels_.tolist())
```
<!--sortie-->
```text
itération 1 | affectations [0, 0, 0, 1, 1, 1] | centres [[-0.94, -0.91], [0.94, 0.91]]
itération 2 | affectations [0, 0, 0, 1, 1, 1] | centres [[-0.94, -0.91], [0.94, 0.91]]
KMeans : [1, 1, 1, 0, 0, 0]
```

**Lecture.** Dès la première itération, les affectations sont {A, B, C} et {D, E, F} ; la seconde itération redonne les mêmes centres, $(-0{,}94\,;-0{,}91)$ et $(0{,}94\,;0{,}91)$ : l'algorithme a **convergé en une itération**. `KMeans` retrouve les mêmes groupes (les numéros sont inversés, ce qui est sans importance).

### Corrigé 4.3

```python
d = pd.DataFrame({"rec": g["rec"], "n": g["n"]})
Zs = StandardScaler().fit_transform(d)
a = KMeans(3, n_init=10, random_state=0).fit(Zs).labels_
b = KMeans(3, n_init=10, random_state=0).fit(d.values).labels_
print("accord (indice de Rand ajusté) :", round(adjusted_rand_score(a, b), 2))
print("écarts-types sans standardisation :", d.std().round(1).to_dict())
print("moyenne de la récence et des commandes par segment, sans standardisation :")
print(d.assign(s=b).groupby("s").mean().round(1))
```
<!--sortie-->
```text
accord (indice de Rand ajusté) : 0.35
écarts-types sans standardisation : {'rec': 238.1, 'n': 7.9}
moyenne de la récence et des commandes par segment, sans standardisation :
     rec    n
s            
0  780.8  1.6
1   57.5  9.7
2  342.7  3.6
```

**Lecture.** L'accord est de 0,35 seulement. Sans standardisation, la **récence domine** : son écart-type est de 238 jours contre 7,9 pour le nombre de commandes ; les trois groupes sont donc des tranches de récence (781, 58 et 343 jours en moyenne) et le nombre de commandes ne fait que les suivre (1,6 ; 9,7 ; 3,6).

### Corrigé 4.4

```python
t0 = pd.Timestamp("2025-06-30")
c0 = cmd[cmd["date_commande"] <= t0]
g0 = O.table_clients(c0, lig[lig["id_commande"].isin(c0["id_commande"])], t0)
g0["seg"] = O.nommer_segments(g0, KMeans(4, n_init=10, random_state=0).fit(StandardScaler().fit_transform(O.variables_kmeans(g0))).labels_)
h2 = cmd[cmd["date_commande"] > t0]
sh = h2.groupby("id_client").agg(n=("id_commande", "size"), promo=("promo", "sum"))
j = g0[["seg"]].join(sh).dropna()
print((j.groupby("seg")["promo"].sum() / j.groupby("seg")["n"].sum() * 100).round(1).sort_values(ascending=False))
```
<!--sortie-->
```text
seg
Chasseurs de promotions    15.9
Réguliers actifs           14.1
Dormants du Site           13.3
Dormants de la Boutique    12.5
dtype: float64
```

**Lecture.** Les « chasseurs de promotions » de juin passent **15,9 %** de leurs commandes du second semestre avec un code, contre 14,1 % pour les réguliers actifs, 13,3 % et 12,5 % pour les dormants : l'écart est de 2 à 3 points, très loin des 76 % qui avaient fait leur nom. L'étiquette tient mal : elle reposait sur deux ou trois commandes par client, et une part de 76 % sur trois commandes se produit facilement par hasard (un code **soldes** suffit aux soldes). Réserve : la part de commandes avec code dépend aussi du **calendrier** (les soldes) et de la carte de fidélité (code réservé), pas seulement du goût du client pour les rabais.

### Corrigé 4.5

À l'âge 0, trois clients sur six commandent (1, 4, 6) : 50 % ; à l'âge 1, trois (1, 2, 6) : 50 % ; à l'âge 2, trois (2, 5, 6) : 50 % ; à l'âge 3, trois (2, 4, 6) : 50 %. Le client 3 n'a jamais commandé : 1/6, soit 17 %.

```python
trim = {1: [0, 1], 2: [1, 2, 3], 3: [], 4: [0, 3], 5: [2], 6: [0, 1, 2, 3]}
ret = [sum(a in v for v in trim.values()) / len(trim) for a in range(4)]
print("rétention aux âges 0 à 3 :", [round(x * 100) for x in ret], "| jamais commandé :", round(sum(len(v) == 0 for v in trim.values()) / len(trim) * 100), "%")
```
<!--sortie-->
```text
rétention aux âges 0 à 3 : [50, 50, 50, 50] | jamais commandé : 17 %
```

**Lecture.** Chaque âge compte trois clients actifs sur six, soit 50 % ; le client 3 n'a jamais commandé (1 sur 6, soit 17 %). Remarquez que la rétention est constante à 50 % alors que les clients sont **différents** d'un âge à l'autre : la matrice donne une part, pas des personnes qui restent.

### Corrigé 4.6

```python
anc = cli[cli["date_inscription"] < "2023-01-01"]["id_client"]
nou = cli[cli["date_inscription"] >= "2023-01-01"]
cq = cmd.assign(per=cmd["date_commande"].dt.to_period("Q"))
res = {}
for nom, ids in [("anciens (avant 2023)", set(anc))]:
    a = cq[cq["id_client"].isin(ids)].groupby("per")["id_client"].nunique() / len(ids)
    res[nom] = a
print((pd.DataFrame(res) * 100).round(1).T.to_string())
print("nouveaux, âge ≥ 1 :", (O.activite_par_periode(cli, cmd) * 100).round(1).values.tolist())
```
<!--sortie-->
```text
per                   2023Q1  2023Q2  2023Q3  2023Q4  2024Q1  2024Q2  2024Q3  2024Q4  2025Q1  2025Q2  2025Q3  2025Q4
anciens (avant 2023)    34.4    37.1    35.0    44.7    32.6    34.5    32.6    42.2    30.6    33.8    30.9    41.8
nouveaux, âge ≥ 1 : [39.5, 38.0, 42.7, 32.7, 34.0, 32.5, 41.8, 31.8, 34.4, 33.9, 40.7]
```

**Lecture.** Les anciens clients montrent la **même saisonnalité** : 42 à 45 % d'actifs chaque quatrième trimestre contre 31 à 37 % aux autres trimestres, comme les nouveaux. L'effet de période n'est donc pas propre aux nouveaux clients : c'est la saison. On note aussi des niveaux plus élevés en 2023 qu'en 2025 (par exemple 37,1 % au deuxième trimestre de 2023 contre 33,8 % en 2025) : la dilution décrite à la section 4.2.8.

### Corrigé 4.7

```python
eff, taux, _ = O.matrice_cohortes(cli, cmd, pas="Q")
n = int(eff.iloc[0])
for age in (3, 8):
    p = taux.iloc[0][age]
    lo, hi = O.ic_proportion(p * n, n)
    print(f"âge {age} : {p * 100:.0f} %, intervalle à 95 % de {lo * 100:.0f} % à {hi * 100:.0f} %")
```
<!--sortie-->
```text
âge 3 : 50 %, intervalle à 95 % de 42 % à 57 %
âge 8 : 26 %, intervalle à 95 % de 20 % à 34 %
```

**Lecture.** Les deux intervalles (42 à 57 % et 20 à 34 %) ne se chevauchent pas : la différence est probablement réelle. Mais l'âge 3 de cette cohorte tombe au quatrième trimestre de 2023 (la saison forte) et l'âge 8 au premier trimestre de 2025 (la saison faible) : c'est un effet de **période**, pas d'âge. Une case isolée ne se lit jamais seule, même quand elle est « significative ».

### Corrigé 4.8

```python
new = cli[cli["date_inscription"] >= "2023-01-01"]
n = cmd[cmd["id_client"].isin(new["id_client"])].sort_values("date_commande")
f = n.groupby("id_client").nth(0).set_index("id_client")
s = n.groupby("id_client").nth(1).set_index("id_client")
d = pd.DataFrame({"prem": f["date_commande"], "promo1": f["promo"], "sec": s["date_commande"]}).query("prem <= '2025-07-04'")
d["retour"] = ((d["sec"] - d["prem"]).dt.days <= 180).fillna(False)
t = d.groupby("promo1")["retour"].agg(["size", "sum", "mean"])
print(t.round(3))
p1, p0 = t.loc[True, "mean"], t.loc[False, "mean"]
se = np.sqrt(p1 * (1 - p1) / t.loc[True, "size"] + p0 * (1 - p0) / t.loc[False, "size"])
print("écart :", round((p1 - p0) * 100, 1), "points, intervalle à 95 % de", round((p1 - p0 - 1.96 * se) * 100, 1), "à", round((p1 - p0 + 1.96 * se) * 100, 1))
```
<!--sortie-->
```text
        size  sum   mean
promo1                  
False    794  484  0.610
True     332  230  0.693
écart : 8.3 points, intervalle à 95 % de 2.3 à 14.3
```

**Lecture.** 69,3 % des nouveaux clients dont la première commande utilisait un code reviennent en 180 jours, contre 61,0 % des autres : un écart de 8,3 points, d'intervalle 2,3 à 14,3 (il exclut zéro). Mais on ne peut pas dire que le code fait revenir : les codes ne sont pas distribués au hasard (soldes, bienvenue, fidélité) et les clients qui en utilisent un ne ressemblent pas aux autres. Il faudrait un test A/B : donner le code au hasard à la moitié des nouveaux clients.

### Corrigé 4.9

```python
s = O.rfm(g)
s["seg"] = [O.nom_segment_rfm(r, f) for r, f in zip(s["R"], s["F"])]
r = g.join(s)[lambda d: d["seg"] == "À risque (gros clients)"].sort_values("ca", ascending=False).head(10)
print(r[["n", "ca", "rec"]].round(0).astype(int))
print("CA annuel moyen de ces 10 clients (sur 3 ans) :", round(r["ca"].sum() / 3), "€")
```
<!--sortie-->
```text
            n    ca  rec
id_client               
4154       35  4162  181
12         32  3131  156
798        22  2690  164
3900       24  2519  147
2377       14  2494  418
2882       24  2484  187
1735       20  2334  156
3113       15  2254  404
1900       20  2151  161
3393       17  2067  266
CA annuel moyen de ces 10 clients (sur 3 ans) : 8762 €
```

**Lecture.** Ces dix clients ont passé de 14 à 35 commandes, pour un chiffre d'affaires de 2 067 à 4 162 € chacun, et leur dernière commande a 147 à 418 jours : ensemble, 8 762 € par an. À ce niveau, un appel personnel se justifie même avec une faible chance de retour. Avant d'appeler, regardez le **rythme habituel** de chaque client (le client 2377 est silencieux depuis 418 jours, alors que le client 4154 l'est depuis 181 jours pour 35 commandes) et vérifiez le **consentement** à être contacté.

### Corrigé 4.10

(1) Il y a rentabilité quand $\Delta p\times30-3>0$, soit $\Delta p>3/30=10$ points, **quelle que soit** la tranche. (2) Une relance ne peut pas faire gagner plus que $1-p$ : 22 points pour les clients récents, 64 points pour les plus silencieux. (3) Non : ces données disent **combien** de clients reviennent, pas **combien reviennent à cause de la relance**. Les clients récents reviennent déjà à 78 % : le gain possible est faible, et le seuil de 10 points est difficile à atteindre ; les silencieux ont plus de marge, mais rien ne garantit qu'une relance les fasse revenir. Il faut un **test A/B** (chapitre 2, section 2.2) : relancer un échantillon au hasard dans chaque tranche, comparer au groupe non relancé, et chiffrer le gain en points avec son intervalle.

```python
rr = O.reachat(cmd, "2025-06-30")
rr["groupe"] = pd.cut(rr["rec"], [-1, 30, 90, 180, 365, 2000], labels=["0-30 j", "31-90 j", "91-180 j", "181-365 j", "plus de 365 j"])
p = rr.groupby("groupe")["reachete"].mean()
print("seuil de rentabilité :", 3 / 30 * 100, "points")
print(pd.DataFrame({"p_sans_relance_%": (p * 100).round(1), "gain_maximal_points": ((1 - p) * 100).round(1)}))
```
<!--sortie-->
```text
seuil de rentabilité : 10.0 points
               p_sans_relance_%  gain_maximal_points
groupe                                              
0-30 j                     77.6                 22.4
31-90 j                    74.3                 25.7
91-180 j                   67.1                 32.9
181-365 j                  53.6                 46.4
plus de 365 j              36.2                 63.8
```

### Corrigé 4.11

```python
src = O.entonnoir(sess, "source")
pm = cmd[cmd["canal"] == "Site"].groupby(sess.loc[sess["commande"] == 1].set_index("id_commande")["source"].reindex(cmd.loc[cmd["canal"] == "Site", "id_commande"]).values)["ca"].mean()
src["pm"] = pm
src["perdu"] = (src["ajout_panier"] - src["commande"]) * src["pm"]
src["abandon"] = 1 - src["commande"] / src["ajout_panier"]
print(src[["ajout_panier", "pm", "abandon", "perdu"]].round(2).sort_values("perdu", ascending=False))
```
<!--sortie-->
```text
           ajout_panier      pm  abandon      perdu
source                                             
organique          5802  106.03     0.70  431126.44
direct             5885  100.74     0.58  344332.55
payant             2235   98.38     0.76  167239.45
reseaux            1808  105.46     0.82  155971.61
email              1585   96.21     0.51   78221.42
referent            801   98.38     0.70   55288.64
```

**Lecture.** La valeur perdue la plus forte est celle de la source **organique** (4 066 paniers non convertis, 431 126 € de paniers), devant le direct et la publicité ; le taux d'abandon le plus élevé est celui des **réseaux** (82 %), le plus faible celui de l'e-mail (51 %). Les deux classements ne sont pas les mêmes : le volume pèse autant que le taux. Précaution : ces montants sont des **paniers**, pas des ventes manquées (beaucoup de paniers ne seraient jamais devenus des commandes).

### Corrigé 4.12

```python
eff, taux, _ = O.matrice_cohortes(cli, cmd, pas="Q")
t1 = taux[1].dropna() * 100
an = pd.Series([str(c)[:4] for c in t1.index], index=t1.index)
print(pd.DataFrame({"cohorte": t1.round(0), "an": an}).groupby("an")["cohorte"].agg(["size", "mean"]).round(1))
```
<!--sortie-->
```text
      size  mean
an              
2023     4  35.5
2024     4  35.2
2025     3  37.3
```

**Lecture.** Les trois phrases pourraient être : *Pour les cohortes de 2023 (4 cohortes), 2024 (4) et 2025 (3 observées), 35,5 %, 35,2 % et 37,3 % des clients commandent au trimestre qui suit leur inscription.* *Le niveau est stable d'une année à l'autre ; les écarts sont du même ordre que le bruit attendu pour des cohortes de 150 à 190 clients.* *Ce tableau ne dit rien du comportement ultérieur ni de la saison : les cohortes de 2025 sont observées à des trimestres civils différents de celles de 2023.*


## Pistes des applications

Les « À vous » des applications n'ont pas de corrigé détaillé : voici une piste pour chacun, avec les ordres de grandeur à retrouver.

- **Application 4.1.** La carte de fidélité ne va pas avec plus de commandes : 5,0 contre 4,9 (clients de la Boutique), 10,3 contre 10,5 (mixtes), 2,9 contre 3,0 (Site). Et même si elle y allait, on ne pourrait pas conclure que la carte les **fait** commander : elle n'est pas distribuée au hasard. Remarquez aussi que la catégorie « Mixte » (10 commandes) est mécaniquement celle des gros acheteurs : un client qui n'a passé qu'une commande ne peut pas être mixte.
- **Application 4.2.** Avec trois actions, k = 3 convient : silhouette 0,264 (contre 0,276 pour k = 4), plus petit segment de 1 189 clients, accord de 0,82 avec k = 4. On perd l'isolement d'un petit groupe (392 clients) dont l'étiquette, on l'a vu, est fragile. k = 5 est moins bon (0,213) et s'accorde peu avec k = 4 (0,50).
- **Application 4.3.** Les règles séparent **mieux** que les k-moyennes : 85,4 % de recommandes chez les réguliers contre 36,2 % chez les endormis (49 points), contre 83,3 % et 43,5 % pour les k-moyennes (40 points). Les règles utilisent directement la fréquence et la récence, qui commandent le réachat ; les k-moyennes ajoutent le canal et les promotions, qui ne prédisent presque rien. Une méthode plus sophistiquée ne prédit pas mieux : elle sert à **découvrir** des profils.
- **Application 4.4.** Les cohortes mensuelles vont de 5 à 33 % à l'âge 1 (écart-type 7,2 points), les trimestrielles de 30 à 41 % (3,6). Le hasard seul donnerait 4,9 points pour une proportion de 16 % sur 57 clients et 3,7 points pour 36 % sur 170 : les cohortes trimestrielles varient comme le hasard le prévoit, les mensuelles davantage, parce que leur âge 1 tombe dans des mois civils très différents (décembre contre l'été).
- **Application 4.5.** La moyenne (252 € pour les inscrits de 2023, 240 € pour ceux de 2024) est deux fois la médiane (130 € et 126 €) : 31 % des clients inscrits ne rapportent **rien** en douze mois, et les 10 % meilleurs rapportent 40 % du total. Fixer un budget d'acquisition sur 250 € surestimerait ce que rapporte la moitié des clients.
- **Application 4.6.** Les quintiles sur valeurs brutes donnent des groupes de 1 410, 881, 596, 1 035 et 884 clients ; sur les rangs, des groupes égaux (961 ou 962). Parmi les 257 clients à risque (7,3 % du chiffre d'affaires), on appelle d'abord les plus gros (35 commandes, 4 162 €) mais il manque leur **rythme habituel**, la raison du silence (une livraison ratée ?) et le **consentement** à être contactés.
- **Application 4.7.** Les réguliers actifs ont la plus grande valeur vie (rétention de 93 %, marge de 157 € par client actif, valeur de 1 142 €) contre 198 à 235 € pour les trois autres segments. Elle est **très sensible** à la rétention : avec 0,92 la valeur tombe à 1 059 €, avec 0,95 elle monte à 1 303 €. Les rétentions des petits segments reposent sur 345 à 692 clients seulement.
- **Application 4.8.** Selon l'appareil, les conversions par source varient peu, sauf pour de petites cases (par exemple la publicité sur tablette, 4,3 %, repose sur très peu de sessions). En nombre, la source organique perd le plus de paniers et de paiements (2 611 et 1 455) ; en proportion, ce sont les réseaux. Les deux classements diffèrent.
