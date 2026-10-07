## 4.3 ➕ Pour aller plus loin : analyse RFM, valeur vie client, analyse du churn

> 🧭 **Section complémentaire.** Trois outils d'usage courant en relation client, qui prolongent les segments et les cohortes : un score simple pour classer les clients (**RFM**), une estimation de ce qu'un client rapporte pendant sa vie (**valeur vie client**), et une manière sérieuse de parler de clients « perdus » (**churn**). Ils ne sont pas nécessaires à la suite du volume.

```python hide
import sys, warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import numpy as np, pandas as pd
import outils_ch04 as O
T = O.charger()
cli, cmd, lig, sess, prod = T["cli"], T["cmd"], T["lig"], T["sess"], T["prod"]
g = O.table_clients(cmd, lig)
eff, taux, ca_client = O.matrice_cohortes(cli, cmd, pas="Q")
```

### 4.3.1 Le score RFM : récence, fréquence, montant

Le **RFM** résume un client par trois nombres : sa **récence** (depuis combien de jours a-t-il commandé pour la dernière fois ?), sa **fréquence** (combien de commandes ?) et son **montant** (combien a-t-il dépensé ?). L'idée est ancienne et robuste : les meilleurs clients sont récents, fréquents et dépensiers, et les trois mesures se calculent en une requête.

Le procédé tient en trois gestes.

1. **Découper chaque mesure en cinq groupes de même taille** (les quintiles) et donner un score de 1 (faible) à 5 (fort). Pour la récence, c'est le plus **récent** qui reçoit 5.
2. **Combiner** les scores en segments nommés : par exemple les clients à R ≥ 4 et F ≥ 4 sont des « champions », ceux à R ≤ 2 et F ≥ 4 sont des « gros clients à risque » (ils étaient bons, ils se sont tus).
3. **Vérifier** que les segments se comportent comme leur nom le dit.

Une précaution technique, que l'on oublie souvent : la fréquence compte beaucoup d'**ex æquo** (17 % de nos clients n'ont passé qu'une commande). Un découpage en quintiles sur les valeurs brutes donnerait des groupes de tailles inégales, voire impossibles. On classe donc les clients par **rang** avant de découper, et les ex æquo sont départagés arbitrairement : il faut le savoir pour ne pas sur-interpréter la différence entre deux clients de même fréquence.

```python
s = O.rfm(g)                                    # scores R, F, M de 1 à 5 par quintiles de rang
s["segment"] = [O.nom_segment_rfm(r, f) for r, f in zip(s["R"], s["F"])]
t = g.join(s).groupby("segment").agg(clients=("n", "size"), recence_med=("rec", "median"), commandes=("n", "mean"), ca=("ca", "sum"))
t["part_clients"] = t["clients"] / t["clients"].sum() * 100
t["part_ca"] = t["ca"] / t["ca"].sum() * 100
print(t.drop(columns="ca").sort_values("part_ca", ascending=False).round(1))
```
<!--sortie-->
```text
                         clients  recence_med  commandes  part_clients  part_ca
segment                                                                        
Champions                   1221         18.0       16.3          25.4     54.6
Fidèles                      995         64.0        8.4          20.7     23.0
À risque (gros clients)      257        209.0       10.1           5.3      7.3
À surveiller                 713        176.0        3.6          14.8      7.0
Perdus                      1256        422.0        1.8          26.1      6.1
Nouveaux ou récents          364         21.0        2.1           7.6      2.0
```

```python hide
O.fig_rfm(pd.crosstab(s["R"], s["F"]))
assert [int(x) for x in t.loc[["Champions", "Fidèles", "À risque (gros clients)", "À surveiller", "Perdus", "Nouveaux ou récents"], "clients"]] == [1221, 995, 257, 713, 1256, 364]
assert round(t.loc["Champions", "part_ca"], 1) == 54.6 and round(g["n"].eq(1).mean() * 100) == 17
```
<!--sortie-->
```text
figure : ch04-rfm.png
```

![Nombre de clients par couple de scores (récence R, fréquence F) : la diagonale est dense, les coins opposés sont presque vides.](figures/ch04-rfm.png)

Le tableau est parlant : **25 % des clients (les champions) font 55 % du chiffre d'affaires**, 26 % (les perdus) en font 6 %. La grille de la figure montre aussi une structure réelle : les clients **récents et fréquents** (en haut à droite) et **anciens et rares** (en bas à gauche) sont nombreux, les deux autres coins presque vides : ceux qui commandent souvent et ne sont plus revenus depuis longtemps sont rares, mais c'est précisément le groupe « gros clients à risque » (257 clients, 7 % du chiffre d'affaires) qu'un coup de téléphone peut sauver.

**La vérification** est la même qu'à la section 4.1 : se placer au 30 juin 2025, scorer les clients avec les données connues à cette date, et regarder qui commande au second semestre.

```python hide-code
t0 = pd.Timestamp("2025-06-30")
c0 = cmd[cmd["date_commande"] <= t0]
g0 = O.table_clients(c0, lig[lig["id_commande"].isin(c0["id_commande"])], t0)
s0 = O.rfm(g0)
s0["segment"] = [O.nom_segment_rfm(r, f) for r, f in zip(s0["R"], s0["F"])]
h2 = cmd[cmd["date_commande"] > t0].groupby("id_client").agg(n2=("id_commande", "size"), ca2=("ca", "sum"))
j = g0.join(s0).join(h2)
j[["n2", "ca2"]] = j[["n2", "ca2"]].fillna(0)
v = j.groupby("segment").agg(clients=("n", "size"), achat=("n2", lambda x: (x > 0).mean() * 100), ca2=("ca2", "mean")).sort_values("achat", ascending=False)
print(v.round(1).to_string())
assert round(v.loc["Champions", "achat"], 1) == 89.9 and round(v.loc["Perdus", "achat"], 1) == 35.5
```
<!--sortie-->
```text
                         clients  achat    ca2
segment                                       
Champions                   1102   89.9  305.4
À risque (gros clients)      268   78.0  178.5
Fidèles                      963   71.9  173.2
À surveiller                 567   51.5   90.5
Nouveaux ou récents          325   47.7  104.0
Perdus                      1184   35.5   51.7
```

Les segments sont **ordonnés comme annoncé** : 90 % des champions recommandent dans les six mois (305 € de chiffre d'affaires par client), contre 36 % des perdus (52 €). Remarquez la ligne « Perdus » : **un client sur trois classé « perdu » recommande dans les six mois**. Nous y revenons à la section 4.3.3.

> ⚠️ **Piège.** Le RFM est **simple, donc fragile** : les trois scores pèsent autant sans raison, les quintiles de rang sont relatifs à la clientèle du moment (un « 5 » de récence n'a pas le même sens après un mois creux), et les noms des segments dépendent de seuils arbitraires. Utilisez-le pour **prioriser des actions**, pas pour établir une vérité. Et ne le confondez pas avec une segmentation statistique : le RFM classe sur **trois** variables fixées d'avance.

### 4.3.2 La valeur vie client

La **valeur vie client** (en anglais *customer lifetime value*, CLV) est ce qu'un client rapporte en tout, pendant qu'il est client. On l'utilise pour décider de ce qu'on peut dépenser pour l'acquérir (un client qui rapporte 70 € de marge justifie moins de publicité qu'un client qui en rapporte 400 €) et pour comparer des segments.

**La formule simple.** Elle suppose que le client rapporte chaque année la même **marge** et qu'il reste client avec une probabilité constante $\rho$ d'une année à l'autre :

$$\text{CLV}=m\sum_{t\ge0}\left(\frac{\rho}{1+i}\right)^t=\frac{m}{1-\rho/(1+i)},$$

où $m$ est la marge annuelle d'un client actif, $\rho$ la **rétention annuelle** et $i$ un taux d'actualisation (un euro dans un an vaut moins qu'un euro aujourd'hui). Sans actualisation ($i=0$), c'est simplement $m$ multiplié par la **durée de vie moyenne** $1/(1-\rho)$.

Avec les chiffres de 2025 : on compte 3 875 clients actifs ; la marge brute hors taxe de l'année est de 419 017 €, soit **108 € par client actif** ; sur 3 479 clients actifs en 2024, 2 828 le sont encore en 2025, soit une rétention de 81,3 % (une perte de 18,7 %), qui donne une durée de vie de 5,3 ans. Sans actualisation, $\text{CLV}=108\times5{,}35\approx578$ € ; avec un taux fictif de 8 %, 437 €.

```python hide-code
c25 = cmd[cmd["date_commande"].dt.year == 2025]
act25 = c25["id_client"].nunique()
x = lig.merge(cmd[["id_commande", "date_commande"]], on="id_commande").merge(prod[["id_produit", "cout_achat"]], on="id_produit")
x = x[x["date_commande"].dt.year == 2025]
marge25 = (x["montant"] / 1.2 - x["quantite"] * x["cout_achat"]).sum()
a24 = set(cmd.loc[cmd["date_commande"].dt.year == 2024, "id_client"]); a25 = set(c25["id_client"])
rho = len(a24 & a25) / len(a24)
m = marge25 / act25
print("clients actifs 2025 :", act25, "| marge brute HT 2025 :", round(marge25), "€ | marge par client actif :", round(m, 1), "€")
print("rétention 2024 -> 2025 :", len(a24 & a25), "sur", len(a24), "=", round(rho * 100, 1), "% | durée de vie :", round(1 / (1 - rho), 2), "ans")
print("CLV sans actualisation :", round(m / (1 - rho)), "€ | avec 8 % :", round(m / (1 - rho / 1.08)), "€")
assert (act25, len(a24), len(a24 & a25), round(marge25), round(m, 1)) == (3875, 3479, 2828, 419017, 108.1)
assert (round(m / (1 - rho)), round(m / (1 - rho / 1.08))) == (578, 437)
```
<!--sortie-->
```text
clients actifs 2025 : 3875 | marge brute HT 2025 : 419017 € | marge par client actif : 108.1 €
rétention 2024 -> 2025 : 2828 sur 3479 = 81.3 % | durée de vie : 5.34 ans
CLV sans actualisation : 578 € | avec 8 % : 437 €
```

**La version empirique par cohortes.** Mais ces 578 € surestiment ce que rapporte un **nouveau** client : la formule suit les clients **actifs**, un groupe déjà trié (un client qui n'a jamais commandé n'y figure pas). Observons plutôt ce que rapportent les clients **inscrits**, grâce aux cohortes de la section 4.2 : sur les quatre premiers trimestres, un client inscrit rapporte en moyenne **219 €** de chiffre d'affaires, soit environ **69 €** de marge brute hors taxe (le taux de marge de 2025 est de 31,6 % du chiffre d'affaires toutes taxes comprises) ; sur les huit premiers trimestres, 446 € de chiffre d'affaires, soit environ 141 € de marge.

Les deux estimations ne se contredisent pas : 69 € est à peu près **108 € × 3 875 / 6 000**, c'est-à-dire la marge par client actif, répartie sur **tous** les clients inscrits (en 2025, 3 875 des 6 000 inscrits ont commandé, soit 65 %). La différence est une question de **dénominateur**, et c'est le piège numéro un de la valeur vie client : *par client de quoi ?*

> ⚠️ **Les pièges de la valeur vie client.**
> 1. **Revenu ou marge ?** Une valeur vie en chiffre d'affaires n'est pas une valeur vie en marge ; seule la seconde se compare à un coût d'acquisition.
> 2. **L'horizon.** Dire « 578 € » suppose que les clients durent 5,3 ans en moyenne, alors que nos données n'ont que trois ans d'histoire : le reste est une **extrapolation**. Préférez une valeur à horizon donné (« 141 € de marge sur deux ans »).
> 3. **L'hypothèse de rétention constante.** Elle est fausse si les clients diffèrent (c'est le cas : section 4.3.3).
> 4. **La moyenne.** Le revenu moyen d'un client sur la période est de 760 €, sa médiane de 474 € : les 10 % de meilleurs clients font 36 % du chiffre d'affaires, les 20 % meilleurs 55 %. Une moyenne de valeur vie masque cette concentration ; donnez la médiane et la part des meilleurs.
> 5. **L'actualisation** : un taux de 8 % est un exemple, pas une vérité ; la valeur change de 578 € à 437 € selon qu'on actualise ou non.

```python hide
assert (round(g["ca"].mean()), round(g["ca"].median())) == (760, 474)
srt = g["ca"].sort_values(ascending=False)
assert (round(srt.head(int(0.1 * len(g))).sum() / g["ca"].sum() * 100), round(srt.head(int(0.2 * len(g))).sum() / g["ca"].sum() * 100)) == (36, 55)
assert round(ca_client.iloc[:5, :8].sum(axis=1).mean()) == 446 and round(marge25 / (c25["ca"].sum()) * 100, 1) == 31.6
```

### 4.3.3 Le churn : un client silencieux est-il un client perdu ?

Le **churn** (ou attrition) est la perte de clients. Le mot paraît simple, mais il cache une question de **définition** : dans une boutique, **où est la frontière entre un client « endormi » et un client « parti » ?** Un abonnement donne la réponse (le client résilie) ; un achat libre ne la donne pas : il n'y a pas de résiliation, seulement du silence.

**Première approche : un taux annuel.** On compte les clients actifs une année et l'on regarde combien ne le sont plus la suivante : **18,7 %** des clients actifs en 2024 n'ont rien commandé en 2025 (3 479 actifs, 2 828 encore actifs), et 18,8 % entre 2023 et 2024. C'est stable, donc utilisable. Mais c'est un taux **de silence sur douze mois**, pas un taux de départ : un client silencieux en 2025 peut commander en 2026.

**Seconde approche : la probabilité de revenir.** Plutôt que de décréter « perdu », demandons aux données quelle est la probabilité qu'un client commande à nouveau **selon le temps écoulé depuis sa dernière commande**. On se place au 30 juin 2025 : pour chaque client déjà connu, on note le nombre de jours depuis sa dernière commande, puis on regarde s'il recommande dans les six mois suivants.

```python
r = O.reachat(cmd, "2025-06-30")                     # récence au 30 juin 2025 et achat dans les 184 jours suivants
r["groupe"] = pd.cut(r["rec"], [-1, 30, 90, 180, 365, 2000], labels=["0-30 j", "31-90 j", "91-180 j", "181-365 j", "plus de 365 j"])
tb = r.groupby("groupe").agg(n=("reachete", "size"), p=("reachete", "mean"))
tb["p"] = (tb["p"] * 100).round(1)
print(tb)
```
<!--sortie-->
```text
                  n     p
groupe                   
0-30 j          847  77.6
31-90 j        1070  74.3
91-180 j        771  67.1
181-365 j       961  53.6
plus de 365 j   760  36.2
```

```python hide
O.fig_reachat(tb)
assert [int(x) for x in tb["n"]] == [847, 1070, 771, 961, 760] and [round(x, 1) for x in tb["p"]] == [77.6, 74.3, 67.1, 53.6, 36.2]
assert round(760 * 36.2 / 100) == 275
a23 = set(cmd.loc[cmd["date_commande"].dt.year == 2023, "id_client"]); a24b = set(cmd.loc[cmd["date_commande"].dt.year == 2024, "id_client"])
assert round((1 - len(a23 & a24b) / len(a23)) * 100, 1) == 18.8 and round(3875 / 6000 * 100) == 65 and round(108.1 * 3875 / 6000) == 70
```
<!--sortie-->
```text
figure : ch04-reachat.png
```

![Part des clients qui commandent dans les six mois suivants, selon le nombre de jours écoulés depuis leur dernière commande au 30 juin 2025.](figures/ch04-reachat.png)

La probabilité de revenir **baisse régulièrement avec le silence**, mais **ne tombe jamais à zéro** : **36 % des clients silencieux depuis plus d'un an recommandent dans les six mois**. Décréter « perdu après douze mois » aurait classé 760 clients comme perdus, dont 275 seraient revenus. Le churn est une **probabilité**, pas un état.

Deux éléments de cadrage aident à choisir un seuil raisonnable. Le délai **habituel** entre deux commandes d'un même client est de 47 jours en médiane, mais 213 jours pour le 90ᵉ centile et 306 jours pour le 95ᵉ : un silence de 200 jours est banal pour une partie de la clientèle. Et la fréquence passée change tout : au 30 juin, parmi les clients qui n'avaient commandé **qu'une fois**, 33 % recommandent dans les six mois ; parmi ceux qui avaient commandé **dix fois et plus**, 94 %. Un seuil de silence doit donc **dépendre du rythme du client** (un gros client qui s'arrête trois mois est plus inquiétant qu'un acheteur annuel qui s'arrête huit mois).

```python hide
cs = cmd.sort_values(["id_client", "date_commande"])
gap = cs.groupby("id_client")["date_commande"].diff().dt.days.dropna()
assert (gap.median(), gap.quantile(0.9), gap.quantile(0.95)) == (47.0, 213.0, 306.0)
c0 = cmd[cmd["date_commande"] <= "2025-06-30"]
nb = c0.groupby("id_client").size()
r["nb"] = nb.reindex(r.index)
rb = r.groupby(pd.cut(r["nb"], [0, 1, 4, 9, 1000]))["reachete"].mean() * 100
assert [round(x) for x in rb.values] == [33, 50, 74, 94]
```

### 4.3.4 Du churn à l'action

Une probabilité de revenir sert à **décider qui relancer**. La logique est celle d'un arbitrage : relancer coûte (un code promotionnel, un message), et rapporte si le client revient *à cause* de la relance. Trois conséquences pratiques.

- **Ne pas relancer ceux qui reviendront seuls.** Les clients à 0–30 jours reviennent à 78 % sans rien faire : leur offrir un rabais est de l'argent perdu. À l'inverse, les 181–365 jours (54 %) et plus de 365 jours (36 %) sont ceux où une action peut changer quelque chose, à condition que la valeur d'un client retrouvé dépasse le coût de la relance.
- **Prédire avec plusieurs variables.** Pour aller plus loin que la seule récence, on estime la probabilité de recommander par une **régression logistique** (récence, fréquence, panier, canal, part de promotions…) : c'est exactement l'outil de la section 3.3. Le gain par rapport à la grille de récence se mesure sur des données **qui n'ont pas servi** à l'estimation (comme ci-dessus : on construit à une date, on évalue après).
- **Mesurer l'effet réel de la relance** par un test A/B (chapitre 2, section 2.2), car la corrélation « les relancés reviennent plus » ne prouve pas que la relance en est la cause : les clients relancés sont souvent choisis parce qu'ils sont déjà plus actifs.

> ✅ **À retenir.** Le **RFM** classe les clients sur trois mesures simples (quintiles de rang, segments nommés) et se vérifie en regardant ce que font les segments ensuite. La **valeur vie client** dépend du dénominateur (clients actifs ou inscrits), de l'horizon, de la marge et de l'actualisation : annoncez-la avec ces quatre précisions et à horizon fini. Le **churn** est une probabilité qui dépend du temps de silence et du rythme du client : un client silencieux n'est pas un client perdu.

> 📒 **Pour s'entraîner.** Cahier, chapitre 4 : applications 4.6 et 4.7, exercices 4.9 et 4.10.
