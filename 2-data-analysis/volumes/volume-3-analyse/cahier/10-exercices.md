# Chapitre 10 : ➕ Analytique marketing et web — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 10 du livre. Les **applications** se font devant l'ordinateur, par petites étapes ; les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ difficile) ont des corrigés à la fin. Les données sont **simulées** ; les parcours multi-contacts, le groupe témoin, la vue d'outil et les doublons d'événements sont **fabriqués** par `build/outils_ch10.py` et signalés comme tels. Google Analytics n'est pas exécuté.

```python
import os, sys, warnings
import numpy as np, pandas as pd
warnings.filterwarnings("ignore")
sys.path.insert(0, "build")
import outils_ch10 as O

s, camp, cmd, lig, prod = O.charger()
m = O.marge_commandes(cmd, lig, prod)
w = s[s["id_commande"].notna()].merge(m, on="id_commande")
print(len(s), "sessions |", int(s["commande"].sum()), "commandes |", len(camp), "lignes de campagne")
```
<!--sortie-->
```text
127022 sessions | 6078 commandes | 36 lignes de campagne
```

## Applications

### Application 10.1 — La conversion par source, avec son incertitude (section 10.1.2)

**Objectif.** Calculer la conversion de chaque source et dire quelles différences sont fiables.

**Étape 1 — la table.**

```python
g = s.groupby("source").agg(sessions=("commande", "size"), commandes=("commande", "sum"))
g["conversion_%"] = (g["commandes"] / g["sessions"] * 100).round(2)
ic = [O.wilson(k, n) for k, n in zip(g["commandes"], g["sessions"])]
g["ic_bas_%"], g["ic_haut_%"] = [round(a * 100, 2) for a, b in ic], [round(b * 100, 2) for a, b in ic]
print(g.sort_values("conversion_%").to_string())
```
<!--sortie-->
```text
           sessions  commandes  conversion_%  ic_bas_%  ic_haut_%
source                                                           
reseaux       15243        329          2.16      1.94       2.40
payant        17783        535          3.01      2.77       3.27
referent       6351        239          3.76      3.32       4.26
organique     43187       1736          4.02      3.84       4.21
direct        35566       2467          6.94      6.68       7.21
email          8892        772          8.68      8.11       9.29
```

**Étape 2 — deux sources se distinguent-elles ?** Deux intervalles qui se recouvrent ne prouvent pas une égalité, mais l'absence de recouvrement est un signe net. Comparez le payant et l'organique, puis le référent et l'organique, avec un test de deux proportions.

```python
from statsmodels.stats.proportion import proportions_ztest
for a, b in [("payant", "organique"), ("referent", "organique")]:
    ka, na, kb, nb = g.loc[a, "commandes"], g.loc[a, "sessions"], g.loc[b, "commandes"], g.loc[b, "sessions"]
    z, p = proportions_ztest([ka, kb], [na, nb])
    print(f"{a} contre {b} : écart {(ka / na - kb / nb) * 100:+.2f} point | z = {z:.2f} | p = {p:.4f}")
```
<!--sortie-->
```text
payant contre organique : écart -1.01 point | z = -5.99 | p = 0.0000
referent contre organique : écart -0.26 point | z = -0.98 | p = 0.3292
```

**Lecture.** Le payant convertit 1,01 point de moins que l'organique : l'écart est **très significatif**. Le référent (3,76 %) et l'organique (4,02 %) ont des intervalles qui se recouvrent, et le test donne un écart de −0,26 point avec une probabilité critique d'environ 0,33 : **on ne peut pas** dire qu'ils diffèrent.

**À vous.** Ajoutez la comparaison e-mail contre direct. Qu'en concluez-vous, et quelle taille d'écart un test aurait-il détectée avec 6 351 sessions ?

### Application 10.2 — L'entonnoir par appareil (section 10.1.3)

**Objectif.** Trouver l'étape où l'on perd le plus selon l'appareil.

```python
f = s.groupby("appareil")[["ajout_panier", "debut_paiement", "commande"]].sum()
f["sessions"] = s.groupby("appareil").size()
tab = pd.DataFrame({"panier_%": f["ajout_panier"] / f["sessions"] * 100, "paiement_%": f["debut_paiement"] / f["ajout_panier"] * 100,
                    "commande_%": f["commande"] / f["debut_paiement"] * 100, "conversion_%": f["commande"] / f["sessions"] * 100}).round(2)
print(tab.to_string())
```
<!--sortie-->
```text
            panier_%  paiement_%  commande_%  conversion_%
appareil                                                  
mobile         14.35       57.17       58.69          4.81
ordinateur     14.11       57.37       58.41          4.73
tablette       14.35       56.01       60.23          4.84
```

**Lecture.** Les trois appareils ont des taux de passage voisins, et une conversion globale de 4,73 % à 4,84 % : dans ces données, **aucune étape n'est propre à un appareil**. Sur un site réel, un écart important au paiement sur mobile serait la première piste de travail.

**À vous.** Faites la même table par `nouveau_visiteur`, puis par source **et** appareil (six sources, trois appareils). Combien de cases ont moins de 500 sessions, et que cela change-t-il à la lecture ?

### Application 10.3 — La rentabilité par source payante (section 10.2.2 et 10.2.3)

**Objectif.** Calculer le ROAS, le ROI, le coût par commande et le coût d'acquisition d'un client.

**Étape 1 — dépense et marge.**

```python
dep = camp.groupby("source")["depense"].sum()
g2 = w.groupby("source").agg(commandes=("ca_ht", "size"), ca_ht=("ca_ht", "sum"), marge=("marge", "sum"), neufs=("premiere_commande", "sum"))
r = pd.DataFrame({"depense": dep}).join(g2)
r["cout_commande"] = r["depense"] / r["commandes"]
r["roas_ht"] = r["ca_ht"] / r["depense"]
r["roi_%"] = (r["marge"] - r["depense"]) / r["depense"] * 100
r["cac"] = r["depense"] / r["neufs"]
print(r[["depense", "commandes", "cout_commande", "roas_ht", "roi_%", "neufs", "cac"]].round(2).to_string())
```
<!--sortie-->
```text
          depense  commandes  cout_commande  roas_ht   roi_%  neufs      cac
source                                                                      
email     8239.76        772          10.67     7.51  180.23     42   196.18
payant   42374.19        535          79.20     1.04  -60.69     32  1324.19
reseaux  22528.77        329          68.48     1.28  -50.69     23   979.51
```

**Étape 2 — la valeur d'un client.** On compare le CAC à la marge qu'un client génère sur deux ans : pour les clients inscrits entre janvier et septembre 2023, on additionne la marge de leurs commandes dans les 730 jours suivant l'inscription.

```python
cli = pd.read_csv(os.path.join(O.D, "clients.csv"), parse_dates=["date_inscription"])
nv = cli[(cli["date_inscription"] >= "2023-01-01") & (cli["date_inscription"] < "2023-10-01")]
mm = m.merge(nv[["id_client", "date_inscription"]], on="id_client")
mm = mm[mm["date_commande"] < mm["date_inscription"] + pd.Timedelta(days=730)]
print(len(nv), "clients | marge sur 24 mois par client :", round(mm["marge"].sum() / len(nv), 1), "€ | commandes par client :", round(len(mm) / len(nv), 2))
```
<!--sortie-->
```text
515 clients | marge sur 24 mois par client : 149.1 € | commandes par client : 4.9
```

**Lecture.** Un client inscrit en 2023 a rapporté en moyenne **149,1 € de marge** en 730 jours, avec 4,9 commandes. Le CAC de l'e-mail (196 €) est du même ordre ; celui de la publicité payante (1 324 €) et des réseaux (980 €) est **six à neuf fois** la valeur du client. Mais seules 345 commandes sont des premières commandes : le CAC attribue toute la dépense aux nouveaux clients, ce qui le surestime. Le vrai coût se situe entre le coût par commande (79 €) et le CAC ; **seul un test** peut le dire.

**À vous.** Recalculez le ROI de la publicité payante **mois par mois**. Dans quels mois est-il le moins mauvais ? Ce résultat vient-il de la dépense, de la saison ou du hasard ?

### Application 10.4 — Attribution et groupe témoin (sections 10.2.5 et 10.2.6)

**Objectif.** Voir comment le modèle d'attribution déplace le mérite, puis mesurer l'incrémental avec son incertitude.

**Étape 1 — comparer quatre modèles** sur 4 000 parcours **fabriqués**.

```python
parcours = O.parcours_fabriques(4000)
cred = pd.DataFrame({mo: O.attribution(parcours, mo) for mo in ["dernier clic", "premier clic", "linéaire", "en U"]}).mul(100).round(1)
print(cred.loc[["direct", "email", "organique", "payant", "reseaux", "referent"]].to_string())
```
<!--sortie-->
```text
           dernier clic  premier clic  linéaire  en U
direct             40.8          16.6      26.5  27.7
email              24.6          11.6      19.0  18.5
organique          17.8          25.5      22.6  22.0
payant              9.6          21.0      14.8  15.1
reseaux             3.8          20.8      12.9  12.6
referent            3.4           4.6       4.3   4.1
```

**Étape 2 — l'incrémental avec son intervalle.** Dans le test fabriqué, la différence entre les taux d'achat exposé et témoin est un écart de proportions ; son incertitude se calcule comme au chapitre 2.

```python
t = O.test_temoin()
exp, tem = t[t["expose"] == 1]["achat"], t[t["expose"] == 0]["achat"]
p1, p0 = exp.mean(), tem.mean()
se = np.sqrt(p1 * (1 - p1) / len(exp) + p0 * (1 - p0) / len(tem))
print(f"écart : {(p1 - p0) * 100:.2f} point | intervalle à 95 % : de {(p1 - p0 - 1.96 * se) * 100:.2f} à {(p1 - p0 + 1.96 * se) * 100:.2f} point")
print("achats incrémentaux estimés :", round((p1 - p0) * len(exp)), "| intervalle :", round((p1 - p0 - 1.96 * se) * len(exp)), "à", round((p1 - p0 + 1.96 * se) * len(exp)))
```
<!--sortie-->
```text
écart : 0.36 point | intervalle à 95 % : de 0.02 à 0.70 point
achats incrémentaux estimés : 174 | intervalle : 10 à 338
```

**Lecture.** L'écart de 0,36 point a un intervalle de **0,02 à 0,70 point** (de 10 à 338 achats incrémentaux) : il exclut à peine zéro, et il est **très large**. Le dernier clic en attribuait 683. Même la borne haute de l'intervalle (338 achats) reste très en dessous.

**À vous.** Quelle taille de groupe témoin faudrait-il pour réduire de moitié l'intervalle ? (L'erreur type diminue en $1/\sqrt n$ : pour la diviser par deux, il faut quatre fois plus de personnes.)

### Application 10.5 — Réconcilier un outil d'analyse web (section 10.3)

**Objectif.** Mesurer la couverture d'un outil, puis corriger un ROAS avec le bon redressement.

```python
vue = O.vue_outil(s)
base_site = cmd[(cmd["canal"] == "Site") & (cmd["date_commande"] >= "2025-01-01")]
couverture = vue["commande"].sum() / len(base_site)
print("commandes du site en base :", len(base_site), "| vues par l'outil :", int(vue["commande"].sum()), f"| couverture : {couverture * 100:.1f} %")
par_source = (vue.groupby("source")["commande"].sum() / s.groupby("source")["commande"].sum() * 100).round(1)
print("couverture par source (%) :", par_source.to_dict())
```
<!--sortie-->
```text
commandes du site en base : 6078 | vues par l'outil : 4821 | couverture : 79.3 %
couverture par source (%) : {'direct': 84.5, 'email': 95.3, 'organique': 76.1, 'payant': 61.7, 'referent': 66.1, 'reseaux': 58.4}
```

**Redressement global ou par source ?** Si l'on divise les commandes vues par la couverture **globale**, on corrige en moyenne mais pas par source.

```python
dep = camp.groupby("source")["depense"].sum()
wv = vue[vue["id_commande"].notna()].merge(m, on="id_commande")
ca_vu = wv.groupby("source")["ca_ht"].sum()
vrai = w.groupby("source")["ca_ht"].sum()
tab = pd.DataFrame({"roas_vrai": vrai / dep, "roas_outil": ca_vu / dep, "roas_corrige_global": ca_vu / couverture / dep}).dropna().round(2)
print(tab.loc[["email", "reseaux", "payant"]].to_string())
```
<!--sortie-->
```text
         roas_vrai  roas_outil  roas_corrige_global
source                                             
email         7.51        7.14                 9.01
reseaux       1.28        0.74                 0.93
payant        1.04        0.65                 0.82
```

**Lecture.** Le redressement global donne un ROAS de la publicité payante de **0,82** pour une vérité de **1,04**, et de **0,93** pour les réseaux contre **1,28** : on **réduit** l'erreur mais l'écart reste de 20 à 27 %, parce que la couverture n'est pas la même partout (environ 62 % pour le payant, 58 % pour les réseaux et 95 % pour l'e-mail dans cette vue fabriquée) ; l'e-mail, lui, est **surestimé** (9,01 contre 7,51). Pour corriger source par source, il faudrait connaître la couverture de chacune : on ne l'a que si l'on peut comparer à une référence indépendante.

**À vous.** Quel serait le ROAS « corrigé » si l'on connaissait la couverture par source ? Que valent alors les trois ROAS ?

## Exercices

### Exercice 10.1 ⭐ — Un taux de conversion et son intervalle, à la main (section 10.1.2)

Une source a 2 000 sessions et 90 commandes. Calculez le taux de conversion, l'erreur type et l'intervalle de confiance à 95 % (approximation normale).

### Exercice 10.2 ⭐ — Lire un entonnoir (section 10.1.3)

Sur 10 000 sessions, 1 200 ajoutent au panier, 600 commencent le paiement et 400 commandent. Calculez les taux de passage, la conversion globale, et dites où se situe la perte la plus massive et la plus actionnable.

### Exercice 10.3 ⭐⭐ — Deux sources, une vraie différence ? (section 10.1.2)

Source A : 40 commandes sur 1 000 sessions. Source B : 50 commandes sur 1 000 sessions. L'écart de 1 point est-il significatif au seuil de 5 % ? Même question avec dix fois plus de sessions (400 contre 500 commandes). Que conclure ?

### Exercice 10.4 ⭐⭐ — L'effet de mélange (section 10.1.5)

Le site a 100 000 sessions et 5 000 commandes. On ajoute 10 000 sessions d'une source qui convertit à 2 %. Calculez la nouvelle conversion globale et le nombre de commandes ajoutées. La campagne est-elle « mauvaise » ?

### Exercice 10.5 ⭐ — ROAS et ROI (section 10.2.2)

On dépense 2 000 € et l'on attribue 5 000 € de chiffre d'affaires hors taxe, avec une marge brute de 38 % du chiffre d'affaires hors taxe. Calculez le ROAS, la marge dégagée, le ROI et dites si le canal est rentable.

### Exercice 10.6 ⭐⭐ — Le seuil de rentabilité du ROAS (section 10.2.2)

Calculez le ROAS minimal (hors taxe) pour couvrir une dépense publicitaire quand la marge brute vaut 30 %, 38 % et 45 % du chiffre d'affaires hors taxe. Pourquoi un ROAS de 2,5 peut-il être rentable pour un produit et ruineux pour un autre ?

### Exercice 10.7 ⭐⭐ — CAC et durée de retour (section 10.2.3)

On dépense 4 000 € pour acquérir 25 nouveaux clients. Un client génère 20 € de marge brute à sa première commande et 50 € de plus en moyenne sur les deux années suivantes. Calculez le CAC, le ratio valeur du client sur CAC, et dites si l'acquisition est rentable avec ou sans les commandes suivantes.

### Exercice 10.8 ⭐⭐⭐ — Attribution à la main (section 10.2.5)

Trois parcours d'achat : (réseaux, organique, direct), (payant, email), (direct). Calculez le mérite de chaque source selon le dernier clic, le premier clic et le modèle linéaire. Quelle source gagne ou perd le plus selon le modèle ?

### Exercice 10.9 ⭐⭐ — La couverture d'un outil (section 10.3.4)

Un outil voit 4 821 commandes quand la base en compte 6 078 pour le site. Calculez la couverture. Si l'outil annonce 90 000 € de chiffre d'affaires, quelle estimation donneriez-vous du chiffre d'affaires réel, et quelle hypothèse faites-vous ?

### Exercice 10.10 ⭐⭐⭐ — Des événements en double (section 10.3.5)

Un outil reçoit 6 262 événements « achat » pour 6 078 commandes distinctes, d'un montant moyen de 100 € (non transmis dans l'événement). De combien le chiffre d'affaires de l'outil est-il gonflé ? Comment le corriger, et que se passe-t-il si les doublons ne portent pas sur les mêmes montants que les autres commandes ?

## Corrigés

### Corrigé 10.1

Taux $p=90/2\,000=4{,}5\ \%$ ; erreur type $\sqrt{p(1-p)/n}=\sqrt{0{,}045\times0{,}955/2\,000}\approx0{,}0046$ ; intervalle $4{,}5\ \%\pm1{,}96\times0{,}46\ \%$, soit de **3,6 % à 5,4 %**.

```python
p, n = 90 / 2000, 2000
se = np.sqrt(p * (1 - p) / n)
print(round(p * 100, 2), round(se * 100, 3), round((p - 1.96 * se) * 100, 2), round((p + 1.96 * se) * 100, 2))
```
<!--sortie-->
```text
4.5 0.464 3.59 5.41
```

### Corrigé 10.2

Taux de passage : $1\,200/10\,000=12\ \%$ ; $600/1\,200=50\ \%$ ; $400/600\approx66{,}7\ \%$ ; conversion globale $400/10\,000=4\ \%$. La perte la plus **massive** est la première (88 % des sessions n'ajoutent rien) ; la plus **actionnable** est souvent la dernière : un tiers de ceux qui commencent à payer s'arrêtent.

### Corrigé 10.3

Avec 1 000 sessions : $p_A=4\ \%$, $p_B=5\ \%$, proportion commune $4{,}5\ \%$, erreur type $\sqrt{0{,}045\times0{,}955\times(2/1\,000)}\approx0{,}0093$, $z\approx1{,}08$, $p\approx0{,}28$ : **non significatif**. Avec dix fois plus de sessions, l'erreur type est divisée par $\sqrt{10}$, $z\approx3{,}4$ et $p<0{,}001$ : **très significatif**.

```python
from statsmodels.stats.proportion import proportions_ztest
for k, n in [([40, 50], [1000, 1000]), ([400, 500], [10000, 10000])]:
    z, p = proportions_ztest(k, n)
    print(f"z = {z:.2f}, p = {p:.4f}")
```
<!--sortie-->
```text
z = -1.08, p = 0.2807
z = -3.41, p = 0.0006
```

Le même écart d'un point est du bruit sur 1 000 sessions et une vraie différence sur 10 000 : **la taille de l'échantillon décide**.

### Corrigé 10.4

Commandes ajoutées : $10\,000\times2\ \%=200$. Nouvelle conversion : $(5\,000+200)/110\,000\approx4{,}73\ \%$, contre 5,00 % avant. La conversion globale **baisse** de 0,27 point alors que les commandes **augmentent** de 200 : la campagne n'est pas « mauvaise », elle est moins bonne que la moyenne ; sa rentabilité se juge sur son coût et sa marge (section 10.2).

```python
print(round(5200 / 110000 * 100, 2), 10000 * 0.02)
```
<!--sortie-->
```text
4.73 200.0
```

### Corrigé 10.5

ROAS $=5\,000/2\,000=2{,}5$. Marge $=0{,}38\times5\,000=1\,900$ €. ROI $=(1\,900-2\,000)/2\,000=-5\ \%$ : le canal **perd** 100 €. Un ROAS de 2,5 paraît bon mais ne couvre pas la dépense : le seuil de rentabilité est $1/0{,}38\approx2{,}63$.

### Corrigé 10.6

Seuil $=1/\text{taux de marge}$ : $1/0{,}30\approx3{,}33$ ; $1/0{,}38\approx2{,}63$ ; $1/0{,}45\approx2{,}22$. Un ROAS de 2,5 est rentable pour un produit à 45 % de marge (au-dessus de 2,22), insuffisant pour un produit à 38 % (seuil 2,63) et ruineux pour un produit à 30 % (seuil 3,33).

```python
print([round(1 / x, 2) for x in (0.30, 0.38, 0.45)])
```
<!--sortie-->
```text
[3.33, 2.63, 2.22]
```

### Corrigé 10.7

CAC $=4\,000/25=160$ €. Valeur du client : 20 € à la première commande, 70 € au total sur deux ans. Ratio valeur/CAC : $70/160\approx0{,}44$, donc l'acquisition **ne se rentabilise pas**, même avec les commandes suivantes ; sur la seule première commande, le rapport est $20/160=0{,}125$. Il faudrait un client qui rapporte plus de 160 € de marge sur sa vie, ou un coût d'acquisition plus bas.

### Corrigé 10.8

Dernier clic : direct 2 (parcours 1 et 3), email 1 ; réseaux, organique, payant 0. Premier clic : réseaux 1, payant 1, direct 1 ; organique, email 0. Linéaire : parcours 1 donne un tiers à chacun de réseaux, organique, direct ; parcours 2 donne ½ à payant et ½ à email ; parcours 3 donne 1 au direct ; total direct $1{,}33$, réseaux $0{,}33$, organique $0{,}33$, payant $0{,}5$, email $0{,}5$. Le **direct** gagne le plus au dernier clic (2 sur 3) et le moins au premier clic (1 sur 3) ; les **réseaux** et le **payant** passent de 0 à 1 selon qu'on regarde la fin ou le début.

```python
parcours = [["reseaux", "organique", "direct"], ["payant", "email"], ["direct"]]
for mo in ["dernier clic", "premier clic", "linéaire"]:
    print(mo, {k: round(v * 3, 2) for k, v in O.attribution(parcours, mo).items() if v > 0})
```
<!--sortie-->
```text
dernier clic {'direct': 2.0, 'email': 1.0}
premier clic {'direct': 1.0, 'payant': 1.0, 'reseaux': 1.0}
linéaire {'direct': 1.33, 'organique': 0.33, 'payant': 0.5, 'email': 0.5, 'reseaux': 0.33}
```

### Corrigé 10.9

Couverture $=4\,821/6\,078\approx79{,}3\ \%$. Estimation du chiffre d'affaires réel : $90\,000/0{,}793\approx113\,500$ €, **en supposant** que les commandes non vues ont le même montant moyen que les commandes vues et que la couverture est la même pour toutes les sources (hypothèse fausse dans notre vue fabriquée, où elle varie de 55 % à 95 % selon la source). Le chiffre est donc une **estimation grossière**, pas un redressement exact.

```python
print(round(4821 / 6078 * 100, 1), round(90000 / (4821 / 6078)))
```
<!--sortie-->
```text
79.3 113466
```

### Corrigé 10.10

Le surplus d'événements est $6\,262-6\,078=184$ achats, soit 3,0 %. Si chaque événement vaut 100 €, le chiffre d'affaires de l'outil est gonflé de **18 400 €** (3,0 %). On corrige en **dédoublonnant** sur l'identifiant de commande, présent dans l'événement. Si les doublons portent sur des commandes d'un montant différent de la moyenne (par exemple des commandes plus grosses, parce que les gros paniers rechargent plus souvent la page de confirmation), le gonflement du chiffre d'affaires n'est **pas** de 3 % : il peut être plus ou moins élevé que le surplus en nombre. Raison de plus de dédoublonner par identifiant plutôt que de corriger par un coefficient.

```python
ev = O.evenements_doublons(s)
print(len(ev) - ev["id_commande"].nunique(), (len(ev) - ev["id_commande"].nunique()) * 100, round((len(ev) / ev["id_commande"].nunique() - 1) * 100, 1))
```
<!--sortie-->
```text
184 18400 3.0
```
