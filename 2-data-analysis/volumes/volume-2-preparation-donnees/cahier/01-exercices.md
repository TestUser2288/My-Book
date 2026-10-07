# Chapitre 1 : Nettoyage des données — exercices et applications

> 🧭 Ce chapitre du cahier prolonge le chapitre 1 du livre. Les **applications** sont de petites études guidées sur les fichiers désordonnés de la boutique, à refaire pas à pas ; les **exercices** (⭐ facile, ⭐⭐ moyen, ⭐⭐⭐ plus long) vous demandent de produire vous-même un résultat, avec un corrigé détaillé en fin de chapitre. Les fichiers `verite_*` ne servent qu'à **juger** un nettoyage : ouvrez-les à la fin, comme un corrigé. Tout le code se rejoue d'un trait, dans l'ordre.

```python
import os, io, re, sys, glob, tempfile
import numpy as np, pandas as pd
sys.path.insert(0, "build")
import outils_ch01 as C
D = os.environ["DONNEES"]
profil = pd.read_csv(os.path.join(D, "profil_clients.csv"))
verite = pd.read_csv(os.path.join(D, "profil_clients_verite.csv"))
```

## Applications

### Application 1.1 — Profiler un fichier avant tout calcul (sections 1.1.1 et 1.1.2)

**Objectif.** Le premier geste d'une analyste est un **profil** du fichier : combien de lignes, quels types, combien de manquants, quelles valeurs spéciales. On le fait **avant** de calculer quoi que ce soit.

**Étape 1 — Un profil par colonne.** Une petite fonction qui résume chaque colonne : type, manquants, valeurs distinctes, minimum et maximum.

```python
def profiler(t):
    p = pd.DataFrame({"type": t.dtypes.astype(str), "manquants": t.isna().sum(), "part_%": (t.isna().mean() * 100).round(1), "distinctes": t.nunique()})
    p["min"] = [t[c].min() if pd.api.types.is_numeric_dtype(t[c]) else "" for c in t.columns]
    p["max"] = [t[c].max() if pd.api.types.is_numeric_dtype(t[c]) else "" for c in t.columns]
    return p
print(profiler(profil).to_string())
```
<!--sortie-->
```text
                      type  manquants  part_%  distinctes     min       max
id_client            int64          0     0.0        6000       1      6000
age                  int64          0     0.0          68      18        85
canal_acquisition      str          0     0.0           3                  
revenu_annuel      float64       1039    17.3         555  6900.0  104400.0
nb_commandes_2025    int64          0     0.0          24       0        25
depense_2025       float64        297     5.0        2838     0.0   3382.33
satisfaction_moy   float64        562     9.4         312     1.0       5.0
minutes_site       float64          0     0.0         533     0.2      86.4
```

**Lecture.** Trois colonnes ont des manquants (revenu, dépense, satisfaction). Les colonnes sans trou ont tout de même des **valeurs à regarder** : le minimum de `age`, le maximum de `minutes_site`, les zéros éventuels.

**Étape 2 — Les valeurs spéciales d'une colonne de montants.** Le fichier `montants_saisis.csv` contient des montants saisis à la main. On cherche les valeurs qui **ressemblent** à des codes plutôt qu'à des montants : zéros, négatifs, 9999.

```python
saisis = pd.read_csv(os.path.join(D, "montants_saisis.csv"))
print("montants nuls :", int((saisis["montant"] == 0).sum()), "| négatifs :", int((saisis["montant"] < 0).sum()), "| égaux à 9999 :", int((saisis["montant"] == 9999).sum()))
print("montants au-dessus de 1 000 € :", int((saisis["montant"] > 1000).sum()))
```
<!--sortie-->
```text
montants nuls : 10 | négatifs : 22 | égaux à 9999 : 9
montants au-dessus de 1 000 € : 28
```

**Lecture.** Les zéros, les négatifs et les « 9999 » ne sont pas des montants plausibles pour une boutique dont la ligne moyenne vaut une quarantaine d'euros : ce sont des **suspects** à examiner (section 1.2), non des manquants. On les **liste**, on ne les remplace pas encore.

**Étape 3 — Ce qui se déduit.** Les clients sans commande ont forcément dépensé 0 €.

```python
sans_commande = profil["nb_commandes_2025"] == 0
deduite = profil["depense_2025"].where(~sans_commande, 0.0)
print("dépenses manquantes avant :", int(profil["depense_2025"].isna().sum()), "| après déduction :", int(deduite.isna().sum()))
```
<!--sortie-->
```text
dépenses manquantes avant : 297 | après déduction : 196
```

**À vous.** Appliquez `profiler` au fichier `crm_clients.csv` lu **sans** `dtype=str`, puis avec `dtype=str`, et comparez les types obtenus (exercice 1.1).

### Application 1.2 — Tester le mécanisme d'absence (section 1.1.3)

**Objectif.** Pour chaque colonne avec des trous, déterminer si l'absence dépend de **ce que l'on connaît** (MAR) ou semble aléatoire.

**Étape 1 — Un test du khi-deux par colonne et par variable.**

```python
from scipy.stats import chi2_contingency
profil["classe_age"] = pd.cut(profil["age"], [0, 29, 44, 59, 200], labels=["moins de 30", "30-44", "45-59", "60 et plus"])
profil["classe_commandes"] = pd.cut(profil["nb_commandes_2025"], [-1, 0, 3, 10, 1000], labels=["0", "1 à 3", "4 à 10", "plus de 10"])
for col in ["depense_2025", "revenu_annuel", "satisfaction_moy"]:
    ps = {v: chi2_contingency(pd.crosstab(profil[v], profil[col].isna()))[1] for v in ["classe_age", "canal_acquisition", "classe_commandes"]}
    print(f"{col:17s}", {k: float(f"{p:.2g}") for k, p in ps.items()})
```
<!--sortie-->
```text
depense_2025      {'classe_age': 0.72, 'canal_acquisition': 0.53, 'classe_commandes': 0.54}
revenu_annuel     {'classe_age': 7.2e-49, 'canal_acquisition': 1.4e-09, 'classe_commandes': 0.13}
satisfaction_moy  {'classe_age': 0.76, 'canal_acquisition': 0.36, 'classe_commandes': 0.28}
```

**Lecture.** Le revenu dépend de l'âge et du canal (probabilités critiques minuscules). La **dépense** ne dépend ni de l'âge, ni du canal, ni du nombre de commandes (0,72 ; 0,53 ; 0,54) : l'absence est compatible avec le hasard, y compris chez les clients sans commande (101 sur 2 125, soit 4,8 %, contre 5,1 % ailleurs), et c'est pourquoi 101 des 297 trous sont **déductibles** sans rien changer au mécanisme. La **satisfaction** ne dépend de rien de visible.

**Étape 2 — Prédire l'absence.** Une autre façon de tester MAR : essayer de **prédire** l'absence à partir des colonnes connues. Une aire sous la courbe ROC (la probabilité qu'un client dont la valeur manque reçoive un score plus élevé qu'un client dont elle est connue) proche de 0,5 signifie « on ne fait pas mieux que le hasard ».

```python
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score
X = pd.get_dummies(profil[["age", "canal_acquisition", "nb_commandes_2025", "minutes_site"]], drop_first=True).astype(float)
for col in ["revenu_annuel", "depense_2025", "satisfaction_moy"]:
    y = profil[col].isna().astype(int)
    p = LogisticRegression(max_iter=2000).fit((X - X.mean()) / X.std(), y).predict_proba((X - X.mean()) / X.std())[:, 1]
    print(f"{col:17s} aire sous la courbe ROC pour prédire l'absence : {roc_auc_score(y, p):.3f}")
```
<!--sortie-->
```text
revenu_annuel     aire sous la courbe ROC pour prédire l'absence : 0.618
depense_2025      aire sous la courbe ROC pour prédire l'absence : 0.524
satisfaction_moy  aire sous la courbe ROC pour prédire l'absence : 0.521
```

**Lecture.** Une valeur de 0,62 pour le revenu, nettement supérieure à 0,5, confirme que l'absence est **prévisible** par l'âge et le canal (MAR). Les valeurs proches de 0,5 pour la dépense (0,52) et pour la satisfaction (0,52) ne prouvent **pas** que le mécanisme est aléatoire : pour la satisfaction, il dépend de la valeur manquante elle-même (MNAR), invisible ici.

**Étape 3 — La vérité (réservée au cahier).**

```python
vraie = pd.cut(verite["satisfaction_moy"], [0, 2.5, 3.5, 4.5, 5.01], labels=["≤ 2,5", "2,5-3,5", "3,5-4,5", "> 4,5"])
print((profil["satisfaction_moy"].isna().groupby(vraie, observed=True).mean() * 100).round(1).to_string())
```
<!--sortie-->
```text
satisfaction_moy
≤ 2,5      37.6
2,5-3,5     7.5
3,5-4,5     8.9
> 4,5       7.1
```

**À vous.** Refaites le test pour `depense_2025` en ne gardant que les clients **ayant commandé** : l'absence y est-elle aléatoire ? (exercice 1.3)

### Application 1.3 — Détecter les aberrantes : un compromis précision/rappel (sections 1.2.2 et 1.2.3)

**Objectif.** Voir comment le seuil d'une méthode statistique déplace l'équilibre entre « trop de fausses alertes » et « anomalies ratées », et comparer à la règle métier.

**Étape 1 — Préparer.**

```python
saisis = saisis.merge(pd.read_csv(os.path.join(D, "verite_montants.csv")), on="id_ligne")
saisis["vraie_anomalie"] = saisis["anomalie"].notna()
m = saisis["montant"]
mad = (m - m.median()).abs().median()
score = (0.6745 * (m - m.median()) / mad).abs()
print("anomalies injectées :", int(saisis["vraie_anomalie"].sum()), "sur", len(saisis), "| MAD :", round(mad, 2))
```
<!--sortie-->
```text
anomalies injectées : 85 sur 6000 | MAD : 17.47
```

**Étape 2 — Balayer le seuil du score z robuste.**

```python
for seuil in (2, 3.5, 5, 10, 20, 50):
    signal = score > seuil
    vrais = int((signal & saisis["vraie_anomalie"]).sum())
    print(f"seuil {seuil:>4} : signalées {int(signal.sum()):4d} | précision {vrais / signal.sum() * 100:5.1f} % | rappel {vrais / saisis['vraie_anomalie'].sum() * 100:5.1f} %")
```
<!--sortie-->
```text
seuil    2 : signalées  695 | précision   9.6 % | rappel  78.8 %
seuil  3.5 : signalées  324 | précision  17.0 % | rappel  64.7 %
seuil    5 : signalées  150 | précision  34.0 % | rappel  60.0 %
seuil   10 : signalées   68 | précision  67.6 % | rappel  54.1 %
seuil   20 : signalées   33 | précision 100.0 % | rappel  38.8 %
seuil   50 : signalées   26 | précision 100.0 % | rappel  30.6 %
```

**Lecture.** Plus le seuil monte, plus la **précision** augmente (on ne signale que des cas flagrants) et plus le **rappel** chute (on rate les anomalies discrètes). Aucun seuil ne donne à la fois une précision et un rappel proches de 100 %, parce que la distribution des montants légitimes a elle-même une longue queue.

**Étape 3 — La règle métier.**

```python
rapport = saisis["montant"] / (saisis["quantite"] * saisis["prix_unitaire"])
suspect = ~rapport.between(0.795, 1.005)
vrais = int((suspect & saisis["vraie_anomalie"]).sum())
print("règle métier : signalées", int(suspect.sum()), "| précision", round(vrais / suspect.sum() * 100, 1), "% | rappel", round(vrais / saisis["vraie_anomalie"].sum() * 100, 1), "%")
```
<!--sortie-->
```text
règle métier : signalées 85 | précision 100.0 % | rappel 100.0 %
```

**Étape 4 — L'effet sur le total.**

```python
corrige = np.where(suspect, saisis["quantite"] * saisis["prix_unitaire"], saisis["montant"])
vrai_total = saisis["montant_vrai"].sum()
print("total saisi :", round(saisis["montant"].sum()), "| corrigé par la règle :", round(corrige.sum()), "| vrai :", round(vrai_total), "| écart du total corrigé :", round((corrige.sum() / vrai_total - 1) * 100, 2), "%")
```
<!--sortie-->
```text
total saisi : 447950 | corrigé par la règle : 255711 | vrai : 255631 | écart du total corrigé : 0.03 %
```

**À vous.** Ajoutez une deuxième règle (montant strictement positif et quantité entre 1 et 10) et vérifiez ce qu'elle signale en plus ou en moins de la première.

### Application 1.4 — Dédoublonner les commandes du site avec un journal (section 1.3.2)

**Objectif.** Construire une fonction qui **nettoie** l'export du site **et** garde la trace de ce qu'elle retire.

**Étape 1 — Les trois raisons de retirer une ligne.**

```python
site = pd.read_csv(os.path.join(D, "site_commandes.csv"), dtype=str)
def nettoyer_site(t):
    journal = []
    sans_doublon = t.drop_duplicates("order_ref")
    journal.append(("doublon d'export", t[t.duplicated("order_ref")]))
    test = sans_doublon["customer_email"].str.strip().str.lower().eq("test@example.com")
    journal.append(("commande de test", sans_doublon[test]))
    reste = sans_doublon[~test]
    annulee = reste["status"].str.lower().eq("cancelled")
    journal.append(("commande annulée", reste[annulee]))
    return reste[~annulee], journal
propre, journal = nettoyer_site(site)
print("lignes avant :", len(site), "| après :", len(propre))
```
<!--sortie-->
```text
lignes avant : 6259 | après : 5897
```

**Étape 2 — Le journal.**

```python
for raison, lignes in journal:
    print(f"{raison:18s} {len(lignes):4d} lignes")
print("somme :", sum(len(l) for _, l in journal), "= lignes retirées :", len(site) - len(propre))
```
<!--sortie-->
```text
doublon d'export    121 lignes
commande de test     60 lignes
commande annulée    181 lignes
somme : 362 = lignes retirées : 362
```

**Lecture.** La somme des lignes du journal est **égale** au nombre de lignes retirées : rien n'a disparu sans explication. C'est la propriété à exiger de tout nettoyage.

**Étape 3 — Contrôles de bon sens.** Deux lignes de même `order_ref` ont-elles toujours le même contenu ? Y a-t-il des commandes sans e-mail ?

```python
doublons = site[site["order_ref"].duplicated(keep=False)]
print("références en double dont le contenu diffère :", int((doublons.groupby("order_ref").apply(lambda g: len(g.drop_duplicates()) > 1)).sum()))
print("commandes sans e-mail :", int(site["customer_email"].isna().sum()), "| statuts :", sorted(site["status"].str.lower().unique()))
```
<!--sortie-->
```text
références en double dont le contenu diffère : 0
commandes sans e-mail : 0 | statuts : ['cancelled', 'paid']
```

**À vous.** Ajoutez à la fonction une quatrième raison : une commande dont le total vaut 0 ou est négatif.

### Application 1.5 — Détecter et corriger le changement d'unité (section 1.4.2)

**Objectif.** Trouver la date d'un changement d'unité **sans regarder le fichier à la main**, le corriger et le vérifier.

**Étape 1 — Convertir les montants et dater les commandes.**

```python
def nombre(texte):
    return float(texte.replace("€", "").replace(" ", "").replace(",", ".").strip())
site["total_n"] = site["total"].map(nombre)
site["dt"] = pd.to_datetime(site["created_at"].str.replace("Z", "", regex=False), format="mixed")
quotidien = site.set_index("dt")["total_n"].resample("D").median()
print(quotidien.describe().round(0).to_string())
```
<!--sortie-->
```text
count      365.0
mean      2453.0
std       3793.0
min         25.0
25%         75.0
50%         98.0
75%       6314.0
max      12742.0
```

**Étape 2 — Chercher la rupture : le rapport à la médiane des quatorze jours précédents.**

```python
precedent = quotidien.rolling(14, min_periods=7).median().shift(1)
rapport = quotidien / precedent
jour_rupture = rapport[rapport > 20].index[0]
print("premier jour où le montant médian dépasse 20 fois celui des 14 jours précédents :", jour_rupture.date())
print("rapport ce jour-là :", round(rapport[jour_rupture], 1), "| rapports de plus de 20 :", int((rapport > 20).sum()))
```
<!--sortie-->
```text
premier jour où le montant médian dépasse 20 fois celui des 14 jours précédents : 2025-09-15
rapport ce jour-là : 149.7 | rapports de plus de 20 : 7
```

**Lecture.** La rupture est détectée **par un calcul**, et non à l'œil : le 15 septembre, le montant médian est près de 150 fois celui des quatorze jours précédents (un facteur de l'ordre de 100, bruité par la variabilité d'une médiane quotidienne), ce qui désigne le passage de l'euro au centime. Sept jours dépassent le seuil de 20 : les premiers jours après la rupture, tant que la médiane glissante est encore dominée par les anciens montants en euros.

**Étape 3 — Corriger et vérifier.**

```python
site["total_corrige"] = np.where(site["dt"] >= jour_rupture, site["total_n"] / 100, site["total_n"])
verite_site = pd.read_csv(os.path.join(D, "verite_site.csv")).drop_duplicates("order_ref")
x = site.merge(verite_site[verite_site["defaut"] != "test"], on="order_ref")
print("écart maximal avec la vérité :", round((x["total_corrige"] - x["total_vrai"]).abs().max(), 4), "€ sur", len(x), "commandes")
```
<!--sortie-->
```text
écart maximal avec la vérité : 0.0 € sur 6199 commandes
```

**Étape 4 — Le chiffre d'affaires mensuel du site, avant et après.**

```python
site["mois"] = site["dt"].dt.strftime("%Y-%m")
propre = site.drop_duplicates("order_ref")
propre = propre[~propre["customer_email"].str.strip().str.lower().eq("test@example.com") & (propre["status"].str.lower() != "cancelled")]
print(propre.groupby("mois")[["total_n", "total_corrige"]].sum().round(0).astype(int).to_string())
```
<!--sortie-->
```text
         total_n  total_corrige
mois                           
2025-01    40221          40221
2025-02    32746          32746
2025-03    40821          40821
2025-04    41828          41828
2025-05    47471          47471
2025-06    48555          48555
2025-07    52340          52340
2025-08    36278          36278
2025-09  3012754          54524
2025-10  5499972          55000
2025-11  6288428          62884
2025-12  8749607          87496
```

**À vous.** Que se passe-t-il si l'on corrige « à l'œil », en divisant par cent toutes les valeurs supérieures à 1 000 € ? (exercice 1.8)

### Application 1.6 — Lire les douze fichiers de caisse et les réconcilier (sections 1.3.3 et 1.4.6)

**Objectif.** Lire les douze exports mensuels avec la fonction `lire_caisse`, puis **expliquer** mois par mois l'écart avec le total affiché.

**Étape 1 — Lire et vérifier.**

```python
fichiers = sorted(glob.glob(os.path.join(D, "caisse", "*.csv")))
cais = pd.concat([C.lire_caisse(f)[0].assign(mois=os.path.basename(f)[7:14]) for f in fichiers], ignore_index=True)
totaux = {os.path.basename(f)[7:14]: C.lire_caisse(f)[1] for f in fichiers}
print("lignes lues :", len(cais), "| montants vides :", int(cais["montant"].isna().sum()), "| colonnes :", list(cais.columns))
```
<!--sortie-->
```text
lignes lues : 12678 | montants vides : 399 | colonnes : ['ticket', 'date', 'heure', 'article', 'categorie', 'quantite', 'prix_unitaire', 'montant', 'id_commande', 'mois', 'remise_pct']
```

**Étape 2 — Rapprocher chaque ligne d'une ligne de la base (avec un rang).**

```python
produits = pd.read_csv(os.path.join(D, "produits.csv"))[["id_produit", "nom_produit"]]
base = pd.read_csv(os.path.join(D, "lignes_commande.csv")).merge(pd.read_csv(os.path.join(D, "commandes.csv"))[["id_commande", "canal", "date_commande"]], on="id_commande").merge(produits, on="id_produit")
base = base[(base["canal"] == "Boutique") & (base["date_commande"] >= "2025-01-01")].copy()
base["article"], cais["article"] = base["nom_produit"].str.lower(), cais["article"].str.lower()
cle = ["id_commande", "article", "quantite", "prix_unitaire"]
for t in (cais, base):
    t["rang"] = t.groupby(cle).cumcount()
r = cais.merge(base[cle + ["rang", "montant"]].rename(columns={"montant": "montant_base"}), on=cle + ["rang"], how="left", indicator=True)
print(r["_merge"].value_counts().to_string())
```
<!--sortie-->
```text
_merge
both          12611
left_only        67
right_only        0
```

**Étape 3 — L'écart de chaque mois, expliqué.**

```python
r["double"] = r["_merge"] == "left_only"
r["vide_retrouve"] = np.where(r["montant"].isna() & ~r["double"], r["montant_base"], 0.0)
g = r.groupby("mois").apply(lambda t: pd.Series({"somme_lue": t["montant"].sum(), "doubles": t.loc[t["double"], "montant"].sum(), "vides_retrouvés": t["vide_retrouve"].sum()}))
g["reconstitué"] = g["somme_lue"] - g["doubles"] + g["vides_retrouvés"]
g["total_affiché"] = pd.Series(totaux)
g["écart_restant"] = (g["total_affiché"] - g["reconstitué"]).round(2)
print(g.round(2).to_string())
```
<!--sortie-->
```text
         somme_lue  doubles  vides_retrouvés  reconstitué  total_affiché  écart_restant
mois                                                                                   
2025-01   37826.31   245.22          1301.32     38882.41       38882.41            0.0
2025-02   32273.46     0.00           805.95     33079.41       33079.41            0.0
2025-03   37863.67   135.26          1310.49     39038.90       39038.90            0.0
2025-04   45426.14   671.69          1078.12     45832.57       45832.57            0.0
2025-05   43381.31   291.72          1816.33     44905.92       44905.92            0.0
2025-06   42277.42   236.32          1077.06     43118.16       43118.16            0.0
2025-07   41035.68   144.25           704.39     41595.82       41595.82            0.0
2025-08   42350.83   451.37           974.04     42873.50       42873.50            0.0
2025-09   45600.67   321.44          1075.02     46354.25       46354.25            0.0
2025-10   49839.95    82.00          1563.53     51321.48       51321.48            0.0
2025-11   59096.64   243.54          1733.52     60586.62       60586.62            0.0
2025-12   70924.34   303.48          2764.01     73384.87       73384.87            0.0
```

**Lecture.** L'écart restant est **nul pour chacun des douze mois** : non seulement le total global, mais chaque fichier se reconstitue au centime. Une réconciliation fine, mois par mois, localise une erreur si elle survient (un mois dont l'écart restant ne serait pas nul).

**À vous.** Quel mois compte le plus de lignes en double ? Le plus de montants vides ?

### Application 1.7 — Nettoyer le fichier clients du CRM (sections 1.4.4, 1.4.5 et 1.5)

**Objectif.** Assembler les corrections de la section 1.4 et de la section 1.5 en un **seul traitement**, qui produit un tableau propre et une **table de contrôle**.

**Étape 1 — Lire en texte, retirer les lignes de test.**

```python
crm = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
test = crm["email"].str.strip().str.lower().eq("test@example.com")
crm = crm[~test].copy()
print("lignes :", len(test), "| lignes de test retirées :", int(test.sum()), "| restantes :", len(crm))
```
<!--sortie-->
```text
lignes : 7140 | lignes de test retirées : 140 | restantes : 7000
```

**Étape 2 — Normaliser les colonnes.**

```python
def ville_propre(s):
    s = s.strip()
    return "Ville " + chr(65 + C.AR.index(s.split()[-1])) if s.startswith("المدينة") else C.normaliser_ville(s)
crm["ville_propre"] = crm["ville"].map(ville_propre)
crm["cp"] = crm["code_postal"].str.zfill(5)
crm["email_propre"] = crm["email"].str.strip().str.lower()
crm["tel"] = crm["telephone"].map(lambda s: (lambda ch: ch if re.fullmatch(r"0\d{9}", ch) else None)(("0" + re.sub(r"\D", "", s)[2:]) if s.startswith("+") else re.sub(r"\D", "", s)))
crm["naissance"] = crm["date_naissance"].map(lambda s: C.date_mixte(s, americain=bool(re.fullmatch(r"\d\d/\d\d/\d{4}", s)) and int(s[3:5]) > 12))
crm["consentement"] = crm["consentement_marketing"].str.strip().str.lower().map({"oui": True, "o": True, "1": True, "true": True, "non": False})
print(crm[["ville_propre", "cp", "tel", "naissance", "consentement"]].isna().sum().to_string())
```
<!--sortie-->
```text
ville_propre       0
cp               424
tel                0
naissance         44
consentement    2161
```

**Étape 3 — La table de contrôle.**

```python
regles = {"ville reconnue": crm["ville_propre"].str.fullmatch(r"Ville [A-T]"),
          "code postal de 5 chiffres (si renseigné)": crm["cp"].isna() | crm["cp"].str.fullmatch(r"\d{5}"),
          "e-mail valide (si renseigné)": crm["email_propre"].isna() | crm["email_propre"].str.fullmatch(r"(?!.*\.\.)[\w.+-]+@[\w-]+\.[\w.]+"),
          "naissance lisible": crm["naissance"].notna(),
          "naissance entre 1920 et 2010": crm["naissance"].isna() | crm["naissance"].between("1920-01-01", "2010-12-31")}
controle = pd.DataFrame({"infractions": {k: int((~v).sum()) for k, v in regles.items()}})
controle["part_%"] = (controle["infractions"] / len(crm) * 100).round(2)
print(controle.to_string())
```
<!--sortie-->
```text
                                          infractions  part_%
ville reconnue                                      0    0.00
code postal de 5 chiffres (si renseigné)            0    0.00
e-mail valide (si renseigné)                       95    1.36
naissance lisible                                  44    0.63
naissance entre 1920 et 2010                       24    0.34
```

**Étape 4 — Dédoublonner par e-mail, en gardant la ligne la plus complète.**

```python
avec_email = crm[crm["email_propre"].notna()].copy()
avec_email["manquants"] = avec_email[["tel", "cp", "naissance"]].isna().sum(axis=1)
fusion = avec_email.sort_values(["email_propre", "manquants"]).groupby("email_propre", as_index=False).first()
print("lignes avec e-mail :", len(avec_email), "| après fusion :", len(fusion), "| lignes sans e-mail (gardées telles quelles) :", int(crm["email_propre"].isna().sum()))
```
<!--sortie-->
```text
lignes avec e-mail : 6769 | après fusion : 6092 | lignes sans e-mail (gardées telles quelles) : 231
```

**À vous.** Quel est le nombre de clients après fusion, en comptant les lignes sans e-mail comme autant de clients distincts ? Comparez avec les 6 000 clients de la vérité : que vous apprend l'écart ?

### Application 1.8 — Comparer les imputations à la vérité, avec vos propres trous (section 1.6)

**Objectif.** Pour **choisir** une méthode d'imputation, on la teste sur des trous que l'on a **soi-même** faits dans des données complètes, en variant le mécanisme.

**Étape 1 — Fabriquer trois mécanismes d'absence sur le revenu (complet dans la vérité).**

```python
rng = np.random.default_rng(1)
rev = verite["revenu_annuel"]
p_mar = np.where(verite["age"] < 30, 0.35, 0.12)                       # dépend de l'âge, connu
p_mnar = 0.08 + 0.35 * (rev > rev.quantile(0.75))                      # dépend du revenu lui-même
masques = {"MCAR": rng.random(len(rev)) < 0.17, "MAR": rng.random(len(rev)) < p_mar, "MNAR": rng.random(len(rev)) < p_mnar}
print({k: round(float(v.mean()) * 100, 1) for k, v in masques.items()}, "% de manquants")
```
<!--sortie-->
```text
{'MCAR': 17.3, 'MAR': 15.7, 'MNAR': 17.6} % de manquants
```

**Étape 2 — Trois méthodes d'imputation.**

```python
from sklearn.linear_model import LinearRegression
X = pd.get_dummies(verite[["age", "canal_acquisition", "nb_commandes_2025", "minutes_site"]], drop_first=True).astype(float)
classe = pd.cut(verite["age"], [0, 29, 44, 59, 200])
def imputer(masque):
    obs = rev.where(~masque)
    return {"moyenne": pd.Series(obs.mean(), index=rev.index),
            "moyenne par âge": obs.groupby(classe, observed=True).transform("mean"),
            "régression": pd.Series(LinearRegression().fit(X[~masque], rev[~masque]).predict(X), index=rev.index)}
```

**Étape 3 — Biais de la moyenne et erreur, par mécanisme et par méthode.**

```python
lignes = []
for meca, masque in masques.items():
    for nom, imp in imputer(masque).items():
        complet = rev.where(~masque, imp)
        lignes.append((meca, nom, round(complet.mean() - rev.mean()), round(np.sqrt(((imp[masque] - rev[masque]) ** 2).mean()))))
print(pd.DataFrame(lignes, columns=["mécanisme", "méthode", "biais_moyenne_€", "erreur_typique_€"]).to_string(index=False))
```
<!--sortie-->
```text
mécanisme         méthode  biais_moyenne_€  erreur_typique_€
     MCAR         moyenne                4             11397
     MCAR moyenne par âge               28             10843
     MCAR      régression               48             10839
      MAR         moyenne              251             10869
      MAR moyenne par âge              -33              9934
      MAR      régression              -19              9851
     MNAR         moyenne            -1749             15767
     MNAR moyenne par âge            -1574             14586
     MNAR      régression            -1558             14460
```

**Lecture.** Sous **MCAR**, les trois méthodes retrouvent la moyenne. Sous **MAR**, la moyenne simple est biaisée alors que les méthodes qui utilisent l'âge corrigent le biais. Sous **MNAR** (les revenus élevés manquent plus souvent), **aucune** méthode ne retrouve la moyenne : toutes sous-estiment le revenu, parce que l'information sur ce qui manque a disparu avec les valeurs.

**À vous.** Répétez avec dix graines différentes et regardez la variabilité du biais : la conclusion dépend-elle du hasard d'une graine ?

## Exercices

### Exercice 1.1 ⭐ — Deux lectures d'un même fichier (section 1.1.1)

Lisez `crm_clients.csv` une première fois **sans** option, une seconde fois avec `dtype=str`. Pour la colonne `code_postal`, comparez le type obtenu et le nombre de valeurs manquantes. Que devient un code qui commence par 0 ?

### Exercice 1.2 ⭐⭐ — Déduire avant d'imputer (section 1.1.2)

Dans `profil_clients.csv`, vérifiez la règle « dépense nulle si et seulement si aucune commande » sur les clients dont la dépense est **connue**. Combien de clients la violent ? Que concluez-vous sur la déduction des 101 dépenses manquantes ?

### Exercice 1.3 ⭐⭐ — Le mécanisme de la dépense (section 1.1.3)

Parmi les clients **ayant passé au moins une commande**, la dépense manque-t-elle au hasard ? Testez sa dépendance à la classe d'âge et au canal d'acquisition avec un khi-deux, et calculez la part de manquants.

### Exercice 1.4 ⭐ — Les seuils à la main (section 1.2.2)

Pour les neuf montants 20, 25, 30, 35, 40, 45, 50, 60 et 260 : calculez à la main les quartiles (méthode de la médiane des moitiés ou interpolation linéaire de pandas), l'écart interquartile et les seuils de la règle 1,5 × EIQ, puis le score z classique de 260 et son score z robuste. Que signale chaque méthode ?

### Exercice 1.5 ⭐⭐ — Plafonner à 95 %, 99 %, 99,9 % (section 1.2.4)

Sur la dépense annuelle **vraie** (`profil_clients_verite.csv`), plafonnez les valeurs aux centiles 95, 99 et 99,9. Pour chaque plafond, donnez la moyenne, l'écart-type et la part du chiffre d'affaires qui est « coupée ».

### Exercice 1.6 ⭐ — Doublons d'un petit tableau (section 1.3.1)

On donne le tableau de six lignes ci-dessous. Combien de doublons exacts ? Combien si l'on ne regarde que `ticket` et `article` ? Que fait `keep=False` ?

```python
petit = pd.DataFrame({"ticket": ["T1", "T1", "T2", "T2", "T3", "T3"], "article": ["Vase", "Vase", "Plaid", "Bol", "Bol", "Bol"],
                      "quantite": [1, 1, 2, 1, 1, 2], "montant": [20.0, 20.0, 60.0, 15.0, 15.0, 30.0]})
```

### Exercice 1.7 ⭐⭐ — Le plus récent ou le plus complet ? (section 1.3.4)

Sur le CRM (sans les lignes de test), regroupez les lignes par e-mail normalisé. Comparez deux règles de fusion : garder, pour chaque e-mail, la ligne à la `date_inscription` la plus **récente**, ou la ligne la plus **complète** (le moins de colonnes vides). Dans chaque cas, combien de codes postaux manquent après fusion ?

### Exercice 1.8 ⭐⭐ — Corriger « à l'œil » (section 1.4.2)

Dans l'export du site, corrigez le changement d'unité en divisant par 100 **toutes** les valeurs supérieures à 1 000 € (et rien d'autre). Comparez le résultat à la vérité : combien de commandes sont mal corrigées, dans quel sens ? Pourquoi une correction **datée** est-elle meilleure ?

### Exercice 1.9 ⭐⭐⭐ — Un treizième fichier (section 1.4.6)

Le logiciel de caisse envoie, en janvier 2026, un fichier au format encore différent : séparateur tabulation, dates `AAAA-MM-JJ`, colonnes dans un autre ordre. Voici son contenu (écrit dans un fichier temporaire par le code ci-dessous). `C.lire_caisse` ne sait pas le lire. Écrivez une version **plus générale** de la fonction, qui détecte le séparateur parmi `;`, `,` et tabulation, et le format de date, puis vérifiez le total affiché.

```python
contenu = "Export caisse - Boutique\t\t\t\t\t\t\nPériode : janvier 2026\t\t\t\t\t\t\n\t\t\t\t\t\t\nTicket\tDate\tHeure\tArticle\tCatégorie\tQté\tPrix unitaire\tMontant\nT90001\t2026-01-02\t10:05\tPlaid nordique\tMaison\t1\t22.56\t22.56\nT90001\t2026-01-02\t10:05\tVase mat\tDécoration\t2\t14.90\t29.80\n\t\t\t\t\t\tTotal\t52.36\n"
dossier = tempfile.mkdtemp(dir=os.environ.get("TMPDIR"))
fichier13 = os.path.join(dossier, "caisse_2026-01.csv")
open(fichier13, "w", encoding="utf-8").write(contenu)
```

### Exercice 1.10 ⭐⭐ — Normaliser des téléphones (section 1.5.3)

Appliquez une normalisation en dix chiffres commençant par 0 aux numéros ci-dessous (formats mélangés, dont un invalide). Quels sont ceux que l'on **rejette** et pourquoi ?

```python
numeros = ["01 23 45 67 89", "01.23.45.67.89", "0123456789", "(0)1 23456789", "+99 1 23 45 67 89", "12 34 56", "01 23 45 67 8A"]
```

### Exercice 1.11 ⭐⭐ — Médiane de groupe contre moyenne de groupe (section 1.6.2)

Sur le revenu manquant de `profil_clients.csv`, imputez par la **médiane** de chaque groupe (classe d'âge × canal) puis par la **moyenne** de chaque groupe. Comparez l'erreur individuelle, le biais de la moyenne et l'écart-type final à la vérité. Laquelle choisir, et pourquoi la différence est-elle faible ?

### Exercice 1.12 ⭐⭐⭐ — Un MNAR que vous fabriquez, et un δ à choisir (section 1.6.6)

À partir de la satisfaction **vraie**, supprimez avec la probabilité 0,5 les valeurs inférieures à 3 (et 0,05 les autres). Calculez la moyenne observée et le biais. Cherchez, par un balayage, le décalage δ qui, soustrait aux valeurs imputées par la moyenne, retrouve la vraie moyenne. Dans la vraie vie, comment choisiriez-vous δ sans connaître la vérité ?

## Corrigés

### Corrigé 1.1

```python
brut = pd.read_csv(os.path.join(D, "crm_clients.csv"))
texte = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
zero = texte["code_postal"].str.startswith("0", na=False)
print("sans option :", brut["code_postal"].dtype, "| manquants", int(brut["code_postal"].isna().sum()), "| avec dtype=str :", texte["code_postal"].dtype, "| manquants", int(texte["code_postal"].isna().sum()))
print("codes commençant par 0 lus sans option :", brut.loc[zero, "code_postal"].head(3).tolist(), "| en texte :", texte.loc[zero, "code_postal"].head(3).tolist())
```
<!--sortie-->
```text
sans option : float64 | manquants 424 | avec dtype=str : str | manquants 424
codes commençant par 0 lus sans option : [5723.0, 9321.0, 5723.0] | en texte : ['05723', '09321', '05723']
```

Sans option, pandas lit la colonne en **nombres décimaux** (`float64`, à cause des manquants) : le code `05723` devient `5723.0`, et le zéro initial est **perdu définitivement** (il faudrait le réinventer avec `zfill(5)`, en supposant que tous les codes ont cinq chiffres). Avec `dtype=str`, le code reste `05723`. Le nombre de manquants est le même, mais la colonne n'a plus le même sens. **Règle** : les identifiants se lisent en texte.

### Corrigé 1.2

```python
connus = profil.dropna(subset=["depense_2025"])
print("clients avec dépense connue :", len(connus))
print("dépense nulle ET commandes > 0 :", int(((connus["depense_2025"] == 0) & (connus["nb_commandes_2025"] > 0)).sum()))
print("dépense > 0 ET aucune commande :", int(((connus["depense_2025"] > 0) & (connus["nb_commandes_2025"] == 0)).sum()))
```
<!--sortie-->
```text
clients avec dépense connue : 5703
dépense nulle ET commandes > 0 : 0
dépense > 0 ET aucune commande : 0
```

La règle n'a **aucune exception** parmi les clients dont la dépense est connue (les deux comptes de violations sont nuls). On peut donc appliquer la déduction aux 101 dépenses manquantes des clients sans commande, avec la confiance que donne une règle vérifiée sur plus de 5 700 cas. C'est plus sûr que n'importe quelle imputation statistique.

### Corrigé 1.3

```python
avec = profil[profil["nb_commandes_2025"] > 0].copy()
avec["classe_age"] = pd.cut(avec["age"], [0, 29, 44, 59, 200])
print("clients avec commandes :", len(avec), "| dépense manquante :", int(avec["depense_2025"].isna().sum()), f"({avec['depense_2025'].isna().mean() * 100:.1f} %)")
for v in ["classe_age", "canal_acquisition"]:
    print(v, "p =", round(chi2_contingency(pd.crosstab(avec[v], avec["depense_2025"].isna()))[1], 3))
```
<!--sortie-->
```text
clients avec commandes : 3875 | dépense manquante : 196 (5.1 %)
classe_age p = 0.974
canal_acquisition p = 0.579
```

Parmi les 3 875 clients qui ont commandé, la dépense manque pour 5,1 % d'entre eux, sans dépendance visible à l'âge ni au canal (probabilités critiques de 0,97 et 0,58) : c'est compatible avec un mécanisme **MCAR**. C'est cohérent avec l'application 1.2 : ni l'âge, ni le canal, ni le nombre de commandes n'expliquent l'absence de la dépense.

### Corrigé 1.4

```python
v = pd.Series([20, 25, 30, 35, 40, 45, 50, 60, 260])
q1, q3 = v.quantile([0.25, 0.75])
print("Q1 =", q1, "| Q3 =", q3, "| EIQ =", q3 - q1, "| seuils :", q1 - 1.5 * (q3 - q1), "et", q3 + 1.5 * (q3 - q1))
mad = (v - v.median()).abs().median()
print("z classique de 260 :", round((260 - v.mean()) / v.std(), 2), "| z robuste de 260 :", round(0.6745 * (260 - v.median()) / mad, 2), "| MAD =", mad)
```
<!--sortie-->
```text
Q1 = 30.0 | Q3 = 50.0 | EIQ = 20.0 | seuils : 0.0 et 80.0
z classique de 260 : 2.63 | z robuste de 260 : 14.84 | MAD = 10.0
```

À la main : les valeurs triées occupent les rangs 0 à 8 ; avec l'interpolation linéaire, $Q_1$ est au rang 2 (30) et $Q_3$ au rang 6 (50), donc l'EIQ vaut 20 et les seuils sont $30-30=0$ et $50+30=80$ : **260 est signalée**. Le **score z classique** de 260 vaut environ 2,6 (la moyenne, 62,8, et l'écart-type, 75, sont tous deux tirés par 260 elle-même) : sous le seuil de 3, **260 n'est pas signalée**, c'est le masquage. Le **score z robuste** vaut 14,8 (la MAD vaut 10) : **260 est signalée**. Deux méthodes sur trois la repèrent ; sur un petit échantillon, le score z classique est le moins fiable.

### Corrigé 1.5

```python
dep = verite["depense_2025"]
print(f"vérité : moyenne {dep.mean():.1f}, écart-type {dep.std():.1f}")
for q in (0.95, 0.99, 0.999):
    plafond = dep.quantile(q)
    coupe = (dep - dep.clip(upper=plafond)).sum() / dep.sum()
    print(f"plafond au centile {q * 100:g} ({plafond:7.1f} €) : moyenne {dep.clip(upper=plafond).mean():6.1f} | écart-type {dep.clip(upper=plafond).std():6.1f} | part du CA coupée {coupe * 100:4.1f} %")
```
<!--sortie-->
```text
vérité : moyenne 220.8, écart-type 318.0
plafond au centile 95 (  842.9 €) : moyenne  202.0 | écart-type  252.1 | part du CA coupée  8.5 %
plafond au centile 99 ( 1452.0 €) : moyenne  217.3 | écart-type  300.0 | part du CA coupée  1.6 %
plafond au centile 99.9 ( 2230.8 €) : moyenne  220.3 | écart-type  314.4 | part du CA coupée  0.2 %
```

Plus le plafond est bas, plus la moyenne et surtout l'écart-type diminuent, et plus la part du chiffre d'affaires « coupée » augmente : plafonner au 95ᵉ centile (843 €) retire 8,5 % du chiffre d'affaires et ramène l'écart-type de 318 € à 252 €, plafonner au 99ᵉ (1 452 €) en retire 1,6 %, plafonner au 99,9ᵉ seulement 0,2 %. Le plafond est un **curseur** entre « une moyenne stable » et « la vérité des gros clients » : on le choisit en fonction de la question (une moyenne de pilotage tolère le plafond, un calcul de chiffre d'affaires non).

### Corrigé 1.6

```python
print("doublons exacts :", int(petit.duplicated().sum()), "| sur (ticket, article) :", int(petit.duplicated(["ticket", "article"]).sum()))
print(petit[petit.duplicated(["ticket", "article"], keep=False)].index.tolist(), "| keep=False marque toutes les copies, première comprise")
```
<!--sortie-->
```text
doublons exacts : 1 | sur (ticket, article) : 2
[0, 1, 4, 5] | keep=False marque toutes les copies, première comprise
```

Il y a **1 doublon exact** (la ligne T1, Vase, 1, 20 € répétée). Sur `(ticket, article)` seulement, il y en a **2** : T1/Vase, mais aussi T3/Bol (la quantité diffère : 1 et 2). Ce n'est **pas** un doublon, mais deux lignes d'un même ticket pour un même article (deux achats, ou une erreur de saisie) : la clé était trop **large**. `keep=False` marque **toutes** les copies, première comprise, ce qui sert à les afficher et à les examiner (alors que `keep="first"` ne marque que les suivantes).

### Corrigé 1.7

```python
c = pd.read_csv(os.path.join(D, "crm_clients.csv"), dtype=str)
c = c[c["email"].str.strip().str.lower() != "test@example.com"].dropna(subset=["email"]).copy()
c["email_cle"] = c["email"].str.strip().str.lower()
c["ins"] = pd.to_datetime(c["date_inscription"], format="%d/%m/%Y")
c["manquants"] = c[["telephone", "code_postal", "date_naissance"]].isna().sum(axis=1)
recent = c.sort_values(["email_cle", "ins"], kind="stable").drop_duplicates("email_cle", keep="last")
complete = c.sort_values(["email_cle", "manquants"], kind="stable").drop_duplicates("email_cle", keep="first")
fusion = c.sort_values(["email_cle", "manquants"], kind="stable").groupby("email_cle").first()
print("lignes :", len(c), "| fiches :", len(complete), "| égalité des dates d'inscription dans les groupes de doublons :", bool((c.groupby("email_cle")["ins"].nunique() <= 1).all()))
print("codes postaux manquants : ligne la plus récente", int(recent["code_postal"].isna().sum()), "| ligne la plus complète", int(complete["code_postal"].isna().sum()), "| fusion colonne par colonne", int(fusion["code_postal"].isna().sum()))
```
<!--sortie-->
```text
lignes : 6769 | fiches : 6092 | égalité des dates d'inscription dans les groupes de doublons : False
codes postaux manquants : ligne la plus récente 368 | ligne la plus complète 328 | fusion colonne par colonne 328
```

Choisir **la ligne la plus récente** laisse **368** codes postaux manquants ; choisir **la ligne la plus complète** en laisse **328**, et la **fusion colonne par colonne** (`groupby(...).first()` prend, pour chaque colonne, la première valeur **non vide**) aussi : ici, la ligne la plus complète contient déjà tout ce que les autres copies savent, de sorte que la fusion ne gagne rien de plus. Le critère « le plus récent » n'a presque aucun pouvoir de discrimination : les copies d'un même client recopient la **même date d'inscription** (les seuls groupes aux dates différentes sont les trois e-mails partagés par deux clients distincts), et la ligne retenue dépend alors de l'ordre du fichier. Le critère se choisit d'après ce qui **distingue** réellement les copies.

### Corrigé 1.8

```python
x = site.merge(pd.read_csv(os.path.join(D, "verite_site.csv")).drop_duplicates("order_ref").query("defaut != 'test'"), on="order_ref")
x["a_l_oeil"] = np.where(x["total_n"] > 1000, x["total_n"] / 100, x["total_n"])
ecart = x["a_l_oeil"] - x["total_vrai"]
mal = ecart.abs() > 0.01
print("commandes mal corrigées :", int(mal.sum()), "sur", len(x), "| trop petites :", int((ecart < -0.01).sum()), "| trop grandes :", int((ecart > 0.01).sum()))
print("total en centimes le plus bas parmi les commandes mal corrigées :", int(x.loc[mal, "total_n"].min()), "| plus haut :", int(x.loc[mal, "total_n"].max()), "| date minimale :", x.loc[mal, "dt"].min().date())
```
<!--sortie-->
```text
commandes mal corrigées : 49 sur 6199 | trop petites : 0 | trop grandes : 49
total en centimes le plus bas parmi les commandes mal corrigées : 239 | plus haut : 917 | date minimale : 2025-09-17
```

La correction « à l'œil » rate 49 commandes, **toutes cent fois trop grandes** : ce sont des commandes **postérieures au 15 septembre** dont le total, **en centimes**, est inférieur à 1 000 (donc moins de 10 €) : le seuil sur la valeur ne les divise pas. Elles sont peu nombreuses parce que les petites commandes sont rares, mais elles faussent la moyenne et surtout les valeurs extrêmes. Le seuil confond **le niveau d'une valeur** et **son unité**. La correction **datée** s'appuie sur la seule information fiable : la date où le système a changé, que l'on a détectée (application 1.5) et vérifiée.

### Corrigé 1.9

```python
def lire_caisse2(fichier):
    brut = open(fichier, "rb").read()
    try:
        lignes, enc = brut.decode("utf-8-sig").splitlines(), "utf-8"
    except UnicodeDecodeError:
        lignes, enc = brut.decode("cp1252").splitlines(), "cp1252"
    est_entete = lambda l: re.match(r'^"?(N° ticket|Ticket)', l) is not None
    i0 = next(i for i, l in enumerate(lignes) if est_entete(l))
    sep = max([";", ",", "\t"], key=lambda s: lignes[i0].count(s))
    total = float(lignes[-1].split(sep)[-1].strip('"').replace(",", "."))
    t = pd.read_csv(io.StringIO("\n".join([lignes[i0]] + [l for l in lignes[i0 + 1:-1] if not est_entete(l)])), sep=sep, dtype=str)
    t.columns = [c.replace("N° ticket", "ticket").replace("Ticket", "ticket").replace("Quantité", "Qté") for c in t.columns]
    t = t.rename(columns={"Date": "date", "Heure": "heure", "Article": "article", "Catégorie": "categorie", "Qté": "quantite", "Prix unitaire": "prix_unitaire", "Montant": "montant"})
    for c in ("prix_unitaire", "montant"):
        t[c] = pd.to_numeric(t[c].str.replace(",", "."), errors="coerce")
    fmt = "%Y-%m-%d" if re.fullmatch(r"\d{4}-\d\d-\d\d", t["date"].iloc[0]) else ("%d/%m/%y" if len(t["date"].iloc[0]) == 8 else "%d/%m/%Y")
    t["date"] = pd.to_datetime(t["date"], format=fmt)
    t["quantite"] = t["quantite"].astype(int)
    return t, total, f"{enc}, séparateur {sep!r}"
```

```python
t13, total13, desc13 = lire_caisse2(fichier13)
print(desc13, "| lignes :", len(t13), "| somme lue :", round(t13["montant"].sum(), 2), "| total affiché :", total13, "| dates :", t13["date"].dt.strftime("%d/%m/%Y").tolist())
print("l'ancienne fonction sur le même fichier :", end=" ")
try:
    C.lire_caisse(fichier13)
except Exception as e:
    print(type(e).__name__)
```
<!--sortie-->
```text
utf-8, séparateur '\t' | lignes : 2 | somme lue : 52.36 | total affiché : 52.36 | dates : ['02/01/2026', '02/01/2026']
l'ancienne fonction sur le même fichier : ValueError
```

Deux changements suffisent : le séparateur est choisi par **le caractère le plus fréquent** dans l'en-tête (parmi trois candidats), et le format de date est **déduit de la forme** de la première date. La somme lue (52,36 €) retrouve le total affiché. La généralisation a un coût : chaque nouvelle variante de format demande de reprendre la fonction. Raison de plus pour obtenir de l'équipe qui produit l'export un **format stable et documenté** (CSV en UTF-8, point-virgule, dates ISO).

### Corrigé 1.10

```python
def tel(s):
    chiffres = re.sub(r"\D", "", s)
    if s.startswith("+"):
        chiffres = "0" + chiffres[2:]
    return chiffres if re.fullmatch(r"0\d{9}", chiffres) else None
for n in numeros:
    print(f"{n:22s} -> {tel(n)}")
```
<!--sortie-->
```text
01 23 45 67 89         -> 0123456789
01.23.45.67.89         -> 0123456789
0123456789             -> 0123456789
(0)1 23456789          -> 0123456789
+99 1 23 45 67 89      -> 0123456789
12 34 56               -> None
01 23 45 67 8A         -> None
```

Les cinq premiers numéros se ramènent à `0123456789`. « +99 1 23 45 67 89 » est accepté **parce que** l'indicatif de deux chiffres est remplacé par 0 : c'est une hypothèse (l'indicatif n'est pas contrôlé) à documenter. « 12 34 56 » est **rejeté** (six chiffres : trop court) et « 01 23 45 67 8A » aussi (le `A` disparaît avec `\D`, il ne reste que neuf chiffres). On préfère rejeter une valeur invalide plutôt que d'en inventer une.

### Corrigé 1.11

```python
m = profil["revenu_annuel"].isna()
profil["classe_age2"] = pd.cut(profil["age"], [0, 29, 44, 59, 200])
for nom in ("median", "mean"):
    imp = profil.groupby(["classe_age2", "canal_acquisition"], observed=True)["revenu_annuel"].transform(nom)
    complet = profil["revenu_annuel"].where(~m, imp)
    print(f"{nom:6s} par groupe : erreur typique {np.sqrt(((imp[m] - verite.loc[m, 'revenu_annuel']) ** 2).mean()):8.0f} | biais de la moyenne {complet.mean() - verite['revenu_annuel'].mean():6.0f} | écart-type {complet.std():8.0f}")
```
<!--sortie-->
```text
median par groupe : erreur typique    10352 | biais de la moyenne   -320 | écart-type    10400
mean   par groupe : erreur typique    10180 | biais de la moyenne    -24 | écart-type    10365
```

La **moyenne** de groupe fait légèrement mieux ici : erreur individuelle de 10 180 € contre 10 352 €, et surtout **biais de la moyenne de −24 € contre −320 €**. La raison est simple : la distribution des revenus est asymétrique (la médiane d'un groupe est inférieure à sa moyenne), donc imputer la médiane **tire la moyenne vers le bas**. La différence d'erreur individuelle est faible parce que **le groupe explique peu le revenu** : peu importe la valeur centrale, l'incertitude individuelle domine. On choisit la médiane si l'on veut être robuste aux extrêmes, la moyenne si l'on veut **préserver la moyenne**.

### Corrigé 1.12

```python
rng = np.random.default_rng(3)
sat = verite["satisfaction_moy"]
manque = rng.random(len(sat)) < np.where(sat < 3, 0.5, 0.05)
obs = sat.where(~manque)
print("part de manquants :", round(manque.mean() * 100, 1), "% | moyenne vraie :", round(sat.mean(), 3), "| moyenne observée :", round(obs.mean(), 3), "| biais :", round(obs.mean() - sat.mean(), 3))
for delta in (0, 0.1, 0.2, 0.3, 0.4, 0.5):
    print(f"delta {delta:.1f} : moyenne après imputation {obs.where(~manque, obs.mean() - delta).mean():.3f}")
print("décalage réel entre répondants et non-répondants :", round(obs.mean() - sat[manque].mean(), 3))
```
<!--sortie-->
```text
part de manquants : 12.1 % | moyenne vraie : 3.729 | moyenne observée : 3.808 | biais : 0.079
delta 0.0 : moyenne après imputation 3.808
delta 0.1 : moyenne après imputation 3.796
delta 0.2 : moyenne après imputation 3.784
delta 0.3 : moyenne après imputation 3.772
delta 0.4 : moyenne après imputation 3.760
delta 0.5 : moyenne après imputation 3.748
décalage réel entre répondants et non-répondants : 0.653
```

L'absence supprime surtout les clients peu satisfaits : la moyenne observée (3,81) est supérieure à la vérité (3,73) : le biais est positif, de 0,08 point. Le balayage montre que la moyenne retrouvée dépend **linéairement** de δ, et que le δ qui rétablit la vraie moyenne est celui que l'on lit dans la dernière ligne, l'écart réel entre répondants et non-répondants (0,65 point) : avec 12 % de manquants, il faut soustraire 0,65 aux valeurs imputées pour compenser un biais de 0,08. Cet écart ne s'obtient **qu'avec la vérité**. Dans la vraie vie, on choisit δ **à partir d'une source externe** (une enquête de relance auprès d'un échantillon de non-répondants, qui mesure l'écart réel) ou on présente **plusieurs valeurs** de δ en disant comment la conclusion change : c'est une analyse de sensibilité, pas une correction.
