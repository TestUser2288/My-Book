## 4.1 Segmentation de la clientèle et du portefeuille

Segmenter, c'est renoncer à la moyenne pour parler à des groupes. Cette section montre deux façons de former des groupes, par **règles** puis par **k-moyennes**, décortique l'algorithme sur six clients, apprend à choisir le nombre de segments et à les nommer, et surtout à **vérifier** qu'ils servent à quelque chose. Elle s'appuie sur les 4 806 clients qui ont commandé au moins une fois.

```python hide
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import outils_ch04 as O
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
T = O.charger()
cli, cmd, lig, sess = T["cli"], T["cmd"], T["lig"], T["sess"]
g = O.table_clients(cmd, lig)
```

### 4.1.1 Pourquoi segmenter : une action différente par groupe

Une segmentation ne vaut pas par la beauté de ses groupes, mais par **les décisions qu'elle permet**. La gérante a une enveloppe pour les fêtes : avec un seul groupe, elle envoie le même message à tous et dépense autant pour une cliente qui commande douze fois par an que pour un client qui n'a pas acheté depuis deux ans. Avec des segments, elle peut remercier les premiers, relancer les seconds, et ne pas dépenser un euro pour ceux qui reviendraient de toute façon.

On distingue deux familles de segmentations, qui se complètent.

- **Par règles métier** : on fixe des seuils à la main (« au moins trois commandes sur douze mois »). Elles sont **lisibles**, **stables** et faciles à expliquer ; leur défaut est que les seuils sont arbitraires et que l'on ne voit que les structures que l'on a prévues.
- **Statistiques** (algorithmes de regroupement, ici les **k-moyennes**) : on laisse les données proposer des groupes à partir de plusieurs variables à la fois. Elles découvrent des combinaisons auxquelles on n'avait pas pensé ; leur défaut est qu'elles rendent toujours un résultat, même sans structure, et que leurs groupes demandent à être **lus, nommés et vérifiés**.

Le bon réflexe est de commencer par les règles : elles donnent une référence, et elles disent déjà beaucoup.

### 4.1.2 Des segments par règles métier

Prenons cinq segments, fondés sur la dernière année et sur l'ancienneté d'inscription : les **nouveaux** (inscrits depuis moins de douze mois), les **réguliers** (au moins trois commandes sur douze mois), les **occasionnels** (une ou deux), les **endormis** (déjà clients, mais aucune commande sur douze mois) et ceux qui **n'ont jamais commandé**. L'appel suivant fabrique ces segments en une instruction.

```python
deb = O.FIN - pd.Timedelta(days=365)
c12 = cmd[cmd["date_commande"] > deb].groupby("id_client").agg(n12=("id_commande", "size"), ca12=("ca", "sum"))
b = cli.set_index("id_client").join(c12).join(g[["n"]].rename(columns={"n": "n_tot"}))
b[["n12", "ca12", "n_tot"]] = b[["n12", "ca12", "n_tot"]].fillna(0)
b["segment"] = np.select([b["date_inscription"] > deb, b["n12"] >= 3, b["n12"] >= 1, b["n_tot"] > 0],
                         ["Nouveaux", "Réguliers", "Occasionnels", "Endormis"], "Jamais commandé")
t = b.groupby("segment").agg(clients=("n12", "size"), ca12=("ca12", "sum"))
t["part_clients"] = (t["clients"] / t["clients"].sum() * 100).round(1)
t["part_ca"] = (t["ca12"] / t["ca12"].sum() * 100).round(1)
print(t[["clients", "part_clients", "part_ca"]].sort_values("part_ca", ascending=False))
```
<!--sortie-->
```text
                 clients  part_clients  part_ca
segment                                        
Réguliers           1726          28.8     73.9
Occasionnels        1813          30.2     19.2
Nouveaux             634          10.6      6.9
Endormis             931          15.5      0.0
Jamais commandé      896          14.9      0.0
```

Ce simple tableau est déjà un résultat : **29 % des clients réalisent 74 % du chiffre d'affaires des douze derniers mois**, tandis que 30 % des clients n'ont **rien acheté depuis douze mois** (931 endormis, et 896 qui n'ont jamais commandé). La gérante sait où est l'enjeu. Remarquez au passage une précaution : les règles s'appliquent **dans un ordre** (un nouveau client n'est pas aussi « régulier »), et cet ordre est une décision à écrire.

```python hide
assert [int(x) for x in t.loc[["Réguliers", "Occasionnels", "Nouveaux", "Endormis", "Jamais commandé"], "clients"]] == [1726, 1813, 634, 931, 896]
assert round(t.loc["Réguliers", "part_ca"], 1) == 73.9
```

### 4.1.3 Les k-moyennes, à la main sur six clients

Pour qu'une règle statistique soit autre chose qu'une boîte noire, calculons-la à la main. Les **k-moyennes** (k-means) cherchent **k** groupes tels que chaque client soit proche du **centre** de son groupe. L'algorithme tient en quatre phrases :

1. on choisit k centres de départ ;
2. on affecte chaque client au **centre le plus proche** ;
3. on recalcule chaque centre comme la **moyenne** de ses clients ;
4. on recommence les étapes 2 et 3 jusqu'à ce que les affectations ne changent plus.

Six clients, deux variables : le nombre de commandes et le panier moyen (en €).

| Client | A | B | C | D | E | F |
|---|---|---|---|---|---|---|
| Commandes | 1 | 2 | 2 | 9 | 10 | 12 |
| Panier moyen | 60 | 80 | 70 | 95 | 110 | 100 |

Les deux variables n'ont pas la même échelle (des unités contre des dizaines d'euros) : on les **standardise** d'abord, c'est-à-dire que l'on retire la moyenne et que l'on divise par l'écart-type. Les moyennes sont 6 commandes et 85,83 €, les écarts-types 4,43 et 17,42. On obtient les valeurs standardisées suivantes, puis les distances euclidiennes aux deux centres de départ (on prend les clients A et F, au hasard).

| Client | Commandes (z) | Panier (z) | Distance à A | Distance à F | Segment |
|---|---|---|---|---|---|
| A | −1,13 | −1,48 | 0,00 | 3,38 | 1 |
| B | −0,90 | −0,33 | 1,17 | 2,52 | 1 |
| C | −0,90 | −0,91 | 0,61 | 2,83 | 1 |
| D | 0,68 | 0,53 | 2,70 | 0,73 | 2 |
| E | 0,90 | 1,39 | 3,52 | 0,73 | 2 |
| F | 1,35 | 0,81 | 3,38 | 0,00 | 2 |

La distance de B à A vaut $\sqrt{(-0{,}90+1{,}13)^2+(-0{,}33+1{,}48)^2}\approx1{,}17$ : c'est un théorème de Pythagore sur les valeurs standardisées. Chaque client rejoint le centre le plus proche : A, B, C forment le segment 1, D, E, F le segment 2. On recalcule alors les centres : celui du segment 1 est $(-0{,}98 ; -0{,}91)$, celui du segment 2 est $(0{,}98 ; 0{,}91)$. Recalculées, les distances donnent **les mêmes affectations** : l'algorithme a convergé en une itération. La somme des carrés des distances de chaque client à son centre, que l'on appelle l'**inertie**, vaut environ 1,3 ; c'est la quantité que l'algorithme cherche à rendre petite.

```python hide
pts = pd.DataFrame({"commandes": [1, 2, 2, 9, 10, 12], "panier": [60, 80, 70, 95, 110, 100]}, index=list("ABCDEF"))
m, sd = pts.mean(), pts.std(ddof=0)
z = (pts - m) / sd
assert (round(m["commandes"], 2), round(m["panier"], 2), round(sd["commandes"], 2), round(sd["panier"], 2)) == (6.0, 85.83, 4.43, 17.42)
assert np.allclose(z.values, [[-1.13, -1.48], [-0.9, -0.33], [-0.9, -0.91], [0.68, 0.53], [0.9, 1.39], [1.35, 0.81]], atol=0.006)
dA = np.sqrt(((z.values - z.values[0]) ** 2).sum(1)); dF = np.sqrt(((z.values - z.values[5]) ** 2).sum(1))
assert np.allclose(dA, [0.0, 1.17, 0.61, 2.7, 3.52, 3.38], atol=0.015) and np.allclose(dF, [3.38, 2.52, 2.83, 0.73, 0.73, 0.0], atol=0.015)   # tableau arrondi à deux décimales
lab = (dF < dA).astype(int)
assert lab.tolist() == [0, 0, 0, 1, 1, 1]
c1, c2 = z.values[lab == 0].mean(0), z.values[lab == 1].mean(0)
assert np.allclose(c1, [-0.98, -0.91], atol=0.015) and np.allclose(c2, [0.98, 0.91], atol=0.015)
lab2 = (np.linalg.norm(z.values - c2, axis=1) < np.linalg.norm(z.values - c1, axis=1)).astype(int)
assert lab2.tolist() == lab.tolist()
inertie = ((z.values[lab == 0] - c1) ** 2).sum() + ((z.values[lab == 1] - c2) ** 2).sum()
assert 1.25 < inertie < 1.35, inertie
```

### 4.1.4 Préparer les variables avant de regrouper

Les k-moyennes mesurent des **distances** : tout ce qui change l'échelle d'une variable change le résultat. Trois précautions s'imposent pour nos 4 806 clients.

- **Choisir des variables qui décrivent un comportement et qui n'ont pas de lien mécanique entre elles.** Nous retenons cinq variables : le nombre de commandes, le panier moyen, la récence (jours depuis la dernière commande), la part de commandes passées sur le Site, et la part de commandes avec un code promotionnel. Nous n'utilisons pas le chiffre d'affaires total, qui est le produit du nombre de commandes par le panier.
- **Rendre symétriques les variables très asymétriques.** Le nombre de commandes va de 1 à 88 et la récence de 0 à 1 094 jours : on prend leur **logarithme**, sinon quelques gros clients tirent les centres.
- **Standardiser**, pour que chaque variable pèse autant.

```python
X = O.variables_kmeans(g)              # logarithme du nombre de commandes, du panier et de la récence ; parts du Site et des promotions
Z = StandardScaler().fit_transform(X)
km = KMeans(n_clusters=4, n_init=10, random_state=0).fit(Z)
g["segment"] = O.nommer_segments(g, km.labels_)
print(g["segment"].value_counts())
```
<!--sortie-->
```text
segment
Réguliers actifs           2295
Dormants de la Boutique    1066
Dormants du Site           1053
Chasseurs de promotions     392
Name: count, dtype: int64
```

Que se passe-t-il si l'on oublie ces précautions ? Les mêmes cinq variables, en unités naturelles (commandes, euros, jours, parts), donnent des groupes **très différents** : le nombre de jours depuis la dernière commande, qui varie sur des centaines d'unités, écrase les parts qui varient entre 0 et 1. Le résultat concorde faiblement avec le précédent (indice de Rand ajusté de 0,35 : 1 pour des groupes identiques, 0 pour des groupes sans rapport).

```python hide-code
Xr = pd.DataFrame({"n": g["n"], "panier": g["panier"], "rec": g["rec"], "site": g["site"], "promo": g["promo"]})
kr = KMeans(4, n_init=10, random_state=0).fit(Xr.values)
print("tailles des segments sans transformation ni standardisation :", sorted(int(x) for x in np.bincount(kr.labels_)), "| accord avec la version standardisée :", round(adjusted_rand_score(km.labels_, kr.labels_), 2))
assert sorted(int(x) for x in np.bincount(kr.labels_)) == [378, 641, 968, 2819] and round(adjusted_rand_score(km.labels_, kr.labels_), 2) == 0.35
```
<!--sortie-->
```text
tailles des segments sans transformation ni standardisation : [378, 641, 968, 2819] | accord avec la version standardisée : 0.35
```

### 4.1.5 Combien de segments ? Le coude et la silhouette

L'algorithme demande k à l'avance. Deux outils aident à le choisir, aucun ne tranche seul.

- Le **coude** : on trace l'inertie (la dispersion à l'intérieur des groupes) selon k. Elle baisse toujours quand k augmente (avec autant de groupes que de clients, elle est nulle) ; on cherche un k après lequel la baisse devient lente. Sur nos données, la courbe descend régulièrement, **sans cassure nette**.
- La **silhouette** de chaque client compare la distance moyenne aux autres membres de son groupe (a) à la distance moyenne aux membres du groupe voisin le plus proche (b) : $s=(b-a)/\max(a,b)$. Elle vaut 1 si le client est bien à sa place, 0 s'il est entre deux groupes, un nombre négatif s'il est mal classé. On moyenne sur tous les clients.

```python
sil = {k: silhouette_score(Z, KMeans(k, n_init=10, random_state=0).fit_predict(Z), sample_size=3000, random_state=0) for k in range(2, 9)}
print({k: round(v, 3) for k, v in sil.items()})
```
<!--sortie-->
```text
{2: 0.23, 3: 0.264, 4: 0.276, 5: 0.213, 6: 0.224, 7: 0.224, 8: 0.206}
```

```python hide
ine = [KMeans(k, n_init=10, random_state=0).fit(Z).inertia_ for k in range(2, 9)]
O.fig_coude(ine, [sil[k] for k in range(2, 9)], list(range(2, 9)))
assert max(sil, key=sil.get) == 4
```
<!--sortie-->
```text
figure : ch04-coude-silhouette.png
```

![Inertie et silhouette moyenne selon le nombre de segments : la silhouette est maximale pour quatre segments, mais ne dépasse pas 0,28.](figures/ch04-coude-silhouette.png)

Le maximum est à **k = 4**, avec une silhouette de 0,276. Retenez l'ordre de grandeur plus que le maximum : on lit en général une silhouette supérieure à 0,5 comme une structure nette, entre 0,25 et 0,5 comme **faible**, et en dessous comme absente. Notre clientèle ne forme donc pas des îlots séparés : c'est un **nuage continu** que l'algorithme découpe en quatre morceaux utiles. Cela n'invalide pas la segmentation, mais change ce qu'on peut en dire : les frontières sont des conventions commodes, pas des faits.

> 💡 **Intuition.** Segmenter un nuage continu ressemble à découper un pays en régions : les frontières sont tracées pour la commodité de la gestion, pas parce que les habitants changent brusquement d'un côté à l'autre. Cela suffit pour gérer, pourvu qu'on s'en souvienne.

### 4.1.6 Lire et nommer les segments

Un segment n'existe pour la gérante que lorsqu'il a un **nom** et un **profil**. On le lit de deux façons : un tableau en unités naturelles, et une carte de chaleur des écarts à la moyenne générale (en écarts-types), qui montre d'un coup d'œil ce qui distingue chaque groupe.

```python hide-code
prof = g.groupby("segment").agg(clients=("n", "size"), commandes=("n", "mean"), panier=("panier", "mean"), recence_mediane=("rec", "median"),
                                part_site=("site", "mean"), part_promo=("promo", "mean"), ca=("ca", "sum"))
prof["part_ca_%"] = prof["ca"] / prof["ca"].sum() * 100
ordre = ["Réguliers actifs", "Chasseurs de promotions", "Dormants du Site", "Dormants de la Boutique"]
print(prof.loc[ordre].drop(columns="ca").round(2).to_string())
assert int(prof.loc["Réguliers actifs", "clients"]) == 2295 and round(prof.loc["Réguliers actifs", "part_ca_%"], 1) == 81.6
```
<!--sortie-->
```text
                         clients  commandes  panier  recence_mediane  part_site  part_promo  part_ca_%
segment                                                                                               
Réguliers actifs            2295      12.84  101.85             29.0       0.42        0.16      81.62
Chasseurs de promotions      392       2.28   85.18            225.5       0.45        0.76       2.08
Dormants du Site            1053       2.96   96.51            220.0       0.76        0.06       8.19
Dormants de la Boutique     1066       2.75  105.59            290.0       0.10        0.06       8.11
```

```python hide
zs = pd.DataFrame(Z, index=X.index, columns=["Commandes", "Panier", "Récence", "Part Site", "Part promo"]).assign(segment=g["segment"]).groupby("segment").mean().loc[ordre]
O.fig_profils(zs, g["segment"].value_counts().to_dict())
```
<!--sortie-->
```text
figure : ch04-profils-segments.png
```

![Écart de chaque segment à la moyenne générale pour les cinq variables de la segmentation, en écarts-types : rouge au-dessus, bleu en dessous.](figures/ch04-profils-segments.png)

On y lit quatre profils.

- **Les réguliers actifs** (2 295 clients, 48 % de la clientèle active) : près de 13 commandes en trois ans, une dernière commande vieille de 29 jours en médiane. Ils réalisent **82 % du chiffre d'affaires**.
- **Les chasseurs de promotions** (392 clients) : seulement 2,3 commandes en moyenne, un panier plus petit (85 €), et **76 % de leurs commandes passent par un code promotionnel**. C'est le profil le plus facile à reconnaître, la carte de chaleur le désigne par la valeur +2,6 sur la part de promotions.
- **Les dormants du Site** (1 053 clients) et **les dormants de la Boutique** (1 066 clients) : trois commandes environ, dont la dernière date de 220 jours et 290 jours en médiane ; ce qui les sépare est le **canal** (76 % de commandes sur le Site contre 10 %).

Un nom doit **suggérer l'action**. « Réguliers actifs » : on les remercie. « Chasseurs de promotions » : une étiquette à **tester** avant d'agir (voir la section suivante : elle tient mal dans le temps). « Dormants » : on les relance, par le canal qu'ils utilisent. Un nom comme « segment 3 » ne dit rien à la gérante, qui oubliera de s'en servir.

### 4.1.7 Vérifier : stabilité et pouvoir de prédiction

Une segmentation qui n'a pas été éprouvée est une jolie image. Deux épreuves, simples, la rendent crédible.

**La stabilité.** Si l'on retire ou remplace quelques clients, retrouve-t-on les mêmes groupes ? On rééchantillonne cinq fois la clientèle (avec remise), on refait la segmentation, et l'on compare ses affectations à celles de la segmentation de référence par l'indice de Rand ajusté.

```python hide-code
aris = []
for s in range(1, 6):
    idx = np.random.default_rng(s).choice(len(Z), len(Z), replace=True)
    k2 = KMeans(4, n_init=10, random_state=s).fit(Z[idx])
    aris.append(adjusted_rand_score(km.labels_, k2.predict(Z)))
print("accord avec la segmentation de référence sur cinq rééchantillonnages :", [round(a, 2) for a in aris])
assert round(min(aris), 2) == 0.91 and round(max(aris), 2) == 0.99
```
<!--sortie-->
```text
accord avec la segmentation de référence sur cinq rééchantillonnages : [0.91, 0.99, 0.96, 0.94, 0.93]
```

Les accords vont de 0,91 à 0,99 : les groupes ne dépendent pas de l'échantillon, c'est rassurant.

**Le pouvoir de prédiction.** Un segment utile prédit **quelque chose que l'on n'a pas utilisé pour le fabriquer**. On se place au 30 juin 2025 : on construit les segments avec les seules données connues à cette date, puis on regarde ce que font les clients au **second semestre**. Les segments distinguent-ils des comportements futurs ?

```python hide
t0 = pd.Timestamp("2025-06-30")
c0 = cmd[cmd["date_commande"] <= t0]
g0 = O.table_clients(c0, lig[lig["id_commande"].isin(c0["id_commande"])], t0)
Z0 = StandardScaler().fit_transform(O.variables_kmeans(g0))
g0["segment"] = O.nommer_segments(g0, KMeans(4, n_init=10, random_state=0).fit(Z0).labels_)
h2 = cmd[cmd["date_commande"] > t0].groupby("id_client").agg(n2=("id_commande", "size"), ca2=("ca", "sum"))
g0 = g0.join(h2)
g0[["n2", "ca2"]] = g0[["n2", "ca2"]].fillna(0)
```

```python hide-code
val = g0.groupby("segment").agg(eff=("n", "size"), achat=("n2", lambda s: (s > 0).mean() * 100), ca2=("ca2", "mean")).loc[ordre]
val.attrs["global"] = (g0["n2"] > 0).mean() * 100
print(val.round(1).to_string())
print("ensemble :", len(g0), "clients,", round(val.attrs["global"], 1), "% ont commandé,", round(g0["ca2"].mean(), 1), "€ par client")
assert [int(x) for x in val["eff"]] == [2018, 431, 896, 1064] and round(val.loc["Réguliers actifs", "achat"], 1) == 83.3
```
<!--sortie-->
```text
                          eff  achat    ca2
segment                                    
Réguliers actifs         2018   83.3  253.0
Chasseurs de promotions   431   49.2   91.4
Dormants du Site          896   45.0   73.8
Dormants de la Boutique  1064   43.5   76.6
ensemble : 4409 clients, 62.6 % ont commandé, 158.2 € par client
```

```python hide
O.fig_validation(val)
```
<!--sortie-->
```text
figure : ch04-validation-segments.png
```

![Part de clients ayant commandé au second semestre 2025, selon le segment construit au 30 juin.](figures/ch04-validation-segments.png)

Les segments **prédisent** : 83 % des réguliers actifs commandent au second semestre et dépensent 253 € en moyenne, contre 43 à 49 % et 74 à 91 € pour les trois autres groupes ; la moyenne générale (63 % et 158 €) cache cet écart. Notez ce que le test **ne dit pas** : les trois derniers segments ne se distinguent presque pas entre eux sur ce critère (43 % à 49 %). Si la gérante voulait un traitement différent pour eux, il faudrait que la différence entre eux soit visible sur *une autre* mesure, par exemple la sensibilité aux promotions. L'exercice 4.4 du cahier fait précisément ce test pour les « chasseurs de promotions » : au second semestre, **15,9 %** de leurs commandes utilisent un code promotionnel, contre 12,5 à 14,1 % pour les trois autres segments. Leur étiquette, fondée sur 76 % de commandes avec code sur deux ou trois commandes en tout, était en grande partie un **effet de petits nombres** : le nom promettait plus que les données ne tiennent.

> ⚠️ **Piège : les segments bougent.** Une segmentation décrit les clients à **une date**. Entre le 30 juin et le 31 décembre, **22,5 %** des clients présents aux deux dates changent de segment (77,5 % restent dans le leur). Refaire la segmentation périodiquement, avec les mêmes variables et les mêmes règles de nommage, est une tâche courante ; la comparer à la précédente en fait un outil de suivi (qui entre chez les réguliers ? qui en sort ?).

```python hide
com = g0.index.intersection(g.index)
ct = pd.crosstab(g0.loc[com, "segment"], g.loc[com, "segment"])
rest = np.trace(ct.reindex(index=ct.columns, columns=ct.columns).fillna(0).values) / ct.values.sum() * 100
assert round(rest, 1) == 77.5
```

### 4.1.8 Les pièges de la segmentation

Quatre erreurs reviennent presque toujours.

1. **Segmenter sur ce que l'on veut ensuite comparer.** Si l'on fabrique les segments avec le chiffre d'affaires, il est évident que les segments diffèrent par leur chiffre d'affaires : c'est un cercle. Les variables de la segmentation décrivent le comportement ; le critère de validation doit être **extérieur** (ici, la commande du semestre suivant).
2. **Trop de segments.** Avec huit segments, la silhouette tombe à 0,206 : on découpe du bruit. Un segment qu'on ne sait pas nommer, ni traiter différemment, n'a pas de raison d'exister. Le nombre utile est souvent celui des **actions distinctes** dont on dispose.
3. **Oublier la standardisation** (section 4.1.4) : l'algorithme ne regroupe alors que la variable qui a les plus grandes unités.
4. **Prendre les segments pour des causes.** Les chasseurs de promotions achètent avec des codes ; cela ne prouve pas que la promotion les fait acheter plus qu'ils ne le feraient sans elle. Un segment décrit, il n'explique pas (voir la section 1.4 du volume I et la section 2.3 pour la différence entre corrélation et causalité, et le chapitre 3 pour les outils qui isolent un effet).

> ✅ **À retenir.** Une segmentation est un **outil de décision**, pas une découverte. Commencez par des règles lisibles ; si vous utilisez les k-moyennes, transformez et standardisez les variables, choisissez k avec le coude **et** la silhouette **et** votre capacité d'agir, donnez un nom qui suggère l'action, puis **éprouvez** les segments (stabilité, prédiction d'un critère extérieur) et refaites-les régulièrement.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.1 à 4.3, exercices 4.1 à 4.4.
